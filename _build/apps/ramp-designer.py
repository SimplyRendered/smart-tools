APP = dict(
slug="ramp-designer", title="Accessible Ramp Designer", h1="Accessible Ramp",
sub="Enter the level difference. Get the runs, landings, total length and plan footprint of a wheelchair ramp, checked against ADA 2010, UK Part M or your own code.",
meta=[("Sheet","T-11"),("Code","ADA 2010 §405 / ADM"),("Units","mm"),("By","@smart_tools_every_week")],
source="ADA 2010 Standards §405 & §505 (US Access Board). UK Approved Document M Vol 2 (2015) Table 2. For India, pick Custom and enter your authority's limits (Harmonised Guidelines 2021 / local bylaws).",
inputs="""
      <label for="code">Code
        <select id="code">
          <option value="ada" selected>ADA 2010 (US)</option>
          <option value="adm">Approved Doc. M (UK)</option>
          <option value="cus">Custom / local code</option>
        </select>
      </label>
      <label for="rise">Level difference mm <span id="risev" class="time" style="font-size:18px"></span><input id="rise" type="number" step="10" value="900"></label>
      <label for="n">Gradient 1 : n <span id="nv" class="time" style="font-size:18px"></span><input id="n" type="range" min="8" max="25" step="0.5" value="12"></label>
      <label for="lay">Layout
        <select id="lay"><option value="straight">Straight run</option><option value="switch">Switchback (U-turns)</option></select>
      </label>
      <div class="row">
        <label for="W">Clear width mm<input id="W" type="number" step="50" value="1200"></label>
        <label for="L">Landing length mm<input id="L" type="number" step="25" value="1525"></label>
      </div>
      <div class="row">
        <label for="nmax">Steepest 1 : n<input id="nmax" type="number" step="0.5" value="12"></label>
        <label for="rmax">Max rise / run mm<input id="rmax" type="number" step="10" value="760"></label>
      </div>
      <div class="row">
        <label for="wmin">Min width mm<input id="wmin" type="number" step="25" value="915"></label>
        <label for="hr">Handrails if rise &gt; mm<input id="hr" type="number" step="10" value="150"></label>
      </div>
      <p class="note">ADA: 1:12 max, 760 mm (30 in) rise per run, 1525 mm (60 in) landings top, bottom and between runs, 915 mm (36 in) clear width, handrails both sides at 865–965 mm when the rise is over 150 mm. Part M: steeper ramps must be shorter (1:12 for 2 m, 1:15 for 5 m, 1:20 for 10 m), 500 mm max rise per flight.</p>
""",
right="""
      <div class="readout">
        <div><b>Total length</b><span id="oLen" class="hi">–</span></div>
        <div><b>Sloped runs</b><span id="oRuns">–</span></div>
        <div><b>Landings</b><span id="oLand">–</span></div>
        <div><b>Footprint</b><span id="oFoot">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Section <span id="secLabel"></span></h2><svg id="sec" viewBox="0 0 840 260" role="img" aria-label="Ramp section"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Plan <span id="planLabel"></span></h2><svg id="plan" viewBox="0 0 420 330" role="img" aria-label="Ramp plan"></svg></div>
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="data">
        <h2>Run schedule <span>levels above the lower floor</span></h2>
        <div class="tablewrap"><table><thead><tr><th>Element</th><th>From (mm)</th><th>To (mm)</th><th>Length (mm)</th><th>Starts at (mm)</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
css=".view.full svg{max-height:260px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const PRE={ada:{nmax:12,rmax:760,wmin:915,L:1525,hr:150},adm:{nmax:12,rmax:500,wmin:1500,L:1500,hr:0},cus:null};
function lockPreset(){const c=$("code").value,p=PRE[c];["nmax","rmax","wmin","hr"].forEach(id=>{$(id).disabled=!!p});
  if(p){$("nmax").value=p.nmax;$("rmax").value=p.rmax;$("wmin").value=p.wmin;$("hr").value=p.hr;$("L").value=p.L;}}
$("code").addEventListener("change",()=>{lockPreset();render()});
// UK ADM Vol 2 Table 2: going 2 m @1:12, 5 m @1:15, 10 m @1:20 (interpolate); max rise 500 mm
function admMaxRise(n){if(n<12)return 0;if(n>20)return Infinity;const g=n<=15?2000+(n-12)/3*3000:5000+(n-15)/5*5000;return Math.min(500,g/n);}
function ramp(){
  const code=$("code").value,rise=num("rise",10,10000,900),n=num("n",4,40,12),W=num("W",500,5000,1200),L=num("L",500,5000,1525);
  const nmax=num("nmax",4,40,12),rmaxIn=num("rmax",20,10000,760),wmin=num("wmin",0,5000,915),hr=num("hr",0,2000,150);
  const rmax=code==="adm"?admMaxRise(n):rmaxIn;
  const okSlope=n>=nmax-1e-9;
  const k=Math.max(1,Math.ceil(rise/Math.max(1,(Number.isFinite(rmax)&&rmax>0?rmax:rise))-1e-9));
  const kk=Math.min(k,200);
  const G=rise*n,run=G/kk,landings=kk+1;
  const total=G+landings*L, lay=$("lay").value;
  const foot=lay==="straight"?[total,W]:[run+2*L,kk*W+(kk-1)*150];
  return {code,rise,n,W,L,nmax,rmax,wmin,hr,okSlope,k:kk,G,run,landings,total,lay,foot,pct:100/n};
}
function render(){
  const s=ramp(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),ok=css("--ok"),paper=css("--paper");
  $("risev").textContent="";$("nv").textContent="1:"+s.n+"  ("+fmt(s.pct,1)+"%)";
  $("oLen").textContent=(s.total/1000).toFixed(2)+" m";$("oRuns").textContent=s.k+" × "+(s.run/1000).toFixed(2)+" m";
  $("oLand").textContent=s.landings+" × "+(s.L/1000).toFixed(2)+" m";$("oFoot").textContent=(s.foot[0]/1000).toFixed(1)+"×"+(s.foot[1]/1000).toFixed(1)+" m";
  const perRun=s.rise/s.k;
  const C=[[`Gradient 1:${s.n} (${fmt(s.pct,1)}%) no steeper than 1:${s.nmax}`,s.okSlope],
    [s.code==="adm"?`Rise per flight ${fmt(perRun,0)} mm ≤ ${s.rmax===0?"0 (too steep)":Number.isFinite(s.rmax)?fmt(s.rmax,0):"no limit"} mm for 1:${s.n} (Part M Table 2)`:`Rise per run ${fmt(perRun,0)} mm ≤ ${fmt(s.rmax,0)} mm`,s.rmax>0&&perRun<=s.rmax+1e-6],
    [`Clear width ${s.W} mm ≥ ${s.wmin} mm`,s.W>=s.wmin],
    [`Landings ${s.L} mm long at the bottom, top and between runs`,true,"info"],
    [s.rise>s.hr?`Handrails both sides (rise ${s.rise} mm > ${s.hr} mm)${s.code==="ada"?", 865–965 mm high, 305 mm extensions":""}`:"Handrails not required at this rise",true,"info"],
    [`Cross slope ≤ 1:48 and edge kerb or rail on open sides`,true,"info"]];
  if(s.lay==="switch")C.push([`Turn landings at least ${s.code==="ada"?"1525 × 1525":s.L+" × "+s.L} mm clear`,true,"info"]);
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":"bad";if(!okk)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all limits met";
  // SECTION unfolded
  const sv=$("sec");sv.innerHTML="";const sc=780/s.total,sv2=Math.min(170/s.rise,sc*6),ox=(840-s.total*sc)/2,gy=215;
  const X=v=>ox+v*sc,Y=v=>gy-v*sv2;const ve=sv2/sc;$("secLabel").textContent=ve>1.05?"unfolded · heights ×"+ve.toFixed(1):"unfolded, to scale";
  el("line",{x1:0,y1:gy,x2:X(0),y2:gy,stroke:ink,"stroke-width":2},sv);
  let x=0,y=0,d=`M${X(0)} ${Y(0)}`;const rows=[];
  el("rect",{x:X(0),y:Y(0)-3,width:s.L*sc,height:3,fill:blue},sv);rows.push(["Bottom landing",0,0,s.L,0]);x+=s.L;d+=` L${X(x)} ${Y(0)}`;
  for(let i=0;i<s.k;i++){const y2=y+perRun;d+=` L${X(x+s.run)} ${Y(y2)}`;rows.push(["Run "+(i+1)+" (1:"+s.n+")",y,y2,s.run,x]);
    if(s.k<=12)el("text",{x:X(x+s.run/2),y:Y((y+y2)/2)-8,"text-anchor":"middle",fill:red,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,(s.run/1000).toFixed(2)+" m");
    x+=s.run;y=y2;const lab=i<s.k-1?"Landing "+(i+1):"Top landing";el("rect",{x:X(x),y:Y(y)-3,width:s.L*sc,height:3,fill:blue},sv);rows.push([lab,y,y,s.L,x]);d+=` L${X(x+s.L)} ${Y(y)}`;x+=s.L;}
  el("path",{d:d+` L${X(x)} ${gy} L${X(0)} ${gy} Z`,fill:rule,opacity:.6},sv);
  el("path",{d,fill:"none",stroke:ink,"stroke-width":2},sv);
  el("line",{x1:X(x),y1:Y(s.rise),x2:840,y2:Y(s.rise),stroke:ink,"stroke-width":2},sv);
  el("line",{x1:X(0),y1:gy+18,x2:X(s.total),y2:gy+18,stroke:ink2},sv);
  el("text",{x:X(s.total/2),y:gy+32,"text-anchor":"middle",fill:ink,"font-size":12,"font-weight":500,"font-family":"IBM Plex Mono, monospace"},sv,"total "+(s.total/1000).toFixed(2)+" m  ·  rise "+s.rise+" mm");
  el("text",{x:X(x),y:Y(s.rise)-10,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"FFL +"+s.rise);el("text",{x:X(0),y:gy-10,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"±0");
  // PLAN
  const pv=$("plan");pv.innerHTML="";const F=s.foot,k=Math.min(390/F[0],230/F[1]),px=(420-F[0]*k)/2,py=(320-F[1]*k)/2+10;
  const R=(x,y,w,h,f,st)=>el("rect",{x:px+x*k,y:py+y*k,width:Math.max(0.5,w*k),height:Math.max(0.5,h*k),fill:f,stroke:st||ink,"stroke-width":1.2},pv);
  const arrow=(x1,x2,yy)=>{el("line",{x1:px+x1*k,y1:py+yy*k,x2:px+x2*k,y2:py+yy*k,stroke:red,"stroke-width":1.5},pv);const dir=Math.sign(x2-x1);
    el("path",{d:`M${px+x2*k} ${py+yy*k} l${-8*dir} -4 v8z`,fill:red},pv)};
  if(s.lay==="straight"){let xx=0;R(0,0,s.L,s.W,paper);xx=s.L;for(let i=0;i<s.k;i++){R(xx,0,s.run,s.W,rule);arrow(xx+s.run*0.1,xx+s.run*0.9,s.W/2);xx+=s.run;R(xx,0,s.L,s.W,paper);xx+=s.L;}
    el("text",{x:px+4,y:py-6,fill:red,"font-size":11,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif"},pv,"UP →");}
  else{const g=150;for(let i=0;i<s.k;i++){const yy=i*(s.W+g),fwd=i%2===0;R(s.L,yy,s.run,s.W,rule);
      fwd?arrow(s.L+s.run*0.1,s.L+s.run*0.9,yy+s.W/2):arrow(s.L+s.run*0.9,s.L+s.run*0.1,yy+s.W/2);}
    // landings: bottom at left of run1, turns alternate right/left spanning two runs, top at the end
    R(0,0,s.L,s.W,paper);
    for(let i=0;i<s.k-1;i++){const right=i%2===0,yy=i*(s.W+g);R(right?s.L+s.run:0,yy,s.L,2*s.W+g,paper);}
    const last=s.k-1,yl=last*(s.W+g);if(s.k%2===1)R(s.L+s.run,yl,s.L,s.W,paper);else R(0,yl,s.L,s.W,paper);
    el("text",{x:px+4,y:py-6,fill:red,"font-size":11,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif"},pv,"UP");}
  $("planLabel").textContent=(F[0]/1000).toFixed(2)+" × "+(F[1]/1000).toFixed(2)+" m";
  const tb=$("tbl");tb.innerHTML="";rows.forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${r[0]}</td><td>${r[1].toFixed(0)}</td><td>${r[2].toFixed(0)}</td><td>${r[3].toFixed(0)}</td><td>${r[4].toFixed(0)}</td>`;tb.appendChild(tr)});
}
lockPreset();
""")
