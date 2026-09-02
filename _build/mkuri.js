const fs=require('fs');
const B='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad';
const img=fs.readFileSync('C:/Users/Phil/OneDrive/Documents/Development/talon-app2026-ui/public/images/portal-masthead.jpg');
const uri='data:image/jpeg;base64,'+img.toString('base64');
fs.writeFileSync(B+'/masthead-datauri.txt',uri);
console.log('masthead data URI: '+Math.round(uri.length/1024)+'KB');
