const fs=require('fs');
const B='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad';
const IMG='C:/Users/Phil/OneDrive/Documents/Development/talon-app2026-ui/public/images';
const uri=f=>"data:image/jpeg;base64,"+fs.readFileSync(IMG+'/'+f).toString('base64');
let s=fs.readFileSync(B+'/portal-home-snapshot.html','utf8');
const rep=[['--tile-guest','tile-guest.jpg'],['--tile-flights','tile-flights.jpg'],['--tile-pay','tile-payments.jpg'],['--tile-act','tile-adventures.jpg'],['--tile-spa','tile-spa.jpg'],['--tile-lic','tile-license.jpg']];
for(const [tok,f] of rep){ s=s.replace("background:var("+tok+")","background:url('"+uri(f)+"') center/cover"); }
// drop emoji glyphs in the photo bands
s=s.replace(/<span class="emoji">[^<]*<\/span>/g,'');
if(s.includes('background:var(--tile-')){console.error('a tile usage remained');process.exit(1);}
fs.writeFileSync(B+'/portal-home-snapshot.html',s);
console.log('snapshot updated to photo tiles · '+Math.round(s.length/1024)+'KB');
