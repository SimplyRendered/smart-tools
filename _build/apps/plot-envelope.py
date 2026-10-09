APP = dict(
slug="plot-envelope", title="Plot Envelope & FAR", h1="Plot Envelope",
sub="How much can you really build on this plot? Setbacks, ground coverage, FAR and the height limit, all applied together, with the governing rule shown and a live 3D envelope.",
meta=[("Sheet","T-16"),("Rules","FAR · coverage · setbacks"),("Units","m / m²"),("By","@smart_tools_every_week")],
source="Definitions per NBC 2016 Part 3 (FAR = total covered area of all floors ÷ plot area; ground coverage = footprint ÷ plot area). Setbacks, coverage, FAR and height limits vary by city: enter your own Development Control Regulations. Height-by-road rule is a common DCR form; check yours.",
inputs="""
      <div class="row">
        <label for="W">Plot frontage m<input id="W" type="number" step="0.5" value="12"></label>
        <label for="D">Plot depth m<input id="D" type="number" step="0.5" value="20"></label>
      </div>
      <div class="row">
        <label for="sf">Front setback m<input id="sf" type="number" step="0.25" value="3"></label>
        <label for="sr">Rear setback m<input id="sr" type="number" step="0.25" value="1.5"></label>
      </div>
      <div class="row">
        <label for="sl">Side 1 m<input id="sl" type="number" step="0.25" value="1.5"></label>
        <label for="ss">Side 2 m<input id="ss" type="number" step="0.25" value="1.5"></label>
      </div>
      <div class="row">
        <label for="gc">Max ground coverage %<input id="gc" type="number" step="1" value="60"></label>
        <label for="far">FAR / FSI<input id="far" type="number" step="0.05" value="2"></label>
      </div>
      <label for="hmax">Max height m <span id="hv" class="time" style="font-size:18px"></span><input id="hmax" type="range" min="6" max="60" step="0.5" value="12"></label>
      <div class="row">
        <label for="ftf">Floor to floor m<input id="ftf" type="number" step="0.05" value="3.2"></label>
        <label for="stilt">Stilt parking
          <select id="stilt"><option value="0" selected>No stilt</option><option value="1">Stilt (not in FAR)</option></select>
        </label>
      </div>
      <div class="row">
        <label for="road">Road width m<input id="road" type="number" step="0.5" value="9"></label>
        <label for="rk">Height ≤ k × (road + front), k<input id="rk" type="number" step="0.1" value="1.5"></label>
      </div>
      <p class="note">FAR (FSI) caps the total floor area; ground coverage and setbacks cap the footprint; the height limit caps the number of floors. The smallest wins. Set k to 0 to switch the road-width rule off. Many DCRs exclude stilt parking, lift and stair cores or balconies from FAR: adjust the FAR if yours does.</p>
""",
right="""
      <div class="readout">
        <div><b>Buildable area</b><span id="oA" class="hi">–</span></div>
        <div><b>Floors</b><span id="oF">–</span></div>
        <div><b>Footprint</b><span id="oP">–</span></div>
        <div><b>FAR used</b><span id="oU">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Envelope <span id="axLabel"></span></h2><svg id="ax" viewBox="0 0 420 340" role="img" aria-label="Axonometric of the plot and building envelope"></svg></div>
        <div class="view"><h2>Plan <span id="planLabel"></span></h2><svg id="plan" viewBox="0 0 420 340" role="img" aria-label="Plot plan with setbacks and footprint"></svg></div>
      </div>
      <div class="data">
        <h2>Which rule governs <span id="gov"></span></h2>
        <ul class="checks" id="checks"></ul>
      </div>
      <div class="data" style="border-top:1px solid var(--rule)">
        <h2>Floor schedule <span>areas in m² and sq ft</span></h2>
        <div class="tablewrap"><table><thead><tr><th>Floor</th><th>Level m</th><th>Area m²</th><th>Area sq ft</th><th>Cumulative m²</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const SQFT=10.7639;
function env(){
  const W=num("W",3,500,12),D=num("D",3,500,20);
  const sf=num("sf",0,50,3),sr=num("sr",0,50,1.5),sl=num("sl",0,50,1.5),ss=num("ss",0,50,1.5);
  const gc=num("gc",1,100,60),far=num("far",0.1,20,2),hmax=num("hmax",3,300,12),ftf=num("ftf",2.4,6,3.2);
  const stilt=$("stilt").value==="1",road=num("road",0,200,9),rk=num("rk",0,10,1.5);
  const plot=W*D,bw=Math.max(0,W-sl-ss),bd=Math.max(0,D-sf-sr),buildable=bw*bd,cov=plot*gc/100;
  const foot=Math.min(buildable,cov),k=buildable>0?Math.sqrt(foot/buildable):0,fw=bw*k,fd=bd*k;
  const hRoad=rk>0?rk*(road+sf):Infinity,H=Math.min(hmax,hRoad);
  const stH=stilt?Math.min(ftf,H):0;
  const nH=foot>0?Math.min(100,Math.max(0,Math.floor((H-stH)/ftf+1e-9))):0;
  const farA=far*plot,full=foot>0?Math.min(nH,Math.floor(farA/foot+1e-9)):0;
  let part=0;if(full<nH&&foot>0)part=Math.max(0,farA-full*foot);
  const floors=[];for(let i=0;i<full;i++)floors.push(foot);if(part>0.01)floors.push(part);
  const bua=floors.reduce((s,a)=>s+a,0);
  let gov;if(foot<=0)gov="setbacks";else if(bua>=farA-0.01)gov="FAR";else gov=H<hmax?"road width":"height";
  return {W,D,sf,sr,sl,ss,gc,far,hmax,ftf,stilt,road,rk,plot,bw,bd,buildable,cov,foot,fw,fd,hRoad,H,stH,nH,farA,floors,bua,gov};
}
function render(){
  const e=env(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),ok=css("--ok"),paper=css("--paper"),sheet=css("--sheet");
  $("hv").textContent=fmt(e.hmax,1)+" m";
  $("oA").textContent=Math.round(e.bua).toLocaleString("en-IN")+" m²";
  $("oF").textContent=(e.stilt?"S + ":"")+e.floors.length+(e.floors.length&&e.floors[e.floors.length-1]<e.foot-0.01?" (part)":"");
  $("oP").textContent=fmt(e.foot,1)+" m²";
  $("oU").textContent=fmt(e.bua/e.plot,2)+" of "+(+e.far.toFixed(2));
  // AXONOMETRIC (x = frontage, y = depth, z = height)
  const sv=$("ax");sv.innerHTML="";
  const c=Math.cos(Math.PI/6),s=Math.sin(Math.PI/6);
  const topZ=e.stH+e.floors.length*e.ftf,Hdraw=Math.max(e.H,topZ);
  const spanX=(e.W+e.D)*c,spanY=(e.W+e.D)*s;
  const sc=Math.min(380/spanX,300/(spanY+Hdraw)),ox=20+e.D*c*sc+(380-spanX*sc)/2,oy=330-(spanY)*sc-6;
  const P=(x,y,z)=>[ox+(x-y)*c*sc,oy+(x+y)*s*sc-z*sc];
  const poly=(pts,attrs)=>el("polygon",Object.assign({points:pts.map(p=>p.join(",")).join(" ")},attrs),sv);
  poly([P(0,0,0),P(e.W,0,0),P(e.W,e.D,0),P(0,e.D,0)],{fill:paper,stroke:ink,"stroke-width":1.5});
  // setback line on ground
  const x0=e.sl,y0=e.D-e.sf-e.bd; // y=0 is the rear, y=D the road front
  poly([P(x0,y0,0),P(x0+e.bw,y0,0),P(x0+e.bw,y0+e.bd,0),P(x0,y0+e.bd,0)],{fill:"none",stroke:red,"stroke-dasharray":"4 3","stroke-width":1});
  // height limit ghost
  if(e.bw>0&&e.bd>0){const g=[[x0,y0],[x0+e.bw,y0],[x0+e.bw,y0+e.bd],[x0,y0+e.bd]];
    poly(g.map(p=>P(p[0],p[1],e.H)),{fill:"none",stroke:ink2,"stroke-dasharray":"2 4","stroke-width":1});
    [[x0+e.bw,y0],[x0+e.bw,y0+e.bd],[x0,y0+e.bd]].forEach(p=>el("line",{x1:P(p[0],p[1],0)[0],y1:P(p[0],p[1],0)[1],x2:P(p[0],p[1],e.H)[0],y2:P(p[0],p[1],e.H)[1],stroke:ink2,"stroke-dasharray":"2 4","stroke-width":1},sv));}
  // footprint centred in the buildable rectangle
  const fx=x0+(e.bw-e.fw)/2,fy=y0+(e.bd-e.fd)/2;
  const face=(pts,fill,op)=>{poly(pts,{fill:sheet,stroke:"none"});poly(pts,{fill,"fill-opacity":op,stroke:ink,"stroke-width":1})};
  const box=(z0,z1,depth,fill)=>{const a=fx,b=fy+e.fd-depth,w=e.fw,d=depth;
    face([P(a+w,b,z0),P(a+w,b+d,z0),P(a+w,b+d,z1),P(a+w,b,z1)],fill,.55);
    face([P(a,b+d,z0),P(a+w,b+d,z0),P(a+w,b+d,z1),P(a,b+d,z1)],fill,.8);
    face([P(a,b,z1),P(a+w,b,z1),P(a+w,b+d,z1),P(a,b+d,z1)],fill,.3);};
  if(e.foot>0){
    if(e.stilt){box(0,e.stH,e.fd,ink2);}
    e.floors.forEach((a,i)=>{const z0=e.stH+i*e.ftf;box(z0,z0+e.ftf,e.fd*a/e.foot,i===e.floors.length-1&&a<e.foot-0.01?sun:blue);});
  }
  const fr=P(e.W/2,e.D,0);el("text",{x:fr[0],y:Math.min(336,fr[1]+16),"text-anchor":"middle",fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},sv,"road "+fmt(e.road,1)+" m");
  const hp=P(x0,y0,e.H);el("text",{x:hp[0]+4,y:hp[1]-6,fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},sv,"limit "+fmt(e.H,1)+" m");
  $("axLabel").textContent=(e.stilt?"stilt + ":"")+e.floors.length+" floor"+(e.floors.length===1?"":"s")+" · "+fmt(topZ,1)+" m";
  // PLAN (road at the bottom)
  const pv=$("plan");pv.innerHTML="";const k=Math.min(330/e.W,260/e.D),px=(420-e.W*k)/2,py=24;
  const X=x=>px+x*k,Y=y=>py+y*k;
  el("rect",{x:X(0),y:Y(0),width:e.W*k,height:e.D*k,fill:paper,stroke:ink,"stroke-width":2},pv);
  if(e.bw>0&&e.bd>0)el("rect",{x:X(x0),y:Y(y0),width:e.bw*k,height:e.bd*k,fill:"none",stroke:red,"stroke-dasharray":"5 4"},pv);
  if(e.foot>0)el("rect",{x:X(fx),y:Y(fy),width:e.fw*k,height:e.fd*k,fill:blue,opacity:.35,stroke:blue,"stroke-width":1.5},pv);
  el("rect",{x:X(0)-10,y:Y(e.D)+4,width:e.W*k+20,height:12,fill:rule},pv);
  el("text",{x:X(e.W/2),y:Y(e.D)+14,"text-anchor":"middle",fill:ink,"font-size":9,"font-family":"IBM Plex Mono, monospace"},pv,"ROAD");
  const dim=(t,x,y,anchor)=>el("text",{x,y,"text-anchor":anchor||"middle",fill:red,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pv,t);
  dim(fmt(e.sf,2),X(e.W/2),Y(e.D-e.sf/2)+4);dim(fmt(e.sr,2),X(e.W/2),Y(e.sr/2)+4);
  dim(fmt(e.sl,2),X(0)-4,Y(e.D/2)+4,"end");dim(fmt(e.ss,2),X(e.W)+4,Y(e.D/2)+4,"start");
  if(e.foot>0){el("text",{x:X(fx+e.fw/2),y:Y(fy+e.fd/2)-4,"text-anchor":"middle",fill:ink,"font-size":13,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},pv,fmt(e.fw,2)+" × "+fmt(e.fd,2));
    el("text",{x:X(fx+e.fw/2),y:Y(fy+e.fd/2)+12,"text-anchor":"middle",fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},pv,fmt(100*e.foot/e.plot,1)+"% coverage");}
  el("text",{x:210,y:336,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},pv,"plot "+fmt(e.W,1)+" × "+fmt(e.D,1)+" = "+fmt(e.plot,1)+" m²");
  $("planLabel").textContent=e.buildable>e.cov?"coverage trims the footprint":"setbacks set the footprint";
  // GOVERNING RULES
  const nFar=e.foot>0?e.farA/e.foot:0;
  const C=[[`Setbacks leave ${fmt(e.bw,2)} × ${fmt(e.bd,2)} = ${fmt(e.buildable,1)} m²`,e.buildable<=e.cov,e.buildable<=e.cov?"governs footprint":"ok"],
    [`Ground coverage ${e.gc}% allows ${fmt(e.cov,1)} m²`,e.cov<e.buildable,e.cov<e.buildable?"governs footprint":"ok"],
    [`FAR ${fmt(e.far,2)} allows ${fmt(e.farA,1)} m² (${fmt(nFar,2)} floors of footprint)`,e.gov==="FAR",e.gov==="FAR"?"governs":"spare "+fmt(Math.max(0,e.farA-e.bua),0)+" m²"],
    [`Height ${fmt(e.hmax,1)} m allows ${e.stilt?"stilt + ":""}${e.nH} floors at ${fmt(e.ftf,2)} m`,e.gov==="height","" ],
    [e.rk>0?`Road rule ${fmt(e.rk,1)} × (${fmt(e.road,1)} + ${fmt(e.sf,2)}) = ${fmt(e.hRoad,1)} m`:"Road-width height rule off",e.gov==="road width",""]];
  C[3][2]=e.gov==="height"?"governs":"ok";C[4][2]=e.gov==="road width"?"governs":(e.rk>0?"ok":"off");
  const ul=$("checks");ul.innerHTML="";
  C.forEach(([t,g,lab])=>{const li=document.createElement("li");const cls=g?"bad":lab==="off"?"warn":"ok";
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${lab}</span>`;ul.appendChild(li)});
  $("gov").textContent=e.gov==="FAR"?"FAR is used in full":e.gov+" limit governs · "+fmt(Math.max(0,e.farA-e.bua),0)+" m² of FAR unused";
  // TABLE
  const tb=$("tbl");tb.innerHTML="";let cum=0,lev=0;
  const row=(n,l,a,c2)=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${n}</td><td>${fmt(l,2)}</td><td>${fmt(a,1)}</td><td>${Math.round(a*SQFT).toLocaleString("en-IN")}</td><td>${c2}</td>`;tb.appendChild(tr)};
  if(e.stilt){row("Stilt (parking)",0,e.foot,"not in FAR");lev=e.stH;}
  const names=["Ground","First","Second","Third","Fourth","Fifth","Sixth","Seventh","Eighth","Ninth"];
  e.floors.forEach((a,i)=>{cum+=a;const nm=(e.stilt?(i<9?names[i+1]:"Floor "+(i+1)):(i<10?names[i]:"Floor "+i))+(a<e.foot-0.01?" (part)":"");row(nm,lev+i*e.ftf,a,fmt(cum,1))});
  const tr=document.createElement("tr");tr.className="now";tr.innerHTML=`<td>Total in FAR</td><td></td><td>${fmt(e.bua,1)}</td><td>${Math.round(e.bua*SQFT).toLocaleString("en-IN")}</td><td>FAR ${fmt(e.bua/e.plot,2)}</td>`;tb.appendChild(tr);
}
""")
