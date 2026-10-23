APP = dict(
slug="drain-gradient", title="Drain Gradient & Invert Levels", h1="Drain Gradient & Invert Levels",
sub="Enter the pipe, the run length, the gradient and the ground levels. Get the fall, the invert level at every manhole, the cover and whether the flow cleans itself, on a live long section.",
meta=[("Sheet","T-32"),("Method","Manning, full + part flow"),("Units","m, mm"),("By","@smart_tools_every_week")],
source="Fall = length ÷ N for a gradient of 1 in N. Velocity V = (1/n) R^(2/3) S^(1/2) (Manning), R = hydraulic radius, solved for part-full flow in a circular pipe. n: PVC 0.010, cast iron 0.012, concrete / stoneware 0.013 (typical textbook values). Self-cleansing velocity of about 0.75 m/s and a 3.0 m/s ceiling are commonly quoted for building drains (NBC 2016 Part 9); confirm gradients, minimum cover and manhole spacing with your local code.",
inputs="""
      <div class="row">
        <label for="dia">Pipe diameter
          <select id="dia"><option value="75">75 mm</option><option value="100" selected>100 mm</option><option value="150">150 mm</option><option value="200">200 mm</option><option value="230">230 mm</option><option value="300">300 mm</option></select>
        </label>
        <label for="mat">Pipe material
          <select id="mat"><option value="0.010" selected>PVC · n 0.010</option><option value="0.012">Cast iron · n 0.012</option><option value="0.013">Concrete / stoneware · n 0.013</option></select>
        </label>
      </div>
      <div class="row">
        <label for="L">Run length m<input id="L" type="number" step="1" value="24"></label>
        <label for="Q">Design flow L/s<input id="Q" type="number" step="0.1" value="1.5"></label>
      </div>
      <div class="row">
        <label for="gsel">Gradient
          <select id="gsel"><option value="40">1 in 40</option><option value="60" selected>1 in 60</option><option value="80">1 in 80</option><option value="100">1 in 100</option><option value="c">Custom</option></select>
        </label>
        <label for="gn">1 in N<input id="gn" type="number" step="5" value="60"></label>
      </div>
      <div class="row">
        <label for="g0">Ground at start RL m<input id="g0" type="number" step="0.05" value="100.00"></label>
        <label for="g1">Ground at end RL m<input id="g1" type="number" step="0.05" value="99.85"></label>
      </div>
      <div class="row">
        <label for="d0">Start invert depth m<input id="d0" type="number" step="0.05" value="0.60"></label>
        <label for="cov">Minimum cover m<input id="cov" type="number" step="0.05" value="0.45"></label>
      </div>
      <div class="row">
        <label for="vmin">Min velocity m/s<input id="vmin" type="number" step="0.05" value="0.75"></label>
        <label for="mh">Manhole every m<input id="mh" type="number" step="1" value="12"></label>
      </div>
      <p class="note">Invert depth = ground level minus the bottom inside of the pipe at the start. Cover = ground to the top of the pipe. Flow is the peak you expect in the pipe (a bathroom group is often about 0.5 to 1.5 L/s).</p>
""",
right="""
      <div class="readout">
        <div><b>Fall</b><span id="oF" class="hi">–</span></div>
        <div><b>End invert</b><span id="oE">–</span></div>
        <div><b>Velocity</b><span id="oV">–</span></div>
        <div><b>Flow depth</b><span id="oH">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Long section <span id="lsLabel"></span></h2><svg id="ls" viewBox="0 0 560 280" role="img" aria-label="Drain long section"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Pipe section <span id="csLabel"></span></h2><svg id="cs" viewBox="0 0 300 300" role="img" aria-label="Pipe cross section with flow depth" style="max-height:300px"></svg></div>
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
      </div>
      <div class="data"><h2>Invert levels <span>RL, m</span></h2><div class="tablewrap"><table><thead><tr><th>Point</th><th>Chainage</th><th>Ground</th><th>Invert</th><th>Cover</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
$("gsel").addEventListener("change",()=>{const v=$("gsel").value;if(v!=="c")$("gn").value=v;render()});
$("gn").addEventListener("input",()=>{$("gsel").value=["40","60","80","100"].includes($("gn").value)?$("gn").value:"c"});
function partial(Q,D,n,S){ // Q m3/s, D m. returns {y (depth ratio),V,full,Qf,over}
  const Af=Math.PI*D*D/4,Rf=D/4,Vf=(1/n)*Math.pow(Rf,2/3)*Math.sqrt(S),Qf=Vf*Af;
  const fl=th=>{const A=D*D/8*(th-Math.sin(th)),P=D*th/2,R=A/P,V=(1/n)*Math.pow(R,2/3)*Math.sqrt(S);return {A,V,Q:A*V,y:(1-Math.cos(th/2))/2}};
  const thMax=2*Math.acos(1-2*0.938);let over=false,th;
  if(Q>=fl(thMax).Q){over=true;th=thMax}
  else{let lo=1e-4,hi=thMax;for(let i=0;i<60;i++){const m=(lo+hi)/2;fl(m).Q<Q?lo=m:hi=m}th=(lo+hi)/2}
  const r=fl(th);return {y:r.y,V:over?Vf:r.V,Vf,Qf,over,A:r.A};
}
function calc(){
  const D=num("dia",50,600,100)/1000,n=num("mat",0.008,0.02,0.01),L=num("L",1,500,24),Q=num("Q",0.01,2000,0.8)/1000,N=num("gn",5,1000,60),S=1/N;
  const g0=num("g0",-100,5000,100),g1=num("g1",-100,5000,99.85),d0=num("d0",0.1,10,0.6),cov=num("cov",0,5,0.45),vmin=num("vmin",0.1,3,0.75),mh=num("mh",1,200,12);
  const fall=L*S,i0=g0-d0,i1=i0-fall,p=partial(Q,D,n,S);
  const pts=[];const ch=[];for(let x=0;x<L-1e-9;x+=mh)ch.push(x);ch.push(L);
  ch.forEach((x,i)=>{const gr=g0+(g1-g0)*x/L,inv=i0-fall*x/L;pts.push({x,gr,inv,cover:gr-inv-D,i,last:i===ch.length-1})});
  return {D,n,L,Q,N,S,g0,g1,d0,cov,vmin,mh,fall,i0,i1,p,pts,minCover:Math.min(...pts.map(q=>q.cover))};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun");
  const p=c.p;
  $("oF").textContent=Math.round(c.fall*1000)+" mm";$("oE").textContent=fmt(c.i1,3);$("oV").textContent=fmt(p.V,2)+" m/s";$("oH").textContent=p.over?"full":Math.round(p.y*100)+"% of D";
  $("oV").className=p.V<c.vmin||p.V>3?"bad":"";
  const C=[[`Velocity ${fmt(p.V,2)} m/s ≥ ${fmt(c.vmin,2)} m/s so solids are carried along`,p.V>=c.vmin],
    [`Velocity ${fmt(p.V,2)} m/s is under the 3.0 m/s wear limit`,p.V<=3],
    [p.over?`Pipe is too small: the flow exceeds its capacity (full bore ${fmt(p.Qf*1000,1)} L/s)`:`Flow fills ${Math.round(p.y*100)}% of the pipe depth (full bore carries ${fmt(p.Qf*1000,1)} L/s)`,!p.over&&p.y<=0.75,"warn"],
    [`Cover over the pipe is ${fmt(c.minCover,2)} m at the shallowest point (needs ${fmt(c.cov,2)} m)`,c.minCover>=c.cov],
    [`End invert ${fmt(c.i1,3)} m is ${fmt(c.g1-c.i1,2)} m below the ground`,true,"info"]];
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=kind==="info"?"warn":okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&!kind)fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${kind==="info"?"note":okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" failing":"all checks met";
  // long section
  const sv=$("ls");sv.innerHTML="";
  const ymax=Math.max(c.g0,c.g1)+0.15,ymin=Math.min(c.i0,c.i1)-0.25,ex=Math.min(40,Math.max(1,(220/(ymax-ymin))/(500/c.L)));
  const sx=500/c.L,sy=sx*ex,ox=40,oy=20,X=x=>ox+x*sx,Y=v=>oy+(ymax-v)*sy;
  const sy2=Math.min(sy,220/(ymax-ymin)),Yv=v=>oy+(ymax-v)*sy2;
  const k=sy2/sx;
  el("polygon",{points:`${X(0)},${Yv(c.g0)} ${X(c.L)},${Yv(c.g1)} ${X(c.L)},${Yv(ymin)} ${X(0)},${Yv(ymin)}`,fill:rule,opacity:.35},sv);
  el("line",{x1:X(0),y1:Yv(c.g0),x2:X(c.L),y2:Yv(c.g1),stroke:ink,"stroke-width":2},sv);
  el("polygon",{points:`${X(0)},${Yv(c.i0)} ${X(c.L)},${Yv(c.i1)} ${X(c.L)},${Yv(c.i1+c.D)} ${X(0)},${Yv(c.i0+c.D)}`,fill:sheet,stroke:blue,"stroke-width":1.6},sv);
  el("polygon",{points:`${X(0)},${Yv(c.i0)} ${X(c.L)},${Yv(c.i1)} ${X(c.L)},${Yv(c.i1+c.D*p.y)} ${X(0)},${Yv(c.i0+c.D*p.y)}`,fill:blue,opacity:.35},sv);
  c.pts.forEach(q=>{el("rect",{x:X(q.x)-5,y:Yv(q.gr),width:10,height:Math.max(1,Yv(q.inv)-Yv(q.gr)+2),fill:"none",stroke:ink2,"stroke-width":1.2},sv);
    el("circle",{cx:X(q.x),cy:Yv(q.inv),r:2.6,fill:red},sv);});
  el("text",{x:X(0)+8,y:Yv(c.i0)+15,fill:red,"font-size":11,"font-family":"IBM Plex Mono, monospace"},sv,"IL "+fmt(c.i0,3));
  el("text",{x:X(c.L)-8,y:Yv(c.i1)+15,fill:red,"font-size":11,"text-anchor":"end","font-family":"IBM Plex Mono, monospace"},sv,"IL "+fmt(c.i1,3));
  el("text",{x:ox,y:Math.min(272,Yv(ymin)+16),fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},sv,"vertical scale ×"+fmt(k,0)+" · 1 in "+Math.round(c.N)+" · "+Math.round(c.D*1000)+" mm");
  $("lsLabel").textContent="run "+fmt(c.L,1)+" m · fall "+Math.round(c.fall*1000)+" mm";
  // cross section
  const cv=$("cs");cv.innerHTML="";const r=110,cx=150,cy=140;
  el("circle",{cx,cy,r,fill:sheet,stroke:ink,"stroke-width":3},cv);
  const th=p.over?2*Math.PI:2*Math.acos(1-2*p.y),yy=cy+r-2*r*p.y;
  if(p.over)el("circle",{cx,cy,r:r-2,fill:blue,opacity:.4},cv);
  else if(p.y>0.001){const hw=Math.sqrt(Math.max(0,r*r-(cy+r-yy-r)*(cy+r-yy-r)));
    const dy=yy-cy,half=Math.sqrt(Math.max(0,r*r-dy*dy));const large=p.y>0.5?1:0;
    el("path",{d:`M ${cx-half} ${yy} A ${r} ${r} 0 ${large} 0 ${cx+half} ${yy} Z`,fill:blue,opacity:.4,stroke:blue},cv);}
  el("line",{x1:cx-r-15,y1:cy+r,x2:cx+r+15,y2:cy+r,stroke:rule},cv);
  el("text",{x:cx,y:cy-8,"text-anchor":"middle",fill:ink,"font-size":13,"font-family":"IBM Plex Mono, monospace"},cv,Math.round(c.D*1000)+" mm");
  el("text",{x:cx,y:cy+8,"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},cv,p.over?"full":"flow "+Math.round(p.y*c.D*1000)+" mm deep");
  el("text",{x:cx,y:cy+r+34,"text-anchor":"middle",fill:red,"font-size":14,"font-family":"IBM Plex Mono, monospace"},cv,fmt(p.V,2)+" m/s at "+fmt(c.Q*1000,1)+" L/s");
  $("csLabel").textContent="n "+c.n;
  const tb=$("tb");tb.innerHTML="";c.pts.forEach(q=>{const tr=document.createElement("tr");tr.innerHTML=`<td>${q.last?"End":q.i===0?"Start":"MH "+q.i}</td><td>${fmt(q.x,1)}</td><td>${fmt(q.gr,3)}</td><td>${fmt(q.inv,3)}</td><td class="${q.cover>=c.cov?"":"bad"}">${fmt(q.cover,2)}</td>`;tb.appendChild(tr)});
}
""")
