const fs=require('fs'),path=require('path');
const base='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad';
const repo='C:/Users/Phil/OneDrive/Documents/Development/talon-lodge-design';
let tpl=fs.readFileSync(base+'/review.template.html','utf8');
tpl=tpl.replace('__EAGLE__',fs.readFileSync(base+'/eagle-datauri.txt','utf8').trim());
const imgDir=base+'/review';
fs.readdirSync(imgDir).filter(f=>f.endsWith('.jpg')).forEach(f=>{
  const tok='__IMG_'+f.replace(/\.jpg$/,'')+'__';
  if(tpl.includes(tok)){const b64=fs.readFileSync(path.join(imgDir,f)).toString('base64');tpl=tpl.split(tok).join('data:image/jpeg;base64,'+b64);}
});
const left=(tpl.match(/__IMG_[a-z-]+__/g)||[]);
if(left.length){console.error('UNRESOLVED:',[...new Set(left)]);process.exit(1);}
fs.writeFileSync(base+'/project-review.artifact.html',tpl);
const marker='\n<div class="doc">';const i=tpl.indexOf(marker);
// keep the fixed .tools before .doc inside body; head = up to first <div class="tools">
const hi=tpl.indexOf('<div class="tools');
const head=tpl.slice(0,hi).trim(), body=tpl.slice(hi).trim();
const full='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'+head+'\n</head>\n<body>\n'+body+'\n</body>\n</html>\n';
fs.writeFileSync(base+'/project-review.html',full);
fs.writeFileSync(repo+'/project-review.html',full);
console.log('project-review assembled: '+Math.round(full.length/1024)+' KB');
