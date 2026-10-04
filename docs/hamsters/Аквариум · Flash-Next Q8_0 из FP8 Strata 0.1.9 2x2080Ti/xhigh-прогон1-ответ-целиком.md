# 🐠 Аквариум «Живая система» — установка №07

Единый HTML-файл: Three.js r128 + OrbitControls, процедурные рыбы с canvas-текстурами окраса, стаи с избеганием/ростом, кормление кликом, стеклянный резервуар в металлической раме, каустика, god-ray лучи и приборный HUD в стиле натурной таблицы.

```html
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Аквариум · живая система</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,700;1,6..96,500;1,6..96,700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{
  --abyss:#010c15; --deep:#04202f; --mid:#0a3a52;
  --foam:#eaf7fb; --mist:#9dc3d6;
  --sand:#e8d3a5; --coral:#ff6b3d; --amber:#ffbb52; --bio:#5fe9ff;
  --panel:rgba(5,30,44,.58);
  --stroke:rgba(120,214,240,.20);
  --shadow:0 26px 70px rgba(0,6,12,.55);
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0; overflow:hidden; color:var(--foam);
  background:var(--abyss);
  font-family:'IBM Plex Sans',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;
  transition:background 1.1s ease;
}
html.night body{background:#00060c}

/* ————— фоновые слои ————— */
.bg{position:fixed;inset:0;z-index:0;pointer-events:none;transition:opacity 1.1s ease;
  background:
   radial-gradient(130% 85% at 50% -12%, #1c86a8 0%, rgba(10,64,88,.92) 28%, rgba(3,26,40,0) 63%),
   radial-gradient(95% 65% at 10% 104%, rgba(232,211,165,.18), transparent 58%),
   linear-gradient(#073046 0%, #04202f 46%, #010c15 100%);
}
html.night .bg{opacity:.42}
#scene{position:fixed;inset:0;display:block;width:100%;height:100%;z-index:1;touch-action:none}
.caustics{position:fixed;inset:-14%;z-index:3;pointer-events:none;mix-blend-mode:screen;opacity:.26;
  background:
   repeating-conic-gradient(from 8deg at 32% 8%, rgba(150,240,255,0) 0deg 11deg, rgba(160,245,255,.20) 13deg 16deg),
   radial-gradient(46% 30% at 72% 4%, rgba(200,252,255,.42), transparent 72%);
  filter:blur(30px); animation:drift 34s linear infinite;
}
.caustics--b{mix-blend-mode:soft-light;opacity:.30;animation-duration:52s;animation-direction:reverse;
  background:repeating-conic-gradient(from 190deg at 66% -4%, rgba(255,255,255,0) 0deg 9deg, rgba(255,255,255,.22) 11deg 13deg);}
@keyframes drift{0%{transform:translate3d(-3%,0,0) scale(1.05)}50%{transform:translate3d(3%,2%,0) scale(1.14)}100%{transform:translate3d(-3%,0,0) scale(1.05)}}
.grain{position:fixed;inset:0;z-index:4;pointer-events:none;opacity:.16;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/></filter><rect width='180' height='180' filter='url(%23n)' opacity='.6'/></svg>");}
.vig{position:fixed;inset:0;z-index:5;pointer-events:none;
  background:radial-gradient(120% 90% at 50% 46%, transparent 40%, rgba(0,8,14,.62) 100%);}

/* ————— HUD ————— */
.hud{position:fixed;inset:0;z-index:10;pointer-events:none;padding:clamp(14px,2.2vw,30px);
  display:grid;grid-template-columns:minmax(260px,340px) 1fr minmax(240px,300px);
  grid-template-rows:auto 1fr auto;gap:18px;align-items:start}
.reveal{opacity:0;transform:translateY(14px);animation:rise .9s cubic-bezier(.2,.75,.25,1) forwards;animation-delay:var(--d,0s)}
@keyframes rise{to{opacity:1;transform:none}}

.brand{grid-column:1;grid-row:1;pointer-events:auto}
.eyebrow{display:flex;align-items:center;gap:.5rem;margin:0 0 .7rem;
  font-family:'IBM Plex Mono',monospace;font-size:.63rem;letter-spacing:.24em;text-transform:uppercase;color:#8fd6ef}
.dot{width:7px;height:7px;border-radius:50%;background:var(--coral);box-shadow:0 0 0 0 rgba(255,107,61,.7);animation:pulse 2.4s infinite}
@keyframes pulse{70%{box-shadow:0 0 0 11px rgba(255,107,61,0)}100%{box-shadow:0 0 0 0 rgba(255,107,61,0)}}
.brand h1{margin:0;font-family:'Bodoni Moda',serif;font-weight:700;font-size:clamp(2.9rem,6.6vw,5.1rem);
  line-height:.86;letter-spacing:-.025em;text-shadow:0 18px 46px rgba(0,10,18,.65)}
.brand h1 em{display:block;font-size:.2em;font-style:italic;font-weight:500;letter-spacing:.02em;
  color:var(--sand);margin-top:.7rem;padding-left:.4em;border-left:2px solid var(--coral)}
.lede{max-width:30ch;margin:1.1rem 0 0;font-size:.86rem;font-weight:300;line-height:1.55;color:#b9d6e3}

.panel{pointer-events:auto;background:var(--panel);border:1px solid var(--stroke);
  backdrop-filter:blur(16px) saturate(1.25);-webkit-backdrop-filter:blur(16px) saturate(1.25);
  box-shadow:var(--shadow), inset 0 1px 0 rgba(255,255,255,.06);position:relative;padding:14px}
.panel::before,.panel::after{content:'';position:absolute;width:9px;height:9px;border:1px solid rgba(255,187,82,.55)}
.panel::before{top:-1px;left:-1px;border-right:0;border-bottom:0}
.panel::after{bottom:-1px;right:-1px;border-left:0;border-top:0}
.ph{display:flex;align-items:baseline;gap:.6rem;margin:0 0 .85rem;font-family:'IBM Plex Mono',monospace;
  font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:#a9d8ea;font-weight:500}
.ph::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(140,220,245,.35),transparent)}
.ph i{font-style:normal;color:#6fa7bd}

.controls{grid-column:1;grid-row:2;align-self:start;margin-top:22px}
.btn{display:flex;align-items:center;gap:.6rem;width:100%;margin-bottom:.5rem;padding:.68rem .75rem;
  background:linear-gradient(100deg,rgba(255,107,61,.14),rgba(95,233,255,.05));
  border:1px solid rgba(255,140,90,.3);color:var(--foam);cursor:pointer;position:relative;overflow:hidden;
  font-family:'IBM Plex Mono',monospace;font-size:.7rem;letter-spacing:.09em;text-transform:uppercase;
  transition:transform .3s cubic-bezier(.2,.8,.2,1),border-color .3s,box-shadow .3s,background .3s}
.btn:last-child{margin-bottom:0}
.btn span.g{font-size:.95rem;line-height:1;filter:saturate(1.3)}
.btn .k{margin-left:auto;font-size:.58rem;opacity:.55;border:1px solid rgba(255,255,255,.16);padding:.14rem .3rem}
.btn::after{content:'';position:absolute;inset:0;transform:translateX(-110%);transition:transform .65s ease;
  background:linear-gradient(100deg,transparent 25%,rgba(255,255,255,.2),transparent 75%)}
.btn:hover{transform:translateX(5px);border-color:rgba(255,187,82,.85);
  background:linear-gradient(100deg,rgba(255,107,61,.3),rgba(95,233,255,.1));
  box-shadow:0 12px 34px rgba(255,107,61,.18)}
.btn:hover::after{transform:translateX(110%)}
.btn:active{transform:translateX(2px) scale(.985)}
.btn.is-off{border-color:rgba(120,170,190,.28);background:rgba(10,40,55,.4);color:#8fb3c4}

.stats{grid-column:3;grid-row:1}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:2px;background:rgba(140,220,245,.12)}
.stat{background:rgba(4,26,38,.72);padding:.6rem .7rem}
.stat b{display:block;font-family:'Bodoni Moda',serif;font-weight:700;font-size:1.85rem;line-height:1;
  color:#fff;letter-spacing:-.01em}
.stat span{display:block;margin-top:.28rem;font-family:'IBM Plex Mono',monospace;font-size:.55rem;
  letter-spacing:.16em;text-transform:uppercase;color:#7fb3c8}
#spark{display:block;width:100%;height:42px;margin-top:10px}
.tele{margin:.5rem 0 0;font-family:'IBM Plex Mono',monospace;font-size:.6rem;letter-spacing:.1em;color:#6fa7bd}

.legend{grid-column:3;grid-row:2;align-self:start;margin-top:16px}
.legend ul{list-style:none;margin:0;padding:0}
.legend li{display:flex;align-items:center;gap:.6rem;padding:.34rem .35rem;cursor:pointer;
  border-bottom:1px solid rgba(140,220,245,.08);transition:.25s;font-size:.76rem;color:#cfe6ef}
.legend li:hover{background:rgba(95,233,255,.1);transform:translateX(4px);color:#fff}
.sw{width:26px;height:11px;flex:0 0 26px;border-radius:1px;box-shadow:0 0 0 1px rgba(0,0,0,.4),0 0 14px rgba(255,255,255,.12)}
.legend em{margin-left:auto;font-style:normal;font-family:'IBM Plex Mono',monospace;font-size:.6rem;color:#6fa7bd}

.hints{grid-column:1/4;grid-row:3;justify-self:center;pointer-events:none;display:flex;flex-wrap:wrap;
  justify-content:center;gap:.45rem .9rem;font-family:'IBM Plex Mono',monospace;font-size:.62rem;
  letter-spacing:.12em;text-transform:uppercase;color:#8fbfd3;text-shadow:0 2px 12px rgba(0,10,18,.9)}
.hints b{color:#fff;background:rgba(6,34,48,.7);border:1px solid var(--stroke);padding:.2rem .42rem;font-weight:500}

.toast{position:fixed;z-index:20;pointer-events:none;transform:translate(-50%,-50%);
  font-family:'IBM Plex Mono',monospace;font-size:.66rem;letter-spacing:.1em;color:var(--amber);
  text-shadow:0 0 16px rgba(255,187,82,.6);animation:floatUp .95s ease-out forwards}
@keyframes floatUp{0%{opacity:0;transform:translate(-50%,-50%) scale(.7)}18%{opacity:1}100%{opacity:0;transform:translate(-50%,-160%) scale(1.05)}}

/* ————— boot ————— */
#boot{position:fixed;inset:0;z-index:40;background:linear-gradient(#031824,#000810);display:grid;place-items:center;
  transition:opacity .9s ease,visibility .9s}
#boot.done{opacity:0;visibility:hidden}
.boot-in{width:min(420px,84vw)}
.boot-in h3{font-family:'Bodoni Moda',serif;font-style:italic;font-weight:500;font-size:2.4rem;margin:0 0 .3rem}
.boot-log{font-family:'IBM Plex Mono',monospace;font-size:.66rem;letter-spacing:.12em;color:#6fa7bd;min-height:5.4em;margin-top:1rem}
.boot-log div{opacity:0;animation:rise .5s forwards}
.bar{height:2px;background:rgba(140,220,245,.18);margin-top:1rem;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--coral),var(--bio));transition:width .25s}

@media (max-width:1040px){
  .hud{grid-template-columns:1fr auto}
  .legend{display:none}
  .lede{display:none}
}
@media (max-width:680px){
  .hud{grid-template-columns:1fr;grid-template-rows:auto auto 1fr auto;gap:10px}
  .brand h1{font-size:2.6rem}
  .controls{grid-column:1;grid-row:2;margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:.4rem}
  .btn{margin-bottom:0}
  .stats{grid-column:1;grid-row:1;justify-self:end;width:min(300px,60vw)}
  #spark{height:30px}
  .hints{grid-row:4;font-size:.55rem}
}
</style>
</head>
<body>
<div class="bg"></div>
<canvas id="scene"></canvas>
<div class="caustics" aria-hidden="true"></div>
<div class="caustics caustics--b" aria-hidden="true"></div>
<div class="grain" aria-hidden="true"></div>
<div class="vig" aria-hidden="true"></div>

<div class="hud">
  <header class="brand reveal">
    <p class="eyebrow"><span class="dot"></span>Морская лаборатория · установка №07</p>
    <h1>Аквариум<em>живая система · three.js</em></h1>
    <p class="lede">Тропическое сообщество в резервуаре 36×24×20. Кормите рыбу, следите за телеметрией, запускайте новые особи.</p>
  </header>

  <section class="panel controls reveal" style="--d:.12s">
    <h2 class="ph"><span>Управление</span><i>01</i></h2>
    <button class="btn" id="btnFish"><span class="g">＋</span>Добавить рыбку<span class="k">F</span></button>
    <button class="btn" id="btnFeed"><span class="g">◍</span>Покормить ×5<span class="k">Space</span></button>
    <button class="btn" id="btnBub"><span class="g">◦</span>Больше пузырей<span class="k">B</span></button>
    <button class="btn" id="btnLight"><span class="g">☀</span>Основной свет<span class="k">L</span></button>
  </section>

  <section class="panel stats reveal" style="--d:.2s">
    <h2 class="ph"><span>Телеметрия</span><i>live</i></h2>
    <div class="grid">
      <div class="stat"><b id="sFish">15</b><span>особей</span></div>
      <div class="stat"><b id="sFood">0</b><span>корминок</span></div>
      <div class="stat"><b id="sBub">30</b><span>пузырьков</span></div>
      <div class="stat"><b id="sGrowth">100</b><span>средняя масса %</span></div>
    </div>
    <canvas id="spark" width="280" height="42"></canvas>
    <p class="tele" id="tele">камера — · азимут —</p>
  </section>

  <section class="panel legend reveal" style="--d:.28s">
    <h2 class="ph"><span>Каталог окрасов</span><i>8</i></h2>
    <ul id="legend"></ul>
  </section>

  <footer class="hints reveal" style="--d:.36s">
    <span><b>ЛКМ</b> вращать</span><span><b>ПКМ</b> панорама</span><span><b>колесо</b> зум</span>
    <span><b>клик по воде</b> бросить корм</span><span><b>клик по рыбе</b> вспугнуть</span>
  </footer>
</div>

<div id="boot"><div class="boot-in">
  <h3>Аквариум</h3>
  <div class="boot-log" id="blog"></div>
  <div class="bar"><i id="bbar"></i></div>
</div></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function(){
'use strict';
/* ═══════════ boot-лог ═══════════ */
const blog=document.getElementById('blog'), bbar=document.getElementById('bbar');
const lines=['инициализация рендера ······ ok','резервуар 36 × 24 × 20 ··· ok','субстрат и валуны ······· ok','посадка валлиснерии ····· ok','запуск популяции (15) ··· ok'];
lines.forEach((t,i)=>{const d=document.createElement('div');d.textContent=t;d.style.animationDelay=(i*.16+.05)+'s';blog.appendChild(d);});

if(typeof THREE==='undefined'){
  blog.innerHTML='<div style="color:#ff8a6b">не удалось загрузить three.js — проверьте соединение</div>';
  return;
}

/* ═══════════ константы ═══════════ */
const TANK={w:36,h:24,d:20};
const B={x:TANK.w/2-2.8,yMin:1.4,yMax:TANK.h-2.8,z:TANK.d/2-2.6};
const MAX_FISH=60;
const rnd=(a,b)=>a+Math.random()*(b-a);
const clamp=(v,a,b)=>v<a?a:v>b?b:v;

/* ═══════════ сцена ═══════════ */
const canvas=document.getElementById('scene');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.08;

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0x052434,0.0135);

const camera=new THREE.PerspectiveCamera(52,innerWidth/innerHeight,0.1,400);
camera.position.set(27,16,33);

const controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.target.set(0,9,0);
controls.enableDamping=true; controls.dampingFactor=.055;
controls.minDistance=10; controls.maxDistance=60;
controls.maxPolarAngle=Math.PI/1.8;
controls.rotateSpeed=.7; controls.panSpeed=.6;

/* ═══════════ свет ═══════════ */
const amb=new THREE.AmbientLight(0x404040,.4); scene.add(amb);
const hemi=new THREE.HemisphereLight(0x9fdcff,0x0a2233,.38); scene.add(hemi);

const sun=new THREE.DirectionalLight(0xdff3ff,1.55);
sun.position.set(16,42,20); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-28; sun.shadow.camera.right=28;
sun.shadow.camera.top=28; sun.shadow.camera.bottom=-28;
sun.shadow.camera.near=1; sun.shadow.camera.far=120;
sun.shadow.bias=-0.0006; sun.shadow.radius=2;
scene.add(sun);

const under1=new THREE.PointLight(0x39c2ff,1.15,72); under1.position.set(-13,6,7); scene.add(under1);
const under2=new THREE.PointLight(0x2f7bff,1.0,72);  under2.position.set(14,4,-7);  scene.add(under2);

let lightOn=true, sunTarget=1.55, ambTarget=.4, underTarget=1.15;

/* ═══════════ резервуар ═══════════ */
const tankG=new THREE.Group(); scene.add(tankG);

// стекло
const glass=new THREE.Mesh(
  new THREE.BoxGeometry(TANK.w,TANK.h,TANK.d),
  new THREE.MeshPhysicalMaterial({color:0xbfeeff,transparent:true,opacity:.10,roughness:.05,metalness:0,
    transmission:.95,thickness:1.2,clearcoat:1,clearcoatRoughness:.05,side:THREE.DoubleSide,depthWrite:false})
);
glass.position.y=TANK.h/2; tankG.add(glass);

// рёбра
const edges=new THREE.LineSegments(new THREE.EdgesGeometry(glass.geometry),
  new THREE.LineBasicMaterial({color:0x9beaff,transparent:true,opacity:.5}));
edges.position.copy(glass.position); tankG.add(edges);

// металлическая рама + постамент
const metal=new THREE.MeshStandardMaterial({color:0x2b3d48,metalness:.92,roughness:.34});
const beamY=[[TANK.w+.5,.5,.6,0,0],[.6,.5,TANK.d+.5,0,0]];
[[0,TANK.h],[0,0]].forEach(([_,y])=>{
  [-1,1].forEach(s=>{
    const a=new THREE.Mesh(new THREE.BoxGeometry(TANK.w+.6,.55,.62),metal); a.position.set(0,y,s*(TANK.d/2+.02)); a.castShadow=true; tankG.add(a);
    const b=new THREE.Mesh(new THREE.BoxGeometry(.62,.55,TANK.d+.6),metal); b.position.set(s*(TANK.w/2+.02),y,0); b.castShadow=true; tankG.add(b);
  });
});
[-1,1].forEach(sx=>[-1,1].forEach(sz=>{
  const p=new THREE.Mesh(new THREE.BoxGeometry(.62,TANK.h,.62),metal);
  p.position.set(sx*(TANK.w/2+.02),TANK.h/2,sz*(TANK.d/2+.02)); p.castShadow=true; tankG.add(p);
}));
const plinth=new THREE.Mesh(new THREE.BoxGeometry(TANK.w+5,2.4,TANK.d+5),
  new THREE.MeshStandardMaterial({color:0x131f27,metalness:.35,roughness:.75}));
plinth.position.y=-1.25; plinth.receiveShadow=true; plinth.castShadow=true; tankG.add(plinth);

// текстура песка
function sandTex(){
  const c=document.createElement('canvas'); c.width=c.height=512; const g=c.getContext('2d');
  g.fillStyle='#d9c193'; g.fillRect(0,0,512,512);
  for(let i=0;i<240;i++){const x=Math.random()*512,y=Math.random()*512,r=18+Math.random()*70;
    const gr=g.createRadialGradient(x,y,0,x,y,r),d=Math.random()>.5;
    gr.addColorStop(0,d?'rgba(118,92,58,.16)':'rgba(255,244,214,.16)'); gr.addColorStop(1,'rgba(0,0,0,0)');
    g.fillStyle=gr; g.fillRect(x-r,y-r,r*2,r*2);}
  for(let i=0;i<26000;i++){const x=Math.random()*512,y=Math.random()*512,r=Math.random()*1.3+.2,l=(185+Math.random()*70)|0;
    g.fillStyle='rgba('+l+','+((l*.87)|0)+','+((l*.62)|0)+','+(.1+Math.random()*.35).toFixed(2)+')';
    g.beginPath(); g.arc(x,y,r,0,6.283); g.fill();}
  const t=new THREE.CanvasTexture(c);
  t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(4,2.4); t.anisotropy=4; t.encoding=THREE.sRGBEncoding;
  return t;
}
const hSand=(x,z)=>Math.sin(x*.34)*Math.cos(z*.41)*.42+Math.sin(x*.86+1.3)*Math.cos(z*.63-.7)*.2+Math.sin(x*1.9)*.06;
const sandG=new THREE.PlaneGeometry(TANK.w,TANK.d,72,44);
{ const p=sandG.attributes.position;
  for(let i=0;i<p.count;i++) p.setZ(i,hSand(p.getX(i),p.getY(i)));
  p.needsUpdate=true; sandG.computeVertexNormals(); }
const sand=new THREE.Mesh(sandG,new THREE.MeshStandardMaterial({map:sandTex(),color:0xf0dfc0,roughness:.95,metalness:0}));
sand.rotation.x=-Math.PI/2; sand.receiveShadow=true; tankG.add(sand);

// валуны
const rockMat=new THREE.MeshStandardMaterial({color:0x6d7068,roughness:.92,metalness:.05,flatShading:true});
for(let i=0;i<8;i++){
  const r=rnd(1.1,2.4), g=new THREE.DodecahedronGeometry(r,0);
  const p=g.attributes.position;
  for(let k=0;k<p.count;k++) p.setXYZ(k,p.getX(k)*rnd(.76,1.2),p.getY(k)*rnd(.6,.95),p.getZ(k)*rnd(.76,1.2));
  g.computeVertexNormals();
  const m=new THREE.Mesh(g,rockMat.clone());
  m.material.color.offsetHSL(rnd(-.04,.04),0,rnd(-.1,.1));
  const x=rnd(-B.x+1,B.x-1), z=rnd(-B.z+1,B.z-1);
  m.position.set(x,hSand(x,-z)-.25+r*.35,z);
  m.rotation.set(rnd(0,6.28),rnd(0,6.28),rnd(0,6.28));
  m.castShadow=true; m.receiveShadow=true; tankG.add(m);
}

// водоросли
const plants=[];
for(let i=0;i<12;i++){
  const bush=new THREE.Group();
  const bx=rnd(-B.x-1,B.x+1), bz=rnd(-B.z-.5,B.z+.5);
  bush.position.set(clamp(bx,-TANK.w/2+1.5,TANK.w/2-1.5),0,clamp(bz,-TANK.d/2+1,TANK.d/2-1));
  const blades=3+((Math.random()*4)|0), hue=rnd(.24,.44);
  for(let b=0;b<blades;b++){
    const h=rnd(5,13.5), lean=rnd(-1.9,1.9), pts=[];
    for(let s=0;s<=5;s++){const t=s/5;
      pts.push(new THREE.Vector3(Math.sin(t*2.1+b)*lean*t*.75+t*lean*.4, h*t, Math.cos(t*1.7+b*1.3)*lean*t*.5));}
    const curve=new THREE.CatmullRomCurve3(pts);
    const mat=new THREE.MeshStandardMaterial({
      color:new THREE.Color().setHSL(hue,rnd(.42,.7),rnd(.24,.42)),roughness:.72,metalness:0,
      side:THREE.DoubleSide,transparent:true,opacity:.95});
    const blade=new THREE.Mesh(new THREE.TubeGeometry(curve,18,rnd(.09,.16),6,false),mat);
    blade.scale.x=.34; blade.castShadow=true; bush.add(blade);
  }
  bush.userData={phase:rnd(0,6.28),amp:rnd(.05,.11)};
  plants.push(bush); tankG.add(bush);
}

// поверхность воды
const surfG=new THREE.PlaneGeometry(TANK.w,TANK.d,34,20);
const surfBase=surfG.attributes.position.array.slice();
const surf=new THREE.Mesh(surfG,new THREE.MeshPhysicalMaterial({
  color:0x8fdcf5,transparent:true,opacity:.26,roughness:.12,metalness:0,clearcoat:1,
  side:THREE.DoubleSide,depthWrite:false}));
surf.rotation.x=-Math.PI/2; surf.position.y=TANK.h-1.1; tankG.add(surf);

// световые лучи
function rayTex(){
  const c=document.createElement('canvas'); c.width=128;c.height=512; const g=c.getContext('2d');
  const gr=g.createLinearGradient(0,0,0,512);
  gr.addColorStop(0,'rgba(255,255,255,.55)'); gr.addColorStop(.55,'rgba(200,240,255,.16)'); gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr; g.fillRect(0,0,128,512);
  g.globalCompositeOperation='destination-in';
  const h=g.createLinearGradient(0,0,128,0);
  h.addColorStop(0,'rgba(0,0,0,0)'); h.addColorStop(.5,'rgba(0,0,0,1)'); h.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=h; g.fillRect(0,0,128,512);
  return new THREE.CanvasTexture(c);
}
const rTex=rayTex();
for(let i=0;i<4;i++){
  const p=new THREE.Mesh(new THREE.PlaneGeometry(rnd(6,11),22),
    new THREE.MeshBasicMaterial({map:rTex,transparent:true,opacity:.09,blending:THREE.AdditiveBlending,
      depthWrite:false,side:THREE.DoubleSide}));
  p.position.set(rnd(-13,13),TANK.h-11,rnd(-7,7)); p.rotation.z=rnd(-.22,.22);
  p.userData={ph:rnd(0,6.28)}; scene.add(p); rays.push(p);
}
var rays=window.__rays||[];

// взвесь
const dustN=340, dPos=new Float32Array(dustN*3);
for(let i=0;i<dustN;i++){dPos[i*3]=rnd(-B.x,B.x);dPos[i*3+1]=rnd(0,TANK.h-1.5);dPos[i*3+2]=rnd(-B.z,B.z);}
const dGeo=new THREE.BufferGeometry(); dGeo.setAttribute('position',new THREE.BufferAttribute(dPos,3));
const dust=new THREE.Points(dGeo,new THREE.PointsMaterial({size:.1,color:0xbfefff,transparent:true,opacity:.5,depthWrite:false}));
scene.add(dust);

/* ═══════════ окрасы ═══════════ */
const SCHEMES=[
  {n:'Оранжевая',   base:'#ff7a1f',dark:'#8f3a05',light:'#ffd9a3',fin:'#ffb265',accent:'#fff0d6'},
  {n:'Синяя',       base:'#2f66ff',dark:'#0a1f7a',light:'#b4dcff',fin:'#7fb2ff',accent:'#e2f0ff'},
  {n:'Жёлто-красная',base:'#ffd21e',dark:'#c0392b',light:'#fff3b0',fin:'#ff8a3d',accent:'#ffffff'},
  {n:'Фиолетовая',  base:'#8f46ff',dark:'#3d1170',light:'#dcc0ff',fin:'#b48cff',accent:'#f3e8ff'},
  {n:'Красная',     base:'#e0204a',dark:'#6d0a20',light:'#ffa9bb',fin:'#ff6c86',accent:'#ffe3e9'},
  {n:'Зелёная',     base:'#1fc079',dark:'#08543a',light:'#bdf5d6',fin:'#66dfa8',accent:'#eafff4'},
  {n:'Розовая',     base:'#ff5fb0',dark:'#7d1450',light:'#ffd9ec',fin:'#ff95ca',accent:'#fff0f8'},
  {n:'Золотая',     base:'#ffb300',dark:'#7a4b00',light:'#fff0bd',fin:'#ffd166',accent:'#fffbe8'}
];
const PATTERNS=['bands','spots','saddle','sheen'];

function fishTexture(s,pat){
  const c=document.createElement('canvas'); c.width=256;c.height=128; const g=c.getContext('2d');
  const gr=g.createLinearGradient(0,0,0,128);
  gr.addColorStop(0,s.dark); gr.addColorStop(.28,s.base); gr.addColorStop(.68,s.base); gr.addColorStop(1,s.light);
  g.fillStyle=gr; g.fillRect(0,0,256,128);
  if(pat==='bands'){
    for(let i=0;i<4;i++){const x=26+i*60+rnd(-8,8), w=rnd(13,24);
      g.fillStyle='rgba(255,255,255,.72)'; g.beginPath();
      for(let y=0;y<=128;y+=8){const off=Math.sin(y*.06+i)*5; g.lineTo(x+off+(y/128-.5)*4,y);}
      for(let y=128;y>=0;y-=8){const off=Math.sin(y*.06+i)*5; g.lineTo(x+w+off+(y/128-.5)*4,y);}
      g.closePath(); g.fill();
      g.fillStyle='rgba(20,16,30,.22)'; g.fillRect(x+w,0,5,128);}
  } else if(pat==='spots'){
    for(let i=0;i<46;i++){const x=Math.random()*256,y=Math.random()*128,r=rnd(2.5,8);
      g.fillStyle=Math.random()>.35?'rgba(255,255,255,.4)':'rgba(20,10,30,.28)';
      g.beginPath(); g.ellipse(x,y,r,r*.8,0,0,6.283); g.fill();}
  } else if(pat==='saddle'){
    for(let i=0;i<7;i++){const x=i*36+rnd(-6,6);
      g.fillStyle='rgba(15,10,25,.4)'; g.beginPath();
      g.ellipse(x,18+rnd(-4,6),rnd(12,22),rnd(14,26),0,0,6.283); g.fill();}
    for(let i=0;i<20;i++){g.fillStyle='rgba(255,255,255,.3)';
      g.beginPath(); g.arc(Math.random()*256,rnd(50,120),rnd(1.5,4),0,6.283); g.fill();}
  } else {
    const sh=g.createLinearGradient(0,44,0,74);
    sh.addColorStop(0,'rgba(255,255,255,0)'); sh.addColorStop(.5,'rgba(226,248,255,.62)'); sh.addColorStop(1,'rgba(255,255,255,0)');
    g.fillStyle=sh; g.fillRect(0,40,256,40);
    for(let i=0;i<9;i++){g.fillStyle='rgba(12,8,24,.22)'; g.fillRect(i*29+rnd(-4,4),0,4,128);}
  }
  // чешуйчатый микрорисунок
  g.globalAlpha=.09;
  for(let y=6;y<128;y+=7){for(let x=0;x<256;x+=9){
    g.strokeStyle='#000'; g.lineWidth=1; g.beginPath(); g.arc(x+(y%14?4:0),y,4.4,0,3.2); g.stroke();}}
  g.globalAlpha=1;
  const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding; t.anisotropy=4;
  return t;
}

/* ═══════════ геометрия плавников ═══════════ */
function caudalGeo(){
  const s=new THREE.Shape();
  s.moveTo(0,.2);
  s.bezierCurveTo(.45,.34,.78,.66,1.04,.96);
  s.bezierCurveTo(.84,.44,.72,.18,.6,0);
  s.bezierCurveTo(.72,-.18,.84,-.44,1.04,-.96);
  s.bezierCurveTo(.78,-.66,.45,-.34,0,-.2);
  return new THREE.ShapeGeometry(s,14);
}
function dorsalGeo(){
  const s=new THREE.Shape();
  s.moveTo(0,0);
  s.bezierCurveTo(.3,.52,.72,.62,1.1,.1);
  s.lineTo(1.1,0); s.closePath();
  return new THREE.ShapeGeometry(s,12);
}
function pectoralGeo(){
  const s=new THREE.Shape();
  s.moveTo(0,.06);
  s.quadraticCurveTo(.45,.24,.9,-.02);
  s.quadraticCurveTo(.5,-.34,0,-.16);
  s.closePath();
  return new THREE.ShapeGeometry(s,10);
}
const G={body:new THREE.SphereGeometry(1,28,20), caudal:caudalGeo(), dorsal:dorsalGeo(), pect:pectoralGeo(),
  eye:new THREE.SphereGeometry(.2,14,12), pupil:new THREE.SphereGeometry(.115,12,10),
  glint:new THREE.SphereGeometry(.045,8,6), mouth:new THREE.SphereGeometry(.16,12,10)};

/* ═══════════ рыба ═══════════ */
const fishArray=[];
function createFish(schemeIdx){
  const si=schemeIdx!=null?schemeIdx:(Math.random()*SCHEMES.length)|0;
  const s=SCHEMES[si], pat=PATTERNS[(Math.random()*PATTERNS.length)|0];

  const bodyMat=new THREE.MeshPhysicalMaterial({map:fishTexture(s,pat),roughness:.36,metalness:.08,
    clearcoat:.7,clearcoatRoughness:.25,emissive:new THREE.Color(s.accent),emissiveIntensity:0});
  const finMat=new THREE.MeshPhysicalMaterial({color:new THREE.Color(s.fin),transparent:true,opacity:.82,
    roughness:.4,metalness:.02,side:THREE.DoubleSide,clearcoat:.5,
    emissive:new THREE.Color(s.accent),emissiveIntensity:0});

  const g=new THREE.Group(), body=new THREE.Group(); g.add(body);

  const trunk=new THREE.Mesh(G.body,bodyMat);
  trunk.scale.set(.56,.8,1.32); trunk.castShadow=true; body.add(trunk);

  const tailP=new THREE.Object3D(); tailP.position.z=-1.24; body.add(tailP);
  const tail=new THREE.Mesh(G.caudal,finMat); tail.rotation.y=Math.PI/2; tail.scale.setScalar(.86);
  tail.castShadow=true; tailP.add(tail);

  const dorP=new THREE.Object3D(); dorP.position.set(0,.6,-.12); body.add(dorP);
  const dorsal=new THREE.Mesh(G.dorsal,finMat); dorsal.rotation.y=Math.PI/2; dorsal.scale.setScalar(.72);
  dorsal.castShadow=true; dorP.add(dorsal);

  const mkFin=(side)=>{
    const p=new THREE.Object3D(); p.position.set(side*.42,-.06,.5); body.add(p);
    const m=new THREE.Mesh(G.pect,finMat); m.rotation.x=-Math.PI/2+.42; m.scale.set(side*1,.9,.9);
    p.add(m); return p;
  };
  const finL=mkFin(1), finR=mkFin(-1);

  [1,-1].forEach(side=>{
    const e=new THREE.Group(); e.position.set(side*.3,.17,.78); body.add(e);
    const w=new THREE.Mesh(G.eye,new THREE.MeshPhysicalMaterial({color:0xf7fdff,roughness:.15,clearcoat:1}));
    e.add(w);
    const p=new THREE.Mesh(G.pupil,new THREE.MeshStandardMaterial({color:0x08060c,roughness:.2}));
    p.position.set(side*.09,.02,.14); e.add(p);
    const gl=new THREE.Mesh(G.glint,new THREE.MeshBasicMaterial({color:0xffffff}));
    gl.position.set(side*.14,.1,.18); e.add(gl);
  });
  const mouth=new THREE.Mesh(G.mouth,new THREE.MeshStandardMaterial({color:new THREE.Color(s.dark),roughness:.6}));
  mouth.position.set(0,-.12,1.16); mouth.scale.set(.9,.6,.5); body.add(mouth);

  const sc=rnd(.6,1.2);
  const f={mesh:g,body:body,tail:tail,tailP,dorsal,dorP,finL,finR,
    velocity:new THREE.Vector3(rnd(-1,1),rnd(-.3,.3),rnd(-1,1)).normalize(),
    speed:rnd(2.5,5.2), tailSpeed:rnd(4.2,8.4), phase:rnd(0,6.28),
    targetFood:null, avoidanceRadius:rnd(2.6,4.4),
    scale:sc, baseScale:1.25, startle:0, roll:0, spawnT:0, highlight:false,
    scheme:si, mats:[bodyMat,finMat], wander:new THREE.Vector3(), wanderT:0};
  g.scale.setScalar(.001);
  g.position.set(rnd(-B.x,B.x),rnd(4,TANK.h-5),rnd(-B.z,B.z));
  scene.add(g); fishArray.push(f);
  return f;
}
for(let i=0;i<15;i++) createFish(i%8);

/* ═══════════ пузыри ═══════════ */
const bubbles=[];
const bubGeo=new THREE.SphereGeometry(1,12,10);
const bubMat=new THREE.MeshPhysicalMaterial({color:0xffffff,transparent:true,opacity:.24,roughness:.02,
  metalness:0,clearcoat:1,clearcoatRoughness:0,depthWrite:false});
function addBubble(n){
  for(let i=0;i<n;i++){
    const m=new THREE.Mesh(bubGeo,bubMat);
    const r=rnd(.1,.34); m.scale.setScalar(r);
    m.position.set(rnd(-B.x,B.x),rnd(0,TANK.h-2),rnd(-B.z,B.z));
    m.userData={r,sp:rnd(1.6,4.2),ph:rnd(0,6.28),amp:rnd(.25,1.1)};
    scene.add(m); bubbles.push(m);
  }
}
addBubble(30);

/* ═══════════ корм ═══════════ */
const foods=[];
const foodGeo=new THREE.DodecahedronGeometry(.24,0);
const foodMat=new THREE.MeshStandardMaterial({color:0xc8641e,roughness:.85,emissive:0x3a1200,emissiveIntensity:.4});
function addFood(x,y,z){
  const m=new THREE.Mesh(foodGeo,foodMat);
  m.position.set(clamp(x,-B.x,B.x),clamp(y,1,TANK.h-1.4),clamp(z,-B.z,B.z));
  m.scale.setScalar(rnd(.75,1.35)); m.castShadow=true;
  m.rotation.set(rnd(0,6.3),rnd(0,6.3),rnd(0,6.3));
  m.userData={vel:new THREE.Vector3(rnd(-.5,.5),rnd(-.2,.4),rnd(-.5,.5)),rest:0};
  scene.add(m); foods.push(m);
  return m;
}

/* ═══════════ клики ═══════════ */
const ray=new THREE.Raycaster(), ndc=new THREE.Vector2();
const clickPlane=new THREE.Plane();
const dummy=new THREE.Object3D();
let downX=0,downY=0,downT=0,hoverFish=null;

function pick(ev,inTank){
  ndc.x=(ev.clientX/innerWidth)*2-1; ndc.y=-(ev.clientY/innerHeight)*2+1;
  ray.setFromCamera(ndc,camera);
}
function fishAt(ev){
  pick(ev);
  const bodies=[];
  for(const f of fishArray){ bodies.push(f.body.children[0]); }
  const hits=ray.intersectObjects(bodies,false);
  if(!hits.length) return null;
  return fishArray.find(f=>f.body.children[0]===hits[0].object)||null;
}
function pointInTank(ev){
  pick(ev);
  const n=new THREE.Vector3(); camera.getWorldDirection(n);
  clickPlane.setFromNormalAndCoplanarPoint(n,controls.target);
  const p=new THREE.Vector3();
  if(!ray.ray.intersectPlane(clickPlane,p)) return null;
  return {x:clamp(p.x,-B.x+.5,B.x-.5), y:clamp(p.y,B.yMin+.5,TANK.h-1.6), z:clamp(p.z,-B.z+.5,B.z-.5)};
}
renderer.domElement.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;downT=performance.now();});
renderer.domElement.addEventListener('pointerup',e=>{
  if(Math.hypot(e.clientX-downX,e.clientY-downY)>7||performance.now()-downT>420) return;
  const f=fishAt(e);
  if(f){ f.startle=1.6; toast(e.clientX,e.clientY,'вспугнута'); burst(f.mesh.position,6); return; }
  const p=pointInTank(e);
  if(p){ for(let i=0;i<2;i++) addFood(p.x+rnd(-1.4,1.4),Math.max(p.y,TANK.h-4)+rnd(0,2),p.z+rnd(-1.4,1.4));
    burst(new THREE.Vector3(p.x,TANK.h-1.4,p.z),4); }
});
renderer.domElement.addEventListener('pointermove',(e)=>{
  if(e.buttons){ canvas.style.cursor='grabbing'; return; }
  hoverFish=fishAt(e); canvas.style.cursor=hoverFish?'pointer':'grab';
});

function toast(x,y,txt){
  const d=document.createElement('div'); d.className='toast'; d.textContent=txt;
  d.style.left=x+'px'; d.style.top=y+'px'; document.body.appendChild(d);
  setTimeout(()=>d.remove(),1000);
}
const burstPool=[];
function burst(pos,n){
  for(let i=0;i<n;i++){
    const m=new THREE.Mesh(bubGeo,bubMat); m.scale.setScalar(rnd(.07,.15));
    m.position.copy(pos);
    m.userData.v=new THREE.Vector3(rnd(-1,1),rnd(.6,2.2),rnd(-1,1));
    m.userData.life=1; scene.add(m); burstPool.push(m);
  }
}

/* ═══════════ UI ═══════════ */
const el=id=>document.getElementById(id);
const legendUl=el('legend'), counts=new Array(8).fill(0);
SCHEMES.forEach((s,i)=>{
  const li=document.createElement('li');
  li.innerHTML='<span class="sw" style="background:linear-gradient(100deg,'+s.dark+','+s.base+' 45%,'+s.light+')"></span>'+s.n+'<em>0</em>';
  li.addEventListener('mouseenter',()=>fishArray.forEach(f=>{if(f.scheme===i)f.highlight=true;}));
  li.addEventListener('mouseleave',()=>fishArray.forEach(f=>f.highlight=false));
  li.addEventListener('click',()=>{const f=createFish(i); counts[i]++; toast(innerWidth-140,120,'+ '+s.n.toLowerCase());});
  legendUl.appendChild(li);
});
function refreshLegend(){
  counts.fill(0); fishArray.forEach(f=>counts[f.scheme]++);
  [...legendUl.children].forEach((li,i)=>{li.querySelector('em').textContent=counts[i];
    li.style.opacity=counts[i]?1:.45;});
}

el('btnFish').onclick=()=>{ if(fishArray.length<MAX_FISH) createFish(); refreshLegend(); };
el('btnBub').onclick=()=>addBubble(10);
el('btnFeed').onclick=()=>{ for(let i=0;i<5;i++) addFood(rnd(-B.x,B.x),TANK.h-2.2+rnd(-.6,.6),rnd(-B.z,B.z)); };
el('btnLight').onclick=e=>{
  lightOn=!lightOn;
  sunTarget=lightOn?1.55:.1; ambTarget=lightOn?.4:.16; underTarget=lightOn?1.15:2.3;
  e.currentTarget.classList.toggle('is-off',!lightOn);
  document.documentElement.classList.toggle('night',!lightOn);
};
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k==='f') el('btnFish').click();
  if(k==='b') el('btnBub').click();
  if(k==='l') el('btnLight').click();
  if(e.code==='Space'){e.preventDefault(); el('btnFeed').click();}
});

/* FPS sparkline */
const sc=el('spark'), sg=sc.getContext('2d'), hist=new Array(64).fill(60);
function drawSpark(){
  const w=sc.width=sc.clientWidth*2, h=sc.height=84;
  sg.clearRect(0,0,w,h);
  sg.strokeStyle='rgba(140,220,245,.16)'; sg.lineWidth=2;
  sg.beginPath(); sg.moveTo(0,h*.5); sg.lineTo(w,h*.5); sg.stroke();
  const bw=w/hist.length;
  for(let i=0;i<hist.length;i++){
    const v=Math.min(hist[i],75)/75, bh=v*h*.92, x=i*bw;
    const g=sg.createLinearGradient(0,h-bh,0,h);
    g.addColorStop(0,'#5fe9ff'); g.addColorStop(1,'rgba(95,233,255,.08)');
    sg.fillStyle=g; sg.fillRect(x,h-bh,Math.max(bw-2.5,1.5),bh);
  }
}

/* ═══════════ цикл ═══════════ */
let last=performance.now(), acc=0, frames=0, fpsT=0, uiT=0;
const v1=new THREE.Vector3(), v2=new THREE.Vector3(), v3=new THREE.Vector3(), prevDir=new THREE.Vector3();

function tick(now){
  requestAnimationFrame(tick);
  const dt=Math.min((now-last)/1000,.05); last=now; const t=now/1000;

  /* свет */
  sun.intensity+=(sunTarget-sun.intensity)*Math.min(1,dt*3);
  amb.intensity+=(ambTarget-amb.intensity)*Math.min(1,dt*3);
  under1.intensity+=(underTarget-under1.intensity)*Math.min(1,dt*3);
  under2.intensity+=(underTarget*.85-under2.intensity)*Math.min(1,dt*3);

  /* вода */
  { const p=surfG.attributes.position;
    for(let i=0;i<p.count;i++){
      const x=surfBase[i*3], y=surfBase[i*3+1];
      p.setZ(i,Math.sin(x*.55+t*1.7)*.16+Math.cos(y*.7-t*1.2)*.13);
    } p.needsUpdate=true; surf.geometry.computeVertexNormals(); }
  surf.material.opacity=.2+(lightOn?.08:.02)+Math.sin(t*.9)*.03;

  /* растения */
  for(const b of plants){
    b.rotation.x=Math.sin(t*.7+b.userData.phase)*b.userData.amp;
    b.rotation.z=Math.cos(t*.55+b.userData.phase*1.4)*b.userData.amp*1.15;
  }
  /* взвесь */
  { const p=dGeo.attributes.position;
    for(let i=0;i<dustN;i++){
      let y=p.getY(i)+dt*.28; if(y>TANK.h-1.5) y=.3;
      p.setY(i,y); p.setX(i,p.getX(i)+Math.sin(t*.5+i)*dt*.09);
    } p.needsUpdate=true; }

  /* пузыри */
  for(const b of bubbles){
    const u=b.userData;
    b.position.y+=u.sp*dt;
    b.position.x+=Math.sin(t*1.6+u.ph)*u.amp*dt*2.2;
    b.position.z+=Math.cos(t*1.25+u.ph)*u.amp*dt*2.2;
    b.scale.setScalar(u.r*(1+Math.sin(t*3+u.ph)*.06));
    if(b.position.y>TANK.h-1.4){ b.position.set(rnd(-B.x,B.x),.4,rnd(-B.z,B.z)); }
  }
  for(let i=burstPool.length-1;i>=0;i--){
    const m=burstPool[i], u=m.userData;
    u.life-=dt*1.4; m.position.addScaledVector(u.v,dt); u.v.y+=dt*1.2;
    m.scale.multiplyScalar(1-dt*.6);
    if(u.life<=0){scene.remove(m); burstPool.splice(i,1);}
  }

  /* корм */
  for(let i=foods.length-1;i>=0;i--){
    const f=foods[i], u=f.userData;
    if(f.position.y>1.05){
      u.vel.y-=4.2*dt; u.vel.multiplyScalar(1-1.1*dt);
      f.position.addScaledVector(u.vel,dt);
      f.rotation.x+=dt*1.6; f.rotation.y+=dt*1.1;
    } else {
      f.position.y=Math.max(f.position.y,hSand(f.position.x,-f.position.z)+.2);
      u.rest+=dt;
      if(u.rest>7){ f.material=f.material; f.scale.multiplyScalar(1-dt*.5); }
      if(u.rest>9.5){ scene.remove(f); foods.splice(i,1); continue; }
    }
    if(f.position.y<=B.yMin+.05 && !u.settled){ u.settled=true; burst(f.position,2); }
  }

  /* рыбы */
  for(const f of fishArray){
    if(f.spawnT<1){ f.spawnT=Math.min(1,f.spawnT+dt*1.6); }
    const ease=1-Math.pow(1-f.spawnT,3);
    f.mesh.scale.setScalar(f.scale*f.baseScale*(0.15+0.85*ease));

    const steer=v1.set(0,0,0);
    const spd=f.speed*(1+f.startle*1.9);

    // цель — корм
    f.targetFood=null;
    let best=225; // 15^2
    for(const fo of foods){
      const d2=fo.position.distanceToSquared(f.mesh.position);
      if(d2<best){best=d2;f.targetFood=fo;}
    }
    if(f.targetFood){
      v2.copy(f.targetFood.position).sub(f.mesh.position);
      const dist=v2.length();
      steer.addScaledVector(v2.normalize(),spd*1.5);
      if(dist<1.0+f.scale*.7){
        scene.remove(f.targetFood); foods.splice(foods.indexOf(f.targetFood),1);
        f.scale=Math.min(2.3,f.scale*1.05);
        f.startle=Math.max(f.startle,.35);
        burst(f.mesh.position,4);
        const pv=f.mesh.position.clone().project(camera);
        toast((pv.x*.5+.5)*innerWidth,(-pv.y*.5+.5)*innerHeight,'масса +5%');
        f.targetFood=null;
      }
    } else {
      // блуждание
      f.wanderT-=dt;
      if(f.wanderT<=0){ f.wanderT=rnd(1.4,3.6);
        f.wander.set(rnd(-1,1),rnd(-.45,.45),rnd(-1,1)).multiplyScalar(spd*.55); }
      steer.add(f.wander);
      // мягкая волна по глубине
      steer.y+=Math.sin(t*.6+f.phase)*.5;
    }

    // избегание
    for(const o of fishArray){
      if(o===f) continue;
      const d2=o.mesh.position.distanceToSquared(f.mesh.position);
      const r=f.avoidanceRadius*(1+f.scale*.25);
      if(d2<r*r && d2>.0001){
        v3.copy(f.mesh.position).sub(o.mesh.position);
        steer.addScaledVector(v3.normalize(),(r-Math.sqrt(d2))*spd*1.5);
      }
    }

    // стенки
    const m=3.4, p=f.mesh.position;
    if(p.x> B.x-m) steer.x-=(p.x-(B.x-m))*spd*1.1;
    if(p.x<-B.x+m) steer.x+=(B.x-m-p.x)*spd*1.1;
    if(p.z> B.z-m) steer.z-=(p.z-(B.z-m))*spd*1.1;
    if(p.z<-B.z+m) steer.z+=(B.z-m-p.z)*spd*1.1;
    if(p.y> B.yMax-m) steer.y-=(p.y-(B.yMax-m))*spd*1.2;
    if(p.y< B.yMin+m) steer.y+=(B.yMin+m-p.y)*spd*1.2;

    // интегрирование
    prevDir.copy(f.velocity);
    f.velocity.addScaledVector(steer,dt);
    const len=f.velocity.length();
    const maxS=spd, minS=spd*.45;
    if(len>maxS) f.velocity.multiplyScalar(maxS/len);
    else if(len<minS&&len>.001) f.velocity.multiplyScalar(minS/len);
    p.addScaledVector(f.velocity,dt);
    p.x=clamp(p.x,-B.x,B.x); p.z=clamp(p.z,-B.z,B.z); p.y=clamp(p.y,B.yMin,B.yMax);

    // ориентация + крен
    dummy.position.copy(p); dummy.lookAt(v2.copy(p).add(f.velocity));
    f.mesh.quaternion.slerp(dummy.quaternion,1-Math.exp(-dt*5.5));
    const cross=prevDir.x*f.velocity.z-prevDir.z*f.velocity.x;
    f.roll+=(clamp(-cross*1.6,-.55,.55)-f.roll)*Math.min(1,dt*4);
    f.body.rotation.z=f.roll;
    f.body.rotation.y=Math.sin(t*.9+f.phase)*.05;

    // анимация плавников
    const ts=f.tailSpeed*(1+f.startle*1.6)*(0.6+len/(spd+0.001)*.6);
    f.tailP.rotation.y=Math.sin(t*ts+f.phase)*.52;
    f.dorP.rotation.z=Math.sin(t*ts*.7+f.phase+.8)*.14;
    const flap=Math.sin(t*ts*.85+f.phase)*.34+.16;
    f.finL.rotation.z=flap*.9; f.finL.rotation.y=-.25+flap*.3;
    f.finR.rotation.z=-flap*.9; f.finR.rotation.y=.25-flap*.3;

    f.startle=Math.max(0,f.startle-dt*1.1);
    const hl=(f.highlight||f===hoverFish)?.7:0;
    for(const mt of f.mats) mt.emissiveIntensity+=(hl-mt.emissiveIntensity)*Math.min(1,dt*6);
  }

  controls.update();
  renderer.render(scene,camera);

  /* телеметрия */
  frames++; acc+=dt; fpsT+=dt; uiT+=dt;
  if(fpsT>=.4){ const fps=Math.round(frames/fpsT); hist.push(fps); hist.shift();
    el('sFps').textContent=fps; drawSpark(); frames=0; fpsT=0; }
  if(uiT>=.35){ uiT=0;
    el('sFish').textContent=fishArray.length;
    el('sFood').textContent=foods.length;
    el('sBub').textContent=bubbles.length;
    let g=0; for(const f of fishArray) g+=f.scale;
    el('sGrowth').textContent=fishArray.length?Math.round(g/fishArray.length/0.9*100):100;
    const d=camera.position.distanceTo(controls.target);
    const az=Math.round((Math.atan2(camera.position.x-controls.target.x,camera.position.z-controls.target.z)*57.2958+360)%360);
    el('tele').textContent='камера '+d.toFixed(1)+' ед · азимут '+az+'° · глубина '+(TANK.h-controls.target.y).toFixed(1);
  }
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight); drawSpark();
});

/* старт */
let bp=0;
const bootTimer=setInterval(()=>{
  bp+=rnd(9,20); bbar.style.width=Math.min(bp,100)+'%';
  if(bp>=100){clearInterval(bootTimer);
    setTimeout(()=>document.getElementById('boot').classList.add('done'),260);}
},110);
refreshLegend(); drawSpark(); requestAnimationFrame(tick);
})();
</script>
</body>
</html>
```

**Что внутри, помимо ТЗ:**

- **Процедурный окрас вместо однотонных рыб** — canvas-текстуры 256×128 с четырьмя типами узора (полосы-«клоуны», пятна, «сёдла», радужный бок) + чешуйчатый микрорисунок; плавники полупрозрачные, глаза с роговицей, зрачком и бликом.
- **Анатомия вместо «вращай хвостом»**: хвостовой/спинной/грудные плавники на отдельных пивотах, рыбка кренится (`roll`) в повороте через cross-product скоростей, инерционный `slerp` квaternиона.
- **Живое поведение**: поиск ближайшего корма (радиус 15²), репульсия соседей, мягкий отбой у стенок, дрейф по глубине, эффект «вспугнутости» по клику на рыбу — рывок + кольцо пузырей.
- **Среда**: стекло в металлической раме с постаментом, анимированная поверхность воды, god-ray лучи, взвесь (340 частиц), каустика и зерно поверх кадра, «ночной» режим с биолюминесцентным свечением.
- **HUD как приборная таблица**: Bodoni Moda + IBM Plex Mono/Sans, FPS-спарклайн, телеметрия камеры, каталог окрасов — наведение подсвечивает нужных рыб в баке (emissive-пульс), клик заселяет особь этого цвета.
- **Обратная связь**: всплывающие метки «масса +5%» прямо над рыбой в экранных координатах, различение клика и драга OrbitControls, горячие клавиши F / B / L / Space.