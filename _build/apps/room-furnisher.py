APP = dict(
slug="room-furnisher", title="Room Furnisher: Auto Furniture Layout", h1="Room Furnisher",
sub="Enter the room, door and window. It arranges standard furniture automatically with walking clearances, and shows other layouts that also work.",
meta=[("Sheet","T-14"),("Method","Clearance rules"),("Units","mm"),("By","@smart_tools_every_week")],
source="Furniture sizes and clearances from standard references: Panero & Zelnik, Human Dimension & Interior Space; Neufert, Architects' Data; Time-Saver Standards. A starting layout, not a final design.",
inputs="""
      <label for="type">Room
        <select id="type"><option value="bed" selected>Bedroom</option><option value="living">Living room</option><option value="dining">Dining room</option><option value="study">Study / home office</option></select>
      </label>
      <div class="row">
        <label for="L">Length mm <span id="Lv" class="time" style="font-size:16px"></span><input id="L" type="number" step="50" value="4200"></label>
        <label for="W">Width mm<input id="W" type="number" step="50" value="3600"></label>
      </div>
      <label for="opt">Main piece
        <select id="opt"></select>
      </label>
      <div class="row" style="grid-template-columns:1fr 1fr 1fr">
        <label for="dwall">Door wall<select id="dwall"><option value="0">Top</option><option value="1">Right</option><option value="2" selected>Bottom</option><option value="3">Left</option></select></label>
        <label for="dpos">Door at mm<input id="dpos" type="number" step="50" value="300"></label>
        <label for="dwid">Door mm<input id="dwid" type="number" step="50" value="900"></label>
      </div>
      <div class="row" style="grid-template-columns:1fr 1fr 1fr">
        <label for="wwall">Window wall<select id="wwall"><option value="0" selected>Top</option><option value="1">Right</option><option value="2">Bottom</option><option value="3">Left</option><option value="-1">None</option></select></label>
        <label for="wpos">Window at mm<input id="wpos" type="number" step="50" value="1350"></label>
        <label for="wwid">Window mm<input id="wwid" type="number" step="50" value="1500"></label>
      </div>
      <label for="path">Walkway width mm<input id="path" type="number" step="50" value="750"></label>
      <div class="chips"><button type="button" id="prev">← Previous</button><button type="button" id="next">Next layout →</button></div>
      <p class="note">"Door at" and "Window at" are measured along the wall from its left end (top and bottom walls) or its top end (side walls). Tall pieces (wardrobes, shelves) are kept off the window. Clearance zones are shaded; they may overlap each other but never a piece of furniture or the door swing.</p>
""",
right="""
      <div class="readout">
        <div><b>Layout</b><span id="oK" class="hi">–</span></div>
        <div><b>Pieces placed</b><span id="oP">–</span></div>
        <div><b>Floor used</b><span id="oF">–</span></div>
        <div><b>Free floor</b><span id="oFree">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Plan <span id="planLabel"></span></h2><svg id="plan" viewBox="0 0 840 520" role="img" aria-label="Furnished room plan with clearances"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>Checks <span id="sum"></span></h2><ul class="checks" id="checks"></ul></div>
        <div class="view"><h2>Furniture <span>size and wall</span></h2><div class="tablewrap"><table><thead><tr><th>Piece</th><th>Size</th><th>Clear in front</th></tr></thead><tbody id="tbl"></tbody></table></div></div>
      </div>
""",
css=".view.full svg{max-height:520px} #dwall,#wwall{font-size:13px;padding:9px 4px}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
// w = along the wall, d = depth from the wall, f = clearance in front, s = clearance at the sides, tall = keep off windows
const OPTS={bed:[["queen","Queen bed 1500 × 2000"],["king","King bed 1800 × 2000"],["single","Single bed 900 × 1900"]],
  living:[["s3","3-seat sofa 2100"],["s2","2-seat sofa 1600"],["l","L-sofa 2400 × 1600"]],
  dining:[["4","4 seats, table 1200 × 800"],["6","6 seats, table 1800 × 900"],["8","8 seats, table 2400 × 1000"]],
  study:[["one","One desk 1400 × 700"],["two","Two desks side by side"]]};
function fillOpts(){const t=$("type").value,o=$("opt");o.innerHTML="";OPTS[t].forEach(([v,n])=>{const e=document.createElement("option");e.value=v;e.textContent=n;o.appendChild(e)});
  const dflt={bed:[4200,3600],living:[5000,4000],dining:[4000,3500],study:[3300,3000]}[t];$("L").value=dflt[0];$("W").value=dflt[1];
  $("wpos").value=Math.max(0,Math.round(((+$("wwall").value%2===0?dflt[0]:dflt[1])-1500)/2/50)*50);}
$("type").addEventListener("change",()=>{fillOpts();idx=0;render()});
function pieces(t,o){
  if(t==="bed"){const B={queen:[1500,2000],king:[1800,2000],single:[900,1900]}[o];const dbl=o!=="single";
    return [{id:"bed",n:o==="single"?"Single bed":o==="king"?"King bed":"Queen bed",w:B[0],d:B[1],f:600,s:dbl?600:0,sOne:!dbl?600:0,anchor:1,nt:dbl?2:1},
      {id:"ward",n:"Wardrobe",w:o==="king"?2400:1800,d:600,f:900,tall:1,need:1},{id:"desk",n:"Dresser / desk",w:1000,d:500,f:750,opt:1},{id:"chair",n:"Easy chair",w:750,d:750,f:450,opt:1}];}
  if(t==="living"){const S={s3:[2100,900],s2:[1600,900],l:[2400,900]}[o];
    return [{id:"sofa",n:o==="l"?"L-sofa":o==="s2"?"2-seat sofa":"3-seat sofa",w:S[0],d:S[1],f:1500,anchor:1,L:o==="l"?1600:0,ct:1},
      {id:"tv",n:"TV unit",w:1800,d:450,f:0,face:1,need:1},{id:"arm",n:"Armchair",w:800,d:800,f:450,opt:1,near:1},{id:"arm2",n:"Armchair",w:800,d:800,f:450,opt:1,near:1},{id:"shelf",n:"Bookshelf",w:900,d:350,f:750,tall:1,opt:1}];}
  if(t==="dining"){const T={"4":[1200,800,2],"6":[1800,900,3],"8":[2400,1000,4]}[o];
    return [{id:"table",n:"Dining table",w:T[0],d:T[1],free:1,chairs:T[2],anchor:1},{id:"side",n:"Sideboard",w:1500,d:450,f:900,need:1},{id:"crock",n:"Crockery unit",w:1000,d:450,f:900,tall:1,opt:1}];}
  const two=o==="two";
  return [{id:"desk",n:two?"Desks (×2)":"Desk",w:two?2800:1400,d:700,f:900,anchor:1},{id:"shelf",n:"Bookshelf",w:1000,d:350,f:750,tall:1,need:1},{id:"shelf2",n:"Bookshelf",w:1000,d:350,f:750,tall:1,opt:1},{id:"read",n:"Reading chair",w:800,d:800,f:450,opt:1},{id:"cab",n:"Filing cabinet",w:500,d:600,f:750,opt:1}];
}
const E=1;
const ov=(a,b)=>a.x<b.x+b.w-E&&b.x<a.x+a.w-E&&a.y<b.y+b.h-E&&b.y<a.y+a.h-E;
const inRoom=(r,L,W)=>r.x>=-E&&r.y>=-E&&r.x+r.w<=L+E&&r.y+r.h<=W+E;
const clip=(r,L,W)=>{const x=Math.max(0,r.x),y=Math.max(0,r.y);return {x,y,w:Math.max(0,Math.min(L,r.x+r.w)-x),h:Math.max(0,Math.min(W,r.y+r.h)-y)}};
// rectangle against wall k (0 top,1 right,2 bottom,3 left), 'a' = offset along the wall, piece w along / d deep; zone of depth c in front
function onWall(k,a,w,d,c,L,W){
  if(k===0)return {r:{x:a,y:0,w,h:d},z:{x:a,y:d,w,h:c},sideA:(s,from)=>({x:a-s,y:from,w:s,h:d-from}),sideB:(s,from)=>({x:a+w,y:from,w:s,h:d-from})};
  if(k===2)return {r:{x:a,y:W-d,w,h:d},z:{x:a,y:W-d-c,w,h:c},sideA:(s,from)=>({x:a-s,y:W-d,w:s,h:d-from}),sideB:(s,from)=>({x:a+w,y:W-d,w:s,h:d-from})};
  if(k===3)return {r:{x:0,y:a,w:d,h:w},z:{x:d,y:a,w:c,h:w},sideA:(s,from)=>({x:from,y:a-s,w:d-from,h:s}),sideB:(s,from)=>({x:from,y:a+w,w:d-from,h:s})};
  return {r:{x:L-d,y:a,w:d,h:w},z:{x:L-d-c,y:a,w:c,h:w},sideA:(s,from)=>({x:L-d,y:a-s,w:d-from,h:s}),sideB:(s,from)=>({x:L-d,y:a+w,w:d-from,h:s})};
}
const wallLen=(k,L,W)=>k%2===0?L:W;
function openings(L,W){
  const dk=+$("dwall").value,dl=wallLen(dk,L,W),dwid=Math.min(num("dwid",500,3000,900),dl),dpos=Math.min(num("dpos",0,40000,300),dl-dwid);
  const door=onWall(dk,dpos,dwid,0,dwid,L,W).z; // swing square inside the room
  const wk=+$("wwall").value;let win=null;if(wk>=0){const wl=wallLen(wk,L,W),ww=Math.min(num("wwid",300,20000,1500),wl),wp=Math.min(num("wpos",0,40000,1350),wl-ww);win={k:wk,a:wp,w:ww,r:onWall(wk,wp,ww,0,450,L,W).z}}
  return {dk,dpos,dwid,door,win};
}
function tryPlace(p,k,a,ctx){
  const {L,W,placed,zones,op}=ctx;const g=onWall(k,a,p.w,p.d,p.f||0,L,W);const rects=[g.r];const zs=[];
  if(p.f)zs.push(g.z);
  if(p.s){zs.push(g.sideA(p.s,450),g.sideB(p.s,450))}
  const fr=(off,len,ds,dl)=>k===0?{x:a+off,y:ds,w:len,h:dl}:k===2?{x:a+off,y:W-ds-dl,w:len,h:dl}:k===3?{x:ds,y:a+off,w:dl,h:len}:{x:L-ds-dl,y:a+off,w:dl,h:len};
  if(p.nt){rects.push(fr(-450,450,0,400));if(p.nt===2)rects.push(fr(p.w,450,0,400));}
  if(p.L)rects.push(fr(p.w-p.d,p.d,0,p.L));
  if(p.ct){const av=p.L?p.w-p.d:p.w;rects.push(fr((av-1100)/2,1100,p.d+450,600));}
  if(p.sOne)zs.push(g.sideB(p.sOne,450));
  for(const r of rects){if(!inRoom(r,L,W))return null;if(ov(r,op.door))return null;if(p.tall&&op.win&&ov(r,op.win.r))return null;
    for(const q of placed)for(const qr of q.rects)if(ov(r,qr))return null;for(const z of zones)if(ov(r,z))return null;}
  for(const z of zs){const c=clip(z,L,W);if(c.w*c.h<0.6*z.w*z.h)return null;for(const q of placed)for(const qr of q.rects)if(ov(z,qr))return null;}
  return {p,k,a,rects,zs};
}
function placeFree(p,ctx){// dining table: centred if possible, else the nearest spot clear of the door; 600 chair zone, walkway beyond
  const {L,W,op}=ctx;let best=null,bd=Infinity;
  for(let dx=-2000;dx<=2000;dx+=100)for(let dy=-2000;dy<=2000;dy+=100){
    const r={x:(L-p.w)/2+dx,y:(W-p.d)/2+dy,w:p.w,h:p.d};const cz={x:r.x-600,y:r.y-600,w:r.w+1200,h:r.h+1200};
    if(!inRoom(cz,L,W)||ov(cz,op.door))continue;const wz={x:cz.x-ctx.path,y:cz.y-ctx.path,w:cz.w+2*ctx.path,h:cz.h+2*ctx.path};
    const d=Math.hypot(dx,dy)+(ov(wz,op.door)?0:0);if(d<bd){bd=d;best={p,k:-1,a:0,rects:[r],zs:[cz],chairZ:cz,walk:wz}}}
  return best;
}
function solve(){
  const t=$("type").value,o=$("opt").value,L=num("L",1500,20000,4200),W=num("W",1500,20000,3600),path=num("path",500,1500,750);
  const op=openings(L,W);const P=pieces(t,o);const results=[];
  const anchor=P[0],rest=P.slice(1);
  const anchorCands=[];
  if(anchor.free){const r=placeFree(anchor,{L,W,op,path});if(r)anchorCands.push(r)}
  else for(let k=0;k<4;k++){const len=wallLen(k,L,W);[ (len-anchor.w)/2, 0+(anchor.s||anchor.nt?450+(anchor.s?0:0):0), len-anchor.w-(anchor.s||anchor.nt?450:0)].forEach(a=>{a=Math.round(a/50)*50;if(a<0||a+anchor.w>len)return;
      const r=tryPlace(anchor,k,a,{L,W,placed:[],zones:[],op});if(r)anchorCands.push(r)})}
  for(const ac of anchorCands){
    for(const order of [0,1]){
      const placed=[ac];let zones=[...ac.zs];const miss=[];
      for(const p of rest){let best=null,bs=Infinity;
        const walls=[0,1,2,3].sort((x,y)=>order?y-x:x-y);
        for(const k of walls){const len=wallLen(k,L,W);if(p.w>len)continue;
          const steps=[];for(let a=0;a<=len-p.w;a+=50)steps.push(a);if(steps[steps.length-1]!==len-p.w)steps.push(len-p.w);
          // TV faces the sofa: same axis on the opposite wall
          for(const a of steps){const r=tryPlace(p,k,a,{L,W,placed,zones,op});if(!r)continue;
            let sc=Math.min(a,len-p.w-a);// prefer corners
            if(p.face){const sk=ac.k;if(k!==(sk+2)%4){sc+=1e6}else{const sofaMid=ac.a+ac.p.w/2;sc=Math.abs(a+p.w/2-sofaMid)}}
            if(p.near){const c=ac.rects[ac.rects.length-1],q=r.rects[0];sc=Math.hypot(q.x+q.w/2-c.x-c.w/2,q.y+q.h/2-c.y-c.h/2)}
            if(p.tall&&k===ac.k)sc+=500;
            if(order)sc+=k===op.dk?300:0;
            if(sc<bs){bs=sc;best=r}}}
        if(best){placed.push(best);zones.push(...best.zs)}else miss.push(p);}
      const needMiss=miss.filter(p=>!p.opt).length;
      const key=placed.map(q=>q.p.id+":"+q.k+":"+Math.round(q.a/100)).join("|");
      let pen=needMiss*10000+miss.length*1000;if(anchor.anchor&&ac.k===op.dk)pen+=400;if(op.win&&ac.k===op.win.k&&t==="bed")pen+=150;
      if(!anchor.free){const len=wallLen(ac.k,L,W);pen+=Math.abs(ac.a+ac.p.w/2-len/2)/10}
      if(!results.some(r=>r.key===key))results.push({key,placed,miss,pen});
    }}
  results.sort((x,y)=>x.pen-y.pen);
  return {t,o,L,W,path,op,P,results};
}
let idx=0;
$("next").addEventListener("click",()=>{idx++;render()});$("prev").addEventListener("click",()=>{idx--;render()});
const WN=["top","right","bottom","left"];
function render(){
  const s=solve(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),paper=css("--paper"),okc=css("--ok");
  const n=s.results.length;if(n)idx=((idx%n)+n)%n;const R=n?s.results[idx]:null;
  $("Lv").textContent=fmt(s.L/1000,1)+" × "+fmt(s.W/1000,1)+" m";
  $("oK").textContent=n?(idx+1)+" of "+n:"none fits";
  const all=s.P.length,pl=R?R.placed.length:0;$("oP").textContent=pl+" / "+all;
  let used=0;if(R)R.placed.forEach(q=>q.rects.forEach(r=>used+=r.w*r.h));const area=s.L*s.W;
  $("oF").textContent=fmt(100*used/area,0)+"%";$("oFree").textContent=fmt((area-used)/1e6,1)+" m²";
  // checks
  const C=[];
  if(!R){C.push(["The main piece doesn't fit with its clearances. Try a smaller size or a bigger room",false])}
  else{
    C.push([`${s.P[0].n} fits with ${s.P[0].f?s.P[0].f+" mm in front":"600 mm chair space all round"}${s.P[0].s?" and "+s.P[0].s+" mm each side":""}`,true]);
    R.miss.forEach(p=>C.push([`${p.n} left out: no wall space with ${p.f} mm clear in front`,!!p.opt,p.opt?"warn":""]));
    if(s.t==="dining"){const a=R.placed[0];const w=a.walk;const okW=inRoom(w,s.L,s.W);C.push([`${s.path} mm walkway behind the chairs all round`,okW,"warn"])}
    if(s.t==="living"){const tv=R.placed.find(q=>q.p.id==="tv"),sofa=R.placed[0];if(tv){const dist=sofa.k%2===0?Math.abs((tv.rects[0].y+tv.rects[0].h/2)-(sofa.rects[0].y+sofa.rects[0].h/2)):Math.abs((tv.rects[0].x+tv.rects[0].w/2)-(sofa.rects[0].x+sofa.rects[0].w/2));
      C.push([`Sofa to TV ${fmt(dist/1000,2)} m. Screens up to ${Math.round(dist/1.6/25.4)} inch fill a 30° view (SMPTE)`,dist>=1800,"warn"])}}
    if(s.t==="bed"&&s.P[0].s)C.push(["600 mm each side of the bed so two people can get in",true]);
    C.push(["Door swing kept clear",true]);
    if(s.op.win)C.push(["Wardrobes and shelves kept off the window",true]);
  }
  const ul=$("checks");ul.innerHTML="";let fails=0;
  C.forEach(([t,okk,kind])=>{const li=document.createElement("li");const cls=okk?"ok":kind==="warn"?"warn":"bad";if(!okk&&kind!=="warn")fails++;
    li.innerHTML=`<span>${t}</span><span class="pill ${cls}">${okk?"pass":kind==="warn"?"check":"fail"}</span>`;ul.appendChild(li)});
  $("sum").textContent=fails?fails+" problem"+(fails>1?"s":""):"works";
  // PLAN
  const sv=$("plan");sv.innerHTML="";const sc=Math.min(780/s.L,460/s.W),ox=(840-s.L*sc)/2,oy=(500-s.W*sc)/2+10;
  const X=v=>ox+v*sc,Y=v=>oy+v*sc;const rr=(r,at)=>el("rect",Object.assign({x:X(r.x),y:Y(r.y),width:Math.max(0,r.w*sc),height:Math.max(0,r.h*sc)},at),sv);
  rr({x:0,y:0,w:s.L,h:s.W},{fill:paper});
  if(R){R.placed.forEach(q=>q.zs.forEach(z=>rr(clip(z,s.L,s.W),{fill:okc,opacity:.10,stroke:okc,"stroke-opacity":.35,"stroke-dasharray":"4 3"})));
    if(R.placed[0].walk)rr(clip(R.placed[0].walk,s.L,s.W),{fill:"none",stroke:blue,"stroke-dasharray":"6 4","stroke-opacity":.6});}
  // door swing
  const d=s.op.door;rr(d,{fill:red,opacity:.08});
  const dk=s.op.dk,hinge=dk===0?[d.x,d.y]:dk===2?[d.x,d.y+d.h]:dk===3?[d.x,d.y]:[d.x+d.w,d.y];
  const leafEnd=dk===0?[d.x,d.y+d.h]:dk===2?[d.x,d.y]:dk===3?[d.x+d.w,d.y]:[d.x,d.y],openEnd=dk===0?[d.x+d.w,d.y]:dk===2?[d.x+d.w,d.y+d.h]:dk===3?[d.x,d.y+d.h]:[d.x+d.w,d.y+d.h];
  el("line",{x1:X(hinge[0]),y1:Y(hinge[1]),x2:X(leafEnd[0]),y2:Y(leafEnd[1]),stroke:red,"stroke-width":2},sv);
  el("path",{d:`M${X(leafEnd[0])} ${Y(leafEnd[1])} A${d.w*sc} ${d.w*sc} 0 0 ${dk===0||dk===1?0:1} ${X(openEnd[0])} ${Y(openEnd[1])}`,fill:"none",stroke:red,"stroke-width":1,"stroke-dasharray":"3 3"},sv);
  // walls
  rr({x:0,y:0,w:s.L,h:s.W},{fill:"none",stroke:ink,"stroke-width":4});
  const gap=(k,a,w,col,wd)=>{const p=k===0?[a,0,a+w,0]:k===2?[a,s.W,a+w,s.W]:k===3?[0,a,0,a+w]:[s.L,a,s.L,a+w];el("line",{x1:X(p[0]),y1:Y(p[1]),x2:X(p[2]),y2:Y(p[3]),stroke:col,"stroke-width":wd},sv)};
  gap(dk,s.op.dpos,s.op.dwid,paper,6);
  if(s.op.win){gap(s.op.win.k,s.op.win.a,s.op.win.w,paper,6);gap(s.op.win.k,s.op.win.a,s.op.win.w,blue,2)}
  if(R)R.placed.forEach(q=>{q.rects.forEach((r,i)=>{rr(r,{fill:q.p.tall?rule:css("--sheet"),stroke:ink,"stroke-width":1.5});});
    const r=q.rects[0];
    if(q.p.id==="table"){const ch=q.p.chairs;for(let i=0;i<ch;i++){const cx=r.x+(i+0.5)*r.w/ch-225;rr({x:cx,y:r.y-500,w:450,h:450},{fill:"none",stroke:ink2});rr({x:cx,y:r.y+r.h+50,w:450,h:450},{fill:"none",stroke:ink2});}}
    if(q.p.id==="bed"){const pil=q.k===0?{x:r.x+80,y:r.y+80,w:r.w-160,h:350}:q.k===2?{x:r.x+80,y:r.y+r.h-430,w:r.w-160,h:350}:q.k===3?{x:r.x+80,y:r.y+80,w:350,h:r.h-160}:{x:r.x+r.w-430,y:r.y+80,w:350,h:r.h-160};rr(pil,{fill:"none",stroke:ink2})}
    const fs=Math.max(9,Math.min(13,Math.min(r.w,r.h)*sc/5));
    el("text",{x:X(r.x+r.w/2),y:Y(r.y+r.h/2)+4,"text-anchor":"middle",fill:ink,"font-size":fs,"font-weight":600,"font-family":"IBM Plex Sans, sans-serif"},sv,q.p.n.replace(/ \(.*\)/,""));});
  el("text",{x:X(s.L/2),y:Y(0)-6,"text-anchor":"middle",fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,s.L+" mm");
  el("text",{x:X(0)-6,y:Y(s.W/2),"text-anchor":"end",fill:ink2,"font-size":12,"font-family":"IBM Plex Mono, monospace"},sv,s.W+"");
  $("planLabel").textContent="green = clearance zones · red = door swing";
  const tb=$("tbl");tb.innerHTML="";s.P.forEach(p=>{const q=R&&R.placed.find(x=>x.p===p);const tr=document.createElement("tr");
    tr.innerHTML=`<td>${p.n}</td><td>${p.w} × ${p.d}${p.L?" + "+p.L:""}</td><td class="${q?"ok":"bad"}">${q?(p.free?"600 chairs":p.f?p.f+" mm":"–")+" · "+(q.k>=0?WN[q.k]:"centre"):"not placed"}</td>`;tb.appendChild(tr)});
}
fillOpts();
""")
