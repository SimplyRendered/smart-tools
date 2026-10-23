APP = dict(
slug="water-demand", title="Water Demand & Tank Sizing", h1="Water Demand & Tank Sizing",
sub="Pick the building type and the number of users. Get the daily water demand, the drinking and flushing split, the sump and overhead tank sizes and the pump, drawn on a live building section.",
meta=[("Sheet","T-33"),("Method","NBC per-head demand"),("Units","litres, m"),("By","@smart_tools_every_week")],
source="Per-head demand and flushing share from NBC 2016 Part 9 (Plumbing Services), Table 2: dwellings 135 L (flushing 45), offices and day schools 45 (20), boarding schools and hostels 135 (45), hospitals 340 or 450 (110 / 150) per bed, hotels up to 3 star 180 (60), restaurants 70 (15), cinemas 15 (10) per seat. Pump power = ρ g Q H ÷ efficiency. Tank split and fill time are design choices, so adjust them. Confirm figures for your city's bylaws; fire storage is not included.",
inputs="""
      <label for="bt">Building type
        <select id="bt">
          <option value="135,45,Dwelling" selected>Dwelling · 135 L/head</option>
          <option value="150,45,Dwelling (large city)">Dwelling, city over 1 lakh · 150</option>
          <option value="45,20,Office">Office · 45 L/head</option>
          <option value="45,20,Day school">School, day · 45 L/head</option>
          <option value="135,45,Hostel">Hostel / boarding school · 135</option>
          <option value="340,110,Hospital">Hospital up to 100 beds · 340 /bed</option>
          <option value="450,150,Hospital">Hospital over 100 beds · 450 /bed</option>
          <option value="180,60,Hotel">Hotel up to 3 star · 180 /bed</option>
          <option value="70,15,Restaurant">Restaurant · 70 /seat</option>
          <option value="15,10,Cinema">Cinema / hall · 15 /seat</option>
        </select>
      </label>
      <div class="row">
        <label for="un">Units (flats, rooms…)<input id="un" type="number" step="1" value="24"></label>
        <label for="up">Users per unit<input id="up" type="number" step="1" value="5"></label>
      </div>
      <div class="row">
        <label for="fr">Overhead tank, share of a day %<input id="fr" type="number" step="5" value="33"></label>
        <label for="sd">Sump, days of demand<input id="sd" type="number" step="0.5" value="1"></label>
      </div>
      <div class="row">
        <label for="hb">Building height m<input id="hb" type="number" step="1" value="18"></label>
        <label for="ft">Pump fills tank in h<input id="ft" type="number" step="0.5" value="2"></label>
      </div>
      <div class="row">
        <label for="td">Tank water depth m<input id="td" type="number" step="0.1" value="1.5"></label>
        <label for="ef">Pump efficiency %<input id="ef" type="number" step="5" value="55"></label>
      </div>
      <p class="note">Users per unit: 5 for a flat, 1 for an office desk, 1 for a bed or seat. Tank sizes round up to the next common size. Pipe friction is taken as 20% of the lift.</p>
""",
right="""
      <div class="readout">
        <div><b>Daily demand</b><span id="oQ" class="hi">–</span></div>
        <div><b>Flushing water</b><span id="oFl">–</span></div>
        <div><b>Overhead tank</b><span id="oT">–</span></div>
        <div><b>Sump</b><span id="oS">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Building section <span id="bsLabel"></span></h2><svg id="bs" viewBox="0 0 420 380" role="img" aria-label="Sump, pump and overhead tank in a building section"></svg></div>
        <div class="view"><h2>Where the water goes <span id="spLabel"></span></h2><svg id="sp" viewBox="0 0 420 380" role="img" aria-label="Daily demand split"></svg></div>
      </div>
      <div class="data"><h2>Sizing summary <span id="sum"></span></h2><div class="tablewrap"><table><thead><tr><th>Item</th><th>Value</th><th>How</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const STD=[500,1000,1500,2000,3000,4000,5000,7500,10000,15000,20000,25000,30000,40000,50000,75000,100000,150000,200000,300000,500000];
const stdUp=v=>{for(const s of STD)if(s>=v-1e-9)return s;return Math.ceil(v/50000)*50000};
function calc(){
  const [tot,fl,name]=$("bt").value.split(",");const lpd=+tot,fls=+fl;
  const un=Math.round(num("un",1,100000,24)),up=Math.round(num("up",1,100,5)),users=un*up;
  const fr=num("fr",5,100,33)/100,sd=num("sd",0,10,1),hb=num("hb",1,300,18),ft=num("ft",0.25,24,2),td=num("td",0.5,6,1.5),ef=num("ef",10,95,55)/100;
  const Q=users*lpd,Qfl=users*fls,Qdm=Q-Qfl,oht=Q*fr,ohtS=stdUp(oht),sump=Q*sd,sumpS=sump>0?stdUp(sump):0;
  const pq=ohtS/(ft*3600), H=(hb+td)*1.2, kw=pq/1000*1000*9.81*H/ef/1000; // pq L/s -> m3/s: /1000
  const A=ohtS/1000/td,side=Math.sqrt(A),Asp=sumpS/1000/td,sideS=Math.sqrt(Asp);
  return {name,lpd,fls,un,up,users,fr,sd,hb,ft,td,ef,Q,Qfl,Qdm,oht,ohtS,sump,sumpS,pq,H,kw,side,sideS};
}
const L=v=>v>=10000?(v/1000).toFixed(v%1000?1:0)+" kL":Math.round(v).toLocaleString("en-IN")+" L";
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun");
  $("oQ").textContent=Math.round(c.Q).toLocaleString("en-IN")+" L/day";$("oFl").textContent=Math.round(c.Qfl).toLocaleString("en-IN")+" L";
  $("oT").textContent=L(c.ohtS);$("oS").textContent=c.sumpS?L(c.sumpS):"none";
  // building section
  const sv=$("bs");sv.innerHTML="";const gy=270,fh=Math.min(28,200/Math.max(1,Math.round(c.hb/3)));const nf=Math.max(1,Math.round(c.hb/3)),bh=nf*fh,bx=120,bw=170;
  el("line",{x1:10,y1:gy,x2:410,y2:gy,stroke:ink,"stroke-width":2},sv);
  el("rect",{x:bx,y:gy-bh,width:bw,height:bh,fill:sheet,stroke:ink,"stroke-width":2},sv);
  for(let i=1;i<nf;i++)el("line",{x1:bx,y1:gy-i*fh,x2:bx+bw,y2:gy-i*fh,stroke:rule},sv);
  const tw=70,th=Math.max(18,Math.min(44,16+Math.log10(c.ohtS)*6));
  el("rect",{x:bx+bw/2-tw/2,y:gy-bh-th,width:tw,height:th,fill:blue,opacity:.35,stroke:blue,"stroke-width":1.8},sv);
  el("text",{x:bx+bw/2,y:gy-bh-th-6,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"OHT "+L(c.ohtS));
  const sw=90,sh=48;
  el("rect",{x:bx-sw-14,y:gy+10,width:sw,height:sh,fill:blue,opacity:.35,stroke:blue,"stroke-width":1.8},sv);
  el("text",{x:bx-sw/2-14,y:gy+sh+28,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,c.sumpS?"Sump "+L(c.sumpS):"No sump");
  el("circle",{cx:bx-4,cy:gy+34,r:8,fill:red},sv);
  el("polyline",{points:`${bx-4},${gy+34} ${bx-4},${gy-bh-th/2} ${bx+bw/2-tw/2},${gy-bh-th/2}`,fill:"none",stroke:red,"stroke-width":2},sv);
  el("line",{x1:bx+bw+16,y1:gy,x2:bx+bw+16,y2:gy-bh,stroke:ink2},sv);
  el("text",{x:bx+bw+22,y:gy-bh/2,fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,fmt(c.hb,0)+" m");
  el("text",{x:bx-4,y:gy+68,"text-anchor":"middle",fill:red,"font-size":12,"font-family":"IBM Plex Mono, monospace","dx":0},sv,"");
  el("text",{x:20,y:372,fill:red,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"pump "+fmt(c.kw,2)+" kW · "+fmt(c.H,1)+" m head");
  $("bsLabel").textContent=c.users.toLocaleString("en-IN")+" users";
  // split chart
  const s2=$("sp");s2.innerHTML="";const x0=60,w=110,y0=30,hh=280,hDm=hh*(c.Qdm/c.Q),hFl=hh-hDm;
  el("rect",{x:x0,y:y0,width:w,height:hFl,fill:sun,opacity:.8,stroke:ink},s2);
  el("rect",{x:x0,y:y0+hFl,width:w,height:hDm,fill:blue,opacity:.7,stroke:ink},s2);
  const T=(x,y,t,col,anchor)=>el("text",{x,y,fill:col||ink,"font-size":13,"text-anchor":anchor||"start","font-family":"IBM Plex Mono, monospace"},s2,t);
  T(x0+w+14,y0+hFl/2+4,"Flushing "+Math.round(c.Qfl).toLocaleString("en-IN")+" L");
  T(x0+w+14,y0+hFl+hDm/2+4,"Drinking, cooking,");T(x0+w+14,y0+hFl+hDm/2+20,"bathing "+Math.round(c.Qdm).toLocaleString("en-IN")+" L");
  T(x0,y0-10,c.name+" · "+c.lpd+" L per head per day",ink2);
  T(x0,y0+hh+30,"Treated or recycled water for flushing",ink2);T(x0,y0+hh+48,"could cover "+Math.round(100*c.fls/c.lpd)+"% of the demand.",ink2);
  $("spLabel").textContent=Math.round(c.Q).toLocaleString("en-IN")+" L/day";
  const rows=[["Daily demand",Math.round(c.Q).toLocaleString("en-IN")+" L",`${c.users} users × ${c.lpd} L`],
    ["Overhead tank",L(c.ohtS)+" ("+Math.round(c.oht).toLocaleString("en-IN")+" L needed)",`${Math.round(c.fr*100)}% of a day, next size up · ${fmt(c.side,1)} × ${fmt(c.side,1)} × ${fmt(c.td,1)} m deep`],
    ["Sump",c.sumpS?L(c.sumpS)+" ("+Math.round(c.sump).toLocaleString("en-IN")+" L needed)":"none",c.sumpS?`${fmt(c.sd,1)} day(s) of demand · ${fmt(c.sideS,1)} × ${fmt(c.sideS,1)} × ${fmt(c.td,1)} m deep`:"set sump days above 0"],
    ["Pump flow",fmt(c.pq*60,0)+" L/min ("+fmt(c.pq,2)+" L/s)",`${L(c.ohtS)} in ${fmt(c.ft,1)} h`],
    ["Pump head",fmt(c.H,1)+" m",`(${fmt(c.hb,0)} m + ${fmt(c.td,1)} m tank) × 1.2 friction`],
    ["Pump shaft power",fmt(c.kw,2)+" kW",`ρ g Q H ÷ ${Math.round(c.ef*100)}% efficiency`]];
  $("tb").innerHTML=rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td style="white-space:normal;text-align:left;color:var(--ink-2)">${r[2]}</td></tr>`).join("");
  $("sum").textContent="";
}
""")
