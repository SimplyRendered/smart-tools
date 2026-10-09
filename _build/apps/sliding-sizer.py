APP = dict(
slug="sliding-sizer", title="Sliding Door & Window Sizer", h1="Sliding Door & Window",
sub="Enter the opening and pick the system. Get every shutter and glass size, the clear opening, the glass weight on the rollers and the pocket wall you need. Slide it open to see it work.",
meta=[("Sheet","T-15"),("Method","Shutter + interlock"),("Units","mm"),("By","@smart_tools_every_week")],
source="Shutter = (inner frame width + joints × interlock) ÷ shutters. Glass weight = area × thickness × 2.5 kg/m² per mm. Door clear width ≥ 815 mm per ADA 2010 §404.2.3. Safety glass in doors per UK Approved Doc K / IS 16231-4. Profile deductions vary by maker: check the system catalogue before ordering.",
inputs="""
      <label for="kind">Use
        <select id="kind"><option value="win">Window</option><option value="door" selected>Door</option></select>
      </label>
      <label for="sys">System
        <select id="sys">
          <option value="2-2">2 shutters · 2 tracks</option>
          <option value="3-3">3 shutters · 3 tracks</option>
          <option value="4-2" selected>4 shutters · 2 tracks (centre opens)</option>
          <option value="p1">Pocket · 1 leaf</option>
          <option value="p2">Pocket · 2 leaves (bi-parting)</option>
        </select>
      </label>
      <div class="row">
        <label for="W">Opening width mm<input id="W" type="number" step="10" value="2400"></label>
        <label for="H">Opening height mm<input id="H" type="number" step="10" value="2100"></label>
      </div>
      <label for="op">Slide open % <span id="opv" class="time" style="font-size:18px"></span><input id="op" type="range" min="0" max="100" step="1" value="60"></label>
      <div class="row">
        <label for="fr">Outer frame mm<input id="fr" type="number" step="5" value="60"></label>
        <label for="ov">Interlock overlap mm<input id="ov" type="number" step="5" value="40"></label>
      </div>
      <div class="row">
        <label for="st">Shutter stile mm<input id="st" type="number" step="5" value="70"></label>
        <label for="hd">Height deduction mm<input id="hd" type="number" step="5" value="40"></label>
      </div>
      <div class="row">
        <label for="tg">Glass mm<input id="tg" type="number" step="1" value="10"></label>
        <label for="cap">Rollers carry kg<input id="cap" type="number" step="5" value="80"></label>
      </div>
      <p class="note">Interlock: how much neighbouring shutters overlap where they meet (25–50 mm on most aluminium and uPVC systems). Height deduction: track and roller allowance between the inner frame and the shutter. Glass bite into the stile is taken as 10 mm.</p>
""",
right="""
      <div class="readout">
        <div><b>Shutter size</b><span id="oS" class="hi">–</span></div>
        <div><b>Clear opening</b><span id="oO">–</span></div>
        <div><b>Glass / shutter</b><span id="oG">–</span></div>
        <div><b>Glass weight</b><span id="oKg">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Elevation + plan <span id="elLabel"></span></h2><svg id="elev" viewBox="0 0 840 470" role="img" aria-label="Sliding system elevation and plan"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
        <div class="view"><h2>Cutting list <span>per opening</span></h2><div class="tablewrap"><table><thead><tr><th>Item</th><th>No.</th><th>Size (mm)</th></tr></thead><tbody id="cut"></tbody></table></div></div>
      </div>
""",
css=".view.full svg{max-height:470px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
$("kind").addEventListener("change",()=>{const d=$("kind").value==="door";$("tg").value=d?10:5;$("cap").value=d?80:40;$("fr").value=d?60:50;$("st").value=d?70:50;
  $("W").value=d?2400:1500;$("H").value=d?2100:1200;$("sys").value=d?"4-2":"2-2";render()});
function calc(){
  const sys=$("sys").value,door=$("kind").value==="door";
  const W=num("W",300,12000,2400),H=num("H",300,6000,2100),fr=num("fr",0,200,60),ov=num("ov",0,200,40),st=num("st",20,200,70),hd=num("hd",0,300,40),tg=num("tg",3,30,10),cap=num("cap",5,1000,80),op=num("op",0,100,60)/100;
  const Wi=Math.max(50,W-2*fr),Hi=Math.max(50,H-2*fr);
  const n={"2-2":2,"3-3":3,"4-2":4,p1:1,p2:2}[sys],tracks={"2-2":2,"3-3":3,"4-2":2,p1:1,p2:1}[sys];
  const joints=sys==="p1"?1:sys==="p2"?2:n-1; // pocket: lap into the jamb stop (and meeting stiles)
  const s=(Wi+joints*ov)/n,hs=Math.max(10,Hi-hd);
  const gw=Math.max(0,s-2*(st-10)),gh=Math.max(0,hs-2*(st-10)),ga=gw*gh/1e6,kg=ga*tg*2.5;
  const open=sys==="4-2"?Math.max(0,Wi-2*s):sys[0]==="p"?Wi:Math.max(0,Wi-s);
  const pocket=sys==="p1"?s+50:sys==="p2"?s+50:0; // pocket depth each side incl. 50 mm stop
  return {sys,door,W,H,fr,ov,st,hd,tg,cap,op,Wi,Hi,n,tracks,joints,s,hs,gw,gh,ga,kg,open,pocket};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),paper=css("--paper"),sheet=css("--sheet");
  $("opv").textContent=Math.round(c.op*100)+"%";
  $("oS").textContent=Math.round(c.s)+" × "+Math.round(c.hs);$("oO").textContent=Math.round(c.open)+" mm";
  $("oG").textContent=Math.round(c.gw)+" × "+Math.round(c.gh);$("oKg").textContent=fmt(c.kg,1)+" kg";$("oKg").className=c.kg>c.cap?"bad":"";
  const pct=100*c.open/c.Wi;
  const C=[[`Glass ${fmt(c.kg,1)} kg per shutter ≤ ${c.cap} kg roller rating`,c.kg<=c.cap],
    [`Clear opening ${Math.round(c.open)} mm, ${Math.round(pct)}% of the width`,true,"info"]];
  if(c.door)C.push([`Clear width ${Math.round(c.open)} mm ≥ 815 mm for a wheelchair (ADA)`,c.open>=815,"warn"]);
  const ratio=c.hs/c.s;C.push([`Shutter height : width = ${fmt(ratio,1)} : 1${ratio>3?". Tall, narrow shutters can rack and bind":""}`,ratio<=3,"warn"]);
  if(c.door)C.push(["Doors: toughened or laminated safety glass",true,"info"]);
  if(c.pocket)C.push([`Pocket wall: ${Math.round(c.pocket)} mm clear cavity ${c.sys==="p2"?"each side":"beside the opening"}, wall ≥ ${Math.round(c.tg+2*25+50)} mm thick`,true,"info"]);
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // DRAWING
  const sv=$("elev");sv.innerHTML="";const totW=c.W+2*c.pocket,sc=Math.min(780/totW,300/c.H),ox=(840-totW*sc)/2+c.pocket*sc,oy=24;
  const X=v=>ox+(v+c.fr)*sc,Y=v=>oy+(v+c.fr)*sc; // inner-frame coordinates
  if(c.pocket){[[-c.pocket-c.fr,c.pocket],[c.Wi+c.fr,c.pocket]].slice(0,c.sys==="p2"?2:1).forEach(([x,w])=>{el("rect",{x:ox+(x+c.fr)*sc,y:oy,width:w*sc,height:c.H*sc,fill:rule,opacity:.5,stroke:ink2,"stroke-dasharray":"5 4"},sv)});}
  el("rect",{x:ox,y:oy,width:c.W*sc,height:c.H*sc,fill:sheet,stroke:ink,"stroke-width":2},sv);
  el("rect",{x:X(0),y:Y(0),width:c.Wi*sc,height:c.Hi*sc,fill:paper,stroke:ink2},sv);
  // shutter positions
  const step=c.s-c.ov,pos=[],trk=[];
  for(let i=0;i<c.n;i++){let x=i*step,t=0;
    if(c.sys==="2-2"){t=i===0?1:0;if(i===1)x-=step*c.op}
    else if(c.sys==="3-3"){t=c.n-1-i;x-=i*step*c.op}
    else if(c.sys==="4-2"){t=(i===0||i===3)?1:0;if(i===1)x-=step*c.op;if(i===2)x+=step*c.op}
    else if(c.sys==="p1"){x=-c.ov-(c.s-c.ov)*c.op;t=0}
    else{x=i===0?-c.ov-(c.s-c.ov)*c.op:c.Wi/2+(c.s-c.ov)*c.op;t=0}
    pos.push(x);trk.push(t)}
  const order=[...Array(c.n).keys()].sort((a,b)=>trk[b]-trk[a]);
  const sy=c.hd/2;
  order.forEach(i=>{const x=pos[i];el("rect",{x:X(x),y:Y(sy),width:c.s*sc,height:c.hs*sc,fill:sheet,stroke:ink,"stroke-width":1.5},sv);
    el("rect",{x:X(x+c.st-10),y:Y(sy+c.st-10),width:c.gw*sc,height:c.gh*sc,fill:blue,opacity:trk[i]?.16:.28,stroke:blue,"stroke-width":.8},sv);
    el("text",{x:X(x+c.s/2),y:Y(sy+c.hs/2)+4,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,String.fromCharCode(65+i));});
  // clear opening dimension
  if(c.op>0.99||c.sys==="p1"||c.sys==="p2"){}
  el("line",{x1:X(0),y1:oy+c.H*sc+16,x2:X(c.Wi),y2:oy+c.H*sc+16,stroke:ink2},sv);
  el("text",{x:X(c.Wi/2),y:oy+c.H*sc+30,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"opening "+c.W+" × "+c.H+" · inner frame "+Math.round(c.Wi)+" × "+Math.round(c.Hi));
  // plan strip
  const py=oy+c.H*sc+56,tg=14;
  el("rect",{x:ox,y:py-6,width:c.W*sc,height:(c.tracks*tg+12),fill:"none",stroke:ink,"stroke-width":1.5},sv);
  for(let t=0;t<c.tracks;t++)el("line",{x1:X(0),y1:py+t*tg+tg/2,x2:X(c.Wi),y2:py+t*tg+tg/2,stroke:rule,"stroke-dasharray":"2 3"},sv);
  if(c.pocket){el("line",{x1:ox-c.pocket*sc,y1:py+tg/2,x2:ox,y2:py+tg/2,stroke:rule,"stroke-dasharray":"2 3"},sv);if(c.sys==="p2")el("line",{x1:ox+c.W*sc,y1:py+tg/2,x2:ox+(c.W+c.pocket)*sc,y2:py+tg/2,stroke:rule,"stroke-dasharray":"2 3"},sv);}
  for(let i=0;i<c.n;i++)el("rect",{x:X(pos[i]),y:py+(c.tracks-1-trk[i])*tg+3,width:c.s*sc,height:tg-6,fill:i%2?blue:css("--sun"),opacity:.8},sv);
  el("text",{x:ox,y:py+c.tracks*tg+24,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"PLAN · "+c.tracks+" track"+(c.tracks>1?"s":"")+(c.pocket?" · dashed = wall pocket":""));
  $("elLabel").textContent=c.n+" × "+Math.round(c.s)+" mm shutters · drag 'Slide open'";
  const rows=[["Shutter",c.n,Math.round(c.s)+" × "+Math.round(c.hs)],["Glass",c.n,Math.round(c.gw)+" × "+Math.round(c.gh)+" × "+c.tg],
    ["Stiles",2*c.n,Math.round(c.hs)],["Rails",2*c.n,Math.round(c.s-2*c.st)],
    ["Frame head + sill",2,Math.round(c.W)],["Frame jambs",2,Math.round(c.H)],["All glass",c.n,fmt(c.ga*c.n,2)+" m², "+fmt(c.kg*c.n,0)+" kg"]];
  const tb=$("cut");tb.innerHTML="";rows.forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td>`;tb.appendChild(tr)});
}
""")
