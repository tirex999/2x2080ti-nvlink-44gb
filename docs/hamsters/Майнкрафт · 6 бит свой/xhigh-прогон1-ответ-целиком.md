

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Voxelcraft — mc.html</title>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #87ceeb; }
  canvas { display: block; }

  /* ---------- crosshair ---------- */
  #crosshair { position: fixed; left: 50%; top: 50%; width: 0; height: 0; pointer-events: none; z-index: 5; }
  #crosshair::before, #crosshair::after {
    content: ""; position: absolute; background: rgba(255,255,255,.9);
    box-shadow: 0 0 3px rgba(0,0,0,.9);
  }
  #crosshair::before { width: 20px; height: 2px; margin: -1px 0 0 -10px; }
  #crosshair::after  { width: 2px; height: 20px; margin: -10px 0 0 -1px; }

  /* ---------- hotbar ---------- */
  #hotbar {
    position: fixed; left: 50%; bottom: 14px; transform: translateX(-50%);
    display: flex; gap: 6px; padding: 7px;
    background: rgba(0,0,0,.55); border-radius: 10px; z-index: 5;
  }
  .slot {
    width: 48px; height: 48px; position: relative;
    border: 3px solid rgba(255,255,255,.3); border-radius: 6px;
    box-shadow: inset -6px -6px 0 rgba(0,0,0,.2), inset 6px 6px 0 rgba(255,255,255,.18);
    transition: transform .08s ease, border-color .08s ease;
  }
  .slot:hover { transform: translateY(-3px); }
  .slot.sel { border-color: #fff; transform: translateY(-4px); }
  .slot span {
    position: absolute; top: 2px; left: 4px; pointer-events: none;
    font: 700 11px/1 "Courier New", monospace; color: #fff;
    text-shadow: 1px 1px 0 rgba(0,0,0,.9);
  }

  /* ---------- start overlay ---------- */
  #overlay {
    position: fixed; inset: 0; z-index: 10;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; color: #fff; cursor: pointer; user-select: none;
    font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    background: radial-gradient(ellipse at 50% 40%, rgba(25,45,70,.55) 0%, rgba(4,10,20,.88) 100%);
  }
  #overlay h1 {
    margin: 0; font-family: "Courier New", monospace; font-weight: 900;
    font-size: clamp(42px, 9vw, 78px); letter-spacing: 8px;
    text-shadow: 5px 5px 0 rgba(0,0,0,.45);
  }
  #overlay .swatches { display: flex; gap: 7px; margin: 16px 0 4px; }
  #overlay .swatches i {
    display: block; width: 16px; height: 16px; border-radius: 3px;
    box-shadow: inset -4px -4px 0 rgba(0,0,0,.25), inset 4px 4px 0 rgba(255,255,255,.28);
  }
  #overlay .sub { margin: 0 0 24px; font-size: 14px; letter-spacing: 3px; color: #bfe3ff; }
  #overlay .panel {
    background: rgba(0,0,0,.45); border: 1px solid rgba(255,255,255,.16);
    border-radius: 12px; padding: 14px 28px; font-size: 14px; line-height: 2.1;
  }
  #overlay .panel b {
    font-family: "Courier New", monospace; font-size: 12px; color: #ffd54f;
    background: rgba(0,0,0,.5); border: 1px solid rgba(255,213,79,.35);
    border-radius: 4px; padding: 2px 7px;
  }
  #overlay .play { margin-top: 28px; font-size: 20px; font-weight: 700; letter-spacing: 4px; animation: pulse 1.4s ease-in-out infinite; }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .3; } }
</style>
</head>
<body>

<div id="crosshair"></div>
<div id="hotbar"></div>

<div id="overlay">
  <h1>VOXELCRAFT</h1>
  <div class="swatches">
    <i style="background:#4caf50"></i><i style="background:#795548"></i><i style="background:#9e9e9e"></i><i style="background:#e7d9a8"></i><i style="background:#8d6e63"></i><i style="background:#2e7d32"></i><i style="background:#ffffff"></i>
  </div>
  <p class="sub">AN ENDLESS BLOCKY WORLD</p>
  <div class="panel">
    <b>W A S D</b> move&nbsp;&nbsp;&nbsp;<b>SPACE</b> jump&nbsp;&nbsp;&nbsp;<b>MOUSE</b> look around<br>
    <b>LEFT CLICK</b> break block&nbsp;&nbsp;&nbsp;<b>RIGHT CLICK</b> place block<br>
    <b>1 &ndash; 7</b> / <b>SCROLL</b> choose block&nbsp;&nbsp;&nbsp;<b>ESC</b> release mouse
  </div>
  <div class="play">&#9654; CLICK TO PLAY</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* =====================================================================
   VOXELCRAFT — a single-file Minecraft-style voxel sandbox (three.js r128)
   ===================================================================== */

/* ============================== constants ============================= */
var CS = 16, CH = 80;                          // chunk footprint, world height
var GEN_R = 5, MESH_R = 4, UNLOAD_R = 7;       // streaming radii
var GRAV = 25, JUMP_V = 8.5, WALK = 5.5;       // physics
var PW = 0.3, PH = 1.8, EYE = 1.62;            // player half-width, height, eye
var WATER_Y = 14.3, REACH = 6;                 // water level, tool reach

var BLOCKS = {
  1: { name: "Grass",  hex: 0x4caf50 },
  2: { name: "Dirt",   hex: 0x795548 },
  3: { name: "Stone",  hex: 0x9e9e9e },
  4: { name: "Sand",   hex: 0xe7d9a8 },
  5: { name: "Wood",   hex: 0x8d6e63 },
  6: { name: "Leaves", hex: 0x2e7d32 },
  7: { name: "Snow",   hex: 0xffffff }
};
var HOTBAR = [1, 2, 3, 4, 5, 6, 7];
var RGB = {};
Object.keys(BLOCKS).forEach(function (k) {
  var h = BLOCKS[k].hex;
  RGB[k] = [((h >> 16) & 255) / 255, ((h >> 8) & 255) / 255, (h & 255) / 255];
});

/* ======================= deterministic value noise ===================== */
function hash2(x, y) {
  var h = (Math.imul(x, 374761393) + Math.imul(y, 668265263)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function hash3(x, y, z) {
  var h = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1440662683)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function smooth(t) { return t * t * (3 - 2 * t); }

function noise2(x, y) {
  var xi = Math.floor(x), yi = Math.floor(y);
  var u = smooth(x - xi), v = smooth(y - yi);
  var a = hash2(xi, yi),     b = hash2(xi + 1, yi);
  var c = hash2(xi, yi + 1), d = hash2(xi + 1, yi + 1);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var u = smooth(x - xi), v = smooth(y - yi), w = smooth(z - zi);
  var c000 = hash3(xi, yi, zi),       c100 = hash3(xi + 1, yi, zi);
  var c010 = hash3(xi, yi + 1, zi),   c110 = hash3(xi + 1, yi + 1, zi);
  var c001 = hash3(xi, yi, zi + 1),   c101 = hash3(xi + 1, yi, zi + 1);
  var c011 = hash3(xi, yi + 1, zi + 1), c111 = hash3(xi + 1, yi + 1, zi + 1);
  var x00 = c000 + (c100 - c000) * u, x10 = c010 + (c110 - c010) * u;
  var x01 = c001 + (c101 - c001) * u, x11 = c011 + (c111 - c011) * u;
  var y0 = x00 + (x10 - x00) * v,     y1 = x01 + (x11 - x01) * v;
  return y0 + (y1 - y0) * w;
}
function fractal2(x, y) {                       // 4 octaves
  var t = 0, amp = 1, f = 1, n = 0;
  for (var i = 0; i < 4; i++) { t += noise2(x * f, y * f) * amp; n += amp; amp *= 0.5; f *= 2; }
  return t / n;
}
function fractal3(x, y, z) {                    // 3 octaves (caves)
  var t = 0, amp = 1, f = 1, n = 0;
  for (var i = 0; i < 3; i++) { t += noise3(x * f, y * f, z * f) * amp; n += amp; amp *= 0.5; f *= 2; }
  return t / n;
}

/* ================================ chunks =============================== */
var CHUNKS = new Map();        // "cx,cz" -> { cx, cz, data: Uint8Array, mesh }
var chunkMeshes = [];          // every live chunk mesh (raycast targets)

function ckey(cx, cz) { return cx + "," + cz; }
function getChunk(cx, cz) { return CHUNKS.get(ckey(cx, cz)); }

function getBlock(x, y, z) {
  if (y < 0 || y >= CH) return 0;
  var cx = Math.floor(x / CS), cz = Math.floor(z / CS);
  var c = CHUNKS.get(ckey(cx, cz));
  if (!c) return 0;
  return c.data[(x - cx * CS) + (z - cz * CS) * CS + y * CS * CS];
}
function setBlock(x, y, z, id) {
  if (y < 0 || y >= CH) return;
  var cx = Math.floor(x / CS), cz = Math.floor(z / CS);
  var c = CHUNKS.get(ckey(cx, cz));
  if (!c) return;
  c.data[(x - cx * CS) + (z - cz * CS) * CS + y * CS * CS] = id;
}

/* =============================== terrain =============================== */
function putLeaves(data, lx, lz, y, r) {        // (2r+1) x (2r+1) canopy layer
  if (y < 0 || y >= CH) return;
  for (var dx = -r; dx <= r; dx++)
    for (var dz = -r; dz <= r; dz++) {
      var tx = lx + dx, tz = lz + dz;
      if (tx < 0 || tx >= CS || tz < 0 || tz >= CS) continue;
      var i = tx + tz * CS + y * CS * CS;
      if (data[i] === 0) data[i] = 6;           // only into air
    }
}

function generateData(cx, cz) {
  var data = new Uint8Array(CS * CS * CH);
  for (var lz = 0; lz < CS; lz++) {
    for (var lx = 0; lx < CS; lx++) {
      var wx = cx * CS + lx, wz = cz * CS + lz;
      var m  = fractal2(wx * 0.004, wz * 0.004);
      var hf = fractal2(wx * 0.02,  wz * 0.02);
      var H = Math.floor(5 + m * m * 58 + hf * 10);
      if (H >= CH) H = CH - 1;

      var surf, mid;
      if (H >= 46)      { surf = 7; mid = 3; }  // snowy peak
      else if (H >= 37) { surf = 3; mid = 3; }  // rocky mountain
      else if (H <= 16) { surf = 4; mid = 4; }  // beach / seabed
      else              { surf = 1; mid = 2; }  // grassland

      for (var y = 0; y <= H; y++) {
        var id;
        if (y === H) id = surf;
        else if (y >= H - 3) id = mid;
        else id = 3;                                       // stone (y=0 unbreakable)
        if (y >= 3 && y <= H - 2 &&
            fractal3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) id = 0;   // caves
        data[lx + lz * CS + y * CS * CS] = id;
      }

      // trees on grass
      if (surf === 1 && data[lx + lz * CS + H * CS * CS] === 1 && hash2(wx, wz) < 0.02) {
        for (var t = 1; t <= 4; t++) {                    // 4 wood up
          var ty = H + t;
          if (ty < CH) data[lx + lz * CS + ty * CS * CS] = 5;
        }
        putLeaves(data, lx, lz, H + 4, 2);                // 5x5
        putLeaves(data, lx, lz, H + 5, 2);                // 5x5
        putLeaves(data, lx, lz, H + 6, 1);                // 3x3
        putLeaves(data, lx, lz, H + 7, 0);                // 1 on top
      }
    }
  }
  return data;
}

function ensureData(cx, cz) {
  var k = ckey(cx, cz);
  if (!CHUNKS.has(k))
    CHUNKS.set(k, { cx: cx, cz: cz, data: generateData(cx, cz), mesh: null });
}

/* =============================== meshing =============================== */
/* face table: outward normal, brightness, 4 CCW corners (world offsets)   */
var FACES = [
  { d: [ 1, 0, 0], s: 0.8,  c: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]] },
  { d: [-1, 0, 0], s: 0.8,  c: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
  { d: [ 0, 1, 0], s: 1.0,  c: [[0,1,0],[0,1,1],[1,1,1],[1,1,0]] },
  { d: [ 0,-1, 0], s: 0.55, c: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { d: [ 0, 0, 1], s: 0.8,  c: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]] },
  { d: [ 0, 0,-1], s: 0.8,  c: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]] }
];

var scene, camera, renderer, sharedMat;

function buildMesh(c) {
  var pos = [], nor = [], col = [], idx = [];
  var ox = c.cx * CS, oz = c.cz * CS, data = c.data;
  var nE = getChunk(c.cx + 1, c.cz), nW = getChunk(c.cx - 1, c.cz);
  var nN = getChunk(c.cx, c.cz + 1), nS = getChunk(c.cx, c.cz - 1);

  /* neighbor probe: fast in-chunk path, global rule (missing = air) at borders */
  function nb(wx, wy, wz) {
    if (wy < 0 || wy >= CH) return 0;
    var lx = wx - ox, lz = wz - oz;
    if (lx >= 0 && lx < CS && lz >= 0 && lz < CS) return data[lx + lz * CS + wy * CS * CS];
    if (lx === -1) return nW ? nW.data[(CS - 1) + lz * CS + wy * CS * CS] : 0;
    if (lx === CS) return nE ? nE.data[lz * CS + wy * CS * CS] : 0;
    if (lz === -1) return nS ? nS.data[lx + (CS - 1) * CS + wy * CS * CS] : 0;
    if (lz === CS) return nN ? nN.data[lx + wy * CS * CS] : 0;
    return 0;
  }

  for (var y = 0; y < CH; y++)
    for (var lz = 0; lz < CS; lz++)
      for (var lx = 0; lx < CS; lx++) {
        var id = data[lx + lz * CS + y * CS * CS];
        if (!id) continue;
        var wx = ox + lx, wz = oz + lz, rgb = RGB[id];
        for (var f = 0; f < 6; f++) {
          var fc = FACES[f];
          if (nb(wx + fc.d[0], y + fc.d[1], wz + fc.d[2]) !== 0) continue;
          var base = pos.length / 3;
          for (var i = 0; i < 4; i++) {
            pos.push(wx + fc.c[i][0], y + fc.c[i][1], wz + fc.c[i][2]);
            nor.push(fc.d[0], fc.d[1], fc.d[2]);
            col.push(rgb[0] * fc.s, rgb[1] * fc.s, rgb[2] * fc.s);
          }
          idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
        }
      }

  var geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("normal",   new THREE.Float32BufferAttribute(nor, 3));
  geo.setAttribute("color",    new THREE.Float32BufferAttribute(col, 3));
  geo.setIndex(idx);
  var mesh = new THREE.Mesh(geo, sharedMat);   // world-space verts, mesh at origin
  c.mesh = mesh;
  chunkMeshes.push(mesh);
  scene.add(mesh);
}

function rebuildChunk(cx, cz) {
  var c = getChunk(cx, cz);
  if (!c || !c.mesh) return;
  scene.remove(c.mesh);
  var i = chunkMeshes.indexOf(c.mesh);
  if (i >= 0) chunkMeshes.splice(i, 1);
  c.mesh.geometry.dispose();
  c.mesh = null;
  buildMesh(c);
}

/* ============================= scene setup ============================= */
scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = "YXZ";

renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.6, 1, 0.4);
scene.add(sun);

sharedMat = new THREE.MeshLambertMaterial({ vertexColors: true });

/* water: one big translucent plane, re-centered on the player each frame */
var water = new THREE.Mesh(
  new THREE.PlaneGeometry(400, 400),
  new THREE.MeshLambertMaterial({
    color: 0x3a6fd8, transparent: true, opacity: 0.55,
    side: THREE.DoubleSide, depthWrite: false
  })
);
water.rotation.x = -Math.PI / 2;
scene.add(water);

/* drifting clouds */
var cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 });
var clouds = [];
for (var ci = 0; ci < 25; ci++) {
  var cw = 10 + hash2(ci * 7 + 1, 913) * 20;
  var cd = 7  + hash2(ci * 7 + 2, 914) * 14;
  var cm = new THREE.Mesh(new THREE.BoxGeometry(cw, 1.5, cd), cloudMat);
  cm.position.set(
    (hash2(ci * 7 + 3, 915) - 0.5) * 320,
    88 + hash2(ci * 7 + 4, 916) * 10,
    (hash2(ci * 7 + 5, 917) - 0.5) * 320
  );
  scene.add(cm);
  clouds.push({ m: cm, sp: 1.2 + hash2(ci * 7 + 6, 918) * 2 });
}

/* targeted-block outline */
var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

/* ================================ player =============================== */
var player = { x: 8, y: 40, z: 8, vx: 0, vy: 0, vz: 0, onGround: false };
var spawn  = { x: 8, y: 40, z: 8 };
var yaw = 0, pitch = 0;
var keys = {};

function findSpawn() {
  ensureData(0, 0);
  for (var y = CH - 1; y >= 0; y--) {
    if (getBlock(8, y, 8) !== 0) {
      var sy = y + 1;
      while (sy < CH - 2 && boxCollides(8, sy, 8)) sy++;   // clear any tree canopy
      spawn.y = sy;
      break;
    }
  }
}
function respawn() {
  player.x = spawn.x; player.y = spawn.y; player.z = spawn.z;
  player.vx = player.vy = player.vz = 0;
  player.onGround = false;
}

function boxCollides(px, py, pz) {
  var x0 = Math.floor(px - PW), x1 = Math.floor(px + PW);
  var y0 = Math.floor(py),     y1 = Math.floor(py + PH);
  var z0 = Math.floor(pz - PW), z1 = Math.floor(pz + PW);
  for (var by = y0; by <= y1; by++)
    for (var bz = z0; bz <= z1; bz++)
      for (var bx = x0; bx <= x1; bx++)
        if (getBlock(bx, by, bz) !== 0) return true;
  return false;
}

function stepPhysics(dt) {
  var fx = 0, fz = 0, s = Math.sin(yaw), c = Math.cos(yaw);
  if (keys["KeyW"]) { fx -= s; fz -= c; }
  if (keys["KeyS"]) { fx += s; fz += c; }
  if (keys["KeyA"]) { fx -= c; fz += s; }
  if (keys["KeyD"]) { fx += c; fz -= s; }
  var l = Math.sqrt(fx * fx + fz * fz);
  if (l > 0) { fx = fx / l * WALK; fz = fz / l * WALK; }
  player.vx = fx; player.vz = fz;

  player.vy -= GRAV * dt;
  if (player.vy < -50) player.vy = -50;
  if (keys["Space"] && player.onGround) { player.vy = JUMP_V; player.onGround = false; }

  /* axis-separated movement: move, revert on overlap */
  var nx = player.x + player.vx * dt;
  if (!boxCollides(nx, player.y, player.z)) player.x = nx; else player.vx = 0;

  var nz = player.z + player.vz * dt;
  if (!boxCollides(player.x, player.y, nz)) player.z = nz; else player.vz = 0;

  var ny = player.y + player.vy * dt;
  if (!boxCollides(player.x, ny, player.z)) { player.y = ny; player.onGround = false; }
  else { if (player.vy < 0) player.onGround = true; player.vy = 0; }

  if (player.y < -20) respawn();
}

/* ============================ aiming & editing ========================= */
var raycaster = new THREE.Raycaster();
raycaster.far = REACH;
var aimCenter = new THREE.Vector2(0, 0);
var aim = null;   // { tx,ty,tz break cell, px..nz hit point + normal }

function updateTarget() {
  raycaster.setFromCamera(aimCenter, camera);
  var hits = raycaster.intersectObjects(chunkMeshes);
  if (hits.length > 0) {
    var h = hits[0], n = h.face.normal;
    aim = {
      tx: Math.floor(h.point.x - n.x * 0.5),
      ty: Math.floor(h.point.y - n.y * 0.5),
      tz: Math.floor(h.point.z - n.z * 0.5),
      px: h.point.x, py: h.point.y, pz: h.point.z,
      nx: n.x, ny: n.y, nz: n.z
    };
    outline.position.set(aim.tx + 0.5, aim.ty + 0.5, aim.tz + 0.5);
    outline.visible = true;
  } else {
    aim = null;
    outline.visible = false;
  }
}

function overlapsPlayer(bx, by, bz) {
  return bx + 1 > player.x - PW && bx < player.x + PW &&
         by + 1 > player.y     && by < player.y + PH &&
         bz + 1 > player.z - PW && bz < player.z + PW;
}

function editBlock(x, y, z, id) {
  setBlock(x, y, z, id);
  var cx = Math.floor(x / CS), cz = Math.floor(z / CS);
  var lx = x - cx * CS, lz = z - cz * CS;
  rebuildChunk(cx, cz);
  if (lx === 0)    rebuildChunk(cx - 1, cz);   // chunk-border neighbors
  if (lx === CS-1) rebuildChunk(cx + 1, cz);
  if (lz === 0)    rebuildChunk(cx, cz - 1);
  if (lz === CS-1) rebuildChunk(cx, cz + 1);
}

function breakBlock() {
  if (!aim || aim.ty === 0) return;                        // y=0 is unbreakable
  if (getBlock(aim.tx, aim.ty, aim.tz) === 0) return;
  editBlock(aim.tx, aim.ty, aim.tz, 0);
}
function placeBlock() {
  if (!aim) return;
  var bx = Math.floor(aim.px + aim.nx * 0.5);
  var by = Math.floor(aim.py + aim.ny * 0.5);
  var bz = Math.floor(aim.pz + aim.nz * 0.5);
  if (getBlock(bx, by, bz) !== 0) return;                  // must be air
  if (overlapsPlayer(bx, by, bz)) return;                  // must not embed player
  editBlock(bx, by, bz, HOTBAR[selected]);
}

/* ================================ hotbar =============================== */
var selected = 0;
var hotbarEl = document.getElementById("hotbar");
var slotEls = [];
HOTBAR.forEach(function (id, i) {
  var s = document.createElement("div");
  s.className = "slot";
  s.style.background = "#" + BLOCKS[id].hex.toString(16).padStart(6, "0");
  var n = document.createElement("span");
  n.textContent = i + 1;
  s.appendChild(n);
  s.title = BLOCKS[id].name;
  hotbarEl.appendChild(s);
  slotEls.push(s);
});
function setSelected(i) {
  selected = ((i % 7) + 7) % 7;
  for (var j = 0; j < slotEls.length; j++)
    slotEls[j].classList.toggle("sel", j === selected);
}
setSelected(0);

/* ================================= input =============================== */
var overlay = document.getElementById("overlay");

overlay.addEventListener("click", function () {
  var p = renderer.domElement.requestPointerLock();
  if (p && p.catch) p.catch(function () {});
});

document.addEventListener("pointerlockchange", function () {
  if (document.pointerLockElement === renderer.domElement) {
    overlay.style.display = "none";
  } else {
    overlay.style.display = "flex";
    keys = {};
  }
});

document.addEventListener("mousemove", function (e) {
  if (document.pointerLockElement !== renderer.domElement) return;
  yaw   -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  var lim = Math.PI / 2 - 0.01;
  if (pitch >  lim) pitch =  lim;
  if (pitch < -lim) pitch = -lim;
});

document.addEventListener("mousedown", function (e) {
  if (document.pointerLockElement !== renderer.domElement) return;  // locked only
  if (e.button === 0) breakBlock();
  else if (e.button === 2) placeBlock();
});

document.addEventListener("contextmenu", function (e) { e.preventDefault(); });

document.addEventListener("wheel", function (e) {
  setSelected(selected + (e.deltaY > 0 ? 1 : -1));
});

document.addEventListener("keydown", function (e) {
  keys[e.code] = true;
  if (e.code === "Space") e.preventDefault();
  if (/^Digit[1-7]$/.test(e.code)) setSelected(parseInt(e.code.slice(5), 10) - 1);
});
document.addEventListener("keyup", function (e) { keys[e.code] = false; });
window.addEventListener("blur", function () { keys = {}; });

window.addEventListener("resize", function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ============================ world streaming ========================== */
function updateWorld() {
  var pcx = Math.floor(player.x / CS), pcz = Math.floor(player.z / CS);

  /* 1) block data within 5 chunks, max 4 per frame */
  var gen = 0;
  for (var dz = -GEN_R; dz <= GEN_R && gen < 4; dz++)
    for (var dx = -GEN_R; dx <= GEN_R && gen < 4; dx++) {
      var k = ckey(pcx + dx, pcz + dz);
      if (!CHUNKS.has(k)) {
        CHUNKS.set(k, { cx: pcx + dx, cz: pcz + dz, data: generateData(pcx + dx, pcz + dz), mesh: null });
        gen++;
      }
    }

  /* 2) meshes within 4 chunks (4 neighbors must have data), max 2 per frame */
  var built = 0;
  for (var dz2 = -MESH_R; dz2 <= MESH_R && built < 2; dz2++)
    for (var dx2 = -MESH_R; dx2 <= MESH_R && built < 2; dx2++) {
      var cx = pcx + dx2, cz = pcz + dz2;
      var c = getChunk(cx, cz);
      if (!c || c.mesh) continue;
      if (!getChunk(cx + 1, cz) || !getChunk(cx - 1, cz) ||
          !getChunk(cx, cz + 1) || !getChunk(cx, cz - 1)) continue;
      buildMesh(c);
      built++;
    }

  /* 3) unload beyond 7 chunks */
  CHUNKS.forEach(function (c, k) {
    if (Math.max(Math.abs(c.cx - pcx), Math.abs(c.cz - pcz)) > UNLOAD_R) {
      if (c.mesh) {
        scene.remove(c.mesh);
        var i = chunkMeshes.indexOf(c.mesh);
        if (i >= 0) chunkMeshes.splice(i, 1);
        c.mesh.geometry.dispose();
      }
      CHUNKS.delete(k);
    }
  });
}

/* ============================== main loop ============================== */
var lastT = performance.now();
function frame(now) {
  requestAnimationFrame(frame);
  var dt = (now - lastT) / 1000;
  lastT = now;
  if (dt > 0.1) dt = 0.1;

  updateWorld();

  /* fixed-substep physics (stable collisions) */
  var acc = dt;
  while (acc > 1e-6) {
    var s = Math.min(acc, 1 / 120);
    stepPhysics(s);
    acc -= s;
  }

  camera.position.set(player.x, player.y + EYE, player.z);
  camera.rotation.set(pitch, yaw, 0);

  updateTarget();

  /* clouds drift and wrap around the player */
  for (var i = 0; i < clouds.length; i++) {
    var cl = clouds[i], p = cl.m.position;
    p.x += cl.sp * dt;
    if (p.x - player.x >  200) p.x -= 400; else if (p.x - player.x < -200) p.x += 400;
    if (p.z - player.z >  200) p.z -= 400; else if (p.z - player.z < -200) p.z += 400;
  }
  water.position.set(player.x, WATER_Y, player.z);

  renderer.render(scene, camera);
}

/* ================================= boot ================================ */
findSpawn();
for (var dz0 = -3; dz0 <= 3; dz0++)
  for (var dx0 = -3; dx0 <= 3; dx0++)
    ensureData(dx0, dz0);          // pre-generate the immediate neighborhood
requestAnimationFrame(frame);
</script>
</body>
</html>
```