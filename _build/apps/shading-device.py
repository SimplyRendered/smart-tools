import pathlib
SOLAR = (pathlib.Path(__file__).parent/'solar.js').read_text()
APP = dict(
slug="shading-device", title="Shading Device Sizer", h1="Shading Device Sizer",
sub="How deep should the chajja or fins be? Pick a city, the wall direction and the hours to shade. Get overhang and fin depths from real sun angles.",
meta=[("Sheet","T-05"),("Method","HSA / VSA"),("Sun","NOAA solar"),("By","@smart_tools_every_week")],
source="Shadow angles: tan VSA = tan(altitude) / cos(HSA). Sun position: NOAA algorithm (±1°).",
inputs="""
      <label for="city">Location<select id="city"></select></label>
      <div class="row">
        <label for="lat">Latitude °<input id="lat" type="number" step="0.01" value="28.61"></label>
        <label for="lon">Longitude °<input id="lon" type="number" step="0.01" value="77.21"></label>
      </div>
      <label for="tz">UTC offset (hours)<input id="tz" type="number" step="0.25" value="5.5"></label>
      <label for="face">Window faces
        <select id="face">
          <option value="0">North (0°)</option><option value="45">North-east (45°)</option><option value="90">East (90°)</option><option value="135">South-east (135°)</option>
          <option value="180" selected>South (180°)</option><option value="225">South-west (225°)</option><option value="270">West (270°)</option><option value="315">North-west (315°)</option>
        </select>
      </label>
      <div class="row">
        <label for="date">Design date<input id="date" type="date" value="2026-04-21"></label>
        <label for="rot">Fine-tune wall °<input id="rot" type="number" step="1" value="0"></label>
      </div>
      <div class="row">
        <label for="t0">Shade from<input id="t0" type="time" value="09:00"></label>
        <label for="t1">Shade until<input id="t1" type="time" value="16:00"></label>
      </div>
      <div class="row">
        <label for="H">Window height mm<input id="H" type="number" step="50" value="1500"></label>
        <label for="W">Window width mm<input id="W" type="number" step="50" value="1200"></label>
      </div>
      <label for="G">Overhang above window head (mm)<input id="G" type="number" step="25" value="150"></label>
      <p class="note">The tool sizes a horizontal overhang to shade the whole window height, and vertical fins to shade the whole width when the sun is at least 20° off the wall's facing direction, for every hour in your window of time on that date. Pick the hottest month you care about.</p>
""",
right="""
      <div class="readout">
        <div><b>Overhang depth</b><span id="oD" class="hi">–</span></div>
        <div><b>Fin depth (oblique sun)</b><span id="oF">–</span></div>
        <div><b>Worst hour</b><span id="oT">–</span></div>
        <div><b>Sun on wall</b><span id="oS">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Section <span>overhang vs. worst sun ray</span></h2><svg id="sec" viewBox="0 0 420 330" role="img" aria-label="Window section with overhang"></svg></div>
        <div class="view"><h2>Plan <span>fins vs. sun direction</span></h2><svg id="plan" viewBox="0 0 420 330" role="img" aria-label="Window plan with fins"></svg></div>
      </div>
      <div class="data">
        <h2>Hour by hour <span id="tblLabel"></span></h2>
        <div class="tablewrap"><table><thead><tr><th>Time</th><th>Altitude</th><th>Azimuth</th><th>HSA</th><th>VSA</th><th>Overhang (mm)</th><th>Fin (mm)</th></tr></thead><tbody id="tbl"></tbody></table></div>
        <p class="note" style="margin-top:10px">HSA is the sun's angle from the window's facing direction in plan. VSA is the profile angle in section. A deep overhang at low VSA (east and west walls) usually means vertical fins or louvres work better.</p>
      </div>
""",
js=SOLAR + r"""
const sel=$("city");CITIES.forEach((c,i)=>{const o=document.createElement("option");o.value=i;o.textContent=c[0];sel.appendChild(o)});
sel.addEventListener("change",()=>{const c=CITIES[sel.value];if(c[1]!==null){$("lat").value=c[1];$("lon").value=c[2];$("tz").value=c[3]}});
["lat","lon","tz"].forEach(id=>$(id).addEventListener("input",()=>{sel.value=CITIES.length-1}));
const tmin=v=>{const [h,m]=v.split(":").map(Number);return h*60+m};
const hm=m=>String(Math.floor(m/60)).padStart(2,"0")+":"+String(Math.round(m%60)).padStart(2,"0");
function angles(p,wall){let hsa=((p.az-wall+540)%360)-180;const on=p.alt>0&&Math.abs(hsa)<90;const vsa=on?deg(Math.atan(Math.tan(rad(p.alt))/Math.cos(rad(hsa)))):NaN;return{hsa,vsa,on}}
function render(){
  const lat=+$("lat").value,lon=+$("lon").value,tz=+$("tz").value,ds=$("date").value||"2026-04-21";
  const wall=(+$("face").value+ +$("rot").value+360)%360,H=+$("H").value,W=+$("W").value,G=+$("G").value;
  const a=tmin($("t0").value||"09:00"),b=tmin($("t1").value||"16:00");
  const rows=[];let worst=null,maxD=0,maxF=0,onCount=0;
  for(let m=a;m<=b;m+=30){const p=solar(ds,m,lat,lon,tz);const g=angles(p,wall);let D=null,F=null;
    if(g.on){onCount++;D=(H+G)/Math.tan(rad(g.vsa));F=Math.abs(g.hsa)<20?null:W/Math.tan(rad(Math.abs(g.hsa)));
      if(D>maxD){maxD=D;worst={m,p,g}}if(F!=null)maxF=Math.max(maxF,F);}
    rows.push({m,p,g,D,F});}
  const ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),sun=css("--sun")||"#E09A1E",blue=css("--blue");
  $("oD").textContent=onCount?(maxD/1000).toFixed(2)+" m":"none";
  $("oF").textContent=onCount&&maxF>0?(maxF/1000).toFixed(2)+" m":"not needed";
  $("oT").textContent=worst?hm(worst.m):"–";
  $("oS").textContent=onCount?Math.round(onCount*30/60*10)/10+" h":"0 h";
  $("tblLabel").textContent=`${DIRS[Math.round(wall/22.5)%16]}-facing wall (${wall}°), ${ds}`;
  // section
  const sv=$("sec");sv.innerHTML="";const k=Math.min(230/(H+G+600),1);const wx=230,wy=60,X=v=>wx+v*k,Y=v=>wy+v*k;
  el("rect",{x:wx,y:20,width:26,height:290,fill:rule,stroke:ink},sv);
  el("rect",{x:wx-2,y:Y(G),width:30,height:H*k,fill:css("--sheet"),stroke:blue,"stroke-width":2},sv);
  const Dd=Math.min(maxD,3500);el("rect",{x:wx-Dd*k,y:Y(0)-8,width:Dd*k+26,height:8,fill:ink},sv);
  if(worst){const v=worst.g.vsa;const L=420;const sx=wx-Dd*k,sy=Y(0);el("line",{x1:sx-Math.cos(rad(v))*L,y1:sy-Math.sin(rad(v))*L,x2:wx,y2:Y(G+H),stroke:sun,"stroke-width":2},sv);
    el("text",{x:20,y:24,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,`VSA ${v.toFixed(1)}° at ${hm(worst.m)}`);
    el("text",{x:sx,y:sy-14,fill:red,"font-size":12,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},sv,(maxD/1000).toFixed(2)+" m");}
  el("text",{x:wx+34,y:Y(G+H/2),fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"window "+H);
  el("text",{x:wx+34,y:300,fill:ink2,"font-size":11,"font-family":"IBM Plex Sans, sans-serif"},sv,"INSIDE");el("text",{x:20,y:300,fill:ink2,"font-size":11,"font-family":"IBM Plex Sans, sans-serif"},sv,"OUTSIDE");
  // plan (wall horizontal, outside at bottom)
  const pv=$("plan");pv.innerHTML="";const kp=Math.min(260/(W+2*Math.min(maxF,1500)+200),0.2);const cx=210,cy=110;
  el("rect",{x:0,y:cy-14,width:420,height:14,fill:rule,stroke:ink},pv);
  el("line",{x1:cx-W*kp/2,y1:cy-7,x2:cx+W*kp/2,y2:cy-7,stroke:blue,"stroke-width":4},pv);
  const Fd=Math.min(maxF,3000)*kp;[-1,1].forEach(sg=>el("rect",{x:cx+sg*W*kp/2-(sg>0?0:4),y:cy,width:4,height:Fd,fill:ink},pv));
  el("text",{x:cx,y:cy-22,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pv,"window "+W);
  if(onCount){el("text",{x:cx+W*kp/2+8,y:cy+Fd/2,fill:red,"font-size":12,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},pv,(maxF/1000).toFixed(2)+" m");}
  rows.filter(r=>r.g.on).forEach(r=>{const ang=rad(r.g.hsa);const L=170;el("line",{x1:cx,y1:cy,x2:cx+Math.sin(ang)*L,y2:cy+Math.cos(ang)*L,stroke:sun,"stroke-width":1,"stroke-opacity":.6},pv);});
  el("text",{x:8,y:320,fill:ink2,"font-size":11,"font-family":"IBM Plex Sans, sans-serif"},pv,"OUTSIDE · sun directions each half hour");
  const tb=$("tbl");tb.innerHTML="";rows.filter(r=>r.m%60===0||r.m===a||r.m===b).forEach(r=>{const tr=document.createElement("tr");
    tr.innerHTML=`<td>${hm(r.m)}</td><td>${r.p.alt.toFixed(1)}°</td><td>${r.p.az.toFixed(0)}°</td><td>${r.g.on?r.g.hsa.toFixed(0)+"°":"—"}</td><td>${r.g.on?r.g.vsa.toFixed(1)+"°":"—"}</td><td>${r.D!=null?Math.round(r.D):"no sun"}</td><td>${!r.g.on?"no sun":r.F!=null?Math.round(r.F):"sun head-on"}</td>`;tb.appendChild(tr)});
}
""")
