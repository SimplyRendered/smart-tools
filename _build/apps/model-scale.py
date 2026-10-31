APP = dict(
slug="model-scale", title="Model Scale & Board", h1="Model Scale & Board",
sub="Pick the model scale and the board thicknesses you can buy. Get every wall, slab and floor height in model millimetres, the board (or stack of two) that matches best, the base size and how many sheets to buy.",
meta=[("Sheet","T-45"),("Method","Real size ÷ scale"),("Units","mm, m"),("By","@smart_tools_every_week")],
source="Model size = real size ÷ scale denominator (first principles). Best board = the single board, or stack of two, closest to the scaled thickness. Sheets = board area needed ÷ (sheet area × yield), walls counted once per floor, slabs = footprint per floor. Typical mount / foam board sizes are editable; the human figure is 1,750 mm tall.",
inputs="""
      <div class="row">
        <label for="ssel">Scale
          <select id="ssel"><option value="20">1:20</option><option value="50">1:50</option><option value="100" selected>1:100</option><option value="200">1:200</option><option value="500">1:500</option><option value="c">Custom</option></select>
        </label>
        <label for="N">1 : N<input id="N" type="number" step="10" value="100"></label>
      </div>
      <label for="boards">Boards you can buy, mm<input id="boards" type="text" value="1, 2, 3, 5"></label>
      <div class="row">
        <label for="we">External wall mm<input id="we" type="number" step="5" value="230"></label>
        <label for="wi">Internal wall mm<input id="wi" type="number" step="5" value="115"></label>
      </div>
      <div class="row">
        <label for="sl">Slab mm<input id="sl" type="number" step="5" value="150"></label>
        <label for="fh">Floor to floor mm<input id="fh" type="number" step="50" value="3000"></label>
      </div>
      <div class="row">
        <label for="nf">Floors<input id="nf" type="number" step="1" value="2"></label>
        <label for="wl">Wall length per floor m<input id="wl" type="number" step="1" value="60"></label>
      </div>
      <div class="row">
        <label for="bl">Building length m<input id="bl" type="number" step="0.5" value="12"></label>
        <label for="bw">Building width m<input id="bw" type="number" step="0.5" value="9"></label>
      </div>
      <div class="row">
        <label for="pl">Site length m<input id="pl" type="number" step="1" value="24"></label>
        <label for="pw">Site width m<input id="pw" type="number" step="1" value="15"></label>
      </div>
      <div class="row">
        <label for="shl">Sheet length mm<input id="shl" type="number" step="10" value="841"></label>
        <label for="shw">Sheet width mm<input id="shw" type="number" step="10" value="594"></label>
      </div>
      <p class="note">Sheet 841 × 594 mm is A1 board; foam board often comes 762 × 508 mm. A 70% yield allows for offcuts and windows cut out.</p>
""",
right="""
      <div class="readout">
        <div><b>External wall</b><span id="oW" class="hi">–</span></div>
        <div><b>Best board</b><span id="oB">–</span></div>
        <div><b>Model height</b><span id="oH">–</span></div>
        <div><b>Sheets to buy</b><span id="oS">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Model section <span id="sLabel"></span></h2><svg id="sec" viewBox="0 0 580 320" role="img" aria-label="Model section with boards and a scale figure"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Board fit <span>scaled vs board</span></h2><svg id="fit" viewBox="0 0 300 230" role="img" aria-label="Scaled thickness compared with the best board"></svg></div>
        <div class="view"><h2>Model base <span id="bLabel"></span></h2><svg id="base" viewBox="0 0 300 230" role="img" aria-label="Model base with building footprint"></svg></div>
      </div>
      <div class="data"><h2>Cutting list <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Element</th><th>Real</th><th>At scale</th><th>Best board</th><th>Error</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
$("ssel").addEventListener("change",()=>{const v=$("ssel").value;if(v!=="c")$("N").value=v;render()});
$("N").addEventListener("input",()=>{$("ssel").value=["20","50","100","200","500"].includes($("N").value)?$("N").value:"c"});
function boards(){const b=($("boards").value||"").split(/[ ,;]+/).map(parseFloat).filter(v=>Number.isFinite(v)&&v>0&&v<=100).slice(0,12);return b.length?b:[1,2,3,5]}
function best(t,B){let r={v:B[0],lab:fmt(B[0],B[0]%1?1:0)+" mm",e:Infinity};
  const cand=B.map(b=>[b,fmt(b,b%1?1:0)+" mm"]);B.forEach((a,i)=>B.forEach((b,j)=>{if(j>=i)cand.push([a+b,fmt(a,a%1?1:0)+" + "+fmt(b,b%1?1:0)+" mm"])}));
  cand.forEach(([v,lab])=>{const e=Math.abs(v-t);if(e<r.e-1e-9||(Math.abs(e-r.e)<1e-9&&!lab.includes("+")))r={v,lab,e}});r.err=t>0?(r.v/t-1)*100:0;return r}
function calc(){
  const N=num("N",1,5000,100),B=boards(),we=num("we",10,2000,230),wi=num("wi",10,2000,115),sl=num("sl",10,2000,150),fh=num("fh",500,20000,3000),nf=Math.round(num("nf",1,60,2));
  const wl=num("wl",0,10000,60),bl=num("bl",1,1000,12),bw=num("bw",1,1000,9),pl=Math.max(num("pl",1,5000,24),bl),pw=Math.max(num("pw",1,5000,15),bw),shl=num("shl",50,3000,841),shw=num("shw",50,3000,594);
  const E=[["External wall",we,"t"],["Internal wall",wi,"t"],["Slab",sl,"t"],["Floor to floor",fh,"h"],["Door height",2100,"h"],["Person",1750,"h"]].map(([n,r,k])=>{const m=r/N;return {n,r,m,k,b:k==="t"?best(m,B):null}});
  const H=fh*nf/N,area=(wl*1000*fh*nf+bl*bw*1e6*nf)/(N*N),sheets=Math.ceil(area/(shl*shw*0.7)),baseL=pl*1000/N+40,baseW=pw*1000/N+40;
  return {N,B,E,we:E[0],H,area,sheets,baseL,baseW,pl,pw,bl,bw,fh,nf,sl,shl,shw};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),ok=css("--ok"),F="IBM Plex Mono, monospace";
  const w=c.we;$("oW").textContent=fmt(w.m,w.m<10?2:1)+" mm";$("oB").textContent=w.b.lab;$("oB").className=Math.abs(w.b.err)>25?"bad":"";
  $("oH").textContent=fmt(c.H,c.H<100?1:0)+" mm";$("oS").textContent=c.sheets;
  // section: building width at model scale, fitted to the view
  const sv=$("sec");sv.innerHTML="";
  const Wmm=c.bw*1000/c.N,Hmm=c.H+c.sl/c.N,k=Math.min(420/Math.max(Wmm,1e-6),215/Math.max(Hmm,1e-6)),ox=70,oy=285,X=x=>ox+x*k,Y=y=>oy-y*k;
  el("line",{x1:30,y1:oy,x2:560,y2:oy,stroke:ink,"stroke-width":1.4},sv);
  const bt=w.b.v,tt=c.E[2].b.v,wt=Math.max(1.5,bt*k),st=Math.max(1.5,tt*k);
  for(let f=0;f<c.nf;f++){const y0=f*c.fh/c.N;
    el("rect",{x:fmt(X(0),1),y:fmt(Y(y0+c.fh/c.N),1),width:fmt(wt,1),height:fmt(c.fh/c.N*k,1),fill:blue,opacity:.7},sv);
    el("rect",{x:fmt(X(Wmm)-wt,1),y:fmt(Y(y0+c.fh/c.N),1),width:fmt(wt,1),height:fmt(c.fh/c.N*k,1),fill:blue,opacity:.7},sv);
    el("rect",{x:fmt(X(0),1),y:fmt(Y(y0+c.fh/c.N)-st,1),width:fmt(Wmm*k,1),height:fmt(st,1),fill:red,opacity:.75},sv);}
  // true wall thickness ghost
  el("rect",{x:fmt(X(0),1),y:fmt(Y(c.H),1),width:fmt(Math.max(1,w.m*k),1),height:fmt(c.H*k,1),fill:"none",stroke:ink,"stroke-dasharray":"3 3"},sv);
  // person at scale
  const ph=1750/c.N*k,px=X(Wmm*0.55);el("circle",{cx:fmt(px,1),cy:fmt(oy-ph*0.92,1),r:fmt(Math.max(1,ph*0.07),1),fill:"none",stroke:ink,"stroke-width":1.2},sv);
  el("line",{x1:fmt(px,1),y1:fmt(oy-ph*0.85,1),x2:fmt(px,1),y2:fmt(oy-ph*0.45,1),stroke:ink,"stroke-width":1.2},sv);
  el("line",{x1:fmt(px,1),y1:fmt(oy-ph*0.45,1),x2:fmt(px-ph*0.1,1),y2:oy,stroke:ink,"stroke-width":1.2},sv);
  el("line",{x1:fmt(px,1),y1:fmt(oy-ph*0.45,1),x2:fmt(px+ph*0.1,1),y2:oy,stroke:ink,"stroke-width":1.2},sv);
  el("text",{x:fmt(px+8,1),y:fmt(oy-ph*0.5,1),fill:ink2,"font-size":13,"font-family":F},sv,fmt(1750/c.N,1)+" mm figure");
  el("line",{x1:fmt(X(Wmm)+18,1),y1:oy,x2:fmt(X(Wmm)+18,1),y2:fmt(Y(c.H),1),stroke:ink2},sv);
  el("text",{x:fmt(X(Wmm)+24,1),y:fmt(Y(c.H/2),1),fill:ink,"font-size":14,"font-family":F},sv,fmt(c.H,c.H<100?1:0)+" mm");
  el("text",{x:30,y:22,fill:blue,"font-size":14,"font-family":F},sv,"walls: "+w.b.lab+" board for "+fmt(w.m,2)+" mm");
  el("text",{x:30,y:40,fill:red,"font-size":14,"font-family":F},sv,"slabs: "+c.E[2].b.lab+" for "+fmt(c.E[2].m,2)+" mm");
  el("text",{x:30,y:312,fill:ink2,"font-size":12,"font-family":F},sv,"dashed = true wall thickness at 1:"+c.N+" · width "+fmt(Wmm,0)+" mm");
  $("sLabel").textContent="1:"+c.N+" · "+c.nf+" floor"+(c.nf>1?"s":"");
  // fit bars
  const fv=$("fit");fv.innerHTML="";const T=c.E.filter(e=>e.b),mx=Math.max(...T.map(e=>Math.max(e.m,e.b.v)),1e-6),bk=150/mx;
  T.forEach((e,i)=>{const y=24+i*68;el("text",{x:10,y,fill:ink,"font-size":12,"font-family":F},fv,e.n+" · "+fmt(e.m,2)+" mm");
    el("rect",{x:10,y:y+8,width:fmt(Math.max(1,e.m*bk),1),height:14,fill:ink2,opacity:.5},fv);
    el("rect",{x:10,y:y+26,width:fmt(Math.max(1,e.b.v*bk),1),height:14,fill:Math.abs(e.b.err)>25?red:ok,opacity:.85},fv);
    el("text",{x:fmt(16+Math.max(e.m,e.b.v)*bk,1),y:y+38,fill:Math.abs(e.b.err)>25?red:ok,"font-size":11,"font-family":F},fv,e.b.lab+" ("+(e.b.err>=0?"+":"")+fmt(e.b.err,0)+"%)")});
  // base
  const bv=$("base");bv.innerHTML="";const bs=Math.min(270/c.baseL,190/c.baseW),bx=(300-c.baseL*bs)/2,by=(205-c.baseW*bs)/2;
  el("rect",{x:fmt(bx,1),y:fmt(by,1),width:fmt(c.baseL*bs,1),height:fmt(c.baseW*bs,1),fill:"none",stroke:ink,"stroke-width":1.6},bv);
  el("rect",{x:fmt(bx+20*bs,1),y:fmt(by+20*bs,1),width:fmt(c.pl*1000/c.N*bs,1),height:fmt(c.pw*1000/c.N*bs,1),fill:rule,opacity:.6},bv);
  el("rect",{x:fmt(bx+20*bs+(c.pl-c.bl)/2*1000/c.N*bs,1),y:fmt(by+20*bs+(c.pw-c.bw)/2*1000/c.N*bs,1),width:fmt(c.bl*1000/c.N*bs,1),height:fmt(c.bw*1000/c.N*bs,1),fill:blue,opacity:.7},bv);
  el("text",{x:150,y:222,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},bv,fmt(c.baseL,0)+" × "+fmt(c.baseW,0)+" mm incl. 20 mm border");
  $("bLabel").textContent=c.baseL>c.shl||c.baseW>c.shw?"bigger than one sheet":"fits one sheet";
  // table
  $("tb").innerHTML=c.E.map(e=>`<tr${e===w?' class="now"':""}><td>${e.n}</td><td>${Math.round(e.r)} mm</td><td>${fmt(e.m,e.m<10?2:1)} mm</td><td>${e.b?e.b.lab:"cut to "+fmt(e.m,1)+" mm"}</td><td class="${e.b&&Math.abs(e.b.err)>25?"bad":""}">${e.b?(e.b.err>=0?"+":"")+fmt(e.b.err,0)+"%":"–"}</td></tr>`).join("")+
    `<tr><td>Board area</td><td colspan="2">${fmt(c.area/1e6,3)} m²</td><td>${c.sheets} sheet${c.sheets>1?"s":""} ${Math.round(c.shl)} × ${Math.round(c.shw)}</td><td>70% yield</td></tr>`;
  $("dLabel").textContent="boards: "+c.B.join(", ")+" mm";
}
""")
