# Low-Poly Hamster Playground

A single-file Three.js diorama: 8 faceted hamsters, a wire cage, a spinning wheel, a see-through tunnel arch, a food bowl with scatterable seeds, and a little hut for nap time. Drag to orbit, click a hamster to boop it, hover the resident list to spotlight someone.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Low-Poly Hamster Playground — Cage 07</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#2A1E17;
    --ink-soft:rgba(42,30,23,.62);
    --paper:#FFF8EC;
    --paper-2:#FFEFDA;
    --tangerine:#FF7A3D;
    --mint:#2FBE9E;
    --sky:#4FA9E8;
    --sun:#FFC53D;
    --berry:#E8506E;
    --line:2.5px solid var(--ink);
    --pop:0 4px 0 rgba(42,30,23,.92), 0 14px 26px rgba(42,30,23,.18);
    --pop-sm:0 3px 0 rgba(42,30,23,.92), 0 8px 18px rgba(42,30,23,.14);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0; overflow:hidden; color:var(--ink);
    font-family:'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
    background:#F0DFC4;
    -webkit-font-smoothing:antialiased;
  }

  /* ---------- ambient layered backdrop ---------- */
  #bg{position:fixed; inset:0; z-index:0; transition:background 1.1s ease;
    background:
      radial-gradient(130% 78% at 50% 112%, #FFE9C4 0%, rgba(255,233,196,0) 62%),
      radial-gradient(70% 45% at 12% 4%, #FFF6DE 0%, rgba(255,246,222,0) 70%),
      linear-gradient(#B9E2F0 0%, #DCEFE3 40%, #F6E4C2 100%);
  }
  #bg::before{
    content:''; position:absolute; inset:-30%;
    background:repeating-linear-gradient(-16deg, rgba(255,255,255,.5) 0 2px, rgba(255,255,255,0) 2px 46px);
    opacity:.34; animation:beams 26s linear infinite;
  }
  #bg::after{
    content:''; position:absolute; inset:-20%;
    background-image:radial-gradient(rgba(42,30,23,.16) 1.2px, transparent 1.3px);
    background-size:26px 26px; opacity:.55;
    -webkit-mask-image:radial-gradient(72% 62% at 50% 46%, transparent 26%, #000 100%);
            mask-image:radial-gradient(72% 62% at 50% 46%, transparent 26%, #000 100%);
    animation:drift 44s linear infinite;
  }
  @keyframes beams{to{transform:translateX(92px)}}
  @keyframes drift{to{transform:translate(26px,26px)}}
  body.dusk #bg{
    background:
      radial-gradient(130% 78% at 50% 112%, #FFCB90 0%, rgba(255,203,144,0) 58%),
      radial-gradient(60% 40% at 82% 10%, #FFE3B6 0%, rgba(255,227,182,0) 72%),
      linear-gradient(#26325C 0%, #6A5583 48%, #C4886A 100%);
  }
  #scene{position:fixed; inset:0; width:100%; height:100%; z-index:1; display:block; touch-action:none; cursor:grab}
  #scene.dragging{cursor:grabbing}
  .vignette{position:fixed; inset:0; z-index:2; pointer-events:none;
    box-shadow:inset 0 -140px 180px -90px rgba(63,38,15,.34), inset 0 120px 160px -110px rgba(255,255,255,.5);}
  body.dusk .vignette{box-shadow:inset 0 -160px 200px -80px rgba(18,12,40,.55), inset 0 120px 160px -120px rgba(255,203,144,.25)}

  /* ---------- HUD shell ---------- */
  .hud{position:fixed; inset:0; z-index:5; pointer-events:none}
  .hud > *{pointer-events:auto}
  .card{
    background:var(--paper); border:var(--line); border-radius:16px;
    box-shadow:var(--pop-sm);
    opacity:0; transform:translateY(14px) scale(.985);
    animation:rise .7s cubic-bezier(.2,.9,.28,1.2) forwards; animation-delay:var(--d,0s);
  }
  @keyframes rise{to{opacity:1; transform:none}}

  /* ---------- plaque / title ---------- */
  .plaque{position:absolute; left:24px; top:22px; padding:14px 20px 15px; transform:rotate(-1.6deg);}
  .plaque{animation-name:riseRotate}
  @keyframes riseRotate{to{opacity:1; transform:rotate(-1.6deg)}}
  .kicker{display:flex; align-items:center; gap:8px; font-size:.62rem; letter-spacing:.24em; text-transform:uppercase; font-weight:700; color:var(--ink-soft)}
  .kicker .dot{width:8px;height:8px;border-radius:50%;background:var(--tangerine);box-shadow:0 0 0 2px var(--ink);animation:blip 1.8s ease-in-out infinite}
  @keyframes blip{50%{background:var(--mint)}}
  h1{
    font-family:'Baloo 2', cursive; font-weight:800; margin:.06em 0 0;
    font-size:clamp(1.9rem, 3.6vw, 3.15rem); line-height:.86; letter-spacing:-.02em;
  }
  h1 em{font-style:normal; color:var(--tangerine); -webkit-text-stroke:1.4px var(--ink); text-stroke:1.4px var(--ink)}
  h1 span{display:block; font-size:.38em; letter-spacing:.26em; font-weight:700; color:var(--ink-soft); margin-top:.5em}
  .meta{display:flex; gap:6px; margin-top:11px; flex-wrap:wrap}
  .tag{font-size:.6rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; padding:3px 8px; border:2px solid var(--ink); border-radius:99px; background:var(--paper-2)}

  /* ---------- residents ---------- */
  .census{position:absolute; right:24px; top:22px; width:280px; display:flex; flex-direction:column; max-height:min(58vh, 560px); padding:12px 12px 10px}
  .census h2{font-family:'Baloo 2',cursive; font-size:.95rem; margin:2px 4px 8px; letter-spacing:.06em; text-transform:uppercase; display:flex; justify-content:space-between; align-items:center}
  .census h2 b{background:var(--ink); color:var(--paper); font-size:.7rem; padding:2px 8px; border-radius:99px; letter-spacing:.1em}
  .list{list-style:none; margin:0; padding:0 2px 0 0; overflow:auto; scrollbar-width:thin}
  .res{display:grid; grid-template-columns:14px 1fr auto 20px; align-items:center; gap:9px;
    padding:7px 8px; border-radius:11px; cursor:pointer; transition:background .18s, transform .18s cubic-bezier(.2,.9,.3,1.4);}
  .res + .res{margin-top:2px}
  .res:hover{background:var(--paper-2); transform:translateX(-4px)}
  .res.on{background:#FFE7C4; box-shadow:inset 0 0 0 2px var(--ink)}
  .chip{width:14px;height:14px;border-radius:5px;background:var(--c);border:2px solid var(--ink); box-shadow:1.5px 1.5px 0 rgba(42,30,23,.35)}
  .nm{font-family:'Baloo 2',cursive; font-weight:700; font-size:.98rem; line-height:1; display:flex; flex-direction:column; gap:2px}
  .nm small{font-family:'Space Grotesk',sans-serif; font-weight:500; font-size:.55rem; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-soft)}
  .st{font-size:.62rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; padding:3px 7px; border-radius:99px; white-space:nowrap; border:2px solid currentColor}
  .st[data-s="idle"]{color:#8B7B63} .st[data-s="walk"]{color:#1E9A7E} .st[data-s="eat"]{color:#C46A16}
  .st[data-s="run"]{color:var(--berry)} .st[data-s="drink"]{color:#2C86C4} .st[data-s="tube"]{color:#B0562F}
  .st[data-s="sleep"]{color:#6A5FA3} .st[data-s="boop"]{color:var(--tangerine)} .st[data-s="move"]{color:#8B7B63}
  .st.runpulse{animation:pulse 1s ease-in-out infinite}
  @keyframes pulse{50%{transform:scale(1.07)}}
  .go{opacity:0; font-size:.8rem; text-align:center; transition:opacity .18s}
  .res:hover .go, .res.on .go{opacity:1}
  .newrow{animation:rowIn .5s cubic-bezier(.2,.9,.3,1.5) both}
  @keyframes rowIn{from{opacity:0; transform:translateX(24px) rotate(3deg)}}

  /* ---------- dock ---------- */
  .dock{position:absolute; left:50%; bottom:22px; transform:translateX(-50%); padding:11px 12px; display:flex; gap:9px; align-items:center; flex-wrap:wrap; justify-content:center; max-width:min(92vw, 780px)}
  .dock{animation-name:riseCenter}
  @keyframes riseCenter{to{opacity:1; transform:translateX(-50%)}}
  .btn{font-family:'Baloo 2',cursive; font-weight:700; font-size:.86rem; color:var(--ink);
    display:inline-flex; align-items:center; gap:7px; padding:7px 12px 7px 8px;
    background:var(--paper); border:2.5px solid var(--ink); border-radius:13px; cursor:pointer;
    box-shadow:var(--pop-sm); transition:transform .14s cubic-bezier(.2,.9,.3,1.5), box-shadow .14s, background .2s;}
  .btn:hover{transform:translate(-2px,-3px); box-shadow:0 7px 0 rgba(42,30,23,.92), 0 14px 22px rgba(42,30,23,.2); background:#fff}
  .btn:active{transform:translate(1px,3px); box-shadow:0 0 0 rgba(42,30,23,.92)}
  .btn .g{width:22px;height:22px; display:grid; place-items:center; border-radius:7px; border:2px solid var(--ink); font-size:.8rem; line-height:1; background:var(--gc,var(--sun))}
  .btn[aria-pressed="true"]{background:var(--sun)}
  .btn:disabled{opacity:.45; cursor:not-allowed; transform:none; box-shadow:var(--pop-sm)}
  .sep{width:2px; align-self:stretch; background:repeating-linear-gradient(var(--ink) 0 4px, transparent 4px 8px); opacity:.35; margin:0 2px}
  .speed{display:flex; align-items:center; gap:8px; padding:0 6px; font-size:.6rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-soft)}
  input[type=range]{-webkit-appearance:none; appearance:none; width:88px; height:22px; background:transparent; cursor:pointer}
  input[type=range]::-webkit-slider-runnable-track{height:8px; background:var(--paper-2); border:2px solid var(--ink); border-radius:99px}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none; width:16px;height:16px;margin-top:-6px; border-radius:50%; background:var(--tangerine); border:2px solid var(--ink); box-shadow:1px 1px 0 rgba(42,30,23,.6)}
  input[type=range]::-moz-range-track{height:8px; background:var(--paper-2); border:2px solid var(--ink); border-radius:99px}
  input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:50%; background:var(--tangerine); border:2px solid var(--ink)}

  /* ---------- meters + keys ---------- */
  .meters{position:absolute; right:24px; bottom:22px; width:236px; padding:12px 14px 13px}
  .mrow{display:flex; justify-content:space-between; align-items:baseline; font-size:.6rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-soft)}
  .big{font-family:'Baloo 2',cursive; font-weight:800; font-size:2.15rem; line-height:.9; letter-spacing:-.02em}
  .big i{font-style:normal; font-size:.42em; color:var(--ink-soft); margin-left:3px}
  .bar{height:11px; border:2px solid var(--ink); border-radius:99px; background:var(--paper-2); overflow:hidden; margin:6px 0 12px}
  .bar i{display:block; height:100%; width:0%; background:repeating-linear-gradient(-45deg, var(--berry) 0 7px, #FF7E97 7px 14px); transition:width .18s linear}
  .bar.mint i{background:repeating-linear-gradient(-45deg, var(--mint) 0 7px, #6FE0C4 7px 14px)}
  .tiny{font-size:.58rem; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-soft); font-weight:700}
  .keys{position:absolute; left:24px; bottom:24px; padding:10px 13px; max-width:250px; line-height:1.9}
  .keys b{font-family:'Space Grotesk'; font-size:.6rem; background:var(--paper-2); border:2px solid var(--ink); border-radius:6px; padding:1px 5px; margin-right:5px}
  .keys p{margin:0; font-size:.63rem; letter-spacing:.04em; color:var(--ink-soft)}

  /* ---------- squeak bubble ---------- */
  .bubble{position:fixed; z-index:7; transform:translate(-50%,-115%) scale(.6); opacity:0; pointer-events:none;
    background:var(--paper); border:2.5px solid var(--ink); border-radius:12px; padding:3px 9px;
    font-family:'Baloo 2',cursive; font-weight:800; font-size:.8rem; white-space:nowrap; box-shadow:var(--pop-sm);
    transition:opacity .16s, transform .28s cubic-bezier(.2,.9,.3,1.6)}
  .bubble.show{opacity:1; transform:translate(-50%,-135%) scale(1)}
  .bubble::after{content:''; position:absolute; left:50%; bottom:-7px; width:10px;height:10px; background:var(--paper); border-right:2.5px solid var(--ink); border-bottom:2.5px solid var(--ink); transform:translateX(-50%) rotate(45deg)}

  /* ---------- boot ---------- */
  #boot{position:fixed; inset:0; z-index:20; display:grid; place-items:center; background:#F6E7CC; transition:opacity .6s ease, visibility .6s}
  #boot.gone{opacity:0; visibility:hidden}
  .bootin{text-align:center}
  .wheel-svg{width:96px;height:96px; animation:spin 1.5s linear infinite; margin-bottom:14px}
  @keyframes spin{to{transform:rotate(360deg)}}
  .bootin h3{font-family:'Baloo 2',cursive; font-weight:800; font-size:1.3rem; margin:0}
  .bootin p{font-size:.62rem; letter-spacing:.24em; text-transform:uppercase; color:var(--ink-soft); margin:6px 0 0}

  @media (max-width:1080px){ .keys{display:none} }
  @media (max-width:900px){
    .plaque{left:14px; top:14px; padding:10px 14px}
    .census{right:14px; top:14px; width:210px; max-height:44vh}
    .meters{display:none}
    .dock{bottom:14px; gap:7px; padding:8px}
    .btn{font-size:.78rem; padding:6px 9px 6px 6px}
    .speed{display:none}
  }
  @media (prefers-reduced-motion:reduce){ *{animation-duration:.01ms !important; transition-duration:.01ms !important} }
</style>
</head>
<body>
<div id="bg"></div>
<canvas id="scene"></canvas>
<div class="vignette"></div>

<div class="hud">
  <header class="plaque card" style="--d:.05s">
    <div class="kicker"><span class="dot"></span> Field enclosure 07 · live feed</div>
    <h1>Hamster <em>Play</em>ground<span>Low-poly · 8 residents</span></h1>
    <div class="meta">
      <span class="tag">drag to orbit</span><span class="tag">click to boop</span><span class="tag">scroll to zoom</span>
    </div>
  </header>

  <aside class="census card" style="--d:.18s">
    <h2>Residents <b id="popCount">0/8</b></h2>
    <ul class="list" id="resList"></ul>
  </aside>

  <div class="dock card" style="--d:.3s">
    <button class="btn" id="bSeeds"><span class="g" style="--gc:var(--sun)">✿</span>Scatter seeds</button>
    <button class="btn" id="bWheel"><span class="g" style="--gc:var(--berry)">◍</span>Shove wheel</button>
    <button class="btn" id="bAdd"><span class="g" style="--gc:var(--mint)">+</span>New hamster</button>
    <div class="sep"></div>
    <button class="btn" id="bLamp" aria-pressed="false"><span class="g" style="--gc:var(--sky)">☾</span>Lamp</button>
    <button class="btn" id="bOrbit" aria-pressed="true"><span class="g" style="--gc:#D9CFBE">↻</span>Orbit</button>
    <button class="btn" id="bPause" aria-pressed="false"><span class="g" style="--gc:#D9CFBE">‖</span>Pause</button>
    <button class="btn" id="bView"><span class="g" style="--gc:var(--tangerine)">⌂</span>View</button>
    <div class="sep"></div>
    <label class="speed">Zoomies <input type="range" id="rSpeed" min="0.25" max="2.2" step="0.05" value="1"><span id="spdVal">1.0×</span></label>
  </div>

  <div class="meters card" style="--d:.42s">
    <div class="mrow"><span>Wheel speed</span><span id="fps">— fps</span></div>
    <div class="big"><span id="rpm">0</span><i>rpm</i></div>
    <div class="bar"><i id="rpmBar"></i></div>
    <div class="mrow"><span>Seeds in tray</span><span id="seedN">0</span></div>
    <div class="bar mint"><i id="seedBar"></i></div>
    <p class="tiny" id="mood">Mood: mildly chaotic</p>
  </div>

  <div class="keys card" style="--d:.54s">
    <p><b>S</b>seeds <b>W</b>wheel <b>A</b>add hamster</p>
    <p><b>L</b>lamp <b>O</b>orbit <b>Space</b>pause</p>
    <p><b>1–8</b>follow a hamster <b>Esc</b>free cam</p>
  </div>
</div>

<div class="bubble" id="bubble"></div>

<div id="boot">
  <div class="bootin">
    <svg class="wheel-svg" viewBox="0 0 100 100" fill="none" stroke="#2A1E17" stroke-width="5" stroke-linecap="round">
      <circle cx="50" cy="50" r="38"/><circle cx="50" cy="50" r="6" fill="#FF7A3D"/>
      <path d="M50 12v32M50 56v32M12 50h32M56 50h32M23 23l23 23M54 54l23 23M77 23L54 46M46 54L23 77"/>
    </svg>
    <h3>Warming up the wheel…</h3>
    <p id="bootMsg">assembling 8 hamsters</p>
  </div>
</div>

<script>
  window.__HP_BOOTED = false;
  setTimeout(function(){
    if(!window.__HP_BOOTED){
      document.getElementById('bootMsg').textContent = 'could not load three.js — check your connection';
    }
  }, 9000);
</script>

<script type="importmap">
{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js" } }
</script>

<script type="module">
import * as THREE from 'three';

/* ============================================================
   0 · tiny utils
   ============================================================ */
const rnd = (a,b)=> a + Math.random()*(b-a);
const irnd = (a,b)=> Math.floor(rnd(a,b+1));
const pick = a => a[Math.floor(Math.random()*a.length)];
const clamp = THREE.MathUtils.clamp;
const damp  = THREE.MathUtils.damp;
const wrap  = a => { while(a> Math.PI) a-=Math.PI*2; while(a<-Math.PI) a+=Math.PI*2; return a; };
const $ = id => document.getElementById(id);

/* ============================================================
   1 · renderer, scene, camera rig
   ============================================================ */
const canvas = $('scene');
let renderer;
try{
  renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true, powerPreference:'high-performance'});
}catch(err){
  document.getElementById('bootMsg').textContent = 'WebGL unavailable on this device';
  throw err;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight, false);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xF7E7C8, 34, 86);

const camera = new THREE.PerspectiveCamera(40, innerWidth/innerHeight, 0.1, 220);

const view = {
  theta:0.95, phi:1.10, dist:27,
  tTheta:0.95, tPhi:1.10, tDist:27,
  target:new THREE.Vector3(0,2.6,0),
  tTarget:new THREE.Vector3(0,2.6,0)
};
const HOME = { theta:0.95, phi:1.10, dist:27, target:new THREE.Vector3(0,2.6,0) };

/* ============================================================
   2 · lighting + day / lamp themes
   ============================================================ */
const hemi = new THREE.HemisphereLight(0xFFF4DE, 0xD9B183, 1.35);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xFFF2D6, 2.0);
sun.position.set(9, 15, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 46;
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;   sun.shadow.camera.bottom = -12;
sun.shadow.bias = -0.0009;
sun.shadow.normalBias = 0.03;
scene.add(sun, sun.target);

const fill = new THREE.DirectionalLight(0xC7E6FF, 0.55);
fill.position.set(-9, 7, -8);
scene.add(fill);

const lamp = new THREE.PointLight(0xFFC46A, 0, 16, 2);
lamp.position.set(4.2, 3.0, -2.4);
scene.add(lamp);

const THEME = {
  day : { hemiSky:0xFFF4DE, hemiGround:0xD9B183, hemiI:1.35, sunC:0xFFF2D6, sunI:2.0, fillC:0xC7E6FF, fillI:0.55, fog:0xF7E7C8, lamp:0 },
  dusk: { hemiSky:0x93A3DE, hemiGround:0x6B4E6A, hemiI:0.72, sunC:0xFFAE76, sunI:0.85, fillC:0x7189CE, fillI:0.5,  fog:0x7C6B95, lamp:26 }
};
let dusk = false, themeMix = 0;
const _cA = new THREE.Color(), _cB = new THREE.Color();
function lerpTheme(dt){
  const goal = dusk ? 1 : 0;
  themeMix = damp(themeMix, goal, 2.2, dt);
  const a = THEME.day, b = THEME.dusk, m = themeMix;
  hemi.color.set(_cA.copy(_cB.setHex(a.hemiSky)).lerp(_cB.clone().setHex(b.hemiSky), m));
  hemi.groundColor.setHex(a.hemiGround).lerp(_cB.setHex(b.hemiGround), m);
  hemi.intensity = THREE.MathUtils.lerp(a.hemiI, b.hemiI, m);
  sun.color.setHex(a.sunC).lerp(_cB.setHex(b.sunC), m);
  sun.intensity = THREE.MathUtils.lerp(a.sunI, b.sunI, m);
  fill.color.setHex(a.fillC).lerp(_cB.setHex(b.fillC), m);
  fill.intensity = THREE.MathUtils.lerp(a.fillI, b.fillI, m);
  scene.fog.color.setHex(a.fog).lerp(_cB.setHex(b.fog), m);
  lamp.intensity = THREE.MathUtils.lerp(a.lamp, b.lamp, m);
  bulb.material.opacity = 0.25 + lamp.intensity/40;
  glow.material.opacity = lamp.intensity/70;
}

/* ============================================================
   3 · material helper
   ============================================================ */
const mat = (color, o={}) => new THREE.MeshStandardMaterial(Object.assign({color, roughness:.84, metalness:.03, flatShading:true}, o));
const smooth = (color, o={}) => new THREE.MeshStandardMaterial(Object.assign({color, roughness:.35, metalness:.15}, o));

/* ============================================================
   4 · the room: table, tray, cage, bedding
   ============================================================ */
const BX = 6.4, BZ = 4.8;          // bar line
const IN_X = 5.7, IN_Z = 4.1;      // hamster bounds

const table = new THREE.Mesh(new THREE.CylinderGeometry(16, 16, 1.4, 44), mat(0xC99268,{roughness:.9}));
table.position.y = -2.2; table.receiveShadow = true; scene.add(table);
const tableRim = new THREE.Mesh(new THREE.CylinderGeometry(16.15, 16.15, .34, 44), mat(0xB07C53));
tableRim.position.y = -1.55; scene.add(tableRim);

const tray = new THREE.Group(); scene.add(tray);
const trayBody = new THREE.Mesh(new THREE.BoxGeometry(14.6, 1.5, 11.4), mat(0x59C3B0,{roughness:.55}));
trayBody.position.y = -0.75; trayBody.receiveShadow = true; tray.add(trayBody);
const sand = new THREE.Mesh(new THREE.BoxGeometry(13.6, .26, 10.4), mat(0xF0DCB2,{roughness:1}));
sand.position.y = -0.06; sand.receiveShadow = true; tray.add(sand);

// tray lip
const lipGeoX = new THREE.BoxGeometry(14.6,.5,.4), lipGeoZ = new THREE.BoxGeometry(.4,.5,11.4);
[[0,BZ+.2,lipGeoX],[0,-BZ-.2,lipGeoX]].forEach(([x,z,g])=>{
  const m = new THREE.Mesh(g, mat(0x46AE9C,{roughness:.5})); m.position.set(x,.12,z); m.castShadow=m.receiveShadow=true; tray.add(m);
});
[[BX+.2,0,lipGeoZ],[-BX-.2,0,lipGeoZ]].forEach(([x,z,g])=>{
  const m = new THREE.Mesh(g, mat(0x46AE9C,{roughness:.5})); m.position.set(x,.12,z); m.castShadow=m.receiveShadow=true; tray.add(m);
});

// bedding chips (instanced)
const chipCount = 170;
const chip = new THREE.InstancedMesh(new THREE.BoxGeometry(.3,.09,.16), mat(0xE9CE9B,{roughness:1}), chipCount);
chip.receiveShadow = true;
{
  const dummy = new THREE.Object3D(); const col = new THREE.Color();
  for(let i=0;i<chipCount;i++){
    dummy.position.set(rnd(-6.1,6.1), rnd(0.02,.1), rnd(-4.4,4.4));
    dummy.rotation.set(rnd(-.3,.3), rnd(0,Math.PI*2), rnd(-.4,.4));
    dummy.scale.setScalar(rnd(.7,1.5));
    dummy.updateMatrix(); chip.setMatrixAt(i, dummy.matrix);
    chip.setColorAt(i, col.setHSL(rnd(.09,.13), rnd(.35,.6), rnd(.62,.82)));
  }
  chip.instanceColor.needsUpdate = true;
}
scene.add(chip);

// bars
const barMat = smooth(0x8FD8C9,{roughness:.42, metalness:.35});
const barH = 6.6;
function barMesh(r,h){ const m = new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,6), barMat); m.castShadow = true; return m; }
{
  const bars = new THREE.Group();
  const step = .82;
  const nx = Math.floor((BX*2)/step), nz = Math.floor((BZ*2)/step);
  const vGeo = new THREE.CylinderGeometry(.075,.075,barH,6);
  const inst = new THREE.InstancedMesh(vGeo, barMat, (nx+1)*2 + (nz+1)*2 + 4);
  inst.castShadow = true;
  const d = new THREE.Object3D(); let k = 0;
  const put = (x,z)=>{ d.position.set(x, 0.35 + barH/2, z); d.rotation.set(0,0,0); d.scale.set(1,1,1); d.updateMatrix(); inst.setMatrixAt(k++, d.matrix); };
  for(let i=0;i<=nx;i++){ const x = -BX + i*(BX*2/nx); put(x, BZ); put(x,-BZ); }
  for(let i=0;i<=nz;i++){ const z = -BZ + i*(BZ*2/nz); put( BX, z); put(-BX, z); }
  [[BX,BZ],[BX,-BZ],[-BX,BZ],[-BX,-BZ]].forEach(([x,z])=>{
    d.position.set(x, .3 + barH/2, z); d.scale.set(2.1,1,2.1); d.updateMatrix(); inst.setMatrixAt(k++, d.matrix);
  });
  bars.add(inst);

  // rails
  const railX = new THREE.BoxGeometry(BX*2+.5,.17,.17), railZ = new THREE.BoxGeometry(.17,.17,BZ*2+.5);
  [barH+.35, 3.4].forEach(y=>{
    [[0,BZ,railX],[0,-BZ,railX]].forEach(([x,z,g])=>{ const m=new THREE.Mesh(g,barMat); m.position.set(x,y,z); m.castShadow=true; bars.add(m); });
    [[BX,0,railZ],[-BX,0,railZ]].forEach(([x,z,g])=>{ const m=new THREE.Mesh(g,barMat); m.position.set(x,y,z); m.castShadow=true; bars.add(m); });
  });
  // lid bars
  const lidGeo = new THREE.CylinderGeometry(.07,.07,BZ*2+.4,6);
  const lid = new THREE.InstancedMesh(lidGeo, barMat, nx+1);
  lid.castShadow = true;
  for(let i=0;i<=nx;i++){
    d.position.set(-BX + i*(BX*2/nx), barH+.35, 0); d.rotation.set(Math.PI/2,0,0); d.scale.set(1,1,1);
    d.updateMatrix(); lid.setMatrixAt(i, d.matrix);
  }
  bars.add(lid);

  // door frame on the front
  const door = new THREE.Group(); door.position.set(0, 0, BZ);
  const frameMat = smooth(0xFFC53D,{roughness:.4, metalness:.25});
  [[-1.35],[1.35]].forEach(([x])=>{ const m=new THREE.Mesh(new THREE.CylinderGeometry(.13,.13,4.4,8), frameMat); m.position.set(x,2.6,0); m.castShadow=true; door.add(m); });
  [ .5, 4.7 ].forEach(y=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(2.9,.24,.24), frameMat); m.position.set(0,y,0); m.castShadow=true; door.add(m); });
  const knob = new THREE.Mesh(new THREE.SphereGeometry(.2,8,6), mat(0xE8506E,{roughness:.4}));
  knob.position.set(1.15, 2.7, .18); knob.castShadow = true; door.add(knob);
  bars.add(door);
  scene.add(bars);
}

/* floating dust motes */
const motes = (()=>{
  const g = new THREE.BufferGeometry();
  const n = 110, pos = new Float32Array(n*3);
  for(let i=0;i<n;i++){ pos[i*3]=rnd(-13,13); pos[i*3+1]=rnd(.5,11); pos[i*3+2]=rnd(-10,10); }
  g.setAttribute('position', new THREE.BufferAttribute(pos,3));
  const p = new THREE.Points(g, new THREE.PointsMaterial({size:.1, color:0xFFF3D8, transparent:true, opacity:.6, depthWrite:false}));
  scene.add(p); return p;
})();

/* ============================================================
   5 · enrichment objects
   ============================================================ */
// ---- exercise wheel (axis = X) ----
const WHEEL = { x:-4.35, z:-1.3, cy:3.0, R:2.6 };
const wheelGroup = new THREE.Group(); wheelGroup.position.set(WHEEL.x, 0, WHEEL.z); scene.add(wheelGroup);
const wheelSpin = new THREE.Group(); wheelSpin.position.y = WHEEL.cy; wheelGroup.add(wheelSpin);
{
  const orange = mat(0xFF8A4C,{roughness:.5});
  const plateMat = new THREE.MeshStandardMaterial({color:0xFFC79A, roughness:.25, metalness:.05, transparent:true, opacity:.55, flatShading:true, side:THREE.DoubleSide});
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(2.95,2.95,.13,22), plateMat);
  plate.rotation.z = Math.PI/2; plate.position.x = -.55; wheelSpin.add(plate);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(2.95,.17,6,26), orange);
  rim.rotation.y = Math.PI/2; rim.position.x = .55; rim.castShadow = true; wheelSpin.add(rim);
  const rungGeo = new THREE.CylinderGeometry(.1,.1,1.1,6);
  for(let i=0;i<14;i++){
    const a = i/14*Math.PI*2;
    const r = new THREE.Mesh(rungGeo, orange);
    r.rotation.z = Math.PI/2; r.position.set(0, Math.sin(a)*WHEEL.R, Math.cos(a)*WHEEL.R);
    r.castShadow = true; wheelSpin.add(r);
  }
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(.28,.28,1.9,10), smooth(0x5B6B84,{metalness:.5,roughness:.35}));
  hub.rotation.z = Math.PI/2; wheelSpin.add(hub);

  const stand = new THREE.Group(); wheelGroup.add(stand);
  const base = new THREE.Mesh(new THREE.BoxGeometry(2.9,.36,2.0), mat(0x4FA9E8,{roughness:.5}));
  base.position.y = .18; base.castShadow = base.receiveShadow = true; stand.add(base);
  [-1.05, 1.05].forEach(x=>{
    const leg = new THREE.Mesh(new THREE.BoxGeometry(.32, 3.3, .5), mat(0x3E7FBF,{roughness:.5}));
    leg.position.set(x, 1.6, 0); leg.rotation.z = x>0 ? -.09 : .09; leg.castShadow = true; stand.add(leg);
  });
}

// ---- see-through tunnel arch ----
const TUBE = { pos:new THREE.Vector3(0.7,0,3.0), rot:0.24, R:2.3 };
const tubeGroup = new THREE.Group(); tubeGroup.position.copy(TUBE.pos); tubeGroup.rotation.y = TUBE.rot; scene.add(tubeGroup);
{
  const t = new THREE.Mesh(
    new THREE.TorusGeometry(TUBE.R, .95, 7, 20, Math.PI),
    new THREE.MeshStandardMaterial({color:0xFF9F6B, roughness:.2, metalness:.05, transparent:true, opacity:.42, flatShading:true, side:THREE.DoubleSide})
  );
  t.position.y = .12; t.castShadow = false; tubeGroup.add(t);
  const ringGeo = new THREE.TorusGeometry(.98,.08,5,12);
  for(let i=0;i<=6;i++){
    const a = i/6*Math.PI;
    const r = new THREE.Mesh(ringGeo, mat(0xF1793A,{roughness:.45}));
    r.position.set(Math.cos(a)*TUBE.R, Math.sin(a)*TUBE.R + .12, 0);
    r.rotation.y = Math.PI/2; r.rotation.x = 0; r.lookAt(new THREE.Vector3(Math.cos(a)*TUBE.R*2, Math.sin(a)*TUBE.R*2, 0));
    tubeGroup.add(r);
  }
}
const tubeRight = new THREE.Vector3(Math.cos(TUBE.rot), 0, -Math.sin(TUBE.rot));
function tubePoint(t){ // t: 0 → one mouth, 1 → other mouth
  const a = Math.PI * t;
  return new THREE.Vector3(
    TUBE.pos.x + tubeRight.x*Math.cos(a)*TUBE.R,
    Math.sin(a)*TUBE.R + .35,
    TUBE.pos.z + tubeRight.z*Math.cos(a)*TUBE.R
  );
}

// ---- food bowl ----
const BOWL = new THREE.Vector3(4.0, 0, 2.5);
{
  const b = new THREE.Group(); b.position.copy(BOWL); scene.add(b);
  const outer = new THREE.Mesh(new THREE.CylinderGeometry(1.15,.8,.62,10), mat(0x4FA9E8,{roughness:.5}));
  outer.position.y = .31; outer.castShadow = outer.receiveShadow = true; b.add(outer);
  const inner = new THREE.Mesh(new THREE.CylinderGeometry(.95,.72,.2,10), mat(0x2C7CB8,{roughness:.6}));
  inner.position.y = .55; b.add(inner);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(1.12,.1,5,12), mat(0xFFC53D,{roughness:.45}));
  ring.rotation.x = Math.PI/2; ring.position.y = .6; ring.castShadow = true; b.add(ring);
}

// ---- hut (open front) ----
const HUT = { pos:new THREE.Vector3(4.55,0,-3.0), rot:-0.42 };
{
  const h = new THREE.Group(); h.position.copy(HUT.pos); h.rotation.y = HUT.rot; scene.add(h);
  const wall = mat(0xE8506E,{roughness:.7});
  const back = new THREE.Mesh(new THREE.BoxGeometry(2.9,1.9,.24), wall); back.position.set(0,.95,-1.1); 
  const l = new THREE.Mesh(new THREE.BoxGeometry(.24,1.9,2.2), wall); l.position.set(-1.33,.95,0);
  const r = l.clone(); r.position.x = 1.33;
  const floor = new THREE.Mesh(new THREE.BoxGeometry(2.9,.24,2.3), mat(0xC94A63)); floor.position.y=.12;
  [back,l,r,floor].forEach(m=>{ m.castShadow = m.receiveShadow = true; h.add(m); });
  const roof = new THREE.Mesh(new THREE.ConeGeometry(2.35,1.35,4), mat(0xFFC53D,{roughness:.6}));
  roof.position.y = 2.55; roof.rotation.y = Math.PI/4; roof.castShadow = true; h.add(roof);
  const matDoor = new THREE.Mesh(new THREE.CircleGeometry(.7,12), mat(0x3A2A33,{roughness:1}));
  matDoor.position.set(0,.85,-1.2); h.add(matDoor);
  // night bulb + glow near hut
  bulb = new THREE.Mesh(new THREE.SphereGeometry(.24,10,7), new THREE.MeshBasicMaterial({color:0xFFD79A, transparent:true, opacity:.25}));
  bulb.position.set(-1.9, 2.6, .8); h.add(bulb);
  glow = new THREE.Mesh(new THREE.SphereGeometry(.85,12,9), new THREE.MeshBasicMaterial({color:0xFFC46A, transparent:true, opacity:0, blending:THREE.AdditiveBlending, depthWrite:false}));
  glow.position.copy(bulb.position); h.add(glow);
}
var bulb, glow;

// ---- water bottle on the bars ----
const BOTTLE = { pos:new THREE.Vector3(6.15, 0, -0.7), drink:new THREE.Vector3(5.25, 0, -0.7) };
{
  const g = new THREE.Group(); g.position.copy(BOTTLE.pos); scene.add(g);
  const body = new THREE.Mesh(new THREE.CylinderGeometry(.42,.42,2.1,12), new THREE.MeshStandardMaterial({color:0xBFE6FF, roughness:.15, metalness:.1, transparent:true, opacity:.6}));
  body.position.y = 2.5; g.add(body);
  const cap = new THREE.Mesh(new THREE.CylinderGeometry(.3,.44,.4,10), mat(0xE8506E,{roughness:.5}));
  cap.position.y = 3.65; cap.castShadow = true; g.add(cap);
  const spout = new THREE.Mesh(new THREE.CylinderGeometry(.09,.06,.55,8), smooth(0xB9C3CC,{metalness:.8,roughness:.25}));
  spout.rotation.z = Math.PI/2; spout.position.set(-.6,1.6,0); g.add(spout);
  const bead = new THREE.Mesh(new THREE.SphereGeometry(.09,8,6), smooth(0xE8EEF2,{metalness:.9,roughness:.15}));
  bead.position.set(-.9,1.52,0); g.add(bead);
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(.14,.14,.3,8), mat(0x4FA9E8));
  collar.rotation.z = Math.PI/2; collar.position.set(-.35,1.6,0); g.add(collar);
}

// ---- chew toys ----
{
  const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(.62,0), mat(0x2FBE9E,{roughness:.6}));
  ball.position.set(-1.7,.58,-3.1); ball.castShadow = true; scene.add(ball);
  [[-2.6,.42,2.9,0x9B7BE0],[2.9,.4,-1.0,0xFFC53D],[-0.6,.32,-2.2,0xFF8A4C]].forEach(([x,y,z,c],i)=>{
    const b = new THREE.Mesh(new THREE.BoxGeometry(.8,.8,.8), mat(c,{roughness:.7}));
    b.position.set(x,y,z); b.rotation.y = rnd(0,3); b.castShadow = b.receiveShadow = true; scene.add(b);
  });
  const plank = new THREE.Mesh(new THREE.BoxGeometry(2.6,.24,.9), mat(0xD8A76B,{roughness:.9}));
  plank.position.set(1.6,.14,-3.6); plank.rotation.y = .5; plank.castShadow = plank.receiveShadow = true; scene.add(plank);
}

const BLOCKERS = [ {x:HUT.pos.x, z:HUT.pos.z, r:1.9}, {x:WHEEL.x, z:WHEEL.z, r:1.15}, {x:BOWL.x, z:BOWL.z, r:.9} ];

/* ============================================================
   6 · seeds
   ============================================================ */
const seedGeo = new THREE.OctahedronGeometry(.17, 0);
const seeds = [];
function scatterSeeds(n=10){
  for(let i=0;i<n && seeds.length<26;i++){
    const m = new THREE.Mesh(seedGeo, mat(Math.random()<.4 ? 0xFFC53D : 0x5A4632, {roughness:.7}));
    let x=0,z=0,tries=0;
    do{ x = rnd(-5.3,5.3); z = rnd(-3.7,3.7); tries++; }
    while(tries<12 && BLOCKERS.some(b=>Math.hypot(x-b.x,z-b.z) < b.r+.4));
    m.position.set(x,.14,z); m.rotation.set(rnd(0,3),rnd(0,3),rnd(0,3));
    m.castShadow = true; scene.add(m);
    seeds.push({mesh:m, gone:false, born:clock});
  }
}
function nearestSeed(p){
  let best=null, bd=1e9;
  for(const s of seeds){ if(s.gone) continue; const d = Math.hypot(s.mesh.position.x-p.x, s.mesh.position.z-p.z); if(d<bd){bd=d; best=s;} }
  return best;
}

/* ============================================================
   7 · hamsters
   ============================================================ */
const COATS = [
  {label:'golden',   body:0xF2B84B, belly:0xFFEAC2, patch:0xE0932A},
  {label:'cream',    body:0xFBE3C0, belly:0xFFF8EE, patch:0xEECB9C},
  {label:'cinnamon', body:0xC9793F, belly:0xFFE2C4, patch:0xA65A28},
  {label:'dwarf grey',body:0x9AA3AE,belly:0xEAF0F5, patch:0x767F8C},
  {label:'panda',    body:0xFDF6EC, belly:0xFFFFFF, patch:0x3A3238},
  {label:'chocolate',body:0x7A5237, belly:0xD9B18C, patch:0x503121},
  {label:'honey',    body:0xFFD277, belly:0xFFF4DC, patch:0xF0A93F},
  {label:'slate',    body:0x7C8AA0, belly:0xE3EAF2, patch:0x5A6577}
];
const NAMES = ['Nacho','Waffles','Biscuit','Mochi','Pickle','Nugget','Toots','Branston','Dumpling','Sprout','Gizmo','Pudding'];
const STANCE = .72;
const MAX_HAMSTERS = 8;

const hamsters = [];
let usedNames = [], usedCoats = [], idc = 0;
let wheelUser = -1, hutUser = -1;

const heartGeo = (()=>{
  const s = new THREE.Shape();
  s.moveTo(0,-.34);
  s.bezierCurveTo(-.58,.1,-.3,.56,0,.27);
  s.bezierCurveTo(.3,.56,.58,.1,0,-.34);
  const g = new THREE.ExtrudeGeometry(s,{depth:.14, bevelEnabled:false, curveSegments:6});
  g.center(); return g;
})();

function makeHamster(){
  const id = ++idc;
  const coat = COATS.find((c,i)=>!usedCoats.includes(i)) !== undefined
    ? COATS[COATS.map((_,i)=>i).filter(i=>!usedCoats.includes(i))[0] % COATS.length]
    : pick(COATS);
  usedCoats.push(COATS.indexOf(coat));
  const freeName = NAMES.find(n=>!usedNames.includes(n));
  const name = freeName || ('Hamster ' + id); usedNames.push(name);

  const g = new THREE.Group();
  const tilt = new THREE.Group(); g.add(tilt);
  const rig  = new THREE.Group(); tilt.add(rig);

  const torso = new THREE.Group(); torso.scale.set(1.12,.95,1.18); rig.add(torso);
  const body = new THREE.Mesh(new THREE.SphereGeometry(.62,10,7), mat(coat.body)); torso.add(body);
  const backPatch = new THREE.Mesh(new THREE.SphereGeometry(.635,10,7,0,Math.PI*2,0,Math.PI*.38), mat(coat.patch)); torso.add(backPatch);
  const bellyPatch = new THREE.Mesh(new THREE.SphereGeometry(.635,10,7,0,Math.PI*2,Math.PI*.58,Math.PI*.42), mat(coat.belly)); torso.add(bellyPatch);

  const tail = new THREE.Mesh(new THREE.ConeGeometry(.1,.28,5), mat(coat.patch));
  tail.position.set(0,.2,-.74); tail.rotation.x = -2.3; rig.add(tail);

  const head = new THREE.Group(); head.position.set(0,.3,.6); rig.add(head);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(.4,10,7), mat(coat.body)); skull.scale.set(1,.95,.96); head.add(skull);
  const snout = new THREE.Mesh(new THREE.SphereGeometry(.2,8,5), mat(coat.belly)); snout.scale.set(.85,.72,1.1); snout.position.set(0,-.04,.33); head.add(snout);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(.062,6,5), mat(0xE98A9A,{roughness:.4})); nose.position.set(0,.01,.54); head.add(nose);

  const eyeMat = new THREE.MeshStandardMaterial({color:0x241B22, roughness:.2, metalness:.1});
  const eyes = [-1,1].map(s=>{
    const e = new THREE.Mesh(new THREE.SphereGeometry(.078,8,6), eyeMat);
    e.position.set(.2*s,.1,.32); head.add(e);
    const spark = new THREE.Mesh(new THREE.SphereGeometry(.024,6,4), new THREE.MeshBasicMaterial({color:0xFFFFFF}));
    spark.position.set(.03,-.02,.06); e.add(spark); return e;
  });
  const cheeks = [-1,1].map(s=>{
    const c = new THREE.Mesh(new THREE.SphereGeometry(.19,8,6), mat(coat.belly,{roughness:.9}));
    c.position.set(.25*s,-.03,.2); head.add(c); return c;
  });
  const ears = [-1,1].map(s=>{
    const e = new THREE.Group(); e.position.set(.27*s,.33,.05); e.rotation.z = -.4*s; head.add(e);
    const outer = new THREE.Mesh(new THREE.SphereGeometry(.15,7,5), mat(coat.body)); outer.scale.set(1,1,.42); e.add(outer);
    const innerM = new THREE.Mesh(new THREE.SphereGeometry(.1,7,5), mat(0xF3B9BC)); innerM.scale.set(1,1,.4); innerM.position.z=.05; e.add(innerM);
    return e;
  });

  const legs = [];
  const legGeo = new THREE.CylinderGeometry(.085,.07,.3,6);
  [[-.31,-.42,.4],[.31,-.42,.4],[-.31,-.42,-.42],[.31,-.42,-.42]].forEach(([x,y,z],i)=>{
    const L = new THREE.Group(); L.position.set(x,y,z); rig.add(L);
    const m = new THREE.Mesh(legGeo, mat(i<2 ? coat.body : coat.patch));
    m.position.y = -.15; L.add(m);
    const paw = new THREE.Mesh(new THREE.SphereGeometry(.075,6,4), mat(0xF6CDBE)); paw.position.y=-.3; L.add(paw);
    legs.push(L);
  });

  const ring = new THREE.Mesh(new THREE.RingGeometry(.85,1.06,26),
    new THREE.MeshBasicMaterial({color:0xFF7A3D, transparent:true, opacity:.85, side:THREE.DoubleSide, depthWrite:false}));
  ring.rotation.x = -Math.PI/2; ring.position.y = -STANCE + .04; ring.visible = false; g.add(ring);

  g.traverse(o=>{ if(o.isMesh){ o.castShadow = true; } });
  g.position.set(rnd(-4,4), STANCE, rnd(-3,3));
  scene.add(g);

  const h = {
    id, name, coat, group:g, tilt, rig, torso, head, eyes, cheeks, ears, legs, tail, ring,
    state:'idle', t:0, timer:rnd(.5,2), sub:pick(['look','groom','stretch']),
    heading:rnd(0,Math.PI*2), turn:rnd(2.6,3.6), maxSpeed:rnd(1.5,2.15), speedNow:0,
    phase:rnd(0,10), target:new THREE.Vector3(), purpose:'wander', seed:null, lerp:null,
    hopT:-1, scaleGoal:1, bobAmt:.05, chew:0, sleepFace:false, rowEl:null
  };
  g.userData.hamster = h;
  hamsters.push(h);
  addRow(h);
  return h;
}

/* ============================================================
   8 · behaviour brain
   ============================================================ */
function release(h){
  if(wheelUser === h.id) wheelUser = -1;
  if(hutUser === h.id) hutUser = -1;
}
function setState(h, s, dur){ h.state = s; h.t = 0; h.timer = dur === undefined ? rnd(1,3) : dur; }

function walkTo(h, x, z, purpose){
  h.target.set(x, STANCE, z); h.purpose = purpose || 'wander';
  setState(h, 'walk', 14);
}
function chooseNext(h){
  release(h);
  const opts = [['wander',2.8],['idle',2.4]];
  if(seeds.some(s=>!s.gone)) opts.push(['food', dusk?1.1:2.6]);
  if(wheelUser === -1) opts.push(['wheel', dusk?.5:2.2]);
  if(hutUser === -1) opts.push(['hut', dusk?3.2:.9]);
  opts.push(['tube',1.0],['drink',.8]);
  let total = opts.reduce((a,o)=>a+o[1],0), r = Math.random()*total, choice='wander';
  for(const [name,w] of opts){ if((r-=w) <= 0){ choice = name; break; } }

  if(choice === 'idle'){ h.sub = pick(['look','groom','stretch']); setState(h,'idle', rnd(1.2,3.4)); return; }
  if(choice === 'wander'){ walkTo(h, rnd(-IN_X,IN_X), rnd(-IN_Z,IN_Z), 'wander'); return; }
  if(choice === 'food'){ const s = nearestSeed(h.group.position); if(s){ h.seed = s; walkTo(h, s.mesh.position.x, s.mesh.position.z, 'food'); return; } walkTo(h, rnd(-IN_X,IN_X), rnd(-IN_Z,IN_Z)); return; }
  if(choice === 'wheel'){ wheelUser = h.id; walkTo(h, WHEEL.x + 2.9, WHEEL.z, 'wheel'); return; }
  if(choice === 'hut'){ hutUser = h.id; const fx = HUT.pos.x - Math.sin(HUT.rot)*1.5, fz = HUT.pos.z - Math.cos(HUT.rot)*1.5; walkTo(h, fx, fz, 'hut'); return; }
  if(choice === 'tube'){
    const a = tubePoint(0), b = tubePoint(1);
    const da = Math.hypot(a.x-h.group.position.x, a.z-h.group.position.z);
    const db = Math.hypot(b.x-h.group.position.x, b.z-h.group.position.z);
    h.tubeDir = da < db ? 0 : 1;
    const p = da < db ? a : b;
    walkTo(h, p.x, p.z, 'tube'); return;
  }
  if(choice === 'drink'){ walkTo(h, BOTTLE.drink.x, BOTTLE.drink.z, 'drink'); return; }
}
function beginLerp(h, to, dur, arc, toHeading){
  h.lerp = { from:h.group.position.clone(), to:to.clone(), t:0, dur, arc:arc||0, fromHeading:h.heading, toHeading: toHeading===undefined?h.heading:toHeading };
}

function onArrive(h){
  switch(h.purpose){
    case 'food':  setState(h,'eat', 1.5 + Math.random()); break;
    case 'wheel': setState(h,'enterWheel',.6); beginLerp(h, new THREE.Vector3(WHEEL.x, WHEEL.cy - WHEEL.R + STANCE, WHEEL.z), .6, 1.0, 0); break;
    case 'hut':   setState(h,'enterHut',.5); {
        const fx = HUT.pos.x - Math.sin(HUT.rot)*.2, fz = HUT.pos.z - Math.cos(HUT.rot)*.2;
        beginLerp(h, new THREE.Vector3(fx, STANCE*.86, fz), .5, .1, HUT.rot + Math.PI);
      } break;
    case 'tube':  setState(h,'tube', 2.6); h.tubeT = h.tubeDir; break;
    case 'drink': setState(h,'drink', 2.4); break;
    default:      if(Math.random()<.55) chooseNext(h); else { h.sub = pick(['look','groom','stretch']); setState(h,'idle', rnd(.8,2.2)); }
  }
  h.purpose = 'wander';
}

function boop(h, silent){
  if(h.state === 'boop') return;
  release(h);
  setState(h,'boop', .95); h.hopT = 0;
  spawnHeart(h);
  if(!silent) squeak(h, pick(['squeak!','eek!','?','nom?','hi!']));
}

function updateHamster(h, dt, time){
  h.t += dt;
  const p = h.group.position;
  let move = 0, legAmp = .1, legRate = 2.2, headYaw = 0, headPitch = 0, cheekGoal = 1, sleepFace = false;
  h.bobAmt = damp(h.bobAmt, .05, 6, dt);

  switch(h.state){

    case 'idle': {
      if(h.sub === 'look'){ headYaw = Math.sin(time*1.1 + h.id)*0.7; h.heading += Math.sin(time*.6+h.id)*dt*.35; }
      else if(h.sub === 'groom'){ headPitch = .55 + Math.sin(time*9)*.12; headYaw = Math.sin(time*4)*.25; }
      else { h.rig.scale.y = damp(h.rig.scale.y, 1.08, 6, dt); h.rig.scale.x = damp(h.rig.scale.x, .95, 6, dt); headPitch = -.3; }
      legAmp = .07; legRate = 1.6;
      if(h.t > h.timer) chooseNext(h);
      break;
    }

    case 'walk': {
      const dx = h.target.x - p.x, dz = h.target.z - p.z;
      const dist = Math.hypot(dx,dz);
      const want = Math.atan2(dx,dz);
      const diff = wrap(want - h.heading);
      h.heading += clamp(diff, -h.turn*dt, h.turn*dt);
      if(Math.abs(diff) < .9){
        move = h.maxSpeed * (0.45 + 0.55*Math.min(1,Math.abs(diff)/1.2));
        legAmp = .85; legRate = 11; h.bobAmt = .07;
      } else { legRate = 3.4; legAmp = .25; }
      headPitch = -.12;
      if(dist < .35 || h.t > h.timer) onArrive(h);
      break;
    }

    case 'eat': {
      const s = h.seed;
      if(s && !s.gone){
        const dx = s.mesh.position.x - p.x, dz = s.mesh.position.z - p.z;
        h.heading += wrap(Math.atan2(dx,dz) - h.heading) * Math.min(1, dt*8);
        headPitch = .5 + Math.sin(time*17)*.16;
        cheekGoal = 1.55; legAmp = .05; legRate = 2;
        const k = clamp(h.t / h.timer, 0, 1);
        s.mesh.scale.setScalar(Math.max(.001, 1-k));
        if(k > .9){ s.gone = true; scene.remove(s.mesh); h.seed = null; }
      } else { cheekGoal = 1.1; headPitch = .2*Math.sin(time*6); }
      if(h.t > h.timer){ h.seed = null; chooseNext(h); }
      break;
    }

    case 'drink': {
      const want = Math.PI/2;
      h.heading += wrap(want - h.heading) * Math.min(1, dt*6);
      headPitch = -.75 + Math.sin(time*7)*.08;
      legAmp = .05; legRate = 1.6;
      if(h.t > h.timer) chooseNext(h);
      break;
    }

    case 'enterWheel': {
      runLerp(h, dt);
      legAmp = .9; legRate = 14;
      break;
    }

    case 'run': {
      p.x = damp(p.x, WHEEL.x, 8, dt); p.z = damp(p.z, WHEEL.z, 8, dt);
      p.y = damp(p.y, WHEEL.cy - WHEEL.R + STANCE, 8, dt);
      h.heading += wrap(0 - h.heading) * Math.min(1, dt*7);
      legAmp = 1.15; legRate = 26; h.bobAmt = .035; headPitch = -.15 + Math.sin(time*26)*.05;
      if(h.t > h.timer){ setState(h,'exitWheel',.55); beginLerp(h, new THREE.Vector3(WHEEL.x + 2.9, STANCE, WHEEL.z), .55, .9, Math.PI/2); }
      break;
    }

    case 'exitWheel': {
      runLerp(h, dt);
      legAmp = .8; legRate = 16;
      if(Math.random() < dt*.7) h.heading += dt*2.5;
      break;
    }

    case 'tube': {
      const speed = 0.42;
      h.tubeT += (h.tubeDir === 0 ? 1 : -1) * dt * speed;
      const pt = tubePoint(clamp(h.tubeT,0,1));
      const nxt = tubePoint(clamp(h.tubeT + (h.tubeDir===0?.03:-.03),0,1));
      p.copy(pt); p.y += STANCE*.5;
      const dx = nxt.x - pt.x, dz = nxt.z - pt.z;
      h.heading = Math.atan2(dx,dz);
      h.tilt.rotation.x = -Math.atan2(nxt.y - pt.y, Math.hypot(dx,dz)) * (h.tubeDir===0?1:-1);
      h.scaleGoal = .78;
      legAmp = 1.0; legRate = 16;
      if(h.tubeT <= 0 || h.tubeT >= 1){ h.tilt.rotation.x = 0; setState(h,'idle',.5); h.scaleGoal = 1; }
      break;
    }

    case 'enterHut': { runLerp(h, dt); sleepFace = true; legAmp = .3; legRate = 4; break; }

    case 'sleep': {
      sleepFace = true; h.scaleGoal = 1;
      h.rig.scale.y = damp(h.rig.scale.y, .8, 5, dt);
      h.rig.scale.x = damp(h.rig.scale.x, 1.08 + Math.sin(time*1.6)*.02, 4, dt);
      headPitch = .6; legAmp = 0; legRate = 0;
      h.heading += Math.sin(time*.5)*dt*.1;
      if(h.t > h.timer || (dusk === false && Math.random() < dt*.05)) chooseNext(h);
      break;
    }

    case 'boop': {
      h.hopT += dt;
      const k = clamp(h.hopT/.95, 0, 1);
      p.y = STANCE + Math.sin(k*Math.PI)*.85;
      h.heading += dt*10*(1-k);
      h.rig.scale.y = 1 + Math.sin(k*Math.PI*2)*.16;
      h.rig.scale.x = 1 - Math.sin(k*Math.PI*2)*.12;
      legAmp = .6; legRate = 20; headPitch = -.4;
      if(k >= 1) chooseNext(h);
      break;
    }
  }

  /* ---- integrate movement + collisions ---- */
  if(move > 0){
    p.x += Math.sin(h.heading) * move * dt;
    p.z += Math.cos(h.heading) * move * dt;
    h.speedNow = damp(h.speedNow, move, 10, dt);
  } else {
    h.speedNow = damp(h.speedNow, 0, 8, dt);
  }
  p.x = clamp(p.x, -IN_X, IN_X);
  p.z = clamp(p.z, -IN_Z, IN_Z);

  if(h.state !== 'tube' && h.state !== 'run'){
    for(const b of BLOCKERS){
      const dx = p.x-b.x, dz = p.z-b.z, d = Math.hypot(dx,dz);
      if(d < b.r && d > .0001){ p.x = b.x + dx/d*b.r; p.z = b.z + dz/d*b.r; }
    }
    for(const o of hamsters){
      if(o === h || o.state==='tube' || o.state==='sleep') continue;
      const dx = p.x-o.group.position.x, dz = p.z-o.group.position.z, d = Math.hypot(dx,dz);
      if(d < .95 && d > .0001){ p.x += dx/d*(.95-d)*.5; p.z += dz/d*(.95-d)*.5; }
    }
    p.y = damp(p.y, STANCE * (h.state==='sleep'?.86:1), 9, dt);
  }

  /* ---- animation layer ---- */
  h.phase += dt * legRate * (h.state==='walk' ? (0.4 + h.speedNow/h.maxSpeed) : 1);
  const offs = [0,Math.PI,Math.PI,0];
  h.legs.forEach((L,i)=>{ L.rotation.x = Math.sin(h.phase + offs[i]) * legAmp; });

  h.rig.position.y = Math.abs(Math.sin(h.phase)) * h.bobAmt;
  h.rig.rotation.z = Math.sin(h.phase) * h.bobAmt * .8;
  if(h.state !== 'boop' && h.state !== 'sleep' && h.state !== 'idle'){
    h.rig.scale.y = damp(h.rig.scale.y, 1, 8, dt);
    h.rig.scale.x = damp(h.rig.scale.x, 1, 8, dt);
  }
  h.group.rotation.y = h.heading;
  h.tilt.rotation.x = damp(h.tilt.rotation.x, h.state==='tube'?h.tilt.rotation.x:0, 6, dt);
  h.rig.scale.z = damp(h.rig.scale.z, h.scaleGoal, 8, dt);
  h.rig.scale.x = h.rig.scale.x*.5 + (h.scaleGoal)*.5 + h.rig.scale.x*.0;

  h.head.rotation.y = damp(h.head.rotation.y, headYaw, 9, dt);
  h.head.rotation.x = damp(h.head.rotation.x, headPitch, 11, dt);
  h.cheeks.forEach(c=>{ const s = damp(c.scale.x, cheekGoal, 6, dt); c.scale.setScalar(s); });
  h.eyes.forEach(e=>{ e.scale.y = damp(e.scale.y, sleepFace ? .12 : 1, 8, dt); });
  h.torso.rotation.z = Math.sin(time*2 + h.id)*.03;
  h.tail.rotation.x = -2.3 + Math.sin(time*6 + h.phase)*(h.state==='run'? .5 : .12);
  h.ring.visible = (highlightId === h.id || focusId === h.id);
  if(h.ring.visible){
    const s = 1 + Math.sin(time*5)*.07; h.ring.scale.setScalar(s);
    h.ring.material.opacity = .55 + Math.sin(time*5)*.25;
  }
}

function runLerp(h, dt){
  const L = h.lerp; if(!L) return;
  L.t = Math.min(1, L.t + dt / L.dur);
  const e = L.t<.5 ? 2*L.t*L.t : 1-Math.pow(-2*L.t+2,2)/2;
  h.group.position.x = THREE.MathUtils.lerp(L.from.x, L.to.x, e);
  h.group.position.z = THREE.MathUtils.lerp(L.from.z, L.to.z, e);
  h.group.position.y = THREE.MathUtils.lerp(L.from.y, L.to.y, e) + Math.sin(e*Math.PI)*L.arc;
  h.heading += wrap(L.toHeading - h.heading) * Math.min(1, dt*6);
  if(L.t >= 1){
    h.lerp = null;
    if(h.state === 'enterWheel') setState(h,'run', rnd(5,12));
    else if(h.state === 'exitWheel'){ release(h); setState(h,'idle', .8); }
    else if(h.state === 'enterHut') setState(h,'sleep', rnd(6,14));
  }
}

/* ============================================================
   9 · hearts + squeak bubble
   ============================================================ */
const hearts = [];
function spawnHeart(h){
  for(let i=0;i<3;i++){
    const m = new THREE.Mesh(heartGeo, new THREE.MeshBasicMaterial({color: i===1?0xFF7A3D:0xE8506E, transparent:true, opacity:1}));
    m.position.copy(h.group.position).add(new THREE.Vector3(rnd(-.3,.3), rnd(.9,1.3), rnd(-.3,.3)));
    m.scale.setScalar(rnd(.28,.44));
    scene.add(m);
    hearts.push({m, life:0, max:rnd(.8,1.3), spin:rnd(-3,3), rise:rnd(1.1,1.9)});
  }
}
function updateHearts(dt){
  for(let i=hearts.length-1;i>=0;i--){
    const x = hearts[i]; x.life += dt;
    x.m.position.y += dt*x.rise; x.m.rotation.z += dt*x.spin;
    const k = 1 - x.life/x.max;
    x.m.material.opacity = Math.max(0,k);
    x.m.scale.setScalar(.35 * (0.4 + k*0.9));
    if(k <= 0){ scene.remove(x.m); x.m.material.dispose(); hearts.splice(i,1); }
  }
}

const bubbleEl = $('bubble');
let bubbleTimer = 0;
function squeak(h, text){
  bubbleEl.textContent = text;
  bubbleEl.classList.add('show');
  bubbleTimer = 1.15;
  bubbleFollow = h;
}
let bubbleFollow = null;
const _v = new THREE.Vector3();
function updateBubble(dt){
  if(bubbleTimer > 0){
    bubbleTimer -= dt;
    if(bubbleFollow){
      bubbleFollow.group.getWorldPosition(_v); _v.y += 1.15;
      _v.project(camera);
      bubbleEl.style.left = (_v.x*.5+.5)*innerWidth + 'px';
      bubbleEl.style.top  = (-_v.y*.5+.5)*innerHeight + 'px';
    }
    if(bubbleTimer <= 0){ bubbleEl.classList.remove('show'); bubbleFollow = null; }
  }
}

/* ============================================================
   10 · wheel physics
   ============================================================ */
let wheelOmega = 0;
function updateWheel(dt){
  let runners = 0;
  for(const h of hamsters) if(h.state === 'run') runners++;
  const goal = runners ? 5.6 + runners*1.6 : 0;
  wheelOmega = damp(wheelOmega, goal, runners ? 2.4 : 0.55, dt);
  wheelSpin.rotation.x += wheelOmega * dt;
}
function shoveWheel(){ wheelOmega += 13; squeakAny('wheee!'); }

/* ============================================================
   11 · HUD wiring
   ============================================================ */
const resList = $('resList');
const labelFor = {
  idle:'loafing', walk:'trotting', eat:'stuffing face', drink:'sipping', run:'wheel mode',
  enterWheel:'climbing in', exitWheel:'dizzy', tube:'in the tube', enterHut:'moving in',
  sleep:'curled up', boop:'BOOPED'
};
const bucketFor = s => (['enterWheel','exitWheel','enterHut'].includes(s)) ? 'move' : (s==='seekFood'?'walk':s);

function addRow(h){
  const li = document.createElement('li');
  li.className = 'res newrow'; li.dataset.id = h.id;
  li.innerHTML = `<span class="chip" style="--c:#${h.coat.body.toString(16).padStart(6,'0')}"></span>
    <span class="nm">${h.name}<small>${h.coat.label}</small></span>
    <span class="st" data-s="idle">loafing</span><span class="go">◎</span>`;
  li.addEventListener('click', ()=> setFocus(focusId === h.id ? -1 : h.id));
  li.addEventListener('mouseenter', ()=> highlightId = h.id);
  li.addEventListener('mouseleave', ()=> { if(highlightId === h.id) highlightId = -1; });
  resList.appendChild(li);
  h.rowEl = li;
  $('popCount').textContent = hamsters.length + '/' + MAX_HAMSTERS;
}
let focusId = -1, highlightId = -1;
function setFocus(id){
  focusId = id;
  hamsters.forEach(h=> h.rowEl.classList.toggle('on', h.id === id));
  if(id === -1) view.tTarget.copy(HOME.target);
}
function updateRows(){
  for(const h of hamsters){
    const st = h.rowEl.querySelector('.st');
    const txt = labelFor[h.state] || 'potato';
    if(st.textContent !== txt){ st.textContent = txt; st.dataset.s = bucketFor(h.state); }
    st.classList.toggle('runpulse', h.state === 'run');
  }
}

let paused = false, autoOrbit = !window.matchMedia('(prefers-reduced-motion: reduce)').matches, simSpeed = 1;
$('bSeeds').addEventListener('click', ()=>{ scatterSeeds(10); squeakAny('seeds!'); });
$('bWheel').addEventListener('click', shoveWheel);
$('bAdd').addEventListener('click', ()=> addHamster());
$('bLamp').addEventListener('click', e=>{ dusk = !dusk; e.currentTarget.setAttribute('aria-pressed', dusk); document.body.classList.toggle('dusk', dusk); squeakAny(dusk?'zzz…':'morning!'); });
$('bOrbit').addEventListener('click', e=>{ autoOrbit = !autoOrbit; e.currentTarget.setAttribute('aria-pressed', autoOrbit); });
$('bPause').addEventListener('click', e=>{ paused = !paused; e.currentTarget.setAttribute('aria-pressed', paused); e.currentTarget.querySelector('span').textContent = paused ? '▶' : '‖'; });
$('bView').addEventListener('click', ()=>{ setFocus(-1); view.tTheta = HOME.theta; view.tPhi = HOME.phi; view.tDist = HOME.dist; });
$('rSpeed').addEventListener('input', e=>{ simSpeed = parseFloat(e.target.value); $('spdVal').textContent = simSpeed.toFixed(1)+'×'; });

function addHamster(){
  if(hamsters.length >= MAX_HAMSTERS){ squeakAny('cage is full!'); return; }
  const h = makeHamster();
  h.group.position.set(rnd(-1,1), 3.2, rnd(-1,1));
  beginLerp(h, new THREE.Vector3(rnd(-4,4), STANCE, rnd(-3,3)), .9, 1.6, rnd(0,6.28));
  setState(h,'idle',.9);
  spawnHeart(h);
  $('bAdd').disabled = hamsters.length >= MAX_HAMSTERS;
}
function squeakAny(t){ if(hamsters.length) squeak(pick(hamsters), t); }

addEventListener('keydown', e=>{
  const k = e.key.toLowerCase();
  if(k === 's'){ scatterSeeds(10); squeakAny('seeds!'); }
  else if(k === 'w') shoveWheel();
  else if(k === 'a') addHamster();
  else if(k === 'l') $('bLamp').click();
  else if(k === 'o') $('bOrbit').click();
  else if(k === ' '){ e.preventDefault(); $('bPause').click(); }
  else if(k === 'escape') setFocus(-1);
  else if(k === 'r') $('bView').click();
  else if(/^[1-8]$/.test(k)){ const h = hamsters[+k-1]; if(h) setFocus(focusId===h.id?-1:h.id); }
});

/* ============================================================
   12 · camera controls (hand-rolled orbit + pinch)
   ============================================================ */
const pointers = new Map();
let dragging = false, movedPx = 0, pinchPrev = 0;
canvas.addEventListener('pointerdown', e=>{
  canvas.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
  dragging = pointers.size === 1; movedPx = 0;
  canvas.classList.add('dragging');
});
canvas.addEventListener('pointermove', e=>{
  if(pointers.has(e.pointerId)){
    const prev = pointers.get(e.pointerId);
    const dx = e.clientX - prev.x, dy = e.clientY - prev.y;
    pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
    movedPx += Math.abs(dx) + Math.abs(dy);
    if(pointers.size === 2){
      const pts = [...pointers.values()];
      const d = Math.hypot(pts[0].x-pts[1].x, pts[0].y-pts[1].y);
      if(pinchPrev) view.tDist = clamp(view.tDist * (pinchPrev/d), 12, 48);
      pinchPrev = d;
    } else if(dragging){
      view.tTheta -= dx * .006;
      view.tPhi = clamp(view.tPhi - dy * .005, .35, 1.42);
      if(movedPx > 8) setFocus(-1);
    }
  } else {
    hoverTest(e.clientX, e.clientY);
  }
});
function endPointer(e){
  if(pointers.has(e.pointerId)){
    pointers.delete(e.pointerId);
    if(pointers.size < 2) pinchPrev = 0;
    if(pointers.size === 0){
      dragging = false; canvas.classList.remove('dragging');
      if(movedPx < 7) tryBoop(e.clientX, e.clientY);
    }
  }
}
canvas.addEventListener('pointerup', endPointer);
canvas.addEventListener('pointercancel', endPointer);
canvas.addEventListener('wheel', e=>{ e.preventDefault(); view.tDist = clamp(view.tDist + Math.sign(e.deltaY)*1.6, 12, 48); }, {passive:false});

const ray = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let hoverT = 0;
function pickHamster(cx, cy){
  ndc.set((cx/innerWidth)*2-1, -(cy/innerHeight)*2+1);
  ray.setFromCamera(ndc, camera);
  const hits = ray.intersectObjects(hamsters.map(h=>h.group), true);
  if(!hits.length) return null;
  let o = hits[0].object;
  while(o && !o.userData.hamster) o = o.parent;
  return o ? o.userData.hamster : null;
}
function hoverTest(cx, cy){
  const now = performance.now();
  if(now - hoverT < 90) return; hoverT = now;
  const h = pickHamster(cx, cy);
  canvas.style.cursor = h ? 'pointer' : (dragging ? 'grabbing' : 'grab');
  highlightId = h ? h.id : -1;
}
function tryBoop(cx, cy){
  const h = pickHamster(cx, cy);
  if(h) boop(h);
}

function updateCamera(dt){
  if(autoOrbit && !dragging) view.tTheta += dt*.09;
  if(focusId !== -1){
    const h = hamsters.find(x=>x.id === focusId);
    if(h){ view.tTarget.copy(h.group.position); view.tTarget.y += .6; }
    else setFocus(-1);
  }
  view.theta = damp(view.theta, view.tTheta, 6, dt);
  view.phi   = damp(view.phi, view.tPhi, 6, dt);
  view.dist  = damp(view.dist, view.tDist, 5, dt);
  view.target.lerp(view.tTarget, 1 - Math.exp(-5*dt));
  const s = Math.sin(view.phi)*view.dist;
  camera.position.set(
    view.target.x + s*Math.sin(view.theta),
    view.target.y + Math.cos(view.phi)*view.dist,
    view.target.z + s*Math.cos(view.theta)
  );
  camera.lookAt(view.target);
}

/* ============================================================
   13 · resize / loop
   ============================================================ */
addEventListener('resize', ()=>{
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
});

let clock = 0, last = performance.now(), rowTick = 0, fpsAcc = 0, fpsN = 0;
const moodLines = ['mildly chaotic','seed-fuelled','wheel-obsessed','deeply napping','structurally snacky','unhinged (cute)'];
let moodSwap = 0, mood = moodLines[0];

function frame(now){
  const raw = Math.min(.05, (now - last)/1000); last = now;
  const dt = paused ? 0 : raw * simSpeed;
  clock += dt;

  for(const h of hamsters) updateHamster(h, dt, clock);
  updateWheel(dt);
  updateHearts(dt);
  updateBubble(paused ? 0 : raw);
  lerpTheme(raw);
  updateCamera(raw);

  motes.rotation.y += raw*.02;
  motes.position.y = Math.sin(clock*.35)*.25;

  rowTick += raw;
  if(rowTick > .16){ rowTick = 0; updateRows(); refreshMeters(); }
  moodSwap += raw;
  if(moodSwap > 7){ moodSwap = 0; mood = pick(moodLines); $('mood').textContent = 'Mood: ' + mood; }

  fpsAcc += raw; fpsN++;
  if(fpsAcc > .5){ $('fps').textContent = Math.round(fpsN/fpsAcc) + ' fps'; fpsAcc = 0; fpsN = 0; }

  renderer.render(scene, camera);
  if(!window.__HP_BOOTED){
    window.__HP_BOOTED = true;
    setTimeout(()=>{ const b = $('boot'); b.classList.add('gone'); setTimeout(()=>b.remove(), 800); }, 260);
  }
  requestAnimationFrame(frame);
}

function refreshMeters(){
  const rpm = Math.abs(wheelOmega) * 9.5493;
  $('rpm').textContent = Math.round(rpm);
  $('rpmBar').style.width = Math.min(100, rpm/62*100) + '%';
  const n = seeds.filter(s=>!s.gone).length;
  $('seedN').textContent = n;
  $('seedBar').style.width = Math.min(100, n/26*100) + '%';
}

/* ============================================================
   14 · curtain up
   ============================================================ */
for(let i=0;i<MAX_HAMSTERS;i++){ const h = makeHamster(); h.group.position.set(rnd(-4.5,4.5), STANCE, rnd(-3,3)); h.heading = rnd(0,6.28); }
scatterSeeds(12);
$('bAdd').disabled = true;
setTimeout(()=>{ $('bAdd').disabled = hamsters.length >= MAX_HAMSTERS; }, 400);
requestAnimationFrame(frame);
</script>
</body>
</html>
```

**What's in the box**

- **Cage & tray:** instanced wire bars, lid rails, a yellow feeding door with a knob, a mint tray filled with 170 randomly tinted bedding chips, all sitting on a round wooden table so it reads as a diorama.
- **Interactive objects:** a plastic wheel (real spin-up/coast physics, RPM meter), a translucent arch tunnel you can watch a hamster run *through*, a food bowl, a water bottle on the bars, an open-front hut for naps, chew toys.
- **Autonomy:** weighted state machine per hamster — loafing (look / groom / stretch sub-animations), wandering with turning + soft collision avoidance, seed seeking and chewing with puffing cheeks, wheel sprinting (climbs in, runs, stumbles out dizzy), drinking, tube traversal with correct banking, sleeping with closed eyes and breathing.
- **You can poke it:** drag to orbit, scroll/pinch to zoom, click a hamster to boop it (hop, spin, hearts, squeak bubble), hover the resident list to spotlight one, click to have the camera follow it. Keys: `S` seeds, `W` shove wheel, `A` new hamster, `L` lamp (dusk lighting theme + sleepier hamsters), `O` orbit, `Space` pause, `1–8` follow, `Esc` free cam.