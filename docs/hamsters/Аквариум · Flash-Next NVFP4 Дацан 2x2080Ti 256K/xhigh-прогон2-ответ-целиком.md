# 🐠 3D Аквариум — живой симулятор на Three.js

Собрал полноценную сцену в одном файле: процедурные рыбы (8 окрасов × паттерны на canvas-текстурах), ИИ стаи, каустика на дне, день/ночь и автокормушка.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>АКВАРИУМ · интерактивный 3D симулятор</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@300;400;700;800&family=Manrope:wght@400;500;600;800&display=swap" rel="stylesheet">
<style>
/* ============================================================
   ПАЛИТРА / БАЗА
   ============================================================ */
:root{
  --abyss:#02121a;
  --deep:#06293a;
  --ink:#eaf9fd;
  --muted:#7fa9ba;
  --aqua:#5ff0dc;
  --glow:#7fe9ff;
  --coral:#ff7a4d;
  --sand:#f2dba9;
  --panel:rgba(5,31,44,.66);
  --panel-2:rgba(5,31,44,.5);
  --line:rgba(120,225,235,.20);
  --shadow:0 24px 60px -22px rgba(0,0,0,.85);
  --ease:cubic-bezier(.22,.9,.28,1);
}
*{box-sizing:border-box}
html,body{height:100%;margin:0;overflow:hidden;background:var(--abyss);color:var(--ink);
  font-family:'Manrope',system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
body.night{--aqua:#8fb6ff;--glow:#a9c8ff;--line:rgba(140,170,255,.22);--panel:rgba(6,14,34,.66)}
#stage{position:fixed;inset:0;z-index:0}
#stage canvas{display:block;width:100%;height:100%;cursor:crosshair;touch-action:none}

/* атмосферные слои поверх рендера */
.vignette,.beam{position:fixed;inset:0;pointer-events:none;z-index:2}
.vignette{background:
  radial-gradient(120% 90% at 50% 8%,rgba(140,255,246,.10),transparent 55%),
  radial-gradient(140% 120% at 50% 120%,rgba(0,0,0,.62),transparent 60%)}
.beam{background:linear-gradient(103deg,transparent 30%,rgba(150,255,250,.055) 44%,transparent 58%);
  mix-blend-mode:screen;animation:sweep 17s var(--ease) infinite}
@keyframes sweep{0%,100%{transform:translateX(-14%) skewX(-6deg);opacity:.5}50%{transform:translateX(12%) skewX(4deg);opacity:1}}

/* ============================================================
   ПАНЕЛИ HUD
   ============================================================ */
.panel{position:fixed;z-index:10;background:var(--panel);border:1px solid var(--line);
  backdrop-filter:blur(16px) saturate(1.35);-webkit-backdrop-filter:blur(16px) saturate(1.35);
  box-shadow:var(--shadow),inset 0 1px 0 rgba(255,255,255,.07);padding:20px;
  transition:background .6s var(--ease),border-color .6s var(--ease),transform .5s var(--ease);
  animation:rise .9s var(--ease) both}
.panel::before,.panel::after{content:"";position:absolute;width:14px;height:14px;border:1.5px solid var(--aqua);opacity:.75}
.panel::before{top:-1px;left:-1px;border-right:0;border-bottom:0}
.panel::after{bottom:-1px;right:-1px;border-left:0;border-top:0}
@keyframes rise{from{opacity:0;transform:translateY(-14px) scale(.985)}to{opacity:1;transform:none}}
.panel--tl{top:22px;left:22px;width:min(340px,calc(100vw - 44px));animation-delay:.05s}
.panel--tr{top:22px;right:22px;width:min(246px,calc(100vw - 44px));animation-delay:.18s}
body.ui-hidden .panel,body.ui-hidden .dock,body.ui-hidden .credit{opacity:0;pointer-events:none;transform:translateY(-10px)}

/* бренд */
.eyebrow{display:flex;align-items:center;gap:8px;font-size:9.5px;letter-spacing:.28em;text-transform:uppercase;
  color:var(--muted);font-weight:700;margin-bottom:10px}
.eyebrow i{width:6px;height:6px;border-radius:50%;background:var(--coral);box-shadow:0 0 12px var(--coral);
  animation:pulse 2.4s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.7)}}
h1{font-family:'Unbounded',sans-serif;font-weight:800;font-size:clamp(34px,4.2vw,46px);line-height:.86;
  letter-spacing:-.045em;margin:0 0 12px}
h1 span{display:block;font-weight:300;color:transparent;-webkit-text-stroke:1.2px var(--aqua);
  letter-spacing:.02em;font-size:.86em;transition:-webkit-text-stroke-color .6s}
.lead{font-size:12.5px;line-height:1.55;color:#b9dbe6;margin:0}
.rule{height:1px;background:linear-gradient(90deg,var(--line),transparent);margin:16px 0}

/* инструкции */
.keys{list-style:none;margin:0;padding:0;display:grid;gap:7px}
.keys li{display:flex;align-items:center;gap:10px;font-size:11.5px;color:#a6cdd9}
.k{font-family:'Unbounded',sans-serif;font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--glow);border:1px solid var(--line);padding:4px 7px;min-width:96px;text-align:center;
  background:rgba(127,233,255,.05);transition:.3s var(--ease)}
.keys li:hover .k{background:rgba(127,233,255,.16);border-color:var(--aqua);transform:translateX(2px)}

/* кнопки */
.acts{display:grid;gap:8px;margin-top:18px}
.btn{position:relative;display:flex;align-items:center;gap:10px;width:100%;padding:11px 13px;cursor:pointer;
  font-family:'Manrope',sans-serif;font-size:12px;font-weight:700;letter-spacing:.02em;color:var(--ink);
  background:linear-gradient(100deg,rgba(95,240,220,.13),rgba(95,240,220,.03));
  border:1px solid rgba(95,240,220,.28);overflow:hidden;transition:.35s var(--ease);text-align:left}
.btn svg{width:15px;height:15px;flex:none;stroke:var(--aqua);fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;transition:.35s var(--ease)}
.btn kbd{margin-left:auto;font-family:'Unbounded',sans-serif;font-size:8.5px;opacity:.5;border:1px solid var(--line);padding:2px 5px}
.btn::after{content:"";position:absolute;inset:0;background:linear-gradient(100deg,transparent 35%,rgba(255,255,255,.28) 50%,transparent 65%);
  transform:translateX(-120%);transition:transform .7s var(--ease)}
.btn:hover{transform:translateY(-2px);border-color:var(--aqua);background:linear-gradient(100deg,rgba(95,240,220,.26),rgba(95,240,220,.06));
  box-shadow:0 10px 26px -12px rgba(95,240,220,.6)}
.btn:hover::after{transform:translateX(120%)}
.btn:hover svg{transform:scale(1.15) rotate(-6deg)}
.btn:active{transform:translateY(0) scale(.985)}
.btn--alt{background:linear-gradient(100deg,rgba(255,122,77,.14),rgba(255,122,77,.03));border-color:rgba(255,122,77,.3)}
.btn--alt svg{stroke:var(--coral)}
.btn--alt:hover{border-color:var(--coral);background:linear-gradient(100deg,rgba(255,122,77,.28),rgba(255,122,77,.06));box-shadow:0 10px 26px -12px rgba(255,122,77,.6)}
.btn.on{background:linear-gradient(100deg,rgba(95,240,220,.34),rgba(95,240,220,.1));border-color:var(--aqua);box-shadow:inset 0 0 22px rgba(95,240,220,.18)}

/* статистика */
.stats{display:grid;grid-template-columns:1fr 1fr;gap:14px 10px}
.stat b{display:block;font-family:'Unbounded',sans-serif;font-weight:700;font-size:26px;line-height:1;
  letter-spacing:-.03em;font-variant-numeric:tabular-nums;transition:color .3s,transform .3s}
.stat i{display:block;font-style:normal;font-size:8.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);margin-top:5px}
.stat.bump b{color:var(--aqua);transform:scale(1.14)}
#spark{width:100%;height:30px;display:block;margin-top:14px;opacity:.85}
.mini{font-family:'Unbounded',sans-serif;font-size:9px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;
  color:var(--muted);margin:0 0 10px}
.legend{list-style:none;margin:0;padding:0;display:grid;gap:5px}
.legend li{display:flex;align-items:center;gap:9px;font-size:10.5px;color:#9dc4d2;cursor:default;transition:.25s var(--ease)}
.legend li:hover{color:var(--ink);transform:translateX(3px)}
.legend s{width:16px;height:16px;flex:none;text-decoration:none;border-radius:2px;transform:rotate(45deg);
  box-shadow:0 0 0 1px rgba(255,255,255,.18),0 4px 10px -4px #000;transition:.35s var(--ease)}
.legend li:hover s{transform:rotate(0deg) scale(1.25)}
.legend em{margin-left:auto;font-style:normal;font-size:9px;opacity:.5;font-variant-numeric:tabular-nums}

/* нижняя подсказка + кредит */
.dock{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:10;display:flex;align-items:center;gap:12px;
  padding:9px 16px;background:var(--panel-2);border:1px solid var(--line);backdrop-filter:blur(14px);
  font-size:11.5px;color:#c3e4ee;white-space:nowrap;animation:rise .9s .3s var(--ease) both;transition:.5s var(--ease)}
.dock .dot{width:7px;height:7px;border-radius:50%;background:var(--aqua);box-shadow:0 0 0 0 rgba(95,240,220,.6);animation:ring 2s infinite}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(95,240,220,.55)}70%{box-shadow:0 0 0 11px rgba(95,240,220,0)}100%{box-shadow:0 0 0 0 rgba(95,240,220,0)}}
.dock b{font-family:'Unbounded',sans-serif;font-weight:700;font-size:10px;letter-spacing:.08em;color:var(--aqua)}
.credit{position:fixed;right:22px;bottom:22px;z-index:10;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;
  color:rgba(160,200,215,.45);animation:rise .9s .4s var(--ease) both;transition:.5s}
#uiToggle{position:fixed;left:22px;bottom:22px;z-index:11;width:38px;height:38px;display:grid;place-items:center;cursor:pointer;
  background:var(--panel);border:1px solid var(--line);color:var(--aqua);backdrop-filter:blur(14px);transition:.3s var(--ease)}
#uiToggle:hover{background:rgba(95,240,220,.18);transform:translateY(-2px)}
#toast{position:fixed;left:50%;bottom:76px;transform:translate(-50%,14px);z-index:12;padding:9px 18px;
  background:rgba(2,18,26,.9);border:1px solid var(--aqua);font-family:'Unbounded',sans-serif;font-size:10px;
  font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--aqua);opacity:0;pointer-events:none;
  transition:.45s var(--ease)}
#toast.show{opacity:1;transform:translate(-50%,0)}
.ripple{position:fixed;z-index:9;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;border:1.5px solid var(--aqua);
  pointer-events:none;animation:rip .75s var(--ease) forwards}
@keyframes rip{from{transform:scale(.4);opacity:.95}to{transform:scale(7);opacity:0}}

/* загрузка */
#loader{position:fixed;inset:0;z-index:30;display:grid;place-content:center;justify-items:center;gap:20px;
  background:radial-gradient(circle at 50% 40%,#0a3446,#02101a 70%);transition:opacity .8s ease,visibility .8s}
#loader.gone{opacity:0;visibility:hidden}
#loader h2{font-family:'Unbounded',sans-serif;font-weight:300;font-size:15px;letter-spacing:.5em;
  text-transform:uppercase;color:#9fe6f5;margin:0;text-indent:.5em}
.tank-fill{width:180px;height:44px;border:1px solid rgba(127,233,255,.35);position:relative;overflow:hidden}
.tank-fill span{position:absolute;left:0;bottom:0;height:0;width:100%;
  background:linear-gradient(180deg,rgba(95,240,220,.85),rgba(20,120,150,.6));animation:fill 1.5s .2s var(--ease) forwards}
.tank-fill::after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 17px,rgba(127,233,255,.14) 17px 18px)}
@keyframes fill{to{height:76%}}

@media (max-width:900px){
  .panel--tl{width:calc(100vw - 32px);top:auto;bottom:78px;left:16px;padding:15px}
  .panel--tr{top:16px;right:16px;left:16px;width:auto}
  .keys,.legend,.lead,#spark{display:none}
  h1{font-size:26px}
  .stat b{font-size:20px}
  .dock{bottom:14px;font-size:10px;padding:7px 12px}
  #uiToggle{bottom:14px;left:14px}
  .credit{display:none}
}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
</head>
<body>

<div id="stage"></div>
<div class="beam" aria-hidden="true"></div>
<div class="vignette" aria-hidden="true"></div>

<!-- ЛЕВАЯ ПАНЕЛЬ -->
<header class="panel panel--tl" id="panelL">
  <div class="eyebrow"><i></i>симулятор · three.js r128</div>
  <h1>АКВА<span>РИУМ</span></h1>
  <p class="lead">Живая экосистема за стеклом: процедурные тропические рыбы, поведенческий ИИ, каустика на дне и настоящий рост.</p>
  <div class="rule"></div>
  <ul class="keys">
    <li><span class="k">ЛКМ + тяга</span> орбита камеры</li>
    <li><span class="k">ПКМ + тяга</span> панорамирование</li>
    <li><span class="k">Колесо</span> зум 10 → 60</li>
    <li><span class="k">Клик по воде</span> бросить корм</li>
  </ul>
  <div class="acts">
    <button class="btn" data-act="fish">
      <svg viewBox="0 0 24 24"><path d="M3 12c3-5 8-6 11-4 2-1 4-2 7-2-1 3-1 5-2 6-1 2-1 4-5 4-3 2-8 1-11-4Z"/><circle cx="8" cy="11" r=".9" fill="currentColor"/></svg>
      Добавить рыбку <kbd>F</kbd></button>
    <button class="btn" data-act="bubbles">
      <svg viewBox="0 0 24 24"><circle cx="9" cy="15" r="4"/><circle cx="16" cy="8" r="2.6"/><circle cx="17.5" cy="15.5" r="1.4"/></svg>
      Больше пузырей <kbd>B</kbd></button>
    <button class="btn btn--alt" data-act="light">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.4M12 19.6V22M2 12h2.4M19.6 12H22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7"/></svg>
      <span class="lbl">Ночной свет</span> <kbd>L</kbd></button>
    <button class="btn" data-act="feeder">
      <svg viewBox="0 0 24 24"><path d="M12 3v7"/><path d="M6.5 13.5a5.5 5.5 0 0 1 11 0"/><circle cx="12" cy="18.5" r="1.6"/></svg>
      <span class="lbl">Автокорм</span> <kbd>A</kbd></button>
  </div>
</header>

<!-- ПРАВАЯ ПАНЕЛЬ -->
<aside class="panel panel--tr" id="panelR">
  <div class="eyebrow"><i></i>телеметрия</div>
  <div class="stats">
    <div class="stat" id="cFish"><b>15</b><i>рыбок</i></div>
    <div class="stat" id="cBub"><b>30</b><i>пузырьков</i></div>
    <div class="stat" id="cFood"><b>0</b><i>корм</i></div>
    <div class="stat" id="cFps"><b>60</b><i>fps</i></div>
  </div>
  <canvas id="spark"></canvas>
  <div class="rule"></div>
  <h2 class="mini">окраски</h2>
  <ul class="legend" id="legend"></ul>
</aside>

<div class="dock"><span class="dot"></span><b>КОРМЛЕНИЕ</b> кликните по воде — рыбы найдут корм за секунды</div>
<div class="credit">процедурная генерация · 36×24×20</div>
<button id="uiToggle" title="Скрыть интерфейс (H)">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="2.6"/></svg>
</button>
<div id="toast"></div>

<div id="loader"><h2>наполняем</h2><div class="tank-fill"><span></span></div></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function(){
'use strict';
if(!window.THREE){document.getElementById('loader').innerHTML='<h2>не удалось загрузить three.js</h2>';return;}

/* ============================================================
   1. КОНФИГУРАЦИЯ
   ============================================================ */
const TANK={w:36,h:24,d:20};
const H={x:TANK.w/2,y:TANK.h/2,z:TANK.d/2};
const SAND_Y=-11.15;
const BOUND={x:H.x-2.4,z:H.z-2.4,yTop:H.y-2.2,yBot:SAND_Y+1.5};
const START_FISH=15, START_BUB=30, MAX_FISH=34, FOOD_R=15;

const PALETTES=[
  {name:'Оранжевая',   base:'#ff7f22',dark:'#a83f08',accent:'#fff2df',pat:['stripes','stripes','gradient'], metal:.1,rough:.4},
  {name:'Синяя',       base:'#2a63e8',dark:'#0a2059',accent:'#ffd23f',pat:['lateral','gradient','spots'],   metal:.2,rough:.35},
  {name:'Жёлто-красная',base:'#ffc11a',dark:'#c0330b',accent:'#ff5a2b',pat:['twoTone','gradient','spots'],   metal:.15,rough:.4},
  {name:'Фиолетовая',  base:'#8b5cf6',dark:'#3d1d78',accent:'#f3c8ff',pat:['stripes','spots','gradient'],    metal:.25,rough:.3},
  {name:'Красная',     base:'#e03030',dark:'#6d0d14',accent:'#ffdcc4',pat:['gradient','spots','lateral'],    metal:.15,rough:.38},
  {name:'Зелёная',     base:'#3ec46d',dark:'#0e5a2d',accent:'#dcffb2',pat:['spots','lateral','twoTone'],     metal:.1,rough:.45},
  {name:'Розовая',     base:'#ff6ba4',dark:'#96204f',accent:'#fff0f6',pat:['stripes','twoTone','gradient'],  metal:.2,rough:.32},
  {name:'Золотая',     base:'#ffb703',dark:'#8d5c00',accent:'#fff3b0',pat:['gradient','twoTone','spots'],    metal:.65,rough:.2}
];

/* ============================================================
   2. РЕНДЕР / СЦЕНА / КАМЕРА
   ============================================================ */
const stage=document.getElementById('stage');
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
renderer.setSize(innerWidth,innerHeight);
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.12;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
stage.appendChild(renderer.domElement);
const MAXA=renderer.capabilities.getMaxAnisotropy();

const scene=new THREE.Scene();
const FOG_DAY=new THREE.Color('#0d4a63'), FOG_NIGHT=new THREE.Color('#071a33');
scene.fog=new THREE.FogExp2(FOG_DAY.clone(),0.0135);

const camera=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,.1,500);
camera.position.set(4,7,46);

const controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.055;
controls.minDistance=10; controls.maxDistance=60;
controls.maxPolarAngle=Math.PI/1.8; controls.minPolarAngle=.08;
controls.target.set(0,-1.5,0);
controls.autoRotateSpeed=.35;
controls.enablePan=true; controls.screenSpacePanning=true;

/* ============================================================
   3. ФОН (ГРАДИЕНТ) + СВЕТ
   ============================================================ */
const bgU={uMix:{value:1}};
scene.add(new THREE.Mesh(
  new THREE.SphereGeometry(230,32,16),
  new THREE.ShaderMaterial({
    side:THREE.BackSide,depthWrite:false,fog:false,uniforms:bgU,
    vertexShader:`varying vec3 vP;void main(){vP=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`varying vec3 vP;uniform float uMix;
      void main(){float h=clamp(vP.y/230.*.5+.5,0.,1.);
        vec3 dA=vec3(.006,.055,.086),dB=vec3(.035,.29,.39);
        vec3 nA=vec3(.004,.02,.05),nB=vec3(.03,.07,.22);
        vec3 c=mix(mix(nA,nB,h),mix(dA,dB,h),uMix);
        float g=fract(sin(dot(vP.xy,vec2(12.9898,78.233)))*43758.5453);
        gl_FragColor=vec4(c+g*.012,1.);}`
  })
));

const amb=new THREE.AmbientLight(0x404040,.4); scene.add(amb);
const hemi=new THREE.HemisphereLight(0xa6e8ff,0x0b2b34,.5); scene.add(hemi);
const sun=new THREE.DirectionalLight(0xfff1dc,1.25);
sun.position.set(17,34,15); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
const sc=sun.shadow.camera; sc.left=-28;sc.right=28;sc.top=24;sc.bottom=-24;sc.near=1;sc.far=110;
sun.shadow.bias=-.0008; sun.shadow.radius=3; scene.add(sun);
const pl1=new THREE.PointLight(0x35c8ff,1.6,52,2); pl1.position.set(-13,-6,6); scene.add(pl1);
const pl2=new THREE.PointLight(0x2a6bff,1.3,54,2); pl2.position.set(14,-7,-5); scene.add(pl2);

/* ============================================================
   4. АКВАРИУМ: СТЕКЛО, РАМА, ДНО
   ============================================================ */
const tank=new THREE.Group(); scene.add(tank);

const glass=new THREE.Mesh(new THREE.BoxGeometry(TANK.w,TANK.h,TANK.d),
  new THREE.MeshPhysicalMaterial({color:0xbfeeff,metalness:0,roughness:.04,transparent:true,opacity:.115,
    side:THREE.DoubleSide,depthWrite:false,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1}));
glass.renderOrder=6; tank.add(glass);
tank.add(new THREE.LineSegments(new THREE.EdgesGeometry(glass.geometry),
  new THREE.LineBasicMaterial({color:0x8ff0ff,transparent:true,opacity:.34})));

// металлическая рама
const frameMat=new THREE.MeshStandardMaterial({color:0x9fb6c1,metalness:.85,roughness:.34});
function bar(x,y,z,sx,sy,sz){const m=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),frameMat);
  m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;tank.add(m);}
[H.x,-H.x].forEach(x=>[H.z,-H.z].forEach(z=>bar(x,0,z,.55,TANK.h+.4,.55)));
[H.y,-H.y].forEach(y=>{bar(0,y,H.z,TANK.w+.7,.5,.5);bar(0,y,-H.z,TANK.w+.7,.5,.5);
  bar(H.x,y,0,.5,.5,TANK.d+.7);bar(-H.x,y,0,.5,.5,TANK.d+.7);});

// пол под аквариумом
const floor=new THREE.Mesh(new THREE.CircleGeometry(120,48),
  new THREE.MeshStandardMaterial({color:0x06222e,roughness:.92,metalness:0}));
floor.rotation.x=-Math.PI/2; floor.position.y=-H.y-.35; floor.receiveShadow=true; scene.add(floor);

// песчаное дно с процедурным рельефом + vertex colors
const sandGeo=new THREE.PlaneGeometry(TANK.w,TANK.d,96,64);
{ const p=sandGeo.attributes.position, col=[];
  const c1=new THREE.Color('#e7cf9d'),c2=new THREE.Color('#b99a68'),c3=new THREE.Color('#f5e6c2');
  for(let i=0;i<p.count;i++){
    const x=p.getX(i),y=p.getY(i);
    let h=Math.sin(x*.34)*Math.cos(y*.42)*.34+Math.sin(x*1.05+y*.72)*.16+Math.sin(x*2.4-y*1.8)*.07;
    const dw=Math.min(H.x-Math.abs(x),H.z-Math.abs(y));
    if(dw<3.2) h+=(3.2-dw)*.34;
    p.setZ(i,h);
    const t=THREE.MathUtils.clamp(.5+h*.9+Math.sin(x*7.1+y*3.3)*.08,0,1);
    const c=t<.5?c2.clone().lerp(c1,t*2):c1.clone().lerp(c3,(t-.5)*2);
    col.push(c.r,c.g,c.b);
  }
  sandGeo.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  sandGeo.computeVertexNormals();
}
const sand=new THREE.Mesh(sandGeo,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.98,metalness:0}));
sand.rotation.x=-Math.PI/2; sand.position.y=SAND_Y; sand.receiveShadow=true; tank.add(sand);

// КАУСТИКА на дне (аддитивный шейдер)
const causticU={uTime:{value:0},uStrength:{value:1},uColor:{value:new THREE.Color('#9ff3ff')}};
const caustic=new THREE.Mesh(new THREE.PlaneGeometry(TANK.w,TANK.d),
  new THREE.ShaderMaterial({
    transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:causticU,
    vertexShader:`varying vec2 vU;void main(){vU=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`varying vec2 vU;uniform float uTime,uStrength;uniform vec3 uColor;
      void main(){vec2 p=(vU-.5)*vec2(9.,6.);float t=uTime*.5;float c=1.;float in_=0.0055;
        for(int n=0;n<3;n++){float tt=t*(1.-(3.5/float(n+1)));
          vec2 i=p+vec2(cos(tt-p.y)+sin(tt+p.x),sin(tt-p.y)+cos(tt+p.x));
          c+=1./length(vec2(p.x/(sin(i.x+tt)/in_),p.y/(cos(i.y+tt)/in_)));}
        c/=3.;c=1.17-pow(max(c,0.),1.4);
        float g=pow(abs(c),8.);
        vec2 e=smoothstep(0.,.14,vU)*smoothstep(0.,.14,1.-vU);
        gl_FragColor=vec4(uColor*g*uStrength,clamp(g,0.,1.)*.85*e.x*e.y);}`
  }));
caustic.rotation.x=-Math.PI/2; caustic.position.y=SAND_Y+.09; caustic.renderOrder=3; tank.add(caustic);

// поверхность воды
const surfU={uTime:{value:0}};
const surface=new THREE.Mesh(new THREE.PlaneGeometry(TANK.w,TANK.d,1,1),
  new THREE.ShaderMaterial({
    transparent:true,depthWrite:false,side:THREE.DoubleSide,uniforms:surfU,
    vertexShader:`varying vec2 vU;varying vec3 vW;void main(){vU=uv;vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader:`varying vec2 vU;varying vec3 vW;uniform float uTime;
      void main(){vec3 v=normalize(cameraPosition-vW);
        float f=pow(1.-abs(dot(v,vec3(0.,1.,0.))),2.6);
        float r=sin(vU.x*72.+uTime*1.7)*sin(vU.y*58.-uTime*1.2);
        vec3 c=mix(vec3(.03,.24,.32),vec3(.62,.98,1.),clamp(f*.85+r*.06+.06,0.,1.));
        gl_FragColor=vec4(c,.26+f*.5);}`
  }));
surface.rotation.x=Math.PI/2; surface.position.y=H.y-.45; surface.renderOrder=5; tank.add(surface);

/* ---- камни ---- */
const rockMat=new THREE.MeshStandardMaterial({color:0x6d7a80,roughness:.9,metalness:.05,flatShading:true});
for(let i=0;i<8;i++){
  const r=1+Math.random()*1.5, g=new THREE.DodecahedronGeometry(r,0), p=g.attributes.position;
  for(let j=0;j<p.count;j++) p.setXYZ(j,p.getX(j)*(.78+Math.random()*.46),p.getY(j)*(.62+Math.random()*.4),p.getZ(j)*(.78+Math.random()*.46));
  g.computeVertexNormals();
  const m=new THREE.Mesh(g,rockMat.clone());
  m.material.color.offsetHSL(Math.random()*.06-.03,0,(Math.random()*.16-.08));
  const a=Math.random()*Math.PI*2, rad=3+Math.random()*13;
  m.position.set(Math.cos(a)*rad,SAND_Y+r*.42,Math.sin(a)*rad*.55);
  m.rotation.set(Math.random()*3,Math.random()*6,Math.random()*3);
  m.castShadow=true;m.receiveShadow=true;tank.add(m);
}
// мелкая галька
const pebG=new THREE.IcosahedronGeometry(.3,0);
for(let i=0;i<26;i++){
  const m=new THREE.Mesh(pebG,rockMat);
  const a=Math.random()*Math.PI*2,rad=2+Math.random()*15;
  m.position.set(Math.cos(a)*rad,SAND_Y+.1,Math.sin(a)*rad*.55);
  m.scale.setScalar(.5+Math.random()*1.2);m.rotation.set(Math.random()*3,Math.random()*3,Math.random()*3);
  m.castShadow=true;m.receiveShadow=true;tank.add(m);
}

/* ---- водоросли (TubeGeometry + CatmullRomCurve3) ---- */
const plants=[];
function makePlant(x,z){
  const g=new THREE.Group(); g.position.set(x,SAND_Y-.1,z);
  const blades=3+Math.floor(Math.random()*4), hue=.26+Math.random()*.22;
  for(let b=0;b<blades;b++){
    const hgt=3.4+Math.random()*6.4, lean=(Math.random()-.5)*2.6, pts=[];
    for(let j=0;j<=5;j++){const t=j/5;
      pts.push(new THREE.Vector3(Math.sin(t*2.4+b)*lean*t,.1+t*hgt,Math.cos(t*1.7+b*1.3)*lean*.55*t));}
    const curve=new THREE.CatmullRomCurve3(pts),tub=14,rad=6,r=.17;
    const geo=new THREE.TubeGeometry(curve,tub,r,rad,false),p=geo.attributes.position,cv=new THREE.Vector3();
    for(let j=0;j<=tub;j++){curve.getPointAt(j/tub,cv);const s=Math.max(.1,1-.88*(j/tub));
      for(let k=0;k<=rad;k++){const i=j*(rad+1)+k;
        cv.sub(new THREE.Vector3(p.getX(i),p.getY(i),p.getZ(i))).multiplyScalar(s).add(new THREE.Vector3(p.getX(i),p.getY(i),p.getZ(i)));
        p.setXYZ(i,cv.x,cv.y,cv.z);}}
    geo.computeVertexNormals();
    const m=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({
      color:new THREE.Color().setHSL(hue,.62,.28+Math.random()*.14),roughness:.78,
      side:THREE.DoubleSide,emissive:new THREE.Color().setHSL(hue,.7,.07)}));
    if(b===0)m.castShadow=true; g.add(m);
  }
  tank.add(g);
  plants.push({g,ph:Math.random()*6.28,sp:.5+Math.random()*.5,a:.05+Math.random()*.05});
}
for(let i=0;i<12;i++){
  const a=(i/12)*Math.PI*2+Math.random()*.5;
  makePlant(Math.cos(a)*(6+Math.random()*9),Math.sin(a)*(3+Math.random()*5.5));
}

/* ---- планктон ---- */
const MOTES=700, mp=new Float32Array(MOTES*3), ms=new Float32Array(MOTES);
for(let i=0;i<MOTES;i++){mp[i*3]=(Math.random()-.5)*TANK.w;mp[i*3+1]=SAND_Y+Math.random()*TANK.h;
  mp[i*3+2]=(Math.random()-.5)*TANK.d;ms[i]=Math.random();}
const moteGeo=new THREE.BufferGeometry();
moteGeo.setAttribute('position',new THREE.BufferAttribute(mp,3));
const motes=new THREE.Points(moteGeo,new THREE.PointsMaterial({color:0xa9f0ff,size:.14,transparent:true,
  opacity:.55,depthWrite:false,blending:THREE.AdditiveBlending,sizeAttenuation:true}));
tank.add(motes);

/* ============================================================
   5. ПУЗЫРИ
   ============================================================ */
const bubGeo=new THREE.SphereGeometry(1,12,10);
const bubMat=new THREE.MeshPhysicalMaterial({color:0xdffaff,metalness:0,roughness:0,transparent:true,
  opacity:.34,clearcoat:1,clearcoatRoughness:0,depthWrite:false});
const bubbles=[];
function addBubble(n){
  for(let i=0;i<n;i++){
    const m=new THREE.Mesh(bubGeo,bubMat);
    const s=.09+Math.random()*.24; m.scale.setScalar(s);
    const emitter=Math.random()<.45?[-11+Math.random()*1.2,-H.z+3]:[8+Math.random()*1.2,H.z-4];
    const b={m,sp:.9+Math.random()*1.5,w:.4+Math.random()*1.3,ph:Math.random()*6.28,
      ex:Array.isArray(emitter)?emitter[0]:0,ez:Array.isArray(emitter)?emitter[1]:0};
    m.position.set(b.ex+(Math.random()-.5)*.7,SAND_Y+Math.random()*(TANK.h-1),b.ez+(Math.random()-.5)*.7);
    tank.add(m); bubbles.push(b);
  }
}
addBubble(START_BUB);

/* ============================================================
   6. РЫБЫ: КОЖА + АНАТОМИЯ
   ============================================================ */
const skinCache={};
function skin(pal,pat){
  const key=pal.name+pat; if(skinCache[key])return skinCache[key];
  const W=512,Hg=256,c=document.createElement('canvas');c.width=W;c.height=Hg;const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,0,Hg);
  g.addColorStop(0,pal.dark);g.addColorStop(.34,pal.base);g.addColorStop(.72,pal.base);
  g.addColorStop(.94,mix(pal.base,pal.accent,.75));g.addColorStop(1,'#fdf6e8');
  x.fillStyle=g;x.fillRect(0,0,W,Hg);
  function band(cx,w,col){const gr=x.createLinearGradient(cx-w,0,cx+w,0);
    gr.addColorStop(0,'rgba(0,0,0,0)');gr.addColorStop(.5,col);gr.addColorStop(1,'rgba(0,0,0,0)');
    x.fillStyle=gr;x.fillRect(cx-w,0,w*2,Hg);}
  function mix(a,b,t){const A=new THREE.Color(a),B=new THREE.Color(b);A.lerp(B,t);return '#'+A.getHexString();}
  if(pat==='stripes'){x.globalAlpha=.92;
    [.05,.16,.55,.66].forEach((u,i)=>band(u*W,(i%2?14:24),pal.accent));
    x.globalAlpha=.35;[.30,.80].forEach(u=>band(u*W,9,pal.dark));}
  if(pat==='lateral'){x.globalAlpha=.9;
    const gr=x.createLinearGradient(0,Hg*.42,0,Hg*.6);gr.addColorStop(0,'rgba(0,0,0,0)');
    gr.addColorStop(.5,pal.accent);gr.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=gr;x.fillRect(0,Hg*.4,W,Hg*.22);}
  if(pat==='twoTone'){x.globalAlpha=.85;const gr=x.createLinearGradient(0,Hg*.46,0,Hg*.66);
    gr.addColorStop(0,'rgba(0,0,0,0)');gr.addColorStop(.5,pal.dark);gr.addColorStop(1,'rgba(0,0,0,0)');
    x.fillStyle=gr;x.fillRect(0,Hg*.4,W,Hg*.3);}
  if(pat==='spots'){x.globalAlpha=.55;
    for(let i=0;i<46;i++){const sx=Math.random()*W,sy=Hg*(.18+Math.random()*.55),r=3+Math.random()*9;
      x.fillStyle=Math.random()<.5?pal.accent:pal.dark;x.beginPath();x.ellipse(sx,sy,r,r*.8,0,0,6.28);x.fill();}}
  // чешуя
  x.globalAlpha=.07;x.strokeStyle='#fff';x.lineWidth=1.1;
  for(let r=0;r<14;r++)for(let cI=0;cI<44;cI++){x.beginPath();
    x.arc(cI*12+(r%2?6:0),Hg*.16+r*14,7,.3,Math.PI-.3);x.stroke();}
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;t.wrapS=THREE.RepeatWrapping;t.anisotropy=MAXA;
  skinCache[key]=t;return t;
}
function finShape(len,h,c1,c2){
  const s=new THREE.Shape();s.moveTo(0,0);
  s.bezierCurveTo(len*.35,h*c1,len*.7,h*.9,len,h*c2);
  s.bezierCurveTo(len*.62,-h*.18,len*.32,-h*.3,0,0);
  return s;
}
function tailShape(len,h){
  const s=new THREE.Shape();s.moveTo(0,-.16);s.lineTo(0,.16);
  s.bezierCurveTo(len*.45,h*.34,len*.82,h*.78,len,h);
  s.bezierCurveTo(len*.78,h*.34,len*.66,h*.12,len*.52,0);
  s.bezierCurveTo(len*.66,-h*.12,len*.78,-h*.34,len,-h);
  s.bezierCurveTo(len*.82,-h*.78,len*.45,-h*.34,0,-.16);
  return s;
}
const GEO={
  body:new THREE.SphereGeometry(1,30,20),
  eyeW:new THREE.SphereGeometry(.155,14,10),
  eyeB:new THREE.SphereGeometry(.082,10,8),
  glint:new THREE.SphereGeometry(.032,6,5),
  mouth:new THREE.SphereGeometry(.12,8,6),
  dorsal:new THREE.ShapeGeometry(finShape(1.9,.85,1.15,.25),10),
  ventral:new THREE.ShapeGeometry(finShape(.75,.42,.9,-.4),8),
  pec:new THREE.ShapeGeometry(finShape(.85,.5,1,.35),8),
  tail:new THREE.ShapeGeometry(tailShape(1.35,.95),12)
};
const fishArray=[];

function createFish(palIdx,scale){
  const pal=PALETTES[palIdx===undefined?Math.floor(Math.random()*8):palIdx];
  const pat=pal.pat[Math.floor(Math.random()*pal.pat.length)];
  const G=new THREE.Group();

  const bodyM=new THREE.MeshPhysicalMaterial({map:skin(pal,pat),roughness:pal.rough,metalness:pal.metal,
    clearcoat:.55,clearcoatRoughness:.35,emissive:new THREE.Color(pal.base).multiplyScalar(.05)});
  const body=new THREE.Mesh(GEO.body,bodyM);
  body.scale.set(.46,.8,1.55); body.castShadow=true; G.add(body);

  const finM=new THREE.MeshStandardMaterial({color:new THREE.Color(pal.accent).lerp(new THREE.Color(pal.base),.45),
    transparent:true,opacity:.82,side:THREE.DoubleSide,roughness:.55,
    emissive:new THREE.Color(pal.base).multiplyScalar(.12),depthWrite:false});

  const tailG=new THREE.Group(); tailG.position.z=-1.42;
  const tail=new THREE.Mesh(GEO.tail,finM); tail.rotation.y=Math.PI/2; tail.castShadow=true;
  tailG.add(tail); G.add(tailG);

  const dor=new THREE.Mesh(GEO.dorsal,finM); dor.rotation.y=-Math.PI/2; dor.position.set(0,.6,-.15); G.add(dor);
  const ven=new THREE.Mesh(GEO.ventral,finM); ven.rotation.y=-Math.PI/2; ven.position.set(0,-.58,-.75); G.add(ven);

  const fins=[];
  [1,-1].forEach(s=>{
    const f=new THREE.Mesh(GEO.pec,finM);
    f.position.set(.4*s,-.1,.62);
    f.rotation.set(0,s>0?-.95:-(Math.PI-.95),s*.35);
    G.add(f); fins.push({m:f,base:s*.35,s});
  });
  [1,-1].forEach(s=>{
    const e=new THREE.Group(); e.position.set(.27*s,.16,.98);
    const w=new THREE.Mesh(GEO.eyeW,new THREE.MeshStandardMaterial({color:0xf7fbff,roughness:.14,metalness:0}));
    const b=new THREE.Mesh(GEO.eyeB,new THREE.MeshStandardMaterial({color:0x080d12,roughness:.25,emissive:0x0a1a22}));
    b.position.set(.055*s,0,.12);
    const gl=new THREE.Mesh(GEO.glint,new THREE.MeshBasicMaterial({color:0xffffff}));
    gl.position.set(-.05*s,.06,.17);
    e.add(w,b,gl); G.add(e);
  });
  const mo=new THREE.Mesh(GEO.mouth,new THREE.MeshStandardMaterial({color:new THREE.Color(pal.dark),roughness:.7}));
  mo.position.set(0,-.13,1.46); mo.scale.set(.9,.5,.35); G.add(mo);

  const sc=scale!==undefined?scale:.6+Math.random()*.6;
  G.scale.setScalar(sc);
  G.position.set((Math.random()-.5)*BOUND.x*1.7,(Math.random()-.5)*BOUND.yTop*1.4,(Math.random()-.5)*BOUND.z*1.6);
  tank.add(G);

  const f={mesh:G,finMesh:finM,tail:tailG,pec:fins,body:body,
    vel:new THREE.Vector3(Math.random()-.5,Math.random()*.2,Math.random()-.5).normalize(),
    speed:1.6+Math.random()*1.9, tailSpeed:4+Math.random()*4.5, phase:Math.random()*6.28,
    targetFood:null, avoid:2.4+Math.random()*2.2, scale:sc, targetScale:sc,
    wander:new THREE.Vector3(), wTimer:Math.random()*3, bold:Math.random()*2-1, eaten:0,
    q:new THREE.Quaternion(), bank:0};
  fishArray.push(f); return f;
}
for(let i=0;i<START_FISH;i++) createFish(i%8);

/* ============================================================
   7. КОРМ + ЭФФЕКТЫ
   ============================================================ */
const foodGeo=new THREE.SphereGeometry(.26,8,6);
const foodMat=new THREE.MeshStandardMaterial({color:0xd2662c,roughness:.75,emissive:0x3a1200});
const foods=[];
function addFood(x,z,n){
  n=n||4;
  for(let i=0;i<n;i++){
    const m=new THREE.Mesh(foodGeo,foodMat);
    m.position.set(x+(Math.random()-.5)*1.6,H.y-1.1,z+(Math.random()-.5)*1.6);
    m.scale.setScalar(.7+Math.random()*.7); m.castShadow=true; tank.add(m);
    foods.push({m,vy:-.4-Math.random()*.5,vx:(Math.random()-.5)*.7,vz:(Math.random()-.5)*.7,life:9,set:false});
  }
  bump('cFood');
}
const ringGeo=new THREE.RingGeometry(.36,.58,30);
const rings=[];
for(let i=0;i<12;i++){
  const m=new THREE.Mesh(ringGeo,new THREE.MeshBasicMaterial({color:0xa8fff0,transparent:true,opacity:0,
    blending:THREE.AdditiveBlending,side:THREE.DoubleSide,depthWrite:false}));
  m.rotation.x=-Math.PI/2;m.visible=false;m.renderOrder=4;tank.add(m);rings.push({m,l:0,dur:1});
}
function pop(pos,color,scaleMax){
  const r=rings.find(r=>r.l<=0)||rings[0];
  r.m.position.copy(pos);r.m.position.y+=.12;r.m.visible=true;r.l=1;r.dur=.85;
  r.m.material.color.set(color||0xa8fff0);r.max=scaleMax||2.6;
}

/* ============================================================
   8. ПОВЕДЕНИЕ (ИИ)
   ============================================================ */
const dummy=new THREE.Object3D(), tmpA=new THREE.Vector3(), tmpB=new THREE.Vector3(), sep=new THREE.Vector3();
function pickWander(f){
  f.wander.set((Math.random()-.5)*BOUND.x*1.8,(Math.random()-.4)*BOUND.yTop*1.5,(Math.random()-.5)*BOUND.z*1.8);
  f.wTimer=2.5+Math.random()*4;
}
function updateFish(f,dt,t){
  const p=f.mesh.position, acc=tmpA.set(0,0,0);

  // блуждание
  f.wTimer-=dt; if(f.wTimer<=0) pickWander(f);
  tmpB.subVectors(f.wander,p);
  if(tmpB.length()<3) pickWander(f);
  acc.add(tmpB.normalize().multiplyScalar(.45));

  // избегание соседей + лёгкое согласование
  sep.set(0,0,0); let n=0, ax=0,ay=0,az=0;
  for(let i=0;i<fishArray.length;i++){
    const o=fishArray[i]; if(o===f) continue;
    const d=p.distanceTo(o.mesh.position);
    if(d<f.avoid&&d>1e-4){ tmpB.subVectors(p,o.mesh.position).normalize().multiplyScalar((1-d/f.avoid)/Math.max(d*.35,.3)); sep.add(tmpB); n++; }
    if(d<8){ax+=o.vel.x;ay+=o.vel.y;az+=o.vel.z;}
  }
  if(n) acc.add(sep.multiplyScalar(2.6));
  if(ax||ay||az) acc.add(new THREE.Vector3(ax,ay,az).normalize().multiplyScalar(.14));

  // мягкие стены
  const k=2.6;
  if(p.x>BOUND.x) acc.x-=(p.x-BOUND.x)*k; if(p.x<-BOUND.x) acc.x+=(Math.abs(BOUND.x+p.x))*k;
  if(p.z>BOUND.z) acc.z-=(p.z-BOUND.z)*k; if(p.z<-BOUND.z) acc.z+=(Math.abs(BOUND.z+p.z))*k;
  if(p.y>BOUND.yTop) acc.y-=(p.y-BOUND.yTop)*k; if(p.y<BOUND.yBot) acc.y+=(Math.abs(BOUND.yBot+p.y))*k;

  // корм
  f.targetFood=null; let best=FOOD_R;
  for(let i=0;i<foods.length;i++){
    const fd=foods[i], d=p.distanceTo(fd.m.position);
    if(d<best){best=d;f.targetFood=fd;}
  }
  if(f.targetFood){
    tmpB.subVectors(f.targetFood.m.position,p).normalize(); acc.add(tmpB.multiplyScalar(2.4));
    if(best<1.05*f.scale){ eat(f,f.targetFood); }
  }

  // любопытство к камере
  const dc=p.distanceTo(camera.position);
  if(dc<16&&f.bold>.35&&!f.targetFood){tmpB.subVectors(camera.position,p).normalize();acc.add(tmpB.multiplyScalar(.28*f.bold));}
  else if(dc<7.5&&f.bold<0){tmpB.subVectors(p,camera.position).normalize();acc.add(tmpB.multiplyScalar(1.6));}

  // интегрирование
  f.vel.lerp(acc.normalize().multiplyScalar(f.speed),1-Math.exp(-3.2*dt));
  if(f.vel.length()>f.speed*1.6) f.vel.setLength(f.speed*1.6);
  p.addScaledVector(f.vel,dt);
  p.x=THREE.MathUtils.clamp(p.x,-H.x+.7,H.x-.7);
  p.z=THREE.MathUtils.clamp(p.z,-H.z+.7,H.z-.7);
  p.y=THREE.MathUtils.clamp(p.y,SAND_Y+.45,H.y-.8);

  // ориентация + крен в повороте
  if(f.vel.lengthSq()>1e-6){
    dummy.position.copy(p); dummy.up.set(0,1,0);
    dummy.lookAt(tmpB.copy(p).add(f.vel)); dummy.updateMatrix();
    const target=new THREE.Quaternion().setFromRotationMatrix(dummy.matrix);
    f.mesh.quaternion.slerp(target,1-Math.exp(-5*dt));
  }
  // хвост и плавники
  const sp=f.vel.length()/f.speed;
  const amp=.28+sp*.42;
  f.tail.rotation.y=Math.sin(t*f.tailSpeed+f.phase)*amp;
  f.body.rotation.y=Math.sin(t*f.tailSpeed+f.phase-.9)*amp*.16;
  f.pec.forEach(o=>{o.m.rotation.z=o.base+Math.sin(t*3.4+f.phase)*(0.28*sp+.12)*o.s;});
  // рост / вспышка при поедании
  if(f.scale<f.targetScale){f.scale+=(f.targetScale-f.scale)*Math.min(1,dt*4);f.mesh.scale.setScalar(f.scale);}
  if(f.eaten>0){f.eaten-=dt;f.finMesh.emissive.copy(new THREE.Color(f.flash)).multiplyScalar(.12+f.eaten*.7);}
}
function eat(f,fd){
  const i=foods.indexOf(fd); if(i<0)return;
  foods.splice(i,1); tank.remove(fd.m);
  f.targetScale=Math.min(2.0,f.targetScale*1.05);
  f.eaten=.6; f.flash=f.finMesh.emissive.getHex(); f.speed*=1.01;
  pop(f.mesh.position,0xffe9a8,2.2); bump('cFood');
}

/* ============================================================
   9. ВЗАИМОДЕЙСТВИЕ
   ============================================================ */
const ray=new THREE.Raycaster(), ndc=new THREE.Vector2();
const pickBox=new THREE.Mesh(new THREE.BoxGeometry(TANK.w-1,TANK.h-1,TANK.d-1),
  new THREE.MeshBasicMaterial({visible:false})); tank.add(pickBox);
const surfPlane=new THREE.Plane(new THREE.Vector3(0,1,0),-(H.y-.6));

function feedAt(cx,cy){
  ndc.set((cx/innerWidth)*2-1,-(cy/innerHeight)*2+1);
  ray.setFromCamera(ndc,camera);
  let hit=new THREE.Vector3();
  const pv=new THREE.Vector3();
  if(ray.ray.intersectPlane(surfPlane,pv)&&Math.abs(pv.x)<H.x-1&&Math.abs(pv.z)<H.z-1) hit=pv;
  else{ const its=ray.intersectObject(pickBox,false);
    if(its.length) hit.copy(its[0].point);
    else ray.ray.at(30,hit); }
  hit.x=THREE.MathUtils.clamp(hit.x,-H.x+2,H.x-2);
  hit.z=THREE.MathUtils.clamp(hit.z,-H.z+2,H.z-2);
  addFood(hit.x,hit.z,3+Math.floor(Math.random()*4));
  pop(new THREE.Vector3(hit.x,H.y-.5,hit.z),0x9ff7ff,5.5);
  const d=document.createElement('div');d.className='ripple';
  d.style.left=cx+'px';d.style.top=cy+'px';document.body.appendChild(d);setTimeout(()=>d.remove(),760);
}
let down=null;
renderer.domElement.addEventListener('pointerdown',e=>{down={x:e.clientX,y:e.clientY,t:performance.now()};idle=0;controls.autoRotate=false;});
addEventListener('pointerup',e=>{
  if(!down)return;
  const dx=e.clientX-down.x,dy=e.clientY-down.y;
  if(Math.hypot(dx,dy)<7&&performance.now()-down.t<420) feedAt(e.clientX,e.clientY);
  down=null;
});

/* --- UI --- */
const el=id=>document.getElementById(id);
const toastEl=el('toast'); let tTimer;
function toast(msg){toastEl.textContent=msg;toastEl.classList.add('show');clearTimeout(tTimer);
  tTimer=setTimeout(()=>toastEl.classList.remove('show'),1700);}
function bump(id){const c=el(id);c.classList.add('bump');setTimeout(()=>c.classList.remove('bump'),320);}

let lightOn=true, lightMix=1, feeder=false, feedTimer=0;
const actions={
  fish(){ if(fishArray.length>=MAX_FISH){toast('максимум '+MAX_FISH+' рыб');return;}
    createFish(); bump('cFish'); toast('+ рыбка'); },
  bubbles(){ addBubble(10); bump('cBub'); toast('+10 пузырьков'); },
  light(){ lightOn=!lightOn; document.body.classList.toggle('night',!lightOn);
    document.querySelector('[data-act="light"] .lbl').textContent=lightOn?'Ночной свет':'Дневной свет';
    toast(lightOn?'День':'Ночь · биолюминесценция'); },
  feeder(){ feeder=!feeder; document.querySelector('[data-act="feeder"]').classList.toggle('on',feeder);
    toast(feeder?'Автокорм включён':'Автокорм выключен'); }
};
document.querySelectorAll('.btn').forEach(b=>b.addEventListener('click',()=>actions[b.dataset.act]()));
el('uiToggle').addEventListener('click',()=>document.body.classList.toggle('ui-hidden'));
addEventListener('keydown',e=>{const k=e.key.toLowerCase();idle=0;controls.autoRotate=false;
  if(k==='f')actions.fish(); if(k==='b')actions.bubbles(); if(k==='l')actions.light();
  if(k==='a')actions.feeder(); if(k==='h')document.body.classList.toggle('ui-hidden');
  if(k===' '){e.preventDefault();addFood((Math.random()-.5)*BOUND.x*1.6,(Math.random()-.5)*BOUND.z*1.6,5);}});

// легенда окрасов + счётчики особей
const legend=el('legend'); const palCount=new Array(8).fill(0);
fishArray.forEach(f=>{});
function renderLegend(){
  PALETTES.forEach((p,i)=>{
    const li=document.createElement('li');
    li.innerHTML=`<s style="background:linear-gradient(135deg,${p.base},${p.dark})"></s>${p.name}<em>×${palCount[i]}</em>`;
    legend.appendChild(li);
  });
}
(function countPals(){ // привязка существующих рыб к палитрам
  fishArray.forEach((f,i)=>{palCount[i%8]++;});
})();
renderLegend();

/* --- спарклайн FPS --- */
const spark=el('spark'), sctx=spark.getContext('2d'); const hist=[];
function sizeSpark(){const r=spark.getBoundingClientRect(),d=Math.min(devicePixelRatio,2);
  spark.width=r.width*d;spark.height=r.height*d;sctx.setTransform(d,0,0,d,0,0);}
function drawSpark(){
  const w=spark.width/Math.min(devicePixelRatio,2),h=spark.height/Math.min(devicePixelRatio,2);
  sctx.clearRect(0,0,w,h); const n=Math.min(hist.length,42), off=42-n;
  for(let i=0;i<n;i++){const v=Math.min(hist[hist.length-n+i],75)/75,x=(i+off)/42*w,bh=Math.max(1.5,v*(h-4));
    sctx.fillStyle=v>.4?'rgba(95,240,220,.75)':'rgba(255,122,77,.85)';sctx.fillRect(x,h-bh,Math.max(w/44,1.5),bh);}
  sctx.fillStyle='rgba(127,233,255,.18)';sctx.fillRect(0,h-1,w,1);
}

/* ============================================================
   10. ЦИКЛ
   ============================================================ */
const clock=new THREE.Clock(); let fps=60,acc=0,frames=0,uiAcc=0,idle=0,lowT=0,quality=1;
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);sizeSpark();
});
sizeSpark();

function tick(){
  requestAnimationFrame(tick);
  const dt=Math.min(clock.getDelta(),.05), t=clock.elapsedTime;

  // свет (плавный переход день/ночь)
  const tgt=lightOn?1:0; lightMix+=(tgt-lightMix)*Math.min(1,dt*2.6);
  sun.intensity=THREE.MathUtils.lerp(.10,1.25,lightMix);
  amb.intensity=THREE.MathUtils.lerp(.22,.4,lightMix);
  hemi.intensity=THREE.MathUtils.lerp(.22,.5,lightMix);
  pl1.intensity=THREE.MathUtils.lerp(3.4,1.6,lightMix)*(1+Math.sin(t*1.7)*.06);
  pl2.intensity=THREE.MathUtils.lerp(2.6,1.3,lightMix)*(1+Math.cos(t*1.3)*.06);
  causticU.uStrength.value=THREE.MathUtils.lerp(.45,1.15,lightMix);
  scene.fog.color.copy(FOG_NIGHT).lerp(FOG_DAY,lightMix);
  bgU.uMix.value=lightMix;
  causticU.uTime.value=t; surfU.uTime.value=t;

  // рыбы
  for(let i=0;i<fishArray.length;i++) updateFish(fishArray[i],dt,t);

  // корм
  for(let i=foods.length-1;i>=0;i--){
    const fd=foods[i];
    if(!fd.set){
      fd.vy-=6.4*dt; fd.vy=Math.max(fd.vy,-4.2);
      fd.m.position.y+=fd.vy*dt;
      fd.m.position.x+=fd.vx*dt; fd.m.position.z+=fd.vz*dt;
      fd.vx*=.99; fd.vz*=.99;
      const sy=SAND_Y+.28+Math.sin(fd.m.position.x*.34)*Math.cos(fd.m.position.z*.42)*.34;
      if(fd.m.position.y<=sy){fd.m.position.y=sy;fd.set=true;}
    } else fd.life-=dt;
    fd.m.rotation.y+=dt*1.4; fd.m.rotation.x+=dt*.9;
    if(fd.set&&fd.life<2) fd.m.scale.multiplyScalar(1-dt*.5);
    if(fd.life<=0||fd.m.position.y<-H.y){tank.remove(fd.m);foods.splice(i,1);bump('cFood');}
  }

  // пузыри
  for(let i=0;i<bubbles.length;i++){
    const b=bubbles[i], p=b.m.position;
    p.y+=b.sp*dt*(.6+b.m.scale.x*2);
    p.x=b.ex+Math.sin(t*b.w+b.ph)*.55;
    p.z=b.ez+Math.cos(t*b.w*.86+b.ph)*.5;
    if(p.y>H.y-.7){p.y=SAND_Y+.3;p.x=b.ex+(Math.random()-.5)*.7;p.z=b.ez+(Math.random()-.5)*.7;}
    b.m.rotation.y+=dt;
  }

  // водоросли
  for(let i=0;i<plants.length;i++){const pl=plants[i];
    pl.g.rotation.x=Math.sin(t*pl.sp+pl.ph)*pl.a;
    pl.g.rotation.z=Math.cos(t*pl.sp*.8+pl.ph)*pl.a*1.3;}

  // планктон
  const pa=moteGeo.attributes.position;
  for(let i=0;i<MOTES;i++){let y=pa.getY(i)+dt*(.25+ms[i]*.35);
    if(y>H.y-.6)y=SAND_Y+.2; pa.setY(i,y);
    pa.setX(i,pa.getX(i)+Math.sin(t*.4+i)*dt*.08);}
  pa.needsUpdate=true;

  // кольца-эффекты
  for(let i=0;i<rings.length;i++){const r=rings[i]; if(r.l<=0)continue;
    r.l-=dt/r.dur; const k=1-Math.max(r.l,0);
    r.m.scale.setScalar(.6+k*r.max); r.m.material.opacity=Math.max(r.l,0)*.85;
    if(r.l<=0)r.m.visible=false;}

  // автокорм
  if(feeder){feedTimer-=dt;if(feedTimer<=0){addFood((Math.random()-.5)*BOUND.x*1.5,(Math.random()-.5)*BOUND.z*1.4,4);feedTimer=3.6;}}

  // авто-вращение в простое
  idle+=dt; if(idle>18) controls.autoRotate=true;
  controls.update();

  // телеметрия
  frames++; acc+=dt; uiAcc+=dt;
  if(acc>=.5){fps=frames/acc;frames=0;acc=0;hist.push(fps);if(hist.length>60)hist.shift();drawSpark();
    el('cFps').querySelector('b').textContent=Math.round(fps);
    if(fps<30&&quality===1){lowT++;if(lowT>3){quality=2;renderer.setPixelRatio(1);sun.shadow.mapSize.set(1024,1024);
      sun.shadow.map&&sun.shadow.map.dispose();sun.shadow.map=null;toast('эконом-режим');}}
    else if(fps>52&&quality===2){quality=1;renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));lowT=0;}
  }
  if(uiAcc>=.35){uiAcc=0;
    el('cFish').querySelector('b').textContent=fishArray.length;
    el('cBub').querySelector('b').textContent=bubbles.length;
    el('cFood').querySelector('b').textContent=foods.length;}

  renderer.render(scene,camera);
}
tick();

setTimeout(()=>el('loader').classList.add('gone'),1200);
setTimeout(()=>toast('кликните по воде, чтобы покормить'),2400);
})();
</script>
</body>
</html>
```

**Что внутри, помимо ТЗ:**

| Блок | Реализация |
|---|---|
| **Кожа рыб** | 8 палитр × паттерны (`stripes / lateral / twoTone / spots`) рисуются на CanvasTexture с UV-логикой сферы: `u` — огибание тела (полосы как у клоуна на обоих боках), `v` — тёмная спина → светлое брюхо + чешуйчатый микрорельеф |
| **Анатомия** | Тело-сфера, вилочкий хвост на отдельном пивоте (мах с амплитудой от реальной скорости), спинной, анальный и 2 грудных плавника (мах по оси Z), глаз = склера + зрачок + блик |
| **ИИ** | Блуждание по таймеру, разделение соседей + слабое согласование, мягкие стены, поиск корма в радиусе 15, любопытство/пугливость к камере, рост ×1.05 за корм |
| **Вода** | Каустика на дне (итеративный GLSL), анимированная поверхность с френелем, планктон (700 точек), `FogExp2`, градиентное небо-сфера с дизерингом |
| **Свет** | День↔Ночь с плавным лерпом интенсивностей, тумана и фона; ночью усиливаются подводные PointLight и каустика |
| **Производительство** | Дельта-тайминг, кэш текстур, тени только от тел/хвостов, авто-даунскейл pixelRatio и shadowMap при FPS < 30, авто-орбита камеры в простое 18 с |
| **HUD** | Телеметрия со спарклайном FPS, легенда окрасов со счётчиком особей, тосты, ripple на клике, скрытие интерфейса (`H`), горячие клавиши `F B L A Space` |