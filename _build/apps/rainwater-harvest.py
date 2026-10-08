APP = dict(
slug="rainwater-harvest", title="Rainwater Harvesting", h1="Rainwater Harvesting",
sub="How much rain can your roof collect, and how big should the tank be? Enter the catchment, rainfall and use, and get the yearly yield, tank size and supply days.",
meta=[("Sheet","T-08"),("Method","Q = A × R × C"),("Units","m² · mm · L"),("By","@smart_tools_every_week")],
source="Yield = catchment area × rainfall × runoff coefficient × collection efficiency. City rainfall figures are approximate annual normals; use IMD data for your site.",
inputs="""
      <label for="city">City (approx. annual rainfall)<select id="city"></select></label>
      <label for="R">Annual rainfall (mm)<input id="R" type="number" step="10" value="790"></label>
      <div class="row">
        <label for="A">Roof area (m²)<input id="A" type="number" step="5" value="120"></label>
        <label for="roof">Roof surface<select id="roof">
          <option value="0.85">RCC / concrete (0.85)</option><option value="0.90">Metal sheet (0.90)</option><option value="0.75">Clay tile (0.75)</option><option value="0.60">Green roof (0.60)</option></select></label>
      </div>
      <div class="row">
        <label for="A2">Paved area (m²)<input id="A2" type="number" step="5" value="40"></label>
        <label for="C2">Paved coeff.<input id="C2" type="number" step="0.05" value="0.60"></label>
      </div>
      <div class="row">
        <label for="eff">Collection efficiency<input id="eff" type="number" step="0.05" value="0.80"></label>
        <label for="ff">First flush (mm)<input id="ff" type="number" step="0.5" value="2"></label>
      </div>
      <div class="row">
        <label for="dd">Design storm (mm/day)<input id="dd" type="number" step="5" value="50"></label>
        <label for="use">Use (litres/day)<input id="use" type="number" step="50" value="400"></label>
      </div>
      <p class="note">The tank is sized to catch one design-storm day from the roof. Paved areas usually go to a recharge pit rather than the tank. Runoff coefficients are typical values, so adjust them for your surfaces.</p>
""",
right="""
      <div class="readout">
        <div><b>Roof yield / year</b><span id="oY" class="hi">–</span></div>
        <div><b>Suggested tank</b><span id="oT">–</span></div>
        <div><b>Days of supply</b><span id="oD">–</span></div>
        <div><b>Recharge / year</b><span id="oP">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>System <span>roof → first flush → tank → overflow to recharge</span></h2><svg id="sys" viewBox="0 0 640 260" role="img" aria-label="Rainwater harvesting system diagram"></svg></div>
      </div>
      <div class="data">
        <h2>Numbers <span>per year unless stated</span></h2>
        <div class="tablewrap"><table><thead><tr><th>Item</th><th>Value</th><th>How</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
js=r"""
const CITY=[["New Delhi",790],["Mumbai",2200],["Bengaluru",970],["Chennai",1400],["Kolkata",1600],["Hyderabad",830],["Pune",720],["Ahmedabad",780],["Jaipur",650],["Lucknow",1000],["Chandigarh",1100],["Raipur / Durg",1300],["Panaji, Goa",2900],["Kochi",3000],["Guwahati",1700],["Custom",null]];
const cs=$("city");CITY.forEach((c,i)=>{const o=document.createElement("option");o.value=i;o.textContent=c[1]?`${c[0]} (~${c[1]} mm)`:c[0];cs.appendChild(o)});
cs.addEventListener("change",()=>{const c=CITY[cs.value];if(c[1])$("R").value=c[1]});$("R").addEventListener("input",()=>{cs.value=CITY.length-1});
const TANKS=[500,750,1000,1500,2000,3000,5000,7500,10000,15000,20000,25000,30000,50000];
const L=v=>v>=10000?(v/1000).toFixed(1)+" m³":Math.round(v).toLocaleString("en-IN")+" L";
function render(){
  const R=+$("R").value,A=+$("A").value,C=+$("roof").value,A2=+$("A2").value,C2=+$("C2").value,eff=+$("eff").value,ff=+$("ff").value,dd=+$("dd").value,use=+$("use").value;
  const roofYield=A*(R/1000)*C*eff*1000; // litres
  const flushPerEvent=A*ff; // L per rain event (1 mm on 1 m² = 1 L)
  const design=A*dd*C*eff-flushPerEvent;const tank=TANKS.find(t=>t>=design)||Math.ceil(design/1000)*1000;
  const days=use>0?tank/use:Infinity;const annualUse=use*365;const cover=Math.min(1,roofYield/annualUse);
  const pave=A2*(R/1000)*C2*1000;
  $("oY").textContent=L(roofYield);$("oT").textContent=L(tank);$("oD").textContent=Number.isFinite(days)?days.toFixed(1)+" d":"–";$("oP").textContent=L(pave);
  const rows=[["Rain falling on roof",L(A*R),`${A} m² × ${R} mm`],["Roof yield",L(roofYield),`× runoff ${C} × efficiency ${eff}`],["Design-storm volume",L(Math.max(0,design)),`${A} m² × ${dd} mm × ${C} × ${eff} − first flush ${L(flushPerEvent)}`],
    ["Suggested tank (next standard size)",L(tank),"catches one design-storm day"],["Days of supply from a full tank",Number.isFinite(days)?days.toFixed(1):"–",`${L(tank)} ÷ ${use} L/day`],
    ["Yearly demand",L(annualUse),`${use} L/day × 365`],["Share of yearly demand the roof could meet",(cover*100).toFixed(0)+"%","if every litre is stored and used; real figure is lower in a short monsoon"],
    ["Paved area runoff to recharge",L(pave),`${A2} m² × ${R} mm × ${C2}`],["First-flush diverter per rain event",L(flushPerEvent),`${ff} mm × ${A} m²`]];
  const tb=$("tbl");tb.innerHTML="";rows.forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${r[0]}</td><td>${r[1]}</td><td style="white-space:normal;text-align:left;font-family:var(--body)">${r[2]}</td>`;tb.appendChild(tr)});
  // diagram
  const s=$("sys");s.innerHTML="";const ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),blue=css("--blue"),red=css("--red");
  for(let i=0;i<22;i++)el("line",{x1:20+i*9,y1:8+(i%3)*6,x2:14+i*9,y2:24+(i%3)*6,stroke:blue,"stroke-width":1.2,"stroke-opacity":.6},s);
  el("polygon",{points:"10,70 120,40 230,70",fill:rule,stroke:ink,"stroke-width":1.5},s);el("rect",{x:30,y:70,width:180,height:120,fill:"none",stroke:ink,"stroke-width":1.5},s);
  el("text",{x:120,y:64,"text-anchor":"middle",fill:ink,"font-size":12,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif"},s,`ROOF ${A} m²`);
  el("path",{d:"M228 72 L250 72 L250 120 L300 120",fill:"none",stroke:ink,"stroke-width":2},s);
  el("rect",{x:300,y:105,width:24,height:60,fill:css("--paper"),stroke:ink},s);el("text",{x:312,y:182,"text-anchor":"middle",fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},s,"FIRST");el("text",{x:312,y:194,"text-anchor":"middle",fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},s,"FLUSH");
  el("path",{d:"M324 120 L370 120",fill:"none",stroke:ink,"stroke-width":2},s);
  const th=130,fillH=Math.min(1,Math.max(0,design)/tank)*th;el("rect",{x:370,y:90,width:120,height:th,fill:"none",stroke:ink,"stroke-width":2},s);
  el("rect",{x:372,y:90+th-fillH+2,width:116,height:Math.max(0,fillH-4),fill:blue,"fill-opacity":.35},s);
  el("text",{x:430,y:84,"text-anchor":"middle",fill:ink,"font-size":12,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif"},s,"TANK "+L(tank));
  el("text",{x:430,y:162,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},s,Number.isFinite(days)?days.toFixed(1)+" days":"");
  el("path",{d:"M490 100 L540 100 L540 200",fill:"none",stroke:red,"stroke-width":2,"stroke-dasharray":"5 4"},s);el("text",{x:546,y:118,fill:red,"font-size":11,"font-family":"IBM Plex Sans, sans-serif"},s,"overflow");
  el("rect",{x:510,y:200,width:70,height:44,fill:css("--paper"),stroke:ink},s);for(let i=0;i<6;i++)el("circle",{cx:520+i*11,cy:226,r:3,fill:ink2},s);
  el("text",{x:545,y:256,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Sans, sans-serif"},s,"RECHARGE PIT");
  el("line",{x1:0,y1:244,x2:640,y2:244,stroke:ink,"stroke-width":1},s);
  el("text",{x:30,y:214,fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},s,`${L(roofYield)} / year from the roof`);
}
""")
