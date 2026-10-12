# Tidehaven

A single-file, fully procedural WebGL diorama. Everything below — island, cabin, rays, fish, water, audio — is generated in code.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>Tidehaven — Island Diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,500;9..144,700;9..144,900&family=Karla:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* ============================================================
   TIDEHAVEN — UI
   Palette: deep sea ink, warm sand, copper, lagoon teal
   ============================================================ */
:root{
  --ink:#04202a; --ink2:#082c38; --panel:rgba(6,30,39,.74);
  --line:rgba(232,212,174,.16); --line-hi:rgba(232,212,174,.32);
  --sand:#f2e5c8; --sand-dim:#a89e88; --copper:#e08b4c; --copper-hi:#f6b274;
  --sea:#63d9c8;
  --shadow:0 24px 60px -28px rgba(0,0,0,.9), inset 0 1px 0 rgba(255,255,255,.05);
  --r:14px;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#04141c}
body{
  font-family:'Karla',system-ui,sans-serif;color:var(--sand);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
  overscroll-behavior:none;
}
canvas#scene{position:fixed;inset:0;width:100%;height:100%;display:block;touch-action:none}

/* ---- atmosphere overlays ---- */
.vig{position:fixed;inset:0;pointer-events:none;z-index:2;
  background:radial-gradient(115% 85% at 52% 42%, rgba(0,0,0,0) 42%, rgba(2,12,18,.42) 88%, rgba(1,8,12,.72) 100%);
  mix-blend-mode:multiply}
.grain{position:fixed;inset:-50%;pointer-events:none;z-index:3;opacity:.055;
  background-image:radial-gradient(rgba(255,255,255,.9) .5px, transparent .6px);
  background-size:3px 3px;animation:grain 6s steps(6) infinite}
@keyframes grain{0%{transform:translate(0,0)}20%{transform:translate(-2%,1%)}40%{transform:translate(1%,-2%)}60%{transform:translate(-1%,2%)}80%{transform:translate(2%,-1%)}100%{transform:translate(0,0)}}
.uw{position:fixed;inset:0;pointer-events:none;z-index:2;opacity:0;transition:opacity .5s ease;
  background:
    radial-gradient(120% 90% at 50% 0%, rgba(150,255,235,.16), rgba(0,0,0,0) 55%),
    linear-gradient(180deg, rgba(20,140,140,.30), rgba(3,42,58,.55) 60%, rgba(1,20,32,.7));
  mix-blend-mode:multiply}
.uw.on{opacity:1}

/* ---- shell ---- */
#ui{position:fixed;inset:0;z-index:5;pointer-events:none;
  padding:clamp(12px,2vw,22px);display:grid;
  grid-template-columns:326px 1fr auto;grid-template-rows:auto 1fr auto;
  gap:14px;align-items:start}
.panel{pointer-events:auto;background:var(--panel);border:1px solid var(--line);
  border-radius:var(--r);box-shadow:var(--shadow);
  backdrop-filter:blur(16px) saturate(1.25);-webkit-backdrop-filter:blur(16px) saturate(1.25);
  padding:14px 15px}
.rise{animation:rise .8s cubic-bezier(.16,.84,.3,1) both}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

/* ---- brand ---- */
.brand{grid-column:1;grid-row:1;max-width:326px}
.kicker{font-size:9.5px;letter-spacing:.26em;text-transform:uppercase;color:var(--copper);
  display:flex;align-items:center;gap:8px;margin-bottom:6px;font-weight:700}
.kicker::before{content:"";width:16px;height:1px;background:linear-gradient(90deg,var(--copper),transparent)}
h1{font-family:'Fraunces',Georgia,serif;font-weight:900;font-size:clamp(40px,5.2vw,60px);
  line-height:.86;letter-spacing:-.035em;color:#fbf2df;
  font-variation-settings:'SOFT' 40,'WONK' 1}
h1 em{font-style:normal;color:var(--copper)}
.sub{font-size:12.5px;line-height:1.5;color:var(--sand-dim);margin-top:9px;max-width:27ch}
.rule{height:1px;background:linear-gradient(90deg,var(--line-hi),transparent);margin:11px 0 10px}
.readout{display:flex;gap:14px;flex-wrap:wrap;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--sand-dim)}
.readout b{display:block;font-family:'Fraunces',serif;font-size:15px;letter-spacing:0;
  color:var(--sand);font-weight:700;font-variant-numeric:tabular-nums;text-transform:none;margin-top:2px}
.live{width:6px;height:6px;border-radius:50%;background:var(--sea);display:inline-block;margin-right:5px;
  box-shadow:0 0 0 0 rgba(99,217,200,.6);animation:pulse 2.4s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(99,217,200,.55)}70%{box-shadow:0 0 0 7px rgba(99,217,200,0)}100%{box-shadow:0 0 0 0 rgba(99,217,200,0)}}

/* ---- control stack ---- */
.stack{grid-column:1;grid-row:2;display:flex;flex-direction:column;gap:11px;align-self:end;
  max-height:100%;overflow:auto;padding-bottom:2px;scrollbar-width:thin}
.stack::-webkit-scrollbar{width:4px}.stack::-webkit-scrollbar-thumb{background:var(--line-hi);border-radius:9px}
h2{font-family:'Fraunces',serif;font-size:11px;font-weight:700;letter-spacing:.2em;
  text-transform:uppercase;color:var(--copper);margin-bottom:11px;display:flex;justify-content:space-between;align-items:center}
h2 span{font-family:'Karla';font-size:9.5px;letter-spacing:.08em;color:var(--sand-dim);text-transform:none;font-weight:400}
.row{display:flex;gap:7px;flex-wrap:wrap}
.btn{flex:1 1 auto;font:700 10px/1 'Karla',sans-serif;letter-spacing:.13em;text-transform:uppercase;
  padding:9px 10px;border-radius:9px;background:rgba(242,229,200,.055);border:1px solid var(--line);
  color:var(--sand);cursor:pointer;transition:transform .18s cubic-bezier(.2,.9,.3,1.2),background .2s,border-color .2s,color .2s;
  position:relative;overflow:hidden;white-space:nowrap}
.btn::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.18) 50%,transparent 65%);
  transform:translateX(-110%);transition:transform .55s}
.btn:hover{background:rgba(224,139,76,.14);border-color:rgba(224,139,76,.45);transform:translateY(-1.5px)}
.btn:hover::after{transform:translateX(110%)}
.btn:active{transform:translateY(0) scale(.98)}
.btn.on{background:linear-gradient(180deg,var(--copper-hi),#c9702f);color:#20100a;border-color:#f3ab6d;
  box-shadow:0 8px 20px -10px rgba(224,139,76,.9)}
.btn.sea.on{background:linear-gradient(180deg,#7fe9d6,#2ba79a);color:#03252a;border-color:#8ff0df;box-shadow:0 8px 20px -10px rgba(99,217,200,.9)}
.seg{display:flex;gap:0;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:rgba(0,0,0,.18)}
.seg .btn{border:0;border-radius:0;flex:1;box-shadow:none}
.seg .btn+.btn{border-left:1px solid var(--line)}
.field{margin-bottom:13px}
.field:last-child{margin-bottom:0}
.lab{display:flex;justify-content:space-between;align-items:baseline;font-size:9.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--sand-dim);margin-bottom:7px}
.lab b{font:700 11px/1 'Karla';color:var(--sand);letter-spacing:.04em;font-variant-numeric:tabular-nums}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:20px;background:transparent;cursor:pointer;display:block}
input[type=range]::-webkit-slider-runnable-track{height:4px;border-radius:4px;
  background:linear-gradient(90deg,var(--copper) 0 var(--v,50%),rgba(242,229,200,.14) var(--v,50%) 100%)}
input[type=range]::-moz-range-track{height:4px;border-radius:4px;background:rgba(242,229,200,.14)}
input[type=range]::-moz-range-progress{height:4px;border-radius:4px;background:var(--copper)}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;
  background:#fdf3e2;border:2px solid var(--copper);margin-top:-5px;
  box-shadow:0 2px 8px rgba(0,0,0,.5);transition:transform .16s}
input[type=range]:hover::-webkit-slider-thumb{transform:scale(1.2)}
input[type=range]::-moz-range-thumb{width:12px;height:12px;border-radius:50%;background:#fdf3e2;border:2px solid var(--copper)}
select{width:100%;font:700 10px/1 'Karla';letter-spacing:.1em;text-transform:uppercase;color:var(--sand);
  background:rgba(0,0,0,.28);border:1px solid var(--line);border-radius:8px;padding:8px 9px;cursor:pointer}
select:focus,input:focus-visible,.btn:focus-visible{outline:2px solid var(--copper);outline-offset:2px}

/* ---- camera bar ---- */
.cams{grid-column:2/4;grid-row:3;justify-self:center;align-self:end;display:flex;gap:6px;padding:7px;
  pointer-events:auto;background:var(--panel);border:1px solid var(--line);border-radius:999px;box-shadow:var(--shadow);
  backdrop-filter:blur(16px) saturate(1.25);-webkit-backdrop-filter:blur(16px) saturate(1.25)}
.cams .btn{border-radius:999px;flex:0 0 auto;padding:9px 15px}
.cams .btn.on::before{content:"";width:5px;height:5px;border-radius:50%;background:currentColor;display:inline-block;
  margin-right:6px;vertical-align:1px;animation:pulse 2s infinite}

/* ---- audio ---- */
.audio{grid-column:3;grid-row:2;align-self:end;justify-self:end;width:214px}
.audiorow{display:flex;align-items:center;gap:9px}
.icon{width:36px;height:36px;flex:none;border-radius:10px;display:grid;place-items:center;padding:0}
.icon svg{width:15px;height:15px;fill:currentColor}
.hint{font-size:9.5px;color:var(--sand-dim);letter-spacing:.05em;margin-top:10px;line-height:1.55}
kbd{font:700 9px/1 'Karla';background:rgba(242,229,200,.1);border:1px solid var(--line);border-radius:4px;
  padding:2px 4px;color:var(--sand)}

/* ---- toast ---- */
#toast{position:fixed;left:50%;bottom:96px;transform:translate(-50%,14px);z-index:9;opacity:0;
  pointer-events:none;transition:opacity .3s,transform .3s cubic-bezier(.16,.84,.3,1);
  background:rgba(6,30,39,.9);border:1px solid var(--line-hi);border-radius:999px;padding:9px 18px;
  font:700 10px/1 'Karla';letter-spacing:.16em;text-transform:uppercase;
  backdrop-filter:blur(10px);box-shadow:var(--shadow);white-space:nowrap;max-width:90vw;overflow:hidden;text-overflow:ellipsis}
#toast.show{opacity:1;transform:translate(-50%,0)}

/* ---- intro ---- */
#intro{position:fixed;inset:0;z-index:20;display:grid;place-items:center;padding:24px;
  background:radial-gradient(90% 70% at 50% 45%,rgba(6,34,44,.72),rgba(2,10,16,.94));
  backdrop-filter:blur(7px);transition:opacity .9s ease,visibility .9s}
#intro.gone{opacity:0;visibility:hidden}
.card{max-width:520px;text-align:left;border:1px solid var(--line-hi);border-radius:20px;padding:34px 34px 28px;
  background:linear-gradient(165deg,rgba(10,44,56,.92),rgba(4,22,30,.94));box-shadow:0 50px 90px -40px #000}
.card h1{font-size:clamp(52px,9vw,80px)}
.card .sub{font-size:14px;max-width:38ch;margin-top:12px;color:#c9bfa9}
.card .btn{margin-top:22px;padding:13px 22px;flex:none;display:inline-block;width:auto}
.card .fine{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--sand-dim);margin-top:16px}
.loader{height:2px;background:rgba(242,229,200,.12);border-radius:2px;overflow:hidden;margin-top:22px}
.loader i{display:block;height:100%;width:30%;background:linear-gradient(90deg,var(--sea),var(--copper));
  animation:load 1.15s cubic-bezier(.5,0,.5,1) infinite}
@keyframes load{0%{transform:translateX(-100%)}100%{transform:translateX(340%)}}

/* ---- mobile ---- */
#sheetBtn{display:none}
@media (max-width:900px){
  #ui{grid-template-columns:1fr;grid-template-rows:auto 1fr auto;padding:10px}
  .brand{grid-column:1;grid-row:1;max-width:none;padding:11px 13px}
  h1{font-size:34px}.sub{display:none}.rule{margin:8px 0 7px}
  .stack{grid-column:1;grid-row:3;position:fixed;left:8px;right:8px;bottom:74px;max-height:52vh;
    transform:translateY(calc(100% + 92px));transition:transform .45s cubic-bezier(.16,.84,.3,1);
    background:rgba(4,22,30,.86);border:1px solid var(--line);border-radius:18px;padding:12px;
    backdrop-filter:blur(18px);box-shadow:var(--shadow);z-index:6}
  body.sheet .stack{transform:none}
  .stack .panel{background:rgba(255,255,255,.035)}
  .audio{grid-column:1;grid-row:1;justify-self:end;align-self:start;width:auto;padding:8px 10px}
  .audio .field,.audio .hint{display:none}
  .cams{grid-column:1;grid-row:3;bottom:12px;position:fixed;left:50%;transform:translateX(-50%);
    justify-self:none;overflow-x:auto;max-width:calc(100vw - 118px);border-radius:999px}
  #sheetBtn{display:flex;position:fixed;right:10px;bottom:12px;z-index:7;pointer-events:auto;
    width:56px;height:46px;border-radius:14px;align-items:center;justify-content:center;gap:3px;flex-direction:column;
    background:linear-gradient(180deg,var(--copper-hi),#c9702f);border:1px solid #f3ab6d;cursor:pointer;
    box-shadow:0 12px 26px -12px rgba(0,0,0,.9)}
  #sheetBtn i{display:block;width:16px;height:2px;border-radius:2px;background:#20100a;transition:.3s}
  body.sheet #sheetBtn i:nth-child(1){transform:translateY(4px) rotate(45deg)}
  body.sheet #sheetBtn i:nth-child(2){opacity:0}
  body.sheet #sheetBtn i:nth-child(3){transform:translateY(-4px) rotate(-45deg)}
  #toast{bottom:150px}
}
@media (max-height:620px){.hint{display:none}}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div class="vig"></div><div class="grain"></div><div class="uw" id="uwFx"></div>

<div id="ui">
  <header class="panel brand rise" style="animation-delay:.05s">
    <div class="kicker">Procedural diorama · No. 04</div>
    <h1>Tidehaven<em>.</em></h1>
    <p class="sub">A quarter-cut lagoon — a cabin in the pines above, a living reef turning below.</p>
    <div class="rule"></div>
    <div class="readout">
      <div><span><span class="live"></span>Hour</span><b id="roTime">Midday</b></div>
      <div><span>Tide</span><b id="roTide">0.00 m</b></div>
      <div><span>Wind</span><b id="roWind">9 kn</b></div>
    </div>
  </header>

  <div class="stack" id="stack">
    <section class="panel rise" style="animation-delay:.18s">
      <h2>Conditions <span>tide · breeze · light</span></h2>
      <div class="field">
        <div class="lab"><span>Tide level</span><b id="vTide">0.00 m</b></div>
        <input id="sTide" type="range" min="-70" max="55" value="0" step="1" aria-label="Tide level">
      </div>
      <div class="field">
        <div class="lab"><span>Wind</span><b id="vWind">9 kn</b></div>
        <input id="sWind" type="range" min="0" max="100" value="34" step="1" aria-label="Wind strength">
      </div>
      <div class="field">
        <div class="lab"><span>Time of day</span></div>
        <div class="seg" role="group" aria-label="Time of day">
          <button class="btn on" data-tod="day">Day</button>
          <button class="btn" data-tod="sunset">Sunset</button>
          <button class="btn" data-tod="night">Night</button>
        </div>
      </div>
    </section>

    <section class="panel rise" style="animation-delay:.28s">
      <h2>Visit <span>tap to act</span></h2>
      <div class="row" style="margin-bottom:7px">
        <button class="btn sea" id="bKayak">Launch kayak</button>
        <button class="btn sea" id="bRay">Ray leap</button>
      </div>
      <div class="row">
        <button class="btn" id="bPause">Pause world</button>
        <button class="btn" id="bReset">Reset</button>
      </div>
    </section>

    <section class="panel rise" style="animation-delay:.38s">
      <h2>Render <span>device budget</span></h2>
      <div class="field" style="margin:0">
        <div class="lab"><span>Quality</span></div>
        <select id="qSel" aria-label="Quality">
          <option value="high">High — full shadows</option>
          <option value="med" selected>Medium — balanced</option>
          <option value="low">Low — mobile</option>
        </select>
      </div>
    </section>
  </div>

  <nav class="cams rise" style="animation-delay:.45s" aria-label="Camera views">
    <button class="btn on" data-cam="iso">Overhead</button>
    <button class="btn" data-cam="cabin">Cabin &amp; pier</button>
    <button class="btn" data-cam="reef">Reef</button>
    <button class="btn" data-cam="free">Free orbit</button>
  </nav>

  <section class="panel audio rise" style="animation-delay:.32s">
    <div class="audiorow">
      <button class="btn icon" id="bSound" aria-label="Toggle sound">
        <svg viewBox="0 0 24 24"><path d="M4 9v6h4l5 4V5L8 9H4zm12.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 2.2v2.1c3.4.9 5.9 4 5.9 7.7s-2.5 6.8-5.9 7.7v2.1c4.6-1 8-5 8-9.8s-3.4-8.8-8-9.8z"/></svg>
      </button>
      <div style="flex:1">
        <div class="lab" style="margin:0 0 3px"><span>Sound</span><b id="vVol">55</b></div>
        <input id="sVol" type="range" min="0" max="100" value="55" step="1" aria-label="Volume">
      </div>
    </div>
    <div class="hint"><kbd>1</kbd><kbd>2</kbd><kbd>3</kbd> views · <kbd>K</kbd> kayak · <kbd>R</kbd> ray · <kbd>Space</kbd> pause · drag to orbit</div>
  </section>
</div>

<button id="sheetBtn" aria-label="Toggle controls"><i></i><i></i><i></i></button>
<div id="toast"></div>

<div id="intro">
  <div class="card">
    <div class="kicker">Procedural diorama · No. 04</div>
    <h1>Tidehaven<em>.</em></h1>
    <p class="sub">A one-storey cabin, a copper roof, a pier with a kayak tied to it — and beneath the waterline, a cut-away lagoon where the rays are still awake.</p>
    <button class="btn on" id="begin">Step inside</button>
    <div class="loader"><i></i></div>
    <div class="fine">Best with sound · drag to orbit the vitrine</div>
  </div>
</div>

<script type="importmap">
{"imports":{
  "three":"https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
  "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

/* ============================================================================
   0 · CONFIG, STATE, HELPERS
   ========================================================================== */
const HALF = 8.5;                 // diorama half-footprint
const SEABED = -5.2;              // floor of the lagoon
const ISLAND = { x:-2.2, z:-2.4, r:5.0 };
const TER    = { x:-2.9, z:-3.1, r:1.5, y:1.85 };   // cabin terrace

const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const sat=v=>v<0?0:v>1?1:v;
const sstep=(a,b,x)=>{const t=sat((x-a)/(b-a));return t*t*(3-2*t);};
const easeIO=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
// deterministic RNG so Reset always rebuilds the same world
let _seed=20240717;
function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
let rnd=mulberry(_seed);
const R=(a,b)=>a+(b-a)*rnd();
const pick=a=>a[(rnd()*a.length)|0];

/* ---- terrain height: single source of truth, mirrored in GLSL ------------- */
function prof(d){
  if(d>=1) return SEABED;
  let h=lerp(2.45,2.30,sstep(0,.34,d));
  h=lerp(h,1.55,sstep(.34,.50,d));
  h=lerp(h,.72,sstep(.50,.62,d));
  h=lerp(h,.10,sstep(.62,.80,d));
  h=lerp(h,-.05,sstep(.80,.87,d));
  h=lerp(h,-.60,sstep(.87,.93,d));
  h=lerp(h,SEABED,sstep(.93,1,d));
  return h;
}
function terrainH(x,z){
  const ang=Math.atan2(z-ISLAND.z,x-ISLAND.x);
  const wob=1+.10*Math.sin(ang*2+.6)+.06*Math.cos(ang*3-1.2)+.035*Math.sin(ang*5+2.1);
  const d=Math.hypot(x-ISLAND.x,z-ISLAND.z)/(ISLAND.r*wob);
  let h=prof(d);
  const inner=sstep(.72,.30,d);
  h+=inner*(.42*Math.sin(x*.53+1.1)*Math.cos(z*.47-.4)+.24*Math.sin(x*1.03-2)*Math.cos(z*.87+1.3)+.12*Math.sin(x*1.9+z*1.4));
  h=lerp(h,TER.y,sstep(2.7,1.5,Math.hypot(x-TER.x,z-TER.z)));
  h+=sstep(.95,1.35,d)*(.30*Math.sin(x*.62+2.1)*Math.cos(z*.55-1)+.16*Math.sin(x*1.3+z*1.1)+.10);
  return h;
}
const TERRAIN_GLSL = /* glsl */`
float sstep2(float a,float b,float x){ float t=clamp((x-a)/(b-a),0.0,1.0); return t*t*(3.0-2.0*t); }
float prof(float d){
  if(d>=1.0) return ${SEABED.toFixed(2)};
  float h=mix(2.45,2.30,sstep2(0.0,0.34,d));
  h=mix(h,1.55,sstep2(0.34,0.50,d));
  h=mix(h,0.72,sstep2(0.50,0.62,d));
  h=mix(h,0.10,sstep2(0.62,0.80,d));
  h=mix(h,-0.05,sstep2(0.80,0.87,d));
  h=mix(h,-0.60,sstep2(0.87,0.93,d));
  h=mix(h,${SEABED.toFixed(2)},sstep2(0.93,1.0,d));
  return h;
}
float terrainH(vec2 p){
  float ang=atan(p.y-${ISLAND.z.toFixed(2)},p.x-${ISLAND.x.toFixed(2)});
  float wob=1.0+0.10*sin(ang*2.0+0.6)+0.06*cos(ang*3.0-1.2)+0.035*sin(ang*5.0+2.1);
  float d=length(p-vec2(${ISLAND.x.toFixed(2)},${ISLAND.z.toFixed(2)}))/(${ISLAND.r.toFixed(2)}*wob);
  float h=prof(d);
  float inner=sstep2(0.72,0.30,d);
  h+=inner*(0.42*sin(p.x*0.53+1.1)*cos(p.y*0.47-0.4)+0.24*sin(p.x*1.03-2.0)*cos(p.y*0.87+1.3)+0.12*sin(p.x*1.9+p.y*1.4));
  h=mix(h,${TER.y.toFixed(2)},sstep2(2.7,1.5,length(p-vec2(${TER.x.toFixed(2)},${TER.z.toFixed(2)}))));
  h+=sstep2(0.95,1.35,d)*(0.30*sin(p.x*0.62+2.1)*cos(p.y*0.55-1.0)+0.16*sin(p.x*1.3+p.y*1.1)+0.10);
  return h;
}`;
// CPU twin of the wave sum used by the water shader (floating props ride on it)
function waveH(x,z,t,wind){
  const a=(.05+wind*.17);
  let h=Math.sin(x*1.15+t*1.25)*.45*a+Math.sin(z*1.35-t*1.05)*.38*a
       +Math.sin((x*.8+z*1.15)+t*1.9)*.28*a+Math.sin((x*2.7-z*1.7)-t*2.4)*.14*a*(.25+wind);
  return h;
}

/* ---- shared uniforms ------------------------------------------------------ */
const U = {
  time:{value:0}, wind:{value:.34}, level:{value:0},
  sunDir:{value:new THREE.Vector3(.55,.72,.42)},
  sunCol:{value:new THREE.Color('#fff1dc')},
  skyTop:{value:new THREE.Color('#4d90c6')},
  skyBot:{value:new THREE.Color('#cfe6ee')},
  shallow:{value:new THREE.Color('#54d3c2')},
  deep:{value:new THREE.Color('#0d6a84')},
  waterTint:{value:new THREE.Color('#0e6f7f')},
  night:{value:0}, lamp:{value:0}, fog:{value:new THREE.Color('#cfe6ee')},
  pixel:{value:1}
};

/* ---- GLSL snippets -------------------------------------------------------- */
const CAUSTIC = /* glsl */`
float caust(vec2 p,float t){
  vec2 i=p; float c=1.0; const float inten=0.0045;
  for(int n=0;n<3;n++){
    float tt=t*(1.0-(3.5/float(n+1)));
    i=p+vec2(cos(tt-i.x)+sin(tt+i.y),sin(tt-i.y)+cos(tt+i.x));
    float sx=sin(i.x+tt); sx=sign(sx)*max(abs(sx),0.03);
    float sy=cos(i.y+tt); sy=sign(sy)*max(abs(sy),0.03);
    c+=1.0/length(vec2(p.x/(sx/inten),p.y/(sy/inten)));
  }
  c/=3.0; c=1.17-pow(c,1.4);
  return clamp(pow(abs(c),8.0),0.0,1.35);
}`;
const HASHNOISE = /* glsl */`
float h21(vec2 p){ return fract(sin(dot(p,vec2(41.31,289.7)))*43758.5453); }
float vn(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(h21(i),h21(i+vec2(1,0)),f.x),mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.0,a=0.5; for(int i=0;i<4;i++){ s+=a*vn(p); p*=2.03; a*=0.5; } return s; }`;

/* ============================================================================
   1 · RENDERER · SCENE · CAMERA · CONTROLS
   ========================================================================== */
const canvas=document.getElementById('scene');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.02;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(U.fog.value.getHex(),42,210);

const camera=new THREE.PerspectiveCamera(22,1,.12,900);
camera.position.set(34,27,34);

const controls=new OrbitControls(camera,canvas);
controls.enableDamping=true; controls.dampingFactor=.06;
controls.minDistance=6; controls.maxDistance=140;
controls.minPolarAngle=.12; controls.maxPolarAngle=1.95;
controls.enablePan=true; controls.panSpeed=.6; controls.rotateSpeed=.85; controls.zoomSpeed=.8;
controls.target.set(.3,-.4,.3);

/* quality */
const QUAL={high:{dpr:2,shadow:2048,sh:true},med:{dpr:1.5,shadow:1024,sh:true},low:{dpr:1,shadow:1024,sh:false}};
let quality='med';
function applyQuality(q){
  quality=q; const c=QUAL[q];
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,c.dpr));
  renderer.shadowMap.enabled=c.sh;
  sun.castShadow=c.sh; sun.shadow.mapSize.set(c.shadow,c.shadow);
  if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null;}
  scene.traverse(o=>{ if(o.material){ const m=Array.isArray(o.material)?o.material:[o.material]; m.forEach(x=>x.needsUpdate=true);} });
  onResize();
}

/* ============================================================================
   2 · SKY · LIGHTS · TIME OF DAY
   ========================================================================== */
const skyMat=new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false,
  uniforms:{uTop:U.skyTop,uBot:U.skyBot,uSunCol:U.sunCol,uSunDir:U.sunDir,uNight:U.night,uTime:U.time},
  vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz;
    gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`
    varying vec3 vW; uniform vec3 uTop,uBot,uSunCol,uSunDir; uniform float uNight,uTime;
    float h31(vec3 p){ return fract(sin(dot(p,vec3(12.99,78.23,45.16)))*43758.5453); }
    void main(){
      vec3 d=normalize(vW-cameraPosition);
      float h=clamp(d.y*0.5+0.5,0.0,1.0);
      vec3 col=mix(uBot,uTop,pow(h,0.85));
      vec3 S=normalize(uSunDir);
      float sd=max(dot(d,S),0.0);
      col+=uSunCol*pow(sd,26.0)*(1.0-uNight*0.55)*1.1;
      col+=uSunCol*pow(sd,4.0)*0.20*(1.0-uNight*0.7);
      // moon / sun disc
      float disc=smoothstep(0.9993,0.99975,dot(d,S));
      col+=uSunCol*disc*(1.6+uNight*1.2);
      float halo=smoothstep(0.9955,0.9993,dot(d,S));
      col+=uSunCol*halo*0.25;
      // stars
      if(uNight>0.01 && d.y>-0.02){
        vec3 c3=floor(d*230.0);
        float st=h31(c3);
        float tw=0.6+0.4*sin(uTime*2.2+st*60.0);
        col+=vec3(0.85,0.92,1.0)*smoothstep(0.9982,1.0,st)*tw*uNight*sstep2(0.0,0.25,d.y)*1.6;
      }
      gl_FragColor=vec4(col,1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`.replace('sstep2','sstep2')
     .replace('void main','void main')
     .replace('varying vec3 vW;','varying vec3 vW;\nfloat sstep2(float a,float b,float x){float t=clamp((x-a)/(b-a),0.0,1.0);return t*t*(3.0-2.0*t);}')
});
const sky=new THREE.Mesh(new THREE.SphereGeometry(400,32,20),skyMat);
sky.frustumCulled=false; scene.add(sky);

const hemi=new THREE.HemisphereLight(0xbfe6f2,0x6b7a5e,.85); scene.add(hemi);
const amb=new THREE.AmbientLight(0xffffff,.18); scene.add(amb);
const sun=new THREE.DirectionalLight(0xfff1dc,2.6);
sun.position.copy(U.sunDir.value).multiplyScalar(42);
sun.castShadow=true;
sun.shadow.mapSize.set(1024,1024);
sun.shadow.camera.left=-12; sun.shadow.camera.right=12;
sun.shadow.camera.top=12; sun.shadow.camera.bottom=-12;
sun.shadow.camera.near=1; sun.shadow.camera.far=110;
sun.shadow.bias=-.0009; sun.shadow.normalBias=.035; sun.shadow.radius=2.2;
scene.add(sun);

/* lamps (only a few real lights; the rest are emissive + sprites) */
const lampCabin=new THREE.PointLight(0xffb45e,0,9,2.2); lampCabin.position.set(TER.x,TER.y+1.1,TER.z+.3); scene.add(lampCabin);
const lampPier =new THREE.PointLight(0xffc078,0,8,2.2);  scene.add(lampPier);
const lampBeach=new THREE.PointLight(0xffa860,0,6,2.2);  scene.add(lampBeach);

const TOD={
  day:   {dir:new THREE.Vector3(.55,.78,.42),sunCol:new THREE.Color('#fff2df'),sunInt:2.7,
          hSky:new THREE.Color('#bfe6f2'),hGnd:new THREE.Color('#6f7f60'),hInt:.9,amb:.2,
          top:new THREE.Color('#4d90c6'),bot:new THREE.Color('#d3e9ef'),fog:new THREE.Color('#cfe6ee'),
          sh:new THREE.Color('#59d8c5'),dp:new THREE.Color('#0d6a84'),tint:new THREE.Color('#12798c'),
          night:0,expo:1.02,fogN:44,fogF:220},
  sunset:{dir:new THREE.Vector3(.94,.16,.28),sunCol:new THREE.Color('#ff9c4e'),sunInt:2.5,
          hSky:new THREE.Color('#f2b189'),hGnd:new THREE.Color('#4a4a58'),hInt:.62,amb:.16,
          top:new THREE.Color('#2b4a80'),bot:new THREE.Color('#ff9a58'),fog:new THREE.Color('#e0977a'),
          sh:new THREE.Color('#66cfc2'),dp:new THREE.Color('#0b4f6c'),tint:new THREE.Color('#0f5f74'),
          night:.42,expo:1.06,fogN:26,fogF:150},
  night: {dir:new THREE.Vector3(-.34,.62,-.46),sunCol:new THREE.Color('#9db9ff'),sunInt:.55,
          hSky:new THREE.Color('#2b4066'),hGnd:new THREE.Color('#141d28'),hInt:.34,amb:.09,
          top:new THREE.Color('#040a1c'),bot:new THREE.Color('#12294a'),fog:new THREE.Color('#0c1830'),
          sh:new THREE.Color('#1e8396'),dp:new THREE.Color('#032230'),tint:new THREE.Color('#062d40'),
          night:1,expo:1.16,fogN:22,fogF:130}
};
const cur=JSON.parse(JSON.stringify({})); // unused placeholder
const todFrom={...TOD.day}, todTo={...TOD.day};
let todT=1, todName='day';
const cA=new THREE.Color(), cB=new THREE.Color();
function lerpCol(a,b,t,out){ out.setRGB(lerp(a.r,b.r,t),lerp(a.g,b.g,t),lerp(a.b,b.b,t)); return out; }
const TODV={dir:new THREE.Vector3().copy(TOD.day.dir),sunCol:new THREE.Color().copy(TOD.day.sunCol),
  hSky:new THREE.Color().copy(TOD.day.hSky),hGnd:new THREE.Color().copy(TOD.day.hGnd),
  top:new THREE.Color().copy(TOD.day.top),bot:new THREE.Color().copy(TOD.day.bot),
  fog:new THREE.Color().copy(TOD.day.fog),sh:new THREE.Color().copy(TOD.day.sh),
  dp:new THREE.Color().copy(TOD.day.dp),tint:new THREE.Color().copy(TOD.day.tint),
  sunInt:2.7,hInt:.9,amb:.2,night:0,expo:1.02,fogN:44,fogF:220};
const TOD_SNAP=()=>({dir:TODV.dir.clone(),sunCol:TODV.sunCol.clone(),hSky:TODV.hSky.clone(),hGnd:TODV.hGnd.clone(),
  top:TODV.top.clone(),bot:TODV.bot.clone(),fog:TODV.fog.clone(),sh:TODV.sh.clone(),dp:TODV.dp.clone(),
  tint:TODV.tint.clone(),sunInt:TODV.sunInt,hInt:TODV.hInt,amb:TODV.amb,night:TODV.night,expo:TODV.expo,fogN:TODV.fogN,fogF:TODV.fogF});
let todA=TOD_SNAP(), todB=TOD_SNAP();
function setTimeOfDay(n){
  if(n===todName && todT>=1) return;
  todA=TOD_SNAP(); todB={...TOD[n],dir:TOD[n].dir.clone(),sunCol:TOD[n].sunCol.clone(),hSky:TOD[n].hSky.clone(),
    hGnd:TOD[n].hGnd.clone(),top:TOD[n].top.clone(),bot:TOD[n].bot.clone(),fog:TOD[n].fog.clone(),
    sh:TOD[n].sh.clone(),dp:TOD[n].dp.clone(),tint:TOD[n].tint.clone()};
  todT=0; todName=n;
  document.querySelectorAll('[data-tod]').forEach(b=>b.classList.toggle('on',b.dataset.tod===n));
}
function updateTOD(dt){
  if(todT<1){ todT=Math.min(1,todT+dt/2.4); }
  const t=easeIO(todT), a=todA, b=todB;
  TODV.dir.lerpVectors(a.dir,b.dir,t).normalize();
  lerpCol(a.sunCol,b.sunCol,t,TODV.sunCol); lerpCol(a.hSky,b.hSky,t,TODV.hSky);
  lerpCol(a.hGnd,b.hGnd,t,TODV.hGnd); lerpCol(a.top,b.top,t,TODV.top);
  lerpCol(a.bot,b.bot,t,TODV.bot); lerpCol(a.fog,b.fog,t,TODV.fog);
  lerpCol(a.sh,b.sh,t,TODV.sh); lerpCol(a.dp,b.dp,t,TODV.dp); lerpCol(a.tint,b.tint,t,TODV.tint);
  TODV.sunInt=lerp(a.sunInt,b.sunInt,t); TODV.hInt=lerp(a.hInt,b.hInt,t); TODV.amb=lerp(a.amb,b.amb,t);
  TODV.night=lerp(a.night,b.night,t); TODV.expo=lerp(a.expo,b.expo,t);
  TODV.fogN=lerp(a.fogN,b.fogN,t); TODV.fogF=lerp(a.fogF,b.fogF,t);

  U.sunDir.value.copy(TODV.dir); U.sunCol.value.copy(TODV.sunCol);
  U.skyTop.value.copy(TODV.top); U.skyBot.value.copy(TODV.bot);
  U.shallow.value.copy(TODV.sh); U.deep.value.copy(TODV.dp);
  U.waterTint.value.copy(TODV.tint); U.night.value=TODV.night;
  U.lamp.value=sstep(.30,.80,TODV.night);
  sun.position.copy(TODV.dir).multiplyScalar(42);
  sun.color.copy(TODV.sunCol); sun.intensity=TODV.sunInt;
  hemi.color.copy(TODV.hSky); hemi.groundColor.copy(TODV.hGnd); hemi.intensity=TODV.hInt;
  amb.intensity=TODV.amb;
  scene.fog.color.copy(TODV.fog); scene.fog.near=TODV.fogN; scene.fog.far=TODV.fogF;
  renderer.toneMappingExposure=TODV.expo;
  const L=U.lamp.value;
  lampCabin.intensity=L*7.5; lampPier.intensity=L*5.2; lampBeach.intensity=L*3.6;
}

/* ============================================================================
   3 · MATERIAL PATCH HELPERS
   ========================================================================== */
const WORLD_CHUNK=`
vec3 tideWorldPos(vec3 tp){
  #ifdef USE_INSTANCING
    return (modelMatrix*instanceMatrix*vec4(tp,1.0)).xyz;
  #else
    return (modelMatrix*vec4(tp,1.0)).xyz;
  #endif
}`;
/** depth-based lagoon fog baked into any standard material (underwater only) */
function underwater(mat,str=1){
  mat.onBeforeCompile=s=>{
    s.uniforms.uLevel=U.level; s.uniforms.uWT=U.waterTint;
    s.vertexShader='varying vec3 vWP;\n'+WORLD_CHUNK+'\n'+s.vertexShader
      .replace('#include <begin_vertex>','#include <begin_vertex>\n vWP=tideWorldPos(transformed);');
    s.fragmentShader='uniform float uLevel; uniform vec3 uWT; varying vec3 vWP;\n'+s.fragmentShader
      .replace('#include <dithering_fragment>',
        `#include <dithering_fragment>
         float _dep=max(uLevel-vWP.y,0.0);
         float _f=(1.0-exp(-_dep*0.30))*${str.toFixed(2)};
         gl_FragColor.rgb=mix(gl_FragColor.rgb,uWT,_f);`);
  };
  mat.customProgramCacheKey=()=>'uw'+str;
}
/** wind sway for vegetation / cloth */
function sway(mat,{amp=.14,freq=1.6,span=1}={}){
  mat.onBeforeCompile=s=>{
    s.uniforms.uTime=U.time; s.uniforms.uWind=U.wind;
    s.vertexShader=`uniform float uTime; uniform float uWind;\n${WORLD_CHUNK}\n`+s.vertexShader
      .replace('#include <begin_vertex>',`#include <begin_vertex>
        { vec3 wp0=tideWorldPos(vec3(0.0));
          float hh=clamp(transformed.y/${span.toFixed(2)},0.0,1.0);
          float ph=uTime*${freq.toFixed(2)}+wp0.x*0.8+wp0.z*1.15;
          float gust=0.6+0.4*sin(uTime*0.43+ph*0.5);
          float amt=pow(hh,1.6)*uWind*${amp.toFixed(3)}*gust;
          transformed.x+=sin(ph)*amt; transformed.z+=cos(ph*1.27)*amt*0.65; }`);
  };
  mat.customProgramCacheKey=()=>'sw'+amp+freq+span;
}

/* ============================================================================
   4 · TERRAIN  (island + seabed in one continuous mesh — no intersection)
   ========================================================================== */
const C_DEEP=new THREE.Color('#a8916a'), C_SANDW=new THREE.Color('#c6ab7c'),
      C_SAND=new THREE.Color('#ecd9ad'), C_GRASS=new THREE.Color('#6f9a4f'),
      C_GRASS2=new THREE.Color('#4f7c40'), C_ROCK=new THREE.Color('#8b857a'),
      C_WEED=new THREE.Color('#557f4e');
const terGeo=new THREE.PlaneGeometry(HALF*2,HALF*2,182,182);
terGeo.rotateX(-Math.PI/2);
{
  const p=terGeo.attributes.position, n=p.count;
  const col=new Float32Array(n*3); const c=new THREE.Color();
  for(let i=0;i<n;i++){
    const x=p.getX(i), z=p.getZ(i);
    const h=terrainH(x,z); p.setY(i,h);
    const dh=1.1, slope=Math.hypot(terrainH(x+dh,z)-terrainH(x-dh,z),terrainH(x,z+dh)-terrainH(x,z-dh))/(2*dh);
    const nz=(Math.sin(x*3.7)*Math.cos(z*3.1)*.5+.5);
    if(h<-.55){ c.copy(C_DEEP).lerp(C_WEED,nz*.55*sstep(.6,2.2,-h)); }
    else if(h<.16){ c.copy(C_SANDW).lerp(C_SAND,sstep(-.4,.16,h)); }
    else if(h<.66){ c.copy(C_SAND).lerp(C_GRASS2,sstep(.16,.66,h)*.55); }
    else { c.copy(C_GRASS2).lerp(C_GRASS,nz); if(slope>.85) c.lerp(C_ROCK,sstep(.85,1.5,slope)); }
    if(h>.7&&h<1.25){ // sandy footpath from deck down to the beach
      const t=sstep(.34,0,Math.abs((x-TER.x)-(z-TER.z))*.706);
      const along=sstep(-.5,1.2,(x+z-TER.x-TER.z)*.706);
      c.lerp(C_SAND,t*along*.75*sstep(1.3,.7,h));
    }
    c.offsetHSL(0,0,(nz-.5)*.05);
    col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b;
  }
  terGeo.setAttribute('color',new THREE.BufferAttribute(col,3));
  terGeo.computeVertexNormals();
}
const terMat=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.95,metalness:0});
terMat.onBeforeCompile=s=>{
  s.uniforms.uTime=U.time; s.uniforms.uLevel=U.level; s.uniforms.uNight=U.night;
  s.vertexShader='varying vec3 vWP;\n'+WORLD_CHUNK+'\n'+s.vertexShader
    .replace('#include <begin_vertex>','#include <begin_vertex>\n vWP=tideWorldPos(transformed);');
  s.fragmentShader=`uniform float uTime,uLevel,uNight; varying vec3 vWP;\n${CAUSTIC}\n`+s.fragmentShader
    .replace('#include <dithering_fragment>',
    `#include <dithering_fragment>
     float dep=max(uLevel-vWP.y,0.0);
     float uw=smoothstep(0.12,-0.25,vWP.y-uLevel);
     float ca=caust(vWP.xz*0.85+vec2(uTime*0.035,uTime*0.05),uTime*0.55);
     float fade=exp(-dep*0.30);
     gl_FragColor.rgb+=ca*fade*uw*mix(vec3(0.55,0.95,0.85),vec3(0.25,0.5,0.6),uNight)*1.15;
     float above=vWP.y-uLevel;
     float wet=(1.0-smoothstep(0.02,0.52,above))*smoothstep(-0.55,-0.08,above);
     gl_FragColor.rgb*=mix(1.0,0.63,wet);
     gl_FragColor.rgb+=vec3(0.35,0.55,0.6)*wet*0.06;
     // lagoon depth haze
     float f=(1.0-exp(-dep*0.30))*uw;
     gl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(0.05,0.42,0.5)*mix(1.0,0.35,uNight),f*0.85);`);
};
terMat.customProgramCacheKey=()=>'terrain';
const terrain=new THREE.Mesh(terGeo,terMat);
terrain.castShadow=true; terrain.receiveShadow=true; scene.add(terrain);

/* ============================================================================
   5 · WATER — surface, cut-away walls, ripples, bubbles, light shafts
   ========================================================================== */
const ripples=[]; for(let i=0;i<6;i++) ripples.push(new THREE.Vector4(0,0,0,0));
const wakeU={value:new THREE.Vector4(0,0,0,0)};
const wakeDir={value:new THREE.Vector2(0,1)};

const WAVE_FN=/* glsl */`
uniform float uWind;
void waveAt(vec2 p,float dep,out float h,out vec2 g){
  float damp=smoothstep(0.0,1.5,dep);
  float a=(0.05+uWind*0.17)*damp;
  h=0.0; g=vec2(0.0);
  vec2 d1=vec2(0.88,0.47); float f1=1.15,s1=1.25,a1=0.45;
  vec2 d2=vec2(-0.35,0.94); float f2=1.35,s2=-1.05,a2=0.38;
  vec2 d3=vec2(0.57,0.82); float f3=1.42,s3=1.9,a3=0.28;
  float c1=cos(dot(p,d1)*f1+uTime*s1); h+=sin(dot(p,d1)*f1+uTime*s1)*a1*a; g+=d1*f1*c1*a1*a;
  float c2=cos(dot(p,d2)*f2+uTime*s2); h+=sin(dot(p,d2)*f2+uTime*s2)*a2*a; g+=d2*f2*c2*a2*a;
  float c3=cos(dot(p,d3)*f3+uTime*s3); h+=sin(dot(p,d3)*f3+uTime*s3)*a3*a; g+=d3*f3*c3*a3*a;
  float a4=a*(0.22+uWind*0.9);
  float c4=cos(dot(p,vec2(2.7,-1.7))*1.0-uTime*2.4); h+=sin(dot(p,vec2(2.7,-1.7))-uTime*2.4)*0.14*a4; g+=vec2(2.7,-1.7)*c4*0.14*a4;
  h*=1.0;
}`;
const waterMat=new THREE.ShaderMaterial({
  transparent:true,depthWrite:false,side:THREE.DoubleSide,
  uniforms:{uTime:U.time,uWind:U.wind,uLevel:U.level,uSunDir:U.sunDir,uSunCol:U.sunCol,
    uSkyTop:U.skyTop,uSkyBot:U.skyBot,uShallow:U.shallow,uDeep:U.deep,uNight:U.night,
    uRipples:{value:ripples},uWake:wakeU,uWakeDir:wakeDir},
  vertexShader:`uniform float uTime,uLevel; varying vec3 vW; ${TERRAIN_GLSL} ${WAVE_FN}
    void main(){ vec4 w=modelMatrix*vec4(position,1.0);
      float th=terrainH(w.xz); float dep=max(uLevel-th,0.0);
      float h; vec2 g; waveAt(w.xz,dep,h,g);
      w.y=uLevel+h; vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`
    precision highp float;
    varying vec3 vW;
    uniform float uTime,uLevel,uWind,uNight;
    uniform vec3 uSunDir,uSunCol,uSkyTop,uSkyBot,uShallow,uDeep;
    uniform vec4 uRipples[6]; uniform vec4 uWake; uniform vec2 uWakeDir;
    ${TERRAIN_GLSL} ${WAVE_FN} ${HASHNOISE}
    void main(){
      float th=terrainH(vW.xz);
      float dep=max(uLevel-th,0.0);
      vec3 V=normalize(cameraPosition-vW);
      float h; vec2 g; waveAt(vW.xz,dep,h,g);
      // fine detail normal
      float e=0.14;
      float n0=vn(vW.xz*2.6+vec2(uTime*0.25,-uTime*0.18));
      float nx=vn((vW.xz+vec2(e,0.0))*2.6+vec2(uTime*0.25,-uTime*0.18));
      float nz=vn((vW.xz+vec2(0.0,e))*2.6+vec2(uTime*0.25,-uTime*0.18));
      vec2 det=vec2(nx-n0,nz-n0)*(0.55+uWind*1.4)/e;
      vec3 N=normalize(vec3(-(g.x+det.x),1.0,-(g.y+det.y)));
      if(!gl_FrontFacing) N=-N;
      vec3 R=reflect(-V,N);
      float fres=0.035+0.96*pow(1.0-max(dot(V,N),0.0),4.0);
      vec3 sky=mix(uSkyBot,uSkyTop,clamp(R.y*1.3,0.0,1.0));
      vec3 body=mix(uShallow,uDeep,smoothstep(0.0,3.4,dep));
      vec3 H=normalize(normalize(uSunDir)+V);
      float ndh=max(dot(N,H),0.0);
      float spec=pow(ndh,240.0)*3.2+pow(ndh,26.0)*0.22;
      vec3 col=mix(body,sky,fres)+uSunCol*spec;
      float sss=pow(max(dot(V,-normalize(uSunDir)),0.0),3.0)*smoothstep(2.6,0.0,dep);
      col+=uShallow*sss*0.42*(1.0-uNight*0.7);
      // ---- foam ----
      float shore=smoothstep(0.85,0.06,dep);
      float n=fbm(vW.xz*1.9+vec2(uTime*0.16,uTime*0.05));
      float foam=shore*smoothstep(0.34,0.92,n+shore*0.5);
      foam+=smoothstep(0.55,1.0,h/max(0.03,(0.05+uWind*0.17)*3.0))*uWind*0.35;
      for(int i=0;i<6;i++){
        vec4 rp=uRipples[i];
        if(rp.w>0.001){
          float d=length(vW.xz-rp.xy);
          foam+=rp.w*smoothstep(0.30,0.0,abs(d-rp.z))*(1.0-clamp(rp.z*0.07,0.0,0.9));
        }
      }
      // kayak wake
      if(uWake.w>0.001){
        vec2 d=vW.xz-uWake.xy; float al=dot(d,uWakeDir);
        float ac=abs(d.x*uWakeDir.y-d.y*uWakeDir.x);
        foam+=uWake.w*step(0.0,al)*smoothstep(1.9,0.0,al)*smoothstep(0.16+al*0.30,0.0,ac);
      }
      foam=clamp(foam,0.0,1.0);
      vec3 fc=mix(vec3(0.96,0.99,0.99),vec3(0.55,0.72,0.80),uNight*0.6);
      col=mix(col,fc,foam);
      float alpha=mix(0.58,0.95,smoothstep(0.0,2.2,dep));
      alpha=max(alpha,foam*0.96);
      if(!gl_FrontFacing) alpha*=0.72;
      gl_FragColor=vec4(col,alpha);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`
});
const water=new THREE.Mesh(new THREE.PlaneGeometry(HALF*2,HALF*2,150,150).rotateX(-Math.PI/2),waterMat);
water.renderOrder=6; water.frustumCulled=false; scene.add(water);

/* ---- cut-away aquarium walls ---- */
const wallMat=(dir)=>new THREE.ShaderMaterial({
  transparent:true,depthWrite:false,side:THREE.DoubleSide,
  uniforms:{uTime:U.time,uLevel:U.level,uNight:U.night,uShallow:U.shallow,uDeep:U.deep,
    uSkyBot:U.skyBot,uSunDir:U.sunDir,k:{value:dir}},
  vertexShader:`varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0);
    vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`
    precision highp float; varying vec3 vW;
    uniform float uTime,uLevel,uNight,k; uniform vec3 uShallow,uDeep,uSkyBot,uSunDir;
    ${CAUSTIC}
    void main(){
      float d=uLevel-vW.y;
      if(d<0.0) discard;
      float dt=1.0-exp(-d*0.34);
      vec3 col=mix(uShallow*1.06,uDeep,dt);
      float c=caust(vW.xz*0.75+vec2(uTime*0.02,uTime*0.05),uTime*0.5);
      col+=c*0.42*(1.0-dt)*vec3(0.55,1.0,0.92)*(1.0-uNight*0.75);
      col+=vec3(0.92,1.0,0.97)*exp(-d*24.0)*0.6;                     // waterline meniscus
      col+=vec3(0.6,0.85,0.9)*exp(-abs(d-0.0)*1.0)*0.0;
      vec3 V=normalize(cameraPosition-vW);
      vec3 Nn=normalize(vec3(k,0.0,1.0-k*k));
      float fres=pow(1.0-abs(dot(V,Nn)),3.0);
      float a=mix(0.10,0.60,dt);
      a=mix(a,min(a+0.22,0.82),fres);
      col=mix(col,uSkyBot*0.55,fres*0.35);
      if(!gl_FrontFacing) a*=0.22;
      a*=mix(1.0,0.75,uNight);
      gl_FragColor=vec4(col,a);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`
});
const WALL_H=1.35-SEABED;
function addWall(w,h,x,y,z,ry,k,order){
  const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),wallMat(k));
  m.position.set(x,y,z); m.rotation.y=ry; m.renderOrder=order;
  m.frustumCulled=false; scene.add(m); return m;
}
const topW=(1.35+SEABED)/2;
addWall(HALF*2,WALL_H, 0,topW, HALF,0,1,8);      // front  (+Z)  cut face
addWall(HALF*2,WALL_H, HALF,topW,0,-Math.PI/2,1,8); // right (+X) cut face
addWall(HALF*2,WALL_H, 0,topW,-HALF,Math.PI,0,7);   // far walls (thin glass)
addWall(HALF*2,WALL_H,-HALF,topW,0,Math.PI/2,0,7);

/* ---- brass frame + plinth ---- */
const brass=new THREE.MeshStandardMaterial({color:'#b98a4e',metalness:.9,roughness:.34});
const woodDark=new THREE.MeshStandardMaterial({color:'#4a3527',roughness:.9});
{
  const g=[]; const box=(w,h,d,x,y,z,ry=0)=>{const b=new THREE.BoxGeometry(w,h,d);
    const m=new THREE.Matrix4().makeRotationY(ry); m.setPosition(x,y,z); b.applyMatrix4(m); g.push(b);};
  const e=.09;
  box(HALF*2+.5,e,e,0,1.35,HALF+.22); box(e,e,HALF*2+.5,HALF+.22,1.35,0);
  box(HALF*2+.5,e,e,0,SEABED-.02,HALF+.22); box(e,e,HALF*2+.5,HALF+.22,SEABED-.02,0);
  box(e,e,HALF*2+.5,-HALF-.22,SEABED-.02,0); box(HALF*2+.5,e,e,0,SEABED-.02,-HALF-.22);
  box(.16,1.35-SEABED+.4,.16,HALF+.22,(1.35+SEABED)/2,HALF+.22);
  box(.16,1.35-SEABED+.4,.16,-HALF-.22,(1.35+SEABED)/2,HALF+.22);
  box(.16,1.35-SEABED+.4,.16,HALF+.22,(1.35+SEABED)/2,-HALF-.22);
  const frame=new THREE.Mesh(mergeGeometries(g),brass); frame.castShadow=true; scene.add(frame);

  const pl=new THREE.Mesh(new THREE.BoxGeometry(HALF*2+.9,1.25,HALF*2+.9),woodDark);
  pl.position.y=SEABED-.68; pl.receiveShadow=true; pl.castShadow=true; scene.add(pl);
  const lip=new THREE.Mesh(new THREE.BoxGeometry(HALF*2+1.05,.14,HALF*2+1.05),brass);
  lip.position.y=SEABED-.06; scene.add(lip);

  // engraved nameplate (canvas texture, no external asset)
  const cv=document.createElement('canvas'); cv.width=768; cv.height=160;
  const cx=cv.getContext('2d');
  cx.fillStyle='#182a2e'; cx.fillRect(0,0,768,160);
  cx.strokeStyle='rgba(232,205,155,.35)'; cx.lineWidth=3; cx.strokeRect(14,14,740,132);
  cx.fillStyle='#e8cfa2'; cx.textAlign='center'; cx.textBaseline='middle';
  cx.font='700 58px Georgia, "Times New Roman", serif'; cx.fillText('TIDEHAVEN',384,66);
  cx.font='400 20px Georgia, serif'; cx.fillStyle='rgba(232,207,162,.62)';
  cx.fillText('I S L A N D   D I O R A M A   ·   N O .  0 4',384,112);
  const tex=new THREE.CanvasTexture(cv); tex.colorSpace=THREE.SRGBColorSpace; tex.anisotropy=4;
  const plate=new THREE.Mesh(new THREE.PlaneGeometry(3.1,.65),
    new THREE.MeshStandardMaterial({map:tex,roughness:.5,metalness:.35}));
  plate.position.set(0,SEABED-.72,HALF+.46); scene.add(plate);
}

/* ---- bubbles ---- */
const BUB_N=140;
const bubMat=new THREE.MeshStandardMaterial({color:'#dffcff',transparent:true,opacity:.42,roughness:.1,
  metalness:0,depthWrite:false,emissive:'#7fd8e8',emissiveIntensity:.25});
underwater(bubMat,.6);
const bubbles=new THREE.InstancedMesh(new THREE.SphereGeometry(1,7,5),bubMat,BUB_N);
bubbles.renderOrder=5; scene.add(bubbles);
const vents=[];
for(let i=0;i<7;i++){
  let x,z,h,tries=0;
  do{ x=R(-6.8,6.8); z=R(-6.8,6.8); h=terrainH(x,z); tries++; }while(h>-.9&&tries<40);
  vents.push({x,z,y:h});
}
const bub=[]; const dummy=new THREE.Object3D();
for(let i=0;i<BUB_N;i++){
  const v=pick(vents);
  bub.push({x:v.x+R(-.5,.5),z:v.z+R(-.5,.5),y:v.y+R(-.2,0),sp:R(.35,.9),r:R(.018,.055),ph:R(0,6.3),vy:v.y});
}
/* ---- light shafts ---- */
const shaftMat=new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,
  uniforms:{uTime:U.time,uLevel:U.level,uNight:U.night,uCol:U.shallow},
  vertexShader:`varying vec2 vUv; varying vec3 vW; void main(){ vUv=uv;
    vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`varying vec2 vUv; varying vec3 vW; uniform float uTime,uLevel,uNight; uniform vec3 uCol;
    void main(){
      float edge=pow(1.0-abs(vUv.x*2.0-1.0),1.4);
      float len=smoothstep(0.0,0.35,vUv.y)*smoothstep(1.0,0.55,vUv.y);
      float fl=0.6+0.4*sin(uTime*0.5+vW.x*1.6+vW.z*1.1);
      float a=edge*len*fl*0.16*(1.0-uNight*0.75);
      gl_FragColor=vec4(mix(uCol,vec3(0.85,1.0,0.95),0.4),a);
    }`});
const shafts=new THREE.Group(); scene.add(shafts);
for(let i=0;i<5;i++){
  const c=new THREE.Mesh(new THREE.ConeGeometry(R(1.0,1.9),6.2,10,1,true),shaftMat);
  c.position.set(R(-4,7),U.level.value-3.0,R(-1,7)); c.rotation.z=R(-.22,.22); c.rotation.x=R(-.16,.16);
  c.renderOrder=7; shafts.add(c);
}

/* ============================================================================
   6 · UNDERWATER LIFE — rays, fish, kelp, reef rocks
   ========================================================================== */
/* ---- manta ray: shape computed in the vertex shader, normals by FD ---- */
const MANTA_FN=/* glsl */`
attribute vec2 aParam; attribute float aFace;
uniform float uTime,uFlap;
const float PI=3.14159265;
float mSpan(float u){
  float a=pow(smoothstep(0.0,0.42,u),0.62);
  float b=pow(1.0-smoothstep(0.42,1.0,u),1.25);
  return min(a,b)*1.12;
}
float mThk(float u){ return (0.14+0.13*sin(PI*clamp(u*1.35,0.0,1.0)))*(1.0-smoothstep(0.75,1.0,u)*0.72); }
vec3 mShape(vec2 q){
  float u=q.x,s=q.y; float sp=mSpan(u);
  float x=s*sp;
  float z=0.80-u*2.35-0.42*abs(s)*smoothstep(0.02,0.5,u);
  float k=max(0.0,1.0-s*s);
  float y=(aFace>0.0)? mThk(u)*pow(k,0.55) : -mThk(u)*0.42*pow(k,0.45);
  y+=0.06*sin(PI*u)*cos(s*1.4);
  return vec3(x,y,z);
}
vec3 mPos(vec2 q){
  vec3 p=mShape(q); float u=q.x,s=q.y,as=abs(s); float t=uTime;
  p.y+=sin(t*2.2+u*1.0)*pow(as,1.45)*mSpan(u)*0.34*uFlap;
  p.y+=sin(t*3.3+u*6.0+as*4.0)*0.018*pow(as,2.0)*uFlap;
  float tw=pow(max(u-0.62,0.0)/0.38,2.0);
  p.x+=sin(t*1.5-u*2.2)*0.17*tw;
  p.y+=sin(t*2.2+0.4)*0.03*uFlap;
  return p;
}`;
function mantaGeo(su=30,sv=12){
  const pos=[],uv=[],face=[],col=[],idx=[];
  const cTop=new THREE.Color('#2f4a56'),cTop2=new THREE.Color('#5d8794'),cBot=new THREE.Color('#e8eef0');
  const c=new THREE.Color();
  const push=(u,s,f)=>{
    const sp=1.12, x=s*sp; // placeholder (positions overwritten by shader)
    const z=0.80-u*2.35;
    const y=f>0?0.2:0.05;
    pos.push(x,y,z); uv.push(u,s); face.push(f);
    c.copy(f>0?cTop:cBot);
    if(f>0){ c.lerp(cTop2,Math.max(0,Math.sin(u*7.0+s*3.0))*.35); }
    col.push(c.r,c.g,c.b);
  };
  for(let f=0;f<2;f++){
    const s0=idx.length;
    for(let i=0;i<=su;i++) for(let j=0;j<=sv;j++) push(i/su,(j/sv)*2-1,f===0?1:-1);
    for(let i=0;i<su;i++) for(let j=0;j<sv;j++){
      const a=s0+i*(sv+1)+j,b=a+sv+1;
      idx.push(a,b,a+1,b,b+1,a+1);
    }
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  g.setAttribute('aParam',new THREE.Float32BufferAttribute(uv,2));
  g.setAttribute('aFace',new THREE.Float32BufferAttribute(face,1));
  g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  g.setIndex(idx);
  g.boundingSphere=new THREE.Sphere(new THREE.Vector3(0,0,-.4),2.9);
  return g;
}
const mantaG=mantaGeo();
function mantaMat(){
  const m=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.62,metalness:.05,side:THREE.DoubleSide});
  m.onBeforeCompile=s=>{
    s.uniforms.uTime=U.time; s.uniforms.uFlap={value:1};
    s.vertexShader='varying vec3 vWP;\n'+WORLD_CHUNK+'\n'+MANTA_FN+'\n'+s.vertexShader
      .replace('#include <beginnormal_vertex>','#include <beginnormal_vertex>\n')
      .replace('#include <begin_vertex>',`#include <begin_vertex>
        { vec3 P=mPos(aParam);
          vec2 e=vec2(0.014,0.0);
          vec3 N=normalize(cross(mPos(aParam+e)-P,mPos(aParam+e.yx)-P));
          if(dot(N,vec3(0.0,aFace,0.0))<0.0) N=-N;
          transformed=P; objectNormal=N; }`)
      .replace('#include <begin_vertex>','#include <begin_vertex>');
    // world pos after displacement
    s.vertexShader=s.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\n vWP=(modelMatrix*vec4(transformed,1.0)).xyz;');
    s.fragmentShader='uniform float uLevel; uniform vec3 uWT; varying vec3 vWP;\n'+s.fragmentShader
      .replace('#include <dithering_fragment>',
      `#include <dithering_fragment>
       float _dep=max(uLevel-vWP.y,0.0);
       gl_FragColor.rgb=mix(gl_FragColor.rgb,uWT,(1.0-exp(-_dep*0.30))*0.92);`);
  };
  m.customProgramCacheKey=()=>'manta';
  m.userData.shader=null;
  return m;
}
const eyeGeo=new THREE.SphereGeometry(.055,8,6);
const hornGeo=new THREE.ConeGeometry(.07,.34,6);
const mouthGeo=new THREE.BoxGeometry(.42,.045,.16);
const rays=[];
function makeRay(scale,cx,cz,rx,rz,yc,ya,spd,ph){
  const mat=mantaMat();
  const g=new THREE.Group();
  const body=new THREE.Mesh(mantaG,mat); g.add(body);
  const dark=new THREE.MeshStandardMaterial({color:'#1c2b32',roughness:.4});
  const pale=new THREE.MeshStandardMaterial({color:'#e6ecee',roughness:.6});
  for(const s of [-1,1]){
    const e=new THREE.Mesh(eyeGeo,dark); e.position.set(.34*s,.09,.30); g.add(e);
    const h=new THREE.Mesh(hornGeo,pale); h.position.set(.17*s,-.02,.86); h.rotation.x=Math.PI*.55; g.add(h);
  }
  const mo=new THREE.Mesh(mouthGeo,dark); mo.position.set(0,-.09,.52); g.add(mo);
  g.scale.setScalar(scale); scene.add(g);
  const r={group:g,mat,cx,cz,rx,rz,yc,ya,spd,ph,heading:0,leaping:false,recover:0,
    home:new THREE.Vector3(cx,cz,0),pos:new THREE.Vector3()};
  rays.push(r); return r;
}
makeRay(.92, 5.0,3.8, 2.9,3.0, -1.9,.8, .17, 0.0);
makeRay(.72, 1.0,5.6, 3.1,1.5, -2.7,.7, .13, 2.4);
makeRay(.58, 5.6,-1.4, 1.9,2.9, -3.3,.6, .21, 4.1);
const hero=rays[0];

/* ---- fish schools (instanced) ---- */
function fishGeo(){
  const b=new THREE.IcosahedronGeometry(.1,0); b.scale(1.05,.78,2.1);
  const t=new THREE.ConeGeometry(.11,.24,4); t.rotateX(Math.PI/2); t.translate(0,0,-.24); t.scale(1,.5,1);
  const d=new THREE.IcosahedronGeometry(.03,0); d.translate(0,.02,.13);
  return mergeGeometries([b,t,d]);
}
const fGeo=fishGeo();
const schools=[];
function makeSchool(n,cx,cz,rx,rz,y,col,spd,ph,region){
  const m=new THREE.MeshStandardMaterial({color:col,roughness:.42,metalness:.25,flatShading:true});
  underwater(m,.95);
  const im=new THREE.InstancedMesh(fGeo,m,n);
  im.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  const c=new THREE.Color(col);
  for(let i=0;i<n;i++){ const cc=c.clone().offsetHSL(R(-.05,.05),R(-.1,.1),R(-.14,.14)); im.setColorAt(i,cc); }
  scene.add(im);
  const off=[]; for(let i=0;i<n;i++) off.push(new THREE.Vector3(R(-1,1),R(-1,1),R(-1,1)));
  schools.push({im,n,cx,cz,rx,rz,y,spd,ph,off,region});
}
makeSchool(26, 4.6,4.4, 2.6,2.4,-1.4,'#f2a44c',.30,1.1);
makeSchool(22,-0.4,6.0, 3.0,1.3,-2.6,'#7fd3e8',.26,3.4);
makeSchool(18, 6.2,-2.0, 1.8,2.6,-3.4,'#cfd9e6',.34,5.2);
makeSchool(14, 2.2,-5.4, 2.6,1.4,-2.2,'#8ce0a8',.29,2.0);

/* ---- kelp & seagrass ---- */
function bladeGeo(h,w,seg){
  const p=[],uv=[],idx=[];
  for(let i=0;i<=seg;i++){
    const t=i/seg,y=t*h,ww=w*(1-t*t*.85);
    p.push(-ww,y,0); uv.push(0,t);
    p.push( ww,y,0); uv.push(1,t);
  }
  for(let i=0;i<seg;i++){const a=i*2;idx.push(a,a+2,a+1,a+1,a+2,a+3);}
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
  g.setIndex(idx); g.computeVertexNormals(); return g;
}
function scatter(count,test,cb){
  const out=[]; let tries=0;
  while(out.length<count&&tries<count*90){
    tries++; const x=R(-7.6,7.6),z=R(-7.6,7.6);
    if(test(x,z)){ const o=cb(x,z); if(o){o.x=x;o.z=z;out.push(o);} }
  }
  return out;
}
const kelpMat=new THREE.MeshStandardMaterial({color:'#3d7a52',roughness:.75,side:THREE.DoubleSide,transparent:true,opacity:.94});
underwater(kelpMat,.7); sway(kelpMat,{amp:.42,freq:1.05,span:2.2});
{
  const list=scatter(52,(x,z)=>{const h=terrainH(x,z);return h<-.6&&h>-4.4&&Math.hypot(x-ISLAND.x,z-ISLAND.z)>5.4;},
    (x,z)=>({h:terrainH(x,z),s:R(.5,1.5)}));
  const g=bladeGeo(2.2,.26,7);
  const im=new THREE.InstancedMesh(g,kelpMat,list.length);
  list.forEach((k,i)=>{ dummy.position.set(k.x,k.h,k.z); dummy.rotation.set(0,R(0,6.3),R(-.15,.15));
    dummy.scale.set(k.s*R(.8,1.2),k.s,R(.8,1.2)); dummy.updateMatrix(); im.setMatrixAt(i,dummy.matrix); });
  im.instanceMatrix.needsUpdate=true; scene.add(im);
}
const grassMat=new THREE.MeshStandardMaterial({color:'#4f8f52',roughness:.85,side:THREE.DoubleSide});
underwater(grassMat,.5); sway(grassMat,{amp:.22,freq:1.7,span:.8});
{
  const list=scatter(180,(x,z)=>{const h=terrainH(x,z);return h<-.15&&h>-3.2&&Math.hypot(x-ISLAND.x,z-ISLAND.z)>5.0;},
    ()=>({h:terrainH(0,0),s:R(.6,1.3)}));
  const g=bladeGeo(.8,.14,4);
  const im=new THREE.InstancedMesh(g,grassMat,list.length);
  list.forEach((k,i)=>{ const x=k.x,z=k.z; k.h=terrainH(x,z);
    dummy.position.set(x,k.h-.03,z); dummy.rotation.set(0,R(0,6.3),R(-.2,.2));
    dummy.scale.setScalar(k.s); dummy.updateMatrix(); im.setMatrixAt(i,dummy.matrix); });
  im.instanceMatrix.needsUpdate=true; scene.add(im);
}
/* ---- reef rocks (3 variants, instanced) ---- */
const rockMat=new THREE.MeshStandardMaterial({color:'#7d7a70',roughness:.95,flatShading:true});
underwater(rockMat,.85);
const rockMats=new THREE.MeshStandardMaterial({color:'#8a857a',roughness:.95,flatShading:true});
function rockGeo(seed,det){
  const g=new THREE.IcosahedronGeometry(1,det);
  const p=g.attributes.position, r=mulberry(seed);
  for(let i=0;i<p.count;i++){
    const v=new THREE.Vector3().fromBufferAttribute(p,i);
    const n=1+ (Math.sin(v.x*3.1+seed)*Math.cos(v.y*2.7-seed)*Math.sin(v.z*3.3+seed*.5))*.18;
    v.multiplyScalar(n); v.y*=.72; p.setXYZ(i,v.x,v.y,v.z);
  }
  g.computeVertexNormals(); return g;
}
{
  const geos=[rockGeo(3,1),rockGeo(11,1),rockGeo(23,0)];
  const spots=scatter(46,(x,z)=>{const h=terrainH(x,z);return h<-1.2&&Math.hypot(x-ISLAND.x,z-ISLAND.z)>5.2;},
    ()=>({s:R(.25,.85)}));
  geos.forEach((g,gi)=>{
    const sub=spots.filter((_,i)=>i%3===gi);
    const im=new THREE.InstancedMesh(g,rockMat,sub.length);
    sub.forEach((s,i)=>{ dummy.position.set(s.x,s.h+s.s*.25,s.z); dummy.rotation.set(R(-.2,.2),R(0,6.3),R(-.2,.2));
      dummy.scale.set(s.s*R(.8,1.3),s.s*R(.5,.9),s.s*R(.8,1.3)); dummy.updateMatrix(); im.setMatrixAt(i,dummy.matrix); });
    im.instanceMatrix.needsUpdate=true; im.castShadow=false; im.receiveShadow=true; scene.add(im);
  });
  // shore & pier rocks above water
  const big=scatter(24,(x,z)=>{const h=terrainH(x,z);return h>-.6&&h<1.6&&Math.hypot(x-ISLAND.x,z-ISLAND.z)>3.2;},
    ()=>({s:R(.22,.62)}));
  const im=new THREE.InstancedMesh(geos[0],rockMats,big.length);
  big.forEach((s,i)=>{ dummy.position.set(s.x,s.h+s.s*.18,s.z); dummy.rotation.set(R(-.3,.3),R(0,6.3),R(-.3,.3));
    dummy.scale.setScalar(s.s); dummy.updateMatrix(); im.setMatrixAt(i,dummy.matrix); });
  im.instanceMatrix.needsUpdate=true; im.castShadow=true; im.receiveShadow=true; scene.add(im);
}

/* ============================================================================
   7 · THE CABIN · PIER · PROPS
   ========================================================================== */
const M={
  wood:new THREE.MeshStandardMaterial({color:'#a5764c',roughness:.86}),
  woodDark:new THREE.MeshStandardMaterial({color:'#6d4c31',roughness:.9}),
  woodPale:new THREE.MeshStandardMaterial({color:'#c9a071',roughness:.8}),
  copper:new THREE.MeshStandardMaterial({color:'#b8703a',metalness:.92,roughness:.32}),
  copperPatina:new THREE.MeshStandardMaterial({color:'#5f9b86',metalness:.7,roughness:.55}),
  glass:new THREE.MeshStandardMaterial({color:'#ffd79a',emissive:'#ffb054',emissiveIntensity:0,roughness:.18,transparent:true,opacity:.9}),
  dark:new THREE.MeshStandardMaterial({color:'#2c2622',roughness:.6,metalness:.3}),
  cloth:new THREE.MeshStandardMaterial({color:'#e8e0cf',roughness:1,side:THREE.DoubleSide}),
  fabricA:new THREE.MeshStandardMaterial({color:'#d9694f',roughness:1,side:THREE.DoubleSide}),
  fabricB:new THREE.MeshStandardMaterial({color:'#4f97a8',roughness:1,side:THREE.DoubleSide}),
  leaf:new THREE.MeshStandardMaterial({color:'#4e7d43',roughness:.9,flatShading:true}),
  leafDark:new THREE.MeshStandardMaterial({color:'#37603a',roughness:.9,flatShading:true}),
  leafLight:new THREE.MeshStandardMaterial({color:'#7fa552',roughness:.9,flatShading:true}),
  bark:new THREE.MeshStandardMaterial({color:'#5b4433',roughness:.95}),
  kayak:new THREE.MeshStandardMaterial({color:'#f4e6c9',roughness:.42,metalness:.05}),
  kayakTrim:new THREE.MeshStandardMaterial({color:'#d9723f',roughness:.5}),
  pot:new THREE.MeshStandardMaterial({color:'#b8663f',roughness:.85}),
  rope:new THREE.MeshStandardMaterial({color:'#c8b48c',roughness:1})
};
const P=(g,m)=>{const c=g.clone();c.applyMatrix4(m);return c;};
const mtx=(x,y,z,rx=0,ry=0,rz=0)=>{const m=new THREE.Matrix4();
  m.makeRotationFromEuler(new THREE.Euler(rx,ry,rz)); m.setPosition(x,y,z); return m;};

/* ---- glow sprite texture ---- */
function glowTex(){
  const c=document.createElement('canvas'); c.width=c.height=128;
  const x=c.getContext('2d'); const g=x.createRadialGradient(64,64,0,64,64,64);
  g.addColorStop(0,'rgba(255,225,175,1)'); g.addColorStop(.28,'rgba(255,190,120,.55)');
  g.addColorStop(1,'rgba(255,170,90,0)'); x.fillStyle=g; x.fillRect(0,0,128,128);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t;
}
const GLOW=glowTex();
const glows=[];
function addGlow(x,y,z,s,op=1){
  const m=new THREE.SpriteMaterial({map:GLOW,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0});
  const sp=new THREE.Sprite(m); sp.position.set(x,y,z); sp.scale.setScalar(s);
  sp.userData.base=op; sp.renderOrder=12; scene.add(sp); glows.push(sp); return sp;
}

/* ---- A-frame cabin ---- */
const cabin=new THREE.Group();
{
  const W=1.55,H=2.95,D=3.1;                    // half width, ridge height, half depth
  const slope=Math.hypot(W,H), ang=Math.atan2(H,W);
  const woodG=[],copG=[],glassG=[];
  // roof panels + standing seams
  for(const s of [-1,1]){
    const panel=new THREE.BoxGeometry(slope+.26,.075,D*2+.3);
    const m=new THREE.Matrix4().makeRotationZ(s>0?Math.PI-ang:ang);
    m.setPosition(-s*W/2,H/2+.02,0);
    copG.push(P(panel,m));
    for(let i=-3;i<=3;i++){
      const rib=new THREE.BoxGeometry(.055,.05,D*2+.34);
      const mm=new THREE.Matrix4().makeRotationZ(s>0?Math.PI-ang:ang);
      mm.setPosition(-s*(W/2+i*(W/3.4))*1.0,H/2+i*(W/3.4)*Math.tan(ang)*-1*(s>0?-1:1)+.06+.045,0);
      mm.setPosition(-s*W/2+(-s)*i*(W/3.6)*Math.cos(ang)*1.0, H/2+i*(W/3.6)*(H/W)*1.0+.07,0);
      copG.push(P(rib,mm));
    }
  }
  // gable ends (triangles) + front glazing
  const tri=new THREE.BufferGeometry();
  tri.setAttribute('position',new THREE.Float32BufferAttribute([-W,0,0, W,0,0, 0,H,0],3));
  tri.computeVertexNormals();
  const triBack=tri.clone(); triBack.applyMatrix4(mtx(0,0,-D));
  const triFront=tri.clone(); triFront.applyMatrix4(mtx(0,0,D));
  const backG=[];
  { const g2=triBack.clone(); backG.push(g2); }
  woodG.push(...backG);
  // front: frame + big window
  const glassTri=new THREE.BufferGeometry();
  const gi=.20;
  glassTri.setAttribute('position',new THREE.Float32BufferAttribute(
    [-W+gi,.06,D, W-gi,.06,D, 0,H-gi*1.4,D],3));
  glassTri.computeVertexNormals(); glassG.push(glassTri);
  // mullions
  for(let i=-2;i<=2;i++){
    const t=(i+2)/4, x0=-W+gi+ (0-(-W+gi))*t*2*(i<0?1:1);
  }
  for(let i=1;i<4;i++){
    const t=i/4;
    const lx=lerp(-W+gi,0,t), rx=lerp(W-gi,0,t), yy=lerp(.06,H-gi*1.4,t);
    woodG.push(P(new THREE.BoxGeometry(.06,.06,.06),0)).pop(); // placeholder removed below
    woodG.pop();
    const bar=new THREE.BoxGeometry(Math.abs(lx-rx)||.05,.07,.07);
    woodG.push(P(bar,mtx((lx+rx)/2,yy,D)));
  }
  const king=new THREE.BoxGeometry(.08,H-.3,.09); woodG.push(P(king,mtx(0,H/2-.05,D)));
  // door
  woodG.push(P(new THREE.BoxGeometry(.72,1.5,.1),mtx(-.62,.75,D+.02)));
  copG.push(P(new THREE.BoxGeometry(.06,.06,.06),mtx(-.30,.78,D+.09)));
  // side windows
  for(const s of [-1,1]){
    for(let k=0;k<2;k++){
      const y=.95+k*0, zz=-.85+k*1.7;
      const panel=new THREE.BoxGeometry(.07,.62,.72);
      const m=new THREE.Matrix4().makeRotationZ(s>0?-ang:ang);
      const off=new THREE.Vector3(s*(W*.42),H*.42,zz);
      m.setPosition(off.x,off.y,off.z);
      glassG.push(P(panel,m));
      const fr=new THREE.BoxGeometry(.05,.74,.84);
      const m2=new THREE.Matrix4().makeRotationZ(s>0?-ang:ang); m2.setPosition(off.x+s*.03,off.y+s*.045,off.z);
      woodG.push(P(fr,m2));
    }
  }
  // ridge cap + chimney
  copG.push(P(new THREE.BoxGeometry(.3,.1,D*2+.4),mtx(0,H+.06,0)));
  copG.push(P(new THREE.CylinderGeometry(.13,.13,.95,10),mtx(.75,H*.55+.5,-1.0)));
  copG.push(P(new THREE.CylinderGeometry(.19,.19,.1,10),mtx(.75,H*.55+1.0,-1.0)));
  // base skirting
  woodG.push(P(new THREE.BoxGeometry(W*2+.1,.28,D*2+.1),mtx(0,.14,0)));

  const woodMesh=new THREE.Mesh(mergeGeometries(woodG),M.wood);
  const copMesh =new THREE.Mesh(mergeGeometries(copG),M.copper);
  const glassMesh=new THREE.Mesh(mergeGeometries(glassG),M.glass);
  [woodMesh,copMesh,glassMesh].forEach(m=>{m.castShadow=true;m.receiveShadow=true;cabin.add(m);});
  cabin.userData.glass=glassMesh;
  // interior warm box so the windows read as lit
  const inner=new THREE.Mesh(new THREE.BoxGeometry(W*1.7,1.6,D*1.7),
    new THREE.MeshStandardMaterial({color:'#000',emissive:'#ff9b45',emissiveIntensity:0}));
  inner.position.y=1.0; cabin.add(inner); cabin.userData.inner=inner;
  addGlow(0,1.2,D+.5,3.4,1.0); addGlow(0,1.2,-D-.4,2.4,.6);
}
cabin.position.set(TER.x,TER.y,TER.z);
cabin.rotation.y=Math.PI*.75;   // face the pier (front toward +X+Z)
scene.add(cabin);

/* ---- deck ---- */
const deckY=TER.y;
const deck=new THREE.Group();
{
  const plankG=[],postG=[];
  const L=3.5,Wd=2.9;
  for(let i=0;i<16;i++){
    const g=new THREE.BoxGeometry(Wd,.07,.17);
    plankG.push(P(g,mtx(0,0,-L/2+.15+i*(L/15.6))));
  }
  const planks=new THREE.Mesh(mergeGeometries(plankG),M.woodPale);
  planks.position.set(0,0,0); planks.castShadow=true; planks.receiveShadow=true; deck.add(planks);
  for(const sx of [-1,1]) for(let i=0;i<=4;i++){
    postG.push(P(new THREE.CylinderGeometry(.055,.055,.52,6),mtx(sx*Wd/2,.26,-L/2+i*(L/4))));
  }
  for(const sx of [-1,1]) postG.push(P(new THREE.BoxGeometry(.07,.07,L),mtx(sx*Wd/2,.48,0)));
  postG.push(P(new THREE.BoxGeometry(Wd,.08,.08),mtx(0,.48,-L/2)));
  // steps down toward the beach
  for(let i=0;i<3;i++) postG.push(P(new THREE.BoxGeometry(1.1,.08,.3),mtx(0,-.12-i*.19,L/2+.25+i*.3)));
  const posts=new THREE.Mesh(mergeGeometries(postG),M.wood);
  posts.castShadow=true; posts.receiveShadow=true; deck.add(posts);
  // supports
  const sup=[];
  for(const sx of[-1,1])for(const sz of[-1,1]) sup.push(P(new THREE.CylinderGeometry(.07,.07,1.6,6),mtx(sx*Wd*.42,-.85,sz*L*.42)));
  const sm=new THREE.Mesh(mergeGeometries(sup),M.woodDark); sm.castShadow=true; deck.add(sm);
}
deck.position.set(TER.x+1.55,deckY+.06,TER.z+1.75);
deck.rotation.y=Math.PI*.75;
scene.add(deck);
lampBeach.position.set(TER.x+2.6,deckY+.9,TER.z+2.9);

/* ---- deck life: table, chairs, crates, plants, lantern ---- */
function crate(x,y,z,s,ry){
  const g=[]; const b=new THREE.BoxGeometry(s,s,s);
  g.push(P(b,mtx(0,0,0)));
  for(const ax of ['x','y','z']) for(const sg of [-1,1]){
    const t=s*.06;
    if(ax==='y') g.push(P(new THREE.BoxGeometry(s*1.03,t,s*1.03),mtx(0,sg*s*.42,0)));
    if(ax==='x') g.push(P(new THREE.BoxGeometry(t,s*1.03,s*1.03),mtx(sg*s*.42,0,0)));
    if(ax==='z') g.push(P(new THREE.BoxGeometry(s*1.03,s*1.03,t),mtx(0,0,sg*s*.42)));
  }
  const m=new THREE.Mesh(mergeGeometries(g),M.woodPale);
  m.position.set(x,y+s/2,z); m.rotation.y=ry; m.castShadow=true; m.receiveShadow=true; scene.add(m); return m;
}
function potted(x,y,z,s,mat){
  const g=new THREE.Group();
  const pot=new THREE.Mesh(new THREE.CylinderGeometry(.16*s,.12*s,.22*s,10),M.pot);
  pot.position.y=.11*s; pot.castShadow=true; g.add(pot);
  for(let i=0;i<4;i++){
    const b=new THREE.Mesh(new THREE.IcosahedronGeometry(.14*s,0),mat||M.leaf);
    b.position.set(R(-.1,.1)*s,.3*s+R(0,.16)*s,R(-.1,.1)*s);
    b.scale.set(1,R(.7,1.1),1); b.castShadow=true; g.add(b);
  }
  g.position.set(x,y,z); scene.add(g); return g;
}
function lanternPost(x,y,z,h){
  const g=new THREE.Group();
  const post=new THREE.Mesh(new THREE.CylinderGeometry(.045,.055,h,6),M.woodDark);
  post.position.y=h/2; post.castShadow=true; g.add(post);
  const arm=new THREE.Mesh(new THREE.BoxGeometry(.34,.05,.05),M.woodDark); arm.position.set(.15,h-.05,0); g.add(arm);
  const cage=new THREE.Mesh(new THREE.CylinderGeometry(.10,.12,.22,6,1,true),M.dark);
  cage.position.set(.30,h-.20,0); g.add(cage);
  const bulb=new THREE.Mesh(new THREE.SphereGeometry(.075,8,6),
    new THREE.MeshStandardMaterial({color:'#fff0c8',emissive:'#ffb45c',emissiveIntensity:0}));
  bulb.position.set(.30,h-.20,0); g.add(bulb); g.userData.bulb=bulb;
  g.position.set(x,y,z); scene.add(g);
  addGlow(x+.30,y+h-.20,z,1.35,1);
  return g;
}
const lanterns=[];
{
  const fx=TER.x,fz=TER.z;
  // deck-side props, positioned in world space along the deck axes
  const ax=new THREE.Vector2(.707,.707);   // downhill / pier direction
  const bx=new THREE.Vector2(-.707,.707);  // along-deck direction
  const at=(u,v)=>[TER.x+1.55+bx.x*u+ax.x*v, TER.z+1.75+bx.y*u+ax.y*v];
  let p=at(-.9,1.0); table(p[0],deckY+.1,p[1]);
  p=at(-1.35,1.75); crate(p[0],deckY+.08,p[1],.42,R(-.4,.4));
  p=at(-1.55,1.35); crate(p[0],deckY+.08,p[1],.34,R(-.4,.4));
  p=at(-1.4,1.55); crate(p[0],deckY+.42,p[1],.28,R(-.4,.4));
  p=at(1.2,.9); potted(p[0],deckY+.08,p[1],1.1);
  p=at(-.2,1.55); potted(p[0],deckY+.08,p[1],.85,M.leafLight);
  p=at(1.5,-.4); potted(p[0],deckY+.08,p[1],.95,M.leafDark);
  p=at(-1.9,.2); lanterns.push(lanternPost(p[0],deckY+.08,p[1],1.5));
  // cabin door lantern
  const dl=lanternPost(TER.x+1.05,TER.y+1.05,TER.z+1.25,1.0); dl.scale.setScalar(.8); lanterns.push(dl);
}
function table(x,y,z){
  const g=new THREE.Group();
  const top=new THREE.Mesh(new THREE.CylinderGeometry(.42,.42,.06,14),M.woodPale);
  top.position.y=.46; top.castShadow=true; g.add(top);
  const leg=new THREE.Mesh(new THREE.CylinderGeometry(.05,.07,.46,6),M.woodDark);
  leg.position.y=.23; leg.castShadow=true; g.add(leg);
  const base=new THREE.Mesh(new THREE.CylinderGeometry(.2,.24,.05,10),M.woodDark);
  base.position.y=.02; g.add(base);
  const mug=new THREE.Mesh(new THREE.CylinderGeometry(.05,.04,.09,8),M.fabricA);
  mug.position.set(.15,.53,.05); mug.castShadow=true; g.add(mug);
  g.position.set(x,y,z); scene.add(g); return g;
}

/* ---- bench on the beach ---- */
{
  const g=new THREE.Group();
  const parts=[];
  parts.push(P(new THREE.BoxGeometry(1.15,.07,.34),mtx(0,.4,0)));
  parts.push(P(new THREE.BoxGeometry(1.15,.34,.07),mtx(0,.6,-.14)));
  for(const s of[-1,1]){
    parts.push(P(new THREE.BoxGeometry(.07,.4,.3),mtx(s*.5,.2,0)));
    parts.push(P(new THREE.BoxGeometry(.06,.06,.34),mtx(s*.5,.42,0)));
  }
  const m=new THREE.Mesh(mergeGeometries(parts),M.woodPale);
  m.castShadow=true; m.receiveShadow=true; g.add(m);
  g.position.set(ISLAND.x+3.05,terrainH(ISLAND.x+3.05,ISLAND.z+2.6)+.02,ISLAND.z+2.6);
  g.rotation.y=Math.PI*.78; scene.add(g);
}
/* ---- towel rack ---- */
const towels=[];
{
  const x=ISLAND.x+2.3,z=ISLAND.z+3.15,y=terrainH(x,z);
  const g=new THREE.Group();
  const parts=[];
  for(const s of[-1,1]) parts.push(P(new THREE.CylinderGeometry(.04,.05,.95,6),mtx(s*.62,.47,0)));
  parts.push(P(new THREE.CylinderGeometry(.035,.035,1.3,6),mtx(0,.92,0)).clone().rotateZ(Math.PI/2));
  const posts=new THREE.Mesh(mergeGeometries(parts),M.woodDark); posts.castShadow=true; g.add(posts);
  for(let i=0;i<2;i++){
    const t=new THREE.Mesh(new THREE.PlaneGeometry(.55,.72,6,8),i?M.fabricA:M.fabricB);
    t.position.set(-.3+i*.6,.55,.03); t.castShadow=true; g.add(t); towels.push(t);
  }
  g.position.set(x,y,z); g.rotation.y=Math.PI*.8; scene.add(g);
}
/* ---- hammock between two trees ---- */
let hammock;
{
  const x=ISLAND.x-1.1,z=ISLAND.z+1.0;
  const g=new THREE.Group();
  const geo=new THREE.PlaneGeometry(1.5,.62,14,4);
  const p=geo.attributes.position;
  for(let i=0;i<p.count;i++){
    const u=(p.getX(i)/1.5+.5);
    p.setZ(i,-Math.sin(u*Math.PI)*.30+Math.cos(u*Math.PI)*.02);
    p.setY(i,p.getY(i)*(0.75+0.25*Math.sin(u*Math.PI)));
  }
  geo.computeVertexNormals();
  const m=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:'#e6dcc4',roughness:1,side:THREE.DoubleSide}));
  sway(m,{amp:.06,freq:1.1,span:.6});
  m.position.y=0; m.castShadow=true; g.add(m); hammock=m;
  g.position.set(x,terrainH(x,z)+.75,z); g.rotation.y=.5; scene.add(g);
}

/* ---- trees & bushes ---- */
{
  const spots=scatter(20,(x,z)=>{
    const h=terrainH(x,z);
    if(h<.95||h>3.1) return false;
    if(Math.hypot(x-TER.x,z-TER.z)<2.5) return false;
    if(Math.hypot(x-ISLAND.x,z-ISLAND.z)>3.5) return false;
    const dh=1.0; const sl=Math.hypot(terrainH(x+dh,z)-terrainH(x-dh,z),terrainH(x,z+dh)-terrainH(x,z-dh))/(2*dh);
    return sl<.85;
  },()=>({}));
  const trunkG=[],coneG=[],blobG=[];
  spots.forEach((s,i)=>{
    const h=terrainH(s.x,s.z), conifer=i%2===0;
    const sc=R(.8,1.35);
    if(conifer){
      trunkG.push(P(new THREE.CylinderGeometry(.07*sc,.11*sc,.7*sc,6),mtx(s.x,h+.35*sc,s.z)));
      for(let k=0;k<3;k++){
        const r=(.62-k*.15)*sc, hh=(.75-k*.1)*sc;
        coneG.push(P(new THREE.ConeGeometry(r,hh,7),mtx(s.x,h+.75*sc+k*.44*sc,s.z,R(-.05,.05),R(0,3),R(-.05,.05))));
      }
    } else {
      trunkG.push(P(new THREE.CylinderGeometry(.06*sc,.1*sc,.85*sc,6),mtx(s.x,h+.42*sc,s.z)));
      for(let k=0;k<3;k++){
        const g2=new THREE.IcosahedronGeometry(R(.42,.6)*sc,0);
        blobG.push(P(g2,mtx(s.x+R(-.28,.28)*sc,h+1.05*sc+R(-.14,.24)*sc,s.z+R(-.28,.28)*sc)));
      }
    }
  });
  const trunks=new THREE.Mesh(mergeGeometries(trunkG),M.bark); trunks.castShadow=true; scene.add(trunks);
  const coneM=new THREE.MeshStandardMaterial({color:'#3d6b43',roughness:.92,flatShading:true});
  sway(coneM,{amp:.055,freq:1.25,span:2.6});
  const cones=new THREE.Mesh(mergeGeometries(coneG),coneM); cones.castShadow=true; scene.add(cones);
  const blobM=new THREE.MeshStandardMaterial({color:'#5c8a45',roughness:.92,flatShading:true});
  sway(blobM,{amp:.075,freq:1.5,span:2.2});
  const blobs=new THREE.Mesh(mergeGeometries(blobG),blobM); blobs.castShadow=true; scene.add(blobs);
  // bushes
  const bs=scatter(26,(x,z)=>{const h=terrainH(x,z);return h>.55&&h<2.6&&Math.hypot(x-TER.x,z-TER.z)>1.9;},()=>({s:R(.2,.45)}));
  const bm=new THREE.MeshStandardMaterial({color:'#4d7a41',roughness:.95,flatShading:true});
  sway(bm,{amp:.09,freq:1.9,span:.7});
  const bg=new THREE.IcosahedronGeometry(1,0);
  const bi=new THREE.InstancedMesh(bg,bm,bs.length);
  bs.forEach((s,i)=>{dummy.position.set(s.x,terrainH(s.x,s.z)+s.s*.4,s.z);dummy.rotation.set(R(0,3),R(0,3),0);
    dummy.scale.set(s.s,s.s*.75,s.s);dummy.updateMatrix();bi.setMatrixAt(i,dummy.matrix);});
  bi.instanceMatrix.needsUpdate=true; bi.castShadow=true; scene.add(bi);
  // grass tufts
  const gs=scatter(320,(x,z)=>{const h=terrainH(x,z);return h>.75&&h<3.0;},()=>({s:R(.14,.3)}));
  const gm=new THREE.MeshStandardMaterial({color:'#79a452',roughness:.95,side:THREE.DoubleSide});
  sway(gm,{amp:.16,freq:2.2,span:.4});
  const tg=bladeGeo(.42,.075,3);
  const gi=new THREE.InstancedMesh(tg,gm,gs.length);
  gs.forEach((s,i)=>{dummy.position.set(s.x,terrainH(s.x,s.z)-.02,s.z);dummy.rotation.set(0,R(0,6.3),0);
    dummy.scale.set(s.s*3,s.s*3,s.s*3);dummy.updateMatrix();gi.setMatrixAt(i,dummy.matrix);});
  gi.instanceMatrix.needsUpdate=true; scene.add(gi);
  // reeds at the waterline
  const rs=scatter(70,(x,z)=>{const h=terrainH(x,z);return h>-.05&&h<.5;},()=>({s:R(.5,1.1)}));
  const rm=new THREE.MeshStandardMaterial({color:'#879150',roughness:.9,side:THREE.DoubleSide});
  underwater(rm,.4); sway(rm,{amp:.2,freq:2.6,span:1.0});
  const rg=bladeGeo(.95,.05,4);
  const ri=new THREE.InstancedMesh(rg,rm,rs.length);
  rs.forEach((s,i)=>{dummy.position.set(s.x,terrainH(s.x,s.z)-.05,s.z);dummy.rotation.set(0,R(0,6.3),0);
    dummy.scale.set(s.s,s.s,s.s);dummy.updateMatrix();ri.setMatrixAt(i,dummy.matrix);});
  ri.instanceMatrix.needsUpdate=true; scene.add(ri);
  // shells & pebbles
  const ss=scatter(60,(x,z)=>{const h=terrainH(x,z);return h>-.15&&h<.7;},()=>({s:R(.05,.11)}));
  const sm=new THREE.MeshStandardMaterial({color:'#f0e3cd',roughness:.6,flatShading:true});
  const si=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1,0),sm,ss.length);
  ss.forEach((s,i)=>{dummy.position.set(s.x,terrainH(s.x,s.z)+s.s*.3,s.z);dummy.rotation.set(R(0,3),R(0,3),0);
    dummy.scale.set(s.s,s.s*.4,s.s);dummy.updateMatrix();si.setMatrixAt(i,dummy.matrix);});
  si.instanceMatrix.needsUpdate=true; scene.add(si);
}

/* ---- PIER ---- */
const DECK_Y=.82;
const pierEnd=new THREE.Vector3(5.35,DECK_Y,5.05);
const pierStart=new THREE.Vector3(0.72,DECK_Y,0.42);
{
  const dir=new THREE.Vector3().subVectors(pierEnd,pierStart).normalize();
  const len=pierStart.distanceTo(pierStart.clone().add(dir.clone().multiplyScalar(0)));
  const L=pierStart.distanceTo(pierEnd);
  const ang=Math.atan2(dir.x,dir.z);
  const g=new THREE.Group(); g.position.copy(pierStart); g.rotation.y=ang;
  const plankG=[],postG=[];
  const n=Math.round(L/.24);
  for(let i=0;i<=n;i++) plankG.push(P(new THREE.BoxGeometry(1.5,.07,.19),mtx(0,0,i*(L/n)-L/2)));
  for(const s of[-1,1]){
    plankG.push(P(new THREE.BoxGeometry(.12,.12,L),mtx(s*.62,-.1,0)));
    for(let i=0;i<=4;i++){
      const z=-L/2+i*(L/4);
      postG.push(P(new THREE.CylinderGeometry(.085,.1,L+3.0,7),mtx(s*.66,-(L+3.0)/2+.35,z)));
      postG.push(P(new THREE.BoxGeometry(.1,.1,.1),mtx(s*.66,.16,z)));
    }
    plankG.push(P(new THREE.BoxGeometry(.09,.09,L+.2),mtx(s*.68,.5,0)));
    for(let i=0;i<=10;i++) plankG.push(P(new THREE.BoxGeometry(.05,.4,.05),mtx(s*.68,.3,-L/2+i*(L/10))));
  }
  // T-platform at the end
  for(let i=0;i<8;i++) plankG.push(P(new THREE.BoxGeometry(2.6,.07,.2),mtx(0,0,L/2+.12+i*.22)));
  for(const s of[-1,1]){
    postG.push(P(new THREE.CylinderGeometry(.09,.1,4.2,7),mtx(s*1.15,-2.0,L/2+.95)));
    plankG.push(P(new THREE.BoxGeometry(.1,.1,2.2),mtx(s*1.2,.48,L/2+.1)));
  }
  const pm=new THREE.Mesh(mergeGeometries(plankG),M.woodPale);
  pm.castShadow=true; pm.receiveShadow=true; g.add(pm);
  const po=new THREE.Mesh(mergeGeometries(postG),M.woodDark);
  po.castShadow=true; g.add(po);
  // ladder down into the water (on the seaward side)
  const lad=new THREE.Group();
  const lg=[];
  for(const s of[-1,1]) lg.push(P(new THREE.CylinderGeometry(.045,.045,2.0,6),mtx(s*.19,-.95,0)));
  for(let i=0;i<6;i++) lg.push(P(new THREE.CylinderGeometry(.035,.035,.4,6),mtx(0,-.25-i*.3,0)).clone().rotateZ(Math.PI/2));
  const lm=new THREE.Mesh(mergeGeometries(lg),M.woodPale); lm.castShadow=true; lad.add(lm);
  lad.position.set(1.35,.15,L/2+.6); lad.rotation.y=.12; g.add(lad);
  // cleats + coil of rope + barrel + crates
  const cl=new THREE.Mesh(new THREE.CylinderGeometry(.07,.09,.22,8),M.dark);
  cl.position.set(-.9,.2,L/2+.4); g.add(cl);
  const rope=new THREE.Mesh(new THREE.TorusGeometry(.22,.045,6,16),M.rope);
  rope.rotation.x=-Math.PI/2; rope.position.set(-.75,.08,L/2+.95); rope.castShadow=true; g.add(rope);
  const bar=new THREE.Mesh(new THREE.CylinderGeometry(.24,.22,.6,12),M.woodDark);
  bar.position.set(-.55,.42,-L*.35); bar.castShadow=true; g.add(bar);
  g.add((()=>{const c=crate(0,0,0,.4,.3); c.position.set(.55,.04,-L*.5); c.parent&&0; return c;})());
  // lanterns along the pier
  for(const t of[-.28,.22,.72]){
    const z=-L/2+t*L;
    const lp=new THREE.Group();
    lp.add(new THREE.Mesh(new THREE.CylinderGeometry(.04,.05,.75,6),M.woodDark)).position.y=.5;
    const cage=new THREE.Mesh(new THREE.CylinderGeometry(.09,.11,.2,6,1,true),M.dark); cage.position.y=.92; lp.add(cage);
    const bulb=new THREE.Mesh(new THREE.SphereGeometry(.07,8,6),
      new THREE.MeshStandardMaterial({color:'#fff0c8',emissive:'#ffb45c',emissiveIntensity:0}));
    bulb.position.y=.92; lp.add(bulb); lanterns.push({userData:{bulb},position:new THREE.Vector3(),scale:new THREE.Vector3(1,1,1)});
    lanterns[lanterns.length-1]=lp; lp.userData.bulb=bulb;
    lp.position.set(-.68,.12,z); lp.children.forEach(c=>c.castShadow=true);
    g.add(lp);
    const wp=new THREE.Vector3().copy(lp.position); g.localToWorld(wp);
    wp.y+=.92; addGlow(wp.x,wp.y,wp.z,1.5,1);
    if(t===.22) lampPier.position.set(wp.x,wp.y,wp.z);
  }
  scene.add(g);
  // mooring rope to the kayak
  const moor=new THREE.Mesh(new THREE.CylinderGeometry(.025,.025,1.0,5),M.rope);
  scene.add(moor); scene.userData.moor=moor;
}
/* ---- kayak ---- */
const kayak=new THREE.Group();
{
  const hull=new THREE.SphereGeometry(.3,16,10);
  const p=hull.attributes.position;
  for(let i=0;i<p.count;i++){
    let x=p.getX(i),y=p.getY(i),z=p.getZ(i);
    z*=4.6; x*=1.15; y*=.72;
    const t=Math.min(1,Math.abs(z)/1.45);
    x*=1-.72*Math.pow(t,2.4); y*=1-.55*Math.pow(t,3.0);
    if(y>0) y*=.62;
    p.setXYZ(i,x,y,z);
  }
  hull.computeVertexNormals();
  const hm=new THREE.Mesh(hull,M.kayak); hm.castShadow=true; hm.receiveShadow=true; kayak.add(hm);
  const cock=new THREE.Mesh(new THREE.CylinderGeometry(.20,.22,.16,12),M.dark);
  cock.scale.set(1,.5,2.0); cock.position.y=.10; kayak.add(cock);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(.21,.022,5,18),M.kayakTrim);
  rim.rotation.x=Math.PI/2; rim.scale.set(1,2.0,1); rim.position.y=.14; kayak.add(rim);
  const seat=new THREE.Mesh(new THREE.BoxGeometry(.3,.04,.16),M.woodPale); seat.position.set(0,.12,-.1); kayak.add(seat);
  for(const s of[1,-1]){
    const tip=new THREE.Mesh(new THREE.SphereGeometry(.07,8,6),M.kayakTrim);
    tip.position.set(0,.02,s*1.32); tip.scale.set(1,.7,1.6); kayak.add(tip);
  }
  const paddle=new THREE.Group();
  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.022,.022,1.5,6),M.woodPale);
  shaft.rotation.z=Math.PI/2; paddle.add(shaft);
  for(const s of[1,-1]){
    const bl=new THREE.Mesh(new THREE.BoxGeometry(.30,.02,.13),M.woodPale);
    bl.position.set(s*.72,0,0); bl.rotation.z=s*.25; paddle.add(bl);
  }
  paddle.position.set(0,.24,.15); paddle.rotation.y=.5; kayak.add(paddle);
  kayak.userData.paddle=paddle;
}
scene.add(kayak);
const kayakDock={pos:new THREE.Vector3(5.95,DECK_Y-.35,4.45),rot:.62};
kayak.position.copy(kayakDock.pos); kayak.rotation.y=kayakDock.rot;

/* ---- buoy ---- */
const buoy=new THREE.Group();
{
  const b=new THREE.Mesh(new THREE.SphereGeometry(.17,12,9),M.fabricA);
  b.scale.y=.85; b.castShadow=true; buoy.add(b);
  const s=new THREE.Mesh(new THREE.CylinderGeometry(.012,.012,.34,4),M.dark); s.position.y=.28; buoy.add(s);
  const t=new THREE.Mesh(new THREE.SphereGeometry(.045,6,5),M.dark); t.position.y=.46; buoy.add(t);
}
buoy.position.set(6.9,0,2.4); scene.add(buoy);

/* ---- smoke, fireflies, droplets (points systems) ---- */
function pointsSys(n,frag,color,size){
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(n*3),3));
  g.setAttribute('aSize',new THREE.BufferAttribute(new Float32Array(n),1));
  g.setAttribute('aAlpha',new THREE.BufferAttribute(new Float32Array(n),1));
  const m=new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.NormalBlending,
    uniforms:{uCol:{value:new THREE.Color(color)},uH:{value:600}},
    vertexShader:`attribute float aSize; attribute float aAlpha; varying float vA; uniform float uH;
      void main(){ vA=aAlpha; vec4 mv=modelViewMatrix*vec4(position,1.0);
        gl_PointSize=aSize*uH/max(0.001,-mv.z); gl_Position=projectionMatrix*mv; }`,
    fragmentShader:`varying float vA; uniform vec3 uCol; ${frag}`});
  const pts=new THREE.Points(g,m); pts.frustumCulled=false; scene.add(pts);
  return {pts,g,m};
}
const softFrag=`void main(){ vec2 d=gl_PointCoord-0.5; float r=length(d);
  if(r>0.5) discard; float a=smoothstep(0.5,0.05,r)*vA; gl_FragColor=vec4(uCol,a); }`;
const sparkFrag=`void main(){ vec2 d=gl_PointCoord-0.5; float r=length(d);
  if(r>0.5) discard; float a=smoothstep(0.5,0.15,r)*vA;
  gl_FragColor=vec4(uCol+vec3(0.4)*smoothstep(0.25,0.0,r),a); }`;
const SMOKE_N=30, smoke=pointsSys(SMOKE_N,softFrag,'#cfd6d8',1);
const smokeD=[]; for(let i=0;i<SMOKE_N;i++) smokeD.push({x:0,y:-99,z:0,life:R(0,1),max:R(2.5,4.5),s:R(.5,1.4)});
const FF_N=44, ff=pointsSys(FF_N,sparkFrag,'#ffd489',1);
const ffD=[]; for(let i=0;i<FF_N;i++) ffD.push({x:ISLAND.x+R(-3,3),y:0,z:ISLAND.z+R(-3,3),ph:R(0,6.3),sp:R(.3,1)});
const DROP_N=90, drops=pointsSys(DROP_N,sparkFrag,'#dff8ff',1);
drops.pts.material.blending=THREE.AdditiveBlending;
const dropD=[]; for(let i=0;i<DROP_N;i++) dropD.push({x:0,y:-99,z:0,vx:0,vy:0,vz:0,life:0});

/* ---- gulls & clouds ---- */
const gulls=[];
{
  const wing=new THREE.PlaneGeometry(.42,.16);
  wing.translate(.21,0,0);
  for(let i=0;i<3;i++){
    const g=new THREE.Group();
    const mat=new THREE.MeshStandardMaterial({color:'#f4f1e8',roughness:.9,side:THREE.DoubleSide});
    const l=new THREE.Mesh(wing,mat), r=new THREE.Mesh(wing,mat);
    r.scale.x=-1; g.add(l,r);
    const body=new THREE.Mesh(new THREE.CapsuleGeometry(.05,.2,4,6),mat);
    body.rotation.x=Math.PI/2; g.add(body);
    g.userData={l,r,ph:R(0,6.3),rad:R(5.5,8),y:R(6,9),sp:R(.14,.24),off:R(0,6.3)};
    scene.add(g); gulls.push(g);
  }
}
const clouds=[];
{
  const mat=new THREE.MeshStandardMaterial({color:'#ffffff',roughness:1,flatShading:true,transparent:true,opacity:.9});
  for(let i=0;i<7;i++){
    const g=[]; const n=3+((rnd()*4)|0);
    for(let k=0;k<n;k++){
      const s=R(.9,2.1);
      g.push(P(new THREE.IcosahedronGeometry(s,0),mtx(R(-2.4,2.4),R(-.4,.5),R(-1.2,1.2),0,R(0,3),0)));
    }
    const m=new THREE.Mesh(mergeGeometries(g),mat);
    m.position.set(R(-60,60),R(20,34),R(-60,60)); m.scale.y=.55;
    scene.add(m); clouds.push(m);
  }
}

/* ============================================================================
   8 · INTERACTION STATE
   ========================================================================== */
const state={paused:false, tide:0, wind:.34, cam:'iso', camTween:null,
  kayak:{mode:'dock', t:0, from:new THREE.Vector3(), blend:0}};
const kayakPath=new THREE.CatmullRomCurve3([
  new THREE.Vector3(5.4,0,4.6), new THREE.Vector3(7.9,0,1.6), new THREE.Vector3(7.2,0,-3.0),
  new THREE.Vector3(4.4,0,-6.4), new THREE.Vector3(0.0,0,-7.7), new THREE.Vector3(-4.8,0,-7.6),
  new THREE.Vector3(-7.4,0,-4.2), new THREE.Vector3(-7.8,0,0.6), new THREE.Vector3(-5.2,0,4.8),
  new THREE.Vector3(-1.6,0,7.2), new THREE.Vector3(2.6,0,7.6), new THREE.Vector3(5.0,0,6.4)
],true,'catmullrom',.5);
const leap={active:false,t:0,dur:2.9,ray:null,from:new THREE.Vector3(),to:new THREE.Vector3(),
  prev:new THREE.Vector3(),above:false};

function spawnRipple(x,z,strength,speed){
  let best=ripples[0],bv=1e9;
  for(const r of ripples){ if(r.w<bv){bv=r.w;best=r;} }
  best.set(x,z,.25,strength); best.userData=(best.userData||0);
  ripplesMeta[ripples.indexOf(best)]={sp:speed||2.2,life:0};
}
const ripplesMeta=ripples.map(()=>({sp:2.2,life:0}));
function spawnDroplets(x,y,z,n,spread){
  let s=0;
  for(let i=0;i<DROP_N&&s<n;i++){
    const d=dropD[i];
    if(d.life>0) continue;
    d.x=x+R(-.3,.3); d.y=y; d.z=z+R(-.3,.3);
    d.vx=R(-spread,spread); d.vy=R(1.6,4.2); d.vz=R(-spread,spread);
    d.life=R(.7,1.4); s++;
  }
}
function triggerLeap(){
  if(leap.active) return;
  const r=hero; r.leaping=true; leap.active=true; leap.t=0; leap.ray=r;
  leap.from.copy(r.group.position);
  leap.prev.copy(leap.from);
  const dir=new THREE.Vector3(Math.sin(r.heading),0,Math.cos(r.heading));
  leap.to.copy(leap.from).addScaledVector(dir,4.6);
  leap.to.x=clamp(leap.to.x,-6.2,6.6); leap.to.z=clamp(leap.to.z,-6.2,6.6);
  leap.to.y=r.yc;
  leap.above=leap.from.y>U.level.value;
  Audio.splash(.35); toast('A ray breaches');
}
function toggleKayak(){
  const k=state.kayak;
  if(k.mode==='dock'){
    k.mode='launch'; k.blend=0;
    k.from.copy(kayak.position);
    toast('Kayak cast off — around the lagoon');
    Audio.creak();
  } else {
    k.mode='return'; k.blend=0; toast('Kayak heading home'); Audio.creak();
  }
}
/* cameras */
const CAMS={
  iso:{dir:new THREE.Vector3(1,.80,1).normalize(),dist:56,tgt:new THREE.Vector3(.3,-.4,.3),fov:22},
  cabin:{dir:new THREE.Vector3(.86,.30,.86).normalize(),dist:16.5,tgt:new THREE.Vector3(-.9,1.5,-.6),fov:34},
  reef:{dir:new THREE.Vector3(.72,-.20,.72).normalize(),dist:11.5,tgt:new THREE.Vector3(1.2,-2.1,1.2),fov:52}
};
function fitScale(){ const a=innerWidth/innerHeight; return clamp(1.55/a,1,2.1); }
function camPos(name){
  const c=CAMS[name], f=(name==='iso')?fitScale():clamp(1.25/(innerWidth/innerHeight),1,1.7);
  return {pos:c.dir.clone().multiplyScalar(c.dist*f),tgt:c.tgt.clone(),fov:c.fov};
}
function setCam(name,instant){
  if(name==='free'){ setCamBtn('free'); state.cam='free'; return; }
  const p=camPos(name);
  state.cam=name; setCamBtn(name);
  if(instant){ camera.position.copy(p.pos); controls.target.copy(p.tgt); camera.fov=p.fov; camera.updateProjectionMatrix(); return; }
  state.camTween={t:0,dur:1.5,
    p0:camera.position.clone(),p1:p.pos,t0:controls.target.clone(),t1:p.tgt,f0:camera.fov,f1:p.fov};
  controls.enabled=false;
}
function setCamBtn(n){ document.querySelectorAll('[data-cam]').forEach(b=>b.classList.toggle('on',b.dataset.cam===n)); }

/* ============================================================================
   9 · AUDIO — procedural ambience + music (Web Audio API)
   ========================================================================== */
const Audio={
  ctx:null,ready:false,on:true,vol:.55,
  init(){
    if(this.ctx) return;
    const AC=window.AudioContext||window.webkitAudioContext; if(!AC) return;
    const c=this.ctx=new AC();
    this.master=c.createGain(); this.master.gain.value=0; this.master.connect(c.destination);
    this.music=c.createGain(); this.music.gain.value=.5; this.music.connect(this.master);
    this.amb=c.createGain(); this.amb.gain.value=.9; this.amb.connect(this.master);
    // noise source
    const len=c.sampleRate*3, buf=c.createBuffer(1,len,c.sampleRate), d=buf.getChannelData(0);
    let lp=0; for(let i=0;i<len;i++){ const w=Math.random()*2-1; lp=(lp+.02*w)/1.02; d[i]=w*.5+lp*3; }
    this.noise=buf;
    // water lapping
    const ws=c.createBufferSource(); ws.buffer=buf; ws.loop=true;
    const wf=c.createBiquadFilter(); wf.type='bandpass'; wf.frequency.value=520; wf.Q.value=.8;
    this.wg=c.createGain(); this.wg.gain.value=.10;
    ws.connect(wf); wf.connect(this.wg); this.wg.connect(this.amb); ws.start();
    const lfo=c.createOscillator(); lfo.frequency.value=.09;
    const lg=c.createGain(); lg.gain.value=.055; lfo.connect(lg); lg.connect(this.wg.gain); lfo.start();
    const lfo2=c.createOscillator(); lfo2.frequency.value=.045;
    const lg2=c.createGain(); lg2.gain.value=180; lfo2.connect(lg2); lg2.connect(wf.frequency); lfo2.start();
    // wind
    const wn=c.createBufferSource(); wn.buffer=buf; wn.loop=true;
    const wnf=c.createBiquadFilter(); wnf.type='lowpass'; wnf.frequency.value=420; wnf.Q.value=1.2;
    this.wnd=c.createGain(); this.wnd.gain.value=.03;
    wn.connect(wnf); wnf.connect(this.wnd); this.wnd.connect(this.amb); wn.start();
    this.windF=wnf;
    const wl=c.createOscillator(); wl.frequency.value=.07;
    const wlg=c.createGain(); wlg.gain.value=.022; wl.connect(wlg); wlg.connect(this.wnd.gain); wl.start();
    // drone pad
    this.pad=c.createGain(); this.pad.gain.value=.075; this.pad.connect(this.music);
    const pf=c.createBiquadFilter(); pf.type='lowpass'; pf.frequency.value=520; pf.Q.value=.6; pf.connect(this.pad);
    [110,164.81,220,277.18].forEach((f,i)=>{
      const o=c.createOscillator(); o.type=i%2?'triangle':'sawtooth'; o.frequency.value=f/2;
      o.detune.value=(i-1.5)*6;
      const g=c.createGain(); g.gain.value=.22; o.connect(g); g.connect(pf); o.start();
      const v=c.createOscillator(); v.frequency.value=.05+i*.017;
      const vg=c.createGain(); vg.gain.value=.12; v.connect(vg); vg.connect(g.gain); v.start();
    });
    // reverb-ish delay
    this.dly=c.createDelay(1.2); this.dly.delayTime.value=.38;
    const fb=c.createGain(); fb.gain.value=.34;
    const df=c.createBiquadFilter(); df.type='lowpass'; df.frequency.value=1800;
    this.dly.connect(df); df.connect(fb); fb.connect(this.dly);
    this.dlyOut=c.createGain(); this.dlyOut.gain.value=.5; df.connect(this.dlyOut); this.dlyOut.connect(this.master);
    // music scheduler
    this.scale=[220,246.94,277.18,329.63,369.99,440,493.88,554.37,659.25];
    this.next=0; this.timer=setInterval(()=>this.sched(),40);
    this.ready=true; this.apply();
  },
  sched(){
    if(!this.ctx||!this.on) return;
    const c=this.ctx;
    while(this.next<c.currentTime+.25){
      if(Math.random()<.62){
        const f=this.scale[(Math.random()*this.scale.length)|0];
        this.note(f,this.next,.055+Math.random()*.05);
        if(Math.random()<.22) this.note(f*1.5,this.next+.14+Math.random()*.2,.03);
      }
      this.next+=1.05+Math.random()*.9;
    }
  },
  note(f,t,g){
    const c=this.ctx, o=c.createOscillator(), o2=c.createOscillator(), gn=c.createGain();
    o.type='sine'; o.frequency.value=f; o2.type='triangle'; o2.frequency.value=f*2.003;
    const g2=c.createGain(); g2.gain.value=.25;
    gn.gain.setValueAtTime(0,t); gn.gain.linearRampToValueAtTime(g,t+.03);
    gn.gain.exponentialRampToValueAtTime(.0001,t+2.4);
    o.connect(gn); o2.connect(g2); g2.connect(gn); gn.connect(this.music); gn.connect(this.dly);
    o.start(t); o2.start(t); o.stop(t+2.6); o2.stop(t+2.6);
  },
  blip(f=880,g=.05){
    if(!this.ctx||!this.on) return;
    const c=this.ctx,t=c.currentTime,o=c.createOscillator(),gn=c.createGain();
    o.type='triangle'; o.frequency.value=f;
    gn.gain.setValueAtTime(g,t); gn.gain.exponentialRampToValueAtTime(.0001,t+.14);
    o.connect(gn); gn.connect(this.master); o.start(t); o.stop(t+.16);
  },
  splash(v=1){
    if(!this.ctx||!this.on) return;
    const c=this.ctx,t=c.currentTime,s=c.createBufferSource(); s.buffer=this.noise; s.loop=true;
    const f=c.createBiquadFilter(); f.type='bandpass'; f.Q.value=1.1;
    f.frequency.setValueAtTime(2400,t); f.frequency.exponentialRampToValueAtTime(280,t+.55);
    const g=c.createGain(); g.gain.setValueAtTime(0,t);
    g.gain.linearRampToValueAtTime(.34*v,t+.02); g.gain.exponentialRampToValueAtTime(.0001,t+.85);
    s.connect(f); f.connect(g); g.connect(this.master); g.connect(this.dly);
    s.start(t); s.stop(t+1.0);
  },
  creak(){
    if(!this.ctx||!this.on) return;
    const c=this.ctx,t=c.currentTime,s=c.createBufferSource(); s.buffer=this.noise; s.loop=true;
    const f=c.createBiquadFilter(); f.type='bandpass'; f.frequency.value=340; f.Q.value=9;
    const g=c.createGain(); g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(.10,t+.08);
    g.gain.exponentialRampToValueAtTime(.0001,t+.7);
    const o=c.createOscillator(); o.type='sine'; o.frequency.setValueAtTime(120,t);
    o.frequency.linearRampToValueAtTime(88,t+.6);
    const og=c.createGain(); og.gain.setValueAtTime(.05,t); og.gain.exponentialRampToValueAtTime(.0001,t+.6);
    s.connect(f); f.connect(g); g.connect(this.master); o.connect(og); og.connect(this.master);
    s.start(t); s.stop(t+.8); o.start(t); o.stop(t+.7);
  },
  setWind(w){ if(this.windF) this.windF.frequency.value=320+w*1400; if(this.wnd) this.wnd.gain.value=.018+w*.075; },
  apply(){
    if(!this.ctx) return;
    const t=this.ctx.currentTime;
    this.master.gain.cancelScheduledValues(t);
    this.master.gain.linearRampToValueAtTime(this.on?this.vol*.9:0,t+.35);
  },
  toggle(){ this.on=!this.on; this.init(); this.apply(); return this.on; },
  setVol(v){ this.vol=v; this.apply(); }
};

/* ============================================================================
   10 · UI WIRING
   ========================================================================== */
const $=s=>document.querySelector(s);
const toastEl=$('#toast'); let toastT=0;
function toast(msg){ toastEl.textContent=msg; toastEl.classList.add('show'); clearTimeout(toastT);
  toastT=setTimeout(()=>toastEl.classList.remove('show'),2400); }
function fill(el){ const p=(el.value-el.min)/(el.max-el.min)*100; el.style.setProperty('--v',p+'%'); }
document.querySelectorAll('input[type=range]').forEach(fill);

const sTide=$('#sTide'),sWind=$('#sWind'),sVol=$('#sVol');
function updateTideReadout(){
  const m=state.tide;
  $('#vTide').textContent=(m>=0?'+':'')+m.toFixed(2)+' m';
  $('#roTide').textContent=(m>=0?'+':'')+m.toFixed(2)+' m';
}
function updateWindReadout(){
  const kn=Math.round(state.wind*26);
  $('#vWind').textContent=kn+' kn'; $('#roWind').parentElement.nextElementSibling;
  document.querySelectorAll('.readout b')[2].textContent=kn+' kn';
}
sTide.addEventListener('input',()=>{ state.tide=+sTide.value/100; fill(sTide); updateTideReadout(); });
sWind.addEventListener('input',()=>{ state.wind=+sWind.value/100; fill(sWind); updateWindReadout(); Audio.setWind(state.wind); });
sVol.addEventListener('input',()=>{ Audio.setVol(+sVol.value/100); fill(sVol); $('#vVol').textContent=sVol.value; });

document.querySelectorAll('[data-tod]').forEach(b=>b.addEventListener('click',()=>{
  setTimeOfDay(b.dataset.tod); Audio.blip(660,.04);
  document.querySelectorAll('.readout b')[0].textContent=
    b.dataset.tod==='day'?'Midday':b.dataset.tod==='sunset'?'Golden hour':'Night';
}));
document.querySelectorAll('[data-cam]').forEach(b=>b.addEventListener('click',()=>{
  setCam(b.dataset.cam); Audio.blip(520,.04); document.body.classList.remove('sheet');
}));
$('#bKayak').addEventListener('click',e=>{ toggleKayak(); e.currentTarget.classList.toggle('on',state.kayak.mode!=='dock'); });
$('#bRay').addEventListener('click',()=>triggerLeap());
$('#bPause').addEventListener('click',e=>{
  state.paused=!state.paused; e.currentTarget.classList.toggle('on',state.paused);
  e.currentTarget.textContent=state.paused?'Resume world':'Pause world';
  toast(state.paused?'World paused':'World resumed'); Audio.blip(state.paused?300:600,.05);
});
$('#bReset').addEventListener('click',()=>{
  state.tide=0; sTide.value=0; fill(sTide); updateTideReadout();
  state.wind=.34; sWind.value=34; fill(sWind); updateWindReadout();
  setTimeOfDay('day'); document.querySelectorAll('.readout b')[0].textContent='Midday';
  state.paused=false; $('#bPause').classList.remove('on'); $('#bPause').textContent='Pause world';
  $('#bKayak').classList.remove('on');
  Object.assign(state.kayak,{mode:'dock',t:0,blend:0});
  leap.active=false; hero.leaping=false; hero.recover=0;
  ripples.forEach(r=>r.set(0,0,0,0));
  rays.forEach((r,i)=>r.ph=[0,2.4,4.1][i]||0);
  setCam('iso'); toast('Diorama restored'); Audio.blip(880,.05);
});
$('#bSound').addEventListener('click',e=>{
  const on=Audio.toggle(); e.currentTarget.classList.toggle('on',on);
  $('#vVol').textContent=on?sVol.value:'0';
  if(on) Audio.setVol(+sVol.value/100);
  toast(on?'Sound on':'Sound muted');
});
$('#qSel').addEventListener('change',e=>applyQuality(e.target.value));
$('#sheetBtn').addEventListener('click',()=>{document.body.classList.toggle('sheet');Audio.blip(700,.03);});
addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT') return;
  const k=e.key.toLowerCase();
  if(k==='1'){setCam('iso');} else if(k==='2'){setCam('cabin');}
  else if(k==='3'){setCam('reef');} else if(k==='4'){setCam('free');}
  else if(k==='k'){toggleKayak(); $('#bKayak').classList.toggle('on',state.kayak.mode!=='dock');}
  else if(k==='r'){triggerLeap();}
  else if(k==='0'){$('#bReset').click();}
  else if(e.code==='Space'){e.preventDefault();$('#bPause').click();}
});
// intro / first gesture unlocks audio
let started=false;
function begin(){
  if(started) return; started=true;
  $('#intro').classList.add('gone');
  Audio.init(); Audio.setVol(+sVol.value/100);
  $('#bSound').classList.add('on');
  setTimeout(()=>toast('Drag to orbit · try the reef camera'),1400);
}
$('#begin').addEventListener('click',begin);
addEventListener('pointerdown',()=>{ if(!started) Audio.init(); },{once:true});
// audio follows the scene
addEventListener('pointerdown',()=>{ if(started&&!Audio.ctx) Audio.init(); });

/* ============================================================================
   11 · RESIZE
   ========================================================================== */
function onResize(){
  const w=innerWidth,h=innerHeight;
  camera.aspect=w/h; camera.updateProjectionMatrix();
  renderer.setSize(w,h,false);
  const pr=renderer.getPixelRatio();
  U.pixel.value=pr;
  const hh=(h*pr)/(2*Math.tan(camera.fov*Math.PI/360));
  smoke.m.uniforms.uH.value=hh; ff.m.uniforms.uH.value=hh; drops.m.uniforms.uH.value=hh;
  if(!state.camTween&&state.cam!=='free'){
    const p=camPos(state.cam);
    camera.position.copy(p.pos); controls.target.copy(p.tgt);
    camera.fov=p.fov; camera.updateProjectionMatrix();
  }
}
addEventListener('resize',onResize);
document.addEventListener('visibilitychange',()=>{ clock.getDelta(); });

/* ============================================================================
   12 · ANIMATION LOOP
   ========================================================================== */
const clock=new THREE.Clock();
let elapsed=0;
const tmpV=new THREE.Vector3(), tmpV2=new THREE.Vector3(), tmpQ=new THREE.Quaternion();
const up=new THREE.Vector3(0,1,0);

function animate(){
  requestAnimationFrame(animate);
  const raw=Math.min(clock.getDelta(),.05);
  const dt=state.paused?0:raw;
  elapsed+=dt;
  U.time.value=elapsed;
  U.wind.value=lerp(U.wind.value,state.wind,1-Math.pow(.001,raw));
  U.level.value=lerp(U.level.value,state.tide,1-Math.pow(.002,raw));

  updateTOD(raw);

  /* --- camera tween --- */
  if(state.camTween){
    const tw=state.camTween; tw.t=Math.min(1,tw.t+raw/tw.dur);
    const e=easeIO(tw.t);
    camera.position.lerpVectors(tw.p0,tw.p1,e);
    controls.target.lerpVectors(tw.t0,tw.t1,e);
    camera.fov=lerp(tw.f0,tw.f1,e); camera.updateProjectionMatrix();
    if(tw.t>=1){ state.camTween=null; controls.enabled=true; }
  }
  controls.update();

  /* --- underwater overlay + point size --- */
  const insideBox=Math.abs(camera.position.x)<HALF&&Math.abs(camera.position.z)<HALF;
  const uw=sat(sstep(U.level.value+.25,U.level.value-.7,camera.position.y)*(insideBox?1:0));
  const uwEl=$('#uwFx'); uwEl.style.opacity=uw.toFixed(3); uwEl.classList.toggle('on',uw>.02);

  /* --- ripples --- */
  ripples.forEach((r,i)=>{
    if(r.w>.001){
      const m=ripplesMeta[i]; m.life+=dt;
      r.z+=dt*m.sp; r.w=Math.max(0,r.w-dt*.42);
    }
  });

  /* --- rays --- */
  rays.forEach((r,i)=>{
    if(r.leaping) return;
    const t=elapsed*r.spd+r.ph;
    const px=r.cx+Math.sin(t)*r.rx;
    const pz=r.cz+Math.sin(t*.77+r.ph)*r.rz;
    const py=clamp(r.yc+Math.sin(t*.9+r.ph*1.3)*r.ya,U.level.value-1.2,SEABED+1.3);
    tmpV.set(px,py,pz);
    if(r.recover>0){
      r.recover=Math.max(0,r.recover-dt/1.4);
      tmpV.lerp(r.pos,1-Math.pow(r.recover,2));
    }
    tmpV2.copy(tmpV).sub(r.pos);
    r.pos.copy(tmpV);
    if(tmpV2.lengthSq()>1e-8){
      const want=Math.atan2(tmpV2.x,tmpV2.z);
      let d=want-r.heading; while(d>Math.PI)d-=Math.PI*2; while(d<-Math.PI)d+=Math.PI*2;
      r.heading+=d*Math.min(1,dt*2.4);
      r.bank=lerp(r.bank||0,clamp(-d*3,-.5,.5),dt*3);
    }
    r.group.position.copy(tmpV);
    r.group.rotation.set(Math.sin(elapsed*1.2+r.ph)*.05,r.heading,r.bank||0);
  });
  /* --- leap --- */
  if(leap.active){
    const r=leap.ray; leap.t+=dt/leap.dur;
    const u=Math.min(1,leap.t), e=easeIO(u);
    tmpV.lerpVectors(leap.from,leap.to,e);
    const arc=Math.sin(Math.PI*u)*3.35;
    tmpV.y=lerp(leap.from.y,leap.to.y,u)+arc;
    tmpV2.copy(tmpV).sub(leap.prev);
    r.group.position.copy(tmpV);
    if(tmpV2.lengthSq()>1e-9){
      const h=Math.atan2(tmpV2.x,tmpV2.z);
      r.group.rotation.y=h;
      const horiz=Math.hypot(tmpV2.x,tmpV2.z);
      r.group.rotation.x=-Math.atan2(tmpV2.y,horiz)*.85;
      r.group.rotation.z=u*Math.PI*2;
      r.heading=h;
    }
    const nowAbove=tmpV.y>U.level.value;
    if(nowAbove!==leap.above){
      spawnRipple(tmpV.x,tmpV.z,nowAbove?.85:1.15,nowAbove?1.6:2.6);
      spawnDroplets(tmpV.x,U.level.value+.05,tmpV.z,nowAbove?14:26,nowAbove?1.4:2.4);
      Audio.splash(nowAbove?.4:1);
      leap.above=nowAbove;
    }
    if(u>=1){
      leap.active=false; r.leaping=false; r.recover=1; r.pos.copy(tmpV);
    }
    leap.prev.copy(tmpV);
  }

  /* --- fish --- */
  schools.forEach((s,si)=>{
    const t=elapsed*s.spd+s.ph;
    for(let i=0;i<s.n;i++){
      const o=s.off[i];
      const a=t+i*.53;
      const wob=Math.sin(elapsed*2.4+i*1.7)*.06;
      const x=s.cx+Math.sin(a)*s.rx+o.x*.55+Math.cos(a*.6+si)*.4;
      const z=s.cz+Math.sin(a*.83+o.z)*s.rz+o.z*.55;
      const y=s.y+Math.sin(elapsed*.6+i*.9)*.35+o.y*.3+wob;
      const px=s.cx+Math.sin(a+.05)*s.rx+o.x*.55+Math.cos((a+.05)*.6+si)*.4;
      const pz=s.cz+Math.sin((a+.05)*.83+o.z)*s.rz+o.z*.55;
      dummy.position.set(x,y,z);
      tmpV.set(px-x,0,pz-z);
      if(tmpV.lengthSq()<1e-8) tmpV.set(1,0,0);
      dummy.lookAt(x+tmpV.x,y,z+tmpV.z);
      dummy.rotateY(Math.PI*.5);
      dummy.rotation.z+=Math.sin(elapsed*6+i)*.12;
      const sc=.7+((i%5)*.09);
      dummy.scale.setScalar(sc);
      dummy.updateMatrix();
      s.im.setMatrixAt(i,dummy.matrix);
    }
    s.im.instanceMatrix.needsUpdate=true;
  });

  /* --- bubbles --- */
  for(let i=0;i<BUB_N;i++){
    const b=bub[i];
    b.y+=dt*b.sp*(.5+U.wind.value*.6);
    if(b.y>U.level.value-.06){
      const v=pick(vents);
      b.x=v.x+R(-.5,.5); b.z=v.z+R(-.5,.5); b.y=v.y+R(-.2,.1); b.r=R(.018,.055);
    }
    dummy.position.set(b.x+Math.sin(elapsed*2+b.ph)*.06,b.y,b.z+Math.cos(elapsed*1.7+b.ph)*.06);
    dummy.scale.setScalar(b.r); dummy.rotation.set(0,0,0); dummy.updateMatrix();
    bubbles.setMatrixAt(i,dummy.matrix);
  }
  bubbles.instanceMatrix.needsUpdate=true;
  shafts.children.forEach((c,i)=>{ c.position.y=U.level.value-3.0; c.position.x+=dt*.06*(i%2?1:-1);
    if(c.position.x>7.5)c.position.x=-4; if(c.position.x<-4.5)c.position.x=7; });

  /* --- kayak --- */
  {
    const k=state.kayak;
    const lvl=U.level.value;
    if(k.mode==='launch'||k.mode==='trip'){
      k.t=(k.t+dt*0.0075)%1; k.blend=Math.min(1,k.blend+dt/1.2);
      const p=kayakPath.getPointAt(k.t), tan=kayakPath.getTangentAt(k.t);
      tmpV.set(p.x,0,p.z);
      kayak.position.lerp(tmpV,1-Math.pow(.02,dt));
      kayak.position.y=lvl+waveH(kayak.position.x,kayak.position.z,elapsed,U.wind.value)+.03;
      const want=Math.atan2(tan.x,tan.z);
      let d=want-kayak.rotation.y; while(d>Math.PI)d-=Math.PI*2; while(d<-Math.PI)d+=Math.PI*2;
      kayak.rotation.y+=d*Math.min(1,dt*2.2);
      kayak.rotation.z=Math.sin(elapsed*1.6)*.06+d*.35;
      kayak.rotation.x=Math.sin(elapsed*1.2)*.03;
      kayak.userData.paddle.rotation.y=.5+Math.sin(elapsed*2.4)*.55;
      wakeU.value.set(kayak.position.x,kayak.position.z,1,Math.min(1,k.blend)*.55);
      wakeDir.value.set(tan.x,tan.z);
      if(k.mode==='launch'&&k.blend>=1) k.mode='trip';
    } else if(k.mode==='return'){
      k.blend+=dt/1.6;
      const e=easeIO(Math.min(1,k.blend));
      kayak.position.lerpVectors(kayak.position,kayakDock.pos,1-Math.pow(.05,dt));
      kayak.position.y=lerp(kayak.position.y,lvl+waveH(kayak.position.x,kayak.position.z,elapsed,U.wind.value)-.02,dt*3);
      let d=kayakDock.rot-kayak.rotation.y; while(d>Math.PI)d-=Math.PI*2; while(d<-Math.PI)d+=Math.PI*2;
      kayak.rotation.y+=d*Math.min(1,dt*2.5);
      kayak.rotation.z*=1-Math.min(1,dt*2);
      wakeU.value.w=Math.max(0,wakeU.value.w-dt*.8);
      if(kayak.position.distanceTo(kayakDock.pos)<.15||k.blend>3.2){
        k.mode='dock'; kayak.position.copy(kayakDock.pos);
        kayak.rotation.y=kayakDock.rot; kayak.rotation.z=0;
        $('#bKayak').classList.remove('on');
      }
    } else {
      kayak.position.y=lvl+waveH(kayak.position.x,kayak.position.z,elapsed,U.wind.value)-.02;
      kayak.rotation.z=Math.sin(elapsed*1.1)*.035*(.3+U.wind.value);
      kayak.rotation.x=Math.sin(elapsed*.9)*.02;
      wakeU.value.w=Math.max(0,wakeU.value.w-dt);
    }
    // mooring rope
    const moor=scene.userData.moor;
    if(moor){
      const a=new THREE.Vector3(4.75,lvl+.5,5.35), b=kayak.position.clone().setY(kayak.position.y+.15);
      moor.position.copy(a).lerp(b,.5);
      moor.lookAt(b); moor.rotateX(Math.PI/2);
      moor.scale.z=a.distanceTo(b);
      moor.visible=kayak.position.distanceTo(a)<3.4;
    }
    buoy.position.y=lvl+waveH(buoy.position.x,buoy.position.z,elapsed,U.wind.value)-.02;
    buoy.rotation.z=Math.sin(elapsed*1.3)*.12;
    buoy.rotation.x=Math.sin(elapsed*1.0)*.08;
  }

  /* --- cloth, smoke, fireflies, droplets, gulls, clouds --- */
  towels.forEach((t,i)=>{
    const p=t.geometry.attributes.position;
    for(let k=0;k<p.count;k++){
      const x=p.getX(k), y=p.getY(k);
      p.setZ(k,Math.sin(x*7+elapsed*3+i)*.03*(.5+U.wind.value)*(0.5-y));
    }
    p.needsUpdate=true;
  });
  if(hammock){ hammock.rotation.z=Math.sin(elapsed*.8)*.05*(.4+U.wind.value); hammock.position.y=Math.sin(elapsed*.8+1)*.02; }

  // chimney smoke (world position of the stovepipe)
  const chim=new THREE.Vector3(.75,TER.y+2.1,-1.0).applyMatrix4(new THREE.Matrix4().makeRotationY(Math.PI*.75)).add(new THREE.Vector3(TER.x,TER.z*0,TER.z));
  const chimX=TER.x+Math.cos(Math.PI*.75)*.75+Math.sin(Math.PI*.75)*1.0;
  const chimZ=TER.z+Math.sin(Math.PI*.75)*.75-Math.cos(Math.PI*.75)*1.0;
  const sp=smoke.g.attributes, spd=sp.position.array, ssz=sp.aSize.array, sal=sp.aAlpha.array;
  for(let i=0;i<SMOKE_N;i++){
    const s=smokeD[i]; s.life+=dt;
    if(s.life>s.max){ s.life=0; s.x=chimX+R(-.05,.05); s.y=TER.y+2.55; s.z=chimZ+R(-.05,.05); s.max=R(2.5,4.5); s.s=R(.4,1.0); }
    const u=s.life/s.max;
    s.y+=dt*(.45+u*.4); s.x+=dt*(U.wind.value*.9+.05); s.z+=dt*(U.wind.value*.5);
    spd[i*3]=s.x; spd[i*3+1]=s.y; spd[i*3+2]=s.z;
    ssz[i]=(s.s*(.35+u*1.6))*.02; sal[i]=Math.sin(u*Math.PI)*.16*(1-U.night.value*.4);
  }
  sp.position.needsUpdate=true; sp.aSize.needsUpdate=true; sp.aAlpha.needsUpdate=true;

  // fireflies (night only)
  const fp=ff.g.attributes, fa=fp.aAlpha.array, fpos=fp.position.array, fsz=fp.aSize.array;
  for(let i=0;i<FF_N;i++){
    const f=ffD[i];
    fpos[i*3]=f.x+Math.sin(elapsed*f.sp+f.ph)*.6;
    fpos[i*3+1]=terrainH(f.x,f.z)+.55+Math.sin(elapsed*f.sp*1.7+f.ph*2)*.35;
    fpos[i*3+2]=f.z+Math.cos(elapsed*f.sp*.9+f.ph)*.6;
    fsz[i]=.035;
    fa[i]=Math.max(0,Math.sin(elapsed*2.2+f.ph*3))*.9*U.lamp.value;
  }
  fp.position.needsUpdate=true; fp.aAlpha.needsUpdate=true; fp.aSize.needsUpdate=true;

  // droplets
  const dp=drops.g.attributes, dpos=dp.position.array, dsz=dp.aSize.array, dal=dp.aAlpha.array;
  for(let i=0;i<DROP_N;i++){
    const d=dropD[i];
    if(d.life>0){
      d.life-=dt; d.vy-=9.2*dt;
      d.x+=d.vx*dt; d.y+=d.vy*dt; d.z+=d.vz*dt;
      if(d.y<U.level.value&&d.vy<0){ d.life=0; }
    }
    dpos[i*3]=d.x; dpos[i*3+1]=d.life>0?d.y:-99; dpos[i*3+2]=d.z;
    dsz[i]=.045; dal[i]=d.life>0?Math.min(1,d.life*1.6):0;
  }
  dp.position.needsUpdate=true; dp.aAlpha.needsUpdate=true; dp.aSize.needsUpdate=true;

  // gulls
  gulls.forEach((g,i)=>{
    const u=g.userData;
    if(U.night.value>.5){ g.visible=false; return; } else g.visible=true;
    const a=elapsed*u.sp+u.off;
    g.position.set(ISLAND.x+Math.cos(a)*u.rad,TER.y+u.y+Math.sin(elapsed*.6+i)*.5,ISLAND.z+Math.sin(a)*u.rad);
    g.rotation.y=-a+Math.PI*.5;
    const f=Math.sin(elapsed*5+u.ph);
    u.l.rotation.z=f*.55; u.r.rotation.z=-f*.55;
  });
  // clouds
  clouds.forEach((c,i)=>{ c.position.x+=dt*(.25+U.wind.value*.9); if(c.position.x>75) c.position.x=-75; });

  /* --- lamps & emissives --- */
  const L=U.lamp.value;
  M.glass.emissiveIntensity=L*2.6;
  if(cabin.userData.inner) cabin.userData.inner.material.emissiveIntensity=L*1.9;
  lanterns.forEach(lp=>{ if(lp.userData.bulb) lp.userData.bulb.material.emissiveIntensity=L*3.2; });
  glows.forEach(s=>s.material.opacity=L*s.userData.base*(.85+Math.sin(elapsed*7+s.position.x)*.06));
  sun.castShadow=QUAL[quality].sh;

  renderer.render(scene,camera);
}

/* ============================================================================
   13 · BOOT
   ========================================================================== */
renderer.setPixelRatio(Math.min(devicePixelRatio||1,QUAL.med.dpr));
onResize();
setCam('iso',true);
updateTideReadout(); updateWindReadout();
$('#qSel').value=(devicePixelRatio>2.2||(navigator.hardwareConcurrency||8)<=4)?'low':'med';
applyQuality($('#qSel').value);
setCam('iso',true);
animate();
</script>
</body>
</html>
```

**What's inside**

- **Cutaway lagoon** — the water is a real volume: a wave-displaced surface shader, four glass "aquarium" walls that `discard` above the tide line (front/right at full depth tint, far walls at 22 %), a single continuous seabed+island heightfield (so there is no shore intersection to sort), and depth-keyed transparency. Transparent passes use `depthTest` on / `depthWrite` off with fixed `renderOrder`, so nothing flickers or swaps.
- **One terrain function, two languages** — `terrainH()` exists in JS and in GLSL (trig only, no `sin`-hash, so both agree bit-for-bit). That drives shoreline foam, wet-sand darkening, the tide-flooded beach and the reef shelf that breaches at low tide.
- **Rays** are parametric surfaces solved entirely in the vertex shader — normals rebuilt by finite differences each frame, so the fin undulation shades correctly. The leap is a velocity-tracked parabola with a barrel roll; surface crossings spawn shader-integrated expanding ripples, droplet points and a filtered-noise splash.
- **Living details** — kayak circumnavigates the island with a paddle stroke and a V-wake baked into the foam; chimney smoke, fireflies after dark, gulls by day, swaying hammock, towels fluttering, caustics crawling over the seabed, light shafts drifting down through the cut face.
- **Audio** is entirely synthesised: a four-voice detuned drone, a pentatonic music-box scheduler with feedback delay, band-passed wave lapping, wind that opens with the wind slider, plus splash and hull-creak one-shots.