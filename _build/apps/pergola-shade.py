import pathlib
SOLAR = (pathlib.Path(__file__).parent/'solar.js').read_text()
APP = dict(
slug="pergola-shade", title="Pergola Slat Shade", h1="Pergola Slat Shade",
sub="How much of the terrace do the pergola slats really shade? Pick the city, date and time, the slat size, gap and direction. Get the shade under the pergola right now, the hours of full shade and a day chart.",
meta=[("Sheet","T-51"),("Method","Profile angle"),("Sun","NOAA solar"),("By","@smart_tools_every_week")],
source="Sun position: NOAA solar algorithm (±1°). Profile angle across the slats: tan θ = tan(altitude) ÷ |cos(sun azimuth − slat normal)|. Shadow of one slat on the ground = width + depth ÷ tan θ; shade = that ÷ (width + gap), capped at 100%. Direct sun only, flat slats on a level grid; sky light and slat reflections are not counted.",
inputs="""
      <label for="city">Location<select id="city"></select></label>
      <div class="row">
        <label for="lat">Latitude °<input id="lat" type="number" step="0.01" value="28.61"></label>
        <label for="lon">Longitude °<input id="lon" type="number" step="0.01" value="77.21"></label>
      </div>
      <div class="row">
        <label for="tz">UTC offset h<input id="tz" type="number" step="0.25" value="5.5"></label>
        <label for="date">Date<input id="date" type="date" value="2026-05-21"></label>
      </div>
      <label for="t">Time <span id="tLab" class="time">15:30</span><input id="t" type="range" min="360" max="1170" step="15" value="930"></label>
      <label for="ax">Slats run towards, ° from north<input id="ax" type="number" step="5" value="0"></label>
      <p class="note">90 = slats run east–west, 0 = north–south. Long east–west slats block the high midday sun; north–south slats block low morning and evening sun.</p>
      <div class="row">
        <label for="w">Slat width mm<input id="w" type="number" step="5" value="50"></label>
        <label for="dp">Slat depth mm<input id="dp" type="number" step="5" value="150"></label>
      </div>
      <label for="s">Clear gap between slats mm<input id="s" type="number" step="5" value="50"></label>
""",
right="""
      <div class="readout">
        <div><b>Shade now</b><span id="oS" class="hi">–</span></div>
        <div><b>Sun profile angle</b><span id="oA">–</span></div>
        <div><b>Full shade below</b><span id="oC">–</span></div>
        <div><b>Full shade today</b><span id="oH">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Section across the slats <span id="sLabel"></span></h2><svg id="sec" viewBox="0 0 580 300" role="img" aria-label="Section through the slats with sun rays and the shadow on the floor"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Shade through the day <span id="cLabel"></span></h2><svg id="day" viewBox="0 0 300 230" role="img" aria-label="Chart of shade percent through the day"></svg></div>
        <div class="view"><h2>Plan <span id="pLabel"></span></h2><svg id="plan" viewBox="0 0 300 230" role="img" aria-label="Plan of the slats with north and the sun direction"></svg></div>
      </div>
      <div class="data"><h2>Hour by hour <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Time</th><th>Sun altitude</th><th>Azimuth</th><th>Profile angle</th><th>Shade</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=SOLAR + r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const hm=m=>{m=Math.round(m);m=((m%1440)+1440)%1440;return String(Math.floor(m/60)).padStart(2,"0")+":"+String(m%60).padStart(2,"0")};
const sel=$("city");CITIES.forEach((c,i)=>{const o=document.createElement("option");o.value=i;o.textContent=c[0];sel.appendChild(o)});
sel.addEventListener("change",()=>{const c=CITIES[sel.value];if(c[1]!==null){$("lat").value=c[1];$("lon").value=c[2];$("tz").value=c[3]}render()});
["lat","lon","tz"].forEach(id=>$(id).addEventListener("input",()=>{sel.value=CITIES.length-1}));
function shadeAt(p,ax,w,d,s){
  if(p.alt<=0)return null;
  const nrm=ax+90,cg=Math.cos(rad(p.az-nrm)),ta=Math.tan(rad(Math.min(p.alt,89.999)));
  const prof=Math.abs(cg)<1e-9?90:deg(Math.atan(ta/Math.abs(cg)));
  const sh=Math.min(1,(w+d*Math.abs(cg)/ta)/(w+s));
  return {prof,sh,side:cg>=0?1:-1};
}
function calc(){
  const lat=num("lat",-66,66,28.61),lon=num("lon",-180,180,77.21),tz=num("tz",-12,14,5.5);
  let ds=$("date").value;if(!/^\d{4}-\d{2}-\d{2}$/.test(ds))ds="2026-05-21";
  const t=num("t",0,1439,930),ax=num("ax",-360,360,90),w=num("w",5,1000,50),d=num("dp",0,2000,150),s=num("s",1,3000,50);
  const p=solar(ds,t,lat,lon,tz),now=shadeAt(p,ax,w,d,s),cut=deg(Math.atan(d/s));
  const day=[];let full=0;const step=5;
  for(let m=0;m<1440;m+=step){const q=solar(ds,m,lat,lon,tz),r=shadeAt(q,ax,w,d,s);if(r){day.push([m,r.sh]);if(r.sh>=0.999)full+=step}}
  const rows=[];for(let m=360;m<=1140;m+=60){const q=solar(ds,m,lat,lon,tz);rows.push({m,q,r:shadeAt(q,ax,w,d,s)})}
  return {lat,lon,tz,ds,t,ax,w,d,s,p,now,cut,day,full,rows,base:w/(w+s)};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),shadow=css("--shadow"),F="IBM Plex Mono, monospace";
  $("tLab").textContent=hm(c.t);
  $("oS").textContent=c.now?fmt(c.now.sh*100,0)+"%":"sun down";$("oA").textContent=c.now?fmt(c.now.prof,1)+"°":"–";
  $("oC").textContent=fmt(c.cut,1)+"°";$("oH").textContent=(c.full/60).toFixed(1)+" h";
  // section across the slats
  const sv=$("sec");sv.innerHTML="";const p=c.w+c.s,n=Math.max(3,Math.min(14,Math.floor(1500/p))),span=n*p,k=Math.min(500/span,120/Math.max(c.d,1),3),ox=(580-span*k)/2,top=92,gy=255,bot=top+c.d*k;
  el("line",{x1:20,y1:gy,x2:560,y2:gy,stroke:ink,"stroke-width":1.4},sv);
  if(c.now){const cot=Math.min(50,1/Math.tan(rad(Math.max(c.now.prof,0.5)))),sg=c.now.side,pr=(X,Y)=>X-sg*cot*(gy-Y),E0=ox,E1=ox+span*k;
    el("rect",{x:fmt(E0,1),y:gy-14,width:fmt(span*k,1),height:14,fill:sun,opacity:.95},sv);
    for(let i=-60;i<n+60;i++){const x=ox+(i*p+c.s/2)*k,xs=[pr(x,top),pr(x+c.w*k,top),pr(x,bot),pr(x+c.w*k,bot)],L1=Math.max(E0,Math.min(...xs)),R1=Math.min(E1,Math.max(...xs));
      if(R1>L1)el("rect",{x:fmt(L1,1),y:gy-14,width:fmt(R1-L1,1),height:14,fill:"#5A6672"},sv)}
    for(let i=0;i<n-1;i+=Math.max(1,Math.floor(n/5))){const gl=ox+(i*p+c.s/2+c.w)*k,gr=gl+c.s*k,xt=(gl+gr)/2,xb=xt-sg*cot*(bot-top),y0=60,x0=xt+sg*cot*(top-y0);
      if(xb>=gl-0.01&&xb<=gr+0.01)el("line",{x1:fmt(x0,1),y1:y0,x2:fmt(pr(xt,top),1),y2:gy-14,stroke:sun,"stroke-width":1.6},sv);
      else{const ed=sg>0?gl:gr,yh=top+Math.abs(xt-ed)/cot;el("line",{x1:fmt(x0,1),y1:y0,x2:fmt(ed,1),y2:fmt(yh,1),stroke:sun,"stroke-width":1.6},sv)}}
  }
  for(let i=0;i<n;i++){const x=ox+(i*p+c.s/2)*k;el("rect",{x:fmt(x,1),y:top,width:fmt(Math.max(1,c.w*k),1),height:fmt(Math.max(1,c.d*k),1),fill:blue,opacity:.85},sv)}
  el("text",{x:20,y:24,fill:red,"font-size":15,"font-family":F},sv,c.now?"shade on the floor "+fmt(c.now.sh*100,0)+"% at "+hm(c.t):"sun is down at "+hm(c.t));
  el("text",{x:20,y:44,fill:ink2,"font-size":13,"font-family":F},sv,"slats "+c.w+" × "+c.d+" mm, gap "+c.s+" mm · plan cover "+fmt(c.base*100,0)+"%");
  el("text",{x:20,y:288,fill:ink2,"font-size":13,"font-family":F},sv,"grey = shadow, gold = sun on the floor · full shade at ≤ "+fmt(c.cut,1)+"°");
  $("sLabel").textContent=c.now?"profile "+fmt(c.now.prof,1)+"°":"night";
  // day chart
  const dv=$("day");dv.innerHTML="";const X=m=>40+(m-300)/(1200-300)*245,Y=v=>190-v*165;
  el("line",{x1:40,y1:190,x2:288,y2:190,stroke:ink},dv);el("line",{x1:40,y1:20,x2:40,y2:190,stroke:ink},dv);
  [0,0.5,1].forEach(v=>{el("line",{x1:40,y1:fmt(Y(v),1),x2:288,y2:fmt(Y(v),1),stroke:rule},dv);el("text",{x:34,y:fmt(Y(v)+4,1),"text-anchor":"end",fill:ink2,"font-size":11,"font-family":F},dv,v*100+"%")});
  [360,540,720,900,1080].forEach(m=>el("text",{x:fmt(X(m),1),y:206,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},dv,hm(m)));
  el("line",{x1:40,y1:fmt(Y(c.base),1),x2:288,y2:fmt(Y(c.base),1),stroke:ink2,"stroke-dasharray":"4 4"},dv);
  el("text",{x:286,y:fmt(Y(c.base)+14,1),"text-anchor":"end",fill:ink2,"font-size":10,"font-family":F},dv,"plan cover "+fmt(c.base*100,0)+"%");
  const pts=c.day.filter(q=>q[0]>=300&&q[0]<=1200);
  if(pts.length){el("path",{d:pts.map((q,i)=>(i?"L":"M")+fmt(X(q[0]),1)+" "+fmt(Y(q[1]),1)).join(""),fill:"none",stroke:blue,"stroke-width":2},dv)}
  if(c.now&&c.t>=300&&c.t<=1200)el("circle",{cx:fmt(X(c.t),1),cy:fmt(Y(c.now.sh),1),r:5,fill:red},dv);
  $("cLabel").textContent=c.ds;
  // plan
  const pv=$("plan");pv.innerHTML="";const cx=150,cy=115,R=85,a=rad(c.ax);
  el("rect",{x:cx-R,y:cy-R,width:2*R,height:2*R,fill:"none",stroke:ink2},pv);
  const ux=Math.sin(a),uy=-Math.cos(a),nx=-uy,ny=ux;
  for(let i=-6;i<=6;i++){const o=i*13,x1=cx+nx*o-ux*R*1.5,y1=cy+ny*o-uy*R*1.5,x2=cx+nx*o+ux*R*1.5,y2=cy+ny*o+uy*R*1.5;el("line",{x1:fmt(x1,1),y1:fmt(y1,1),x2:fmt(x2,1),y2:fmt(y2,1),stroke:blue,"stroke-width":3,opacity:.8,"clip-path":"url(#clp)"},pv)}
  const cp=el("clipPath",{id:"clp"},pv);el("rect",{x:cx-R,y:cy-R,width:2*R,height:2*R},cp);
  el("text",{x:cx,y:cy-R-8,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":F},pv,"N ↑");
  if(c.now){const az=rad(c.p.az),sx=cx+Math.sin(az)*(R+18),sy=cy-Math.cos(az)*(R+18);el("line",{x1:fmt(sx,1),y1:fmt(sy,1),x2:cx,y2:cy,stroke:sun,"stroke-width":2.5},pv);el("circle",{cx:fmt(sx,1),cy:fmt(sy,1),r:8,fill:sun},pv)}
  el("text",{x:cx,y:224,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},pv,"slats run "+fmt(((c.ax%360)+360)%360,0)+"° · sun az "+fmt(c.p.az,0)+"°, alt "+fmt(c.p.alt,0)+"°");
  $("pLabel").textContent=dirName(c.ax)+"–"+dirName(c.ax+180);
  // table
  $("tb").innerHTML=c.rows.map(r=>`<tr${Math.abs(r.m-c.t)<30?' class="now"':""}><td>${hm(r.m)}</td><td>${fmt(r.q.alt,1)}°</td><td>${fmt(r.q.az,0)}°</td><td>${r.r?fmt(r.r.prof,1)+"°":"–"}</td><td>${r.r?fmt(r.r.sh*100,0)+"%":"sun down"}</td></tr>`).join("");
  $("dLabel").textContent=fmt(c.full/60,1)+" h of full shade · lat "+fmt(c.lat,2)+"°";
}
""")
