

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mc.html — voxel sandbox</title>
<style>
  html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; }
  canvas { display: block; }
  #crosshair {
    position: fixed; left: 50%; top: 50%; width: 18px; height: 18px;
    margin: -9px 0 0 -9px; pointer-events: none; z-index: 5;
  }
  #crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: rgba(255,255,255,0.85);
  }
  #crosshair::before { left: 8px; top: 0; width: 2px; height: 18px; }
  #crosshair::after  { left: 0; top: 8px; width: 18px; height: 2px; }
  #hotbar {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; padding: 5px; z-index: 5;
    background: rgba(0,0,0,0.45); border-radius: 6px;
  }
  .slot {
    width: 44px; height: 44px; border: 2px solid rgba(255,255,255,0.25);
    border-radius: 4px; display: flex; align-items: center; justify-content: center;
    color: #fff; font: bold 14px/1 monospace; text-shadow: 0 0 3px #000;
    box-shadow: inset 0 0 6px rgba(0,0,0,0.5);
  }
  .slot.sel { border-color: #ffffff; box-shadow: 0 0 8px rgba(255,255,255,0.9); }
  #overlay {
    position: fixed; inset: 0; z-index: 10;
    background: rgba(20, 24, 30, 0.75);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: #fff; font-family: monospace; text-align: center; cursor: pointer;
  }
  #overlay h1 { font-size: 42px; margin: 0 0 18px; letter-spacing: 4px; text-shadow: 3px 3px 0 #000; }
  #overlay p  { font-size: 15px; margin: 4px 0; color: #cfd8dc; }
  #overlay .play { margin-top: 26px; font-size: 20px; color: #ffeb3b; animation: pulse 1.2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>V O X E L C R A F T</h1>
  <p>W A S D — move &nbsp;&nbsp; SPACE — jump &nbsp;&nbsp; MOUSE — look</p>
  <p>LEFT CLICK — break block &nbsp;&nbsp; RIGHT CLICK — place block</p>
  <p>1–7 or MOUSE WHEEL — select block</p>
  <p class="play">▶ Click to play ◀</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
'use strict';

/* ============================== BLOCKS ============================== */
var BLOCK_IDS   = [0, 1, 2, 3, 4, 5, 6, 7];
var BLOCK_NAMES = ['air','grass','dirt','stone','sand','wood','leaves','snow'];
var BLOCK_HEX   = [0x000000, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
var BLOCK_COLOR = [];
for (var _bi = 0; _bi < 8; _bi++) BLOCK_COLOR[_bi] = new THREE.Color(BLOCK_HEX[_bi]);

var CHUNK = 16, HEIGHT = 80;

/* ============================ NOISE (deterministic) ============================ */
function hash2(x, z) {
  var h = (Math.imul(x, 374761393) + Math.imul(z, 668265263)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177) | 0;
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function hash3(x, y, z) {
  var h = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1274126177)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177) | 0;
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function sm(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
  var xi = Math.floor(x), zi = Math.floor(z);
  var tx = sm(x - xi), tz = sm(z - zi);
  var a = hash2(xi, zi),     b = hash2(xi + 1, zi);
  var c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
  return a + (b - a) * tx + (c - a) * tz + (a - b - c + d) * tx * tz;
}
function fbm2(x, z) {
  var v = 0, amp = 0.5, f = 1;
  for (var i = 0; i < 4; i++) { v += amp * noise2(x * f, z * f); f *= 2; amp *= 0.5; }
  return v;
}
function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var tx = sm(x - xi), ty = sm(y - yi), tz = sm(z - zi);
  var c000 = hash3(xi, yi, zi),       c100 = hash3(xi + 1, yi, zi);
  var c010 = hash3(xi, yi + 1, zi),   c110 = hash3(xi + 1, yi + 1, zi);
  var c001 = hash3(xi, yi, zi + 1),   c101 = hash3(xi + 1, yi, zi + 1);
  var c011 = hash3(xi, yi + 1, zi + 1), c111 = hash3(xi + 1, yi + 1, zi + 1);
  var x00 = c000 + (c100 - c000) * tx;
  var x10 = c010 + (c110 - c010) * tx;
  var x01 = c001 + (c101 - c001) * tx;
  var x11 = c011 + (c111 - c011) * tx;
  var y0 = x00 + (x10 - x00) * ty;
  var y1 = x01 + (x11 - x01) * ty;
  return y0 + (y1 - y0) * tz;
}
function fbm3(x, y, z) {
  var v = 0, amp = 0.5, f = 1;
  for (var i = 0; i < 4; i++) { v += amp * noise3(x * f, y * f, z * f); f *= 2; amp *= 0.5; }
  return v;
}

function terrainHeight(wx, wz) {
  var m = fbm2(wx * 0.004, wz * 0.004);
  var h = fbm2(wx * 0.02,  wz * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}

/* ============================== CHUNKS ============================== */
var chunks = new Map();   // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
var meshes = [];          // all live chunk meshes (raycast targets)
var mat = new THREE.MeshLambertMaterial({ vertexColors: true });

function chunkKey(cx, cz) { return cx + ',' + cz; }

function getBlock(x, y, z) {
  if (y < 0 || y >= HEIGHT) return 0;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var ch = chunks.get(chunkKey(cx, cz));
  if (!ch) return 0;
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  return ch.data[(y * CHUNK + lz) * CHUNK + lx];
}
function setBlock(x, y, z, id) {
  if (y < 0 || y >= HEIGHT) return;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var ch = chunks.get(chunkKey(cx, cz));
  if (!ch) return;
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  ch.data[(y * CHUNK + lz) * CHUNK + lx] = id;
  rebuildChunk(cx, cz);
  if (lx === 0)  rebuildChunk(cx - 1, cz);
  if (lx === 15) rebuildChunk(cx + 1, cz);
  if (lz === 0)  rebuildChunk(cx, cz - 1);
  if (lz === 15) rebuildChunk(cx, cz + 1);
}

/* ---------- terrain generation ---------- */
function generateChunk(cx, cz) {
  var data = new Uint8Array(CHUNK * HEIGHT * CHUNK);
  var ch = { data: data, mesh: null };
  chunks.set(chunkKey(cx, cz), ch);

  for (var lz = 0; lz < CHUNK; lz++) {
    for (var lx = 0; lx < CHUNK; lx++) {
      var wx = cx * CHUNK + lx, wz = cz * CHUNK + lz;
      var H = terrainHeight(wx, wz);
      var idx = function (y) { return (y * CHUNK + lz) * CHUNK + lx; };

      for (var y = 0; y <= H; y++) {
        var b;
        if (y === 0 || y < H - 3) {
          b = 3; // stone (y=0 unbreakable bedrock-ish stone)
        } else if (y < H) {
          b = (H <= 16) ? 4 : (H >= 37) ? 3 : 2; // sub-surface: sand / stone / dirt
        } else {
          b = (H >= 46) ? 7 : (H >= 37) ? 3 : (H <= 16) ? 4 : 1; // snow / stone / sand / grass
        }
        if (y >= 3 && y < H - 1) {
          if (fbm3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) b = 0; // cave
        }
        data[idx(y)] = b;
      }

      // trees
      if (H > 16 && H < 37 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 && H + 6 < HEIGHT &&
          hash2(wx, wz) < 0.02) {
        var put = function (ox, oy, oz, id) {
          var xx = lx + ox, yy = y + 0 + oy, zz = lz + oz;
          if (xx < 0 || xx >= CHUNK || zz < 0 || zz >= CHUNK || yy < 0 || yy >= HEIGHT) return;
          var i = (yy * CHUNK + zz) * CHUNK + xx;
          if (data[i] === 0) data[i] = id; // only into air
        };
        for (var dy = 1; dy <= 4; dy++) put(0, dy, 0, 5);            // trunk
        for (var dy2 = 3; dy2 <= 4; dy2++)                          // 5x5 twice
          for (var dx = -2; dx <= 2; dx++)
            for (var dz = -2; dz <= 2; dz++) put(dx, dy2, dz, 6);
        for (var dx2 = -1; dx2 <= 1; dx2++)                         // 3x3
          for (var dz2 = -1; dz2 <= 1; dz2++) put(dx2, 5, dz2, 6);
        put(0, 6, 0, 6);                                            // tip
      }
    }
  }
}

/* ---------- meshing ---------- */
var FACES = [
  { n: [ 1, 0, 0], c: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]], sh: 0.8 },
  { n: [-1, 0, 0], c: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]], sh: 0.8 },
  { n: [ 0, 1, 0], c: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]], sh: 1.0 },
  { n: [ 0,-1, 0], c: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], sh: 0.55 },
  { n: [ 0, 0, 1], c: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], sh: 0.8 },
  { n: [ 0, 0,-1], c: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]], sh: 0.8 }
];

function neighborsHaveData(cx, cz) {
  return chunks.has(chunkKey(cx + 1, cz)) && chunks.has(chunkKey(cx - 1, cz)) &&
         chunks.has(chunkKey(cx, cz + 1)) && chunks.has(chunkKey(cx, cz - 1));
}

function buildChunkMesh(cx, cz) {
  var ch = chunks.get(chunkKey(cx, cz));
  if (!ch || ch.mesh) return;
  var pos = [], nor = [], col = [], idx = [];
  var ox = cx * CHUNK, oz = cz * CHUNK;

  for (var ly = 0; ly < HEIGHT; ly++) {
    for (var lz = 0; lz < CHUNK; lz++) {
      for (var lx = 0; lx < CHUNK; lx++) {
        var id = ch.data[(ly * CHUNK + lz) * CHUNK + lx];
        if (id === 0) continue;
        var wx = ox + lx, wz = oz + lz;
        var bc = BLOCK_COLOR[id];
        for (var f = 0; f < 6; f++) {
          var F = FACES[f];
          if (getBlock(wx + F.n[0], ly + F.n[1], wz + F.n[2]) !== 0) continue;
          var base = pos.length / 3;
          for (var v = 0; v < 4; v++) {
            pos.push(wx + F.c[v][0], ly + F.c[v][1], wz + F.c[v][2]);
            nor.push(F.n[0], F.n[1], F.n[2]);
            col.push(bc.r * F.sh, bc.g * F.sh, bc.b * F.sh);
          }
          idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
        }
      }
    }
  }

  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('normal',   new THREE.Float32BufferAttribute(nor, 3));
  geo.setAttribute('color',    new THREE.Float32BufferAttribute(col, 3));
  geo.setIndex(idx);
  var mesh = new THREE.Mesh(geo, mat);
  mesh.userData.cx = cx; mesh.userData.cz = cz;
  scene.add(mesh);
  meshes.push(mesh);
  ch.mesh = mesh;
}

function rebuildChunk(cx, cz) {
  var ch = chunks.get(chunkKey(cx, cz));
  if (!ch) return;
  if (ch.mesh) {
    scene.remove(ch.mesh);
    var mi = meshes.indexOf(ch.mesh);
    if (mi !== -1) meshes.splice(mi, 1);
    ch.mesh.geometry.dispose();
    ch.mesh = null;
  }
  buildChunkMesh(cx, cz);
}

/* ---------- per-frame world streaming ---------- */
function updateWorld() {
  var pcx = Math.floor(player.pos.x / CHUNK), pcz = Math.floor(player.pos.z / CHUNK);

  var gen = 0;
  for (var dx = -5; dx <= 5 && gen < 4; dx++)
    for (var dz = -5; dz <= 5 && gen < 4; dz++) {
      var k = chunkKey(pcx + dx, pcz + dz);
      if (!chunks.has(k)) { generateChunk(pcx + dx, pcz + dz); gen++; }
    }

  var bld = 0;
  for (var bx = -4; bx <= 4 && bld < 2; bx++)
    for (var bz = -4; bz <= 4 && bld < 2; bz++) {
      var ccx = pcx + bx, ccz = pcz + bz;
      var c = chunks.get(chunkKey(ccx, ccz));
      if (c && !c.mesh && neighborsHaveData(ccx, ccz)) { buildChunkMesh(ccx, ccz); bld++; }
    }

  for (var key in chunks.keys()) {} // (Map iteration below)
  var toDelete = [];
  chunks.forEach(function (c, key) {
    var parts = key.split(',');
    var cx = parseInt(parts[0], 10), cz = parseInt(parts[1], 10);
    if (Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz)) > 7) toDelete.push(key);
  });
  for (var i = 0; i < toDelete.length; i++) {
    var c2 = chunks.get(toDelete[i]);
    if (c2.mesh) {
      scene.remove(c2.mesh);
      var mi2 = meshes.indexOf(c2.mesh);
      if (mi2 !== -1) meshes.splice(mi2, 1);
      c2.mesh.geometry.dispose();
    }
    chunks.delete(toDelete[i]);
  }
}

/* ============================== SCENE ============================== */
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

var renderer = new THREE.WebGLRenderer({ antialias: false });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(60, 120, 40);
scene.add(sun);

/* water */
var water = new THREE.Mesh(
  new THREE.PlaneGeometry(512, 512),
  new THREE.MeshLambertMaterial({ color: 0x3b6fd4, transparent: true, opacity: 0.55, depthWrite: false })
);
water.rotation.x = -Math.PI / 2;
water.position.y = 14.3;
scene.add(water);

/* clouds */
var cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
var clouds = [];
for (var ci = 0; ci < 25; ci++) {
  var cw = 8 + hash2(ci, 11) * 14, cd = 6 + hash2(ci, 23) * 10;
  var cm = new THREE.Mesh(new THREE.BoxGeometry(cw, 1.2, cd), cloudMat);
  cm.position.set((hash2(ci, 37) - 0.5) * 300, 88 + hash2(ci, 41) * 8, (hash2(ci, 53) - 0.5) * 300);
  cm.userData.speed = 1 + hash2(ci, 67) * 2;
  clouds.push(cm);
  scene.add(cm);
}

/* block outline */
var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01, 1.01, 1.01)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

/* ============================== PLAYER ============================== */
var player = {
  pos: new THREE.Vector3(8, 40, 8),
  vel: new THREE.Vector3(),
  yaw: 0, pitch: 0,
  onGround: false,
  hw: 0.3, height: 1.8, eye: 1.62
};
var SPAWN = new THREE.Vector3(8, 0, 8);

function respawn() {
  player.pos.set(SPAWN.x, terrainHeight(SPAWN.x, SPAWN.z) + 1, SPAWN.z);
  player.vel.set(0, 0, 0);
  player.onGround = false;
}

function collides(px, py, pz) {
  var x0 = Math.floor(px - player.hw), x1 = Math.floor(px + player.hw);
  var y0 = Math.floor(py),             y1 = Math.floor(py + player.height);
  var z0 = Math.floor(pz - player.hw), z1 = Math.floor(pz + player.hw);
  for (var x = x0; x <= x1; x++)
    for (var y = y0; y <= y1; y++)
      for (var z = z0; z <= z1; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}

var keys = {};
function updatePlayer(dt) {
  var fwd = (keys['KeyW'] ? 1 : 0) - (keys['KeyS'] ? 1 : 0);
  var str = (keys['KeyD'] ? 1 : 0) - (keys['KeyA'] ? 1 : 0);
  var len = Math.sqrt(fwd * fwd + str * str);
  var sx = 0, sz = 0;
  if (len > 0) {
    fwd /= len; str /= len;
    var sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
    sx = (-sin * fwd + cos * str) * 5.5;
    sz = (-cos * fwd - sin * str) * 5.5;
  }
  player.vel.x = sx;
  player.vel.z = sz;

  if (keys['Space'] && player.onGround) player.vel.y = 8.5;
  player.vel.y -= 25 * dt;
  if (player.vel.y < -20) player.vel.y = -20;

  // X
  var nx = player.pos.x + player.vel.x * dt;
  if (!collides(nx, player.pos.y, player.pos.z)) player.pos.x = nx;
  else player.vel.x = 0;
  // Z
  var nz = player.pos.z + player.vel.z * dt;
  if (!collides(player.pos.x, player.pos.y, nz)) player.pos.z = nz;
  else player.vel.z = 0;
  // Y
  var ny = player.pos.y + player.vel.y * dt;
  if (!collides(player.pos.x, ny, player.pos.z)) {
    player.pos.y = ny;
    player.onGround = false;
  } else {
    if (player.vel.y < 0) { player.onGround = true; player.pos.y = Math.ceil(ny); }
    player.vel.y = 0;
  }

  if (player.pos.y < -20) respawn();

  camera.position.set(player.pos.x, player.pos.y + player.eye, player.pos.z);
  camera.rotation.x = player.pitch;
  camera.rotation.y = player.yaw;
  camera.rotation.z = 0;
}

/* ============================== INPUT ============================== */
var overlay = document.getElementById('overlay');
var locked = false;

overlay.addEventListener('click', function () {
  renderer.domElement.requestPointerLock();
});
document.addEventListener('pointerlockchange', function () {
  locked = (document.pointerLockElement === renderer.domElement);
  overlay.style.display = locked ? 'none' : 'flex';
});
document.addEventListener('mousemove', function (e) {
  if (!locked) return;
  player.yaw   -= e.movementX * 0.002;
  player.pitch -= e.movementY * 0.002;
  var lim = 1.55;
  if (player.pitch >  lim) player.pitch =  lim;
  if (player.pitch < -lim) player.pitch = -lim;
});
document.addEventListener('keydown', function (e) {
  keys[e.code] = true;
  if (e.code >= 'Digit1' && e.code <= 'Digit7') selectSlot(parseInt(e.code.charAt(5), 10) - 1);
  if (e.code === 'Space') e.preventDefault();
});
document.addEventListener('keyup', function (e) { keys[e.code] = false; });
window.addEventListener('blur', function () { keys = {}; });
document.addEventListener('contextmenu', function (e) { e.preventDefault(); });

var selected = 0;
document.addEventListener('wheel', function (e) {
  selectSlot(selected + (e.deltaY > 0 ? 1 : -1));
}, { passive: true });

/* ============================== HOTBAR ============================== */
var HOTBAR = [1, 2, 3, 4, 5, 6, 7];
var hb = document.getElementById('hotbar');
HOTBAR.forEach(function (id, i) {
  var s = document.createElement('div');
  s.className = 'slot' + (i === 0 ? ' sel' : '');
  s.style.background = '#' + BLOCK_HEX[id].toString(16).padStart(6, '0');
  s.textContent = String(i + 1);
  hb.appendChild(s);
});
function selectSlot(i) {
  selected = ((i % 7) + 7) % 7;
  var kids = hb.children;
  for (var j = 0; j < kids.length; j++) kids[j].classList.toggle('sel', j === selected);
}

/* ============================== BREAK / PLACE ============================== */
var raycaster = new THREE.Raycaster();
raycaster.far = 6;
var center2 = new THREE.Vector2(0, 0);
var target = null; // {x,y,z} break target

function updateTarget() {
  target = null;
  if (!locked) { outline.visible = false; return; }
  raycaster.setFromCamera(center2, camera);
  var pcx = Math.floor(player.pos.x / CHUNK), pcz = Math.floor(player.pos.z / CHUNK);
  var near = [];
  for (var i = 0; i < meshes.length; i++) {
    var m = meshes[i];
    if (Math.abs(m.userData.cx - pcx) <= 1 && Math.abs(m.userData.cz - pcz) <= 1) near.push(m);
  }
  var hits = raycaster.intersectObjects(near, false);
  if (hits.length > 0) {
    var h = hits[0];
    var n = h.face.normal; // mesh at origin, no transform -> object space == world space
    var tx = Math.floor(h.point.x - n.x * 0.5);
    var ty = Math.floor(h.point.y - n.y * 0.5);
    var tz = Math.floor(h.point.z - n.z * 0.5);
    target = { x: tx, y: ty, z: tz,
               px: Math.floor(h.point.x + n.x * 0.5),
               py: Math.floor(h.point.y + n.y * 0.5),
               pz: Math.floor(h.point.z + n.z * 0.5) };
    outline.position.set(tx + 0.5, ty + 0.5, tz + 0.5);
    outline.visible = true;
  } else {
    outline.visible = false;
  }
}

function overlapsPlayer(bx, by, bz) {
  return bx < player.pos.x + player.hw && bx + 1 > player.pos.x - player.hw &&
         bz < player.pos.z + player.hw && bz + 1 > player.pos.z - player.hw &&
         by < player.pos.y + player.height && by + 1 > player.pos.y;
}

document.addEventListener('mousedown', function (e) {
  if (!locked) return;
  if (!target) return;
  if (e.button === 0) {
    if (target.y > 0) setBlock(target.x, target.y, target.z, 0); // y=0 unbreakable
  } else if (e.button === 2) {
    if (target.py >= 0 && target.py < HEIGHT &&
        getBlock(target.px, target.py, target.pz) === 0 &&
        !overlapsPlayer(target.px, target.py, target.pz)) {
      setBlock(target.px, target.py, target.pz, HOTBAR[selected]);
    }
  }
});

/* ============================== INIT & LOOP ============================== */
window.addEventListener('resize', function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// pre-generate around spawn so the player starts on solid ground
for (var ix = -2; ix <= 2; ix++)
  for (var iz = -2; iz <= 2; iz++)
    if (!chunks.has(chunkKey(ix, iz))) generateChunk(ix, iz);
for (var ix2 = -1; ix2 <= 1; ix2++)
  for (var iz2 = -1; iz2 <= 1; iz2++)
    buildChunkMesh(ix2, iz2);

respawn();

var lastT = performance.now();
function loop() {
  requestAnimationFrame(loop);
  var now = performance.now();
  var dt = (now - lastT) / 1000;
  lastT = now;
  if (dt > 0.05) dt = 0.05;

  updateWorld();
  updatePlayer(dt);
  updateTarget();

  water.position.x = player.pos.x;
  water.position.z = player.pos.z;

  for (var i = 0; i < clouds.length; i++) {
    var c = clouds[i];
    c.position.x += c.userData.speed * dt;
    if (c.position.x >  player.pos.x + 150) c.position.x = player.pos.x - 150;
    if (c.position.x <  player.pos.x - 150) c.position.x = player.pos.x + 150;
  }

  renderer.render(scene, camera);
}
loop();
</script>
</body>
</html>
```