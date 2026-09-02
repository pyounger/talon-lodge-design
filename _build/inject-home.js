const fs=require('fs');
const B='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad';
let s=fs.readFileSync(B+'/portal-home-snapshot.html','utf8');
s=s.replace('__MASTHEAD__',fs.readFileSync(B+'/masthead-datauri.txt','utf8').trim());
s=s.replace('__EAGLE__',fs.readFileSync(B+'/eagle-datauri.txt','utf8').trim());
if(s.includes('__MASTHEAD__')||s.includes('__EAGLE__')){console.error('unresolved');process.exit(1);}
fs.writeFileSync(B+'/portal-home-snapshot.html',s);
console.log('injected · file '+Math.round(s.length/1024)+'KB');
