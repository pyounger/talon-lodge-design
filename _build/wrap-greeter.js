const fs=require('fs');
const base='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad';
const repo='C:/Users/Phil/OneDrive/Documents/Development/talon-lodge-design';
let c=fs.readFileSync(base+'/greeter.artifact.html','utf8');
const marker='\n<div class="wrap">';
const i=c.indexOf(marker);
if(i<0){console.error('marker not found');process.exit(1);}
const head=c.slice(0,i).trim(), body=c.slice(i).trim();
const full='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'+head+'\n</head>\n<body>\n'+body+'\n</body>\n</html>\n';
fs.writeFileSync(base+'/arrivals-departures-greeter.html',full);
fs.writeFileSync(repo+'/arrivals-departures-greeter.html',full);
console.log('standalone written: '+Math.round(full.length/1024)+' KB');
