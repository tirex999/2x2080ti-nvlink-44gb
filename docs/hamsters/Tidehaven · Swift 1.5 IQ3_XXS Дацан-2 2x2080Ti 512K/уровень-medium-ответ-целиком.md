# Tidehaven 🏝️

Below is the complete, self-contained `index.html`. Save it and open in any modern browser — everything (geometry, shaders, audio) is procedural.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Tidehaven — a tiny coastal world</title>
<style>
  :root{
    --ink:#eaf6f4; --panel:rgba(16,30,36,.62); --edge:rgba(255,255,255,.14);
    --accent:#7fd8c4; --accent2:#ffc98a;
  }
  *{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
  html,body{margin:0;height:100%;overflow:hidden;background:#0a1626;
    font-family:"Avenir Next","Segoe UI",system-ui,sans-serif;color:var(--ink)}
  canvas{display:block}
  #ui{position:fixed;left:14px;top:14px;display:flex;flex-direction:column;gap:10px;
      max-height:calc(100vh - 28px);overflow-y:auto;pointer-events:none;z-index:10;scrollbar-width:none}
  #ui::-webkit-scrollbar{display:none}
  .panel{pointer-events:auto;background:var(--panel);border:1px solid var(--edge);
      border-radius:14px;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
      box-shadow:0 8px 24px rgba(0,0,0,.28);max-width:300px;overflow:hidden}
  .phead{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;
      cursor:pointer;user-select:none;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
  .phead .chev{transition:transform .25s;font-size:10px}
  .panel.closed .chev{transform:rotate(-90deg)}
  .pbody{padding:4px 14px 14px;display:flex;flex-direction:column;gap:9px;
      transition:opacity .25s;overflow:hidden}
  .panel.closed .pbody{display:none}
  #title h1{font-family:Georgia,"Times New Roman",serif;font-size:26px;margin:2px 0 0;letter-spacing:.02em}
  #title p{margin:2px 0 0;font-size:12px;opacity:.75;line-height:1.45}
  .row{display:flex;gap:6px;flex-wrap:wrap}
  .btn{background:rgba(255,255,255,.08);border:1px solid var(--edge);color:var(--ink);
      border-radius:9px;padding:7px 11px;font-size:12px;cursor:pointer;transition:.18s;flex:1;white-space:nowrap}
  .btn:hover{background:rgba(255,255,255,.16)}
  .btn.active{background:var(--accent);color:#083028;border-color:var(--accent);font-weight:600}
  label.sl{font-size:11px;letter-spacing:.06em;opacity:.85;display:flex;flex-direction:column;gap:4px}
  input[type=range]{width:100%;accent-color:var(--accent);height:18px}
  select{background:rgba(255,255,255,.08);color:var(--ink);border:1px solid var(--edge);
      border-radius:8px;padding:5px 8px;font-size:12px}
  .cap{font-size:10px;opacity:.55;letter-spacing:.08em;text-transform:uppercase;margin-top:2px}
  @media (max-width:720px){
    #ui{left:8px;top:8px;gap:7px}
    .panel{max-width:min(72vw,250px)}
    #title h1{font-size:20px}
  }
</style>
</head>
<body>
<div id="ui">
  <div class="panel" id="title"><div class="pbody" style="padding:12px 16px">
    <h1>Tidehaven</h1><p>A tiny coastal world — cozy above, alive below.<br>Drag to orbit · scroll to zoom.</p>
  </div></div>

  <div class="panel" data-p="cam"><div class="phead">Camera <span class="chev">▼</span></div>
    <div class="pbody">
      <div class="row"><button class="btn" data-cam="iso">Isometric</button><button class="btn" data-cam="cabin">Cabin</button></div>
      <div class="row"><button class="btn" data-cam="under">Underwater</button><button class="btn" data-cam="free">Free Orbit</button></div>
    </div></div>

  <div class="panel" data-p="world"><div class="phead">World <span class="chev">▼</span></div>
    <div class="pbody">
      <div class="row"><button class="btn" id="bKayak">Launch Kayak</button><button class="btn" id="bRay">Ray Leap</button></div>
      <div class="row"><button class="btn" id="bPause">Pause</button><button class="btn" id="bReset">Reset</button></div>
      <label class="sl">Tide <input type="range" id="sTide" min="-2" max="2" step="0.01" value="0"></label>
      <label class="sl">Wind <input type="range" id="sWind" min="0" max="1" step="0.01" value="0.5"></label>
      <div class="row"><button class="btn" data-time="day">Day</button><button class="btn" data-time="sunset">Sunset</button><button class="btn" data-time="night">Night</button></div>
    </div></div>

  <div class="panel" data-p="audio"><div class="phead">Audio & Quality <span class="chev">▼</span></div>
    <div class="pbody">
      <div class="row"><button class="btn" id="bMusic">Music: Off</button></div>
      <label class="sl">Volume <input type="range" id="sVol" min="0" max="1" step="0.01" value="0.7"></label>
      <label class="sl">Quality <select id="qSel"><option value="low">Low</option><option value="med" selected>Medium</option><option value="high">High</option></select></label>
      <div class="cap">Audio starts after your first click</div>
    </div></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
'use strict';
/* ============================================================
   TIDEHAVEN — procedural coastal diorama
   Sections: setup · lighting · tank · island · cabin & pier
   water shaders · sea life · interactions · audio · loop
============================================================ */

/* ---------- core setup ---------- */
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.1, 400);
camera.position.set(34, 26, 34);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.06;
controls.target.set(0, 2, 0);
controls.minDistance = 8; controls.maxDistance = 120;
controls.maxPolarAngle = Math.PI*0.52;

scene.fog = new THREE.FogExp2(0xa8d8e4, 0.012);
scene.background = new THREE.Color(0xa8d8e4);

/* ---------- state ---------- */
const S = {
  time:0, paused:false, wind:0.5, tide:0,
  timeOfDay:'day', night:0, nightTarget:0,
  kayak:'moored', kayakA:0, kayakRet:null,
  jump:null
};
const W = 64, D = 44, HALF = {x:32, z:22};   // tank footprint
const SEABED = -14;

/* ---------- lighting ---------- */
const hemi = new THREE.HemisphereLight(0x9fd8e8, 0xc9b28a, 0.8); scene.add(hemi);
const amb  = new THREE.AmbientLight(0xffffff, 0.22); scene.add(amb);
const sun  = new THREE.DirectionalLight(0xfff2df, 1.15);
sun.position.set(25,35,12); sun.castShadow = true;
sun.shadow.mapSize.set(1024,1024); sun.shadow.camera.near=1; sun.shadow.camera.far=140;
const sd = 46; sun.shadow.camera.left=-sd; sun.shadow.camera.right=sd;
sun.shadow.camera.top=sd; sun.shadow.camera.bottom=-sd;
sun.shadow.bias = -0.0008;
scene.add(sun);

const TIME_PRESETS = {
  day:   {sky:0x9fd8e8, ground:0xc9b28a, hemi:.8,  sunPos:[25,35,12],  sunCol:0xfff2df, sunInt:1.15, bg:0xa8d8e4, fog:.012, night:0},
  sunset:{sky:0xf2b28a, ground:0x8a6a52, hemi:.55, sunPos:[40,9,-10],  sunCol:0xff9a52, sunInt:1.0,  bg:0xe08a5a, fog:.017, night:.42},
  night: {sky:0x2a4060, ground:0x1a2430, hemi:.25, sunPos:[-25,22,-15],sunCol:0x8fb0e8, sunInt:.35,  bg:0x0a1626, fog:.019, night:1}
};
const LP = {sky:new THREE.Color(), ground:new THREE.Color(), sunCol:new THREE.Color(), bg:new THREE.Color()};
// init lerped values to day
(function(){const p=TIME_PRESETS.day; LP.sky.setHex(p.sky); LP.ground.setHex(p.ground);
 LP.sunCol.setHex(p.sunCol); LP.bg.setHex(p.bg); hemi.color.copy(LP.sky); hemi.groundColor.copy(LP.ground);
 sun.color.copy(LP.sunCol); scene.background.copy(LP.bg); scene.fog.color.copy(LP.bg);})();

/* ---------- tiny helpers ---------- */
function noise3(x,y,z){ return Math.sin(x*0.7+1.3)*Math.cos(z*0.9-y*0.5)*0.5 + Math.sin(x*1.7+z*1.3+y)*0.25; }
function lerpC(cur, target, k){ cur.lerp(target, k); }
const ease = t => t<.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2;

/* ============================================================
   DIORAMA TANK — glass box, wooden frame, pedestal
============================================================ */
const tank = new THREE.Group(); scene.add(tank);
const woodMat = new THREE.MeshStandardMaterial({color:0x5a4632, roughness:.85});
const H = 32;
// glass shell (all faces, very subtle)
const glass = new THREE.Mesh(new THREE.BoxGeometry(W, H, D),
  new THREE.MeshBasicMaterial({color:0xbfe8e8, transparent:true, opacity:0.05, side:THREE.DoubleSide, depthWrite:false}));
glass.renderOrder = 6; tank.add(glass);
// frame edges
const edgeGeoX = new THREE.BoxGeometry(W+0.6,0.55,0.55),
      edgeGeoY = new THREE.BoxGeometry(0.55,H+0.6,0.55),
      edgeGeoZ = new THREE.BoxGeometry(0.55,0.55,D+0.6);
[[-1,-1],[1,-1],[1,1],[-1,1]].forEach(([sx,sz])=>{
  const ex = new THREE.Mesh(edgeGeoX, woodMat); ex.position.set(0, 16*sx===16?16: -16, sz*HALF.z); // top/bottom along x
  const e1 = new THREE.Mesh(edgeGeoX, woodMat); e1.position.set(0, 16, sz*HALF.z);
  const e2 = new THREE.Mesh(edgeGeoX, woodMat); e2.position.set(0,-16, sz*HALF.z);
  const e3 = new THREE.Mesh(edgeGeoZ, woodMat); e3.position.set(sx*HALF.x, 16, 0);
  const e4 = new THREE.Mesh(edgeGeoZ, woodMat); e4.position.set(sx*HALF.x,-16, 0);
  const e5 = new THREE.Mesh(edgeGeoY, woodMat); e5.position.set(sx*HALF.x, 0, sz*HALF.z);
  tank.add(e1,e2,e3,e4,e5);
});
// pedestal
const pedestal = new THREE.Mesh(new THREE.BoxGeometry(W+3, 3.5, D+3),
  new THREE.MeshStandardMaterial({color:0x463322, roughness:.9}));
pedestal.position.y = -17.75; pedestal.receiveShadow = true; tank.add(pedestal);

/* ============================================================
   ISLAND — lathed terrain with vertex colors
============================================================ */
const profile = [ new THREE.Vector2(0,8), new THREE.Vector2(6,8), new THREE.Vector2(10,4),
  new THREE.Vector2(13.5,0.5), new THREE.Vector2(14.5,-0.6), new THREE.Vector2(16,-3),
  new THREE.Vector2(20,-13.8) ];
const islandGeo = new THREE.LatheGeometry(profile, 48);
// displace + color
{
  const pos = islandGeo.attributes.position, n = pos.count;
  const colors = new Float32Array(n*3);
  const sand=new THREE.Color(0.90,0.78,0.56), grass=new THREE.Color(0.40,0.60,0.28),
        wet=new THREE.Color(0.62,0.60,0.44), deep=new THREE.Color(0.45,0.50,0.40);
  for(let i=0;i<n;i++){
    let x=pos.getX(i), y=pos.getY(i), z=pos.getZ(i);
    const top = THREE.MathUtils.smoothstep(y,6,8);           // keep plateau flat
    const d = noise3(x,y,z)*(1-top*0.8);
    const r = Math.hypot(x,z);
    if(r>0.01){ const k = 1 + d*0.05; pos.setX(i,x*k); pos.setZ(i,z*k); }
    pos.setY(i, y + d*0.9*(1-top));
    const yy = pos.getY(i);
    let c;
    if(yy < 0.1) c = sand.clone().lerp(wet, THREE.MathUtils.smoothstep(yy,0.1,-1.5));
    else if(yy < 2.2) c = sand.clone().lerp(grass, THREE.MathUtils.smoothstep(yy,0.6,2.2));
    else c = grass.clone();
    if(yy < -1.5) c = c.clone().lerp(deep, THREE.MathUtils.smoothstep(yy,-1.5,-13));
    colors[i*3]=c.r; colors[i*3+1]=c.g; colors[i*3+2]=c.b;
  }
  islandGeo.setAttribute('color', new THREE.BufferAttribute(colors,3));
  islandGeo.computeVertexNormals();
}
const island = new THREE.Mesh(islandGeo, new THREE.MeshStandardMaterial({vertexColors:true, flatShading:true, roughness:.95}));
island.castShadow = island.receiveShadow = true; scene.add(island);

// seabed plane with caustics shader
const seabedMat = new THREE.ShaderMaterial({
  uniforms:{ uTime:{value:0}, uNight:{value:0} },
  vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.); vW=w.xyz;
    gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`uniform float uTime; uniform float uNight; varying vec3 vW;
    void main(){ vec2 p=vW.xz*0.35; float t=uTime*0.55;
      float w1=sin(p.x*3.0+t)+sin(p.y*2.4-t);
      float w2=sin((p.x+p.y)*2.2+t*1.3)+sin((p.x-p.y)*2.6-t*0.8);
      float ca=clamp(pow(abs(w1*w2)*0.25,3.0),0.0,0.8);
      vec3 sand=vec3(0.82,0.70,0.50);
      vec3 col=sand*(0.22+0.35*ca+0.06*sin(vW.x*0.15));
      col+=vec3(0.08,0.45,0.40)*ca*0.4;
      col*=mix(0.30,1.0,1.0-uNight*0.62);
      gl_FragColor=vec4(col,1.0); }`
});
const seabed = new THREE.Mesh(new THREE.PlaneGeometry(W, D, 1, 1).rotateX(-Math.PI/2), seabedMat);
seabed.position.y = SEABED; scene.add(seabed);

/* ============================================================
   WATER — surface, cutaway walls, tint volume  (render-order sorted)
============================================================ */
// --- surface ---
const surfMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, side:THREE.DoubleSide,
  uniforms:{ uTime:{value:0}, uWave:{value:.5}, uShoreR:{value:14}, uNight:{value:0} },
  vertexShader:`
    uniform float uTime, uWave;
    varying vec3 vW; varying vec3 vN;
    float wave(vec2 p, float t){
      float a = 0.06 + uWave*0.30;
      float damp = smoothstep(6.0,16.0,length(p));
      return (sin(p.x*0.55+t*1.4) + 0.8*sin(p.y*0.40-t*1.1) + 0.6*sin((p.x+p.y)*0.30+t*0.7))*a*damp;
    }
    void main(){
      vec3 pos = position; vec2 p = pos.xz;
      pos.y += wave(p,uTime);
      float e=0.6;
      float hx = wave(p+vec2(e,0.),uTime)-wave(p-vec2(e,0.),uTime);
      float hz = wave(p+vec2(0.,e),uTime)-wave(p-vec2(0.,e),uTime);
      vN = normalize(vec3(-hx,2.0*e,-hz));
      vec4 w = modelMatrix*vec4(pos,1.0); vW = w.xyz;
      gl_Position = projectionMatrix*viewMatrix*w;
    }`,
  fragmentShader:`
    uniform float uTime, uShoreR, uNight;
    varying vec3 vW; varying vec3 vN;
    void main(){
      float d = length(vW.xz);
      vec3 deep=vec3(0.07,0.36,0.42), shal=vec3(0.28,0.72,0.66), foam=vec3(0.95,0.98,0.97);
      vec3 col = mix(shal, deep, smoothstep(14.0,26.0,d));
      vec3 V = normalize(cameraPosition - vW);
      float fres = pow(1.0-max(dot(V,vN),0.0),3.0);
      col = mix(col, mix(shal,vec3(0.72,0.84,0.90),0.55), fres*0.5);
      float sparkle = pow(max(sin(vW.x*1.3+vW.z*0.9+uTime*2.2),0.0),22.0)*0.25*smoothstep(7.0,14.0,d);
      col += vec3(sparkle);
      float band = 1.0 - smoothstep(uShoreR-0.5, uShoreR+1.7, d);
      float ripple = 0.5+0.5*sin(d*9.0-uTime*2.6);
      float f = band*smoothstep(0.25,0.85,ripple);
      col = mix(col, foam, f*0.85);
      float alpha = mix(0.72, 0.95, smoothstep(uShoreR, uShoreR+4.0, d));
      alpha = mix(alpha, 0.92, f);
      col *= mix(0.32,1.0,1.0-uNight*0.66);
      gl_FragColor = vec4(col, alpha);
    }`
});
const waterSurface = new THREE.Mesh(new THREE.PlaneGeometry(W, D, 56, 40).rotateX(-Math.PI/2), surfMat);
waterSurface.renderOrder = 4; scene.add(waterSurface);

// --- cutaway walls (front +z, right +x) with tide clipping ---
const wallMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, side:THREE.DoubleSide,
  uniforms:{ uTide:{value:0}, uNight:{value:0} },
  vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.); vW=w.xyz;
    gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`uniform float uTide,uNight; varying vec3 vW;
    void main(){
      if(vW.y > uTide+0.02 || vW.y < -14.05) discard;
      vec3 top=vec3(0.30,0.74,0.68), bot=vec3(0.04,0.28,0.32);
      float g=smoothstep(-14.0,0.0,vW.y);
      vec3 col=mix(bot,top,g);
      float a=0.34*mix(1.0,0.45,smoothstep(-2.5,0.0,vW.y));
      float meniscus=smoothstep(0.35,0.0,abs(vW.y-uTide));
      col=mix(col,vec3(0.92,0.97,0.95),meniscus*0.7); a=mix(a,0.8,meniscus);
      col*=mix(0.32,1.0,1.0-uNight*0.62);
      gl_FragColor=vec4(col,a);
    }`
});
const wallF = new THREE.Mesh(new THREE.PlaneGeometry(W,34), wallMat);
wallF.position.set(0,-1,HALF.z-0.05); wallF.renderOrder=3; scene.add(wallF);
const wallR = new THREE.Mesh(new THREE.PlaneGeometry(D,34), wallMat);
wallR.rotation.y = -Math.PI/2; wallR.position.set(HALF.x-0.05,-1,0); wallR.renderOrder=3; scene.add(wallR);

// --- underwater tint volume ---
const tint = new THREE.Mesh(new THREE.BoxGeometry(W-0.1, 30, D-0.1),
  new THREE.MeshBasicMaterial({color:0x1f8f86, transparent:true, opacity:0.16, side:THREE.BackSide, depthWrite:false}));
tint.renderOrder = 2; scene.add(tint);

/* ============================================================
   CABIN — A-frame, deck, glowing windows, props
============================================================ */
const cabinG = new THREE.Group();
const woodA = new THREE.MeshStandardMaterial({color:0x8b6a44, roughness:.8});
const woodB = new THREE.MeshStandardMaterial({color:0x6e5136, roughness:.85});
const copper = new THREE.MeshStandardMaterial({color:0xc97f4a, roughness:.45, metalness:.55});
const glowMat = new THREE.MeshStandardMaterial({color:0x33281f, emissive:0xffb45e, emissiveIntensity:0.1, roughness:.6});
{
  // A-frame roof panels
  const roofGeo = new THREE.BoxGeometry(3.6, 0.22, 5.2);
  const rL = new THREE.Mesh(roofGeo, copper); rL.rotation.z = 0.72; rL.position.set(-1.15, 2.35, 0);
  const rR = new THREE.Mesh(roofGeo, copper); rR.rotation.z = -0.72; rR.position.set(1.15, 2.35, 0);
  // gable triangles (front/back)
  const tri = new THREE.BufferGeometry();
  tri.setAttribute('position', new THREE.Float32BufferAttribute([-1.9,0,0, 1.9,0,0, 0,3.1,0],3));
  tri.computeVertexNormals();
  const gF = new THREE.Mesh(tri, woodA); gF.position.set(0,0.35,2.61);
  const gB = new THREE.Mesh(tri, woodA); gB.position.set(0,0.35,-2.61); gB.rotation.y=Math.PI;
  // side walls (low)
  const wallGeo = new THREE.BoxGeometry(3.2, 1.1, 5.0);
  const wL = new THREE.Mesh(wallGeo, woodB); wL.position.set(-1.35,0.55,0);
  const wR = new THREE.Mesh(wallGeo, woodB); wR.position.set( 1.35,0.55,0);
  // windows + door
  const winGeo = new THREE.BoxGeometry(0.9,0.9,0.1);
  const win1 = new THREE.Mesh(winGeo, glowMat); win1.position.set(-0.85,1.15,2.66);
  const win2 = new THREE.Mesh(winGeo, glowMat); win2.position.set( 0.85,1.15,2.66);
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.9,1.6,0.12), woodB); door.position.set(0,0.8,2.66);
  // chimney
  const chim = new THREE.Mesh(new THREE.BoxGeometry(0.5,1.4,0.5), new THREE.MeshStandardMaterial({color:0x777066,roughness:.9}));
  chim.position.set(1.1,3.4,-1.2);
  cabinG.add(rL,rR,gF,gB,wL,wR,win1,win2,door,chim);
  cabinG.children.forEach(c=>{c.castShadow=true;c.receiveShadow=true;});
}
cabinG.position.set(-0.5, 8.15, -0.5); scene.add(cabinG);
const windowMats = [glowMat];

// deck + railing + bench + towels + crates + plants
const topProps = new THREE.Group(); topProps.position.set(0,8.1,0); scene.add(topProps);
{
  const deck = new THREE.Mesh(new THREE.BoxGeometry(6.5,0.22,4.2), woodA);
  deck.position.set(0.2,0.11,3.6); deck.castShadow=deck.receiveShadow=true; topProps.add(deck);
  const railGeo = new THREE.CylinderGeometry(0.07,0.07,1.0,6);
  [[-2.9,5.6],[3.4,5.6],[-2.9,1.7],[3.4,1.7],[0.2,5.6]].forEach(([x,z])=>{
    const p = new THREE.Mesh(railGeo, woodB); p.position.set(x,0.7,z); p.castShadow=true; topProps.add(p);
  });
  const bar = new THREE.Mesh(new THREE.BoxGeometry(6.4,0.1,0.1), woodB); bar.position.set(0.2,1.15,5.6); topProps.add(bar);
  // bench
  const bench = new THREE.Group();
  const seat = new THREE.Mesh(new THREE.BoxGeometry(1.8,0.12,0.6), woodA); seat.position.y=0.55;
  [-0.75,0.75].forEach(x=>{ const leg=new THREE.Mesh(new THREE.BoxGeometry(0.12,0.55,0.5),woodB); leg.position.set(x,0.27,0); bench.add(leg); });
  bench.add(seat); bench.position.set(2.6,0.22,3.0); bench.rotation.y=-0.4;
  // towels on rail
  const towel1 = new THREE.Mesh(new THREE.BoxGeometry(0.9,0.06,0.7), new THREE.MeshStandardMaterial({color:0xe2725b,roughness:.95}));
  towel1.position.set(-1.6,1.22,5.55); towel1.rotation.x=0.25;
  const towel2 = new THREE.Mesh(new THREE.BoxGeometry(0.9,0.06,0.7), new THREE.MeshStandardMaterial({color:0x62b6cb,roughness:.95}));
  towel2.position.set(1.9,1.22,5.55); towel2.rotation.x=0.25;
  // crates
  const crateGeo = new THREE.BoxGeometry(0.9,0.7,0.9);
  const cr1 = new THREE.Mesh(crateGeo, woodB); cr1.position.set(-2.5,0.58,2.2); cr1.rotation.y=0.3;
  const cr2 = new THREE.Mesh(crateGeo, woodB); cr2.position.set(-2.2,1.28,2.35); cr2.rotation.y=0.75;
  topProps.add(bench,towel1,towel2,cr1,cr2);
  // potted plants
  const potMat = new THREE.MeshStandardMaterial({color:0xb96f4a, roughness:.9});
  const leafMat = new THREE.MeshStandardMaterial({color:0x4f9e5c, roughness:.8});
  [[-2.9,4.6],[3.3,3.4],[1.6,1.6]].forEach(([x,z],i)=>{
    const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.28,0.22,0.4,8), potMat); pot.position.set(x,0.42,z);
    for(let k=0;k<3;k++){ const lf = new THREE.Mesh(new THREE.ConeGeometry(0.16,0.6,5), leafMat);
      lf.position.set(x+Math.cos(k*2.1)*0.12, 0.95, z+Math.sin(k*2.1)*0.12); lf.rotation.set(Math.cos(k*2.1)*0.4,0,Math.sin(k*2.1)*0.4);
      topProps.add(lf);} topProps.add(pot);
  });
  topProps.children.forEach(c=>{c.castShadow=true;});
}

/* ---------- trees & grass (swaying) ---------- */
const trees = [];
const leafMat = new THREE.MeshStandardMaterial({color:0x4e8f4a, roughness:.85, flatShading:true});
const trunkMat = new THREE.MeshStandardMaterial({color:0x7a5a3a, roughness:.9});
const trunkGeo = new THREE.CylinderGeometry(0.14,0.22,1.6,7);
const canopyGeo = new THREE.SphereGeometry(1,7,6);
function groundY(r){ // approximate island surface height at radius r
  if(r<=6) return 8; if(r<=10) return 8 + (r-6)/4*(4-8);
  if(r<=13.5) return 4 + (r-10)/3.5*(0.5-4); return 0.5;
}
[[-3.5,-3.5,1.15],[3.2,-4.2,1.0],[-4.6,3.2,0.95]].forEach(([x,z,sc])=>{
  const g = new THREE.Group();
  const t = new THREE.Mesh(trunkGeo, trunkMat); t.position.y=0.8; t.castShadow=true;
  const c1 = new THREE.Mesh(canopyGeo, leafMat); c1.scale.setScalar(sc); c1.position.y=2.1; c1.castShadow=true;
  const c2 = new THREE.Mesh(canopyGeo, leafMat); c2.scale.set(sc*0.7,sc*0.7,sc*0.7); c2.position.set(0.5,1.6,0.3); c2.castShadow=true;
  g.add(t,c1,c2);
  const r=Math.hypot(x,z); g.position.set(x, groundY(r)-0.15, z);
  scene.add(g); trees.push(g);
});
// instanced grass with sway shader
const bladeGeo = new THREE.PlaneGeometry(0.13,0.6,1,2).translate(0,0.3,0);
const grassMat = new THREE.MeshLambertMaterial({color:0x6fa052, side:THREE.DoubleSide});
const uGrass = {uTime:{value:0}, uWind:{value:0.5}};
grassMat.onBeforeCompile = s=>{
  s.uniforms.uTime=uGrass.uTime; s.uniforms.uWind=uGrass.uWind;
  s.vertexShader = 'uniform float uTime; uniform float uWind;\n' + s.vertexShader;
  s.vertexShader = s.vertexShader.replace('#include <begin_vertex>',
    `#include <begin_vertex>
     transformed.x += sin(uTime*2.2 + instanceMatrix[3][0]*0.7 + instanceMatrix[3][2]*0.9)*uWind*position.y*0.5;`);
};
{
  const N=240, grass = new THREE.InstancedMesh(bladeGeo, grassMat, N);
  const d = new THREE.Object3D();
  for(let i=0;i<N;i++){
    const a=Math.random()*Math.PI*2, r=5+Math.random()*7.5;
    const x=Math.cos(a)*r, z=Math.sin(a)*r;
    d.position.set(x, groundY(r)-0.05, z); d.rotation.set(0,Math.random()*Math.PI,(Math.random()-0.5)*0.3);
    d.scale.setScalar(0.7+Math.random()*0.8); d.updateMatrix(); grass.setMatrixAt(i,d.matrix);
  }
  grass.castShadow=true; scene.add(grass);
}
// shore rocks — instanced
{
  const rockGeo = new THREE.IcosahedronGeometry(0.8,0);
  const rockMat = new THREE.MeshStandardMaterial({color:0x9b8f7e, roughness:.95, flatShading:true});
  const N=14, rocks=new THREE.InstancedMesh(rockGeo,rockMat,N), d=new THREE.Object3D();
  for(let i=0;i<N;i++){
    const a=(i/N)*Math.PI*2+Math.random(), r=12.6+Math.random()*2.2;
    d.position.set(Math.cos(a)*r, -0.2+Math.random()*0.4, Math.sin(a)*r);
    d.rotation.set(Math.random(),Math.random(),Math.random());
    d.scale.set(0.6+Math.random(),0.4+Math.random()*0.5,0.6+Math.random());
    d.updateMatrix(); rocks.setMatrixAt(i,d.matrix);
  }
  rocks.castShadow=rocks.receiveShadow=true; scene.add(rocks);
}

/* ============================================================
   PIER — planks, posts, lanterns, ladder, kayak, mooring rope
============================================================ */
const PIER_END = new THREE.Vector3(0,0,20.5);
const lanternLights = [];
{
  const pier = new THREE.Group();
  const deckP = new THREE.Mesh(new THREE.BoxGeometry(1.9,0.16,11), woodA);
  deckP.position.set(0,0.9,15.5); deckP.castShadow=deckP.receiveShadow=true; pier.add(deckP);
  const postGeo = new THREE.CylinderGeometry(0.13,0.15,9,7);
  for(let i=0;i<5;i++){ [-0.75,0.75].forEach(x=>{
    const p=new THREE.Mesh(postGeo,woodB); p.position.set(x,-3.6,10.8+i*2.4); p.castShadow=true; pier.add(p);});}
  // ladder
  const railGeo = new THREE.BoxGeometry(0.1,6,0.1);
  [-0.35,0.35].forEach(x=>{ const r=new THREE.Mesh(railGeo,woodB); r.position.set(x,-2.1,20.2); r.rotation.x=0.12; pier.add(r); });
  for(let i=0;i<4;i++){ const rung=new THREE.Mesh(new THREE.BoxGeometry(0.7,0.08,0.08),woodB);
    rung.position.set(0,0.4-i*1.35,20.05+i*0.16); pier.add(rung); }
  // lanterns
  const lampGlow = new THREE.MeshStandardMaterial({color:0x2a2a2a, emissive:0xffc46b, emissiveIntensity:0.15, roughness:.5});
  [11.2,15.5,19.8].forEach(z=>{
    const post=new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,1.6,6),woodB); post.position.set(0.8,1.75,z);
    const bulb=new THREE.Mesh(new THREE.SphereGeometry(0.18,10,8), lampGlow); bulb.position.set(0.8,2.6,z);
    const L=new THREE.PointLight(0xffb45e,0,9,2); L.position.set(0.8,2.6,z); lanternLights.push(L);
    pier.add(post,bulb,L);
  });
  // crate on pier
  const cr=new THREE.Mesh(new THREE.BoxGeometry(0.8,0.6,0.8),woodB); cr.position.set(-0.55,1.28,12.2); cr.rotation.y=0.4; cr.castShadow=true; pier.add(cr);
  scene.add(pier);
  // cabin door lantern
  const lb=new THREE.Mesh(new THREE.SphereGeometry(0.16,10,8), lampGlow);
  lb.position.set(0.9,9.6,2.1); scene.add(lb);
  const L2=new THREE.PointLight(0xffb45e,0,8,2); L2.position.set(0.9,9.6,2.2); lanternLights.push(L2);
}
// kayak
const kayak = new THREE.Group();
{
  const hull = new THREE.Mesh(new THREE.SphereGeometry(1,16,10),
    new THREE.MeshStandardMaterial({color:0xf4b942, roughness:.4, flatShading:true}));
  hull.scale.set(1.9,0.32,0.55); hull.castShadow=true;
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.14,0.4), woodB); seat.position.y=0.28;
  const paddle = new THREE.Mesh(new THREE.BoxGeometry(1.8,0.05,0.05), woodA); paddle.position.set(0,0.42,0.35); paddle.rotation.y=0.6;
  kayak.add(hull,seat,paddle);
}
scene.add(kayak);
const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.025,0.025,2.2,5),
  new THREE.MeshStandardMaterial({color:0xd8c9a0}));
rope.rotation.z=Math.PI/2; rope.rotation.y=0.5; scene.add(rope);
function setKayakMoored(){
  kayak.position.set(1.7, S.tide+0.12, 19.2); kayak.rotation.set(0,0.35,0);
  rope.position.set(0.85,S.tide+0.55,19.8); rope.visible=true;
}
setKayakMoored();
// bobbing buoys
const buoys=[];
[[18,-11],[-20,9]].forEach(([x,z],i)=>{
  const b=new THREE.Mesh(new THREE.SphereGeometry(0.45,10,8),
    new THREE.MeshStandardMaterial({color:i?0xe2725b:0xf2f0e0, roughness:.5}));
  b.castShadow=true; scene.add(b); buoys.push({m:b,x,z});
});

/* ============================================================
   SEA LIFE — rays, fish school, seagrass, bubbles
============================================================ */
const rayMat = new THREE.MeshStandardMaterial({color:0x8f9aa6, roughness:.7, flatShading:true});
const rays = [];
function makeRay(x,z,depth,rad,speed,phase){
  const g=new THREE.Group();
  const body=new THREE.Mesh(new THREE.SphereGeometry(1,14,10), rayMat);
  body.scale.set(2.2,0.45,1.5); body.castShadow=true;
  const finGeo=new THREE.ConeGeometry(0.9,1.6,4);
  const fL=new THREE.Mesh(finGeo,rayMat); fL.scale.set(0.25,1,0.7); fL.rotation.z=Math.PI/2; fL.position.set(-0.3,0.05,1.15);
  const fR=new THREE.Mesh(finGeo,rayMat); fR.scale.set(0.25,1,0.7); fR.rotation.z=Math.PI/2; fR.position.set(-0.3,0.05,-1.15);
  const tail=new THREE.Mesh(new THREE.ConeGeometry(0.55,1.9,4),rayMat);
  tail.scale.set(0.3,1,0.55); tail.rotation.z=Math.PI/2; tail.position.set(-2.7,0,0);
  g.add(body,fL,fR,tail);
  g.position.set(x,depth,z); scene.add(g);
  rays.push({g,body,tail,angle:Math.atan2(z,x),rad,depth,speed,phase});
}
makeRay(18,-4,-4.5,19,0.13,0); makeRay(-17,8,-6,18,-0.11,2); makeRay(6,16,-5,17,0.15,4);
const LEAP_RAY = rays[0];

// fish school — instanced
const fishGeo = new THREE.ConeGeometry(0.13,0.55,5).rotateX(-Math.PI/2); // faces +z
const fishMat = new THREE.MeshStandardMaterial({color:0xffffff, roughness:.6});
const FISH_N=42, fish=new THREE.InstancedMesh(fishGeo,fishMat,FISH_N);
const fishData=[];
{
  const cols=[new THREE.Color(0xf08a4b),new THREE.Color(0x62b6cb),new THREE.Color(0xf2e3ae),new THREE.Color(0xa86bd9)];
  for(let i=0;i<FISH_N;i++){
    fishData.push({r:15+Math.random()*8, y:-2.5-Math.random()*9, a:Math.random()*Math.PI*2,
      s:(0.25+Math.random()*0.2)*(Math.random()<0.5?1:-1), ph:Math.random()*10, sc:0.7+Math.random()*0.8});
    fish.setColorAt(i, cols[i%cols.length]);
  }
  fish.instanceColor.needsUpdate=true;
}
scene.add(fish);

// seagrass — instanced with sway
const blade2 = new THREE.PlaneGeometry(0.32,2.2,1,4).translate(0,1.1,0);
const seaMat = new THREE.MeshLambertMaterial({color:0x2f8f5a, side:THREE.DoubleSide});
const uSea={uTime:{value:0},uWind:{value:0.5}};
seaMat.onBeforeCompile=s=>{
  s.uniforms.uTime=uSea.uTime; s.uniforms.uWind=uSea.uWind;
  s.vertexShader='uniform float uTime; uniform float uWind;\n'+s.vertexShader;
  s.vertexShader=s.vertexShader.replace('#include <begin_vertex>',
   `#include <begin_vertex>
    transformed.x += sin(uTime*1.6 + instanceMatrix[3][0]*0.5 + instanceMatrix[3][2]*0.7)*(0.25+uWind)*position.y*0.45;`);
};
{
  const N=46, sg=new THREE.InstancedMesh(blade2,seaMat,N), d=new THREE.Object3D();
  for(let i=0;i<N;i++){
    const a=Math.random()*Math.PI*2, r=17+Math.random()*11;
    d.position.set(Math.cos(a)*r*1.2, SEABED, Math.sin(a)*r*0.85);
    d.rotation.set(0,Math.random()*Math.PI,0); d.scale.setScalar(0.7+Math.random()*0.9);
    d.updateMatrix(); sg.setMatrixAt(i,d.matrix);
  }
  scene.add(sg);
}
// bubbles — instanced pool
const BUB_N=48;
const bubbles=new THREE.InstancedMesh(new THREE.SphereGeometry(0.1,6,6),
  new THREE.MeshBasicMaterial({color:0xcfeef0, transparent:true, opacity:0.5, depthWrite:false}), BUB_N);
bubbles.renderOrder=3;
const bubData=[];
for(let i=0;i<BUB_N;i++) bubData.push({x:0,y:SEABED,z:0,sp:0,ph:Math.random()*10});
scene.add(bubbles);
const BUB_EMIT=[[0,-12,20],[8,-13,-8],[-14,-13,10],[16,-13,14]];

// ripples + droplets pools
const ripples=[];
for(let i=0;i<5;i++){
  const r=new THREE.Mesh(new THREE.RingGeometry(0.6,0.85,40),
    new THREE.MeshBasicMaterial({color:0xe8fbf6, transparent:true, opacity:0, depthWrite:false, side:THREE.DoubleSide}));
  r.rotation.x=-Math.PI/2; r.renderOrder=5; r.visible=false; scene.add(r); ripples.push({m:r,t:1});
}
const DROP_N=22;
const drops=new THREE.InstancedMesh(new THREE.SphereGeometry(0.09,6,6),
  new THREE.MeshBasicMaterial({color:0xbfeee8, transparent:true, opacity:0.85, depthWrite:false}), DROP_N);
drops.renderOrder=5; scene.add(drops);
const dropData=[]; for(let i=0;i<DROP_N;i++) dropData.push({life:0,p:new THREE.Vector3(),v:new THREE.Vector3()});

// stars (night)
{
  const n=220, pos=new Float32Array(n*3);
  for(let i=0;i<n;i++){ const a=Math.random()*Math.PI*2, e=Math.random()*Math.PI*0.45, R=90;
    pos[i*3]=Math.cos(a)*Math.cos(e)*R; pos[i*3+1]=Math.sin(e)*R+8; pos[i*3+2]=Math.sin(a)*Math.cos(e)*R; }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  var stars=new THREE.Points(g,new THREE.PointsMaterial({color:0xf5f2e0,size:0.7,transparent:true,opacity:0}));
  scene.add(stars);
}

/* ============================================================
   CAMERA presets + smooth transitions
============================================================ */
const CAM = {
  iso:   {pos:new THREE.Vector3(34,26,34),  tgt:new THREE.Vector3(0,2,0)},
  cabin: {pos:new THREE.Vector3(9,10,21),   tgt:new THREE.Vector3(-1,8,4)},
  under: {pos:new THREE.Vector3(15,-7,15),  tgt:new THREE.Vector3(-2,-5,0)},
};
let camAnim=null;
function goCam(name){
  document.querySelectorAll('[data-cam]').forEach(b=>b.classList.toggle('active', b.dataset.cam===name));
  if(name==='free'){ camAnim=null; return; }
  const p=CAM[name];
  camAnim={t:0, from:camera.position.clone(), fromT:controls.target.clone(), to:p.pos.clone(), toT:p.tgt.clone()};
}
goCam('iso');

/* ============================================================
   AUDIO — procedural pad, plucks, breeze, water
============================================================ */
let AC=null, master, musicGain, breezeGain, waterGain, musicOn=false, oscs=[], audioReady=false;
function ensureAudio(){
  if(audioReady) return; audioReady=true;
  const Ctx = window.AudioContext||window.webkitAudioContext; if(!Ctx) return;
  AC=new Ctx();
  master=AC.createGain(); master.gain.value=parseFloat(sVol.value); master.connect(AC.destination);
  musicGain=AC.createGain(); musicGain.gain.value=0; musicGain.connect(master);
  // pad
  const lp=AC.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=650; lp.connect(musicGain);
  [220,277,330].forEach(f=>{ const o=AC.createOscillator(); o.type='sine'; o.frequency.value=f;
    const g=AC.createGain(); g.gain.value=0.09; o.connect(g); g.connect(lp); o.start(); oscs.push(o); });
  const chords=[[220,277,330],[196,247,294],[175,220,262],[196,262,330],[165,220,262],[196,247,330]];
  setInterval(()=>{ if(!AC) return; const c=chords[Math.floor(Math.random()*chords.length)];
    oscs.forEach((o,i)=>o.frequency.setTargetAtTime(c[i],AC.currentTime,2.5)); },4200);
  // plucks
  const notes=[523,587,659,784,880,1047];
  setInterval(()=>{ if(!AC||!musicOn) return;
    const o=AC.createOscillator(), g=AC.createGain(); o.type='triangle';
    o.frequency.value=notes[Math.floor(Math.random()*notes.length)]*(Math.random()<0.3?0.5:1);
    const t=AC.currentTime; g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(0.10,t+0.04);
    g.gain.exponentialRampToValueAtTime(0.001,t+1.6); o.connect(g); g.connect(musicGain); o.start(t); o.stop(t+1.7);
  },2300);
  // noise helper
  function noise(){ const b=AC.createBuffer(1,AC.sampleRate*2,AC.sampleRate);
    const d=b.getChannelData(0); for(let i=0;i<d.length;i++) d[i]=Math.random()*2-1;
    const s=AC.createBufferSource(); s.buffer=b; s.loop=true; s.start(); return s; }
  // breeze
  const nb=noise(); const bp=AC.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=480; bp.Q.value=0.6;
  breezeGain=AC.createGain(); breezeGain.gain.value=0.03; nb.connect(bp); bp.connect(breezeGain); breezeGain.connect(master);
  // water
  const nw=noise(); const wl=AC.createBiquadFilter(); wl.type='lowpass'; wl.frequency.value=520;
  waterGain=AC.createGain(); waterGain.gain.value=0.05; nw.connect(wl); wl.connect(waterGain); waterGain.connect(master);
  const lfo=AC.createOscillator(); lfo.frequency.value=0.18; const lg=AC.createGain(); lg.gain.value=0.035;
  lfo.connect(lg); lg.connect(waterGain.gain); lfo.start();
}
function setMusic(on){
  musicOn=on; bMusic.textContent='Music: '+(on?'On':'Off'); bMusic.classList.toggle('active',on);
  if(AC) musicGain.gain.setTargetAtTime(on?0.55:0, AC.currentTime, 0.8);
}

/* ============================================================
   UI wiring
============================================================ */
const $ = id=>document.getElementById(id);
const bKayak=$('bKayak'), bRay=$('bRay'), bPause=$('bPause'), bReset=$('bReset'),
      bMusic=$('bMusic'), sTide=$('sTide'), sWind=$('sWind'), sVol=$('sVol'), qSel=$('qSel');
// collapsible panels
document.querySelectorAll('.panel[data-p]').forEach(p=>{
  const head=p.querySelector('.phead');
  if(innerWidth<720) p.classList.add('closed');
  head.addEventListener('click',()=>{p.classList.toggle('closed');});
});
// start audio on any interaction
document.getElementById('ui').addEventListener('pointerdown',ensureAudio,{once:true});
renderer.domElement.addEventListener('pointerdown',ensureAudio,{once:true});

document.querySelectorAll('[data-cam]').forEach(b=>b.addEventListener('click',()=>{ensureAudio();goCam(b.dataset.cam);}));
document.querySelectorAll('[data-time]').forEach(b=>b.addEventListener('click',()=>{
  ensureAudio(); S.timeOfDay=b.dataset.time;
  document.querySelectorAll('[data-time]').forEach(x=>x.classList.toggle('active',x===b));
}));
document.querySelector('[data-time="day"]').classList.add('active');
bMusic.addEventListener('click',()=>{ensureAudio(); setMusic(!musicOn);});
bPause.addEventListener('click',()=>{ensureAudio(); S.paused=!S.paused;
  bPause.textContent=S.paused?'Resume':'Pause'; bPause.classList.toggle('active',S.paused);});
bReset.addEventListener('click',()=>{ensureAudio(); resetAll();});
bKayak.addEventListener('click',()=>{
  ensureAudio();
  if(S.kayak==='moored'){ S.kayak='out'; S.kayakA=Math.atan2(kayak.position.z,kayak.position.x);
    bKayak.textContent='Return Kayak'; rope.visible=false; }
  else if(S.kayak==='out'){ S.kayak='returning'; S.kayakRet=0; bKayak.textContent='Launch Kayak'; }
});
bRay.addEventListener('click',()=>{
  ensureAudio();
  if(S.jump) return;
  const r=LEAP_RAY, p=r.g.position.clone();
  const h=new THREE.Vector3(-Math.sin(r.angle),0,Math.cos(r.angle)).multiplyScalar(Math.sign(r.speed));
  S.jump={r,t:0,start:p,h,dur:2.4};
  bRay.classList.add('active'); setTimeout(()=>bRay.classList.remove('active'),2500);
});
sTide.addEventListener('input',()=>{ensureAudio(); S.tide=parseFloat(sTide.value);});
sWind.addEventListener('input',()=>{ensureAudio(); S.wind=parseFloat(sWind.value);
  if(AC) breezeGain.gain.setTargetAtTime(0.02+S.wind*0.05,AC.currentTime,0.3);});
sVol.addEventListener('input',()=>{ensureAudio(); if(AC) master.gain.setTargetAtTime(parseFloat(sVol.value),AC.currentTime,0.1);});
qSel.addEventListener('change',()=>{
  const q=qSel.value;
  renderer.setPixelRatio(Math.min(devicePixelRatio, q==='low'?1:q==='med'?1.5:2));
  const sz=q==='low'?512:q==='med'?1024:2048;
  sun.shadow.mapSize.set(sz,sz); if(sun.shadow.map){sun.shadow.map.dispose(); sun.shadow.map=null;}
});
function resetAll(){
  S.tide=0; sTide.value=0; S.wind=0.5; sWind.value=0.5;
  S.paused=false; bPause.textContent='Pause'; bPause.classList.remove('active');
  S.timeOfDay='day'; document.querySelectorAll('[data-time]').forEach(x=>x.classList.toggle('active',x.dataset.time==='day'));
  S.kayak='moored'; bKayak.textContent='Launch Kayak'; setKayakMoored(); S.jump=null;
  goCam('iso');
}
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));

/* ============================================================
   MAIN LOOP
============================================================ */
const clock=new THREE.Clock(); const dummy=new THREE.Object3D();
function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05);
  const wdt = S.paused?0:dt;
  S.time += wdt;
  const t=S.time;

  /* --- time of day (smooth lerp) --- */
  const P=TIME_PRESETS[S.timeOfDay], k=1-Math.exp(-dt*1.6);
  LP.sky.setHex(P.sky); LP.ground.setHex(P.ground); LP.sunCol.setHex(P.sunCol); LP.bg.setHex(P.bg);
  hemi.color.lerp(LP.sky,k); hemi.groundColor.lerp(LP.ground,k); hemi.intensity+=(P.hemi-hemi.intensity)*k;
  sun.color.lerp(LP.sunCol,k); sun.intensity+=(P.sunInt-sun.intensity)*k;
  sun.position.lerp(new THREE.Vector3(...P.sunPos),k);
  scene.background.lerp(LP.bg,k); scene.fog.color.lerp(LP.bg,k);
  scene.fog.density+=(P.fog-scene.fog.density)*k;
  S.night+=(P.night-S.night)*k;
  stars.material.opacity=S.night*0.9;
  // lamps & windows
  windowMats.forEach(m=>m.emissiveIntensity=0.1+S.night*2.2);
  lanternLights.forEach(L=>L.intensity=S.night*1.5);

  /* --- tide & waves --- */
  const surfY=S.tide;
  waterSurface.position.y=surfY;
  tint.position.y=surfY-15;
  surfMat.uniforms.uTime.value=t; surfMat.uniforms.uWave.value=S.wind;
  surfMat.uniforms.uShoreR.value=14 - surfY*0.9; surfMat.uniforms.uNight.value=S.night;
  wallMat.uniforms.uTide.value=surfY; wallMat.uniforms.uNight.value=S.night;
  seabedMat.uniforms.uTime.value=t; seabedMat.uniforms.uNight.value=S.night;
  uGrass.uTime.value=t; uGrass.uWind.value=0.25+S.wind;
  uSea.uTime.value=t; uSea.uWind.value=S.wind;

  /* --- trees sway --- */
  trees.forEach((g,i)=>{ g.rotation.z=Math.sin(t*1.3+i*2.1)*0.035*(0.3+S.wind); });

  /* --- kayak --- */
  const bob=(x,z)=>surfY+0.12+Math.sin(t*1.5+x*0.55)*0.10*(0.3+S.wind)+Math.cos(t*1.1+z*0.4)*0.07;
  if(S.kayak==='out'){
    S.kayakA+=wdt*0.28; const R=21.5;
    const x=Math.cos(S.kayakA)*R*1.25, z=Math.sin(S.kayakA)*R*0.85;
    kayak.position.set(x, bob(x,z), z);
    kayak.rotation.set(Math.sin(t*1.4)*0.06, -S.kayakA-0.9, Math.cos(t*1.1)*0.05);
  } else if(S.kayak==='returning'){
    S.kayakRet+=dt/2.2; const e=ease(Math.min(S.kayakRet,1));
    const tx=1.7,tz=19.2;
    kayak.position.x+=(tx-kayak.position.x)*k*3; kayak.position.z+=(tz-kayak.position.z)*k*3;
    kayak.position.y=bob(kayak.position.x,kayak.position.z);
    if(S.kayakRet>=1){ S.kayak='moored'; setKayakMoored(); }
  } else {
    kayak.position.y=bob(kayak.position.x,kayak.position.z);
    kayak.rotation.x=Math.sin(t*1.4)*0.05; kayak.rotation.z=Math.cos(t*1.1)*0.04;
    rope.position.y=kayak.position.y+0.45;
  }
  buoys.forEach((b,i)=>{ b.m.position.y=bob(b.x,b.z)+0.25; b.m.rotation.y=t*0.3+i; });

  /* --- rays --- */
  rays.forEach(r=>{
    if(S.jump && S.jump.r===r) return;
    r.angle+=r.speed*wdt;
    const x=Math.cos(r.angle)*r.rad*1.25, z=Math.sin(r.angle)*r.rad*0.85;
    r.g.position.set(x, r.depth+Math.sin(t*0.5+r.phase)*0.7, z);
    const hx=x-Math.cos(r.angle-r.speed*0.01)*r.rad*1.25, hz=z-Math.sin(r.angle-r.speed*0.01)*r.rad*0.85;
    r.g.rotation.y=Math.atan2(-hz,hx);
    r.g.rotation.z=Math.sin(t*0.8+r.phase)*0.04;
    r.tail.rotation.y=Math.sin(t*3.2+r.phase)*0.55;
    r.body.rotation.y=Math.sin(t*1.6+r.phase)*0.08;
  });
  /* --- ray leap --- */
  if(S.jump){
    const j=S.jump; j.t+=wdt/j.dur; const u=Math.min(j.t,1);
    const x=j.start.x+j.h.x*16*u, z=j.start.z+j.h.z*16*u;
    const y=j.start.y + 11*Math.sin(Math.PI*u) + u*1.5;
    j.r.g.position.set(x,y,z);
    j.r.g.rotation.y=Math.atan2(-j.h.z,j.h.x);
    j.r.g.rotation.z=Math.sin(Math.PI*u)*1.25;
    j.r.tail.rotation.y=Math.sin(t*6)*0.3;
    if(j.t>=1){ // splash!
      const sy=surfY;
      // ripples
      for(let i=0,n=0;i<ripples.length&&n<2;i++){ if(ripples[i].t>=1){ ripples[i].m.position.set(x,sy+0.05,z);
        ripples[i].m.visible=true; ripples[i].t=0; n++; } }
      // droplets
      for(let i=0,n=0;i<DROP_N&&n<14;i++){ if(dropData[i].life<=0){
        dropData[i].life=1; dropData[i].p.set(x,sy,z);
        dropData[i].v.set((Math.random()-0.5)*5, 4+Math.random()*5, (Math.random()-0.5)*5); n++; } }
      j.r.depth=-4.5; j.r.angle=Math.atan2(z,x); S.jump=null;
    }
  }
  /* --- ripples --- */
  ripples.forEach(r=>{ if(r.t<1){ r.t+=dt/1.8; const s=1+r.t*8;
    r.m.scale.set(s,s,s); r.m.material.opacity=0.55*(1-r.t);
    if(r.t>=1){r.visible=false;r.m.material.opacity=0;} } });
  /* --- droplets --- */
  for(let i=0;i<DROP_N;i++){ const d=dropData[i];
    if(d.life>0){ d.life-=dt; d.v.y-=9.5*dt; d.p.addScaledVector(d.v,dt); }
    dummy.position.copy(d.p); dummy.scale.setScalar(d.life>0?Math.min(d.life*2,1):0.001);
    dummy.updateMatrix(); drops.setMatrixAt(i,dummy.matrix);
  } drops.instanceMatrix.needsUpdate=true;

  /* --- fish --- */
  for(let i=0;i<FISH_N;i++){ const f=fishData[i];
    f.a+=f.s*wdt*(1+S.wind*0.3);
    const x=Math.cos(f.a)*f.r*1.2, z=Math.sin(f.a)*f.r*0.85,
          y=f.y+Math.sin(t*0.9+f.ph)*0.8;
    const nx=Math.cos(f.a+f.s*0.05)*f.r*1.2, nz=Math.sin(f.a+f.s*0.05)*f.r*0.85;
    dummy.position.set(x,y,z); dummy.rotation.set(0,Math.atan2(-(nz-z),(nx-x)),Math.sin(t*2+f.ph)*0.1);
    dummy.scale.setScalar(f.sc); dummy.updateMatrix(); fish.setMatrixAt(i,dummy.matrix);
  } fish.instanceMatrix.needsUpdate=true;

  /* --- bubbles --- */
  for(let i=0;i<BUB_N;i++){ const b=bubData[i];
    if(b.y>=surfY-0.3 || b.sp===0){ const e=BUB_EMIT[i%BUB_EMIT.length];
      b.x=e[0]+(Math.random()-0.5)*3; b.y=e[1]+Math.random(); b.z=e[2]+(Math.random()-0.5)*3; b.sp=0.8+Math.random()*1.4; }
    b.y+=b.sp*wdt;
    dummy.position.set(b.x+Math.sin(t*3+b.ph)*0.15, b.y, b.z+Math.cos(t*2.4+b.ph)*0.15);
    dummy.scale.setScalar(0.5+ (b.y-SEABED)/(surfY-SEABED) *0.9);
    dummy.updateMatrix(); bubbles.setMatrixAt(i,dummy.matrix);
  } bubbles.instanceMatrix.needsUpdate=true;

  /* --- camera transition --- */
  if(camAnim){
    camAnim.t+=dt/1.2; const e=ease(Math.min(camAnim.t,1));
    camera.position.lerpVectors(camAnim.from,camAnim.to,e);
    controls.target.lerpVectors(camAnim.fromT,camAnim.toT,e);
    if(camAnim.t>=1) camAnim=null;
  }
  controls.update();
  renderer.render(scene,camera);
}
animate();

/* ---------- resize ---------- */
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
renderer.setSize(innerWidth,innerHeight);
</script>
</body>
</html>
```

## Highlights

**Cutaway water system** — Four depth-sorted layers (`renderOrder` + `depthWrite:false`) eliminate transparency flicker: a wave-displaced surface shader with shore foam & sparkle, tide-clipped cutaway walls with a meniscus line, a backside tint volume for underwater haze, and a caustic-shaded seabed.

**Living details** — Undulating rays (tail/body sine chains), a 42-fish instanced school, swaying instanced grass & seagrass via `onBeforeCompile` injection, rising bubbles, splash droplets on ballistic arcs, and expanding ripple rings.

**Tide & wind** — The slider moves the surface, tint volume, wall clipping uniform, shoreline foam radius, and all floating objects (kayak, buoys) simultaneously; wind drives wave amplitude, sway strength, and the procedural breeze volume.

**Day cycle** — All light colors, fog, sky, and star opacity lerp exponentially; lanterns, cabin windows, and point lights fade in at dusk.

**Audio** — A drifting three-oscillator pad with pentatonic plucks, band-passed noise breeze, and LFO-modulated water noise — all starting only after your first interaction.