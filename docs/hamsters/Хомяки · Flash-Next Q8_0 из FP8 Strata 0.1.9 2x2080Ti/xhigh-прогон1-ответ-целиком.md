# Low-Poly Hamster Playground

A single-file Three.js toy habitat. Save as `index.html`, open in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Low-Poly Hamster Playground · Exhibit 07</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lilita+One&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#241a26;
    --ink-soft:rgba(36,26,38,.62);
    --paper:#fff7ea;
    --paper-2:#ffeeda;
    --mint:#2ecaa6;
    --mint-d:#0e7568;
    --coral:#ff6a4d;
    --sun:#ffc247;
    --plum:#6b3357;
    --sky:#7fdcff;
    --shadow:6px 6px 0 rgba(36,26,38,.9);
    --shadow-sm:3px 3px 0 rgba(36,26,38,.85);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0; overflow:hidden; background:#ffd7a8;
    font-family:"Space Grotesk", ui-sans-serif, system-ui, sans-serif;
    color:var(--ink);
    -webkit-font-smoothing:antialiased;
  }
  #scene{position:fixed; inset:0; width:100%; height:100%; display:block; touch-action:none; z-index:0}

  /* ---------- ambient layers over the render ---------- */
  .fx{position:fixed; inset:0; pointer-events:none; z-index:2}
  .vig{background:
      radial-gradient(120% 100% at 50% 42%, rgba(255,255,255,0) 48%, rgba(96,44,20,.30) 100%),
      linear-gradient(to bottom, rgba(255,240,210,.22), rgba(255,255,255,0) 30%);}
  .grain{
    opacity:.16; mix-blend-mode:multiply;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='.55'/%3E%3C/svg%3E");
  }
  .nightTint{
    background:radial-gradient(130% 95% at 55% 18%, rgba(60,80,170,.18), rgba(10,14,44,.74));
    opacity:0; transition:opacity 1.1s ease; mix-blend-mode:multiply;
  }
  body.night .nightTint{opacity:1}

  /* ---------- shared HUD card ---------- */
  .hud{position:fixed; z-index:10; background:var(--paper); border:3px solid var(--ink);
       box-shadow:var(--shadow); border-radius:16px}
  .panel-h{display:flex; align-items:center; justify-content:space-between; gap:10px;
    font-family:"Lilita One",cursive; font-size:12px; letter-spacing:.16em; text-transform:uppercase;
    padding:11px 14px 9px; border-bottom:2px dashed rgba(36,26,38,.25)}
  .panel-h b{font-family:"Space Grotesk"; font-size:11px; background:var(--ink); color:var(--paper);
    padding:2px 8px; border-radius:999px; letter-spacing:.06em}

  /* entrance */
  .hud,.hint{opacity:0; transform:translateY(16px)}
  body.ready .hud, body.ready .hint{opacity:1; transform:none;
    transition:opacity .7s ease var(--d,0s), transform .8s cubic-bezier(.2,.9,.2,1) var(--d,0s)}

  /* ---------- brand sticker ---------- */
  .brand{top:20px; left:20px; max-width:352px; padding:14px 18px 16px; transform:rotate(-1.3deg)}
  body.ready .brand{transform:rotate(-1.3deg)}
  .eyebrow{display:flex; align-items:center; gap:8px; margin:0 0 4px; font-size:10.5px; font-weight:700;
    letter-spacing:.24em; text-transform:uppercase; color:var(--mint-d)}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--coral);box-shadow:0 0 0 3px rgba(255,106,77,.28);
    animation:pulse 1.6s infinite}
  @keyframes pulse{50%{box-shadow:0 0 0 7px rgba(255,106,77,0)}}
  .brand h1{font-family:"Lilita One",cursive; font-weight:400; margin:.05em 0 .35em;
    font-size:clamp(30px,4.4vw,50px); line-height:.87; letter-spacing:-.012em}
  .brand h1 .hl{color:var(--paper); background:var(--coral); padding:0 .12em; border-radius:6px;
    display:inline-block; transform:rotate(.8deg); box-shadow:3px 3px 0 var(--ink)}
  .sub{margin:0 0 8px; font-size:13px; line-height:1.45; color:var(--ink-soft); max-width:31ch}
  .sci{margin:0; font-size:10.5px; letter-spacing:.04em; color:rgba(36,26,38,.45);
    border-top:2px dotted rgba(36,26,38,.2); padding-top:7px}
  .sci b{font-style:italic; font-weight:700; color:var(--plum)}

  /* ---------- residents census ---------- */
  .residents{top:20px; right:20px; width:258px; padding-bottom:8px}
  .residents ul{list-style:none; margin:0; padding:6px; max-height:min(46vh,340px); overflow:auto}
  .residents ul::-webkit-scrollbar{width:8px}
  .residents ul::-webkit-scrollbar-thumb{background:rgba(36,26,38,.25); border-radius:9px}
  .res{display:grid; grid-template-columns:14px 1fr auto; grid-template-rows:auto 4px; gap:2px 9px;
    align-items:center; padding:7px 8px; border-radius:10px; cursor:pointer;
    transition:background .18s ease, transform .18s ease}
  .res:hover{background:var(--paper-2); transform:translateX(3px)}
  .res.on{background:var(--ink); color:var(--paper)}
  .res.on .st{color:var(--sun)} .res.on em{color:rgba(255,247,234,.6)}
  .sw{width:14px;height:14px;border-radius:5px;background:var(--c);border:2px solid var(--ink); grid-row:span 2}
  .res b{font-size:13px; font-weight:700; letter-spacing:-.01em; display:block; line-height:1.15}
  .res em{font-style:normal; font-size:9.5px; letter-spacing:.16em; text-transform:uppercase; color:rgba(36,26,38,.45)}
  .st{font-family:"Lilita One",cursive; font-size:11px; letter-spacing:.03em; color:var(--mint-d); white-space:nowrap}
  .bar{grid-column:2/4; height:4px; background:rgba(36,26,38,.14); border-radius:9px; overflow:hidden}
  .bar i{display:block; height:100%; background:var(--coral); border-radius:9px; transition:width .18s linear}
  .residents .foot{margin:2px 0 0; padding:8px 14px 9px; font-size:10px; letter-spacing:.1em;
    text-transform:uppercase; color:rgba(36,26,38,.42); border-top:2px dashed rgba(36,26,38,.2)}

  /* ---------- controls ---------- */
  .controls{left:20px; bottom:20px; width:308px; padding-bottom:10px}
  .btns{display:grid; grid-template-columns:1fr 1fr; gap:8px; padding:11px}
  .b{display:flex; align-items:center; gap:6px; font-family:"Space Grotesk"; font-weight:700; font-size:12.5px;
    letter-spacing:-.005em; color:var(--ink); background:var(--paper-2); border:2.5px solid var(--ink);
    border-radius:999px; padding:9px 11px; box-shadow:var(--shadow-sm); cursor:pointer;
    transition:transform .13s ease, box-shadow .13s ease, filter .2s ease}
  .b kbd{margin-left:auto; font-family:"Space Grotesk"; font-size:9.5px; font-weight:700; padding:1px 5px;
    border:2px solid var(--ink); border-radius:5px; background:rgba(255,255,255,.6)}
  .b:hover{transform:translate(-2px,-2px); box-shadow:5px 5px 0 rgba(36,26,38,.9); filter:saturate(1.15)}
  .b:active{transform:translate(2px,2px); box-shadow:1px 1px 0 rgba(36,26,38,.9)}
  .b.sun{background:var(--sun)} .b.mint{background:var(--mint)} .b.coral{background:var(--coral)}
  .b.plum{background:#e5d7ea} .b.ghost{background:transparent; box-shadow:none; border-style:dashed}
  .b.ghost:hover{background:var(--paper-2); transform:translateY(-1px)}
  .b.on{background:var(--plum); color:var(--paper)} .b.on kbd{border-color:var(--paper)}

  /* ---------- live stats strip ---------- */
  .stats{right:20px; bottom:20px; display:flex; align-items:stretch; gap:0; padding:0; overflow:hidden}
  .stat{padding:10px 16px 11px; border-right:2px dashed rgba(36,26,38,.2); min-width:84px; text-align:right}
  .stat:last-child{border-right:0}
  .stat b{display:block; font-family:"Lilita One",cursive; font-weight:400; font-size:27px; line-height:1;
    letter-spacing:-.01em; transition:color .2s ease}
  .stat span{display:block; font-size:9px; letter-spacing:.18em; text-transform:uppercase; color:rgba(36,26,38,.5); margin-top:3px}
  .stat b.pop{animation:pop .34s cubic-bezier(.3,1.6,.4,1)}
  @keyframes pop{0%{transform:scale(1)}40%{transform:scale(1.28); color:var(--coral)}100%{transform:scale(1)}}

  .hint{left:50%; bottom:22px; transform:translateX(-50%); z-index:10; position:fixed;
    font-size:10.5px; letter-spacing:.16em; text-transform:uppercase; color:rgba(36,26,38,.6);
    background:rgba(255,247,234,.78); border:2px solid rgba(36,26,38,.5); border-radius:999px; padding:6px 14px}
  body.ready .hint{transform:translateX(-50%)}

  /* ---------- floating tip / toast ---------- */
  .tip{position:fixed; z-index:30; pointer-events:none; opacity:0; transform:translate(-50%,-142%) scale(.9);
    background:var(--ink); color:var(--paper); border-radius:11px; padding:7px 11px; box-shadow:var(--shadow-sm);
    transition:opacity .16s ease, transform .16s cubic-bezier(.2,1.5,.4,1); white-space:nowrap}
  .tip.show{opacity:1; transform:translate(-50%,-158%) scale(1)}
  .tip b{font-family:"Lilita One",cursive; font-weight:400; font-size:13px; letter-spacing:.01em}
  .tip i{font-style:normal; color:var(--sun); font-size:11px}
  .toast{position:fixed; z-index:32; left:50%; bottom:78px; transform:translate(-50%,26px) scale(.94);
    opacity:0; pointer-events:none; background:var(--coral); color:#fff; border:3px solid var(--ink);
    border-radius:14px; box-shadow:var(--shadow); padding:9px 16px; font-weight:700; font-size:13px;
    transition:opacity .22s ease, transform .32s cubic-bezier(.2,1.5,.4,1)}
  .toast.show{opacity:1; transform:translate(-50%,0) scale(1)}

  /* ---------- loader ---------- */
  .loader{position:fixed; inset:0; z-index:60; display:grid; place-content:center; gap:20px; justify-items:center;
    background:linear-gradient(170deg,#ffe6bf,#ffd0a3 60%,#f7b98c); transition:opacity .6s ease}
  .loader.gone{opacity:0; pointer-events:none}
  .lmark{width:54px;height:54px;background:var(--coral);border:3px solid var(--ink);
    clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%); animation:tumble 1.1s infinite ease-in-out}
  @keyframes tumble{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-16px) rotate(180deg)}}
  .loader p{font-family:"Lilita One",cursive; letter-spacing:.14em; text-transform:uppercase; font-size:12px; color:var(--ink); margin:0}

  @media (max-width:1080px){
    .brand{max-width:300px} .residents{width:222px} .controls{width:274px}
  }
  @media (max-width:780px){
    .brand{left:12px; top:12px; right:12px; max-width:none; padding:11px 14px 12px}
    .sub,.sci{display:none} .hint{display:none} .stats{display:none}
    .residents{left:12px; right:12px; top:auto; bottom:108px; width:auto; padding:0}
    .residents .panel-h,.residents .foot{display:none}
    .residents ul{display:flex; gap:8px; overflow-x:auto; overflow-y:hidden; max-height:none; padding:8px}
    .res{grid-template-columns:12px auto; grid-template-rows:auto auto; flex:0 0 auto; border:2px solid var(--ink)}
    .st{grid-column:2} .bar{display:none}
    .controls{left:12px; right:12px; bottom:12px; width:auto}
    .btns{grid-auto-flow:column; grid-template-columns:none; overflow-x:auto; align-items:stretch}
    .b{flex:0 0 auto} .b kbd{display:none} .panel-h{display:none}
  }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div class="fx vig" aria-hidden="true"></div>
<div class="fx grain" aria-hidden="true"></div>
<div class="fx nightTint" aria-hidden="true"></div>

<header class="hud brand" style="--d:.05s">
  <p class="eyebrow"><span class="dot"></span>Exhibit 07 · habitat live</p>
  <h1>Low-Poly<br><span class="hl">Hamster</span><br>Playground</h1>
  <p class="sub">Six chunky rodents, one wobbly wheel and a tunnel of questionable engineering. Drag to orbit the enclosure.</p>
  <p class="sci"><b>Mesocricetus polygonus</b> · captive-bred for roundness</p>
</header>

<aside class="hud residents" style="--d:.18s">
  <div class="panel-h"><span>Residents</span><b id="popBadge">0/8</b></div>
  <ul id="resList"></ul>
  <p class="foot">hover to flag · click to follow</p>
</aside>

<section class="hud controls" style="--d:.3s">
  <div class="panel-h"><span>Habitat controls</span></div>
  <div class="btns">
    <button class="b sun"   data-act="food">🥕 Toss food <kbd>F</kbd></button>
    <button class="b mint"  data-act="wheel">🌀 Spin wheel <kbd>W</kbd></button>
    <button class="b plum"  data-act="night">🌙 Lights out <kbd>L</kbd></button>
    <button class="b coral" data-act="add">🐹 New hamster <kbd>N</kbd></button>
    <button class="b ghost" data-act="reset">🎯 Reset view <kbd>R</kbd></button>
    <button class="b ghost" data-act="sound">🔇 Sound <kbd>S</kbd></button>
  </div>
</section>

<div class="hud stats" style="--d:.42s">
  <div class="stat"><b id="sRpm">0</b><span>wheel rpm</span></div>
  <div class="stat"><b id="sSnack">0</b><span>snacks</span></div>
  <div class="stat"><b id="sBoop">0</b><span>boops</span></div>
  <div class="stat"><b id="sClock">12:00</b><span>habitat clock</span></div>
</div>

<p class="hint">drag to orbit · scroll to zoom · click the wheel, the bowl, or a hamster</p>

<div class="tip" id="tip"></div>
<div class="toast" id="toast"></div>
<div class="loader" id="loader"><div class="lmark"></div><p>digging bedding…</p></div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════ helpers ══════════════════ */
const rand  = (a,b)=>a+Math.random()*(b-a);
const pick  = a=>a[(Math.random()*a.length)|0];
const clamp = THREE.MathUtils.clamp;
const damp  = THREE.MathUtils.damp;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ══════════════════ renderer / scene ══════════════════ */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
function skyTexture(){
  const c = document.createElement('canvas'); c.width = 8; c.height = 320;
  const g = c.getContext('2d');
  const grd = g.createLinearGradient(0,0,0,320);
  grd.addColorStop(0,'#a8e6ff'); grd.addColorStop(.42,'#ffeecb');
  grd.addColorStop(.72,'#ffd3a0'); grd.addColorStop(1,'#f7b98c');
  g.fillStyle = grd; g.fillRect(0,0,8,320);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
scene.background = skyTexture();
scene.backgroundIntensity = 1;
scene.fog = new THREE.Fog(0xffd9b0, 30, 72);

const camera = new THREE.PerspectiveCamera(38, innerWidth/innerHeight, .1, 240);
const HOME_POS = new THREE.Vector3(11.6, 8.6, 14.4);
const HOME_TGT = new THREE.Vector3(0, 1.5, 0);
camera.position.copy(REDUCED ? HOME_POS : HOME_POS.clone().multiplyScalar(1.7).setY(16));

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = .07;
controls.target.copy(HOME_TGT);
controls.minDistance = 6.5; controls.maxDistance = 34;
controls.minPolarAngle = .28; controls.maxPolarAngle = 1.44;
controls.autoRotateSpeed = .45;
controls.enabled = !REDUCED ? false : true;

/* ══════════════════ lights ══════════════════ */
const hemi = new THREE.HemisphereLight(0xdff4ff, 0xffd39a, .8); scene.add(hemi);
const key  = new THREE.DirectionalLight(0xfff1d6, 2.35);
key.position.set(8,13,7); key.castShadow = true;
key.shadow.mapSize.set(2048,2048);
const sc = key.shadow.camera; sc.left=-13; sc.right=13; sc.top=13; sc.bottom=-13; sc.near=.5; sc.far=44;
key.shadow.bias = -.0007; key.shadow.normalBias = .045;
scene.add(key);
const fill = new THREE.DirectionalLight(0x9fd8ff, .55); fill.position.set(-9,6,-8); scene.add(fill);
const lamp = new THREE.PointLight(0xffb05c, 0, 16, 2); lamp.position.set(0,3.7,.4); scene.add(lamp);

/* ══════════════════ materials & shared geometry ══════════════════ */
const M = (color, o={}) => new THREE.MeshStandardMaterial({color, roughness:.92, flatShading:true, ...o});
const mat = {
  table : M(0x1f7a6a,{roughness:1}),
  trayIn: M(0xf2d7ab),
  trayOut: M(0xe8bf8c),
  bar   : new THREE.MeshStandardMaterial({color:0xfff4e4, metalness:.45, roughness:.38, flatShading:true}),
  post  : M(0xff6a4d),
  rail  : M(0xffc247),
  plasticMint: new THREE.MeshStandardMaterial({color:0x6fe3cd, roughness:.35, metalness:.05,
                transparent:true, opacity:.42, side:THREE.DoubleSide, flatShading:true, depthWrite:false}),
  bowl  : M(0xff6a4d),
  bowlIn: M(0xfff1dd),
  wood  : M(0xd98b52),
  wood2 : M(0xc06f3e),
  dark  : M(0x3a2b31,{roughness:.7}),
  wheelA: new THREE.MeshStandardMaterial({color:0x2ecaa6, roughness:.4, metalness:.12, flatShading:true}),
  wheelB: M(0xffc247),
  seed1 : M(0xe8a33d), seed2: M(0xb5763f), seed3: M(0x9ecb52),
  carrot: M(0xff7a2f), greens: M(0x6cbf49)
};
const G = {
  body : new THREE.SphereGeometry(.52, 7, 5),
  head : new THREE.SphereGeometry(.38, 7, 5),
  small: new THREE.SphereGeometry(.16, 6, 4),
  eye  : new THREE.SphereGeometry(.085, 6, 5),
  glint: new THREE.SphereGeometry(.03, 5, 4),
  leg  : new THREE.BoxGeometry(.15,.26,.19),
  cone5: new THREE.ConeGeometry(.17,.3,5),
  nub  : new THREE.ConeGeometry(.09,.2,5),
  seed : new THREE.CylinderGeometry(.14,.11,.17,6)
};

/* ══════════════════ habitat: table, tray, bedding ══════════════════ */
const WORLD = new THREE.Group(); scene.add(WORLD);

const table = new THREE.Mesh(new THREE.CircleGeometry(38, 42), mat.table);
table.rotation.x = -Math.PI/2; table.position.y = -1.62; table.receiveShadow = true; WORLD.add(table);

const tray = new THREE.Mesh(new THREE.BoxGeometry(14.6, 1.5, 11.1), mat.trayOut);
tray.position.y = -.76; tray.castShadow = true; tray.receiveShadow = true; WORLD.add(tray);
const trayIn = new THREE.Mesh(new THREE.BoxGeometry(13.4, .28, 9.9), mat.trayIn);
trayIn.position.y = .02; trayIn.receiveShadow = true; WORLD.add(trayIn);

// bedding pellets (instanced)
const BED_N = 190, bed = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.17,0),
        new THREE.MeshStandardMaterial({roughness:1, flatShading:true}), BED_N);
bed.castShadow = true; bed.receiveShadow = true;
{
  const d = new THREE.Object3D(), c = new THREE.Color(), tints = [0xf5dfb8,0xe9c894,0xdcb27c,0xfff0d4];
  for(let i=0;i<BED_N;i++){
    d.position.set(rand(-6.2,6.2), rand(.04,.16), rand(-4.4,4.4));
    d.rotation.set(rand(0,3),rand(0,3),rand(0,3));
    d.scale.set(rand(.7,1.5), rand(.4,.8), rand(.7,1.4));
    d.updateMatrix(); bed.setMatrixAt(i,d.matrix); bed.setColorAt(i, c.setHex(pick(tints)));
  }
  bed.instanceColor.needsUpdate = true;
}
WORLD.add(bed);

// soft mounds
[[-1.9,3.0,1.25],[4.9,3.1,.95],[-5.4,-3.2,1.05]].forEach(([x,z,r])=>{
  const m = new THREE.Mesh(new THREE.SphereGeometry(r,8,4), M(0xf8e3bd));
  m.position.set(x,-r*.72,z); m.scale.y = .3; m.receiveShadow = true; WORLD.add(m);
});

/* ══════════════════ cage bars + frame ══════════════════ */
const CAGE = {hw:6.5, hd:4.75, h:4.4};
{
  const spots = [];
  for(let x=-CAGE.hw; x<=CAGE.hw+.01; x+=.52){ spots.push([x, CAGE.hd]); spots.push([x,-CAGE.hd]); }
  for(let z=-CAGE.hd+.52; z<=CAGE.hd-.5; z+=.52){ spots.push([ CAGE.hw, z]); spots.push([-CAGE.hw, z]); }
  const bars = new THREE.InstancedMesh(new THREE.CylinderGeometry(.075,.075,CAGE.h,5), mat.bar, spots.length);
  const d = new THREE.Object3D();
  spots.forEach(([x,z],i)=>{ d.position.set(x, CAGE.h/2, z); d.rotation.set(0,0,0); d.updateMatrix(); bars.setMatrixAt(i,d.matrix); });
  bars.castShadow = true; WORLD.add(bars);

  // top frame + lid rails + corner posts + handle
  const railGeoX = new THREE.BoxGeometry(CAGE.hw*2+.5,.2,.2), railGeoZ = new THREE.BoxGeometry(.2,.2,CAGE.hd*2+.5);
  [[0,CAGE.h+.1, CAGE.hd+.1,railGeoX],[0,CAGE.h+.1,-CAGE.hd-.1,railGeoX],
   [ CAGE.hw+.1,CAGE.h+.1,0,railGeoZ],[-CAGE.hw-.1,CAGE.h+.1,0,railGeoZ]].forEach(([x,y,z,g])=>{
    const m = new THREE.Mesh(g, mat.rail); m.position.set(x,y,z); m.castShadow = true; WORLD.add(m);
  });
  for(let x=-CAGE.hw+.4; x<=CAGE.hw-.4; x+=.95){
    const m = new THREE.Mesh(new THREE.BoxGeometry(.11,.13,CAGE.hd*2+.2), mat.bar);
    m.position.set(x,CAGE.h+.28,0); m.castShadow = true; WORLD.add(m);
  }
  [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(([sx,sz])=>{
    const p = new THREE.Mesh(new THREE.BoxGeometry(.34,CAGE.h+.9,.34), mat.post);
    p.position.set(sx*(CAGE.hw+.18), (CAGE.h+.9)/2-.7, sz*(CAGE.hd+.18)); p.castShadow = true; WORLD.add(p);
  });
  const handle = new THREE.Mesh(new THREE.TorusGeometry(.62,.1,5,14), mat.post);
  handle.rotation.x = Math.PI/2; handle.position.set(0,CAGE.h+.44,0); handle.castShadow = true; WORLD.add(handle);

  // front hatch frame
  const hatch = new THREE.Group(); hatch.position.set(-.2,.2,CAGE.hd+.06);
  [[0,1.5,3.2,.16],[0,0,3.2,.16],[1.6,.75,.16,.16],[-1.6,.75,.16,.16]].forEach(([x,y,w,h])=>{
    const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,.16), mat.rail); m.position.set(x,y,0); hatch.add(m);
  });
  WORLD.add(hatch);
}

/* ══════════════════ wheel (interactive) ══════════════════ */
const WHEEL = {x:-4.1, y:1.52, z:-2.15, r:1.45};
const wheelSpin = new THREE.Group();
let wheelVel = 0, rider = null;
{
  const g = new THREE.Group(); g.position.set(WHEEL.x, WHEEL.y, WHEEL.z); WORLD.add(g);
  wheelSpin.position.set(0,0,0); g.add(wheelSpin);

  const rim = new THREE.Mesh(new THREE.TorusGeometry(WHEEL.r,.17,5,18), mat.wheelA);
  rim.castShadow = true; wheelSpin.add(rim);
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(WHEEL.r-.06,WHEEL.r-.06,.07,20), mat.wheelB);
  plate.rotation.x = Math.PI/2; plate.position.z = -.5; plate.castShadow = true; wheelSpin.add(plate);
  for(let i=0;i<11;i++){
    const a = i/11*Math.PI*2;
    const rung = new THREE.Mesh(new THREE.BoxGeometry(.15,.15,1.02), mat.wheelA);
    rung.position.set(Math.cos(a)*(WHEEL.r-.24), Math.sin(a)*(WHEEL.r-.24), 0);
    rung.castShadow = true; wheelSpin.add(rung);
  }
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(.2,.2,1.7,8), mat.dark);
  hub.rotation.x = Math.PI/2; g.add(hub);
  [-0.78,0.78].forEach(z=>{
    const leg = new THREE.Mesh(new THREE.BoxGeometry(.24,WHEEL.y,.24), mat.post);
    leg.position.set(WHEEL.x, WHEEL.y/2, WHEEL.z+z); leg.castShadow = true; WORLD.add(leg);
  });
  const foot = new THREE.Mesh(new THREE.BoxGeometry(1.1,.2,2.1), mat.post);
  foot.position.set(WHEEL.x,.1,WHEEL.z); foot.castShadow = true; WORLD.add(foot);
  g.userData.pick = 'wheel';
}
const WHEEL_MOUNT = new THREE.Vector3(WHEEL.x, WHEEL.y-.74, WHEEL.z);

/* ══════════════════ hut / nest / tunnel / bowl / bottle ══════════════════ */
const HUT = {x:3.9, z:-2.5};
{
  const hut = new THREE.Group(); hut.position.set(HUT.x,0,HUT.z); WORLD.add(hut);
  const floor = new THREE.Mesh(new THREE.BoxGeometry(2.9,.2,2.3), mat.wood2); floor.position.y=.1;
  const back  = new THREE.Mesh(new THREE.BoxGeometry(2.9,1.6,.2), mat.wood);  back.position.set(0,.9,-1.05);
  const left  = new THREE.Mesh(new THREE.BoxGeometry(.2,1.6,2.3), mat.wood);  left.position.set(-1.35,.9,0);
  const right = left.clone(); right.position.x = 1.35;
  [floor,back,left,right].forEach(m=>{m.castShadow=true;m.receiveShadow=true;hut.add(m);});
  const roof = new THREE.Mesh(new THREE.CylinderGeometry(1.72,1.72,3.1,3), mat.wood2);
  roof.rotation.z = Math.PI/2; roof.rotation.y = Math.PI/2; roof.position.set(0,1.98,0);
  roof.scale.set(.62,1,1); roof.rotation.x = Math.PI/2; roof.castShadow = true; hut.add(roof);
  hut.traverse(o=>{ if(o.isMesh) o.castShadow = true; });
}
const NESTS = [new THREE.Vector3(-1.9,.0,3.0), new THREE.Vector3(3.9,.0,-.75), new THREE.Vector3(-4.9,.0,3.4)];
{ // nest ring
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.05,.16,5,14), M(0xe4bd8e));
  ring.rotation.x = Math.PI/2; ring.position.set(-1.9,.12,3.0); ring.receiveShadow = true; WORLD.add(ring);
}

const TUN_A = new THREE.Vector3(1.1,.62,3.35), TUN_B = new THREE.Vector3(5.35,.62,1.15);
{
  const dir = new THREE.Vector3().subVectors(TUN_B,TUN_A), len = dir.length();
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(.64,.64,len,9,1,true), mat.plasticMint);
  tube.position.copy(TUN_A).addScaledVector(dir,.5);
  tube.rotation.x = Math.PI/2; tube.rotation.y = 0;
  tube.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir.clone().normalize());
  WORLD.add(tube);
  [TUN_A,TUN_B].forEach(p=>{
    const rim = new THREE.Mesh(new THREE.TorusGeometry(.66,.1,5,14), mat.coralRim || (mat.coralRim = M(0xff6a4d)));
    rim.position.copy(p); rim.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), dir.clone().normalize());
    rim.castShadow = true; WORLD.add(rim);
  });
}

const BOWL = new THREE.Vector3(-4.85,.0,2.45);
{
  const g = new THREE.Group(); g.position.copy(BOWL); WORLD.add(g);
  const outer = new THREE.Mesh(new THREE.CylinderGeometry(.78,.52,.46,10), mat.bowl);
  outer.position.y = .23; outer.castShadow = true; outer.receiveShadow = true; g.add(outer);
  const inner = new THREE.Mesh(new THREE.CylinderGeometry(.62,.42,.34,10), mat.bowlIn);
  inner.position.y = .3; g.add(inner);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(.76,.08,5,14), mat.bowl);
  rim.rotation.x = Math.PI/2; rim.position.y = .45; rim.castShadow = true; g.add(rim);
  for(let i=0;i<5;i++){
    const s = new THREE.Mesh(G.seed, pick([mat.seed1,mat.seed2,mat.seed3]));
    s.position.set(rand(-.4,.4),.45,rand(-.4,.4)); s.rotation.set(rand(0,3),rand(0,3),rand(0,3)); g.add(s);
  }
  g.userData.pick = 'bowl';
}
{ // water bottle on the front bars
  const g = new THREE.Group(); g.position.set(-1.4,2.35,CAGE.hd+.42); WORLD.add(g);
  const bottle = new THREE.Mesh(new THREE.CylinderGeometry(.34,.34,1.5,10),
    new THREE.MeshStandardMaterial({color:0xbdefff, transparent:true, opacity:.55, roughness:.15, metalness:.1}));
  bottle.castShadow = true; g.add(bottle);
  const cap = new THREE.Mesh(new THREE.CylinderGeometry(.2,.24,.28,8), mat.mintCap || (mat.mintCap = M(0x2ecaa6)));
  cap.position.y = -.82; g.add(cap);
  const spout = new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,.9,6), mat.bar);
  spout.rotation.x = Math.PI/2; spout.position.set(0,-.9,-.45); g.add(spout);
}

/* ══════════════════ hamsters ══════════════════ */
const HAM_CFG = [
  {body:0xf7c05b, patch:0xe08a3c, belly:0xfff1d2, ear:0xffb0a3},
  {body:0xfbf0e2, patch:0x9a6242, belly:0xfff8ef, ear:0xffc2b8},
  {body:0xc7ced6, patch:0x6f7c87, belly:0xf3f6f8, ear:0xffb9b0},
  {body:0xfff7f0, patch:0x2e2a2c, belly:0xffffff, ear:0xffc0bb},
  {body:0xe2874a, patch:0xb4552a, belly:0xffe6cf, ear:0xffa79c},
  {body:0xf3d9a4, patch:0xc9a05e, belly:0xfff6e4, ear:0xffb6ab},
  {body:0x8f7bd1, patch:0x5c47a0, belly:0xe9e2ff, ear:0xffb9d0},
  {body:0x9fd98a, patch:0x5da06a, belly:0xf0ffe8, ear:0xffc1c8}
];
const NAMES = ['Nugget','Mochi','Waffles','Biscuit','Peanut','Noodle','Pickle','Butter','Tofu','Zucchini','Dumpling','Crisp'];
const MOODS = ['zoomie','sleepy','hungry','cheeky'];
const WEIGHTS = {
  zoomie : {wander:.30, wheel:.30, tunnel:.22, pause:.10, eat:.08},
  sleepy : {nap:.34, pause:.26, wander:.20, eat:.16, wheel:.04},
  hungry : {eat:.44, wander:.20, pause:.14, wheel:.12, tunnel:.10},
  cheeky : {tunnel:.26, wander:.28, pause:.20, eat:.14, wheel:.12}
};
const LABEL = {
  wander:'exploring', sniffing:'sniffing around', groom:'grooming', look:'watching you',
  riding:'on the wheel', nibble:'snacking', tunnel:'in the tunnel', zoomies:'ZOOMIES',
  nap:'curled up', boop:'BOOPED'
};
const MAX_H = 8;
const hamsters = [];
const BLOCKERS = [{x:WHEEL.x, z:WHEEL.z, r:1.05}, {x:HUT.x, z:HUT.z, r:1.9}];
let nameBag = NAMES.slice();

function makeHamster(cfg){
  const root = new THREE.Group(), bob = new THREE.Group(); root.add(bob);
  const fur   = M(cfg.body), patch = M(cfg.patch), bellyM = M(cfg.belly),
        pink  = M(cfg.ear),  dark  = new THREE.MeshStandardMaterial({color:0x2a1f26, roughness:.35, metalness:.1}),
        glintM= new THREE.MeshBasicMaterial({color:0xffffff});

  const body = new THREE.Mesh(G.body, fur); body.scale.set(1.06,.96,1.24); body.position.y=.52; bob.add(body);
  const saddle = new THREE.Mesh(G.body, patch); saddle.scale.set(1.03,.9,1.0); saddle.position.set(0,.6,-.14); bob.add(saddle);
  const belly = new THREE.Mesh(G.body, bellyM); belly.scale.set(1.03,.9,.98); belly.position.set(0,.42,.1); bob.add(belly);

  const head = new THREE.Group(); head.position.set(0,.78,.44); bob.add(head);
  const skull = new THREE.Mesh(G.head, fur); skull.scale.set(1,.94,.95); head.add(skull);
  const snout = new THREE.Mesh(G.cone5, bellyM); snout.rotation.x = Math.PI/2; snout.position.set(0,-.06,.3); head.add(snout);
  const nose = new THREE.Mesh(G.glint, pink); nose.scale.setScalar(2.1); nose.position.set(0,-.04,.47); head.add(nose);

  const eyes = [];
  [-1,1].forEach(s=>{
    const e = new THREE.Group(); e.position.set(.19*s,.06,.28); head.add(e);
    const ball = new THREE.Mesh(G.eye, dark); e.add(ball);
    const gl = new THREE.Mesh(G.glint, glintM); gl.position.set(.03,.04,.07); e.add(gl);
    eyes.push(e);
    const ear = new THREE.Group(); ear.position.set(.27*s,.28,-.06); head.add(ear);
    const pinna = new THREE.Mesh(G.small, fur); pinna.scale.set(1,1,.42); ear.add(pinna);
    const inner = new THREE.Mesh(G.small, pink); inner.scale.set(.55,.55,.45); inner.position.z=.05; ear.add(inner);
    const cheek = new THREE.Mesh(G.small, bellyM); cheek.position.set(.3*s,-.16,.16); cheek.scale.set(1,.95,.9);
    head.add(cheek);
    if(!eyes.length) return;
  });
  const cheeks = head.children.filter(o=>o.geometry===G.small && o.material===bellyM);

  const legs = [];
  [[-.25,.3],[.25,.3],[-.27,-.26],[.27,-.26]].forEach(([x,z])=>{
    const l = new THREE.Group(); l.position.set(x,.24,z); bob.add(l);
    const m = new THREE.Mesh(G.leg, fur); m.position.y=-.13; l.add(m); legs.push(l);
  });
  const tail = new THREE.Mesh(G.nub, patch); tail.rotation.x = -Math.PI/2; tail.position.set(0,.5,-.62); bob.add(tail);

  bob.traverse(o=>{ if(o.isMesh){o.castShadow=true;o.receiveShadow=true;} });
  WORLD.add(root);
  return {root, bob, head, eyes, legs, cheeks, nose};
}

function addHamster(){
  if(hamsters.length >= MAX_H){ toast('Cage is at capacity — eight is plenty.'); return null; }
  const cfgIdx = hamsters.length % HAM_CFG.length;
  const cfg = HAM_CFG[cfgIdx];
  const parts = makeHamster(cfg);
  const h = {
    ...parts,
    id: hamsters.length,
    name: nameBag.length ? nameBag.splice((Math.random()*nameBag.length)|0,1)[0] : 'Specimen '+(hamsters.length+1),
    mood: pick(MOODS),
    color: '#'+new THREE.Color(cfg.body).getHexString(),
    pos: new THREE.Vector3(rand(-3.5,3.5), 0, rand(-2.5,3)),
    yaw: rand(0,6.28), state:'wander', sub:'', t:0, dur:2, speed:1.15,
    phase: rand(0,6.28), blink: rand(1,4), boost:0, hop:0,
    target:new THREE.Vector3(), tunnelP:0, tunnelDir:1, food:null,
    size: rand(.78,1.06), flagged:false
  };
  h.root.position.copy(h.pos); h.root.scale.setScalar(h.size);
  enterState(h,'wander');
  hamsters.push(h); buildRow(h); updateBadge();
  puff(h.pos, 6);
  return h;
}

/* ---------- behaviour ---------- */
function floorPoint(){
  for(let i=0;i<24;i++){
    const x = rand(-5.2,5.2), z = rand(-3.7,3.7);
    if(BLOCKERS.every(b=>Math.hypot(x-b.x,z-b.z) > b.r+.4)) return new THREE.Vector3(x,0,z);
  }
  return new THREE.Vector3(0,0,2);
}
function weightedState(extra={}){
  const w = {...WEIGHTS[hamsters.length? 'cheeky':'cheeky'], ...extra};
  const entries = Object.entries(w).map(([k,v])=>[k, v + (night>.4 && k==='nap' ? .3 : 0) + (night>.4 && k==='wheel' ? -.02 : 0)]);
  let total = entries.reduce((s,[,v])=>s+Math.max(0,v),0), r = Math.random()*total;
  for(const [k,v] of entries){ r -= Math.max(0,v); if(r<=0) return k; }
  return 'wander';
}
function enterState(h, s){
  h.state = s; h.t = 0; h.food = null;
  const w = WEIGHTS[h.mood];
  switch(s){
    case 'wander': h.target.copy(floorPoint()); h.speed = rand(1.05,1.6)*(h.mood==='zoomie'?1.25:1); h.dur = rand(3,7); h.sub=''; break;
    case 'pause' : h.sub = pick(['sniffing','groom','look']); h.speed = 0; h.dur = rand(1.2,3.2); h.sub = h.sub==='look'?'watching you':h.sub; break;
    case 'wheel' : h.target.copy(WHEEL_MOUNT).setY(0); h.target.z += .95; h.speed = 1.5; h.dur = rand(4,9); h.sub=''; break;
    case 'eat'   : { const p = nearestPellet(h); h.target.copy(p ? p.mesh.position : BOWL).setY(0); h.speed = 1.25; h.dur = rand(3,6); h.sub=''; break; }
    case 'tunnel': h.tunnelDir = Math.random()<.5?1:-1;
                   h.target.copy(h.tunnelDir>0?TUN_A:TUN_B).setY(0); h.speed = 1.6; h.dur = rand(4,8); h.sub=''; break;
    case 'nap'   : h.target.copy(Math.random()<.72 ? pick(NESTS) : h.pos); h.speed = .95; h.dur = rand(6,13); h.sub=''; break;
  }
}
function pickNext(h){
  const w = {...WEIGHTS[h.mood]};
  if(rider && rider!==h) w.wheel = 0;
  if(night>.45){ w.nap += .3; w.wheel *= .4; w.tunnel *= .6; }
  let total = Object.values(w).reduce((a,b)=>a+b,0), r = Math.random()*total;
  for(const k in w){ r -= w[k]; if(r<=0) return enterState(h,k); }
  enterState(h,'wander');
}
function nearestPellet(h){
  let best=null, bd=1e9;
  for(const p of pellets){
    if(p.state!=='idle') continue;
    const d = Math.hypot(p.mesh.position.x-h.pos.x, p.mesh.position.z-h.pos.z);
    if(d<bd){bd=d;best=p;}
  }
  return best;
}

const tmpV = new THREE.Vector3();
function updateHamster(h, dt, t){
  h.t += dt;
  const st = h.state;
  const moving = (st==='wander'||st==='wheel'||st==='eat'||st==='tunnel'||st==='nap');

  if(st==='zoomies'){
    if(h.t>h.dur){ enterState(h,'pause'); }
    else {
      h.speed = 3.4;
      if(h.t>h.targetSet || !h.target){ h.target.copy(floorPoint()); h.targetSet=h.t+.9; }
    }
  }

  if(moving || st==='zoomies'){
    tmpV.subVectors(h.target, h.pos); tmpV.y = 0;
    const d = tmpV.length();
    if(d < .26){
      if(st==='wheel' && !rider){ rider = h; h.state='riding'; h.t=0; h.dur=rand(5,11); }
      else if(st==='eat'){ h.state='nibble'; h.t=0; h.dur=rand(2,4); h.food=nearestPellet(h); }
      else if(st==='tunnel'){ h.state='tunnelIn'; h.tunnelP=0; }
      else if(st==='nap'){ /* settled below */ h.sub=''; }
      else pickNext(h);
    } else {
      const sp = h.speed * (h.boost>0?1.9:1);
      h.pos.addScaledVector(tmpV.normalize(), Math.min(sp*dt, d));
      const want = Math.atan2(tmpV.x, tmpV.z);
      let diff = ((want - h.yaw + Math.PI)%6.283) - Math.PI; if(diff<-Math.PI) diff+=6.283;
      h.yaw += diff * Math.min(1, dt*7);
    }
  }

  if(st==='nibble'){
    const p = h.food && h.food.state==='idle' ? h.food : (h.food = nearestPellet(h));
    const anchor = p ? p.mesh.position : BOWL;
    tmpV.set(anchor.x - h.pos.x, 0, anchor.z - h.pos.z);
    if(tmpV.length() > .72){ h.target.copy(anchor).setY(0); h.state='eat'; }
    else {
      const want = Math.atan2(tmpV.x, tmpV.z);
      let diff = ((want - h.yaw + Math.PI)%6.283) - Math.PI; if(diff<-Math.PI) diff+=6.283;
      h.yaw += diff*Math.min(1,dt*6);
      if(p){ p.progress += dt*(p.kind==='carrot'?.5:.95); p.mesh.scale.setScalar(Math.max(.02,1-p.progress));
             if(p.progress>=1){ p.state='gone'; p.mesh.visible=false; snacks++; puff(p.mesh.position,4); h.food=null; } }
      else if(h.t>h.dur*.6 && !h.dugOnce){ h.dugOnce=true; snacks++; }
      if(h.t>h.dur){ h.dugOnce=false; pickNext(h); }
    }
  }

  if(st==='tunnelIn'){
    h.tunnelP += dt*.55;
    const a = h.tunnelDir>0?TUN_A:TUN_B, b = h.tunnelDir>0?TUN_B:TUN_A;
    h.pos.lerpVectors(a,b,clamp(h.tunnelP,0,1));
    h.yaw = Math.atan2(b.x-a.x, b.z-a.z);
    if(h.tunnelP>=1){ h.state='zoomies'; h.t=0; h.dur=rand(2.4,4.2); h.targetSet=0; snacks+=0; }
  }

  if(st==='riding'){
    h.pos.set(WHEEL.x, 0, WHEEL.z); h.yaw = Math.PI/2;
    wheelVel = damp(wheelVel, -5.6, 2.2, dt);
    if(h.t>h.dur || (h.t>1 && rider!==h)){ rider=null; h.state='wander'; h.t=0; enterState(h,'wander'); }
  }

  if(st==='boop'){
    h.hop = Math.abs(Math.sin(h.t*13)) * Math.max(0,.42-h.t*.3);
    h.yaw += dt*3.2;
    if(h.t>.95){ h.hop=0; enterState(h,'wander'); }
  }

  if(st==='nap' && h.t>h.dur) pickNext(h);

  // keep inside the tray & out of solid props
  if(st!=='riding' && st!=='tunnelIn'){
    h.pos.x = clamp(h.pos.x, -5.5, 5.5); h.pos.z = clamp(h.pos.z, -3.85, 3.85);
    if(st==='wander'||st==='pause'||st==='zoomies'||st==='nap'){
      for(const b of BLOCKERS){
        const dx = h.pos.x-b.x, dz = h.pos.z-b.z, d = Math.hypot(dx,dz);
        if(d < b.r && d > 1e-4){ h.pos.x = b.x + dx/d*b.r; h.pos.z = b.z + dz/d*b.r; }
      }
    }
  }

  /* ---- animation ---- */
  const asleep = st==='nap' || (night>.55 && st==='pause' && h.t>2.4);
  const napMix = damp(h.napMix||0, asleep?1:0, 6, dt); h.napMix = napMix;
  const gait = (st==='wander'||st==='wheel'||st==='eat'||st==='tunnel'||st==='zoomies'||st==='nap') ? h.speed : 0;
  h.phase += dt * (2.2 + gait*4.6);

  const scrambling = st==='riding';
  const legAmp = scrambling?.95 : gait>.1 ? .62 : .07;
  h.legs.forEach((l,i)=>{ l.rotation.x = Math.sin(h.phase*(scrambling?2.1:1) + i*Math.PI)*legAmp; });

  const walkBob = gait>.1 ? Math.sin(h.phase*2)*.035*gait : 0;
  h.bob.position.y = walkBob;
  h.bob.rotation.z = gait>.1 ? Math.sin(h.phase)*.05 : Math.sin(t*.9+h.id)*.012;
  h.bob.scale.set(1+napMix*.14, 1-napMix*.26, 1+napMix*.1);
  h.head.rotation.x = (st==='nibble'? Math.sin(t*16)*.14 : 0) + (h.sub==='sniffing'? Math.sin(t*7)*.1:0) + napMix*.3;
  h.head.rotation.z = h.sub==='look' ? Math.sin(t*1.3+h.id)*.12 : 0;

  const chewing = st==='nibble' ? 1 : 0;
  h.cheeks.forEach((c,i)=>{ const s = 1 + chewing*(.5+Math.sin(t*11+i)*.12); c.scale.set(s,.95*s,.9*s); });

  h.blink -= dt;
  if(h.blink<0) h.blink = rand(1.6,5.2);
  const blinkT = h.blink<.13 ? 1 : 0;
  const lidY = Math.max(blinkT, napMix);
  h.eyes.forEach(e=> e.scale.y = 1 - lidY*.88);

  if(asleep && Math.random() < dt*.7) spawnParticle('z', new THREE.Vector3(h.pos.x, .9+h.size, h.pos.z));
  if(scrambling && Math.random() < dt*1.2) spawnParticle('dust', new THREE.Vector3(h.pos.x+rand(-.4,.4), .18, h.pos.z+rand(-.4,.4)));

  h.boost = Math.max(0, h.boost-dt);
  h.root.position.set(h.pos.x, h.hop, h.pos.z);
  h.root.rotation.y = h.yaw;
}

/* separation */
function separate(){
  for(let i=0;i<hamsters.length;i++) for(let j=i+1;j<hamsters.length;j++){
    const a=hamsters[i], b=hamsters[j];
    if(a.state==='riding'||b.state==='riding') continue;
    const dx=b.pos.x-a.pos.x, dz=b.pos.z-a.pos.z, d=Math.hypot(dx,dz), min=.86;
    if(d<min && d>1e-4){
      const push=(min-d)/2, ux=dx/d, uz=dz/d;
      a.pos.x-=ux*push; a.pos.z-=uz*push; b.pos.x+=ux*push; b.pos.z+=uz*push;
    }
  }
}

/* ══════════════════ food pellets ══════════════════ */
const pellets = [];
const pelletPool = [];
function getPelletMesh(kind){
  let p = pelletPool.find(p=>p.state==='gone' && p.kind===kind);
  if(!p){
    const mesh = kind==='carrot'
      ? new THREE.Mesh(new THREE.ConeGeometry(.16,.6,6), mat.carrot)
      : new THREE.Mesh(G.seed, pick([mat.seed1,mat.seed2,mat.seed3]));
    mesh.castShadow = true; WORLD.add(mesh);
    p = {mesh, kind, state:'gone', vy:0, progress:0}; pellets.push(p);
  }
  return p;
}
function tossFood(n=4){
  let made = 0;
  for(let i=0;i<n;i++){
    const kind = Math.random()<.25 ? 'carrot':'seed';
    const p = getPelletMesh(kind);
    const a = rand(0,6.28), r = rand(1.2,3.4);
    p.mesh.position.set(BOWL.x+Math.cos(a)*r*.5, 3.9, BOWL.z+Math.sin(a)*r*.5);
    if(kind==='carrot') p.mesh.rotation.set(rand(-.4,.4),rand(0,3),rand(-.4,.4));
    p.mesh.scale.setScalar(1); p.mesh.visible = true;
    p.state='fly'; p.vy = rand(-1,1); p.progress=0; made++;
    hamsters.forEach(h=>{ if(h.state==='pause'||h.state==='nap'){ if(Math.random()<.6) enterState(h,'eat'); } });
  }
  snacks += 0; beep(520,.07,'triangle',.05); setTimeout(()=>beep(760,.06,'triangle',.04),90);
  toast(made+' snack'+(made>1?'s':'')+' hit the tray');
}
function updatePellets(dt){
  for(const p of pellets){
    if(p.state!=='fly') continue;
    p.vy -= 20*dt; p.mesh.position.y += p.vy*dt;
    p.mesh.rotation.x += dt*4;
    if(p.mesh.position.y <= .18){
      p.mesh.position.y = .18;
      if(Math.abs(p.vy) > 1.6){ p.vy = -p.vy*.32; puff(p.mesh.position,2); }
      else { p.state='idle'; puff(p.mesh.position,3); }
    }
  }
  // hamsters go hunting when food lands
}

/* ══════════════════ particles ══════════════════ */
function labelTex(draw){
  const c = document.createElement('canvas'); c.width=c.height=128;
  draw(c.getContext('2d'));
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const TEX = {
  heart: labelTex(g=>{g.fillStyle='#ff4d6d'; g.beginPath();
      g.moveTo(64,110); g.bezierCurveTo(4,62,18,8,64,40); g.bezierCurveTo(110,8,124,62,64,110); g.fill();}),
  z: labelTex(g=>{g.fillStyle='#2a3f7a'; g.font='700 92px "Lilita One", sans-serif'; g.textAlign='center';
      g.textBaseline='middle'; g.fillText('z',64,70);}),
  dust: labelTex(g=>{const gr=g.createRadialGradient(64,64,4,64,64,58);
      gr.addColorStop(0,'rgba(255,240,214,.95)'); gr.addColorStop(1,'rgba(255,240,214,0)');
      g.fillStyle=gr; g.beginPath(); g.arc(64,64,58,0,7); g.fill();})
};
const particles = [];
for(let i=0;i<30;i++){
  const s = new THREE.Sprite(new THREE.SpriteMaterial({map:TEX.dust, transparent:true, depthWrite:false, opacity:0}));
  s.scale.setScalar(.5); WORLD.add(s);
  particles.push({s, life:0, ttl:1, vy:.6, kind:'dust'});
}
function spawnParticle(kind, pos){
  const p = particles.find(p=>p.life<=0); if(!p) return;
  p.kind = kind; p.s.material.map = TEX[kind]; p.s.material.needsUpdate = true;
  p.s.position.copy(pos); p.s.position.x += rand(-.15,.15);
  p.life = p.ttl = kind==='z'?2.1:.6;
  p.vy = kind==='z'?.7:rand(.5,1.2);
  p.s.scale.setScalar(kind==='dust'?.34:.42);
  p.s.material.opacity = 1;
}
function puff(pos,n=4){ for(let i=0;i<n;i++) spawnParticle('dust', new THREE.Vector3(pos.x+rand(-.3,.3),.2,pos.z+rand(-.3,.3))); }
function hearts(pos){ for(let i=0;i<3;i++) setTimeout(()=>spawnParticle('heart', new THREE.Vector3(pos.x,.95,pos.z)), i*110); }
function updateParticles(dt){
  for(const p of particles){
    if(p.life<=0) continue;
    p.life -= dt;
    const k = clamp(p.life/p.ttl,0,1);
    p.s.position.y += p.vy*dt;
    p.s.position.x += Math.sin((1-k)*6)*dt*.25;
    p.s.material.opacity = k;
    p.s.scale.setScalar((p.kind==='z'? .3+(1-k)*.4 : .3*(1.6-k)));
    if(p.life<=0) p.s.material.opacity = 0;
  }
}

/* ══════════════════ highlight ring ══════════════════ */
const ring = new THREE.Mesh(new THREE.RingGeometry(.62,.86,26),
  new THREE.MeshBasicMaterial({color:0x2ecaa6, transparent:true, opacity:.9, side:THREE.DoubleSide}));
ring.rotation.x = -Math.PI/2; ring.position.y = .09; ring.visible = false; WORLD.add(ring);

/* ══════════════════ picking & interaction ══════════════════ */
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
let hovered = null, focusId = null, downAt = null;
const tipEl = document.getElementById('tip');

function pickables(){
  const list = [];
  WORLD.children.forEach(o=>{ if(o.userData.pick) list.push(o); });
  hamsters.forEach(h=>list.push(h.root));
  return list;
}
function findPick(obj){
  while(obj){
    if(obj.userData.h) return obj.userData.h;
    if(obj.userData.pick) return obj.userData.pick;
    obj = obj.parent;
  }
  return null;
}
function pointerNdc(e){ ndc.x = (e.clientX/innerWidth)*2-1; ndc.y = -(e.clientY/innerHeight)*2+1; }
function hoverTest(e){
  pointerNdc(e); ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(pickables(), true)[0];
  const p = hit ? findPick(hit.object) : null;
  hovered = p;
  canvas.style.cursor = p ? 'pointer' : 'grab';
  if(p && typeof p === 'object'){
    showTip(e.clientX, e.clientY, `<b>${p.name}</b> <i>${LABEL[p.state]||''} · ${p.mood}</i>`);
  } else if(p==='wheel'){
    showTip(e.clientX, e.clientY, `<b>Exercise wheel</b> <i>click to spin</i>`);
  } else if(p==='bowl'){
    showTip(e.clientX, e.clientY, `<b>Snack bowl</b> <i>click to toss food</i>`);
  } else hideTip();
}
function showTip(x,y,html){ tipEl.innerHTML = html; tipEl.style.left = x+'px'; tipEl.style.top = y+'px'; tipEl.classList.add('show'); }
function hideTip(){ tipEl.classList.remove('show'); }

canvas.addEventListener('pointermove', e=>{ if(!downAt) hoverTest(e); });
canvas.addEventListener('pointerleave', ()=>{ hovered=null; hideTip(); });
canvas.addEventListener('pointerdown', e=>{ downAt = {x:e.clientX, y:e.clientY, t:performance.now()}; hideTip(); });
canvas.addEventListener('pointerup', e=>{
  if(!downAt) return;
  const moved = Math.hypot(e.clientX-downAt.x, e.clientY-downAt.y);
  const quick = performance.now()-downAt.t < 450;
  downAt = null; lastInput = performance.now();
  if(moved>6 || !quick) return;
  pointerNdc(e); ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(pickables(), true)[0];
  const p = hit ? findPick(hit.object) : null;
  if(typeof p === 'object') boop(p);
  else if(p==='wheel'){ wheelVel -= 7.5; beep(300,.12,'sine',.06); toast('Wheee!'); }
  else if(p==='bowl') tossFood(4);
});

function boop(h){
  if(h.state==='riding') rider = null;
  h.state='boop'; h.t=0; h.hop=.001; boops++;
  hearts(h.pos); beep(680,.09,'sine',.06); setTimeout(()=>beep(920,.07,'sine',.045),80);
}

/* ══════════════════ HUD wiring ══════════════════ */
let snacks = 0, boops = 0, night = 0, nightTarget = 0;
const listEl = document.getElementById('resList'), badgeEl = document.getElementById('popBadge');
const sRpm = document.getElementById('sRpm'), sSnack = document.getElementById('sSnack'),
      sBoop = document.getElementById('sBoop'), sClock = document.getElementById('sClock');
const toastEl = document.getElementById('toast');
let toastTimer;
function toast(msg){
  toastEl.textContent = msg; toastEl.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(()=>toastEl.classList.remove('show'), 2000);
}
function bump(el,v){ if(el.textContent!==String(v)){ el.textContent=v; el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); } }
function updateBadge(){ badgeEl.textContent = hamsters.length+'/'+MAX_H; }

function buildRow(h){
  const li = document.createElement('li');
  li.className='res'; li.dataset.id = h.id;
  li.innerHTML = `<span class="sw" style="--c:${h.color}"></span>
    <span><b>${h.name}</b><em>${h.mood}</em></span>
    <span class="st">waking up</span><span class="bar"><i style="width:0%"></i></span>`;
  li.addEventListener('pointerenter', ()=>{ h.flagged = true; });
  li.addEventListener('pointerleave', ()=>{ h.flagged = false; });
  li.addEventListener('click', ()=>{
    focusId = focusId===h.id ? null : h.id;
    [...listEl.children].forEach(c=>c.classList.toggle('on', +c.dataset.id===focusId));
    toast(focusId===h.id ? `Following ${h.name}` : 'Camera released');
  });
  listEl.appendChild(li);
  h.ui = {li, st: li.querySelector('.st'), bar: li.querySelector('.bar i')};
}

document.querySelectorAll('.b').forEach(b=>b.addEventListener('click', ()=>{
  const a = b.dataset.act;
  if(a==='food') tossFood(4);
  if(a==='wheel'){ wheelVel -= 7.5; toast('Wheee!'); beep(300,.12,'sine',.06); }
  if(a==='night'){ nightTarget = nightTarget>.5?0:1; b.classList.toggle('on', nightTarget>.5);
    b.innerHTML = nightTarget>.5 ? '☀️ Lights on <kbd>L</kbd>' : '🌙 Lights out <kbd>L</kbd>';
    document.body.classList.toggle('night', nightTarget>.5);
    toast(nightTarget>.5?'Night mode — the hamsters disagree':'Morning!'); }
  if(a==='add'){ const h = addHamster(); if(h) toast(`${h.name} the ${h.mood} has moved in`); }
  if(a==='reset'){ focusId=null; [...listEl.children].forEach(c=>c.classList.remove('on'));
    introT = 0; introFrom = camera.position.clone(); introFromT = controls.target.clone(); introRun = true; controls.enabled=false;
    toast('View reset'); }
  if(a==='sound'){ audioOn = !audioOn; b.classList.toggle('on', audioOn); b.innerHTML = (audioOn?'🔊 Sound':'🔇 Sound')+' <kbd>S</kbd>';
    if(audioOn) beep(660,.08,'triangle',.05); }
  lastInput = performance.now();
}));
addEventListener('keydown', e=>{
  const k = e.key.toLowerCase();
  const map = {f:'food', w:'wheel', l:'night', n:'add', r:'reset', s:'sound'};
  if(map[k]){ document.querySelector(`.b[data-act="${map[k]}"]`).click(); }
  if(e.key==='Escape'){ focusId=null; [...listEl.children].forEach(c=>c.classList.remove('on')); }
});

/* ---------- tiny synth ---------- */
let audioCtx = null, audioOn = false;
function beep(freq, dur, type='sine', gain=.05){
  if(!audioOn) return;
  audioCtx = audioCtx || new (window.AudioContext||window.webkitAudioContext)();
  const o = audioCtx.createOscillator(), g = audioCtx.createGain();
  o.type = type; o.frequency.value = freq;
  g.gain.setValueAtTime(gain, audioCtx.currentTime);
  g.gain.exponentialRampToValueAtTime(.0001, audioCtx.currentTime+dur);
  o.connect(g).connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime+dur);
}

/* ══════════════════ boot ══════════════════ */
for(let i=0;i<6;i++) addHamster();
tossFood(3);

let introRun = !REDUCED, introT = 0;
let introFrom = camera.position.clone(), introFromT = controls.target.clone();
let lastInput = performance.now(), lastUI = 0, clockStart = performance.now();
const loader = document.getElementById('loader');

addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
controls.addEventListener('start', ()=>{ lastInput = performance.now(); introRun = false; controls.enabled = true; });
canvas.addEventListener('wheel', ()=>{ lastInput = performance.now(); }, {passive:true});

const camTmp = new THREE.Vector3();
let firstFrame = true;

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), .05), t = clock.elapsedTime;

  /* intro / focus camera */
  if(introRun){
    introT += dt/2.1;
    const k = Math.min(1, introT), e = k<.5 ? 4*k*k*k : 1-Math.pow(-2*k+2,3)/2;
    camera.position.lerpVectors(introFrom, HOME_POS, e);
    controls.target.lerpVectors(introFromT, HOME_TGT, e);
    if(k>=1){ introRun=false; controls.enabled = true; }
  } else if(focusId!==null && hamsters[focusId]){
    const h = hamsters[focusId];
    camTmp.set(h.pos.x, .55, h.pos.z);
    controls.target.lerp(camTmp, 1-Math.pow(.001, dt));
  }
  controls.autoRotate = !REDUCED && focusId===null && !introRun && (performance.now()-lastInput > 6500);
  controls.update();

  /* night blend */
  night = damp(night, nightTarget, 2.2, dt);
  key.intensity  = THREE.MathUtils.lerp(2.35,.42,night);
  hemi.intensity = THREE.MathUtils.lerp(.8,.3,night);
  fill.intensity = THREE.MathUtils.lerp(.55,.2,night);
  lamp.intensity = night*16*(1+Math.sin(t*7.3)*.03);
  scene.backgroundIntensity = THREE.MathUtils.lerp(1,.34,night);
  scene.fog.color.setHex(0xffd9b0).lerp(new THREE.Color(0x1a2148), night);

  /* wheel physics */
  if(!rider) wheelVel *= Math.pow(.55, dt);
  if(Math.abs(wheelVel)<.005) wheelVel = 0;
  wheelSpin.rotation.z += wheelVel*dt;

  /* hamsters */
  hamsters.forEach(h=>updateHamster(h, dt, t));
  separate();
  updatePellets(dt);
  updateParticles(dt);

  /* highlight ring follows hovered / focused hamster */
  const target = (hovered && typeof hovered==='object') ? hovered : (focusId!==null ? hamsters[focusId] : null);
  if(target){
    ring.visible = true;
    ring.position.set(target.pos.x, .09, target.pos.z);
    ring.rotation.z += dt*1.4;
    ring.material.color.setHex(hovered===target ? 0xff6a4d : 0xffc247);
    const s = (.8+target.size*.5)*(1+Math.sin(t*4)*.03);
    ring.scale.setScalar(s);
  } else ring.visible = false;

  /* HUD */
  const now = performance.now();
  if(now-lastUI > 120){
    lastUI = now;
    bump(sRpm, Math.round(Math.abs(wheelVel)*60/6.283));
    bump(sSnack, snacks); bump(sBoop, boops);
    const mins = Math.floor(((now-clockStart)/1000*45 + 12*60) % 1440);
    sClock.textContent = String(Math.floor(mins/60)).padStart(2,'0')+':'+String(mins%60).padStart(2,'0');
    hamsters.forEach(h=>{
      if(!h.ui) return;
      const label = h.state==='nap' ? (night>.5?'nocturnal nap':'curled up')
                : h.state==='pause' ? (LABEL[h.sub]||'sniffing around')
                : LABEL[h.state] || 'exploring';
      if(h.ui.st.textContent!==label) h.ui.st.textContent = label;
      const dur = h.dur || 4;
      h.ui.bar.style.width = clamp(h.t/dur,0,1)*100 + '%';
      h.ui.bar.style.background = h.state==='zoomies' ? '#ffc247' : h.state==='nap' ? '#6b3357' : h.state==='riding' ? '#2ecaa6' : '#ff6a4d';
    });
  }

  renderer.render(scene, camera);

  if(firstFrame){
    firstFrame = false;
    loader.classList.add('gone');
    document.body.classList.add('ready');
    setTimeout(()=>loader.remove(), 800);
  }
}
const clock = new THREE.Clock();
animate();
</script>
</body>
</html>
```

**What's in the box**

- **Habitat:** sand tray with instanced bedding pellets, mint plastic tunnel, open-front wooden hut, nest ring, snack bowl, water bottle on the bars, and a full bar cage with corner posts, lid rails and a carry handle — all flat-shaded primitives.
- **The wheel** is the interactive centrepiece: it has real angular velocity, a hamster climbs in and runs it up to ~50 rpm, and clicking it (or pressing `W`) gives it an impulse that coasts down.
- **Autonomous hamsters** run a weighted mood FSM — `explore / sniff / groom / watch-you / ride-wheel / snack / tunnel / ZOOMIES / curl-up` — with leg gaits, body bob, blink timers, puffing cheeks while nibbling, and separation so they don't merge into one hamster blob.
- **Living feedback:** hover a resident to flag it with a spinning ring, click to make the camera follow; hover the 3D hamsters for name/mood tags; boop them for hearts; toss food and hungry ones change their plans mid-walk.
- **Night mode** dims the sky texture, warms a caged lamp, and nudges the mood weights toward napping (with floating `z`'s).