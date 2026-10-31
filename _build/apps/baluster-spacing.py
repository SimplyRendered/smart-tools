APP = dict(
slug="baluster-spacing", title="Baluster & Slat Spacing", h1="Baluster & Slat Spacing",
sub="Enter the railing length, post and baluster sizes and the largest gap allowed. Get the posts, the number of balusters per bay and the exact equal gap, with the site setting-out.",
meta=[("Sheet","T-38"),("Method","Equal gaps per bay"),("Units","mm"),("By","@smart_tools_every_week")],
source="Layout is plain arithmetic: in each bay, gap = (clear bay width − n × baluster width) ÷ (n + 1), with n the fewest balusters that keep the gap within the limit. The 100 mm default sits just inside the 4 in (102 mm) sphere rule for guard openings in IBC 2021 §1015.4; the 1067 mm (42 in) guard height is the IBC 2021 §1015.3 value for most uses. Both are editable: set your own local code values (stairs, schools and homes often differ). Works the same for fence pickets, timber slats and louvres.",
inputs="""
      <div class="row">
        <label for="L">Railing length, mm<input id="L" type="number" step="50" value="4200"></label>
        <label for="mp">Max post spacing, mm<input id="mp" type="number" step="50" value="1500"></label>
      </div>
      <div class="row">
        <label for="pw">Post width, mm<input id="pw" type="number" step="5" value="50"></label>
        <label for="bw">Baluster width, mm<input id="bw" type="number" step="1" value="16"></label>
      </div>
      <div class="row">
        <label for="G">Largest gap allowed, mm<input id="G" type="number" step="1" value="100"></label>
        <label for="gh">Guard height, mm<input id="gh" type="number" step="10" value="1100"></label>
      </div>
      <div class="row">
        <label for="rd">Top rail depth, mm<input id="rd" type="number" step="5" value="40"></label>
        <label for="bg">Gap under bottom rail, mm<input id="bg" type="number" step="5" value="75"></label>
      </div>
      <label for="mh">Minimum guard height by code, mm<input id="mh" type="number" step="10" value="1067"></label>
      <p class="note">Length is the whole run, outer face of the first post to outer face of the last. Posts are spread evenly, then each bay gets its own equal gaps. Set the largest gap and minimum height from the code that applies to you.</p>
""",
right="""
      <div class="readout">
        <div><b>Balusters per bay</b><span id="oN" class="hi">–</span></div>
        <div><b>Equal gap</b><span id="oG">–</span></div>
        <div><b>Pitch, centre to centre</b><span id="oP">–</span></div>
        <div><b>Posts · bays</b><span id="oB">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Elevation <span id="elLabel"></span></h2><svg id="el" viewBox="0 0 960 300" role="img" aria-label="Railing elevation with posts and balusters"></svg></div>
        <div class="view"><h2>Gap detail at a post <span id="dtLabel"></span></h2><svg id="dt" viewBox="0 0 420 380" role="img" aria-label="Detail of the first balusters beside a post with the sphere test"></svg></div>
        <div class="view"><h2>Last gap in a bay <span id="cmLabel"></span></h2><svg id="cm" viewBox="0 0 420 380" role="img" aria-label="Last gap, fixed gap method against equal gaps"></svg></div>
      </div>
      <div class="data"><h2>Quantities and checks <span id="sum"></span></h2><div class="tablewrap"><table><thead><tr><th>Item</th><th>Value</th><th>Check</th></tr></thead><tbody id="tb"></tbody></table></div></div>
      <div class="data"><h2>Setting-out from the post face <span id="sum2"></span></h2><div class="tablewrap"><table><thead><tr><th>Baluster</th><th>Edge from post</th><th>Centre from post</th></tr></thead><tbody id="tb2"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function calc(){
  const L=num("L",300,30000,4200),mp=num("mp",300,3000,1500),pw=num("pw",20,100,50),bw=num("bw",5,100,16),G=num("G",30,300,100);
  const gh=num("gh",300,2000,1100),rd=num("rd",0,200,40),bg=num("bg",0,300,75),mh=num("mh",300,2000,1067);
  const bays=Math.max(1,Math.ceil((L-pw)/mp-1e-9)),cc=(L-pw)/bays,clear=cc-pw;
  let n=Math.max(0,Math.ceil((clear-G)/(bw+G)-1e-9));
  while(n>0&&(clear-n*bw)/(n+1)<3)n--;
  const g=(clear-n*bw)/(n+1),pitch=bw+g;
  // the usual way: fixed gap G from the post, last gap is what is left
  const nu=Math.max(0,Math.floor((clear-G)/(bw+G)+1e-9)),lastU=clear-nu*(bw+G);
  const blen=Math.max(50,gh-rd-bg);
  return {L,mp,pw,bw,G,gh,rd,bg,mh,bays,cc,clear,n,g,pitch,nu,lastU,blen,total:bays*n,posts:bays+1};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sheet=css("--sheet"),ok=css("--ok"),bad=css("--bad"),sun=css("--sun");
  const gOk=c.g<=c.G+1e-9,bOk=c.bg<=c.G+1e-9,hOk=c.gh>=c.mh;
  $("oN").textContent=c.n;$("oG").textContent=fmt(c.g,1)+" mm";$("oG").className=gOk?"ok":"bad";
  $("oP").textContent=fmt(c.pitch,1)+" mm";$("oB").textContent=c.posts+" · "+c.bays;
  const M=(sv,x,y,t,col,a,s)=>el("text",{x,y,fill:col||ink2,"font-size":s||12,"text-anchor":a||"start","font-family":"IBM Plex Mono, monospace"},sv,t);
  // elevation
  const sv=$("el");sv.innerHTML="";const k=Math.min(900/c.L,0.6),W=c.L*k,x0=(960-W)/2,H=c.gh*k,vh=Math.round(H+90);
  sv.setAttribute("viewBox","0 0 960 "+vh);const gy=H+30;
  const X=v=>x0+v*k;
  el("line",{x1:20,y1:gy,x2:940,y2:gy,stroke:ink,"stroke-width":2},sv);
  // rails
  el("rect",{x:X(0),y:gy-H,width:W,height:Math.max(2,c.rd*k),fill:ink2,opacity:.85},sv);
  const by=gy-c.bg*k-1.5;el("rect",{x:X(0),y:by-Math.max(2,c.rd*k*0.8),width:W,height:Math.max(2,c.rd*k*0.8),fill:ink2,opacity:.85},sv);
  for(let i=0;i<c.bays;i++){
    const left=i*c.cc+c.pw;
    for(let j=0;j<c.n;j++){const bx=left+c.g+j*c.pitch;el("rect",{x:X(bx),y:gy-H+c.rd*k,width:Math.max(0.8,c.bw*k),height:Math.max(2,c.blen*k),fill:blue,opacity:.8},sv)}
  }
  for(let i=0;i<=c.bays;i++)el("rect",{x:X(i*c.cc),y:gy-H-4,width:Math.max(2,c.pw*k),height:H+4,fill:ink},sv);
  el("line",{x1:X(0),y1:gy+22,x2:X(c.L),y2:gy+22,stroke:ink2},sv);M(sv,X(c.L/2),gy+40,fmt(c.L,0)+" mm · "+c.bays+" bay"+(c.bays>1?"s":"")+" of "+fmt(c.cc,0)+" mm post to post",ink2,"middle");
  el("line",{x1:X(c.L)+16,y1:gy,x2:X(c.L)+16,y2:gy-H,stroke:ink2},sv);M(sv,Math.min(X(c.L)+22,880),gy-H/2,fmt(c.gh,0),ink2);
  $("elLabel").textContent=c.total+" balusters";
  // detail: post face, 2 balusters, sphere
  const d=$("dt");d.innerHTML="";const span=c.pw*0.6+c.g*2+c.bw*2+Math.max(c.G*0.7,20),k2=400/span,dx=10,dy=60;
  const D=v=>dx+v*k2;let x=0;
  const hh=Math.min(300,Math.max(c.G*1.6,120)*k2);
  el("rect",{x:D(0),y:dy,width:c.pw*0.6*k2,height:hh,fill:ink},d);x=c.pw*0.6;
  const gaps=[];
  for(let j=0;j<2;j++){gaps.push([x,c.g]);x+=c.g;el("rect",{x:D(x),y:dy,width:c.bw*k2,height:hh,fill:blue,opacity:.8},d);x+=c.bw}
  gaps.push([x,c.g]);
  const sy=dy+hh*0.45,sr=c.G/2*k2;
  const g0=gaps[0];el("circle",{cx:D(g0[0]+g0[1]/2),cy:sy,r:sr,fill:"none",stroke:gOk?ok:bad,"stroke-width":2,"stroke-dasharray":"6 4"},d);
  gaps.forEach((g,i)=>{el("line",{x1:D(g[0]),y1:dy+hh+14,x2:D(g[0]+g[1]),y2:dy+hh+14,stroke:ink2},d);M(d,D(g[0]+g[1]/2),dy+hh+32,fmt(c.g,1),ink,"middle",12)});
  M(d,10,30,"Ø"+fmt(c.G,0)+" mm test sphere",gOk?ok:bad,"start",14);
  M(d,10,48,gOk?"cannot pass between balusters":"passes through: too wide",gOk?ok:bad,"start",12);
  M(d,10,dy+hh+62,"post · gap · baluster · gap · baluster · gap",ink2,"start",11);
  $("dtLabel").textContent="";
  // comparison bars
  const s2=$("cm");s2.innerHTML="";const mx=Math.max(c.lastU,c.g,c.G)*1.25,bw2=300/mx;
  const bar=(y,label,v,col)=>{const t=M(s2,20,y-8,label,ink2,"start",12);t.setAttribute("stroke",sheet);t.setAttribute("stroke-width",4);t.setAttribute("paint-order","stroke");el("rect",{x:20,y:y,width:Math.max(2,v*bw2),height:34,fill:col,opacity:.85},s2);M(s2,28+v*bw2,y+23,fmt(v,1)+" mm",ink,"start",14)};
  {const lx0=20+c.G*bw2;el("line",{x1:lx0,y1:50,x2:lx0,y2:250,stroke:sun,"stroke-width":2,"stroke-dasharray":"6 4"},s2)}
  bar(80,"Fixed "+fmt(c.G,0)+" mm gaps, leftover at the end",c.lastU,c.lastU<=c.G+1e-9?ok:bad);
  bar(170,"Equal gaps (this tool)",c.g,gOk?ok:bad);
  const lx=20+c.G*bw2;M(s2,lx-4,270,"limit "+fmt(c.G,0)+" mm",sun,"end",12);
  M(s2,20,320,"Fixed method: "+c.nu+" balusters, last gap "+fmt(c.lastU,1)+" mm.",ink2,"start",12);
  M(s2,20,338,"Equal method: "+c.n+" balusters, every gap "+fmt(c.g,1)+" mm.",ink2,"start",12);
  $("cmLabel").textContent="per bay";
  // tables
  const pill=(t,good)=>`<td class="${good?"ok":"bad"}">${t}</td>`;
  const rows=[
    ["Posts ("+fmt(c.pw,0)+" mm)",c.posts+" at "+fmt(c.cc,1)+" mm centres",pill(c.cc<=c.mp+1e-9?"within "+fmt(c.mp,0):"too far",c.cc<=c.mp+1e-9)],
    ["Clear width of each bay",fmt(c.clear,1)+" mm",""],
    ["Balusters",c.total+" ("+c.n+" per bay) at "+fmt(c.pitch,1)+" mm pitch",""],
    ["Gap between balusters",fmt(c.g,1)+" mm",pill(gOk?"≤ "+fmt(c.G,0)+" mm":"over "+fmt(c.G,0),gOk)],
    ["Gap under the bottom rail",fmt(c.bg,0)+" mm",pill(bOk?"≤ "+fmt(c.G,0)+" mm":"over "+fmt(c.G,0),bOk)],
    ["Guard height",fmt(c.gh,0)+" mm",pill(hOk?"≥ "+fmt(c.mh,0)+" mm":"below "+fmt(c.mh,0),hOk)],
    ["Baluster length",fmt(c.blen,0)+" mm × "+c.total,"<td>cut list</td>"],
    ["Top and bottom rail",fmt(c.L-2*0,0)+" mm each, in "+c.bays+" piece"+(c.bays>1?"s":""),""]
  ];
  $("tb").innerHTML=rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td>${r[2]||"<td></td>"}</tr>`).join("");
  const show=Math.min(c.n,12),r2=[];
  for(let j=0;j<show;j++){const e=c.g+j*c.pitch;r2.push(`<tr><td>${j+1}</td><td>${fmt(e,1)} mm</td><td>${fmt(e+c.bw/2,1)} mm</td></tr>`)}
  if(c.n>show)r2.push(`<tr><td colspan="3" style="text-align:left;color:var(--ink-2)">… and ${c.n-show} more at ${fmt(c.pitch,1)} mm pitch. Every bay is the same.</td></tr>`);
  if(c.n===0)r2.push(`<tr><td colspan="3" style="text-align:left;color:var(--ink-2)">The bay is narrow enough that no baluster is needed.</td></tr>`);
  $("tb2").innerHTML=r2.join("");
  $("sum").textContent="";$("sum2").textContent="same in every bay";
}
""")
