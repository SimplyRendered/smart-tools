APP = dict(
slug="sightline-rake", title="Sightline & Seating Rake", h1="Sightline & Seating Rake",
sub="Set the number of rows, the row depth and the C-value. Get the riser of every row so each seat sees over the heads in front, drawn as a live section with the sightlines.",
meta=[("Sheet","T-31"),("Method","C-value sightline"),("Units","mm"),("By","@smart_tools_every_week")],
source="C-value = vertical clearance of the sightline above the eye of the person in front; the common range is 60 mm (minimum) to 120 mm (ideal), see Time-Saver Standards, Neufert and Wikipedia 'Sightline (architecture)'. Rows are solved with similar triangles from the focus point. Check fire and aisle-step rules with your local code.",
inputs="""
      <div class="row">
        <label for="N">Rows<input id="N" type="number" step="1" value="14"></label>
        <label for="d">Row depth mm<input id="d" type="number" step="10" value="900"></label>
      </div>
      <div class="row">
        <label for="D1">Focus to row 1 mm<input id="D1" type="number" step="100" value="3000"></label>
        <label for="Hf">Focus above row 1 floor mm<input id="Hf" type="number" step="50" value="1000"></label>
      </div>
      <label for="eye">Seated eye height mm<input id="eye" type="number" step="10" value="1100"></label>
      <label for="cpre">C-value
        <select id="cpre"><option value="60">60 mm · minimum</option><option value="90" selected>90 mm · good</option><option value="120">120 mm · ideal</option><option value="c">Custom</option></select>
      </label>
      <label for="C">C-value mm<input id="C" type="number" step="5" value="90"></label>
      <label for="rnd">Round each riser up to
        <select id="rnd"><option value="0">No rounding</option><option value="5" selected>5 mm</option><option value="10">10 mm</option></select>
      </label>
      <p class="note">Focus point: the lowest point everyone must see (stage edge or bottom of the screen). Row depth is back to back. Eye height 1100 mm is typical for a seated adult; use 1000 to 1050 for a low-slung cinema seat.</p>
""",
right="""
      <div class="readout">
        <div><b>Total rise</b><span id="oR" class="hi">–</span></div>
        <div><b>Biggest riser</b><span id="oM">–</span></div>
        <div><b>Hall depth</b><span id="oD">–</span></div>
        <div><b>Real min C</b><span id="oC">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Section <span id="secLabel"></span></h2><svg id="sec" viewBox="0 0 840 340" role="img" aria-label="Auditorium section with sightlines"></svg></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="data"><h2>Row schedule <span>mm</span></h2><div class="tablewrap" style="max-height:340px;overflow-y:auto"><table><thead><tr><th>Row</th><th>From focus</th><th>Riser</th><th>Floor</th><th>C</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css=".view.full svg{max-height:430px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
$("cpre").addEventListener("change",()=>{const v=$("cpre").value;if(v!=="c")$("C").value=v;render()});
$("C").addEventListener("input",()=>{const p=$("cpre");const m=["60","90","120"].includes($("C").value);p.value=m?$("C").value:"c"});
function calc(){
  const N=Math.round(num("N",2,60,14)),d=num("d",500,1500,900),D1=num("D1",500,30000,3000),Hf=num("Hf",-2000,4000,1000),eye=num("eye",800,1400,1100),C=num("C",0,300,90),rnd=num("rnd",0,50,5);
  const rows=[];let prevE=0,prevF=0;
  for(let i=0;i<N;i++){
    const D=D1+i*d;let F,E;
    if(i===0){F=-Hf;E=F+eye;rows.push({n:1,D,F,E,riser:0,c:NaN});}
    else{
      const Dp=D-d,Ereq=D*(prevE+C)/Dp;let riser=Math.max(0,Ereq-eye-prevF);
      if(rnd>0)riser=Math.ceil(riser/rnd-1e-9)*rnd;
      F=prevF+riser;E=F+eye;
      const cc=E*Dp/D-prevE;
      rows.push({n:i+1,D,F,E,riser,c:cc});
    }
    prevE=E;prevF=F;
  }
  const rise=rows[N-1].F-rows[0].F,maxR=Math.max(0,...rows.map(r=>r.riser)),minC=rows.length>1?Math.min(...rows.slice(1).map(r=>r.c)):C;
  return {N,d,D1,Hf,eye,C,rnd,rows,rise,maxR,minC,depth:(N-1)*d,slope:Math.atan2(rise,(N-1)*d)*180/Math.PI,angle:Math.atan2(rows[N-1].E,rows[N-1].D)*180/Math.PI};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun");
  $("oR").textContent=Math.round(c.rise)+" mm";$("oM").textContent=Math.round(c.maxR)+" mm";$("oD").textContent=(c.depth/1000).toFixed(1)+" m";$("oC").textContent=Math.round(c.minC)+" mm";
  const C=[[`Every row clears the heads in front by ≥ ${Math.round(c.C)} mm (real minimum ${fmt(c.minC,0)} mm)`,c.minC>=c.C-0.01],
    [`C-value ${Math.round(c.C)} mm ${c.C>=120?"is ideal":c.C>=90?"is good":c.C>=60?"is the minimum (staggered seats help)":"is below the usual 60 mm minimum"}`,c.C>=60,"warn"],
    [`Biggest riser ${Math.round(c.maxR)} mm ${c.maxR>450?"is steep: stepped terraces and aisle stairs needed":"is gentle enough for a continuous tier"}`,c.maxR<=450,"warn"],
    [`Average slope ${fmt(c.slope,1)}° over ${(c.depth/1000).toFixed(1)} m of seating`,true,"info"],
    [`Last row looks ${fmt(c.angle,1)}° ${c.angle>=0?"up":"down"} to the focus point`,true,"info"]];
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // drawing
  const sv=$("sec");sv.innerHTML="";const R=c.rows,last=R[R.length-1];
  const x0=-1800,x1=last.D+c.d,vmin=Math.min(-c.Hf,0)-250,vmax=Math.max(last.E,0)+450;
  const sc=Math.min(790/(x1-x0),300/(vmax-vmin)),ox=24-x0*sc,oy=10+vmax*sc;
  const X=x=>ox+x*sc,Y=v=>oy-v*sc;
  el("line",{x1:X(x0),y1:Y(-c.Hf),x2:X(x1),y2:Y(-c.Hf),stroke:rule,"stroke-dasharray":"4 4"},sv);
  el("rect",{x:X(x0),y:Y(0),width:(0-x0)*sc,height:Math.max(0,(c.Hf)*sc),fill:rule,opacity:.5,stroke:ink2},sv);
  let pts=[`${X(x0)},${Y(-c.Hf)}`];
  R.forEach(r=>{const xa=r.D-c.d/2,xb=r.D+c.d/2;pts.push(`${X(xa)},${Y(r.F)}`,`${X(xb)},${Y(r.F)}`)});
  const lastF=last.F;
  el("polygon",{points:pts.join(" ")+` ${X(last.D+c.d/2)},${Y(vmin)} ${X(x0)},${Y(vmin)}`,fill:sheet,stroke:ink,"stroke-width":1.8},sv);
  // sightlines
  R.forEach((r,i)=>{if(i>0&&(i===R.length-1||R.length<=16||i%3===0))el("line",{x1:X(0),y1:Y(0),x2:X(r.D),y2:Y(r.E),stroke:i===R.length-1?red:blue,"stroke-width":i===R.length-1?2:.8,opacity:i===R.length-1?1:.45},sv)});
  R.forEach((r,i)=>{const hx=X(r.D),hy=Y(r.E),rad=Math.max(2.5,110*sc);
    el("line",{x1:hx,y1:hy,x2:hx,y2:Y(r.F),stroke:ink2,"stroke-width":Math.max(1,rad*.7),"stroke-linecap":"round",opacity:.35},sv);
    el("circle",{cx:hx,cy:hy,r:rad,fill:i===R.length-1?red:sun,stroke:ink,"stroke-width":.8},sv)});
  el("circle",{cx:X(0),cy:Y(0),r:5,fill:red},sv);
  el("text",{x:X(0)+8,y:Y(0)-8,fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"focus point");
  if(R.length>1){const p=R[R.length-2],yy=p.E*(1)+0;const hl=last.E*p.D/last.D; // sightline height at the row in front
    el("line",{x1:X(p.D),y1:Y(p.E),x2:X(p.D),y2:Y(hl),stroke:red,"stroke-width":2.5},sv);
    el("text",{x:X(p.D)-8,y:Y(hl)-6,fill:red,"font-size":12,"text-anchor":"end","font-family":"IBM Plex Mono, monospace"},sv,"C "+Math.round(c.minC>0?last.c:0)+" mm");}
  el("text",{x:X(x0)+4,y:Y(vmin)-4,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"stage / screen");
  $("secLabel").textContent=c.N+" rows · rise "+Math.round(c.rise)+" mm";
  const tb=$("tb");tb.innerHTML="";R.forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${r.n}</td><td>${Math.round(r.D)}</td><td>${r.n===1?"–":Math.round(r.riser)}</td><td>${Math.round(r.F-R[0].F)}</td><td>${r.n===1?"–":Math.round(r.c)}</td>`;tb.appendChild(tr)});
}
""")
