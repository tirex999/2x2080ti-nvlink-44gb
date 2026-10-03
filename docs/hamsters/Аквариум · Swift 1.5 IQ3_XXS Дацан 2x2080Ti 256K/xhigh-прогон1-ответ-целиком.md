# 🐠 Глубоководный аквариум — интерактивная 3D-экосистема

Ниже — один самодостаточный HTML-файл. Внутри: процедурная анатомия рыб (тело, countershading, глаза с бликами, хвостовой веер, 4 плавника), стейринг-ИИ (блуждание → разделение → уклонение от стенок → преследование корма → рост), стеклянный бак на `transmission`, песчаное дно с дюнами и вертексными цветами, 12TubeGeometry-водорослей, пузыри, планктон, корм с гравитацией, круги на воде, дневной/ночной свет и стеклянный HUD с FPS-графиком.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Аквавиум · Интерактивная 3D-экосистема</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --abyss:#03101c; --deep:#062b45; --shallow:#0b4f74;
  --aqua:#5ff2d6; --aqua2:#39c7f0; --coral:#ff8a52; --sand:#e8cfa3;
  --ink:#eaf6ff; --muted:rgba(214,238,250,.62);
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0; overflow:hidden; color:var(--ink);
  font-family:'Manrope',system-ui,sans-serif;
  background:radial-gradient(120% 95% at 50% 0%, #0d5a82 0%, #07324f 40%, #041725 72%, #020b14 100%);
  transition:background 1.4s ease;
}
body.night{background:radial-gradient(120% 95% at 50% 0%, #0a2c4b 0%, #04192e 42%, #020c18 74%, #01060d 100%);}
canvas#scene{position:fixed; inset:0; display:block; z-index:1}

/* ——— слоистая атмосфера ——— */
.layer{position:fixed; inset:0; pointer-events:none; z-index:2}
.rays{
  background:repeating-linear-gradient(104deg,
    rgba(160,240,255,.10) 0px, rgba(160,240,255,0) 26px,
    rgba(160,240,255,.06) 58px, rgba(160,240,255,0) 96px);
  mix-blend-mode:screen; opacity:.55; filter:blur(1px);
  animation:drift 22s linear infinite;
}
@keyframes drift{from{background-position:0 0}to{background-position:420px 0}}
.vignette{background:radial-gradient(80% 65% at 50% 42%, transparent 40%, rgba(1,7,14,.55) 100%);}
.grain{opacity:.05; background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E");}
.caustic{
  background:radial-gradient(45% 26% at 30% 6%, rgba(120,255,230,.14), transparent 60%),
             radial-gradient(38% 22% at 72% 12%, rgba(90,190,255,.13), transparent 60%);
  animation:pulse 9s ease-in-out infinite alternate;
}
@keyframes pulse{from{opacity:.45; transform:translateY(0)}to{opacity:.95; transform:translateY(14px)}}

/* ——— стеклянные панели ——— */
.glass{
  background:linear-gradient(180deg, rgba(11,42,66,.78), rgba(4,20,34,.62));
  border:1px solid rgba(95,242,214,.20);
  backdrop-filter:blur(18px) saturate(150%); -webkit-backdrop-filter:blur(18px) saturate(150%);
  box-shadow:0 22px 48px rgba(0,0,0,.46), inset 0 1px 0 rgba(255,255,255,.09);
  border-radius:18px 18px 18px 5px;
}
#hud{position:fixed; inset:0; z-index:5; pointer-events:none}
#hud > *{pointer-events:auto}

.panel-left{position:absolute; top:22px; left:22px; width:296px; padding:20px 20px 18px}
.eyebrow{font-size:9.5px; letter-spacing:.34em; text-transform:uppercase; color:var(--aqua); opacity:.9; font-weight:700}
h1{
  font-family:'Syne',sans-serif; font-weight:800; font-size:31px; line-height:.94;
  margin:9px 0 2px; letter-spacing:-.01em; color:#f2fdff;
  text-shadow:0 0 26px rgba(95,242,214,.35);
}
h1 em{font-style:normal; color:var(--aqua)}
.sub{font-size:11.5px; color:var(--muted); line-height:1.5; margin-bottom:14px}
.wave{height:12px; margin:0 0 13px; opacity:.85}
.wave path{stroke:var(--aqua); stroke-width:1.4; fill:none; stroke-dasharray:90 200; animation:flow 4s linear infinite}
@keyframes flow{to{stroke-dashoffset:-290}}

.keys{display:flex; flex-direction:column; gap:7px; margin-bottom:15px}
.key{display:flex; align-items:center; gap:9px; font-size:11.5px; color:var(--muted)}
.chip{
  font-family:'Syne',sans-serif; font-weight:700; font-size:9px; letter-spacing:.1em;
  padding:4px 7px; border-radius:6px; min-width:44px; text-align:center; color:#04222e;
  background:linear-gradient(180deg,#7ef7e2,#31b6df); box-shadow:0 3px 10px rgba(95,242,214,.22);
}
.btns{display:flex; flex-wrap:wrap; gap:8px}
.btn{
  font-family:'Manrope',sans-serif; font-weight:700; font-size:11.5px; letter-spacing:.03em;
  padding:9px 12px; border-radius:11px 11px 11px 4px; cursor:pointer; color:var(--ink);
  border:1px solid rgba(95,242,214,.26);
  background:linear-gradient(180deg, rgba(95,242,214,.20), rgba(30,120,170,.14));
  transition:transform .2s cubic-bezier(.34,1.56,.64,1), box-shadow .25s, background .25s, color .25s;
}
.btn:hover{transform:translateY(-2px); box-shadow:0 10px 24px rgba(95,242,214,.22); color:#fff}
.btn:active{transform:translateY(0) scale(.96)}
.btn.primary{background:linear-gradient(180deg,#7df6e0,#22b3e6); color:#03222f; border-color:transparent}
.btn.primary:hover{box-shadow:0 12px 30px rgba(57,199,240,.42)}
.btn.on{background:linear-gradient(180deg,#ffd36b,#ff8a52); color:#2b1205; border-color:transparent}

.panel-right{position:absolute; top:22px; right:22px; width:196px; padding:16px 18px 14px}
.stat{display:flex; align-items:baseline; justify-content:space-between; padding:5px 0; border-bottom:1px solid rgba(95,242,214,.10)}
.stat:last-of-type{border-bottom:none}
.stat .lab{font-size:9px; letter-spacing:.22em; text-transform:uppercase; color:var(--muted)}
.stat .val{font-family:'Syne',sans-serif; font-weight:800; font-size:22px; color:#f0fbff; font-variant-numeric:tabular-nums}
.stat .val.aqua{color:var(--aqua)} .stat .val.coral{color:var(--coral)}
#fpsGraph{display:block; width:100%; height:30px; margin-top:9px; opacity:.9}
.pulse{animation:pop .45s cubic-bezier(.34,1.8,.64,1)}
@keyframes pop{0%{transform:scale(1)}45%{transform:scale(1.28); color:var(--aqua)}100%{transform:scale(1)}}

.legend{position:absolute; left:22px; bottom:22px; padding:13px 16px; width:296px}
.legend .lab{font-size:9px; letter-spacing:.24em; text-transform:uppercase; color:var(--muted); margin-bottom:9px}
.swatches{display:flex; gap:9px; flex-wrap:wrap}
.sw{width:26px; height:26px; border-radius:50% 50% 50% 6px; position:relative; cursor:help;
  border:1px solid rgba(255,255,255,.24); transition:transform .22s cubic-bezier(.34,1.7,.64,1), box-shadow .22s}
.sw:hover{transform:translateY(-4px) rotate(-8deg) scale(1.14); box-shadow:0 8px 18px rgba(0,0,0,.4)}
.sw::after{content:attr(data-n); position:absolute; bottom:130%; left:50%; transform:translateX(-50%);
  white-space:nowrap; font-size:9.5px; letter-spacing:.12em; text-transform:uppercase; padding:4px 7px;
  background:rgba(3,18,30,.92); border:1px solid rgba(95,242,214,.25); border-radius:6px;
  opacity:0; transition:opacity .2s; pointer-events:none}
.sw:hover::after{opacity:1}

.hint{position:absolute; right:22px; bottom:22px; padding:13px 17px; max-width:250px; display:flex; gap:11px; align-items:center}
.hint .dot{width:9px; height:9px; border-radius:50%; background:var(--coral); box-shadow:0 0 14px var(--coral); animation:blink 1.8s ease-in-out infinite; flex:none}
@keyframes blink{50%{opacity:.28; transform:scale(.75)}}
.hint p{margin:0; font-size:11.5px; color:var(--muted); line-height:1.45}
.hint b{color:#fff; font-weight:700}

#toasts{position:absolute; top:22px; left:50%; transform:translateX(-50%); display:flex; flex-direction:column; gap:8px; align-items:center; pointer-events:none}
.toast{
  font-size:11.5px; font-weight:600; letter-spacing:.04em; padding:9px 16px; border-radius:11px 11px 11px 4px;
  background:linear-gradient(180deg, rgba(11,42,66,.9), rgba(4,20,34,.8));
  border:1px solid rgba(95,242,214,.3); box-shadow:0 14px 34px rgba(0,0,0,.4);
  animation:toastIn .4s cubic-bezier(.34,1.6,.64,1) both;
}
.toast.out{animation:toastOut .45s ease forwards}
@keyframes toastIn{from{opacity:0; transform:translateY(-14px) scale(.94)}}
@keyframes toastOut{to{opacity:0; transform:translateY(-10px) scale(.96)}}

/* ——— загрузка ——— */
#loader{position:fixed; inset:0; z-index:40; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px;
  background:radial-gradient(70% 60% at 50% 45%, #0a3f5f, #020b14 80%); transition:opacity .9s ease}
#loader.gone{opacity:0; pointer-events:none}
#loader .t{font-family:'Syne',sans-serif; font-weight:800; font-size:clamp(26px,5vw,46px); letter-spacing:.02em}
#loader .t span{color:var(--aqua)}
.bar{width:min(320px,70vw); height:3px; border-radius:3px; background:rgba(95,242,214,.16); overflow:hidden}
.bar i{display:block; height:100%; width:0%; background:linear-gradient(90deg,var(--aqua),var(--aqua2)); animation:fill 1.6s ease forwards}
@keyframes fill{to{width:100%}}
#loader .s{font-size:10.5px; letter-spacing:.3em; text-transform:uppercase; color:var(--muted)}

@media (max-width:820px){
  .panel-left{width:calc(100vw - 44px)} .keys{display:none}
  .legend{display:none} .panel-right{width:150px; top:auto; bottom:22px; right:22px; padding:12px 14px}
  .hint{display:none} h1{font-size:26px} .stat .val{font-size:18px}
}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div class="layer caustic"></div>
<div class="layer rays"></div>
<div class="layer grain"></div>
<div class="layer vignette"></div>

<div id="hud">
  <section class="panel-left glass">
    <div class="eyebrow">Three.js · r128 · живая система</div>
    <h1>Аква<em>риум</em></h1>
    <p class="sub">Экосистема на 15 тропических рыб: стейринг-ИИ, рост от корма, стеклянный бак с преломлением.</p>
    <svg class="wave" viewBox="0 0 260 12" preserveAspectRatio="none">
      <path d="M0 6 Q 20 0 40 6 T 80 6 T 120 6 T 160 6 T 200 6 T 240 6 T 280 6"/>
    </svg>
    <div class="keys">
      <div class="key"><span class="chip">ЛКМ</span> вращение вокруг бака</div>
      <div class="key"><span class="chip">ПКМ</span> панорамирование</div>
      <div class="key"><span class="chip">КОЛЕСО</span> зум 10 → 60</div>
      <div class="key"><span class="chip">КЛИК</span> бросить корм в воду</div>
    </div>
    <div class="btns">
      <button class="btn primary" id="bFish">+ Рыбка</button>
      <button class="btn" id="bBub">+10 пузырей</button>
      <button class="btn" id="bFeed">Покормить</button>
      <button class="btn" id="bLight">☾ Ночной свет</button>
      <button class="btn" id="bOrbit">Автооблёт</button>
    </div>
  </section>

  <section class="panel-right glass">
    <div class="stat"><span class="lab">Рыбки</span><span class="val aqua" id="sFish">15</span></div>
    <div class="stat"><span class="lab">Корм в воде</span><span class="val coral" id="sFood">0</span></div>
    <div class="stat"><span class="lab">Пузыри</span><span class="val" id="sBub">30</span></div>
    <div class="stat"><span class="lab">Средний размер</span><span class="val" id="sSize">1.00×</span></div>
    <div class="stat"><span class="lab">FPS</span><span class="val aqua" id="sFps">60</span></div>
    <canvas id="fpsGraph" width="160" height="30"></canvas>
  </section>

  <section class="legend glass">
    <div class="lab">8 цветовых схем · наведите</div>
    <div class="swatches" id="swatches"></div>
  </section>

  <section class="hint glass">
    <span class="dot"></span>
    <p><b>Кликните по воде</b> — корм пойдёт ко дну, рыбы в радиусе 15 единиц начнут преследование и вырастут на 5%.</p>
  </section>

  <div id="toasts"></div>
</div>

<div id="loader">
  <div class="t">Аква<span>риум</span></div>
  <div class="bar"><i></i></div>
  <div class="s">заполняем водой…</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ══════════════════════════════════════════════════════════
   0. КОНСТАНТЫ И ПАЛИТРА
══════════════════════════════════════════════════════════ */
const TANK = { w:36, h:24, d:20 };
const B    = { x:16.0, yMin:1.7, yMax:22.2, z:8.4 };
const MAX_FISH = 48;

const SCHEMES = [
  {name:'Оранжевая',    body:0xff7a29, fin:0xffb066, belly:0xffe3c2, back:0xc74600},
  {name:'Синяя',        body:0x2f80e0, fin:0x7fc0ff, belly:0xd8ecff, back:0x0c3f8f},
  {name:'Жёлто-красная',body:0xffc21a, fin:0xff6b2e, belly:0xfff0c2, back:0xd9330a},
  {name:'Фиолетовая',   body:0x9b5de5, fin:0xc99df0, belly:0xe8dcff, back:0x54189a},
  {name:'Красная',      body:0xe63946, fin:0xff8fa0, belly:0xffd7dd, back:0x8b1121},
  {name:'Зелёная',      body:0x2ec4a5, fin:0x8ff0d4, belly:0xd9fff2, back:0x0f6b57},
  {name:'Розовая',      body:0xff6fae, fin:0xffb6d5, belly:0xffe1ef, back:0xb0306a},
  {name:'Золотая',      body:0xf2b53c, fin:0xffe08a, belly:0xfff4cf, back:0xa06f0a}
];

/* ══════════════════════════════════════════════════════════
   1. РЕНДЕРЕР / СЦЕНА / КАМЕРА
══════════════════════════════════════════════════════════ */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.06;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x08405f, 0.0165);

const camera = new THREE.PerspectiveCamera(52, innerWidth/innerHeight, 0.1, 400);
camera.position.set(52, 40, 52);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 11, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.055;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.minPolarAngle = 0.14;
controls.panSpeed = 0.7;
controls.rotateSpeed = 0.85;
controls.enabled = false;

/* ══════════════════════════════════════════════════════════
   2. ОСВЕЩЕНИЕ
══════════════════════════════════════════════════════════ */
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xcfeeff, 1.25);
sun.position.set(20, 46, 18);
sun.target.position.set(0, 8, 0);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 140;
sun.shadow.camera.left = -26; sun.shadow.camera.right = 26;
sun.shadow.camera.top = 32;   sun.shadow.camera.bottom = -12;
sun.shadow.bias = -0.0007;
sun.shadow.radius = 2.2;
scene.add(sun, sun.target);

const underA = new THREE.PointLight(0x2ea8ff, 1.5, 62, 2);
underA.position.set(-13, 18, -6);
const underB = new THREE.PointLight(0x1560ff, 1.1, 58, 2);
underB.position.set(13, 5, 8);
scene.add(underA, underB);

/* ══════════════════════════════════════════════════════════
   3. СТЕКЛЯННЫЙ БАК + СТАНД + РАМКА
══════════════════════════════════════════════════════════ */
const glass = new THREE.Mesh(
  new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d),
  new THREE.MeshPhysicalMaterial({
    color:0xbfe8ff, transparent:true, opacity:0.16,
    transmission:0.95, thickness:2.0, ior:1.33,
    roughness:0.06, metalness:0.0,
    clearcoat:1.0, clearcoatRoughness:0.05,
    side:THREE.DoubleSide, depthWrite:false
  })
);
glass.position.set(0, TANK.h/2, 0);
glass.renderOrder = 10;
scene.add(glass);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(TANK.w+0.06, TANK.h+0.06, TANK.d+0.06)),
  new THREE.LineBasicMaterial({color:0x5ff2d6, transparent:true, opacity:0.5})
);
edges.position.set(0, TANK.h/2, 0);
scene.add(edges);

// верхняя рамка + подиум
const metal = new THREE.MeshStandardMaterial({color:0x14232f, roughness:0.55, metalness:0.75});
const frameMat = new THREE.MeshStandardMaterial({color:0x0d2a3a, roughness:0.45, metalness:0.8, emissive:0x0a3a44, emissiveIntensity:0.5});
const rimParts = [
  [TANK.w+1.6, 0.9, 1.5, 0, TANK.h+0.2,  TANK.d/2+0.5],
  [TANK.w+1.6, 0.9, 1.5, 0, TANK.h+0.2, -TANK.d/2-0.5],
  [1.5, 0.9, TANK.d+1.6,  TANK.w/2+0.5, TANK.h+0.2, 0],
  [1.5, 0.9, TANK.d+1.6, -TANK.w/2-0.5, TANK.h+0.2, 0]
];
rimParts.forEach(p=>{
  const m = new THREE.Mesh(new THREE.BoxGeometry(p[0],p[1],p[2]), frameMat);
  m.position.set(p[3],p[4],p[5]); m.castShadow = true; m.receiveShadow = true; scene.add(m);
});
const plinth = new THREE.Mesh(new THREE.BoxGeometry(TANK.w+3.4, 2.4, TANK.d+3.4), metal);
plinth.position.set(0, -1.35, 0); plinth.receiveShadow = true; plinth.castShadow = true;
scene.add(plinth);

// невидимый объём воды для raycast-кликов
const waterVolume = new THREE.Mesh(new THREE.BoxGeometry(TANK.w-1, TANK.h-1, TANK.d-1),
  new THREE.MeshBasicMaterial({visible:false}));
waterVolume.position.set(0, TANK.h/2, 0);
scene.add(waterVolume);

/* ══════════════════════════════════════════════════════════
   4. ПЕСЧАНОЕ ДНО (процедурные дюны + вертексные цвета)
══════════════════════════════════════════════════════════ */
const sandGeo = new THREE.PlaneGeometry(TANK.w-0.4, TANK.d-0.4, 76, 48);
sandGeo.rotateX(-Math.PI/2);
{
  const p = sandGeo.attributes.position;
  const col = new Float32Array(p.count*3);
  const base = new THREE.Color(0xe8cfa3), dark = new THREE.Color(0xb8975f), lite = new THREE.Color(0xf7e3c0);
  const c = new THREE.Color();
  for(let i=0;i<p.count;i++){
    const x=p.getX(i), z=p.getZ(i);
    let h = Math.sin(x*0.46)*Math.cos(z*0.42)*0.26 + Math.sin(x*1.25+z*0.9)*0.13 + Math.random()*0.05;
    h += Math.exp(-((x+9)*(x+9)+(z-4)*(z-4))/14)*0.75;
    h += Math.exp(-((x-8)*(x-8)+(z+5)*(z+5))/20)*0.5;
    p.setY(i, h);
    c.copy(base).lerp(h>0.35?lite:dark, Math.min(1, Math.abs(h)*1.5));
    col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b;
  }
  sandGeo.setAttribute('color', new THREE.BufferAttribute(col,3));
  sandGeo.computeVertexNormals();
}
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({vertexColors:true, roughness:0.96, metalness:0.0}));
sand.position.y = 0.05; sand.receiveShadow = true;
scene.add(sand);

/* ══════════════════════════════════════════════════════════
   5. КАМНИ (деформированные додекаэдры)
══════════════════════════════════════════════════════════ */
const rockMats = [
  new THREE.MeshStandardMaterial({color:0x5d6a72, roughness:0.92, metalness:0.05, flatShading:true}),
  new THREE.MeshStandardMaterial({color:0x6b5f52, roughness:0.95, metalness:0.03, flatShading:true}),
  new THREE.MeshStandardMaterial({color:0x4a5a63, roughness:0.88, metalness:0.08, flatShading:true})
];
for(let i=0;i<8;i++){
  const r = 1.2 + Math.random()*1.4;
  const g = new THREE.DodecahedronGeometry(r, 0);
  const pp = g.attributes.position;
  for(let v=0; v<pp.count; v++){
    pp.setXYZ(v, pp.getX(v)+(Math.random()-0.5)*r*0.34,
                 pp.getY(v)+(Math.random()-0.5)*r*0.34,
                 pp.getZ(v)+(Math.random()-0.5)*r*0.34);
  }
  g.computeVertexNormals();
  const rock = new THREE.Mesh(g, rockMats[i%3]);
  rock.position.set((Math.random()-0.5)*(TANK.w-7), r*0.42, (Math.random()-0.5)*(TANK.d-6));
  rock.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  rock.scale.set(1, 0.62+Math.random()*0.3, 1);
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

/* ══════════════════════════════════════════════════════════
   6. ВОДОРОСЛИ (TubeGeometry + CatmullRomCurve3)
══════════════════════════════════════════════════════════ */
const weeds = [];
const weedColors = [0x1f9e6b, 0x2fbf7a, 0x18875f, 0x3ad29a, 0x14785a, 0x5ecf8c];
for(let i=0;i<12;i++){
  const bush = new THREE.Group();
  const bx = (Math.random()-0.5)*(TANK.w-6), bz = (Math.random()-0.5)*(TANK.d-5);
  bush.position.set(bx, 0.1, bz);
  const blades = 3 + Math.floor(Math.random()*3);
  const mat = new THREE.MeshStandardMaterial({
    color:weedColors[i%weedColors.length], roughness:0.72, metalness:0.02, side:THREE.DoubleSide
  });
  for(let b=0;b<blades;b++){
    const h = 3 + Math.random()*5.2, lean = 0.5+Math.random()*0.9;
    const pts = [];
    for(let s=0;s<=6;s++){
      const t = s/6;
      pts.push(new THREE.Vector3(Math.sin(t*2.3+b)*lean*t*1.5, t*h, Math.cos(t*1.7+b*0.7)*lean*t*0.9));
    }
    const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 26, 0.055+Math.random()*0.05, 6, false);
    const blade = new THREE.Mesh(geo, mat);
    blade.position.set((Math.random()-0.5)*1.1, 0, (Math.random()-0.5)*1.1);
    blade.rotation.y = Math.random()*Math.PI*2;
    bush.add(blade);
  }
  bush.userData = {phase:Math.random()*Math.PI*2, amp:0.08+Math.random()*0.09};
  weeds.push(bush); scene.add(bush);
}

/* ══════════════════════════════════════════════════════════
   7. ПОВЕРХНОСТЬ ВОДЫ + ПЛАНКТОН
══════════════════════════════════════════════════════════ */
const surfGeo = new THREE.PlaneGeometry(TANK.w-0.6, TANK.d-0.6, 48, 28);
const surfBase = surfGeo.attributes.position.array.slice();
const surface = new THREE.Mesh(surfGeo, new THREE.MeshPhysicalMaterial({
  color:0xa9e8ff, transparent:true, opacity:0.26, roughness:0.08, metalness:0.0,
  transmission:0.6, side:THREE.DoubleSide, depthWrite:false
}));
surface.rotation.x = -Math.PI/2;
surface.position.y = TANK.h - 0.55;
surface.renderOrder = 9;
scene.add(surface);

const planktonGeo = new THREE.BufferGeometry();
{
  const n=380, arr=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    arr[i*3]=(Math.random()-0.5)*(TANK.w-3);
    arr[i*3+1]=1+Math.random()*(TANK.h-3);
    arr[i*3+2]=(Math.random()-0.5)*(TANK.d-3);
  }
  planktonGeo.setAttribute('position', new THREE.BufferAttribute(arr,3));
}
const plankton = new THREE.Points(planktonGeo, new THREE.PointsMaterial({
  size:0.15, color:0x9fe8ff, transparent:true, opacity:0.5,
  depthWrite:false, blending:THREE.AdditiveBlending, sizeAttenuation:true
}));
scene.add(plankton);

/* ══════════════════════════════════════════════════════════
   8. РЫБКИ — анатомия
══════════════════════════════════════════════════════════ */
const sphereGeo = new THREE.SphereGeometry(1, 22, 16);
const eyeWhiteMat = new THREE.MeshStandardMaterial({color:0xf8fbff, roughness:0.22, metalness:0.05});
const pupilMat    = new THREE.MeshStandardMaterial({color:0x05070a, roughness:0.12, metalness:0.15});
const glintMat    = new THREE.MeshBasicMaterial({color:0xffffff});

function tailGeometry(){
  const s = new THREE.Shape();
  s.moveTo(0,0);
  s.quadraticCurveTo(-0.34, 0.40, -0.95, 0.62);
  s.lineTo(-1.18, 0.20);
  s.quadraticCurveTo(-0.58, 0.02, -1.18, -0.20);
  s.lineTo(-0.95, -0.62);
  s.quadraticCurveTo(-0.34, -0.40, 0, 0);
  const g = new THREE.ExtrudeGeometry(s, {depth:0.05, bevelEnabled:false});
  g.translate(0,0,-0.025);
  return g;
}
function finGeometry(w,h){
  const s = new THREE.Shape();
  s.moveTo(0,0);
  s.quadraticCurveTo(-w*0.45, h*0.55, -w, h*0.32);
  s.lineTo(-w*0.92, -h*0.28);
  s.quadraticCurveTo(-w*0.35, -h*0.42, 0, 0);
  const g = new THREE.ExtrudeGeometry(s, {depth:0.035, bevelEnabled:false});
  g.translate(0,0,-0.017);
  return g;
}
const TAIL_GEO = tailGeometry();
const DORSAL_GEO = finGeometry(1.05, 0.62);
const PEC_GEO = finGeometry(0.55, 0.34);
const ANAL_GEO = finGeometry(0.5, 0.3);

const fishArray = [];
const pickTargets = [];

function createFish(pos, schemeIdx){
  if(fishArray.length >= MAX_FISH) return null;
  const si = (schemeIdx === undefined) ? Math.floor(Math.random()*SCHEMES.length) : schemeIdx;
  const sc = SCHEMES[si];

  const bodyMat  = new THREE.MeshStandardMaterial({color:sc.body, roughness:0.40, metalness:0.28,
                    emissive:sc.body, emissiveIntensity:0.07});
  const backMat  = new THREE.MeshStandardMaterial({color:sc.back, roughness:0.55, metalness:0.18});
  const bellyMat = new THREE.MeshStandardMaterial({color:sc.belly, roughness:0.62, metalness:0.05});
  const finMat   = new THREE.MeshStandardMaterial({color:sc.fin, roughness:0.5, metalness:0.08,
                    transparent:true, opacity:0.88, side:THREE.DoubleSide,
                    emissive:sc.fin, emissiveIntensity:0.05});

  const g = new THREE.Group();

  const body = new THREE.Mesh(sphereGeo, bodyMat);
  body.scale.set(1.28, 0.62, 0.46); body.castShadow = true;
  g.add(body);

  const back = new THREE.Mesh(sphereGeo, backMat);
  back.scale.set(1.10, 0.30, 0.40); back.position.set(-0.06, 0.26, 0);
  g.add(back);

  const belly = new THREE.Mesh(sphereGeo, bellyMat);
  belly.scale.set(1.02, 0.34, 0.38); belly.position.set(0.06, -0.20, 0);
  g.add(belly);

  // хвост на шарнире
  const tailPivot = new THREE.Group();
  tailPivot.position.set(-1.22, 0, 0);
  const tail = new THREE.Mesh(TAIL_GEO, finMat);
  tail.scale.set(1.15, 1.05, 1);
  tailPivot.add(tail);
  g.add(tailPivot);

  // спинной плавник
  const dorsal = new THREE.Mesh(DORSAL_GEO, finMat);
  dorsal.position.set(0.18, 0.52, 0); dorsal.rotation.z = 0.12;
  g.add(dorsal);

  // анальный плавник
  const anal = new THREE.Mesh(ANAL_GEO, finMat);
  anal.position.set(-0.62, -0.42, 0); anal.rotation.set(Math.PI, 0, -0.18);
  g.add(anal);

  // грудные плавники
  const leftFin = new THREE.Mesh(PEC_GEO, finMat);
  leftFin.position.set(0.34, -0.10, 0.40); leftFin.rotation.set(0, -0.55, -0.35);
  g.add(leftFin);
  const rightFin = new THREE.Mesh(PEC_GEO, finMat);
  rightFin.position.set(0.34, -0.10, -0.40); rightFin.rotation.set(0, Math.PI+0.55, 0.35);
  g.add(rightFin);

  // глаза
  [0.40, -0.40].forEach(z=>{
    const w = new THREE.Mesh(sphereGeo, eyeWhiteMat); w.scale.setScalar(0.17);
    w.position.set(0.86, 0.16, z*0.82); g.add(w);
    const p = new THREE.Mesh(sphereGeo, pupilMat); p.scale.setScalar(0.10);
    p.position.set(1.00, 0.16, z*0.95); g.add(p);
    const gl = new THREE.Mesh(sphereGeo, glintMat); gl.scale.setScalar(0.045);
    gl.position.set(1.02, 0.24, z*0.98); g.add(gl);
  });

  // рот
  const mouth = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({color:sc.back, roughness:0.7}));
  mouth.scale.set(0.13, 0.09, 0.20); mouth.position.set(1.16, -0.06, 0);
  g.add(mouth);

  const s = 0.6 + Math.random()*0.6;
  g.position.copy(pos);
  scene.add(g);

  body.userData.fishIndex = fishArray.length;
  pickTargets.push(body);

  fishArray.push({
    mesh:g, body:body, tail:tailPivot, dorsal:dorsal, anal:anal,
    leftFin:leftFin, rightFin:rightFin,
    velocity:new THREE.Vector3((Math.random()-0.5)*2, (Math.random()-0.5)*0.6, (Math.random()-0.5)*2),
    speed:1.9 + Math.random()*1.7,
    tailSpeed:4.5 + Math.random()*4.5,
    phase:Math.random()*Math.PI*2,
    targetFood:null,
    avoidanceRadius:2.2 + Math.random()*1.8,
    scale:s, targetScale:s,
    yaw:Math.random()*Math.PI*2, pitch:0, roll:0,
    wander:new THREE.Vector3(Math.random()-0.5, (Math.random()-0.5)*0.3, Math.random()-0.5).normalize(),
    wanderTimer:Math.random()*3,
    scheme:si, popT:0
  });
  return fishArray.length-1;
}
for(let i=0;i<15;i++){
  createFish(new THREE.Vector3((Math.random()-0.5)*24, 3+Math.random()*16, (Math.random()-0.5)*12));
}

/* ══════════════════════════════════════════════════════════
   9. ПУЗЫРИ
══════════════════════════════════════════════════════════ */
const bubbleGeo = new THREE.SphereGeometry(1, 14, 10);
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color:0xcfeeff, transparent:true, opacity:0.55, transmission:0.55,
  roughness:0.06, metalness:0.0, clearcoat:1.0, ior:1.12, side:THREE.DoubleSide, depthWrite:false
});
const bubbles = [];
function addBubble(){
  const b = new THREE.Mesh(bubbleGeo, bubbleMat);
  const r = 0.10 + Math.random()*0.30;
  b.scale.setScalar(r);
  b.position.set((Math.random()-0.5)*(TANK.w-4), 0.6+Math.random()*(TANK.h-3), (Math.random()-0.5)*(TANK.d-4));
  b.renderOrder = 8;
  scene.add(b);
  bubbles.push({mesh:b, r:r, v:0.7+Math.random()*1.6, ph:Math.random()*Math.PI*2, amp:0.25+Math.random()*0.7});
}
for(let i=0;i<30;i++) addBubble();

/* ══════════════════════════════════════════════════════════
   10. КОРМ + КРУГИ НА ВОДЕ
══════════════════════════════════════════════════════════ */
const flakeGeo = new THREE.SphereGeometry(0.26, 8, 6);
const flakeMat = new THREE.MeshStandardMaterial({color:0xffcf7a, roughness:0.7,
  emissive:0xff8a3d, emissiveIntensity:0.25});
const foodArray = [];

function createFood(x, y, z){
  const g = new THREE.Group();
  for(let i=0;i<3;i++){
    const f = new THREE.Mesh(flakeGeo, flakeMat);
    f.position.set((Math.random()-0.5)*0.42, (Math.random()-0.5)*0.36, (Math.random()-0.5)*0.42);
    f.scale.setScalar(0.6+Math.random()*0.7);
    g.add(f);
  }
  g.position.set(x, y, z);
  scene.add(g);
  foodArray.push({mesh:g, vel:new THREE.Vector3((Math.random()-0.5)*0.7, -0.4, (Math.random()-0.5)*0.7),
                  spin:(Math.random()-0.5)*2});
  return foodArray.length-1;
}

const rippleGeo = new THREE.RingGeometry(0.35, 0.52, 40);
const ripples = [];
function ripple(x, z){
  const m = new THREE.Mesh(rippleGeo, new THREE.MeshBasicMaterial({
    color:0xa8f4ff, transparent:true, opacity:0.75, side:THREE.DoubleSide, depthWrite:false}));
  m.rotation.x = -Math.PI/2; m.position.set(x, TANK.h-0.5, z);
  scene.add(m); ripples.push({mesh:m, t:0});
}

/* ══════════════════════════════════════════════════════════
   11. КЛИКИ = КОРМ / ИНСПЕКЦИЯ РЫБКИ
══════════════════════════════════════════════════════════ */
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let downX=0, downY=0, downT=0;

renderer.domElement.addEventListener('pointerdown', e=>{
  if(e.button!==0) return;
  downX=e.clientX; downY=e.clientY; downT=performance.now();
});
renderer.domElement.addEventListener('pointerup', e=>{
  if(e.button!==0) return;
  if(Math.hypot(e.clientX-downX, e.clientY-downY) > 7) return;
  if(performance.now()-downT > 420) return;

  ndc.x = (e.clientX/innerWidth)*2-1;
  ndc.y = -(e.clientY/innerHeight)*2+1;
  raycaster.setFromCamera(ndc, camera);

  // 1) клик по рыбке → карточка
  const hitFish = raycaster.intersectObjects(pickTargets, false)[0];
  if(hitFish){
    const f = fishArray[hitFish.object.userData.fishIndex];
    if(f){
      f.popT = 1;
      toast(`Рыбка #${hitFish.object.userData.fishIndex+1} · ${SCHEMES[f.scheme].name} · ${(f.scale).toFixed(2)}×`);
      ripple(f.mesh.position.x, f.mesh.position.z);
    }
    return;
  }

  // 2) клик по воде → корм с поверхности
  const hit = raycaster.intersectObject(waterVolume, false)[0];
  let x=0, z=0;
  if(hit){ x = hit.point.x; z = hit.point.z; }
  x = THREE.MathUtils.clamp(x, -B.x+1, B.x-1);
  z = THREE.MathUtils.clamp(z, -B.z+1, B.z-1);
  createFood(x, TANK.h-1.2, z);
  ripple(x, z);
});

/* ══════════════════════════════════════════════════════════
   12. UI
══════════════════════════════════════════════════════════ */
const $ = id => document.getElementById(id);
const toastsEl = $('toasts');
function toast(txt){
  const d = document.createElement('div');
  d.className='toast'; d.textContent = txt;
  toastsEl.appendChild(d);
  setTimeout(()=>{ d.classList.add('out'); setTimeout(()=>d.remove(), 460); }, 2100);
}
function pulse(el){ el.classList.remove('pulse'); void el.offsetWidth; el.classList.add('pulse'); }

$('bFish').onclick = ()=>{
  const i = createFish(new THREE.Vector3((Math.random()-0.5)*20, TANK.h-3-Math.random()*4, (Math.random()-0.5)*10));
  if(i===null){ toast('Бак заполнен — 48 рыбок'); return; }
  toast(`Запущена новая рыбка · ${SCHEMES[fishArray[i].scheme].name}`);
  pulse($('sFish'));
};
$('bBub').onclick = ()=>{ for(let i=0;i<10;i++) addBubble(); toast('+10 пузырей'); pulse($('sBub')); };
$('bFeed').onclick = ()=>{
  for(let i=0;i<5;i++){
    const x=(Math.random()-0.5)*24, z=(Math.random()-0.5)*12;
    createFood(x, TANK.h-1.2-Math.random()*1.5, z); ripple(x,z);
  }
  toast('Порция корма брошена'); pulse($('sFood'));
};

let night = false;
const LIT = {sun:1.25, amb:0.4, pA:1.5, pB:1.1, fog:0.0165, exp:1.06};
const DARK= {sun:0.18, amb:0.22, pA:2.6, pB:2.0, fog:0.027, exp:1.22};
const lightTarget = {...LIT};
$('bLight').onclick = (e)=>{
  night = !night;
  Object.assign(lightTarget, night ? DARK : LIT);
  document.body.classList.toggle('night', night);
  e.currentTarget.textContent = night ? '☀ Дневной свет' : '☾ Ночной свет';
  e.currentTarget.classList.toggle('on', night);
  toast(night ? 'Ночной режим: подводные прожекторы' : 'Дневной режим: солнечный свет');
};
$('bOrbit').onclick = (e)=>{
  controls.autoRotate = !controls.autoRotate;
  controls.autoRotateSpeed = 0.55;
  e.currentTarget.classList.toggle('on', controls.autoRotate);
  toast(controls.autoRotate ? 'Автооблёт включён' : 'Автооблёт выключен');
};

// легенда схем
const swWrap = $('swatches');
SCHEMES.forEach(s=>{
  const d = document.createElement('div');
  d.className='sw'; d.dataset.n = s.name;
  d.style.background = `radial-gradient(circle at 32% 28%, #${s.belly.toString(16).padStart(6,'0')}, #${s.body.toString(16).padStart(6,'0')} 55%, #${s.back.toString(16).padStart(6,'0')})`;
  swWrap.appendChild(d);
});

/* ══════════════════════════════════════════════════════════
   13. ЦИКЛ АНИМАЦИИ
══════════════════════════════════════════════════════════ */
const clock = new THREE.Clock();
let introT = 0;
const camA = new THREE.Vector3(52,40,52), camB = new THREE.Vector3(29,21,31);
const tmpV = new THREE.Vector3(), acc = new THREE.Vector3();

function lerpAngle(a,b,t){ let d=b-a; while(d>Math.PI)d-=Math.PI*2; while(d<-Math.PI)d+=Math.PI*2; return a+d*t; }

let frames=0, fpsT=performance.now(), fps=60;
const hist = new Array(40).fill(60);
const gctx = $('fpsGraph').getContext('2d');
function drawGraph(){
  const w=160,h=30; gctx.clearRect(0,0,w,h);
  for(let i=0;i<hist.length;i++){
    const v = Math.min(1, hist[i]/70);
    const bh = Math.max(1.5, v*h);
    gctx.fillStyle = v>0.62 ? 'rgba(95,242,214,.85)' : (v>0.4 ? 'rgba(255,196,90,.85)' : 'rgba(255,110,90,.85)');
    gctx.fillRect(i*4, h-bh, 2.6, bh);
  }
}

let statT = 0;
function updateStats(){
  $('sFish').textContent = fishArray.length;
  $('sFood').textContent = foodArray.length;
  $('sBub').textContent  = bubbles.length;
  const avg = fishArray.reduce((s,f)=>s+f.scale,0)/Math.max(1,fishArray.length);
  $('sSize').textContent = avg.toFixed(2)+'×';
  $('sFps').textContent  = fps;
}

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // —— интро-подлёт камеры
  if(introT < 1){
    introT = Math.min(1, introT + dt/2.4);
    const e = 1 - Math.pow(1-introT, 3);
    camera.position.lerpVectors(camA, camB, e);
    camera.lookAt(controls.target);
    if(introT>=1) controls.enabled = true;
  } else controls.update();

  // —— свет (плавный переход к цели)
  sun.intensity      = THREE.MathUtils.lerp(sun.intensity, lightTarget.sun, dt*2.2);
  ambient.intensity  = THREE.MathUtils.lerp(ambient.intensity, lightTarget.amb, dt*2.2);
  underA.intensity   = THREE.MathUtils.lerp(underA.intensity, lightTarget.pA, dt*2.2);
  underB.intensity   = THREE.MathUtils.lerp(underB.intensity, lightTarget.pB, dt*2.2);
  scene.fog.density  = THREE.MathUtils.lerp(scene.fog.density, lightTarget.fog, dt*1.6);
  renderer.toneMappingExposure = THREE.MathUtils.lerp(renderer.toneMappingExposure, lightTarget.exp, dt*2);
  const fogTarget = night ? new THREE.Color(0x04203a) : new THREE.Color(0x08405f);
  scene.fog.color.lerp(fogTarget, dt*1.6);
  // дрожание света
  sun.intensity += Math.sin(t*2.1)*0.012 + Math.sin(t*3.7)*0.008;
  underA.position.x = -13 + Math.sin(t*0.24)*2.2;
  underB.position.z =  8  + Math.cos(t*0.19)*2.0;

  // —— поверхность воды
  {
    const p = surfGeo.attributes.position;
    for(let i=0;i<p.count;i++){
      const x = surfBase[i*3], z = surfBase[i*3+2];
      p.setZ(i, Math.sin(x*0.55 + t*1.6)*0.16 + Math.cos(z*0.7 - t*1.2)*0.13 + Math.sin((x+z)*0.3 + t*0.8)*0.09);
    }
    p.needsUpdate = true;
  }

  // —— водоросли
  weeds.forEach(w=>{
    w.rotation.x = Math.sin(t*0.72 + w.userData.phase) * w.userData.amp;
    w.rotation.z = Math.cos(t*0.55 + w.userData.phase*1.4) * w.userData.amp;
  });

  // —— планктон
  plankton.rotation.y += dt*0.024;
  plankton.position.y = Math.sin(t*0.35)*0.35;

  // —— пузыри
  for(let i=bubbles.length-1;i>=0;i--){
    const b = bubbles[i];
    b.mesh.position.y += b.v*dt;
    b.mesh.position.x += Math.cos(t*1.4 + b.ph)*b.amp*dt;
    b.mesh.position.z += Math.sin(t*1.1 + b.ph)*b.amp*dt;
    b.mesh.scale.setScalar(b.r*(1+Math.sin(t*3+b.ph)*0.06));
    if(b.mesh.position.y > TANK.h-0.9){
      b.mesh.position.y = 0.55;
      b.mesh.position.x = (Math.random()-0.5)*(TANK.w-4);
      b.mesh.position.z = (Math.random()-0.5)*(TANK.d-4);
    }
  }

  // —— корм
  for(let i=foodArray.length-1;i>=0;i--){
    const f = foodArray[i];
    f.vel.y -= 5.6*dt;
    f.vel.x *= (1-0.7*dt); f.vel.z *= (1-0.7*dt);
    f.mesh.position.addScaledVector(f.vel, dt);
    f.mesh.rotation.y += f.spin*dt; f.mesh.rotation.x += f.spin*0.6*dt;
    if(f.mesh.position.y < 0.55){ scene.remove(f.mesh); foodArray.splice(i,1); }
  }

  // —— рыбки: стейринг-ИИ
  for(let i=0;i<fishArray.length;i++){
    const f = fishArray[i], pos = f.mesh.position;
    acc.set(0,0,0);

    // блуждание
    f.wanderTimer -= dt;
    if(f.wanderTimer <= 0){
      f.wanderTimer = 2 + Math.random()*3.6;
      f.wander.set((Math.random()-0.5), (Math.random()-0.5)*0.35, (Math.random()-0.5)).normalize();
    }
    acc.addScaledVector(f.wander, 1.7);

    // разделение
    for(let j=0;j<fishArray.length;j++){
      if(j===i) continue;
      const o = fishArray[j];
      const dx = pos.x-o.mesh.position.x, dy = pos.y-o.mesh.position.y, dz = pos.z-o.mesh.position.z;
      const d2 = dx*dx+dy*dy+dz*dz;
      const R = f.avoidanceRadius + o.avoidanceRadius*0.35;
      if(d2 < R*R && d2 > 0.0001){
        const d = Math.sqrt(d2), k = (R-d)/R;
        acc.x += dx/d*k*9; acc.y += dy/d*k*4.5; acc.z += dz/d*k*9;
      }
    }

    // мягкое отражение от стенок
    const m = 2.6;
    if(pos.x >  B.x-m) acc.x -= (pos.x-(B.x-m))*4.2;
    if(pos.x < -B.x+m) acc.x += (-B.x+m-pos.x)*4.2;
    if(pos.z >  B.z-m) acc.z -= (pos.z-(B.z-m))*4.6;
    if(pos.z < -B.z+m) acc.z += (-B.z+m-pos.z)*4.6;
    if(pos.y >  B.yMax-1.6) acc.y -= (pos.y-(B.yMax-1.6))*4.0;
    if(pos.y <  B.yMin+1.2) acc.y += (B.yMin+1.2-pos.y)*4.0;

    // преследование корма
    f.targetFood = null;
    let best = 15;
    for(let k=0;k<foodArray.length;k++){
      const fd = foodArray[k].mesh.position;
      const d = pos.distanceTo(fd);
      if(d < best){ best = d; f.targetFood = foodArray[k]; }
    }
    let chasing = false;
    if(f.targetFood){
      chasing = true;
      tmpV.copy(f.targetFood.mesh.position).sub(pos).normalize();
      acc.addScaledVector(tmpV, 13);
      const eatR = 1.25*f.scale + 0.45;
      if(best < eatR){
        const idx = foodArray.indexOf(f.targetFood);
        scene.remove(f.targetFood.mesh);
        foodArray.splice(idx,1);
        f.targetScale = Math.min(2.1, f.targetScale*1.05);
        f.popT = 1;
        pulse($('sFood'));
        toast(`Рыбка #${i+1} съела корм · рост ${(f.targetScale/f.scale*100-100).toFixed(0)}%`);
      }
    }

    // интеграция
    f.velocity.addScaledVector(acc, dt);
    f.velocity.multiplyScalar(1 - 0.85*dt);
    const sp = f.velocity.length();
    const maxSp = f.speed*(chasing?2.1:1)*(1/f.scale*0.9+0.25);
    if(sp > maxSp) f.velocity.multiplyScalar(maxSp/sp);
    if(sp < 0.35) f.velocity.addScaledVector(f.wander, 1.6*dt);
    pos.addScaledVector(f.velocity, dt);

    // жёсткие границы с отражением
    if(pos.x > B.x){ pos.x = B.x; f.velocity.x *= -0.7; }
    if(pos.x < -B.x){ pos.x = -B.x; f.velocity.x *= -0.7; }
    if(pos.z > B.z){ pos.z = B.z; f.velocity.z *= -0.7; }
    if(pos.z < -B.z){ pos.z = -B.z; f.velocity.z *= -0.7; }
    if(pos.y > B.yMax){ pos.y = B.yMax; f.velocity.y *= -0.6; }
    if(pos.y < B.yMin){ pos.y = B.yMin; f.velocity.y *= -0.6; }

    // рост + «поп» при поедании
    f.scale = THREE.MathUtils.lerp(f.scale, f.targetScale, dt*2.4);
    if(f.popT > 0){
      f.popT = Math.max(0, f.popT - dt*1.8);
      const k = 1 + Math.sin(f.popT*Math.PI)*0.16;
      f.mesh.scale.setScalar(f.scale*k);
    } else f.mesh.scale.setScalar(f.scale);

    // ориентация по вектору движения
    const v = f.velocity;
    const hSp = Math.hypot(v.x, v.z);
    const targetYaw = Math.atan2(-v.z, v.x);
    const prevYaw = f.yaw;
    f.yaw = lerpAngle(f.yaw, targetYaw, 1 - Math.pow(0.0008, dt));
    f.pitch = lerpAngle(f.pitch, -Math.atan2(v.y, Math.max(hSp, 0.6))*0.85, 1 - Math.pow(0.02, dt));
    const turn = lerpAngle(0, lerpAngle(0, targetYaw-prevYaw, 1), 1);
    f.roll = lerpAngle(f.roll, THREE.MathUtils.clamp(-turn*2.2, -0.6, 0.6), 1 - Math.pow(0.05, dt));
    f.mesh.rotation.set(f.pitch, f.yaw, f.roll);

    // анимация плавников и хвоста
    const w = (chasing?1.55:1) * f.tailSpeed;
    const s = Math.sin(t*w + f.phase);
    f.tail.rotation.y = s*0.62;
    f.body.rotation.y = Math.sin(t*w + f.phase - 0.7)*0.13;
    f.dorsal.rotation.z = 0.12 + Math.sin(t*w*0.75 + f.phase)*0.14;
    f.anal.rotation.z  = -0.18 + Math.sin(t*w*0.75 + f.phase + 1.2)*0.16;
    f.leftFin.rotation.y  = -0.55 + Math.sin(t*w*0.9 + f.phase)*0.5;
    f.rightFin.rotation.y =  Math.PI+0.55 - Math.sin(t*w*0.9 + f.phase)*0.5;
    f.leftFin.rotation.z  = -0.35 + Math.cos(t*w*0.9 + f.phase)*0.18;
    f.rightFin.rotation.z =  0.35 - Math.cos(t*w*0.9 + f.phase)*0.18;
  }

  // —— круги на воде
  for(let i=ripples.length-1;i>=0;i--){
    const r = ripples[i]; r.t += dt;
    const k = r.t/1.25;
    r.mesh.scale.setScalar(1 + k*7);
    r.mesh.material.opacity = 0.75*(1-k);
    if(k>=1){ scene.remove(r.mesh); r.mesh.material.dispose(); ripples.splice(i,1); }
  }

  // —— статы / FPS
  frames++;
  const now = performance.now();
  if(now - fpsT > 500){
    fps = Math.round(frames*1000/(now-fpsT));
    frames = 0; fpsT = now;
    hist.push(fps); hist.shift();
    drawGraph();
  }
  statT += dt;
  if(statT > 0.25){ statT = 0; updateStats(); }

  renderer.render(scene, camera);
}

addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

updateStats(); drawGraph(); animate();
setTimeout(()=>document.getElementById('loader').classList.add('gone'), 1500);
setTimeout(()=>toast('Кликните по воде, чтобы покормить рыб'), 2600);
</script>
</body>
</html>
```

## Что внутри

| Модуль | Реализация |
|---|---|
| **Анатомия** | Тело (сфера × масштаб) + countershading-спина + светлое брюхо, хвостовой веер на шарнире (`ExtrudeGeometry` из `Shape`), спинной, анальный и 2 грудных плавника, глаз: склера → зрачок → блик, рот |
| **8 схем** | Оранжевая, синяя, жёлто-красная, фиолетовая, красная, зелёная, розовая, золотая — каждая с 4 производными цветами (тело/плавники/брюхо/спина) |
| **ИИ** | Силы: блуждание → разделение по `avoidanceRadius` → мягкий отбойник у стенок + жёсткое отражение → преследование ближайшего корма (радиус 15) → съедение и рост ×1.05 с «поп»-анимацией |
| **Плавники** | Yaw/pitch/roll сглаживаются по вектору скорости (bank в повороте), хвост и тело идут бегущей волной с фазовым сдвигом, грудные плавники взмахивают синхронно с `tailSpeed` |
| **Окружение** | Бак 36×24×20 (`transmission: 0.95`, `ior: 1.33`, `clearcoat`), `EdgesGeometry`-рама, металлический подиум и верхняя оправа; дно с дюнами, вертексными цветами и тенями; 8 деформированных додекаэдров; 12 кустов TubeGeometry с покачиванием |
| **Пузыри** | 30 стартовых, `MeshPhysicalMaterial` c transmission + «дыхание» радиуса, синусоидальное покачивание, сброс у поверхности, кнопка +10 |
| **Корм** | 3 хлопья в группе, гравитация 5.6, снос по X/Z, исчезновение у дна, расходящееся кольцо на поверхности при броске |
| **Свет** | Ambient `0x404040 / 0.4`, Directional с PCFSoft 2048² и мерцанием, 2 PointLight (голубой/синий) с дрейфом; кнопка переключает дневной ↔ ночной режим (экспозиция, плотность и цвет тумана, CSS-градиент фона) |
| **HUD** | Панель управления + FPS-спарклайн (реальный график за 20 секунд), счётчики с pop-анимацией, легенда 8 схем с тултипами, тосты событий, экран заполнения водой |

Бонусом: клик по самой рыбке показывает карточку (номер, схема, текущий размер) с всплеском воды, «Автооблёт» включает медленное вращение камеры, а 380 частиц планктона и caustic-слой создают живую толщу воды.