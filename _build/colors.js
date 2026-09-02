const {g}=require('./extract2.js');
// enumerate fills on data cells rows 4-29, cols C..I (3..9); collect samples
const map={};
for(let r=4;r<=29;r++){for(let c=3;c<=9;c++){const cc=g(r,c);const key=cc.f||'(empty/none)';(map[key]=map[key]||[]).push(cc.v||'(blank)');}}
console.log('=== fill colors on booking cells (count · samples) ===');
Object.entries(map).sort((a,b)=>b[1].length-a[1].length).forEach(([k,arr])=>{
  const withVal=arr.filter(v=>v!=='(blank)');
  const samp=[...new Set(withVal)].slice(0,6).join(' | ');
  console.log(k.padEnd(14),'×'+arr.length,' filled:'+withVal.length,'  e.g. '+ (samp||'(all blank)'));
});
