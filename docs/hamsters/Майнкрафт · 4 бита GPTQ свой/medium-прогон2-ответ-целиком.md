

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mc.html - Voxel Sandbox</title>
<style>
  html, body { margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:#000; }
  canvas { display:block; }

  #overlay {
    position:fixed; left:0; top:0; width:100%; height:100%;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    background:rgba(0,0,0,0.6); color:#fff;
    font-family:'Courier New', monospace; text-align:center;
    z-index:10; cursor:pointer;
  }
  #overlay h1 { font-size:48px; margin:0 0 12px; letter-spacing:6px; text-shadow:4px 4px 0 #222; }
  #overlay .controls {
    background:rgba(0,0,0,0.45); padding:14px 28px; border-radius:6px;
    line-height:1.8; font-size:14px; margin-bottom:24px; text-align:left;
  }
  #overlay .play { font-size:22px; animation:pulse 1.2s ease-in-out infinite; }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.45; } }

  #crosshair {
    position:fixed; left:50%; top:50%; transform:translate(-50%,-50%);
    width:20px; height:20px; pointer-events:none; z-index:5;
  }
  #crosshair span { position:absolute; background:rgba(255,255,255,0.85); }
  #crosshair .h { left:0; top:9px; width:20px; height:2px; }
  #crosshair .v { left:9px; top:0; width:2px; height:20px; }

  #hotbar {
    position:fixed; left:50%; bottom:12px; transform:translateX(-50%);
    display:flex; gap:6px; background:rgba(0,0,0,0.45);
    padding:6px; border-radius:6px; z-index:5;
  }
  .slot {
    width:46px; height:46px; display:flex; align-items:center; justify-content:center;
    color:#fff; font:bold 15px 'Courier New', monospace;
    text-shadow:0 0 4px #000, 0 0 4px #000;
    border:2px solid rgba(255,255,255,0.25); border-radius:4px; cursor:pointer;
  }
  .slot.selected { border:2px solid #fff; box-shadow:0 0 8px rgba(255,255,255,0.8); }
</style>
</head>
<body>
<div id="overlay">
  <h1>MINECRAFT&nbsp;JS</h1>
  <div class="controls">
    WASD &mdash; move<br>
    SPACE &mdash; jump<br>
    MOUSE &mdash; look around<br>
    LEFT CLICK &mdash; break block<br>
    RIGHT CLICK &mdash; place block<br>
    1&ndash;7 / WHEEL &mdash; select block
  </div>
  <div class="play">Click to play</div>
</div>
<div id="crosshair"><span class="h"></span><span class="v"></span></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
'use strict';

// ---------- Block ids ----------
const AIR=0, GRASS=1, DIRT=2, STONE=3, SAND=4, WOOD=5, LEAVES=6, SNOW=7;
const CH_W=16, CH_H=80;

const BLOCK_COLORS = {};
BLOCK_COLORS[GRASS]  = new THREE.Color(0x4caf50);
BLOCK_COLORS[DIRT]   = new THREE.Color(0x795548);
BLOCK_COLORS[STONE]  = new THREE.Color(0x9e9e9e);
BLOCK_COLORS[SAND]   = new THREE.Color(0xe7d9a8);
BLOCK_COLORS[WOOD]   = new THREE.Color(0x8d6e63);
BLOCK_COLORS[LEAVES] = new THREE.Color(0x2e7d32);
BLOCK_COLORS[SNOW]   = new THREE.Color(0xffffff);

const HOTBAR = [GRASS, DIRT, STONE, SAND, WOOD, LEAVES, SNOW];

// ---------- Deterministic value noise ----------
function hash2i(x, z) {
  let h = (Math.imul(x, 374761393) + Math.imul(z, 668265263)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function hash3i(x, y, z) {
  let h = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1440662185)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function smooth(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
  const xi = Math.floor(x), zi = Math.floor(z);
  const u = smooth(x - xi), v = smooth(z - zi);
  const a = hash2i(xi, zi),     b = hash2i(xi + 1, zi);
  const c = hash2i(xi, zi + 1), d = hash2i(xi + 1, zi + 1);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const u = smooth(x - xi), v = smooth(y - yi), w = smooth(z - zi);
  const c000=hash3i(xi,yi,zi),   c100=hash3i(xi+1,yi,zi),
        c010=hash3i(xi,yi+1,zi), c110=hash3i(xi+1,yi+1,zi),
        c001=hash3i(xi,yi,zi+1), c101=hash3i(xi+1,yi,zi+1),
        c011=hash3i(xi,yi+1,zi+1),c111=hash3i(xi+1,yi+1,zi+1);
  const x00=c000+(c100-c000)*u, x10=c010+(c110-c010)*u;
  const x01=c001+(c101-c001)*u, x11=c011+(c111-c011)*u;
  const y0=x00+(x10-x00)*v,     y1=x01+(x11-x01)*v;
  return y0+(y1-y0)*w;
}
function fractal2(x, z) {
  let f = 0, amp = 0.5, freq = 1;
  for (let i = 0; i < 4; i++) { f += noise2(x * freq, z * freq) * amp; freq *= 2; amp *= 0.5; }
  return f;
}
function columnHeight(wx, wz) {
  const m = fractal2(wx * 0.004, wz * 0.004);
  const h = fractal2(wx * 0.02,  wz * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}

// ---------- Scene ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.5, 1, 0.3);
scene.add(sun);

const voxelMat = new THREE.MeshLambertMaterial({ vertexColors: true });

// Water
const water = new THREE.Mesh(
  new THREE.PlaneGeometry(400, 400),
  new THREE.MeshBasicMaterial({ color: 0x3366dd, transparent: true, opacity: 0.55 })
);
water.rotation.x = -Math.PI / 2;
scene.add(water);

// Clouds
const cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.75, depthWrite: false });
const clouds = [];
for (let i = 0; i < 25; i++) {
  const c = new THREE.Mesh(new THREE.BoxGeometry(15 + Math.random() * 25, 1.5, 10 + Math.random() * 18), cloudMat);
  c.position.set(8 + (Math.random() * 600 - 300), 85 + Math.random() * 12, 8 + (Math.random() * 600 - 300));
  c.userData.speed = 0.5 + Math.random() * 1.2;
  scene.add(c);
  clouds.push(c);
}

// Target outline
const outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.001, 1.001, 1.001)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

// ---------- Chunk storage & block helpers ----------
const chunks = new Map();   // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
const chunkMeshes = [];

function getBlock(wx, wy, wz) {
  if (wy < 0 || wy >= CH_H) return AIR;
  const cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
  const c = chunks.get(cx + ',' + cz);
  if (!c || !c.data) return AIR;
  return c.data[(wy * 16 + (wz - cz * 16)) * 16 + (wx - cx * 16)];
}
function setBlock(wx, wy, wz, id) {
  if (wy < 0 || wy >= CH_H) return;
  const cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
  const c = chunks.get(cx + ',' + cz);
  if (!c || !c.data) return;
  c.data[(wy * 16 + (wz - cz * 16)) * 16 + (wx - cx * 16)] = id;
}

// ---------- Terrain generation ----------
function generateData(cx, cz) {
  const data = new Uint8Array(CH_W * CH_W * CH_H);
  const set = (lx, y, lz, id) => {
    if (y >= 0 && y < CH_H && lx >= 0 && lx < 16 && lz >= 0 && lz < 16)
      data[(y * 16 + lz) * 16 + lx] = id;
  };
  const get = (lx, y, lz) =>
    (y >= 0 && y < CH_H && lx >= 0 && lx < 16 && lz >= 0 && lz < 16)
      ? data[(y * 16 + lz) * 16 + lx] : 0;

  for (let lz = 0; lz < 16; lz++) {
    for (let lx = 0; lx < 16; lx++) {
      const wx = cx * 16 + lx, wz = cz * 16 + lz;
      const H = columnHeight(wx, wz);
      for (let y = 0; y < H; y++) {
        let id;
        if (y === 0) id = STONE;                                   // unbreakable base
        else if (y < H - 3) id = STONE;
        else if (y < H) id = (H <= 16) ? SAND : (H >= 37 ? STONE : DIRT);
        else id = (H >= 46) ? SNOW : (H >= 37 ? STONE : (H <= 16 ? SAND : GRASS));
        set(lx, y, lz, id);
      }
      // caves
      for (let y = 3; y < H - 2; y++) {
        if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) set(lx, y, lz, AIR);
      }
    }
  }
  // trees (only when the whole tree fits inside this chunk)
  for (let lz = 2; lz < 14; lz++) {
    for (let lx = 2; lx < 14; lx++) {
      const wx = cx * 16 + lx, wz = cz * 16 + lz;
      const H = columnHeight(wx, wz);
      if (H <= 16 || H >= 37) continue;
      if (get(lx, H, lz) !== GRASS) continue;
      if (hash2i(wx, wz) >= 0.02) continue;
      for (let y = 1; y <= 4; y++)
        if (get(lx, H + y, lz) === AIR) set(lx, H + y, lz, WOOD);
      for (let dy = 3; dy <= 4; dy++)
        for (let dx = -2; dx <= 2; dx++)
          for (let dz = -2; dz <= 2; dz++)
            if (get(lx + dx, H + dy, lz + dz) === AIR) set(lx + dx, H + dy, lz + dz, LEAVES);
      for (let dx = -1; dx <= 1; dx++)
        for (let dz = -1; dz <= 1; dz++)
          if (get(lx + dx, H + 5, lz + dz) === AIR) set(lx + dx, H + 5, lz + dz, LEAVES);
      if (get(lx, H + 6, lz) === AIR) set(lx, H + 6, lz, LEAVES);
    }
  }
  return data;
}

// ---------- Meshing ----------
const FACES = [
  { d:[ 1,0,0], s:0.8,  c:[[1,1,1],[1,0,1],[1,1,0],[1,0,0]] },
  { d:[-1,0,0], s:0.8,  c:[[0,1,0],[0,0,0],[0,1,1],[0,0,1]] },
  { d:[0, 1,0], s:1.0,  c:[[0,1,1],[1,1,1],[0,1,0],[1,1,0]] },
  { d:[0,-1,0], s:0.55, c:[[0,0,0],[1,0,0],[0,0,1],[1,0,1]] },
  { d:[0,0, 1], s:0.8,  c:[[0,1,1],[0,0,1],[1,1,1],[1,0,1]] },
  { d:[0,0,-1], s:0.8,  c:[[1,1,0],[1,0,0],[0,1,0],[0,0,0]] }
];

function buildChunkGeometry(c, cx, cz) {
  const pos = [], nor = [], col = [], idx = [];
  for (let y = 0; y < CH_H; y++) {
    for (let lz = 0; lz < 16; lz++) {
      for (let lx = 0; lx < 16; lx++) {
        const id = c.data[(y * 16 + lz) * 16 + lx];
        if (id === AIR) continue;
        const bc = BLOCK_COLORS[id];
        const wx = cx * 16 + lx, wz = cz * 16 + lz;
        for (let f = 0; f < 6; f++) {
          const face = FACES[f];
          if (getBlock(wx + face.d[0], y + face.d[1], wz + face.d[2]) !== AIR) continue;
          const base = pos.length / 3;
          for (let i = 0; i < 4; i++) {
            pos.push(wx + face.c[i][0], y + face.c[i][1], wz + face.c[i][2]);
            nor.push(face.d[0], face.d[1], face.d[2]);
            col.push(bc.r * face.s, bc.g * face.s, bc.b * face.s);
          }
          idx.push(base, base + 1, base + 2, base + 2, base + 1, base + 3);
        }
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal',   new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('color',    new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  return g;
}

function rebuildChunk(cx, cz) {
  const c = chunks.get(cx + ',' + cz);
  if (!c || !c.data) return;
  if (c.mesh) {
    scene.remove(c.mesh);
    c.mesh.geometry.dispose();
    const i = chunkMeshes.indexOf(c.mesh);
    if (i >= 0) chunkMeshes.splice(i, 1);
    c.mesh = null;
  }
  const mesh = new THREE.Mesh(buildChunkGeometry(c, cx, cz), voxelMat);
  mesh.userData.cx = cx;
  mesh.userData.cz = cz;
  scene.add(mesh);
  chunkMeshes.push(mesh);
  c.mesh = mesh;
}

function editBlock(wx, wy, wz, id) {
  setBlock(wx, wy, wz, id);
  const cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
  rebuildChunk(cx, cz);
  const lx = wx - cx * 16, lz = wz - cz * 16;
  if (lx === 0)  rebuildChunk(cx - 1, cz);
  if (lx === 15) rebuildChunk(cx + 1, cz);
  if (lz === 0)  rebuildChunk(cx, cz - 1);
  if (lz === 15) rebuildChunk(cx, cz + 1);
}

// ---------- Per-frame world streaming ----------
function updateWorld() {
  const pcx = Math.floor(player.x / 16), pcz = Math.floor(player.z / 16);

  let gen = 0;
  outerGen:
  for (let dz = -5; dz <= 5; dz++) {
    for (let dx = -5; dx <= 5; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const k = cx + ',' + cz;
      if (!chunks.has(k)) {
        chunks.set(k, { data: generateData(cx, cz), mesh: null });
        if (++gen >= 4) break outerGen;
      }
    }
  }

  let built = 0;
  outerMesh:
  for (let dz = -4; dz <= 4; dz++) {
    for (let dx = -4; dx <= 4; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const c = chunks.get(cx + ',' + cz);
      if (!c || !c.data || c.mesh) continue;
      if (!chunks.get((cx - 1) + ',' + cz) || !chunks.get((cx + 1) + ',' + cz) ||
          !chunks.get(cx + ',' + (cz - 1)) || !chunks.get(cx + ',' + (cz + 1))) continue;
      rebuildChunk(cx, cz);
      if (++built >= 2) break outerMesh;
    }
  }

  for (const [k, c] of Array.from(chunks)) {
    const parts = k.split(',');
    const cx = parseInt(parts[0], 10), cz = parseInt(parts[1], 10);
    if (Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz)) > 7) {
      if (c.mesh) {
        scene.remove(c.mesh);
        c.mesh.geometry.dispose();
        const i = chunkMeshes.indexOf(c.mesh);
        if (i >= 0) chunkMeshes.splice(i, 1);
      }
      chunks.delete(k);
    }
  }
}

// ---------- Player ----------
let yaw = 0, pitch = 0;
const player = { x: 8.5, y: 40, z: 8.5, vx: 0, vy: 0, vz: 0, onGround: false };

function findSpawn() {
  for (let r = 0; r < 8; r++) {
    for (let dx = -r; dx <= r; dx++) {
      for (let dz = -r; dz <= r; dz++) {
        if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;
        const sx = 8.5 + dx, sz = 8.5 + dz;
        const sy = columnHeight(Math.floor(sx), Math.floor(sz)) + 1;
        if (!collides(sx, sy, sz)) return { x: sx, y: sy, z: sz };
      }
    }
  }
  return { x: 8.5, y: columnHeight(8, 8) + 1, z: 8.5 };
}
const SPAWN = findSpawn();
player.x = SPAWN.x; player.y = SPAWN.y; player.z = SPAWN.z;

function collides(px, py, pz) {
  const x0 = Math.floor(px - 0.3), x1 = Math.floor(px + 0.3);
  const y0 = Math.floor(py),       y1 = Math.floor(py + 1.8);
  const z0 = Math.floor(pz - 0.3), z1 = Math.floor(pz + 0.3);
  for (let x = x0; x <= x1; x++)
    for (let y = y0; y <= y1; y++)
      for (let z = z0; z <= z1; z++)
        if (getBlock(x, y, z) !== AIR) return true;
  return false;
}

const keys = {};
function updatePlayer(dt) {
  if (keys['Space'] && player.onGround) player.vy = 8.5;
  player.vy -= 25 * dt;
  if (player.vy < -60) player.vy = -60;

  const s = Math.sin(yaw), c = Math.cos(yaw);
  let mx = 0, mz = 0;
  if (keys['KeyW']) { mx -= s; mz -= c; }
  if (keys['KeyS']) { mx += s; mz += c; }
  if (keys['KeyA']) { mx -= c; mz += s; }
  if (keys['KeyD']) { mx += c; mz -= s; }
  const len = Math.hypot(mx, mz);
  if (len > 0) { mx /= len; mz /= len; }
  player.vx = mx * 5.5;
  player.vz = mz * 5.5;

  player.onGround = false;
  player.x += player.vx * dt;
  if (collides(player.x, player.y, player.z)) player.x -= player.vx * dt;
  player.z += player.vz * dt;
  if (collides(player.x, player.y, player.z)) player.z -= player.vz * dt;
  player.y += player.vy * dt;
  if (collides(player.x, player.y, player.z)) {
    player.y -= player.vy * dt;
    if (player.vy < 0) player.onGround = true;
    player.vy = 0;
  }
  if (player.y < -20) {
    player.x = SPAWN.x; player.y = SPAWN.y; player.z = SPAWN.z;
    player.vx = player.vy = player.vz = 0;
  }
  camera.position.set(player.x, player.y + 1.62, player.z);
}

// ---------- Break / place ----------
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
const center = new THREE.Vector2(0, 0);
let target = null, place = null;

function overlapsPlayer(bx, by, bz) {
  return bx < player.x + 0.3 && bx + 1 > player.x - 0.3 &&
         bz < player.z + 0.3 && bz + 1 > player.z - 0.3 &&
         by < player.y + 1.8 && by + 1 > player.y;
}

function updateTarget() {
  raycaster.setFromCamera(center, camera);
  const hits = raycaster.intersectObjects(chunkMeshes);
  if (hits.length > 0) {
    const h = hits[0];
    const n = h.face.normal;
    target = {
      x: Math.floor(h.point.x - n.x * 0.5),
      y: Math.floor(h.point.y - n.y * 0.5),
      z: Math.floor(h.point.z - n.z * 0.5)
    };
    place = {
      x: Math.floor(h.point.x + n.x * 0.5),
      y: Math.floor(h.point.y + n.y * 0.5),
      z: Math.floor(h.point.z + n.z * 0.5)
    };
    outline.visible = true;
    outline.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
  } else {
    target = null;
    outline.visible = false;
  }
}

// ---------- Input ----------
let locked = false;
const overlay = document.getElementById('overlay');

overlay.addEventListener('click', () => {
  document.body.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  locked = (document.pointerLockElement === document.body);
  overlay.style.display = locked ? 'none' : 'flex';
});
document.addEventListener('pointerlockerror', () => {
  overlay.style.display = 'flex';
});

document.addEventListener('mousemove', (e) => {
  if (!locked) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  pitch = Math.max(-1.55, Math.min(1.55, pitch));
  camera.rotation.set(pitch, yaw, 0);
});

document.addEventListener('mousedown', (e) => {
  if (!locked) return;
  if (!target || !place) return;
  if (e.button === 0) {
    if (target.y > 0) editBlock(target.x, target.y, target.z, AIR);
  } else if (e.button === 2) {
    if (place.y > 0 && place.y < CH_H &&
        getBlock(place.x, place.y, place.z) === AIR &&
        !overlapsPlayer(place.x, place.y, place.z)) {
      editBlock(place.x, place.y, place.z, HOTBAR[selected]);
    }
  }
});

window.addEventListener('contextmenu', (e) => e.preventDefault());

window.addEventListener('keydown', (e) => {
  keys[e.code] = true;
  if (e.code === 'Space') e.preventDefault();
  if (e.code.indexOf('Digit') === 0) {
    const n = parseInt(e.code.slice(5), 10);
    if (n >= 1 && n <= 7) selectSlot(n - 1);
  }
});
window.addEventListener('keyup', (e) => { keys[e.code] = false; });

// ---------- Hotbar ----------
let selected = 0;
const hotbarEl = document.getElementById('hotbar');
HOTBAR.forEach((id, i) => {
  const s = document.createElement('div');
  s.className = 'slot';
  s.style.background = '#' + BLOCK_COLORS[id].getHexString();
  s.textContent = String(i + 1);
  s.addEventListener('click', () => selectSlot(i));
  hotbarEl.appendChild(s);
});
function selectSlot(i) {
  selected = i;
  Array.prototype.forEach.call(hotbarEl.children, (el, j) =>
    el.classList.toggle('selected', j === i));
}
selectSlot(0);

document.addEventListener('wheel', (e) => {
  if (!locked) return;
  selected = (selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
  selectSlot(selected);
}, { passive: true });

// ---------- Resize ----------
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ---------- Pre-generate area around spawn ----------
for (let dz = -4; dz <= 4; dz++)
  for (let dx = -4; dx <= 4; dx++)
    chunks.set(dx + ',' + dz, { data: generateData(dx, dz), mesh: null });
for (let dz = -3; dz <= 3; dz++)
  for (let dx = -3; dx <= 3; dx++)
    rebuildChunk(dx, dz);

// ---------- Main loop ----------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  updateWorld();
  updatePlayer(dt);
  updateTarget();

  water.position.set(player.x, 14.3, player.z);

  for (const cld of clouds) {
    cld.position.x += cld.userData.speed * dt;
    let dx = cld.position.x - player.x;
    if (dx > 300) cld.position.x -= 600; else if (dx < -300) cld.position.x += 600;
    let dz = cld.position.z - player.z;
    if (dz > 300) cld.position.z -= 600; else if (dz < -300) cld.position.z += 600;
  }

  renderer.render(scene, camera);
}
animate();

})();
</script>
</body>
</html>
```