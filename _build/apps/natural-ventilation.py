APP = dict(
slug="natural-ventilation", title="Natural Ventilation: Wind & Stack", h1="Natural Ventilation",
sub="Enter the room, the two openings, the wind and the temperatures. Get the airflow from wind and from the stack effect, the air changes per hour, and whether it meets the ventilation rate for the room's use.",
meta=[("Sheet","T-28"),("Method","Wind + stack"),("Units","m, m², L/s"),("By","@smart_tools_every_week")],
source="Wind: Q = Cd·A·V, Cd 0.6 at 90° falling to 0.3 at 45° (ASHRAE, via CED Engineering). Stack: Q = Cd·A·√(2·g·h·(Ti−To)/Ti), Cd 0.65 (ASHRAE). Two openings combine as 1/A² = 1/A₁² + 1/A₂². Wind + stack: Q = √(Qw² + Qs²) (Awbi, CIBSE). Required rates: 2024 IMC Table 403.3.1.1 (office 5 cfm/person + 0.06 cfm/ft², classroom 10 cfm/person + 0.12 cfm/ft²) and §403.3.2.1 (dwelling 0.03 cfm/ft² + 7.5 cfm × (bedrooms + 1)). Wind speed is the speed at the window, not the weather-station value. A design estimate, not a CFD result.",
inputs="""
      <div class="row">
        <label for="L">Room length m<input id="L" type="number" step="0.1" value="5"></label>
        <label for="W">Room width m<input id="W" type="number" step="0.1" value="4"></label>
      </div>
      <label for="H">Ceiling height m<input id="H" type="number" step="0.1" value="3"></label>
      <div class="row">
        <label for="ai">Inlet area m²<input id="ai" type="number" step="0.05" value="1.2"></label>
        <label for="ao">Outlet area m²<input id="ao" type="number" step="0.05" value="0.8"></label>
      </div>
      <label for="hs">Height between the two openings m <span id="hsv" class="time" style="font-size:18px"></span><input id="hs" type="range" min="0" max="2.4" step="0.1" value="1.8"></label>
      <div class="row">
        <label for="V">Wind at window m/s<input id="V" type="number" step="0.1" value="1.5"></label>
        <label for="ang">Wind angle ° <span id="angv" class="time" style="font-size:18px"></span><input id="ang" type="range" min="45" max="90" step="5" value="90"></label>
      </div>
      <div class="row">
        <label for="Ti">Inside °C<input id="Ti" type="number" step="0.5" value="30"></label>
        <label for="To">Outside °C<input id="To" type="number" step="0.5" value="26"></label>
      </div>
      <label for="use">Room use
        <select id="use"><option value="dw" selected>Dwelling (bedroom, living)</option><option value="of">Office</option><option value="cl">Classroom</option></select>
      </label>
      <label for="occ" id="occl">Bedrooms in home<input id="occ" type="number" step="1" value="2"></label>
      <p class="note">Openings are the free (openable) areas, not the window size. The stack height is the vertical distance between the centres of the inlet and the outlet. Wind speed is measured at the window; city streets are calmer than the weather report.</p>
""",
right="""
      <div class="readout">
        <div><b>Airflow</b><span id="oQ" class="hi">–</span></div>
        <div><b>Air changes</b><span id="oA">–</span></div>
        <div><b>Needed</b><span id="oR">–</span></div>
        <div><b>Effective area</b><span id="oE">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Section <span id="secL"></span></h2><svg id="sec" viewBox="0 0 440 340" role="img" aria-label="Section through the room showing airflow"></svg></div>
        <div class="view"><h2>Plan <span id="plL"></span></h2><svg id="plan" viewBox="0 0 440 340" role="img" aria-label="Plan of the room with the wind direction"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
        <div class="view"><h2>Wind sensitivity <span>same room</span></h2><div class="tablewrap"><table><thead><tr><th>Wind m/s</th><th>Wind L/s</th><th>Stack L/s</th><th>ACH</th><th></th></tr></thead><tbody id="tb"></tbody></table></div></div>
      </div>
""",
css=".view svg{max-height:340px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const G=9.81,CFM=0.4719474,CFMFT2=5.0800; // cfm -> L/s ; cfm/ft2 -> L/s per m2
function flows(c,V){
  const Ae=1/Math.sqrt(1/(c.ai*c.ai)+1/(c.ao*c.ao));
  const Cdw=0.3+0.3*(c.ang-45)/45,Qw=Cdw*Ae*V;
  const dT=c.Ti-c.To,Tref=(dT>=0?c.Ti:c.To)+273.15,Qs=0.65*Ae*Math.sqrt(2*G*c.hs*Math.abs(dT)/Tref);
  const Q=Math.sqrt(Qw*Qw+Qs*Qs);
  return {Ae,Cdw,Qw:Qw*1000,Qs:Qs*1000,Q:Q*1000,ach:Q*3600/c.vol,dT};
}
function calc(){
  const L=num("L",1,30,5),W=num("W",1,30,4),H=num("H",2,8,3),ai=num("ai",0.02,30,1.2),ao=num("ao",0.02,30,0.8);
  const hs=Math.min(num("hs",0,2.4,1.8),H-0.4),V=num("V",0,15,1.5),ang=num("ang",45,90,90),Ti=num("Ti",-10,50,30),To=num("To",-10,50,26);
  const use=$("use").value,occ=Math.round(num("occ",1,use==="dw"?8:200,use==="dw"?2:20));
  const vol=L*W*H,area=L*W;
  const c={L,W,H,ai,ao,hs,V,ang,Ti,To,use,occ,vol,area};
  Object.assign(c,flows(c,V));
  const ft2=area*10.7639;
  let cfm=use==="dw"?0.03*ft2+7.5*(occ+1):use==="of"?5*occ+0.06*ft2:10*occ+0.12*ft2;
  c.req=cfm*CFM; c.reqACH=c.req/1000*3600/vol; c.ratio=c.req>0?c.Q/c.req:0;
  return c;
}
$("use").addEventListener("change",()=>{const u=$("use").value;$("occl").firstChild.textContent=u==="dw"?"Bedrooms in home":"People in room";$("occ").value=u==="dw"?2:u==="of"?6:30;render()});
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),okc=css("--ok"),bad=css("--bad");
  $("hsv").textContent=fmt(c.hs,1)+" m";$("angv").textContent=Math.round(c.ang)+"°";
  $("oQ").textContent=fmt(c.Q,0)+" L/s";$("oA").textContent=fmt(c.ach,1)+" /h";$("oR").textContent=fmt(c.req,0)+" L/s";$("oE").textContent=fmt(c.Ae,2)+" m²";
  $("oQ").className=c.ratio>=1?"hi":"bad";
  const small=Math.min(c.ai,c.ao),big=Math.max(c.ai,c.ao);
  const C=[[`Airflow ${fmt(c.Q,0)} L/s ≥ ${fmt(c.req,0)} L/s needed (${fmt(c.reqACH,1)} air changes/h)`,c.ratio>=1]];
  const calm=flows(c,0);
  C.push([`Calm day (no wind): stack alone gives ${fmt(calm.Q,0)} L/s, ${fmt(calm.ach,1)} /h`,calm.Q>=c.req,"warn"]);
  C.push([`Effective area ${fmt(c.Ae,2)} m² is ${Math.round(100*c.Ae/small)}% of the smaller opening${big>2*small?". Enlarging the larger one gains little":""}`,big<=2*small,"warn"]);
  if(c.dT<=0)C.push([`Outside is ${c.dT===0?"as warm as":"warmer than"} inside: no stack lift, air only moves with the wind`,false,"warn"]);
  if(c.hs<0.5)C.push(["Openings almost level: little stack effect. Put the outlet high",false,"warn"]);
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?"too little air":"meets the rate";
  // SECTION
  const sv=$("sec");sv.innerHTML="";const sc=Math.min(340/c.L,230/c.H),rw=c.L*sc,rh=c.H*sc,ox=(440-rw)/2,oy=36;
  const Y=m=>oy+rh-m*sc; // height m -> y
  el("rect",{x:ox,y:oy,width:rw,height:rh,fill:sheet,stroke:ink,"stroke-width":2.5},sv);
  el("line",{x1:ox-20,y1:oy+rh,x2:ox+rw+20,y2:oy+rh,stroke:ink,"stroke-width":3},sv);
  const y1=(c.H-c.hs)/2,y2=y1+c.hs,hin=Math.min(c.H*0.45,Math.max(0.12,c.ai/1.2)),hout=Math.min(c.H*0.45,Math.max(0.12,c.ao/1.2));
  const win=(x,yc,h,col)=>el("rect",{x:x-3,y:Y(yc+h/2),width:6,height:Math.max(3,h*sc),fill:col,stroke:ink,"stroke-width":1},sv);
  win(ox,y1,hin,blue);win(ox+rw,y2,hout,red);
  const lw=Math.max(2,Math.min(26,c.Q/ 70));
  const mx=ox+rw/2;
  const path=`M ${ox-44} ${Y(y1)} L ${ox+6} ${Y(y1)} C ${mx} ${Y(y1)}, ${mx} ${Y(y2)}, ${ox+rw-6} ${Y(y2)} L ${ox+rw+44} ${Y(y2)}`;
  el("path",{d:path,fill:"none",stroke:blue,"stroke-width":lw,opacity:.45,"stroke-linecap":"round"},sv);
  el("path",{d:path,fill:"none",stroke:ink,"stroke-width":1.2,"stroke-dasharray":"6 5"},sv);
  el("polygon",{points:`${ox+rw+50},${Y(y2)} ${ox+rw+36},${Y(y2)-7} ${ox+rw+36},${Y(y2)+7}`,fill:ink},sv);
  el("polygon",{points:`${ox-30},${Y(y1)} ${ox-44},${Y(y1)-7} ${ox-44},${Y(y1)+7}`,fill:ink},sv);
  // height dimension
  const dx=ox+rw*0.2;el("line",{x1:dx,y1:Y(y1),x2:dx,y2:Y(y2),stroke:ink2,"stroke-dasharray":"3 3"},sv);
  el("text",{x:dx+6,y:(Y(y1)+Y(y2))/2+4,fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"h "+fmt(c.hs,1)+" m");
  el("text",{x:ox,y:oy-12,fill:blue,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"IN "+fmt(c.ai,2)+" m²");
  el("text",{x:ox+rw,y:oy-12,fill:red,"text-anchor":"end","font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"OUT "+fmt(c.ao,2)+" m²");
  el("text",{x:mx,y:oy+rh+22,fill:ink2,"text-anchor":"middle","font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,fmt(c.L,1)+" m × "+fmt(c.H,1)+" m · "+fmt(c.vol,0)+" m³");
  if(c.dT>0)for(let i=0;i<3;i++){const x=ox+rw*(0.62+i*0.12);el("path",{d:`M ${x} ${oy+rh-12} L ${x} ${oy+14}`,stroke:red,"stroke-width":1.5,opacity:.5,"stroke-dasharray":"2 5"},sv);}
  $("secL").textContent=fmt(c.Qw,0)+" wind + "+fmt(c.Qs,0)+" stack L/s";
  // PLAN
  const pv=$("plan");pv.innerHTML="";const ps=Math.min(260/c.L,200/c.W),pw=c.L*ps,ph=c.W*ps,px=(440-pw)/2+10,py=(340-ph)/2;
  el("rect",{x:px,y:py,width:pw,height:ph,fill:sheet,stroke:ink,"stroke-width":2.5},pv);
  const wl=Math.min(ph*0.6,Math.max(10,Math.sqrt(c.ai)*ps*0.9)),wl2=Math.min(ph*0.6,Math.max(10,Math.sqrt(c.ao)*ps*0.9));
  el("rect",{x:px-3,y:py+ph/2-wl/2,width:6,height:wl,fill:blue,stroke:ink},pv);
  el("rect",{x:px+pw-3,y:py+ph/2-wl2/2,width:6,height:wl2,fill:red,stroke:ink},pv);
  const a=(90-c.ang)*Math.PI/180; // 0 = straight at the wall
  const cx=px-6,cy=py+ph/2,len=60;
  const sx=cx-len*Math.cos(a),sy=cy+len*Math.sin(a);
  el("line",{x1:sx,y1:sy,x2:cx,y2:cy,stroke:blue,"stroke-width":4},pv);
  const ah=[[0,0],[-12,-6],[-12,6]].map(([u,v])=>[cx+u*Math.cos(a)+v*Math.sin(a),cy-u*Math.sin(a)+v*Math.cos(a)]);
  el("polygon",{points:ah.map(p=>p.join(",")).join(" "),fill:blue},pv);
  el("line",{x1:px+6,y1:cy,x2:px+pw-6,y2:cy,stroke:ink2,"stroke-dasharray":"2 4"},pv);
  el("text",{x:sx-4,y:sy-10,fill:blue,"font-size":12,"font-family":"IBM Plex Mono, monospace"},pv,fmt(c.V,1)+" m/s");
  el("text",{x:px+pw/2,y:py+ph+22,fill:ink2,"text-anchor":"middle","font-size":12,"font-family":"IBM Plex Mono, monospace"},pv,fmt(c.L,1)+" × "+fmt(c.W,1)+" m · Cd "+fmt(c.Cdw,2));
  $("plL").textContent="wind at "+Math.round(c.ang)+"° to the wall";
  // TABLE
  const tb=$("tb");tb.innerHTML="";
  [0,0.5,1,1.5,2,3,4].forEach(v=>{const f=flows(c,v),okk=f.Q>=c.req,tr=document.createElement("tr");if(Math.abs(v-c.V)<0.001)tr.className="now";
    tr.innerHTML=`<td>${v}</td><td>${fmt(f.Qw,0)}</td><td>${fmt(f.Qs,0)}</td><td>${fmt(f.ach,1)}</td><td class="${okk?"ok":"bad"}">${okk?"✓":"✕"}</td>`;tb.appendChild(tr)});
}
""")
