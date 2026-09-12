// Inline Google Fonts into a self-contained copy of an HTML file.
// Chromium in this container can't complete TLS through the egress proxy, but curl can,
// so we fetch with curl and embed as data: URIs. Render input stays byte-identical.
const fs=require('fs'), cp=require('child_process');
const UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/131.0.0.0 Chrome/131.0.0.0 Safari/537.36";
const get=(url,bin)=>cp.execFileSync("curl",["-sS","--fail","--max-time","60","-A",UA,url],
  {maxBuffer:1<<28, encoding: bin?"buffer":"utf8"});

const [,,IN,OUT]=process.argv;
let html=fs.readFileSync(IN,"utf8");

// drop preconnects (they only stall against a proxy that can't serve them)
html=html.replace(/<link[^>]+rel=["']?(?:preconnect|dns-prefetch)["']?[^>]*>\s*/gi,"");

const links=[...html.matchAll(/<link[^>]+href=["'](https:\/\/fonts\.googleapis\.com\/css2?[^"']+)["'][^>]*>/gi)];
if(!links.length){ fs.writeFileSync(OUT,html); console.log("  no google-fonts links"); process.exit(0); }

let faces=0, bytes=0;
for(const m of links){
  const url=m[1].replace(/&amp;/g,"&");
  let css=get(url);
  const fonts=[...new Set([...css.matchAll(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+)\)/g)].map(x=>x[1]))];
  for(const fu of fonts){
    const buf=get(fu,true); bytes+=buf.length; faces++;
    const mime=/\.woff2(\?|$)/.test(fu)?"font/woff2":/\.woff(\?|$)/.test(fu)?"font/woff":"font/ttf";
    css=css.split("url("+fu+")").join("url(data:"+mime+";base64,"+buf.toString("base64")+")");
  }
  html=html.replace(m[0],"<style>\n"+css+"\n</style>");
}
fs.writeFileSync(OUT,html);
console.log("  inlined "+faces+" font files ("+(bytes/1024).toFixed(0)+" KB) from "+links.length+" stylesheet(s)");
