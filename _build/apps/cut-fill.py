APP = dict(
slug="cut-fill", title="Cut & Fill for a Sloping Plot", h1="Cut & Fill",
sub="Sloping plot? Set the four corner levels and the building pad. Get cut, fill, the balanced pad level and how many truckloads of earth leave or arrive, with contours and a live section.",
meta=[("Sheet","T-18"),("Method","Grid volumes"),("Units","m / m³"),("By","@smart_tools_every_week")],
source="Ground modelled as a bilinear surface through the four corner levels; volumes by fine grid integration over the pad (the grid / borrow-pit method). Swell (bank to loose) and shrinkage (bank to compacted) are typical textbook values (e.g. Peurifoy, Construction Planning, Equipment and Methods); test your soil. Side slopes beyond the pad and topsoil strip are not included.",
inputs="""
      <div class="row">
        <label for="W">Plot width m<input id="W" type="number" step="0.5" value="15"></label>
        <label for="D">Plot depth m<input id="D" type="number" step="0.5" value="25"></label>
      </div>
      <div class="row">
        <label for="la">Level rear-left m<input id="la" type="number" step="0.05" value="101.5"></label>
        <label for="lb">Level rear-right m<input id="lb" type="number" step="0.05" value="101.2"></label>
      </div>
      <div class="row">
        <label for="lc">Level front-left m<input id="lc" type="number" step="0.05" value="99.6"></label>
        <label for="ld">Level front-right m<input id="ld" type="number" step="0.05" value="99.4"></label>
      </div>
      <div class="row">
        <label for="pw">Pad width m<input id="pw" type="number" step="0.5" value="10"></label>
        <label for="pd">Pad depth m<input id="pd" type="number" step="0.5" value="14"></label>
      </div>
      <div class="row">
        <label for="px">Pad from left m<input id="px" type="number" step="0.5" value="2.5"></label>
        <label for="py">Pad from rear m<input id="py" type="number" step="0.5" value="5.5"></label>
      </div>
      <label for="pl">Pad level m <span id="plv" class="time" style="font-size:18px"></span><input id="pl" type="range" min="98" max="103" step="0.05" value="100.45"></label>
      <button type="button" id="bal">Set to balanced level</button>
      <div class="row">
        <label for="soil">Soil · swell
          <select id="soil"><option value="12">Sand · 12%</option><option value="25" selected>Earth · 25%</option><option value="40">Clay · 40%</option><option value="50">Hardpan · 50%</option></select>
        </label>
        <label for="sh">Shrinkage %<input id="sh" type="number" step="1" value="10"></label>
      </div>
      <label for="tr">Truck (tipper) load m³<input id="tr" type="number" step="0.5" value="10"></label>
      <p class="note">Swell: dug earth takes up more room in the truck than in the ground. Shrinkage: fill compacted in place takes less room than it did in the ground. So a pad at the average ground level does not balance, and a cut of 100 m³ fills more than 10 trucks of 10 m³.</p>
""",
right="""
      <div class="readout">
        <div><b>Cut (in ground)</b><span id="oC">–</span></div>
        <div><b>Fill (compacted)</b><span id="oF">–</span></div>
        <div><b>Balanced level</b><span id="oB">–</span></div>
        <div><b>Truckloads</b><span id="oT" class="hi">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Plan <span id="planLabel"></span></h2><svg id="plan" viewBox="0 0 420 380" role="img" aria-label="Plot plan with contours and cut and fill on the pad"></svg></div>
        <div class="view"><h2>Section A–A <span id="secLabel"></span></h2><svg id="sec" viewBox="0 0 420 380" role="img" aria-label="Section through the pad showing cut and fill"></svg></div>
      </div>
      <div class="data">
        <h2>Pad level options <span id="sum"></span></h2>
        <div class="tablewrap"><table><thead><tr><th>Pad level m</th><th>Cut m³</th><th>Fill m³</th><th>Off site (loose) m³</th><th>Truckloads</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
css="#bal{align-self:flex-start}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function site(){
  const W=num("W",2,500,15),D=num("D",2,500,25);
  const la=num("la",-500,9000,101.5),lb=num("lb",-500,9000,101.2),lc=num("lc",-500,9000,99.6),ld=num("ld",-500,9000,99.4);
  const pw=Math.min(W,num("pw",0.5,500,10)),pd=Math.min(D,num("pd",0.5,500,14));
  const px=Math.min(W-pw,num("px",0,500,2.5)),py=Math.min(D-pd,num("py",0,500,5.5));
  const sw=+$("soil").value/100,sh=num("sh",0,40,10)/100,tr=num("tr",1,40,10);
  const g=(x,y)=>{const u=x/W,v=y/D;return la*(1-u)*(1-v)+lb*u*(1-v)+lc*(1-u)*v+ld*u*v}; // y=0 rear, y=D front
  return {W,D,la,lb,lc,ld,pw,pd,px,py,sw,sh,tr,g,lo:Math.min(la,lb,lc,ld),hi:Math.max(la,lb,lc,ld)};
}
const N=80;
function vols(s,p){let c=0,f=0;const dA=(s.pw/N)*(s.pd/N);
  for(let i=0;i<N;i++)for(let j=0;j<N;j++){const d=s.g(s.px+(i+.5)*s.pw/N,s.py+(j+.5)*s.pd/N)-p;if(d>0)c+=d*dA;else f-=d*dA;}
  const surplus=c-f/(1-s.sh); // bank m³ left over (+) or short (-)
  const loose=surplus*(1+s.sw),loads=Math.ceil(Math.abs(loose)/s.tr-1e-9);
  return {c,f,surplus,loose,loads};}
function balanced(s){let a=s.lo-1,b=s.hi+1;for(let k=0;k<50;k++){const m=(a+b)/2,v=vols(s,m);if(v.c*(1-s.sh)>v.f)a=m;else b=m;}return (a+b)/2;}
$("bal").addEventListener("click",()=>{const s=site();$("pl").value=(Math.round(balanced(s)*20)/20).toFixed(2);render()});
function render(){
  const s=site(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),paper=css("--paper"),sheet=css("--sheet");
  const pl=$("pl");pl.min=(Math.floor((s.lo-1.5)*20)/20).toFixed(2);pl.max=(Math.ceil((s.hi+1.5)*20)/20).toFixed(2);
  const p=num("pl",s.lo-1.5,s.hi+1.5,(s.lo+s.hi)/2);$("plv").textContent=p.toFixed(2)+" m";
  const v=vols(s,p),pb=balanced(s);
  let avg=0;for(let i=0;i<N;i++)for(let j=0;j<N;j++)avg+=s.g(s.px+(i+.5)*s.pw/N,s.py+(j+.5)*s.pd/N);avg/=N*N;
  $("oC").textContent=fmt(v.c,1)+" m³";$("oF").textContent=fmt(v.f,1)+" m³";$("oB").textContent=pb.toFixed(2)+" m";
  $("oT").textContent=v.loads+(v.loose>0.05?" out":v.loose<-0.05?" in":"");
  // PLAN
  const sv=$("plan");sv.innerHTML="";const k=Math.min(330/s.W,320/s.D),ox=(420-s.W*k)/2,oy=20;const X=x=>ox+x*k,Y=y=>oy+y*k;
  el("rect",{x:X(0),y:Y(0),width:s.W*k,height:s.D*k,fill:paper,stroke:ink,"stroke-width":2},sv);
  // cut/fill cells on pad
  const M=24,dmax=Math.max(0.3,s.hi-s.lo);
  for(let i=0;i<M;i++)for(let j=0;j<M;j++){const x=s.px+(i+.5)*s.pw/M,y=s.py+(j+.5)*s.pd/M,d=s.g(x,y)-p;
    el("rect",{x:X(s.px+i*s.pw/M),y:Y(s.py+j*s.pd/M),width:s.pw*k/M+.3,height:s.pd*k/M+.3,fill:d>0?red:blue,"fill-opacity":Math.min(.75,.12+Math.abs(d)/dmax*.8)},sv);}
  el("rect",{x:X(s.px),y:Y(s.py),width:s.pw*k,height:s.pd*k,fill:"none",stroke:ink,"stroke-width":2},sv);
  // contours (marching squares on the bilinear surface)
  const rng=s.hi-s.lo,step=rng<=1.5?0.1:rng<=4?0.25:rng<=10?0.5:rng<=25?1:Math.pow(10,Math.ceil(Math.log10(rng/25)))*1;
  const G=40,lev=[];for(let z=Math.ceil(s.lo/step)*step;z<=s.hi+1e-9&&lev.length<60;z+=step)lev.push(+z.toFixed(3));
  const seg=(z,col,wd,dash)=>{let d="";for(let i=0;i<G;i++)for(let j=0;j<G;j++){const xs=[i,i+1,i+1,i].map(a=>a*s.W/G),ys=[j,j,j+1,j+1].map(b=>b*s.D/G);
      const vv=xs.map((x,q)=>s.g(x,ys[q])-z),pts=[];for(let q=0;q<4;q++){const a=vv[q],b=vv[(q+1)%4];if((a>0)!==(b>0)){const t=a/(a-b);pts.push([xs[q]+(xs[(q+1)%4]-xs[q])*t,ys[q]+(ys[(q+1)%4]-ys[q])*t]);}}
      if(pts.length>=2)d+=`M${X(pts[0][0]).toFixed(1)} ${Y(pts[0][1]).toFixed(1)}L${X(pts[1][0]).toFixed(1)} ${Y(pts[1][1]).toFixed(1)}`;}
    if(d)el("path",{d,stroke:col,"stroke-width":wd,fill:"none","stroke-dasharray":dash||"none"},sv);};
  lev.forEach((z,i)=>{seg(z,ink2,.8);});
  // labels along left edge
  lev.forEach(z=>{const v0=(z-s.la)/(s.lc-s.la);if(Number.isFinite(v0)&&v0>0.03&&v0<0.97)el("text",{x:X(0)-3,y:Y(v0*s.D)+3,"text-anchor":"end",fill:ink2,"font-size":9,"font-family":"IBM Plex Mono, monospace"},sv,z.toFixed(2))});
  seg(p,sun,2.2,"6 3");
  // section line
  const sx=s.px+s.pw/2;el("line",{x1:X(sx),y1:Y(0)-8,x2:X(sx),y2:Y(s.D)+8,stroke:ink,"stroke-width":1,"stroke-dasharray":"8 3 2 3"},sv);
  el("text",{x:X(sx)+4,y:Y(0)-8,fill:ink,"font-size":10,"font-family":"IBM Plex Mono, monospace"},sv,"A");el("text",{x:X(sx)+4,y:Y(s.D)+16,fill:ink,"font-size":10,"font-family":"IBM Plex Mono, monospace"},sv,"A");
  [[0,0,s.la],[s.W,0,s.lb],[0,s.D,s.lc],[s.W,s.D,s.ld]].forEach(([x,y,z])=>el("text",{x:X(x)+(x?-4:4),y:Y(y)+(y?-5:12),"text-anchor":x?"end":"start",fill:ink,"font-size":10,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},sv,z.toFixed(2)));
  el("text",{x:210,y:Y(s.D)+22,"text-anchor":"middle",fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},sv,"front · contours every "+step+" m · dashed = pad level");
  $("planLabel").textContent="red cut · blue fill";
  // SECTION along y through pad centre
  const qv=$("sec");qv.innerHTML="";const zs=[];for(let i=0;i<=60;i++)zs.push(s.g(sx,i*s.D/60));
  const zlo=Math.min(...zs,p)-0.6,zhi=Math.max(...zs,p)+0.6,hx=380/s.D,hz=Math.min(260/(zhi-zlo),hx*8),ve=hz/hx;
  const SX=y=>20+y*hx,SZ=z=>320-(z-zlo)*hz;
  let gd=`M${SX(0)} ${SZ(zs[0])}`;zs.forEach((z,i)=>gd+=` L${SX(i*s.D/60)} ${SZ(z)}`);
  el("path",{d:gd+` L${SX(s.D)} 340 L${SX(0)} 340 Z`,fill:rule,"fill-opacity":.5},qv);
  // cut and fill polygons between ground and pad
  const n2=60;for(let i=0;i<n2;i++){const y0=s.py+i*s.pd/n2,y1=s.py+(i+1)*s.pd/n2,g0=s.g(sx,y0),g1=s.g(sx,y1),m=(g0+g1)/2;
    el("path",{d:`M${SX(y0)} ${SZ(g0)} L${SX(y1)} ${SZ(g1)} L${SX(y1)} ${SZ(p)} L${SX(y0)} ${SZ(p)} Z`,fill:m>p?red:blue,"fill-opacity":.45,stroke:"none"},qv);}
  el("path",{d:gd,fill:"none",stroke:ink,"stroke-width":2},qv);
  el("line",{x1:SX(s.py),y1:SZ(p),x2:SX(s.py+s.pd),y2:SZ(p),stroke:sun,"stroke-width":3},qv);
  const gEnd=s.g(sx,s.py+s.pd),gSt=s.g(sx,s.py);el("text",{x:gEnd<p?SX(s.py+s.pd):SX(s.py),y:SZ(p)-8,"text-anchor":gEnd<p?"end":"start",fill:sun,"font-size":12,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},qv,"pad "+p.toFixed(2));
  el("text",{x:SX(0),y:SZ(zs[0])-8,fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},qv,"rear "+zs[0].toFixed(2));
  el("text",{x:SX(s.D),y:SZ(zs[60])-8,"text-anchor":"end",fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},qv,"front "+zs[60].toFixed(2));
  el("text",{x:210,y:364,"text-anchor":"middle",fill:ink,"font-size":12,"font-family":"IBM Plex Mono, monospace"},qv,"cut "+fmt(v.c,1)+" m³ · fill "+fmt(v.f,1)+" m³");
  $("secLabel").textContent=ve>1.05?"heights ×"+ve.toFixed(1):"to scale";
  // TABLE of options
  const tb=$("tbl");tb.innerHTML="";const opts=[];for(let d=-1;d<=1.001;d+=0.25)opts.push(+(pb+d).toFixed(2));
  const addRow=(z,cls,tag)=>{const w=vols(s,z),tr=document.createElement("tr");if(cls)tr.className=cls;
    tr.innerHTML=`<td>${z.toFixed(2)}${tag?" "+tag:""}</td><td>${fmt(w.c,1)}</td><td>${fmt(w.f,1)}</td><td>${w.loose>=0?"+":"−"}${fmt(Math.abs(w.loose),1)}</td><td>${w.loads} ${w.loose>0.05?"out":w.loose<-0.05?"in":""}</td>`;tb.appendChild(tr)};
  opts.forEach((z,i)=>addRow(z,"",i===4?"(balanced)":""));addRow(p,"now","(yours)");
  const naive=Math.ceil(Math.max(0,v.c-v.f)/s.tr-1e-9);
  $("sum").textContent=`average ground ${avg.toFixed(2)} m · without swell you'd count ${naive} loads`;
}
""")
