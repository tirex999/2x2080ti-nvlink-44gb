

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>mc.html — voxel sandbox</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:100%; height:100%; overflow:hidden; }
  body { background:#87ceeb; font-family:"Segoe UI", system-ui, -apple-system, sans-serif; }
  canvas { display:block; }

  /* ---------- crosshair ---------- */
  #crosshair { position:fixed; left:50%; top:50%; width:20px; height:20px;
    transform:translate(-50%,-50%); pointer-events:none; z-index:5; mix-blend-mode:difference; }
  #crosshair::before, #crosshair::after { content:""; position:absolute; background:#fff; }
  #crosshair::before { left:9px; top:0; width:2px; height:20px; }
  #crosshair::after  { left:0;  top:9px; width:20px; height:2px; }

  /* ---------- stats ---------- */
  #stats { position:fixed; top:10px; left:12px; z-index:10; color:rgba(255,255,255,0.85);
    font-family:ui-monospace, Menlo, Consolas, monospace; font-size:12px; letter-spacing:0.04em;
    text-shadow:0 1px 2px rgba(0,0,0,0.7); pointer-events:none; }

  /* ---------- hud / hotbar ---------- */
  #hud { position:fixed; left:50%; bottom:14px; transform:translateX(-50%); z-index:10;
    text-align:center; pointer-events:none; }
  #selName { font-family:ui-monospace, Menlo, Consolas, monospace; font-size:11px;
    letter-spacing:0.3em; text-transform:uppercase; color:#fff;
    text-shadow:0 1px 3px rgba(0,0,0,0.8); margin-bottom:8px; }
  #hotbar { display:flex; gap:6px; padding:8px; background:rgba(10,16,24,0.55);
    border:1px solid rgba(255,255,255,0.14); border-radius:10px; }
  .slot { position:relative; width:48px; height:48px; border-radius:7px;
    border:2px solid rgba(255,255,255,0.22); background:rgba(255,255,255,0.05);
    display:flex; align-items:center; justify-content:center;
    transition:transform .12s ease, border-color .12s ease, box-shadow .12s ease; }
  .slot.selected { border-color:#fff; transform:translateY(-5px);
    box-shadow:0 0 14px rgba(255,255,255,0.45), inset 0 0 8px rgba(255,255,255,0.15); }
  .swatch { width:26px; height:26px; border-radius:4px;
    box-shadow:inset 0 3px 0 rgba(255,255,255,0.25), inset 0 -3px 0 rgba(0,0,0,0.28); }
  .num { position:absolute; top:2px; left:5px; font-size:10px; color:rgba(255,255,255,0.75);
    font-family:ui-monospace, Menlo, Consolas, monospace; }

  /* ---------- start overlay ---------- */
  #overlay { position:fixed; inset:0; z-index:20; display:flex; align-items:center; justify-content:center;
    cursor:pointer; user-select:none;
    background:
      radial-gradient(1100px 650px at 50% 15%, rgba(135,206,235,0.28), rgba(135,206,235,0) 60%),
      linear-gradient(180deg, rgba(14,24,34,0.70), rgba(7,13,20,0.90)); }
  #overlay.hidden { display:none; }
  .panel { text-align:center; color:#fff; padding:44px 56px; max-width:720px; }
  .panel h1 { font-family:ui-monospace, "Cascadia Mono", Menlo, Consolas, monospace;
    font-size:clamp(42px, 7vw, 74px); font-weight:800; letter-spacing:0.06em; line-height:1;
    text-shadow:0 5px 0 rgba(0,0,0,0.35), 0 14px 44px rgba(0,0,0,0.55); }
  .panel h1 .accent { color:#8be04a; }
  .sub { margin-top:12px; color:rgba(255,255,255,0.6); letter-spacing:0.3em;
    text-transform:uppercase; font-size:11px; }
  .controls { margin:36px auto 0; display:grid; grid-template-columns:auto auto;
    gap:11px 36px; font-size:13px; color:rgba(255,255,255,0.85); text-align:left; }
  .controls b { display:inline-block; min-width:96px; text-align:center;
    background:rgba(255,255,255,0.10); border:1px solid rgba(255,255,255,0.18);
    border-bottom-width:2px; border-radius:5px; padding:3px 8px; margin-right:10px;
    font-family:ui-monospace, Menlo, Consolas, monospace; font-size:11px; letter-spacing:0.04em;
    color:#d9f2c8; }
  .play { margin-top:40px; font-family:ui-monospace, Menlo, Consolas, monospace;
    font-size:15px; font-weight:700; letter-spacing:0.35em;
    animation:pulse 1.4s ease-in-out infinite; }
  @keyframes pulse {
    0%,100% { opacity:1; text-shadow:0 0 18px rgba(139,224,74,0.9); }
    50%     { opacity:0.4; text-shadow:none; }
  }
</style>
</head>
<body>
  <div id="stats"></div>
  <div id="crosshair"></div>
  <div id="hud">
    <div id="selName">Grass</div>
    <div id="hotbar"></div>
  </div>
  <div id="overlay">
    <div class="panel">
      <h1>VOXEL<span class="accent">CRAFT</span></h1>
      <div class="sub">a minecraft clone in one html file</div>
      <div class="controls">
        <div><b>W A S D</b>move</div>
        <div><b>SPACE</b>jump</div>
        <div><b>MOUSE</b>look around</div>
        <div><b>LEFT CLICK</b>break block</div>
        <div><b>RIGHT CLICK</b>place block</div>
        <div><b>1–7 / WHEEL</b>choose block</div>
        <div><b>ESC</b>release mouse</div>
      </div>
      <div class="play">CLICK TO PLAY</div>
    </div>
  </div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
'use strict';

/* ============================== constants ============================== */
var CHUNK = 16, HEIGHT = 80;
var GRAVITY = 25, JUMP_V = 8.5, WALK_SPEED = 5.5;
var P_HALF = 0.3, P_HEIGHT = 1.8, P_EYE = 1.62;
var REACH = 6, LOOK_SENS = 0.002;

var BLOCKS = {
  1:{name:'Grass',  color:0x4caf50},
  2:{name:'Dirt',   color:0x795548},
  3:{name:'Stone',  color:0x9e9e9e},
  4:{name:'Sand',   color:0xe7d9a8},
  5:{name:'Wood',   color:0x8d6e63},
  6:{name:'Leaves', color:0x2e7d32},
  7:{name:'Snow',   color:0xffffff}
};
var HOTBAR = [1,2,3,4,5,6,7];

var BLOCK_RGB = {};
(function(){
  for (var id in BLOCKS) {
    var c = new THREE.Color(BLOCKS[id].color);
    BLOCK_RGB[id] = [c.r, c.g, c.b];
  }
})();

/* ============================== dom refs ============================== */
var overlay   = document.getElementById('overlay');
var hotbarEl  = document.getElementById('hotbar');
var selNameEl = document.getElementById('selName');
var statsEl   = document.getElementById('stats');

/* ============================== noise ============================== */
function hash2(x, z){
  var n = Math.imul(x, 374761393) ^ Math.imul(z, 668265263);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
function hash3(x, y, z){
  var n = Math.imul(x, 374761393) ^ Math.imul(y, 2246822519) ^ Math.imul(z, 668265263);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
function treeHash(x, z){
  var n = Math.imul(x, 92837111) ^ Math.imul(z, 689287499);
  n = Math.imul(n ^ (n >>> 13), 3644798167);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
function smooth(t){ return t * t * (3 - 2 * t); }

function noise2(x, z){
  var xi = Math.floor(x), zi = Math.floor(z);
  var xf = x - xi, zf = z - zi;
  var a = hash2(xi, zi),     b = hash2(xi + 1, zi);
  var c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
  var u = smooth(xf), v = smooth(zf);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function fbm2(x, z){
  var sum = 0, amp = 1, freq = 1, norm = 0;
  for (var i = 0; i < 4; i++){
    sum += noise2(x * freq, z * freq) * amp;
    norm += amp; amp *= 0.5; freq *= 2;
  }
  return sum / norm;
}
function noise3(x, y, z){
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var xf = x - xi, yf = y - yi, zf = z - zi;
  var u = smooth(xf), v = smooth(yf), w = smooth(zf);
  var c000 = hash3(xi, yi, zi),     c100 = hash3(xi+1, yi, zi);
  var c010 = hash3(xi, yi+1, zi),   c110 = hash3(xi+1, yi+1, zi);
  var c001 = hash3(xi, yi, zi+1),   c101 = hash3(xi+1, yi, zi+1);
  var c011 = hash3(xi, yi+1, zi+1), c111 = hash3(xi+1, yi+1, zi+1);
  var x00 = c000 + (c100 - c000) * u, x10 = c010 + (c110 - c010) * u;
  var x01 = c001 + (c101 - c001) * u, x11 = c011 + (c111 - c011) * u;
  var y0 = x00 + (x10 - x00) * v, y1 = x01 + (x11 - x01) * v;
  return y0 + (y1 - y0) * w;
}
function fbm3(x, y, z){
  var sum = 0, amp = 1, freq = 1, norm = 0;
  for (var i = 0; i < 2; i++){
    sum += noise3(x * freq, y * freq, z * freq) * amp;
    norm += amp; amp *= 0.5; freq *= 2;
  }
  return sum / norm;
}

/* ============================== chunks ============================== */
var chunks = new Map();          // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
var chunkMeshes = [];            // every live chunk mesh, for raycasting

function getBlock(wx, wy, wz){
  if (wy < 0 || wy >= HEIGHT) return 0;
  var cx = Math.floor(wx / CHUNK), cz = Math.floor(wz / CHUNK);
  var c = chunks.get(cx + ',' + cz);
  if (!c) return 0;
  var lx = wx - cx * CHUNK, lz = wz - cz * CHUNK;
  return c.data[(wy * CHUNK + lz) * CHUNK + lx];
}
function setBlock(wx, wy, wz, id){
  if (wy < 0 || wy >= HEIGHT) return;
  var cx = Math.floor(wx / CHUNK), cz = Math.floor(wz / CHUNK);
  var c = chunks.get(cx + ',' + cz);
  if (!c) return;
  var lx = wx - cx * CHUNK, lz = wz - cz * CHUNK;
  c.data[(wy * CHUNK + lz) * CHUNK + lx] = id;
}

/* ============================== three.js setup ============================== */
var renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(60, 100, 40);
scene.add(sun);

var chunkMaterial = new THREE.MeshLambertMaterial({ vertexColors:true });

/* ============================== terrain generation ============================== */
function generateChunk(cx, cz){
  var key = cx + ',' + cz;
  if (chunks.has(key)) return;
  var data = new Uint8Array(HEIGHT * CHUNK * CHUNK);

  for (var lx = 0; lx < CHUNK; lx++){
    for (var lz = 0; lz < CHUNK; lz++){
      var wx = cx * CHUNK + lx, wz = cz * CHUNK + lz;
      var m = fbm2(wx * 0.004, wz * 0.004);
      var h = fbm2(wx * 0.02,  wz * 0.02);
      var H = Math.floor(5 + m * m * 58 + h * 10);
      var surf = (H >= 46) ? 7 : (H >= 37) ? 3 : (H <= 16) ? 4 : 1;
      var sub  = (H <= 16) ? 4 : (H >= 37) ? 3 : 2;
      var top = Math.min(H, HEIGHT - 1);
      for (var y = 0; y <= top; y++){
        var id;
        if (y === 0)        id = 3;
        else if (y < H - 3) id = 3;
        else if (y < H)     id = sub;
        else                id = surf;
        data[(y * CHUNK + lz) * CHUNK + lx] = id;
      }
      for (var cy = 3; cy <= H - 2; cy++){
        if (fbm3(wx * 0.09, cy * 0.09, wz * 0.09) > 0.67)
          data[(cy * CHUNK + lz) * CHUNK + lx] = 0;
      }
    }
  }

  /* trees: on grass, sparse, canopy kept inside the chunk */
  for (var tx = 2; tx < 14; tx++){
    for (var tz = 2; tz < 14; tz++){
      var twx = cx * CHUNK + tx, twz = cz * CHUNK + tz;
      var sy = -1;
      for (var yy = HEIGHT - 1; yy >= 0; yy--){
        if (data[(yy * CHUNK + tz) * CHUNK + tx] !== 0){ sy = yy; break; }
      }
      if (sy < 1 || sy > 68) continue;
      if (data[(sy * CHUNK + tz) * CHUNK + tx] !== 1) continue;   // grass only
      if (treeHash(twx, twz) >= 0.02) continue;
      for (var t = 1; t <= 4; t++){
        var ty = sy + t;
        if (ty >= HEIGHT) break;
        data[(ty * CHUNK + tz) * CHUNK + tx] = 5;                 // trunk
      }
      function leaf(x, y2, z2){
        if (y2 < 0 || y2 >= HEIGHT) return;
        var i = (y2 * CHUNK + z2) * CHUNK + x;
        if (data[i] === 0) data[i] = 6;
      }
      var ly, dx, dz;
      for (var L = 0; L < 2; L++){                                // 5x5 twice
        ly = sy + 4 + L;
        for (dx = -2; dx <= 2; dx++)
          for (dz = -2; dz <= 2; dz++)
            leaf(tx + dx, ly, tz + dz);
      }
      for (dx = -1; dx <= 1; dx++)                                // 3x3
        for (dz = -1; dz <= 1; dz++)
          leaf(tx + dx, sy + 6, tz + dz);
      leaf(tx, sy + 7, tz);                                       // tip
    }
  }

  chunks.set(key, { data:data, mesh:null });
}

/* ============================== meshing ============================== */
var FACES = [
  { dir:[-1, 0, 0], corners:[[0,1,0],[0,0,0],[0,1,1],[0,0,1]], shade:0.8  },
  { dir:[ 1, 0, 0], corners:[[1,1,1],[1,0,1],[1,1,0],[1,0,0]], shade:0.8  },
  { dir:[ 0,-1, 0], corners:[[1,0,1],[0,0,1],[1,0,0],[0,0,0]], shade:0.55 },
  { dir:[ 0, 1, 0], corners:[[0,1,1],[1,1,1],[0,1,0],[1,1,0]], shade:1.0  },
  { dir:[ 0, 0,-1], corners:[[1,0,0],[0,0,0],[1,1,0],[0,1,0]], shade:0.8  },
  { dir:[ 0, 0, 1], corners:[[0,0,1],[1,0,1],[0,1,1],[1,1,1]], shade:0.8  }
];

function removeMesh(c){
  scene.remove(c.mesh);
  c.mesh.geometry.dispose();
  var i = chunkMeshes.indexOf(c.mesh);
  if (i !== -1) chunkMeshes.splice(i, 1);
  c.mesh = null;
}

function buildMesh(cx, cz){
  var c = chunks.get(cx + ',' + cz);
  if (!c) return;
  if (c.mesh) removeMesh(c);

  var data = c.data;
  var bx = cx * CHUNK, bz = cz * CHUNK;
  var pos = [], nor = [], col = [], idx = [];

  function nbAt(nx, ny, nz){
    if (ny < 0 || ny >= HEIGHT) return 0;
    if (nx >= 0 && nx < CHUNK && nz >= 0 && nz < CHUNK)
      return data[(ny * CHUNK + nz) * CHUNK + nx];
    return getBlock(bx + nx, ny, bz + nz);
  }

  for (var y = 0; y < HEIGHT; y++){
    for (var lz = 0; lz < CHUNK; lz++){
      for (var lx = 0; lx < CHUNK; lx++){
        var id = data[(y * CHUNK + lz) * CHUNK + lx];
        if (id === 0) continue;
        var wx = bx + lx, wz = bz + lz;
        var rgb = BLOCK_RGB[id];
        for (var f = 0; f < 6; f++){
          var face = FACES[f];
          if (nbAt(lx + face.dir[0], y + face.dir[1], lz + face.dir[2]) !== 0) continue;
          var base = pos.length / 3;
          for (var k = 0; k < 4; k++){
            var cn = face.corners[k];
            pos.push(wx + cn[0], y + cn[1], wz + cn[2]);
            nor.push(face.dir[0], face.dir[1], face.dir[2]);
            col.push(rgb[0] * face.shade, rgb[1] * face.shade, rgb[2] * face.shade);
          }
          idx.push(base, base + 1, base + 2, base + 2, base + 1, base + 3);
        }
      }
    }
  }

  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('normal',   new THREE.Float32BufferAttribute(nor, 3));
  geo.setAttribute('color',    new THREE.Float32BufferAttribute(col, 3));
  geo.setIndex(idx);
  var mesh = new THREE.Mesh(geo, chunkMaterial);
  scene.add(mesh);
  chunkMeshes.push(mesh);
  c.mesh = mesh;
}

function rebuildChunk(cx, cz){
  var c = chunks.get(cx + ',' + cz);
  if (c && c.mesh) buildMesh(cx, cz);
}
function rebuildAround(wx, wy, wz){
  var cx = Math.floor(wx / CHUNK), cz = Math.floor(wz / CHUNK);
  var lx = wx - cx * CHUNK, lz = wz - cz * CHUNK;
  rebuildChunk(cx, cz);
  if (lx === 0)  rebuildChunk(cx - 1, cz);
  if (lx === 15) rebuildChunk(cx + 1, cz);
  if (lz === 0)  rebuildChunk(cx, cz - 1);
  if (lz === 15) rebuildChunk(cx, cz + 1);
}

/* ============================== streaming ============================== */
function byDistance(pcx, pcz, radius, fn){
  var list = [];
  for (var dx = -radius; dx <= radius; dx++)
    for (var dz = -radius; dz <= radius; dz++)
      list.push([dx * dx + dz * dz, pcx + dx, pcz + dz]);
  list.sort(function(a, b){ return a[0] - b[0]; });
  for (var i = 0; i < list.length; i++) fn(list[i][1], list[i][2]);
}

function updateWorld(){
  var pcx = Math.floor(player.pos.x / CHUNK);
  var pcz = Math.floor(player.pos.z / CHUNK);

  var gen = 0;
  byDistance(pcx, pcz, 5, function(cx, cz){
    if (gen >= 4) return;
    if (!chunks.has(cx + ',' + cz)){ generateChunk(cx, cz); gen++; }
  });

  var built = 0;
  byDistance(pcx, pcz, 4, function(cx, cz){
    if (built >= 2) return;
    var c = chunks.get(cx + ',' + cz);
    if (!c || c.mesh) return;
    if (!chunks.has((cx-1) + ',' + cz) || !chunks.has((cx+1) + ',' + cz) ||
        !chunks.has(cx + ',' + (cz-1)) || !chunks.has(cx + ',' + (cz+1))) return;
    buildMesh(cx, cz);
    built++;
  });

  var dead = [];
  chunks.forEach(function(c, key){
    var p = key.split(',');
    var dx = Math.abs(+p[0] - pcx), dz = Math.abs(+p[1] - pcz);
    if (dx > 7 || dz > 7) dead.push(key);
  });
  for (var i = 0; i < dead.length; i++){
    var cc = chunks.get(dead[i]);
    if (cc.mesh) removeMesh(cc);
    chunks.delete(dead[i]);
  }
}

/* ============================== player ============================== */
var player = {
  pos: new THREE.Vector3(),
  vel: new THREE.Vector3(),
  yaw: -0.6, pitch: -0.08,
  onGround: false
};
var keys = {};

function collides(px, py, pz){
  var x0 = Math.floor(px - P_HALF), x1 = Math.floor(px + P_HALF - 1e-7);
  var y0 = Math.floor(py),           y1 = Math.floor(py + P_HEIGHT - 1e-7);
  var z0 = Math.floor(pz - P_HALF), z1 = Math.floor(pz + P_HALF - 1e-7);
  for (var x = x0; x <= x1; x++)
    for (var y = y0; y <= y1; y++)
      for (var z = z0; z <= z1; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}

function isLocked(){ return document.pointerLockElement === renderer.domElement; }

function updatePlayer(dt){
  var f = 0, r = 0;
  if (isLocked()){
    if (keys['KeyW']) f += 1;
    if (keys['KeyS']) f -= 1;
    if (keys['KeyD']) r += 1;
    if (keys['KeyA']) r -= 1;
  }
  var len = Math.hypot(f, r);
  if (len > 0){ f /= len; r /= len; }
  var sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
  player.vel.x = (f * -sin + r * cos) * WALK_SPEED;
  player.vel.z = (f * -cos + r * -sin) * WALK_SPEED;

  player.vel.y -= GRAVITY * dt;
  if (player.vel.y < -50) player.vel.y = -50;
  if (isLocked() && keys['Space'] && player.onGround) player.vel.y = JUMP_V;

  var nx = player.pos.x + player.vel.x * dt;
  if (!collides(nx, player.pos.y, player.pos.z)) player.pos.x = nx;

  var ny = player.pos.y + player.vel.y * dt;
  if (!collides(player.pos.x, ny, player.pos.z)){
    player.pos.y = ny;
    player.onGround = false;
  } else {
    if (player.vel.y < 0) player.onGround = true;
    player.vel.y = 0;
  }

  var nz = player.pos.z + player.vel.z * dt;
  if (!collides(player.pos.x, player.pos.y, nz)) player.pos.z = nz;

  if (player.pos.y < -20){
    player.pos.copy(SPAWN);
    player.vel.set(0, 0, 0);
  }
}

/* ============================== break & place ============================== */
var raycaster = new THREE.Raycaster();
raycaster.far = REACH;
var screenCenter = new THREE.Vector2(0, 0);
var targetBlock = null;

var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.004, 1.004, 1.004)),
  new THREE.LineBasicMaterial({ color:0x000000 })
);
outline.visible = false;
scene.add(outline);

function updateTarget(){
  if (!isLocked()){
    targetBlock = null;
    outline.visible = false;
    return;
  }
  raycaster.setFromCamera(screenCenter, camera);
  var hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length > 0){
    var hit = hits[0];
    var p = hit.point, n = hit.face.normal;
    targetBlock = {
      x:  Math.floor(p.x - n.x * 0.5),
      y:  Math.floor(p.y - n.y * 0.5),
      z:  Math.floor(p.z - n.z * 0.5),
      px: Math.floor(p.x + n.x * 0.5),
      py: Math.floor(p.y + n.y * 0.5),
      pz: Math.floor(p.z + n.z * 0.5)
    };
    outline.position.set(targetBlock.x + 0.5, targetBlock.y + 0.5, targetBlock.z + 0.5);
    outline.visible = true;
  } else {
    targetBlock = null;
    outline.visible = false;
  }
}

function breakBlock(){
  if (!targetBlock) return;
  var x = targetBlock.x, y = targetBlock.y, z = targetBlock.z;
  if (y === 0) return;                       // bedrock
  if (getBlock(x, y, z) === 0) return;
  setBlock(x, y, z, 0);
  rebuildAround(x, y, z);
}

function placeBlock(){
  if (!targetBlock) return;
  var x = targetBlock.px, y = targetBlock.py, z = targetBlock.pz;
  if (y < 1 || y >= HEIGHT) return;
  if (getBlock(x, y, z) !== 0) return;
  var p = player.pos;
  if (x + 1 > p.x - P_HALF && x < p.x + P_HALF &&
      y + 1 > p.y &&             y < p.y + P_HEIGHT &&
      z + 1 > p.z - P_HALF && z < p.z + P_HALF) return;
  setBlock(x, y, z, HOTBAR[selected]);
  rebuildAround(x, y, z);
}

/* ============================== hotbar ============================== */
var selected = 0;
var slotEls = [];
HOTBAR.forEach(function(id, i){
  var s = document.createElement('div');
  s.className = 'slot' + (i === 0 ? ' selected' : '');
  var n = document.createElement('span');
  n.className = 'num';
  n.textContent = String(i + 1);
  var w = document.createElement('div');
  w.className = 'swatch';
  w.style.backgroundColor = '#' + BLOCKS[id].color.toString(16).padStart(6, '0');
  s.appendChild(n);
  s.appendChild(w);
  hotbarEl.appendChild(s);
  slotEls.push(s);
});
function selectSlot(i){
  selected = ((i % HOTBAR.length) + HOTBAR.length) % HOTBAR.length;
  for (var j = 0; j < slotEls.length; j++)
    slotEls[j].classList.toggle('selected', j === selected);
  selNameEl.textContent = BLOCKS[HOTBAR[selected]].name;
}

/* ============================== sky extras ============================== */
var cloudGroup = new THREE.Group();
var cloudMat = new THREE.MeshLambertMaterial({
  color:0xffffff, transparent:true, opacity:0.85, fog:false
});
for (var ci = 0; ci < 25; ci++){
  var cw = 10 + hash2(ci, 7)  * 20;
  var cd = 8  + hash2(ci, 13) * 16;
  var cm = new THREE.Mesh(new THREE.BoxGeometry(cw, 1.5, cd), cloudMat);
  var ang = hash2(ci, 29) * Math.PI * 2;
  var rad = 30 + hash2(ci, 41) * 250;
  cm.position.set(Math.cos(ang) * rad, 88 + hash2(ci, 53) * 8, Math.sin(ang) * rad);
  cm.userData.speed = 1.5 + hash2(ci, 67) * 2;
  cloudGroup.add(cm);
}
scene.add(cloudGroup);

var water = new THREE.Mesh(
  new THREE.PlaneGeometry(300, 300),
  new THREE.MeshLambertMaterial({
    color:0x2e6bd6, transparent:true, opacity:0.6, depthWrite:false
  })
);
water.rotation.x = -Math.PI / 2;
scene.add(water);

/* ============================== events ============================== */
window.addEventListener('keydown', function(e){
  keys[e.code] = true;
  if (e.code === 'Space') e.preventDefault();
  if (e.code >= 'Digit1' && e.code <= 'Digit7')
    selectSlot(parseInt(e.code.slice(5), 10) - 1);
});
window.addEventListener('keyup', function(e){ keys[e.code] = false; });
window.addEventListener('blur', function(){ for (var k in keys) keys[k] = false; });

window.addEventListener('wheel', function(e){
  e.preventDefault();
  selectSlot(selected + (e.deltaY > 0 ? 1 : -1));
}, { passive:false });

document.addEventListener('mousemove', function(e){
  if (!isLocked()) return;
  player.yaw   -= e.movementX * LOOK_SENS;
  player.pitch -= e.movementY * LOOK_SENS;
  var lim = Math.PI / 2 - 0.01;
  if (player.pitch >  lim) player.pitch =  lim;
  if (player.pitch < -lim) player.pitch = -lim;
});

document.addEventListener('mousedown', function(e){
  if (!isLocked()) return;
  if (e.button === 0) breakBlock();
  else if (e.button === 2) placeBlock();
});
document.addEventListener('contextmenu', function(e){ e.preventDefault(); });

overlay.addEventListener('click', function(){
  try {
    var p = renderer.domElement.requestPointerLock();
    if (p && p.catch) p.catch(function(){});
  } catch(err){}
});
document.addEventListener('pointerlockchange', function(){
  overlay.classList.toggle('hidden', isLocked());
});

window.addEventListener('resize', function(){
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ============================== init & main loop ============================== */
generateChunk(0, 0);
generateChunk(-1, 0); generateChunk(1, 0);
generateChunk(0, -1); generateChunk(0, 1);
buildMesh(0, 0);

var groundY = 0;
for (var gy = HEIGHT - 1; gy >= 0; gy--)
  if (getBlock(8, gy, 8) !== 0){ groundY = gy; break; }
var SPAWN = new THREE.Vector3(8.5, groundY + 1.02, 8.5);
player.pos.copy(SPAWN);

var lastT = performance.now();
var statTime = 0, statFrames = 0;

function animate(){
  requestAnimationFrame(animate);
  var now = performance.now();
  var dt = (now - lastT) / 1000;
  lastT = now;
  if (dt > 0.05) dt = 0.05;

  updateWorld();
  if (isLocked()) updatePlayer(dt);

  camera.position.set(player.pos.x, player.pos.y + P_EYE, player.pos.z);
  camera.rotation.set(player.pitch, player.yaw, 0);
  updateTarget();

  for (var i = 0; i < cloudGroup.children.length; i++){
    var c = cloudGroup.children[i];
    c.position.x += c.userData.speed * dt;
    if (c.position.x - player.pos.x >  300) c.position.x -= 600;
    else if (c.position.x - player.pos.x < -300) c.position.x += 600;
    if (c.position.z - player.pos.z >  300) c.position.z -= 600;
    else if (c.position.z - player.pos.z < -300) c.position.z += 600;
  }
  water.position.set(player.pos.x, 14.3, player.pos.z);

  statTime += dt; statFrames++;
  if (statTime >= 0.25){
    statsEl.textContent =
      'x ' + player.pos.x.toFixed(1) +
      '  y ' + player.pos.y.toFixed(1) +
      '  z ' + player.pos.z.toFixed(1) +
      '   \u00b7   ' + Math.round(statFrames / statTime) + ' fps';
    statTime = 0; statFrames = 0;
  }

  renderer.render(scene, camera);
}
animate();

})();
</script>
</body>
</html>
```