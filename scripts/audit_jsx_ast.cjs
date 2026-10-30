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
const line=n=>sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1;
const attr=(node,name)=>node.attributes.properties.find(x=>ts.isJsxAttribute(x)&&x.name.getText(sf)===name);
const strValue=initializer=>{
  if(!initializer)return null;
  if(ts.isStringLiteral(initializer))return initializer.text;
  if(ts.isJsxExpression(initializer)&&initializer.expression&&ts.isStringLiteral(initializer.expression))return initializer.expression.text;
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
    if(tag==='iframe'&&!attr(node,'title'))
      issue('IFRAME_MISSING_TITLE',node,['NX-021'],'P1_CANDIDATE','high','iframe sem título acessível.');
  }
  ts.forEachChild(node,visit);
}
visit(sf);
process.stdout.write(JSON.stringify({parser:'typescript-jsx-ast',file:filepath,findings}));
