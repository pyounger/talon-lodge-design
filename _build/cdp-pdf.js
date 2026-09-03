const fs=require('fs'), cp=require('child_process'), os=require('os'), path=require('path');
const CHROME="C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const FILE="file:///C:/Users/Phil/OneDrive/Documents/Development/talon-lodge-design/system-blueprint.html";
const OUT=process.argv[2]||(__dirname+"/blueprint-cdp.pdf");
const PORT=9223;
const UDD=path.join(os.tmpdir(),"cdp-chrome-"+Date.now());
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

(async()=>{
  const chrome=cp.spawn(CHROME,["--headless=new","--disable-gpu","--no-first-run","--no-default-browser-check",
    "--remote-debugging-port="+PORT,"--user-data-dir="+UDD,"about:blank"],{stdio:"ignore"});
  try{
    let target;
    for(let i=0;i<40;i++){
      try{const r=await fetch("http://127.0.0.1:"+PORT+"/json");const list=await r.json();target=list.find(t=>t.type==="page");if(target&&target.webSocketDebuggerUrl)break;}catch(e){}
      await sleep(300);
    }
    if(!target)throw new Error("no page target");
    const ws=new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
    let id=0;const pending={};
    ws.onmessage=ev=>{const d=JSON.parse(ev.data);if(d.id&&pending[d.id]){pending[d.id](d);delete pending[d.id];}};
    function cmd(method,params){
      return new Promise((res,rej)=>{
        const i=++id;
        pending[i]=function(d){ if(d.error){rej(new Error(method+": "+JSON.stringify(d.error)));} else {res(d.result);} };
        ws.send(JSON.stringify({id:i,method:method,params:params||{}}));
      });
    }
    await cmd("Page.enable");
    await cmd("Page.navigate",{url:FILE});
    await sleep(4000);
    const dec=await cmd("Runtime.evaluate",{awaitPromise:true,returnByValue:true,expression:
      "(async()=>{try{await document.fonts.ready;}catch(e){} const imgs=[...document.images]; let ok=0,fail=0; await Promise.all(imgs.map(async im=>{try{await im.decode();ok++;}catch(e){fail++;}})); return {total:imgs.length,ok:ok,fail:fail};})()"});
    console.log("decode:",JSON.stringify(dec.value));
    await sleep(1500);
    const pr=await cmd("Page.printToPDF",{printBackground:true,displayHeaderFooter:false,marginTop:0.4,marginBottom:0.4,marginLeft:0.4,marginRight:0.4,transferMode:"ReturnAsStream"});
    const handle=pr.stream;
    let chunks=[];let eof=false;
    while(!eof){const r=await cmd("IO.read",{handle:handle,size:2097152});chunks.push(Buffer.from(r.data,r.base64Encoded?"base64":"utf8"));eof=r.eof;}
    await cmd("IO.close",{handle:handle});
    fs.writeFileSync(OUT,Buffer.concat(chunks));
    console.log("PDF written:",fs.statSync(OUT).size,"bytes");
    ws.close();
  }finally{
    try{chrome.kill();}catch(e){}
    try{fs.rmSync(UDD,{recursive:true,force:true});}catch(e){}
  }
})().catch(e=>{console.error("ERR",e.message);process.exit(1);});
