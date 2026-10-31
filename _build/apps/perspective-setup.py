APP = dict(
slug="perspective-setup", title="Perspective Setup", h1="Perspective Setup",
sub="Set the building, eye height, station point and angle. Get the two vanishing points in millimetres on your sheet, the view angle, and the building drawn to scale, so no vanishing point lands off the paper.",
meta=[("Sheet","T-39"),("Method","Two-point perspective"),("Units","m, mm, °"),("By","@smart_tools_every_week")],
source="Plain projection geometry: the viewer stands at the station point, the picture plane is the paper, and a corner of the building touches it so that edge is true size. A point at plan (x, y) and height z projects to u = x·S ÷ (y + S), v = (z − E)·S ÷ (y + S). The vanishing points of walls turned θ and 90° − θ to the picture plane lie on the horizon at S ÷ tan θ and S × tan θ from the centre of vision. Keeping the subject inside a 60° cone of vision is the usual drawing rule; the cone angle is editable.",
inputs="""
      <div class="row">
        <label for="W">Building width, m<input id="W" type="number" step="0.5" value="8"></label>
        <label for="D">Building depth, m<input id="D" type="number" step="0.5" value="6"></label>
      </div>
      <div class="row">
        <label for="Hb">Building height, m<input id="Hb" type="number" step="0.5" value="7"></label>
        <label for="E">Eye height, m<input id="E" type="number" step="0.1" value="1.6"></label>
      </div>
      <div class="row">
        <label for="S">Station point distance, m<input id="S" type="number" step="0.5" value="15"></label>
        <label for="th">Angle of the long wall, °<input id="th" type="number" step="1" value="30"></label>
      </div>
      <div class="row">
        <label for="cx">Corner left or right of eye, m<input id="cx" type="number" step="0.5" value="0"></label>
        <label for="cone">Comfortable cone, °<input id="cone" type="number" step="5" value="60"></label>
      </div>
      <div class="row">
        <label for="sc">Drawing scale 1 :<input id="sc" type="number" step="10" value="100"></label>
        <label for="sw">Sheet width, mm<select id="sw"><option value="297,210">A4 · 297</option><option value="420,297" selected>A3 · 420</option><option value="594,420">A2 · 594</option><option value="841,594">A1 · 841</option></select></label>
      </div>
      <p class="note">The angle is between the long wall and the paper. The wall touching the paper is drawn at true size. Distances are on the ground; the eye height sets the horizon.</p>
""",
right="""
      <div class="readout">
        <div><b>Left vanishing point</b><span id="oL" class="hi">–</span></div>
        <div><b>Right vanishing point</b><span id="oR">–</span></div>
        <div><b>View angle</b><span id="oA">–</span></div>
        <div><b>On your sheet</b><span id="oF">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Your sheet at scale <span id="shLabel"></span></h2><svg id="sh" viewBox="0 0 960 400" role="img" aria-label="Sheet with horizon, vanishing points and the building in perspective"></svg></div>
        <div class="view"><h2>Plan <span id="plLabel"></span></h2><svg id="pl" viewBox="0 0 420 380" role="img" aria-label="Plan with picture plane, station point and cone of vision"></svg></div>
        <div class="view"><h2>Squeezed or comfortable? <span id="cnLabel"></span></h2><svg id="cn" viewBox="0 0 420 380" role="img" aria-label="View angle against the comfortable cone"></svg></div>
      </div>
      <div class="data"><h2>Where to mark it on the sheet <span id="sum"></span></h2><div class="tablewrap"><table><thead><tr><th>Point</th><th>Across from centre of vision</th><th>Up from horizon</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const RAD=Math.PI/180;
function calc(){
  const W=num("W",1,100,8),D=num("D",1,100,6),Hb=num("Hb",1,100,7),E=num("E",0.1,50,1.6),S=num("S",2,300,15);
  const th=num("th",5,85,30),cx=num("cx",-40,40,0),cone=num("cone",20,120,60),sc=num("sc",5,2000,100);
  const sp=$("sw").value.split(","),sw=+sp[0],sh=+sp[1];
  const t=th*RAD,C0=[cx,0],A=[cx+W*Math.cos(t),W*Math.sin(t)],B=[cx-D*Math.sin(t),D*Math.cos(t)],F=[A[0]-D*Math.sin(t),A[1]+D*Math.cos(t)];
  const mm=1000/sc,vpR=S/Math.tan(t),vpL=-S*Math.tan(t);
  const proj=(p,z)=>{const d=p[1]+S;return [p[0]*S/d,(z-E)*S/d]};
  const ang=[C0,A,B,F].map(p=>Math.atan2(p[0],p[1]+S)/RAD),view=Math.max(...ang)-Math.min(...ang);
  const span=(vpR-vpL)*mm,best=(sw-span)/2-vpL*mm,hz=Math.max(15,(sh-Hb*mm)/2)+E*mm;
  return {W,D,Hb,E,S,th,t,cx,cone,sc,sw,sh,C0,A,B,F,mm,vpR,vpL,proj,view,aMin:Math.min(...ang),aMax:Math.max(...ang),span,fits:span<=sw+1e-9,best,hz};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),ok=css("--ok"),bad=css("--bad"),sun=css("--sun");
  const wide=c.view>c.cone+1e-9;
  $("oL").textContent=fmt(-c.vpL*c.mm,0)+" mm left";$("oR").textContent=fmt(c.vpR*c.mm,0)+" mm right";
  $("oA").textContent=fmt(c.view,0)+"°";$("oA").className=wide?"bad":"ok";
  $("oF").textContent=c.fits?"Fits ("+fmt(c.span,0)+" of "+c.sw+" mm)":"Too wide: needs "+fmt(c.span,0)+" mm";$("oF").className=c.fits?"ok":"bad";
  const T=(sv,x,y,t,col,a,s)=>{const e=el("text",{x,y,fill:col||ink2,"font-size":s||12,"text-anchor":a||"start","font-family":"IBM Plex Mono, monospace"},sv,t);return e};
  // ---- sheet view
  const sv=$("sh");sv.innerHTML="";
  const cvx=c.best,xa=Math.min(0,cvx+c.vpL*c.mm)-30,xb=Math.max(c.sw,cvx+c.vpR*c.mm)+30,k=Math.min(900/(xb-xa),3.2),vh=Math.round(c.sh*k+60);
  sv.setAttribute("viewBox","0 0 960 "+vh);
  const ox=(960-(xb-xa)*k)/2,SX=x=>ox+(x-xa)*k,SY=y=>20+(c.sh-y)*k; // y: mm up from sheet bottom
  const P=(p,z)=>{const q=c.proj(p,z);return [SX(cvx+q[0]*c.mm),SY(c.hz+q[1]*c.mm)]};
  el("rect",{x:SX(0),y:SY(c.sh),width:c.sw*k,height:c.sh*k,fill:sheet,stroke:ink,"stroke-width":2},sv);
  el("line",{x1:SX(xa),y1:SY(c.hz),x2:SX(xb),y2:SY(c.hz),stroke:red,"stroke-width":1.4,"stroke-dasharray":"8 5"},sv);
  T(sv,SX(xa)+2,SY(c.hz)-5,"horizon",red);
  const vl=[SX(cvx+c.vpL*c.mm),SY(c.hz)],vr=[SX(cvx+c.vpR*c.mm),SY(c.hz)];
  // construction lines to near corner
  const nb=P(c.C0,0),nt=P(c.C0,c.Hb);
  [[vl,nb],[vl,nt],[vr,nb],[vr,nt]].forEach(s=>el("line",{x1:s[0][0],y1:s[0][1],x2:s[1][0],y2:s[1][1],stroke:ink2,"stroke-width":1,"stroke-dasharray":"3 4",opacity:.8},sv));
  // faces
  const faces=[],mid=(p,q)=>[(p[0]+q[0])/2,(p[1]+q[1])/2];
  const sides=[[c.C0,c.A,[Math.sin(c.t),-Math.cos(c.t)]],[c.B,c.F,[-Math.sin(c.t),Math.cos(c.t)]],[c.C0,c.B,[-Math.cos(c.t),-Math.sin(c.t)]],[c.A,c.F,[Math.cos(c.t),Math.sin(c.t)]]];
  const spt=[0,-c.S];
  sides.forEach(s=>{const m=mid(s[0],s[1]);if((spt[0]-m[0])*s[2][0]+(spt[1]-m[1])*s[2][1]>0)faces.push({p:s,d:Math.hypot(m[0]-spt[0],m[1]-spt[1])})});
  faces.sort((a,b)=>b.d-a.d);
  if(c.E>c.Hb){const poly=[c.C0,c.A,c.F,c.B].map(p=>P(p,c.Hb).join(",")).join(" ");el("polygon",{points:poly,fill:sun,opacity:.35,stroke:ink,"stroke-width":1.6},sv)}
  faces.forEach((f,i)=>{const a=f.p[0],b=f.p[1];const poly=[P(a,0),P(b,0),P(b,c.Hb),P(a,c.Hb)].map(q=>q.join(",")).join(" ");
    el("polygon",{points:poly,fill:blue,opacity:i%2?0.55:0.32,stroke:ink,"stroke-width":1.8},sv)});
  // true-size edge on picture plane
  const gl=P([c.cx,0],0),gt=P([c.cx,0],c.Hb);
  el("line",{x1:gl[0],y1:gl[1],x2:gt[0],y2:gt[1],stroke:ink,"stroke-width":3},sv);
  T(sv,gt[0]+6,gt[1]+12,"true height "+fmt(c.Hb*c.mm,0)+" mm",ink2);
  // CV and VPs
  el("line",{x1:SX(cvx)-6,y1:SY(c.hz),x2:SX(cvx)+6,y2:SY(c.hz),stroke:ink,"stroke-width":2},sv);el("line",{x1:SX(cvx),y1:SY(c.hz)-6,x2:SX(cvx),y2:SY(c.hz)+6,stroke:ink,"stroke-width":2},sv);
  T(sv,SX(cvx)+8,SY(c.hz)+16,"CV",ink2);
  [[vl,c.vpL*c.mm,"VP left"],[vr,c.vpR*c.mm,"VP right"]].forEach(v=>{
    const xs=cvx+v[1],inside=xs>=0&&xs<=c.sw;
    el("circle",{cx:v[0][0],cy:v[0][1],r:7,fill:inside?ok:bad},sv);
    T(sv,v[0][0],v[0][1]-14,v[2]+" "+fmt(Math.abs(v[1]),0)+" mm"+(inside?"":" · off the sheet"),inside?ok:bad,"middle",13)});
  T(sv,SX(0)+4,SY(c.sh)+14,c.sw+" × "+c.sh+" mm sheet",ink2);
  $("shLabel").textContent="1 : "+fmt(c.sc,0);
  // ---- plan
  const p=$("pl");p.innerHTML="";const pts=[c.C0,c.A,c.B,c.F,[0,-c.S]];
  const x0=Math.min(...pts.map(q=>q[0]))-2,x1=Math.max(...pts.map(q=>q[0]))+2,y0=Math.min(...pts.map(q=>q[1]))-1,y1=Math.max(...pts.map(q=>q[1]))+2;
  const pk=Math.min(380/(x1-x0),330/(y1-y0)),PX=x=>20+(x-x0)*pk,PY=y=>30+(y1-y)*pk;
  el("line",{x1:10,y1:PY(0),x2:410,y2:PY(0),stroke:red,"stroke-width":2},p);T(p,12,PY(0)-6,"picture plane (your paper)",red);
  const half=c.cone/2*RAD,ry=(y1+c.S)*0.0+Math.max(y1,1);
  [-1,1].forEach(sg=>el("line",{x1:PX(0),y1:PY(-c.S),x2:PX(sg*Math.tan(half)*(y1+c.S)),y2:PY(y1),stroke:sun,"stroke-width":1.4,"stroke-dasharray":"6 4"},p));
  el("polygon",{points:[c.C0,c.A,c.F,c.B].map(q=>PX(q[0])+","+PY(q[1])).join(" "),fill:blue,opacity:.4,stroke:ink,"stroke-width":2},p);
  [c.A,c.B,c.C0,c.F].forEach(q=>el("line",{x1:PX(0),y1:PY(-c.S),x2:PX(q[0]),y2:PY(q[1]),stroke:ink2,"stroke-width":1},p));
  el("circle",{cx:PX(0),cy:PY(-c.S),r:6,fill:ink},p);T(p,PX(0)+10,PY(-c.S)+4,"station point "+fmt(c.S,1)+" m",ink);
  el("circle",{cx:PX(c.C0[0]),cy:PY(0),r:4,fill:red},p);
  $("plLabel").textContent="wall at "+fmt(c.th,0)+"° and "+fmt(90-c.th,0)+"°";
  // ---- cone gauge
  const g=$("cn");g.innerHTML="";const cxm=210,cyb=330,R=290;
  const ang=a=>[cxm+R*Math.sin(a*RAD),cyb-R*Math.cos(a*RAD)];
  const half2=c.cone/2;
  el("path",{d:`M${cxm},${cyb} L${ang(-half2)[0]},${ang(-half2)[1]} A${R},${R} 0 0 1 ${ang(half2)[0]},${ang(half2)[1]} Z`,fill:ok,opacity:.12,stroke:ok,"stroke-dasharray":"6 4"},g);
  const a0=ang(c.aMin),a1=ang(c.aMax);
  el("path",{d:`M${cxm},${cyb} L${a0[0]},${a0[1]} A${R},${R} 0 0 1 ${a1[0]},${a1[1]} Z`,fill:wide?bad:blue,opacity:.45,stroke:wide?bad:blue,"stroke-width":2},g);
  el("line",{x1:cxm,y1:cyb,x2:cxm,y2:cyb-R,stroke:ink2,"stroke-dasharray":"2 5"},g);
  T(g,12,26,"building fills "+fmt(c.view,0)+"° of your view",wide?bad:ok,"start",14);
  T(g,12,46,"comfortable cone "+fmt(c.cone,0)+"°",ink2,"start",12);
  T(g,12,366,wide?"too wide: the edges will look stretched":"inside the cone: looks natural",wide?bad:ok,"start",13);
  $("cnLabel").textContent="";
  // ---- table
  const rows=[],f2=(n,q,z)=>{const r=c.proj(q,z);rows.push([n,fmt(r[0]*c.mm,1)+" mm",fmt(r[1]*c.mm,1)+" mm"])};
  rows.push(["Left vanishing point",fmt(c.vpL*c.mm,1)+" mm","0"]);rows.push(["Right vanishing point",fmt(c.vpR*c.mm,1)+" mm","0"]);
  f2("Near corner, base",c.C0,0);f2("Near corner, top",c.C0,c.Hb);f2("Right corner, base",c.A,0);f2("Right corner, top",c.A,c.Hb);f2("Left corner, base",c.B,0);f2("Left corner, top",c.B,c.Hb);f2("Far corner, base",c.F,0);f2("Far corner, top",c.F,c.Hb);
  rows.push(["Centre of vision on the sheet",fmt(c.best,0)+" mm from the left edge",fmt(c.hz,0)+" mm up from the bottom (horizon)"]);
  $("tb").innerHTML=rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join("");
  $("sum").textContent="at 1 : "+fmt(c.sc,0);
}
""")
