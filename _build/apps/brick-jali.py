APP = dict(
slug="brick-jali", title="Brick Jali Open Area", h1="Brick Jali Open Area",
sub="Set the brick, the joint and the gap between bricks in a honeycomb jali. Get the real open area, the bearing each brick keeps on the course below, bricks per m² and a full panel elevation you can count.",
meta=[("Sheet","T-50"),("Method","Module geometry"),("Units","mm, m²"),("By","@smart_tools_every_week")],
source="Honeycomb jali geometry (first principles): each course is brick, gap, brick…; the next course is offset half a module so every brick sits centred over a gap. Module = brick face u + gap g; open area = g ÷ (u + g); bearing each side = (u − g) ÷ 2; bricks per m² = 10⁶ ÷ ((u + g)(h + joint)). Brick sizes: IS 1077 modular 190 × 90 × 90 and common 230 × 110 × 75. Minimum bearing is your choice (editable); check slender or tall panels with an engineer.",
inputs="""
      <label for="bk">Brick
        <select id="bk"><option value="m" selected>Modular 190 × 90 × 90 (IS 1077)</option><option value="c">Common 230 × 110 × 75</option><option value="x">Custom</option></select>
      </label>
      <div class="row">
        <label for="L">Length mm<input id="L" type="number" step="5" value="190"></label>
        <label for="W">Width mm<input id="W" type="number" step="5" value="90"></label>
      </div>
      <div class="row">
        <label for="H">Height mm<input id="H" type="number" step="5" value="90"></label>
        <label for="j">Bed joint mm<input id="j" type="number" step="1" value="10"></label>
      </div>
      <label for="lay">Laid
        <select id="lay"><option value="flat" selected>Flat (face L × H, wall W thick)</option><option value="edge">On edge (face L × W, wall H thick)</option></select>
      </label>
      <div class="row">
        <label for="g">Gap between bricks mm<input id="g" type="number" step="5" value="95"></label>
        <label for="mb">Min bearing mm<input id="mb" type="number" step="5" value="45"></label>
      </div>
      <div class="row">
        <label for="pw">Panel width m<input id="pw" type="number" step="0.1" value="1.8"></label>
        <label for="ph">Panel height m<input id="ph" type="number" step="0.1" value="1.2"></label>
      </div>
      <p class="note">Open area is the see-through part of the wall face. Air flow through the jali is less than this free area, and deeper walls cut more sun at an angle.</p>
""",
right="""
      <div class="readout">
        <div><b>Open area</b><span id="oO" class="hi">–</span></div>
        <div><b>Bearing each side</b><span id="oB">–</span></div>
        <div><b>Bricks per m²</b><span id="oN">–</span></div>
        <div><b>Bricks in panel</b><span id="oP">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Panel elevation <span id="eLabel"></span></h2><svg id="elev" viewBox="0 0 580 320" role="img" aria-label="Elevation of the jali panel with every brick"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Module <span id="mLabel"></span></h2><svg id="mod" viewBox="0 0 300 230" role="img" aria-label="One jali module with gap, bearing and joint"></svg></div>
        <div class="view"><h2>Open area vs gap <span>bearing limit in red</span></h2><svg id="chart" viewBox="0 0 300 230" role="img" aria-label="Chart of open area against gap"></svg></div>
      </div>
      <div class="data"><h2>Gap options <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Gap</th><th>Open area</th><th>Bearing</th><th>Bricks / m²</th><th>Saved vs solid</th><th>Check</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const SIZES={m:[190,90,90],c:[230,110,75]};
$("bk").addEventListener("change",()=>{const s=SIZES[$("bk").value];if(s){$("L").value=s[0];$("W").value=s[1];$("H").value=s[2];$("g").value=Math.round(s[0]/2/5)*5}render()});
["L","W","H"].forEach(id=>$(id).addEventListener("input",()=>{$("bk").value="x"}));
function mod(u,g,hc,j,mb){const p=u+g,br=(u-g)/2;return {g,p,open:g/p*100,br,ok:br>=mb-1e-9&&g>=0,perM2:1e6/(p*hc),save:(1-(u+j)/p)*100}}
function calc(){
  const L=num("L",40,600,190),W=num("W",30,400,90),H=num("H",30,400,90),j=num("j",0,40,10),mb=num("mb",0,300,45);
  const edge=$("lay").value==="edge",u=L,hf=edge?W:H,t=edge?H:W,hc=hf+j;
  const g=num("g",0,u,95),pw=num("pw",0.2,30,1.8),ph=num("ph",0.2,30,1.2);
  const m=mod(u,g,hc,j,mb),P=pw*1000,Q=ph*1000,courses=Math.max(1,Math.floor((Q+j)/hc));
  // panel layout: odd courses start with a full brick, even courses with a closer (u-g)/2
  const C=[];let bricks=0,closers=0,open=0;
  for(let r=0;r<courses;r++){const off=r%2?m.p/2:0,list=[];
    for(let x=-off;x<P;x+=m.p){const a=Math.max(0,x),b=Math.min(P,x+u);if(b-a>0.5){list.push([a,b]);bricks++;if(b-a<u-0.5)closers++}}
    let covered=list.reduce((s,q)=>s+(q[1]-q[0]),0);open+=(P-covered)*(r<courses-1?hc:hf);C.push(list);if(bricks>60000)break}
  const panelOpen=open/(P*courses*hc)*100;
  const maxG=Math.max(0,u-2*mb),opts=[];for(let x=20;x<=Math.min(u,maxG+30);x+=Math.max(5,Math.round(u/20/5)*5))opts.push(x);
  if(!opts.some(x=>Math.abs(x-g)<0.5))opts.push(g);opts.sort((a,b)=>a-b);
  return {L,W,H,j,mb,u,hf,t,hc,g,pw,ph,P,Q,m,courses,C,bricks,closers,open,panelOpen,maxG,opts:opts.map(x=>mod(u,x,hc,j,mb)),edge};
}
function render(){
  const c=calc(),m=c.m,ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),ok=css("--ok"),paper=css("--paper"),F="IBM Plex Mono, monospace",BR="#B5653F";
  $("oO").textContent=fmt(m.open,1)+"%";$("oB").textContent=fmt(m.br,Math.abs(m.br%1)>0.01?1:0)+" mm";$("oB").className=m.ok?"ok":"bad";
  $("oN").textContent=fmt(m.perM2,1);$("oP").textContent=c.bricks;
  // elevation
  const ev=$("elev");ev.innerHTML="";const usedH=c.courses*c.hc-c.j,k=Math.min(520/c.P,262/usedH),ox=(580-c.P*k)/2,oy=24+262-(262-usedH*k)/2;
  el("rect",{x:fmt(ox,1),y:fmt(oy-usedH*k,1),width:fmt(c.P*k,1),height:fmt(usedH*k,1),fill:paper},ev);
  const big=c.bricks>4000;
  if(!big)c.C.forEach((list,r)=>{const yb=oy-r*c.hc*k;list.forEach(([a,b])=>el("rect",{x:fmt(ox+a*k,2),y:fmt(yb-c.hf*k,2),width:fmt(Math.max(0.3,(b-a)*k),2),height:fmt(Math.max(0.3,c.hf*k),2),fill:BR,stroke:ink,"stroke-width":Math.min(1,k*3)},ev))});
  else el("text",{x:290,y:160,"text-anchor":"middle",fill:ink,"font-size":14,"font-family":F},ev,c.bricks+" bricks: too many to draw, see the module");
  el("rect",{x:fmt(ox,1),y:fmt(oy-usedH*k,1),width:fmt(c.P*k,1),height:fmt(usedH*k,1),fill:"none",stroke:ink,"stroke-width":1.5},ev);
  el("text",{x:290,y:16,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":F},ev,fmt(c.pw,2)+" m wide × "+c.courses+" courses ("+fmt(usedH/1000,2)+" m)");
  el("text",{x:290,y:312,"text-anchor":"middle",fill:ink2,"font-size":13,"font-family":F},ev,c.bricks+" bricks incl. "+c.closers+" cut · panel open "+fmt(c.panelOpen,1)+"%");
  $("eLabel").textContent=c.edge?"on edge":"flat";
  // module detail: 2 courses x 2 modules
  const mv=$("mod");mv.innerHTML="";const span=2*m.p,kk=Math.min(250/span,120/(2*c.hc)),mx=25,my=150;
  for(let r=0;r<3;r++){const off=r%2?m.p/2:0,yb=my-r*c.hc*kk;for(let x=-off;x<span;x+=m.p){const a=Math.max(0,x),b=Math.min(span,x+c.u);if(b>a)el("rect",{x:fmt(mx+a*kk,1),y:fmt(yb-c.hf*kk,1),width:fmt((b-a)*kk,1),height:fmt(c.hf*kk,1),fill:BR,stroke:ink,"stroke-width":1},mv)}}
  el("line",{x1:fmt(mx+c.u*kk,1),y1:my+14,x2:fmt(mx+m.p*kk,1),y2:my+14,stroke:blue,"stroke-width":2},mv);
  el("text",{x:fmt(mx+(c.u+m.g/2)*kk,1),y:my+30,"text-anchor":"middle",fill:blue,"font-size":12,"font-family":F},mv,"gap "+fmt(m.g,0));
  el("line",{x1:mx,y1:my+14,x2:fmt(mx+c.u*kk,1),y2:my+14,stroke:ink2},mv);
  el("text",{x:fmt(mx+c.u*kk/2,1),y:my+30,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":F},mv,"brick "+fmt(c.u,0));
  const yb1=my-c.hc*kk-c.hf*kk;if(m.br>0)el("rect",{x:fmt(mx+(m.p/2)*kk,1),y:fmt(yb1-c.hc*kk,1),width:fmt(Math.max(1,m.br*kk),1),height:fmt((c.hc+c.hf)*kk,1),fill:m.ok?ok:red,opacity:.35,stroke:m.ok?ok:red,"stroke-width":2.5},mv);
  el("line",{x1:fmt(mx+(m.p/2+m.br/2)*kk,1),y1:22,x2:fmt(mx+(m.p/2+m.br/2)*kk,1),y2:fmt(yb1-c.hc*kk,1),stroke:m.ok?ok:red,"stroke-width":1.2},mv);
  el("text",{x:fmt(Math.min(220,Math.max(80,mx+(m.p/2+m.br/2)*kk)),1),y:16,"text-anchor":"middle",fill:m.ok?ok:red,"font-size":12,"font-family":F},mv,"bearing "+fmt(m.br,Math.abs(m.br%1)>0.01?1:0)+" mm");
  el("text",{x:150,y:205,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":F},mv,"open = "+fmt(m.g,0)+" ÷ "+fmt(m.p,0)+" = "+fmt(m.open,1)+"%");
  el("text",{x:150,y:224,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},mv,"wall "+fmt(c.t,0)+" mm thick · course "+fmt(c.hc,0)+" mm");
  $("mLabel").textContent=fmt(c.u,0)+" + "+fmt(m.g,0)+" mm";
  // chart open % vs gap
  const cv=$("chart");cv.innerHTML="";const X=g=>40+g/c.u*245,Y=p=>195-p/50*170;
  el("line",{x1:40,y1:195,x2:288,y2:195,stroke:ink},cv);el("line",{x1:40,y1:20,x2:40,y2:195,stroke:ink},cv);
  [0,10,20,30,40,50].forEach(p=>{el("line",{x1:40,y1:fmt(Y(p),1),x2:288,y2:fmt(Y(p),1),stroke:rule},cv);el("text",{x:34,y:fmt(Y(p)+4,1),"text-anchor":"end",fill:ink2,"font-size":11,"font-family":F},cv,p+"%")});
  if(c.maxG<c.u)el("rect",{x:fmt(X(c.maxG),1),y:20,width:fmt(X(c.u)-X(c.maxG),1),height:175,fill:red,opacity:.12},cv);
  let d="";for(let i=0;i<=40;i++){const g=c.u*i/40;d+=(i?"L":"M")+fmt(X(g),1)+" "+fmt(Y(g/(c.u+g)*100),1)}el("path",{d,fill:"none",stroke:blue,"stroke-width":2},cv);
  el("circle",{cx:fmt(X(m.g),1),cy:fmt(Y(m.open),1),r:5,fill:m.ok?ok:red},cv);
  el("text",{x:fmt(Math.min(X(m.g)+8,215),1),y:fmt(Y(m.open)-8,1),fill:m.ok?ok:red,"font-size":12,"font-family":F},cv,fmt(m.open,1)+"%");
  el("text",{x:164,y:220,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},cv,"gap 0 → "+fmt(c.u,0)+" mm (max 50% at zero bearing)");
  // table
  $("tb").innerHTML=c.opts.map(o=>`<tr${Math.abs(o.g-m.g)<0.5?' class="now"':""}><td>${fmt(o.g,0)} mm</td><td>${fmt(o.open,1)}%</td><td>${fmt(o.br,Math.abs(o.br%1)>0.01?1:0)} mm</td><td>${fmt(o.perM2,1)}</td><td>${fmt(o.save,0)}%</td><td class="${o.ok?"ok":"bad"}">${o.ok?"bearing OK":"under "+fmt(c.mb,0)+" mm"}</td></tr>`).join("");
  $("dLabel").textContent="largest gap for "+fmt(c.mb,0)+" mm bearing: "+fmt(c.maxG,0)+" mm ("+fmt(c.maxG/(c.u+c.maxG)*100,1)+"% open)";
}
""")
