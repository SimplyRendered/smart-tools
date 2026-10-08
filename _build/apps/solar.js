const CITIES=[["New Delhi",28.61,77.21,5.5],["Mumbai",19.08,72.88,5.5],["Bengaluru",12.97,77.59,5.5],["Chennai",13.08,80.27,5.5],["Kolkata",22.57,88.36,5.5],["Hyderabad",17.39,78.49,5.5],["Pune",18.52,73.86,5.5],["Ahmedabad",23.02,72.57,5.5],["Jaipur",26.91,75.79,5.5],["Lucknow",26.85,80.95,5.5],["Chandigarh",30.73,76.78,5.5],["Raipur / Durg",21.19,81.28,5.5],["Panaji, Goa",15.49,73.83,5.5],["Kochi",9.93,76.27,5.5],["Guwahati",26.14,91.74,5.5],["Dubai",25.20,55.27,4],["Singapore",1.35,103.82,8],["London",51.51,-0.13,0],["New York",40.71,-74.01,-5],["Sydney",-33.87,151.21,10],["Custom",null,null,null]];
const rad=d=>d*Math.PI/180, deg=r=>r*180/Math.PI;
const DIRS=["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"];
const dirName=a=>DIRS[Math.round(((a%360)+360)%360/22.5)%16];

function solar(dateStr,minutes,lat,lon,tz){
  const [y,m,d]=dateStr.split("-").map(Number);
  const jd=Date.UTC(y,m-1,d)/86400000+2440587.5+(minutes-tz*60)/1440;
  const jc=(jd-2451545)/36525;
  const L0=(280.46646+jc*(36000.76983+jc*0.0003032))%360;
  const M=357.52911+jc*(35999.05029-0.0001537*jc);
  const e=0.016708634-jc*(0.000042037+0.0000001267*jc);
  const C=Math.sin(rad(M))*(1.914602-jc*(0.004817+0.000014*jc))+Math.sin(rad(2*M))*(0.019993-0.000101*jc)+Math.sin(rad(3*M))*0.000289;
  const app=L0+C-0.00569-0.00478*Math.sin(rad(125.04-1934.136*jc));
  const eps0=23+(26+(21.448-jc*(46.815+jc*(0.00059-jc*0.001813)))/60)/60;
  const eps=eps0+0.00256*Math.cos(rad(125.04-1934.136*jc));
  const decl=deg(Math.asin(Math.sin(rad(eps))*Math.sin(rad(app))));
  const yy=Math.tan(rad(eps/2))**2;
  const eot=4*deg(yy*Math.sin(2*rad(L0))-2*e*Math.sin(rad(M))+4*e*yy*Math.sin(rad(M))*Math.cos(2*rad(L0))-0.5*yy*yy*Math.sin(4*rad(L0))-1.25*e*e*Math.sin(2*rad(M)));
  let tst=(minutes+eot+4*lon-60*tz)%1440; if(tst<0)tst+=1440;
  const ha=tst/4<0?tst/4+180:tst/4-180;
  const cz=Math.sin(rad(lat))*Math.sin(rad(decl))+Math.cos(rad(lat))*Math.cos(rad(decl))*Math.cos(rad(ha));
  const zen=deg(Math.acos(Math.min(1,Math.max(-1,cz))));
  let alt=90-zen;
  // atmospheric refraction (NOAA)
  let refr=0; if(alt>85)refr=0; else if(alt>5)refr=(58.1/Math.tan(rad(alt))-0.07/Math.tan(rad(alt))**3+0.000086/Math.tan(rad(alt))**5)/3600; else if(alt>-0.575)refr=(1735+alt*(-518.2+alt*(103.4+alt*(-12.79+alt*0.711))))/3600; else refr=(-20.772/Math.tan(rad(alt)))/3600;
  alt+=refr;
  const den=Math.cos(rad(lat))*Math.sin(rad(zen));
  let az;
  if(Math.abs(den)<1e-9) az=lat>decl?180:0;
  else{const a=deg(Math.acos(Math.min(1,Math.max(-1,(Math.sin(rad(lat))*Math.cos(rad(zen))-Math.sin(rad(decl)))/den))));
    az=ha>0?(a+180)%360:(540-a)%360;}
  const haR=deg(Math.acos(Math.min(1,Math.max(-1,Math.cos(rad(90.833))/(Math.cos(rad(lat))*Math.cos(rad(decl)))-Math.tan(rad(lat))*Math.tan(rad(decl))))));
  const noon=720-4*lon-eot+tz*60;
  return {alt,az,decl,noon,rise:noon-haR*4,set:noon+haR*4,dayLen:8*haR};
}
