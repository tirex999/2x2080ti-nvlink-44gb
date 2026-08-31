

Готово — единый файл `aquarium.html`, всё по ТЗ: 15 рыбок с ИИ (разделение, блуждание, погоня за кормом, рост +5%), стекло с `transmission: 0.95`, песок с процедурными буграми, 8 камней, 12 водорослей на `TubeGeometry`, 30 пузырей, кормление кликом, день/ночь, статистика и FPS. Просто сохраните и откройте в браузере.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark">
<title>🐠 3D Аквариум — интерактивный</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Russo+One&family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  :root{
    --cyan:#3ee6ff; --teal:#2bd9a0; --blue:#3b82f6; --amber:#ffc857;
    --panel:rgba(7,24,48,.58); --line:rgba(120,205,255,.22);
    --txt:#d9ecff; --dim:#8fb4d8;
  }
  html,body{height:100%;overflow:hidden}
  body{
    font-family:'Manrope',system-ui,sans-serif;color:var(--txt);
    background:linear-gradient(180deg,#030d1f 0%,#07244d 55%,#0b3a72 100%);
    transition:background 1.2s ease;
  }
  body.night{background:linear-gradient(180deg,#01050e 0%,#03132b 55%,#062044 100%)}
  #scene{position:fixed;inset:0;display:block}

  /* ---------- Панели (glass UI) ---------- */
  .panel{
    position:fixed;z-index:10;
    background:var(--panel);
    border:1px solid var(--line);border-radius:16px;
    backdrop-filter:blur(14px) saturate(140%);
    -webkit-backdrop-filter:blur(14px) saturate(140%);
    box-shadow:0 18px 40px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.07);
    padding:18px 20px;
  }
  #info{top:20px;left:20px;width:280px}
  #stats{top:20px;right:20px;width:190px}

  .logo{display:flex;align-items:center;gap:10px;margin-bottom:6px}
  .logo svg{width:36px;height:24px;filter:drop-shadow(0 0 8px rgba(62,230,255,.55))}
  h1{
    font-family:'Russo One';font-size:24px;letter-spacing:.5px;
    background:linear-gradient(90deg,var(--cyan),var(--teal));
    -webkit-background-clip:text;background-clip:text;color:transparent;
  }
  .sub{font-size:10.5px;color:var(--dim);letter-spacing:2.5px;text-transform:uppercase;margin-bottom:14px}

  .controls{list-style:none;font-size:12.5px;color:var(--dim);display:grid;gap:7px;margin-bottom:16px}
  .controls li{display:flex;gap:9px;align-items:center}
  .controls .key{
    flex:0 0 auto;min-width:58px;text-align:center;font-size:10px;font-weight:800;letter-spacing:.4px;
    padding:3px 8px;border-radius:6px;
    background:rgba(62,230,255,.1);border:1px solid rgba(62,230,255,.25);color:var(--cyan);
  }

  .btns{display:flex;flex-direction:column;gap:9px}
  .btn{
    font-family:'Manrope';font-weight:800;font-size:13px;letter-spacing:.3px;
    color:#04121f;border:none;cursor:pointer;
    padding:10px 14px;border-radius:10px;
    display:flex;justify-content:space-between;align-items:center;
    position:relative;overflow:hidden;
    transition:transform .18s ease, box-shadow .18s ease;
  }
  .btn::after{
    content:'';position:absolute;inset:0;
    background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.5) 50%,transparent 70%);
    transform:translateX(-130%);transition:transform .5s ease;
  }
  .btn:hover::after{transform:translateX(130%)}
  .btn:hover{transform:translateY(-2px)}
  .btn:active{transform:translateY(0) scale(.97)}
  .b-fish{background:linear-gradient(135deg,#3ee6ff,#1fa8ff)}
  .b-fish:hover{box-shadow:0 8px 22px rgba(62,230,255,.4)}
  .b-bub{background:linear-gradient(135deg,#7db8ff,#3b82f6);color:#fff}
  .b-bub:hover{box-shadow:0 8px 22px rgba(90,160,255,.4)}
  .b-light{background:linear-gradient(135deg,#ffd166,#ff9f43)}
  .b-light:hover{box-shadow:0 8px 22px rgba(255,190,80,.4)}
  .b-light.off{background:linear-gradient(135deg,#5b6b8c,#31415f);color:#cfe0ff}
  .btn .tag{font-size:10px;font-weight:800;opacity:.75}

  /* ---------- Статистика ---------- */
  #stats h2{font-family:'Russo One';font-size:11px;letter-spacing:3px;color:var(--dim);text-transform:uppercase;margin-bottom:10px}
  .stat{
    display:flex;justify-content:space-between;align-items:baseline;
    padding:7px 0;border-bottom:1px dashed rgba(120,205,255,.15);
    font-size:12px;color:var(--dim);
  }
  .stat:last-child{border:none}
  .stat b{font-family:'Russo One';font-size:18px;color:var(--txt);display:inline-block}
  #fps{color:var(--teal)}
  .pop{animation:pop .35s ease}
  @keyframes pop{40%{transform:scale(1.4);color:var(--cyan)}}

  /* ---------- Подсказка / тосты / float ---------- */
  #hint{
    position:fixed;left:50%;bottom:26px;transform:translateX(-50%);z-index:10;
    display:flex;gap:10px;align-items:center;
    background:var(--panel);border:1px solid var(--line);border-radius:999px;
    padding:10px 20px;font-size:13px;font-weight:600;
    backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    transition:opacity .8s ease, transform .8s ease;
  }
  #hint .dot{width:9px;height:9px;border-radius:50%;background:var(--amber);box-shadow:0 0 10px var(--amber);animation:pulse 1.6s infinite}
  @keyframes pulse{50%{transform:scale(1.6);opacity:.5}}
  #hint.hide{opacity:0;transform:translate(-50%,16px);pointer-events:none}

  #toasts{position:fixed;right:20px;bottom:22px;z-index:20;display:flex;flex-direction:column;gap:8px;align-items:flex-end}
  .toast{
    background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--cyan);
    padding:9px 16px;border-radius:10px;font-size:12.5px;font-weight:600;
    backdrop-filter:blur(10px);animation:tin .3s ease;transition:opacity .4s,transform .4s;
  }
  .toast.out{opacity:0;transform:translateX(20px)}
  @keyframes tin{from{opacity:0;transform:translateX(24px)}}

  .float{
    position:fixed;z-index:15;font-family:'Russo One';font-size:14px;color:var(--amber);
    text-shadow:0 0 10px rgba(255,200,80,.8);pointer-events:none;animation:rise 1s ease forwards;
  }
  @keyframes rise{to{transform:translateY(-46px);opacity:0}}

  /* ---------- Загрузчик ---------- */
  #loader{
    position:fixed;inset:0;z-index:50;display:flex;flex-direction:column;gap:18px;
    align-items:center;justify-content:center;
    background:radial-gradient(circle at 50% 40%,#0a2a55,#030d1f 70%);
    transition:opacity .7s ease;
  }
  #loader.hide{opacity:0;pointer-events:none}
  .ring{width:52px;height:52px;border-radius:50%;border:3px solid rgba(62,230,255,.2);border-top-color:var(--cyan);animation:spin 1s linear infinite}
  @keyframes spin{to{transform:rotate(360deg)}}
  #loader p{font-family:'Russo One';letter-spacing:4px;font-size:12px;color:var(--dim);animation:blink 1.4s infinite}
  @keyframes blink{50%{opacity:.4}}

  @media(max-width:760px){
    #info{width:225px;padding:14px}
    .controls li:nth-child(n+3){display:none}
    #stats{width:150px;padding:12px 14px}
    h1{font-size:19px}
  }
</style>
</head>
<body>

<canvas id="scene"></canvas>

<!-- ======== Панель информации ======== -->
<div class="panel" id="info">
  <div class="logo">
    <svg viewBox="0 0 52 32">
      <defs><linearGradient id="gf" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#3ee6ff"/><stop offset="1" stop-color="#2bd9a0"/>
      </linearGradient></defs>
      <path d="M40 16 L50 7 L47 16 L50 25 Z" fill="url(#gf)"/>
      <path d="M2 16 Q 12 3 26 6 Q 38 9 41 16 Q 38 23 26 26 Q 12 29 2 16 Z" fill="url(#gf)"/>
      <circle cx="10" cy="14" r="2.2" fill="#062038"/>
    </svg>
    <h1>АКВАРИУМ</h1>
  </div>
  <div class="sub">Интерактивный 3D · Three.js</div>
  <ul class="controls">
    <li><span class="key">ЛКМ</span> вращение камеры</li>
    <li><span class="key">ПКМ</span> перемещение</li>
    <li><span class="key">Колесо</span> зум (10–60)</li>
    <li><span class="key">Клик</span> бросить корм 🐟</li>
  </ul>
  <div class="btns">
    <button class="btn b-fish"  id="btnFish">+ Добавить рыбку <span class="tag">🐠</span></button>
    <button class="btn b-bub"   id="btnBub">+ Больше пузырей <span class="tag">🫧</span></button>
    <button class="btn b-light" id="btnLight">☀ Свет <span class="tag">ВКЛ</span></button>
  </div>
</div>

<!-- ======== Статистика ======== -->
<div class="panel" id="stats">
  <h2>Статистика</h2>
  <div class="stat"><span>Рыбки</span><b id="sFish">0</b></div>
  <div class="stat"><span>Корм</span><b id="sFood">0</b></div>
  <div class="stat"><span>Съедено</span><b id="sEaten">0</b></div>
  <div class="stat"><span>FPS</span><b id="fps">—</b></div>
</div>

<div id="hint"><span class="dot"></span> Кликните по аквариуму, чтобы покормить рыбок</div>
<div id="toasts"></div>
<div id="loader"><div class="ring"></div><p>ЗАПУСК АКВАРИУМА…</p></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function(){
'use strict';

/* ================= Утилиты ================= */
const rand  = (a,b)=>a+Math.random()*(b-a);
const pick  = a=>a[Math.floor(Math.random()*a.length)];
const clamp = THREE.MathUtils.clamp;

/* ================= Сцена / рендерер ================= */
const canvas   = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.setClearColor(0x000000,0);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type    = THREE.PCFSoftShadowMap;
renderer.outputEncoding    = THREE.sRGBEncoding;
renderer.toneMapping       = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0d3560, 0.011);          // имитация воды

const camera = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, 0.1, 300);
camera.position.set(26, 11, 31);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance   = 10;
controls.maxDistance   = 60;
controls.maxPolarAngle = Math.PI/1.8;
controls.target.set(0,-1,0);

/* ================= Константы аквариума ================= */
const TANK_W=36, TANK_H=24, TANK_D=20;
const BX=16.5, BY=10.5, BZ=8.5;      // границы для рыбок
const SAND_Y=-11.4;

/* ================= Освещение ================= */
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xfff1d6, 1.0);
sun.position.set(18,28,12);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-26; sun.shadow.camera.right=26;
sun.shadow.camera.top=20;   sun.shadow.camera.bottom=-20;
sun.shadow.camera.near=5;   sun.shadow.camera.far=70;
sun.shadow.bias=-0.0004;
sun.shadow.camera.updateProjectionMatrix();
scene.add(sun);

const pl1 = new THREE.PointLight(0x3fd0ff, 0.55, 45);  // голубой
pl1.position.set(-14,5,9);
const pl2 = new THREE.PointLight(0x2b6bff, 0.5, 45);   // синий
pl2.position.set(13,-5,-9);
scene.add(pl1, pl2);

const lightState   = {day:true};
const lightTargets = {sun:1.0, amb:0.4, p1:0.55, p2:0.5,
                      fog:new THREE.Color(0x0d3560), fogD:0.011};

function setLight(day){
  lightState.day = day;
  document.body.classList.toggle('night', !day);
  if(day){
    Object.assign(lightTargets,{sun:1.0, amb:0.4, p1:0.55, p2:0.5, fogD:0.011});
    lightTargets.fog.set(0x0d3560);
  }else{
    Object.assign(lightTargets,{sun:0.06, amb:0.22, p1:1.0, p2:0.85, fogD:0.014});
    lightTargets.fog.set(0x041226);
  }
  const b=document.getElementById('btnLight');
  b.classList.toggle('off', !day);
  b.innerHTML = day ? '☀ Свет <span class="tag">ВКЛ</span>'
                    : '🌙 Свет <span class="tag">ВЫКЛ</span>';
}

/* ================= Стекло + рама + подставка ================= */
const glassGeo = new THREE.BoxGeometry(TANK_W,TANK_H,TANK_D);
const glassMat = new THREE.MeshPhysicalMaterial({
  color:0x9fd8ff, metalness:0, roughness:0.06,
  transmission:0.95, thickness:1.5, ior:1.33,
  clearcoat:1, clearcoatRoughness:0.08,
  side:THREE.DoubleSide
});
const glass = new THREE.Mesh(glassGeo, glassMat);
scene.add(glass);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(glassGeo),
  new THREE.LineBasicMaterial({color:0x9fe8ff, transparent:true, opacity:0.5})
);
scene.add(edges);

const base = new THREE.Mesh(
  new THREE.BoxGeometry(TANK_W+3, 1.2, TANK_D+3),
  new THREE.MeshStandardMaterial({color:0x0e1c30, roughness:0.6, metalness:0.3})
);
base.position.y = -TANK_H/2 - 0.6;
base.receiveShadow = true;
scene.add(base);

/* ================= Песок (процедурный) ================= */
const sandGeo = new THREE.PlaneGeometry(TANK_W, TANK_D, 56, 40);
sandGeo.rotateX(-Math.PI/2);
{
  const p = sandGeo.attributes.position;
  for(let i=0;i<p.count;i++){
    const x=p.getX(i), z=p.getZ(i);
    p.setY(i,
      0.35*Math.sin(x*0.45)*Math.cos(z*0.6) +
      0.22*Math.sin(x*0.9+z*1.3) +
      0.12*Math.sin(z*2.1+x*0.3) +
      (Math.random()-0.5)*0.08
    );
  }
  sandGeo.computeVertexNormals();
}
const sand = new THREE.Mesh(sandGeo,
  new THREE.MeshStandardMaterial({color:0xdec48f, roughness:0.95}));
sand.position.y = SAND_Y;
sand.receiveShadow = true;
scene.add(sand);

/* ================= Камни (8 деформированных додекаэдров) ================= */
const ROCK_COLORS=[0x6b7280,0x57606f,0x7a6a58,0x4f5b6b,0x8a7f6d];
for(let i=0;i<8;i++){
  const r = rand(0.9,2.0);
  const g = new THREE.DodecahedronGeometry(r,0);
  const p = g.attributes.position;
  for(let j=0;j<p.count;j++){
    p.setXYZ(j,
      p.getX(j)*(1+rand(-0.25,0.25)),
      p.getY(j)*(1+rand(-0.25,0.25)),
      p.getZ(j)*(1+rand(-0.25,0.25)));
  }
  g.computeVertexNormals();
  const rock = new THREE.Mesh(g, new THREE.MeshStandardMaterial({
    color:pick(ROCK_COLORS), roughness:0.9, flatShading:true
  }));
  rock.position.set(rand(-14,14), SAND_Y+0.3-r*0.25, rand(-7.5,7.5));
  rock.rotation.set(rand(0,Math.PI),rand(0,Math.PI),rand(0,Math.PI));
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

/* ================= Водоросли (12 кустов, TubeGeometry) ================= */
const ALGAE_GREENS=[0x2f9e44,0x37b24d,0x52c41a,0x74c69d,0x40916c];
const algaeList=[];
for(let i=0;i<12;i++){
  const clump = new THREE.Group();
  const blades=[];
  const n = 3+Math.floor(Math.random()*3);
  const baseHue = pick(ALGAE_GREENS);
  for(let b=0;b<n;b++){
    const h=rand(2.2,5.5), sway=rand(0.5,1.4);
    const rx=rand(-sway,sway), rz=rand(-sway,sway);
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0,0,0),
      new THREE.Vector3(rx*0.3, h*0.35, rz*0.3),
      new THREE.Vector3(rx*0.7, h*0.7,  rz*0.7),
      new THREE.Vector3(rx*1.5, h,      rz*1.5)
    ]);
    const col = new THREE.Color(baseHue).offsetHSL(rand(-0.03,0.03),0,rand(-0.06,0.06));
    const blade = new THREE.Mesh(
      new THREE.TubeGeometry(curve,10,rand(0.06,0.13),6,false),
      new THREE.MeshStandardMaterial({color:col, roughness:0.7,
        emissive:col.clone().multiplyScalar(0.12)})
    );
    blade.rotation.y = rand(0,Math.PI*2);
    clump.add(blade);
    blades.push(blade);
  }
  clump.position.set(rand(-15,15), SAND_Y+0.15, rand(-7.5,7.5));
  scene.add(clump);
  algaeList.push({blades, speed:rand(0.7,1.6), phase:rand(0,6.28)});
}

/* ================= Пузыри (30 на старте) ================= */
const bubbleGeo = new THREE.SphereGeometry(1,12,10);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color:0xcfeeff, metalness:0, roughness:0.05,
  transparent:true, opacity:0.28, clearcoat:1, clearcoatRoughness:0
});
const bubbles=[];
function addBubble(atPos){
  const m = new THREE.Mesh(bubbleGeo, bubbleMat);
  const s = rand(0.12,0.4);
  m.scale.setScalar(s);
  let x,y,z;
  if(atPos){ x=atPos.x+rand(-0.5,0.5); y=atPos.y+rand(-0.3,0.3); z=atPos.z+rand(-0.5,0.5); }
  else     { x=rand(-16,16); y=rand(-11,10); z=rand(-8,8); }
  m.position.set(x,y,z);
  scene.add(m);
  bubbles.push({mesh:m, baseX:x, baseZ:z,
    speed:rand(1.2,3), amp:rand(0.25,0.7), freq:rand(1,3), phase:rand(0,6.28)});
}
for(let i=0;i<30;i++) addBubble();

function updateBubbles(dt,t){
  for(const b of bubbles){
    b.mesh.position.y += b.speed*dt;
    b.mesh.position.x  = b.baseX + Math.sin(t*b.freq   + b.phase)*b.amp;
    b.mesh.position.z  = b.baseZ + Math.cos(t*b.freq*0.8 + b.phase)*b.amp;
    if(b.mesh.position.y > 10.8){               // сброс на поверхность
      b.mesh.position.y = -11;
      b.baseX = rand(-16,16); b.baseZ = rand(-8,8);
      b.mesh.position.x = b.baseX; b.mesh.position.z = b.baseZ;
    }
  }
}

/* ================= Корм ================= */
const foodGeo = new THREE.SphereGeometry(0.28,10,8);
const foodItems=[];

function dropFood(pos){
  const m = new THREE.Mesh(foodGeo, new THREE.MeshStandardMaterial({
    color:0xffa94d, emissive:0x552200, roughness:0.55
  }));
  m.position.copy(pos);
  m.castShadow = true;
  scene.add(m);
  foodItems.push({mesh:m,
    vel:new THREE.Vector3(rand(-0.4,0.4),0,rand(-0.4,0.4)),
    spin:rand(1,3)});
  for(let i=0;i<3;i++) addBubble(pos);
  refreshStats();
}
function removeFood(fi){
  scene.remove(fi.mesh);
  const i=foodItems.indexOf(fi);
  if(i>-1) foodItems.splice(i,1);
  refreshStats();
}
function updateFood(dt,t){
  for(let i=foodItems.length-1;i>=0;i--){
    const fi=foodItems[i];
    fi.vel.y -= 3.5*dt;                        // гравитация
    fi.vel.multiplyScalar(1-0.5*dt);           // сопротивление воды
    fi.mesh.position.addScaledVector(fi.vel,dt);
    fi.mesh.rotation.y += fi.spin*dt;
    if(fi.mesh.position.y < SAND_Y+0.35) removeFood(fi);  // упало на дно
  }
}

/* ================= Рыбки ================= */
const SCHEMES=[
  {body:0xff8c2e, fin:0xffc169, belly:0xffe3b8},              // оранжевая
  {body:0x2f7bff, fin:0x8fd0ff, belly:0xd6ecff},              // синяя
  {body:0xffc93c, fin:0xff4d4d, belly:0xfff1b8},              // жёлто-красная
  {body:0x9b5de5, fin:0xd8b4fe, belly:0xe9d5ff},              // фиолетовая
  {body:0xef3e36, fin:0xff9b92, belly:0xffd9d4},              // красная
  {body:0x37b24d, fin:0xa8e05f, belly:0xdcf2c8},              // зелёная
  {body:0xff6fae, fin:0xffc2dc, belly:0xffe6f1},              // розовая
  {body:0xffc94d, fin:0xe0a106, belly:0xffeaa8, metal:0.6}    // золотая
];

const fishArray=[];
const _euler = new THREE.Euler(0,0,0,'YXZ');
const _quat  = new THREE.Quaternion();
const _steer = new THREE.Vector3();

function createFish(position){
  const scheme = pick(SCHEMES);
  const scale  = rand(0.6,1.2);
  const g = new THREE.Group();

  const bodyMat  = new THREE.MeshStandardMaterial({color:scheme.body,  roughness:0.35, metalness:scheme.metal||0.08});
  const finMat   = new THREE.MeshStandardMaterial({color:scheme.fin,   roughness:0.5,  transparent:true, opacity:0.92});
  const bellyMat = new THREE.MeshStandardMaterial({color:scheme.belly, roughness:0.45});

  // тело — вытянутая сфера
  const body = new THREE.Mesh(new THREE.SphereGeometry(1,20,16), bodyMat);
  body.scale.set(0.5,0.42,0.95);
  body.castShadow = true;
  g.add(body);

  // брюшко светлее
  const belly = new THREE.Mesh(new THREE.SphereGeometry(1,16,12), bellyMat);
  belly.scale.set(0.4,0.3,0.78);
  belly.position.set(0,-0.13,0.06);
  g.add(belly);

  // глаза + зрачки
  const eyeGeo=new THREE.SphereGeometry(0.13,10,8), pupGeo=new THREE.SphereGeometry(0.06,8,6);
  const eyeMat=new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.25});
  const pupMat=new THREE.MeshStandardMaterial({color:0x101010, roughness:0.1});
  [-1,1].forEach(s=>{
    const e=new THREE.Mesh(eyeGeo,eyeMat); e.position.set(s*0.27,0.15,0.50); g.add(e);
    const p=new THREE.Mesh(pupGeo,pupMat); p.position.set(s*0.31,0.15,0.58); g.add(p);
  });

  // хвост (пивот для вращения по Z)
  const tailPivot = new THREE.Group();
  tailPivot.position.z = -0.82;
  const tailGeo = new THREE.ConeGeometry(0.5,0.9,10);
  tailGeo.rotateX(-Math.PI/2);
  tailGeo.translate(0,0,-0.42);
  const tail = new THREE.Mesh(tailGeo, finMat);
  tail.scale.set(0.22,1,1);
  tail.castShadow = true;
  tailPivot.add(tail);
  g.add(tailPivot);

  // спинной плавник
  const dorsalGeo = new THREE.ConeGeometry(0.38,0.55,10);
  dorsalGeo.scale(0.18,1,1);
  const dorsal = new THREE.Mesh(dorsalGeo, finMat);
  dorsal.position.set(0,0.46,-0.18);
  dorsal.rotation.x = -0.35;
  g.add(dorsal);

  // боковые плавники
  const finGeo = new THREE.SphereGeometry(0.3,10,8);
  const leftFin = new THREE.Mesh(finGeo, finMat);
  leftFin.scale.set(0.09,0.22,0.5);
  leftFin.position.set(-0.4,-0.05,0.18);
  leftFin.rotation.z = 0.75;
  g.add(leftFin);
  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.scale.set(0.09,0.22,0.5);
  rightFin.position.set(0.4,-0.05,0.18);
  rightFin.rotation.z = -0.75;
  g.add(rightFin);

  g.scale.setScalar(scale);
  if(position) g.position.copy(position);
  else g.position.set(rand(-14,14), rand(-8,8), rand(-6.5,6.5));
  scene.add(g);

  const fish={
    mesh:g, tail, leftFin, rightFin, dorsal,
    velocity:new THREE.Vector3(rand(-1,1),rand(-0.3,0.3),rand(-1,1))
                .normalize().multiplyScalar(rand(1.5,3)),
    speed:rand(2.2,4),
    tailSpeed:rand(5,9),
    phase:rand(0,Math.PI*2),
    targetFood:null,
    avoidanceRadius:rand(1.6,2.6)+scale,
    wanderDir:new THREE.Vector3(rand(-1,1),rand(-0.3,0.3),rand(-1,1)).normalize(),
    wanderTimer:rand(1,4),
    baseLF:0.75, baseRF:-0.75
  };
  fishArray.push(fish);
  return fish;
}
for(let i=0;i<15;i++) createFish();

function updateFish(f,dt,t){
  const p = f.mesh.position;

  // --- поиск корма (радиус 15) ---
  let food=null, best=15;
  for(const fi of foodItems){
    const d=p.distanceTo(fi.mesh.position);
    if(d<best){best=d; food=fi;}
  }
  f.targetFood=food;

  // --- руление ---
  _steer.set(0,0,0);
  if(food){
    _steer.copy(food.mesh.position).sub(p).normalize().multiplyScalar(f.speed*1.9);
  }else{
    f.wanderTimer-=dt;
    if(f.wanderTimer<=0){
      f.wanderTimer=rand(2,6);
      f.wanderDir.set(rand(-1,1),rand(-0.4,0.4),rand(-1,1)).normalize();
    }
    _steer.copy(f.wanderDir).multiplyScalar(f.speed);
  }

  // --- избегание столкновений ---
  for(const o of fishArray){
    if(o===f) continue;
    const op=o.mesh.position;
    const dx=p.x-op.x, dy=p.y-op.y, dz=p.z-op.z;
    const r=f.avoidanceRadius, d2=dx*dx+dy*dy+dz*dz;
    if(d2<r*r && d2>1e-4){
      const d=Math.sqrt(d2), k=(1-d/r)*5;
      _steer.x+=dx/d*k; _steer.y+=dy/d*k; _steer.z+=dz/d*k;
    }
  }

  // --- мягкое отражение от стен ---
  const M=3, K=12;
  if(p.x> BX-M) _steer.x-=(p.x-( BX-M))/M*K;
  if(p.x<-BX+M) _steer.x+=((-BX+M)-p.x)/M*K;
  if(p.y> BY-M) _steer.y-=(p.y-( BY-M))/M*K;
  if(p.y<-BY+M) _steer.y+=((-BY+M)-p.y)/M*K;
  if(p.z> BZ-M) _steer.z-=(p.z-( BZ-M))/M*K;
  if(p.z<-BZ+M) _steer.z+=((-BZ+M)-p.z)/M*K;
  _steer.y -= p.y*0.03;   // лёгкое удержание в середине воды

  // --- интеграция ---
  f.velocity.lerp(_steer, 1-Math.exp(-dt*2.2));
  const sp=f.velocity.length();
  const maxS = food ? f.speed*2.3 : f.speed*1.5;
  if(sp>maxS) f.velocity.multiplyScalar(maxS/sp);
  p.addScaledVector(f.velocity,dt);
  // жёсткий предел + отражение
  if(p.x> BX){p.x= BX; f.velocity.x*=-0.5;} else if(p.x<-BX){p.x=-BX; f.velocity.x*=-0.5;}
  if(p.y> BY){p.y= BY; f.velocity.y*=-0.5;} else if(p.y<-BY){p.y=-BY; f.velocity.y*=-0.5;}
  if(p.z> BZ){p.z= BZ; f.velocity.z*=-0.5;} else if(p.z<-BZ){p.z=-BZ; f.velocity.z*=-0.5;}

  // --- поедание: удалить корм + рост 5% ---
  if(food && p.distanceTo(food.mesh.position) < 1.0 + f.mesh.scale.x*0.35){
    removeFood(food);
    if(f.mesh.scale.x < 2.2) f.mesh.scale.multiplyScalar(1.05);
    for(let i=0;i<4;i++) addBubble(p);
    stats.eaten++;
    popEl(elEaten);
    floatText(p, '+5%');
    refreshStats();
  }

  // --- поворот в направлении движения ---
  const v=f.velocity, len=v.length()||1;
  _euler.set(
    Math.asin(clamp(v.y/len,-1,1)),
    Math.atan2(v.x,v.z),
    Math.sin(t*f.tailSpeed*0.5+f.phase)*0.12
  );
  _quat.setFromEuler(_euler);
  f.mesh.quaternion.slerp(_quat, 1-Math.exp(-dt*4));

  // --- анимация хвоста и плавников ---
  const wag=Math.sin(t*f.tailSpeed+f.phase);
  f.tail.rotation.z     = wag*0.55;
  f.leftFin.rotation.z  = f.baseLF  + Math.sin(t*f.tailSpeed*0.8+f.phase)*0.3;
  f.rightFin.rotation.z = f.baseRF - Math.sin(t*f.tailSpeed*0.8+f.phase+0.6)*0.3;
  f.dorsal.rotation.x   = -0.35 + Math.sin(t*f.tailSpeed*0.6+f.phase)*0.1;
}

/* ================= Кормление кликом (raycaster) ================= */
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let downPos=null;
renderer.domElement.addEventListener('pointerdown', e=>{
  if(e.button===0) downPos={x:e.clientX, y:e.clientY};
});
window.addEventListener('pointerup', e=>{
  if(e.button!==0 || !downPos) return;
  if(e.target!==renderer.domElement){ downPos=null; return; }   // клик по UI
  const dx=e.clientX-downPos.x, dy=e.clientY-downPos.y;
  downPos=null;
  if(dx*dx+dy*dy>36) return;                                    // это было вращение
  ndc.x=(e.clientX/innerWidth)*2-1;
  ndc.y=-(e.clientY/innerHeight)*2+1;
  raycaster.setFromCamera(ndc,camera);
  const hits=raycaster.intersectObject(glass,false);
  if(!hits.length) return;
  const pt=hits[0].point;
  pt.x=clamp(pt.x,-16,16); pt.y=clamp(pt.y,-10.5,10.5); pt.z=clamp(pt.z,-8,8);
  dropFood(pt);
  document.getElementById('hint').classList.add('hide');
});

/* ================= UI ================= */
const elFish=document.getElementById('sFish'),
      elFood=document.getElementById('sFood'),
      elEaten=document.getElementById('sEaten'),
      elFps=document.getElementById('fps');
const stats={eaten:0};

function refreshStats(){
  elFish.textContent=fishArray.length;
  elFood.textContent=foodItems.length;
  elEaten.textContent=stats.eaten;
}
function popEl(el){ el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); }

function toast(msg){
  const box=document.getElementById('toasts');
  const el=document.createElement('div');
  el.className='toast'; el.textContent=msg;
  box.appendChild(el);
  setTimeout(()=>el.classList.add('out'),1800);
  setTimeout(()=>el.remove(),2300);
}
function floatText(worldPos,text){
  const v=worldPos.clone().project(camera);
  const el=document.createElement('div');
  el.className='float'; el.textContent=text;
  el.style.left=((v.x*0.5+0.5)*innerWidth)+'px';
  el.style.top =((-v.y*0.5+0.5)*innerHeight)+'px';
  document.body.appendChild(el);
  setTimeout(()=>el.remove(),1000);
}

document.getElementById('btnFish').onclick=()=>{
  if(fishArray.length>=40){ toast('Максимум 40 рыбок'); return; }
  createFish();
  popEl(elFish); refreshStats();
  toast('+1 рыбка 🐠');
};
document.getElementById('btnBub').onclick=()=>{
  for(let i=0;i<10;i++) addBubble();
  toast('+10 пузырей 🫧');
};
document.getElementById('btnLight').onclick=()=> setLight(!lightState.day);

/* ================= FPS ================= */
let frames=0, fpsTime=performance.now();
function tickFps(){
  frames++;
  const now=performance.now();
  if(now-fpsTime>=500){
    elFps.textContent=Math.round(frames*1000/(now-fpsTime));
    frames=0; fpsTime=now;
  }
}

/* ================= Анимация света (день/ночь) ================= */
function updateLights(dt,t){
  const k=1-Math.exp(-dt*2);
  sun.intensity     += (lightTargets.sun-sun.intensity)*k;
  ambient.intensity += (lightTargets.amb-ambient.intensity)*k;
  pl1.intensity     += (lightTargets.p1-pl1.intensity)*k;
  pl2.intensity     += (lightTargets.p2-pl2.intensity)*k;
  scene.fog.color.lerp(lightTargets.fog,k);
  scene.fog.density += (lightTargets.fogD-scene.fog.density)*k;
  pl1.intensity += Math.sin(t*1.3)*0.06;   // лёгкое «дыхание» света
  pl2.intensity += Math.cos(t*1.1)*0.05;
}

/* ================= Анимация водорослей ================= */
function updateAlgae(t){
  for(const a of algaeList){
    for(const b of a.blades){
      b.rotation.x = Math.sin(t*a.speed   + a.phase)*0.1;
      b.rotation.z = Math.cos(t*a.speed*0.8 + a.phase)*0.1;
    }
  }
}

/* ================= Resize ================= */
window.addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* ================= Главный цикл ================= */
refreshStats();
const clock=new THREE.Clock();

function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05);
  const t=clock.elapsedTime;

  for(const f of fishArray) updateFish(f,dt,t);
  updateFood(dt,t);
  updateBubbles(dt,t);
  updateAlgae(t);
  updateLights(dt,t);

  controls.update();
  renderer.render(scene,camera);
  tickFps();
}
animate();

setTimeout(()=>document.getElementById('loader').classList.add('hide'),700);
})();
</script>
</body>
</html>
```

**Что внутри и как это работает**

- **Рыбки** — тело из двух сфер (спина + светлое брюшко), глаза с зрачками, хвост-конус на пивоте (вращение по Z), спинной и два боковых плавника. 8 схем (золотая — с metalness 0.6), масштаб 0.6–1.2, у каждой своя скорость, фаза и частота маха. Поворот — сферическая интерполяция кватерниона по вектору скорости (yaw + pitch + лёгкий крен).
- **ИИ** — каждый кадр: поиск корма в радиусе 15 → погоня (скорость ×1.9); иначе блуждание с таймером смены курса; O(n²)-разделение с индивидуальным `avoidanceRadius`; мягкие силы у стен + жёсткое отражение как страховка. Съели — удаление, `scale × 1.05` (кап 2.2), всплеск пузырей и летящая метка «+5%».
- **Кормление** — клик (не драг, проверка смещения < 6px) → raycast по стеклу → точка клампится внутрь аквариума, корм падает с гравитацией и сопротивлением воды, исчезает на песке.
- **День/ночь** — кнопка плавно (экспоненциальный lerp) переводит солнце/фон/туман/точечные источники в ночной режим, фон страницы тоже меняется с CSS-переходом.
- **Производительность** — дельта-время везде, шары/трубы низкополигональные, общий `bubbleGeo`, тень только с тела рыбки; лимит 40 рыбок.

Если хотите, могу добавить: следование курсору («рыбки смотрят за мышкой»), звук бульканья, или сохранение размера рыбок в `localStorage`.