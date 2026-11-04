APP = dict(
slug="hip-roof", title="Hip Roof Geometry", h1="Hip Roof Geometry",
sub="Enter the wall plate size, pitch and overhang of an equal-pitch hip roof. Get the true hip rafter length, the backing angle, every jack rafter and the roof area, drawn on a live plan.",
meta=[("Sheet","T-55"),("Method","Solid geometry, 45° hips"),("Units","m, mm, degrees"),("By","@smart_tools_every_week")],
source="Equal-pitch hip roof on a rectangle, hips at 45° in plan (first-principles geometry, as in any carpentry roofing text): run R = half the eaves width, rise = R·tan θ, common rafter = R ÷ cos θ, hip plan = R·√2, hip true length = √(2R² + rise²), hip pitch = atan(rise ÷ R√2), backing angle: tan b = sin(hip pitch), jack rafter = its plan run ÷ cos θ, roof area = plan area ÷ cos θ. Lengths are to the centre lines; the cut length deducts half the hip thickness. Check sizes with a structural engineer.",
inputs="""
      <div class="row">
        <label for="L">Wall plate length m<input id="L" type="number" step="0.1" value="12"></label>
        <label for="W">Wall plate width m<input id="W" type="number" step="0.1" value="8"></label>
      </div>
      <div class="row">
        <label for="P">Roof pitch °<input id="P" type="number" step="0.5" value="30"></label>
        <label for="O">Overhang (plan) m<input id="O" type="number" step="0.05" value="0.6"></label>
      </div>
      <div class="row">
        <label for="S">Rafter spacing mm<input id="S" type="number" step="50" value="600"></label>
        <label for="T">Hip thickness mm<input id="T" type="number" step="5" value="50"></label>
      </div>
      <p class="note">Every face has the same pitch, so the hips run at 45° in plan and the ridge is the length minus the width. A square plan gives a pyramid roof with no ridge. Jack rafters run from the eaves up to a hip; the list is for one face next to one hip, and every hip has the same set on both sides.</p>
""",
right="""
      <div class="readout">
        <div><b>Hip rafter</b><span id="oH" class="hi">–</span></div>
        <div><b>Common rafter</b><span id="oC">–</span></div>
        <div><b>Backing angle</b><span id="oB">–</span></div>
        <div><b>Roof area</b><span id="oA">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Roof plan <span id="plL"></span></h2><svg id="pl" viewBox="0 0 600 380" role="img" aria-label="Roof plan with hips, ridge, common and jack rafters"></svg></div>
        <div class="view"><h2>Section across <span id="seL"></span></h2><svg id="se" viewBox="0 0 420 260" role="img" aria-label="Cross-section of the roof with pitch and rise"></svg></div>
        <div class="view"><h2>Hip, true length <span id="hpL"></span></h2><svg id="hp" viewBox="0 0 420 260" role="img" aria-label="Hip rafter development triangle"></svg></div>
      </div>
      <div class="data"><h2>Jack rafters, one face of one hip <span id="dtL"></span></h2><div class="tablewrap"><table><thead><tr><th>Jack</th><th>From corner</th><th>Centre-line length</th><th>Cut length</th><th>Per roof</th></tr></thead><tbody id="tb"></tbody></table></div></div>
      <div class="data"><h2>Cutting summary <span id="smL"></span></h2><div class="tablewrap"><table><thead><tr><th>Member</th><th>Number</th><th>Length each</th><th>Total</th></tr></thead><tbody id="tb2"></tbody></table></div></div>
""",
css=".view.full svg{max-height:400px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const D=Math.PI/180;
function calc(){
  let L=num("L",1,100,12),W=num("W",1,100,8);if(W>L){const t=L;L=W;W=t}
  const p={L,W,th:num("P",5,65,30),o:num("O",0,2,0.6),s:num("S",200,1500,600),t:num("T",10,200,50)};
  const c=Math.cos(p.th*D),tn=Math.tan(p.th*D);
  p.Lr=p.L+2*p.o;p.Wr=p.W+2*p.o;p.R=p.Wr/2;p.rise=p.R*tn;p.ridgeH=p.W/2*tn;p.ridge=p.L-p.W;
  p.com=p.R/c;p.hipPlan=p.R*Math.SQRT2;p.hip=Math.hypot(p.hipPlan,p.rise);p.hipP=Math.atan2(p.rise,p.hipPlan)/D;
  p.back=Math.atan(Math.sin(p.hipP*D))/D;p.guess=p.com*Math.SQRT2;
  p.area=p.Lr*p.Wr/c;p.plan=p.Lr*p.Wr;
  const sm=p.s/1000,ded=(p.t/1000/2)*Math.SQRT2/c;p.ded=ded;
  p.jacks=[];for(let k=1;k*sm<p.R-1e-9&&k<400;k++){const x=k*sm,len=x/c;p.jacks.push({k,x,len,cut:Math.max(0,len-ded)})}
  p.nJ=p.jacks.length*8;
  p.nCom=p.ridge>1e-9?2*(Math.floor(p.ridge/sm+1e-9)+1)+2:4;
  p.totJ=p.jacks.reduce((a,j)=>a+j.cut,0)*8;
  return p;
}
function render(){
  const p=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),ok=css("--ok");
  const M="IBM Plex Mono, monospace";
  $("oH").textContent=fmt(p.hip,3)+" m";$("oC").textContent=fmt(p.com,3)+" m";
  $("oB").textContent=fmt(p.back,1)+"°";$("oA").textContent=fmt(p.area,1)+" m²";
  // plan
  const sv=$("pl");sv.innerHTML="";const sc=Math.min(520/p.Lr,300/p.Wr),ox=(600-p.Lr*sc)/2,oy=40;
  const X=x=>ox+x*sc,Y=y=>oy+y*sc;
  el("rect",{x:X(0),y:Y(0),width:p.Lr*sc,height:p.Wr*sc,fill:sun,"fill-opacity":.18,stroke:ink,"stroke-width":2},sv);
  if(p.o>0)el("rect",{x:X(p.o),y:Y(p.o),width:p.L*sc,height:p.W*sc,fill:"none",stroke:ink2,"stroke-dasharray":"6 4"},sv);
  const R=p.R,r1=[R,R],r2=[p.Lr-R,R];
  // commons on long faces and hip-end centre
  const sm=p.s/1000;
  if(p.ridge>1e-9){for(let x=R;x<=p.Lr-R+1e-6;x+=sm){el("line",{x1:X(x),y1:Y(0),x2:X(x),y2:Y(R),stroke:blue,"stroke-width":1.2},sv);el("line",{x1:X(x),y1:Y(p.Wr),x2:X(x),y2:Y(R),stroke:blue,"stroke-width":1.2},sv)}}
  el("line",{x1:X(0),y1:Y(R),x2:X(R),y2:Y(R),stroke:blue,"stroke-width":1.2},sv);el("line",{x1:X(p.Lr),y1:Y(R),x2:X(p.Lr-R),y2:Y(R),stroke:blue,"stroke-width":1.2},sv);
  // jacks
  for(const j of p.jacks){const x=j.x;
    [[x,0,x,x],[x,p.Wr,x,p.Wr-x],[p.Lr-x,0,p.Lr-x,x],[p.Lr-x,p.Wr,p.Lr-x,p.Wr-x],[0,x,x,x],[0,p.Wr-x,x,p.Wr-x],[p.Lr,x,p.Lr-x,x],[p.Lr,p.Wr-x,p.Lr-x,p.Wr-x]]
    .forEach(([a,b,c2,d])=>el("line",{x1:X(a),y1:Y(b),x2:X(c2),y2:Y(d),stroke:ok,"stroke-width":1.2},sv))}
  // hips + ridge
  [[0,0,...r1],[0,p.Wr,...r1],[p.Lr,0,...r2],[p.Lr,p.Wr,...r2]].forEach(([a,b,c2,d])=>el("line",{x1:X(a),y1:Y(b),x2:X(c2),y2:Y(d),stroke:red,"stroke-width":3},sv));
  el("line",{x1:X(r1[0]),y1:Y(R),x2:X(r2[0]),y2:Y(R),stroke:red,"stroke-width":3},sv);
  el("text",{x:X(R/2)+6,y:Y(R/2)-6,fill:red,"font-size":14,"font-family":M},sv,`hip ${fmt(p.hip,2)} m`);
  if(p.ridge>0.5)el("text",{x:X(p.Lr/2),y:Y(R)-8,"text-anchor":"middle",fill:red,"font-size":14,"font-family":M},sv,`ridge ${fmt(p.ridge,2)} m`);
  el("text",{x:X(p.Lr/2),y:Y(0)-12,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":M},sv,`eaves ${fmt(p.Lr,2)} m (wall ${fmt(p.L,2)} m)`);
  el("text",{x:X(p.Lr)+0,y:Y(p.Wr)+22,"text-anchor":"end",fill:ink2,"font-size":13,"font-family":M},sv,`eaves width ${fmt(p.Wr,2)} m`);
  el("text",{x:X(0),y:Y(p.Wr)+22,fill:ok,"font-size":13,"font-family":M},sv,`${p.nJ} jacks @ ${Math.round(p.s)}`);
  $("plL").textContent=p.ridge>1e-9?`${fmt(p.L,1)} × ${fmt(p.W,1)} m walls · ${fmt(p.th,1)}°`:"square plan: pyramid roof";
  // section
  const s2=$("se");s2.innerHTML="";const k=Math.min(360/p.Wr,170/Math.max(p.rise,0.1)),bx=(420-p.Wr*k)/2,by=220;
  el("polygon",{points:`${bx},${by} ${bx+p.Wr*k/2},${by-p.rise*k} ${bx+p.Wr*k},${by}`,fill:sun,"fill-opacity":.22,stroke:ink,"stroke-width":2},s2);
  el("rect",{x:bx+p.o*k-4,y:by,width:8,height:30,fill:ink2},s2);el("rect",{x:bx+(p.Wr-p.o)*k-4,y:by,width:8,height:30,fill:ink2},s2);
  el("line",{x1:bx+p.Wr*k/2,y1:by,x2:bx+p.Wr*k/2,y2:by-p.rise*k,stroke:red,"stroke-dasharray":"5 4"},s2);
  el("text",{x:bx+p.Wr*k/2+6,y:by-p.rise*k/2,fill:red,"font-size":13,"font-family":M},s2,`rise ${fmt(p.rise,2)}`);
  el("text",{x:bx+p.Wr*k/4-6,y:by-p.rise*k/2-8,"text-anchor":"end",fill:ink,"font-size":13,"font-family":M},s2,`${fmt(p.com,2)} m`);
  el("path",{d:`M${bx+40},${by} A40 40 0 0 0 ${bx+40*Math.cos(p.th*D)},${by-40*Math.sin(p.th*D)}`,fill:"none",stroke:ink2},s2);
  el("text",{x:bx+46,y:by-8,fill:ink2,"font-size":13,"font-family":M},s2,`${fmt(p.th,1)}°`);
  el("text",{x:210,y:252,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":M},s2,`ridge ${fmt(p.ridgeH,2)} m above wall plate`);
  $("seL").textContent=`run ${fmt(p.R,2)} m`;
  // hip development
  const s3=$("hp");s3.innerHTML="";const k3=Math.min(330/p.hipPlan,170/Math.max(p.rise,0.1)),hx=40,hy=210;
  el("polygon",{points:`${hx},${hy} ${hx+p.hipPlan*k3},${hy} ${hx+p.hipPlan*k3},${hy-p.rise*k3}`,fill:red,"fill-opacity":.12,stroke:ink2},s3);
  el("line",{x1:hx,y1:hy,x2:hx+p.hipPlan*k3,y2:hy-p.rise*k3,stroke:red,"stroke-width":3},s3);
  el("line",{x1:hx,y1:hy,x2:hx+p.com*Math.SQRT2*Math.cos(p.hipP*D)*k3,y2:hy-p.com*Math.SQRT2*Math.sin(p.hipP*D)*k3,stroke:ink2,"stroke-dasharray":"4 5"},s3);
  el("text",{x:hx+p.hipPlan*k3/2,y:hy+20,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":M},s3,`plan R√2 = ${fmt(p.hipPlan,2)} m`);
  el("text",{x:hx+p.hipPlan*k3/2-10,y:hy-p.rise*k3/2-12,"text-anchor":"end",fill:red,"font-size":13,"font-family":M},s3,`true ${fmt(p.hip,3)} m`);
  el("text",{x:hx,y:24,fill:ink2,"font-size":12,"font-family":M},s3,`- - common × √2 = ${fmt(p.guess,3)} m (too long)`);
  el("text",{x:hx,y:244,fill:ink2,"font-size":12,"font-family":M},s3,`hip pitch ${fmt(p.hipP,1)}° · backing ${fmt(p.back,1)}°`);
  $("hpL").textContent=`+${fmt((p.guess-p.hip)*1000,0)} mm if guessed`;
  // tables
  $("tb").innerHTML=p.jacks.length?p.jacks.map(j=>`<tr><td>J${j.k}</td><td>${Math.round(j.x*1000)} mm</td><td>${Math.round(j.len*1000)} mm</td><td>${Math.round(j.cut*1000)} mm</td><td>8</td></tr>`).join(""):`<tr><td colspan="5">No jacks: the spacing is wider than the run.</td></tr>`;
  $("dtL").textContent=`common difference ${Math.round(p.s/Math.cos(p.th*D))} mm · cut = centre line − ${Math.round(p.ded*1000)} mm`;
  const nc=p.nCom,rows=[["Hip rafters",4,p.hip],["Common rafters",nc,p.com],["Ridge",p.ridge>1e-9?1:0,p.ridge],["Jack rafters",p.nJ,p.nJ?p.totJ/p.nJ:0]];
  $("tb2").innerHTML=rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[1]?fmt(r[2],3)+" m":"–"}</td><td>${fmt(r[1]*r[2],2)} m</td></tr>`).join("");
  const tot=rows.reduce((a,r)=>a+r[1]*r[2],0);
  $("smL").textContent=`about ${fmt(tot,0)} m of rafter, centre lines`;
}
""")
