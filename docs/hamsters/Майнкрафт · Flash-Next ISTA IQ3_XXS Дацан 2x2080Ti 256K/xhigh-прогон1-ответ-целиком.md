```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>mc.html</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #000;
    font-family: monospace;
  }

  canvas {
    display: block;
  }

  #overlay {
    position: fixed;
    inset: 0;
    z-index: 20;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    background: rgba(0, 0, 0, 0.72);
    user-select: none;
  }

  #overlay h1 {
    margin: 0 0 16px 0;
    font-size: 42px;
    letter-spacing: 4px;
  }

  #overlay .controls {
    max-width: 720px;
    text-align: center;
    line-height: 1.65;
    font-size: 15px;
    color: #d8d8d8;
  }

  #overlay .play {
    margin-top: 18px;
    font-size: 20px;
    color: #fff;
  }

  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 22px;
    height: 22px;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 5;
  }

  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: #fff;
  }

  #crosshair::before {
    left: 50%;
    top: 0;
    width: 2px;
    height: 22px;
    transform: translateX(-50%);
  }

  #crosshair::after {
    top: 50%;
    left: 0;
    width: 22px;
    height: 2px;
    transform: translateY(-50%);
  }

  #hotbar {
    position: fixed;
    left: 50%;
    bottom: 12px;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    padding: 8px;
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.55);
    z-index: 5;
    pointer-events: none;
  }

  .slot {
    box-sizing: border-box;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: bold;
    text-shadow: 0 1px 2px #000;
    border: 2px solid rgba(255, 255, 255, 0.35);
  }

  .slot.selected {
    border-color: #fff;
  }
</style>
</head>
<body>
<div id="overlay">
  <h1>mc.html</h1>
  <div class="controls">
    WASD move · Space jump · Mouse look<br>
    Left click break · Right click place<br>
    Keys 1-7 or mouse wheel select block
  </div>
  <div class="play">Click to play</div>
</div>

<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const CHUNK_SIZE = 16;
const WORLD_HEIGHT = 80;

const AIR = 0;
const GRASS = 1;
const DIRT = 2;
const STONE = 3;
const SAND = 4;
const WOOD = 5;
const LEAVES = 6;
const SNOW = 7;

const BLOCK_COLORS = [
  0x000000,
  0x4caf50,
  0x795548,
  0x9e9e9e,
  0xe7d9a8,
  0x8d6e63,
  0x2e7d32,
  0xffffff
];

const HOTBAR_IDS = [GRASS, DIRT, STONE, SAND, WOOD, LEAVES, SNOW];

const PLAYER_HALF_WIDTH = 0.3;
const PLAYER_HEIGHT = 1.8;
const PLAYER_EYE = 1.62;
const GRAVITY = 25;
const JUMP_VELOCITY = 8.5;
const WALK_SPEED = 5.5;
const EPS = 1e-6;

let scene, camera, renderer, raycaster, outline, water, chunkMaterial;
const clouds = [];

const chunks = new Map();
const chunkMeshes = [];

const player = { x: 8, y: 0, z: 8 };
let vy = 0;
let onGround = false;
let yaw = 0;
let pitch = 0;
let selected = 0;
let pointerLocked = false;
let lastHit = null;

const keys = {
  KeyW: false,
  KeyA: false,
  KeyS: false,
  KeyD: false
};

const FACES = [
  {
    normal: [0, 1, 0],
    factor: 1.0,
    verts: [
      [0, 1, 0],
      [0, 1, 1],
      [1, 1, 1],
      [1, 1, 0]
    ]
  },
  {
    normal: [0, -1, 0],
    factor: 0.55,
    verts: [
      [0, 0, 0],
      [1, 0, 0],
      [1, 0, 1],
      [0, 0, 1]
    ]
  },
  {
    normal: [1, 0, 0],
    factor: 0.8,
    verts: [
      [1, 0, 0],
      [1, 1, 0],
      [1, 1, 1],
      [1, 0, 1]
    ]
  },
  {
    normal: [-1, 0, 0],
    factor: 0.8,
    verts: [
      [0, 0, 0],
      [0, 0, 1],
      [0, 1, 1],
      [0, 1, 0]
    ]
  },
  {
    normal: [0, 0, 1],
    factor: 0.8,
    verts: [
      [0, 0, 1],
      [1, 0, 1],
      [1, 1, 1],
      [0, 1, 1]
    ]
  },
  {
    normal: [0, 0, -1],
    factor: 0.8,
    verts: [
      [0, 0, 0],
      [0, 1, 0],
      [1, 1, 0],
      [1, 0, 0]
    ]
  }
];

const FACE_ORDER = [0, 1, 2, 0, 2, 3];

function chunkKey(cx, cz) {
  return cx + "," + cz;
}

function blockIndex(lx, y, lz) {
  return (y * CHUNK_SIZE + lz) * CHUNK_SIZE + lx;
}

function readBlock(x, y, z) {
  if (y < 0 || y >= WORLD_HEIGHT) return AIR;

  const cx = Math.floor(x / CHUNK_SIZE);
  const cz = Math.floor(z / CHUNK_SIZE);
  const lx = x - cx * CHUNK_SIZE;
  const lz = z - cz * CHUNK_SIZE;

  const chunk = chunks.get(chunkKey(cx, cz));
  if (!chunk) return AIR;

  return chunk.data[blockIndex(lx, y, lz)];
}

function writeBlock(x, y, z, id) {
  if (y < 1 || y >= WORLD_HEIGHT) return false;

  const cx = Math.floor(x / CHUNK_SIZE);
  const cz = Math.floor(z / CHUNK_SIZE);
  const lx = x - cx * CHUNK_SIZE;
  const lz = z - cz * CHUNK_SIZE;

  const chunk = chunks.get(chunkKey(cx, cz));
  if (!chunk) return false;

  chunk.data[blockIndex(lx, y, lz)] = id;
  return true;
}

function hash3(x, y, z) {
  let n = (x * 374761393 + y * 668265263 + z * 1274126177) >>> 0;
  n ^= n >>> 13;
  n = Math.imul(n, 1274126177) >>> 0;
  n ^= n >>> 16;
  return (n >>> 0) / 4294967295;
}

function smooth(t) {
  return t * t * (3 - 2 * t);
}

function noise2(x, z) {
  const ix = Math.floor(x);
  const iz = Math.floor(z);

  const fx = x - ix;
  const fz = z - iz;

  const sx = smooth(fx);
  const sz = smooth(fz);

  const v00 = hash3(ix, 0, iz);
  const v10 = hash3(ix + 1, 0, iz);
  const v01 = hash3(ix, 0, iz + 1);
  const v11 = hash3(ix + 1, 0, iz + 1);

  const a = v00 + (v10 - v00) * sx;
  const b = v01 + (v11 - v01) * sx;
  return a + (b - a) * sz;
}

function fractal2(x, z) {
  let value = 0;
  let amplitude = 1;
  let maxAmplitude = 0;

  for (let i = 0; i < 4; i++) {
    const freq = 1 << i;
    value += noise2(x * freq, z * freq) * amplitude;
    maxAmplitude += amplitude;
    amplitude *= 0.5;
  }

  return value / maxAmplitude;
}

function noise3(x, y, z) {
  const ix = Math.floor(x);
  const iy = Math.floor(y);
  const iz = Math.floor(z);

  const fx = x - ix;
  const fy = y - iy;
  const fz = z - iz;

  const sx = smooth(fx);
  const sy = smooth(fy);
  const sz = smooth(fz);

  const v000 = hash3(ix, iy, iz);
  const v100 = hash3(ix + 1, iy, iz);
  const v010 = hash3(ix, iy + 1, iz);
  const v110 = hash3(ix + 1, iy + 1, iz);

  const v001 = hash3(ix, iy, iz + 1);
  const v101 = hash3(ix + 1, iy, iz + 1);
  const v011 = hash3(ix, iy + 1, iz + 1);
  const v111 = hash3(ix + 1, iy + 1, iz + 1);

  const x00 = v000 + (v100 - v000) * sx;
  const x10 = v010 + (v110 - v010) * sx;
  const x01 = v001 + (v101 - v001) * sx;
  const x11 = v011 + (v111 - v011) * sx;

  const y0 = x00 + (x10 - x00) * sy;
  const y1 = x01 + (x11 - x01) * sy;

  return y0 + (y1 - y0) * sz;
}

function columnHeight(wx, wz) {
  const m = fractal2(wx * 0.004, wz * 0.004);
  const h = fractal2(wx * 0.02, wz * 0.02);

  let H = Math.floor(5 + m * m * 58 + h * 10);
  if (H < 1) H = 1;
  if (H > WORLD_HEIGHT - 1) H = WORLD_HEIGHT - 1;
  return H;
}

function ensureChunkData(cx, cz) {
  const key = chunkKey(cx, cz);
  let chunk = chunks.get(key);
  if (chunk) return chunk;

  chunk = {
    cx: cx,
    cz: cz,
    data: new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * WORLD_HEIGHT),
    mesh: null,
    dirty: true
  };

  chunks.set(key, chunk);
  generateChunkData(cx, cz, chunk.data);

  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  for (const d of dirs) {
    const neighbor = chunks.get(chunkKey(cx + d[0], cz + d[1]));
    if (neighbor) neighbor.dirty = true;
  }

  return chunk;
}

function generateChunkData(cx, cz, data) {
  const baseX = cx * CHUNK_SIZE;
  const baseZ = cz * CHUNK_SIZE;

  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      const wx = baseX + lx;
      const wz = baseZ + lz;
      const H = columnHeight(wx, wz);

      let surfaceId;
      let subsurfaceId;

      if (H >= 46) surfaceId = SNOW;
      else if (H >= 37) surfaceId = STONE;
      else if (H <= 16) surfaceId = SAND;
      else surfaceId = GRASS;

      if (H <= 16) subsurfaceId = SAND;
      else if (H >= 37) subsurfaceId = STONE;
      else subsurfaceId = DIRT;

      const maxSolid = Math.min(H, WORLD_HEIGHT - 1);

      for (let y = 0; y <= maxSolid; y++) {
        let id = AIR;

        if (y === 0) {
          id = STONE;
        } else if (y < H - 3) {
          id = STONE;
        } else if (y < H) {
          id = subsurfaceId;
        } else {
          id = surfaceId;
        }

        data[blockIndex(lx, y, lz)] = id;
      }

      for (let y = 3; y <= H - 2 && y < WORLD_HEIGHT; y++) {
        const ii = blockIndex(lx, y, lz);
        if (data[ii] !== AIR) {
          if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
            data[ii] = AIR;
          }
        }
      }

      if (
        H < WORLD_HEIGHT &&
        data[blockIndex(lx, H, lz)] === GRASS &&
        hash3(wx, 17, wz) < 0.02 &&
        lx >= 2 && lx <= CHUNK_SIZE - 3 &&
        lz >= 2 && lz <= CHUNK_SIZE - 3
      ) {
        for (let ty = H + 1; ty <= H + 4; ty++) {
          if (ty >= WORLD_HEIGHT) break;
          const ii = blockIndex(lx, ty, lz);
          if (data[ii] === AIR) data[ii] = WOOD;
        }

        for (let layer = 0; layer < 2; layer++) {
          const ty = H + 3 + layer;
          if (ty >= WORLD_HEIGHT) continue;

          for (let dx = -2; dx <= 2; dx++) {
            for (let dz = -2; dz <= 2; dz++) {
              const x = lx + dx;
              const z = lz + dz;
              if (x < 0 || x >= CHUNK_SIZE || z < 0 || z >= CHUNK_SIZE) continue;

              const ii = blockIndex(x, ty, z);
              if (data[ii] === AIR) data[ii] = LEAVES;
            }
          }
        }

        let ty = H + 5;
        if (ty < WORLD_HEIGHT) {
          for (let dx = -1; dx <= 1; dx++) {
            for (let dz = -1; dz <= 1; dz++) {
              const x = lx + dx;
              const z = lz + dz;
              const ii = blockIndex(x, ty, z);
              if (data[ii] === AIR) data[ii] = LEAVES;
            }
          }
        }

        ty = H + 6;
        if (ty < WORLD_HEIGHT) {
          const ii = blockIndex(lx, ty, lz);
          if (data[ii] === AIR) data[ii] = LEAVES;
        }
      }
    }
  }
}

function addFace(positions, normals, colors, wx, wy, wz, face, r, g, b) {
  const f = face.factor;
  const cr = r * f;
  const cg = g * f;
  const cb = b * f;

  const n = face.normal;
  const verts = face.verts;

  for (let i = 0; i < 6; i++) {
    const p = verts[FACE_ORDER[i]];

    positions.push(wx + p[0], wy + p[1], wz + p[2]);
    normals.push(n[0], n[1], n[2]);
    colors.push(cr, cg, cb);
  }
}

function removeChunkMesh(cx, cz) {
  const key = chunkKey(cx, cz);
  const chunk = chunks.get(key);
  if (!chunk || !chunk.mesh) return;

  scene.remove(chunk.mesh);

  const idx = chunkMeshes.indexOf(chunk.mesh);
  if (idx >= 0) chunkMeshes.splice(idx, 1);

  chunk.mesh.geometry.dispose();
  chunk.mesh = null;
}

function buildChunkMesh(cx, cz) {
  const key = chunkKey(cx, cz);
  const chunk = chunks.get(key);
  if (!chunk) return;

  removeChunkMesh(cx, cz);

  const positions = [];
  const normals = [];
  const colors = [];

  const baseX = cx * CHUNK_SIZE;
  const baseZ = cz * CHUNK_SIZE;

  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      for (let y = 0; y < WORLD_HEIGHT; y++) {
        const id = chunk.data[blockIndex(lx, y, lz)];
        if (id === AIR) continue;

        const hex = BLOCK_COLORS[id];
        const r = ((hex >> 16) & 255) / 255;
        const g = ((hex >> 8) & 255) / 255;
        const b = (hex & 255) / 255;

        const wx = baseX + lx;
        const wz = baseZ + lz;

        for (let fi = 0; fi < FACES.length; fi++) {
          const face = FACES[fi];
          const nx = face.normal[0];
          const ny = face.normal[1];
          const nz = face.normal[2];

          if (readBlock(wx + nx, y + ny, wz + nz) !== AIR) continue;

          addFace(positions, normals, colors, wx, y, wz, face, r, g, b);
        }
      }
    }
  }

  chunk.dirty = false;

  if (positions.length === 0) {
    chunk.mesh = null;
    return;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  geometry.computeBoundingSphere();

  const mesh = new THREE.Mesh(geometry, chunkMaterial);
  scene.add(mesh);

  chunk.mesh = mesh;
  chunkMeshes.push(mesh);
}

function rebuildChunk(cx, cz) {
  buildChunkMesh(cx, cz);
}

function generateNearbyChunks() {
  const pcx = Math.floor(player.x / CHUNK_SIZE);
  const pcz = Math.floor(player.z / CHUNK_SIZE);

  const list = [];

  for (let cx = pcx - 5; cx <= pcx + 5; cx++) {
    for (let cz = pcz - 5; cz <= pcz + 5; cz++) {
      if (!chunks.has(chunkKey(cx, cz))) {
        const dx = cx - pcx;
        const dz = cz - pcz;
        const d2 = dx * dx + dz * dz;
        if (d2 <= 25) list.push({ cx: cx, cz: cz, d2: d2 });
      }
    }
  }

  list.sort((a, b) => a.d2 - b.d2);

  const count = Math.min(4, list.length);
  for (let i = 0; i < count; i++) {
    ensureChunkData(list[i].cx, list[i].cz);
  }
}

function buildNearbyMeshes() {
  const pcx = Math.floor(player.x / CHUNK_SIZE);
  const pcz = Math.floor(player.z / CHUNK_SIZE);

  const list = [];

  for (let cx = pcx - 4; cx <= pcx + 4; cx++) {
    for (let cz = pcz - 4; cz <= pcz + 4; cz++) {
      const chunk = chunks.get(chunkKey(cx, cz));
      if (!chunk) continue;
      if (chunk.mesh && !chunk.dirty) continue;

      if (
        !chunks.has(chunkKey(cx - 1, cz)) ||
        !chunks.has(chunkKey(cx + 1, cz)) ||
        !chunks.has(chunkKey(cx, cz - 1)) ||
        !chunks.has(chunkKey(cx, cz + 1))
      ) continue;

      const dx = cx - pcx;
      const dz = cz - pcz;

      list.push({
        cx: cx,
        cz: cz,
        d2: dx * dx + dz * dz,
        dirty: !!chunk.dirty
      });
    }
  }

  list.sort((a, b) => {
    if (a.dirty !== b.dirty) return a.dirty ? -1 : 1;
    return a.d2 - b.d2;
  });

  const count = Math.min(2, list.length);
  for (let i = 0; i < count; i++) {
    buildChunkMesh(list[i].cx, list[i].cz);
  }
}

function removeFarChunks() {
  const pcx = Math.floor(player.x / CHUNK_SIZE);
  const pcz = Math.floor(player.z / CHUNK_SIZE);

  const toDelete = [];

  for (const chunk of chunks.values()) {
    const dx = Math.abs(chunk.cx - pcx);
    const dz = Math.abs(chunk.cz - pcz);
    if (Math.max(dx, dz) > 7) {
      toDelete.push(chunk);
    }
  }

  for (const chunk of toDelete) {
    removeChunkMesh(chunk.cx, chunk.cz);

    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    for (const d of dirs) {
      const neighbor = chunks.get(chunkKey(chunk.cx + d[0], chunk.cz + d[1]));
      if (neighbor) neighbor.dirty = true;
    }

    chunks.delete(chunkKey(chunk.cx, chunk.cz));
  }
}

function collidesAt(x, y, z) {
  const minX = x - PLAYER_HALF_WIDTH;
  const maxX = x + PLAYER_HALF_WIDTH;
  const minY = y;
  const maxY = y + PLAYER_HEIGHT;
  const minZ = z - PLAYER_HALF_WIDTH;
  const maxZ = z + PLAYER_HALF_WIDTH;

  const x0 = Math.floor(minX);
  const x1 = Math.floor(maxX - EPS);
  const y0 = Math.floor(minY);
  const y1 = Math.floor(maxY - EPS);
  const z0 = Math.floor(minZ);
  const z1 = Math.floor(maxZ - EPS);

  for (let bx = x0; bx <= x1; bx++) {
    for (let bz = z0; bz <= z1; bz++) {
      for (let by = y0; by <= y1; by++) {
        if (readBlock(bx, by, bz) !== AIR) return true;
      }
    }
  }

  return false;
}

function moveAxisX(delta) {
  if (delta === 0) return;

  const old = player.x;
  player.x += delta;

  if (collidesAt(player.x, player.y, player.z)) {
    player.x = old;
  }
}

function moveAxisZ(delta) {
  if (delta === 0) return;

  const old = player.z;
  player.z += delta;

  if (collidesAt(player.x, player.y, player.z)) {
    player.z = old;
  }
}

function moveY(delta) {
  if (delta === 0) return;

  const oldY = player.y;
  const newY = oldY + delta;

  if (collidesAt(player.x, newY, player.z)) {
    const x0 = Math.floor(player.x - PLAYER_HALF_WIDTH);
    const x1 = Math.floor(player.x + PLAYER_HALF_WIDTH - EPS);
    const z0 = Math.floor(player.z - PLAYER_HALF_WIDTH);
    const z1 = Math.floor(player.z + PLAYER_HALF_WIDTH - EPS);
    const y0 = Math.floor(newY);
    const y1 = Math.floor(newY + PLAYER_HEIGHT - EPS);

    if (delta < 0) {
      let best = -Infinity;

      for (let bx = x0; bx <= x1; bx++) {
        for (let bz = z0; bz <= z1; bz++) {
          for (let by = y0; by <= y1; by++) {
            if (readBlock(bx, by, bz) !== AIR) {
              const candidate = by + 1;
              if (candidate <= oldY + EPS && candidate > best) best = candidate;
            }
          }
        }
      }

      if (best !== -Infinity && best > newY && best <= oldY + EPS && !collidesAt(player.x, best, player.z)) {
        player.y = best;
        vy = 0;
        onGround = true;
      } else {
        player.y = oldY;
        vy = 0;
        onGround = false;
      }
    } else {
      let best = Infinity;

      for (let bx = x0; bx <= x1; bx++) {
        for (let bz = z0; bz <= z1; bz++) {
          for (let by = y0; by <= y1; by++) {
            if (readBlock(bx, by, bz) !== AIR) {
              const candidate = by - PLAYER_HEIGHT;
              if (candidate >= oldY - EPS && candidate < best) best = candidate;
            }
          }
        }
      }

      if (best !== Infinity && best < newY && best >= oldY - EPS && !collidesAt(player.x, best, player.z)) {
        player.y = best;
        vy = 0;
      } else {
        player.y = oldY;
        vy = 0;
      }

      onGround = false;
    }
  } else {
    player.y = newY;
    onGround = collidesAt(player.x, player.y - 0.01, player.z);
  }
}

function updatePlayer(dt) {
  let mx = 0;
  let mz = 0;

  const forwardX = -Math.sin(yaw);
  const forwardZ = -Math.cos(yaw);
  const rightX = Math.cos(yaw);
  const rightZ = -Math.sin(yaw);

  if (keys.KeyW) {
    mx += forwardX;
    mz += forwardZ;
  }
  if (keys.KeyS) {
    mx -= forwardX;
    mz -= forwardZ;
  }
  if (keys.KeyD) {
    mx += rightX;
    mz += rightZ;
  }
  if (keys.KeyA) {
    mx -= rightX;
    mz -= rightZ;
  }

  if (mx !== 0 || mz !== 0) {
    const len = Math.hypot(mx, mz);
    if (len > 0) {
      mx = (mx / len) * WALK_SPEED;
      mz = (mz / len) * WALK_SPEED;
    }
  }

  moveAxisX(mx * dt);
  moveAxisZ(mz * dt);

  vy -= GRAVITY * dt;
  if (vy < -30) vy = -30;

  moveY(vy * dt);

  if (player.y < -20) {
    respawnPlayer();
  }
}

function updateCamera() {
  camera.position.set(player.x, player.y + PLAYER_EYE, player.z);
  camera.rotation.x = pitch;
  camera.rotation.y = yaw;
  camera.rotation.z = 0;
  camera.updateMatrixWorld();
}

function findSpawnY() {
  ensureChunkData(0, 0);

  let top = -1;
  for (let y = WORLD_HEIGHT - 1; y >= 0; y--) {
    if (readBlock(8, y, 8) !== AIR) {
      top = y;
      break;
    }
  }

  let y = top + 1;
  if (y < 1) y = 1;

  while (y < WORLD_HEIGHT && collidesAt(8, y, 8)) {
    y++;
  }

  return Math.min(y, WORLD_HEIGHT - 1);
}

function respawnPlayer() {
  player.x = 8;
  player.z = 8;
  player.y = findSpawnY();
  vy = 0;
  onGround = false;
}

function overlapsPlayer(bx, by, bz) {
  return (
    player.x + PLAYER_HALF_WIDTH > bx &&
    player.x - PLAYER_HALF_WIDTH < bx + 1 &&
    player.y + PLAYER_HEIGHT > by &&
    player.y < by + 1 &&
    player.z + PLAYER_HALF_WIDTH > bz &&
    player.z - PLAYER_HALF_WIDTH < bz + 1
  );
}

function editBlock(x, y, z, id) {
  if (!writeBlock(x, y, z, id)) return false;

  const cx = Math.floor(x / CHUNK_SIZE);
  const cz = Math.floor(z / CHUNK_SIZE);
  const lx = x - cx * CHUNK_SIZE;
  const lz = z - cz * CHUNK_SIZE;

  rebuildChunk(cx, cz);

  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);

  return true;
}

function updateRaycast() {
  if (!pointerLocked) {
    outline.visible = false;
    lastHit = null;
    return;
  }

  camera.updateMatrixWorld();

  raycaster.ray.origin.copy(camera.position);
  raycaster.ray.direction.set(0, 0, -1).applyQuaternion(camera.quaternion);

  const hits = raycaster.intersectObjects(chunkMeshes, false);

  let hit = null;
  for (const h of hits) {
    if (h.distance <= 6) {
      hit = h;
      break;
    }
  }

  if (hit && hit.face) {
    lastHit = hit;

    const n = hit.face.normal.clone().normalize();
    const p = hit.point;

    const bx = Math.floor(p.x - n.x * 0.5);
    const by = Math.floor(p.y - n.y * 0.5);
    const bz = Math.floor(p.z - n.z * 0.5);

    if (by >= 0) {
      outline.visible = true;
      outline.position.set(bx + 0.5, by + 0.5, bz + 0.5);
    } else {
      outline.visible = false;
      lastHit = null;
    }
  } else {
    outline.visible = false;
    lastHit = null;
  }
}

function createClouds() {
  const cloudMaterial = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.75,
    fog: false
  });

  for (let i = 0; i < 25; i++) {
    const a = hash3(i * 17 + 3, 1000, i * 31 + 7);
    const b = hash3(i * 23 + 5, 2000, i * 13 + 11);
    const c = hash3(i * 29 + 1, 3000, i * 37 + 13);
    const d = hash3(i * 41 + 2, 4000, i * 53 + 19);

    const width = 25 + a * 35;
    const height = 2 + c * 4;
    const depth = 25 + b * 35;

    const geometry = new THREE.BoxGeometry(width, height, depth);
    const cloud = new THREE.Mesh(geometry, cloudMaterial);

    cloud.position.set(
      player.x + (a - 0.5) * 360,
      90 + c * 8,
      player.z + (b - 0.5) * 360
    );

    cloud.userData.speedX = 0.4 + d * 1.2;
    cloud.userData.speedZ = 0.1 + a * 0.6;

    scene.add(cloud);
    clouds.push(cloud);
  }
}

function updateClouds(dt) {
  const wrap = 360;

  for (const cloud of clouds) {
    cloud.position.x += cloud.userData.speedX * dt;
    cloud.position.z += cloud.userData.speedZ * dt;

    let dx = cloud.position.x - player.x;
    if (dx < -wrap / 2) cloud.position.x += wrap;
    else if (dx > wrap / 2) cloud.position.x -= wrap;

    let dz = cloud.position.z - player.z;
    if (dz < -wrap / 2) cloud.position.z += wrap;
    else if (dz > wrap / 2) cloud.position.z -= wrap;
  }
}

function createWater() {
  const geometry = new THREE.PlaneGeometry(1000, 1000);
  const material = new THREE.MeshBasicMaterial({
    color: 0x4488ff,
    transparent: true,
    opacity: 0.65,
    side: THREE.DoubleSide
  });

  water = new THREE.Mesh(geometry, material);
  water.rotation.x = -Math.PI / 2;
  water.position.set(player.x, 14.3, player.z);
  scene.add(water);
}

function buildHotbar() {
  const bar = document.getElementById("hotbar");

  for (let i = 0; i < HOTBAR_IDS.length; i++) {
    const slot = document.createElement("div");
    slot.className = "slot";

    const hex = BLOCK_COLORS[HOTBAR_IDS[i]];
    slot.style.backgroundColor = "#" + hex.toString(16).padStart(6, "0");
    slot.textContent = String(i + 1);

    bar.appendChild(slot);
  }

  updateHotbar();
}

function updateHotbar() {
  const slots = document.querySelectorAll("#hotbar .slot");
  for (let i = 0; i < slots.length; i++) {
    slots[i].classList.toggle("selected", i === selected);
  }
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function onPointerLockChange() {
  pointerLocked = document.pointerLockElement === renderer.domElement;

  const overlay = document.getElementById("overlay");
  overlay.style.display = pointerLocked ? "none" : "flex";

  if (!pointerLocked) {
    keys.KeyW = false;
    keys.KeyA = false;
    keys.KeyS = false;
    keys.KeyD = false;
  }
}

function onMouseMove(e) {
  if (!pointerLocked) return;

  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;

  const limit = Math.PI / 2 - 0.01;
  if (pitch > limit) pitch = limit;
  if (pitch < -limit) pitch = -limit;
}

function onMouseDown(e) {
  if (!pointerLocked || !lastHit) return;

  const n = lastHit.face.normal.clone().normalize();
  const p = lastHit.point;

  if (e.button === 0) {
    const bx = Math.floor(p.x - n.x * 0.5);
    const by = Math.floor(p.y - n.y * 0.5);
    const bz = Math.floor(p.z - n.z * 0.5);

    if (by <= 0) return;

    editBlock(bx, by, bz, AIR);
  } else if (e.button === 2) {
    const bx = Math.floor(p.x + n.x * 0.5);
    const by = Math.floor(p.y + n.y * 0.5);
    const bz = Math.floor(p.z + n.z * 0.5);

    if (by < 1 || by >= WORLD_HEIGHT) return;
    if (readBlock(bx, by, bz) !== AIR) return;
    if (overlapsPlayer(bx, by, bz)) return;

    editBlock(bx, by, bz, HOTBAR_IDS[selected]);
  }
}

function onKeyDown(e) {
  if (e.code === "Space") {
    if (pointerLocked && onGround) {
      vy = JUMP_VELOCITY;
      onGround = false;
    }
    e.preventDefault();
    return;
  }

  if (e.code in keys) {
    keys[e.code] = true;
  } else if (e.key >= "1" && e.key <= "7") {
    selected = parseInt(e.key, 10) - 1;
    updateHotbar();
  }
}

function onKeyUp(e) {
  if (e.code in keys) {
    keys[e.code] = false;
  }
}

function onWheel(e) {
  if (!pointerLocked) return;

  e.preventDefault();

  if (e.deltaY > 0) selected = (selected + 1) % HOTBAR_IDS.length;
  else selected = (selected - 1 + HOTBAR_IDS.length) % HOTBAR_IDS.length;

  updateHotbar();
}

function updateWorld(dt) {
  generateNearbyChunks();
  buildNearbyMeshes();
  removeFarChunks();

  updateClouds(dt);

  water.position.set(player.x, 14.3, player.z);

  updateRaycast();
}

let lastTime = performance.now();

function animate() {
  const now = performance.now();
  let dt = (now - lastTime) / 1000;
  lastTime = now;

  if (dt > 0.05) dt = 0.05;

  if (pointerLocked) {
    updatePlayer(dt);
  }

  updateCamera();
  updateWorld(dt);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

function init() {
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

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(100, 200, 100);
  scene.add(dirLight);

  chunkMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

  raycaster = new THREE.Raycaster();
  raycaster.far = 6;

  const outlineGeometry = new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002));
  const outlineMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
  outline = new THREE.LineSegments(outlineGeometry, outlineMaterial);
  outline.visible = false;
  scene.add(outline);

  createClouds();
  createWater();

  player.y = findSpawnY();

  buildHotbar();

  window.addEventListener("resize", onResize);
  document.addEventListener("pointerlockchange", onPointerLockChange);
  document.addEventListener("mousemove", onMouseMove);
  document.addEventListener("mousedown", onMouseDown);
  document.addEventListener("contextmenu", e => e.preventDefault());
  document.addEventListener("keydown", onKeyDown);
  document.addEventListener("keyup", onKeyUp);
  document.addEventListener("wheel", onWheel, { passive: false });

  document.getElementById("overlay").addEventListener("click", () => {
    try {
      const req = renderer.domElement.requestPointerLock();
      if (req && req.catch) req.catch(() => {});
    } catch (_) {
      // Ignore pointer lock request failures.
    }
  });

  requestAnimationFrame(animate);
}

init();
</script>
</body>
</html>
```