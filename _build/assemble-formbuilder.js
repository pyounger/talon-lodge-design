// form-builder.template.html -> ../form-builder.html  (inlines the eagle mark)
// Portable: paths are resolved relative to this file, not a hard-coded machine.
//   node _build/assemble-contact.js
const fs = require('fs'), path = require('path');
const B = __dirname, REPO = path.resolve(__dirname, '..');

let t = fs.readFileSync(path.join(B, 'form-builder.template.html'), 'utf8');
t = t.replace('__EAGLE__', fs.readFileSync(path.join(B, 'eagle-datauri.txt'), 'utf8').trim());
if (t.indexOf('__EAGLE__') >= 0) { console.error('eagle unresolved'); process.exit(1); }

const out = path.join(REPO, 'form-builder.html');
fs.writeFileSync(out, t);
console.log('form-builder assembled: ' + Math.round(t.length / 1024) + ' KB -> ' + out);
