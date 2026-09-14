// contact-form.template.html -> ../contact-form.html  (inlines the eagle mark)
// Portable: paths are resolved relative to this file, not a hard-coded machine.
//   node _build/assemble-contact.js
const fs = require('fs'), path = require('path');
const B = __dirname, REPO = path.resolve(__dirname, '..');

let t = fs.readFileSync(path.join(B, 'contact-form.template.html'), 'utf8');
t = t.replace('__EAGLE__', fs.readFileSync(path.join(B, 'eagle-datauri.txt'), 'utf8').trim());
if (t.indexOf('__EAGLE__') >= 0) { console.error('eagle unresolved'); process.exit(1); }

const out = path.join(REPO, 'contact-form.html');
fs.writeFileSync(out, t);
console.log('contact-form assembled: ' + Math.round(t.length / 1024) + ' KB -> ' + out);
