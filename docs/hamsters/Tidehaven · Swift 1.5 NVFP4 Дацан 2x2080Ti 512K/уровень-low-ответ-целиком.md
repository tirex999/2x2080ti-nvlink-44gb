```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Tidehaven</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#1a1a2e;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;color:#fff}
canvas{display:block}
#ui{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10}
#title-panel{position:absolute;top:20px;left:20px;pointer-events:auto;background:rgba(10,15,30,0.55);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.12);border-radius:16px;padding:18px 24px;max-width:320px}
#title-panel h1{font-size:28px;font-weight:700;letter-spacing:1px;background:linear-gradient(135deg,#f8d8a0,#f0a050);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:4px}
#title-panel p{font-size:12px;color:rgba(255,255,255,0.6);line-height:1.4}
#controls{position:absolute;top:20px;right:20px;pointer-events:auto;display:flex;flex-direction:column;gap:8px;max-height:calc(100vh - 40px);overflow-y:auto;scrollbar-width:none}
#controls::-webkit-scrollbar{display:none}
.panel{background:rgba(10,15,30,0.55);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.12);border-radius:12px;padding:12px 16px;min-width:200px}
.panel-title{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:rgba(255,255,255,0.45);margin-bottom:8px;font-weight:600}
.btn{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#fff;padding:7px 14px;border-radius:8px;cursor:pointer;font-size:12px;font-family:inherit;transition:all .2s;display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.btn:hover{background:rgba(255,255,255,0.15);border-color:rgba(255,255,255,0.3)}
.btn.active{background:rgba(248,216,160,0.2);border-color:rgba(248,216,160,0.5);color:#f8d8a0}
.btn-row{display:flex;gap:6px;flex-wrap:wrap}
.slider-row{display:flex;align-items:center;gap:8px;margin:4px 0}
.slider-row label{font-size:11px;color:rgba(255,255,255,0.6);min-width:40px}
.slider-row input[type=range]{flex:1;height:4px;-webkit-appearance:none;appearance:none;background:rgba(255,255,255,0.15);border-radius:2px;outline:none}
.slider-row input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:#f8d8a0;cursor:pointer;border:2px solid rgba(0,0,0,0.3)}
#mobile-toggle{display:none;position:fixed;bottom:20px;right:20px;z-index:20;pointer-events:auto;background:rgba(10,15,30,0.7);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.2);border-radius:50%;width:48px;height:48px;font-size:20px;cursor:pointer;color:#fff}
@media(max-width:768px){
#title-panel{top:10px;left:10px;padding:12px 16px;max-width:200px}
#title-panel h1{font-size:20px}
#title-panel p{font-size:10px}
#controls{top:auto;bottom:80px;right:10px;left:10px;max-height:50vh;transform:translateY(120%);transition:transform .3s}
#controls.open{transform:translateY(0)}
#mobile-toggle{display:flex;align-items:center;justify-content:center}
}
#loading{position:fixed;top:0;left:0;width:100%;height:100%;background:#1a1a2e;display:flex;align-items:center;justify-content:center;z-index:100;transition:opacity .8s}
#loading span{font-size:18px;color:rgba(255,255,255,0.6);letter-spacing:2px}
</style>
</head>
<body>
<div id="loading"><span>Tidehaven...</span></div>
<div id="ui">
  <div id="title-panel">
    <h1>Tidehaven</h1>
    <p>A cozy island diorama with a living underwater world. Explore above and below the waves.</p>
  </div>
  <div id="controls">
    <div class="panel">
      <div class="panel-title">Camera</div>
      <div class="btn-row">
        <button class="btn active" data-cam="iso">Isometric</button>
        <button class="btn" data-cam="cabin">Cabin</button>
        <button class="btn" data-cam="under">Underwater</button>
        <button class="btn" data-cam="free">Free</button>
      </div>
    </div>
    <div class="panel">
      <div class="panel-title">Actions</div>
      <div class="btn-row">
        <button class="btn" id="btn-kayak">🛶 Kayak</button>
        <button class="btn" id="btn-ray">🐟 Ray Leap</button>
      </div>
    </div>
    <div class="panel">
      <div class="panel-title">Environment</div>
      <div class="slider-row"><label>Tide</label><input type="range" id="sl-tide" min="-1" max="1" step="0.01" value="0"></div>
      <div class="slider-row"><label>Wind</label><input type="range" id="sl-wind" min="0" max="1" step="0.01" value="0.3"></div>
    </div>
    <div class="panel">
      <div class="panel-title">Time of Day</div>
      <div class="btn-row">
        <button class="btn active" data-time="day">☀️ Day</button>
        <button class="btn" data-time="sunset">🌅 Sunset</button>
        <button class="btn" data-time="night">🌙 Night</button>
      </div>
    </div>
    <div class="panel">
      <div class="panel-title">Audio</div>
      <div class="btn-row">
        <button class="btn" id="btn-music">🎵 Music</button>
      </div>
      <div class="slider-row"><label>Vol</label><input type="range" id="sl-vol" min="0" max="1" step="0.01" value="0.5"></div>
    </div>
    <div class="panel">
      <div class="panel-title">World</div>
      <div class="btn-row">
        <button class="btn" id="btn-pause">⏸ Pause</button>
        <button class="btn" id="btn-reset">🔄 Reset</button>
      </div>
    </div>
  </div>
</div>
<button id="mobile-toggle">⚙</button>

<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}
</script>
<script type="module">
import*as THREE from'three';
import{OrbitControls}from'three/addons/controls/OrbitControls.js';

/* ============================================================
   GLOBALS & STATE
   ============================================================ */
let scene,camera,renderer,controls,clock;
let paused=false,audioStarted=false,musicOn=false;
let timeOfDay=0,targetTimeOfDay=0; // 0=day,1=sunset,2=night
let tideLevel=0,targetTide=0;
let windStrength=0.3,targetWind=0.3;
let kayakLaunched=false,kayakAngle=0,kayakTarget=null;
let rayLeaping=false,rayLeapT=0;
let waterSurface,waterVolume,glassFront,glassRight;
let seabed,causticMat;
let rays=[],fishSchools=[],waterPlants=[],bubbles=[];
let trees=[],lanterns=[],cabinWindows=[];
let kayak,rayMesh;
let sunLight,ambientLight,pointLights=[];
let skyColor=new THREE.Color(0x87ceeb);
let targetSkyColor=new THREE.Color(0x87ceeb);
let waterLevelY=0;
const WATER_BASE=0;
const DIORAMA_W=22,DIORAMA_H=12,DIORAMA_D=22;
let audioCtx,masterGain,musicGain,sfxGain;
let musicNodes=[];
let droplets=[],ripples=[];
let frameCount=0;

/* ============================================================
   INIT
   ============================================================ */
function init(){
  clock=new THREE.Clock();
  scene=new THREE.Scene();
  scene.fog=new THREE.FogExp2(0x87ceeb,0.008);

  camera=new THREE.PerspectiveCamera(45,window.innerWidth/window.innerHeight,0.1,200);
  camera.position.set(18,14,18);

  renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});
  renderer.setSize(window.innerWidth,window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.1;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  document.body.appendChild(renderer.domElement);

  controls=new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true;
  controls.dampingFactor=0.05;
  controls.target.set(0,1,0);
  controls.maxPolarAngle=Math.PI*0.85;
  controls.minDistance=8;
  controls.maxDistance=50;

  setupLighting();
  createDiorama();
  createIsland();
  createCabin();
  createPier();
  createWater();
  createUnderwaterLife();
  createDecorations();
  createKayak();
  createBubbles();

  setupUI();
  setupAudio();

  window.addEventListener('resize',onResize);
  renderer.domElement.addEventListener('click',()=>{if(!audioStarted)initAudio()});

  setTimeout(()=>{
    document.getElementById('loading').style.opacity='0';
    setTimeout(()=>document.getElementById('loading').style.display='none',800);
  },500);

  animate();
}

/* ============================================================
   LIGHTING
   ============================================================ */
function setupLighting(){
  ambientLight=new THREE.AmbientLight(0x405060,0.6);
  scene.add(ambientLight);

  sunLight=new THREE.DirectionalLight(0xfff0d0,1.5);
  sunLight.position.set(10,20,8);
  sunLight.castShadow=true;
  sunLight.shadow.mapSize.set(2048,2048);
  sunLight.shadow.camera.near=1;
  sunLight.shadow.camera.far=60;
  sunLight.shadow.camera.left=-15;
  sunLight.shadow.camera.right=15;
  sunLight.shadow.camera.top=15;
  sunLight.shadow.camera.bottom=-15;
  sunLight.shadow.bias=-0.001;
  scene.add(sunLight);

  const hemi=new THREE.HemisphereLight(0x87ceeb,0x3d5c3a,0.4);
  scene.add(hemi);

  // Cabin window light
  const cabinLight=new THREE.PointLight(0xffa040,0,8);
  cabinLight.position.set(0,2.5,0);
  scene.add(cabinLight);
  pointLights.push(cabinLight);

  // Lantern lights
  const lanternPositions=[
    new THREE.Vector3(4,2.8,6),
    new THREE.Vector3(4,2.8,9),
    new THREE.Vector3(4,2.8,12),
    new THREE.Vector3(-2,2.2,0.5),
    new THREE.Vector3(2,2.2,0.5)
  ];
  lanternPositions.forEach(p=>{
    const l=new THREE.PointLight(0xffa040,0,5);
    l.position.copy(p);
    scene.add(l);
    pointLights.push(l);
  });
}

/* ============================================================
   DIORAMA SHELL
   ============================================================ */
function createDiorama(){
  // Back wall
  const wallMat=new THREE.MeshStandardMaterial({color:0x2a3a4a,roughness:0.8});
  const backWall=new THREE.Mesh(new THREE.PlaneGeometry(DIORAMA_W,DIORAMA_H),wallMat);
  backWall.position.set(0,DIORAMA_H/2-DIORAMA_H/2,-DIORAMA_D/2);
  backWall.receiveShadow=true;
  scene.add(backWall);

  // Left wall
  const leftWall=new THREE.Mesh(new THREE.PlaneGeometry(DIORAMA_D,DIORAMA_H),wallMat);
  leftWall.position.set(-DIORAMA_W/2,0,0);
  leftWall.rotation.y=Math.PI/2;
  leftWall.receiveShadow=true;
  scene.add(leftWall);

  // Floor
  const floorMat=new THREE.MeshStandardMaterial({color:0x1a2530,roughness:0.9});
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(DIORAMA_W,DIORAMA_D),floorMat);
  floor.rotation.x=-Math.PI/2;
  floor.position.y=-DIORAMA_H/2;
  floor.receiveShadow=true;
  scene.add(floor);

  // Glass front
  const glassMat=new THREE.MeshPhysicalMaterial({
    color:0xffffff,transparent:true,opacity:0.08,
    roughness:0.05,metalness:0,transmission:0.95,
    thickness:0.1,side:THREE.DoubleSide
  });
  glassFront=new THREE.Mesh(new THREE.PlaneGeometry(DIORAMA_W,DIORAMA_H),glassMat);
  glassFront.position.set(0,0,DIORAMA_D/2);
  glassFront.renderOrder=100;
  scene.add(glassFront);

  // Glass right
  glassRight=new THREE.Mesh(new THREE.PlaneGeometry(DIORAMA_D,DIORAMA_H),glassMat.clone());
  glassRight.position.set(DIORAMA_W/2,0,0);
  glassRight.rotation.y=-Math.PI/2;
  glassRight.renderOrder=100;
  scene.add(glassRight);

  // Frame edges
  const frameMat=new THREE.MeshStandardMaterial({color:0x3a4a5a,roughness:0.5,metalness:0.3});
  const frameGeo=new THREE.BoxGeometry(0.15,DIORAMA_H,0.15);
  [[-DIORAMA_W/2,0,DIORAMA_D/2],[DIORAMA_W/2,0,DIORAMA_D/2],[DIORAMA_W/2,0,-DIORAMA_D/2],[-DIORAMA_W/2,0,-DIORAMA_D/2]].forEach(p=>{
    const f=new THREE.Mesh(frameGeo,frameMat);
    f.position.set(p[0],0,p[2]);
    scene.add(f);
  });
  // Top frame
  const topFrameGeo1=new THREE.BoxGeometry(DIORAMA_W,0.15,0.15);
  const topFrameGeo2=new THREE.BoxGeometry(0.15,0.15,DIORAMA_D);
  [DIORAMA_H/2,-DIORAMA_H/2].forEach(y=>{
    const f1=new THREE.Mesh(topFrameGeo1,frameMat);f1.position.set(0,y,DIORAMA_D/2);scene.add(f1);
    const f2=new THREE.Mesh(topFrameGeo1,frameMat);f2.position.set(0,y,-DIORAMA_D/2);scene.add(f2);
    const f3=new THREE.Mesh(topFrameGeo2,frameMat);f3.position.set(DIORAMA_W/2,y,0);scene.add(f3);
    const f4=new THREE.Mesh(topFrameGeo2,frameMat);f4.position.set(-DIORAMA_W/2,y,0);scene.add(f4);
  });
}

/* ============================================================
   ISLAND
   ============================================================ */
function createIsland(){
  const islandGroup=new THREE.Group();

  // Main island body - layered approach
  const islandShape=new THREE.Shape();
  const pts=[];
  for(let i=0;i<32;i++){
    const a=i/32*Math.PI*2;
    const r=5+Math.sin(a*3)*0.8+Math.cos(a*5)*0.5+Math.sin(a*7)*0.3;
    pts.push(new THREE.Vector2(Math.cos(a)*r,Math.sin(a)*r));
  }
  islandShape.setFromPoints(pts);

  // Island top (grass/sand)
  const topGeo=new THREE.ShapeGeometry(islandShape,16);
  const topMat=new THREE.MeshStandardMaterial({color:0x5a8a3a,roughness:0.9});
  const top=new THREE.Mesh(topGeo,topMat);
  top.rotation.x=-Math.PI/2;
  top.position.y=2.5;
  top.receiveShadow=true;
  top.castShadow=true;
  islandGroup.add(top);

  // Island sides (cliff/sand)
  const sideGeo=new THREE.ExtrudeGeometry(islandShape,{depth:6,bevelEnabled:false});
  const sideMat=new THREE.MeshStandardMaterial({color:0x8a7a5a,roughness:0.9});
  const side=new THREE.Mesh(sideGeo,sideMat);
  side.rotation.x=-Math.PI/2;
  side.position.y=2.5;
  side.castShadow=true;
  side.receiveShadow=true;
  islandGroup.add(side);

  // Sandy shore ring
  const shoreShape=new THREE.Shape();
  const shorePts=[];
  for(let i=0;i<32;i++){
    const a=i/32*Math.PI*2;
    const r=5.5+Math.sin(a*3)*0.8+Math.cos(a*5)*0.5+Math.sin(a*7)*0.3+0.5;
    shorePts.push(new THREE.Vector2(Math.cos(a)*r,Math.sin(a)*r));
  }
  shoreShape.setFromPoints(shorePts);
  shoreShape.holes.push(islandShape);
  const shoreGeo=new THREE.ShapeGeometry(shoreShape,16);
  const shoreMat=new THREE.MeshStandardMaterial({color:0xd4b896,roughness:0.95});
  const shore=new THREE.Mesh(shoreGeo,shoreMat);
  shore.rotation.x=-Math.PI/2;
  shore.position.y=2.2;
  shore.receiveShadow=true;
  islandGroup.add(shore);

  // Underwater base (sandy slope)
  const baseShape=new THREE.Shape();
  const basePts=[];
  for(let i=0;i<32;i++){
    const a=i/32*Math.PI*2;
    const r=7+Math.sin(a*3)*1.2+Math.cos(a*5)*0.7;
    basePts.push(new THREE.Vector2(Math.cos(a)*r,Math.sin(a)*r));
  }
  baseShape.setFromPoints(basePts);
  const baseGeo=new THREE.ExtrudeGeometry(baseShape,{depth:3,bevelEnabled:false});
  const baseMat=new THREE.MeshStandardMaterial({color:0xc4a876,roughness:0.95});
  const base=new THREE.Mesh(baseGeo,baseMat);
  base.rotation.x=-Math.PI/2;
  base.position.y=-0.5;
  base.receiveShadow=true;
  islandGroup.add(base);

  // Rocks (instanced)
  const rockGeo=new THREE.DodecahedronGeometry(0.4,0);
  const rockMat=new THREE.MeshStandardMaterial({color:0x6a6a6a,roughness:0.9});
  const rockCount=25;
  const rockMesh=new THREE.InstancedMesh(rockGeo,rockMat,rockCount);
  const dummy=new THREE.Object3D();
  for(let i=0;i<rockCount;i++){
    const a=Math.random()*Math.PI*2;
    const r=4.5+Math.random()*2;
    dummy.position.set(Math.cos(a)*r,2+Math.random()*0.5,Math.sin(a)*r);
    dummy.scale.setScalar(0.5+Math.random()*1);
    dummy.rotation.set(Math.random()*Math.PI,Math.random()*Math.PI,Math.random()*Math.PI);
    dummy.updateMatrix();
    rockMesh.setMatrixAt(i,dummy.matrix);
  }
  rockMesh.castShadow=true;
  rockMesh.receiveShadow=true;
  islandGroup.add(rockMesh);

  // Trees (instanced cones + cylinders)
  const trunkGeo=new THREE.CylinderGeometry(0.08,0.12,1,6);
  const trunkMat=new THREE.MeshStandardMaterial({color:0x6b4226,roughness:0.9});
  const foliageGeo=new THREE.ConeGeometry(0.6,1.5,6);
  const foliageMat=new THREE.MeshStandardMaterial({color:0x3a7a2a,roughness:0.8});

  const treePositions=[
    [-2,2.5,-2],[-3,2.5,1],[-1.5,2.5,-3],[1.5,2.5,-2.5],
    [-2.5,2.5,2],[2,2.5,-1],[-1,2.5,2.5],[3,2.5,-2],
    [-3.5,2.5,-1],[0,2.5,-3.5]
  ];
  treePositions.forEach(p=>{
    const trunk=new THREE.Mesh(trunkGeo,trunkMat);
    trunk.position.set(p[0],p[1]+0.5,p[2]);
    trunk.castShadow=true;
    islandGroup.add(trunk);
    trees.push(trunk);

    const foliage=new THREE.Mesh(foliageGeo,foliageMat);
    foliage.position.set(p[0],p[1]+1.8,p[2]);
    foliage.castShadow=true;
    islandGroup.add(foliage);
    trees.push(foliage);
  });

  // Grass patches (instanced small cones)
  const grassGeo=new THREE.ConeGeometry(0.05,0.3,4);
  const grassMat=new THREE.MeshStandardMaterial({color:0x4a9a3a,roughness:0.9});
  const grassCount=80;
  const grassMesh=new THREE.InstancedMesh(grassGeo,grassMat,grassCount);
  for(let i=0;i<grassCount;i++){
    const a=Math.random()*Math.PI*2;
    const r=Math.random()*4;
    dummy.position.set(Math.cos(a)*r,2.65,Math.sin(a)*r);
    dummy.scale.set(1,0.8+Math.random()*0.6,1);
    dummy.rotation.set(0,Math.random()*Math.PI,0);
    dummy.updateMatrix();
    grassMesh.setMatrixAt(i,dummy.matrix);
  }
  islandGroup.add(grassMesh);

  scene.add(islandGroup);
}

/* ============================================================
   CABIN
   ============================================================ */
function createCabin(){
  const cabin=new THREE.Group();
  cabin.position.set(0,2.5,0);

  // A-frame walls
  const wallMat=new THREE.MeshStandardMaterial({color:0x8b6b4a,roughness:0.85});
  const roofMat=new THREE.MeshStandardMaterial({color:0x4a8a7a,roughness:0.4,metalness:0.6});

  // Front triangle
  const triShape=new THREE.Shape();
  triShape.moveTo(-1.5,0);
  triShape.lineTo(1.5,0);
  triShape.lineTo(0,3);
  triShape.closePath();

  const frontTri=new THREE.Mesh(new THREE.ShapeGeometry(triShape),wallMat);
  frontTri.position.z=1.2;
  frontTri.castShadow=true;
  cabin.add(frontTri);

  const backTri=new THREE.Mesh(new THREE.ShapeGeometry(triShape),wallMat);
  backTri.position.z=-1.2;
  backTri.castShadow=true;
  cabin.add(backTri);

  // Roof panels (copper)
  const roofW=Math.sqrt(1.5*1.5+3*3);
  const roofGeo=new THREE.PlaneGeometry(roofW,2.4);

  const roofL=new THREE.Mesh(roofGeo,roofMat);
  roofL.position.set(-0.75,1.5,0);
  roofL.rotation.z=Math.atan2(3,1.5);
  roofL.rotation.x=0;
  roofL.castShadow=true;
  cabin.add(roofL);

  const roofR=new THREE.Mesh(roofGeo,roofMat);
  roofR.position.set(0.75,1.5,0);
  roofR.rotation.z=-Math.atan2(3,1.5);
  roofR.castShadow=true;
  cabin.add(roofR);

  // Floor
  const floorGeo=new THREE.BoxGeometry(3,0.1,2.4);
  const floor=new THREE.Mesh(floorGeo,wallMat);
  floor.position.y=0.05;
  floor.receiveShadow=true;
  cabin.add(floor);

  // Door
  const doorGeo=new THREE.PlaneGeometry(0.7,1.4);
  const doorMat=new THREE.MeshStandardMaterial({color:0x5a3a1a,roughness:0.9});
  const door=new THREE.Mesh(doorGeo,doorMat);
  door.position.set(0,0.75,1.21);
  cabin.add(door);

  // Windows (glowing)
  const winGeo=new THREE.PlaneGeometry(0.5,0.5);
  const winMat=new THREE.MeshStandardMaterial({color:0xffa040,emissive:0xffa040,emissiveIntensity:0,transparent:true,opacity:0.9});
  cabinWindows=[];
  [[-0.6,1.2,1.21],[0.6,1.2,1.21],[-0.6,1.2,-1.21],[0.6,1.2,-1.21]].forEach(p=>{
    const w=new THREE.Mesh(winGeo,winMat.clone());
    w.position.set(p[0],p[1],p[2]);
    cabin.add(w);
    cabinWindows.push(w);
  });

  // Deck
  const deckGeo=new THREE.BoxGeometry(4,0.12,2);
  const deckMat=new THREE.MeshStandardMaterial({color:0x9a7a5a,roughness:0.9});
  const deck=new THREE.Mesh(deckGeo,deckMat);
  deck.position.set(0,0.06,2.2);
  deck.receiveShadow=true;
  deck.castShadow=true;
  cabin.add(deck);

  // Deck railing
  const railMat=new THREE.MeshStandardMaterial({color:0x7a5a3a,roughness:0.85});
  const railGeo=new THREE.CylinderGeometry(0.04,0.04,0.8,6);
  [[-1.9,0.4,3.2],[1.9,0.4,3.2],[-1.9,0.4,1.2],[1.9,0.4,1.2]].forEach(p=>{
    const r=new THREE.Mesh(railGeo,railMat);
    r.position.set(p[0],p[1],p[2]);
    cabin.add(r);
  });
  // Top rail
  const topRailGeo=new THREE.BoxGeometry(3.8,0.06,0.06);
  const topRail=new THREE.Mesh(topRailGeo,railMat);
  topRail.position.set(0,0.8,3.2);
  cabin.add(topRail);

  scene.add(cabin);
}

/* ============================================================
   PIER
   ============================================================ */
function createPier(){
  const pier=new THREE.Group();
  const woodMat=new THREE.MeshStandardMaterial({color:0x8a6a4a,roughness:0.9});
  const darkWoodMat=new THREE.MeshStandardMaterial({color:0x5a4030,roughness:0.9});

  // Pier planks
  const plankGeo=new THREE.BoxGeometry(1.8,0.08,0.35);
  for(let i=0;i<14;i++){
    const plank=new THREE.Mesh(plankGeo,woodMat);
    plank.position.set(3.5,2.3,3+i*0.4);
    plank.castShadow=true;
    plank.receiveShadow=true;
    pier.add(plank);
  }

  // Pier posts
  const postGeo=new THREE.CylinderGeometry(0.08,0.1,5,6);
  [[2.6,0,4.5],[4.4,0,4.5],[2.6,0,7],[4.4,0,7],[2.6,0,9.5],[4.4,0,9.5]].forEach(p=>{
    const post=new THREE.Mesh(postGeo,darkWoodMat);
    post.position.set(p[0],p[1],p[2]);
    post.castShadow=true;
    pier.add(post);
  });

  // Ladder at end
  const ladderMat=new THREE.MeshStandardMaterial({color:0x6a5a3a,roughness:0.85});
  const ladderSideGeo=new THREE.BoxGeometry(0.06,3,0.06);
  const ladderRungGeo=new THREE.BoxGeometry(0.5,0.05,0.05);
  const lx=3.5,lz=9.8;
  const ls1=new THREE.Mesh(ladderSideGeo,ladderMat);
  ls1.position.set(lx-0.25,0.8,lz);
  pier.add(ls1);
  const ls2=new THREE.Mesh(ladderSideGeo,ladderMat);
  ls2.position.set(lx+0.25,0.8,lz);
  pier.add(ls2);
  for(let i=0;i<5;i++){
    const rung=new THREE.Mesh(ladderRungGeo,ladderMat);
    rung.position.set(lx,2.2-i*0.6,lz);
    pier.add(rung);
  }

  // Lanterns on pier
  const lanternGeo=new THREE.SphereGeometry(0.12,8,6);
  const lanternMat=new THREE.MeshStandardMaterial({color:0xffcc60,emissive:0xffa040,emissiveIntensity:0,transparent:true,opacity:0.9});
  const lanternPoleGeo=new THREE.CylinderGeometry(0.03,0.03,1.2,6);
  [[2.5,2.8,5],[4.5,2.8,5],[2.5,2.8,8],[4.5,2.8,8]].forEach((p,i)=>{
    const pole=new THREE.Mesh(lanternPoleGeo,darkWoodMat);
    pole.position.set(p[0],p[1]-0.6,p[2]);
    pier.add(pole);
    const lantern=new THREE.Mesh(lanternGeo,lanternMat.clone());
    lantern.position.set(p[0],p[1],p[2]);
    pier.add(lantern);
    lanterns.push(lantern);
  });

  scene.add(pier);
}

/* ============================================================
   WATER SYSTEM (CUTAWAY)
   ============================================================ */
function createWater(){
  // Water surface with waves
  const waterGeo=new THREE.PlaneGeometry(DIORAMA_W,DIORAMA_D,64,64);
  const waterMat=new THREE.ShaderMaterial({
    transparent:true,
    depthWrite:false,
    side:THREE.DoubleSide,
    uniforms:{
      uTime:{value:0},
      uWind:{value:0.3},
      uTide:{value:0},
      uColor1:{value:new THREE.Color(0x40c8c8)},
      uColor2:{value:new THREE.Color(0x1a6a8a)},
      uOpacity:{value:0.55}
    },
    vertexShader:`
      uniform float uTime;
      uniform float uWind;
      varying vec2 vUv;
      varying float vWave;
      void main(){
        vUv=uv;
        vec3 pos=position;
        float w1=sin(pos.x*2.0+uTime*1.5)*0.08*uWind;
        float w2=sin(pos.y*3.0+uTime*2.0)*0.05*uWind;
        float w3=sin((pos.x+pos.y)*1.5+uTime*1.0)*0.06*uWind;
        pos.z+=w1+w2+w3;
        vWave=w1+w2+w3;
        gl_Position=projectionMatrix*modelViewMatrix*vec4(pos,1.0);
      }
    `,
    fragmentShader:`
      uniform vec3 uColor1;
      uniform vec3 uColor2;
      uniform float uOpacity;
      uniform float uTime;
      varying vec2 vUv;
      varying float vWave;
      void main(){
        vec3 col=mix(uColor1,uColor2,vUv.y*0.5+vWave*2.0+0.3);
        // Foam at edges
        float edge=min(min(vUv.x,1.0-vUv.x),min(vUv.y,1.0-vUv.y));
        float foam=smoothstep(0.0,0.05,edge);
        col=mix(vec3(0.9,0.95,1.0),col,foam);
        float alpha=uOpacity*(1.0-smoothstep(0.0,0.03,edge)*0.3);
        gl_FragColor=vec4(col,alpha);
      }
    `
  });
  waterSurface=new THREE.Mesh(waterGeo,waterMat);
  waterSurface.rotation.x=-Math.PI/2;
  waterSurface.position.y=WATER_BASE;
  waterSurface.renderOrder=50;
  scene.add(waterSurface);

  // Water volume (the body of water)
  const volGeo=new THREE.BoxGeometry(DIORAMA_W-0.1,DIORAMA_H/2,DIORAMA_D-0.1);
  const volMat=new THREE.MeshStandardMaterial({
    color:0x2a8a9a,transparent:true,opacity:0.18,
    roughness:0.1,metalness:0,side:THREE.BackSide,
    depthWrite:false
  });
  waterVolume=new THREE.Mesh(volGeo,volMat);
  waterVolume.position.y=-DIORAMA_H/4;
  waterVolume.renderOrder=10;
  scene.add(waterVolume);

  // Seabed with caustics
  const seabedGeo=new THREE.PlaneGeometry(DIORAMA_W,DIORAMA_D,32,32);
  causticMat=new THREE.ShaderMaterial({
    transparent:true,
    depthWrite:false,
    uniforms:{
      uTime:{value:0},
      uBaseColor:{value:new THREE.Color(0xc4a876)}
    },
    vertexShader:`
      varying vec2 vUv;
      void main(){
        vUv=uv;
        gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);
      }
    `,
    fragmentShader:`
      uniform float uTime;
      uniform vec3 uBaseColor;
      varying vec2 vUv;
      float caustic(vec2 uv,float t){
        vec2 p=uv*8.0;
        float c=0.0;
        c+=sin(p.x+t*0.7)*sin(p.y+t*0.5)*0.5+0.5;
        c+=sin(p.x*1.5-t*0.3)*sin(p.y*1.3+t*0.8)*0.3;
        c+=sin((p.x+p.y)*0.8+t*0.6)*0.2;
        return smoothstep(0.6,1.2,c);
      }
      void main(){
        float c=caustic(vUv,uTime);
        vec3 col=uBaseColor+c*vec3(0.3,0.4,0.2);
        gl_FragColor=vec4(col,0.9);
      }
    `
  });
  seabed=new THREE.Mesh(seabedGeo,causticMat);
  seabed.rotation.x=-Math.PI/2;
  seabed.position.y=-DIORAMA_H/2+0.05;
  seabed.renderOrder=5;
  scene.add(seabed);

  // Shore foam ring
  const foamGeo=new THREE.RingGeometry(5.8,6.8,48);
  const foamMat=new THREE.MeshStandardMaterial({
    color:0xffffff,transparent:true,opacity:0.4,
    side:THREE.DoubleSide,depthWrite:false
  });
  const foam=new THREE.Mesh(foamGeo,foamMat);
  foam.rotation.x=-Math.PI/2;
  foam.position.y=WATER_BASE+0.02;
  foam.renderOrder=55;
  scene.add(foam);
}

/* ============================================================
   UNDERWATER LIFE
   ============================================================ */
function createUnderwaterLife(){
  // Rays
  const rayGeo=createRayGeometry();
  const rayMat=new THREE.MeshStandardMaterial({color:0x6a7a8a,roughness:0.7,side:THREE.DoubleSide});

  for(let i=0;i<3;i++){
    const ray=new THREE.Mesh(rayGeo,rayMat.clone());
    ray.position.set(
      -6+i*4,
      -2-Math.random()*2,
      -5+i*3
    );
    ray.userData={
      basePos:ray.position.clone(),
      phase:Math.random()*Math.PI*2,
      speed:0.3+Math.random()*0.2,
      radius:3+Math.random()*2,
      isLeaper:i===0
    };
    scene.add(ray);
    rays.push(ray);
  }
  rayMesh=rays[0];

  // Fish schools (instanced)
  const fishGeo=createFishGeometry();
  const fishColors=[0xff8844,0x44aaff,0xffcc44,0x44ff88,0xff44aa];
  for(let s=0;s<5;s++){
    const count=15;
    const fishMat=new THREE.MeshStandardMaterial({color:fishColors[s],roughness:0.6});
    const school=new THREE.InstancedMesh(fishGeo,fishMat,count);
    school.userData={
      center:new THREE.Vector3(
        (Math.random()-0.5)*12,
        -1-Math.random()*3,
        (Math.random()-0.5)*12
      ),
      phase:Math.random()*Math.PI*2,
      speed:0.5+Math.random()*0.5,
      radius:2+Math.random()*3,
      count:count
    };
    school.renderOrder=20;
    scene.add(school);
    fishSchools.push(school);
  }

  // Aquatic plants
  const plantGeo=new THREE.ConeGeometry(0.15,1.5,5);
  const plantMat=new THREE.MeshStandardMaterial({color:0x2a7a4a,roughness:0.8,transparent:true,opacity:0.8});
  for(let i=0;i<20;i++){
    const a=Math.random()*Math.PI*2;
    const r=6+Math.random()*3;
    const plant=new THREE.Mesh(plantGeo,plantMat.clone());
    plant.position.set(Math.cos(a)*r,-DIORAMA_H/2+0.75,Math.sin(a)*r);
    plant.scale.y=0.5+Math.random()*1;
    plant.userData={phase:Math.random()*Math.PI*2};
    scene.add(plant);
    waterPlants.push(plant);
  }

  // Underwater rocks
  const uwRockGeo=new THREE.DodecahedronGeometry(0.5,0);
  const uwRockMat=new THREE.MeshStandardMaterial({color:0x4a5a5a,roughness:0.9});
  const uwRockMesh=new THREE.InstancedMesh(uwRockGeo,uwRockMat,15);
  const dummy=new THREE.Object3D();
  for(let i=0;i<15;i++){
    const a=Math.random()*Math.PI*2;
    const r=7+Math.random()*3;
    dummy.position.set(Math.cos(a)*r,-DIORAMA_H/2+0.3,Math.sin(a)*r);
    dummy.scale.setScalar(0.5+Math.random()*1.5);
    dummy.rotation.set(Math.random(),Math.random(),Math.random());
    dummy.updateMatrix();
    uwRockMesh.setMatrixAt(i,dummy.matrix);
  }
  uwRockMesh.renderOrder=4;
  scene.add(uwRockMesh);
}

function createRayGeometry(){
  const shape=new THREE.Shape();
  shape.moveTo(0,0.8);
  shape.quadraticCurveTo(0.6,0.4,0.9,0);
  shape.quadraticCurveTo(0.6,-0.2,0,-0.1);
  shape.quadraticCurveTo(-0.6,-0.2,-0.9,0);
  shape.quadraticCurveTo(-0.6,0.4,0,0.8);

  const geo=new THREE.ShapeGeometry(shape,8);
  geo.rotateX(-Math.PI/2);

  // Add tail
  const tailGeo=new THREE.CylinderGeometry(0.03,0.01,1.5,4);
  tailGeo.translate(0,0,-1.2);
  tailGeo.rotateX(Math.PI/2);

  const merged=THREE.BufferGeometryUtils?
    THREE.BufferGeometryUtils.mergeGeometries([geo,tailGeo]):geo;
  return geo; // Use shape only for simplicity
}

function createFishGeometry(){
  const body=new THREE.ConeGeometry(0.06,0.25,5);
  body.rotateZ(Math.PI/2);
  return body;
}

/* ============================================================
   BUBBLES
   ============================================================ */
function createBubbles(){
  const bubbleGeo=new THREE.SphereGeometry(0.06,6,6);
  const bubbleMat=new THREE.MeshStandardMaterial({
    color:0xffffff,transparent:true,opacity:0.3,
    roughness:0.1,metalness:0.1
  });
  for(let i=0;i<30;i++){
    const b=new THREE.Mesh(bubbleGeo,bubbleMat.clone());
    b.position.set(
      (Math.random()-0.5)*16,
      -DIORAMA_H/2+Math.random()*5,
      (Math.random()-0.5)*16
    );
    b.userData={
      speed:0.2+Math.random()*0.4,
      wobble:Math.random()*Math.PI*2,
      startY:b.position.y
    };
    b.renderOrder=30;
    scene.add(b);
    bubbles.push(b);
  }
}

/* ============================================================
   DECORATIONS
   ============================================================ */
function createDecorations(){
  const woodMat=new THREE.MeshStandardMaterial({color:0x7a5a3a,roughness:0.9});

  // Bench
  const benchSeat=new THREE.Mesh(new THREE.BoxGeometry(1.2,0.08,0.4),woodMat);
  benchSeat.position.set(-2,2.7,2.5);
  benchSeat.castShadow=true;
  scene.add(benchSeat);
  const benchLegGeo=new THREE.BoxGeometry(0.08,0.5,0.08);
  [[-0.5,2.45,2.3],[0.5,2.45,2.3],[-0.5,2.45,2.7],[0.5,2.45,2.7]].forEach(p=>{
    const leg=new THREE.Mesh(benchLegGeo,woodMat);
    leg.position.set(p[0],p[1],p[2]);
    scene.add(leg);
  });

  // Crates
  const crateGeo=new THREE.BoxGeometry(0.5,0.5,0.5);
  const crateMat=new THREE.MeshStandardMaterial({color:0x9a7a4a,roughness:0.9});
  [[3,2.75,2],[3.5,2.75,2.3],[3.2,3.25,2.1]].forEach(p=>{
    const crate=new THREE.Mesh(crateGeo,crateMat);
    crate.position.set(p[0],p[1],p[2]);
    crate.rotation.y=Math.random()*0.3;
    crate.castShadow=true;
    scene.add(crate);
  });

  // Towels on deck
  const towelGeo=new THREE.PlaneGeometry(0.4,0.8);
  const towelColors=[0xff6666,0x6666ff,0xffcc44];
  towelColors.forEach((c,i)=>{
    const towel=new THREE.Mesh(towelGeo,new THREE.MeshStandardMaterial({color:c,roughness:0.95,side:THREE.DoubleSide}));
    towel.position.set(2+i*0.5,2.4,3.5);
    towel.rotation.x=-Math.PI/2+0.1;
    towel.rotation.z=0.1*i;
    scene.add(towel);
  });

  // Potted plants near cabin
  const potGeo=new THREE.CylinderGeometry(0.15,0.12,0.25,8);
  const potMat=new THREE.MeshStandardMaterial({color:0xb85a3a,roughness:0.9});
  const potPlantGeo=new THREE.SphereGeometry(0.2,6,6);
  const potPlantMat=new THREE.MeshStandardMaterial({color:0x3a8a2a,roughness:0.8});
  [[-1.8,2.6,1.5],[1.8,2.6,1.5],[-1.8,2.6,-1.5],[1.8,2.6,-1.5]].forEach(p=>{
    const pot=new THREE.Mesh(potGeo,potMat);
    pot.position.set(p[0],p[1],p[2]);
    scene.add(pot);
    const pp=new THREE.Mesh(potPlantGeo,potPlantMat);
    pp.position.set(p[0],p[1]+0.3,p[2]);
    pp.castShadow=true;
    scene.add(pp);
  });
}

/* ============================================================
   KAYAK
   ============================================================ */
function createKayak(){
  kayak=new THREE.Group();

  // Hull
  const hullShape=new THREE.Shape();
  hullShape.moveTo(0,0.8);
  hullShape.quadraticCurveTo(0.25,0.3,0.2,0);
  hullShape.quadraticCurveTo(0.15,-0.5,0,-0.8);
  hullShape.quadraticCurveTo(-0.15,-0.5,-0.2,0);
  hullShape.quadraticCurveTo(-0.25,0.3,0,0.8);

  const hullGeo=new THREE.ExtrudeGeometry(hullShape,{depth:0.15,bevelEnabled:true,bevelThickness:0.05,bevelSize:0.05,bevelSegments:3});
  const hullMat=new THREE.MeshStandardMaterial({color:0xcc4422,roughness:0.6});
  const hull=new THREE.Mesh(hullGeo,hullMat);
  hull.rotation.x=-Math.PI/2;
  hull.position.y=0.05;
  hull.castShadow=true;
  kayak.add(hull);

  // Seat
  const seatGeo=new THREE.BoxGeometry(0.2,0.05,0.3);
  const seatMat=new THREE.MeshStandardMaterial({color:0x4a4a4a,roughness:0.8});
  const seat=new THREE.Mesh(seatGeo,seatMat);
  seat.position.set(0,0.15,0);
  kayak.add(seat);

  // Paddle
  const paddleGeo=new THREE.CylinderGeometry(0.02,0.02,1.2,4);
  const paddleMat=new THREE.MeshStandardMaterial({color:0x8a6a3a,roughness:0.8});
  const paddle=new THREE.Mesh(paddleGeo,paddleMat);
  paddle.rotation.z=Math.PI/2;
  paddle.position.set(0,0.2,0);
  kayak.add(paddle);

  kayak.position.set(4,2.3,10);
  kayak.userData={moored:true};
  scene.add(kayak);
}

/* ============================================================
   CAMERA SYSTEM
   ============================================================ */
const camPresets={
  iso:{pos:new THREE.Vector3(18,14,18),target:new THREE.Vector3(0,1,0)},
  cabin:{pos:new THREE.Vector3(6,4,8),target:new THREE.Vector3(1,2.5,2)},
  under:{pos:new THREE.Vector3(8,-3,8),target:new THREE.Vector3(0,-3,0)},
  free:null
};
let camTransition=null;

function setCamera(name){
  if(name==='free'){
    controls.enabled=true;
    camTransition=null;
    return;
  }
  const preset=camPresets[name];
  if(!preset)return;
  controls.enabled=false;
  camTransition={
    startPos:camera.position.clone(),
    endPos:preset.pos.clone(),
    startTarget:controls.target.clone(),
    endTarget:preset.target.clone(),
    t:0,duration:1.5
  };
}

function updateCamera(dt){
  if(camTransition){
    camTransition.t+=dt/camTransition.duration;
    if(camTransition.t>=1){
      camTransition.t=1;
      camera.position.copy(camTransition.endPos);
      controls.target.copy(camTransition.endTarget);
      camTransition=null;
      controls.enabled=true;
    }else{
      const t=easeInOut(camTransition.t);
      camera.position.lerpVectors(camTransition.startPos,camTransition.endPos,t);
      controls.target.lerpVectors(camTransition.startTarget,camTransition.endTarget,t);
    }
  }
  controls.update();
}

function easeInOut(t){return t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2}

/* ============================================================
   RAY LEAP
   ============================================================ */
function triggerRayLeap(){
  if(rayLeaping)return;
  rayLeaping=true;
  rayLeapT=0;
}

function updateRayLeap(dt){
  if(!rayLeaping)return;
  rayLeapT+=dt*0.6;
  const ray=rayMesh;
  if(rayLeapT<1){
    // Arc out of water
    const t=rayLeapT;
    const x=ray.userData.basePos.x;
    const z=ray.userData.basePos.z;
    const y=WATER_BASE+Math.sin(t*Math.PI)*4;
    ray.position.set(x,y,z);
    ray.rotation.x=Math.sin(t*Math.PI)*0.8;
  }else if(rayLeapT<1.5){
    // Splash down
    const t=(rayLeapT-1)/0.5;
    const x=ray.userData.basePos.x;
    const z=ray.userData.basePos.z;
    const y=WATER_BASE*(1-t)+ray.userData.basePos.y*t;
    ray.position.set(x,y,z);
    ray.rotation.x=0.8*(1-t);

    // Create droplets at splash
    if(t<0.1){
      for(let i=0;i<12;i++){
        createDroplet(ray.position.clone());
      }
      createRipple(ray.position.clone());
    }
  }else{
    rayLeaping=false;
    ray.position.copy(ray.userData.basePos);
    ray.rotation.x=0;
  }
}

function createDroplet(pos){
  const geo=new THREE.SphereGeometry(0.04,4,4);
  const mat=new THREE.MeshStandardMaterial({color:0x88ddff,transparent:true,opacity:0.8});
  const d=new THREE.Mesh(geo,mat);
  d.position.copy(pos);
  d.position.y+=0.5;
  d.userData={
    vel:new THREE.Vector3((Math.random()-0.5)*3,3+Math.random()*3,(Math.random()-0.5)*3),
    life:1
  };
  d.renderOrder=60;
  scene.add(d);
  droplets.push(d);
}

function createRipple(pos){
  const geo=new THREE.RingGeometry(0.1,0.2,24);
  const mat=new THREE.MeshStandardMaterial({
    color:0xffffff,transparent:true,opacity:0.6,side:THREE.DoubleSide,depthWrite:false
  });
  const r=new THREE.Mesh(geo,mat);
  r.rotation.x=-Math.PI/2;
  r.position.copy(pos);
  r.position.y=WATER_BASE+0.03;
  r.userData={life:1,speed:3};
  r.renderOrder=56;
  scene.add(r);
  ripples.push(r);
}

function updateParticles(dt){
  // Droplets
  for(let i=droplets.length-1;i>=0;i--){
    const d=droplets[i];
    d.userData.vel.y-=9.8*dt;
    d.position.add(d.userData.vel.clone().multiplyScalar(dt));
    d.userData.life-=dt*1.5;
    d.material.opacity=d.userData.life*0.8;
    if(d.userData.life<=0){
      scene.remove(d);
      d.geometry.dispose();
      d.material.dispose();
      droplets.splice(i,1);
    }
  }
  // Ripples
  for(let i=ripples.length-1;i>=0;i--){
    const r=ripples[i];
    r.userData.life-=dt*0.8;
    const s=1+(1-r.userData.life)*r.userData.speed;
    r.scale.set(s,s,1);
    r.material.opacity=r.userData.life*0.6;
    if(r.userData.life<=0){
      scene.remove(r);
      r.geometry.dispose();
      r.material.dispose();
      ripples.splice(i,1);
    }
  }
}

/* ============================================================
   KAYAK ANIMATION
   ============================================================ */
function toggleKayak(){
  kayakLaunched=!kayakLaunched;
  const btn=document.getElementById('btn-kayak');
  btn.classList.toggle('active',kayakLaunched);
}

function updateKayak(dt){
  if(kayakLaunched){
    kayakAngle+=dt*0.3;
    const r=8;
    kayak.position.set(Math.cos(kayakAngle)*r,WATER_BASE+0.1,Math.sin(kayakAngle)*r);
    kayak.rotation.y=-kayakAngle+Math.PI/2;
    // Bob
    kayak.position.y+=Math.sin(kayakAngle*3)*0.05;
  }else{
    // Return to pier
    const target=new THREE.Vector3(4,WATER_BASE+0.1,10);
    kayak.position.lerp(target,dt*2);
    kayak.rotation.y+=(0-kayak.rotation.y)*dt*2;
  }
}

/* ============================================================
   TIME OF DAY
   ============================================================ */
function setTimeOfDay(t){
  targetTimeOfDay=t;
  document.querySelectorAll('[data-time]').forEach(b=>{
    b.classList.toggle('active',b.dataset.time===['day','sunset','night'][t]);
  });
}

function updateTimeOfDay(dt){
  timeOfDay+=(targetTimeOfDay-timeOfDay)*dt*1.5;

  const day={sky:0x87ceeb,sun:0xfff0d0,sunI:1.5,amb:0.6,fog:0x87ceeb,exp:1.1};
  const sunset={sky:0xff7744,sun:0xff8844,sunI:1.2,amb:0.3,fog:0xff6633,exp:0.9};
  const night={sky:0x0a0a2a,sun:0x4466aa,sunI:0.2,amb:0.15,fog:0x0a0a2a,exp:0.6};

  const presets=[day,sunset,night];
  const idx=Math.min(Math.floor(timeOfDay),1);
  const frac=timeOfDay-idx;
  const a=presets[idx],b=presets[Math.min(idx+1,2)];

  const lerpC=(ca,cb,f)=>new THREE.Color(ca).lerp(new THREE.Color(cb),f);

  scene.background=lerpC(a.sky,b.sky,frac);
  scene.fog.color.copy(lerpC(a.fog,b.fog,frac));
  sunLight.color.copy(lerpC(a.sun,b.sun,frac));
  sunLight.intensity=a.sunI+(b.sunI-a.sunI)*frac;
  ambientLight.intensity=a.amb+(b.amb-a.amb)*frac;
  renderer.toneMappingExposure=a.exp+(b.exp-a.exp)*frac;

  // Sun position
  const sunAngle=timeOfDay*Math.PI*0.4+0.3;
  sunLight.position.set(Math.cos(sunAngle)*15,Math.sin(sunAngle)*20,8);

  // Night lights
  const nightFactor=Math.max(0,(timeOfDay-0.5)/1.5);
  pointLights.forEach(l=>{l.intensity=nightFactor*2});
  cabinWindows.forEach(w=>{
    w.material.emissiveIntensity=nightFactor*2;
  });
  lanterns.forEach(l=>{
    l.material.emissiveIntensity=nightFactor*3;
  });
}

/* ============================================================
   ANIMATION LOOP
   ============================================================ */
function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05);
  if(!paused){
    frameCount++;
    updateWorld(dt);
  }
  updateCamera(dt);
  updateParticles(dt);
  renderer.render(scene,camera);
}

function updateWorld(dt){
  const t=clock.elapsedTime;

  // Water
  waterSurface.material.uniforms.uTime.value=t;
  waterSurface.material.uniforms.uWind.value=windStrength;
  waterSurface.position.y=WATER_BASE+tideLevel;
  waterVolume.position.y=-DIORAMA_H/4+tideLevel*0.5;
  waterVolume.scale.y=1+tideLevel*0.05;
  causticMat.uniforms.uTime.value=t;

  // Rays
  rays.forEach((ray,i)=>{
    if(ray.userData.isLeaper&&rayLeaping)return;
    const d=ray.userData;
    const angle=t*d.speed+d.phase;
    ray.position.x=d.basePos.x+Math.cos(angle)*d.radius;
    ray.position.z=d.basePos.z+Math.sin(angle)*d.radius;
    ray.position.y=d.basePos.y+Math.sin(t*0.5+d.phase)*0.5;
    ray.rotation.y=-angle+Math.PI/2;
    // Fin undulation via scale
    ray.scale.x=1+Math.sin(t*3+d.phase)*0.1;
    ray.scale.z=1+Math.cos(t*2+d.phase)*0.05;
  });

  // Fish schools
  fishSchools.forEach(school=>{
    const d=school.userData;
    const dummy=new THREE.Object3D();
    for(let i=0;i<d.count;i++){
      const angle=t*d.speed+d.phase+i*0.4;
      const r=d.radius*(0.5+0.5*Math.sin(i*1.7));
      dummy.position.set(
        d.center.x+Math.cos(angle)*r,
        d.center.y+Math.sin(t*2+i)*0.3,
        d.center.z+Math.sin(angle)*r
      );
      dummy.rotation.y=-angle+Math.PI/2;
      dummy.scale.setScalar(0.8+Math.sin(i*2.3)*0.3);
      dummy.updateMatrix();
      school.setMatrixAt(i,dummy.matrix);
    }
    school.instanceMatrix.needsUpdate=true;
  });

  // Water plants sway
  waterPlants.forEach(p=>{
    p.rotation.z=Math.sin(t*1.5+p.userData.phase)*0.15*windStrength;
    p.rotation.x=Math.cos(t*1.2+p.userData.phase)*0.1*windStrength;
  });

  // Bubbles
  bubbles.forEach(b=>{
    b.position.y+=b.userData.speed*dt;
    b.position.x+=Math.sin(t*2+b.userData.wobble)*0.002;
    b.position.z+=Math.cos(t*1.5+b.userData.wobble)*0.002;
    if(b.position.y>WATER_BASE+tideLevel){
      b.position.y=-DIORAMA_H/2+0.5;
      b.position.x=(Math.random()-0.5)*16;
      b.position.z=(Math.random()-0.5)*16;
    }
  });

  // Trees sway
  trees.forEach((tree,i)=>{
    tree.rotation.z=Math.sin(t*1.5+i*0.7)*0.05*windStrength;
    tree.rotation.x=Math.cos(t*1.2+i*0.5)*0.03*windStrength;
  });

  // Kayak
  updateKayak(dt);

  // Ray leap
  updateRayLeap(dt);

  // Time of day
  updateTimeOfDay(dt);

  // Tide
  tideLevel+=(targetTide-tideLevel)*dt*2;
}

/* ============================================================
   AUDIO SYSTEM
   ============================================================ */
function setupAudio(){
  // Will be initialized on first click
}

function initAudio(){
  if(audioStarted)return;
  audioStarted=true;
  audioCtx=new(window.AudioContext||window.webkitAudioContext)();
  masterGain=audioCtx.createGain();
  masterGain.gain.value=0.5;
  masterGain.connect(audioCtx.destination);

  musicGain=audioCtx.createGain();
  musicGain.gain.value=0;
  musicGain.connect(masterGain);

  sfxGain=audioCtx.createGain();
  sfxGain.gain.value=0.3;
  sfxGain.connect(masterGain);

  // Ambient pad
  startAmbientPad();
  startWindSound();
  startWaterSound();
}

function startAmbientPad(){
  const notes=[261.63,329.63,392.0,523.25,659.25]; // C major pentatonic
  const baseFreqs=[130.81,164.81,196.0];

  baseFreqs.forEach(f=>{
    const osc=audioCtx.createOscillator();
    osc.type='sine';
    osc.frequency.value=f;
    const gain=audioCtx.createGain();
    gain.gain.value=0.04;
    osc.connect(gain);
    gain.connect(musicGain);
    osc.start();
    musicNodes.push({osc,gain});
  });

  // Melodic notes
  function playNote(){
    if(!musicOn)return;
    const freq=notes[Math.floor(Math.random()*notes.length)];
    const osc=audioCtx.createOscillator();
    osc.type='triangle';
    osc.frequency.value=freq;
    const gain=audioCtx.createGain();
    gain.gain.setValueAtTime(0.06,audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+3);
    osc.connect(gain);
    gain.connect(musicGain);
    osc.start();
    osc.stop(audioCtx.currentTime+3);
    setTimeout(playNote,2000+Math.random()*4000);
  }
  setTimeout(playNote,1000);
}

function startWindSound(){
  const bufferSize=2*audioCtx.sampleRate;
  const buffer=audioCtx.createBuffer(1,bufferSize,audioCtx.sampleRate);
  const data=buffer.getChannelData(0);
  for(let i=0;i<bufferSize;i++)data[i]=(Math.random()*2-1)*0.3;

  const source=audioCtx.createBufferSource();
  source.buffer=buffer;
  source.loop=true;

  const filter=audioCtx.createBiquadFilter();
  filter.type='lowpass';
  filter.frequency.value=400;
  filter.Q.value=1;

  const lfo=audioCtx.createOscillator();
  lfo.frequency.value=0.1;
  const lfoGain=audioCtx.createGain();
  lfoGain.gain.value=200;
  lfo.connect(lfoGain);
  lfoGain.connect(filter.frequency);
  lfo.start();

  const gain=audioCtx.createGain();
  gain.gain.value=0.08;

  source.connect(filter);
  filter.connect(gain);
  gain.connect(musicGain);
  source.start();
  musicNodes.push({source,gain,lfo});
}

function startWaterSound(){
  const bufferSize=2*audioCtx.sampleRate;
  const buffer=audioCtx.createBuffer(1,bufferSize,audioCtx.sampleRate);
  const data=buffer.getChannelData(0);
  for(let i=0;i<bufferSize;i++)data[i]=(Math.random()*2-1)*0.2;

  const source=audioCtx.createBufferSource();
  source.buffer=buffer;
  source.loop=true;

  const filter=audioCtx.createBiquadFilter();
  filter.type='bandpass';
  filter.frequency.value=800;
  filter.Q.value=0.5;

  const gain=audioCtx.createGain();
  gain.gain.value=0.05;

  source.connect(filter);
  filter.connect(gain);
  gain.connect(sfxGain);
  source.start();
  musicNodes.push({source,gain});
}

function toggleMusic(){
  if(!audioStarted)initAudio();
  musicOn=!musicOn;
  musicGain.gain.linearRampToValueAtTime(musicOn?0.5:0,audioCtx.currentTime+0.5);
  document.getElementById('btn-music').classList.toggle('active',musicOn);
}

function setVolume(v){
  if(masterGain)masterGain.gain.value=v;
}

/* ============================================================
   UI SETUP
   ============================================================ */
function setupUI(){
  // Camera buttons
  document.querySelectorAll('[data-cam]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      document.querySelectorAll('[data-cam]').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      setCamera(btn.dataset.cam);
    });
  });

  // Time buttons
  document.querySelectorAll('[data-time]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const times={day:0,sunset:1,night:2};
      setTimeOfDay(times[btn.dataset.time]);
    });
  });

  // Kayak
  document.getElementById('btn-kayak').addEventListener('click',()=>{
    if(!audioStarted)initAudio();
    toggleKayak();
  });

  // Ray leap
  document.getElementById('btn-ray').addEventListener('click',()=>{
    if(!audioStarted)initAudio();
    triggerRayLeap();
  });

  // Tide
  document.getElementById('sl-tide').addEventListener('input',e=>{
    targetTide=parseFloat(e.target.value)*2;
  });

  // Wind
  document.getElementById('sl-wind').addEventListener('input',e=>{
    targetWind=parseFloat(e.target.value);
    windStrength=targetWind;
  });

  // Music
  document.getElementById('btn-music').addEventListener('click',toggleMusic);

  // Volume
  document.getElementById('sl-vol').addEventListener('input',e=>{
    setVolume(parseFloat(e.target.value));
  });

  // Pause
  document.getElementById('btn-pause').addEventListener('click',()=>{
    paused=!paused;
    document.getElementById('btn-pause').classList.toggle('active',paused);
    document.getElementById('btn-pause').textContent=paused?'▶ Play':'⏸ Pause';
  });

  // Reset
  document.getElementById('btn-reset').addEventListener('click',()=>{
    targetTimeOfDay=0;
    targetTide=0;
    targetWind=0.3;
    windStrength=0.3;
    kayakLaunched=false;
    kayakAngle=0;
    paused=false;
    document.getElementById('btn-pause').classList.remove('active');
    document.getElementById('btn-pause').textContent='⏸ Pause';
    document.getElementById('btn-kayak').classList.remove('active');
    document.getElementById('sl-tide').value=0;
    document.getElementById('sl-wind').value=0.3;
    setTimeOfDay(0);
    setCamera('iso');
    document.querySelectorAll('[data-cam]').forEach(b=>b.classList.remove('active'));
    document.querySelector('[data-cam="iso"]').classList.add('active');
  });

  // Mobile toggle
  document.getElementById('mobile-toggle').addEventListener('click',()=>{
    document.getElementById('controls').classList.toggle('open');
  });
}

/* ============================================================
   RESIZE
   ============================================================ */
function onResize(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
}

/* ============================================================
   START
   ============================================================ */
scene.background=new THREE.Color(0x87ceeb);
init();
</script>
</body>
</html>
```

This is a complete, self-contained `index.html` file that creates **Tidehaven** — an interactive 3D coastal island diorama. Here's what's included:

**Scene Elements:**
- Procedural island with grass, sandy shore, rocks, and trees
- A-frame cabin with copper roof, glowing windows, and wooden deck
- Pier with ladder, lanterns, and moored kayak
- Benches, crates, towels, and potted plants

**Cutaway Water (Main Feature):**
- Glass walls on front and right sides for aquarium cross-section view
- Animated wave shader on the water surface
- Caustic light patterns on the seabed
- Shore foam ring
- Rising bubbles

**Underwater Life:**
- 3 rays with undulating fins swimming in circular paths
- 5 fish schools using `InstancedMesh` (75 fish total)
- Swaying aquatic plants and underwater rocks

**Interactions:**
- 🛶 **Kayak** — launches on a circular trip, press again to return
- 🐟 **Ray Leap** — ray arcs out of water with droplet particles and expanding ripple rings
- **Tide slider** — smoothly raises/lowers water level
- **Wind slider** — affects waves, tree sway, and plant movement
- **Time of Day** — Day/Sunset/Night with smooth lighting transitions; lanterns and windows glow at night
- **Pause/Reset**

**Cameras:**
- Isometric, Cabin, Underwater presets with smooth lerp transitions
- Free orbit via OrbitControls

**Audio:**
- Procedural ambient pad (sine oscillators, pentatonic melody)
- Filtered noise for wind and water
- Starts on first click, with music toggle and volume slider

**Technical:**
- Delta-time animations, capped pixel ratio, responsive mobile layout with collapsible panels
- `InstancedMesh` for fish, rocks, grass
- Custom GLSL shaders for water waves and seabed caustics
- Proper `renderOrder` and `depthWrite` management for transparency