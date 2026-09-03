Готово! Ниже — полный самодостаточный файл `aquarium.html`. Сохраните его и откройте в браузере (нужен интернет для CDN Three.js).

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:100%; height:100%; overflow:hidden;
    font-family:'Segoe UI', system-ui, sans-serif; }
  body { background:linear-gradient(180deg,#03101f 0%,#07294d 45%,#0d4a7a 100%); }
  canvas { display:block; }

  .panel{
    position:absolute; z-index:10;
    background:rgba(5,22,44,.55);
    backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(110,190,255,.28); border-radius:16px;
    box-shadow:0 10px 34px rgba(0,10,30,.45), inset 0 1px 0 rgba(160,220,255,.15);
    color:#dcefff;
  }
  #infoPanel{ top:18px; left:18px; width:282px; padding:16px 16px 15px; }
  h1.title{
    font-size:21px; font-weight:800; letter-spacing:.4px; margin-bottom:10px;
    background:linear-gradient(90deg,#ffd76a 0%,#ff8f3f 35%,#3fb6ff 75%,#7ef3ff 100%);
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .hint{ font-size:12.3px; line-height:1.6; color:#b9d9f7; }
  .hint b{ color:#8fd4ff; font-weight:600; }
  .btnRow{ display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
  button.aqBtn{
    cursor:pointer; border:none; color:#fff;
    font:600 12.5px/1 'Segoe UI',sans-serif; padding:9px 12px; border-radius:11px;
    background:linear-gradient(135deg,#2f7cf6 0%,#2fc3ff 100%);
    box-shadow:0 4px 14px rgba(35,130,255,.35), inset 0 1px 0 rgba(255,255,255,.25);
    transition:transform .15s, box-shadow .15s, filter .15s;
  }
  button.aqBtn:hover{ transform:translateY(-2px); filter:brightness(1.12);
    box-shadow:0 8px 22px rgba(45,170,255,.5), inset 0 1px 0 rgba(255,255,255,.3); }
  button.aqBtn:active{ transform:scale(.97); }

  #statsPanel{ top:18px; right:18px; padding:12px 16px; min-width:152px; }
  .statLine{ display:flex; justify-content:space-between; gap:14px;
    font-size:13px; padding:3px 0; color:#bfe0ff; }
  .statVal{ font-weight:700; color:#7ee7ff; font-variant-numeric:tabular-nums; }
</style>
</head>
<body>

<div class="panel" id="infoPanel">
  <h1 class="title">🐠 3D Аквариум</h1>
  <div class="hint">
    <b>ЛКМ + движение</b> — вращение камеры<br>
    <b>ПКМ + движение</b> — панорамирование<br>
    <b>Колесо мыши</b> — зум<br>
    <b>Клик по воде</b> — бросить корм 🍤
  </div>
  <div class="btnRow">
    <button class="aqBtn" id="btnAddFish">➕ Рыбка</button>
    <button class="aqBtn" id="btnBubbles">🫧 Пузыри</button>
    <button class="aqBtn" id="btnLight">💡 Свет</button>
  </div>
</div>

<div class="panel" id="statsPanel">
  <div class="statLine"><span>Рыбки</span><span class="statVal" id="statFish">15</span></div>
  <div class="statLine"><span>FPS</span><span class="statVal" id="statFps">60</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ================= НАСТРОЙКА СЦЕНЫ ================= */
const TANK = { W:36, H:24, D:20 };
const HW = TANK.W/2, HH = TANK.H/2, HD = TANK.D/2;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a3a63, 0.011);          // «вода»

const camera = new THREE.PerspectiveCamera(55, innerWidth/innerHeight, 0.1, 300);
camera.position.set(24, 19, 33);

const renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 10.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI/1.8;

/* ================= СВЕТ ================= */
const ambient = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xfff1d6, 1.15);
sun.position.set(26, 42, 18);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -32;  sun.shadow.camera.right = 32;
sun.shadow.camera.top   =  38; sun.shadow.camera.bottom = -6;
sun.shadow.camera.near = 5;   sun.shadow.camera.far = 110;
sun.shadow.bias = -0.0004;
scene.add(sun);

const p1 = new THREE.PointLight(0x3fd2ff, 0.85, 46, 2); p1.position.set(-12, 8, 7);
const p2 = new THREE.PointLight(0x2a6bff, 0.75, 46, 2); p2.position.set(13, 11, -7);
scene.add(p1, p2);

/* ================= СТЕКЛЯННЫЙ АКВАРИУМ ================= */
const glass = new THREE.Mesh(
  new THREE.BoxGeometry(TANK.W, TANK.H, TANK.D),
  new THREE.MeshPhysicalMaterial({
    color:0xbfe4ff, metalness:0, roughness:0.05,
    transmission:0.95, thickness:1.6, transparent:true, opacity:0.92
  })
);
glass.position.y = HH;
scene.add(glass);

const edges = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(TANK.W, TANK.H, TANK.D)),
  new THREE.LineBasicMaterial({ color:0x8fd8ff, transparent:true, opacity:0.85 })
);
edges.position.y = HH;
scene.add(edges);

/* ================= ПЕСЧАНОЕ ДНО ================= */
(function makeSand(){
  const geo = new THREE.PlaneGeometry(TANK.W, TANK.D, 44, 30);
  const pos = geo.attributes.position;
  for(let i=0;i<pos.count;i++){
    const x = pos.getX(i), y = pos.getY(i);
    pos.setZ(i,
      Math.sin(x*0.55)*Math.cos(y*0.62)*0.22 +
      Math.sin(x*1.7+1.3)*Math.cos(y*1.9)*0.07);
  }
  geo.computeVertexNormals();
  geo.rotateX(-Math.PI/2);
  const m = new THREE.Mesh(geo,
    new THREE.MeshStandardMaterial({ color:0xd8bd85, roughness:0.95 }));
  m.receiveShadow = true;
  scene.add(m);
})();

/* ================= КАМНИ (8) ================= */
for(let i=0;i<8;i++){
  const s = 0.7 + Math.random()*1.3;
  const geo = new THREE.DodecahedronGeometry(1, 0);
  const p = geo.attributes.position;
  for(let v=0; v<p.count; v++){
    const x=p.getX(v), y=p.getY(v), z=p.getZ(v);
    const seed = Math.sin(x*127.1 + y*311.7 + z*74.7)*43758.5453;
    const rnd = seed - Math.floor(seed);
    const k = (rnd-0.5)*0.55, len = Math.sqrt(x*x+y*y+z*z)||1;
    p.setXYZ(v, x+x/len*k, y+y/len*k, z+z/len*k);
  }
  geo.computeVertexNormals();
  const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color:new THREE.Color().setHSL(0.08+Math.random()*0.05, 0.18, 0.28+Math.random()*0.12),
    roughness:0.9, metalness:0.05, flatShading:true
  }));
  rock.scale.setScalar(s);
  rock.position.set((Math.random()*2-1)*(HW-2.5), s*0.45, (Math.random()*2-1)*(HD-2.5));
  rock.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
  rock.castShadow = rock.receiveShadow = true;
  scene.add(rock);
}

/* ================= ВОДОРОСЛИ (12) ================= */
const plants = [];
for(let i=0;i<12;i++){
  const g = new THREE.Group();
  const base = new THREE.Color().setHSL(0.3+Math.random()*0.12, 0.65, 0.3+Math.random()*0.15);
  const blades = 3 + Math.floor(Math.random()*3);
  for(let b=0;b<blades;b++){
    const ang = Math.random()*Math.PI*2, lean = 0.25+Math.random()*0.5, h = 1.6+Math.random()*2.4;
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0,0,0),
      new THREE.Vector3(Math.cos(ang)*lean*0.4, h*0.38, Math.sin(ang)*lean*0.4),
      new THREE.Vector3(Math.cos(ang)*lean,     h*0.72, Math.sin(ang)*lean),
      new THREE.Vector3(Math.cos(ang)*(lean+0.35), h,  Math.sin(ang)*(lean+0.35))
    ]);
    const blade = new THREE.Mesh(
      new THREE.TubeGeometry(curve, 10, 0.13+Math.random()*0.09, 5),
      new THREE.MeshStandardMaterial({
        color:base.clone().offsetHSL(Math.random()*0.04-0.02, 0, Math.random()*0.12-0.06),
        roughness:0.75, side:THREE.DoubleSide
      }));
    blade.castShadow = true;
    g.add(blade);
  }
  g.position.set((Math.random()*2-1)*(HW-2), 0.1, (Math.random()*2-1)*(HD-2));
  g.rotation.y = Math.random()*Math.PI*2;
  plants.push({ group:g, phase:Math.random()*Math.PI*2 });
  scene.add(g);
}

/* ================= БУБЛЬКИ (30) ================= */
const bubbles = [];
const bubbleMat = new THREE.MeshPhysicalMaterial({
  color:0xcfeaff, roughness:0.12, transparent:true, opacity:0.4,
  transmission:0.55, thickness:0.4
});
function addBubble(){
  const m = new THREE.Mesh(new THREE.SphereGeometry(0.14+Math.random()*0.26, 12, 10), bubbleMat);
  const d = {
    mesh:m,
    baseX:(Math.random()*2-1)*(HW-1.5),
    baseZ:(Math.random()*2-1)*(HD-1.5),
    y:0.4 + Math.random()*HH,
    rise:1.2 + Math.random()*1.6,
    amp:0.3 + Math.random()*0.5,
    freq:1 + Math.random()*1.5,
    phase:Math.random()*Math.PI*2
  };
  m.position.set(d.baseX, d.y, d.baseZ);
  bubbles.push(d);
  scene.add(m);
}
for(let i=0;i<30;i++) addBubble();

function updateBubbles(t, dt){
  for(const b of bubbles){
    b.y += b.rise*dt;
    if(b.y > TANK.H-0.7){                       // сброс на дно
      b.y = 0.35;
      b.baseX = (Math.random()*2-1)*(HW-1.5);
      b.baseZ = (Math.random()*2-1)*(HD-1.5);
    }
    b.mesh.position.set(
      b.baseX + Math.sin(t*b.freq + b.phase)*b.amp,
      b.y,
      b.baseZ + Math.cos(t*b.freq*0.9 + b.phase)*b.amp*0.8
    );
  }
}

/* ================= КОРМ ================= */
const foods = [];
const foodMat = new THREE.MeshStandardMaterial({
  color:0xff8a2a, emissive:0x7a2c00, roughness:0.5
});
function spawnFood(x, z){
  const m = new THREE.Mesh(new THREE.SphereGeometry(0.34, 10, 8), foodMat);
  m.position.set(x, TANK.H-0.6, z);
  scene.add(m);
  foods.push({
    mesh:m,
    vel:new THREE.Vector3((Math.random()-0.5)*0.6, 0, (Math.random()-0.5)*0.6)
  });
}
function updateFoods(dt){
  for(let i=foods.length-1;i>=0;i--){
    const f = foods[i];
    f.vel.y -= 6.5*dt;                               // гравитация в воде
    f.mesh.position.addScaledVector(f.vel, dt);
    f.mesh.rotation.y += dt*2;
    if(f.mesh.position.y <= 0.45){                    // упало на дно
      scene.remove(f.mesh);
      foods.splice(i,1);
    }
  }
}

/* ================= РЫБКИ ================= */
const FISH_PALETTES = [
  { body:0xff8c1a, fin:0xffd27a },   // оранжевая
  { body:0x2e7bff, fin:0x9fd0ff },   // синяя
  { body:0xffc400, fin:0xff5722 },   // жёлто-красная
  { body:0x8e44dd, fin:0xc79bf2 },   // фиолетовая
  { body:0xe8332a, fin:0xff8a6b },   // красная
  { body:0x3fae4c, fin:0xa8e063 },   // зелёная
  { body:0xff7bac, fin:0xffc9de },   // розовая
  { body:0xf5b700, fin:0xfff3b0 }    // золотая
];

function createFish(pal){
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color:pal.body, roughness:0.45, metalness:0.15 });
  const finMat  = new THREE.MeshStandardMaterial({ color:pal.fin, roughness:0.5, metalness:0.1, transparent:true, opacity:0.92, side:THREE.DoubleSide });

  // Тело — вытянутый эллипсоид
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 14), bodyMat);
  body.scale.set(1.55, 0.62, 0.5);
  body.castShadow = true;
  g.add(body);

  // Голова
  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
  head.scale.set(0.85, 0.6, 0.55);
  head.position.set(1.05, 0.02, 0);
  head.castShadow = true;
  g.add(head);

  // Глаза с зрачками
  const eyeG = new THREE.SphereGeometry(0.17, 12, 10);
  const pupG = new THREE.SphereGeometry(0.08, 10, 8);
  const whiteM = new THREE.MeshStandardMaterial({ color:0xf5faff, roughness:0.25 });
  const pupilM = new THREE.MeshStandardMaterial({ color:0x101418, roughness:0.2 });
  for(const s of [-1,1]){
    const e = new THREE.Mesh(eyeG, whiteM);
    e.position.set(1.32, 0.12, s*0.3); g.add(e);
    const p = new THREE.Mesh(pupG, pupilM);
    p.position.set(1.42, 0.12, s*0.33); g.add(p);
  }

  // Хвост — пивот на задней части, сплющенный конус
  const tailPivot = new THREE.Group();
  tailPivot.position.set(-1.35, 0, 0);
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.55, 1.0, 8), finMat);
  tail.rotation.z = Math.PI/2;
  tail.scale.set(1, 1, 0.28);
  tail.position.x = -0.5;
  tailPivot.add(tail);
  g.add(tailPivot);

  // Верхний плавник
  const dorsal = new THREE.Mesh(new THREE.ConeGeometry(0.42, 0.55, 4), finMat);
  dorsal.scale.set(1.15, 1, 0.22);
  dorsal.position.set(-0.15, 0.52, 0);
  g.add(dorsal);

  // Боковые плавники
  const finG = new THREE.ConeGeometry(0.3, 0.5, 6);
  const leftFin = new THREE.Mesh(finG, finMat);
  leftFin.position.set(0.75, -0.18, 0.42);
  leftFin.rotation.set(0.5, 0, -0.7);
  g.add(leftFin);
  const rightFin = new THREE.Mesh(finG, finMat);
  rightFin.position.set(0.75, -0.18, -0.42);
  rightFin.rotation.set(0.5, 0, 0.7);
  g.add(rightFin);

  return { group:g, tailPivot, leftFin, rightFin };
}

const fishArray = [];
function addFish(){
  const pal = FISH_PALETTES[Math.floor(Math.random()*FISH_PALETTES.length)];
  const f = createFish(pal);
  const s = 0.6 + Math.random()*0.6;                     // размер 0.6–1.2
  f.group.scale.setScalar(s);
  f.group.position.set(
    (Math.random()*2-1)*(HW-3),
    2.5 + Math.random()*(TANK.H-6),
    (Math.random()*2-1)*(HD-3)
  );
  const v = new THREE.Vector3(Math.random()-0.5,(Math.random()-0.5)*0.4,Math.random()-0.5)
    .normalize().multiplyScalar(2.4 + Math.random()*1.8);
  scene.add(f.group);
  fishArray.push({
    mesh:f.group, tail:f.tailPivot, leftFin:f.leftFin, rightFin:f.rightFin,
    velocity:v,
    speed:2.4 + Math.random()*1.8,
    tailSpeed:5.5 + Math.random()*3.5,
    phase:Math.random()*Math.PI*2,
    targetFood:null,
    avoidanceRadius:2.4 + Math.random()*1.2,
    baseScale:s
  });
  updateFishCount();
}
for(let i=0;i<15;i++) addFish();

function updateFishCount(){
  document.getElementById('statFish').textContent = fishArray.length;
}

/* -------- ИИ / поведение -------- */
const _tv = new THREE.Vector3();
const _te = new THREE.Euler();
const _tq = new THREE.Quaternion();

function updateFish(dt, t){
  const n = fishArray.length;
  for(let i=0;i<n;i++){
    const f = fishArray[i];
    const pos = f.mesh.position, vel = f.velocity;

    // Цель: еда или блуждание
    let chasing = false;
    if(f.targetFood && foods.indexOf(f.targetFood) === -1) f.targetFood = null;
    if(!f.targetFood){
      let best=null, bd=15;
      for(const fd of foods){
        const d = pos.distanceTo(fd.mesh.position);
        if(d<bd){ bd=d; best=fd; }
      }
      f.targetFood = best;
    }
    if(f.targetFood){
      chasing = true;
      _tv.copy(f.targetFood.mesh.position).sub(pos).normalize();
      vel.addScaledVector(_tv, 6.5*dt);
    }else{
      f.wanderTimer = (f.wanderTimer ?? Math.random()*3) - dt;
      if(f.wanderTimer <= 0){
        f.wanderTimer = 1.5 + Math.random()*3;
        _tv.set(Math.random()-0.5,(Math.random()-0.5)*0.5,Math.random()-0.5).normalize();
        vel.addScaledVector(_tv, f.speed*0.9);
      }
    }

    // Избегание других рыбок
    for(let j=i+1;j<n;j++){
      const o = fishArray[j];
      const dx=pos.x-o.mesh.position.x, dy=pos.y-o.mesh.position.y, dz=pos.z-o.mesh.position.z;
      const rr=(f.avoidanceRadius+o.avoidanceRadius)*0.62;
      const d2=dx*dx+dy*dy+dz*dz;
      if(d2<rr*rr && d2>1e-4){
        const d=Math.sqrt(d2), push=(1-d/rr)*3.2*dt/d;
        vel.x+=dx*push; vel.y+=dy*push; vel.z+=dz*push;
        o.velocity.x-=dx*push; o.velocity.y-=dy*push; o.velocity.z-=dz*push;
      }
    }

    // Плавный разворот у стенок
    const m=2.6, tf=7.5*dt;
    if(pos.x < -HW+m) vel.x += tf; else if(pos.x > HW-m) vel.x -= tf;
    if(pos.z < -HD+m) vel.z += tf; else if(pos.z > HD-m) vel.z -= tf;
    if(pos.y < 1.6) vel.y += tf; else if(pos.y > TANK.H-1.8) vel.y -= tf;

    // Лимит скорости
    const maxS = chasing ? f.speed*1.9 : f.speed*1.15;
    const minS = f.speed*0.45;
    const sp = vel.length();
    if(sp>maxS) vel.multiplyScalar(maxS/sp);
    else if(sp<minS && sp>1e-4) vel.multiplyScalar(minS/sp);

    pos.addScaledVector(vel, dt);
    pos.x = THREE.MathUtils.clamp(pos.x, -HW+0.7, HW-0.7);
    pos.z = THREE.MathUtils.clamp(pos.z, -HD+0.7, HD-0.7);
    pos.y = THREE.MathUtils.clamp(pos.y, 1.0, TANK.H-1.2);

    // Поворот в сторону движения
    const vlen = vel.length();
    if(vlen>0.05){
      const yaw   = Math.atan2(-vel.z, vel.x);
      const pitch  = Math.asin(THREE.MathUtils.clamp(vel.y/vlen, -1, 1));
      _te.set(0, yaw, pitch, 'YZX');
      _tq.setFromEuler(_te);
      f.mesh.quaternion.slerp(_tq, Math.min(1, 4.5*dt));
    }

    // Поглощение корма + рост
    if(f.targetFood){
      if(pos.distanceTo(f.targetFood.mesh.position) < 1.15){
        const idx = foods.indexOf(f.targetFood);
        if(idx!==-1){ scene.remove(foods[idx].mesh); foods.splice(idx,1); }
        f.targetFood = null;
        f.baseScale = Math.min(f.baseScale*1.05, 2.1);
        f.mesh.scale.setScalar(f.baseScale);
      }
    }

    // Анимация хвоста и плавников
    f.tail.rotation.z = Math.sin(t*f.tailSpeed + f.phase)*0.5;
    f.leftFin.rotation.x  = 0.5 + Math.sin(t*4.2 + f.phase)*0.28;
    f.rightFin.rotation.x = 0.5 + Math.sin(t*4.2 + f.phase + Math.PI)*0.28;
  }
}

/* ================= КЛИК → КОРМ ================= */
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
const floorPlane = new THREE.Plane(new THREE.Vector3(0,1,0), 0);
const hitPoint = new THREE.Vector3();
let downX=0, downY=0;

renderer.domElement.addEventListener('pointerdown', e=>{ downX=e.clientX; downY=e.clientY; });
renderer.domElement.addEventListener('pointerup', e=>{
  if(Math.hypot(e.clientX-downX, e.clientY-downY) > 6) return;   // было вращение
  ndc.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1);
  raycaster.setFromCamera(ndc, camera);
  if(raycaster.ray.intersectPlane(floorPlane, hitPoint)){
    spawnFood(
      THREE.MathUtils.clamp(hitPoint.x, -HW+1.2, HW-1.2),
      THREE.MathUtils.clamp(hitPoint.z, -HD+1.2, HD-1.2)
    );
  }
});

/* ================= КНОПКИ ================= */
document.getElementById('btnAddFish').onclick = ()=> addFish();
document.getElementById('btnBubbles').onclick = ()=>{ for(let i=0;i<10;i++) addBubble(); };

let lightOn = true;
document.getElementById('btnLight').onclick = (e)=>{
  lightOn = !lightOn;
  sun.intensity     = lightOn ? 1.15 : 0.12;
  ambient.intensity   = lightOn ? 0.4  : 0.16;
  e.currentTarget.textContent = lightOn ? '💡 Свет' : '🌙 Свет';
};

/* ================= ЦИКЛ ================= */
const clock = new THREE.Clock();
let elapsed=0, frames=0, fpsTimer=0;

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  elapsed += dt;

  updateFish(dt, elapsed);
  updateFoods(dt);
  updateBubbles(elapsed, dt);

  for(const p of plants){
    p.group.rotation.x = Math.sin(elapsed*0.9 + p.phase)*0.07;
    p.group.rotation.z = Math.cos(elapsed*0.7 + p.phase)*0.07;
  }

  controls.update();
  renderer.render(scene, camera);

  frames++; fpsTimer += dt;
  if(fpsTimer >= 0.5){
    document.getElementById('statFps').textContent = Math.round(frames/fpsTimer);
    frames = 0; fpsTimer = 0;
  }
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

**Что внутри:**

- **15 рыбок** из 8 цветовых схем, с телом‑эллипсоидом, глазами со зрачками, машущим хвостом (поворот по Z) и боковыми плавниками. Размер 0.6–1.2, у каждой свои скорость, фаза и радиус избегания.
- **ИИ:** разлёт при сближении, плавный разворот у стенок, случайное блуждание, преследование корма в радиусе 15, рост на 5 % после поедания.
- **Окружение:** стеклянная коробка 36×24×20 с `transmission: 0.95` и wireframe‑рамкой, процедурное песчаное дно, 8 деформированных камней, 12 покачивающихся водорослей на `TubeGeometry` + `CatmullRomCurve3`.
- **30 пузырей** с подъёмом и «змейкой», сброс на дно; **+10** по кнопке.
- **Корм:** клик по воде (raycast на плоскость дна) роняет гранулу с гравитацией; рыбки атакуют, на дне — исчезает.
- **Свет:** ambient 0.4, направленный с тенями 2048² (PCFSoft), два подводных point‑light; кнопка **Свет** гасит основной свет.
- **Камера:** OrbitControls с damping, зум 10–60, `maxPolarAngle = π/1.8`.
- **UI:** glass‑панели (blur), градиентный заголовок, подсказки, счётчик рыбок и FPS, три кнопки.
- **Эффекты:** `FogExp2` как вода, CSS‑градиент фона, ACES‑тонмаппинг, мягкие тени.

**Как пользоваться:** открыть файл, вращать/зумить мышью, кликать по воде чтобы кормить, добавлять рыбок/пузыри и переключать свет кнопками.