const fs=require('fs');
const base='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad';
const repo='C:/Users/Phil/OneDrive/Documents/Development/talon-lodge-design';
let t=fs.readFileSync(base+'/rescal.template.html','utf8');
const data=fs.readFileSync(base+'/reservation-2027.json','utf8').trim();
t=t.replace('__DATA__',data).replace('__EAGLE__',fs.readFileSync(base+'/eagle-datauri.txt','utf8').trim());
if(t.includes('__DATA__')||t.includes('__EAGLE__')){console.error('unresolved placeholder');process.exit(1);}
fs.writeFileSync(base+'/reservation-calendar.artifact.html',t);
const marker='\n<div class="wrap">';const i=t.indexOf(marker);
const head=t.slice(0,i).trim(),body=t.slice(i).trim();
const full='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'+head+'\n</head>\n<body>\n'+body+'\n</body>\n</html>\n';
fs.writeFileSync(base+'/reservation-calendar.html',full);
fs.writeFileSync(repo+'/reservation-calendar.html',full);
console.log('reservation-calendar assembled: '+Math.round(full.length/1024)+' KB');
