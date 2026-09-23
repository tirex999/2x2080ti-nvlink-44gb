

Готово — полный файл `aquarium.html`, который достаточно открыть в браузере. Всё по ТЗ: 15 рыбок с ИИ, кормление кликом, рост, пузыри, водоросли, камни, стекло с преломлением, туман, тени и стеклянный UI.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Аквариум — Интерактивная экосистема</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Russo+One&family=Rubik:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  *{ margin:0; padding:0; box-sizing:border-box }
  html,body{ height:100% }
  body{
    overflow:hidden;
    font-family:'Rubik',sans-serif;
    color:#dceeff;
    background:linear-gradient(180deg,#02101f 0%,#06304f 55%,#0a4a72 100%);
  }
  canvas{ display:block; cursor:crosshair }

  #vignette{
    position:fixed; inset:0; pointer-events:none; z-index:2;
    background:radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(1,8,20,.55) 100%);
  }

  /* ---------- Панели (glass UI) ---------- */
  .panel{
    position:fixed; z-index:10;
    background:rgba(5,24,46,.58);
    backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
    border:1px solid rgba(110,210,255,.22);
    box-shadow:0 12px 40px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.07);
    padding:16px 18px;
    animation:drop .8s cubic-bezier(.18,.9,.32,1.25) backwards;
  }
  @keyframes drop{ from{ opacity:0; transform:translateY(-16px) } }

  #info{ top:18px; left:18px; max-width:272px; border-radius:20px 20px 20px 4px; animation-delay:.15s }
  #info h1{
    font-family:'Russo One',sans-serif; font-size:26px; letter-spacing:.5px;
    background:linear-gradient(90deg,#5eead4,#4dc3ff);
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .tag{ display:block; margin-top:4px; font-size:10.5px; letter-spacing:1.6px; text-transform:uppercase; color:#7fb6d9 }
  .desc{ list-style:none; margin:13px 0 14px; display:grid; gap:6px; font-size:12.5px; color:#b9d9ef }
  .desc b{ color:#6fe0ff; font-weight:600 }

  .actions{ display:flex; flex-wrap:wrap; gap:8px }
  .btn{
    font-family:'Rubik',sans-serif; font-size:12.5px; font-weight:600; letter-spacing:.3px;
    color:#eaf7ff; padding:9px 13px; border-radius:10px; cursor:pointer;
    border:1px solid rgba(140,220,255,.35);
    background:linear-gradient(135deg, rgba(20,120,190,.9), rgba(16,165,150,.9));
    box-shadow:0 4px 14px rgba(0,15,35,.45);
    transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease, filter .18s ease;
  }
  .btn:hover{ transform:translateY(-2px); box-shadow:0 8px 24px rgba(45,190,255,.35); border-color:rgba(190,240,255,.75); filter:brightness(1.1) }
  .btn:active{ transform:translateY(0) scale(.96) }
  .btn.off{ background:linear-gradient(135deg, rgba(38,58,92,.9), rgba(26,40,66,.9)); border-color:rgba(120,150,200,.3) }

  #stats{ top:18px; right:18px; border-radius:4px 20px 20px 20px; display:grid; grid-template-columns:auto auto; gap:8px 22px; animation-delay:.3s }
  .stat{ display:flex; align-items:baseline; gap:8px }
  .s-label{ font-size:9.5px; letter-spacing:1.4px; text-transform:uppercase; color:#7fb6d9 }
  .s-val{
    display:inline-block; min-width:34px; text-align:right;
    font-family:'Russo One',sans-serif; font-size:21px; color:#5fd8ff;
    text-shadow:0 0 14px rgba(80,200,255,.5);
  }
  .s-val.bump{ animation:bump .45s ease }
  @keyframes bump{ 35%{ transform:scale(1.35); color:#fff } }

  #hint{
    position:fixed; bottom:18px; left:0; right:0; margin:0 auto; width:max-content; max-width:92vw;
    z-index:10; font-size:12px; color:#b9d9ef; padding:9px 16px; text-align:center;
    background:rgba(5,24,46,.55); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(110,210,255,.2); border-radius:999px;
    box-shadow:0 8px 26px rgba(0,0,0,.4);
    animation:drop .8s .5s cubic-bezier(.18,.9,.32,1.25) backwards, pulse 3.5s 1.5s ease-in-out infinite;
  }
  #hint b{ color:#6fe0ff }
  @keyframes pulse{ 50%{ box-shadow:0 8px 30px rgba(60,190,255,.3) } }

  /* ---------- Экран загрузки ---------- */
  #loader{
    position:fixed; inset:0; z-index:100; display:flex; align-items:center; justify-content:center;
    background:linear-gradient(180deg,#02101f,#06304f); transition:opacity .8s ease;
  }
  #loader.done{ opacity:0; pointer-events:none }
  .l-box{ position:relative; width:230px; height:160px; text-align:center }
  .l-title{
    font-family:'Russo One',sans-serif; font-size:30px;
    background:linear-gradient(90deg,#5eead4,#4dc3ff);
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .l-sub{ margin-top:8px; font-size:11px; letter-spacing:2px; text-transform:uppercase; color:#7fb6d9 }
  .l-bub{ position:absolute; inset:0; overflow:hidden }
  .l-bub i{ position:absolute; bottom:-12px; width:9px; height:9px; border-radius:50%; background:rgba(130,215,255,.55); animation:rise 1.9s linear infinite }
  .l-bub i:nth-child(1){ left:15% }
  .l-bub i:nth-child(2){ left:35%; width:6px; height:6px; animation-delay:.5s }
  .l-bub i:nth-child(3){ left:55%; animation-delay:1s }
  .l-bub i:nth-child(4){ left:72%; width:5px; height:5px; animation-delay:.3s }
  .l-bub i:nth-child(5){ left:88%; width:7px; height:7px; animation-delay:.8s }
  @keyframes rise{ to{ transform:translateY(-170px); opacity:0 } }

  @media (max-width:640px){
    .desc{ display:none }
    #info{ max-width:212px; padding:12px 14px }
    #info h1{ font-size:20px }
    .btn{ font-size:11.5px; padding:8px 10px }
    #stats{ padding:10px 14px; gap:6px 14px }
    .s-val{ font-size:16px }
    #hint{ font-size:10.5px; padding:8px 12px }
  }
</style>
</head>
<body>

<div id="loader">
  <div class="l-box">
    <div class="l-title">3D Аквариум</div>
    <div class="l-sub">Подготовка аквариума…</div>
    <div class="l-bub"><i></i><i></i><i></i><i></i><i></i></div>
  </div>
</div>

<div id="vignette"></div>

<section class="panel" id="info">
  <header>
    <h1>3D Аквариум</h1>
    <span class="tag">Интерактивная экосистема · Three.js</span>
  </header>
  <ul class="desc">
    <li><b>ЛКМ + движение</b> — вращение камеры</li>
    <li><b>ПКМ + движение</b> — панорамирование</li>
    <li><b>Колесо мыши</b> — зум</li>
    <li><b>Клик по воде</b> — покормить рыбок</li>
  </ul>
  <div class="actions">
    <button class="btn" id="btnFish">＋ Добавить рыбку</button>
    <button class="btn" id="btnBubbles">🫧 Больше пузырей</button>
    <button class="btn" id="btnLight">💡 Свет: вкл</button>
  </div>
</section>

<section class="panel" id="stats">
  <div class="stat"><span class="s-label">Рыбки</span><span class="s-val" id="fishCount">0</span></div>
  <div class="stat"><span class="s-label">Пузыри</span><span class="s-val" id="bubbleCount">0</span></div>
  <div class="stat"><span class="s-label">Корм</span><span class="s-val" id="foodCount">0</span></div>
  <div class="stat"><span class="s-label">FPS</span><span class="s-val" id="fps">—</span></div>
</section>

<div id="hint">🖱 Перетаскивание — вращение · Колесо — зум · <b>Клик по воде — корм</b></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ================================================================
   3D АКВАРИУМ
   ================================================================ */
const W = 36, H = 24, D = 20;                       // размеры аквариума
const rand = (a, b) => a + Math.random() * (b - a);
const fract = x => x - Math.floor(x);
const el = id => document.getElementById(id);
const X_AXIS = new THREE.Vector3(1, 0, 0);

// временные векторы (без аллокаций в цикле)
const _desired = new THREE.Vector3();
const _to = new THREE.Vector3();
const _diff = new THREE.Vector3();
const _q = new THREE.Quaternion();

/* ---------------- Сцена, рендерер, камера ---------------- */
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a3a63, 0.010);     // имитация воды

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(26, 20, 34);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);                // фон — CSS-градиент
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;   // мягкие тени
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 11, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

/* ---------------- Освещение ---------------- */
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sun = new THREE.DirectionalLight(0xfff1d6, 1.15);
sun.position.set(16, 38, 14);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -30; sun.shadow.camera.right = 30;
sun.shadow.camera.top = 30;   sun.shadow.camera.bottom = -30;
sun.shadow.camera.near = 5;   sun.shadow.camera.far = 90;
sun.shadow.bias = -0.0004;
scene.add(sun);

const pl1 = new THREE.PointLight(0x33ccff, 0.8, 70);  // голубой
pl1.position.set(-12, 9, -8);
const pl2 = new THREE.PointLight(0x2266ff, 0.7, 70);  // синий
pl2.position.set(12, 15, 8);
scene.add(pl1, pl2);

/* ---------------- Стекло и рамка ---------------- */
const glass = new THREE.Mesh(
  new THREE.BoxGeometry(W, H, D),
  new THREE.MeshPhysicalMaterial({
    color: 0x9fd4ff, metalness: 0, roughness: 0.05,
    transmission: 0.95, thickness: 1, ior: 1.33,     // преломление
    transparent: true, opacity: 0.22,
    side: THREE.DoubleSide, depthWrite: false
  })
);
glass.position.y = H / 2;
glass.renderOrder = 20;
scene.add(glass);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(glass.geometry),
  new THREE.LineBasicMaterial({ color: 0x6fdcff, transparent: true, opacity: 0.55 })
);
edges.position.y = H / 2;
edges.renderOrder = 21;
scene.add(edges);

/* ---------------- Песчаное дно (procedural) ---------------- */
const sandGeo = new THREE.PlaneGeometry(W - 0.6, D - 0.6, 48, 32);
sandGeo.rotateX(-Math.PI / 2);
{
  const p = sandGeo.attributes.position;
  const cols = new Float32Array(p.count * 3);
  const base = new THREE.Color(0xd9c493), c = new THREE.Color();
  for (let i = 0; i < p.count; i++){
    const x = p.getX(i), z = p.getZ(i);
    const h = Math.sin(x * 0.35) * Math.cos(z * 0.5) * 0.28
            + Math.sin(x * 0.9 + z * 0.7) * 0.12
            + Math.sin((x + z) * 0.23) * 0.18;
    p.setY(i, h * 0.55);
    c.copy(base).offsetHSL(0, 0, rand(-0.05, 0.05));
    cols[i * 3] = c.r; cols[i * 3 + 1] = c.g; cols[i * 3 + 2] = c.b;
  }
  sandGeo.setAttribute('color', new THREE.BufferAttribute(cols, 3));
  sandGeo.computeVertexNormals();
}
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1 }));
sand.position.y = 0.18;
sand.receiveShadow = true;
scene.add(sand);

/* ---------------- Камни (деформированные додекаэдры) ---------------- */
for (let i = 0; i < 8; i++){
  const geo = new THREE.DodecahedronGeometry(rand(0.9, 1.9), 0);
  const p = geo.attributes.position, v = new THREE.Vector3();
  for (let j = 0; j < p.count; j++){
    v.fromBufferAttribute(p, j);
    const n = fract(Math.sin(v.x * 12.9898 + v.y * 78.233 + v.z * 37.719) * 43758.5453);
    v.multiplyScalar(1 + (n - 0.5) * 0.5);          // детерминированная деформация
    p.setXYZ(j, v.x, v.y, v.z);
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(0.07 + Math.random() * 0.05, 0.08, rand(0.3, 0.5)),
    roughness: 0.95, flatShading: true
  }));
  rock.position.set(rand(-W / 2 + 3, W / 2 - 3), rand(0.4, 0.9), rand(-D / 2 + 3, D / 2 - 3));
  rock.rotation.set(rand(0, Math.PI), rand(0, Math.PI), rand(0, Math.PI));
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

/* ---------------- Водоросли (TubeGeometry + CatmullRom) ---------------- */
const plants = [];
for (let i = 0; i < 12; i++){
  const grp = new THREE.Group();
  const blades = 3 + (Math.random() * 3 | 0);
  const hBase = rand(3, 7);
  const col = new THREE.Color().setHSL(rand(0.33, 0.45), 0.55, rand(0.28, 0.45));
  for (let b = 0; b < blades; b++){
    const pts = [];
    const lean = rand(-0.8, 0.8), bh = hBase * rand(0.6, 1.1);
    for (let k = 0; k <= 4; k++){
      const t = k / 4;
      pts.push(new THREE.Vector3(lean * t * t + rand(-0.15, 0.15) * t, t * bh, rand(-0.15, 0.15) * t));
    }
    const blade = new THREE.Mesh(
      new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 6, 0.13, 5),
      new THREE.MeshStandardMaterial({ color: col.clone().offsetHSL(0, 0, rand(-0.06, 0.06)), roughness: 0.8 })
    );
    blade.castShadow = true;
    grp.add(blade);
  }
  grp.position.set(rand(-W / 2 + 2.5, W / 2 - 2.5), 0.3, rand(-D / 2 + 2.5, D / 2 - 2.5));
  scene.add(grp);
  plants.push({ mesh: grp, phase: Math.random() * Math.PI * 2, ax: rand(0.03, 0.08), az: rand(0.03, 0.08) });
}

/* ---------------- Лучи света в воде (атмосфера) ---------------- */
const shaftTex = (() => {
  const c = document.createElement('canvas'); c.width = 64; c.height = 256;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0, 'rgba(255,255,255,0.9)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 64, 256);
  const g2 = ctx.createLinearGradient(0, 0, 64, 0);
  g2.addColorStop(0, '#000'); g2.addColorStop(0.5, 'rgba(0,0,0,0)'); g2.addColorStop(1, '#000');
  ctx.globalCompositeOperation = 'destination-out';
  ctx.fillStyle = g2; ctx.fillRect(0, 0, 64, 256);
  return new THREE.CanvasTexture(c);
})();
const shafts = [];
for (let i = 0; i < 4; i++){
  const mat = new THREE.MeshBasicMaterial({
    map: shaftTex, transparent: true, opacity: 0.1,
    blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide
  });
  const sh = new THREE.Mesh(new THREE.PlaneGeometry(rand(2.5, 4.5), H - 2), mat);
  sh.position.set(rand(-W / 2 + 6, W / 2 - 6), H / 2, rand(-D / 2 + 4, D / 2 - 4));
  sh.rotation.y = rand(0, Math.PI);
  sh.rotation.z = rand(-0.12, 0.12);
  sh.renderOrder = 5;
  scene.add(sh);
  shafts.push({ mesh: sh, mat, phase: Math.random() * 6, baseZ: sh.rotation.z });
}

/* ---------------- Пузыри ---------------- */
const bubbles = [];
const bubbleGeo = new THREE.SphereGeometry(0.16, 10, 8);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color: 0xd9f3ff, metalness: 0, roughness: 0.05,
  transmission: 0.9, transparent: true, opacity: 0.35, depthWrite: false
});
function makeBubble(x, y, z){
  const m = new THREE.Mesh(bubbleGeo, bubbleMat);
  m.scale.setScalar(0.5 + Math.random());
  m.position.set(x, y, z);
  scene.add(m);
  bubbles.push({
    mesh: m, speed: rand(1.2, 3.0), phase: Math.random() * Math.PI * 2,
    freq: rand(1, 2), amp: rand(0.15, 0.5), baseX: x, baseZ: z
  });
}
for (let i = 0; i < 30; i++)
  makeBubble(rand(-W / 2 + 1.5, W / 2 - 1.5), rand(0.5, H - 1), rand(-D / 2 + 1.5, D / 2 - 1.5));

/* ---------------- Корм ---------------- */
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.22, 10, 8);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xd98a3f, roughness: 0.6, emissive: 0x5a2f08, emissiveIntensity: 0.4 });
function spawnFood(pos){
  const m = new THREE.Mesh(foodGeo, foodMat);
  m.position.copy(pos);
  m.castShadow = true;
  scene.add(m);
  foods.push({ mesh: m, vel: new THREE.Vector3(rand(-0.4, 0.4), -0.5, rand(-0.4, 0.4)), wob: Math.random() * 6 });
  updateCounts();
}
function removeFood(fd){
  scene.remove(fd.mesh);
  const i = foods.indexOf(fd);
  if (i > -1) foods.splice(i, 1);
  updateCounts();
}

/* ---------------- Эффекты (вспышки при поедании) ---------------- */
const effects = [];
const popGeo = new THREE.SphereGeometry(0.08, 6, 5);
function popEffect(pos, color){
  for (let i = 0; i < 7; i++){
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
    const m = new THREE.Mesh(popGeo, mat);
    m.position.copy(pos);
    scene.add(m);
    effects.push({ m, vel: new THREE.Vector3(rand(-2, 2), rand(0.5, 3), rand(-2, 2)), life: 0.6, max: 0.6 });
  }
}

/* ---------------- Рыбки ---------------- */
const SCHEMES = [
  { body: 0xff8c2b, fin: 0xffc46b },              // оранжевая
  { body: 0x2e7bff, fin: 0x8fd8ff },              // синяя
  { body: 0xffd21f, fin: 0xff4b2e },              // жёлто-красная
  { body: 0x9b5cff, fin: 0xdcb3ff },              // фиолетовая
  { body: 0xef3b3b, fin: 0xff9d7a },              // красная
  { body: 0x3fd47a, fin: 0xb8f7cd },              // зелёная
  { body: 0xff77b9, fin: 0xffd1e8 },              // розовая
  { body: 0xf2b53c, fin: 0xfff3c0, gold: true }   // золотая
];

// общие низкополигональные геометрии
const bodyGeo  = new THREE.SphereGeometry(1, 18, 12);
const bellyGeo = new THREE.SphereGeometry(1, 14, 10);
const eyeGeo   = new THREE.SphereGeometry(0.17, 10, 8);
const pupGeo   = new THREE.SphereGeometry(0.08, 8, 6);
const finGeo   = new THREE.SphereGeometry(0.5, 10, 8);  finGeo.scale(0.9, 0.16, 0.62);
const ringGeo  = new THREE.TorusGeometry(1.02, 0.05, 6, 20); ringGeo.rotateY(Math.PI / 2);
const tailGeo  = new THREE.ConeGeometry(0.62, 1.25, 4);
tailGeo.rotateZ(-Math.PI / 2);                  // остриё к телу (+X)
tailGeo.translate(-0.625, 0, 0);                // шарнир маха — в начале координат
tailGeo.scale(1, 1, 0.22);                      // сплюснутый «веер»
const dorsalGeo = new THREE.ConeGeometry(0.45, 0.9, 4);
dorsalGeo.rotateZ(0.3); dorsalGeo.scale(1, 1, 0.18);

const eyeMat = new THREE.MeshStandardMaterial({ color: 0xf6fbff, roughness: 0.15 });
const pupMat = new THREE.MeshStandardMaterial({ color: 0x0a1016, roughness: 0.1 });

const fishArray = [];

function createFish(){
  const sc = SCHEMES[(Math.random() * SCHEMES.length) | 0];
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: sc.body, roughness: 0.35, metalness: sc.gold ? 0.65 : 0.25 });
  const finMat  = new THREE.MeshStandardMaterial({ color: sc.fin, roughness: 0.45, metalness: 0.15, transparent: true, opacity: 0.95, side: THREE.DoubleSide });
  const bellyMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(sc.body).lerp(new THREE.Color(0xffffff), 0.55), roughness: 0.5, metalness: 0.1 });

  const body = new THREE.Mesh(bodyGeo, bodyMat);           // вытянутое тело
  body.scale.set(1.55, 0.95, 0.55);
  body.castShadow = true;
  g.add(body);

  const belly = new THREE.Mesh(bellyGeo, bellyMat);        // светлое брюшко
  belly.scale.set(1.4, 0.85, 0.48);
  belly.position.y = -0.15;
  g.add(belly);

  const tail = new THREE.Mesh(tailGeo, finMat);            // хвост (шарнир в корне)
  tail.position.set(-1.42, 0, 0);
  tail.castShadow = true;
  g.add(tail);

  const dorsal = new THREE.Mesh(dorsalGeo, finMat);        // спинной плавник
  dorsal.position.set(0.1, 0.78, 0);
  g.add(dorsal);

  const leftFin = new THREE.Mesh(finGeo, finMat);          // грудные плавники
  leftFin.position.set(0.3, -0.3, 0.4);
  leftFin.rotation.z = 0.5;
  g.add(leftFin);
  const rightFin = new THREE.Mesh(finGeo, finMat);
  rightFin.position.set(0.3, -0.3, -0.4);
  rightFin.rotation.z = -0.5;
  g.add(rightFin);

  for (const s of [1, -1]){                                // глаза с зрачками
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(1.0, 0.22, 0.33 * s);
    const pup = new THREE.Mesh(pupGeo, pupMat);
    pup.position.set(0.05, 0, 0.1 * s);
    eye.add(pup);
    g.add(eye);
  }

  for (const x of [0.45, -0.3])                            // полосы-кольца
  {
    const ring = new THREE.Mesh(ringGeo, finMat);
    ring.scale.set(1, 0.95, 0.55);
    ring.position.x = x;
    g.add(ring);
  }

  const baseScale = rand(0.6, 1.2);                        // разнообразие размеров
  g.scale.setScalar(baseScale);
  g.position.set(rand(-W / 2 + 4, W / 2 - 4), rand(4, H - 5), rand(-D / 2 + 3, D / 2 - 3));
  scene.add(g);

  const f = {
    mesh: g, body, tail, dorsal, leftFin, rightFin,
    velocity: new THREE.Vector3(rand(-1, 1), rand(-0.3, 0.3), rand(-1, 1)).normalize().multiplyScalar(2.5),
    speed: rand(2.2, 4.0),
    tailSpeed: rand(5, 9),
    phase: Math.random() * Math.PI * 2,
    targetFood: null,
    avoidanceRadius: rand(1.8, 2.8),
    wanderDir: new THREE.Vector3(rand(-1, 1), rand(-0.4, 0.4), rand(-1, 1)).normalize(),
    wanderTimer: rand(0, 3),
    baseScale, grow: 1,
    color: sc.body
  };
  fishArray.push(f);
  updateCounts();
  return f;
}
for (let i = 0; i < 15; i++) createFish();

function eatFood(fd, f){
  removeFood(fd);
  f.grow = Math.min(3, f.grow * 1.05);                     // рост на 5%
  f.mesh.scale.setScalar(f.baseScale * f.grow);
  popEffect(fd.mesh.position, f.color);
  for (let i = 0; i < 3; i++)
    makeBubble(fd.mesh.position.x + rand(-0.3, 0.3), fd.mesh.position.y, fd.mesh.position.z + rand(-0.3, 0.3));
  bump(el('fishCount'));
}

/* ---------------- ИИ рыбок ---------------- */
function updateFish(dt, t){
  const n = fishArray.length;
  for (let i = 0; i < n; i++){
    const f = fishArray[i], p = f.mesh.position;

    // случайное блуждание
    f.wanderTimer -= dt;
    if (f.wanderTimer <= 0){
      f.wanderTimer = rand(1.5, 4.5);
      f.wanderDir.set(rand(-1, 1), rand(-0.4, 0.4), rand(-1, 1)).normalize();
    }
    _desired.copy(f.wanderDir);

    // поиск корма (радиус 15)
    let best = null, bestD = 15;
    for (let k = 0; k < foods.length; k++){
      const d = p.distanceTo(foods[k].mesh.position);
      if (d < bestD){ bestD = d; best = foods[k]; }
    }
    f.targetFood = best;
    if (best){
      _to.copy(best.mesh.position).sub(p);
      const d = _to.length();
      if (d < 1.1 + 0.4 * f.mesh.scale.x) eatFood(best, f);
      else _desired.copy(_to.normalize());
    }

    // избегание столкновений
    for (let j = 0; j < n; j++){
      if (j === i) continue;
      const o = fishArray[j].mesh.position;
      _diff.subVectors(p, o);
      const d = _diff.length();
      const r = f.avoidanceRadius + fishArray[j].mesh.scale.x;
      if (d < r && d > 1e-4) _desired.addScaledVector(_diff.normalize(), (r - d) / r * 5);
    }

    // плавное отражение от стен
    const bx = W / 2 - 2.2, bz = D / 2 - 2.2;
    if (p.x < -bx) _desired.x += (-bx - p.x) * 2.5; else if (p.x > bx) _desired.x -= (p.x - bx) * 2.5;
    if (p.z < -bz) _desired.z += (-bz - p.z) * 2.5; else if (p.z > bz) _desired.z -= (p.z - bz) * 2.5;
    if (p.y < 2) _desired.y += (2 - p.y) * 2.5; else if (p.y > H - 2.2) _desired.y -= (p.y - (H - 2.2)) * 2.5;

    // интеграция (плавный поворот скорости)
    if (_desired.lengthSq() > 1e-6) _desired.normalize();
    _desired.multiplyScalar(f.speed * (best ? 1.9 : 1));
    f.velocity.lerp(_desired, 1 - Math.exp(-3.2 * dt));
    p.addScaledVector(f.velocity, dt);

    p.x = THREE.MathUtils.clamp(p.x, -W / 2 + 1.2, W / 2 - 1.2);
    p.y = THREE.MathUtils.clamp(p.y, 1.2, H - 1.4);
    p.z = THREE.MathUtils.clamp(p.z, -D / 2 + 1.2, D / 2 - 1.2);

    // ориентация по направлению движения
    _to.set(f.velocity.x, f.velocity.y * 0.4, f.velocity.z);
    if (_to.lengthSq() > 1e-4){
      _q.setFromUnitVectors(X_AXIS, _to.normalize());
      f.mesh.quaternion.slerp(_q, 1 - Math.exp(-4.5 * dt));
    }

    // анимация плавников и хвоста (каждая рыбка — своя частота и фаза)
    const tt = t * f.tailSpeed + f.phase;
    f.tail.rotation.y = Math.sin(tt) * 0.55;               // маш хвостом в плоскости плавания
    f.dorsal.rotation.z = Math.sin(tt * 0.7) * 0.1;
    f.leftFin.rotation.z = 0.5 + Math.sin(tt * 0.9 + 1) * 0.35;
    f.rightFin.rotation.z = -0.5 - Math.sin(tt * 0.9 + 1) * 0.35;
    f.body.position.y = Math.sin(tt * 0.5) * 0.05;         // лёгкое «дыхание» тела
  }
}

/* ---------------- Клик = корм (raycaster) ---------------- */
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let downXY = null;
renderer.domElement.addEventListener('pointerdown', e => { downXY = [e.clientX, e.clientY]; });
addEventListener('pointerup', e => {
  if (!downXY) return;
  const dx = e.clientX - downXY[0], dy = e.clientY - downXY[1];
  downXY = null;
  if (dx * dx + dy * dy > 36) return;                       // это было вращение, не клик
  mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(mouseNDC, camera);
  const hit = raycaster.intersectObject(glass)[0];
  if (!hit) return;
  const p = hit.point;
  spawnFood(new THREE.Vector3(
    THREE.MathUtils.clamp(p.x, -W / 2 + 1.5, W / 2 - 1.5),
    THREE.MathUtils.clamp(p.y + 0.8, 1.5, H - 1),
    THREE.MathUtils.clamp(p.z, -D / 2 + 1.5, D / 2 - 1.5)
  ));
});

/* ---------------- Кнопки UI ---------------- */
function bump(node){ node.classList.remove('bump'); void node.offsetWidth; node.classList.add('bump'); }
function updateCounts(){
  el('fishCount').textContent = fishArray.length;
  el('bubbleCount').textContent = bubbles.length;
  el('foodCount').textContent = foods.length;
}

el('btnFish').onclick = () => {
  if (fishArray.length >= 40){ bump(el('fishCount')); return; }   // потолок производительности
  const f = createFish();
  popEffect(f.mesh.position, 0x7de8ff);
  bump(el('fishCount'));
};
el('btnBubbles').onclick = () => {
  for (let i = 0; i < 10 && bubbles.length < 150; i++)
    makeBubble(rand(-W / 2 + 1.5, W / 2 - 1.5), rand(0.4, 1.5), rand(-D / 2 + 1.5, D / 2 - 1.5));
  updateCounts(); bump(el('bubbleCount'));
};
let sunOn = true;
el('btnLight').onclick = function(){
  sunOn = !sunOn;
  sun.intensity = sunOn ? 1.15 : 0;
  this.classList.toggle('off', !sunOn);
  this.textContent = sunOn ? '💡 Свет: вкл' : '🌙 Свет: выкл';
};

/* ---------------- Главный цикл ---------------- */
const clock = new THREE.Clock();
let t = 0, frames = 0, acc = 0;

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);   // дельта-время
  t += dt;

  updateFish(dt, t);

  // корм: гравитация + сопротивление воды
  for (let i = foods.length - 1; i >= 0; i--){
    const fd = foods[i];
    fd.vel.y = Math.max(fd.vel.y - 6 * dt, -2.4);
    fd.mesh.position.addScaledVector(fd.vel, dt);
    fd.mesh.position.x += Math.sin(t * 3 + fd.wob) * 0.2 * dt;
    if (fd.mesh.position.y < 0.7) removeFood(fd);   // упал на дно — убираем
  }

  // пузыри
  for (const b of bubbles){
    const m = b.mesh;
    m.position.y += b.speed * dt;
    m.position.x = b.baseX + Math.sin(t * b.freq + b.phase) * b.amp;
    m.position.z = b.baseZ + Math.cos(t * b.freq * 0.8 + b.phase) * b.amp * 0.6;
    if (m.position.y > H - 0.6){
      m.position.y = rand(0.4, 1.0);
      b.baseX = rand(-W / 2 + 1.5, W / 2 - 1.5);
      b.baseZ = rand(-D / 2 + 1.5, D / 2 - 1.5);
    }
  }

  // водоросли покачиваются
  for (const pl of plants){
    pl.mesh.rotation.x = Math.sin(t * 0.8 + pl.phase) * pl.ax;
    pl.mesh.rotation.z = Math.sin(t * 0.6 + pl.phase * 1.4) * pl.az;
  }

  // лучи и «живое» подводное освещение
  for (const s of shafts){
    s.mat.opacity = 0.05 + 0.05 * (0.5 + 0.5 * Math.sin(t * 0.4 + s.phase));
    s.mesh.rotation.z = s.baseZ + Math.sin(t * 0.15 + s.phase) * 0.04;
  }
  pl1.intensity = 0.7 + Math.sin(t * 0.7) * 0.25;
  pl2.intensity = 0.6 + Math.sin(t * 0.5 + 2) * 0.25;
  pl1.position.x = -12 + Math.sin(t * 0.2) * 3;
  pl2.position.z = 8 + Math.cos(t * 0.17) * 3;

  // частицы-вспышки
  for (let i = effects.length - 1; i >= 0; i--){
    const e = effects[i];
    e.life -= dt;
    if (e.life <= 0){ scene.remove(e.m); e.m.material.dispose(); effects.splice(i, 1); continue; }
    e.m.position.addScaledVector(e.vel, dt);
    e.vel.multiplyScalar(1 - 2 * dt);
    const s = e.life / e.max;
    e.m.scale.setScalar(s);
    e.m.material.opacity = s;
  }

  controls.update();
  renderer.render(scene, camera);

  frames++; acc += dt;
  if (acc >= 0.5){
    el('fps').textContent = Math.round(frames / acc);
    frames = 0; acc = 0;
  }
}
animate();

/* ---------------- Прочее ---------------- */
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

window.addEventListener('load', () => setTimeout(() => {
  const l = el('loader');
  l.classList.add('done');
  setTimeout(() => l.remove(), 900);
}, 600));
</script>
</body>
</html>
```

**Что внутри и как это работает**

- **Рыбки** — группа из тела (сплюснутая сфера), брюшка, хвоста-«веера» на шарнире, спинного и двух грудных плавников, глаз с зрачками и полос-колец. У каждой свои скорость, фаза, частота маха и радиус избегания; ориентация — плавным `slerp` к вектору скорости.
- **ИИ** — блуждание с таймером, отталкивание от соседей, мягкий «отскок» от стенок (управляющая сила у границы, а не мгновенный разворот), погоня за кормом в радиусе 15 с ускорением ×1.9, рост ×1.05 за каждую частицу (с потолком ×3, чтобы не вырастить кита).
- **Кормление** — клик распознаётся отдельно от вращения камеры (порог смещения курсора < 6 px), точка берётся рейкастом по стеклу и вжимается внутрь аквариума. При поедании — вспышка частиц и пара пузырьков.
- **Окружение** — стекло с `transmission: 0.95`, процедурный песок с вершинными цветами, 8 камней с детерминированной деформацией (без «разрывов» граней), 12 кустов из `TubeGeometry`, плюс бонус — мерцающие световые столбы и «дышащие» точечные источники для живой воды.
- **Оптимизации** — общие геометрии и материалы, нулевые аллокации в горячем цикле (временные векторы), `pixelRatio ≤ 2`, низкие сегменты, лимиты: 40 рыбок / 150 пузырей.

Одно осознанное отступление от ТЗ: хвост я анимирую вращением вокруг вертикальной оси рыбы (в её системе это даёт боковой замах в плоскости плавания). Буквальное вращение вокруг мировой Z для горизонтально плывущей рыбки выглядело бы как вертикальное «хлопанье» — против реализма, на который нацелен проект. Если нужен именно `rotation.z` — скажите, переверну модель.