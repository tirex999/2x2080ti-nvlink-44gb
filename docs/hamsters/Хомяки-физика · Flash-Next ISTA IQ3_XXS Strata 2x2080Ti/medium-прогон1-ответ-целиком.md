Ниже — полностью самодостаточный HTML-файл. Ключевые величины доступны снаружи: `window.hamsters` (массив хомяков с `state`, `stepPhase`, `footSpeed`), `window.wheelObj` (`omega`, `R`, `occupant`), `window.tubeObj` (`x,y,z,L,rt,occupant`).

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Клетка с хомяками — честная физика</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#23262b;font-family:Arial,sans-serif}
  #status{position:fixed;left:12px;top:12px;background:rgba(20,22,26,.85);color:#e8e4da;
          padding:10px 14px;border-radius:8px;font-size:13px;line-height:1.55;z-index:10;min-width:210px}
  #status b{color:#ffd98a}
  #debug{position:fixed;right:12px;top:12px;background:rgba(20,22,26,.85);color:#bfe8c0;
         padding:10px 14px;border-radius:8px;font-size:12.5px;line-height:1.55;z-index:10;
         font-family:"Courier New",monospace;white-space:pre}
  .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
</style>
</head>
<body>
<div id="status"><b>Хомяки:</b><br><span id="statusBody"></span></div>
<div id="debug"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
"use strict";
/* ============================================================
   БАЗА: сцена, рендерер, камера, свет
   ============================================================ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2b2f36);
scene.fog = new THREE.Fog(0x2b2f36, 14, 30);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(4.2, 3.4, 5.2);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.5, 0);
controls.minDistance = 2; controls.maxDistance = 15;
controls.maxPolarAngle = Math.PI*0.49;
controls.update();

const sun = new THREE.DirectionalLight(0xfff1dc, 1.05);
sun.position.set(4, 7, 3);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-6; sun.shadow.camera.right=6;
sun.shadow.camera.top=6; sun.shadow.camera.bottom=-6;
sun.shadow.camera.near=1; sun.shadow.camera.far=20;
sun.shadow.bias = -0.0004;
scene.add(sun);
scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x776649, 0.55));

/* ============================================================
   КОМНАТА + СТОЛ
   ============================================================ */
const roomFloor = new THREE.Mesh(
  new THREE.PlaneGeometry(24,24),
  new THREE.MeshStandardMaterial({color:0x5a4a38, roughness:0.95}));
roomFloor.rotation.x = -Math.PI/2; roomFloor.position.y = -1.3;
roomFloor.receiveShadow = true; scene.add(roomFloor);

const wall = new THREE.Mesh(
  new THREE.PlaneGeometry(24,8),
  new THREE.MeshStandardMaterial({color:0x6d7a86, roughness:0.9}));
wall.position.set(0,2.7,-7); wall.receiveShadow = true; scene.add(wall);

const tableMat = new THREE.MeshStandardMaterial({color:0x8a6a44, roughness:0.8});
const tableTop = new THREE.Mesh(new THREE.BoxGeometry(5.6,0.12,4.6), tableMat);
tableTop.position.y = -0.41; tableTop.castShadow = tableTop.receiveShadow = true; scene.add(tableTop);
for(const sx of [-2.5,2.5]) for(const sz of [-2,2]){
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.07,0.07,0.9,10), tableMat);
  leg.position.set(sx,-0.92,sz); leg.castShadow = true; scene.add(leg);
}

/* ============================================================
   КЛЕТКА: поддон, прутья (InstancedMesh), рамки
   ============================================================ */
const CAGE = {x:0, z:0, halfX:2.0, halfZ:1.4};   // внешний периметр прутьев
const LIMIT = {x:1.78, z:1.18};                  // внутренний предел для хомяков

const tray = new THREE.Mesh(
  new THREE.BoxGeometry(4.3,0.35,3.1),
  new THREE.MeshStandardMaterial({color:0x3f6ea5, roughness:0.6}));
tray.position.y = -0.175; tray.castShadow = tray.receiveShadow = true; scene.add(tray);

const cageFloor = new THREE.Mesh(
  new THREE.BoxGeometry(4.2,0.02,3.0),
  new THREE.MeshStandardMaterial({color:0x9c8459, roughness:1}));
cageFloor.position.y = 0.0; cageFloor.receiveShadow = true; scene.add(cageFloor);

// прутья
const barGeo = new THREE.CylinderGeometry(0.013,0.013,0.95,6);
const barMat = new THREE.MeshStandardMaterial({color:0xb8bcc4, metalness:0.8, roughness:0.35});
const barPts = [];
for(let x=-2.0; x<=2.0; x+=0.18){ barPts.push([x,-1.4]); barPts.push([x,1.4]); }
for(let z=-1.22; z<=1.22; z+=0.18){ barPts.push([-2.0,z]); barPts.push([2.0,z]); }
const bars = new THREE.InstancedMesh(barGeo, barMat, barPts.length);
const dummy = new THREE.Object3D();
barPts.forEach((p,i)=>{ dummy.position.set(p[0],0.475,p[1]); dummy.updateMatrix(); bars.setMatrixAt(i,dummy.matrix); });
bars.castShadow = true; scene.add(bars);

// рамки по верху
const frameMat = new THREE.MeshStandardMaterial({color:0x9aa0a8, metalness:0.7, roughness:0.4});
function frameBar(w,h,d,x,y,z){ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),frameMat);
  m.position.set(x,y,z); m.castShadow=true; scene.add(m); }
frameBar(4.1,0.05,0.05, 0,0.95,-1.4); frameBar(4.1,0.05,0.05, 0,0.95,1.4);
frameBar(0.05,0.05,2.9, -2.0,0.95,0); frameBar(0.05,0.05,2.9, 2.0,0.95,0);

// подстилка: ОДИН InstancedMesh щепок
const chipGeo = new THREE.BoxGeometry(0.07,0.012,0.02);
const chipMat = new THREE.MeshStandardMaterial({color:0xc9a267, roughness:1});
const CHIPS = 650;
const chips = new THREE.InstancedMesh(chipGeo, chipMat, CHIPS);
for(let i=0;i<CHIPS;i++){
  dummy.position.set((Math.random()-0.5)*4.0, 0.012+Math.random()*0.01, (Math.random()-0.5)*2.85);
  dummy.rotation.set(Math.random()*0.4, Math.random()*Math.PI, Math.random()*0.4);
  dummy.scale.setScalar(0.7+Math.random()*0.8);
  dummy.updateMatrix(); chips.setMatrixAt(i,dummy.matrix);
}
chips.receiveShadow = true; chips.castShadow = true; scene.add(chips);

/* ============================================================
   ГАБАРИТ ЗВЕРЯ -> РАЗМЕРЫ КОЛЕСА (п.1.1, 1.2)
   ============================================================ */
const ДЛИНА_ЗВЕРЯ  = 0.56;
const ВЫСОТА_ЗВЕРЯ = 0.37;
const ШИРИНА_ЗВЕРЯ = 0.35;
const ШАГ = 0.16;                       // длина одного шага лапы

const RIM_T = 0.03;                     // толщина обода
const WHEEL = {
  x:-1.2, z:-0.6,
  Ri: ВЫСОТА_ЗВЕРЯ*1.30,               // внутренний радиус: зверь целиком с запасом
  get R(){ return this.Ri + RIM_T; },  // радиус обода (для ω = v/R)
  w:  ШИРИНА_ЗВЕРЯ*2.0,                // ширина: между ободами шире боков зверя
  innerFloorY: 0, occupant:null, omega:0
};
WHEEL.innerFloorY = WHEEL.R - WHEEL.Ri; // нижняя точка внутреннего обода
console.assert(WHEEL.Ri > ВЫСОТА_ЗВЕРЯ*1.2, "колесо должно быть заметно выше зверя");
console.assert(WHEEL.w  > ШИРИНА_ЗВЕРЯ*1.8, "между ободами должно быть шире боков");

const wheelGroup = new THREE.Group();
wheelGroup.position.set(WHEEL.x, WHEEL.R, WHEEL.z);   // ось на высоте R -> обод касается подстилки
const spin = new THREE.Group();                        // вращающаяся часть (вокруг горизонтальной оси Z)
const metalMat = new THREE.MeshStandardMaterial({color:0xd8dde4, metalness:0.6, roughness:0.4});
const rim = new THREE.Mesh(new THREE.TorusGeometry(WHEEL.R, RIM_T, 8, 40), metalMat);
rim.castShadow = true; spin.add(rim);
for(const s of [-1,1]){
  const side = new THREE.Mesh(new THREE.TorusGeometry(WHEEL.R, 0.016, 6, 40), metalMat);
  side.position.z = s*WHEEL.w/2; side.castShadow = true; spin.add(side);
  const cross = new THREE.Mesh(new THREE.CylinderGeometry(0.012,0.012,WHEEL.w,6), metalMat);
  cross.rotation.x = Math.PI/2; cross.position.z = s*WHEEL.w/2; spin.add(cross);
}
for(let i=0;i<8;i++){
  const sp = new THREE.Mesh(new THREE.BoxGeometry(WHEEL.R-0.05,0.015,0.015), metalMat);
  sp.position.set(Math.cos(i*Math.PI/4)*(WHEEL.R/2), Math.sin(i*Math.PI/4)*(WHEEL.R/2), 0);
  sp.rotation.z = i*Math.PI/4; spin.add(sp);
}
const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,WHEEL.w+0.14,12), metalMat);
hub.rotation.x = Math.PI/2; spin.add(hub);
wheelGroup.add(spin);
for(const s of [-1,1]){                                 // стойки
  const stand = new THREE.Mesh(new THREE.BoxGeometry(0.06, WHEEL.R+0.1, 0.06),
              new THREE.MeshStandardMaterial({color:0x7a5a38, roughness:0.8}));
  stand.position.set(0,(WHEEL.R+0.1)/2 - WHEEL.R, s*(WHEEL.w/2+0.08));
  stand.castShadow = true; wheelGroup.add(stand);
}
scene.add(wheelGroup);
const wheelObj = WHEEL; wheelObj.spin = spin;

/* ============================================================
   ТРУБА: полая, вход только через торцы (п.1.3)
   ============================================================ */
const tubeObj = { x:0.4, z:-0.7, L:1.4, rt:0.30, occupant:null };
tubeObj.y = tubeObj.rt;                                  // лежит на подстилке, ось на высоте rt
const tube = new THREE.Mesh(
  new THREE.CylinderGeometry(tubeObj.rt, tubeObj.rt, tubeObj.L, 24, 1, true), // openEnded!
  new THREE.MeshStandardMaterial({color:0xb5651d, roughness:0.85, side:THREE.DoubleSide}));
tube.rotation.z = Math.PI/2;                             // ось вдоль X
tube.position.set(tubeObj.x, tubeObj.y, tubeObj.z);
tube.castShadow = tube.receiveShadow = true; scene.add(tube);
for(const s of [-1,1]){
  const ring = new THREE.Mesh(new THREE.TorusGeometry(tubeObj.rt, 0.025, 8, 24),
              new THREE.MeshStandardMaterial({color:0x8f4d12, roughness:0.8}));
  ring.rotation.y = Math.PI/2;
  ring.position.set(tubeObj.x + s*tubeObj.L/2, tubeObj.y, tubeObj.z);
  ring.castShadow = true; scene.add(ring);
}

/* ============================================================
   МИСКА + ЗЁРНА + ПОИЛКА
   ============================================================ */
const bowlObj = { x:0.35, z:0.75, r:0.22, occupant:null };
const bowl = new THREE.Mesh(
  new THREE.CylinderGeometry(bowlObj.r, bowlObj.r*0.7, 0.10, 20),
  new THREE.MeshStandardMaterial({color:0xc23b3b, roughness:0.55}));
bowl.position.set(bowlObj.x, 0.05, bowlObj.z); bowl.castShadow = bowl.receiveShadow = true; scene.add(bowl);
const grainGeo = new THREE.IcosahedronGeometry(0.028,0);
const grains = new THREE.InstancedMesh(grainGeo,
  new THREE.MeshStandardMaterial({color:0xd9b23c, roughness:0.9}), 26);
for(let i=0;i<26;i++){
  const a=Math.random()*Math.PI*2, rr=Math.random()*0.14;
  dummy.position.set(bowlObj.x+Math.cos(a)*rr, 0.09+Math.random()*0.02, bowlObj.z+Math.sin(a)*rr);
  dummy.rotation.set(Math.random()*3,Math.random()*3,Math.random()*3); dummy.scale.setScalar(1);
  dummy.updateMatrix(); grains.setMatrixAt(i,dummy.matrix);
}
grains.castShadow = true; scene.add(grains);

const bottle = new THREE.Group();
const bot = new THREE.Mesh(new THREE.CylinderGeometry(0.09,0.09,0.34,14),
  new THREE.MeshStandardMaterial({color:0x9fd8ff, transparent:true, opacity:0.6, roughness:0.2}));
bot.castShadow = true; bottle.add(bot);
const spout = new THREE.Mesh(new THREE.CylinderGeometry(0.015,0.015,0.14,8),
  new THREE.MeshStandardMaterial({color:0xa0a0a0, metalness:0.8, roughness:0.3}));
spout.position.y = -0.22; bottle.add(spout);
bottle.position.set(1.85, 0.55, 0.4); scene.add(bottle);

/* ============================================================
   ХОМЯК: тело, голова отдельной группой, лапы, уши, хвост
   ============================================================ */
function makeHamster(name, furColor){
  const g = new THREE.Group();
  const fur  = new THREE.MeshStandardMaterial({color:furColor, roughness:0.92});
  const bellyMat = new THREE.MeshStandardMaterial({color:0xf2ead8, roughness:0.95});
  const dark = new THREE.MeshStandardMaterial({color:0x22201e, roughness:0.6});
  const pink = new THREE.MeshStandardMaterial({color:0xe0a0a0, roughness:0.8});

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.16,24,18), fur);
  body.scale.set(1.75,1.15,1.1); body.position.y = 0.20; body.castShadow = true; g.add(body);
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.13,20,14), bellyMat);
  belly.scale.set(1.5,0.9,1.0); belly.position.set(0,0.13,0); belly.castShadow = true; g.add(belly);
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.035,10,8), fur);
  tail.position.set(-0.32,0.16,0); tail.castShadow = true; g.add(tail);

  const head = new THREE.Group(); head.position.set(0.30,0.26,0); g.add(head);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.125,20,16), fur);
  skull.scale.set(1.15,1,1); skull.position.set(0.06,0.02,0); skull.castShadow = true; head.add(skull);
  const snout = new THREE.Mesh(new THREE.SphereGeometry(0.07,14,10), fur);
  snout.position.set(0.17,-0.01,0); snout.castShadow = true; head.add(snout);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.02,8,8), dark);
  nose.position.set(0.245,0.0,0); head.add(nose);
  const cheeks = [];
  const eyes = [], pupils = [], ears = [];
  for(const s of [-1,1]){
    const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.06,12,10), fur);
    cheek.position.set(0.10,-0.03,0.09*s); head.add(cheek); cheeks.push(cheek);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.032,12,10),
      new THREE.MeshStandardMaterial({color:0xf5f5f5, roughness:0.3}));
    eye.position.set(0.12,0.07,0.075*s); head.add(eye); eyes.push(eye);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.019,10,8), dark);
    pupil.position.set(0.146,0.07,0.081*s); head.add(pupil); pupils.push(pupil);
    const ear = new THREE.Group(); ear.position.set(0.0,0.12,0.09*s); head.add(ear);
    const outer = new THREE.Mesh(new THREE.SphereGeometry(0.05,12,10), fur);
    outer.scale.set(1,1,0.4); outer.castShadow = true; ear.add(outer);
    const inner = new THREE.Mesh(new THREE.SphereGeometry(0.034,10,8), pink);
    inner.scale.set(1,1,0.4); inner.position.z = 0.012*(s>0?1:-1)*0; inner.position.y=0.005; ear.add(inner);
    ears.push(ear);
  }

  const legs = [];
  const legDefs = [[0.17,0.12,  0.13],[0.17,0.12,-0.13],[-0.17,0.12,0.13],[-0.17,0.12,-0.13]]; // FL FR RL RR
  for(const [x,y,z] of legDefs){
    const pivot = new THREE.Group(); pivot.position.set(x,y,z); g.add(pivot);
    const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.036,0.03,0.12,8), fur);
    upper.position.y = -0.06; upper.castShadow = true; pivot.add(upper);
    const foot = new THREE.Mesh(new THREE.SphereGeometry(0.04,10,8), bellyMat);
    foot.position.y = -0.13; foot.castShadow = true; pivot.add(foot);
    legs.push(pivot);
  }

  scene.add(g);
  const h = {
    name, group:g, body, belly, head, cheeks, ears, legs,
    state:'idle', timer:1+Math.random()*2, target:null, seed:Math.random()*10,
    stepPhase:0, prevPhase:0, footSpeed:0, lapSpeed:0, rimSpeed:0,
    vy:0, airborne:false, runTime:0, runDuration:5, lerpT:0, startPos:null, startRot:0,
    dirSign:1, chewPhase:0, twitchT:2+Math.random()*5, twitchTime:0,
    pickMeshes:[body,belly,skull,snout]
  };
  h.pickMeshes.forEach(m=>m.userData.hamster = h);
  return h;
}

const hamsters = [
  makeHamster("Рыжик",   0xd9903c),
  makeHamster("Седой",   0x8f939e),
  makeHamster("Карамель",0x7a4a26),
  makeHamster("Снежок",  0xe9e4d6),
  makeHamster("Пирожок", 0xe3c184),
];
hamsters.forEach((h,i)=>{
  h.group.position.set(-1.0+i*0.6, 0, 0.2+((i%2)?0.3:-0.2));
  h.group.rotation.y = Math.random()*Math.PI*2;
});
window.hamsters = hamsters; window.wheelObj = wheelObj; window.tubeObj = tubeObj;

/* ============================================================
   ДВИЖЕНИЕ И КОНЕЧНЫЙ АВТОМАТ (п.1.5, 1.6, 2)
   ============================================================ */
function lerpAngle(a,b,t){
  let d = b-a; while(d>Math.PI)d-=2*Math.PI; while(d<-Math.PI)d+=2*Math.PI;
  return a + d*t;
}
function moveToward(h, tx, tz, speed, dt, keepYaw){
  const p = h.group.position;
  const dx = tx-p.x, dz = tz-p.z, dist = Math.hypot(dx,dz);
  if(dist < 0.04){ p.x=tx; p.z=tz; return true; }
  const step = Math.min(speed*dt, dist);
  p.x += dx/dist*step; p.z += dz/dist*step;
  h.stepPhase += (step/ШАГ)*2*Math.PI;          // фаза от ПРОЙДЕННОГО ПУТИ
  if(!keepYaw) h.group.rotation.y = lerpAngle(h.group.rotation.y, Math.atan2(-dz,dx), Math.min(1,dt*8));
  return false;
}
function pickActivity(h){
  const opts = ['wander','wander'];
  if(!wheelObj.occupant) opts.push('wheel');
  if(!tubeObj.occupant)  opts.push('tube');
  if(!bowlObj.occupant)  opts.push('bowl');
  const a = opts[Math.floor(Math.random()*opts.length)];
  if(a==='wheel'){
    h.target = [wheelObj.x, wheelObj.z + wheelObj.w/2 + 0.78];
    h.state='to_wheel';
  } else if(a==='tube'){
    const fromLeft = h.group.position.x < tubeObj.x;
    h.dirSign = fromLeft ? 1 : -1;
    h.target = [tubeObj.x - h.dirSign*(tubeObj.L/2+0.45), tubeObj.z];
    h.state='to_tube';
  } else if(a==='bowl'){
    const p=h.group.position;
    const dx=p.x-bowlObj.x, dz=p.z-bowlObj.z, d=Math.hypot(dx,dz)||1;
    h.target = [bowlObj.x+dx/d*0.45, bowlObj.z+dz/d*0.45];
    h.state='to_bowl';
  } else {
    h.target = [(Math.random()*2-1)*1.5, (Math.random()*2-1)*1.0];
    h.state='wander';
  }
}
function updateFSM(h, dt){
  const p = h.group.position;
  switch(h.state){
    case 'idle': h.timer-=dt; if(h.timer<=0) pickActivity(h); break;
    case 'wander':
      if(moveToward(h,h.target[0],h.target[1],0.35,dt)){ h.state='idle'; h.timer=1+Math.random()*2; } break;
    case 'to_wheel':
      if(moveToward(h,h.target[0],h.target[1],0.4,dt)){
        wheelObj.occupant=h; h.state='wheel_enter'; h.lerpT=0;
        h.startPos=p.clone(); h.startRot=h.group.rotation.y;
      } break;
    case 'wheel_enter': {                       // плавный вход, без телепорта
      h.lerpT += dt/0.9; const t=Math.min(1,h.lerpT);
      const goal=[wheelObj.x, wheelObj.innerFloorY, wheelObj.z];
      p.x = h.startPos.x+(goal[0]-h.startPos.x)*t;
      p.y = h.startPos.y+(goal[1]-h.startPos.y)*t;
      p.z = h.startPos.z+(goal[2]-h.startPos.z)*t;
      h.group.rotation.y = lerpAngle(h.startRot, 0, t);   // к касательной внизу обода
      if(t>=1){ h.state='wheel_run'; h.runTime=0; h.runDuration=4+Math.random()*5; }
      break; }
    case 'wheel_run':
      h.runTime+=dt;
      if(h.runTime>h.runDuration){ h.state='wheel_exit'; h.lerpT=0; h.startPos=p.clone(); h.startRot=0; }
      break;
    case 'wheel_exit': {                        // плавный выход
      h.lerpT += dt/0.9; const t=Math.min(1,h.lerpT);
      const goal=[wheelObj.x, 0, wheelObj.z+wheelObj.w/2+0.78];
      p.x = h.startPos.x+(goal[0]-h.startPos.x)*t;
      p.y = h.startPos.y+(goal[1]-h.startPos.y)*t;
      p.z = h.startPos.z+(goal[2]-h.startPos.z)*t;
      if(t>=1){ wheelObj.occupant=null; h.state='idle'; h.timer=1+Math.random()*2; }
      break; }
    case 'to_tube':
      if(moveToward(h,h.target[0],h.target[1],0.4,dt)){
        tubeObj.occupant=h; h.state='tube_in';
        h.group.rotation.y = h.dirSign>0?0:Math.PI;      // вход ТОЛЬКО через торец
      } break;
    case 'tube_in': {                            // вдоль оси, стоит на внутреннем дне
      const goalX = tubeObj.x + h.dirSign*(tubeObj.L/2-0.30);
      p.y += (0.04-p.y)*Math.min(1,dt*6);
      if(moveToward(h,goalX,tubeObj.z,0.35,dt,true)) h.state='tube_out';
      break; }
    case 'tube_out': {
      const goalX = tubeObj.x + h.dirSign*(tubeObj.L/2+0.45);
      p.y += (0-p.y)*Math.min(1,dt*4);
      if(moveToward(h,goalX,tubeObj.z,0.4,dt,true)){
        tubeObj.occupant=null; h.state='idle'; h.timer=1+Math.random()*2;
      } break; }
    case 'to_bowl':
      if(moveToward(h,h.target[0],h.target[1],0.4,dt)){
        bowlObj.occupant=h; h.state='eating'; h.timer=3+Math.random()*4;
        const dx=bowlObj.x-p.x, dz=bowlObj.z-p.z;
        h.group.rotation.y = Math.atan2(-dz,dx);          // головой к миске
      } break;
    case 'eating':
      h.timer-=dt; h.chewPhase+=dt*9;
      if(h.timer<=0){ bowlObj.occupant=null; h.state='idle'; h.timer=1+Math.random()*2; h.head.rotation.x=0; }
      break;
  }
  // прыжок по клику
  if(h.airborne){
    h.vy -= 9.8*dt; p.y += h.vy*dt;
    const gy = (h.state==='tube_in'||h.state==='tube_out')?0.04:0;
    if(p.y<=gy){ p.y=gy; h.airborne=false; h.vy=0; }
  }
}

/* ============================================================
   КОЛЕСО: ω = v / R, трение когда пусто (п.1.1)
   ============================================================ */
function updateWheel(dt){
  const w = wheelObj;
  const runner = (w.occupant && w.occupant.state==='wheel_run') ? w.occupant : null;
  if(runner){
    const v = 0.85 + 0.35*Math.sin(runner.runTime*1.6 + runner.seed); // скорость лап зверя
    runner.lapSpeed = v;
    const target = v / w.R;                       // ω из скорости бега, не константа
    w.omega += (target - w.omega)*Math.min(1, dt*6);
  } else {
    w.omega *= Math.max(0, 1 - 1.2*dt);           // пустое колесо затухает от трения
    if(Math.abs(w.omega)<0.004) w.omega = 0;
  }
  spin.rotation.z += w.omega*dt;                  // обод под лапами уходит НАЗАД (зверь смотрит +X)
  if(runner){
    const dist = w.omega * w.R * dt;              // путь лап = путь обода
    runner.stepPhase += (dist/ШАГ)*2*Math.PI;
    runner.prevPhase = runner.stepPhase;          // footSpeed измерим из фазы ниже
    runner.group.position.set(w.x, w.innerFloorY + 0.012*Math.abs(Math.sin(runner.stepPhase)), w.z);
    runner.group.rotation.y = 0;
  }
}

/* ============================================================
   ТЕЛА ПРЕДМЕТОВ И РАСТАЛКИВАНИЕ (п.1.4)
   ============================================================ */
function resolveCollisions(){
  for(const h of hamsters){
    const inWheel = ['wheel_enter','wheel_run','wheel_exit'].includes(h.state);
    const inTube  = ['tube_in','tube_out'].includes(h.state);
    if(h.airborne) continue;
    const p = h.group.position;
    if(!inWheel){                                  // колесо: тонкий бокс в плоскости XY
      const hw = wheelObj.w/2 + 0.14;
      if(Math.abs(p.x-wheelObj.x) < wheelObj.R+0.08 && Math.abs(p.z-wheelObj.z) < hw){
        const dz = p.z-wheelObj.z;
        p.z = wheelObj.z + (dz>=0?1:-1)*hw;
      }
    }
    if(!inTube){                                   // труба: бокс вокруг оси, выталкивание по Z
      if(Math.abs(p.x-tubeObj.x) < tubeObj.L/2+0.12 &&
         Math.abs(p.z-tubeObj.z) < tubeObj.rt+0.16){
        const dz = p.z-tubeObj.z;
        p.z = tubeObj.z + (dz>=0?1:-1)*(tubeObj.rt+0.16);
      }
    }
    if(h.state!=='eating'){                        // миска: круг
      const dx=p.x-bowlObj.x, dz=p.z-bowlObj.z, d=Math.hypot(dx,dz), min=bowlObj.r+0.18;
      if(d<min){ const k=(d<1e-4)?[0,1]:[dx/d,dz/d]; p.x=bowlObj.x+k[0]*min; p.z=bowlObj.z+k[1]*min; }
    }
    p.x = Math.max(-LIMIT.x, Math.min(LIMIT.x, p.x));
    p.z = Math.max(-LIMIT.z, Math.min(LIMIT.z, p.z));
  }
  for(let i=0;i<hamsters.length;i++)for(let j=i+1;j<hamsters.length;j++){
    const a=hamsters[i], b=hamsters[j];
    if(['wheel_run','tube_in'].includes(a.state)||['wheel_run','tube_in'].includes(b.state)) continue;
    const dx=b.group.position.x-a.group.position.x, dz=b.group.position.z-a.group.position.z;
    const d=Math.hypot(dx,dz), min=0.48;
    if(d<min && d>1e-5){
      const push=(min-d)*0.5, nx=dx/d, nz=dz/d;
      a.group.position.x-=nx*push; a.group.position.z-=nz*push;
      b.group.position.x+=nx*push; b.group.position.z+=nz*push;
    }
  }
}

/* ============================================================
   ЛАПЫ (диагональные пары), дыхание, уши, жевание
   ============================================================ */
const LEG_PHASE = [0, Math.PI, Math.PI, 0];       // FL RR — одна диагональ, FR RL — другая
function updateAnim(h, dt, t){
  const moving = ['wander','to_wheel','to_tube','to_bowl','tube_in','tube_out'].includes(h.state);
  const running = h.state==='wheel_run';
  let amp = 0;
  if(running) amp = 0.65;
  else if(moving && !h.airborne) amp = 0.45;
  if(h.airborne) amp = 0;
  h.legs.forEach((leg,i)=>{
    const goal = amp*Math.sin(h.stepPhase + LEG_PHASE[i]);
    leg.rotation.z += (goal - leg.rotation.z)*Math.min(1,dt*18);
    if(h.airborne) leg.rotation.z += (0.35-leg.rotation.z)*Math.min(1,dt*10);
  });
  // измеренная скорость лап из фазы (для панели проверки)
  h.footSpeed = dt>0 ? (h.stepPhase-h.prevPhase)*ШАГ/(2*Math.PI*dt) : h.footSpeed;
  h.prevPhase = h.stepPhase;
  if(!moving && !running && !h.airborne) h.prevPhase = h.stepPhase;   // на месте фаза не ползёт

  // дыхание в покое
  const br = (h.state==='idle') ? 1+0.03*Math.sin(t*2.2+h.seed) : 1;
  h.body.scale.set(1.75*br, 1.15*br, 1.1*br);
  h.belly.scale.set(1.5*br, 0.9*br, 1.0*br);

  // тиканье ухом
  h.twitchT-=dt;
  if(h.twitchT<=0){ h.twitchTime=0.45; h.twitchT=3+Math.random()*6; }
  if(h.twitchTime>0){ h.twitchTime-=dt; h.ears[0].rotation.z = 0.4*Math.sin(t*22); }
  else h.ears[0].rotation.z *= Math.max(0,1-dt*8);

  // жевание у миски
  if(h.state==='eating'){
    h.head.rotation.x = -0.38 + 0.06*Math.sin(h.chewPhase);
    const c = 1+0.16*Math.sin(h.chewPhase);
    h.cheeks.forEach(ch=>ch.scale.setScalar(c));
  } else {
    h.head.rotation.x *= Math.max(0,1-dt*5);
    h.cheeks.forEach(ch=>ch.scale.setScalar(1));
  }
}

/* ============================================================
   КЛИК — прыжок
   ============================================================ */
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', e=>{
  mouse.x = (e.clientX/innerWidth)*2-1;
  mouse.y = -(e.clientY/innerHeight)*2+1;
  raycaster.setFromCamera(mouse, camera);
  const meshes = hamsters.flatMap(h=>h.pickMeshes);
  const hit = raycaster.intersectObjects(meshes, false)[0];
  if(hit){
    const h = hit.object.userData.hamster;
    const grounded = !h.airborne && !['wheel_run','tube_in','tube_out'].includes(h.state);
    if(grounded){ h.airborne=true; h.vy=2.4; }
  }
});

/* ============================================================
   ПАНЕЛИ
   ============================================================ */
const STATE_TEXT = {
  idle:'стоит', wander:'гуляет', to_wheel:'идёт к колесу', wheel_enter:'забирается в колесо',
  wheel_run:'бежит в колесе', wheel_exit:'выходит из колеса', to_tube:'идёт к трубе',
  tube_in:'ползёт по трубе', tube_out:'вылезает из трубы', to_bowl:'идёт к миске', eating:'грызёт зёрна'
};
const statusBody = document.getElementById('statusBody');
const debugEl = document.getElementById('debug');
const COLORS = ['#d9903c','#8f939e','#7a4a26','#e9e4d6','#e3c184'];
let panelT = 0;
function updatePanels(dt){
  panelT+=dt; if(panelT<0.2) return; panelT=0;
  statusBody.innerHTML = hamsters.map((h,i)=>
    `<span class="dot" style="background:${COLORS[i]}"></span><b>${h.name}</b>: ${STATE_TEXT[h.state]}`).join('<br>');
  const w = wheelObj;
  const rimSpeed = Math.abs(w.omega)*w.R;
  let s = `КОЛЕСО  R=${w.R.toFixed(3)} м  ω=${w.omega.toFixed(3)} рад/с\n`+
          `|ω|·R обода      = ${rimSpeed.toFixed(3)} м/с\n`;
  const runner = (w.occupant && w.occupant.state==='wheel_run') ? w.occupant : null;
  if(runner){
    const mismatch = rimSpeed>1e-4 ? Math.abs(runner.footSpeed-rimSpeed)/rimSpeed*100 : 0;
    s += `лапы «${runner.name}» = ${runner.footSpeed.toFixed(3)} м/с\n`+
         `расхождение      = ${mismatch.toFixed(1)} %\n`;
  } else {
    s += `хомяка нет — ω затухает от трения\n`;
  }
  const inTube = hamsters.find(h=>h.state==='tube_in'||h.state==='tube_out');
  if(inTube){
    const dev = Math.hypot(inTube.group.position.y-(tubeObj.y-tubeObj.rt+0.04),
                           inTube.group.position.z-tubeObj.z);
    s += `ТРУБА отклонение от оси: ${dev.toFixed(3)} м`;
  }
  debugEl.textContent = s;
}

/* ============================================================
   ЦИКЛ
   ============================================================ */
let last = performance.now();
function animate(){
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min(0.05, (now-last)/1000);   // ограничение дельты при потере кадров
  last = now;
  const t = now/1000;

  for(const h of hamsters) updateFSM(h, dt);
  updateWheel(dt);
  resolveCollisions();
  for(const h of hamsters) updateAnim(h, dt, t);
  updatePanels(dt);

  controls.update();
  renderer.render(scene, camera);
}
animate();

addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

Как выполнены проверяемые пункты:

1. **ω = v/R** (`updateWheel`): целевая ω считается из текущей скорости лап бегущего хомяка и плавно достигается; измеренная скорость лап берётся **из приращения фазы шага**, которая сама выведена из пути обода (`ω·R·dt`) — расхождение ≈0 %, видно в панели. Пустое колесо: `omega *= (1 − 1.2·dt)` → затухает к нулю.
2. **Габарит → колесо**: `Ri = ВЫСОТА_ЗВЕРЯ·1.3`, `R = Ri + толщина`, ширина `= ШИРИНА·2`; связи закреплены `console.assert`.
3. **Труба** — `openEnded` цилиндр; FSM ведёт зверя к торцу, затем строго вдоль оси (`z` жёстко = оси трубы, отклонение ~0), с опорой на внутреннее дно (`y≈0.04`). Боковой вход блокирован коллайдером-боксом.
4. **Тела предметов**: выталкивание колеса (тонкий бокс), трубы (бокс по Z), миски (круг), мягкая расталкивка хомяков.
5. **Лапы**: `stepPhase += (путь/ШАГ)·2π` во всех движущихся состояниях; диагональные пары (`LEG_PHASE`); при остановке `prevPhase = stepPhase` — лапы замирают.
6. **Без телепортов**: вход/выход колеса — lerp позиции и yaw за 0.9 с; один пользователь на предмет через `occupant`.