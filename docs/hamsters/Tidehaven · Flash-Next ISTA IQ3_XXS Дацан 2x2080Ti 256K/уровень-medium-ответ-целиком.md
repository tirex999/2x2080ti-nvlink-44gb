# Tidehaven

A complete single-file interactive 3D diorama. Save as `index.html` and open in any modern browser. Everything is procedural — no external assets.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Tidehaven — Coastal Island Diorama</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html,body { width:100%; height:100%; overflow:hidden; background:#0c161c;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
  canvas { display:block; }

  #title { position:fixed; top:18px; left:20px; pointer-events:none; z-index:10;
    color:#f4ede2; text-shadow:0 2px 12px rgba(0,0,0,.45); }
  #title h1 { font-size:26px; font-weight:700; letter-spacing:2px; }
  #title p  { font-size:12px; opacity:.75; letter-spacing:1.5px; margin-top:3px; }

  .panel { position:fixed; z-index:10; background:rgba(16,28,33,.55);
    backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,.13); border-radius:14px; padding:10px 12px;
    color:#eaf2ef; box-shadow:0 8px 28px rgba(0,0,0,.35); }
  .panel h3 { font-size:10px; letter-spacing:2px; text-transform:uppercase; opacity:.6; margin-bottom:8px; }
  .row { display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin-bottom:6px; }
  .row:last-child { margin-bottom:0; }

  .btn { border:1px solid rgba(255,255,255,.18); background:rgba(255,255,255,.07);
    color:#eaf2ef; font-size:11.5px; padding:7px 11px; border-radius:9px; cursor:pointer;
    letter-spacing:.5px; transition:background .2s,border-color .2s,transform .1s; }
  .btn:hover { background:rgba(255,255,255,.16); }
  .btn:active { transform:scale(.96); }
  .btn.active { background:#2f9c86; border-color:#5fd0b4; color:#fff; }

  .slider { display:flex; align-items:center; gap:8px; font-size:11px; margin-bottom:6px; }
  .slider label { width:42px; opacity:.75; letter-spacing:.5px; }
  input[type=range] { -webkit-appearance:none; width:110px; height:4px; border-radius:2px;
    background:rgba(255,255,255,.25); outline:none; }
  input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:14px; height:14px;
    border-radius:50%; background:#7fd4c1; cursor:pointer; border:2px solid #16242a; }
  input[type=range]::-moz-range-thumb { width:12px; height:12px; border-radius:50%;
    background:#7fd4c1; cursor:pointer; border:2px solid #16242a; }

  #camPanel  { left:20px;  bottom:20px; }
  #actPanel  { right:20px; bottom:20px; }
  #timePanel { right:20px; top:20px; }
  #hint { position:fixed; bottom:22px; left:50%; transform:translateX(-50%); z-index:9;
    font-size:11px; color:rgba(255,255,255,.5); letter-spacing:1px; pointer-events:none;
    text-shadow:0 1px 6px rgba(0,0,0,.5); }

  #collapseBtn { display:none; position:fixed; bottom:20px; left:50%; transform:translateX(-50%);
    z-index:11; }

  @media (max-width:760px){
    #title h1 { font-size:19px; } #title p { font-size:10px; }
    .panel { padding:8px 9px; }
    #camPanel { left:10px; bottom:64px; } #actPanel { right:10px; bottom:64px; max-width:44vw; }
    #timePanel { right:10px; top:10px; }
    input[type=range] { width:80px; }
    #hint { display:none; }
    #collapseBtn { display:block; }
    body.panels-hidden .panel { display:none; }
  }
</style>
</head>
<body>

<div id="title"><h1>TIDEHAVEN</h1><p>A COZY COASTAL DIORAMA</p></div>
<div id="hint">Drag to orbit · Scroll to zoom</div>
<button class="btn" id="collapseBtn">☰ Controls</button>

<div class="panel" id="camPanel">
  <h3>Camera</h3>
  <div class="row">
    <button class="btn active" data-cam="iso">Isometric</button>
    <button class="btn" data-cam="cabin">Cabin</button>
    <button class="btn" data-cam="under">Underwater</button>
  </div>
</div>

<div class="panel" id="actPanel">
  <h3>Actions</h3>
  <div class="row">
    <button class="btn" id="kayakBtn">Launch Kayak</button>
    <button class="btn" id="rayBtn">Ray Leap</button>
    <button class="btn" id="pauseBtn">Pause</button>
    <button class="btn" id="resetBtn">Reset</button>
  </div>
  <div class="slider"><label>Tide</label><input type="range" id="tide" min="-1" max="1" step="0.01" value="0"></div>
  <div class="slider"><label>Wind</label><input type="range" id="wind" min="0" max="1" step="0.01" value="0.5"></div>
  <h3 style="margin-top:8px">Audio</h3>
  <div class="row"><button class="btn" id="musicBtn">Music: Off</button></div>
  <div class="slider"><label>Volume</label><input type="range" id="vol" min="0" max="1" step="0.01" value="0.7"></div>
</div>

<div class="panel" id="timePanel">
  <h3>Time of Day</h3>
  <div class="row">
    <button class="btn active" data-time="day">Day</button>
    <button class="btn" data-time="sunset">Sunset</button>
    <button class="btn" data-time="night">Night</button>
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
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

/* ============================================================
   1. RENDERER / SCENE / CAMERA
============================================================ */
const isMobile = /Mobi|Android|iPhone/i.test(navigator.userAgent);
const renderer = new THREE.WebGLRenderer({ antialias: !isMobile });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0xbfe3ea, 0.012);

const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.1, 200);
camera.position.set(17, 13, 17);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.06;
controls.minDistance = 3; controls.maxDistance = 48;
controls.maxPolarAngle = Math.PI * 0.92;
controls.target.set(0, 0, 0);

/* ============================================================
   2. SHARED UNIFORMS & STATE
============================================================ */
const U = {
  time:  { value: 0 },
  wind:  { value: 0.5 },
  level: { value: 0.15 }   // water surface height
};
const BASE_LEVEL = 0.15;
let paused = false, worldTime = 0;

// Diorama bounds
const BOX = { x0:-12, x1:12, z0:-8, z1:8, y0:-6, y1:6 };

/* ============================================================
   3. LIGHTS & TIME OF DAY
============================================================ */
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.castShadow = true;
sun.shadow.mapSize.set(isMobile ? 512 : 1024, isMobile ? 512 : 1024);
sun.shadow.camera.left = -14; sun.shadow.camera.right = 14;
sun.shadow.camera.top = 14; sun.shadow.camera.bottom = -14;
sun.shadow.camera.near = 1; sun.shadow.camera.far = 60;
sun.shadow.bias = -0.0008;
scene.add(sun);

const hemi = new THREE.HemisphereLight(0xbfe3ea, 0x6b5a44, 0.55);
scene.add(hemi);
const ambient = new THREE.AmbientLight(0x22333a, 0.4);
scene.add(ambient);

const TIME_PRESETS = {
  day:    { sky:0xbfe3ea, sunC:0xfff2df, sunI:1.6, hemiI:0.55, ambI:0.4,
            pos:[8,13,6],  lamp:0, night:0, spec:0.8 },
  sunset: { sky:0xf0a066, sunC:0xff9a58, sunI:1.15, hemiI:0.42, ambI:0.5,
            pos:[-11,4,4], lamp:0.65, night:0.25, spec:1.2 },
  night:  { sky:0x141f2c, sunC:0x9db8d8, sunI:0.45, hemiI:0.22, ambI:0.3,
            pos:[7,11,-8], lamp:1.0, night:1.0, spec:0.25 }
};
const cur = {
  sky:new THREE.Color(TIME_PRESETS.day.sky), sunC:new THREE.Color(TIME_PRESETS.day.sunC),
  sunI:1.6, hemiI:0.55, ambI:0.4, lamp:0, night:0, spec:0.8,
  pos:new THREE.Vector3(8,13,6)
};
let target = TIME_PRESETS.day;

// Stars (visible at night)
const starGeo = new THREE.BufferGeometry();
const starPos = new Float32Array(250*3);
for (let i=0;i<250;i++){
  const a = Math.random()*Math.PI*2, r = 30+Math.random()*35, h = 12+Math.random()*35;
  starPos[i*3]=Math.cos(a)*r; starPos[i*3+1]=h; starPos[i*3+2]=Math.sin(a)*r;
}
starGeo.setAttribute('position', new THREE.BufferAttribute(starPos,3));
const starMat = new THREE.PointsMaterial({ color:0xffffff, size:0.35, transparent:true, opacity:0, depthWrite:false });
scene.add(new THREE.Points(starGeo, starMat));

/* ============================================================
   4. DIORAMA SHELL — wooden base, walls, glass, frame
============================================================ */
const woodMat  = new THREE.MeshStandardMaterial({ color:0x8a6746, roughness:0.85 });
const darkWood = new THREE.MeshStandardMaterial({ color:0x5f4630, roughness:0.9 });
const copper   = new THREE.MeshStandardMaterial({ color:0xb87333, roughness:0.35, metalness:0.6 });
const frameMat = new THREE.MeshStandardMaterial({ color:0x4a3826, roughness:0.8 });

// Wooden base slab
const slab = new THREE.Mesh(new THREE.BoxGeometry(26, 0.8, 18), frameMat);
slab.position.y = -6.5; slab.receiveShadow = true; scene.add(slab);

// Opaque back / left walls (interior)
const wallMat = new THREE.MeshStandardMaterial({ color:0x123f47, roughness:0.9 });
const backWall = new THREE.Mesh(new THREE.PlaneGeometry(24, 12), wallMat);
backWall.position.set(0, 0, BOX.z0); backWall.receiveShadow = true; scene.add(backWall);
const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(16, 12), wallMat);
leftWall.rotation.y = Math.PI/2; leftWall.position.set(BOX.x0, 0, 0);
leftWall.receiveShadow = true; scene.add(leftWall);

// Glass front + right (cutaway faces) — depthWrite OFF, drawn last
const glassMat = new THREE.MeshPhysicalMaterial({
  color:0xcfeef0, transparent:true, opacity:0.10, roughness:0.12, metalness:0,
  side:THREE.DoubleSide, depthWrite:false });
const glassFront = new THREE.Mesh(new THREE.PlaneGeometry(24, 12), glassMat);
glassFront.position.set(0, 0, BOX.z1); glassFront.renderOrder = 5; scene.add(glassFront);
const glassRight = new THREE.Mesh(new THREE.PlaneGeometry(16, 12), glassMat);
glassRight.rotation.y = -Math.PI/2; glassRight.position.set(BOX.x1, 0, 0);
glassRight.renderOrder = 5; scene.add(glassRight);

// Frame edges
function frameBar(w,h,d,x,y,z){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), frameMat);
  m.position.set(x,y,z); m.castShadow = true; scene.add(m);
}
const F=0.3, H=12, Yc=0;
for (const [x,z] of [[BOX.x0,BOX.z0],[BOX.x0,BOX.z1],[BOX.x1,BOX.z0],[BOX.x1,BOX.z1]])
  frameBar(F,H,F,x,Yc,z);
frameBar(24+F,F,F,0,BOX.y1,BOX.z1); frameBar(F,F,16+F,BOX.x1,BOX.y1,0);
frameBar(24+F,F,F,0,BOX.y0,BOX.z1); frameBar(F,F,16+F,BOX.x1,BOX.y0,0);
frameBar(24+F,F,F,0,BOX.y1,BOX.z0); frameBar(F,F,16+F,BOX.x0,BOX.y1,0);
frameBar(24+F,F,F,0,BOX.y0,BOX.z0); frameBar(F,F,16+F,BOX.x0,BOX.y0,0);

/* ============================================================
   5. SEABED with animated caustics
============================================================ */
const bedGeo = new THREE.PlaneGeometry(24, 16, 48, 48);
bedGeo.rotateX(-Math.PI/2);
{ // gentle bumps
  const p = bedGeo.attributes.position;
  for (let i=0;i<p.count;i++){
    const x=p.getX(i), z=p.getZ(i);
    p.setY(i, p.getY(i) + Math.sin(x*0.7)*Math.cos(z*0.9)*0.18 + Math.sin(x*2.1+z*1.7)*0.06);
  }
  bedGeo.computeVertexNormals();
}
const bedMat = new THREE.MeshStandardMaterial({ color:0xb3a177, roughness:1 });
bedMat.onBeforeCompile = s => {
  s.uniforms.uTime = U.time;
  s.vertexShader = 'varying vec2 vUvC;\n' + s.vertexShader.replace(
    '#include <begin_vertex>', '#include <begin_vertex>\n vUvC = uv;');
  s.fragmentShader = 'uniform float uTime;\nvarying vec2 vUvC;\n' + s.fragmentShader.replace(
    '#include <emissivemap_fragment>', `#include <emissivemap_fragment>
    float cc = sin(vUvC.x*42.0+uTime*1.2)+sin(vUvC.y*37.0-uTime*0.9)+sin((vUvC.x+vUvC.y)*31.0+uTime*1.6);
    cc = max(cc,0.0)/3.0; cc = pow(cc,3.0);
    totalEmissiveRadiance += vec3(0.28,0.46,0.40)*cc*1.3;`);
};
const seabed = new THREE.Mesh(bedGeo, bedMat);
seabed.position.y = BOX.y0; seabed.receiveShadow = true; scene.add(seabed);

/* ============================================================
   6. ISLAND (lathe profile + noise + vertex colors)
============================================================ */
const profile = [
  [0.001,-6.3],[3.8,-6.2],[5.0,-5.0],[5.3,-2.0],[5.1,-0.6],
  [4.7,0.3],[4.0,1.2],[3.2,2.0],[2.4,2.7],[1.6,3.3],[0,3.38]
].map(p => new THREE.Vector2(p[0], p[1]));

const islandGeo = new THREE.LatheGeometry(profile, 44);
{
  const p = islandGeo.attributes.position;
  for (let i=0;i<p.count;i++){
    const x=p.getX(i), y=p.getY(i), z=p.getZ(i);
    const r = Math.hypot(x,z);
    if (r>0.02){
      const a = Math.atan2(z,x);
      const f = 1 + Math.sin(a*3 + y*1.7)*0.06 + Math.sin(a*7 - y*2.3)*0.03;
      p.setX(i, x*f); p.setZ(i, z*f);
    }
  }
  const colors = new Float32Array(p.count*3);
  const rock=new THREE.Color(0x6b5c4c), sand=new THREE.Color(0xd9c491), grass=new THREE.Color(0x5a8a44);
  const c = new THREE.Color();
  for (let i=0;i<p.count;i++){
    const y = p.getY(i);
    if (y < -0.4) c.copy(rock);
    else if (y < 0.9) c.copy(rock).lerp(sand, THREE.MathUtils.smoothstep(y,-0.4,0.9));
    else c.copy(sand).lerp(grass, THREE.MathUtils.smoothstep(y,0.9,1.7));
    // subtle variation
    const v = 1 + Math.sin(p.getX(i)*4+p.getZ(i)*3)*0.05;
    colors[i*3]=c.r*v; colors[i*3+1]=c.g*v; colors[i*3+2]=c.b*v;
  }
  islandGeo.setAttribute('color', new THREE.BufferAttribute(colors,3));
  islandGeo.computeVertexNormals();
}
const island = new THREE.Mesh(islandGeo,
  new THREE.MeshStandardMaterial({ vertexColors:true, roughness:0.95 }));
island.castShadow = true; island.receiveShadow = true;
scene.add(island);

// Height helper for object placement (top half of profile)
function islandHeight(r){
  const pts = profile.slice().reverse(); // r descending: 0 → 5.1
  for (let i=0;i<pts.length-1;i++){
    if (r >= pts[i].x && r <= pts[i+1].x){
      const t = (r-pts[i].x)/(pts[i+1].x-pts[i].x);
      return THREE.MathUtils.lerp(pts[i].y, pts[i+1].y, t);
    }
  }
  return 3.3;
}

/* ============================================================
   7. SWAYING FOLIAGE — trees, grass, kelp (instanced where many)
============================================================ */
function swayMaterial(base, amp, speed){
  const m = base.clone();
  m.onBeforeCompile = s => {
    s.uniforms.uTime = U.time; s.uniforms.uWind = U.wind;
    s.vertexShader = 'uniform float uTime; uniform float uWind;\n' + s.vertexShader.replace(
      '#include <begin_vertex>', `#include <begin_vertex>
      #ifdef USE_INSTANCING
        float ph = instanceMatrix[3].x*1.7 + instanceMatrix[3].z*2.3;
      #else
        float ph = 0.0;
      #endif
      float sway = sin(uTime*${speed.toFixed(1)} + ph + transformed.y*2.0) * uWind * ${amp.toFixed(2)} * max(transformed.y,0.0);
      transformed.x += sway; transformed.z += sway*0.5;`);
  };
  return m;
}

// Trees (few → groups, shared swaying foliage material)
const foliageMat = swayMaterial(new THREE.MeshStandardMaterial({ color:0x4e7f3d, roughness:0.9 }), 0.06, 2.0);
const trunkMat = new THREE.MeshStandardMaterial({ color:0x6b4f36, roughness:0.9 });
const trunkGeo = new THREE.CylinderGeometry(0.09, 0.14, 1.2, 7);
const coneGeo  = new THREE.ConeGeometry(1, 1, 9);
const treeSpots = [[2.0,-1.6,2.57],[-2.3,-0.8,2.68],[0.6,-2.3,2.72],[2.4,1.2,2.48]];
for (const [tx,tz,ty] of treeSpots){
  const g = new THREE.Group();
  const trunk = new THREE.Mesh(trunkGeo, trunkMat); trunk.position.y=0.6; trunk.castShadow=true; g.add(trunk);
  const c1 = new THREE.Mesh(coneGeo, foliageMat); c1.scale.set(0.7,1.3,0.7); c1.position.y=1.6; c1.castShadow=true; g.add(c1);
  const c2 = new THREE.Mesh(coneGeo, foliageMat); c2.scale.set(0.5,1.0,0.5); c2.position.y=2.3; c2.castShadow=true; g.add(c2);
  g.position.set(tx, ty, tz);
  g.rotation.y = Math.random()*Math.PI;
  scene.add(g);
}

// Grass blades on plateau (InstancedMesh)
const bladeGeo = new THREE.PlaneGeometry(0.06, 0.45, 1, 2);
bladeGeo.translate(0, 0.22, 0);
const grassMat = swayMaterial(new THREE.MeshStandardMaterial({ color:0x6fa353, roughness:1, side:THREE.DoubleSide }), 0.15, 2.6);
const grass = new THREE.InstancedMesh(bladeGeo, grassMat, 240);
{
  const d = new THREE.Object3D();
  for (let i=0;i<240;i++){
    const a = Math.random()*Math.PI*2, r = Math.sqrt(Math.random())*2.5;
    d.position.set(Math.cos(a)*r, islandHeight(r)-0.03, Math.sin(a)*r);
    d.rotation.set(0, Math.random()*Math.PI, (Math.random()-0.5)*0.3);
    d.scale.setScalar(0.7+Math.random()*0.7);
    d.updateMatrix(); grass.setMatrixAt(i, d.matrix);
  }
}
scene.add(grass);

// Rocks on shoreline (InstancedMesh)
const rockGeo = new THREE.DodecahedronGeometry(0.35, 0);
const rockMat = new THREE.MeshStandardMaterial({ color:0x776858, roughness:0.95 });
const rocks = new THREE.InstancedMesh(rockGeo, rockMat, 14);
{
  const d = new THREE.Object3D();
  for (let i=0;i<14;i++){
    const a = Math.random()*Math.PI*2, r = 4.5+Math.random()*0.9;
    d.position.set(Math.cos(a)*r, islandHeight(r)+0.1, Math.sin(a)*r);
    d.rotation.set(Math.random()*3, Math.random()*3, Math.random()*3);
    d.scale.set(0.6+Math.random()*1.1, 0.5+Math.random()*0.8, 0.6+Math.random()*1.1);
    d.updateMatrix(); rocks.setMatrixAt(i, d.matrix);
  }
}
rocks.castShadow = true; rocks.receiveShadow = true; scene.add(rocks);

// Stepping stones down to the pier
const stoneGeo = new THREE.CylinderGeometry(0.3, 0.34, 0.1, 8);
const stones = new THREE.InstancedMesh(stoneGeo, rockMat, 6);
{
  const d = new THREE.Object3D();
  for (let i=0;i<6;i++){
    const r = 2.6 + i*0.4, a = 0.71; // toward pier
    d.position.set(Math.cos(a)*r, islandHeight(r)+0.04, Math.sin(a)*r);
    d.rotation.y = Math.random()*Math.PI;
    d.updateMatrix(); stones.setMatrixAt(i, d.matrix);
  }
}
stones.receiveShadow = true; stones.castShadow = true; scene.add(stones);

/* ============================================================
   8. CABIN — A-frame, copper roof, glowing windows, deck & props
============================================================ */
const lampMats = []; // emissive materials that respond to time of day
function glowMat(){
  const m = new THREE.MeshStandardMaterial({ color:0xffd9a0, emissive:0xffb45e, emissiveIntensity:0, roughness:0.6 });
  lampMats.push(m); return m;
}
const cabin = new THREE.Group();
cabin.position.set(-0.4, 3.22, -0.6);

// A-frame shell
const tri = new THREE.Shape();
tri.moveTo(-1.5,0); tri.lineTo(1.5,0); tri.lineTo(0,2.3); tri.closePath();
const shell = new THREE.Mesh(new THREE.ExtrudeGeometry(tri,{depth:2.3,bevelEnabled:false}), woodMat);
shell.translate(0,0,-1.15); shell.castShadow=true; shell.receiveShadow=true; cabin.add(shell);

// Copper roof panels
const slope = Math.atan2(2.3,1.5);
const roofGeo = new THREE.BoxGeometry(3.0, 0.07, 2.7);
const roofL = new THREE.Mesh(roofGeo, copper);
roofL.rotation.z = slope; roofL.position.set(-0.78, 1.22, 0); roofL.castShadow=true; cabin.add(roofL);
const roofR = new THREE.Mesh(roofGeo, copper);
roofR.rotation.z = -slope; roofR.position.set(0.78, 1.22, 0); roofR.castShadow=true; cabin.add(roofR);
const ridge = new THREE.Mesh(new THREE.BoxGeometry(0.14,0.1,2.8), copper);
ridge.position.set(0,2.38,0); cabin.add(ridge);

// Gable window (glowing triangle), door, round back window
const winTri = new THREE.Shape();
winTri.moveTo(-0.85,0.45); winTri.lineTo(0.85,0.45); winTri.lineTo(0,1.7); winTri.closePath();
const gableWin = new THREE.Mesh(new THREE.ShapeGeometry(winTri), glowMat());
gableWin.position.z = 1.16; cabin.add(gableWin);
const door = new THREE.Mesh(new THREE.PlaneGeometry(0.55,1.0), darkWood);
door.position.set(0,0.5,1.16); cabin.add(door);
const backWin = new THREE.Mesh(new THREE.CircleGeometry(0.28,12), glowMat());
backWin.position.set(0,1.2,-1.16); backWin.rotation.y = Math.PI; cabin.add(backWin);

// Warm interior light
const cabinLight = new THREE.PointLight(0xffb45e, 0, 7, 2);
cabinLight.position.set(0,1.2,0.4); cabin.add(cabinLight);

// Deck + railing + towels
const deck = new THREE.Mesh(new THREE.BoxGeometry(2.8,0.1,1.5), woodMat);
deck.position.set(0,-0.05,1.9); deck.castShadow=true; deck.receiveShadow=true; cabin.add(deck);
const postGeo = new THREE.CylinderGeometry(0.045,0.045,0.55,6);
for (const px of [-1.35,-0.81,-0.27,0.27,0.81,1.35]){
  const p = new THREE.Mesh(postGeo, darkWood); p.position.set(px,0.32,2.6); p.castShadow=true; cabin.add(p);
}
const rail = new THREE.Mesh(new THREE.BoxGeometry(2.8,0.06,0.06), darkWood);
rail.position.set(0,0.58,2.6); cabin.add(rail);
const towel1 = new THREE.Mesh(new THREE.BoxGeometry(0.55,0.03,0.3), new THREE.MeshStandardMaterial({color:0xe2725b, roughness:1}));
towel1.position.set(-0.7,0.62,2.6); towel1.rotation.x=0.15; cabin.add(towel1);
const towel2 = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.03,0.3), new THREE.MeshStandardMaterial({color:0x5fb8a5, roughness:1}));
towel2.position.set(0.85,0.62,2.6); towel2.rotation.x=0.15; cabin.add(towel2);

// Crates & potted plants
const crateMat = new THREE.MeshStandardMaterial({ color:0x9c7a52, roughness:0.9 });
for (const [cx,cz,ry] of [[-1.9,1.0,0.4],[-1.45,1.25,-0.2],[-1.85,1.5,0.9]]){
  const cr = new THREE.Mesh(new THREE.BoxGeometry(0.45,0.45,0.45), crateMat);
  cr.position.set(cx,0.23,cz); cr.rotation.y=ry; cr.castShadow=true; cabin.add(cr);
}
const potMat = new THREE.MeshStandardMaterial({ color:0xb0673f, roughness:0.9 });
const leafMat = swayMaterial(new THREE.MeshStandardMaterial({ color:0x5c9a4d, roughness:1, side:THREE.DoubleSide }), 0.1, 3.0);
for (const [px,pz] of [[1.3,2.4],[-1.3,2.4],[1.5,1.2]]){
  const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.14,0.11,0.22,8), potMat);
  pot.position.set(px,0.11,pz); pot.castShadow=true; cabin.add(pot);
  const bush = new THREE.Mesh(new THREE.ConeGeometry(0.18,0.4,7), leafMat);
  bush.position.set(px,0.42,pz); cabin.add(bush);
}
scene.add(cabin);

// Bench on the hill
const bench = new THREE.Group();
const seat = new THREE.Mesh(new THREE.BoxGeometry(0.95,0.07,0.32), woodMat);
seat.position.y=0.42; seat.castShadow=true; bench.add(seat);
for (const bx of [-0.4,0.4]) for (const bz of [-0.11,0.11]){
  const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06,0.42,0.06), darkWood);
  leg.position.set(bx,0.21,bz); bench.add(leg);
}
bench.position.set(1.7, islandHeight(2.5), 1.8); bench.rotation.y=-0.6;
scene.add(bench);

/* ============================================================
   9. PIER — planks, posts, ladder, lanterns
============================================================ */
const pier = new THREE.Group();
const pStart = new THREE.Vector2(3.2, 2.7), pEnd = new THREE.Vector2(6.6, 5.4);
const pDir = pEnd.clone().sub(pStart);
const pLen = pDir.length(); const pAng = Math.atan2(pDir.x, pDir.y); // for group yaw
const DECK_Y = 0.78;

const plankGeo = new THREE.BoxGeometry(1.15, 0.07, 0.2);
const planks = new THREE.InstancedMesh(plankGeo, woodMat, 20);
{
  const d = new THREE.Object3D();
  for (let i=0;i<20;i++){
    const t = i/19;
    d.position.set(0, 0, -pLen/2 + t*pLen);
    d.updateMatrix(); planks.setMatrixAt(i, d.matrix);
  }
}
planks.castShadow = true; planks.receiveShadow = true; pier.add(planks);

const pierPostGeo = new THREE.CylinderGeometry(0.09,0.11, DECK_Y-BOX.y0+0.2, 8);
for (const sx of [-0.5,0.5]) for (const sz of [-pLen/2+0.15, pLen/2-0.15]){
  const p = new THREE.Mesh(pierPostGeo, darkWood);
  p.position.set(sx, (DECK_Y+BOX.y0)/2 - 0.05, sz); p.castShadow=true; pier.add(p);
}

// Ladder at the pier end
const ladder = new THREE.Group();
const railGeo = new THREE.CylinderGeometry(0.035,0.035,1.5,6);
for (const lx of [-0.2,0.2]){
  const r = new THREE.Mesh(railGeo, darkWood); r.position.set(lx,-0.7,0); ladder.add(r);
}
const rungGeo = new THREE.CylinderGeometry(0.03,0.03,0.4,6);
for (let i=0;i<4;i++){
  const r = new THREE.Mesh(rungGeo, darkWood);
  r.rotation.z = Math.PI/2; r.position.set(0,-0.25-i*0.35,0); ladder.add(r);
}
ladder.position.set(0.55, DECK_Y, pLen/2 - 0.1); pier.add(ladder);

// Lanterns (mid + end)
const lanternMats = [], lanternLights = [];
for (const lz of [-pLen/4, pLen/2-0.3]){
  const post = new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.05,0.8,6), darkWood);
  post.position.set(-0.5, DECK_Y+0.4, lz); post.castShadow=true; pier.add(post);
  const lm = glowMat(); lanternMats.push(lm);
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.1,10,8), lm);
  bulb.position.set(-0.5, DECK_Y+0.85, lz); pier.add(bulb);
  const cap = new THREE.Mesh(new THREE.ConeGeometry(0.13,0.12,8), copper);
  cap.position.set(-0.5, DECK_Y+0.99, lz); pier.add(cap);
  const pl = new THREE.PointLight(0xffc46b, 0, 6, 2);
  pl.position.set(-0.5, DECK_Y+0.85, lz); pier.add(pl); lanternLights.push(pl);
}
pier.position.set((pStart.x+pEnd.x)/2, DECK_Y, (pStart.y+pEnd.y)/2);
pier.rotation.y = -pAng + Math.PI/2;
scene.add(pier);

/* ============================================================
   10. KAYAK
============================================================ */
const kayak = new THREE.Group();
const hullGeo = new THREE.CapsuleGeometry(0.2, 1.15, 4, 10);
hullGeo.rotateX(Math.PI/2);
const hull = new THREE.Mesh(hullGeo, new THREE.MeshStandardMaterial({ color:0xe2725b, roughness:0.55 }));
hull.scale.set(1,0.6,1.15); hull.castShadow=true; kayak.add(hull);
const cockpit = new THREE.Mesh(new THREE.CylinderGeometry(0.16,0.16,0.35,10), darkWood);
cockpit.rotation.x = Math.PI/2; cockpit.scale.set(1,0.12,1); kayak.add(cockpit);
const paddle = new THREE.Mesh(new THREE.CylinderGeometry(0.02,0.02,1.1,6), darkWood);
paddle.rotation.z = Math.PI/2; paddle.rotation.y = 0.4; paddle.position.y = 0.16; kayak.add(paddle);
scene.add(kayak);

const KAYAK_C = new THREE.Vector2(0, 0.5), KAYAK_R = 7.2;
const dockAngle = Math.atan2(4.4-KAYAK_C.y, 6.4-KAYAK_C.x);
let kayakState = 'moored', kayakAngle = dockAngle, kayakBlend = 0;

/* ============================================================
   11. WATER — volume tint + animated surface (cutaway)
   Draw order: opaque world → volume(1) → surface(2) → ripples(4) → glass(5)
============================================================ */
const volMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, side:THREE.FrontSide,
  uniforms:{ uLevel:U.level },
  vertexShader:`
    varying vec3 vView; varying vec3 vN;
    void main(){
      vec4 mv = modelViewMatrix*vec4(position,1.0);
      vView = mv.xyz; vN = normalize(normalMatrix*normal);
      gl_Position = projectionMatrix*mv;
    }`,
  fragmentShader:`
    varying vec3 vView; varying vec3 vN; uniform float uLevel;
    void main(){
      vec3 V = normalize(-vView);
      float fres = pow(1.0-abs(dot(normalize(vN),V)),2.0);
      float depth = clamp((uLevel - (vView.y))/8.0, 0.0, 1.0); // approx
      vec3 col = mix(vec3(0.24,0.62,0.60), vec3(0.05,0.28,0.38), depth);
      float a = 0.06 + fres*0.30 + depth*0.18;
      gl_FragColor = vec4(col, a);
    }`
});
const waterVolume = new THREE.Mesh(new THREE.BoxGeometry(1,1,1), volMat);
waterVolume.renderOrder = 1; scene.add(waterVolume);

const surfGeo = new THREE.PlaneGeometry(24, 16, 90, 60);
surfGeo.rotateX(-Math.PI/2);
const surfMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, side:THREE.DoubleSide,
  uniforms:{ uTime:U.time, uWind:U.wind, uLevel:U.level,
             uSunDir:{value:new THREE.Vector3(8,13,6)}, uSpec:{value:0.8} },
  vertexShader:`
    uniform float uTime; uniform float uWind;
    varying vec3 vWorld;
    void main(){
      vec3 p = position;
      float amp = 0.04 + 0.22*uWind;
      float w = sin(p.x*0.8 + uTime*1.6)*0.5
              + sin(p.z*1.1 - uTime*1.2)*0.4
              + sin((p.x+p.z)*0.6 + uTime*0.9)*0.3;
      p.y += w*amp;
      vec4 wp = modelMatrix*vec4(p,1.0);
      vWorld = wp.xyz;
      gl_Position = projectionMatrix*viewMatrix*wp;
    }`,
  fragmentShader:`
    uniform float uTime; uniform float uWind; uniform float uLevel;
    uniform vec3 uSunDir; uniform float uSpec;
    varying vec3 vWorld;
    void main(){
      vec3 nrm = normalize(cross(dFdx(vWorld), dFdy(vWorld)));
      vec3 V = normalize(cameraPosition - vWorld);
      float fres = pow(1.0-abs(dot(nrm,V)),3.0);
      // shoreline foam
      float d = length(vWorld.xz);
      float ang = atan(vWorld.z, vWorld.x);
      float shoreR = 5.1 - uLevel*0.3;
      float f = smoothstep(shoreR+0.55, shoreR-0.15, d);
      f *= 0.55 + 0.45*sin(d*5.0 - uTime*2.5 + ang*4.0);
      f = clamp(f,0.0,1.0) * (0.4+0.6*uWind+0.2);
      vec3 shallow = vec3(0.30,0.72,0.68), deep = vec3(0.10,0.42,0.52);
      vec3 col = mix(deep, shallow, 0.45+0.2*fres);
      col = mix(col, vec3(0.95,0.98,1.0), f);
      vec3 H = normalize(normalize(uSunDir)+V);
      float spec = pow(max(dot(nrm,H),0.0),60.0)*uSpec;
      col += vec3(1.0)*spec;
      float a = clamp(0.5 + fres*0.45 + f*0.45 + spec*0.3, 0.0, 0.95);
      gl_FragColor = vec4(col, a);
    }`
});
const waterSurface = new THREE.Mesh(surfGeo, surfMat);
waterSurface.renderOrder = 2; scene.add(waterSurface);

// JS wave sampler matching the shader (for floating objects)
function waveY(x,z,t,wind){
  const amp = 0.04 + 0.22*wind;
  return (Math.sin(x*0.8+t*1.6)*0.5 + Math.sin(z*1.1-t*1.2)*0.4 +
          Math.sin((x+z)*0.6+t*0.9)*0.3) * amp;
}

/* ============================================================
   12. UNDERWATER LIFE — kelp, bubbles, fish schools, rays
============================================================ */
// Kelp (instanced, swaying)
const kelpGeo = new THREE.PlaneGeometry(0.2, 1.7, 1, 5); kelpGeo.translate(0,0.85,0);
const kelpMat = swayMaterial(new THREE.MeshStandardMaterial({ color:0x2f7d55, roughness:0.8, side:THREE.DoubleSide }), 0.22, 1.6);
const kelp = new THREE.InstancedMesh(kelpGeo, kelpMat, 26);
{
  const d = new THREE.Object3D();
  for (let i=0;i<26;i++){
    d.position.set((Math.random()*2-1)*10.5, BOX.y0+0.1, (Math.random()*2-1)*6.5);
    d.rotation.y = Math.random()*Math.PI;
    d.scale.setScalar(0.7+Math.random()*0.9);
    d.updateMatrix(); kelp.setMatrixAt(i, d.matrix);
  }
}
scene.add(kelp);

// Underwater rocks
const uRocks = new THREE.InstancedMesh(rockGeo, rockMat, 10);
{
  const d = new THREE.Object3D();
  for (let i=0;i<10;i++){
    d.position.set((Math.random()*2-1)*10, BOX.y0+0.2, (Math.random()*2-1)*6.5);
    d.rotation.set(Math.random()*3,Math.random()*3,Math.random()*3);
    d.scale.setScalar(0.7+Math.random()*1.3);
    d.updateMatrix(); uRocks.setMatrixAt(i, d.matrix);
  }
}
scene.add(uRocks);

// Bubbles
const bubGeo = new THREE.SphereGeometry(0.05, 8, 6);
const bubMat = new THREE.MeshStandardMaterial({ color:0xdff6f2, transparent:true, opacity:0.75, roughness:0.2 });
const BUB_N = 45;
const bubbles = new THREE.InstancedMesh(bubGeo, bubMat, BUB_N);
const bubData = [];
for (let i=0;i<BUB_N;i++)
  bubData.push({ x:(Math.random()*2-1)*10.5, z:(Math.random()*2-1)*6.5,
                 y:BOX.y0+Math.random()*6, s:0.4+Math.random()*0.9, sp:0.25+Math.random()*0.35 });
scene.add(bubbles);

// Fish schools (InstancedMesh per school)
const fishGeo = mergeGeometries([
  (()=>{ const g=new THREE.ConeGeometry(0.05,0.16,6); g.rotateZ(-Math.PI/2); g.translate(0.05,0,0); return g; })(),
  (()=>{ const g=new THREE.ConeGeometry(0.055,0.09,4); g.rotateZ(Math.PI/2); g.scale(1,1,0.45); g.translate(-0.09,0,0); return g; })()
]);
const schools = [
  { color:0xff9a5a, n:14, c:new THREE.Vector2(-6.5,-4.0), r:2.2, sp:0.35, ph:0.0, y:-2.6 },
  { color:0xf4d06f, n:14, c:new THREE.Vector2(7.0,-4.8),  r:2.4, sp:-0.3, ph:2.1, y:-3.3 },
  { color:0x8fd0c0, n:12, c:new THREE.Vector2(0.5,5.8),   r:1.8, sp:0.42, ph:4.4, y:-2.2 }
];
for (const s of schools){
  s.mesh = new THREE.InstancedMesh(fishGeo,
    new THREE.MeshStandardMaterial({ color:s.color, roughness:0.6 }), s.n);
  scene.add(s.mesh);
}

// Manta rays — procedural wing grid animated on CPU
function buildRay(){
  const nx=13, nz=11, uvB=[], pos=[], idx=[];
  for (let j=0;j<nz;j++){ const v=j/(nz-1);
    for (let i=0;i<nx;i++){ const u=-1+2*i/(nx-1);
      uvB.push([u,v]); pos.push(0,0,0);
    }}
  for (let j=0;j<nz-1;j++) for (let i=0;i<nx-1;i++){
    const a=j*nx+i, b=a+1, c=a+nx, d=c+1;
    idx.push(a,c,b, b,c,d);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  geo.setIndex(idx); geo.computeVertexNormals();
  return { geo, uvB, nx, nz };
}
const rayMat = new THREE.MeshStandardMaterial({ color:0x46586a, roughness:0.7, side:THREE.DoubleSide });
const tailGeoBase = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
  new THREE.Vector3(0,0,-1.15), new THREE.Vector3(0,0.05,-1.9), new THREE.Vector3(0,-0.02,-2.6)
]), 12, 0.05, 6, false);
const eyeGeo = new THREE.SphereGeometry(0.05,8,6);
const eyeMat = new THREE.MeshStandardMaterial({ color:0x101418 });

const rays = [];
const RAY_CFG = [
  { R:4.6, sp:0.22, ph:0.0,  y:-2.4, cx:0.5,  cz:0.5 },
  { R:3.8, sp:-0.27, ph:2.4, y:-3.4, cx:-1.5, cz:-1.0 },
  { R:5.2, sp:0.18, ph:4.2,  y:-2.9, cx:1.0,  cz:-0.5 }
];
for (const cfg of RAY_CFG){
  const { geo, uvB } = buildRay();
  const body = new THREE.Mesh(geo, rayMat);
  const group = new THREE.Group(); group.add(body);
  const tailMat = rayMat.clone();
  tailMat.onBeforeCompile = s => {
    s.uniforms.uTime = U.time; s.uniforms.uPhase = { value: cfg.ph };
    s.vertexShader = 'uniform float uTime; uniform float uPhase;\n' + s.vertexShader.replace(
      '#include <begin_vertex>', `#include <begin_vertex>
      transformed.x += sin(uTime*2.2 + uPhase + position.z*2.5)*0.14*clamp(-(position.z+1.0),0.0,1.6);`);
  };
  group.add(new THREE.Mesh(tailGeoBase, tailMat));
  for (const ex of [-0.35,0.35]){
    const e = new THREE.Mesh(eyeGeo, eyeMat); e.position.set(ex,0.09,0.95); group.add(e);
  }
  group.scale.setScalar(1.15);
  scene.add(group);
  rays.push({ group, body, geo, uvB, cfg, prevY:cfg.y, jump:null });
}

function animateRayBody(r, t){
  const pos = r.geo.attributes.position.array, { uvB, nx, nz } = r;
  const flap = Math.sin((r.jump? 4.5 : 2.0)*t + r.cfg.ph);
  let k=0;
  for (let j=0;j<nz;j++){ const v=j/(nz-1);
    for (let i=0;i<nx;i++){ const [u,vv]=uvB[k++];
      const span = 1.35*Math.sin(Math.PI*Math.pow(v,0.85));
      pos[k*3+0] = u*span;
      pos[k*3+1] = 0.16*Math.sin(Math.PI*v)*(1-Math.abs(u)*0.7)
                 + 0.5*Math.abs(u)*Math.sin(2.0*t + v*3.0 + r.cfg.ph);
      pos[k*3+2] = (v-0.5)*2.4;
    }}
  r.geo.attributes.position.needsUpdate = true;
  r.geo.computeVertexNormals();
}

/* ============================================================
   13. EFFECTS — ripples & splash droplets
============================================================ */
const rippleGeo = new THREE.RingGeometry(0.9, 1.0, 40);
rippleGeo.rotateX(-Math.PI/2);
const ripples = [];
for (let i=0;i<4;i++){
  const m = new THREE.Mesh(rippleGeo, new THREE.MeshBasicMaterial({
    color:0xeafcff, transparent:true, opacity:0, blending:THREE.AdditiveBlending, depthWrite:false }));
  m.renderOrder = 4; m.visible = false; scene.add(m);
  ripples.push({ mesh:m, t:-1, delay:0 });
}
function spawnRipple(x,z,delay){
  const r = ripples.find(r=>r.t<0); if(!r) return;
  r.t = 0; r.delay = delay||0; r.mesh.visible = true;
  r.mesh.position.set(x, U.level.value+0.03, z);
}

const dropGeo = new THREE.SphereGeometry(0.06, 8, 6);
const dropMat = new THREE.MeshStandardMaterial({ color:0xbfeef0, roughness:0.1, transparent:true, opacity:0.9 });
const DROP_N = 26;
const drops = new THREE.InstancedMesh(dropGeo, dropMat, DROP_N);
const dropData = []; for (let i=0;i<DROP_N;i++) dropData.push({ life:-1 });
scene.add(drops);
function spawnDroplets(p){
  let n = 0;
  for (const d of dropData){
    if (n>=12) break;
    if (d.life < 0){
      d.life = 0;
      d.x=p.x+(Math.random()-0.5)*0.6; d.y=p.y+0.3; d.z=p.z+(Math.random()-0.5)*0.6;
      d.vx=(Math.random()-0.5)*2.2; d.vy=2.5+Math.random()*2.5; d.vz=(Math.random()-0.5)*2.2;
      n++;
    }
  }
}

/* ============================================================
   14. UI WIRING
============================================================ */
const $ = id => document.getElementById(id);
const tideEl=$('tide'), windEl=$('wind'), volEl=$('vol');
const kayakBtn=$('kayakBtn'), rayBtn=$('rayBtn'), pauseBtn=$('pauseBtn'), resetBtn=$('resetBtn');
const musicBtn=$('musicBtn');

// Camera presets + smooth transitions
const CAMS = {
  iso:    { pos:new THREE.Vector3(17,13,17),  tgt:new THREE.Vector3(0,0,0) },
  cabin:  { pos:new THREE.Vector3(9,3.6,9.5), tgt:new THREE.Vector3(-0.5,1.6,1.5) },
  under:  { pos:new THREE.Vector3(8,-3,5),    tgt:new THREE.Vector3(0,-2.6,0) }
};
let camTrans = null;
document.querySelectorAll('[data-cam]').forEach(b=>{
  b.addEventListener('click', ()=>{
    document.querySelectorAll('[data-cam]').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    camTrans = CAMS[b.dataset.cam];
    tick();
  });
});

// Time of day
document.querySelectorAll('[data-time]').forEach(b=>{
  b.addEventListener('click', ()=>{
    document.querySelectorAll('[data-time]').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    target = TIME_PRESETS[b.dataset.time];
    tick();
  });
});

kayakBtn.addEventListener('click', ()=>{
  if (kayakState==='moored'){ kayakState='out'; kayakBtn.textContent='Recall Kayak'; kayakBtn.classList.add('active'); }
  else if (kayakState==='out'){ kayakState='returning'; }
  tick();
});

rayBtn.addEventListener('click', ()=>{
  const r = rays[0];
  if (!r.jump){
    const p = r.group.position.clone();
    const dir = new THREE.Vector2(p.x, p.z);
    if (dir.length()<0.3) dir.set(1,0.5); dir.normalize().multiplyScalar(3.2);
    r.jump = { t:0, dur:2.8, p0:p, dx:dir.x, dz:dir.y, H:2.8, splashed:false };
  }
  tick();
});

pauseBtn.addEventListener('click', ()=>{
  paused = !paused;
  pauseBtn.textContent = paused ? 'Resume' : 'Pause';
  pauseBtn.classList.toggle('active', paused);
  tick();
});

resetBtn.addEventListener('click', ()=>{
  tideEl.value=0; windEl.value=0.5; U.wind.value=0.5;
  kayakState='moored'; kayakBtn.textContent='Launch Kayak'; kayakBtn.classList.remove('active');
  rays[0].jump=null; paused=false; pauseBtn.textContent='Pause'; pauseBtn.classList.remove('active');
  camTrans = CAMS.iso;
  document.querySelectorAll('[data-time]').forEach(x=>x.classList.toggle('active', x.dataset.time==='day'));
  target = TIME_PRESETS.day;
  tick();
});

$('collapseBtn').addEventListener('click', ()=> document.body.classList.toggle('panels-hidden'));

/* ============================================================
   15. AUDIO — procedural music, breeze, water, splash (Web Audio)
============================================================ */
let actx=null, master, musicGain, breezeGain, waterGain, melodyTimer=null, musicOn=false;
let volVal = 0.7;

function initAudio(){
  if (actx) return;
  actx = new (window.AudioContext||window.webkitAudioContext)();
  master = actx.createGain(); master.gain.value = volVal; master.connect(actx.destination);

  // Chord pad
  musicGain = actx.createGain(); musicGain.gain.value = 0;
  const lp = actx.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=1100;
  lp.connect(musicGain); musicGain.connect(master);
  [110,164.8,220,261.6].forEach((f,i)=>{
    const o=actx.createOscillator(); o.type='sine'; o.frequency.value=f; o.detune.value=(i-1)*3;
    const g=actx.createGain(); g.gain.value=0.05; o.connect(g); g.connect(lp); o.start();
  });
  const lfo=actx.createOscillator(); lfo.frequency.value=0.08;
  const lfoG=actx.createGain(); lfoG.gain.value=350; lfo.connect(lfoG); lfoG.connect(lp.frequency); lfo.start();

  // Gentle echo for melody
  const delay=actx.createDelay(); delay.delayTime.value=0.42;
  const fb=actx.createGain(); fb.gain.value=0.35;
  delay.connect(fb); fb.connect(delay); delay.connect(musicGain);
  window._melodyBus = delay;

  // Noise-based ambience
  const nb = actx.createBuffer(1, actx.sampleRate*2, actx.sampleRate);
  const ch = nb.getChannelData(0);
  for (let i=0;i<ch.length;i++) ch[i]=Math.random()*2-1;

  breezeGain = actx.createGain(); breezeGain.gain.value = 0.055;
  const bp = actx.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=650; bp.Q.value=0.7;
  const bs = actx.createBufferSource(); bs.buffer=nb; bs.loop=true;
  bs.connect(bp); bp.connect(breezeGain); breezeGain.connect(master); bs.start();

  waterGain = actx.createGain(); waterGain.gain.value = 0.035;
  const wl = actx.createBiquadFilter(); wl.type='lowpass'; wl.frequency.value=320;
  const ws = actx.createBufferSource(); ws.buffer=nb; ws.loop=true;
  const wLfo=actx.createOscillator(); wLfo.frequency.value=0.18;
  const wLfoG=actx.createGain(); wLfoG.gain.value=0.02;
  ws.connect(wl); wl.connect(waterGain); waterGain.connect(master);
  wLfo.connect(wLfoG); wLfoG.connect(waterGain.gain);
  ws.start(); wLfo.start();
}
document.addEventListener('pointerdown', initAudio, { once:true });

function tick(){
  if (!actx) return;
  const o=actx.createOscillator(), g=actx.createGain();
  o.frequency.value=880; g.gain.setValueAtTime(0.05, actx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.0001, actx.currentTime+0.09);
  o.connect(g); g.connect(master); o.start(); o.stop(actx.currentTime+0.1);
}
function splashSound(){
  if (!actx) return;
  const src=actx.createBufferSource(); const nb=actx.createBuffer(1, actx.sampleRate*0.6, actx.sampleRate);
  const ch=nb.getChannelData(0); for(let i=0;i<ch.length;i++) ch[i]=(Math.random()*2-1)*(1-i/ch.length);
  src.buffer=nb;
  const bp=actx.createBiquadFilter(); bp.type='bandpass';
  bp.frequency.setValueAtTime(900, actx.currentTime);
  bp.frequency.exponentialRampToValueAtTime(140, actx.currentTime+0.55);
  const g=actx.createGain(); g.gain.setValueAtTime(0.5, actx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime+0.6);
  src.connect(bp); bp.connect(g); g.connect(master); src.start();
}

musicBtn.addEventListener('click', ()=>{
  musicOn = !musicOn;
  musicBtn.textContent = 'Music: ' + (musicOn?'On':'Off');
  musicBtn.classList.toggle('active', musicOn);
  if (actx){
    musicGain.gain.cancelScheduledValues(actx.currentTime);
    musicGain.gain.linearRampToValueAtTime(musicOn?0.6:0, actx.currentTime+0.8);
  }
  if (musicOn && !melodyTimer){
    melodyTimer = setInterval(()=>{
      if (!actx || !musicOn) return;
      const notes=[220,261.6,293.7,329.6,392,440,523.3];
      const f = notes[Math.floor(Math.random()*notes.length)];
      const o=actx.createOscillator(), g=actx.createGain();
      o.type='triangle'; o.frequency.value=f;
      g.gain.setValueAtTime(0, actx.currentTime);
      g.gain.linearRampToValueAtTime(0.09, actx.currentTime+0.05);
      g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime+1.4);
      o.connect(g); g.connect(window._melodyBus); g.connect(musicGain);
      o.start(); o.stop(actx.currentTime+1.5);
    }, 2400);
  } else if (!musicOn && melodyTimer){ clearInterval(melodyTimer); melodyTimer=null; }
});

tideEl.addEventListener('input', ()=>{ U.level.value = BASE_LEVEL + parseFloat(tideEl.value)*0.8; });
windEl.addEventListener('input', ()=>{
  U.wind.value = parseFloat(windEl.value);
  if (actx) breezeGain.gain.value = 0.02 + U.wind.value*0.10;
});
volEl.addEventListener('input', ()=>{
  volVal = parseFloat(volEl.value);
  if (actx) master.gain.value = volVal;
});

/* ============================================================
   16. MAIN LOOP
============================================================ */
const clock = new THREE.Clock();
const dummy = new THREE.Object3D();

function update(dt, t){
  // --- water level & volume ---
  const level = U.level.value;
  waterSurface.position.y = level;
  const vH = level - 0.05 - BOX.y0;
  waterVolume.scale.set(23.9, vH, 15.9);
  waterVolume.position.y = BOX.y0 + vH/2;
  surfMat.uniforms.uSunDir.value.copy(cur.pos);
  surfMat.uniforms.uSpec.value = cur.spec;

  // --- time of day blending ---
  const k = 1 - Math.exp(-dt*1.4);
  cur.sky.lerp(new THREE.Color(target.sky), k);
  cur.sunC.lerp(new THREE.Color(target.sunC), k);
  cur.sunI += (target.sunI-cur.sunI)*k;
  cur.hemiI += (target.hemiI-cur.hemiI)*k;
  cur.ambI += (target.ambI-cur.ambI)*k;
  cur.lamp += (target.lamp-cur.lamp)*k;
  cur.night += (target.night-cur.night)*k;
  cur.spec += (target.spec-cur.spec)*k;
  cur.pos.lerp(new THREE.Vector3(...target.pos), k);
  sun.color.copy(cur.sunC); sun.intensity = cur.sunI; sun.position.copy(cur.pos);
  hemi.intensity = cur.hemiI; hemi.color.copy(cur.sky);
  ambient.intensity = cur.ambI;
  scene.background = cur.sky; scene.fog.color.copy(cur.sky);
  starMat.opacity = cur.night*0.9;
  for (const m of lampMats) m.emissiveIntensity = cur.lamp*1.4;
  cabinLight.intensity = cur.lamp*2.2;
  for (const pl of lanternLights) pl.intensity = cur.lamp*1.6;

  // --- kayak ---
  if (kayakState==='out'){
    kayakAngle += dt*0.45;
    if (kayakAngle > dockAngle + Math.PI*2) { kayakState='returning'; }
  } else if (kayakState==='returning'){
    kayakAngle -= dt*0.5;
    if (kayakAngle <= dockAngle){ kayakAngle = dockAngle; kayakState='moored';
      kayakBtn.textContent='Launch Kayak'; kayakBtn.classList.remove('active'); }
  }
  const kx = KAYAK_C.x + KAYAK_R*Math.cos(kayakAngle);
  const kz = KAYAK_C.y + KAYAK_R*Math.sin(kayakAngle);
  kayak.position.set(kx, level + waveY(kx,kz,t,U.wind.value)*0.6 + 0.12, kz);
  kayak.rotation.y = -kayakAngle + Math.PI/2;
  kayak.rotation.z = Math.sin(t*1.1)*0.05*(0.5+U.wind.value);
  kayak.rotation.x = Math.cos(t*0.9)*0.04;

  // --- rays ---
  for (const r of rays){
    const c = r.cfg;
    if (r.jump){
      const j = r.jump; j.t += dt;
      const p = Math.min(j.t/j.dur, 1);
      const x = THREE.MathUtils.lerp(j.p0.x, j.p0.x+j.dx, p);
      const z = THREE.MathUtils.lerp(j.p0.z, j.p0.z+j.dz, p);
      const y = THREE.MathUtils.lerp(j.p0.y, level-0.7, p) + 4*j.H*p*(1-p);
      r.group.position.set(x,y,z);
      const dirX = j.dx, dirZ = j.dz;
      r.group.rotation.y = Math.atan2(dirX, dirZ);
      r.group.rotation.x = -Math.sin(Math.PI*Math.min(p*1.15,1))*0.9;
      if (!j.splashed && p>0.72){
        j.splashed = true; splashSound();
        spawnRipple(x,z,0); spawnRipple(x,z,0.35); spawnDroplets(new THREE.Vector3(x,level,z));
      }
      if (p>=1){
        // resume swimming from landing point
        const a = Math.atan2((z-c.cz)/0.8, (x-c.cx));
        c.ph = a - t*c.sp; r.jump=null; r.group.rotation.x=0;
      }
    } else {
      const a = t*c.sp + c.ph;
      const x = c.cx + c.R*Math.cos(a);
      const z = c.cz + c.R*0.8*Math.sin(a);
      const y = c.y + Math.sin(t*0.6+c.ph)*0.35;
      r.group.position.set(x,y,z);
      r.group.rotation.y = Math.atan2(x - (c.cx + c.R*Math.cos(a-0.05)),
                                     z - (c.cz + c.R*0.8*Math.sin(a-0.05)));
      const vy = (y - r.prevY)/Math.max(dt,0.001);
      r.group.rotation.x = THREE.MathUtils.clamp(-vy*0.25, -0.4, 0.4);
      r.prevY = y;
    }
    animateRayBody(r, t);
  }

  // --- fish schools ---
  for (const s of schools){
    const cx = s.c.x + Math.cos(t*s.sp*0.6+s.ph)*1.2;
    const cz = s.c.y + Math.sin(t*s.sp*0.5+s.ph)*1.0;
    for (let i=0;i<s.n;i++){
      const a = t*s.sp*2.2 + i/s.n*Math.PI*2 + s.ph;
      const rr = s.r + Math.sin(t*0.7+i*2.1)*0.35;
      dummy.position.set(
        cx + Math.cos(a)*rr,
        s.y + Math.sin(t*0.9+i*1.7)*0.25,
        cz + Math.sin(a)*rr*0.8);
      dummy.rotation.set(0, -(a+Math.PI/2) + Math.sin(t*6+i)*0.25, Math.sin(t*3+i)*0.1);
      dummy.scale.setScalar(0.85+((i*37)%10)/18);
      dummy.updateMatrix(); s.mesh.setMatrixAt(i, dummy.matrix);
    }
    s.mesh.instanceMatrix.needsUpdate = true;
  }

  // --- bubbles (follow tide) ---
  for (let i=0;i<BUB_N;i++){
    const b = bubData[i];
    b.y += b.sp*dt;
    if (b.y > level-0.15){ b.y = BOX.y0+0.2; b.x=(Math.random()*2-1)*10.5; b.z=(Math.random()*2-1)*6.5; }
    dummy.position.set(b.x + Math.sin(t*2+i)*0.1, b.y, b.z);
    dummy.scale.setScalar(b.s);
    dummy.updateMatrix(); bubbles.setMatrixAt(i, dummy.matrix);
  }
  bubbles.instanceMatrix.needsUpdate = true;

  // --- ripples ---
  for (const r of ripples){
    if (r.t<0) continue;
    if (r.delay>0){ r.delay-=dt; continue; }
    r.t += dt;
    const s = 0.3 + r.t*2.2;
    r.mesh.scale.setScalar(s);
    r.mesh.position.y = level + 0.03;
    r.mesh.material.opacity = Math.max(0, 0.55 - r.t*0.35);
    if (r.t > 1.8){ r.t=-1; r.mesh.visible=false; }
  }

  // --- droplets ---
  let anyDrop=false;
  for (let i=0;i<DROP_N;i++){
    const d = dropData[i];
    if (d.life<0){ dummy.position.set(0,-100,0); dummy.scale.setScalar(0.0001);
      dummy.updateMatrix(); drops.setMatrixAt(i, dummy.matrix); continue; }
    anyDrop=true; d.life+=dt; d.vy -= 9.8*dt;
    d.x+=d.vx*dt; d.y+=d.vy*dt; d.z+=d.vz*dt;
    if (d.y < level-0.3 && d.vy<0){ d.life=-1; dummy.scale.setScalar(0.0001); }
    else dummy.scale.setScalar(0.8+Math.sin(i)*0.2);
    dummy.position.set(d.x, Math.max(d.y, BOX.y0), d.z);
    dummy.updateMatrix(); drops.setMatrixAt(i, dummy.matrix);
  }
  if (anyDrop) drops.instanceMatrix.needsUpdate = true;
}

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  if (!paused){ worldTime += dt; U.time.value = worldTime; update(dt, worldTime); }

  // camera transition
  if (camTrans){
    const k = 1 - Math.exp(-dt*3.2);
    camera.position.lerp(camTrans.pos, k);
    controls.target.lerp(camTrans.tgt, k);
    if (camera.position.distanceTo(camTrans.pos) < 0.03) camTrans = null;
  }
  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ============================================================
   17. RESIZE
============================================================ */
window.addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
});
</script>
</body>
</html>
```

## Highlights

**Cutaway water** — the lagoon uses a strict render-order pipeline (opaque world → tinted volume → animated surface → ripples → glass) with `depthWrite:false` on all transparent layers, eliminating sorting flicker. The island is opaque so the water surface is cleanly occluded where it meets the shore, and shader-driven foam hides the intersection line.

**Living details** — CPU-animated manta ray wing grids with flapping, instanced fish schools orbiting in three groups, rising bubbles that follow the tide, caustics injected into the seabed's emissive term, and a ray leap with ballistic droplets and staggered expanding ripples plus a procedural splash sound.

**Atmosphere** — time-of-day lerps sun/hemisphere/ambient colors, fog, sky, star opacity, specular intensity, and ramps up emissive windows and lanterns at dusk. Audio is fully synthesized: chord pad with slow filter LFO, delayed pentatonic plucks, filtered-noise breeze tied to the wind slider, and lapping water.

**Performance** — `InstancedMesh` for grass, rocks, kelp, planks, fish, bubbles, and droplets; shared materials; capped pixel ratio and shadow maps on mobile; delta-time animation throughout.