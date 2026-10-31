APP = dict(
slug="shelf-sag", title="Shelf Sag Check", h1="Shelf Sag Check",
sub="Pick the board, the span, the load and how the shelf is held. Get the sag now and after a few years, the longest span that passes, and the thickness you need, drawn on a live elevation.",
meta=[("Sheet","T-40"),("Method","Beam deflection, UDL"),("Units","mm, kg/m"),("By","@smart_tools_every_week")],
source="Sag of a uniform load: 5wL⁴/384EI on loose supports, wL⁴/384EI with both ends fully fixed, wL⁴/185EI per span over a middle support (standard beam formulas, e.g. Roark's Formulas for Stress and Strain). Typical stiffness E: MDF 3,000 MPa, particleboard 2,800, plywood 7,000, pine 8,500, red oak 12,500 (Engineering ToolBox / USDA Wood Handbook ranges; use your supplier's datasheet). Target 1.7 mm per metre of span (0.02 in per ft) and about 50% extra sag over time follow the Sagulator (woodbin.com). Books weigh about 30 to 60 kg per metre of shelf.",
inputs="""
      <label for="mat">Board
        <select id="mat">
          <option value="3000,750" selected>MDF · E 3,000 MPa</option>
          <option value="2800,650">Particleboard · E 2,800</option>
          <option value="7000,600">Plywood (face grain along span) · 7,000</option>
          <option value="8500,400">Pine, solid · 8,500</option>
          <option value="12500,700">Red oak, solid · 12,500</option>
          <option value="c">Custom</option>
        </select>
      </label>
      <div class="row">
        <label for="E">Stiffness E MPa<input id="E" type="number" step="100" value="3000"></label>
        <label for="rho">Density kg/m³<input id="rho" type="number" step="10" value="750"></label>
      </div>
      <div class="row">
        <label for="L">Clear span mm<input id="L" type="number" step="10" value="900"></label>
        <label for="t">Thickness mm<input id="t" type="number" step="1" value="18"></label>
      </div>
      <div class="row">
        <label for="D">Shelf depth mm<input id="D" type="number" step="10" value="300"></label>
        <label for="w">Load kg per m<input id="w" type="number" step="5" value="45"></label>
      </div>
      <label for="sup">Supports
        <select id="sup">
          <option value="ss" selected>Ends only, loose on pins or cleats</option>
          <option value="fx">Ends fully fixed (glued and screwed)</option>
          <option value="mid">Extra support in the middle</option>
        </select>
      </label>
      <div class="row">
        <label for="lh">Front lip height mm<input id="lh" type="number" step="5" value="0"></label>
        <label for="lt">Lip thickness mm<input id="lt" type="number" step="1" value="20"></label>
      </div>
      <div class="row">
        <label for="lim">Target mm per m<input id="lim" type="number" step="0.1" value="1.7"></label>
        <label for="cr">Creep, extra over time %<input id="cr" type="number" step="5" value="50"></label>
      </div>
      <p class="note">Load: paperbacks about 30 kg/m, a full row of hardbacks or files 45 to 60 kg/m, folded clothes 15 to 20, display items 10. The shelf's own weight is added. A solid-wood front lip (E 10,000 MPa, top flush with the shelf) stiffens it a lot. Fully fixed ends are rare in practice, so treat that case as a best case.</p>
""",
right="""
      <div class="readout">
        <div><b>Sag now</b><span id="oS" class="hi">–</span></div>
        <div><b>After a few years</b><span id="oL">–</span></div>
        <div><b>Allowed</b><span id="oA">–</span></div>
        <div><b>Longest span that passes</b><span id="oM">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Elevation <span id="elL"></span></h2><svg id="el" viewBox="0 0 600 300" role="img" aria-label="Shelf elevation with the sag drawn exaggerated"></svg></div>
        <div class="view"><h2>Section <span id="seL"></span></h2><svg id="se" viewBox="0 0 420 260" role="img" aria-label="Shelf cross-section with the front lip"></svg></div>
        <div class="view"><h2>Sag vs span <span id="chL"></span></h2><svg id="ch" viewBox="0 0 420 260" role="img" aria-label="Chart of sag against span"></svg></div>
      </div>
      <div class="data"><h2>Every board at this load <span id="dtL"></span></h2><div class="tablewrap"><table><thead><tr><th>Board</th><th>Sag at this span</th><th>Longest span</th><th>Thickness needed</th><th></th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css=".view.full svg{max-height:320px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const MATS=[["MDF",3000,750],["Particleboard",2800,650],["Plywood",7000,600],["Pine",8500,400],["Red oak",12500,700]];
const ELIP=10000,RHOLIP=700;
$("mat").addEventListener("input",()=>{const v=$("mat").value;if(v!=="c"){const [e,r]=v.split(",");$("E").value=e;$("rho").value=r}render()});
const KS={ss:5/384,fx:1/384,mid:1/185};
function EI(E,D,t,lh,lt){ // N·mm²; shelf rect D wide × t deep, lip lt wide × lh deep, tops flush
  const A1=D*t,y1=t/2,A2=lh>0?lt*lh:0,y2=lh/2;
  const yc=(E*A1*y1+ELIP*A2*y2)/(E*A1+ELIP*A2);
  return E*(D*t**3/12+A1*(y1-yc)**2)+(A2?ELIP*(lt*lh**3/12+A2*(y2-yc)**2):0);
}
function sag(p,L,t,E,rho){ // mm
  const wkg=p.w+rho*p.D*t*1e-9*1000+(p.lh>0?RHOLIP*p.lt*p.lh*1e-6:0); // kg/m
  const wN=wkg*9.81/1000; // N/mm
  const Ls=p.sup==="mid"?L/2:L;
  return {d:KS[p.sup]*wN*Ls**4/EI(E,p.D,t,p.lh,p.lt),wkg};
}
function maxSpan(p,t,E,rho){let lo=50,hi=6000;if(sag(p,lo,t,E,rho).d>p.lim*lo/1000)return 0;if(sag(p,hi,t,E,rho).d<=p.lim*hi/1000)return hi;
  for(let i=0;i<50;i++){const m=(lo+hi)/2;if(sag(p,m,t,E,rho).d<=p.lim*m/1000)lo=m;else hi=m}return lo}
function tNeed(p,E,rho){let lo=3,hi=200;if(sag(p,p.L,hi,E,rho).d>p.lim*p.L/1000)return Infinity;
  for(let i=0;i<50;i++){const m=(lo+hi)/2;if(sag(p,p.L,m,E,rho).d<=p.lim*p.L/1000)hi=m;else lo=m}return Math.ceil(hi)}
function calc(){
  const p={E:num("E",100,250000,3000),rho:num("rho",50,8000,750),L:num("L",100,3000,900),t:num("t",3,100,18),D:num("D",50,1200,300),
    w:num("w",0,300,45),sup:KS[$("sup").value]?$("sup").value:"ss",lh:num("lh",0,200,0),lt:num("lt",3,100,20),lim:num("lim",0.2,20,1.7),cr:num("cr",0,300,50)/100};
  const s=sag(p,p.L,p.t,p.E,p.rho);p.d=s.d;p.wkg=s.wkg;p.dl=s.d*(1+p.cr);p.allow=p.lim*p.L/1000;p.ok=p.d<=p.allow+1e-9;
  p.ms=maxSpan(p,p.t,p.E,p.rho);p.tn=tNeed(p,p.E,p.rho);return p;
}
function shape(p,x){ // normalised 0..1 deflection shape along the shelf (x 0..1)
  if(p.sup==="fx"){return 16*x*x*(1-x)*(1-x)}
  if(p.sup==="mid"){const u=x<=.5?x*2:(1-x)*2;const f=u*(1-3*u*u+2*u**3);return f/0.2600}
  return x*(1-2*x*x+x**3)/0.3125;
}
function render(){
  const p=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun"),ok=css("--ok"),bad=css("--bad");
  const M="IBM Plex Mono, monospace";
  $("oS").textContent=fmt(p.d,1)+" mm";$("oS").className=p.ok?"ok":"bad";
  $("oL").textContent=fmt(p.dl,1)+" mm";$("oA").textContent=fmt(p.allow,1)+" mm";
  $("oM").textContent=p.ms>=6000?"> 6 m":p.ms<50?"< 50 mm":Math.floor(p.ms/10)*10+" mm";
  // elevation
  const sv=$("el");sv.innerHTML="";const x0=50,x1=550,yT=150,th=Math.max(6,Math.min(26,p.t*0.9));
  const exg=Math.max(1,Math.min(40,70/Math.max(p.d,0.01)));
  el("rect",{x:x0-26,y:30,width:26,height:240,fill:sheet,stroke:ink,"stroke-width":2},sv);
  el("rect",{x:x1,y:30,width:26,height:240,fill:sheet,stroke:ink,"stroke-width":2},sv);
  if(p.sup==="mid")el("rect",{x:(x0+x1)/2-8,y:yT+th,width:16,height:120-th,fill:sheet,stroke:ink,"stroke-width":1.5},sv);
  const N=60,top=[],bot=[];for(let i=0;i<=N;i++){const x=i/N,X=x0+(x1-x0)*x,dy=shape(p,x)*p.d*exg;top.push(`${X.toFixed(1)},${(yT+dy).toFixed(1)}`);bot.unshift(`${X.toFixed(1)},${(yT+th+dy).toFixed(1)}`)}
  el("line",{x1:x0,y1:yT,x2:x1,y2:yT,stroke:ink2,"stroke-dasharray":"5 4"},sv);
  // books
  const nb=Math.max(0,Math.min(40,Math.round(p.w/45*18)));
  for(let i=0;i<nb;i++){const x=(i+0.5)/Math.max(nb,1),X=x0+(x1-x0)*x,dy=shape(p,x)*p.d*exg,bw=(x1-x0)/Math.max(nb,1)-2,bh=70+((i*37)%30);
    el("rect",{x:X-bw/2,y:yT+dy-bh,width:Math.max(1,bw),height:bh,fill:i%3?blue:sun,opacity:.35,stroke:ink2,"stroke-width":.8},sv)}
  el("polygon",{points:top.concat(bot).join(" "),fill:p.ok?ok:bad,opacity:.85,stroke:ink,"stroke-width":1.5},sv);
  const mx=p.sup==="mid"?0.2108:0.5,MX=x0+(x1-x0)*mx,md=shape(p,mx)*p.d*exg;
  el("line",{x1:MX,y1:yT,x2:MX,y2:yT+md,stroke:red,"stroke-width":2},sv);
  el("text",{x:MX+8,y:yT+th+md+22,fill:red,"font-size":14,"font-family":M},sv,`sag ${fmt(p.d,1)} mm (allowed ${fmt(p.allow,1)})`);
  el("line",{x1:x0,y1:285,x2:x1,y2:285,stroke:ink2},sv);
  for(const X of [x0,x1])el("line",{x1:X,y1:278,x2:X,y2:292,stroke:ink2},sv);
  el("text",{x:(x0+x1)/2,y:280,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":M},sv,`clear span ${Math.round(p.L)} mm`);
  $("elL").textContent=`sag drawn ×${Math.round(exg)} · load ${fmt(p.wkg,1)} kg/m incl. shelf`;
  // section
  const s2=$("se");s2.innerHTML="";const sc=Math.min(320/(p.D+(p.lh>0?p.lt:0)),140/Math.max(p.t,p.lh,1));const sx=40,sy=90;
  el("rect",{x:sx,y:sy,width:p.D*sc,height:p.t*sc,fill:sun,opacity:.45,stroke:ink,"stroke-width":1.5},s2);
  if(p.lh>0)el("rect",{x:sx+p.D*sc,y:sy,width:p.lt*sc,height:p.lh*sc,fill:blue,opacity:.5,stroke:ink,"stroke-width":1.5},s2);
  const A1=p.D*p.t,A2=p.lh>0?p.lt*p.lh:0,yc=(p.E*A1*p.t/2+ELIP*A2*p.lh/2)/(p.E*A1+ELIP*A2);
  el("line",{x1:sx-20,y1:sy+yc*sc,x2:sx+(p.D+(p.lh>0?p.lt:0))*sc+16,y2:sy+yc*sc,stroke:red,"stroke-dasharray":"6 4"},s2);
  el("text",{x:Math.min(410,sx+(p.D+(p.lh>0?p.lt:0))*sc+16),y:sy+yc*sc+18,"text-anchor":"end",fill:red,"font-size":12,"font-family":M},s2,"neutral axis");
  el("text",{x:sx,y:sy-14,fill:ink,"font-size":13,"font-family":M},s2,`${Math.round(p.D)} deep × ${Math.round(p.t)} thick`);
  if(p.lh>0)el("text",{x:sx,y:Math.min(250,sy+Math.max(p.t,p.lh)*sc+22),fill:ink2,"font-size":12,"font-family":M},s2,`+ lip ${Math.round(p.lt)} × ${Math.round(p.lh)} mm, E ${ELIP}`);
  const ei=EI(p.E,p.D,p.t,p.lh,p.lt),ei0=EI(p.E,p.D,p.t,0,p.lt);
  el("text",{x:sx,y:252,fill:ink2,"font-size":12,"font-family":M},s2,p.lh>0?`stiffness ×${fmt(ei/ei0,1)} with the lip`:"no lip: add one to stiffen");
  $("seL").textContent=`EI ${fmt(ei/1e9,2)} kN·m²`;
  // chart sag vs span
  const s3=$("ch");s3.innerHTML="";const cx0=50,cx1=400,cy0=220,cy1=20,Lmax=Math.max(600,Math.min(3000,Math.ceil(p.L*1.6/100)*100));
  const dmax=Math.max(p.lim*Lmax/1000*1.5,p.d*1.25,1);
  const X=L=>cx0+(cx1-cx0)*L/Lmax,Y=d=>cy0-(cy0-cy1)*Math.min(d,dmax)/dmax;
  el("line",{x1:cx0,y1:cy0,x2:cx1,y2:cy0,stroke:ink2},s3);el("line",{x1:cx0,y1:cy0,x2:cx0,y2:cy1,stroke:ink2},s3);
  const pts=[],lim=[];for(let i=1;i<=50;i++){const L=Lmax*i/50;pts.push(`${X(L).toFixed(1)},${Y(sag(p,L,p.t,p.E,p.rho).d).toFixed(1)}`);lim.push(`${X(L).toFixed(1)},${Y(p.lim*L/1000).toFixed(1)}`)}
  el("polyline",{points:lim.join(" "),fill:"none",stroke:ok,"stroke-width":2,"stroke-dasharray":"6 4"},s3);
  el("polyline",{points:pts.join(" "),fill:"none",stroke:red,"stroke-width":2.5},s3);
  el("circle",{cx:X(p.L),cy:Y(p.d),r:6,fill:p.ok?ok:bad},s3);
  if(p.ms>50&&p.ms<Lmax){el("line",{x1:X(p.ms),y1:cy0,x2:X(p.ms),y2:Y(p.lim*p.ms/1000),stroke:ok},s3);el("text",{x:X(p.ms)+4,y:cy0-6,fill:ok,"font-size":11,"font-family":M},s3,Math.floor(p.ms/10)*10+" mm")}
  el("text",{x:cx1,y:246,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":M},s3,`span to ${Lmax} mm`);
  el("text",{x:cx0+6,y:cy1+10,fill:ink2,"font-size":11,"font-family":M},s3,`sag (to ${fmt(dmax,0)} mm)`);
  el("text",{x:cx0+6,y:cy1+26,fill:ok,"font-size":11,"font-family":M},s3,"- - target "+fmt(p.lim,1)+" mm/m");
  $("chL").textContent=p.ok?"passes":"too much sag";
  // table
  $("tb").innerHTML=MATS.map(([n,E,r])=>{const s=sag(p,p.L,p.t,E,r).d,ms=maxSpan(p,p.t,E,r),tn=tNeed(p,E,r),okk=s<=p.allow;
    return `<tr${Math.abs(E-p.E)<1&&Math.abs(r-p.rho)<1?' class="now"':''}><td>${n} ${Math.round(p.t)} mm</td><td class="${okk?'ok':'bad'}">${fmt(s,1)} mm</td><td>${ms>=6000?'> 6000':Math.floor(ms/10)*10} mm</td><td>${Number.isFinite(tn)?tn+' mm':'> 200 mm'}</td><td><span class="pill ${okk?'ok':'bad'}">${okk?'pass':'sags'}</span></td></tr>`}).join("");
  $("dtL").textContent=`${Math.round(p.w)} kg/m · ${Math.round(p.L)} mm span · ${$("sup").selectedOptions[0]?$("sup").selectedOptions[0].text.split(",")[0]:""}`;
}
""")
