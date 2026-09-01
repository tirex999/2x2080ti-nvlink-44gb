Here's the complete single-file project — save as `index.html` and open in any modern browser (it pulls Three.js from a CDN, so it needs an internet connection on first load).

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
  :root{ --ink:#33272a; --paper:#fffdf7; --coral:#f2795f; --mint:#5fd0bb; --butter:#ffd166; }
  *{ box-sizing:border-box; margin:0; }
  html,body{ height:100%; }
  body{
    overflow:hidden;
    font-family:'Nunito',system-ui,sans-serif;
    color:var(--ink);
    background:linear-gradient(180deg,#8fd3f0 0%, #c6ecdf 46%, #ffe9b8 100%);
  }
  body::after{ /* soft vignette for depth */
    content:''; position:fixed; inset:0; pointer-events:none; z-index:2;
    background:radial-gradient(ellipse at 50% 42%, transparent 55%, rgba(64,42,80,.15) 100%);
  }
  canvas{ display:block; }

  #hud{ position:fixed; inset:0; pointer-events:none; z-index:5; }
  #hud > *{ animation:pop .55s cubic-bezier(.34,1.56,.64,1) backwards; }
  .title-card{ animation-delay:.05s } .top-right{ animation-delay:.15s } .hints{ animation-delay:.28s }
  @keyframes pop{ from{ opacity:0; transform:translateY(12px) scale(.95); } to{ opacity:1; transform:none; } }

  .card{ background:var(--paper); border:3px solid var(--ink); box-shadow:6px 6px 0 rgba(51,39,42,.16); }
  .title-card{
    position:absolute; top:18px; left:18px; padding:14px 18px 13px; border-radius:18px;
    max-width:min(430px, calc(100vw - 36px));
  }
  .title-card h1{ font-family:'Fredoka'; font-weight:700; font-size:clamp(19px,2.4vw,28px); line-height:1.15; }
  .title-card p{ font-size:13px; font-weight:600; color:#7a6a5e; margin-top:4px; }
  .dots{ display:flex; gap:6px; margin-top:10px; }
  .dots i{ width:11px; height:11px; border-radius:50%; border:2px solid var(--ink); display:inline-block; }

  .top-right{ position:absolute; top:18px; right:18px; display:flex; flex-direction:column; align-items:flex-end; gap:10px; }
  #seedBtn{
    pointer-events:auto; cursor:pointer;
    font-family:'Fredoka'; font-weight:600; font-size:16px; color:#fff;
    background:var(--coral); border:3px solid var(--ink); border-radius:999px;
    padding:10px 18px; box-shadow:4px 4px 0 rgba(51,39,42,.85);
    transition:transform .12s, box-shadow .12s, background .12s;
  }
  #seedBtn:hover{ transform:translate(-2px,-2px); box-shadow:6px 6px 0 rgba(51,39,42,.85); background:#ff8a6e; }
  #seedBtn:active{ transform:translate(2px,2px); box-shadow:1px 1px 0 rgba(51,39,42,.85); }

  .chip{
    background:rgba(255,253,247,.92); border:2px solid var(--ink); border-radius:999px;
    padding:5px 12px; font-size:12px; font-weight:700; letter-spacing:.02em;
    box-shadow:3px 3px 0 rgba(51,39,42,.12);
  }
  .chip b{ color:var(--coral); font-weight:800; }
  .hints{ position:absolute; left:18px; bottom:16px; display:flex; gap:8px; flex-wrap:wrap; max-width:calc(100vw - 36px); }

  #tip{
    position:fixed; z-index:9; pointer-events:none; white-space:nowrap;
    background:var(--ink); color:#ffe9c6; font-family:'Fredoka'; font-weight:600; font-size:13px;
    padding:6px 11px; border-radius:10px; transform:translate(-50%,-130%);
    opacity:0; transition:opacity .12s;
  }
  #tip b{ color:var(--butter); }
  #bubble{
    position:fixed; z-index:9; pointer-events:none; white-space:nowrap;
    background:#fff; border:2.5px solid var(--ink); border-radius:12px; padding:4px 10px;
    font-family:'Fredoka'; font-weight:700; font-size:14px; color:var(--coral); opacity:0;
  }
  @media (max-width:600px){
    .hints .chip:nth-child(n+3){ display:none; }
    .title-card p{ display:none; }
  }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>

<div id="hud">
  <div class="card title-card">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <p>Four tiny employees. One wheel. Infinite snacks.</p>
    <div class="dots">
      <i style="background:#f2ae5c"></i><i style="background:#f5f1ea"></i>
      <i style="background:#aeb6c2"></i><i style="background:#a9744f"></i>
    </div>
  </div>
  <div class="top-right">
    <button id="seedBtn">🌻 Toss a seed</button>
    <div class="chip" id="counter">munched: 0</div>
  </div>
  <div class="hints">
    <span class="chip"><b>drag</b>&nbsp; orbit</span>
    <span class="chip"><b>scroll</b>&nbsp; zoom</span>
    <span class="chip"><b>click sand</b>&nbsp; toss a seed</span>
    <span class="chip"><b>boop</b>&nbsp; a hamster</span>
  </div>
</div>
<div id="tip"></div>
<div id="bubble"></div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================== SETUP ============================== */
const tipEl = document.getElementById('tip');
const bubbleEl = document.getElementById('bubble');
const counterEl = document.getElementById('counter');
const seedBtn = document.getElementById('seedBtn');

const renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.1, 100);
camera.position.set(8, 5.6, 9.5);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 4.5;
controls.maxDistance = 20;
controls.maxPolarAngle = Math.PI/2 - 0.06;
controls.minPolarAngle = 0.15;
controls.enablePan = false;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.7;
let lastUser = performance.now() - 9000;
controls.addEventListener('start', () => lastUser = performance.now());

scene.add(new THREE.HemisphereLight(0xcfeaff, 0xffe0b0, 1.0));
const sunLight = new THREE.DirectionalLight(0xfff1d6, 2.4);
sunLight.position.set(7, 11, 5);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -8; sunLight.shadow.camera.right = 8;
sunLight.shadow.camera.top = 8;   sunLight.shadow.camera.bottom = -8;
sunLight.shadow.camera.near = 2;  sunLight.shadow.camera.far = 30;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
const fill = new THREE.DirectionalLight(0xbfe0ff, 0.5);
fill.position.set(-6, 6, -5);
scene.add(fill);

/* ============================ HELPERS ============================= */
const rand  = THREE.MathUtils.randFloat;
const damp  = THREE.MathUtils.damp;
const clamp = THREE.MathUtils.clamp;
const ease  = k => k*k*(3-2*k);
function dampAngle(a, b, lambda, dt){
  let d = (b - a) % (Math.PI*2);
  if (d >  Math.PI) d -= Math.PI*2;
  if (d < -Math.PI) d += Math.PI*2;
  return a + d * (1 - Math.exp(-lambda*dt));
}
const matCache = {};
function mat(c){
  if (!matCache[c]) matCache[c] = new THREE.MeshStandardMaterial({ color:c, flatShading:true, roughness:.95, metalness:0 });
  return matCache[c];
}
const S = (r, w, h) => new THREE.SphereGeometry(r, w, h);

/* ========================= WORLD CONSTANTS ======================== */
const FLOOR_Y   = 0.62;
const WHEEL_POS = new THREE.Vector3(-2.0, FLOOR_Y, -1.05);
const BOWL_POS  = new THREE.Vector3( 2.1, FLOOR_Y,  1.15);
const BX = { min:-2.8, max:2.8 };
const BZ = { min:-1.75, max:1.75 };
const SPEED = 1.15;

/* ============================ ENVIRONMENT ========================= */
const dirt = new THREE.Mesh(new THREE.CylinderGeometry(15, 14.3, .5, 32), mat(0xb5825a));
dirt.position.y = -.25; dirt.receiveShadow = true; scene.add(dirt);
const grass = new THREE.Mesh(new THREE.CircleGeometry(15, 32), mat(0x93d17e));
grass.rotation.x = -Math.PI/2; grass.position.y = .005; grass.receiveShadow = true; scene.add(grass);

const sun = new THREE.Mesh(new THREE.IcosahedronGeometry(1.4, 0), new THREE.MeshBasicMaterial({ color:0xffd76a }));
sun.position.set(-13, 10.5, -17); scene.add(sun);

const clouds = [];
function makeCloud(x, y, z, s){
  const g = new THREE.Group();
  for (let i = 0; i < 3; i++){
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(.5 + Math.random()*.4, 0), mat(0xffffff));
    m.position.set(i*.6 - .6, Math.random()*.15, Math.random()*.3);
    m.scale.y = .6;
    g.add(m);
  }
  g.position.set(x, y, z); g.scale.setScalar(s);
  g.userData.v = .25 + Math.random()*.3;
  scene.add(g); clouds.push(g);
}
makeCloud(-10, 7, -14, 1.6); makeCloud(4, 8.5, -16, 2.2); makeCloud(12, 6.5, -10, 1.2);

function makeTree(x, z, s){
  const g = new THREE.Group();
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(.14*s, .18*s, .6*s, 6), mat(0x8a5a3b));
  trunk.position.y = .3*s;
  const f1 = new THREE.Mesh(new THREE.IcosahedronGeometry(.7*s, 0), mat(0x6cbf6b));
  f1.position.y = .95*s;
  const f2 = new THREE.Mesh(new THREE.IcosahedronGeometry(.45*s, 0), mat(0x83d47f));
  f2.position.set(.25*s, 1.35*s, .1*s);
  g.add(trunk, f1, f2);
  g.position.set(x, 0, z); g.rotation.y = Math.random()*3;
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  scene.add(g);
}
makeTree(-7.5, -3.5, 1.1); makeTree(8, -5, 1.3); makeTree(6.8, 4.5, .9);

const grassMat = mat(0x7cc576);
for (let i = 0; i < 16; i++){
  const a = Math.random()*Math.PI*2, r = 5.5 + Math.random()*8.5;
  const t = new THREE.Mesh(new THREE.ConeGeometry(.09, .28, 5), grassMat);
  t.position.set(Math.cos(a)*r, .14, Math.sin(a)*r);
  t.rotation.y = Math.random()*3; t.castShadow = true;
  scene.add(t);
}
const flowerCols = [0xff8fb3, 0xffd166, 0xff8a5c, 0xa5d8ff, 0xc3a6ff];
for (let i = 0; i < 8; i++){
  const a = Math.random()*Math.PI*2, r = 5 + Math.random()*9;
  const f = new THREE.Group();
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(.02, .02, .24, 4), grassMat);
  stem.position.y = .12;
  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(.09, 0), mat(flowerCols[i%5]));
  head.position.y = .26; head.castShadow = true;
  f.add(stem, head);
  f.position.set(Math.cos(a)*r, 0, Math.sin(a)*r);
  scene.add(f);
}

/* ============================== CAGE ============================== */
let sandMesh;
(function buildCage(){
  const g = new THREE.Group();
  const white = mat(0xf7f9fc), barMat = mat(0xf2795f);

  const tray = new THREE.Mesh(new THREE.BoxGeometry(7.2, .5, 4.6), white);
  tray.position.y = .25; g.add(tray);
  const lip = new THREE.Mesh(new THREE.BoxGeometry(7.4, .12, 4.8), white);
  lip.position.y = .56; g.add(lip);
  sandMesh = new THREE.Mesh(new THREE.BoxGeometry(6.8, .1, 4.2), mat(0xf2cf8b));
  sandMesh.position.y = .57; sandMesh.receiveShadow = true; g.add(sandMesh);

  const barGeo = new THREE.CylinderGeometry(.04, .04, 2.28, 5);
  for (let i = 0; i <= 12; i++){
    const x = -3.2 + i*(6.4/12);
    for (const z of [-2.2, 2.2]){
      const b = new THREE.Mesh(barGeo, barMat);
      b.position.set(x, 1.76, z); b.castShadow = true; g.add(b);
    }
  }
  for (let i = 0; i <= 8; i++){
    const z = -2.2 + i*(4.4/8);
    for (const x of [-3.2, 3.2]){
      const b = new THREE.Mesh(barGeo, barMat);
      b.position.set(x, 1.76, z); b.castShadow = true; g.add(b);
    }
  }
  const postGeo = new THREE.CylinderGeometry(.07, .07, 2.3, 6);
  for (const x of [-3.2, 3.2]) for (const z of [-2.2, 2.2]){
    const p = new THREE.Mesh(postGeo, barMat);
    p.position.set(x, 1.77, z); p.castShadow = true; g.add(p);
  }
  for (const z of [-2.2, 2.2]){
    const r = new THREE.Mesh(new THREE.BoxGeometry(7.3, .09, .09), barMat);
    r.position.set(0, 2.9, z); g.add(r);
  }
  for (const x of [-3.2, 3.2]){
    const r = new THREE.Mesh(new THREE.BoxGeometry(.09, .09, 4.5), barMat);
    r.position.set(x, 2.9, 0); g.add(r);
  }
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  scene.add(g);
})();

/* hand-painted sign on the front bars */
(function makeSign(text){
  const c = document.createElement('canvas'); c.width = 512; c.height = 128;
  const ctx = c.getContext('2d');
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  function rr(x, y, w, h, r){
    ctx.beginPath();
    ctx.moveTo(x+r, y); ctx.arcTo(x+w, y, x+w, y+h, r); ctx.arcTo(x+w, y+h, x, y+h, r);
    ctx.arcTo(x, y+h, x, y, r); ctx.arcTo(x, y, x+w, y, r); ctx.closePath();
  }
  function draw(){
    ctx.clearRect(0, 0, 512, 128);
    ctx.fillStyle = '#fffdf7'; ctx.strokeStyle = '#33272a'; ctx.lineWidth = 10;
    rr(8, 8, 496, 112, 28); ctx.fill(); ctx.stroke();
    ctx.font = '600 54px Fredoka, sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = '#33272a';
    ctx.fillText(text, 256, 68);
    tex.needsUpdate = true;
  }
  draw();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(1.15, .29),
    new THREE.MeshBasicMaterial({ map:tex, transparent:true, side:THREE.DoubleSide }));
  m.position.set(0, .95, 2.32);
  scene.add(m);
})('SNACK ZONE');

/* ======================= INTERACTIVE OBJECTS ====================== */
const world = {
  wheel: null,
  wheelBusy(){
    return hamsters.some(h => ['toWheel','enterWheel','wheelRun','exitWheel'].includes(h.state));
  }
};

(function buildWheel(){
  const g = new THREE.Group(); g.position.copy(WHEEL_POS);
  const mint = mat(0x5fd0bb), white = mat(0xffffff), coral = mat(0xf2795f);
  const spin = new THREE.Group(); spin.position.y = .78; g.add(spin);

  const rim = new THREE.Mesh(new THREE.TorusGeometry(.68, .06, 8, 26), mint);
  spin.add(rim);
  for (let i = 0; i < 6; i++){
    const s = new THREE.Mesh(new THREE.CylinderGeometry(.026, .026, 1.3, 5), white);
    s.rotation.z = i * Math.PI/6;
    spin.add(s);
  }
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(.1, .1, .14, 8), white);
  hub.rotation.x = Math.PI/2; spin.add(hub);

  const base = new THREE.Mesh(new THREE.BoxGeometry(.75, .08, .42), coral);
  base.position.set(0, .04, -.4); g.add(base);
  const post = new THREE.Mesh(new THREE.BoxGeometry(.11, .74, .11), coral);
  post.position.set(0, .43, -.56); g.add(post);
  const arm = new THREE.Mesh(new THREE.CylinderGeometry(.035, .035, .58, 6), coral);
  arm.rotation.x = Math.PI/2; arm.position.set(0, .78, -.28); g.add(arm);
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, .5, 6), mat(0x8d95a3));
  axle.rotation.x = Math.PI/2; g.add(axle);

  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  scene.add(g);
  world.wheel = { g, spin, speed:0, target:0 };
})();

const SEED_GEO = new THREE.SphereGeometry(.05, 5, 4);
SEED_GEO.scale(.7, 1.25, .7);
const SEED_MAT = mat(0xe0a63e);

(function buildBowl(){
  const g = new THREE.Group(); g.position.copy(BOWL_POS);
  const outer = new THREE.Mesh(new THREE.CylinderGeometry(.42, .3, .24, 10), mat(0xf25c54));
  outer.position.y = .12; g.add(outer);
  const food = new THREE.Mesh(new THREE.SphereGeometry(.3, 7, 5), mat(0xd9a441));
  food.scale.set(1, .35, 1); food.position.y = .2; g.add(food);
  for (let i = 0; i < 4; i++){
    const s = new THREE.Mesh(SEED_GEO, SEED_MAT);
    s.position.set(rand(-.15, .15), .27, rand(-.15, .15));
    s.rotation.y = rand(0, 3); g.add(s);
  }
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  scene.add(g);
})();

(function buildTunnel(){
  const geo = new THREE.CylinderGeometry(.55, .55, 1.5, 10, 1, true, -Math.PI/2, Math.PI);
  geo.rotateX(-Math.PI/2); geo.rotateY(Math.PI/2);
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color:0xffd166, flatShading:true, side:THREE.DoubleSide, roughness:.9
  }));
  m.position.set(.4, FLOOR_Y, -1.55);
  m.castShadow = true;
  scene.add(m);
})();

/* ============================== SEEDS ============================= */
const seeds = [];
let munched = 0;

function spawnSeed(x, z){
  x = clamp(x, BX.min + .1, BX.max - .1);
  z = clamp(z, BZ.min + .1, BZ.max - .1);
  if (seeds.length >= 6) removeSeed(seeds[0]);
  const m = new THREE.Mesh(SEED_GEO, SEED_MAT);
  m.position.set(x, FLOOR_Y + .05, z);
  m.rotation.y = Math.random()*Math.PI;
  m.castShadow = true;
  m.userData = { pop:0, shrink:1, claimed:false };
  scene.add(m); seeds.push(m);
  claim(m);
}
function removeSeed(m){
  const i = seeds.indexOf(m);
  if (i >= 0) seeds.splice(i, 1);
  scene.remove(m);
  for (const h of hamsters){
    if (h.seedRef === m){
      h.seedRef = null;
      if (h.state === 'toSeed'){ h.state = 'wander'; h.pickTarget(); }
    }
  }
}
function claim(m){
  let best = null, bd = 1e9;
  for (const h of hamsters){
    if (h.seedRef) continue;
    if (!['idle','wander','toSeed'].includes(h.state)) continue;
    const d = Math.hypot(h.pos.x - m.position.x, h.pos.z - m.position.z);
    if (d < bd){ bd = d; best = h; }
  }
  if (best){
    m.userData.claimed = true;
    best.seedRef = m;
    const d = best.pos.clone().sub(m.position); d.y = 0;
    if (d.lengthSq() < .001) d.set(1, 0, 0);
    d.normalize();
    best.target.copy(m.position).addScaledVector(d, .34);
    best.state = 'toSeed';
    best.mood = 'SEED?!';
  }
}
seedBtn.addEventListener('click', () => spawnSeed(rand(-2.4, 2.4), rand(-1.4, 1.4)));

/* ============================ HAMSTERS ============================ */
function buildHamster(style){
  const g = new THREE.Group();
  const bodyMat = mat(style.body), bellyMat = mat(style.belly),
        pinkMat = mat(style.pink), footMat = mat(style.foot);

  const torso = new THREE.Group(); g.add(torso);
  const body = new THREE.Mesh(S(.32, 9, 7), bodyMat);
  body.scale.set(1.05, .92, 1.2); body.position.set(0, .3, -.05); torso.add(body);
  const belly = new THREE.Mesh(S(.26, 8, 6), bellyMat);
  belly.scale.set(.85, .7, .9); belly.position.set(0, .21, .16); torso.add(belly);
  const tail = new THREE.Mesh(S(.05, 5, 4), pinkMat);
  tail.position.set(0, .24, -.46); torso.add(tail);

  const head = new THREE.Group(); head.position.set(0, .36, .26); g.add(head);
  head.add(new THREE.Mesh(S(.23, 8, 6), bodyMat));
  const muzzle = new THREE.Mesh(S(.12, 6, 5), bellyMat);
  muzzle.scale.set(1, .8, .9); muzzle.position.set(0, -.06, .15); head.add(muzzle);
  const nose = new THREE.Mesh(S(.035, 6, 4), pinkMat);
  nose.position.set(0, -.02, .26); head.add(nose);

  const eyes = [], ears = [], cheeks = [];
  const eyeMat = mat(0x2b2320), glintMat = mat(0xffffff);
  for (const s of [-1, 1]){
    const e = new THREE.Mesh(S(.042, 6, 4), eyeMat);
    e.position.set(.115*s, .055, .185); head.add(e); eyes.push(e);
    const gl = new THREE.Mesh(S(.014, 4, 3), glintMat);
    gl.position.set(.1*s, .075, .215); head.add(gl);
    const ear = new THREE.Mesh(S(.085, 6, 4), bodyMat);
    ear.scale.set(1, 1, .6); ear.position.set(.15*s, .19, -.02); head.add(ear); ears.push(ear);
    const earIn = new THREE.Mesh(S(.05, 6, 4), pinkMat);
    earIn.scale.set(1, 1, .5); earIn.position.set(.15*s, .19, .015); head.add(earIn);
    const cheek = new THREE.Mesh(S(.1, 6, 5), bodyMat);
    cheek.position.set(.155*s, -.07, .12); head.add(cheek); cheeks.push(cheek);
  }
  const wpts = [];
  for (const s of [-1, 1]){
    wpts.push(new THREE.Vector3(.05*s, -.05, .24), new THREE.Vector3(.24*s, -.01, .27));
    wpts.push(new THREE.Vector3(.05*s, -.09, .24), new THREE.Vector3(.24*s, -.13, .26));
  }
  head.add(new THREE.LineSegments(
    new THREE.BufferGeometry().setFromPoints(wpts),
    new THREE.LineBasicMaterial({ color:0xffffff, transparent:true, opacity:.75 })
  ));

  const feet = [];
  for (const [sx, sz] of [[-1, 1], [1, 1], [-1, -1], [1, -1]]){
    const f = new THREE.Mesh(S(.06, 5, 4), footMat);
    f.scale.set(1, .7, 1.3); f.position.set(.13*sx, .05, .24*sz);
    g.add(f); feet.push(f);
  }

  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  return { g, torso, head, eyes, ears, cheeks, feet };
}

class Hamster {
  constructor(style, x, z){
    this.name = style.name;
    this.parts = buildHamster(style);
    this.group = this.parts.g;
    scene.add(this.group);
    this.pos = new THREE.Vector3(x, FLOOR_Y, z);
    this.rotY = Math.random()*Math.PI*2;
    this.state = 'idle';
    this.timer = .8 + Math.random()*1.5;
    this.dur = 0;
    this.target = new THREE.Vector3(x, FLOOR_Y, z);
    this.from = new THREE.Vector3();
    this.exitTo = new THREE.Vector3();
    this.walkPhase = Math.random()*10;
    this.puff = 0; this.airY = 0; this.hopY = 0; this.jv = 0;
    this.wheelCd = 1.5 + Math.random()*4;
    this.bowlCd  = 1 + Math.random()*3;
    this.blinkT  = 1 + Math.random()*3;
    this.earTw = 0; this.earSide = 1;
    this.seedRef = null;
    this.phase = Math.random()*10;
    this.boopT = 0;
    this.mood = 'daydreaming';
  }

  pickTarget(){
    for (let i = 0; i < 8; i++){
      const x = rand(BX.min, BX.max), z = rand(BZ.min, BZ.max);
      if (Math.hypot(x - this.pos.x, z - this.pos.z) > 1.1){
        this.target.set(x, FLOOR_Y, z); break;
      }
    }
  }

  decide(){
    const r = Math.random();
    if (r < .3 && this.wheelCd <= 0 && !world.wheelBusy()){
      this.state = 'toWheel'; this.mood = 'WHEEL TIME';
    } else if (r < .55 && this.bowlCd <= 0){
      const d = this.pos.clone().sub(BOWL_POS); d.y = 0;
      if (d.lengthSq() < .01) d.set(1, 0, 0);
      d.normalize();
      this.target.copy(BOWL_POS).addScaledVector(d, .62);
      this.state = 'toBowl'; this.mood = 'snack time';
    } else {
      const free = seeds.find(s => !s.userData.claimed);
      if (free && Math.random() < .7){
        free.userData.claimed = true;
        this.seedRef = free;
        const d = this.pos.clone().sub(free.position); d.y = 0;
        if (d.lengthSq() < .001) d.set(1, 0, 0);
        d.normalize();
        this.target.copy(free.position).addScaledVector(d, .34);
        this.state = 'toSeed'; this.mood = 'SEED?!';
      } else {
        this.pickTarget();
        this.state = 'wander'; this.mood = 'on a mission';
      }
    }
  }

  stepTo(tp, dt, mult = 1){
    const dx = tp.x - this.pos.x, dz = tp.z - this.pos.z;
    const d = Math.hypot(dx, dz);
    if (d < .001) return false;
    const sp = SPEED * mult;
    this.rotY = dampAngle(this.rotY, Math.atan2(dx, dz), 9, dt);
    const step = Math.min(sp*dt, d);
    this.pos.x += dx/d*step; this.pos.z += dz/d*step;
    this.walkPhase += dt*sp*7;
    return true;
  }
  arrived(tp, r){ return Math.hypot(tp.x - this.pos.x, tp.z - this.pos.z) < r; }
  facePoint(p, dt){
    this.rotY = dampAngle(this.rotY, Math.atan2(p.x - this.pos.x, p.z - this.pos.z), 12, dt);
  }
  avoid(){
    const obs = [
      { p:WHEEL_POS, r:.75, skip:['toWheel','enterWheel','wheelRun','exitWheel'] },
      { p:BOWL_POS,  r:.6,  skip:['toBowl','eat'] }
    ];
    for (const o of obs){
      if (o.skip.includes(this.state)) continue;
      const dx = this.pos.x - o.p.x, dz = this.pos.z - o.p.z;
      const d = Math.hypot(dx, dz);
      if (d < o.r && d > .001){
        const push = (o.r - d) * .6;
        this.pos.x += dx/d*push; this.pos.z += dz/d*push;
      }
    }
  }

  update(dt, t){
    this.wheelCd -= dt; this.bowlCd -= dt;
    this.puff = Math.max(0, this.puff - dt*.3);
    this.boopT = Math.max(0, this.boopT - dt);
    this.blinkT -= dt;
    if (this.blinkT < 0) this.blinkT = 2 + Math.random()*3;
    const blinking = this.blinkT < .12;
    if (this.earTw > 0) this.earTw -= dt;
    else if (Math.random() < dt*.3){ this.earTw = .3; this.earSide = Math.random() < .5 ? -1 : 1; }

    let moving = false;
    switch (this.state){
      case 'idle':
        this.timer -= dt;
        if (this.timer <= 0) this.decide();
        break;
      case 'wander':
        moving = this.stepTo(this.target, dt);
        if (this.arrived(this.target, .18)){ this.state = 'idle'; this.timer = 1 + Math.random()*2.5; }
        break;
      case 'toWheel':
        moving = this.stepTo(WHEEL_POS, dt);
        if (this.arrived(WHEEL_POS, .22)){ this.state = 'enterWheel'; this.dur = 0; this.from.copy(this.pos); }
        break;
      case 'enterWheel': {
        this.dur += dt/.45;
        const k = Math.min(1, this.dur);
        this.pos.lerpVectors(this.from, WHEEL_POS, ease(k));
        this.airY = Math.sin(k*Math.PI)*.28;
        this.rotY = dampAngle(this.rotY, Math.PI/2, 12, dt);
        if (k >= 1){
          this.state = 'wheelRun'; this.dur = 3 + Math.random()*3;
          world.wheel.target = 9; this.mood = 'SPINNING!';
        }
        break;
      }
      case 'wheelRun':
        this.dur -= dt;
        this.walkPhase += dt*16;
        this.rotY = dampAngle(this.rotY, Math.PI/2, 12, dt);
        if (this.dur <= 0){
          this.state = 'exitWheel'; this.dur = 0; this.from.copy(this.pos);
          this.exitTo.copy(WHEEL_POS).add(new THREE.Vector3(.85, 0, .55));
        }
        break;
      case 'exitWheel': {
        this.dur += dt/.5;
        const k = Math.min(1, this.dur);
        this.pos.lerpVectors(this.from, this.exitTo, ease(k));
        this.airY = Math.sin(k*Math.PI)*.3;
        if (k >= 1){
          this.airY = 0; this.state = 'idle'; this.timer = .6;
          this.wheelCd = 6 + Math.random()*7;
          world.wheel.target = 0; this.mood = 'phew.';
        }
        break;
      }
      case 'toBowl':
        moving = this.stepTo(this.target, dt);
        if (this.arrived(this.target, .16)){ this.state = 'eat'; this.dur = 2 + Math.random()*2; this.mood = 'nom nom'; }
        break;
      case 'eat':
        this.facePoint(BOWL_POS, dt);
        this.dur -= dt;
        this.puff = Math.min(1, this.puff + dt*.5);
        if (this.dur <= 0){ this.state = 'idle'; this.timer = 1 + Math.random()*2; this.bowlCd = 4 + Math.random()*5; }
        break;
      case 'toSeed':
        if (!this.seedRef || !this.seedRef.parent){ this.state = 'wander'; this.pickTarget(); break; }
        moving = this.stepTo(this.target, dt, 1.25);
        if (this.arrived(this.target, .14)){ this.state = 'eatSeed'; this.dur = 1.8; this.mood = 'CRUNCH'; }
        break;
      case 'eatSeed':
        if (!this.seedRef){ this.state = 'idle'; this.timer = 1; break; }
        this.facePoint(this.seedRef.position, dt);
        this.dur -= dt;
        this.puff = Math.min(1, this.puff + dt*.7);
        this.seedRef.userData.shrink = Math.max(0, 1 - (1.8 - this.dur)/1.4);
        if (this.dur <= 0){
          const s = this.seedRef; this.seedRef = null;
          removeSeed(s);
          munched++;
          counterEl.textContent = 'munched: ' + munched;
          this.state = 'idle'; this.timer = 1 + Math.random()*2;
        }
        break;
    }

    if (this.hopY > 0 || this.jv > 0){
      this.hopY += this.jv*dt; this.jv -= 14*dt;
      if (this.hopY <= 0){ this.hopY = 0; this.jv = 0; }
    }

    if (moving){
      this.avoid();
      this.pos.x = clamp(this.pos.x, BX.min, BX.max);
      this.pos.z = clamp(this.pos.z, BZ.min, BZ.max);
    }

    this.visuals(dt, t, moving, blinking);
  }

  visuals(dt, t, moving, blinking){
    const P = this.parts;
    let bob = 0;
    if (moving) bob = Math.abs(Math.sin(this.walkPhase))*.04;
    else if (this.state === 'wheelRun') bob = Math.abs(Math.sin(this.walkPhase))*.05;
    this.group.position.set(this.pos.x, FLOOR_Y + bob + this.airY + this.hopY, this.pos.z);
    this.group.rotation.y = this.rotY;

    const lean = this.state === 'wheelRun' ? .18 : 0;
    P.torso.rotation.x = damp(P.torso.rotation.x, lean, 8, dt);
    let sy = 1 + Math.sin(t*2.4 + this.phase)*.025;
    if (this.hopY > .01) sy *= 1.18;
    P.torso.scale.set(1, sy, 1);

    let hx = 0;
    if (this.state === 'eat' || this.state === 'eatSeed') hx = .55 + Math.sin(this.dur*14)*.15;
    else if (this.state === 'wheelRun') hx = .15;
    P.head.rotation.x = damp(P.head.rotation.x, hx, 10, dt);
    P.head.rotation.z = moving ? Math.sin(this.walkPhase)*.06 : damp(P.head.rotation.z, 0, 8, dt);

    const es = blinking ? .12 : 1;
    for (const e of P.eyes) e.scale.y += (es - e.scale.y)*Math.min(1, dt*30);

    const mag = this.earTw > 0 ? Math.sin((.3 - this.earTw)/.3*Math.PI)*.55 : 0;
    P.ears[0].rotation.z = damp(P.ears[0].rotation.z, this.earSide === -1 ? mag : 0, 18, dt);
    P.ears[1].rotation.z = damp(P.ears[1].rotation.z, this.earSide ===  1 ? mag : 0, 18, dt);

    const offs = [0, Math.PI, Math.PI, 0];
    const run = moving || this.state === 'wheelRun';
    for (let i = 0; i < 4; i++){
      const lift = Math.max(0, Math.sin(this.walkPhase + offs[i])) * .05 * (run ? 1 : .2);
      P.feet[i].position.y = .05 + lift;
    }

    const cs = 1 + this.puff*.85;
    for (const c of P.cheeks) c.scale.set(cs, cs, cs);
  }
}

const hamsters = [
  new Hamster({ name:'Mochi',   body:0xf2ae5c, belly:0xffe9c6, pink:0xff9d9d, foot:0xd97b5f },  .8,  .3),
  new Hamster({ name:'Snowy',   body:0xf5f1ea, belly:0xffffff, pink:0xff9d9d, foot:0xe8a0a0 },  -.5,  .8),
  new Hamster({ name:'Ash',     body:0xaeb6c2, belly:0xe9edf2, pink:0xff9d9d, foot:0x8d95a3 },  1.5, -.6),
  new Hamster({ name:'Cocoa',   body:0xa9744f, belly:0xe8cfae, pink:0xff9d9d, foot:0x8a5a3b },  -.8, -.3),
];

const hitMeshes = [];
for (const h of hamsters){
  h.group.traverse(o => { if (o.isMesh){ o.userData.hamster = h; hitMeshes.push(o); } });
}

/* =========================== INTERACTION ========================== */
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const _v = new THREE.Vector3();
function setMouse(e){
  mouse.x = (e.clientX/innerWidth)*2 - 1;
  mouse.y = -(e.clientY/innerHeight)*2 + 1;
}

let lastBooped = null;
const boopWords = ['boop!', 'wheek!', 'hehe ♪', '*happy squeak*', 'boing!'];
function boop(h){
  if (h.hopY <= .01 && h.jv <= 0) h.jv = 3.6;
  h.boopT = .9;
  lastBooped = h;
  bubbleEl.textContent = boopWords[Math.floor(Math.random()*boopWords.length)];
}

renderer.domElement.addEventListener('pointermove', e => {
  setMouse(e);
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(hitMeshes, false);
  if (hits.length){
    const h = hits[0].object.userData.hamster;
    tipEl.innerHTML = '<b>' + h.name + '</b> · ' + h.mood;
    tipEl.style.left = e.clientX + 'px';
    tipEl.style.top  = (e.clientY - 16) + 'px';
    tipEl.style.opacity = 1;
    renderer.domElement.style.cursor = 'pointer';
  } else {
    tipEl.style.opacity = 0;
    renderer.domElement.style.cursor = '';
  }
});

let downX = 0, downY = 0, downT = 0;
renderer.domElement.addEventListener('pointerdown', e => {
  downX = e.clientX; downY = e.clientY; downT = performance.now();
});
window.addEventListener('pointerup', e => {
  if (performance.now() - downT > 350 || Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return;
  setMouse(e);
  raycaster.setFromCamera(mouse, camera);
  const hh = raycaster.intersectObjects(hitMeshes, false);
  if (hh.length){ boop(hh[0].object.userData.hamster); return; }
  const hs = raycaster.intersectObject(sandMesh, false);
  if (hs.length) spawnSeed(hs[0].point.x, hs[0].point.z);
});

/* ============================== LOOP ============================== */
spawnSeed(-1.2, .9);
spawnSeed(1.6, -.9);

const clock = new THREE.Clock();
function tick(){
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), .05);
  const t = clock.elapsedTime;

  for (const h of hamsters) h.update(dt, t);

  const w = world.wheel;
  w.speed += (w.target - w.speed)*Math.min(1, dt*2.5);
  w.spin.rotation.z -= w.speed*dt;

  for (const s of seeds){
    const u = s.userData;
    u.pop = Math.min(1, u.pop + dt*6);
    s.scale.setScalar(Math.max(.001, u.pop*u.shrink));
  }

  for (const c of clouds){
    c.position.x += c.userData.v*dt;
    if (c.position.x > 26) c.position.x = -26;
  }
  sun.rotation.z += dt*.15;

  if (lastBooped && lastBooped.boopT > 0){
    _v.set(lastBooped.pos.x, FLOOR_Y + 1 + lastBooped.hopY, lastBooped.pos.z).project(camera);
    const sx = (_v.x*.5 + .5)*innerWidth;
    const sy = (-_v.y*.5 + .5)*innerHeight;
    bubbleEl.style.transform = 'translate(' + sx + 'px,' + sy + 'px) translate(-50%,-100%)';
    bubbleEl.style.opacity = Math.min(1, lastBooped.boopT*2);
  } else {
    bubbleEl.style.opacity = 0;
  }

  controls.autoRotate = performance.now() - lastUser > 8000;
  controls.update();
  renderer.render(scene, camera);
}
tick();

window.addEventListener('resize', () => {
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

**What's in the pen**

- **The cage** — a white tray with sand, coral wire bars, corner posts, and a hand-painted "SNACK ZONE" sign on the front.
- **Four hamsters** (Mochi, Snowy, Ash, Cocoa) built from flat-shaded primitives with whiskers, blinking, ear twitches, and cheek-puffing after meals.
- **Autonomous behavior** — each runs a small state machine: wander → pause → decide. They take turns claiming the **running wheel** (climb in, sprint, wheel spins, hop out), queue at the **food bowl**, and race to whatever seed you toss.
- **Interactive bits** — drag to orbit (auto-rotates gently when idle), scroll to zoom, click the sand or the 🌻 button to toss a seed, click a hamster to boop it (it jumps with a speech bubble), and hover any hamster for its name and current mood.
- **The yard** — a grassy island with trees, flowers, drifting low-poly clouds, and a spinning icosahedron sun.

No build step, no assets — just open the file and watch the little guys work.