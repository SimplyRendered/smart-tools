APP = dict(
slug="car-ramp", title="Car Ramp Scrape Check", h1="Car Ramp Scrape Check",
sub="Enter the floor height, ramp slope and your car. See if the nose, belly or tail scrapes at the top or bottom of the ramp, and how long the transitions must be.",
meta=[("Sheet","T-37"),("Method","Rigid car on ramp profile"),("Units","m, mm, %"),("By","@smart_tools_every_week")],
source="Geometry only: a rigid car on two wheel contact points, flat underbody between the axles, overhang tips set by the approach and departure angles. Each transition runs at half the ramp gradient, the usual way it is drawn. The car presets are typical values, not a model: enter your design vehicle's wheelbase, overhangs, clearance and angles from its data sheet. The slope limit is yours to set from the local bylaw. A preliminary check, not a swept-path or headroom study.",
inputs="""
      <div class="row">
        <label for="hh">Floor to floor, m<input id="hh" type="number" step="0.1" value="3"></label>
        <label for="sl">Ramp slope %<input id="sl" type="number" step="0.5" value="15"></label>
      </div>
      <div class="row">
        <label for="lt">Transition at each end, m<input id="lt" type="number" step="0.1" value="1.5"></label>
        <label for="mg">Safety margin, mm<input id="mg" type="number" step="5" value="25"></label>
      </div>
      <label for="car">Car
        <select id="car">
          <option value="hatch" selected>Hatchback (typical)</option>
          <option value="sedan">Sedan (typical)</option>
          <option value="suv">SUV (typical)</option>
          <option value="low">Low sports car</option>
          <option value="custom">Your own car (edit below)</option>
        </select>
      </label>
      <div class="row">
        <label for="wb">Wheelbase, m<input id="wb" type="number" step="0.05" value="2.45"></label>
        <label for="gc">Belly clearance, m<input id="gc" type="number" step="0.01" value="0.17"></label>
      </div>
      <div class="row">
        <label for="fo">Front overhang, m<input id="fo" type="number" step="0.05" value="0.83"></label>
        <label for="ro">Rear overhang, m<input id="ro" type="number" step="0.05" value="0.78"></label>
      </div>
      <div class="row">
        <label for="ap">Approach angle, °<input id="ap" type="number" step="1" value="18"></label>
        <label for="dp">Departure angle, °<input id="dp" type="number" step="1" value="25"></label>
      </div>
      <label for="mx">Slope limit in your bylaw, %<input id="mx" type="number" step="0.5" value="15"></label>
      <label for="pos">Move the car <span id="posv" class="time" style="font-size:18px"></span><input id="pos" type="range" min="0" max="1000" step="1" value="500"></label>
      <button id="worst" type="button">Show the worst spot</button>
      <p class="note">The slope limit is only a check line: set it from your local bylaw. Typical ramps run 1 in 8 to 1 in 6 (12.5% to 16.7%).</p>
""",
right="""
      <div class="readout">
        <div><b>Least clearance</b><span id="oMin" class="hi">–</span></div>
        <div><b>Result</b><span id="oRes">–</span></div>
        <div><b>Shortest transition that clears</b><span id="oLt">–</span></div>
        <div><b>Ramp length in plan</b><span id="oLen">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Ramp profile with the car <span id="pfLabel"></span></h2><svg id="pf" viewBox="0 0 960 230" role="img" aria-label="Side view of the ramp with the car"></svg></div>
        <div class="view"><h2>Car at this spot <span id="zmLabel"></span></h2><svg id="zm" viewBox="0 0 420 380" role="img" aria-label="Zoomed side view of the car on the ramp"></svg></div>
        <div class="view"><h2>Clearance along the drive <span id="chLabel"></span></h2><svg id="ch" viewBox="0 0 420 380" role="img" aria-label="Clearance against car position"></svg></div>
      </div>
      <div class="data"><h2>Ramp sections for your drawing <span id="sum"></span></h2><div class="tablewrap"><table><thead><tr><th>Section</th><th>Plan length</th><th>Slope</th><th>Level change</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const PRE={hatch:[2.45,0.17,0.83,0.78,18,25],sedan:[2.65,0.15,0.95,1.00,14,18],suv:[2.70,0.21,0.92,0.95,20,25],low:[2.60,0.11,0.95,0.95,11,14]};
const IDS=["wb","gc","fo","ro","ap","dp"];
let userMoved=false,cache={key:"",val:null};
$("car").addEventListener("change",()=>{const p=PRE[$("car").value];if(p)IDS.forEach((id,i)=>{$(id).value=p[i]});render()});
IDS.forEach(id=>$(id).addEventListener("input",()=>{$("car").value="custom"}));
$("pos").addEventListener("input",()=>{userMoved=true});
$("worst").addEventListener("click",()=>{userMoved=false;render()});
function inputs(){
  const hh=num("hh",0.5,12,3),sl=num("sl",3,40,15)/100,mg=num("mg",0,200,25)/1000;
  const wb=num("wb",1.5,4,2.45),gc=num("gc",0.05,0.4,0.17),fo=num("fo",0.3,1.5,0.83),ro=num("ro",0.3,1.8,0.78);
  const ap=num("ap",3,45,18),dp=num("dp",3,45,25);
  let lt=num("lt",0,10,1.5);lt=Math.min(lt,hh/sl);
  return {hh,sl,mg,wb,gc,fo,ro,ap,dp,lt,mx:num("mx",3,40,15)/100};
}
function profile(c,lt){
  const Lm=Math.max(0,(c.hh-c.sl*lt)/c.sl),P=[[-15,0],[0,0]];
  if(lt>0)P.push([lt,-c.sl/2*lt]);
  P.push([lt+Lm,-c.sl/2*lt-c.sl*Lm]);
  if(lt>0)P.push([2*lt+Lm,-c.hh]);
  P.push([2*lt+Lm+15,-c.hh]);
  return {P,Lm,end:2*lt+Lm};
}
function yAt(P,x){
  if(x<=P[0][0])return P[0][1];
  for(let i=1;i<P.length;i++){const a=P[i-1],b=P[i];if(b[0]>a[0]&&x<=b[0])return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]);}
  return P[P.length-1][1];
}
function body(c){const ta=Math.tan(c.ap*Math.PI/180),td=Math.tan(c.dp*Math.PI/180);
  return [[-c.ro,c.ro*td],[0,c.gc],[c.wb,c.gc],[c.wb+c.fo,c.fo*ta]];}
function bodyY(B,xl){for(let i=1;i<B.length;i++){if(xl<=B[i][0]){const a=B[i-1],b=B[i];return b[0]>a[0]?a[1]+(b[1]-a[1])*(xl-a[0])/(b[0]-a[0]):b[1];}}return B[B.length-1][1];}
function frame(c,P,xr){
  const yr=yAt(P,xr);let lo=xr,hi=xr+c.wb;
  for(let k=0;k<40;k++){const m=(lo+hi)/2;if(Math.hypot(m-xr,yAt(P,m)-yr)<c.wb)lo=m;else hi=m;}
  const xf=(lo+hi)/2,yf=yAt(P,xf),ux=(xf-xr)/c.wb,uy=(yf-yr)/c.wb;
  return {R:[xr,yr],F:[xf,yf],u:[ux,uy],n:[-uy,ux]};
}
// least clearance for one car position; returns {m, part, gx}
function clearAt(c,P,B,xr,gs){
  const f=frame(c,P,xr),R=f.R,u=f.u,n=f.n;let m=1e9,part="",gx=0;
  const xs=[];for(let x=xr-c.ro-0.2;x<=f.F[0]+c.fo+0.2;x+=gs)xs.push(x);
  for(const v of P)if(v[0]>xr-c.ro-0.2&&v[0]<f.F[0]+c.fo+0.2)xs.push(v[0]);
  for(const x of xs){
    const dx=x-R[0],dy=yAt(P,x)-R[1],xl=dx*u[0]+dy*u[1],yl=dx*n[0]+dy*n[1];
    if(xl<-c.ro||xl>c.wb+c.fo)continue;
    const cl=bodyY(B,xl)-yl;
    if(cl<m){m=cl;part=xl<0?"tail":(xl>c.wb?"nose":"belly");gx=x}
  }
  return {m,part,gx};
}
function sweep(c,lt,step,gs){
  const pr=profile(c,lt),P=pr.P,B=body(c),x0=-(c.wb+c.ro+0.5),x1=pr.end+c.fo+0.5;
  const pos=[],clr=[];let best={m:1e9,xr:x0,part:"",gx:0};
  for(let xr=x0;xr<=x1+1e-9;xr+=step){const r=clearAt(c,P,B,xr,gs);pos.push(xr);clr.push(r.m);if(r.m<best.m)best={m:r.m,xr,part:r.part,gx:r.gx}}
  return {pos,clr,best,pr,x0,x1};
}
function analyse(c){
  const key=JSON.stringify(c);if(cache.key===key)return cache.val;
  const main=sweep(c,c.lt,0.05,0.02);
  let need=null;const ltMax=c.hh/c.sl;
  for(let lt=0;lt<=ltMax+1e-9;lt+=0.1){const r=sweep(c,lt,0.12,0.05);if(r.best.m>=c.mg){need=Math.round(lt*10)/10;break}}
  // steepest slope that clears with this transition
  let steep=null;
  for(let s=0.04;s<=0.331;s+=0.01){const c2=Object.assign({},c,{sl:s,lt:Math.min(c.lt,c.hh/s)});const r=sweep(c2,c2.lt,0.12,0.05);if(r.best.m>=c.mg)steep=s;else if(steep!==null)break}
  const val={main,need,steep};cache={key,val};return val;
}
function pt(f,x,y){return [f.R[0]+x*f.u[0]+y*f.n[0],f.R[1]+x*f.u[1]+y*f.n[1]]}
function carShape(c,B){
  const top=1.45+Math.max(0,c.gc-0.17),L=B.slice();
  L.push([c.wb+c.fo,0.62],[c.wb+0.38,0.82],[c.wb*0.62,top],[c.wb*0.12,top],[-c.ro+0.18,0.96],[-c.ro,0.80]);
  return L;
}
function render(){
  const c=inputs(),A=analyse(c),M=A.main,ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),ok=css("--ok"),bad=css("--bad");
  const P=M.pr.P,B=body(c),best=M.best,clear=best.m>=c.mg,mm=Math.round(best.m*1000);
  if(!userMoved)$("pos").value=Math.round(1000*(best.xr-M.x0)/(M.x1-M.x0));
  const xr=M.x0+(M.x1-M.x0)*(+$("pos").value)/1000,f=frame(c,P,xr),here=clearAt(c,P,B,xr,0.02);
  const where=best.gx>M.pr.end/2?"bottom":"top";
  $("oMin").textContent=mm+" mm";$("oMin").className="hi "+(clear?"ok":"bad");
  $("oRes").textContent=clear?"Clears":("Scrapes: "+best.part+" at the "+where);$("oRes").className=clear?"ok":"bad";
  $("oLt").textContent=A.need===null?"No length works: flatten the ramp":(A.need===0?"None needed":fmt(A.need,1)+" m each end");
  $("oLen").textContent=fmt(M.pr.end,1)+" m";
  $("posv").textContent=fmt(xr-0,1)+" m";
  // overview
  const sv=$("pf");sv.innerHTML="";const xmin=-7,xmax=M.pr.end+7,k=Math.min(960/(xmax-xmin),24),yb=48,sx=x=>(x-xmin)*k+(960-(xmax-xmin)*k)/2,sy=y=>yb+(-y)*k;
  const poly=P.map(p=>sx(p[0])+","+sy(p[1])).join(" ");
  el("polygon",{points:poly+" "+sx(xmax+10)+","+sy(-c.hh-1.5)+" "+sx(xmin-10)+","+sy(-c.hh-1.5),fill:rule,opacity:.45},sv);
  el("polyline",{points:poly,fill:"none",stroke:ink,"stroke-width":2.4},sv);
  const shape=carShape(c,B).map(q=>{const w=pt(f,q[0],q[1]);return sx(w[0])+","+sy(w[1])}).join(" ");
  el("polygon",{points:shape,fill:blue,opacity:.5,stroke:blue,"stroke-width":1.6},sv);
  [0,c.wb].forEach(x=>{const w=pt(f,x,0.31);el("circle",{cx:sx(w[0]),cy:sy(w[1]),r:0.31*k,fill:sheet,stroke:ink,"stroke-width":1.6},sv)});
  if(best.m<1e8){const gy=yAt(P,best.gx);el("circle",{cx:sx(best.gx),cy:sy(gy),r:7,fill:"none",stroke:clear?ok:bad,"stroke-width":2.5},sv)}
  const T=(x,y,t,col,a)=>el("text",{x,y,fill:col||ink2,"font-size":12,"text-anchor":a||"start","font-family":"IBM Plex Mono, monospace"},sv,t);
  T(sx(0)-4,sy(0)-12,"top of ramp",ink2,"end");T(sx(M.pr.end)+4,sy(-c.hh)-12,"bottom",ink2,"start");
  el("line",{x1:sx(M.pr.end+3.2),y1:sy(0),x2:sx(M.pr.end+3.2),y2:sy(-c.hh),stroke:ink2},sv);T(sx(M.pr.end+3.2)+6,sy(-c.hh/2)+4,fmt(c.hh,2)+" m",ink2);
  T(12,222,"slope "+fmt(c.sl*100,1)+"% (1 in "+fmt(1/c.sl,1)+") · transitions "+fmt(c.lt,1)+" m at "+fmt(c.sl*50,1)+"%",ink2);
  $("pfLabel").textContent=c.sl>c.mx+1e-9?"slope above your limit":"";
  // zoom
  const z=$("zm");z.innerHTML="";const cx=(f.R[0]+f.F[0])/2,cy=(f.R[1]+f.F[1])/2,zk=420/(c.wb+c.fo+c.ro+1.6);
  const zx=x=>210+(x-cx)*zk,zy=y=>250-(y-cy)*zk;
  const xs=[];for(let x=cx-3.8;x<=cx+3.8;x+=0.05)xs.push(x);
  el("polygon",{points:xs.map(x=>zx(x)+","+zy(yAt(P,x))).join(" ")+" "+zx(cx+3.8)+",380 "+zx(cx-3.8)+",380",fill:rule,opacity:.45},z);
  el("polyline",{points:xs.map(x=>zx(x)+","+zy(yAt(P,x))).join(" "),fill:"none",stroke:ink,"stroke-width":2.4},z);
  el("polygon",{points:carShape(c,B).map(q=>{const w=pt(f,q[0],q[1]);return zx(w[0])+","+zy(w[1])}).join(" "),fill:blue,opacity:.5,stroke:blue,"stroke-width":1.8},z);
  [0,c.wb].forEach(x=>{const w=pt(f,x,0.31);el("circle",{cx:zx(w[0]),cy:zy(w[1]),r:0.31*zk,fill:sheet,stroke:ink,"stroke-width":1.8},z)});
  if(here.m<1e8){const gy=yAt(P,here.gx),hit=here.m<c.mg;el("circle",{cx:zx(here.gx),cy:zy(gy),r:8,fill:"none",stroke:hit?bad:ok,"stroke-width":2.5},z)}
  el("text",{x:12,y:24,fill:here.m>=c.mg?ok:bad,"font-size":15,"font-family":"IBM Plex Mono, monospace"},z,"clearance here "+Math.round(here.m*1000)+" mm");
  el("text",{x:12,y:44,fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},z,here.part?("tightest: "+here.part):"");
  $("zmLabel").textContent="";
  // chart
  const s2=$("ch");s2.innerHTML="";const pL=44,pR=12,pT=24,pB=40,W=420-pL-pR,Hh=380-pT-pB;
  const vals=M.clr.map(v=>v*1000),lo=Math.min(-60,Math.min(...vals)-20),hi=Math.max(c.mg*1000+60,Math.min(400,Math.max(...vals)));
  const gx=x=>pL+(x-M.x0)/(M.x1-M.x0)*W,gy2=v=>pT+(hi-v)/(hi-lo)*Hh;
  el("line",{x1:pL,y1:gy2(0),x2:pL+W,y2:gy2(0),stroke:ink,"stroke-width":1.5},s2);
  el("line",{x1:pL,y1:gy2(c.mg*1000),x2:pL+W,y2:gy2(c.mg*1000),stroke:ok,"stroke-dasharray":"5 4"},s2);
  el("text",{x:pL+W,y:gy2(c.mg*1000)-5,fill:ok,"font-size":11,"text-anchor":"end","font-family":"IBM Plex Mono, monospace"},s2,"margin "+Math.round(c.mg*1000)+" mm");
  el("polyline",{points:M.pos.map((x,i)=>gx(x)+","+gy2(Math.min(hi,vals[i]))).join(" "),fill:"none",stroke:blue,"stroke-width":2},s2);
  el("line",{x1:gx(xr),y1:pT,x2:gx(xr),y2:pT+Hh,stroke:red,"stroke-width":1.5},s2);
  el("circle",{cx:gx(best.xr),cy:gy2(Math.min(hi,best.m*1000)),r:5,fill:clear?ok:bad},s2);
  el("text",{x:pL,y:14,fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},s2,"clearance, mm");
  el("text",{x:pL+W/2,y:372,fill:ink2,"font-size":12,"text-anchor":"middle","font-family":"IBM Plex Mono, monospace"},s2,"rear axle position along the ramp, m");
  [lo,0,hi].forEach(v=>el("text",{x:pL-6,y:gy2(v)+4,fill:ink2,"font-size":11,"text-anchor":"end","font-family":"IBM Plex Mono, monospace"},s2,Math.round(v)));
  $("chLabel").textContent="least "+mm+" mm";
  // table
  const pr=M.pr,sl2=c.sl/2*100;
  const rows=[["Level approach",fmt(15,0)+" m (shown)","0%","0 mm"]];
  if(c.lt>0)rows.push(["Top transition",fmt(c.lt,2)+" m",fmt(sl2,1)+"%","−"+Math.round(c.sl/2*c.lt*1000)+" mm"]);
  rows.push(["Main ramp",fmt(pr.Lm,2)+" m",fmt(c.sl*100,1)+"%","−"+Math.round(c.sl*pr.Lm*1000)+" mm"]);
  if(c.lt>0)rows.push(["Bottom transition",fmt(c.lt,2)+" m",fmt(sl2,1)+"%","−"+Math.round(c.sl/2*c.lt*1000)+" mm"]);
  rows.push(["Total ramp",fmt(pr.end,2)+" m","average "+fmt(c.hh/pr.end*100,1)+"%","−"+Math.round(c.hh*1000)+" mm"]);
  if(A.steep!==null)rows.push(["Steepest slope that clears","with these transitions",fmt(A.steep*100,0)+"%",""]);
  $("tb").innerHTML=rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("");
  $("sum").textContent="";
}
""")
