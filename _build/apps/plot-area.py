APP = dict(
slug="plot-area", title="Plot Area from Sides", h1="Plot Area from Sides",
sub="Enter the four sides of a plot and one diagonal, as measured on site. Get the true area from two triangles, the plot drawn to scale, every corner angle, and how far the 'average of opposite sides' shortcut is off.",
meta=[("Sheet","T-43"),("Method","Two triangles · Heron"),("Units","m, ft, sq ft, guntha"),("By","@smart_tools_every_week")],
source="Area = sum of two triangles, each by Heron's formula A = √(s(s−a)(s−b)(s−c)), s = half the perimeter (first-principles geometry). Corner angles by the cosine rule. Assumes a convex four-sided plot with B and D on opposite sides of diagonal AC. 1 ft = 0.3048 m (exact); 1 sq yd = 0.83612736 m²; 1 guntha = 1,089 sq ft; 1 cent = 435.6 sq ft; 1 acre = 43,560 sq ft; 1 ha = 10,000 m². For legal area, rely on a licensed survey.",
inputs="""
      <label for="un">Units of the tape
        <select id="un"><option value="m" selected>Metres</option><option value="ft">Feet</option></select>
      </label>
      <div class="row">
        <label for="ab">Side AB (front)<input id="ab" type="number" step="0.1" value="18"></label>
        <label for="bc">Side BC<input id="bc" type="number" step="0.1" value="30"></label>
      </div>
      <div class="row">
        <label for="cd">Side CD (rear)<input id="cd" type="number" step="0.1" value="14"></label>
        <label for="da">Side DA<input id="da" type="number" step="0.1" value="32"></label>
      </div>
      <div class="row">
        <label for="ac">Diagonal AC<input id="ac" type="number" step="0.1" value="29"></label>
        <label for="bd">Diagonal BD (check, 0 = none)<input id="bd" type="number" step="0.1" value="0"></label>
      </div>
      <label for="rate">Land rate per sq ft (optional)<input id="rate" type="number" step="100" value="0"></label>
      <p class="note">Walk round the plot A → B → C → D. Measure the four sides and the diagonal from A to C. If you also tape B to D, the tool checks how well your measurements close.</p>
""",
right="""
      <div class="readout">
        <div><b>True area</b><span id="oA" class="hi">–</span></div>
        <div><b>In sq ft</b><span id="oF">–</span></div>
        <div><b>Average-of-sides</b><span id="oG">–</span></div>
        <div><b>Shortcut error</b><span id="oE">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Plot to scale <span id="pLabel"></span></h2><svg id="plan" viewBox="0 0 560 400" role="img" aria-label="Plot drawn to scale from the measured sides"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Working <span>Heron</span></h2><ul class="checks" id="work"></ul></div>
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="data"><h2>Area in every unit <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Unit</th><th>True area</th><th>Average-of-sides</th><th>Difference</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function heron(a,b,c){const s=(a+b+c)/2,v=s*(s-a)*(s-b)*(s-c);return {s,A:v>0?Math.sqrt(v):0,ok:v>0}}
function apex(base,dA,dC,side){ // point at dA from (0,0) and dC from (base,0); side -1 below, +1 above
  const x=(dA*dA-dC*dC+base*base)/(2*base),r=dA*dA-x*x;return {x,y:side*Math.sqrt(Math.max(0,r)),ok:r>0}}
const ang=(p,q,r)=>{const ux=q.x-p.x,uy=q.y-p.y,vx=r.x-p.x,vy=r.y-p.y;const l=Math.hypot(ux,uy)*Math.hypot(vx,vy);return l>0?Math.acos(Math.max(-1,Math.min(1,(ux*vx+uy*vy)/l)))*180/Math.PI:0};
function calc(){
  const ft=$("un").value==="ft",k=ft?0.3048:1,mx=ft?3000:1000;
  const AB=num("ab",0.1,mx,18)*k,BC=num("bc",0.1,mx,30)*k,CD=num("cd",0.1,mx,14)*k,DA=num("da",0.1,mx,32)*k,AC=num("ac",0.1,mx,29)*k,BDm=num("bd",0,mx,0)*k,rate=num("rate",0,1e7,0);
  const t1=heron(AB,BC,AC),t2=heron(CD,DA,AC),A=t1.A+t2.A,ok=t1.ok&&t2.ok;
  const P={A:{x:0,y:0},C:{x:AC,y:0}};P.B=apex(AC,AB,BC,-1);P.D=apex(AC,DA,CD,1);
  const BD=Math.hypot(P.B.x-P.D.x,P.B.y-P.D.y);
  const angA=ang(P.A,P.B,P.C)+ang(P.A,P.C,P.D),angC=ang(P.C,P.B,P.A)+ang(P.C,P.A,P.D),angB=ang(P.B,P.A,P.C),angD=ang(P.D,P.C,P.A);
  const G=(AB+CD)/2*(BC+DA)/2,err=A>0?(G/A-1)*100:0;
  return {ft,k,AB,BC,CD,DA,AC,BDm,BD,t1,t2,A,ok,P,angA,angB,angC,angD,G,err,rate,convex:angA<180&&angC<180};
}
const SQFT=0.09290304;
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet");
  const u=c.ft?"ft":"m",L=v=>fmt(v/c.k,2)+" "+u;
  $("oA").textContent=c.ok?fmt(c.A,1)+" m²":"no close";
  $("oF").textContent=c.ok?Math.round(c.A/SQFT).toLocaleString("en-IN"):"–";
  $("oG").textContent=fmt(c.G,1)+" m²";
  $("oE").textContent=c.ok?(c.err>=0?"+":"")+fmt(c.err,1)+"%":"–";$("oE").className=c.ok&&Math.abs(c.err)>2?"bad":"";
  // working
  const W=[[`Triangle ABC: s = ${fmt(c.t1.s/c.k,2)} ${u}`,`${fmt(c.t1.A,2)} m²`],[`Triangle ACD: s = ${fmt(c.t2.s/c.k,2)} ${u}`,`${fmt(c.t2.A,2)} m²`],
    ["True area = ABC + ACD",`${fmt(c.A,2)} m²`],[`Shortcut: (AB+CD)/2 × (BC+DA)/2`,`${fmt(c.G,2)} m²`]];
  $("work").innerHTML=W.map(([a,b])=>`<li><span>${a}</span><span style="font-family:var(--mono)">${b}</span></li>`).join("");
  const C=[[c.t1.ok?"Sides AB, BC and diagonal AC make a triangle":"AB + BC must be longer than AC: re-measure",c.t1.ok],
    [c.t2.ok?"Sides CD, DA and diagonal AC make a triangle":"CD + DA must be longer than AC: re-measure",c.t2.ok],
    [c.convex?"All corners under 180°, plot is convex":"A corner is over 180°: this method needs a convex plot, add another diagonal",c.convex],
    c.BDm>0?[`Measured BD ${L(c.BDm)} vs drawn ${L(c.BD)}: ${fmt(Math.abs(c.BDm-c.BD)/c.k,2)} ${u} off`,Math.abs(c.BDm-c.BD)<=Math.max(0.05,0.005*c.BD)]:["Tape B to D too, to check the measurements close",true,"info"]];
  let fails=0;$("checks").innerHTML=C.map(([t,okk,kind])=>{if(!okk)fails++;const cls=kind?"warn":okk?"ok":"bad";return `<li><span>${t}</span><span class="pill ${cls}">${kind?"tip":okk?"pass":"fail"}</span></li>`}).join("");
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // plan: rotate so AB runs left to right along the bottom
  const sv=$("plan");sv.innerHTML="";
  const th=Math.atan2(c.P.B.y-c.P.A.y,c.P.B.x-c.P.A.x),R=p=>({x:p.x*Math.cos(-th)-p.y*Math.sin(-th),y:p.x*Math.sin(-th)+p.y*Math.cos(-th)});
  const Q={A:R(c.P.A),B:R(c.P.B),C:R(c.P.C),D:R(c.P.D)},xs=Object.values(Q).map(p=>p.x),ys=Object.values(Q).map(p=>p.y);
  const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys),sc=Math.min(400/Math.max(1e-6,x1-x0),270/Math.max(1e-6,y1-y0));
  const ox=80+(400-(x1-x0)*sc)/2,oy=45+(270+(y1-y0)*sc)/2,X=p=>ox+(p.x-x0)*sc,Y=p=>oy-(p.y-y0)*sc;
  const pts=k=>k.map(n=>`${fmt(X(Q[n]),1)},${fmt(Y(Q[n]),1)}`).join(" ");
  el("polygon",{points:pts(["A","B","C"]),fill:blue,opacity:.16},sv);el("polygon",{points:pts(["A","C","D"]),fill:red,opacity:.12},sv);
  el("polygon",{points:pts(["A","B","C","D"]),fill:"none",stroke:ink,"stroke-width":2.4},sv);
  el("line",{x1:X(Q.A),y1:Y(Q.A),x2:X(Q.C),y2:Y(Q.C),stroke:ink2,"stroke-width":1.2,"stroke-dasharray":"6 4"},sv);
  if(c.BDm>0)el("line",{x1:X(Q.B),y1:Y(Q.B),x2:X(Q.D),y2:Y(Q.D),stroke:rule,"stroke-width":1,"stroke-dasharray":"2 4"},sv);
  const cx=(X(Q.A)+X(Q.B)+X(Q.C)+X(Q.D))/4,cy=(Y(Q.A)+Y(Q.B)+Y(Q.C)+Y(Q.D))/4,F="IBM Plex Mono, monospace";
  const side=(a,b,t)=>{const ax=X(Q[a]),ay=Y(Q[a]),bx=X(Q[b]),by=Y(Q[b]),mx=(ax+bx)/2,my=(ay+by)/2,l=Math.hypot(bx-ax,by-ay)||1;let nx=(by-ay)/l,ny=-(bx-ax)/l;if(nx*(mx-cx)+ny*(my-cy)<0){nx=-nx;ny=-ny}
    el("text",{x:fmt(mx+nx*12,1),y:fmt(my+ny*12+4+ny*6,1),"text-anchor":nx>0.5?"start":nx<-0.5?"end":"middle",fill:ink,"font-size":15,"font-family":F},sv,t)};
  side("A","B",L(c.AB));side("B","C",L(c.BC));side("C","D",L(c.CD));side("D","A",L(c.DA));
  const angs={A:c.angA,B:c.angB,C:c.angC,D:c.angD};
  const nb={A:["D","B"],B:["A","C"],C:["B","D"],D:["C","A"]};
  ["A","B","C","D"].forEach(n=>{const x=X(Q[n]),y=Y(Q[n]),dx=x-cx,dy=y-cy,l=Math.hypot(dx,dy)||1;el("circle",{cx:fmt(x,1),cy:fmt(y,1),r:4,fill:red},sv);
    const t=el("text",{x:fmt(x+dx/l*14+(dx>=0?6:-6),1),y:fmt(y+dy/l*22+6,1),"text-anchor":dx>=0?"start":"end","font-family":F},sv);
    const a=document.createElementNS(NS,"tspan");a.setAttribute("fill",red);a.setAttribute("font-size",18);a.setAttribute("font-weight",600);a.textContent=n+" ";t.appendChild(a);
    const b=document.createElementNS(NS,"tspan");b.setAttribute("fill",ink2);b.setAttribute("font-size",13);b.textContent=fmt(angs[n],1)+"°";t.appendChild(b);
});
  const mA=R({x:(c.P.A.x+c.P.B.x+c.P.C.x)/3,y:(c.P.A.y+c.P.B.y+c.P.C.y)/3}),mD=R({x:(c.P.A.x+c.P.C.x+c.P.D.x)/3,y:(c.P.A.y+c.P.C.y+c.P.D.y)/3});
  el("text",{x:fmt(X(mA),1),y:fmt(Y(mA),1),"text-anchor":"middle",fill:blue,"font-size":15,"font-family":F},sv,fmt(c.t1.A,1)+" m²");
  el("text",{x:fmt(X(mD),1),y:fmt(Y(mD),1),"text-anchor":"middle",fill:red,"font-size":15,"font-family":F},sv,fmt(c.t2.A,1)+" m²");
  el("text",{x:20,y:388,fill:ink2,"font-size":13,"font-family":F},sv,"diagonal AC "+L(c.AC)+" · drawn to scale, AB at the bottom");
  $("pLabel").textContent=fmt(c.A,1)+" m² · "+Math.round(c.A/SQFT).toLocaleString("en-IN")+" sq ft";
  // table
  const U=[["m²",1],["sq ft",SQFT],["sq yd (gaj)",0.83612736],["guntha",1089*SQFT],["cent",435.6*SQFT],["acre",43560*SQFT],["hectare",10000]];
  $("tb").innerHTML=U.map(([n,f])=>{const d=f>=1000?4:f>=40?3:f>=1?1:0;return `<tr${n==="sq ft"?' class="now"':""}><td>${n}</td><td>${(c.A/f).toLocaleString("en-IN",{maximumFractionDigits:d,minimumFractionDigits:d})}</td><td>${(c.G/f).toLocaleString("en-IN",{maximumFractionDigits:d,minimumFractionDigits:d})}</td><td class="${c.G>c.A*1.02?"bad":""}">${((c.G-c.A)/f).toLocaleString("en-IN",{maximumFractionDigits:d,minimumFractionDigits:d})}</td></tr>`}).join("")+
    (c.rate>0?`<tr><td>Value at rate</td><td>₹ ${Math.round(c.A/SQFT*c.rate).toLocaleString("en-IN")}</td><td>₹ ${Math.round(c.G/SQFT*c.rate).toLocaleString("en-IN")}</td><td class="bad">₹ ${Math.round((c.G-c.A)/SQFT*c.rate).toLocaleString("en-IN")}</td></tr>`:"");
  $("dLabel").textContent=c.ok?"shortcut "+(c.err>=0?"+":"")+fmt(c.err,1)+"%":"sides do not close";
}
""")
