# Tidehaven 🏝️

A complete single-file interactive 3D diorama. Save as `index.html` and open in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Tidehaven — a cozy island diorama</title>
<style>
  :root{
    --panel:rgba(18,26,34,.62); --panel-brd:rgba(255,255,255,.14);
    --ink:#eaf3f4; --ink-dim:#9fb6bb; --accent:#59c9b8; --accent2:#f2b48a;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;overflow:hidden;background:#0c1420;
    font-family:"Segoe UI",system-ui,-apple-system,Helvetica,Arial,sans-serif;color:var(--ink)}
  canvas{display:block}
  #hdr{position:fixed;top:18px;left:20px;z-index:10;pointer-events:none;
    text-shadow:0 2px 14px rgba(0,0,0,.55)}
  #hdr h1{font-size:30px;font-weight:600;letter-spacing:5px;color:#f4efe6}
  #hdr p{font-size:12px;letter-spacing:1.4px;color:var(--ink-dim);margin-top:2px}
  #panels{position:fixed;top:16px;right:16px;z-index:10;width:236px;display:flex;
    flex-direction:column;gap:10px;max-height:calc(100vh - 32px);overflow-y:auto;
    scrollbar-width:none}
  #panels::-webkit-scrollbar{display:none}
  .panel{background:var(--panel);border:1px solid var(--panel-brd);border-radius:14px;
    padding:12px 14px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    box-shadow:0 8px 28px rgba(0,0,0,.35)}
  .panel h2{font-size:10px;font-weight:700;letter-spacing:2.4px;text-transform:uppercase;
    color:var(--accent);margin-bottom:9px}
  .panel label{display:block;font-size:11px;color:var(--ink-dim);margin:8px 0 3px;
    letter-spacing:.6px}
  .panel label span{color:var(--ink)}
  .row{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
  .btn{flex:1;min-width:60px;background:rgba(255,255,255,.07);border:1px solid var(--panel-brd);
    color:var(--ink);border-radius:9px;padding:7px 6px;font-size:11px;letter-spacing:.4px;
    cursor:pointer;transition:all .18s;font-family:inherit}
  .btn:hover{background:rgba(255,255,255,.16)}
  .btn.active{background:var(--accent);border-color:var(--accent);color:#06231e;font-weight:600}
  input[type=range]{width:100%;height:22px;-webkit-appearance:none;background:transparent;cursor:pointer}
  input[type=range]::-webkit-slider-runnable-track{height:4px;border-radius:2px;
    background:linear-gradient(90deg,var(--accent),rgba(255,255,255,.16))}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;
    border-radius:50%;background:#fff;margin-top:-5px;box-shadow:0 1px 5px rgba(0,0,0,.5)}
  input[type=range]::-moz-range-track{height:4px;border-radius:2px;background:rgba(255,255,255,.25)}
  input[type=range]::-moz-range-thumb{width:14px;height:14px;border:none;border-radius:50%;background:#fff}
  select{width:100%;background:rgba(255,255,255,.07);color:var(--ink);border:1px solid var(--panel-brd);
    border-radius:8px;padding:5px 8px;font-family:inherit;font-size:11px;margin-top:3px}
  select option{background:#16222e}
  #hint{position:fixed;bottom:14px;left:20px;font-size:11px;letter-spacing:1px;color:var(--ink-dim);
    z-index:10;pointer-events:none;text-shadow:0 1px 8px rgba(0,0,0,.6)}
  #loading{position:fixed;inset:0;background:#0c1420;z-index:50;display:flex;align-items:center;
    justify-content:center;font-size:14px;letter-spacing:3px;color:var(--ink-dim);
    transition:opacity .7s}
  #loading.gone{opacity:0;pointer-events:none}
  #panelToggle{display:none;position:fixed;top:16px;right:16px;z-index:20;width:42px;height:42px;
    border-radius:12px;background:var(--panel);border:1px solid var(--panel-brd);color:var(--ink);
    font-size:18px;cursor:pointer;backdrop-filter:blur(12px)}
  @media (max-width:760px){
    #hdr h1{font-size:22px} #hdr p{display:none}
    #panelToggle{display:block}
    #panels{top:66px;transition:transform .3s,opacity .3s}
    #panels.hidden{transform:translateX(120%);opacity:0;pointer-events:none}
  }
</style>
</head>
<body>
<div id="hdr"><h1>TIDEHAVEN</h1><p>a cozy island diorama — warm lights above, living waters below</p></div>
<button id="panelToggle" aria-label="Toggle controls">☰</button>
<div id="panels">
  <section class="panel">
    <h2>Scene</h2>
    <div class="row">
      <button class="btn cam active" data-cam="iso">Isometric</button>
      <button class="btn cam" data-cam="cabin">Cabin</button>
      <button class="btn cam" data-cam="under">Underwater</button>
    </div>
    <div class="row">
      <button class="btn" id="actKayak">Launch kayak</button>
      <button class="btn" id="actRay">Ray leap</button>
    </div>
    <div class="row">
      <button class="btn" id="actPause">Pause</button>
      <button class="btn" id="actReset">Reset</button>
    </div>
  </section>
  <section class="panel">
    <h2>Environment</h2>
    <label>Tide — <span id="tideVal">0.0</span></label>
    <input id="tide" type="range" min="-0.9" max="0.5" step="0.01" value="0">
    <label>Wind — <span id="windVal">45%</span></label>
    <input id="wind" type="range" min="0" max="1" step="0.01" value="0.45">
    <label>Time of day</label>
    <div class="row">
      <button class="btn tod active" data-tod="day">Day</button>
      <button class="btn tod" data-tod="sunset">Sunset</button>
      <button class="btn tod" data-tod="night">Night</button>
    </div>
    <label>Quality</label>
    <select id="quality">
      <option value="high">High</option>
      <option value="med" selected>Medium</option>
      <option value="low">Low</option>
    </select>
  </section>
  <section class="panel">
    <h2>Audio</h2>
    <div class="row"><button class="btn" id="actMusic">♪ Music on</button></div>
    <label>Volume</label>
    <input id="vol" type="range" min="0" max="1" step="0.01" value="0.7">
  </section>
</div>
<div id="hint">drag to orbit · scroll / pinch to zoom</div>
<div id="loading">PREPARING TIDEHAVEN…</div>

<script type="importmap">
{"imports":{
  "three":"https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

/* ============================================================
   TIDEHAVEN — a procedural coastal island diorama
   Sections: 0 core · 1 island · 2 water · 3 cabin/pier · 4 nature
             5 sea life · 6 fx · 7 time-of-day · 8 cameras
             9 audio · 10 UI · 11 loop
   ============================================================ */

/* ---------- 0. CORE ---------- */
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.1, 200);
camera.position.set(13,10.5,13);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.06;
controls.minDistance = 4; controls.maxDistance = 42;
controls.maxPolarAngle = 1.72; controls.target.set(0,-0.6,0);

const world = new THREE.Group(); scene.add(world);   // everything lives here
const clock = new THREE.Clock();
const state = { paused:false, time:0, tide:0, wind:0.45, quality:'med' };
const waterTop = () => state.tide;                    // world y of water surface

// shared uniforms for wind/time driven shaders
const envU = { uTime:{value:0}, uWind:{value:0.45}, uDay:{value:1},
               uSunDir:{value:new THREE.Vector3(0.6,0.8,0.4)} };

// helper: standard material with wind sway injected into vertex shader
function swayMaterial(color, opts={}, amp=1){
  const m = new THREE.MeshStandardMaterial(Object.assign({color, roughness:0.85}, opts));
  m.onBeforeCompile = s => {
    s.uniforms.uTime = envU.uTime; s.uniforms.uWind = envU.uWind;
    s.vertexShader = 'uniform float uTime;uniform float uWind;\n' + s.vertexShader.replace(
      '#include <begin_vertex>', `#include <begin_vertex>
      { vec4 wp = modelMatrix * vec4(position,1.0);
        float k = max(position.y,0.0); k = k*k*${amp.toFixed(2)};
        transformed.x += sin(uTime*1.7 + wp.x*3.0 + wp.z*2.0)*uWind*0.07*k;
        transformed.z += cos(uTime*1.4 + wp.z*3.0)*uWind*0.06*k; }`);
  };
  return m;
}
const mat = (c,r=0.85,m=0)=> new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:m});

/* ---------- LIGHTS ---------- */
const hemi = new THREE.HemisphereLight(0xcfe8f5, 0x9a7b52, 0.85); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2dd, 2.4);
sun.position.set(8,12,6); sun.castShadow = true;
sun.shadow.mapSize.set(1024,1024);
sun.shadow.camera.left=-13; sun.shadow.camera.right=13;
sun.shadow.camera.top=13; sun.shadow.camera.bottom=-13;
sun.shadow.camera.near=1; sun.shadow.camera.far=45; sun.shadow.bias=-0.0006;
scene.add(sun, sun.target);
const cabinLight = new THREE.PointLight(0xffb066, 0, 7, 2); cabinLight.position.set(0,2.1,0.2); world.add(cabinLight);
const lanternLights = [];

/* ---------- 1. ISLAND ---------- */
// lathe profile (radius, y) from summit down to seabed
const PROFILE = [[1.4,1.35],[1.9,1.15],[2.5,0.85],[3.05,0.45],[3.28,0.15],
                 [3.22,0.0],[3.15,-0.3],[3.0,-1.0],[2.7,-2.0],[2.3,-3.2],[1.9,-4.4]];
function islandRadiusAtY(y){
  for(let i=0;i<PROFILE.length-1;i++){
    const [r1,y1]=PROFILE[i],[r2,y2]=PROFILE[i+1];
    if((y<=y1&&y>=y2)||(y>=y1&&y<=y2)){ const t=(y-y1)/(y2-y1||1); return r1+(r2-r1)*t; }
  }
  return y>1.35?1.4:1.9;
}
function islandHeightAtR(r){
  for(let i=0;i<PROFILE.length-1;i++){
    const [r1,y1]=PROFILE[i],[r2,y2]=PROFILE[i+1];
    if(r>=Math.min(r1,r2)&&r<=Math.max(r1,r2)){ const t=(r-r1)/((r2-r1)||1); return y1+(y2-y1)*t; }
  }
  return 1.35;
}
const grassC=new THREE.Color(0x6da24e), sandC=new THREE.Color(0xdcc28c), wetSandC=new THREE.Color(0xc4ab7d);
function paintIsland(geo){
  const pos=geo.attributes.position, col=new Float32Array(pos.count*3), c=new THREE.Color();
  for(let i=0;i<pos.count;i++){
    const y=pos.getY(i);
    if(y>0.5) c.copy(grassC).offsetHSL(0,(i%7-3)*0.01,(i%5-2)*0.015);
    else if(y>0.12) c.copy(grassC).lerp(sandC,(0.5-y)/0.38);
    else if(y>-0.6) c.copy(sandC);
    else c.copy(sandC).lerp(wetSandC,Math.min(1,(-0.6-y)/3));
    col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(col,3));
}
{
  const pts = PROFILE.map(p=>new THREE.Vector2(p[0],p[1]));
  const lathe = new THREE.LatheGeometry(pts, 56);
  // organic wobble (keep radius <= 3.28 so it never touches the water hole wall)
  const pos = lathe.attributes.position;
  for(let i=0;i<pos.count;i++){
    const x=pos.getX(i), y=pos.getY(i), z=pos.getZ(i);
    const th=Math.atan2(z,x), r=Math.hypot(x,z);
    if(r>0.01){
      const n=1+(Math.sin(th*5)*0.05+Math.sin(th*13+2)*0.03)*(y<0.35?1:0.5);
      let nr=Math.min(r*n,3.28);
      pos.setX(i,Math.cos(th)*nr); pos.setZ(i,Math.sin(th)*nr);
    }
  }
  lathe.computeVertexNormals(); paintIsland(lathe);
  const cap = new THREE.CircleGeometry(1.42,48); cap.rotateX(-Math.PI/2); cap.translate(0,1.35,0);
  paintIsland(cap);
  const island = new THREE.Mesh(mergeGeometries([lathe,cap]),
    new THREE.MeshStandardMaterial({vertexColors:true,roughness:0.95}));
  island.castShadow = island.receiveShadow = true; world.add(island);
}
// seabed with animated caustics
const causticU = { uTime:envU.uTime, uDay:envU.uDay };
{
  const g = new THREE.PlaneGeometry(17.3,17.3); g.rotateX(-Math.PI/2);
  const m = new THREE.ShaderMaterial({ uniforms:causticU,
    vertexShader:`varying vec2 vP; void main(){ vec4 w=modelMatrix*vec4(position,1.); vP=w.xz;
      gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`uniform float uTime,uDay; varying vec2 vP;
      void main(){
        vec2 p=vP;
        float c=sin(p.x*2.1+uTime)+sin(p.y*2.6-uTime*.9)+sin((p.x+p.y)*1.7+uTime*1.3)
              +sin(length(p+7.)*2.4-uTime*1.7);
        c=c*.25+.5; float k=pow(c,7.)*1.5;
        vec3 sand=vec3(.78,.70,.53)*(.85+.15*sin(p.x*.7)*sin(p.y*.55));
        vec3 col=sand*(.28+.55*uDay)+vec3(.55,.85,.8)*k*(.25+.6*uDay);
        gl_FragColor=vec4(col,1.); }`});
  const bed = new THREE.Mesh(g,m); bed.position.y=-4.4; world.add(bed);
}
// diorama base + glass walls + wooden rim
{
  const base = new THREE.Mesh(new THREE.BoxGeometry(17.7,1.4,17.7), mat(0x2c3947,0.95));
  base.position.y=-5.1; base.receiveShadow=true; world.add(base);
  const glass = new THREE.MeshPhysicalMaterial({color:0xcfeff2,transparent:true,opacity:0.07,
    roughness:0.05,metalness:0,side:THREE.DoubleSide,depthWrite:false});
  const pg = new THREE.PlaneGeometry(17.4,5.95);
  [[0,8.72,0],[0,-8.72,Math.PI],[8.72,0,-Math.PI/2],[-8.72,0,Math.PI/2]].forEach(([x,z,ry])=>{
    const p=new THREE.Mesh(pg,glass); p.position.set(x,-1.42,z); p.rotation.y=ry;
    p.renderOrder=10; world.add(p);
  });
  const rimM = mat(0x3a2c22,0.8);
  const rimA=new THREE.BoxGeometry(17.9,0.16,0.34), rimB=new THREE.BoxGeometry(0.34,0.16,17.9);
  [[0,8.72,rimA],[0,-8.72,rimA]].forEach(([x,z,g])=>{const m=new THREE.Mesh(g,rimM);m.position.set(x,1.56,z);m.castShadow=true;world.add(m);});
  [[8.72,0],[−8.72,0]].forEach(([x,z])=>{const m=new THREE.Mesh(rimB,rimM);m.position.set(x,1.56,z);m.castShadow=true;world.add(m);});
}

/* ---------- 2. WATER (cutaway lagoon) ---------- */
const waterGroup = new THREE.Group(); world.add(waterGroup);
const waveVert = `
  uniform float uTime,uWind; varying vec3 vN,vW;
  void main(){
    vec3 p=position; vec3 n=vec3(0.,1.,0.);
    float w=.35+.65*uWind;
    p.y += (sin(p.x*1.6+uTime*1.4)*.055+sin(p.z*2.1-uTime*1.1)*.045
           +sin((p.x+p.z)*1.15+uTime*.7)*.03)*w;
    float dx=(cos(p.x*1.6+uTime*1.4)*.088+cos((p.x+p.z)*1.15+uTime*.7)*.034)*w;
    float dz=(cos(p.z*2.1-uTime*1.1)*.095+cos((p.x+p.z)*1.15+uTime*.7)*.034)*w;
    vN=normalize(vec3(-dx,1.,-dz));
    vec4 wp=modelMatrix*vec4(p,1.); vW=wp.xyz;
    gl_Position=projectionMatrix*viewMatrix*wp; }`;
const waterFrag = `
  uniform vec3 uShallow,uDeep,uSunDir; uniform float uOpacity,uDay;
  varying vec3 vN,vW;
  void main(){
    vec3 N=normalize(vN); if(!gl_FrontFacing) N=-N;
    vec3 V=normalize(cameraPosition-vW);
    float fres=pow(1.-abs(dot(V,N)),2.5);
    vec3 base=mix(uDeep,uShallow,clamp((vW.y+4.)/4.,0.,1.));
    vec3 R=reflect(-normalize(uSunDir),N);
    float spec=pow(max(dot(R,V),0.),70.);
    vec3 col=base*(.35+.65*uDay)+fres*vec3(.45,.7,.7)*(.4+.6*uDay)+spec*1.1*uDay;
    gl_FragColor=vec4(col,uOpacity+fres*.22+spec*.45); }`;
const waterUni = { uShallow:{value:new THREE.Color(0x3fd0c9)}, uDeep:{value:new THREE.Color(0x0e6f86)},
  uTime:envU.uTime, uWind:envU.uWind, uOpacity:{value:0.36}, uDay:envU.uDay, uSunDir:envU.uSunDir };
{
  // volume (cross-section walls) — extruded rectangle with a hole for the island
  const shape=new THREE.Shape();
  shape.moveTo(-8.65,-8.65); shape.lineTo(8.65,-8.65); shape.lineTo(8.65,8.65); shape.lineTo(-8.65,8.65);
  const hole=new THREE.Path(); hole.absarc(0,0,3.32,0,Math.PI*2,true); shape.holes.push(hole);
  const vol=new THREE.ExtrudeGeometry(shape,{depth:5.98,bevelEnabled:false,curveSegments:64});
  vol.rotateX(-Math.PI/2); vol.translate(0,-6,0);
  const volMesh=new THREE.Mesh(vol,new THREE.ShaderMaterial({
    uniforms:waterUni, transparent:true, depthWrite:false, side:THREE.FrontSide,
    vertexShader:`varying vec3 vN,vW; void main(){ vN=normal; vec4 w=modelMatrix*vec4(position,1.);
      vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:waterFrag.replace('uOpacity','uOpacity') }));
  volMesh.renderOrder=2; waterGroup.add(volMesh);
  // animated surface (dense plane; hidden under the island by depth test)
  const surf=new THREE.PlaneGeometry(17.3,17.3,88,88); surf.rotateX(-Math.PI/2);
  const surfMesh=new THREE.Mesh(surf,new THREE.ShaderMaterial({
    uniforms:waterUni, vertexShader:waveVert, fragmentShader:waterFrag,
    transparent:true, depthWrite:false, side:THREE.DoubleSide }));
  surfMesh.position.y=0.001; surfMesh.renderOrder=2; waterGroup.add(surfMesh);
}
// shoreline foam ring (follows tide + island radius)
const foam = (()=>{
  const g=new THREE.RingGeometry(0.9,1.0,90); g.rotateX(-Math.PI/2);
  const m=new THREE.ShaderMaterial({
    uniforms:{uTime:envU.uTime,uWind:envU.uWind,uDay:envU.uDay},
    transparent:true, depthWrite:false, side:THREE.DoubleSide,
    vertexShader:`varying vec2 vUv; void main(){ vUv=uv;
      gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader:`uniform float uTime,uWind,uDay; varying vec2 vUv;
      void main(){
        float n=fract(sin(vUv.x*57.0)*43758.5453);
        float a=(.55+.45*sin(vUv.x*(60.+n*40.)+uTime*(2.+uWind*3.)))*(.45+.55*uWind);
        a*=smoothstep(0.,.25,vUv.y)*smoothstep(1.,.5,vUv.y);
        gl_FragColor=vec4(1.,1.,1.,a*.6*(.4+.6*uDay)); }`});
  const mesh=new THREE.Mesh(g,m); mesh.renderOrder=3; waterGroup.add(mesh); return mesh;
})();
// expanding ripples pool
const rippleGeo = new THREE.RingGeometry(0.86,1.0,48); rippleGeo.rotateX(-Math.PI/2);
const ripples = [];
function spawnRipple(x,z,n=3){
  for(let i=0;i<n;i++){
    const m=new THREE.Mesh(rippleGeo,new THREE.MeshBasicMaterial({color:0xeafcff,
      transparent:true,opacity:0.55,depthWrite:false,side:THREE.DoubleSide}));
    m.position.set(x,waterTop()+0.04,z); m.renderOrder=4;
    m.scale.setScalar(0.25); world.add(m); ripples.push({m,t:-i*0.14});
  }
}

/* ---------- 3. CABIN · DECK · PIER · PROPS ---------- */
const woodM=mat(0x8a6248,0.9), woodDark=mat(0x5f4433,0.9), copper=mat(0xc97b4a,0.35,0.65);
const glowMats=[]; // emissive materials that light up in the evening
function glowMat(c=0xffcf8a){ const m=new THREE.MeshBasicMaterial({color:c}); glowMats.push(m); return m; }
{
  // A-frame cabin (triangular prism)
  const sh=new THREE.Shape(); sh.moveTo(-0.85,0); sh.lineTo(0.85,0); sh.lineTo(0,1.55); sh.closePath();
  const body=new THREE.Mesh(new THREE.ExtrudeGeometry(sh,{depth:1.6,bevelEnabled:false}), woodM);
  body.position.set(0,1.37,-1.0); body.castShadow=body.receiveShadow=true; world.add(body);
  // copper roof panels + ridge
  const ang=Math.atan2(1.55,0.85), L=Math.hypot(1.55,0.85)+0.16;
  const roofG=new THREE.BoxGeometry(L,0.07,1.86);
  const rL=new THREE.Mesh(roofG,copper); rL.position.set(-0.42,1.37+0.775+0.05,0.2); rL.rotation.z=ang;
  const rR=new THREE.Mesh(roofG,copper); rR.position.set(0.42,1.37+0.775+0.05,0.2); rR.rotation.z=-ang;
  const ridge=new THREE.Mesh(new THREE.BoxGeometry(0.16,0.09,1.92),copper); ridge.position.set(0,2.95,0.2);
  [rL,rR,ridge].forEach(r=>{r.castShadow=true;world.add(r);});
  // glowing gable window + door
  const wsh=new THREE.Shape(); wsh.moveTo(-0.3,0.15); wsh.lineTo(0.3,0.15); wsh.lineTo(0,0.95); wsh.closePath();
  const win=new THREE.Mesh(new THREE.ShapeGeometry(wsh),glowMat());
  win.position.set(0,1.42,0.63); world.add(win);
  const door=new THREE.Mesh(new THREE.BoxGeometry(0.36,0.62,0.06),mat(0x4a3226,0.9));
  door.position.set(0,1.68,0.63); door.castShadow=true; world.add(door);
  const chimney=new THREE.Mesh(new THREE.BoxGeometry(0.18,0.55,0.18),mat(0x6f6f6f,0.9));
  chimney.position.set(0.5,2.55,-0.4); chimney.castShadow=true; world.add(chimney);
  // deck + steps + railing
  const deck=new THREE.Mesh(new THREE.BoxGeometry(2.6,0.12,1.8),woodM);
  deck.position.set(0,1.31,2.15); deck.castShadow=deck.receiveShadow=true; world.add(deck);
  for(let i=0;i<3;i++){ const st=new THREE.Mesh(new THREE.BoxGeometry(0.9,0.09,0.3),woodDark);
    st.position.set(0,1.18-i*0.22,3.15+i*0.28); st.castShadow=true; world.add(st); }
  const railG=new THREE.BoxGeometry(2.6,0.05,0.05), postG=new THREE.BoxGeometry(0.06,0.42,0.06);
  [[0,3.02,0],[1.27,2.15,Math.PI/2],[-1.27,2.15,Math.PI/2]].forEach(([x,z,ry])=>{
    const r=new THREE.Mesh(railG,woodDark); r.position.set(x,1.62,z); r.rotation.y=ry;
    if(x!==0){r.scale.x=1.8;} r.castShadow=true; world.add(r);
  });
  [[-1.27,3.02],[1.27,3.02],[-1.27,1.3],[1.27,1.3],[0,3.02]].forEach(([x,z])=>{
    const p=new THREE.Mesh(postG,woodDark); p.position.set(x,1.55,z); world.add(p);
  });
  // bench + towels
  const bench=new THREE.Group();
  const seat=new THREE.Mesh(new THREE.BoxGeometry(0.72,0.06,0.28),woodM); seat.position.y=0.24;
  const b1=new THREE.Mesh(new THREE.BoxGeometry(0.06,0.24,0.24),woodDark); b1.position.set(-0.3,0.12,0);
  const b2=b1.clone(); b2.position.x=0.3;
  bench.add(seat,b1,b2); bench.position.set(0.85,1.37,2.55); bench.rotation.y=-0.5;
  bench.children.forEach(c=>c.castShadow=true); world.add(bench);
  const towel1=new THREE.Mesh(new THREE.BoxGeometry(0.55,0.025,0.3),mat(0xf08a6b,0.95));
  towel1.position.set(0.85,1.68,2.55); towel1.rotation.set(-0.06,-0.5,0.1); world.add(towel1);
  const towel2=new THREE.Mesh(new THREE.BoxGeometry(0.3,0.55,0.02),mat(0x6fb7d8,0.95));
  towel2.position.set(-0.55,1.35,3.05); towel2.rotation.set(0,0.12,0.06); world.add(towel2);
  // crates
  [[-0.95,1.53,2.3,0.2],[-0.55,1.53,2.55,-0.3],[-0.95,1.85,2.3,0.1]].forEach(([x,y,z,ry])=>{
    const c=new THREE.Mesh(new THREE.BoxGeometry(0.34,0.32,0.34),woodDark);
    c.position.set(x,y,z); c.rotation.y=ry; c.castShadow=true; world.add(c);
  });
  // potted plants
  const potM=mat(0xb3623f,0.9), leafM=swayMaterial(0x4f8f43,{},14);
  [[1.05,1.43,2.75],[-1.15,1.43,1.7],[1.6,islandHeightAtR(1.9)-0.02,1.1],
   [-1.7,islandHeightAtR(2.0)-0.02,-0.6]].forEach(([x,y,z])=>{
    const pot=new THREE.Mesh(new THREE.CylinderGeometry(0.11,0.085,0.16,10),potM);
    pot.position.set(x,y+0.08,z); pot.castShadow=true;
    const leaves=new THREE.Mesh(new THREE.IcosahedronGeometry(0.16,1),leafM);
    leaves.position.set(x,y+0.3,z); leaves.castShadow=true; world.add(pot,leaves);
  });
}
{
  // pier: planks + posts (instanced), railing, ladder
  const plankG=new THREE.BoxGeometry(1.16,0.07,0.24);
  const planks=new THREE.InstancedMesh(plankG,woodM,15);
  const dummy=new THREE.Object3D();
  for(let i=0;i<15;i++){ dummy.position.set(0,0.78,3.15+i*0.245);
    dummy.rotation.y=(i%3-1)*0.008; dummy.updateMatrix(); planks.setMatrixAt(i,dummy.matrix); }
  planks.castShadow=planks.receiveShadow=true; world.add(planks);
  const postG=new THREE.CylinderGeometry(0.06,0.075,2.5,8);
  const posts=new THREE.InstancedMesh(postG,woodDark,8);
  let pi=0;
  for(const z of [3.3,4.4,5.5,6.4]) for(const x of [-0.5,0.5]){
    dummy.position.set(x,-0.4,z); dummy.rotation.set(0,0,0); dummy.scale.setScalar(1);
    dummy.updateMatrix(); posts.setMatrixAt(pi++,dummy.matrix);
  }
  posts.castShadow=true; world.add(posts);
  const rail=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.05,3.4),woodDark);
  rail.position.set(0.57,1.08,4.85); rail.castShadow=true; world.add(rail);
  // ladder into the water
  const lrail=new THREE.BoxGeometry(0.05,2.1,0.05);
  [-0.19,0.19].forEach(x=>{ const l=new THREE.Mesh(lrail,woodDark);
    l.position.set(x,-0.28,6.62); l.castShadow=true; world.add(l); });
  const rung=new THREE.CylinderGeometry(0.025,0.025,0.38,6); rung.rotateZ(Math.PI/2);
  [0.55,0.1,-0.35,-0.8].forEach(y=>{ const r=new THREE.Mesh(rung,woodDark);
    r.position.set(0,y,6.62); world.add(r); });
  // lanterns (post + glowing lamp + light)
  [[0.57,1.1,4.2],[0.57,1.1,6.35],[-1.15,1.6,2.9]].forEach(([x,y,z],i)=>{
    const pm=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.5,0.05),woodDark); pm.position.set(x,y+0.2,z);
    const lamp=new THREE.Mesh(new THREE.BoxGeometry(0.13,0.17,0.13),glowMat(0xffd9a0));
    lamp.position.set(x,y+0.52,z);
    const pl=new THREE.PointLight(0xffc27a,0,5,2); pl.position.set(x,y+0.52,z);
    world.add(pm,lamp,pl); lanternLights.push({light:pl,seed:i*2.1});
  });
}
// kayak (docked at the pier)
const kayak = new THREE.Group();
{
  const hull=new THREE.Mesh(new THREE.SphereGeometry(1,16,10),mat(0xe8813f,0.55));
  hull.scale.set(0.3,0.13,1.15); hull.castShadow=true;
  const deckTop=new THREE.Mesh(new THREE.SphereGeometry(1,14,8),mat(0xf2b48a,0.6));
  deckTop.scale.set(0.24,0.1,0.9); deckTop.position.y=0.06;
  const cockpit=new THREE.Mesh(new THREE.CircleGeometry(0.14,12),mat(0x33261d,0.9));
  cockpit.rotation.x=-Math.PI/2; cockpit.position.set(0,0.12,0.05);
  const paddle=new THREE.Mesh(new THREE.BoxGeometry(0.04,0.02,0.85),woodDark);
  paddle.position.set(0.2,0.16,0); paddle.rotation.y=0.5;
  kayak.add(hull,deckTop,cockpit,paddle);
  kayak.position.set(1.05,0.1,5.7); kayak.rotation.y=0.25;
  world.add(kayak);
}
const KAYAK_DOCK = kayak.position.clone();
let kayakState='dock', kayakAngle=0;

/* ---------- 4. TREES · GRASS · ROCKS (instanced where repeated) ---------- */
{
  const trunkM=swayMaterial(0x6e4b32,{},2.2);
  const pineM=swayMaterial(0x3f7a45,{},4.5), roundM=swayMaterial(0x5c9a4a,{},5);
  const trunkG=new THREE.CylinderGeometry(0.06,0.1,0.6,7);
  const coneG=new THREE.ConeGeometry(0.5,0.75,9);
  const blobG=new THREE.IcosahedronGeometry(0.42,1);
  const spots=[[1.1,0.7],[1.7,-0.5],[0.2,1.5],[-1.3,1.0],[-1.8,-0.7],[-0.4,-1.6],[1.0,-1.4]];
  spots.forEach(([x,z],i)=>{
    const r=Math.hypot(x,z), y=islandHeightAtR(r)-0.05;
    const g=new THREE.Group();
    const tr=new THREE.Mesh(trunkG,trunkM); tr.position.y=0.3; tr.castShadow=true; g.add(tr);
    if(i%2===0){
      for(let k=0;k<3;k++){ const c=new THREE.Mesh(coneG,pineM);
        c.position.y=0.7+k*0.42; c.scale.setScalar(1-k*0.22); c.castShadow=true; g.add(c); }
    } else {
      const b=new THREE.Mesh(blobG,roundM); b.position.y=0.85; b.scale.set(1,1.15,1); b.castShadow=true; g.add(b);
      const b2=new THREE.Mesh(blobG,roundM); b2.position.set(0.22,0.62,0.1); b2.scale.setScalar(0.6); b2.castShadow=true; g.add(b2);
    }
    g.position.set(x,y,z); g.scale.setScalar(0.85+(i%3)*0.18); world.add(g);
  });
  // grass tufts
  const tuft=new THREE.InstancedMesh(new THREE.ConeGeometry(0.05,0.26,5),swayMaterial(0x7fb35a,{},8),42);
  const d=new THREE.Object3D();
  for(let i=0;i<42;i++){
    const a=Math.random()*Math.PI*2, r=0.3+Math.random()*2.1;
    const x=Math.cos(a)*r, z=Math.sin(a)*r;
    d.position.set(x,islandHeightAtR(r)+0.1,z);
    d.rotation.set((Math.random()-0.5)*0.3,Math.random()*3,(Math.random()-0.5)*0.3);
    d.scale.setScalar(0.7+Math.random()*0.7); d.updateMatrix(); tuft.setMatrixAt(i,d.matrix);
  }
  tuft.castShadow=true; world.add(tuft);
  // rocks: shoreline ring + underwater boulders
  const rockM=mat(0x77747a,0.95);
  const rocks=new THREE.InstancedMesh(new THREE.DodecahedronGeometry(0.3,0),rockM,26);
  for(let i=0;i<26;i++){
    const shore=i<10;
    const a=Math.random()*Math.PI*2;
    const r=shore? 3.0+Math.random()*0.22 : 4.2+Math.random()*3.4;
    const y=shore? 0.05+Math.random()*0.15 : -4.25+Math.random()*0.2;
    d.position.set(Math.cos(a)*r,y,Math.sin(a)*r);
    d.rotation.set(Math.random()*3,Math.random()*3,Math.random()*3);
    d.scale.set(shore?0.35+Math.random()*0.4:0.8+Math.random()*1.4,
                shore?0.3+Math.random()*0.3:0.5+Math.random()*0.7,
                shore?0.35+Math.random()*0.4:0.8+Math.random()*1.2);
    d.updateMatrix(); rocks.setMatrixAt(i,d.matrix);
  }
  rocks.castShadow=rocks.receiveShadow=true; world.add(rocks);
  // stars (night)
  const starGeo=new THREE.BufferGeometry();
  const sp=new Float32Array(400*3);
  for(let i=0;i<400;i++){ const v=new THREE.Vector3().randomDirection().multiplyScalar(70);
    v.y=Math.abs(v.y); sp.set([v.x,v.y,v.z],i*3); }
  starGeo.setAttribute('position',new THREE.BufferAttribute(sp,3));
  const stars=new THREE.Points(starGeo,new THREE.PointsMaterial({color:0xdfe8ff,size:0.35,
    transparent:true,opacity:0,depthWrite:false}));
  scene.add(stars); window.__stars=stars;
}
// kelp (shader-bent planes)
const kelpUni={uTime:envU.uTime,uWind:envU.uWind,uDay:envU.uDay};
{
  const kelpM=new THREE.ShaderMaterial({uniforms:kelpUni,side:THREE.DoubleSide,
    vertexShader:`uniform float uTime,uWind; varying float vY;
      void main(){ vY=uv.y; vec3 p=position;
        vec4 wp=modelMatrix*vec4(position,1.);
        float k=uv.y*uv.y*(.4+.6*uWind);
        p.x+=sin(uTime*1.3+wp.x*2.+wp.z*1.7)*.28*k;
        p.z+=cos(uTime*1.1+wp.z*2.1)*.2*k;
        gl_Position=projectionMatrix*viewMatrix*modelMatrix*vec4(p,1.); }`,
    fragmentShader:`varying float vY; uniform float uDay;
      void main(){ vec3 c=mix(vec3(.05,.3,.2),vec3(.2,.65,.3),vY);
        gl_FragColor=vec4(c*(.4+.6*uDay),1.); }`});
  for(let i=0;i<12;i++){
    const h=0.9+Math.random()*1.6;
    const g=new THREE.PlaneGeometry(0.28,h,1,6); g.translate(0,h/2,0);
    const m=new THREE.Mesh(g,kelpM);
    const a=Math.random()*Math.PI*2, r=4.3+Math.random()*3.6;
    m.position.set(Math.cos(a)*r,-4.35,Math.sin(a)*r);
    m.rotation.y=Math.random()*Math.PI; m.renderOrder=1; world.add(m);
  }
}

/* ---------- 5. SEA LIFE ---------- */
// manta rays — merged geometry with per-vertex mask (0 body / 1 fin / 2 tail)
function rayGeometry(){
  const parts=[];
  const add=(g,mask)=>{ const n=g.attributes.position.count;
    const a=new Float32Array(n).fill(mask); g.setAttribute('aMask',new THREE.BufferAttribute(a,1));
    parts.push(g); };
  const body=new THREE.SphereGeometry(1,22,12); body.scale(0.55,0.13,1.15); add(body,0);
  const head=new THREE.SphereGeometry(0.34,12,8); head.scale(1,0.55,0.9); head.translate(0,0.02,-1.05); add(head,0);
  const finL=new THREE.SphereGeometry(1,16,8); finL.scale(0.98,0.045,0.55); finL.translate(-0.78,0,0.2); add(finL,1);
  const finR=new THREE.SphereGeometry(1,16,8); finR.scale(0.98,0.045,0.55); finR.translate(0.78,0,0.2); add(finR,1);
  const tail=new THREE.CylinderGeometry(0.1,0.015,1.3,6); tail.rotateX(Math.PI/2);
  tail.translate(0,0,1.55); tail.scale(0.25,1,1); add(tail,2);
  return mergeGeometries(parts);
}
const rayGeo=rayGeometry();
function rayMaterial(topC,bellyC){
  return new THREE.ShaderMaterial({
    uniforms:{uTime:envU.uTime,uTop:{value:new THREE.Color(topC)},
      uBelly:{value:new THREE.Color(bellyC)},uLight:envU.uSunDir,uDay:envU.uDay},
    vertexShader:`attribute float aMask; uniform float uTime; varying vec3 vN,vW;
      void main(){ vec3 p=position;
        if(aMask>.5&&aMask<1.5){ float ax=abs(p.x);
          p.y+=sin(uTime*3.0-ax*2.4)*.3*smoothstep(.25,1.6,ax);
        } else if(aMask>1.5){
          p.y+=sin(uTime*3.0-p.z*2.2)*.22*smoothstep(.2,1.5,p.z);
        } else { p.y+=sin(uTime*2.6+p.z*1.5)*.03; }
        vN=normalize(normalMatrix*normal);
        vec4 wp=modelMatrix*vec4(p,1.); vW=wp.xyz;
        gl_Position=projectionMatrix*viewMatrix*wp; }`,
    fragmentShader:`uniform vec3 uTop,uBelly,uLight; uniform float uDay; varying vec3 vN,vW;
      void main(){ vec3 N=normalize(vN);
        float d=max(dot(N,normalize(uLight)),0.);
        float rim=pow(1.-max(dot(normalize(cameraPosition-vW),N),0.),2.);
        vec3 col=mix(uBelly,uTop,clamp(N.y*.5+.5,0.,1.))*(.3+.75*uDay*(0.4+0.6*d))+rim*vec3(.2,.35,.4)*uDay;
        gl_FragColor=vec4(col,1.); }`});
}
const rays=[];
for(let i=0;i<4;i++){
  const mesh=new THREE.Mesh(rayGeo,rayMaterial(
    [0x5a6f86,0x4a5a6e,0x6d6257,0x556b74][i],[0xd9e2ea,0xcfd8dd,0xd8cfc2,0xd4dde0][i]));
  mesh.renderOrder=1; mesh.rotation.order='YXZ';
  const a=i/4*Math.PI*2, r=4.5+Math.random()*2;
  mesh.position.set(Math.cos(a)*r,-2.4-Math.random(),Math.sin(a)*r);
  mesh.scale.setScalar(0.75+Math.random()*0.35);
  world.add(mesh);
  rays.push({mesh,heading:Math.random()*Math.PI*2,speed:0.7+Math.random()*0.35,
    phase:Math.random()*9,jumping:false,jt:0,jphase:'',jstart:null,jyaw:0});
}
// fish schools (InstancedMesh, per-instance matrices)
const fishGeo=(()=>{
  const b=new THREE.SphereGeometry(1,7,5); b.scale(0.09,0.13,0.3);
  const t=new THREE.ConeGeometry(0.09,0.16,4); t.rotateX(-Math.PI/2); t.translate(0,0,0.32);
  return mergeGeometries([b,t]);
})();
const schools=[];
for(let s=0;s<2;s++){
  const N=24;
  const im=new THREE.InstancedMesh(fishGeo,new THREE.MeshStandardMaterial({roughness:0.6,flatShading:true}),N);
  const col=new THREE.Color();
  for(let i=0;i<N;i++){ col.setHSL([0.09,0.55][s],0.7,0.5+Math.random()*0.25); im.setColorAt(i,col); }
  im.renderOrder=1; world.add(im);
  const fish=[];
  for(let i=0;i<N;i++) fish.push({off:new THREE.Vector3((Math.random()-0.5)*1.8,(Math.random()-0.5)*0.9,(Math.random()-0.5)*1.8),ph:Math.random()*9});
  schools.push({im,fish,r:4.6+s*2.2,y:-1.6-s*1.3,spd:0.35+s*0.12,ang:s*3});
}
// bubbles
const bubbles=(()=>{
  const N=42;
  const im=new THREE.InstancedMesh(new THREE.SphereGeometry(0.05,6,5),
    new THREE.MeshBasicMaterial({color:0xcfefff,transparent:true,opacity:0.4,depthWrite:false}),N);
  im.renderOrder=1; world.add(im);
  const arr=[];
  for(let i=0;i<N;i++){ const a=Math.random()*Math.PI*2,r=4+Math.random()*4;
    arr.push({x:Math.cos(a)*r,z:Math.sin(a)*r,y:-4.3+Math.random()*3,spd:0.35+Math.random()*0.4,ph:Math.random()*9}); }
  return {im,arr};
})();

/* ---------- 6. FX: droplets, splash, kayak, ray jump ---------- */
const droplets=(()=>{
  const N=120, pos=new Float32Array(N*3), vel=new Float32Array(N*3), life=new Float32Array(N);
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const pts=new THREE.Points(g,new THREE.PointsMaterial({color:0xdff6ff,size:0.09,
    transparent:true,opacity:0.9,depthWrite:false}));
  pts.renderOrder=4; pts.frustumCulled=false; world.add(pts);
  return {N,pos,vel,life,pts};
})();
function spawnSplash(x,z){
  const d=droplets; let spawned=0;
  for(let i=0;i<d.N&&spawned<45;i++){
    if(d.life[i]<=0){
      const a=Math.random()*Math.PI*2, r=Math.random()*0.4;
      d.pos[i*3]=x+Math.cos(a)*r; d.pos[i*3+1]=waterTop()+0.1; d.pos[i*3+2]=z+Math.sin(a)*r;
      d.vel[i*3]=Math.cos(a)*(0.6+Math.random()*1.4);
      d.vel[i*3+1]=2.2+Math.random()*2.8;
      d.vel[i*3+2]=Math.sin(a)*(0.6+Math.random()*1.4);
      d.life[i]=0.9+Math.random()*0.4; spawned++;
    }
  }
  spawnRipple(x,z,3); Audio.splash();
}
function updateDroplets(dt){
  const d=droplets;
  for(let i=0;i<d.N;i++){
    if(d.life[i]>0){ d.life[i]-=dt;
      d.vel[i*3+1]-=9.5*dt;
      d.pos[i*3]+=d.vel[i*3]*dt; d.pos[i*3+1]+=d.vel[i*3+1]*dt; d.pos[i*3+2]+=d.vel[i*3+2]*dt;
      if(d.pos[i*3+1]<waterTop()&&d.vel[i*3+1]<0) d.life[i]=0;
    } else d.pos[i*3+1]=-999;
  }
  d.pts.geometry.attributes.position.needsUpdate=true;
}
function updateKayak(dt){
  if(kayakState==='out'){
    kayakAngle+=dt*0.28;
    const x=Math.cos(kayakAngle)*6.3, z=Math.sin(kayakAngle)*6.3;
    kayak.position.set(x,0, z);
    kayak.lookAt(Math.cos(kayakAngle+0.1)*6.3, 0, Math.sin(kayakAngle+0.1)*6.3);
  } else if(kayakState==='back'){
    kayak.position.lerp(KAYAK_DOCK,1-Math.pow(0.06,dt));
    if(kayak.position.distanceTo(KAYAK_DOCK)<0.05){ kayakState='dock';
      kayak.position.copy(KAYAK_DOCK); kayak.rotation.set(0,0.25,0); }
  }
  if(kayakState!=='dock'){
    kayak.position.y=waterTop()+0.1+Math.sin(state.time*2)*0.025*(0.4+state.wind);
  } else kayak.position.y=waterTop()+0.1+Math.sin(state.time*1.6)*0.015;
}
function updateRays(dt){
  for(const r of rays){
    if(r.jumping){
      r.jt+=dt/1.8;
      const t=Math.min(r.jt,1);
      if(r.jphase==='approach'){
        const target=new THREE.Vector3(1.2,waterTop()-0.6,3.4);
        r.mesh.position.lerp(target,1-Math.pow(0.02,dt));
        r.mesh.lookAt(target);
        if(r.mesh.position.distanceTo(target)<0.35){
          r.jphase='air'; r.jt=0;
          r.jstart=r.mesh.position.clone();
          r.jyaw=Math.atan2(-1,2.6); // leap toward the front glass
        }
      } else {
        const dir=new THREE.Vector3(Math.sin(r.jyaw),0,Math.cos(r.jyaw));
        const speed=5.2;
        r.mesh.position.copy(r.jstart).addScaledVector(dir,speed*1.8*t);
        r.mesh.position.y=waterTop()+Math.sin(Math.PI*t)*4.2;
        r.mesh.rotation.set(0.95-1.9*t, r.jyaw+Math.PI, 0);
        if(t>=1){ r.jumping=false; r.mesh.rotation.set(0,r.jyaw+Math.PI,0);
          spawnSplash(r.mesh.position.x,r.mesh.position.z);
          r.heading=r.jyaw+Math.PI; }
      }
      continue;
    }
    // gentle wander, stay inside the lagoon
    r.heading+=Math.sin(state.time*0.5+r.phase)*dt*0.4;
    const dir=new THREE.Vector3(Math.sin(r.heading),0,Math.cos(r.heading));
    r.mesh.position.addScaledVector(dir,r.speed*dt);
    r.mesh.position.y+=Math.sin(state.time*0.6+r.phase)*dt*0.18;
    const rr=Math.hypot(r.mesh.position.x,r.mesh.position.z);
    if(rr>7.2){ r.heading=Math.atan2(-r.mesh.position.x,-r.mesh.position.z)+Math.PI+ (Math.random()-0.5); }
    const minY=-3.5, maxY=waterTop()-0.8;
    r.mesh.position.y=THREE.MathUtils.clamp(r.mesh.position.y,minY,Math.max(minY,maxY));
    if(rr<4.0){ r.heading=Math.atan2(r.mesh.position.x,r.mesh.position.z); } // avoid island column
    r.mesh.lookAt(r.mesh.position.clone().add(dir));
  }
}

/* ---------- 7. TIME OF DAY ---------- */
const TOD={
  day:   {sky:0xbfe3ef,sun:0xfff2dd,sunPos:[8,12,6],  sunI:2.4,hemiSky:0xcfe8f5,hemiG:0x9a7b52,hemiI:0.85,glow:0,star:0,day:1},
  sunset:{sky:0xf0b088,sun:0xff9a4d,sunPos:[11,4,-6], sunI:2.1,hemiSky:0xf7c9a0,hemiG:0x6b4a3a,hemiI:0.6, glow:0.6,star:0.1,day:0.7},
  night: {sky:0x101a2c,sun:0x7f9cc9,sunPos:[-6,9,-4], sunI:0.5,hemiSky:0x24314a,hemiG:0x141a26,hemiI:0.35,glow:1,  star:1,  day:0.25},
};
let todTarget=TOD.day, glowCur=0;
const _c1=new THREE.Color(),_c2=new THREE.Color();
scene.background=new THREE.Color(TOD.day.sky);
scene.fog=new THREE.FogExp2(TOD.day.sky,0.008);
function lerpTOD(dt){
  const k=1-Math.exp(-dt*1.6), T=todTarget;
  scene.background.lerp(_c1.setHex(T.sky),k);
  scene.fog.color.copy(scene.background);
  sun.color.lerp(_c1.setHex(T.sun),k);
  sun.intensity+=(T.sunI-sun.intensity)*k;
  sun.position.lerp(_c2.set(...T.sunPos),k);
  hemi.color.lerp(_c1.setHex(T.hemiSky),k);
  hemi.groundColor.lerp(_c2.setHex(T.hemiG),k);
  hemi.intensity+=(T.hemiI-hemi.intensity)*k;
  glowCur+=(T.glow-glowCur)*k;
  envU.uDay.value+=(T.day-envU.uDay.value)*k;
  window.__stars.material.opacity+=(T.star-window.__stars.material.opacity)*k;
  envU.uSunDir.value.copy(sun.position).normalize();
  cabinLight.intensity=glowCur*2.4;
  lanternLights.forEach(l=>l.light.intensity=glowCur*1.7*(0.9+0.1*Math.sin(state.time*7+l.seed)));
  glowMats.forEach(m=>{const b=0.25+glowCur*0.75; m.color.setRGB(b,b*0.78,b*0.5);});
}

/* ---------- 8. CAMERAS ---------- */
const CAMS={
  iso:  {p:new THREE.Vector3(13,10.5,13),   l:new THREE.Vector3(0,-0.6,0)},
  cabin:{p:new THREE.Vector3(5.4,3.4,8.2),  l:new THREE.Vector3(0.3,1.5,1.6)},
  under:{p:new THREE.Vector3(6.4,-1.6,7.0), l:new THREE.Vector3(0,-2.7,-0.6)},
};
let camTrans=null;
function goCam(name){
  const c=CAMS[name];
  camTrans={p0:camera.position.clone(),l0:controls.target.clone(),p1:c.p,l1:c.l,t:0,dur:1.7};
}
controls.addEventListener('start',()=>camTrans=null);
function updateCam(dt){
  if(!camTrans) return;
  camTrans.t=Math.min(camTrans.t+dt/camTrans.dur,1);
  const e=camTrans.t<0.5? 2*camTrans.t*camTrans.t : 1-Math.pow(-2*camTrans.t+2,2)/2;
  camera.position.lerpVectors(camTrans.p0,camTrans.p1,e);
  controls.target.lerpVectors(camTrans.l0,camTrans.l1,e);
  if(camTrans.t>=1) camTrans=null;
}

/* ---------- 9. AUDIO (procedural, starts on first interaction) ---------- */
const Audio={ctx:null,master:null,musicGain:null,on:false,musicOn:false,
  nextChord:0,chordIdx:0,timer:null,
  init(){
    if(this.ctx) return;
    const AC=window.AudioContext||window.webkitAudioContext; this.ctx=new AC();
    this.master=this.ctx.createGain(); this.master.gain.value=0.7; this.master.connect(this.ctx.destination);
    // wind: looped noise through bandpass
    const nb=this.ctx.createBuffer(1,this.ctx.sampleRate*2,this.ctx.sampleRate);
    const nd=nb.getChannelData(0); for(let i=0;i<nd.length;i++) nd[i]=Math.random()*2-1;
    const mkNoise=(freq,q,g)=>{ const s=this.ctx.createBufferSource(); s.buffer=nb; s.loop=true;
      const f=this.ctx.createBiquadFilter(); f.type='bandpass'; f.frequency.value=freq; f.Q.value=q;
      const gn=this.ctx.createGain(); gn.gain.value=g; s.connect(f).connect(gn).connect(this.master); s.start();
      const lfo=this.ctx.createOscillator(), lg=this.ctx.createGain();
      lfo.frequency.value=0.1+Math.random()*0.06; lg.gain.value=g*0.6;
      lfo.connect(lg).connect(gn.gain); lfo.start(); return gn; };
    this.windGain=mkNoise(420,0.5,0.05);
    this.waterGain=mkNoise(240,0.8,0.05);
    // music bus
    this.musicGain=this.ctx.createGain(); this.musicGain.gain.value=0;
    const lp=this.ctx.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=1000;
    this.musicGain.connect(lp).connect(this.master);
    const prog=[[220,261.6,329.6],[174.6,220,261.6],[261.6,329.6,392],[196,246.9,293.7]];
    this.prog=prog; this.nextChord=this.ctx.currentTime+0.1;
    this.timer=setInterval(()=>this.schedule(),400);
    this.setWind(state.wind);
  },
  schedule(){
    if(!this.ctx||!this.musicOn) return;
    while(this.nextChord<this.ctx.currentTime+1.2){
      this.chord(this.prog[this.chordIdx%4],this.nextChord);
      if(Math.random()<0.5) this.bell(this.nextChord+1+Math.random()*3);
      this.chordIdx++; this.nextChord+=5.5;
    }
  },
  chord(freqs,t){
    for(const f of freqs){
      const o=this.ctx.createOscillator(); o.type='sine'; o.frequency.value=f;
      const o2=this.ctx.createOscillator(); o2.type='triangle'; o2.frequency.value=f*2;
      const g=this.ctx.createGain(); g.gain.setValueAtTime(0,t);
      g.gain.linearRampToValueAtTime(0.05,t+1.8); g.gain.linearRampToValueAtTime(0,t+6.4);
      const g2=this.ctx.createGain(); g2.gain.value=0.15;
      o.connect(g); o2.connect(g2).connect(g); g.connect(this.musicGain);
      o.start(t); o.stop(t+6.6); o2.start(t); o2.stop(t+6.6);
    }
  },
  bell(t){
    const penta=[392,440,523.3,587.3,659.3];
    const o=this.ctx.createOscillator(); o.type='triangle';
    o.frequency.value=penta[Math.floor(Math.random()*5)];
    const g=this.ctx.createGain(); g.gain.setValueAtTime(0.09,t);
    g.gain.exponentialRampToValueAtTime(0.0001,t+2.2);
    o.connect(g).connect(this.musicGain); o.start(t); o.stop(t+2.4);
  },
  splash(){
    if(!this.ctx) return;
    const dur=0.5, b=this.ctx.createBuffer(1,this.ctx.sampleRate*dur,this.ctx.sampleRate);
    const d=b.getChannelData(0); for(let i=0;i<d.length;i++) d[i]=(Math.random()*2-1)*(1-i/d.length);
    const s=this.ctx.createBufferSource(); s.buffer=b;
    const f=this.ctx.createBiquadFilter(); f.type='bandpass'; f.frequency.value=900; f.Q.value=0.7;
    const g=this.ctx.createGain(); g.gain.setValueAtTime(0.35,this.ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001,this.ctx.currentTime+dur);
    s.connect(f).connect(g).connect(this.master); s.start();
  },
  setMusic(on){ this.musicOn=on; if(!this.ctx) this.init();
    this.musicGain.gain.linearRampToValueAtTime(on?1:0,this.ctx.currentTime+1); },
  setVol(v){ if(this.master) this.master.gain.value=v; },
  setWind(w){ if(this.windGain) this.windGain.gain.value=0.02+w*0.09; },
};
addEventListener('pointerdown',()=>Audio.init(),{once:true});

/* ---------- 10. UI ---------- */
const $=id=>document.getElementById(id);
const tideEl=$('tide'), windEl=$('wind'), volEl=$('vol');
tideEl.oninput=()=>{ state.tide=+tideEl.value; $('tideVal').textContent=state.tide.toFixed(1); };
windEl.oninput =()=>{ state.wind=+windEl.value; envU.uWind.value=state.wind;
  $('windVal').textContent=Math.round(state.wind*100)+'%'; Audio.setWind(state.wind); };
volEl.oninput  =()=>Audio.setVol(+volEl.value);
document.querySelectorAll('.cam').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.cam').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); goCam(b.dataset.cam);
});
document.querySelectorAll('.tod').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.tod').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); todTarget=TOD[b.dataset.tod];
});
$('actKayak').onclick=()=>{
  if(kayakState==='dock'){ kayakState='out'; kayakAngle=Math.PI/2;
    $('actKayak').textContent='Recall kayak'; $('actKayak').classList.add('active');
  } else if(kayakState==='out'){ kayakState='back'; }
};
$('actRay').onclick=()=>{
  const r=rays.find(r=>!r.jumping); if(!r) return;
  r.jumping=true; r.jphase='approach'; r.jt=0; Audio.splash();
};
$('actPause').onclick=()=>{ state.paused=!state.paused;
  $('actPause').textContent=state.paused?'Resume':'Pause';
  $('actPause').classList.toggle('active',state.paused); };
$('actReset').onclick=()=>{
  state.tide=0; tideEl.value=0; $('tideVal').textContent='0.0';
  state.wind=0.45; windEl.value=0.45; envU.uWind.value=0.45; $('windVal').textContent='45%';
  todTarget=TOD.day; document.querySelectorAll('.tod').forEach(x=>x.classList.toggle('active',x.dataset.tod==='day'));
  kayakState='dock'; kayak.position.copy(KAYAK_DOCK); kayak.rotation.set(0,0.25,0);
  $('actKayak').textContent='Launch kayak'; $('actKayak').classList.remove('active');
  rays.forEach(r=>r.jumping=false);
  state.paused=false; $('actPause').textContent='Pause'; $('actPause').classList.remove('active');
  goCam('iso'); document.querySelectorAll('.cam').forEach(x=>x.classList.toggle('active',x.dataset.cam==='iso'));
};
$('actMusic').onclick=()=>{ Audio.setMusic(!Audio.musicOn);
  $('actMusic').textContent=Audio.musicOn?'♪ Music off':'♪ Music on';
  $('actMusic').classList.toggle('active',Audio.musicOn); };
$('quality').onchange=e=>{
  state.quality=e.target.value;
  const caps={high:1.75,med:1,low:0.75}, sm={high:2048,med:1024,low:512};
  renderer.setPixelRatio(Math.min(devicePixelRatio,caps[state.quality]));
  sun.shadow.mapSize.set(sm[state.quality],sm[state.quality]);
  if(sun.shadow.map){ sun.shadow.map.dispose(); sun.shadow.map=null; }
};
$('panelToggle').onclick=()=>$('panels').classList.toggle('hidden');
if(innerWidth<760) $('panels').classList.add('hidden');
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
renderer.setPixelRatio(Math.min(devicePixelRatio,1));

/* ---------- 11. MAIN LOOP ---------- */
goCam('iso');
let first=true;
function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05);
  if(!state.paused){
    state.time+=dt; envU.uTime.value=state.time;
    // tide follows water group; foam ring hugs the shoreline
    waterGroup.position.y=state.tide;
    foam.position.y=0.035;
    const fr=islandRadiusAtY(state.tide+0.02)+0.06;
    foam.scale.setScalar(fr);
    updateRays(dt); updateKayak(dt); updateDroplets(dt);
    // fish schools
    const d=new THREE.Object3D();
    for(const s of schools){
      s.ang+=dt*s.spd;
      const cx=Math.cos(s.ang)*s.r, cz=Math.sin(s.ang)*s.r;
      const tan=new THREE.Vector3(-Math.sin(s.ang),0,Math.cos(s.ang));
      s.fish.forEach((f,i)=>{
        const wob=new THREE.Vector3(Math.sin(state.time*2+f.ph)*0.15,
          Math.sin(state.time*1.5+f.ph*2)*0.08, Math.cos(state.time*2.3+f.ph)*0.15);
        const p=new THREE.Vector3(cx,f.y+s.y+Math.sin(state.time+f.ph)*0.15,cz).add(f.off).add(wob);
        p.y=THREE.MathUtils.clamp(p.y,-4.0,waterTop()-0.5);
        d.position.copy(p); d.lookAt(p.clone().add(tan)); d.updateMatrix();
        s.im.setMatrixAt(i,d.matrix);
      });
      s.im.instanceMatrix.needsUpdate=true;
    }
    // bubbles
    const bd=new THREE.Object3D();
    bubbles.arr.forEach((b,i)=>{
      b.y+=b.spd*dt*(0.6+state.wind*0.6);
      if(b.y>waterTop()-0.15){ b.y=-4.3; const a=Math.random()*Math.PI*2,r=4+Math.random()*4;
        b.x=Math.cos(a)*r; b.z=Math.sin(a)*r; }
      bd.position.set(b.x+Math.sin(state.time*2+b.ph)*0.08,b.y,b.z);
      bd.scale.setScalar(0.6+Math.sin(b.ph+state.time)*0.3+0.5);
      bd.updateMatrix(); bubbles.im.setMatrixAt(i,bd.matrix);
    });
    bubbles.im.instanceMatrix.needsUpdate=true;
    // ripples
    for(let i=ripples.length-1;i>=0;i--){
      const r=ripples[i]; r.t+=dt*0.7;
      if(r.t>1){ world.remove(r.m); r.m.material.dispose(); ripples.splice(i,1); continue; }
      if(r.t>0){ r.m.scale.setScalar(0.25+r.t*9); r.m.material.opacity=0.55*(1-r.t);
        r.m.position.y=waterTop()+0.04; }
    }
    lerpTOD(dt);
  }
  updateCam(dt);
  controls.update();
  renderer.render(scene,camera);
  if(first){ first=false; setTimeout(()=>$('loading').classList.add('gone'),300); }
}
animate();
</script>
</body>
</html>
```

**Highlights of the build:**

- **Cutaway water done right** — an extruded water volume with a hole around the island gives clean cross-section walls; a separate high-density wave plane handles the animated surface, and the opaque island hides it via depth testing, so there is **no z-fighting at the shoreline**. All transparent layers use `depthWrite:false` with explicit `renderOrder` (fish → water → foam → ripples → glass).
- **Living lagoon** — 4 shader-animated manta rays (undulating fins/tail via a vertex mask attribute), 2 instanced fish schools, swaying kelp, rising bubbles, and a caustics shader on the seabed.
- **Ray leap** — approach → parabolic arc with pitch → splash with droplet particles, expanding ripples, and a procedural splash sound.
- **Tide slider** moves the whole water group; foam ring, kayak float, ripple height, and ray depth ceiling all follow.
- **Time of day** smoothly lerps sun, hemisphere, sky, fog, stars, water brightness, and flickering lantern/cabin lights.
- **Audio** — generative pentatonic pads with bell accents, filtered-noise wind (tied to the wind slider) and lagoon ambience, all starting only after the first interaction.
- **Performance** — instanced planks, posts, rocks, fish, bubbles, grass; capped pixel ratio; 3 quality tiers with live shadow-map resizing; delta-time animation with pause support.