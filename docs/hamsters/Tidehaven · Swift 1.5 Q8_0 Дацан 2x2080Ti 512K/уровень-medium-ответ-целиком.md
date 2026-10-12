# Tidehaven

A complete, self-contained interactive 3D diorama. Save as `index.html` and open in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Tidehaven — a cozy island diorama</title>
<style>
  :root{
    --panel: rgba(16,28,38,.52);
    --panel-border: rgba(255,255,255,.14);
    --text: #eef6f4;
    --dim: #a8c0bd;
    --accent: #57d6c0;
    --accent-dark: #1d6f61;
  }
  *{ margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html,body{ width:100%; height:100%; overflow:hidden; background:#0a141c;
    font-family: ui-rounded, "SF Pro Rounded", "Segoe UI", system-ui, -apple-system, sans-serif; color:var(--text); }
  #app{ position:fixed; inset:0; }
  canvas{ display:block; }

  /* ---------- Typography & panels ---------- */
  .panel{
    position:fixed; background:var(--panel); border:1px solid var(--panel-border);
    border-radius:16px; backdrop-filter: blur(14px) saturate(1.3); -webkit-backdrop-filter: blur(14px) saturate(1.3);
    box-shadow: 0 10px 40px rgba(0,0,0,.28); padding:14px 16px; z-index:10; user-select:none;
    transition: transform .35s cubic-bezier(.2,.9,.3,1), opacity .3s;
  }
  .panel h2{ font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--dim);
    font-weight:700; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; }
  .panel h2 .chev{ transition:transform .3s; font-size:10px; }
  .panel.collapsed .body{ display:none; }
  .panel.collapsed h2 .chev{ transform:rotate(-90deg); }

  #titlePanel{ top:18px; left:18px; padding:16px 20px; pointer-events:none; }
  #titlePanel h1{ font-size:26px; font-weight:800; letter-spacing:.02em;
    background:linear-gradient(120deg,#eafff9 20%, #7fe8d2 70%); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
  #titlePanel p{ font-size:12px; color:var(--dim); margin-top:3px; letter-spacing:.04em; }

  #worldPanel{ top:18px; right:18px; width:230px; }
  #cameraPanel{ bottom:18px; left:18px; }
  #actionPanel{ bottom:18px; left:50%; transform:translateX(-50%); }
  #audioPanel{ bottom:18px; right:18px; width:200px; }

  .row{ display:flex; gap:8px; margin-bottom:8px; align-items:center; }
  .row:last-child{ margin-bottom:0; }
  .row.wrap{ flex-wrap:wrap; }
  .lbl{ font-size:11px; color:var(--dim); letter-spacing:.05em; min-width:38px; }
  .val{ font-size:11px; color:var(--accent); min-width:34px; text-align:right; font-variant-numeric:tabular-nums;}

  button{
    font-family:inherit; font-size:12px; font-weight:600; letter-spacing:.03em; color:var(--text);
    background:rgba(255,255,255,.08); border:1px solid var(--panel-border); border-radius:10px;
    padding:8px 12px; cursor:pointer; transition:background .18s, transform .1s, border-color .18s, color .18s;
    flex:1; white-space:nowrap;
  }
  button:hover{ background:rgba(255,255,255,.16); }
  button:active{ transform:scale(.96); }
  button.active{ background:var(--accent); color:#06302a; border-color:var(--accent); box-shadow:0 0 18px rgba(87,214,192,.35); }
  button.big{ padding:10px 16px; font-size:13px; }

  input[type=range]{ flex:1; appearance:none; -webkit-appearance:none; height:4px; border-radius:2px;
    background:rgba(255,255,255,.22); outline:none; cursor:pointer; }
  input[type=range]::-webkit-slider-thumb{ -webkit-appearance:none; width:15px; height:15px; border-radius:50%;
    background:var(--accent); border:2px solid #06302a; box-shadow:0 0 8px rgba(87,214,192,.6); }
  input[type=range]::-moz-range-thumb{ width:13px; height:13px; border-radius:50%; background:var(--accent); border:2px solid #06302a; }

  select{ font-family:inherit; font-size:12px; background:rgba(255,255,255,.08); color:var(--text);
    border:1px solid var(--panel-border); border-radius:8px; padding:6px 8px; cursor:pointer; outline:none; flex:1;}
  select option{ background:#12242f; }

  #hint{ position:fixed; bottom:18px; left:50%; transform:translateX(-50%); translate:0 64px;
    font-size:11px; color:rgba(255,255,255,.55); letter-spacing:.06em; pointer-events:none; z-index:9;
    text-shadow:0 1px 6px rgba(0,0,0,.6); }

  #loader{ position:fixed; inset:0; z-index:99; background:#0a141c; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:14px; transition:opacity .8s; }
  #loader .ring{ width:44px; height:44px; border-radius:50%; border:3px solid rgba(87,214,192,.2);
    border-top-color:var(--accent); animation:spin 1s linear infinite; }
  #loader p{ font-size:12px; letter-spacing:.2em; color:var(--dim); text-transform:uppercase; }
  @keyframes spin{ to{ transform:rotate(360deg);} }
  #loader.gone{ opacity:0; pointer-events:none; }

  @media (max-width: 820px){
    #titlePanel h1{ font-size:20px; } #titlePanel p{ display:none; }
    #worldPanel{ width:190px; top:14px; right:14px; padding:10px 12px; }
    #cameraPanel, #audioPanel{ width:150px; padding:10px 12px; }
    #actionPanel{ bottom:84px; padding:10px 12px; max-width:92vw; }
    #cameraPanel{ bottom:14px; left:14px; } #audioPanel{ bottom:14px; right:14px; }
    #hint{ display:none; }
    .row.wrap button{ flex:1 1 40%; }
  }
</style>
</head>
<body>
<div id="app"></div>

<div id="loader"><div class="ring"></div><p>Building Tidehaven…</p></div>

<div id="titlePanel" class="panel">
  <h1>Tidehaven</h1>
  <p>a cozy island, and a living lagoon beneath it</p>
</div>

<div id="worldPanel" class="panel">
  <h2 data-collapse>World <span class="chev">▾</span></h2>
  <div class="body">
    <div class="row"><span class="lbl">Tide</span><input id="tide" type="range" min="0" max="1" step="0.001" value="0.5"><span class="val" id="tideVal">0.0m</span></div>
    <div class="row"><span class="lbl">Wind</span><input id="wind" type="range" min="0" max="1" step="0.001" value="0.35"><span class="val" id="windVal">35%</span></div>
    <div class="row"><span class="lbl">Light</span></div>
    <div class="row wrap">
      <button id="todDay" class="active">Day</button><button id="todSunset">Sunset</button><button id="todNight">Night</button>
    </div>
    <div class="row" style="margin-top:6px"><span class="lbl">Quality</span>
      <select id="quality"><option value="low">Low</option><option value="med" selected>Medium</option><option value="high">High</option></select>
    </div>
    <div class="row"><button id="pauseBtn">⏸ Pause</button><button id="resetBtn">↺ Reset</button></div>
  </div>
</div>

<div id="cameraPanel" class="panel">
  <h2 data-collapse>Camera <span class="chev">▾</span></h2>
  <div class="body">
    <div class="row wrap">
      <button id="camIso" class="active">Isometric</button><button id="camCabin">Cabin</button><button id="camWater">Underwater</button>
    </div>
  </div>
</div>

<div id="actionPanel" class="panel">
  <div class="row">
    <button id="kayakBtn" class="big">🛶 Launch Kayak</button>
    <button id="rayBtn" class="big">✨ Ray Leap</button>
  </div>
</div>

<div id="audioPanel" class="panel">
  <h2 data-collapse>Audio <span class="chev">▾</span></h2>
  <div class="body">
    <div class="row"><button id="musicBtn">♪ Music Off</button></div>
    <div class="row"><span class="lbl">Volume</span><input id="volume" type="range" min="0" max="1" step="0.01" value="0.7"></div>
  </div>
</div>

<div id="hint">drag to orbit · scroll to zoom · panels collapse on tap</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
   TIDEHAVEN — single-file coastal diorama
   Sections: state · core · sky/light · island · water · cabin
             pier · nature · wildlife · effects · audio · UI · loop
   ============================================================ */

/* ---------------- Global state ---------------- */
const S = {
  worldTime: 0, paused: false,
  tide: 0.0, wind: 0.35, windSmooth: 0.35,
  waterY: 0.0,
  tod: 'day', todBlend: 0,            // blend progress toward target preset
  kayakState: 'moored', kayakT: 0, kayakAngle: 0,
  rayJump: null,                       // active jump animation data
  quality: 'med',
  camAnim: null,
};
const BASE_WATER_Y = 0.0;
const TIDE_RANGE = 1.1;                // total tide travel
const SHORE_R = 6.75;                  // approx island shoreline radius

/* ---------------- Core ---------------- */
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias:true, powerPreference:'high-performance' });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x9ed4e0, 0.010);

const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.1, 300);
camera.position.set(17, 13, 17);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.06;
controls.minDistance = 3.5; controls.maxDistance = 46;
controls.maxPolarAngle = Math.PI * 0.72;
controls.target.set(0, 0.5, 0);

/* ---------------- Lighting & sky ---------------- */
const hemi = new THREE.HemisphereLight(0xbfe8f0, 0xc9a06a, 0.75);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2d8, 2.4);
sun.position.set(12, 16, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -16; sun.shadow.camera.right = 16;
sun.shadow.camera.top = 16; sun.shadow.camera.bottom = -16;
sun.shadow.camera.near = 1; sun.shadow.camera.far = 60;
sun.shadow.bias = -0.0012; sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);
const ambient = new THREE.AmbientLight(0xffffff, 0.12);
scene.add(ambient);

// Sky dome (gradient, updated by time-of-day)
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite:false, fog:false,
  uniforms:{ uTop:{value:new THREE.Color(0x6fc3e8)}, uBot:{value:new THREE.Color(0xd8f0ee)}, uSunDir:{value:new THREE.Vector3(0.6,0.6,0.4)}, uGlow:{value:new THREE.Color(0xffd9a0)}, uGlowAmt:{value:0.0} },
  vertexShader:`varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader:`
    uniform vec3 uTop,uBot,uGlow; uniform vec3 uSunDir; uniform float uGlowAmt; varying vec3 vDir;
    void main(){
      float h = clamp(vDir.y*0.5+0.5, 0.0, 1.0);
      vec3 c = mix(uBot, uTop, pow(h,0.8));
      float g = pow(max(dot(normalize(vDir), normalize(uSunDir)),0.0), 6.0);
      c += uGlow * g * uGlowAmt;
      gl_FragColor = vec4(c,1.0);
    }`
});
const sky = new THREE.Mesh(new THREE.SphereGeometry(120, 24, 16), skyMat);
scene.add(sky);

// Stars (visible at night)
{
  const n = 420, p = new Float32Array(n*3);
  for(let i=0;i<n;i++){ const v = new THREE.Vector3().randomDirection().multiplyScalar(100); v.y = Math.abs(v.y)*0.9+8; v.toArray(p,i*3); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p,3));
  var stars = new THREE.Points(g, new THREE.PointsMaterial({ color:0xffffff, size:0.55, transparent:true, opacity:0, depthWrite:false, fog:false }));
  scene.add(stars);
}

// Time-of-day presets (lerped smoothly every frame)
const TOD = {
  day:    { skyTop:0x6fc3e8, skyBot:0xd8f0ee, fog:0x9ed4e0, fogD:0.010, sunC:0xfff2d8, sunI:2.4, sunP:[12,16,8],  hemiS:0xbfe8f0, hemiG:0xc9a06a, hemiI:0.75, night:0, glow:0.15, exposure:1.05 },
  sunset: { skyTop:0x3a4a7a, skyBot:0xf5a465, fog:0xc98a68, fogD:0.014, sunC:0xff9a55, sunI:2.1, sunP:[17,4.5,-5], hemiS:0xf2b98a, hemiG:0x7a4a35, hemiI:0.55, night:0.35, glow:0.9, exposure:1.0 },
  night:  { skyTop:0x060b18, skyBot:0x12203a, fog:0x0c1626, fogD:0.018, sunC:0x9db8ff, sunI:0.55, sunP:[-9,13,5], hemiS:0x2c3a5c, hemiG:0x141c2c, hemiI:0.4,  night:1, glow:0.25, exposure:0.95 },
};
const cur = { // live interpolated values
  skyTop:new THREE.Color(TOD.day.skyTop), skyBot:new THREE.Color(TOD.day.skyBot), fog:new THREE.Color(TOD.day.fog),
  fogD:TOD.day.fogD, sunC:new THREE.Color(TOD.day.sunC), sunI:TOD.day.sunI, sunP:new THREE.Vector3(...TOD.day.sunP),
  hemiS:new THREE.Color(TOD.day.hemiS), hemiG:new THREE.Color(TOD.day.hemiG), hemiI:TOD.day.hemiI,
  night:0, glow:0.15, exposure:1.05
};
const tgt = JSON.parse(JSON.stringify(TOD.day)); // target preset (plain)

/* ---------------- Shared helpers ---------------- */
// deterministic pseudo-noise for terrain jitter
function hash(n){ const s = Math.sin(n*127.1+311.7)*43758.5453; return s - Math.floor(s); }
function noise1(x){ const i=Math.floor(x), f=x-i, u=f*f*(3-2*f); return (hash(i)*2-1)*(1-u) + (hash(i+1)*2-1)*u; }
// island surface height at radius r (matches lathe profile)
const PROFILE = [[0,2.3],[2.8,2.3],[4.2,1.4],[5.6,0.55],[6.5,0.05],[6.9,-0.5],[7.4,-2.4]];
function islandY(r){
  for(let i=0;i<PROFILE.length-1;i++){
    const [r0,y0]=PROFILE[i], [r1,y1]=PROFILE[i+1];
    if(r<=r1) return y0 + (y1-y0)*THREE.MathUtils.smoothstep(r, r0, r1);
  }
  return -2.4;
}

/* ============================================================
   ISLAND — displaced lathe with vertex colors, flat shading
   ============================================================ */
{
  const pts = PROFILE.map(([r,y]) => new THREE.Vector2(Math.max(r,0.001), y));
  let g = new THREE.LatheGeometry(pts, 56);
  const pos = g.attributes.position;
  for(let i=0;i<pos.count;i++){
    const x=pos.getX(i), y=pos.getY(i), z=pos.getZ(i);
    const r = Math.hypot(x,z);
    if(r > 0.2){
      const a = Math.atan2(z,x);
      const d = (noise1(a*3.1 + y*1.7) * 0.5 + noise1(a*7.7 - y*2.3) * 0.28) * (y<2.25?0.34:0.12);
      const s = 1 + d/Math.max(r,1);
      pos.setXYZ(i, x*s, y + (y>2.2?0:noise1(a*5.0+r*2.0)*0.06), z*s);
    }
  }
  g = g.toNonIndexed(); g.computeVertexNormals();
  // vertex colors: grass / sand / underwater sand
  const p = g.attributes.position, col = new Float32Array(p.count*3);
  const cGrass=new THREE.Color(0x74b04f), cGrass2=new THREE.Color(0x5d9944),
        cSand=new THREE.Color(0xe6cd96), cDeep=new THREE.Color(0xc2a271), tmp=new THREE.Color();
  for(let i=0;i<p.count;i++){
    const y=p.getY(i), x=p.getX(i), z=p.getZ(i);
    if(y > 0.75) tmp.copy(cGrass).lerp(cGrass2, 0.5+0.5*noise1(x*2.2+z*3.1));
    else if(y > 0.02) tmp.copy(cSand).lerp(cGrass, THREE.MathUtils.smoothstep(y,0.05,0.75));
    else tmp.copy(cDeep).lerp(cSand, THREE.MathUtils.smoothstep(y,-1.2,0.0));
    col.set([tmp.r,tmp.g,tmp.b], i*3);
  }
  g.setAttribute('color', new THREE.BufferAttribute(col,3));
  const island = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors:true, flatShading:true, roughness:0.95 }));
  island.castShadow = island.receiveShadow = true;
  scene.add(island);
}

/* ============================================================
   WATER — cutaway lagoon: volume box + animated surface + seabed
   Render order: opaque(0) → volume(4) → surface(5) → foam FX(6)
   ============================================================ */
const waterUniforms = {
  uTime:{value:0}, uWind:{value:0.35}, uNight:{value:0}, uShore:{value:SHORE_R},
  uSunDir:{value:new THREE.Vector3(0.6,0.7,0.4)}
};

// --- Seabed with animated caustics ---
const seabed = new THREE.Mesh(
  new THREE.PlaneGeometry(26, 26, 1, 1),
  new THREE.ShaderMaterial({
    uniforms: waterUniforms,
    vertexShader:`varying vec2 vXZ; void main(){ vec4 wp = modelMatrix*vec4(position,1.0); vXZ = wp.xz; gl_Position = projectionMatrix*viewMatrix*wp; }`,
    fragmentShader:`
      uniform float uTime,uNight; varying vec2 vXZ;
      void main(){
        float d = length(vXZ);
        vec3 sand = vec3(0.78,0.66,0.46);
        vec3 p = vXZ*1.4;
        float c = sin(p.x*3.1+uTime*1.1)*sin(p.y*2.7-uTime*0.9)
                + sin(p.x*2.0-uTime*0.6 + p.y*2.6)
                + sin(length(p-vXZ.x*0.3)*4.0 - uTime*1.4);
        c = pow(max(0.0, c*0.3333), 3.0);
        vec3 col = sand*(0.75+0.25*sin(vXZ.x*0.8)*sin(vXZ.y*0.7)) + c*0.5*vec3(0.85,1.0,0.9);
        col *= smoothstep(15.5, 7.0, d)*0.75 + 0.25;               // darken far edges
        col *= mix(1.0, 0.22, uNight);                              // night dimming
        gl_FragColor = vec4(col,1.0);
      }`
  })
);
seabed.rotation.x = -Math.PI/2; seabed.position.y = -2.45; seabed.receiveShadow = false;
scene.add(seabed);

// --- Aquarium water volume (the cutaway faces) ---
const waterVolMat = new THREE.MeshPhongMaterial({
  color:0x2fbfb2, transparent:true, opacity:0.16, depthWrite:false,
  shininess:80, specular:0x88ffff, side:THREE.FrontSide
});
const waterVol = new THREE.Mesh(new THREE.BoxGeometry(26,1,26), waterVolMat);
waterVol.renderOrder = 4;
scene.add(waterVol);

// --- Animated water surface ---
const waterSurf = new THREE.Mesh(
  new THREE.PlaneGeometry(26, 26, 130, 130),
  new THREE.ShaderMaterial({
    transparent:true, depthWrite:false, side:THREE.DoubleSide,
    uniforms: waterUniforms,
    vertexShader:`
      uniform float uTime,uWind; varying vec3 vWorld; varying float vWave;
      void main(){
        vec4 wp = modelMatrix*vec4(position,1.0);
        float w = sin(wp.x*1.3 + uTime*1.5)*0.055
                + sin(wp.z*1.7 - uTime*1.1)*0.045
                + sin((wp.x+wp.z)*2.4 + uTime*2.2)*0.028;
        w *= 0.3 + uWind*1.6;
        wp.y += w; vWave = w; vWorld = wp.xyz;
        gl_Position = projectionMatrix*viewMatrix*wp;
      }`,
    fragmentShader:`
      uniform float uTime,uWind,uNight,uShore; uniform vec3 uSunDir; varying vec3 vWorld; varying float vWave;
      void main(){
        float d = length(vWorld.xz);
        vec3 shallow = vec3(0.28,0.82,0.76), deep = vec3(0.04,0.40,0.48);
        vec3 col = mix(deep, shallow, smoothstep(11.5, 5.0, d));
        vec3 V = normalize(cameraPosition - vWorld);
        float fres = pow(1.0 - max(dot(V, vec3(0.0,1.0,0.0)), 0.0), 3.0);
        float alpha = 0.40 + 0.45*fres;
        // sun glint
        float glint = pow(max(sin(vWorld.x*7.0+uTime*2.1)*sin(vWorld.z*6.0-uTime*1.6),0.0), 18.0);
        col += vec3(1.0,0.95,0.8)*glint*0.35*max(0.0,1.0-uNight*1.4);
        // shoreline foam band
        float band = smoothstep(uShore+1.25, uShore+0.1, d) * smoothstep(uShore-0.55, uShore+0.05, d);
        float wob = 0.5 + 0.5*sin(d*20.0 - uTime*3.0 + atan(vWorld.z,vWorld.x)*5.0 + vWave*24.0);
        float foam = clamp(band*wob*1.25, 0.0, 1.0);
        col = mix(col, vec3(0.97,1.0,0.99), foam*0.9);
        alpha = mix(alpha, 0.95, foam);
        // night tint
        col = mix(col, vec3(0.05,0.16,0.26), uNight*0.72);
        gl_FragColor = vec4(col, alpha);
      }`
  })
);
waterSurf.rotation.x = -Math.PI/2; waterSurf.renderOrder = 5;
scene.add(waterSurf);

function updateWaterTide(){
  S.waterY = BASE_WATER_Y + (S.tide - 0.5) * TIDE_RANGE;
  waterSurf.position.y = S.waterY;
  const h = (S.waterY + 2.45);
  waterVol.scale.y = h; waterVol.position.y = -2.45 + h/2;
}
updateWaterTide();

/* ============================================================
   CABIN — A-frame with copper roof, deck, glowing windows
   ============================================================ */
const cabinGroup = new THREE.Group();
const glowMats = [];   // window/lantern materials that light up at night
const lampLights = []; // point lights for lanterns/windows
{
  const wood = new THREE.MeshStandardMaterial({ color:0x8a5a34, roughness:0.85 });
  const woodDark = new THREE.MeshStandardMaterial({ color:0x6b4526, roughness:0.9 });
  const copper = new THREE.MeshStandardMaterial({ color:0x4fa08c, metalness:0.75, roughness:0.35 });
  const glassGlow = new THREE.MeshStandardMaterial({ color:0xffd9a0, emissive:0xffb347, emissiveIntensity:0.2, roughness:0.4 });
  glowMats.push(glassGlow);

  const T = 2.32; // plateau top
  cabinGroup.position.set(0.6, T, -0.6);

  // Deck
  const deck = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.14, 2.6), wood);
  deck.position.set(0, 0.07, 0.4); deck.castShadow = deck.receiveShadow = true;
  cabinGroup.add(deck);

  // A-frame roof panels (patinated copper)
  const roofGeo = new THREE.BoxGeometry(2.35, 0.09, 2.5);
  for(const s of [-1,1]){
    const r = new THREE.Mesh(roofGeo, copper);
    r.position.set(s*0.62, 1.32, -0.55); r.rotation.z = s * -0.72;
    r.castShadow = true; cabinGroup.add(r);
  }
  // ridge beam
  const ridge = new THREE.Mesh(new THREE.BoxGeometry(0.14,0.14,2.62), woodDark);
  ridge.position.set(0, 2.16, -0.55); ridge.castShadow = true; cabinGroup.add(ridge);

  // Gable walls (triangles) front & back
  const tri = new THREE.Shape(); tri.moveTo(-1.05,0); tri.lineTo(1.05,0); tri.lineTo(0,1.95); tri.closePath();
  const triGeo = new THREE.ExtrudeGeometry(tri, { depth:0.08, bevelEnabled:false });
  for(const z of [-1.8, 0.68]){
    const w = new THREE.Mesh(triGeo, woodDark);
    w.position.set(0, 0.14, z); w.castShadow = true; cabinGroup.add(w);
  }
  // Side walls (inset, slanted)
  const sideGeo = new THREE.PlaneGeometry(2.5, 2.05);
  for(const s of [-1,1]){
    const w = new THREE.Mesh(sideGeo, wood);
    w.position.set(s*0.98, 1.06, -0.56); w.rotation.y = s*Math.PI/2; w.rotation.x = 0;
    w.rotation.order='YXZ'; w.rotation.z = s*-0.72; w.rotation.y = s*Math.PI/2;
    w.castShadow = true; cabinGroup.add(w);
  }

  // Glowing front window + door
  const win = new THREE.Mesh(new THREE.PlaneGeometry(0.85, 0.62), glassGlow);
  win.position.set(0, 1.02, 0.77); cabinGroup.add(win);
  const winFrame = new THREE.Mesh(new THREE.BoxGeometry(0.98,0.74,0.05), woodDark);
  winFrame.position.set(0, 1.02, 0.745); cabinGroup.add(winFrame); win.position.z = 0.775;
  const door = new THREE.Mesh(new THREE.BoxGeometry(0.52, 1.0, 0.06), woodDark);
  door.position.set(-0.55, 0.64, 0.74); cabinGroup.add(door);

  // Warm interior light
  const interior = new THREE.PointLight(0xffb35c, 0, 7, 2);
  interior.position.set(0, 1.1, 0.2); cabinGroup.add(interior);
  lampLights.push(interior);

  // Railing posts along deck front
  const postGeo = new THREE.CylinderGeometry(0.045,0.045,0.55,6);
  for(let i=0;i<5;i++){
    const p = new THREE.Mesh(postGeo, woodDark);
    p.position.set(-1.6+i*0.8, 0.42, 1.65); p.castShadow=true; cabinGroup.add(p);
  }
  const rail = new THREE.Mesh(new THREE.BoxGeometry(3.4,0.06,0.06), woodDark);
  rail.position.set(0,0.68,1.65); cabinGroup.add(rail);

  // Bench
  const bench = new THREE.Group();
  const seat = new THREE.Mesh(new THREE.BoxGeometry(1.0,0.08,0.34), wood); seat.position.y=0.36;
  for(const s of [-1,1]){ const l = new THREE.Mesh(new THREE.BoxGeometry(0.08,0.36,0.28), woodDark); l.position.set(s*0.42,0.18,0); bench.add(l); }
  bench.add(seat); bench.position.set(1.25, 0.14, 1.15); bench.rotation.y = -0.5;
  bench.traverse(o=>{ if(o.isMesh) o.castShadow=true; }); cabinGroup.add(bench);

  // Towels — one draped on the rail, one on the bench
  const towel1 = new THREE.Mesh(new THREE.BoxGeometry(0.55,0.03,0.4), new THREE.MeshStandardMaterial({color:0xe86f5a, roughness:0.95}));
  towel1.position.set(0.7,0.71,1.68); towel1.rotation.x=0.06; towel1.castShadow=true; cabinGroup.add(towel1);
  const towel2 = new THREE.Mesh(new THREE.BoxGeometry(0.45,0.03,0.3), new THREE.MeshStandardMaterial({color:0x53a6d6, roughness:0.95}));
  towel2.position.set(1.25,0.41,1.15); towel2.rotation.y=-0.5; towel2.castShadow=true; cabinGroup.add(towel2);

  // Crates
  const crateGeo = new THREE.BoxGeometry(0.42,0.42,0.42);
  const crateMat = new THREE.MeshStandardMaterial({ color:0x9c7042, roughness:0.9 });
  [[-1.45,0.35,1.2,0.3],[-1.15,0.35,1.45,-0.2],[-1.3,0.77,1.3,0.1]].forEach(([x,y,z,ry])=>{
    const c = new THREE.Mesh(crateGeo, crateMat); c.position.set(x,y,z); c.rotation.y=ry; c.castShadow=true; cabinGroup.add(c);
  });

  // Potted plants
  const potGeo = new THREE.CylinderGeometry(0.14,0.11,0.2,8);
  const potMat = new THREE.MeshStandardMaterial({ color:0xc4744a, roughness:0.85 });
  const leafGeo = new THREE.IcosahedronGeometry(0.17, 0);
  const leafMat = new THREE.MeshStandardMaterial({ color:0x4f9e3f, roughness:0.9, flatShading:true });
  [[1.7,0.24,0.4],[1.62,0.24,-0.1],[-1.68,0.24,0.5],[0.55,0.24,1.5]].forEach(([x,y,z])=>{
    const pot = new THREE.Mesh(potGeo, potMat); pot.position.set(x,y,z); pot.castShadow=true;
    const leaves = new THREE.Mesh(leafGeo, leafMat); leaves.position.set(x,y+0.24,z); leaves.scale.set(1,1.25,1); leaves.castShadow=true;
    cabinGroup.add(pot, leaves);
  });

  scene.add(cabinGroup);
}

/* ============================================================
   PIER — planks, posts, ladder, lanterns, moored kayak
   ============================================================ */
const pierGroup = new THREE.Group();
const PIER_Y = 0.48, PIER_X0 = 5.9, PIER_X1 = 11.4;
const kayak = new THREE.Group();
{
  const wood = new THREE.MeshStandardMaterial({ color:0x9a6b3f, roughness:0.9 });
  const woodDark = new THREE.MeshStandardMaterial({ color:0x6e4a26, roughness:0.9 });

  // planks (instanced)
  const plankGeo = new THREE.BoxGeometry(0.34, 0.07, 1.5);
  const nPlanks = 18;
  const planks = new THREE.InstancedMesh(plankGeo, wood, nPlanks);
  planks.castShadow = planks.receiveShadow = true;
  const m = new THREE.Matrix4();
  for(let i=0;i<nPlanks;i++){
    m.makeTranslation(PIER_X0 + i*(PIER_X1-PIER_X0)/(nPlanks-1), PIER_Y, 0.4);
    planks.setMatrixAt(i, m);
  }
  pierGroup.add(planks);

  // posts (instanced) — down to the seabed
  const postGeo = new THREE.CylinderGeometry(0.09, 0.11, 3.1, 7);
  const posts = new THREE.InstancedMesh(postGeo, woodDark, 8);
  posts.castShadow = true;
  let pi = 0;
  for(const x of [6.4, 8.2, 10.0, 11.1]) for(const z of [-0.25, 1.05]){
    m.makeTranslation(x, PIER_Y - 1.55, z); posts.setMatrixAt(pi++, m);
  }
  pierGroup.add(posts);

  // ladder into the water at the pier end
  const railGeo = new THREE.CylinderGeometry(0.045,0.045,1.9,6);
  for(const z of [-0.05, 0.5]){
    const r = new THREE.Mesh(railGeo, woodDark);
    r.position.set(11.55, PIER_Y-0.75, z); r.rotation.z = 0.12; r.castShadow=true; pierGroup.add(r);
  }
  const rungGeo = new THREE.CylinderGeometry(0.035,0.035,0.62,6);
  for(let i=0;i<4;i++){
    const rg = new THREE.Mesh(rungGeo, woodDark);
    rg.position.set(11.55 - (0.12*(i*0.45)), PIER_Y-0.25-i*0.42, 0.225);
    rg.rotation.x = Math.PI/2; rg.castShadow=true; pierGroup.add(rg);
  }

  // lanterns (two on the pier)
  const lampPostGeo = new THREE.CylinderGeometry(0.05,0.06,0.85,6);
  const lampBoxGeo = new THREE.BoxGeometry(0.18,0.22,0.18);
  const lampGlassGeo = new THREE.SphereGeometry(0.09, 10, 8);
  const lampMat = new THREE.MeshStandardMaterial({ color:0xffe0a8, emissive:0xffb347, emissiveIntensity:0.15 });
  glowMats.push(lampMat);
  for(const x of [8.2, 11.1]){
    const p = new THREE.Mesh(lampPostGeo, woodDark); p.position.set(x, PIER_Y+0.45, -0.28); p.castShadow=true;
    const b = new THREE.Mesh(lampBoxGeo, woodDark); b.position.set(x, PIER_Y+0.98, -0.28);
    const g = new THREE.Mesh(lampGlassGeo, lampMat); g.position.set(x, PIER_Y+0.98, -0.28);
    pierGroup.add(p,b,g);
    const L = new THREE.PointLight(0xffb35c, 0, 5.5, 2); L.position.set(x, PIER_Y+1.0, -0.28);
    pierGroup.add(L); lampLights.push(L);
  }

  // kayak (capsule hull + rim + paddle)
  const hullMat = new THREE.MeshStandardMaterial({ color:0xf08a3c, roughness:0.4, metalness:0.05 });
  const hull = new THREE.Mesh(new THREE.CapsuleGeometry(0.26, 1.35, 4, 10), hullMat);
  hull.rotation.z = Math.PI/2; hull.scale.y = 0.55; hull.castShadow = true;
  const rim = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.035, 6, 14), new THREE.MeshStandardMaterial({ color:0xd96f22, roughness:0.5 }));
  rim.rotation.y = Math.PI/2; rim.scale.set(1, 0.6, 3.6); rim.position.y = 0.11;
  const paddle = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.03, 0.09), wood);
  paddle.position.set(0, 0.18, 0.18); paddle.rotation.y = 0.5;
  kayak.add(hull, rim, paddle);
  kayak.position.set(10.6, S.waterY+0.12, 1.5);
  scene.add(kayak);

  // mooring rope
  const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.015,0.015,1.0,4), new THREE.MeshStandardMaterial({color:0xcbb98a}));
  rope.position.set(11.15, PIER_Y-0.15, 1.0); rope.rotation.z = 0.9; rope.rotation.x = -0.4;
  pierGroup.add(rope);

  scene.add(pierGroup);
}

/* ============================================================
   NATURE — trees, rocks, grass tufts, kelp, buoys (instanced)
   ============================================================ */
const swayUniforms = { uTime:{value:0}, uWind:{value:0.35} };
function addSwayShader(mat, amp){
  mat.onBeforeCompile = (sh)=>{
    sh.uniforms.uTime = swayUniforms.uTime; sh.uniforms.uWind = swayUniforms.uWind;
    sh.vertexShader = 'uniform float uTime; uniform float uWind;\n' + sh.vertexShader.replace(
      '#include <begin_vertex>',
      `#include <begin_vertex>
       #ifdef USE_INSTANCING
         vec3 ip = instanceMatrix[3].xyz;
       #else
         vec3 ip = vec3(0.0);
       #endif
       float sway = sin(uTime*1.7 + ip.x*2.1 + ip.z*1.3) * (0.25 + uWind*uWind*1.5)
                  + sin(uTime*3.3 + ip.z*3.7) * 0.15 * uWind;
       transformed.x += sway * transformed.y * ${amp.toFixed(2)};
       transformed.z += sway * transformed.y * ${(amp*0.6).toFixed(2)};`
    );
  };
  mat.customProgramCacheKey = ()=>'sway'+amp;
}

// Trees — CPU-swayed groups (few enough to animate directly)
const trees = [];
{
  const trunkMat = new THREE.MeshStandardMaterial({ color:0x7a5230, roughness:0.9 });
  const leafMat  = new THREE.MeshStandardMaterial({ color:0x3f8f3a, roughness:0.85, flatShading:true });
  const leafMat2 = new THREE.MeshStandardMaterial({ color:0x59a84a, roughness:0.85, flatShading:true });
  const trunkGeo = new THREE.CylinderGeometry(0.09, 0.14, 1.2, 6);
  const coneGeo  = new THREE.ConeGeometry(0.75, 1.15, 7);
  const ballGeo  = new THREE.IcosahedronGeometry(0.62, 0);
  const spots = [ [3.6,0.9],[4.6,2.4],[2.2,3.6],[-2.9,3.3],[-4.3,0.6],[-3.2,-2.6],[1.4,-4.0],[4.2,-1.6],[-1.2,-4.6] ];
  spots.forEach(([x,z],i)=>{
    const r = Math.hypot(x,z), g = new THREE.Group();
    g.position.set(x, islandY(r)-0.08, z);
    const trunk = new THREE.Mesh(trunkGeo, trunkMat); trunk.position.y = 0.6; trunk.castShadow=true;
    g.add(trunk);
    if(i%2===0){
      const c1 = new THREE.Mesh(coneGeo, leafMat); c1.position.y = 1.55; c1.castShadow=true;
      const c2 = new THREE.Mesh(coneGeo, leafMat2); c2.position.y = 2.15; c2.scale.setScalar(0.68); c2.castShadow=true;
      g.add(c1,c2);
    } else {
      const b = new THREE.Mesh(ballGeo, leafMat); b.position.y = 1.65; b.scale.set(1,0.9,1); b.castShadow=true;
      const b2 = new THREE.Mesh(ballGeo, leafMat2); b2.position.set(0.32,1.35,0.1); b2.scale.setScalar(0.6); b2.castShadow=true;
      g.add(b,b2);
    }
    g.scale.setScalar(0.8 + hash(i*13.7)*0.5);
    scene.add(g); trees.push({ g, phase: hash(i*7.3)*6.28 });
  });
}

// Shore + seabed rocks (instanced dodecahedra)
{
  const rockGeo = new THREE.DodecahedronGeometry(1, 0);
  const rockMat = new THREE.MeshStandardMaterial({ color:0x8d8779, roughness:0.95, flatShading:true });
  const rocks = new THREE.InstancedMesh(rockGeo, rockMat, 30);
  rocks.castShadow = rocks.receiveShadow = true;
  const mm = new THREE.Matrix4(), qq = new THREE.Quaternion(), ee = new THREE.Euler(), vv = new THREE.Vector3(), ss = new THREE.Vector3();
  for(let i=0;i<30;i++){
    const seabedRock = i>=20;
    const a = hash(i*3.1)*Math.PI*2;
    const r = seabedRock ? 8.5 + hash(i*5.7)*3.5 : SHORE_R - 0.4 + hash(i*2.3)*1.1;
    const y = seabedRock ? -2.35 : Math.max(islandY(r), -0.1);
    const sc = seabedRock ? 0.35+hash(i*9.2)*0.5 : 0.18+hash(i*4.4)*0.3;
    ee.set(hash(i)*3, hash(i*2)*3, hash(i*3)*3); qq.setFromEuler(ee);
    vv.set(Math.cos(a)*r, y, Math.sin(a)*r); ss.set(sc, sc*(0.6+hash(i*7)*0.5), sc);
    mm.compose(vv, qq, ss); rocks.setMatrixAt(i, mm);
  }
  scene.add(rocks);
}

// Grass tufts (instanced swaying blades)
{
  const bladeGeo = new THREE.PlaneGeometry(0.16, 0.5, 1, 2);
  bladeGeo.translate(0, 0.25, 0);
  const grassMat = new THREE.MeshStandardMaterial({ color:0x5da244, roughness:0.9, side:THREE.DoubleSide });
  addSwayShader(grassMat, 0.5);
  const tufts = new THREE.InstancedMesh(bladeGeo, grassMat, 260);
  const mm = new THREE.Matrix4(), qq = new THREE.Quaternion(), e = new THREE.Euler();
  for(let i=0;i<260;i++){
    const a = hash(i*1.7)*Math.PI*2;
    const r = 3.0 + hash(i*3.3)*2.9;
    const y = islandY(r) - 0.02;
    e.set(0, hash(i*9.1)*Math.PI, (hash(i*5.5)-0.5)*0.3); qq.setFromEuler(e);
    mm.compose(new THREE.Vector3(Math.cos(a)*r, y, Math.sin(a)*r), qq, new THREE.Vector3(1,0.6+hash(i*7.7)*0.9,1));
    tufts.setMatrixAt(i, mm);
  }
  scene.add(tufts);
}

// Kelp (instanced swaying strips underwater)
{
  const kelpGeo = new THREE.PlaneGeometry(0.22, 1.7, 1, 6);
  kelpGeo.translate(0, 0.85, 0);
  const kelpMat = new THREE.MeshStandardMaterial({ color:0x2f8f5e, roughness:0.8, side:THREE.DoubleSide, transparent:true, opacity:0.92 });
  addSwayShader(kelpMat, 0.45);
  const kelp = new THREE.InstancedMesh(kelpGeo, kelpMat, 46);
  const mm = new THREE.Matrix4(), qq = new THREE.Quaternion(), e = new THREE.Euler();
  for(let i=0;i<46;i++){
    const a = hash(i*2.9)*Math.PI*2, r = 8.0 + hash(i*6.1)*4.2;
    e.set(0, hash(i*4.4)*Math.PI, 0); qq.setFromEuler(e);
    mm.compose(new THREE.Vector3(Math.cos(a)*r, -2.42, Math.sin(a)*r), qq, new THREE.Vector3(1, 0.6+hash(i*8.8)*0.8, 1));
    kelp.setMatrixAt(i, mm);
  }
  scene.add(kelp);
}

// Bubbles (instanced, animated)
const BUBBLE_N = 70;
const bubbles = new THREE.InstancedMesh(
  new THREE.SphereGeometry(0.045, 6, 5),
  new THREE.MeshStandardMaterial({ color:0xdffcf8, transparent:true, opacity:0.55, roughness:0.1, metalness:0.2 }),
  BUBBLE_N
);
{
  const d = [];
  for(let i=0;i<BUBBLE_N;i++){
    const a = Math.random()*Math.PI*2, r = 7.6+Math.random()*4.6;
    d.push({ a, r, y:-2.3+Math.random()*2, sp:0.25+Math.random()*0.4, ph:Math.random()*6.28, sc:0.5+Math.random() });
  }
  bubbles.userData.d = d; scene.add(bubbles);
}

// Buoys (float with tide)
const buoys = [];
{
  const bMat = new THREE.MeshStandardMaterial({ color:0xe8543f, roughness:0.4 });
  const wMat = new THREE.MeshStandardMaterial({ color:0xf5f0e6, roughness:0.5 });
  for(const [x,z] of [[-8.5,5.5],[7.5,-8.0]]){
    const g = new THREE.Group();
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 10), bMat); s.castShadow=true;
    const band = new THREE.Mesh(new THREE.SphereGeometry(0.225, 12, 6), wMat); band.scale.y = 0.35;
    const nub = new THREE.Mesh(new THREE.ConeGeometry(0.05,0.2,6), wMat); nub.position.y = 0.3;
    g.add(s,band,nub); g.position.set(x,0,z); scene.add(g); buoys.push(g);
  }
}

/* ============================================================
   WILDLIFE — manta rays (undulating) + fish schools (instanced)
   ============================================================ */
function makeRayGeometry(){
  const U=16, V=22, pos=[], col=[], idx=[];
  const cTop=new THREE.Color(0x33445e), cBot=new THREE.Color(0xbfd0dc), c=new THREE.Color();
  for(let j=0;j<=V;j++){
    const v=-1+2*j/V;
    let w = 1.7*Math.pow(Math.max(0,1-v*v), 0.55);
    if(v<-0.55) w = Math.max(0.06, w*0.35);
    for(let i=0;i<=U;i++){
      const u=-1+2*i/U;
      const th = 0.15*Math.pow(Math.cos(u*Math.PI/2),1.2)*Math.pow(Math.max(0,1-v*v),0.4)+0.02;
      pos.push(u*w, th*(1-Math.abs(u)*0.7), v*1.9);
      c.copy(cTop).lerp(cBot, 0.25+0.55*Math.abs(u)); col.push(c.r,c.g,c.b);
    }
  }
  for(let j=0;j<V;j++) for(let i=0;i<U;i++){
    const a=j*(U+1)+i, b=a+1, d=a+U+1, e=d+1;
    idx.push(a,d,b, b,d,e);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  g.setIndex(idx); g.computeVertexNormals();
  g.userData.base = Float32Array.from(pos);
  return g;
}
const rayMat = new THREE.MeshStandardMaterial({ vertexColors:true, roughness:0.6, metalness:0.05, side:THREE.DoubleSide });
const rays = [];
{
  const eyeGeo = new THREE.SphereGeometry(0.05, 6, 6);
  const eyeMat = new THREE.MeshStandardMaterial({ color:0x0c1220 });
  for(let k=0;k<3;k++){
    const g = makeRayGeometry();
    const mesh = new THREE.Mesh(g, rayMat);
    mesh.castShadow = true;
    const grp = new THREE.Group(); grp.add(mesh);
    grp.add(new THREE.Mesh(eyeGeo, eyeMat).translateX(0.16).translateY(0.08).translateZ(1.75));
    const eye2 = new THREE.Mesh(eyeGeo, eyeMat); eye2.position.set(-0.16,0.08,1.75); grp.add(eye2);
    scene.add(grp);
    rays.push({
      grp, mesh, geo:g,
      a: k*2.1, radius: 8.2+k*0.9, yBase: -1.0-k*0.35, speed: 0.22+k*0.05,
      phase: k*2.4, jumping:false
    });
  }
}
function animateRayBody(ray, t){
  const p = ray.geo.attributes.position, base = ray.geo.userData.base;
  for(let i=0;i<p.count;i++){
    const bx=base[i*3], by=base[i*3+1], bz=base[i*3+2];
    const flap = Math.sin(t*3.4 + Math.abs(bx)*2.6 + ray.phase) * 0.17 * Math.pow(Math.abs(bx)/1.7, 1.6);
    const wag  = Math.sin(t*2.6 + bz*1.4 + ray.phase) * 0.10 * Math.max(0, (-bz-0.9)/2.9);
    p.setXYZ(i, bx+wag, by+flap, bz);
  }
  p.needsUpdate = true; ray.geo.computeVertexNormals();
}

// Fish schools
const schools = [];
{
  const fishGeo = new THREE.ConeGeometry(0.05, 0.22, 5);
  fishGeo.rotateX(Math.PI/2);
  const configs = [
    { n:26, color:0xf2b134, r:8.4, y:-0.9, sp:0.55 },
    { n:22, color:0x59c3e8, r:9.6, y:-1.6, sp:-0.42 },
    { n:18, color:0xef7f7f, r:7.8, y:-1.9, sp:0.65 },
  ];
  const mm = new THREE.Matrix4(), qq = new THREE.Quaternion(), e = new THREE.Euler();
  configs.forEach((cfg, si)=>{
    const mesh = new THREE.InstancedMesh(fishGeo, new THREE.MeshStandardMaterial({ color:cfg.color, roughness:0.55 }), cfg.n);
    scene.add(mesh);
    const members = [];
    for(let i=0;i<cfg.n;i++) members.push({ off: hash(i*3.7+si*100)*6.28, rad: (hash(i*7.1+si*57)-0.5)*1.6, yoff:(hash(i*11.3+si*31)-0.5)*0.8, ph:hash(i*5.9)*6.28 });
    schools.push({ mesh, cfg, members });
  });
}

/* ============================================================
   EFFECTS — ripples, splash droplets, ray jump
   ============================================================ */
const ripples = [];
{
  const rGeo = new THREE.RingGeometry(0.85, 1, 40);
  const rMat = new THREE.MeshBasicMaterial({ color:0xeafffa, transparent:true, opacity:0, side:THREE.DoubleSide, depthWrite:false });
  for(let i=0;i<7;i++){
    const r = new THREE.Mesh(rGeo, rMat.clone());
    r.rotation.x = -Math.PI/2; r.renderOrder = 6; r.visible = false;
    scene.add(r); ripples.push({ mesh:r, t:1, x:0, z:0 });
  }
}
function spawnRipple(x, z){
  const rp = ripples.find(r=>r.t>=1) || ripples[0];
  rp.t = 0; rp.x = x; rp.z = z; rp.mesh.visible = true;
}
// splash droplets (pooled Points)
const splash = { points:null, vel:[], life:0 };
{
  const N = 60, p = new Float32Array(N*3);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p,3));
  splash.points = new THREE.Points(g, new THREE.PointsMaterial({ color:0xcff5ef, size:0.09, transparent:true, opacity:0, depthWrite:false }));
  splash.points.renderOrder = 7; scene.add(splash.points);
  for(let i=0;i<N;i++) splash.vel.push(new THREE.Vector3());
}
function triggerSplash(x, y, z){
  const pos = splash.points.geometry.attributes.position;
  for(let i=0;i<pos.count;i++){
    pos.setXYZ(i, x+(Math.random()-0.5)*0.5, y+0.1, z+(Math.random()-0.5)*0.5);
    splash.vel[i].set((Math.random()-0.5)*2.6, 2.5+Math.random()*3.5, (Math.random()-0.5)*2.6);
  }
  pos.needsUpdate = true; splash.life = 1.2;
  splash.points.material.opacity = 1;
  spawnRipple(x,z); setTimeout(()=>spawnRipple(x,z), 180); setTimeout(()=>spawnRipple(x,z), 420);
  Audio.splash();
}
function startRayLeap(){
  if(S.rayJump) return;
  const ray = rays.find(r=>!r.jumping);
  if(!ray) return;
  ray.jumping = true;
  const p = ray.grp.position;
  const dir = new THREE.Vector3(p.x, 0, p.z).normalize().negate(); // jump toward island center-ish
  S.rayJump = { ray, t:0, dur:1.7, p0:p.clone(), dir, landed:false };
}

/* ============================================================
   AUDIO — procedural ambient music, waves, wind, splashes
   ============================================================ */
const Audio = {
  ctx:null, master:null, musicGain:null, waveGain:null, windGain:null,
  musicOn:false, started:false, _seq:null,
  init(){
    if(this.started) return; this.started = true;
    const C = window.AudioContext || window.webkitAudioContext;
    this.ctx = new C();
    this.master = this.ctx.createGain(); this.master.gain.value = 0.7; this.master.connect(this.ctx.destination);
    // --- music bus ---
    this.musicGain = this.ctx.createGain(); this.musicGain.gain.value = 0;
    const musicLP = this.ctx.createBiquadFilter(); musicLP.type='lowpass'; musicLP.frequency.value=1400;
    this.musicGain.connect(musicLP); musicLP.connect(this.master);
    // drones
    const droneFreqs=[110, 164.81];
    droneFreqs.forEach((f,i)=>{
      const o=this.ctx.createOscillator(); o.type='sine'; o.frequency.value=f;
      const g=this.ctx.createGain(); g.gain.value=0.11;
      const lfo=this.ctx.createOscillator(); lfo.frequency.value=0.07+i*0.03;
      const lg=this.ctx.createGain(); lg.gain.value=0.05;
      lfo.connect(lg); lg.connect(g.gain);
      o.connect(g); g.connect(this.musicGain); o.start(); lfo.start();
    });
    // gentle pentatonic arpeggio
    const notes=[329.63,392,440,493.88,587.33,659.25];
    let step=0;
    this._seq = setInterval(()=>{
      if(!this.musicOn || this.ctx.state!=='running') return;
      if(Math.random()<0.35) return;
      const t=this.ctx.currentTime, o=this.ctx.createOscillator(), g=this.ctx.createGain();
      o.type='triangle'; o.frequency.value=notes[(step + Math.floor(Math.random()*2))%notes.length] * (Math.random()<0.2?0.5:1);
      g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(0.09,t+0.05); g.gain.exponentialRampToValueAtTime(0.0001,t+2.4);
      o.connect(g); g.connect(this.musicGain); o.start(t); o.stop(t+2.5); step++;
    }, 850);
    // --- noise: waves + wind ---
    const len=this.ctx.sampleRate*2, buf=this.ctx.createBuffer(1,len,this.ctx.sampleRate), d=buf.getChannelData(0);
    for(let i=0;i<len;i++) d[i]=Math.random()*2-1;
    this.noiseBuf = buf;
    const mkNoise = (type,freq,q,gain)=>{
      const src=this.ctx.createBufferSource(); src.buffer=buf; src.loop=true;
      const f=this.ctx.createBiquadFilter(); f.type=type; f.frequency.value=freq; f.Q.value=q;
      const g=this.ctx.createGain(); g.gain.value=gain;
      src.connect(f); f.connect(g); g.connect(this.master); src.start();
      return {g,f};
    };
    const waves = mkNoise('lowpass', 420, 0.6, 0.05); this.waveGain = waves.g;
    const lfo=this.ctx.createOscillator(); lfo.frequency.value=0.13;
    const lg=this.ctx.createGain(); lg.gain.value=0.03; lfo.connect(lg); lg.connect(waves.g.gain); lfo.start();
    const lfo2=this.ctx.createOscillator(); lfo2.frequency.value=0.09;
    const lg2=this.ctx.createGain(); lg2.gain.value=180; lfo2.connect(lg2); lg2.connect(waves.f.frequency); lfo2.start();
    this.windGain = mkNoise('bandpass', 900, 0.8, 0.0).g;
  },
  setVolume(v){ if(this.master) this.master.gain.value = v; },
  setMusic(on){
    this.musicOn = on;
    if(!this.started && on) this.init();
    if(this.ctx.state==='suspended') this.ctx.resume();
    this.musicGain.gain.setTargetAtTime(on?0.9:0, this.ctx.currentTime, 0.5);
  },
  setWind(w){ if(this.windGain) this.windGain.gain.setTargetAtTime(w*w*0.05, this.ctx.currentTime, 0.4); },
  splash(){
    if(!this.ctx || this.ctx.state!=='running') return;
    const t=this.ctx.currentTime, src=this.ctx.createBufferSource(); src.buffer=this.noiseBuf;
    const f=this.ctx.createBiquadFilter(); f.type='bandpass'; f.Q.value=0.7;
    f.frequency.setValueAtTime(1800,t); f.frequency.exponentialRampToValueAtTime(200,t+0.7);
    const g=this.ctx.createGain(); g.gain.setValueAtTime(0.35,t); g.gain.exponentialRampToValueAtTime(0.001,t+0.8);
    src.connect(f); f.connect(g); g.connect(this.master); src.start(t); src.stop(t+0.9);
  }
};

/* ============================================================
   UI WIRING
   ============================================================ */
const $ = id => document.getElementById(id);
// collapsible panels
document.querySelectorAll('[data-collapse]').forEach(h=>{
  h.addEventListener('click', ()=> h.parentElement.classList.toggle('collapsed'));
});
if(innerWidth < 820) document.querySelectorAll('#worldPanel,#cameraPanel,#audioPanel').forEach(p=>p.classList.add('collapsed'));

// tide & wind
$('tide').addEventListener('input', e=>{ S.tide = parseFloat(e.target.value); updateWaterTide();
  $('tideVal').textContent = ((S.tide-0.5)*TIDE_RANGE).toFixed(1)+'m'; });
$('wind').addEventListener('input', e=>{ S.wind = parseFloat(e.target.value);
  $('windVal').textContent = Math.round(S.wind*100)+'%'; Audio.setWind(S.wind); });

// time of day
function setTOD(name){
  S.tod = name; Object.assign(tgt, TOD[name]);
  ['todDay','todSunset','todNight'].forEach(id=>$(id).classList.remove('active'));
  ({day:'todDay', sunset:'todSunset', night:'todNight'})[name] && $(({day:'todDay',sunset:'todSunset',night:'todNight'})[name]).classList.add('active');
}
$('todDay').onclick=()=>setTOD('day'); $('todSunset').onclick=()=>setTOD('sunset'); $('todNight').onclick=()=>setTOD('night');

// cameras
const CAMS = {
  iso:    { pos:[17,13,17],   tgt:[0,0.5,0] },
  cabin:  { pos:[7.6,4.4,6.8],tgt:[0.8,2.4,-0.4] },
  water:  { pos:[2.2,-1.5,10.8], tgt:[0,-1.3,0] },
};
function setCam(name, btn){
  const c = CAMS[name];
  S.camAnim = { t:0, dur:1.6,
    p0:camera.position.clone(), p1:new THREE.Vector3(...c.pos),
    t0:controls.target.clone(), t1:new THREE.Vector3(...c.tgt) };
  ['camIso','camCabin','camWater'].forEach(id=>$(id).classList.remove('active'));
  $(btn).classList.add('active');
}
$('camIso').onclick=()=>setCam('iso','camIso');
$('camCabin').onclick=()=>setCam('cabin','camCabin');
$('camWater').onclick=()=>setCam('water','camWater');

// actions
$('kayakBtn').onclick = ()=>{
  if(S.kayakState==='moored'){ S.kayakState='launching'; $('kayakBtn').textContent='🛶 Return Kayak'; }
  else if(S.kayakState==='out'){ S.kayakState='returning'; $('kayakBtn').textContent='🛶 Return Kayak'; }
};
$('rayBtn').onclick = ()=> startRayLeap();

// pause / reset
$('pauseBtn').onclick = ()=>{
  S.paused = !S.paused;
  $('pauseBtn').textContent = S.paused ? '▶ Resume' : '⏸ Pause';
  $('pauseBtn').classList.toggle('active', S.paused);
};
$('resetBtn').onclick = ()=>{
  S.tide=0.5; $('tide').value=0.5; $('tideVal').textContent='0.0m'; updateWaterTide();
  S.wind=0.35; $('wind').value=0.35; $('windVal').textContent='35%'; Audio.setWind(0.35);
  setTOD('day');
  S.kayakState='moored'; $('kayakBtn').textContent='🛶 Launch Kayak';
  S.rayJump=null; rays.forEach(r=>r.jumping=false);
  S.paused=false; $('pauseBtn').textContent='⏸ Pause'; $('pauseBtn').classList.remove('active');
  setCam('iso','camIso');
};

// quality
function applyQuality(q){
  S.quality = q;
  const pr = { low:1, med:1.5, high:2 }[q];
  renderer.setPixelRatio(Math.min(devicePixelRatio, pr));
  renderer.shadowMap.enabled = q!=='low';
  sun.shadow.mapSize.set(q==='high'?2048:1024, q==='high'?2048:1024);
  if(sun.shadow.map){ sun.shadow.map.dispose(); sun.shadow.map=null; }
  scene.traverse(o=>{ if(o.isMesh && o.material) (Array.isArray(o.material)?o.material:[o.material]).forEach(m=>m.needsUpdate=true); });
}
$('quality').onchange = e=>applyQuality(e.target.value);
applyQuality('med');

// audio
$('musicBtn').onclick = ()=>{
  const on = !Audio.musicOn;
  Audio.setMusic(on);
  $('musicBtn').textContent = on ? '♪ Music On' : '♪ Music Off';
  $('musicBtn').classList.toggle('active', on);
};
$('volume').addEventListener('input', e=>{ if(Audio.ctx) Audio.setVolume(parseFloat(e.target.value)); });
// audio must init on user gesture
const startAudio = ()=>{ Audio.init(); Audio.setVolume(parseFloat($('volume').value)); Audio.setWind(S.wind);
  renderer.domElement.removeEventListener('pointerdown', startAudio); };
renderer.domElement.addEventListener('pointerdown', startAudio);

/* ---------------- Resize ---------------- */
function onResize(){
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
}
addEventListener('resize', onResize); onResize();

/* ============================================================
   ANIMATION LOOP (delta-time based)
   ============================================================ */
const clock = new THREE.Clock();
const _v = new THREE.Vector3(), _q = new THREE.Quaternion(), _m = new THREE.Matrix4();
const KAYAK_HOME = new THREE.Vector3(10.6, 0, 1.5);

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const wdt = S.paused ? 0 : dt;
  S.worldTime += wdt;
  const t = S.worldTime;

  /* smooth wind + water uniforms */
  S.windSmooth += (S.wind - S.windSmooth) * Math.min(1, dt*3);
  waterUniforms.uTime.value = t;
  waterUniforms.uWind.value = 0.25 + S.windSmooth;
  swayUniforms.uTime.value = t;
  swayUniforms.uWind.value = S.windSmooth;

  /* time-of-day interpolation */
  const k = Math.min(1, dt*1.4);
  cur.skyTop.lerp(new THREE.Color(tgt.skyTop), k); cur.skyBot.lerp(new THREE.Color(tgt.skyBot), k);
  cur.fog.lerp(new THREE.Color(tgt.fog), k); cur.fogD += (tgt.fogD-cur.fogD)*k;
  cur.sunC.lerp(new THREE.Color(tgt.sunC), k); cur.sunI += (tgt.sunI-cur.sunI)*k;
  cur.sunP.lerp(new THREE.Vector3(...tgt.sunP), k);
  cur.hemiS.lerp(new THREE.Color(tgt.hemiS), k); cur.hemiG.lerp(new THREE.Color(tgt.hemiG), k);
  cur.hemiI += (tgt.hemiI-cur.hemiI)*k; cur.night += (tgt.night-cur.night)*k;
  cur.glow += (tgt.glow-cur.glow)*k; cur.exposure += (tgt.exposure-cur.exposure)*k;
  skyMat.uniforms.uTop.value.copy(cur.skyTop); skyMat.uniforms.uBot.value.copy(cur.skyBot);
  skyMat.uniforms.uSunDir.value.copy(cur.sunP).normalize(); skyMat.uniforms.uGlowAmt.value = cur.glow;
  scene.fog.color.copy(cur.fog); scene.fog.density = cur.fogD;
  sun.color.copy(cur.sunC); sun.intensity = cur.sunI; sun.position.copy(cur.sunP);
  hemi.color.copy(cur.hemiS); hemi.groundColor.copy(cur.hemiG); hemi.intensity = cur.hemiI;
  renderer.toneMappingExposure = cur.exposure;
  waterUniforms.uNight.value = cur.night;
  stars.material.opacity = cur.night * 0.9;
  // lanterns & windows glow at night
  const glowI = cur.night;
  glowMats.forEach(m=> m.emissiveIntensity = 0.15 + glowI*2.2);
  lampLights.forEach(L=> L.intensity = glowI*2.6);

  /* trees sway */
  trees.forEach(tr=>{
    tr.g.rotation.z = Math.sin(t*1.6 + tr.phase) * 0.035 * (0.2 + S.windSmooth*1.6);
    tr.g.rotation.x = Math.sin(t*1.2 + tr.phase*1.7) * 0.02 * (0.2 + S.windSmooth*1.6);
  });

  /* bubbles rise */
  {
    const d = bubbles.userData.d;
    for(let i=0;i<BUBBLE_N;i++){
      const b = d[i];
      b.y += wdt * b.sp;
      if(b.y > S.waterY-0.1){ b.y = -2.3; }
      const wob = Math.sin(t*2 + b.ph)*0.12;
      _m.makeScale(b.sc,b.sc,b.sc);
      _m.setPosition(Math.cos(b.a)*b.r + wob, b.y, Math.sin(b.a)*b.r + wob*0.7);
      bubbles.setMatrixAt(i, _m);
    }
    bubbles.needsMatrixUpdate = true;
    bubbles.visible = S.waterY > -1.5;
  }

  /* fish schools */
  schools.forEach(sch=>{
    const {cfg, members, mesh} = sch;
    for(let i=0;i<members.length;i++){
      const mb = members[i];
      const a = t*cfg.sp + mb.off;
      const r = cfg.r + mb.rad + Math.sin(t*0.6+mb.ph)*0.4;
      const x = Math.cos(a)*r, z = Math.sin(a)*r;
      const y = cfg.y + mb.yoff*0.4 + Math.sin(t*1.4+mb.ph)*0.15;
      const heading = Math.atan2(Math.cos(a)*cfg.sp, -Math.sin(a)*cfg.sp);
      _q.setFromEuler(new THREE.Euler(0, heading + Math.PI/2, Math.sin(t*6+mb.ph)*0.15));
      _m.compose(_v.set(x,y,z), _q, new THREE.Vector3(1,1,1));
      mesh.setMatrixAt(i, _m);
    }
    mesh.needsMatrixUpdate = true;
  });

  /* rays: swim or jump */
  rays.forEach(ray=>{
    if(ray.jumping && (!S.rayJump || S.rayJump.ray!==ray)){
      // idle circling while not jumping
      ray.a += wdt * ray.speed;
      const x = Math.cos(ray.a)*ray.radius, z = Math.sin(ray.a)*ray.radius;
      const y = ray.yBase + Math.sin(t*0.5+ray.phase)*0.45;
      ray.grp.position.set(x, Math.min(y, S.waterY-0.55), z);
      ray.grp.lookAt(x + Math.cos(ray.a+0.1)*ray.radius, y, z + Math.sin(ray.a+0.1)*ray.radius);
      ray.grp.rotateY(Math.PI/2);
      animateRayBody(ray, t);
    }
  });
  if(S.rayJump){
    const J = S.rayJump; J.t += wdt / J.dur;
    const p = Math.min(J.t, 1);
    const x = J.p0.x + J.dir.x * (p*5.2), z = J.p0.z + J.dir.z * (p*5.2);
    const y = -0.35 + 5.4 * p * (1-p) * 1.15;
    const prevY = -0.35 + 5.4 * Math.max(0,p-0.02) * (1-Math.max(0,p-0.02)) * 1.15;
    J.ray.grp.position.set(x, y, z);
    const yaw = Math.atan2(J.dir.z, J.dir.x);
    const pitch = Math.atan2(y - prevY, 0.02*5.4);
    _q.setFromEuler(new THREE.Euler(THREE.MathUtils.clamp(pitch,-0.9,0.9) * (p<0.5?1:-1) * -1 + (p<0.5?0:0), yaw+Math.PI/2, Math.sin(p*Math.PI*2)*0.4));
    // simple readable orientation: yaw toward dir, pitch arc, roll spin midair
    _q.setFromEuler(new THREE.Euler(
      (0.5-p)*2.4,                       // pitch: nose up then down
      yaw + Math.PI/2 + (p<0.5?0:Math.PI)*0 , // keep heading
      Math.sin(p*Math.PI*3)*0.35));
    J.ray.grp.quaternion.copy(_q);
    animateRayBody(J.ray, t*2.2);
    if(p > 0.5 && !J.landed && y < S.waterY){ J.landed = true; triggerSplash(x, S.waterY, z); }
    if(p >= 1){
      J.ray.jumping = false; S.rayJump = null;
      J.ray.a = Math.atan2(J.ray.grp.position.z, J.ray.grp.position.x);
    }
  }

  /* kayak trip */
  {
    const bob = Math.sin(t*1.8)*0.05 + waterSurf.position.y*0 + S.waterY;
    if(S.kayakState==='launching'){
      kayak.position.lerp(_v.set(Math.cos(S.kayakAngle)*9.5, 0, Math.sin(S.kayakAngle)*9.5), Math.min(1, dt*1.6));
      if(kayak.position.distanceTo(_v.set(Math.cos(S.kayakAngle)*9.5,0,Math.sin(S.kayakAngle)*9.5)) < 0.6) S.kayakState='out';
    }
    if(S.kayakState==='out'){
      S.kayakAngle += wdt*0.32;
      kayak.position.set(Math.cos(S.kayakAngle)*9.5, 0, Math.sin(S.kayakAngle)*9.5);
    }
    if(S.kayakState==='returning'){
      kayak.position.lerp(KAYAK_HOME, Math.min(1, dt*1.4));
      if(kayak.position.distanceTo(KAYAK_HOME) < 0.15){ S.kayakState='moored'; $('kayakBtn').textContent='🛶 Launch Kayak'; }
    }
    if(S.kayakState==='moored'){ kayak.position.lerp(KAYAK_HOME, Math.min(1,dt*2)); }
    kayak.position.y = S.waterY + 0.12 + Math.sin(t*1.8)*0.045;
    kayak.rotation.z = Math.sin(t*1.5)*0.05;
    kayak.rotation.y = (S.kayakState==='out'||S.kayakState==='launching') ? -S.kayakAngle + Math.PI/2 : 0.35;
    buoys.forEach((b,i)=>{ b.position.y = S.waterY + 0.02 + Math.sin(t*1.6+i*2.1)*0.05; b.rotation.z = Math.sin(t*1.2+i)*0.12; });
  }

  /* ripples & splash droplets */
  ripples.forEach(rp=>{
    if(rp.t < 1){
      rp.t += dt*0.9;
      const s = 0.4 + rp.t*4.2;
      rp.mesh.scale.set(s,s,s);
      rp.mesh.position.set(rp.x, S.waterY+0.02, rp.z);
      rp.mesh.material.opacity = (1-rp.t)*0.65;
      if(rp.t>=1) rp.mesh.visible=false;
    }
  });
  if(splash.life > 0){
    splash.life -= dt;
    const pos = splash.points.geometry.attributes.position;
    for(let i=0;i<pos.count;i++){
      const v = splash.vel[i]; v.y -= 9.5*dt;
      pos.setXYZ(i, pos.getX(i)+v.x*dt, pos.getY(i)+v.y*dt, pos.getZ(i)+v.z*dt);
      if(pos.getY(i) < S.waterY && v.y<0){ v.set(0,0,0); }
    }
    pos.needsUpdate = true;
    splash.points.material.opacity = Math.max(0, splash.life/1.2);
  }

  /* camera transition */
  if(S.camAnim){
    const A = S.camAnim; A.t += dt/A.dur;
    const p = THREE.MathUtils.smoothstep(Math.min(A.t,1), 0, 1);
    camera.position.lerpVectors(A.p0, A.p1, p);
    controls.target.lerpVectors(A.t0, A.t1, p);
    if(A.t >= 1) S.camAnim = null;
  }

  controls.update();
  renderer.render(scene, camera);
}

/* ---------------- Go ---------------- */
animate();
requestAnimationFrame(()=> setTimeout(()=> document.getElementById('loader').classList.add('gone'), 300));
</script>
</body>
</html>
```

## Highlights

**Cutaway water system** — three cooperating layers with explicit render ordering: opaque seabed/seabed-life first, a translucent aquarium **volume box** (`renderOrder 4`, `depthWrite:false`), then the shader-driven **surface** (`renderOrder 5`). This eliminates transparency flicker and keeps the cross-section readable from every angle, including the underwater camera inside the volume.

**Living water** — vertex-displaced waves scaled by the wind slider, a procedural foam band hugging the shoreline, animated caustics on the seabed shader, rising instanced bubbles, and tide-aware floating props (kayak, buoys, ripples, splashes all track the water plane).

**Rays** — parametric manta geometry with per-frame CPU vertex undulation (wing flap + tail wag), heading-locked swimming, and a full jump state machine: parabolic arc, pitch/roll, splash droplets (pooled `Points`), triple expanding ripples, and a procedural Web Audio splash.

**Performance** — `InstancedMesh` for planks, posts, rocks, grass, kelp, bubbles, and fish; shader-injected wind sway via `onBeforeCompile`; capped pixel ratio with Low/Med/High quality switching; delta-time everywhere.