# Tidehaven

A single-file, fully procedural WebGL diorama. Everything below is `index.html` — save it and open it in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Tidehaven — a coastal island diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,500;9..144,700;9..144,900&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* ============================================================
   TIDEHAVEN — interface styling
   ============================================================ */
:root{
  --ink:#06171c;
  --ink2:#0d2830;
  --cream:#f7eddc;
  --sand:#e8d5ad;
  --copper:#e08a4c;
  --verd:#5fd3c0;
  --deep:#0a4b57;
  --panel:rgba(7,26,32,.70);
  --panel2:rgba(9,32,39,.82);
  --stroke:rgba(247,237,220,.13);
  --stroke2:rgba(247,237,220,.26);
  --shadow:0 22px 50px -26px rgba(0,0,0,.9), inset 0 1px 0 rgba(255,255,255,.07);
  --r:15px;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;margin:0;overflow:hidden;background:#05141a;color:var(--cream);
  font-family:'Outfit',system-ui,sans-serif;font-weight:300;letter-spacing:.005em;
  -webkit-font-smoothing:antialiased}
canvas#scene{position:fixed;inset:0;display:block;touch-action:none}

/* underwater haze overlay (driven by JS) */
#haze{position:fixed;inset:0;pointer-events:none;opacity:0;transition:opacity .9s ease;
  background:
    radial-gradient(120% 90% at 50% 8%, rgba(150,255,240,.20), transparent 60%),
    linear-gradient(180deg, rgba(18,120,128,.42) 0%, rgba(6,60,74,.62) 55%, rgba(3,32,44,.78) 100%);
  mix-blend-mode:multiply}
#haze::after{content:"";position:absolute;inset:-20%;opacity:.28;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(190,255,250,.5) 0 2px, transparent 3px),
    radial-gradient(circle at 70% 60%, rgba(190,255,250,.4) 0 3px, transparent 4px),
    radial-gradient(circle at 45% 80%, rgba(190,255,250,.35) 0 2px, transparent 3px),
    radial-gradient(circle at 85% 20%, rgba(190,255,250,.3) 0 2px, transparent 3px);
  background-size:340px 340px, 520px 520px, 420px 420px, 600px 600px;
  animation:drift 26s linear infinite;filter:blur(2px)}
@keyframes drift{to{transform:translate3d(-120px,90px,0) rotate(3deg)}}

/* vignette + grain */
#vig{position:fixed;inset:0;pointer-events:none;
  background:radial-gradient(120% 100% at 50% 42%, transparent 42%, rgba(2,12,16,.55) 100%)}

/* ---------- HUD layout ---------- */
.hud{position:fixed;inset:0;pointer-events:none;display:grid;
  grid-template-columns:minmax(230px,1fr) auto;
  grid-template-rows:auto 1fr auto;
  padding:clamp(14px,2.2vw,28px);gap:14px;z-index:10}

.brand{grid-column:1;grid-row:1;display:flex;gap:14px;align-items:flex-start;
  animation:rise .9s .15s cubic-bezier(.2,.85,.25,1) both}
.brand .mark{width:44px;height:44px;flex:none;border-radius:13px;position:relative;overflow:hidden;
  background:linear-gradient(155deg,#12414c,#06222b);border:1px solid var(--stroke2);
  box-shadow:var(--shadow)}
.brand .mark::before{content:"";position:absolute;inset:0;
  background:
    radial-gradient(60% 40% at 50% 78%, #e8d5ad 0 60%, transparent 61%),
    radial-gradient(140% 40% at 50% 62%, rgba(95,211,192,.95) 0 100%, transparent 100%);
  animation:swelltide 5.5s ease-in-out infinite}
@keyframes swelltide{0%,100%{transform:translateY(3px)}50%{transform:translateY(-3px)}}
.brand h1{margin:0;font-family:'Fraunces',Georgia,serif;font-weight:300;
  font-size:clamp(30px,4.4vw,50px);line-height:.92;letter-spacing:-.022em;
  text-shadow:0 10px 30px rgba(0,0,0,.55)}
.brand h1 b{font-weight:900}
.brand p{margin:7px 0 0;font-size:12.5px;line-height:1.45;max-width:34ch;
  color:rgba(247,237,220,.62);letter-spacing:.045em;text-transform:uppercase;font-weight:400}
.brand .tag{display:inline-flex;gap:7px;align-items:center;margin-top:9px;font-size:11px;
  color:var(--verd);letter-spacing:.14em;text-transform:uppercase}
.brand .dot{width:6px;height:6px;border-radius:50%;background:var(--verd);
  box-shadow:0 0 0 0 rgba(95,211,192,.6);animation:pulse 2.6s infinite}
@keyframes pulse{70%{box-shadow:0 0 0 9px rgba(95,211,192,0)}100%{box-shadow:0 0 0 0 rgba(95,211,192,0)}}

.sheets{grid-column:2;grid-row:1/4;display:flex;flex-direction:column;gap:11px;
  width:282px;align-self:center;justify-content:center;pointer-events:none;
  max-height:100%;overflow:auto;padding-bottom:2px;scrollbar-width:thin;
  scrollbar-color:rgba(247,237,220,.2) transparent}
.sheets::-webkit-scrollbar{width:5px}
.sheets::-webkit-scrollbar-thumb{background:rgba(247,237,220,.18);border-radius:9px}

.panel{pointer-events:auto;background:var(--panel);backdrop-filter:blur(18px) saturate(1.45);
  -webkit-backdrop-filter:blur(18px) saturate(1.45);border:1px solid var(--stroke);
  border-radius:var(--r);padding:13px 14px 15px;box-shadow:var(--shadow);
  animation:rise .85s cubic-bezier(.2,.85,.25,1) both;transition:border-color .3s,transform .3s}
.panel:hover{border-color:var(--stroke2)}
.sheets .panel:nth-child(1){animation-delay:.22s}
.sheets .panel:nth-child(2){animation-delay:.30s}
.sheets .panel:nth-child(3){animation-delay:.38s}
.sheets .panel:nth-child(4){animation-delay:.46s}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}

.plabel{display:flex;align-items:center;justify-content:space-between;gap:8px;
  font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:rgba(247,237,220,.5);
  font-weight:500;margin:0 0 11px}
.plabel::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--stroke2),transparent)}
.plabel i{font-style:normal;color:var(--copper)}

/* buttons */
.btn{appearance:none;border:1px solid var(--stroke);background:rgba(247,237,220,.045);
  color:var(--cream);font-family:'Outfit',sans-serif;font-weight:400;font-size:12.5px;
  padding:9px 11px;border-radius:10px;cursor:pointer;display:flex;align-items:center;gap:8px;
  justify-content:center;position:relative;overflow:hidden;transition:.22s cubic-bezier(.2,.9,.2,1);
  letter-spacing:.01em}
.btn:hover{background:rgba(247,237,220,.10);border-color:var(--stroke2);transform:translateY(-1px)}
.btn:active{transform:translateY(0) scale(.985)}
.btn .k{font-size:9.5px;opacity:.42;border:1px solid var(--stroke);border-radius:4px;
  padding:1px 4px;letter-spacing:.06em}
.btn[aria-pressed="true"]{background:linear-gradient(160deg,#f0a05c,#cf6f34);
  color:#231007;border-color:transparent;font-weight:500;
  box-shadow:0 10px 22px -12px rgba(224,138,76,.95), inset 0 1px 0 rgba(255,255,255,.35)}
.btn[aria-pressed="true"] .k{opacity:.5;border-color:rgba(35,16,7,.3)}
.btn.sea[aria-pressed="true"]{background:linear-gradient(160deg,#79e6d2,#26a795);color:#04231f;
  box-shadow:0 10px 22px -12px rgba(95,211,192,.9), inset 0 1px 0 rgba(255,255,255,.35)}
.btn .ico{width:15px;height:15px;flex:none;opacity:.9}
.btn.big{padding:11px 12px;font-size:13px}
.row{display:grid;gap:7px}
.row.c2{grid-template-columns:1fr 1fr}
.row.c3{grid-template-columns:repeat(3,1fr)}
.row.c4{grid-template-columns:repeat(4,1fr)}

.seg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:4px;
  background:rgba(0,0,0,.24);border-radius:11px;border:1px solid rgba(0,0,0,.25)}
.seg button{padding:7px 4px;font-size:11.5px;border-radius:8px}

/* sliders */
.sl{margin:12px 0 2px}
.sl .top{display:flex;justify-content:space-between;align-items:baseline;
  font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:rgba(247,237,220,.62)}
.sl .val{font-family:'Fraunces',serif;font-size:15px;font-weight:500;color:var(--sand);
  letter-spacing:0;font-variant-numeric:tabular-nums}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:22px;background:transparent;
  cursor:pointer;margin:2px 0 0;display:block}
input[type=range]::-webkit-slider-runnable-track{height:5px;border-radius:99px;
  background:linear-gradient(90deg,var(--copper) var(--p,50%),rgba(247,237,220,.14) var(--p,50%))}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;
  background:radial-gradient(circle at 34% 30%,#fff8ea,#e3b184 60%,#a86a3c);margin-top:-5.5px;
  box-shadow:0 3px 10px rgba(0,0,0,.6),0 0 0 1px rgba(0,0,0,.35);transition:transform .18s}
input[type=range]:hover::-webkit-slider-thumb{transform:scale(1.16)}
input[type=range]::-moz-range-track{height:5px;border-radius:99px;background:rgba(247,237,220,.14)}
input[type=range]::-moz-range-progress{height:5px;border-radius:99px;background:var(--copper)}
input[type=range]::-moz-range-thumb{width:15px;height:15px;border:none;border-radius:50%;
  background:#f0c79c;box-shadow:0 3px 10px rgba(0,0,0,.6)}
.sea input[type=range]::-webkit-slider-runnable-track{
  background:linear-gradient(90deg,var(--verd) var(--p,50%),rgba(247,237,220,.14) var(--p,50%))}
.sea input[type=range]::-webkit-slider-thumb{background:radial-gradient(circle at 34% 30%,#eafffb,#5fd3c0 55%,#1d7f74)}

/* ticker + hints */
.ticker{grid-column:1;grid-row:3;display:flex;flex-wrap:wrap;gap:7px;align-items:center;
  pointer-events:none;animation:rise 1s .55s cubic-bezier(.2,.85,.25,1) both}
.chip{pointer-events:auto;display:inline-flex;gap:7px;align-items:center;font-size:11px;
  letter-spacing:.08em;text-transform:uppercase;padding:6px 10px;border-radius:99px;
  background:rgba(6,22,28,.6);backdrop-filter:blur(12px);border:1px solid var(--stroke);
  color:rgba(247,237,220,.72);transition:.25s}
.chip b{font-weight:500;color:var(--sand);font-variant-numeric:tabular-nums;letter-spacing:.02em}
.chip.on{border-color:rgba(95,211,192,.5);color:#c9fff3}
.hints{grid-column:1/-1;grid-row:3;justify-self:end;align-self:end;text-align:right;
  font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:rgba(247,237,220,.34);
  line-height:1.7;pointer-events:none;animation:rise 1s .7s both}
.hints kbd{font-family:'Outfit';color:rgba(247,237,220,.6)}

/* mobile menu button */
#menuBtn{display:none;position:fixed;right:12px;top:12px;z-index:30;pointer-events:auto;
  width:46px;height:46px;border-radius:14px;background:var(--panel2);border:1px solid var(--stroke2);
  backdrop-filter:blur(14px);color:var(--cream);cursor:pointer;align-items:center;justify-content:center}
#menuBtn svg{width:20px;height:20px}

/* boot */
#boot{position:fixed;inset:0;z-index:60;background:radial-gradient(120% 90% at 50% 30%,#0d3340,#03151b 70%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;
  transition:opacity .9s ease,visibility .9s}
#boot.gone{opacity:0;visibility:hidden}
#boot h2{font-family:'Fraunces',serif;font-weight:300;font-size:clamp(34px,7vw,64px);margin:0;
  letter-spacing:-.02em}
#boot h2 b{font-weight:900}
#boot .tide{width:min(300px,60vw);height:3px;border-radius:9px;background:rgba(247,237,220,.12);overflow:hidden}
#boot .tide i{display:block;height:100%;width:40%;border-radius:9px;
  background:linear-gradient(90deg,transparent,#5fd3c0,#e8d5ad,transparent);animation:sweep 1.5s ease-in-out infinite}
@keyframes sweep{0%{transform:translateX(-120%)}100%{transform:translateX(320%)}}
#boot small{font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:rgba(247,237,220,.45)}

@media (max-width:900px){
  .hud{grid-template-columns:1fr;grid-template-rows:auto 1fr auto;padding:12px;gap:8px}
  .brand{grid-column:1;grid-row:1}
  .brand p{max-width:24ch}
  .hints{display:none}
  .ticker{grid-row:3;grid-column:1;justify-self:start;bottom:12px}
  #menuBtn{display:flex}
  .sheets{position:fixed;left:10px;right:10px;bottom:62px;width:auto;grid-row:auto;
    max-height:min(56vh,460px);z-index:25;padding-right:2px;
    transform:translateY(calc(100% + 90px));opacity:0;pointer-events:none;
    transition:transform .5s cubic-bezier(.2,.9,.2,1),opacity .4s}
  body.menu-open .sheets{transform:none;opacity:1;pointer-events:auto}
  .sheets .panel{animation:none}
}
@media (max-width:420px){ .brand h1{font-size:29px} .brand .mark{width:38px;height:38px} }
</style>
</head>
<body>

<canvas id="scene"></canvas>
<div id="haze"></div>
<div id="vig"></div>

<button id="menuBtn" aria-label="Toggle controls">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
    <path d="M4 8h16M4 16h16"/></svg>
</button>

<div class="hud">
  <header class="brand">
    <div class="mark" aria-hidden="true"></div>
    <div>
      <h1>Tide<b>haven</b></h1>
      <p>A single island, sawn cleanly in half — the tide working, the rays below.</p>
      <span class="tag"><span class="dot"></span><span id="statusWord">the tide is turning</span></span>
    </div>
  </header>

  <div class="sheets" id="sheets">

    <section class="panel">
      <p class="plabel">View <i id="viewName">Island</i></p>
      <div class="row c3">
        <button class="btn cam" data-view="island" aria-pressed="true"><span class="k">1</span>Island</button>
        <button class="btn cam" data-view="cabin"  aria-pressed="false"><span class="k">2</span>Cabin</button>
        <button class="btn cam" data-view="under"  aria-pressed="false"><span class="k">3</span>Below</button>
      </div>
      <div class="row" style="margin-top:9px">
        <div class="seg" role="group" aria-label="Quality">
          <button class="btn q" data-q="low"  aria-pressed="false">Low</button>
          <button class="btn q" data-q="med"  aria-pressed="false">Medium</button>
          <button class="btn q" data-q="high" aria-pressed="true">High</button>
        </div>
      </div>
    </section>

    <section class="panel sea">
      <p class="plabel">World</p>
      <div class="sl">
        <div class="top"><span>Tide</span><span class="val" id="tideVal">+0.02 m</span></div>
        <input id="tide" type="range" min="-42" max="46" value="2" step="1" aria-label="Tide level">
      </div>
      <div class="sl">
        <div class="top"><span>Wind</span><span class="val" id="windVal">45%</span></div>
        <input id="wind" type="range" min="0" max="100" value="45" step="1" aria-label="Wind strength">
      </div>
      <div class="sl" style="margin-bottom:2px">
        <div class="top" style="margin-bottom:6px"><span>Hour</span></div>
        <div class="seg" role="group" aria-label="Time of day">
          <button class="btn tod" data-tod="day"    aria-pressed="true">Day</button>
          <button class="btn tod" data-tod="sunset" aria-pressed="false">Sunset</button>
          <button class="btn tod" data-tod="night"  aria-pressed="false">Night</button>
        </div>
      </div>
    </section>

    <section class="panel">
      <p class="plabel">Activity</p>
      <div class="row">
        <button class="btn big sea" id="btnKayak" aria-pressed="false">
          <svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path d="M2 15c4-1.5 16-1.5 20 0-2.6 3-6 4.4-10 4.4S4.6 18 2 15Z"/><path d="M6 11.5 18 5.5"/></svg>
          <span id="kayakLabel">Launch kayak</span><span class="k">K</span>
        </button>
        <button class="btn big" id="btnRay">
          <svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path d="M2 13c3.5-4 8.5-5.5 13-4.4M22 12c-2.4 2.6-5.4 4-9 4.3"/><path d="M15 8.6 21 4M15 8.6 21 13"/></svg>
          <span>Send a ray leaping</span><span class="k">R</span>
        </button>
      </div>
      <div class="row c2" style="margin-top:7px">
        <button class="btn" id="btnPause" aria-pressed="false"><span class="k">␣</span><span id="pauseLabel">Pause</span></button>
        <button class="btn" id="btnReset"><span class="k">T</span>Reset</button>
      </div>
    </section>

    <section class="panel">
      <p class="plabel">Sound</p>
      <div class="row c2">
        <button class="btn" id="btnSound" aria-pressed="false">
          <svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path d="M4 9.5h3.2L12 5.6v12.8L7.2 14.5H4z"/><path d="M16 9.2a4 4 0 0 1 0 5.6M18.6 6.6a7.6 7.6 0 0 1 0 10.8"/></svg>
          <span id="soundLabel">Sound on</span></button>
        <button class="btn" id="btnMusic" aria-pressed="true"><span class="k">M</span>Music</button>
      </div>
      <div class="sl" style="margin-bottom:0">
        <div class="top"><span>Volume</span><span class="val" id="volVal">55%</span></div>
        <input id="vol" type="range" min="0" max="100" value="55" step="1" aria-label="Volume">
      </div>
    </section>
  </div>

  <footer class="ticker">
    <span class="chip">Tide <b id="cTide">+0.02</b></span>
    <span class="chip">Wind <b id="cWind">45%</b></span>
    <span class="chip">Light <b id="cTod">Day</b></span>
    <span class="chip" id="cKayak">Kayak <b>moored</b></span>
    <span class="chip" id="cRay">Rays <b>gliding</b></span>
    <span class="chip" id="cFps">— fps</span>
  </footer>

  <div class="hints">
    drag to orbit · scroll to zoom<br>
    <kbd>1 2 3</kbd> views · <kbd>space</kbd> pause · <kbd>k</kbd> kayak · <kbd>r</kbd> ray · <kbd>t</kbd> reset
  </div>
</div>

<div id="boot">
  <h2>Tide<b>haven</b></h2>
  <div class="tide"><i></i></div>
  <small>filling the lagoon…</small>
</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import * as BGU from 'three/addons/utils/BufferGeometryUtils.js';

/* ============================================================================
   0 · CONSTANTS & STATE
   ========================================================================== */
const TW = 11.2, TD = 9.0;            // tank width (x) / depth (z)
const FLOOR = -2.35, RIM = 3.30;      // tank floor / rim height
const CABIN = new THREE.Vector2(-1.05, -0.75);
const PAD_Y = 1.58;                   // flattened pad height for the cabin
const PIER_A = new THREE.Vector2(1.50, 1.40);
const PIER_B = new THREE.Vector2(1.98, 4.28);
const DECK_Y = 0.78;
const TIDE_MIN = -0.42, TIDE_MAX = 0.46;

const S = {
  t: 0, paused: false,
  tide: 0.02, tideTarget: 0.02,
  wind: 0.45, windTarget: 0.45,
  tod: 'day',
  quality: 'high',
  kayakMode: 'dock', kayakU: 0, kayakVel: 0,
  leaping: false,
  view: 'island',
  audioOn: false, musicOn: true, vol: 0.55
};

const QUALITY = {
  low : { dpr:1.0, shadow:1024, g:[80,64],  wseg:56,  grass:230, kelp:45,  bubbles:34, fish:16, gulls:2 },
  med : { dpr:1.35,shadow:1536, g:[112,90], wseg:88,  grass:430, kelp:80,  bubbles:60, fish:24, gulls:3 },
  high: { dpr:1.8, shadow:2048, g:[150,120],wseg:128, grass:700, kelp:120, bubbles:96, fish:34, gulls:4 }
};

/* ============================================================================
   1 · MATH / NOISE HELPERS
   ========================================================================== */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const smoothstep=(e0,e1,x)=>{const t=clamp((x-e0)/(e1-e0),0,1);return t*t*(3-2*t);};
const damp=(a,b,l,dt)=>lerp(a,b,1-Math.exp(-l*dt));
function mulberry(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const RNG = mulberry(20240611);
const rnd=(a=1,b=0)=>b+RNG()*(a-b);

function jhash(x,y){const s=Math.sin(x*127.1+y*311.7)*43758.5453;return s-Math.floor(s);}
function jnoise(x,y){
  const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi;
  const u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf);
  return lerp(lerp(jhash(xi,yi),jhash(xi+1,yi),u),lerp(jhash(xi,yi+1),jhash(xi+1,yi+1),u),v);
}

/** Island elevation — the SAME function is compiled into GLSL (see GLSL_ISLAND).
 *  It drives terrain, waterline clipping, foam, prop placement and ray steering. */
function islandHeight(x,z){
  const r=Math.hypot(x,z), a=Math.atan2(z,x);
  const shp=1+0.15*Math.sin(3*a+0.6)+0.09*Math.sin(5*a-2.1)+0.05*Math.sin(2*a+1.3);
  const t=r/(3.85*shp);
  let h=3.30*(1-smoothstep(0.08,1.10,t));
  h+=0.34*Math.sin(x*1.7+0.4)*Math.cos(z*1.5-0.2)*(1-smoothstep(0.55,1.30,t));
  h+=0.17*Math.sin(x*3.4-1.1)*Math.sin(z*3.9+0.8)*(1-smoothstep(0.35,1.05,t));
  h-=0.50*smoothstep(0.60,1.02,t);
  h-=1.72;
  const d=Math.hypot(x-CABIN.x,z-CABIN.y);
  const pad=(1-smoothstep(0.85,1.95,d))*0.92;
  h=lerp(h,PAD_Y,pad);
  return h;
}
const slopeAt=(x,z)=>{const e=0.16;
  return Math.hypot(islandHeight(x+e,z)-islandHeight(x-e,z),islandHeight(x,z+e)-islandHeight(x,z-e))/(2*e);};

/** CPU twin of the GPU wave sum — keeps floating props glued to the rendered surface. */
function waveH(x,z,t,amp){
  let h=0;
  h+=Math.sin(x*1.9+t*1.5)*0.30;
  h+=Math.sin(z*2.3-t*1.8)*0.26;
  h+=Math.sin((x*0.8+z*1.4)+t*2.4)*0.20;
  h+=Math.sin((x*3.7-z*2.9)+t*3.6)*0.10*amp;
  h+=Math.sin((x*7.1+z*6.3)-t*5.2)*0.035;
  return h*amp;
}
const waveAmp=()=>0.028+S.wind*0.075;

/* ============================================================================
   2 · SHADER SNIPPETS
   ========================================================================== */
const GLSL_ISLAND = /* glsl */`
  float islandHeight(vec2 p){
    float r = length(p);
    float a = atan(p.y, p.x);
    float shp = 1.0 + 0.15*sin(3.0*a+0.6) + 0.09*sin(5.0*a-2.1) + 0.05*sin(2.0*a+1.3);
    float t = r/(3.85*shp);
    float h = 3.30*(1.0 - smoothstep(0.08,1.10,t));
    h += 0.34*sin(p.x*1.7+0.4)*cos(p.y*1.5-0.2)*(1.0-smoothstep(0.55,1.30,t));
    h += 0.17*sin(p.x*3.4-1.1)*sin(p.y*3.9+0.8)*(1.0-smoothstep(0.35,1.05,t));
    h -= 0.50*smoothstep(0.60,1.02,t);
    h -= 1.72;
    float d = length(p - vec2(${CABIN.x.toFixed(2)}, ${CABIN.y.toFixed(2)}));
    float pad = (1.0 - smoothstep(0.85,1.95,d))*0.92;
    h = mix(h, ${PAD_Y.toFixed(2)}, pad);
    return h;
  }`;

const GLSL_NOISE = /* glsl */`
  float hash21(vec2 p){ p = fract(p*vec2(233.34,851.73)); p += dot(p,p+23.45); return fract(p.x*p.y); }
  float vnoise(vec2 p){
    vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
    float a=hash21(i), b=hash21(i+vec2(1,0)), c=hash21(i+vec2(0,1)), d=hash21(i+vec2(1,1));
    return mix(mix(a,b,f.x), mix(c,d,f.x), f.y);
  }
  float fbm(vec2 p){ float s=0.0,a=0.5; for(int i=0;i<4;i++){ s+=a*vnoise(p); p*=2.03; a*=0.5;} return s; }`;

const GLSL_CAUSTIC = /* glsl */`
  float caustic(vec2 p, float t){
    vec2 i = p; float c = 1.0; const float inten = 0.0045;
    for(int n=0;n<3;n++){
      float tt = t*(1.0-(3.5/float(n+1)));
      i = i + vec2(cos(tt-i.x)+sin(tt+i.y), sin(tt-i.y)+cos(tt+i.x));
      c += 1.0/max(0.001, length(vec2(p.x/(sin(i.x+tt)/inten), p.y/(cos(i.y+tt)/inten))));
    }
    c /= 3.0; c = 1.17-pow(clamp(c,0.0,1.4),1.4);
    return clamp(pow(abs(c),8.0),0.0,3.0);
  }`;

const GLSL_WAVE = /* glsl */`
  float waveH(vec2 p, float t, float amp){
    float h = 0.0;
    h += sin(p.x*1.9 + t*1.5)*0.30;
    h += sin(p.y*2.3 - t*1.8)*0.26;
    h += sin((p.x*0.8+p.y*1.4) + t*2.4)*0.20;
    h += sin((p.x*3.7-p.y*2.9) + t*3.6)*0.10*amp;
    h += sin((p.x*7.1+p.y*6.3) - t*5.2)*0.035;
    return h*amp;
  }`;

/* Shared uniforms — one object referenced by every material. */
const U = {
  uTime:{value:0}, uWindV:{value:0.45}, uWaveE:{value:1.0}, uWater:{value:0.02},
  uSunDir:{value:new THREE.Vector3(0.55,0.72,0.42).normalize()},
  uSunCol:{value:new THREE.Color('#fff1d6')},
  uShallow:{value:new THREE.Color('#57d6c6')},
  uDeep:{value:new THREE.Color('#0a5060')},
  uSky:{value:new THREE.Color('#cfe8f0')},
  uLightMix:{value:1.0}, uNight:{value:0.0}, uLamp:{value:0.0}
};

/* ============================================================================
   3 · RENDERER / SCENE / CAMERA
   ========================================================================== */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, powerPreference:'high-performance'});
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setPixelRatio(Math.min(window.devicePixelRatio, QUALITY.high.dpr));

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(33, innerWidth/innerHeight, 0.1, 220);
camera.position.set(9.6,7.4,11.2);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.055;
controls.target.set(0,0.15,0);
controls.minDistance = 4.5; controls.maxDistance = 34;
controls.minPolarAngle = 0.12; controls.maxPolarAngle = 1.60;
controls.enablePan = false;

if (matchMedia('(pointer:coarse)').matches) S.quality = 'med';

/* ============================================================================
   4 · SKY DOME + TABLE
   ========================================================================== */
const skyMat = new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false,
  uniforms:{
    uZenith:U.uSky, uHorizon:{value:new THREE.Color('#e6f2f4')},
    uBelow:{value:new THREE.Color('#233238')},
    uSunDir:U.uSunDir, uSunCol:U.uSunCol, uNight:U.uNight, uTime:U.uTime
  },
  vertexShader:`varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`
    uniform vec3 uZenith,uHorizon,uBelow,uSunDir,uSunCol; uniform float uNight,uTime; varying vec3 vD;
    float h31(vec3 p){ p=fract(p*0.3183099+vec3(.11,.17,.13)); p*=17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
    void main(){
      float y = vD.y;
      vec3 c = mix(uHorizon, uZenith, pow(smoothstep(0.02,0.85,y),0.75));
      c = mix(c, uBelow, smoothstep(0.02,-0.30,y));
      float sd = max(dot(vD, normalize(uSunDir)),0.0);
      c += uSunCol*pow(sd,300.0)*2.6*(1.0-uNight*0.7);
      c += uSunCol*pow(sd,9.0)*0.22*(1.0-uNight*0.8);
      if(uNight>0.01 && y>-0.02){
        vec3 g=vD*150.0; vec3 id=floor(g); vec3 f=fract(g)-0.5;
        float n=h31(id);
        float st = n>0.9955 ? smoothstep(0.16,0.0,length(f)) : 0.0;
        st *= 0.55+0.45*sin(uTime*1.7+n*60.0);
        c += vec3(0.85,0.92,1.0)*st*uNight*smoothstep(-0.02,0.28,y);
      }
      gl_FragColor=vec4(c,1.0);
    }`
});
const sky = new THREE.Mesh(new THREE.SphereGeometry(80,32,20), skyMat);
sky.renderOrder = -10; scene.add(sky);

/* wooden table the diorama rests on */
const tableMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false,
  uniforms:{ uLightMix:U.uLightMix, uSky:U.uSky },
  vertexShader:`varying vec2 vP; void main(){ vP=position.xz; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`
    varying vec2 vP; uniform float uLightMix; uniform vec3 uSky;
    void main(){
      float r = length(vP*vec2(0.82,1.0));
      float pl = 0.5+0.5*sin(vP.x*7.0+sin(vP.y*1.3)*1.4);
      vec3 wood = mix(vec3(0.16,0.10,0.075), vec3(0.24,0.155,0.105), pl*0.6);
      float a = (1.0-smoothstep(5.0,13.0,r))*0.92;
      vec3 c = mix(wood, uSky*0.20, smoothstep(4.0,11.0,r));
      c *= (0.35+0.65*uLightMix);
      gl_FragColor=vec4(c,a);
    }`
});
const table = new THREE.Mesh(new THREE.PlaneGeometry(34,30), tableMat);
table.rotation.x = -Math.PI/2; table.position.y = FLOOR-0.62; table.renderOrder=-8;
scene.add(table);

/* ============================================================================
   5 · LIGHTS
   ========================================================================== */
const hemi = new THREE.HemisphereLight('#bfe6f2','#7d6a4d',0.85); scene.add(hemi);
const amb  = new THREE.AmbientLight('#ffffff',0.22); scene.add(amb);
const sun  = new THREE.DirectionalLight('#fff1d6',2.5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-7.4; sun.shadow.camera.right=7.4;
sun.shadow.camera.top=7.4; sun.shadow.camera.bottom=-7.4;
sun.shadow.camera.near=2; sun.shadow.camera.far=48;
sun.shadow.bias=-0.0008; sun.shadow.normalBias=0.022; sun.shadow.radius=2.4;
scene.add(sun); scene.add(sun.target);
/* cool bounce from the lagoon, no shadow */
const bounce = new THREE.DirectionalLight('#7fe3d6',0.35);
bounce.position.set(-2,-6,3); scene.add(bounce);
/* cabin + lantern lamps */
const lampLight = new THREE.PointLight('#ffb268',0,7,2.0); lampLight.position.set(CABIN.x,PAD_Y+0.85,CABIN.y); scene.add(lampLight);
const pierLight = new THREE.PointLight('#ffc07a',0,6,2.0); pierLight.position.set(PIER_B.x,DECK_Y+0.55,PIER_B.y-0.5); scene.add(pierLight);
const pierLight2= new THREE.PointLight('#ffb46a',0,5,2.0); pierLight2.position.set(PIER_A.x+0.5,DECK_Y+0.5,PIER_A.y+1.0); scene.add(pierLight2);

/* ============================================================================
   6 · MATERIAL LIBRARY
   ========================================================================== */
const M = {
  wood:   new THREE.MeshStandardMaterial({color:'#8a5a33',roughness:.78,metalness:.02}),
  woodLt: new THREE.MeshStandardMaterial({color:'#b07c48',roughness:.72}),
  woodDk: new THREE.MeshStandardMaterial({color:'#4d3320',roughness:.85}),
  stone:  new THREE.MeshStandardMaterial({color:'#7c7568',roughness:.94,flatShading:true}),
  rock:   new THREE.MeshStandardMaterial({color:'#6f6a60',roughness:.95,flatShading:true}),
  copper: new THREE.MeshStandardMaterial({color:'#c2703c',roughness:.34,metalness:.85}),
  verd:   new THREE.MeshStandardMaterial({color:'#4e9b86',roughness:.55,metalness:.35}),
  cloth:  new THREE.MeshStandardMaterial({color:'#f2e6d0',roughness:.95}),
  cloth2: new THREE.MeshStandardMaterial({color:'#d9745c',roughness:.95}),
  leaf:   new THREE.MeshStandardMaterial({color:'#4c7a3c',roughness:.9}),
  leafDk: new THREE.MeshStandardMaterial({color:'#3a6136',roughness:.9}),
  pine:   new THREE.MeshStandardMaterial({color:'#3f6b45',roughness:.9,flatShading:true}),
  trunk:  new THREE.MeshStandardMaterial({color:'#5d4028',roughness:.92}),
  glass:  new THREE.MeshStandardMaterial({color:'#ffd9a0',roughness:.15,metalness:0,
            transparent:true,opacity:.72,emissive:'#ff9c3c',emissiveIntensity:0}),
  brass:  new THREE.MeshStandardMaterial({color:'#c99a5a',roughness:.3,metalness:.9}),
  kayakA: new THREE.MeshStandardMaterial({color:'#e0714a',roughness:.35,metalness:.1}),
  kayakB: new THREE.MeshStandardMaterial({color:'#f4e3c4',roughness:.5}),
  ray:    new THREE.MeshStandardMaterial({color:'#9c8168',roughness:.72,metalness:0,
            side:THREE.DoubleSide,vertexColors:true}),
  fish:   new THREE.MeshStandardMaterial({color:'#ffffff',roughness:.42,metalness:.25}),
  kelp:   new THREE.MeshStandardMaterial({color:'#3f8a5e',roughness:.85,side:THREE.DoubleSide}),
  weed:   new THREE.MeshStandardMaterial({color:'#5fae74',roughness:.9,side:THREE.DoubleSide}),
  bubble: new THREE.MeshStandardMaterial({color:'#dffcff',roughness:.1,metalness:0,
            transparent:true,opacity:.5,emissive:'#8fd8e8',emissiveIntensity:.25}),
  drop:   new THREE.MeshBasicMaterial({color:'#c9f4ff',transparent:true,opacity:.9}),
  gull:   new THREE.MeshStandardMaterial({color:'#f6f1e6',roughness:.8,side:THREE.DoubleSide}),
  lampGlass:new THREE.MeshStandardMaterial({color:'#ffd9a0',transparent:true,opacity:.9,
            emissive:'#ffa24d',emissiveIntensity:0,roughness:.2}),
  dark:   new THREE.MeshStandardMaterial({color:'#2a2119',roughness:.9})
};

/* grass / foliage sway injected into a Standard material (instanced aware) */
function swayMat(base, k=1.0, key='sway'){
  const m = base.clone();
  m.onBeforeCompile = sh => {
    sh.uniforms.uTime = U.uTime; sh.uniforms.uWindV = U.uWindV;
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nuniform float uTime,uWindV;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        float ph = 0.0;
        #ifdef USE_INSTANCING
          ph = instanceMatrix[3].x*1.37 + instanceMatrix[3].z*2.11;
        #else
          ph = modelMatrix[3].x*1.37 + modelMatrix[3].z*2.11;
        #endif
        float hh = max(transformed.y, 0.0);
        float amp = pow(hh*${k.toFixed(2)},2.0)*(0.018 + uWindV*0.115);
        transformed.x += sin(uTime*1.7 + ph + hh*2.1)*amp;
        transformed.z += cos(uTime*1.33 + ph*0.8 + hh*1.5)*amp*0.72;`);
  };
  m.customProgramCacheKey = () => key+k;
  return m;
}
const M_grass = swayMat(new THREE.MeshStandardMaterial({color:'#6f9a4a',roughness:.95,side:THREE.DoubleSide}),1.3,'grass');
const M_pine  = swayMat(M.pine,0.55,'pine');
const M_leaf  = swayMat(M.leaf,0.9,'leaf');
const M_kelp  = swayMat(M.kelp,0.75,'kelp');
const M_weed  = swayMat(M.weed,1.1,'weed');

/* ============================================================================
   7 · TERRAIN (top grid + cut-away skirt + base) — the "cross-section"
   ========================================================================== */
const groundMat = new THREE.MeshStandardMaterial({vertexColors:true, roughness:.96, metalness:0});
groundMat.onBeforeCompile = sh => {
  Object.assign(sh.uniforms,{uTime:U.uTime,uWater:U.uWater,uWaveE:U.uWaveE,uLightMix:U.uLightMix});
  sh.vertexShader = sh.vertexShader
    .replace('#include <common>','#include <common>\nvarying vec3 vWP;')
    .replace('#include <begin_vertex>','#include <begin_vertex>\n vWP=(modelMatrix*vec4(transformed,1.0)).xyz;');
  sh.fragmentShader = sh.fragmentShader
    .replace('#include <common>',`#include <common>
      varying vec3 vWP; uniform float uTime,uWater,uWaveE,uLightMix;
      ${GLSL_NOISE}\n${GLSL_CAUSTIC}`)
    .replace('#include <color_fragment>',`#include <color_fragment>
      float dh = vWP.y - uWater;
      /* wet, darkened sand just above the waterline */
      float wet = (1.0-smoothstep(0.0,0.36,dh))*step(-0.03,dh);
      diffuseColor.rgb *= mix(1.0,0.63,wet*0.9);
      /* lace of shoreline foam */
      float band = smoothstep(0.11,0.0,abs(dh));
      float fn = fbm(vWP.xz*9.0 + vec2(0.0,uTime*0.5));
      float foam = band*smoothstep(0.33,0.70,fn)*(0.30+0.70*uWaveE);
      diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.97,0.99,1.0), clamp(foam,0.0,1.0)*0.92);
      /* animated caustics on the seabed + submerged skirt */
      float sub = smoothstep(0.03,-0.14,dh);
      float ca = caustic(vWP.xz*2.35, uTime*0.5);
      float fade = exp(-max(0.0,-dh)*0.80);
      diffuseColor.rgb += vec3(0.52,0.95,0.86)*ca*sub*fade*0.62*uLightMix;
      /* deep-water falloff */
      diffuseColor.rgb *= mix(1.0,0.40,smoothstep(0.0,1.9,-dh));`)
    .replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
      roughnessFactor = mix(roughnessFactor,0.26,wet*0.85);`);
};
groundMat.customProgramCacheKey = ()=>'ground';

function createGroundGeometry(nx,nz){
  const w=TW,d=TD,yb=FLOOR, cols=nx+1, rows=nz+1, nTop=cols*rows;
  const segs = nx*2+nz*2, nSkirt = segs*4, nBot=4;
  const total = nTop+nSkirt+nBot;
  const pos=new Float32Array(total*3), col=new Float32Array(total*3), idx=[];
  const put=(i,x,y,z,r,g,b)=>{pos[i*3]=x;pos[i*3+1]=y;pos[i*3+2]=z;col[i*3]=r;col[i*3+1]=g;col[i*3+2]=b;};
  let v=0;
  for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){
    const x=-w/2+i*nx>0?0:0; // (kept simple below)
    const px=-w/2+(i/nx)*w, pz=-d/2+(j/nz)*d;
    const y=Math.max(islandHeight(px,pz), yb+0.004);
    const sl=slopeAt(px,pz);
    const n=jnoise(px*2.7,pz*2.7)*0.5+jnoise(px*9,pz*9)*0.5;
    let r,g,b;
    const sand=[0.90,0.80,0.585], wet=[0.72,0.61,0.44], grass=[0.315,0.47,0.245],
          grass2=[0.42,0.55,0.27], rock=[0.40,0.375,0.345], mud=[0.30,0.36,0.245];
    const beach=smoothstep(-0.05,0.34,y), deep=1.0-smoothstep(-0.35,-1.15,y);
    r=lerp(sand[0],grass[0],beach); g=lerp(sand[1],grass[1],beach); b=lerp(sand[2],grass[2],beach);
    r=lerp(r,grass2[0],n*0.55*beach); g=lerp(g,grass2[1],n*0.5*beach); b=lerp(b,grass2[2],n*0.45*beach);
    const rk=smoothstep(0.42,0.78,sl);
    r=lerp(r,rock[0],rk); g=lerp(g,rock[1],rk); b=lerp(b,rock[2],rk);
    const wd=smoothstep(0.20,-0.30,y); r=lerp(r,wet[0],wd*0.8); g=lerp(g,wet[1],wd*0.8); b=lerp(b,wet[2],wd*0.8);
    const seagrass=smoothstep(0.55,0.85,jnoise(px*1.3+7,pz*1.3-3))*deep;
    r=lerp(r,mud[0],seagrass*0.75); g=lerp(g,mud[1],seagrass*0.75); b=lerp(b,mud[2],seagrass*0.75);
    put(v++,px,y,pz,r,g,b);
  }
  for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){
    const a=j*cols+i, b=a+1, c=a+cols, d2=c+1;
    idx.push(a,c,b, b,c,d2);
  }
  /* skirt: vertical cut faces with sediment strata */
  const edge=[];
  for(let i=0;i<nx;i++) edge.push([i,0,i+1,0]);
  for(let j=0;j<nz;j++) edge.push([nx,j,nx,j+1]);
  for(let i=0;i<nx;i++) edge.push([i,nz,i-1+1-1,nz]);
  for(let j=0;j<nz;j++) edge.push([0,j,0,j-1+1-1]);
  const pushEdge=(i0,j0,i1,j1)=>{
    const x0=-w/2+(i0/nx)*w,z0=-d/2+(j0/nz)*d, x1=-w/2+(i1/nx)*w,z1=-d/2+(j1/nz)*d;
    const y0=Math.max(islandHeight(x0,z0),yb+0.004), y1=Math.max(islandHeight(x1,z1),yb+0.004);
    const s=v;
    const strat=(y)=>{
      const t=(y-yb)/(1.6);
      const b1=0.5+0.5*Math.sin(t*9.0+jnoise(x0*2.1,z0*2.1)*2.4);
      return [lerp(0.20,0.40,b1),lerp(0.145,0.29,b1),lerp(0.105,0.21,b1)];
    };
    let c=strat(y0); put(s  ,x0,y0,z0,c[0],c[1],c[2]);
    c=strat(y1);     put(s+1,x1,y1,z1,c[0],c[1],c[2]);
    c=strat(yb);     put(s+2,x1,yb,z1,c[0]*0.6,c[1]*0.6,c[2]*0.6);
                       put(s+3,x0,yb,z0,c[0]*0.6,c[1]*0.6,c[2]*0.6);
    idx.push(s,s+1,s+2, s,s+2,s+3);
    v+=4;
  };
  for(let i=0;i<nx;i++) pushEdge(i,0,i+1,0);
  for(let j=0;j<nz;j++) pushEdge(nx,j,nx,j+1);
  for(let i=nx;i>0;i--) pushEdge(i,nz,i-1,nz);
  for(let j=nz;j>0;j--) pushEdge(0,j,0,j-1);
  /* base */
  put(v,-w/2,yb,-d/2,.09,.07,.06); put(v+1,w/2,yb,-d/2,.09,.07,.06);
  put(v+2,w/2,yb,d/2,.09,.07,.06); put(v+3,-w/2,yb,d/2,.09,.07,.06);
  idx.push(v,v+1,v+2, v,v+2,v+3);
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('color',new THREE.BufferAttribute(col,3));
  g.setIndex(idx); g.computeVertexNormals();
  return g;
}
const ground = new THREE.Mesh(createGroundGeometry(...QUALITY[S.quality].g), groundMat);
ground.castShadow=true; ground.receiveShadow=true;
scene.add(ground);

/* ============================================================================
   8 · WATER — volume, surface, ripples, glass walls
   ========================================================================== */
/* 8a · volume: single-sided box, fragments above the tide are discarded, so the
      tint exists only in the submerged part and never washes out the island. */
const volMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, side:THREE.FrontSide,
  uniforms:{uTime:U.uTime,uWater:U.uWater,uShallow:U.uShallow,uDeep:U.uDeep,
            uLightMix:U.uLightMix,uSunCol:U.uSunCol,uWindV:U.uWindV},
  vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz;
    gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`
    varying vec3 vW; uniform float uTime,uWater,uLightMix,uWindV;
    uniform vec3 uShallow,uDeep,uSunCol;
    ${GLSL_NOISE}\n${GLSL_CAUSTIC}
    void main(){
      if(vW.y > uWater) discard;
      float depth = uWater - vW.y;
      float a = 1.0-exp(-depth*0.60);
      float k = clamp(depth/2.1,0.0,1.0);
      vec3 col = mix(uShallow*1.05, uDeep, k*k*0.8+0.2);
      col += uSunCol*0.05*caustic(vW.xz*1.5, uTime*0.45)*clamp(depth,0.0,1.2);
      /* gentle internal shimmer */
      col += uShallow*0.035*sin(vW.y*7.0-uTime*1.1)*sin(vW.x*2.2+uTime*0.4);
      col *= (0.30+0.70*uLightMix);
      gl_FragColor = vec4(col, a*0.92);
    }`
});
const waterVol = new THREE.Mesh(new THREE.BoxGeometry(TW-0.06, (RIM-FLOOR), TD-0.06), volMat);
waterVol.position.y = (RIM+FLOOR)/2; waterVol.renderOrder = 10; scene.add(waterVol);

/* 8b · surface: waves, foam, glitter, clipped exactly to the analytic shoreline */
const surfMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, side:THREE.FrontSide,
  uniforms:{uTime:U.uTime,uWind:U.uWindV,uWater:U.uWater,uWaveE:U.uWaveE,
    uShallow:U.uShallow,uDeep:U.uDeep,uSky:U.uSky,uSunDir:U.uSunDir,uSunCol:U.uSunCol,
    uLightMix:U.uLightMix,uCam:{value:new THREE.Vector3()}},
  vertexShader:`
    uniform float uTime,uWind,uWater; varying vec3 vW; varying vec3 vN; varying float vShoal;
    ${GLSL_ISLAND}\n${GLSL_WAVE}
    void main(){
      vec3 t = position;
      float amp = 0.028 + uWind*0.075;
      float isl = islandHeight(position.xz);
      float shoal = smoothstep(0.0,-0.85, isl-uWater);
      vShoal = shoal;
      float m = 0.30+0.70*shoal;
      t.y += waveH(position.xz,uTime,amp)*m;
      vec2 e = vec2(0.07,0.0);
      float hx=(waveH(position.xz+e.xy,uTime,amp)-waveH(position.xz-e.xy,uTime,amp))*m;
      float hz=(waveH(position.xz+e.yx,uTime,amp)-waveH(position.xz-e.yx,uTime,amp))*m;
      vN = normalize(vec3(-hx/0.14,1.0,-hz/0.14));
      vec4 w = modelMatrix*vec4(t,1.0); vW=w.xyz;
      gl_Position = projectionMatrix*viewMatrix*w;
    }`,
  fragmentShader:`
    varying vec3 vW; varying vec3 vN; varying float vShoal;
    uniform float uTime,uWater,uWaveE,uLightMix;
    uniform vec3 uShallow,uDeep,uSky,uSunDir,uSunCol,uCam;
    ${GLSL_ISLAND}\n${GLSL_NOISE}
    void main(){
      float isl = islandHeight(vW.xz);
      if(isl > uWater-0.002) discard;
      float dShore = uWater - isl;
      vec3 N = normalize(vN);
      vec3 V = normalize(uCam - vW);
      float fres = pow(1.0-clamp(dot(N,V),0.0,1.0),4.0);
      float k = clamp(dShore/1.9,0.0,1.0);
      vec3 col = mix(uShallow*1.06, uDeep, k*k*0.85+0.15);
      vec3 R = reflect(-V,N);
      col += uSunCol*pow(max(dot(R,normalize(uSunDir)),0.0),190.0)*2.6*uLightMix;
      col += uSunCol*pow(max(dot(R,normalize(uSunDir)),0.0),14.0)*0.10*uLightMix;
      col = mix(col, uSky*0.92, fres*0.60);
      float fn = fbm(vW.xz*7.5 + vec2(uTime*0.16,uTime*0.34));
      float foam = smoothstep(0.32,0.02,dShore)*(0.42+0.72*fn);
      foam += smoothstep(0.62,0.16,dShore)*smoothstep(0.36,0.74,fn)*0.55;
      foam *= (0.35+0.65*uWaveE);
      col = mix(col, vec3(0.97,0.99,1.0), clamp(foam,0.0,1.0)*0.9);
      col *= (0.28+0.72*uLightMix);
      float a = mix(0.60,0.95,fres)+clamp(foam,0.0,1.0)*0.35;
      a *= smoothstep(0.0,0.055,dShore);
      gl_FragColor = vec4(col, clamp(a,0.0,1.0));
    }`
});
function surfaceGeo(seg){
  const g=new THREE.PlaneGeometry(TW-0.07, TD-0.07, seg, Math.round(seg*TD/TW));
  g.rotateX(-Math.PI/2); return g;
}
const waterSurf = new THREE.Mesh(surfaceGeo(QUALITY[S.quality].wseg), surfMat);
waterSurf.renderOrder = 12; scene.add(waterSurf);

/* 8c · ripples: one quad, 8 GPU ripples — used by splashes, kayak, ambient drops */
const RIP = Array.from({length:8},()=>new THREE.Vector4(0,0,0,0));
const ripMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, depthTest:true,
  uniforms:{uRip:{value:RIP},uSize:{value:new THREE.Vector2(TW,TD)},uLightMix:U.uLightMix},
  vertexShader:`varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`
    uniform vec4 uRip[8]; uniform vec2 uSize; uniform float uLightMix; varying vec2 vUv;
    void main(){
      vec2 p=(vUv-0.5)*uSize; float s=0.0;
      for(int i=0;i<8;i++){
        float str=uRip[i].w; if(str<=0.001) continue;
        float age=uRip[i].y; float r=length(p-uRip[i].xy);
        float rad=age*2.35, w=0.05+age*0.11;
        float ring=exp(-pow((r-rad)/w,2.0));
        float ring2=exp(-pow((r-rad*0.60)/(w*0.75),2.0))*0.45;
        s += (ring+ring2)*str*(1.0-smoothstep(0.22,1.0,age))*exp(-r*0.16);
      }
      s=clamp(s,0.0,1.0);
      if(s<0.004) discard;
      gl_FragColor=vec4(vec3(0.98,1.0,1.0)*(0.45+0.55*uLightMix), s*0.85);
    }`
});
const ripPlane = new THREE.Mesh(new THREE.PlaneGeometry(TW-0.07,TD-0.07).rotateX(-Math.PI/2), ripMat);
ripPlane.renderOrder = 14; scene.add(ripPlane);
let ripIdx=0;
function addRipple(x,z,strength){
  const r=RIP[ripIdx=(ripIdx+1)%8]; r.set(x,z,0,strength);
}

/* 8d · aquarium glass: front + two sides only, so the cut reads cleanly */
const glassMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, side:THREE.DoubleSide,
  uniforms:{uWater:U.uWater,uLightMix:U.uLightMix,uSky:U.uSky},
  vertexShader:`varying vec3 vW; varying vec3 vN;
    void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz;
      vN=normalize(mat3(modelMatrix)*normal); gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`
    varying vec3 vW; varying vec3 vN; uniform float uWater,uLightMix; uniform vec3 uSky;
    ${GLSL_NOISE}
    void main(){
      vec3 V=normalize(cameraPosition-vW);
      float f=pow(1.0-abs(dot(normalize(vN),V)),3.0);
      float streak=vnoise(vec2(vW.x*2.6,vW.y*0.9))*0.022;
      float a=0.035+f*0.30+streak;
      a += 0.055*smoothstep(0.05,0.0,abs(vW.y-uWater));
      vec3 col=mix(vec3(0.72,0.90,0.94), vec3(1.0), f*0.55);
      col*=(0.45+0.55*uLightMix);
      gl_FragColor=vec4(col,clamp(a,0.0,0.6));
    }`
});
const glassGeos=[];
{
  const h=RIM-FLOOR;
  const f=new THREE.PlaneGeometry(TW,h); f.translate(0,(FLOOR+RIM)/2,TD/2); glassGeos.push(f);
  const l=new THREE.PlaneGeometry(TD,h); l.rotateY(Math.PI/2); l.translate(-TW/2,(FLOOR+RIM)/2,0); glassGeos.push(l);
  const r=new THREE.PlaneGeometry(TD,h); r.rotateY(-Math.PI/2); r.translate(TW/2,(FLOOR+RIM)/2,0); glassGeos.push(r);
}
const glass = new THREE.Mesh(BGU.mergeGeometries(glassGeos,false), glassMat);
glass.renderOrder = 30; scene.add(glass);

/* 8e · wooden frame, corner posts, plinth + brass nameplate */
function mergeParts(parts,mat,cast=true,rec=true){
  const gs=parts.map(p=>{const g=p.g.clone();
    if(p.rot) g.rotateX(p.rot[0]||0),g.rotateY(p.rot[1]||0),g.rotateZ(p.rot[2]||0);
    if(p.scl) g.scale(p.scl[0],p.scl[1],p.scl[2]);
    if(p.pos) g.translate(p.pos[0],p.pos[1],p.pos[2]);
    return g;});
  const g=BGU.mergeGeometries(gs,false); gs.forEach(x=>x.dispose());
  const m=new THREE.Mesh(g,mat); m.castShadow=cast; m.receiveShadow=rec; return m;
}
const box=(w,h,d)=>new THREE.BoxGeometry(w,h,d);
const cyl=(r1,r2,h,s=10)=>new THREE.CylinderGeometry(r1,r2,h,s);

const frameParts=[];
const fw=0.13;
frameParts.push({g:box(TW+fw*2,fw,fw),pos:[0,RIM, TD/2+fw/2]});
frameParts.push({g:box(TW+fw*2,fw,fw),pos:[0,RIM,-TD/2-fw/2]});
frameParts.push({g:box(fw,fw,TD+fw*2),pos:[ TW/2+fw/2,RIM,0]});
frameParts.push({g:box(fw,fw,TD+fw*2),pos:[-TW/2-fw/2,RIM,0]});
for(const sx of[-1,1])for(const sz of[-1,1])
  frameParts.push({g:box(0.15,RIM-FLOOR+fw,0.15),pos:[sx*(TW/2+fw/2),(RIM+FLOOR)/2,sz*(TD/2+fw/2)]});
const frame = mergeParts(frameParts, M.woodDk); scene.add(frame);

const plinth = mergeParts([
  {g:box(TW+0.62,0.46,TD+0.62),pos:[0,FLOOR-0.23,0]},
  {g:box(TW+0.30,0.14,TD+0.30),pos:[0,FLOOR-0.50,0]}
], M.wood); scene.add(plinth);

/* nameplate (canvas texture, drawn once the display font is ready) */
const plateMat = new THREE.MeshStandardMaterial({color:'#ffffff',roughness:.42,metalness:.55});
const plate = new THREE.Mesh(new THREE.PlaneGeometry(2.35,0.5), plateMat);
plate.position.set(0,FLOOR-0.22,TD/2+0.32); scene.add(plate);
(document.fonts?document.fonts.ready:Promise.resolve()).then(()=>{
  const c=document.createElement('canvas'); c.width=768; c.height=164;
  const g=c.getContext('2d');
  g.fillStyle='#17262b'; g.fillRect(0,0,768,164);
  g.strokeStyle='#c99a5a'; g.lineWidth=7; g.strokeRect(13,13,742,138);
  g.fillStyle='#f0dcae'; g.textAlign='center'; g.textBaseline='middle';
  g.font='500 74px Fraunces, Georgia, serif'; g.fillText('TIDEHAVEN',384,88);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4;
  plateMat.map=t; plateMat.needsUpdate=true;
});

/* ============================================================================
   9 · THE CABIN (A-frame, copper roof, deck, glowing gable)
   ========================================================================== */
const cabin = new THREE.Group();
cabin.position.set(CABIN.x, PAD_Y-0.02, CABIN.y);
cabin.rotation.y = Math.atan2(PIER_A.x-CABIN.x, PIER_A.y-CABIN.y);
scene.add(cabin);
{
  /* stone footing */
  const foot=[];
  for(let i=0;i<7;i++){
    const a=i/7*Math.PI*2;
    foot.push({g:new THREE.IcosahedronGeometry(0.24,0),pos:[Math.cos(a)*1.25,-0.10,Math.sin(a)*1.45],
      scl:[1.1,0.6,1.1],rot:[RNG()*2,RNG()*2,0]});
  }
  foot.push({g:box(2.3,0.16,2.7),pos:[0,-0.02,0]});
  cabin.add(mergeParts(foot,M.stone));

  /* A-frame walls (two slopes) */
  const walls=[];
  const W=1.02, H=1.78, D=2.55, ang=Math.atan2(H,W), slope=Math.hypot(W,H);
  for(const s of[-1,1]){
    walls.push({g:box(0.10,slope,D),pos:[s*W/2,H/2,0],rot:[0,0,s*ang]});
  }
  walls.push({g:box(2.1,0.14,D),pos:[0,0.05,0]});
  cabin.add(mergeParts(walls,M.woodLt,true,true));

  /* gable ends */
  const tri=new THREE.Shape();
  tri.moveTo(-W,0); tri.lineTo(W,0); tri.lineTo(0,H); tri.lineTo(-W,0);
  const triG=new THREE.ExtrudeGeometry(tri,{depth:0.07,bevelEnabled:false});
  const back=triG.clone(); back.translate(0,0,-D/2);
  cabin.add(mergeParts([{g:back}],M.wood,true,true));

  /* copper roof panels + ridge + verdigris trim */
  const roof=[];
  for(const s of[-1,1])
    roof.push({g:box(0.075,slope+0.30,D+0.34),pos:[s*(W/2+0.03),H/2+0.04,0],rot:[0,0,s*ang]});
  roof.push({g:box(0.16,0.13,D+0.40),pos:[0,H+0.06,0]});
  cabin.add(mergeParts(roof,M.copper,true,false));
  cabin.add(mergeParts([
    {g:box(0.05,0.06,D+0.42),pos:[-0.92,0.62,0],rot:[0,0,ang]},
    {g:box(0.05,0.06,D+0.42),pos:[ 0.92,0.62,0],rot:[0,0,-ang]}
  ],M.verd,false,false));

  /* glowing triangular window + mullions */
  const winShape=new THREE.Shape();
  const iw=W-0.16, ih=H-0.24;
  winShape.moveTo(-iw,0.10); winShape.lineTo(iw,0.10); winShape.lineTo(0,ih); winShape.lineTo(-iw,0.10);
  const win=new THREE.Mesh(new THREE.ShapeGeometry(winShape), M.glass);
  win.position.set(0,0,D/2+0.02); cabin.add(win);
  const mull=[];
  mull.push({g:box(0.055,ih,0.06),pos:[0,0.10+ih/2,D/2+0.05]});
  mull.push({g:box(iw*1.7,0.055,0.06),pos:[0,0.10+ih*0.36,D/2+0.05]});
  mull.push({g:box(0.06,0.06,D+0.02),pos:[0,H+0.02,0]});
  cabin.add(mergeParts(mull,M.woodDk,true,false));

  /* chimney */
  cabin.add(mergeParts([
    {g:box(0.26,1.05,0.26),pos:[-0.62,1.42,-0.85]},
    {g:box(0.34,0.10,0.34),pos:[-0.62,1.97,-0.85]}
  ],M.stone,true,false));
  CHIMNEY_TOP = new THREE.Vector3(-0.62,2.05,-0.85).applyMatrix4(new THREE.Matrix4()
    .makeRotationY(cabin.rotation.y).setPosition(cabin.position.x,cabin.position.y,cabin.position.z));

  /* deck: planks, joists, railing, steps */
  const deck=new THREE.Group(); deck.position.set(0,-0.02,D/2+0.02); cabin.add(deck);
  const plankGeo=box(0.24,0.06,1.75);
  const planks=[]; for(let i=0;i<11;i++) planks.push({g:plankGeo,pos:[-1.25+i*0.25,0.14,0.86]});
  planks.push({g:box(2.7,0.10,0.12),pos:[0,0.08,0.02]});
  deck.add(mergeParts(planks,M.wood,true,true));
  const rail=[];
  for(const sx of[-1,1]){
    rail.push({g:cyl(0.045,0.05,0.62,7),pos:[sx*1.32,0.46,0.10]});
    rail.push({g:cyl(0.045,0.05,0.62,7),pos:[sx*1.32,0.46,0.88]});
    rail.push({g:cyl(0.045,0.05,0.62,7),pos:[sx*1.32,0.46,1.66]});
    rail.push({g:box(0.07,0.06,1.78),pos:[sx*1.32,0.76,0.88],rot:[0,0,0]});
    rail.push({g:box(0.06,0.05,1.78),pos:[sx*1.32,0.52,0.88]});
  }
  for(let i=0;i<5;i++) rail.push({g:cyl(0.045,0.05,0.62,7),pos:[-1.25+i*0.62,0.46,1.72]});
  rail.push({g:box(1.7,0.07,0.06),pos:[0.15,0.76,1.72]});
  rail.push({g:box(1.7,0.05,0.06),pos:[0.15,0.52,1.72]});
  deck.add(mergeParts(rail,M.woodLt,true,false));
  /* steps down the slope */
  const steps=[];
  for(let i=0;i<4;i++) steps.push({g:box(1.0,0.08,0.30),pos:[0,0.10-i*0.16,1.92+i*0.32]});
  deck.add(mergeParts(steps,M.wood,true,true));

  /* door, lantern bracket, pennant pole */
  cabin.add(mergeParts([
    {g:box(0.5,0.95,0.07),pos:[-0.72,0.53,D/2+0.04]},
    {g:box(0.06,0.06,0.06),pos:[-0.53,0.53,D/2+0.10]}
  ],M.woodDk,true,false));

  /* interior lamp */
  const bulb=new THREE.Mesh(new THREE.SphereGeometry(0.10,10,8), M.lampGlass);
  bulb.position.set(0,1.05,D/2-0.45); cabin.add(bulb);
  LAMP_MESHES.push(M.glass,M.lampGlass);
}

/* ============================================================================
   10 · PIER, LADDER, LANTERNS, KAYAK + lived-in props
   ========================================================================== */
const pierDir = new THREE.Vector2().subVectors(PIER_B,PIER_A);
const pierLen = pierDir.length(), pierAng = Math.atan2(pierDir.x,pierDir.y);
const pier = new THREE.Group();
pier.position.set(PIER_A.x,0,PIER_A.y); pier.rotation.y = pierAng; scene.add(pier);
{
  const posts=[],planks=[];
  const n=Math.ceil(pierLen/0.78);
  for(let i=0;i<=n;i++){
    const z=i*(pierLen/n);
    const wz=PIER_A.y+Math.sin(pierAng)*z, wx=PIER_A.x+Math.cos(pierAng)*z;
    const gy=Math.max(islandHeight(wx,wz),FLOOR+0.02);
    const L=DECK_Y-gy+0.05;
    for(const sx of[-1,1]){
      posts.push({g:cyl(0.075,0.09,L,8),pos:[sx*0.44,DECK_Y-L/2,z],scl:[1,1,1]});
    }
    posts.push({g:box(0.94,0.06,0.06),pos:[0,DECK_Y-0.30,z]});
  }
  for(let i=0;i<Math.floor(pierLen/0.24);i++)
    planks.push({g:box(1.02,0.07,0.185),pos:[0,DECK_Y,0.12+i*0.24]});
  planks.push({g:box(1.06,0.09,0.24),pos:[0,DECK_Y,pierLen-0.10]});
  pier.add(mergeParts(posts,M.woodDk,true,false));
  pier.add(mergeParts(planks,M.wood,true,true));
  /* railing on the land side only, so the water stays open */
  const rail=[];
  for(let i=0;i<=Math.floor(pierLen/0.9);i++){
    rail.push({g:cyl(0.04,0.045,0.6,7),pos:[-0.46,DECK_Y+0.30,0.10+i*0.9]});
  }
  rail.push({g:box(0.06,0.055,pierLen),pos:[-0.46,DECK_Y+0.58,pierLen/2]});
  rail.push({g:box(0.05,0.05,pierLen),pos:[-0.46,DECK_Y+0.40,pierLen/2]});
  pier.add(mergeParts(rail,M.woodLt,true,false));
  /* ladder down into the lagoon at the pier head */
  const lad=[];
  for(const sx of[-1,1]) lad.push({g:cyl(0.04,0.04,1.9,7),pos:[sx*0.19,DECK_Y-0.95,pierLen+0.28]});
  for(let i=0;i<6;i++) lad.push({g:box(0.40,0.045,0.045),pos:[0,DECK_Y-0.30-i*0.30,pierLen+0.28]});
  pier.add(mergeParts(lad,M.woodLt,true,false));
  /* lanterns */
  const lampPosts=[];
  for(const z of [pierLen*0.42, pierLen-0.18]){
    lampPosts.push({g:cyl(0.045,0.05,0.95,7),pos:[0.44,DECK_Y+0.48,z]});
    lampPosts.push({g:box(0.05,0.05,0.16),pos:[0.44,DECK_Y+0.94,z]});
    const l=new THREE.Mesh(new THREE.BoxGeometry(0.16,0.20,0.16), M.lampGlass);
    l.position.set(0.36,DECK_Y+0.84,z); pier.add(l); LAMP_MESHES.push(M.lampGlass);
    const cap=new THREE.Mesh(box(0.21,0.05,0.21),M.brass); cap.position.set(0.36,DECK_Y+0.96,z); pier.add(cap);
  }
  pier.add(mergeParts(lampPosts,M.woodDk,true,false));
  /* crates, barrel, towels, coil of rope */
  const crateGeo=box(0.42,0.36,0.42);
  pier.add(mergeParts([
    {g:crateGeo,pos:[-0.24,DECK_Y+0.22,pierLen-1.05],rot:[0,0.4,0]},
    {g:crateGeo,pos:[-0.20,DECK_Y+0.22,pierLen-1.52],rot:[0,-0.2,0],scl:[0.9,0.8,0.9]},
    {g:crateGeo,pos:[-0.24,DECK_Y+0.56,pierLen-1.20],rot:[0,0.9,0],scl:[0.8,0.7,0.8]},
    {g:cyl(0.21,0.19,0.5,10),pos:[0.28,DECK_Y+0.29,pierLen-1.85]},
  ],M.wood,true,true));
  const towel=new THREE.Mesh(new THREE.PlaneGeometry(0.44,0.62,4,6), M.cloth2.clone());
  towel.material.side=THREE.DoubleSide;
  towel.position.set(-0.48,DECK_Y+0.30,pierLen-2.35); towel.rotation.y=Math.PI/2;
  pier.add(towel); FLUTTER.push({m:towel,k:0.05,base:0});
  const towel2=new THREE.Mesh(new THREE.PlaneGeometry(0.40,0.56,4,6), M.cloth.clone());
  towel2.material.side=THREE.DoubleSide;
  towel2.position.set(0.48,DECK_Y+0.32,pierLen-0.62); towel2.rotation.y=-Math.PI/2;
  pier.add(towel2); FLUTTER.push({m:towel2,k:0.045,base:0});
  const coil=new THREE.Mesh(new THREE.TorusGeometry(0.16,0.032,6,16), M.cloth);
  coil.rotation.x=Math.PI/2; coil.position.set(0.30,DECK_Y+0.06,pierLen-0.55); pier.add(coil);
}

/* kayak (lofted hull) + paddle, moored to the pier head */
function hullGeo(){
  const rings=[[0.02,0.015],[0.11,0.075],[0.16,0.115],[0.165,0.12],[0.13,0.10],[0.055,0.05],[0.012,0.012]];
  const zs=[-0.95,-0.62,-0.28,0.05,0.42,0.78,0.98];
  const NU=12, pos=[],idx=[];
  for(let i=0;i<zs.length;i++){
    const [rx,ry]=rings[i], z=zs[i];
    for(let j=0;j<=NU;j++){
      const a=j/NU*Math.PI*2;
      pos.push(Math.cos(a)*rx, Math.sin(a)*ry*0.92-ry*0.28, z);
    }
  }
  for(let i=0;i<zs.length-1;i++)for(let j=0;j<NU;j++){
    const a=i*(NU+1)+j,b=a+1,c=a+NU+1,d=c+1;
    idx.push(a,c,b,b,c,d);
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  g.setIndex(idx); g.computeVertexNormals(); return g;
}
const kayak = new THREE.Group(); scene.add(kayak);
{
  const hull=new THREE.Mesh(hullGeo(),M.kayakA); hull.castShadow=true; kayak.add(hull);
  const deckIn=new THREE.Mesh(hullGeo(),M.kayakB);
  deckIn.scale.set(0.86,0.55,0.93); deckIn.position.y=0.045; kayak.add(deckIn);
  const seat=new THREE.Mesh(box(0.16,0.03,0.20),M.woodDk); seat.position.set(0,0.075,-0.02); kayak.add(seat);
  const pad=new THREE.Group();
  pad.add(new THREE.Mesh(cyl(0.014,0.014,0.92,6),M.woodDk));
  for(const s of[-1,1]){
    const b=new THREE.Mesh(box(0.07,0.014,0.20),M.woodLt);
    b.position.set(0,0,s*0.46); pad.add(b);
  }
  pad.rotation.set(0.35,0,0.5); pad.position.set(0.12,0.14,0.1); kayak.add(pad);
  const rope=new THREE.Mesh(cyl(0.012,0.012,0.55,5),M.cloth);
  rope.rotation.z=Math.PI/2.4; rope.position.set(0.30,0.05,0.30); kayak.add(rope);
}
const kayakPath = new THREE.CatmullRomCurve3((()=>{
  const pts=[];
  const N=14;
  for(let i=0;i<N;i++){
    const a=i/N*Math.PI*2;
    const rx=3.85+Math.sin(a*3+1.2)*0.22, rz=3.55+Math.cos(a*2.4)*0.18;
    pts.push(new THREE.Vector3(Math.cos(a)*rx, 0, Math.sin(a)*rz));
  }
  return pts;
})(), true, 'catmullrom', 0.4);
/* start the lap right beside the pier head */
{
  let best=0,bd=1e9;
  for(let i=0;i<=200;i++){const p=kayakPath.getPoint(i/200);
    const d=Math.hypot(p.x-PIER_B.x-0.55,p.z-PIER_B.y-0.1); if(d<bd){bd=d;best=i/200;}}
  kayakPath.shiftPoint = best; // stored offset used by the update loop
}

/* lanterns on the shore + a bench, campfire ring, clothesline */
function shoreLantern(x,z){
  const g=new THREE.Group(); const y=islandHeight(x,z);
  g.position.set(x,y,z);
  g.add(mergeParts([
    {g:cyl(0.05,0.06,1.15,7),pos:[0,0.58,0]},
    {g:box(0.20,0.05,0.20),pos:[0,1.18,0]}
  ],M.woodDk,true,false));
  const l=new THREE.Mesh(box(0.17,0.22,0.17),M.lampGlass);
  l.position.set(0,1.04,0); g.add(l); LAMP_MESHES.push(M.lampGlass);
  scene.add(g); return g;
}
shoreLantern(PIER_A.x-0.85, PIER_A.y+0.55);
shoreLantern(CABIN.x+1.55, CABIN.y+1.35);

{ /* bench facing the lagoon */
  const y=islandHeight(2.55,0.55), b=new THREE.Group(); b.position.set(2.55,y,0.55);
  b.rotation.y=-0.55;
  b.add(mergeParts([
    {g:box(0.9,0.06,0.30),pos:[0,0.30,0]},
    {g:box(0.9,0.26,0.05),pos:[0,0.46,-0.13],rot:[0.16,0,0]},
    {g:box(0.06,0.30,0.26),pos:[-0.38,0.15,0]},
    {g:box(0.06,0.30,0.26),pos:[ 0.38,0.15,0]}
  ],M.woodLt,true,true));
  scene.add(b);
}
{ /* campfire ring + drying line between two posts */
  const cx=-2.35,cz=1.35,cy=islandHeight(cx,cz);
  const ring=[];
  for(let i=0;i<8;i++){const a=i/8*Math.PI*2;
    ring.push({g:new THREE.IcosahedronGeometry(0.12,0),pos:[cx+Math.cos(a)*0.34,cy+0.05,cz+Math.sin(a)*0.34],
      scl:[1,0.7,1],rot:[RNG(),RNG(),0]});}
  scene.add(mergeParts(ring,M.stone,true,true));
  const logs=[];
  for(let i=0;i<3;i++) logs.push({g:cyl(0.05,0.05,0.5,6),pos:[cx,cy+0.09,cz],rot:[Math.PI/2,0,i*1.1]});
  scene.add(mergeParts(logs,M.woodDk,true,true));

  const p1=[-0.35,1.95],p2=[0.95,2.55];
  const posts=[];
  for(const p of[p1,p2]){const y=islandHeight(p[0],p[1]);
    posts.push({g:cyl(0.045,0.05,1.5,7),pos:[p[0],y+0.75,p[1]]});}
  scene.add(mergeParts(posts,M.woodDk,true,false));
  const line=new THREE.Mesh(new THREE.CylinderGeometry(0.012,0.012,1.42,5),M.cloth);
  const y1=islandHeight(p1[0],p1[1])+1.45, y2=islandHeight(p2[0],p2[1])+1.45;
  line.position.set((p1[0]+p2[0])/2,(y1+y2)/2,(p1[1]+p2[1])/2);
  line.rotation.set(0,Math.atan2(p2[0]-p1[0],p2[1]-p1[1]),Math.PI/2-0.06);
  scene.add(line);
  const shirt=new THREE.Mesh(new THREE.PlaneGeometry(0.34,0.44,4,5), M.cloth.clone());
  shirt.material.side=THREE.DoubleSide;
  shirt.position.set(p1[0]*0.45+p2[0]*0.55, y1*0.5+y2*0.5-0.24, p1[1]*0.45+p2[1]*0.55);
  shirt.rotation.y=Math.atan2(p2[0]-p1[0],p2[1]-p1[1]);
  scene.add(shirt); FLUTTER.push({m:shirt,k:0.06,base:0});
}

/* ============================================================================
   11 · SCENERY — trees, rocks, grass, pots (instanced, wind-swayed)
   ========================================================================== */
const R2 = mulberry(4242);
function jitterIco(r,detail,seed){
  const g=new THREE.IcosahedronGeometry(r,detail); const p=g.attributes.position;
  const rr=mulberry(seed);
  for(let i=0;i<p.count;i++){
    const x=p.getX(i),y=p.getY(i),z=p.getZ(i),l=Math.hypot(x,y,z);
    const s=1+(rr()-0.5)*0.42;
    p.setXYZ(i,x/l*r*s,y/l*r*s*0.78,z/l*r*s);
  }
  g.computeVertexNormals(); return g;
}
const rockGeo=[jitterIco(0.34,1,7),jitterIco(0.5,1,11),jitterIco(0.22,0,23)];

/* rocks (above + below water) */
function scatterRocks(){
  const list=[];
  let tries=0;
  while(list.length<30 && tries++<900){
    const x=(R2()*2-1)*4.9, z=(R2()*2-1)*3.9, h=islandHeight(x,z);
    if(h<-1.9) continue;
    if(Math.hypot(x-CABIN.x,z-CABIN.y)<1.9) continue;
    if(Math.abs(x-PIER_A.x)<0.9&&z>PIER_A.y-0.6) continue;
    const s=0.55+R2()*1.1;
    list.push({p:new THREE.Vector3(x,Math.max(h,FLOOR+0.02)+s*0.06,z),
      r:{x:R2()*3,y:R2()*6,z:R2()*0.6},s:[s,s,s]});
  }
  const geo=rockGeo[0];
  const im=new THREE.InstancedMesh(geo,M.rock,list.length);
  const d=new THREE.Object3D();
  list.forEach((t,i)=>{d.position.copy(t.p);d.rotation.set(t.r.x,t.r.y,t.r.z);d.scale.set(...t.s);
    d.updateMatrix();im.setMatrixAt(i,d.matrix);});
  im.castShadow=true;im.receiveShadow=true;scene.add(im);
  return im;
}
scatterRocks();

/* conifers + palms */
function scatterTrees(){
  const trunks=[],crowns=[];
  const spots=[];
  let tries=0;
  while(spots.length<9 && tries++<900){
    const a=R2()*Math.PI*2, r=0.9+R2()*1.9;
    const x=Math.cos(a)*r*1.25, z=Math.sin(a)*r;
    const h=islandHeight(x,z);
    if(h<0.75||h>2.6) continue;
    if(Math.hypot(x-CABIN.x,z-CABIN.y)<1.85) continue;
    spots.push([x,z,h]);
  }
  for(const [x,z,h] of spots){
    const s=0.8+R2()*0.55;
    trunks.push({p:new THREE.Vector3(x,h-0.05,z),r:{y:R2()*6},s:[s,s,s]});
    crowns.push({p:new THREE.Vector3(x,h-0.05,z),r:{y:R2()*6},s:[s,s,s]});
  }
  const tGeo=cyl(0.055,0.11,1.0,7).translate(0,0.5,0);
  const cGeo=(()=>{
    const parts=[];
    parts.push(new THREE.ConeGeometry(0.62,0.85,9).translate(0,1.05,0));
    parts.push(new THREE.ConeGeometry(0.48,0.78,9).translate(0,1.55,0));
    parts.push(new THREE.ConeGeometry(0.32,0.66,9).translate(0,2.02,0));
    return BGU.mergeGeometries(parts,false);
  })();
  const mk=(geo,mat,list)=>{
    const im=new THREE.InstancedMesh(geo,mat,list.length); const d=new THREE.Object3D();
    list.forEach((t,i)=>{d.position.copy(t.p);d.rotation.set(0,t.r.y,0);d.scale.set(...t.s);
      d.updateMatrix();im.setMatrixAt(i,d.matrix);});
    im.castShadow=true;im.receiveShadow=true;scene.add(im);return im;
  };
  mk(tGeo,M.trunk,trunks); mk(cGeo,M_pine,crowns);

  /* two palms near the shore */
  for(const [x,z] of [[-2.9,2.1],[2.9,-1.9]]){
    const h=islandHeight(x,z); if(h<0.1) continue;
    const g=new THREE.Group(); g.position.set(x,h,z); scene.add(g);
    const seg=[];
    for(let i=0;i<6;i++) seg.push({g:cyl(0.10-i*0.008,0.11-i*0.008,0.34,7),
      pos:[Math.sin(i*0.22)*0.10,0.17+i*0.33,Math.cos(i*0.3)*0.06],rot:[0,0,Math.sin(i*0.2)*0.16]});
    g.add(mergeParts(seg,M.trunk,true,false));
    const fr=[];
    for(let i=0;i<7;i++){
      const a=i/7*Math.PI*2;
      fr.push({g:new THREE.PlaneGeometry(0.24,1.05,1,6).rotateX(-Math.PI/2).translate(0,0,0.52),
        pos:[Math.cos(a)*0.06,2.05,Math.sin(a)*0.06],rot:[0.34,-a,0]});
    }
    const fm=swayMat(new THREE.MeshStandardMaterial({color:'#4f8b4a',roughness:.9,side:THREE.DoubleSide}),0.8,'palm');
    const palm=mergeParts(fr,fm,true,false); palm.position.y=0; g.add(palm);
  }
}
scatterTrees();

/* grass tufts: three crossed tapered blades, instanced */
let grassMesh;
{
  const blade=new THREE.PlaneGeometry(0.09,0.34,1,3).translate(0,0.17,0);
  const p=blade.attributes.position;
  for(let i=0;i<p.count;i++){const y=p.getY(i);p.setX(i,p.getX(i)*(1-y/0.5));}
  blade.computeVertexNormals();
  const parts=[blade.clone(),blade.clone().rotateY(1.1),blade.clone().rotateY(2.2)];
  const geo=BGU.mergeGeometries(parts,false);
  const list=[];
  let tries=0;
  while(list.length<QUALITY.high.grass && tries++<6000){
    const x=(R2()*2-1)*4.6, z=(R2()*2-1)*3.7, h=islandHeight(x,z);
    if(h<0.30||h>2.7) continue;
    if(slopeAt(x,z)>0.85) continue;
    if(Math.hypot(x-CABIN.x,z-CABIN.y)<1.15) continue;
    list.push([x,h,z,R2()]);
  }
  grassMesh=new THREE.InstancedMesh(geo,M_grass,list.length);
  const d=new THREE.Object3D();
  list.forEach((t,i)=>{d.position.set(t[0],t[2]===undefined?0:t[1],t[2]);
    d.rotation.set(0,t[3]*6.28,0);const s=0.7+t[3]*0.9;d.scale.set(s,s*(0.7+t[3]*0.8),s);
    d.updateMatrix();grassMesh.setMatrixAt(i,d.matrix);});
  grassMesh.receiveShadow=true; scene.add(grassMesh);
}

/* potted plants + flower beds around the deck */
{
  const pots=[];
  const spots=[[CABIN.x+1.35,CABIN.y+1.9],[CABIN.x-1.5,CABIN.y+1.6],[CABIN.x+0.2,CABIN.y+2.35],
               [PIER_A.x-0.55,PIER_A.y-0.35],[CABIN.x-2.0,CABIN.y+0.2]];
  for(const [x,z] of spots){const h=islandHeight(x,z); if(h<0.2) continue; pots.push([x,h,z]);}
  const potGeo=cyl(0.15,0.11,0.22,9).translate(0,0.11,0);
  const bushGeo=(()=>{const p=[new THREE.IcosahedronGeometry(0.19,0).translate(0,0.34,0),
    new THREE.IcosahedronGeometry(0.14,0).translate(0.12,0.44,0.05),
    new THREE.IcosahedronGeometry(0.12,0).translate(-0.10,0.42,-0.06)];
    return BGU.mergeGeometries(p,false);})();
  const imP=new THREE.InstancedMesh(potGeo,M.stone,pots.length);
  const imB=new THREE.InstancedMesh(bushGeo,M_leaf,pots.length);
  const d=new THREE.Object3D();
  pots.forEach((t,i)=>{d.position.set(t[0],t[1],t[2]);d.rotation.set(0,R2()*6,0);d.scale.setScalar(1);
    d.updateMatrix();imP.setMatrixAt(i,d.matrix);imB.setMatrixAt(i,d.matrix);});
  imP.castShadow=imB.castShadow=true; imP.receiveShadow=imB.receiveShadow=true;
  scene.add(imP); scene.add(imB);
  /* wildflowers */
  const fl=[];let tries=0;
  while(fl.length<120&&tries++<2500){
    const x=(R2()*2-1)*4.2,z=(R2()*2-1)*3.4,h=islandHeight(x,z);
    if(h<0.55||h>2.3||slopeAt(x,z)>0.7)continue;
    fl.push([x,h,z]);
  }
  const fg=new THREE.SphereGeometry(0.045,5,4);
  const fm=new THREE.MeshStandardMaterial({color:'#f2c14e',roughness:.8});
  const imF=new THREE.InstancedMesh(fg,fm,fl.length); const d2=new THREE.Object3D();
  const cols=[new THREE.Color('#f2c14e'),new THREE.Color('#f07a6a'),new THREE.Color('#f7ecd6'),new THREE.Color('#c98bd6')];
  fl.forEach((t,i)=>{d2.position.set(t[0],t[1]+0.14,t[2]);d2.scale.setScalar(0.7+R2()*0.8);
    d2.updateMatrix();imF.setMatrixAt(i,d2.matrix);imF.setColorAt(i,cols[(R2()*4)|0]);});
  scene.add(imF);
}

/* ============================================================================
   12 · UNDERWATER LIFE — rays, schools, kelp, bubbles
   ========================================================================== */
/* 12a · ray geometry: a parametric disc with baked span/length attributes */
function rayWidth(u){
  const w = 0.66*smoothstep(0.14,0.52,u)*(1-smoothstep(0.62,0.99,u)*0.90);
  return Math.max(w, 0.018+0.022*(1-u));
}
function makeRayGeometry(){
  const NU=30,NV=20,L=1.55, pos=[],col=[],idx=[],aSpan=[],aU=[];
  for(let i=0;i<=NU;i++){
    const u=i/NU, z=(u-0.62)*L, w=rayWidth(u);
    for(let j=0;j<=NV;j++){
      const s=(j/NV)*2-1, x=s*w, an=Math.abs(s);
      const dome=0.115*Math.exp(-Math.pow(x/0.26,2))*Math.sin(Math.PI*clamp((u-0.16)/0.84,0,1));
      const keel=0.02*(1-an)*smoothstep(0.1,0.4,u)*(1-smoothstep(0.85,1.0,u));
      const y=dome+keel;
      pos.push(x,y,z); aSpan.push(an); aU.push(u);
      const spot=jnoise(u*22,j*3.1);
      const base=[0.60,0.49,0.39];
      const rim=[0.83,0.76,0.64];
      const t=smoothstep(0.45,1.0,an);
      let r=lerp(base[0],rim[0],t), g=lerp(base[1],rim[1],t), b=lerp(base[2],rim[2],t);
      const sp=smoothstep(0.80,0.95,spot)*0.35*(1-t);
      r+=sp;g+=sp*0.95;b+=sp*0.85;
      col.push(r,g,b);
    }
  }
  for(let i=0;i<NU;i++)for(let j=0;j<NV;j++){
    const a=i*(NV+1)+j,b=a+1,c=a+NV+1,d=c+1;
    idx.push(a,c,b,b,c,d);
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  g.setAttribute('aSpan',new THREE.Float32BufferAttribute(aSpan,1));
  g.setAttribute('aU',new THREE.Float32BufferAttribute(aU,1));
  g.setIndex(idx); g.computeVertexNormals();
  return g;
}
const rayGeo = makeRayGeometry();
const rayUniforms = {uTime:U.uTime, uFlap:{value:1}};
M.ray.onBeforeCompile = sh=>{
  sh.uniforms.uTime=rayUniforms.uTime; sh.uniforms.uFlap=rayUniforms.uFlap;
  sh.vertexShader=sh.vertexShader
    .replace('#include <common>','#include <common>\nattribute float aSpan;attribute float aU;\nuniform float uTime,uFlap;')
    .replace('#include <begin_vertex>',`#include <begin_vertex>
      float w = sin(aU*7.2 - uTime*3.1 + aSpan*1.7);
      transformed.y += w*0.155*pow(aSpan,1.45)*uFlap;
      transformed.z += cos(aU*7.2 - uTime*3.1)*0.035*aSpan*uFlap;`);
  sh.fragmentShader=sh.fragmentShader
    .replace('#include <color_fragment>',`#include <color_fragment>
      float up = smoothstep(-0.28,0.34,vNormal.y);
      diffuseColor.rgb = mix(vec3(0.94,0.90,0.83), diffuseColor.rgb, up);`);
};
M.ray.customProgramCacheKey=()=>'ray';

const rays=[];
function makeRay(scale,phase){
  const g=new THREE.Group();
  const m=new THREE.Mesh(rayGeo,M.ray); m.castShadow=false; g.add(m);
  /* eyes */
  for(const s of[-1,1]){
    const e=new THREE.Mesh(new THREE.SphereGeometry(0.028,7,6),M.dark);
    e.position.set(s*0.115,0.055,0.30); g.add(e);
  }
  /* tail fin */
  const fin=new THREE.Mesh(new THREE.ConeGeometry(0.09,0.30,4),M.ray);
  fin.rotation.x=Math.PI/2; fin.rotation.z=Math.PI/2;
  fin.position.set(0,0.02,-0.86); fin.scale.set(1,0.18,1); g.add(fin);
  g.scale.setScalar(scale); scene.add(g);
  const r={g,m,phase,speed:0.55+Math.random()*0.25,
    vel:new THREE.Vector3(),target:new THREE.Vector3(),leap:0,leapT:0,leapFrom:new THREE.Vector3(),
    leapTo:new THREE.Vector3(),leapPeak:0,roll:0,scale};
  r.target.copy(randomRayPoint());
  g.position.copy(r.target);
  rays.push(r); return r;
}
function randomRayPoint(){
  const a=Math.random()*Math.PI*2;
  const r=2.2+Math.random()*2.2;
  const x=clamp(Math.cos(a)*r,-4.6,4.6), z=clamp(Math.sin(a)*r,-3.4,3.4);
  const y=lerp(FLOOR+0.45, S.tide-0.45, 0.15+Math.random()*0.7);
  return new THREE.Vector3(x,y,z);
}
makeRay(1.00,0); makeRay(0.82,1.9); makeRay(0.92,3.4); makeRay(0.7,4.8);

/* 12b · fish schools (instanced) */
const fishGeo=(()=>{
  const b=new THREE.SphereGeometry(0.055,7,5); b.scale(0.85,0.9,2.1);
  const t=new THREE.ConeGeometry(0.055,0.10,4); t.rotateX(Math.PI/2); t.scale(0.35,1,1); t.translate(0,0,-0.13);
  const d=new THREE.ConeGeometry(0.05,0.06,3); d.rotateX(-Math.PI/2); d.translate(0,0.02,0.05);
  return BGU.mergeGeometries([b,t,d],false);
})();
const schools=[];
function makeSchool(n,palette,cx,cz,rad,depth,spd){
  const im=new THREE.InstancedMesh(fishGeo,M.fish,n);
  const d=new THREE.Object3D();
  const off=[];
  for(let i=0;i<n;i++){
    off.push({r:0.18+Math.random()*0.55,a:Math.random()*6.28,y:(Math.random()-0.5)*0.5,
      ph:Math.random()*6.28,sp:0.6+Math.random()*0.8,s:0.6+Math.random()*0.7});
    im.setColorAt(i,palette[(Math.random()*palette.length)|0]);
  }
  im.instanceColor.needsUpdate=true; scene.add(im);
  schools.push({im,off,n,cx,cz,rad,depth,spd,t:Math.random()*10});
}
makeSchool(QUALITY.high.fish,[new THREE.Color('#ffd479'),new THREE.Color('#f4f0e2'),new THREE.Color('#7fd7e8')],0,0,3.1,-1.05,0.30);
makeSchool(Math.round(QUALITY.high.fish*0.75),[new THREE.Color('#ff9d6b'),new THREE.Color('#ffd0a8'),new THREE.Color('#8de3c6')],1.2,-0.8,2.4,-0.55,0.42);

/* 12c · kelp forest + seagrass meadow */
let kelpMesh, weedMesh;
{
  const blade=new THREE.PlaneGeometry(0.13,1.0,1,7).translate(0,0.5,0);
  const p=blade.attributes.position;
  for(let i=0;i<p.count;i++){const y=p.getY(i);p.setX(i,p.getX(i)*(1-y*0.8));}
  blade.computeVertexNormals();
  const list=[];let tries=0;
  while(list.length<QUALITY.high.kelp&&tries++<3000){
    const x=(R2()*2-1)*5.0,z=(R2()*2-1)*3.9,h=islandHeight(x,z);
    if(h>-0.35) continue;
    if(Math.hypot(x-CABIN.x,z-CABIN.y)<1.2) continue;
    list.push([x,Math.max(h,FLOOR+0.02),z,R2()]);
  }
  kelpMesh=new THREE.InstancedMesh(blade,M_kelp,list.length);
  const d=new THREE.Object3D();
  list.forEach((t,i)=>{d.position.set(t[0],t[1],t[2]);d.rotation.set(0,t[3]*6.28,0);
    d.scale.set(0.8+t[3]*0.7,1.1+t[3]*1.5,1);d.updateMatrix();kelpMesh.setMatrixAt(i,d.matrix);});
  scene.add(kelpMesh);

  const wg=new THREE.PlaneGeometry(0.10,0.42,1,3).translate(0,0.21,0);
  const wl=[];tries=0;
  while(wl.length<QUALITY.high.kelp*1.6&&tries++<5000){
    const x=(R2()*2-1)*5.1,z=(R2()*2-1)*4.0,h=islandHeight(x,z);
    if(h>-0.18||h<FLOOR+0.06) continue;
    wl.push([x,Math.max(h,FLOOR+0.02),z,R2()]);
  }
  weedMesh=new THREE.InstancedMesh(wg,M_weed,wl.length);
  wl.forEach((t,i)=>{d.position.set(t[0],t[1],t[2]);d.rotation.set(0,t[3]*6.28,0);
    d.scale.setScalar(0.7+t[3]*0.9);d.updateMatrix();weedMesh.setMatrixAt(i,d.matrix);});
  scene.add(weedMesh);
}

/* 12d · bubbles rising from two vents */
let bubbleMesh;
{
  const bg=new THREE.SphereGeometry(0.032,6,5);
  const n=QUALITY.high.bubbles;
  bubbleMesh=new THREE.InstancedMesh(bg,M.bubble,n);
  bubbleMesh.userData.items=[];
  for(let i=0;i<n;i++) bubbleMesh.userData.items.push(newBubble());
  scene.add(bubbleMesh);
}
function newBubble(){
  const vent=Math.random()<0.5?[2.9,-2.6]:[-3.4,1.9];
  return {x:vent[0]+(Math.random()-0.5)*0.5, z:vent[1]+(Math.random()-0.5)*0.5,
          y:FLOOR+0.15+Math.random()*0.6, s:0.4+Math.random()*1.1, v:0.16+Math.random()*0.22,
          w:Math.random()*6.28};
}

/* ============================================================================
   13 · FX — droplets, chimney smoke, fireflies, gulls
   ========================================================================== */
let dropMesh; const drops=[];
{
  dropMesh=new THREE.InstancedMesh(new THREE.SphereGeometry(0.045,6,5),M.drop,90);
  dropMesh.frustumCulled=false; scene.add(dropMesh);
  dropMesh.renderOrder=16;
}
function splash(x,y,z,n=18,power=1){
  for(let i=0;i<n;i++){
    if(drops.length>86) break;
    const a=Math.random()*Math.PI*2, sp=(0.6+Math.random()*1.5)*power;
    drops.push({x,y,z,vx:Math.cos(a)*sp*0.42,vy:1.1+Math.random()*2.1*power,vz:Math.sin(a)*sp*0.42,
      life:0,max:0.7+Math.random()*0.6,s:0.35+Math.random()*0.9});
  }
  addRipple(x,z,Math.min(1,0.55*power));
  addRipple(x,z,Math.min(1,0.35*power));
  Audio.splash(clamp(power*0.6,0.15,1));
}
/* smoke: fully GPU, driven by an instance seed */
const smokeMat=new THREE.MeshStandardMaterial({color:'#e8e2d6',roughness:1,transparent:true,opacity:0.34,depthWrite:false});
smokeMat.onBeforeCompile=sh=>{
  sh.uniforms.uTime=U.uTime; sh.uniforms.uWindV=U.uWindV;
  sh.vertexShader=sh.vertexShader
    .replace('#include <common>','#include <common>\nuniform float uTime,uWindV;\nattribute float aSeed;\nvarying float vA;')
    .replace('#include <begin_vertex>',`#include <begin_vertex>
      float age=fract(uTime*0.14+aSeed);
      float sc=0.25+age*1.9;
      transformed *= sc;
      transformed.x += sin(aSeed*31.0+uTime*0.5)*0.30*age + uWindV*age*age*1.5;
      transformed.z += cos(aSeed*24.0+uTime*0.42)*0.26*age;
      transformed.y += age*2.1;
      vA=(1.0-age)*smoothstep(0.0,0.12,age);`)
  ;
  sh.fragmentShader=sh.fragmentShader
    .replace('#include <common>','#include <common>\nvarying float vA;')
    .replace('#include <opaque_fragment>','#include <opaque_fragment>\n gl_FragColor.a *= vA*0.9;');
  sh.transparent=true;
};
smokeMat.customProgramCacheKey=()=>'smoke';
{
  const n=16, geo=new THREE.SphereGeometry(0.16,7,6);
  const im=new THREE.InstancedMesh(geo,smokeMat,n);
  const seeds=new Float32Array(n); const d=new THREE.Object3D();
  for(let i=0;i<n;i++){seeds[i]=i/n;
    d.position.set(CHIMNEY_TOP.x,CHIMNEY_TOP.y,CHIMNEY_TOP.z);d.scale.setScalar(1);d.updateMatrix();
    im.setMatrixAt(i,d.matrix);}
  geo.setAttribute('aSeed',new THREE.InstancedBufferAttribute(seeds,1));
  im.renderOrder=18; scene.add(im);
}
/* fireflies */
let fireflyMat;
{
  const n=90, pos=new Float32Array(n*3), seed=new Float32Array(n);
  for(let i=0;i<n;i++){
    const a=Math.random()*6.28,r=1.2+Math.random()*2.6;
    pos[i*3]=Math.cos(a)*r+CABIN.x*0.4; pos[i*3+1]=0.6+Math.random()*1.6; pos[i*3+2]=Math.sin(a)*r+CABIN.y*0.4;
    seed[i]=Math.random();
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('aSeed',new THREE.BufferAttribute(seed,1));
  fireflyMat=new THREE.ShaderMaterial({
    transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    uniforms:{uTime:U.uTime,uNight:U.uNight},
    vertexShader:`attribute float aSeed;uniform float uTime,uNight;varying float vA;
      void main(){
        vec3 p=position;
        p.x+=sin(uTime*0.6+aSeed*30.0)*0.5; p.y+=sin(uTime*0.9+aSeed*17.0)*0.28; p.z+=cos(uTime*0.5+aSeed*23.0)*0.5;
        vA=uNight*(0.35+0.65*pow(0.5+0.5*sin(uTime*3.0+aSeed*40.0),2.0));
        vec4 mv=modelViewMatrix*vec4(p,1.0);
        gl_PointSize=(120.0/max(1.0,-mv.z))*(0.5+aSeed*0.6);
        gl_Position=projectionMatrix*mv;
      }`,
    fragmentShader:`varying float vA; void main(){
      float d=length(gl_PointCoord-0.5);
      float a=smoothstep(0.5,0.0,d)*vA;
      gl_FragColor=vec4(vec3(1.0,0.88,0.55)*a,a);
    }`
  });
  const pts=new THREE.Points(g,fireflyMat); pts.renderOrder=20; scene.add(pts);
}
/* gulls */
const gulls=[];
{
  const wing=new THREE.PlaneGeometry(0.34,0.13,1,2).translate(0.17,0,0);
  for(let i=0;i<QUALITY.high.gulls;i++){
    const g=new THREE.Group();
    const b=new THREE.Mesh(new THREE.SphereGeometry(0.07,6,5),M.gull); b.scale.set(0.6,0.7,2.0); g.add(b);
    const L=new THREE.Mesh(wing,M.gull), R=wing.clone()?new THREE.Mesh(wing,M.gull):null;
    L.position.x=-0.03; R.position.x=0.03; R.scale.x=-1;
    g.add(L,R); g.userData={L,R,phase:i*1.7,radius:4.6+i*0.9,y:4.3+i*0.5,sp:0.16+i*0.03,a:i*2.1};
    scene.add(g); gulls.push(g);
  }
}

/* ============================================================================
   14 · TIME OF DAY
   ========================================================================== */
const TOD = {
  day:{ sun:[0.55,0.78,0.42], sunCol:'#fff2d8', sunInt:2.55, hemiSky:'#c3e8f4', hemiGnd:'#88734f',
    hemiInt:0.9, amb:0.26, zenith:'#6fb2da', horizon:'#e6f2f4', below:'#2b3a40', sky:'#cfe8f0',
    mix:1.0, night:0, lamp:0, expo:1.0, sh:'#57d6c6', sd:'#0a5060', table:'#8a6a4a' },
  sunset:{ sun:[0.94,0.17,-0.26], sunCol:'#ff9a52', sunInt:2.15, hemiSky:'#f0b489', hemiGnd:'#5b4436',
    hemiInt:0.55, amb:0.20, zenith:'#3d5a8f', horizon:'#ffb27a', below:'#241d26', sky:'#f2c49b',
    mix:0.74, night:0.35, lamp:0.85, expo:1.05, sh:'#7fd9c2', sd:'#124a63', table:'#7a5236' },
  night:{ sun:[-0.42,0.66,-0.5], sunCol:'#a8bfee', sunInt:0.55, hemiSky:'#20364f', hemiGnd:'#141c24',
    hemiInt:0.24, amb:0.14, zenith:'#060f1e', horizon:'#1a3049', below:'#080d14', sky:'#16273c',
    mix:0.30, night:1.0, lamp:1.0, expo:1.16, sh:'#1f7f8e', sd:'#04222e', table:'#3a2a1e' }
};
const C = {
  sunCol:new THREE.Color(), hemiSky:new THREE.Color(), hemiGnd:new THREE.Color(),
  zenith:new THREE.Color(), horizon:new THREE.Color(), below:new THREE.Color(), sky:new THREE.Color(),
  sh:new THREE.Color(), sd:new THREE.Color()
};
const cur = {sunInt:2.55,hemiInt:.9,amb:.26,mix:1,night:0,lamp:0,expo:1};
const sunDir = new THREE.Vector3().fromArray(TOD.day.sun).normalize();
function applyTOD(dt){
  const t=TOD[S.tod], k=1-Math.exp(-dt*1.7);
  sunDir.lerp(_v.fromArray(t.sun).normalize(),k).normalize();
  C.sunCol.lerp(_c.set(t.sunCol),k); C.hemiSky.lerp(_c2.set(t.hemiSky),k);
  C.hemiGnd.lerp(_c3.set(t.hemiGnd),k); C.zenith.lerp(_c4.set(t.zenith),k);
  C.horizon.lerp(_c5.set(t.horizon),k); C.below.lerp(_c6.set(t.below),k);
  C.sky.lerp(_c7.set(t.sky),k); C.sh.lerp(_c8.set(t.sh),k); C.sd.lerp(_c9.set(t.sd),k);
  cur.sunInt=lerp(cur.sunInt,t.sunInt,k); cur.hemiInt=lerp(cur.hemiInt,t.hemiInt,k);
  cur.amb=lerp(cur.amb,t.amb,k); cur.mix=lerp(cur.mix,t.mix,k);
  cur.night=lerp(cur.night,t.night,k); cur.lamp=lerp(cur.lamp,t.lamp,k);
  cur.expo=lerp(cur.expo,t.expo,k);

  sun.position.copy(sunDir).multiplyScalar(17); sun.color.copy(C.sunCol); sun.intensity=cur.sunInt;
  hemi.color.copy(C.hemiSky); hemi.groundColor.copy(C.hemiGnd); hemi.intensity=cur.hemiInt;
  amb.intensity=cur.amb;
  renderer.toneMappingExposure=cur.expo;
  U.uSunDir.value.copy(sunDir); U.uSunCol.value.copy(C.sunCol);
  U.uSky.value.copy(C.sky); U.uShallow.value.copy(C.sh); U.uDeep.value.copy(C.sd);
  U.uLightMix.value=cur.mix; U.uNight.value=cur.night; U.uLamp.value=cur.lamp;
  skyMat.uniforms.uZenith.value.copy(C.zenith);
  skyMat.uniforms.uHorizon.value.copy(C.horizon);
  skyMat.uniforms.uBelow.value.copy(C.below);
  for(const m of LAMP_MESHES) m.emissiveIntensity=cur.lamp*2.4;
  M.glass.opacity=0.55+cur.lamp*0.3;
  lampLight.intensity=cur.lamp*3.4;
  pierLight.intensity=cur.lamp*2.6;
  pierLight2.intensity=cur.lamp*1.8;
  bounce.intensity=0.12+cur.mix*0.3;
}
const _v=new THREE.Vector3(),_c=new THREE.Color(),_c2=new THREE.Color(),_c3=new THREE.Color(),
      _c4=new THREE.Color(),_c5=new THREE.Color(),_c6=new THREE.Color(),_c7=new THREE.Color(),
      _c8=new THREE.Color(),_c9=new THREE.Color();
const LAMP_MESHES=[], FLUTTER=[]; let CHIMNEY_TOP=new THREE.Vector3();
applyTOD(1);

/* ============================================================================
   15 · AUDIO — procedural pad, pentatonic plucks, surf, breeze, splashes
   ========================================================================== */
const Audio = {
  ctx:null, ready:false,
  init(){
    if(this.ready) return;
    const AC = window.AudioContext||window.webkitAudioContext; if(!AC) return;
    const ctx = new AC(); this.ctx=ctx;
    const master = ctx.createGain(); master.gain.value=0; master.connect(ctx.destination);
    this.master=master;
    /* reverb */
    const conv=ctx.createConvolver(); conv.buffer=this.ir(2.8,2.4);
    const revG=ctx.createGain(); revG.gain.value=0.5; revG.connect(conv); conv.connect(master);
    this.rev=revG;
    /* noise source factory */
    const nb=this.noise(5); this.noiseBuf=nb;
    this.waves=this.layer(nb,{type:'lowpass',f:430,q:0.6,g:0.13,lfo:0.11,depth:0.075});
    this.breeze=this.layer(nb,{type:'bandpass',f:820,q:0.8,g:0.035,lfo:0.06,depth:0.022});
    /* music bus */
    const mb=ctx.createGain(); mb.gain.value=0.55; mb.connect(master); mb.connect(revG);
    this.music=mb;
    /* pad */
    const pf=ctx.createBiquadFilter(); pf.type='lowpass'; pf.frequency.value=620; pf.Q.value=0.7;
    const pg=ctx.createGain(); pg.gain.value=0.0; pf.connect(pg); pg.connect(mb);
    this.padFilter=pf; this.padGain=pg;
    this.padOsc=[0,1,2].map(i=>{
      const o=ctx.createOscillator(); o.type=i===0?'sine':'triangle';
      const g=ctx.createGain(); g.gain.value=0.32;
      o.connect(g); g.connect(pf); o.start(); return o;
    });
    this.ready=true;
    this.setVol(S.vol);
    this.applyMusic();
    this.chordAt=0; this.step=0; this.nextNote=ctx.currentTime+0.1;
    setInterval(()=>this.sched(),90);
  },
  noise(sec){
    const ctx=this.ctx, len=ctx.sampleRate*sec, b=ctx.createBuffer(1,len,ctx.sampleRate), d=b.getChannelData(0);
    let last=0;
    for(let i=0;i<len;i++){const w=Math.random()*2-1; last=(last+0.02*w)/1.02; d[i]=(last*3.2+w*0.4);}
    return b;
  },
  ir(sec,dec){
    const ctx=this.ctx, len=ctx.sampleRate*sec, b=ctx.createBuffer(2,len,ctx.sampleRate);
    for(let ch=0;ch<2;ch++){const d=b.getChannelData(ch);
      for(let i=0;i<len;i++) d[i]=(Math.random()*2-1)*Math.pow(1-i/len,dec);}
    return b;
  },
  layer(buf,{type,f,q,g,lfo,depth}){
    const ctx=this.ctx;
    const src=ctx.createBufferSource(); src.buffer=buf; src.loop=true;
    const flt=ctx.createBiquadFilter(); flt.type=type; flt.frequency.value=f; flt.Q.value=q;
    const gn=ctx.createGain(); gn.gain.value=g;
    const o=ctx.createOscillator(); o.frequency.value=lfo;
    const og=ctx.createGain(); og.gain.value=depth;
    o.connect(og); og.connect(gn.gain);
    src.connect(flt); flt.connect(gn); gn.connect(this.master);
    src.start(); o.start();
    return {gn,flt,base:g};
  },
  setVol(v){ if(!this.ready)return;
    this.master.gain.setTargetAtTime(S.audioOn?v*0.85:0, this.ctx.currentTime, 0.25); },
  applyMusic(){ if(!this.ready)return;
    this.padGain.gain.setTargetAtTime(S.musicOn?0.16:0, this.ctx.currentTime, 1.2);
    this.musicTarget=S.musicOn; },
  splash(amp){
    if(!this.ready||!S.audioOn) return;
    const ctx=this.ctx,t=ctx.currentTime;
    const src=ctx.createBufferSource(); src.buffer=this.noiseBuf;
    const f=ctx.createBiquadFilter(); f.type='bandpass'; f.Q.value=1.1;
    f.frequency.setValueAtTime(1900,t); f.frequency.exponentialRampToValueAtTime(260,t+0.45);
    const g=ctx.createGain(); g.gain.setValueAtTime(0.0001,t);
    g.gain.exponentialRampToValueAtTime(0.35*amp,t+0.02);
    g.gain.exponentialRampToValueAtTime(0.0001,t+0.7);
    src.connect(f); f.connect(g); g.connect(this.master); g.connect(this.rev);
    src.start(t); src.stop(t+0.8);
    const o=ctx.createOscillator(); o.type='sine';
    const og=ctx.createGain();
    o.frequency.setValueAtTime(150,t); o.frequency.exponentialRampToValueAtTime(58,t+0.28);
    og.gain.setValueAtTime(0.22*amp,t); og.gain.exponentialRampToValueAtTime(0.0001,t+0.35);
    o.connect(og); og.connect(this.master); o.start(t); o.stop(t+0.4);
  },
  click(hi){
    if(!this.ready||!S.audioOn) return;
    const ctx=this.ctx,t=ctx.currentTime;
    const o=ctx.createOscillator(); o.type='triangle';
    o.frequency.setValueAtTime(hi?1180:760,t);
    const g=ctx.createGain(); g.gain.setValueAtTime(0.05,t);
    g.gain.exponentialRampToValueAtTime(0.0001,t+0.09);
    o.connect(g); g.connect(this.master); o.start(t); o.stop(t+0.1);
  },
  /* scheduler */
  CHORDS:[[50,57,62,66],[48,55,60,64],[47,54,59,62],[45,52,57,61]],
  PENT:[0,2,4,7,9,12,14,16],
  sched(){
    if(!this.ready||!S.audioOn||!S.musicOn) return;
    const ctx=this.ctx, ahead=ctx.currentTime+0.35;
    while(this.nextNote<ahead){
      const t=this.nextNote, bar=this.step%16;
      if(bar%8===0){
        const ch=this.CHORDS[(this.step/16|0)%4];
        this.padOsc.forEach((o,i)=>o.frequency.setTargetAtTime(440*Math.pow(2,(ch[i]-69)/12),t,1.4));
      }
      if(bar%2===0 && Math.random()<0.62){
        const ch=this.CHORDS[(this.step/16|0)%4];
        const n=ch[(Math.random()*ch.length)|0]+12+this.PENT[(Math.random()*this.PENT.length)|0];
        this.pluck(440*Math.pow(2,(n-69)/12), t, 0.11+Math.random()*0.06);
      }
      this.nextNote+=0.5; this.step++;
    }
  },
  pluck(f,t,a){
    const ctx=this.ctx;
    const o=ctx.createOscillator(); o.type='triangle'; o.frequency.value=f;
    const o2=ctx.createOscillator(); o2.type='sine'; o2.frequency.value=f*2.01;
    const g=ctx.createGain(); g.gain.setValueAtTime(0.0001,t);
    g.gain.exponentialRampToValueAtTime(a,t+0.012);
    g.gain.exponentialRampToValueAtTime(0.0001,t+1.5);
    const g2=ctx.createGain(); g2.gain.value=0.22;
    o.connect(g); o2.connect(g2); g2.connect(g); g.connect(this.music);
    o.start(t); o2.start(t); o.stop(t+1.6); o2.stop(t+1.6);
  },
  setAmbience(){ if(!this.ready)return;
    const on=S.audioOn?1:0;
    this.waves.gn.gain.setTargetAtTime(on*(0.055+S.wind*0.13),this.ctx.currentTime,0.6);
    this.waves.flt.frequency.setTargetAtTime(300+S.wind*420,this.ctx.currentTime,0.6);
    this.breeze.gn.gain.setTargetAtTime(on*(0.012+S.wind*0.075),this.ctx.currentTime,0.8);
  }
};

/* ============================================================================
   16 · CAMERA PRESETS + SMOOTH FLIGHT
   ========================================================================== */
const VIEWS = {
  island:{p:[9.6,7.4,11.2], t:[0,0.15,0], haze:0, min:6, max:34, name:'Island'},
  cabin: {p:[5.35,2.55,7.4], t:[0.30,1.05,1.20], haze:0, min:3, max:24, name:'Cabin & Pier'},
  under: {p:[0.15,-0.92,6.35], t:[-0.35,-1.15,-0.55], haze:1, min:2.2, max:20, name:'Underwater'}
};
const flight={on:false,t:0,dur:1.5,p0:new THREE.Vector3(),p1:new THREE.Vector3(),
  t0:new THREE.Vector3(),t1:new THREE.Vector3()};
function flyTo(key){
  const v=VIEWS[key]; S.view=key;
  flight.p0.copy(camera.position); flight.p1.fromArray(v.p);
  flight.t0.copy(controls.target); flight.t1.fromArray(v.t);
  flight.t=0; flight.on=true;
  controls.enabled=false;
  controls.minDistance=v.min; controls.maxDistance=v.max;
  document.getElementById('haze').style.opacity=v.haze;
  document.getElementById('viewName').textContent=v.name;
  document.querySelectorAll('.cam').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===key)));
}
function updateFlight(dt){
  if(!flight.on) return;
  flight.t=Math.min(1,flight.t+dt/flight.dur);
  const e=flight.t<0.5?4*flight.t**3:1-Math.pow(-2*flight.t+2,3)/2;
  camera.position.lerpVectors(flight.p0,flight.p1,e);
  controls.target.lerpVectors(flight.t0,flight.t1,e);
  if(flight.t>=1){flight.on=false;controls.enabled=true;}
}

/* ============================================================================
   17 · UI WIRING
   ========================================================================== */
const $=s=>document.querySelector(s);
const setP=el=>el.style.setProperty('--p',((el.value-el.min)/(el.max-el.min)*100)+'%');

document.querySelectorAll('.cam').forEach(b=>b.addEventListener('click',()=>{
  Audio.click(true); flyTo(b.dataset.view==='under'?'under':b.dataset.view);}));
document.querySelectorAll('.tod').forEach(b=>b.addEventListener('click',()=>{
  S.tod=b.dataset.tod; Audio.click(true);
  document.querySelectorAll('.tod').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  $('#cTod').textContent=b.textContent;
  $('#statusWord').textContent = S.tod==='day'?'the tide is turning':S.tod==='sunset'?'lanterns coming on':'the island is asleep';
}));
document.querySelectorAll('.q').forEach(b=>b.addEventListener('click',()=>{
  S.quality=b.dataset.q; Audio.click(false);
  document.querySelectorAll('.q').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  applyQuality();
}));
$('#tide').addEventListener('input',e=>{S.tideTarget=+e.target.value/100;setP(e.target);});
$('#wind').addEventListener('input',e=>{S.windTarget=+e.target.value/100;setP(e.target);Audio.setAmbience();});
$('#vol').addEventListener('input',e=>{S.vol=+e.target.value/100;setP(e.target);Audio.setVol();});
$('#btnKayak').addEventListener('click',()=>toggleKayak());
$('#btnRay').addEventListener('click',()=>leap());
$('#btnPause').addEventListener('click',()=>togglePause());
$('#btnReset').addEventListener('click',()=>resetAll());
$('#btnSound').addEventListener('click',()=>{
  S.audioOn=!S.audioOn;
  $('#btnSound').setAttribute('aria-pressed',String(S.audioOn));
  $('#soundLabel').textContent=S.audioOn?'Sound on':'Sound off';
  if(S.audioOn){Audio.init();Audio.ctx&&Audio.ctx.resume();Audio.setVol();Audio.setAmbience();Audio.click(true);}
  else Audio.setVol();
});
$('#btnMusic').addEventListener('click',()=>{
  S.musicOn=!S.musicOn;
  $('#btnMusic').setAttribute('aria-pressed',String(S.musicOn));
  if(!S.audioOn) $('#btnSound').click();
  Audio.applyMusic(); Audio.click(false);
});
$('#menuBtn').addEventListener('click',()=>{document.body.classList.toggle('menu-open');Audio.click(false);});
addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT') return;
  const k=e.key.toLowerCase();
  if(k==='1')flyTo('island'); else if(k==='2')flyTo('cabin'); else if(k==='3')flyTo('under');
  else if(k==='k')toggleKayak(); else if(k==='r')leap();
  else if(k===' '){e.preventDefault();togglePause();}
  else if(k==='t')resetAll(); else if(k==='m')$('#btnMusic').click();
});
[...document.querySelectorAll('.btn')].forEach(b=>b.addEventListener('pointerenter',()=>Audio.click(false)));
['tide','wind','vol'].forEach(id=>setP($('#'+id)));

function toggleKayak(){
  Audio.click(true);
  if(S.kayakMode==='dock'){S.kayakMode='cruise';S.kayakVel=0;}
  else if(S.kayakMode==='cruise'){S.kayakMode='return';}
  else {S.kayakMode='dock';}
  $('#btnKayak').setAttribute('aria-pressed',String(S.kayakMode!=='dock'));
  $('#kayakLabel').textContent = S.kayakMode==='dock'?'Launch kayak':S.kayakMode==='cruise'?'Bring it home':'Return to dock';
  $('#cKayak').innerHTML='Kayak <b>'+(S.kayakMode==='dock'?'moored':S.kayakMode==='cruise'?'on the lap':'heading in')+'</b>';
  $('#cKayak').classList.toggle('on',S.kayakMode!=='dock');
}
function togglePause(){
  S.paused=!S.paused;
  $('#btnPause').setAttribute('aria-pressed',String(S.paused));
  $('#pauseLabel').textContent=S.paused?'Resume':'Pause';
}
function resetAll(){
  Audio.click(true);
  S.tideTarget=0.02; S.windTarget=0.45; S.tod='day';
  $('#tide').value=2; $('#wind').value=45; setP($('#tide')); setP($('#wind'));
  document.querySelectorAll('.tod').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.tod==='day')));
  $('#cTod').textContent='Day';
  if(S.kayakMode!=='dock') toggleKayak();
  S.paused=false; $('#btnPause').setAttribute('aria-pressed','false'); $('#pauseLabel').textContent='Pause';
  flyTo('island');
  $('#statusWord').textContent='the tide is turning';
}
function applyQuality(){
  const q=QUALITY[S.quality];
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,q.dpr));
  sun.shadow.mapSize.set(q.shadow,q.shadow);
  if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null;}
  ground.geometry.dispose(); ground.geometry=createGroundGeometry(q.g[0],q.g[1]);
  waterSurf.geometry.dispose(); waterSurf.geometry=surfaceGeo(q.wseg);
  grassMesh.count=Math.min(grassMesh.instanceMatrix.count,q.grass);
  kelpMesh.count=Math.min(kelpMesh.instanceMatrix.count,q.kelp);
  weedMesh.count=Math.min(weedMesh.instanceMatrix.count,Math.round(q.kelp*1.6));
  bubbleMesh.count=Math.min(bubbleMesh.instanceMatrix.count,q.bubbles);
  schools.forEach(s=>s.im.count=Math.min(s.n,q.fish*(s===schools[0]?1:0.75)|0));
  gulls.forEach((g,i)=>g.visible=i<q.gulls);
  resize();
}

/* ============================================================================
   18 · RESIZE
   ========================================================================== */
function resize(){
  const w=innerWidth,h=innerHeight;
  camera.aspect=w/h; camera.updateProjectionMatrix();
  renderer.setSize(w,h,false);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,QUALITY[S.quality].dpr));
}
addEventListener('resize',resize); resize();

/* ============================================================================
   19 · ANIMATION LOOP
   ========================================================================== */
const clock=new THREE.Clock();
let fpsAcc=0,fpsN=0,uiAcc=0;
const dummy=new THREE.Object3D();

function tick(){
  requestAnimationFrame(tick);
  const dt=Math.min(clock.getDelta(),0.05);
  const raw=dt;
  if(!S.paused) S.t+=dt;

  /* smooth tide & wind */
  S.tide=damp(S.tide,S.tideTarget,4,dt);
  S.wind=damp(S.wind,S.windTarget,3,dt);
  U.uTime.value=S.t; U.uWater.value=S.tide; U.uWindV.value=S.wind;
  U.uWaveE.value=0.35+S.wind*0.9;
  applyTOD(raw);

  waterSurf.position.y=S.tide;
  waterVol.position.y=(RIM+FLOOR)/2;
  ripPlane.position.y=S.tide+0.014;
  surfMat.uniforms.uCam.value.copy(camera.position);

  /* ripples age */
  for(const r of RIP){ if(r.w>0){ r.y+=dt*0.85; if(r.y>1.25) r.w=0; } }

  /* ambient droplets → ripples */
  if(!S.paused && Math.random()<dt*0.35){
    const a=Math.random()*6.28, rr=1.4+Math.random()*3.2;
    addRipple(Math.cos(a)*rr,Math.sin(a)*rr,0.18+Math.random()*0.2);
  }

  /* fluttering cloth */
  for(const f of FLUTTER){
    const p=f.m.geometry.attributes.position;
    if(!f.orig) f.orig=Float32Array.from(p.array);
    for(let i=0;i<p.count;i++){
      const x=f.orig[i*3],y=f.orig[i*3+1];
      const k=(0.5-y/0.62);
      p.array[i*3+2]=Math.sin(S.t*2.6+x*7+f.base)*f.k*k*(0.3+S.wind*1.6);
      p.array[i*3]=x+Math.sin(S.t*1.7+y*4)*f.k*0.4*k;
    }
    p.needsUpdate=true; f.m.geometry.computeVertexNormals();
  }

  updateKayak(dt);
  updateRays(dt);
  updateSchools(dt);
  updateBubbles(dt);
  updateDrops(dt);
  updateGulls(dt);

  /* gull + firefly visibility by hour */
  gulls.forEach(g=>{g.visible=g.visible;});

  updateFlight(raw);
  controls.update();
  renderer.render(scene,camera);

  /* HUD */
  fpsAcc+=1/Math.max(raw,1e-4); fpsN++; uiAcc+=raw;
  if(uiAcc>0.28){
    $('#cTide').textContent=(S.tide>=0?'+':'')+S.tide.toFixed(2);
    $('#tideVal').textContent=(S.tide>=0?'+':'')+S.tide.toFixed(2)+' m';
    $('#cWind').textContent=Math.round(S.wind*100)+'%';
    $('#windVal').textContent=Math.round(S.wind*100)+'%';
    $('#volVal').textContent=Math.round(S.vol*100)+'%';
    $('#cFps').textContent=Math.round(fpsAcc/fpsN)+' fps';
    fpsAcc=0;fpsN=0;uiAcc=0;
  }
}

/* --- kayak ------------------------------------------------------------- */
const KAYAK_START = kayakPath.shiftPoint;
function updateKayak(dt){
  if(S.paused) dt=0;
  const speed=0.052;
  if(S.kayakMode==='cruise'){
    S.kayakVel=damp(S.kayakVel,1,1.2,dt);
    S.kayakU=(S.kayakU+S.kayakVel*speed*dt)%1;
  } else if(S.kayakMode==='return'){
    S.kayakVel=damp(S.kayakVel,1,1.6,dt);
    S.kayakU-=S.kayakVel*speed*1.15*dt;
    if(S.kayakU<=0){S.kayakU=0;S.kayakMode='dock';
      $('#btnKayak').setAttribute('aria-pressed','false');
      $('#kayakLabel').textContent='Launch kayak';
      $('#cKayak').innerHTML='Kayak <b>moored</b>';$('#cKayak').classList.remove('on');
      splash(kayak.position.x,S.tide,kayak.position.z,7,0.35);}
  } else S.kayakVel=damp(S.kayakVel,0,2,dt);

  const u=(KAYAK_START+S.kayakU)%1;
  const p=kayakPath.getPointAt(u);
  const tan=kayakPath.getTangentAt(u);
  const amp=waveAmp();
  const wy=S.tide+waveH(p.x,p.z,S.t,amp)+0.055;
  const docked=S.kayakMode==='dock';
  if(docked){
    const a=pier.rotation.y;
    kayak.position.set(PIER_B.x+Math.cos(a)*0.75+Math.sin(a)*0.55, 0, PIER_B.z-Math.sin(a)*0.75+Math.cos(a)*0.55);
    kayak.position.y=S.tide+waveH(kayak.position.x,kayak.position.z,S.t,amp)+0.05;
    kayak.rotation.set(Math.sin(S.t*1.1)*0.05*(0.4+S.wind), a+0.3, Math.cos(S.t*0.9)*0.06*(0.4+S.wind));
  } else {
    kayak.position.set(p.x,wy,p.z);
    const yaw=Math.atan2(tan.x,tan.z);
    const slopeF=(waveH(p.x+0.2,p.z,S.t,amp)-waveH(p.x-0.2,p.z,S.t,amp))/0.4;
    const slopeR=(waveH(p.x,p.z+0.2,S.t,amp)-waveH(p.x,p.z-0.2,S.t,amp))/0.4;
    kayak.rotation.set(-slopeR*0.9, yaw, slopeF*0.9+Math.sin(S.t*3.1)*0.05*S.kayakVel);
    if(Math.random()<dt*1.4) addRipple(p.x,p.z,0.12);
  }
}

/* --- rays -------------------------------------------------------------- */
function updateRays(dt){
  if(S.paused) dt=0;
  rayUniforms.uTime.value=S.t;
  for(const r of rays){
    if(r.leap>0){
      r.leapT+=dt/2.35;
      const p=Math.min(1,r.leapT);
      const from=r.leapFrom, to=r.leapTo;
      const x=lerp(from.x,to.x,p), z=lerp(from.z,to.z,p);
      const h=1.55+Math.abs(S.tide-from.y);
      const y=lerp(from.y,to.y,p)+4*h*p*(1-p)*0.62;
      r.g.position.set(x,y,z);
      /* pitch follows the arc, plus a full roll through the air */
      const dy=4*h*(1-2*p)*0.62, dxz=Math.hypot(to.x-from.x,to.z-from.z)/2.35;
      const pitch=Math.atan2(dy,dxz);
      const yaw=Math.atan2(to.x-from.x,to.z-from.z)+Math.PI*p*0.9;
      r.g.rotation.set(-pitch,yaw,Math.sin(p*Math.PI)*Math.PI*1.0);
      rayUniforms.uFlap.value=1.7;
      if(p>=1){
        r.leap=0; rayUniforms.uFlap.value=1;
        r.g.position.copy(to);
        splash(to.x,S.tide,to.z,26,1.15);
        r.vel.set((to.x-from.x)*0.2,0.1,(to.z-from.z)*0.2);
        r.target.copy(randomRayPoint());
        $('#cRay').innerHTML='Rays <b>gliding</b>'; $('#cRay').classList.remove('on');
      }
      continue;
    }
    /* wander inside the lagoon, steer away from shore / walls / surface */
    const p=r.g.position;
    const d=r.target.clone().sub(p);
    if(d.length()<0.7) r.target.copy(randomRayPoint());
    r.vel.lerp(d.normalize().multiplyScalar(r.speed),1-Math.exp(-dt*0.9));
    /* keep clear of the island cone and the tank walls */
    const rad=Math.hypot(p.x,p.z);
    if(rad<2.35){const n=new THREE.Vector3(p.x,0,p.z).normalize();r.vel.addScaledVector(n,(2.35-rad)*2.2);}
    if(Math.abs(p.x)>4.4) r.vel.x-=Math.sign(p.x)*(Math.abs(p.x)-4.4)*2.4;
    if(Math.abs(p.z)>3.3) r.vel.z-=Math.sign(p.z)*(Math.abs(p.z)-3.3)*2.4;
    const ceil=S.tide-0.42, bed=Math.max(islandHeight(p.x,p.z),FLOOR)+0.30;
    if(p.y>ceil) r.vel.y-=(p.y-ceil)*2.2;
    if(p.y<bed)  r.vel.y+=(bed-p.y)*2.2;
    p.addScaledVector(r.vel,dt);
    p.y=clamp(p.y,Math.max(bed,FLOOR+0.12),Math.min(ceil,0.6));
    /* orientation + banking */
    const v=r.vel.clone(); if(v.lengthSq()<1e-5) v.set(0,0,1);
    const yaw=Math.atan2(v.x,v.z);
    const pitch=clamp(-Math.atan2(v.y,Math.hypot(v.x,v.z)),-0.6,0.6);
    const dYaw=-(yaw-r.roll);
    r.roll=yaw;
    r.g.rotation.set(pitch,yaw,clamp(dYaw*2.2,-0.75,0.75));
  }
}
function leap(){
  if(S.leaping) return;
  Audio.click(true);
  /* pick the ray closest to the front glass */
  let best=rays[0],bd=-1e9;
  for(const r of rays){ if(r.leap>0) continue; const s=r.g.position.z-r.g.position.x*0.2; if(s>bd){bd=s;best=r;} }
  const r=best;
  const dir=new THREE.Vector3(r.g.position.x,0,r.g.position.z).normalize();
  if(dir.lengthSq()<0.01) dir.set(0,0,1);
  const out=new THREE.Vector3(r.g.position.x,0,r.g.position.z).addScaledVector(dir,1.9);
  out.x=clamp(out.x,-4.3,4.3); out.z=clamp(out.z,-3.2,3.6);
  r.leapFrom.copy(r.g.position); r.leapFrom.y=S.tide-0.12;
  r.leapTo.set(out.x,Math.max(FLOOR+0.5,S.tide-0.9),out.z);
  r.leapT=0; r.leap=1; S.leaping=true;
  splash(r.leapFrom.x,S.tide,r.leapFrom.z,16,0.8);
  $('#cRay').innerHTML='Rays <b>airborne!</b>'; $('#cRay').classList.add('on');
}

/* --- fish -------------------------------------------------------------- */
function updateSchools(dt){
  if(S.paused) dt=0;
  for(const s of schools){
    s.t+=dt*s.spd;
    const cx=s.cx+Math.cos(s.t)*s.rad, cz=s.cz+Math.sin(s.t*1.27)*s.rad*0.8;
    const cy=clamp(s.depth+Math.sin(s.t*0.8)*0.22, FLOOR+0.35, S.tide-0.30);
    const n=s.im.count;
    for(let i=0;i<n;i++){
      const o=s.off[i];
      const a=o.a+s.t*o.sp*1.5;
      const r=o.r*(1+0.12*Math.sin(s.t*2+o.ph));
      const x=cx+Math.cos(a)*r, z=cz+Math.sin(a)*r*0.85;
      const y=clamp(cy+o.y*0.55+Math.sin(s.t*1.7+o.ph)*0.10, FLOOR+0.18, S.tide-0.16);
      const tx=-Math.sin(a)*r*o.sp*1.5, tz=Math.cos(a)*r*0.85*o.sp*1.5;
      dummy.position.set(x,y,z);
      dummy.lookAt(x+tx,y,z+tz);
      dummy.scale.setScalar(o.s*(0.8+0.25*Math.sin(s.t*4+o.ph)));
      dummy.updateMatrix();
      s.im.setMatrixAt(i,dummy.matrix);
    }
    s.im.instanceMatrix.needsUpdate=true;
  }
}

/* --- bubbles / droplets / gulls --------------------------------------- */
function updateBubbles(dt){
  if(S.paused) dt=0;
  const items=bubbleMesh.userData.items;
  for(let i=0;i<bubbleMesh.count;i++){
    const b=items[i];
    b.y+=b.v*dt; b.x+=Math.sin(S.t*2+b.w)*0.06*dt; b.z+=Math.cos(S.t*1.7+b.w)*0.06*dt;
    if(b.y>S.tide-0.05){
      items[i]=newBubble();
      if(Math.random()<0.25) addRipple(b.x,b.z,0.09);
    }
    dummy.position.set(b.x,b.y,b.z); dummy.scale.setScalar(b.s); dummy.rotation.set(0,0,0);
    dummy.updateMatrix(); bubbleMesh.setMatrixAt(i,dummy.matrix);
  }
  bubbleMesh.instanceMatrix.needsUpdate=true;
}
function updateDrops(dt){
  if(S.paused) dt=0;
  let n=0;
  for(let i=drops.length-1;i>=0;i--){
    const d=drops[i];
    d.life+=dt; d.vy-=9.2*dt;
    d.x+=d.vx*dt; d.y+=d.vy*dt; d.z+=d.vz*dt;
    if(d.y<S.tide&&d.vy<0){
      if(Math.random()<0.5) addRipple(d.x,d.z,0.05);
      drops.splice(i,1); continue;
    }
    if(d.life>d.max){drops.splice(i,1);continue;}
    if(n<dropMesh.count){
      const k=1-d.life/d.max;
      dummy.position.set(d.x,d.y,d.z); dummy.scale.setScalar(d.s*k*1.1);
      dummy.updateMatrix(); dropMesh.setMatrixAt(n++,dummy.matrix);
    }
  }
  for(let i=n;i<dropMesh.count;i++){dummy.position.set(0,-99,0);dummy.scale.setScalar(0.0001);
    dummy.updateMatrix();dropMesh.setMatrixAt(i,dummy.matrix);}
  dropMesh.instanceMatrix.needsUpdate=true;
}
function updateGulls(dt){
  if(S.paused) dt=0;
  for(const g of gulls){
    if(!g.visible) continue;
    const u=g.userData;
    u.a+=dt*u.sp;
    g.position.set(Math.cos(u.a)*u.radius, u.y+Math.sin(u.a*2)*0.28, Math.sin(u.a)*u.radius*0.85);
    g.rotation.y=-u.a+Math.PI/2;
    const f=Math.sin(S.t*6+u.phase)*0.55;
    u.L.rotation.z=f; u.R.rotation.z=-f;
  }
}

/* ============================================================================
   20 · BOOT
   ========================================================================== */
applyQuality();
flyTo('island'); flight.t=1; flight.on=false; controls.enabled=true;
camera.position.fromArray(VIEWS.island.p); controls.target.fromArray(VIEWS.island.t);
tick();
setTimeout(()=>document.getElementById('boot').classList.add('gone'),900);
setTimeout(()=>{
  const b=document.getElementById('boot'); if(b) b.remove();
},2200);
</script>
</body>
</html>
```

**What's inside, briefly**

- **Cutaway logic.** The island is generated from one analytic height function that is compiled *identically* into GLSL. The water surface discards fragments where that function rises above the tide, so the shoreline is a perfect conforming cut — no z-fighting, no harsh intersections. The water *volume* is a single-sided box that discards above the tide line, so it tints only submerged geometry (never the island above water). Draw order is fixed: bubbles → volume → surface → ripples → glass, all `depthWrite:false`.
- **Cross-section.** The ground mesh is extruded into a solid block with sediment-strata skirts, framed in wood with corner posts, a plinth and a canvas-drawn brass nameplate.
- **Life.** Four shader-animated rays (undulating fins baked into a parametric disc), two boid-ish instanced schools, kelp, seagrass, bubble vents, GPU chimney smoke, fireflies, gulls, fluttering laundry and a pennant.
- **Everything is live:** tide drives foam bands, wet sand, floats, ray ceilings and the glass waterline; wind drives waves, shoaling, sway and the breeze layer in the mix; the hour lerps sun, sky, stars, exposure and lamps together.