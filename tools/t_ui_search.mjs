// UI-level regression: type into the REAL search box and read what is rendered (the data-level test missed a hidden result group)
import pw from 'playwright-core'; const { chromium } = pw;
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
const ctx = await b.newContext({viewport:{width:390,height:844},geolocation:{latitude:32.0835,longitude:34.8035},permissions:['geolocation']});
await ctx.addInitScript(()=>{localStorage.setItem('nativ.v1',JSON.stringify({account:{name:'t',contact:'051',terms:1},prefs:{voice:false}}))});
const p=await ctx.newPage(); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://localhost:8765/test4.html#srchdebug'); await p.waitForTimeout(9000);
const qs=process.argv.slice(2); let bad=0;
for(const q of qs){ const [typed,want]=q.split('=>');
  await p.evaluate(t=>{document.querySelector('#sOpen').click();const q=document.querySelector('#q');q.value=t;q.dispatchEvent(new Event('input'))},typed); await p.waitForTimeout(400);
  const rows=await p.evaluate(()=>[...document.querySelectorAll('#sResults .li')].slice(0,12).map(e=>e.innerText.replace(/\s+/g,' ').trim()));
  const ok=rows.some(r=>r.includes(want)); if(!ok) bad++;
  console.log(ok?'OK  ':'FAIL',typed,'->',rows.slice(0,3).join(' | ')); }
console.log('bad',bad); process.exit(bad?1:0);
