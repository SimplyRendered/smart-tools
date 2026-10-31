APP = dict(
slug="gutter-sizer", title="Gutter & Downpipe Sizer", h1="Gutter & Downpipe Sizer",
sub="Enter the roof, the rainfall intensity, the gutter and the downpipe. Get the peak flow, whether the gutter and the outlet can carry it, and how many downpipes the roof needs, on a live plan and gutter section.",
meta=[("Sheet","T-35"),("Method","Rational + Manning"),("Units","m, mm, L/s"),("By","@smart_tools_every_week")],
source="Peak flow Q = C · i · A ÷ 3600 (rational method, Q in L/s, i in mm/h, A plan area in m²). Gutter capacity by Manning, V = (1/n) R^(2/3) S^(1/2), with n: PVC 0.010, galvanized iron 0.016, concrete 0.013, copper 0.011 (typical textbook values). Downpipe inlet = the lesser of a broad-crested weir (Q = 1.45 · πD · h^1.5) and an orifice (Q = 0.6 · A · √(2gh)), h = flow depth in the gutter. Rainfall intensity is your design value: take it from your local rainfall data or drainage code. Preliminary sizing, confirm with the manufacturer.",
inputs="""
      <div class="row">
        <label for="L">Gutter length m<input id="L" type="number" step="0.5" value="12"></label>
        <label for="W">Roof run to ridge m<input id="W" type="number" step="0.5" value="5"></label>
      </div>
      <div class="row">
        <label for="i">Rainfall mm/h<input id="i" type="number" step="10" value="150"></label>
        <label for="C">Runoff coefficient<input id="C" type="number" step="0.05" value="0.95"></label>
      </div>
      <div class="row">
        <label for="gt">Gutter shape
          <select id="gt"><option value="h" selected>Half-round</option><option value="b">Box (rectangular)</option></select>
        </label>
        <label for="mat">Gutter material
          <select id="mat"><option value="0.010" selected>PVC 0.010</option><option value="0.011">Copper 0.011</option><option value="0.013">Concrete 0.013</option><option value="0.016">Galvanized 0.016</option></select>
        </label>
      </div>
      <div class="row">
        <label for="gw">Gutter width / dia mm<input id="gw" type="number" step="5" value="125"></label>
        <label for="gd">Box depth mm<input id="gd" type="number" step="5" value="100"></label>
      </div>
      <div class="row">
        <label for="gs">Gutter fall 1 in<input id="gs" type="number" step="50" value="200"></label>
        <label for="fl">Max fill %<input id="fl" type="number" step="5" value="80"></label>
      </div>
      <div class="row">
        <label for="pd">Downpipe dia
          <select id="pd"><option value="50">50 mm</option><option value="63">63 mm</option><option value="75" selected>75 mm</option><option value="90">90 mm</option><option value="100">100 mm</option><option value="110">110 mm</option><option value="150">150 mm</option></select>
        </label>
        <label for="no">Outlets on this gutter<input id="no" type="number" step="1" value="1"></label>
      </div>
      <p class="note">Plan area = gutter length × roof run, since rain falls straight down. One gutter run catches one roof slope. A gable roof has two gutters, so check each. Outlets share the flow equally.</p>
""",
right="""
      <div class="readout">
        <div><b>Peak flow</b><span id="oQ" class="hi">–</span></div>
        <div><b>Gutter carries</b><span id="oG">–</span></div>
        <div><b>Downpipe takes</b><span id="oP">–</span></div>
        <div><b>Downpipes needed</b><span id="oN">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Roof plan <span id="rLabel"></span></h2><svg id="rp" viewBox="0 0 400 320" role="img" aria-label="Roof plan with gutter and downpipes" style="max-height:340px"></svg></div>
        <div class="view"><h2>Gutter section <span id="sLabel"></span></h2><svg id="gs2" viewBox="0 0 300 260" role="img" aria-label="Gutter cross section" style="max-height:300px"></svg></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="data"><h2>Downpipe sizes <span>for this roof and gutter</span></h2><div class="tablewrap"><table><thead><tr><th>Downpipe</th><th>Takes L/s</th><th>Roof per pipe m²</th><th>Pipes for this roof</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const G=9.81;
function gutterGeom(c){ // returns A (m2), P, flow depth y (m), top width
  const fl=c.fl/100;
  if(c.gt==="h"){const R=c.gw/2000,y=Math.max(1e-4,fl*R),th=2*Math.acos(Math.max(-1,Math.min(1,(R-y)/R)));
    return {A:R*R/2*(th-Math.sin(th)),P:R*th,y,depth:R,R};}
  const w=c.gw/1000,y=Math.max(1e-4,fl*c.gd/1000);return {A:w*y,P:w+2*y,y,depth:c.gd/1000,w};
}
function pipeQ(D,y){ // m3/s, inlet control, outlet in gutter bottom
  const A=Math.PI*D*D/4,weir=1.45*Math.PI*D*Math.pow(y,1.5),ori=0.6*A*Math.sqrt(2*G*y);return Math.min(weir,ori);
}
function calc(){
  const c={L:num("L",1,60,12),W:num("W",1,30,5),i:num("i",20,400,150),C:num("C",0.3,1,0.95),gt:$("gt").value==="b"?"b":"h",n:num("mat",0.008,0.02,0.01),
    gw:num("gw",50,400,125),gd:num("gd",40,400,100),gs:num("gs",50,1000,200),fl:num("fl",30,100,80),pd:num("pd",40,200,75),no:Math.round(num("no",1,6,1))};
  c.area=c.L*c.W;c.Q=c.C*c.i*c.area/3600;c.Qo=c.Q/c.no;
  const g=gutterGeom(c);c.g=g;const S=1/c.gs;
  c.Qg=(g.A>0&&g.P>0)?(1/c.n)*g.A*Math.pow(g.A/g.P,2/3)*Math.sqrt(S):0;c.Vg=g.A>0?c.Qg/g.A:0;c.Qg*=1000;
  c.Qp=pipeQ(c.pd/1000,g.y)*1000;
  c.need=Math.max(1,Math.ceil(c.Q/c.Qp-1e-9));
  c.areaPer=c.Qp*3600/(c.C*c.i);
  return c;
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet");
  $("oQ").textContent=fmt(c.Q,2)+" L/s";$("oG").textContent=fmt(c.Qg,2)+" L/s";$("oP").textContent=fmt(c.Qp,2)+" L/s";$("oN").textContent=c.need+" × "+c.pd+" mm";
  $("oG").className=c.Qg<c.Qo?"bad":"";$("oP").className=c.Qp<c.Qo?"bad":"";
  const C=[[`Gutter carries ${fmt(c.Qg,2)} L/s, each outlet end needs ${fmt(c.Qo,2)} L/s`,c.Qg>=c.Qo],
   [`One ${c.pd} mm downpipe takes ${fmt(c.Qp,2)} L/s, each outlet needs ${fmt(c.Qo,2)} L/s`,c.Qp>=c.Qo],
   [`Outlets: you have ${c.no}, the roof needs at least ${c.need} of this size`,c.no>=c.need],
   [`Roof per downpipe is ${fmt(c.area/c.no,1)} m² (this size copes with ${fmt(c.areaPer,1)} m² at ${fmt(c.i,0)} mm/h)`,c.area/c.no<=c.areaPer],
   [`Flow speed in the gutter is ${fmt(c.Vg,2)} m/s at ${fmt(c.fl,0)}% full`,true,"info"]];
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // plan
  const rp=$("rp");rp.innerHTML="";const mx=340/c.L,my=170/Math.max(c.W,1),s=Math.min(mx,my),w=c.L*s,h=c.W*s,ox=(400-w)/2,oy=24;
  el("rect",{x:ox,y:oy,width:w,height:h,fill:sheet,stroke:ink,"stroke-width":2},rp);
  for(let k=1;k<6;k++){el("line",{x1:ox+w*k/6,y1:oy+8,x2:ox+w*k/6,y2:oy+h-14,stroke:blue,"stroke-width":1.2,opacity:.6},rp);el("path",{d:`M ${ox+w*k/6-4} ${oy+h-20} L ${ox+w*k/6} ${oy+h-12} L ${ox+w*k/6+4} ${oy+h-20}`,fill:"none",stroke:blue,"stroke-width":1.2,opacity:.8},rp);}
  el("rect",{x:ox,y:oy+h,width:w,height:12,fill:blue,opacity:.3,stroke:blue},rp);
  const pos=[];for(let k=0;k<c.no;k++)pos.push(c.no===1?0:k/(c.no-1));
  pos.forEach(f=>{const x=c.no===1?ox+8:ox+8+f*(w-16);el("circle",{cx:x,cy:oy+h+6,r:6,fill:red},rp);el("line",{x1:x,y1:oy+h+12,x2:x,y2:oy+h+46,stroke:red,"stroke-width":3},rp)});
  el("text",{x:200,y:oy+h/2+4,"text-anchor":"middle",fill:ink2,"font-size":14,"font-family":"IBM Plex Mono, monospace"},rp,fmt(c.area,0)+" m² roof (plan)");
  el("text",{x:200,y:oy+h+72,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":"IBM Plex Mono, monospace"},rp,"peak "+fmt(c.Q,2)+" L/s · "+c.no+" outlet"+(c.no>1?"s":"")+" × "+fmt(c.Qo,2)+" L/s");
  el("text",{x:200,y:oy+h+92,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},rp,"gutter "+fmt(c.L,1)+" m, fall 1 in "+fmt(c.gs,0));
  $("rLabel").textContent=fmt(c.L,0)+" × "+fmt(c.W,0)+" m";
  // section
  const sv=$("gs2");sv.innerHTML="";const g=c.g,k=140/Math.max(c.gt==="h"?c.gw/2:Math.max(c.gw,c.gd)/1.2,1)*0.9;
  const cx=150,top=40;
  if(c.gt==="h"){const R=c.gw/2*k,cy=top;
    el("path",{d:`M ${cx-R} ${cy} A ${R} ${R} 0 0 0 ${cx+R} ${cy}`,fill:"none",stroke:ink,"stroke-width":3},sv);
    const y=g.y*1000*k,dx=Math.sqrt(Math.max(0,R*R-(R-y)*(R-y)));
    el("path",{d:`M ${cx-dx} ${cy+R-y} L ${cx+dx} ${cy+R-y} A ${R} ${R} 0 0 1 ${cx-dx} ${cy+R-y} Z`,fill:blue,opacity:.4,stroke:blue},sv);
    el("text",{x:cx,y:cy+R+26,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"Ø "+fmt(c.gw,0)+" mm half-round");
    el("text",{x:cx,y:cy+R+44,"text-anchor":"middle",fill:red,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"water "+fmt(g.y*1000,0)+" mm deep");}
  else{const w=c.gw*k,d=c.gd*k;
    el("path",{d:`M ${cx-w/2} ${top} L ${cx-w/2} ${top+d} L ${cx+w/2} ${top+d} L ${cx+w/2} ${top}`,fill:"none",stroke:ink,"stroke-width":3},sv);
    const y=g.y*1000*k;el("rect",{x:cx-w/2+1.5,y:top+d-y,width:w-3,height:y,fill:blue,opacity:.4,stroke:blue},sv);
    el("text",{x:cx,y:top+d+26,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,fmt(c.gw,0)+" × "+fmt(c.gd,0)+" mm box");
    el("text",{x:cx,y:top+d+44,"text-anchor":"middle",fill:red,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"water "+fmt(g.y*1000,0)+" mm deep");}
  el("text",{x:cx,y:246,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,fmt(c.Qg,2)+" L/s at "+fmt(c.fl,0)+"% full");
  $("sLabel").textContent="n "+c.n;
  const tb=$("tb");tb.innerHTML="";[50,63,75,90,100,110,150].forEach(d=>{const q=pipeQ(d/1000,c.g.y)*1000,need=Math.max(1,Math.ceil(c.Q/q-1e-9)),tr=document.createElement("tr");
    tr.innerHTML=`<td>${d} mm${d===c.pd?" ◀":""}</td><td>${fmt(q,2)}</td><td>${fmt(q*3600/(c.C*c.i),1)}</td><td class="${need>c.no?"bad":"ok"}">${need}</td>`;tb.appendChild(tr)});
}
""")
