APP = dict(
slug="cooling-load", title="AC Cooling Load", h1="AC Cooling Load",
sub="Enter the room, the window and what happens inside. Get the cooling load item by item in watts and tons of refrigeration, the next standard AC size and how far the 1 TR per 100 sq ft rule is off, on a live plan and load chart.",
meta=[("Sheet","T-36"),("Method","Heat balance, peak hour"),("Units","m, W, TR"),("By","@smart_tools_every_week")],
source="Each load is a first-principles heat balance: wall and roof conduction = U × A × (ΔT + sun add-on); glass conduction = U × A × ΔT; glass solar = A × SHGC × peak solar × shading; people, lights and equipment as watts; fresh air sensible = 1.21 W per L/s per K (air density × specific heat) and latent = 3.0 W per L/s per g/kg (density × 2501 kJ/kg). 1 TR = 12,000 Btu/h = 3.517 kW. The glazing, U-value, solar and per-person numbers are typical early-design values and are all editable: this is an estimate, not an HVAC design. Have an HVAC engineer size the final system (ISHRAE / ASHRAE load calculation).",
inputs="""
      <div class="row">
        <label for="L">Room length m<input id="L" type="number" step="0.1" value="5"></label>
        <label for="W">Room width m<input id="W" type="number" step="0.1" value="4"></label>
      </div>
      <div class="row">
        <label for="H">Ceiling height m<input id="H" type="number" step="0.1" value="3"></label>
        <label for="ex">Exposed wall length m<input id="ex" type="number" step="0.1" value="5"></label>
      </div>
      <div class="row">
        <label for="or">Exposed wall faces
          <select id="or"><option value="N">North</option><option value="E">East</option><option value="S">South</option><option value="W" selected>West</option></select>
        </label>
        <label for="wa">Window area m²<input id="wa" type="number" step="0.5" value="3"></label>
      </div>
      <div class="row">
        <label for="gl">Glazing
          <select id="gl"><option value="0.80,5.8">Single clear</option><option value="0.45,5.6">Single reflective</option><option value="0.70,2.8" selected>Double clear</option><option value="0.40,1.8">Double low-e</option></select>
        </label>
        <label for="sh">Shading factor<input id="sh" type="number" step="0.1" value="1"></label>
      </div>
      <div class="row">
        <label for="rf">Roof above
          <select id="rf"><option value="1" selected>Top floor (sun on roof)</option><option value="0">Another floor above</option></select>
        </label>
        <label for="to">Outdoor °C<input id="to" type="number" step="1" value="40"></label>
      </div>
      <div class="row">
        <label for="ti">Indoor °C<input id="ti" type="number" step="0.5" value="24"></label>
        <label for="np">People<input id="np" type="number" step="1" value="4"></label>
      </div>
      <div class="row">
        <label for="lt">Lighting W/m²<input id="lt" type="number" step="1" value="10"></label>
        <label for="eq">Equipment W<input id="eq" type="number" step="50" value="300"></label>
      </div>
      <div class="row">
        <label for="fa">Fresh air L/s each<input id="fa" type="number" step="0.5" value="5"></label>
        <label for="dw">Moisture gap g/kg<input id="dw" type="number" step="0.5" value="6"></label>
      </div>
      <div class="row">
        <label for="uw">Wall U W/m²K<input id="uw" type="number" step="0.1" value="2"></label>
        <label for="ur">Roof U W/m²K<input id="ur" type="number" step="0.1" value="2.8"></label>
      </div>
      <div class="row">
        <label for="is">Peak sun on glass W/m²<input id="is" type="number" step="10" value="520"></label>
        <label for="sf">Safety margin %<input id="sf" type="number" step="5" value="10"></label>
      </div>
      <p class="note">Peak sun on glass fills in when you change the wall direction (typical clear-day values for a low latitude, edit them). Wall U 2.0 is a plastered 230 mm brick wall (see the Wall U-Value tool). The sun adds 5 K to walls and 15 K to roofs on top of the air temperature difference.</p>
""",
right="""
      <div class="readout">
        <div><b>Cooling load</b><span id="oW" class="hi">–</span></div>
        <div><b>Tonnage</b><span id="oT">–</span></div>
        <div><b>Next AC size</b><span id="oS">–</span></div>
        <div><b>1 TR / 100 sq ft rule</b><span id="oR">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Plan <span id="pLabel"></span></h2><svg id="pl" viewBox="0 0 360 300" role="img" aria-label="Room plan with window and sun" style="max-height:320px"></svg></div>
        <div class="view"><h2>Where the heat comes from <span id="bLabel"></span></h2><svg id="bar" viewBox="0 0 360 300" role="img" aria-label="Load breakdown bars" style="max-height:340px"></svg></div>
      </div>
      <div class="data"><h2>Load schedule <span>peak hour</span></h2><div class="tablewrap"><table><thead><tr><th>Source</th><th>Watts</th><th>TR</th><th>Share</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const SUN={N:130,E:520,S:260,W:520};
$("or").addEventListener("change",()=>{$("is").value=SUN[$("or").value]||520;render()});
const SIZES=[0.75,1,1.5,2,2.5,3,4,5,7.5,10,15,20,30,50];
function calc(){
  const L=num("L",1,30,5),W=num("W",1,30,4),H=num("H",2,8,3),ex=num("ex",0,40,5),wa0=num("wa",0,60,3),to=num("to",20,55,40),ti=num("ti",16,30,24),
    np=Math.round(num("np",0,200,4)),lt=num("lt",0,60,10),eq=num("eq",0,50000,300),fa=num("fa",0,30,5),dw=num("dw",0,20,6),uw=num("uw",0.1,6,2),ur=num("ur",0.1,6,2.8),
    is=num("is",0,1100,520),sf=num("sf",0,50,10),sh=num("sh",0,1,1),pp=($("gl").value||"0.7,2.8").split(",").map(Number);
  const SHGC=pp[0]||0.7,UG=pp[1]||2.8,roof=$("rf").value==="1",area=L*W,dT=to-ti,
    wallGross=ex*H,wa=Math.min(wa0,wallGross),wall=wallGross-wa;
  const items=[
    ["Walls",uw*wall*Math.max(0,dT+5)],
    ["Roof",roof?ur*area*Math.max(0,dT+15):0],
    ["Glass heat conduction",UG*wa*dT],
    ["Sun through glass",wa*SHGC*is*sh],
    ["People",np*130],
    ["Lights",lt*area],
    ["Equipment",eq],
    ["Fresh air (temperature)",1.21*fa*np*dT],
    ["Fresh air (humidity)",3.0*fa*np*dw]];
  const ppl=items.find(x=>x[0]==="People");
  const sens=parseFloat($("np").value);
  const sum=items.reduce((a,b)=>a+Math.max(0,b[1]),0),total=sum*(1+sf/100),tr=total/3517,
    next=SIZES.find(s=>s>=tr-1e-9)||SIZES[SIZES.length-1],sqft=area*10.7639,rule=sqft/100;
  return {L,W,H,ex,wa,dT,to,ti,np,sf,roof,area,items,sum,total,tr,next,sqft,rule,or:$("or").value,wall,is,SHGC,UG};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun");
  $("oW").textContent=fmt(c.total/1000,2)+" kW";$("oT").textContent=fmt(c.tr,2)+" TR";$("oS").textContent=fmt(c.next,2).replace(/\.?0+$/,"")+" TR";
  $("oR").textContent=fmt(c.rule,1)+" TR";$("oR").className=c.rule>c.tr*1.15?"bad":"";
  // plan
  const pl=$("pl");pl.innerHTML="";const s=Math.min(240/c.L,170/c.W),w=c.L*s,h=c.W*s,ox=(360-w)/2,oy=(300-h)/2;
  el("rect",{x:ox,y:oy,width:w,height:h,fill:sheet,stroke:ink,"stroke-width":c.roof?5:3},pl);
  const o=c.or,wl=Math.min(c.wa/Math.max(c.H,1),(o==="N"||o==="S"?w:h)-10);
  let g,sx,sy,ax,ay;
  if(o==="N"){g=[ox+(w-wl)/2,oy-2,wl,6];sx=ox+w/2;sy=oy-48;ax=0;ay=1}
  else if(o==="S"){g=[ox+(w-wl)/2,oy+h-4,wl,6];sx=ox+w/2;sy=oy+h+48;ax=0;ay=-1}
  else if(o==="W"){g=[ox-2,oy+(h-wl)/2,6,wl];sx=ox-48;sy=oy+h/2;ax=1;ay=0}
  else{g=[ox+w-4,oy+(h-wl)/2,6,wl];sx=ox+w+48;sy=oy+h/2;ax=-1;ay=0}
  el("rect",{x:g[0],y:g[1],width:g[2],height:g[3],fill:blue,stroke:blue},pl);
  for(let k=-1;k<=1;k++){const px=o==="N"||o==="S"?sx+k*18:sx,py=o==="N"||o==="S"?sy:sy+k*18;
    el("line",{x1:px,y1:py,x2:px+ax*34,y2:py+ay*34,stroke:sun,"stroke-width":3},pl);
    el("path",{d:`M ${px+ax*34-ay*5-ax*6} ${py+ay*34+ax*5-ay*6} L ${px+ax*38} ${py+ay*38} L ${px+ax*34+ay*5-ax*6} ${py+ay*34-ax*5-ay*6}`,fill:"none",stroke:sun,"stroke-width":3},pl);}
  el("text",{x:180,y:oy+h/2+4,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":"IBM Plex Mono, monospace"},pl,fmt(c.area,1)+" m² · "+fmt(c.sqft,0)+" sq ft");
  el("text",{x:180,y:20,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pl,"N ↑");
  el("text",{x:180,y:292,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pl,c.roof?"thick walls = roof in sun":"another floor above");
  $("pLabel").textContent=({N:"north",E:"east",S:"south",W:"west"})[o]+" window "+fmt(c.wa,1)+" m²";
  // bars
  const bs=$("bar");bs.innerHTML="";const mx=Math.max(1,...c.items.map(x=>Math.max(0,x[1])));
  c.items.forEach((it,i)=>{const y=14+i*30,wv=Math.max(0,it[1])/mx*170;
    el("text",{x:4,y:y+10,fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},bs,it[0]);
    el("rect",{x:4,y:y+14,width:Math.max(1,wv),height:9,fill:it[0]==="Sun through glass"?sun:blue,opacity:.85},bs);
    el("text",{x:Math.max(1,wv)+10,y:y+23,fill:ink,"font-size":11,"font-family":"IBM Plex Mono, monospace"},bs,fmt(Math.max(0,it[1]),0)+" W");});
  $("bLabel").textContent=fmt(c.sum,0)+" W + "+fmt(c.sf,0)+"%";
  const tb=$("tb");tb.innerHTML="";c.items.forEach(it=>{const v=Math.max(0,it[1]),tr=document.createElement("tr");tr.innerHTML=`<td>${it[0]}</td><td>${fmt(v,0)}</td><td>${fmt(v/3517,2)}</td><td>${fmt(c.sum>0?v/c.sum*100:0,0)}%</td>`;tb.appendChild(tr)});
  const t2=document.createElement("tr");t2.innerHTML=`<td><b>Total + ${fmt(c.sf,0)}% margin</b></td><td><b>${fmt(c.total,0)}</b></td><td><b>${fmt(c.tr,2)}</b></td><td>100%</td>`;tb.appendChild(t2);
}
""")
