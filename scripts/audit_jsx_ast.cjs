#!/usr/bin/env node
/* Optional semantic JSX/TSX checks using the project's TypeScript parser.
 * Read-only. Usage: node audit_jsx_ast.cjs /path/to/component.tsx
 * Dependency: TypeScript must be installed locally or globally. */
'use strict';
const fs=require('fs');
const path=require('path');
const child=require('child_process');
let ts;
try {ts=require('typescript');} catch (_) {
  try {const prefix=child.execFileSync('npm',['root','-g'],{encoding:'utf8',timeout:4000}).trim();ts=require(path.join(prefix,'typescript'));}
  catch (_) {console.error('typescript not found; install locally: npm i -D typescript');process.exit(2);}
}
const filepath=process.argv[2];
if(!filepath){console.error('file path required');process.exit(2);}
const source=fs.readFileSync(filepath,'utf8');
const sf=ts.createSourceFile(filepath,source,ts.ScriptTarget.Latest,true,filepath.endsWith('.tsx')?ts.ScriptKind.TSX:ts.ScriptKind.JSX);
const findings=[];
const labelsFor = new Set();
const line=n=>sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1;
const attr=(node,name)=>node.attributes.properties.find(x=>ts.isJsxAttribute(x)&&x.name.getText(sf)===name);
const strValue=initializer=>{
  if(!initializer)return null;
  if(ts.isStringLiteral(initializer))return initializer.text;
  if(ts.isJsxExpression(initializer)&&initializer.expression&&(ts.isStringLiteral(initializer.expression)||ts.isNumericLiteral(initializer.expression)))return initializer.expression.text;
  return null;
};
function emptyHandler(item){
  if(!item||!item.initializer||!ts.isJsxExpression(item.initializer))return false;
  const e=item.initializer.expression;
  if(!e||!(ts.isArrowFunction(e)||ts.isFunctionExpression(e)))return false;
  const body=e.body;
  if(ts.isBlock(body))return body.statements.length===0;
  return body.kind===ts.SyntaxKind.NullKeyword||body.kind===ts.SyntaxKind.FalseKeyword||body.kind===ts.SyntaxKind.UndefinedKeyword;
}
function issue(key,node,rules,severity,confidence,note){
  findings.push({key,file:path.basename(filepath),line:line(node),occurrences:1,source_rules:rules,severity,confidence,note,status:'candidate_not_verified'});
}
function attrString(node,name){return strValue(attr(node,name)?.initializer);}
function nameFromChildren(element){
  if(!element||!ts.isJsxElement(element))return false;
  return element.children.some(x => (ts.isJsxText(x) && x.getText(sf).trim()) ||
    (ts.isJsxExpression(x) && x.expression && x.expression.kind!==ts.SyntaxKind.NullKeyword) ||
    (ts.isJsxElement(x) && (x.openingElement.tagName.getText(sf)==='img' && attrString(x.openingElement,'alt'))) ||
    (ts.isJsxElement(x) && x.children.some(c => ts.isJsxText(c)&&c.getText(sf).trim())));
}
function parentLabel(node){
  let p=node.parent;
  while(p){if(ts.isJsxElement(p) && p.openingElement.tagName.getText(sf)==='label')return true;p=p.parent;}
  return false;
}
function insideForm(node){
  let p=node.parent;
  while(p){if(ts.isJsxElement(p) && p.openingElement.tagName.getText(sf)==='form')return true;p=p.parent;}
  return false;
}
function collectLabels(node){
  if(ts.isJsxOpeningElement(node)&&node.tagName.getText(sf)==='label'){
    const htmlFor=attrString(node,'htmlFor')||attrString(node,'for');
    if(htmlFor)labelsFor.add(htmlFor);
  }
  ts.forEachChild(node,collectLabels);
}
collectLabels(sf);
function visit(node){
  if(ts.isJsxOpeningElement(node)||ts.isJsxSelfClosingElement(node)){
    const tag=node.tagName.getText(sf);
    if((tag==='img'||tag==='Image')&&!attr(node,'alt'))
      issue('MISSING_IMG_ALT',node,['NX-021','SA-034'],'P1_CANDIDATE','high','Imagem JSX sem alt; confirmar descrição ou alt vazio intencional.');
    if((tag==='a'||tag==='Link')&&['#','javascript:void(0)','javascript:;'].includes(strValue(attr(node,'href')?.initializer)))
      issue('PLACEHOLDER_HREF',node,['NX-043','NX-056'],'P0_CANDIDATE','medium','href JSX parece placeholder; confirmar ação.');
    if(emptyHandler(attr(node,'onClick')))
      issue('EMPTY_ONCLICK',node,['NX-056'],'P0_CANDIDATE','high','Handler vazio identificado pela AST.');
    if(['div','span'].includes(tag)&&attr(node,'onClick')&&!(attr(node,'role')&&(attr(node,'onKeyDown')||attr(node,'onKeyUp')||attr(node,'onKeyPress'))))
      issue('NON_SEMANTIC_CLICK',node,['NX-022','NX-056'],'P1_CANDIDATE','medium','onClick sem semântica/teclado evidente.');
    if(tag==='video'&&attr(node,'autoPlay')&&!attr(node,'muted'))
      issue('AUTOPLAY_UNMUTED',node,['NX-038'],'P1_CANDIDATE','medium','Video autoplay sem muted.');
    if((tag==='img'||tag==='Image')&&attrString(node,'src')==='')
      issue('EMPTY_IMAGE_SRC',node,['NX-021'],'P1_CANDIDATE','high','Imagem com src vazio.');
    const hidden=attrString(node,'aria-hidden')==='true';
    const tabindex=attrString(node,'tabIndex')||attrString(node,'tabindex');
    // Positive literal tabIndex changes expected sequential keyboard navigation.
    const positiveIndex=attrString(node,'tabIndex') ?? attrString(node,'tabindex');
    if(positiveIndex!==null && /^\d+$/.test(positiveIndex) && Number(positiveIndex)>0)
      issue('POSITIVE_TABINDEX',node,['NX-037','SA-076'],'P1_CANDIDATE','high','Ordem de foco alterada por tabIndex positivo.');
    const focusable=['a','button','input','select','textarea'].includes(tag) && !(tag==='a'&&!attr(node,'href'));
    if(hidden && !attr(node,'disabled') && tabindex!=='-1' && (focusable||(tabindex!==null && Number(tabindex)>=0)))
      issue('ARIA_HIDDEN_FOCUSABLE',node,['NX-022','SA-076'],'P1_CANDIDATE','high','Elemento focável oculto da árvore de acessibilidade.');
    if((tag==='a'||tag==='Link')&&attrString(node,'target')==='_blank'&&attr(node,'href')){
      const rel=(attrString(node,'rel')||'').toLowerCase().split(/\s+/);
      if(!rel.includes('noopener')&&!rel.includes('noreferrer'))
        issue('EXTERNAL_TARGET_REL',node,['NX-022'],'P3_CANDIDATE','low','Verificar política de rel=noopener; browsers modernos isolam _blank.');
    }
    if(['input','select','textarea'].includes(tag) && (tag!=='input'||!['hidden','button','submit','reset','image'].includes(attrString(node,'type')))){
      const id=attrString(node,'id');
      if(!attr(node,'aria-label')&&!attr(node,'aria-labelledby')&&!attr(node,'title')&&!parentLabel(node)&&!(id&&labelsFor.has(id)))
        issue({input:'UNLABELED_INPUT',select:'UNLABELED_SELECT',textarea:'UNLABELED_TEXTAREA'}[tag],node,['SA-076','NX-022'],'P1_CANDIDATE','medium','Controle sem nome acessível evidente.');
    }
    if(tag==='button'){
      if(!attr(node,'aria-label')&&!attr(node,'aria-labelledby')&&!attr(node,'title')&&!nameFromChildren(node.parent))
        issue('UNNAMED_BUTTON',node,['SA-076','NX-022'],'P1_CANDIDATE','medium','Botão sem nome acessível evidente.');
      if(insideForm(node)&&!attr(node,'type'))
        issue('IMPLICIT_SUBMIT_BUTTON',node,['NX-056'],'P2_CANDIDATE','medium','Button dentro de form realiza submit implícito.');
    }
    if((tag==='a'||tag==='Link') && attr(node,'href') && !attr(node,'aria-label')&&!attr(node,'aria-labelledby')&&!attr(node,'title')&&!nameFromChildren(node.parent))
      issue('UNNAMED_LINK',node,['SA-076','NX-022'],'P1_CANDIDATE','medium','Link sem nome acessível evidente.');
    if(tag==='iframe'&&!attr(node,'title'))
      issue('IFRAME_MISSING_TITLE',node,['NX-021'],'P1_CANDIDATE','high','iframe sem título acessível.');
  }
  ts.forEachChild(node,visit);
}
visit(sf);
process.stdout.write(JSON.stringify({parser:'typescript-jsx-ast',file:filepath,findings}));
