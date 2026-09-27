# 3D клетка с хомяками — честная физика

Один самодостаточный HTML-файл. Все проверяемые величины доступны из консоли: `window.HAMSTERS`, `window.WHEEL`, `window.PIPE`, `window.BOWL`, `window.DIMS`.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Клетка с хомяками — честная физика</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#1a1c22;font-family:'Segoe UI',Arial,sans-serif}
  #ui{position:fixed;top:12px;left:12px;background:rgba(10,12,18,.78);color:#eee;padding:12px 14px;border-radius:10px;font-size:13px;line-height:1.55;min-width:215px;z-index:5}
  #ui h3{margin:0 0 6px;font-size:14px}
  .dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px;border:1px solid #0005}
  #phys{position:fixed;top:12px;right:12px;background:rgba(10,12,18,.78);color:#8f8;padding:12px 14px;border-radius:10px;font-size:12.5px;line-height:1.6;z-index:5;font-family:Consolas,monospace;min-width:230px}
  #phys b{color:#fff}
  #hint{position:fixed;bottom:10px;left:12px;color:#aab;font-size:12px;z-index:5}
</style>
</head>
<body>
<div id="ui"><h3>Хомяки</h3><div id="hams"></div></div>
<div id="phys">
  <b>Контроль колеса</b><br>
  бегун: <span id="pRunner">—</span><br>
  скорость лап v: <span id="pPaw">—</span><br>
  ω (угловая): <span id="pOmega">—</span><br>
  |ω|·R обода: <span id="pRim">—</span><br>
  расхождение: <span id="pErr">—</span>
</div>
<div id="hint">ЛКМ по хомяку — прыжок · мышь — вращение камеры · колесо — зум</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
'use strict';
/* ================= КОНСТАНТЫ ГАБАРИТОВ (п.1.2) ================= */
const ДЛИНА_ЗВЕРЯ = 0.9, ВЫСОТА_ЗВЕРЯ = 0.55, ШИРИНА_ЗВЕРЯ = 0.45;
const STEP_LEN = 0.22, TAU = Math.PI*2;
/* Радиус колеса — ИЗ габарита зверя: зверь целиком (и в длину, и в высоту)
   помещается с запасом; ширина между дисками шире боков. */
const WHEEL = {
  R: ВЫСОТА_ЗВЕРЯ*1.9,                 // 1.045 > ВЫСОТА и > ДЛИНА
  width: ШИРИНА_ЗВЕРЯ*2.0,             // 0.9 > ШИРИНА (запас по бокам)
  x:-2.1, z:0, angle:0, omega:0, friction:1.6, occupant:null
};
WHEEL.axleY = WHEEL.R + 0.30;          // зазор снизу — хомяк пролезает, пригнувшись
const PIPE = { r: ВЫСОТА_ЗВЕРЯ*0.78, len:1.8, x:0.9, z:0.95, occupant:null };
const BOWL = { x:1.9, z:-1.0, r:0.30 };
const DIMS = {ДЛИНА_ЗВЕРЯ, ВЫСОТА_ЗВЕРЯ, ШИРИНА_ЗВЕРЯ};
console.assert(WHEEL.R > ДЛИНА_ЗВЕРЯ && WHEEL.R > ВЫСОТА_ЗВЕРЯ, 'колесо должно быть больше зверя');
console.assert(WHEEL.width > ШИРИНА_ЗВЕРЯ*1.4, 'между ободами должно быть шире боков');

/* ================= СЦЕНА ================= */
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x23262e);
const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, .1, 100);
camera.position.set(6.4, 4.4, 7.2);
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0,0.9,0); controls.enableDamping = true; controls.maxPolarAngle = 1.5;

const hemi = new THREE.HemisphereLight(0xfff2dd, 0x3a4456, .55); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff4e2, 1.05);
sun.position.set(5,9,3.5); sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-6; sun.shadow.camera.right=6;
sun.shadow.camera.top=6; sun.shadow.camera.bottom=-6;
sun.shadow.camera.near=1; sun.shadow.camera.far=25; sun.shadow.bias=-0.0006;
scene.add(sun);

const M = (c,r=.9,g=.0)=>new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:g});
function box(w,h,d,mat,x,y,z,parent){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;(parent||scene).add(m);return m;}

/* ---- комната, стол ---- */
const floorM = new THREE.Mesh(new THREE.PlaneGeometry(24,24), M(0x5a4a3a,1));
floorM.rotation.x=-Math.PI/2; floorM.position.y=-2.0; floorM.receiveShadow=true; scene.add(floorM);
box(24,4,.3, M(0x6b7f8f,1), 0,0,-8);
box(.3,4,24, M(0x5f7383,1), -9,0,0);
box(7.4,.18,5.4, M(0x8a6a45,1), 0,-.35,0);
for(const sx of[-1,1])for(const sz of[-1,1]) box(.22,1.74,.22, M(0x6e5236,1), sx*3.3,-1.13,sz*2.3);

/* ---- поддон, пол клетки ---- */
box(6.8,.5,4.8, M(0xb8bfc9,.7), 0,-.2,0);
const cageFloor = new THREE.Mesh(new THREE.PlaneGeometry(6.4,4.4), M(0x7a5c3e,1));
cageFloor.rotation.x=-Math.PI/2; cageFloor.position.y=.006; cageFloor.receiveShadow=true; scene.add(cageFloor);

/* ---- прутья и рамки ---- */
const barMat = M(0xc8cdd6,.35,.6), barGeo = new THREE.CylinderGeometry(.022,.022,2.2,8);
function bar(x,z){const b=new THREE.Mesh(barGeo,barMat);b.position.set(x,1.1,z);b.castShadow=true;scene.add(b);}
for(let x=-3.3;x<=3.31;x+=.27){bar(x,-2.3);bar(x,2.3);}
for(let z=-2.3;z<=2.31;z+=.27){bar(-3.3,z);bar(3.3,z);}
const frameMat=M(0x9aa2ad,.4,.5);
box(6.8,.1,.1,frameMat,0,2.24,-2.3); box(6.8,.1,.1,frameMat,0,2.24,2.3);
box(.1,.1,4.8,frameMat,-3.3,2.24,0); box(.1,.1,4.8,frameMat,3.3,2.24,0);
box(6.8,.08,.08,frameMat,0,2.28,0); box(.08,.08,4.8,frameMat,0,2.28,0);

/* ---- подстилка: InstancedMesh щепок (п.3) ---- */
{
  const N=650, im=new THREE.InstancedMesh(new THREE.BoxGeometry(.1,.02,.035), M(0xc9a86a,1), N);
  const d=new THREE.Object3D(), c=new THREE.Color();
  for(let i=0;i<N;i++){
    d.position.set((Math.random()*2-1)*3.05,.012+Math.random()*.015,(Math.random()*2-1)*2.05);
    d.rotation.set((Math.random()-.5)*.5,Math.random()*TAU,(Math.random()-.5)*.5);
    d.updateMatrix(); im.setMatrixAt(i,d.matrix);
    c.setHSL(.09+Math.random()*.05,.45,.45+Math.random()*.25); im.setColorAt(i,c);
  }
  im.receiveShadow=true; scene.add(im);
}

/* ---- колесо: ось горизонтальна (вдоль Z), обод, диски, перекладины ---- */
const wheelG = new THREE.Group(); wheelG.position.set(WHEEL.x,WHEEL.axleY,WHEEL.z); scene.add(wheelG);
const rotor = new THREE.Group(); wheelG.add(rotor);
{
  const rim=new THREE.Mesh(new THREE.TorusGeometry(WHEEL.R,.05,12,48), M(0xe8e4da,.6));
  rim.castShadow=true; rotor.add(rim);
  for(const zs of[-1,1]){
    const disk=new THREE.Mesh(new THREE.CylinderGeometry(WHEEL.R-.01,WHEEL.R-.01,.035,40), M(0xf2eee6,.7));
    disk.rotation.x=Math.PI/2; disk.position.z=zs*WHEEL.width/2; disk.castShadow=true; rotor.add(disk);
  }
  const rungGeo=new THREE.CylinderGeometry(.018,.018,WHEEL.width-.02,8);
  for(let k=0;k<12;k++){const a=k/12*TAU;
    const r=new THREE.Mesh(rungGeo,M(0xd9d4c8,.7));
    r.rotation.x=Math.PI/2; r.position.set(Math.cos(a)*(WHEEL.R-.05),Math.sin(a)*(WHEEL.R-.05),0);
    r.castShadow=true; rotor.add(r);}
  const axle=new THREE.Mesh(new THREE.CylinderGeometry(.04,.04,WHEEL.width+.3,12),M(0x888,.3,.6));
  axle.rotation.x=Math.PI/2; wheelG.add(axle);
}
for(const zs of[-1,1]){ // стойка
  const leg=box(.12,WHEEL.axleY,.1,M(0x8fa0b5,.5),WHEEL.x,WHEEL.axleY/2,WHEEL.z+zs*(WHEEL.width/2+.12));
  leg.castShadow=true;
}

/* ---- полая труба: открытый цилиндр, вход только с торцов ---- */
{
  const g=new THREE.Group(); g.position.set(PIPE.x,PIPE.r,PIPE.z); scene.add(g);
  const inner=new THREE.Mesh(new THREE.CylinderGeometry(PIPE.r,PIPE.r,PIPE.len,28,1,true),
    new THREE.MeshStandardMaterial({color:0xd8b98a,roughness:1,side:THREE.DoubleSide}));
  inner.rotation.z=Math.PI/2; inner.receiveShadow=true; g.add(inner);
  const outer=new THREE.Mesh(new THREE.CylinderGeometry(PIPE.r+.05,PIPE.r+.05,PIPE.len,28,1,true),
    new THREE.MeshStandardMaterial({color:0xbfe3ee,roughness:.2,transparent:true,opacity:.28,side:THREE.DoubleSide}));
  outer.rotation.z=Math.PI/2; g.add(outer);
  for(const xs of[-1,1]){
    const t=new THREE.Mesh(new THREE.TorusGeometry(PIPE.r+.025,.03,10,28),M(0xc9a15c,.8));
    t.rotation.y=Math.PI/2; t.position.x=xs*PIPE.len/2; t.castShadow=true; g.add(t);
  }
}

/* ---- миска с зёрнами ---- */
{
  const bowl=new THREE.Mesh(new THREE.CylinderGeometry(BOWL.r,BOWL.r*.7,.16,24),M(0x44607a,.5));
  bowl.position.set(BOWL.x,.08,BOWL.z); bowl.castShadow=true; bowl.receiveShadow=true; scene.add(bowl);
  const seeds=new THREE.InstancedMesh(new THREE.SphereGeometry(.022,6,5),M(0xd9b13b,1),40);
  const d=new THREE.Object3D();
  for(let i=0;i<40;i++){const a=Math.random()*TAU,rr=Math.random()*BOWL.r*.7;
    d.position.set(BOWL.x+Math.cos(a)*rr,.15+Math.random()*.02,BOWL.z+Math.sin(a)*rr);
    d.updateMatrix(); seeds.setMatrixAt(i,d.matrix);}
  scene.add(seeds);
}
/* ---- поилка ---- */
{
  const g=new THREE.Group(); g.position.set(2.95,0,-.7); scene.add(g);
  const b=new THREE.Mesh(new THREE.CylinderGeometry(.11,.11,.5,16),
    new THREE.MeshStandardMaterial({color:0x9fd8ee,transparent:true,opacity:.5,roughness:.15}));
  b.position.y=1.05; g.add(b);
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,.1,12),M(0x999,.3,.7)); cap.position.y=.78; g.add(cap);
  const tube=new THREE.Mesh(new THREE.CylinderGeometry(.015,.015,.5,8),M(0xaaa,.3,.6)); tube.position.y=.52; g.add(tube);
}

/* ================= ХОМЯК ================= */
function makeHamster(cfg){
  const g=new THREE.Group();
  const fur=M(cfg.color,.95), cream=M(0xf3e7cf,.95), pink=M(0xe8a0a8,.8), dark=M(0x241d18,.6);
  const body=new THREE.Mesh(new THREE.SphereGeometry(.27,20,16),fur);
  body.scale.set(1.55,1.05,1.0); body.position.y=.32; body.castShadow=true; g.add(body);
  const belly=new THREE.Mesh(new THREE.SphereGeometry(.22,16,12),cream);
  belly.scale.set(1.25,.9,.88); belly.position.set(.04,.26,0); g.add(belly);
  const headG=new THREE.Group(); headG.position.set(.36,.5,0); g.add(headG);
  const head=new THREE.Mesh(new THREE.SphereGeometry(.19,18,14),fur); head.castShadow=true; headG.add(head);
  for(const zs of[-1,1]){
    const eye=new THREE.Mesh(new THREE.SphereGeometry(.045,10,8),M(0x120e0a,.3));
    eye.position.set(.13,.04,zs*.105); headG.add(eye);
    const pup=new THREE.Mesh(new THREE.SphereGeometry(.02,8,6),M(0xffffff,.2));
    pup.position.set(.165,.055,zs*.105); headG.add(pup);
    const ch=new THREE.Mesh(new THREE.SphereGeometry(.07,10,8),pink);
    ch.position.set(.09,-.055,zs*.105); headG.add(ch);
    const earP=new THREE.Group(); earP.position.set(-.02,.15,zs*.12); headG.add(earP);
    const ear=new THREE.Mesh(new THREE.SphereGeometry(.065,10,8),fur); ear.scale.z=.4; earP.add(ear);
    const earIn=new THREE.Mesh(new THREE.SphereGeometry(.042,8,6),pink); earIn.scale.z=.4; earIn.position.z=zs*.012; earP.add(earIn);
    earP.userData.zs=zs; headG.add(earP);
    if(zs>0) g.userData.earR=earP; else g.userData.earL=earP;
  }
  const nose=new THREE.Mesh(new THREE.SphereGeometry(.03,8,6),pink); nose.position.set(.185,-.01,0); headG.add(nose);
  const legs=[];
  const legGeo=new THREE.SphereGeometry(.055,8,6);
  for(const lx of[1,-1])for(const lz of[1,-1]){
    const p=new THREE.Group(); p.position.set(lx*.2,.19,lz*.16); g.add(p);
    const l=new THREE.Mesh(legGeo,fur); l.scale.set(1,1.55,1); l.position.y=-.075; l.castShadow=true; p.add(l);
    legs.push({pivot:p, off:(lx>0)===(lz>0)?0:Math.PI}); // диагональные пары
  }
  const tail=new THREE.Mesh(new THREE.SphereGeometry(.045,8,6),fur);
  tail.scale.set(1.4,1,1); tail.position.set(-.46,.3,0); g.add(tail);
  g.userData.hamsterRef=null;
  scene.add(g);
  return {name:cfg.name, group:g, bodyMesh:body, headG, legs, tail,
    bScale:{x:1.55,y:1.05,z:1.0},
    pos:new THREE.Vector3(cfg.x,.02,cfg.z), targetHeading:Math.random()*TAU,
    state:'idle', timer:1+Math.random()*2, target:new THREE.Vector3(),
    speed:0, runSpeed:0, phase:0, moveAmp:0, crouch:0,
    jumping:false, vy:0, enterT:0, mouthX:0, pipeDir:1, pipeS:0,
    breathPhase:Math.random()*TAU, twitchT:1+Math.random()*3, twitchActive:0};
}
const HAMSTERS=[
  makeHamster({name:'Рыжик',   color:0xd98e3d, x:-0.5,z: 0.4}),
  makeHamster({name:'Топтя',   color:0xa9744a, x: 0.8,z:-0.6}),
  makeHamster({name:'Нуба',    color:0xe8d9b0, x: 1.6,z: 1.2}),
  makeHamster({name:'Пепел',   color:0x9aa0a8, x:-1.2,z:-1.1}),
  makeHamster({name:'Снежана', color:0xf2ede4, x: 0.2,z: 1.5}),
];
HAMSTERS.forEach(h=>h.group.userData.hamsterRef=h);

/* ================= УТИЛИТЫ ================= */
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;
const approach=(v,t,d)=>v<t?Math.min(t,v+d):Math.max(t,v-d);
const easeIO=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
function angleLerp(a,b,t){let d=b-a;while(d>Math.PI)d-=TAU;while(d<-Math.PI)d+=TAU;return a+d*clamp(t,0,1);}
const WHEEL_FIX=['wheel_enter','running_wheel','wheel_exit'];
const FIXED=h=>WHEEL_FIX.includes(h.state)||h.state==='pipe_move';
function groundY(h){
  if(WHEEL_FIX.includes(h.state)) return WHEEL.axleY-WHEEL.R+0.05;
  if(h.state==='pipe_move') return .06;
  return .02;
}
function randPoint(){return new THREE.Vector3((Math.random()*2-1)*2.5,0,(Math.random()*2-1)*1.6);}

/* ================= КОЛЕСО: ФИЗИКА (п.1.1) ================= */
function updateWheel(dt){
  const o=WHEEL.occupant;
  if(o && o.state==='running_wheel'){
    WHEEL.omega = o.runSpeed / WHEEL.R;   // без проскальзывания: ω = v / R
  } else {
    const d=WHEEL.friction*dt;            // пустое колесо — трение
    WHEEL.omega = Math.abs(WHEEL.omega)<=d ? 0 : WHEEL.omega-Math.sign(WHEEL.omega)*d;
  }
  WHEEL.angle += WHEEL.omega*dt;
  rotor.rotation.z = WHEEL.angle;
}

/* ================= ПОВЕДЕНИЕ (ЧАСТЬ 2) ================= */
function startWalk(h,p){h.state='walking'; h.target.copy(p);}
function pickActivity(h){
  const r=Math.random();
  if(r<.32 && !WHEEL.occupant){ h.state='to_wheel'; h.target.set(WHEEL.x+WHEEL.R+.5,0,WHEEL.z); }
  else if(r<.60 && !PIPE.occupant){
    h.pipeDir=Math.random()<.5?1:-1; h.state='to_pipe';
    h.target.set(PIPE.x-h.pipeDir*(PIPE.len/2+PIPE.r+.4),0,PIPE.z);
  } else if(r<.85){
    const dx=h.pos.x-BOWL.x,dz=h.pos.z-BOWL.z,d=Math.hypot(dx,dz)||1;
    h.state='to_bowl'; h.target.set(BOWL.x+dx/d*(BOWL.r+.5),0,BOWL.z+dz/d*(BOWL.r+.5));
  } else startWalk(h,randPoint());
}
function onArrive(h){
  if(h.state==='to_wheel'){WHEEL.occupant=h; h.mouthX=h.target.x; h.state='wheel_enter'; h.enterT=0;}
  else if(h.state==='to_pipe'){PIPE.occupant=h; h.state='pipe_move'; h.pipeS=-h.pipeDir*(PIPE.len/2+PIPE.r+.4);}
  else if(h.state==='to_bowl'){h.state='eating'; h.timer=3+Math.random()*4;}
  else {h.state='idle'; h.timer=1+Math.random()*2.5;}
}

function updateHamster(h,dt,t){
  switch(h.state){
    case 'idle':
      h.speed=0; h.timer-=dt; if(h.timer<=0) pickActivity(h); break;
    case 'walking': case 'to_wheel': case 'to_pipe': case 'to_bowl': {
      const dx=h.target.x-h.pos.x, dz=h.target.z-h.pos.z, d=Math.hypot(dx,dz);
      h.speed=approach(h.speed, d>.04?1.1:0, 4*dt);
      if(d>1e-4 && h.speed>.001){
        const step=h.speed*dt;
        h.pos.x+=dx/d*step; h.pos.z+=dz/d*step;
        h.phase+=step/STEP_LEN*TAU;              // фаза от ПРОЙДЕННОГО ПУТИ (п.1.5)
        h.targetHeading=Math.atan2(-dz,dx);
      }
      if(d<.07) onArrive(h);
      break;
    }
    case 'wheel_enter': {                        // плавный вход, без телепорта (п.1.6)
      h.enterT+=dt/1.2; const e=easeIO(clamp(h.enterT,0,1));
      h.pos.x=lerp(h.mouthX,WHEEL.x,e); h.pos.z=WHEEL.z;
      h.pos.y=lerp(.02, WHEEL.axleY-WHEEL.R+.05, e);
      h.crouch=Math.sin(e*Math.PI);
      h.speed=.7; h.phase+=.7*dt/STEP_LEN*TAU; h.targetHeading=Math.PI;
      if(h.enterT>=1){h.state='running_wheel'; h.timer=4+Math.random()*5; h.crouch=0;}
      break;
    }
    case 'running_wheel': {
      h.timer-=dt;
      h.runSpeed=approach(h.runSpeed, h.timer<.8?0:2.3, 5*dt);
      h.speed=h.runSpeed;
      h.phase+=h.runSpeed*dt/STEP_LEN*TAU;       // шаг привязан к скорости обода
      h.pos.set(WHEEL.x, WHEEL.axleY-WHEEL.R+.05+Math.abs(Math.sin(h.phase))*.015, WHEEL.z);
      h.targetHeading=Math.PI;
      if(h.timer<=0 && h.runSpeed<.05){h.state='wheel_exit'; h.enterT=0;}
      break;
    }
    case 'wheel_exit': {
      h.enterT+=dt/1.2; const e=easeIO(clamp(h.enterT,0,1));
      h.pos.x=lerp(WHEEL.x,h.mouthX,e); h.pos.z=WHEEL.z;
      h.pos.y=lerp(WHEEL.axleY-WHEEL.R+.05,.02,e);
      h.crouch=Math.sin(e*Math.PI);
      h.speed=.7; h.phase+=.7*dt/STEP_LEN*TAU; h.targetHeading=Math.PI;
      if(h.enterT>=1){WHEEL.occupant=null; h.crouch=0; h.runSpeed=0; startWalk(h,randPoint());}
      break;
    }
    case 'pipe_move': {                          // строго вдоль оси, вход через торец (п.1.3)
      const sp=.9; h.speed=sp;
      h.pipeS+=h.pipeDir*sp*dt;
      h.pos.x=PIPE.x+h.pipeS; h.pos.z=PIPE.z; h.pos.y=.06;
      h.phase+=sp*dt/STEP_LEN*TAU;
      h.targetHeading=h.pipeDir>0?0:Math.PI;
      if(h.pipeDir*h.pipeS>PIPE.len/2+PIPE.r+.4){PIPE.occupant=null; startWalk(h,randPoint());}
      break;
    }
    case 'eating':
      h.speed=0; h.timer-=dt; if(h.timer<=0) startWalk(h,randPoint()); break;
  }
  if(h.jumping){
    h.vy-=12*dt; h.pos.y+=h.vy*dt;
    const gy=groundY(h); if(h.pos.y<=gy){h.pos.y=gy;h.jumping=false;h.vy=0;}
  } else if(!FIXED(h)) h.pos.y=groundY(h);
  if(!FIXED(h)) collideWorld(h);                 // твёрдые тела предметов (п.1.4)

  /* --- визуал --- */
  h.group.position.copy(h.pos);
  h.group.rotation.y=angleLerp(h.group.rotation.y,h.targetHeading,10*dt);
  h.group.scale.y=1-.42*h.crouch;
  const moving=h.speed>.06;
  h.moveAmp=approach(h.moveAmp,moving?1:0,6*dt);
  for(const L of h.legs)
    L.pivot.rotation.z = h.jumping ? -.7 : Math.sin(h.phase+L.off)*.65*h.moveAmp;
  const a=.03*Math.sin(t*2.4+h.breathPhase)*(h.state==='idle'?1:.4);
  h.bodyMesh.scale.set(h.bScale.x*(1+a), h.bScale.y*(1-a*.5), h.bScale.z*(1+a));
  h.headG.rotation.x = h.state==='eating' ? .16+.13*Math.sin(t*14) : .06*Math.sin(t*1.6+h.breathPhase);
  h.twitchT-=dt;
  if(h.twitchT<=0){h.twitchT=2+Math.random()*4; h.twitchActive=.4;}
  if(h.twitchActive>0){h.twitchActive-=dt; h.group.userData.earL.rotation.z=Math.sin(t*25)*.5;}
  else h.group.userData.earL.rotation.z=0;
  h.tail.rotation.y=Math.sin(t*3+h.breathPhase)*.25;
}

/* ================= КОЛЛИЗИИ (п.1.4) ================= */
function collideWorld(h){
  const r=.3;
  h.pos.x=clamp(h.pos.x,-3+r,3-r); h.pos.z=clamp(h.pos.z,-2+r,2-r);
  // миска — круг
  {const dx=h.pos.x-BOWL.x,dz=h.pos.z-BOWL.z,d=Math.hypot(dx,dz),m=BOWL.r+r;
   if(d<m&&d>1e-6){h.pos.x+=dx/d*(m-d);h.pos.z+=dz/d*(m-d);}}
  // колесо — прямоугольник в плане
  {const hx=WHEEL.R+.06,hz=WHEEL.width/2+.1,dx=h.pos.x-WHEEL.x,dz=h.pos.z-WHEEL.z;
   if(Math.abs(dx)<hx+r&&Math.abs(dz)<hz+r){
     const px=hx+r-Math.abs(dx), pz=hz+r-Math.abs(dz);
     if(px<pz) h.pos.x=WHEEL.x+Math.sign(dx||1)*(hx+r);
     else      h.pos.z=WHEEL.z+Math.sign(dz||1)*(hz+r);
   }}
  // труба — прямоугольник в плане (снаружи; внутри — состояние pipe_move)
  {const hx=PIPE.len/2+.12,hz=PIPE.r+.1,dx=h.pos.x-PIPE.x,dz=h.pos.z-PIPE.z;
   if(Math.abs(dx)<hx+r&&Math.abs(dz)<hz+r){
     const px=hx+r-Math.abs(dx), pz=hz+r-Math.abs(dz);
     if(px<pz) h.pos.x=PIPE.x+Math.sign(dx||1)*(hx+r);
     else      h.pos.z=PIPE.z+Math.sign(dz||1)*(hz+r);
   }}
}
function separateHamsters(){
  for(let i=0;i<HAMSTERS.length;i++)for(let j=i+1;j<HAMSTERS.length;j++){
    const a=HAMSTERS[i],b=HAMSTERS[j];
    if(FIXED(a)||FIXED(b))continue;
    let dx=b.pos.x-a.pos.x,dz=b.pos.z-a.pos.z,d=Math.hypot(dx,dz);
    const m=.55;
    if(d<m&&d>1e-6){const p=(m-d)/2;dx/=d;dz/=d;
      a.pos.x-=dx*p;a.pos.z-=dz*p;b.pos.x+=dx*p;b.pos.z+=dz*p;}
  }
}

/* ================= КЛИК — ПРЫЖОК ================= */
const raycaster=new THREE.Raycaster(), ndc=new THREE.Vector2();
let downX=0,downY=0;
renderer.domElement.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;});
renderer.domElement.addEventListener('pointerup',e=>{
  if(Math.hypot(e.clientX-downX,e.clientY-downY)>6)return;
  ndc.set(e.clientX/innerWidth*2-1, -(e.clientY/innerHeight)*2+1);
  raycaster.setFromCamera(ndc,camera);
  const hits=raycaster.intersectObjects(HAMSTERS.map(h=>h.group),true);
  if(!hits.length)return;
  let o=hits[0].object; while(o&&!o.userData.hamsterRef)o=o.parent;
  const h=o&&o.userData.hamsterRef;
  if(h&&!h.jumping&&!FIXED(h)&&h.state!=='eating'){h.jumping=true;h.vy=2.6;}
});

/* ================= UI ================= */
const STATUS={idle:'стоит, дышит',walking:'гуляет',to_wheel:'идёт к колесу',
  wheel_enter:'забегает в колесо',running_wheel:'бежит в колесе',wheel_exit:'выходит из колеса',
  to_pipe:'идёт к трубе',pipe_move:'ползёт по трубе',to_bowl:'идёт к миске',eating:'грызёт зёрна'};
const rowsEl=document.getElementById('hams'), rows=[];
HAMSTERS.forEach(h=>{const d=document.createElement('div');
  d.innerHTML=`<span class="dot" style="background:#${h.group.children[0].material.color.getHexString()}"></span><b>${h.name}</b>: <span>…</span>`;
  rowsEl.appendChild(d); rows.push(d.querySelector('span:last-child'));});
const pR=document.getElementById('pRunner'),pP=document.getElementById('pPaw'),
      pO=document.getElementById('pOmega'),pS=document.getElementById('pRim'),pE=document.getElementById('pErr');
function updateUI(){
  HAMSTERS.forEach((h,i)=>rows[i].textContent=STATUS[h.state]);
  const o=WHEEL.occupant, running=o&&o.state==='running_wheel';
  const paw=running?o.runSpeed:0, rim=Math.abs(WHEEL.omega)*WHEEL.R;
  pR.textContent=running?o.name:(o?o.name+' (не бежит)':'— пусто');
  pP.textContent=paw.toFixed(2)+' м/с';
  pO.textContent=WHEEL.omega.toFixed(2)+' рад/с';
  pS.textContent=rim.toFixed(2)+' м/с';
  pE.textContent=paw>.15?(Math.abs(rim-paw)/paw*100).toFixed(1)+' %':'—';
}

/* ================= ЦИКЛ ================= */
const clock=new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),.05), t=clock.elapsedTime;
  updateWheel(dt);
  for(const h of HAMSTERS) updateHamster(h,dt,t);
  separateHamsters();
  updateUI();
  controls.update();
  renderer.render(scene,camera);
}
animate();
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* ================= ЭКСПОРТ ДЛЯ ПРОВЕРКИ ================= */
window.HAMSTERS=HAMSTERS; window.WHEEL=WHEEL; window.PIPE=PIPE; window.BOWL=BOWL; window.DIMS=DIMS;
</script>
</body>
</html>
```

## Как выполнены критерии проверки

| # | Требование | Реализация |
|---|---|---|
| 1 | \|ω\|·R = скорость лап | Пока бегун в состоянии `running_wheel`, `WHEEL.omega = runSpeed / R` — расхождение тождественно 0 %, видно в панели |
| 2 | Пустое колесо затухает | Без бегуна `omega` уменьшается на `friction·dt` до точного нуля |
| 3 | Стояние на нижней точке, габарит < R | Лапы на `axleY − R + 0.05`; `R = ВЫСОТА_ЗВЕРЯ·1.9 = 1.045 > 0.9` и `> 0.55` — проверено `console.assert` |
| 4 | Хомяк в трубе на оси | В `pipe_move` `pos.z = PIPE.z` строго; координата вдоль оси меняется только через торцы (старт с `±(len/2 + r + 0.4)`) |
| 5 | Нет прохождения сквозь предметы | `collideWorld`: выталкивание по минимальной нормали из AABB колеса/трубы и круга миски; состояния «внутри» кинематические и легитимные |
| 6 | Лапы замирают | `phase += step/STEP_LEN·2π` — только от пройденного пути; амплитуда `moveAmp` гаснет при остановке |
| 7 | Без ошибок | Один файл, r128 + OrbitControls с указанных CDN, dt ограничен 0.05, resize обработан |

Дополнительно: обод уходит назад относительно взгляда бегуна (ось Z, ω>0 при морде в −X), ширина колеса 0.9 > боков 0.45, один пользователь на колесо и трубу, вход в колесо с пригибанием (crouch) без телепорта, подстилка — один `InstancedMesh` из 650 щепок.