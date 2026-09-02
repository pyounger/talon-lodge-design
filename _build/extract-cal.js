const fs=require('fs');
const X='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad/xlsx';
const rd=f=>fs.readFileSync(X+'/'+f,'utf8');
function decode(s){return s.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#(\d+);/g,(m,n)=>String.fromCharCode(+n));}
const ss=[]; {const s=rd('xl/sharedStrings.xml');const re=/<si>([\s\S]*?)<\/si>/g;let m;while((m=re.exec(s))){const txt=(m[1].match(/<t[^>]*>([\s\S]*?)<\/t>/g)||[]).map(x=>x.replace(/<[^>]+>/g,'')).join('');ss.push(decode(txt));}}
const styles=rd('xl/styles.xml');
const fills=[]; {const fb=styles.match(/<fills[^>]*>([\s\S]*?)<\/fills>/)[1];const re=/<fill>([\s\S]*?)<\/fill>/g;let m;while((m=re.exec(fb))){const f=m[1];let rgb=null;const fg=f.match(/<fgColor([^>]*)\/>/);if(fg){const r=fg[1].match(/rgb="([0-9A-Fa-f]{8})"/);if(r)rgb=r[1].slice(2).toUpperCase();}const pat=(f.match(/patternType="([^"]*)"/)||[])[1]||'none';fills.push({rgb,pat});}}
const cellXfs=[]; {const xb=styles.match(/<cellXfs[^>]*>([\s\S]*?)<\/cellXfs>/)[1];const re=/<xf\b([^>]*?)(?:\/>|>[\s\S]*?<\/xf>)/g;let m;while((m=re.exec(xb))){cellXfs.push(+((m[1].match(/fillId="(\d+)"/)||[])[1]||0));}}
const fillOf=s=>{if(s==null)return null;const f=fills[cellXfs[s]];return f&&f.pat==='solid'?f.rgb:null;};
const sheet=rd('xl/worksheets/sheet3.xml');
function colToNum(c){let n=0;for(const ch of c)n=n*26+(ch.charCodeAt(0)-64);return n;}
const cell={}; {const re=/<c r="([A-Z]+)(\d+)"([^>]*)(?:\/>|>([\s\S]*?)<\/c>)/g;let m;
  while((m=re.exec(sheet))){const col=colToNum(m[1]),row=+m[2],attr=m[3],inner=m[4]||'';
    const s=(attr.match(/ s="(\d+)"/)||[])[1];const t=(attr.match(/ t="([a-z]+)"/)||[])[1];
    let v=(inner.match(/<v>([\s\S]*?)<\/v>/)||[])[1];let val='';
    if(t==='s'&&v!=null)val=ss[+v]||'';else if(v!=null)val=v;
    cell[row+'_'+col]={v:(val||'').trim(),f:fillOf(s!=null?+s:null)};}}
const g=(r,c)=>cell[r+'_'+c]||{v:'',f:null};

const ROOMS=[{name:'Spruce 1',cap:2},{name:'Spruce 2',cap:2},{name:'Spruce House',cap:6},{name:'Cedar 1',cap:2},{name:'Cedar 2',cap:2},{name:'Cedar House',cap:4},{name:'Bluff House',cap:6}];
const COLS=[3,4,5,6,7,8,9];
function status(f,val){ if(!val)return 'available';
  if(f==='FF0000')return 'held';                 // red — held, deciding
  if(f==='00FFFF'||f==='C9DAF8')return 'reserved'; // blue/aqua — reserved, deposit not received
  if(f==='F4CCCC')return 'prospect';             // pink — "book group" prospect
  return 'confirmed';                            // white / series-week green(D8E4BC)/purple(CCC0DA) / grey note
}
function seriesOf(f){ if(f==='CCC0DA')return 'Winemaker'; if(f==='D8E4BC')return 'Chef'; return 'Standard'; }
function party(val){const m=val.match(/\((\d+)(?:\/\d+)?\)/);return m?+m[1]:null;}

const weeks=[];
for(let r=4;r<=28;r++){
  const label=g(r,2).v; if(!label)continue;
  const rowFill=g(r,1).f||g(r,2).f;
  const series=seriesOf(rowFill);
  const cells=COLS.map((c,i)=>{const cc=g(r,c);const st=status(cc.f,cc.v);return {room:i,guest:cc.v,party:party(cc.v),status:st};});
  weeks.push({n:+g(r,1).v||weeks.length+1,label,series,available:+g(r,10).v||0,sold:+g(r,14).v||0,cells});
}
const totals={possible:+g(29,1).v||564,sold:+g(30,1).v||0,remaining:+g(31,1).v||0,pct:+g(32,1).v||0};
const out={rooms:ROOMS,weeks,totals};
fs.writeFileSync(X+'/../reservation-2027.json',JSON.stringify(out,null,1));
// summary
const cnt={};weeks.forEach(w=>w.cells.forEach(c=>cnt[c.status]=(cnt[c.status]||0)+1));
console.log('weeks',weeks.length,'· statuses',JSON.stringify(cnt),'· series',JSON.stringify(weeks.reduce((a,w)=>{a[w.series]=(a[w.series]||0)+1;return a;},{})));
console.log('totals',JSON.stringify(totals));
console.log('sample week 1:',JSON.stringify(weeks[0]));
console.log('held cells:',weeks.flatMap(w=>w.cells.filter(c=>c.status==='held').map(c=>w.label+' · '+ROOMS[c.room].name+' · '+c.guest)).join('  |  '));
