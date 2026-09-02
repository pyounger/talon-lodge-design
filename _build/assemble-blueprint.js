const fs=require('fs');
const DIR="C:/Users/Phil/OneDrive/Documents/Development/talon-lodge-design";
const SHOTS=DIR+"/_build/blueprint-shots";
const SP="C:/Users/Phil/AppData/Local/Temp/claude/C--Users-Phil-OneDrive-Documents-vessel-public/4717bc68-92d5-4010-bbc6-9e9ecbee5a31/scratchpad";
let t=fs.readFileSync(DIR+"/_build/system-blueprint.template.html","utf8");
// eagle
const eagle=fs.readFileSync(DIR+"/_build/eagle-datauri.txt","utf8").trim();
t=t.replace(/__EAGLE__/g,eagle);
// images
const map={record:"record","dberd":"db-erd",guestlist:"guestlist",portalhome:"portalhome",portalprof:"portalprof",assets:"assets",rooms:"rooms",approvals:"approvals",boats:"boats",meals:"meals",fish:"fish",daily:"daily",survey:"survey",dashboard:"dashboard",profilesat:"profilesat"};
for(const [ph,file] of Object.entries(map)){
  const b64=fs.readFileSync(SHOTS+"/"+file+".png").toString("base64");
  const uri="data:image/png;base64,"+b64;
  const re=new RegExp("__IMG_"+ph+"__","g");
  if(!re.test(t)){console.log("WARN placeholder missing:",ph);}
  t=t.replace(new RegExp("__IMG_"+ph+"__","g"),uri);
}
// leftover check
const left=(t.match(/__IMG_[a-z]+__|__EAGLE__/g)||[]);
if(left.length){console.log("UNREPLACED:",left);}
// 1) artifact (content-only)
fs.writeFileSync(SP+"/system-blueprint.artifact.html",t);
// 2) standalone repo file (full doc wrapper)
const doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'+t+'\n</head_noop></html>';
// t already contains <title><style>...</style> then body markup; wrap properly:
const full='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
  + t.slice(0, t.indexOf('</style>')+8)  // title+style
  + '\n</head>\n<body>\n'
  + t.slice(t.indexOf('</style>')+8)      // body markup (starts with <div class="wrap">)
  + '\n</body></html>';
fs.writeFileSync(DIR+"/system-blueprint.html",full);
fs.writeFileSync(SP+"/system-blueprint.standalone.html",full);
console.log("assembled. artifact bytes:",t.length,"standalone bytes:",full.length);
