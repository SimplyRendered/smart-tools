APP = dict(
slug="room-acoustics", title="Room Acoustics RT60", h1="Room Acoustics RT60",
sub="Will the room echo? Enter the size and finishes to get the reverberation time, compare it with a target, and see how much absorption to add.",
meta=[("Sheet","T-07"),("Method","Sabine · Eyring"),("Band","500 Hz"),("By","@smart_tools_every_week")],
source="RT60 = 0.161 V / A (Sabine). Absorption coefficients at 500 Hz from standard tables (HyperPhysics). Use measured product data for final design.",
inputs="""
      <label for="use">Room use (target)
        <select id="use">
          <option value="0.4,0.6">Classroom / lecture (0.4–0.6 s)</option>
          <option value="0.5,0.8" selected>Office / meeting room (0.5–0.8 s)</option>
          <option value="0.3,0.5">Home theatre / studio (0.3–0.5 s)</option>
          <option value="0.4,0.7">Restaurant / café (0.4–0.7 s)</option>
          <option value="0.8,1.2">Auditorium, speech (0.8–1.2 s)</option>
          <option value="1.5,2.2">Concert hall, music (1.5–2.2 s)</option>
        </select>
      </label>
      <div class="row">
        <label for="L">Length (m)<input id="L" type="number" step="0.1" value="8"></label>
        <label for="W">Width (m)<input id="W" type="number" step="0.1" value="6"></label>
      </div>
      <label for="H">Height (m)<input id="H" type="number" step="0.1" value="3.2"></label>
      <label for="mf">Floor<select id="mf"></select></label>
      <label for="mc">Ceiling<select id="mc"></select></label>
      <label for="mw">Walls<select id="mw"></select></label>
      <div class="row">
        <label for="ag">Glass area m²<input id="ag" type="number" step="0.5" value="8"></label>
        <label for="ad">Curtain area m²<input id="ad" type="number" step="0.5" value="0"></label>
      </div>
      <div class="row">
        <label for="ap">Acoustic panels m²<input id="ap" type="number" step="0.5" value="0"></label>
        <label for="aa">Seated people m²<input id="aa" type="number" step="0.5" value="6"></label>
      </div>
      <p class="note">Glass, curtains and panels are taken out of the wall area. "Seated people" is the floor area covered by occupied upholstered seating.</p>
""",
right="""
      <div class="readout">
        <div><b>RT60 Sabine</b><span id="oS" class="hi">–</span></div>
        <div><b>RT60 Eyring</b><span id="oE">–</span></div>
        <div><b>Volume</b><span id="oV">–</span></div>
        <div><b>Absorption A</b><span id="oA">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Result vs target <span id="verdict"></span></h2><svg id="gauge" viewBox="0 0 640 120" role="img" aria-label="Reverberation time against target range"></svg></div>
        <div class="view full"><h2>Where the absorption comes from <span>m² sabins at 500 Hz</span></h2><svg id="bars" viewBox="0 0 640 250" role="img" aria-label="Absorption by surface"></svg></div>
      </div>
      <div class="data">
        <h2>To reach the target <span id="fixLabel"></span></h2>
        <ul class="checks" id="fix"></ul>
      </div>
""",
js=r"""
const MAT=[["Poured concrete",0.02],["Brick, unglazed",0.03],["Concrete block, painted",0.06],["Concrete block, unpainted",0.30],["Gypsum board on studs",0.05],["Plaster on lath",0.10],["Plywood panel on studs",0.10],["Vinyl / tile on concrete",0.03],["Wood platform floor",0.20],["Heavy carpet on concrete",0.15],["Heavy carpet on felt underlay",0.40],["Acoustical plaster",0.50],["Acoustic tile, suspended",0.60],["Acoustic tile, rigid mount",0.70]];
const GLASS=0.20,DRAPE=0.50,PANEL=0.70,SEAT=0.80;
function fill(id,def){const s=$(id);MAT.forEach((m,i)=>{const o=document.createElement("option");o.value=i;o.textContent=`${m[0]} (${m[1].toFixed(2)})`;s.appendChild(o)});s.value=def}
fill("mf",7);fill("mc",4);fill("mw",4);
function calc(){const L=+$("L").value,W=+$("W").value,H=+$("H").value;const V=L*W*H;
  const floor=L*W,ceil=L*W,wallsGross=2*(L+W)*H;const ag=+$("ag").value,ad=+$("ad").value,ap=+$("ap").value,aa=Math.min(+$("aa").value,floor);
  const walls=Math.max(0,wallsGross-ag-ad-ap);const mf=MAT[$("mf").value],mc=MAT[$("mc").value],mw=MAT[$("mw").value];
  const parts=[["Floor · "+mf[0],(floor-aa)*mf[1],floor-aa],["Seated people",aa*SEAT,aa],["Ceiling · "+mc[0],ceil*mc[1],ceil],["Walls · "+mw[0],walls*mw[1],walls],["Glass",ag*GLASS,ag],["Curtains",ad*DRAPE,ad],["Acoustic panels",ap*PANEL,ap]].filter(p=>p[2]>0);
  const A=parts.reduce((s,p)=>s+p[1],0),S=parts.reduce((s,p)=>s+p[2],0);const abar=A/S;
  const sab=0.161*V/A,ey=0.161*V/(-S*Math.log(1-Math.min(abar,0.99)));return{V,A,S,abar,sab,ey,parts,mw}}
function render(){const r=calc();const [t0,t1]=$("use").value.split(",").map(Number);const ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),ok=css("--ok"),blue=css("--blue");
  $("oS").textContent=fmt(r.sab,2)+" s";$("oE").textContent=fmt(r.ey,2)+" s";$("oV").textContent=r.V.toFixed(0)+" m³";$("oA").textContent=r.A.toFixed(1)+" m²";
  const inBand=r.sab>=t0&&r.sab<=t1;$("oS").className=inBand?"ok":"bad";
  $("verdict").textContent=inBand?"inside the target range":r.sab>t1?"too reverberant":"too dead";
  const g=$("gauge");g.innerHTML="";const max=Math.max(2.5,Math.ceil(r.sab*2)/2+0.5),X=v=>30+v/max*580;
  el("rect",{x:X(t0),y:30,width:X(t1)-X(t0),height:40,fill:css("--okbg"),stroke:ok},g);
  el("line",{x1:X(0),y1:70,x2:X(max),y2:70,stroke:ink,"stroke-width":1.5},g);
  for(let v=0;v<=max+1e-9;v+=0.5){el("line",{x1:X(v),y1:70,x2:X(v),y2:76,stroke:ink},g);el("text",{x:X(v),y:92,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},g,v.toFixed(1)+" s")}
  const mx=X(Math.min(r.sab,max));el("line",{x1:mx,y1:18,x2:mx,y2:72,stroke:inBand?ok:red,"stroke-width":3},g);
  el("text",{x:mx,y:14,"text-anchor":"middle",fill:inBand?ok:red,"font-size":13,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},g,r.sab.toFixed(2)+" s");
  el("text",{x:(X(t0)+X(t1))/2,y:110,"text-anchor":"middle",fill:ok,"font-size":11,"font-family":"IBM Plex Sans, sans-serif"},g,"target "+t0+"–"+t1+" s");
  const b=$("bars");b.innerHTML="";const amax=Math.max(...r.parts.map(p=>p[1]),1);const rowH=Math.min(34,240/r.parts.length);
  r.parts.forEach((p,i)=>{const y=10+i*rowH;el("text",{x:0,y:y+rowH/2+4,fill:ink,"font-size":12,"font-family":"IBM Plex Sans, sans-serif"},b,p[0].length>30?p[0].slice(0,29)+"…":p[0]);
    const w=p[1]/amax*330;el("rect",{x:230,y:y+4,width:Math.max(1,w),height:rowH-10,fill:blue},b);
    el("text",{x:236+w,y:y+rowH/2+4,fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},b,p[1].toFixed(1)+" ("+p[2].toFixed(0)+" m²)")});
  const ul=$("fix");ul.innerHTML="";const tgt=(t0+t1)/2;const need=0.161*r.V/tgt;const add=(need-r.A);
  const item=(t,c)=>{const li=document.createElement("li");li.innerHTML=`<span>${t}</span><span class="pill ${c[0]}">${c[1]}</span>`;ul.appendChild(li)};
  if(add>0.5){const panel=add/(PANEL-r.mw[1]);item(`Add about ${add.toFixed(1)} m² sabins of absorption to reach ${tgt.toFixed(2)} s`,["warn","add"]);
    item(`≈ ${panel.toFixed(1)} m² of acoustic wall panels (α 0.70) replacing ${r.mw[0].toLowerCase()}`,["ok","option"]);
    item(`or switch the ceiling to suspended acoustic tile (α 0.60)`,["ok","option"]);
    $("fixLabel").textContent=`aim for the middle of the range, ${tgt.toFixed(2)} s`;}
  else if(add<-0.5){item(`Room is drier than needed: about ${(-add).toFixed(1)} m² sabins could be removed`,["warn","reduce"]);item("Use reflective finishes on some walls or ceiling, or less soft furnishing",["ok","option"]);$("fixLabel").textContent=`target ${tgt.toFixed(2)} s`;}
  else{item("Absorption is about right for this use",["ok","ok"]);$("fixLabel").textContent="";}
  item(`Average absorption coefficient ${r.abar.toFixed(2)}: ${r.abar<0.2?"Sabine is reliable at this level":"above about 0.2, trust the Eyring figure more"}`,["warn","note"]);
}
""")
