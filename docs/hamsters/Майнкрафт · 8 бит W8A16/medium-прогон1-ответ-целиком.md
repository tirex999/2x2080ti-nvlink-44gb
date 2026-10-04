

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>mc.html - Voxel Sandbox</title>
<style>
  html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; }
  canvas { display: block; }
  #overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.65); color: #fff;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-family: monospace; cursor: pointer; z-index: 10; text-align: center;
  }
  #overlay h1 { font-size: 48px; letter-spacing: 4px; margin: 0 0 20px 0; text-shadow: 3px 3px 0 #222; }
  #overlay .controls { font-size: 15px; line-height: 1.8; color: #ddd; margin-bottom: 24px; }
  #overlay .play { font-size: 22px; color: #ffdd55; animation: pulse 1.2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  #crosshair {
    position: fixed; left: 50%; top: 50%; transform: translate(-50%,-50%);
    width: 20px; height: 20px; pointer-events: none; z-index: 5;
  }
  #crosshair::before, #crosshair::after { content: ""; position: absolute; background: rgba(255,255,255,0.85); }
  #crosshair::before { left: 9px; top: 0; width: 2px; height: 20px; }
  #crosshair::after { left: 0; top: 9px; width: 20px; height: 2px; }
  #hotbar {
    position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; background: rgba(0,0,0,0.55); padding: 6px;
    border-radius: 6px; z-index: 5;
  }
  .slot {
    width: 44px; height: 44px; border: 2px solid rgba(255,255,255,0.35);
    border-radius: 4px; position: relative;
  }
  .slot.selected { border: 3px solid #ffffff; box-shadow: 0 0 6px rgba(255,255,255,0.8); }
  .slot span {
    position: absolute; top: 1px; left: 3px; font-family: monospace;
    font-size: 11px; color: #fff; text-shadow: 1px 1px 0 #000;
  }
</style>
</head>
<body>
<div id="overlay">
  <h1>VOXELCRAFT</h1>
  <div class="controls">
    WASD &mdash; move &nbsp;&nbsp; SPACE &mdash; jump<br>
    Mouse &mdash; look around<br>
    Left click &mdash; break block &nbsp;&nbsp; Right click &mdash; place block<br>
    1&ndash;7 or mouse wheel &mdash; choose block
  </div>
  <div class="play">Click to play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
"use strict";

/* ============================== Constants ============================== */
var CH = 16, CT = 80;
var COLORS = {
  1: 0x4caf50, 2: 0x795548, 3: 0x9e9e9e, 4: 0xe7d9a8,
  5: 0x8d6e63, 6: 0x2e7d32, 7: 0xffffff
};
var COLOR_RGB = {};
for (var k in COLORS) {
  var c = COLORS[k];
  COLOR_RGB[k] = [ ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255 ];
}
var HOTBAR_ITEMS = [
  { id: 1, color: "#4caf50" }, { id: 2, color: "#795548" }, { id: 3, color: "#9e9e9e" },
  { id: 4, color: "#e7d9a8" }, { id: 5, color: "#8d6e63" }, { id: 6, color: "#2e7d32" },
  { id: 7, color: "#ffffff" }
];
var SPAWN = new THREE.Vector3(8.5, 0, 8.5);

/* ============================ Deterministic noise ============================ */
function hashInt(n) {
  n = (n ^ 61) ^ (n >>> 16);
  n = n + (n << 3); n = n ^ (n >>> 4);
  n = Math.imul(n, 0x27d4eb2d);
  n = n ^ (n >>> 15);
  return (n >>> 0) / 4294967296;
}
function hash2(x, y) {
  return hashInt(Math.imul(x, 374761393) + Math.imul(y, 668265263));
}
function hash3(x, y, z) {
  return hashInt(Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1440662683));
}
function smoothstep(t) { return t * t * (3 - 2 * t); }

function noise2(x, y) {
  var xi = Math.floor(x), yi = Math.floor(y);
  var xf = x - xi, yf = y - yi;
  var a = hash2(xi, yi), b = hash2(xi + 1, yi),
      c = hash2(xi, yi + 1), d = hash2(xi + 1, yi + 1);
  var u = smoothstep(xf), v = smoothstep(yf);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var xf = x - xi, yf = y - yi, zf = z - zi;
  var c000 = hash3(xi, yi, zi),     c100 = hash3(xi + 1, yi, zi),
      c010 = hash3(xi, yi + 1, zi), c110 = hash3(xi + 1, yi + 1, zi),
      c001 = hash3(xi, yi, zi + 1), c101 = hash3(xi + 1, yi, zi + 1),
      c011 = hash3(xi, yi + 1, zi + 1), c111 = hash3(xi + 1, yi + 1, zi + 1);
  var u = smoothstep(xf), v = smoothstep(yf), w = smoothstep(zf);
  var x00 = c000 + (c100 - c000) * u;
  var x10 = c010 + (c110 - c010) * u;
  var x01 = c001 + (c101 - c001) * u;
  var x11 = c011 + (c111 - c011) * u;
  var y0 = x00 + (x10 - x00) * v;
  var y1 = x01 + (x11 - x01) * v;
  return y0 + (y1 - y0) * w;
}
function fbm2(x, y) {
  var amp = 1, freq = 1, sum = 0, norm = 0;
  for (var i = 0; i < 4; i++) {
    sum += noise2(x * freq, y * freq) * amp;
    norm += amp; amp *= 0.5; freq *= 2;
  }
  return sum / norm;
}
function fbm3(x, y, z) {
  var amp = 1, freq = 1, sum = 0, norm = 0;
  for (var i = 0; i < 4; i++) {
    sum += noise3(x * freq, y * freq, z * freq) * amp;
    norm += amp; amp *= 0.5; freq *= 2;
  }
  return sum / norm;
}

/* ================================ Terrain ================================ */
function colHeight(x, z) {
  var m = fbm2(x * 0.004, z * 0.004);
  var h = fbm2(x * 0.02, z * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}
function localIdx(x, y, z) { return (y * CH + z) * CH + x; }

function genData(cx, cz) {
  var data = new Uint8Array(CH * CH * CT);
  var lx, lz, y, wx, wz, H, surf, sub, id;
  for (lz = 0; lz < CH; lz++) {
    for (lx = 0; lx < CH; lx++) {
      wx = cx * CH + lx; wz = cz * CH + lz;
      H = colHeight(wx, wz);
      if (H >= CT) H = CT - 1;
      if (H >= 46) surf = 7;
      else if (H >= 37) surf = 3;
      else if (H <= 16) surf = 4;
      else surf = 1;
      if (H <= 16) sub = 4;
      else if (H >= 37) sub = 3;
      else sub = 2;
      for (y = 0; y <= H; y++) {
        if (y === 0) id = 3;
        else if (y < H - 3) id = 3;
        else if (y < H) id = sub;
        else id = surf;
        if (y > 2 && y < H - 1 && fbm3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) id = 0;
        data[localIdx(lx, y, lz)] = id;
      }
    }
  }
  // Trees
  function putIfAir(x, y, z, v) {
    if (x < 0 || x >= CH || y < 0 || y >= CT || z < 0 || z >= CH) return;
    if (data[localIdx(x, y, z)] === 0) data[localIdx(x, y, z)] = v;
  }
  for (lz = 0; lz < CH; lz++) {
    for (lx = 0; lx < CH; lx++) {
      wx = cx * CH + lx; wz = cz * CH + lz;
      H = colHeight(wx, wz);
      if (H <= 16 || H >= 37) continue;          // only on grass
      if (H + 6 >= CT) continue;
      if (data[localIdx(lx, H, lz)] !== 1) continue;
      if (lx < 2 || lx > 13 || lz < 2 || lz > 13) continue; // trunk + canopy fit in chunk
      if (hash2(wx, wz) >= 0.02) continue;
      for (y = 1; y <= 4; y++) data[localIdx(lx, H + y, lz)] = 5;   // trunk
      var ly, dx, dz2;
      for (ly = H + 3; ly <= H + 4; ly++)          // 5x5 twice
        for (dx = -2; dx <= 2; dx++)
          for (dz2 = -2; dz2 <= 2; dz2++)
            putIfAir(lx + dx, ly, lz + dz2, 6);
      for (dx = -1; dx <= 1; dx++)                 // 3x3
        for (dz2 = -1; dz2 <= 1; dz2++)
          putIfAir(lx + dx, H + 5, lz + dz2, 6);
      putIfAir(lx, H + 6, lz, 6);                  // top
    }
  }
  return data;
}

/* ============================ Global block access ============================ */
var chunks = new Map();

function getBlock(x, y, z) {
  if (y < 0 || y >= CT) return 0;
  var cx = Math.floor(x / CH), cz = Math.floor(z / CH);
  var c = chunks.get(cx + "," + cz);
  if (!c) return 0;
  return c.data[localIdx(x - cx * CH, y, z - cz * CH)];
}
function setBlock(x, y, z, id) {
  if (y < 0 || y >= CT) return;
  var cx = Math.floor(x / CH), cz = Math.floor(z / CH);
  var c = chunks.get(cx + "," + cz);
  if (!c) return;
  c.data[localIdx(x - cx * CH, y, z - cz * CH)] = id;
}

/* ================================ Scene setup ================================ */
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = "YXZ";

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.5, 1.0, 0.3);
scene.add(sun);

var voxelMat = new THREE.MeshLambertMaterial({ vertexColors: true });

/* ================================ Meshing ================================ */
var FACES = [
  { dir: [ 1, 0, 0], corners: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]], shade: 0.8 },
  { dir: [-1, 0, 0], corners: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]], shade: 0.8 },
  { dir: [ 0, 1, 0], corners: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]], shade: 1.0 },
  { dir: [ 0,-1, 0], corners: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], shade: 0.55 },
  { dir: [ 0, 0, 1], corners: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], shade: 0.8 },
  { dir: [ 0, 0,-1], corners: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]], shade: 0.8 }
];
var TRI = [0, 1, 2, 0, 2, 3];

var chunkMeshes = [];

function buildChunkMesh(chunk) {
  var pos = [], nor = [], col = [];
  var cx = chunk.cx, cz = chunk.cz;
  for (var y = 0; y < CT; y++) {
    for (var lz = 0; lz < CH; lz++) {
      for (var lx = 0; lx < CH; lx++) {
        var id = chunk.data[localIdx(lx, y, lz)];
        if (!id) continue;
        var wx = cx * CH + lx, wz = cz * CH + lz;
        var rgb = COLOR_RGB[id];
        for (var f = 0; f < 6; f++) {
          var face = FACES[f];
          if (getBlock(wx + face.dir[0], y + face.dir[1], wz + face.dir[2]) !== 0) continue;
          for (var t = 0; t < 6; t++) {
            var cr = face.corners[TRI[t]];
            pos.push(wx + cr[0], y + cr[1], wz + cr[2]);
            nor.push(face.dir[0], face.dir[1], face.dir[2]);
            col.push(rgb[0] * face.shade, rgb[1] * face.shade, rgb[2] * face.shade);
          }
        }
      }
    }
  }
  var geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  var mesh = new THREE.Mesh(geo, voxelMat);
  mesh.position.set(0, 0, 0);
  scene.add(mesh);
  chunk.mesh = mesh;
  chunkMeshes.push(mesh);
}

function rebuildChunk(cx, cz) {
  var c = chunks.get(cx + "," + cz);
  if (!c) return;
  if (c.mesh) {
    scene.remove(c.mesh);
    c.mesh.geometry.dispose();
    var i = chunkMeshes.indexOf(c.mesh);
    if (i >= 0) chunkMeshes.splice(i, 1);
  }
  buildChunkMesh(c);
}

/* ============================ World streaming ============================ */
function updateWorld() {
  var pcx = Math.floor(player.pos.x / CH), pcz = Math.floor(player.pos.z / CH);
  var dx, dz, k, c;

  var gen = 0;
  for (dz = -5; dz <= 5 && gen < 4; dz++) {
    for (dx = -5; dx <= 5 && gen < 4; dx++) {
      k = (pcx + dx) + "," + (pcz + dz);
      if (!chunks.has(k)) {
        chunks.set(k, { cx: pcx + dx, cz: pcz + dz, data: genData(pcx + dx, pcz + dz), mesh: null });
        gen++;
      }
    }
  }

  var built = 0;
  for (dz = -4; dz <= 4 && built < 2; dz++) {
    for (dx = -4; dx <= 4 && built < 2; dx++) {
      var ccx = pcx + dx, ccz = pcz + dz;
      k = ccx + "," + ccz;
      c = chunks.get(k);
      if (!c || c.mesh) continue;
      if (chunks.has((ccx - 1) + "," + ccz) && chunks.has((ccx + 1) + "," + ccz) &&
          chunks.has(ccx + "," + (ccz - 1)) && chunks.has(ccx + "," + (ccz + 1))) {
        buildChunkMesh(c);
        built++;
      }
    }
  }

  for (var it = Array.from(chunks.keys()), j = 0; j < it.length; j++) {
    c = chunks.get(it[j]);
    if (Math.max(Math.abs(c.cx - pcx), Math.abs(c.cz - pcz)) > 7) {
      if (c.mesh) {
        scene.remove(c.mesh);
        c.mesh.geometry.dispose();
        var mi = chunkMeshes.indexOf(c.mesh);
        if (mi >= 0) chunkMeshes.splice(mi, 1);
      }
      chunks.delete(it[j]);
    }
  }
}

/* ================================ Player ================================ */
var player = {
  pos: new THREE.Vector3(SPAWN.x, colHeight(8, 8) + 1, SPAWN.z),
  vel: new THREE.Vector3(0, 0, 0),
  yaw: 0, pitch: 0,
  onGround: false
};
SPAWN.y = player.pos.y;

var keys = {};
function collides(px, py, pz) {
  var minX = Math.floor(px - 0.3), maxX = Math.floor(px + 0.3);
  var minY = Math.floor(py),     maxY = Math.floor(py + 1.8);
  var minZ = Math.floor(pz - 0.3), maxZ = Math.floor(pz + 0.3);
  for (var x = minX; x <= maxX; x++)
    for (var y = minY; y <= maxY; y++)
      for (var z = minZ; z <= maxZ; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}

function updatePlayer(dt) {
  player.vel.y -= 25 * dt;
  if (player.vel.y < -50) player.vel.y = -50;

  var fwd = 0, str = 0;
  if (keys["KeyW"]) fwd += 1;
  if (keys["KeyS"]) fwd -= 1;
  if (keys["KeyD"]) str += 1;
  if (keys["KeyA"]) str -= 1;
  var sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
  var mx = (-sin * fwd + cos * str) * 5.5 * dt;
  var mz = (-cos * fwd - sin * str) * 5.5 * dt;

  var nx = player.pos.x + mx;
  if (!collides(nx, player.pos.y, player.pos.z)) player.pos.x = nx;
  var nz = player.pos.z + mz;
  if (!collides(player.pos.x, player.pos.y, nz)) player.pos.z = nz;

  if (keys["Space"] && player.onGround) {
    player.vel.y = 8.5;
    player.onGround = false;
  }
  var ny = player.pos.y + player.vel.y * dt;
  if (!collides(player.pos.x, ny, player.pos.z)) {
    player.pos.y = ny;
    player.onGround = false;
  } else {
    if (player.vel.y < 0) player.onGround = true;
    player.vel.y = 0;
  }

  if (player.pos.y < -20) {
    player.pos.set(SPAWN.x, SPAWN.y, SPAWN.z);
    player.vel.set(0, 0, 0);
  }

  camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
  camera.rotation.y = player.yaw;
  camera.rotation.x = player.pitch;
}

/* ============================ Break / place ============================ */
var raycaster = new THREE.Raycaster();
raycaster.far = 6;
var centerVec = new THREE.Vector2(0, 0);
var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

var target = null;

function updateTarget() {
  raycaster.setFromCamera(centerVec, camera);
  var hits = raycaster.intersectObjects(chunkMeshes);
  if (hits.length > 0) {
    var h = hits[0];
    var n = h.face.normal;
    var p = h.point;
    target = {
      x: Math.floor(p.x - n.x * 0.5),
      y: Math.floor(p.y - n.y * 0.5),
      z: Math.floor(p.z - n.z * 0.5),
      px: Math.floor(p.x + n.x * 0.5),
      py: Math.floor(p.y + n.y * 0.5),
      pz: Math.floor(p.z + n.z * 0.5)
    };
    outline.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
    outline.visible = true;
  } else {
    target = null;
    outline.visible = false;
  }
}

function overlapsPlayer(bx, by, bz) {
  return (bx + 1 > player.pos.x - 0.3 && bx < player.pos.x + 0.3 &&
          by + 1 > player.pos.y && by < player.pos.y + 1.8 &&
          bz + 1 > player.pos.z - 0.3 && bz < player.pos.z + 0.3);
}

function rebuildAround(bx, by, bz) {
  var cx = Math.floor(bx / CH), cz = Math.floor(bz / CH);
  var lx = bx - cx * CH, lz = bz - cz * CH;
  rebuildChunk(cx, cz);
  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === CH - 1) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === CH - 1) rebuildChunk(cx, cz + 1);
}

function doBreak() {
  if (!target || target.y <= 0) return;
  if (getBlock(target.x, target.y, target.z) === 0) return;
  setBlock(target.x, target.y, target.z, 0);
  rebuildAround(target.x, target.y, target.z);
}

function doPlace() {
  if (!target) return;
  var bx = target.px, by = target.py, bz = target.pz;
  if (by < 0 || by >= CT) return;
  if (getBlock(bx, by, bz) !== 0) return;
  if (overlapsPlayer(bx, by, bz)) return;
  setBlock(bx, by, bz, HOTBAR_ITEMS[selected].id);
  rebuildAround(bx, by, bz);
}

/* ================================ Input ================================ */
var overlay = document.getElementById("overlay");
var canvas = renderer.domElement;

overlay.addEventListener("click", function () {
  if (document.pointerLockElement !== canvas) canvas.requestPointerLock();
});
document.addEventListener("pointerlockchange", function () {
  overlay.style.display = (document.pointerLockElement === canvas) ? "none" : "flex";
});
document.addEventListener("mousemove", function (e) {
  if (document.pointerLockElement !== canvas) return;
  player.yaw -= e.movementX * 0.002;
  player.pitch -= e.movementY * 0.002;
  var lim = Math.PI / 2 - 0.01;
  if (player.pitch > lim) player.pitch = lim;
  if (player.pitch < -lim) player.pitch = -lim;
});
document.addEventListener("mousedown", function (e) {
  if (document.pointerLockElement !== canvas) return;
  if (e.button === 0) doBreak();
  else if (e.button === 2) doPlace();
});
document.addEventListener("contextmenu", function (e) { e.preventDefault(); });
window.addEventListener("keydown", function (e) {
  keys[e.code] = true;
  if (e.code === "Space") e.preventDefault();
  if (e.code >= "Digit1" && e.code <= "Digit7") {
    setSelected(parseInt(e.code.charAt(5), 10) - 1);
  }
});
window.addEventListener("keyup", function (e) { keys[e.code] = false; });
window.addEventListener("wheel", function (e) {
  if (document.pointerLockElement !== canvas) return;
  setSelected(selected + (e.deltaY > 0 ? 1 : -1));
});
window.addEventListener("resize", function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ================================ Hotbar UI ================================ */
var selected = 0;
var hotbarEl = document.getElementById("hotbar");
var slotEls = [];
HOTBAR_ITEMS.forEach(function (item, i) {
  var s = document.createElement("div");
  s.className = "slot";
  s.style.background = item.color;
  var num = document.createElement("span");
  num.textContent = String(i + 1);
  s.appendChild(num);
  hotbarEl.appendChild(s);
  slotEls.push(s);
});
function setSelected(i) {
  selected = ((i % 7) + 7) % 7;
  for (var j = 0; j < slotEls.length; j++)
    slotEls[j].className = "slot" + (j === selected ? " selected" : "");
}
setSelected(0);

/* ============================ Sky: clouds & water ============================ */
var clouds = [];
for (var ci = 0; ci < 25; ci++) {
  var cg = new THREE.BoxGeometry(14 + Math.random() * 18, 2, 10 + Math.random() * 14);
  var cm = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.8, depthWrite: false });
  var cloud = new THREE.Mesh(cg, cm);
  cloud.position.set(
    player.pos.x + (Math.random() - 0.5) * 600,
    88 + Math.random() * 8,
    player.pos.z + (Math.random() - 0.5) * 600
  );
  cloud.userData.speed = 1.5 + Math.random() * 2.5;
  scene.add(cloud);
  clouds.push(cloud);
}
function updateClouds(dt) {
  for (var i = 0; i < clouds.length; i++) {
    var cl = clouds[i];
    cl.position.x += cl.userData.speed * dt;
    if (cl.position.x - player.pos.x > 300) cl.position.x -= 600;
    if (cl.position.x - player.pos.x < -300) cl.position.x += 600;
    if (cl.position.z - player.pos.z > 300) cl.position.z -= 600;
    if (cl.position.z - player.pos.z < -300) cl.position.z += 600;
  }
}

var waterGeo = new THREE.PlaneGeometry(400, 400);
waterGeo.rotateX(-Math.PI / 2);
var waterMat = new THREE.MeshLambertMaterial({ color: 0x3f76e4, transparent: true, opacity: 0.6 });
var water = new THREE.Mesh(waterGeo, waterMat);
water.position.set(player.pos.x, 14.3, player.pos.z);
scene.add(water);

/* ============================ Pre-generate spawn area ============================ */
var guard = 0;
while (!chunks.has("0,0") || !chunks.get("0,0").mesh) {
  updateWorld();
  if (++guard > 500) break;
}

/* ================================ Main loop ================================ */
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
  water.position.set(player.pos.x, 14.3, player.pos.z);

  renderer.render(scene, camera);
}
animate();

})();
</script>
</body>
</html>
```