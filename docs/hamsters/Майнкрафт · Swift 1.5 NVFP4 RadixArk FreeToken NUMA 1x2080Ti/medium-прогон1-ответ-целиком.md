

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>mc.html - Voxel Sandbox</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%; background: #000; font-family: 'Segoe UI', Arial, sans-serif; }
  canvas { display: block; }

  #overlay {
    position: fixed; inset: 0; z-index: 20;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: rgba(10, 20, 35, 0.82); color: #fff; cursor: pointer;
    text-align: center; user-select: none;
  }
  #overlay h1 {
    font-size: 56px; letter-spacing: 6px; margin: 0 0 18px 0;
    color: #8bc34a; text-shadow: 3px 3px 0 #1b3a1b, 6px 6px 0 rgba(0,0,0,0.4);
  }
  #overlay .controls {
    background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px; padding: 14px 26px; font-size: 15px; line-height: 1.9; text-align: left;
  }
  #overlay .play { margin-top: 26px; font-size: 22px; color: #ffd54f; animation: pulse 1.4s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.45; } }

  #crosshair {
    position: fixed; left: 50%; top: 50%; width: 20px; height: 20px;
    transform: translate(-50%, -50%); pointer-events: none; z-index: 10;
  }
  #crosshair::before, #crosshair::after { content: ''; position: absolute; background: rgba(255,255,255,0.9); }
  #crosshair::before { left: 9px; top: 0; width: 2px; height: 20px; }
  #crosshair::after  { top: 9px; left: 0; width: 20px; height: 2px; }

  #hotbar {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; padding: 6px; z-index: 10;
    background: rgba(0,0,0,0.55); border-radius: 6px;
  }
  .slot {
    width: 42px; height: 42px; border: 2px solid rgba(255,255,255,0.25);
    border-radius: 4px; position: relative; box-sizing: border-box;
  }
  .slot span {
    position: absolute; left: 3px; top: 1px; font-size: 11px; color: #fff;
    text-shadow: 1px 1px 1px #000; font-weight: bold;
  }
  .slot.sel { border: 3px solid #ffffff; }
</style>
</head>
<body>

<div id="overlay">
  <h1>VOXELCRAFT</h1>
  <div class="controls">
    <b>WASD</b> — move &nbsp;|&nbsp; <b>Space</b> — jump<br>
    <b>Mouse</b> — look around<br>
    <b>Left click</b> — break block &nbsp;|&nbsp; <b>Right click</b> — place block<br>
    <b>1–7 / Mouse wheel</b> — choose block in hotbar<br>
    <b>Esc</b> — release mouse
  </div>
  <div class="play">Click to play</div>
</div>

<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
'use strict';

/* ============================================================
   CONSTANTS
============================================================ */
var CHUNK = 16, HEIGHT = 80;
var WATER_LEVEL = 14.3;
var GRAVITY = 25, JUMP_V = 8.5, SPEED = 5.5;
var PLAYER_HALF = 0.3, PLAYER_H = 1.8, EYE = 1.62;
var REACH = 6;

var BLOCK_COLORS = {
  1: [0x4c/255, 0xaf/255, 0x50/255], // grass
  2: [0x79/255, 0x55/255, 0x48/255], // dirt
  3: [0x9e/255, 0x9e/255, 0x9e/255], // stone
  4: [0xe7/255, 0xd9/255, 0xa8/255], // sand
  5: [0x8d/255, 0x6e/255, 0x63/255], // wood
  6: [0x2e/255, 0x7d/255, 0x32/255], // leaves
  7: [1.0, 1.0, 1.0]                 // snow
};
var HOTBAR_IDS = [1, 2, 3, 4, 5, 6, 7];
var HOTBAR_CSS = ['#4caf50','#795548','#9e9e9e','#e7d9a8','#8d6e63','#2e7d32','#ffffff'];

/* Cube faces: normal, 4 corner offsets (CCW outward), shade. */
var FACES = [
  { n: [ 1, 0, 0], v: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]], shade: 0.8 },
  { n: [-1, 0, 0], v: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]], shade: 0.8 },
  { n: [ 0, 1, 0], v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]], shade: 1.0 },
  { n: [ 0,-1, 0], v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], shade: 0.55 },
  { n: [ 0, 0, 1], v: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], shade: 0.8 },
  { n: [ 0, 0,-1], v: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]], shade: 0.8 }
];
var TRI = [0, 1, 2, 0, 2, 3];

/* ============================================================
   DETERMINISTIC VALUE NOISE
============================================================ */
function hash2(x, z) {
  var h = Math.imul(x | 0, 0x27d4eb2d) ^ Math.imul(z | 0, 0x165667b1) ^ 0x9e3779b9;
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function hash3(x, y, z) {
  var h = Math.imul(x | 0, 0x27d4eb2d) ^ Math.imul(y | 0, 0x1b873593) ^
          Math.imul(z | 0, 0x165667b1) ^ 0x9e3779b9;
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function smooth(t) { return t * t * (3 - 2 * t); }
function lerp(a, b, t) { return a + (b - a) * t; }

function noise2(x, z) {
  var xi = Math.floor(x), zi = Math.floor(z);
  var u = smooth(x - xi), v = smooth(z - zi);
  var a = hash2(xi, zi),     b = hash2(xi + 1, zi);
  var c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}
function fractal2(x, z) {
  var v = 0, amp = 1, f = 1, tot = 0;
  for (var i = 0; i < 4; i++) {
    v += amp * noise2(x * f, z * f);
    tot += amp; amp *= 0.5; f *= 2;
  }
  return v / tot;
}
function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var u = smooth(x - xi), v = smooth(y - yi), w = smooth(z - zi);
  var c000 = hash3(xi, yi, zi),     c100 = hash3(xi + 1, yi, zi);
  var c010 = hash3(xi, yi + 1, zi), c110 = hash3(xi + 1, yi + 1, zi);
  var c001 = hash3(xi, yi, zi + 1),     c101 = hash3(xi + 1, yi, zi + 1);
  var c011 = hash3(xi, yi + 1, zi + 1), c111 = hash3(xi + 1, yi + 1, zi + 1);
  var x00 = lerp(c000, c100, u), x10 = lerp(c010, c110, u);
  var x01 = lerp(c001, c101, u), x11 = lerp(c011, c111, u);
  return lerp(lerp(x00, x10, v), lerp(x01, x11, v), w);
}
function fractal3(x, y, z) {
  var v = 0, amp = 1, f = 1, tot = 0;
  for (var i = 0; i < 4; i++) {
    v += amp * noise3(x * f, y * f, z * f);
    tot += amp; amp *= 0.5; f *= 2;
  }
  return v / tot;
}

function heightAt(wx, wz) {
  var m = fractal2(wx * 0.004, wz * 0.004);
  var h = fractal2(wx * 0.02, wz * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}

/* ============================================================
   CHUNK STORAGE + GLOBAL BLOCK READ / WRITE
============================================================ */
var chunks = new Map();   // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null, built: bool }
var meshList = [];        // all chunk meshes, for raycasting

function idx(lx, y, lz) { return lx + 16 * (lz + 16 * y); }

function getBlock(x, y, z) {
  if (y < 0 || y >= HEIGHT) return 0;
  var cx = Math.floor(x / 16), cz = Math.floor(z / 16);
  var ch = chunks.get(cx + ',' + cz);
  if (!ch) return 0;
  return ch.data[idx(x - cx * 16, y, z - cz * 16)];
}
function setBlock(x, y, z, id) {
  if (y < 0 || y >= HEIGHT) return;
  var cx = Math.floor(x / 16), cz = Math.floor(z / 16);
  var ch = chunks.get(cx + ',' + cz);
  if (!ch) return;
  ch.data[idx(x - cx * 16, y, z - cz * 16)] = id;
}

/* ============================================================
   TERRAIN GENERATION
============================================================ */
function genChunk(cx, cz) {
  var key = cx + ',' + cz;
  if (chunks.has(key)) return;
  var data = new Uint8Array(CHUNK * HEIGHT * CHUNK);

  for (var x = 0; x < 16; x++) {
    for (var z = 0; z < 16; z++) {
      var wx = cx * 16 + x, wz = cz * 16 + z;
      var H = heightAt(wx, wz);
      if (H < 1) H = 1;
      if (H > HEIGHT - 9) H = HEIGHT - 9;

      /* column fill */
      for (var y = 0; y <= H; y++) {
        var id;
        if (y === H) {
          id = (H >= 46) ? 7 : (H >= 37) ? 3 : (H <= 16) ? 4 : 1;
        } else if (y >= H - 3) {
          id = (H <= 16) ? 4 : (H >= 37) ? 3 : 2;
        } else {
          id = 3;
        }
        data[idx(x, y, z)] = id;
      }

      /* caves */
      for (var cy = 3; cy <= H - 2; cy++) {
        if (fractal3(wx * 0.09, cy * 0.09, wz * 0.09) > 0.67) {
          data[idx(x, cy, z)] = 0;
        }
      }
      /* y = 0 is unbreakable bedrock stone */
      data[idx(x, 0, z)] = 3;

      /* trees (only fully inside this chunk) */
      if (H > 16 && H < 37 && x >= 2 && x <= 13 && z >= 2 && z <= 13 &&
          H + 8 < HEIGHT && hash2(wx + 911, wz + 131) < 0.02) {
        var i;
        for (i = 1; i <= 4; i++) data[idx(x, H + i, z)] = 5;         // trunk
        for (var ly = H + 5; ly <= H + 6; ly++) {                    // 5x5 x2
          for (var ox = -2; ox <= 2; ox++) for (var oz = -2; oz <= 2; oz++) {
            var j1 = idx(x + ox, ly, z + oz);
            if (data[j1] === 0) data[j1] = 6;
          }
        }
        for (var ox2 = -1; ox2 <= 1; ox2++) for (var oz2 = -1; oz2 <= 1; oz2++) { // 3x3
          var j2 = idx(x + ox2, H + 7, z + oz2);
          if (data[j2] === 0) data[j2] = 6;
        }
        var j3 = idx(x, H + 8, z);                                    // cap
        if (data[j3] === 0) data[j3] = 6;
      }
    }
  }
  chunks.set(key, { data: data, mesh: null, built: false });
}

/* ============================================================
   SCENE SETUP
============================================================ */
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);
var canvas = renderer.domElement;

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.4, 0.8, 0.3);
scene.add(sun);

var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

/* Water: visual-only plane re-centered on player each frame */
var water = new THREE.Mesh(
  new THREE.PlaneGeometry(800, 800),
  new THREE.MeshLambertMaterial({ color: 0x3d7ed6, transparent: true, opacity: 0.55, depthWrite: false })
);
water.rotation.x = -Math.PI / 2;
water.renderOrder = 2;
scene.add(water);

/* Clouds: 25 flat drifting boxes at height ~90 */
var clouds = [];
var cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
for (var ci = 0; ci < 25; ci++) {
  var cw = 15 + Math.random() * 30, cd = 15 + Math.random() * 30;
  var cloud = new THREE.Mesh(new THREE.BoxGeometry(cw, 2, cd), cloudMat);
  cloud.position.set((Math.random() - 0.5) * 480, 90, (Math.random() - 0.5) * 480);
  scene.add(cloud);
  clouds.push(cloud);
}

/* Block outline (targeted block) */
var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

/* ============================================================
   MESHING — one BufferGeometry per chunk, world-space vertices
============================================================ */
function buildMesh(cx, cz) {
  var key = cx + ',' + cz;
  var ch = chunks.get(key);
  if (!ch || ch.built) return;

  var d = ch.data;
  var px = [], pn = [], pc = [];

  for (var y = 0; y < HEIGHT; y++) {
    for (var z = 0; z < 16; z++) {
      for (var x = 0; x < 16; x++) {
        var id = d[idx(x, y, z)];
        if (id === 0) continue;
        var wx = cx * 16 + x, wz = cz * 16 + z;
        var col = BLOCK_COLORS[id];
        for (var f = 0; f < 6; f++) {
          var F = FACES[f];
          if (getBlock(wx + F.n[0], y + F.n[1], wz + F.n[2]) !== 0) continue;
          for (var t = 0; t < 6; t++) {
            var v = F.v[TRI[t]];
            px.push(wx + v[0], y + v[1], wz + v[2]);
            pn.push(F.n[0], F.n[1], F.n[2]);
            pc.push(col[0] * F.shade, col[1] * F.shade, col[2] * F.shade);
          }
        }
      }
    }
  }

  ch.built = true;
  if (px.length === 0) return;

  var g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(px, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(pn, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(pc, 3));
  var mesh = new THREE.Mesh(g, blockMaterial);
  scene.add(mesh);
  meshList.push(mesh);
  ch.mesh = mesh;
}

function dropMesh(ch) {
  if (ch.mesh) {
    scene.remove(ch.mesh);
    ch.mesh.geometry.dispose();
    var i = meshList.indexOf(ch.mesh);
    if (i >= 0) meshList.splice(i, 1);
    ch.mesh = null;
  }
}

function rebuildChunk(cx, cz) {
  var ch = chunks.get(cx + ',' + cz);
  if (!ch || !ch.built) return;
  dropMesh(ch);
  ch.built = false;
  buildMesh(cx, cz);
}

/* ============================================================
   CHUNK STREAMING
============================================================ */
function updateChunks(pcx, pcz) {
  /* unload far chunks */
  chunks.forEach(function (ch, key) {
    var parts = key.split(',');
    var cx = +parts[0], cz = +parts[1];
    if (Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz)) > 7) {
      dropMesh(ch);
      chunks.delete(key);
    }
  });

  /* generate data: within 5, max 4 per frame, nearest rings first */
  var gen = 0;
  for (var r = 0; r <= 5 && gen < 4; r++) {
    for (var dx = -r; dx <= r && gen < 4; dx++) {
      for (var dz = -r; dz <= r && gen < 4; dz++) {
        if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;
        var key = (pcx + dx) + ',' + (pcz + dz);
        if (!chunks.has(key)) { genChunk(pcx + dx, pcz + dz); gen++; }
      }
    }
  }

  /* build meshes: within 4, all 4 neighbors have data, max 2 per frame */
  var built = 0;
  for (var mx = -4; mx <= 4 && built < 2; mx++) {
    for (var mz = -4; mz <= 4 && built < 2; mz++) {
      var cx2 = pcx + mx, cz2 = pcz + mz;
      var ch2 = chunks.get(cx2 + ',' + cz2);
      if (!ch2 || ch2.built) continue;
      if (chunks.has((cx2 + 1) + ',' + cz2) && chunks.has((cx2 - 1) + ',' + cz2) &&
          chunks.has(cx2 + ',' + (cz2 + 1)) && chunks.has(cx2 + ',' + (cz2 - 1))) {
        buildMesh(cx2, cz2);
        built++;
      }
    }
  }
}

/* ============================================================
   PLAYER STATE + INPUT
============================================================ */
var pos = new THREE.Vector3(8.5, 40, 8.5);  // feet position
var vy = 0, onGround = false;
var yaw = 0.6, pitch = -0.15;
var locked = false;
var keys = {};
var selected = 0;

function respawn() {
  pos.set(8.5, heightAt(8, 8) + 1, 8.5);
  vy = 0;
  onGround = false;
}

/* initial world data around spawn (synchronous so player has ground) */
for (var gx = -5; gx <= 5; gx++) for (var gz = -5; gz <= 5; gz++) genChunk(gx, gz);
respawn();

var overlay = document.getElementById('overlay');
overlay.addEventListener('click', function () {
  canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', function () {
  locked = (document.pointerLockElement === canvas);
  overlay.style.display = locked ? 'none' : 'flex';
});
document.addEventListener('mousemove', function (e) {
  if (!locked) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  var lim = Math.PI / 2 - 0.01;
  pitch = Math.max(-lim, Math.min(lim, pitch));
});
document.addEventListener('contextmenu', function (e) { e.preventDefault(); });

document.addEventListener('keydown', function (e) {
  keys[e.code] = true;
  if (e.code === 'Space' && locked) e.preventDefault();
  if (e.code.indexOf('Digit') === 0) {
    var n = +e.code.substring(5);
    if (n >= 1 && n <= 7) { selected = n - 1; updateHotbar(); }
  }
});
document.addEventListener('keyup', function (e) { keys[e.code] = false; });
document.addEventListener('wheel', function (e) {
  if (!locked) return;
  selected = (selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
  updateHotbar();
});

/* ============================================================
   PHYSICS — axis-separated collision
============================================================ */
function collides() {
  var minX = Math.floor(pos.x - PLAYER_HALF), maxX = Math.floor(pos.x + PLAYER_HALF);
  var minY = Math.floor(pos.y),               maxY = Math.floor(pos.y + PLAYER_H);
  var minZ = Math.floor(pos.z - PLAYER_HALF), maxZ = Math.floor(pos.z + PLAYER_HALF);
  for (var x = minX; x <= maxX; x++)
    for (var y = minY; y <= maxY; y++)
      for (var z = minZ; z <= maxZ; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}

function physics(dt) {
  /* horizontal input relative to yaw */
  var fwd = (keys['KeyW'] ? 1 : 0) - (keys['KeyS'] ? 1 : 0);
  var str = (keys['KeyD'] ? 1 : 0) - (keys['KeyA'] ? 1 : 0);
  var len = Math.hypot(fwd, str) || 1;
  var vx = (-Math.sin(yaw) * fwd + Math.cos(yaw) * str) / len * SPEED;
  var vz = (-Math.cos(yaw) * fwd - Math.sin(yaw) * str) / len * SPEED;

  if (keys['Space'] && onGround) { vy = JUMP_V; onGround = false; }
  vy -= GRAVITY * dt;
  if (vy < -50) vy = -50;

  var old;

  old = pos.x; pos.x += vx * dt;
  if (collides()) pos.x = old;

  old = pos.z; pos.z += vz * dt;
  if (collides()) pos.z = old;

  old = pos.y; pos.y += vy * dt;
  if (collides()) {
    pos.y = old;
    if (vy < 0) onGround = true;
    vy = 0;
  } else {
    onGround = false;
  }

  if (pos.y < -20) respawn();

  camera.position.set(pos.x, pos.y + EYE, pos.z);
  camera.rotation.y = yaw;
  camera.rotation.x = pitch;
}

/* ============================================================
   BREAK / PLACE
============================================================ */
var raycaster = new THREE.Raycaster();
raycaster.far = REACH;
var center = new THREE.Vector2(0, 0);
var target = null;   // { b:{x,y,z} break cell, c:{x,y,z} place cell }

function updateTarget() {
  raycaster.setFromCamera(center, camera);
  var hits = raycaster.intersectObjects(meshList);
  target = null;
  for (var i = 0; i < hits.length; i++) {
    var h = hits[i];
    if (h.distance > REACH) break;
    var p = h.point, n = h.face.normal;
    target = {
      b: { x: Math.floor(p.x - n.x * 0.5), y: Math.floor(p.y - n.y * 0.5), z: Math.floor(p.z - n.z * 0.5) },
      c: { x: Math.floor(p.x + n.x * 0.5), y: Math.floor(p.y + n.y * 0.5), z: Math.floor(p.z + n.z * 0.5) }
    };
    outline.position.set(target.b.x + 0.5, target.b.y + 0.5, target.b.z + 0.5);
    outline.visible = locked;
    break;
  }
  if (!target) outline.visible = false;
}

function overlapsPlayer(bx, by, bz) {
  return (bx + 1 > pos.x - PLAYER_HALF && bx < pos.x + PLAYER_HALF &&
          by + 1 > pos.y && by < pos.y + PLAYER_H &&
          bz + 1 > pos.z - PLAYER_HALF && bz < pos.z + PLAYER_HALF);
}

function editBlock(wx, wy, wz, id) {
  setBlock(wx, wy, wz, id);
  var cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
  rebuildChunk(cx, cz);
  var lx = wx - cx * 16, lz = wz - cz * 16;
  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === 15) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === 15) rebuildChunk(cx, cz + 1);
}

document.addEventListener('mousedown', function (e) {
  if (!locked || !target) return;
  if (e.button === 0) {
    /* break (y 0 is unbreakable) */
    if (target.b.y > 0) editBlock(target.b.x, target.b.y, target.b.z, 0);
  } else if (e.button === 2) {
    /* place selected block */
    var c = target.c;
    if (c.y >= 0 && c.y < HEIGHT &&
        getBlock(c.x, c.y, c.z) === 0 &&
        !overlapsPlayer(c.x, c.y, c.z)) {
      editBlock(c.x, c.y, c.z, HOTBAR_IDS[selected]);
    }
  }
});

/* ============================================================
   HOTBAR UI
============================================================ */
var hotbarEl = document.getElementById('hotbar');
var slotEls = [];
(function buildHotbar() {
  for (var i = 0; i < 7; i++) {
    var s = document.createElement('div');
    s.className = 'slot';
    s.style.background = HOTBAR_CSS[i];
    var label = document.createElement('span');
    label.textContent = (i + 1);
    s.appendChild(label);
    hotbarEl.appendChild(s);
    slotEls.push(s);
  }
  updateHotbar();
})();
function updateHotbar() {
  for (var i = 0; i < 7; i++) {
    slotEls[i].className = (i === selected) ? 'slot sel' : 'slot';
  }
}

/* ============================================================
   RESIZE
============================================================ */
window.addEventListener('resize', function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ============================================================
   MAIN LOOP
============================================================ */
var last = performance.now();
function frame(now) {
  requestAnimationFrame(frame);
  var dt = Math.min((now - last) / 1000, 0.05);
  last = now;

  physics(dt);
  updateChunks(Math.floor(pos.x / 16), Math.floor(pos.z / 16));
  updateTarget();

  /* clouds drift + wrap around player */
  for (var i = 0; i < clouds.length; i++) {
    var c = clouds[i];
    c.position.x += 1.5 * dt;
    if (c.position.x > pos.x + 250) c.position.x -= 500;
    if (c.position.z > pos.z + 250) c.position.z -= 500;
    if (c.position.z < pos.z - 250) c.position.z += 500;
  }

  /* water follows player */
  water.position.set(pos.x, WATER_LEVEL, pos.z);

  renderer.render(scene, camera);
}
requestAnimationFrame(frame);

})();
</script>
</body>
</html>
```