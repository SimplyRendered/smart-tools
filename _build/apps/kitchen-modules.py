APP = dict(
slug="kitchen-modules", title="Kitchen Cabinet Modules", h1="Kitchen Cabinet Modules",
sub="Enter the wall length, the sink, hob and appliance spaces and the cabinet widths you can buy. Get the mix of standard modules that fills the run with the smallest fillers, drawn as an elevation and plan, with the next-best options.",
meta=[("Sheet","T-53"),("Method","Exact fill search"),("Units","mm"),("By","@smart_tools_every_week")],
source="Exact search over every combination of the module widths you enter (first principles): the mix that leaves the least filler, then the fewest cabinets, wins. Module widths, the 25 mm minimum wall filler, 600 mm counter depth and the 900 mm counter height drawn are typical modular-kitchen sizes, not code values: change them to suit your maker. Leftover length is split equally between the wall ends.",
inputs="""
      <label for="L">Wall length mm<input id="L" type="number" step="10" value="3250"></label>
      <div class="row">
        <label for="le">Left end
          <select id="le"><option value="w" selected>Wall</option><option value="o">Open</option></select>
        </label>
        <label for="re">Right end
          <select id="re"><option value="w" selected>Wall</option><option value="o">Open</option></select>
        </label>
      </div>
      <label for="mf">Min filler at a wall mm<input id="mf" type="number" step="5" value="25"></label>
      <div class="row">
        <label for="sk">Sink unit mm<input id="sk" type="number" step="50" value="900"></label>
        <label for="hb">Hob unit mm<input id="hb" type="number" step="50" value="600"></label>
      </div>
      <div class="row">
        <label for="dw">Dishwasher mm<input id="dw" type="number" step="50" value="0"></label>
        <label for="tl">Tall / fridge mm<input id="tl" type="number" step="50" value="0"></label>
      </div>
      <label for="ws">Cabinet widths you can buy, mm<input id="ws" type="text" value="150, 300, 450, 600, 750, 900"></label>
      <p class="note">Enter 0 for anything the run does not have. For an L or U kitchen, measure each run from the face of the corner unit and set that end to Open. Fillers let doors and drawers open past the wall and its skirting.</p>
""",
right="""
      <div class="readout">
        <div><b>Filler each end</b><span id="oF" class="hi">–</span></div>
        <div><b>Cabinets</b><span id="oN">–</span></div>
        <div><b>Modules fill</b><span id="oM">–</span></div>
        <div><b>÷ 600 rule gap</b><span id="oU">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Elevation <span id="eLabel"></span></h2><svg id="elev" viewBox="0 0 580 320" role="img" aria-label="Kitchen run elevation with base and wall cabinets, fillers and widths"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Plan <span id="pLabel"></span></h2><svg id="plan" viewBox="0 0 300 230" role="img" aria-label="Plan of the counter with the sink and hob"></svg></div>
        <div class="view"><h2>Filler vs wall <span id="cLabel"></span></h2><svg id="saw" viewBox="0 0 300 230" role="img" aria-label="Filler needed for wall lengths around yours"></svg></div>
      </div>
      <div class="data"><h2>Best mixes <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>#</th><th>Modules</th><th>Cabinets</th><th>Fill</th><th>Filler each end</th><th>Total filler</th></tr></thead><tbody id="tb"></tbody></table></div></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function widths(){const w=[...new Set(($("ws").value||"").split(/[ ,;]+/).map(v=>Math.round(parseFloat(v))).filter(v=>Number.isFinite(v)&&v>=100&&v<=1200))].sort((a,b)=>b-a).slice(0,10);return w.length?w:[900,750,600,450,300,150]}
// fewest cabinets for every reachable sum up to F (unbounded coin change), largest width first on ties
function table(F,W){const cnt=new Int32Array(F+1).fill(1e9),pick=new Int32Array(F+1);cnt[0]=0;
  for(let s=1;s<=F;s++)for(const w of W){if(w<=s&&cnt[s-w]+1<cnt[s]){cnt[s]=cnt[s-w]+1;pick[s]=w}}return {cnt,pick}}
function parts(t,s){const out=[];while(s>0&&out.length<200){out.push(t.pick[s]);s-=t.pick[s]}return out.sort((a,b)=>b-a)}
function solve(L,p,W){const fixed=p.sk+p.hb+p.dw+p.tl,F=Math.floor(L-p.mf*p.nw-fixed);
  if(F<0)return {F,fit:false,mixes:[]};const t=table(F,W),mixes=[];
  for(let s=F;s>=0&&mixes.length<6;s--){if(t.cnt[s]<1e9)mixes.push({s,n:t.cnt[s],m:parts(t,s),left:F-s})}
  return {F,fit:true,mixes}}
function arrange(m,p){ // left -> right sequence of {w,type}
  const mods=[...m],prep=mods.length?mods.shift():null,A=[],B=[];mods.forEach((w,i)=>(i%2?B:A).push(w));
  const seq=[];A.forEach(w=>seq.push({w,t:"m"}));if(p.hb)seq.push({w:p.hb,t:"hob"});if(prep)seq.push({w:prep,t:"m"});
  if(p.sk)seq.push({w:p.sk,t:"sink"});if(p.dw)seq.push({w:p.dw,t:"dw"});B.forEach(w=>seq.push({w,t:"m"}));if(p.tl)seq.push({w:p.tl,t:"tall"});return seq}
function calc(){
  const L=num("L",600,20000,3250),le=$("le").value==="w",re=$("re").value==="w",nw=(le?1:0)+(re?1:0);
  const p={mf:num("mf",0,300,25),sk:num("sk",0,2000,900),hb:num("hb",0,2000,600),dw:num("dw",0,1000,0),tl:num("tl",0,2000,0),nw};
  ["sk","hb","dw","tl"].forEach(k=>p[k]=Math.round(p[k]));const W=widths(),r=solve(L,p,W),best=r.mixes[0]||null;
  const fe=best?(nw?p.mf+best.left/nw:0):0,openGap=best&&!nw?best.left:0;
  const fL=le?fe:0,fR=re?fe:0,seq=best?arrange(best.m,p):[];
  const usualN=Math.floor(L/600),usualGap=L-usualN*600;
  const saw=[];for(let d=-300;d<=300;d+=10){const s=solve(L+d,p,W);saw.push({L:L+d,f:s.fit&&s.mixes.length?s.mixes[0].left+p.mf*nw:null})}
  return {L,le,re,nw,...p,W,r,best,fe,fL,fR,openGap,seq,usualN,usualGap,saw,fixed:p.sk+p.hb+p.dw+p.tl};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),ok=css("--ok"),F="IBM Plex Mono, monospace";
  const OKF="#2F8A57",FIL="#C8432B",SUN="#E09A1E";
  const b=c.best;
  $("oF").textContent=b?(c.nw?fmt(c.fe,0)+" mm":"0 mm"):"won't fit";$("oF").className=b?(c.fe>100?"bad":"ok"):"bad";
  $("oN").textContent=b?b.n+(c.fixed?" + "+[c.sk,c.hb,c.dw,c.tl].filter(v=>v>0).length:""):"–";
  $("oM").textContent=b?b.s+" mm":"–";$("oU").textContent=fmt(c.usualGap,0)+" mm";
  // ---- elevation
  const sv=$("elev");sv.innerHTML="";const k=520/c.L,x0=30,yF=262,X=x=>x0+x*k,Y=y=>yF-y*k*0.62/0.62;
  const hk=Math.min(k,190/2300),Yh=y=>yF-y*hk;
  el("line",{x1:20,y1:yF,x2:560,y2:yF,stroke:ink,"stroke-width":1.6},sv);
  if(c.le)el("rect",{x:x0-10,y:fmt(Yh(2400),1),width:10,height:fmt(2400*hk,1),fill:ink2,opacity:.55},sv);
  if(c.re)el("rect",{x:fmt(X(c.L),1),y:fmt(Yh(2400),1),width:10,height:fmt(2400*hk,1),fill:ink2,opacity:.55},sv);
  el("text",{x:20,y:22,fill:red,"font-size":15,"font-family":F},sv,b?(c.nw?"filler "+fmt(c.fe,0)+" mm at each wall":"no wall fillers, "+fmt(c.openGap,0)+" mm open end")+" · "+b.n+" cabinets + "+c.fixed+" mm fixed":"the fixed units and fillers are longer than the wall");
  el("text",{x:20,y:42,fill:ink2,"font-size":13,"font-family":F},sv,"usual ÷ 600: "+c.usualN+" × 600 + a "+fmt(c.usualGap,0)+" mm gap");
  let x=0;const draw=(w,t)=>{const xa=X(x),ww=w*k;
    if(t==="fil"){el("rect",{x:fmt(xa,1),y:fmt(Yh(900),1),width:fmt(Math.max(0.5,ww),1),height:fmt(900*hk,1),fill:FIL,opacity:.55},sv);
      el("rect",{x:fmt(xa,1),y:fmt(Yh(2200),1),width:fmt(Math.max(0.5,ww),1),height:fmt(700*hk,1),fill:FIL,opacity:.35},sv);x+=w;return}
    if(t==="tall"){el("rect",{x:fmt(xa,1),y:fmt(Yh(2200),1),width:fmt(ww,1),height:fmt(2200*hk,1),fill:"none",stroke:ink,"stroke-width":1.4},sv);
      el("text",{x:fmt(xa+ww/2,1),y:fmt(Yh(1300),1),fill:ink2,"font-size":12,"font-family":F,"text-anchor":"middle"},sv,"tall")}
    else{el("rect",{x:fmt(xa,1),y:fmt(Yh(860),1),width:fmt(ww,1),height:fmt(760*hk,1),fill:"none",stroke:ink,"stroke-width":1.4},sv);
      if(t==="hob"){for(let i=1;i<=3;i++)el("line",{x1:fmt(xa+3,1),y1:fmt(Yh(860-i*190),1),x2:fmt(xa+ww-3,1),y2:fmt(Yh(860-i*190),1),stroke:ink2},sv);
        el("rect",{x:fmt(xa+ww*0.15,1),y:fmt(Yh(2200),1),width:fmt(ww*0.7,1),height:fmt(450*hk,1),fill:"none",stroke:ink2,"stroke-dasharray":"3 3"},sv);
        el("text",{x:fmt(xa+ww/2,1),y:fmt(Yh(1950),1),fill:ink2,"font-size":12,"font-family":F,"text-anchor":"middle"},sv,"hood")}
      else if(t==="dw")el("text",{x:fmt(xa+ww/2,1),y:fmt(Yh(450),1),fill:ink2,"font-size":12,"font-family":F,"text-anchor":"middle"},sv,"DW");
      else{const dn=w>450?2:1;for(let i=1;i<dn;i++)el("line",{x1:fmt(xa+ww*i/dn,1),y1:fmt(Yh(860),1),x2:fmt(xa+ww*i/dn,1),y2:fmt(Yh(100),1),stroke:ink2},sv)}
      if(t==="sink"||t==="hob")el("text",{x:fmt(xa+ww/2,1),y:fmt(Yh(t==="hob"?170:500),1),fill:t==="sink"?blue:SUN,"font-size":12,"font-family":F,"text-anchor":"middle"},sv,t);
      if(t==="sink")el("path",{d:`M${fmt(xa+ww*0.2,1)} ${fmt(Yh(900),1)} q ${fmt(ww*0.3,1)} 10 ${fmt(ww*0.6,1)} 0`,fill:"none",stroke:blue,"stroke-width":2},sv);
      if(t!=="hob"){el("rect",{x:fmt(xa,1),y:fmt(Yh(2200),1),width:fmt(ww,1),height:fmt(700*hk,1),fill:"none",stroke:ink2,"stroke-width":1},sv)}
      el("rect",{x:fmt(xa,1),y:fmt(Yh(100),1),width:fmt(ww,1),height:fmt(100*hk,1),fill:ink2,opacity:.35},sv)}
    el("text",{x:fmt(xa+ww/2,1),y:fmt(yF+16,1),fill:t==="m"?ok:ink,"font-size":ww<30?10:12,"font-family":F,"text-anchor":"middle"},sv,w);x+=w};
  if(b){if(c.fL>0)draw(c.fL,"fil");c.seq.forEach(s=>draw(s.w,s.t));if(c.fR>0)draw(c.fR,"fil");
    el("rect",{x:fmt(X(c.fL),1),y:fmt(Yh(900),1),width:fmt((c.L-c.fL-c.fR-(c.tl||0)-c.openGap)*k,1),height:fmt(40*hk,1),fill:SUN,opacity:.8},sv)}
  el("text",{x:20,y:308,fill:ink2,"font-size":13,"font-family":F},sv,"wall "+Math.round(c.L)+" mm · green = modules · red = fillers · counter 900");
  $("eLabel").textContent=Math.round(c.L)+" mm run";
  // ---- plan
  const pv=$("plan");pv.innerHTML="";const pk=270/c.L,py=70;
  el("rect",{x:15,y:py,width:fmt(c.L*pk,1),height:fmt(600*pk,1),fill:rule,opacity:.35,stroke:ink,"stroke-width":1.2},pv);
  if(b){let px=c.fL;c.seq.forEach(s=>{const xa=15+px*pk,ww=s.w*pk;el("line",{x1:fmt(xa,1),y1:py,x2:fmt(xa,1),y2:fmt(py+600*pk,1),stroke:ink2},pv);
      if(s.t==="hob")[[.3,.3],[.7,.3],[.3,.7],[.7,.7]].forEach(q=>el("circle",{cx:fmt(xa+ww*q[0],1),cy:fmt(py+600*pk*q[1],1),r:fmt(Math.max(1.5,ww*0.12),1),fill:"none",stroke:ink},pv));
      if(s.t==="sink")el("rect",{x:fmt(xa+ww*0.15,1),y:fmt(py+600*pk*0.2,1),width:fmt(ww*0.7,1),height:fmt(600*pk*0.6,1),rx:3,fill:"none",stroke:blue,"stroke-width":1.5},pv);
      px+=s.w});
    if(c.fL>0)el("rect",{x:15,y:py,width:fmt(c.fL*pk,1),height:fmt(600*pk,1),fill:FIL,opacity:.55},pv);
    if(c.fR>0)el("rect",{x:fmt(15+(c.L-c.fR)*pk,1),y:py,width:fmt(c.fR*pk,1),height:fmt(600*pk,1),fill:FIL,opacity:.55},pv)}
  el("text",{x:15,y:fmt(py+600*pk+24,1),fill:ink2,"font-size":12,"font-family":F},pv,"600 deep · "+(b?c.seq.length+" units":"no fit"));
  el("text",{x:15,y:40,fill:ink,"font-size":13,"font-family":F},pv,b?"fill "+b.s+" of "+c.r.F+" mm free":"short by "+fmt(-c.r.F,0)+" mm");
  $("pLabel").textContent=c.le&&c.re?"wall to wall":(c.le||c.re?"one wall":"open");
  // ---- saw chart
  const gv=$("saw");gv.innerHTML="";const vals=c.saw.filter(s=>s.f!=null).map(s=>s.f),fm=Math.max(50,...(vals.length?vals:[0]))*1.1;
  const gx=Lx=>30+(Lx-(c.L-300))/600*255,gy=f=>190-f/fm*165;
  el("line",{x1:30,y1:190,x2:288,y2:190,stroke:ink,"stroke-width":1.2},gv);el("line",{x1:30,y1:20,x2:30,y2:190,stroke:ink,"stroke-width":1.2},gv);
  let d="";c.saw.forEach(s=>{if(s.f==null)return;d+=(d?" L":"M")+fmt(gx(s.L),1)+" "+fmt(gy(s.f),1)});if(d)el("path",{d,fill:"none",stroke:blue,"stroke-width":1.8},gv);
  if(b)el("circle",{cx:fmt(gx(c.L),1),cy:fmt(gy(c.fe*c.nw),1),r:5,fill:OKF},gv);
  [-300,0,300].forEach(o=>el("text",{x:fmt(gx(c.L+o),1),y:206,fill:ink2,"font-size":11,"font-family":F,"text-anchor":"middle"},gv,Math.round(c.L+o)));
  el("text",{x:34,y:16,fill:ink2,"font-size":11,"font-family":F},gv,"total filler mm (max "+fmt(fm/1.1,0)+")");
  el("text",{x:288,y:224,fill:ink2,"font-size":11,"font-family":F,"text-anchor":"end"},gv,"wall length mm");
  $("cLabel").textContent="±300 mm";
  // ---- table
  $("tb").innerHTML=(c.r.mixes.length?c.r.mixes.map((m,i)=>{const fe=c.nw?c.mf+m.left/c.nw:0;return `<tr${i===0?' class="now"':""}><td>${i+1}</td><td>${m.m.join(" + ")||"none"}</td><td>${m.n}</td><td>${m.s}</td><td class="${fe>100?"bad":"ok"}">${c.nw?fmt(fe,0)+" mm":"open "+m.left}</td><td>${fmt(m.left+c.mf*c.nw,0)} mm</td></tr>`}).join(""):`<tr><td colspan="6">The fixed units and fillers need ${fmt(-c.r.F,0)} mm more wall.</td></tr>`)+
    `<tr><td>÷600</td><td>${c.usualN} × 600, no sink or hob sizes</td><td>${c.usualN}</td><td>${c.usualN*600}</td><td class="bad">${fmt(c.usualGap,0)} mm gap</td><td>${fmt(c.usualGap,0)} mm</td></tr>`;
  $("dLabel").textContent="widths "+c.W.slice().sort((a,b)=>a-b).join(", ");
}
""")
