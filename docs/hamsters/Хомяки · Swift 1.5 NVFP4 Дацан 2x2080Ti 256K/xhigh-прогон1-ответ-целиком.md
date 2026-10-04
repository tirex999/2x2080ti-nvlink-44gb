# Low-Poly Hamster Playground

A single-file Three.js diorama: a bright plastic cage on a dark table, six chunky hamsters with real little routines (zoomies, snacking, grooming, naps, wheel-time), a spinning wheel you can flick, a door that opens, treats you can drop by clicking the bedding — and a live field guide that tells you what every hamster is doing.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Low-Poly Hamster Playground</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#152430; --ink2:#4b6472; --paper:#fffdf7; --paper2:#f4ecdd;
  --tang:#ff8a3d; --pink:#ff5d8f; --mint:#2ec4a6; --butter:#ffd166; --sky:#7fd3ff;
  --hard:5px 5px 0 rgba(3,17,22,.42);
  --hard-lg:9px 9px 0 rgba(3,17,22,.45);
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;overflow:hidden;background:#07161c;color:#eaf6f4;
  font-family:'Nunito Sans',system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;
}

/* ---------- layered ambient background ---------- */
.bg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;background:
   radial-gradient(120% 90% at 50% 8%, #1b4a52 0%, #0d2a33 42%, #061217 100%);}
.bg-grid{position:absolute;inset:-10%;
  background-image:radial-gradient(rgba(255,255,255,.18) 1.4px, transparent 1.5px);
  background-size:30px 30px;opacity:.09;
  animation:gridDrift 60s linear infinite;}
@keyframes gridDrift{to{transform:translate3d(30px,30px,0)}}
.bg-sweep{position:absolute;left:50%;top:52%;width:170vmax;height:170vmax;transform:translate(-50%,-50%);
  background:conic-gradient(from 0deg, transparent 0deg, rgba(46,196,166,.13) 26deg, transparent 60deg,
   transparent 180deg, rgba(255,138,61,.10) 210deg, transparent 250deg);
  animation:sweep 46s linear infinite;}
@keyframes sweep{to{transform:translate(-50%,-50%) rotate(360deg)}}
.bg-arc{position:absolute;border-radius:50%;border:1.5px dashed rgba(127,211,255,.14);}
.a1{width:70vmax;height:70vmax;left:-18vmax;bottom:-30vmax;animation:spinSlow 90s linear infinite}
.a2{width:46vmax;height:46vmax;right:-14vmax;top:-16vmax;border-color:rgba(255,93,143,.16);animation:spinSlow 70s linear infinite reverse}
@keyframes spinSlow{to{transform:rotate(360deg)}}
.motes{position:absolute;inset:0}
.mote{position:absolute;width:5px;height:5px;border-radius:50%;background:rgba(255,231,187,.75);
  filter:blur(.4px);box-shadow:0 0 10px rgba(255,206,140,.55);animation:floatUp linear infinite}
@keyframes floatUp{
  0%{transform:translateY(20px) translateX(0) scale(.6);opacity:0}
  12%{opacity:.85}
  90%{opacity:.5}
  100%{transform:translateY(-88vh) translateX(34px) scale(1.1);opacity:0}
}
#nightfall{position:fixed;inset:0;z-index:2;pointer-events:none;opacity:0;
  background:radial-gradient(90% 70% at 50% 30%, rgba(6,14,40,.35), rgba(2,6,20,.86));}
.bg-vignette{position:fixed;inset:0;z-index:3;pointer-events:none;
  box-shadow:inset 0 0 22vmax rgba(0,0,0,.55);}
.bg-grain{position:fixed;inset:0;z-index:3;pointer-events:none;opacity:.055;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E");}

#scene{position:fixed;inset:0;width:100%;height:100%;display:block;z-index:4;touch-action:none;cursor:grab}
#scene.pointing{cursor:pointer}

/* ---------- HUD ---------- */
.hud{position:fixed;inset:0;z-index:6;display:grid;pointer-events:none;
  grid-template-columns:minmax(250px,25vw) 1fr minmax(232px,21vw);
  grid-template-rows:auto 1fr auto;gap:14px;padding:clamp(12px,1.8vw,24px);}
.hud > *{pointer-events:auto}
.panel{background:linear-gradient(#fffdf7,#f5edde);color:var(--ink);
  border:2.5px solid var(--ink);border-radius:18px 18px 18px 7px;box-shadow:var(--hard);
  padding:13px 15px;animation:rise .8s cubic-bezier(.2,.9,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(22px) scale(.97)}}

.brand{grid-column:1;grid-row:1;background:none;border:0;box-shadow:none;padding:0;max-width:34ch}
.eyebrow{display:flex;align-items:center;gap:8px;margin:0;font-size:10.5px;font-weight:700;
  letter-spacing:.24em;text-transform:uppercase;color:#7fe6cd}
.dot{width:9px;height:9px;border-radius:50%;background:var(--pink);box-shadow:0 0 0 0 rgba(255,93,143,.7);
  animation:pulse 2s ease-out infinite}
@keyframes pulse{70%{box-shadow:0 0 0 12px rgba(255,93,143,0)}100%{box-shadow:0 0 0 0 rgba(255,93,143,0)}}
.brand h1{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;text-transform:uppercase;
  font-size:clamp(2.1rem,5.3vw,4.3rem);line-height:.82;letter-spacing:-.038em;margin:.22em 0 .34em}
.brand h1 span{display:block;text-shadow:4px 4px 0 rgba(3,17,22,.6)}
.brand h1 .l2{color:var(--tang);margin-left:.07em}
.lede{margin:0;font-size:14.5px;line-height:1.5;color:#c7dedd;max-width:31ch}
.lede b{color:#fff}

.stats{grid-column:3;grid-row:1;display:grid;grid-template-columns:1fr 1fr;gap:9px 12px;animation-delay:.08s}
.stat b{display:block;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.42rem;line-height:1;letter-spacing:-.02em}
.stat span{display:block;margin-top:3px;font-size:8.6px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--ink2)}
.stat:nth-child(2) b{color:var(--pink)}.stat:nth-child(3) b{color:#e08a1f}

.guide{grid-column:3;grid-row:2;align-self:start;margin-top:12px;animation-delay:.16s}
.phead{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:9px}
.phead h2{margin:0;font-family:'Bricolage Grotesque',sans-serif;font-size:12px;font-weight:800;
  letter-spacing:.16em;text-transform:uppercase}
.chip{font-size:8.6px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;padding:3px 7px;
  border-radius:99px;border:1.5px solid var(--ink);background:var(--mint);color:#08281f}
#roster{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
#roster li{display:grid;grid-template-columns:12px 1fr auto;align-items:center;gap:8px;padding:6px 7px;
  border-radius:9px;cursor:pointer;transition:background .18s, transform .18s}
#roster li:hover{background:rgba(46,196,166,.2);transform:translateX(3px)}
#roster li.sel{background:var(--ink);color:var(--paper)}
.sw{width:12px;height:12px;border-radius:4px;border:1.5px solid var(--ink)}
.nm{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:13.5px;letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.st{font-size:8.4px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:2px 6px;border-radius:99px;
  background:rgba(21,36,48,.1);white-space:nowrap}
.st[data-k="hot"]{background:var(--pink);color:#fff}
.st[data-k="food"]{background:var(--butter);color:#4a3200}
.st[data-k="calm"]{background:rgba(46,196,166,.45)}
.st[data-k="sleep"]{background:#cdd8ff;color:#22315e}
.ebar{grid-column:2/4;height:4px;border-radius:99px;background:rgba(21,36,48,.14);overflow:hidden}
.ebar i{display:block;height:100%;background:linear-gradient(90deg,var(--mint),var(--sky));transition:width .5s ease}
.focus{margin-top:11px;padding-top:10px;border-top:2px dashed rgba(21,36,48,.25);font-size:12px;line-height:1.45}
.focus h3{margin:0 0 3px;font-family:'Bricolage Grotesque',sans-serif;font-size:1.28rem;font-weight:800;letter-spacing:-.02em}
.focus .tags{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0}
.focus .tags em{font-style:normal;font-size:8.6px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  padding:3px 6px;border-radius:99px;background:var(--butter);border:1.5px solid var(--ink)}
.focus .nums{display:flex;gap:10px;margin-top:6px;color:var(--ink2);font-weight:600;font-size:11px}

.log{grid-column:1;grid-row:3;align-self:end;width:min(34ch,25vw);animation-delay:.24s}
#feed{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:5px;max-height:26vh;overflow:hidden}
#feed li{display:flex;gap:8px;align-items:flex-start;font-size:12.2px;line-height:1.35;
  animation:slideIn .45s cubic-bezier(.2,.9,.2,1) both}
#feed li i{flex:none;width:7px;height:7px;border-radius:50%;margin-top:5px;background:var(--tang)}
#feed li:nth-child(n+4){opacity:.42}
#feed li:nth-child(n+6){opacity:.2}
@keyframes slideIn{from{opacity:0;transform:translateX(-14px)}}

.dock{grid-column:2;grid-row:3;justify-self:center;align-self:end;display:flex;flex-direction:column;gap:9px;
  animation-delay:.32s;max-width:min(660px,92vw)}
.row{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
.btn{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:12.5px;letter-spacing:-.01em;
  display:inline-flex;align-items:center;gap:6px;padding:9px 13px;border-radius:12px;cursor:pointer;
  border:2.5px solid var(--ink);background:var(--paper);color:var(--ink);box-shadow:3px 3px 0 rgba(3,17,22,.42);
  transition:transform .16s cubic-bezier(.2,.9,.2,1), box-shadow .16s, background .16s}
.btn:hover{transform:translate(-2px,-3px);box-shadow:6px 7px 0 rgba(3,17,22,.45)}
.btn:active{transform:translate(1px,2px);box-shadow:1px 1px 0 rgba(3,17,22,.45)}
.btn .ico{font-size:15px;line-height:1;display:inline-block;transition:transform .4s}
.btn:hover .ico{transform:rotate(28deg) scale(1.16)}
.btn.p{background:var(--tang)}.btn.k{background:var(--mint)}
.btn[aria-pressed="true"]{background:var(--ink);color:var(--paper)}
.btn.sm{font-size:10.6px;padding:7px 10px;letter-spacing:.05em;text-transform:uppercase;border-radius:10px}
.sliders{display:flex;gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;
  padding-top:8px;border-top:2px dashed rgba(21,36,48,.25)}
.sl{display:flex;align-items:center;gap:7px;font-size:9.6px;font-weight:700;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink2)}
.sl output{font-family:'Bricolage Grotesque',sans-serif;font-size:12.5px;color:var(--ink);min-width:22px;text-align:center}
input[type=range]{-webkit-appearance:none;appearance:none;width:104px;height:22px;background:transparent;cursor:pointer}
input[type=range]::-webkit-slider-runnable-track{height:7px;border-radius:99px;background:#e3d9c6;border:2px solid var(--ink)}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:17px;height:17px;margin-top:-7px;border-radius:6px;
  background:var(--pink);border:2.5px solid var(--ink);box-shadow:2px 2px 0 rgba(3,17,22,.35)}
input[type=range]::-moz-range-track{height:7px;border-radius:99px;background:#e3d9c6;border:2px solid var(--ink)}
input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:5px;background:var(--pink);border:2.5px solid var(--ink)}

#hint{position:fixed;grid-column:1/-1;z-index:6;left:50%;transform:translateX(-50%);bottom:6px;
  font-size:10px;letter-spacing:.13em;text-transform:uppercase;font-weight:700;color:rgba(226,244,242,.5);
  pointer-events:none;text-align:center}
#hint kbd{font-family:inherit;background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);
  border-radius:4px;padding:1px 4px;margin:0 2px;color:#fff}

/* ---------- floating tags + bubble ---------- */
#tags{position:fixed;inset:0;z-index:5;pointer-events:none}
.tag{position:absolute;left:0;top:0;transform:translate(-50%,-130%);white-space:nowrap;
  font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:10.5px;letter-spacing:.02em;
  padding:3px 8px;border-radius:99px;background:rgba(10,26,32,.82);color:#fff;border:1.5px solid rgba(255,255,255,.35);
  transition:opacity .3s, transform .18s;backdrop-filter:blur(2px)}
.tag.sel{background:var(--tang);border-color:var(--ink);color:#231200;transform:translate(-50%,-130%) scale(1.16)}
.tag.sleep{background:rgba(120,140,255,.85);font-size:13px;letter-spacing:.16em}
.bubble{position:fixed;z-index:7;transform:translate(-50%,-115%) rotate(-1.6deg);max-width:210px;
  background:var(--paper);color:var(--ink);border:2.5px solid var(--ink);border-radius:14px 14px 14px 4px;
  padding:8px 11px;font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:13px;line-height:1.25;
  box-shadow:var(--hard);pointer-events:none;transition:opacity .3s}
.bubble::after{content:"";position:absolute;left:22px;bottom:-9px;width:12px;height:12px;background:var(--paper);
  border-right:2.5px solid var(--ink);border-bottom:2.5px solid var(--ink);transform:rotate(45deg)}
.bubble.hide{opacity:0}

/* ---------- boot ---------- */
#boot{position:fixed;inset:0;z-index:40;display:grid;place-items:center;background:#07161c;transition:opacity .7s}
#boot.gone{opacity:0;pointer-events:none}
.bootcard{text-align:center;width:min(320px,80vw)}
.wheel-ico{width:64px;height:64px;margin:0 auto 16px;border-radius:50%;border:5px solid var(--tang);
  border-top-color:var(--mint);position:relative;animation:spinFast 1.1s linear infinite}
.wheel-ico::after{content:"";position:absolute;inset:9px;border-radius:50%;border:2px dashed rgba(255,255,255,.35)}
@keyframes spinFast{to{transform:rotate(360deg)}}
.bootcard h2{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.5rem;letter-spacing:-.02em;margin:0 0 6px}
.bootcard p{margin:0 0 14px;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#7fe6cd}
.bar{height:8px;border-radius:99px;border:2px solid rgba(255,255,255,.3);overflow:hidden}
.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--tang),var(--pink));transition:width .18s}

@media (max-width:1080px){
  .hud{grid-template-columns:minmax(210px,1fr) 1fr minmax(200px,26vw)}
  .guide{display:none}.lede{display:none}
  .log{width:auto;grid-column:1;justify-self:start}
}
@media (max-width:720px){
  .hud{grid-template-columns:1fr;grid-template-rows:auto 1fr auto auto}
  .stats{grid-column:1;grid-row:1;grid-template-columns:repeat(4,1fr);margin-top:6px}
  .brand{grid-column:1;grid-row:1}
  .log{display:none}
  .dock{grid-column:1;grid-row:3}
  .btn{font-size:11.5px;padding:8px 10px}
  #hint{display:none}
}
@media (prefers-reduced-motion:reduce){
  .bg-sweep,.bg-grid,.bg-arc,.mote,.wheel-ico{animation:none!important}
}
</style>
</head>
<body>

<div class="bg">
  <div class="bg-grid"></div>
  <div class="bg-sweep"></div>
  <div class="bg-arc a1"></div><div class="bg-arc a2"></div>
  <div class="motes" id="motes"></div>
</div>
<div id="nightfall"></div>
<div class="bg-grain"></div>
<div class="bg-vignette"></div>

<canvas id="scene"></canvas>
<div id="tags"></div>
<div id="bubble" class="bubble hide"></div>

<div class="hud">
  <header class="brand">
    <p class="eyebrow"><span class="dot"></span> low-poly habitat · live simulation</p>
    <h1><span class="l1">Hamster</span><span class="l2">Playground</span></h1>
    <p class="lede">Six round roommates, one extremely loud wheel. <b>Drag to orbit</b>, click a hamster to interrogate it, click the bedding to drop a treat.</p>
  </header>

  <section class="stats panel" aria-label="Habitat telemetry">
    <div class="stat"><b id="sPop">6</b><span>hamsters</span></div>
    <div class="stat"><b id="sRpm">0</b><span>wheel rpm</span></div>
    <div class="stat"><b id="sSnacks">0</b><span>snacks</span></div>
    <div class="stat"><b id="sClock">09:00</b><span>habitat time</span></div>
  </section>

  <aside class="guide panel">
    <div class="phead"><h2>Field guide</h2><span class="chip">watching</span></div>
    <ul id="roster"></ul>
    <div class="focus" id="focus"></div>
  </aside>

  <section class="log panel">
    <div class="phead"><h2>Cage chatter</h2><span class="chip" style="background:var(--butter);color:#4a3200">noisy</span></div>
    <ul id="feed"></ul>
  </section>

  <div class="dock panel">
    <div class="row">
      <button class="btn p" id="bSpin"><span class="ico">🎡</span>Spin wheel</button>
      <button class="btn" id="bFood"><span class="ico">🌻</span>Refill bowl</button>
      <button class="btn" id="bTreat"><span class="ico">🍽</span>Scatter treats</button>
      <button class="btn k" id="bDoor"><span class="ico">🚪</span>Door</button>
    </div>
    <div class="row">
      <button class="btn sm" id="bNight" aria-pressed="false"><span class="ico">🌙</span>Nap time</button>
      <button class="btn sm" id="bOrbit" aria-pressed="false"><span class="ico">🧭</span>Auto-orbit</button>
      <button class="btn sm" id="bTags" aria-pressed="true"><span class="ico">🏷</span>Tags</button>
      <button class="btn sm" id="bCam"><span class="ico">⟳</span>Reset view</button>
      <div class="sliders" style="border:0;padding:0">
        <label class="sl">crew<input type="range" id="rPop" min="1" max="8" step="1" value="6"><output id="oPop">6</output></label>
        <label class="sl">speed<input type="range" id="rSpeed" min="0.3" max="2.2" step="0.1" value="1"><output id="oSpeed">1.0</output></label>
      </div>
    </div>
  </div>
</div>

<div id="hint"><kbd>drag</kbd> orbit · <kbd>scroll</kbd> zoom · <kbd>click floor</kbd> treat · <kbd>space</kbd> spin · <kbd>f</kbd> food · <kbd>n</kbd> nap · <kbd>r</kbd> reset</div>

<div id="boot"><div class="bootcard">
  <div class="wheel-ico"></div>
  <h2>Assembling the cage</h2><p id="bootMsg">bedding the tray…</p>
  <div class="bar"><i id="bootBar"></i></div>
</div></div>

<script type="importmap">
{"imports":{
  "three":"https://unpkg.com/three@0.161.0/build/three.module.js",
  "three/addons/":"https://unpkg.com/three@0.161.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';

/* ══════════════ helpers ══════════════ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const rand=(a,b)=>a+Math.random()*(b-a);
const pick=a=>a[(Math.random()*a.length)|0];
const lerp=(a,b,t)=>a+(b-a)*t;
function angStep(a,b,max){let d=(b-a)%(Math.PI*2);if(d>Math.PI)d-=Math.PI*2;if(d<-Math.PI)d+=Math.PI*2;
  return a+clamp(d,-max,max);}
const M=(color,o={})=>new THREE.MeshStandardMaterial({color,flatShading:true,roughness:.82,metalness:.03,...o});
function box(w,h,d,m,x=0,y=0,z=0){const me=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);me.position.set(x,y,z);me.castShadow=true;me.receiveShadow=true;return me;}
const $=s=>document.querySelector(s);

/* ══════════════ renderer / scene ══════════════ */
const canvas=$('#scene');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.06;

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0x08191f,34,78);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.1,220);
camera.position.set(12.4,9.2,14.6);
const controls=new OrbitControls(camera,canvas);
controls.enableDamping=true;controls.dampingFactor=.075;controls.enablePan=false;
controls.target.set(0,1.5,0);controls.minDistance=8;controls.maxDistance=34;
controls.minPolarAngle=.18;controls.maxPolarAngle=1.44;controls.autoRotateSpeed=.55;

/* ══════════════ lights ══════════════ */
const hemi=new THREE.HemisphereLight(0xbfe9ff,0xffd6a0,.62);scene.add(hemi);
const key=new THREE.DirectionalLight(0xfff3da,1.75);
key.position.set(9,15,7);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);
const sc=key.shadow.camera;sc.left=-11;sc.right=11;sc.top=9;sc.bottom=-9;sc.near=1;sc.far=42;
key.shadow.bias=-.0007;key.shadow.normalBias=.02;scene.add(key);
const fill=new THREE.DirectionalLight(0x9fd6ff,.4);fill.position.set(-9,6,-7);scene.add(fill);
const rim=new THREE.DirectionalLight(0xffb3c1,.45);rim.position.set(-5,3.5,-11);scene.add(rim);
const lamp=new THREE.PointLight(0xffb86b,0,17,2);lamp.position.set(0,7.4,0);scene.add(lamp);

/* hanging bulb above the cage (night mood) */
const bulbG=new THREE.Group();scene.add(bulbG);
bulbG.add(box(.06,.06,3.4,M(0x2a3b44),0,9.6,0));
const shade=new THREE.Mesh(new THREE.ConeGeometry(1.5,.9,10,1,true),M(0x1d3038,{side:THREE.DoubleSide}));
shade.position.set(0,8.55,0);bulbG.add(shade);
const bulbMat=new THREE.MeshStandardMaterial({color:0x4a3a20,emissive:0xffc27a,emissiveIntensity:.1,flatShading:true});
const bulb=new THREE.Mesh(new THREE.IcosahedronGeometry(.34,1),bulbMat);bulb.position.set(0,8.2,0);bulbG.add(bulb);

/* ══════════════ table + tray ══════════════ */
const C={mint:0x2ec4a6,mintD:0x23a186,cream:0xfbf6ea,bed:0xe9d5a4,bed2:0xf3e3bc,bed3:0xd9c08a,
         tang:0xff8a3d,butter:0xffd166,pink:0xff5d8f,pinkD:0xe04f7d,wood:0xd8ab6d,card:0xcf9a5f};

(function table(){
  const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d');
  const r=g.createRadialGradient(128,128,10,128,128,128);
  r.addColorStop(0,'#2a5a62');r.addColorStop(.55,'#163842');r.addColorStop(1,'#071318');
  g.fillStyle=r;g.fillRect(0,0,256,256);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;
  const disc=new THREE.Mesh(new THREE.CircleGeometry(24,44),
    new THREE.MeshStandardMaterial({map:t,roughness:1,metalness:0}));
  disc.rotation.x=-Math.PI/2;disc.position.y=-1.52;disc.receiveShadow=true;scene.add(disc);
})();

const BX=6,BZ=4.2, WALLH=6;
(function tray(){
  const g=new THREE.Group();scene.add(g);
  g.add(box(13.7,1.5,9.9,M(C.mint),0,-.75,0));
  const lm=M(C.mintD);
  g.add(box(13.7,.44,.36,lm,0,.16,4.77));g.add(box(13.7,.44,.36,lm,0,.16,-4.77));
  g.add(box(.36,.44,9.9,lm,6.67,.16,0));g.add(box(.36,.44,9.9,lm,-6.67,.16,0));
  const bed=box(13.05,.14,9.25,M(C.bed),0,.02,0);bed.name='floor';g.add(bed);
  // soft mounds
  for(let i=0;i<4;i++){
    const m=new THREE.Mesh(new THREE.IcosahedronGeometry(rand(.9,1.6),0),M(pick([C.bed2,C.bed,C.bed3])));
    m.position.set(rand(-5,5),rand(-.05,.02),rand(-3,3));m.scale.y=.24;m.receiveShadow=true;m.castShadow=true;g.add(m);
  }
  // bedding flakes (instanced)
  const N=460, geo=new THREE.BoxGeometry(.3,.05,.11);
  const inst=new THREE.InstancedMesh(geo,new THREE.MeshStandardMaterial({roughness:1,flatShading:true}),N);
  const d=new THREE.Object3D(),col=new THREE.Color();
  const pal=[0xf6e7bf,0xe8d3a1,0xdcc089,0xfff4d8,0xcfae76];
  for(let i=0;i<N;i++){
    d.position.set(rand(-6.3,6.3),rand(.05,.13),rand(-4.4,4.4));
    d.rotation.set(rand(-.3,.3),rand(0,Math.PI*2),rand(-.3,.3));
    d.scale.setScalar(rand(.7,1.5));d.updateMatrix();inst.setMatrixAt(i,d.matrix);
    col.set(pick(pal));inst.setColorAt(i,col);
  }
  inst.instanceColor.needsUpdate=true;inst.receiveShadow=true;g.add(inst);
})();

/* ══════════════ cage bars, posts, lid, door ══════════════ */
const doorPivot=new THREE.Group();doorPivot.position.set(-1.75,0,BZ);scene.add(doorPivot);
(function cage(){
  const barMat=M(C.cream,{roughness:.42,metalness:.35});
  const pts=[],seen=new Set();
  const add=(x,z)=>{const k=x.toFixed(2)+','+z.toFixed(2);if(seen.has(k))return;seen.add(k);
    if(z===BZ&&Math.abs(x)<1.8)return;           // door gap
    pts.push([x,z]);};
  for(let x=-BX;x<=BX+.01;x+=.6){add(x,BZ);add(x,-BZ);}
  for(let z=-BZ+.4;z<=BZ-.39;z+=.6){add(BX,z);add(-BX,z);}
  const inst=new THREE.InstancedMesh(new THREE.CylinderGeometry(.052,.052,WALLH,5),barMat,pts.length);
  const d=new THREE.Object3D();
  pts.forEach(([x,z],i)=>{d.position.set(x,WALLH/2+.2,z);d.rotation.set(0,0,0);d.updateMatrix();inst.setMatrixAt(i,d.matrix);});
  inst.castShadow=true;scene.add(inst);

  // lid bars
  const lids=[];for(let z=-BZ;z<=BZ+.01;z+=.6)lids.push(z);
  const li=new THREE.InstancedMesh(new THREE.CylinderGeometry(.05,.05,BX*2,5),barMat,lids.length);
  lids.forEach((z,i)=>{d.position.set(0,WALLH+.3,z);d.rotation.set(0,0,Math.PI/2);d.updateMatrix();li.setMatrixAt(i,d.matrix);});
  li.castShadow=true;scene.add(li);

  // frame + posts
  const fm=M(C.tang,{roughness:.5}),bm=M(C.butter,{roughness:.45});
  scene.add(box(BX*2+.7,.36,.36,fm,0,WALLH+.3,BZ));scene.add(box(BX*2+.7,.36,.36,fm,0,WALLH+.3,-BZ));
  scene.add(box(.36,.36,BZ*2,fm,BX,WALLH+.3,0));scene.add(box(.36,.36,BZ*2,fm,-BX,WALLH+.3,0));
  [[-1,-1],[-1,1],[1,-1],[1,1]].forEach(([sx,sz])=>{
    const p=new THREE.Mesh(new THREE.CylinderGeometry(.17,.19,WALLH+.8,6),fm);
    p.position.set(sx*BX,(WALLH+.8)/2,sz*BZ);p.castShadow=true;scene.add(p);
    const k=new THREE.Mesh(new THREE.IcosahedronGeometry(.24,0),bm);
    k.position.set(sx*BX,WALLH+.95,sz*BZ);k.castShadow=true;scene.add(k);
  });

  // door
  const dg=new THREE.Group();doorPivot.add(dg);
  dg.add(box(3.6,.18,.18,fm,1.75,3.62,0));dg.add(box(3.6,.18,.18,fm,1.75,.42,0));
  dg.add(box(.18,3.4,.18,fm,.04,2.0,0));dg.add(box(.18,3.4,.18,fm,3.46,2.0,0));
  for(let i=0;i<4;i++)dg.add(box(.1,3.1,.1,barMat,.55+i*.8,2.0,0));
  const latch=box(.26,.34,.3,bm,3.6,2.0,.06);dg.add(latch);
})();

/* ══════════════ wheel (interactive) ══════════════ */
const wheel={group:new THREE.Group(),spinner:new THREE.Group(),spin:0,angle:0,occupant:null,dist:0};
(function buildWheel(){
  const g=wheel.group;g.position.set(3.7,0,-1.7);g.rotation.y=-.5;scene.add(g);
  const cream=M(C.cream,{roughness:.45,metalness:.2}), pm=M(C.pink), pd=M(C.pinkD), bm=M(C.butter);
  g.add(box(1.8,.24,2.9,cream,0,.12,0));
  g.add(box(.26,1.5,.26,cream,0,.85,1.06));g.add(box(.26,1.5,.26,cream,0,.85,-1.06));
  const axle=new THREE.Mesh(new THREE.CylinderGeometry(.08,.08,2.5,8),bm);
  axle.rotation.x=Math.PI/2;axle.position.y=1.55;axle.castShadow=true;g.add(axle);

  const s=wheel.spinner;s.position.y=1.55;g.add(s);
  [ .52,-.52].forEach(z=>{const t=new THREE.Mesh(new THREE.TorusGeometry(1.3,.1,4,20),pm);t.position.z=z;t.castShadow=true;s.add(t);});
  const shell=new THREE.Mesh(new THREE.TorusGeometry(1.3,.21,5,22),pm);shell.castShadow=true;s.add(shell);
  const back=new THREE.Mesh(new THREE.CircleGeometry(1.22,14),pd);back.position.z=-.62;back.material=pd;s.add(back);
  const rungM=M(C.butter,{roughness:.6});
  for(let i=0;i<14;i++){const a=i/14*Math.PI*2;
    const r=new THREE.Mesh(new THREE.BoxGeometry(.11,.11,1.02),rungM);
    r.position.set(Math.cos(a)*1.17,Math.sin(a)*1.17,0);r.rotation.z=a;r.castShadow=true;s.add(r);}
  for(let i=0;i<3;i++){const sp=box(.1,2.3,.1,cream,0,0,-.5);sp.rotation.z=i*Math.PI/3;s.add(sp);}
  const hub=new THREE.Mesh(new THREE.CylinderGeometry(.18,.18,.34,8),bm);hub.rotation.x=Math.PI/2;hub.position.z=-.5;s.add(hub);
})();

/* ══════════════ bowl, bottle, tunnel, house, pebbles ══════════════ */
const bowl={group:new THREE.Group(),pos:new THREE.Vector3(-4.3,0,2.5),pellets:[]};
(function buildBowl(){
  const g=bowl.group;g.position.copy(bowl.pos);scene.add(g);
  const prof=[[0,0],[.36,0],[.52,.12],[.64,.3],[.61,.36]].map(p=>new THREE.Vector2(p[0],p[1]));
  const lathe=new THREE.Mesh(new THREE.LatheGeometry(prof,11),M(C.butter,{side:THREE.DoubleSide}));
  lathe.castShadow=true;lathe.receiveShadow=true;g.add(lathe);
  g.add(box(.9,.06,.9,M(0xc78a45),0,.2,0));
  g.position.y=0;
})();
const bottle={pos:new THREE.Vector3(6.05,0,-2.4),dripT:0,drip:null};
(function buildBottle(){
  const g=new THREE.Group();g.position.copy(bottle.pos);scene.add(g);
  const glass=new THREE.Mesh(new THREE.CylinderGeometry(.42,.42,1.75,10,1,true),
    new THREE.MeshStandardMaterial({color:0xdff6ff,transparent:true,opacity:.4,roughness:.15,side:THREE.DoubleSide}));
  glass.position.set(0,3.5,-.3);g.add(glass);
  const water=new THREE.Mesh(new THREE.CylinderGeometry(.35,.35,1.15,10),
    new THREE.MeshStandardMaterial({color:0x7fd3ff,transparent:true,opacity:.75,flatShading:true}));
  water.position.set(0,3.2,-.3);g.add(water);
  const collar=new THREE.Mesh(new THREE.CylinderGeometry(.24,.16,.3,8),M(0xb9c6cc,{metalness:.6,roughness:.3}));
  collar.position.set(0,2.55,-.3);collar.castShadow=true;g.add(collar);
  const tube=new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,.7,6),M(0xcfd8dc,{metalness:.5,roughness:.3}));
  tube.position.set(0,2.2,-.3);g.add(tube);
  const d=new THREE.Mesh(new THREE.IcosahedronGeometry(.07,0),
    new THREE.MeshStandardMaterial({color:0xbfefff,transparent:true,opacity:.9}));
  d.position.set(0,1.95,-.3);g.add(d);bottle.drip=d;bottle.dripT=rand(2,7);
})();
const tunnel={pos:new THREE.Vector3(2.0,0,2.4),rot:.35,a:new THREE.Vector3(),b:new THREE.Vector3()};
(function buildTunnel(){
  const g=new THREE.Group();g.position.copy(tunnel.pos);g.rotation.y=tunnel.rot;scene.add(g);
  const tube=new THREE.Mesh(new THREE.CylinderGeometry(.74,.74,3.1,13,1,true),
    M(C.card,{side:THREE.DoubleSide,roughness:.95}));
  tube.rotation.z=Math.PI/2;tube.position.y=.74;tube.castShadow=true;tube.receiveShadow=true;g.add(tube);
  [-1.55,1.55].forEach(x=>{const r=new THREE.Mesh(new THREE.TorusGeometry(.74,.08,4,13),M(0xb8814c));
    r.rotation.y=Math.PI/2;r.position.set(x,.74,0);r.castShadow=true;g.add(r);});
  const dir=new THREE.Vector3(1,0,0).applyEuler(new THREE.Euler(0,tunnel.rot,0));
  tunnel.a.copy(tunnel.pos).addScaledVector(dir,-1.75);
  tunnel.b.copy(tunnel.pos).addScaledVector(dir,1.75);
})();
const house={pos:new THREE.Vector3(-4.4,0,-2.3)};
(function buildHouse(){
  const g=new THREE.Group();g.position.copy(house.pos);scene.add(g);
  g.add(box(2.3,1.35,2.1,M(0xffe9c9),0,.68,0));
  const roof=new THREE.Mesh(new THREE.ConeGeometry(1.95,1.05,4),M(C.tang));
  roof.position.y=1.85;roof.rotation.y=Math.PI/4;roof.castShadow=true;g.add(roof);
  const door=new THREE.Mesh(new THREE.CircleGeometry(.42,9),new THREE.MeshStandardMaterial({color:0x3a2a20}));
  door.position.set(0,.62,1.06);g.add(door);
  for(let i=0;i<3;i++){const h=new THREE.Mesh(new THREE.ConeGeometry(.14,.34,5),M(C.bed2));
    h.position.set(rand(-1.4,1.4),.17,rand(1,1.4));g.add(h);}
})();
(function scatter(){
  const peb=M(0x9fb0b8);
  for(let i=0;i<7;i++){const p=new THREE.Mesh(new THREE.IcosahedronGeometry(rand(.12,.24),0),peb);
    p.position.set(rand(-5.6,5.6),.08,rand(-3.6,3.6));p.castShadow=true;scene.add(p);}
  const seedM=[M(0xe2b96a),M(0xb5763a)];
  for(let i=0;i<10;i++){const s=new THREE.Mesh(new THREE.DodecahedronGeometry(.08,0),pick(seedM));
    s.position.set(rand(-6,6),.07,rand(-4,4));s.castShadow=true;scene.add(s);}
})();

/* dust motes in 3D */
const dust=(function(){
  const N=170,pos=new Float32Array(N*3);
  for(let i=0;i<N;i++){pos[i*3]=rand(-9,9);pos[i*3+1]=rand(.4,8.5);pos[i*3+2]=rand(-7,7);}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const p=new THREE.Points(g,new THREE.PointsMaterial({color:0xffe9c0,size:.075,transparent:true,opacity:.55,
    blending:THREE.AdditiveBlending,depthWrite:false}));
  scene.add(p);return p;
})();

/* ══════════════ hamsters ══════════════ */
const NAMES=['Pumpkin','Nugget','Biscuit','Waffles','Pickles','Mochi','Noodle','Toots','Gizmo','Pebbles','Churro','Bramble'];
const FURS=[0xf3a53b,0xfff1dc,0xd9772f,0x9fb4c0,0xf6c46a,0xe88ea0,0x6f6a63,0xffd8a8];
const CAPS=[0xc9762a,0xd9542f,0x6d8898,0xe0b45c,0xbfbfbf,0xd07f92,0x4e4a45,0xe8c391];
const LINES={
  walk:["excavation mode","patrol complete","sniffed a flake","where is everyone","big lap energy"],
  idle:["loafing intensifies","considering a seed","three seconds of stillness","melting into bedding"],
  sniff:["this flake is premium","smells like Tuesday","investigating a crumb","noted. filed. moved on."],
  groom:["extremely professional","ear polish day","whiskers aligned","not a hair out of place"],
  wheel:["RUNNING (union rates apply)","the wheel wins again","vroom vroom","cardio? never heard of it"],
  eat:["storing for winter","cheeks: full","one seed, four stashes","nom nom nom"],
  drink:["sip sip","hygiene queen","bottle is mine now","drip acquired"],
  sleep:["zzz","dreaming of sunflower seeds","a very round loaf","do not disturb (seriously)"],
  spook:["ZOOMIES","startled by a flake","fast little potato","why is it like this"],
  tunnelIn:["tunnel!!","whoosh","tube specialist","applied physics: gone"]
};
const STATE_LABEL={walk:['exploring','calm'],idle:['loafing','calm'],sniff:['sniffing','calm'],groom:['grooming','calm'],
  wheel:['wheel!!','hot'],eat:['snacking','food'],drink:['drinking','calm'],sleep:['asleep','sleep'],
  spook:['ZOOMIES','hot'],seek:['treat chase','food'],tunnelIn:['tunnel!','hot']};

const W={night:0,bx:5.4,bz:3.3,obstacles:[],wheel,treats:[],food:0,doorOpen:false,
  log:(m,k)=>addFeed(m,k)};
W.obstacles=[{x:3.7,z:-1.7,r:1.55,id:'wheel'},{x:-4.4,z:-2.3,r:1.5,id:'house'},{x:-4.3,z:2.5,r:.85,id:'bowl'}];

class Hamster{
  constructor(i){
    this.name=NAMES[i%NAMES.length];
    const fur=FURS[i%FURS.length], cap=CAPS[(i*3+1)%CAPS.length];
    this.furHex='#'+new THREE.Color(fur).getHexString();
    this.traits={speed:rand(.5,1),energy:rand(.2,1),foodie:rand(.2,1),sleepy:rand(.1,.9),curious:rand(.2,1)};
    this.stats={snacks:0,naps:0,dist:0};
    this.energy=rand(.55,1);this.phase=rand(0,6.28);this.blink=rand(1,5);
    this.pos=new THREE.Vector3(rand(-3,3),0,rand(-2,2));
    this.heading=rand(0,6.28);this.state='idle';this.stateT=0;this.dur=rand(1,3);
    this.target=null;this.ignore=null;this.treat=null;this.mount=0;this.eatTick=0;
    this.sel=false;this.hover=false;this.energy=clamp(this.energy,.4,1);

    const g=new THREE.Group();this.group=g;scene.add(g);
    const rig=new THREE.Group();g.add(rig);this.rig=rig;
    const furM=M(fur),bellyM=M(0xfff5e6),skinM=M(0xffb3c1),darkM=M(0x241a12,{roughness:.35});
    this.furMat=furM;
    const body=new THREE.Mesh(new THREE.IcosahedronGeometry(.5,1),furM);
    body.scale.set(1.14,.95,1.36);body.position.y=.53;body.castShadow=true;rig.add(body);this.body=body;
    const shell=new THREE.Mesh(new THREE.SphereGeometry(.512,9,6,0,Math.PI*2,0,Math.PI*.62),M(cap));
    shell.scale.set(1.14,.96,1.36);shell.position.y=.53;shell.rotation.x=-.42;shell.castShadow=true;rig.add(shell);
    const belly=new THREE.Mesh(new THREE.IcosahedronGeometry(.42,1),bellyM);
    belly.scale.set(1,.72,1.15);belly.position.set(0,.34,.1);rig.add(belly);

    const head=new THREE.Group();head.position.set(0,.83,.5);rig.add(head);this.head=head;
    const skull=new THREE.Mesh(new THREE.IcosahedronGeometry(.36,1),furM);skull.castShadow=true;head.add(skull);
    const muz=new THREE.Mesh(new THREE.IcosahedronGeometry(.19,1),bellyM);
    muz.scale.set(1,.8,1.15);muz.position.set(0,-.09,.26);head.add(muz);
    const nose=new THREE.Mesh(new THREE.IcosahedronGeometry(.06,0),skinM);nose.position.set(0,-.02,.44);head.add(nose);
    this.eyes=[];this.cheeks=[];this.ears=[];
    [-1,1].forEach(s=>{
      const e=new THREE.Mesh(new THREE.IcosahedronGeometry(.07,1),darkM);
      e.position.set(.19*s,.06,.29);head.add(e);this.eyes.push(e);
      const hl=new THREE.Mesh(new THREE.IcosahedronGeometry(.026,0),
        new THREE.MeshStandardMaterial({color:0xffffff,emissive:0xffffff,emissiveIntensity:.7}));
      hl.position.set(.21*s,.09,.34);head.add(hl);
      const ch=new THREE.Mesh(new THREE.IcosahedronGeometry(.18,1),bellyM);
      ch.position.set(.25*s,-.13,.2);head.add(ch);this.cheeks.push(ch);
      const ear=new THREE.Group();ear.position.set(.3*s,.26,.02);
      const disc=new THREE.Mesh(new THREE.CylinderGeometry(.15,.17,.05,6),furM);
      disc.rotation.z=Math.PI/2;disc.castShadow=true;ear.add(disc);
      const inr=new THREE.Mesh(new THREE.CylinderGeometry(.09,.1,.06,6),skinM);inr.rotation.z=Math.PI/2;ear.add(inr);
      ear.rotation.y=s*.55;head.add(ear);this.ears.push(ear);
    });
    // whiskers
    const wpts=[];[-1,1].forEach(s=>{for(let k=0;k<3;k++){
      wpts.push(.1*s,-.03,.42, .58*s,-.09+k*.06,.5);}});
    const wg=new THREE.BufferGeometry();wg.setAttribute('position',new THREE.Float32BufferAttribute(wpts,3));
    head.add(new THREE.LineSegments(wg,new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.4})));
    const tail=new THREE.Mesh(new THREE.IcosahedronGeometry(.09,0),furM);
    tail.position.set(0,.5,-.72);rig.add(tail);this.tail=tail;
    this.legs=[];
    [[-.34,.36],[.34,.36],[-.35,-.36],[.35,-.36]].forEach(([x,z])=>{
      const l=new THREE.Group();l.position.set(x,.3,z);rig.add(l);
      const m=new THREE.Mesh(new THREE.BoxGeometry(.16,.26,.2),furM);m.position.y=-.12;m.castShadow=true;l.add(m);
      const paw=new THREE.Mesh(new THREE.IcosahedronGeometry(.085,0),skinM);paw.position.set(0,-.26,.03);l.add(paw);
      this.legs.push(l);
    });
    // selection ring
    const ring=new THREE.Mesh(new THREE.TorusGeometry(.92,.055,4,22),
      new THREE.MeshBasicMaterial({color:0xffd166,transparent:true,opacity:0}));
    ring.rotation.x=-Math.PI/2;ring.position.y=.14;g.add(ring);this.ring=ring;

    const tag=document.createElement('div');tag.className='tag';tag.textContent=this.name;
    $('#tags').appendChild(tag);this.tag=tag;
    this.setNext();
  }
  dispose(){
    this.group.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material&&o.material.dispose)o.material.dispose();});
    scene.remove(this.group);this.tag.remove();
  }

  /* ── state machine ── */
  enter(s,dur){this.state=s;this.stateT=0;this.dur=dur;}
  setNext(){
    const t=this.traits,n=W.night;
    if(n>.55&&Math.random()<.45+t.sleepy*.45)return this.goSleep();
    if(this.energy<.24&&Math.random()<.7)return this.goSleep();
    const r=Math.random();
    if(!W.wheel.occupant&&r<.13+t.energy*.32)return this.goWheel();
    if(r<.2+t.foodie*.28&&W.food>0)return this.goEat();
    if(r<.06+t.curious*.14){this.target=new THREE.Vector3(bottle.pos.x-.95,0,bottle.pos.z);
      this.enter('walk',12);this.ignore=null;return;}
    if(r<.1+t.curious*.16){this.target=tunnel.a.clone();this.enter('walk',14);this.ignore=null;return;}
    if(r<.08)return this.enter('sniff',rand(1.6,3.2));
    if(r<.16)return this.enter('groom',rand(2,3.6));
    if(r<.2)return this.goSleep();
    this.goWalk();
  }
  goWalk(){
    let tx,tz;
    if(Math.random()<.4){const o=pick(W.obstacles);tx=o.x+rand(-2.2,2.2);tz=o.z+rand(-1.8,1.8);}
    else{tx=rand(-W.bx,W.bx);tz=rand(-W.bz,W.bz);}
    this.target=new THREE.Vector3(clamp(tx,-W.bx,W.bx),0,clamp(tz,-W.bz,W.bz));
    this.ignore=null;this.enter('walk',rand(4,9));
  }
  goEat(){this.target=new THREE.Vector3(W.bowl.pos.x+.15,0,W.bowl.pos.z+.8);this.enter('walk',14);this.ignore='bowl';this.pending='bowl';}
  goWheel(){this.target=new THREE.Vector3(3.7,0,-.15);this.enter('walk',16);this.ignore='wheel';this.pending='wheel';}
  goSleep(){
    this.stats.naps++;this.energy=clamp(this.energy+.42,0,1);
    if(Math.random()<.55){this.target=new THREE.Vector3(house.pos.x,0,house.pos.z+1.35);this.enter('walk',16);this.ignore='house';this.pending='sleep';}
    else{this.enter('sleep',rand(7,15)*(W.night>.5?1.7:1));}
  }
  seek(treat){if(this.state==='sleep')return;this.treat=treat;this.target=treat.pos.clone();this.ignore=null;this.enter('seek',14);}
  onArrive(){
    const p=this.pending;this.pending=null;
    if(p==='wheel'){W.wheel.occupant=this;this.mount=0;this.ground=this.pos.clone();this.enter('wheel',rand(6,13));return;}
    if(p==='bowl'){this.enter('eat',rand(3,5.2));this.eatTick=0;return;}
    if(p==='sleep'){this.stats.naps++;this.energy=clamp(this.energy+.4,0,1);this.enter('sleep',rand(6,13)*(W.night>.5?1.7:1));return;}
    this.setNext();
  }

  moveStep(dt,speed,turn=3.2){
    const dx=this.target.x-this.pos.x, dz=this.target.z-this.pos.z;
    const dist=Math.hypot(dx,dz);
    let dirx=dx/(dist||1),dirz=dz/(dist||1);
    for(const o of W.obstacles){
      if(this.ignore===o.id)continue;
      const ox=this.pos.x-o.x,oz=this.pos.z-o.z,d=Math.hypot(ox,oz),rr=o.r+.5;
      if(d<rr&&d>.001){const k=(rr-d)*2.4/d;dirx+=ox*k;dirz+=oz*k;}
    }
    const want=Math.atan2(dirx,dirz);
    this.heading=angStep(this.heading,want,turn*dt);
    const step=speed*dt;
    this.pos.x=clamp(this.pos.x+Math.sin(this.heading)*step,-W.bx,W.bx);
    this.pos.z=clamp(this.pos.z+Math.cos(this.heading)*step,-W.bz,W.bz);
    this.stats.dist+=step;return dist;
  }

  /* ── animation bits ── */
  animWalk(t,rate=1,amp=.72){
    const p=this.phase,w=t*10*rate;
    this.legs[0].rotation.x=Math.sin(w)*amp;this.legs[3].rotation.x=Math.sin(w)*amp;
    this.legs[1].rotation.x=Math.sin(w+Math.PI)*amp;this.legs[2].rotation.x=Math.sin(w+Math.PI)*amp;
    this.rig.position.y=Math.abs(Math.sin(w))*.055*rate;
    this.rig.rotation.z=Math.sin(w*.5)*.045;
    this.head.rotation.x=Math.sin(w*.5)*.12;this.tail.rotation.y=Math.sin(t*7)*.4;
  }
  animIdle(t){
    const b=1+Math.sin(t*2.1+this.phase)*.028;
    this.rig.scale.set(1,b,1);this.rig.position.y=0;
    this.legs.forEach(l=>{l.rotation.x=lerp(l.rotation.x,0,.12);});
    this.head.rotation.x=Math.sin(t*1.3+this.phase)*.08;this.head.rotation.y=Math.sin(t*.6)*.25;
    this.tail.rotation.y=Math.sin(t*2.2)*.25;
  }
  animSniff(t){
    this.animIdle(t);
    this.head.rotation.x=.42+Math.sin(t*9)*.2;
    this.rig.position.y=Math.abs(Math.sin(t*4.5))*.02;
  }
  animGroom(t){
    this.head.rotation.z=Math.sin(t*6)*.5;this.head.rotation.x=.3;
    this.rig.rotation.y=Math.sin(t*3)*.18;
    this.legs[0].rotation.x=-1.5+Math.sin(t*9)*.4;this.legs[1].rotation.x=-1.5+Math.sin(t*9+1)*.4;
    this.rig.position.y=Math.abs(Math.sin(t*3))*.03;
  }
  animEat(t,dt){
    this.head.rotation.x=.5+Math.sin(t*13)*.28;
    const puff=1+Math.min(.7,this.stateT*.22)+Math.sin(t*13)*.09;
    this.cheeks.forEach(c=>c.scale.setScalar(puff));
    this.rig.position.y=Math.abs(Math.sin(t*6.5))*.03;
    this.legs[0].rotation.x=Math.sin(t*13)*.3;this.legs[1].rotation.x=-Math.sin(t*13)*.3;
  }
  animDrink(t){
    this.head.rotation.x=-.62+Math.sin(t*11)*.12;
    this.cheeks.forEach(c=>c.scale.setScalar(1));
    this.rig.position.y=0;this.legs.forEach(l=>l.rotation.x=lerp(l.rotation.x,0,.1));
  }
  animSleep(t){
    this.rig.scale.set(1.06,.82+Math.sin(t*1.4)*.03,1.06);
    this.head.position.set(0,.7,-.02);this.head.rotation.x=.5;this.head.rotation.z=0;
    this.eyes.forEach(e=>e.scale.y=lerp(e.scale.y,.1,.2));
    this.ears.forEach(e=>e.rotation.z=.3);
    this.legs.forEach(l=>l.rotation.x=lerp(l.rotation.x,.4,.1));
    this.cheeks.forEach(c=>c.scale.setScalar(1));
    this.rig.position.y=0;
  }

  update(dt){
    this.stateT+=dt;const t=this.stateT;
    this.blink-=dt;
    if(this.blink<0){this.blink=rand(2.4,6);if(this.state!=='sleep')
      {this.eyes.forEach(e=>e.scale.y=.12);setTimeout(()=>this.eyes.forEach(e=>e.scale.y=1),130);}}

    switch(this.state){
      case 'walk':{
        const d=this.moveStep(dt,1.5+this.traits.speed*1.5);
        this.animWalk(t,1);
        this.energy=clamp(this.energy-dt*.012,0,1);
        if(d<.42)this.onArrive();
        else if(t>this.dur)this.setNext();
        break;}
      case 'seek':{
        if(!this.treat||this.treat.taken){this.setNext();break;}
        const d=this.moveStep(dt,2.6,.0+3.6);this.animWalk(t,1.7,.95);
        this.energy=clamp(this.energy-dt*.02,0,1);
        if(d<.5){this.treat.eat();this.stats.snacks++;this.enter('eat',1.7);this.eatTick=9;
          W.log(`${this.name} located a treat. Priorities: confirmed.`,'food');}
        else if(t>this.dur)this.setNext();
        break;}
      case 'idle':this.animIdle(t);if(t>this.dur)this.setNext();break;
      case 'sniff':this.animSniff(t);if(t>this.dur)this.setNext();break;
      case 'groom':this.animGroom(t);if(t>this.dur)this.setNext();break;
      case 'eat':{
        this.animEat(t,dt);
        if(this.eatTick<9){this.eatTick+=dt;
          if(this.eatTick>1.15&&W.food>0){this.eatTick=0;W.removePellet();this.stats.snacks++;
            W.log(`${this.name} buried a seed in its cheeks.`,'food');}}
        if(t>this.dur){this.cheeks.forEach(c=>c.scale.setScalar(1));this.setNext();}
        break;}
      case 'drink':{
        this.animDrink(t);bottle.dripT=.4;
        if(t>this.dur)this.setNext();break;}
      case 'wheel':{
        const wm=W.wheel;const running=this.stateT>.6&&this.stateT<this.dur-.5;
        this.mount=Math.min(1,this.mount+dt*2.2);
        const seat=wm.group.localToWorld(new THREE.Vector3(0,-1.02,.06));
        const e=1-Math.pow(1-this.mount,3);
        this.group.position.lerpVectors(this.ground,seat,e);
        this.group.rotation.y=wm.group.rotation.y+Math.PI/2;
        this.animWalk(t,running?2.1:.4,running?1:.4);
        this.rig.position.y=Math.sin(t*19)*.045;
        this.energy=clamp(this.energy-dt*.06,0,1);
        if(running)wm.runner=this; 
        if(this.stateT>this.dur){
          wm.occupant=null;if(wm.runner===this)wm.runner=null;
          const out=new THREE.Vector3(wm.group.position.x*.55,0,wm.group.position.z+2.1);
          this.pos.set(clamp(out.x,-W.bx,W.bx),0,clamp(out.z,-W.bz,W.bz));
          this.rig.scale.set(1,1,1);this.head.position.set(0,.83,.5);
          this.enter('idle',rand(.6,1.4));
          W.log(`${this.name} stepped off the wheel, wobbly.`,'calm');
        }
        return; // skip transform write below
      }
      case 'sleep':{
        this.animSleep(t);
        this.energy=clamp(this.energy+dt*.05,0,1);
        if(t>this.dur&&W.night<.5){this.rig.scale.set(1,1,1);this.head.position.set(0,.83,.5);
          this.eyes.forEach(e=>e.scale.y=1);this.ears.forEach(e=>e.rotation.z=0);this.enter('idle',rand(.6,1.6));}
        break;}
      case 'tunnelIn':{
        const d=this.moveStep(dt,3.2,4.5);this.animWalk(t,2,.9);
        if(d<.4){this.pos.copy(tunnel.b);this.enter('idle',rand(.4,1));
          W.log(`${this.name} was launched out of the tunnel.`,'hot');}
        break;}
    }
    // tunnel trigger on arrival at entrance
    if(this.state==='walk'&&this.target&&this.target.distanceTo(tunnel.a)<.5){
      this.target=tunnel.b.clone();this.enter('tunnelIn',10);
      W.log(`${this.name} entered the cardboard tube.`,'hot');
    }
    this.group.position.set(this.pos.x,0,this.pos.z);
    this.group.rotation.y=angStep(this.group.rotation.y,this.heading,.28);
  }
}

/* food pellets */
const PAL=[0xe2b96a,0xb5763a,0xf2d08a,0xc98a4b];
W.addPellet=function(){
  const p=new THREE.Mesh(new THREE.DodecahedronGeometry(.095,0),M(pick(PAL)));
  const a=rand(0,6.28),r=rand(.05,.34);
  p.position.set(Math.cos(a)*r,.3,Math.sin(a)*r);p.castShadow=true;
  bowl.group.add(p);bowl.pellets.push(p);W.food++;
};
W.removePellet=function(){
  const p=bowl.pellets.pop();if(!p)return;p.material.dispose();p.geometry.dispose();
  bowl.group.remove(p);W.food=Math.max(0,W.food-1);
};
W.refill=function(){while(W.food<9)W.addPellet();W.log('Bowl refilled. Nine seeds, zero chill.','food');};

/* treats */
let treatId=0;
W.spawnTreat=function(x,z){
  const m=new THREE.Mesh(new THREE.DodecahedronGeometry(.14,0),M(0xb5763a));
  m.position.set(x,.14,z);m.castShadow=true;scene.add(m);
  const t={id:++treatId,mesh:m,pos:new THREE.Vector3(x,0,z),taken:false,spin:rand(0,6)};
  t.eat=()=>{t.taken=true;scene.remove(m);m.geometry.dispose();m.material.dispose();
    W.treats=W.treats.filter(o=>o!==t);};
  W.treats.push(t);
  hamsters.map(h=>({h,d:h.pos.distanceTo(t.pos)})).sort((a,b)=>a.d-b.d).slice(0,2)
    .forEach(({h})=>h.seek(t));
  return t;
};

const hamsters=[];
function addHamster(){
  if(hamsters.length>=8)return;
  const h=new Hamster(hamsters.length+((Date.now()/1000)|0));
  hamsters.push(h);buildRoster();
}
function removeHamster(){
  const h=hamsters.pop();if(!h)return;
  if(W.wheel.occupant===h)W.wheel.occupant=null;
  if(selected===h)select(null);
  h.dispose();buildRoster();
}

/* ══════════════ UI ══════════════ */
const feedEl=$('#feed');
function addFeed(msg,kind){
  const li=document.createElement('li');
  li.innerHTML=`<i style="background:${kind==='food'?'#e08a1f':kind==='hot'?'#ff5d8f':kind==='sleep'?'#7f8fff':'#2ec4a6'}"></i><span>${msg}</span>`;
  feedEl.prepend(li);
  while(feedEl.children.length>6)feedEl.lastChild.remove();
}
const rosterEl=$('#roster');
function buildRoster(){
  rosterEl.innerHTML='';
  hamsters.forEach((h,i)=>{
    const li=document.createElement('li');li.dataset.i=i;
    li.innerHTML=`<span class="sw" style="background:${h.furHex}"></span>
      <span class="nm">${h.name}</span><span class="st" data-k="calm">loafing</span>
      <span class="ebar"><i style="width:${Math.round(h.energy*100)}%"></i></span>`;
    li.addEventListener('click',()=>select(h));
    li.addEventListener('pointerenter',()=>h.hover=true);
    li.addEventListener('pointerleave',()=>h.hover=false);
    rosterEl.appendChild(li);
  });
  $('#sPop').textContent=hamsters.length;
}
let selected=null;
function select(h){
  hamsters.forEach(x=>{x.sel=false;x.tag.classList.remove('sel');});
  selected=h;
  const f=$('#focus');
  if(!h){f.innerHTML=`<h3>Nobody picked</h3><p>Click a hamster in the scene or the list to open its file.</p>`;
    bubble.classList.add('hide');}
  else{
    h.sel=true;h.tag.classList.add('sel');
    const t=h.traits;
    const chips=[t.energy>.65?'wheel maniac':t.energy<.35?'professional loafer':'steady walker',
      t.foodie>.6?'food-motivated':t.foodie<.35?'picky grazer':'seed appreciator',
      t.sleepy>.6?'champion napper':'early riser',t.curious>.6?'tunnel scientist':'cautious explorer']
      .map(c=>`<em>${c}</em>`).join('');
    f.innerHTML=`<h3>${h.name}</h3><p>Currently: <b data-f="act">loafing</b></p>
      <div class="tags">${chips}</div>
      <div class="nums"><span data-f="s">0 snacks</span><span data-f="d">0 m walked</span><span data-f="n">0 naps</span></div>`;
    focusPoint.set(h.pos.x,.9,h.pos.z);focusing=true;
  }
  [...rosterEl.children].forEach((li,i)=>li.classList.toggle('sel',hamsters[i]===h));
}
const bubble=$('#bubble'),focusPoint=new THREE.Vector3();let focusing=false;

/* dust motes (DOM) */
(function motes(){
  const c=$('#motes');
  for(let i=0;i<16;i++){const d=document.createElement('div');d.className='mote';
    d.style.left=rand(2,98)+'vw';d.style.top=rand(60,110)+'vh';
    d.style.animationDuration=rand(16,34)+'s';d.style.animationDelay=(-rand(0,20))+'s';
    d.style.transform=`scale(${rand(.5,1.5)})`;c.appendChild(d);}
})();

/* controls wiring */
let simSpeed=1,showTags=true;
$('#bSpin').onclick=()=>{W.wheel.spin+=7.5;addFeed('Somebody flicked the wheel. Chaos.','hot');};
$('#bFood').onclick=()=>W.refill();
$('#bTreat').onclick=()=>{for(let i=0;i<3;i++)W.spawnTreat(rand(-5,5),rand(-3,3));
  addFeed('Treats scattered. Emergency meeting called.','food');};
const doorBtn=$('#bDoor');
doorBtn.onclick=()=>{W.doorOpen=!W.doorOpen;doorBtn.setAttribute('aria-pressed',W.doorOpen);
  addFeed(W.doorOpen?'The door creaks open. Nobody escapes. Probably.':'Door shut. Containment: excellent.','calm');};
const nightBtn=$('#bNight');let nightTarget=0;
nightBtn.onclick=()=>{nightTarget=nightTarget?0:1;nightBtn.setAttribute('aria-pressed',!!nightTarget);
  addFeed(nightTarget?'Lights out. The wheel keeps ticking anyway.':'Sunrise. The crew is deeply offended.','sleep');};
const orbitBtn=$('#bOrbit');let autoOrbit=false;
orbitBtn.onclick=()=>{autoOrbit=!autoOrbit;orbitBtn.setAttribute('aria-pressed',autoOrbit);};
const tagsBtn=$('#bTags');
tagsBtn.onclick=()=>{showTags=!showTags;tagsBtn.setAttribute('aria-pressed',showTags);};
$('#bCam').onclick=()=>{camTarget.set(12.4,9.2,14.6);focusPoint.set(0,1.5,0);focusing=true;camEase=.03;};
let camTarget=null,camEase=0;
$('#rPop').oninput=e=>{const v=+e.target.value;$('#oPop').textContent=v;
  while(hamsters.length<v)addHamster();while(hamsters.length>v)removeHamster();};
$('#rSpeed').oninput=e=>{simSpeed=+e.target.value;$('#oSpeed').textContent=simSpeed.toFixed(1);};

addEventListener('keydown',e=>{
  if(e.code==='Space'){e.preventDefault();$('#bSpin').click();}
  if(e.key==='f'||e.key==='F')$('#bFood').click();
  if(e.key==='n'||e.key==='N')nightBtn.click();
  if(e.key==='r'||e.key==='R')$('#bCam').click();
});

/* picking */
const ray=new THREE.Raycaster(),ndc=new THREE.Vector2();
let down=null;
canvas.addEventListener('pointerdown',e=>{down={x:e.clientX,y:e.clientY,t:performance.now()};
  canvas.style.cursor='grabbing';focusing=false;});
canvas.addEventListener('pointerup',e=>{
  canvas.style.cursor='';
  if(!down)return;
  const moved=Math.hypot(e.clientX-down.x,e.clientY-down.y),dtm=performance.now()-down.t;down=null;
  if(moved>7||dtm>420)return;
  ndc.set((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);
  ray.setFromCamera(ndc,camera);
  const hs=hamsters.map(h=>h.group);
  let hit=ray.intersectObjects(hs,true)[0];
  if(hit){let g=hit.object;while(g.parent&&!g.parent.isScene)g=g.parent;
    const h=hamsters.find(x=>x.group===g);if(h){select(h);
      hamsters.forEach(o=>{if(o!==h&&o.pos.distanceTo(h.pos)<2.6&&o.state!=='sleep')
        {o.pos.add(new THREE.Vector3(rand(-1,1),0,rand(-1,1)).multiplyScalar(.6));o.enter('spook',rand(1.4,2.6));
         o.target=o.pos.clone();}});
      addFeed(`${h.name} was inspected and demands payment in seeds.`,'hot');return;}}
  hit=ray.intersectObject(W.wheel.group,true)[0];
  if(hit){W.wheel.spin+=6.5;addFeed('Wheel flicked. Free entertainment.','hot');return;}
  hit=ray.intersectObjects(scene.children.filter(o=>o.name==='floor'),false)[0]||
       ray.intersectObjects(scene.children.filter(o=>o.type==='Group'),true).find(h=>h.object.name==='floor');
  if(hit){const p=hit.point;W.spawnTreat(clamp(p.x,-5.4,5.4),clamp(p.z,-3.3,3.3));
    addFeed('A treat hit the bedding. Two hamsters are now athletes.','food');return;}
  // clicked empty space: deselect
  select(null);
});
canvas.addEventListener('pointermove',e=>{
  ndc.set((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);
  ray.setFromCamera(ndc,camera);
  const hs=hamsters.map(h=>h.group);
  const onSomething=ray.intersectObjects(hs,true)[0]||ray.intersectObject(W.wheel.group,true)[0];
  canvas.classList.toggle('pointing',!!onSomething);
});

/* ══════════════ loop ══════════════ */
const nightHemiC=new THREE.Color(0x2c3f7a),dayHemiC=new THREE.Color(0xbfe9ff);
const nightGndC=new THREE.Color(0x141d3a),dayGndC=new THREE.Color(0xffd6a0);
const nightFogC=new THREE.Color(0x050d1a),dayFogC=new THREE.Color(0x08191f);
let nightV=0,simTime=0,clockMin=9*60,uiT=0,bubbleT=0;
const nfEl=$('#nightfall'),tmpV=new THREE.Vector3();

function updateWheel(dt){
  const wm=W.wheel;
  const running=wm.runner&&wm.runner.state==='wheel'&&wm.runner.stateT>.6&&wm.runner.stateT<wm.runner.dur-.5;
  if(running)wm.spin=lerp(wm.spin,2.9,dt*1.6);
  else wm.spin*=Math.max(0,1-dt*.75);
  wm.spinner.rotation.z-=wm.spin*dt;
  wm.angle+=wm.spin*dt;wm.dist+=wm.spin*dt*1.17;
  if(wm.spin>.4&&Math.random()<dt*.35)addFeed(`The wheel ticks loudly (${Math.round(wm.spin*9.5)} rpm).`,'hot');
}
function updateDust(dt){
  const p=dust.geometry.attributes.position;
  for(let i=0;i<p.count;i++){
    let y=p.getY(i)+dt*.28;if(y>8.6)y=.3;
    p.setY(i,y);p.setX(i,p.getX(i)+Math.sin(simTime*.5+i)*dt*.09);
  }
  p.needsUpdate=true;
}
function updateBottle(dt){
  bottle.dripT-=dt;
  const d=bottle.drip;
  if(bottle.dripT<0){
    d.position.y-=dt*1.6;d.visible=true;
    if(d.position.y<1.25){d.position.y=1.95;bottle.dripT=rand(5,11);d.visible=false;}
  }else{d.position.y=1.95;d.visible=Math.random()<.5;}
}
function uiUpdate(){
  $('#sRpm').textContent=W.wheel.spin>.05?Math.round(W.wheel.spin*9.5):0;
  const snacks=hamsters.reduce((a,h)=>a+h.stats.snacks,0);
  $('#sSnacks').textContent=snacks;
  clockMin=(clockMin+1)%1440;
  $('#sClock').textContent=String(Math.floor(clockMin/60)).padStart(2,'0')+':'+String(Math.floor(clockMin%60)).padStart(2,'0');
  [...rosterEl.children].forEach((li,i)=>{
    const h=hamsters[i];if(!h)return;
    const lab=STATE_LABEL[h.state]||['loafing','calm'];
    const st=li.querySelector('.st');
    if(st.textContent!==lab[0]){st.textContent=lab[0];st.dataset.k=lab[1];}
    li.querySelector('.ebar i').style.width=Math.round(h.energy*100)+'%';
  });
  if(selected){
    const f=$('#focus');
    const lab=STATE_LABEL[selected.state]||['loafing','calm'];
    const a=f.querySelector('[data-f="act"]');if(a)a.textContent=lab[0];
    const s=f.querySelector('[data-f="s"]');if(s)s.textContent=selected.stats.snacks+' snacks';
    const d=f.querySelector('[data-f="d"]');if(d)d.textContent=Math.round(selected.stats.dist)+' m walked';
    const n=f.querySelector('[data-f="n"]');if(n)n.textContent=selected.stats.naps+' naps';
  }
}
function updateTags(){
  hamsters.forEach(h=>{
    const show=(showTags||h.sel)&&nightV<.85;
    tmpV.set(h.group.position.x,1.55,h.group.position.z).project(camera);
    const vis=show&&tmpV.z<1;
    h.tag.style.opacity=vis?(h.sel?1:.72):0;
    if(!vis)return;
    h.tag.style.transform=`translate(${(tmpV.x*.5+.5)*innerWidth}px,${(-tmpV.y*.5+.5)*innerHeight}px) translate(-50%,-130%) scale(${h.sel?1.16:1})`;
    h.tag.classList.toggle('sleep',h.state==='sleep');
    h.tag.textContent=h.state==='sleep'?'z z z':h.name;
  });
  if(selected){
    tmpV.set(selected.group.position.x,2.15,selected.group.position.z).project(camera);
    bubble.style.left=(tmpV.x*.5+.5)*innerWidth+'px';
    bubble.style.top=(-tmpV.y*.5+.5)*innerHeight+'px';
    bubble.classList.toggle('hide',tmpV.z>1);
  }
}
let last=performance.now();
function tick(now){
  requestAnimationFrame(tick);
  const raw=Math.min(.05,(now-last)/1000);last=now;
  simTime+=raw;const dt=raw*simSpeed;

  nightV=lerp(nightV,nightTarget,raw*1.6);
  hemi.intensity=lerp(.62,.2,nightV);
  hemi.color.copy(dayHemiC).lerp(nightHemiC,nightV);
  hemi.groundColor.copy(dayGndC).lerp(nightGndC,nightV);
  key.intensity=lerp(1.75,.3,nightV);
  fill.intensity=lerp(.4,.16,nightV);rim.intensity=lerp(.45,.5,nightV);
  lamp.intensity=lerp(0,2.1,nightV);bulbMat.emissiveIntensity=lerp(.08,2.4,nightV);
  scene.fog.color.copy(dayFogC).lerp(nightFogC,nightV);
  renderer.toneMappingExposure=lerp(1.06,.98,nightV);
  nfEl.style.opacity=(nightV*.9).toFixed(3);
  W.night=nightV;
  key.position.x=9+Math.sin(simTime*.14)*1.6;key.position.z=7+Math.cos(simTime*.11)*1.4;

  updateWheel(dt);
  for(const h of hamsters)h.update(dt);
  W.treats.forEach(t=>{t.mesh.rotation.y+=dt*1.2;t.spin+=dt;});
  updateBottle(raw);updateDust(raw);

  doorPivot.rotation.y=lerp(doorPivot.rotation.y,W.doorOpen?-1.95:0,raw*3.2);
  bulbG.position.x=Math.sin(simTime*.5)*.06;

  hamsters.forEach(h=>{
    const want=(h.sel?1:0)+(h.hover?.55:0);
    h.ring.material.opacity=lerp(h.ring.material.opacity,want*.9,raw*7);
    const s=h.sel?1+Math.sin(simTime*3.4)*.03:h.hover?1.05:1;
    h.rig.scale.x=lerp(h.rig.scale.x,s,raw*8);
    h.furMat.emissive=new THREE.Color(h.hover||h.sel?0x3a2408:0x000000);
  });

  if(camTarget){camera.position.lerp(camTarget,raw*3.2);camEase+=raw;if(camEase>1.2){camTarget=null;}}
  if(focusing){controls.target.lerp(focusPoint,raw*3.4);
    if(controls.target.distanceTo(focusPoint)<.06)focusing=false;}
  controls.autoRotate=autoOrbit&&!selected;
  controls.update();
  updateTags();

  bubbleT-=raw;
  if(selected&&bubbleT<0){bubbleT=4.2;
    const arr=LINES[selected.state]||LINES.idle;
    bubble.textContent=pick(arr);}

  uiT+=raw;if(uiT>.16){uiT=0;uiUpdate();}
  renderer.render(scene,camera);
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* ══════════════ boot ══════════════ */
const bootBar=$('#bootBar'),bootMsg=$('#bootMsg');
const msgs=['bedding the tray…','bending 84 bars…','oiling the wheel…','naming the round ones…','hiding seeds…'];
let bp=0;
(function boot(){
  const iv=setInterval(()=>{
    bp=Math.min(100,bp+rand(9,22));
    bootBar.style.width=bp+'%';bootMsg.textContent=msgs[Math.min(msgs.length-1,Math.floor(bp/21))];
    if(bp>=100){clearInterval(iv);
      setTimeout(()=>{$('#boot').classList.add('gone');setTimeout(()=>$('#boot').remove(),800);},340);}
  },170);
})();

W.refill();
for(let i=0;i<6;i++)addHamster();
select(null);
addFeed('Habitat online. Six hamsters, one wheel, zero supervision.','calm');
setTimeout(()=>{const h=hamsters[0];if(h){h.goWheel();}},2400);
requestAnimationFrame(tick);
</script>
</body>
</html>
```

**What's in the box**

- **Cage**: 84 instanced bars + tangerine posts, lid bars, a hinged front door that swings open, and a dripping water bottle.
- **Tray**: mint plastic tub with a lip, bedding plane, mounded substrate and ~460 instanced wood shavings in five tones.
- **Interactive objects**: a spoked running wheel (flick it with the button, a click, or `space` — hamsters climb in and drive it, and it coasts down with friction), a lathe-turned seed bowl with a real food count, a cardboard tunnel hamsters get launched out of, a hut they nap in, and treats you drop by clicking the bedding (the two nearest hamsters turn into athletes).
- **Autonomy**: each hamster has personality weights (`energy`, `foodie`, `sleepy`, `curious`), an energy budget, obstacle repulsion steering, and states — exploring, sniffing, grooming, loafing, wheel-running, eating, drinking, tunnel-transit, sleep (curled, eyes shut, `z z z` tag), and spook-zoomies when you poke a neighbour.
- **Living HUD**: field guide with live state chips and energy bars, cage-chatter log, telemetry strip, projected name tags, speech bubbles, day→night lighting with a hanging bulb, drifting 3D dust, sweeping background light, and keyboard shortcuts.