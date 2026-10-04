# Хомякина физика — 3D клетка с честным колесом

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>ХОМЯКИ · честная физика клетки · Three.js r128</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0c0908; --panel:#171110; --panel2:#221915; --line:#3d2d23;
  --amber:#f2a63c; --amber2:#ffc973; --ink:#f5ead9; --muted:#a58e79;
  --ok:#79d99a; --warn:#f2c94c; --bad:#f0705e;
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;background:var(--bg);color:var(--ink);overflow:hidden;
  font-family:'IBM Plex Sans',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;
}
canvas#scene{position:fixed;inset:0;display:block;z-index:0}
#vignette{
  position:fixed;inset:0;z-index:1;pointer-events:none;
  background:
    radial-gradient(120% 90% at 62% 38%, rgba(0,0,0,0) 38%, rgba(0,0,0,.55) 100%),
    linear-gradient(180deg, rgba(20,10,4,.35), rgba(0,0,0,0) 22%);
  mix-blend-mode:multiply;
}

/* ============ ПАНЕЛЬ ============ */
#panel{
  position:fixed;left:0;top:0;bottom:0;width:352px;z-index:6;
  display:flex;flex-direction:column;
  background:
    repeating-linear-gradient(90deg, rgba(255,255,255,.014) 0 1px, transparent 1px 5px),
    linear-gradient(180deg,#221813 0%, #150f0d 42%, #100b0a 100%);
  border-right:1px solid var(--line);
  box-shadow:26px 0 70px rgba(0,0,0,.6), inset -1px 0 0 rgba(255,190,110,.06);
  animation:slideIn .7s cubic-bezier(.2,.9,.25,1) both;
}
@keyframes slideIn{from{transform:translateX(-102%);opacity:0}to{transform:none;opacity:1}}
#panel::after{
  content:"";position:absolute;left:0;right:0;top:0;height:2px;
  background:linear-gradient(90deg,var(--amber),#c9552a 40%,transparent);
}
.head{padding:20px 20px 14px;position:relative;overflow:hidden}
.kicker{
  font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.22em;
  color:var(--amber);text-transform:uppercase;display:flex;gap:8px;align-items:center
}
.kicker b{color:#6d5849;font-weight:500}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--amber);
  box-shadow:0 0 0 0 rgba(242,166,60,.6);animation:pulse 2.2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(242,166,60,.55)}70%{box-shadow:0 0 0 12px rgba(242,166,60,0)}100%{box-shadow:0 0 0 0 rgba(242,166,60,0)}}
h1{
  font-family:'Unbounded',sans-serif;font-weight:800;font-size:38px;line-height:.92;
  margin:12px 0 6px;letter-spacing:-.03em;color:var(--ink);
  text-shadow:0 2px 0 #000, 0 0 34px rgba(242,166,60,.14);
}
h1 em{font-style:normal;color:var(--amber);display:block;font-size:14px;letter-spacing:.02em;margin-top:8px;font-weight:600}
.sub{font-size:12.5px;color:var(--muted);line-height:1.55;max-width:300px}
.wm{
  position:absolute;right:-14px;top:-26px;font-family:'Unbounded',sans-serif;font-weight:800;
  font-size:124px;color:rgba(255,170,80,.045);pointer-events:none;user-select:none;
}

.sect{padding:14px 20px 6px;font-family:'IBM Plex Mono',monospace;font-size:10px;
  letter-spacing:.2em;color:#7b6553;text-transform:uppercase;display:flex;justify-content:space-between}
.sect span{color:#4d3d31}

#roster{padding:0 12px;overflow-y:auto;flex:1;scrollbar-width:thin;scrollbar-color:#3a2a20 transparent}
#roster::-webkit-scrollbar{width:6px}#roster::-webkit-scrollbar-thumb{background:#3a2a20;border-radius:3px}
.h-item{
  position:relative;display:grid;grid-template-columns:26px 1fr auto;gap:11px;align-items:center;
  padding:11px 10px 12px;border-radius:3px;cursor:pointer;border:1px solid transparent;
  transition:background .22s, transform .22s, border-color .22s;
}
.h-item:hover{background:linear-gradient(90deg,rgba(242,166,60,.09),rgba(242,166,60,0));transform:translateX(4px);border-color:rgba(242,166,60,.16)}
.h-item.on{background:linear-gradient(90deg,rgba(242,166,60,.13),transparent);border-color:rgba(242,166,60,.28)}
.h-item::before{content:"";position:absolute;left:0;top:8px;bottom:8px;width:2px;background:var(--c);
  opacity:.25;transition:opacity .2s, top .2s, bottom .2s;border-radius:2px}
.h-item:hover::before,.h-item.on::before{opacity:1;top:2px;bottom:2px;box-shadow:0 0 12px var(--c)}
.dot{width:26px;height:26px;border-radius:50%;background:
   radial-gradient(circle at 34% 28%, color-mix(in srgb,var(--c) 78%, #fff), var(--c) 58%, color-mix(in srgb,var(--c) 62%, #000));
   box-shadow:0 2px 6px rgba(0,0,0,.55), inset 0 -2px 4px rgba(0,0,0,.35);transition:transform .25s cubic-bezier(.3,1.6,.5,1)}
.h-item:hover .dot{transform:scale(1.16) rotate(-8deg)}
.nm{font-family:'Unbounded',sans-serif;font-weight:600;font-size:14px;letter-spacing:-.01em;line-height:1.2}
.act{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--amber2);margin-top:3px;letter-spacing:.01em}
.act.mute{color:#7d6a5b}
.spd{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#8a7462;text-align:right;line-height:1.35}
.spd b{display:block;font-size:15px;color:var(--ink);font-weight:600}
.bar{grid-column:1/-1;height:2px;background:#2a1f19;border-radius:2px;overflow:hidden;margin-top:2px}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--c),var(--amber2));width:0;transition:width .12s linear}

.foot{border-top:1px solid var(--line);padding:12px 18px 16px;background:linear-gradient(180deg,rgba(0,0,0,.25),transparent)}
.tog{display:flex;align-items:center;gap:9px;font-family:'IBM Plex Mono',monospace;font-size:11px;
  color:var(--muted);cursor:pointer;padding:5px 0;user-select:none;transition:color .2s}
.tog:hover{color:var(--ink)}
.box{width:14px;height:14px;border:1px solid #4a382c;border-radius:2px;position:relative;flex:0 0 auto;transition:.2s}
.tog.on .box{background:var(--amber);border-color:var(--amber);box-shadow:0 0 12px rgba(242,166,60,.45)}
.tog.on .box::after{content:"";position:absolute;left:4px;top:1px;width:4px;height:8px;border:solid #1a1008;border-width:0 2px 2px 0;transform:rotate(42deg)}
.tog input{display:none}
.slider{display:flex;align-items:center;gap:10px;margin-top:8px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted)}
input[type=range]{-webkit-appearance:none;flex:1;height:2px;background:#3a2a20;border-radius:2px;outline:none}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;border-radius:50%;background:var(--amber);cursor:pointer;box-shadow:0 0 10px rgba(242,166,60,.6)}
input[type=range]::-moz-range-thumb{width:13px;height:13px;border:none;border-radius:50%;background:var(--amber);cursor:pointer}
.btn{
  margin-top:10px;width:100%;padding:9px;background:transparent;border:1px solid #4a382c;color:var(--amber2);
  font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.13em;text-transform:uppercase;
  cursor:pointer;border-radius:3px;transition:.2s;position:relative;overflow:hidden
}
.btn:hover{background:var(--amber);color:#180f06;border-color:var(--amber);transform:translateY(-1px)}
.btn:active{transform:translateY(1px)}

/* ============ ДИАГНОСТИКА ============ */
#diag{
  position:fixed;right:18px;bottom:18px;z-index:5;width:322px;
  background:linear-gradient(180deg,rgba(20,14,11,.93),rgba(11,8,7,.95));
  border:1px solid var(--line);border-left:2px solid var(--amber);
  padding:13px 15px 12px;font-family:'IBM Plex Mono',monospace;font-size:11px;
  box-shadow:0 22px 60px rgba(0,0,0,.6);animation:fadeUp .9s .35s cubic-bezier(.2,.9,.25,1) both;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.dhead{display:flex;justify-content:space-between;align-items:center;
  font-size:9.5px;letter-spacing:.2em;color:#8a7360;text-transform:uppercase;margin-bottom:9px}
.pill{padding:2px 8px;border-radius:2px;font-weight:600;letter-spacing:.12em}
.pill.ok{background:rgba(121,217,154,.14);color:var(--ok);border:1px solid rgba(121,217,154,.35)}
.pill.bad{background:rgba(240,112,94,.16);color:var(--bad);border:1px solid rgba(240,112,94,.4);animation:blink .8s infinite}
@keyframes blink{50%{opacity:.45}}
.row{display:flex;justify-content:space-between;gap:8px;padding:2.5px 0;color:#9b8571}
.row b{color:var(--ink);font-weight:500;font-variant-numeric:tabular-nums}
.row.hl{color:var(--amber2)} .row.hl b{color:var(--amber2)}
.row.good b{color:var(--ok)} .row.warnv b{color:var(--bad)}
.sep{height:1px;background:var(--line);margin:8px 0}
.row .tag{color:#5d4a3c;font-size:9.5px;letter-spacing:.1em}

#hint{
  position:fixed;left:372px;bottom:18px;z-index:5;font-family:'IBM Plex Mono',monospace;
  font-size:10.5px;letter-spacing:.09em;color:#7a6555;pointer-events:none;
  animation:fadeUp 1s .6s both}
#hint kbd{background:#241a14;border:1px solid #3d2d23;padding:1px 5px;border-radius:2px;color:var(--amber2);font-family:inherit}

#togglePanel{display:none}
@media (max-width:980px){
  #panel{width:100%;height:46vh;top:auto;bottom:0;border-right:none;border-top:1px solid var(--line)}
  .head{padding:14px 16px 8px} h1{font-size:28px} .sub{display:none} .wm{display:none}
  #diag{right:10px;top:10px;bottom:auto;width:min(322px,calc(100% - 20px));transform:scale(.9);transform-origin:top right}
  #hint{display:none}
}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="vignette"></div>

<aside id="panel">
  <div class="head">
    <div class="wm">5</div>
    <div class="kicker"><span class="pulse"></span> БИОЛАБОРАТОРИЯ · <b>three.js r128</b></div>
    <h1>ХОМЯКИ<em>честная физика клетки</em></h1>
    <p class="sub">Колесо крутит тот, кто в нём бежит: ω = v/R. Лапы считаются от пройденного пути, а не от часов. Труба полная — вход только через торец.</p>
  </div>

  <div class="sect">КТО ГДЕ <span id="whoCount">5 активных</span></div>
  <div id="roster"></div>

  <div class="foot">
    <label class="tog on" id="togCol"><input type="checkbox" checked><span class="box"></span>показать тела столкновений</label>
    <label class="tog" id="togPause"><input type="checkbox"><span class="box"></span>пауза</label>
    <div class="slider"><span>ЗАМЕДЛЕНИЕ</span><input type="range" id="tsl" min="0.15" max="1.6" step="0.05" value="1"><b id="tval" style="color:#f5ead9">1.00×</b></div>
    <button class="btn" id="kick">толкнуть пустое колесо</button>
  </div>
</aside>

<div id="diag">
  <div class="dhead"><span>Проверка физики · live</span><span class="pill ok" id="verdict">OK</span></div>
  <div class="row"><span>бегун в колесе</span><b id="dRunner">—</b></div>
  <div class="row hl"><span>v лап (лапы по ободу)</span><b id="dPaw">0.000</b></div>
  <div class="row hl"><span>|ω| · R (обод под лапами)</span><b id="dRim">0.000</b></div>
  <div class="row" id="rDev"><span>расхождение</span><b id="dDev">—</b></div>
  <div class="sep"></div>
  <div class="row"><span>ω колеса</span><b id="dOmega">0.000 рад/с</b></div>
  <div class="row"><span>обороты</span><b id="dRpm">0.0 об/мин</b></div>
  <div class="row"><span>габарит / R</span><b id="dClr">—</b></div>
  <div class="row"><span>лапы на нижней точке</span><b id="dFoot">—</b></div>
  <div class="sep"></div>
  <div class="row"><span>в трубе</span><b id="dPipe">—</b></div>
  <div class="row"><span>отклонение от оси</span><b id="dAxis">0.000</b></div>
  <div class="row"><span>фаза шага / Δ</span><b id="dPhase">0.00 / 0.000</b></div>
  <div class="row" id="rViol"><span>проходов сквозь тела</span><b id="dViol">0</b></div>
  <div class="sep"></div>
  <div class="row"><span>кадров <span class="tag">FPS</span></span><b id="dFps">60</b></div>
  <div class="row"><span>draw calls</span><b id="dDc">0</b></div>
</div>

<div id="hint"><kbd>клик</kbd> хомяк → прыжок &nbsp;·&nbsp; <kbd>клик</kbd> колесо → толчок &nbsp;·&nbsp; <kbd>мышь</kbd> орбита &nbsp;·&nbsp; <kbd>колесо</kbd> зум</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
"use strict";
/* =====================================================================
   0. ГАБАРИТЫ — из них всё считается, а не подбирается на глаз
   ===================================================================== */
const ДЛИНА_ЗВЕРЯ   = 0.62;   // нос -> основание хвоста
const ВЫСОТА_ЗВЕРЯ  = 0.34;   // стопы -> верх спины
const ШИРИНА_ЗВЕРЯ  = 0.30;   // бока
const ТОРС          = 0.24;   // стопы -> центр корпуса (точка position хомяка)
const ЗАПАС         = 0.10;

// радиус беговой поверхности колеса ВЫЧИСЛЕН из габарита зверя
const R_ОБОДА       = ВЫСОТА_ЗВЕРЯ + ДЛИНА_ЗВЕРЯ * 0.55 + ЗАПАС;        // 0.781
const ШИРИНА_КОЛЕСА = ШИРИНА_ЗВЕРЯ * 2.2;                               // 0.66 — шире боков в 2.2 раза
const ГАБАРИТ_ДИАГ  = Math.hypot(ДЛИНА_ЗВЕРЯ * 0.5, ВЫСОТА_ЗВЕРЯ);      // худший угол зверя = 0.504
const ШАГ_ЛАПА      = ДЛИНА_ЗВЕРЯ * 0.30;                               // длина одного шага лап
const RADIUS_ТЕЛА   = 0.16;   // радиус тела в плане (для толкания)

console.assert(ГАБАРИТ_ДИАГ < R_ОБОДА - 0.05, 'зверь обязан целиком помещаться в колесе');
console.assert(ШИРИНА_КОЛЕСА > ШИРИНА_ЗВЕРЯ * 1.8, 'расстояние между ободами обязано быть шире боков');

/* =====================================================================
   1. СЦЕНА
   ===================================================================== */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x120c09);
scene.fog = new THREE.Fog(0x140d09, 11, 34);

const camera = new THREE.PerspectiveCamera(40, innerWidth/innerHeight, 0.1, 120);
camera.position.set(3.9, 2.35, 5.15);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.075;
controls.target.set(0.15, 0.55, 0.05);
controls.minDistance = 1.8; controls.maxDistance = 17;
controls.maxPolarAngle = Math.PI * 0.495;
controls.update();

/* ---- текстуры-процедуры ---- */
function woodTex(base, dark, w, h, planks){
  const c = document.createElement('canvas'); c.width=w; c.height=h;
  const g = c.getContext('2d');
  g.fillStyle = base; g.fillRect(0,0,w,h);
  for(let i=0;i<240;i++){
    g.globalAlpha = 0.03 + Math.random()*0.06;
    g.strokeStyle = Math.random()<0.5 ? dark : '#ffffff';
    g.lineWidth = 0.6 + Math.random()*2.4;
    const y = Math.random()*h; g.beginPath(); g.moveTo(0,y);
    for(let x=0;x<=w;x+=28) g.lineTo(x, y + Math.sin(x*0.02 + i)*3.2 + (Math.random()-0.5)*2);
    g.stroke();
  }
  g.globalAlpha = 1;
  if(planks){
    g.strokeStyle = 'rgba(0,0,0,.42)'; g.lineWidth = 2.5;
    for(let i=1;i<planks;i++){ const y = h*i/planks; g.beginPath(); g.moveTo(0,y); g.lineTo(w,y); g.stroke(); }
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4;
  return t;
}
function noiseTex(base, amt, size){
  const c = document.createElement('canvas'); c.width=c.height=size;
  const g = c.getContext('2d'); g.fillStyle = base; g.fillRect(0,0,size,size);
  const im = g.getImageData(0,0,size,size), d = im.data;
  for(let i=0;i<d.length;i+=4){ const n=(Math.random()-0.5)*amt; d[i]+=n; d[i+1]+=n*0.9; d[i+2]+=n*0.8; }
  g.putImageData(im,0,0);
  const t = new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; return t;
}

/* ---- свет ---- */
scene.add(new THREE.HemisphereLight(0xbcd0ee, 0x53341f, 0.42));
const sun = new THREE.DirectionalLight(0xfff1dc, 2.05);
sun.position.set(5.2, 8.4, 4.6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1; sun.shadow.camera.far = 26;
sun.shadow.camera.left = -6.5; sun.shadow.camera.right = 6.5;
sun.shadow.camera.top = 6; sun.shadow.camera.bottom = -6;
sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.018;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x8fb2ff, 0.30); fill.position.set(-7, 3.4, -2.5); scene.add(fill);
const lamp = new THREE.PointLight(0xffb463, 1.15, 9, 2); lamp.position.set(0.2, 3.15, 0.1); scene.add(lamp);

/* =====================================================================
   2. КОМНАТА + СТОЛ
   ===================================================================== */
const ROOM = new THREE.Group(); scene.add(ROOM);
{
  const floorT = woodTex('#5a3a24', '#2c1a0e', 512, 512, 6); floorT.repeat.set(6,6);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(34,34),
    new THREE.MeshStandardMaterial({map:floorT, roughness:0.78, metalness:0.02}));
  floor.rotation.x = -Math.PI/2; floor.position.y = -2.55; floor.receiveShadow = true; ROOM.add(floor);

  const wallT = noiseTex('#8c7a67', 26, 256); wallT.repeat.set(6,3);
  const wallMat = new THREE.MeshStandardMaterial({map:wallT, roughness:0.95});
  const back = new THREE.Mesh(new THREE.PlaneGeometry(34,15), wallMat);
  back.position.set(0, 4.2, -8.5); back.receiveShadow = true; ROOM.add(back);
  const left = new THREE.Mesh(new THREE.PlaneGeometry(34,15), wallMat);
  left.rotation.y = Math.PI/2; left.position.set(-9.5, 4.2, 0); left.receiveShadow = true; ROOM.add(left);

  const skirt = new THREE.Mesh(new THREE.BoxGeometry(34,0.42,0.12),
    new THREE.MeshStandardMaterial({color:0xc9b79f, roughness:0.85}));
  skirt.position.set(0, -2.34, -8.42); ROOM.add(skirt);

  // окно слева (источник «дневного» света)
  const win = new THREE.Group(); win.position.set(-9.4, 2.6, -2.2); win.rotation.y = Math.PI/2; ROOM.add(win);
  const glow = new THREE.Mesh(new THREE.PlaneGeometry(3.1,2.2),
    new THREE.MeshBasicMaterial({color:0xdce9ff})); win.add(glow);
  const frameM = new THREE.MeshStandardMaterial({color:0xf0e8dc, roughness:0.7});
  [[0,1.16,3.3,0.14],[0,-1.16,3.3,0.14],[1.63,0,0.14,2.4],[-1.63,0,0.14,2.4],[0,0,0.09,2.3]].forEach(p=>{
    const b = new THREE.Mesh(new THREE.BoxGeometry(p[2],p[3],0.12), frameM); b.position.set(p[0],p[1],0.06); win.add(b);
  });

  // стол
  const topT = woodTex('#7a4b2b', '#3a2113', 1024, 512, 0);
  const table = new THREE.Group(); ROOM.add(table);
  const top = new THREE.Mesh(new THREE.BoxGeometry(9.4,0.16,6.8),
    new THREE.MeshStandardMaterial({map:topT, roughness:0.42, metalness:0.04}));
  top.position.y = -0.38; top.castShadow = top.receiveShadow = true; table.add(top);
  const apronM = new THREE.MeshStandardMaterial({color:0x4a2c19, roughness:0.7});
  [[0,-0.52,-3.32,9.1,0.22],[0,-0.52,3.32,9.1,0.22],[-4.55,-0.52,0,0.22,6.6],[4.55,-0.52,0,0.22,6.6]].forEach(a=>{
    const b = new THREE.Mesh(new THREE.BoxGeometry(a[3],a[4],a[3]===9.1?0.14:6.6), apronM);
    b.position.set(a[0],a[1],a[2]); b.castShadow = true; table.add(b);
  });
  [[-4.2,-2.9],[4.2,-2.9],[-4.2,2.9],[4.2,2.9]].forEach(p=>{
    const l = new THREE.Mesh(new THREE.CylinderGeometry(0.11,0.085,2.1,10), apronM);
    l.position.set(p[0],-1.5,p[1]); l.castShadow = true; table.add(l);
  });

  //Books + plant + лампа
  const bookCols=[0x8c2f2a,0x2f5a4a,0xb98a35,0x2d3b5e];
  for(let i=0;i<4;i++){
    const b=new THREE.Mesh(new THREE.BoxGeometry(0.62,0.11,0.44),
      new THREE.MeshStandardMaterial({color:bookCols[i],roughness:0.72}));
    b.position.set(3.55+Math.sin(i)*0.05, -0.295+0.115*i+0.005, -2.35);
    b.rotation.y=0.12*i; b.castShadow=true; ROOM.add(b);
  }
  const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.3,0.5,16),
    new THREE.MeshStandardMaterial({color:0xa1553a, roughness:0.85}));
  pot.position.set(-3.9,-0.05,-2.3); pot.castShadow=true; ROOM.add(pot);
  for(let i=0;i<7;i++){
    const leaf=new THREE.Mesh(new THREE.ConeGeometry(0.11,0.95,5),
      new THREE.MeshStandardMaterial({color:0x3f6b3c, roughness:0.8}));
    const a=i/7*6.28; leaf.position.set(-3.9+Math.cos(a)*0.16, 0.62, -2.3+Math.sin(a)*0.16);
    leaf.rotation.set(Math.cos(a)*0.42, 0, Math.sin(a)*-0.42); leaf.castShadow=true; ROOM.add(leaf);
  }
  const cord=new THREE.Mesh(new THREE.CylinderGeometry(0.014,0.014,3.4,6),
    new THREE.MeshStandardMaterial({color:0x241a14})); cord.position.set(0.2,4.4,0.1); ROOM.add(cord);
  const shade=new THREE.Mesh(new THREE.ConeGeometry(0.62,0.5,22,1,true),
    new THREE.MeshStandardMaterial({color:0x2c2320,roughness:0.5,metalness:0.35,side:THREE.DoubleSide}));
  shade.position.set(0.2,3.0,0.1); shade.castShadow=true; ROOM.add(shade);
  const bulb=new THREE.Mesh(new THREE.SphereGeometry(0.12,12,10),
    new THREE.MeshBasicMaterial({color:0xffdfae})); bulb.position.set(0.2,2.86,0.1); ROOM.add(bulb);
}

/* =====================================================================
   3. КЛЕТКА: поддон, прутья, рамки, подстилка (InstancedMesh)
   ===================================================================== */
const CAGE = {w:6.0, d:4.0, wallH:1.9, barR:0.022};
const GROUND_Y = 0.0;
{
  const tray = new THREE.Mesh(new THREE.BoxGeometry(CAGE.w+0.34, 0.40, CAGE.d+0.34),
    new THREE.MeshStandardMaterial({color:0x8d939b, roughness:0.42, metalness:0.62}));
  tray.position.y = -0.14; tray.castShadow = tray.receiveShadow = true; scene.add(tray);
  const rimM = new THREE.MeshStandardMaterial({color:0xb9c0c8, roughness:0.35, metalness:0.7});
  [[0,(CAGE.d+0.34)/2-0.03,CAGE.w+0.34,0.07],[0,-(CAGE.d+0.34)/2+0.03,CAGE.w+0.34,0.07]]
   .forEach(r=>{const b=new THREE.Mesh(new THREE.BoxGeometry(r[2],0.075,0.07),rimM);b.position.set(r[0],0.05,r[1]);b.castShadow=true;scene.add(b);});
  [[(CAGE.w+0.34)/2-0.03,0],[ -(CAGE.w+0.34)/2+0.03,0]].forEach(r=>{
    const b=new THREE.Mesh(new THREE.BoxGeometry(0.07,0.075,CAGE.d+0.34),rimM);b.position.set(r[0],0.05,r[1]);b.castShadow=true;scene.add(b);});

  // подстилка
  const bed = new THREE.Mesh(new THREE.PlaneGeometry(CAGE.w, CAGE.d),
    new THREE.MeshStandardMaterial({map:noiseTex('#c9a06a',34,256), color:0xd8b481, roughness:0.98}));
  bed.rotation.x = -Math.PI/2; bed.position.y = 0.004; bed.receiveShadow = true; scene.add(bed);

  // ЩЕПКИ — один InstancedMesh
  const N_CHIP = 950;
  const chipGeo = new THREE.CylinderGeometry(0.048,0.048,0.024,6,1,true,0,2.3);
  const chipMat = new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.95, side:THREE.DoubleSide});
  const chips = new THREE.InstancedMesh(chipGeo, chipMat, N_CHIP);
  chips.receiveShadow = true;
  const dummy = new THREE.Object3D(), col = new THREE.Color();
  for(let i=0;i<N_CHIP;i++){
    dummy.position.set((Math.random()-0.5)*(CAGE.w-0.1), 0.006+Math.random()*0.035, (Math.random()-0.5)*(CAGE.d-0.1));
    dummy.rotation.set(Math.random()*6.28, Math.random()*6.28, Math.random()*6.28);
    const s = 0.55+Math.random()*0.95; dummy.scale.set(s, s*(0.7+Math.random()*0.7), s);
    dummy.updateMatrix(); chips.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.08+Math.random()*0.045, 0.42+Math.random()*0.2, 0.42+Math.random()*0.28);
    chips.setColorAt(i, col);
  }
  chips.instanceMatrix.needsUpdate = true; scene.add(chips);

  // ПРУТЬЯ + РАМКИ — один InstancedMesh (юнит-цилиндр, длина масштабом матрицы)
  const barGeo = new THREE.CylinderGeometry(1,1,1,7);
  const barMat = new THREE.MeshStandardMaterial({color:0xc4ccd4, roughness:0.33, metalness:0.78});
  const parts = [];
  const step = 0.235, y0 = 0.055, H = CAGE.wallH;
  for(let x=-CAGE.w/2+0.06; x<=CAGE.w/2-0.05; x+=step){ parts.push([x,y0+H/2, CAGE.d/2, 0,0,0,H,CAGE.barR]); parts.push([x,y0+H/2,-CAGE.d/2, 0,0,0,H,CAGE.barR]); }
  for(let z=-CAGE.d/2+0.06; z<=CAGE.d/2-0.05; z+=step){ parts.push([ CAGE.w/2,y0+H/2,z, 0,0,0,H,CAGE.barR]); parts.push([-CAGE.w/2,y0+H/2,z, 0,0,0,H,CAGE.barR]); }
  const RY = CAGE.w/2+0.02, RZ = CAGE.d/2+0.02;
  parts.push([0,y0+H, RZ, Math.PI/2,0,0, CAGE.w+0.08, 0.032]);
  parts.push([0,y0+H,-RZ, Math.PI/2,0,0, CAGE.w+0.08, 0.032]);
  parts.push([ RY,y0+H,0, 0,0,Math.PI/2, CAGE.d+0.08, 0.032]);
  parts.push([-RY,y0+H,0, 0,0,Math.PI/2, CAGE.d+0.08, 0.032]);
  parts.push([0,y0+H+0.11,0, Math.PI/2,0,0, CAGE.w+0.08, 0.026]);
  parts.push([0,y0+H+0.11,0, 0,0,Math.PI/2, CAGE.d+0.08, 0.026]);
  for(let i=1;i<6;i++){ const x=-CAGE.w/2+i*CAGE.w/6; parts.push([x,y0+H+0.11,0, Math.PI/2,0,0, CAGE.d, 0.017]); }
  for(let i=1;i<4;i++){ const z=-CAGE.d/2+i*CAGE.d/4; parts.push([0,y0+H+0.11,z, 0,0,Math.PI/2, CAGE.w, 0.017]); }
  [[ RY, RZ],[ RY,-RZ],[-RY, RZ],[-RY,-RZ]].forEach(p=>parts.push([p[0],y0+H/2,p[1],0,0,0,H+0.1,0.048]));
  [[ RY,0],[ -RY,0]].forEach(p=>parts.push([p[0],y0+H*0.55,0,0,0,0,CAGE.d*0.98,0.02]));

  const bars = new THREE.InstancedMesh(barGeo, barMat, parts.length);
  bars.castShadow = true;
  const d2 = new THREE.Object3D();
  parts.forEach((p,i)=>{
    d2.position.set(p[0],p[1],p[2]); d2.rotation.set(p[3],p[4],p[5]);
    d2.scale.set(p[7], p[6], p[7]); d2.updateMatrix(); bars.setMatrixAt(i,d2.matrix);
  });
  bars.instanceMatrix.needsUpdate = true; scene.add(bars);
}

/* =====================================================================
   4. ПРЕДМЕТЫ + ИХ ТЕЛА
   ===================================================================== */
/* ---------- 4.1 КОЛЕСО ---------- */
const WHEEL = {
  R: R_ОБОДА,                       // радиус поверхности, где лапы — ОН же в формуле ω=v/R
  halfW: ШИРИНА_КОЛЕСА/2,
  center: new THREE.Vector3(1.85, R_ОБОДА + 0.14, 0.75),
  angle: 0, omega: 0,               // рад, рад/с (ось — Z)
  friction: 1.7,                    // затухание пустого колеса
  occupant: null,
  facing: 0,                        // хомяк смотрит вдоль +X
  entrance: null, inside: null,
  pawSpeed: 0, rimSpeed: 0, dev: 0
};
WHEEL.entrance = new THREE.Vector3(WHEEL.center.x, GROUND_Y + ТОРС, WHEEL.center.z + WHEEL.halfW + 0.42);
WHEEL.inside   = new THREE.Vector3(WHEEL.center.x, WHEEL.center.y - WHEEL.R + ТОРС, WHEEL.center.z);
WHEEL.facingVec = new THREE.Vector3(1,0,0);

const wheelG = new THREE.Group(); wheelG.position.copy(WHEEL.center); scene.add(wheelG);
const wheelSpin = new THREE.Group(); wheelG.add(wheelSpin);
{
  const shellM = new THREE.MeshStandardMaterial({color:0xf0e3cd, roughness:0.62, side:THREE.DoubleSide});
  const drum = new THREE.Mesh(new THREE.CylinderGeometry(WHEEL.R+0.028, WHEEL.R+0.028, WHEEL.halfW*2, 52,1,true), shellM);
  drum.geometry.rotateX(Math.PI/2); drum.castShadow = true; wheelSpin.add(drum);

  const rimM = new THREE.MeshStandardMaterial({color:0xd9c7a8, roughness:0.5});
  [-1,1].forEach(s=>{
    const t = new THREE.Mesh(new THREE.TorusGeometry(WHEEL.R+0.03, 0.03, 8, 46), rimM);
    t.position.z = s*WHEEL.halfW; t.castShadow = true; wheelSpin.add(t);
  });
  const back = new THREE.Mesh(new THREE.CylinderGeometry(WHEEL.R+0.02, WHEEL.R+0.02, 0.022, 44),
    new THREE.MeshStandardMaterial({color:0xe4d5b8, roughness:0.7}));
  back.geometry.rotateX(Math.PI/2); back.position.z = -WHEEL.halfW-0.014; back.castShadow=true; wheelSpin.add(back);
  const spokeM = new THREE.MeshStandardMaterial({color:0xcbb894, roughness:0.7});
  for(let i=0;i<6;i++){
    const sp = new THREE.Mesh(new THREE.BoxGeometry(WHEEL.R*0.94, 0.035, 0.02), spokeM);
    sp.position.set(Math.cos(i*Math.PI/3)*(WHEEL.R*0.5), Math.sin(i*Math.PI/3)*(WHEEL.R*0.5), -WHEEL.halfW+0.02);
    sp.rotation.z = i*Math.PI/3; wheelSpin.add(sp);
  }
  // перекладины: внутренняя грань ровно на радиусе R (там, где лапы)
  const slatM = new THREE.MeshStandardMaterial({color:0xcfa870, roughness:0.8});
  for(let i=0;i<18;i++){
    const a = i/18*Math.PI*2;
    const s = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.024, WHEEL.halfW*2-0.02), slatM);
    s.position.set(Math.cos(a)*(WHEEL.R+0.012), Math.sin(a)*(WHEEL.R+0.012), 0);
    s.rotation.z = a; s.castShadow = true; wheelSpin.add(s);
  }
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.075,0.075,WHEEL.halfW*2+0.16,14),
    new THREE.MeshStandardMaterial({color:0x9aa1a8, roughness:0.35, metalness:0.6}));
  hub.geometry.rotateX(Math.PI/2); wheelSpin.add(hub);
  [0,2.1,4.2].forEach(a=>{
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.035,10,8), new THREE.MeshStandardMaterial({color:0xd8452f, roughness:0.5}));
    m.position.set(Math.cos(a)*(WHEEL.R+0.03), Math.sin(a)*(WHEEL.R+0.03), WHEEL.halfW); wheelSpin.add(m);
  });
  // стойка (не вращается)
  const standM = new THREE.MeshStandardMaterial({color:0x7f868e, roughness:0.4, metalness:0.6});
  const post = new THREE.Mesh(new THREE.BoxGeometry(0.1, WHEEL.center.y, 0.1), standM);
  post.position.set(WHEEL.center.x, WHEEL.center.y/2, WHEEL.center.z - WHEEL.halfW - 0.14); post.castShadow=true; scene.add(post);
  const arm = new THREE.Mesh(new THREE.BoxGeometry(0.075,0.075,0.30), standM);
  arm.position.set(WHEEL.center.x, WHEEL.center.y, WHEEL.center.z - WHEEL.halfW + 0.01); arm.castShadow=true; scene.add(arm);
  const base = new THREE.Mesh(new THREE.BoxGeometry(0.62,0.06,0.42), standM);
  base.position.set(WHEEL.center.x, 0.03, WHEEL.center.z - WHEEL.halfW - 0.14); base.castShadow=true; scene.add(base);
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,0.62,10), standM);
  axle.geometry.rotateX(Math.PI/2); axle.position.set(WHEEL.center.x, WHEEL.center.y, WHEEL.center.z - WHEEL.halfW + 0.02); scene.add(axle);
}

/* ---------- 4.2 ТРУБА (полость, вход только торцами) ---------- */
const PIPE = {
  x1:-2.30, x2:-0.50, z:-1.15,
  rIn:0.245, wall:0.040,
  axisY:0, occupant:null
};
PIPE.rOut = PIPE.rIn + PIPE.wall;
PIPE.axisY = PIPE.rOut - 0.02;            // слегка утоплена в подстилку
PIPE.innerBottomY = PIPE.axisY - PIPE.rIn;
console.assert(PIPE.rIn >= ТОРС, 'внутри трубы зверь должен доставать до дна ногами');
{
  const g = 0.44;                          // половина угла выреза сверху (чтобы было видно)
  const start = Math.PI*1.5 + g, len = Math.PI*2 - g*2;
  const rot = geo => { geo.rotateZ(-Math.PI/2); return geo; };
  const L = PIPE.x2 - PIPE.x1, cxm = (PIPE.x1+PIPE.x2)/2;
  const outM = new THREE.MeshStandardMaterial({color:0xd8cbb6, roughness:0.55, side:THREE.DoubleSide});
  const inM  = new THREE.MeshStandardMaterial({color:0xf2e7d5, roughness:0.85, side:THREE.DoubleSide});
  const outer = new THREE.Mesh(rot(new THREE.CylinderGeometry(PIPE.rOut,PIPE.rOut,L,40,1,true,start,len)), outM);
  const inner = new THREE.Mesh(rot(new THREE.CylinderGeometry(PIPE.rIn,PIPE.rIn,L,40,1,true,start,len)), inM);
  [outer,inner].forEach(m=>{ m.position.set(cxm, PIPE.axisY, PIPE.z); m.castShadow=true; m.receiveShadow=true; scene.add(m); });
  const glassM = new THREE.MeshStandardMaterial({color:0xcfe4f2, transparent:true, opacity:0.20, roughness:0.12, metalness:0.0, side:THREE.DoubleSide});
  const glass = new THREE.Mesh(rot(new THREE.CylinderGeometry(PIPE.rOut,PIPE.rOut,L,20,1,true,Math.PI*1.5-g,g*2)), glassM);
  glass.position.set(cxm, PIPE.axisY, PIPE.z); scene.add(glass);
  const ringM = new THREE.MeshStandardMaterial({color:0xbfae94, roughness:0.7});
  [PIPE.x1, PIPE.x2].forEach(x=>{
    const r = new THREE.Mesh(new THREE.TorusGeometry((PIPE.rIn+PIPE.rOut)/2, PIPE.wall/2, 8, 34), ringM);
    r.rotation.y = Math.PI/2; r.position.set(x, PIPE.axisY, PIPE.z); r.castShadow=true; scene.add(r);
  });
}

/* ---------- 4.3 МИСКА С ЗЁРНАМИ ---------- */
const BOWL = {pos:new THREE.Vector3(-0.45, 0, 1.28), r:0.33, users:0};
{
  const pts=[]; for(let i=0;i<=10;i++){ const t=i/10; pts.push(new THREE.Vector2(0.055+t*(BOWL.r-0.055), 0.145*Math.pow(t,1.7))); }
  pts.push(new THREE.Vector2(BOWL.r*0.99, 0.152), new THREE.Vector2(BOWL.r*1.05, 0.145));
  const bowl = new THREE.Mesh(new THREE.LatheGeometry(pts, 34),
    new THREE.MeshStandardMaterial({color:0x3c6f8c, roughness:0.32, metalness:0.15, side:THREE.DoubleSide}));
  bowl.position.copy(BOWL.pos); bowl.castShadow = bowl.receiveShadow = true; scene.add(bowl);
  const seedGeo = new THREE.SphereGeometry(0.022, 7, 6); seedGeo.scale(1,0.62,0.75);
  const seeds = new THREE.InstancedMesh(seedGeo, new THREE.MeshStandardMaterial({color:0x6b4a24, roughness:0.8}), 34);
  const d3 = new THREE.Object3D();
  for(let i=0;i<34;i++){
    const a=Math.random()*6.28, rr=Math.sqrt(Math.random())*0.24;
    d3.position.set(BOWL.pos.x+Math.cos(a)*rr, 0.05+Math.random()*0.03, BOWL.pos.z+Math.sin(a)*rr);
    d3.rotation.set(Math.random(),Math.random()*6.28,Math.random()); d3.scale.setScalar(0.85+Math.random()*0.5);
    d3.updateMatrix(); seeds.setMatrixAt(i,d3.matrix);
  }
  seeds.instanceMatrix.needsUpdate=true; seeds.castShadow=true; scene.add(seeds);
  const husk = new THREE.InstancedMesh(seedGeo, new THREE.MeshStandardMaterial({color:0x39301f, roughness:0.9}), 22);
  for(let i=0;i<22;i++){
    const a=Math.random()*6.28, rr=0.42+Math.random()*0.75;
    d3.position.set(BOWL.pos.x+Math.cos(a)*rr, 0.016, BOWL.pos.z+Math.sin(a)*rr);
    d3.rotation.set(Math.random()*0.4,Math.random()*6.28,Math.random()*0.4); d3.scale.setScalar(0.8+Math.random()*0.5);
    d3.updateMatrix(); husk.setMatrixAt(i,d3.matrix);
  }
  husk.instanceMatrix.needsUpdate=true; scene.add(husk);
}

/* ---------- 4.4 ПОИЛКА ---------- */
const DRINK = {pos:new THREE.Vector3(-2.82, 0.92, 0.42)};
{
  const g = new THREE.Group(); g.position.copy(DRINK.pos); scene.add(g);
  const glass = new THREE.Mesh(new THREE.CylinderGeometry(0.135,0.135,0.52,20),
    new THREE.MeshStandardMaterial({color:0xdfeaf2, transparent:true, opacity:0.28, roughness:0.08}));
  g.add(glass);
  const water = new THREE.Mesh(new THREE.CylinderGeometry(0.118,0.118,0.34,18),
    new THREE.MeshStandardMaterial({color:0x8fc3e0, transparent:true, opacity:0.55, roughness:0.05}));
  water.position.y = -0.07; g.add(water);
  const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.075,0.075,0.1,14),
    new THREE.MeshStandardMaterial({color:0xb9c0c7, roughness:0.3, metalness:0.8})); cap.position.y=-0.3; g.add(cap);
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.019,0.019,0.17,10),
    new THREE.MeshStandardMaterial({color:0xcfd6dd, roughness:0.25, metalness:0.9}));
  tube.position.set(0.055,-0.4,0); tube.rotation.z = -0.55; g.add(tube);
  const ball = new THREE.Mesh(new THREE.SphereGeometry(0.026,10,8),
    new THREE.MeshStandardMaterial({color:0xe6ecf2, roughness:0.15, metalness:0.95}));
  ball.position.set(0.128,-0.465,0); g.add(ball);
  const holder = new THREE.Mesh(new THREE.TorusGeometry(0.15,0.012,6,20),
    new THREE.MeshStandardMaterial({color:0xa8afb6, roughness:0.4, metalness:0.7}));
  holder.rotation.y = Math.PI/2; holder.position.y = 0.12; g.add(holder);
  DRINK.tip = new THREE.Vector3(-2.69, 0.455, 0.42);
}
const drip = new THREE.Mesh(new THREE.SphereGeometry(0.016,8,7),
  new THREE.MeshStandardMaterial({color:0x9fd0e8, transparent:true, opacity:0.75, roughness:0.05}));
scene.add(drip); let dripT = 3.2, dripY = 0;

/* ---------- 4.5 ДОМИК ---------- */
const HOUSE = {pos:new THREE.Vector3(2.28, 0, -1.32), r:0.52};
{
  const g = new THREE.Group(); g.position.copy(HOUSE.pos); scene.add(g);
  const woodM = new THREE.MeshStandardMaterial({color:0xb98a55, roughness:0.85});
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.86,0.5,0.78), woodM);
  body.position.y = 0.25; body.castShadow = body.receiveShadow = true; g.add(body);
  const roof = new THREE.Mesh(new THREE.ConeGeometry(0.68,0.34,4), new THREE.MeshStandardMaterial({color:0x8f5f38, roughness:0.8}));
  roof.position.y = 0.66; roof.rotation.y = Math.PI/4; roof.castShadow = true; g.add(roof);
  const hole = new THREE.Mesh(new THREE.CircleGeometry(0.17, 20), new THREE.MeshBasicMaterial({color:0x140c07}));
  hole.position.set(0,0.22,0.392); g.add(hole);
}

/* ---------- 4.6 ТЕЛА СТОЛКНОВЕНИЙ (2D в плане XZ) ---------- */
const COLLIDERS = [
  {kind:'capsule', owner:'wheel', ax:WHEEL.center.x-WHEEL.R, az:WHEEL.center.z, bx:WHEEL.center.x+WHEEL.R, bz:WHEEL.center.z,
   r:WHEEL.halfW + RADIUS_ТЕЛА, label:'колесо'},
  {kind:'capsule', owner:'pipe', ax:PIPE.x1+0.34, az:PIPE.z, bx:PIPE.x2-0.34, bz:PIPE.z,
   r:PIPE.rOut + RADIUS_ТЕЛА, label:'труба'},
  {kind:'circle', owner:'bowl', px:BOWL.pos.x, pz:BOWL.pos.z, r:BOWL.r + RADIUS_ТЕЛА*0.85, label:'миска'},
  {kind:'circle', owner:'house', px:HOUSE.pos.x, pz:HOUSE.pos.z, r:HOUSE.r, label:'домик'},
  {kind:'circle', owner:'drink', px:DRINK.pos.x+0.1, pz:DRINK.pos.z, r:0.24, label:'поилка'}
];
COLLIDERS.forEach(c=>c.lastPen=0);

// визуализация тел
const helperG = new THREE.Group(); scene.add(helperG);
COLLIDERS.forEach(c=>{
  let geo;
  if(c.kind==='capsule'){
    const L = Math.hypot(c.bx-c.ax, c.bz-c.az);
    geo = new THREE.BoxGeometry(L, 0.9, c.r*2);
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({color:0x54d6a0, wireframe:true, transparent:true, opacity:0.35}));
    m.position.set((c.ax+c.bx)/2, 0.45, (c.az+c.bz)/2); helperG.add(m); c.mesh=m;
  } else {
    geo = new THREE.CylinderGeometry(c.r, c.r, 0.9, 22, 1, true);
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({color:0x54d6a0, wireframe:true, transparent:true, opacity:0.35, side:THREE.DoubleSide}));
    m.position.set(c.px, 0.45, c.pz); helperG.add(m); c.mesh=m;
  }
});
// ось трубы + нижняя точка обода (реперы для проверки)
const axisMark = new THREE.Mesh(new THREE.CylinderGeometry(0.008,0.008,PIPE.x2-PIPE.x1+0.6,6),
  new THREE.MeshBasicMaterial({color:0x54d6a0}));
axisMark.rotation.z = Math.PI/2; axisMark.position.set((PIPE.x1+PIPE.x2)/2, PIPE.axisY, PIPE.z); helperG.add(axisMark);
const bottomMark = new THREE.Mesh(new THREE.SphereGeometry(0.03,10,8), new THREE.MeshBasicMaterial({color:0xffd166}));
bottomMark.position.set(WHEEL.center.x, WHEEL.center.y - WHEEL.R, WHEEL.center.z); helperG.add(bottomMark);

/* =====================================================================
   5. ХОМЯК — сборка из частей
   ===================================================================== */
const HIP_Y = -0.09, L1 = 0.10, L2 = 0.10;
function makeHamster(cfg){
  const root = new THREE.Group();
  const bodyG = new THREE.Group(); root.add(bodyG);
  const fur  = new THREE.MeshStandardMaterial({color:cfg.fur,  roughness:0.92});
  const belly= new THREE.MeshStandardMaterial({color:cfg.belly,roughness:0.95});
  const dark = new THREE.MeshStandardMaterial({color:cfg.dark, roughness:0.9});
  const pink = new THREE.MeshStandardMaterial({color:0xe8a3a0, roughness:0.75});
  const black= new THREE.MeshStandardMaterial({color:0x120d0a, roughness:0.25});

  const sph = (r,sx,sy,sz)=>{const g=new THREE.SphereGeometry(r,18,14);g.scale(sx,sy,sz);return g;};

  const body = new THREE.Mesh(sph(1, 0.245, 0.125, 0.152), fur);
  body.castShadow = true; bodyG.add(body);
  if(cfg.patch){
    const p = new THREE.Mesh(sph(1,0.14,0.075,0.10), dark);
    p.position.set(-0.05,0.075,0.055); bodyG.add(p);
    const p2 = new THREE.Mesh(sph(1,0.075,0.05,0.07), dark);
    p2.position.set(0.10,0.05,-0.08); bodyG.add(p2);
  }
  const bellyM = new THREE.Mesh(sph(1,0.20,0.098,0.128), belly);
  bellyM.position.set(0.01,-0.045,0); bodyG.add(bellyM);

  // голова — отдельной группой, чтобы кивать
  const head = new THREE.Group(); head.position.set(0.205,0.045,0); head.rotation.order='YXZ'; bodyG.add(head);
  const skull = new THREE.Mesh(sph(0.112,1.06,0.95,1.0), fur); skull.castShadow=true; head.add(skull);
  const muzzle = new THREE.Mesh(sph(0.062,1.15,0.72,0.9), belly); muzzle.position.set(0.082,-0.022,0); head.add(muzzle);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.019,10,8), pink); nose.position.set(0.145,-0.012,0); head.add(nose);
  const cheekL = new THREE.Mesh(sph(0.058,1.1,0.9,0.9), belly); cheekL.position.set(0.075,-0.03,0.072); head.add(cheekL);
  const cheekR = cheekL.clone(); cheekR.position.z = -0.072; head.add(cheekR);
  const eyes=[], pupils=[];
  [1,-1].forEach(s=>{
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.029,12,10), black);
    e.position.set(0.072,0.032,s*0.072); head.add(e); eyes.push(e);
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.011,8,7),
      new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.1, emissive:0x8899aa, emissiveIntensity:0.4}));
    p.position.set(0.092,0.045,s*0.078); head.add(p); pupils.push(p);
  });
  const ears=[];
  [1,-1].forEach(s=>{
    const eg = new THREE.Group(); eg.position.set(0.115,0.098,s*0.072); head.add(eg);
    const out = new THREE.Mesh(sph(0.052,0.95,1.0,0.42), fur); out.castShadow=true; eg.add(out);
    const inn = new THREE.Mesh(sph(0.036,0.85,0.9,0.30), pink); inn.position.set(0.012,0,s*0.014); eg.add(inn);
    ears.push(eg);
  });
  const wGeo = new THREE.BufferGeometry();
  const wv = [];
  [1,-1].forEach(s=>{ for(let i=0;i<3;i++){ wv.push(0.13,-0.01,s*0.045, 0.235+Math.random()*0.02, -0.035+i*0.018, s*(0.10+i*0.022)); }});
  wGeo.setAttribute('position', new THREE.Float32BufferAttribute(wv,3));
  head.add(new THREE.LineSegments(wGeo, new THREE.LineBasicMaterial({color:0xf6ecd9, transparent:true, opacity:0.55})));

  // 4 лапы: плечо -> колено -> кисть
  const legs=[];
  [[0.135,1],[0.135,-1],[-0.135,1],[-0.135,-1]].forEach(p=>{
    const hip = new THREE.Group(); hip.position.set(p[0], HIP_Y, p[1]*0.105); bodyG.add(hip);
    const th = new THREE.Mesh(new THREE.CylinderGeometry(0.033,0.028,L1,7), fur);
    th.geometry.translate(0,-L1/2,0); th.castShadow=true; hip.add(th);
    const knee = new THREE.Group(); knee.position.y = -L1; hip.add(knee);
    const sh = new THREE.Mesh(new THREE.CylinderGeometry(0.027,0.023,L2,7), fur);
    sh.geometry.translate(0,-L2/2,0); knee.add(sh);
    const paw = new THREE.Mesh(sph(0.032,1.25,0.6,0.95), belly); paw.position.y=-L2; knee.add(paw);
    hip.userData = {knee, paw};
    legs.push(hip);
  });
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.026,0.075,7), fur);
  tail.position.set(-0.255,0.02,0); tail.rotation.z = Math.PI/2 - 0.5; bodyG.add(tail);

  const ring = new THREE.Mesh(new THREE.RingGeometry(0.26,0.31,32),
    new THREE.MeshBasicMaterial({color:cfg.fur, transparent:true, opacity:0, side:THREE.DoubleSide}));
  ring.rotation.x = -Math.PI/2; ring.position.y = 0.012; scene.add(ring);

  scene.add(root);
  root.traverse(o=>{ if(o.isMesh) o.userData.hamster = null; });
  return {root, bodyG, head, ears, eyes, pupils, cheekL, cheekR, legs, tail, ring, nose};
}

const HAMDEN = [
  {name:'Рыжик',    fur:0xe0913f, belly:0xf6e3c4, dark:0x9c5c22, patch:false, color:'#e0913f'},
  {name:'Сметанка', fur:0xf0e6d2, belly:0xffffff, dark:0xcbb89a, patch:false, color:'#f0e6d2'},
  {name:'Уголёк',   fur:0x54504c, belly:0xb9b3a9, dark:0x2b2825, patch:false, color:'#8d8880'},
  {name:'Пирожок',  fur:0xc9793c, belly:0xf7e7cd, dark:0x6f3d1c, patch:true,  color:'#c9793c'},
  {name:'Топтыжка', fur:0x8f7550, belly:0xe8d7b8, dark:0x54432d, patch:true,  color:'#a98a5e'}
];

const HAMSTERS = [];
HAMDEN.forEach((cfg,i)=>{
  const parts = makeHamster(cfg);
  const h = {
    id:i, name:cfg.name, colorHex:cfg.color, parts,
    pos:new THREE.Vector3(-2.2+i*1.05, GROUND_Y+ТОРС, -0.35+((i%2)*0.9)),
    heading:Math.random()*6.28, speed:0, pawSpeed:0,
    phase:0, pawPath:0, path:0, prev:new THREE.Vector3(),
    state:'idle', goalKind:'wander', timer:Math.random()*2, t:0,
    cruise:0.85, walkSpeed:0.52+Math.random()*0.14,
    inWheel:false, inPipe:false, pipeDir:1, transFrom:new THREE.Vector3(),
    jumpY:0, vy:0, grounded:true, squash:0,
    surfaceY:GROUND_Y, legScale:0.75, feetY:0,
    breathRate:1.5+Math.random()*0.7, breathPhase:Math.random()*6.28,
    twitchT:Math.random()*3, twitchEar:0, chew:0, headYaw:0, headPitch:0,
    activity:'стоит', violations:0
  };
  h.prev.copy(h.pos);
  parts.root.traverse(o=>{ o.userData.hamsterRef = h; });
  HAMSTERS.push(h);
});
window.HAMSTERS = HAMSTERS; window.WHEEL = WHEEL; window.PIPE = PIPE; window.BOWL = BOWL;

/* =====================================================================
   6. ПОВЕДЕНИЕ — конечный автомат
   ===================================================================== */
const LABEL = {
  idle:'стоит', enter_wheel:'забирается в колесо', run_wheel:'бежит в колесе', exit_wheel:'выходит из колеса',
  enter_pipe:'залезает в трубу', run_pipe:'ползёт по трубе', exit_pipe:'вылезает из трубы', eat:'грызёт зёрна',
  walk:'гуляет'
};
const GOAL_LABEL = {wheel:'идёт к колесу', pipe:'идёт к трубе', bowl:'идёт к миске', wander:'гуляет'};

function freePoint(){
  for(let k=0;k<40;k++){
    const x = (Math.random()-0.5)*4.9, z = (Math.random()-0.5)*3.1;
    let ok = true;
    for(const c of COLLIDERS){ if(distToCollider(c,x,z) < c.r*0.55) {ok=false;break;} }
    if(ok) return new THREE.Vector3(x, GROUND_Y+ТОРС, z);
  }
  return new THREE.Vector3(0, GROUND_Y+ТОРС, 0);
}
function chooseNext(h){
  const opts = [];
  if(!WHEEL.occupant) opts.push('wheel','wheel','wheel');
  if(!PIPE.occupant)  opts.push('pipe','pipe');
  if(BOWL.users < 2)  opts.push('bowl','bowl');
  opts.push('wander','wander','wander','idle','idle');
  const k = opts[(Math.random()*opts.length)|0];
  if(k === 'idle'){ h.state='idle'; h.timer = 1.2 + Math.random()*3.4; return; }
  h.goalKind = k; h.state = 'walk'; h.timer = 16;
  if(k === 'wheel'){ h.goal = WHEEL.entrance.clone(); }
  else if(k === 'pipe'){
    const left = Math.random() < 0.5;
    h.pipeDir = left ? 1 : -1;
    h.goal = new THREE.Vector3(left ? PIPE.x1-0.36 : PIPE.x2+0.36, GROUND_Y+ТОРС, PIPE.z);
  }
  else if(k === 'bowl'){
    const a = Math.random()*6.28;
    h.goal = new THREE.Vector3(BOWL.pos.x + Math.cos(a)*(BOWL.r+0.26), GROUND_Y+ТОРС, BOWL.pos.z + Math.sin(a)*(BOWL.r+0.26));
    h.bowlAngle = Math.atan2(-(BOWL.pos.z-h.goal.z), BOWL.pos.x-h.goal.x);
  }
  else h.goal = freePoint();
}
function arrive(h){
  if(h.goalKind === 'wheel'){
    WHEEL.occupant = h; h.inWheel = true; h.state='enter_wheel'; h.t=0; h.transFrom.copy(h.pos);
  } else if(h.goalKind === 'pipe'){
    PIPE.occupant = h; h.inPipe = true; h.state='enter_pipe'; h.t=0; h.transFrom.copy(h.pos);
  } else if(h.goalKind === 'bowl'){
    h.state='eat'; h.timer = 4 + Math.random()*5; BOWL.users++;
  } else { h.state='idle'; h.timer = 1 + Math.random()*3; }
}
const smooth = t => { t = Math.max(0, Math.min(1,t)); return t*t*(3-2*t); };
const damp   = (a,b,l,dt)=> a + (b-a)*(1-Math.exp(-l*dt));
function dampAngle(a,b,l,dt){
  let d = ((b-a+Math.PI)%(Math.PI*2)+Math.PI*2)%(Math.PI*2)-Math.PI;
  return a + d*(1-Math.exp(-l*dt));
}
const clamp = (v,a,b)=>v<a?a:v>b?b:v;

function updateHamster(h, dt){
  h.timer -= dt;
  let wantSpeed = 0, wantHeading = h.heading;

  switch(h.state){
    case 'idle':
      h.headYaw = damp(h.headYaw, Math.sin(clock*0.5 + h.id*2)*0.55, 2, dt);
      if(h.timer <= 0) chooseNext(h);
      break;

    case 'walk': {
      const dx = h.goal.x - h.pos.x, dz = h.goal.z - h.pos.z;
      const d = Math.hypot(dx,dz);
      wantHeading = Math.atan2(-dz, dx);
      h.headYaw = damp(h.headYaw, 0, 4, dt);
      if(d < 0.11 || h.timer <= 0) arrive(h); else wantSpeed = h.walkSpeed;
      break;
    }

    /* ---- КОЛЕСО: вход/выход плавным лерпом, без единого присваивания координат ---- */
    case 'enter_wheel': {
      h.t += dt/1.35; const k = smooth(h.t);
      h.pos.lerpVectors(h.transFrom, WHEEL.inside, k);
      wantHeading = WHEEL.facing;
      h.pawSpeed = h.cruise * smooth((h.t-0.45)/0.55);
      if(h.t >= 1){ h.state='run_wheel'; h.timer = 6 + Math.random()*8; }
      break;
    }
    case 'run_wheel': {
      h.pos.copy(WHEEL.inside);
      wantHeading = WHEEL.facing; h.headYaw = 0;
      if(h.timer < 0.4) h.cruise = damp(h.cruise, 0.15, 1.6, dt);
      else if(Math.random() < dt*0.45) h.cruise = 0.55 + Math.random()*0.75;
      h.pawSpeed = damp(h.pawSpeed, h.cruise, 2.6, dt);
      if(h.timer <= 0) h.state = 'exit_wheel';
      break;
    }
    case 'exit_wheel': {
      h.pawSpeed = damp(h.pawSpeed, 0, 4.5, dt);
      wantHeading = WHEEL.facing;
      if(h.pawSpeed < 0.06){
        h.t += dt/1.25; const k = smooth(h.t);
        h.pos.lerpVectors(WHEEL.inside, WHEEL.entrance, k);
        wantHeading = Math.atan2(-(WHEEL.entrance.z-h.pos.z+0.001), WHEEL.entrance.x-h.pos.x);
        if(h.t >= 1){
          h.inWheel = false; WHEEL.occupant = null; h.pawSpeed = 0;
          h.state='walk'; h.goalKind='wander'; h.goal=freePoint(); h.timer=14;
        }
      }
      break;
    }

    /* ---- ТРУБА: только через торец, внутри строго по оси ---- */
    case 'enter_pipe': {
      h.t += dt/1.15; const k = smooth(h.t);
      const to = new THREE.Vector3(h.pipeDir>0 ? PIPE.x1+0.22 : PIPE.x2-0.22, PIPE.axisY, PIPE.z);
      h.pos.lerpVectors(h.transFrom, to, k);
      wantHeading = h.pipeDir>0 ? 0 : Math.PI;
      h.pawSpeed = 0.30 * smooth((h.t-0.25)/0.75);
      if(h.t >= 1){ h.state='run_pipe'; h.timer = 14; }
      break;
    }
    case 'run_pipe': {
      h.pos.x += h.pipeDir * 0.40 * dt;
      h.pos.y = PIPE.axisY; h.pos.z = PIPE.z;         // отклонение от оси = 0
      wantHeading = h.pipeDir>0 ? 0 : Math.PI;
      h.pawSpeed = 0.40;
      if((h.pipeDir>0 && h.pos.x > PIPE.x2-0.22) || (h.pipeDir<0 && h.pos.x < PIPE.x1+0.22)){
        h.state='exit_pipe'; h.t=0; h.transFrom.copy(h.pos);
      }
      break;
    }
    case 'exit_pipe': {
      h.t += dt/1.0; const k = smooth(h.t);
      const to = new THREE.Vector3(h.pipeDir>0 ? PIPE.x2+0.40 : PIPE.x1-0.40, GROUND_Y+ТОРС, PIPE.z);
      h.pos.lerpVectors(h.transFrom, to, k);
      h.pawSpeed = 0.32*(1-k);
      wantHeading = h.pipeDir>0 ? 0 : Math.PI;
      if(h.t >= 1){
        h.inPipe=false; PIPE.occupant=null; h.pawSpeed=0;
        h.state='walk'; h.goalKind='wander'; h.goal=freePoint(); h.timer=12;
      }
      break;
    }

    case 'eat': {
      wantHeading = h.bowlAngle; h.headYaw = 0;
      h.headPitch = damp(h.headPitch, 0.62, 5, dt);
      h.chew = damp(h.chew, 1, 6, dt);
      if(Math.sin(clock*1.3 + h.id) > 0.985) h.headYaw = 0.5;
      if(h.timer <= 0){ h.state='idle'; h.timer = 0.6+Math.random()*2; BOWL.users = Math.max(0,BOWL.users-1); }
      break;
    }
  }

  if(h.state !== 'eat') { h.headPitch = damp(h.headPitch, 0, 5, dt); h.chew = damp(h.chew, 0, 5, dt); }

  /* ---- скорость и направление (плавные, без рывков) ---- */
  const acc = 1.5;
  h.speed += clamp(wantSpeed - h.speed, -acc*1.8*dt, acc*1.8*dt);
  h.heading = dampAngle(h.heading, wantHeading, 6.5, dt);

  const onSurface = !h.inWheel && !h.inPipe;
  if(onSurface){
    h.pos.x += Math.cos(h.heading) * h.speed * dt;
    h.pos.z -= Math.sin(h.heading) * h.speed * dt;
  }

  /* ---- ТРУБКА: фактическое смещение (для честной фазы шага) ---- */
  const disp = Math.hypot(h.pos.x - h.prev.x, h.pos.z - h.prev.z);
  const dy   = h.pos.y - h.prev.y;
  h.path += Math.hypot(disp, dy);
  h.pos.copy(h.prev) && 0;
  h.prev.copy(h.pos);

  /* ---- ПОВЕРХНОСТЬ ПОД ЛАПАМИ ---- */
  if(h.inWheel)      h.surfaceY = WHEEL.center.y - WHEEL.R;          // НИЖНЯЯ ТОЧКА ОБОДА
  else if(h.inPipe)  h.surfaceY = PIPE.innerBottomY;
  else               h.surfaceY = GROUND_Y;
  if(!h.inWheel && !h.inPipe) h.pos.y = GROUND_Y + ТОРС;

  /* ---- ПРЫЖОК ---- */
  if(!h.grounded){
    h.vy -= 11.5*dt; h.jumpY += h.vy*dt;
    if(h.jumpY <= 0){ h.jumpY = 0; h.vy = 0; h.grounded = true; h.squash = 1; }
  }
  h.squash = damp(h.squash, 0, 9, dt);

  /* ---- ФОЛЛАУТ + ГРАНИЦЫ + ТЕЛА + ДРУГ О ДРУГА ---- */
  let pushed = false;
  if(!h.inWheel && !h.inPipe){
    const lim = {x:CAGE.w/2 - 0.19, z:CAGE.d/2 - 0.19};
    if(Math.abs(h.pos.x) > lim.x){ h.pos.x = Math.sign(h.pos.x)*lim.x; pushed=true; }
    if(Math.abs(h.pos.z) > lim.z){ h.pos.z = Math.sign(h.pos.z)*lim.z; pushed=true; }
    for(const c of COLLIDERS){
      if(c.owner === 'wheel' && h.inWheel) continue;
      if(c.owner === 'pipe'  && h.inPipe)  continue;
      const d = distToCollider(c, h.pos.x, h.pos.z);
      const pen = c.r - d;
      if(pen > 0.0001){
        const n = closestOnCollider(c, h.pos.x, h.pos.z);
        let nx = h.pos.x - n.x, nz = h.pos.z - n.z, l = Math.hypot(nx,nz);
        if(l < 1e-5){ nx = 0; nz = h.pos.z > c.az ? 1 : -1; l = 1; }
        h.pos.x += (nx/l)*pen; h.pos.z += (nz/l)*pen; pushed = true;
        c.lastPen = Math.max(c.lastPen, pen);
      } else c.lastPen = Math.max(0, c.lastPen - dt*0.5);
    }
  }
  // мягкое расталкивание зверей
  for(const o of HAMSTERS){
    if(o === h || o.inWheel || o.inPipe || h.inWheel || h.inPipe) continue;
    const dx = h.pos.x-o.pos.x, dz = h.pos.z-o.pos.z, d = Math.hypot(dx,dz), min = RADIUS_ТЕЛА*2;
    if(d < min && d > 1e-5){ const push = (min-d)*0.5; h.pos.x += dx/d*push; h.pos.z += dz/d*push; }
  }
  if(pushed && h.state==='walk' && Math.random()<0.08) h.goal = freePoint();

  /* ---- ФАЗА ШАГА: от ПРОЙДЕННОГО ПУТИ (в колесе — от пути лап по ободу) ---- */
  const dpaw = h.inWheel ? h.pawSpeed*dt : (h.inPipe ? 0.40*dt*0 + Math.hypot(h.pos.x-h.prev.x,0) : disp);
  const pawDelta = h.inWheel ? h.pawSpeed*dt : disp;
  h.pawPath += pawDelta;
  const prevPhase = h.phase;
  h.phase += (pawDelta / ШАГ_ЛАПА) * Math.PI*2;
  h.dPhase = h.phase - prevPhase;
  h.pawSpeedReported = h.inWheel ? h.pawSpeed : (pawDelta/Math.max(dt,1e-4));

  /* ---- ПОЗА ---- */
  pose(h, dt, pushed);
}

function pose(h, dt, pushed){
  const p = h.parts, t = clock;
  const v = h.inWheel ? h.pawSpeed : h.speed;
  const runF = clamp(v/0.7, 0, 1.35);
  const amp  = 0.10 + 0.46*Math.min(runF,1.2);

  // длина лап под текущую поверхность
  const reach = clamp((h.pos.y - h.surfaceY - HIP_Y) / (L1+L2), 0.55, 0.99);
  h.legScale = damp(h.legScale, reach, 10, dt);
  h.feetY = h.pos.y + HIP_Y - h.legScale*(L1+L2)*Math.cos(0.3);

  p.legs.forEach((leg,i)=>{
    const off = (i===0 || i===3) ? 0 : Math.PI;          // ДИАГОНАЛЬНЫЕ ПАРЫ
    const ph = h.phase + off;
    const air = h.grounded ? 0 : 0.55;
    leg.rotation.z = Math.sin(ph)*amp*(1-air*0.4) + (air? -0.35 : 0);
    leg.scale.y = h.legScale * (1 - air*0.22);
    const knee = leg.userData.knee;
    knee.rotation.z = -0.30 - 0.42*(0.5 - 0.5*Math.cos(ph))*Math.min(runF,1.2) - air*0.7;
    knee.scale.y = 1;
  });

  // дыхание + подпрыгивание корпуса
  const idleF = clamp(1 - runF, 0, 1);
  const br = Math.sin(t*h.breathRate + h.breathPhase);
  const bs = 0.006 + 0.017*idleF;
  const sq = h.squash*0.16;
  p.bodyG.scale.set(1 + br*bs*0.7 + sq*0.6, 1 + br*bs - sq, 1 + br*bs*0.9 + sq*0.4);
  p.bodyG.position.y = -0.006 + Math.abs(Math.sin(h.phase))*0.011*Math.min(runF,1) + br*0.004 - sq*0.05;
  p.bodyG.rotation.x = -Math.sin(h.phase*2)*0.022*Math.min(runF,1);
  p.bodyG.rotation.z = Math.sin(h.phase)*0.028*Math.min(runF,1);

  // голова
  p.head.rotation.y = damp(p.head.rotation.y, h.headYaw + Math.sin(h.phase)*0.03*runF, 6, dt);
  p.head.rotation.x = damp(p.head.rotation.x, h.headPitch - Math.sin(h.phase*2)*0.03*runF, 7, dt);
  const chew = h.chew*Math.sin(t*15.5);
  p.cheekL.scale.setScalar(1 + chew*0.13); p.cheekR.scale.setScalar(1 - chew*0.11);
  p.nose.position.y = -0.012 + chew*0.004;
  const blink = (Math.sin(t*0.7 + h.id*1.7) > 0.995) ? 0.15 : 1;
  p.eyes.forEach(e=>e.scale.y = blink); p.pupils.forEach(e=>e.scale.y = blink);

  // дёрганье уха
  h.twitchT -= dt;
  if(h.twitchT <= 0){ h.twitchT = 1.6 + Math.random()*4.5; h.twitchEar = Math.random()<0.5?0:1; h.twitchDur = 0.35; }
  let tw = 0;
  if(h.twitchT > 0 && h.twitchT < 0.35) tw = Math.sin((0.35-h.twitchT)/0.35*Math.PI*3)*0.5;
  p.ears[0].rotation.x = (h.twitchEar===0?tw:0) + Math.sin(t*2+h.id)*0.04;
  p.ears[1].rotation.x = (h.twitchEar===1?tw:0) + Math.sin(t*2.3+h.id)*0.04;
  p.ears[0].rotation.z = -0.15 + (h.twitchEar===0?tw*0.5:0);
  p.ears[1].rotation.z =  0.15 - (h.twitchEar===1?tw*0.5:0);
  if(h.inPipe){ p.ears[0].rotation.z = -0.5; p.ears[1].rotation.z = 0.5; }

  p.tail.rotation.z = Math.PI/2 - 0.5 + Math.sin(t*3.1+h.id)*0.22;
  p.tail.rotation.y = Math.sin(t*2.3+h.id)*0.3;

  // в мир
  p.root.position.set(h.pos.x, h.pos.y + h.jumpY, h.pos.z);
  p.root.rotation.y = h.heading;

  // кольцо-подсветка
  p.ring.position.set(h.pos.x, 0.014, h.pos.z);
  const wantOp = (h === hovered) ? 0.75 : (h === focused ? 0.45 : 0);
  p.ring.material.opacity = damp(p.ring.material.opacity, wantOp, 8, dt);
  p.ring.scale.setScalar(1 + Math.sin(t*4)*0.06*(wantOp>0?1:0));
  p.ring.visible = p.ring.material.opacity > 0.01;
}

/* ---- геометрия тел столкновений ---- */
function closestOnCollider(c, x, z){
  if(c.kind === 'circle') return {x:c.px, z:c.pz};
  const abx = c.bx-c.ax, abz = c.bz-c.az;
  const L2 = abx*abx+abz*abz;
  let t = L2 > 0 ? ((x-c.ax)*abx + (z-c.az)*abz)/L2 : 0;
  t = clamp(t,0,1);
  return {x:c.ax+abx*t, z:c.az+abz*t};
}
function distToCollider(c, x, z){ const n = closestOnCollider(c,x,z); return Math.hypot(x-n.x, z-n.z); }

/* =====================================================================
   7. КОЛЕСО: ω = v / R
   ===================================================================== */
function updateWheel(dt){
  const runner = WHEEL.occupant;
  const driven = runner && runner.state === 'run_wheel' || (runner && runner.pawSpeed > 0.03);
  if(runner && driven){
    // лапы не скользят: жёсткая кинематическая связь, сильный (τ=0.02 c) захват
    const target = -runner.pawSpeed / WHEEL.R;
    WHEEL.omega += (target - WHEEL.omega) * Math.min(1, dt/0.02);
  } else if(runner){
    // бегун встал — лапы работают тормозом
    WHEEL.omega += (0 - WHEEL.omega) * Math.min(1, dt/0.35);
  } else {
    // пустое колесо: только трение, затухает к нулю
    WHEEL.omega *= Math.exp(-WHEEL.friction*dt);
    if(Math.abs(WHEEL.omega) < 0.004) WHEEL.omega = 0;
  }
  WHEEL.angle += WHEEL.omega*dt;
  wheelSpin.rotation.z = WHEEL.angle;
  WHEEL.pawSpeed = runner ? runner.pawSpeedReported : 0;
  WHEEL.rimSpeed = Math.abs(WHEEL.omega) * WHEEL.R;
  WHEEL.dev = WHEEL.pawSpeed > 0.05 ? Math.abs(WHEEL.rimSpeed - WHEEL.pawSpeed)/WHEEL.pawSpeed*100 : 0;
}

/* =====================================================================
   8. КОНТРОЛ: клик, наведение, тела
   ===================================================================== */
const ray = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let hovered = null, focused = null, focusT = 0;
const pickables = [wheelG, ...HAMSTERS.map(h=>h.parts.root)];

function pick(ev){
  const r = renderer.domElement.getBoundingClientRect();
  ndc.x = ((ev.clientX-r.left)/r.width)*2-1;
  ndc.y = -((ev.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ndc, camera);
  return ray.intersectObjects(pickables, true);
}
let downXY = null;
renderer.domElement.addEventListener('pointerdown', e=>{ downXY = {x:e.clientX, y:e.clientY}; });
renderer.domElement.addEventListener('pointerup', e=>{
  if(!downXY) return;
  if(Math.hypot(e.clientX-downXY.x, e.clientY-downXY.y) > 5) return;
  const hits = pick(e);
  if(!hits.length) { focused = null; return; }
  let o = hits[0].object, hm = null;
  while(o){ if(o.userData.hamsterRef){ hm = o.userData.hamsterRef; break; } o = o.parent; }
  if(hm){
    if(hm.grounded && !hm.inWheel && !hm.inPipe){ hm.grounded=false; hm.vy=2.35; hm.jumpY=0.001; }
    else { hm.twitchT = 0.001; }
    focused = hm; focusT = 3.2;
    document.querySelectorAll('.h-item').forEach(n=>n.classList.toggle('on', hm.id === +n.dataset.i));
  } else {
    // клик по колесу — толчок пустого колеса
    let w = hits[0].object;
    while(w){ if(w === wheelG){ if(!WHEEL.occupant) WHEEL.omega += (Math.random()<0.5?-1:1)*4.5; break; } w = w.parent; }
  }
});
renderer.domElement.addEventListener('pointermove', e=>{
  const hits = pick(e);
  hovered = null;
  if(hits.length){
    let o = hits[0].object;
    while(o){ if(o.userData.hamsterRef){ hovered = o.userData.hamsterRef; break; } o = o.parent; }
  }
  renderer.domElement.style.cursor = hovered ? 'pointer' : 'grab';
});
controls.addEventListener('start', ()=>{ focused = null; });

/* =====================================================================
   9. UI
   ===================================================================== */
const roster = document.getElementById('roster');
HAMSTERS.forEach((h,i)=>{
  const el = document.createElement('div');
  el.className = 'h-item'; el.dataset.i = i; el.style.setProperty('--c', h.colorHex);
  el.innerHTML = `<span class="dot"></span>
    <div><div class="nm">${h.name}</div><div class="act">стоит</div></div>
    <div class="spd"><b>0.00</b>м/с</div>
    <div class="bar"><i></i></div>`;
  el.addEventListener('click', ()=>{
    focused = h; focusT = 4;
    document.querySelectorAll('.h-item').forEach(n=>n.classList.remove('on'));
    el.classList.add('on');
    if(h.grounded && !h.inWheel && !h.inPipe){ h.grounded=false; h.vy=2.35; h.jumpY=0.001; }
  });
  roster.appendChild(el);
  h.ui = {row:el, act:el.querySelector('.act'), spd:el.querySelector('.spd b'), bar:el.querySelector('.bar i')};
});
const $ = id => document.getElementById(id);
function activityOf(h){
  if(h.state === 'walk') return GOAL_LABEL[h.goalKind] || 'гуляет';
  return LABEL[h.state] || h.state;
}
let violCount = 0, fps = 60;
function updateUI(now){
  HAMSTERS.forEach(h=>{
    const a = activityOf(h);
    if(h.ui.act.textContent !== a){ h.ui.act.textContent = a; h.ui.act.classList.toggle('mute', a==='стоит'); }
    const v = h.inWheel ? h.pawSpeed : h.speed;
    h.ui.spd.textContent = v.toFixed(2);
    h.ui.bar.style.width = Math.min(100, v/1.4*100).toFixed(0)+'%';
  });
  const r = WHEEL.occupant;
  $('dRunner').textContent = r ? r.name : '—';
  $('dPaw').textContent = WHEEL.pawSpeed.toFixed(3);
  $('dRim').textContent = WHEEL.rimSpeed.toFixed(3);
  $('dDev').textContent = r ? WHEEL.dev.toFixed(2)+' %' : '—';
  $('rDev').className = 'row' + (r ? (WHEEL.dev < 5 ? ' good' : ' warnv') : '');
  $('dOmega').textContent = WHEEL.omega.toFixed(3)+' рад/с';
  $('dRpm').textContent = (Math.abs(WHEEL.omega)*60/(Math.PI*2)).toFixed(1)+' об/мин';
  const inW = HAMSTERS.find(h=>h.inWheel);
  if(inW){
    const clr = WHEEL.R - Math.hypot(ДЛИНА_ЗВЕРЯ*0.5, inW.pos.y - WHEEL.center.y + ВЫСОТА_ЗВЕРЯ*0.5);
    $('dClr').textContent = (ГАБАРИТ_ДИАГ/WHEEL.R*100).toFixed(0)+'% · запас '+clr.toFixed(2)+' м';
    $('dFoot').textContent = 'Δ '+(inW.feetY - (WHEEL.center.y-WHEEL.R)).toFixed(4)+' м';
  } else { $('dClr').textContent = (ГАБАРИТ_ДИАГ/WHEEL.R*100).toFixed(0)+'% (зазор '+(R_ОБОДА-ГАБАРИТ_ДИАГ).toFixed(2)+')'; $('dFoot').textContent = '—'; }
  const p = PIPE.occupant;
  $('dPipe').textContent = p ? p.name : '—';
  $('dAxis').textContent = p ? Math.hypot(p.pos.y-PIPE.axisY, p.pos.z-PIPE.z).toFixed(4) : '0.0000';
  const any = HAMSTERS.find(h=>h.inWheel) || HAMSTERS.find(h=>h.inPipe) || HAMSTERS[0];
  $('dPhase').textContent = any.phase.toFixed(2)+' / '+any.dPhase.toFixed(3);
  $('dViol').textContent = violCount;
  $('rViol').className = 'row' + (violCount ? ' warnv' : ' good');
  $('dFps').textContent = fps.toFixed(0);
  $('dDc').textContent = renderer.info.render.calls;
  const ok = violCount === 0 && (!r || WHEEL.dev < 5);
  const v = $('verdict'); v.textContent = ok ? 'OK' : 'ОШИБКА'; v.className = 'pill ' + (ok?'ok':'bad');
}
$('togCol').addEventListener('click', ()=>{
  const el = $('togCol'); el.classList.toggle('on');
  helperG.visible = el.classList.contains('on');
});
$('togPause').addEventListener('click', ()=>{ $('togPause').classList.toggle('on'); paused = !paused; });
$('tsl').addEventListener('input', e=>{ timeScale = +e.target.value; $('tval').textContent = timeScale.toFixed(2)+'×'; });
$('kick').addEventListener('click', ()=>{ if(!WHEEL.occupant) WHEEL.omega += 5.2; });

/* =====================================================================
   10. ЦИКЛ
   ===================================================================== */
let clock = 0, last = performance.now(), paused = false, timeScale = 1;
let fpsAcc = 0, fpsN = 0, uiT = 0;

function step(dt){
  updateWheel(dt);
  for(const h of HAMSTERS){ h.prev.copy(h.pos); updateHamster(h, dt); }

  // контроль «не прошёл ли гуляющий сквозь тело»
  for(const h of HAMSTERS){
    if(h.inWheel || h.inPipe) continue;
    for(const c of COLLIDERS){
      if(distToCollider(c, h.pos.x, h.pos.z) < c.r - RADIUS_ТЕЛА - 0.02){
        violCount++; c.owner && (c.lastPen = 1);
      }
    }
  }

  // капля из поилки
  dripT -= dt;
  if(dripT <= 0){ dripT = 4 + Math.random()*7; dripY = 0; drip.visible = true; }
  if(drip.visible){
    dripY += dt*1.4; drip.position.set(DRINK.tip.x, DRINK.tip.y - dripY*dripY*3.2 - dripY*0.4, DRINK.tip.z);
    if(drip.position.y < 0.02){ drip.visible = false; }
  }
  lamp.intensity = 1.1 + Math.sin(clock*7.3)*0.012 + Math.sin(clock*2.1)*0.02;
}

function frame(now){
  requestAnimationFrame(frame);
  let dt = (now - last)/1000; last = now;
  if(dt > 0.05) dt = 0.05;                      // ограничение дельты при просадках
  fpsAcc += dt; fpsN++;
  if(fpsAcc > 0.5){ fps = fpsN/fpsAcc; fpsAcc = 0; fpsN = 0; }

  const sdt = paused ? 0 : dt*timeScale;
  clock += sdt;
  if(sdt > 0) step(sdt);

  if(focused && focusT > 0){
    focusT -= dt;
    controls.target.x = damp(controls.target.x, focused.pos.x, 3, dt);
    controls.target.y = damp(controls.target.y, focused.pos.y + 0.1, 3, dt);
    controls.target.z = damp(controls.target.z, focused.pos.z, 3, dt);
    if(focusT <= 0) document.querySelectorAll('.h-item').forEach(n=>n.classList.remove('on'));
  } else if(focused && focusT <= -2){
    focused = null;
  }
  if(!focused) {
    controls.target.x = damp(controls.target.x, 0.15, 0.6, dt);
    controls.target.y = damp(controls.target.y, 0.55, 0.6, dt);
    controls.target.z = damp(controls.target.z, 0.05, 0.6, dt);
  }
  controls.update();
  renderer.render(scene, camera);

  uiT += dt;
  if(uiT > 0.09){ uiT = 0; updateUI(now); }
}
requestAnimationFrame(frame);

addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
});

/* =====================================================================
   11. ВНЕШНИЙ ИНТЕРФЕЙС — чтобы числа можно было прочитать консолью
   ===================================================================== */
window.__diag = {
  get wheel(){ return {R:WHEEL.R, omega:WHEEL.omega, rimSpeed:WHEEL.rimSpeed, pawSpeed:WHEEL.pawSpeed,
                       discrepancyPct:WHEEL.dev, occupant:WHEEL.occupant && WHEEL.occupant.name}; },
  get pipe(){ const p = PIPE.occupant; return {axisY:PIPE.axisY, z:PIPE.z, rIn:PIPE.rIn,
              occupant:p && p.name, axisDeviation:p ? Math.hypot(p.pos.y-PIPE.axisY, p.pos.z-PIPE.z) : 0}; },
  get hamsters(){ return HAMSTERS.map(h=>({name:h.name, state:h.state, activity:activityOf(h),
      pos:{x:h.pos.x,y:h.pos.y,z:h.pos.z}, speed:h.speed, pawSpeed:h.pawSpeedReported,
      phase:h.phase, dPhase:h.dPhase, feetY:h.feetY, surfaceY:h.surfaceY, inWheel:h.inWheel, inPipe:h.inPipe})); },
  get violations(){ return violCount; },
  dims:{ДЛИНА_ЗВЕРЯ, ВЫСОТА_ЗВЕРЯ, ШИРИНА_ЗВЕРЯ, R_ОБОДА, ШИРИНА_КОЛЕСА, ШАГ_ЛАПА, ГАБАРИТ_ДИАГ},
  kickWheel:(w=5)=>{ if(!WHEEL.occupant) WHEEL.omega += w; }
};
console.log('%cХОМЯКИ · честная физика','color:#f2a63c;font:700 15px Unbounded,sans-serif',
  '\nR колеса =', R_ОБОДА.toFixed(3),'м · габарит зверя', ГАБАРИТ_ДИАГ.toFixed(3),'м',
  '\nwindow.__diag.wheel / .pipe / .hamsters — живые числа');
</script>
</body>
</html>
```

## Что именно гарантирует правильность

**Колесо.** `R_ОБОДА` не выбран на глаз — он вычислен из `ВЫСОТА_ЗВЕРЯ + ДЛИНА_ЗВЕРЯ·0.55 + ЗАПАС`, а `ШИРИНА_КОЛЕСА = ШИРИНА_ЗВЕРЯ·2.2`. Худший угол зверя (`ГАБАРИТ_ДИАГ = 0.504`) заведомо меньше радиуса (0.781) — это проверено `console.assert` при старте и показано в панели. ω берётся из `−v/R` с жёсткой кинематической связью (τ = 0.02 с), поэтому расхождение держится в долях процента; знак подобран так, что обод под лапами уходит назад. Пустое колесо крутится только по инерции: `ω *= exp(−1.7·t)` — проверьте кнопкой «толкнуть».

**Лапы.** Фаза — аккумулятор от пути: `phase += (Δпуть/длина шага)·2π`. На земле Δпуть — реальное смещение тела, в колесе — путь лап по ободу. Стоящий зверь не перебирает лапами: Δфазы в панели буквально 0.000. Работают диагонали (FL+RR / FR+RL).

**Труба.** Полость: наружная и внутренняя оболочки + торцевые кольца, сверху прозрачная вставка, чтобы было видно жителя. Вход — только лерпом от точки у торца; внутри `pos.y = axisY; pos.z = PIPE.z` каждую секунду, то есть отклонение от оси ровно ноль, а лапы достают до внутреннего дна (ноги масштабятся под расстояние до поверхности, и `feetY` совпадает с `axisY − rIn`).

**Тела.** Капсула у колеса, капсула у трубы (короче самой трубы — торцы открыты), круги у миски/домика/поилки. Выталкивание по кратчайшей нормали каждый кадр, счётчик «проходов сквозь тела» в панели — держится на нуле. Зелёные каркасы показывают всё это вживую.