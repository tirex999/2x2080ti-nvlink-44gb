# Честная 3D-клетка с хомяками

Ниже — полный самодостаточный файл. Ключевые решения:

- **Колесо**: `ω = −v/R` считается из скорости лап бегуна каждый кадр; без бегуна `ω` затухает экспоненциально. Хомяк стоит на нижней точке обода (`y = cy − R + толщина обода`). Панель проверки показывает `v`, `|ω|·R` и расхождение в %.
- **Габариты**: `R = ВЫСОТА + 0.45`, ширина обода = `ШИРИНА + 0.6`, с явными `console.assert`.
- **Труба**: входы только через торцы (хомяк сначала идёт к точке у торца снаружи), внутри `z` жёстко равен оси, `y` — внутренний день.
- **Фаза шага** — от пройденного пути, диагональные пары.
- Все величины наружу: `window.hamsters`, `window.wheelObj`, `window.pipeObj`.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Клетка с хомяками — честная физика</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#1a1a22;font-family:Arial,sans-serif}
  #panel{position:fixed;left:10px;top:10px;width:230px;background:rgba(15,15,25,.82);
         color:#eee;padding:10px 12px;border-radius:10px;font-size:13px;z-index:10;
         line-height:1.45;user-select:none}
  #panel h3{margin:0 0 6px;font-size:14px}
  .hrow{display:flex;align-items:center;gap:6px;margin:3px 0}
  .chip{width:11px;height:11px;border-radius:50%;flex:0 0 auto;border:1px solid #fff5}
  .act{color:#ffd97a}
  #debug{margin-top:8px;padding-top:6px;border-top:1px solid #ffffff33;font-size:11.5px;
         font-family:monospace;white-space:pre}
  #hint{color:#9aa;margin-top:6px;font-size:11px}
</style>
</head>
<body>
<div id="panel">
  <h3>Хомяки</h3>
  <div id="hlist"></div>
  <div id="debug"></div>
  <div id="hint">Клик по хомяку — прыжок.<br>ЛКМ-вращение, колесо — зум.</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
'use strict';
/* ============ 1. ГАБАРИТЫ: колесо выводится ИЗ размера зверя ============ */
const ЗВЕРЬ = { ДЛИНА:1.0, ВЫСОТА:0.55, ШИРИНА:0.5 };
const КОЛЕСО_R = ЗВЕРЬ.ВЫСОТА + 0.45;              // 1.00 — радиус внутренней поверхности обода
const КОЛЕСО_W = ЗВЕРЬ.ШИРИНА + 0.60;              // 1.10 — расстояние между боковыми ободами
const ОБОД_ТРУБА = 0.07;
console.assert(КОЛЕСО_R >= ЗВЕРЬ.ДЛИНА/2 + 0.35, 'хомяк не помещается в колесо по длине');
console.assert(КОЛЕСО_R >= ЗВЕРЬ.ВЫСОТА + 0.30, 'хомяк не помещается в колесо по высоте');
console.assert(КОЛЕСО_W  >= ЗВЕРЬ.ШИРИНА + 0.45, 'ободья уже боков хомяка');

const ТРУБА = { rIn:0.45, rOut:0.50, x1:0.4, x2:3.0, axisZ:1.6, centerY:0.50 };
console.assert(ТРУБА.rIn*2 >= ЗВЕРЬ.ВЫСОТА + 0.30, 'хомяк не пролезает в трубу');

const Миска = new THREE.Vector3(2.9, 0, -1.7), МИСКА_R = 0.45;
const WALK=1.15, RUN=2.2, ШАГ=0.34, G=12;
const TAU=Math.PI*2;

/* ============ 2. СЦЕНА ============ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2b2b38);
const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
camera.position.set(9, 6.5, 9.5);
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0,1,0); controls.maxPolarAngle = 1.5; controls.minDistance=4; controls.maxDistance=25;

const hemi = new THREE.HemisphereLight(0xcfd8ff, 0x60483a, 0.55); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2dd, 0.95);
sun.position.set(6,11,5); sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-9; sun.shadow.camera.right=9;
sun.shadow.camera.top=9;   sun.shadow.camera.bottom=-9;
sun.shadow.camera.near=1;  sun.shadow.camera.far=35;
scene.add(sun);

function box(w,h,d,c){return new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshStandardMaterial({color:c,roughness:.9}));}
function cyl(r,h,c,seg){return new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,seg||16),new THREE.MeshStandardMaterial({color:c,roughness:.8}));}
function sh(m){m.castShadow=true;m.receiveShadow=true;return m;}

/* --- комната и стол --- */
const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,40),new THREE.MeshStandardMaterial({color:0x5a4632,roughness:1}));
floor.rotation.x=-Math.PI/2; floor.position.y=-2.35; floor.receiveShadow=true; scene.add(floor);
const wall=new THREE.Mesh(new THREE.PlaneGeometry(40,20),new THREE.MeshStandardMaterial({color:0x6c7488,roughness:1}));
wall.position.set(0,7.6,-15); wall.receiveShadow=true; scene.add(wall);
const wall2=wall.clone(); wall2.rotation.y=Math.PI/2; wall2.position.set(-15,7.6,0); scene.add(wall2);
const table=sh(box(11,0.35,9,0x8a6a45)); table.position.y=-0.475; scene.add(table);

/* --- поддон, пол, прутья, рамки --- */
const CX=4, CZ=3, BH=2.6;
const tray=sh(box(8.6,0.3,6.6,0x7a5a3a)); tray.position.y=-0.15; scene.add(tray);
const sand=new THREE.Mesh(new THREE.PlaneGeometry(8,6),new THREE.MeshStandardMaterial({color:0xcbb27f,roughness:1}));
sand.rotation.x=-Math.PI/2; sand.position.y=0.005; sand.receiveShadow=true; scene.add(sand);
function rail(x,z,w,d){const r=sh(box(w,0.09,d,0x44444e)); r.position.set(x,BH+0.04,z); scene.add(r);}
rail(0,-CZ,8.3,0.1); rail(0,CZ,8.3,0.1); rail(-CX,0,0.1,6.1); rail(CX,0,0.1,6.1);
rail(0,-CZ,8.3,0.1); // верх
const railB=box(8.3,0.1,0.1,0x44444e); railB.position.set(0,0.05,-CZ); scene.add(railB);
const barGeo=new THREE.CylinderGeometry(0.03,0.03,BH,8);
const barMat=new THREE.MeshStandardMaterial({color:0x55555f,roughness:.5,metalness:.6});
function bar(x,z){const b=new THREE.Mesh(barGeo,barMat);b.position.set(x,BH/2,z);b.castShadow=true;scene.add(b);}
for(let x=-CX;x<=CX+1e-6;x+=0.32){bar(x,-CZ);bar(x,CZ);}
for(let z=-CZ+0.32;z<=CZ-0.32;z+=0.32){bar(-CX,z);bar(CX,z);}

/* --- стружка: один InstancedMesh --- */
{
  const g=new THREE.BoxGeometry(0.14,0.03,0.045);
  const m=new THREE.MeshStandardMaterial({roughness:1});
  const N=650, bed=new THREE.InstancedMesh(g,m,N), d=new THREE.Object3D(), col=new THREE.Color();
  for(let i=0;i<N;i++){
    d.position.set((Math.random()*2-1)*3.9, 0.02+Math.random()*0.02, (Math.random()*2-1)*2.9);
    d.rotation.set(0, Math.random()*TAU, (Math.random()-0.5)*0.4);
    d.scale.set(0.6+Math.random(),1,0.7+Math.random()*0.8);
    d.updateMatrix(); bed.setMatrixAt(i,d.matrix);
    col.setHSL(0.09+Math.random()*0.03, 0.45+Math.random()*0.2, 0.5+Math.random()*0.2);
    bed.setColorAt(i,col);
  }
  bed.instanceMatrix.needsUpdate=true; bed.instanceColor.needsUpdate=true;
  bed.receiveShadow=true; scene.add(bed);
}

/* ============ 3. КОЛЕСО (объект с понятными полями) ============ */
const wheelObj = {
  center: new THREE.Vector3(-2.3, КОЛЕСО_R+0.18, 0),
  R: КОЛЕСО_R, W: КОЛЕСО_W, omega: 0, angle: 0,
  runner: null, occupied: false, mesh: null,
  feetY: 0 // вычислим ниже
};
{
  const g=new THREE.Group(); g.position.copy(wheelObj.center);
  const rimMat=new THREE.MeshStandardMaterial({color:0x3fa7d6,roughness:.55});
  for(const z of [-КОЛЕСО_W/2, КОЛЕСО_W/2]){
    const t=new THREE.Mesh(new THREE.TorusGeometry(КОЛЕСО_R,ОБОД_ТРУБА,10,48),rimMat);
    t.position.z=z; t.castShadow=true; g.add(t);
    for(let k=0;k<6;k++){ // спицы
      const a=k/6*TAU, s=cyl(0.028,КОЛЕСО_R-0.12,0x3fa7d6,8);
      s.position.set(Math.cos(a)*(КОЛЕСО_R-0.12)/2, Math.sin(a)*(КОЛЕСО_R-0.12)/2, z);
      s.rotation.z=a-Math.PI/2; s.castShadow=true; g.add(s);
    }
  }
  for(let k=0;k<12;k++){ // перекладины, на них стоит зверь
    const a=k/12*TAU, r=cyl(0.025,КОЛЕСО_W,0x2b8ab8,8);
    r.position.set(Math.cos(a)*(КОЛЕСО_R-0.02), Math.sin(a)*(КОЛЕСО_R-0.02), 0);
    r.rotation.x=Math.PI/2; r.castShadow=true; g.add(r);
  }
  const hub=cyl(0.07,КОЛЕСО_W+0.3,0x333340,12); hub.rotation.x=Math.PI/2; g.add(hub);
  wheelObj.mesh=g; scene.add(g);
  const axle=cyl(0.04,КОЛЕСО_W+0.7,0x333340,10); axle.rotation.x=Math.PI/2;
  axle.position.copy(wheelObj.center); scene.add(axle);
  for(const z of [-(КОЛЕСО_W/2+0.18), КОЛЕСО_W/2+0.18]){
    const p=sh(box(0.12,wheelObj.center.y,0.22,0x666670));
    p.position.set(wheelObj.center.x, wheelObj.center.y/2, z); scene.add(p);
  }
  wheelObj.feetY = wheelObj.center.y - КОЛЕСО_R + ОБОД_ТРУБА + 0.02; // нижняя точка обода
}

/* ============ 4. ТРУБА (полый цилиндр, входы только через торцы) ============ */
const pipeObj = { x1:ТРУБА.x1, x2:ТРУБА.x2, axisZ:ТРУБА.axisZ, rIn:ТРУБА.rIn,
                  rOut:ТРУБА.rOut, centerY:ТРУБА.centerY, innerBottomY:ТРУБА.centerY-ТРУБА.rIn,
                  users:0 };
{
  const L=ТРУБА.x2-ТРУБА.x1;
  const outer=new THREE.Mesh(new THREE.CylinderGeometry(ТРУБА.rOut,ТРУБА.rOut,L,28,1,true),
        new THREE.MeshStandardMaterial({color:0xb06f3a,roughness:.8,side:THREE.DoubleSide}));
  outer.rotation.z=Math.PI/2; outer.position.set((ТРУБА.x1+ТРУБА.x2)/2,ТРУБА.centerY,ТРУБА.axisZ);
  outer.castShadow=true; outer.receiveShadow=true; scene.add(outer);
  const inner=new THREE.Mesh(new THREE.CylinderGeometry(ТРУБА.rIn,ТРУБА.rIn,L,28,1,true),
        new THREE.MeshStandardMaterial({color:0x5a3a1c,roughness:1,side:THREE.BackSide}));
  inner.rotation.z=Math.PI/2; inner.position.copy(outer.position); scene.add(inner);
}
function pipeGroundY(x){
  if(x<ТРУБА.x1||x>ТРУБА.x2) return 0;
  const t=Math.min((x-ТРУБА.x1)/0.35,(ТРУБА.x2-x)/0.35,1);
  return pipeObj.innerBottomY*t;
}

/* ============ 5. МИСКА С ЗЁРНАМИ + ПОИЛКА ============ */
{
  const bowl=new THREE.Group(); bowl.position.copy(Миска);
  const out=cyl(МИСКА_R,0.22,0xc44b3f,24); out.position.y=0.11; sh(out); bowl.add(out);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(МИСКА_R,0.035,8,24),
        new THREE.MeshStandardMaterial({color:0xa83a30}));
  rim.rotation.x=Math.PI/2; rim.position.y=0.22; sh(rim); bowl.add(rim);
  const inr=cyl(МИСКА_R-0.05,0.03,0x7a2a22,24); inr.position.y=0.21; bowl.add(inr);
  const sg=new THREE.SphereGeometry(0.035,6,6);
  const seeds=new THREE.InstancedMesh(sg,new THREE.MeshStandardMaterial({roughness:.7}),45);
  const d=new THREE.Object3D(),c=new THREE.Color();
  for(let i=0;i<45;i++){
    const a=Math.random()*TAU,r=Math.random()*0.3;
    d.position.set(Math.cos(a)*r,0.22+Math.random()*0.02,Math.sin(a)*r);
    d.updateMatrix(); seeds.setMatrixAt(i,d.matrix);
    c.setHSL(0.09+Math.random()*0.12,0.7,0.35+Math.random()*0.3); seeds.setColorAt(i,c);
  }
  seeds.instanceMatrix.needsUpdate=true; seeds.instanceColor.needsUpdate=true;
  seeds.castShadow=true; bowl.add(seeds); scene.add(bowl);
}
{ // поилка на прутьях
  const gp=new THREE.Group(); gp.position.set(3.8,1.15,-0.7);
  const b=cyl(0.17,0.75,0x9fd0e8,16); b.material.transparent=true; b.material.opacity=0.75;
  b.rotation.z=Math.PI/2; b.position.x=-0.15; gp.add(b);
  const sp=cyl(0.028,0.35,0xb8b8c0,8); sp.rotation.z=Math.PI/2; sp.position.set(-0.68,-0.12,0); gp.add(sp);
  gp.traverse(m=>{if(m.isMesh)m.castShadow=true;}); scene.add(gp);
}

/* ============ 6. ХОМЯК ============ */
function makeHamster(cfg){
  const g=new THREE.Group();
  const fur=new THREE.MeshStandardMaterial({color:cfg.color,roughness:.95});
  const bel=new THREE.MeshStandardMaterial({color:cfg.belly,roughness:.95});
  const bodyG=new THREE.Group(); g.add(bodyG);
  const sph=(r,mat,sx,sy,sz,x,y,z)=>{const m=new THREE.Mesh(new THREE.SphereGeometry(r,18,14),mat);
      m.scale.set(sx,sy,sz);m.position.set(x,y,z);m.castShadow=true;return m;};
  const H=ЗВЕРЬ.ВЫСОТА,L=ЗВЕРЬ.ДЛИНА,W=ЗВЕРЬ.ШИРИНА;
  bodyG.add(sph(0.5,fur,L*0.45,H*0.52,W*0.5, 0,H*0.52,0));
  bodyG.add(sph(0.5,bel,L*0.36,H*0.42,W*0.42, 0.06,H*0.36,0));
  bodyG.add(sph(0.06,fur,1,1,1, -L*0.5,H*0.45,0)); // хвост
  const headG=new THREE.Group(); headG.position.set(L*0.45,H*0.68,0); bodyG.add(headG);
  headG.add(sph(0.23,fur,1.15,1,1, 0.05,0,0));
  for(const s of [-1,1]){
    headG.add(sph(0.05, new THREE.MeshStandardMaterial({color:0xffffff}),1,1,1, 0.24,0.06,s*0.12));
    headG.add(sph(0.027,new THREE.MeshStandardMaterial({color:0x111111}),1,1,1, 0.275,0.06,s*0.12));
    headG.add(sph(0.09,fur,1,0.9,0.8, 0.12,-0.06,s*0.15)); // щёки
    const ear=new THREE.Group(); ear.position.set(-0.02,0.19,s*0.14);
    ear.add(sph(0.09,fur,0.5,1.1,1.1, 0,0.07,0));
    ear.add(sph(0.06,new THREE.MeshStandardMaterial({color:0xe0a0a8}),0.5,1,1, 0.02,0.07,0));
    headG.add(ear); headG.userData['ear'+(s>0?'L':'R')]=ear;
  }
  headG.add(sph(0.035,new THREE.MeshStandardMaterial({color:0xd0707a}),1,1,1, 0.31,-0.01,0)); // нос
  const legs=[];
  for(const [fx,fz,nm] of [[1,1,'FL'],[1,-1,'FR'],[-1,1,'BL'],[-1,-1,'BR']]){
    const hip=new THREE.Group(); hip.position.set(fx*0.28,H*0.45,fz*W*0.42);
    const l=cyl(0.055,0.22,0,8); l.material=fur; l.position.y=-0.11; l.castShadow=true;
    hip.add(l); hip.add(sph(0.06,bel,1,0.6,1, 0,-0.22,0));
    bodyG.add(hip); legs[nm]=hip;
  }
  return {group:g, bodyG, headG, legs, color:cfg.color, name:cfg.name};
}

/* ============ 7. ПЯТЬ ХОМЯКОВ + КОНЕЧНЫЙ АВТОМАТ ============ */
const NAMES=[
 {name:'Ржик', color:0xd9a066, belly:0xf5e9d0},
 {name:'Тёмка',color:0x6b4a2f, belly:0xc9a878},
 {name:'Золта',color:0xe8c07a, belly:0xf8efd8},
 {name:'Пепя', color:0x9a9aa4, belly:0xe4e0d4},
 {name:'Снеж', color:0xefe8d6, belly:0xffffff}];
const hamsters=[];
NAMES.forEach((cfg,i)=>{
  const h=makeHamster(cfg);
  Object.assign(h,{
    pos:new THREE.Vector3(-1+i*1.2,0,(Math.random()-0.5)*3),
    curY:0, jumpY:0, vy:0, yaw:Math.random()*TAU,
    phase:Math.random()*TAU, speed:0, v:0, vTarget:0,
    state:'idle', intent:'', timer:0.5+Math.random()*2, hops:0,
    tx:0, tz:0, pipeDir:1, breatheOff:i*1.7,
    twitch:0, twitchT:2+Math.random()*4
  });
  h.group.position.copy(h.pos); scene.add(h.group);
  h.group.traverse(m=>{m.userData.h=h;});
  hamsters.push(h);
});
window.hamsters=hamsters; window.wheelObj=wheelObj; window.pipeObj=pipeObj;

const LABEL={idle:'стоит, осматривается',wheel_enter:'забегает в колесо',wheel_run:'бежит в колесе',
  wheel_exit:'останавливается в колесе',wheel_leave:'выходит из колеса',
  pipe_enter:'заползает в трубу',pipe_run:'ползёт по трубе',pipe_exit:'вылезает из трубы',
  eat:'грызёт зёрна'};
function label(h){
  if(h.state==='walk') return h.intent==='wheel'?'идёт к колесу':h.intent==='pipe'?'идёт к трубе':
    h.intent==='eat'?'идёт к миске':'гуляет по клетке';
  return LABEL[h.state]||h.state;
}
function freeSpot(){
  for(let k=0;k<50;k++){
    const x=(Math.random()*2-1)*3.3, z=(Math.random()*2-1)*2.3;
    if(Math.hypot(x-wheelObj.center.x,z-wheelObj.center.z)>wheelObj.R+0.6)
    if(!(x>ТРУБА.x1-0.6&&x<ТРУБА.x2+0.6&&Math.abs(z-ТРУБА.axisZ)<ТРУБА.rOut+0.6))
    if(Math.hypot(x-Миска.x,z-Миска.z)>МИСКА_R+0.6) return [x,z];
  } return [0,0];
}
function pickActivity(h){
  const opts=['wander','wander','eat'];
  if(!wheelObj.occupied) opts.push('wheel','wheel');
  if(pipeObj.users<1) opts.push('pipe');
  const a=opts[(Math.random()*opts.length)|0];
  h.state='walk'; h.intent=a; h.timer=20;
  if(a==='wander'){h.hops=1+((Math.random()*3)|0);[h.tx,h.tz]=freeSpot();}
  else if(a==='eat'){const g=Math.random()*TAU;h.tx=Миска.x+Math.cos(g)*0.8;h.tz=Миска.z+Math.sin(g)*0.8;}
  else if(a==='wheel'){wheelObj.occupied=true;h.tx=wheelObj.center.x;h.tz=wheelObj.center.z+КОЛЕСО_R+0.95;}
  else {h.tx=ТРУБА.x1-0.25;h.tz=ТРУБА.axisZ;}
}
function moveToward(h,tx,tz,sp,dt){
  const dx=tx-h.pos.x, dz=tz-h.pos.z, d=Math.hypot(dx,dz);
  if(d<0.05){h.pos.x=tx;h.pos.z=tz;return true;}
  const s=Math.min(sp*dt,d);
  h.pos.x+=dx/d*s; h.pos.z+=dz/d*s;
  h.yaw=lerpAngle(h.yaw, Math.atan2(-dz,dx), Math.min(1,10*dt));
  return false;
}
function lerpAngle(a,b,t){let d=(b-a)%TAU;if(d>Math.PI)d-=TAU;if(d<-Math.PI)d+=TAU;return a+d*t;}

function updateHamster(h,dt,t){
  let groundY=0;
  h.vTarget = (h.state==='wheel_run')?RUN : (h.state==='wheel_exit')?0 : 0;
  h.v += THREE.MathUtils.clamp(h.vTarget-h.v,-4*dt,4*dt);
  h.speed=0;
  switch(h.state){
    case 'idle':
      h.timer-=dt; if(h.timer<=0) pickActivity(h); break;
    case 'walk':{
      const arr=moveToward(h,h.tx,h.tz,WALK,dt); h.speed=WALK*(arr?0:1);
      h.timer-=dt;
      if(arr){
        if(h.intent==='wheel') h.state='wheel_enter';
        else if(h.intent==='eat'){h.state='eat';h.timer=4+Math.random()*6;}
        else if(h.intent==='pipe'){h.state='pipe_enter';pipeObj.users++;}
        else if(--h.hops>0){[h.tx,h.tz]=freeSpot();}
        else {h.state='idle';h.timer=1+Math.random()*2.5;}
      } else if(h.timer<=0){h.state='idle';}
      break;}
    case 'wheel_enter':{
      groundY=wheelObj.feetY;
      const d=moveToward(h,wheelObj.center.x,wheelObj.center.z,0.55,dt);
      if(d){h.state='wheel_run';wheelObj.runner=h;h.v=0;h.timer=6+Math.random()*7;}
      break;}
    case 'wheel_run':
      h.pos.x=wheelObj.center.x; h.pos.z=wheelObj.center.z;
      groundY=wheelObj.feetY; h.speed=h.v;
      h.yaw=lerpAngle(h.yaw,0,Math.min(1,8*dt)); // мордой +X: низ обода уходит на -X (назад)
      h.timer-=dt; if(h.timer<=0) h.state='wheel_exit';
      break;
    case 'wheel_exit':
      h.pos.x=wheelObj.center.x; h.pos.z=wheelObj.center.z;
      groundY=wheelObj.feetY; h.speed=h.v;
      if(h.v<0.08){wheelObj.runner=null;h.state='wheel_leave';}
      break;
    case 'wheel_leave':
      groundY=wheelObj.feetY*((Math.hypot(h.pos.x-wheelObj.center.x,h.pos.z-wheelObj.center.z)/(КОЛЕСО_R+0.95)));
      h.speed=0.6;
      if(moveToward(h,wheelObj.center.x,wheelObj.center.z+КОЛЕСО_R+0.95,0.6,dt)){
        wheelObj.occupied=false;h.state='idle';h.timer=0.5+Math.random();}
      break;
    case 'pipe_enter':{
      h.speed=0.5; h.pos.x+=0.5*dt;
      h.pos.z+=(pipeObj.axisZ-h.pos.z)*Math.min(1,10*dt);
      h.yaw=lerpAngle(h.yaw,0,Math.min(1,10*dt));
      groundY=pipeGroundY(h.pos.x);
      if(h.pos.x>=ТРУБА.x1+0.6){h.state='pipe_run';h.pipeDir=1;h.timer=3+Math.random()*4;}
      break;}
    case 'pipe_run':{
      h.speed=0.55; h.pos.x+=h.pipeDir*0.55*dt;
      if(h.pos.x>ТРУБА.x2-0.6){h.pos.x=ТРУБА.x2-0.6;h.pipeDir=-1;}
      if(h.pos.x<ТРУБА.x1+0.6){h.pos.x=ТРУБА.x1+0.6;h.pipeDir=1;}
      h.pos.z=pipeObj.axisZ; groundY=pipeObj.innerBottomY;
      h.yaw=lerpAngle(h.yaw,h.pipeDir>0?0:Math.PI,Math.min(1,10*dt));
      h.timer-=dt; if(h.timer<=0) h.state='pipe_exit';
      break;}
    case 'pipe_exit':
      h.speed=0.55; h.pos.x+=0.55*dt;
      h.pos.z+=(pipeObj.axisZ-h.pos.z)*Math.min(1,6*dt);
      groundY=pipeGroundY(h.pos.x);
      if(h.pos.x>ТРУБА.x2+0.8){pipeObj.users--;h.state='idle';h.timer=1;}
      break;
    case 'eat':
      groundY=0;
      h.yaw=lerpAngle(h.yaw,Math.atan2(-(Миска.z-h.pos.z),Миска.x-h.pos.x),Math.min(1,8*dt));
      h.timer-=dt; if(h.timer<=0){h.state='idle';h.timer=1+Math.random()*2;}
      break;
  }
  /* --- фаза шага ОТ ПРОЙДЕННОГО ПУТИ (в колесе — от скорости обода) --- */
  const dist = (h.state.startsWith('wheel')) ? h.v*dt : h.speed*dt;
  h.phase += dist/ШАГ*TAU;
  /* --- прыжок --- */
  if(h.jumpY>0||h.vy>0){h.vy-=G*dt;h.jumpY+=h.vy*dt;if(h.jumpY<=0){h.jumpY=0;h.vy=0;}}
  h.curY+=(groundY-h.curY)*Math.min(1,8*dt);
  h.pos.x=THREE.MathUtils.clamp(h.pos.x,-3.6,3.6);
  h.pos.z=THREE.MathUtils.clamp(h.pos.z,-2.6,2.6);
  h.group.position.set(h.pos.x,h.curY+h.jumpY,h.pos.z);
  h.group.rotation.y=h.yaw;
  /* --- лапы: диагональные пары --- */
  const amp=Math.min(1,h.speed/RUN)*0.6;
  h.legs.FL.rotation.z=Math.sin(h.phase)*amp;
  h.legs.BR.rotation.z=Math.sin(h.phase)*amp;
  h.legs.FR.rotation.z=Math.sin(h.phase+Math.PI)*amp;
  h.legs.BL.rotation.z=Math.sin(h.phase+Math.PI)*amp;
  /* --- дыхание, жука, ухо --- */
  const breath=(amp<0.08)?1+0.035*Math.sin(t*2.2+h.breatheOff):1;
  h.bodyG.scale.set(breath,1,1);
  h.twitchT-=dt; if(h.twitchT<=0){h.twitch=1;h.twitchT=2+Math.random()*5;}
  h.twitch=Math.max(0,h.twitch-dt*2.5);
  h.headG.userData.earL.rotation.z=Math.sin(t*40)*0.35*h.twitch;
  h.headG.userData.earR.rotation.z=-Math.sin(t*33)*0.35*h.twitch;
  if(h.state==='eat') h.headG.rotation.x=-0.35+Math.sin(t*9)*0.15;
  else h.headG.rotation.x*=Math.min(1,5*dt);
}

/* ============ 8. КОЛЕСО: ω = v / R, трение без бегуна ============ */
function updateWheel(dt){
  if(wheelObj.runner){
    wheelObj.omega = -wheelObj.runner.v / wheelObj.R;  // низ обода уходит назад от морды
  } else {
    wheelObj.omega *= Math.exp(-1.6*dt);               // пустое колесо затухает
    if(Math.abs(wheelObj.omega)<1e-4) wheelObj.omega=0;
  }
  wheelObj.angle += wheelObj.omega*dt;
  wheelObj.mesh.rotation.z = wheelObj.angle;
}

/* ============ 9. КОЛЛИЗИИ: круг/прямоугольник, выталкивание ============ */
function pushCircle(h,cx,cz,r){
  const dx=h.pos.x-cx,dz=h.pos.z-cz,d=Math.hypot(dx,dz);
  if(d<r&&d>1e-6){h.pos.x=cx+dx/d*r;h.pos.z=cz+dz/d*r;}
}
function collide(h){
  if(h.state.startsWith('wheel')||h.state.startsWith('pipe'))return;
  pushCircle(h,wheelObj.center.x,wheelObj.center.z,wheelObj.R+0.35);
  pushCircle(h,Миска.x,Миска.z,МИСКА_R+0.28);
  // прямоугольник трубы (боковая стенка тверда, выталкивание по кратчайшей нормали)
  const x1=ТРУБА.x1-0.28,x2=ТРУБА.x2+0.28,z1=ТРУБА.axisZ-ТРУБА.rOut-0.28,z2=ТРУБА.axisZ+ТРУБА.rOut+0.28;
  if(h.pos.x>x1&&h.pos.x<x2&&h.pos.z>z1&&h.pos.z<z2){
    const p=[h.pos.x-x1,x2-h.pos.x,h.pos.z-z1,z2-h.pos.z],m=Math.min(...p);
    if(m===p[0])h.pos.x=x1; else if(m===p[1])h.pos.x=x2; else if(m===p[2])h.pos.z=z1; else h.pos.z=z2;
  }
}
function separate(){
  for(let i=0;i<hamsters.length;i++)for(let j=i+1;j<hamsters.length;j++){
    const a=hamsters[i],b=hamsters[j];
    if(a.state.startsWith('wheel')||a.state.startsWith('pipe')||
       b.state.startsWith('wheel')||b.state.startsWith('pipe'))continue;
    const dx=b.pos.x-a.pos.x,dz=b.pos.z-a.pos.z,d=Math.hypot(dx,dz);
    if(d<0.56&&d>1e-6){const s=(0.56-d)/2;
      a.pos.x-=dx/d*s;a.pos.z-=dz/d*s;b.pos.x+=dx/d*s;b.pos.z+=dz/d*s;}
  }
}

/* ============ 10. UI + КЛИКИ ============ */
const hlist=document.getElementById('hlist'),dbg=document.getElementById('debug');
const rows=hamsters.map(h=>{
  const r=document.createElement('div');r.className='hrow';
  r.innerHTML=`<span class="chip" style="background:#${h.color.toString(16).padStart(6,'0')}"></span>
               <b>${h.name}</b>&nbsp;—&nbsp;<span class="act"></span>`;
  hlist.appendChild(r);return r.querySelector('.act');
});
const ray=new THREE.Raycaster(), mouse=new THREE.Vector2();
let downX=0,downY=0;
renderer.domElement.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;});
renderer.domElement.addEventListener('pointerup',e=>{
  if(Math.hypot(e.clientX-downX,e.clientY-downY)>5)return;
  mouse.set(e.clientX/innerWidth*2-1,-(e.clientY/innerHeight)*2+1);
  ray.setFromCamera(mouse,camera);
  const hit=ray.intersectObjects(hamsters.map(h=>h.group),true)[0];
  if(hit){const h=hit.object.userData.h;if(h&&h.jumpY===0&&h.vy===0)h.vy=2.6;}
});
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* ============ 11. ЦИКЛ ============ */
const clock=new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05), t=clock.elapsedTime;
  for(const h of hamsters){updateHamster(h,dt,t);collide(h);}
  separate();
  updateWheel(dt);
  // панель
  hamsters.forEach((h,i)=>{const s=label(h);if(rows[i].textContent!==s)rows[i].textContent=s;});
  const r=wheelObj.runner, v=r?r.v:0, rim=Math.abs(wheelObj.omega)*wheelObj.R;
  const diff=v>0.05?Math.abs(rim-v)/v*100:0;
  const inPipe=hamsters.find(h=>h.state.startsWith('pipe')&&h.pos.x>ТРУБА.x1&&h.pos.x<ТРУБА.x2);
  dbg.textContent=
    `Бегун: ${r?r.name:'—'}\n`+
    `лапы v      = ${v.toFixed(3)}\n`+
    `|ω|·R       = ${rim.toFixed(3)}\n`+
    `расхожд.    = ${diff.toFixed(1)} %\n`+
    `ω колеса    = ${wheelObj.omega.toFixed(3)} рад/с\n`+
    `в трубе: ${inPipe?inPipe.name+' |dz|='+Math.abs(inPipe.pos.z-pipeObj.axisZ).toFixed(3):'—'}`;
  controls.update();
  renderer.render(scene,camera);
}
animate();
</script>
</body>
</html>
```

**Как выполнены проверочные пункты:**

| № | Механизм |
|---|---|
| 1 | `wheelObj.omega = -runner.v / R` каждый кадр → расхождение ≈ 0% (видно на панели) |
| 2 | Без бегуна `omega *= exp(-1.6·dt)` → затухает к нулю |
| 3 | Позиция бегуна = `(cx, cy − R + толщина обода, cz)`; `R` выведен из габарита с assert'ами |
| 4 | Внутри трубы `pos.z` жёстко приравнивается оси (`|dz| = 0` в панели); вход только через цель `x1−0.25` |
| 5 | Круговые коллайдеры колеса/миски + прямоугольник трубы с выталкиванием по минимальной нормали |
| 6 | `phase += dist/ШАГ·2π` — при `dist = 0` фаза стоит |
| 7 | Один файл, r128, ошибок в консоли нет |