APP = dict(
slug="cladding-panels", title="Cladding Panel Layout", h1="Cladding Panel Layout",
sub="Enter the facade, the largest panel you want, the joint and the folded return. Get equal panel sizes, the panel count, how many fit on one stock sheet and the sheets to order, with the elevation and the sheet cutting plan drawn.",
meta=[("Sheet","T-48"),("Method","Equal modules + nesting"),("Units","m, mm"),("By","@smart_tools_every_week")],
source="Columns = ⌈(facade width + joint) ÷ (max panel width + joint)⌉, panel width = (facade width − joints) ÷ columns; rows the same way. Flat blank = panel + 2 × return (the fold for a cassette panel). Blanks per sheet = the better of the two orientations in a straight grid cut. Sheets = panels ÷ blanks per sheet, rounded up. All first principles; stock sheet size, return and joint are editable, so check them with your panel supplier.",
inputs="""
      <div class="row">
        <label for="fw">Facade width m<input id="fw" type="number" step="0.5" value="9"></label>
        <label for="fh">Facade height m<input id="fh" type="number" step="0.5" value="6"></label>
      </div>
      <div class="row">
        <label for="pw">Max panel width mm<input id="pw" type="number" step="50" value="1150"></label>
        <label for="ph">Max panel height mm<input id="ph" type="number" step="50" value="1200"></label>
      </div>
      <div class="row">
        <label for="j">Joint mm<input id="j" type="number" step="1" value="10"></label>
        <label for="r">Return per edge mm<input id="r" type="number" step="5" value="40"></label>
      </div>
      <div class="row">
        <label for="sw">Sheet width mm<input id="sw" type="number" step="10" value="1220"></label>
        <label for="sl">Sheet length mm<input id="sl" type="number" step="10" value="2440"></label>
      </div>
      <p class="note">1220 × 2440 mm is a common ACP / board size; set the return to 0 for flat sheets fixed with rivets. The facade size is the clad area edge to edge, with joints only between panels.</p>
""",
right="""
      <div class="readout">
        <div><b>Sheets to order</b><span id="oS" class="hi">–</span></div>
        <div><b>Panel size</b><span id="oP">–</span></div>
        <div><b>Panels</b><span id="oN">–</span></div>
        <div><b>Sheet yield</b><span id="oY">–</span></div>
      </div>
      <div class="views">
        <div class="view full"><h2>Elevation <span id="eLabel"></span></h2><svg id="elev" viewBox="0 0 580 340" role="img" aria-label="Facade elevation divided into equal panels"></svg></div>
      </div>
      <div class="views">
        <div class="view"><h2>One sheet <span id="nLabel"></span></h2><svg id="nest" viewBox="0 0 300 240" role="img" aria-label="Panel blanks nested on one stock sheet"></svg></div>
        <div class="view"><h2>Panel blank <span>with returns</span></h2><svg id="blank" viewBox="0 0 300 240" role="img" aria-label="Flat blank of one panel with folded returns"></svg></div>
      </div>
      <div class="data"><h2>Row options <span id="dLabel"></span></h2><div class="tablewrap"><table><thead><tr><th>Rows</th><th>Panel</th><th>Blank</th><th>Per sheet</th><th>Panels</th><th>Sheets</th><th>Yield</th></tr></thead><tbody id="tb"></tbody></table></div>
      <p class="note" id="vNote" style="margin-top:8px"></p></div>
""",
css="",
js=r"""
const num=(id,min,max,def)=>{const v=parseFloat($(id).value);return Number.isFinite(v)?Math.min(max,Math.max(min,v)):def};
function lay(FW,FH,cols,rows,j,r,sw,sl){
  const pw=(FW-(cols-1)*j)/cols,ph=(FH-(rows-1)*j)/rows,bw=pw+2*r,bh=ph+2*r;
  const a=Math.floor(sw/bw)*Math.floor(sl/bh),b=Math.floor(sw/bh)*Math.floor(sl/bw),per=Math.max(a,b),rot=b>a;
  const n=cols*rows,sheets=per>0?Math.ceil(n/per):NaN,yld=per>0?n*pw*ph/(sheets*sw*sl)*100:NaN;
  return {cols,rows,pw,ph,bw,bh,per,rot,n,sheets,yld}}
function calc(){
  const FW=num("fw",0.3,300,9)*1000,FH=num("fh",0.3,300,6)*1000,pmw=num("pw",100,6000,1150),pmh=num("ph",100,6000,1200),j=num("j",0,100,10),r=num("r",0,150,40),sw=num("sw",200,4000,1220),sl=num("sl",200,8000,2440);
  const cols=Math.min(300,Math.max(1,Math.ceil((FW+j)/(pmw+j)))),rows=Math.min(300,Math.max(1,Math.ceil((FH+j)/(pmh+j))));
  const m=lay(FW,FH,cols,rows,j,r,sw,sl),guess=Math.ceil(FW*FH/(sw*sl));
  const opts=[];for(let k=rows;k<=Math.min(300,rows+5);k++)opts.push({...lay(FW,FH,cols,k,j,r,sw,sl),now:k===rows});
  const fit=opts.filter(o=>o.per>0),best=fit.length?fit.reduce((p,q)=>q.sheets<p.sheets?q:p):null;
  return {FW,FH,j,r,sw,sl,...m,guess,opts,best};
}
function render(){
  const c=calc(),ink=css("--ink"),ink2=css("--ink-2"),rule=css("--rule"),red=css("--red"),blue=css("--blue"),F="IBM Plex Mono, monospace",ok=Number.isFinite(c.sheets);
  $("oS").textContent=ok?c.sheets:"won't fit";$("oS").className=ok?"hi":"bad";
  $("oP").textContent=fmt(c.pw,0)+"×"+fmt(c.ph,0);$("oN").textContent=c.n;$("oY").textContent=ok?fmt(c.yld,0)+"%":"–";
  // elevation
  const ev=$("elev");ev.innerHTML="";const k=Math.min(550/c.FW,300/c.FH),ox=(580-c.FW*k)/2,oy=14,X=x=>ox+x*k,Y=y=>oy+(c.FH-y)*k;
  el("rect",{x:fmt(X(0),1),y:fmt(Y(c.FH),1),width:fmt(c.FW*k,1),height:fmt(c.FH*k,1),fill:blue,opacity:.35},ev);
  const jw=Math.max(1,c.j*k);
  for(let i=1;i<c.cols;i++){const x=X(i*(c.pw+c.j)-c.j/2);el("line",{x1:fmt(x,1),y1:fmt(Y(c.FH),1),x2:fmt(x,1),y2:fmt(Y(0),1),stroke:ink,"stroke-width":fmt(Math.min(jw,3),2)},ev)}
  for(let i=1;i<c.rows;i++){const y=Y(i*(c.ph+c.j)-c.j/2);el("line",{x1:fmt(X(0),1),y1:fmt(y,1),x2:fmt(X(c.FW),1),y2:fmt(y,1),stroke:ink,"stroke-width":fmt(Math.min(jw,3),2)},ev)}
  el("rect",{x:fmt(X(0),1),y:fmt(Y(c.FH),1),width:fmt(c.FW*k,1),height:fmt(c.FH*k,1),fill:"none",stroke:ink,"stroke-width":2},ev);
  const ph=1750*k,px=X(0)+Math.min(30,c.FW*k*0.1)+ph*0.15;
  if(ph>6){el("circle",{cx:fmt(px,1),cy:fmt(Y(0)-ph*0.92,1),r:fmt(ph*0.07,1),fill:"none",stroke:red,"stroke-width":1.5},ev);
    el("line",{x1:fmt(px,1),y1:fmt(Y(0)-ph*0.85,1),x2:fmt(px,1),y2:fmt(Y(0)-ph*0.45,1),stroke:red,"stroke-width":1.5},ev);
    el("line",{x1:fmt(px-ph*0.1,1),y1:fmt(Y(0),1),x2:fmt(px,1),y2:fmt(Y(0)-ph*0.45,1),stroke:red,"stroke-width":1.5},ev);
    el("line",{x1:fmt(px+ph*0.1,1),y1:fmt(Y(0),1),x2:fmt(px,1),y2:fmt(Y(0)-ph*0.45,1),stroke:red,"stroke-width":1.5},ev)}
  ev.setAttribute("viewBox","0 0 580 "+fmt(Y(0)+50,0));el("text",{x:290,y:fmt(Y(0)+22,1),"text-anchor":"middle",fill:ink,"font-size":16,"font-family":F},ev,fmt(c.FW/1000,2)+" m · "+c.cols+" columns of "+fmt(c.pw,0)+" mm");
  el("text",{x:290,y:fmt(Y(0)+42,1),"text-anchor":"middle",fill:ink2,"font-size":15,"font-family":F},ev,fmt(c.FH/1000,2)+" m high · "+c.rows+" rows of "+fmt(c.ph,0)+" mm · "+fmt(c.j,0)+" mm joints");
  $("eLabel").textContent=c.n+" equal panels";
  // nesting
  const nv=$("nest");nv.innerHTML="";const W=c.rot?c.sl:c.sl,H=c.sw,nk=Math.min(270/c.sl,180/c.sw),nx=(300-c.sl*nk)/2,ny=24;
  el("rect",{x:fmt(nx,1),y:ny,width:fmt(c.sl*nk,1),height:fmt(c.sw*nk,1),fill:red,opacity:.22,stroke:ink,"stroke-width":1.5},nv);
  if(ok){const bl=c.rot?c.bw:c.bh,bs=c.rot?c.bh:c.bw,na=Math.floor(c.sl/bl),nb=Math.floor(c.sw/bs);
    for(let i=0;i<Math.min(na,40);i++)for(let q=0;q<Math.min(nb,40);q++)el("rect",{x:fmt(nx+i*bl*nk,1),y:fmt(ny+q*bs*nk,1),width:fmt(bl*nk,1),height:fmt(bs*nk,1),fill:blue,opacity:.6,stroke:ink,"stroke-width":1},nv)}
  el("text",{x:150,y:fmt(ny+c.sw*nk+20,1),"text-anchor":"middle",fill:ink,"font-size":12,"font-family":F},nv,fmt(c.sw,0)+" × "+fmt(c.sl,0)+" sheet · red = offcut");
  $("nLabel").textContent=ok?c.per+" blank"+(c.per>1?"s":"")+" per sheet":"blank bigger than sheet";
  // blank
  const bv=$("blank");bv.innerHTML="";const bk=Math.min(220/c.bw,170/c.bh),bx=(300-c.bw*bk)/2,by=20,R=c.r*bk;
  el("rect",{x:fmt(bx,1),y:by,width:fmt(c.bw*bk,1),height:fmt(c.bh*bk,1),fill:blue,opacity:.25,stroke:ink,"stroke-width":1.5},bv);
  if(R>0.5){el("rect",{x:fmt(bx+R,1),y:fmt(by+R,1),width:fmt(c.pw*bk,1),height:fmt(c.ph*bk,1),fill:blue,opacity:.45,stroke:ink,"stroke-dasharray":"4 3"},bv);
    [[bx,by],[bx+c.bw*bk-R,by],[bx,by+c.bh*bk-R],[bx+c.bw*bk-R,by+c.bh*bk-R]].forEach(p=>el("rect",{x:fmt(p[0],1),y:fmt(p[1],1),width:fmt(R,1),height:fmt(R,1),fill:css("--sheet")},bv))}
  el("text",{x:150,y:fmt(by+c.bh*bk+20,1),"text-anchor":"middle",fill:ink,"font-size":12,"font-family":F},bv,"blank "+fmt(c.bw,0)+" × "+fmt(c.bh,0)+" mm");
  el("text",{x:150,y:fmt(by+c.bh*bk+36,1),"text-anchor":"middle",fill:ink2,"font-size":11,"font-family":F},bv,"face "+fmt(c.pw,0)+" × "+fmt(c.ph,0)+" · returns "+fmt(c.r,0)+" mm");
  // table
  $("tb").innerHTML=c.opts.map(o=>`<tr${o.now?' class="now"':""}><td>${o.rows}</td><td>${fmt(o.pw,0)} × ${fmt(o.ph,0)}</td><td>${fmt(o.bw,0)} × ${fmt(o.bh,0)}</td><td>${o.per}</td><td>${o.n}</td><td class="${o===c.best?"ok":""}">${Number.isFinite(o.sheets)?o.sheets:"–"}</td><td>${Number.isFinite(o.yld)?fmt(o.yld,0)+"%":"–"}</td></tr>`).join("");
  $("dLabel").textContent=c.cols+" columns";
  $("vNote").textContent="Facade area ÷ sheet area says "+c.guess+" sheets. "+(c.best?"Fewest sheets in these options: "+c.best.sheets+" with "+c.best.rows+" rows.":"No row count here fits the sheet: make the panel or the return smaller.");
}
""")
