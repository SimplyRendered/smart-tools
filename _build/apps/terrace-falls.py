APP = dict(
slug="terrace-falls", title="Terrace Screed Falls", h1="Terrace Screed Falls",
sub="Enter the terrace, the outlets and the fall. Get the thickest point of the screed, the real fall along the valleys, the volume and the dead load, with the hip-and-valley falls drawn on the plan.",
meta=[("Sheet","T-46"),("Method","Hip & valley planes"),("Units","m, mm, kN"),("By","@smart_tools_every_week")],
source="Screed top = minimum thickness + fall × distance to the nearest outlet, each plane falling square to the edge it drains (hip-and-valley), so valleys run on the diagonal at the fall ÷ √2. Average thickness and volume by numerical integration over the plan (first principles). Fall, minimum thickness and density are editable: take them from your waterproofing specification (for example BS 6229 designs falls at 1:40 so the finished roof is not flatter than 1:80).",
inputs="""
      <div class="row">
        <label for="L">Terrace length m<input id="L" type="number" step="0.5" value="12"></label>
        <label for="W">Terrace width m<input id="W" type="number" step="0.5" value="8"></label>
      </div>
      <label for="lay">Outlets
        <select id="lay"><option value="edge" selected>Along one long edge</option><option value="both">Along both long edges</option><option value="corners">At the 4 corners</option></select>
      </label>
      <div class="row">
        <label for="n">Outlets per edge<input id="n" type="number" step="1" value="2"></label>
        <label for="N">Fall 1 in<input id="N" type="number" step="10" value="100"></label>
      </div>
      <div class="row">
        <label for="tmin">Min. screed mm<input id="tmin" type="number" step="5" value="40"></label>
        <label for="den">Density kN/m³<input id="den" type="number" step="1" value="20"></label>
      </div>
      <p class="note">The fall is set on each plane. Valleys into the outlets run on the diagonal, so they are flatter than the planes. Minimum thickness is the screed at the outlet. Cement screed or brick-bat coba is roughly 19–22 kN/m³; use your own value. Outlets per edge is ignored for the 4-corner layout.</p>
""",
right="""
      <div class="readout">
        <div><b>Thickest point</b><span id="oMax" class="hi">–</span></div>
        <div><b>Valley fall</b><span id="oVf">–</span></div>
        <div><b>Screed volume</b><span id="oVol">–</span></div>
        <div><b>Dead load avg</b><span id="oLd">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Plan of falls <span id="pLabel"></span></h2><svg id="plan" viewBox="0 0 580 380" role="img" aria-label="Terrace plan shaded by screed thickness with outlets"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Section <span id="sLabel">along the outlet edge</span></h2><svg id="sec" viewBox="0 0 300 220" role="img" aria-label="Section of screed thickness along the terrace"></svg></div>
        <div class="view"><h2>Per outlet <span>catchment m²</span></h2><svg id="cat" viewBox="0 0 300 220" role="img" aria-label="Roof area draining to each outlet"></svg></div>
      </div>
      <div class="data"><h2>Outlet options <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Layout</th><th>Outlets</th><th>Thickest</th><th>Average</th><th>Volume</th><th>Load avg</th></tr></thead><tbody id="tb"></tbody></table></div>
      <p class="note" id="vNote" style="margin-top:8px"></p></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function outlets(L,W,lay,n){const o=[];
  if(lay==="corners")return [[0,0],[L,0],[0,W],[L,W]];
  for(let i=0;i<n;i++)o.push([(i+.5)*L/n,0]);
  if(lay==="both")for(let i=0;i<n;i++)o.push([(i+.5)*L/n,W]);
  return o}
function dist(x,y,O){let d=Infinity,k=0,g=Infinity;for(let i=0;i<O.length;i++){const ax=Math.abs(x-O[i][0]),ay=Math.abs(y-O[i][1]),e=Math.max(ax,ay),h=ax*ax+ay*ay;if(e<d-1e-9||(Math.abs(e-d)<=1e-9&&h<g)){d=e;k=i;g=h}}return [d,k]}
function mix(a,b,t){const p=h=>{h=h.replace("#","");if(h.length===3)h=h.split("").map(ch=>ch+ch).join("");const n=parseInt(h,16);return Number.isFinite(n)?[n>>16&255,n>>8&255,n&255]:[128,128,128]};const A=p(a),B=p(b);return "rgb("+A.map((v,i)=>Math.round(v+(B[i]-v)*t)).join(",")+")"}
function solve(L,W,O,tmin,N,G){
  const nx=G,ny=Math.max(4,Math.round(G*W/L)),dx=L/nx,dy=W/ny,ar=new Array(O.length).fill(0);let s=0,mx=0,hx=0,hy=0;
  for(let i=0;i<nx;i++)for(let j=0;j<ny;j++){const [d,k]=dist((i+.5)*dx,(j+.5)*dy,O);s+=d;ar[k]+=dx*dy}
  for(let i=0;i<=nx;i++)for(let j=0;j<=ny;j++){const d=dist(i*dx,j*dy,O)[0];if(d>mx+1e-9){mx=d;hx=i*dx;hy=j*dy}}
  const r=1000/N,avg=tmin+r*s/(nx*ny),max=tmin+r*mx;return {avg,max,hx,hy,ar}}
function calc(){
  const L=num("L",1,300,12),W=num("W",1,300,8),lay=$("lay").value,n=Math.round(num("n",1,12,2)),N=num("N",10,1000,100),tmin=num("tmin",0,300,40),den=num("den",1,40,20);
  const O=outlets(L,W,lay,n),r=solve(L,W,O,tmin,N,120),A=L*W,vol=A*r.avg/1000,guess=A*(tmin+r.max)/2/1000;
  const opts=[];[["edge",1],["edge",2],["edge",3],["edge",4],["both",1],["both",2],["both",3],["corners",1]].forEach(([l,k])=>{const OO=outlets(L,W,l,k),q=solve(L,W,OO,tmin,N,60);
    opts.push({l,k,cnt:OO.length,max:q.max,avg:q.avg,vol:A*q.avg/1000,ld:q.avg/1000*den,now:l===lay&&(l==="corners"||k===n)})});
  return {L,W,lay,n,N,tmin,den,O,A,vol,guess,ld:r.avg/1000*den,ldmax:r.max/1000*den,...r,opts};
}
const LN={edge:"One long edge",both:"Both long edges",corners:"4 corners"};
function render(){
  const c=calc(),sheet=css("--sheet"),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),F="IBM Plex Mono, monospace";
  $("oMax").textContent=fmt(c.max,0)+" mm";$("oVf").textContent="1 in "+fmt(c.N*Math.SQRT2,0);$("oVol").textContent=fmt(c.vol,c.vol<10?2:1)+" m³";$("oLd").textContent=fmt(c.ld,2)+" kN/m²";
  // plan
  const pv=$("plan");pv.innerHTML="";const k=Math.min(500/c.L,300/c.W),ox=(580-c.L*k)/2,oy=30,X=x=>ox+x*k,Y=y=>oy+(c.W-y)*k;
  const span=Math.max(c.max-c.tmin,1e-6),raw=span/10,steps=[5,10,20,25,50,100,200,500],step=steps.find(s=>s>=raw)||1000;
  const nx=Math.min(60,Math.max(12,Math.round(60))),ny=Math.max(4,Math.min(60,Math.round(nx*c.W/c.L))),cw=c.L/nx,ch=c.W/ny;
  for(let i=0;i<nx;i++)for(let j=0;j<ny;j++){const t=c.tmin+1000/c.N*dist((i+.5)*cw,(j+.5)*ch,c.O)[0],b=Math.floor((t-c.tmin)/step),op=0.1+0.75*Math.min(1,b*step/span);
    el("rect",{x:fmt(X(i*cw),2),y:fmt(Y((j+1)*ch),2),width:fmt(cw*k+0.6,2),height:fmt(ch*k+0.6,2),fill:mix(sheet,blue,op)},pv)}
  el("rect",{x:fmt(X(0),1),y:fmt(Y(c.W),1),width:fmt(c.L*k,1),height:fmt(c.W*k,1),fill:"none",stroke:ink,"stroke-width":2},pv);
  c.O.forEach(o=>{el("circle",{cx:fmt(X(o[0]),1),cy:fmt(Y(o[1]),1),r:7,fill:red,stroke:ink,"stroke-width":1},pv)});
  el("circle",{cx:fmt(X(c.hx),1),cy:fmt(Y(c.hy),1),r:5,fill:"none",stroke:red,"stroke-width":2},pv);
  el("text",{x:20,y:20,fill:red,"font-size":14,"font-family":F},pv,"○ high point "+fmt(c.max,0)+" mm");
  el("text",{x:290,y:fmt(Y(0)+22,1),"text-anchor":"middle",fill:ink,"font-size":14,"font-family":F},pv,fmt(c.L,1)+" m");
  el("text",{x:fmt(X(0)-8,1),y:fmt(Y(c.W/2),1),"text-anchor":"end",fill:ink,"font-size":14,"font-family":F},pv,fmt(c.W,1)+" m");
  el("text",{x:20,y:fmt(Math.min(372,Y(0)+44),1),fill:ink2,"font-size":13,"font-family":F},pv,"stronger blue = thicker · bands every "+step+" mm · ● outlet");
  $("pLabel").textContent=LN[c.lay]+" · "+c.O.length+" outlet"+(c.O.length>1?"s":"")+" · 1 in "+fmt(c.N,0);
  // section along x at y = high point
  const sv=$("sec");sv.innerHTML="";const sk=270/c.L,vk=120/Math.max(c.max,1),sb=170,pts=[];let ep=0;
  for(let i=0;i<=120;i++){const x=i/120*c.L,t=c.tmin+1000/c.N*dist(x,0,c.O)[0];ep=Math.max(ep,t);pts.push(fmt(15+x*sk,1)+","+fmt(sb-t*vk,1))}
  el("rect",{x:15,y:sb,width:270,height:14,fill:ink2,opacity:.45},sv);
  el("polygon",{points:"15,"+sb+" "+pts.join(" ")+" 285,"+sb,fill:blue,opacity:.55,stroke:blue},sv);
  el("text",{x:15,y:22,fill:red,"font-size":13,"font-family":F},sv,"ridge "+fmt(ep,0)+" mm · outlet "+fmt(c.tmin,0)+" mm");
  el("text",{x:15,y:205,fill:ink2,"font-size":12,"font-family":F},sv,"along the outlet edge · vertical × "+fmt(vk*1000/sk,0));
  // catchments
  const cv=$("cat");cv.innerHTML="";const mA=Math.max(...c.ar,1e-6),nb=c.ar.length,bw=Math.min(40,250/nb);
  c.ar.forEach((a,i)=>{const h=a/mA*140,x=25+i*(250/nb)+(250/nb-bw)/2;el("rect",{x:fmt(x,1),y:fmt(175-h,1),width:fmt(bw*0.85,1),height:fmt(h,1),fill:red,opacity:.75},cv);
    el("text",{x:fmt(x+bw*0.42,1),y:fmt(168-h,1),"text-anchor":"middle",fill:ink,"font-size":nb>6?10:12,"font-family":F},cv,fmt(a,0));
    el("text",{x:fmt(x+bw*0.42,1),y:192,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},cv,"O"+(i+1))});
  el("line",{x1:20,y1:175,x2:285,y2:175,stroke:ink},cv);
  el("text",{x:20,y:212,fill:ink2,"font-size":12,"font-family":F},cv,"total "+fmt(c.A,1)+" m²");
  // table
  $("tb").innerHTML=c.opts.map(o=>`<tr${o.now?' class="now"':""}><td>${LN[o.l]}</td><td>${o.cnt}</td><td>${fmt(o.max,0)} mm</td><td>${fmt(o.avg,0)} mm</td><td>${fmt(o.vol,1)} m³</td><td>${fmt(o.ld,2)} kN/m²</td></tr>`).join("");
  $("dLabel").textContent=fmt(c.L,1)+" × "+fmt(c.W,1)+" m · 1 in "+fmt(c.N,0);
  $("vNote").textContent="Average thickness "+fmt(c.avg,0)+" mm. Valleys run on the diagonal at 1 in "+fmt(c.N*Math.SQRT2,0)+": to keep them at 1 in "+fmt(c.N,0)+", set the planes at 1 in "+fmt(c.N/Math.SQRT2,0)+". (min + max) ÷ 2 would give "+fmt(c.guess,2)+" m³; the true volume is "+fmt(c.vol,2)+" m³. Load at the high point "+fmt(c.ldmax,2)+" kN/m².";
}
""")
