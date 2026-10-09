APP = dict(
slug="carpet-area", title="Carpet Area Statement (RERA)", h1="Carpet Area",
sub="RERA carpet, built-up and super built-up area of a flat from its room sizes, with the loading and the real price per carpet sq ft. Ready for your area statement.",
meta=[("Sheet","T-17"),("Definition","RERA Act 2016 §2(k)"),("Units","m² / sq ft"),("By","@smart_tools_every_week")],
source="Carpet area per Real Estate (Regulation and Development) Act 2016, Section 2(k): net usable floor area, excluding external walls, service shafts, exclusive balcony/verandah and exclusive open terrace, including internal partition walls. Built-up and super built-up are trade terms, not defined in the Act; the method here is common practice. 1 m² = 10.7639 sq ft.",
inputs="""
      <label for="rooms">Rooms · name, length × width (m)
        <textarea id="rooms" rows="9" spellcheck="false">Living, 4.8 x 3.6
Dining, 3.0 x 3.0
Kitchen, 3.0 x 2.4
Bedroom 1, 3.6 x 3.3
Bedroom 2, 3.3 x 3.0
Toilet 1, 2.4 x 1.5
Toilet 2, 2.1 x 1.5
Passage, 3.0 x 1.0</textarea>
      </label>
      <div class="row">
        <label for="iwl">Internal walls, length m<input id="iwl" type="number" step="0.5" value="22"></label>
        <label for="iwt">Thickness mm<input id="iwt" type="number" step="5" value="115"></label>
      </div>
      <div class="row">
        <label for="ewl">External walls, outer perimeter m<input id="ewl" type="number" step="0.5" value="36"></label>
        <label for="ewt">Thickness mm<input id="ewt" type="number" step="5" value="230"></label>
      </div>
      <div class="row">
        <label for="bal">Exclusive balcony m²<input id="bal" type="number" step="0.1" value="4.5"></label>
        <label for="sh">Service shafts m²<input id="sh" type="number" step="0.1" value="0.6"></label>
      </div>
      <label for="ld">Loading (common areas) % <span id="ldv" class="time" style="font-size:18px"></span><input id="ld" type="range" min="0" max="60" step="1" value="30"></label>
      <label for="rate">Quoted rate ₹ / sq ft super built-up<input id="rate" type="number" step="100" value="8000"></label>
      <p class="note">One room per line, e.g. "Bedroom 1, 3.6 x 3.3". Loading is the flat's share of lobbies, stairs, lifts, clubhouse and other common areas, added on top of built-up. Built-up here = carpet + external walls + shafts + balcony.</p>
""",
right="""
      <div class="readout">
        <div><b>RERA carpet</b><span id="oC" class="hi">–</span></div>
        <div><b>Built-up</b><span id="oB">–</span></div>
        <div><b>Super built-up</b><span id="oS">–</span></div>
        <div><b>Carpet ÷ super</b><span id="oR">–</span></div>
      </div>
      <div class="views">
        <div class="view"><h2>Area diagram <span>to area, not to plan</span></h2><svg id="diag" viewBox="0 0 420 360" role="img" aria-label="Nested area diagram of rooms, walls, balcony and common areas"></svg></div>
        <div class="view"><h2>Where the sq ft go <span id="pxLabel"></span></h2><svg id="bars" viewBox="0 0 420 360" role="img" aria-label="Stacked bar of area components and price per sq ft"></svg></div>
      </div>
      <div class="data">
        <h2>Area statement <span id="sum"></span></h2>
        <div class="tablewrap"><table><thead><tr><th>Item</th><th>m²</th><th>sq ft</th><th>% of super</th></tr></thead><tbody id="tbl"></tbody></table></div>
      </div>
""",
css="textarea{font:500 14px/1.45 var(--mono);color:var(--ink);background:var(--paper);border:1px solid var(--rule);padding:9px 10px;border-radius:0;width:100%;resize:vertical;text-transform:none;letter-spacing:0}",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
const SQ=10.7639,inr=v=>"₹"+Math.round(v).toLocaleString("en-IN");
function parseRooms(){
  const out=[];($("rooms").value||"").split(/\n/).slice(0,60).forEach((ln,i)=>{
    const nums=(ln.match(/\d+(?:\.\d+)?/g)||[]).map(Number);
    const name=(ln.split(",")[0]||"").replace(/[\d.]+\s*[x×*]\s*[\d.]+/,"").trim()||("Room "+(i+1));
    if(nums.length>=2){const a=Math.min(100,nums[nums.length-2]),b=Math.min(100,nums[nums.length-1]);if(a>0&&b>0)out.push({name:name.slice(0,24),a:a*b,l:a,w:b});}
  });return out;
}
function calc(){
  const rooms=parseRooms(),R=rooms.reduce((s,r)=>s+r.a,0);
  const iw=num("iwl",0,1000,22)*num("iwt",0,600,115)/1000;
  const et=num("ewt",0,600,230)/1000,ep=num("ewl",0,2000,36),ew=Math.max(0,ep*et-4*et*et);
  const bal=num("bal",0,500,4.5),sh=num("sh",0,200,0.6),ld=num("ld",0,200,30),rate=num("rate",0,1e6,8000);
  const C=R+iw,B=C+ew+sh+bal,L=B*ld/100,S=B+L,price=S*SQ*rate;
  return {rooms,R,iw,ew,bal,sh,ld,rate,C,B,L,S,price,perC:C>0?price/(C*SQ):0};
}
// squarified treemap
function squarify(items,x,y,w,h){const out=[];let rest=items.slice().sort((a,b)=>b.v-a.v);
  while(rest.length){const short=Math.min(w,h),tot=rest.reduce((s,i)=>s+i.v,0);if(tot<=0||w<=0||h<=0)break;const k=w*h/tot;
    let row=[],best=Infinity;for(const it of rest){const r=row.concat([it]),s=r.reduce((a,b)=>a+b.v*k,0),mx=Math.max(...r.map(z=>z.v*k)),mn=Math.min(...r.map(z=>z.v*k));
      const worst=Math.max(short*short*mx/(s*s),(s*s)/(short*short*mn));if(worst<=best){best=worst;row=r}else break;}
    const s=row.reduce((a,b)=>a+b.v*k,0),t=s/short;let o=0;
    row.forEach(it=>{const l=it.v*k/t;if(w>=h)out.push({it,x:x,y:y+o,w:t,h:l});else out.push({it,x:x+o,y:y,w:l,h:t});o+=l;});
    if(w>=h){x+=t;w-=t}else{y+=t;h-=t}rest=rest.slice(row.length);}
  return out;}
function render(){
  const e=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),sun=css("--sun"),ok=css("--ok"),paper=css("--paper"),sheet=css("--sheet");
  $("ldv").textContent=e.ld+"%";
  const f=(m)=>fmt(m,1)+" m² · "+Math.round(m*SQ).toLocaleString("en-IN")+" sq ft";
  $("oC").textContent=Math.round(e.C*SQ).toLocaleString("en-IN")+" sq ft";$("oB").textContent=Math.round(e.B*SQ).toLocaleString("en-IN")+" sq ft";
  $("oS").textContent=Math.round(e.S*SQ).toLocaleString("en-IN")+" sq ft";$("oR").textContent=e.S>0?fmt(100*e.C/e.S,0)+"%":"–";
  // DIAGRAM: nested squares, area-true
  const dv=$("diag");dv.innerHTML="";const side=320,sc=e.S>0?side/Math.sqrt(e.S):0,cx=210,cy=178;
  const sq=(A,fill,st,dash,op)=>{const s=Math.sqrt(Math.max(0,A))*sc;el("rect",{x:cx-s/2,y:cy-s/2,width:s,height:s,fill,"fill-opacity":op==null?1:op,stroke:st,"stroke-dasharray":dash||"none","stroke-width":1.5},dv);return s};
  const sS=sq(e.S,sun,sun,"5 4",.18),sB=sq(e.B,paper,ink),sCb=Math.sqrt(Math.max(0,e.C+e.bal))*sc,sC=Math.sqrt(Math.max(0,e.C))*sc;
  // balcony strip along bottom of the built-up square, walls+shafts as the ring
  const bx=cx-sB/2,by=cy-sB/2,inner=sB-(sB-sCb);
  const ringW=(sB-sCb)/2,cw=sCb,ch=e.C+e.bal>0?sCb*e.C/(e.C+e.bal):0;
  el("rect",{x:bx+ringW,y:by+ringW,width:cw,height:sCb,fill:ink2,"fill-opacity":.15},dv);
  el("rect",{x:bx+ringW,y:by+ringW+ch,width:cw,height:Math.max(0,sCb-ch),fill:blue,"fill-opacity":.35,stroke:blue},dv);
  if(sCb-ch>12)el("text",{x:cx,y:by+ringW+ch+(sCb-ch)/2+4,"text-anchor":"middle",fill:blue,"font-size":10,"font-family":"IBM Plex Mono, monospace"},dv,"balcony");
  const rects=squarify(e.rooms.map(r=>({v:r.a,name:r.name})).concat(e.iw>0?[{v:e.iw,name:"int. walls",wall:1}]:[]),bx+ringW,by+ringW,cw,ch);
  rects.forEach(r=>{el("rect",{x:r.x,y:r.y,width:Math.max(0,r.w),height:Math.max(0,r.h),fill:r.it.wall?ink2:sheet,"fill-opacity":r.it.wall?.45:1,stroke:ink,"stroke-width":.8},dv);
    if(r.w>44&&r.h>22){el("text",{x:r.x+r.w/2,y:r.y+r.h/2,"text-anchor":"middle",fill:ink,"font-size":Math.min(11,r.w/7),"font-family":"IBM Plex Sans, sans-serif"},dv,r.it.name);
      el("text",{x:r.x+r.w/2,y:r.y+r.h/2+12,"text-anchor":"middle",fill:ink2,"font-size":9,"font-family":"IBM Plex Mono, monospace"},dv,fmt(r.it.v,1)+" m²");}});
  el("rect",{x:bx+ringW,y:by+ringW,width:cw,height:ch,fill:"none",stroke:red,"stroke-width":2.5},dv);
  el("text",{x:cx,y:cy-sS/2-6,"text-anchor":"middle",fill:sun,"font-size":11,"font-family":"IBM Plex Mono, monospace"},dv,"super built-up · loading "+e.ld+"%");
  el("text",{x:cx,y:by-4,"text-anchor":"middle",fill:ink2,"font-size":10,"font-family":"IBM Plex Mono, monospace"},dv,"built-up (walls + shafts ring)");
  el("text",{x:cx,y:Math.min(356,cy+sS/2+14),"text-anchor":"middle",fill:red,"font-size":11,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},dv,"red line = RERA carpet "+fmt(e.C,1)+" m²");
  // BARS
  const bv=$("bars");bv.innerHTML="";const parts=[["Rooms",e.R,css("--ink")],["Internal walls",e.iw,ink2],["External walls",e.ew,rule],["Shafts",e.sh,rule],["Balcony",e.bal,blue],["Common (loading)",e.L,sun]];
  const W0=380,x0=20,s2=e.S>0?W0/e.S:0;let x=x0;
  el("text",{x:x0,y:22,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},bv,"SUPER BUILT-UP "+Math.round(e.S*SQ).toLocaleString("en-IN")+" sq ft");
  parts.forEach(([n,a,c])=>{const w=a*s2;el("rect",{x,y:30,width:Math.max(0,w),height:40,fill:c,"fill-opacity":n==="Rooms"?.75:.8,stroke:sheet},bv);x+=w;});
  el("line",{x1:x0+e.C*s2,y1:24,x2:x0+e.C*s2,y2:80,stroke:red,"stroke-width":2.5},bv);
  el("text",{x:x0+e.C*s2,y:94,"text-anchor":"middle",fill:red,"font-size":12,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},bv,"carpet "+(e.S>0?fmt(100*e.C/e.S,0):"–")+"%");
  parts.forEach(([n,a,c],i)=>{const y=118+i*20;el("rect",{x:x0,y:y-10,width:12,height:12,fill:c,"fill-opacity":.8},bv);
    el("text",{x:x0+20,y,fill:ink,"font-size":11,"font-family":"IBM Plex Sans, sans-serif"},bv,n);
    el("text",{x:x0+W0,y,"text-anchor":"end",fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},bv,Math.round(a*SQ).toLocaleString("en-IN")+" sq ft");});
  // price per sq ft
  const pr=[["Quoted / sq ft super",e.rate,ink2],["Real / sq ft carpet",e.perC,red]],mx=Math.max(1,e.rate,e.perC);
  el("text",{x:x0,y:258,fill:ink2,"font-size":11,"font-family":"IBM Plex Mono, monospace"},bv,"PRICE "+inr(e.price));
  pr.forEach(([n,v,c],i)=>{const y=268+i*44;el("rect",{x:x0,y,width:Math.max(0,W0*0.62*v/mx),height:22,fill:c,"fill-opacity":.7},bv);
    el("text",{x:x0+W0*0.62*v/mx+8,y:y+16,fill:c,"font-size":13,"font-weight":600,"font-family":"IBM Plex Mono, monospace"},bv,inr(v));
    el("text",{x:x0,y:y+36,fill:ink2,"font-size":10,"font-family":"IBM Plex Sans, sans-serif"},bv,n);});
  $("pxLabel").textContent="you pay "+inr(e.perC)+" per carpet sq ft";
  // TABLE
  const tb=$("tbl");tb.innerHTML="";const pc=a=>e.S>0?fmt(100*a/e.S,1)+"%":"–";
  const add=(n,a,cls)=>{const tr=document.createElement("tr");if(cls)tr.className=cls;tr.innerHTML=`<td>${n}</td><td>${fmt(a,2)}</td><td>${Math.round(a*SQ).toLocaleString("en-IN")}</td><td>${pc(a)}</td>`;tb.appendChild(tr)};
  e.rooms.forEach(r=>add(r.name+" ("+fmt(r.l,2)+" × "+fmt(r.w,2)+")",r.a));
  add("Internal partition walls",e.iw);add("RERA carpet area",e.C,"now");
  add("External walls",e.ew);add("Service shafts",e.sh);add("Exclusive balcony",e.bal);add("Built-up area",e.B,"now");
  add("Common areas (loading "+e.ld+"%)",e.L);add("Super built-up area",e.S,"now");
  $("sum").textContent="loading factor "+(e.C>0?fmt(e.S/e.C,2):"–")+" × carpet";
}
$("rooms").addEventListener("input",render);
""")
