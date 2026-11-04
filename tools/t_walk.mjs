import pw from 'playwright-core'; const { chromium } = pw;
const D='/tmp/claude-0/-home-claude/1b6ae73e-58cb-557a-a5ed-d3d6f4739dab/scratchpad/';
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
const ctx = await b.newContext({viewport:{width:390,height:844},geolocation:{latitude:32.0835,longitude:34.8035},permissions:['geolocation'],deviceScaleFactor:2});
await ctx.addInitScript(()=>{localStorage.setItem('nativ.v1',JSON.stringify({account:{name:'t',contact:'051',terms:1},prefs:{voice:false}}))});
const p=await ctx.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://localhost:8765/test4.html#srchdebug,hopdebug,walkdebug'); await p.waitForTimeout(9000);
const info=await p.evaluate(async()=>{ const S=window.__SRCH, A=window.__HOPAPI, W=window.__WALK;
 const d=await S.run('צור הדסה'), m=await S.run('בר גיורא'); const me={x:m.x,y:m.y,label:'בר גיורא'};
 const R=await A.hopCompute({x:d.x,y:d.y,label:'צור הדסה'},me); const c=R.picks[0]; R.me=me;
 W.walkStart(R,c,me); const L=W.WLK; return {steps:L.steps.map(s=>[s.turn,s.name,Math.round(s.s0),Math.round(s.s1)]), total:Math.round(L.total), min:Math.round(L.total/1.25/60), drop:[Math.round(c.x),Math.round(c.y)], toLL:null}; });
console.log(JSON.stringify(info).slice(0,1400));
await p.waitForTimeout(2500); await p.screenshot({path:D+'walk1.png'});
const pts=await p.evaluate(()=>{const L=window.__WALK.WLK; return [L.pts[0],L.pts[Math.floor(L.pts.length/3)],L.pts[Math.floor(L.pts.length*0.8)]];});
const LAT0=32.0865, LON0=34.815, KX=111320*Math.cos(LAT0*Math.PI/180), KY=110540;
console.log('before', await p.evaluate(()=>document.querySelector('#wbBig').textContent+' | '+document.querySelector('#wbSub').textContent));
for(const [i,pt] of pts.entries()){ await ctx.setGeolocation({latitude:LAT0+pt[1]/KY, longitude:LON0+pt[0]/KX, accuracy:8}); await p.waitForTimeout(3500); console.log('pos'+i, await p.evaluate(()=>document.querySelector('#wbBig').textContent+' | '+document.querySelector('#wbSub').textContent+' | '+document.querySelector('#wbProg').style.width)); if(i===1) await p.screenshot({path:D+'walk2.png'}); }
console.log(await p.evaluate(()=>document.querySelector('#wbBig').textContent+' | '+document.querySelector('#wbSub').textContent));
process.exit(0);
