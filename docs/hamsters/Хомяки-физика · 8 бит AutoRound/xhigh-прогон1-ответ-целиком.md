

Ниже — один самодостаточный HTML-файл. Вся физика построена честно: радиус колеса считается из констант габарита зверя, ω = v/R с инерционным лагом и затуханием от трения, фаза шага — только от пройденного пути, труба проходима лишь вдоль оси через торцы, все предметы имеют формы столкновения. Для внешней проверки всё вынесено в `window.CAGE` (см. заметки после кода).

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Клетка с хомяками — честная физика</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700&family=Rubik:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{
  --panel:#251b12; --panel2:#31241a; --ink:#f4e9d6; --muted:#b59c7e;
  --amber:#f2a541; --green:#8fd67a; --red:#ff7a6b; --line:rgba(242,165,65,.28);
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:hidden;background:#1b140d;font-family:Rubik,system-ui,sans-serif;color:var(--ink)}
#scene{position:fixed;inset:0}
canvas{display:block}
.hud{position:fixed;z-index:10;pointer-events:none}
.card{pointer-events:auto;background:linear-gradient(165deg,var(--panel2),var(--panel) 70%);border:1px solid var(--line);border-radius:12px;box-shadow:0 10px 34px rgba(0,0,0,.5);animation:rise .7s cubic-bezier(.2,.7,.3,1) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
#title{top:16px;left:16px}
#title .card{padding:14px 18px;max-width:330px}
#title h1{font-family:Unbounded,Rubik,sans-serif;font-weight:700;font-size:18px;line-height:1.22}
#title h1 em{font-style:normal;color:var(--amber)}
#title p{margin-top:7px;font-size:12px;line-height:1.5;color:var(--muted)}
#roster{top:16px;right:16px;width:252px}
#roster .card{padding:12px 12px 8px;animation-delay:.12s}
.ptitle{font-family:Unbounded;font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.16em;color:var(--muted);margin:0 4px 8px}
.ham{display:flex;align-items:center;gap:9px;padding:6px;border-radius:9px;transition:background .25s,transform .25s}
.ham:hover{background:rgba(242,165,65,.09);transform:translateX(-3px)}
.dot{width:12px;height:12px;border-radius:50%;flex:none;box-shadow:0 0 0 2px rgba(0,0,0,.35)}
.ham.busy .dot{animation:pulse 1.1s ease-in-out infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 2px rgba(0,0,0,.35),0 0 4px 1px currentColor}50%{box-shadow:0 0 0 2px rgba(0,0,0,.35),0 0 12px 3px currentColor}}
.nm{font-size:13px;font-weight:600;width:62px;flex:none}
.st{font-size:11.5px;color:var(--muted);text-align:right;flex:1;transition:color .3s}
.ham.busy .st{color:var(--amber)}
#tele{bottom:16px;left:16px}
#tele .card{padding:12px 16px;min-width:312px;font-family:"JetBrains Mono",monospace;animation-delay:.24s}
.row{display:flex;justify-content:space-between;gap:26px;font-size:12px;padding:2.5px 0}
.row span{color:var(--muted)}
.ok{color:var(--green)!important}.bad{color:var(--red)!important}.dim{color:var(--muted)!important}
#devBar{height:5px;border-radius:3px;background:rgba(255,255,255,.09);margin-top:9px;overflow:hidden}
#devFill{height:100%;width:0;background:var(--green);transition:width .15s linear,background .3s}
#hint{bottom:16px;right:16px}
#hint .card{padding:9px 14px;font-size:11.5px;color:var(--muted);animation-delay:.36s}
#hint b{color:var(--amber);font-weight:600}
@media(max-width:820px){#roster{display:none}#title .card{max-width:250px}#title h1{font-size:15px}}
</style>
</head>
<body>
<div id="scene"></div>

<header class="hud" id="title"><div class="card">
  <h1>Клетка с хомяками<br><em>честная физика</em></h1>
  <p>Колесо крутит только бегун: ω&nbsp;=&nbsp;v/R. Труба — лишь через торцы. Фаза шага — от пройденного пути, а не от часов.</p>
</div></header>

<aside class="hud" id="roster"><div class="card">
  <div class="ptitle">Обитатели · 5</div>
  <div id="hamList"></div>
</div></aside>

<div class="hud" id="tele"><div class="card">
  <div class="ptitle">Проверка колеса</div>
  <div class="row"><span>кто в колесе</span><b id="tWho" class="dim">—</b></div>
  <div class="row"><span>скорость лап v</span><b id="tV">0.000 м/с</b></div>
  <div class="row"><span>обод |ω|·R</span><b id="tR">0.000 м/с</b></div>
  <div class="row"><span>ω</span><b id="tW">0.00 рад/с</b></div>
  <div class="row"><span>расхождение</span><b id="tDev" class="dim">—</b></div>
  <div id="devBar"><div id="devFill"></div></div>
  <div class="row" style="margin-top:7px"><span id="tGeom"></span></div>
</div></div>

<div class="hud" id="hint"><div class="card">клик по хомяку — <b>подскок</b> · тяни мышью — обзор</div></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
"use strict";
/* ==================================================================
   1. РАЗМЕРЫ — от габарита зверя к колесу (ничего «на глаз»)
================================================================== */
const TAU = Math.PI * 2;
const DLINA_ZVERA   = 0.30;   // м, хвост — нос
const VYSOTA_ZVERA  = 0.175;  // м, лапы — макушка
const SHIROTA_ZVERA = 0.14;   // м

// Прямоугольный габарит, стоящий на нижней точке обода, целиком
// внутри кольца, когда sqrt((L/2)^2 + (R-H)^2) <= R  =>  R >= (L^2/4 + H^2)/(2H)
const R_MIN_KOLESA = (DLINA_ZVERA*DLINA_ZVERA/4 + VYSOTA_ZVERA*VYSOTA_ZVERA) / (2*VYSOTA_ZVERA);
const R_KOLESA     = R_MIN_KOLESA * 2.1;        // запас комфорта
const SHIRINA_KOLESA = SHIROTA_ZVERA * 1.7;     // шире боков зверя

const TABLE_TOP = 0.92, TRAY_H = 0.14, BED_H = 0.06;
const FLOOR_Y = TABLE_TOP + TRAY_H + BED_H;     // верх подстилки

console.assert(R_KOLESA > DLINA_ZVERA && R_KOLESA > VYSOTA_ZVERA, 'R колеса больше габарита зверя');
console.assert(SHIRINA_KOLESA > SHIROTA_ZVERA, 'ширина колеса шире боков зверя');

/* ---------- утилиты ---------- */
const clamp   = (v,a,b)=>Math.max(a,Math.min(b,v));
const clamp01 = v=>clamp(v,0,1);
const rand    = (a,b)=>a+Math.random()*(b-a);
const easeIO  = t=>t*t*(3-2*t);
function turnToward(a,b,max){let d=(b-a)%TAU;if(d>Math.PI)d-=TAU;if(d<-Math.PI)d+=TAU;return Math.abs(d)<=max?b:a+Math.sign(d)*max;}
function lerpAngle(a,b,t){let d=(b-a)%TAU;if(d>Math.PI)d-=TAU;if(d<-Math.PI)d+=TAU;return a+d*t;}
function mkMesh(geo,mat,sx=1,sy=sx,sz=sx){const m=new THREE.Mesh(geo,mat);m.scale.set(sx,sy,sz);m.castShadow=true;m.receiveShadow=true;return m;}

/* ==================================================================
   2. СЦЕНА, СВЕТ, КАМЕРА
================================================================== */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x241c13);
scene.fog = new THREE.Fog(0x241c13, 9, 20);

const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 60);
camera.position.set(2.6, 2.4, 3.4);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
document.getElementById('scene').appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xffe9cf, 0x54402c, 0.55));
const sun = new THREE.DirectionalLight(0xfff1dd, 1.15);
sun.position.set(-2.6, 4.6, 2.4);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
const sc = sun.shadow.camera;
sc.left=-3; sc.right=3; sc.top=3.4; sc.bottom=-1.6; sc.near=0.5; sc.far=12;
sc.updateProjectionMatrix();
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.015;
sun.target.position.set(0,1.2,0);
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight(0xdfe8ff, 0.22);
fill.position.set(3, 2.5, 4);
scene.add(fill);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.45, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 1.1;
controls.maxDistance = 9;
controls.maxPolarAngle = 1.5;

/* ==================================================================
   3. СОСТОЯНИЕ ПРЕДМЕТОВ (поля читаются снаружи через window.CAGE)
================================================================== */
const wheel = { omega:0, angle:0, owner:null };          // динамика колеса
const WHEEL = {                                          // геометрия колеса
  cx:-0.85, cz:-0.30,
  cy: FLOOR_Y + 0.02 + R_KOLESA,                         // низ обода = подстилка+2 см
  enterDur:1.15, exitDur:1.15,
  entryPoint:   new THREE.Vector3(-0.85 + SHIRINA_KOLESA/2 + 0.16, FLOOR_Y, -0.30),
  innerPoint:   new THREE.Vector3(-0.85, FLOOR_Y + 0.02, -0.30),   // лапы на нижней точке обода
  entryHeading: -Math.PI/2,
};
const TUBE = {                                           // геометрия трубы
  x0:0.15, x1:1.0, ty:FLOOR_Y + 0.15, tz:0.35,
  rOut:0.15, rIn:0.13,
  bottomY: FLOOR_Y + 0.02,                               // = ty - rIn: внутреннее дно
  enterDur:0.9, exitDur:0.7,
  startPoint:    new THREE.Vector3(0.24, FLOOR_Y + 0.02, 0.35),
  approachPoint: new THREE.Vector3(-0.15, FLOOR_Y, 0.35), // на продолжении оси!
  exitPoint:     new THREE.Vector3(1.12, FLOOR_Y, 0.35),
  owner:null,
};
const BOWL   = { x:0.35, z:-0.45, r:0.13 };
const BOTTLE = { x:-0.30, z:0.70 };

/* ==================================================================
   4. КОМНАТА, КЛЕТКА, МЕБЕЛЬ
================================================================== */
(function buildRoom(){
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(16,16), new THREE.MeshStandardMaterial({color:0x7a5636, roughness:.95}));
  floor.rotation.x = -Math.PI/2; floor.receiveShadow = true; scene.add(floor);
  const rug1 = new THREE.Mesh(new THREE.CircleGeometry(2.2,40), new THREE.MeshStandardMaterial({color:0x83402e, roughness:1}));
  rug1.rotation.x = -Math.PI/2; rug1.position.set(0,.005,.3); rug1.scale.set(1.3,1,1.05); rug1.receiveShadow = true; scene.add(rug1);
  const rug2 = new THREE.Mesh(new THREE.CircleGeometry(1.55,40), new THREE.MeshStandardMaterial({color:0x93503a, roughness:1}));
  rug2.rotation.x = -Math.PI/2; rug2.position.set(0,.008,.3); rug2.scale.set(1.3,1,1.05); rug2.receiveShadow = true; scene.add(rug2);

  const wallB = new THREE.Mesh(new THREE.PlaneGeometry(16,5.5), new THREE.MeshStandardMaterial({color:0x9c8468, roughness:1}));
  wallB.position.set(0,2.75,-4); wallB.receiveShadow = true; scene.add(wallB);
  const wallL = new THREE.Mesh(new THREE.PlaneGeometry(16,5.5), new THREE.MeshStandardMaterial({color:0x8f785e, roughness:1}));
  wallL.position.set(-4,2.75,0); wallL.rotation.y = Math.PI/2; wallL.receiveShadow = true; scene.add(wallL);
  const bbMat = new THREE.MeshStandardMaterial({color:0x5f4936, roughness:.9});
  const bb1 = new THREE.Mesh(new THREE.BoxGeometry(16,.12,.03), bbMat); bb1.position.set(0,.06,-3.985); scene.add(bb1);
  const bb2 = new THREE.Mesh(new THREE.BoxGeometry(.03,.12,16), bbMat); bb2.position.set(-3.985,.06,0); scene.add(bb2);

  // окно на левой стене (мотивирует свет)
  const winG = new THREE.Group(); winG.position.set(-3.97,2.5,.8); winG.rotation.y = Math.PI/2; scene.add(winG);
  winG.add(new THREE.Mesh(new THREE.PlaneGeometry(1.5,1.1), new THREE.MeshBasicMaterial({color:0xfff0d0})));
  const fMat = new THREE.MeshStandardMaterial({color:0x5f4936, roughness:.8});
  [[0,.585,1.62,.06],[0,-.585,1.62,.06],[-.78,0,.06,1.16],[.78,0,.06,1.16],[0,0,1.5,.04],[0,0,.04,1.1]].forEach(f=>{
    const m = new THREE.Mesh(new THREE.BoxGeometry(f[2],f[3],.05), fMat); m.position.set(f[0],f[1],.01); winG.add(m);
  });
  // картина
  const pic = new THREE.Group(); pic.position.set(1.7,2.5,-3.97); scene.add(pic);
  pic.add(new THREE.Mesh(new THREE.BoxGeometry(.56,.44,.03), new THREE.MeshStandardMaterial({color:0x4a3524, roughness:.7})));
  const pi = new THREE.Mesh(new THREE.PlaneGeometry(.48,.36), new THREE.MeshStandardMaterial({color:0xd8b878, roughness:.9}));
  pi.position.z = .017; pic.add(pi);
  const hamPic = new THREE.Mesh(new THREE.SphereGeometry(.05,10,8), new THREE.MeshStandardMaterial({color:0xe8a85c}));
  hamPic.scale.set(1.3,.9,.5); hamPic.position.set(.02,.02,.02); pic.add(hamPic);

  // стол
  const tMat = new THREE.MeshStandardMaterial({color:0x8a5a33, roughness:.7});
  const top = new THREE.Mesh(new THREE.BoxGeometry(3.1,.07,2.2), tMat);
  top.position.set(0,.885,0); top.castShadow = top.receiveShadow = true; scene.add(top);
  [[-1.42,-.95],[1.42,-.95],[-1.42,.95],[1.42,.95]].forEach(pt=>{
    const leg = new THREE.Mesh(new THREE.BoxGeometry(.1,.85,.1), tMat);
    leg.position.set(pt[0],.425,pt[1]); leg.castShadow = true; scene.add(leg);
  });
})();

(function buildCage(){
  const tray = new THREE.Mesh(new THREE.BoxGeometry(2.6,.14,1.7), new THREE.MeshStandardMaterial({color:0x98a1ab, roughness:.5}));
  tray.position.set(0,.99,0); tray.castShadow = tray.receiveShadow = true; scene.add(tray);
  const bed = new THREE.Mesh(new THREE.BoxGeometry(2.52,.06,1.62), new THREE.MeshStandardMaterial({color:0xcfa76f, roughness:1}));
  bed.position.set(0,1.09,0); bed.receiveShadow = true; scene.add(bed);

  // прутья — один InstancedMesh
  const positions = [];
  const NB = 31, stepX = 2.56/NB;
  for(let i=0;i<=NB;i++){ const x=-1.28+i*stepX; positions.push([x,.83],[x,-.83]); }
  const NS = 18, stepZ = 1.5/NS;
  for(let i=0;i<=NS;i++){ const z=-.75+i*stepZ; positions.push([-1.28,z],[1.28,z]); }
  const bars = new THREE.InstancedMesh(
    new THREE.CylinderGeometry(.0055,.0055,.85,6),
    new THREE.MeshStandardMaterial({color:0xb8bec6, metalness:.75, roughness:.3}),
    positions.length);
  const d = new THREE.Object3D();
  positions.forEach((pt,i)=>{ d.position.set(pt[0],1.485,pt[1]); d.rotation.set(0,0,0); d.updateMatrix(); bars.setMatrixAt(i,d.matrix); });
  bars.castShadow = bars.receiveShadow = true; scene.add(bars);

  const railMat = new THREE.MeshStandardMaterial({color:0x8f979f, metalness:.6, roughness:.35});
  [[0,.83,2.64,.035,.035],[0,-.83,2.64,.035,.035],[-1.28,0,.035,.035,1.7],[1.28,0,.035,.035,1.7]].forEach(r=>{
    const m = new THREE.Mesh(new THREE.BoxGeometry(r[2],r[3],r[4]), railMat);
    m.position.set(r[0],1.915,r[1]); m.castShadow = true; scene.add(m);
  });
  [[-1.28,-.83],[1.28,-.83],[-1.28,.83],[1.28,.83]].forEach(pt=>{
    const m = new THREE.Mesh(new THREE.CylinderGeometry(.011,.011,.9,10), railMat);
    m.position.set(pt[0],1.46,pt[1]); m.castShadow = true; scene.add(m);
  });
})();

(function buildChips(){                                   // стружка: один InstancedMesh
  const N = 750;
  const chips = new THREE.InstancedMesh(
    new THREE.BoxGeometry(.045,.005,.016),
    new THREE.MeshStandardMaterial({roughness:1}), N);
  const d = new THREE.Object3D(), c = new THREE.Color();
  for(let i=0;i<N;i++){
    d.position.set(rand(-1.22,1.22), rand(1.105,1.128), rand(-.77,.77));
    d.rotation.set(rand(-.4,.4), rand(0,TAU), rand(-.4,.4));
    d.updateMatrix(); chips.setMatrixAt(i, d.matrix);
    c.setHSL(.08+rand(-.015,.015), rand(.35,.55), rand(.45,.68));
    chips.setColorAt(i, c);
  }
  chips.instanceColor.needsUpdate = true;
  chips.receiveShadow = true;
  scene.add(chips);
})();

let wheelSpin;                                            // вращающаяся часть колеса
(function buildWheel(){
  const g = new THREE.Group();
  g.position.set(WHEEL.cx, WHEEL.cy, WHEEL.cz);
  const orient = new THREE.Group();                       // ось вращения — вдоль X
  orient.rotation.y = Math.PI/2; g.add(orient);
  wheelSpin = new THREE.Group(); orient.add(wheelSpin);

  const gapHalf = 50*Math.PI/180;                          // зазор снизу — вход
  const arcStart = -Math.PI/2 + gapHalf;
  const arcLen   = TAU - 2*gapHalf;
  const plateMat = new THREE.MeshStandardMaterial({color:0xa9b6bf, roughness:.45, side:THREE.DoubleSide});
  const rimMat   = new THREE.MeshStandardMaterial({color:0xcfd6dc, roughness:.4, metalness:.15});

  for(const s of [-1,1]){
    const plate = new THREE.Mesh(new THREE.RingGeometry(R_KOLESA+.004, R_KOLESA+.048, 48, 1, arcStart, arcLen), plateMat);
    plate.position.z = s*SHIRINA_KOLESA/2;
    plate.castShadow = plate.receiveShadow = true;
    wheelSpin.add(plate);
  }
  const rim = new THREE.Mesh(new THREE.TorusGeometry(R_KOLESA+.016, .016, 10, 72, arcLen), rimMat);
  rim.rotation.z = arcStart; rim.castShadow = true;       // внутренняя поверхность обода ровно на R
  wheelSpin.add(rim);
  const nSp = 8;
  for(let i=0;i<nSp;i++){
    const th = arcStart + arcLen*(i+.5)/nSp;
    const sp = new THREE.Mesh(new THREE.CylinderGeometry(.006,.006,R_KOLESA-.03,6), rimMat);
    sp.position.set(Math.cos(th)*(R_KOLESA/2), Math.sin(th)*(R_KOLESA/2), 0);
    sp.rotation.z = th - Math.PI/2; sp.castShadow = true;
    wheelSpin.add(sp);
  }
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,.06,16), rimMat);
  hub.rotation.x = Math.PI/2; wheelSpin.add(hub);

  const frameMat = new THREE.MeshStandardMaterial({color:0x6d7680, roughness:.5, metalness:.4});
  const base = new THREE.Mesh(new THREE.BoxGeometry(SHIRINA_KOLESA+.16,.02,.18), frameMat);
  base.position.y = FLOOR_Y+.01; base.castShadow = base.receiveShadow = true; g.add(base);
  for(const s of [-1,1]){
    const post = new THREE.Mesh(new THREE.BoxGeometry(.022, WHEEL.cy-FLOOR_Y-.02, .06), frameMat);
    post.position.set(s*(SHIRINA_KOLESA/2+.045), (FLOOR_Y+WHEEL.cy)/2, 0);
    post.castShadow = post.receiveShadow = true; g.add(post);
  }
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(.013,.013,SHIRINA_KOLESA+.14,10), frameMat);
  axle.rotation.z = Math.PI/2; axle.castShadow = true; g.add(axle);
  scene.add(g);
})();

(function buildTube(){
  const len = TUBE.x1 - TUBE.x0, midX = (TUBE.x0+TUBE.x1)/2;
  const mat  = new THREE.MeshStandardMaterial({color:0x8fbf7f, roughness:.55, side:THREE.DoubleSide});
  const matIn= new THREE.MeshStandardMaterial({color:0x6f9c60, roughness:.8,  side:THREE.BackSide});
  const shell = new THREE.Mesh(new THREE.CylinderGeometry(TUBE.rOut,TUBE.rOut,len,28,1,true), mat);
  shell.rotation.z = Math.PI/2; shell.position.set(midX,TUBE.ty,TUBE.tz);
  shell.castShadow = shell.receiveShadow = true; scene.add(shell);
  const inner = new THREE.Mesh(new THREE.CylinderGeometry(TUBE.rIn,TUBE.rIn,len-.01,28,1,true), matIn);
  inner.rotation.z = Math.PI/2; inner.position.copy(shell.position); scene.add(inner);
  for(const s of [-1,1]){
    const ring = new THREE.Mesh(new THREE.TorusGeometry((TUBE.rIn+TUBE.rOut)/2,(TUBE.rOut-TUBE.rIn)/2,10,28), mat);
    ring.rotation.y = Math.PI/2; ring.position.set(TUBE.x0+s*len/2, TUBE.ty, TUBE.tz);
    ring.castShadow = true; scene.add(ring);
  }
})();

(function buildBowl(){
  const g = new THREE.Group(); g.position.set(BOWL.x, FLOOR_Y, BOWL.z);
  const pts = [new THREE.Vector2(.015,0), new THREE.Vector2(.105,0), new THREE.Vector2(.128,.042),
               new THREE.Vector2(.124,.05), new THREE.Vector2(.10,.047), new THREE.Vector2(.094,.018)];
  const lathe = new THREE.Mesh(new THREE.LatheGeometry(pts,28),
    new THREE.MeshStandardMaterial({color:0x4f7fa8, roughness:.35, side:THREE.DoubleSide}));
  lathe.castShadow = lathe.receiveShadow = true; g.add(lathe);
  const grains = new THREE.Mesh(new THREE.SphereGeometry(.085,16,12), new THREE.MeshStandardMaterial({color:0xc7a04e, roughness:1}));
  grains.scale.set(1,.42,1); grains.position.y = .038; grains.castShadow = true; g.add(grains);
  const gm = new THREE.MeshStandardMaterial({color:0xb98f3e, roughness:1});
  for(let i=0;i<14;i++){
    const gr = new THREE.Mesh(new THREE.SphereGeometry(.005,6,5), gm);
    const a=rand(0,TAU), r=rand(0,.07);
    gr.position.set(Math.cos(a)*r, .05+rand(0,.012), Math.sin(a)*r); g.add(gr);
  }
  scene.add(g);
  for(let i=0;i<10;i++){                                    // рассыпанные зёрна
    const gr = new THREE.Mesh(new THREE.SphereGeometry(.0045,6,5), gm);
    const a=rand(0,TAU), r=rand(.16,.34);
    gr.position.set(BOWL.x+Math.cos(a)*r, FLOOR_Y+.004, BOWL.z+Math.sin(a)*r); scene.add(gr);
  }
})();

(function buildBottle(){
  const g = new THREE.Group(); g.position.set(BOTTLE.x, 0, BOTTLE.z);
  const glass = new THREE.MeshStandardMaterial({color:0xcfe9f5, roughness:.15, transparent:true, opacity:.5});
  const body = new THREE.Mesh(new THREE.CylinderGeometry(.032,.032,.17,16), glass);
  body.position.y = 1.52; body.rotation.x = -.1; body.castShadow = true; g.add(body);
  const water = new THREE.Mesh(new THREE.CylinderGeometry(.026,.026,.075,16),
    new THREE.MeshStandardMaterial({color:0x5aa7d6, roughness:.2, transparent:true, opacity:.8}));
  water.position.y = 1.465; water.rotation.x = -.1; g.add(water);
  const cap = new THREE.Mesh(new THREE.ConeGeometry(.016,.035,12), new THREE.MeshStandardMaterial({color:0xd8d8d8, roughness:.4}));
  cap.position.y = 1.425; cap.rotation.x = Math.PI+.1; g.add(cap);
  const cup = new THREE.Mesh(new THREE.CylinderGeometry(.02,.024,.022,14),
    new THREE.MeshStandardMaterial({color:0xb8bec6, metalness:.7, roughness:.3}));
  cup.position.y = 1.395; g.add(cup);
  const mount = new THREE.Mesh(new THREE.BoxGeometry(.05,.16,.015), new THREE.MeshStandardMaterial({color:0x6d7680, roughness:.5}));
  mount.position.set(0,1.53,.14); mount.castShadow = true; g.add(mount);
  scene.add(g);
})();

/* ==================================================================
   5. ХОМЯКИ: модель из частей
================================================================== */
function createHamsterModel(cfg){
  const root = new THREE.Group();                          // позиция = точка лап
  const body = new THREE.Group(); root.add(body);
  const fur    = new THREE.MeshStandardMaterial({color:cfg.fur, roughness:.9});
  const bellyM = new THREE.MeshStandardMaterial({color:cfg.belly, roughness:.95});
  const dark   = new THREE.MeshStandardMaterial({color:0x241812, roughness:.35});
  const pink   = new THREE.MeshStandardMaterial({color:0xe5a18c, roughness:.7});
  const black  = new THREE.MeshBasicMaterial({color:0x000000});
  const white  = new THREE.MeshBasicMaterial({color:0xffffff});
  const ears = [], cheeks = [];

  const torso = mkMesh(new THREE.SphereGeometry(1,20,14), fur, .075,.068,.105);
  torso.position.set(0,.085,-.015); body.add(torso);
  const belly = mkMesh(new THREE.SphereGeometry(1,18,12), bellyM, .06,.05,.082);
  belly.position.set(0,.06,.014); body.add(belly);

  const head = new THREE.Group();                          // отдельная группа — кивает
  head.position.set(0,.105,.095); body.add(head);
  head.add(mkMesh(new THREE.SphereGeometry(1,18,14), fur, .055,.05,.052));
  for(const s of [-1,1]){
    const eye = mkMesh(new THREE.SphereGeometry(.0105,12,10), dark);
    eye.position.set(.030*s,.013,.040); head.add(eye);
    const pup = mkMesh(new THREE.SphereGeometry(.0055,10,8), black);
    pup.position.set(.030*s,.013,.0495); head.add(pup);
    const gl = mkMesh(new THREE.SphereGeometry(.0018,6,6), white);
    gl.castShadow = false; gl.position.set(.033*s,.017,.0505); head.add(gl);
    const ch = mkMesh(new THREE.SphereGeometry(1,12,10), fur, .02,.026,.026);
    ch.position.set(.042*s,-.012,.026); head.add(ch); cheeks.push(ch);
    const eg = new THREE.Group(); eg.position.set(.031*s,.043,-.014);
    eg.add(mkMesh(new THREE.SphereGeometry(1,12,10), fur, .015,.02,.011));
    const inn = mkMesh(new THREE.SphereGeometry(1,10,8), pink, .009,.012,.006);
    inn.position.z = .005; eg.add(inn);
    head.add(eg); ears.push(eg);
  }
  const nose = mkMesh(new THREE.SphereGeometry(.0068,10,8), pink);
  nose.position.set(0,.001,.0575); head.add(nose);

  const tail = mkMesh(new THREE.SphereGeometry(.015,10,8), fur);
  tail.position.set(0,.078,-.122); body.add(tail);

  const legs = {};                                         // диагонали: FL+HR / FR+HL
  const defs = { fl:[-.056,.052], fr:[.056,.052], hl:[-.056,-.078], hr:[.056,-.078] };
  for(const k in defs){
    const g = new THREE.Group(); g.position.set(defs[k][0], .058, defs[k][1]);
    const limb = mkMesh(new THREE.CylinderGeometry(.0105,.009,.05,8), fur);
    limb.position.y = -.024; g.add(limb);
    const foot = mkMesh(new THREE.SphereGeometry(1,10,8), fur, .013,.007,.017);
    foot.position.y = -.051; g.add(foot);
    body.add(g); legs[k] = g;
  }
  return {root, body, head, ears, cheeks, legs, tail, mats:{fur}};
}

const pickMeshes = [];
function makeHamster(i, cfg){
  const m = createHamsterModel(cfg);
  const h = {
    idx:i, name:cfg.name, root:m.root, parts:m,
    state:'idle', stateT:0, idleDur:.4 + i*.45, idleText:'отдыхает',
    heading:rand(0,TAU), legPhase:0, strideLen:rand(.08,.1),
    runV:0, runDir:1, jumpY:0, jumpV:0, squashT:0, wiggleT:0,
    breathRate:rand(1.8,2.6), seed:Math.random()*10,
    earT:0, earSide:0, earSideSign:1, chewT:0,
    plan:null, _prev:new THREE.Vector3(), _lastSpeed:0,
    uiRow:null, uiSt:null,
  };
  m.root.position.set(cfg.pos[0], FLOOR_Y, cfg.pos[1]);
  m.root.rotation.y = h.heading;
  h._prev.copy(m.root.position);
  scene.add(m.root);
  m.root.traverse(o=>{ if(o.isMesh){ o.userData.hidx = i; pickMeshes.push(o); } });
  return h;
}
const CASTS = [
  {name:'Барни',   fur:0xe8a85c, belly:0xf6e7cd, pos:[-.35,.25]},
  {name:'Клепа',   fur:0x9aa0ab, belly:0xe9e5dc, pos:[.55,-.15]},
  {name:'Муму',    fur:0xf0ddb4, belly:0xfff7e8, pos:[.10,.45]},
  {name:'Шустрик', fur:0x8a5a33, belly:0xc99b6d, pos:[-.45,-.40]},
  {name:'Плюша',   fur:0xdf7f42, belly:0xf7d9ba, pos:[.80,.05]},
];
const HAMSTERS = CASTS.map((c,i)=>makeHamster(i,c));

/* ==================================================================
   6. ПОВЕДЕНИЕ: конечный автомат
   idle -> walk -> (wheelEnter|tubeEnter|eat|idle) -> ...
================================================================== */
const PUSHABLE = new Set(['idle','walk','eat']);
const EVENTS = [];
let simTime = 0;
function logEvent(type, extra){
  EVENTS.push(Object.assign({t:+simTime.toFixed(2), type}, extra||{}));
  if(EVENTS.length > 300) EVENTS.shift();
}

function updateWheel(dt){
  const runner = HAMSTERS.find(h=>h.state==='wheelRun');
  if(runner){
    // ω = v/R. Знак: при взгляде вдоль +Z обод под лапами уходит в -Z.
    const target = runner.runDir * runner.runV / R_KOLESA;
    wheel.omega += (target - wheel.omega) * Math.min(1, dt/0.04);   // малая инерция
  } else {
    wheel.omega *= Math.exp(-2.0*dt);                               // трение гасит
    if(Math.abs(wheel.omega) < 0.008) wheel.omega = 0;
  }
  wheel.angle += wheel.omega*dt;
  wheelSpin.rotation.z = wheel.angle;
}

function eaterCount(){
  return HAMSTERS.filter(o=>o.state==='eat' || (o.state==='walk' && o.plan && o.plan.kind==='bowl')).length;
}
function isClear(x,z,r){
  if(x < -1.1+r || x > 1.1-r || z < -.68+r || z > .68-r) return false;
  if(Math.abs(x-WHEEL.cx) < .21+r && Math.abs(z-WHEEL.cz) < .42) return false;
  const qx = clamp(x, TUBE.x0, TUBE.x1);
  if(Math.hypot(x-qx, z-TUBE.tz) < TUBE.rOut+.08+r) return false;
  if(Math.hypot(x-BOWL.x, z-BOWL.z) < BOWL.r+.08+r) return false;
  if(Math.hypot(x-BOTTLE.x, z-BOTTLE.z) < .12+r) return false;
  return true;
}
function randomPoint(){
  for(let i=0;i<14;i++){
    const x=rand(-1,1), z=rand(-.6,.6);
    if(isClear(x,z,.09)) return {x,z};
  }
  return {x:rand(-.5,.5), z:rand(-.3,.3)};
}
function bowlSpot(h){
  for(let i=0;i<10;i++){
    const a=Math.random()*TAU, x=BOWL.x+Math.cos(a)*.25, z=BOWL.z+Math.sin(a)*.25;
    if(!isClear(x,z,.08)) continue;
    let ok = true;
    for(const o of HAMSTERS)
      if(o!==h && Math.hypot(o.root.position.x-x, o.root.position.z-z) < .22) ok = false;
    if(ok) return {x,z};
  }
  return {x:BOWL.x, z:BOWL.z+.25};
}
function setIdleText(h){ h.idleText = ['отдыхает','дышит','чистится','прислушивается'][(Math.random()*4)|0]; }

function decide(h){
  const opts = [];
  if(!wheel.owner) opts.push('wheel','wheel','wheel');   // один бегун — один колесо
  if(!TUBE.owner)  opts.push('tube','tube');
  if(eaterCount()<2) opts.push('bowl','bowl');
  opts.push('stroll','stroll');
  const kind = opts[(Math.random()*opts.length)|0];
  if(kind==='wheel'){ wheel.owner = h; h.plan = {kind, target:WHEEL.entryPoint.clone(), speed:.24}; }
  else if(kind==='tube'){ TUBE.owner = h; h.plan = {kind, target:TUBE.approachPoint.clone(), speed:.24}; }
  else if(kind==='bowl'){ h.plan = {kind, target:bowlSpot(h), speed:.24}; }
  else { h.plan = {kind, target:randomPoint(), speed:rand(.18,.3)}; }
  h.state = 'walk'; h.stateT = 0;
}

function onArrive(h){
  const kind = h.plan.kind;
  if(kind==='wheel'){
    h.state='wheelEnter'; h.stateT=0;
    h.plan.from = h.root.position.clone();
    h.plan.fromHeading = h.heading;
    h.runDir = Math.random()<.5 ? 1 : -1;
    h.plan.runHeading = h.runDir>0 ? 0 : Math.PI;
    h.plan.dur = rand(5,9); h.plan.vMax = rand(.45,.62);
    logEvent('wheel_enter',{who:h.name});
  } else if(kind==='tube'){
    h.state='tubeEnter'; h.stateT=0;
    h.plan.from = h.root.position.clone();
    logEvent('tube_enter',{who:h.name, offsetFromAxis:+Math.abs(h.root.position.z-TUBE.tz).toFixed(3)});
  } else if(kind==='bowl'){
    h.state='eat'; h.stateT=0; h.plan.dur=rand(3,6); h.chewT=0;
  } else {
    h.state='idle'; h.stateT=0; h.idleDur=rand(.8,2.2); setIdleText(h);
  }
}

function updateHamster(h, dt){
  const p = h.root.position, before = h._prev;
  h.stateT += dt;

  switch(h.state){
    case 'idle':
      if(h.stateT >= h.idleDur) decide(h);
      break;
    case 'walk': {
      const t = h.plan.target;
      const dx = t.x-p.x, dz = t.z-p.z, d = Math.hypot(dx,dz);
      if(d < .055){ onArrive(h); break; }
      h.heading = turnToward(h.heading, Math.atan2(dx,dz), 4.2*dt);
      const sp = h.plan.speed;
      p.x += Math.sin(h.heading)*sp*dt;
      p.z += Math.cos(h.heading)*sp*dt;
      break;
    }
    case 'wheelEnter': {                                     // плавный вход через зазор
      const k = easeIO(clamp01(h.stateT/WHEEL.enterDur));
      p.lerpVectors(h.plan.from, WHEEL.innerPoint, k);
      h.heading = lerpAngle(h.plan.fromHeading, h.plan.runHeading, k);
      if(k>=1){ h.state='wheelRun'; h.stateT=0; h.runV=0; }
      break;
    }
    case 'wheelRun': {                                       // стоит на нижней точке обода
      const dur=h.plan.dur, A=1.1, B=.8, vm=h.plan.vMax;
      h.runV = h.stateT<A ? vm*h.stateT/A
               : (h.stateT>dur-B ? vm*clamp01((dur-h.stateT)/B) : vm);
      p.set(WHEEL.cx, WHEEL.cy - R_KOLESA + Math.abs(Math.sin(h.legPhase))*.006, WHEEL.cz);
      h.heading = h.plan.runHeading;
      if(h.stateT>=dur){
        h.state='wheelExit'; h.stateT=0;
        h.plan.from = p.clone(); h.plan.fromHeading = h.heading;
      }
      break;
    }
    case 'wheelExit': {                                      // плавный выход
      const k = easeIO(clamp01(h.stateT/WHEEL.exitDur));
      p.lerpVectors(h.plan.from, WHEEL.entryPoint, k);
      h.heading = lerpAngle(h.plan.fromHeading, WHEEL.entryHeading, k);
      if(k>=1){
        h.state='idle'; h.stateT=0; h.idleDur=rand(1,2.6); h.runV=0;
        wheel.owner = null; logEvent('wheel_exit',{who:h.name}); setIdleText(h);
      }
      break;
    }
    case 'tubeEnter': {                                      // только вдоль оси, через торец
      const k = easeIO(clamp01(h.stateT/TUBE.enterDur));
      p.lerpVectors(h.plan.from, TUBE.startPoint, k);
      h.heading = Math.PI/2;
      if(k>=1){ h.state='tubeRun'; h.stateT=0; }
      break;
    }
    case 'tubeRun': {                                        // на внутреннем дне, z === tz
      p.x += .16*dt; p.y = TUBE.bottomY; p.z = TUBE.tz;
      h.heading = Math.PI/2;
      if(p.x >= TUBE.x1-.09){ h.state='tubeExit'; h.stateT=0; h.plan.from=p.clone(); }
      break;
    }
    case 'tubeExit': {
      const k = easeIO(clamp01(h.stateT/TUBE.exitDur));
      p.lerpVectors(h.plan.from, TUBE.exitPoint, k);
      h.heading = Math.PI/2;
      if(k>=1){
        h.state='idle'; h.stateT=0; h.idleDur=rand(1,2.6);
        TUBE.owner = null; logEvent('tube_exit',{who:h.name}); setIdleText(h);
      }
      break;
    }
    case 'eat':
      h.heading = turnToward(h.heading, Math.atan2(BOWL.x-p.x, BOWL.z-p.z), 3*dt);
      if(h.stateT >= h.plan.dur){ h.state='idle'; h.stateT=0; h.idleDur=rand(1.2,3); setIdleText(h); }
      break;
  }

  // ФАЗА ШАГА — от пройденного пути (в колесе — от скорости лап, равной скорости обода)
  const movedH = Math.hypot(p.x-before.x, p.z-before.z);
  if(h.state==='wheelRun') h.legPhase += (h.runV*dt/h.strideLen)*TAU;
  else if(h.state!=='eat') h.legPhase += (movedH/h.strideLen)*TAU;
  before.copy(p);

  // прыжок от клика
  if(h.jumpY>0 || h.jumpV>0){
    h.jumpY += h.jumpV*dt; h.jumpV -= 9.8*dt;
    if(h.jumpY<=0 && h.jumpV<0){ h.jumpY=0; h.jumpV=0; h.squashT=.22; }
  }
  if(h.squashT>0) h.squashT -= dt;

  // базовая высота (в колесе/трубе y уже задан состоянием)
  if(h.state!=='wheelRun' && h.state!=='tubeRun' && h.state!=='tubeEnter' && h.state!=='tubeExit' && h.state!=='wheelEnter')
    p.y = FLOOR_Y + h.jumpY;

  h.root.rotation.y = h.heading;
  updateLook(h, dt, movedH);
}

function gaitNorm(h){
  switch(h.state){
    case 'walk': return Math.min(1,(h.plan.speed||.25)/.3);
    case 'wheelRun': return Math.min(1,h.runV/.5);
    case 'wheelEnter': case 'wheelExit': case 'tubeEnter': case 'tubeExit': return .35;
    case 'tubeRun': return .5;
    default: return 0;
  }
}

function updateLook(h, dt, movedH){
  const gait = gaitNorm(h), amp = .5*gait;
  const L = h.parts.legs;
  if(h.jumpY > .004){
    L.fl.rotation.x = L.fr.rotation.x = L.hl.rotation.x = L.hr.rotation.x = -1.05;
  } else {
    L.fl.rotation.x = Math.sin(h.legPhase)*amp;
    L.hr.rotation.x = Math.sin(h.legPhase)*amp;
    L.fr.rotation.x = Math.sin(h.legPhase+Math.PI)*amp;
    L.hl.rotation.x = Math.sin(h.legPhase+Math.PI)*amp;
  }
  // дыхание + squash при приземлении
  const b = Math.sin(simTime*h.breathRate + h.seed*7);
  const sq = h.squashT>0 ? 1-.3*Math.sin(Math.PI*clamp01(h.squashT/.22)) : 1;
  h.parts.body.scale.set(1+.04*b, (1+.02*b)*sq, 1+.04*b);
  h.parts.body.position.y = Math.abs(Math.sin(h.legPhase))*.004*gait;

  // голова
  let hx=.06, hy=0, hz=0;
  if(h.state==='eat'){
    h.chewT += dt;
    hx = .5 + Math.sin(h.chewT*10)*.06;
    const ch = 1+.4*Math.abs(Math.sin(h.chewT*5));
    h.parts.cheeks[0].scale.set(.02*ch,.026*ch,.026*ch);
    h.parts.cheeks[1].scale.set(.02*ch,.026*ch,.026*ch);
  } else {
    h.parts.cheeks[0].scale.set(.02,.026,.026);
    h.parts.cheeks[1].scale.set(.02,.026,.026);
    if(h.state==='idle'){ hz = Math.sin(simTime*.6+h.seed*9)*.09; hy = Math.sin(simTime*.21+h.seed*5)*.35; }
    if(h.state==='wheelRun') hx = -.18;
  }
  if(h.wiggleT>0){ h.wiggleT -= dt; hy = Math.sin(h.wiggleT*28)*.35; }
  h.parts.head.rotation.set(hx,hy,hz);

  // ухо
  if(h.earT>0){
    h.earT -= dt;
    const f = clamp01(h.earT/.55);
    h.parts.ears[h.earSide].rotation.z = h.earSideSign*Math.sin((.55-Math.max(h.earT,0))*26)*.45*f;
  } else {
    h.parts.ears[0].rotation.z = 0; h.parts.ears[1].rotation.z = 0;
    if(Math.random() < dt*.14){ h.earT=.55; h.earSide=Math.random()<.5?0:1; h.earSideSign=Math.random()<.5?-1:1; }
  }
  h.parts.tail.rotation.y = Math.sin(simTime*(2.5+5*gait)+h.seed*3)*.25;

  const inst = dt>0 ? movedH/dt : 0;
  h._lastSpeed = h._lastSpeed*.7 + inst*.3;
}

/* ---------- столкновения: выталкивание по кратчайшей нормали ---------- */
function resolveCollisions(h){
  const p = h.root.position;
  p.x = clamp(p.x, -1.17, 1.17);                            // стенки клетки
  p.z = clamp(p.z, -0.72, 0.72);
  // колесо: диск с зазором снизу — зона между пластинами/стойками
  {
    const dx = p.x-WHEEL.cx, dz = p.z-WHEEL.cz;
    if(Math.abs(dz) < .42 && Math.abs(dx) < .205)
      p.x = WHEEL.cx + Math.sign(dx||1)*.205;
  }
  // труба: горизонтальная капсула (бок твёрдый, вход только через торцы)
  {
    const qx = clamp(p.x, TUBE.x0, TUBE.x1);
    const dx = p.x-qx, dz = p.z-TUBE.tz, d = Math.hypot(dx,dz);
    const rr = TUBE.rOut + .075;
    if(d < rr && d > 1e-4){ p.x += dx/d*(rr-d); p.z += dz/d*(rr-d); }
  }
  // миска
  {
    const dx = p.x-BOWL.x, dz = p.z-BOWL.z, d = Math.hypot(dx,dz);
    const rr = BOWL.r + .075;
    if(d < rr && d > 1e-4){ p.x += dx/d*(rr-d); p.z += dz/d*(rr-d); }
  }
  // поилка
  {
    const dx = p.x-BOTTLE.x, dz = p.z-BOTTLE.z, d = Math.hypot(dx,dz);
    if(d < .115 && d > 1e-4){ p.x += dx/d*(.115-d); p.z += dz/d*(.115-d); }
  }
}

function repel(){                                            // хомяки не стоят друг в друге
  for(let i=0;i<HAMSTERS.length;i++) for(let j=i+1;j<HAMSTERS.length;j++){
    const a=HAMSTERS[i], b=HAMSTERS[j];
    const pa=a.root.position, pb=b.root.position;
    if(Math.abs(pa.y-pb.y) > .12) continue;
    const dx=pb.x-pa.x, dz=pb.z-pa.z, d=Math.hypot(dx,dz);
    const minD=.155;
    if(d>=minD || d<1e-5) continue;
    const nx=dx/d, nz=dz/d, push=minD-d;
    const fa=PUSHABLE.has(a.state), fb=PUSHABLE.has(b.state);
    if(fa&&fb){ pa.x-=nx*push*.5; pa.z-=nz*push*.5; pb.x+=nx*push*.5; pb.z+=nz*push*.5; }
    else if(fa){ pa.x-=nx*push; pa.z-=nz*push; }
    else if(fb){ pb.x+=nx*push; pb.z+=nz*push; }
  }
}

/* ==================================================================
   7. UI: ростер, телеметрия, клики, hover
================================================================== */
const listEl = document.getElementById('hamList');
for(const h of HAMSTERS){
  const row = document.createElement('div');
  row.className = 'ham';
  const css = '#'+h.parts.mats.fur.color.getHexString();
  row.innerHTML = '<span class="dot" style="background:'+css+';color:'+css+'"></span>' +
                  '<span class="nm">'+h.name+'</span><span class="st">отдыхает</span>';
  listEl.appendChild(row);
  h.uiRow = row; h.uiSt = row.querySelector('.st');
}
const el = {
  tWho:document.getElementById('tWho'), tV:document.getElementById('tV'),
  tR:document.getElementById('tR'), tW:document.getElementById('tW'),
  tDev:document.getElementById('tDev'), devFill:document.getElementById('devFill'),
  tGeom:document.getElementById('tGeom'),
};
el.tGeom.innerHTML = 'R='+R_KOLESA.toFixed(3)+' м &gt; '+DLINA_ZVERA+'×'+VYSOTA_ZVERA+' ✓ · ширина '+SHIRINA_KOLESA.toFixed(2)+' &gt; '+SHIROTA_ZVERA+' ✓';

function statusText(h){
  switch(h.state){
    case 'idle': return h.idleText;
    case 'walk': return {wheel:'идёт к колесу', tube:'идёт к трубе', bowl:'идёт к миске', stroll:'гуляет'}[h.plan.kind];
    case 'wheelEnter': return 'забирается в колесо';
    case 'wheelRun': return 'бежит в колесе';
    case 'wheelExit': return 'выходит из колеса';
    case 'tubeEnter': return 'заходит в трубу';
    case 'tubeRun': return 'ползёт по трубе';
    case 'tubeExit': return 'выходит из трубы';
    case 'eat': return 'грызёт зёрна';
  }
  return '';
}
function updateUI(){
  for(const h of HAMSTERS){
    h.uiSt.textContent = statusText(h);
    h.uiRow.classList.toggle('busy', h.state!=='idle');
  }
  const occ = wheel.owner;
  const runner = occ && occ.state==='wheelRun' ? occ : null;
  const rim = Math.abs(wheel.omega)*R_KOLESA;
  el.tW.textContent = wheel.omega.toFixed(2)+' рад/с';
  if(runner){