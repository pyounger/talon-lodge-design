// in-situ.template.html -> ../contact-form-in-situ.html
// Embeds the real contact-form.html inside reproduced site chrome. The form's own
// prototype chrome is hidden (not removed — its JS still binds to those buttons).
//   node _build/assemble-insitu.js
const fs = require('fs'), path = require('path');
const B = __dirname, REPO = path.resolve(__dirname, '..');

let form = fs.readFileSync(path.join(REPO, 'contact-form.html'), 'utf8');
if (form.indexOf('id="site-talon"') < 0) { console.error('contact-form.html looks wrong'); process.exit(1); }

// hide the prototype chrome for the embedded copy
form = form.replace('</head>',
  '<style>/* embedded: the host page drives brand + width */\n' +
  '.topbar,.demobar{display:none!important}\n' +
  'body > .foot{display:none!important}   /* prototype note, not part of the embed */\n' +
  'body{background:#fff}\n' +
  '.submitbar{position:static}\n' +
  '</style>\n</head>');

const b64 = Buffer.from(form, 'utf8').toString('base64');

let t = fs.readFileSync(path.join(B, 'in-situ.template.html'), 'utf8');
t = t.replace('__EAGLE__', fs.readFileSync(path.join(B, 'eagle-datauri.txt'), 'utf8').trim());
t = t.replace('__FORM_B64__', b64);
for (const ph of ['__EAGLE__', '__FORM_B64__']) {
  if (t.indexOf(ph) >= 0) { console.error(ph + ' unresolved'); process.exit(1); }
}

const out = path.join(REPO, 'contact-form-in-situ.html');
fs.writeFileSync(out, t);
console.log('in-situ assembled: ' + Math.round(t.length / 1024) + ' KB -> ' + out);
