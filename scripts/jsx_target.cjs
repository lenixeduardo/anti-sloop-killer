#!/usr/bin/env node
/* Locate a JSX/TSX element by a unique *literal* id without rewriting formatting. */
const fs = require('fs');
let ts;
try { ts = require('typescript'); } catch {
  try { const root=require('child_process').execFileSync('npm',['root','-g'],{encoding:'utf8'}).trim(); ts = require(require('path').join(root,'typescript')); }
  catch { process.stderr.write('typescript is required for JSX structural fixes\n'); process.exit(3); }
}
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const source = payload.source, id = payload.id;
const file = ts.createSourceFile('target.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const matches = [];
function inspect(node) {
  if (ts.isJsxElement(node) || ts.isJsxSelfClosingElement(node)) {
    const opening = ts.isJsxElement(node) ? node.openingElement : node;
    const attr = opening.attributes.properties.find(p => ts.isJsxAttribute(p) && p.name.text === 'id');
    if (attr && attr.initializer && ts.isStringLiteral(attr.initializer) && attr.initializer.text === id) {
      matches.push({
        tag: opening.tagName.getText(file),
        opening_start: opening.getStart(file), opening_end: opening.getEnd(),
        start: node.getStart(file), end: node.getEnd(),
        self_closing: ts.isJsxSelfClosingElement(node)
      });
    }
  }
  ts.forEachChild(node, inspect);
}
inspect(file);
if (matches.length !== 1) { process.stderr.write(`Expected one JSX element id=${JSON.stringify(id)}, found ${matches.length}\n`); process.exit(2); }
process.stdout.write(JSON.stringify(matches[0]));
