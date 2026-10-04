# Low-Poly Hamster Playground

A single-file Three.js habitat: five chubby faceted hamsters, a wire cage with dyed bedding, a running wheel, a see-through tunnel, a food bowl, and a hideout. They wander, sniff, eat, tunnel, run, and nap — and every one of them is clickable.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Low-Poly Hamster Playground · Habitat 03</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bungee&family=Karla:ital,wght@0,400;0,600;0,800&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#08222a;
    --panel:rgba(9,36,44,.86);
    --panel-2:rgba(9,36,44,.62);
    --line:rgba(178,240,235,.18);
    --text:#eefaf8;
    --dim:#9dbfc2;
    --tang:#ff8a3d;
    --butter:#ffd166;
    --mint:#5fe3b0;
    --sky:#79d0ff;
    --pink:#ff8fa8;
    --shadow:0 18px 40px -18px rgba(0,0,0,.75);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0;background:#08222a;color:var(--text);
    font-family:"Karla",system-ui,sans-serif;
    overflow:hidden;
    -webkit-font-smoothing:antialiased;
  }
  canvas#scene{position:fixed;inset:0;display:block;width:100%;height:100%;touch-action:none}

  /* ambient layers over the render */
  .glow,.vignette,.grain{position:fixed;inset:0;pointer-events:none}
  .glow{
    background:
      radial-gradient(58% 44% at 16% 6%, rgba(255,209,102,.30), transparent 62%),
      radial-gradient(50% 46% at 88% 88%, rgba(95,227,176,.20), transparent 66%);
    mix-blend-mode:screen;transition:opacity .8s ease, transform .8s ease;
  }
  body.night .glow{opacity:.34;transform:translateY(6%)}
  .vignette{background:radial-gradient(120% 92% at 50% 46%, transparent 44%, rgba(2,14,18,.62) 100%)}
  .grain{
    opacity:.05;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/></filter><rect width='140' height='140' filter='url(%23n)'/></svg>");
  }

  #ui{position:fixed;inset:0;pointer-events:none;z-index:6}
  #ui > *{pointer-events:auto}

  /* ---------- brand ---------- */
  .brand{
    position:absolute;top:clamp(14px,2.2vw,26px);left:clamp(14px,2.2vw,28px);
    display:flex;gap:14px;align-items:flex-start;
  }
  .mark{
    width:54px;height:54px;flex:0 0 54px;border-radius:50%;
    background:linear-gradient(160deg,#12414d,#0a2a33);
    border:1px solid var(--line);display:grid;place-items:center;
    box-shadow:var(--shadow);
  }
  .mark svg{width:36px;height:36px;animation:spin 3.4s linear infinite;transform-origin:50% 50%}
  @keyframes spin{to{transform:rotate(360deg)}}
  .kicker{
    margin:2px 0 2px;font-family:"Bungee",cursive;font-size:10px;letter-spacing:.32em;
    color:var(--mint);text-transform:uppercase;
  }
  h1{
    margin:0;font-family:"Bungee",cursive;font-weight:400;line-height:.86;
    font-size:clamp(26px,3.9vw,52px);letter-spacing:-.005em;
    text-shadow:0 4px 0 rgba(0,0,0,.28);
  }
  h1 em{display:block;font-style:normal;color:var(--butter);font-size:.62em;letter-spacing:.02em;margin-top:4px}
  .sub{margin:8px 0 0;font-size:12.5px;color:var(--dim);max-width:31ch;line-height:1.45}
  .sub b{color:var(--text);font-weight:800}

  /* ---------- crew roster ---------- */
  .roster{
    position:absolute;top:clamp(14px,2.2vw,26px);right:clamp(14px,2.2vw,28px);width:250px;
    background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--tang);
    border-radius:14px 14px 16px 4px;padding:12px 12px 10px;box-shadow:var(--shadow);
    backdrop-filter:blur(6px);
  }
  .roster h2{
    margin:0 0 8px;font-family:"Bungee",cursive;font-size:11px;letter-spacing:.2em;
    text-transform:uppercase;color:var(--dim);display:flex;justify-content:space-between;align-items:center;
  }
  .roster h2 span{color:var(--tang);font-size:13px}
  #crewList{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:4px}
  #crewList li{
    display:grid;grid-template-columns:10px 1fr auto;gap:8px;align-items:center;
    padding:6px 8px;border-radius:9px;background:rgba(255,255,255,.035);
    border:1px solid transparent;cursor:pointer;transition:background .18s,transform .18s,border-color .18s;
  }
  #crewList li:hover{background:rgba(255,255,255,.1);transform:translateX(-3px)}
  #crewList li.active{border-color:var(--butter);background:rgba(255,209,102,.14)}
  .dot{width:10px;height:10px;border-radius:3px;box-shadow:0 0 0 1px rgba(0,0,0,.4) inset}
  .nm{font-weight:800;font-size:13px;letter-spacing:.01em}
  .md{display:block;font-size:10.5px;color:var(--dim);font-weight:400;letter-spacing:.03em}
  .mt{font-size:11px;color:var(--mint);font-variant-numeric:tabular-nums;font-weight:800}
  .stats{display:flex;gap:6px;margin-top:10px;border-top:1px dashed rgba(255,255,255,.14);padding-top:9px}
  .stats div{flex:1;text-align:center}
  .stats b{display:block;font-family:"Bungee",cursive;font-size:16px;color:var(--butter);font-variant-numeric:tabular-nums}
  .stats span{font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}

  /* ---------- dock ---------- */
  .dock{
    position:absolute;left:clamp(14px,2.2vw,28px);bottom:clamp(14px,2.2vw,26px);
    display:flex;flex-wrap:wrap;gap:8px;align-items:center;max-width:min(640px,92vw);
    background:var(--panel-2);border:1px solid var(--line);border-radius:16px 16px 4px 16px;
    padding:10px;box-shadow:var(--shadow);backdrop-filter:blur(6px);
  }
  button{
    font-family:"Bungee",cursive;font-size:11px;letter-spacing:.06em;text-transform:uppercase;
    color:var(--ink);background:var(--butter);border:0;border-radius:9px;padding:9px 12px 10px;
    cursor:pointer;box-shadow:0 4px 0 rgba(0,0,0,.4);
    transition:transform .1s ease, box-shadow .1s ease, filter .18s ease;
  }
  button:hover{filter:brightness(1.1)}
  button:active{transform:translateY(4px);box-shadow:0 0 0 rgba(0,0,0,.4)}
  button.alt{background:var(--sky)}
  button.ghost{background:transparent;color:var(--text);border:1px solid var(--line);box-shadow:0 4px 0 rgba(0,0,0,.25)}
  button.on{background:var(--mint)}
  .slider{display:flex;align-items:center;gap:8px;padding:0 6px;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}
  input[type=range]{-webkit-appearance:none;appearance:none;width:92px;height:4px;border-radius:4px;background:rgba(255,255,255,.22);outline:none}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:var(--tang);border:2px solid #0a2a33;cursor:pointer}
  input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:50%;background:var(--tang);border:2px solid #0a2a33;cursor:pointer}

  /* ---------- log ---------- */
  .log{
    position:absolute;right:clamp(14px,2.2vw,28px);bottom:clamp(14px,2.2vw,26px);
    width:min(330px,46vw);display:flex;flex-direction:column;gap:5px;align-items:flex-end;
    pointer-events:none;
  }
  .log p{
    margin:0;font-size:12px;line-height:1.35;padding:6px 11px;border-radius:11px 11px 3px 11px;
    background:rgba(9,36,44,.8);border:1px solid var(--line);color:#d8eeec;
    animation:pop .35s cubic-bezier(.2,1.5,.4,1) both;max-width:100%;
  }
  .log p:nth-child(2){opacity:.55;transform:scale(.97)}
  .log p:nth-child(3){opacity:.28;transform:scale(.94)}
  @keyframes pop{from{opacity:0;transform:translateY(8px) scale(.9)}to{opacity:1;transform:none}}
  .hint{
    position:absolute;left:50%;bottom:10px;transform:translateX(-50%);
    font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:rgba(200,230,228,.45);
    pointer-events:none;white-space:nowrap;
  }

  /* ---------- 3d labels ---------- */
  #overlay{position:fixed;inset:0;pointer-events:none;z-index:5}
  .tag{position:absolute;top:0;left:0;will-change:transform}
  .bubble{
    position:absolute;bottom:22px;left:50%;transform:translateX(-50%) scale(0);
    background:#fff8ec;color:#0b2530;border-radius:12px 12px 12px 3px;padding:1px 7px;
    font-size:15px;line-height:1.5;font-weight:800;box-shadow:0 6px 14px -6px rgba(0,0,0,.8);
    transition:transform .2s cubic-bezier(.3,1.7,.5,1),opacity .2s;opacity:0;white-space:nowrap;
  }
  .bubble.on{transform:translateX(-50%) scale(1);opacity:1}
  .plate{
    position:absolute;top:8px;left:50%;transform:translateX(-50%) translateY(4px);
    font-family:"Bungee",cursive;font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;
    padding:3px 8px;border-radius:20px;background:rgba(8,34,42,.85);border:1px solid var(--line);
    opacity:0;transition:opacity .2s,transform .2s;white-space:nowrap;color:#dff2ef;
  }
  .tag.show .plate{opacity:1;transform:translateX(-50%) translateY(0)}

  .tip{
    position:fixed;z-index:9;pointer-events:none;font-size:11px;letter-spacing:.05em;
    padding:5px 9px;border-radius:8px;background:#0b2530;border:1px solid var(--line);
    color:#e6f7f4;opacity:0;transform:translateY(6px);transition:opacity .14s,transform .14s;
    box-shadow:var(--shadow);white-space:nowrap;
  }
  .tip.on{opacity:1;transform:none}

  /* ---------- loader ---------- */
  #loader{
    position:fixed;inset:0;z-index:20;display:grid;place-items:center;gap:18px;
    background:radial-gradient(70% 60% at 50% 40%,#123c48,#061a21 70%);
    transition:opacity .6s ease,visibility .6s;
  }
  #loader.gone{opacity:0;visibility:hidden}
  #loader .inner{text-align:center}
  #loader svg{width:76px;height:76px;animation:spin 1.1s linear infinite}
  #loader p{font-family:"Bungee",cursive;font-size:12px;letter-spacing:.26em;text-transform:uppercase;color:var(--mint);margin:16px 0 0}
  #loader small{display:block;color:var(--dim);font-size:11px;margin-top:6px;letter-spacing:.1em}

  @media (max-width:860px){
    .roster{display:none}
    .log{width:min(240px,52vw)}
    .sub{display:none}
  }
  @media (max-width:560px){
    .hint{display:none}
    .dock{border-radius:12px;max-width:calc(100vw - 28px)}
    button{padding:8px 9px 9px;font-size:10px}
  }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div class="glow"></div>
<div class="grain"></div>
<div class="vignette"></div>

<div id="overlay"></div>

<div id="ui">
  <header class="brand">
    <div class="mark">
      <svg viewBox="0 0 40 40" fill="none" stroke="#ffd166" stroke-width="2.4" stroke-linecap="round">
        <circle cx="20" cy="20" r="14"/><circle cx="20" cy="20" r="3.4" fill="#ff8a3d" stroke="none"/>
        <path d="M20 6v10M20 24v10M6 20h10M24 20h10M10 10l7 7M30 30l-7-7M30 10l-7 7M10 30l7-7"/>
      </svg>
    </div>
    <div>
      <p class="kicker">Habitat 03 · Three.js</p>
      <h1>Hamster<em>Playground</em></h1>
      <p class="sub">A tiny faceted society of <b id="crewNum">5</b> rodents. Drag to orbit, scroll to zoom, click anybody.</p>
    </div>
  </header>

  <aside class="roster">
    <h2>Inhabitants <span id="crewBadge">05</span></h2>
    <ul id="crewList"></ul>
    <div class="stats">
      <div><b id="statM">0</b><span>metres</span></div>
      <div><b id="statS">0</b><span>snacks</span></div>
      <div><b id="statW">0</b><span>laps</span></div>
    </div>
  </aside>

  <div class="dock">
    <button data-act="wheel">Spin wheel</button>
    <button data-act="food" class="alt">Scatter food</button>
    <button data-act="nap" class="ghost">Lights out</button>
    <button data-act="add" class="ghost">+ hamster</button>
    <div class="slider">Zoomie&nbsp;rate <input id="speed" type="range" min="0.3" max="2.2" step="0.1" value="1"></div>
    <button data-act="reset" class="ghost">Reset view</button>
  </div>

  <div class="log" id="log"></div>
  <div class="hint">drag · orbit &nbsp;/&nbsp; scroll · zoom &nbsp;/&nbsp; click · investigate &nbsp;/&nbsp; space · wheel</div>
</div>

<div class="tip" id="tip"></div>

<div id="loader"><div class="inner">
  <svg viewBox="0 0 40 40" fill="none" stroke="#ffd166" stroke-width="2.6" stroke-linecap="round">
    <circle cx="20" cy="20" r="15"/><circle cx="20" cy="20" r="3.6" fill="#ff8a3d" stroke="none"/>
    <path d="M20 5v11M20 24v11M5 20h11M24 20h11M9 9l8 8M31 31l-8-8M31 9l-8 8M9 31l8-8"/>
  </svg>
  <p>Filling the shavings</p>
  <small id="loadErr"></small>
</div></div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
   0 · helpers
   ============================================================ */
const rand  = (a,b)=>a+Math.random()*(b-a);
const pick  = a=>a[(Math.random()*a.length)|0];
const clamp = (v,a,b)=>v<a?a:v>b?b:v;
const lerp  = (a,b,t)=>a+(b-a)*t;
const damp  = (dt,k)=>1-Math.exp(-k*dt);

const MAT = new Map();
function mat(color, o={}){
  const key = color+'|'+JSON.stringify(o);
  if(MAT.has(key)) return MAT.get(key);
  const m = new THREE.MeshStandardMaterial({ color, flatShading:true, roughness:.82, metalness:0, ...o });
  MAT.set(key,m); return m;
}

/* ============================================================
   1 · renderer / scene / camera
   ============================================================ */
const canvas = document.getElementById('scene');
let renderer;
try{
  renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:false });
}catch(e){
  document.getElementById('loadErr').textContent = 'WebGL unavailable in this browser.';
  throw e;
}
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.06;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, .1, 120);
camera.position.set(9.5,8.2,11.5);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = .06;
controls.enablePan = false;
controls.minDistance = 3.4;
controls.maxDistance = 17;
controls.minPolarAngle = .22;
controls.maxPolarAngle = Math.PI*.487;
controls.target.set(0,.95,0);
controls.autoRotateSpeed = .35;

const HOME = { pos:new THREE.Vector3(6.6,5.1,7.6), tgt:new THREE.Vector3(0,.85,0) };

/* soft image-based lighting so the plastics and wires read nicely */
try{
  const { RoomEnvironment } = await import('three/addons/environments/RoomEnvironment.js');
  const pm = new THREE.PMREMGenerator(renderer);
  const env = pm.fromScene(new RoomEnvironment(), .04);
  scene.environment = env.texture;
}catch(e){ /* fine without it */ }

/* sky gradients (day / night) */
function skyTex(a,b,c){
  const cv=document.createElement('canvas'); cv.width=8; cv.height=256;
  const g=cv.getContext('2d'), gr=g.createLinearGradient(0,0,0,256);
  gr.addColorStop(0,a); gr.addColorStop(.55,b); gr.addColorStop(1,c);
  g.fillStyle=gr; g.fillRect(0,0,8,256);
  const t=new THREE.CanvasTexture(cv); t.colorSpace=THREE.SRGBColorSpace; return t;
}
const SKY_DAY   = skyTex('#5cb9d8','#a9e2ea','#ffd8a4');
const SKY_NIGHT = skyTex('#050f1d','#10293f','#274a63');
scene.background = SKY_DAY;

/* ============================================================
   2 · lights
   ============================================================ */
const hemi = new THREE.HemisphereLight(0xcdefff, 0x6b5236, 1.0);
scene.add(hemi);

const key = new THREE.DirectionalLight(0xfff2d8, 2.5);
key.position.set(6.5,9.5,5.5);
key.castShadow = true;
key.shadow.mapSize.set(2048,2048);
key.shadow.camera.near=.5; key.shadow.camera.far=32;
key.shadow.camera.left=-6.2; key.shadow.camera.right=6.2;
key.shadow.camera.top=5.4; key.shadow.camera.bottom=-5.4;
key.shadow.bias=-.0012; key.shadow.normalBias=.022;
scene.add(key, key.target);

const fill = new THREE.DirectionalLight(0x9fd8ff, .55);
fill.position.set(-7,4.5,-4);
scene.add(fill);

const lamp = new THREE.PointLight(0xffb066, 0, 6, 2);
lamp.position.set(-2.1,1.1,-1.2);
scene.add(lamp);

const LIGHT = { day:{hemi:1.0,key:2.5,fill:.55,lamp:0}, night:{hemi:.24,key:.32,fill:.16,lamp:2.6} };
let nightMix = 0, nightOn = false;

/* ============================================================
   3 · the room + cage
   ============================================================ */
const world = new THREE.Group();
scene.add(world);

/* table */
(function ground(){
  const cv=document.createElement('canvas'); cv.width=cv.height=256;
  const g=cv.getContext('2d');
  const rg=g.createRadialGradient(128,128,10,128,128,140);
  rg.addColorStop(0,'#37666e'); rg.addColorStop(.6,'#1c4049'); rg.addColorStop(1,'#0a2027');
  g.fillStyle=rg; g.fillRect(0,0,256,256);
  const t=new THREE.CanvasTexture(cv); t.colorSpace=THREE.SRGBColorSpace;
  const m=new THREE.Mesh(new THREE.CircleGeometry(17,48), new THREE.MeshStandardMaterial({map:t,roughness:1}));
  m.rotation.x=-Math.PI/2; m.position.y=-.702; m.receiveShadow=true; world.add(m);
})();

const INX = 3.0, INZ = 2.1;            // hamster bounds
const HALF_W = 3.5, HALF_D = 2.6;

/* tray */
(function tray(){
  const body = new THREE.Mesh(new THREE.BoxGeometry(HALF_W*2,.7,HALF_D*2), mat(0x2c6f7e,{roughness:.55}));
  body.position.y=-.35; body.castShadow=body.receiveShadow=true; world.add(body);
  const lip = new THREE.Mesh(new THREE.BoxGeometry(HALF_W*2+.12,.16,HALF_D*2+.12), mat(0x3f95a6,{roughness:.5}));
  lip.position.y=.06; lip.castShadow=lip.receiveShadow=true; world.add(lip);
  const floor = new THREE.Mesh(new THREE.BoxGeometry(HALF_W*2-.5,.1,HALF_D*2-.5), mat(0xd9b47a,{roughness:1}));
  floor.position.y=.03; floor.receiveShadow=true; world.add(floor);
})();

/* bedding chips */
(function bedding(){
  const n=230, geo=new THREE.TetrahedronGeometry(.075), chips=new THREE.InstancedMesh(geo, mat(0xffffff,{roughness:1}), n);
  chips.receiveShadow=true;
  const d=new THREE.Object3D(), c=new THREE.Color();
  for(let i=0;i<n;i++){
    d.position.set(rand(-3.15,3.15), rand(.03,.11), rand(-2.25,2.25));
    d.rotation.set(rand(0,6.3),rand(0,6.3),rand(0,6.3));
    d.scale.set(rand(.7,1.9),rand(.4,.85),rand(.8,1.7));
    d.updateMatrix(); chips.setMatrixAt(i,d.matrix);
    const dyed = Math.random()<.12;
    if(dyed) c.setHSL(pick([.45,.9,.55,.14]), .62, rand(.6,.75));
    else     c.setHSL(rand(.08,.13), rand(.35,.6), rand(.5,.76));
    chips.setColorAt(i,c);
  }
  world.add(chips);
})();

/* bars + rails */
(function cage(){
  const H=2.7, barGeo=new THREE.CylinderGeometry(.032,.032,H,5);
  const spots=[];
  for(let x=-3.42;x<=3.421;x+=.3){ spots.push([x,-2.52],[x,2.52]); }
  for(let z=-2.22;z<=2.221;z+=.3){ spots.push([-3.42,z],[3.42,z]); }
  const bars=new THREE.InstancedMesh(barGeo, mat(0xdfe9ec,{roughness:.32,metalness:.75}), spots.length);
  bars.castShadow=true;
  const d=new THREE.Object3D();
  spots.forEach((s,i)=>{ d.position.set(s[0],H/2,s[1]); d.updateMatrix(); bars.setMatrixAt(i,d.matrix); });
  world.add(bars);

  const railMat=mat(0x2c6f7e,{roughness:.5});
  const rX=new THREE.BoxGeometry(HALF_W*2+.2,.13,.13), rZ=new THREE.BoxGeometry(.13,.13,HALF_D*2+.2);
  [[0,-2.52,rX],[0,2.52,rX]].forEach(([x,z,g])=>{
    const m=new THREE.Mesh(g,railMat); m.position.set(x,H,z); m.castShadow=true; world.add(m);
  });
  [[-3.42,rZ],[3.42,rZ]].forEach(([x,g])=>{
    const m=new THREE.Mesh(g,railMat); m.position.set(x,H,0); m.castShadow=true; world.add(m);
  });
  // lid crossbars
  for(let x=-2.4;x<=2.41;x+=.8){
    const m=new THREE.Mesh(new THREE.CylinderGeometry(.026,.026,5.05,5), mat(0xdfe9ec,{roughness:.32,metalness:.75}));
    m.rotation.x=Math.PI/2; m.position.set(x,H+.001,0); m.castShadow=true; world.add(m);
  }
  // corner posts + feet
  const postMat=mat(0xff8a3d,{roughness:.45});
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([sx,sz])=>{
    const p=new THREE.Mesh(new THREE.BoxGeometry(.16,H+.1,.16),postMat);
    p.position.set(sx*3.44,(H)/2,sz*2.54); p.castShadow=true; world.add(p);
    const f=new THREE.Mesh(new THREE.CylinderGeometry(.16,.2,.14,7),postMat);
    f.position.set(sx*3.44,-.72,sz*2.54); world.add(f);
  });
  // top handle
  const h=new THREE.Mesh(new THREE.TorusGeometry(.34,.055,5,14), postMat);
  h.rotation.x=Math.PI/2; h.position.set(0,H+.18,0); h.castShadow=true; world.add(h);
})();

/* ============================================================
   4 · interactive props
   ============================================================ */
const pickables = [];
function proxy(parent, r, y, info){
  const p=new THREE.Mesh(new THREE.SphereGeometry(r,8,6), new THREE.MeshBasicMaterial({visible:false}));
  p.position.y=y; p.userData=info; parent.add(p); pickables.push(p); return p;
}

/* --- running wheel --- */
const wheel = new THREE.Group();
wheel.position.set(1.55,.06,-1.32);
world.add(wheel);
const spin = new THREE.Group(); wheel.add(spin);
let wheelOmega = 0, wheelTurns = 0;
(function buildWheel(){
  const drum=new THREE.Mesh(new THREE.CylinderGeometry(.95,.95,.52,20,1,true), mat(0x79d0ff,{roughness:.35,side:THREE.DoubleSide,transparent:true,opacity:.92}));
  drum.rotation.x=Math.PI/2; drum.castShadow=true; spin.add(drum);
  const back=new THREE.Mesh(new THREE.CylinderGeometry(.94,.94,.05,20), mat(0x4fb6e8,{roughness:.4}));
  back.rotation.x=Math.PI/2; back.position.z=.27; back.castShadow=true; spin.add(back);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(.96,.07,5,22), mat(0xffd166,{roughness:.4}));
  rim.castShadow=true; spin.add(rim);
  const rungGeo=new THREE.BoxGeometry(.07,.022,.46), rungMat=mat(0xffe9b0,{roughness:.6});
  for(let i=0;i<15;i++){
    const a=i/15*Math.PI*2;
    const r=new THREE.Mesh(rungGeo,rungMat);
    r.position.set(Math.cos(a)*.93,Math.sin(a)*.93,0); r.rotation.z=a-Math.PI/2; spin.add(r);
  }
  for(let i=0;i<6;i++){
    const a=i/6*Math.PI*2;
    const s=new THREE.Mesh(new THREE.BoxGeometry(.9,.045,.045), mat(0x4fb6e8,{roughness:.45}));
    s.position.set(Math.cos(a)*.47,Math.sin(a)*.47,0); s.rotation.z=a; spin.add(s);
  }
  const hub=new THREE.Mesh(new THREE.CylinderGeometry(.1,.1,.72,8), mat(0xff8a3d,{roughness:.4}));
  hub.rotation.x=Math.PI/2; spin.add(hub);
  // stand
  const st=mat(0x2c6f7e,{roughness:.5});
  [-.42,.42].forEach(z=>{
    const p=new THREE.Mesh(new THREE.BoxGeometry(.26,1.0,.09),st); p.position.set(0,.5,z); p.castShadow=true; wheel.add(p);
  });
  const base=new THREE.Mesh(new THREE.BoxGeometry(1.5,.12,1.05),st); base.position.y=.06; base.castShadow=true; wheel.add(base);
  proxy(wheel,1.05,.9,{kind:'wheel',label:'Exercise wheel',hint:'click to spin'});
})();

/* --- tunnel --- */
const tunnel = new THREE.Group();
tunnel.position.set(-2.2,.5,.15);
world.add(tunnel);
const TUN = { x:-2.2, zA:-1.15, zB:1.45 };
(function buildTunnel(){
  const m=mat(0x5fe3b0,{roughness:.25,transparent:true,opacity:.42,side:THREE.DoubleSide,depthWrite:false});
  const tube=new THREE.Mesh(new THREE.CylinderGeometry(.52,.52,2.6,16,1,true),m);
  tube.rotation.x=Math.PI/2; tunnel.add(tube);
  [-1.3,1.3].forEach(z=>{
    const r=new THREE.Mesh(new THREE.TorusGeometry(.52,.06,5,18), mat(0x9ff0cf,{roughness:.35}));
    r.position.z=z; tunnel.add(r);
  });
  proxy(tunnel,1.0,0,{kind:'tunnel',label:'See-through tunnel',hint:'click to call them'});
})();

/* --- food bowl --- */
const bowl = new THREE.Group();
bowl.position.set(2.3,.06,1.35);
world.add(bowl);
(function buildBowl(){
  const outer=new THREE.Mesh(new THREE.CylinderGeometry(.46,.32,.3,12), mat(0xff6b8a,{roughness:.5}));
  outer.position.y=.15; outer.castShadow=outer.receiveShadow=true; bowl.add(outer);
  const inner=new THREE.Mesh(new THREE.CylinderGeometry(.38,.3,.06,12), mat(0x8f2f45,{roughness:.8}));
  inner.position.y=.29; bowl.add(inner);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(.44,.035,5,14), mat(0xffa3b6,{roughness:.4}));
  rim.rotation.x=Math.PI/2; rim.position.y=.29; bowl.add(rim);
  proxy(bowl,.6,.3,{kind:'bowl',label:'Seed bowl',hint:'click to scatter food'});
})();

/* --- hideout --- */
const house = new THREE.Group();
house.position.set(-2.1,.06,-1.72);
world.add(house);
(function buildHouse(){
  const dome=new THREE.Mesh(new THREE.SphereGeometry(.64,9,5,0,Math.PI*2,0,Math.PI*.55), mat(0xe2604a,{roughness:.75}));
  dome.scale.set(1.15,.92,1); dome.position.y=.05; dome.castShadow=dome.receiveShadow=true; house.add(dome);
  const base=new THREE.Mesh(new THREE.CylinderGeometry(.74,.72,.1,10), mat(0xa83f30,{roughness:.8}));
  base.position.y=.05; base.castShadow=true; house.add(base);
  const door=new THREE.Mesh(new THREE.CircleGeometry(.25,10), mat(0x2b1620,{roughness:1}));
  door.position.set(0,.3,.63); house.add(door);
  const knob=new THREE.Mesh(new THREE.IcosahedronGeometry(.1,0), mat(0xffd166,{roughness:.5}));
  knob.position.y=.62; house.add(knob);
  proxy(house,.9,.4,{kind:'house',label:'The hideout',hint:'click to tuck them in'});
})();

/* --- water bottle --- */
(function bottle(){
  const g=new THREE.Group(); g.position.set(3.24,1.5,1.05); world.add(g);
  const b=new THREE.Mesh(new THREE.CylinderGeometry(.17,.17,.66,10), mat(0xdff3ff,{roughness:.15,transparent:true,opacity:.55}));
  g.add(b);
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(.09,.11,.14,8), mat(0xbfcfd6,{roughness:.3,metalness:.7}));
  cap.position.y=-.36; g.add(cap);
  const straw=new THREE.Mesh(new THREE.CylinderGeometry(.018,.018,.16,5), mat(0xbfcfd6,{roughness:.3,metalness:.7}));
  straw.position.y=-.48; g.add(straw);
  const ball=new THREE.Mesh(new THREE.SphereGeometry(.03,6,4), mat(0xe8f4f8,{roughness:.15,metalness:.4}));
  ball.position.y=-.56; g.add(ball);
})();

/* --- rocks --- */
[[.25,1.75,0x8ea3a8,.34],[2.95,-.35,0x9db98f,.28],[-.75,-1.95,0xa3a0b8,.3]].forEach(([x,z,c,s])=>{
  const r=new THREE.Mesh(new THREE.DodecahedronGeometry(s,0), mat(c,{roughness:.95}));
  r.position.set(x,.06+s*.5,z); r.scale.y=.66; r.rotation.y=rand(0,6.3);
  r.castShadow=r.receiveShadow=true; world.add(r);
});

/* --- floating dust motes --- */
const motes = (function(){
  const n=180, pos=new Float32Array(n*3), seed=[];
  for(let i=0;i<n;i++){ pos[i*3]=rand(-5,5); pos[i*3+1]=rand(.2,4); pos[i*3+2]=rand(-4,4); seed.push(rand(0,6.3)); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const p=new THREE.Points(g,new THREE.PointsMaterial({color:0xffe6b8,size:.035,transparent:true,opacity:.45,sizeAttenuation:true,depthWrite:false}));
  world.add(p); return {p,pos,seed,n};
})();

/* --- crumb particles --- */
const puff = (function(){
  const N=90, pos=new Float32Array(N*3), col=new Float32Array(N*3);
  for(let i=0;i<N;i++){ pos[i*3+1]=-99; }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('color',new THREE.BufferAttribute(col,3));
  const pts=new THREE.Points(g,new THREE.PointsMaterial({size:.055,vertexColors:true,transparent:true,opacity:.95,depthWrite:false}));
  world.add(pts);
  const vel=[], life=new Float32Array(N); let cursor=0;
  for(let i=0;i<N;i++) vel.push(new THREE.Vector3());
  return {
    burst(p,c,count,spd){
      const col3=new THREE.Color(c);
      for(let k=0;k<count;k++){
        const i=cursor=(cursor+1)%N;
        pos[i*3]=p.x+rand(-.05,.05); pos[i*3+1]=p.y+rand(0,.1); pos[i*3+2]=p.z+rand(-.05,.05);
        vel[i].set(rand(-1,1),rand(.6,1.9),rand(-1,1)).multiplyScalar(spd);
        col[i*3]=col3.r; col[i*3+1]=col3.g; col[i*3+2]=col3.b;
        life[i]=rand(.45,.9);
      }
    },
    update(dt){
      for(let i=0;i<N;i++){
        if(life[i]<=0) continue;
        life[i]-=dt; if(life[i]<=0){ pos[i*3+1]=-99; continue; }
        vel[i].y-=4.4*dt;
        pos[i*3]+=vel[i].x*dt; pos[i*3+1]+=vel[i].y*dt; pos[i*3+2]+=vel[i].z*dt;
        if(pos[i*3+1]<.08){ pos[i*3+1]=.08; vel[i].y*=-.35; vel[i].x*=.6; vel[i].z*=.6; }
      }
      g.attributes.position.needsUpdate=true; g.attributes.color.needsUpdate=true;
    }
  };
})();

/* ============================================================
   5 · hamsters
   ============================================================ */
const G = {
  body : new THREE.SphereGeometry(.22,8,6),
  head : new THREE.SphereGeometry(.145,8,6),
  snout: new THREE.SphereGeometry(.075,6,4),
  eye  : new THREE.SphereGeometry(.033,7,5),
  glint: new THREE.SphereGeometry(.012,5,4),
  ear  : new THREE.SphereGeometry(.062,6,4),
  cheek: new THREE.SphereGeometry(.06,6,4),
  tail : new THREE.SphereGeometry(.038,6,4),
  leg  : new THREE.CylinderGeometry(.042,.032,.13,5),
  pick : new THREE.SphereGeometry(.4,8,6)
};

const PRESETS = [
  {name:'Nacho',   fur:0xf0b24b, belly:0xfce6c0, ear:0xffab8f, hex:'#f0b24b'},
  {name:'Waffles', fur:0xc9713c, belly:0xf6dcbc, ear:0xffa98c, hex:'#c9713c'},
  {name:'Mochi',   fur:0xf4ede1, belly:0xffffff, ear:0xffbccb, hex:'#f4ede1'},
  {name:'Pickle',  fur:0x99a8ae, belly:0xe0e9ea, ear:0xffbccb, hex:'#99a8ae'},
  {name:'Butter',  fur:0xffd06a, belly:0xfff3d2, ear:0xffab8f, hex:'#ffd06a'},
  {name:'Ziggy',   fur:0x5c4b53, belly:0xa8938f, ear:0xd98d9c, hex:'#5c4b53'},
  {name:'Paprika', fur:0xe0654a, belly:0xfbd9b0, ear:0xffa288, hex:'#e0654a'},
  {name:'Kiwi',    fur:0x93c07a, belly:0xeef7d8, ear:0xf0a9b8, hex:'#93c07a'}
];

const MOOD = {
  wander:['wandering','var(--sky)'], idle:['looking around','var(--sky)'],
  sniff:['sniffing hard','var(--sky)'], eat:['nibbling','var(--pink)'],
  zoom:['ZOOMIES','var(--tang)'], wheel:['on the wheel','var(--butter)'],
  tunnel:['in the tunnel','var(--mint)'], sleep:['curled up','var(--dim)'],
  groom:['washing up','var(--mint)'], spook:['startled!','var(--tang)']
};

const hamsters=[];
const overlay=document.getElementById('overlay');
let presetIdx=0;

function makeHamster(preset, x, z){
  const fur=mat(preset.fur), belly=mat(preset.belly), earM=mat(preset.ear), dark=mat(0x1a1216,{roughness:.35});

  const root=new THREE.Group(); root.position.set(x,.06,z); world.add(root);
  const bob=new THREE.Group(); bob.position.y=0; root.add(bob);

  const body=new THREE.Mesh(G.body,fur); body.scale.set(1.28,.98,1.06); body.position.y=.2; bob.add(body);
  const bellyM=new THREE.Mesh(G.body,belly); bellyM.scale.set(1.12,.72,.9); bellyM.position.set(.03,.14,0); bob.add(bellyM);
  const tail=new THREE.Mesh(G.tail,fur); tail.position.set(-.29,.19,0); bob.add(tail);

  const head=new THREE.Group(); head.position.set(.25,.27,0); bob.add(head);
  const headM=new THREE.Mesh(G.head,fur); headM.scale.set(1.06,1,.98); head.add(headM);
  const snout=new THREE.Mesh(G.snout,belly); snout.scale.set(1,.8,.85); snout.position.set(.11,-.02,0); head.add(snout);
  const nose=new THREE.Mesh(new THREE.SphereGeometry(.026,6,4), mat(0xff8fa8,{roughness:.5})); nose.position.set(.17,-.005,0); head.add(nose);

  const eyes=[],glints=[],ears=[],cheeks=[];
  [-1,1].forEach(s=>{
    const e=new THREE.Mesh(G.eye,dark); e.position.set(.095,.05,s*.082); head.add(e); eyes.push(e);
    const g=new THREE.Mesh(G.glint,mat(0xffffff,{roughness:.1})); g.position.set(.118,.075,s*.062); head.add(g); glints.push(g);
    const ear=new THREE.Mesh(G.ear,earM); ear.scale.set(1,1,.42); ear.position.set(-.02,.12,s*.1); head.add(ear); ears.push(ear);
    const ch=new THREE.Mesh(G.cheek,fur); ch.position.set(.055,-.035,s*.1); head.add(ch); cheeks.push(ch);
  });

  const legs=[];
  [[.14,-.1],[.14,.1],[-.14,-.1],[-.14,.1]].forEach(([lx,lz],i)=>{
    const hip=new THREE.Group(); hip.position.set(lx,.14,lz); bob.add(hip);
    const m=new THREE.Mesh(G.leg,fur); m.position.y=-.055; hip.add(m);
    legs.push({hip,phase:(i===0||i===3)?0:Math.PI});
  });

  const proxy=new THREE.Mesh(G.pick,new THREE.MeshBasicMaterial({visible:false}));
  proxy.position.set(0,.25,0); root.add(proxy);

  const tag=document.createElement('div'); tag.className='tag';
  tag.innerHTML='<span class="bubble"></span><span class="plate"></span>';
  overlay.appendChild(tag);

  const h={
    name:preset.name, hex:preset.hex, preset,
    root,bob,body,bellyM,head,eyes,glints,ears,cheeks,legs,tail,proxy,tag,
    bubbleEl:tag.querySelector('.bubble'), plateEl:tag.querySelector('.plate'),
    yaw:rand(0,6.3), target:new THREE.Vector3(x,0,z),
    state:'idle', timer:rand(.5,2), anim:rand(0,10),
    speed:rand(.5,.72), energy:rand(.6,1), hunger:rand(.1,.6),
    metres:0, emoteT:0, curl:0, wheelTime:0, tun:null, spookT:0,
    pose:{sit:0,curl:0,eye:1,cheek:0,pitch:0,headYaw:0,legFreq:8,legAmp:.5,lean:0},
    tp:{sit:0,curl:0,eye:1,cheek:0,pitch:0,headYaw:0,legFreq:8,legAmp:.5,lean:0}
  };
  proxy.userData={kind:'hamster',ref:h,label:preset.name,hint:'click to follow'};
  pickables.push(proxy);
  hamsters.push(h);
  return h;
}

/* pellets */
const pellets=[];
const PELLET_GEO=new THREE.IcosahedronGeometry(.052,0);
function dropPellet(x,z,from){
  if(pellets.length>26) return;
  const m=new THREE.Mesh(PELLET_GEO, mat(pick([0xd8a55c,0x9dc06a,0xb5623f,0xe8d38a]),{roughness:.9}));
  m.position.set(x,from||1.2,z); m.castShadow=true; world.add(m);
  pellets.push({mesh:m,vy:0,rest:false});
}
function scatterFood(n=8,at){
  const c=at||{x:2.3,z:1.35};
  for(let i=0;i<n;i++) dropPellet(c.x+rand(-.9,.9), c.z+rand(-.9,.9), rand(.9,1.7));
  puff.burst(new THREE.Vector3(c.x,.4,c.z),0xffd166,14,1.1);
  hamsters.forEach(h=>{ h.hunger=1; if(h.state==='sleep'){ wake(h); if(Math.random()<.6) say(h,'!'); } else if(Math.random()<.5) say(h,'?'); });
  log(pick(['Seeds hit the shavings. Chaos is imminent.','Snack bell rings — every nose in the cage twitches.','Someone shook the bowl. Fortunes rise.']));
  bump('statS',0);
}

/* ============================================================
   6 · behaviour
   ============================================================ */
const OBSTACLES=[
  {x:1.55,z:-1.32,r:1.02,key:'wheel'},
  {x:-2.1,z:-1.72,r:.78,key:'house'},
  {x:2.3,z:1.35,r:.42,key:'bowl'},
  {x:-2.2,z:.15,r:.62,key:'tunnel'},
  {x:.25,z:1.75,r:.36},{x:2.95,z:-.35,r:.3},{x:-.75,z:-1.95,r:.32}
];

function say(h,text,dur=1.7){
  h.bubbleEl.textContent=text; h.bubbleEl.classList.add('on'); h.emoteT=dur;
}
function setState(h,s,t){ h.state=s; h.timer=t||rand(1.2,3.2); }
function wake(h){ if(h.state==='sleep'){ setState(h,'idle',rand(.4,1)); h.tp.curl=0; } }

function choose(h){
  if(h.spookT>0){ setState(h,'zoom',rand(1,2)); newTarget(h); return; }
  const nearPellet = pellets.length>0;
  if(nightOn || h.energy<.18){ setState(h,'sleep',rand(7,14)); goSleepSpot(h); return; }
  const r=Math.random();
  if(nearPellet && h.hunger>.45){ goEat(h); return; }
  if(r<.18 && wheelOccupant()!==h){ goWheel(h); return; }
  if(r<.32){ goTunnel(h); return; }
  if(r<.46){ setState(h,'groom',rand(1.4,2.6)); return; }
  if(r<.72){ setState(h,'wander',rand(2,4.5)); newTarget(h); return; }
  setState(h,'idle',rand(1,2.6));
}
function newTarget(h){
  h.target.set(rand(-INX,INX),0,rand(-INZ,INZ));
}
function goSleepSpot(h){
  const spots=[[-2.05,-.95],[-2.75,-1.15],[-1.4,-1.05],[-2.9,-.3]];
  const s=pick(spots); h.target.set(s[0],0,s[1]);
}
function goEat(h){
  if(!pellets.length){ choose(h); return; }
  let best=null,bd=1e9;
  const p=h.root.position;
  pellets.forEach(pl=>{ const d=(pl.mesh.position.x-p.x)**2+(pl.mesh.position.z-p.z)**2; if(d<bd){bd=d;best=pl;} });
  h.food=best; h.target.set(best.mesh.position.x,0,best.mesh.position.z);
  setState(h,'wander',6);
}
function goWheel(h){
  if(wheelOccupant()){ newTarget(h); setState(h,'wander',2); return; }
  h.wheelTime=rand(4,9); h.target.set(1.55,0,-1.32); setState(h,'wander',5); h.pending='wheel';
}
function goTunnel(h){
  const p=h.root.position;
  const enterA = Math.abs(p.z-TUN.zA) < Math.abs(p.z-TUN.zB);
  h.tun={from:enterA?TUN.zA:TUN.zB, to:enterA?TUN.zB:TUN.zA, t:0};
  h.target.set(TUN.x,0,h.tun.from); setState(h,'wander',6); h.pending='tunnel';
}
function wheelOccupant(){ return hamsters.find(h=>h.state==='wheel')||null; }

function spookAll(power){
  hamsters.forEach(h=>{
    if(h.state!=='wheel'&&h.state!=='sleep'){ h.spookT=rand(1,2.2); say(h,'!',1.2); if(h.state!=='zoom'){ setState(h,'zoom',rand(.9,1.8)); newTarget(h);} }
    else if(h.state==='sleep'){ wake(h); say(h,'?',1.2); }
  });
}

function updateHamster(h,dt){
  const p=h.root.position, T=h.tp;
  h.anim+=dt; h.timer-=dt;
  h.spookT=Math.max(0,h.spookT-dt);
  h.energy=clamp(h.energy + (h.state==='sleep'?dt*.035:-dt*.006),0,1);
  h.hunger=clamp(h.hunger - dt*.01,0,1);

  // pose defaults
  T.sit=0;T.curl=0;T.eye=1;T.cheek=0;T.pitch=0;T.headYaw=Math.sin(h.anim*.7)*.3;T.legFreq=7;T.legAmp=.42;T.lean=0;

  switch(h.state){
    case 'idle':{
      T.legFreq=2.2; T.legAmp=.05; T.sit=Math.random()<.002?1:0;
      T.headYaw=Math.sin(h.anim*1.9)*.7; T.pitch=Math.sin(h.anim*1.3)*.12;
      if(h.timer<=0) choose(h);
      break;
    }
    case 'sniff':{
      T.headPitch=.5; T.headYaw=Math.sin(h.anim*5)*.5; T.legAmp=.1; T.legFreq=4;
      if(h.timer<=0) choose(h);
      break;
    }
    case 'wander':{
      const dx=h.target.x-p.x, dz=h.target.z-p.z, dist=Math.hypot(dx,dz);
      const want=Math.atan2(-dz,dx);
      let diff=((want-h.yaw+Math.PI*3)%(Math.PI*2))-Math.PI;
      h.yaw += diff*Math.min(1,dt*5.5);
      const dir=new THREE.Vector3(Math.cos(h.yaw),0,-Math.sin(h.yaw));
      const sp=(h.state==='zoom'?h.speed*2.4:h.speed)*(h.spookT>0?2.1:1);
      if(dist>.12){
        p.addScaledVector(dir, sp*dt);
        h.metres += sp*dt;
        T.legFreq=h.spookT>0?26:13; T.legAmp=h.spookT>0?.9:.55; T.lean=.12;
      }else{
        if(h.pending==='wheel'){ h.pending=null; setState(h,'wheel',h.wheelTime); p.set(1.55,.06,-1.32); h.yaw=0; say(h,'♪',1.2); }
        else if(h.pending==='tunnel'){ h.pending=null; setState(h,'tunnel',3); }
        else if(h.food && pellets.includes(h.food)){ setState(h,'eat',rand(1.6,2.8)); say(h,'♪',1.4); }
        else { setState(h, Math.random()<.35?'sniff':'idle', Math.random()<.35?rand(.8,1.6):rand(.5,1.4)); }
      }
      break;
    }
    case 'zoom':{
      const dx=h.target.x-p.x, dz=h.target.z-p.z;
      if(Math.hypot(dx,dz)<.2) newTarget(h);
      const want=Math.atan2(-dz,dx);
      let diff=((want-h.yaw+Math.PI*3)%(Math.PI*2))-Math.PI;
      h.yaw+=diff*Math.min(1,dt*7);
      const sp=h.speed*2.5;
      p.addScaledVector(new THREE.Vector3(Math.cos(h.yaw),0,-Math.sin(h.yaw)), sp*dt);
      h.metres+=sp*dt;
      T.legFreq=28;T.legAmp=.95;T.lean=.2;
      if(h.timer<=0){ setState(h,'idle',rand(.6,1.4)); }
      break;
    }
    case 'eat':{
      T.headPitch=.65+Math.sin(h.anim*9)*.18; T.cheek=1; T.legAmp=.08; T.legFreq=3; T.sit=.25;
      if(h.timer<=0){
        if(h.food && pellets.includes(h.food)){
          const pos=h.food.mesh.position.clone();
          puff.burst(pos,0xffd166,7,.7);
          world.remove(h.food.mesh); pellets.splice(pellets.indexOf(h.food),1);
          state.snacks++; say(h,'♥',1.3);
          if(Math.random()<.5) log(`${h.name} found a seed and took it personally.`);
        }
        h.food=null; choose(h);
      }
      break;
    }
    case 'groom':{
      T.sit=.8; T.headYaw=Math.sin(h.anim*11)*.5; T.pitch=-.25; T.legAmp=.28; T.legFreq=12;
      T.cheek=.25+.2*Math.sin(h.anim*11);
      if(h.timer<=0) choose(h);
      break;
    }
    case 'wheel':{
      p.set(1.55,.06,-1.32); h.yaw=0;
      T.legFreq=30; T.legAmp=.85; T.lean=.08; T.headYaw=0; T.pitch=-.08;
      wheelOmega=lerp(wheelOmega, 9.5, Math.min(1,dt*1.6));
      h.timer-=dt*0; // timer handled below
      h.wheelTime-=dt;
      if(h.wheelTime<=0){
        setState(h,'idle',rand(.8,1.6));
        say(h,'@_@',1.8);
        h.yaw=rand(0,6.3); newTarget(h);
        if(Math.random()<.6) log(`${h.name} steps off the wheel. The room is spinning. Lovely.`);
      }
      break;
    }
    case 'tunnel':{
      const t=h.tun; t.t=clamp(t.t+dt*.42,0,1);
      p.z=lerp(t.from,t.to,t.t); p.x=TUN.x;
      h.yaw=Math.atan2(-(t.to>t.from?1:-1),0);
      p.y=.06+Math.sin(t.t*Math.PI)*0;
      T.legFreq=15;T.legAmp=.5;T.lean=.15;T.headYaw=0;
      if(t.t>=1){ p.x=TUN.x; setState(h,'idle',rand(.4,1)); say(h,'!',1);
        puff.burst(new THREE.Vector3(TUN.x,.2,t.to),0x9ff0cf,8,.8);
        if(Math.random()<.4) log(`${h.name} exits the tunnel. Philosophically changed.`);
      }
      break;
    }
    case 'sleep':{
      T.curl=1; T.eye=0; T.legAmp=0; T.legFreq=1.2; T.headYaw=0;
      const dx=h.target.x-p.x, dz=h.target.z-p.z;
      if(Math.hypot(dx,dz)>.15){
        const want=Math.atan2(-dz,dx);
        let diff=((want-h.yaw+Math.PI*3)%(Math.PI*2))-Math.PI;
        h.yaw+=diff*Math.min(1,dt*4);
        p.addScaledVector(new THREE.Vector3(Math.cos(h.yaw),0,-Math.sin(h.yaw)), h.speed*.7*dt);
        h.metres+=h.speed*.7*dt;
        T.curl=0; T.eye=1; T.legAmp=.3; T.legFreq=7;
      }
      if(!nightOn && h.energy>.92) choose(h);
      if(h.timer<=0 && !nightOn) choose(h);
      break;
    }
  }

  /* bounds + obstacles + friends */
  p.x=clamp(p.x,-INX,INX); p.z=clamp(p.z,-INZ,INZ);
  if((p.x===-INX||p.x===INX||p.z===-INZ||p.z===INZ) && (h.state==='wander'||h.state==='zoom')) newTarget(h);
  if(h.state!=='wheel'&&h.state!=='tunnel'){
    OBSTACLES.forEach(o=>{
      if(o.key===h.state) return;
      if(o.key==='bowl' && h.state==='eat') return;
      const dx=p.x-o.x, dz=p.z-o.z, d=Math.hypot(dx,dz);
      if(d<o.r && d>1e-4){ p.x=o.x+dx/d*o.r; p.z=o.z+dz/d*o.r; }
    });
  }
  hamsters.forEach(o=>{
    if(o===h||o.state==='wheel'||h.state==='wheel') return;
    const dx=p.x-o.root.position.x, dz=p.z-o.root.position.z, d=Math.hypot(dx,dz);
    if(d<.34&&d>1e-4){ const push=(.34-d)*.5; p.x+=dx/d*push; p.z+=dz/d*push; }
  });

  /* pose smoothing */
  const P=h.pose, k=damp(dt,9);
  for(const key in T) P[key]=lerp(P[key],T[key],k);
  const breathe=Math.sin(h.anim*(P.curl>.4?1.6:4.5))*.02;

  h.root.rotation.y=h.yaw;
  h.bob.position.y=Math.abs(Math.sin(h.anim*P.legFreq))*.022*(P.legAmp>.2?1:0)+P.curl*-.02;
  h.bob.rotation.z=P.sit*.62-P.lean+P.curl*.05;
  h.body.scale.set(1.28*(1+breathe+P.curl*.12),.98*(1-breathe*.6-P.curl*.16),1.06*(1+P.curl*.14));
  h.bellyM.scale.set(1.12,.72*(1-P.curl*.2),.9);
  h.head.position.set(.25-P.curl*.05,.27-P.curl*.09-P.sit*.02,0);
  h.head.rotation.set(P.pitch,P.headYaw,0);
  h.eyes.forEach(e=>{ e.scale.y=lerp(.14,1,P.eye); });
  h.glints.forEach(g=>{ g.visible=P.eye>.4; });
  h.cheeks.forEach((c,i)=>{ const s=1+P.cheek*.85; c.scale.setScalar(s); c.rotation.x=Math.sin(h.anim*11+i*3)*.2*P.sit; });
  h.ears.forEach((e,i)=>{ e.rotation.z=Math.sin(h.anim*(2+i))*0.16*(1-P.curl); });
  h.tail.rotation.y=Math.sin(h.anim*3)*.3;
  h.tail.scale.setScalar(1-P.curl*.5);
  h.legs.forEach(l=>{
    l.hip.rotation.x=Math.sin(h.anim*P.legFreq+l.phase)*P.legAmp;
    l.hip.scale.y=lerp(1,.45,P.curl);
  });
}

/* ============================================================
   7 · UI wiring
   ============================================================ */
const state={ speed:1, focus:null, lastAct:performance.now(), snacks:0, wheelTurns:0 };
const crewList=document.getElementById('crewList');
const logBox=document.getElementById('log');
const tip=document.getElementById('tip');

function log(msg){
  const p=document.createElement('p'); p.textContent=msg;
  logBox.prepend(p);
  while(logBox.children.length>3) logBox.lastChild.remove();
}
function bump(){ }
function buildRoster(){
  crewList.innerHTML='';
  hamsters.forEach((h,i)=>{
    const li=document.createElement('li');
    li.innerHTML=`<span class="dot" style="background:${h.hex}"></span>
      <span class="nm">${h.name}<span class="md">waking up…</span></span>
      <span class="mt">0.0m</span>`;
    li.addEventListener('click',()=>focusHamster(h));
    crewList.appendChild(li);
    h.row=li; h.rowMood=li.querySelector('.md'); h.rowM=li.querySelector('.mt');
  });
  document.getElementById('crewNum').textContent=hamsters.length;
  document.getElementById('crewBadge').textContent=String(hamsters.length).padStart(2,'0');
}

function focusHamster(h){
  state.focus=h;
  hamsters.forEach(o=>o.row&&o.row.classList.toggle('active',o===h));
  const off=camera.position.clone().sub(controls.target).normalize().multiplyScalar(3.6);
  tweenCam(h.root.position.clone().add(off).setY(Math.max(1.4,h.root.position.y+1.5)), h.root.position.clone().setY(.3), .9);
  say(h,'?',1.2);
  log(`Camera locked on ${h.name}. ${h.name} pretends not to notice.`);
}
function unfocus(){ state.focus=null; hamsters.forEach(o=>o.row&&o.row.classList.remove('active')); }

let camTween=null;
function tweenCam(toPos,toTgt,dur=1.1){
  camTween={t:0,dur,fp:camera.position.clone(),ft:controls.target.clone(),tp:toPos,tt:toTgt};
}

function setNight(on){
  nightOn=on; document.body.classList.toggle('night',on);
  scene.background = on?SKY_NIGHT:SKY_DAY;
  const btn=document.querySelector('[data-act="nap"]');
  btn.classList.toggle('on',on);
  btn.textContent = on?'Lights on':'Lights out';
  log(on?'Lights out. The cage becomes a small blue moon.':'Sunrise. Somebody stretches dramatically.');
  if(on) hamsters.forEach(h=>{ if(Math.random()<.85) setState(h,'sleep',rand(9,16)), goSleepSpot(h); });
  else hamsters.forEach(h=>wake(h));
}

document.querySelector('.dock').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  state.lastAct=performance.now();
  const a=b.dataset.act;
  if(a==='wheel'){ wheelOmega+=13; spookAll(); log('Somebody flicked the wheel. It whooshes heroically.'); }
  if(a==='food') scatterFood(9);
  if(a==='nap')  setNight(!nightOn);
  if(a==='add'){
    if(hamsters.length>=8){ log('The council declines. Eight is a full house.'); return; }
    const p=PRESETS[hamsters.length%PRESETS.length];
    const h=makeHamster(p,rand(-1,1),rand(-.5,.5));
    buildRoster(); h.plateEl.textContent=p.name;
    puff.burst(new THREE.Vector3(h.root.position.x,.3,h.root.position.z),0xffd166,16,1.4);
    say(h,'!',2); log(`${p.name} arrives, immediately suspicious of the tunnel.`);
  }
  if(a==='reset'){ unfocus(); tweenCam(HOME.pos.clone(),HOME.tgt.clone(),.9); }
});
document.getElementById('speed').addEventListener('input',e=>{ state.speed=parseFloat(e.target.value); });

addEventListener('keydown',e=>{
  state.lastAct=performance.now();
  if(e.code==='Space'){ e.preventDefault(); wheelOmega+=13; spookAll(); log('Keyboard wheel. Very modern.'); }
  if(e.key==='f'||e.key==='F') scatterFood(9);
  if(e.key==='n'||e.key==='N') setNight(!nightOn);
  if(e.key==='r'||e.key==='R'){ unfocus(); tweenCam(HOME.pos.clone(),HOME.tgt.clone(),.9); }
  if(e.key==='Escape') unfocus();
});

/* pointer picking */
const ray=new THREE.Raycaster(), ndc=new THREE.Vector2();
let hovered=null, down=null;
function pointerAt(ev){
  ndc.x=(ev.clientX/innerWidth)*2-1; ndc.y=-(ev.clientY/innerHeight)*2+1;
  ray.setFromCamera(ndc,camera);
  const hit=ray.intersectObjects(pickables,false)[0];
  return hit?hit.object.userData:null;
}
renderer.domElement.addEventListener('pointermove',ev=>{
  const u=pointerAt(ev);
  hovered=u;
  renderer.domElement.style.cursor=u?'pointer':'grab';
  if(u){
    tip.classList.add('on');
    tip.innerHTML=`<b style="font-family:Bungee">${u.label}</b> <span style="opacity:.6">· ${u.hint}</span>`;
    tip.style.left=Math.min(innerWidth-180,ev.clientX+14)+'px';
    tip.style.top=(ev.clientY-34)+'px';
  } else tip.classList.remove('on');
});
renderer.domElement.addEventListener('pointerdown',ev=>{ down={x:ev.clientX,y:ev.clientY,t:performance.now()}; state.lastAct=performance.now(); controls.autoRotate=false; });
renderer.domElement.addEventListener('pointerup',ev=>{
  if(!down) return;
  const moved=Math.hypot(ev.clientX-down.x,ev.clientY-down.y);
  down=null; state.lastAct=performance.now();
  if(moved>6) return;
  const u=pointerAt(ev); if(!u) { unfocus(); return; }
  if(u.kind==='hamster') focusHamster(u.ref);
  else if(u.kind==='wheel'){ wheelOmega+=13; spookAll(); log('Wheel: manual override engaged.'); }
  else if(u.kind==='bowl') scatterFood(9);
  else if(u.kind==='tunnel'){ hamsters.forEach(h=>{ if(h.state!=='wheel'&&Math.random()<.5) goTunnel(h); }); log('A whistle through the tunnel. They investigate, as one does.'); }
  else if(u.kind==='house'){ setNight(true); }
});

/* ============================================================
   8 · loop
   ============================================================ */
const clock=new THREE.Clock();
const proj=new THREE.Vector3();
let uiTick=0;

function frame(){
  const raw=Math.min(.05,clock.getDelta());
  const dt=raw*state.speed;

  /* camera tween */
  if(camTween){
    camTween.t=Math.min(1,camTween.t+raw/camTween.dur);
    const e=1-Math.pow(1-camTween.t,3);
    camera.position.lerpVectors(camTween.fp,camTween.tp,e);
    controls.target.lerpVectors(camTween.ft,camTween.tt,e);
    if(camTween.t>=1) camTween=null;
  }
  if(state.focus){
    const want=state.focus.root.position.clone().setY(.3);
    controls.target.lerp(want, damp(raw,4));
    state.focus.plateEl.textContent=state.focus.name;
  }
  controls.autoRotate = !state.focus && !camTween && (performance.now()-state.lastAct>7000);
  controls.update();

  /* lights blend */
  nightMix=lerp(nightMix, nightOn?1:0, damp(raw,2.2));
  const D=LIGHT.day, N=LIGHT.night;
  hemi.intensity=lerp(D.hemi,N.hemi,nightMix);
  key.intensity=lerp(D.key,N.key,nightMix);
  key.color.setHex(nightMix>.5?0x9fb8ff:0xfff2d8);
  fill.intensity=lerp(D.fill,N.fill,nightMix);
  lamp.intensity=lerp(D.lamp,N.lamp,nightMix);

  /* hamsters */
  hamsters.forEach(h=>updateHamster(h,dt));

  /* wheel physics */
  wheelOmega*=Math.pow(.35,raw);
  if(Math.abs(wheelOmega)<.002) wheelOmega=0;
  spin.rotation.z+=wheelOmega*raw;
  state.wheelTurns+=Math.abs(wheelOmega)*raw/(Math.PI*2);
  if(wheelOmega>6 && Math.random()<.02) log('The wheel files a complaint about overtime.');

  /* pellets */
  for(const p of pellets){
    if(p.rest) continue;
    p.vy-=6.5*raw; p.mesh.position.y+=p.vy*raw;
    p.mesh.rotation.x+=raw*3; p.mesh.rotation.z+=raw*2;
    if(p.mesh.position.y<=.1){ p.mesh.position.y=.1; p.rest=true; }
  }
  puff.update(raw);

  /* motes */
  const mp=motes.pos;
  for(let i=0;i<motes.n;i++){
    mp[i*3+1]+=raw*.09; mp[i*3]+=Math.sin(clock.elapsedTime*.4+motes.seed[i])*.0016;
    if(mp[i*3+1]>4.4) mp[i*3+1]=.15;
  }
  motes.p.geometry.attributes.position.needsUpdate=true;

  /* labels */
  hamsters.forEach(h=>{
    const show = h.emoteT>0 || hovered?.ref===h || state.focus===h;
    h.emoteT-=raw;
    if(h.emoteT<=0) h.bubbleEl.classList.remove('on');
    else h.bubbleEl.classList.add('on');
    if(h.state==='sleep' && h.emoteT<=0 && Math.random()<.012) say(h,'z z',2.4);
    if(h.state==='zoom' && h.emoteT<=0 && Math.random()<.02) say(h,'💨',1);
    h.tag.classList.toggle('show', !!(hovered?.ref===h || state.focus===h));
    if(!show && !h.tag.classList.contains('show')){ h.tag.style.transform='translate3d(-9999px,-9999px,0)'; return; }
    proj.set(h.root.position.x,.62,h.root.position.z).project(camera);
    if(proj.z>1){ h.tag.style.transform='translate3d(-9999px,-9999px,0)'; return; }
    h.tag.style.transform=`translate3d(${(proj.x*.5+.5)*innerWidth}px,${(-proj.y*.5+.5)*innerHeight}px,0)`;
  });

  /* ui text (throttled) */
  uiTick+=raw;
  if(uiTick>.18){
    uiTick=0;
    let total=0;
    hamsters.forEach(h=>{
      total+=h.metres;
      const m=MOOD[h.state]||MOOD.idle;
      if(h.rowMood){ h.rowMood.textContent=m[0]; h.rowMood.style.color=m[1]; h.rowM.textContent=h.metres.toFixed(1)+'m'; }
    });
    document.getElementById('statM').textContent=total.toFixed(0);
    document.getElementById('statS').textContent=state.snacks;
    document.getElementById('statW').textContent=state.wheelTurns.toFixed(0);
  }

  renderer.render(scene,camera);
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* ============================================================
   9 · go
   ============================================================ */
(function init(){
  const starts=[[-.4,.6],[.9,.9],[-1.1,-.4],[1.6,.6],[-1.6,.9]];
  starts.forEach((s,i)=>{ const h=makeHamster(PRESETS[i],s[0],s[1]); h.plateEl.textContent=h.name; });
  buildRoster();
  for(let i=0;i<5;i++) dropPellet(2.3+rand(-.3,.3),1.35+rand(-.3,.3),rand(.4,.9));
  tweenCam(HOME.pos.clone(),HOME.tgt.clone(),1.7);
  renderer.setAnimationLoop(frame);
  setTimeout(()=>{
    document.getElementById('loader').classList.add('gone');
    log('Habitat 03 is open. Five hamsters, one wheel, zero plans.');
    setTimeout(()=>log('Tip: click any hamster to follow it around.'),1400);
  },420);
  renderer.domElement.style.cursor='grab';
})();
</script>
</body>
</html>
```

**What's in the box**

- **Cage** — instanced wire bars, orange corner posts with feet, lid crossbars, a raised tray rim, and 230 instanced bedding chips (a few dyed pastel for fun).
- **Five hamsters** (up to eight) built from faceted spheres/cones with per-hamster palettes, glinting eyes, wiggling ears, a twitching tail, and puffed cheeks when they stash seeds.
- **Autonomy** — a weighted state machine: `wander · zoom · sniff · groom · eat · wheel · tunnel · sleep`, driven by hunger and energy meters, with soft collision so they never clip through props or each other.
- **Interactive objects** — the wheel has real spin + friction (a runner accelerates it, clicks add an impulse); the tunnel is translucent so you can watch a hamster slide through; the bowl scatters physics-driven pellets; the hideout triggers lights-out.
- **Feedback everywhere** — projected speech bubbles (`♪ ♥ ! @_@ z z`), nameplates, hover tooltips, a live crew roster with mood + metres, and a running stat strip for metres / snacks / wheel laps.
- **Atmosphere** — day↔night light blend with a warm lamp glow in the hideout corner, drifting dust motes, crumb particle bursts, ACES tone mapping, PMREM environment lighting, and idle auto-orbit that hands control back the moment you touch anything.