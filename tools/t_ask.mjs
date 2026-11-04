import pw from 'playwright-core'; const { chromium } = pw;
const D='/tmp/claude-0/-home-claude/1b6ae73e-58cb-557a-a5ed-d3d6f4739dab/scratchpad/';
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
const ctx = await b.newContext({viewport:{width:390,height:844},geolocation:{latitude:32.0835,longitude:34.8035},permissions:['geolocation'],deviceScaleFactor:2});
await ctx.addInitScript(()=>{localStorage.setItem('nativ.v1',JSON.stringify({account:{name:'t',contact:'051',terms:1},prefs:{voice:false},home:{kind:'pin',label:'רחוב 601 22 בני ברק',sub:'',x:600,y:900}}))});
const p=await ctx.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://localhost:8765/test4.html#askdebug'); await p.waitForTimeout(9000);
await p.screenshot({path:D+'ask_home.png'});
const qs=process.argv.slice(2);
for(const q of qs){ const t=Date.now(); const r=await p.evaluate(async q=>{ const a=await window.__ASK.understand(q); return a&&{say:a.say, html:(a.html||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').slice(0,160)}; },q); console.log(Math.round((Date.now()-t)/1000)+'s',q,'=>',JSON.stringify(r)); }
await p.evaluate(()=>window.__ASK.open()); await p.waitForTimeout(500);
await p.evaluate(async()=>{ await window.__ASK.run('בתי קפה ליד נס הרים'); }); await p.waitForTimeout(1500);
await p.screenshot({path:D+'ask_modal.png'});
process.exit(0);
