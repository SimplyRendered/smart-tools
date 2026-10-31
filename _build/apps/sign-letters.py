APP = dict(
slug="sign-letters", title="Sign Letter Height", h1="Sign Letter Height",
sub="Enter how far away people read the sign and how high it hangs. Get the minimum letter height from ADA Table 703.5.5, compared with the 1 inch per 10 feet rule, on a live elevation with the sightline.",
meta=[("Sheet","T-44"),("Standard","ADA 2010 · 703.5.5"),("Units","m, mm, inches"),("By","@smart_tools_every_week")],
source="Minimum character height (uppercase I, measured from the baseline) from 2010 ADA Standards Table 703.5.5: baseline 40–70 in: 5/8 in, plus 1/8 in per ft of viewing distance over 72 in; over 70–120 in: 2 in, plus 1/8 in per ft over 180 in; over 120 in: 3 in, plus 1/8 in per ft over 21 ft (applied pro-rata here). Baseline at least 40 in (1015 mm) above the floor (703.5.6). Viewing distance = horizontal distance to the nearest point people can stand. The '1 in per 10 ft' rule of thumb is editable. Check your local code (e.g. Harmonised Guidelines 2021 in India) too.",
inputs="""
      <div class="row">
        <label for="dist">Viewing distance m<input id="dist" type="number" step="0.5" value="9"></label>
        <label for="hb">Letter baseline above floor m<input id="hb" type="number" step="0.05" value="2.75"></label>
      </div>
      <div class="row">
        <label for="eye">Eye height m<input id="eye" type="number" step="0.05" value="1.6"></label>
        <label for="rule">Rule of thumb mm per m<input id="rule" type="number" step="0.1" value="8.3"></label>
      </div>
      <label for="txt">Sign text<input id="txt" type="text" value="LECTURE HALL 2" maxlength="24"></label>
      <label for="cap">Letters you plan mm (0 = none)<input id="cap" type="number" step="5" value="75"></label>
      <p class="note">Eye height: about 1.60 m standing, 1.20 m in a wheelchair. 8.3 mm per m is the sign-trade rule of 1 inch of letter for every 10 feet of distance.</p>
""",
right="""
      <div class="readout">
        <div><b>ADA minimum</b><span id="oH" class="hi">–</span></div>
        <div><b>In inches</b><span id="oI">–</span></div>
        <div><b>Rule of thumb</b><span id="oR">–</span></div>
        <div><b>Look-up angle</b><span id="oA">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Elevation <span id="eLabel"></span></h2><svg id="elev" viewBox="0 0 580 330" role="img" aria-label="Elevation of a viewer and a sign with the sightline"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Letters side by side <span>to scale</span></h2><svg id="let" viewBox="0 0 300 220" role="img" aria-label="Letter heights compared at the same scale"></svg></div>
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="data"><h2>Minimum height by distance <span>mm · ADA 703.5.5</span></h2><div class="tablewrap"><table><thead><tr><th>Distance</th><th>Baseline 1.0–1.8 m</th><th>1.8–3.05 m</th><th>Over 3.05 m</th><th>1 in / 10 ft</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function ada(hIn,dIn){ // returns minimum character height in inches and band
  if(hIn<=70){return {band:1,h:dIn<72?0.625:0.625+(dIn-72)/12*0.125}}
  if(hIn<=120){return {band:2,h:dIn<180?2:2+(dIn-180)/12*0.125}}
  return {band:3,h:dIn<252?3:3+(dIn-252)/12*0.125};
}
const BANDS=["","1015–1780 mm","over 1780 to 3050 mm","over 3050 mm"];
function calc(){
  const d=num("dist",0.3,200,9),hb=num("hb",0.3,20,2.75),eye=num("eye",0.5,2.5,1.6),rule=num("rule",0.5,50,8.3),cap=num("cap",0,2000,0);
  const r=ada(hb/0.0254,d/0.0254),mm=Math.ceil(r.h*25.4),rt=Math.ceil(d*rule);
  const ang=Math.atan2(hb+mm/2000-eye,d)*180/Math.PI;
  return {d,hb,eye,rule,cap,band:r.band,inch:r.h,mm,rt,ang,low:hb<1.015};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),ok=css("--ok"),F="IBM Plex Mono, monospace";
  $("oH").textContent=c.mm+" mm";$("oI").textContent=fmt(c.inch,2)+" in";$("oR").textContent=c.rt+" mm";$("oA").textContent=fmt(c.ang,1)+"°";
  $("oR").className=c.rt<c.mm?"bad":"";
  const C=[[`Baseline ${Math.round(c.hb*1000)} mm is at least 1015 mm above the floor (703.5.6)`,!c.low],
    [`Rule of thumb gives ${c.rt} mm: ${c.rt>=c.mm?"meets":"under"} the ADA ${c.mm} mm`,c.rt>=c.mm,"warn"],
    c.cap>0?[`Your ${c.cap} mm letters ${c.cap>=c.mm?"meet":"are under"} the ${c.mm} mm minimum`,c.cap>=c.mm]:["Enter your letter size to check it",true,"info"],
    [`Look-up angle ${fmt(c.ang,1)}° from a ${fmt(c.eye,2)} m eye height${Math.abs(c.ang)>30?": steep, move it lower or further":""}`,Math.abs(c.ang)<=30,"warn"]];
  let fails=0;$("checks").innerHTML=C.map(([t,okk,kind])=>{if(!okk&&!kind)fails++;const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";return `<li><span>${t}</span><span class="pill ${cls}">${kind==="info"?"tip":okk?"pass":kind==="warn"?"check":"fail"}</span></li>`}).join("");
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // elevation
  const sv=$("elev");sv.innerHTML="";
  const H=Math.max(3.4,c.hb+0.6,c.eye+0.4),Wm=c.d+1.2,sc=Math.min(470/Wm,270/H),vbH=Math.round(H*sc+70),ox=50,oy=vbH-40,X=x=>ox+x*sc,Y=y=>oy-y*sc;sv.setAttribute("viewBox","0 0 580 "+vbH);
  // height bands on the wall
  const wx=X(c.d);[[1.015,1.778,1],[1.778,3.048,2],[3.048,H,3]].forEach(([a,b,n])=>{if(a>=H)return;const bb=Math.min(b,H);
    el("rect",{x:fmt(wx,1),y:fmt(Y(bb),1),width:14,height:fmt(Math.max(0,(bb-a)*sc),1),fill:n===c.band?red:rule,opacity:n===c.band?.5:.7},sv)});
  el("line",{x1:ox-20,y1:oy,x2:570,y2:oy,stroke:ink,"stroke-width":2},sv);
  el("line",{x1:wx,y1:oy,x2:wx,y2:Y(H),stroke:ink,"stroke-width":2.4},sv);
  // person
  const e=c.eye,px=X(0),s=e/1.6;
  el("circle",{cx:px,cy:fmt(Y(e+0.02*s),1),r:fmt(Math.max(3,0.11*s*sc),1),fill:"none",stroke:ink,"stroke-width":1.6},sv);
  el("line",{x1:px,y1:fmt(Y(e-0.1*s),1),x2:px,y2:fmt(Y(e*0.5),1),stroke:ink,"stroke-width":1.6},sv);
  el("line",{x1:px,y1:fmt(Y(e*0.5),1),x2:fmt(px-0.12*sc,1),y2:oy,stroke:ink,"stroke-width":1.6},sv);
  el("line",{x1:px,y1:fmt(Y(e*0.5),1),x2:fmt(px+0.12*sc,1),y2:oy,stroke:ink,"stroke-width":1.6},sv);
  // sign
  const sh=Math.max(c.mm/1000*1.6,0.05),sx=wx-6;
  el("rect",{x:fmt(sx-4,1),y:fmt(Y(c.hb+sh),1),width:8,height:fmt(Math.max(2,sh*sc+4),1),fill:blue},sv);
  el("line",{x1:px,y1:fmt(Y(e),1),x2:fmt(sx-4,1),y2:fmt(Y(c.hb+c.mm/2000),1),stroke:red,"stroke-width":1.6,"stroke-dasharray":"7 4"},sv);
  el("text",{x:fmt(sx-12,1),y:fmt(Y(c.hb+sh)-8,1),"text-anchor":"end",fill:ink,"font-size":15,"font-family":F},sv,"sign · letters "+c.mm+" mm");
  el("text",{x:fmt(sx-12,1),y:fmt(Y(c.hb)+42,1),"text-anchor":"end",fill:ink2,"font-size":13,"font-family":F},sv,"baseline "+fmt(c.hb,2)+" m");
  el("text",{x:fmt(px+14,1),y:fmt(Y(e)+20,1),fill:red,"font-size":15,"font-family":F},sv,fmt(c.ang,1)+"° up · eye "+fmt(e,2)+" m");
  el("line",{x1:px,y1:oy+14,x2:wx,y2:oy+14,stroke:ink2},sv);
  el("text",{x:fmt((px+wx)/2,1),y:oy+27,"text-anchor":"middle",fill:ink2,"font-size":13,"font-family":F},sv,"viewing distance "+fmt(c.d,2)+" m");
  $("eLabel").textContent="band "+BANDS[c.band];
  // letters compared
  const lv=$("let");lv.innerHTML="";const items=[["ADA",c.mm,red],["Rule",c.rt,ink2]];if(c.cap>0)items.push(["Yours",c.cap,c.cap>=c.mm?ok:red]);
  const mx=Math.max(...items.map(i=>i[1]),1),k=110/mx;const txt=($("txt").value||"EXIT").trim().slice(0,24)||"EXIT";
  items.forEach(([n,v,col],i)=>{const x=20+i*95,h=Math.max(1,v*k);
    el("rect",{x,y:fmt(180-h,1),width:14,height:fmt(h,1),fill:col,opacity:.85},lv);
    el("text",{x:x+20,y:174,fill:ink,"font-size":fmt(Math.max(4,h/0.72),1),"font-family":"Barlow Condensed, Arial Narrow, sans-serif","font-weight":600},lv,(txt.match(/[A-Za-z0-9]/)||["E"])[0].toUpperCase());
    el("text",{x,y:200,fill:col,"font-size":12,"font-family":F},lv,n+" "+v+" mm")});
  el("line",{x1:10,y1:180,x2:290,y2:180,stroke:rule},lv);
  el("text",{x:10,y:215,fill:ink2,"font-size":10,"font-family":F},lv,"“"+txt+"” · cap height drawn to one scale");
  // table
  const D=[2,4,6,8,10,12,15,20,25,30];if(!D.some(v=>Math.abs(v-c.d)<1e-6))D.push(+c.d.toFixed(2));D.sort((a,b)=>a-b);
  $("tb").innerHTML=D.map(dd=>{const di=dd/0.0254,v=[60,100,140].map(h=>Math.ceil(ada(h,di).h*25.4));const now=Math.abs(dd-c.d)<1e-6;
    return `<tr${now?' class="now"':""}><td>${fmt(dd,dd%1?2:0)} m</td><td>${v[0]}</td><td>${v[1]}</td><td>${v[2]}</td><td>${Math.ceil(dd*c.rule)}</td></tr>`}).join("");
}
""")
