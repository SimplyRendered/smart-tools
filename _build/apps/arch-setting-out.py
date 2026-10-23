APP = dict(
slug="arch-setting-out", title="Arch & Curve Setting-out", h1="Arch & Curve Setting-out",
sub="Give any two of span, rise, radius or arc length. Get the radius, the centre point, the arc length and a table of plumb ordinates for pegging the curve on site, with the voussoirs drawn.",
meta=[("Sheet","T-29"),("Method","Circular segment"),("Units","mm"),("By","@smart_tools_every_week")],
source="Circle through the chord ends and the crown: R = (c²/4 + s²) ÷ 2s, half-angle θ = asin(c ÷ 2R), arc = 2Rθ, ordinate y = √(R² − x²) − (R − s). Standard geometry of a circular segment (chord c, rise s). Voussoir joints are drawn radial to the centre; brick sizes and ring depth are not checked, so ask a structural engineer for load-bearing arches.",
inputs="""
      <label for="mode">I know
        <select id="mode">
          <option value="cs" selected>Span and rise</option>
          <option value="rc">Radius and span</option>
          <option value="rl">Radius and arc length</option>
        </select>
      </label>
      <div class="row">
        <label for="a" id="al">Span mm<input id="a" type="number" step="10" value="3000"></label>
        <label for="b" id="bl">Rise mm<input id="b" type="number" step="10" value="750"></label>
      </div>
      <label for="n">Ordinates each side <span id="nv" class="time" style="font-size:18px"></span><input id="n" type="range" min="2" max="10" step="1" value="5"></label>
      <label for="vs">Voussoirs (bricks) in the ring <span id="vsv" class="time" style="font-size:18px"></span><input id="vs" type="range" min="5" max="41" step="2" value="19"></label>
      <label for="d">Ring depth mm<input id="d" type="number" step="5" value="230"></label>
      <p class="note">Span is the chord between the springing points. Rise is the height of the crown above the springing line. A rise of half the span is a semicircular arch; the rise is limited to that. Ordinates are measured up from the springing line at set distances from the centre line.</p>
""",
right="""
      <div class="readout">
        <div><b>Radius</b><span id="oR" class="hi">–</span></div>
        <div><b>Arc length</b><span id="oL">–</span></div>
        <div><b>Span / rise</b><span id="oS">–</span></div>
        <div><b>Centre below springing</b><span id="oC">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Arch elevation <span id="elL"></span></h2><svg id="el" viewBox="0 0 840 420" role="img" aria-label="Arch with centre, radius and ordinates"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Setting-out ordinates <span>from the centre line</span></h2><div class="tablewrap"><table><thead><tr><th>x from centre</th><th>y above springing</th><th>from springing end</th></tr></thead><tbody id="tb"></tbody></table></div></div>
        <div class="view"><h2>Working <span>every step</span></h2><ul class="checks" id="steps"></ul></div>
      </div>
""",
css=".view.full svg{max-height:420px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const LAB={cs:["Span mm","Rise mm",3000,750],rc:["Radius mm","Span mm",1875,3000],rl:["Radius mm","Arc length mm",1875,3500]};
$("mode").addEventListener("change",()=>{const m=LAB[$("mode").value];$("al").firstChild.textContent=m[0];$("bl").firstChild.textContent=m[1];$("a").value=m[2];$("b").value=m[3];render()});
function calc(){
  const mode=$("mode").value,a=num("a",100,60000,3000),b0=num("b",10,120000,750);
  let R,c,s,th;
  if(mode==="cs"){c=a;s=Math.min(b0,c/2);R=(c*c/4+s*s)/(2*s);}
  else if(mode==="rc"){R=a;c=Math.min(b0,2*R);s=R-Math.sqrt(Math.max(0,R*R-c*c/4));}
  else{R=a;th=Math.min(Math.PI/2,b0/(2*R));c=2*R*Math.sin(th);s=R*(1-Math.cos(th));}
  th=Math.asin(Math.min(1,c/(2*R)));
  const arc=2*R*th,drop=R-s,n=Math.round(num("n",2,10,5)),vs=Math.round(num("vs",5,41,19)),d=num("d",50,1000,230);
  const rows=[];for(let i=0;i<=n;i++){const x=(c/2)*i/n;const y=Math.sqrt(Math.max(0,R*R-x*x))-drop;rows.push({x,y,w:c/2-x});}
  return {mode,R,c,s,th,arc,drop,n,vs,d,rows,semi:Math.abs(s-c/2)<0.5};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),sun=css("--sun");
  $("nv").textContent=c.n;$("vsv").textContent=c.vs;
  const mm=v=>v>=10000?fmt(v/1000,2)+" m":Math.round(v)+" mm";
  $("oR").textContent=mm(c.R);$("oL").textContent=mm(c.arc);$("oS").textContent=Math.round(c.c)+" / "+Math.round(c.s);$("oC").textContent=c.drop>=0?mm(c.drop):"–";
  const sv=$("el");sv.innerHTML="";
  const ext=c.R+c.d, vw=c.c+2*c.d+200; const sc=Math.min(760/(c.c+2*c.d),300/(c.s+c.d+300)),ox=420-c.c/2*sc,base=330;
  const X=v=>ox+v*sc,Y=v=>base-v*sc; // x from left springing, y above springing line
  const cx=c.c/2,cy=-c.drop;
  // wall piers
  el("rect",{x:X(-c.d)-40,y:Y(c.s+c.d+120),width:40+c.d*sc,height:(c.s+c.d+120)*sc+60,fill:rule,opacity:.45},sv);
  el("rect",{x:X(c.c),y:Y(c.s+c.d+120),width:40+c.d*sc,height:(c.s+c.d+120)*sc+60,fill:rule,opacity:.45},sv);
  // arch ring as polygon between intrados R and extrados R+d
  const N=60,pts=[],a0=Math.PI/2-c.th,a1=Math.PI/2+c.th;
  for(let i=0;i<=N;i++){const t=a0+(a1-a0)*i/N;pts.push([X(cx+(c.R+c.d)*Math.cos(t)),Y(cy+(c.R+c.d)*Math.sin(t))]);}
  for(let i=N;i>=0;i--){const t=a0+(a1-a0)*i/N;pts.push([X(cx+c.R*Math.cos(t)),Y(cy+c.R*Math.sin(t))]);}
  el("polygon",{points:pts.map(p=>p.join(",")).join(" "),fill:sheet,stroke:ink,"stroke-width":2},sv);
  for(let k=1;k<c.vs;k++){const t=a0+(a1-a0)*k/c.vs;el("line",{x1:X(cx+c.R*Math.cos(t)),y1:Y(cy+c.R*Math.sin(t)),x2:X(cx+(c.R+c.d)*Math.cos(t)),y2:Y(cy+(c.R+c.d)*Math.sin(t)),stroke:ink2,"stroke-width":1},sv);}
  // keystone
  const kt=[a0+(a1-a0)*(c.vs-1)/2/c.vs,a0+(a1-a0)*((c.vs-1)/2+1)/c.vs];
  el("polygon",{points:[kt[0],kt[1]].map(t=>[X(cx+c.R*Math.cos(t)),Y(cy+c.R*Math.sin(t))]).concat([kt[1],kt[0]].map(t=>[X(cx+(c.R+c.d)*Math.cos(t)),Y(cy+(c.R+c.d)*Math.sin(t))])).map(p=>p.join(",")).join(" "),fill:red,opacity:.35,stroke:red},sv);
  // springing line, chord, centre line
  el("line",{x1:X(-c.d)-40,y1:Y(0),x2:X(c.c+c.d)+40,y2:Y(0),stroke:ink2,"stroke-dasharray":"8 5"},sv);
  el("line",{x1:X(cx),y1:Y(c.s+c.d)-20,x2:X(cx),y2:Y(0)+6,stroke:ink2,"stroke-dasharray":"2 4"},sv);
  // ordinates
  c.rows.forEach((r,i)=>{if(i===0&&false)return;[cx-r.x,cx+r.x].forEach((x,j)=>{if(j===1&&i===0)return;
    el("line",{x1:X(x),y1:Y(0),x2:X(x),y2:Y(r.y),stroke:blue,"stroke-width":1.5},sv);el("circle",{cx:X(x),cy:Y(r.y),r:3.5,fill:blue},sv);});});
  // rise dimension
  el("line",{x1:X(cx)+18,y1:Y(0),x2:X(cx)+18,y2:Y(c.s),stroke:red,"stroke-width":1.5},sv);
  el("text",{x:X(cx)+26,y:Y(c.s/2)+4,fill:red,"font-size":14,"font-family":"IBM Plex Mono, monospace"},sv,"rise "+Math.round(c.s));
  el("line",{x1:X(0),y1:Y(0)+30,x2:X(c.c),y2:Y(0)+30,stroke:ink},sv);
  el("text",{x:X(cx),y:Y(0)+50,"text-anchor":"middle",fill:ink,"font-size":14,"font-family":"IBM Plex Mono, monospace"},sv,"span "+Math.round(c.c));
  // radius to the centre if centre visible (inside canvas)
  const cyPix=Y(cy);if(cyPix<410){el("circle",{cx:X(cx),cy:cyPix,r:5,fill:sun,stroke:ink},sv);
    el("line",{x1:X(cx),y1:cyPix,x2:X(c.c),y2:Y(0),stroke:sun,"stroke-width":1.5,"stroke-dasharray":"5 4"},sv);
    el("text",{x:X(cx)+10,y:cyPix+4,fill:ink2,"font-size":13,"font-family":"IBM Plex Mono, monospace"},sv,"centre");}
  else el("text",{x:X(cx),y:408,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,"▼ centre "+mm(c.drop)+" below springing line");
  $("elL").textContent="R "+mm(c.R)+" · "+(c.semi?"semicircular":"segmental")+" arch";
  const tb=$("tb");tb.innerHTML="";c.rows.forEach((r,i)=>{const tr=document.createElement("tr");if(i===0)tr.className="now";tr.innerHTML=`<td>${Math.round(r.x)}</td><td>${Math.round(r.y)}</td><td>${Math.round(r.w)}</td>`;tb.appendChild(tr)});
  const S=[[`R = (${Math.round(c.c)}² ÷ 4 + ${Math.round(c.s)}²) ÷ (2 × ${Math.round(c.s)}) = ${Math.round(c.R)} mm`],
    [`Half-angle θ = asin(${Math.round(c.c)} ÷ ${Math.round(2*c.R)}) = ${fmt(c.th*180/Math.PI,1)}°`],
    [`Arc = 2 × R × θ = ${Math.round(c.arc)} mm`],
    [`Centre is R − rise = ${Math.round(c.drop)} mm below the springing line`],
    [`Each voussoir spans ${fmt(c.arc/c.vs,0)} mm on the intrados (${c.vs} in the ring)`],
    [`Shallow-arch shortcut c² ÷ 8s = ${Math.round(c.c*c.c/(8*c.s))} mm is ${Math.round(100*(c.R-c.c*c.c/(8*c.s))/c.R)}% short of the true radius`]];
  const ul=$("steps");ul.innerHTML="";S.forEach(([t])=>{const li=document.createElement("li");li.innerHTML=`<span>${t}</span>`;ul.appendChild(li)});
}
""")
