APP = dict(
slug="brick-bond", title="Brick Bond Planner", h1="Brick Bond Planner",
sub="Pick the brick, the bond and the wall size. It sets out every course with headers, stretchers, queen closers and bats, finds any straight joints and counts the bricks, on a live elevation and plan.",
meta=[("Sheet","T-57"),("Method","Quarter-brick set-out"),("Units","mm"),("By","@smart_tools_every_week")],
source="Set out in quarter-brick modules: ¼ brick = (length + joint) ÷ 4, header = 2 modules, queen closer = 1, three-quarter bat = 3, stretcher = 4 (works when brick width = (length − joint) ÷ 2, true of IS 1077 230 × 110 and 190 × 90 bricks and UK 215 × 102.5). English and Flemish bond put a queen closer after the quoin header so vertical joints break by a quarter brick; stretcher bond laps by half a brick, header bond starts alternate courses with a three-quarter bat (standard brickwork practice, e.g. W. B. McKay, Building Construction Vol. 1; Barry, The Construction of Buildings). A straight joint is a vertical joint that lines up in two courses one above the other. Brick count from wall volume; add wastage.",
inputs="""
      <label for="BR">Brick
        <select id="BR">
          <option value="230,110,70,10" selected>IS 1077 traditional 230 × 110 × 70</option>
          <option value="190,90,90,10">IS 1077 modular 190 × 90 × 90</option>
          <option value="215,102.5,65,10">UK 215 × 102.5 × 65</option>
          <option value="c">Custom</option>
        </select>
      </label>
      <div class="row">
        <label for="BL">Brick length<input id="BL" type="number" step="5" value="230"></label>
        <label for="BW">Brick width<input id="BW" type="number" step="5" value="110"></label>
      </div>
      <div class="row">
        <label for="BH">Brick height<input id="BH" type="number" step="5" value="70"></label>
        <label for="J">Joint<input id="J" type="number" step="1" value="10"></label>
      </div>
      <label for="BD">Bond
        <select id="BD">
          <option value="english" selected>English bond (one brick wall)</option>
          <option value="flemish">Flemish bond (one brick wall)</option>
          <option value="stretcher">Stretcher bond (half brick wall)</option>
          <option value="header">Header bond (one brick wall)</option>
        </select>
      </label>
      <div class="row">
        <label for="WL">Wall length mm<input id="WL" type="number" step="10" value="2400"></label>
        <label for="WH">Wall height mm<input id="WH" type="number" step="10" value="1000"></label>
      </div>
      <div class="row">
        <label for="QC">Queen closers at the ends
          <select id="QC"><option value="1" selected>Yes</option><option value="0">No</option></select>
        </label>
        <label for="WS">Wastage %<input id="WS" type="number" step="1" value="5"></label>
      </div>
      <p class="note">Both ends of the wall are square (stopped) ends. The length is set out to the nearest quarter brick. A length that is not a whole number of half bricks leaves a cut bat at the right end. Turn queen closers off to see the straight joints you get when every course starts with a full brick.</p>
""",
right="""
      <div class="readout">
        <div><b>Straight joints</b><span id="oJ" class="hi">–</span></div>
        <div><b>Lap</b><span id="oL">–</span></div>
        <div><b>Cut pieces</b><span id="oK">–</span></div>
        <div><b>Bricks</b><span id="oN">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Elevation <span id="elL"></span></h2><svg id="ev" viewBox="0 0 600 340" role="img" aria-label="Brick wall elevation with every course set out"></svg></div>
        <div class="view full"><h2>Plan of two courses, left end <span id="plL"></span></h2><svg id="pl" viewBox="0 0 600 244" role="img" aria-label="Plan of the first two courses at the left end"></svg></div>
      </div>
      <div class="data"><h2>Every bond for this wall <span id="dtL"></span></h2><div class="tablewrap"><table><thead><tr><th>Bond</th><th>Wall</th><th>Straight joints</th><th>Lap</th><th>Cut pieces</th><th>Bricks per m²</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css=".view.full svg{max-height:380px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
$("BR").addEventListener("input",()=>{const v=$("BR").value;if(v!=="c"){const [a,b,c,d]=v.split(",");$("BL").value=a;$("BW").value=b;$("BH").value=c;$("J").value=d}render()});
const U={S:4,H:2,Q:1,T:3,B:2};
const NAMES={english:"English",flemish:"Flemish",stretcher:"Stretcher",header:"Header"};
function pattern(bond,odd,qc){ // returns {start,cycle,end}; odd = second course
  const Hs=qc?["H","Q"]:["H"],He=qc?["Q","H"]:["H"];
  if(bond==="english")return odd?{start:[],cycle:["S"],end:[]}:{start:Hs,cycle:["H"],end:He};
  if(bond==="flemish")return odd?{start:["S"],cycle:["H","S"],end:[]}:{start:Hs,cycle:["S","H"],end:He};
  if(bond==="stretcher")return odd?{start:["B"],cycle:["S"],end:[]}:{start:[],cycle:["S"],end:[]};
  return odd?{start:qc?["T"]:["H"],cycle:["H"],end:qc?["T"]:["H"]}:{start:[],cycle:["H"],end:[]}; // header
}
function course(bond,odd,qc,n){
  const p=pattern(bond,odd,qc),len=a=>a.reduce((s,u)=>s+U[u],0),out=[];let r=n;
  for(const u of p.start){if(U[u]<=r){out.push({u,w:U[u]});r-=U[u]}}
  const eL=len(p.end);let i=0,guard=0;
  while(r>0&&guard++<2000){
    if(r===eL){p.end.forEach(u=>out.push({u,w:U[u]}));r=0;break}
    const u=p.cycle[i%p.cycle.length];
    if(r>=U[u]+eL){out.push({u,w:U[u]});r-=U[u];i++;continue}
    const cut=r-eL;
    if(cut>0){out.push({u:"X",w:cut});r-=cut}
    else{out.push({u:"X",w:r});r=0}
  }
  return out;
}
function joints(c){const j=[];let x=0;for(let i=0;i<c.length-1;i++){x+=c[i].w;j.push(x)}return j}
function analyse(bond,qc,n,nc){
  const A=course(bond,false,qc,n),B=course(bond,true,qc,n),jA=joints(A),jB=joints(B);
  const same=jA.filter(x=>jB.includes(x));
  let lap=Infinity;for(const a of jA)for(const b of jB)lap=Math.min(lap,Math.abs(a-b));
  if(!jA.length||!jB.length)lap=NaN;
  const cuts=c=>c.filter(u=>u.u!=="S"&&u.u!=="H").length;
  const nA=Math.ceil(nc/2),nB=Math.floor(nc/2);
  return {A,B,jA,jB,same,lapQ:lap,straight:same.length*Math.max(0,nc-1),cuts:cuts(A)*nA+cuts(B)*nB};
}
function calc(){
  const p={L:num("BL",50,500,230),W:num("BW",20,300,110),H:num("BH",20,300,70),j:num("J",0,30,10),
    bond:NAMES[$("BD").value]?$("BD").value:"english",qc:$("QC").value!=="0",wl:num("WL",300,12000,2400),wh:num("WH",50,6000,1000),ws:num("WS",0,50,5)};
  p.q=(p.L+p.j)/4;p.n=Math.max(4,Math.round((p.wl+p.j)/p.q));p.len=p.n*p.q-p.j;
  p.nc=Math.max(1,Math.min(80,Math.round((p.wh+p.j)/(p.H+p.j))));p.ht=p.nc*(p.H+p.j)-p.j;
  Object.assign(p,analyse(p.bond,p.qc,p.n,p.nc));
  p.lap=p.lapQ*p.q;
  p.half=p.bond==="stretcher";p.thick=p.half?p.W:p.L;
  p.perM2=(p.half?1:2)*1e6/((p.L+p.j)*(p.H+p.j));
  p.bricks=Math.ceil(p.perM2*(p.len+p.j)*(p.ht+p.j)/1e6*(1+p.ws/100));
  p.modOK=Math.abs(p.W-(p.L-p.j)/2)<=2;
  return p;
}
const FILL={S:"#B5532F",H:"#8E3B22",Q:"#E0A33A",T:"#D07A2E",B:"#D07A2E",X:"#E0A33A"};
const LBL={Q:"Qc",T:"¾",B:"½",X:"bat"};
function render(){
  const p=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),ok=css("--ok"),bad=css("--bad");
  const M="IBM Plex Mono, monospace";
  $("oJ").textContent=p.straight;$("oJ").className=p.straight?"bad":"ok";
  $("oL").textContent=Number.isFinite(p.lap)?Math.round(p.lap)+" mm":"–";
  $("oK").textContent=p.cuts;$("oN").textContent=p.bricks.toLocaleString("en-IN");
  // elevation
  const sv=$("ev");sv.innerHTML="";const show=Math.min(p.nc,14),k=Math.min(560/p.len,260/(show*(p.H+p.j))),ox=(600-p.len*k)/2,base=300;
  el("line",{x1:ox-10,y1:base+1,x2:ox+p.len*k+10,y2:base+1,stroke:ink2,"stroke-width":2},sv);
  for(let c=0;c<show;c++){const crs=c%2?p.B:p.A,y=base-(c+1)*(p.H+p.j)*k+p.j*k;let x=0;
    for(const u of crs){const w=u.w*p.q-p.j,X=ox+x*p.q*k;
      el("rect",{x:X,y,width:Math.max(0.5,w*k),height:p.H*k,fill:FILL[u.u],stroke:"#2A1A12","stroke-width":.6},sv);
      if(LBL[u.u]&&w*k>14&&p.H*k>11)el("text",{x:X+w*k/2,y:y+p.H*k/2+4,"text-anchor":"middle",fill:"#1A1A1A","font-size":Math.min(12,p.H*k*0.7),"font-family":M},sv,LBL[u.u]);
      x+=u.w}
    if(c<show-1)for(const s of p.same){const X=ox+(s*p.q-p.j/2)*k;el("line",{x1:X,y1:y-p.j*k-p.H*k,x2:X,y2:y+p.H*k,stroke:"#FF3B30","stroke-width":3},sv)}}
  el("text",{x:300,y:328,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":M},sv,`${Math.round(p.len)} mm = ${p.n} quarter bricks · ${p.nc} courses, ${Math.round(p.ht)} mm`);
  $("elL").textContent=(p.nc>show?`bottom ${show} of ${p.nc} courses · `:"")+(p.straight?"red = straight joint":"joints all broken");
  // plan of first two courses, left end
  const s2=$("pl");s2.innerHTML="";const nq=Math.min(p.n,28),k2=Math.min(540/(nq*p.q),(70)/p.thick),px=30;
  [[p.A,"course 1",20],[p.B,"course 2",120]].forEach(([crs,lab,py])=>{
    el("text",{x:px,y:py+8,fill:ink2,"font-size":12,"font-family":M},s2,lab);let x=0;const y0=py+16;
    for(const u of crs){if(x>=nq)break;const w=Math.min(u.w,nq-x)*p.q-p.j,X=px+x*p.q*k2;
      const full=!p.half&&["H","Q","T"].includes(u.u);
      if(full||p.half){el("rect",{x:X,y:y0,width:Math.max(.5,w*k2),height:(p.half?p.W:p.L)*k2,fill:FILL[u.u],stroke:"#2A1A12","stroke-width":.6},s2)}
      else{el("rect",{x:X,y:y0,width:Math.max(.5,w*k2),height:p.W*k2,fill:FILL[u.u],stroke:"#2A1A12","stroke-width":.6},s2);
        el("rect",{x:X,y:y0+(p.W+p.j)*k2,width:Math.max(.5,w*k2),height:p.W*k2,fill:FILL[u.u],stroke:"#2A1A12","stroke-width":.6},s2)}
      x+=u.w}});
  el("text",{x:px,y:236,fill:ink2,"font-size":12,"font-family":M},s2,`face at top · wall ${Math.round(p.thick)} mm thick`);
  $("plL").textContent=p.modOK?"":"brick width ≠ (length − joint) ÷ 2: bond will not close";
  // table
  $("tb").innerHTML=Object.keys(NAMES).map(b=>{const a=analyse(b,p.qc,p.n,p.nc),half=b==="stretcher",pm=(half?1:2)*1e6/((p.L+p.j)*(p.H+p.j));
    return `<tr${b===p.bond?' class="now"':''}><td>${NAMES[b]}</td><td>${Math.round(half?p.W:p.L)} mm</td><td class="${a.straight?'bad':'ok'}">${a.straight}</td><td>${Number.isFinite(a.lapQ)?Math.round(a.lapQ*p.q)+' mm':'–'}</td><td>${a.cuts}</td><td>${fmt(pm,1)}</td></tr>`}).join("");
  $("dtL").textContent=`${Math.round(p.len)} × ${Math.round(p.ht)} mm · queen closers ${p.qc?"on":"off"}`;
}
""")
