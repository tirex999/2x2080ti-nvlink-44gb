

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mc.html</title>
<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #000;
  font-family: 'Courier New', monospace;
}
canvas { display: block; }

#overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  z-index: 10;
  cursor: pointer;
  text-align: center;
}
#overlay h1 {
  font-size: 52px;
  margin: 0 0 12px;
  letter-spacing: 4px;
  text-shadow: 0 0 12px rgba(0, 0, 0, 0.8);
}
#overlay .controls {
  font-size: 15px;
  line-height: 1.7;
  margin-bottom: 24px;
  opacity: 0.9;
}
#overlay .play {
  font-size: 22px;
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

#crosshair {
  position: fixed;
  left: 50%;
  top: 50%;
  width: 20px;
  height: 20px;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 5;
}
#crosshair::before,
#crosshair::after {
  content: '';
  position: absolute;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.8);
}
#crosshair::before {
  left: 9px;
  top: 0;
  width: 2px;
  height: 20px;
}
#crosshair::after {
  left: 0;
  top: 9px;
  width: 20px;
  height: 2px;
}

#hotbar {
  position: fixed;
  left: 50%;
  bottom: 12px;
  transform: translateX(-50%);
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.45);
  padding: 4px;
  border-radius: 6px;
  z-index: 5;
  pointer-events: none;
}
.slot {
  width: 48px;
  height: 48px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  box-sizing: border-box;
  position: relative;
  border-radius: 3px;
}
.slot.selected {
  border-color: #ffffff;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.8);
}
.slot span {
  position: absolute;
  left: 3px;
  top: 1px;
  font-size: 10px;
  color: #fff;
  text-shadow: 1px 1px 0 #000;
}
</style>
</head>
<body>
<div id="overlay">
  <h1>MC.HTML</h1>
  <div class="controls">
    WASD — move<br>
    Space — jump<br>
    Mouse — look<br>
    Left click — break block<br>
    Right click — place block<br>
    1-7 / wheel — select block
  </div>
  <div class="play">Click to play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
'use strict';

const CHUNK = 16;
const HEIGHT = 80;

const BLOCKS = [0, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
const HOTBAR = [1, 2, 3, 4, 5, 6, 7];

const RGB = [];
for (let i = 0; i < BLOCKS.length; i++) {
  const c = BLOCKS[i];
  RGB.push([
    (c >> 16 & 255) / 255,
    (c >> 8 & 255) / 255,
    (c & 255) / 255
  ]);
}

const TRI_ORDER = [0, 1, 2, 0, 2, 3];

const FACE_DEFS = [
  { dir: [1, 0, 0],  shade: 0.8,  verts: [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]] },
  { dir: [-1, 0, 0], shade: 0.8,  verts: [[0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]] },
  { dir: [0, 1, 0],  shade: 1.0,  verts: [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]] },
  { dir: [0, -1, 0], shade: 0.55, verts: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]] },
  { dir: [0, 0, 1],  shade: 0.8,  verts: [[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]] },
  { dir: [0, 0, -1], shade: 0.8,  verts: [[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]] }
];

function colorToCss(c) {
  return '#' + ('000000' + c.toString(16)).slice(-6);
}

function hash2(x, z) {
  let h = (Math.imul(x, 374761393) + Math.imul(z, 668265263)) | 0;
  h ^= h >>> 13;
  h = Math.imul(h, 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967295;
}

function hash3(x, y, z) {
  let h = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1440638059)) | 0;
  h ^= h >>> 13;
  h = Math.imul(h, 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967295;
}

function smooth(t) {
  return t * t * (3 - 2 * t);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function noise2(x, z) {
  const xi = Math.floor(x);
  const zi = Math.floor(z);
  const xf = x - xi;
  const zf = z - zi;
  const u = smooth(xf);
  const v = smooth(zf);

  const a = hash2(xi, zi);
  const b = hash2(xi + 1, zi);
  const c = hash2(xi, zi + 1);
  const d = hash2(xi + 1, zi + 1);

  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}

function noise3(x, y, z) {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const zi = Math.floor(z);
  const xf = x - xi;
  const yf = y - yi;
  const zf = z - zi;

  const u = smooth(xf);
  const v = smooth(yf);
  const w = smooth(zf);

  const c000 = hash3(xi, yi, zi);
  const c100 = hash3(xi + 1, yi, zi);
  const c010 = hash3(xi, yi + 1, zi);
  const c110 = hash3(xi + 1, yi + 1, zi);
  const c001 = hash3(xi, yi, zi + 1);
  const c101 = hash3(xi + 1, yi, zi + 1);
  const c011 = hash3(xi, yi + 1, zi + 1);
  const c111 = hash3(xi + 1, yi + 1, zi + 1);

  const x00 = lerp(c000, c100, u);
  const x10 = lerp(c010, c110, u);
  const x01 = lerp(c001, c101, u);
  const x11 = lerp(c011, c111, u);

  const y0 = lerp(x00, x10, v);
  const y1 = lerp(x01, x11, v);

  return lerp(y0, y1, w);
}

function fractal2(x, z) {
  let total = 0;
  let amp = 0.5;
  let freq = 1;
  let norm = 0;

  for (let i = 0; i < 4; i++) {
    total += noise2(x * freq, z * freq) * amp;
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }

  return total / norm;
}

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));

const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(100, 200, 100);
scene.add(sun);

const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

const chunkMeshes = [];

const outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

const water = new THREE.Mesh(
  new THREE.PlaneGeometry(400, 400),
  new THREE.MeshBasicMaterial({
    color: 0x3f76e4,
    transparent: true,
    opacity: 0.65,
    depthWrite: false,
    side: THREE.DoubleSide
  })
);
water.rotation.x = -Math.PI / 2;
scene.add(water);

const cloudMat = new THREE.MeshBasicMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.75,
  depthWrite: false
});

const clouds = [];
for (let i = 0; i < 25; i++) {
  const h1 = hash2(i * 17 + 1, i * 31 + 7);
  const h2 = hash2(i * 53 + 11, i * 97 + 13);
  const h3 = hash2(i * 101 + 3, i * 13 + 19);

  const geo = new THREE.BoxGeometry(8 + h1 * 20, 1 + h2 * 2, 12 + h3 * 16);
  const cloud = new THREE.Mesh(geo, cloudMat);
  cloud.position.set(
    (h1 - 0.5) * 300,
    90 + (h2 - 0.5) * 10,
    (h2 - 0.5) * 300
  );
  scene.add(cloud);
  clouds.push(cloud);
}

const hotbar = document.getElementById('hotbar');
const slots = [];
let selected = 0;

HOTBAR.forEach(function (id, i) {
  const div = document.createElement('div');
  div.className = 'slot';
  div.style.background = colorToCss(BLOCKS[id]);

  const span = document.createElement('span');
  span.textContent = String(i + 1);
  div.appendChild(span);

  hotbar.appendChild(div);
  slots.push(div);
});

function updateHotbar() {
  for (let i = 0; i < slots.length; i++) {
    slots[i].classList.toggle('selected', i === selected);
  }
}
updateHotbar();

const HW = 0.3;
const PH = 1.8;
const EYE = 1.62;

const playerPos = new THREE.Vector3(8, 0, 8);
let vy = 0;
let yaw = 0;
let pitch = 0;
let onGround = false;
let locked = false;
let spawnY = 0;

const keys = {};

const raycaster = new THREE.Raycaster();
raycaster.far = 6;
const screenCenter = new THREE.Vector2(0, 0);

const chunkMap = new Map();

function key(cx, cz) {
  return cx + ',' + cz;
}

function getChunk(cx, cz) {
  return chunkMap.get(key(cx, cz));
}

function localIndex(x, y, z) {
  return (y * CHUNK + z) * CHUNK + x;
}

function getBlock(x, y, z) {
  if (y < 0 || y >= HEIGHT) return 0;

  const cx = Math.floor(x / CHUNK);
  const cz = Math.floor(z / CHUNK);
  const chunk = chunkMap.get(key(cx, cz));
  if (!chunk) return 0;

  const lx = x - cx * CHUNK;
  const lz = z - cz * CHUNK;
  if (lx < 0 || lx >= CHUNK || lz < 0 || lz >= CHUNK) return 0;

  return chunk.data[localIndex(lx, y, lz)];
}

function setBlock(x, y, z, id) {
  if (y < 0 || y >= HEIGHT) return false;

  const cx = Math.floor(x / CHUNK);
  const cz = Math.floor(z / CHUNK);
  const chunk = chunkMap.get(key(cx, cz));
  if (!chunk) return false;

  const lx = x - cx * CHUNK;
  const lz = z - cz * CHUNK;
  if (lx < 0 || lx >= CHUNK || lz < 0 || lz >= CHUNK) return false;

  chunk.data[localIndex(lx, y, lz)] = id;
  return true;
}

function terrainHeight(wx, wz) {
  const m = fractal2(wx * 0.004, wz * 0.004);
  const h = fractal2(wx * 0.02, wz * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}

function generateChunkData(cx, cz) {
  const data = new Uint8Array(CHUNK * CHUNK * HEIGHT);

  for (let lx = 0; lx < CHUNK; lx++) {
    for (let lz = 0; lz < CHUNK; lz++) {
      const wx = cx * CHUNK + lx;
      const wz = cz * CHUNK + lz;
      const H = terrainHeight(wx, wz);

      const surface = H >= 46 ? 7 : (H >= 37 ? 3 : (H <= 16 ? 4 : 1));
      const under = H <= 16 ? 4 : (H >= 37 ? 3 : 2);

      for (let y = 0; y <= H; y++) {
        let id;
        if (y === 0) {
          id = 3;
        } else if (y < H - 3) {
          id = 3;
        } else if (y < H) {
          id = under;
        } else {
          id = surface;
        }
        data[localIndex(lx, y, lz)] = id;
      }

      for (let y = 3; y <= H - 2; y++) {
        if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
          data[localIndex(lx, y, lz)] = 0;
        }
      }

      if (
        surface === 1 &&
        hash2(wx, wz) < 0.02 &&
        lx >= 2 && lx <= 13 &&
        lz >= 2 && lz <= 13 &&
        H + 6 < HEIGHT
      ) {
        for (let ty = 1; ty <= 4; ty++) {
          const yy = H + ty;
          if (yy < HEIGHT && data[localIndex(lx, yy, lz)] === 0) {
            data[localIndex(lx, yy, lz)] = 5;
          }
        }

        for (let dy = 3; dy <= 4; dy++) {
          const yy = H + dy;
          if (yy >= HEIGHT) continue;

          for (let ox = -2; ox <= 2; ox++) {
            for (let oz = -2; oz <= 2; oz++) {
              const xx = lx + ox;
              const zz = lz + oz;
              if (xx < 0 || xx >= CHUNK || zz < 0 || zz >= CHUNK) continue;
              if (data[localIndex(xx, yy, zz)] === 0) {
                data[localIndex(xx, yy, zz)] = 6;
              }
            }
          }
        }

        const yy = H + 5;
        if (yy < HEIGHT) {
          for (let ox = -1; ox <= 1; ox++) {
            for (let oz = -1; oz <= 1; oz++) {
              const xx = lx + ox;
              const zz = lz + oz;
              if (xx >= 0 && xx < CHUNK && zz >= 0 && zz < CHUNK && data[localIndex(xx, yy, zz)] === 0) {
                data[localIndex(xx, yy, zz)] = 6;
              }
            }
          }
        }

        const topY = H + 6;
        if (topY < HEIGHT && data[localIndex(lx, topY, lz)] === 0) {
          data[localIndex(lx, topY, lz)] = 6;
        }
      }
    }
  }

  chunkMap.set(key(cx, cz), { data: data, mesh: null });
}

function removeMesh(mesh) {
  scene.remove(mesh);
  mesh.geometry.dispose();
  const i = chunkMeshes.indexOf(mesh);
  if (i >= 0) chunkMeshes.splice(i, 1);
}

function buildChunkMesh(cx, cz) {
  const chunk = getChunk(cx, cz);
  if (!chunk) return;

  if (chunk.mesh) {
    removeMesh(chunk.mesh);
    chunk.mesh = null;
  }

  const positions = [];
  const normals = [];
  const colors = [];
  const data = chunk.data;

  for (let y = 0; y < HEIGHT; y++) {
    for (let z = 0; z < CHUNK; z++) {
      for (let x = 0; x < CHUNK; x++) {
        const id = data[localIndex(x, y, z)];
        if (id === 0) continue;

        const wx = cx * CHUNK + x;
        const wz = cz * CHUNK + z;
        const wy = y;
        const rgb = RGB[id];

        for (let f = 0; f < FACE_DEFS.length; f++) {
          const face = FACE_DEFS[f];
          const nx = wx + face.dir[0];
          const ny = wy + face.dir[1];
          const nz = wz + face.dir[2];

          if (getBlock(nx, ny, nz) === 0) {
            const s = face.shade;
            const cr = rgb[0] * s;
            const cg = rgb[1] * s;
            const cb = rgb[2] * s;
            const v = face.verts;

            for (let i = 0; i < 6; i++) {
              const vi = TRI_ORDER[i];
              positions.push(wx + v[vi][0], wy + v[vi][1], wz + v[vi][2]);
              normals.push(face.dir[0], face.dir[1], face.dir[2]);
              colors.push(cr, cg, cb);
            }
          }
        }
      }
    }
  }

  if (positions.length === 0) return;

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.computeBoundingSphere();

  const mesh = new THREE.Mesh(geometry, blockMaterial);
  scene.add(mesh);
  chunkMeshes.push(mesh);
  chunk.mesh = mesh;
}

function rebuildExistingChunk(cx, cz) {
  const chunk = getChunk(cx, cz);
  if (chunk && chunk.mesh) {
    buildChunkMesh(cx, cz);
  }
}

function rebuildAround(bx, by, bz) {
  const cx = Math.floor(bx / CHUNK);
  const cz = Math.floor(bz / CHUNK);

  rebuildExistingChunk(cx, cz);

  const lx = bx - cx * CHUNK;
  const lz = bz - cz * CHUNK;

  if (lx === 0) rebuildExistingChunk(cx - 1, cz);
  if (lx === CHUNK - 1) rebuildExistingChunk(cx + 1, cz);
  if (lz === 0) rebuildExistingChunk(cx, cz - 1);
  if (lz === CHUNK - 1) rebuildExistingChunk(cx, cz + 1);
}

function hasDataNeighbors(cx, cz) {
  return chunkMap.has(key(cx + 1, cz)) &&
         chunkMap.has(key(cx - 1, cz)) &&
         chunkMap.has(key(cx, cz + 1)) &&
         chunkMap.has(key(cx, cz - 1));
}

function rebuildNeighborKeys(keyList) {
  if (keyList.length === 0) return;

  const set = new Set();

  for (let i = 0; i < keyList.length; i++) {
    const parts = keyList[i].split(',');
    const cx = parseInt(parts[0], 10);
    const cz = parseInt(parts[1], 10);

    set.add(key(cx + 1, cz));
    set.add(key(cx - 1, cz));
    set.add(key(cx, cz + 1));
    set.add(key(cx, cz - 1));
  }

  for (const nk of set) {
    const parts = nk.split(',');
    rebuildExistingChunk(parseInt(parts[0], 10), parseInt(parts[1], 10));
  }
}

function updateWorldGeneration() {
  const pcx = Math.floor(playerPos.x / CHUNK);
  const pcz = Math.floor(playerPos.z / CHUNK);

  const generatedKeys = [];
  let generated = 0;

  for (let r = 0; r <= 5 && generated < 4; r++) {
    for (let dx = -r; dx <= r; dx++) {
      for (let dz = -r; dz <= r; dz++) {
        if (r > 0 && Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;

        const cx = pcx + dx;
        const cz = pcz + dz;
        const k = key(cx, cz);

        if (!chunkMap.has(k)) {
          generateChunkData(cx, cz);
          generatedKeys.push(k);
          generated++;
          if (generated >= 4) break;
        }
      }
      if (generated >= 4) break;
    }
  }

  rebuildNeighborKeys(generatedKeys);

  let built = 0;
  for (let r = 0; r <= 4 && built < 2; r++) {
    for (let dx = -r; dx <= r; dx++) {
      for (let dz = -r; dz <= r; dz++) {
        if (r > 0 && Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;

        const cx = pcx + dx;
        const cz = pcz + dz;
        const chunk = getChunk(cx, cz);

        if (chunk && !chunk.mesh && hasDataNeighbors(cx, cz)) {
          buildChunkMesh(cx, cz);
          built++;
          if (built >= 2) break;
        }
      }
      if (built >= 2) break;
    }
  }

  const toDelete = [];
  const deleteNeighbors = new Set();

  for (const entry of chunkMap) {
    const ck = entry[0];
    const parts = ck.split(',');
    const cx = parseInt(parts[0], 10);
    const cz = parseInt(parts[1], 10);

    if (Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz)) > 7) {
      toDelete.push(ck);
      deleteNeighbors.add(key(cx + 1, cz));
      deleteNeighbors.add(key(cx - 1, cz));
      deleteNeighbors.add(key(cx, cz + 1));
      deleteNeighbors.add(key(cx, cz - 1));
    }
  }

  for (let i = 0; i < toDelete.length; i++) {
    const chunk = chunkMap.get(toDelete[i]);
    if (chunk && chunk.mesh) removeMesh(chunk.mesh);
    chunkMap.delete(toDelete[i]);
  }

  for (const nk of deleteNeighbors) {
    const parts = nk.split(',');
    rebuildExistingChunk(parseInt(parts[0], 10), parseInt(parts[1], 10));
  }
}

function collides() {
  const minX = Math.floor(playerPos.x - HW);
  const maxX = Math.floor(playerPos.x + HW - 1e-7);
  const minY = Math.floor(playerPos.y);
  const maxY = Math.floor(playerPos.y + PH - 1e-7);
  const minZ = Math.floor(playerPos.z - HW);
  const maxZ = Math.floor(playerPos.z + HW - 1e-7);

  for (let x = minX; x <= maxX; x++) {
    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (getBlock(x, y, z) !== 0) return true;
      }
    }
  }

  return false;
}

function moveAxis(axis, delta) {
  if (delta === 0) return;

  const step = 0.5;
  let remaining = delta;

  while (Math.abs(remaining) > 1e-9) {
    const d = Math.sign(remaining) * Math.min(step, Math.abs(remaining));
    playerPos[axis] += d;

    if (collides()) {
      playerPos[axis] -= d;
      if (axis === 'y') {
        if (delta < 0) onGround = true;
        vy = 0;
      }
      return;
    }

    remaining -= d;
  }
}

function blockOverlapsPlayer(bx, by, bz) {
  return bx < playerPos.x + HW && bx + 1 > playerPos.x - HW &&
         by < playerPos.y + PH && by + 1 > playerPos.y &&
         bz < playerPos.z + HW && bz + 1 > playerPos.z - HW;
}

function respawn() {
  playerPos.set(8, spawnY, 8);
  vy = 0;
  yaw = 0;
  pitch = 0;
  camera.rotation.x = 0;
  camera.rotation.y = 0;
}

function updatePlayer(dt) {
  let ix = 0;
  let iz = 0;

  if (keys['KeyW']) iz = 1;
  if (keys['KeyS']) iz = -1;
  if (keys['KeyA']) ix = -1;
  if (keys['KeyD']) ix = 1;

  const speed = 5.5;
  const dx = (Math.cos(yaw) * ix - Math.sin(yaw) * iz) * speed * dt;
  const dz = (-Math.sin(yaw) * ix - Math.cos(yaw) * iz) * speed * dt;

  if (keys['Space'] && onGround) {
    vy = 8.5;
  }

  vy -= 25 * dt;
  onGround = false;

  moveAxis('x', dx);
  moveAxis('z', dz);
  moveAxis('y', vy * dt);

  if (playerPos.y < -20) {
    respawn();
  }
}

let targetInfo = null;

function updateTarget() {
  if (!locked) {
    targetInfo = null;
    outline.visible = false;
    return;
  }

  raycaster.far = 6;
  raycaster.setFromCamera(screenCenter, camera);

  const hits = raycaster.intersectObjects(chunkMeshes, false);

  if (hits.length > 0) {
    const hit = hits[0];
    const p = hit.point;
    const n = hit.face.normal;

    const tx = Math.floor(p.x - n.x * 0.5);
    const ty = Math.floor(p.y - n.y * 0.5);
    const tz = Math.floor(p.z - n.z * 0.5);

    if (ty >= 0 && ty < HEIGHT && getBlock(tx, ty, tz) !== 0) {
      const px = Math.floor(p.x + n.x * 0.5);
      const py = Math.floor(p.y + n.y * 0.5);
      const pz = Math.floor(p.z + n.z * 0.5);

      targetInfo = { x: tx, y: ty, z: tz, px: px, py: py, pz: pz };
      outline.position.set(tx + 0.5, ty + 0.5, tz + 0.5);
      outline.visible = true;
      return;
    }
  }

  targetInfo = null;
  outline.visible = false;
}

function breakBlock() {
  if (!locked || !targetInfo) return;

  const x = targetInfo.x;
  const y = targetInfo.y;
  const z = targetInfo.z;

  if (y === 0) return;
  if (getBlock(x, y, z) === 0) return;

  if (setBlock(x, y, z, 0)) {
    rebuildAround(x, y, z);
  }
}

function placeBlock() {
  if (!locked || !targetInfo) return;

  const x = targetInfo.px;
  const y = targetInfo.py;
  const z = targetInfo.pz;

  if (y < 0 || y >= HEIGHT) return;
  if (getBlock(x, y, z) !== 0) return;
  if (blockOverlapsPlayer(x, y, z)) return;

  if (setBlock(x, y, z, HOTBAR[selected])) {
    rebuildAround(x, y, z);
  }
}

const overlay = document.getElementById('overlay');

function requestLock() {
  try {
    const p = renderer.domElement.requestPointerLock();
    if (p && typeof p.catch === 'function') {
      p.catch(function () {});
    }
  } catch (e) {}
}

overlay.addEventListener('click', requestLock);

document.addEventListener('pointerlockchange', function () {
  locked = document.pointerLockElement === renderer.domElement;
  overlay.style.display = locked ? 'none' : 'flex';

  if (!locked) {
    for (const k in keys) {
      keys[k] = false;
    }
  }
});

document.addEventListener('pointerlockerror', function () {
  locked = false;
  overlay.style.display = 'flex';
});

document.addEventListener('mousemove', function (e) {
  if (!locked) return;

  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;

  const lim = Math.PI / 2 - 0.01;
  if (pitch > lim) pitch = lim;
  if (pitch < -lim) pitch = -lim;

  camera.rotation.x = pitch;
  camera.rotation.y = yaw;
});

document.addEventListener('mousedown', function (e) {
  if (!locked) return;

  if (e.button === 0) {
    e.preventDefault();
    breakBlock();
  } else if (e.button === 2) {
    e.preventDefault();
    placeBlock();
  }
});

document.addEventListener('contextmenu', function (e) {
  e.preventDefault();
});

window.addEventListener('keydown', function (e) {
  keys[e.code] = true;

  if (e.code === 'Space') {
    e.preventDefault();
  }

  if (e.code >= 'Digit1' && e.code <= 'Digit7') {
    selected = parseInt(e.code.charAt(5), 10) - 1;
    updateHotbar();
  }
});

window.addEventListener('keyup', function (e) {
  keys[e.code] = false;
});

window.addEventListener('wheel', function (e) {
  if (!locked) return;
  e.preventDefault();

  const dir = e.deltaY > 0 ? 1 : (e.deltaY < 0 ? -1 : 0);
  if (dir !== 0) {
    selected = (selected + dir + HOTBAR.length) % HOTBAR.length;
    updateHotbar();
  }
}, { passive: false });

window.addEventListener('resize', function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

generateChunkData(0, 0);
spawnY = terrainHeight(8, 8) + 1;
playerPos.set(8, spawnY, 8);
camera.position.set(playerPos.x, playerPos.y + EYE, playerPos.z);

const clock = new THREE.Clock();

function updateClouds(dt) {
  const range = 300;

  for (let i = 0; i < clouds.length; i++) {
    const c = clouds[i];

    c.position.x += dt * 1.5;
    c.position.z += dt * 0.5;

    if (c.position.x > playerPos.x + range / 2) c.position.x -= range;
    if (c.position.x < playerPos.x - range / 2) c.position.x += range;
    if (c.position.z > playerPos.z + range / 2) c.position.z -= range;
    if (c.position.z < playerPos.z - range / 2) c.position.z += range;
  }
}

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.1);

  updateWorldGeneration();

  if (locked) {
    updatePlayer(dt);
  }

  if (playerPos.y < -20) {
    respawn();
  }

  updateTarget();
  updateClouds(dt);

  water.position.set(playerPos.x, 14.3, playerPos.z);
  camera.position.set(playerPos.x, playerPos.y + EYE, playerPos.z);

  renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
```