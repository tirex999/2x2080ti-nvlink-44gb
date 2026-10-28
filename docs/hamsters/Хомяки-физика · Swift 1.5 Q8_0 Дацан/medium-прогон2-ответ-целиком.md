# Клетка с хомяками — честная физика

Ниже — полный самодостаточный HTML-файл. Ключевые величины вынесены в `window` (`hamsters`, `wheelObj`, `tubeObj`, `ANIMAL`), панель телеметрии показывает |ω|·R против скорости лап в реальном времени.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Клетка с хомяками — честная физика</title>
<style>
  body{margin:0;overflow:hidden;font-family:Arial,Helvetica,sans-serif;background:#171210}
  #panel{position:fixed;top:10px;left:10px;background:rgba(24,17,10,.85);color:#f5e9d0;
         padding:12px 16px;border-radius:10px;font-size:13px;line-height:1.7;z-index:10;min-width:230px}
  #panel h3{margin:0 0 6px;font-size:14px;color:#ffd98a}
  .dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;border:1px solid #0006}
  #debug{position:fixed;top:10px;right:10px;background:rgba(8,14,24,.88);color:#9fe8a0;
         padding:10px 14px;border-radius:10px;font:12px/1.7 "Consolas",monospace;z-index:10;white-space:pre}
  #hint{position:fixed;bottom:8px;left:12px;color:#c9b896;font-size:12px;z-index:10}
</style>
</head>
<body>
<div id="panel"><h3>Хомяки</h3><div id="plist"></div></div>
<div id="debug"></div>
<div id="hint">ЛКМ по хомяку — прыжок · мышь — вращение камеры · колесо — зум</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
'use strict';
/* ============================================================================
   КОНСТАНТЫ ГАБАРИТОВ (п.1.2): радиус колеса ВЫВОДИТСЯ ИЗ размера зверя.
   ========================================================================== */
const ANIMAL_LEN = 1.00;          // длина зверя (нос-хвост), м
const ANIMAL_H   = 0.62;          // высота зверя (лапы-макушка), м
const ANIMAL_R   = 0.30;          // радиус тела в плане (для столкновений)
const STEP_LEN   = 0.35;          // длина шага для фазы лап (п.1.5)

// Колесо: зверь целиком внутри с запасом: R > ANIMAL_H + запас над головой.
const WHEEL_R = ANIMAL_H * 1.9;   // ≈1.18 → запас над головой ~0.56 > 0 ✓
const WHEEL_W = ANIMAL_LEN * 1.4; // расстояние между ободами шире боков (0.6) ✓
console.assert(WHEEL_R > ANIMAL_H + 0.3, 'Колесо должно быть больше зверя');
console.assert(WHEEL_W > ANIMAL_R*2 + 0.4, 'Между ободами шире боков зверя');

/* ============================== СЦЕНА ==================================== */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2a211b);
scene.fog = new THREE.Fog(0x2a211b, 30, 55);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, .1, 120);
camera.position.set(9, 9.5, 15);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.6, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI*0.49;
controls.minDistance = 5; controls.maxDistance = 40;

/* ------------------------------ свет ------------------------------------ */
scene.add(new THREE.HemisphereLight(0xfff3e0, 0x665544, 0.55));
const sun = new THREE.DirectionalLight(0xfff2dd, 0.95);
sun.position.set(10, 18, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -14; sun.shadow.camera.right = 14;
sun.shadow.camera.top = 14;   sun.shadow.camera.bottom = -14;
sun.shadow.camera.far = 45;   sun.shadow.bias = -0.0006;
scene.add(sun);

/* ----------------------------- комната ----------------------------------- */
const roomFloor = new THREE.Mesh(new THREE.PlaneGeometry(46,34),
  new THREE.MeshLambertMaterial({color:0x7d5f42}));
roomFloor.rotation.x = -Math.PI/2; roomFloor.position.y = -4.6;
roomFloor.receiveShadow = true; scene.add(roomFloor);
const wallMat = new THREE.MeshLambertMaterial({color:0xa98d6e});
const backWall = new THREE.Mesh(new THREE.PlaneGeometry(46,17), wallMat);
backWall.position.set(0,3.9,-14); scene.add(backWall);
const sideWall = new THREE.Mesh(new THREE.PlaneGeometry(34,17), wallMat);
sideWall.rotation.y = Math.PI/2; sideWall.position.set(-20,3.9,3); scene.add(sideWall);

/* ------------------------------ стол -------------------------------------- */
const tableMat = new THREE.MeshLambertMaterial({color:0x6b4a2c});
const tableTop = new THREE.Mesh(new THREE.BoxGeometry(15,0.45,11), tableMat);
tableTop.position.y = -0.72; tableTop.castShadow = tableTop.receiveShadow = true;
scene.add(tableTop);
for(const sx of [-1,1]) for(const sz of [-1,1]){
  const leg = new THREE.Mesh(new THREE.BoxGeometry(0.5,3.85,0.5), tableMat);
  leg.position.set(sx*7, -2.87, sz*5); leg.castShadow = true; scene.add(leg);
}

/* ----------------------------- поддон клетки ------------------------------ */
const CX = 6, CZ = 4, WALL_H = 3.6;          // внутренние границы прутьев
const trayMat = new THREE.MeshLambertMaterial({color:0x3f5d72});
const tray = new THREE.Mesh(new THREE.BoxGeometry(12.6,0.5,8.6), trayMat);
tray.position.y = -0.25; tray.castShadow = tray.receiveShadow = true; scene.add(tray);
for(const [w,d,x,z] of [[12.6,.3,0,-4.15],[12.6,.3,0,4.15],[.3,8.6,-6.15,0],[.3,8.6,6.15,0]]){
  const rim = new THREE.Mesh(new THREE.BoxGeometry(w,0.5,d), trayMat);
  rim.position.set(x,0.1,z); rim.castShadow = true; scene.add(rim);
}

/* --------------------- подстилка: ONE InstancedMesh (п.3) ------------------ */
{
  const n = 650;
  const chipGeo = new THREE.BoxGeometry(0.2,0.035,0.055);
  const chips = new THREE.InstancedMesh(chipGeo,
    new THREE.MeshLambertMaterial({color:0xffffff}), n);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(),
        e = new THREE.Euler(), s = new THREE.Vector3(), p = new THREE.Vector3(),
        col = new THREE.Color();
  for(let i=0;i<n;i++){
    p.set((Math.random()*2-1)*5.9, 0.02+Math.random()*0.02, (Math.random()*2-1)*3.9);
    e.set(0, Math.random()*Math.PI, (Math.random()-0.5)*0.25); q.setFromEuler(e);
    s.set(0.7+Math.random()*0.9, 1, 0.7+Math.random()*0.9);
    chips.setMatrixAt(i, m.compose(p,q,s));
    col.setHSL(0.09+Math.random()*0.04, 0.45, 0.55+Math.random()*0.2);
    chips.setColorAt(i, col);
  }
  chips.receiveShadow = true; scene.add(chips);
}

/* --------------------- прутья: ONE InstancedMesh + рамки ------------------- */
{
  const step=0.48, positions=[];
  for(let x=-CX; x<=CX+1e-6; x+=step){ positions.push([x,-CZ]); positions.push([x,CZ]); }
  for(let z=-CZ+step; z<=CZ-step+1e-6; z+=step){ positions.push([-CX,z]); positions.push([CX,z]); }
  const bars = new THREE.InstancedMesh(
    new THREE.CylinderGeometry(0.045,0.045,WALL_H,8),
    new THREE.MeshStandardMaterial({color:0xb9c2cc, metalness:0.75, roughness:0.35}),
    positions.length);
  const m=new THREE.Matrix4(), q=new THREE.Quaternion(), p=new THREE.Vector3(), s=new THREE.Vector3(1,1,1);
  positions.forEach((b,i)=>{ p.set(b[0], 0.4+WALL_H/2, b[1]);
    bars.setMatrixAt(i, m.compose(p,q,s)); });
  bars.castShadow = true; scene.add(bars);
  const frameMat = new THREE.MeshStandardMaterial({color:0x8d98a4, metalness:0.7, roughness:0.4});
  for(const [w,d,x,z] of [[12.3,.14,0,-CZ],[12.3,.14,0,CZ],[.14,8.3,-CX,0],[.14,8.3,CX,0]]){
    const f = new THREE.Mesh(new THREE.BoxGeometry(w,0.16,d), frameMat);
    f.position.set(x, 0.4+WALL_H, z); f.castShadow = true; scene.add(f);
  }
}

/* ============================================================================
   КОЛЕСО (п.1.1–1.2). Ось горизонтальна (X). ω выводится из скорости бега:
   ω = v / R. Пустое колесо затухает от трения.
   ========================================================================== */
const wheelObj = {
  R: WHEEL_R, W: WHEEL_W,
  cx: 3.8, cy: WHEEL_R + 0.35, cz: -1.0,
  omega: 0,          // рад/с, знаковая
  user: null,        // хомяк-бегун (один пользователь — п.1.6)
  FRICTION: 1.4      // коэффициент затухания пустого колеса
};
const wheelGroup = new THREE.Group();
wheelGroup.position.set(wheelObj.cx, wheelObj.cy, wheelObj.cz);
scene.add(wheelGroup);
const spinner = new THREE.Group(); wheelGroup.add(spinner);
{
  const plastic = new THREE.MeshStandardMaterial({color:0xe8f2f6, roughness:0.4, side:THREE.DoubleSide});
  // беговая поверхность — открытая цилиндрическая стенка, ось X
  const g = new THREE.CylinderGeometry(WHEEL_R, WHEEL_R, WHEEL_W, 40, 1, true);
  g.rotateZ(Math.PI/2);
  const drum = new THREE.Mesh(g, plastic); drum.castShadow = true; spinner.add(drum);
  const rimMat = new THREE.MeshStandardMaterial({color:0x63b6d8, roughness:0.4});
  for(const sx of [-1,1]){
    const torus = new THREE.Mesh(new THREE.TorusGeometry(WHEEL_R+0.06, 0.075, 10, 44), rimMat);
    torus.rotation.y = Math.PI/2; torus.position.x = sx*WHEEL_W/2; torus.castShadow = true;
    spinner.add(torus);
  }
  for(let i=0;i<8;i++){
    const sp = new THREE.Mesh(new THREE.BoxGeometry(0.035, 2*(WHEEL_R-0.02), 0.05), rimMat);
    sp.rotation.x = i*Math.PI/8; spinner.add(sp);
  }
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,WHEEL_W+1.1,10),
    new THREE.MeshStandardMaterial({color:0x8d98a4, metalness:0.7, roughness:0.4}));
  axle.rotation.z = Math.PI/2; wheelGroup.add(axle);
  const standMat = new THREE.MeshLambertMaterial({color:0x55606c});
  for(const sx of [-1,1]){
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.18, wheelObj.cy, 0.22), standMat);
    post.position.set(wheelObj.cx + sx*(WHEEL_W/2+0.5), wheelObj.cy/2, wheelObj.cz);
    post.castShadow = true; scene.add(post);
  }
}
const WHEEL_ENTRY = { x: wheelObj.cx, z: wheelObj.cz + WHEEL_R + 0.95 }; // точка входа снаружи
const WHEEL_RUN   = { x: wheelObj.cx, y: wheelObj.cy - WHEEL_R, z: wheelObj.cz }; // НИЖНЯЯ точка обода (п.1.1)

/* ============================================================================
   ТРУБА (п.1.3): полый цилиндр на подстилке, ось Z, вход только через торцы.
   ========================================================================== */
const tubeObj = {
  cx: -3.6, cz: 0.8, cy: 0.62,      // центр; cy = rOut → лежит на полу
  len: 3.4, rOut: 0.62, rIn: 0.50,
  innerFloorY: 0.62 - 0.50,          // внутренний дно, на нём стоит зверь
  users: 0
};
{
  const g = new THREE.CylinderGeometry(tubeObj.rOut, tubeObj.rOut, tubeObj.len, 30, 1, true);
  g.rotateX(Math.PI/2);
  const tube = new THREE.Mesh(g, new THREE.MeshStandardMaterial(
    {color:0xc9a26b, roughness:0.65, side:THREE.DoubleSide}));
  tube.position.set(tubeObj.cx, tubeObj.cy, tubeObj.cz);
  tube.castShadow = true; scene.add(tube);
  for(const sz of [-1,1]){
    const ring = new THREE.Mesh(new THREE.TorusGeometry(tubeObj.rOut, 0.05, 8, 30),
      new THREE.MeshLambertMaterial({color:0x8a6b42}));
    ring.position.set(tubeObj.cx, tubeObj.cy, tubeObj.cz + sz*tubeObj.len/2);
    scene.add(ring);
  }
}

/* --------------------- миска с зёрнами + поилка ---------------------------- */
const bowlObj = { x: 0.6, z: 2.6, r: 0.55 };
{
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.55,0.42,0.24,24),
    new THREE.MeshLambertMaterial({color:0x3f8f4f}));
  bowl.position.set(bowlObj.x, 0.12, bowlObj.z); bowl.castShadow = true; scene.add(bowl);
  const inner = new THREE.Mesh(new THREE.CylinderGeometry(0.46,0.36,0.2,24),
    new THREE.MeshLambertMaterial({color:0x2a5e35}));
  inner.position.set(bowlObj.x, 0.16, bowlObj.z); scene.add(inner);
  const seedMat = new THREE.MeshLambertMaterial({color:0xd8b24a});
  for(let i=0;i<16;i++){
    const s = new THREE.Mesh(new THREE.DodecahedronGeometry(0.05), seedMat);
    const a = Math.random()*Math.PI*2, r = Math.random()*0.32;
    s.position.set(bowlObj.x+Math.cos(a)*r, 0.2, bowlObj.z+Math.sin(a)*r);
    s.rotation.set(Math.random(),Math.random(),Math.random()); scene.add(s);
  }
}
{ // поилка на стенке
  const gz = new THREE.Group(); gz.position.set(-5.78, 1.4, -2.6);
  const glass = new THREE.Mesh(new THREE.CylinderGeometry(0.17,0.17,1.1,18),
    new THREE.MeshPhongMaterial({color:0xcfe8f5, transparent:true, opacity:0.45, shininess:90}));
  gz.add(glass);
  const water = new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.13,0.85,16),
    new THREE.MeshPhongMaterial({color:0x4fa8d8, transparent:true, opacity:0.7}));
  water.position.y = -0.1; gz.add(water);
  const spout = new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.02,0.45,10),
    new THREE.MeshStandardMaterial({color:0x9aa6b2, metalness:0.8, roughness:0.3}));
  spout.rotation.z = Math.PI/2; spout.position.set(0.3,-0.5,0); gz.add(spout);
  gz.children.forEach(c=>c.castShadow=true); scene.add(gz);
}

/* ============================ ХОМЯК ======================================= */
function makeHamster(cfg){
  const g = new THREE.Group();
  const fur   = new THREE.MeshLambertMaterial({color:cfg.fur});
  const belly = new THREE.MeshLambertMaterial({color:cfg.belly});
  const dark  = new THREE.MeshLambertMaterial({color:0x181818});
  const pink  = new THREE.MeshLambertMaterial({color:0xe8a0a0});
  const P = {};

  P.body = new THREE.Mesh(new THREE.SphereGeometry(0.30,20,16), fur);
  P.body.scale.set(1,0.88,1.4); P.body.position.y = 0.32; P.body.castShadow = true; g.add(P.body);

  P.bellyM = new THREE.Mesh(new THREE.SphereGeometry(0.235,18,14), belly);
  P.bellyM.scale.set(1,0.78,1.15); P.bellyM.position.set(0,0.25,0.06); g.add(P.bellyM);

  P.head = new THREE.Group(); P.head.position.set(0,0.46,0.27); g.add(P.head);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.195,20,16), fur);
  skull.castShadow = true; P.head.add(skull);
  for(const sx of [-1,1]){
    const eyeW = new THREE.Mesh(new THREE.SphereGeometry(0.05,12,10),
      new THREE.MeshLambertMaterial({color:0xf5f5f5}));
    eyeW.position.set(sx*0.115, 0.05, 0.155); P.head.add(eyeW);
    const pup = new THREE.Mesh(new THREE.SphereGeometry(0.024,10,8), dark);
    pup.position.set(sx*0.125, 0.055, 0.19); P.head.add(pup);
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.085,12,10), belly);
    cheek.position.set(sx*0.12,-0.05,0.09); P.head.add(cheek);
    const ear = new THREE.Group(); ear.position.set(sx*0.13, 0.16, -0.02); P.head.add(ear);
    const outer = new THREE.Mesh(new THREE.SphereGeometry(0.085,12,10), fur);
    outer.scale.set(1,1,0.35); outer.rotation.set(-0.5, sx*0.55, 0); ear.add(outer);
    const inr = new THREE.Mesh(new THREE.SphereGeometry(0.055,10,8), pink);
    inr.scale.set(1,1,0.35); inr.position.z = 0.02; inr.rotation.copy(outer.rotation); ear.add(inr);
    if(sx>0) P.earL = ear; else P.earR = ear;
  }
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.032,10,8), pink);
  nose.position.set(0,-0.015,0.19); P.head.add(nose);

  P.legs = [];
  const legPos = [[0.17,0.28],[-0.17,0.28],[0.17,-0.26],[-0.17,-0.26]]; // FL FR BL BR
  for(const [lx,lz] of legPos){
    const leg = new THREE.Group(); leg.position.set(lx, 0.22, lz);
    const up = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.045,0.16,10), fur);
    up.position.y = -0.08; leg.add(up);
    const foot = new THREE.Mesh(new THREE.SphereGeometry(0.05,10,8), pink);
    foot.scale.set(1,0.6,1.3); foot.position.set(0,-0.165,0.025); leg.add(foot);
    g.add(leg); P.legs.push(leg);
  }
  P.tail = new THREE.Mesh(new THREE.ConeGeometry(0.045,0.14,10), fur);
  P.tail.position.set(0,0.36,-0.42); P.tail.rotation.x = 2.5; g.add(P.tail);

  g.traverse(o=>{ if(o.isMesh){ o.castShadow = true; } });
  return {group:g, parts:P};
}

/* ============================ ФАБРИКА ХОМЯКОВ ============================= */
const NAMES_CFG = [
  {name:'Пух',     fur:0xe8b34a, belly:0xf7e3bd},
  {name:'Стрелка', fur:0xcfd4da, belly:0xf2f4f7},
  {name:'Кекс',    fur:0x9a5c28, belly:0xe6cba0},
  {name:'Тень',    fur:0x565a62, belly:0xa9adb5},
  {name:'Снежка',  fur:0xf3efe6, belly:0xffffff},
];
const hamsters = [];

function spawnHamster(cfg, x, z){
  const m = makeHamster(cfg);
  m.group.position.set(x,0,z);
  m.group.userData.hIndex = hamsters.length;
  scene.add(m.group);
  hamsters.push({
    name:cfg.name, furHex:cfg.fur,
    group:m.group, parts:m.parts,
    pos:{x, y:0, z}, rotY:Math.random()*6.28,
    state:'idle', timer:0.5+Math.random()*2, intent:null, target:{x,z},
    v:0, cruise:0, runT:0, wheelDir:1, tubeDir:1, tr:null,
    stepPhase:Math.random()*6.28, animSpeed:0, animTarget:0,
    vy:0, yOff:0, earT:1+Math.random()*4, earOn:0, phaseOff:Math.random()*6.28
  });
}
NAMES_CFG.forEach((c,i)=>spawnHamster(c, -3+i*1.6, 1.5+((i%2)?1:0)));

/* ============================== FSM ======================================= */
const rnd=(a,b)=>a+Math.random()*(b-a);
function lerpAngle(a,b,t){let d=b-a;while(d>Math.PI)d-=6.283185;while(d<-Math.PI)d+=6.283185;return a+d*Math.min(1,t);}
function smooth(t){return t*t*(3-2*t);}

function chooseActivity(h){
  const r = Math.random();
  if(!wheelObj.user && r < 0.40){                 // колесо: один пользователь (п.1.6)
    wheelObj.user = h; h.intent='wheel';
    h.target = {x:WHEEL_ENTRY.x, z:WHEEL_ENTRY.z};
  } else if(tubeObj.users < 2 && r < 0.65){       // труба
    tubeObj.users++; h.intent='tube';
    h.tubeDir = Math.random()<0.5 ? 1 : -1;
    h.target = {x:tubeObj.cx, z:tubeObj.cz - h.tubeDir*(tubeObj.len/2 + 1.1)};
  } else if(r < 0.85){                            // миска
    h.intent='bowl';
    const a=Math.random()*6.28;
    h.target = {x:bowlObj.x+Math.cos(a)*1.0, z:bowlObj.z+Math.sin(a)*1.0};
  } else {                                        // прогулка
    h.intent='walk';
    h.target = {x:rnd(-5,5), z:rnd(-3,3)};
  }
  h.state='walk';
}
function toIdle(h){ h.state='idle'; h.timer=rnd(1,3); h.intent=null; h.animTarget=0; }

function beginTransition(h, from, to, dur){
  h.tr = {fx:from.x, fy:from.y, fz:from.z, tx:to.x, ty:to.y, tz:to.z, t:0, dur};
}
function stepTransition(h, dt){
  h.tr.t += dt/h.tr.dur;
  const k = smooth(Math.min(1,h.tr.t));            // п.1.6: плавный лерп, без телепортов
  h.pos.x = h.tr.fx+(h.tr.tx-h.tr.fx)*k;
  h.pos.y = h.tr.fy+(h.tr.ty-h.tr.fy)*k;
  h.pos.z = h.tr.fz+(h.tr.tz-h.tr.fz)*k;
  return h.tr.t >= 1;
}

function onArrive(h){
  switch(h.intent){
    case 'wheel':
      beginTransition(h, h.pos, {x:WHEEL_RUN.x, y:WHEEL_RUN.y, z:WHEEL_RUN.z}, 0.7);
      h.state='wheel_enter'; h.wheelDir=1; break;
    case 'tube':  h.state='tube_walk'; break;
    case 'bowl':  h.state='eat'; h.timer=rnd(2.5,5.5); break;
    default:      toIdle(h);
  }
}

function updateFSM(h, dt){
  switch(h.state){
    case 'idle':
      h.animTarget = 0; h.timer -= dt;
      if(h.timer<=0) chooseActivity(h);
      break;

    case 'walk': {
      const dx=h.target.x-h.pos.x, dz=h.target.z-h.pos.z, d=Math.hypot(dx,dz);
      if(d < 0.14){ onArrive(h); break; }
      const sp = 1.35, dist = sp*dt;
      h.pos.x += dx/d*dist; h.pos.z += dz/d*dist;
      h.stepPhase += dist/STEP_LEN*6.283185;       // п.1.5: фаза от ПРОЙДЕННОГО ПУТИ
      h.rotY = lerpAngle(h.rotY, Math.atan2(dx,dz), 9*dt);
      h.animTarget = sp;
      break;
    }

    case 'wheel_enter':
      h.animTarget = 1.1;
      if(stepTransition(h,dt)){
        h.state='wheel_run'; h.v=0; h.cruise=rnd(1.6,3.2); h.runT=rnd(4,9);
        h.rotY = h.wheelDir>0 ? 0 : Math.PI;
      }
      break;

    case 'wheel_run': {
      h.v += (h.cruise - h.v)*Math.min(1, 1.6*dt); // разгон
      const dist = h.v*dt;
      h.stepPhase += dist/STEP_LEN*6.283185;       // шаг привязан к скорости обода (п.1.5)
      // ГЛАВНАЯ ФОРМУЛА (п.1.1): ω = v / R, знак — по направлению бега
      wheelObj.omega = h.wheelDir * h.v / wheelObj.R;
      h.animTarget = h.v;
      h.runT -= dt;
      if(h.runT <= 0){
        wheelObj.user = null;                       // колесо свободно, дальше — трение
        beginTransition(h, h.pos, {x:WHEEL_ENTRY.x, y:0, z:WHEEL_ENTRY.z}, 0.8);
        h.state='wheel_exit';
      }
      break;
    }

    case 'wheel_exit':
      h.animTarget = 1.1;
      if(stepTransition(h,dt)) toIdle(h);
      break;

    case 'tube_walk': {
      const t = tubeObj;
      h.pos.x += (t.cx - h.pos.x)*Math.min(1, 7*dt);   // строго на оси трубы (п.1.3)
      const sp = 0.95, dist = sp*dt;
      h.pos.z += h.tubeDir*sp*dt;
      h.stepPhase += dist/STEP_LEN*6.283185;
      const inside = Math.abs(h.pos.z - t.cz) < t.len/2 + 0.15;
      const ty = inside ? t.innerFloorY : 0;           // стоит на внутреннем дне
      h.pos.y += (ty - h.pos.y)*Math.min(1, 9*dt);
      h.rotY = h.tubeDir>0 ? 0 : Math.PI;
      h.animTarget = sp;
      if(Math.abs(h.pos.z - t.cz) > t.len/2 + 1.0){
        tubeObj.users--; toIdle(h);
      }
      break;
    }

    case 'eat':
      h.animTarget = 0; h.timer -= dt;
      { const dx=bowlObj.x-h.pos.x, dz=bowlObj.z-h.pos.z;
        h.rotY = lerpAngle(h.rotY, Math.atan2(dx,dz), 6*dt); }
      if(h.timer<=0) toIdle(h);
      break;
  }
}

/* ==================== СТОЛКНОВЕНИЯ: ТЁПЛЫЕ ТЕЛА (п.1.4) =================== */
function collideWheelRect(p){       // прямоугольник проекции колеса на пол
  const hx = wheelObj.W/2 + 0.25, hz = wheelObj.R + 0.25;
  const dx = p.x - wheelObj.cx, dz = p.z - wheelObj.cz;
  const ox = hx - Math.abs(dx), oz = hz - Math.abs(dz);
  if(ox > 0 && oz > 0){
    if(ox < oz) p.x = wheelObj.cx + Math.sign(dx||1)*hx;
    else        p.z = wheelObj.cz + Math.sign(dz||1)*hz;
  }
}
function collideTubeCapsule(p){     // капсула: выталкивает с боков и от торцов
  const t = tubeObj, min = t.rOut + ANIMAL_R;
  const dzc = Math.max(-t.len/2, Math.min(t.len/2, p.z - t.cz));
  let dx = p.x - t.cx, dz = p.z - (t.cz + dzc);
  let d = Math.hypot(dx,dz);
  if(d < min){
    if(d < 1e-5){ p.x = t.cx + min; return; }
    p.x = t.cx + dx/d*min; p.z = t.cz + dzc + dz/d*min;
  }
}
function collideBowl(p){
  const min = bowlObj.r + 0.24;
  const dx = p.x - bowlObj.x, dz = p.z - bowlObj.z, d = Math.hypot(dx,dz);
  if(d < min && d > 1e-5){ p.x = bowlObj.x + dx/d*min; p.z = bowlObj.z + dz/d*min; }
}
function clampCage(p){
  p.x = Math.max(-CX+0.35, Math.min(CX-0.35, p.x));
  p.z = Math.max(-CZ+0.35, Math.min(CZ-0.35, p.z));
}
function separateHamsters(){         // мягкое расталкивание зверей (п.1.4)
  for(let i=0;i<hamsters.length;i++) for(let j=i+1;j<hamsters.length;j++){
    const a=hamsters[i], b=hamsters[j];
    const busy = h => h.state.startsWith('wheel_') || h.state==='tube_walk';
    if(busy(a)||busy(b)) continue;
    const dx=b.pos.x-a.pos.x, dz=b.pos.z-a.pos.z, min=ANIMAL_R*2;
    const d=Math.hypot(dx,dz);
    if(d<min && d>1e-5){
      const push=(min-d)/2;
      a.pos.x-=dx/d*push; a.pos.z-=dz/d*push;
      b.pos.x+=dx/d*push; b.pos.z+=dz/d*push;
    }
  }
}

/* ========================= АНИМАЦИЯ ЗВЕРЯ ================================= */
function animateHamster(h, dt, time){
  h.animSpeed += (h.animTarget - h.animSpeed)*Math.min(1, 9*dt);
  const amp = Math.min(1, h.animSpeed/1.3);
  // лапы диагональными парами: FL+BR, FR+BL (п.1.5)
  const L = h.parts.legs;
  L[0].rotation.x = Math.sin(h.stepPhase)*0.55*amp;
  L[3].rotation.x = Math.sin(h.stepPhase)*0.55*amp;
  L[1].rotation.x = Math.sin(h.stepPhase+Math.PI)*0.55*amp;
  L[2].rotation.x = Math.sin(h.stepPhase+Math.PI)*0.55*amp;

  const bob = Math.abs(Math.sin(h.stepPhase))*0.025*amp;
  h.parts.body.position.y = 0.32 + bob;
  h.parts.head.position.y = 0.46 + bob;
  h.parts.bellyM.position.y = 0.25 + bob;

  if(h.animSpeed < 0.08){            // дыхание в покое (п.2)
    const br = 1 + 0.035*Math.sin(time*2.6 + h.phaseOff);
    h.parts.body.scale.set(br, 0.88*br, 1.4*br);
  } else {
    h.parts.body.scale.set(1,0.88,1.4);
  }

  if(h.state==='eat'){               // жуёт, наклонив голову
    h.parts.head.rotation.x = 0.32 + Math.sin(time*11)*0.16;
    h.parts.head.rotation.y = Math.sin(time*3)*0.1;
  } else {
    h.parts.head.rotation.x += (0 - h.parts.head.rotation.x)*Math.min(1,5*dt);
    h.parts.head.rotation.y = Math.sin(time*0.8 + h.phaseOff)*0.15*(1-amp);
  }

  h.earT -= dt;                      // дёрганье ухом
  if(h.earT <= 0){ h.earOn = 0.5; h.earT = rnd(2,6); }
  if(h.earOn > 0){
    h.earOn -= dt;
    h.parts.earL.rotation.z = Math.sin(time*28)*0.4*Math.max(0,h.earOn);
  } else h.parts.earL.rotation.z *= Math.max(0,1-6*dt);
}

/* ============================== ЦИКЛ ====================================== */
const clock = new THREE.Clock();
const plist = document.getElementById('plist');
const dbg   = document.getElementById('debug');
let panelT = 0;

const STATUS = {
  idle:'осматривается', walk:{wheel:'идёт к колесу', tube:'идёт к трубе',
  bowl:'идёт к миске', walk:'гуляет по клетке'},
  wheel_enter:'забирается в колесо', wheel_run:'бежит в колесе ⚙',
  wheel_exit:'вылезает из колеса', tube_walk:'ползёт по трубе', eat:'грызёт зёрна 🌾'
};
function statusText(h){
  const s = STATUS[h.state];
  return typeof s === 'object' ? (s[h.intent]||'идёт…') : s;
}

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);   // дельта ограничена сверху (п.4)
  const time = clock.elapsedTime;

  for(const h of hamsters){
    updateFSM(h, dt);
    const walker = (h.state==='idle'||h.state==='walk'||h.state==='eat');
    if(walker){ collideWheelRect(h.pos); collideTubeCapsule(h.pos); collideBowl(h.pos); }
    clampCage(h.pos);
    h.vy -= 14*dt; h.yOff += h.vy*dt;            // прыжок по клику
    if(h.yOff <= 0){ h.yOff = 0; h.vy = 0; }
    h.group.position.set(h.pos.x, h.pos.y + h.yOff, h.pos.z);
    h.group.rotation.y = h.rotY;
    animateHamster(h, dt, time);
  }
  separateHamsters();

  // Колесо: бегун задаёт ω= v/R (выше), без бегуна — затухание от трения (п.1.1)
  if(!wheelObj.user || wheelObj.user.state!=='wheel_run'){
    wheelObj.omega *= Math.exp(-wheelObj.FRICTION*dt);
    if(Math.abs(wheelObj.omega) < 0.005) wheelObj.omega = 0;
  }
  spinner.rotation.x += wheelObj.omega*dt;

  // панели
  panelT -= dt;
  if(panelT <= 0){
    panelT = 0.15;
    plist.innerHTML = hamsters.map(h =>
      `<div><span class="dot" style="background:#${h.furHex.toString(16).padStart(6,'0')}"></span>`+
      `<b>${h.name}</b> — ${statusText(h)}</div>`).join('');
    const runner = hamsters.find(h=>h.state==='wheel_run');
    const rim = Math.abs(wheelObj.omega)*wheelObj.R;
    if(runner){
      const paw = runner.v;
      const diff = Math.abs(paw-rim)/Math.max(paw,rim,1e-9)*100;
      dbg.textContent =
`⚙ КОЛЕСО: бегун ${runner.name}
  R                 = ${wheelObj.R.toFixed(3)} м
  скорость лап v    = ${paw.toFixed(3)} м/с
  обод |ω|·R        = ${rim.toFixed(3)} м/с
  расхождение       = ${diff.toFixed(2)} %
  ω                 = ${wheelObj.omega.toFixed(3)} рад/с`;
    } else {
      dbg.textContent =
`⚙ КОЛЕСО: пусто (трение)
  R                 = ${wheelObj.R.toFixed(3)} м
  ω                 = ${wheelObj.omega.toFixed(3)} рад/с
  обод |ω|·R        = ${rim.toFixed(3)} м/с`;
    }
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ====================== КЛИК ПО ХОМАКУ → ПРЫЖОК =========================== */
const raycaster = new THREE.Raycaster(), mouse = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', e=>{
  mouse.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1);
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(hamsters.map(h=>h.group), true);
  if(!hits.length) return;
  let o = hits[0].object;
  while(o && o.userData.hIndex === undefined) o = o.parent;
  if(o){ const h = hamsters[o.userData.hIndex]; if(h.yOff<=0) h.vy = 3.4; }
});

addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

/* ======== экспорт наружу для проверки (п.5) =============================== */
window.hamsters = hamsters;
window.wheelObj = wheelObj;
window.tubeObj  = tubeObj;
window.ANIMAL   = {ДЛИНА:ANIMAL_LEN, ВЫСОТА:ANIMAL_H, ШАГ:STEP_LEN, КОЛЕСО_R:WHEEL_R, КОЛЕСО_W:WHEEL_W};
window.getWheelTelemetry = ()=>{
  const r = hamsters.find(h=>h.state==='wheel_run');
  const rim = Math.abs(wheelObj.omega)*wheelObj.R;
  return {runner:r?r.name:null, pawSpeed:r?r.v:0, rimSpeed:rim, omega:wheelObj.omega, R:wheelObj.R};
};
</script>
</body>
</html>
```

## Как выполнены ключевые проверки

| Проверка | Реализация |
|---|---|
| **\|ω\|·R = v лап** | Единственная формула `omega = dir * v / R` в `wheel_run`; панель телеметрии считает расхождение (≈0%, т.к. ω берётся из того же `v`) |
| **Затухание пустого колеса** | `omega *= exp(−k·dt)` при отсутствии бегуна; виден в панели |
| **Нижняя точка обода, габарит < R** | `WHEEL_RUN.y = cy − R`; `WHEEL_R = ANIMAL_H·1.9` + `console.assert` в коде |
| **Ось трубы, вход с торца** | `pos.x` лерпится точно к `tube.cx`; вход только через целевую точку у торца; коллизия-капсула не пускает в бок |
| **Тела предметов** | Прямоугольник колеса, капсула трубы, круг миски — выталкивание по кратчайшей нормали; расталкивание пар хомяков |
| **Фаза от пути** | `stepPhase += dist/STEP_LEN·2π` во всех локомоциях (прогулка, труба, колесо); на месте лапы замирают (`amp→0`) |
| **Без телепортов** | `beginTransition/stepTransition` с smoothstep для входа/выхода из колеса; `wheelObj.user` — один бегун |

Все величины читаются из консоли: `getWheelTelemetry()`, `hamsters[i].pos/state/stepPhase`, `wheelObj.omega`, `tubeObj`.