const fs=require('fs');
const base='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad';
const repo='C:/Users/Phil/OneDrive/Documents/Development/talon-lodge-design';
let t=fs.readFileSync(base+'/styleguide.template.html','utf8');
t=t.replace('__EAGLE__',fs.readFileSync(base+'/eagle-datauri.txt','utf8').trim());
if(t.includes('__EAGLE__')){console.error('eagle unresolved');process.exit(1);}
fs.writeFileSync(base+'/style-guide.artifact.html',t);
// standalone: wrap. content-only starts with <title>... then <link>...<style>...</style> then body divs+script
const i=t.indexOf('\n<div class="wrap">');
const head=t.slice(0,i).trim(), body=t.slice(i).trim();
const full='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'+head+'\n</head>\n<body>\n'+body+'\n</body>\n</html>\n';
fs.writeFileSync(base+'/style-guide.html',full);
fs.writeFileSync(repo+'/style-guide.html',full);
console.log('style-guide assembled: '+Math.round(full.length/1024)+' KB');
