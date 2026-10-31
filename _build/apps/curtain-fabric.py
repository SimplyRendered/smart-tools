APP = dict(
slug="curtain-fabric", title="Curtain Fabric Calculator", h1="Curtain Fabric Calculator",
sub="Enter the track, the drop, the heading and the fabric roll. Get the widths, the cut drop matched to the pattern repeat and the metres to order, with a live elevation and a cutting plan.",
meta=[("Sheet","T-41"),("Method","Workroom widths × cut drops"),("Units","mm, m"),("By","@smart_tools_every_week")],
source="Workroom method: flat width = (track share + return + overlap) × fullness + side hems; widths = flat width ÷ usable roll width, rounded up (to half widths if allowed); cut drop = finished drop + hem and heading allowance, rounded up to whole pattern repeats; fabric = cut drops × cut drop + one repeat to place the pattern (see Direct Fabrics 'Fabric calculation for curtains', and makers' calculators such as Morris & Co. and Jane Clayton). Fullness by heading and all allowances are typical values: ask your curtain maker for theirs.",
inputs="""
      <div class="row">
        <label for="tw">Track width mm<input id="tw" type="number" step="50" value="2400"></label>
        <label for="dr">Finished drop mm<input id="dr" type="number" step="50" value="2600"></label>
      </div>
      <div class="row">
        <label for="np">Curtains
          <select id="np"><option value="2" selected>Pair (2)</option><option value="1">Single</option></select>
        </label>
        <label for="nw">Same windows<input id="nw" type="number" step="1" value="1"></label>
      </div>
      <label for="hd">Heading
        <select id="hd">
          <option value="2">Eyelet · ×2.0</option>
          <option value="2.5" selected>Pencil pleat · ×2.5</option>
          <option value="2.25">Pinch (triple) pleat · ×2.25</option>
          <option value="2.0">Wave · ×2.0</option>
          <option value="1.5">Tab top · ×1.5</option>
          <option value="c">Custom</option>
        </select>
      </label>
      <div class="row">
        <label for="fu">Fullness ×<input id="fu" type="number" step="0.05" value="2.5"></label>
        <label for="rw">Roll width mm<input id="rw" type="number" step="10" value="1370"></label>
      </div>
      <div class="row">
        <label for="rp">Pattern repeat mm<input id="rp" type="number" step="10" value="320"></label>
        <label for="al">Hem + heading mm<input id="al" type="number" step="10" value="300"></label>
      </div>
      <div class="row">
        <label for="rt">Return per curtain mm<input id="rt" type="number" step="10" value="80"></label>
        <label for="ov">Centre overlap mm<input id="ov" type="number" step="10" value="50"></label>
      </div>
      <div class="row">
        <label for="sh">Side hem, each side mm<input id="sh" type="number" step="5" value="40"></label>
        <label for="sm">Seams per width mm<input id="sm" type="number" step="5" value="30"></label>
      </div>
      <label for="hw">Rounding
        <select id="hw"><option value="0.5" selected>Half widths allowed</option><option value="1">Whole widths only</option></select>
      </label>
      <p class="note">Track width: usually the window plus 150 to 300 mm each side so the curtains stack off the glass. Return: the bit that wraps from the track end back to the wall. Overlap: each leading edge passes the centre by this much. Set the repeat to 0 for plain fabric. Lining uses the same widths, cut 150 mm shorter, with no repeat. Quick rule: track × fullness ÷ roll width, rounded up, × (drop + 300 mm).</p>
""",
right="""
      <div class="readout">
        <div><b>Fabric to order</b><span id="oF" class="hi">–</span></div>
        <div><b>Widths</b><span id="oW">–</span></div>
        <div><b>Cut drop</b><span id="oC">–</span></div>
        <div><b>Quick rule says</b><span id="oQ">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Elevation <span id="elL"></span></h2><svg id="el" viewBox="0 0 420 380" role="img" aria-label="Window elevation with the curtains drawn"></svg></div>
        <div class="view"><h2>Flat curtain <span id="flL"></span></h2><svg id="fl" viewBox="0 0 420 380" role="img" aria-label="One curtain laid flat with its widths"></svg></div>
        <div class="view full"><h2>Cutting plan <span id="cpL"></span></h2><svg id="cp" viewBox="0 0 580 170" role="img" aria-label="Fabric roll with every cut drop"></svg></div>
      </div>
      <div class="data"><h2>Fabric by fullness <span id="dtL"></span></h2><div class="tablewrap"><table><thead><tr><th>Fullness</th><th>Widths per curtain</th><th>Drops to cut</th><th>Fabric</th><th>Lining</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css=".view.full svg{max-height:220px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
$("hd").addEventListener("input",()=>{const v=$("hd").value;if(v!=="c")$("fu").value=v;render()});
function solve(p,fu){
  const n=p.np,share=p.tw/n,cov=share+p.rt+(n===2?p.ov:0),flat=cov*fu+2*p.sh,use=Math.max(100,p.rw-p.sm);
  const raw=flat/use,per=Math.ceil(raw/p.hw-1e-9)*p.hw,tot=per*n*p.nw,drops=Math.ceil(tot-1e-9);
  const cdRaw=p.dr+p.al,cd=p.rp>0?Math.ceil(cdRaw/p.rp-1e-9)*p.rp:cdRaw;
  const fab=(drops*cd+(p.rp>0?p.rp:0))/1000,lin=drops*(p.dr+Math.max(0,p.al-150))/1000;
  return {cov,flat,use,raw,per,tot,drops,cdRaw,cd,fab:Math.ceil(fab*10-1e-9)/10,lin:Math.ceil(lin*10-1e-9)/10,waste:cd-cdRaw};
}
function calc(){
  const p={tw:num("tw",300,20000,2400),dr:num("dr",300,10000,2600),np:$("np").value==="1"?1:2,nw:Math.round(num("nw",1,200,1)),fu:num("fu",1,4,2.5),
    rw:num("rw",300,3500,1370),rp:num("rp",0,2000,320),al:num("al",0,1000,300),rt:num("rt",0,500,80),ov:num("ov",0,500,50),sh:num("sh",0,200,40),sm:num("sm",0,200,30),hw:$("hw").value==="1"?1:0.5};
  p.s=solve(p,p.fu);
  const qw=Math.ceil(p.tw*p.fu/p.rw-1e-9);p.quick=Math.ceil(qw*(p.dr+300)/100-1e-9)/10*p.nw;p.qw=qw;
  return p;
}
function render(){
  const p=calc(),s=p.s,ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun"),ok=css("--ok");
  const M="IBM Plex Mono, monospace";
  $("oF").textContent=fmt(s.fab,1)+" m";$("oW").textContent=`${s.per} × ${p.np}${p.nw>1?" × "+p.nw:""}`;
  $("oC").textContent=fmt(s.cd/1000,2)+" m";$("oQ").textContent=fmt(p.quick,1)+" m";
  // elevation
  const sv=$("el");sv.innerHTML="";const ww=Math.max(p.tw-400,p.tw*0.7),sc=Math.min(360/p.tw,300/(p.dr+200));
  const cx=210,ty=40,TW=p.tw*sc,DR=p.dr*sc,WW=ww*sc;
  el("rect",{x:cx-WW/2,y:ty+18,width:WW,height:Math.min(DR-30,DR*0.8),fill:blue,opacity:.15,stroke:ink2,"stroke-width":1.5},sv);
  el("line",{x1:cx,y1:ty+18,x2:cx,y2:ty+18+Math.min(DR-30,DR*0.8),stroke:ink2},sv);
  el("line",{x1:cx-TW/2,y1:ty,x2:cx+TW/2,y2:ty,stroke:ink,"stroke-width":4},sv);
  const open=0.32; // curtains drawn part open
  const folds=Math.max(3,Math.round(s.per*9));
  for(let c=0;c<p.np;c++){
    const cw=(p.np===2?TW/2:TW)*(1-open*(p.np===2?1:0.6)),x0=p.np===2?(c===0?cx-TW/2:cx+TW/2-cw):cx-TW/2;
    el("rect",{x:x0,y:ty,width:cw,height:DR,fill:sun,opacity:.35,stroke:ink,"stroke-width":1.5},sv);
    for(let i=1;i<folds;i++){const x=x0+cw*i/folds;el("line",{x1:x,y1:ty+4,x2:x,y2:ty+DR,stroke:ink2,"stroke-width":i%2?1:.5,opacity:.8},sv)}
  }
  el("line",{x1:cx-TW/2,y1:ty+DR+22,x2:cx+TW/2,y2:ty+DR+22,stroke:ink2},sv);
  el("text",{x:cx,y:ty+DR+40,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":M},sv,`track ${Math.round(p.tw)} mm`);
  el("line",{x1:cx+TW/2+14,y1:ty,x2:cx+TW/2+14,y2:ty+DR,stroke:ink2},sv);
  el("text",{x:Math.min(412,cx+TW/2+20),y:ty+DR/2,fill:ink,"font-size":13,"font-family":M,"text-anchor":cx+TW/2+20>360?"end":"start"},sv,`${Math.round(p.dr)}`);
  $("elL").textContent=`${p.np===2?"pair":"single"} · ×${fmt(p.fu,2)} fullness`;
  // flat curtain
  const s2=$("fl");s2.innerHTML="";const fw=s.per*p.rw,fsc=Math.min(360/Math.max(fw,1),260/s.cd),FX=30,FY=40;
  for(let i=0;i<Math.ceil(s.per);i++){const part=Math.min(1,s.per-i),w=p.rw*part*fsc;
    el("rect",{x:FX+i*p.rw*fsc,y:FY,width:w,height:s.cd*fsc,fill:i%2?blue:sun,opacity:.3,stroke:ink,"stroke-width":1.2},s2);
    el("text",{x:FX+i*p.rw*fsc+w/2,y:FY+s.cd*fsc/2,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":M},s2,part<1?"½ width":"width "+(i+1))}
  if(p.rp>0){for(let y=p.rp;y<s.cd;y+=p.rp)el("line",{x1:FX,y1:FY+y*fsc,x2:FX+fw*fsc,y2:FY+y*fsc,stroke:ink2,"stroke-dasharray":"3 4",opacity:.6},s2)}
  el("rect",{x:FX,y:FY,width:s.flat*fsc,height:s.cd*fsc,fill:"none",stroke:red,"stroke-width":2.5},s2);
  el("text",{x:FX,y:FY-12,fill:red,"font-size":13,"font-family":M},s2,`flat width needed ${Math.round(s.flat)} mm`);
  el("text",{x:FX,y:FY+s.cd*fsc+22,fill:ink2,"font-size":12,"font-family":M},s2,`(${Math.round(s.cov)} covered × ${fmt(p.fu,2)} + ${Math.round(2*p.sh)} hems)`);
  el("text",{x:FX,y:FY+s.cd*fsc+40,fill:ink2,"font-size":12,"font-family":M},s2,`÷ ${Math.round(s.use)} usable = ${fmt(s.raw,2)} → ${s.per} widths`);
  $("flL").textContent="one curtain";
  // cutting plan
  const s3=$("cp");s3.innerHTML="";const tot=s.fab*1000,csc=520/Math.max(tot,1),CY=40,CH=70;
  el("rect",{x:30,y:CY,width:tot*csc,height:CH,fill:"none",stroke:ink,"stroke-width":1.5},s3);
  for(let i=0;i<s.drops;i++){const x=30+i*s.cd*csc;
    el("rect",{x,y:CY,width:s.cdRaw*csc,height:CH,fill:i%2?blue:sun,opacity:.35,stroke:ink,"stroke-width":1},s3);
    if(s.waste>0)el("rect",{x:x+s.cdRaw*csc,y:CY,width:s.waste*csc,height:CH,fill:red,opacity:.35},s3);
    if(s.cd*csc>26)el("text",{x:x+s.cdRaw*csc/2,y:CY+CH/2+5,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":M},s3,String(i+1))}
  if(p.rp>0)el("rect",{x:30+s.drops*s.cd*csc,y:CY,width:Math.max(0,tot-s.drops*s.cd)*csc,height:CH,fill:red,opacity:.2},s3);
  el("text",{x:30,y:CY-12,fill:ink,"font-size":13,"font-family":M},s3,`${s.drops} drops × ${fmt(s.cd/1000,2)} m${p.rp>0?" + 1 repeat":""} = ${fmt(s.fab,1)} m`);
  el("text",{x:30,y:CY+CH+26,fill:red,"font-size":12,"font-family":M},s3,s.waste>0||p.rp>0?`red = pattern loss ${Math.round(s.waste)} mm per drop`:"plain fabric: no repeat loss");
  $("cpL").textContent=`${fmt(s.tot,1)} widths in all`;
  // table
  const F=[1.5,1.8,2,2.25,2.5,3];if(!F.some(f=>Math.abs(f-p.fu)<1e-6))F.push(p.fu);F.sort((a,b)=>a-b);
  $("tb").innerHTML=F.map(f=>{const r=solve(p,f);return `<tr${Math.abs(f-p.fu)<1e-6?' class="now"':''}><td>×${fmt(f,2)}</td><td>${r.per}</td><td>${r.drops}</td><td>${fmt(r.fab,1)} m</td><td>${fmt(r.lin,1)} m</td></tr>`}).join("");
  $("dtL").textContent=`quick rule (track × fullness ÷ roll, × drop + 300): ${fmt(p.quick,1)} m`;
}
""")
