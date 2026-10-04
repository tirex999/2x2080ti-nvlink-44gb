

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
    overflow: hidden;
    background: #000;
    font-family: Arial, sans-serif;
  }
  canvas#c {
    display: block;
    width: 100vw;
    height: 100vh;
  }
  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.78);
    color: #fff;
    z-index: 30;
    text-align: center;
    cursor: pointer;
    user-select: none;
  }
  #overlay h1 {
    margin: 0 0 18px 0;
    font-size: 72px;
    letter-spacing: 6px;
    text-shadow: 5px 5px 0 #000;
  }
  #overlay .controls {
    font-size: 16px;
    line-height: 1.7;
    margin-bottom: 28px;
  }
  #overlay .play {
    font-size: 26px;
    font-weight: bold;
  }
  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 18px;
    height: 18px;
    transform: translate(-50%, -50%);
    z-index: 10;
    pointer-events: none;
  }
  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: rgba(255, 255, 255, 0.88);
  }
  #crosshair::before {
    left: 8px;
    top: 0;
    width: 2px;
    height: 18px;
  }
  #crosshair::after {
    left: 0;
    top: 8px;
    width: 18px;
    height: 2px;
  }
  #hotbar {
    position: fixed;
    left: 50%;
    bottom: 16px;
    transform: translateX(-50%);
    display: flex;
    gap: 4px;
    padding: 6px;
    background: rgba(0, 0, 0, 0.45);
    border: 2px solid rgba(255, 255, 255, 0.25);
    z-index: 10;
    pointer-events: none;
  }
  .slot {
    width: 44px;
    height: 44px;
    box-sizing: border-box;
    border: 2px solid rgba(255, 255, 255, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: #fff;
    text-shadow: 1px 1px 0 #000;
    user-select: none;
  }
  .slot.selected {
    border-color: #fff;
    box-shadow: 0 0 0 2px #fff inset;
  }
</style>
</head>
<body>
<div id="overlay">
  <h1>MC</h1>
  <div class="controls">
    WASD — move<br>
    Space — jump<br>
    Mouse — look<br>
    Left click — break<br>
    Right click — place<br>
    1–7 / mouse wheel — select block
  </div>
  <div class="play">Click to play</div>
</div>

<div id="crosshair"></div>
<div id="hotbar"></div>
<canvas id="c"></canvas>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
'use strict';

const CHUNK_SIZE = 16;
const CHUNK_HEIGHT = 80;

const BLOCK_COLORS = [
  0,
  0x4caf50, // grass
  0x795548, // dirt
  0x9e9e9e, // stone
  0xe7d9a8, // sand
  0x8d6e63, // wood
  0x2e7d32, // leaves
  0xffffff  // snow
];

const HOTBAR_IDS = [1, 2, 3, 4, 5, 6, 7];

function hexToRgb(hex) {
  return [
    ((hex >> 16) & 255) / 255,
    ((hex >> 8) & 255) / 255,
    (hex & 255) / 255
  ];
}

const COLORS = BLOCK_COLORS.map(hexToRgb);

const FACES = [
  {
    dir: [1, 0, 0],
    shade: 0.8,
    verts: [
      [1, 0, 1],
      [1, 0, 0],
      [1, 1, 0],
      [1, 1, 1]
    ]
  },
  {
    dir: [-1, 0, 0],
    shade: 0.8,
    verts: [
      [0, 0, 0],
      [0, 0, 1],
      [0, 1, 1],
      [0, 1, 0]
    ]
  },
  {
    dir: [0, 1, 0],
    shade: 1.0,
    verts: [
      [0, 1, 1],
      [1, 1, 1],
      [1, 1, 0],
      [0, 1, 0]
    ]
  },
  {
    dir: [0, -1, 0],
    shade: 0.55,
    verts: [
      [0, 0, 0],
      [1, 0, 0],
      [1, 0, 1],
      [0, 0, 1]
    ]
  },
  {
    dir: [0, 0, 1],
    shade: 0.8,
    verts: [
      [0, 0, 1],
      [1, 0, 1],
      [1, 1, 1],
      [0, 1, 1]
    ]
  },
  {
    dir: [0, 0, -1],
    shade: 0.8,
    verts: [
      [1, 0, 0],
      [0, 0, 0],
      [0, 1, 0],
      [1, 1, 0]
    ]
  }
];

const TRI = [0, 1, 2, 0, 2, 3];

const chunks = new Map();
const chunkMeshes = [];

function key(cx, cz) {
  return cx + ',' + cz;
}

function idx(lx, y, lz) {
  return (y * 16 + lz) * 16 + lx;
}

function hash2(x, y) {
  let h = Math.imul(x, 374761393) ^ Math.imul(y, 668265263);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

function hash3(x, y, z) {
  let h = Math.imul(x, 374761393) ^ Math.imul(y, 668265263) ^ Math.imul(z, 1274126177);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
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

  const ab = lerp(a, b, u);
  const cd = lerp(c, d, u);
  return lerp(ab, cd, v);
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

  const x00 = lerp(hash3(xi, yi, zi), hash3(xi + 1, yi, zi), u);
  const x10 = lerp(hash3(xi, yi + 1, zi), hash3(xi + 1, yi + 1, zi), u);
  const x01 = lerp(hash3(xi, yi, zi + 1), hash3(xi + 1, yi, zi + 1), u);
  const x11 = lerp(hash3(xi, yi + 1, zi + 1), hash3(xi + 1, yi + 1, zi + 1), u);

  const y0 = lerp(x00, x10, v);
  const y1 = lerp(x01, x11, v);
  return lerp(y0, y1, w);
}

function fractal2(x, z) {
  let amp = 1;
  let freq = 1;
  let sum = 0;
  let norm = 0;

  for (let i = 0; i < 4; i++) {
    sum += amp * noise2(x * freq, z * freq);
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }

  return sum / norm;
}

function terrainHeight(x, z) {
  const m = fractal2(x * 0.004, z * 0.004);
  const h = fractal2(x * 0.02, z * 0.02);
  return Math.floor(5 + m * m * 58 + h * 10);
}

function setLocal(blocks, lx, y, lz, id, onlyAir) {
  if (y < 0 || y >= CHUNK_HEIGHT) return;
  if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE) return;

  const i = idx(lx, y, lz);
  if (onlyAir && blocks[i] !== 0) return;
  blocks[i] = id;
}

function generateChunkData(cx, cz) {
  const blocks = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
  const ox = cx * CHUNK_SIZE;
  const oz = cz * CHUNK_SIZE;

  for (let lz = 0; lz < CHUNK_SIZE; lz++) {
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      const x = ox + lx;
      const z = oz + lz;
      const H = terrainHeight(x, z);
      const top = Math.min(H, CHUNK_HEIGHT - 1);

      for (let y = 0; y <= top; y++) {
        let id = 0;

        if (y === 0) {
          id = 3;
        } else if (y < H - 3) {
          id = 3;
        } else if (y < H) {
          if (H <= 16) id = 4;
          else if (H >= 37) id = 3;
          else id = 2;
        } else {
          if (H >= 46) id = 7;
          else if (H >= 37) id = 3;
          else if (H <= 16) id = 4;
          else id = 1;
        }

        blocks[idx(lx, y, lz)] = id;
      }

      for (let y = 3; y <= H - 2 && y < CHUNK_HEIGHT; y++) {
        if (noise3(x * 0.09, y * 0.09, z * 0.09) > 0.67) {
          blocks[idx(lx, y, lz)] = 0;
        }
      }

      if (
        H >= 17 &&
        H <= 36 &&
        H + 8 < CHUNK_HEIGHT &&
        lx >= 2 && lx < 14 &&
        lz >= 2 && lz < 14 &&
        hash2(x + 12345, z - 67890) < 0.02
      ) {
        for (let i = 1; i <= 4; i++) {
          setLocal(blocks, lx, H + i, lz, 5, true);
        }

        for (let ly = H + 5; ly <= H + 6; ly++) {
          for (let dx = -2; dx <= 2; dx++) {
            for (let dz = -2; dz <= 2; dz++) {
              setLocal(blocks, lx + dx, ly, lz + dz, 6, true);
            }
          }
        }

        for (let dx = -1; dx <= 1; dx++) {
          for (let dz = -1; dz <= 1; dz++) {
            setLocal(blocks, lx + dx, H + 7, lz + dz, 6, true);
          }
        }

        setLocal(blocks, lx, H + 8, lz, 6, true);
      }
    }
  }

  return blocks;
}

function ensureChunkData(cx, cz) {
  const k = key(cx, cz);
  if (!chunks.has(k)) {
    chunks.set(k, {
      blocks: generateChunkData(cx, cz),
      mesh: null
    });
  }
}

function readBlock(x, y, z) {
  if (y < 0 || y >= CHUNK_HEIGHT) return 0;

  const cx = Math.floor(x / CHUNK_SIZE);
  const cz = Math.floor(z / CHUNK_SIZE);
  const ch = chunks.get(key(cx, cz));
  if (!ch) return 0;

  const lx = x - cx * CHUNK_SIZE;
  const lz = z - cz * CHUNK_SIZE;
  return ch.blocks[idx(lx, y, lz)];
}

function writeBlock(x, y, z, id) {
  if (y < 0 || y >= CHUNK_HEIGHT) return;

  const cx = Math.floor(x / CHUNK_SIZE);
  const cz = Math.floor(z / CHUNK_SIZE);
  const ch = chunks.get(key(cx, cz));
  if (!ch) return;

  const lx = x - cx * CHUNK_SIZE;
  const lz = z - cz * CHUNK_SIZE;
  ch.blocks[idx(lx, y, lz)] = id;
}

let scene;
let camera;
let renderer;
let raycaster;
let center;
let blockMaterial;
let water;
let outline;
let clock;

const clouds = [];

let yaw = 0;
let pitch = 0;

const player = {
  x: 8,
  y: 30,
  z: 8,
  vx: 0,
  vy: 0,
  vz: 0,
  onGround: false
};

const keys = {};

let selected = 0;
let targetBlock = null;
let placeTarget = null;

function removeChunkMesh(ch) {
  if (!ch || !ch.mesh) return;

  scene.remove(ch.mesh);

  const i = chunkMeshes.indexOf(ch.mesh);
  if (i >= 0) chunkMeshes.splice(i, 1);

  ch.mesh.geometry.dispose();
  ch.mesh = null;
}

function buildChunkMesh(cx, cz) {
  const ch = chunks.get(key(cx, cz));
  if (!ch) return;

  removeChunkMesh(ch);

  const positions = [];
  const normals = [];
  const colors = [];

  const ox = cx * CHUNK_SIZE;
  const oz = cz * CHUNK_SIZE;

  for (let y = 0; y < CHUNK_HEIGHT; y++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      for (let lx = 0; lx < CHUNK_SIZE; lx++) {
        const id = ch.blocks[idx(lx, y, lz)];
        if (id === 0) continue;

        const x = ox + lx;
        const z = oz + lz;
        const col = COLORS[id];

        for (let f = 0; f < FACES.length; f++) {
          const face = FACES[f];

          const nx = x + face.dir[0];
          const ny = y + face.dir[1];
          const nz = z + face.dir[2];

          if (readBlock(nx, ny, nz) !== 0) continue;

          const shade = face.shade;
          const cr = col[0] * shade;
          const cg = col[1] * shade;
          const cb = col[2] * shade;

          for (let ti = 0; ti < 6; ti++) {
            const v = face.verts[TRI[ti]];

            positions.push(
              x + v[0],
              y + v[1],
              z + v[2]
            );

            normals.push(
              face.dir[0],
              face.dir[1],
              face.dir[2]
            );

            colors.push(cr, cg, cb);
          }
        }
      }
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3));
  geo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(normals), 3));
  geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(colors), 3));

  const mesh = new THREE.Mesh(geo, blockMaterial);
  mesh.position.set(0, 0, 0);

  scene.add(mesh);
  ch.mesh = mesh;
  chunkMeshes.push(mesh);
}

function rebuildChunk(cx, cz) {
  const ch = chunks.get(key(cx, cz));
  if (ch && ch.mesh) {
    buildChunkMesh(cx, cz);
  }
}

function rebuildAround(x, z) {
  const cx = Math.floor(x / CHUNK_SIZE);
  const cz = Math.floor(z / CHUNK_SIZE);

  rebuildChunk(cx, cz);

  const lx = x - cx * CHUNK_SIZE;
  const lz = z - cz * CHUNK_SIZE;

  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);
}

function updateChunks() {
  const pcx = Math.floor(player.x / CHUNK_SIZE);
  const pcz = Math.floor(player.z / CHUNK_SIZE);

  const gen = [];
  for (let dz = -5; dz <= 5; dz++) {
    for (let dx = -5; dx <= 5; dx++) {
      const cx = pcx + dx;
      const cz = pcz + dz;
      if (!chunks.has(key(cx, cz))) {
        gen.push({
          cx: cx,
          cz: cz,
          d: Math.max(Math.abs(dx), Math.abs(dz))
        });
      }
    }
  }

  gen.sort((a, b) => a.d - b.d);

  for (let i = 0; i < gen.length && i < 4; i++) {
    ensureChunkData(gen[i].cx, gen[i].cz);
  }

  const build = [];
  for (let dz = -4; dz <= 4; dz++) {
    for (let dx = -4; dx <= 4; dx++) {
      const cx = pcx + dx;
      const cz = pcz + dz;
      const ch = chunks.get(key(cx, cz));

      if (ch && !ch.mesh) {
        if (
          chunks.has(key(cx + 1, cz)) &&
          chunks.has(key(cx - 1, cz)) &&
          chunks.has(key(cx, cz + 1)) &&
          chunks.has(key(cx, cz - 1))
        ) {
          build.push({
            cx: cx,
            cz: cz,
            d: Math.max(Math.abs(dx), Math.abs(dz))
          });
        }
      }
    }
  }

  build.sort((a, b) => a.d - b.d);

  for (let i = 0; i < build.length && i < 2; i++) {
    buildChunkMesh(build[i].cx, build[i].cz);
  }

  const del = [];
  for (const k of chunks.keys()) {
    const parts = k.split(',');
    const cx = parseInt(parts[0], 10);
    const cz = parseInt(parts[1], 10);

    if (Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz)) > 7) {
      del.push(k);
    }
  }

  for (const k of del) {
    const ch = chunks.get(k);
    removeChunkMesh(ch);
    chunks.delete(k);
  }
}

function collides(px, py, pz) {
  const EPS_XZ = 0.0001;
  const EPS_Y = 0.0000001;

  const minX = Math.floor(px - 0.3 - EPS_XZ);
  const maxX = Math.floor(px + 0.3 - EPS_XZ);
  const minY = Math.floor(py + EPS_Y);
  const maxY = Math.floor(py + 1.8 - EPS_Y);
  const minZ = Math.floor(pz - 0.3 - EPS_XZ);
  const maxZ = Math.floor(pz + 0.3 - EPS_XZ);

  for (let x = minX; x <= maxX; x++) {
    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (readBlock(x, y, z) !== 0) return true;
      }
    }
  }

  return false;
}

function overlapsPlayer(bx, by, bz) {
  const EPS = 0.0001;

  const minX = player.x - 0.3 + EPS;
  const maxX = player.x + 0.3 - EPS;
  const minY = player.y + EPS;
  const maxY = player.y + 1.8 - EPS;
  const minZ = player.z - 0.3 + EPS;
  const maxZ = player.z + 0.3 - EPS;

  return (
    bx + 1 > minX && bx < maxX &&
    by + 1 > minY && by < maxY &&
    bz + 1 > minZ && bz < maxZ
  );
}

function spawn() {
  player.x = 8;
  player.z = 8;
  player.y = terrainHeight(8, 8) + 2;
  player.vx = 0;
  player.vy = 0;
  player.vz = 0;
  player.onGround = false;
}

function isLocked() {
  return document.pointerLockElement === renderer.domElement;
}

function updatePhysics(dt) {
  let mx = 0;
  let mz = 0;

  if (isLocked()) {
    const speed = 5.5;

    const forwardX = -Math.sin(yaw);
    const forwardZ = -Math.cos(yaw);
    const rightX = Math.cos(yaw);
    const rightZ = -Math.sin(yaw);

    if (keys['KeyW']) {
      mx += forwardX;
      mz += forwardZ;
    }
    if (keys['KeyS']) {
      mx -= forwardX;
      mz -= forwardZ;
    }
    if (keys['KeyD']) {
      mx += rightX;
      mz += rightZ;
    }
    if (keys['KeyA']) {
      mx -= rightX;
      mz -= rightZ;
    }

    const len = Math.hypot(mx, mz);
    if (len > 0) {
      mx = (mx / len) * speed;
      mz = (mz / len) * speed;
    }

    if (keys['Space'] && player.onGround) {
      player.vy = 8.5;
      player.onGround = false;
    }
  }

  player.vx = mx;
  player.vz = mz;

  player.vy -= 25 * dt;
  if (player.vy < -50) player.vy = -50;

  const ox = player.x;
  player.x += player.vx * dt;
  if (collides(player.x, player.y, player.z)) {
    player.x = ox;
  }

  const oz = player.z;
  player.z += player.vz * dt;
  if (collides(player.x, player.y, player.z)) {
    player.z = oz;
  }

  const oy = player.y;
  const oldVy = player.vy;

  player.y += player.vy * dt;
  if (collides(player.x, player.y, player.z)) {
    player.y = oy;
    if (oldVy < 0) player.onGround = true;
    player.vy = 0;
  } else {
    player.onGround = false;
  }

  if (player.y < -20) {
    spawn();
  }
}

function updateTarget() {
  targetBlock = null;
  placeTarget = null;

  if (isLocked()) {
    raycaster.setFromCamera(center, camera);
    const hits = raycaster.intersectObjects(chunkMeshes, false);

    if (hits.length) {
      const hit = hits[0];
      const p = hit.point;
      const n = hit.face.normal;

      targetBlock = {
        x: Math.floor(p.x - n.x * 0.5),
        y: Math.floor(p.y - n.y * 0.5),
        z: Math.floor(p.z - n.z * 0.5)
      };

      placeTarget = {
        x: Math.floor(p.x + n.x * 0.5),
        y: Math.floor(p.y + n.y * 0.5),
        z: Math.floor(p.z + n.z * 0.5)
      };

      outline.visible = true;
      outline.position.set(
        targetBlock.x + 0.5,
        targetBlock.y + 0.5,
        targetBlock.z + 0.5
      );
    }
  }

  if (!targetBlock) {
    outline.visible = false;
  }
}

function breakBlock() {
  if (!isLocked() || !targetBlock) return;

  const b = targetBlock;
  if (b.y <= 0) return;

  writeBlock(b.x, b.y, b.z, 0);
  rebuildAround(b.x, b.z);
}

function placeBlock() {
  if (!isLocked() || !placeTarget) return;

  const b = placeTarget;
  if (b.y < 0 || b.y >= CHUNK_HEIGHT) return;
  if (readBlock(b.x, b.y, b.z) !== 0) return;
  if (overlapsPlayer(b.x, b.y, b.z)) return;

  writeBlock(b.x, b.y, b.z, HOTBAR_IDS[selected]);
  rebuildAround(b.x, b.z);
}

function updateClouds(dt) {
  for (const c of clouds) {
    c.mesh.position.x += c.vx * dt;
    c.mesh.position.z += c.vz * dt;
    c.mesh.position.y = 90;

    if (c.mesh.position.x > player.x + 200) c.mesh.position.x -= 400;
    if (c.mesh.position.x < player.x - 200) c.mesh.position.x += 400;
    if (c.mesh.position.z > player.z + 200) c.mesh.position.z -= 400;
    if (c.mesh.position.z < player.z - 200) c.mesh.position.z += 400;
  }
}

function hexCss(hex) {
  return '#' + hex.toString(16).padStart(6, '0');
}

function createHotbar() {
  const bar = document.getElementById('hotbar');

  for (let i = 0; i < HOTBAR_IDS.length; i++) {
    const id = HOTBAR_IDS[i];
    const slot = document.createElement('div');
    slot.className = 'slot';
    slot.style.background = hexCss(BLOCK_COLORS[id]);
    slot.textContent = String(i + 1);
    bar.appendChild(slot);
  }

  updateHotbar();
}

function updateHotbar() {
  const slots = document.querySelectorAll('.slot');
  for (let i = 0; i < slots.length; i++) {
    slots[i].classList.toggle('selected', i === selected);
  }
}

function addEventListeners() {
  const overlay = document.getElementById('overlay');

  overlay.addEventListener('click', () => {
    renderer.domElement.requestPointerLock();
  });

  document.addEventListener('pointerlockchange', () => {
    const locked = isLocked();
    overlay.style.display = locked ? 'none' : 'flex';

    if (!locked) {
      keys['KeyW'] = false;
      keys['KeyA'] = false;
      keys['KeyS'] = false;
      keys['KeyD'] = false;
      keys['Space'] = false;
    }
  });

  document.addEventListener('mousemove', (e) => {
    if (!isLocked()) return;

    yaw -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;

    const lim = Math.PI / 2 - 0.01;
    pitch = Math.max(-lim, Math.min(lim, pitch));
  });

  document.addEventListener('mousedown', (e) => {
    if (!isLocked()) return;

    if (e.button === 0) {
      breakBlock();
    } else if (e.button === 2) {
      placeBlock();
    }
  });

  document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
  });

  document.addEventListener('wheel', (e) => {
    if (!isLocked()) return;

    e.preventDefault();
    const dir = e.deltaY > 0 ? 1 : -1;
    selected = (selected + dir + 7) % 7;
    updateHotbar();
  }, { passive: false });

  document.addEventListener('keydown', (e) => {
    keys[e.code] = true;

    if (e.code === 'Space') {
      e.preventDefault();
    }

    if (e.code.startsWith('Digit')) {
      const n = parseInt(e.code.slice(5), 10);
      if (n >= 1 && n <= 7) {
        selected = n - 1;
        updateHotbar();
      }
    }
  });

  document.addEventListener('keyup', (e) => {
    keys[e.code] = false;
  });

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.1);

  updateChunks();
  updatePhysics(dt);

  camera.position.set(player.x, player.y + 1.62, player.z);
  camera.rotation.set(pitch, yaw, 0, 'YXZ');

  updateTarget();
  updateClouds(dt);

  water.position.set(player.x, 14.3, player.z);

  renderer.render(scene, camera);
}

function init() {
  const canvas = document.getElementById('c');

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x87ceeb, 1);

  scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    400
  );
  camera.rotation.order = 'YXZ';

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));

  const dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(0.5, 1, 0.25);
  scene.add(dir);

  blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

  raycaster = new THREE.Raycaster();
  raycaster.far = 6;
  center = new THREE.Vector2(0, 0);

  const outlineGeo = new THREE.BoxGeometry(1.002, 1.002, 1.002);
  outline = new THREE.LineSegments(
    new THREE.EdgesGeometry(outlineGeo),
    new THREE.LineBasicMaterial({
      color: 0x000000,
      depthTest: false,
      transparent: true,
      opacity: 0.8
    })
  );
  outline.visible = false;
  scene.add(outline);

  const waterGeo = new THREE.PlaneGeometry(400, 400);
  waterGeo.rotateX(-Math.PI / 2);

  water = new THREE.Mesh(
    waterGeo,
    new THREE.MeshBasicMaterial({
      color: 0x3399ff,
      transparent: true,
      opacity: 0.55,
      depthWrite: false
    })
  );
  water.position.set(8, 14.3, 8);
  scene.add(water);

  const cloudMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.8,
    depthWrite: false
  });

  for (let i = 0; i < 25; i++) {
    const r1 = hash2(i, 111);
    const r2 = hash2(i, 222);
    const r3 = hash2(i, 333);

    const w = 20 + r1 * 40;
    const d = 10 + r2 * 30;

    const geo = new THREE.BoxGeometry(w, 1, d);
    const mesh = new THREE.Mesh(geo, cloudMat);

    mesh.position.set(
      8 + (r1 - 0.5) * 400,
      90,
      8 + (r2 - 0.5) * 400
    );

    scene.add(mesh);

    clouds.push({
      mesh: mesh,
      vx: 0.3 + r3 * 0.4,
      vz: 0.1 + r1 * 0.2
    });
  }

  createHotbar();
  spawn();

  for (let dz = -5; dz <= 5; dz++) {
    for (let dx = -5; dx <= 5; dx++) {
      ensureChunkData(dx, dz);
    }
  }

  updateChunks();
  addEventListeners();

  clock = new THREE.Clock();
  animate();
}

init();
</script>
</body>
</html>
```