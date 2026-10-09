APP = dict(
slug="lighting-layout", title="Lighting Layout", h1="Lighting Layout",
sub="How many lights does this room need, and where do they go? Lumen-method fitting count, spacing check and a ceiling grid for any room.",
meta=[("Sheet","T-09"),("Method","Lumen method"),("Units","m · lux · lm"),("By","@smart_tools_every_week")],
source="N = E × A ÷ (F × UF × MF). Default UF values are typical for recessed LED panels (ceiling/wall/floor reflectance 70/50/20); use your luminaire's photometric data for final design.",
inputs="""
      <label for="space">Space (typical target)
        <select id="space">
          <option value="150">Living room (150 lux)</option><option value="100">Bedroom (100 lux)</option><option value="300" selected>Kitchen / classroom (300 lux)</option>
          <option value="500">Office desk / study (500 lux)</option><option value="750">Drawing office / detailed work (750 lux)</option><option value="100">Corridor / stairs (100 lux)</option><option value="500">Retail floor (500 lux)</option>
        </select>
      </label>
      <label for="E">Target illuminance (lux)<input id="E" type="number" step="25" value="300"></label>
      <div class="row">
        <label for="L">Length (m)<input id="L" type="number" step="0.1" value="6"></label>
        <label for="W">Width (m)<input id="W" type="number" step="0.1" value="4.5"></label>
      </div>
      <div class="row">
        <label for="Hc">Ceiling height (m)<input id="Hc" type="number" step="0.05" value="3.0"></label>
        <label for="Hw">Work plane (m)<input id="Hw" type="number" step="0.05" value="0.75"></label>
      </div>
      <div class="row">
        <label for="F">Lumens per fitting<input id="F" type="number" step="100" value="3600"></label>
        <label for="P">Watts per fitting<input id="P" type="number" step="1" value="36"></label>
      </div>
      <div class="row">
        <label for="MF">Maintenance factor<input id="MF" type="number" step="0.05" value="0.80"></label>
        <label for="UFm">UF (blank = auto)<input id="UFm" type="number" step="0.01" placeholder="auto"></label>
      </div>
      <p class="note">Targets are common design values. Check your local code, such as NBC Part 8 or IS 3646, for the exact requirement.</p>
""",
right="""
      <div class="readout">
        <div><b>Fittings</b><span id="oN" class="hi">–</span></div>
        <div><b>Grid</b><span id="oG">–</span></div>
        <div><b>Average lux</b><span id="oE">–</span></div>
        <div><b>Power density</b><span id="oP">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Reflected ceiling plan <span id="rcp"></span></h2><svg id="plan" viewBox="0 0 640 400" role="img" aria-label="Ceiling plan with light fittings and light spread"></svg></div>
      </div>
      <div class="data">
        <h2>Working <span>lumen method, step by step</span></h2>
        <div class="tablewrap"><table><thead><tr><th>Step</th><th>Value</th><th>How</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
js=r"""
$("space").addEventListener("change",()=>{$("E").value=$("space").value});
const UFT=[[0.6,0.40],[0.8,0.48],[1.0,0.53],[1.25,0.58],[1.5,0.62],[2.0,0.67],[2.5,0.70],[3.0,0.72],[4.0,0.75],[5.0,0.77]];
function ufFor(ri){if(ri<=UFT[0][0])return UFT[0][1];for(let i=1;i<UFT.length;i++){if(ri<=UFT[i][0]){const [a,ua]=UFT[i-1],[b,ub]=UFT[i];return ua+(ub-ua)*(ri-a)/(b-a)}}return UFT[UFT.length-1][1]}
function render(){
  const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)&&v>=min?Math.min(max,v):def};
  const E=num("E",1,5000,300),L=num("L",0.5,60,0.5),W=num("W",0.5,60,0.5),Hc=num("Hc",1,30,3),Hw=num("Hw",0,5,0.75),F=num("F",100,200000,3600),P=num("P",0,2000,36),MF=Math.min(1,num("MF",0.1,1,0.8));
  const Hm=Math.max(0.3,Hc-Hw),A=L*W,RI=A/(Hm*(L+W));const ufIn=parseFloat($("UFm").value);const UF=Number.isFinite(ufIn)&&ufIn>=0.05?Math.min(1,ufIn):ufFor(RI);
  const Nraw=E*A/(F*UF*MF);let N=Math.max(1,Math.ceil(Nraw));
  let cols=Math.max(1,Math.round(Math.sqrt(N*L/W))),rows=Math.max(1,Math.ceil(N/cols));while((cols-1)*rows>=N&&cols>1)cols--;rows=Math.ceil(N/cols);const n=rows*cols;
  const Sx=L/cols,Sy=W/rows,SHR=Math.max(Sx,Sy)/Hm,Eav=n*F*UF*MF/A,LPD=n*P/A;
  $("oN").textContent=n;$("oG").textContent=`${cols} × ${rows}`;$("oE").textContent=Math.round(Eav)+" lx";$("oP").textContent=LPD.toFixed(1)+" W/m²";
  $("rcp").textContent=`spacing ${Sx.toFixed(2)} × ${Sy.toFixed(2)} m · SHR ${SHR.toFixed(2)}${SHR>1.5?" (too wide)":""}`;
  const rowsT=[["Mounting height above work plane Hm",Hm.toFixed(2)+" m",`${Hc} − ${Hw}`],["Room index RI",RI.toFixed(2),`(L × W) ÷ (Hm × (L + W))`],["Utilisation factor UF",UF.toFixed(2),Number.isFinite(ufIn)&&ufIn>=0.05?"entered":"typical value for this RI"],
    ["Fittings needed",Nraw.toFixed(2)+" → "+N,`${E} lx × ${A.toFixed(1)} m² ÷ (${F} lm × ${UF.toFixed(2)} × ${MF})`],["Layout",`${cols} × ${rows} = ${n}`,"even grid close to the room's proportions"],
    ["Spacing to height ratio",SHR.toFixed(2),SHR<=1.5?"within the usual 1.5 limit":"over 1.5: expect dark patches, so add a row or column"],["Maintained average",Math.round(Eav)+" lux",`${n} × ${F} × ${UF.toFixed(2)} × ${MF} ÷ ${A.toFixed(1)}`],["Lighting power density",LPD.toFixed(1)+" W/m²",`${n} × ${P} W ÷ ${A.toFixed(1)} m²`]];
  const tb=$("tbl");tb.innerHTML="";rowsT.forEach(r=>{const tr=document.createElement("tr");tr.innerHTML=`<td style="font-family:var(--body);text-align:left">${r[0]}</td><td>${r[1]}</td><td style="white-space:normal;text-align:left">${r[2]}</td>`;tb.appendChild(tr)});
  const s=$("plan");s.innerHTML="";const ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),sunc=css("--sun")||"#E09A1E";
  const k=Math.min(560/L,320/W),ox=(640-L*k)/2,oy=30,X=v=>ox+v*k,Y=v=>oy+v*k;
  const pts=[];for(let r=0;r<rows;r++)for(let c=0;c<cols;c++)pts.push([Sx*(c+0.5),Sy*(r+0.5)]);
  // relative direct illuminance (Lambertian, cos^4/h^2), shown as tint
  const g=24,cw=L/g,ch=W/Math.max(1,Math.round(g*W/L));const ny=Math.round(W/ch);let vals=[],mx=0,mn=Infinity;
  for(let j=0;j<ny;j++)for(let i=0;i<g;i++){const x=(i+0.5)*cw,y=(j+0.5)*ch;let e=0;pts.forEach(p=>{const d2=(x-p[0])**2+(y-p[1])**2+Hm*Hm;e+=Hm**4/(d2*d2)});vals.push([i,j,e]);mx=Math.max(mx,e);mn=Math.min(mn,e)}
  vals.forEach(([i,j,e])=>el("rect",{x:X(i*cw),y:Y(j*ch),width:cw*k+0.5,height:ch*k+0.5,fill:sunc,"fill-opacity":(0.08+0.55*(e-mn)/(mx-mn||1)).toFixed(3)},s));
  el("rect",{x:X(0),y:Y(0),width:L*k,height:W*k,fill:"none",stroke:ink,"stroke-width":2},s);
  pts.forEach(p=>{el("rect",{x:X(p[0])-9,y:Y(p[1])-9,width:18,height:18,fill:css("--sheet"),stroke:ink,"stroke-width":1.5},s);el("line",{x1:X(p[0])-9,y1:Y(p[1])-9,x2:X(p[0])+9,y2:Y(p[1])+9,stroke:ink},s);el("line",{x1:X(p[0])+9,y1:Y(p[1])-9,x2:X(p[0])-9,y2:Y(p[1])+9,stroke:ink},s)});
  if(cols>1){const y=Y(W)+18;el("line",{x1:X(pts[0][0]),y1:y,x2:X(pts[1][0]),y2:y,stroke:red},s);el("text",{x:(X(pts[0][0])+X(pts[1][0]))/2,y:y+14,"text-anchor":"middle",fill:red,"font-size":11,"font-family":"IBM Plex Mono, monospace"},s,Sx.toFixed(2)+" m")}
  el("text",{x:X(0),y:Y(0)-10,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},s,`${L} × ${W} m · uniformity (direct) Emin/Eav ≈ ${(mn/(vals.reduce((a,v)=>a+v[2],0)/vals.length)).toFixed(2)}`);
}
""")
