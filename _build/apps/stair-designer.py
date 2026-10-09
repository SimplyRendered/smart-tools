APP = dict(
slug="stair-designer", title="Staircase Designer", h1="Staircase Designer",
sub="Enter the floor height. Get risers, treads, flights and the slab opening for headroom, checked against NBC 2016 limits.",
meta=[("Sheet","T-04"),("Code","NBC 2016 Pt 3/4"),("Units","mm"),("By","@smart_tools_every_week")],
source="Limits per NBC 2016 (stairs). Bylaws vary by city; confirm with your local authority.",
inputs="""
      <label for="use">Building use
        <select id="use">
          <option value="res">Residential (R ≤ 190, T ≥ 250)</option>
          <option value="com">Office / commercial (R ≤ 175, T ≥ 275)</option>
          <option value="asm">Assembly / educational (R ≤ 150, T ≥ 300)</option>
          <option value="cus">Custom limits</option>
        </select>
      </label>
      <div class="row">
        <label for="rmax">Max riser<input id="rmax" type="number" value="190"></label>
        <label for="tmin">Min tread<input id="tmin" type="number" value="250"></label>
      </div>
      <div class="row">
        <label for="H">Floor to floor<input id="H" type="number" step="10" value="3150"></label>
        <label for="T">Tread (going)<input id="T" type="number" step="5" value="270"></label>
      </div>
      <label for="type">Stair type
        <select id="type"><option value="dog">Dog-legged (two flights, half landing)</option><option value="straight">Straight run</option></select>
      </label>
      <div class="row">
        <label for="W">Flight width<input id="W" type="number" step="50" value="1000"></label>
        <label for="slab">Slab + finish<input id="slab" type="number" step="10" value="150"></label>
      </div>
      <div class="row">
        <label for="hr">Min headroom<input id="hr" type="number" step="50" value="2100"></label>
        <label for="mx">Max risers / flight<input id="mx" type="number" value="12"></label>
      </div>
      <p class="note">NBC 2016 gives 190 mm max riser and 250 mm min tread for residential stairs, a comfortable 2R + T of 600–650 mm, and at least 2.1 m headroom. Many designers aim for 2.2 m.</p>
""",
right="""
      <div class="readout">
        <div><b>Risers</b><span id="oN" class="hi">–</span></div>
        <div><b>Riser height</b><span id="oR">–</span></div>
        <div><b>2R + T</b><span id="oB">–</span></div>
        <div><b>Stair length</b><span id="oL">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Section <span id="secLabel"></span></h2><svg id="sec" viewBox="0 0 420 330" role="img" aria-label="Stair section"></svg></div>
        <div class="view"><h2>Plan <span id="planLabel"></span></h2><svg id="plan" viewBox="0 0 420 330" role="img" aria-label="Stair plan"></svg></div>
      </div>
      <div class="data">
        <h2>Code checks <span id="sum"></span></h2>
        <ul class="checks" id="checks"></ul>
      </div>
      <div class="data" style="border-top:1px solid var(--rule)">
        <h2>Step schedule <span>level of each tread nosing above the lower floor</span></h2>
        <div class="tablewrap"><table><thead><tr><th>Step</th><th>Flight</th><th>Height (mm)</th><th>Going from start (mm)</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
js=r"""
const PRESETS={res:[190,250],com:[175,275],asm:[150,300]};
$("use").addEventListener("change",()=>{const p=PRESETS[$("use").value];if(p){$("rmax").value=p[0];$("tmin").value=p[1];if(+$("T").value<p[1])$("T").value=p[1]}});
function stair(){
  const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
  const H=num("H",300,20000,3150),T=num("T",150,600,270),rmax=num("rmax",100,250,190),tmin=num("tmin",150,600,250),W=num("W",500,5000,1000),slab=num("slab",0,1000,150),hr=num("hr",1500,4000,2100),mx=Math.round(num("mx",3,30,12)),type=$("type").value;
  const n=Math.ceil(H/rmax),R=H/n;
  let flights;
  if(type==="dog"){const a=Math.ceil(n/2);flights=[a,n-a];}
  else{const k=Math.ceil(n/mx);flights=[];let left=n;for(let i=0;i<k;i++){const f=Math.ceil(left/(k-i));flights.push(f);left-=f;}}
  const treads=flights.map(f=>f-1);
  const goingStraight=treads.reduce((s,t)=>s+t,0)*T+(flights.length-1)*W;
  const length=type==="dog"?Math.max(...treads)*T+W:goingStraight;
  // headroom (straight): nosing k at height kR, ceiling soffit at H-slab
  const kcrit=Math.floor((H-slab-hr)/R);
  const opening=type==="straight"?Math.max(0,(n-1-kcrit))*T:null;
  return {H,T,R,n,rmax,tmin,W,slab,hr,mx,type,flights,treads,length,opening,kcrit,blondel:2*R+T};
}
function render(){
  const s=stair(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue");
  $("oN").textContent=s.n+" ("+s.flights.join(" + ")+")";$("oR").textContent=fmt(s.R,1)+" mm";$("oB").textContent=fmt(s.blondel,0)+" mm";$("oL").textContent=(s.length/1000).toFixed(2)+" m";
  // checks
  const C=[["Riser "+fmt(s.R,1)+" mm ≤ "+s.rmax+" mm",s.R<=s.rmax+1e-9],["Tread "+s.T+" mm ≥ "+s.tmin+" mm",s.T>=s.tmin],
    ["2R + T = "+fmt(s.blondel,0)+" mm (comfort range 600–650)",s.blondel>=600&&s.blondel<=650,"warn"],
    ["Largest flight "+Math.max(...s.flights)+" risers ≤ "+s.mx,Math.max(...s.flights)<=s.mx],
    ["Flight width "+s.W+" mm (NBC: ≥ 900 single dwelling, ≥ 1000 apartments)",s.W>=900,"warn"]];
  if(s.type==="straight")C.push(["Slab opening ≥ "+(s.opening/1000).toFixed(2)+" m long keeps "+s.hr+" mm headroom",true,"info"]);
  else C.push(["Headroom under the upper flight and landing beam: check in section",true,"info"]);
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,ok,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":ok?"ok":kind==="warn"?"warn":"bad";if(!ok&&kind!=="warn"&&kind!=="info")fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":ok?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all limits met";
  // section (straight run to scale; dog-legged shown unfolded)
  const sv=$("sec");sv.innerHTML="";
  let x=0,y=0,step=0;const rows=[];let d="";
  s.flights.forEach((f,fi)=>{for(let i=0;i<f;i++){if(i>0||fi>0){} y+=s.R;step++;rows.push([step,fi+1,y,x]);if(i<f-1){x+=s.T}}
    if(fi<s.flights.length-1){x+=s.W}});
  const xTop=x;const sc=Math.min(380/Math.max(xTop+500,1),260/(s.H+300));const ox=20,oy=300;const X=v=>ox+v*sc,Y=v=>oy-v*sc;
  d=`M${X(-300)} ${Y(0)} L${X(0)} ${Y(0)}`;let px=0,py=0;
  rows.forEach(r=>{d+=` L${X(r[3])} ${Y(r[2])}`;const nx=rows.find(q=>q[0]===r[0]+1);const tx=nx?nx[3]:r[3]+300;d+=` L${X(tx)} ${Y(r[2])}`});
  el("line",{x1:0,y1:Y(0),x2:420,y2:Y(0),stroke:ink,"stroke-width":2},sv);
  el("path",{d,fill:"none",stroke:ink,"stroke-width":2},sv);
  const soffit=s.H-s.slab;
  if(s.type==="straight"){
    const firstLow=rows.find(r=>soffit-r[2]<s.hr&&r[0]<s.n);const xOpen=firstLow?firstLow[3]:xTop;
    s.opening=xTop-xOpen;
    el("rect",{x:0,y:Y(s.H),width:Math.max(0,X(xOpen)),height:s.slab*sc,fill:rule,stroke:ink,"stroke-width":1},sv);
    el("rect",{x:X(xTop),y:Y(s.H),width:420,height:s.slab*sc,fill:rule,stroke:ink,"stroke-width":1},sv);
    const under=rows.filter(r=>r[3]<xOpen);const lastOk=under[under.length-1];
    if(lastOk){el("line",{x1:X(lastOk[3])+2,y1:Y(lastOk[2]),x2:X(lastOk[3])+2,y2:Y(soffit),stroke:red,"stroke-width":1.5,"stroke-dasharray":"4 3"},sv);
      el("text",{x:X(lastOk[3])+7,y:(Y(lastOk[2])+Y(soffit))/2,fill:red,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,(soffit-lastOk[2]).toFixed(0)+" headroom");}
    el("line",{x1:X(xOpen),y1:Y(s.H)-14,x2:X(xTop),y2:Y(s.H)-14,stroke:blue,"stroke-width":1},sv);
    el("text",{x:(X(xOpen)+X(xTop))/2,y:Y(s.H)-18,"text-anchor":"middle",fill:blue,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"opening "+(s.opening/1000).toFixed(2)+" m");
  }else{el("rect",{x:X(xTop),y:Y(s.H),width:420,height:s.slab*sc,fill:rule,stroke:ink,"stroke-width":1},sv);}
  el("text",{x:6,y:Y(s.H)-24,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"FFL +"+s.H);
  el("text",{x:6,y:Y(0)+16,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"FFL ±0");
  // refresh opening check text now that it is exact
  if(s.type==="straight"){const li=[...ul.children].pop();li.firstChild.textContent="Slab opening ≥ "+(s.opening/1000).toFixed(2)+" m long keeps "+s.hr+" mm headroom";}
  $("secLabel").textContent=s.type==="dog"?"flights unfolded":"to scale";
  // plan
  const pv=$("plan");pv.innerHTML="";
  if(s.type==="dog"){const L=Math.max(...s.treads)*s.T,gap=100,Wt=2*s.W+gap,Lt=L+s.W;const k=Math.min(380/Wt,290/Lt);const px=(420-Wt*k)/2,py=20;
    const P=(xx,yy)=>[px+xx*k,py+yy*k];
    el("rect",{x:px,y:py,width:Wt*k,height:Lt*k,fill:"none",stroke:ink,"stroke-width":2},pv);
    el("rect",{x:px,y:py,width:Wt*k,height:s.W*k,fill:css("--paper"),stroke:ink,"stroke-width":1},pv);
    el("text",{x:px+Wt*k/2,y:py+s.W*k/2+4,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pv,"LANDING "+s.W+" × "+Wt);
    [[0,s.treads[0]],[s.W+gap,s.treads[1]]].forEach(([ox2,t],fi)=>{for(let i=0;i<=t;i++){const yy=s.W+i*s.T;el("line",{x1:px+ox2*k,y1:py+yy*k,x2:px+(ox2+s.W)*k,y2:py+yy*k,stroke:i===0?ink:rule,"stroke-width":1},pv)}
      el("rect",{x:px+ox2*k,y:py+s.W*k,width:s.W*k,height:t*s.T*k,fill:"none",stroke:ink,"stroke-width":1.5},pv);
      const cx=px+(ox2+s.W/2)*k;const a=fi===0?[py+Lt*k-6,py+s.W*k+8]:[py+s.W*k+8,py+(s.W+t*s.T)*k-6];
      el("line",{x1:cx,y1:a[0],x2:cx,y2:a[1],stroke:red,"stroke-width":1.5},pv);el("circle",{cx,cy:a[0],r:3,fill:red},pv);
      el("text",{x:cx,y:fi===0?py+Lt*k-12:py+(s.W+t*s.T)*k+14,"text-anchor":"middle",fill:red,"font-size":11,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif"},pv,fi===0?"UP":"")});
    $("planLabel").textContent=`${(Wt/1000).toFixed(2)} × ${(Lt/1000).toFixed(2)} m stair hall`;
  }else{const L=s.length,k=Math.min(390/L,200/s.W);const px=15,py=(330-s.W*k)/2;
    el("rect",{x:px,y:py,width:L*k,height:s.W*k,fill:"none",stroke:ink,"stroke-width":2},pv);
    let xx=0;s.flights.forEach((f,fi)=>{for(let i=0;i<f-1;i++){xx+=s.T;el("line",{x1:px+xx*k,y1:py,x2:px+xx*k,y2:py+s.W*k,stroke:rule,"stroke-width":1},pv)}if(fi<s.flights.length-1){el("rect",{x:px+xx*k,y:py,width:s.W*k,height:s.W*k,fill:css("--paper"),stroke:ink},pv);xx+=s.W}});
    el("line",{x1:px+6,y1:py+s.W*k/2,x2:px+L*k-8,y2:py+s.W*k/2,stroke:red,"stroke-width":1.5},pv);el("text",{x:px+8,y:py-8,fill:red,"font-size":11,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif"},pv,"UP →");
    $("planLabel").textContent=`${(L/1000).toFixed(2)} × ${(s.W/1000).toFixed(2)} m`;}
  const tb=$("tbl");tb.innerHTML="";rows.forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${r[0]}</td><td>${r[1]}</td><td>${r[2].toFixed(0)}</td><td>${r[3].toFixed(0)}</td>`;tb.appendChild(tr)});
}
""")
