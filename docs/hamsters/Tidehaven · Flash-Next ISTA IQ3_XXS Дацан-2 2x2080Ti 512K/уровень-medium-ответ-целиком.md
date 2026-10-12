# Tidehaven 🏝️

A complete single-file interactive 3D diorama. Save as `index.html` and open in any modern browser. Everything is procedural — no external assets.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Tidehaven — a coastal diorama</title>
<style>
  :root{
    --panel: rgba(18,28,34,.55);
    --panel-border: rgba(255,255,255,.12);
    --text:#eaf4f2; --muted:#9fb8b4; --accent:#7fd8c9; --accent-dark:#2f8f7d;
  }
  *{box-sizing:border-box; margin:0; padding:0;}
  html,body{height:100%; overflow:hidden; background:#0c1418;
    font-family:'Segoe UI', system-ui, -apple-system, sans-serif; color:var(--text);}
  canvas{display:block;}
  #underwater-tint{position:fixed; inset:0; pointer-events:none; opacity:0;
    background:radial-gradient(circle at 50% 55%, rgba(20,120,130,.05), rgba(10,70,90,.38));
    transition:opacity .9s ease; z-index:2;}

  /* ---------- Title ---------- */
  #title{position:fixed; top:18px; left:20px; z-index:10; pointer-events:none;
    text-shadow:0 2px 14px rgba(0,0,0,.5);}
  #title h1{font-size:30px; font-weight:600; letter-spacing:4px; color:#f4efe4;}
  #title h1 span{color:var(--accent);}
  #title p{font-size:12.5px; color:var(--muted); letter-spacing:1.5px; margin-top:2px;}

  /* ---------- Panels ---------- */
  #ui{position:fixed; top:16px; right:16px; z-index:10; width:248px;
    display:flex; flex-direction:column; gap:10px; max-height:calc(100vh - 32px); overflow-y:auto;
    scrollbar-width:none;}
  #ui::-webkit-scrollbar{display:none;}
  .panel{background:var(--panel); border:1px solid var(--panel-border); border-radius:12px;
    padding:12px 14px; backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);}
  .panel h3{font-size:10.5px; text-transform:uppercase; letter-spacing:2px; color:var(--accent);
    margin-bottom:9px; font-weight:600;}
  .row{display:flex; gap:7px; flex-wrap:wrap;}
  button{flex:1; min-width:60px; background:rgba(255,255,255,.07); color:var(--text);
    border:1px solid rgba(255,255,255,.14); border-radius:8px; padding:8px 6px; font-size:12px;
    cursor:pointer; transition:all .2s; font-family:inherit; letter-spacing:.4px;}
  button:hover{background:rgba(255,255,255,.15);}
  button.active{background:var(--accent-dark); border-color:var(--accent); color:#fff;
    box-shadow:0 0 12px rgba(127,216,201,.35);}
  .slider-row{display:flex; align-items:center; gap:10px; margin:6px 0;}
  .slider-row label{font-size:11.5px; color:var(--muted); width:42px;}
  input[type=range]{flex:1; -webkit-appearance:none; height:4px; border-radius:2px;
    background:rgba(255,255,255,.22); outline:none;}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none; width:15px; height:15px;
    border-radius:50%; background:var(--accent); cursor:pointer; box-shadow:0 0 8px rgba(127,216,201,.5);}
  input[type=range]::-moz-range-thumb{width:15px; height:15px; border:none; border-radius:50%;
    background:var(--accent); cursor:pointer;}
  .val{font-size:11px; color:var(--accent); width:34px; text-align:right;}

  #menuBtn{display:none; position:fixed; top:18px; right:18px; z-index:11; flex:none;
    width:42px; height:42px; min-width:42px; font-size:18px; border-radius:10px;}

  @media (max-width:760px){
    #title h1{font-size:22px;} #title{top:12px; left:14px;}
    #menuBtn{display:block;}
    #ui{top:66px; left:10px; right:10px; width:auto; transform:translateY(-140%);
      transition:transform .35s ease; max-height:70vh;}
    #ui.open{transform:none;}
    #ui .panel{padding:10px 12px;}
  }
</style>
</head>
<body>

<div id="title">
  <h1>TIDE<span>HAVEN</span></h1>
  <p>a cozy island above · a living lagoon below</p>
</div>

<button id="menuBtn">☰</button>
<div id="underwater-tint"></div>

<div id="ui">
  <div class="panel">
    <h3>View</h3>
    <div class="row">
      <button id="camIso" class="active">Isometric</button>
      <button id="camCozy">Cabin &amp; Pier</button>
      <button id="camUnder">Underwater</button>
    </div>
  </div>
  <div class="panel">
    <h3>Actions</h3>
    <div class="row">
      <button id="kayakBtn">Launch kayak</button>
      <button id="rayBtn">Ray leap</button>
    </div>
  </div>
  <div class="panel">
    <h3>Environment</h3>
    <div class="slider-row"><label>Tide</label><input id="tide" type="range" min="-0.6" max="1.0" step="0.01" value="0.25"><span class="val" id="tideVal">0.25</span></div>
    <div class="slider-row"><label>Wind</label><input id="wind" type="range" min="0" max="1.5" step="0.01" value="0.6"><span class="val" id="windVal">0.6</span></div>
    <div class="row" style="margin-top:8px">
      <button id="todDay" class="active">Day</button>
      <button id="todSunset">Sunset</button>
      <button id="todNight">Night</button>
    </div>
  </div>
  <div class="panel">
    <h3>Playback &amp; Audio</h3>
    <div class="row">
      <button id="pauseBtn">Pause</button>
      <button id="resetBtn">Reset</button>
      <button id="musicBtn">Music ✕</button>
    </div>
    <div class="slider-row"><label>Volume</label><input id="volume" type="range" min="0" max="1" step="0.01" value="0.7"><span class="val" id="volVal">70%</span></div>
  </div>
</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* =========================================================================
   TIDEHAVEN — procedural coastal diorama
   Layout: island inside an aquarium box. Water volume + animated surface
   + caustics + glass walls, sorted with explicit renderOrder & depthWrite
   false to avoid transparency artifacts.
   ========================================================================= */

// ---------------- Renderer / Scene / Camera ----------------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const MOBILE = /Mobi|Android/i.test(navigator.userAgent) || innerWidth < 760;
renderer.setPixelRatio(Math.min(devicePixelRatio, MOBILE ? 1 : 1.75));

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.1, 200);
camera.position.set(13, 10, 13);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.06;
controls.minDistance = 4; controls.maxDistance = 40;
controls.maxPolarAngle = 2.75;
controls.target.set(0, 0.5, 0);

// ---------------- World constants ----------------
const BOX = { hx: 9, hz: 7, top: 4, bottom: -3 };     // aquarium footprint
const ISL = { R: 6.4, H: 5.4, base: -3, ez: 0.8 };    // island profile (ellipse in z)
const SAND = 0xe6d3a3, SAND_WET = 0xc9b489, GRASS = 0x6fae64;

// Shared animation uniforms (used by wind-sway shaders)
const uTime = { value: 0 }, uWind = { value: 0.6 };

// World state
const state = {
  tide: 0.25, wind: 0.6, paused: false,
  tod: 'day', todT: 1,          // transition progress
  time: 0,
};

// ---------------- Lighting ----------------
const hemi = new THREE.HemisphereLight(0xbfdfe9, 0xd9c49a, 0.7);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2d9, 1.6);
sun.position.set(11, 17, 9);
sun.castShadow = true;
sun.shadow.mapSize.set(MOBILE ? 1024 : 2048, MOBILE ? 1024 : 2048);
sun.shadow.camera.left = -13; sun.shadow.camera.right = 13;
sun.shadow.camera.top = 13; sun.shadow.camera.bottom = -13;
sun.shadow.camera.near = 1; sun.shadow.camera.far = 60;
sun.shadow.bias = -0.0008;
scene.add(sun);

const warmL1 = new THREE.PointLight(0xffb46a, 0, 9, 2); warmL1.position.set(0.2, 2.3, 1.4);
const warmL2 = new THREE.PointLight(0xffc477, 0, 8, 2); warmL2.position.set(0.8, 1.6, 4.6);
scene.add(warmL1, warmL2);

const TIME_PRESETS = {
  day:    { bg:0xcfe6ef, sunC:0xfff2d9, sunI:1.6, hSky:0xbfdfe9, hGnd:0xd9c49a, hI:0.7, glow:0.15, lamp:0,   deep:0x1f8f96, shallow:0x5fc9c2, caustic:1.0 },
  sunset: { bg:0xf0b285, sunC:0xff9a5c, sunI:1.25,hSky:0xe8a477, hGnd:0x8a5a44, hI:0.55,glow:0.9,  lamp:0.7, deep:0x2c6f86, shallow:0x8fb0a8, caustic:0.7 },
  night:  { bg:0x0e1826, sunC:0x9db8d8, sunI:0.28,hSky:0x24344d, hGnd:0x14202c, hI:0.38,glow:1.8,  lamp:1.4, deep:0x0e4a58, shallow:0x2a7c82, caustic:0.35 },
};
let todFrom = {...TIME_PRESETS.day}, todTo = {...TIME_PRESETS.day};
scene.background = new THREE.Color(TIME_PRESETS.day.bg);

// Helper colors for lerping
const cFrom = {}, cTo = {};
function setTod(name){
  todFrom = snapshotTod(); todTo = TIME_PRESETS[name]; todT = 0; state.tod = name;
}
function snapshotTod(){
  return { bg: scene.background.getHex(), sunC: sun.color.getHex(), sunI: sun.intensity,
    hSky: hemi.color.getHex(), hGnd: hemi.groundColor.getHex(), hI: hemi.intensity,
    glow: glowMats[0] ? glowMats[0].emissiveIntensity : 1, lamp: warmL1.intensity,
    deep: waterVol.material.color.getHex(), shallow: surfMat.uniforms.uShallow.value.getHex(),
    caustic: causticMat.uniforms.uIntensity.value };
}
const _a = new THREE.Color(), _b = new THREE.Color();
function lerpTod(dt){
  if (todT >= 1) return;
  todT = Math.min(1, todT + dt / 1.8);
  const t = todT*todT*(3-2*todT);
  const mix = (k, apply) => { apply(new THREE.Color(todFrom[k]).lerp(_b.setHex ? _b.setHex(todTo[k]) : _b, t)); };
  const lerpC = (k, fn) => { _a.setHex(todFrom[k]); _b.setHex(todTo[k]); fn(_a.lerp(_b, t)); };
  const lerpN = (k, fn) => fn(THREE.MathUtils.lerp(todFrom[k], todTo[k], t));
  lerpC('bg', c => scene.background.copy(c));
  lerpC('sunC', c => sun.color.copy(c));
  lerpC('hSky', c => hemi.color.copy(c));
  lerpC('hGnd', c => hemi.groundColor.copy(c));
  lerpC('deep', c => { waterVol.material.color.copy(c); });
  lerpC('shallow', c => surfMat.uniforms.uShallow.value.copy(c));
  lerpN('sunI', v => sun.intensity = v);
  lerpN('hI', v => hemi.intensity = v);
  lerpN('glow', v => glowMats.forEach(m => m.emissiveIntensity = v));
  lerpN('lamp', v => { warmL1.intensity = v; warmL2.intensity = v*0.8; });
  lerpN('caustic', v => causticMat.uniforms.uIntensity.value = v);
}

// ---------------- Materials (shared) ----------------
const matWood  = new THREE.MeshStandardMaterial({ color: 0x8a6746, roughness: .8 });
const matWoodD = new THREE.MeshStandardMaterial({ color: 0x5c4630, roughness: .85 });
const matCopper= new THREE.MeshStandardMaterial({ color: 0xb87333, roughness: .32, metalness: .65 });
const matRock  = new THREE.MeshStandardMaterial({ color: 0x7d8288, roughness: .95 });
const matSand  = new THREE.MeshStandardMaterial({ color: SAND_WET, roughness: 1 });
const glowMats = [];
function glowMat(){ const m = new THREE.MeshStandardMaterial({ color:0x3a2c1c, emissive:0xffb45e, emissiveIntensity:0.15, roughness:.6 }); glowMats.push(m); return m; }

// ---------------- Island (procedural heightfield with vertex colors) ----------------
function islandH(x, z){                       // ellipse-scaled radial height
  const r = Math.sqrt(x*x + (z/ISL.ez)*(z/ISL.ez));
  if (r >= ISL.R) return ISL.base;
  return ISL.base + ISL.H * Math.pow(1 - (r/ISL.R)**2, 1.5);
}
function shoreRadius(level){                  // island radius at a given water level
  const f = Math.min(1, Math.max(0, ((level - ISL.base) / ISL.H) ** (2/3)));
  return ISL.R * Math.sqrt(Math.max(0, 1 - f));
}

function buildIsland(){
  const rings = 40, segs = 72, maxR = 8.2;
  const pos = [], col = [], idx = [];
  const cSand = new THREE.Color(SAND), cWet = new THREE.Color(SAND_WET),
        cGrass = new THREE.Color(GRASS), cGrass2 = new THREE.Color(0x5c9a55);
  for (let i = 0; i <= rings; i++){
    const r = (i/rings) * maxR;
    for (let j = 0; j <= segs; j++){
      const a = (j/segs) * Math.PI * 2;
      const x = Math.cos(a) * r, z = Math.sin(a) * r * ISL.ez;
      let h = islandH(x, z);
      // gentle noise bumps above the waterline
      if (h > -0.4){ h += Math.sin(x*1.7)*Math.cos(z*2.1)*0.14 + Math.sin(x*4.3+z*3.7)*0.05; }
      pos.push(x, h, z);
      const c = new THREE.Color();
      if (h < -0.35) c.copy(cWet);
      else if (h < 0.55) c.lerpColors(cWet, cSand, (h+0.35)/0.9);
      else c.lerpColors(new THREE.Color(SAND), cGrass, Math.min(1,(h-0.55)/0.7));
      if (h > 0.9) c.lerp(cGrass2, 0.35 + 0.35*Math.sin(x*2.9+z*2.3));
      col.push(c.r, c.g, c.b);
    }
  }
  for (let i = 0; i < rings; i++) for (let j = 0; j < segs; j++){
    const a = i*(segs+1)+j, b = a+1, c2 = a+(segs+1), d = c2+1;
    idx.push(a,c2,b, b,c2,d);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  g.setIndex(idx); g.computeVertexNormals();
  const mesh = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors:true, roughness:1 }));
  mesh.castShadow = mesh.receiveShadow = true;
  return mesh;
}
scene.add(buildIsland());

// Seabed
const seabed = new THREE.Mesh(new THREE.PlaneGeometry(BOX.hx*2, BOX.hz*2), matSand);
seabed.rotation.x = -Math.PI/2; seabed.position.y = BOX.bottom; seabed.receiveShadow = true;
scene.add(seabed);

// ---------------- Rocks (InstancedMesh) ----------------
{
  const geo = new THREE.DodecahedronGeometry(1, 0);
  const rocks = new THREE.InstancedMesh(geo, matRock, 26);
  const d = new THREE.Object3D(); const rng = THREE.MathUtils.randFloat;
  for (let i = 0; i < 26; i++){
    const a = Math.random()*Math.PI*2;
    let x, z, s;
    if (i < 12){ // shore rocks
      const r = shoreRadius(0.25) + rng(-0.4, 0.9);
      x = Math.cos(a)*r; z = Math.sin(a)*r*ISL.ez; s = rng(0.25,0.6);
      d.position.set(x, islandH(x,z)-s*0.3, z);
    } else {     // seabed rocks
      x = rng(-8,8); z = rng(-6,6); s = rng(0.3,0.9);
      d.position.set(x, BOX.bottom + s*0.5, z);
    }
    d.rotation.set(Math.random()*3, Math.random()*3, Math.random()*3);
    d.scale.set(s, s*rng(0.5,0.9), s*rng(0.7,1.2));
    d.updateMatrix(); rocks.setMatrixAt(i, d.matrix);
  }
  rocks.castShadow = rocks.receiveShadow = true;
  scene.add(rocks);
}

// Wind-sway injection for instanced foliage
function addSway(mat, amp, speed){
  mat.onBeforeCompile = sh => {
    sh.uniforms.uTime = uTime; sh.uniforms.uWind = uWind;
    sh.vertexShader = 'uniform float uTime; uniform float uWind;\n' +
      sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      #ifdef USE_INSTANCING
        vec4 iwp = instanceMatrix * vec4(0.,0.,0.,1.);
        float ph = iwp.x*1.6 + iwp.z*2.2;
        float a = uWind * ${amp.toFixed(2)} * max(position.y, 0.0);
        transformed.x += sin(uTime*${speed.toFixed(1)} + ph + position.y*1.4) * a;
        transformed.z += cos(uTime*${(speed*0.8).toFixed(1)} + ph) * a * 0.55;
      #endif`);
  };
}

// ---------------- Grass (InstancedMesh + sway shader) ----------------
{
  const geo = new THREE.ConeGeometry(0.05, 0.55, 4, 1, true);
  geo.translate(0, 0.275, 0);
  const mat = new THREE.MeshStandardMaterial({ color: 0x79b05f, roughness: 1 });
  addSway(mat, 0.32, 2.4);
  const N = 380, grass = new THREE.InstancedMesh(geo, mat, N);
  const d = new THREE.Object3D(); const c = new THREE.Color();
  let placed = 0, guard = 0;
  while (placed < N && guard++ < 4000){
    const x = THREE.MathUtils.randFloatSpread(11), z = THREE.MathUtils.randFloatSpread(9);
    const h = islandH(x, z);
    if (h < 0.55) continue;
    d.position.set(x, h - 0.03, z);
    d.rotation.set(THREE.MathUtils.randFloatSpread(0.25), Math.random()*Math.PI, THREE.MathUtils.randFloatSpread(0.25));
    const s = THREE.MathUtils.randFloat(0.7, 1.5);
    d.scale.setScalar(s); d.updateMatrix();
    grass.setMatrixAt(placed, d.matrix);
    c.setHSL(0.28 + Math.random()*0.06, 0.45, 0.32 + Math.random()*0.14);
    grass.setColorAt(placed, c);
    placed++;
  }
  grass.count = placed; grass.castShadow = true;
  scene.add(grass);
}

// ---------------- Trees ----------------
const trees = [];
{
  const trunkGeo = new THREE.CylinderGeometry(0.09, 0.14, 1, 6);
  const leafGeo  = new THREE.ConeGeometry(0.7, 1.1, 7);
  const matTrunk = new THREE.MeshStandardMaterial({ color: 0x6b4a30, roughness: .9 });
  const matLeaf  = new THREE.MeshStandardMaterial({ color: 0x4e9147, roughness: .95 });
  const matLeaf2 = new THREE.MeshStandardMaterial({ color: 0x63a857, roughness: .95 });
  const spots = [[-2.4,-1.6],[2.2,-1.9],[-1.3,1.9],[1.8,1.2],[-3.2,0.8]];
  spots.forEach(([x,z], i) => {
    const g = new THREE.Group();
    const h = islandH(x, z);
    const s = THREE.MathUtils.randFloat(0.85, 1.25);
    const trunk = new THREE.Mesh(trunkGeo, matTrunk);
    trunk.position.y = 0.5; trunk.castShadow = true; g.add(trunk);
    for (let k = 0; k < 3; k++){
      const leaf = new THREE.Mesh(leafGeo, k%2 ? matLeaf : matLeaf2);
      leaf.position.y = 1.05 + k*0.55; leaf.scale.setScalar(1 - k*0.22);
      leaf.castShadow = true; g.add(leaf);
    }
    g.position.set(x, h - 0.05, z); g.scale.setScalar(s);
    g.userData.phase = i * 1.7;
    scene.add(g); trees.push(g);
  });
}

// ---------------- A-frame cabin ----------------
const cabin = new THREE.Group();
{
  const W = 2.5, D = 2.3, wallH = 0.55, roofH = 2.0;
  // Roof panels (copper A-frame)
  const slope = Math.hypot(W/2, roofH);
  const roofGeo = new THREE.BoxGeometry(slope + 0.18, 0.09, D + 0.28);
  const ang = Math.atan2(roofH, W/2);
  const rL = new THREE.Mesh(roofGeo, matCopper);
  rL.rotation.z = ang; rL.position.set(-W/4, wallH + roofH/2, 0);
  const rR = new THREE.Mesh(roofGeo, matCopper);
  rR.rotation.z = -ang; rR.position.set(W/4, wallH + roofH/2, 0);
  rL.castShadow = rR.castShadow = true; cabin.add(rL, rR);
  // Ridge cap
  const ridge = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.1, D + 0.34), matCopper);
  ridge.position.y = wallH + roofH + 0.02; ridge.castShadow = true; cabin.add(ridge);
  // Gable triangles (front & back)
  function gable(zPos){
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(
      [-W/2,0,0, W/2,0,0, 0,roofH,0], 3));
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, matWoodD);
    m.position.set(0, wallH, zPos); m.castShadow = true; return m;
  }
  cabin.add(gable(D/2), gable(-D/2));
  // Lower wall band
  const wall = new THREE.Mesh(new THREE.BoxGeometry(W*0.96, wallH, D*0.94), matWoodD);
  wall.position.y = wallH/2; wall.castShadow = true; cabin.add(wall);
  // Door + glowing windows on the front gable
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.95, 0.06), new THREE.MeshStandardMaterial({ color:0x7a5230, roughness:.8 }));
  door.position.set(0, 0.48, D/2 + 0.02); cabin.add(door);
  const winGeo = new THREE.BoxGeometry(0.42, 0.42, 0.06);
  const wm = glowMat();
  [[-0.62, 1.35], [0.62, 1.35]].forEach(([x,y]) => {
    const w = new THREE.Mesh(winGeo, wm);
    w.position.set(x, wallH + y*0.75, D/2 + 0.03); cabin.add(w);
  });
  // Side windows
  [[-W/2-0.02, 1.0, -0.55],[W/2+0.02, 1.0, -0.55]].forEach(([x,y,z]) => {
    const w = new THREE.Mesh(winGeo, wm); w.position.set(x,y,z); w.rotation.y = Math.PI/2; cabin.add(w);
  });
  // Chimney
  const chim = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.7, 0.24), matRock);
  chim.position.set(-0.75, wallH + roofH*0.72, -0.7); chim.castShadow = true; cabin.add(chim);
  // Lantern by the door
  const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.11, 10, 8), glowMat());
  lamp.position.set(0.55, 1.15, D/2 + 0.1); cabin.add(lamp);

  const cx = 0.2, cz = -0.6;
  cabin.position.set(cx, islandH(cx, cz) - 0.02, cz);
  scene.add(cabin);
}

// ---------------- Deck, pier, ladder, props ----------------
{
  // Deck
  const deck = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.14, 2.4), matWood);
  deck.position.set(0.2, 2.02, 1.35); deck.castShadow = deck.receiveShadow = true; scene.add(deck);
  // Deck posts
  [[-1.4,0.3],[1.6,0.3],[-1.4,2.4],[1.6,2.4]].forEach(([x,z]) => {
    const p = new THREE.Mesh(new THREE.CylinderGeometry(0.07,0.07,1.4,6), matWoodD);
    p.position.set(x, 1.4, z); p.castShadow = true; scene.add(p);
  });
  // Deck railing
  const rail = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.07, 0.07), matWood);
  rail.position.set(0.2, 2.6, 2.5); rail.castShadow = true; scene.add(rail);

  // Pier planks (extends toward +z)
  const pierY = 0.85;
  for (let i = 0; i < 9; i++){
    const plank = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.1, 0.46), matWood);
    plank.position.set(0.6, pierY, 2.6 + i*0.52);
    plank.castShadow = plank.receiveShadow = true; scene.add(plank);
  }
  // Pier piles down to the seabed
  [[-0.1,3.0],[1.3,3.0],[-0.1,5.0],[1.3,5.0],[-0.1,6.9],[1.3,6.9]].forEach(([x,z]) => {
    const pile = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.11, pierY - BOX.bottom, 7), matWoodD);
    pile.position.set(x, (pierY + BOX.bottom)/2, z); pile.castShadow = true; scene.add(pile);
  });
  // Pier lanterns
  [[-0.15, 6.6],[1.35, 6.6]].forEach(([x,z]) => {
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.06,1.1,6), matWoodD);
    post.position.set(x, pierY + 0.55, z); post.castShadow = true; scene.add(post);
    const orb = new THREE.Mesh(new THREE.SphereGeometry(0.13, 10, 8), glowMat());
    orb.position.set(x, pierY + 1.18, z); scene.add(orb);
  });
  // Ladder into the water
  const lad = new THREE.Group();
  [[-0.18,0],[0.18,0]].forEach(([x]) => {
    const rail2 = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.7, 0.06), matWood);
    rail2.position.set(x, -0.4, 0); lad.add(rail2);
  });
  for (let i = 0; i < 5; i++){
    const rung = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.05, 0.05), matWood);
    rung.position.set(0, 0.25 - i*0.34, 0); lad.add(rung);
  }
  lad.position.set(0.6, pierY, 7.0); lad.rotation.x = 0.18; scene.add(lad);

  // Bench on the deck
  const bench = new THREE.Group();
  const seat = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.08, 0.42), matWood);
  seat.position.y = 0.42; bench.add(seat);
  [[-0.48,0],[0.48,0]].forEach(([x,z]) => {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.42, 0.36), matWoodD);
    leg.position.set(x, 0.21, z); bench.add(leg);
  });
  bench.children.forEach(c => c.castShadow = true);
  bench.position.set(-1.1, 2.09, 1.6); bench.rotation.y = 0.4; scene.add(bench);

  // Towels (draped thin boxes)
  const towel1 = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.04, 0.5), new THREE.MeshStandardMaterial({ color:0xd96a55, roughness:1 }));
  towel1.position.set(-1.1, 0.48, 1.6); towel1.rotation.set(0.35, 0.4, 0.1); towel1.castShadow = true; scene.add(towel1);
  const towel2 = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.04, 0.85), new THREE.MeshStandardMaterial({ color:0x62a7c9, roughness:1 }));
  towel2.position.set(1.45, pierY + 0.09, 4.4); towel2.rotation.z = 0.12; towel2.castShadow = true; scene.add(towel2);

  // Crates (InstancedMesh)
  const crateGeo = new THREE.BoxGeometry(0.5, 0.5, 0.5);
  const crates = new THREE.InstancedMesh(crateGeo, matWood, 4);
  const d = new THREE.Object3D();
  [[-1.9, 2.09, 0.2, 0.3],[1.7, 2.09, 0.6, -0.5],[-1.6, 2.09, 1.0, 0.9],[1.6, pierY + 0.3, 3.4, 0.4]]
  .forEach(([x,y,z,ry], i) => {
    d.position.set(x,y,z); d.rotation.set(0, ry, 0); d.scale.setScalar(1);
    d.updateMatrix(); crates.setMatrixAt(i, d.matrix);
  });
  crates.castShadow = true; scene.add(crates);

  // Potted plants: pots + instanced leaves
  const potGeo = new THREE.CylinderGeometry(0.16, 0.12, 0.24, 8);
  const potMat = new THREE.MeshStandardMaterial({ color:0xb0704a, roughness:1 });
  [[1.9, 2.09, 2.2],[-1.9, 2.09, 2.3],[1.3, pierY + 0.17, 2.9]].forEach(([x,y,z]) => {
    const pot = new THREE.Mesh(potGeo, potMat); pot.position.set(x,y,z); pot.castShadow = true; scene.add(pot);
  });
  const leafGeo2 = new THREE.ConeGeometry(0.07, 0.42, 4); leafGeo2.translate(0, 0.21, 0);
  const plantMat = new THREE.MeshStandardMaterial({ color:0x5aa04f, roughness:1 });
  addSway(plantMat, 0.4, 3.0);
  const leaves = new THREE.InstancedMesh(leafGeo2, plantMat, 21);
  let li = 0;
  [[1.9,2.09,2.2],[-1.9,2.09,2.3],[1.3,pierY+0.17,2.9]].forEach(([x,y,z]) => {
    for (let k = 0; k < 7; k++){
      d.position.set(x + THREE.MathUtils.randFloatSpread(0.22), y + 0.12, z + THREE.MathUtils.randFloatSpread(0.22));
      d.rotation.set(THREE.MathUtils.randFloatSpread(0.5), Math.random()*3, THREE.MathUtils.randFloatSpread(0.5));
      d.scale.setScalar(THREE.MathUtils.randFloat(0.7, 1.3));
      d.updateMatrix(); leaves.setMatrixAt(li++, d.matrix);
    }
  });
  leaves.castShadow = true; scene.add(leaves);
}

// ---------------- Water: volume, surface, caustics, glass ----------------
// Volume — soft turquoise body, depthWrite off so everything inside sorts cleanly
const waterVol = new THREE.Mesh(
  new THREE.BoxGeometry(BOX.hx*2 - 0.1, 1, BOX.hz*2 - 0.1),
  new THREE.MeshPhongMaterial({ color: 0x1f8f96, transparent: true, opacity: 0.24,
    depthWrite: false, side: THREE.DoubleSide, shininess: 60, specular: 0x88e0dd })
);
waterVol.renderOrder = 4;
scene.add(waterVol);

// Animated surface with foam band around the shoreline
const surfMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, side: THREE.DoubleSide,
  uniforms: {
    uTime, uWind,
    uShoreR: { value: shoreRadius(0.25) },
    uDeep:   { value: new THREE.Color(0x1f8f96) },
    uShallow:{ value: new THREE.Color(0x5fc9c2) },
  },
  vertexShader: `
    uniform float uTime; uniform float uWind;
    varying vec3 vW; varying float vH;
    void main(){
      vec3 p = position;
      float h = (sin(p.x*0.9 + uTime*1.7) * 0.5
               + sin(p.y*1.25 - uTime*1.35) * 0.4
               + sin((p.x+p.y)*0.65 + uTime*2.3) * 0.35) * uWind * 0.11;
      p.z += h;
      vH = h;
      vec4 wp = modelMatrix * vec4(p, 1.0);
      vW = wp.xyz;
      gl_Position = projectionMatrix * viewMatrix * wp;
    }`,
  fragmentShader: `
    uniform float uTime; uniform float uShoreR; uniform float uWind;
    uniform vec3 uDeep; uniform vec3 uShallow;
    varying vec3 vW; varying float vH;
    void main(){
      float r = sqrt(vW.x*vW.x + (vW.z/0.8)*(vW.z/0.8));
      vec3 col = mix(uShallow, uDeep, smoothstep(2.5, 8.0, r));
      col += vH * 2.2;                                  // wave sheen
      // Foam band hugging the shore, animated with soft noise
      float band = smoothstep(uShoreR + 0.55, uShoreR + 0.05, r)
                 * smoothstep(uShoreR - 0.6, uShoreR + 0.05, r);
      float ang = atan(vW.z, vW.x);
      float n = 0.55 + 0.45 * sin(r*9.0 - uTime*2.6 + ang*5.0) * sin(ang*3.0 + uTime);
      float foam = band * n * (0.55 + uWind*0.45);
      col = mix(col, vec3(0.94, 0.97, 0.96), clamp(foam, 0.0, 1.0));
      float alpha = 0.5 + foam*0.4 + smoothstep(3.0, 8.5, r)*0.18;
      gl_FragColor = vec4(col, alpha);
    }`
});
const waterSurf = new THREE.Mesh(new THREE.PlaneGeometry(BOX.hx*2 - 0.1, BOX.hz*2 - 0.1, 84, 64), surfMat);
waterSurf.rotation.x = -Math.PI/2;
waterSurf.renderOrder = 5;
scene.add(waterSurf);

// Caustics on the seabed (additive, animated)
const causticMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uTime, uIntensity: { value: 1.0 } },
  vertexShader: `varying vec2 vP; void main(){ vP = position.xy;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `
    uniform float uTime; uniform float uIntensity; varying vec2 vP;
    void main(){
      float w1 = sin(vP.x*1.35 + uTime*0.9) + sin(vP.y*1.7 - uTime*0.75);
      float w2 = sin((vP.x - vP.y)*0.8 + uTime*0.55) + sin(vP.x*0.6 + vP.y*1.1 + uTime*1.1);
      float c = smoothstep(1.1, 2.0, w1 + w2);
      c = pow(c, 1.6) * 0.22 * uIntensity;
      gl_FragColor = vec4(0.45*c, 0.95*c, 0.85*c, c);
    }`
});
const caustics = new THREE.Mesh(new THREE.PlaneGeometry(BOX.hx*2, BOX.hz*2), causticMat);
caustics.rotation.x = -Math.PI/2; caustics.position.y = BOX.bottom + 0.06;
caustics.renderOrder = 1;
scene.add(caustics);

// Glass walls + frame + wooden tray
const glass = new THREE.Mesh(
  new THREE.BoxGeometry(BOX.hx*2, BOX.top - BOX.bottom, BOX.hz*2),
  new THREE.MeshPhysicalMaterial({ color: 0xcfe9ee, transparent: true, opacity: 0.07,
    roughness: 0.15, metalness: 0, depthWrite: false, side: THREE.DoubleSide })
);
glass.position.y = (BOX.top + BOX.bottom)/2;
glass.renderOrder = 8;
scene.add(glass);
const frame = new THREE.LineSegments(new THREE.EdgesGeometry(glass.geometry),
  new THREE.LineBasicMaterial({ color: 0x2c3e46, transparent: true, opacity: 0.85 }));
frame.position.copy(glass.position); frame.renderOrder = 9;
scene.add(frame);
const tray = new THREE.Mesh(new THREE.BoxGeometry(BOX.hx*2 + 0.7, 0.55, BOX.hz*2 + 0.7),
  new THREE.MeshStandardMaterial({ color: 0x6b4f36, roughness: .85 }));
tray.position.y = BOX.bottom - 0.28; tray.receiveShadow = true; tray.castShadow = true;
scene.add(tray);

function applyTide(){
  const L = state.tide;
  const h = L - BOX.bottom;
  waterVol.scale.y = h; waterVol.position.y = BOX.bottom + h/2;
  waterSurf.position.y = L;
  surfMat.uniforms.uShoreR.value = shoreRadius(L);
}
applyTide();

// ---------------- Underwater life ----------------
// Rays — undulating fins via per-vertex animation
const rays = [];
function makeRay(scale, color){
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color, roughness: .7 });
  const bodyGeo = new THREE.SphereGeometry(0.85, 16, 10);
  bodyGeo.scale(1, 0.17, 1.25);
  const body = new THREE.Mesh(bodyGeo, mat); g.add(body);
  // Pectoral fins (animated plane geometry)
  const fins = [];
  for (const s of [-1, 1]){
    const fg = new THREE.PlaneGeometry(1.55, 1.0, 8, 4);
    fg.rotateX(-Math.PI/2);
    fg.translate(0.95*s, 0, -0.1);
    const fin = new THREE.Mesh(fg, new THREE.MeshStandardMaterial({ color, roughness:.75, side: THREE.DoubleSide }));
    fin.userData.base = fg.attributes.position.array.slice();
    fin.userData.side = s;
    g.add(fin); fins.push(fin);
  }
  // Tail
  const tail = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.09, 1.2, 5), mat);
  tail.rotation.x = Math.PI/2; tail.position.z = -1.45;
  const tailPivot = new THREE.Group(); tailPivot.add(tail); g.add(tailPivot);
  g.scale.setScalar(scale);
  g.userData = { fins, tailPivot, angle: Math.random()*Math.PI*2,
    speed: THREE.MathUtils.randFloat(0.14, 0.2), depth: THREE.MathUtils.randFloat(-2.2, -1.1),
    flap: THREE.MathUtils.randFloat(2.4, 3.2), jump: null };
  scene.add(g); rays.push(g); return g;
}
makeRay(1.0, 0x51626e); makeRay(0.8, 0x5f7079); makeRay(0.7, 0x47565f);

// Fish schools (InstancedMesh cones)
const schools = [];
{
  const fishGeo = new THREE.ConeGeometry(0.07, 0.3, 5); fishGeo.rotateX(Math.PI/2);
  const palettes = [0xf2a54c, 0xe8e0d0, 0x7fb3d4];
  for (let s = 0; s < 3; s++){
    const mat = new THREE.MeshStandardMaterial({ color: palettes[s], roughness: .6 });
    const N = 16;
    const im = new THREE.InstancedMesh(fishGeo, mat, N);
    const offs = []; for (let i = 0; i < N; i++) offs.push(new THREE.Vector3(THREE.MathUtils.randFloatSpread(1.8), THREE.MathUtils.randFloatSpread(0.9), THREE.MathUtils.randFloatSpread(1.8)));
    schools.push({ im, offs, N, angle: Math.random()*Math.PI*2,
      speed: THREE.MathUtils.randFloat(0.25, 0.4), rx: THREE.MathUtils.randFloat(5.5, 7.4),
      rz: THREE.MathUtils.randFloat(4.2, 5.4), y: THREE.MathUtils.randFloat(-2.3, -1.2) });
    scene.add(im);
  }
}

// Aquatic plants (instanced, swaying)
{
  const geo = new THREE.CylinderGeometry(0.03, 0.1, 1.7, 5, 3); geo.translate(0, 0.85, 0);
  const mat = new THREE.MeshStandardMaterial({ color: 0x3f8f6a, roughness: 1, transparent: true, opacity: 0.9 });
  addSway(mat, 0.55, 1.6);
  const N = 26, weeds = new THREE.InstancedMesh(geo, mat, N);
  const d = new THREE.Object3D(); const c = new THREE.Color();
  for (let i = 0; i < N; i++){
    const a = Math.random()*Math.PI*2, r = THREE.MathUtils.randFloat(4.6, 8.2);
    const x = Math.cos(a)*r, z = Math.sin(a)*r*0.85;
    if (Math.abs(x) > BOX.hx-0.6 || Math.abs(z) > BOX.hz-0.6) continue;
    d.position.set(x, BOX.bottom, z);
    d.rotation.set(THREE.MathUtils.randFloatSpread(0.3), Math.random()*3, THREE.MathUtils.randFloatSpread(0.3));
    d.scale.set(1, THREE.MathUtils.randFloat(0.6, 1.4), 1);
    d.updateMatrix(); weeds.setMatrixAt(i, d.matrix);
    c.setHSL(0.35 + Math.random()*0.1, 0.5, 0.28 + Math.random()*0.12);
    weeds.setColorAt(i, c);
  }
  scene.add(weeds);
}

// Bubbles (rising instanced spheres)
const bubbles = [];
{
  const geo = new THREE.SphereGeometry(0.06, 8, 6);
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0.4, roughness: .2 });
  const im = new THREE.InstancedMesh(geo, mat, 26);
  for (let i = 0; i < 26; i++) bubbles.push({ x: THREE.MathUtils.randFloatSpread(16), z: THREE.MathUtils.randFloatSpread(12),
    y: THREE.MathUtils.randFloat(BOX.bottom, state.tide), s: THREE.MathUtils.randFloat(0.4, 1.2), v: THREE.MathUtils.randFloat(0.25, 0.7) });
  scene.add(im); bubbles.im = im;
}

// ---------------- Kayak ----------------
const kayak = new THREE.Group();
{
  const hullGeo = new THREE.SphereGeometry(0.5, 14, 10);
  hullGeo.scale(0.42, 0.22, 1.7);
  const hull = new THREE.Mesh(hullGeo, new THREE.MeshStandardMaterial({ color: 0xe2762f, roughness: .45 }));
  hull.castShadow = true; kayak.add(hull);
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.06, 0.3), matWoodD);
  seat.position.y = 0.18; kayak.add(seat);
  const paddle = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.03, 0.9), matWood);
  paddle.position.set(0.16, 0.24, 0); paddle.rotation.y = 0.6; kayak.add(paddle);
}
const KAYAK_DOCK = { x: 1.75, z: 5.2, angle: Math.atan2(5.2, 1.75) * 0.4 };
kayak.position.set(KAYAK_DOCK.x, state.tide + 0.12, KAYAK_DOCK.z);
scene.add(kayak);
const kayakState = { mode: 'docked', t: 0, theta: 0, fromTheta: 0 };

// ---------------- Ray leap + splash FX ----------------
const ringGeo = new THREE.RingGeometry(0.15, 0.32, 40);
const ripples = [];
for (let i = 0; i < 4; i++){
  const m = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0xeef7f4, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }));
  m.rotation.x = -Math.PI/2; m.visible = false; m.renderOrder = 6; scene.add(m); ripples.push(m);
}
const dropMat = new THREE.MeshStandardMaterial({ color: 0xbfe9ef, transparent: true, opacity: 0.85, roughness: .15 });
const dropGeo = new THREE.SphereGeometry(0.05, 6, 5);
const dropsMesh = new THREE.InstancedMesh(dropGeo, dropMat, 48);
const drops = []; for (let i = 0; i < 48; i++) drops.push({ live: false, p: new THREE.Vector3(), v: new THREE.Vector3(), life: 0 });
scene.add(dropsMesh);
const dummy = new THREE.Object3D();

function triggerRayLeap(){
  const ray = rays[0]; if (ray.userData.jump) return;
  const dir = new THREE.Vector3(-Math.sin(ray.userData.angle)*ray.userData.rx, 0, Math.cos(ray.userData.angle)*ray.userData.rz).normalize();
  ray.userData.jump = { t: 0, vy: 6.6, g: 9.8, vh: 3.4, dir, start: ray.position.clone() };
  audio.paddle();
}
function splashAt(p){
  audio.splash();
  let n = 0;
  for (const r of ripples){
    r.visible = true; r.position.set(p.x, state.tide + 0.03, p.z);
    r.scale.setScalar(0.6); r.material.opacity = 0.55 - n*0.1; r.userData.t = -n*0.15; n++;
    if (n >= 3) break;
  }
  for (const d of drops){
    if (d.live) continue;
    d.live = true; d.life = THREE.MathUtils.randFloat(0.7, 1.4);
    d.p.copy(p); d.p.y = state.tide;
    d.v.set(THREE.MathUtils.randFloatSpread(2.4), THREE.MathUtils.randFloat(2.5, 5.5), THREE.MathUtils.randFloatSpread(2.4));
  }
}

// ---------------- Camera presets & transitions ----------------
const CAMS = {
  iso:  { pos: new THREE.Vector3(13, 10, 13),  tgt: new THREE.Vector3(0, 0.5, 0) },
  cozy: { pos: new THREE.Vector3(6.2, 2.7, 9.4), tgt: new THREE.Vector3(0.6, 1.4, 3.6) },
  under:{ pos: new THREE.Vector3(-2.4, -1.5, 6.0), tgt: new THREE.Vector3(0.5, -1.4, 0) },
};
let camAnim = null;
function goCam(name){
  camAnim = { t: 0, p0: camera.position.clone(), p1: CAMS[name].pos.clone(),
              t0: controls.target.clone(), t1: CAMS[name].tgt.clone() };
  document.getElementById('underwater-tint').style.opacity = name === 'under' ? 1 : 0;
  ['camIso','camCozy','camUnder'].forEach(id => document.getElementById(id).classList.remove('active'));
  document.getElementById({ iso:'camIso', cozy:'camCozy', under:'camUnder' }[name]).classList.add('active');
}

// ---------------- Audio (Web Audio API, all procedural) ----------------
const audio = {
  ctx: null, master: null, musicOn: false, musicGain: null, timer: null,
  init(){
    if (this.ctx) return;
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    this.master = this.ctx.createGain();
    this.master.gain.value = parseFloat(volSlider.value);
    this.master.connect(this.ctx.destination);
    // Noise buffer (shared)
    const len = this.ctx.sampleRate * 2;
    const buf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random()*2 - 1;
    this.noiseBuf = buf;
    // Waves ambience: lowpass noise with slow LFO
    const wSrc = this.ctx.createBufferSource(); wSrc.buffer = buf; wSrc.loop = true;
    const wf = this.ctx.createBiquadFilter(); wf.type = 'lowpass'; wf.frequency.value = 550; wf.Q.value = 0.6;
    const wg = this.ctx.createGain(); wg.gain.value = 0.10;
    const lfo = this.ctx.createOscillator(); lfo.frequency.value = 0.13;
    const lfoG = this.ctx.createGain(); lfoG.gain.value = 0.05;
    lfo.connect(lfoG); lfoG.connect(wg.gain);
    wSrc.connect(wf); wf.connect(wg); wg.connect(this.master);
    wSrc.start(); lfo.start();
    // Wind: bandpass noise, gain follows wind slider
    const kSrc = this.ctx.createBufferSource(); kSrc.buffer = buf; kSrc.loop = true;
    const kf = this.ctx.createBiquadFilter(); kf.type = 'bandpass'; kf.frequency.value = 420; kf.Q.value = 0.8;
    const kg = this.ctx.createGain(); kg.gain.value = 0.02;
    kSrc.connect(kf); kf.connect(kg); kg.connect(this.master);
    kSrc.start(); this.windGain = kg;
    // Music chain: delay echo
    this.musicGain = this.ctx.createGain(); this.musicGain.gain.value = 0;
    const delay = this.ctx.createDelay(); delay.delayTime.value = 0.42;
    const fb = this.ctx.createGain(); fb.gain.value = 0.38;
    const df = this.ctx.createBiquadFilter(); df.type = 'lowpass'; df.frequency.value = 1400;
    this.musicGain.connect(df); df.connect(this.master);
    df.connect(delay); delay.connect(fb); fb.connect(delay); delay.connect(df);
  },
  setWind(v){ if (this.windGain) this.windGain.gain.value = 0.015 + v * 0.05; },
  setVolume(v){ if (this.master) this.master.gain.value = v; },
  toggleMusic(){
    this.init(); if (this.ctx.state === 'suspended') this.ctx.resume();
    this.musicOn = !this.musicOn;
    this.musicGain.gain.setTargetAtTime(this.musicOn ? 0.16 : 0, this.ctx.currentTime, 0.6);
    if (this.musicOn && !this.timer) this.schedule();
    return this.musicOn;
  },
  schedule(){
    const scale = [220, 261.6, 293.7, 329.6, 392, 440, 523.3]; // A pentatonic-ish
    const note = () => {
      if (!this.musicOn) { this.timer = null; return; }
      const t = this.ctx.currentTime;
      const f = scale[Math.floor(Math.random()*scale.length)] * (Math.random() < 0.2 ? 2 : 1);
      const o = this.ctx.createOscillator(); o.type = 'triangle'; o.frequency.value = f;
      const o2 = this.ctx.createOscillator(); o2.type = 'sine'; o2.frequency.value = f*2;
      const g = this.ctx.createGain();
      const dur = THREE.MathUtils.randFloat(1.2, 2.2);
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(THREE.MathUtils.randFloat(0.5, 0.9), t + 0.04);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      o.connect(g); o2.connect(g); g.connect(this.musicGain);
      o.start(t); o2.start(t); o.stop(t + dur + 0.1); o2.stop(t + dur + 0.1);
      this.timer = setTimeout(note, THREE.MathUtils.randFloat(700, 1600));
    };
    note();
  },
  splash(){
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    const src = this.ctx.createBufferSource(); src.buffer = this.noiseBuf;
    const f = this.ctx.createBiquadFilter(); f.type = 'lowpass';
    f.frequency.setValueAtTime(2200, t); f.frequency.exponentialRampToValueAtTime(200, t + 0.5);
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.5, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.6);
    src.connect(f); f.connect(g); g.connect(this.master);
    src.start(t); src.stop(t + 0.7);
    const o = this.ctx.createOscillator(); o.frequency.setValueAtTime(180, t);
    o.frequency.exponentialRampToValueAtTime(60, t + 0.3);
    const og = this.ctx.createGain(); og.gain.setValueAtTime(0.25, t);
    og.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
    o.connect(og); og.connect(this.master); o.start(t); o.stop(t + 0.4);
  },
  paddle(){
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    const src = this.ctx.createBufferSource(); src.buffer = this.noiseBuf;
    const f = this.ctx.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 900; f.Q.value = 1.2;
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.18, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
    src.connect(f); f.connect(g); g.connect(this.master); src.start(t); src.stop(t + 0.4);
  }
};

// ---------------- UI wiring ----------------
const $ = id => document.getElementById(id);
const tideSlider = $('tide'), windSlider = $('wind'), volSlider = $('volume');

tideSlider.addEventListener('input', e => {
  state.tide = parseFloat(e.target.value); $('tideVal').textContent = state.tide.toFixed(2); applyTide();
});
windSlider.addEventListener('input', e => {
  state.wind = parseFloat(e.target.value); $('windVal').textContent = state.wind.toFixed(2);
  uWind.value = state.wind; audio.setWind(state.wind);
});
volSlider.addEventListener('input', e => {
  $('volVal').textContent = Math.round(e.target.value*100) + '%'; audio.setVolume(parseFloat(e.target.value));
});
$('camIso').onclick   = () => goCam('iso');
$('camCozy').onclick  = () => goCam('cozy');
$('camUnder').onclick = () => goCam('under');
$('rayBtn').onclick   = () => { audio.init(); if (audio.ctx.state==='suspended') audio.ctx.resume(); triggerRayLeap(); };
$('kayakBtn').onclick = () => {
  audio.init(); if (audio.ctx.state==='suspended') audio.ctx.resume(); audio.paddle();
  if (kayakState.mode === 'docked'){
    kayakState.mode = 'out'; kayakState.t = 0; kayakState.fromTheta = 0;
    $('kayakBtn').textContent = 'Return kayak';
  } else if (kayakState.mode === 'cruising'){
    kayakState.mode = 'back'; kayakState.t = 0;
    $('kayakBtn').textContent = 'Launch kayak';
  }
};
['Day','Sunset','Night'].forEach(name => {
  $('tod'+name).onclick = () => {
    setTod(name.toLowerCase());
    ['Day','Sunset','Night'].forEach(n => $('tod'+n).classList.toggle('active', n === name));
  };
});
$('pauseBtn').onclick = () => {
  state.paused = !state.paused;
  $('pauseBtn').textContent = state.paused ? 'Resume' : 'Pause';
  $('pauseBtn').classList.toggle('active', state.paused);
};
$('resetBtn').onclick = () => {
  state.tide = 0.25; tideSlider.value = 0.25; $('tideVal').textContent = '0.25'; applyTide();
  state.wind = 0.6; windSlider.value = 0.6; $('windVal').textContent = '0.6'; uWind.value = 0.6; audio.setWind(0.6);
  setTod('day'); ['Day','Sunset','Night'].forEach(n => $('tod'+n).classList.toggle('active', n==='Day'));
  kayakState.mode = 'docked'; $('kayakBtn').textContent = 'Launch kayak';
  rays[0].userData.jump = null;
  goCam('iso');
  state.paused = false; $('pauseBtn').textContent = 'Pause'; $('pauseBtn').classList.remove('active');
};
$('musicBtn').onclick = () => {
  const on = audio.toggleMusic();
  $('musicBtn').textContent = on ? 'Music ✓' : 'Music ✕';
  $('musicBtn').classList.toggle('active', on);
};
$('menuBtn').onclick = () => $('ui').classList.toggle('open');

// Start audio context lazily on first interaction (autoplay policies)
const kick = () => { audio.init(); if (audio.ctx.state === 'suspended') audio.ctx.resume(); audio.setWind(state.wind); };
window.addEventListener('pointerdown', kick, { once: true });

// ---------------- Main loop ----------------
const clock = new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const active = !state.paused;
  if (active) state.time += dt;
  const T = state.time;
  uTime.value = T;

  // Time-of-day transitions run even while paused (UI-driven)
  lerpTod(dt);

  // Camera transition
  if (camAnim){
    camAnim.t = Math.min(1, camAnim.t + dt / 1.4);
    const e = camAnim.t < 0.5 ? 4*camAnim.t**3 : 1 - Math.pow(-2*camAnim.t+2, 3)/2;
    camera.position.lerpVectors(camAnim.p0, camAnim.p1, e);
    controls.target.lerpVectors(camAnim.t0, camAnim.t1, e);
    if (camAnim.t >= 1) camAnim = null;
  }
  controls.update();

  if (active){
    // Tree sway
    trees.forEach(t => {
      t.rotation.z = Math.sin(T*1.4 + t.userData.phase) * 0.035 * (0.3 + state.wind);
      t.rotation.x = Math.cos(T*1.1 + t.userData.phase) * 0.02 * (0.3 + state.wind);
    });

    // Rays
    rays.forEach((ray, ri) => {
      const ud = ray.userData;
      // Fin undulation
      ud.fins.forEach(fin => {
        const pos = fin.geometry.attributes.position;
        const base = fin.userData.base;
        for (let i = 0; i < pos.count; i++){
          const x = base[i*3];
          const dist = Math.abs(x) / 1.7;
          pos.array[i*3+1] = Math.sin(T*ud.flap + dist*2.6 + fin.userData.side*0.6) * 0.42 * dist * dist;
        }
        pos.needsUpdate = true;
      });
      ud.tailPivot.rotation.y = Math.sin(T*2.1 + ri) * 0.22;

      if (ud.jump){
        // Parabolic leap
        const j = ud.jump; j.t += dt;
        const x = j.start.x + j.dir.x * j.vh * j.t;
        const z = j.start.z + j.dir.z * j.vh * j.t;
        const y = j.start.y + j.vy * j.t - 0.5 * j.g * j.t * j.t;
        if (y <= state.tide && j.t > 0.2){
          ray.position.set(x, state.tide, z);
          splashAt(new THREE.Vector3(x, state.tide, z));
          ud.jump = null;
          ud.angle = Math.atan2(z / ud.rz, x / ud.rx);
          ray.rotation.set(0, 0, 0);
        } else {
          ray.position.set(x, y, z);
          const pitch = Math.atan2(j.vy - j.g*j.t, j.vh);
          const yaw = Math.atan2(j.dir.x, j.dir.z);
          ray.rotation.order = 'YXZ';
          ray.rotation.set(-pitch, yaw, 0);
        }
      } else {
        ud.angle += ud.speed * dt;
        const a = ud.angle;
        ray.position.set(Math.cos(a)*ud.rx, ud.depth + Math.sin(T*0.5 + ri*2)*0.4, Math.sin(a)*ud.rz);
        const tx = -Math.sin(a)*ud.rx, tz = Math.cos(a)*ud.rz;
        ray.rotation.set(0, Math.atan2(tx, tz), Math.sin(T*0.8 + ri)*0.06);
      }
    });

    // Fish schools
    schools.forEach(sc => {
      sc.angle += sc.speed * dt;
      const cx = Math.cos(sc.angle)*sc.rx, cz = Math.sin(sc.angle)*sc.rz;
      const cy = sc.y + Math.sin(T*0.7 + sc.angle)*0.35;
      const yaw = Math.atan2(-Math.sin(sc.angle)*sc.rx, Math.cos(sc.angle)*sc.rz);
      for (let i = 0; i < sc.N; i++){
        const o = sc.offs[i];
        const ox = o.x*Math.cos(sc.angle) - o.z*Math.sin(sc.angle);
        const oz = o.x*Math.sin(sc.angle) + o.z*Math.cos(sc.angle);
        dummy.position.set(cx+ox, cy+o.y + Math.sin(T*3 + i)*0.06, cz+oz);
        dummy.rotation.set(Math.sin(T*4+i)*0.15, yaw + Math.sin(T*2+i)*0.1, 0);
        dummy.scale.setScalar(1); dummy.updateMatrix();
        sc.im.setMatrixAt(i, dummy.matrix);
      }
      sc.im.instanceMatrix.needsUpdate = true;
    });

    // Bubbles
    bubbles.im.count && bubbles.forEach((b, i) => {
      b.y += b.v * dt;
      if (b.y > state.tide - 0.05){
        b.y = BOX.bottom + 0.1;
        b.x = THREE.MathUtils.randFloatSpread(16); b.z = THREE.MathUtils.randFloatSpread(12);
      }
      dummy.position.set(b.x + Math.sin(T*2 + i)*0.1, b.y, b.z);
      dummy.scale.setScalar(b.s); dummy.rotation.set(0,0,0); dummy.updateMatrix();
      bubbles.im.setMatrixAt(i, dummy.matrix);
    });
    bubbles.im.instanceMatrix.needsUpdate = true;

    // Kayak
    const bob = Math.sin(T*1.8)*0.04*(0.4+state.wind) + 0.12;
    if (kayakState.mode === 'out'){
      kayakState.t += dt / 14;
      const th = kayakState.fromTheta + kayakState.t * Math.PI * 2;
      kayakState.theta = th;
      kayak.position.set(Math.cos(th)*7.2, state.tide + bob, Math.sin(th)*5.4);
      kayak.rotation.set(Math.sin(T*1.6)*0.05, Math.atan2(-Math.sin(th)*7.2, Math.cos(th)*5.4), Math.cos(T*1.3)*0.04);
      if (kayakState.t >= 1){ kayakState.mode = 'cruising'; kayakState.t = 0; }
    } else if (kayakState.mode === 'cruising'){
      kayakState.theta += dt * 0.35;
      kayak.position.set(Math.cos(kayakState.theta)*7.2, state.tide + bob, Math.sin(kayakState.theta)*5.4);
      kayak.rotation.set(Math.sin(T*1.6)*0.05, Math.atan2(-Math.sin(kayakState.theta)*7.2, Math.cos(kayakState.theta)*5.4), Math.cos(T*1.3)*0.04);
    } else if (kayakState.mode === 'back'){
      kayakState.t += dt / 9;
      const e = kayakState.t >= 1 ? 1 : kayakState.t*kayakState.t*(3-2*kayakState.t);
      const th = THREE.MathUtils.lerp(kayakState.theta, KAYAK_DOCK.angle, e);
      kayak.position.set(THREE.MathUtils.lerp(Math.cos(th)*7.2, KAYAK_DOCK.x, e*0.15), state.tide + bob, THREE.MathUtils.lerp(Math.sin(th)*5.4, KAYAK_DOCK.z, e*0.15));
      kayak.rotation.set(Math.sin(T*1.6)*0.05, Math.atan2(-Math.sin(th)*7.2, Math.cos(th)*5.4), Math.cos(T*1.3)*0.04);
      if (kayakState.t >= 1){ kayakState.mode = 'docked'; }
    } else {
      kayak.position.set(KAYAK_DOCK.x, state.tide + bob, KAYAK_DOCK.z);
      kayak.rotation.set(Math.sin(T*1.6)*0.05, 0.5 + Math.sin(T*0.9)*0.05, Math.sin(T*1.2)*0.04);
    }

    // Ripples
    ripples.forEach(r => {
      if (!r.visible) return;
      r.userData.t = (r.userData.t || 0) + dt;
      if (r.userData.t < 0) return;
      r.scale.setScalar(0.6 + r.userData.t * 4.5);
      r.material.opacity = Math.max(0, 0.5 - r.userData.t * 0.55);
      r.position.y = state.tide + 0.03;
      if (r.material.opacity <= 0.01) r.visible = false;
    });

    // Droplets
    let any = false;
    drops.forEach((d, i) => {
      if (!d.live){ dummy.position.set(0,-99,0); dummy.scale.setScalar(0.0001); dummy.updateMatrix(); dropsMesh.setMatrixAt(i, dummy.matrix); return; }
      any = true;
      d.life -= dt; d.v.y -= 9.8*dt; d.p.addScaledVector(d.v, dt);
      if (d.life <= 0 || d.p.y < state.tide - 0.2) d.live = false;
      dummy.position.copy(d.p);
      dummy.scale.setScalar(Math.max(0.0001, d.life)); dummy.updateMatrix();
      dropsMesh.setMatrixAt(i, dummy.matrix);
    });
    dropsMesh.instanceMatrix.needsUpdate = true;
  }

  renderer.render(scene, camera);
}
animate();

// ---------------- Resize ----------------
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, MOBILE ? 1 : 1.75));
});
</script>
</body>
</html>
```

## Highlights

**Cutaway water done right** — the lagoon is a layered stack: additive caustics (renderOrder 1) → island/fish (opaque pass) → water volume (2…4) → animated surface with a foam band computed from the island's height profile (5) → ripples (6) → glass walls + frame (8–9). All transparent layers use `depthWrite: false`, so there's no flicker or sorting chaos.

**Wind is a real uniform** — grass, seaweed, and potted plants share one `uWind`/`uTime` uniform pair injected into `MeshStandardMaterial` via `onBeforeCompile`, so hundreds of instanced blades sway from one slider.

**Everything responds to the tide** — the water box rescales, the foam band re-solves the shoreline radius, and the kayak, bubbles, ripples, and splash droplets all track the current level.

**Fully procedural audio** — filtered noise loops for waves and wind, a delayed pentatonic pluck sequencer for music, plus one-shot synthesis for splashes and paddle strokes. Starts only after a user gesture.

**Performance** — capped pixel ratio, lower shadow maps on mobile, `InstancedMesh` for grass, rocks, fish, weeds, bubbles, droplets, and crates, with delta-time clamped animations throughout.