// render-pdf.js — portable replacement for cdp-pdf.js.
//
//   node _build/render-pdf.js <in.html> <out.pdf>
//
// Same CDP approach and the same print settings as cdp-pdf.js (printBackground,
// 0.4in margins, force-decode every image before printing), but it takes its input
// and output as arguments and finds Chromium via $CHROME instead of a hard-coded
// Windows path.
//
// Webfonts: if the renderer can't reach fonts.googleapis.com, run the file through
// _build/inline-fonts.js first and render the output of that — otherwise headings and
// body copy fall back to whatever the host's system UI font is, which changes how the
// PDF looks. See _build/README.md.
const fs=require('fs'), cp=require('child_process'), os=require('os'), path=require('path');
const CHROME=process.env.CHROME||"/opt/pw-browsers/chromium";
const IN=path.resolve(process.argv[2]), OUT=path.resolve(process.argv[3]);
const PORT=9223+Math.floor(Math.random()*200);
const UDD=path.join(os.tmpdir(),"cdp-chrome-"+Date.now()+"-"+PORT);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

(async()=>{
  const chrome=cp.spawn(CHROME,["--headless=new","--disable-gpu","--no-sandbox","--no-first-run",
    "--no-default-browser-check","--allow-file-access-from-files","--font-render-hinting=none",
    "--remote-debugging-port="+PORT,"--user-data-dir="+UDD,"about:blank"],{stdio:"ignore"});
  try{
    let target;
    for(let i=0;i<60;i++){
      try{const r=await fetch("http://127.0.0.1:"+PORT+"/json");const list=await r.json();
          target=list.find(t=>t.type==="page");if(target&&target.webSocketDebuggerUrl)break;}catch(e){}
      await sleep(300);
    }
    if(!target)throw new Error("no page target");
    const ws=new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
    let id=0;const pending={};
    ws.onmessage=ev=>{const d=JSON.parse(ev.data);if(d.id&&pending[d.id]){pending[d.id](d);delete pending[d.id];}};
    const cmd=(method,params)=>new Promise((res,rej)=>{
      const i=++id;
      pending[i]=d=>d.error?rej(new Error(method+": "+JSON.stringify(d.error))):res(d.result);
      ws.send(JSON.stringify({id:i,method,params:params||{}}));
    });
    await cmd("Page.enable");
    await cmd("Page.navigate",{url:"file://"+IN});
    await sleep(5000);
    // force every image to decode before printing (the fix from the original script)
    const dec=await cmd("Runtime.evaluate",{awaitPromise:true,returnByValue:true,expression:
      "(async()=>{try{await document.fonts.ready;}catch(e){} const imgs=[...document.images]; let ok=0,fail=0; await Promise.all(imgs.map(async im=>{try{await im.decode();ok++;}catch(e){fail++;}})); return {total:imgs.length,ok,fail};})()"});
    console.log("  images:",JSON.stringify(dec.result&&dec.result.value));
    await sleep(2000);
    const pr=await cmd("Page.printToPDF",{printBackground:true,displayHeaderFooter:false,
      marginTop:0.4,marginBottom:0.4,marginLeft:0.4,marginRight:0.4,transferMode:"ReturnAsStream"});
    let chunks=[],eof=false;
    while(!eof){const r=await cmd("IO.read",{handle:pr.stream,size:2097152});
      chunks.push(Buffer.from(r.data,r.base64Encoded?"base64":"utf8"));eof=r.eof;}
    await cmd("IO.close",{handle:pr.stream});
    fs.writeFileSync(OUT,Buffer.concat(chunks));
    console.log("  wrote",OUT,fs.statSync(OUT).size,"bytes");
    ws.close();
  }finally{
    try{chrome.kill();}catch(e){}
    try{fs.rmSync(UDD,{recursive:true,force:true});}catch(e){}
  }
})().catch(e=>{console.error("ERR",e.message);process.exit(1);});
