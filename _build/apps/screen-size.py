APP = dict(
slug="screen-size", title="Screen Size for a Room", h1="Screen Size for a Room",
sub="Enter how far the back and front rows sit and what people will look at. Get the screen size the room really needs, where to mount it, the ceiling and viewing-angle checks and the projector throw, on a live section and plan.",
meta=[("Sheet","T-42"),("Method","4/6/8 image-height rule"),("Units","m, inches"),("By","@smart_tools_every_week")],
source="Image height ≥ farthest viewer ÷ 4 (fine detail, CAD), ÷ 6 (reading text, spreadsheets) or ÷ 8 (video, images); closest viewer ≥ 2 × image height; screen bottom about 1.1 to 1.2 m above the floor; viewers within 30° of the screen axis (45° at most); screen centre no more than 20° above eye level (Projection Rules, proav.de, after the InfoComm/AVIXA 4/6/8 rule). The newer ANSI/AVIXA V202.01:2016 (DISCAS) sizes from the actual content and is worth using for critical rooms. Throw distance = throw ratio × image width.",
inputs="""
      <div class="row">
        <label for="far">Farthest viewer m<input id="far" type="number" step="0.1" value="8.5"></label>
        <label for="near">Closest viewer m<input id="near" type="number" step="0.1" value="3.0"></label>
      </div>
      <label for="ct">What they look at
        <select id="ct">
          <option value="4">Fine detail, CAD, drawings · ÷4</option>
          <option value="6" selected>Text, slides, spreadsheets · ÷6</option>
          <option value="8">Video, pictures · ÷8</option>
        </select>
      </label>
      <div class="row">
        <label for="ar">Aspect
          <select id="ar"><option value="16,9" selected>16:9</option><option value="16,10">16:10</option><option value="4,3">4:3</option><option value="21,9">21:9</option></select>
        </label>
        <label for="pl">Planned display inch<input id="pl" type="number" step="1" value="86"></label>
      </div>
      <div class="row">
        <label for="ch">Ceiling height m<input id="ch" type="number" step="0.05" value="3.0"></label>
        <label for="sb">Screen bottom m<input id="sb" type="number" step="0.05" value="1.2"></label>
      </div>
      <div class="row">
        <label for="eye">Seated eye height m<input id="eye" type="number" step="0.05" value="1.2"></label>
        <label for="hw">Front row half-width m<input id="hw" type="number" step="0.1" value="1.6"></label>
      </div>
      <label for="tr">Projector throw ratio<input id="tr" type="number" step="0.05" value="1.5"></label>
      <p class="note">Distances are measured from the screen. Front row half-width: from the room centre line to the outer seat of the front row. Throw ratio is in the projector's data sheet (short throw about 0.5, standard 1.2 to 2.0). Displays are sized by their diagonal in inches.</p>
""",
right="""
      <div class="readout">
        <div><b>Screen needed</b><span id="oD" class="hi">–</span></div>
        <div><b>Image height</b><span id="oH">–</span></div>
        <div><b>Planned display reads to</b><span id="oP">–</span></div>
        <div><b>Projector throw</b><span id="oT">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Section <span id="seL"></span></h2><svg id="se" viewBox="0 0 580 215" role="img" aria-label="Room section with the screen and the viewers"></svg></div>
        <div class="view"><h2>Plan <span id="plL"></span></h2><svg id="pn" viewBox="0 0 420 300" role="img" aria-label="Plan with viewing angles"></svg></div>
        <div class="view"><h2>Checks <span id="ckL"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="data"><h2>Standard sizes in this room <span id="dtL"></span></h2><div class="tablewrap"><table><thead><tr><th>Diagonal</th><th>Width × height</th><th>Readable to</th><th>Front row from</th><th>Top edge</th><th>Throw</th><th></th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css=".view.full svg{max-height:320px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const SIZES=[55,65,75,86,98,110,120,135,150,180,200];
const IN=0.0254,deg=r=>r*180/Math.PI;
function calc(){
  const [aw,ah]=$("ar").value.split(",").map(Number);const k=[4,6,8].includes(+$("ct").value)?+$("ct").value:6;
  const p={far:num("far",1,100,8.5),near:num("near",0.3,50,2.5),k,aw,ah,pl:num("pl",10,400,86),ch:num("ch",2,30,3),sb:num("sb",0,10,1.2),eye:num("eye",0.5,3,1.2),hw:num("hw",0,30,1.6),tr:num("tr",0.1,10,1.5)};
  if(p.near>p.far)p.near=p.far;
  const hk=Math.hypot(aw,ah);p.hf=ah/hk;p.wf=aw/hk; // height and width per unit diagonal
  p.hMin=p.far/k;p.hMax=p.near/2;p.h=p.hMin;p.w=p.h*aw/ah;p.diag=p.h/p.hf/IN;
  p.top=p.sb+p.h;p.throwD=p.tr*p.w;
  p.vang=deg(Math.atan((p.sb+p.h/2-p.eye)/p.near));p.hang=deg(Math.atan(p.hw/p.near));
  p.plH=p.pl*IN*p.hf;p.plW=p.pl*IN*p.wf;p.plReach=p.plH*k;
  p.checks=[
    ["Closest row at least 2 × image height",p.near>=2*p.h-1e-9,`${fmt(p.near,1)} m vs ${fmt(2*p.h,2)} m`],
    ["Top of image below the ceiling",p.top<=p.ch-0.05,`top at ${fmt(p.top,2)} m, ceiling ${fmt(p.ch,2)} m`],
    ["Screen centre ≤ 20° above front-row eyes",p.vang<=20,`${fmt(p.vang,1)}°`],
    ["Front row within 45° of the axis",p.hang<=45,`${fmt(p.hang,0)}° (ideal ≤ 30°)`],
    ["Planned "+Math.round(p.pl)+"\" display big enough",p.plReach>=p.far-1e-9,`readable to ${fmt(p.plReach,1)} m`]];
  return p;
}
function render(){
  const p=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun"),ok=css("--ok"),bad=css("--bad");
  const M="IBM Plex Mono, monospace";
  $("oD").textContent=Math.ceil(p.diag)+"\"";$("oH").textContent=fmt(p.h,2)+" m";
  $("oP").textContent=fmt(p.plReach,1)+" m";$("oP").className=p.plReach>=p.far-1e-9?"ok":"bad";
  $("oT").textContent=fmt(p.throwD,2)+" m";
  // section
  const sv=$("se");sv.innerHTML="";const D=Math.max(p.far+1,p.throwD+0.5),Hh=Math.max(p.ch,p.top+0.2),sc=Math.min(480/D,180/Hh),x0=56,gy=205,X=d=>x0+d*sc,Y=h=>gy-h*sc;
  el("line",{x1:x0-20,y1:gy,x2:X(D),y2:gy,stroke:ink,"stroke-width":2},sv);
  el("line",{x1:x0-20,y1:Y(p.ch),x2:X(D),y2:Y(p.ch),stroke:ink,"stroke-width":2},sv);
  el("line",{x1:x0,y1:gy,x2:x0,y2:Y(p.ch),stroke:ink,"stroke-width":3},sv);
  const top=p.top>p.ch-0.05;
  el("rect",{x:x0,y:Y(p.top),width:6,height:p.h*sc,fill:top?bad:blue},sv);
  if(p.plH>0)el("rect",{x:x0+8,y:Y(p.sb+p.plH),width:4,height:p.plH*sc,fill:sun},sv);
  const ce=p.sb+p.h/2;
  for(const [d,c,lab] of [[p.near,ink2,"front"],[p.far,red,"back"]]){
    el("circle",{cx:X(d),cy:Y(p.eye),r:7,fill:c},sv);el("line",{x1:X(d),y1:Y(p.eye)+7,x2:X(d),y2:gy,stroke:c,"stroke-width":2},sv);
    el("line",{x1:X(d),y1:Y(p.eye),x2:x0+6,y2:Y(p.top),stroke:c,"stroke-dasharray":"5 4",opacity:.8},sv);
    el("line",{x1:X(d),y1:Y(p.eye),x2:x0+6,y2:Y(p.sb),stroke:c,"stroke-dasharray":"5 4",opacity:.8},sv);
    el("text",{x:X(d),y:Y(p.eye)-14,"text-anchor":"middle",fill:c,"font-size":13,"font-family":M},sv,`${fmt(d,1)} m`)}
  // projector
  if(p.throwD<D){el("rect",{x:X(p.throwD)-12,y:Y(p.ch)+4,width:24,height:12,fill:ink2},sv);
    el("line",{x1:X(p.throwD)-12,y1:Y(p.ch)+10,x2:x0+6,y2:Y(p.top),stroke:sun,opacity:.6},sv);el("line",{x1:X(p.throwD)-12,y1:Y(p.ch)+10,x2:x0+6,y2:Y(p.sb),stroke:sun,opacity:.6},sv);
    el("text",{x:X(p.throwD),y:Y(p.ch)+32,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":M},sv,`projector ${fmt(p.throwD,2)} m`)}
  el("text",{x:x0+14,y:Y(p.top)-6,fill:ink,"font-size":13,"font-family":M},sv,`${Math.ceil(p.diag)}" · ${fmt(p.h,2)} m high`);
  el("text",{x:x0+14,y:Y(p.sb)+16,fill:sun,"font-size":12,"font-family":M},sv,`planned ${Math.round(p.pl)}" = ${fmt(p.plH,2)} m high`);
  el("text",{x:x0-8,y:Y(p.sb)+4,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":M},sv,fmt(p.sb,2));
  $("seL").textContent=`farthest ÷ ${p.k} = image height`;
  // plan
  const s2=$("pn");s2.innerHTML="";const W=Math.max(p.w,p.hw*2,1)+1,ps=Math.min(380/W,250/Math.max(p.far,1)),cx=210,py=30,PX=x=>cx+x*ps,PY=d=>py+d*ps;
  const wedge=(a,c,o)=>{const r=Math.max(p.far,1)*ps*1.02,t=a*Math.PI/180;el("path",{d:`M${cx},${py} L${cx-r*Math.sin(t)},${py+r*Math.cos(t)} A${r},${r} 0 0 0 ${cx+r*Math.sin(t)},${py+r*Math.cos(t)} Z`,fill:c,opacity:o},s2)};
  wedge(45,sun,.12);wedge(30,ok,.14);
  el("line",{x1:PX(-p.w/2),y1:py,x2:PX(p.w/2),y2:py,stroke:blue,"stroke-width":6},s2);
  el("line",{x1:PX(-p.hw),y1:PY(p.near),x2:PX(p.hw),y2:PY(p.near),stroke:p.hang<=45?ink2:bad,"stroke-width":5},s2);
  el("line",{x1:PX(-p.hw),y1:PY(p.far),x2:PX(p.hw),y2:PY(p.far),stroke:red,"stroke-width":5},s2);
  el("text",{x:cx,y:py+18,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":M},s2,`screen ${fmt(p.w,2)} m wide`);
  el("text",{x:cx,y:Math.min(292,PY(p.far)+18),"text-anchor":"middle",fill:red,"font-size":12,"font-family":M},s2,"back row");
  el("text",{x:8,y:292,fill:ok,"font-size":11,"font-family":M},s2,"green 30°  ·  amber 45°");
  $("plL").textContent=`front row at ${fmt(p.hang,0)}°`;
  $("checks").innerHTML=p.checks.map(([t,o,v])=>`<li><span>${t}<br><small style="color:var(--ink-2);font-family:var(--mono)">${v}</small></span><span class="pill ${o?'ok':'bad'}">${o?'ok':'no'}</span></li>`).join("");
  const nb=p.checks.filter(c=>!c[1]).length;$("ckL").textContent=nb?nb+" to fix":"all pass";
  // table
  $("tb").innerHTML=SIZES.map(s=>{const h=s*IN*p.hf,w=s*IN*p.wf,reach=h*p.k,topE=p.sb+h,okk=reach>=p.far-1e-9&&topE<=p.ch-0.05&&p.near>=2*h-1e-9;
    return `<tr${Math.ceil(p.diag)<=s&&SIZES.filter(z=>z<s).every(z=>z<Math.ceil(p.diag))?' class="now"':''}><td>${s}"</td><td>${fmt(w,2)} × ${fmt(h,2)} m</td><td class="${reach>=p.far-1e-9?'ok':'bad'}">${fmt(reach,1)} m</td><td class="${p.near>=2*h-1e-9?'ok':'bad'}">${fmt(2*h,2)} m</td><td class="${topE<=p.ch-0.05?'ok':'bad'}">${fmt(topE,2)} m</td><td>${fmt(p.tr*w,2)} m</td><td><span class="pill ${okk?'ok':'bad'}">${okk?'works':'no'}</span></td></tr>`}).join("");
  $("dtL").textContent=`back row ${fmt(p.far,1)} m · ÷${p.k}`;
}
""")
