APP = dict(
slug="tile-layout", title="Floor Tile Layout & Quantity", h1="Floor Tile Layout",
sub="Lay out floor tiles on your room, straight, offset or diagonal. Count the full and cut tiles, boxes, skirting and grout, and avoid thin slivers at the walls.",
meta=[("Sheet","T-13"),("Method","Tile-by-tile count"),("Units","m / mm"),("By","@smart_tools_every_week")],
source="Tiles counted one by one on the actual layout (every cut uses a new tile), plus breakage. Grout kg/m² = (A+B)/(A×B) × joint × depth × 1.6, the usual manufacturer formula. Rule of thumb: keep edge cuts above one third of a tile.",
inputs="""
      <div class="row">
        <label for="L">Room length m<input id="L" type="number" step="0.05" value="4.2"></label>
        <label for="W">Room width m<input id="W" type="number" step="0.05" value="3.6"></label>
      </div>
      <label for="size">Tile
        <select id="size">
          <option value="600,600,4">600 × 600 mm</option>
          <option value="800,800,3" selected>800 × 800 mm</option>
          <option value="600,1200,2">600 × 1200 mm</option>
          <option value="300,300,11">300 × 300 mm</option>
          <option value="200,1200,6">200 × 1200 plank</option>
          <option value="cus">Custom</option>
        </select>
      </label>
      <div class="row" style="grid-template-columns:1fr 1fr 1fr">
        <label for="a">Along L mm<input id="a" type="number" value="800"></label>
        <label for="b">Along W mm<input id="b" type="number" value="800"></label>
        <label for="box">Tiles / box<input id="box" type="number" value="3"></label>
      </div>
      <label for="pat">Pattern
        <select id="pat"><option value="grid">Straight grid</option><option value="half">Offset ½ (brick)</option><option value="third">Offset ⅓ (planks)</option><option value="diag">Diagonal 45°</option></select>
      </label>
      <label for="start">Start the layout
        <select id="start"><option value="centre">Centred (balanced cuts)</option><option value="corner">From a corner (full tile at the door corner)</option></select>
      </label>
      <label for="sh">Shift layout mm <span id="shv" class="time" style="font-size:18px"></span><input id="sh" type="range" min="-400" max="400" step="10" value="0"></label>
      <div class="row">
        <label for="j">Joint mm<input id="j" type="number" step="0.5" value="2"></label>
        <label for="t">Tile thickness mm<input id="t" type="number" step="0.5" value="9"></label>
      </div>
      <div class="row">
        <label for="brk">Breakage %<input id="brk" type="number" step="1" value="3"></label>
        <label for="dw">Door width(s) m<input id="dw" type="number" step="0.05" value="0.9"></label>
      </div>
      <label for="skh">Skirting height mm (0 = none)<input id="skh" type="number" step="5" value="100"></label>
      <p class="note">Every cut piece is counted as a whole tile, so the count is on the safe side. Offcuts from a long cut can sometimes do a second short one. Slide "Shift" to move the grid and see how the edge cuts change.</p>
""",
right="""
      <div class="readout">
        <div><b>Tiles to buy</b><span id="oN" class="hi">–</span></div>
        <div><b>Boxes</b><span id="oB">–</span></div>
        <div><b>Smallest cut</b><span id="oC">–</span></div>
        <div><b>Floor area</b><span id="oA">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Layout plan <span id="planLabel"></span></h2><svg id="plan" viewBox="0 0 840 460" role="img" aria-label="Tile layout plan with cut tiles"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
        <div class="view"><h2>Count <span>tile by tile vs area method</span></h2>
          <div class="tablewrap"><table><tbody id="cnt"></tbody></table></div></div>
      </div>
      <div class="data">
        <h2>Materials <span>for the order</span></h2>
        <div class="tablewrap"><table><thead><tr><th>Item</th><th>Quantity</th><th>How</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
css=".view.full svg{max-height:460px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function preset(){const v=$("size").value;const c=v==="cus";["a","b","box"].forEach(id=>$(id).disabled=!c);if(!c){const p=v.split(",");$("a").value=p[0];$("b").value=p[1];$("box").value=p[2];}}
$("size").addEventListener("change",()=>{preset();render()});
const E=1e-6;
function layout(){
  const L=num("L",0.3,40,4.2)*1000,W=num("W",0.3,40,3.6)*1000;
  const a=num("a",50,3000,800),b=num("b",50,3000,800),j=num("j",0,20,2),pat=$("pat").value,start=$("start").value,sh=num("sh",-3000,3000,0);
  const px=a+j,py=b+j;const tiles=[];let full=0,cut=0,minCut=Infinity;const cuts=[];
  const tooMany=(L/px)*(W/py)>60000;
  if(pat!=="diag"){
    const off=pat==="half"?0.5:pat==="third"?1/3:0;
    // origin: centred = centre a tile or a joint on the room centre, whichever gives bigger edge cuts
    const edge=(len,p,o,t)=>{let s0=o-Math.ceil(o/p-E)*p;let left=s0+t;if(left<=E)left=t;const sr=o+Math.floor((len-o-E)/p)*p;const right=Math.min(t,len-sr);return Math.min(left,right)/t};
    let ox,oy;
    if(start==="corner"){ox=0;oy=0}else{
      const c1x=L/2-a/2,c2x=L/2-px+j/2;ox=edge(L,px,c1x,a)>=edge(L,px,c2x,a)?c1x:c2x;
      const c1y=W/2-b/2,c2y=W/2-py+j/2;oy=edge(W,py,c1y,b)>=edge(W,py,c2y,b)?c1y:c2y;}
    ox+=sh;
    const k0=Math.floor(-oy/py)-1,k1=Math.ceil((W-oy)/py)+1;
    for(let k=k0;k<=k1&&!tooMany;k++){const y0=oy+k*py,y1=y0+b;if(y1<=E||y0>=W-E)continue;
      const rowOff=(((k*off)%1)+1)%1*px;const xo=ox+rowOff;
      const i0=Math.floor(-xo/px)-1,i1=Math.ceil((L-xo)/px)+1;
      for(let i=i0;i<=i1;i++){const x0=xo+i*px,x1=x0+a;if(x1<=E||x0>=L-E)continue;
        const cx0=Math.max(0,x0),cx1=Math.min(L,x1),cy0=Math.max(0,y0),cy1=Math.min(W,y1);
        const isFull=x0>=-E&&x1<=L+E&&y0>=-E&&y1<=W+E;
        if(isFull)full++;else{cut++;const wx=cx1-cx0,wy=cy1-cy0;const fr=Math.min(wx<a-E?wx/a:1,wy<b-E?wy/b:1);if(fr<minCut){minCut=fr}
          if(cuts.length<1500)cuts.push([cx0,cy0,cx1-cx0,cy1-cy0,fr]);}
      }}
    return {L,W,a,b,j,pat,full,cut,minCut,cuts,ox,oy,px,py,off,tooMany};
  }
  // diagonal 45°: tile grid in (u,v) with u=(x+y)/√2, v=(y−x)/√2
  const s=Math.SQRT1_2,toXY=(u,v)=>[(u-v)*s,(u+v)*s];
  const cu=(L/2+W/2)*s,cv=(W/2-L/2)*s;
  let ou=start==="corner"?0:cu-a/2,ov=start==="corner"?0:cv-b/2;ou+=sh;
  const umin=0,umax=(L+W)*s,vmin=-L*s,vmax=W*s;
  const inside=p=>p[0]>=-E&&p[0]<=L+E&&p[1]>=-E&&p[1]<=W+E;
  const sat=(P)=>{const xs=P.map(p=>p[0]),ys=P.map(p=>p[1]);if(Math.max(...xs)<=E||Math.min(...xs)>=L-E||Math.max(...ys)<=E||Math.min(...ys)>=W-E)return false;
    const R=[[0,0],[L,0],[L,W],[0,W]];for(const ax of [[1,1],[-1,1]]){const pr=Q=>Q.map(q=>q[0]*ax[0]+q[1]*ax[1]);const A=pr(P),B=pr(R);if(Math.max(...A)<=Math.min(...B)+E||Math.max(...B)<=Math.min(...A)+E)return false}return true};
  const n=((umax-umin)/px)*((vmax-vmin)/py);
  if(n<120000){const i0=Math.floor((umin-ou)/px)-1,i1=Math.ceil((umax-ou)/px)+1,k0=Math.floor((vmin-ov)/py)-1,k1=Math.ceil((vmax-ov)/py)+1;
    for(let i=i0;i<=i1;i++)for(let k=k0;k<=k1;k++){const u0=ou+i*px,v0=ov+k*py;const P=[toXY(u0,v0),toXY(u0+a,v0),toXY(u0+a,v0+b),toXY(u0,v0+b)];
      if(P.every(inside)){full++;tiles.push([P,0])}else if(sat(P)){cut++;if(cuts.length<1500)cuts.push(P);}}}
  return {L,W,a,b,j,pat,full,cut,minCut:NaN,cuts,tiles,ou,ov,px,py,tooMany:n>=120000};
}
function render(){
  const g=layout(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),paper=css("--paper"),okc=css("--ok");
  $("shv").textContent=(num("sh",-3000,3000,0)>0?"+":"")+num("sh",-3000,3000,0);
  const brk=num("brk",0,50,3),box=Math.round(num("box",1,100,3)),area=g.L*g.W/1e6,tileA=g.a*g.b/1e6;
  const used=g.full+g.cut,buy=Math.ceil(used*(1+brk/100)),boxes=Math.ceil(buy/box);
  const areaWaste=g.pat==="diag"?15:g.pat==="grid"?10:12,areaMethod=Math.ceil(area/tileA*(1+areaWaste/100));
  $("oN").textContent=g.tooMany?"–":buy.toLocaleString("en-IN");$("oB").textContent=g.tooMany?"–":boxes;
  const mc=g.minCut;$("oC").textContent=Number.isFinite(mc)?Math.round(mc*100)+"% tile":g.pat==="diag"?"triangles":"none";
  $("oC").className=Number.isFinite(mc)&&mc<1/3?"bad":"";$("oA").textContent=fmt(area,2)+" m²";
  // skirting
  const skh=num("skh",0,300,100),dw=num("dw",0,40,0.9),skLen=Math.max(0,2*(g.L+g.W)/1000-dw);
  const long=Math.max(g.a,g.b),short=Math.min(g.a,g.b),strips=skh>0?Math.max(1,Math.floor(short/(skh+3))):0;
  const skTiles=skh>0?Math.ceil(skLen*1000/(long*strips)*1.05):0;
  const tt=num("t",3,30,9),grout=(g.a+g.b)/(g.a*g.b)*num("j",0,20,2)*tt*1.6*area;
  // checks
  const C=[];
  if(g.pat!=="diag"&&Number.isFinite(mc))C.push([`Smallest edge cut ${Math.round(mc*100)}% of a tile (keep above 33%)`,mc>=1/3-1e-9,mc<1/3?"":"ok"]);
  else C.push(["Diagonal: every edge tile is a triangle cut. Allow extra time and tiles",true,"info"]);
  C.push([`${g.cut} cut tiles out of ${used} (${used?Math.round(100*g.cut/used):0}%)`,g.cut/Math.max(1,used)<0.4,"warn"]);
  C.push([`Area method (+${areaWaste}%) says ${areaMethod}; tile count says ${buy}`,true,"info"]);
  if(g.pat==="diag"&&g.a!==g.b)C.push(["Diagonal layouts work best with square tiles",false,"warn"]);
  if(g.tooMany)C.push(["Too many tiles to draw and count here. Use a bigger tile or a smaller room",false]);
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&kind!=="warn"&&kind!=="info")fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?"slivers at the walls":"cuts look fine";
  // PLAN
  const sv=$("plan");sv.innerHTML="";const sc=Math.min(800/g.L,410/g.W),ox=(840-g.L*sc)/2,oy=(450-g.W*sc)/2+6;
  const X=v=>ox+v*sc,Y=v=>oy+v*sc;
  const defs=el("defs",{},sv),cp=el("clipPath",{id:"room"},defs);el("rect",{x:X(0),y:Y(0),width:g.L*sc,height:g.W*sc},cp);
  el("rect",{x:X(0),y:Y(0),width:g.L*sc,height:g.W*sc,fill:paper},sv);
  const G=el("g",{"clip-path":"url(#room)"},sv);
  if(!g.tooMany){
    if(g.pat!=="diag"){
      g.cuts.forEach(c=>el("rect",{x:X(c[0]),y:Y(c[1]),width:c[2]*sc,height:c[3]*sc,fill:c[4]<1/3?red:sun,opacity:c[4]<1/3?.45:.25},G));
      // tile outlines (joints)
      const k0=Math.floor(-g.oy/g.py)-1,k1=Math.ceil((g.W-g.oy)/g.py)+1;let d="";
      for(let k=k0;k<=k1;k++){const y0=g.oy+k*g.py;if(y0+g.b<0||y0>g.W)continue;d+=`M${X(0)} ${Y(y0)}H${X(g.L)}M${X(0)} ${Y(y0+g.b)}H${X(g.L)}`;
        const xo=g.ox+(((k*g.off)%1)+1)%1*g.px;const i0=Math.floor(-xo/g.px)-1,i1=Math.ceil((g.L-xo)/g.px)+1;
        for(let i=i0;i<=i1;i++){const x0=xo+i*g.px;if(x0+g.a<0||x0>g.L)continue;d+=`M${X(x0)} ${Y(Math.max(0,y0))}V${Y(Math.min(g.W,y0+g.b))}M${X(x0+g.a)} ${Y(Math.max(0,y0))}V${Y(Math.min(g.W,y0+g.b))}`}}
      el("path",{d,stroke:ink2,"stroke-width":sc*g.a>14?1:0.5,fill:"none",opacity:.8},G);
    }else{
      g.cuts.forEach(P=>el("polygon",{points:P.map(p=>X(p[0])+","+Y(p[1])).join(" "),fill:sun,opacity:.25,stroke:ink2,"stroke-width":0.8},G));
      g.tiles.forEach(T=>el("polygon",{points:T[0].map(p=>X(p[0])+","+Y(p[1])).join(" "),fill:"none",stroke:ink2,"stroke-width":0.8},G));
    }}
  el("rect",{x:X(0),y:Y(0),width:g.L*sc,height:g.W*sc,fill:"none",stroke:ink,"stroke-width":3},sv);
  // door on bottom-left wall
  const dws=Math.min(dw*1000,g.L);if(dws>0){el("line",{x1:X(150),y1:Y(g.W),x2:X(150+dws),y2:Y(g.W),stroke:paper,"stroke-width":4},sv);
    el("path",{d:`M${X(150)} ${Y(g.W)} L${X(150)} ${Y(g.W)+Math.min(dws*sc,40)}`,stroke:ink2,"stroke-width":1},sv);}
  el("text",{x:X(g.L/2),y:Y(0)-6,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,(g.L/1000).toFixed(2)+" m");
  el("text",{x:X(g.L)+6,y:Y(g.W/2),fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace","writing-mode":"tb"},sv,(g.W/1000).toFixed(2)+" m");
  $("planLabel").textContent=g.full+" full · "+g.cut+" cut"+(g.pat!=="diag"?" · red = slivers under ⅓":"");
  const ct=$("cnt");ct.innerHTML="";[["Full tiles",g.full],["Cut tiles",g.cut],["Laid tiles",used],["+ breakage "+brk+"%",buy],["Boxes of "+box,boxes],["Area method (+"+areaWaste+"%)",areaMethod]]
    .forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${r[0]}</td><td>${g.tooMany?"–":r[1]}</td>`;ct.appendChild(tr)});
  const rows=[["Floor tiles",buy+" tiles · "+boxes+" boxes",fmt(buy*tileA,2)+" m² of tile for "+fmt(area,2)+" m² of floor"],
    ["Skirting",skh>0?fmt(skLen,2)+" m · "+skTiles+" tiles":"none",skh>0?strips+" strips of "+skh+" mm per tile, +5%":""],
    ["Grout",fmt(grout,2)+" kg",(g.a)+"+"+(g.b)+" ÷ ("+g.a+"×"+g.b+") × "+num("j",0,20,2)+" × "+tt+" × 1.6 × area"],
    ["Joint pitch",g.px+" × "+g.py+" mm","tile + joint"]];
  const tb=$("tbl");tb.innerHTML="";rows.forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td>`;tb.appendChild(tr)});
}
preset();
""")
