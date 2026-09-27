```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>mc.html - Voxel Sandbox</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; width: 100%; height: 100%; background: #000; font-family: 'Segoe UI', Arial, sans-serif; }
  canvas { display: block; }

  #overlay {
    position: fixed; left: 0; top: 0; width: 100%; height: 100%;
    background: rgba(10, 15, 25, 0.82);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: #fff; z-index: 20; cursor: pointer; text-align: center;
  }
  #overlay h1 { font-size: 52px; margin: 0 0 10px 0; letter-spacing: 3px; text-shadow: 3px 3px 0 #2e7d32; }
  #overlay .controls { font-size: 16px; line-height: 1.7; color: #cfd8dc; margin: 14px 0 22px 0; }
  #overlay .play { font-size: 26px; color: #fff; background: #2e7d32; padding: 12px 34px; border-radius: 8px; box-shadow: 0 4px 0 #1b5e20; }

  #crosshair { position: fixed; left: 50%; top: 50%; width: 0; height: 0; z-index: 10; pointer-events: none; }
  #crosshair .h { position: absolute; left: -10px; top: -1px; width: 20px; height: 2px; background: rgba(255,255,255,0.85); }
  #crosshair .v { position: absolute; left: -1px; top: -10px; width: 2px; height: 20px; background: rgba(255,255,255,0.85); }

  #hotbar {
    position: fixed; left: 50%; bottom: 12px; transform: translateX(-50%);
    display: flex; gap: 5px; background: rgba(0,0,0,0.55); padding: 6px; border-radius: 8px; z-index: 10;
  }
  .slot {
    width: 46px; height: 46px; border: 2px solid #555; border-radius: 4px; position: relative; box-sizing: border-box;
  }
  .slot.sel { border-color: #fff; box-shadow: 0 0 6px rgba(255,255,255,0.7); }
  .slot span { position: absolute; left: 3px; top: 1px; font-size: 11px; color: #fff; text-shadow: 1px 1px 0 #000; }
</style>
</head>
<body>

<div id="overlay">
  <h1>VOXELCRAFT</h1>
  <div class="controls">
    <b>WASD</b> move &nbsp;·&nbsp; <b>Space</b> jump &nbsp;·&nbsp; <b>Mouse</b> look<br>
    <b>Left click</b> break block &nbsp;·&nbsp; <b>Right click</b> place block<br>
    <b>1–7</b> or <b>mouse wheel</b> select block<br>
    <b>Esc</b> releases the mouse
  </div>
  <div class="play">Click to play</div>
</div>

<div id="crosshair"><div class="h"></div><div class="v"></div></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
'use strict';

// ---------------------------------------------------------------- constants
var CHUNK = 16, HEIGHT = 80, VIEW_GEN = 5, VIEW_MESH = 4, VIEW_UNLOAD = 7;
var GRAVITY = 25, JUMP_V = 8.5, SPEED = 5.5;
var P_HALF = 0.3, P_HEIGHT = 1.8, P_EYE = 1.62;
var REACH = 6, WATER_Y = 14.3;

var BLOCK_COLORS = { 1: 0x4caf50, 2: 0x795548, 3: 0x9e9e9e, 4: 0xe7d9a8, 5: 0x8d6e63, 6: 0x2e7d32, 7: 0xffffff };
var HOTBAR_BLOCKS = [1, 2, 3, 4, 5, 6, 7];

// ---------------------------------------------------------------- noise
function hash(x, y, z) {
  var n = Math.imul(x | 0, 374761393) + Math.imul(y | 0, 668265263) + Math.imul(z | 0, 1274126177);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  n = n ^ (n >>> 16);
  return (n >>> 0) / 4294967295;
}
function smooth(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
  var xi = Math.floor(x), zi = Math.floor(z);
  var xf = x - xi, zf = z - zi;
  var u = smooth(xf), v = smooth(zf);
  var a = hash(xi, 0, zi), b = hash(xi + 1, 0, zi);
  var c = hash(xi, 0, zi + 1), d = hash(xi + 1, 0, zi + 1);
  var ab = a + (b - a) * u, cd = c + (d - c) * u;
  return ab + (cd - ab) * v;
}
function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var xf = x - xi, yf = y - yi, zf = z - zi;
  var u = smooth(xf), v = smooth(yf), w = smooth(zf);
  var c000 = hash(xi, yi, zi),         c100 = hash(xi + 1, yi, zi);
  var c010 = hash(xi, yi + 1, zi),     c110 = hash(xi + 1, yi + 1, zi);
  var c001 = hash(xi, yi, zi + 1),     c101 = hash(xi + 1, yi, zi + 1);
  var c011 = hash(xi, yi + 1, zi + 1), c111 = hash(xi + 1, yi + 1, zi + 1);
  var x00 = c000 + (c100 - c000) * u, x10 = c010 + (c110 - c010) * u;
  var x01 = c001 + (c101 - c001) * u, x11 = c011 + (c111 - c011) * u;
  var y0 = x00 + (x10 - x00) * v, y1 = x01 + (x11 - x01) * v;
  return y0 + (y1 - y0) * w;
}
function fractal2(x, z) {
  var f = 1, a = 0.5, sum = 0, norm = 0;
  for (var o = 0; o < 4; o++) { sum += noise2(x * f, z * f) * a; norm += a; f *= 2; a *= 0.5; }
  return sum / norm;
}
function fractal3(x, y, z) {
  var f = 1, a = 0.5, sum = 0, norm = 0;
  for (var o = 0; o < 3; o++) { sum += noise3(x * f, y * f, z * f) * a; norm += a; f *= 2; a *= 0.5; }
  return sum / norm;
}

// ---------------------------------------------------------------- scene setup
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.5, 1.0, 0.3);
scene.add(sun);

var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

// ---------------------------------------------------------------- chunk storage
var chunks = new Map();          // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
var meshList = [];               // all chunk meshes for raycasting

function key(cx, cz) { return cx + ',' + cz; }
function idx(lx, lz, y) { return lx + lz * 16 + y * 256; }

function getBlock(x, y, z) {
  if (y < 0 || y >= HEIGHT) return 0;
  var cx = Math.floor(x / 16), cz = Math.floor(z / 16);
  var c = chunks.get(key(cx, cz));
  if (!c) return 0;
  return c.data[idx(x - cx * 16, z - cz * 16, y)];
}
function setBlock(x, y, z, b) {
  if (y < 0 || y >= HEIGHT) return;
  var cx = Math.floor(x / 16), cz = Math.floor(z / 16);
  var c = chunks.get(key(cx, cz));
  if (!c) return;
  c.data[idx(x - cx * 16, z - cz * 16, y)] = b;
}

// ---------------------------------------------------------------- terrain generation
function genChunk(cx, cz) {
  var data = new Uint8Array(CHUNK * CHUNK * HEIGHT);
  for (var lz = 0; lz < 16; lz++) {
    for (var lx = 0; lx < 16; lx++) {
      var wx = cx * 16 + lx, wz = cz * 16 + lz;
      var m = fractal2(wx * 0.004, wz * 0.004);
      var h = fractal2(wx * 0.02, wz * 0.02);
      var H = Math.floor(5 + m * m * 58 + h * 10);
      if (H > HEIGHT - 10) H = HEIGHT - 10;

      var sub, surf;
      if (H <= 16)          { sub = 4; surf = 4; }
      else if (H >= 46)     { sub = 3; surf = 7; }
      else if (H >= 37)     { sub = 3; surf = 3; }
      else                  { sub = 2; surf = 1; }

      for (var y = 0; y <= H; y++) {
        var b;
        if (y === 0) b = 3;
        else if (y === H) b = surf;
        else if (y >= H - 3) b = sub;
        else b = 3;
        if (y >= 3 && y <= H - 2 && fractal3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) b = 0;
        data[idx(lx, lz, y)] = b;
      }

      // trees on grass, trunk fully inside chunk (leaves 5x5 fit with 2-block margin)
      if (surf === 1 && H + 8 < HEIGHT && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 &&
          hash(wx, 999, wz) < 0.02) {
        for (var t = 1; t <= 4; t++) data[idx(lx, lz, H + t)] = 5;
        for (var dy = 3; dy <= 4; dy++)
          for (var ox = -2; ox <= 2; ox++)
            for (var oz = -2; oz <= 2; oz++) {
              var i2 = idx(lx + ox, lz + oz, H + dy);
              if (data[i2] === 0) data[i2] = 6;
            }
        for (var ox2 = -1; ox2 <= 1; ox2++)
          for (var oz2 = -1; oz2 <= 1; oz2++) {
            var i3 = idx(lx + ox2, lz + oz2, H + 5);
            if (data[i3] === 0) data[i3] = 6;
          }
        var i4 = idx(lx, lz, H + 6);
        if (data[i4] === 0) data[i4] = 6;
      }
    }
  }
  chunks.set(key(cx, cz), { data: data, mesh: null });
}

// ---------------------------------------------------------------- meshing
var FACES = [
  { n: [1, 0, 0],  b: 0.8,  v: [[1,0,0],[1,1,0],[1,1,1], [1,0,0],[1,1,1],[1,0,1]] },
  { n: [-1, 0, 0], b: 0.8,  v: [[0,0,1],[0,1,1],[0,1,0], [0,0,1],[0,1,0],[0,0,0]] },
  { n: [0, 1, 0],  b: 1.0,  v: [[0,1,1],[1,1,1],[1,1,0], [0,1,1],[1,1,0],[0,1,0]] },
  { n: [0, -1, 0], b: 0.55, v: [[0,0,0],[1,0,0],[1,0,1], [0,0,0],[1,0,1],[0,0,1]] },
  { n: [0, 0, 1],  b: 0.8,  v: [[0,0,1],[1,0,1],[1,1,1], [0,0,1],[1,1,1],[0,1,1]] },
  { n: [0, 0, -1], b: 0.8,  v: [[1,0,0],[0,0,0],[0,1,0], [1,0,0],[0,1,0],[1,1,0]] }
];

function neighborsReady(cx, cz) {
  return chunks.has(key(cx + 1, cz)) && chunks.has(key(cx - 1, cz)) &&
         chunks.has(key(cx, cz + 1)) && chunks.has(key(cx, cz - 1));
}

function buildMesh(cx, cz) {
  var c = chunks.get(key(cx, cz));
  var data = c.data;
  var baseX = cx * 16, baseZ = cz * 16;

  function get(x, y, z) {
    if (y < 0 || y >= HEIGHT) return 0;
    var lx = x - baseX, lz = z - baseZ;
    if (lx >= 0 && lx < 16 && lz >= 0 && lz < 16) return data[idx(lx, lz, y)];
    return getBlock(x, y, z);
  }

  var positions = [], normals = [], colors = [];

  for (var y = 0; y < HEIGHT; y++) {
    for (var lz = 0; lz < 16; lz++) {
      for (var lx = 0; lx < 16; lx++) {
        var b = data[idx(lx, lz, y)];
        if (!b) continue;
        var wx = baseX + lx, wz = baseZ + lz;
        var col = BLOCK_COLORS[b];
        var cr = ((col >> 16) & 255) / 255, cg = ((col >> 8) & 255) / 255, cb = (col & 255) / 255;
        for (var f = 0; f < 6; f++) {
          var face = FACES[f];
          if (get(wx + face.n[0], y + face.n[1], wz + face.n[2])) continue;
          var br = face.b;
          for (var i = 0; i < 6; i++) {
            var v = face.v[i];
            positions.push(wx + v[0], y + v[1], wz + v[2]);
            normals.push(face.n[0], face.n[1], face.n[2]);
            colors.push(cr * br, cg * br, cb * br);
          }
        }
      }
    }
  }

  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  var mesh = new THREE.Mesh(geo, blockMaterial);
  mesh.position.set(0, 0, 0);
  scene.add(mesh);
  meshList.push(mesh);
  return mesh;
}

function removeMesh(c) {
  if (!c.mesh) return;
  scene.remove(c.mesh);
  c.mesh.geometry.dispose();
  var i = meshList.indexOf(c.mesh);
  if (i >= 0) meshList.splice(i, 1);
  c.mesh = null;
}

function rebuildChunk(cx, cz) {
  var c = chunks.get(key(cx, cz));
  if (!c) return;
  removeMesh(c);
  if (neighborsReady(cx, cz)) c.mesh = buildMesh(cx, cz);
}

// ---------------------------------------------------------------- streaming
function updateChunks() {
  var pcx = Math.floor(player.pos.x / 16), pcz = Math.floor(player.pos.z / 16);
  var r, dx, dz, cx, cz, n;

  // generate data, nearest first, max 4 per frame
  n = 0;
  outerGen:
  for (r = 0; r <= VIEW_GEN; r++) {
    for (dx = -r; dx <= r; dx++) {
      for (dz = -r; dz <= r; dz++) {
        if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;
        cx = pcx + dx; cz = pcz + dz;
        if (!chunks.has(key(cx, cz))) {
          genChunk(cx, cz);
          if (++n >= 4) break outerGen;
        }
      }
    }
  }

  // build meshes, max 2 per frame, only when 4 neighbors have data
  n = 0;
  outerMesh:
  for (r = 0; r <= VIEW_MESH; r++) {
    for (dx = -r; dx <= r; dx++) {
      for (dz = -r; dz <= r; dz++) {
        if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;
        cx = pcx + dx; cz = pcz + dz;
        var c = chunks.get(key(cx, cz));
        if (c && !c.mesh && neighborsReady(cx, cz)) {
          c.mesh = buildMesh(cx, cz);
          if (++n >= 2) break outerMesh;
        }
      }
    }
  }

  // unload far chunks
  var toDelete = [];
  chunks.forEach(function (c, k) {
    var p = k.split(',');
    var cx2 = parseInt(p[0], 10), cz2 = parseInt(p[1], 10);
    if (Math.max(Math.abs(cx2 - pcx), Math.abs(cz2 - pcz)) > VIEW_UNLOAD) {
      removeMesh(c);
      toDelete.push(k);
    }
  });
  for (var i = 0; i < toDelete.length; i++) chunks.delete(toDelete[i]);
}

// ---------------------------------------------------------------- player
var player = {
  pos: new THREE.Vector3(8.5, 60, 8.5),
  vy: 0,
  onGround: false,
  yaw: 0,
  pitch: 0
};
var keys = {};
var locked = false;

function findSpawnY(x, z) {
  for (var y = HEIGHT - 1; y >= 0; y--)
    if (getBlock(x, y, z)) return y + 1;
  return 60;
}

function collides() {
  var p = player.pos;
  var x0 = Math.floor(p.x - P_HALF), x1 = Math.floor(p.x + P_HALF);
  var y0 = Math.floor(p.y), y1 = Math.floor(p.y + P_HEIGHT - 0.01);
  var z0 = Math.floor(p.z - P_HALF), z1 = Math.floor(p.z + P_HALF);
  for (var y = y0; y <= y1; y++)
    for (var x = x0; x <= x1; x++)
      for (var z = z0; z <= z1; z++)
        if (getBlock(x, y, z)) return true;
  return false;
}

function updatePlayer(dt) {
  var p = player.pos;

  // horizontal movement relative to yaw
  var mf = 0, ms = 0;
  if (keys['KeyW']) mf += 1;
  if (keys['KeyS']) mf -= 1;
  if (keys['KeyD']) ms += 1;
  if (keys['KeyA']) ms -= 1;
  var len = Math.sqrt(mf * mf + ms * ms);
  if (len > 0) { mf /= len; ms /= len; }
  var fx = -Math.sin(player.yaw), fz = -Math.cos(player.yaw);
  var rx = Math.cos(player.yaw), rz = -Math.sin(player.yaw);
  var mx = (fx * mf + rx * ms) * SPEED * dt;
  var mz = (fz * mf + rz * ms) * SPEED * dt;

  p.x += mx;
  if (collides()) p.x -= mx;
  p.z += mz;
  if (collides()) p.z -= mz;

  // gravity / jump
  var chunkHere = chunks.has(key(Math.floor(p.x / 16), Math.floor(p.z / 16)));
  if (chunkHere) {
    if (keys['Space'] && player.onGround) { player.vy = JUMP_V; player.onGround = false; }
    player.vy -= GRAVITY * dt;
    if (player.vy < -50) player.vy = -50;
    p.y += player.vy * dt;
    if (collides()) {
      p.y -= player.vy * dt;
      if (player.vy < 0) player.onGround = true;
      player.vy = 0;
    } else {
      player.onGround = false;
    }
  }

  // fell out of the world
  if (p.y < -20) {
    p.set(8.5, findSpawnY(8, 8) + 0.01, 8.5);
    player.vy = 0;
  }

  camera.position.set(p.x, p.y + P_EYE, p.z);
  camera.rotation.set(player.pitch, player.yaw, 0);
}

// ---------------------------------------------------------------- break / place
var raycaster = new THREE.Raycaster();
raycaster.far = REACH;
var center = new THREE.Vector2(0, 0);
var targetBlock = { x: 0, y: 0, z: 0, valid: false };

var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

function updateTarget() {
  targetBlock.valid = false;
  outline.visible = false;
  if (!locked) return;

  raycaster.setFromCamera(center, camera);
  var hits = raycaster.intersectObjects(meshList);
  if (!hits.length) return;

  var hit = hits[0];
  var p = hit.point, n = hit.face.normal;
  var bx = Math.floor(p.x - n.x * 0.5);
  var by = Math.floor(p.y - n.y * 0.5);
  var bz = Math.floor(p.z - n.z * 0.5);
  targetBlock.x = bx; targetBlock.y = by; targetBlock.z = bz;
  targetBlock.valid = true;
  outline.position.set(bx + 0.5, by + 0.5, bz + 0.5);
  outline.visible = true;
}

function editNeighbors(bx, by, bz) {
  var cx = Math.floor(bx / 16), cz = Math.floor(bz / 16);
  rebuildChunk(cx, cz);
  var lx = bx - cx * 16, lz = bz - cz * 16;
  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === 15) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === 15) rebuildChunk(cx, cz + 1);
}

function breakBlock() {
  if (!targetBlock.valid) return;
  var bx = targetBlock.x, by = targetBlock.y, bz = targetBlock.z;
  if (by <= 0) return; // bottom layer unbreakable
  if (getBlock(bx, by, bz) === 0) return;
  setBlock(bx, by, bz, 0);
  editNeighbors(bx, by, bz);
}

function placeBlock() {
  if (!targetBlock.valid) return;
  var p = raycaster.ray.origin; // not used, kept for clarity
  var hit = raycaster.intersectObjects(meshList)[0];
  if (!hit) return;
  var pt = hit.point, n = hit.face.normal;
  var bx = Math.floor(pt.x + n.x * 0.5);
  var by = Math.floor(pt.y + n.y * 0.5);
  var bz = Math.floor(pt.z + n.z * 0.5);
  if (by < 0 || by >= HEIGHT) return;
  if (getBlock(bx, by, bz) !== 0) return;

  // don't place inside the player
  var pp = player.pos;
  if (bx + 1 > pp.x - P_HALF && bx < pp.x + P_HALF &&
      by + 1 > pp.y && by < pp.y + P_HEIGHT &&
      bz + 1 > pp.z - P_HALF && bz < pp.z + P_HALF) return;

  setBlock(bx, by, bz, HOTBAR_BLOCKS[selected]);
  editNeighbors(bx, by, bz);
}

// ---------------------------------------------------------------- hotbar UI
var selected = 0;
var hotbarEl = document.getElementById('hotbar');
var slotEls = [];
for (var s = 0; s < 7; s++) {
  var slot = document.createElement('div');
  slot.className = 'slot';
  var col = BLOCK_COLORS[HOTBAR_BLOCKS[s]];
  slot.style.background = '#' + ('000000' + col.toString(16)).slice(-6);
  var num = document.createElement('span');
  num.textContent = (s + 1);
  slot.appendChild(num);
  hotbarEl.appendChild(slot);
  slotEls.push(slot);
}
function updateHotbar() {
  for (var i = 0; i < 7; i++) slotEls[i].className = 'slot' + (i === selected ? ' sel' : '');
}
updateHotbar();

// ---------------------------------------------------------------- clouds & water
var clouds = [];
var cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.75 });
for (var ci = 0; ci < 25; ci++) {
  var cw = 15 + Math.random() * 30;
  var cd = 15 + Math.random() * 30;
  var cloud = new THREE.Mesh(new THREE.BoxGeometry(cw, 3, cd), cloudMat);
  cloud.position.set(
    player.pos.x + (Math.random() - 0.5) * 700,
    88 + Math.random() * 6,
    player.pos.z + (Math.random() - 0.5) * 700
  );
  scene.add(cloud);
  clouds.push(cloud);
}

var water = new THREE.Mesh(
  new THREE.PlaneGeometry(1200, 1200),
  new THREE.MeshLambertMaterial({ color: 0x3d85e0, transparent: true, opacity: 0.55, depthWrite: false })
);
water.rotation.x = -Math.PI / 2;
water.position.y = WATER_Y;
scene.add(water);

function updateWorldObjects(dt) {
  for (var i = 0; i < clouds.length; i++) {
    var c = clouds[i];
    c.position.x += dt * 1.6;
    if (c.position.x - player.pos.x > 350) c.position.x -= 700;
    if (c.position.x - player.pos.x < -350) c.position.x += 700;
    if (c.position.z - player.pos.z > 350) c.position.z -= 700;
    if (c.position.z - player.pos.z < -350) c.position.z += 700;
  }
  water.position.x = player.pos.x;
  water.position.z = player.pos.z;
}

// ---------------------------------------------------------------- input
var overlay = document.getElementById('overlay');

overlay.addEventListener('click', function () {
  renderer.domElement.requestPointerLock();
});
document.addEventListener('pointerlockchange', function () {
  locked = (document.pointerLockElement === renderer.domElement);
  overlay.style.display = locked ? 'none' : 'flex';
  if (!locked) keys = {};
});
document.addEventListener('pointerlockerror', function () {
  overlay.style.display = 'flex';
});

document.addEventListener('mousemove', function (e) {
  if (!locked) return;
  player.yaw -= e.movementX * 0.002;
  player.pitch -= e.movementY * 0.002;
  var lim = Math.PI / 2 - 0.01;
  if (player.pitch > lim) player.pitch = lim;
  if (player.pitch < -lim) player.pitch = -lim;
});

document.addEventListener('mousedown', function (e) {
  if (!locked) return;
  if (e.button === 0) breakBlock();
  else if (e.button === 2) placeBlock();
});

document.addEventListener('contextmenu', function (e) { e.preventDefault(); });

document.addEventListener('wheel', function (e) {
  if (!locked) return;
  selected = (selected + (e.deltaY > 0 ? 1 : 6)) % 7;
  updateHotbar();
}, { passive: true });

document.addEventListener('keydown', function (e) {
  keys[e.code] = true;
  if (e.code === 'Space') e.preventDefault();
  if (e.code.indexOf('Digit') === 0) {
    var d = parseInt(e.code.slice(5), 10);
    if (d >= 1 && d <= 7) { selected = d - 1; updateHotbar(); }
  }
});
document.addEventListener('keyup', function (e) { keys[e.code] = false; });

window.addEventListener('resize', function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------------------------------------------------------------- boot
function init() {
  // pre-generate around spawn so the player has ground to stand on
  for (var r = 0; r <= 2; r++) {
    for (var dx = -r; dx <= r; dx++) {
      for (var dz = -r; dz <= r; dz++) {
        var cx = Math.floor(8 / 16) + dx, cz = Math.floor(8 / 16) + dz;
        if (!chunks.has(key(cx, cz))) genChunk(cx, cz);
      }
    }
  }
  for (var r2 = 0; r2 <= 1; r2++) {
    for (var dx2 = -r2; dx2 <= r2; dx2++) {
      for (var dz2 = -r2; dz2 <= r2; dz2++) {
        var cx2 = Math.floor(8 / 16) + dx2, cz2 = Math.floor(8 / 16) + dz2;
        var c = chunks.get(key(cx2, cz2));
        if (c && !c.mesh && neighborsReady(cx2, cz2)) c.mesh = buildMesh(cx2, cz2);
      }
    }
  }
  player.pos.set(8.5, findSpawnY(8, 8) + 0.01, 8.5);
}
init();

// ---------------------------------------------------------------- main loop
var lastTime = performance.now();
function loop() {
  requestAnimationFrame(loop);
  var now = performance.now();
  var dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;

  updatePlayer(dt);
  updateChunks();
  updateTarget();
  updateWorldObjects(dt);

  renderer.render(scene, camera);
}
loop();

})();
</script>
</body>
</html>
```