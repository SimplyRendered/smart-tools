APP = dict(
slug="bifold-door", title="Bi-fold Door Planner", h1="Bi-fold Door Planner",
sub="Enter the opening, the frame and the number of panels. Get each panel width, the folded stack, the real clear opening and where a lead door works, with a plan you can fold open.",
meta=[("Sheet","T-56"),("Method","Plan geometry"),("Units","mm"),("By","@smart_tools_every_week")],
source="First-principles plan geometry. Panel width = (opening − 2 × frame − tolerance − hinge gaps) ÷ panels. Fully folded, each stack takes its panel count × panel thickness plus the hinge gaps along the opening, and sticks out by about one panel width. While folding at angle a, each panel takes w·cos a + t·sin a along the track. The defaults (frame 60 mm, panel 70 mm thick, 10 mm tolerance, 3 mm gap, 500 to 1,100 mm panels) are typical aluminium values, not a standard: use your system maker's data sheet. A lead (traffic) door that opens on its own needs an odd number of panels on that side.",
inputs="""
      <div class="row">
        <label for="W">Structural opening width<input id="W" type="number" step="10" value="3000"></label>
        <label for="H">Opening height<input id="H" type="number" step="10" value="2400"></label>
      </div>
      <div class="row">
        <label for="N">Number of panels<input id="N" type="number" step="1" value="3"></label>
        <label for="NL">Panels folding left<input id="NL" type="number" step="1" value="3"></label>
      </div>
      <div class="row">
        <label for="F">Outer frame, each side<input id="F" type="number" step="5" value="60"></label>
        <label for="T">Panel thickness<input id="T" type="number" step="2" value="70"></label>
      </div>
      <div class="row">
        <label for="G">Fitting tolerance<input id="G" type="number" step="2" value="10"></label>
        <label for="HG">Gap per hinge<input id="HG" type="number" step="1" value="3"></label>
      </div>
      <div class="row">
        <label for="PMIN">Panel min mm<input id="PMIN" type="number" step="10" value="500"></label>
        <label for="PMAX">Panel max mm<input id="PMAX" type="number" step="10" value="1100"></label>
      </div>
      <label for="OP">Open it: fold %<input id="OP" type="range" min="0" max="100" step="1" value="100"></label>
      <p class="note">All sizes in mm. Panels folding right = panels − panels left. Frame, thickness, gaps and the panel size range differ between systems; the defaults are typical aluminium values, so check them against your maker's data sheet. The clear opening is measured between the folded stacks.</p>
""",
right="""
      <div class="readout">
        <div><b>Clear opening</b><span id="oC" class="hi">–</span></div>
        <div><b>Panel width</b><span id="oP">–</span></div>
        <div><b>Stack L / R</b><span id="oS">–</span></div>
        <div><b>Sticks out</b><span id="oX">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Plan <span id="plL"></span></h2><svg id="pl" viewBox="0 0 600 300" role="img" aria-label="Plan of the bi-fold panels folding open"></svg></div>
        <div class="view full"><h2>Elevation from inside <span id="elL"></span></h2><svg id="ev" viewBox="0 0 600 300" role="img" aria-label="Elevation of the panels with the lead door marked"></svg></div>
      </div>
      <div class="data"><h2>Every panel count for this opening <span id="dtL"></span></h2><div class="tablewrap"><table><thead><tr><th>Panels</th><th>Panel width</th><th>Clear, all one side</th><th>Clear %</th><th>Lead door</th><th></th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const D=Math.PI/180;
function geo(W,F,T,G,HG,n,nl){
  const inner=W-2*F,nr=n-nl,hinges=Math.max(0,nl-1)+Math.max(0,nr-1);
  const pw=(inner-G-hinges*HG-(nl>0&&nr>0?HG:0))/n;
  const st=k=>k>0?k*T+(k-1)*HG:0;
  const sL=st(nl),sR=st(nr);
  return {inner,nr,pw,sL,sR,clear:inner-sL-sR};
}
function calc(){
  const p={W:num("W",400,20000,3000),H:num("H",500,6000,2400),F:num("F",0,300,60),T:num("T",10,200,70),G:num("G",0,100,10),HG:num("HG",0,30,3),
    pmin:num("PMIN",100,3000,500),pmax:num("PMAX",100,3000,1100),op:num("OP",0,100,100)};
  p.n=Math.round(num("N",1,12,3));p.nl=Math.round(Math.min(p.n,num("NL",0,12,p.n)));
  Object.assign(p,geo(p.W,p.F,p.T,p.G,p.HG,p.n,p.nl));
  p.pwOK=p.pw>=p.pmin&&p.pw<=p.pmax;
  p.a=p.op/100*90*D; // fold angle
  const along=k=>k>0?k*(Math.max(0,p.pw)*Math.cos(p.a)+p.T*Math.sin(p.a))+(k-1)*p.HG:0;
  p.uL=along(p.nl);p.uR=along(p.nr);p.clearNow=Math.max(0,p.inner-p.uL-p.uR);
  p.leadL=p.nl%2===1;p.leadR=p.nr%2===1;
  p.rows=[];for(let k=2;k<=8;k++){const g=geo(p.W,p.F,p.T,p.G,p.HG,k,k);p.rows.push({k,pw:g.pw,clear:g.clear,pct:g.clear/p.W*100,ok:g.pw>=p.pmin&&g.pw<=p.pmax})}
  return p;
}
function render(){
  const p=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),ok=css("--ok"),bad=css("--bad");
  const M="IBM Plex Mono, monospace",GL="#6FB0F0";
  $("oC").textContent=Math.round(p.clearNow)+" mm";
  $("oP").textContent=Math.round(p.pw)+" mm";$("oP").className=p.pwOK?"ok":"bad";
  $("oS").textContent=Math.round(p.sL)+" / "+Math.round(p.sR);
  $("oX").textContent=Math.round(Math.max(0,p.pw))+" mm";
  // plan
  const sv=$("pl");sv.innerHTML="";const sc=520/p.W,ox=40,wy=90;const X=x=>ox+x*sc;
  el("rect",{x:X(-0)-24,y:wy-14,width:24,height:28,fill:ink2},sv);el("rect",{x:X(p.W),y:wy-14,width:24,height:28,fill:ink2},sv);
  el("rect",{x:X(0),y:wy-6,width:p.F*sc,height:12,fill:ink},sv);el("rect",{x:X(p.W-p.F),y:wy-6,width:p.F*sc,height:12,fill:ink},sv);
  el("line",{x1:X(p.F),y1:wy,x2:X(p.W-p.F),y2:wy,stroke:ink2,"stroke-dasharray":"4 4"},sv);
  const pw=Math.max(0,p.pw),dx=pw*Math.cos(p.a),dy=pw*Math.sin(p.a),tk=Math.max(2,p.T*sc);
  const drawSide=(k,start,dir,lead)=>{let x=start;for(let i=0;i<k;i++){const out=i%2===0;const x0=x,y0=wy+(out?0:dy*sc),x1=x+dir*dx,y1=wy+(out?dy*sc:0);
      el("line",{x1:X(x0),y1:y0,x2:X(x1),y2:y1,stroke:i===k-1&&lead?red:GL,"stroke-width":tk,"stroke-linecap":"butt",opacity:.9},sv);
      el("circle",{cx:X(x0),cy:y0,r:3,fill:ink},sv);
      x=x1+dir*(p.T*Math.sin(p.a)+p.HG)}};
  drawSide(p.nl,p.F,1,p.leadL);drawSide(p.nr,p.W-p.F,-1,p.leadR);
  // clear dimension
  const cx0=p.F+p.uL,cx1=p.W-p.F-p.uR;
  if(p.clearNow>0){el("line",{x1:X(cx0),y1:wy-36,x2:X(cx1),y2:wy-36,stroke:ok,"stroke-width":2},sv);
    for(const x of [cx0,cx1])el("line",{x1:X(x),y1:wy-44,x2:X(x),y2:wy-28,stroke:ok,"stroke-width":2},sv);
    el("text",{x:X((cx0+cx1)/2),y:wy-46,"text-anchor":"middle",fill:ok,"font-size":14,"font-family":M},sv,`clear ${Math.round(p.clearNow)} mm`)}
  el("text",{x:X(p.W/2),y:286,"text-anchor":"middle",fill:ink2,"font-size":13,"font-family":M},sv,`opening ${Math.round(p.W)} mm · panels swing out ${Math.round(dy)} mm`);
  el("text",{x:24,y:24,fill:ink2,"font-size":13,"font-family":M},sv,"OUTSIDE ↑");
  $("plL").textContent=`${p.op}% folded`;
  // elevation
  const s2=$("ev");s2.innerHTML="";const k=Math.min(520/p.W,230/p.H),ex=(600-p.W*k)/2,ey=20;
  el("rect",{x:ex,y:ey,width:p.W*k,height:p.H*k,fill:"none",stroke:ink,"stroke-width":3},s2);
  el("rect",{x:ex+p.F*k,y:ey+p.F*k,width:(p.W-2*p.F)*k,height:(p.H-2*p.F)*k,fill:"none",stroke:ink2},s2);
  let x=p.F+p.G/2;
  for(let i=0;i<p.n;i++){const left=i<p.nl,idx=left?i:p.n-1-i,side=left?p.nl:p.nr;
    const lead=(left?p.leadL:p.leadR)&&((left&&i===p.nl-1)||(!left&&i===p.nl));
    el("rect",{x:ex+x*k,y:ey+(p.F+5)*k,width:Math.max(0,pw*k),height:(p.H-2*p.F-10)*k,fill:GL,"fill-opacity":lead?.35:.18,stroke:lead?red:GL,"stroke-width":lead?2.5:1.5},s2);
    if(pw*k>30)el("text",{x:ex+(x+pw/2)*k,y:ey+p.H*k/2,"text-anchor":"middle",fill:lead?red:ink,"font-size":13,"font-family":M},s2,lead?"lead":`${i+1}`);
    x+=pw+p.HG}
  el("text",{x:300,y:290,"text-anchor":"middle",fill:ink2,"font-size":13,"font-family":M},s2,`${p.n} × ${Math.round(p.pw)} mm · ${p.nl} left, ${p.nr} right`);
  const ld=[p.leadL&&p.nl?"left":"",p.leadR&&p.nr?"right":""].filter(Boolean);
  $("elL").textContent=ld.length?`lead door: ${ld.join(" + ")}`:"no lead door (even count)";
  $("tb").innerHTML=p.rows.map(r=>`<tr${r.k===p.n&&p.nl===p.n?' class="now"':''}><td>${r.k}</td><td class="${r.ok?'ok':'bad'}">${Math.round(r.pw)} mm</td><td>${Math.round(r.clear)} mm</td><td>${fmt(r.pct,1)}%</td><td>${r.k%2?'yes':'no'}</td><td><span class="pill ${r.ok?'ok':'bad'}">${r.ok?'fits':(r.pw>p.pmax?'too wide':'too narrow')}</span></td></tr>`).join("");
  $("dtL").textContent=`${Math.round(p.W)} mm opening · panels ${Math.round(p.pmin)} to ${Math.round(p.pmax)} mm`;
}
""")
