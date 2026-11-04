APP = dict(
slug="slope-contour", title="Slope & Contour", h1="Slope & Contour",
sub="Measure the gap between contours on your survey and get the real slope in %, degrees and 1 in n, the true length along the ground, and how far apart contours must be for any slope you want to design.",
meta=[("Sheet","T-49"),("Method","Rise ÷ run"),("Units","m, mm, %"),("By","@smart_tools_every_week")],
source="Slope = rise ÷ horizontal run (first principles). % = 100 × rise/run; angle = atan(rise/run); 1 in n = run/rise; ground distance = map distance × scale; true length = √(run² + rise²). 100% = 45°. The 1:12 (8.33%) ramp limit is ADA 2010 §405.2; other limits depend on your local code.",
inputs="""
      <div class="row">
        <label for="h">Contour interval m<input id="h" type="number" step="0.25" value="1"></label>
        <label for="N">Map scale 1 :<input id="N" type="number" step="50" value="500"></label>
      </div>
      <div class="row">
        <label for="d">Map distance mm<input id="d" type="number" step="0.5" value="4"></label>
        <label for="n">Contours crossed<input id="n" type="number" step="1" value="1"></label>
      </div>
      <p class="note">Measure on the print, square to the contours. "Contours crossed" is how many intervals the measured line climbs (1 = between two neighbouring contours).</p>
      <label for="b0">Lowest contour level m<input id="b0" type="number" step="0.5" value="100"></label>
      <label for="tg">Target slope %<input id="tg" type="number" step="0.5" value="8.33"></label>
      <p class="note">Target slope gives the contour spacing you must draw on the grading plan. 8.33% = 1 in 12, the ADA 2010 ramp limit.</p>
""",
right="""
      <div class="readout">
        <div><b>Slope</b><span id="oP" class="hi">–</span></div>
        <div><b>Angle</b><span id="oA">–</span></div>
        <div><b>Gradient</b><span id="oG">–</span></div>
        <div><b>Ground run</b><span id="oR">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Contour plan <span id="pLabel"></span></h2><svg id="plan" viewBox="0 0 580 300" role="img" aria-label="Contour lines with the measured distance"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Section <span>true proportion</span></h2><svg id="sec" viewBox="0 0 300 230" role="img" aria-label="Slope triangle with rise, run and angle"></svg></div>
        <div class="view"><h2>% vs degrees <span>100% = 45°</span></h2><svg id="dial" viewBox="0 0 300 230" role="img" aria-label="Protractor comparing percent and degrees"></svg></div>
      </div>
      <div class="data"><h2>Slope table <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Slope</th><th>Angle</th><th>1 in n</th><th>Contour gap on map</th><th>On ground</th><th>Note</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const DEG=180/Math.PI;
const oneIn=v=>Number.isFinite(v)?(v>=100?fmt(v,0):v>=10?fmt(v,1):fmt(v,2)):"–";
function calc(){
  const h=num("h",0.01,100,1),N=num("N",1,100000,500),d=num("d",0.1,5000,4),n=Math.round(num("n",1,200,1)),b0=num("b0",-1000,9000,100),tg=num("tg",0.1,1000,8.33);
  const run=d*N/1000,rise=n*h,s=rise/run,pct=s*100,ang=Math.atan(s)*DEG,one=run/rise,L=Math.hypot(run,rise),gap=d/n;
  const row=p=>{const g=h/(p/100);return {p,a:Math.atan(p/100)*DEG,one:100/p,map:g*1000/N,ground:g}};
  const base=[1,2,5,8.33,10,15,20,25,33.3,50,100,200].map(row);
  base.forEach(r=>{r.note=Math.abs(r.p-8.33)<1e-6?"1:12 ramp limit (ADA 2010)":r.p===100?"= 45°":r.p===50?"= 26.6°, not 45°":r.p===200?"= 63.4°":""});
  const cur=row(pct);cur.cur=true;cur.note="your measurement";const tgt=row(tg);tgt.tgt=true;tgt.note="target slope";
  const same=(a,b)=>Math.abs(a.p-b.p)<1e-3*Math.max(1,b.p);
  [cur,tgt].forEach(x=>{const m=base.find(r=>same(r,x));if(m&&m.note)x.note+=" · "+m.note});
  const rows=base.filter(r=>!same(r,cur)&&!same(r,tgt)).concat(same(cur,tgt)?[cur]:[cur,tgt]).sort((a,b)=>a.p-b.p);
  return {h,N,d,n,b0,tg,run,rise,s,pct,ang,one,L,gap,rows,tgt};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),F="IBM Plex Mono, monospace";
  $("oP").textContent=fmt(c.pct,c.pct<10?2:1)+"%";$("oA").textContent=fmt(c.ang,1)+"°";$("oG").textContent="1 in "+oneIn(c.one);$("oR").textContent=fmt(c.run,c.run<10?2:1)+" m";
  // plan: contours at true map spacing (scaled for screen)
  const pv=$("plan");pv.innerHTML="";
  const k=Math.min(24,440/c.d),gp=c.gap*k,x0=70,y0=40,y1=250;
  const cnt=Math.min(80,Math.ceil(500/Math.max(gp,1e-6))+1);
  const every=Math.max(1,Math.ceil(30/Math.max(gp,1e-6)));
  for(let i=-Math.min(cnt,Math.floor((x0-20)/Math.max(gp,0.5)));i<=cnt;i++){
    const x=x0+i*gp;if(x<20||x>565)continue;
    const main=i>=0&&i<=c.n,pth=`M${fmt(x,1)} ${y0} C ${fmt(x+gp*0.25+6,1)} ${y0+70}, ${fmt(x-gp*0.25-6,1)} ${y0+140}, ${fmt(x,1)} ${y1}`;
    el("path",{d:pth,fill:"none",stroke:main?blue:ink2,"stroke-width":main?2:1,opacity:main?1:.55},pv);
    if(i%every===0)el("text",{x:fmt(x,1),y:y0-8,"text-anchor":"middle",fill:main?blue:ink2,"font-size":12,"font-family":F},pv,fmt(c.b0+i*c.h,c.h%1?2:0));
  }
  const xa=x0,xb=x0+c.d*k,ym=y0+105;
  el("line",{x1:fmt(xa,1),y1:ym,x2:fmt(xb,1),y2:ym,stroke:red,"stroke-width":2.5},pv);
  [xa,xb].forEach(x=>el("circle",{cx:fmt(x,1),cy:ym,r:4,fill:red},pv));
  el("text",{x:fmt(Math.min(Math.max((xa+xb)/2,150),430),1),y:ym+26,"text-anchor":"middle",fill:red,"font-size":15,"font-family":F,"paint-order":"stroke",stroke:css("--sheet"),"stroke-width":5},pv,fmt(c.d,1)+" mm on map = "+fmt(c.run,2)+" m");
  el("text",{x:20,y:286,fill:ink2,"font-size":13,"font-family":F},pv,"1:"+c.N+" · interval "+c.h+" m · rise "+fmt(c.rise,2)+" m over "+c.n+" interval"+(c.n>1?"s":""));
  $("pLabel").textContent="slope "+fmt(c.pct,1)+"% · "+fmt(c.ang,1)+"°";
  // section
  const sv=$("sec");sv.innerHTML="";const kk=Math.min(220/c.run,160/c.rise),X0=40,Y0=200,rx=X0+c.run*kk,ry=Y0-c.rise*kk;
  el("line",{x1:20,y1:Y0,x2:290,y2:Y0,stroke:ink,"stroke-width":1.2},sv);
  el("polygon",{points:`${X0},${Y0} ${fmt(rx,1)},${Y0} ${fmt(rx,1)},${fmt(ry,1)}`,fill:blue,opacity:.18},sv);
  el("line",{x1:X0,y1:Y0,x2:fmt(rx,1),y2:fmt(ry,1),stroke:red,"stroke-width":2.5},sv);
  const m45=160;el("line",{x1:X0,y1:Y0,x2:X0+m45,y2:Y0-m45,stroke:ink2,"stroke-dasharray":"4 4"},sv);
  el("text",{x:X0+m45-4,y:Y0-m45-4,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":F},sv,"45° = 100%");
  const ar=30,ea=Math.atan(c.s);el("path",{d:`M${X0+ar} ${Y0} A ${ar} ${ar} 0 0 0 ${fmt(X0+ar*Math.cos(ea),1)} ${fmt(Y0-ar*Math.sin(ea),1)}`,fill:"none",stroke:red},sv);
  el("text",{x:X0+ar+6,y:Y0-6,fill:red,"font-size":13,"font-family":F},sv,fmt(c.ang,1)+"°");
  el("text",{x:fmt((X0+rx)/2,1),y:Y0+18,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":F},sv,"run "+fmt(c.run,2)+" m");
  el("text",{x:fmt(rx>190?rx-6:rx+6,1),y:fmt(Math.max((Y0+ry)/2,30),1),"text-anchor":rx>190?"end":"start",fill:ink,"font-size":13,"font-family":F,"paint-order":"stroke",stroke:css("--sheet"),"stroke-width":4},sv,"rise "+fmt(c.rise,2)+" m");
  el("text",{x:20,y:22,fill:ink2,"font-size":12,"font-family":F},sv,"true length "+fmt(c.L,2)+" m");
  // dial
  const dv=$("dial");dv.innerHTML="";const cx=40,cy=205,R=165;
  el("path",{d:`M${cx+R} ${cy} A ${R} ${R} 0 0 0 ${cx} ${cy-R}`,fill:"none",stroke:ink,"stroke-width":1.2},dv);
  el("line",{x1:cx,y1:cy,x2:cx+R,y2:cy,stroke:ink,"stroke-width":1.2},dv);el("line",{x1:cx,y1:cy,x2:cx,y2:cy-R,stroke:ink,"stroke-width":1.2},dv);
  for(let a=0;a<=90;a+=15){const t=a/DEG;el("line",{x1:fmt(cx+(R-8)*Math.cos(t),1),y1:fmt(cy-(R-8)*Math.sin(t),1),x2:fmt(cx+R*Math.cos(t),1),y2:fmt(cy-R*Math.sin(t),1),stroke:ink},dv);
    el("text",{x:fmt(cx+(R-22)*Math.cos(t),1),y:fmt(cy-(R-22)*Math.sin(t)+4,1),"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},dv,a+"°")}
  [10,25,50,100,200].forEach(p=>{const t=Math.atan(p/100);el("line",{x1:fmt(cx+R*Math.cos(t),1),y1:fmt(cy-R*Math.sin(t),1),x2:fmt(cx+(R+8)*Math.cos(t),1),y2:fmt(cy-(R+8)*Math.sin(t),1),stroke:blue,"stroke-width":2},dv);
    el("text",{x:fmt(cx+(R+11)*Math.cos(t),1),y:fmt(cy-(R+11)*Math.sin(t)+4,1),fill:blue,"font-size":11,"font-family":F},dv,p+"%")});
  const t=Math.atan(c.s);el("line",{x1:cx,y1:cy,x2:fmt(cx+(R-4)*Math.cos(t),1),y2:fmt(cy-(R-4)*Math.sin(t),1),stroke:red,"stroke-width":3},dv);
  el("text",{x:170,y:30,"text-anchor":"middle",fill:red,"font-size":14,"font-family":F},dv,fmt(c.pct,1)+"% = "+fmt(c.ang,1)+"°");
  el("text",{x:cx+6,y:cy+18,fill:ink2,"font-size":11,"font-family":F},dv,"blue = %, grey = degrees");
  // table
  $("tb").innerHTML=c.rows.map(r=>`<tr${r.cur?' class="now"':""}><td>${fmt(r.p,r.p<10?2:1)}%</td><td>${fmt(r.a,1)}°</td><td>1 in ${oneIn(r.one)}</td><td>${fmt(r.map,r.map<10?2:1)} mm</td><td>${fmt(r.ground,2)} m</td><td>${r.tgt?"<b>"+r.note+"</b>":r.note}</td></tr>`).join("");
  $("dLabel").textContent="contour gap for "+c.h+" m interval at 1:"+c.N;
}
""")
