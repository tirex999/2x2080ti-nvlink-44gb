Let me build this Minecraft-style voxel game in a single HTML file. I need to carefully implement all the requirements. Let me go through the spec methodically.

Let me plan out the structure:

1. HTML/CSS structure with start overlay, crosshair, hotbar
2. Three.js setup (scene, camera, renderer, lights, sky, fog, clouds, water)
3. Chunk system with global Map
4. Block read/write helpers
5. Terrain generation (value noise, fractal noise, 3D noise)
6. Meshing (BufferGeometry per chunk)
7. Player controls (pointer lock, movement, collision)
8. Break/place with raycasting
9. Hotbar
10. Main loop

Let me write this carefully.

### Noise functions

I need:
- Integer-coordinate hash giving 0-1 (mix with large prime multipliers and xor-shifts)
- Smoothed 2D noise via bilinear interpolation with smoothstep
- 4 octaves combined into fractal noise
- A 3D version for caves

Let me implement value noise.

```javascript
function hash2(ix, iy) {
  // integer hash -> 0..1
  let h = ix * 1664525 + iy * 2745505;
  // xor shift
  h = (h ^ (h >>> 13)) * 1274126177 | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}

function hash3(ix, iy, iz) {
  let h = (ix * 374761393 + iy * 668265263 + iz * 2147483649) | 0;
  h = (h ^ (h >>> 13)) * 1274126177 | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```

Then smoothed 2D noise via bilinear interpolation with smoothstep:

```javascript
function smoothstep(t) {
  return t * t * (3 - 2 * t);
}

function noise2(x, y) {
  const ix = Math.floor(x), iy = Math.floor(y);
  const fx = smoothstep(x - ix), fy = smoothstep(y - iy);
  const v00 = hash2(ix, iy);
  const v10 = hash2(ix + 1, iy);
  const v01 = hash2(ix, iy + 1);
  const v11 = hash2(ix + 1, iy + 1);
  const u = v00 * (1 - fx) + v10 * fx;
  const v = v01 * (1 - fx) + v11 * fx;
  return u * (1 - fy) + v * fy;
}
```

Fractal noise with 4 octaves:

```javascript
function fractal2(x, y, octaves) {
  let amp = 1, freq = 1, sum = 0, norm = 0;
  for (let i = 0; i < octaves; i++) {
    sum += amp * noise2(x * freq, y * freq);
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / norm;
}
```

3D version for caves:

```javascript
function noise3(x, y, z) {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
  const fx = smoothstep(x - ix), fy = smoothstep(y - iy), fz = smoothstep(z - iz);
  // 8 corners
  const d = (dx, dy, dz) => hash3(ix+dx, iy+dy, iz+dz);
  const c000 = d(0,0,0), c100 = d(1,0,0), c010 = d(0,1,0), c110 = d(1,1,0);
  const c001 = d(0,0,1), c101 = d(1,0,1), c011 = d(0,1,1), c111 = d(1,1,1);
  // trilinear
  ...
}
```

### Terrain generation

Column height: 
- m = fractal at coords*0.004
- h = fractal at coords*0.02
- H = floor(5 + m*m*58 + h*10)

Column fill:
- y 0 = unbreakable stone
- below H−3 stone
- the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37)
- surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass

Let me think about the column fill logic carefully. For a given column with height H:
- y = 0: stone (unbreakable)
- y from 1 to H-4 (below H-3): stone
- The 3 layers under the surface: y = H-3, H-2, H-1
  - dirt (sand if H ≤ 16, stone if H ≥ 37)
- surface y = H: 
  - snow if H ≥ 46
  - stone if H ≥ 37
  - sand if H ≤ 16
  - otherwise grass

Wait, let me re-read: "the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37)". So the 3 sub-surface layers are dirt normally, but sand if H ≤ 16, stone if H ≥ 37.

So:
- y = 0: stone
- y in [1, H-1]: 
  - if y <= H-4: stone (below H-3)
  - else (y in H-3, H-2, H-1): dirt/sand/stone based on H
- y = H: surface material

Let me write it:

```javascript
for (let y = 0; y < H; y++) {
  if (y === 0) {
    setBlock(x, y, z, STONE);
  } else if (y < H - 3) {
    setBlock(x, y, z, STONE);
  } else if (y < H) {
    // 3 layers under surface
    if (H <= 16) setBlock(x, y, z, SAND);
    else if (H >= 37) setBlock(x, y, z, STONE);
    else setBlock(x, y, z, DIRT);
  }
  // surface
  if (H >= 46) setBlock(x, H, z, SNOW);
  else if (H >= 37) setBlock(x, H, z, STONE);
  else if (H <= 16) setBlock(x, H, z, SAND);
  else setBlock(x, H, z, GRASS);
}
```

Caves: for y between 3 and H−2, if 3D noise at position*0.09 exceeds 0.67, set air.

```javascript
for (let y = 3; y <= H - 2; y++) {
  if (noise3(x*0.09, y*0.09, z*0.09) > 0.67) {
    setBlock(x, y, z, AIR);
  }
}
```

Trees: on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air).

```javascript
// after filling column
if (surface is grass) {
  if (treeHash < 0.02) {
    // place tree
    let top = H;
    for (let i = 1; i <= 4; i++) setBlock(x, top+i, z, WOOD);
    // leaves
    let ly = top + 5;
    // 5x5 layer twice
    for (let dx=-2; dx<=2; dx++) for (let dz=-2; dz<=2; dz++) {
      setBlock(x+dx, ly, z+dz, LEAVES);
      setBlock(x+dx, ly+1, z+dz, LEAVES);
    }
    // 3x3
    ly += 2;
    for (let dx=-1; dx<=1; dx++) for (let dz=-1; dz<=1; dz++) {
      setBlock(x+dx, ly, z+dz, LEAVES);
    }
    // 1 on top
    ly += 1;
    setBlock(x, ly, z, LEAVES);
  }
}
```

Wait, "the trunk fits inside the chunk" - need to check the tree doesn't extend beyond chunk boundaries. Actually let me handle this: the tree occupies x, z coordinates. If x or z is near the edge, leaves might extend beyond. But since we're generating per-chunk and reading neighbors for meshing, it's fine if leaves extend beyond as long as we store them... but actually they'd be lost if they go to another chunk. Hmm. Let me just check that the trunk base is within the chunk and maybe require some margin. Actually the spec says "the trunk fits inside the chunk" - so just check x,z within [0,15]. But leaves extend 2 blocks out. Let me re-read.

"Trees: on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

I'll interpret "trunk fits inside the chunk" as x and z being within the chunk (0-15). The leaves extending beyond would be a minor issue but since we mesh per chunk with neighbor reads, and the leaves are stored in THIS chunk's array even if positioned at the edge... wait no, if x+dx goes out of [0,15], we can't store it in this chunk. 

Hmm, this is tricky. Let me think. The leaves layer is 5x5 centered on the trunk. If the trunk is at x=0, then leaves span x=-2 to x=2, which goes negative. We can't store x=-2 in this chunk.

But actually, this is a common simplification. Many voxel games just allow trees near edges and the leaves get clipped or stored across chunks. Given the spec says "the trunk fits inside the chunk", I think the intent is just to check the trunk position. To be safe, maybe I should check that the tree leaves won't go out of bounds, OR just place them and clamp. 

Actually, let me just check that x and z are in [0,15] for the trunk, and when placing leaves, skip positions that are out of the current chunk's range. That way we don't lose data to another chunk unnecessarily, but we also don't crash. Actually, that would make trees look weird at edges. 

Alternatively, I could require the tree to be at least 2 blocks from each edge. But the spec explicitly says "the trunk fits inside the chunk". Let me just do the simple thing: check 0 <= x < 16 and 0 <= z < 16, and place leaves clamped/skipped if out of range. Actually, to keep it clean and avoid bugs, I'll place leaves only if within chunk bounds (skip otherwise). This is the safest.

Hmm, but actually there's a subtlety. If I skip leaves that go out of bounds, and the neighboring chunk generates its own tree, there might be gaps. But that's acceptable for this kind of game. Let me just check bounds when placing.

Actually, let me reconsider. The simplest robust approach: place the tree, and for leaves, check bounds before setting. Let me do that.

Let me define per-column hash for trees:

```javascript
function treeHash(x, z) {
  return hash2(x * 31 + z * 17, x * 7 + z * 41); // some deterministic hash
}
```

Actually I can reuse hash2. Let me make a function that returns a value in [0,1).

### Chunk data storage

```javascript
const CHUNK_SIZE = 16;
const CHUNK_HEIGHT = 80;
const chunks = new Map(); // key "cx,cz" -> { data: Uint8Array, mesh: Mesh }
```

Data is Uint8Array of size 16*16*80 = 20480.

Index: `(y * CHUNK_SIZE + z) * CHUNK_SIZE + x` or `(x + z*16 + y*16*16)`. Let me use `x + z*CS + y*CS*CS`.

### Global read/write block helpers

```javascript
function chunkKey(cx, cz) { return cx + ',' + cz; }

function getChunk(cx, cz) {
  return chunks.get(chunkKey(cx, cz));
}

function readBlock(wx, wy, wz) {
  if (wy < 0 || wy >= CHUNK_HEIGHT) return AIR;
  const cx = Math.floor(wx / 16);
  const cz = Math.floor(wz / 16);
  const x = wx - cx * 16;
  const z = wz - cz * 16;
  const c = getChunk(cx, cz);
  if (!c || !c.data) return AIR;
  return c.data[x + z * 16 + wy * 256];
}

function setBlock(wx, wy, wz, id) {
  if (wy < 0 || wy >= CHUNK_HEIGHT) return;
  const cx = Math.floor(wx / 16);
  const cz = Math.floor(wz / 16);
  const x = wx - cx * 16;
  const z = wz - cz * 16;
  const c = getChunk(cx, cz);
  if (!c || !c.data) return;
  c.data[x + z * 16 + wy * 256] = id;
}
```

### Meshing

For each chunk, build a BufferGeometry. Loop all non-air blocks, check 6 neighbors, add faces where neighbor is air.

Fake lighting: multiply block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms.

```javascript
function buildChunkMesh(cx, cz) {
  const c = getChunk(cx, cz);
  if (!c) return;
  const data = c.data;
  
  const positions = [];
  const normals = [];
  const colors = [];
  
  const baseX = cx * 16;
  const baseZ = cz * 16;
  
  const FACES = [
    { dir: [1, 0, 0], normal: [1, 0, 0], light: 0.8, corners: [...] },
    ...
  ];
  ...
}
```

Let me define the 6 faces with their corner vertices. Each face has 4 corners (in CCW order for outward normal) and 2 triangles.

For a cube at (x,y,z) with unit size, the face in +x direction (right) has normal [1,0,0]. Its corners are at x+1. Let me define each face with 4 corner offsets.

Standard approach: for each face, define 4 corners. Let me use this layout:

- +X (right): normal (1,0,0), corners: (1,0,0),(1,1,0),(1,1,1),(1,0,1)
- -X (left): normal (-1,0,0), corners: (0,0,1),(0,1,1),(0,1,0),(0,0,0)
- +Y (top): normal (0,1,0), corners: (0,1,1),(1,1,1),(1,1,0),(0,1,0)
- -Y (bottom): normal (0,-1,0), corners: (0,0,0),(1,0,0),(1,0,1),(0,0,1)
- +Z (front): normal (0,0,1), corners: (1,0,1),(1,1,1),(0,1,1),(0,0,1)
- -Z (back): normal (0,0,-1), corners: (0,0,0),(0,1,0),(1,1,0),(1,0,0)

Each face: 2 triangles. Triangle 1: corners 0,1,2. Triangle 2: corners 0,2,3.

Colors: for each corner, use the same color (block color * light factor). Since it's flat shading, all 4 corners of a face get the same color.

Let me precompute block colors:

```javascript
const BLOCK_COLORS = {
  1: [0x4caf50], // grass
  2: [0x795548], // dirt
  3: [0x9e9e9e], // stone
  4: [0xe7d9a8], // sand
  5: [0x8d6e63], // wood
  6: [0x2e7d32], // leaves
  7: [0xffffff], // snow
};
```

Convert hex to RGB floats:

```javascript
function hexToRgb(hex) {
  return [
    ((hex >> 16) & 255) / 255,
    ((hex >> 8) & 255) / 255,
    (hex & 255) / 255,
  ];
}
```

### Rebuild function

```javascript
function rebuildChunk(cx, cz) {
  const c = getChunk(cx, cz);
  if (!c) return;
  // dispose old mesh
  if (c.mesh) {
    scene.remove(c.mesh);
    c.mesh.geometry.dispose();
  }
  c.mesh = buildChunkMesh(cx, cz);
  if (c.mesh) scene.add(c.mesh);
}
```

### Main loop chunk management

Each frame:
- Generate block data for all chunks within 5 chunks of the player (max 4 per frame)
- Build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame)
- For chunks farther than 7, remove mesh, dispose geometry, delete entry

```javascript
const playerChunkX = Math.floor(player.pos.x / 16);
const playerChunkZ = Math.floor(player.pos.z / 16);

// Generate
let genBudget = 4;
for (let dx = -5; dx <= 5 && genBudget > 0; dx++) {
  for (let dz = -5; dz <= 5 && genBudget > 0; dz++) {
    const cx = playerChunkX + dx;
    const cz = playerChunkZ + dz;
    const key = chunkKey(cx, cz);
    if (!chunks.has(key)) {
      generateChunk(cx, cz);
      genBudget--;
    }
  }
}

// Build meshes
let meshBudget = 2;
for (let dx = -4; dx <= 4 && meshBudget > 0; dx++) {
  for (let dz = -4; dz <= 4 && meshBudget > 0; dz++) {
    const cx = playerChunkX + dx;
    const cz = playerChunkZ + dz;
    const key = chunkKey(cx, cz);
    const c = chunks.get(key);
    if (c && !c.mesh) {
      // check 4 neighbors have data
      const n = getChunk(cx+1, cz) && getChunk(cx-1, cz) && getChunk(cx, cz+1) && getChunk(cx, cz-1);
      if (n) {
        rebuildChunk(cx, cz);
        meshBudget--;
      }
    }
  }
}

// Cleanup
for (const [key, c] of chunks) {
  const [cx, cz] = key.split(',').map(Number);
  const dx = Math.abs(cx - playerChunkX);
  const dz = Math.abs(cz - playerChunkZ);
  if (dx > 7 || dz > 7) {
    if (c.mesh) {
      scene.remove(c.mesh);
      c.mesh.geometry.dispose();
    }
    chunks.delete(key);
  }
}
```

Wait, there's an issue with iterating and deleting in the cleanup. Let me collect keys first then delete.

### Player physics

```javascript
const player = {
  pos: new THREE.Vector3(8, ... , 8),
  vel: new THREE.Vector3(),
  onGround: false,
  yaw: 0,
  pitch: 0,
};
```

Spawn above terrain at x=8, z=8. I need to find the terrain height at (8,8).

```javascript
function surfaceHeightAt(wx, wz) {
  for (let y = CHUNK_HEIGHT - 1; y >= 0; y--) {
    if (readBlock(wx, y, wz) !== AIR) return y + 1;
  }
  return 40;
}
```

Player box: half-width 0.3, height 1.8, eye 1.62. So the box spans from pos.x-0.3 to pos.x+0.3, etc. The eye is at height 1.62 from the feet. Actually, player.pos represents... let me define pos as the feet position (bottom center). Eye is at pos.y + 1.62.

Collision: axis-separated. For each axis, move, then check overlap with any non-air block intersecting the box. If overlap, revert.

```javascript
function collides(px, py, pz) {
  // player box
  const minX = px - 0.3, maxX = px + 0.3;
  const minY = py, maxY = py + 1.8;
  const minZ = pz - 0.3, maxZ = pz + 0.3;
  // check all blocks in range
  const bx0 = Math.floor(minX), bx1 = Math.floor(maxX);
  const by0 = Math.floor(minY), by1 = Math.floor(maxY);
  const bz0 = Math.floor(minZ), bz1 = Math.floor(maxZ);
  for (let x = bx0; x <= bx1; x++)
    for (let y = by0; y <= by1; y++)
      for (let z = bz0; z <= bz1; z++) {
        if (readBlock(x, y, z) !== AIR) return true;
      }
  return false;
}
```

Movement per axis:
```javascript
// X
let np = player.pos.clone();
np.x += vx * dt;
if (!collides(np.x, player.pos.y, player.pos.z)) {
  player.pos.x = np.x;
} else {
  player.vel.x = 0;
}
// similar for Y, Z
```

For Y, if moving down and collides, set onGround = true.

Jump: if onGround and space pressed, vel.y = 8.5.

Gravity: vel.y -= 25 * dt.

Falling below y -20: teleport to spawn.

### Controls

Pointer lock. On clicking start overlay, request pointer lock. Mouse look only while locked.

```javascript
document.addEventListener('mousemove', (e) => {
  if (document.pointerLockElement === canvas) {
    player.yaw -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    player.pitch = Math.max(-Math.PI/2 + 0.01, Math.min(Math.PI/2 - 0.01, player.pitch));
  }
});
```

Rotation order "YXZ": `camera.rotation.order = 'YXZ'; camera.rotation.set(pitch, yaw, 0);`

Movement keys WASD.

### Break & place

Raycast from camera center (max distance 6) against chunk meshes. Use THREE.Raycaster.

```javascript
const raycaster = new THREE.Raycaster();
raycaster.far = 6;

function getTarget() {
  raycaster.set(camera.position, camera.getWorldDirection(new THREE.Vector3()));
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length > 0) {
    const hit = hits[0];
    const p = hit.point;
    const n = hit.face.normal;
    const target = {
      x: Math.floor(p.x - n.x * 0.5),
      y: Math.floor(p.y - n.y * 0.5),
      z: Math.floor(p.z - n.z * 0.5),
    };
    const place = {
      x: Math.floor(p.x + n.x * 0.5),
      y: Math.floor(p.y + n.y * 0.5),
      z: Math.floor(p.z + n.z * 0.5),
    };
    return { target, place };
  }
  return null;
}
```

Wait, but the chunk meshes use flat normals from vertex colors, not face normals from geometry. When using MeshLambertMaterial with vertex colors and BufferGeometry, the face normal is computed from the geometry. Actually, the raycaster uses `hit.face.normal` which requires the geometry to have face normals (non-indexed or indexed with proper normals). With BufferGeometry that's non-indexed, `hit.face` exists. But our normals are flat (per-face constant), so `hit.face.normal` should be correct (one of the 6 axis directions).

Actually, there's a subtlety. When we build the geometry with separate vertices per face (not sharing), the geometry is non-indexed, and Raycaster.intersectObjects will compute face normals from the triangle vertices. These should match our explicit normals. Good.

But wait—there's a concern. The chunk meshes are merged into one big geometry. The individual faces still have their own normals stored in the normals attribute. Raycaster computes face normal from geometry (from the triangle's 3 vertices), which gives the geometric normal. This should be an axis-aligned normal. Good.

Let me make sure the outline box works. I'll create a LineSegments wireframe box that I reposition each frame.

```javascript
const outlineGeo = new THREE.BoxGeometry(1.001, 1.001, 1.001);
const outlineMat = new THREE.LineBasicMaterial({ color: 0x000000 });
const outline = new THREE.LineSegments(outlineGeo, outlineMat);
outline.visible = false;
scene.add(outline);
```

Position it at the target block center.

### Break/place on click

```javascript
canvas.addEventListener('mousedown', (e) => {
  if (document.pointerLockElement !== canvas) return;
  const t = getTarget();
  if (!t) return;
  if (e.button === 0) {
    // break
    if (t.target.y !== 0) {
      setBlock(t.target.x, t.target.y, t.target.z, AIR);
      rebuildChunkAndNeighbors(t.target.x, t.target.y, t.target.z);
    }
  } else if (e.button === 2) {
    // place
    const id = selectedBlock;
    if (readBlock(t.place.x, t.place.y, t.place.z) === AIR) {
      // check not overlapping player
      if (!playerOverlaps(t.place.x, t.place.y, t.place.z)) {
        setBlock(t.place.x, t.place.y, t.place.z, id);
        rebuildChunkAndNeighbors(t.place.x, t.place.y, t.place.z);
      }
    }
  }
});
```

rebuildChunkAndNeighbors:
```javascript
function rebuildChunkAndNeighbors(x, y, z) {
  const cx = Math.floor(x / 16), cz = Math.floor(z / 16);
  rebuildChunk(cx, cz);
  if (x % 16 === 0) rebuildChunk(cx - 1, cz);
  if (x % 16 === 15) rebuildChunk(cx + 1, cz);
  if (z % 16 === 0) rebuildChunk(cx, cz - 1);
  if (z % 16 === 15) rebuildChunk(cx, cz + 1);
}
```

playerOverlaps:
```javascript
function playerOverlaps(bx, by, bz) {
  const px = player.pos.x, py = player.pos.y, pz = player.pos.z;
  return (bx + 1 > px - 0.3 && bx < px + 0.3 &&
          by + 1 > py && by < py + 1.8 &&
          bz + 1 > pz - 0.3 && bz < pz + 0.3);
}
```

Context menu suppression:
```javascript
canvas.addEventListener('contextmenu', (e) => e.preventDefault());
```

### Hotbar

7 slots. Keys 1-7 or mouse wheel.

```javascript
const hotbarBlocks = [1, 2, 3, 4, 5, 6, 7];
let selectedSlot = 0;
```

Mouse wheel:
```javascript
window.addEventListener('wheel', (e) => {
  if (document.pointerLockElement !== canvas) return;
  selectedSlot = (selectedSlot + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
  updateHotbarUI();
});
```

Keys:
```javascript
window.addEventListener('keydown', (e) => {
  if (e.key >= '1' && e.key <= '7') {
    selectedSlot = parseInt(e.key) - 1;
    updateHotbarUI();
  }
});
```

### Sky, clouds, water

Sky blue background 0x87ceeb, fog matching.

```javascript
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);
```

Ambient 0.65 + directional 0.8.

Clouds: ~25 flat white transparent boxes at height ~90, drifting and wrapping around player.

```javascript
const clouds = [];
for (let i = 0; i < 25; i++) {
  const geo = new THREE.BoxGeometry(8 + Math.random()*12, 2, 6 + Math.random()*8);
  ...
}
```

No Math.random allowed! Wait, the spec says "deterministic, no Math.random" for terrain. For clouds it says "Around 25 flat white transparent boxes". It doesn't explicitly forbid Math.random for clouds, but to be safe and consistent, let me use deterministic values. Actually the "no Math.random" rule is specifically about terrain determinism. But let me just use a deterministic hash for cloud sizes too to be safe. Actually, I'll use simple deterministic offsets.

Let me make clouds deterministic:
```javascript
for (let i = 0; i < 25; i++) {
  const w = 6 + ((i * 7) % 12);
  const d = 5 + ((i * 5) % 8);
  const geo = new THREE.BoxGeometry(w, 2, d);
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
  const cloud = new THREE.Mesh(geo, mat);
  cloud.position.set((i * 37) % 200 - 100, 90, (i * 53) % 200 - 100);
  cloud.userData.baseX = cloud.position.x;
  cloud.userData.baseZ = cloud.position.z;
  scene.add(cloud);
  clouds.push(cloud);
}
```

Drift and wrap:
```javascript
clouds.forEach(c => {
  c.position.x += driftSpeed * dt;
  if (c.position.x - player.pos.x > 120) c.position.x -= 240;
  if (c.position.x - player.pos.x < -120) c.position.x += 240;
});
```

Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame.

```javascript
const waterGeo = new THREE.PlaneGeometry(500, 500);
const waterMat = new THREE.MeshLambertMaterial({ color: 0x2b7fff, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
const water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI / 2;
water.position.y = 14.3;
scene.add(water);
```

Re-center each frame: water.position.x = player.pos.x; water.position.z = player.pos.z;

### Camera updates

```javascript
camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
camera.rotation.set(player.pitch, player.yaw, 0);
```

### Start overlay

```html
<div id="overlay">
  <div class="overlay-content">
    <h1>MC</h1>
    <ul>
      <li>WASD - Move</li>
      <li>Space - Jump</li>
      <li>Mouse - Look</li>
      <li>Left Click - Break</li>
      <li>Right Click - Place</li>
      <li>1-7 / Wheel - Select block</li>
    </ul>
    <p class="play">Click to play</p>
  </div>
</div>
```

On clicking overlay, request pointer lock on canvas. When pointer lock is released, show overlay again.

```javascript
overlay.addEventListener('click', () => {
  canvas.requestPointerLock();
});

document.addEventListener('pointerlockchange', () => {
  if (document.pointerLockElement !== canvas) {
    overlay.style.display = 'flex';
  } else {
    overlay.style.display = 'none';
  }
});
```

Wait, but clicking the overlay to start—when we requestPointerLock, the pointerlockchange fires and hides the overlay. But the click also might... let me handle carefully. The overlay click handler requests pointer lock. Then pointerlockchange hides overlay. Good.

But there's a subtlety: the overlay click handler needs the pointer to actually lock. In some browsers, requestPointerLock must be triggered by a user gesture, which the click provides. Good.

### Rendering setup

```javascript
const renderer = new THREE.WebGLRenderer({ canvas: canvas });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
```

### Resize

```javascript
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

### Main loop

```javascript
let lastTime = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  
  updatePlayer(dt);
  updateChunks();
  updateClouds(dt);
  water.position.x = player.pos.x;
  water.position.z = player.pos.z;
  
  updateTargetOutline();
  
  renderer.render(scene, camera);
}
```

Now let me think about the movement input. I'll track keys in a Set.

```javascript
const keys = {};
window.addEventListener('keydown', (e) => { keys[e.code] = true; });
window.addEventListener('keyup', (e) => { keys[e.code] = false; });
```

Movement relative to yaw:
```javascript
const speed = 5.5;
let dx = 0, dz = 0;
if (keys['KeyW']) dz -= 1;
if (keys['KeyS']) dz += 1;
if (keys['KeyA']) dx -= 1;
if (keys['KeyD']) dx += 1;
// normalize
const len = Math.hypot(dx, dz);
if (len > 0) { dx /= len; dz /= len; }
// rotate by yaw
const sinY = Math.sin(player.yaw), cosY = Math.cos(player.yaw);
const worldX = dx * cosY - dz * sinY;
const worldZ = dx * sinY + dz * cosY;
```

Wait, let me think about the coordinate mapping. In Three.js, typically +Z is toward the viewer (away from camera) or into the screen depending. Let me define: player looks in the direction of yaw. When yaw=0, looking in -Z direction (standard). Forward movement (W) should move in the look direction.

Look direction: with rotation order YXZ and rotation.set(pitch, yaw, 0):
- The camera looks along... Let me compute. Rotation about Y by yaw, then about X by pitch.

For yaw=0, pitch=0, camera looks along -Z (default camera). Forward vector = (0, 0, -1) rotated.

Actually, camera.getWorldDirection gives the forward. Let me just use the standard: horizontal movement.

Forward (horizontal) direction for yaw θ: 
- The camera's forward projected onto ground plane.
- forward = (sin(yaw)... hmm let me just derive.

Actually, let me use getWorldDirection for movement to be safe. But that includes pitch. For horizontal movement I want to ignore pitch. Let me compute manually.

With rotation.order = 'YXZ' and rotation.set(pitch, yaw, 0):
The rotation matrix R = Ry(yaw) * Rx(pitch) * Rz(0).

Default forward is (0,0,-1). After applying R:
Ry(yaw) = [[cos, 0, sin],[0,1,0],[-sin,0,cos]]
Rx(pitch) = [[1,0,0],[0,cp,-sp],[0,sp,cp]]

Ry(yaw) * (0,0,-1):
First, (0,0,-1) in world after Ry: 
Ry * (0,0,-1)^T = (sin(yaw)*(-1), 0, cos(yaw)*(-1)) = (-sin(yaw), 0, -cos(yaw)).

Hmm wait let me redo. Ry(yaw) applied to vector (0,0,-1):
Row 1: cos*0 + 0*0 + sin*(-1) = -sin(yaw)
Row 2: 0*0 + 1*0 + 0*(-1) = 0
Row 3: -sin*0 + 0*0 + cos*(-1) = -cos(yaw)

So horizontal forward (ignoring pitch) = (-sin(yaw), 0, -cos(yaw)).

So when yaw=0, forward = (0,0,-1). Good, that's -Z.

Movement: worldX = -sin(yaw) * forwardAmount, worldZ = -cos(yaw) * forwardAmount. Where forwardAmount combines W/S and left/right strafe.

Let me define input vector (ix, iz) where W = forward (iz = -1? or +1?). Let me use: pressing W moves forward. Let me set:
- forward input f = (W? -1 : 0) + (S? 1 : 0)... 

Let me just do it cleanly. Let inputDir be a 2D vector in (east, north) where east = +X, north = +Z... ugh, let me just be concrete.

Let me define:
- keyW: move forward
- keyS: move backward
- keyA: move left
- keyD: move right

Forward direction (horizontal) = (-sin(yaw), -cos(yaw)) for (x, z).
Right direction (horizontal) = (cos(yaw), -sin(yaw)).

Wait, right = forward rotated -90 degrees about Y. Rotating (-sin, -cos) by -90°: 
Rotation by -90 in 2D: (x,y) -> (x*cos(-90) - y*sin(-90), x*sin(-90) + y*cos(-90)) = (x*0 - y*(-1), x*(-1) + y*0) = (y, -x).
So right = (-cos(yaw), sin(yaw))? Let me recompute. forward = (-sin, -cos). right = (forward_y, -forward_x) = (-cos, sin). Hmm.

Let me just verify with yaw=0: forward = (0, -1) (moving in -Z when pressing W). right = (-1, 0) (moving in -X when pressing D)? That means D moves in -X. Is that right? 

With yaw=0 looking toward -Z, your right hand points toward... -X or +X? If I'm looking in -Z direction (into the screen in a top-down view where +X is right and +Z is down/on-screen), then my right is... Let me set up: top-down, +X to the right, +Z toward bottom of screen (since -Z is up/forward). Looking toward -Z (up on screen), my right hand points to +X? No wait.

Ugh, let me think physically. Standard right-handed coords: X right, Y up, Z toward viewer (out of screen). But in Three.js scene, camera looks at -Z by default, so "into the screen" is -Z.

Top-down map: let's say we look down from +Y. X is east (right on map), Z is... if we look from +Y downward with standard orientation, +Z points south (down on map) and -Z points north (up on map). Camera facing north (-Z) means facing up on the map. Player's right when facing up on map = east = +X.

So pressing D (strafe right) should move toward +X. Let me redo the right direction.

forward (facing north/-Z) = (0, -1) in (x,z). right should be (+1, 0) = east/+X.

Using my formula right = (-cos, sin): at yaw=0, that's (-1, 0) = west. Wrong sign.

Let me recompute. Rotating forward by +90° (counterclockwise in x-z plane viewed from top... but orientation matters). 

Let me just directly derive using rotation matrices but carefully.

Actually, simpler: let me define movement using the camera's actual right vector. camera.getWorldDirection gives forward. For right, I can use camera.right (after updating rotation) via camera.matrixWorld. Or compute: right = forward × up, normalized. up = (0,1,0).

right = forward × up. If forward_h = (-sin(yaw), 0, -cos(yaw)) (horizontal part), up=(0,1,0):
right = forward × up = |i j k; -sin 0 -cos; 0 1 0|
= i(0*0 - (-cos)*1) - j((-sin)*0 - (-cos)*0) + k((-sin)*1 - 0*0)
= i(cos) - j(0) + k(-sin)
= (cos(yaw), 0, -sin(yaw)).

At yaw=0: right = (1, 0, 0) = +X = east. Correct!

So:
- Forward horizontal: F = (-sin(yaw), 0, -cos(yaw))
- Right horizontal: R = (cos(yaw), 0, -sin(yaw))

Movement: 
moveVec = F * (S? 1 : 0) ... wait W is forward, S is backward.
moveVec = F * (W?1:0) + F*(-1)*(S?1:0) + R*(D?1:0) + R*(-1)*(A?1:0)

Let me define:
fwdInput = (W ? 1 : 0) - (S ? 1 : 0)  // +1 for W, -1 for S
sideInput = (D ? 1 : 0) - (A ? 1 : 0)  // +1 for D, -1 for A

moveVec = F * fwdInput + R * sideInput

Then normalize and multiply by speed.

moveVec.x = -sin(yaw)*fwdInput + cos(yaw)*sideInput
moveVec.z = -cos(yaw)*fwdInput - sin(yaw)*sideInput

Let me verify: W pressed, yaw=0: fwdInput=1, sideInput=0. moveVec = (0, 0, -1). Moves -Z (north/forward). Correct.
D pressed, yaw=0: sideInput=1. moveVec = (cos0, 0, -sin0) = (1, 0, 0). Moves +X (east/right). Correct.

Great.

Now normalization: len = hypot(moveVec.x, moveVec.z). If len>0, divide.

### Collision details

Let me write updatePlayer:

```javascript
function updatePlayer(dt) {
  // Movement input
  const fwdInput = (keys['KeyW'] ? 1 : 0) - (keys['KeyS'] ? 1 : 0);
  const sideInput = (keys['KeyD'] ? 1 : 0) - (keys['KeyA'] ? 1 : 0);
  const sinY = Math.sin(player.yaw), cosY = Math.cos(player.yaw);
  let mx = -sinY * fwdInput + cosY * sideInput;
  let mz = -cosY * fwdInput - sinY * sideInput;
  const len = Math.hypot(mx, mz);
  if (len > 0) { mx /= len; mz /= len; }
  const speed = 5.5;
  let vx = mx * speed;
  let vz = mz * speed;
  
  // Gravity
  player.vel.y -= 25 * dt;
  
  // Jump
  if (keys['Space'] && player.onGround) {
    player.vel.y = 8.5;
    player.onGround = false;
  }
  
  // Move per axis
  // X
  player.pos.x += vx * dt;
  if (collides(player.pos.x, player.pos.y, player.pos.z)) {
    player.pos.x -= vx * dt;
    player.vel.x = 0;
  }
  // Z
  player.pos.z += vz * dt;
  if (collides(player.pos.x, player.pos.y, player.pos.z)) {
    player.pos.z -= vz * dt;
    player.vel.z = 0;
  }
  // Y
  player.pos.y += player.vel.y * dt;
  player.onGround = false;
  if (collides(player.pos.x, player.pos.y, player.pos.z)) {
    if (player.vel.y < 0) {
      // landed
      player.onGround = true;
    }
    player.pos.y -= player.vel.y * dt;
    player.vel.y = 0;
  }
  
  // Fall respawn
  if (player.pos.y < -20) {
    player.pos.set(8, surfaceHeightAt(8, 8), 8);
    player.vel.set(0, 0, 0);
  }
}
```

Wait, there's an issue with the Y collision and landing. When moving down and collide, I revert and set onGround. When moving up and collide (hit head), I revert but don't set onGround. The condition `if (player.vel.y < 0)` handles landing. But I set onGround=false before the collision check, then set true if landing. Good. But what about after jumping, at the peak vel.y ~ 0, still airborne. Fine.

One issue: after landing, onGround=true, but if the block below is now air (was broken), next frame they'd fall. That's fine.

Also the collision check for X and Z uses the updated position but checks against full box. Good.

Hmm, but there's a subtle bug: when I move X and it collides, I revert X. Then move Z and check collision with reverted X. Then move Y. That's standard axis-separated. Good.

But the collision for X and Z doesn't reset velocity properly for the "revert" — actually it does set vel.x=0. Fine.

Let me double check collides uses floor ranges correctly. Box from (px-0.3, py, pz-0.3) to (px+0.3, py+1.8, pz+0.3). Blocks are unit cubes at integer coords occupying [x, x+1]. A block at integer (bx,by,bz) overlaps the box if bx < px+0.3 and bx+1 > px-0.3, etc. My loop checks blocks from floor(min) to floor(max). Since max corner is at px+0.3, floor(px+0.3) could equal floor(px)+0 or floor(px) depending. Let me ensure I cover all potentially overlapping blocks.

minX = px-0.3, the smallest block index that could overlap is floor(minX). maxX = px+0.3, largest is floor(maxX). Since block bx occupies [bx, bx+1], it overlaps box's x-range [minX, maxX] if bx <= maxX and bx+1 >= minX, i.e., bx <= maxX and bx >= minX-1. floor(minX) to floor(maxX) covers bx from floor(minX) to floor(maxX). Is floor(minX) <= minX-1? Not necessarily. floor(minX) >= minX-1 always (since floor(minX) > minX-1). And we need bx >= minX-1. floor(minX) >= minX-1 means floor(minX) might be > minX-1, so we might miss bx = minX-1 if that's an integer... 

Hmm, let me just expand the range by checking floor(minX)-0 to floor(maxX). Actually since the box is smaller than a block (half-width 0.3 < 0.5), the box is always within a small region. The block containing the center px is floor(px). The box extends 0.3 around. So overlapping blocks are floor(px-0.3) to floor(px+0.3). Since 0.3 < 0.5, this is either {floor(px)} or {floor(px), floor(px)+1}? No: px-0.3 to px+0.3. If px = 2.3, range is [2.0, 2.6], floor gives 2 to 2. Block 2 occupies [2,3], overlaps. Good. If px=2.0, range [1.7, 2.3], floor 1 to 2. Blocks 1 ([1,2]) and 2 ([2,3]). Block 1 overlaps [1.7,2.0]? Block 1 occupies [1,2], box x is [1.7,2.3]. Overlap [1.7,2.0]. Yes overlaps. Block 2 occupies [2,3], overlaps [2.0,2.3]. Yes. So checking floor(minX)=1 to floor(maxX)=2 is correct.

But wait, when px=2.0 exactly, is the player standing exactly on a block boundary? The box x is [1.7, 2.3]. Both blocks 1 and 2 are checked. Good, no miss.

What about px = 2.3, box [2.0, 2.6]. floor(2.0)=2, floor(2.6)=2. Only block 2. Block 2 occupies [2,3], box [2.0,2.6] overlaps. Good.

Edge case px=2.5: box [2.2, 2.8], floor 2 to 2. Block 2. Good.

So floor(minX) to floor(maxX) works because the box width 0.6 < 1. Actually let me double-check a potential miss: px such that box straddles. px=2.0 covered. I think it's fine because box width 0.6 < 1 means at most 2 blocks, and floor(min) to floor(max) captures both. Let me verify px=2.0 gives floor(1.7)=1, floor(2.3)=2 → blocks 1,2. Both checked. px=2.9: box [2.6,3.2], floor(2.6)=2, floor(3.2)=3 → blocks 2,3. Block 2 [2,3] overlaps [2.6,3.0]? yes. Block 3 [3,4] overlaps [3.0,3.2]? yes. Good.

OK the collision range is fine.

For Y: minY=py, maxY=py+1.8. floor(py) to floor(py+1.8). Height 1.8 < 2, so at most 3 blocks. E.g., py=5.0: [5,6.8], floor 5 to 6 → blocks 5,6. But block could be at 6 ([6,7]) overlapping [6,6.8]. And is there a block at 5? [5,6] overlaps [5,5]? The box bottom is exactly at 5.0. Block 5 occupies [5,6], box y is [5,6.8]. Overlap [5,6.8]. Yes. Good. What about py=5.0, do we need block 4? Block 4 [4,5], box [5,6.8]. Overlap only at y=5.0 (touching). Not really overlapping (measure zero). So not needed. Good.

Hmm, but actually there's a subtle issue: when the player is standing exactly on top of a block at y=5 (feet at y=5.0), the box is [5, 6.8]. Block at y=5 occupies [5,6]. The box overlaps it fully in y [5,6.8]∩[5,6]=[5,6]. So collides() returns true, and the player can't move down. But that's the resting state—we want them to rest ON the block, meaning feet at y=5.0 sitting on block top at y=5.0. Wait, block at y=5 has top at y=6. Feet at y=5 would be INSIDE the block [5,6]. That's wrong.

Let me reconsider. If feet (py) = 5.0 and there's a block occupying y from 5 to 6, the player's feet are inside the block. That shouldn't happen if collision works. Let me trace: player falls, vel.y negative. At some point py approaches 5.0 (top of block below is at y=5? No). 

Let me reconsider block positions. A block at integer y occupies [y, y+1] in world. So block at y=4 occupies [4,5], top surface at y=5. Player stands on top of it with feet at y=5.0. Player box y = [5.0, 6.8]. Does it collide with block y=4 ([4,5])? Box [5.0,6.8], block [4,5]. Overlap at y=5.0 only (touching). collides checks floor(5.0)=5 to floor(6.8)=6, so blocks 5 and 6, NOT block 4! So no collision detected, player falls through!

That's a bug. The issue is the block at y=4 has its top at y=5, exactly at the player's feet. My range floor(minY)=floor(5.0)=5 misses block 4.

I need to include the block below the feet. Let me expand: check floor(minY)-? Hmm. The problem is floating point: feet at exactly 5.0, block top at 5.0. They touch but don't overlap in exact math. But physically we want the player to rest there.

Better approach: when landing, snap the player to rest exactly on top. Let me handle collision differently. Instead of reverting exactly, detect the collision and snap.

Alternative: expand the check range to include floor(minY) and also handle the boundary. Actually the cleaner fix: make collides treat touching as collision, OR snap on landing.

Let me change the Y collision to snap:
```javascript
player.pos.y += player.vel.y * dt;
if (collides(...)) {
  if (player.vel.y < 0) {
    // land on top of block: snap feet to block top
    // find the block we hit
    player.pos.y = Math.round(player.pos.y); // snap to integer? risky
    player.onGround = true;
  } else if (player.vel.y > 0) {
    // hit head
  }
  player.vel.y = 0;
}
```

Hmm, snapping to Math.round isn't robust. Let me think differently.

Better: expand collision detection to include adjacent blocks by a small epsilon, OR change the collision to check block centers.

Actually, the cleanest robust approach used in many voxel games: check the blocks that the box overlaps using inclusive ranges with a small expansion. Let me expand the search box by a tiny epsilon (like 0.001) so touching counts:

```javascript
const eps = 0.0001;
const bx0 = Math.floor(minX - eps), bx1 = Math.floor(maxX + eps);
const by0 = Math.floor(minY - eps), by1 = Math.floor(maxY + eps);
const bz0 = Math.floor(minZ - eps), bz1 = Math.floor(maxZ + eps);
```

With eps, feet at 5.0: minY=5.0, by0 = floor(5.0 - 0.0001) = floor(4.9999) = 4. Now block 4 is included. Box [5.0, 6.8] vs block [4,5]: overlap at [5.0,5.0] (measure zero) but with eps expansion, block 4 is [4,5] and we check if it intersects [minX-eps, maxX+eps]×... Actually the intersection is still measure zero in exact terms. Hmm.

Let me think about this more carefully. The real issue: when feet are at y=5.0 and block top is at y=5.0, they're touching. For collision we consider touching as collision (can't pass through). So I should treat the box as slightly expanded, OR treat the block as slightly expanded.

Simplest: expand the player box by epsilon in collides so touching → overlap:
```javascript
const e = 0.0001;
const minX = px - 0.3 - e, maxX = px + 0.3 + e;
const minY = py - e, maxY = py + 1.8 + e;
const minZ = pz - 0.3 - e, maxZ = pz + 0.3 + e;
```
Now box y = [5.0-e, 6.8+e] = [4.9999, 6.8001]. Block y=4 occupies [4,5]. Overlap [4.9999, 5.0]. Positive measure! So collides detects it. 

Then in the Y collision handling, I revert by moving back by vel.y*dt, which would put feet at ~5.0 again (since we moved down by vel.y*dt and revert). Actually reverting: player.pos.y -= player.vel.y*dt. If we moved down by delta (vel.y*dt negative), reverting adds delta back, returning to previous y. But previous y had feet at maybe 4.99. Hmm, this oscillates.

Let me instead snap on landing. When colliding and vel.y < 0:
```javascript
// find highest block top within box footprint
// Actually just snap feet to the top of the block below
```

This is getting complicated. Let me use a cleaner collision resolution: on vertical collision, snap the player to rest precisely.

For landing (vel.y < 0): the player should rest on top of the block. The top of the block they're standing on is at some integer y_top. Feet should be at y_top. Since blocks are at integer positions, y_top is an integer. I can compute it as: the block at (round(px), current_feet_block, round(pz))... but px, pz vary.

Alternative clean approach: On landing, set player.pos.y to the integer value equal to the top of the block. The block we collided with has its top at floor(minY_block)+1... 

Let me simplify: when landing, I know the player is standing on a block. The block's top surface is at an integer y. I'll compute it from the collision. Actually, let me just snap to the nearest integer that's <= current feet:

Since feet should rest exactly on a block top (integer), and the player was falling, the correct resting feet position is ceil-ish. Let me do:
```javascript
player.pos.y = Math.floor(player.pos.y);
```
Wait if feet at 4.99 (fell slightly through), floor gives 4, too low (inside block [4,5]). If feet at 5.0, floor gives 5. If feet at 5.01, floor gives 5. 

Hmm. When falling, before collision feet were at say 5.05 (no collision, box [5.05, 6.85], block 4 [4,5] no overlap since 5.05>5). Then we move by vel.y*dt, feet go to 4.99, now box [4.99, 6.79], block 4 [4,5] overlaps [4.99,5.0]. Collide! Snap feet to 5.0 (top of block 4). Math.floor(4.99) = 4. Wrong.

So I should snap to the block top, which is the integer just above the fallen position. Let me use:
```javascript
player.pos.y = Math.ceil(player.pos.y - 0.0001); // to 5.0
```
ceil(4.99 - 0.0001) = ceil(4.9899) = 5. Good. And if feet at exactly 5.0 (already resting), ceil(5.0-0.0001)=ceil(4.9999)=5. Good.

But this assumes the block top is an integer, which it is (blocks at integer y have tops at integer y+1... wait block at y=4 has top at y=5, which is integer. Yes block tops are always at integer y since blocks are unit cubes at integer positions). So feet rest at integer. Good.

Actually wait, is that always true? The player rests on top of a block whose top surface is at integer y. Yes. So snapping feet to integer via ceil works.

But hold on, what if the player lands on a block but due to horizontal position the "block below" isn't directly... no, collision is per-block in the footprint. The landing snaps to integer feet regardless. Since the block top is integer, feet at integer = resting on that block top. Correct.

Let me also handle head-bumping (vel.y > 0): snap feet down? No, snap the player down so head clears. When hitting head, the player's top (py+1.8) is inside a block. Snap so py+1.8 = block bottom. Block bottom is integer. So py = integer - 1.8. Hmm, that's not integer. Let me snap:
```javascript
// hit head: the block is above. player top should be at block bottom (integer)
player.pos.y = Math.floor(player.pos.y + 1.8) - 1.8;
```
E.g., head hits block at y=7 ([7,8], bottom at 7). Player top py+1.8 should be 7, so py=5.2. If current py=5.25 (top 7.05, inside block [7,8]), snap: floor(5.25+1.8)-1.8 = floor(7.05)-1.8 = 7-1.8 = 5.2. Good.

But this is a minor case; let me keep it simple. Actually, for robustness let me just revert position on any vertical collision rather than snap, but ALSO snap on landing to avoid sinking. Let me combine:

```javascript
// Y
const prevY = player.pos.y;
player.pos.y += player.vel.y * dt;
if (collides(player.pos.x, player.pos.y, player.pos.z)) {
  if (player.vel.y < 0) {
    player.onGround = true;
    player.pos.y = Math.ceil(player.pos.y - 0.0001); // snap to block top
  } else if (player.vel.y > 0) {
    player.pos.y = prevY; // revert head collision
  }
  player.vel.y = 0;
}
```

Wait, but with the epsilon expansion in collides, reverting to prevY when hitting head: prevY had no collision (feet at prevY, box didn't collide). Good.

Hmm, but actually there's still the issue that after snapping to integer on landing, the NEXT frame the player might still slightly overlap due to gravity adding vel.y*dt again. Let me trace: feet at 5.0 (resting, onGround=true). Gravity: vel.y -= 25*dt → vel.y becomes negative (say -0.125 for dt=0.005). Then move: feet to 5.0 - 0.000625 = 4.999. collides? box [4.999-e, ...], block 4 [4,5] overlaps. Collide! vel.y<0, so onGround=true, snap feet to ceil(4.999-0.0001)=ceil(4.9989)=5.0. Good, stays at 5.0. vel.y=0.

But wait, I set vel.y=0 AFTER the jump check. Let me reorder: jump check uses onGround. If onGround was true from previous frame, and space pressed, jump. Then gravity adds vel.y. Then movement. OK the sequence within a frame:
1. Compute movement input (vx, vz)
2. Apply gravity to vel.y
3. Jump check (if onGround and space, set vel.y=8.5, onGround=false)
4. Move X, Z (with collision)
5. Move Y (with collision, snap on land)

Wait, but if I jump in step 3, onGround=false, vel.y=8.5. Then step 5 moves up. Good. If not jumping, vel.y is negative from gravity, step 5 tries to move down, collides, snaps back to 5.0, onGround=true, vel.y=0. Good.

There's a subtle issue: in step 5, after snapping to 5.0 and vel.y=0, onGround=true. Next frame gravity makes vel.y negative again, tries to move, collides, snaps. Oscillates but stays put. Fine, no visual issue since it snaps to same position.

Actually, a cleaner way to avoid the oscillation: only apply gravity when not onGround. Let me add: if onGround and vel.y <= 0, set vel.y = 0 (don't accumulate). Actually simplest: when onGround, don't apply gravity, keep vel.y=0.

```javascript
if (!player.onGround) {
  player.vel.y -= 25 * dt;
} else {
  player.vel.y = 0;
}
```

But there's a catch: onGround is set true during Y collision resolution. On the very next frame, onGround is true so gravity skipped, vel.y=0, then movement tries to move down by 0, no collision issue, stays. Then if player jumps, onGround set false. Good.

But how does onGround get set true initially? During a fall, step 5 collision detects and sets onGround=true. Good.

Let me restructure cleanly:

```javascript
function updatePlayer(dt) {
  // horizontal input
  ...
  // gravity & jump
  if (player.onGround) {
    player.vel.y = 0;
    if (keys['Space']) {
      player.vel.y = 8.5;
      player.onGround = false;
    }
  } else {
    player.vel.y -= 25 * dt;
  }
  
  // move X
  ...
  // move Z
  ...
  // move Y
  player.pos.y += player.vel.y * dt;
  if (collides(...)) {
    if (player.vel.y < 0) {
      player.onGround = true;
      player.pos.y = Math.ceil(player.pos.y - 1e-4);
    } else {
      player.pos.y -= player.vel.y * dt; // revert
    }
    player.vel.y = 0;
  }
}
```

This looks good.

Now, one concern: the initial spawn. Player spawns at x=8, z=8, above terrain. I compute surfaceHeightAt(8,8) and set pos.y = that + 1 (or +0.5). Let me set pos.y = surfaceHeightAt(8,8) + 1.0. But at spawn, chunks near (8,8) need to be generated first. I'll generate initial chunks before the loop, or generate on first frame. Let me generate an initial set of chunks synchronously at startup so spawn works.

Actually, the updateChunks runs every frame. On frame 1, it generates chunks within 5 of player (up to 4). But spawn needs terrain at (8,8) which is the player's chunk. Let me pre-generate the player's chunk and neighbors at startup.

Let me add an init step:
```javascript
function initWorld() {
  // generate a few chunks around spawn so spawn height is available
  for (let dx=-2; dx<=2; dx++) for (let dz=-2; dz<=2; dz++) {
    const cx = 0 + dx, cz = 0 + dz; // player at world (8,8) → chunk 0,0
    if (!chunks.has(chunkKey(cx,cz))) generateChunk(cx, cz);
  }
  player.pos.set(8, surfaceHeightAt(8,8)+1.0, 8);
}
```

Player at world x=8, z=8 → chunk = floor(8/16)=0. So player chunk is (0,0). Good.

Let me make sure surfaceHeightAt works: it reads blocks. After generating chunks around (0,0), readBlock(8,y,8) works. Good.

Now generateChunk:
```javascript
function generateChunk(cx, cz) {
  const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
  const setLocal = (x, y, z, id) => { data[x + z*16 + y*256] = id; };
  const getLocal = (x, y, z) => {
    if (x<0||x>=16||z<0||z>=16||y<0||y>=80) return -1; // sentinel for out-of-chunk
    return data[x + z*16 + y*256];
  };
  
  for (let z=0; z<16; z++) {
    for (let x=0; x<16; x++) {
      const wx = cx*16 + x;
      const wz = cz*16 + z;
      // terrain height
      const m = fractal2(wx*0.004, wz*0.004, 4);
      const h = fractal2(wx*0.02, wz*0.02, 4);
      const H = Math.floor(5 + m*m*58 + h*10);
      // fill
      for (let y=0; y<H; y++) {
        if (y === 0) {
          setLocal(x,y,z, STONE);
        } else if (y < H-3) {
          setLocal(x,y,z, STONE);
        } else {
          // 3 layers under surface
          if (H <= 16) setLocal(x,y,z, SAND);
          else if (H >= 37) setLocal(x,y,z, STONE);
          else setLocal(x,y,z, DIRT);
        }
      }
      // surface
      if (H >= 46) setLocal(x,H,SNOW);
      else if (H >= 37) setLocal(x,H,STONE);
      else if (H <= 16) setLocal(x,H,SAND);
      else setLocal(x,H,GRASS);
      
      // caves
      for (let y=3; y<=H-2; y++) {
        if (noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) {
          setLocal(x,y,z, AIR);
        }
      }
      
      // trees
      if (getSurfaceType(...) === grass && treeHash(wx,wz) < 0.02) {
        // place tree if trunk fits in chunk
        // trunk at (x,z), need leaves within chunk: check x,z in [2,13]? 
        // spec says trunk fits inside chunk, so just 0<=x<16, 0<=z<16
        // place leaves only if within chunk
      }
    }
  }
  chunks.set(chunkKey(cx,cz), { data: data, mesh: null });
}
```

For the surface type check for trees, I need to know if the surface is grass. Let me compute: grass if 16 < H < 37 (since H<=16→sand, H>=37→stone, else grass). And H>=46→snow (but that's >=37 too). Let me recompute surface type:
- H >= 46: snow
- H >= 37: stone
- H <= 16: sand
- else (17..36): grass

So grass when 17 <= H <= 36.

For trees:
```javascript
const isGrass = (H >= 17 && H <= 36);
if (isGrass && treeHash(wx, wz) < 0.02) {
  // check trunk fits: 0<=x<16, 0<=z<16 (always true here)
  // but leaves extend 2 out; place only within chunk
  const th = H;
  for (let i=1;i<=4;i++) setLocal(x, th+i, z, WOOD);
  let ly = th + 5;
  for (let dx=-2;dx<=2;dx++) for (let dz=-2;dz<=2;dz++) {
    const nx=x+dx, nz=z+dz;
    if (nx>=0&&nx<16&&nz>=0&&nz<16) setLocal(nx, ly, nz, LEAVES);
    if (nx>=0&&nx<16&&nz>=0&&nz<16) setLocal(nx, ly+1, nz, LEAVES);
  }
  ly += 2;
  for (let dx=-1;dx<=1;dx++) for (let dz=-1;dz<=1;dz++) {
    const nx=x+dx, nz=z+dz;
    if (nx>=0&&nx<16&&nz>=0&&nz<16) setLocal(nx, ly, nz, LEAVES);
  }
  ly += 1;
  setLocal(x, ly, z, LEAVES);
}
```

Wait, the spec: "leaves as a 5x5 layer twice, then 3x3, then 1 on top". So two 5x5 layers stacked, then a 3x3, then a single on top. Let me re-read: "leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)". 

So:
- Layer 1: 5x5 at ly
- Layer 2: 5x5 at ly+1 ("twice" = two layers)
- Layer 3: 3x3 at ly+2
- Layer 4: 1 at ly+3

"only into air" — only place leaves where the cell is air. So I should check that the target cell is currently air before placing leaves. But careful: the trunk occupies x, th+1..th+4. The leaf layers start at th+5. Let me check air before placing each leaf.

Actually "only into air" likely means don't overwrite existing blocks (like the trunk or terrain). Let me add a check: only set if current value is AIR.

```javascript
if (getLocal(nx, ly, nz) === AIR) setLocal(nx, ly, nz, LEAVES);
```

But getLocal returns the data which for the trunk area... the trunk is at x, th+1..4, and leaf layers at th+5+. The trunk doesn't overlap leaf layers. Terrain below is filled. At th+5+, it should be air (sky). So checking air is fine.

Hmm, but wait: what if the terrain is higher than expected due to... no, H is the surface, th=H, so th+5 is 5 above surface = air. Good.

Let me define treeHash:
```javascript
function treeHash(x, z) {
  return hash2(x * 2654435761 ^ z * 40503, ...);
}
```
Let me just make a simple deterministic hash returning [0,1):
```javascript
function columnHash(x, z) {
  let h = (x * 31 + z) * 2654435761;
  h = (h ^ (h >>> 13)) * 1274126177 | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```

Actually I realize I should double check the "trunk fits inside the chunk" constraint more carefully. If I only place leaves within chunk bounds, trees at edges will have truncated leaves. That's acceptable. But to reduce weirdness, maybe I should require the trunk to be at least 2 blocks from edge so full leaves fit. But the spec explicitly says "the trunk fits inside the chunk", implying just checking trunk position (0<=x<16, 0<=z<16), which is always true in the loop. So the constraint is trivially satisfied, and leaves get clipped at edges. I'll go with placing leaves within bounds.

Hmm, actually, re-reading: "when a per-column hash < 0.02 and the trunk fits inside the chunk". This suggests the hash AND the fit check both gate tree placement. Since trunk is always in chunk, effectively just the hash gates. But maybe they intend to skip trees that would extend beyond. I'll keep the within-bounds leaf placement as the safety.

### Meshing details

Let me write buildChunkMesh:

```javascript
const FACE_DEFS = [
  // [+X]
  { n: [1,0,0], l: 0.8, v: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  // [-X]
  { n: [-1,0,0], l: 0.8, v: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  // [+Y] top
  { n: [0,1,0], l: 1.0, v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  // [-Y] bottom
  { n: [0,-1,0], l: 0.55, v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  // [+Z]
  { n: [0,0,1], l: 0.8, v: [[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
  // [-Z]
  { n: [0,0,-1], l: 0.8, v: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]] },
];
```

For each face, I need the corners in an order that forms a proper polygon with the outward normal (for culling, though we don't cull; but for correct rendering order it doesn't matter much). The 2 triangles: (0,1,2) and (0,2,3).

```javascript
function buildChunkMesh(cx, cz) {
  const c = chunks.get(chunkKey(cx, cz));
  if (!c || !c.data) return null;
  const data = c.data;
  const positions = [];
  const normals = [];
  const colors = [];
  const baseX = cx * 16;
  const baseZ = cz * 16;
  
  for (let y=0; y<CHUNK_HEIGHT; y++) {
    for (let z=0; z<16; z++) {
      for (let x=0; x<16; x++) {
        const id = data[x + z*16 + y*256];
        if (id === AIR) continue;
        const wx = baseX + x;
        const wy = y;
        const wz = baseZ + z;
        const col = BLOCK_COLORS[id];
        if (!col) continue;
        for (const face of FACE_DEFS) {
          const nx = wx + face.n[0];
          const ny = wy + face.n[1];
          const nz = wz + face.n[2];
          if (readBlock(nx, ny, nz) === AIR) {
            const light = face.l;
            const r = col[0]*light, g = col[1]*light, b = col[2]*light;
            for (const cv of face.v) {
              positions.push(wx+cv[0], wy+cv[1], wz+cv[2]);
              normals.push(face.n[0], face.n[1], face.n[2]);
              colors.push(r, g, b);
            }
          }
        }
      }
    }
  }
  
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  const mesh = new THREE.Mesh(geo, blockMaterial);
  mesh.position.set(baseX, 0, baseZ); // keep mesh at origin? 
  ...
}
```

Wait, the spec says "keep the mesh at the origin". So the mesh should be positioned at (0,0,0) in world, and I use world coordinates for vertices. So I should NOT offset the mesh by baseX, baseZ. Instead, vertices already use world coordinates (wx, wy, wz). So mesh.position = (0,0,0) and vertices are in world space.

But then for raycasting, the meshes are at world positions via their vertices. Raycaster works in world space if mesh is at origin with world-space vertices. Good.

Let me set mesh.position.set(0,0,0). Actually default is (0,0,0), so I can skip. But to be safe, set it.

Wait, but if I keep mesh at origin and vertices in world coords, then multiple chunks' meshes all sit at origin but have vertices at different world positions. Raycasting against them: intersectObjects tests against each mesh's geometry in local space, transformed by mesh.matrixWorld. Since mesh at origin, local=world for the transform, and vertices are already world coords. So raycasting works correctly. Good.

Let me keep it simple: mesh.position = (0,0,0), vertices in world coords.

Actually, hmm, but then when I do scene.add(mesh), it's at origin. Fine.

Let me store chunkMeshes globally:
```javascript
const chunkMeshes = [];
```
Add meshes to this array when created.

blockMaterial:
```javascript
const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

### Outline box

```javascript
const outlineGeo = new THREE.BoxGeometry(1.01, 1.01, 1.01);
const outlineEdges = new THREE.EdgesGeometry(outlineGeo);
const outline = new THREE.LineSegments(outlineEdges, new THREE.LineBasicMaterial({color:0x000000}));
outline.visible = false;
scene.add(outline);
```

Actually LineSegments with EdgesGeometry gives a wireframe box. Good.

Each frame, updateTargetOutline:
```javascript
function updateTargetOutline() {
  const t = getTarget();
  if (t) {
    outline.visible = true;
    outline.position.set(t.target.x + 0.5, t.target.y + 0.5, t.target.z + 0.5);
  } else {
    outline.visible = false;
  }
}
```

### getTarget with raycast

```javascript
function getTarget() {
  raycaster.set(camera.position, dir);
  raycaster.far = 6;
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length === 0) return null;
  const hit = hits[0];
  const p = hit.point;
  const n = hit.face.normal;
  return {
    target: { x: Math.floor(p.x - n.x*0.5), y: Math.floor(p.y - n.y*0.5), z: Math.floor(p.z - n.z*0.5) },
    place: { x: Math.floor(p.x + n.x*0.5), y: Math.floor(p.y + n.y*0.5), z: Math.floor(p.z + n.z*0.5) },
  };
}
```

dir = camera.getWorldDirection(new THREE.Vector3()).

But there's a concern: the chunk meshes have vertex normals but the geometry is non-indexed. Raycaster.intersectObjects needs the geometry to have face normals or compute them. For non-indexed BufferGeometry, Raycaster computes face normals from the triangle. This should give the correct axis-aligned normal. Let me verify: the triangles I defined have consistent winding for outward normals (I ordered corners CCW when viewed from outside). Raycaster computes normal via cross product of edges, giving outward normal. Good.

Actually, one concern: does Raycaster use the stored normal attribute or compute from geometry? In three.js r128, Raycaster.intersectObject → intersectObjects → _intersectObject → _intersectTriangle computes the normal from the triangle vertices (v0, v1, v2) using cross product, normalized. It does NOT use the geometry's normal attribute. So as long as my triangle winding produces outward normals via cross product, we're good. Let me make sure winding is correct.

For a face with outward normal N, the corners should be counterclockwise when viewed from the direction of N (i.e., from outside). The standard: normal = normalize(cross(v1-v0, v2-v0)). For this to equal the outward normal, corners must be CCW from outside.

Let me verify the +X face: normal [1,0,0], corners [[1,0,0],[1,1,0],[1,1,1],[1,0,1]].
Triangle 1: v0=[1,0,0], v1=[1,1,0], v2=[1,1,1].
cross(v1-v0, v2-v0) = cross([0,1,0], [0,1,1]) = |i j k; 0 1 0; 0 1 1| = i(1*1-0*1) - j(0*1-0*0) + k(0*1-1*0) = i(1) - j(0) + k(0) = [1,0,0]. 
Matches normal [1,0,0]. 

-Y face (bottom): normal [0,-1,0], corners [[0,0,0],[1,0,0],[1,0,1],[0,0,1]].
Triangle 1: v0=[0,0,0],v1=[1,0,0],v2=[1,0,1].
cross([1,0,0],[1,0,1]) = |i j k;1 0 0;1 0 1| = i(0*1-0*0) - j(1*1-0*1) + k(1*0-0*1) = i(0) - j(1) + k(0) = [0,-1,0]. Matches. 

Good, winding is correct.

### Now let me also double check the raycast hit.point for a merged geometry.

When intersecting a non-indexed geometry, hit.point is the world-space intersection point (transformed by mesh matrix). Since mesh at origin, it's world coords. Good.

### Water plane

The water plane is at y=14.3, large (500x500), centered on player. It's visual only. I should probably exclude it from raycasting (it's not in chunkMeshes, so fine). But it might interfere visually. Opacity 0.6. Also, the water plane might be below terrain in mountain areas, that's fine.

Wait, but the water plane at 500x500 centered on player—when player moves to mountains, water still at y=14.3 which is below. Fine.

Should water render behind or in front of terrain? With transparency, order matters. Three.js handles depth by default. Since water is transparent, it renders after opaque objects if sorted. MeshLambertMaterial with transparent renders in the transparent render queue (after opaque). Terrain is opaque. So water renders on top, composited. Good. But water might show through mountains incorrectly—that's fine for a visual effect.

Actually, there might be a z-fighting or sorting issue but let's not worry.

### Clouds

25 clouds at y~90. Let me make them drift. Wrap around player.

### Fog and sky

scene.background = 0x87ceeb, scene.fog = Fog(0x87ceeb, 40, 110).

The water plane is transparent and might look odd in fog but fine.

### Lights

```javascript
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(50, 100, 30);
scene.add(sun);
```

Directional light position should follow player? For consistent lighting, maybe. But it's fine to keep static or move with player. Let me move it with player slightly, or just leave it. Actually, to avoid the light being behind player causing dark faces, let me position it relative to player. But simpler: keep static far away. The ambient 0.65 ensures nothing is fully dark. Let me keep sun static but maybe move it to stay ahead of player. I'll set sun.position based on player each frame:
```javascript
sun.position.set(player.pos.x + 60, 120, player.pos.z + 40);
sun.target.position.copy(player.pos);
sun.target.updateMatrixWorld();
```
Actually DirectionalLight needs target. Let me just set position and it shines toward origin by default. To shine on player, set target to player. Let me do:
```javascript
sun.position.set(player.pos.x + 80, 150, player.pos.z + 80);
```
and leave target at origin (default). Since it's far, roughly parallel rays. Fine.

### Let me now assemble everything.

Let me reconsider the noise functions to make sure they produce good terrain.

hash2(ix, iy): integer inputs. Let me use a solid hash:
```javascript
function hash2(ix, iy) {
  let h = ix * 374761393 + iy * 668265263;
  h = (h ^ (h >>> 13)) * 1274126177;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```
Note: ix*374761393 can overflow for large coords, but JS numbers are doubles, and bitwise ops convert to 32-bit. The multiplication happens in double precision (fine up to 2^53), then >>> converts to 32-bit unsigned. For world coords up to thousands, ix*374761393 could be ~10^12, still < 2^53 (~9*10^15), fine. The XOR shifts and multiply by 1274126177: 1274126177 ~ 1.27*10^9. h before could be ~10^12, times 1.27*10^9 = 1.27*10^21 > 2^53! That loses precision. Hmm.

To avoid precision loss, I should mask to 32-bit earlier. Let me do the operations in 32-bit integer space using | 0 or >>> 0.

```javascript
function hash2(ix, iy) {
  let h = (ix * 374761393 + iy * 668265263) | 0;  // 32-bit
  h = (h ^ (h >>> 13)) | 0;
  h = (h * 1274126177) | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```
Here (ix*374761393 + iy*668265263) — ix, iy up to ~1000, product ~3.7*10^11 + 6.6*10^11 ~ 10^12. | 0 converts to 32-bit (takes lower 32 bits). This is deterministic. Good. Then subsequent ops are in 32-bit. Good.

Wait, but (ix*374761393 + iy*668265263) as a double then | 0: | 0 truncates to 32-bit signed. The double 10^12 is exactly representable? 10^12 < 2^53 so yes exact. | 0 takes two's complement low 32 bits. Deterministic. Good.

For hash3:
```javascript
function hash3(ix, iy, iz) {
  let h = (ix * 374761393 + iy * 668265263 + iz * 1274126177) | 0;
  h = (h ^ (h >>> 13)) | 0;
  h = (h * 1687499431) | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```
iz*1274126177 with iz~1000 → 1.27*10^12. Sum ~ 2.7*10^12 < 2^53. | 0 ok. Good.

noise2(x,y):
```javascript
function noise2(x, y) {
  const ix = Math.floor(x), iy = Math.floor(y);
  const fx = smoothstep(x - ix), fy = smoothstep(y - iy);
  const a = hash2(ix, iy);
  const b = hash2(ix+1, iy);
  const c = hash2(ix, iy+1);
  const d = hash2(ix+1, iy+1);
  return lerp(lerp(a, b, fx), lerp(c, d, fx), fy);
}
```
where lerp(a,b,t)=a+(b-a)*t and smoothstep(t)=t*t*(3-2t).

fractal2:
```javascript
function fractal2(x, y, octaves) {
  let amp=1, freq=1, sum=0, norm=0;
  for (let i=0;i<octaves;i++){
    sum += amp*noise2(x*freq, y*freq);
    norm += amp;
    amp*=0.5; freq*=2;
  }
  return sum/norm; // 0..1
}
```

noise3:
```javascript
function noise3(x,y,z) {
  const ix=Math.floor(x), iy=Math.floor(y), iz=Math.floor(z);
  const fx=smoothstep(x-ix), fy=smoothstep(y-iy), fz=smoothstep(z-iz);
  const c = (dx,dy,dz) => hash3(ix+dx, iy+dy, iz+dz);
  const c000=c(0,0,0), c100=c(1,0,0), c010=c(0,1,0), c110=c(1,1,0);
  const c001=c(0,0,1), c101=c(1,0,1), c011=c(0,1,1), c111=c(1,1,1);
  const i00=lerp(c000,c100,fx), i10=lerp(c010,c110,fx), i01=lerp(c001,c101,fx), i11=lerp(c011,c111,fx);
  const j0=lerp(i00,i10,fy), j1=lerp(i01,i11,fy);
  return lerp(j0,j1,fz);
}
```

These look good.

Now terrain height: H = floor(5 + m*m*58 + h*10). m,h in [0,1]. m*m in [0,1]. So H ranges ~5 to 5+58+10=73. Good, within 80. Sometimes could exceed 80? m*m max 1 → 58, h max 1 → 10, total 73. Safe.

Wait, but fractal2 returns average of octaves weighted, in [0,1]. m*m*58: if m~1, 58. Plus 5 + h*10 (up to 10) = 73. Good.

Surface types: H>=46 snow, H>=37 stone, H<=16 sand, else grass. With H up to 73, mountains get stone then snow. Good. H around 16 → beaches (sand). Grass plains in between.

Let me sanity check typical values. fractal2 with scale 0.004 (m): over world, slow variation, values cluster around 0.5. m*m ~ 0.25 → 14.5. Plus h (scale 0.02, faster) *10. h ~ 0.5 → 5. H ~ 5+14.5+5 = 24.5 → floor 24. Grass (17-36). Good, plains at H~24.

Mountains where m is high (m~0.8): m*m=0.64→37, +5 +h*10(~5) = 47 → snow. Good.

Beaches where m low (m~0.2): m*m=0.04→2.3, +5+5=12 → H~12 ≤16 → sand beach. Good.

Caves: noise3 at scale 0.09, threshold 0.67. Since noise3 in [0,1], ~33% of cells above 0.67 randomly → cave pockets. Between y=3 and H-2. Good.

Now let me make sure the meshing handles the water/lakes. Where H<=16, surface is sand, and water plane at 14.3 covers it (if terrain below 14.3). Actually water is visual only at y=14.3. Where terrain height H < 14, the sand/stone is below water line, water plane floats above at 14.3. Hmm, but the water plane is at 14.3 and terrain surface might be at H (e.g., 12). The sand block at y=11 ([11,12]) ... the water at 14.3 is above. There'd be a gap. But that's fine visually—it looks like water surface above the beach. Actually for lakes, we want water to sit at the surface level. The spec says water at fixed 14.3. Where terrain is lower (H<14ish), water at 14.3 floats above with air gap. The spec says "lakes and beaches appear automatically where terrain is lower". OK, accept the fixed water level.

Actually, let me reconsider. The water plane at 14.3. Terrain surface blocks occupy [H-1, H] (top block at y=H-1 occupies [H-1,H], top surface at H). If H < 14.3, the terrain top is below water, water floats above. If H >= 15, terrain top (at H >= 15) is above water, so on land. Beaches at H~12-16. For H=14, terrain top at 14, water at 14.3, slight gap. For H=15, terrain top 15 > 14.3, land. So water line ~ between H=14 and 15. Reasonable.

OK let me not overthink water. Fixed at 14.3.

### Let me reconsider chunk generation cost.

generateChunk loops 16*16*80 = 20480 blocks, each checking 6 neighbors (readBlock → chunk lookup + array access). That's ~122k readBlock calls per chunk. With up to 4 chunks/frame generation + occasional meshing... Actually generation is 4 chunks/frame max. Each generation ~20480 iterations. That's fine.

But wait, generation also does caves loop (H-2-3 ~ 70 iterations) and tree placement. Minor.

Meshing loops 20480 blocks × 6 faces × readBlock. Similar cost. 2 meshes/frame max. Fine.

Total per frame: 4 gen + 2 mesh = 6 × 20480 × ~7 ≈ 850k operations. Should run at decent FPS. Might be a bit heavy but acceptable.

Hmm, actually readBlock does a Map.get and arithmetic each call. 850k Map.gets per frame might be slowish but probably OK (Chrome handles ~10M simple ops/sec easily, Map.get is fast). Let me optimize readBlock slightly by caching, but probably fine.

Actually, let me reconsider: 4 chunks gen + 2 chunks mesh = 6 chunks. Each chunk: 20480 blocks. Gen: for each block, up to 6 readBlock (cave loop is separate, ~70). So ~6*20480 = 122k readBlock in gen. Mesh: 6*20480*6 = 737k readBlock in mesh. Total ~860k readBlock/frame. Each readBlock: floor x2, Map.get, array index. Say ~100ns each → 86ms/frame just for that. That's ~12 FPS. Too slow!

I need to optimize. Options:
1. Reduce chunk counts. Spec says max 4 gen, max 2 mesh per frame. But maybe I can make readBlock faster.
2. In meshing, cache the chunk's local data access to avoid readBlock overhead for same-chunk neighbors, and only use readBlock for cross-chunk neighbors.

Let me optimize meshing: within a chunk, for neighbor checks, most neighbors are in the same chunk (fast array access), only border neighbors need cross-chunk readBlock. I can inline the same-chunk check.

```javascript
function buildChunkMesh(cx, cz) {
  const c = chunks.get(chunkKey(cx, cz));
  if (!c || !c.data) return null;
  const data = c.data;
  const baseX = cx*16, baseZ = cz*16;
  const positions=[], normals=[], colors=[];
  
  for (let y=0;y<80;y++){
    for (let z=0;z<16;z++){
      for (let x=0;x<16;x++){
        const idx = x + z*16 + y*256;
        const id = data[idx];
        if (id===AIR) continue;
        const col = BLOCK_COLORS[id];
        const wx = baseX+x, wy=y, wz=baseZ+z;
        for (const face of FACE_DEFS){
          const nx=wx+face.n[0], ny=wy+face.n[1], nz=wz+face.n[2];
          // determine neighbor id
          let nid;
          if (face.n[0]!==0){
            // x neighbor
            if (nx<0 || nx>=16){ nid = readBlock(nx,ny,nz); }
            else { nid = data[x+face.n[0] + z*16 + y*256]; }
          } else if (face.n[2]!==0){
            if (nz<0||nz>=16){ nid = readBlock(nx,ny,nz); }
            else { nid = data[x + (z+face.n[2])*16 + y*256]; }
          } else {
            // y neighbor (always same chunk since chunk is 80 tall)
            nid = data[x + z*16 + (y+face.n[1])*256];
          }
          if (nid===AIR){
            const l=face.l;
            const r=col[0]*l,g=col[1]*l,b=col[2]*l;
            for (const cv of face.v){
              positions.push(wx+cv[0],wy+cv[1],wz+cv[2]);
              normals.push(face.n[0],face.n[1],face.n[2]);
              colors.push(r,g,b);
            }
          }
        }
      }
    }
  }
  ...
}
```

This avoids readBlock for most neighbors (same-chunk direct array access). Only border x/z neighbors use readBlock. Y neighbors always same chunk. This reduces readBlock calls dramatically.

Similarly, generation: for caves, no neighbor checks needed (uses noise3). For surface/tree, no neighbor checks. So generation doesn't call readBlock much. Good.

Actually generation doesn't need readBlock at all except... no. Generation fills independently. Good. So generation is just 20480 iterations with simple writes. Fast.

Meshing now: 20480 blocks × 6 faces, mostly direct array access. ~122k iterations with array access. Fast. Only border faces call readBlock. Good.

So per frame: 4 gen (fast) + 2 mesh (fast). Should be well under 16ms. 

But wait, I also call getChunk for neighbor existence checks in updateChunks. That's minor.

Let me also make sure the meshing is correct for cross-chunk: when x+face.n[0] is out of [0,16), I call readBlock(nx,ny,nz) which reads the neighbor chunk. Correct.

Let me refine the indexing: data index for (x', y, z') = x' + z'*16 + y*256. For x neighbor: x' = x+face.n[0]. For z neighbor: z'=z+face.n[2]. Good.

### Let me also reconsider: the mesh should be added to chunkMeshes array for raycasting, and scene.

In rebuildChunk:
```javascript
function rebuildChunk(cx, cz) {
  const c = chunks.get(chunkKey(cx, cz));
  if (!c) return;
  if (c.mesh) {
    scene.remove(c.mesh);
    const i = chunkMeshes.indexOf(c.mesh);
    if (i>=0) chunkMeshes.splice(i,1);
    c.mesh.geometry.dispose();
    c.mesh = null;
  }
  c.mesh = buildChunkMesh(cx, cz);
  if (c.mesh) {
    scene.add(c.mesh);
    chunkMeshes.push(c.mesh);
  }
}
```

### Cleanup in updateChunks: iterate chunks, delete far ones.

```javascript
// collect keys to delete
const toDelete = [];
for (const [key, c] of chunks) {
  const [cx, cz] = key.split(',').map(Number);
  if (Math.abs(cx-playerCX) > 7 || Math.abs(cz-playerCZ) > 7) {
    toDelete.push(key);
  }
}
for (const key of toDelete) {
  const c = chunks.get(key);
  if (c && c.mesh) {
    scene.remove(c.mesh);
    const i = chunkMeshes.indexOf(c.mesh);
    if (i>=0) chunkMeshes.splice(i,1);
    c.mesh.geometry.dispose();
  }
  chunks.delete(key);
}
```

### Let me write the full HTML now.

Let me also handle the pointer lock and overlay carefully.

Start overlay click → request pointer lock. But requestPointerLock must be called from a user activation (click). The overlay is on top; clicking it triggers the click handler. Good.

However, there's a subtlety: the canvas also has mousedown handlers. When overlay is visible (display:flex covering canvas), clicks go to overlay, not canvas. Good.

After pointer lock, hide overlay. On pointerlockchange, if not locked, show overlay.

Let me also ensure the canvas captures clicks for break/place only when locked.

Let me write the CSS for overlay to cover the screen with a click target.

Let me also make sure clicking the canvas (when overlay hidden) requests lock if not locked. Actually, standard pattern: click anywhere to lock. Let me add a document mousedown that requests lock if not locked and overlay visible. But simpler: overlay click requests lock. Since overlay covers screen, clicking anywhere (on overlay) locks. Once locked, overlay hidden, and canvas clicks do break/place. Good.

But if pointer lock is lost mid-game (e.g., Esc), overlay reappears. Clicking overlay re-locks. Good.

Let me also handle the case where the user clicks the canvas directly (not overlay) when not locked—should request lock. Let me add: canvas mousedown → if not locked, request lock. But then break wouldn't happen. Hmm. Standard Minecraft: click to lock. Let me make canvas mousedown request lock if not locked, else process click. But the overlay covers the canvas when shown, so canvas mousedown won't fire until overlay hidden. So: overlay click → lock. That's the path. I'll rely on that. But to be safe, also handle document click when overlay visible → lock.

Let me just do overlay click → lock, and pointerlockchange → toggle overlay visibility.

Actually, one more: some browsers require the pointer lock request on a click that's a "trusted" event. Overlay click is trusted. Good.

Let me write it.

### Hotbar UI

HTML:
```html
<div id="hotbar">
  <div class="slot" data-i="0">...</div>
  ...
</div>
```
I'll generate slots in JS or hardcode. Let me generate in JS.

Each slot: a colored square with number. Selected slot gets white border.

```javascript
const hotbarBlocks = [1,2,3,4,5,6,7];
const hotbarEl = document.getElementById('hotbar');
hotbarBlocks.forEach((id, i) => {
  const slot = document.createElement('div');
  slot.className = 'slot';
  slot.dataset.i = i;
  const color = '#' + BLOCK_HEX[id].toString(16).padStart(6,'0');
  slot.innerHTML = `<div class="swatch" style="background:${color}"></div><span class="num">${i+1}</span>`;
  hotbarEl.appendChild(slot);
});
```

updateHotbarUI:
```javascript
function updateHotbarUI() {
  document.querySelectorAll('.slot').forEach(s => {
    s.classList.toggle('selected', parseInt(s.dataset.i)===selectedSlot);
  });
}
```

CSS for slots: flex row, each slot fixed size, swatch fills, number in corner, border when selected.

### Let me finalize BLOCK_HEX:
```javascript
const BLOCK_HEX = {
  1: 0x4caf50, 2: 0x795548, 3: 0x9e9e9e, 4: 0xe7d9a8,
  5: 0x8d6e63, 6: 0x2e7d32, 7: 0xffffff,
};
const BLOCK_COLORS = {};
for (const id in BLOCK_HEX) {
  const hex = BLOCK_HEX[id];
  BLOCK_COLORS[id] = [((hex>>16)&255)/255, ((hex>>8)&255)/255, (hex&255)/255];
}
```

Constants:
```javascript
const AIR=0, GRASS=1, DIRT=2, STONE=3, SAND=4, WOOD=5, LEAVES=6, SNOW=7;
```

### Let me write the complete file.

Let me be careful with the animation loop and dt clamping.

Also, I realize the clouds wrapping: I'll update cloud positions relative to player. Let me store cloud world positions and wrap when too far from player.

```javascript
function updateClouds(dt) {
  const spd = 3; // units/sec
  for (const c of clouds) {
    c.position.x += spd * dt;
    const relX = c.position.x - player.pos.x;
    if (relX > 130) c.position.x -= 260;
    else if (relX < -130) c.position.x += 260;
  }
}
```

Clouds at y=90. Player terrain up to ~73, clouds at 90 above. Good.

### Water re-center:
```javascript
water.position.x = player.pos.x;
water.position.z = player.pos.z;
```

### Let me also make sure camera far=400, fov=75.

```javascript
const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 400);
```

### Let me write everything now.

Let me reconsider the collision epsilon and the initial spawn to avoid spawning inside terrain. surfaceHeightAt finds top non-air block; player feet at that y + 1 (one block above surface) to be safe, or +0.5. Let me set feet at surfaceTop + 1.0 where surfaceTop is the y of the top block. Actually surfaceHeightAt returns y+1 (the empty space above top block). Let me define:

```javascript
function surfaceHeightAt(wx, wz) {
  for (let y=CHUNK_HEIGHT-1; y>=0; y--) {
    if (readBlock(wx,y,wz)!==AIR) return y+1; // top of block, player feet here
  }
  return 40;
}
```
Player feet at y+1 (just above the top block's surface at y+1... wait top block at y occupies [y,y+1], surface at y+1. Feet at y+1 rests on surface. But I return y+1 as the feet position. Feet at y+1, box [y+1, y+2.8]. Block at y [y,y+1] doesn't overlap box (touch at y+1). With epsilon, box [y+1-e, ...] overlaps block [y,y+1] at [y+1-e,y+1]. So collides → snaps to ceil(y+1-e)=y+1. Stays. Good. Actually the player spawns at y+1 which is resting on the block. Fine. But to be safe from spawning inside, maybe y+1.5. But then they'd fall 0.5 and land. Either works. Let me use surfaceHeightAt+1 for a small drop. Actually let me just use the returned value (feet on surface). Simpler. But if there's a tree above... unlikely at spawn. Let me add a few blocks of clearance: return y+2 to spawn clearly above. Hmm, but then collision immediately snaps down. Let me do surfaceHeightAt + 1.0. Fine.

Wait, actually there might be trees at (8,8). If a tree grew there, surfaceHeightAt returns the top block y+1, but the tree trunk extends up. Player at y+1 might be inside trunk. Unlikely at exactly (8,8) but possible. Let me spawn and then if colliding, push up. Or just spawn higher. Let me spawn at surfaceHeightAt+2 and let gravity settle. Actually simplest: after setting spawn, if collides, increment y until not colliding (up to some limit).

```javascript
function findSpawnY() {
  let y = surfaceHeightAt(8,8) + 1;
  let guard = 0;
  while (collides(8, y, 8) && guard < 30) { y++; guard++; }
  return y;
}
```

Good.

### Let me also double-check: player spawn chunk (0,0) and neighbors must be generated before findSpawnY. initWorld generates them. Good.

### One more: the raycaster dir. camera.getWorldDirection requires camera.matrixWorldUpdated. Since I update camera position and rotation each frame before raycasting, and I call camera.updateMatrixWorld() implicitly via render, but for raycasting I should update. Let me call camera.updateMatrixWorld() before raycasting, or use camera.rotation directly to compute dir.

Actually, getWorldDirection uses camera.matrixWorld. If I set position and rotation but haven't updated matrixWorld, getWorldDirection may be stale. Let me call camera.updateMatrixWorld() each frame before raycast. Or compute dir from pitch/yaw manually:

```javascript
const dir = new THREE.Vector3();
dir.x = -Math.sin(player.yaw) * Math.cos(player.pitch);
dir.y = Math.sin(player.pitch);
dir.z = -Math.cos(player.yaw) * Math.cos(player.pitch);
```

Wait let me derive. With rotation order YXZ and rotation.set(pitch, yaw, 0):
Forward vector (what camera looks at). Default forward (0,0,-1).

Rotation Ry(yaw) then Rx(pitch). Applied to (0,0,-1):
Ry(yaw)*(0,0,-1) = (-sin(yaw)*(-1)... let me recompute. Ry(yaw) matrix:
[[cosθ, 0, sinθ],
 [0,1,0],
 [-sinθ,0,cosθ]]
Times (0,0,-1)^T:
row0: cos*0+0*0+sin*(-1) = -sinθ
row1: 0
row2: -sin*0+0+cos*(-1) = -cosθ
So after Ry: (-sinθ, 0, -cosθ).

Then Rx(pitch):
[[1,0,0],
 [0,cosφ,-sinφ],
 [0,sinφ,cosφ]]
Times (-sinθ, 0, -cosθ):
row0: -sinθ
row1: 0*cosφ - (-cosθ)*sinφ = cosθ*sinφ
row2: 0*sinφ + (-cosθ)*cosφ = -cosθ*cosφ
So forward = (-sinθ, cosθ*sinφ, -cosθ*cosφ).

So:
dir.x = -sin(yaw)
dir.y = cos(yaw)*sin(pitch)
dir.z = -cos(yaw)*cos(pitch)

Let me verify yaw=0,pitch=0: (0,0,-1). Correct (looking -Z).
yaw=0, pitch=π/2 (looking up): (0, 1*1, 0) = (0,1,0). Looking up. Correct.
yaw=π/2 (look right/-X? ): (-1, 0, 0). Looking -X. Hmm, yaw=90° should look toward... with my forward formula, yaw=π/2 → dir=(-1,0,0) = -X. Earlier I said facing north(-Z) at yaw=0, and right(+X) at D press. At yaw=π/2, looking -X. Is -X "right"? If I rotate 90° clockwise (from above), I'd face... starting facing -Z(north), rotating... depends on sign. Whatever, it's consistent as long as movement matches. Since movement uses same yaw convention, it's consistent. Good.

Let me use manual dir computation to avoid matrix issues.

Actually, camera.rotation.set(pitch, yaw, 0) with order YXZ. Let me just use getWorldDirection after updateMatrixWorld to be safe and consistent with what the camera sees. I'll call camera.updateMatrixWorld() each frame. Then getWorldDirection works.

Let me do:
```javascript
camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
camera.rotation.set(player.pitch, player.yaw, 0);
camera.updateMatrixWorld();
```
Then raycaster dir = camera.getWorldDirection(new THREE.Vector3()).

Good.

### Let me also make sure pointer sensitivity and pitch clamping.

```javascript
player.yaw -= e.movementX * 0.002;
player.pitch -= e.movementY * 0.002;
player.pitch = Math.max(-1.56, Math.min(1.56, player.pitch)); // ~pi/2
```
Use 1.56 to avoid flipping at exactly π/2.

### Let me write the final code.

Let me also add the water and make sure it doesn't break raycasting (not in chunkMeshes).

Also, I should set renderer to handle alpha false, and pixel ratio.

Let me also prevent the page from scrolling with arrow keys etc. Not necessary.

Let me write it all out.

Actually, let me reconsider the mesh at origin issue once more. If I keep mesh at origin (position 0,0,0) and use world-space vertices, then when multiple chunks exist, all their meshes are at origin in the scene graph but occupy different world regions via vertices. Raycasting: intersectObjects transforms each object's geometry by its matrixWorld (identity at origin) → world coords = vertex coords. Correct.

But the outline box: I position it at block center in world coords. Since scene is standard, that's fine.

Water at player position, clouds at player-relative. All world coords. Good.

Let me also double check: the block material uses vertexColors: true. With normals attribute set, MeshLambertMaterial uses normals for lighting. Good.

Let me also make sure I set geo.computeVertexNormals? No, I provide explicit normals. Don't recompute.

Alright, writing the file.

Let me reconsider one thing about the meshing neighbor check for Y neighbors always being same chunk. The chunk is 80 tall (y 0..79). A block at y=79 with +Y face → neighbor y=80, out of chunk. But there's no block above y=79 (chunk only goes to 79). readBlock(80) returns air (y outside 0-79). But in my optimized meshing, for Y neighbor I do `data[x + z*16 + (y+face.n[1])*256]`. At y=79, y+1=80, index = x+z*16+80*256 which is out of bounds for the array (size 80*256=20480, max index 20479 for y=79). Index for y=80 = x+z*16+20480 → out of bounds → undefined. undefined===AIR is false! So it'd add a face (treating undefined as air) — actually that's what we want (air above). But accessing out of bounds gives undefined, and `undefined===AIR`(0) is false, so we'd add the face. Wait, that's the opposite: if nid===AIR add face. undefined===0 is false, so we DON'T add face. That's wrong—there's air above, should add face.

But blocks at y=79: are there any? Terrain max H~73, so y up to 73. Blocks only up to y=72 (surface at H-1? wait). Let me check: surface block placed at y=H (setLocal(x,H,...)). H up to 73. So blocks up to y=73. At y=73, +Y neighbor y=74, index = x+z*16+74*256 < 20480 (74*256=18944 < 20480). In bounds. data[...] = 0 (air, since not filled). So nid=0=AIR, add face. Good.

So the top of terrain is well below 79, no out-of-bounds. Max y with block is ~73, +Y → 74, in bounds, air. Good. No issue.

But to be safe, let me clamp: for Y neighbor, if y+face.n[1] is 80 or -1, treat as air. Actually since terrain never reaches y=79, it's fine. But defensively, let me guard. Actually the fill loop only goes y<H (H<=73), so data beyond H is 0 (air) and in bounds. The meshing loops y from 0 to 79, but blocks only exist up to ~73. For y where data is AIR, we skip (continue). So we never process blocks at y=74-79. And for blocks at y=73, +Y neighbor y=74 in bounds. Good. No out of bounds. 

Let me also make sure the meshing loop `for y<CHUNK_HEIGHT` with data access at y+1 for the topmost possible block (73) → 74, in bounds. Good.

Now, let me also verify the -Y neighbor for y=0: block at y=0 is stone (unbreakable floor). -Y neighbor y=-1. In my meshing, y neighbor: data[x+z*16+(y-1)*256]. At y=0, y-1=-1, index = x+z*16-256 → negative → undefined. undefined===0 false → don't add face. That's correct (no face below floor since it's the bottom; but actually there IS nothing below, should we show the bottom face? The floor at y=0 has air below (nothing). But it's the unbreakable bottom. Showing or not showing the bottom face doesn't matter visually since it's at y=0 and player is above. But to be correct, air below → show bottom face. However undefined causes us to not show it. Minor visual difference (invisible underside at y=0, which is fine since ground). Actually it doesn't matter because below y=0 is void and we never look from there. Let me guard -Y to treat as air for correctness:

Actually, let me just make the Y-neighbor access safe by clamping. For y neighbor ny=y+face.n[1]:
- if ny<0 or ny>=80: nid=AIR (air)
- else: nid=data[...]

Let me add that guard for Y neighbors. For x/z neighbors I already use readBlock which guards. Let me write:

```javascript
} else {
  // y neighbor
  const ny = y + face.n[1];
  nid = (ny<0||ny>=80) ? AIR : data[x + z*16 + ny*256];
}
```

Good.

Also for the floor at y=0, showing the bottom face (air below) is technically correct. Fine.

### Let me also reconsider: should the bottom face of the world (y=0) be shown? It's stone at y=0. Below is air (void). So bottom face shows. That's a flat stone underside at y=0, invisible from above. Fine.

### Alright, writing final code.

Let me also add: when breaking block at y=0, spec says "not at y 0". So break ignores y=0. Good, my click handler checks t.target.y !== 0.

Place: check cell is air and doesn't overlap player. Good.

### Let me also handle the case where raycast returns a hit but the target/block is fine.

### Double-check the outline uses EdgesGeometry for clean lines.

Let me write it.

Also, I want to make sure the game is performant: building geometry with Float32BufferAttribute from arrays. For a chunk, faces count: terrain has many exposed faces. Could be ~10k-30k faces per chunk → positions array ~ 30k*4*6 floats. Building arrays each mesh is fine.

Let me also dispose old geometries properly (done in rebuildChunk).

### Final assembly. Let me write the complete HTML file.

Let me write clean, well-organized JS.

I'll structure:
1. HTML head with CSS
2. Canvas, overlay, hotbar, crosshair elements
3. Script: constants, noise, chunk ops, generation, meshing, scene setup, player, controls, loop.

Let me write.

For CSS, crosshair: two divs forming a plus at center.

```css
#crosshair { position: fixed; top:50%; left:50%; transform:translate(-50%,-50%); width:20px; height:20px; pointer-events:none; }
#crosshair::before, #crosshair::after { content:''; position:absolute; background:white; box-shadow:0 0 2px black; }
#crosshair::before { left:50%; top:0; width:2px; height:100%; transform:translateX(-50%); }
#crosshair::after { top:50%; left:0; height:2px; width:100%; transform:translateY(-50%); }
```

Overlay:
```css
#overlay { position:fixed; inset:0; background:rgba(0,0,0,0.7); display:flex; align-items:center; justify-content:center; color:white; font-family:sans-serif; z-index:10; }
.overlay-content { text-align:center; max-width:480px; }
.overlay-content h1 { font-size:60px; margin:0 0 10px; letter-spacing:4px; }
.overlay-content ul { text-align:left; display:inline-block; line-height:1.8; }
.play { font-size:22px; margin-top:16px; animation: pulse 1.5s infinite; }
```

Hotbar:
```css
#hotbar { position:fixed; bottom:20px; left:50%; transform:translateX(-50%); display:flex; gap:4px; padding:4px; background:rgba(0,0,0,0.5); border-radius:4px; z-index:5; }
.slot { width:48px; height:48px; border:3px solid rgba(255,255,255,0.3); position:relative; border-radius:3px; }
.slot.selected { border-color:white; }
.swatch { position:absolute; inset:3px; border-radius:2px; }
.num { position:absolute; bottom:1px; right:2px; color:white; font-size:12px; font-family:sans-serif; text-shadow:1px 1px 0 black; }
```

Body margin 0, overflow hidden, canvas fullscreen.

```css
body { margin:0; overflow:hidden; }
canvas { display:block; }
```

Let me finalize.

I need to make sure BLOCK_HEX and BLOCK_COLORS are defined before use in hotbar generation and meshing.

Let me write the whole thing now.

One more consideration: the water plane renders with transparency. To avoid it rendering in front of everything (making the world look blue), I could render it behind. But standard transparent sorting in three.js renders transparent objects in order of depth after opaque. Since water is a large plane at y=14.3 spanning 500 units, parts of it are closer than terrain. Depth testing with alpha: three.js sorts transparent objects by distance from camera. Water fragments farther render first. This generally looks OK. Some terrain might appear through water where water is behind terrain—but water is a flat plane, terrain above it is opaque and rendered first (opaque pass), so terrain shows, water shows only where no terrain above. Should be fine.

Actually, there's a subtlety: water at y=14.3, and terrain like mountains at y=50. The water plane extends up to y=14.3 only (it's horizontal). So water only visible at the lake/beach levels. Above that, no water. Good.

But the water plane is 500 wide; at the horizon it's far. Fog fades it. Good.

Let me set water opacity ~0.6 and color blue 0x2b7fff or lighter. Let me use 0x3fa3ff.

Let me write the code.

Also, I should double check: requestPointerLock on overlay click. The overlay has pointer-events. When clicked, handler runs. Good.

Let me also make sure that after locking, subsequent mousedown on canvas (pointer locked) triggers break/place. The canvas mousedown listener checks pointerLockElement===canvas. Good.

Also prevent default on mousedown to avoid text selection. And contextmenu preventDefault.

Let me write final.

Actually, I realize when pointer is locked, mouse events like mousedown still fire on document/canvas. The canvas mousedown with button 0/2. Good.

Let me also add wheel handler for hotbar (with pointer lock check). And keydown for 1-7.

Let me now also reconsider: the spec says "Select with keys 1–7 or the mouse wheel (wraps around)." I'll implement both.

Let me write the complete file now. I'll be thorough.

Let me reconsider the updateChunks ordering relative to spawn and initial frames. On first frame, playerCX=0, playerCZ=0 (spawn at 8,8). updateChunks generates chunks within 5 (budget 4). It won't generate all needed for meshing immediately, but over several frames it converges. Meshing builds chunks within 4 whose 4 neighbors have data. So it takes a few frames to populate. That's fine—the world loads progressively. But the player spawns and might see empty area briefly then blocks appear. Acceptable.

But for spawn height, initWorld pre-generates chunks around (0,0) so spawn works. Good.

Let me make sure initWorld generates enough. I'll generate a 5x5 (dx,dz from -2..2) around spawn. That covers player chunk and neighbors for reasonable spawn. Good.

Now, one concern: generateChunk for a chunk reads/writes only its own data; trees placed within chunk bounds. Neighboring chunks generate their own trees. Fine.

Let me write.

Also, I want to double-check the fractal noise gives smooth terrain (no cliffs). With octaves scaling 0.004 and 0.02, smooth. Good.

Let me also make sure noise2 handles negative fractional parts correctly: Math.floor(-0.5) = -1. hash2(-1, ...) works (integers). Good.

Alright, writing final code.

Let me also reconsider performance of the main loop's updateChunks doing Map iteration for cleanup every frame. With ~169 chunks (11x11) in range, iteration is cheap. Good.

Let me write.

Also need to import three.js from the CDN. Single script tag.

Let me write the full HTML.

Actually, let me reconsider the raycaster and whether intersectObjects works with many meshes. It iterates all chunkMeshes (could be ~169). Each tests ray vs geometry. That's 169 ray-triangle tests on large geometries. Three.js optimizes with bounding sphere. Should be fast enough (<1ms). Fine.

Let me also make raycaster filter: only test meshes within range. But 169 is fine.

Let me finalize.

Let me write the code carefully, section by section, ensuring no syntax errors.

I'll now compose the entire file.

For the outline, I'll use a BoxHelper-like manual approach with EdgesGeometry of a slightly oversized box.

Let me write.

Also, I should set camera near to 0.1 to avoid z-fighting near. Good.

Let me write the final answer.

Let me reconsider the "keep the mesh at the origin" instruction. I'll set mesh.position.set(0,0,0) explicitly and use world coordinates in vertices. Done.

Let me also verify: when I add meshes at origin to scene and also add water/clouds at various positions, raycasting only against chunkMeshes (not water/clouds). Good.

Writing now.

Let me make sure about THREE.LineBasicMaterial and EdgesGeometry availability in r128. Yes.

Also THREE.Float32BufferAttribute exists in r128. Yes.

Let me write.

Final code:

I'll include a small loading note? No, just start.

Let me write the complete thing.

Actually, let me reconsider the collision for X and Z axes: I move and check collision, reverting on collision. But I should also handle the case where after moving X, moving Z might still collide due to the new X position—handled by checking after each axis. Good.

Also, for horizontal collision, when colliding I set velocity component to 0 and revert. Good.

Let me also make sure the player can walk up steps (1-block height). With axis-separated collision and gravity, walking into a 1-block step: horizontal move tries to enter the block's space, collides, reverts horizontal → player stuck at the step. Then gravity keeps them on the lower ground. They can't climb the 1-block step by walking! This is a known voxel game limitation unless we allow "step up". The spec doesn't mention step-up, so I'll leave it. Players can jump up. Fine.

Actually, this might make navigation annoying but it's per spec (axis-separated collision, revert on overlap). OK.

Let me finalize.

Let me write the file now. I'll be complete.

Let me reconsider: do I need to handle the case where readBlock is called during meshing for neighbor chunks that don't exist yet? readBlock returns air for missing chunks. Good, that's handled.

Also, generation: generateChunk doesn't read neighbors, just fills. Good.

Let me write.

I think I've thought through everything. Let me write the complete HTML file.

Let me make the code clean and complete.

For clouds, let me compute sizes deterministically and positions wrapping.

Let me write updateClouds to also reposition if player moves far (wrap). Done above.

Let me write the final code.

Actually, for the water, let me make it render only where needed but a big plane is simplest. I'll use PlaneGeometry(600,600). Rotate -90° about X to be horizontal. position.y=14.3. Recenter each frame.

Let me write.

Also, I realize I should double check: the directional light. If I don't update its target, it shines toward world origin (0,0,0) from its position. With position far (player+80,150,player+80), rays point toward origin, roughly toward player. Ambient 0.65 ensures base illumination. The directional adds 0.8 on lit faces. Faces pointing away from light get only ambient (0.65). That's fine, no pure black. Good.

Actually, MeshLambertMaterial with a single directional light: diffuse = max(0, dot(normal, lightDir)) * lightIntensity. Back faces get 0 diffuse, only ambient 0.65. So back faces are lit at 0.65, not dark. Good, no black faces.

Let me finalize.

Let me write it all out now.

I'll write the JS in a single script.

Let me make sure to reference elements that exist in DOM.

Structure:
- canvas#game
- div#overlay (with content)
- div#crosshair
- div#hotbar
- script (three.js CDN)
- script (game)

Let me write.

Double-check: requestPointerLock is on the canvas element. canvas.requestPointerLock(). Good.

Let me write the pointer lock change handler to show/hide overlay.

Also, initial overlay visible.

Let me write.

Now writing the full code.

I'll also add a subtle detail: prevent right-click context menu globally.

Let me write.

Let me reconsider the hotbar number display and colors. Good.

Writing final.

Let me make sure the game starts the animation loop and initWorld is called before first animate.

```javascript
initWorld();
animate();
```

initWorld generates spawn chunks and sets player pos.

Let me write.

Also, I want to ensure that when the player first loads, chunks mesh progressively. Since I pre-generate 5x5 chunks around spawn, meshing will build them over a few frames (need neighbors for border chunks). The central chunks mesh quickly. Good.

Let me write the complete file now.

Let me reconsider: in updateChunks, generation budget 4, mesh budget 2. Let me make the loops iterate dx,dz from -5..5 for gen and -4..4 for mesh, respecting budgets. Order: I'll iterate in a way that prioritizes nearby chunks (smaller radius first) for better UX. But with budget limits, processing by radius helps. Let me sort by distance or iterate radius layers. Simple: iterate dx,dz but break budget. To prioritize near, iterate in rings. Let me just iterate dx from -R..R, dz from -R..R; near chunks (small |dx|,|dz|) come first in iteration order (dx=0,dz=0 first). Actually dx=-5..5, dx=0 is in the middle. The loop starts dx=-5. So far chunks processed first. To prioritize near, let me iterate by increasing max(|dx|,|dz|). Let me do nested over radius:

```javascript
for (let r=0; r<=5 && genBudget>0; r++){
  for (let dx=-r; dx<=r && genBudget>0; dx++){
    for (let dz=-r; dz<=r && genBudget>0; dz++){
      ...
    }
  }
}
```

This processes radius 0 first (player chunk), then radius 1, etc. Good for progressive loading. Similarly for mesh.

Let me use that.

Now writing.

Let me also make sure generateChunk is only called if chunk not exists.

Final code below.

Let me write it out fully and carefully.

I'll also add comments for clarity (optional but helpful).

Let me write.

Also, for the water, I want it semi-transparent. MeshLambertMaterial transparent:true, opacity:0.6, side:DoubleSide. But DoubleSide with fog and depth might cause issues. Let me use SingleSide (top side up). Actually water surface normal points up; SingleSide with normal up shows from above. Camera looks down at water sometimes. Let me use DoubleSide to be safe. Or FrontSide. Let me use DoubleSide.

Hmm, DoubleSide transparent can render both sides causing artifacts. For a water plane viewed from above, FrontSide (normal up) is best. Let me use FrontSide. Camera above water looking down sees it. If camera is below (can't happen, player above water mostly). FrontSide fine.

Actually, let me use DoubleSide to avoid invisible water if player looks from odd angles. Minor. I'll use DoubleSide.

Let me finalize.

Let me write the code.

I need to be careful: THREE.PlaneGeometry default normal is +Y (folds toward +Z). Rotating -90° about X makes it horizontal with normal +Y. FrontSide shows +Y side (up). Good.

Writing now.

Let me also verify the cloud boxes: BoxGeometry(w,2,d). Transparent white. At y=90. Drift in X. Wrap. Good.

Final code:

I'll write it all.

Let me reconsider the total length. It'll be long but that's expected.

Let me write.

def writing...