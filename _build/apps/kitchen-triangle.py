APP = dict(
slug="kitchen-triangle", title="Kitchen Work Triangle", h1="Kitchen Work Triangle",
sub="Drag the sink, hob and fridge on the plan. Each leg and the total are checked against the classic work-triangle rules.",
meta=[("Sheet","T-06"),("Rule","4–9 ft legs · 12–26 ft total"),("Units","m · ft"),("By","@smart_tools_every_week")],
source="Guideline: each leg 4–9 ft (1.22–2.74 m), total 12–26 ft (3.66–7.92 m), measured centre-front to centre-front.",
css="""
#plan{touch-action:none;user-select:none}
#plan .pt{cursor:grab}
#plan .pt:active{cursor:grabbing}
""",
inputs="""
      <label for="layout">Kitchen layout
        <select id="layout">
          <option value="L">L-shaped</option><option value="U">U-shaped</option><option value="G">Parallel / galley</option><option value="I">Single wall</option>
        </select>
      </label>
      <div class="row">
        <label for="rl">Room length (m)<input id="rl" type="number" step="0.1" min="1.8" value="3.6"></label>
        <label for="rw">Room width (m)<input id="rw" type="number" step="0.1" min="1.8" value="3.0"></label>
      </div>
      <label for="cd">Counter depth (mm)<input id="cd" type="number" step="25" value="600"></label>
      <div class="chips" role="group" aria-label="Actions"><button type="button" id="reset">Reset points</button></div>
      <p class="note">Drag the three points on the plan to where the centre front of the sink, hob and fridge will be. The triangle should be compact but not cramped, and no leg should cross a tall cabinet or the main walkway.</p>
      <p class="note">In a single-wall kitchen the three points sit in a line, so the triangle can't apply. The tool then checks the run length instead.</p>
""",
right="""
      <div class="readout">
        <div><b>Sink ↔ hob</b><span id="l1">–</span></div>
        <div><b>Hob ↔ fridge</b><span id="l2">–</span></div>
        <div><b>Fridge ↔ sink</b><span id="l3">–</span></div>
        <div><b>Total</b><span id="lt" class="hi">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Plan <span id="planLabel">drag the points</span></h2><svg id="plan" viewBox="0 0 640 460" role="img" aria-label="Kitchen plan with work triangle"></svg></div>
      </div>
      <div class="data">
        <h2>Checks <span id="sum"></span></h2>
        <ul class="checks" id="checks"></ul>
      </div>
""",
js=r"""
const NAMES=["Sink","Hob","Fridge"];
let P=null;
function defaults(){const L=+$("rl").value,W=+$("rw").value,d=+$("cd").value/1000,lay=$("layout").value;const f=d*0.9;
  if(lay==="L")return[[L*0.55,f],[L-f,W*0.5],[0.6,f]];
  if(lay==="U")return[[L*0.5,f],[L-f,W*0.6],[f,W*0.6]];
  if(lay==="G")return[[L*0.35,f],[L*0.6,W-f],[L-0.45,f]];
  return[[L*0.45,f],[L*0.75,f],[0.45,f]];}
function counters(){const L=+$("rl").value,W=+$("rw").value,d=+$("cd").value/1000,lay=$("layout").value;
  const r=[[0,0,L,d]];if(lay==="L")r.push([L-d,0,d,W]);if(lay==="U"){r.push([L-d,0,d,W]);r.push([0,0,d,W])}if(lay==="G")r.push([0,W-d,L,d]);return r}
$("layout").addEventListener("input",()=>{P=defaults()});["rl","rw","cd"].forEach(i=>$(i).addEventListener("input",()=>{P=defaults()}));
$("reset").addEventListener("click",()=>{P=defaults();render()});
let drag=-1,geo=null;
const sv=$("plan");
function toRoom(e){const r=sv.getBoundingClientRect();const x=(e.clientX-r.left)/r.width*640,y=(e.clientY-r.top)/r.height*460;return[(x-geo.ox)/geo.k,(y-geo.oy)/geo.k]}
sv.addEventListener("pointerdown",e=>{const t=e.target.closest(".pt");if(!t)return;drag=+t.dataset.i;sv.setPointerCapture(e.pointerId);e.preventDefault()});
sv.addEventListener("pointermove",e=>{if(drag<0)return;const L=+$("rl").value,W=+$("rw").value;let [x,y]=toRoom(e);x=Math.round(Math.min(L,Math.max(0,x))*20)/20;y=Math.round(Math.min(W,Math.max(0,y))*20)/20;P[drag]=[x,y];render()});
["pointerup","pointercancel"].forEach(ev=>sv.addEventListener(ev,()=>drag=-1));
const ft=m=>m/0.3048;
function render(){
  if(!P)P=defaults();const L=+$("rl").value,W=+$("rw").value;const ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),ok=css("--ok"),bad=css("--bad"),blue=css("--blue");
  const k=Math.min(560/L,380/W),ox=(640-L*k)/2,oy=40;geo={k,ox,oy};const X=v=>ox+v*k,Y=v=>oy+v*k;
  sv.innerHTML="";
  el("rect",{x:X(0)-8,y:Y(0)-8,width:L*k+16,height:W*k+16,fill:rule},sv);el("rect",{x:X(0),y:Y(0),width:L*k,height:W*k,fill:css("--sheet")},sv);
  counters().forEach(c=>el("rect",{x:X(c[0]),y:Y(c[1]),width:c[2]*k,height:c[3]*k,fill:css("--paper"),stroke:ink,"stroke-width":1.2},sv));
  for(let g=0.5;g<Math.max(L,W);g+=0.5){if(g<L)el("line",{x1:X(g),y1:Y(0),x2:X(g),y2:Y(W),stroke:rule,"stroke-width":.5,"stroke-dasharray":"2 4"},sv)}
  const legs=[[0,1],[1,2],[2,0]].map(([a,b])=>Math.hypot(P[a][0]-P[b][0],P[a][1]-P[b][1]));const tot=legs[0]+legs[1]+legs[2];
  const legOk=v=>v>=1.2192&&v<=2.7432;const totOk=tot>=3.6576&&tot<=7.9248;
  el("polygon",{points:P.map(p=>X(p[0])+","+Y(p[1])).join(" "),fill:totOk&&legs.every(legOk)?css("--okbg"):css("--badbg"),stroke:"none"},sv);
  [[0,1],[1,2],[2,0]].forEach(([a,b],i)=>{const c=legOk(legs[i])?ok:bad;el("line",{x1:X(P[a][0]),y1:Y(P[a][1]),x2:X(P[b][0]),y2:Y(P[b][1]),stroke:c,"stroke-width":3},sv);
    const mx=(X(P[a][0])+X(P[b][0]))/2,my=(Y(P[a][1])+Y(P[b][1]))/2;el("rect",{x:mx-34,y:my-11,width:68,height:20,fill:css("--sheet"),stroke:c},sv);
    el("text",{x:mx,y:my+4,"text-anchor":"middle",fill:c,"font-size":12,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},sv,legs[i].toFixed(2)+" m")});
  P.forEach((p,i)=>{const g=el("g",{class:"pt","data-i":i},sv);el("circle",{cx:X(p[0]),cy:Y(p[1]),r:16,fill:[blue,red,ink][i]},g);
    el("text",{x:X(p[0]),y:Y(p[1])+4,"text-anchor":"middle",fill:css("--sheet"),"font-size":11,"font-weight":700,"font-family":"IBM Plex Sans, sans-serif","pointer-events":"none"},g,NAMES[i][0]);
    el("text",{x:X(p[0]),y:Y(p[1])-22,"text-anchor":"middle",fill:ink,"font-size":12,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif","pointer-events":"none"},g,NAMES[i])});
  el("text",{x:X(0),y:Y(W)+28,fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,`${L.toFixed(2)} × ${W.toFixed(2)} m · grid 0.5 m`);
  ["l1","l2","l3"].forEach((id,i)=>{$(id).textContent=legs[i].toFixed(2)+" m";$(id).className=legOk(legs[i])?"ok":"bad"});
  $("lt").textContent=tot.toFixed(2)+" m";$("lt").className=totOk?"ok":"bad";
  const lay=$("layout").value;const C=[];
  if(lay==="I"){const run=Math.max(...P.map(p=>p[0]))-Math.min(...P.map(p=>p[0]));C.push([`Single wall: sink-to-hob ${legs[0].toFixed(2)} m and work run ${run.toFixed(2)} m. Keep the run under about 3.6 m (12 ft).`,run<=3.66]);}
  else{NAMES.forEach((n,i)=>{const pair=[["Sink","Hob"],["Hob","Fridge"],["Fridge","Sink"]][i];C.push([`${pair[0]} ↔ ${pair[1]}: ${legs[i].toFixed(2)} m (${ft(legs[i]).toFixed(1)} ft), needs 4–9 ft`,legOk(legs[i])])});
    C.push([`Total ${tot.toFixed(2)} m (${ft(tot).toFixed(1)} ft), needs 12–26 ft`,totOk]);}
  C.push(["Keep tall units (fridge tower, oven stack) out of the triangle legs","note"]);
  C.push(["Main walkway should not cut through the triangle","note"]);
  const ul=$("checks");ul.innerHTML="";let f=0;C.forEach(([t,s])=>{const li=document.createElement("li");const cls=s==="note"?"warn":s?"ok":"bad";if(s===false)f++;li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${s==="note"?"check":s?"pass":"fix"}</span>`;ul.appendChild(li)});
  $("sum").textContent=f?f+" to fix":"triangle works";
}
""")
