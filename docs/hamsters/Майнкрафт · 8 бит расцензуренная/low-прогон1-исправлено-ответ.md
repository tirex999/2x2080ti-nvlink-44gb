

Причина: в прошлом ответе блок ```html оказался полностью пустым — в файл не попало ни одной строки кода, поэтому браузер просто открыл пустую страницу (ничего не рендерилось), и «снимок» зафиксировал пустоту. Фактически был нарушен пункт «не обрезай файл».

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MC</title>
<style>
html,body{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#000;}
canvas{display:block;}
#crosshair{position:fixed;left:50%;top:50%;width:20px;height:20px;margin:-10px 0 0 -10px;pointer-events:none;z-index:5;}
#crosshair::before,#crosshair::after{content:"";position:absolute;background:rgba(255,255,255,0.85);}
#crosshair::before{left:9px;top:0;width:2px;height:20px;}
#crosshair::after{left:0;top:9px;width:20px;height:2px;}
#hotbar{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);display:flex;gap:4px;background:rgba(0,0,0,0.45);padding:5px;border-radius:6px;z-index:5;}
.slot{width:42px;height:42px;border:2px solid rgba(255,255,255,0.35);border-radius:4px;position:relative;display:flex;align-items:center;justify-content:center;color:#fff;font:bold 12px monospace;text-shadow:0 0 3px #000;}
.slot.sel{border-color:#fff;box-shadow:0 0 6px #fff;}
#overlay{position:fixed;left:0;top:0;right:0;bottom:0;background:rgba(20,25,35,0.72);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:monospace;z-index:10;cursor:pointer;text-align:center;}
#overlay h1{font-size:44px;margin:0 0 10px;letter-spacing:4px;}
#overlay p{margin:4px 0;line-height:1.5;}
#play{margin-top:18px;font-size:20px;color:#9fe870;}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
<h1>MINECRAFT CLONE</h1>
<p>WASD &mdash; move, Space &mdash; jump, Mouse &mdash; look</p>
<p>Left click &mdash; break block, Right click &mdash; place block</p>
<p>1&ndash;7 / Wheel &mdash; select block</p>
<p id="play">Click to play</p>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
'use strict';

/* ---------- Blocks ---------- */
var BLOCKS = {
  1:{name:'grass', color:0x4caf50},
  2:{name:'dirt',  color:0x795548},
  3:{name:'stone', color:0x9e9e9e},
  4:{name:'sand',  color:0xe7d9a8},
  5:{name:'wood',  color:0x8d6e63},
  6:{name:'leaves',color:0x2e7d32},
  7:{name:'snow',  color:0xffffff}
};
var HOTBAR = [1,2,3,4,5,6,7];
var selected = 0;

/* ---------- Scene ---------- */
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

var renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.6, 1, 0.4);
scene.add(sun);

var blockMat = new THREE.MeshLambertMaterial({vertexColors:true});

var blockColor = [];
for (var bi = 0; bi < 8; bi++)
  blockColor[bi] = new THREE.Color(BLOCKS[bi] ? BLOCKS[bi].color : 0xffffff);

/* ---------- Noise (deterministic) ---------- */
function ihash2(x, y) {
  var n = Math.imul(x, 374761393) ^ Math.imul(y, 668265263);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
function ihash3(x, y, z) {
  var n = Math.imul(x, 374761393) ^ Math.imul(y, 668265263) ^ Math.imul(z, 2147483629);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  n ^= n >>> 16;
  return (n >>> 0) / 4294967296;
}
function sstep(t) { return t * t * (3 - 2 * t); }

function noise2(x, y) {
  var xi = Math.floor(x), yi = Math.floor(y);
  var xf = sstep(x - xi), yf = sstep(y - yi);
  var a = ihash2(xi, yi),     b = ihash2(xi + 1, yi);
  var c = ihash2(xi, yi + 1), d = ihash2(xi + 1, yi + 1);
  return a + (b - a) * xf + (c - a) * yf + (a - b - c + d) * xf * yf;
}
function fractal2(x, y) {
  var v = 0, amp = 1, f = 1, tot = 0;
  for (var o = 0; o < 4; o++) {
    v += amp * noise2(x * f, y * f);
    tot += amp; amp *= 0.5; f *= 2;
  }
  return v / tot;
}
function noise3(x, y, z) {
  var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  var xf = sstep(x - xi), yf = sstep(y - yi), zf = sstep(z - zi);
  var c000 = ihash3(xi, yi, zi),     c100 = ihash3(xi + 1, yi, zi);
  var c010 = ihash3(xi, yi + 1, zi), c110 = ihash3(xi + 1, yi + 1, zi);
  var c001 = ihash3(xi, yi, zi + 1), c101 = ihash3(xi + 1, yi, zi + 1);
  var c011 = ihash3(xi, yi + 1, zi + 1), c111 = ihash3(xi + 1, yi + 1, zi + 1);
  var x00 = c000 + (c100 - c000) * xf, x10 = c010 + (c110 - c010) * xf;
  var x01 = c001 + (c101 - c001) * xf, x11 = c011 + (c111 - c011) * xf;
  var y0 = x00 + (x10 - x00) * yf, y1 = x01 + (x11 - x01) * yf;
  return y0 + (y1 - y0) * zf;
}

/* ---------- Terrain ---------- */
var CHUNK = 16, HEIGHT = 80;

function colHeight(x, z) {
  var m = fractal2(x * 0.004, z * 0.004);
  var h = fractal2(x * 0.02, z * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}

/* ---------- Chunks ---------- */
var chunks = new Map();
var chunkMeshes = [];

function chunkKey(cx, cz) { return cx + ',' + cz; }

function getBlock(x, y, z) {
  if (y < 0 || y >= HEIGHT) return 0;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var c = chunks.get(chunkKey(cx, cz));
  if (!c) return 0;
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  return c.data[(lx * CHUNK + lz) * HEIGHT + y];
}
function setBlock(x, y, z, id) {
  if (y < 0 || y >= HEIGHT) return;
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var c = chunks.get(chunkKey(cx, cz));
  if (!c) return;
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  c.data[(lx * CHUNK + lz) * HEIGHT + y] = id;
}

function cellAt(data, lx, lz, y) {
  if (lx < 0 || lz < 0 || lx >= CHUNK || lz >= CHUNK || y < 0 || y >= HEIGHT) return -1;
  return data[(lx * CHUNK + lz) * HEIGHT + y];
}
function leafLayer(data, lx, lz, y, r) {
  for (var dx = -r; dx <= r; dx++)
    for (var dz = -r; dz <= r; dz++) {
      if (cellAt(data, lx + dx, lz + dz, y) === 0)
        data[((lx + dx) * CHUNK + (lz + dz)) * HEIGHT + y] = 6;
    }
}

function generateChunk(cx, cz) {
  var data = new Uint8Array(CHUNK * CHUNK * HEIGHT);
  var heights = new Int16Array(CHUNK * CHUNK);
  var lz, lx, wx, wz, H, y;

  for (lz = 0; lz < CHUNK; lz++) {
    for (lx = 0; lx < CHUNK; lx++) {
      wx = cx * CHUNK + lx; wz = cz * CHUNK + lz;
      H = colHeight(wx, wz);
      heights[lx * CHUNK + lz] = H;
      var below = (H <= 16) ? 4 : ((H >= 37) ? 3 : 2);
      var surf  = (H >= 46) ? 7 : ((H >= 37) ? 3 : ((H <= 16) ? 4 : 1));
      for (y = 0; y <= H; y++) {
        var id;
        if (y === 0) id = 3;
        else if (y === H) id = surf;
        else if (y > H - 3) id = below;
        else id = 3;
        data[(lx * CHUNK + lz) * HEIGHT + y] = id;
      }
      for (y = 3; y <= H - 2; y++) {
        if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67)
          data[(lx * CHUNK + lz) * HEIGHT + y] = 0;
      }
    }
  }

  /* trees */
  for (lz = 0; lz < CHUNK; lz++) {
    for (lx = 0; lx < CHUNK; lx++) {
      wx = cx * CHUNK + lx; wz = cz * CHUNK + lz;
      H = heights[lx * CHUNK + lz];
      if (data[(lx * CHUNK + lz) * HEIGHT + H] !== 1) continue;
      if (ihash2(wx * 7 + 13, wz * 7 + 29) >= 0.02) continue;
      if (H + 7 >= HEIGHT) continue;
      for (var t = 1; t <= 4; t++) {
        var yi = H + t;
        if (cellAt(data, lx, lz, yi) === 0)
          data[(lx * CHUNK + lz) * HEIGHT + yi] = 5;
      }
      leafLayer(data, lx, lz, H + 4, 2);
      leafLayer(data, lx, lz, H + 5, 2);
      leafLayer(data, lx, lz, H + 6, 1);
      if (cellAt(data, lx, lz, H + 7) === 0)
        data[(lx * CHUNK + lz) * HEIGHT + H + 7] = 6;
    }
  }

  chunks.set(chunkKey(cx, cz), {data: data, mesh: null});
}

/* ---------- Meshing ---------- */
var FACES = [
  {n:[0, 1, 0],  s:1.0,  v:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]]},
  {n:[0,-1, 0],  s:0.55, v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
  {n:[1, 0, 0],  s:0.8,  v:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]]},
  {n:[-1,0, 0],  s:0.8,  v:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]},
  {n:[0, 0, 1],  s:0.8,  v:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]},
  {n:[0, 0,-1],  s:0.8,  v:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]]}
];

function buildChunkMesh(cx, cz) {
  var c = chunks.get(chunkKey(cx, cz));
  if (!c) return;
  if (c.mesh) {
    scene.remove(c.mesh);
    var ri = chunkMeshes.indexOf(c.mesh);
    if (ri >= 0) chunkMeshes.splice(ri, 1);
    c.mesh.geometry.dispose();
    c.mesh = null;
  }

  var pos = [], nor = [], col = [], idx = [];
  var ox = cx * CHUNK, oz = cz * CHUNK;
  var lz, lx, wx, wz, y, id, f, vi, v, k;

  for (lz = 0; lz < CHUNK; lz++) {
    for (lx = 0; lx < CHUNK; lx++) {
      wx = ox + lx; wz = oz + lz;
      for (y = 0; y < HEIGHT; y++) {
        id = c.data[(lx * CHUNK + lz) * HEIGHT + y];
        if (!id) continue;
        var base = blockColor[id];
        for (f = 0; f < 6; f++) {
          var F = FACES[f];
          if (getBlock(wx + F.n[0], y + F.n[1], wz + F.n[2]) !== 0) continue;
          vi = pos.length / 3;
          for (k = 0; k < 4; k++) {
            v = F.v[k];
            pos.push(wx + v[0], y + v[1], wz + v[2]);
            nor.push(F.n[0], F.n[1], F.n[2]);
            col.push(base.r * F.s, base.g * F.s, base.b * F.s);
          }
          idx.push(vi, vi + 1, vi + 2, vi, vi + 2, vi + 3);
        }
      }
    }
  }

  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('normal',   new THREE.Float32BufferAttribute(nor, 3));
  geo.setAttribute('color',    new THREE.Float32BufferAttribute(col, 3));
  geo.setIndex(idx);

  var mesh = new THREE.Mesh(geo, blockMat);
  mesh.position.set(0, 0, 0);
  mesh.userData.cx = cx;
  mesh.userData.cz = cz;
  c.mesh = mesh;
  scene.add(mesh);
  chunkMeshes.push(mesh);
}

function rebuildChunk(cx, cz) { buildChunkMesh(cx, cz); }

function updateChunks() {
  var pcx = Math.floor(player.x / CHUNK), pcz = Math.floor(player.z / CHUNK);
  var dx, dz, cx, cz, k, c;

  /* generate data: within 5, max 4/frame */
  var toGen = [];
  for (dz = -5; dz <= 5; dz++)
    for (dx = -5; dx <= 5; dx++) {
      cx = pcx + dx; cz = pcz + dz;
      if (!chunks.has(chunkKey(cx, cz)))
        toGen.push([dx * dx + dz * dz, cx, cz]);
    }
  toGen.sort(function(a, b){ return a[0] - b[0]; });
  var gen = 0;
  for (var gi = 0; gi < toGen.length && gen < 4; gi++, gen++)
    generateChunk(toGen[gi][1], toGen[gi][2]);

  /* build meshes: within 4, neighbors have data, max 2/frame */
  var toBuild = [];
  for (var it = chunks.entries(), e; !(e = it.next()).done; ) {
    c = e.value;
    var parts = e.key.split(',');
    cx = +parts[0]; cz = +parts[1];
    dx = cx - pcx; dz = cz - pcz;
    if (dx * dx + dz * dz > 16) continue;
    if (c.mesh) continue;
    if (chunks.has(chunkKey(cx + 1, cz)) && chunks.has(chunkKey(cx - 1, cz)) &&
        chunks.has(chunkKey(cx, cz + 1)) && chunks.has(chunkKey(cx, cz - 1)))
      toBuild.push([dx * dx + dz * dz, cx, cz]);
  }
  toBuild.sort(function(a, b){ return a[0] - b[0]; });
  var built = 0;
  for (var bi2 = 0; bi2 < toBuild.length && built < 2; bi2++, built++)
    buildChunkMesh(toBuild[bi2][1], toBuild[bi2][2]);

  /* unload: farther than 7 */
  for (var it2 = chunks.entries(), e2; !(e2 = it2.next()).done; ) {
    c = e2.value;
    var p2 = e2.key.split(',');
    cx = +p2[0]; cz = +p2[1];
    dx = cx - pcx; dz = cz - pcz;
    if (dx * dx + dz * dz > 49) {
      if (c.mesh) {
        scene.remove(c.mesh);
        c.mesh.geometry.dispose();
        var mi = chunkMeshes.indexOf(c.mesh);
        if (mi >= 0) chunkMeshes.splice(mi, 1);
        c.mesh = null;
      }
      chunks.delete(e2.key);
    }
  }
}

/* ---------- Player ---------- */
var player = {x:8, y:0, z:8, vx:0, vy:0, vz:0, onGround:false};
var SPAWN = {x:8, y:colHeight(8, 8) + 2, z:8};
player.y = SPAWN.y;

var yaw = 0, pitch = 0;
var keys = {};
var locked = false;

function collides(px, py, pz) {
  var minX = Math.floor(px - 0.3), maxX = Math.floor(px + 0.3);
  var minY = Math.floor(py),      maxY = Math.floor(py + 1.8);
  var minZ = Math.floor(pz - 0.3), maxZ = Math.floor(pz + 0.3);
  for (var x = minX; x <= maxX; x++)
    for (var y = minY; y <= maxY; y++)
      for (var z = minZ; z <= maxZ; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}

function updatePlayer(dt) {
  var fwd = (keys['KeyW'] ? 1 : 0) - (keys['KeyS'] ? 1 : 0);
  var str = (keys['KeyD'] ? 1 : 0) - (keys['KeyA'] ? 1 : 0);
  var sin = Math.sin(yaw), cos = Math.cos(yaw);
  var dx = fwd * -sin + str * cos;
  var dz = fwd * -cos + str * -sin;
  var l = Math.sqrt(dx * dx + dz * dz);
  if (l > 0) { dx = dx / l * 5.5; dz = dz / l * 5.5; }
  player.vx = dx; player.vz = dz;

  player.vy -= 25 * dt;
  if (keys['Space'] && player.onGround) { player.vy = 8.5; player.onGround = false; }

  var nx = player.x + player.vx * dt;
  if (!collides(nx, player.y, player.z)) player.x = nx; else player.vx = 0;

  var nz = player.z + player.vz * dt;
  if (!collides(player.x, player.y, nz)) player.z = nz; else player.vz = 0;

  player.onGround = false;
  var rem = player.vy * dt;
  while (rem !== 0) {
    var s = (rem > 0 ? 1 : -1) * Math.min(Math.abs(rem), 0.5);
    var ty = player.y + s;
    if (!collides(player.x, ty, player.z)) { player.y = ty; rem -= s; }
    else { if (player.vy < 0) player.onGround = true; player.vy = 0; break; }
  }

  if (player.y < -20) {
    player.x = SPAWN.x; player.y = SPAWN.y; player.z = SPAWN.z;
    player.vx = player.vy = player.vz = 0;
  }

  camera.position.set(player.x, player.y + 1.62, player.z);
}

/* ---------- Input ---------- */
var overlay = document.getElementById('overlay');
overlay.addEventListener('click', function () {
  renderer.domElement.requestPointerLock();
});
document.addEventListener('pointerlockchange', function () {
  locked = (document.pointerLockElement === renderer.domElement);
  overlay.style.display = locked ? 'none' : 'flex';
});

document.addEventListener('mousemove', function (e) {
  if (!locked) return;
  yaw   -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  var lim = Math.PI / 2 - 0.01;
  if (pitch >  lim) pitch =  lim;
  if (pitch < -lim) pitch = -lim;
  camera.rotation.y = yaw;
  camera.rotation.x = pitch;
});

window.addEventListener('keydown', function (e) {
  keys[e.code] = true;
  if (e.code.indexOf('Digit') === 0) {
    var d = +e.code.slice(5);
    if (d >= 1 && d <= 7) selectSlot(d - 1);
  }
});
window.addEventListener('keyup', function (e) { keys[e.code] = false; });

window.addEventListener('contextmenu', function (e) { e.preventDefault(); });

window.addEventListener('wheel', function (e) {
  selectSlot((selected + (e.deltaY > 0 ? 1 : 6)) % 7);
}, {passive:true});

/* ---------- Raycast / break / place ---------- */
var raycaster = new THREE.Raycaster();
raycaster.far = 6;
var center = new THREE.Vector2(0, 0);

var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({color:0x000000})
);
outline.visible = false;
scene.add(outline);

var target = null;

function updateTarget() {
  raycaster.setFromCamera(center, camera);
  var hits = raycaster.intersectObjects(chunkMeshes);
  var h = hits.length ? hits[0] : null;
  if (h && h.distance <= 6) {
    var p = h.point, n = h.face.normal;
    target = {
      x: Math.floor(p.x - n.x * 0.5),
      y: Math.floor(p.y - n.y * 0.5),
      z: Math.floor(p.z - n.z * 0.5),
      nx: n.x, ny: n.y, nz: n.z
    };
    outline.visible = true;
    outline.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
  } else {
    target = null;
    outline.visible = false;
  }
}

function editRebuild(x, z) {
  var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
  var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
  rebuildChunk(cx, cz);
  if (lx === 0)  rebuildChunk(cx - 1, cz);
  if (lx === 15) rebuildChunk(cx + 1, cz);
  if (lz === 0)  rebuildChunk(cx, cz - 1);
  if (lz === 15) rebuildChunk(cx, cz + 1);
}

window.addEventListener('mousedown', function (e) {
  if (!locked || !target) return;
  if (e.button === 0) {
    if (target.y > 0) {
      setBlock(target.x, target.y, target.z, 0);
      editRebuild(target.x, target.z);
    }
  } else if (e.button === 2) {
    var px = target.x + target.nx;
    var py = target.y + target.ny;
    var pz = target.z + target.nz;
    if (py >= 0 && py < HEIGHT && getBlock(px, py, pz) === 0) {
      var overlap =
        px + 1 > player.x - 0.3 && px < player.x + 0.3 &&
        py + 1 > player.y       && py < player.y + 1.8 &&
        pz + 1 > player.z - 0.3 && pz < player.z + 0.3;
      if (!overlap) {
        setBlock(px, py, pz, HOTBAR[selected]);
        editRebuild(px, pz);
      }
    }
  }
});

/* ---------- Hotbar ---------- */
var hotbarEl = document.getElementById('hotbar');
var slotEls = [];
HOTBAR.forEach(function (id, i) {
  var d = document.createElement('div');
  d.className = 'slot';
  d.style.background = '#' + BLOCKS[id].color.toString(16).padStart(6, '0');
  d.textContent = i + 1;
  hotbarEl.appendChild(d);
  slotEls.push(d);
});
function selectSlot(i) {
  selected = i;
  slotEls.forEach(function (el, j) { el.classList.toggle('sel', j === i); });
}
selectSlot(0);

/* ---------- Clouds & water ---------- */
var clouds = [];
var cloudMat = new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.85});
for (var ci = 0; ci < 25; ci++) {
  var cg = new THREE.BoxGeometry(8 + Math.random() * 18, 1.2, 6 + Math.random() * 12);
  var cm = new THREE.Mesh(cg, cloudMat);
  cm.position.set(
    player.x - 150 + Math.random() * 300,
    88 + Math.random() * 10,
    player.z - 150 + Math.random() * 300
  );
  cm.userData.speed = 1 + Math.random() * 2;
  scene.add(cm);
  clouds.push(cm);
}

var water = new THREE.Mesh(
  new THREE.PlaneGeometry(400, 400),
  new THREE.MeshLambertMaterial({color:0x3d6fd6, transparent:true, opacity:0.55, depthWrite:false})
);
water.rotation.x = -Math.PI / 2;
water.position.y = 14.3;
scene.add(water);

/* ---------- Main loop ---------- */
var last = performance.now();
function animate() {
  requestAnimationFrame(animate);
  var now = performance.now();
  var dt = (now - last) / 1000;
  last = now;
  if (dt > 0.05) dt = 0.05;

  updateChunks();
  updatePlayer(dt);
  updateTarget();

  water.position.x = player.x;
  water.position.z = player.z;

  for (var i = 0; i < clouds.length; i++) {
    var cl = clouds[i];
    cl.position.x += cl.userData.speed * dt;
    if (cl.position.x - player.x >  200) cl.position.x -= 400;
    if (cl.position.x - player.x < -200) cl.position.x += 400;
  }

  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', function () {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```