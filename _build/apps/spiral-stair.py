APP = dict(
slug="spiral-stair", title="Spiral Staircase Geometry", h1="Spiral Staircase Geometry",
sub="Enter the floor height, the stair radius and the tread angle. Get the risers, the tread depth where you really walk, the clear width, the floor opening needed for headroom and the checks, on a live plan and unrolled section.",
meta=[("Sheet","T-34"),("Method","Geometry + walkline"),("Units","mm, degrees"),("By","@smart_tools_every_week")],
source="Geometry: riser = floor height ÷ number of risers; walkline tread depth = (pole radius + 305 mm) × tread angle in radians; 2R + T comfort rule (Blondel, textbook). Default limits follow IRC 2018 R311.7.10.1 for spiral stairs (clear width 660 mm, tread 190 mm at 12 in from the narrow edge, riser at most 241 mm, headroom 1982 mm), as quoted in a municipal residential stair guide. All limits are editable: check your own code (NBC 2016 Part 4 for egress stairs) and the manufacturer for a kit stair.",
inputs="""
      <div class="row">
        <label for="H">Floor to floor mm<input id="H" type="number" step="50" value="3000"></label>
        <label for="R">Outer radius mm<input id="R" type="number" step="25" value="1000"></label>
      </div>
      <div class="row">
        <label for="r0">Centre pole radius mm<input id="r0" type="number" step="5" value="75"></label>
        <label for="hr">Handrail intrusion mm<input id="hr" type="number" step="5" value="50"></label>
      </div>
      <div class="row">
        <label for="rt">Target riser mm<input id="rt" type="number" step="5" value="200"></label>
        <label for="th">Tread angle °<input id="th" type="number" step="0.5" value="30"></label>
      </div>
      <div class="row">
        <label for="sl">Slab thickness mm<input id="sl" type="number" step="10" value="150"></label>
        <label for="tk">Tread thickness mm<input id="tk" type="number" step="5" value="40"></label>
      </div>
      <div class="row">
        <label for="dir">Climbing direction
          <select id="dir"><option value="1" selected>Clockwise</option><option value="-1">Anticlockwise</option></select>
        </label>
        <label for="wo">Walkline from pole mm<input id="wo" type="number" step="5" value="305"></label>
      </div>
      <div class="row">
        <label for="lw">Min clear width mm<input id="lw" type="number" step="10" value="660"></label>
        <label for="lt">Min walkline tread mm<input id="lt" type="number" step="5" value="190"></label>
      </div>
      <div class="row">
        <label for="lr">Max riser mm<input id="lr" type="number" step="1" value="241"></label>
        <label for="lh">Min headroom mm<input id="lh" type="number" step="10" value="1982"></label>
      </div>
      <p class="note">Walkline is where people actually put their feet, 305 mm (12 in) out from the narrow edge. A spiral tread is a wedge, so the width you can use depends on where you measure. Limits are editable: set them to your own code.</p>
""",
right="""
      <div class="readout">
        <div><b>Risers</b><span id="oN" class="hi">–</span></div>
        <div><b>Tread at walkline</b><span id="oT">–</span></div>
        <div><b>Clear width</b><span id="oW">–</span></div>
        <div><b>Opening sweep</b><span id="oO">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Plan <span id="pLabel"></span></h2><svg id="pl" viewBox="0 0 400 400" role="img" aria-label="Spiral stair plan" style="max-height:420px"></svg></div>
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Unrolled section <span id="uLabel"></span></h2><svg id="un" viewBox="0 0 560 250" role="img" aria-label="Unrolled elevation of the stair"></svg></div>
      </div>
      <div class="data"><h2>Tread schedule <span>mm</span></h2><div class="tablewrap"><table><thead><tr><th>Tread</th><th>Top level</th><th>Walkline depth</th><th>Outer depth</th><th>Headroom</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function calc(){
  const H=num("H",1500,6000,3000),r0=num("r0",0,300,75),R0=num("R",500,2000,1000),R=Math.max(R0,r0+200),hr=num("hr",0,150,50),
    rt=num("rt",120,260,200),th=num("th",10,60,30),sl=num("sl",0,600,150),tk=num("tk",0,100,40),dir=+$("dir").value===-1?-1:1,
    wo=num("wo",100,600,305),lw=num("lw",300,1500,660),lt=num("lt",50,400,190),lr=num("lr",100,400,241),lh=num("lh",1500,2500,1982);
  const N=Math.max(2,Math.round(H/rt)),riser=H/N,T=N-1,thr=th*Math.PI/180,total=T*th;
  const rw=Math.min(R-20,r0+wo),walk=rw*thr,outer=R*thr,narrow=r0*thr;
  const clear=R-r0-hr,soffit=H-sl;
  const rows=[];let jmin=T;
  for(let i=0;i<T;i++){const top=(i+1)*riser,hd=soffit-top;rows.push({i,top,walk,outer,hd});}
  for(let i=0;i<T;i++){if(rows[i].hd<lh){jmin=i;break}}
  const openAng=(T-jmin)*th,tpt=360/th,between=riser*tpt-tk;
  return {H,R,r0,hr,rt,th,thr,sl,tk,dir,wo,lw,lt,lr,lh,N,riser,T,total,rw,walk,outer,narrow,clear,soffit,rows,jmin,openAng,tpt,between,blondel:2*riser+walk,
    lap:total>360};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun"),ok=css("--ok");
  $("oN").textContent=c.N+" × "+fmt(c.riser,0)+" mm";$("oT").textContent=fmt(c.walk,0)+" mm";$("oW").textContent=fmt(c.clear,0)+" mm";
  $("oO").textContent=fmt(c.openAng,0)+"°";
  $("oT").className=c.walk<c.lt?"bad":"";$("oW").className=c.clear<c.lw?"bad":"";
  const C=[[`Riser ${fmt(c.riser,0)} mm is at most ${fmt(c.lr,0)} mm`,c.riser<=c.lr],
   [`Tread at the walkline ${fmt(c.walk,0)} mm is at least ${fmt(c.lt,0)} mm (needs ${fmt(Math.ceil(c.lt/c.rw*180/Math.PI*10)/10,1)}° at this radius)`,c.walk>=c.lt],
   [`Clear width ${fmt(c.clear,0)} mm is at least ${fmt(c.lw,0)} mm`,c.clear>=c.lw],
   [c.lap?`Headroom between turns ${fmt(c.between,0)} mm is at least ${fmt(c.lh,0)} mm`:`Less than one full turn: no tread sits above another`,!c.lap||c.between>=c.lh],
   [`Comfort 2R + T = ${fmt(c.blondel,0)} mm (aim for about 600 to 650)`,c.blondel>=590&&c.blondel<=660,"warn"],
   [`Floor opening sweeps ${fmt(c.openAng,0)}° of the circle (${c.T-c.jmin} treads) for ${fmt(c.lh,0)} mm headroom`,true,"info"]];
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // plan
  const pl=$("pl");pl.innerHTML="";const cx=200,cy=200,s=165/c.R,d=c.dir;
  const P=(r,a)=>[cx+r*s*Math.cos(a),cy+r*s*Math.sin(a)];
  const a0=-Math.PI/2;
  const wedge=(i,j,ra,rb,extra)=>{const A=a0+d*i*c.thr,B=a0+d*j*c.thr,p1=P(ra,A),p2=P(rb,A),p3=P(rb,B),p4=P(ra,B);const lg=Math.abs(B-A)>Math.PI?1:0,sw=d>0?1:0;
    return `M ${p1[0]} ${p1[1]} L ${p2[0]} ${p2[1]} A ${rb*s} ${rb*s} 0 ${lg} ${sw} ${p3[0]} ${p3[1]} L ${p4[0]} ${p4[1]} A ${ra*s} ${ra*s} 0 ${lg} ${1-sw} ${p1[0]} ${p1[1]} Z`};
  el("circle",{cx,cy,r:c.R*s,fill:"none",stroke:rule,"stroke-dasharray":"4 4"},pl);
  c.rows.forEach(r=>{const i=r.i;const hot=i>=c.jmin;
    el("path",{d:wedge(i,i+1,c.r0,c.R),fill:hot?sun:sheet,"fill-opacity":hot?.25:1,stroke:ink,"stroke-width":1.2},pl);
    const mid=a0+d*(i+.5)*c.thr,q=P(c.r0+(c.R-c.r0)*(i<c.tpt?.78:.5),mid);
    el("text",{x:q[0],y:q[1]+3,"text-anchor":"middle","font-size":c.th<18?8:10,fill:ink2,"font-family":"IBM Plex Mono, monospace"},pl,String(i+1));});
  el("circle",{cx,cy,r:c.rw*s,fill:"none",stroke:red,"stroke-dasharray":"3 3","stroke-width":1.4},pl);
  el("circle",{cx,cy,r:Math.max(c.r0*s,2),fill:ink,opacity:.85},pl);
  if(c.T-c.jmin>0&&c.openAng>0){const oa=Math.min(c.openAng,359.9);const A=a0+d*c.jmin*c.thr,B=A+d*oa*Math.PI/180,rr=(c.R+60)*s,rr2=(c.R+20)*s;
    const p1=[cx+rr2*Math.cos(A),cy+rr2*Math.sin(A)],p2=[cx+rr*Math.cos(A),cy+rr*Math.sin(A)],p3=[cx+rr*Math.cos(B),cy+rr*Math.sin(B)],p4=[cx+rr2*Math.cos(B),cy+rr2*Math.sin(B)];
    const lg=oa>180?1:0,sw=d>0?1:0;
    el("path",{d:`M ${p1[0]} ${p1[1]} L ${p2[0]} ${p2[1]} A ${rr} ${rr} 0 ${lg} ${sw} ${p3[0]} ${p3[1]} L ${p4[0]} ${p4[1]} A ${rr2} ${rr2} 0 ${lg} ${1-sw} ${p1[0]} ${p1[1]} Z`,fill:red,opacity:.35,stroke:red},pl);}
  el("text",{x:cx,y:392,"text-anchor":"middle","font-size":11,fill:ink2,"font-family":"IBM Plex Mono, monospace"},pl,"Ø "+fmt(c.R*2,0)+" mm · walkline Ø "+fmt(c.rw*2,0)+" mm (red dashed)");
  $("pLabel").textContent=c.T+" treads · "+fmt(c.total,0)+"° turn";
  // unrolled
  const un=$("un");un.innerHTML="";const ox=40,oy=20,W=500,Hh=190,sx=W/Math.max(c.total+c.th,1),sy=Hh/c.H;
  const X=a=>ox+a*sx,Y=h=>oy+Hh-h*sy;
  el("line",{x1:ox,y1:Y(0),x2:ox+W,y2:Y(0),stroke:ink,"stroke-width":2},un);
  el("line",{x1:ox,y1:Y(c.H),x2:ox+W,y2:Y(c.H),stroke:ink,"stroke-width":2},un);
  el("rect",{x:X(c.jmin*c.th),y:Y(c.H),width:Math.max(0,ox+W-X(c.jmin*c.th)),height:Math.max(0,c.sl*sy),fill:rule,opacity:.7},un);
  el("rect",{x:X(0),y:Y(c.H),width:Math.max(0,X(c.jmin*c.th)-X(0)),height:Math.max(0,c.sl*sy),fill:ink2,opacity:.6},un);
  let pts=`${X(0)},${Y(0)}`;
  c.rows.forEach(r=>{pts+=` ${X(r.i*c.th)},${Y(r.top)} ${X((r.i+1)*c.th)},${Y(r.top)}`;});
  el("polyline",{points:`${X(0)},${Y(0)} ${X(0)},${Y(c.rows[0]?c.rows[0].top:0)} `+pts.split(" ").slice(1).join(" "),fill:"none",stroke:blue,"stroke-width":2},un);
  const hx=X(Math.max(0,c.jmin-1)*c.th),hl=Math.min(c.lh,c.soffit-((Math.max(0,c.jmin-1))+1)*c.riser+c.lh);
  if(c.jmin>0&&c.jmin<=c.T){const lvl=c.jmin*c.riser;el("line",{x1:hx,y1:Y(lvl),x2:hx,y2:Y(lvl+c.lh),stroke:red,"stroke-width":2,"stroke-dasharray":"4 3"},un);
    el("text",{x:hx+6,y:Y(lvl+c.lh/2),fill:red,"font-size":11,"font-family":"IBM Plex Mono, monospace"},un,fmt(c.lh,0)+" clear");}
  el("text",{x:ox,y:oy+Hh+22,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},un,"turn 0° to "+fmt(c.total,0)+"° · dark = slab, light = opening");
  el("text",{x:ox+W,y:Y(c.H)-5,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},un,"upper floor +"+fmt(c.H,0));
  $("uLabel").textContent="riser "+fmt(c.riser,1)+" mm";
  const tb=$("tb");tb.innerHTML="";c.rows.forEach(r=>{const tr=document.createElement("tr");
    tr.innerHTML=`<td>${r.i+1}</td><td>${fmt(r.top,0)}</td><td class="${c.walk<c.lt?"bad":""}">${fmt(r.walk,0)}</td><td>${fmt(r.outer,0)}</td><td class="${r.hd<c.lh?"bad":""}">${r.hd<c.lh?"open above":fmt(r.hd,0)}</td>`;tb.appendChild(tr)});
}
""")
