APP = dict(
slug="driveway-turning", title="Driveway Turning Check", h1="Driveway Turning",
sub="Pick a car and the width of the lane it arrives in and the lane it turns into. See the swept path round a 90° corner, the clearance to the walls, and the narrowest lane that lets this car turn in one move.",
meta=[("Sheet","T-30"),("Method","Swept path"),("Units","m"),("By","@smart_tools_every_week")],
source="Single-track (bicycle) model: the car turns about a point on the rear-axle line. Rear-axle centre radius Rm = √(Rk² − wheelbase²) − track/2 from the published kerb-to-kerb turning radius Rk; outer front corner radius = √((Rm + W/2)² + (wheelbase + front overhang)²). Car sizes are typical, not exact; enter your design vehicle. Low-speed geometry only: no tyre slip, no reversing, square inner corner. Always draw the design vehicle's swept path on the final drawing.",
inputs="""
      <label for="car">Design car
        <select id="car">
          <option value="h">Hatchback (3.85 m)</option>
          <option value="s" selected>Compact SUV (4.30 m)</option>
          <option value="l">Large SUV (4.80 m)</option>
          <option value="c">Custom</option>
        </select>
      </label>
      <div class="row">
        <label for="A">Arriving lane m<input id="A" type="number" step="0.1" value="4.5"></label>
        <label for="B">Lane turned into m<input id="B" type="number" step="0.1" value="3.5"></label>
      </div>
      <label for="pos">Car position on the turn <span id="posv" class="time" style="font-size:18px"></span><input id="pos" type="range" min="0" max="100" step="1" value="50"></label>
      <div class="row">
        <label for="len">Car length m<input id="len" type="number" step="0.05" value="4.3"></label>
        <label for="wid">Car width m<input id="wid" type="number" step="0.05" value="1.79"></label>
      </div>
      <div class="row">
        <label for="wb">Wheelbase m<input id="wb" type="number" step="0.05" value="2.61"></label>
        <label for="fo">Front overhang m<input id="fo" type="number" step="0.05" value="0.9"></label>
      </div>
      <label for="rk">Turning radius, kerb to kerb m<input id="rk" type="number" step="0.1" value="5.3"></label>
      <p class="note">Turning radius is the figure in the car's brochure (kerb to kerb). The car arrives in the lane on the left and turns left into the lane going up. The corner on the inside of the turn is a square wall or pillar. Clearance is the smallest gap between any part of the body and a wall.</p>
""",
right="""
      <div class="readout">
        <div><b>Verdict</b><span id="oV" class="hi">–</span></div>
        <div><b>Clearance</b><span id="oC">–</span></div>
        <div><b>Narrowest equal lane</b><span id="oN">–</span></div>
        <div><b>Body swing radius</b><span id="oW">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Swept path, plan <span id="plL"></span></h2><svg id="pl" viewBox="0 0 840 520" role="img" aria-label="Plan of a car turning a corner with its swept path"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
        <div class="view"><h2>Lane needed <span>arriving = turned into</span></h2><div class="tablewrap"><table><thead><tr><th>Car</th><th>Narrowest lane</th><th>Rm</th><th>Swing R</th></tr></thead><tbody id="tb"></tbody></table></div></div>
      </div>
""",
css=".view.full svg{max-height:520px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const CARS={h:{n:"Hatchback",len:3.85,wid:1.735,wb:2.45,fo:0.8,rk:4.8},s:{n:"Compact SUV",len:4.3,wid:1.79,wb:2.61,fo:0.9,rk:5.3},l:{n:"Large SUV",len:4.8,wid:1.855,wb:2.745,fo:0.95,rk:5.8}};
$("car").addEventListener("change",()=>{const k=CARS[$("car").value];if(k){["len","wid","wb","fo","rk"].forEach(i=>$(i).value=k[i])}render()});
["len","wid","wb","fo","rk"].forEach(i=>$(i).addEventListener("input",()=>{if($("car").value!=="c"&&document.activeElement===$(i))$("car").value="c"}));
function carParams(o){
  const len=o.len,wid=o.wid,wb=Math.min(o.wb,len*0.9),fo=Math.min(o.fo,len-wb-0.1),ro=Math.max(0.1,len-wb-fo);
  const tr=Math.max(0.5,wid-0.2),rk=Math.max(o.rk,Math.hypot(wb,tr/2)+tr/2+0.05);
  const Rm=Math.sqrt(Math.max(0.01,rk*rk-wb*wb))-tr/2;
  const Rout=Math.hypot(Rm+wid/2,wb+fo),Rin=Math.max(0,Rm-wid/2);
  return {len,wid,wb,fo,ro,tr,rk,Rm:Math.max(0.5,Rm),Rout,Rin};
}
function carPoly(c,x,y,h){ // reference = rear axle centre, heading h; local (u forward, v left)
  const L=[[-c.ro,-c.wid/2],[c.wb+c.fo,-c.wid/2],[c.wb+c.fo,c.wid/2],[-c.ro,c.wid/2]];
  const ch=Math.cos(h),sh=Math.sin(h);return L.map(([u,v])=>[x+u*ch-v*sh,y+u*sh+v*ch]);
}
function pathPoint(P,t){ // t 0..1 along straight-in, arc, straight-out; returns x,y,heading
  const S=6,arcL=Math.PI/2*P.Rr,tot=2*S+arcL,d=t*tot;
  if(d<S)return [P.xc-P.Rr-(S-d),P.yc,0];
  if(d<S+arcL){const a=(d-S)/P.Rr;return [P.xc-P.Rr+P.Rr*Math.sin(a),P.yc+P.Rr-P.Rr*Math.cos(a),a]}
  return [P.xc,P.yc+P.Rr+(d-S-arcL),Math.PI/2];
}
function dist(p,xr,xi,Ay){ // clearance of one point to walls: bottom y=0, right x=xr, inner block x<=xi,y>=Ay
  let d=Math.min(p[1],xr-p[0]);
  let q;
  if(p[0]<=xi&&p[1]>=Ay)q=-Math.min(xi-p[0],p[1]-Ay);
  else if(p[0]>xi&&p[1]>=Ay)q=p[0]-xi;
  else if(p[0]<=xi&&p[1]<Ay)q=Ay-p[1];
  else q=Math.hypot(p[0]-xi,p[1]-Ay);
  return Math.min(d,q);
}
function clearance(c,P,A,B,xr){
  const xi=xr-B;let m=1e9;
  const N=44;
  for(let k=0;k<=N;k++){
    const [x,y,h]=pathPoint(P,k/N),poly=carPoly(c,x,y,h);
    for(let e=0;e<4;e++){const p0=poly[e],p1=poly[(e+1)%4];for(let s=0;s<6;s++){const f=s/6;m=Math.min(m,dist([p0[0]+(p1[0]-p0[0])*f,p0[1]+(p1[1]-p0[1])*f],xr,xi,A))}}
  }
  return m;
}
function best(c,A,B,xr){
  let bm=-1e9,bp=null;const xi=xr-B;
  for(let i=0;i<=8;i++)for(let j=0;j<=8;j++)for(let k=0;k<5;k++){
    const yc=c.wid/2+(A-c.wid)*(i/8),xc=xi+c.wid/2+(B-c.wid)*(j/8),Rr=c.Rm+k*0.6;
    if(A<c.wid||B<c.wid){}
    const P={yc,xc,Rr},m=clearance(c,P,A,B,xr);
    if(m>bm){bm=m;bp=P}
  }
  return {m:bm,P:bp};
}
function narrowest(c){
  let lo=c.wid,hi=14;
  if(best(c,hi,hi,hi).m<0)return NaN;
  for(let i=0;i<11;i++){const mid=(lo+hi)/2;if(best(c,mid,mid,mid).m>=0)hi=mid;else lo=mid}
  return hi;
}
function calc(){
  const o={len:num("len",2,12,4.3),wid:num("wid",1,3,1.79),wb:num("wb",1.2,6,2.61),fo:num("fo",0.2,2,0.9),rk:num("rk",2,15,5.3)};
  const A=num("A",1.5,12,4.5),B=num("B",1.5,12,3.5),pos=num("pos",0,100,50)/100;
  const c=carParams(o),xr=B+6; // right wall; the lane turned into occupies x in [xr-B,xr]
  const b=best(c,A,B,xr);
  return {c,A,B,pos,xr,b};
}
function render(){
  const {c,A,B,pos,xr,b}=calc();
  const ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),ok=css("--ok"),bad=css("--bad"),sun=css("--sun");
  $("posv").textContent=Math.round(pos*100)+"%";
  const clr=b.m,pass=clr>=0;
  const nar=narrowest(c);
  $("oV").textContent=pass?"Turns in one move":"Needs reversing";$("oV").className=pass?"":"bad";$("oV").style.fontSize="19px";
  $("oC").textContent=(clr*1000>=0?"":"–")+Math.abs(Math.round(clr*1000))+" mm"+(pass?"":" short");$("oC").className=pass?"":"bad";
  $("oN").textContent=Number.isFinite(nar)?fmt(nar,2)+" m":"> 14 m";
  $("oW").textContent=fmt(c.Rout,2)+" m";
  const C=[[`Car body clears every wall by ${Math.round(clr*1000)} mm at its tightest`,pass],
    [`Arriving lane ${fmt(A,1)} m vs ${fmt(c.wid,2)} m car: ${fmt(A-c.wid,2)} m spare in a straight line`,A>=c.wid+0.6,"warn"],
    [`Needs a ${Number.isFinite(nar)?fmt(nar,2):">14"} m lane (both lanes equal) to turn without reversing`,A>=nar&&B>=nar,"warn"],
    [`Body swings ${fmt(c.Rout,2)} m from the turning point, wider than the ${fmt(c.rk,2)} m brochure radius (that is the outer wheel)`,true,"info"]];
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=pass?"fits":"does not fit";
  // DRAWING: x to the right, y up. World extent
  const sv=$("pl");sv.innerHTML="";
  const x0=-3.2,x1=xr+0.8,y0=-0.6,y1=A+Math.max(4.8,c.len+0.8);
  const sc=Math.min(800/(x1-x0),490/(y1-y0)),ox=(840-(x1-x0)*sc)/2,oy=520-(520-(y1-y0)*sc)/2;
  const X=v=>ox+(v-x0)*sc,Y=v=>oy-(v-y0)*sc;
  const xi=xr-B;
  // free space
  el("rect",{x:X(x0),y:Y(A),width:(xr-x0)*sc,height:A*sc,fill:rule,opacity:.35},sv);
  el("rect",{x:X(xi),y:Y(y1),width:B*sc,height:(y1-A)*sc,fill:rule,opacity:.35},sv);
  // walls: outer (bottom + right), inner block
  el("polyline",{points:`${X(x0)},${Y(0)} ${X(xr)},${Y(0)} ${X(xr)},${Y(y1)}`,fill:"none",stroke:ink,"stroke-width":4},sv);
  el("polyline",{points:`${X(x0)},${Y(A)} ${X(xi)},${Y(A)} ${X(xi)},${Y(y1)}`,fill:"none",stroke:ink,"stroke-width":4},sv);
  el("rect",{x:X(x0),y:Y(y1),width:(xi-x0)*sc,height:(y1-A)*sc,fill:ink,opacity:.07},sv);
  // swept footprint: union of car polygons
  const P=b.P,N=90;
  for(let k=0;k<=N;k++){const [x,y,h]=pathPoint(P,k/N),poly=carPoly(c,x,y,h);el("polygon",{points:poly.map(p=>X(p[0])+","+Y(p[1])).join(" "),fill:pass?blue:red,opacity:.07},sv)}
  // rear axle path
  const pts=[];for(let k=0;k<=N;k++){const [x,y]=pathPoint(P,k/N);pts.push(X(x)+","+Y(y))}
  el("polyline",{points:pts.join(" "),fill:"none",stroke:sun,"stroke-width":2,"stroke-dasharray":"6 5"},sv);
  // car at slider position
  const [cx,cy,ch]=pathPoint(P,0.12+0.76*pos),poly=carPoly(c,cx,cy,ch);
  el("polygon",{points:poly.map(p=>X(p[0])+","+Y(p[1])).join(" "),fill:sheet,stroke:pass?ink:red,"stroke-width":2.5},sv);
  // wheels + front marker
  const wheel=(u,v)=>{const a=[u-0.32,v-0.11],b2=[u+0.32,v-0.11],c2=[u+0.32,v+0.11],d=[u-0.32,v+0.11];
    const T=([uu,vv])=>{const hh=ch;return [cx+uu*Math.cos(hh)-vv*Math.sin(hh),cy+uu*Math.sin(hh)+vv*Math.cos(hh)]};
    el("polygon",{points:[a,b2,c2,d].map(T).map(p=>X(p[0])+","+Y(p[1])).join(" "),fill:ink2},sv)};
  [[0,c.tr/2],[0,-c.tr/2],[c.wb,c.tr/2],[c.wb,-c.tr/2]].forEach(([u,v])=>wheel(u,v));
  const fm=[cx+(c.wb+c.fo)*Math.cos(ch),cy+(c.wb+c.fo)*Math.sin(ch)];el("circle",{cx:X(fm[0]),cy:Y(fm[1]),r:5,fill:red},sv);
  // dims
  el("text",{x:X(x0)+8,y:Y(0)-8,fill:ink2,"font-size":13,"font-family":"IBM Plex Mono, monospace"},sv,"arriving lane "+fmt(A,1)+" m");
  el("text",{x:X(xi)-8,y:Y(y1)+22,"text-anchor":"end",fill:ink2,"font-size":13,"font-family":"IBM Plex Mono, monospace"},sv,"lane "+fmt(B,1)+" m →");
  $("plL").textContent=fmt(c.len,2)+" m car · swing "+fmt(c.Rout,2)+" m · "+(pass?"clear":"hits a wall");
  // TABLE
  const tb=$("tb");tb.innerHTML="";
  ["h","s","l"].forEach(k=>{const cc=carParams(CARS[k]),n2=narrowest(cc),tr=document.createElement("tr");if($("car").value===k)tr.className="now";
    tr.innerHTML=`<td>${CARS[k].n}</td><td>${Number.isFinite(n2)?fmt(n2,2):">14"} m</td><td>${fmt(cc.Rm,2)}</td><td>${fmt(cc.Rout,2)}</td>`;tb.appendChild(tr)});
  const tr2=document.createElement("tr");if($("car").value==="c")tr2.className="now";tr2.innerHTML=`<td>Your car</td><td>${Number.isFinite(nar)?fmt(nar,2):">14"} m</td><td>${fmt(c.Rm,2)}</td><td>${fmt(c.Rout,2)}</td>`;tb.appendChild(tr2);
}
""")
