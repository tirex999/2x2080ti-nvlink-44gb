

Here's the complete project in a single `index.html`. Save it, open it in any modern browser (it pulls Three.js and fonts from CDNs), and the four hamsters start wandering, eating, napping, and taking turns on the wheel immediately.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#3a2a1c; --paper:#fffaf0; --sun:#ffc94d; --coral:#ff8a7a;
    --mint:#57cfc0; --blush:#ffd9c4;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;font-family:Nunito,sans-serif;color:var(--ink)}

  /* layered warm backdrop */
  #bg{position:fixed;inset:0;z-index:0;background:
    radial-gradient(1200px 700px at 50% 10%, #fff8e6 0%, rgba(255,248,230,0) 60%),
    linear-gradient(180deg,#ffeccb 0%,#ffdcb4 45%,#ffcda6 100%);}
  #bg::before{content:"";position:absolute;inset:0;opacity:.35;
    background-image:radial-gradient(rgba(255,255,255,.6) 1.6px,transparent 1.7px);
    background-size:30px 30px;
    -webkit-mask-image:linear-gradient(180deg,#000,transparent 75%);
            mask-image:linear-gradient(180deg,#000,transparent 75%);}
  #bg::after{content:"";position:absolute;inset:0;
    background:radial-gradient(120% 95% at 50% 40%,transparent 55%,rgba(140,70,20,.22) 100%);}

  #scene{position:fixed;inset:0;z-index:1;display:block;cursor:grab;touch-action:none}
  #scene.grabbing{cursor:grabbing}

  /* sticker-style cards */
  .card{position:fixed;z-index:3;background:var(--paper);border:3px solid var(--ink);
    border-radius:18px;box-shadow:6px 7px 0 rgba(58,42,28,.85);padding:14px 18px;
    transform:rotate(var(--rot,0deg));
    animation:pop .55s cubic-bezier(.34,1.56,.64,1) backwards;}
  @keyframes pop{from{opacity:0;transform:translateY(16px) scale(.9) rotate(var(--rot,0deg))}
                 to{opacity:1;transform:translateY(0) scale(1) rotate(var(--rot,0deg))}}

  .hud-title{--rot:-1.4deg;top:18px;left:18px;max-width:min(330px,72vw);animation-delay:.1s}
  .badge{display:inline-block;font:800 10.5px Nunito;letter-spacing:1.6px;text-transform:uppercase;
    background:var(--sun);border:2px solid var(--ink);border-radius:999px;padding:3px 10px;
    margin-bottom:8px;transform:rotate(-2deg)}
  h1{font-family:Fredoka;font-weight:700;font-size:clamp(24px,3.4vw,34px);line-height:1.02;
    margin:0 0 4px;letter-spacing:.3px}
  .sub{margin:0;font:700 13px Nunito;color:#9a7350}
  .status{margin-top:10px;display:flex;align-items:center;gap:8px;font:800 13.5px Nunito;
    background:#fff3e0;border:2px dashed #e5c39a;border-radius:10px;padding:6px 10px}
  .pulse{width:9px;height:9px;border-radius:50%;background:var(--mint);flex:none;animation:pulse 1.5s infinite}
  @keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.7);opacity:.45}}

  .hud-roster{--rot:1.2deg;top:18px;right:18px;animation-delay:.2s}
  .hud-roster h2{margin:0;font:600 12px Fredoka;letter-spacing:2.5px;text-transform:uppercase;color:#a07c54}
  #roster{display:flex;flex-direction:column;gap:4px;margin-top:8px}
  .crew{display:flex;align-items:center;gap:9px;padding:6px 10px;border-radius:12px;
    border:2px solid transparent;background:transparent;font:800 14px Nunito;color:var(--ink);
    cursor:pointer;transition:all .15s;text-align:left}
  .crew:hover{background:#ffefdb;transform:translateX(3px)}
  .crew.on{background:var(--sun);border-color:var(--ink);box-shadow:2px 3px 0 rgba(58,42,28,.85)}
  .dot{width:15px;height:15px;border-radius:50%;border:2px solid var(--ink);flex:none}

  .hud-controls{position:fixed;z-index:3;left:50%;bottom:20px;transform:translateX(-50%);
    display:flex;gap:12px;animation:pop .55s cubic-bezier(.34,1.56,.64,1) .3s backwards}
  .ctrl{font-family:Fredoka;font-weight:600;font-size:15px;color:var(--ink);background:var(--paper);
    border:3px solid var(--ink);border-radius:14px;padding:10px 18px;cursor:pointer;
    box-shadow:0 5px 0 var(--ink);transition:transform .12s,box-shadow .12s,background .12s;
    display:inline-flex;align-items:center;gap:8px}
  .ctrl:hover{transform:translateY(-2px);box-shadow:0 7px 0 var(--ink)}
  .ctrl:active{transform:translateY(3px);box-shadow:0 2px 0 var(--ink)}
  .ctrl.feed{background:var(--sun)}
  .ctrl .dot{width:10px;height:10px;background:var(--mint)}
  .ctrl.off .dot{background:#e8d3b3}

  .hud-hint{position:fixed;z-index:3;bottom:24px;right:22px;font:700 12px Nunito;
    color:rgba(58,42,28,.55);animation:pop .5s ease .45s backwards}

  #bubble{position:fixed;z-index:4;pointer-events:none;transform:translate(-50%,-115%);
    background:var(--paper);border:2.5px solid var(--ink);border-radius:12px;padding:7px 12px;
    font:800 13px Nunito;color:var(--ink);box-shadow:3px 4px 0 rgba(58,42,28,.5);
    opacity:0;transition:opacity .18s;white-space:nowrap}
  #bubble b{color:var(--coral)}
  #bubble::after{content:"";position:absolute;left:50%;top:100%;transform:translateX(-50%);
    border:7px solid transparent;border-top-color:var(--ink)}

  #loader{position:fixed;inset:0;z-index:6;display:grid;place-items:center;
    background:linear-gradient(180deg,#ffeccb,#ffcda6);transition:opacity .5s}
  #loader.done{opacity:0;pointer-events:none}
  #loader .box{text-align:center}
  #loader .emoji{font-size:56px;display:inline-block;animation:bounce 1s infinite}
  @keyframes bounce{0%,100%{transform:translateY(0) rotate(-8deg)}50%{transform:translateY(-16px) rotate(8deg)}}
  #loader p{font:600 16px Fredoka;margin:10px 0 0}

  @media(max-width:760px){
    .hud-title{top:12px;left:12px;padding:10px 14px;max-width:56vw}
    .sub{display:none}
    .hud-roster{top:12px;right:12px;padding:10px 12px}
    .crew{font-size:12px;padding:4px 8px}
    .hud-hint{display:none}
    .hud-controls{bottom:14px;width:calc(100% - 24px);justify-content:center;flex-wrap:wrap}
    .ctrl{padding:8px 12px;font-size:13px}
  }
</style>
<script type="importmap">
  { "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js" } }
</script>
</head>
<body>
  <div id="bg"></div>
  <canvas id="scene"></canvas>

  <header class="card hud-title">
    <span class="badge">Low-Poly · Three.js</span>
    <h1>Hamster Playground</h1>
    <p class="sub">four tiny friends, one very busy wheel</p>
    <div class="status"><span class="pulse"></span><span id="statusTxt">warming up…</span></div>
  </header>

  <nav class="card hud-roster">
    <h2>The Crew</h2>
    <div id="roster"></div>
  </nav>

  <div class="hud-controls">
    <button class="ctrl feed" id="feedBtn">🌻 Feed</button>
    <button class="ctrl" id="pauseBtn">⏸ Pause</button>
    <button class="ctrl" id="autoBtn"><span class="dot"></span>Auto-orbit</button>
  </div>

  <div class="hud-hint">drag to orbit · scroll to zoom · click a hamster · tap the wheel</div>
  <div id="bubble"></div>
  <div id="loader"><div class="box"><span class="emoji">🐹</span><p>warming up the wheel…</p></div></div>
  <noscript><div style="position:fixed;inset:0;z-index:9;display:grid;place-items:center">This playground needs JavaScript.</div></noscript>

<script type="module">
import * as THREE from 'three';

/* ============================== helpers ============================== */
const rand  = (a,b)=>a+Math.random()*(b-a);
const pick  = a=>a[Math.floor(Math.random()*a.length)];
const lerp  = (a,b,t)=>a+(b-a)*t;
const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
const easeInOut = t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
function lerpAngle(a,b,t){let d=(b-a)%(Math.PI*2);if(d>Math.PI)d-=Math.PI*2;if(d<-Math.PI)d+=Math.PI*2;return a+d*t;}

/* ============================== renderer ============================= */
const canvas   = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.setClearColor(0x000000,0);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xffe0b8, 16, 34);

const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 100);

/* lights */
scene.add(new THREE.HemisphereLight(0xfff6e0, 0xffc9a0, 1.0));
const sun = new THREE.DirectionalLight(0xfff2d0, 1.7);
sun.position.set(6,9,4);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
Object.assign(sun.shadow.camera,{left:-7,right:7,top:7,bottom:-7,near:2,far:25});
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
scene.add(sun);
const fill = new THREE.DirectionalLight(0xffd9e8, 0.45);
fill.position.set(-6,4,-5);
scene.add(fill);

/* material + mesh helpers (cached, flat-shaded = low-poly look) */
const MAT = {};
function mat(color, extra={}){
  const k = color + JSON.stringify(extra);
  if(MAT[k]) return MAT[k];
  MAT[k] = new THREE.MeshStandardMaterial(Object.assign({color, flatShading:true, roughness:.95, metalness:0}, extra));
  return MAT[k];
}
function mesh(geo, m, x=0,y=0,z=0, o={}){
  const ms = new THREE.Mesh(geo,m);
  ms.position.set(x,y,z);
  ms.rotation.set(o.rx||0, o.ry||0, o.rz||0);
  if(o.sx!==undefined) ms.scale.set(o.sx, o.sy||o.sx, o.sz||o.sx);
  ms.castShadow = o.shadow!==false;
  ms.receiveShadow = true;
  (o.parent||scene).add(ms);
  return ms;
}

/* ============================== the cage ============================= */
const C = {
  sand:0xf6d7a3, tray:0xff9db8, trayDark:0xf77fa5, wood:0xd9a05b,
  wheelRim:0xffd23f, wheelSpoke:0xfff3d6, wheelHub:0xff9f1c,
  house:0x79c2ff, roof:0xff6b6b, door:0x5a3e2b,
  tunnel:0x57cfc0, bowl:0xffa94d, bowlIn:0x8a5a2b, pellet:0xd9a441
};

/* ground + rug */
mesh(new THREE.CircleGeometry(18,48), mat(0xf6c98e), 0,0,0, {rx:-Math.PI/2, shadow:false});
mesh(new THREE.CircleGeometry(5,40),  mat(0xf0b878), 0,.005,0, {rx:-Math.PI/2, shadow:false});

/* tray + sand */
mesh(new THREE.CylinderGeometry(3.6,3.85,0.6,12),  mat(C.tray), 0,0.3,0);
mesh(new THREE.CylinderGeometry(3.35,3.35,0.42,12), mat(C.sand), 0,0.395,0);

/* bars + rings */
const barGeo = new THREE.CylinderGeometry(0.045,0.045,2.7,6);
for(let i=0;i<18;i++){
  const a = i/18*Math.PI*2;
  mesh(barGeo, mat(C.wood), Math.sin(a)*3.5, 1.9, Math.cos(a)*3.5);
}
const ringGeo = new THREE.TorusGeometry(3.5,0.07,8,40);
mesh(ringGeo, mat(C.wood), 0,0.62,0, {rx:Math.PI/2});
mesh(ringGeo, mat(C.wood), 0,3.2,0,  {rx:Math.PI/2});
mesh(new THREE.TorusGeometry(3.5,0.09,8,40), mat(C.trayDark), 0,3.2,0, {rx:Math.PI/2});

/* ============================== props ================================ */
const GROUND_Y = 0.605;

/* --- exercise wheel (the star) --- */
const wheelG = new THREE.Group(); wheelG.position.set(0,0,-2.05); scene.add(wheelG);
mesh(new THREE.BoxGeometry(1.7,0.14,0.8), mat(C.wood), 0,0.67,0, {parent:wheelG});
mesh(new THREE.CylinderGeometry(0.07,0.09,1.15,6), mat(C.wood),  0.6,1.175,0, {parent:wheelG});
mesh(new THREE.CylinderGeometry(0.07,0.09,1.15,6), mat(C.wood), -0.6,1.175,0, {parent:wheelG});
mesh(new THREE.CylinderGeometry(0.05,0.05,1.35,6), mat(0x9aa5b1,{metalness:.6,roughness:.4}), 0,1.75,0, {rz:Math.PI/2, parent:wheelG});

const WHEEL_CY = 1.75, WHEEL_R = 0.8;
const wheelSpin = new THREE.Group(); wheelSpin.position.set(0,WHEEL_CY,0); wheelG.add(wheelSpin);
const wheelHits = [];
const rim = mesh(new THREE.TorusGeometry(WHEEL_R,0.09,8,26), mat(C.wheelRim), 0,0,0, {ry:Math.PI/2, parent:wheelSpin});
rim.userData.wheel = true; wheelHits.push(rim);
mesh(new THREE.CylinderGeometry(0.13,0.13,0.16,8), mat(C.wheelHub), 0,0,0, {rz:Math.PI/2, parent:wheelSpin});
const spokeGeo = new THREE.CylinderGeometry(0.028,0.028,WHEEL_R*0.97,5);
for(let k=0;k<8;k++){
  const a = k/8*Math.PI*2;
  const s = mesh(spokeGeo, mat(C.wheelSpoke), 0, Math.cos(a)*0.4, Math.sin(a)*0.4, {rx:a, parent:wheelSpin});
  s.userData.wheel = true; wheelHits.push(s);
}
const wheelAnchor = new THREE.Object3D(); wheelAnchor.position.set(0,2.75,-2.05); scene.add(wheelAnchor);
const WHEEL_RUN   = new THREE.Vector3(0, WHEEL_CY-(WHEEL_R-0.09), -2.05);
const WHEEL_ENTRY = new THREE.Vector3(0, GROUND_Y, -1.15);

/* --- food bowl --- */
const BOWL_POS = new THREE.Vector3(1.9,0,-1.4);
const BOWL_SPOT = BOWL_POS.clone().add(BOWL_POS.clone().negate().normalize().multiplyScalar(0.62));
mesh(new THREE.CylinderGeometry(0.42,0.3,0.16,10), mat(C.bowl), 1.9,0.68,-1.4);
mesh(new THREE.TorusGeometry(0.42,0.05,6,16), mat(0xff8f2b), 1.9,0.76,-1.4, {rx:Math.PI/2});
mesh(new THREE.CircleGeometry(0.36,12), mat(C.bowlIn), 1.9,0.765,-1.4, {rx:-Math.PI/2});
for(let i=0;i<4;i++){
  const a=rand(0,6.28), r=rand(0,0.2);
  mesh(new THREE.DodecahedronGeometry(0.06,0), mat(C.pellet), 1.9+Math.cos(a)*r, 0.8, -1.4+Math.sin(a)*r);
}

/* --- house --- */
const HOUSE_POS = new THREE.Vector3(-2.05,0,1.25);
const SLEEP_SPOT = HOUSE_POS.clone().add(HOUSE_POS.clone().negate().normalize().multiplyScalar(1.05));
const houseG = new THREE.Group(); houseG.position.copy(HOUSE_POS);
houseG.rotation.y = Math.atan2(-HOUSE_POS.x, -HOUSE_POS.z); scene.add(houseG);
mesh(new THREE.BoxGeometry(1.15,0.9,1.05), mat(C.house), 0,1.05,0, {parent:houseG});
mesh(new THREE.ConeGeometry(0.98,0.62,4),  mat(C.roof),  0,1.81,0, {ry:Math.PI/4, parent:houseG});
mesh(new THREE.CircleGeometry(0.27,14),    mat(C.door),  0,0.92,0.531, {parent:houseG});
mesh(new THREE.CircleGeometry(0.1,10),     mat(0xfff3d6),0.576,1.25,0.15, {ry:Math.PI/2, parent:houseG});

/* --- tunnel (open arch — hamsters stroll under it) --- */
const tunG = new THREE.Group(); tunG.position.set(0.35,0,2.15); scene.add(tunG);
const tunMat = mat(C.tunnel,{side:THREE.DoubleSide});
mesh(new THREE.CylinderGeometry(0.55,0.55,1.7,10,1,true,0,Math.PI), tunMat, 0,1.15,0, {rz:Math.PI/2, parent:tunG, shadow:false});
for(const sx of [-0.85,0.85])
  mesh(new THREE.TorusGeometry(0.55,0.05,6,12,Math.PI), tunMat, sx,1.15,0, {ry:Math.PI/2, parent:tunG});

/* --- water bottle, hay, pebbles, shavings --- */
mesh(new THREE.CylinderGeometry(0.05,0.05,0.9,6),  mat(0x9aa5b1), 2.55,1.05,-0.75);
mesh(new THREE.CylinderGeometry(0.2,0.24,0.55,8),  mat(0xbde0fe,{transparent:true,opacity:.8}), 2.55,1.5,-0.75);
mesh(new THREE.CylinderGeometry(0.09,0.09,0.14,8), mat(0x9aa5b1), 2.55,1.16,-0.75);
mesh(new THREE.IcosahedronGeometry(0.5,0), mat(0xe8c56a), -1.55,0.72,-1.75, {sx:1.2,sy:0.5,sz:1});
for(let i=0;i<4;i++)
  mesh(new THREE.CylinderGeometry(0.018,0.018,0.4,4), mat(C.pellet),
       -1.55+rand(-0.25,0.25), 0.95, -1.75+rand(-0.25,0.25), {rx:rand(-0.5,0.5), rz:rand(-0.5,0.5)});
for(let i=0;i<6;i++){
  const a=rand(0,6.28), r=rand(1.2,2.9);
  mesh(new THREE.DodecahedronGeometry(rand(0.07,0.13),0), mat(i%2?0xd8b48c:0xc9a06a), Math.cos(a)*r, 0.63, Math.sin(a)*r);
}
for(let i=0;i<7;i++){
  const a=rand(0,6.28), r=rand(0.8,2.8);
  mesh(new THREE.CylinderGeometry(0.018,0.018,rand(0.22,0.34),4), mat(0xf3ddb0),
       Math.cos(a)*r, 0.615, Math.sin(a)*r, {rx:Math.PI/2, rz:rand(0,6.28)});
}

/* --- drifting clouds (ambient life in the background) --- */
const clouds = [];
const cloudMat = new THREE.MeshStandardMaterial({color:0xffffff, flatShading:true, roughness:1, transparent:true, opacity:.92});
function makeCloud(x,y,z,s){
  const g = new THREE.Group();
  for(let i=0;i<3;i++){
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(rand(0.5,0.9),0), cloudMat);
    m.position.set(i*0.7-0.7+rand(-0.15,0.15), rand(-0.1,0.15), rand(-0.2,0.2));
    m.scale.y = 0.6; g.add(m);
  }
  g.position.set(x,y,z); g.scale.setScalar(s); scene.add(g);
  clouds.push({mesh:g, speed:rand(0.15,0.35)});
}
makeCloud(-8,6.5,-11,1.6); makeCloud(3,7.5,-13,2.2); makeCloud(9,6,-9,1.3);

/* ============================== hamsters ============================= */
const DEFS = [
  {name:'Mochi',   body:0xfff1dd, belly:0xffffff},
  {name:'Biscuit', body:0xf6a85c, belly:0xffe8c9},
  {name:'Peanut',  body:0xb07b4f, belly:0xe8c9a0},
  {name:'Clover',  body:0xaab3c9, belly:0xf0f3fa},
];
const hamsters = [], hamsterHits = [];

function makeHamster(def, x, z){
  const g = new THREE.Group(); g.position.set(x, GROUND_Y, z); g.rotation.y = rand(0,6.28); scene.add(g);
  const bodyMat = mat(def.body), bellyMat = mat(def.belly),
        pinkMat = mat(0xffb3c1), noseMat = mat(0xff8fa3),
        eyeMat = mat(0x2f2a26), glintMat = mat(0xffffff,{roughness:.4});

  const body  = new THREE.Mesh(new THREE.SphereGeometry(0.42,8,6), bodyMat);
  body.scale.set(1,0.92,1.12); body.position.y = 0.34;
  const snout = new THREE.Mesh(new THREE.SphereGeometry(0.24,7,5), bodyMat);
  snout.position.set(0,0.4,0.36); snout.scale.set(0.95,0.8,0.9);
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.3,7,5), bellyMat);
  belly.position.set(0,0.22,0.3); belly.scale.set(0.8,0.7,0.85);
  const nose  = new THREE.Mesh(new THREE.SphereGeometry(0.045,6,4), noseMat);
  nose.position.set(0,0.44,0.58);
  const eyeL  = new THREE.Mesh(new THREE.SphereGeometry(0.05,6,4), eyeMat);
  eyeL.position.set(0.13,0.47,0.52);
  const eyeR  = eyeL.clone(); eyeR.position.x = -0.13;
  const glintL = new THREE.Mesh(new THREE.SphereGeometry(0.017,4,3), glintMat);
  glintL.position.set(0.145,0.49,0.56);
  const glintR = glintL.clone(); glintR.position.x = -0.145;
  const earL  = new THREE.Mesh(new THREE.SphereGeometry(0.1,6,4), bodyMat);
  earL.position.set(0.2,0.7,0.02); earL.scale.set(1,0.75,0.85);
  const earR  = earL.clone(); earR.position.x = -0.2;
  const earIL = new THREE.Mesh(new THREE.SphereGeometry(0.05,5,3), pinkMat);
  earIL.position.set(0.21,0.72,0.07);
  const earIR = earIL.clone(); earIR.position.x = -0.21;
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.09,6,4), pinkMat);
  cheekL.position.set(0.21,0.36,0.42);
  const cheekR = cheekL.clone(); cheekR.position.x = -0.21;
  const tail  = new THREE.Mesh(new THREE.SphereGeometry(0.06,5,4), bodyMat);
  tail.position.set(0,0.3,-0.52);
  g.add(body,snout,belly,nose,eyeL,eyeR,glintL,glintR,earL,earR,earIL,earIR,cheekL,cheekR,tail);

  const legs = [];
  const legGeo = new THREE.CapsuleGeometry(0.055,0.13,2,6);
  [[0.17,0.28],[-0.17,0.28],[0.2,-0.28],[-0.2,-0.28]].forEach(([lx,lz])=>{
    const lg = new THREE.Group(); lg.position.set(lx,0.22,lz);
    const lm = new THREE.Mesh(legGeo, bodyMat); lm.position.y = -0.12;
    lg.add(lm); g.add(lg); legs.push(lg);
  });
  g.traverse(o=>{ if(o.isMesh){ o.castShadow=true; o.receiveShadow=true; } });

  const anchor = new THREE.Object3D(); anchor.position.set(0,1.05,0); g.add(anchor);

  const h = {
    def, group:g, anchor, legs,
    parts:{body,snout,eyeL,eyeR,earL,earR,cheekL,cheekR,tail},
    state:'wander', stateT:0, phase:'',
    target:new THREE.Vector3(), spot:new THREE.Vector3(), face:new THREE.Vector3(),
    speed:rand(0.85,1.3), seed:Math.random()*10, legPhase:Math.random()*6, moving:false,
    blinkIn:rand(1,4), blink:0, cheek:0, cheekTarget:0,
    hopT:1, flickT:0, chewT:0, k:0, runT:0, pauseYaw:0,
    pellet:null, wheel:false
  };
  [body,snout,belly].forEach(m=>{ m.userData.h=h; hamsterHits.push(m); });
  return h;
}
const STARTS = [[-0.8,0.5],[1.0,0.8],[-0.4,-0.6],[0.9,-0.4]];
DEFS.forEach((d,i)=>hamsters.push(makeHamster(d, STARTS[i][0], STARTS[i][1])));

/* ============================== behavior ============================= */
const ZONES = [
  {x:0,     z:-2.05, r:1.15},  // wheel
  {x:-2.05, z:1.25,  r:1.15},  // house
  {x:1.9,   z:-1.4,  r:0.75},  // bowl
  {x:0.35,  z:2.15,  r:1.2},   // tunnel
  {x:-1.55, z:-1.75, r:0.7},   // hay
];
function randomOpenPoint(){
  for(let i=0;i<12;i++){
    const a=Math.random()*Math.PI*2, r=Math.sqrt(Math.random())*2.7;
    const x=Math.cos(a)*r, z=Math.sin(a)*r;
    if(ZONES.every(z=>Math.hypot(x-z.x,z-z.z)>z.r)) return new THREE.Vector3(x,0,z);
  }
  return new THREE.Vector3(rand(-1,1),0,rand(-1,1));
}

let wheelBusy = false;
function startWander(h){ h.state='wander'; h.target=randomOpenPoint(); h.stateT=rand(4,9); h.cheekTarget=0; }
function startPause(h){ h.state='pause'; h.stateT=rand(1.2,3.2); h.pauseYaw=h.group.rotation.y+rand(-1.4,1.4); h.cheekTarget=0; }
function startEat(h, pellet){
  h.state='eat'; h.phase='go'; h.pellet=pellet; h.stateT=8;
  if(pellet){
    h.spot.copy(pellet.pos); h.spot.x+=rand(-0.18,0.18); h.spot.z+=rand(-0.18,0.18);
    h.face.copy(pellet.pos);
  } else { h.spot.copy(BOWL_SPOT); h.face.copy(BOWL_POS); }
}
function startWheel(h){
  if(wheelBusy) return false;
  wheelBusy=true; h.wheel=true; h.state='wheel'; h.phase='go'; h.stateT=10;
  return true;
}
function startSleep(h){ h.state='sleep'; h.phase='go'; h.spot.copy(SLEEP_SPOT); h.stateT=8; }

function nearestPellet(h){
  let best=null, bd=1e9;
  for(const p of pellets){ const d=h.group.position.distanceTo(p.pos); if(d<bd){bd=d;best=p;} }
  return best;
}
function chooseNext(h){
  if(pellets.length && Math.random()<0.4){
    const p = nearestPellet(h);
    if(p){ startEat(h,p); return; }
  }
  const r = Math.random();
  if(r<0.32)      startPause(h);
  else if(r<0.54) startWander(h);
  else if(r<0.72) startEat(h,null);
  else if(r<0.88) { if(!startWheel(h)) startSleep(h); }
  else if(r<0.95) startSleep(h);
  else            startWander(h);
}

function moveToward(h, target, speed, dt){
  const p = h.group.position;
  const dx = target.x-p.x, dz = target.z-p.z;
  const d = Math.hypot(dx,dz);
  if(d < 0.14) return true;
  const step = Math.min(d, speed*dt);
  p.x += dx/d*step; p.z += dz/d*step;
  h.group.rotation.y = lerpAngle(h.group.rotation.y, Math.atan2(dx,dz), Math.min(1,dt*7));
  h.moving = true;
  h.legPhase += dt*speed*10;
  return false;
}

function updateHamster(h, dt, t){
  h.moving = false;
  h.blinkIn -= dt;
  if(h.blinkIn<=0){ h.blink=0.13; h.blinkIn=rand(2,5); }
  if(h.blink>0) h.blink -= dt;
  if(h.flickT>0) h.flickT -= dt; else if(Math.random()<dt*0.25) h.flickT=0.35;
  if(h.hopT<1) h.hopT = Math.min(1, h.hopT+dt/0.5);
  h.cheek = lerp(h.cheek, h.cheekTarget, Math.min(1,dt*6));

  switch(h.state){
    case 'wander':
      h.stateT -= dt;
      if(moveToward(h,h.target,h.speed,dt) || h.stateT<=0) chooseNext(h);
      break;

    case 'pause':
      h.stateT -= dt;
      h.group.rotation.y = lerpAngle(h.group.rotation.y, h.pauseYaw, Math.min(1,dt*3));
      if(h.stateT<=0) startWander(h);
      break;

    case 'eat':
      h.stateT -= dt;
      if(h.phase==='go'){
        if(moveToward(h,h.spot,h.speed*1.15,dt)){ h.phase='chew'; h.stateT=rand(2.2,4.5); h.cheekTarget=1; h.chewT=0; }
        else if(h.stateT<=0) startWander(h);
      } else {
        h.chewT += dt;
        h.group.rotation.y = lerpAngle(h.group.rotation.y,
          Math.atan2(h.face.x-h.group.position.x, h.face.z-h.group.position.z), Math.min(1,dt*6));
        if(h.stateT<=0){
          if(h.pellet){ h.pellet.eaten=true; h.pellet=null; }
          h.cheekTarget = 0;
          startWander(h);
        }
      }
      break;

    case 'wheel':
      h.stateT -= dt;
      if(h.phase==='go'){
        if(moveToward(h,WHEEL_ENTRY,h.speed*1.1,dt)){ h.phase='climb'; h.k=0; }
        else if(h.stateT<=0){ wheelBusy=false; h.wheel=false; startWander(h); }
      }
      else if(h.phase==='climb'){
        h.k = Math.min(1, h.k+dt/0.9);
        const e = easeInOut(h.k);
        h.group.position.lerpVectors(WHEEL_ENTRY, WHEEL_RUN, e);
        h.group.position.y = lerp(WHEEL_ENTRY.y, WHEEL_RUN.y, e) + Math.sin(e*Math.PI)*0.32;
        h.group.rotation.y = lerpAngle(h.group.rotation.y, 0, Math.min(1,dt*6));
        h.group.rotation.x = lerp(h.group.rotation.x, 0.3, e);
        if(h.k>=1){ h.phase='run'; h.stateT=rand(3.5,6.5); h.runT=0; }
      }
      else if(h.phase==='run'){
        h.runT += dt; h.legPhase += dt*15;
        h.group.position.y = WHEEL_RUN.y + Math.abs(Math.sin(h.runT*15))*0.035;
        h.group.rotation.x = 0.3 + Math.sin(h.runT*15)*0.04;
        if(h.stateT<=0){ h.phase='leave'; h.k=0; }
      }
      else if(h.phase==='leave'){
        h.k = Math.min(1, h.k+dt/0.9);
        const e = easeInOut(h.k);
        h.group.position.lerpVectors(WHEEL_RUN, WHEEL_ENTRY, e);
        h.group.position.y = lerp(WHEEL_RUN.y, WHEEL_ENTRY.y, e) + Math.sin(e*Math.PI)*0.32;
        h.group.rotation.x = lerp(0.3, 0, e);
        if(h.k>=1){ wheelBusy=false; h.wheel=false; startWander(h); }
      }
      break;

    case 'sleep':
      h.stateT -= dt;
      if(h.phase==='go'){
        if(moveToward(h,h.spot,h.speed*0.8,dt)){ h.phase='rest'; h.stateT=rand(4,8); }
        else if(h.stateT<=0) startWander(h);
      } else {
        h.group.rotation.y = lerpAngle(h.group.rotation.y,
          Math.atan2(HOUSE_POS.x-h.group.position.x, HOUSE_POS.z-h.group.position.z), Math.min(1,dt*4));
        if(h.stateT<=0) startWander(h);
      }
      break;
  }

  /* ---- living details: legs, blinking, ears, cheeks, tail ---- */
  const p = h.parts;
  let swing;
  if(h.state==='wheel' && h.phase==='run') swing = Math.sin(h.legPhase)*0.95;
  else if(h.moving)                         swing = Math.sin(h.legPhase)*0.6;
  else                                      swing = Math.sin(t*2.2+h.seed)*0.05;
  h.legs[0].rotation.x =  swing;
  h.legs[1].rotation.x = -swing;
  h.legs[2].rotation.x = -swing*0.85;
  h.legs[3].rotation.x =  swing*0.85;

  const es = h.blink>0 ? 0.15 : 1;
  p.eyeL.scale.y = es; p.eyeR.scale.y = es;
  const fl = h.flickT>0 ? Math.sin(h.flickT*22)*0.35 : 0;
  p.earL.rotation.z =  0.12 + Math.sin(t*3+h.seed)*0.05 + fl;
  p.earR.rotation.z = -0.12 - Math.sin(t*3+h.seed)*0.05 - fl;
  const cs = 1 + h.cheek*0.85;
  p.cheekL.scale.setScalar(cs); p.cheekR.scale.setScalar(cs);
  p.tail.rotation.y = Math.sin(t*4+h.seed)*0.25;
  p.snout.rotation.y = h.state==='pause'
    ? Math.sin(t*6+h.seed)*0.18
    : lerp(p.snout.rotation.y, 0, Math.min(1,dt*6));

  const waddle = (h.state==='pause') ? Math.sin(t*9+h.seed)*0.05 : 0;
  h.group.rotation.z = lerp(h.group.rotation.z, waddle, Math.min(1,dt*8));

  if(h.state!=='wheel'){
    let nod = 0;
    if(h.state==='eat' && h.phase==='chew') nod = Math.sin(h.chewT*11)*0.12;
    h.group.rotation.x = lerp(h.group.rotation.x, nod, Math.min(1,dt*10));

    let yOff=0, sx=1, sy=1;
    if(h.moving) yOff = Math.abs(Math.sin(h.legPhase))*0.035;
    if(h.hopT<1){
      const hs = Math.sin(h.hopT*Math.PI);
      yOff += hs*0.45; sx = 1-hs*0.08; sy = 1+hs*0.14;
    } else if(h.state==='sleep' && h.phase==='rest'){
      sy = 1+Math.sin(t*1.7)*0.035; sx = 1-Math.sin(t*1.7)*0.02;
    }
    h.group.position.y = GROUND_Y + yOff;
    h.group.scale.set(sx, sy, sx);
  }
}

function separate(){
  for(let i=0;i<hamsters.length;i++) for(let j=i+1;j<hamsters.length;j++){
    const a=hamsters[i], b=hamsters[j];
    if(a.wheel||b.wheel) continue;
    const dx=b.group.position.x-a.group.position.x, dz=b.group.position.z-a.group.position.z;
    const d=Math.hypot(dx,dz);
    if(d>0.001 && d<0.8){
      const push=(0.8-d)*0.5, px=dx/d*push, pz=dz/d*push;
      a.group.position.x-=px; a.group.position.z-=pz;
      b.group.position.x+=px; b.group.position.z+=pz;
    }
  }
  for(const h of hamsters){
    if(h.wheel) continue;
    const p=h.group.position, r=Math.hypot(p.x,p.z);
    if(r>2.8){ p.x*=2.8/r; p.z*=2.8/r; }
  }
}

/* ============================== pellets ============================== */
const pellets = [];
function spawnPellet(pos, drop){
  const m = new THREE.Mesh(new THREE.DodecahedronGeometry(0.075,0), mat(C.pellet));
  m.castShadow = true;
  m.position.copy(pos);
  m.position.y = drop ? GROUND_Y+1.3 : GROUND_Y+0.06;
  scene.add(m);
  pellets.push({mesh:m, pos:m.position, vy:0, drop, eaten:false});
}
for(let i=0;i<5;i++) spawnPellet(randomOpenPoint(), false);
function updatePellets(dt){
  for(let i=pellets.length-1;i>=0;i--){
    const p = pellets[i];
    if(p.drop){
      p.vy -= 14*dt; p.pos.y += p.vy*dt;
      if(p.pos.y <= GROUND_Y+0.06){
        p.pos.y = GROUND_Y+0.06;
        if(p.vy < -2) p.vy *= -0.35; else { p.vy=0; p.drop=false; }
      }
    }
    if(p.eaten){
      p.mesh.scale.multiplyScalar(Math.max(0, 1-dt*5));
      if(p.mesh.scale.x < 0.05){ scene.remove(p.mesh); pellets.splice(i,1); }
    }
  }
}

/* ============================== camera orbit ========================= */
const cam = {
  theta:0.85, phi:1.02, r:11.5,
  tTheta:0.85, tPhi:1.02, tR:11.5,
  target:new THREE.Vector3(0,1.25,0),
  auto:true, idle:99
};
let moved=0, pinchDist=0;
const pointers = new Map();
canvas.addEventListener('contextmenu', e=>e.preventDefault());
canvas.addEventListener('pointerdown', e=>{
  canvas.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  cam.idle = 0;
  if(pointers.size===1) moved=0;
  else if(pointers.size===2){
    const p=[...pointers.values()];
    pinchDist = Math.hypot(p[0].x-p[1].x, p[0].y-p[1].y);
  }
  canvas.classList.add('grabbing');
});
canvas.addEventListener('pointermove', e=>{
  if(!pointers.has(e.pointerId)) return;
  const prev = pointers.get(e.pointerId);
  const dx = e.clientX-prev.x, dy = e.clientY-prev.y;
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  cam.idle = 0;
  if(pointers.size===1){
    moved += Math.abs(dx)+Math.abs(dy);
    cam.tTheta -= dx*0.0052;
    cam.tPhi = clamp(cam.tPhi - dy*0.0052, 0.32, 1.42);
  } else if(pointers.size===2){
    const p=[...pointers.values()];
    const d = Math.hypot(p[0].x-p[1].x, p[0].y-p[1].y);
    if(pinchDist>0) cam.tR = clamp(cam.tR*(pinchDist/d), 6, 18);
    pinchDist = d;
  }
});
function endPointer(e){
  const wasSingle = pointers.size===1;
  pointers.delete(e.pointerId);
  if(pointers.size===0){
    canvas.classList.remove('grabbing');
    if(wasSingle && moved<7) handleClick(e.clientX, e.clientY);
  }
}
canvas.addEventListener('pointerup', endPointer);
canvas.addEventListener('pointercancel', endPointer);
canvas.addEventListener('wheel', e=>{
  e.preventDefault();
  cam.tR = clamp(cam.tR*(1+e.deltaY*0.001), 6, 18);
  cam.idle = 0;
},{passive:false});

function updateOrbit(dt){
  cam.idle += dt;
  if(cam.auto && cam.idle>3.5) cam.tTheta += dt*0.1;
  const k = Math.min(1, dt*7);
  cam.theta += (cam.tTheta-cam.theta)*k;
  cam.phi   += (cam.tPhi  -cam.phi)*k;
  cam.r     += (cam.tR    -cam.r)*k;
  camera.position.set(
    cam.target.x + cam.r*Math.sin(cam.phi)*Math.sin(cam.theta),
    cam.target.y + cam.r*Math.cos(cam.phi),
    cam.target.z + cam.r*Math.sin(cam.phi)*Math.cos(cam.theta)
  );
  camera.lookAt(cam.target);
}

/* ============================== clicks & bubbles ===================== */
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), _v = new THREE.Vector3();
const SQUEAKS = ['Squeak!','Hi hi!','Seed please?','*happy wiggle*','Nom nom!','Whee!','Best cage ever'];
const bubbleEl = document.getElementById('bubble');
let bubbleData = null;
function showBubble(obj, html, dur){
  bubbleEl.innerHTML = html;
  bubbleEl.style.opacity = '1';
  bubbleData = {obj, until: performance.now()+dur*1000};
}
function updateBubble(){
  if(!bubbleData) return;
  if(performance.now() > bubbleData.until){ bubbleEl.style.opacity='0'; bubbleData=null; return; }
  _v.setFromMatrixPosition(bubbleData.obj.matrixWorld).project(camera);
  if(_v.z > 1){ bubbleEl.style.opacity='0'; return; }
  bubbleEl.style.opacity = '1';
  bubbleEl.style.left = ((_v.x*0.5+0.5)*innerWidth)+'px';
  bubbleEl.style.top  = ((-_v.y*0.5+0.5)*innerHeight)+'px';
}
function hop(h){ if(h.hopT>=1) h.hopT = 0; }
function handleClick(x,y){
  ndc.set(x/innerWidth*2-1, -(y/innerHeight)*2+1);
  ray.setFromCamera(ndc, camera);
  const hits = ray.intersectObjects(hamsterHits.concat(wheelHits), false);
  if(!hits.length) return;
  const o = hits[0].object;
  if(o.userData.h){
    const h = o.userData.h;
    hop(h);
    showBubble(h.anchor, `<b>${h.def.name}</b> ${pick(SQUEAKS)}`, 1.6);
  } else if(o.userData.wheel){
    wheelBoost = 4.5;
    showBubble(wheelAnchor, 'Push! 💨', 1.4);
  }
}

/* ============================== UI wiring ============================ */
const statusTxt = document.getElementById('statusTxt');
const feedBtn = document.getElementById('feedBtn');
const pauseBtn = document.getElementById('pauseBtn');
const autoBtn = document.getElementById('autoBtn');
const rosterEl = document.getElementById('roster');
let selected = 0, simOn = true, statusTimer = 0;

DEFS.forEach((d,i)=>{
  const b = document.createElement('button');
  b.className = 'crew';
  b.innerHTML = `<span class="dot" style="background:#${d.body.toString(16).padStart(6,'0')}"></span>${d.name}`;
  b.onclick = ()=>{
    selected = i;
    [...rosterEl.children].forEach(c=>c.classList.toggle('on', c===b));
    const h = hamsters[i];
    hop(h);
    showBubble(h.anchor, `<b>${h.def.name}</b> says hi! 👋`, 1.8);
  };
  rosterEl.appendChild(b);
});
rosterEl.children[0].classList.add('on');

feedBtn.onclick = ()=>{
  for(let i=0;i<3;i++) spawnPellet(randomOpenPoint(), true);
  hamsters.forEach(h=>{
    if((h.state==='wander'||h.state==='pause') && Math.random()<0.5){
      const p = nearestPellet(h);
      if(p) startEat(h,p);
    }
  });
};
pauseBtn.onclick = ()=>{
  simOn = !simOn;
  pauseBtn.textContent = simOn ? '⏸ Pause' : '▶ Play';
};
autoBtn.onclick = ()=>{
  cam.auto = !cam.auto;
  autoBtn.classList.toggle('off', !cam.auto);
};
if(matchMedia('(prefers-reduced-motion: reduce)').matches){
  cam.auto = false;
  autoBtn.classList.add('off');
}

function verbFor(h){
  switch(h.state){
    case 'wander': return pick(['is exploring the cage 🐾','is on a secret mission 🕵️']);
    case 'pause':  return pick(['is sniffing the air 👃','is doing a happy wiggle ✨','is plotting something 🤔']);
    case 'eat':    return h.pellet ? 'is munching a sunflower seed 🌻' : 'is raiding the food bowl 🥣';
    case 'wheel':  return 'is running the wheel 🌀';
    case 'sleep':  return 'is power napping 💤';
  }
}
function updateStatus(dt){
  statusTimer -= dt;
  if(statusTimer > 0) return;
  statusTimer = 0.8;
  const h = hamsters[selected];
  statusTxt.textContent = `${h.def.name} ${verbFor(h)}`;
}

/* ============================== main loop ============================ */
const clock = new THREE.Clock();
let wheelVel = 0, wheelBoost = 0, loaded = false;
const loader = document.getElementById('loader');

hamsters.forEach(startWander);

function tick(){
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t  = clock.elapsedTime;

  if(simOn){
    hamsters.forEach(h=>updateHamster(h, dt, t));
    separate();

    const running = hamsters.some(h=>h.state==='wheel' && h.phase==='run');
    wheelVel += ((running?7:0) - wheelVel) * Math.min(1, dt*2.2);
    wheelBoost *= Math.exp(-dt*1.4);
    wheelSpin.rotation.x += (wheelVel + wheelBoost) * dt;

    updatePellets(dt);
    clouds.forEach(c=>{ c.mesh.position.x += c.speed*dt; if(c.mesh.position.x>15) c.mesh.position.x=-15; });
  }

  updateOrbit(dt);
  renderer.render(scene, camera);
  updateBubble();
  updateStatus(dt);

  if(!loaded){
    loaded = true;
    loader.classList.add('done');
    setTimeout(()=>loader.remove(), 700);
  }
}
tick();

addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

**What's inside**

- **The cage** — faceted 12-sided tray with a sand floor, wooden bars, double top ring, plus a water bottle, hay pile, pebbles and wood shavings for texture.
- **Four hamsters** (Mochi, Biscuit, Peanut, Clover) built from flat-shaded primitives, each with a small state machine: *wander → pause (sniffing, wiggling) → eat → wheel → nap*, with blinking, ear flicks, tail wags, cheek puffing while chewing, and hop-squash animation.
- **The wheel** is the star interaction: hamsters take turns climbing in, sprinting (legs blur, wheel spins up), and climbing out. Clicking the wheel gives it a manual push.
- **Props** — food bowl (they raid it and puff their cheeks), a tunnel they stroll under, a house where they nap, and scattered seeds.
- **Interactions** — drag to orbit (with damping + idle auto-orbit), scroll/pinch to zoom, click any hamster for a squeak bubble, **🌻 Feed** drops seeds that send them scrambling, **⏸ Pause** freezes the sim, and the crew panel lets you pick who the live status line reports on.
- **Ambience** — drifting low-poly clouds, warm gradient backdrop with polka dots, soft shadows, and a sticker-style UI in Fredoka + Nunito.

It needs an internet connection on first load for the Three.js CDN and fonts; everything else is self-contained in the one file.