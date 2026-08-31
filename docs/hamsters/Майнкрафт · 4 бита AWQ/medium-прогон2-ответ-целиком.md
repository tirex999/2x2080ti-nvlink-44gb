

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>mc.html — Voxel Sandbox</title>
<style>
  html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: monospace; }
  #gameCanvas { display: block; width: 100%; height: 100%; }

  /* Crosshair */
  #crosshair {
    position: fixed; left: 50%; top: 50%; transform: translate(-50%, -50%);
    width: 20px; height: 20px; pointer-events: none; z-index: 5;
  }
  #crosshair::before, #crosshair::after {
    content: ""; position: absolute; background: rgba(255,255,255,0.85);
  }
  #crosshair::before { left: 9px; top: 0; width: 2px; height: 20px; }
  #crosshair::after  { left: 0; top: 9px; width: 20px; height: 2px; }

  /* Hotbar */
  #hotbar {
    position: fixed; left: 50%; bottom: 12px; transform: translateX(-50%);
    display: flex; gap: 4px; padding: 6px;
    background: rgba(0,0,0,0.55); border-radius: 6px; z-index: 5;
  }
  .slot {
    width: 46px; height: 46px; border: 2px solid rgba(255,255,255,0.35);
    border-radius: 4px; position: relative; box-sizing: border-box;
  }
  .slot.selected { border-color: #ffffff; box-shadow: 0 0 6px rgba(255,255,255,0.8); }
  .slot span {
    position: absolute; left: 3px; top: 1px; color: #fff; font-size: 11px;
    text-shadow: 1px 1px 1px #000;
  }

  /* Start overlay */
  #overlay {
    position: fixed; inset: 0; z-index: 10;
    background: rgba(20, 30, 40, 0.75);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; user-select: none;
  }
  #overlay .panel {
    text-align: center; color: #fff; background: rgba(0,0,0,0.5);
    padding: 34px 50px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.25);
  }
  #overlay h1 { margin: 0 0 18px 0; font-size: 42px; letter-spacing: 3px; color: #9fe08a; text-shadow: 3px 3px 0 #234; }
  #overlay ul { list-style: none; padding: 0; margin: 0 0 22px 0; line-height: 1.8; font-size: 15px; }
  #overlay .play { font-size: 20px; color: #ffd54f; animation: pulse 1.2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.45; } }
</style>
</head>
<body>
<canvas id="gameCanvas"></canvas>

<div id="crosshair"></div>

<div id="hotbar"></div>

<div id="overlay">
  <div class="panel">
    <h1>MINECRAFT&nbsp;JS</h1>
    <ul>
      <li><b>W A S D</b> — move &nbsp;&nbsp; <b>Space</b> — jump</li>
      <li><b>Mouse</b> — look around</li>
      <li><b>Left click</b> — break block</li>
      <li><b>Right click</b> — place block</li>
      <li><b>1 – 7 / wheel</b> — choose block</li>
    </ul>
    <div class="play">Click to play</div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
"use strict";

/* ============================================================
   Constants
   ============================================================ */
var CHUNK = 16;
var HEIGHT = 80;
var WATER_LEVEL = 14.3;
var GRAVITY = 25;
var JUMP_VEL = 8.5;
var WALK_SPEED = 5.5;
var REACH = 6;
var MOUSE_SENS = 0.002;

var BLOCKS = {
  0: null,
  1: 0x4caf50, // grass
  2: 0x795548, // dirt
  3: 0x9e9e9e, // stone
  4: 0xe7d9a8, // sand
  5: 0x8d6e63, // wood
  6: 0x2e7d32, // leaves
  7: 0xffffff  // snow
};
var HOTBAR_IDS = [1, 2, 3, 4, 5, 6, 7];

/* ============================================================
   Deterministic noise
   ============================================================ */
function hash2(x, z) {
  var h = (x * 374761393 + z * 668265263) | 0;
  h = (h ^ (h >> 13)) * 1274126177 | 0;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
function hash3(x, y, z) {
  var h = (x * 374761393 + y * 668265263 + z * 2147483587) | 0;
  h = (h ^ (h >> 13)) * 1274126177 | 0;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
function smooth(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
  var xi = Math.floor(x), zi = Math.floor(z);
  var xf = x - xi, zf = z - zi;
  var u = smooth(xf), v = smooth(zf);
  var a = hash2(xi, zi),     b = hash2(xi + 1, zi);
  var c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function fbm2(x, z) {
  var sum = 0, amp = 1, freq = 1, total = 0;
  for (var i = 0; i < 4; i++) {
    sum += noise2(x * freq, z * freq) * amp;
    total += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / total;
}

function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var xf = x - xi, yf = y - yi, zf = z - zi;
  var u = smooth(xf), v = smooth(yf), w = smooth(zf);
  var c000 = hash3(xi, yi, zi),       c100 = hash3(xi + 1, yi, zi);
  var c010 = hash3(xi, yi + 1, zi),   c110 = hash3(xi + 1, yi + 1, zi);
  var c001 = hash3(xi, yi, zi + 1),   c101 = hash3(xi + 1, yi, zi + 1);
  var c011 = hash3(xi, yi + 1, zi + 1), c111 = hash3(xi + 1, yi + 1, zi + 1);
  var x00 = c000 + (c100 - c000) * u;
  var x10 = c010 + (c110 - c010) * u;
  var x01 = c001 + (c101 - c001) * u;
  var x11 = c011 + (c111 - c011) * u;
  var y0 = x00 + (x10 - x00) * v;
  var y1 = x01 + (x11 - x01) * v;
  return y0 + (y1 - y0) * w;
}
function fbm3(x, y, z) {
  var sum = 0, amp = 1, freq = 1, total = 0;
  for (var i = 0; i < 3; i++) {
    sum += noise3(x * freq, y * freq, z * freq) * amp;
    total += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / total;
}

/* ============================================================
   Three.js setup
   ============================================================ */
var canvas = document.getElementById("gameCanvas");
var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: false });
renderer.setPixelRatio(window.devicePixelRatio || 1);
renderer.setSize(window.innerWidth, window.innerHeight);

var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = "YXZ";

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.5, 1, 0.3);
scene.add(sun);

var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

window.addEventListener("resize", function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ============================================================
   Chunks
   ============================================================ */
var chunks = new Map();          // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
var chunkMeshes = [];            // all live meshes, for raycasting

function chunkIndex(lx, y, lz) { return (lx * 16 + lz) * HEIGHT + y; }

function getBlock(x, y, z) {
  if (y < 0 || y >= HEIGHT) return 0;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var ch = chunks.get(cx + "," + cz);
  if (!ch) return 0;
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  return ch.data[chunkIndex(lx, y, lz)];
}
function setBlock(x, y, z, id) {
  if (y < 0 || y >= HEIGHT) return;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var ch = chunks.get(cx + "," + cz);
  if (!ch) return;
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  ch.data[chunkIndex(lx, y, lz)] = id;
}

/* ---------- Terrain generation ---------- */
function generateChunkData(cx, cz) {
  var data = new Uint8Array(CHUNK * CHUNK * HEIGHT);
  for (var lx = 0; lx < CHUNK; lx++) {
    for (var lz = 0; lz < CHUNK; lz++) {
      var wx = cx * CHUNK + lx, wz = cz * CHUNK + lz;

      var m = fbm2(wx * 0.004, wz * 0.004);
      var h = fbm2(wx * 0.02, wz * 0.02);
      var H = Math.floor(5 + m * m * 58 + h * 10);
      if (H > HEIGHT - 1) H = HEIGHT - 1;

      // Fill column
      for (var y = 0; y < H; y++) {
        var id;
        if (y === 0) id = 3;                                  // bedrock-ish unbreakable stone
        else if (y < H - 3) id = 3;                           // stone
        else if (H <= 16) id = 4;                             // sand underlayer
        else if (H >= 37) id = 3;                             // stone underlayer
        else id = 2;                                          // dirt underlayer
        data[chunkIndex(lx, y, lz)] = id;
      }

      // Surface
      var surf;
      if (H >= 46) surf = 7;
      else if (H >= 37) surf = 3;
      else if (H <= 16) surf = 4;
      else surf = 1;
      data[chunkIndex(lx, H, lz)] = surf;

      // Caves
      for (var cy = 3; cy < H - 2; cy++) {
        if (fbm3(wx * 0.09, cy * 0.09, wz * 0.09) > 0.67) {
          data[chunkIndex(lx, cy, lz)] = 0;
        }
      }

      // Trees (only if trunk + canopy fit inside this chunk)
      if (surf === 1 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 && H + 7 < HEIGHT &&
          hash2(wx * 7 + 13, wz * 7 + 29) < 0.02) {
        // trunk: 4 wood blocks up
        for (var ty = H + 1; ty <= H + 4; ty++) {
          if (data[chunkIndex(lx, ty, lz)] === 0) data[chunkIndex(lx, ty, lz)] = 5;
        }
        // 5x5 leaves twice
        for (var ly = H + 4; ly <= H + 5; ly++) {
          for (var ox = -2; ox <= 2; ox++) {
            for (var oz = -2; oz <= 2; oz++) {
              var di = chunkIndex(lx + ox, ly, lz + oz);
              if (data[di] === 0) data[di] = 6;
            }
          }
        }
        // 3x3
        for (var ox2 = -1; ox2 <= 1; ox2++) {
          for (var oz2 = -1; oz2 <= 1; oz2++) {
            var di2 = chunkIndex(lx + ox2, H + 6, lz + oz2);
            if (data[di2] === 0) data[di2] = 6;
          }
        }
        // 1 on top
        if (data[chunkIndex(lx, H + 7, lz)] === 0) data[chunkIndex(lx, H + 7, lz)] = 6;
      }
    }
  }
  var ch = { data: data, mesh: null };
  chunks.set(cx + "," + cz, ch);
  return ch;
}

/* ---------- Meshing ---------- */
// Face tables: dir offset, 4 corner offsets (outward CCW winding), shade
var FACES = [
  { n: [ 1, 0, 0], s: 0.8, v: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]] }, // +X
  { n: [-1, 0, 0], s: 0.8, v: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]] }, // -X
  { n: [ 0, 1, 0], s: 1.0, v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] }, // +Y
  { n: [ 0,-1, 0], s: 0.55,v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] }, // -Y
  { n: [ 0, 0, 1], s: 0.8, v: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]] }, // +Z
  { n: [ 0, 0,-1], s: 0.8, v: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]] }  // -Z
];

function removeChunkMesh(ch) {
  if (ch.mesh) {
    scene.remove(ch.mesh);
    ch.mesh.geometry.dispose();
    var i = chunkMeshes.indexOf(ch.mesh);
    if (i !== -1) chunkMeshes.splice(i, 1);
    ch.mesh = null;
  }
}

function buildChunkMesh(key) {
  var ch = chunks.get(key);
  if (!ch) return;
  removeChunkMesh(ch);

  var cx = parseInt(key.split(",")[0], 10);
  var cz = parseInt(key.split(",")[1], 10);

  var positions = [], normals = [], colors = [];

  for (var lx = 0; lx < CHUNK; lx++) {
    for (var lz = 0; lz < CHUNK; lz++) {
      var wx = cx * CHUNK + lx, wz = cz * CHUNK + lz;
      for (var y = 0; y < HEIGHT; y++) {
        var id = ch.data[chunkIndex(lx, y, lz)];
        if (id === 0) continue;

        var hex = BLOCKS[id];
        var r = ((hex >> 16) & 255) / 255;
        var g = ((hex >> 8) & 255) / 255;
        var b = (hex & 255) / 255;

        for (var f = 0; f < 6; f++) {
          var face = FACES[f];
          var nb = getBlock(wx + face.n[0], y + face.n[1], wz + face.n[2]);
          if (nb !== 0) continue;

          var sh = face.s;
          var cr = r * sh, cg = g * sh, cb = b * sh;
          var v = face.v;

          // two triangles: (0,1,2) and (0,2,3)
          var order = [0, 1, 2, 0, 2, 3];
          for (var k = 0; k < 6; k++) {
            var pv = v[order[k]];
            positions.push(wx + pv[0], y + pv[1], wz + pv[2]);
            normals.push(face.n[0], face.n[1], face.n[2]);
            colors.push(cr, cg, cb);
          }
        }
      }
    }
  }

  var geom = new THREE.BufferGeometry();
  geom.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  geom.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

  var mesh = new THREE.Mesh(geom, blockMaterial);
  mesh.position.set(0, 0, 0); // vertices are already in world space
  mesh.userData.chunkKey = key;
  scene.add(mesh);
  ch.mesh = mesh;
  chunkMeshes.push(mesh);
}

function neighborsHaveData(cx, cz) {
  return chunks.has((cx - 1) + "," + cz) && chunks.has((cx + 1) + "," + cz) &&
         chunks.has(cx + "," + (cz - 1)) && chunks.has(cx + "," + (cz + 1));
}

function rebuildChunkAtWorld(wx, wz) {
  var cx = Math.floor(wx / CHUNK), cz = Math.floor(wz / CHUNK);
  var key = cx + "," + cz;
  var ch = chunks.get(key);
  if (ch && ch.mesh) buildChunkMesh(key);

  // border blocks affect neighbor chunk meshes
  var lx = wx - cx * CHUNK, lz = wz - cz * CHUNK;
  if (lx === 0)      maybeRebuild(cx - 1, cz);
  if (lx === 15)     maybeRebuild(cx + 1, cz);
  if (lz === 0)      maybeRebuild(cx, cz - 1);
  if (lz === 15)     maybeRebuild(cx, cz + 1);
}
function maybeRebuild(cx, cz) {
  var key = cx + "," + cz;
  var ch = chunks.get(key);
  if (ch && ch.mesh) buildChunkMesh(key);
}

/* ---------- Per-frame world streaming ---------- */
function updateWorld() {
  var pcx = Math.floor(player.pos.x / CHUNK);
  var pcz = Math.floor(player.pos.z / CHUNK);

  // 1) generate data within 5 chunks (max 4/frame)
  var genCount = 0;
  outerGen:
  for (var dx = -5; dx <= 5; dx++) {
    for (var dz = -5; dz <= 5; dz++) {
      var gx = pcx + dx, gz = pcz + dz;
      if (!chunks.has(gx + "," + gz)) {
        generateChunkData(gx, gz);
        genCount++;
        if (genCount >= 4) break outerGen;
      }
    }
  }

  // 2) build meshes within 4 chunks whose 4 neighbors have data (max 2/frame)
  var meshCount = 0;
  outerMesh:
  for (var mx = -4; mx <= 4; mx++) {
    for (var mz = -4; mz <= 4; mz++) {
      var mcx = pcx + mx, mcz = pcz + mz;
      var key = mcx + "," + mcz;
      var ch = chunks.get(key);
      if (ch && !ch.mesh && neighborsHaveData(mcx, mcz)) {
        buildChunkMesh(key);
        meshCount++;
        if (meshCount >= 2) break outerMesh;
      }
    }
  }

  // 3) drop chunks farther than 7
  var toDelete = [];
  chunks.forEach(function (value, key) {
    var parts = key.split(",");
    var cx = parseInt(parts[0], 10), cz = parseInt(parts[1], 10);
    var dist = Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz));
    if (dist > 7) toDelete.push(key);
  });
  for (var i = 0; i < toDelete.length; i++) {
    var delCh = chunks.get(toDelete[i]);
    removeChunkMesh(delCh);
    chunks.delete(toDelete[i]);
  }
}

/* ============================================================
   Player
   ============================================================ */
var player = {
  pos: new THREE.Vector3(8, 60, 8),   // feet position
  vel: new THREE.Vector3(),
  yaw: 0,
  pitch: 0,
  onGround: false,
  halfW: 0.3,
  height: 1.8,
  eye: 1.62
};

var SPAWN = new THREE.Vector3(8, 60, 8);

function computeSpawn() {
  // ensure chunk 0,0 exists
  if (!chunks.has("0,0")) generateChunkData(0, 0);
  for (var y = HEIGHT - 1; y >= 0; y--) {
    if (getBlock(8, y, 8) !== 0) {
      SPAWN.set(8, y + 1, 8);
      break;
    }
  }
  player.pos.copy(SPAWN);
}

function boxCollides(px, py, pz) {
  var x0 = Math.floor(px - player.halfW), x1 = Math.floor(px + player.halfW);
  var y0 = Math.floor(py),                y1 = Math.floor(py + player.height - 0.001);
  var z0 = Math.floor(pz - player.halfW), z1 = Math.floor(pz + player.halfW);
  for (var x = x0; x <= x1; x++)
    for (var y = y0; y <= y1; y++)
      for (var z = z0; z <= z1; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}

var keys = {};
window.addEventListener("keydown", function (e) {
  keys[e.code] = true;
  if (e.code >= "Digit1" && e.code <= "Digit7") {
    selectSlot(parseInt(e.code.charAt(5), 10) - 1);
  }
});
window.addEventListener("keyup", function (e) { keys[e.code] = false; });

function updatePlayer(dt) {
  // input direction relative to yaw
  var fx = -Math.sin(player.yaw), fz = -Math.cos(player.yaw); // forward
  var rx =  Math.cos(player.yaw), rz = -Math.sin(player.yaw); // right
  var mx = 0, mz = 0;
  if (keys["KeyW"]) { mx += fx; mz += fz; }
  if (keys["KeyS"]) { mx -= fx; mz -= fz; }
  if (keys["KeyD"]) { mx += rx; mz += rz; }
  if (keys["KeyA"]) { mx -= rx; mz -= rz; }
  var len = Math.sqrt(mx * mx + mz * mz);
  if (len > 0) { mx = mx / len * WALK_SPEED; mz = mz / len * WALK_SPEED; }

  player.vel.x = mx;
  player.vel.z = mz;

  player.vel.y -= GRAVITY * dt;
  if (player.vel.y < -60) player.vel.y = -60;

  if (keys["Space"] && player.onGround) {
    player.vel.y = JUMP_VEL;
    player.onGround = false;
  }

  var p = player.pos;

  // X axis
  p.x += player.vel.x * dt;
  if (boxCollides(p.x, p.y, p.z)) {
    p.x -= player.vel.x * dt;
    player.vel.x = 0;
  }
  // Z axis
  p.z += player.vel.z * dt;
  if (boxCollides(p.x, p.y, p.z)) {
    p.z -= player.vel.z * dt;
    player.vel.z = 0;
  }
  // Y axis
  p.y += player.vel.y * dt;
  if (boxCollides(p.x, p.y, p.z)) {
    p.y -= player.vel.y * dt;
    if (player.vel.y < 0) player.onGround = true;
    player.vel.y = 0;
  } else if (player.vel.y < -0.01) {
    player.onGround = false;
  }

  // fell off the world
  if (p.y < -20) {
    p.copy(SPAWN);
    player.vel.set(0, 0, 0);
  }

  camera.position.set(p.x, p.y + player.eye, p.z);
  camera.rotation.y = player.yaw;
  camera.rotation.x = player.pitch;
}

/* ============================================================
   Pointer lock, mouse look, break/place
   ============================================================ */
var overlay = document.getElementById("overlay");
var locked = false;

overlay.addEventListener("click", function () {
  canvas.requestPointerLock();
});
document.addEventListener("pointerlockchange", function () {
  locked = (document.pointerLockElement === canvas);
  overlay.style.display = locked ? "none" : "flex";
});
document.addEventListener("contextmenu", function (e) { e.preventDefault(); });

document.addEventListener("mousemove", function (e) {
  if (!locked) return;
  player.yaw   -= e.movementX * MOUSE_SENS;
  player.pitch -= e.movementY * MOUSE_SENS;
  var lim = Math.PI / 2 - 0.01;
  if (player.pitch > lim) player.pitch = lim;
  if (player.pitch < -lim) player.pitch = -lim;
});

/* ---------- Hotbar ---------- */
var selectedSlot = 0;
var hotbarEl = document.getElementById("hotbar");
var slotEls = [];
HOTBAR_IDS.forEach(function (id, i) {
  var div = document.createElement("div");
  div.className = "slot" + (i === 0 ? " selected" : "");
  var hex = "#" + BLOCKS[id].toString(16).padStart(6, "0");
  div.style.background = hex;
  var label = document.createElement("span");
  label.textContent = String(i + 1);
  div.appendChild(label);
  hotbarEl.appendChild(div);
  slotEls.push(div);
});
function selectSlot(i) {
  selectedSlot = ((i % 7) + 7) % 7;
  for (var k = 0; k < slotEls.length; k++) {
    slotEls[k].className = "slot" + (k === selectedSlot ? " selected" : "");
  }
}
window.addEventListener("wheel", function (e) {
  if (!locked) return;
  selectSlot(selectedSlot + (e.deltaY > 0 ? 1 : -1));
}, { passive: true });

/* ---------- Raycast targeting ---------- */
var raycaster = new THREE.Raycaster();
raycaster.far = REACH;
var centerVec = new THREE.Vector2(0, 0);

var outlineBox = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outlineBox.visible = false;
scene.add(outlineBox);

var targetBlock = null; // {x,y,z} of block being aimed at

function updateTarget() {
  targetBlock = null;
  outlineBox.visible = false;
  if (!locked) return;

  raycaster.setFromCamera(centerVec, camera);
  var hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length === 0 || hits[0].distance > REACH) return;

  var hit = hits[0];
  var p = hit.point;
  var n = hit.face.normal; // mesh untransformed => world space

  var bx = Math.floor(p.x - n.x * 0.5);
  var by = Math.floor(p.y - n.y * 0.5);
  var bz = Math.floor(p.z - n.z * 0.5);

  if (by < 0 || by >= HEIGHT) return;
  if (getBlock(bx, by, bz) === 0) return;

  targetBlock = { x: bx, y: by, z: bz };
  outlineBox.position.set(bx + 0.5, by + 0.5, bz + 0.5);
  outlineBox.visible = true;
}

function overlapsPlayerCell(bx, by, bz) {
  var p = player.pos;
  return (bx + 1 > p.x - player.halfW && bx < p.x + player.halfW &&
          bz + 1 > p.z - player.halfW && bz < p.z + player.halfW &&
          by + 1 > p.y && by < p.y + player.height);
}

document.addEventListener("mousedown", function (e) {
  if (!locked) return;
  if (!targetBlock) return;
  var t = targetBlock;

  if (e.button === 0) {
    // break (never the unbreakable bottom layer)
    if (t.y <= 0) return;
    setBlock(t.x, t.y, t.z, 0);
    rebuildChunkAtWorld(t.x, t.z);
  } else if (e.button === 2) {
    // place
    var hit = raycaster.ray.origin.clone().add(raycaster.ray.direction.clone().multiplyScalar(0));
    // recompute place cell from current hit geometry:
    raycaster.setFromCamera(centerVec, camera);
    var hits = raycaster.intersectObjects(chunkMeshes, false);
    if (hits.length === 0) return;
    var hp = hits[0].point, hn = hits[0].face.normal;
    var px = Math.floor(hp.x + hn.x * 0.5);
    var py = Math.floor(hp.y + hn.y * 0.5);
    var pz = Math.floor(hp.z + hn.z * 0.5);
    if (py < 0 || py >= HEIGHT) return;
    if (getBlock(px, py, pz) !== 0) return;
    if (overlapsPlayerCell(px, py, pz)) return;
    setBlock(px, py, pz, HOTBAR_IDS[selectedSlot]);
    rebuildChunkAtWorld(px, pz);
  }
});

/* ============================================================
   Clouds & water
   ============================================================ */
var cloudGeo = new THREE.BoxGeometry(14, 1.5, 9);
var cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
var clouds = [];
(function makeClouds() {
  var seed = 12345;
  function rnd() { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; }
  for (var i = 0; i < 25; i++) {
    var c = new THREE.Mesh(cloudGeo, cloudMat);
    c.scale.set(0.6 + rnd() * 1.8, 1, 0.6 + rnd() * 1.8);
    c.userData.offX = (rnd() - 0.5) * 300;
    c.userData.offZ = (rnd() - 0.5) * 300;
    c.userData.speed = 1 + rnd() * 2;
    scene.add(c);
    clouds.push(c);
  }
})();
function updateClouds(dt) {
  for (var i = 0; i < clouds.length; i++) {
    var c = clouds[i];
    c.userData.offX += c.userData.speed * dt;
    if (c.userData.offX > 150) c.userData.offX -= 300;
    c.position.set(player.pos.x + c.userData.offX, 90, player.pos.z + c.userData.offZ);
  }
}

var waterGeo = new THREE.PlaneGeometry(400, 400);
var waterMat = new THREE.MeshLambertMaterial({
  color: 0x3d7dd8, transparent: true, opacity: 0.55, depthWrite: false
});
var water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI / 2;
scene.add(water);
function updateWater() {
  water.position.set(player.pos.x, WATER_LEVEL, player.pos.z);
}

/* ============================================================
   Boot & main loop
   ============================================================ */
generateChunkData(0, 0);
computeSpawn();

var lastTime = performance.now();
function animate() {
  requestAnimationFrame(animate);
  var now = performance.now();
  var dt = (now - lastTime) / 1000;
  lastTime = now;
  if (dt > 0.05) dt = 0.05;

  updateWorld();
  updatePlayer(dt);
  updateTarget();
  updateClouds(dt);
  updateWater();

  renderer.render(scene, camera);
}
animate();

})();
</script>
</body>
</html>
```