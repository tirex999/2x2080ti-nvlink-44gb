

Here's the complete single-file project — save it as `index.html` and open it in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Low-Poly Hamster Playground</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🐹</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@700;800;900&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;overflow:hidden}
  body{
    font-family:Nunito,system-ui,sans-serif;
    user-select:none;-webkit-user-select:none;
    background:
      radial-gradient(1100px 520px at 50% 115%, rgba(255,140,66,.28), transparent 62%),
      radial-gradient(820px 420px at 88% -8%, rgba(127,216,190,.30), transparent 60%),
      radial-gradient(700px 400px at 6% -6%, rgba(255,143,171,.22), transparent 60%),
      linear-gradient(180deg,#fff8ec 0%,#ffe9d4 52%,#ffdcc6 100%);
  }
  body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
    background-image:radial-gradient(rgba(255,255,255,.6) 1.4px,transparent 1.5px);
    background-size:30px 30px;opacity:.45;}
  body::after{content:"";position:fixed;inset:0;z-index:2;pointer-events:none;
    background:radial-gradient(120% 90% at 50% 45%, transparent 62%, rgba(122,63,24,.14) 100%);}
  #scene{position:fixed;inset:0;z-index:1;display:block;cursor:grab;touch-action:none;animation:fadeIn .8s ease both}
  #scene.dragging{cursor:grabbing}
  @keyframes fadeIn{from{opacity:0}}

  #plate{position:fixed;top:16px;left:16px;z-index:10;background:#fffaf2;border:3px solid #2b2b33;
    border-radius:16px;padding:12px 18px 14px;transform:rotate(-2deg);
    box-shadow:7px 7px 0 rgba(43,43,51,.16);animation:drop .6s cubic-bezier(.2,1.6,.4,1) both}
  #plate .kicker{font-weight:900;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:#ff8c42;margin-bottom:2px}
  #plate h1{font-family:Fredoka;font-weight:700;font-size:clamp(26px,3.6vw,40px);line-height:.95;color:#2b2b33}
  #plate h1 em{font-style:normal;color:#ff8c42}
  #plate .sub{font-size:12px;font-weight:800;color:#9a8b7c;margin-top:5px}
  @keyframes drop{from{transform:rotate(-2deg) translateY(-46px);opacity:0}}

  #hints{position:fixed;top:16px;right:16px;z-index:10;display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;max-width:46vw}
  .chip{background:rgba(255,250,242,.92);border:2px solid #2b2b33;border-radius:999px;padding:6px 12px;
    font-size:12px;font-weight:800;color:#2b2b33;box-shadow:3px 3px 0 rgba(43,43,51,.14)}

  #ticker{position:fixed;left:16px;bottom:16px;z-index:10;display:flex;align-items:center;gap:9px;
    background:rgba(255,250,242,.94);border:2.5px solid #2b2b33;border-radius:999px;padding:9px 16px;
    font-size:13.5px;font-weight:800;color:#2b2b33;box-shadow:4px 4px 0 rgba(43,43,51,.15);max-width:min(70vw,430px)}
  #ticker .dot{width:9px;height:9px;border-radius:50%;background:#ff5d5d;flex:none;animation:pulse 1.2s infinite}
  #ticker.tick #tickTxt{animation:tickin .35s ease}
  @keyframes pulse{50%{transform:scale(1.5);opacity:.5}}
  @keyframes tickin{from{opacity:0;transform:translateY(6px)}}

  #ctrls{position:fixed;right:16px;bottom:16px;z-index:10;display:flex;gap:10px}
  #ctrls button{width:48px;height:48px;border-radius:50%;border:3px solid #2b2b33;background:#fffaf2;
    font-size:20px;cursor:pointer;box-shadow:4px 4px 0 rgba(43,43,51,.16);transition:transform .12s,box-shadow .12s}
  #ctrls button:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 rgba(43,43,51,.18)}
  #ctrls button:active{transform:translate(1px,1px);box-shadow:2px 2px 0 rgba(43,43,51,.16)}

  .float{position:fixed;z-index:20;font-size:26px;pointer-events:none;transform:translate(-50%,-50%);
    animation:floatUp .95s ease-out forwards}
  @keyframes floatUp{to{transform:translate(-50%,-50%) translateY(-80px) scale(1.5) rotate(8deg);opacity:0}}

  #fallback{display:none;position:fixed;inset:0;z-index:30;place-items:center;background:rgba(255,248,236,.96);
    text-align:center;padding:24px;font-weight:800;color:#2b2b33;font-size:16px;line-height:1.6}

  @media(max-width:640px){#hints{display:none}#plate{padding:10px 14px}#plate .sub{display:none}}
</style>
</head>
<body>
<canvas id="scene"></canvas>

<div id="fallback">🐹 Your browser couldn't start WebGL.<br/>Try a recent Chrome, Firefox, Edge or Safari.</div>

<header id="plate">
  <div class="kicker">🐹 low-poly</div>
  <h1>Hamster<br><em>Playground</em></h1>
  <p class="sub">4 tiny chefs · 1 very serious wheel</p>
</header>

<div id="hints">
  <span class="chip">🖱️ drag — orbit</span>
  <span class="chip">🔍 scroll — zoom</span>
  <span class="chip">👆 click things — chaos</span>
</div>

<div id="ticker"><span class="dot"></span><span id="tickTxt">Welcome to the cage! 🐹</span></div>

<div id="ctrls">
  <button id="ctrlSnd" title="toggle sound">🔊</button>
  <button id="ctrlRst" title="reset view">⟲</button>
</div>

<script type="importmap">
{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js" } }
</script>
<script type="module">
import * as THREE from 'three';

/* ============================== SETUP ============================== */
const canvas = document.getElementById('scene');
let renderer;
try{
  renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
}catch(e){
  document.getElementById('fallback').style.display='grid';
  throw e;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;

const scene  = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, .1, 100);

scene.add(new THREE.HemisphereLight(0xfff3e0, 0xffd9c2, .95));
const sun = new THREE.DirectionalLight(0xffffff, 1.7);
sun.position.set(7,12,5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
Object.assign(sun.shadow.camera,{left:-8,right:8,top:8,bottom:-8,near:2,far:30});
sun.shadow.bias = -0.0004;
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight(0xcfe8ff, .45);
fill.position.set(-6,6,-7);
scene.add(fill);

/* ============================ HELPERS ============================== */
const V = (x,y,z)=>new THREE.Vector3(x,y,z);
const rand  = (a,b)=>a+Math.random()*(b-a);
const pick  = a=>a[Math.floor(Math.random()*a.length)];
const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
function lerpAngle(a,b,t){const d=((b-a+Math.PI*3)%(Math.PI*2))-Math.PI;return a+d*t;}
function mat(c,o={}){return new THREE.MeshStandardMaterial(Object.assign({color:c,flatShading:true,roughness:.92,metalness:0},o));}
function mesh(g,m,x=0,y=0,z=0,cast=true,recv=false){
  const o=new THREE.Mesh(g,m); o.position.set(x,y,z); o.castShadow=cast; o.receiveShadow=recv; return o;
}
function roundRect(x,a,b,w,h,r){x.beginPath();x.moveTo(a+r,b);x.arcTo(a+w,b,a+w,b+h,r);x.arcTo(a+w,b+h,a,b+h,r);x.arcTo(a,b+h,a,b,r);x.arcTo(a,b,a+w,b,r);x.closePath();}

/* ============================= WORLD =============================== */
const FLOOR_Y = 1.0;

// table
scene.add(mesh(new THREE.CylinderGeometry(7.3,7.3,.3,28),  mat(0xe2ab6d), 0,-.15,0,false,true));
scene.add(mesh(new THREE.CylinderGeometry(7.0,7.35,.5,28), mat(0xc98f52), 0,-.55,0,false,true));

// cage base + bedding
const cage = new THREE.Group(); scene.add(cage);
cage.add(mesh(new THREE.CylinderGeometry(4.7,5.0,1.0,20),  mat(0x5cb8e8), 0,.5,0,true,true));
cage.add(mesh(new THREE.CylinderGeometry(4.78,4.78,.16,20),mat(0x4aa3d8), 0,.92,0));
cage.add(mesh(new THREE.CylinderGeometry(4.55,4.55,.24,20),mat(0xf0c184), 0,.88,0,false,true));
const flakeCols=[0xe6b06c,0xd9a05a,0xf5d09a,0xcf9a52];
for(let i=0;i<26;i++){
  const f=mesh(new THREE.BoxGeometry(rand(.12,.22),.03,rand(.07,.13)),mat(pick(flakeCols)),0,1.01,0,false,true);
  const a=rand(0,6.28), r=Math.sqrt(Math.random())*4.2;
  f.position.x=Math.cos(a)*r; f.position.z=Math.sin(a)*r; f.rotation.y=rand(0,6.28);
  cage.add(f);
}
// wire fence
const wireMat=mat(0xf6f9fc,{roughness:.35,metalness:.35});
for(let i=0;i<16;i++){
  const a=i/16*Math.PI*2;
  cage.add(mesh(new THREE.CylinderGeometry(.045,.045,3.4,5),wireMat,Math.cos(a)*4.72,2.7,Math.sin(a)*4.72));
}
[1.9,3.0,4.1].forEach(y=>{
  const ring=mesh(new THREE.TorusGeometry(4.72,.045,5,28),wireMat,0,y,0);
  ring.rotation.x=Math.PI/2; cage.add(ring);
});
const rim=mesh(new THREE.TorusGeometry(4.72,.08,6,28),wireMat,0,4.4,0);
rim.rotation.x=Math.PI/2; cage.add(rim);

// "home sweet cage" plaque
const labelCv=document.createElement('canvas'); labelCv.width=512; labelCv.height=128;
const labelTex=new THREE.CanvasTexture(labelCv); labelTex.colorSpace=THREE.SRGBColorSpace;
function drawLabel(){
  const x=labelCv.getContext('2d'); x.clearRect(0,0,512,128);
  x.fillStyle='#ff8c42'; roundRect(x,8,8,496,112,56); x.fill();
  x.fillStyle='#fff'; x.font='600 54px Fredoka, Nunito, sans-serif';
  x.textAlign='center'; x.textBaseline='middle'; x.fillText('🐹 HOME SWEET CAGE',256,68);
  labelTex.needsUpdate=true;
}
drawLabel();
const plaque=mesh(new THREE.PlaneGeometry(2.4,.6),new THREE.MeshBasicMaterial({map:labelTex,transparent:true}),0,.52,4.99,false,false);
scene.add(plaque);

/* ====================== INTERACTIVE OBJECTS ======================== */
// --- wheel ---
const WHEEL_POS=V(3.1,FLOOR_Y,0);
const wheelG=new THREE.Group(); wheelG.position.copy(WHEEL_POS); scene.add(wheelG);
const wStand=mat(0xff8c42);
wheelG.add(mesh(new THREE.BoxGeometry(1.5,.12,1.3),wStand,0,.06,0));
wheelG.add(mesh(new THREE.BoxGeometry(.14,1.1,.14),wStand,0,.55,.5));
wheelG.add(mesh(new THREE.BoxGeometry(.14,1.1,.14),wStand,0,.55,-.5));
wheelG.add(mesh(new THREE.CylinderGeometry(.05,.05,1.15,8).rotateX(Math.PI/2),mat(0xcfd8e3,{metalness:.5,roughness:.4}),0,1.1,0));
const wheelDisc=new THREE.Group(); wheelDisc.position.y=1.1; wheelG.add(wheelDisc);
wheelDisc.add(mesh(new THREE.TorusGeometry(1.05,.09,6,22),mat(0x7fd8be)));
for(let i=0;i<6;i++){
  const s=mesh(new THREE.BoxGeometry(.06,1.78,.06),mat(0xfff6ea));
  s.rotation.z=i*Math.PI/6; wheelDisc.add(s);
}
wheelDisc.add(mesh(new THREE.CylinderGeometry(.15,.15,.18,8).rotateX(Math.PI/2),mat(0xffd166)));
wheelG.userData.tag='wheel';

// --- food bowl ---
const BOWL_POS=V(-2.5,FLOOR_Y,2.05);
const bowlG=new THREE.Group(); bowlG.position.copy(BOWL_POS); scene.add(bowlG);
bowlG.add(mesh(new THREE.CylinderGeometry(.55,.42,.24,12),mat(0xff8fab),0,.12,0));
bowlG.add(mesh(new THREE.CylinderGeometry(.42,.42,.05,12),mat(0xd1608a),0,.21,0,false,true));
bowlG.userData.tag='bowl';
const FOOD_APPROACH=BOWL_POS.clone().add(V(BOWL_POS.x,0,BOWL_POS.z).normalize().negate().multiplyScalar(.95));

// --- tunnel ---
const TUN_A=V(-2.3,FLOOR_Y,-2.4), TUN_B=V(0.7,FLOOR_Y,-2.4);
const tunG=new THREE.Group(); tunG.position.set(-0.8,FLOOR_Y+0.12,-2.4); scene.add(tunG);
const tunGeo=new THREE.CylinderGeometry(.62,.62,3.0,10,1,true,0,Math.PI);
tunGeo.rotateZ(-Math.PI/2); tunGeo.rotateX(-Math.PI/2);
tunG.add(mesh(tunGeo,mat(0xffd166,{side:THREE.DoubleSide})));
tunG.add(mesh(new THREE.BoxGeometry(.16,.12,.5),mat(0xe8b23e),-1.4,0,0));
tunG.add(mesh(new THREE.BoxGeometry(.16,.12,.5),mat(0xe8b23e), 1.4,0,0));
tunG.userData.tag='tunnel';
const TUN_OUT=TUN_A.clone().add(V(TUN_A.x,0,TUN_A.z).normalize().multiplyScalar(.55));

// --- house ---
const HOUSE_POS=V(0.9,FLOOR_Y,2.75);
const houseG=new THREE.Group(); houseG.position.copy(HOUSE_POS); scene.add(houseG);
houseG.add(mesh(new THREE.BoxGeometry(1.5,1.05,1.35),mat(0xb8a1e8),0,.525,0));
const roof=mesh(new THREE.ConeGeometry(1.28,.75,4),mat(0x7a68c2),0,1.42,0);
roof.rotation.y=Math.PI/4; houseG.add(roof);
houseG.add(mesh(new THREE.BoxGeometry(.46,.6,.08),mat(0x4a3f66),0,.3,.68));
const win=mesh(new THREE.CircleGeometry(.15,10),mat(0xfff3b0,{emissive:0xffd94a,emissiveIntensity:.7}),.76,.62,0);
win.rotation.y=Math.PI/2; houseG.add(win);
houseG.rotation.y=Math.atan2(-HOUSE_POS.x,-HOUSE_POS.z);
houseG.userData.tag='house';

// --- water bottle ---
const ba=2.55;
const bottleG=new THREE.Group();
bottleG.position.set(Math.cos(ba)*4.72,2.35,Math.sin(ba)*4.72);
scene.add(bottleG);
bottleG.add(mesh(new THREE.CylinderGeometry(.24,.24,.72,10),mat(0xbfe6ff,{transparent:true,opacity:.7,roughness:.2})));
bottleG.add(mesh(new THREE.CylinderGeometry(.24,.24,.4,10), mat(0x9fd8ff,{transparent:true,opacity:.75,roughness:.2}),0,-.16,0));
bottleG.add(mesh(new THREE.ConeGeometry(.27,.24,10),mat(0xcfd8e3,{metalness:.5,roughness:.35}),0,.48,0));
bottleG.add(mesh(new THREE.CylinderGeometry(.07,.07,.2,8),mat(0xcfd8e3,{metalness:.5}),0,-.46,0));
bottleG.rotation.y=Math.atan2(-Math.cos(ba),-Math.sin(ba));
bottleG.userData.tag='bottle';

// --- table decorations ---
const carrotG=new THREE.Group(); carrotG.position.set(5.6,0,-2.6); carrotG.rotation.y=rand(0,6.28); scene.add(carrotG);
const car=mesh(new THREE.ConeGeometry(.22,.7,7),mat(0xff8c42),0,.2,0);
car.rotation.x=Math.PI/2; carrotG.add(car);
for(let i=0;i<3;i++){
  const leaf=mesh(new THREE.ConeGeometry(.07,.3,5),mat(0x7fd87f),0,.32,-.42);
  leaf.rotation.x=-Math.PI/2+(i-1)*.5; carrotG.add(leaf);
}
carrotG.userData.tag='carrot';
const ball=mesh(new THREE.IcosahedronGeometry(.3,0),mat(0xff6f91),-5.7,.3,2.2);
ball.userData.tag='ball'; scene.add(ball);
let ballSpin=0;

/* ============================ HAMSTERS ============================= */
const INK=0x33323e, PINK=0xff7d9c;
function makeHamster(def){
  const g=new THREE.Group();
  const mb=mat(def.body), mbl=mat(def.belly);
  const body=mesh(new THREE.SphereGeometry(.5,8,6),mb,0,.42,0);
  body.scale.set(1,.88,1.25); g.add(body);
  const head=mesh(new THREE.SphereGeometry(.34,8,6),mb,0,.52,.5); g.add(head);
  g.add(mesh(new THREE.SphereGeometry(.16,6,5),mbl,0,.44,.82));
  g.add(mesh(new THREE.SphereGeometry(.05,6,5),mat(PINK),0,.47,.97));
  const eyeL=mesh(new THREE.SphereGeometry(.055,6,5),mat(INK),-.18,.60,.78);
  const eyeR=mesh(new THREE.SphereGeometry(.055,6,5),mat(INK), .18,.60,.78);
  g.add(eyeL,eyeR);
  const chkL=mesh(new THREE.SphereGeometry(.14,6,5),mbl,-.27,.46,.66);
  const chkR=mesh(new THREE.SphereGeometry(.14,6,5),mbl, .27,.46,.66);
  g.add(chkL,chkR);
  const earL=mesh(new THREE.ConeGeometry(.11,.17,5),mat(def.ear),-.2,.84,.4);
  const earR=mesh(new THREE.ConeGeometry(.11,.17,5),mat(def.ear), .2,.84,.4);
  earL.rotation.set(.15,0,.35); earR.rotation.set(.15,0,-.35);
  g.add(earL,earR);
  const tail=mesh(new THREE.SphereGeometry(.09,6,5),mb,0,.42,-.66); g.add(tail);
  const feet=[];
  [[-.2,.32],[.2,.32],[-.2,-.32],[.2,-.32]].forEach(([x,z])=>{
    const f=mesh(new THREE.SphereGeometry(.09,6,5),mbl,x,.1,z);
    f.scale.set(1,.7,1.4); feet.push(f); g.add(f);
  });
  return {root:g,
    parts:{body,head,eyes:[eyeL,eyeR],cheeks:[chkL,chkR],ears:[earL,earR],tail,feet},
    name:def.name, pos:V(0,FLOOR_Y,0), rot:0, phase:rand(0,6), seed:rand(0,10),
    state:'pause', kind:'', lastKind:'', timer:1,
    tx:0,tz:0, arriveR:.3, speed:1.4,
    vy:0, hopY:0, jumping:false, squash:1, scaleK:1,
    runT:0, runFrom:V(), tunT:0,
    blinkT:rand(1,4), blink:0, earT:rand(1,4), earKick:0, chomp:0, moving:false};
}
const defs=[
  {name:'Mochi',   body:0xffe3b3, belly:0xfff6e6, ear:0xf5c98e, pos:[ 1.6, 1.4]},
  {name:'Biscuit', body:0xffb45e, belly:0xffe8c9, ear:0xf09a3e, pos:[-1.8,-1.2]},
  {name:'Pepper',  body:0xaab4c4, belly:0xf2f5fa, ear:0x8f9aab, pos:[ 2.1,-1.9]},
  {name:'Mango',   body:0xff9e6d, belly:0xffe0c2, ear:0xf07f4a, pos:[-1.1, 2.5]},
];
const hamsters=defs.map(d=>{
  const h=makeHamster(d);
  h.pos.set(d.pos[0],FLOOR_Y,d.pos[1]);
  h.root.position.copy(h.pos);
  scene.add(h.root);
  h.root.userData.tag='hamster';
  h.root.userData.h=h;
  return h;
});

/* ========================= BEHAVIOR BRAIN ========================== */
const XZ={wheel:V(3.1,0,0), house:V(0.9,0,2.75), bowl:V(-2.5,0,2.05), tA:V(-2.3,0,-2.4), tB:V(0.7,0,-2.4)};
const WHEEL_APPROACH=V(3.1,FLOOR_Y,1.75), WHEEL_IN=V(3.1,FLOOR_Y,0);

function segDist(p,a,b){
  const abx=b.x-a.x, abz=b.z-a.z;
  const t=clamp(((p.x-a.x)*abx+(p.z-a.z)*abz)/Math.max(abx*abx+abz*abz,1e-6),0,1);
  return Math.hypot(p.x-(a.x+abx*t), p.z-(a.z+abz*t));
}
function randSpot(){
  for(let i=0;i<10;i++){
    const a=rand(0,Math.PI*2), r=rand(.4,3.2);
    const p=V(Math.cos(a)*r,0,Math.sin(a)*r);
    if(p.distanceTo(XZ.wheel)<1.9 && p.distanceTo(XZ.house)<1.6 &&
       p.distanceTo(XZ.bowl)<1.1 && segDist(p,XZ.tA,XZ.tB)<1.0) continue;
    return p;
  }
  return V(rand(-2,2),0,rand(-2,2));
}
function pickNext(h){
  const opts=[['wander',3],['pause',2.2],['food',1.5],['wheel',1.2],['tunnel',1.2],['house',1.2]]
    .filter(o=>o[0]!==h.lastKind);
  let tot=0; opts.forEach(o=>tot+=o[1]);
  let r=Math.random()*tot;
  for(const [k,w] of opts){ r-=w; if(r<=0) return k; }
  return 'wander';
}
function startKind(h,kind){
  h.kind=kind;
  if(kind==='wander'){const p=randSpot();h.tx=p.x;h.tz=p.z;h.arriveR=.3;h.speed=rand(1.2,1.7);h.state='go';}
  else if(kind==='food'){h.tx=FOOD_APPROACH.x;h.tz=FOOD_APPROACH.z;h.arriveR=.3;h.speed=1.5;h.state='go';}
  else if(kind==='wheel'){h.tx=WHEEL_APPROACH.x;h.tz=WHEEL_APPROACH.z;h.arriveR=.3;h.speed=1.6;h.state='go';}
  else if(kind==='tunnel'){h.tx=TUN_OUT.x;h.tz=TUN_OUT.z;h.arriveR=.35;h.speed=1.5;h.state='go';}
  else if(kind==='house'){h.tx=HOUSE_POS.x;h.tz=HOUSE_POS.z;h.arriveR=1.35;h.speed=1.4;h.state='go';}
  else {h.state='pause';h.timer=rand(1.5,4);h.moving=false;}
}
function arrive(h){
  if(h.kind==='wander'){h.state='pause';h.timer=rand(.8,2);h.moving=false;}
  else if(h.kind==='food'){h.state='eat';h.timer=rand(2.2,4.5);}
  else if(h.kind==='wheel'){h.state='run';h.runT=0;h.runFrom.copy(h.pos);h.timer=rand(3,6);}
  else if(h.kind==='tunnel'){h.state='tunnel';h.tunT=0;}
  else if(h.kind==='house'){h.state='hide';h.timer=rand(2,4);}
  queueMsg(h);
}
function finish(h){
  h.lastKind=h.kind; h.moving=false;
  startKind(h,pickNext(h)); queueMsg(h);
}
function faceToward(h,px,pz,dt){
  h.rot=lerpAngle(h.rot,Math.atan2(px-h.pos.x,pz-h.pos.z),1-Math.exp(-8*dt));
}
function pushOut(p,c,r){
  const dx=p.x-c.x,dz=p.z-c.z,L=Math.hypot(dx,dz);
  if(L<r&&L>1e-4){p.x=c.x+dx/L*r;p.z=c.z+dz/L*r;}
}
function segPush(p,a,b,r){
  const abx=b.x-a.x,abz=b.z-a.z;
  const t=clamp(((p.x-a.x)*abx+(p.z-a.z)*abz)/Math.max(abx*abx+abz*abz,1e-6),0,1);
  const cx=a.x+abx*t,cz=a.z+abz*t;
  const dx=p.x-cx,dz=p.z-cz,L=Math.hypot(dx,dz);
  if(L<r&&L>1e-4){p.x=cx+dx/L*r;p.z=cz+dz/L*r;}
}

/* ============================ ANIMATION ============================ */
function updateHamster(h,dt,t){
  h.moving=false;
  if(h.state!=='go') h.timer-=dt;
  // blink
  h.blinkT-=dt;
  if(h.blinkT<=0){h.blinkT=rand(2,5);h.blink=.13;}
  if(h.blink>0)h.blink-=dt;
  const es=h.blink>0?.15:1;
  h.parts.eyes.forEach(e=>e.scale.y+=(es-e.scale.y)*Math.min(1,dt*25));
  // ear twitches
  h.earT-=dt;
  if(h.earT<=0){h.earT=rand(2.5,6);h.earKick=pick([-1,1])*rand(.4,.7);}
  h.earKick*=Math.exp(-dt*5);

  switch(h.state){
    case 'go':{
      const dx=h.tx-h.pos.x,dz=h.tz-h.pos.z,d=Math.hypot(dx,dz);
      if(d<h.arriveR){arrive(h);break;}
      h.rot=lerpAngle(h.rot,Math.atan2(dx,dz),1-Math.exp(-9*dt));
      h.pos.x+=dx/d*h.speed*dt; h.pos.z+=dz/d*h.speed*dt;
      h.moving=true; break;
    }
    case 'eat':
      faceToward(h,BOWL_POS.x,BOWL_POS.z,dt);
      h.chomp=Math.sin(t*13+h.seed);
      if(h.timer<=0){if(Math.random()<.75)mouthPellet(h);finish(h);}
      break;
    case 'run':
      h.runT+=dt;
      if(h.runT<.4){
        const k=h.runT/.4;
        h.pos.lerpVectors(h.runFrom,WHEEL_IN,k);
        h.rot=lerpAngle(h.rot,Math.PI/2,1-Math.exp(-7*dt));
      }
      h.moving=true;
      if(h.timer<=0){h.vy=3.4;h.jumping=true;finish(h);}
      break;
    case 'tunnel':
      h.tunT+=dt/1.25;
      if(h.tunT>=1){h.pos.set(TUN_B.x,FLOOR_Y,TUN_B.z);h.rot=Math.PI/2;h.scaleK=1;finish(h);}
      else{
        const k=h.tunT*h.tunT*(3-2*h.tunT);
        h.pos.x=TUN_A.x+(TUN_B.x-TUN_A.x)*k; h.pos.z=TUN_B.z; h.rot=Math.PI/2;
        h.scaleK=1-.22*Math.sin(Math.PI*h.tunT);
      }
      break;
    case 'hide':
      faceToward(h,HOUSE_POS.x,HOUSE_POS.z,dt);
      if(h.timer<=0)finish(h);
      break;
    case 'pause':
      if(h.timer<1&&zzzs.length<5&&Math.random()<dt*1.5)spawnZzz(h);
      if(h.timer<=0)finish(h);
      break;
  }

  // hop physics + squash
  if(h.jumping){
    h.vy-=15*dt; h.hopY+=h.vy*dt;
    if(h.hopY<=0){h.hopY=0;h.jumping=false;h.squash=.7;}
  }
  h.squash+=(1-h.squash)*Math.min(1,dt*10);

  // soft collisions
  if(h.state!=='tunnel'&&h.state!=='run'){
    pushOut(h.pos,XZ.wheel,1.7);
    pushOut(h.pos,XZ.house,1.3);
    pushOut(h.pos,XZ.bowl,.9);
    segPush(h.pos,XZ.tA,XZ.tB,.85);
    const L=Math.hypot(h.pos.x,h.pos.z);
    if(L>3.6){h.pos.x*=3.6/L;h.pos.z*=3.6/L;}
  }

  // apply pose
  const bob=h.moving?Math.abs(Math.sin(h.phase))*.05:(.01+.01*Math.sin(t*2.2+h.seed));
  h.root.position.set(h.pos.x,FLOOR_Y+h.hopY+bob,h.pos.z);
  h.root.rotation.y=h.rot;
  const sq=h.squash, ex=1+(1-sq)*.55;
  h.root.scale.set(h.scaleK*ex,h.scaleK*sq,h.scaleK*ex);
  h.phase+=dt*(h.state==='run'?16:h.moving?9:2.4);
  const sw=h.moving?.16:.03;
  h.parts.feet[0].position.z= .32+Math.sin(h.phase)*sw;
  h.parts.feet[1].position.z= .32-Math.sin(h.phase)*sw;
  h.parts.feet[2].position.z=-.32-Math.sin(h.phase)*sw;
  h.parts.feet[3].position.z=-.32+Math.sin(h.phase)*sw;
  h.parts.head.position.y=.52+(h.state==='eat'?.05*Math.max(0,h.chomp):Math.sin(h.phase*.5)*.015);
  h.parts.head.rotation.x=Math.sin(t*.7+h.seed)*.06;
  const cs=h.state==='eat'?1+.32*Math.max(0,Math.sin(h.phase*2)):1;
  h.parts.cheeks.forEach(c=>c.scale.setScalar(cs));
  h.parts.ears[0].rotation.z= .35+h.earKick;
  h.parts.ears[1].rotation.z=-.35-h.earKick;
  h.parts.tail.position.x=Math.sin(h.phase)*.05;
  h.parts.body.scale.y=.88*(1+.03*Math.sin(t*2.6+h.seed));
}
// keep hamsters from stacking
function separate(){
  for(let i=0;i<hamsters.length;i++)for(let j=i+1;j<hamsters.length;j++){
    const a=hamsters[i],b=hamsters[j];
    if(a.state==='tunnel'||b.state==='tunnel')continue;
    const dx=b.pos.x-a.pos.x,dz=b.pos.z-a.pos.z,L=Math.hypot(dx,dz);
    if(L<.72&&L>1e-4){
      const p=(.72-L)/2/L;
      a.pos.x-=dx*p;a.pos.z-=dz*p;b.pos.x+=dx*p;b.pos.z+=dz*p;
    }
  }
}

/* ============================= PELLETS ============================= */
const pellets=[];
const pelCols=[0xff9f43,0xf5a623,0xffd166];
function addPellet(x,y,z,vx=0,vy=0,vz=0,shared=true){
  const m=mesh(new THREE.DodecahedronGeometry(.075,0),shared?mat(pick(pelCols)):mat(pick(pelCols)),x,y,z);
  m.rotation.set(rand(0,6),rand(0,6),rand(0,6));
  scene.add(m);
  pellets.push({m,v:V(vx,vy,vz),settle:false});
  if(pellets.length>40){const old=pellets.shift();scene.remove(old.m);}
}
for(let i=0;i<6;i++){const a=rand(0,6.28),r=rand(0,.28);addPellet(BOWL_POS.x+Math.cos(a)*r,FLOOR_Y+.26,BOWL_POS.z+Math.sin(a)*r);}
for(let i=0;i<5;i++){const a=rand(0,6.28),r=rand(1.5,3.4);addPellet(Math.cos(a)*r,FLOOR_Y+.07,Math.sin(a)*r);}
function dropPellets(){
  for(let i=0;i<9;i++)
    addPellet(BOWL_POS.x+rand(-.2,.2),FLOOR_Y+.3,BOWL_POS.z+rand(-.2,.2),rand(-1,1),rand(2.2,3.6),rand(-1,1));
}
function updatePellets(dt){
  for(const p of pellets){
    if(p.settle)continue;
    p.v.y-=9*dt;
    p.m.position.addScaledVector(p.v,dt);
    p.m.rotation.x+=dt*4; p.m.rotation.z+=dt*3;
    const bf=Math.hypot(p.m.position.x-BOWL_POS.x,p.m.position.z-BOWL_POS.z);
    const rest=bf<.45?.26:.07;
    if(p.m.position.y<rest){
      p.m.position.y=rest;
      if(Math.abs(p.v.y)>1)p.v.y*=-.35;else{p.v.set(0,0,0);p.settle=true;}
      p.v.x*=.75;p.v.z*=.75;
    }
    const L=Math.hypot(p.m.position.x,p.m.position.z);
    if(L>4.3){p.m.position.x*=4.3/L;p.m.position.z*=4.3/L;}
  }
}

/* ===================== FX: zzz + eaten pellets ===================== */
const zzzCv=document.createElement('canvas'); zzzCv.width=zzzCv.height=128;
const zzzTex=new THREE.CanvasTexture(zzzCv); zzzTex.colorSpace=THREE.SRGBColorSpace;
function drawZzz(){
  const x=zzzCv.getContext('2d'); x.clearRect(0,0,128,128);
  x.font='700 96px Fredoka, Nunito, sans-serif';
  x.textAlign='center'; x.textBaseline='middle';
  x.fillStyle='#7a68c2'; x.fillText('z',64,70);
  zzzTex.needsUpdate=true;
}
drawZzz();
if(document.fonts&&document.fonts.ready)
  document.fonts.ready.then(()=>{drawLabel();drawZzz();});

const zzzs=[];
function spawnZzz(h){
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:zzzTex,transparent:true,depthWrite:false}));
  s.position.set(h.pos.x,FLOOR_Y+1.05,h.pos.z);
  s.scale.setScalar(.5);
  scene.add(s);
  zzzs.push({s,life:0,max:1.5});
}
function updateZzz(dt){
  for(let i=zzzs.length-1;i>=0;i--){
    const z=zzzs[i]; z.life+=dt; const k=z.life/z.max;
    z.s.position.y+=dt*.55; z.s.position.x+=dt*.15;
    z.s.material.opacity=1-k; z.s.scale.setScalar(.5+k*.5);
    if(k>=1){scene.remove(z.s);z.s.material.dispose();zzzs.splice(i,1);}
  }
}
const shrinks=[];
function mouthPellet(h){
  const wp=new THREE.Vector3(0,.55,.95).applyQuaternion(h.root.quaternion).add(h.root.position);
  const m=mesh(new THREE.DodecahedronGeometry(.06,0),mat(pick(pelCols)),wp.x,wp.y,wp.z);
  scene.add(m);
  shrinks.push({m,life:0,max:.45});
}
function updateShrinks(dt){
  for(let i=shrinks.length-1;i>=0;i--){
    const s=shrinks[i]; s.life+=dt; const k=s.life/s.max;
    s.m.scale.setScalar(Math.max(.01,1-k));
    if(k>=1){scene.remove(s.m);s.m.material.dispose();shrinks.splice(i,1);}
  }
}

/* =============================== HUD =============================== */
const tickEl=document.getElementById('tickTxt'), tickerEl=document.getElementById('ticker');
function toast(msg){
  tickEl.textContent=msg;
  tickerEl.classList.remove('tick'); void tickerEl.offsetWidth; tickerEl.classList.add('tick');
}
function floaty(x,y,txt){
  const d=document.createElement('div');
  d.className='float'; d.textContent=txt;
  d.style.left=x+'px'; d.style.top=y+'px';
  document.body.appendChild(d);
  d.addEventListener('animationend',()=>d.remove());
}
const MSG={
  wander:n=>`${n} is exploring the yard`,
  pause:n=>pick([`${n} is judging you`,`${n} took a snack break`,`${n} is thinking about seeds`,`${n} is doing absolutely nothing`]),
  eat:n=>`${n} is nom nom nom-ing`,
  run:n=>`${n} is doing laps on the wheel`,
  tunnel:n=>`${n} vanished into the tunnel`,
  hide:n=>`${n} is hiding in the house`,
};
let msgQueue=[], lastMsg=0;
function queueMsg(h){
  const m=MSG[h.state]?MSG[h.state](h.name):null;
  if(m){msgQueue.push(m); if(msgQueue.length>1)msgQueue.shift();}
}

/* ============================== SOUND ============================== */
let actx=null, muted=false;
function snd(f,d,type='sine',g=.14,slide=0){
  if(muted)return;
  try{
    actx=actx||new (window.AudioContext||window.webkitAudioContext)();
    if(actx.state==='suspended')actx.resume();
    const o=actx.createOscillator(),gn=actx.createGain(),t0=actx.currentTime;
    o.type=type; o.frequency.setValueAtTime(f,t0);
    if(slide)o.frequency.linearRampToValueAtTime(Math.max(60,f+slide),t0+d);
    gn.gain.setValueAtTime(g,t0);
    gn.gain.exponentialRampToValueAtTime(.001,t0+d);
    o.connect(gn).connect(actx.destination);
    o.start(t0); o.stop(t0+d+.02);
  }catch(e){}
}
const sndBtn=document.getElementById('ctrlSnd'), rstBtn=document.getElementById('ctrlRst');
sndBtn.onclick=()=>{muted=!muted;sndBtn.textContent=muted?'🔇':'🔊';if(!muted)snd(660,.07,'sine',.12,200);};
rstBtn.onclick=()=>{cam.tTheta=.75;cam.tPhi=1.05;cam.tR=13.5;snd(440,.08,'triangle',.12,120);};

/* =========================== CAMERA / INPUT ======================== */
const cam={theta:.75,phi:1.05,r:13.5,tTheta:.75,tPhi:1.05,tR:13.5,target:V(0,1.7,0)};
let lastAct=0, dragMoved=0, pinchD=0;
const pts=new Map();
const ray=new THREE.Raycaster(), mouse=new THREE.Vector2(-2,-2);
const clickables=[wheelG,bowlG,tunG,houseG,bottleG,carrotG,ball,...hamsters.map(h=>h.root)];
function tagOf(o){while(o){if(o.userData&&o.userData.tag)return o;o=o.parent;}return null;}
function retarget(p,kind){
  hamsters.forEach(h=>{
    if(h.state==='tunnel'||h.state==='run')return;
    if(Math.random()<p){h.lastKind=h.kind;startKind(h,kind);queueMsg(h);}
  });
}
function handleClick(x,y){
  mouse.x=(x/innerWidth)*2-1; mouse.y=-(y/innerHeight)*2+1;
  ray.setFromCamera(mouse,camera);
  const hit=ray.intersectObjects(clickables,true)[0];
  if(!hit)return;
  const node=tagOf(hit.object); if(!node)return;
  const tag=node.userData.tag;
  if(tag==='hamster'){
    const h=node.userData.h;
    h.vy=4.6; h.jumping=true; h.earKick=1.2;
    snd(520,.08,'sine',.16,260);
    floaty(x,y,'💕');
    toast(`Boop! ${h.name} squeaks happily`);
  }else{
    snd(300,.09,'triangle',.14,-140);
    if(tag==='bowl'){dropPellets();floaty(x,y,'🍊');toast('Snack drop! You can hear the crunching from here.');retarget(.65,'food');}
    else if(tag==='wheel'){wheelVel+=7;floaty(x,y,'💨');toast('WHEEL TIME! Zoomies engaged.');retarget(.65,'wheel');}
    else if(tag==='tunnel'){floaty(x,y,'👀');toast('Tunnel boop… someone peeks out.');retarget(.5,'tunnel');}
    else if(tag==='house'){floaty(x,y,'🏠');toast('Knock knock… anyone home?');retarget(.5,'house');}
    else if(tag==='bottle'){floaty(x,y,'💧');toast('Hydration check: 100% hydrated.');}
    else if(tag==='carrot'){floaty(x,y,'🥕');toast('The carrot remains safe. For now.');}
    else if(tag==='ball'){ballSpin=10;floaty(x,y,'🎾');toast("The ball rolls. Nobody cares. It's a hamster.");}
  }
}
canvas.addEventListener('pointerdown',e=>{
  canvas.setPointerCapture(e.pointerId);
  pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pts.size===2){const[a,b]=[...pts.values()];pinchD=Math.hypot(a.x-b.x,a.y-b.y);}
  dragMoved=0; canvas.classList.add('dragging'); canvas.style.cursor='';
  lastAct=performance.now();
});
canvas.addEventListener('pointermove',e=>{
  mouse.x=(e.clientX/innerWidth)*2-1; mouse.y=-(e.clientY/innerHeight)*2+1;
  if(!pts.has(e.pointerId))return;
  const p=pts.get(e.pointerId);
  const dx=e.clientX-p.x, dy=e.clientY-p.y;
  p.x=e.clientX; p.y=e.clientY;
  lastAct=performance.now();
  if(pts.size===1){
    cam.tTheta-=dx*.0055;
    cam.tPhi=clamp(cam.tPhi-dy*.0045,.35,1.35);
    dragMoved+=Math.abs(dx)+Math.abs(dy);
  }else if(pts.size===2){
    const[a,b]=[...pts.values()];
    const d=Math.hypot(a.x-b.x,a.y-b.y);
    if(pinchD>0)cam.tR=clamp(cam.tR*pinchD/d,7.5,19);
    pinchD=d; dragMoved+=10;
  }
});
canvas.addEventListener('pointerup',e=>{
  if(pts.has(e.pointerId)){
    if(dragMoved<7)handleClick(e.clientX,e.clientY);
    pts.delete(e.pointerId);
    if(pts.size<2)pinchD=0;
    if(pts.size===0)canvas.classList.remove('dragging');
  }
});
canvas.addEventListener('pointercancel',e=>{
  pts.delete(e.pointerId);
  if(pts.size===0)canvas.classList.remove('dragging');
});
canvas.addEventListener('wheel',e=>{
  e.preventDefault();
  cam.tR=clamp(cam.tR*(1+e.deltaY*.0011),7.5,19);
  lastAct=performance.now();
},{passive:false});

/* ============================ MAIN LOOP ============================ */
let wheelVel=0;
const clock=new THREE.Clock();
let hoverTick=0;

function loop(){
  requestAnimationFrame(loop);
  const dt=Math.min(clock.getDelta(),.05);
  const t=clock.elapsedTime, now=performance.now();

  hamsters.forEach(h=>updateHamster(h,dt,t));
  separate();

  // wheel + ball
  const running=hamsters.some(h=>h.state==='run');
  wheelVel+=((running?7:0)-wheelVel)*Math.min(1,dt*1.6);
  wheelDisc.rotation.z+=wheelVel*dt;
  ballSpin*=Math.exp(-dt*2);
  ball.rotation.x+=dt*(ballSpin+.2);
  ball.rotation.y+=dt*ballSpin;

  updatePellets(dt);
  updateZzz(dt);
  updateShrinks(dt);

  // activity ticker
  if(msgQueue.length&&now-lastMsg>1400){toast(msgQueue.shift());lastMsg=now;}

  // camera (damped orbit + idle drift)
  if(now-lastAct>5000)cam.tTheta+=dt*.06;
  const k=1-Math.exp(-8*dt);
  cam.theta+=(cam.tTheta-cam.theta)*k;
  cam.phi+=(cam.tPhi-cam.phi)*k;
  cam.r+=(cam.tR-cam.r)*k;
  camera.position.set(
    cam.target.x+cam.r*Math.sin(cam.phi)*Math.sin(cam.theta),
    cam.target.y+cam.r*Math.cos(cam.phi),
    cam.target.z+cam.r*Math.sin(cam.phi)*Math.cos(cam.theta));
  camera.lookAt(cam.target);

  // hover cursor
  if(++hoverTick%3===0&&pts.size===0){
    ray.setFromCamera(mouse,camera);
    canvas.style.cursor=ray.intersectObjects(clickables,true).length?'pointer':'';
  }

  renderer.render(scene,camera);
}

/* ============================== START ============================== */
[['wander'],['food'],['wheel'],['pause']].forEach(([kind],i)=>{
  hamsters[i].lastKind=kind;
  startKind(hamsters[i],kind);
});
toast('Welcome to the cage! Four residents, zero chill. 🐹');

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
loop();
</script>
</body>
</html>
```

**What's inside:**

- **The cage** — a round wire cage on a wooden table: blue plastic base, sand bedding with scattered shavings, 16 wire bars, three rings, and a "Home Sweet Cage" plaque.
- **Four hamsters** (Mochi, Biscuit, Pepper, Mango) built from low-poly primitives with waddling feet, blinking eyes, ear twitches, tail flicks, breathing, and squash-and-stretch hops.
- **Autonomous AI** — a weighted state machine per hamster: wandering, pausing (with floating "z"s), chomping at the bowl (cheeks puff, pellets vanish into their mouths), running the wheel (it actually spins), disappearing into the tunnel and emerging on the other side, and hiding in the house. Soft collisions keep them from overlapping or clipping through furniture.
- **Interactive objects** — click the **bowl** (pellets rain down, everyone gets hungry), the **wheel** (zoomies + spin boost), the **tunnel**, **house**, **water bottle**, **carrot**, or **ball** — each triggers a reaction, an emoji pop, and a sound blip. Click a hamster to boop it.
- **Camera** — drag to orbit, scroll or pinch to zoom, with damping and a gentle auto-drift when idle. Reset-view and mute buttons included.
- **Live ticker** — bottom-left reports what each resident is up to ("Pepper is judging you").

Everything is procedural (no assets beyond the Three.js CDN and two Google Fonts), so it loads instantly and runs offline-ish in any modern browser.