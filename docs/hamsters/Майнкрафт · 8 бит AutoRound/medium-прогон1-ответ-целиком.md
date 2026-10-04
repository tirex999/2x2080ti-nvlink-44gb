

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MC - Voxel Sandbox</title>
<style>
  html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; }
  canvas { display: block; }
  #overlay {
    position: fixed; inset: 0; z-index: 10;
    background: rgba(0,0,0,0.65);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: #fff; font-family: monospace; cursor: pointer; text-align: center;
  }
  #overlay h1 { font-size: 52px; letter-spacing: 6px; margin: 0 0 18px 0; text-shadow: 3px 3px 0 #333; }
  #overlay .controls { font-size: 15px; line-height: 1.7; margin-bottom: 26px; color: #ddd; }
  #overlay .play { font-size: 22px; color: #7dff7d; animation: pulse 1.2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  #crosshair {
    position: fixed; left: 50%; top: 50%; width: 20px; height: 20px;
    transform: translate(-50%,-50%); pointer-events: none; z-index: 5;
  }
  #crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: #fff; mix-blend-mode: difference;
  }
  #crosshair::before { left: 9px; top: 0; width: 2px; height: 20px; }
  #crosshair::after  { left: 0; top: 9px; width: 20px; height: 2px; }
  #hotbar {
    position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 5px; background: rgba(0,0,0,0.5);
    padding: 6px; border-radius: 6px; z-index: 5; font-family: monospace;
  }
  .slot {
    width: 44px; height: 44px; display: flex; align-items: center; justify-content: center;
    border: 2px solid rgba(255,255,255,0.25); border-radius: 4px;
    color: #fff; font-weight: bold; font-size: 14px; text-shadow: 1px 1px 2px #000;
  }
  .slot.selected { border: 2px solid #fff; box-shadow: 0 0 8px rgba(255,255,255,0.8); }
</style>
</head>
<body>
<div id="overlay">
  <h1>MINECRAFT-ISH</h1>
  <div class="controls">
    WASD &mdash; move &nbsp;|&nbsp; SPACE &mdash; jump<br>
    MOUSE &mdash; look &nbsp;|&nbsp; LEFT CLICK &mdash; break block<br>
    RIGHT CLICK &mdash; place block &nbsp;|&nbsp; 1&ndash;7 / WHEEL &mdash; select block<br>
    ESC &mdash; release mouse
  </div>
  <div class="play">Click to play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
'use strict';

// ---------- Constants ----------
var CHUNK = 16, HEIGHT = 80;
var BLOCK_AIR = 0;
var BLOCK_COLORS = {
  1: 0x4caf50, // grass
  2: 0x795548, // dirt
  3: 0x9e9e9e, // stone
  4: 0xe7d9a8, // sand
  5: 0x8d6e63, // wood
  6: 0x2e7d32, // leaves
  7: 0xffffff  // snow
};
var HOTBAR_BLOCKS = [1, 2, 3, 4, 5, 6, 7];
var HOTBAR_NAMES  = ['Grass','Dirt','Stone','Sand','Wood','Leaves','Snow'];

// ---------- Noise (deterministic) ----------
function hash2(x, z) {
  var n = (Math.imul(x, 374761393) + Math.imul(z, 668265263)) | 0;
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
function hash3(x, y, z) {
  var n = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1440662683)) | 0;
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
function noise2(x, z) {
  var xi = Math.floor(x), zi = Math.floor(z);
  var fx = x - xi, fz = z - zi;
  var ux = fx * fx * (3 - 2 * fx), uz = fz * fz * (3 - 2 * fz);
  var a = hash2(xi, zi), b = hash2(xi + 1, zi);
  var c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
  return a + (b - a) * ux + (c - a) * uz + (a - b - c + d) * ux * uz;
}
function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var fx = x - xi, fy = y - yi, fz = z - zi;
  var ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy), uz = fz * fz * (3 - 2 * fz);
  var c000 = hash3(xi, yi, zi),     c100 = hash3(xi + 1, yi, zi);
  var c010 = hash3(xi, yi + 1, zi), c110 = hash3(xi + 1, yi + 1, zi);
  var c001 = hash3(xi, yi, zi + 1), c101 = hash3(xi + 1, yi, zi + 1);
  var c011 = hash3(xi, yi + 1, zi + 1), c111 = hash3(xi + 1, yi + 1, zi + 1);
  var x00 = c000 + (c100 - c000) * ux;
  var x10 = c010 + (c110 - c010) * ux;
  var x01 = c001 + (c101 - c001) * ux;
  var x11 = c011 + (c111 - c011) * ux;
  var y0 = x00 + (x10 - x00) * uy;
  var y1 = x01 + (x11 - x01) * uy;
  return y0 + (y1 - y0) * uz;
}
function fractal2(x, z) {
  var sum = 0, amp = 0.5, total = 0, fx = x, fz = z;
  for (var o = 0; o < 4; o++) {
    sum += amp * noise2(fx, fz);
    total += amp;
    fx *= 2; fz *= 2; amp *= 0.5;
  }
  return sum / total;
}
function terrainHeight(x, z) {
  var m = fractal2(x * 0.004, z * 0.004);
  var h = fractal2(x * 0.02, z * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}

// ---------- Scene ----------
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.5, 1, 0.3);
scene.add(sun);

var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

// ---------- Chunks ----------
var chunks = new Map();      // "cx,cz" -> { data: Uint8Array|null, mesh: Mesh|null }
var chunkMeshes = [];        // all live chunk meshes (for raycasting)

function chunkKey(cx, cz) { return cx + ',' + cz; }

function readBlock(x, y, z) {
  if (y < 0 || y >= HEIGHT) return 0;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var c = chunks.get(chunkKey(cx, cz));
  if (!c || !c.data) return 0;
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  return c.data[(y * CHUNK + lz) * CHUNK + lx];
}
function writeBlock(x, y, z, id) {
  if (y < 0 || y >= HEIGHT) return;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  ensureChunk(cx, cz);
  var c = chunks.get(chunkKey(cx, cz));
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  c.data[(y * CHUNK + lz) * CHUNK + lx] = id;
  if (c.mesh) rebuildChunk(cx, cz);
}
function ensureChunk(cx, cz) {
  var key = chunkKey(cx, cz);
  var c = chunks.get(key);
  if (!c) {
    c = { data: null, mesh: null };
    chunks.set(key, c);
  }
  if (!c.data) generateChunkData(cx, cz, c);
  return c;
}

// ---------- Terrain generation ----------
function generateChunkData(cx, cz, c) {
  var data = new Uint8Array(CHUNK * CHUNK * HEIGHT);
  c.data = data;

  for (var lx = 0; lx < CHUNK; lx++) {
    for (var lz = 0; lz < CHUNK; lz++) {
      var wx = cx * CHUNK + lx, wz = cz * CHUNK + lz;
      var H = terrainHeight(wx, wz);
      if (H > 78) H = 78;
      for (var y = 0; y <= H; y++) {
        var id;
        if (y === 0) id = 3;                       // bedrock layer (unbreakable)
        else if (y < H - 3) id = 3;                // stone
        else if (y < H) id = (H <= 16) ? 4 : (H >= 37) ? 3 : 2; // dirt band
        else id = (H >= 46) ? 7 : (H >= 37) ? 3 : (H <= 16) ? 4 : 1; // surface
        if (y >= 3 && y <= H - 2 && noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) id = 0; // caves
        data[(y * CHUNK + lz) * CHUNK + lx] = id;
      }
      // trees
      var surfaceIsGrass = (H >= 17 && H <= 45);
      if (surfaceIsGrass && hash2(wx, wz) < 0.02 &&
          lx >= 1 && lx <= 14 && lz >= 1 && lz <= 14 && H + 6 < HEIGHT) {
        for (var t = 1; t <= 4; t++) writeBlock(wx, H + t, wz, 5);           // trunk
        for (var dy = 3; dy <= 4; dy++)                                       // 5x5 twice
          for (var dx = -2; dx <= 2; dx++)
            for (var dz = -2; dz <= 2; dz++)
              if (readBlock(wx + dx, H + dy, wz + dz) === 0)
                writeBlock(wx + dx, H + dy, wz + dz, 6);
        for (var dx2 = -1; dx2 <= 1; dx2++)                                   // 3x3
          for (var dz2 = -1; dz2 <= 1; dz2++)
            if (readBlock(wx + dx2, H + 5, wz + dz2) === 0)
              writeBlock(wx + dx2, H + 5, wz + dz2, 6);
        if (readBlock(wx, H + 6, wz) === 0) writeBlock(wx, H + 6, wz, 6);     // top
      }
    }
  }
}

// ---------- Meshing ----------
var FACES = [
  { dir: [ 1, 0, 0], corners: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]], shade: 0.8 },
  { dir: [-1, 0, 0], corners: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]], shade: 0.8 },
  { dir: [ 0, 1, 0], corners: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]], shade: 1.0 },
  { dir: [ 0,-1, 0], corners: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], shade: 0.55 },
  { dir: [ 0, 0, 1], corners: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], shade: 0.8 },
  { dir: [ 0, 0,-1], corners: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]], shade: 0.8 }
];
var COLOR_RGB = {};
for (var bid in BLOCK_COLORS) {
  var col = BLOCK_COLORS[bid];
  COLOR_RGB[bid] = [((col >> 16) & 255) / 255, ((col >> 8) & 255) / 255, (col & 255) / 255];
}

function buildChunkGeometry(cx, cz, data) {
  var positions = [], normals = [], colors = [], indices = [];
  for (var y = 0; y < HEIGHT; y++) {
    for (var lz = 0; lz < CHUNK; lz++) {
      for (var lx = 0; lx < CHUNK; lx++) {
        var id = data[(y * CHUNK + lz) * CHUNK + lx];
        if (id === 0) continue;
        var wx = cx * CHUNK + lx, wy = y, wz = cz * CHUNK + lz;
        var rgb = COLOR_RGB[id];
        for (var f = 0; f < 6; f++) {
          var face = FACES[f];
          if (readBlock(wx + face.dir[0], wy + face.dir[1], wz + face.dir[2]) !== 0) continue;
          var base = positions.length / 3;
          for (var v = 0; v < 4; v++) {
            var cn = face.corners[v];
            positions.push(wx + cn[0], wy + cn[1], wz + cn[2]);
            normals.push(face.dir[0], face.dir[1], face.dir[2]);
            colors.push(rgb[0] * face.shade, rgb[1] * face.shade, rgb[2] * face.shade);
          }
          indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
        }
      }
    }
  }
  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices);
  return geo;
}

function removeChunkMesh(c) {
  if (c.mesh) {
    scene.remove(c.mesh);
    var i = chunkMeshes.indexOf(c.mesh);
    if (i >= 0) chunkMeshes.splice(i, 1);
    c.mesh.geometry.dispose();
    c.mesh = null;
  }
}
function buildChunkMesh(cx, cz) {
  var c = chunks.get(chunkKey(cx, cz));
  if (!c || !c.data || c.mesh) return;
  var geo = buildChunkGeometry(cx, cz, c.data);
  var mesh = new THREE.Mesh(geo, blockMaterial);
  scene.add(mesh);
  chunkMeshes.push(mesh);
  c.mesh = mesh;
}
function rebuildChunk(cx, cz) {
  var c = chunks.get(chunkKey(cx, cz));
  if (!c || !c.data) return;
  removeChunkMesh(c);
  buildChunkMesh(cx, cz);
}

// ---------- World streaming ----------
function updateWorld() {
  var pcx = Math.floor(player.x / CHUNK), pcz = Math.floor(player.z / CHUNK);

  // generate data within 5 chunks (max 4/frame), nearest first
  var missing = [];
  for (var dx = -5; dx <= 5; dx++) {
    for (var dz = -5; dz <= 5; dz++) {
      var c = chunks.get(chunkKey(pcx + dx, pcz + dz));
      if (!c || !c.data) missing.push([dx * dx + dz * dz, pcx + dx, pcz + dz]);
    }
  }
  missing.sort(function (a, b) { return a[0] - b[0]; });
  var genCount = 0;
  for (var i = 0; i < missing.length && genCount < 4; i++, genCount++) {
    ensureChunk(missing[i][1], missing[i][2]);
  }

  // build meshes within 4 chunks (max 2/frame) when 4 neighbors have data
  var todo = [];
  for (var mx = -4; mx <= 4; mx++) {
    for (var mz = -4; mz <= 4; mz++) {
      var cc = chunks.get(chunkKey(pcx + mx, pcz + mz));
      if (cc && cc.data && !cc.mesh) {
        var ok = true;
        if (!chunks.get(chunkKey(pcx + mx + 1, pcz + mz)) || !chunks.get(chunkKey(pcx + mx + 1, pcz + mz)).data) ok = false;
        if (ok && (!chunks.get(chunkKey(pcx + mx - 1, pcz + mz)) || !chunks.get(chunkKey(pcx + mx - 1, pcz + mz)).data)) ok = false;
        if (ok && (!chunks.get(chunkKey(pcx + mx, pcz + mz + 1)) || !chunks.get(chunkKey(pcx + mx, pcz + mz + 1)).data)) ok = false;
        if (ok && (!chunks.get(chunkKey(pcx + mx, pcz + mz - 1)) || !chunks.get(chunkKey(pcx + mx, pcz + mz - 1)).data)) ok = false;
        if (ok) todo.push([mx * mx + mz * mz, pcx + mx, pcz + mz]);
      }
    }
  }
  todo.sort(function (a, b) { return a[0] - b[0]; });
  for (var j = 0; j < todo.length && j < 2; j++) buildChunkMesh(todo[j][1], todo[j][2]);

  // cull beyond 7 chunks
  chunks.forEach(function (c, key) {
    var parts = key.split(',');
    var cx = parseInt(parts[0], 10), cz = parseInt(parts[1], 10);
    if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
      removeChunkMesh(c);
      chunks.delete(key);
    }
  });
}

// ---------- Player ----------
var HALF_W = 0.3, P_HEIGHT = 1.8, EYE = 1.62;
var GRAVITY = 25, JUMP_V = 8.5, MOVE_SPEED = 5.5;

var spawnH = terrainHeight(8, 8);
var spawn = { x: 8.5, y: spawnH + 2, z: 8.5 };
var player = { x: spawn.x, y: spawn.y, z: spawn.z, vx: 0, vy: 0, vz: 0, onGround: false };
var yaw = 0, pitch = 0;

var keys = {};
window.addEventListener('keydown', function (e) {
  keys[e.code] = true;
  if (e.code === 'Space') e.preventDefault();
  if (e.code >= 'Digit1' && e.code <= 'Digit7') selectSlot(parseInt(e.code.charAt(5), 10) - 1);
});
window.addEventListener('keyup', function (e) { keys[e.code] = false; });

function collides(x, y, z) {
  var x0 = Math.floor(x - HALF_W), x1 = Math.floor(x + HALF_W);
  var y0 = Math.floor(y), y1 = Math.floor(y + P_HEIGHT);
  var z0 = Math.floor(z - HALF_W), z1 = Math.floor(z + HALF_W);
  for (var bx = x0; bx <= x1; bx++)
    for (var by = y0; by <= y1; by++)
      for (var bz = z0; bz <= z1; bz++)
        if (readBlock(bx, by, bz) !== 0) return true;
  return false;
}

function updatePlayer(dt) {
  var f = 0, s = 0;
  if (keys['KeyW']) f += 1;
  if (keys['KeyS']) f -= 1;
  if (keys['KeyD']) s += 1;
  if (keys['KeyA']) s -= 1;
  var sinY = Math.sin(yaw), cosY = Math.cos(yaw);
  var dx = (-sinY * f + cosY * s);
  var dz = (-cosY * f - sinY * s);
  var len = Math.sqrt(dx * dx + dz * dz);
  if (len > 0) { dx /= len; dz /= len; }
  player.vx = dx * MOVE_SPEED;
  player.vz = dz * MOVE_SPEED;

  if (keys['Space'] && player.onGround) { player.vy = JUMP_V; player.onGround = false; }
  player.vy -= GRAVITY * dt;

  var nx = player.x + player.vx * dt;
  if (!collides(nx, player.y, player.z)) player.x = nx;

  var nz = player.z + player.vz * dt;
  if (!collides(player.x, player.y, nz)) player.z = nz;

  var ny = player.y + player.vy * dt;
  if (collides(player.x, ny, player.z)) {
    if (player.vy < 0) player.onGround = true;
    player.vy = 0;
  } else {
    player.y = ny;
    player.onGround = false;
  }

  if (player.y < -20) {
    player.x = spawn.x; player.y = spawn.y; player.z = spawn.z;
    player.vx = player.vy = player.vz = 0;
  }

  camera.position.set(player.x, player.y + EYE, player.z);
  camera.rotation.y = yaw;
  camera.rotation.x = pitch;
}

// ---------- Input: pointer lock, mouse, break/place ----------
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
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  var lim = Math.PI / 2 - 0.01;
  if (pitch > lim) pitch = lim;
  if (pitch < -lim) pitch = -lim;
});
document.addEventListener('contextmenu', function (e) { e.preventDefault(); });

var raycaster = new THREE.Raycaster();
raycaster.far = 6;
var centerVec = new THREE.Vector2(0, 0);
var targetBlock = null, placeCell = null;

var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

function updateTarget() {
  targetBlock = null;
  placeCell = null;
  if (!locked) { outline.visible = false; return; }
  raycaster.setFromCamera(centerVec, camera);
  var hits = raycaster.intersectObjects(chunkMeshes);
  if (hits.length > 0) {
    var hit = hits[0];
    var n = hit.face.normal;
    var p = hit.point;
    targetBlock = {
      x: Math.floor(p.x - n.x * 0.5),
      y: Math.floor(p.y - n.y * 0.5),
      z: Math.floor(p.z - n.z * 0.5)
    };
    placeCell = {
      x: Math.floor(p.x + n.x * 0.5),
      y: Math.floor(p.y + n.y * 0.5),
      z: Math.floor(p.z + n.z * 0.5)
    };
    outline.position.set(targetBlock.x + 0.5, targetBlock.y + 0.5, targetBlock.z + 0.5);
    outline.visible = true;
  } else {
    outline.visible = false;
  }
}

function rebuildAround(x, y, z) {
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  rebuildChunk(cx, cz);
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === CHUNK - 1) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === CHUNK - 1) rebuildChunk(cx, cz + 1);
}

function overlapsPlayer(bx, by, bz) {
  return (bx + 1 > player.x - HALF_W && bx < player.x + HALF_W &&
          by + 1 > player.y && by < player.y + P_HEIGHT &&
          bz + 1 > player.z - HALF_W && bz < player.z + HALF_W);
}

document.addEventListener('mousedown', function (e) {
  if (!locked) return;
  if (e.button === 0) {
    if (!targetBlock) return;
    if (targetBlock.y === 0) return; // unbreakable bedrock layer
    writeBlock(targetBlock.x, targetBlock.y, targetBlock.z, 0);
    rebuildAround(targetBlock.x, targetBlock.y, targetBlock.z);
  } else if (e.button === 2) {
    if (!placeCell) return;
    if (placeCell.y < 0 || placeCell.y >= HEIGHT) return;
    if (readBlock(placeCell.x, placeCell.y, placeCell.z) !== 0) return;
    if (overlapsPlayer(placeCell.x, placeCell.y, placeCell.z)) return;
    writeBlock(placeCell.x, placeCell.y, placeCell.z, HOTBAR_BLOCKS[selectedSlot]);
    rebuildAround(placeCell.x, placeCell.y, placeCell.z);
  }
});

// ---------- Hotbar ----------
var selectedSlot = 0;
var hotbarEl = document.getElementById('hotbar');
var slotEls = [];
HOTBAR_BLOCKS.forEach(function (id, i) {
  var el = document.createElement('div');
  el.className = 'slot';
  el.style.background = '#' + BLOCK_COLORS[id].toString(16).padStart(6, '0');
  el.textContent = (i + 1);
  el.title = HOTBAR_NAMES[i];
  hotbarEl.appendChild(el);
  slotEls.push(el);
});
function selectSlot(i) {
  selectedSlot = ((i % 7) + 7) % 7;
  for (var k = 0; k < slotEls.length; k++)
    slotEls[k].className = 'slot' + (k === selectedSlot ? ' selected' : '');
}
selectSlot(0);
window.addEventListener('wheel', function (e) {
  if (!locked) return;
  selectSlot(selectedSlot + (e.deltaY > 0 ? 1 : -1));
}, { passive: true });

// ---------- Clouds ----------
var cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85, depthWrite: false });
var clouds = [];
for (var ci = 0; ci < 25; ci++) {
  var cg = new THREE.BoxGeometry(8 + Math.random() * 18, 1.5, 6 + Math.random() * 14);
  var cm = new THREE.Mesh(cg, cloudMat);
  cm.position.set((Math.random() - 0.5) * 400, 88 + Math.random() * 8, (Math.random() - 0.5) * 400);
  cm.userData.speed = 1.5 + Math.random() * 2;
  scene.add(cm);
  clouds.push(cm);
}
function updateClouds(dt) {
  for (var i = 0; i < clouds.length; i++) {
    var c = clouds[i];
    c.position.x += c.userData.speed * dt;
    if (c.position.x - player.x > 220) c.position.x -= 440;
    if (c.position.x - player.x < -220) c.position.x += 440;
    if (c.position.z - player.z > 220) c.position.z -= 440;
    if (c.position.z - player.z < -220) c.position.z += 440;
  }
}

// ---------- Water ----------
var water = new THREE.Mesh(
  new THREE.PlaneGeometry(400, 400),
  new THREE.MeshLambertMaterial({ color: 0x2277cc, transparent: true, opacity: 0.6, depthWrite: false })
);
water.rotation.x = -Math.PI / 2;
water.position.y = 14.3;
scene.add(water);

// ---------- Resize ----------
window.addEventListener('resize', function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- Main loop ----------
var lastTime = performance.now();
function animate() {
  requestAnimationFrame(animate);
  var now = performance.now();
  var dt = Math.min(0.05, (now - lastTime) / 1000);
  lastTime = now;

  updateWorld();
  updatePlayer(dt);
  updateClouds(dt);
  water.position.x = player.x;
  water.position.z = player.z;
  updateTarget();

  renderer.render(scene, camera);
}
animate();

})();
</script>
</body>
</html>
```