APP = dict(
slug="daylight-factor", title="Daylight Factor & Window Size", h1="Daylight Factor",
sub="Is the window big enough? Average daylight factor from room size, glass and what's outside, checked against the target for the room and the NBC window rule.",
meta=[("Sheet","T-10"),("Method","BRE avg. DF"),("Targets","IS 2440 / SP 41"),("By","@smart_tools_every_week")],
source="ADF = T·Aw·θ·M / (A(1−R²)) and depth rule per BRE BR 209 (Littlefair). Targets: IS 2440:1975 / SP 41 (India), BS 8206-2 (UK). Window ≥ floor fraction per NBC 2016 Pt 3 cl 8.1. An estimate for early design, not a simulation.",
inputs="""
      <label for="room">Room type · target DF
        <select id="room">
          <option value="1.9" selected>Office, general · 1.9%</option>
          <option value="3.75">Drawing office · 3.75%</option>
          <option value="1.9c">Classroom · 1.9%</option>
          <option value="2.5">Kitchen · 2.5%</option>
          <option value="1.9s">Study room · 1.9%</option>
          <option value="0.625">Living room · 0.625%</option>
          <option value="1.25">Hospital ward · 1.25%</option>
          <option value="2uk">Kitchen · 2% UK</option>
          <option value="1.5uk">Living room · 1.5% UK</option>
          <option value="1uk">Bedroom · 1% UK</option>
        </select>
      </label>
      <div class="row">
        <label for="W">Room width (window wall) m<input id="W" type="number" step="0.1" value="4"></label>
        <label for="D">Room depth m<input id="D" type="number" step="0.1" value="6"></label>
      </div>
      <div class="row">
        <label for="H">Ceiling height m<input id="H" type="number" step="0.05" value="3"></label>
        <label for="N">No. of windows<input id="N" type="number" step="1" value="1"></label>
      </div>
      <label for="ww">Window width m <span id="wwv" class="time" style="font-size:18px"></span><input id="ww" type="range" min="0.3" max="6" step="0.05" value="2"></label>
      <div class="row">
        <label for="wh">Window height m<input id="wh" type="number" step="0.05" value="1.2"></label>
        <label for="sill">Sill height m<input id="sill" type="number" step="0.05" value="0.9"></label>
      </div>
      <div class="row">
        <label for="glass">Glass
          <select id="glass"><option value="0.8">Single</option><option value="0.7">Double</option><option value="0.6">Low-E</option><option value="0.45">Tinted</option></select>
        </label>
        <label for="frame">Frame % of window<input id="frame" type="number" step="5" value="20"></label>
      </div>
      <label for="obs">Obstruction angle outside ° <span id="obsv" class="time" style="font-size:18px"></span><input id="obs" type="range" min="0" max="70" step="1" value="15"></label>
      <div class="row">
        <label for="rw">Wall reflectance<input id="rw" type="number" step="0.05" value="0.6"></label>
        <label for="rc">Ceiling reflectance<input id="rc" type="number" step="0.05" value="0.8"></label>
      </div>
      <div class="row">
        <label for="rf">Floor reflectance<input id="rf" type="number" step="0.05" value="0.3"></label>
        <label for="M">Dirt / maintenance<input id="M" type="number" step="0.05" value="0.9"></label>
      </div>
      <label for="clim">Climate (NBC window rule)
        <select id="clim"><option value="10">Hot-dry · 1/10 of floor</option><option value="6">Warm-humid · 1/6 of floor</option><option value="8">Temperate · 1/8 of floor</option><option value="12">Cold · 1/12 of floor</option></select>
      </label>
      <p class="note">Obstruction angle: how high the building or trees opposite rise above the window centre, seen from the window. 0° = open sky. Targets: IS 2440 / SP 41 unless marked UK (BS 8206-2). Indian daylight factors are set for an 8,000 lux design sky, so 1.9% ≈ 150 lux.</p>
""",
right="""
      <div class="readout">
        <div><b>Average DF</b><span id="oDF" class="hi">–</span></div>
        <div><b>Target</b><span id="oT">–</span></div>
        <div><b>Daylight ≈</b><span id="oLux">–</span></div>
        <div><b>Window / floor</b><span id="oWF">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Section <span id="secLabel"></span></h2><svg id="sec" viewBox="0 0 420 330" role="img" aria-label="Room section with sky angle"></svg></div>
        <div class="view"><h2>Plan <span id="planLabel"></span></h2><svg id="plan" viewBox="0 0 420 330" role="img" aria-label="Room plan with daylit depth"></svg></div>
      </div>
      <div class="data">
        <h2>Checks <span id="sum"></span></h2>
        <ul class="checks" id="checks"></ul>
      </div>
      <div class="data" style="border-top:1px solid var(--rule)">
        <h2>Working <span>ADF = T × Aw × θ × M ÷ (A × (1 − R²))</span></h2>
        <div class="tablewrap"><table><thead><tr><th>Step</th><th>Value</th><th>Note</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function adf(o){
  const Ag=o.N*o.ww*o.wh,Aw=Ag*(1-o.frame/100),floor=o.W*o.D,walls=2*(o.W+o.D)*o.H,A=2*floor+walls;
  const R=(o.rf*floor+o.rc*floor+o.rw*Math.max(0,walls-Ag)+0.1*Ag)/A;
  const th=90-o.obs,DF=o.T*Aw*th*o.M/(A*(1-R*R));
  return {Ag,Aw,floor,walls,A,R,th,DF};
}
function read(){
  const W=num("W",1,50,4),D=num("D",1,50,6),H=num("H",2,10,3);
  let wh=num("wh",0.2,H,1.2);const sill=num("sill",0,Math.max(0,H-wh),0.9);
  const N=Math.round(num("N",1,20,1));const ww=Math.min(num("ww",0.3,50,2),W/N);
  return {W,D,H,N,ww,wh,sill,T:+$("glass").value,frame:num("frame",0,60,20),obs:num("obs",0,80,15),
    rw:num("rw",0.05,0.95,0.6),rc:num("rc",0.05,0.95,0.8),rf:num("rf",0.05,0.95,0.3),M:num("M",0.5,1,0.9),clim:+$("clim").value,target:parseFloat($("room").value)};
}
function render(){
  const o=read(),r=adf(o),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),ok=css("--ok"),paper=css("--paper");
  const pass=r.DF>=o.target, lux=r.DF/100*8000, wf=r.Ag/r.floor;
  $("wwv").textContent=o.ww.toFixed(2)+" m";$("obsv").textContent=o.obs+"°";
  $("oDF").textContent=fmt(r.DF,2)+"%";$("oDF").className=pass?"ok":"bad";
  $("oT").textContent=o.target+"%";$("oLux").textContent=Math.round(lux)+" lux";$("oWF").textContent="1/"+(1/wf).toFixed(1);
  // limiting depth (BRE): D/W + D/Hh <= 2/(1-R)
  const Hh=o.sill+o.wh,lhs=o.D/o.W+o.D/Hh,rhs=2/(1-r.R);
  const Dmax=rhs/(1/o.W+1/Hh);
  // window needed for target at the current height (R held constant)
  const AwNeed=o.target*r.A*(1-r.R*r.R)/(o.T*r.th*o.M),AgNeed=AwNeed/(1-o.frame/100),wwNeed=AgNeed/(o.N*o.wh);
  const C=[[`Average DF ${fmt(r.DF,2)}% ≥ target ${o.target}%`,pass],
    [`Window ${fmt(r.Ag,2)} m² ≥ 1/${o.clim} of floor (${fmt(r.floor/o.clim,2)} m², NBC)`,r.Ag>=r.floor/o.clim-1e-9],
    [`Room depth ${fmt(o.D,1)} m ≤ ${fmt(Dmax,1)} m daylit depth (BRE rule)`,lhs<=rhs,"warn"],
    [pass?`Target met. Window could shrink to ${fmt(Math.max(0,wwNeed),2)} m wide`:(wwNeed*o.N<=o.W?`Widen each window to ${fmt(wwNeed,2)} m to meet the target`:`Even a full-width window falls short: raise the head, cut the obstruction or lighten the finishes`),true,"info"]];
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"fix":okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // SECTION
  const sv=$("sec");sv.innerHTML="";
  const span=o.D+Math.max(3,o.H*1.6),sc=Math.min(392/span,250/(o.H+1.2));const ox=Math.max(14,(420-span*sc)/2+Math.max(3,o.H*1.6)*sc*0),gy=290;
  const wx=ox+Math.max(3,o.H*1.6)*sc; // window wall x
  const X=v=>wx+v*sc,Y=v=>gy-v*sc;
  // obstruction building
  const dist=Math.max(3,o.H*1.6)*0.85;const wc=o.sill+o.wh/2;const obH=wc+Math.tan(o.obs*Math.PI/180)*dist;
  if(o.obs>0){el("rect",{x:X(-dist)-24,y:Y(Math.min(obH,o.H+1.1)),width:24,height:Y(0)-Y(Math.min(obH,o.H+1.1)),fill:rule,stroke:ink2},sv);}
  // sky wedge from window centre
  const cx=X(0),cy=Y(wc),Rr=Math.max(30,Math.min(cy-12,dist*sc*1.1));
  const a0=Math.PI-o.obs*Math.PI/180; // direction to obstruction top (left & up)
  const p0=[cx+Rr*Math.cos(a0),cy-Rr*Math.sin(a0)],p1=[cx,cy-Rr];
  el("path",{d:`M${cx} ${cy} L${p0[0]} ${p0[1]} A${Rr} ${Rr} 0 0 1 ${p1[0]} ${p1[1]} Z`,fill:sun,opacity:.22,stroke:sun,"stroke-width":1},sv);
  el("line",{x1:cx,y1:cy,x2:cx-Rr*1.05,y2:cy,stroke:ink2,"stroke-dasharray":"3 3"},sv);
  el("text",{x:cx-Rr*0.55,y:cy-Rr*0.55,fill:sun,"font-size":13,"font-weight":600,"font-family":"IBM Plex Mono, monospace","text-anchor":"middle"},sv,"θ "+r.th+"°");
  if(o.obs>0)el("text",{x:cx-Rr*0.95,y:cy-6,fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},sv,o.obs+"°");
  // room shell
  el("line",{x1:6,y1:Y(0),x2:414,y2:Y(0),stroke:ink,"stroke-width":2},sv);
  el("rect",{x:X(0),y:Y(o.H),width:o.D*sc,height:o.H*sc,fill:paper,stroke:"none"},sv);
  // daylit gradient on floor
  const lim=Math.min(o.D,Dmax);el("rect",{x:X(0),y:Y(0)-6,width:lim*sc,height:6,fill:pass?ok:red,opacity:.55},sv);
  el("line",{x1:X(0),y1:Y(o.H),x2:X(o.D),y2:Y(o.H),stroke:ink,"stroke-width":2},sv);
  el("line",{x1:X(o.D),y1:Y(0),x2:X(o.D),y2:Y(o.H),stroke:ink,"stroke-width":2},sv);
  el("line",{x1:X(0),y1:Y(0),x2:X(0),y2:Y(o.sill),stroke:ink,"stroke-width":3},sv);
  el("line",{x1:X(0),y1:Y(o.sill+o.wh),x2:X(0),y2:Y(o.H),stroke:ink,"stroke-width":3},sv);
  el("line",{x1:X(0),y1:Y(o.sill),x2:X(0),y2:Y(o.sill+o.wh),stroke:blue,"stroke-width":2},sv);
  // light rays into room
  [0.2,0.5,0.8].forEach(f=>{const yy=o.sill+o.wh*f;el("line",{x1:X(0),y1:Y(yy),x2:X(Math.min(o.D,(yy)/Math.tan(Math.max(10,o.obs+10)*Math.PI/180))),y2:Y(0),stroke:sun,"stroke-width":1,opacity:.6},sv)});
  el("text",{x:X(o.D/2),y:Y(o.H/2),"text-anchor":"middle",fill:pass?ok:red,"font-size":22,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},sv,fmt(r.DF,2)+"%");
  el("text",{x:X(o.D/2),y:Y(o.H/2)+18,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"average DF");
  el("text",{x:X(o.D),y:Y(0)+16,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"depth "+fmt(o.D,1)+" m");
  el("text",{x:X(0)+4,y:Y(0)+16,fill:pass?ok:red,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"lit depth "+fmt(lim,1)+" m");
  $("secLabel").textContent="sky angle θ = 90° − obstruction";
  // PLAN
  const pv=$("plan");pv.innerHTML="";const k=Math.min(360/o.W,250/o.D),px=(420-o.W*k)/2,py=30;
  el("rect",{x:px,y:py,width:o.W*k,height:o.D*k,fill:paper,stroke:ink,"stroke-width":2},pv);
  el("rect",{x:px,y:py+o.D*k-lim*k,width:o.W*k,height:lim*k,fill:pass?ok:red,opacity:.12},pv);
  if(lim<o.D)el("line",{x1:px,y1:py+o.D*k-lim*k,x2:px+o.W*k,y2:py+o.D*k-lim*k,stroke:red,"stroke-dasharray":"5 4"},pv);
  const gap=(o.W-o.N*o.ww)/(o.N+1);
  for(let i=0;i<o.N;i++){const x0=px+(gap+(gap+o.ww)*i)*k;el("rect",{x:x0,y:py+o.D*k-3,width:o.ww*k,height:6,fill:blue},pv);
    el("path",{d:`M${x0} ${py+o.D*k} L${x0+o.ww*k/2} ${py+o.D*k-Math.min(lim*k,o.ww*k*1.2)} L${x0+o.ww*k} ${py+o.D*k}Z`,fill:sun,opacity:.25},pv)}
  el("text",{x:px+o.W*k/2,y:py+o.D*k+20,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pv,"window wall "+fmt(o.W,1)+" m · glass "+fmt(r.Ag,2)+" m²");
  el("text",{x:px+o.W*k/2,y:py-10,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pv,"floor "+fmt(r.floor,1)+" m²");
  el("text",{x:px+o.W*k/2,y:py+o.D*k*0.35,"text-anchor":"middle",fill:pass?ok:red,"font-size":20,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},pv,fmt(r.DF,2)+"% / "+o.target+"%");
  el("text",{x:px+o.W*k/2,y:py+o.D*k*0.35+18,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pv,pass?"meets target":"below target");
  $("planLabel").textContent=lim<o.D?"back of room under-lit":"daylit to the back wall";
  // TABLE
  const rows=[["Window (gross)",fmt(r.Ag,2)+" m²",o.N+" × "+fmt(o.ww,2)+" × "+fmt(o.wh,2)],["Net glazed Aw",fmt(r.Aw,2)+" m²","minus "+o.frame+"% frame"],
    ["Room surfaces A",fmt(r.A,1)+" m²","floor + ceiling + walls"],["Mean reflectance R",fmt(r.R,3),"area-weighted, glass 0.10"],
    ["Sky angle θ",r.th+"°","90° − "+o.obs+"° obstruction"],["Glass T × M",fmt(o.T,2)+" × "+fmt(o.M,2),"transmittance × dirt"],
    ["Average DF",fmt(r.DF,2)+"%","target "+o.target+"%"],["Indoor daylight",Math.round(lux)+" lux","at 8,000 lux design sky"],
    ["Depth rule",fmt(lhs,2)+" ≤ "+fmt(rhs,2),"D/W + D/h ≤ 2/(1−R)"]];
  const tb=$("tbl");tb.innerHTML="";rows.forEach(rw=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${rw[0]}</td><td>${rw[1]}</td><td>${rw[2]}</td>`;tb.appendChild(tr)});
}
""")
