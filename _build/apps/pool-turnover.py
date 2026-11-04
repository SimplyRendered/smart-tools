APP = dict(
slug="pool-turnover", title="Pool Volume & Turnover", h1="Pool Volume & Turnover",
sub="Enter the pool, its shallow and deep ends and the turnover time. Get the true water volume of a sloping floor, the pump flow, the filter size and the pipe bore, with the long section drawn to scale.",
meta=[("Sheet","T-47"),("Method","Q = V ÷ turnover"),("Units","m, m³, mm"),("By","@smart_tools_every_week")],
source="Volume = width × area of the long section (shallow flat + sloping part as a trapezium + deep flat). Pump flow Q = volume ÷ turnover time. Filter area = Q ÷ filtration rate; filter Ø from the area per filter. Pipe bore d = √(4Q ÷ πv). All first principles. Turnover time, filtration rate and pipe velocity are editable: take them from your local health code, pool consultant or the filter maker's data sheet.",
inputs="""
      <div class="row">
        <label for="L">Pool length m<input id="L" type="number" step="0.5" value="10"></label>
        <label for="B">Pool width m<input id="B" type="number" step="0.5" value="4"></label>
      </div>
      <div class="row">
        <label for="ds">Shallow water m<input id="ds" type="number" step="0.1" value="1.0"></label>
        <label for="dd">Deep water m<input id="dd" type="number" step="0.1" value="2.0"></label>
      </div>
      <div class="row">
        <label for="a">Shallow flat m<input id="a" type="number" step="0.5" value="3"></label>
        <label for="b">Slope length m<input id="b" type="number" step="0.5" value="3"></label>
      </div>
      <div class="row">
        <label for="T">Turnover hours<input id="T" type="number" step="0.5" value="6"></label>
        <label for="fr">Filter rate m³/h/m²<input id="fr" type="number" step="5" value="30"></label>
      </div>
      <div class="row">
        <label for="nf">Filters<input id="nf" type="number" step="1" value="1"></label>
        <label for="v">Pipe velocity m/s<input id="v" type="number" step="0.1" value="1.5"></label>
      </div>
      <p class="note">Depths are water depths, not to the coping. The deep flat is whatever is left after the shallow flat and the slope. Check turnover and filter rate against your local code and the filter maker's data.</p>
""",
right="""
      <div class="readout">
        <div><b>Water volume</b><span id="oV" class="hi">–</span></div>
        <div><b>Pump flow</b><span id="oQ">–</span></div>
        <div><b>Filter area</b><span id="oF">–</span></div>
        <div><b>Pipe bore</b><span id="oP">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Long section <span id="sLabel"></span></h2><svg id="sec" viewBox="0 0 580 300" role="img" aria-label="Long section of the pool with water depths"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Flow vs turnover <span>m³/h</span></h2><svg id="chart" viewBox="0 0 300 230" role="img" aria-label="Pump flow against turnover hours"></svg></div>
        <div class="view"><h2>Filter <span id="fLabel"></span></h2><svg id="filt" viewBox="0 0 300 230" role="img" aria-label="Filter size and pipe bore"></svg></div>
      </div>
      <div class="data"><h2>Turnover options <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Turnover</th><th>Flow m³/h</th><th>L/min</th><th>Filter m²</th><th>Filter Ø</th><th>Pipe bore</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function hyd(V,T,fr,nf,v){const Q=V/T,A=Q/fr,D=Math.sqrt(4*A/nf/Math.PI),d=Math.sqrt(4*(Q/3600)/(Math.PI*v))*1000;return {T,Q,A,D,d}}
function calc(){
  const L=num("L",1,100,10),B=num("B",0.5,50,4),ds=num("ds",0.2,6,1),dd=num("dd",0.2,6,2),T=num("T",0.5,48,6),fr=num("fr",1,100,30),nf=Math.round(num("nf",1,8,1)),v=num("v",0.2,5,1.5);
  const a=Math.min(num("a",0,100,3),L),b=Math.min(num("b",0,100,3),L-a),c=L-a-b;
  const sec=a*ds+b*(ds+dd)/2+c*dd,V=B*sec,guess=L*B*Math.max(ds,dd),h=hyd(V,T,fr,nf,v);
  const opts=[3,4,5,6,8,10,12].map(t=>({...hyd(V,t,fr,nf,v),now:Math.abs(t-T)<1e-9}));
  return {L,B,ds,dd,a,b,c,T,fr,nf,v,V,guess,avg:V/(L*B),...h,opts};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),F="IBM Plex Mono, monospace";
  $("oV").textContent=fmt(c.V,c.V<100?1:0)+" m³";$("oQ").textContent=fmt(c.Q,1)+" m³/h";$("oF").textContent=fmt(c.A,2)+" m²";$("oP").textContent=fmt(c.d,0)+" mm";
  // section
  const sv=$("sec");sv.innerHTML="";const md=Math.max(c.ds,c.dd),k=Math.min(500/c.L,200/md),ox=(580-c.L*k)/2,oy=78,X=x=>ox+x*k,Y=d=>oy+d*k;
  const floor=[[0,c.ds],[c.a,c.ds],[c.a+c.b,c.dd],[c.L,c.dd]];
  el("polygon",{points:[[0,0],...floor,[c.L,0]].map(p=>fmt(X(p[0]),1)+","+fmt(Y(p[1]),1)).join(" "),fill:blue,opacity:.45},sv);
  el("polyline",{points:[[0,-0.15],...floor,[c.L,-0.15]].map(p=>fmt(X(p[0]),1)+","+fmt(Y(p[1]),1)).join(" "),fill:"none",stroke:ink,"stroke-width":3},sv);
  el("rect",{x:fmt(X(0),1),y:fmt(Y(0),1),width:fmt(c.L*k,1),height:fmt(md*k,1),fill:"none",stroke:red,"stroke-dasharray":"6 5","stroke-width":1.5},sv);
  el("line",{x1:fmt(X(0),1),y1:fmt(Y(0),1),x2:fmt(X(c.L),1),y2:fmt(Y(0),1),stroke:blue,"stroke-width":2},sv);
  el("text",{x:fmt(X(0)+6,1),y:fmt(Y(c.ds)-8,1),fill:ink,"font-size":14,"font-family":F},sv,fmt(c.ds,2)+" m");
  el("text",{x:fmt(X(c.L)-6,1),y:fmt(Y(c.dd)-8,1),"text-anchor":"end",fill:ink,"font-size":14,"font-family":F},sv,fmt(c.dd,2)+" m");
  el("text",{x:20,y:48,"text-anchor":"start",fill:ink,"font-size":14,"font-family":F},sv,fmt(c.L,1)+" m long · avg depth "+fmt(c.avg,2)+" m");
  el("text",{x:20,y:24,fill:red,"font-size":14,"font-family":F},sv,"dashed box = L × W × deep: "+fmt(c.guess,1)+" m³");
  sv.setAttribute("viewBox","0 0 580 "+fmt(Y(md)+42,0));el("text",{x:20,y:fmt(Y(md)+30,1),fill:ink2,"font-size":13,"font-family":F},sv,"flat "+fmt(c.a,1)+" · slope "+fmt(c.b,1)+" · deep flat "+fmt(c.c,1)+" m");
  $("sLabel").textContent=fmt(c.V*1000,0).replace(/\B(?=(\d{3})+(?!\d))/g,",")+" litres";
  // chart
  const cv=$("chart");cv.innerHTML="";const T0=2,T1=12,qmax=Math.max(c.guess/T0,c.Q,1e-6),cx=t=>40+(t-T0)/(T1-T0)*245,cy=q=>190-q/qmax*165;
  el("line",{x1:40,y1:190,x2:285,y2:190,stroke:ink},cv);el("line",{x1:40,y1:20,x2:40,y2:190,stroke:ink},cv);
  [2,4,6,8,10,12].forEach(t=>el("text",{x:fmt(cx(t),1),y:206,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},cv,t+" h"));
  const P=(V,col,dash)=>{const p=[];for(let t=T0;t<=T1+1e-9;t+=0.25)p.push(fmt(cx(t),1)+","+fmt(cy(V/t),1));el("polyline",{points:p.join(" "),fill:"none",stroke:col,"stroke-width":2,"stroke-dasharray":dash||""},cv)};
  P(c.guess,red,"5 4");P(c.V,blue);
  if(c.T>=T0&&c.T<=T1){el("circle",{cx:fmt(cx(c.T),1),cy:fmt(cy(c.Q),1),r:5,fill:blue,stroke:ink},cv)}
  el("text",{x:46,y:18,fill:ink,"font-size":11,"font-family":F},cv,fmt(qmax,1)+" m³/h");
  el("text",{x:285,y:224,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":F},cv,"blue = true volume · red = L×W×deep");
  // filter
  const fv=$("filt");fv.innerHTML="";const Dm=Math.max(c.D,1e-6),nshow=Math.min(c.nf,4),fk=Math.min(140/Dm,250/(nshow*Dm*1.15)),r=Dm*fk/2;
  const gap=(300-nshow*2*r)/(nshow+1);
  for(let i=0;i<nshow;i++){const x=gap+r+i*(2*r+gap);el("circle",{cx:fmt(x,1),cy:105,r:fmt(Math.max(r,2),1),fill:blue,opacity:.35,stroke:blue,"stroke-width":2},fv)}
  el("text",{x:150,y:22,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":F},fv,c.nf+" × Ø "+fmt(c.D*1000,0)+" mm filter"+(c.nf>4?" (4 shown)":""));
  const pd=Math.max(2,Math.min(30,c.d/1000*fk));el("rect",{x:20,y:fmt(195-pd/2,1),width:260,height:fmt(pd,1),fill:red,opacity:.7},fv);
  el("text",{x:150,y:224,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":F},fv,"pipe bore "+fmt(c.d,0)+" mm at "+fmt(c.v,1)+" m/s");
  $("fLabel").textContent=fmt(c.fr,0)+" m³/h per m²";
  $("tb").innerHTML=c.opts.map(o=>`<tr${o.now?' class="now"':""}><td>${o.T} h</td><td>${fmt(o.Q,1)}</td><td>${fmt(o.Q*1000/60,0)}</td><td>${fmt(o.A,2)}</td><td>${c.nf} × ${fmt(o.D*1000,0)} mm</td><td>${fmt(o.d,0)} mm</td></tr>`).join("")+
    `<tr><td>L × W × deep</td><td colspan="5" style="text-align:left">${fmt(c.guess,1)} m³, ${fmt((c.guess/c.V-1)*100,0)}% more water than the pool really holds</td></tr>`;
  $("dLabel").textContent=fmt(c.V,1)+" m³ of water";
}
""")
