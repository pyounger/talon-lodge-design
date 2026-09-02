const {g}=require('./extract2.js');
const fs=require('fs');
const OUT='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad/reservation-2027.json';
const ROOMS=[{name:'Spruce 1',cap:2},{name:'Spruce 2',cap:2},{name:'Spruce House',cap:6},{name:'Cedar 1',cap:2},{name:'Cedar 2',cap:2},{name:'Cedar House',cap:4},{name:'Bluff House',cap:6}];
const COLS=[3,4,5,6,7,8,9];
function status(f,val){ if(!val) return 'available';
  if(f==='FF0000') return 'held';
  if(f==='00FFFF'||f==='C9DAF8') return 'reserved';   // blue: reservation made, deposit not received
  if(f==='F4CCCC') return 'prospect';                 // "book group of N only"
  return 'confirmed';                                 // white / grey(linked) / purple(WM wk) / green(Chef wk)
}
function seriesOf(f){ if(f==='CCC0DA')return 'Winemaker'; if(f==='D8E4BC')return 'Chef'; return 'Standard'; }
function party(v){const m=v.match(/\((\d+)(?:\/\d+)?\)/);return m?+m[1]:null;}
const num=v=>{const n=parseFloat(v);return isFinite(n)?n:null;};

const weeks=[];
for(let r=4;r<=60;r++){
  const label=g(r,2).v; if(!label||!/^\d/.test(label)) continue;
  const wkNo=num(g(r,1).v);
  const rowFill=g(r,2).f;
  const series=seriesOf(rowFill);
  const cells=COLS.map((c,i)=>{const cc=g(r,c);const linked=cc.f==='EFEFEF';return {room:i,guest:cc.v,party:party(cc.v),status:status(cc.f,cc.v),linked};});
  const avail=num(g(r,10).v);       // col J "Available"
  const cap=num(g(r,13).v);         // col M weekly capacity
  const note=g(r,11).v||'';         // col K notes
  weeks.push({n:wkNo!=null?wkNo:weeks.length+1,label,series,available:avail,capacity:cap,note,cells});
}
// season totals from the sheet's own columns
let possible=0,remaining=0;
weeks.forEach(w=>{ if(w.capacity!=null)possible+=w.capacity; if(w.available!=null)remaining+=w.available; });
const confirmedBeds=possible-remaining;
const totals={possible,remaining,confirmed:confirmedBeds,pct: possible? +(confirmedBeds/possible).toFixed(3):0};
fs.writeFileSync(OUT,JSON.stringify({rooms:ROOMS,weeks,totals},null,1));

// report
const sc={};weeks.forEach(w=>w.cells.forEach(c=>sc[c.status]=(sc[c.status]||0)+1));
console.log('weeks:',weeks.length);
console.log('statuses:',JSON.stringify(sc));
console.log('series:',JSON.stringify(weeks.reduce((a,w)=>{a[w.series]=(a[w.series]||0)+1;return a;},{})));
console.log('totals:',JSON.stringify(totals),'→',confirmedBeds,'confirmed /',possible,'possible =',Math.round(totals.pct*100)+'%');
console.log('reserved(blue) cells:',weeks.flatMap(w=>w.cells.filter(c=>c.status==='reserved').map(c=>w.label+' '+ROOMS[c.room].name+'='+c.guest)).join(' | '));
console.log('held(red) cells:',weeks.flatMap(w=>w.cells.filter(c=>c.status==='held').map(c=>w.label+' '+ROOMS[c.room].name+'='+c.guest)).join(' | '));
console.log('last 4 weeks labels:',weeks.slice(-4).map(w=>w.n+':'+w.label).join('  '));
