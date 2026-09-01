

Here's the complete project — save it as `index.html` and open it in any modern browser. It loads Three.js from a CDN, so you just need an internet connection.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Titan+One&family=Nunito:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#33241a; --paper:#fffaf0; --peach:#ffe4c8;
    --coral:#ff7f6e; --mint:#8fd6b4; --butter:#ffd166; --teal:#2ec4b6;
  }
  *{ box-sizing:border-box; }
  html,body{ margin:0; height:100%; overflow:hidden; background:var(--peach);
    font-family:'Nunito',sans-serif; color:var(--ink); }

  #scene{ position:fixed; inset:0; opacity:0; transition:opacity .9s ease; }
  #scene.ready{ opacity:1; }
  #scene canvas{ display:block; }

  .vignette{ position:fixed; inset:0; z-index:3; pointer-events:none;
    background:radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(90,45,15,.16) 100%); }

  .card{ position:fixed; z-index:5; background:var(--paper);
    border:3px solid var(--ink); border-radius:16px; box-shadow:0 7px 0 rgba(51,36,26,.22); }

  /* ---- title sticker ---- */
  .title-card{ top:16px; left:16px; padding:14px 18px 12px;
    animation:rise .7s cubic-bezier(.2,1.4,.4,1) both; }
  .eyebrow{ font-size:10px; font-weight:900; letter-spacing:.24em; color:#b0713a; margin-bottom:5px; }
  h1{ font-family:'Titan One',cursive; font-weight:400; margin:0;
    font-size:clamp(20px,3vw,32px); line-height:.95; }
  h1 .c1{ color:var(--ink); } h1 .c2{ color:var(--coral); } h1 .c3{ color:var(--teal); }
  .sub{ margin-top:7px; font-size:12.5px; font-weight:700; color:#7a5c44; }

  /* ---- residents roster ---- */
  .roster{ left:16px; bottom:16px; width:238px; padding:12px 14px 12px;
    animation:rise .7s .15s cubic-bezier(.2,1.4,.4,1) both; }
  .roster-title{ font-size:10px; font-weight:900; letter-spacing:.24em; color:#b0713a; margin-bottom:8px; }
  .row{ display:flex; align-items:center; gap:9px; padding:6px 0; border-top:2px dashed #ecdcc5; }
  .row:first-child{ border-top:none; padding-top:0; }
  .dot{ width:13px; height:13px; border-radius:50%; border:2px solid var(--ink); flex:none; }
  .row .name{ font-size:13px; font-weight:900; line-height:1.1; }
  .row .status{ font-size:11px; font-weight:700; color:#96755a; line-height:1.2; }
  .status.flash{ animation:stflash .5s ease; }
  @keyframes stflash{ 0%{ color:var(--coral); transform:translateX(4px); } }
  .chip{ display:inline-block; margin-top:9px; background:#ffe9c9; border:2px solid var(--ink);
    border-radius:999px; padding:3px 11px; font-size:11px; font-weight:900; }

  /* ---- buttons ---- */
  .controls{ position:fixed; top:16px; right:16px; z-index:5;
    display:flex; flex-direction:column; gap:10px; align-items:flex-end; }
  .btn{ font-family:'Nunito',sans-serif; font-size:14px; font-weight:900; color:var(--ink);
    padding:10px 16px; border:3px solid var(--ink); border-radius:999px; cursor:pointer;
    box-shadow:0 5px 0 var(--ink); transition:transform .12s ease, box-shadow .12s ease;
    animation:rise .7s .25s cubic-bezier(.2,1.4,.4,1) both; }
  .btn:hover{ transform:translateY(-2px); box-shadow:0 7px 0 var(--ink); }
  .btn:active{ transform:translateY(3px); box-shadow:0 2px 0 var(--ink); }
  #btnSeeds{ background:var(--butter); }
  #btnWheel{ background:var(--mint); }

  /* ---- hint pill ---- */
  .hint{ position:fixed; bottom:16px; left:0; right:0; margin:0 auto; width:max-content;
    z-index:5; background:rgba(51,36,26,.88); color:#ffe9c9;
    font-size:12px; font-weight:800; padding:8px 16px; border-radius:999px;
    animation:rise .7s .35s cubic-bezier(.2,1.4,.4,1) both; }

  @keyframes rise{
    from{ opacity:0; transform:translateY(16px) rotate(var(--rot,0deg)); }
    to{ opacity:1; transform:translateY(0) rotate(var(--rot,0deg)); }
  }

  @media (max-width:680px){
    .roster{ width:192px; padding:10px 12px; }
    .sub{ display:none; }
    .btn{ font-size:12px; padding:8px 12px; }
    .hint{ font-size:10px; padding:7px 12px; max-width:92vw; white-space:normal; text-align:center; }
  }
</style>
</head>
<body>

<div id="scene"></div>
<div class="vignette"></div>

<header class="card title-card" style="--rot:-2deg">
  <div class="eyebrow">A TINY 3D DIORAMA</div>
  <h1><span class="c1">LOW-POLY</span> <span class="c2">HAMSTER</span><br><span class="c3">PLAYGROUND</span></h1>
  <div class="sub">3 tiny citizens &middot; 1 very serious wheel &middot; zero plans</div>
</header>

<aside class="card roster">
  <div class="roster-title">RESIDENTS</div>
  <div id="rosterRows"></div>
  <span class="chip" id="seedChip">🌻 loose seeds: 6</span>
</aside>

<div class="controls">
  <button class="btn" id="btnSeeds">🌻 Drop seeds</button>
  <button class="btn" id="btnWheel">🌀 Kick the wheel</button>
</div>

<div class="hint">drag to orbit &middot; scroll to zoom &middot; click a hamster to pet it &middot; click the wheel to kick it</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ================= helpers ================= */
const rand  = (a,b)=> a + Math.random()*(b-a);
const lerp  = (a,b,t)=> a + (b-a)*t;
const clamp = (v,a,b)=> Math.max(a, Math.min(b, v));
function lerpAngle(a,b,t){
  let d = (b-a) % (Math.PI*2);
  if (d >  Math.PI) d -= Math.PI*2;
  if (d < -Math.PI) d += Math.PI*2;
  return a + d * Math.min(1, t);
}
const mat = c => new THREE.MeshStandardMaterial({ color:c, roughness:.9, metalness:0, flatShading:true });

/* ================= boot ================= */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffe4c8);
scene.fog = new THREE.Fog(0xffe4c8, 18, 46);

const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, .1, 100);
camera.position.set(7.5, 5.6, 9.8);

const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.getElementById('scene').appendChild(renderer.domElement);
renderer.domElement.style.cursor = 'grab';

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.1, 0);
controls.enableDamping = true;
controls.dampingFactor = .06;
controls.minDistance = 5;
controls.maxDistance = 19;
controls.minPolarAngle = .2;
controls.maxPolarAngle = 1.42;
controls.autoRotate = !matchMedia('(prefers-reduced-motion: reduce)').matches;
controls.autoRotateSpeed = .5;
controls.addEventListener('start', ()=> controls.autoRotate = false);

scene.add(new THREE.HemisphereLight(0xfff3e0, 0xffc9a0, 1.0));
const sun = new THREE.DirectionalLight(0xfff0d0, 1.6);
sun.position.set(7, 10, 5);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -8; sun.shadow.camera.right = 8;
sun.shadow.camera.top  =  8; sun.shadow.camera.bottom = -8;
sun.shadow.camera.near = 2;  sun.shadow.camera.far = 30;
sun.shadow.bias = -0.0004;
scene.add(sun);

/* ================= the world ================= */
// grass floor
const floor = new THREE.Mesh(new THREE.CircleGeometry(30, 28), mat(0xb9dfa6));
floor.rotation.x = -Math.PI/2; floor.position.y = -0.501; floor.receiveShadow = true;
scene.add(floor);

// wooden tray + jittered low-poly bedding
const tray = new THREE.Mesh(new THREE.BoxGeometry(8.9, .5, 6.9), mat(0xb07b4f));
tray.position.y = -.25; tray.castShadow = tray.receiveShadow = true;
scene.add(tray);

const bedGeo = new THREE.PlaneGeometry(8.4, 6.4, 12, 9);
{
  const p = bedGeo.attributes.position;
  for (let i=0; i<p.count; i++) p.setZ(i, rand(-.035, .05));
  bedGeo.computeVertexNormals();
}
const bedding = new THREE.Mesh(bedGeo, mat(0xf6d9a6));
bedding.rotation.x = -Math.PI/2; bedding.position.y = .01; bedding.receiveShadow = true;
scene.add(bedding);

// wooden lip strips
const stripMat = mat(0x8a5a3b);
function strip(w, d, x, z){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, .14, d), stripMat);
  m.position.set(x, .07, z); m.castShadow = m.receiveShadow = true;
  scene.add(m);
}
strip(8.9, .3, 0, 3.35); strip(8.9, .3, 0, -3.35);
strip(.3, 6.9, 4.35, 0);  strip(.3, 6.9, -4.35, 0);

// cage: posts, finials, rails, instanced pastel bars
const wood = mat(0x8a5a3b);
[[-4.2,-3.2],[4.2,-3.2],[-4.2,3.2],[4.2,3.2]].forEach(([x,z])=>{
  const post = new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,3.1,6), wood);
  post.position.set(x, 1.55, z); post.castShadow = true; scene.add(post);
  const fin = new THREE.Mesh(new THREE.SphereGeometry(.14,6,5), wood);
  fin.position.set(x, 3.12, z); scene.add(fin);
});
function rail(w, d, x, z){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, .13, d), wood);
  m.position.set(x, 3.05, z); m.castShadow = true; scene.add(m);
}
rail(8.7,.13,0,3.2); rail(8.7,.13,0,-3.2); rail(.13,6.7,4.2,0); rail(.13,6.7,-4.2,0);
{
  const bp = [];
  for (let i=0; i<15; i++){ const x = -4.2 + i*(8.4/14); bp.push([x,1.5,3.2],[x,1.5,-3.2]); }
  for (let i=0; i<13; i++){ const z = -3.2 + i*(6.4/12); bp.push([4.2,1.5,z],[-4.2,1.5,z]); }
  const bars = new THREE.InstancedMesh(
    new THREE.CylinderGeometry(.035,.035,3,5),
    new THREE.MeshStandardMaterial({ color:0x9adcd3, roughness:.5, flatShading:true }),
    bp.length
  );
  const d = new THREE.Object3D();
  bp.forEach((p,i)=>{ d.position.set(p[0],p[1],p[2]); d.updateMatrix(); bars.setMatrixAt(i, d.matrix); });
  bars.castShadow = true;
  scene.add(bars);
}

// the wheel (interactive)
const WHEEL_POS   = new THREE.Vector3(-3, 0, -1.9);
const WHEEL_ENTRY = new THREE.Vector3(-3, 0, -0.75);
const wheelGroup = new THREE.Group();
wheelGroup.position.copy(WHEEL_POS);
wheelGroup.userData = { tag:'wheel' };
const wheel = { spin:0, spinner:new THREE.Group() };

const wBase = new THREE.Mesh(new THREE.BoxGeometry(.9,.14,1.3), wheelGroup ? wood : wood);
wBase.position.y = .07; wheelGroup.add(wBase);
[.58,-.58].forEach(z=>{
  const p = new THREE.Mesh(new THREE.BoxGeometry(.16,1.22,.16), wood);
  p.position.set(0,.75,z); wheelGroup.add(p);
});
wheel.spinner.position.y = 1.35;
[.42,-.42].forEach(z=>{
  const pl = new THREE.Mesh(new THREE.CylinderGeometry(1.15,1.15,.07,12).rotateX(Math.PI/2), mat(0xff7f6e));
  pl.position.z = z; wheel.spinner.add(pl);
});
wheel.spinner.add(new THREE.Mesh(new THREE.TorusGeometry(.95,.08,6,18), mat(0xffd166)));
for (let i=0; i<8; i++){
  const s = new THREE.Mesh(new THREE.BoxGeometry(.06,1.84,.06), mat(0xfff6e6));
  s.rotation.z = i*Math.PI/4; wheel.spinner.add(s);
}
wheel.spinner.add(new THREE.Mesh(new THREE.CylinderGeometry(.15,.15,.2,8).rotateX(Math.PI/2), mat(0x33241a)));
const axle = new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,1.25,6).rotateX(Math.PI/2), mat(0x6b4a33));
axle.position.y = 1.35; wheelGroup.add(axle);
wheelGroup.add(wheel.spinner);
wheelGroup.traverse(o=>{ if (o.isMesh) o.castShadow = true; });
scene.add(wheelGroup);

// tunnel
const tunnel = new THREE.Mesh(
  new THREE.CylinderGeometry(.5,.5,1.4,10,1,true,0,Math.PI).rotateX(-Math.PI/2),
  new THREE.MeshStandardMaterial({ color:0x8fd6b4, roughness:.9, flatShading:true, side:THREE.DoubleSide })
);
tunnel.position.set(.9,.5,-1.2); tunnel.rotation.y = .5; tunnel.castShadow = true;
scene.add(tunnel);

// little house
const house = new THREE.Group();
house.position.set(3, 0, -2.3);
const hw   = new THREE.Mesh(new THREE.BoxGeometry(1.15,.85,1.15), mat(0xfff1d6)); hw.position.y = .425;
const roof = new THREE.Mesh(new THREE.ConeGeometry(.98,.7,4), mat(0xef476f));
roof.position.y = 1.2; roof.rotation.y = Math.PI/4;
const door = new THREE.Mesh(new THREE.CircleGeometry(.26,10), mat(0x4a3527));
door.position.set(0,.32,.578);
house.add(hw, roof, door);
house.traverse(o=>{ if (o.isMesh) o.castShadow = true; });
scene.add(house);

// food bowl
const BOWL_POS   = new THREE.Vector3(3.05, 0, 1.7);
const BOWL_POINT = new THREE.Vector3(2.5, 0, 1.4);
const bowl = new THREE.Group();
bowl.position.copy(BOWL_POS);
const bw   = new THREE.Mesh(new THREE.CylinderGeometry(.42,.28,.2,10), mat(0x2ec4b6)); bw.position.y = .1;
const mush = new THREE.Mesh(new THREE.DodecahedronGeometry(.26,0), mat(0x9c6b3c));
mush.scale.set(1,.45,1); mush.position.y = .2;
bowl.add(bw, mush);
bowl.traverse(o=>{ if (o.isMesh) o.castShadow = true; });
scene.add(bowl);

// bouncy ball toy
const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(.2,0), mat(0xef476f));
ball.position.set(.5,.2,.7); ball.castShadow = true;
scene.add(ball);
const ballVel = new THREE.Vector3();

// seeds
const seedGeo = new THREE.DodecahedronGeometry(.07,0);
const seedMat = mat(0xb5793b);
const seeds = [];
function addSeed(x, z, landed){
  const m = new THREE.Mesh(seedGeo, seedMat);
  m.castShadow = true;
  m.position.set(x, landed ? .07 : rand(2.2,3), z);
  scene.add(m);
  seeds.push({ mesh:m, vy:0, landed, eaten:false, shrink:1, owner:null });
}
for (let i=0; i<6; i++) addSeed(rand(-3,3), rand(-2,2), true);

// obstacles hamsters politely avoid
const OBSTACLES = [
  { x:-3,   z:-1.9, r:1.1  },  // wheel
  { x:3,    z:-2.3, r:1.0  },  // house
  { x:3.05, z:1.7,  r:.55  },  // bowl
  { x:.9,   z:-1.2, r:.8   },  // tunnel
];

// drifting clouds
const clouds = [];
for (let i=0; i<3; i++){
  const g = new THREE.Group();
  const cm = mat(0xffffff);
  for (let j=0; j<3; j++){
    const s = new THREE.Mesh(new THREE.IcosahedronGeometry(rand(.5,.9),0), cm);
    s.position.set(j*.85-.85, rand(-.1,.2), rand(-.3,.3));
    s.scale.y = .55; g.add(s);
  }
  g.position.set(rand(-12,12), rand(5,7.5), rand(-9,-4));
  scene.add(g); clouds.push(g);
}

// dust motes
const moteCount = 46;
const moteGeo = new THREE.BufferGeometry();
const mp = new Float32Array(moteCount*3), mBase = new Float32Array(moteCount);
for (let i=0; i<moteCount; i++){
  mp[i*3] = rand(-6,6); mp[i*3+1] = rand(.3,4); mp[i*3+2] = rand(-4.5,4.5);
  mBase[i] = mp[i*3+1];
}
moteGeo.setAttribute('position', new THREE.BufferAttribute(mp,3));
const dotTex = (()=>{
  const c = document.createElement('canvas'); c.width = c.height = 32;
  const x = c.getContext('2d');
  const g = x.createRadialGradient(16,16,0,16,16,16);
  g.addColorStop(0,'rgba(255,255,255,.9)'); g.addColorStop(1,'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0,0,32,32);
  return new THREE.CanvasTexture(c);
})();
scene.add(new THREE.Points(moteGeo, new THREE.PointsMaterial({
  size:.09, map:dotTex, transparent:true, opacity:.55, depthWrite:false, color:0xfff6e6
})));

// heart sprites
const heartTex = (()=>{
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const x = c.getContext('2d');
  x.fillStyle = '#ff5d8f';
  x.beginPath();
  x.moveTo(32,56);
  x.bezierCurveTo(4,36, 8,8, 32,20);
  x.bezierCurveTo(56,8, 60,36, 32,56);
  x.fill();
  return new THREE.CanvasTexture(c);
})();
const hearts = [];
function spawnHearts(pos){
  for (let i=0; i<3; i++){
    const m = new THREE.SpriteMaterial({ map:heartTex, transparent:true, depthWrite:false });
    const s = new THREE.Sprite(m);
    s.position.copy(pos).add(new THREE.Vector3(rand(-.25,.25), rand(0,.25), rand(-.25,.25)));
    s.scale.setScalar(.3);
    scene.add(s);
    hearts.push({ s, life:1, vy:rand(.7,1.2) });
  }
}

/* ================= hamsters ================= */
const PALETTES = [
  { name:'Mochi', fur:0xf5a94b, belly:0xffe3b3, pink:0xff9d9d },
  { name:'Pip',   fur:0xfdf3e7, belly:0xffffff, pink:0xffb3c1 },
  { name:'Grits', fur:0x9aa5b1, belly:0xe9eef3, pink:0xf4a0a0 },
];
const hamsters = [];

function makeHamster(pal){
  const g = new THREE.Group();
  const fur = mat(pal.fur), belly = mat(pal.belly), pink = mat(pal.pink);

  const body = new THREE.Mesh(new THREE.SphereGeometry(.34,8,6), fur);
  body.scale.set(1,.85,1.15); body.position.y = .3;

  const head = new THREE.Group(); head.position.set(0,.42,.3);
  head.add(new THREE.Mesh(new THREE.SphereGeometry(.26,8,6), fur));
  const snout = new THREE.Mesh(new THREE.SphereGeometry(.11,6,5), belly); snout.position.set(0,-.05,.22);
  const nose  = new THREE.Mesh(new THREE.SphereGeometry(.035,5,4), pink); nose.position.set(0,-.01,.32);
  const eyeGeo = new THREE.SphereGeometry(.045,6,5), eyeMat = mat(0x2b1d16);
  const eL = new THREE.Mesh(eyeGeo, eyeMat); eL.position.set(-.12,.05,.2);
  const eR = new THREE.Mesh(eyeGeo, eyeMat); eR.position.set( .12,.05,.2);
  const chGeo = new THREE.SphereGeometry(.09,6,5);
  const cL = new THREE.Mesh(chGeo, belly); cL.position.set(-.19,-.09,.13);
  const cR = new THREE.Mesh(chGeo, belly); cR.position.set( .19,-.09,.13);
  const earGeo = new THREE.ConeGeometry(.07,.13,5);
  const earL = new THREE.Mesh(earGeo, fur); earL.position.set(-.15,.22,.02); earL.rotation.z =  .35;
  const earR = new THREE.Mesh(earGeo, fur); earR.position.set( .15,.22,.02); earR.rotation.z = -.35;
  head.add(snout, nose, eL, eR, cL, cR, earL, earR);

  const armGeo = new THREE.SphereGeometry(.07,6,5);
  const aL = new THREE.Mesh(armGeo, fur); aL.position.set(-.16,.24,.3);
  const aR = new THREE.Mesh(armGeo, fur); aR.position.set( .16,.24,.3);
  const ftGeo = new THREE.SphereGeometry(.06,6,5);
  const fL = new THREE.Mesh(ftGeo, belly); fL.position.set(-.11,.06,.3);
  const fR = new THREE.Mesh(ftGeo, belly); fR.position.set( .11,.06,.3);
  const tail = new THREE.Mesh(new THREE.ConeGeometry(.05,.14,5), pink);
  tail.rotation.x = -Math.PI/2; tail.position.set(0,.32,-.4);

  g.add(body, head, aL, aR, fL, fR, tail);
  g.traverse(o=>{ if (o.isMesh) o.castShadow = true; });

  return {
    group:g, body, head,
    eyes:[eL,eR], cheeks:[cL,cR], ears:[earL,earR],
    heading:rand(0,Math.PI*2), target:new THREE.Vector3(),
    state:'pause', stateTime:0, baseY:0,
    walkPhase:rand(0,6), ridePhase:0, hopT:0,
    hopFrom:new THREE.Vector3(), hopTo:new THREE.Vector3(),
    blinkT:rand(1,4), blinkFlash:0,
    cheekScale:1, cheekTarget:1,
    seed:null, moving:false, spinVel:0,
    phase:rand(0,6), pal
  };
}

PALETTES.forEach((pal, i)=>{
  const h = makeHamster(pal);
  h.group.position.set(rand(-2,2), 0, rand(-1,1.5));
  h.group.userData = { tag:'hamster', ref:h };
  scene.add(h.group);
  hamsters.push(h);
});

/* ---- live roster UI ---- */
const rosterEl = document.getElementById('rosterRows');
const statusEls = {};
hamsters.forEach((h, i)=>{
  const row = document.createElement('div');
  row.className = 'row';
  row.innerHTML =
    '<span class="dot" style="background:#'+h.pal.fur.toString(16).padStart(6,'0')+'"></span>' +
    '<div><div class="name">'+h.pal.name+'</div>' +
    '<div class="status" id="st-'+i+'">\u2026</div></div>';
  rosterEl.appendChild(row);
  statusEls[h] = row.querySelector('.status');
});

const PHRASES = {
  wander:['wandering','sniffing the air','doing laps','lost, probably','vibing'],
  pause:['resting','daydreaming','grooming','staring at nothing','thinking about seeds'],
  toWheel:['sprinting to the wheel!','WHEEL TIME!!'],
  ride:['on the wheel','marathon mode','spinning for snacks'],
  hop:['hopping off!'],
  toEat:['heading to dinner','smells seeds\u2026'],
  eat:['nom nom nom','chewing loudly','filling cheeks'],
  toSeed:['found a seed!!','treasure hunt!'],
  nibble:['crunch\u2026','delicious'],
  petted:['SPIN SPIN SPIN \u2665','so loved, so dizzy'],
};
function setStatus(h, text){
  const el = statusEls[h]; if (!el) return;
  el.textContent = text;
  el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash');
}
function setState(h, s, time){
  h.state = s; h.stateTime = time;
  if (s !== 'eat' && s !== 'nibble'){ h.cheekTarget = 1; h.head.rotation.x = 0; }
  const p = PHRASES[s];
  setStatus(h, p[Math.floor(Math.random()*p.length)]);
}

/* ---- brains ---- */
let wheelRider = null;

function pickTarget(h){
  h.target.set(rand(-3.3,3.3), 0, rand(-2.3,2.3));
  if (h.target.distanceTo(WHEEL_POS) < 1.3) h.target.z += 1.4;
}
function moveToward(h, tx, tz, speed, dt){
  const p = h.group.position;
  const dx = tx - p.x, dz = tz - p.z, dist = Math.hypot(dx, dz);
  if (dist < .24){ h.moving = false; return true; }
  h.heading = lerpAngle(h.heading, Math.atan2(dx, dz), 10*dt);
  p.x += Math.sin(h.heading)*speed*dt;
  p.z += Math.cos(h.heading)*speed*dt;
  h.group.rotation.y = h.heading;
  h.moving = true;
  return false;
}
function avoid(h){
  const p = h.group.position;
  p.x = clamp(p.x, -3.5, 3.5);
  p.z = clamp(p.z, -2.5, 2.5);
  for (const o of OBSTACLES){
    const dx = p.x - o.x, dz = p.z - o.z, d = Math.hypot(dx, dz);
    if (d < o.r && d > .001){
      if (h.target && Math.abs(o.x - h.target.x) < .35 && Math.abs(o.z - h.target.z) < .35) continue;
      p.x = o.x + dx/d*o.r;
      p.z = o.z + dz/d*o.r;
    }
  }
}
function decideNext(h){
  const near = seeds.find(s => !s.eaten && s.landed && !s.owner &&
    s.mesh.position.distanceTo(h.group.position) < 3);
  if (near){ near.owner = h; h.seed = near; setState(h, 'toSeed', 99); return; }
  const r = Math.random();
  if (r < .18 && !wheelRider){ setState(h, 'toWheel', 99); return; }
  if (r < .34){ setState(h, 'toEat', 99); return; }
  pickTarget(h); setState(h, 'wander', 99);
}

let t = 0;
function updateHamster(h, dt){
  const p = h.group.position;
  h.moving = false;
  h.stateTime -= dt;

  // blinking
  h.blinkT -= dt;
  if (h.blinkT <= 0){ h.blinkT = rand(2,5); h.blinkFlash = .13; }
  if (h.blinkFlash > 0) h.blinkFlash -= dt;
  const eyeS = h.blinkFlash > 0 ? .15 : 1;
  h.eyes.forEach(e => e.scale.y = eyeS);
  // lazy ear sway
  h.ears[1].rotation.z = -.35 + Math.sin(t*1.7 + h.phase)*.06;

  switch (h.state){
    case 'wander':
      if (moveToward(h, h.target.x, h.target.z, 1.05, dt)) setState(h, 'pause', rand(1,3.5));
      break;
    case 'pause':
      if (h.stateTime <= 0) decideNext(h);
      break;
    case 'toWheel':
      if (wheelRider && wheelRider !== h){ pickTarget(h); setState(h, 'wander', 99); break; }
      if (moveToward(h, WHEEL_ENTRY.x, WHEEL_ENTRY.z, 1.7, dt)){
        h.baseY = .32; h.ridePhase = 0; wheelRider = h;
        setState(h, 'ride', rand(3,5.5));
      }
      break;
    case 'ride':
      p.x = lerp(p.x, WHEEL_POS.x, Math.min(1, 8*dt));
      p.z = lerp(p.z, WHEEL_POS.z, Math.min(1, 8*dt));
      h.ridePhase += dt*11;
      h.heading = lerpAngle(h.heading, Math.PI, 6*dt);
      h.group.rotation.y = h.heading;
      if (h.stateTime <= 0){
        wheelRider = null;
        h.hopFrom.copy(p);
        h.hopTo.set(WHEEL_POS.x, 0, WHEEL_POS.z + 1.15);
        h.hopT = .45;
        setState(h, 'hop', .45);
      }
      break;
    case 'hop': {
      h.hopT -= dt;
      const k = 1 - Math.max(0, h.hopT)/.45;
      p.lerpVectors(h.hopFrom, h.hopTo, k);
      if (k >= 1){ p.y = 0; pickTarget(h); setState(h, 'wander', 99); }
      break;
    }
    case 'toEat':
      if (moveToward(h, BOWL_POINT.x, BOWL_POINT.z, 1.15, dt)) setState(h, 'eat', rand(2.5,4.5));
      break;
    case 'eat':
      h.heading = lerpAngle(h.heading, Math.atan2(BOWL_POS.x - p.x, BOWL_POS.z - p.z), 6*dt);
      h.group.rotation.y = h.heading;
      h.head.rotation.x = .55 + Math.sin(t*9)*.18;
      h.cheekTarget = 1.5;
      if (h.stateTime <= 0) setState(h, 'pause', rand(1,2.5));
      break;
    case 'toSeed':
      if (!h.seed || h.seed.eaten || !h.seed.landed){
        if (h.seed) h.seed.owner = null;
        h.seed = null; pickTarget(h); setState(h, 'wander', 99); break;
      }
      if (moveToward(h, h.seed.mesh.position.x, h.seed.mesh.position.z, 1.5, dt))
        setState(h, 'nibble', .9);
      break;
    case 'nibble':
      h.head.rotation.x = .4 + Math.sin(t*14)*.2;
      h.cheekTarget = 1.6;
      if (h.stateTime <= 0){
        const s = h.seed; h.seed = null;
        if (s && !s.eaten) s.eaten = true;
        setState(h, 'pause', rand(1,2.5));
      }
      break;
    case 'petted':
      h.spinVel = Math.max(h.spinVel - 13*dt, 0);
      h.group.rotation.y += h.spinVel*dt;
      if (h.stateTime <= 0){ p.y = 0; pickTarget(h); setState(h, 'wander', 99); }
      break;
  }

  // vertical motion + walk bob
  if (h.state === 'ride')            p.y = h.baseY + Math.abs(Math.sin(h.ridePhase))*.06;
  else if (h.state === 'hop')        p.y = Math.sin(clamp(1 - Math.max(0,h.hopT)/.45, 0, 1)*Math.PI)*.45;
  else if (h.state === 'petted'){
    const k = 1 - Math.max(0, h.stateTime)/1.2;
    p.y = Math.abs(Math.sin(k*Math.PI*2))*.3;
  }
  else if (h.moving){ h.walkPhase += dt*13; p.y = Math.abs(Math.sin(h.walkPhase))*.05; }
  else p.y = h.baseY + Math.sin(t*2 + h.phase)*.012;

  // squash & stretch
  h.body.scale.y = .85 * (h.moving
    ? 1 + Math.sin(h.walkPhase*2)*.05
    : 1 + Math.sin(t*2 + h.phase)*.02);

  // cheek pouches
  h.cheekScale = lerp(h.cheekScale, h.cheekTarget, Math.min(1, 3.5*dt));
  h.cheeks.forEach(c => c.scale.setScalar(h.cheekScale));

  // nudge the ball
  if (h.moving){
    const bdx = ball.position.x - p.x, bdz = ball.position.z - p.z, bd = Math.hypot(bdx, bdz);
    if (bd < .5 && bd > .01){ ballVel.x += bdx/bd*1.5; ballVel.z += bdz/bd*1.5; }
  }

  if (h.state !== 'ride' && h.state !== 'hop') avoid(h);
}

// kickoff
pickTarget(hamsters[0]); setState(hamsters[0], 'wander', 99);
setState(hamsters[1], 'pause', rand(1,3));
setState(hamsters[2], 'toWheel', 99);

/* ================= interactions ================= */
let actx = null;
function beep(f0, f1, dur, type='sine', vol=.05){
  try{
    actx = actx || new (window.AudioContext || window.webkitAudioContext)();
    if (actx.state === 'suspended') actx.resume();
    const o = actx.createOscillator(), g = actx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(f0, actx.currentTime);
    o.frequency.exponentialRampToValueAtTime(Math.max(f1,1), actx.currentTime + dur);
    g.gain.setValueAtTime(vol, actx.currentTime);
    g.gain.exponentialRampToValueAtTime(.0001, actx.currentTime + dur);
    o.connect(g); g.connect(actx.destination);
    o.start(); o.stop(actx.currentTime + dur);
  }catch(err){}
}

const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
const pickables = [...hamsters.map(h => h.group), wheelGroup];
function findTag(o){ while (o){ if (o.userData && o.userData.tag) return o.userData; o = o.parent; } return null; }
function pickAt(x, y){
  ndc.set(x/innerWidth*2 - 1, -(y/innerHeight)*2 + 1);
  ray.setFromCamera(ndc, camera);
  for (const hit of ray.intersectObjects(pickables, true)){
    const tag = findTag(hit.object);
    if (tag) return tag;
  }
  return null;
}

function pet(h){
  if (h.state === 'petted') return;
  if (h.state === 'ride' || h.state === 'toWheel') wheelRider = null;
  if (h.seed){ h.seed.owner = null; h.seed = null; }
  h.spinVel = 11;
  spawnHearts(h.group.position.clone().add(new THREE.Vector3(0,.9,0)));
  beep(650, 1250, .16, 'triangle', .06);
  setState(h, 'petted', 1.2);
}
function kickWheel(){
  wheel.spin = Math.min(wheel.spin + 6, 12);
  beep(150, 430, .28, 'sawtooth', .05);
}

let downX = 0, downY = 0;
renderer.domElement.addEventListener('pointerdown', e => { downX = e.clientX; downY = e.clientY; });
renderer.domElement.addEventListener('pointerup', e => {
  if (Math.hypot(e.clientX - downX, e.clientY - downY) > 7) return;
  const tag = pickAt(e.clientX, e.clientY);
  if (!tag) return;
  if (tag.tag === 'hamster') pet(tag.ref);
  else if (tag.tag === 'wheel') kickWheel();
});
renderer.domElement.addEventListener('pointermove', e => {
  renderer.domElement.style.cursor = pickAt(e.clientX, e.clientY) ? 'pointer' : 'grab';
});

const chip = document.getElementById('seedChip');
function updateSeedChip(){
  chip.textContent = '\uD83C\uDF3B loose seeds: ' + seeds.filter(s => !s.eaten).length;
}
updateSeedChip();

document.getElementById('btnSeeds').addEventListener('click', ()=>{
  for (let i=0; i<4; i++) addSeed(rand(-3,3), rand(-2,2), false);
  beep(320, 180, .09, 'triangle', .05);
  updateSeedChip();
});
document.getElementById('btnWheel').addEventListener('click', kickWheel);

/* ================= system updates ================= */
function updateWheel(dt){
  const target = wheelRider ? 3.6 : 0;
  wheel.spin += (target - wheel.spin) * Math.min(1, (wheelRider ? 2.5 : .6) * dt);
  if (!wheelRider) wheel.spin *= Math.pow(.3, dt);
  wheel.spinner.rotation.z -= wheel.spin * dt;
  wheelGroup.rotation.x = Math.sin(t*4) * .012 * Math.min(1, wheel.spin/4);
}
function updateBall(dt){
  ballVel.multiplyScalar(Math.max(0, 1 - 1.6*dt));
  ball.position.addScaledVector(ballVel, dt);
  ball.rotation.x += ballVel.z/.2*dt;
  ball.rotation.z -= ballVel.x/.2*dt;
  if (ball.position.x >  3.55){ ball.position.x =  3.55; ballVel.x *= -.6; }
  if (ball.position.x < -3.55){ ball.position.x = -3.55; ballVel.x *= -.6; }
  if (ball.position.z >  2.55){ ball.position.z =  2.55; ballVel.z *= -.6; }
  if (ball.position.z < -2.55){ ball.position.z = -2.55; ballVel.z *= -.6; }
  if (ballVel.lengthSq() < .001) ballVel.set(0,0,0);
}
function updateSeeds(dt){
  for (let i=seeds.length-1; i>=0; i--){
    const s = seeds[i];
    if (s.eaten){
      s.shrink -= dt*4;
      if (s.shrink <= 0){
        scene.remove(s.mesh);
        seeds.splice(i,1);
        updateSeedChip();
        continue;
      }
      s.mesh.scale.setScalar(Math.max(s.shrink, .02));
      continue;
    }
    if (!s.landed){
      s.vy -= 9*dt;
      s.mesh.position.y += s.vy*dt;
      if (s.mesh.position.y <= .07){
        s.mesh.position.y = .07;
        s.vy = -s.vy*.35;
        if (Math.abs(s.vy) < .6){ s.landed = true; s.vy = 0; }
      }
    }
  }
}
function updateHearts(dt){
  for (let i=hearts.length-1; i>=0; i--){
    const h = hearts[i];
    h.life -= dt;
    h.s.position.y += h.vy*dt;
    h.s.scale.setScalar(.3 * (1 + (1 - h.life)*.9));
    h.s.material.opacity = Math.max(h.life, 0);
    if (h.life <= 0){
      scene.remove(h.s);
      h.s.material.dispose();
      hearts.splice(i,1);
    }
  }
}

/* ================= main loop ================= */
const clock = new THREE.Clock();
function tick(){
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), .05);
  t += dt;

  hamsters.forEach(h => updateHamster(h, dt));
  updateWheel(dt);
  updateBall(dt);
  updateSeeds(dt);
  updateHearts(dt);

  const pos = moteGeo.attributes.position;
  for (let i=0; i<moteCount; i++) pos.setY(i, mBase[i] + Math.sin(t*.5 + i*1.7)*.35);
  pos.needsUpdate = true;

  clouds.forEach(c => { c.position.x += dt*.25; if (c.position.x > 14) c.position.x = -14; });

  controls.update();
  renderer.render(scene, camera);
}
tick();
setTimeout(()=> document.getElementById('scene').classList.add('ready'), 150);

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

- **The cage** — a wooden tray with jittered low-poly bedding, pastel teal bars (instanced), posts with ball finials, and a soft peach sky with drifting clouds, dust motes, and fog for depth.
- **Three residents** — Mochi (golden), Pip (snow), and Grits (slate), each built from flat-shaded primitives with chubby cheeks, blinking eyes, and idle ear sways.
- **Autonomous behavior** — a small state machine per hamster: wandering, pausing, sprinting to the wheel, riding it (it spins up, then they hop off), eating at the bowl with head-bobbing and puffing cheeks, and hunting for seeds.
- **Interactivity** — orbit/zoom camera (gentle auto-rotate until you grab it), click a hamster to pet it (happy spin + floating hearts + a squeak), click the wheel to kick it, a "Drop seeds" button that rains seeds the hamsters race to claim, and a live roster card that narrates what each hamster is doing right now.
- **Bonus physics** — hamsters can nudge the red ball around the tray, and seeds bounce when they land.

**How to run:** save as `index.html`, double-click it. Everything is procedural — no assets to download beyond the Three.js CDN and the two fonts.