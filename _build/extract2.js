const fs=require('fs');
const X='C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad/xlsx';
const rd=f=>fs.readFileSync(X+'/'+f,'utf8');
function decode(s){return s.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#(\d+);/g,(m,n)=>String.fromCharCode(+n)).replace(/&apos;/g,"'");}
// shared strings
const ss=[];{const s=rd('xl/sharedStrings.xml');const re=/<si>([\s\S]*?)<\/si>/g;let m;while((m=re.exec(s))){const txt=(m[1].match(/<t[^>]*>([\s\S]*?)<\/t>/g)||[]).map(x=>x.replace(/<[^>]+>/g,'')).join('');ss.push(decode(txt));}}
// fills
const styles=rd('xl/styles.xml');
const fills=[];{const fb=styles.match(/<fills[^>]*>([\s\S]*?)<\/fills>/)[1];const re=/<fill>([\s\S]*?)<\/fill>/g;let m;while((m=re.exec(fb))){const f=m[1];let rgb=null;const fg=f.match(/<fgColor([^>]*)\/>/);if(fg){const r=fg[1].match(/rgb="([0-9A-Fa-f]{8})"/);if(r)rgb=r[1].slice(2).toUpperCase();}const pat=(f.match(/patternType="([^"]*)"/)||[])[1]||'none';fills.push({rgb,pat});}}
const cellXfs=[];{const xb=styles.match(/<cellXfs[^>]*>([\s\S]*?)<\/cellXfs>/)[1];const re=/<xf\b([^>]*?)(?:\/>|>[\s\S]*?<\/xf>)/g;let m;while((m=re.exec(xb))){cellXfs.push(+((m[1].match(/fillId="(\d+)"/)||[])[1]||0));}}
const fillOf=s=>{if(s==null)return null;const f=fills[cellXfs[s]];return f&&f.pat==='solid'?f.rgb:null;};
// sheet parse — CORRECT cell regex (non-greedy attrs, proper self-close handling)
const sheet=rd('xl/worksheets/sheet3.xml');
function colToNum(c){let n=0;for(const ch of c)n=n*26+(ch.charCodeAt(0)-64);return n;}
const cell={};
const cre=/<c\s+r="([A-Z]+)(\d+)"([^>]*?)(\/>|>([\s\S]*?)<\/c>)/g;let m;
while((m=cre.exec(sheet))){
  const col=colToNum(m[1]),row=+m[2],attr=m[3],selfClose=m[4]==='/>',inner=m[5]||'';
  const sIdx=(attr.match(/\bs="(\d+)"/)||[])[1];
  const t=(attr.match(/\bt="([a-z]+)"/)||[])[1];
  let val='';
  if(!selfClose){
    let v=(inner.match(/<v>([\s\S]*?)<\/v>/)||[])[1];
    const isv=(inner.match(/<is>[\s\S]*?<t[^>]*>([\s\S]*?)<\/t>/)||[])[1];
    if(t==='s'&&v!=null)val=ss[+v]||'';
    else if(t==='inlineStr'&&isv!=null)val=decode(isv);
    else if(v!=null)val=decode(v);
  }
  cell[row+'_'+col]={v:(val||'').trim(),f:fillOf(sIdx!=null?+sIdx:null)};
}
const g=(r,c)=>cell[r+'_'+c]||{v:'',f:null};
// verify: dump rows 4-9, cols B(2)..K(11)
function numToCol(n){let s='';while(n>0){s=String.fromCharCode(65+(n-1)%26)+s;n=Math.floor((n-1)/26);}return s;}
console.log('=== VERIFY rows 4-9 (cols B..K) ===');
for(let r=4;r<=9;r++){let line='r'+r+': ';for(let c=2;c<=11;c++){const cc=g(r,c);if(cc.v||cc.f)line+='['+numToCol(c)+(cc.f?('#'+cc.f):'')+']'+(cc.v||'·')+'  ';}console.log(line);}
module.exports={g,cell,ss};
