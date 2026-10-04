

# Low-Poly Hamster Playground

A single-file Three.js diorama: eight chubby rodents, a squeaky wheel, a snack bowl, a cardboard tube, and a clickable cage floor that scatters seeds.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Low-Poly Hamster Playground</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#fff4df; --txt:#16323a; --line:#12303a; --muted:#6d838b;
  --chip:#ffffff; --marigold:#ffb703; --tomato:#ef5d4c; --mint:#3fbfa0;
  --bubble:#ff8fab; --sky:#7fc9ff;
}
body.night{ --paper:#13323d; --txt:#f7ecd7; --line:#061b22; --muted:#9db9c1; --chip:rgba(255,255,255,.09); }
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{
  background:#0b2129; font-family:'Nunito',system-ui,sans-serif; color:var(--txt);
  overflow:hidden; -webkit-font-smoothing:antialiased;
}
canvas#scene{position:fixed;inset:0;width:100%;height:100%;display:block;touch-action:none;cursor:grab}
canvas#scene:active{cursor:grabbing}
.vignette{position:fixed;inset:0;pointer-events:none;z-index:3;
  background:radial-gradient(ellipse at 50% 42%, transparent 42%, rgba(4,18,24,.55) 100%)}
.grain{position:fixed;inset:0;pointer-events:none;z-index:4;opacity:.055;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/></filter><rect width='140' height='140' filter='url(%23n)'/></svg>")}

/* ---------- HUD shell ---------- */
.hud{position:fixed;inset:0;z-index:6;pointer-events:none}
.hud>*{pointer-events:auto}
.reveal{opacity:0;transform:translateY(18px)}
body.ready .reveal{opacity:1;transform:none;
  transition:opacity .8s ease var(--d,0s), transform .8s cubic-bezier(.18,.9,.28,1.1) var(--d,0s)}

/* ---------- brand ---------- */
.brand{position:absolute;left:clamp(14px,2.6vw,40px);top:clamp(12px,2.4vw,30px);max-width:min(52vw,470px);
  color:#fff;text-shadow:0 3px 0 rgba(4,22,28,.35)}
.kicker{display:inline-flex;align-items:center;gap:9px;font:800 11px/1 'Nunito';letter-spacing:.3em;
  text-transform:uppercase;color:var(--marigold)}
.kicker::before{content:"";width:26px;height:3px;background:var(--marigold);border-radius:3px}
.brand h1{font-family:'Baloo 2',cursive;font-weight:800;font-size:clamp(36px,5.4vw,72px);line-height:.84;
  letter-spacing:-.025em;margin:.24em 0 .34em;text-transform:uppercase;color:#fff9ec}
.brand h1 em{font-style:normal;color:var(--marigold);display:inline-block;transition:transform .35s cubic-bezier(.2,1.6,.4,1)}
.brand h1:hover em{transform:rotate(-3deg) scale(1.03)}
.lede{margin:0;max-width:38ch;font-size:15px;font-weight:600;line-height:1.45;color:rgba(255,255,255,.8)}
.lede b{color:var(--marigold)}

/* ---------- panels ---------- */
.panel{background:var(--paper);color:var(--txt);border:2.5px solid var(--line);border-radius:18px;
  box-shadow:5px 6px 0 rgba(4,18,24,.42);transition:background .5s,color .5s}
.panel h2{margin:0 0 9px;font-family:'Baloo 2',cursive;font-size:12px;font-weight:800;letter-spacing:.19em;
  text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:8px}
.panel h2 s{flex:1;height:2px;background:currentColor;opacity:.22;border-radius:2px;text-decoration:none}

/* roster */
.roster{position:absolute;right:clamp(12px,2.2vw,28px);top:clamp(12px,2.4vw,28px);width:min(27vw,262px);padding:13px 12px 9px}
.roster ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
.chip{display:grid;grid-template-columns:16px 1fr auto;gap:9px;align-items:center;width:100%;text-align:left;
  padding:6px 8px;border:2px solid transparent;border-radius:11px;background:none;color:inherit;cursor:pointer;
  font:inherit;transition:transform .16s,background .16s,border-color .16s,box-shadow .16s}
.chip:hover{background:var(--chip);border-color:var(--line);transform:translateX(-4px)}
.chip.on{background:var(--marigold);border-color:var(--line);box-shadow:3px 3px 0 var(--line);transform:translateX(-4px)}
.dot{width:15px;height:15px;border-radius:50%;border:2.5px solid var(--line)}
.nm{font-family:'Baloo 2',cursive;font-weight:700;font-size:14.5px;line-height:1.1}
.st{font-size:10px;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
.chip.on .st{color:#4a3200}

/* stats */
.stats{position:absolute;left:clamp(14px,2.6vw,40px);bottom:clamp(90px,11vw,116px);width:min(31vw,300px);padding:14px 14px 12px}
.mrow{display:grid;grid-template-columns:1fr auto;align-items:baseline;gap:6px;margin-bottom:3px}
.mrow span{font-size:11px;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}
.mrow b{font-family:'Baloo 2',cursive;font-size:26px;font-weight:800;line-height:1}
.meter{height:9px;border-radius:6px;background:rgba(0,0,0,.14);overflow:hidden;margin-bottom:11px}
body.night .meter{background:rgba(255,255,255,.12)}
.meter i{display:block;height:100%;width:0%;border-radius:6px;background:linear-gradient(90deg,var(--mint),var(--marigold));
  transition:width .45s cubic-bezier(.2,.9,.3,1.3)}
.meter.warm i{background:linear-gradient(90deg,var(--tomato),var(--bubble))}
.feed{list-style:none;margin:10px 0 0;padding:0;display:flex;flex-direction:column;gap:5px;
  border-top:2px dashed rgba(0,0,0,.14);padding-top:9px}
body.night .feed{border-top-color:rgba(255,255,255,.14)}
.feed li{font-size:11.5px;font-weight:700;line-height:1.3;padding:5px 8px;border-left:3px solid var(--tomato);
  background:var(--chip);border-radius:0 9px 9px 0;animation:slide .38s cubic-bezier(.2,.9,.3,1.2)}
.feed li:nth-child(2n){border-left-color:var(--mint)}
.feed li:nth-child(3n){border-left-color:var(--marigold)}
@keyframes slide{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}

/* dock */
.dock{position:absolute;left:50%;transform:translateX(-50%);bottom:clamp(12px,2.2vw,24px);
  display:flex;gap:7px;padding:8px 9px;max-width:min(94vw,900px);overflow-x:auto;
  background:var(--paper);border:2.5px solid var(--line);border-radius:999px;box-shadow:5px 6px 0 rgba(4,18,24,.42);
  scrollbar-width:none}
.dock::-webkit-scrollbar{display:none}
.btn{flex:0 0 auto;font-family:'Baloo 2',cursive;font-weight:700;font-size:13px;padding:8px 14px;border-radius:999px;
  border:2px solid var(--line);background:var(--chip);color:var(--txt);box-shadow:0 3px 0 var(--line);cursor:pointer;
  transition:transform .14s,box-shadow .14s,background .25s;white-space:nowrap}
.btn:hover{transform:translateY(-3px);box-shadow:0 6px 0 var(--line);background:var(--marigold);color:#3a2600}
.btn:active{transform:translateY(2px);box-shadow:0 1px 0 var(--line)}
.btn.on{background:var(--mint);color:#04241c}
.hint{position:absolute;right:clamp(12px,2.2vw,28px);bottom:clamp(12px,2.2vw,24px);font-size:11.5px;font-weight:700;
  color:rgba(255,255,255,.72);text-shadow:0 2px 4px rgba(0,0,0,.5);text-align:right;line-height:1.7}
.hint kbd{font:inherit;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);border-radius:6px;padding:1px 6px}

/* tags */
#labels{position:fixed;inset:0;z-index:5;pointer-events:none}
.tag{position:absolute;transform:translate(-50%,-100%);display:flex;flex-direction:column;align-items:center;gap:3px;
  will-change:transform}
.tag .nm2{font-family:'Baloo 2',cursive;font-size:11.5px;font-weight:800;letter-spacing:.04em;padding:3px 9px;
  background:var(--line);color:#fff6e2;border-radius:999px;opacity:0;transform:translateY(6px) scale(.9);
  transition:opacity .22s,transform .22s;white-space:nowrap}
.tag.on .nm2{opacity:1;transform:none}
.tag .pt{width:8px;height:8px;border-radius:50%;border:2px solid rgba(10,26,32,.85);box-shadow:0 1px 3px rgba(0,0,0,.4)}
.pop{position:absolute;transform:translate(-50%,-100%);font-size:19px;animation:float 1.2s ease-out forwards;
  text-shadow:0 2px 6px rgba(0,0,0,.4)}
@keyframes float{from{opacity:0;transform:translate(-50%,-90%) scale(.6)}
  25%{opacity:1;transform:translate(-50%,-140%) scale(1.15)}to{opacity:0;transform:translate(-50%,-215%) scale(1)}}

/* loader */
#loader{position:fixed;inset:0;z-index:60;display:grid;place-content:center;justify-items:center;gap:22px;
  background:radial-gradient(circle at 50% 42%,#1d4b57,#07161c 72%);transition:opacity .7s,visibility .7s}
#loader.hide{opacity:0;visibility:hidden}
.lwheel{width:88px;height:88px;border:6px solid var(--marigold);border-radius:50%;position:relative;
  animation:spin 1s linear infinite;box-shadow:0 0 0 5px rgba(255,183,3,.18)}
.lwheel i{position:absolute;left:50%;top:50%;width:74px;height:5px;margin:-2.5px 0 0 -37px;border-radius:3px;background:#ffd98a}
.lwheel b{position:absolute;left:50%;bottom:9px;width:22px;height:17px;margin-left:-11px;border-radius:50%;background:#fff3dd}
@keyframes spin{to{transform:rotate(360deg)}}
.ltext{font-family:'Baloo 2',cursive;font-weight:700;font-size:14px;letter-spacing:.22em;text-transform:uppercase;color:#ffd98a}
.lsub{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.4);max-width:30ch;text-align:center}

@media (max-width:1080px){ .stats{width:270px} .roster{width:220px} }
@media (max-width:860px){
  .roster{display:none} .stats{display:none}
  .brand{max-width:82vw} .lede{font-size:13px} .hint{display:none}
}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div class="vignette"></div>
<div class="grain"></div>
<div id="labels"></div>

<div class="hud">
  <header class="brand reveal" style="--d:.05s">
    <div class="kicker">Three.js · low-poly diorama</div>
    <h1>Hamster<br><em>Playground</em></h1>
    <p class="lede">Chubby rodents, one squeaky wheel. <b>Drag</b> to orbit, <b>click the bedding</b> to drop a seed, <b>click a hamster</b> to star them.</p>
  </header>

  <section class="panel roster reveal" style="--d:.22s">
    <h2>Cage mates <s></s></h2>
    <ul id="roster"></ul>
  </section>

  <section class="panel stats reveal" style="--d:.32s">
    <h2>Cage log <s></s></h2>
    <div class="mrow"><span>Wheel speed</span><b id="v-rpm">0</b></div>
    <div class="meter"><i id="m-rpm"></i></div>
    <div class="mrow"><span>Snacks in bowl</span><b id="v-seed">0</b></div>
    <div class="meter warm"><i id="m-seed"></i></div>
    <div class="mrow"><span>Zoomie level</span><b id="v-zoom">0%</b></div>
    <div class="meter"><i id="m-zoom"></i></div>
    <ul class="feed" id="feed"></ul>
  </section>

  <nav class="dock reveal" style="--d:.42s">
    <button class="btn" data-act="spin">🌀 Spin wheel</button>
    <button class="btn" data-act="seeds">🌾 Scatter seeds</button>
    <button class="btn" data-act="refill">🥣 Refill bowl</button>
    <button class="btn" data-act="zoomies">⚡ Zoomies</button>
    <button class="btn" data-act="door">🚪 Door</button>
    <button class="btn" data-act="night">🌙 Lights</button>
    <button class="btn" data-act="orbit">🎥 Auto-orbit</button>
    <button class="btn" data-act="add">➕ Hamster</button>
    <button class="btn" data-act="reset">↺ Reset view</button>
  </nav>

  <div class="hint reveal" style="--d:.5s">
    <kbd>drag</kbd> orbit &nbsp; <kbd>scroll</kbd> zoom<br>
    click the ball for a boop
  </div>
</div>

<div id="loader">
  <div class="lwheel"><i></i><i style="transform:rotate(60deg)"></i><i style="transform:rotate(120deg)"></i><i style="transform:rotate(180deg)"></i><b></b></div>
  <div class="ltext">Filling the bedding</div>
  <div class="lsub" id="lsub">warming up the wheel…</div>
</div>

<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
   0 · helpers
============================================================ */
const rand=(a,b)=>a+Math.random()*(b-a);
const pick=a=>a[(Math.random()*a.length)|0];
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
function lerpAngle(a,b,t){let d=((b-a+Math.PI)%(Math.PI*2)+Math.PI*2)%(Math.PI*2)-Math.PI;return a+d*t;}
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const M=(color,o={})=>new THREE.MeshStandardMaterial({color,flatShading:true,roughness:.85,metalness:.04,...o});
const box=(w,h,d,m)=>new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);
const cyl=(rt,rb,h,s,m)=>new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,s),m);
function shadows(o,cast=true,rec=true){o.traverse(n=>{if(n.isMesh){n.castShadow=cast;n.receiveShadow=rec;}});return o;}

/* ============================================================
   1 · renderer / scene / camera
============================================================ */
const canvas=document.getElementById('scene');
let renderer;
try{ renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'}); }
catch(e){ document.getElementById('lsub').textContent='WebGL is not available in this browser.'; throw e; }
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.1;

const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.1,220);
camera.position.set(12.5,9.4,14.5);

const controls=new OrbitControls(camera,canvas);
controls.enableDamping=true; controls.dampingFactor=.075;
controls.target.set(0,2.1,0);
controls.minDistance=6.5; controls.maxDistance=34;
controls.maxPolarAngle=Math.PI*.492; controls.autoRotateSpeed=.55;

/* gradient sky (redrawn during the day/night crossfade) */
const skyCv=document.createElement('canvas'); skyCv.width=8; skyCv.height=256;
const skyCtx=skyCv.getContext('2d');
const skyTex=new THREE.CanvasTexture(skyCv); skyTex.colorSpace=THREE.SRGBColorSpace;
scene.background=skyTex;
function paintSky(top,mid,bot){
  const g=skyCtx.createLinearGradient(0,0,0,256);
  g.addColorStop(0,top); g.addColorStop(.58,mid); g.addColorStop(1,bot);
  skyCtx.fillStyle=g; skyCtx.fillRect(0,0,8,256); skyTex.needsUpdate=true;
}
scene.fog=new THREE.Fog(0xd9eef8,34,90);

/* ============================================================
   2 · lights
============================================================ */
const hemi=new THREE.HemisphereLight(0xbfe8ff,0xd9b48a,.62); scene.add(hemi);
const sun=new THREE.DirectionalLight(0xfff2d2,1.5);
sun.position.set(9,16,7); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-14; sun.shadow.camera.right=14;
sun.shadow.camera.top=14; sun.shadow.camera.bottom=-14;
sun.shadow.camera.near=1; sun.shadow.camera.far=44;
sun.shadow.bias=-.0007; sun.shadow.normalBias=.02;
scene.add(sun);
const fill=new THREE.DirectionalLight(0x9fd4ff,.4); fill.position.set(-10,7,-8); scene.add(fill);
const lamp=new THREE.PointLight(0xffa85c,0,16,2); lamp.position.set(-3.4,3.4,-2.4); scene.add(lamp);

/* ============================================================
   3 · cage + props
============================================================ */
const CAGE={w:13,d:9.4,wallH:4.6,trayH:1.35};
const GY=CAGE.trayH;                       // floor level inside the cage
const BX=CAGE.w/2-.55, BZ=CAGE.d/2-.55;    // movement bounds
const C={tray:0xf0654f,rim:0xffb45c,bed:0xe9cd97,bar:0xd9e4ea,post:0x2fa38c,
  wheel:0x5fd3b4,wheel2:0xffd166,bowl:0xffb703,bowlIn:0xd97f24,
  hut:0xe2789a,roof:0xef5d4c,tube:0xc98a52,ball:0x6fb7ff,plant:0x4fbf7a,pot:0xf0654f};

const world=new THREE.Group(); scene.add(world);

/* table */
const tableMat=M(0xf2d7ae,{flatShading:false,roughness:1});
const table=new THREE.Mesh(new THREE.CircleGeometry(70,44),tableMat);
table.rotation.x=-Math.PI/2; table.receiveShadow=true; world.add(table);
const mat=new THREE.Mesh(new THREE.CircleGeometry(11.5,40),M(0xe7c493,{flatShading:false,roughness:1}));
mat.rotation.x=-Math.PI/2; mat.position.y=.012; mat.receiveShadow=true; world.add(mat);

/* tray + bedding floor */
const tray=shadows(box(CAGE.w+1.25,CAGE.trayH,CAGE.d+1.25,M(C.tray)));
tray.position.y=CAGE.trayH/2; world.add(tray);
const rim=shadows(box(CAGE.w+1.6,.3,CAGE.d+1.6,M(C.rim)));
rim.position.y=CAGE.trayH-.05; world.add(rim);
const floor=new THREE.Mesh(new THREE.BoxGeometry(CAGE.w,.3,CAGE.d),M(C.bed,{flatShading:false,roughness:1}));
floor.position.y=CAGE.trayH-.15; floor.receiveShadow=true; world.add(floor);

/* bedding chips (instanced) */
{
  const N=300, g=new THREE.BoxGeometry(.2,.07,.13);
  const im=new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial({roughness:1}),N);
  const d=new THREE.Object3D(), col=new THREE.Color();
  for(let i=0;i<N;i++){
    d.position.set(rand(-6.3,6.3),GY+.03,rand(-4.5,4.5));
    d.rotation.set(rand(-.2,.2),rand(0,6.28),rand(-.2,.2));
    d.scale.setScalar(rand(.7,1.5)); d.updateMatrix(); im.setMatrixAt(i,d.matrix);
    col.setHex(pick([0xd9b06b,0xf0dcae,0xc99a58,0xf6e6c4])); im.setColorAt(i,col);
  }
  im.receiveShadow=true; world.add(im);
}

/* bars (instanced) */
{
  const pts=[];
  for(let x=-CAGE.w/2+.55;x<=CAGE.w/2-.5;x+=.62){
    pts.push([x,-CAGE.d/2]);
    if(Math.abs(x)>1.55) pts.push([x,CAGE.d/2]);           // door gap
  }
  for(let z=-CAGE.d/2+.55;z<=CAGE.d/2-.5;z+=.62){ pts.push([-CAGE.w/2,z]); pts.push([CAGE.w/2,z]); }
  const g=new THREE.CylinderGeometry(.055,.055,CAGE.wallH,7);
  const im=new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial({color:C.bar,metalness:.8,roughness:.32}),pts.length);
  const d=new THREE.Object3D();
  pts.forEach((p,i)=>{d.position.set(p[0],CAGE.trayH+CAGE.wallH/2,p[1]);d.updateMatrix();im.setMatrixAt(i,d.matrix);});
  im.castShadow=true; world.add(im);

  const tg=new THREE.CylinderGeometry(.045,.045,CAGE.w,6); tg.rotateZ(Math.PI/2);
  const n=Math.floor(CAGE.d/.78)+1;
  const top=new THREE.InstancedMesh(tg,new THREE.MeshStandardMaterial({color:C.bar,metalness:.8,roughness:.32}),n);
  for(let i=0;i<n;i++){ const d0=new THREE.Object3D();
    d0.position.set(0,CAGE.trayH+CAGE.wallH+.05,-CAGE.d/2+.4+i*.78); d0.updateMatrix(); top.setMatrixAt(i,d0.matrix); }
  top.castShadow=true; world.add(top);
}
/* corner posts + frame */
{
  const pm=M(C.post,{roughness:.55});
  for(const sx of[-1,1])for(const sz of[-1,1]){
    const p=shadows(box(.36,CAGE.wallH+.4,.36,pm));
    p.position.set(sx*CAGE.w/2,CAGE.trayH+CAGE.wallH/2,sz*CAGE.d/2); world.add(p);
  }
  const fm=new THREE.MeshStandardMaterial({color:C.bar,metalness:.8,roughness:.3});
  const a=shadows(box(CAGE.w+1.1,.28,.3,fm)); a.position.set(0,CAGE.trayH+CAGE.wallH+.2,-CAGE.d/2-.05); world.add(a);
  const b=a.clone(); b.position.z=CAGE.d/2+.05; world.add(b);
  const c=shadows(box(.3,.28,CAGE.d+1.1,fm)); c.position.set(-CAGE.w/2-.05,CAGE.trayH+CAGE.wallH+.2,0); world.add(c);
  const d=c.clone(); d.position.x=CAGE.w/2+.05; world.add(d);
}
/* door */
const door=new THREE.Group();
door.position.set(-1.5,CAGE.trayH,CAGE.d/2); world.add(door);
{
  const bm=new THREE.MeshStandardMaterial({color:C.bar,metalness:.8,roughness:.3});
  for(let i=0;i<5;i++){ const b=shadows(cyl(.055,.055,CAGE.wallH,7,bm)); b.position.set(.3+i*.36,CAGE.wallH/2,0); door.add(b); }
  const r1=shadows(box(2.05,.16,.16,bm)); r1.position.set(1.02,.12,0); door.add(r1);
  const r2=r1.clone(); r2.position.y=CAGE.wallH-.12; door.add(r2);
  const h=new THREE.Mesh(new THREE.TorusGeometry(.22,.055,6,14),M(C.marigold||0xffb703));
  h.position.set(2.15,CAGE.wallH*.5,.1); door.add(shadows(h));
}
let doorOpen=false, doorAngle=0;

/* water bottle */
{
  const g=new THREE.Group(); g.position.set(CAGE.w/2+.15,CAGE.trayH+2.5,1.7); world.add(g);
  const body=cyl(.34,.34,1.5,14,new THREE.MeshStandardMaterial({color:0xdff3ff,transparent:true,opacity:.5,roughness:.15}));
  body.rotation.z=Math.PI/2; g.add(body);
  const cap=cyl(.2,.2,.24,10,M(C.tomato)); cap.rotation.z=Math.PI/2; cap.position.x=-.85; g.add(cap);
  const sp=cyl(.045,.045,.55,6,new THREE.MeshStandardMaterial({color:0xcfd8dc,metalness:.9,roughness:.25}));
  sp.rotation.z=Math.PI/2; sp.position.x=.95; g.add(sp);
}

/* ---------- exercise wheel ---------- */
const wheel={group:new THREE.Group(),spin:new THREE.Group(),vel:0,occupant:null,pos:new THREE.Vector2(4.4,-2.5)};
wheel.group.position.set(wheel.pos.x,GY,wheel.pos.y); world.add(wheel.group);
{
  const frame=M(0x2fa38c,{roughness:.5}), plas=M(C.wheel,{roughness:.45}), plas2=M(C.wheel2,{roughness:.45});
  const base=shadows(box(2.7,.18,1.9,frame)); base.position.y=.09; wheel.group.add(base);
  const s1=shadows(box(.22,2.1,.55,frame)); s1.position.set(0,1.05,-.85); wheel.group.add(s1);
  const s2=s1.clone(); s2.position.z=.85; wheel.group.add(s2);
  wheel.spin.position.set(0,1.5,0); wheel.group.add(wheel.spin);
  for(const z of[-.44,.44]){
    const disc=cyl(1.36,1.36,.07,26,plas); disc.rotation.x=Math.PI/2; disc.position.z=z;
    wheel.spin.add(shadows(disc));
    const ring=new THREE.Mesh(new THREE.TorusGeometry(1.36,.1,6,26),plas2); ring.position.z=z;
    wheel.spin.add(shadows(ring));
  }
  for(let i=0;i<14;i++){
    const a=i/14*Math.PI*2;
    const rung=shadows(box(.17,.05,.8,plas2));
    rung.position.set(Math.cos(a)*1.28,Math.sin(a)*1.28,0); rung.rotation.z=a; wheel.spin.add(rung);
  }
  for(let i=0;i<5;i++){
    const a=i/5*Math.PI;
    const sp=shadows(box(2.55,.07,.07,plas)); sp.rotation.z=a; sp.position.z=0; wheel.spin.add(sp);
  }
  const hub=cyl(.15,.15,1.05,10,frame); hub.rotation.x=Math.PI/2; wheel.spin.add(shadows(hub));
  const star=new THREE.Mesh(new THREE.ConeGeometry(.2,.4,4),M(C.tomato));
  star.position.set(0,.55,.5); wheel.spin.add(star);
}

/* ---------- food bowl ---------- */
const bowl={group:new THREE.Group(),pos:new THREE.Vector2(-4.5,2.7),seeds:12,max:14,dots:[]};
bowl.group.position.set(bowl.pos.x,GY,bowl.pos.y); world.add(bowl.group);
{
  const b=shadows(cyl(.78,.52,.44,14,M(C.bowl,{roughness:.5}))); b.position.y=.22; bowl.group.add(b);
  const r=new THREE.Mesh(new THREE.TorusGeometry(.76,.09,6,16),M(C.bowl,{roughness:.5}));
  r.rotation.x=Math.PI/2; r.position.y=.42; bowl.group.add(shadows(r));
  const in0=cyl(.62,.62,.06,14,M(C.bowlIn)); in0.position.y=.36; bowl.group.add(in0);
  for(let i=0;i<bowl.max;i++){
    const d=new THREE.Mesh(new THREE.SphereGeometry(.11,5,4),M(0xc98a52,{roughness:.9}));
    const a=i/bowl.max*Math.PI*2, rr=rand(.12,.45);
    d.position.set(Math.cos(a)*rr,.44,Math.sin(a)*rr); d.scale.set(1,.7,1.3); d.rotation.y=rand(0,6.3);
    bowl.group.add(d); bowl.dots.push(d);
  }
}
function syncBowl(){ bowl.dots.forEach((d,i)=>{ d.visible=i<bowl.seeds; d.scale.set(1,.7,1.3); }); }
syncBowl();

/* ---------- hut + nest ---------- */
{
  const hut=new THREE.Group(); hut.position.set(-3.7,GY,-3.0); hut.rotation.y=.25; world.add(hut);
  hut.add(shadows(box(2.5,1.5,2.3,M(C.hut)))).position.y=.75;
  const roof=new THREE.Mesh(new THREE.ConeGeometry(2.05,1.15,4),M(C.roof));
  roof.rotation.y=Math.PI/4; roof.position.y=2.05; hut.add(shadows(roof));
  const dr=box(.8,1.0,.12,M(0x5b3a2e)); dr.position.set(0,.55,1.17); hut.add(dr);
  const nest=new THREE.Mesh(new THREE.TorusGeometry(.85,.3,6,14),M(0xd9b06b));
  nest.rotation.x=-Math.PI/2; nest.position.set(3.3,GY+.12,3.0); world.add(shadows(nest));
  const pad=new THREE.Mesh(new THREE.CircleGeometry(.8,14),M(0xf0dcae));
  pad.rotation.x=-Math.PI/2; pad.position.set(3.3,GY+.06,3.0); world.add(pad);
}
/* ---------- cardboard tunnel ---------- */
const tunnel={center:new THREE.Vector2(.5,3.15),ang:-.35,len:3.5};
{
  const dir=tunnelDir();
  const g=new THREE.Group(); g.position.set(tunnel.center.x,GY+.63,tunnel.center.y);
  g.rotation.y=tunnel.ang; world.add(g);
  const tube=new THREE.Mesh(new THREE.CylinderGeometry(.63,.63,tunnel.len,14,1,true),
    new THREE.MeshStandardMaterial({color:C.tube,side:THREE.FrontSide,roughness:.95,flatShading:true}));
  tube.rotation.z=Math.PI/2; g.add(shadows(tube,false,true));
  for(let i=0;i<6;i++){
    const r=new THREE.Mesh(new THREE.TorusGeometry(.63,.07,5,16),M(0xb87a45));
    r.rotation.y=Math.PI/2; r.position.x=-tunnel.len/2+.25+i*(tunnel.len-0.5)/5; g.add(shadows(r));
  }
}
function tunnelDir(){ return new THREE.Vector2(Math.cos(tunnel.ang),-Math.sin(tunnel.ang)); }
const tA=tunnel.center.clone().sub(tunnelDir().clone().multiplyScalar(tunnel.len/2));
const tB=tunnel.center.clone().add(tunnelDir().clone().multiplyScalar(tunnel.len/2));

/* ---------- toys, plants, pebbles ---------- */
const ball=new THREE.Mesh(new THREE.IcosahedronGeometry(.42,1),M(C.ball,{roughness:.4}));
ball.position.set(-1.2,GY+.42,.6); shadows(ball); world.add(ball);
const ballV=new THREE.Vector2(0,0);
{
  const cols=[0xffb703,0xef5d4c,0x3fbfa0];
  [[0,0],[.05,.62],[-.02,1.24]].forEach((p,i)=>{
    const b=shadows(box(.6,.58,.6,M(cols[i])));
    b.position.set(5.5+p[0],GY+.3+i*.58,2.4); b.rotation.y=rand(-.3,.3); world.add(b);
  });
  for(const p of[[-5.8,-3.6],[5.9,3.7],[-6.0,3.4]]){
    const g=new THREE.Group(); g.position.set(p[0],GY,p[1]); world.add(g);
    const pot=shadows(cyl(.36,.28,.42,10,M(C.pot))); pot.position.y=.21; g.add(pot);
    for(let i=0;i<3;i++){
      const c=new THREE.Mesh(new THREE.ConeGeometry(.46-i*.12,.5,6),M(C.plant));
      c.position.y=.6+i*.34; g.add(shadows(c));
    }
  }
  for(let i=0;i<8;i++){
    const s=new THREE.Mesh(new THREE.IcosahedronGeometry(rand(.12,.2),0),M(0xb9c3c9));
    s.position.set(rand(-6,6),GY+.06,rand(-4.2,4.2)); s.rotation.y=rand(0,6.3); world.add(shadows(s));
  }
  for(let i=0;i<4;i++){
    const st=shadows(box(1.5,.12,.5,M(0xd9a76a)));
    st.position.set(1.6,GY+.16+i*.34,-3.9); st.rotation.y=.12*i; world.add(st);
  }
}
/* dust motes */
const motes=(()=>{
  const N=260, pos=new Float32Array(N*3);
  for(let i=0;i<N;i++){ pos[i*3]=rand(-11,11); pos[i*3+1]=rand(.5,9); pos[i*3+2]=rand(-9,9); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const p=new THREE.Points(g,new THREE.PointsMaterial({color:0xffe6b8,size:.075,transparent:true,opacity:.55,depthWrite:false}));
  scene.add(p); return p;
})();

/* obstacles for steering */
const solids=[
  {x:wheel.pos.x,y:wheel.pos.y,r:1.55},
  {x:-3.7,y:-3.0,r:1.75},
  {x:5.5,y:2.4,r:.95},
  {x:-5.8,y:-3.6,r:.85},{x:5.9,y:3.7,r:.85},{x:-6.0,y:3.4,r:.85},
];

/* ============================================================
   4 · hamsters
============================================================ */
const FURS=[
  {name:'Pip',      fur:0xf6b561, belly:0xffe6c2, cheek:0xffc2cf},
  {name:'Noodle',   fur:0xfdf3e3, belly:0xffffff, cheek:0xffb3c1},
  {name:'Waffles',  fur:0xb9793f, belly:0xf3d9b8, cheek:0xffa8bb},
  {name:'Mochi',    fur:0xfff8ee, belly:0xffffff, cheek:0xffc2cf},
  {name:'Biscuit',  fur:0xe0955a, belly:0xffe2bd, cheek:0xffb3c1},
  {name:'Zuzu',     fur:0x9aa6b8, belly:0xe8eef5, cheek:0xffa8bb},
  {name:'Pickles',  fur:0xd8c07a, belly:0xf7ead0, cheek:0xffb3c1},
  {name:'Dumpling', fur:0xf3a6a0, belly:0xffe4d9, cheek:0xff8fab},
];
const hamsters=[];
function createHamster(cfg){
  const g=new THREE.Group();
  const fur=new THREE.MeshStandardMaterial({color:cfg.fur,flatShading:true,roughness:.95});
  const bel=new THREE.MeshStandardMaterial({color:cfg.belly,flatShading:true,roughness:1});
  const pink=new THREE.MeshStandardMaterial({color:cfg.cheek,flatShading:true,roughness:.75});
  const dark=new THREE.MeshStandardMaterial({color:0x241d2b,roughness:.28,metalness:.25});
  const white=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.2});

  const body=new THREE.Mesh(new THREE.IcosahedronGeometry(.46,1),fur);
  body.scale.set(1.02,.94,1.18); body.position.y=.44; g.add(body);
  const belly=new THREE.Mesh(new THREE.IcosahedronGeometry(.4,1),bel);
  belly.scale.set(.92,.82,1.02); belly.position.set(0,.36,.07); g.add(belly);

  const head=new THREE.Group(); head.position.set(0,.66,.42); g.add(head);
  const skull=new THREE.Mesh(new THREE.IcosahedronGeometry(.3,1),fur); skull.scale.set(1.06,.98,.96); head.add(skull);
  const muz=new THREE.Mesh(new THREE.IcosahedronGeometry(.15,1),bel); muz.scale.set(1,.82,1.2); muz.position.set(0,-.04,.23); head.add(muz);
  const nose=new THREE.Mesh(new THREE.IcosahedronGeometry(.05,0),pink); nose.position.set(0,.0,.39); head.add(nose);

  const eyes=[],cheeks=[],ears=[],legs=[];
  for(const s of[-1,1]){
    const e=new THREE.Group(); e.position.set(.145*s,.075,.235);
    e.add(new THREE.Mesh(new THREE.SphereGeometry(.062,8,6),dark));
    const gl=new THREE.Mesh(new THREE.SphereGeometry(.019,6,4),white); gl.position.set(.022,.024,.05); e.add(gl);
    head.add(e); eyes.push(e);

    const c=new THREE.Mesh(new THREE.IcosahedronGeometry(.13,1),fur);
    c.position.set(.2*s,-.035,.11); head.add(c); cheeks.push(c);

    const ear=new THREE.Group(); ear.position.set(.19*s,.245,.01); ear.rotation.set(0,.5*s,.34*s);
    const disc=new THREE.Mesh(new THREE.CylinderGeometry(.115,.13,.05,8),fur); disc.rotation.z=Math.PI/2; ear.add(disc);
    const inn=new THREE.Mesh(new THREE.CylinderGeometry(.075,.085,.06,8),pink); inn.rotation.z=Math.PI/2; inn.position.x=.012*s; ear.add(inn);
    head.add(ear); ears.push(ear);
  }
  for(const [x,z] of [[.26,.3],[-.26,.3],[.26,-.3],[-.26,-.3]]){
    const l=new THREE.Group(); l.position.set(x,.24,z);
    const m=new THREE.Mesh(new THREE.CylinderGeometry(.075,.09,.22,6),fur); m.position.y=-.11; l.add(m);
    const f=new THREE.Mesh(new THREE.IcosahedronGeometry(.075,0),pink); f.scale.set(1,.6,1.35); f.position.set(0,-.21,.03); l.add(f);
    g.add(l); legs.push(l);
  }
  const tail=new THREE.Mesh(new THREE.IcosahedronGeometry(.07,0),pink);
  tail.position.set(0,.42,-.55); tail.scale.set(1,1,1.5); g.add(tail);

  const ring=new THREE.Mesh(new THREE.TorusGeometry(.62,.05,5,20),
    new THREE.MeshBasicMaterial({color:0xffb703,transparent:true,opacity:.9}));
  ring.rotation.x=-Math.PI/2; ring.position.y=.04; ring.visible=false; g.add(ring);

  shadows(g);
  g.scale.setScalar(.95);
  world.add(g);

  const h={
    name:cfg.name,group:g,body,head,eyes,cheeks,ears,legs,ring,
    pos:new THREE.Vector2(rand(-3,3),rand(-2,2)),heading:rand(0,6.28),
    state:'idle',timer:rand(.5,2),sub:0,phase:0,target:null,seed:null,
    t:rand(0,10),blink:0,blinkT:rand(1,4),twitch:rand(1,4),
    hunger:rand(.1,.5),energy:rand(.55,1),running:false,speed:0,
    baseY:GY,headY:0,
  };
  g.userData.h=h;
  return h;
}

/* seeds on the floor */
const seeds=[];
const seedGeo=new THREE.SphereGeometry(.1,5,4);
const seedMat=M(0xc98a52,{roughness:.9});
function dropSeed(x,z,log){
  if(seeds.length>26) return;
  const m=new THREE.Mesh(seedGeo,seedMat); m.scale.set(1,.7,1.35);
  m.castShadow=true; world.add(m);
  seeds.push({mesh:m,x,z,y:.6,vy:0});
  m.position.set(x,GY+.6,z);
  if(log) addLog(`${pick(['A seed lands','A snack appears','Fresh seed'])} at the ${zoneName(x,z)}.`);
}
function zoneName(x,z){ return (z<0?'north':(z>0?'south':'mid'))+' '+(x<0?'west':'east'); }

/* ============================================================
   5 · behaviour
============================================================ */
function setState(h,s,dur){ h.state=s; h.timer=dur??rand(1,3); h.sub=0; h.target=null; h.seed=null; }
function freeSpot(){
  for(let i=0;i<20;i++){
    const x=rand(-BX,BX), z=rand(-BZ,BZ);
    if(solids.every(o=>Math.hypot(x-o.x,z-o.y)>o.r+.6)) return new THREE.Vector2(x,z);
  }
  return new THREE.Vector2(0,0);
}
function pickNext(h){
  const r=Math.random();
  if(h.energy<.24){ setState(h,'nap',rand(6,10)); h.target=new THREE.Vector2(3.3,3.0); return; }
  if(h.hunger>.66 && (bowl.seeds>0||seeds.length)){ setState(h,'seek',8); return; }
  if(r<.26 && !wheel.occupant){ setState(h,'wheel',rand(6,11)); return; }
  if(r<.40){ setState(h,'tunnel',12); h.target=tA.clone(); h.phase=Math.random()<.5?0:1; return; }
  if(r<.54){ setState(h,'groom',rand(2,3.6)); return; }
  if(r<.66){ setState(h,'turn',rand(.6,1.3)); return; }
  setState(h,'walk',rand(3,6.5)); h.target=freeSpot();
}
function steer(h,tx,tz,dt,speed,turn=6){
  const dx=tx-h.pos.x, dz=tz-h.pos.z, d=Math.hypot(dx,dz);
  h.heading=lerpAngle(h.heading,Math.atan2(dx,dz),1-Math.pow(.0015,dt*turn/6));
  h.pos.x+=Math.sin(h.heading)*speed*dt;
  h.pos.z+=Math.cos(h.heading)*speed*dt;
  h.speed=speed;
  return d;
}
function collide(h){
  h.pos.x=clamp(h.pos.x,-BX,BX); h.pos.z=clamp(h.pos.z,-BZ,BZ);
  for(const o of solids){
    const dx=h.pos.x-o.x, dz=h.pos.z-o.y, d=Math.hypot(dx,dz);
    if(d<o.r && d>1e-4){ h.pos.x=o.x+dx/d*o.r; h.pos.z=o.y+dz/d*o.r; }
  }
}
function think(h,dt){
  h.timer-=dt;
  h.hunger=clamp(h.hunger+dt*.014,0,1);
  if(h.state!=='nap') h.energy=clamp(h.energy-dt*.012,0,1);

  switch(h.state){
    case 'idle':
      h.speed=0;
      if(h.timer<=0) pickNext(h);
      break;
    case 'walk':{
      const sp=(zoomiesT>0?2.5:1.15)*(.85+h.energy*.35);
      const d=steer(h,h.target.x,h.target.y,dt,sp);
      collide(h);
      if(d<.4||h.timer<=0){ if(Math.random()<.4) setState(h,'turn',rand(.4,.9)); else { setState(h,'idle',rand(.8,2.4)); } }
      break;}
    case 'turn':
      h.heading+=dt*4.2; h.speed=0;
      if(h.timer<=0) setState(h,Math.random()<.5?'idle':'walk',Math.random()<.5?rand(.6,1.6):rand(2,5));
      if(h.state==='walk') h.target=freeSpot();
      break;
    case 'groom':
      h.speed=0;
      if(h.timer<=0) pickNext(h);
      break;
    case 'seek':{
      let best=null,bd=1e9;
      for(const s of seeds){ const d=Math.hypot(s.x-h.pos.x,s.z-h.pos.z); if(d<bd){bd=d;best=s;} }
      const bd2=Math.hypot(bowl.pos.x-h.pos.x,bowl.pos.y-h.pos.z);
      if(bowl.seeds>0 && (bd2<bd||!best)){ h.target=bowl.pos.clone(); }
      else if(best){ h.target=new THREE.Vector2(best.x,best.z); h.seed=best; }
      else { pickNext(h); break; }
      const d=steer(h,h.target.x,h.target.y,dt,1.7,7);
      collide(h);
      if(d<.62){
        if(h.seed){ const i=seeds.indexOf(h.seed); if(i>=0){ world.remove(h.seed.mesh); seeds.splice(i,1);} pop(h,'😋'); }
        else pop(h,'🥜');
        setState(h,'eat',1.7);
      } else if(h.timer<=0) pickNext(h);
      break;}
    case 'eat':
      h.speed=0; h.energy=clamp(h.energy+dt*.02,0,1);
      if(h.timer<=0){ h.hunger=clamp(h.hunger-.55,0,1); setState(h,'idle',rand(.5,1.4)); }
      break;
    case 'wheel':{
      if(!h.running){
        const ap=new THREE.Vector2(wheel.pos.x,wheel.pos.y+1.95);
        const d=steer(h,ap.x,ap.y,dt,1.5,7); collide(h);
        if(d<.55){ h.running=true; wheel.occupant=h; h.heading=Math.PI/2; addLog(`${h.name} clambered onto the wheel.`); }
      }else{
        h.pos.x=lerp(h.pos.x,wheel.pos.x,1-Math.pow(.001,dt));
        h.pos.z=lerp(h.pos.z,wheel.pos.y,1-Math.pow(.001,dt));
        h.baseY=GY+.26; h.speed=2.2;
        wheel.vel=Math.min(13,wheel.vel+dt*7);
        if(h.timer<=0){
          h.running=false; wheel.occupant=null;
          h.pos.set(wheel.pos.x,wheel.pos.y+1.75); h.baseY=GY;
          setState(h,'walk',rand(2,4)); h.target=freeSpot();
          addLog(`${h.name} hopped off, slightly dizzy.`);
        }
      }
      break;}
    case 'tunnel':{
      const dir=tunnelDir();
      const A=h.phase===0?tA:tB, B=h.phase===0?tB:tA;
      if(h.sub===0){
        const d=steer(h,A.x,A.y,dt,1.5,7); collide(h);
        if(d<.3){ h.sub=1; addLog(`${h.name} squeezed into the tube.`); }
      }else{
        const p=new THREE.Vector2(h.pos.x-A.x,h.pos.y-A.y);
        const along=p.dot(dir), total=tunnel.len;
        const t=clamp(along/total,0,1);
        const np=A.clone().add(dir.clone().multiplyScalar(clamp(along+dt*2.1,0,total)));
        h.pos.copy(np);
        h.heading=lerpAngle(h.heading,Math.atan2(dir.x,dir.y)*(h.phase===0?1:1),1-Math.pow(.001,dt*8));
        h.speed=2.1;
        if(along>=total){ h.pos.copy(B); setState(h,'walk',rand(2,4)); h.target=freeSpot(); }
      }
      if(h.timer<=0){ setState(h,'walk',rand(2,4)); h.target=freeSpot(); }
      break;}
    case 'nap':{
      const d=steer(h,h.target.x,h.target.y,dt,1.2,6); collide(h);
      if(d<.5){ setState(h,'sleep',rand(6,12)); addLog(`${h.name} flopped into the nest 💤`); }
      if(h.timer<=0) pickNext(h);
      break;}
    case 'sleep':
      h.speed=0; h.energy=clamp(h.energy+dt*.13,0,1);
      if(h.timer<=0||h.energy>.98){ setState(h,'idle',rand(.6,1.6)); addLog(`${h.name} woke up refreshed.`); }
      break;
  }
  if(h.state!=='wheel') h.baseY=lerp(h.baseY,GY,1-Math.pow(.002,dt));
}

/* animation of one hamster */
function animate(h,dt){
  const moving=['walk','seek','nap'].includes(h.state)||(h.state==='tunnel');
  const run=h.running;
  const gait=run?2:(moving?1:0);
  h.legs.forEach((l,i)=>{
    const ph=(i<2?0:Math.PI)+(i%2?Math.PI:0);
    l.rotation.x = run ? h.t*17+ph : Math.sin(h.t*11+ph)*.8*gait;
  });
  const bob = gait? Math.abs(Math.sin(h.t*(run?16:9)))*.05*gait : Math.sin(h.t*2.4)*.012;
  const hop = h.state==='turn'? Math.abs(Math.sin(h.t*13))*.06 : 0;
  h.group.position.set(h.pos.x,h.baseY+bob+hop,h.pos.y);
  h.group.rotation.y=h.heading;

  const sleeping=h.state==='sleep';
  h.body.scale.y=(.94+Math.sin(h.t*2.6)*.022)-(sleeping?.07:0);
  h.body.scale.x=1+(sleeping?.05:0);

  const tHeadY = h.state==='idle'? Math.sin(h.t*.9)*.45 : (h.state==='groom'? Math.sin(h.t*4)*.5 : 0);
  h.head.rotation.y=lerp(h.head.rotation.y,tHeadY,.09);
  let hx=0,hz=0;
  if(h.state==='eat') hx=.35+Math.sin(h.t*10)*.35;
  if(h.state==='groom'){ hx=.3; hz=Math.sin(h.t*13)*.35; }
  if(sleeping){ hx=-.25; hz=.2; }
  h.head.rotation.x=lerp(h.head.rotation.x,hx,.12);
  h.head.rotation.z=lerp(h.head.rotation.z,hz,.12);
  h.head.position.y=lerp(h.head.position.y,sleeping?.52:.66,.1);

  const puff=h.state==='eat'?1.5:1;
  h.cheeks.forEach(c=>{ const s=lerp(c.scale.x,puff,.1); c.scale.setScalar(s); });

  h.twitch-=dt;
  if(h.twitch<=0){ h.twitch=rand(1.2,4); h.ears[(Math.random()<.5)?0:1].rotation.z+=rand(-.5,.5); }
  h.ears.forEach(e=>e.rotation.z=lerp(e.rotation.z,e.rotation.z>0?.34:-.34,.05));

  const closed=sleeping||h.blink>0;
  h.blink-=dt; h.blinkT-=dt;
  if(h.blinkT<=0&&!closed){ h.blink=.13; h.blinkT=rand(1.6,5.2); }
  h.eyes.forEach(e=>e.scale.y=lerp(e.scale.y,closed?.12:1,.4));

  h.ring.visible = (selected===h);
  if(h.ring.visible){ h.ring.rotation.z+=dt*2; h.ring.scale.setScalar(1+Math.sin(h.t*5)*.06); }
}

/* ============================================================
   6 · UI: roster, feed, tags, HUD
============================================================ */
const rosterEl=document.getElementById('roster');
const feedEl=document.getElementById('feed');
const labelsEl=document.getElementById('labels');
let selected=null, hovered=null, zoomiesT=0;

function hex(c){ return '#'+c.toString(16).padStart(6,'0'); }
function buildRoster(){
  rosterEl.innerHTML='';
  hamsters.forEach((h,i)=>{
    const li=document.createElement('li');
    const b=document.createElement('button');
    b.className='chip'; b.dataset.i=i;
    b.innerHTML=`<span class="dot" style="background:${hex(h.group.children[0].material.color.getHex())}"></span>
      <span class="nm">${h.name}</span><span class="st" data-st="${i}">idle</span>`;
    b.addEventListener('click',()=>focusHamster(h));
    li.appendChild(b); rosterEl.appendChild(li);

    const tag=document.createElement('div');
    tag.className='tag';
    tag.innerHTML=`<span class="nm2">${h.name}</span><span class="pt" style="background:${hex(FURS[i%FURS.length].fur)}"></span>`;
    labelsEl.appendChild(tag); h.tag=tag;
  });
}
function focusHamster(h){
  if(selected===h){ selected=null; addLog(`${h.name} returns to civilian life.`); }
  else{ selected=h; addLog(`${h.name} is now the main character ⭐`); }
  [...rosterEl.children].forEach((li,i)=>li.firstChild.classList.toggle('on',hamsters[i]===selected));
}
const STATE_TXT={idle:'looking around',walk:'exploring',turn:'spinning',seek:'snack chase',eat:'stuffing cheeks',
  wheel:'on the wheel',tunnel:'in the tube',nap:'heading to bed',sleep:'napping 💤',groom:'washing up'};
function addLog(t){
  const li=document.createElement('li'); li.textContent=t;
  feedEl.prepend(li);
  while(feedEl.children.length>5) feedEl.lastChild.remove();
}
function pop(h,txt){
  const d=document.createElement('div'); d.className='pop'; d.textContent=txt;
  d.dataset.x=h.pos.x; d.dataset.z=h.pos.y; d.dataset.dead='0';
  d.style.left='-9999px'; labelsEl.appendChild(d);
  setTimeout(()=>d.remove(),1250);
}
const v3=new THREE.Vector3();
function updateTags(){
  const w=innerWidth,ht=innerHeight;
  hamsters.forEach(h=>{
    h.head.getWorldPosition(v3); v3.y+=.42; v3.project(camera);
    const x=(v3.x*.5+.5)*w, y=(-v3.y*.5+.5)*ht;
    const vis=v3.z<1;
    h.tag.style.display=vis?'flex':'none';
    h.tag.style.transform=`translate(${x}px,${y}px) translate(-50%,-100%)`;
    h.tag.classList.toggle('on',h===selected||h===hovered||h.state==='sleep');
    if(h.state==='sleep'&&Math.random()<.012) pop(h,'💤');
  });
  labelsEl.querySelectorAll('.pop').forEach(d=>{
    v3.set(+d.dataset.x,GY+1.1,+d.dataset.z).project(camera);
    d.style.left=((v3.x*.5+.5)*w)+'px'; d.style.top=((-v3.y*.5+.5)*ht)+'px';
  });
}
let hudT=0;
function updateHUD(dt){
  hudT-=dt; if(hudT>0) return; hudT=.2;
  const rpm=Math.round(wheel.vel/(Math.PI*2)*60);
  document.getElementById('v-rpm').textContent=rpm;
  document.getElementById('m-rpm').style.width=clamp(rpm/120*100,0,100)+'%';
  document.getElementById('v-seed').textContent=bowl.seeds;
  document.getElementById('m-seed').style.width=(bowl.seeds/bowl.max*100)+'%';
  let act=0; hamsters.forEach(h=>act+=h.speed);
  const z=clamp(Math.round(act/Math.max(1,hamsters.length)/2.6*100),0,100);
  document.getElementById('v-zoom').textContent=z+'%';
  document.getElementById('m-zoom').style.width=z+'%';
  rosterEl.querySelectorAll('[data-st]').forEach((el,i)=>{
    const h=hamsters[i]; if(h) el.textContent=STATE_TXT[h.state]||h.state;
  });
}

/* ============================================================
   7 · interaction
============================================================ */
const ray=new THREE.Raycaster(), ndc=new THREE.Vector2();
const groundPlane=new THREE.Plane(new THREE.Vector3(0,1,0),-GY);
const pickables=[wheel.group,bowl.group,ball,door];
function pickAt(cx,cy){
  ndc.set((cx/innerWidth)*2-1,-(cy/innerHeight)*2+1);
  ray.setFromCamera(ndc,camera);
  let hits=ray.intersectObjects(hamsters.map(h=>h.group),true);
  if(hits.length){ let o=hits[0].object; while(o&&!o.userData.h)o=o.parent; if(o) return {t:'hamster',h:o.userData.h}; }
  hits=ray.intersectObjects(pickables,true);
  if(hits.length){
    let o=hits[0].object;
    while(o){ if(o===wheel.group) return {t:'wheel'}; if(o===bowl.group) return {t:'bowl'};
      if(o===ball) return {t:'ball'}; if(o===door) return {t:'door'}; o=o.parent; }
  }
  const p=new THREE.Vector3();
  if(ray.ray.intersectPlane(groundPlane,p)&&Math.abs(p.x)<CAGE.w/2&&Math.abs(p.z)<CAGE.d/2) return {t:'ground',p};
  return null;
}
let down=null;
canvas.addEventListener('pointerdown',e=>{down={x:e.clientX,y:e.clientY};});
canvas.addEventListener('pointerup',e=>{
  if(!down) return; const moved=Math.hypot(e.clientX-down.x,e.clientY-down.y); down=null;
  if(moved>7) return;
  const r=pickAt(e.clientX,e.clientY); if(!r) return;
  if(r.t==='hamster'){ focusHamster(r.h); pop(r.h,'✨'); }
  else if(r.t==='wheel'){ wheel.vel=Math.min(14,wheel.vel+7); addLog('You gave the wheel a big spin.'); }
  else if(r.t==='bowl'){ bowl.seeds=Math.min(bowl.max,bowl.seeds+1); syncBowl(); addLog('One seed, dropped in the bowl.'); }
  else if(r.t==='ball'){
    const dir=new THREE.Vector3(r.p?0:0,0,0);
    ballV.set(rand(-4,4),rand(-4,4)); addLog('Boop! The ball goes rolling.');
    pop(hamsters[0],'🎾');
  }
  else if(r.t==='door'){ toggleDoor(); }
  else if(r.t==='ground'){ dropSeed(r.p.x,r.p.z,true); }
});
let mvT=0;
canvas.addEventListener('pointermove',e=>{
  const now=performance.now(); if(now-mvT<70) return; mvT=now;
  const r=pickAt(e.clientX,e.clientY);
  hovered = r&&r.t==='hamster' ? r.h : null;
  canvas.style.cursor = hovered ? 'pointer' : (r&&['wheel','bowl','ball','ground','door'].includes(r.t)?'pointer':'grab');
});

function toggleDoor(){
  doorOpen=!doorOpen;
  document.querySelector('[data-act="door"]').classList.toggle('on',doorOpen);
  addLog(doorOpen?'The little door creaks open.':'Door shut. Secrets sealed in.');
}
const CAM0=new THREE.Vector3(12.5,9.4,14.5), T0=new THREE.Vector3(0,2.1,0);
let tween=null;
function flyTo(p,t,dur=.9){ tween={p0:camera.position.clone(),t0:controls.target.clone(),p1:p,t1:t,t:0,dur}; }

/* day / night */
let night=false, nightK=0;
const DAY={top:'#8ed6ff',mid:'#cfeaf6',bot:'#ffe7c2',hemiS:0xbfe8ff,hemiG:0xd9b48a,hemi:.62,
  sunC:0xfff2d2,sun:1.5,fill:.4,exp:1.1,fog:0xd9eef8,table:0xf2d7ae,lamp:0};
const NGT={top:'#08152a',mid:'#17304a',bot:'#43304c',hemiS:0x35527a,hemiG:0x2a2330,hemi:.24,
  sunC:0x9fb8ff,sun:.3,fill:.16,exp:1.0,fog:0x1b2c44,table:0x3d4658,lamp:2.1};
const cA=new THREE.Color(),cB=new THREE.Color();
function applyNight(k){
  paintSky(k<.5?DAY.top:NGT.top, k<.5?DAY.mid:NGT.mid, k<.5?DAY.bot:NGT.bot);
  if(k>0&&k<1) paintSky(lerpC(DAY.top,NGT.top,k),lerpC(DAY.mid,NGT.mid,k),lerpC(DAY.bot,NGT.bot,k));
  hemi.intensity=lerp(DAY.hemi,NGT.hemi,k);
  hemi.color.set(lerpC(DAY.hemiS,NGT.hemiS,k)); hemi.groundColor.set(lerpC(DAY.hemiG,NGT.hemiG,k));
  sun.intensity=lerp(DAY.sun,NGT.sun,k); sun.color.set(lerpC(DAY.sunC,NGT.sunC,k));
  fill.intensity=lerp(DAY.fill,NGT.fill,k);
  lamp.intensity=lerp(DAY.lamp,NGT.lamp,k);
  renderer.toneMappingExposure=lerp(DAY.exp,NGT.exp,k);
  scene.fog.color.set(lerpC(DAY.fog,NGT.fog,k));
  tableMat.color.set(lerpC(DAY.table,NGT.table,k));
}
function lerpC(a,b,k){ cA.setHex(a); cB.setHex(b); return cA.lerp(cB,k).getHex(); }

/* buttons */
document.querySelector('.dock').addEventListener('click',e=>{
  const b=e.target.closest('.btn'); if(!b) return;
  const a=b.dataset.act;
  if(a==='spin'){ wheel.vel=Math.min(14,wheel.vel+8); addLog('Wheeee! The wheel is a blur.'); }
  if(a==='seeds'){ for(let i=0;i<7;i++) dropSeed(rand(-5.5,5.5),rand(-3.8,3.8)); addLog('You scattered seeds everywhere. Chaos.'); }
  if(a==='refill'){ bowl.seeds=bowl.max; syncBowl(); addLog('Bowl refilled to the brim 🥣'); }
  if(a==='zoomies'){ zoomiesT=7; hamsters.forEach(h=>{ if(h.state!=='wheel'){ setState(h,'walk',rand(3,6)); h.target=freeSpot(); } });
    addLog('ZOOMIES! Everyone is suddenly very busy. ⚡'); }
  if(a==='door'){ toggleDoor(); }
  if(a==='night'){ night=!night; b.classList.toggle('on',night); document.body.classList.toggle('night',night);
    addLog(night?'Lights out. The wheel keeps turning.':'Sunshine! The cage glows warm.'); }
  if(a==='orbit'){ controls.autoRotate=!controls.autoRotate; b.classList.toggle('on',controls.autoRotate); }
  if(a==='add'){
    if(hamsters.length>=8){ addLog('The cage is officially full of hamsters.'); return; }
    const cfg=FURS[hamsters.length%FURS.length];
    const h=createHamster({...cfg,name:cfg.name+(hamsters.length>=FURS.length?' Jr':'')});
    h.pos.set(rand(-2,2),rand(-1,1));
    buildRoster(); addLog(`${h.name} has moved in! 👋`);
  }
  if(a==='reset'){ selected=null; buildRosterRefresh(); flyTo(CAM0.clone(),T0.clone(),.9); addLog('Camera back to the good angle.'); }
});
function buildRosterRefresh(){ [...rosterEl.children].forEach(li=>li.firstChild.classList.remove('on')); }

/* ============================================================
   8 · loop
============================================================ */
let last=performance.now(), started=false;
function frame(now){
  const dt=Math.min(.05,(now-last)/1000); last=now;
  const t=now/1000;

  /* day-night transition */
  const target=night?1:0;
  if(Math.abs(nightK-target)>.001){ nightK=lerp(nightK,target,1-Math.pow(.06,dt)); applyNight(nightK); }

  /* hamsters */
  if(zoomiesT>0) zoomiesT-=dt;
  for(const h of hamsters){ h.t+=dt; think(h,dt); animate(h,dt); }

  /* wheel physics */
  if(!wheel.occupant) wheel.vel*=Math.pow(.35,dt);
  wheel.vel=clamp(wheel.vel,0,14);
  wheel.spin.rotation.z+=wheel.vel*dt;

  /* ball */
  if(ballV.lengthSq()>1e-4){
    ball.position.x+=ballV.x*dt; ball.position.z+=ballV.y*dt;
    ballV.multiplyScalar(Math.pow(.35,dt));
    const r=.42;
    if(Math.abs(ball.position.x)>BX-r){ ballV.x*=-.8; ball.position.x=Math.sign(ball.position.x)*(BX-r); }
    if(Math.abs(ball.position.z)>BZ-r){ ballV.y*=-.8; ball.position.z=Math.sign(ball.position.z)*(BZ-r); }
    ball.rotation.z-=ballV.x*dt*2.2; ball.rotation.x+=ballV.y*dt*2.2;
  }

  /* seeds falling */
  for(const s of seeds){
    if(s.y>.05){ s.vy-=14*dt; s.y=Math.max(.05,s.y+s.vy*dt); s.mesh.rotation.x+=dt*7; }
    s.mesh.position.y=GY+s.y;
  }

  /* door */
  doorAngle=lerp(doorAngle,doorOpen?-2.0:0,1-Math.pow(.008,dt));
  door.rotation.y=doorAngle;

  /* motes */
  {
    const p=motes.geometry.attributes.position;
    for(let i=0;i<p.count;i++){
      let y=p.getY(i)+dt*.16; if(y>9.5) y=.4;
      p.setY(i,y); p.setX(i,p.getX(i)+Math.sin(t*.4+i)*dt*.05);
    }
    p.needsUpdate=true;
  }

  /* camera */
  if(tween){
    tween.t+=dt; const k=ease(clamp(tween.t/tween.dur,0,1));
    camera.position.lerpVectors(tween.p0,tween.p1,k);
    controls.target.lerpVectors(tween.t0,tween.t1,k);
    if(k>=1) tween=null;
  } else if(selected){
    selected.head.getWorldPosition(v3);
    controls.target.lerp(v3,1-Math.pow(.02,dt));
  }
  controls.update();
  updateTags(); updateHUD(dt);
  renderer.render(scene,camera);

  if(!started){ started=true; setTimeout(()=>{
      document.getElementById('loader').classList.add('hide');
      document.body.classList.add('ready');
      addLog('Cage is open for business. 🐹');
      addLog('Click the bedding to drop a seed.');
    },520); }
  requestAnimationFrame(frame);
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
document.addEventListener('visibilitychange',()=>{ if(!document.hidden) last=performance.now(); });

/* boot */
applyNight(0);
for(let i=0;i<5;i++) hamsters.push(createHamster(FURS[i]));
buildRoster();
dropSeed(1.2,1.0); dropSeed(-2.4,-1.2);
requestAnimationFrame(frame);

/* graceful failure notice */
setTimeout(()=>{ if(!started) document.getElementById('lsub').textContent='Still loading Three.js — check your connection.'; },7000);
</script>
</body>
</html>
```

**What's in the box**

- **The cage**: injection-molded tray with a marigold rim, 70+ instanced steel bars, mint corner posts, a hinged front door (click it, or use the button), and a hanging water bottle.
- **Five hamsters, up to eight**: each is a flat-shaded icosahedron blob with a head, muzzle, puffed cheeks, disc ears, four swinging legs, and a nub tail. They blink, their ears twitch, they breathe.
- **Autonomy**: a weighted state machine — wander, pivot-spin, groom, snack-chase, eat (cheeks puff), tube-run, wheel-sprint, and nest-nap driven by hunger and energy meters that tick in real time.
- **Interactive objects**: the exercise wheel has real spin inertia (an occupant accelerates it, friction bleeds it off, RPM is metered live); the bowl holds visible seeds that deplete as they're eaten; click the bedding to drop a seed and watch the nearest hungry hamster peel off to get it; the ball boops and bounces off the walls.
- **Extras**: cardboard tunnel that genuinely occludes a hamster mid-transit, day↔night lighting crossfade (sky gradient, sun, lamp, fog, tone mapping all interpolate), dust motes, floating name tags and emoji pops, a live cage log, and a roster you can click to make any hamster the camera's main character.