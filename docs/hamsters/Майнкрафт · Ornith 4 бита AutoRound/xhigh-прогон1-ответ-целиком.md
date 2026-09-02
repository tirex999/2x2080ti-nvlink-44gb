Let me carefully build this Minecraft clone in a single HTML file. Let me go through the spec methodically.

The spec is very detailed. Let me implement each part:

1. **HTML/CSS structure**: Fullscreen canvas, start overlay, crosshair, hotbar.

2. **Three.js setup**: PerspectiveCamera, renderer, lights, sky color, fog.

3. **Block system**: IDs 0-7 with colors.

4. **Chunk system**: 16x16x80 chunks stored in a Map. Block read/write helpers.

5. **Meshing**: One BufferGeometry per chunk with face culling.

6. **Terrain generation**: Value noise, fractal noise, column heights, fill, caves, trees.

7. **Player physics**: Camera, gravity, jumping, movement, collision.

8. **Break/place**: Raycasting, outline, editing.

9. **Hotbar**: 7 slots.

10. **Sky, clouds, water**.

Let me write this carefully.

### Noise functions

I need a deterministic hash function for integer coordinates giving 0-1.

```js
function hash2(x, z) {
  // integer hash -> 0..1
  let h = x * 374761393 + z * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
```

Wait, I should make sure this gives good distribution. Let me use a standard approach. Actually let me combine x and z into a single 64-bit-ish value. Since JS numbers are doubles, integer operations up to 2^53 are safe. But multiplying two ~2^31 numbers gives ~2^62 which loses precision. Let me be careful.

Actually, for a hash, I can do:

```js
function hash2(x, z) {
  let h = (x | 0) * 374761393 + (z | 0) * 668265263 + 1013904223;
  h = (h ^ (h >> 16)) * 0x45d9f3b; // hmm
  ...
}
```

Let me use a well-known integer hash. The key issue is precision. Let me split:

```js
function hash2(x, z) {
  // Combine into a 64-bit-ish hash using modular arithmetic
  let h = (x | 0) * 374761393 + (z | 0) * 668265263 + 1013904223;
  // xor-shift scramble
  h ^= h >> 16;
  h = (h * 0x7bed5fff) >>> 0; // careful with overflow
  ...
}
```

Hmm, `>>> 0` converts to unsigned 32-bit, truncating. That's fine for hashing but we lose info. Let me instead do a proper scramble keeping more bits.

Actually the cleanest: use a pair of multiplications and take modulo.

Let me define:

```js
function hash2(x, z) {
  let v = (x | 0) * 73856093 ^ (z | 0) * 19349663;
  // now v is a signed 32-bit int (since multiplication of two ints mod 2^32 in JS via ^ operator... actually * doesn't truncate to 32 bits)
}
```

In JS, `*` produces a float, and for integers up to 2^53 it's exact. `(x|0)` is in [-2^31, 2^31-1]. Product of two such is up to ~2^62, which exceeds 2^53, losing precision. So I should mask to 32 bits first.

Let me do:

```js
function hash2(x, z) {
  let hx = (x | 0) % 4294967296;
  let hz = (z | 0) % 4294967296;
  let h = ((hx * 374761393) % 4294967296 + (hz * 668265263) % 4294967296 + 1013904223) % 4294967296;
  h = (h ^ (h >> 16)) * 1274126177 % 4294967296;
  h = (h ^ (h >> 13)) * 3266489917 % 4294967296;
  h = h ^ (h >> 16);
  return h / 4294967296;
}
```

This keeps everything within 32-bit range using `% 4294967296`. Products of two 32-bit numbers can be up to ~2^64 which loses precision beyond 2^53. Hmm.

`(hx * 374761393)` where hx < 2^32 and 374761393 < 2^30, product < 2^62. That's > 2^53, so precision loss. But since we immediately take `% 4294967296`, and the result only needs to be deterministic (not perfectly uniform), minor precision loss is acceptable for noise. Actually the concern is determinism — the operation is deterministic even if slightly imprecise. And uniformity — the low bits still vary. It's fine for a game.

Actually, to be safe and keep precision, I can reduce the multiplier size or use a different combination. But honestly for terrain noise this is totally fine. Let me just make it deterministic and reasonably distributed.

Let me simplify with a cleaner hash:

```js
function hash2(x, z) {
  let h = (x | 0) * 374761393 + (z | 0) * 668265263 + 1013904223;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
```

Here `h >>> 0` truncates to unsigned 32-bit at the end. The intermediate products lose precision but it's deterministic. Good enough. Actually wait — will `h >>> 0` at the end give a good distribution? The final value is a 32-bit truncation of a deterministic function. Fine.

But there's a subtlety: `(x|0) * 374761393` for large x could be huge and lose precision, but again deterministic. For our world coordinates (which are bounded by player proximity, within maybe a few hundred blocks), it's fine.

Let me also make a 3D hash for caves:

```js
function hash3(x, y, z) {
  let h = (x | 0) * 374761393 + (y | 0) * 668265263 + (z | 0) * 1013904223 + 12345;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
```

And a per-column hash for trees:

```js
function columnHash(x, z) {
  // reuse hash2
  return hash2(x, z);
}
```

### Noise interpolation

Smoothstep: `t*t*(3-2t)`.

Bilinear interpolation for 2D:

```js
function lerp(a, b, t) { return a + (b - a) * t; }

function smoothstep(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
  const xi = Math.floor(x), zi = Math.floor(z);
  const xf = x - xi, zf = z - zi;
  const u = smoothstep(xf), v = smoothstep(zf);
  const a = hash2(xi, zi);
  const b = hash2(xi + 1, zi);
  const c = hash2(xi, zi + 1);
  const d = hash2(xi + 1, zi + 1);
  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}
```

Fractal (octaves):

```js
function fractal2(x, z, octaves, persistence) {
  let total = 0, amplitude = 1, frequency = 1, maxAmplitude = 0;
  for (let i = 0; i < octaves; i++) {
    total += noise2(x * frequency, z * frequency) * amplitude;
    maxAmplitude += amplitude;
    amplitude *= persistence;
    frequency *= 2;
  }
  return total / maxAmplitude;
}
```

3D noise similar:

```js
function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = smoothstep(xf), v = smoothstep(yf), w = smoothstep(zf);
  // 8 corners
  const c000 = hash3(xi, yi, zi);
  const c100 = hash3(xi+1, yi, zi);
  const c010 = hash3(xi, yi+1, zi);
  const c110 = hash3(xi+1, yi+1, zi);
  const c001 = hash3(xi, yi, zi+1);
  const c101 = hash3(xi+1, yi, zi+1);
  const c011 = hash3(xi, yi+1, zi+1);
  const c111 = hash3(xi+1, yi+1, zi+1);
  const x00 = lerp(c000, c100, u);
  const x10 = lerp(c010, c110, u);
  const x01 = lerp(c001, c101, u);
  const x11 = lerp(c011, c111, u);
  const y0 = lerp(x00, x10, v);
  const y1 = lerp(x01, x11, v);
  return lerp(y0, y1, w);
}
```

### Terrain generation

Column height:
```js
m = fractal2(coords*0.004)  // large features
h = fractal2(coords*0.02)  // smaller features
H = floor(5 + m*m*58 + h*10)
```

Wait, m is 0-1, so m*m ranges 0-1, times 58 = 0-58. Plus h*10 = 0-10. Plus 5. So H ranges roughly 5 to 73. Good, within 0-79.

Column fill logic:
- y = 0: unbreakable stone (block 3)
- below H-3: stone
- the 3 layers under surface: dirt (sand if H ≤ 16, stone if H ≥ 37)
- surface: snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass

Let me think about the vertical structure. For a column at local x, z:

```
for y from 0 to H-1:
  if y == 0: block = stone (unbreakable)
  else if y < H - 3: block = stone
  else if y < H:  // the 3 layers under surface (y = H-3, H-2, H-1)
    if H <= 16: block = sand
    else if H >= 37: block = stone
    else: block = dirt
  else if y == H: // surface
    if H >= 46: block = snow
    else if H >= 37: block = stone
    else if H <= 16: block = sand
    else: block = grass
  else: // y > H, air (until water level maybe)
    air
```

Wait, but we need to handle water. Water is visual only (a plane), so terrain blocks above y=14 are solid, below are... well the terrain fills up to H. If H < 14, then there's empty space above filled blocks down to y=14 where water sits. Actually the water plane is at height 14.3, and terrain below that would be air (or filled with nothing). Since water is visual only, we just leave those cells as air and put a water plane.

Hmm, but should blocks below y=14 be filled? The spec says "water: one large semi-transparent blue plane... lakes and beaches appear automatically where terrain is lower". So terrain is generated normally regardless of water; wherever terrain surface is below ~14, there's air pocket that water covers visually. That's fine.

Actually, let me reconsider. Beaches with water: sand at H ≤ 16. So a column with H around 14 would have sand at surface, and air above it up to y=14 where water is. Good.

Let me define fill:

```js
function generateColumn(cx_local, cz_local, wx, wz) {
  const col = new Uint8Array(80); // default air
  const m = fractal2(wx * 0.004, wz * 0.004);
  const h = fractal2(wx * 0.02, wz * 0.02);
  const H = Math.floor(5 + m*m*58 + h*10);
  for (let y = 0; y < 80; y++) {
    if (y === 0) {
      col[y] = 3; // stone unbreakable
    } else if (y < H - 3) {
      col[y] = 3; // stone
    } else if (y < H) {
      // 3 layers under surface
      if (H <= 16) col[y] = 4; // sand
      else if (H >= 37) col[y] = 3; // stone
      else col[y] = 2; // dirt
    } else if (y === H) {
      // surface
      if (H >= 46) col[y] = 7; // snow
      else if (H >= 37) col[y] = 3; // stone
      else if (H <= 16) col[y] = 4; // sand
      else col[y] = 1; // grass
    } else {
      col[y] = 0; // air
    }
  }
  // caves
  for (let y = 3; y < H - 2; y++) {
    if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
      col[y] = 0;
    }
  }
  // trees
  if (col[H] === 1) { // grass surface
    if (columnHash(wx, wz) < 0.02 && fitsInChunk(...)) {
      // place tree
    }
  }
  return col;
}
```

Wait, the tree placement needs care. "Trees: on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

The tree is placed at the column's local x, z. "trunk fits inside the chunk" means the local x and z must be far enough from edges so the leaf canopy (5x5) fits. The 5x5 leaf layer centered at the column means it spans local x-2..x+2 and z-2..z+2. So we need local x in [2, 13] and local z in [2, 13] (0-indexed, 16 wide, indices 0-15; 5-wide centered means x-2>=0 and x+2<=15, so x in [2,13]).

Actually wait, "the trunk fits inside the chunk" — the trunk is 1 wide at the column, always fits. But the leaves are 5x5, so they need to fit. I'll interpret "trunk fits inside the chunk" as the whole tree fits, i.e., leaf canopy within bounds. Let me require local x in [2,13] and local z in [2,13].

Hmm, but actually the phrase specifically says "the trunk fits inside the chunk". Maybe it literally means just the trunk (single column) fits, which is always true. But then leaves could stick out of the chunk. That would cause gaps at chunk boundaries (leaves in neighbor chunk not generated... but neighbor chunk generation would also place a tree if its own hash matches). Actually leaves sticking into adjacent chunk would create a mismatch. To be safe, I'll require the full canopy to fit within the chunk: local x in [2, 13], local z in [2, 13]. This is the sensible interpretation and avoids boundary artifacts.

Let me place the tree:
- Trunk: 4 wood blocks at y = H+1, H+2, H+3, H+4.
- Leaves: 
  - "5x5 layer twice" at y = H+5 and H+6 (centered, so local dx, dz in [-2, 2])
  - "3x3" at y = H+7
  - "1 on top" at y = H+8

"only into air" — place leaf/wood blocks only if the target cell is currently air.

Let me code:

```js
if (col[H] === 1 && columnHash(wx, wz) < 0.02) {
  const lx = cx_local, lz = cz_local;
  if (lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13) {
    for (let y = H + 1; y <= H + 4; y++) {
      if (y < 80 && col[y] === 0) col[y] = 5; // wood
    }
    // 5x5 layers at H+5, H+6
    for (let dy = -2; dy <= 2; dy++) {
      for (let dz = -2; dz <= 2; dz++) {
        const ly = H + 5 + (dy >= 0 ? 1 : 0); // H+5 and H+6
        // Actually both layers at same y range? "5x5 layer twice" = two layers
        // layer1: y=H+5, layer2: y=H+6
      }
    }
  }
}
```

Let me be precise. Two 5x5 layers means at y = H+5 and y = H+6, each a 5x5 square centered on the trunk. Then a 3x3 at y = H+7, then 1 block at y = H+8.

```js
// trunk
for (let y = H + 1; y <= H + 4; y++) {
  if (y < 80 && col[y] === 0) col[y] = 5;
}
// two 5x5 leaf layers
for (let layer = 0; layer < 2; layer++) {
  const y = H + 5 + layer;
  if (y < 80) {
    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        if (y < 80 && col[y] === 0) col[y] = 6; // leaves
      }
    }
  }
}
// 3x3 layer
{
  const y = H + 7;
  if (y < 80) {
    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        if (y < 80 && col[y] === 0) col[y] = 6;
      }
    }
  }
}
// top
{
  const y = H + 8;
  if (y < 80 && col[y] === 0) col[y] = 6;
}
```

Good.

Now the chunk data storage. Spec: "Store them in a global Map (key "cx,cz", value: a Uint8Array of block IDs plus its mesh)." 

Hmm, storing both the array and mesh in the value. I could store an object `{ data: Uint8Array, mesh: Mesh|null }`. Or store the Uint8Array and keep meshes in a separate array. The spec says value is "a Uint8Array of block IDs plus its mesh". I'll store an object with both, or I could store the array keyed separately. Let me store an object to match the spec: value = { data, mesh }. Actually, re-reading: "value: a Uint8Array of block IDs plus its mesh". I'll make the value an object `{ data: Uint8Array, mesh: THREE.Mesh | null }`.

Wait, but then "Keep all chunk meshes in a global array for raycasting". So meshes are also in a global array. OK.

Let me define chunk coordinates:
```js
function chunkIndex(worldCoord) { return Math.floor(worldCoord / 16); }
function localCoord(worldCoord) { return worldCoord - chunkIndex(worldCoord) * 16; }
```

Global read:
```js
function getBlock(wx, wy, wz) {
  if (wy < 0 || wy > 79) return 0; // air
  const cx = chunkIndex(wx), cz = chunkIndex(wz);
  const key = cx + ',' + cz;
  const chunk = chunks.get(key);
  if (!chunk || !chunk.data) return 0;
  const lx = localCoord(wx), lz = localCoord(wz);
  return chunk.data[lx + lz * 16 + wy];
}
```

Global write:
```js
function setBlock(wx, wy, wz, id) {
  if (wy < 0 || wy > 79) {
    // if wy is out of range, ignore (can't set y=0 anyway for break; place ignores)
    return;
  }
  const cx = chunkIndex(wx), cz = chunkIndex(wz);
  const key = cx + ',' + cz;
  const chunk = chunks.get(key);
  if (!chunk || !chunk.data) return;
  const lx = localCoord(wx), lz = localCoord(wz);
  chunk.data[lx + lz * 16 + wy] = id;
}
```

### Chunk generation

For each chunk within 5 of player, generate block data. "generate block data for all chunks within 5 chunks of the player (max 4 per frame)".

So each frame, we compute which chunks are needed (within radius 5) and generate up to 4 per frame.

```js
let chunksToGenerate = 0;
const maxGenPerFrame = 4;
const pcx = chunkIndex(player.x), pcz = chunkIndex(player.z);
for (let dx = -5; dx <= 5; dx++) {
  for (let dz = -5; dz <= 5; dz++) {
    if (chunksToGenerate >= maxGenPerFrame) break; // hmm need to break outer too
    const cx = pcx + dx, cz = pcz + dz;
    const key = cx + ',' + cz;
    if (!chunks.has(key)) {
      generateChunkData(cx, cz);
      chunksToGenerate++;
    }
  }
}
```

Wait, breaking inner loop when reached limit but continue outer? Let me use a flag.

Actually simpler: iterate and break out of both loops when limit reached.

```js
let genCount = 0;
let done = false;
outer: for (let dx = -5; dx <= 5 && !done; dx++) {
  for (let dz = -5; dz <= 5; dz++) {
    const cx = pcx + dx, cz = pcz + dz;
    const key = cx + ',' + cz;
    if (!chunks.has(key)) {
      generateChunkData(cx, cz);
      genCount++;
      if (genCount >= 4) { done = true; break outer; }
    }
  }
}
```

generateChunkData:
```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(16 * 16 * 80);
  for (let lx = 0; lx < 16; lx++) {
    for (let lz = 0; lz < 16; lz++) {
      const wx = cx * 16 + lx;
      const wz = cz * 16 + lz;
      const m = fractal2(wx * 0.004, wz * 0.004);
      const h = fractal2(wx * 0.02, wz * 0.02);
      const H = Math.floor(5 + m * m * 58 + h * 10);
      for (let y = 0; y < 80; y++) {
        let id = 0;
        if (y === 0) id = 3;
        else if (y < H - 3) id = 3;
        else if (y < H) {
          if (H <= 16) id = 4;
          else if (H >= 37) id = 3;
          else id = 2;
        } else if (y === H) {
          if (H >= 46) id = 7;
          else if (H >= 37) id = 3;
          else if (H <= 16) id = 4;
          else id = 1;
        }
        data[lx + lz * 16 + y] = id;
      }
      // caves
      for (let y = 3; y < H - 2; y++) {
        if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
          data[lx + lz * 16 + y] = 0;
        }
      }
      // trees
      const surfId = data[lx + lz * 16 + H];
      if (surfId === 1 && columnHash(wx, wz) < 0.02 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13) {
        for (let y = H + 1; y <= H + 4; y++) {
          if (y < 80 && data[lx + lz * 16 + y] === 0) data[lx + lz * 16 + y] = 5;
        }
        for (let layer = 0; layer < 2; layer++) {
          const y = H + 5 + layer;
          if (y < 80) {
            for (let dx2 = -2; dx2 <= 2; dx2++) {
              for (let dz2 = -2; dz2 <= 2; dz2++) {
                if (y < 80 && data[lx + lz * 16 + y] === 0) data[lx + lz * 16 + y] = 6;
              }
            }
          }
        }
        {
          const y = H + 7;
          if (y < 80) {
            for (let dx2 = -1; dx2 <= 1; dx2++) {
              for (let dz2 = -1; dz2 <= 1; dz2++) {
                if (y < 80 && data[lx + lz * 16 + y] === 0) data[lx + lz * 16 + y] = 6;
              }
            }
          }
        }
        {
          const y = H + 8;
          if (y < 80 && data[lx + lz * 16 + y] === 0) data[lx + lz * 16 + y] = 6;
        }
      }
    }
  }
  chunks.set(cx + ',' + cz, { data: data, mesh: null });
}
```

### Meshing

For each chunk within 4 chunks whose 4 neighbors have data, build mesh. "build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame)".

The 4 neighbors: I think it means the 4 orthogonal neighbors (north, south, east, west) — or all 4 cardinal directions. Let me check the 4 immediate orthogonal neighbors (±x, ±z). Actually "whose 4 neighbors already have data" — probably the 4 orthogonal neighbors. But to be safe maybe all 8? The spec explicitly says 4, so orthogonal 4.

Wait, but if a chunk's mesh depends on neighbor data for face culling, we need neighbor data present. When we build a chunk's mesh, we call getBlock() which reads neighbor chunks' data. If neighbor data isn't generated yet, faces would incorrectly show (missing culling → holes). So we require the 4 neighbors to have data before meshing.

```js
let meshCount = 0;
let meshDone = false;
outer2: for (let dx = -4; dx <= 4 && !meshDone; dx++) {
  for (let dz = -4; dz <= 4; dz++) {
    const cx = pcx + dx, cz = pcz + dz;
    const key = cx + ',' + cz;
    const chunk = chunks.get(key);
    if (chunk && chunk.data && !chunk.mesh) {
      // check 4 neighbors have data
      const nE = chunks.get((cx+1)+','+cz);
      const nW = chunks.get((cx-1)+','+cz);
      const nN = chunks.get(cx+','+(cz+1));
      const nS = chunks.get(cx+','+(cz-1));
      if (nE && nE.data && nW && nW.data && nN && nN.data && nS && nS.data) {
        buildChunkMesh(cx, cz);
        meshCount++;
        if (meshCount >= 2) { meshDone = true; break outer2; }
      }
    }
  }
}
```

buildChunkMesh:
```js
function buildChunkMesh(cx, cz) {
  const key = cx + ',' + cz;
  const chunk = chunks.get(key);
  if (!chunk) return;
  // dispose existing mesh
  if (chunk.mesh) {
    scene.remove(chunk.mesh);
    chunk.mesh.geometry.dispose();
  }
  const data = chunk.data;
  const positions = [];
  const normals = [];
  const colors = [];
  const indices = [];
  const baseX = cx * 16, baseZ = cz * 16;
  const blockColors = {
    1: [0x4caf50, 0x4caf50...], // need RGB
    ...
  };
  for (let lx = 0; lx < 16; lx++) {
    for (let lz = 0; lz < 16; lz++) {
      for (let y = 0; y < 80; y++) {
        const id = data[lx + lz * 16 + y];
        if (id === 0) continue;
        const wx = baseX + lx, wz = baseZ + lz;
        const rgb = blockRGB[id];
        // check 6 faces
        // top (y+1)
        if (getBlock(wx, y+1, wz) === 0) {
          addFace(positions, normals, colors, indices, wx, y, wz, 'top', rgb);
        }
        ... etc
      }
    }
  }
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geom.setIndex(indices);
  const mesh = new THREE.Mesh(geom, sharedMaterial);
  mesh.position.set(0, 0, 0); // keep at origin; world coords in vertices
  scene.add(mesh);
  chunk.mesh = mesh;
  chunkMeshes.push(mesh);
}
```

Wait, the spec says "keep the mesh at the origin" and "Use world coordinates for vertices". So the mesh has no position offset; vertices use absolute world coords. Good.

addFace function: adds 4 vertices and 2 triangles for a given face at world position (wx, y, wz) with a color.

The 6 faces:
- top: normal (0,1,0), vertices at y+1
- bottom: normal (0,-1,0), vertices at y
- +x: normal (1,0,0)
- -x: normal (-1,0,0)
- +z: normal (0,0,1)
- -z: normal (0,0,-1)

Each face is a square with 4 vertices in CCW order when viewed from outside (for correct facing with Lambert/normal-based lighting — though Lambert uses normal dot light, winding matters for culling but we don't cull; still let's keep consistent).

Let me define face vertices. For a cube at (x,y,z):

Top face (y+1), viewed from above (+y):
```
(x, y+1, z), (x, y+1, z+1), (x+1, y+1, z+1), (x+1, y+1, z)
```
Triangles: (0,1,2), (0,2,3)

Bottom face (y), viewed from below:
```
(x, y, z+1), (x, y, z), (x+1, y, z), (x+1, y, z+1)
```

+x face:
```
(x+1, y, z), (x+1, y, z+1), (x+1, y+1, z+1), (x+1, y+1, z)
```

-x face:
```
(x, y, z+1), (x, y, z), (x, y+1, z), (x, y+1, z+1)
```

+z face:
```
(x+1, y, z+1), (x, y, z+1), (x, y+1, z+1), (x, y+1, z+1)
```

-z face:
```
(x, y, z), (x+1, y, z), (x+1, y+1, z), (x, y+1, z)
```

Let me write addFace with parameters for the 4 corner offsets based on face type. Actually cleaner to write each face inline. Let me write a helper that takes the base position and a set of 4 relative vertex offsets plus normal.

```js
function addFace(pos, norm, col, idx, x, y, z, face, rgb) {
  let verts;
  let nrm;
  switch (face) {
    case 'top':
      verts = [[0,1,0],[0,1,1],[1,1,1],[1,1,0]];
      nrm = [0,1,0];
      break;
    case 'bottom':
      verts = [[0,0,1],[0,0,0],[1,0,0],[1,0,1]];
      nrm = [0,-1,0];
      break;
    case 'right': // +x
      verts = [[1,0,0],[1,0,1],[1,1,1],[1,1,0]];
      nrm = [1,0,0];
      break;
    case 'left': // -x
      verts = [[0,0,1],[0,0,0],[0,1,0],[0,1,1]];
      nrm = [-1,0,0];
      break;
    case 'front': // +z
      verts = [[1,0,1],[0,0,1],[0,1,1],[1,1,1]];
      nrm = [0,0,1];
      break;
    case 'back': // -z
      verts = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]];
      nrm = [0,0,-1];
      break;
  }
  const i0 = pos.length / 3;
  for (const v of verts) {
    pos.push(x + v[0], y + v[1], z + v[2]);
    norm.push(nrm[0], nrm[1], nrm[2]);
    // lighting factor per face
    let f;
    if (face === 'top') f = 1.0;
    else if (face === 'bottom') f = 0.55;
    else f = 0.8;
    col.push(rgb[0]*f, rgb[1]*f, rgb[2]*f);
  }
  idx.push(i0, i0+1, i0+2, i0, i0+2, i0+3);
}
```

The lighting factor: top 1.0, sides 0.8, bottom 0.55. Good.

blockRGB:
```js
const blockRGB = {
  1: [0x4caf50, 0x4caf50], // grass (top is green; sides dirt? spec says single color per block, multiply by lighting)
  ...
};
```

Wait, the spec says "rendered with vertex colors" and "multiply the block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms". So each block has ONE color, and we multiply by lighting per face. So grass is uniformly 0x4caf50 (even sides). That's simpler — no special top color for grass. Good, the spec explicitly says one color per block. So:

```js
const blockRGB = {
  1: [0x4caf50>>16 & 255, 0x4caf50>>8 & 255, 0x4caf50 & 255],
  2: [0x795548...],
  3: [0x9e9e9e...],
  4: [0xe7d9a8...],
  5: [0x8d6e63...],
  6: [0x2e7d32...],
  7: [0xffffff...],
};
```

Let me write a helper to convert hex to RGB:
```js
function hexToRgb(hex) {
  return [(hex >> 16) & 255, (hex >> 8) & 255, hex & 255];
}
```

### Shared material

```js
const sharedMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

### Raycasting

"Keep all chunk meshes in a global array for raycasting." Use THREE.Raycaster.

```js
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
```

Each frame (when pointer locked), cast from center of screen:
```js
raycaster.set(camera.position, camera direction);
const hits = raycaster.intersectObjects(chunkMeshes, false);
```

Camera direction: from camera.getWorldDirection. Since camera rotation order YXZ, getWorldDirection gives forward.

From hit point p and face normal n:
- break target = floor(p - n*0.5)
- place cell = floor(p + n*0.5)

Outline the targeted block with a black wireframe box.

```js
if (hits.length > 0) {
  const hit = hits[0];
  const p = hit.point;
  const n = hit.face.normal; // in world space? For these axis-aligned meshes, face.normal is in object space = world space since mesh at origin.
  const target = [
    Math.floor(p.x - n.x * 0.5),
    Math.floor(p.y - n.y * 0.5),
    Math.floor(p.z - n.z * 0.5)
  ];
  const place = [
    Math.floor(p.x + n.x * 0.5),
    Math.floor(p.y + n.y * 0.5),
    Math.floor(p.z + n.z * 0.5)
  ];
  // update outline position
  outline.position.set(target[0]+0.5, target[1]+0.5, target[2]+0.5);
  outline.visible = true;
} else {
  outline.visible = false;
}
```

Note: face.normal from intersect is in the mesh's local coordinate system. Since mesh is at origin with no rotation, local = world. Good. But the normal components are 0, ±1. Floor of p.y - n.y*0.5: if n.y = 1 (hit top face), p.y is near the top of the block, p.y - 0.5 lands inside the block below? Let me think. If we hit the top face of a block at y, the hit point y is between y and y+1 (on the top surface). Actually the top surface is at world y = blockY + 1. The hit point is on that surface so p.y ≈ blockY+1 (within tolerance). Then floor(p.y - 0.5) = floor(blockY + 0.5) = blockY. Good, that's the block we hit.

If we hit the bottom face, n.y = -1, p.y ≈ blockY (bottom surface). floor(p.y + 0.5) = floor(blockY + 0.5) = blockY. And break target = floor(p.y - (-1)*0.5) = floor(p.y + 0.5) = blockY. Good.

For sides similar. Great.

The outline: a BoxGeometry(1.02,1.02,1.02) with WireframeGeometry or use EdgesGeometry. Let me use:
```js
const outlineGeo = new THREE.BoxGeometry(1.01, 1.01, 1.01);
const outline = new THREE.LineSegments(new THREE.WireframeGeometry(outlineGeo), new THREE.LineBasicMaterial({ color: 0x000000 }));
```

WireframeGeometry is deprecated in newer versions but exists in r128. In r128, THREE.WireframeGeometry exists. Alternatively use EdgesGeometry. Let me use EdgesGeometry which is cleaner:
```js
const outline = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.02, 1.02, 1.02)), new THREE.LineBasicMaterial({color: 0x000000}));
scene.add(outline);
outline.visible = false;
```

### Player physics

Camera perspective, fov 75, far 400, rotation order YXZ.

```js
const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 400);
camera.rotation.order = 'YXZ';
```

Player box: half-width 0.3, height 1.8, eye 1.62. So the camera eye is at player box top + (eye - ?). Let me think. The player box spans from y_bottom to y_bottom + 1.8. Eye at 1.62 from the bottom of the box? Typically eye height is measured from feet. So eye = 1.62 above feet. The box height is 1.8, so eyes are near the top.

Let me define player position as feet position (x, y, z) — the bottom center of the box. Camera y = feet.y + eye (1.62). Horizontal position = feet.x, feet.z.

Collision: box half-width 0.3 in x and z, height 1.8. So the box occupies [x-0.3, x+0.3] x [y, y+1.8] x [z-0.3, z+0.3].

Collision detection: for each axis, move and check if any block in the box volume is solid. If so, revert.

Let me store player velocity vy. Each frame:
- Apply gravity: vy -= 25 * dt (or per-frame). Actually gravity 25/s means acceleration. Let me do vy -= 25*dt.
- If on ground and space pressed, vy = 8.5.
- Move vertically first, then collide.

Movement: WASD relative to yaw. Forward vector = (sin(yaw), 0, cos(yaw))? Let me define yaw such that yaw=0 looks along +z. With rotation order YXZ, camera.rotateY(yaw) rotates around Y. The forward direction after rotateY(yaw) and rotateX(pitch): getWorldDirection.

Let me define input vectors:
```js
const forward = new THREE.Vector3(0, 0, 1);
forward.applyEuler(new THREE.Euler(0, yaw, 0)); // horizontal forward
```
Actually simpler: 
```js
const sinY = Math.sin(yaw), cosY = Math.cos(yaw);
const moveX = (keys.w ? -sinY : 0) + (keys.s ? sinY : 0); // hmm
```

Let me think about camera orientation. With rotation order 'YXZ' and we set camera.rotation.y = yaw. Initially (yaw=0, pitch=0), camera looks along +Z (three.js default camera looks along -Z!). Wait, THREE.PerspectiveCamera initially looks along -Z (negative z). So at yaw=0, looking -Z.

When we rotateY(yaw), it rotates around Z axis (world up). Let me just use getWorldDirection to get forward and compute movement from input.

Let me define:
```js
const dir = new THREE.Vector3();
camera.getWorldDirection(dir);
const forward = new THREE.Vector3(dir.x, 0, dir.z).normalize(); // horizontal component
const right = new THREE.Vector3(forward.z, 0, -forward.x); // perpendicular
```
Hmm, right = cross of up and forward. Let me compute: right = (forward.z, 0, -forward.x)? Let's verify: forward horizontal = (fx, fz). Right should be 90° clockwise when viewed from above. If forward = (0,0,1)... wait three.js looks -Z. Let me just derive.

Actually let me set it up clearly. Let yaw be the rotation. camera.rotation.y = yaw. getWorldDirection gives the forward (into screen) vector.

At yaw=0: forward = (0, 0, -1) (looking -Z).
At yaw=π/2: rotated 90° around Y. The +Z direction... rotateY(π/2) maps (0,0,-1) to? Rotation around Y by angle θ: x' = x cosθ + z sinθ, z' = -x sinθ + z cosθ. For vector (0,0,-1): x' = -sinθ, z' = -cosθ... wait let me redo. Standard rotation around Y:
```
[ cosθ  0  sinθ]
[ 0     1   0  ]
[-sinθ  0  cosθ]
```
Apply to (0,0,-1): x' = sinθ*(-1) = -sinθ, z' = cosθ*(-1) = -cosθ. At θ=π/2: x' = -1, z' = 0. So forward = (-1, 0, 0), i.e., looking -X. Hmm, that means rotating counterclockwise (positive yaw) turns to look -X. That's fine, it's just a convention.

For movement, I'll compute:
```js
const fwd = new THREE.Vector3();
camera.getWorldDirection(fwd);
fwd.y = 0; fwd.normalize();
const right = new THREE.Vector3(fwd.z, 0, -fwd.x); // normalize
```
Check: at yaw=0, fwd=(0,0,-1). right = (fwd.z, 0, -fwd.x) = (-1, 0, 0). Is that "right"? When looking -Z, your right hand points... if you face -Z (south, say), right is +X. But we got -X. So this "right" is actually left. Doesn't matter much as long as consistent with WASD. Let me define velocity:
```js
let vx = 0, vz = 0;
if (w) { vx += fwd.x; vz += fwd.z; }
if (s) { vx -= fwd.x; vz -= fwd.z; }
if (d) { vx += right.x; vz += right.z; }
if (a) { vx -= right.x; vz -= right.z; }
```
Normalize the resulting horizontal vector and multiply by speed 5.5.

Let me just compute and normalize.

Collision resolution per axis:

Let me implement collision by checking blocks. The player box after moving has corners:
- minX = px - 0.3, maxX = px + 0.3
- minY = py (feet), maxY = py + 1.8
- minZ = pz - 0.3, maxZ = pz + 0.3

A block at integer (bx, by, bz) occupies [bx, bx+1] x [by, by+1] x [bz, bz+1]. It collides with the player box if the boxes overlap:
minX < bx+1 && maxX > bx && minY < by+1 && maxY > by && minZ < bz+1 && maxZ > bz.

To check collisions, iterate over block coordinates in the range [floor(minX), floor(maxX)] etc.

Axis-separated: 
1. Move X: new px = px + vx*dt. Check collision with new position. If collision, set vx such that we don't move (place flush) or revert. Simplest: if collision, revert X movement (px stays). But that prevents sliding along walls. Better: resolve to surface. For simplicity and given the spec ("move per axis, revert on overlap"), let me revert on overlap. But reverting fully means no sliding. Hmm. The spec says "revert on overlap". Let me do: attempt move; if collision, revert that axis. That's what spec says. Sliding won't happen but it's acceptable per spec. Actually, we can do better: when colliding on X, snap to the surface. But let me follow spec: revert on overlap. Actually, let me reconsider — full revert means you can't walk alongside walls. But for a simple clone it's fine. However, to allow some sliding, I could move diagonally and resolve per axis: move X (revert if collide), then move Z (revert if collide). This gives sliding along X when moving Z into a wall. That's the standard approach and matches "move per axis". Let me do that:

Order: apply gravity & vertical move, then X move, then Z move. Actually let me do X, Y, Z in some order. Common: resolve each axis independently.

Let me do:
- Compute velocity (with gravity applied to vy).
- Move Y: newY = py + vy*dt. Check collision. If colliding and vy <= 0 (falling), land on block: py = block_top (set feet to block top), vy = 0, onGround = true. If colliding and vy > 0 (jumping), push down: py = block_bottom - 1.8, vy = 0. Else py = newY.
- Move X: newX = px + vx*dt. If no collision, px = newX. Else revert (px unchanged).
- Move Z similarly.

Wait, but if we revert X entirely, then moving diagonally into a wall stops us. That's acceptable.

Hmm, but actually reverting means when you press D toward a wall, you stop. When you press W parallel to wall, you move. When you press both, the X is reverted (wall) and Z moves → sliding works! Because we resolve X and Z separately. Yes! Moving W+D toward a wall on your... let me see: wall is at +X direction. Press D (move +X) → revert. Press W (move +Z... depends). Anyway, one axis reverts, other proceeds → sliding. 

But there's subtlety: if both W and D pressed and wall is +X, X reverts, Z proceeds → you slide along wall in Z. Good.

Let me define collision check function:
```js
function collides(px, py, pz) {
  const minX = Math.floor(px - 0.3), maxX = Math.floor(px + 0.3);
  const minY = Math.floor(py), maxY = Math.floor(py + 1.8);
  const minZ = Math.floor(pz - 0.3), maxZ = Math.floor(pz + 0.3);
  for (let bx = minX; bx <= maxX; bx++) {
    for (let by = minY; by <= maxY; by++) {
      for (let bz = minZ; bz <= maxZ; bz++) {
        if (getBlock(bx, by, bz) !== 0) return true;
      }
    }
  }
  return false;
}
```

Note getBlock returns 0 for y outside 0-79. At y=0 blocks are stone (unbreakable), so collision fine. Above terrain, blocks are air → no collision, player falls. Good.

Vertical resolution:
```js
// after computing vy and tentative newY
let newY = py + vy * dt;
if (!collides(px, newY, pz)) {
  py = newY;
  onGround = false;
} else {
  if (vy < 0) {
    // landing: step up to the block top
    // find the surface: the block we're landing on
    // set py so feet rest on top of block
    let blockY = Math.floor(newY);
    // descend until just above a solid block
    while (blockY >= 0 && collides(px, blockY, pz)) blockY--;
    py = blockY + 1; // feet at top of solid block
    // ensure not inside
    py = Math.max(py, newY); // don't fall through
    vy = 0;
    onGround = true;
  } else {
    // hit head
    let blockY = Math.floor(newY + 1.8);
    while (blockY <= 79 && collides(px, blockY, pz)) blockY++;
    py = blockY - 1.8;
    vy = 0;
    onGround = false;
  }
}
```

Hmm this is getting complicated. Let me simplify the landing: when falling and collision detected, set feet to just above the highest solid block in the column under the player.

Actually, let me simplify. When falling (vy<0) and collision at newY, I want to place feet on top of the ground. I can search downward from newY for the ground surface. But simpler: since we move in small steps, when collision detected during falling, set py to the top of the block we hit. The block we hit is around floor(newY). Let me do:

```js
if (vy < 0) {
  // land: move up to rest on the block
  py = Math.floor(newY) ; // candidate
  // move up until no collision
  while (py > 0 && collides(px, py, pz)) py--;
  py += 1; // now feet is on top of solid
  vy = 0; onGround = true;
}
```

Wait, starting py = floor(newY) which is inside the block (collision). Increment py until no collision. Since floor(newY) is inside a solid block, we increment until we exit. E.g., block from y=5 to 6, newY=5.3, floor=5, collides, py=6 → check collides(px,6,pz): block occupies [5,6], at py=6 the box is [6,7.8], block top is 6, so [6,7.8] vs [5,6] → overlap only at boundary 6? minX< bx+1: 6-0.3=5.7 < 6 yes; maxX>bx: 6.3>5 yes; minY<by+1: 6<6? No. So no collision at py=6. Good, feet at 6 rests on block. 

But what if there's a block at y=6 too (solid stack)? Then py=6 collides, py=7: box [7,8.8], block [6,7], minY<by+1: 7<7 no. No collision. Rests at 7. Good.

Edge: what if the ground is uneven and the block is offset? Our box is 0.6 wide, might straddle. The while loop handles it by finding the lowest non-colliding y. But it might place us partially inside horizontally? No, we only move Y. If horizontally we're overlapping a block that's higher on one side... The collision check uses the full box. Moving up until no collision ensures we're clear. Good enough.

Actually there's a subtle bug: when we move up to find rest position, we might move up through where a ceiling is. But we're on the ground, unlikely. Fine.

Let me also handle the case where after landing, we should double check not sinking. The while loop guarantees no collision at final py. Good.

Horizontal:
```js
let newX = px + vx * dt;
if (!collides(newX, py, pz)) px = newX;
let newZ = pz + vz * dt;
if (!collides(px, py, newZ)) pz = newZ;
```

Note: after moving X, we use updated px for Z check. Standard.

Spawn: above terrain at x=8, z=8. So spawn world coords (8, ?, 8). Local (8, 8) in chunk (0,0). We need to find terrain height at (8,8) and place feet above it. Since world generates lazily, at start we should generate chunk (0,0) and find surface. Let me, before the loop, generate chunk (0,0) and set player y accordingly.

Actually, let me just set initial player position to (8, 60, 8) and let gravity bring them down, but that requires chunk (0,0) to exist. Let me pre-generate chunk (0,0) at startup and set feet to surface+0.5.

Let me do initialization: generateChunkData(0,0); build mesh; find surface height at local (8,8): scan from top down for first non-air. Set py = that + 1.

Actually the main loop generates chunks within 5 of player; at player spawn (8,8) chunk (0,0) is within 5 (dx=0,dz=0). So it'll be generated in first frames. But to spawn correctly, let me pre-generate chunk (0,0) before the loop.

Let me set player feet y = 40 initially and let it fall onto freshly generated terrain. Actually cleaner: pre-generate chunk (0,0), find surface, set feet.

Water plane re-center: water plane at y=14.3, large, re-centered on player each frame. So plane position.x = player.x (feet? or eye?), position.z = player.z. Let me center on player horizontal position. Use player feet x,z or camera x,z. Let me use camera position (eye). Actually the player box center horizontal = player feet x,z (camera is above). Let me center water on player feet x,z. Since camera x = feet x (horizontal), same thing. I'll use player.x, player.z (feet).

Clouds: ~25 flat white transparent boxes at height ~90, drifting and wrapping around player. Each cloud: a group or individual meshes. Let me create 25 meshes, each a flattened box (e.g., 8x1x12), positioned randomly, moving in +x slowly. When x > player.x + 40, wrap to player.x - 40. Keep y around 90. Re-center y? Just fixed ~90. Wrap x around player.

Let me create clouds:
```js
const clouds = [];
for (let i = 0; i < 25; i++) {
  const g = new THREE.Group();
  const boxes = 2 + Math.floor(i % 3); // deterministic count
  for (let j = 0; j < boxes; j++) {
    const w = 4 + j*3, d = 4, h = 1;
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.85}));
    m.position.set(j * 4, 0, (Math.random()-0.5)*3); // but no Math.random!
    ...
  }
}
```

No Math.random allowed! "deterministic, no Math.random". So I must place cloud parts deterministically. Use a hash or just fixed offsets.

```js
m.position.set(j * 4, 0, ((i*7 + j*3) % 5) - 2);
```

Deterministic. Good.

Position cloud: x = (i * 37) % 200 - 100 + player.x... but wrapping each frame. Let me store cloud base x and update: cloud.x = player.x + (offset). Simpler: store cloud.position.x as absolute, increment by speed, wrap relative to player.

```js
cloud.x += speed*dt;
if (cloud.x > player.x + 60) cloud.x -= 120;
cloud.position.set(cloud.x, 90, cloud.z);
```
where cloud.z is a fixed offset (deterministic). Let me store z = (i*53)%120 - 60.

Actually wrapping: if cloud.x > player.x + 60, subtract 120. This keeps clouds near player. Good. Speed ~2 units/sec.

Let me finalize cloud creation:
```js
for (let i = 0; i < 25; i++) {
  const g = new THREE.Group();
  const parts = 2 + (i % 3);
  for (let j = 0; j < parts; j++) {
    const w = 3 + j * 2.5;
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, 1, 3), new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.85}));
    m.position.set(j * 3, 0, ((i*13 + j*7) % 7) - 3);
    g.add(m);
  }
  const baseX = (i * 97) % 140 - 70;
  const baseZ = (i * 61) % 140 - 70;
  g.position.set(baseX, 90, baseZ);
  g.userData = { speed: 1.5 + (i%4)*0.3, baseX: baseX, baseZ: baseZ, playerRef: null };
  scene.add(g);
  clouds.push(g);
}
```

Update:
```js
for (const c of clouds) {
  c.position.x += c.userData.speed * dt;
  if (c.position.x > camPos.x + 70) c.position.x -= 140;
  c.position.z = c.userData.baseZ + (camPos.z - spawnZ) ... 
}
```

Hmm, clouds should wrap around player. Let me keep cloud z relative to player too, or just drift and wrap x only. Simpler: wrap both x and z around player. Actually let me make clouds orbit-ish: keep them within a radius of player. Let me just wrap x; for z, also wrap so they stay near. But if I fix baseZ and only move x, clouds form lines across the map drifting in x, which is fine and looks natural. They'll pass behind and ahead. Let me wrap x when exceeding player.x ± 70. For z, keep fixed offset but also wrap if player moves far. Since player can move anywhere, fixed z would drift away. Let me recompute z relative to player each frame:

Actually simplest robust approach: store cloud's position relative to player (relX, relZ). Each frame: relX += speed*dt; if relX > 70 relX -= 140; position.set(player.x+relX, 90, player.z+relZ). This keeps clouds around player always. 

```js
cloud.relX, cloud.relZ fixed at creation.
update: cloud.relX += speed*dt; if (cloud.relX > 70) cloud.relX -= 140;
cloud.position.set(player.x + cloud.relX, 90, player.z + cloud.relZ);
```

Good.

Water plane:
```js
const water = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshLambertMaterial({color:0x2b6fd4, transparent:true, opacity:0.6}));
water.rotation.x = -Math.PI/2;
scene.add(water);
```
Re-center each frame: water.position.set(player.x, 14.3, player.z). PlaneGeometry is in XY plane; rotating x by -90° makes it horizontal. Good.

Wait, PlaneGeometry lies in XY plane with normal along Z. Rotating -90° about X tilts it to lie in XZ plane with normal +Y. Good, horizontal surface at y=14.3.

### UI / Controls

Start overlay: fullscreen div with title, controls list, "click to play". On click, request pointer lock. Reappears when pointer lock released (pointerlockchange event).

Crosshair: small div at center.

Hotbar: 7 slots at bottom center.

Let me write HTML:
```html
<div id="overlay">
  <div id="title">MC</div>
  <ul id="controls">...</ul>
  <div id="play">Click to play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>
<canvas id="game"></canvas>
```

CSS: overlay fullscreen, crosshair centered, hotbar bottom center.

Event handling:
- pointerlockchange: if document.pointerLockElement is null → overlay visible. Else hidden.
- mousedown: if locked, handle break/place. Before that, on overlay click, requestPointerLock.
- mousemove: if locked, yaw -= movementX*sens, pitch -= movementY*sens, clamp pitch.
- wheel: change selection.
- keydown: 1-7 select.
- contextmenu: preventDefault (to allow right-click place).

Let me write the selection and hotbar building.

```js
const hotbarBlocks = [1,2,3,4,5,6,7];
let selected = 0; // index 0..6
```

Build hotbar DOM:
```js
const hotbar = document.getElementById('hotbar');
for (let i = 0; i < 7; i++) {
  const slot = document.createElement('div');
  slot.className = 'slot';
  slot.dataset.index = i;
  const color = '#' + hotbarBlocks[i].toString(16).padStart(6,'0');
  slot.style.background = color;
  slot.innerHTML = `<span class="num">${i+1}</span>`;
  hotbar.appendChild(slot);
}
function updateHotbar() {
  document.querySelectorAll('.slot').forEach(s => {
    s.classList.toggle('selected', parseInt(s.dataset.index) === selected);
  });
}
```

Key handling: key '1' → selected 0, etc.

Mouse wheel: selected = (selected + (deltaY>0?1:-1)+7)%7.

### Putting it together — main loop

```js
let last = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  let dt = (now - last) / 1000;
  last = now;
  if (dt > 0.1) dt = 0.1; // clamp
  
  if (pointerLocked) {
    // update camera rotation
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
    // movement
    ... physics ...
    // spawn below check
    if (player.y < -20) { reset to spawn; }
  }
  
  // world updates (chunk gen/mesh) - do regardless? Only when needed. Do always but cheap.
  updateChunks();
  
  // raycast for target
  if (pointerLocked) updateTarget();
  
  // water, clouds
  updateClouds(dt);
  water.position.set(player.x, 14.3, player.z);
  
  // camera position
  camera.position.set(player.x, player.y + 1.62, player.z);
  
  renderer.render(scene, camera);
}
```

Wait, camera rotation order YXZ. Setting rotation.y then rotation.x. With order YXZ, three applies rotations in order X then Y? The order string indicates the order of application. 'YXZ' means rotate Z first, then Y, then X? Actually Three.js Euler order string lists the axes in the order they are applied, rightmost first? Let me recall: for order 'XYZ', it applies X first then Y then Z. For 'YXZ', applies Y first? Hmm.

Actually, Three.js Euler: the order string specifies the sequence of rotation applications. For 'YXZ', rotations are applied in the order Y, then X, then Z? Or Z, X, Y? 

From Three.js docs: "The order argument sets the order of rotation for subsequent instances of the object. It is a concatenation of the rotation order letters XYZ, XZY, YXZ, YZX, ZXY, ZYX." The order is the order in which rotations are applied, reading left to right. So 'YXZ' means rotate around Y first, then X, then Z.

But we only set Y and X (Z=0). Setting rotation.y = yaw, rotation.x = pitch. With order YXZ, the effective rotation is Y applied first then X. That gives yaw around world Y then pitch around the already-rotated X (local X). That's the standard FPS camera. Good.

Actually, to be safe, I'll set camera.rotation.set(pitch, yaw, 0, 'YXZ'). Hmm order of args: set(x, y, z, order). So set(pitch, yaw, 0, 'YXZ'). Let me use that.

Let me double check getWorldDirection with this. It should give forward. Good.

Now, potential issue: when pitch is extreme, but we clamp pitch to [-π/2+eps, π/2-eps].

### Pointer lock

```js
const canvas = document.getElementById('game');
overlay.addEventListener('click', () => {
  canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  if (document.pointerLockElement === canvas) {
    pointerLocked = true;
    overlay.style.display = 'none';
  } else {
    pointerLocked = false;
    overlay.style.display = 'flex';
  }
});
document.addEventListener('mousemove', (e) => {
  if (!pointerLocked) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  const limit = Math.PI/2 - 0.01;
  if (pitch > limit) pitch = limit;
  if (pitch < -limit) pitch = -limit;
});
document.addEventListener('mousedown', (e) => {
  if (!pointerLocked) return;
  if (e.button === 0) { // break
    breakTarget();
  } else if (e.button === 2) { // place
    placeTarget();
  }
});
document.addEventListener('contextmenu', (e) => e.preventDefault());
document.addEventListener('wheel', (e) => {
  if (!pointerLocked) return;
  selected = (selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
  updateHotbar();
});
document.addEventListener('keydown', (e) => {
  const k = e.key;
  if (k >= '1' && k <= '7') { selected = parseInt(k) - 1; updateHotbar(); }
  keys[e.code] = true;
});
document.addEventListener('keyup', (e) => { keys[e.code] = false; });
```

Break/place:
```js
function breakTarget() {
  if (!target || target[1] === 0) return; // not at y 0
  setBlock(target[0], target[1], target[2], 0);
  rebuildChunk(target[0], target[1], target[2]);
}
function placeTarget() {
  if (!target) return;
  const cell = [Math.floor(hitPoint.x + normal.x*0.5), ...];
  // Actually we compute place from hit
  if (getBlock(place...) !== 0) return;
  // check not overlapping player
  if (overlapsPlayer(place...)) return;
  setBlock(...);
  rebuildChunk(...);
}
```

Let me store the current hit info (point, normal) and derived target/place cells, updated each frame in updateTarget(). Then break/place use stored values.

Let me store:
```js
let targetCell = null; // [x,y,z] to break
let placeCell = null; // [x,y,z] to place
```

updateTarget():
```js
function updateTarget() {
  targetCell = null; placeCell = null;
  raycaster.set(camera.position, cameraDir);
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length > 0) {
    const hit = hits[0];
    const p = hit.point;
    const n = hit.face.normal;
    targetCell = [Math.floor(p.x - n.x*0.5), Math.floor(p.y - n.y*0.5), Math.floor(p.z - n.z*0.5)];
    placeCell = [Math.floor(p.x + n.x*0.5), Math.floor(p.y + n.y*0.5), Math.floor(p.z + n.z*0.5)];
    outline.position.set(targetCell[0]+0.5, targetCell[1]+0.5, targetCell[2]+0.5);
    outline.visible = true;
  } else {
    outline.visible = false;
  }
}
```

cameraDir:
```js
const cameraDir = new THREE.Vector3();
camera.getWorldDirection(cameraDir);
```

rebuildChunk(wx, wy, wz): determine chunk, rebuild it, and neighbor if on border.
```js
function rebuildChunk(wx, wy, wz) {
  const cx = chunkIndex(wx), cz = chunkIndex(wz);
  rebuildChunkById(cx, cz);
  // if on border, rebuild neighbor
  const lx = localCoord(wx);
  if (lx === 0) rebuildChunkById(cx-1, cz);
  if (lx === 15) rebuildChunkById(cx+1, cz);
  const lz = localCoord(wz);
  if (lz === 0) rebuildChunkById(cx, cz-1);
  if (lz === 15) rebuildChunkById(cx, cz+1);
}
function rebuildChunkById(cx, cz) {
  const key = cx + ',' + cz;
  const chunk = chunks.get(key);
  if (!chunk || !chunk.data) return;
  if (chunk.mesh) {
    scene.remove(chunk.mesh);
    chunk.mesh.geometry.dispose();
    const idx = chunkMeshes.indexOf(chunk.mesh);
    if (idx >= 0) chunkMeshes.splice(idx, 1);
  }
  buildChunkMesh(cx, cz);
}
```

Place overlap check:
```js
function overlapsPlayer(cell) {
  const [bx, by, bz] = cell;
  const minX = player.x - 0.3, maxX = player.x + 0.3;
  const minY = player.y, maxY = player.y + 1.8;
  const minZ = player.z - 0.3, maxZ = player.z + 0.3;
  return !(maxX < bx || minX > bx+1 || maxY < by || minY > by+1 || maxZ < bz || minZ > bz+1);
}
```

Place:
```js
function placeTarget() {
  if (!placeCell) return;
  const [x,y,z] = placeCell;
  if (y < 0 || y > 79) return;
  if (getBlock(x,y,z) !== 0) return;
  if (overlapsPlayer([x,y,z])) return;
  setBlock(x,y,z, hotbarBlocks[selected]);
  rebuildChunk(x,y,z);
}
```

Break:
```js
function breakTarget() {
  if (!targetCell) return;
  const [x,y,z] = targetCell;
  if (y === 0) return; // not at y 0
  setBlock(x,y,z, 0);
  rebuildChunk(x,y,z);
}
```

### Initialization

```js
// pre-generate spawn chunk
generateChunkData(0, 0);
buildChunkMesh(0, 0);
// find surface at local (8,8) world (8,8)
let spawnY = 79;
while (spawnY > 0 && getBlock(8, spawnY, 8) === 0) spawnY--;
player.set(8, spawnY + 1.0, 8); // feet just above surface
```

Wait, player is feet position. spawnY is the surface block top index (non-air at spawnY). Feet should be at spawnY+1 (standing on top). Let me set player.y = spawnY + 1. Actually getBlock(8,spawnY,8) != 0 means block there. Feet at spawnY+1 stands on it. But if spawnY is the top non-air, then spawnY+1 is air. Good. Set player.y = spawnY + 1.

Hmm, but I need to make sure chunk (0,0) generated before this. Yes.

Also need to make sure the mesh for spawn area exists. buildChunkMesh(0,0) covers local 0-15, and player at local (8,8) is within. Good.

Let me also make sure to generate and mesh a few chunks around spawn for immediate visibility. The main loop will handle it.

### Constants and setup

```js
THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
body.appendChild(canvas);
scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.5, 1, 0.3).normalize().multiplyScalar(100);
scene.add(sun);
```

Wait, DirectionalLight intensity in r128 — 0.8 is fine (r128 uses linear, not physically based). Good.

Camera:
```js
const camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';
scene.add(camera);
```

sharedMaterial:
```js
const sharedMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

### Movement details

```js
const keys = {};
let yaw = 0, pitch = 0;
const player = new THREE.Vector3(); // feet
let vy = 0;
let onGround = false;
```

Physics in loop:
```js
if (pointerLocked) {
  // gravity
  vy -= 25 * dt;
  // jump
  if (keys['Space'] && onGround) { vy = 8.5; onGround = false; }
  
  // horizontal input
  const fwd = new THREE.Vector3();
  camera.getWorldDirection(fwd);
  fwd.y = 0; fwd.normalize();
  const right = new THREE.Vector3(fwd.z, 0, -fwd.x).normalize();
  let mx = 0, mz = 0;
  if (keys['KeyW']) { mx += fwd.x; mz += fwd.z; }
  if (keys['KeyS']) { mx -= fwd.x; mz -= fwd.z; }
  if (keys['KeyD']) { mx += right.x; mz += right.z; }
  if (keys['KeyA']) { mx -= right.x; mz -= right.z; }
  const len = Math.hypot(mx, mz);
  if (len > 0) { mx = mx/len * 5.5 * dt; mz = mz/len * 5.5 * dt; }
  
  // move Y
  let ny = player.y + vy * dt;
  if (!collides(player.x, ny, player.z)) {
    player.y = ny; onGround = false;
  } else {
    if (vy < 0) {
      // land
      let ly = Math.floor(ny);
      while (ly > 0 && collides(player.x, ly, player.z)) ly--;
      player.y = ly + 1;
      vy = 0; onGround = true;
    } else {
      // hit head
      let hy = Math.floor(player.y + 1.8);
      while (hy < 80 && collides(player.x, hy, player.z)) hy++;
      player.y = hy - 1.8;
      vy = 0; onGround = false;
    }
  }
  
  // move X
  let nx = player.x + mx;
  if (!collides(nx, player.y, player.z)) player.x = nx;
  
  // move Z
  let nz = player.z + mz;
  if (!collides(player.x, player.y, nz)) player.z = nz;
  
  // fell off
  if (player.y < -20) {
    player.set(8, spawnY + 1, 8); vy = 0;
  }
}
```

Wait, collides uses player box with feet at player.y. When moving Y down into ground, we detect collision and land. Good. But note: initially player spawns at spawnY+1 which is air above surface; collides false, falls. Good.

One concern: the landing while loop `while (ly > 0 && collides(...)) ly--`. Start ly = floor(ny). If ny is inside a solid block, collides true, decrement ly. Continue until no collision. Then player.y = ly+1. But what if floor(ny) is already above a block (no collision)? Then ly doesn't decrement, player.y = ly+1 which might jump up into the block? Let me think: we only enter the `else` branch (landing) when collides(player.x, ny, player.z) is true, meaning at ny there's collision. floor(ny) ≤ ny. If ny is inside block [b, b+1], floor(ny)=b, collides, decrement... wait we want to rise to top of block. Starting ly = floor(ny) = b (inside), collides true, ly-- → b-1. Now check collides at b-1: block [b-1,b]? If that's air, no collision, stop. player.y = (b-1)+1 = b. Feet at b, which is top of block below? Hmm, if block is [b,b+1] and block below [b-1,b], feet at b rests on top of [b-1,b]. But we wanted to rest on top of the block we fell into, which is [b,b+1] top at b+1. 

Wait I think I have the logic backwards. When falling, the ground is BELOW us. ny decreases. We detect collision when our box starts overlapping solid. The solid is below. We want to rest with feet on top of that solid block.

Let me reconsider. Suppose ground block occupies y in [5,6]. Player falling, feet approaching. At player.y=5.5, box [5.5, 7.3]. Does it collide with [5,6]? minX=5.2<6 yes, maxX=5.8>5 yes, minY=5.5<6 yes, maxY=7.3>5 yes, z overlaps. So collision at player.y=5.5. floor(5.5)=5. My loop: ly=5, collides? box [5,6.8], with ground [5,6]: minY=5<6, maxY=6.8>5, x overlap → collision. ly-- → 4. box [4,5.8] vs [5,6]: minY=4<6, maxY=5.8>5, x overlap, but minY<by+1=6 and maxY>by=5 → overlap → collision! ly-- → 3. box [3,4.8] vs [5,6]: maxY=4.8 < 5? by+1=6, minY=3<6 yes; maxY=4.8 > by=5? No, 4.8<5. So no collision (maxY < by). Stop at ly=3. player.y = 3+1 = 4. But that places feet at 4, which is below the ground top (6)! That's wrong — we'd be inside the ground.

The problem: my while loop goes DOWN (ly--) but should go UP (ly++) to find the surface to stand on. When falling and colliding, I need to move UP to rest on top of the ground.

Let me redo: when falling (vy<0) and collision at ny, find the resting position by moving UP from ny until no collision.

```js
if (vy < 0) {
  let ly = Math.floor(ny);
  // move up until no collision
  while (ly < 80 && collides(player.x, ly, player.z)) ly++;
  player.y = ly; // feet at first non-colliding integer level
  // but this might overshoot; better set to ly (already non-colliding)
  vy = 0; onGround = true;
}
```

Wait let me test. Ground [5,6]. ny=5.5, floor=5. collides at 5? yes (computed above). ly++ → 6. collides at 6? box [6,7.8] vs [5,6]: minY=6 < by+1=6? No (6<6 false). No collision. Stop at ly=6. player.y = 6. Feet at 6 = top of ground block. Correct!

Another: ground [5,6], but we fell further, ny=4.2 (already past?). Actually we detect collision when overlapping. Let me trust it.

But there's an edge: what if after moving up we still collide because of a ceiling above? Unlikely when falling to ground. Fine.

Also need to ensure we don't get stuck inside if the whole column is solid (e.g., spawned inside). Should be fine.

Let me also handle: after landing, verify onGround only when we actually landed (vy<0 and collided). Yes.

Head-bump (vy>0 and collide): move down. Find resting by moving down:
```js
else { // vy > 0
  let hy = Math.floor(player.y + 1.8); // top of box
  while (hy > 0 && collides(player.x, hy, player.z)) hy--;
  player.y = hy; // so that top of box (player.y+1.8) just below ceiling
  // Actually we want feet such that box top is below ceiling.
  vy = 0; onGround = false;
}
```
Hmm let me think. Ceiling block at [8,9]. Player standing, feet at 8, box [8,9.8]. Top at 9.8 overlaps ceiling [8,9]? maxY=9.8>8, minY=8<9, overlap → collide. We want to push down so box top ≤ 8. Move down: hy = floor(player.y+1.8) = floor(9.8)=9. collides at 9? box [9,10.8] vs [8,9]: minY=9<9? no. no collision. So hy=9, player.y=9?? That's higher than 8, moving up. Wrong direction.

The head bump: we jumped up and hit ceiling. We should move DOWN. Current feet at 8 (box [8,9.8]) collides with ceiling [8,9]. To clear, feet must be ≤ 8-... we want box top ≤ 8, i.e., player.y+1.8 ≤ 8 → player.y ≤ 6.2. So feet at 6.2. 

Let me instead directly compute: we need top of box below ceiling bottom. Find the lowest solid block above current top. Actually simpler: move feet down until no collision.

```js
else { // vy > 0, hit head
  let hy = Math.floor(player.y); // start at current feet floor
  while (hy >= 0 && collides(player.x, hy, player.z)) hy--;
  player.y = hy + 1; ... 
}
```
Hmm. Let me think differently. When hitting head, current feet player.y such that box collides. Move feet down: try decreasing player.y. Find largest player.y' < player.y with no collision.

```js
let test = player.y;
// move down until no collision
while (test > 0 && collides(player.x, test, player.z)) test -= 0.5; // coarse
```
Too hacky. Let me use integer stepping but from current feet.

Actually, the cleanest: for head bump, set player.y so that the top of the box is just below the lowest solid block above the current box top.

Current box top = player.y + 1.8. Find smallest block index by >= that which is solid; feet should be just below it: player.y = solidBlockIndex - 1.8 (if solidBlockIndex is the bottom of the solid block). Let me:

```js
// hit head: find solid block at or above box top
let top = player.y + 1.8;
let sb = Math.ceil(top); // candidate block bottom
while (sb <= 80 && getBlock(player.x_round?, sb, player.z_round?) ... )
```

This is getting messy with rounding. Let me just do a downward search with fine steps:

```js
// hit head
let testY = player.y;
while (testY > 0) {
  testY -= 0.1;
  if (!collides(player.x, testY, player.z)) { player.y = testY; break; }
}
```
This works but 0.1 steps. Given small movements it's fine. But could be slow if far. Usually collision is immediate so few steps. Acceptable.

Actually, let me reconsider the whole collision approach. A common robust method: after computing new position, if collision, snap to surface along the axis. For vertical, compute the exact resting y.

Let me just do the downward search for head bump with a reasonable step and cap iterations:
```js
else { // vy > 0
  let testY = player.y;
  for (let s = 0; s < 40; s++) {
    testY -= 0.1;
    if (testY <= 0) break;
    if (!collides(player.x, testY, player.z)) { player.y = testY; break; }
  }
  vy = 0;
}
```

Good enough.

For landing, use upward integer search:
```js
if (vy < 0) {
  let ly = Math.floor(ny);
  while (ly < 80 && collides(player.x, ly, player.z)) ly++;
  player.y = ly;
  vy = 0; onGround = true;
}
```
Test earlier gave correct result (feet at 6 on ground [5,6]). But wait, if ny was say 5.5 and floor=5, we found ly=6, player.y=6. But what if the ground top is at 6 and we set feet=6, box [6,7.8]. Good, resting on top. 

But consider player falling from high, ny=2.0 (fell through multiple blocks in one frame due to high speed). floor=2. collides at 2? If ground is at [5,6] but we're at 2, box [2,3.8] doesn't collide with [5,6]! So no collision detected, player keeps falling through the gap created by fast movement. This is tunneling. To mitigate, clamp dt and gravity. With gravity 25 and dt ~0.016, vy max ~0.4/frame, movement ~0.4/block. Shouldn't tunnel through a 1-block gap typically. But caves could cause issues. Acceptable for this clone. Also onGround resets when in air.

Actually there's a subtle issue: when falling fast and landing, the upward search from floor(ny) — if ny=2 and ground at 5, no collision at 2, we don't land, keep falling. Next frame ny≈1.6, still no collision until near 5. Eventually ny≈4.9, floor=4, collides? box [4,5.8] vs [5,6]: maxY=5.8>5, minY=4<6, overlap → collide. Upward search: ly=4 collides, ly=5: box[5,6.8] vs [5,6]: minY=5<6,maxY=6.8>5,x overlap → collide. ly=6: no collision. player.y=6. Lands at 6. Good, just takes a couple frames. Fine.

Alright.

### Camera direction for raycast

I'll compute cameraDir each frame:
```js
camera.getWorldDirection(cameraDir);
```
Need cameraDir as a reusable Vector3.

### Outline

```js
const outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.02, 1.02, 1.02)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);
```

### Clouds and water as above.

### Chunk update function

```js
function updateChunks() {
  const pcx = chunkIndex(player.x), pcz = chunkIndex(player.z);
  // generate data for chunks within 5, max 4
  let gen = 0, done = false;
  gouter: for (let dx = -5; dx <= 5 && !done; dx++) {
    for (let dz = -5; dz <= 5; dz++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx + ',' + cz;
      if (!chunks.has(key)) {
        generateChunkData(cx, cz);
        gen++;
        if (gen >= 4) { done = true; break gouter; }
      }
    }
  }
  // build meshes for chunks within 4 whose 4 neighbors have data, max 2
  let meshCount = 0, mdone = false;
  mouter: for (let dx = -4; dx <= 4 && !mdone; dx++) {
    for (let dz = -4; dz <= 4; dz++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx + ',' + cz;
      const chunk = chunks.get(key);
      if (chunk && chunk.data && !chunk.mesh) {
        const nE = chunks.get((cx+1)+','+cz);
        const nW = chunks.get((cx-1)+','+cz);
        const nN = chunks.get(cx+','+(cz+1));
        const nS = chunks.get(cx+','+(cz-1));
        if (nE && nE.data && nW && nW.data && nN && nN.data && nS && nS.data) {
          buildChunkMesh(cx, cz);
          meshCount++;
          if (meshCount >= 2) { mdone = true; break mouter; }
        }
      }
    }
  }
  // remove far chunks
  for (const [key, chunk] of chunks) {
    const cx = parseInt(key.split(',')[0]), cz = parseInt(key.split(',')[1]);
    if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
      if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        const idx = chunkMeshes.indexOf(chunk.mesh);
        if (idx >= 0) chunkMeshes.splice(idx, 1);
      }
      chunks.delete(key);
    }
  }
}
```

Iterating a Map with for...of while deleting — in JS, deleting entries during iteration is allowed but order is insertion order; safe enough.

### Let me now also double-check the "keep mesh at origin" and raycasting.

Since meshes are at origin with world coords in geometry, raycasting against them uses world coordinates directly. camera.position is world. Good. hit.point is world. Good.

### Face winding and lighting

MeshLambertMaterial uses normals for lighting; winding doesn't matter without face culling (default no cull? Actually default side is FrontSide, so back faces are culled). We only add faces where neighbor is air, so all added faces are outward-facing. Their normals point outward. For each face we defined normals pointing outward. Good. Winding: for FrontSide, visible if winding is CCW from outside. Let me ensure our vertex order gives correct outward normals. It generally does for standard definitions. Even if some are back-facing and culled, we might lose some faces. To be safe, set material side to DoubleSide? But that halves performance and could show internals. Since we only generate exterior faces with correct outward normals, FrontSide should show them. Let me make sure winding is CCW when viewed from the normal direction.

For top face, normal (0,1,0). Vertices (in order): (0,1,0),(0,1,1),(1,1,1),(1,1,0). Viewed from above (+y looking down -z), we want CCW. Points in xy... let me project to xz (since y constant). Points: (x,z)=(0,0),(0,1),(1,1),(1,0). Viewed from +y looking down, with x right and z... when looking down from +y, the screen has x to the right and z upward? Depends on handedness. This is getting complicated. 

To avoid winding issues, I'll just set material side to THREE.FrontSide (default) but ensure correctness, OR use DoubleSide to be safe. Given it's a clone and performance isn't critical, but DoubleSide doubles fill. Let me instead carefully define winding to be CCW viewed from outside.

Standard cube face definitions (CCW from outside) — let me use a known-good set. Actually, let me just define each face's 4 vertices and 2 triangles such that the cross product of edges aligns with the normal.

For a face with normal N and 4 vertices V0,V1,V2,V3 (a square), the winding is correct (CCW from outside) if (V1-V0) × (V2-V0) points in the same direction as N.

Let me construct top face: V0=(0,1,0), V1=(1,1,0), V2=(1,1,1), V3=(0,1,1). 
(V1-V0)=(1,0,0), (V2-V0)=(1,0,1). Cross = (1,0,0)×(1,0,1) = (0*1-0*1, 0*1-1*1, 1*0-0*1) = (0, -1, 0). That points -Y, but normal is +Y. So this winding is CW from outside → back face. So I should reverse: use V0=(0,1,0), V1=(0,1,1), V2=(1,1,1), V3=(1,1,0).
(V1-V0)=(0,0,1), (V2-V0)=(1,0,1). Cross = (0,0,1)×(1,0,1) = (0*1-1*0, 1*1-0*1, 0*0-0*1) = (0,1,0). +Y. Correct! So top face order: (0,1,0),(0,1,1),(1,1,1),(1,1,0). That matches what I had earlier. Good.

Let me verify each face with cross product = normal.

Define face vertex offsets (relative to block origin x,y,z) and desired normal:

Top (normal +Y): V0=(0,1,0), V1=(0,1,1), V2=(1,1,1), V3=(1,1,0). Cross computed = (0,1,0). ✓

Bottom (normal -Y): Need cross of (V1-V0)×(V2-V0) = (0,-1,0). 
Try V0=(0,0,1), V1=(0,0,0), V2=(1,0,0), V3=(1,0,1).
(V1-V0)=(0,0,-1), (V2-V0)=(1,0,-1). Cross = (0,0,-1)×(1,0,-1) = (0*(-1) - (-1)*0, (-1)*1 - 0*(-1), 0*0 - 0*1) = (0, -1, 0). ✓ 

+X (normal +X): Try V0=(1,0,0), V1=(1,1,0), V2=(1,1,1), V3=(1,0,1).
(V1-V0)=(0,1,0), (V2-V0)=(0,1,1). Cross = (0,1,0)×(0,1,1) = (1*1-0*1, 0*0-0*1, 0*1-1*0) = (1, 0, 0). ✓

-X (normal -X): Try V0=(0,0,0), V1=(0,0,1), V2=(0,1,1), V3=(0,1,0).
(V1-V0)=(0,0,1), (V2-V0)=(0,1,1). Cross = (0,0,1)×(0,1,1) = (0*1-1*1, 1*0-0*1, 0*1-0*0) = (-1, 0, 0). ✓

+Z (normal +Z): Try V0=(0,0,1), V1=(1,0,1), V2=(1,1,1), V3=(0,1,1).
(V1-V0)=(1,0,0), (V2-V0)=(1,1,0). Cross = (1,0,0)×(1,1,0) = (0*0-0*1, 0*1-1*0, 1*1-0*1) = (0, 0, 1). ✓

-Z (normal -Z): Try V0=(1,0,0), V1=(0,0,0), V2=(0,1,0), V3=(1,1,0).
(V1-V0)=(0,0,0)? wait V1-V0 = (0-1,0,0)=(-1,0,0). (V2-V0)=(-1,1,0). Cross = (-1,0,0)×(-1,1,0) = (0*0-0*1, 0*(-1)-(-1)*0, (-1)*1-0*(-1)) = (0, 0, -1). ✓

Great, all faces verified with CCW winding from outside. Let me store these offsets:

```js
const FACE_DATA = {
  top:    { n:[0,1,0], v:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]], light:1.0 },
  bottom: { n:[0,-1,0], v:[[0,0,1],[0,0,0],[1,0,0],[1,0,1]], light:0.55 },
  right:  { n:[1,0,0], v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]], light:0.8 },
  left:   { n:[0,0?... ] }
};
```

Wait left I defined as V0=(0,0,0),V1=(0,0,1),V2=(0,1,1),V3=(0,1,0), normal -X. Let me label it 'left' (-X). And I need to map neighbor checks:
- top: neighbor (x, y+1, z), if air → add top face.
- bottom: neighbor (x, y-1, z), if air → add bottom.
- right (+x): neighbor (x+1, y, z), if air → add right.
- left (-x): neighbor (x-1, y, z), if air → add left.
- front (+z): neighbor (x, y, z+1), if air → add front.
- back (-z): neighbor (x, y, z-1), if air → add back.

Let me name front=+z, back=-z.

Front (+z): V0=(0,0,1),V1=(1,0,1),V2=(1,1,1),V3=(0,1,1), normal +Z.
Back (-z): V0=(1,0,0),V1=(0,0,0),V2=(0,1,0),V3=(1,1,0), normal -Z.

Let me store:
```js
const FACES = {
  top:    { n:[0,1,0], v:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]], l:1.0 },
  bottom: { n:[0,-1,0], v:[[0,0,1],[0,0,0],[1,0,0],[1,0,1]], l:0.55 },
  rx:     { n:[1,0,0], v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]], l:0.8 },
  lx:     { n:[-1,0,0], v:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]], l:0.8 },
  rz:     { n:[0,0,1], v:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]], l:0.8 },
  bz:     { n:[0,0,-1], v:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]], l:0.8 },
};
```

Then in buildChunkMesh:
```js
for each block at (x,y,z) with id!=0:
  const rgb = blockRGB[id];
  const nb = {
    top: getBlock(x, y+1, z),
    bottom: getBlock(x, y-1, z),
    rx: getBlock(x+1, y, z),
    lx: getBlock(x-1, y, z),
    rz: getBlock(x, y, z+1),
    bz: getBlock(x, y, z-1),
  };
  for (const f in FACES) {
    if (nb[f] === 0) {
      const F = FACES[f];
      const i0 = pos.length/3;
      for (const vv of F.v) {
        pos.push(x+vv[0], y+vv[1], z+vv[2]);
        norm.push(F.n[0], F.n[1], F.n[2]);
        col.push(rgb[0]*F.l, rgb[1]*F.l, rgb[2]*F.l);
      }
      idx.push(i0,i0+1,i0+2, i0,i0+2,i0+3);
    }
  }
```

Good.

### Performance

Building mesh each frame for up to 2 chunks with up to 16*16*80 = 20480 blocks, each checking 6 neighbors → ~120k getBlock calls per chunk. That's fine at 2 per frame.

### Now let me also reconsider: the spec says "Keep all chunk meshes in a global array for raycasting". I have chunkMeshes global array. Good.

### Let me also ensure the overlay click requests pointer lock and the canvas is clickable. Overlay is on top; clicking it triggers requestPointerLock. Good.

### Edge: requestPointerLock must be in a user gesture. Click handler is a user gesture. Good.

### Let me write the full HTML now.

Let me also make sure to handle initial generation: pre-generate chunk (0,0) and build its mesh, set player. Also maybe pre-generate a few surrounding chunks so the horizon isn't empty at start. Let me pre-generate chunks within radius 2 and build meshes, to have immediate terrain. Actually the main loop will do it over a few frames. But to spawn correctly and have something to see, let me pre-generate a small area (say within 2 chunks) and build meshes. This also avoids a blank screen for the first second.

Let me pre-generate chunks within radius 2 (25 chunks) and build all their meshes. That's instant and gives a nice start.

Actually building 25 meshes at once might be a bit heavy but fine (each up to ~20480 blocks but most underground hidden; still we iterate all). 25 * 20480 * 6 = 3M getBlock calls, quick. Let me do radius 2.

Hmm, but getBlock reads from chunks.map; if a neighbor chunk isn't generated, returns air → those faces render (exposed). For pre-generated radius 2, the border chunks' outer faces would be exposed until neighbors generate. That's fine, they'll get culled once neighbors generate and we rebuild. But rebuilding only happens on edit or far removal. Neighbors generating later won't trigger rebuild of already-meshed chunks. So there could be permanently exposed faces at the boundary of pre-generated region until player moves and triggers rebuild. 

To avoid this, maybe don't pre-build meshes beyond what's necessary, or accept minor exposed faces temporarily. Actually, when new chunks generate and get meshed, their faces toward already-meshed chunks are correct (they check neighbors). The already-meshed chunks won't re-examine. So the exposed faces on old chunks remain. This is a minor visual artifact near the pre-gen boundary. 

Simplest fix: don't pre-build meshes at all; just pre-generate block data for a small region so spawn works and terrain exists, then let meshing proceed naturally. Since meshing requires neighbors to have data, and we generate data for radius 5, the meshes will build up. At spawn, chunk (0,0) data exists, neighbors may not yet → mesh blocked until neighbors generate. Over first ~second, meshes appear. That's acceptable (loading effect).

Alternatively, pre-generate data for radius 5 fully (all 121 chunks) instantly, then mesh builds. Generating 121 chunks * 20480 blocks = 2.5M blocks with noise — fast (<100ms). Then meshing 2 at a time reveals terrain. Let me pre-generate data for radius 3 (49 chunks) quickly, giving good coverage, then let meshes build. Exposed faces at radius-3 boundary: those chunks' outer faces exposed until radius-4 chunks generate and we rebuild radius-3 chunks. But we never rebuild radius-3 unless edited or removed. Minor exposed faces possible. 

Hmm. To fully avoid, I could rebuild all chunks whose neighbor newly generated. But that's complex. Given it's a clone, minor exposed faces at a boundary far from player (radius 3-4) is negligible since fog hides distances >110 and chunks at radius 3 from player span roughly 48 blocks away, within fog but the exposed faces would be on the far side facing away... actually they'd face inward toward player potentially. Could be visible as thin gaps. 

Let me just NOT pre-mesh. Pre-generate data for radius 2 (so spawn terrain is solid and nearby), but only build mesh for chunk (0,0) (where player is). Then let the normal meshing flow handle the rest, and since data for radius 5 is generated, meshes build with correct culling as they come online. The only issue: when chunk (0,0) mesh was built before its neighbors had data, some faces are exposed. But if I generate ALL data first (radius 5) then build meshes, culling is correct from the start.

Plan:
1. Pre-generate block data for all chunks within radius 5 (or 3) — do this synchronously at startup (fast enough).
2. Then the main loop meshes them 2 per frame, revealing terrain with correct culling.

Since data is fully generated before any meshing, culling is correct. 

Let me pre-generate radius 3 (49 chunks) synchronously. That's 49*20480 ≈ 1M blocks with noise eval. Fast (<100ms). Then meshes build over time. Boundary at radius 3 will eventually get neighbors (radius 4) generated and meshed, but radius-3 chunks won't rebuild. However, once player is near the boundary, editing/moving could... no rebuild triggered. 

Alternative: I can make chunk meshing also rebuild a chunk if any of its neighbors newly appeared. But simplest: pre-generate a larger radius so boundary is far. If I pre-generate radius 5 (121 chunks) synchronously (~2.5M blocks, maybe 200-400ms once), then the meshing flow builds meshes for radius up to 4 while radius 5+ generate on demand. The radius-4 chunks will be meshed and their culling checks radius-5 neighbors (data exists) → correct. Radius-5 chunks get meshed later; their culling checks radius-6 (not yet) → some exposed faces at radius 5-6 boundary, but that's far (80+ blocks) and within fog (~110). Borderline visible. 

Given fog cutoff 110 and chunk radius 5 = 80 blocks, radius 5 boundary is at ~80-96 blocks, within fog. Minor exposed faces possible there. But these are transient (as player moves, those chunks get removed and regenerated fresh with correct neighbors). Acceptable for a clone.

Actually, to minimize this, I could rebuild a chunk's mesh whenever one of its neighbors gains data. But that complicates. Let me instead, in updateChunks, when I generate a new chunk's data, also mark neighboring chunks for rebuild if they already have meshes. That way culling stays correct. Let me add: after generating a chunk, if any neighbor already has a mesh, rebuild that neighbor. This keeps things consistent. It's O(1) per generation. Let me do that.

Actually simpler and robust: whenever we generate data for a chunk, rebuild that chunk's mesh (if neighbors have data) AND rebuild any already-meshed neighbor. But rebuilding meshed neighbors each generation could be expensive if many generations happen. Since max 4 gen/frame and each triggers up to 4 neighbor rebuilds = 16 rebuilds/frame worst case, each rebuild processes up to 20480 blocks. 16*20480 = 327k getBlock calls/frame. Acceptable.

Hmm, but that might exceed "max 2 mesh per frame" for the meshing step. But neighbor rebuilds are separate from the "build meshes for chunks within 4" step. The spec's limits are about the periodic meshing. Rebuilds on edit/generation are separate operations. I think it's fine.

But to keep it simpler and match spec intent, let me do this: 
- Generate data for chunks within radius 5 (max 4/frame) — as spec.
- When generating a chunk, if its 4 orthogonal neighbors all have data, build its mesh (but this competes with the "max 2 mesh/frame" budget). 

Ugh, this is getting complicated. Let me step back and choose a clean approach that satisfies the spec and minimizes artifacts:

Approach: 
- Maintain chunks map.
- Each frame:
  a. Generate block data for up to 4 new chunks within radius 5.
  b. After generating, for each newly generated chunk, if all 4 orthogonal neighbors have data, mark it for mesh building (push to a pending list). Also, if a newly generated chunk is a neighbor of an already-meshed chunk, mark that meshed chunk for rebuild (pending).
  c. Build meshes for up to 2 pending chunks (those within radius 4). 
  d. Remove chunks beyond radius 7.

This keeps culling correct. Pending list can grow but we process 2/frame; backlog handles it. Actually if we only process 2/frame but generate 4/frame each triggering rebuilds, backlog grows unboundedly. 

Let me reconsider. The spec explicitly says: "build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame)". So the spec wants exactly this: 2 meshes/frame for chunks fully surrounded by data. It does NOT ask for rebuild-on-neighbor-generation. So the intended design accepts that a chunk's mesh is built once when it becomes eligible (neighbors have data), and edits trigger explicit rebuilds (including neighbor rebuilds at borders).

The exposed-face-at-boundary artifact arises only for chunks meshed BEFORE their neighbors got data. But per spec, a chunk is only meshed when its 4 neighbors already have data. So when chunk A is meshed, its 4 neighbors have data (but might not have meshes yet). If neighbor B later gets a mesh, B's faces toward A are correct (B checks A's data). But A's faces toward B were computed when A had no mesh-data-dependent... wait A's faces depend on B's DATA (block IDs), not B's mesh. Since B has data (required for A to be meshed), A's faces toward B are correctly culled based on B's block IDs. So NO exposed faces! Because culling uses data, and data is present for all 4 neighbors when A is meshed. 

So the spec's rule (mesh only when 4 neighbors have data) guarantees correct culling using data. The only remaining issue: if B's data changes after A is meshed (e.g., B is edited), A won't reflect it. But edits trigger rebuild of the edited chunk and its bordering neighbors. If A and B are neighbors and B is edited, B's rebuild recomputes B's faces; A's faces toward B are not recomputed → A shows stale. BUT the edit rebuild rebuilds the chunk containing the edited block and its chunk-neighbors. If B is edited and B is a chunk, B's mesh rebuilds. A is a neighbor of B; is A rebuilt? The rebuild function rebuilds the edited block's chunk and, if on border, the adjacent chunk. If B is edited in its interior, only B rebuilds; A (neighbor) doesn't → A's faces toward B stale.

Hmm. So editing inside chunk B won't update A's faces toward B. This is a real staleness bug for adjacent chunks. 

But wait — when we edit a block inside chunk B (not on border), we rebuild B. A (neighbor) has faces toward B that were culled based on B's old data. If B changed a block adjacent to the A-B border, A's face there is now stale (should be culled or shown differently). 

To handle this properly, editing ANY block should rebuild both its chunk and all 4 orthogonal chunk neighbors (since a block change affects the face of the neighbor across the border). The spec says "also the neighbor chunk if the block sits on a chunk border." That implies only rebuild neighbor on border. For interior edits, only the chunk rebuilds. But then neighbor's faces toward edited block are stale.

However, note: the neighbor's face toward the edited block only exists if the neighbor's block across the border is air (so the neighbor exposes a face). If we edit a block deep inside chunk B (far from border), the neighbor A's faces toward B are on A's border side, corresponding to B's border blocks, which we didn't edit. So no staleness for interior edits! Because A's faces toward B correspond to B's border cells (adjacent to the A-B boundary). Editing B's interior doesn't change B's border cells → A's faces remain valid. 

Only when editing a cell adjacent to the A-B border does A's faces become stale. And in that case, the edited cell is on... no, the edited cell is in B adjacent to border but B is still one chunk; the cell is at B's border (local x=15 or 0). That IS a chunk border cell! So "if the block sits on a chunk border" → rebuild neighbor. So the spec's rule handles it: editing a border cell rebuilds the neighbor. Editing interior cell doesn't affect any neighbor's faces. 

So the spec's rebuild rule is actually correct and complete: a block change only affects faces between its chunk and neighbors across the 4 borders, which happens iff the block is on a border (local x∈{0,15} or z∈{0,15}). If on border, rebuild neighbor. If not on any border, only rebuild own chunk. And cross-border faces only exist for border cells. So correctness holds. 

Therefore I don't need rebuild-on-generation. The spec's approach is self-consistent. 

So my plan:
- Pre-generate block data for a region (say radius 3) synchronously at startup for immediate terrain and correct spawn.
- Main loop: generate data (4/frame within radius 5), build meshes (2/frame within radius 4 when 4 neighbors have data), remove beyond radius 7.
- Edits: rebuild chunk + bordering neighbor if on border.

Wait, but pre-generating radius 3 and building meshes for radius 4 requires radius 4 data. At startup I generate radius 3 data. Meshes for chunk (0,0) need neighbors (radius 1) data — which exists (radius 3 generated). Good. So I can build meshes for radius up to 2 (needs radius 3 data). Let me pre-generate radius 3 and build meshes for radius 2. Then main loop continues.

Actually, simplest: at startup, generate data for radius 3 (49 chunks), then build meshes for all chunks within radius 2 (25 chunks) — but that's 25 mesh builds at once, might be heavy but ok (~25 * up to 20480 blocks). Let me just build meshes for radius 2 (25 chunks) at startup. Should be fine (<1s).

Hmm, but 25 meshes each possibly with tens of thousands of triangles. Total triangles maybe 25 * 10000 = 250k triangles. Fine for GPU. Building them takes some CPU (buffer allocation) but one-time. OK.

Actually, let me reduce: pre-generate radius 2 (25 chunks) data, build mesh for radius 1 (9 chunks) + center. Eh, let me just pre-generate radius 3 and build meshes for radius 2. It's a one-time cost. Let me do radius 3 data + radius 2 meshes at startup.

Wait, to build mesh for chunk at radius r, its 4 neighbors (radius r+1) need data. For radius 2 meshes, need radius 3 data. So generate radius 3, mesh radius 2. Good.

Let me set: generateRadius = 3 (data), meshRadius = 2 (initial meshes). Then main loop handles expansion.

Actually, I realize I should double check: does building 25 meshes at startup with the buffer attribute creation cause issues? No. Let me proceed but maybe limit initial meshes to radius 2 (25 chunks). Fine.

Let me reduce initial to radius 2 data generated, radius 1 meshed (9 chunks) to keep startup snappy, and let the loop flesh out. Actually the loop generates data 4/frame and meshes 2/frame, so within ~a few seconds everything near loads. Initial 9 meshes give immediate feedback. Let me pre-generate radius 2 (25 chunks) data and mesh radius 1 (9 chunks). Then loop continues.

Hmm, let me just pre-generate radius 3 data and mesh radius 2. It's fine.

Let me reconsider performance of initial meshing 25 chunks: each chunk iterate 16*16*80=20480 cells, 6 neighbor checks each = ~123k getBlock calls, plus building arrays. 25 chunks → ~3M getBlock calls and array pushes. In JS, ~3M operations ~ tens of ms. Fine.

OK let me finalize and write code.

Let me also double check getBlock for y out of range returns air (0). And y up to 79 inclusive. Block array index = lx + lz*16 + y, with y in 0..79. Max index = 15 + 15*16 + 79 = 15+240+79=334. Array size 16*16*80=20480. Good.

Now, collision uses getBlock for blocks possibly at y=80 (above). getBlock returns 0 for y>79 → air, so no collision above. Good. And y=0 stone → collision at ground. Good.

Let me also handle spawn: after generating radius 3 data, find surface at world (8,8):
```js
let sy = 79;
while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
// sy is top non-air block index
player.set(8, sy + 1, 8);
```
feet at sy+1 stands on top of block sy. Good. But need chunk (0,0) generated (it is, radius 3 includes it). Good.

Now camera initial position: set in loop.

Let me also ensure the player doesn't spawn inside a tree or anything. sy is the top non-air; if there's a tree, sy would be a leaf block and feet would be inside a leaf. Unlikely at (8,8) but possible. To be safe, after finding sy, step up while the cell at feet is solid:
```js
while (sy < 80 && getBlock(8, sy, 8) !== 0) sy++;
player.set(8, sy, 8);
```
Wait start sy = top non-air. If that cell is solid (leaf), we step up until air. Let me do:
```js
let sy = 79;
while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
// now sy is top non-air (solid). Step up to find air above it.
while (sy < 80 && getBlock(8, sy, 8) !== 0) sy++;
player.set(8, sy, 8); // feet at first air
```
After loop, getBlock(8,sy,8)==0 (air). feet at sy stands on sy-1 (solid). Good. Unless sy reached 80 (all solid column) — then feet at 80, but that's above range; player would fall. Edge case, ignore.

Now let me write everything out.

Let me also make the overlay show controls list:
- WASD move
- Mouse look
- Space jump
- Left click break
- Right click place
- 1-7 / wheel select block
- Esc release

Let me write the HTML/CSS.

One more: the crosshair is a small div at center, pointer-events none.

Hotbar styling: fixed bottom center, horizontal row of 7 squares.

Let me write CSS:
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: #000; }
canvas { display: block; }
#overlay {
  position: fixed; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; color: #fff;
  background: rgba(0,0,0,0.6); z-index: 10; font-family: monospace; text-align: center;
}
#overlay h1 { font-size: 48px; margin-bottom: 20px; text-shadow: 2px 2px #000; }
#controls { list-style: none; margin-bottom: 24px; line-height: 1.8; font-size: 15px; }
#play { font-size: 20px; padding: 12px 24px; border: 2px solid #fff; border-radius: 6px; cursor: pointer; }
#crosshair {
  position: fixed; left: 50%; top: 50%; transform: translate(-50%,-50%);
  width: 20px; height: 20px; pointer-events: none; z-index: 5;
}
#crosshair::before, #crosshair::after {
  content: ''; position: absolute; background: #fff;
}
#crosshair::before { left: 9px; top: 2px; width: 2px; height: 16px; }
#crosshair::after { top: 9px; left: 2px; width: 16px; height: 2px; }
#hotbar {
  position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%);
  display: flex; gap: 6px; padding: 6px; background: rgba(0,0,0,0.5);
  border-radius: 8px; z-index: 5; pointer-events: none;
}
.slot {
  width: 44px; height: 44px; border: 2px solid #888; border-radius: 4px;
  position: relative; display: flex; align-items: center; justify-content: center;
  color: #fff; font-family: monospace; font-weight: bold; text-shadow: 1px 1px #000;
}
.slot.selected { border-color: #fff; box-shadow: 0 0 6px #fff; }
.slot .num { position: absolute; top: 1px; left: 3px; font-size: 12px; }
```

Now JS. Let me assemble.

I need to be careful about the `for (const [key, chunk] of chunks)` while deleting. Let me collect keys to delete first, then delete. Safer.

Let me also ensure requestPointerLock works on the canvas. Some browsers require the element to be focusable; canvas is fine.

Let me write the final code.

Also, I should set camera.rotation order and initial yaw/pitch. Initial yaw 0 → looking -Z. Player spawns at (8,?,8) looking -Z. Fine.

Let me also clamp pitch in mousemove.

Let me write cameraDir as a Vector3 reused.

Let me now also reconsider the "eye 1.62" — camera position y = player.y + 1.62. Good.

Let me write it all.

Also need to handle window resize: set camera aspect and renderer size.

Let me also make sure to add camera to scene so getWorldDirection works (needs to be in scene graph). scene.add(camera).

DirectionalLight position: set somewhere high.

Let me write the complete file.

Let me reconsider the fractal normalization: sum of amplitudes. With octaves=4, persistence=0.5: amplitudes 1,0.5,0.25,0.125 sum=1.875. total/maxAmplitude → normalized 0..1. Good.

noise2 returns hash-based 0..1. fractal2 returns 0..1. Good.

Let me double-check hash2 for negative coords: (x|0) handles negatives (bitwise OR with 0 coerces to int32). Multiplication and XOR fine. `(h >>> 0)` converts to unsigned. Good. Deterministic.

Let me verify hash2 produces decent spread. It's a linear hash with xor-shift scramble. Fine for noise.

Now, one concern: `hash2` uses `(x|0) * 374761393`. For x up to ~thousands, product ~ 374761393*4000 ≈ 1.5e12, within 2^53 (~9e15). Sum of two such ~3e12, plus 1e9. Fine, exact. Then xor-shift multiply 1274126177 * 3e12 ≈ 3.8e21 > 2^53 → loses precision but deterministic. Final >>>0 truncates. Acceptable. For determinism it's fine.

Actually wait, precision loss means the same input always gives same (lossy) output — deterministic. Good. Distribution still okay. Fine.

Let me also ensure noise at coords*0.004 etc. These are floats; Math.floor works. Good.

Cave noise noise3 at position*0.09. Good.

Now let me also reconsider tree placement condition "fits inside the chunk": I require lx in [2,13] and lz in [2,13] so the 5x5 canopy fits (indices 0..15, canopy spans lx-2..lx+2, need lx-2>=0 and lx+2<=15 → lx in [2,13]). Good.

Let me write final code now. I'll be thorough.

Let me also add: when placing, ensure the block isn't placed where player stands (overlapsPlayer). Already have.

Also break at y==0 prevented. Good.

Also, when pointer not locked, don't process clicks. Already guarded.

Let me also make sure the contextmenu is suppressed globally.

Let me write it.

Actually, I realize for the raycast, using raycaster.intersectObjects with many small meshes is fine. But performance: chunk meshes could be up to ~radius 4 = 81 chunks, each a mesh. Raycasting against 81 meshes is fine.

Let me also set raycaster.far = 6 and near = 0.01.

Now, the camera direction: getWorldDirection returns a normalized vector pointing forward (into screen, -Z of camera). Good for raycast.

Let me finalize.

Also I want to double check the landing math doesn't jitter. When on ground and moving horizontally, vy accumulates gravity, each frame we try ny = player.y + vy*dt. Since on ground, player.y is resting on top of block (e.g., 6). vy becomes negative each frame (~-0.4/frame). ny = 6 - 0.4 = 5.6. collides? box [5.6, 7.4] vs ground [5,6] (if ground top at 6): overlap → collide. So we land again: upward search from floor(5.6)=5: collides at 5? box[5,6.8] vs [5,6]: overlap → collide. ly=6: box[6,7.8] vs [5,6]: no collision. player.y=6. So player stays at 6, vy resets to 0 each frame. Good, no sinking/jitter. onGround=true set. Good.

But wait, when onGround and we press Space, vy=8.5 jumps. Good.

When walking off a ledge: player at edge, vy negative, ny < player.y, no collision (nothing below), falls. Good.

Now horizontal movement when on ground: after vertical resolved (player.y=6), move X: nx = player.x + mx. If no collision, move. Good.

Edge: walking into a wall. Wall at +x. Press D → mx positive. nx collides → revert (player.x unchanged). Press W → mz positive (forward). Moves forward. So sliding along wall. Good.

Alright, writing final.

Let me also make sure to define blockColors mapping and blockRGB.

Let me also reconsider: the spec says "ONE shared MeshLambertMaterial". Using vertexColors true. Good.

Let me write the complete file now.

Let me carefully write the meshing to avoid building huge arrays when chunk empty. Fine.

Also, I should dispose geometry when removing far chunks and when rebuilding. Done.

Let me also handle the case where buildChunkMesh is called but chunk.data is null (shouldn't happen since we only mesh after data present). Guard anyway.

Let me write.

Also, for the initial pre-gen, I'll generate radius 3 and mesh radius 2.

Let me define a helper to generate radius synchronously:
```js
function pregenerate(radius) {
  for (let dx=-radius; dx<=radius; dx++)
    for (let dz=-radius; dz<=radius; dz++)
      generateChunkData(dx, dz);
}
```
And mesh:
```js
function premesh(radius) {
  for (let dx=-radius; dx<=radius; dx++)
    for (let dz=-radius; dz<=radius; dz++)
      buildChunkMesh(dx, dz);
}
```
But buildChunkMesh requires 4 neighbors have data. For radius 2 meshes, neighbors are radius 3 (data present). Good. For radius 2 border chunks, neighbors at radius 3 have data. Good. So premesh(2) works after pregenerate(3).

Wait, buildChunkMesh doesn't check neighbors; it just builds using getBlock. So it's fine regardless. The neighbor-data requirement is only in the periodic meshing step. For pre-gen I can just build all radius-2 meshes directly. Good.

Let me set pregenerate(3), premesh(2).

Hmm, but premesh(2) builds 25 meshes. Let me reduce to premesh(1) (9 meshes) to keep startup light, since the loop will flesh out. Actually let me do premesh(2) for nicer immediate view. 25 meshes one-time is fine. Let me do radius 2.

Actually, let me reconsider total triangles. Surface blocks: each exposed face up to 6. In a terrain, average exposed faces per block maybe 2-3. Blocks: radius 2 = 25 chunks * 256 surface-ish... Actually only top surface blocks expose top + some sides. Rough estimate: 25 chunks * (16*16) surface blocks * ~3 faces * 6 tris... ~25*256*3*2 = 38k triangles. Fine.

Let me finalize.

Let me write the code now fully.

I'll write it out completely.

Let me make sure about `camera.getWorldDirection` requiring the camera to be added to scene and rotation set. I set rotation in loop before computing direction. Good.

Also, initial frame before any movement: yaw=0, pitch=0, camera looks -Z. Player at spawn. Fine.

Let me also add a subtle: set renderer.setClearColor or scene.background. I set scene.background = 0x87ceeb and fog same. Good.

Now writing.

Let me also ensure the water plane is below terrain generally; at y=14.3. Where terrain < 14.3, water covers. Good.

Also, water plane geometry 400x400 centered at origin, positioned at player. Good.

Let me write the final HTML.

I'll include everything in one script.

Let me write it carefully with correct variable scoping (all top-level in one script, no modules).

Final code:

Let me also double-check the "far 400" and fog 40-110. Chunks at radius 4 ~ 64 blocks, within fog. radius 5 ~80. Good.

Let me write.

Also I should make sure that when pointer is not locked, we still render (so overlay shows over scene, but scene might be blank initially). That's fine.

Also, we should keep rendering animation loop running always (requestAnimationFrame). Yes.

Let me write the full thing.

Let me reconsider the meshing "max 2 per frame" and generation "max 4 per frame" loops with break labels. I'll implement with labeled breaks.

Also removal: iterate chunks, delete those beyond radius 7. Use array of keys.

Let me write.

Also, I realize there might be an issue: when generating data for a chunk, if the player is at the boundary, we generate chunks ahead. Good.

Let me also make sure getBlock handles the case where chunk exists but mesh null — data is what matters. getBlock uses chunk.data. Good.

Now writing final code.

Let me also ensure that after break/place, we update target outline stays. It's updated each frame in updateTarget. Good.

Let me write the complete file now.

Actually, let me reconsider the horizontal movement normalization and speed. speed 5.5 m/s. With dt clamped to 0.1, max step 0.55/frame. Fine.

Let me also make gravity/jump: gravity 25, jump 8.5. With dt~0.016, vy decreases 0.4/frame, jump reaches apex quickly. Good.

Let me finalize and output.

One more consideration: The spec says spawn "above terrain at x=8, z=8". I set feet at sy (first air above surface). That's above terrain. Good. Actually "above terrain" — feet just above surface. Good.

Let me also ensure player starts not inside water. If surface sy < 14, feet at sy (below water). Player stands underwater visually (water plane at 14.3 above head if sy small). That's fine visually; player is at beach/lake bottom. Acceptable.

Alright, final code.

Let me write it all out now, carefully.

I'll produce the single code block.

Let me make sure to include everything and not truncate.

Writing now.

Let me reconsider the outline EdlesGeometry: EdgesGeometry(new BoxGeometry(1.02,...)) gives the 12 edges as a LineSegments. Good. Position at block center.

Let me write.

Also, I want the crosshair and hotbar to be visible only when playing ideally, but showing always is fine. Actually when overlay is up, it covers everything. When playing, crosshair+hotbar visible. Good.

Let me finalize.

Let me write the complete HTML file.

I need to double check: `document.pointerLockElement === canvas` in pointerlockchange. When we call requestPointerLock(), on success pointerlockchange fires with pointerLockElement = canvas. Good. On ESC, pointerLockElement becomes null → show overlay. Good.

Also, some browsers fire pointerlockchange; standard. Good.

Let me also add canvas.tabIndex = 0 so it can receive focus for pointer lock request (some browsers require focus). Add style outline none.

Write now.

Let me also make sure the initial camera is positioned before first render. The loop sets camera.position each frame. First frame sets it. Good.

Also set yaw/pitch from mouse after lock. Initial 0.

Alright.

Let me also reconsider: should movement be disabled when not locked? Yes, only update physics when pointerLocked. Otherwise player falls (vy) — but if not locked, we still run physics? The spec: player spawns and falls due to gravity even before playing? That would drop them into the ground immediately upon load. Actually before pointer lock, we might want the player to settle on the ground. Let me run physics always (so player rests on ground), but only allow look/movement/break/place when locked. Actually if we run gravity always, the player falls and lands at spawn within a fraction of a second, then sits. That's fine — when the overlay is showing, the player is sitting on the ground at spawn. When they click to play, they're already grounded. Good. So run physics always.

But running physics always means when overlay shows (pointer unlocked), player still simulates. That's fine; they sit on ground. And falling below -20 teleports to spawn. Good.

So: always run physics; only apply mouse look and input and break/place when locked.

Let me structure: 
```
if (pointerLocked) { apply look; apply input to mx,mz; }
// gravity + collision always
```
Actually gravity and collision should always run. Input only when locked. Look only when locked.

Let me write:
```js
// always
vy -= 25*dt;
// horizontal target from input (only when locked)
let mx=0, mz=0;
if (pointerLocked) {
  // compute fwd/right from camera
  ...
  // set mx,mz from keys
}
// apply jump if locked and onground
if (pointerLocked && keys['Space'] && onGround) { vy=8.5; onGround=false; }
// collision resolution ...
```

Good.

Now, when not locked, camera still needs a position (from player) for rendering. We set camera.position from player each frame regardless. Good. And camera rotation from yaw/pitch (unchanged when locked off). Fine.

Alright, writing final.

Let me write the whole file now, carefully and completely.

I'll now produce the answer.

Let me also double-check: the directional light — in r128, DirectionalLight intensity is linear (0-1ish). 0.8 fine. Ambient 0.65. Combined base ~1.4 then multiplied by face lighting (0.55-1.0) → effectively 0.87 to 1.4. Fine, bright enough.

Let me write.

Also, I'll set pixel ratio cap to avoid perf issues.

Final code below.

Let me make sure I close all tags and the script.

I'll write it now.

Let me reconsider one more time the meshing eligibility in periodic step: "build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame)". I check 4 orthogonal neighbors have data. Good. Within radius 4. Good.

And generation: "generate block data for all chunks within 5 chunks of the player (max 4 per frame)". Within radius 5, max 4/frame. Good.

Removal: "for chunks farther than 7, remove". radius > 7. Good.

Alright.

Now let me also make sure that when we generate a chunk's data, we then can mesh it next frames once neighbors have data. Since we generate 4/frame and mesh 2/frame, and generation is radius 5 while meshing radius 4, eventually all radius-4 chunks get data then meshed. Good.

Edge: a chunk within radius 4 might not have data yet (generation lagging). Then it won't be meshed until data present. Fine.

OK final code.

Let me write it out fully now. I'll be meticulous.

Let me also add a small instruction that pressing Esc releases pointer (browser native).

Writing now. I'll output the single code block.

Let me make sure the HTML has the canvas with id "game", overlay id "overlay", crosshair id "crosshair", hotbar id "hotbar".

Final.
</think>

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>mc.html</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #000; font-family: monospace; }
  #game { display: block; }
  #overlay {
    position: fixed; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; color: #fff;
    background: rgba(0,0,0,0.65); z-index: 20; text-align: center;
  }
  #overlay h1 { font-size: 52px; letter-spacing: 4px; margin-bottom: 18px; text-shadow: 3px 3px 0 #000; }
  #controls { list-style: none; margin-bottom: 26px; line-height: 1.9; font-size: 15px; color: #ddd; }
  #controls b { color: #fff; }
  #play { font-size: 20px; padding: 12px 26px; border: 3px solid #fff; border-radius: 8px; cursor: pointer; background: rgba(0,0,0,0.4); transition: background .15s; }
  #play:hover { background: rgba(255,255,255,0.15); }
  #crosshair { position: fixed; left: 50%; top: 50%; transform: translate(-50%,-50%); width: 22px; height: 22px; pointer-events: none; z-index: 5; }
  #crosshair::before, #crosshair::after { content: ''; position: absolute; background: rgba(255,255,255,0.85); }
  #crosshair::before { left: 10px; top: 3px; width: 2px; height: 16px; }
  #crosshair::after { top: 10px; left: 3px; width: 16px; height: 2px; }
  #hotbar {
    position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%);
    display: flex; gap: 6px; padding: 6px; background: rgba(0,0,0,0.55);
    border-radius: 8px; z-index: 5; pointer-events: none;
  }
  .slot {
    width: 46px; height: 46px; border: 3px solid #777; border-radius: 5px;
    position: relative; display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: bold; font-size: 13px; text-shadow: 1px 1px 2px #000;
  }
  .slot.selected { border-color: #fff; box-shadow: 0 0 8px 2px rgba(255,255,255,0.9); }
  .slot .num { position: absolute; top: 1px; left: 3px; font-size: 11px; opacity: 0.85; }
</style>
</head>
<body>
  <canvas id="game"></canvas>
  <div id="crosshair"></div>
  <div id="hotbar"></div>
  <div id="overlay">
    <h1>MC</h1>
    <ul id="controls">
      <li><b>WASD</b> — move &nbsp; <b>Mouse</b> — look &nbsp; <b>Space</b> — jump</li>
      <li><b>Left click</b> — break block &nbsp; <b>Right click</b> — place block</li>
      <li><b>1–7</b> or <b>mouse wheel</b> — select block &nbsp; <b>Esc</b> — pause</li>
    </ul>
    <div id="play">Click to play</div>
  </div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  "use strict";

  // ---------- Canvas / Renderer / Scene ----------
  const canvas = document.getElementById("game");
  const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  canvas.tabIndex = 0;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb);
  scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
  camera.rotation.order = "YXZ";
  scene.add(camera);

  const ambient = new THREE.AmbientLight(0xffffff, 0.65);
  scene.add(ambient);
  const sun = new THREE.DirectionalLight(0xffffff, 0.8);
  sun.position.set(0.5, 1, 0.3).normalize().multiplyScalar(100);
  scene.add(sun);

  // ---------- Blocks ----------
  const BLOCK_COLORS = {
    1: 0x4caf50, 2: 0x795548, 3: 0x9e9e9e, 4: 0xe7d9a8,
    5: 0x8d6e63, 6: 0x2e7d32, 7: 0xffffff
  };
  const blockRGB = {};
  for (const id in BLOCK_COLORS) {
    const c = BLOCK_COLORS[id];
    blockRGB[id] = [(c >> 16) & 255, (c >> 8) & 255, c & 255];
  }
  const hotbarBlocks = [1, 2, 3, 4, 5, 6, 7];
  const selected = { value: 0 };

  const sharedMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

  // Face definitions: outward normal, 4 CCW vertices (relative to block origin), light factor
  const FACES = {
    top:    { n: [0, 1, 0],    v: [[0,1,0],[0,1,1],[1,1,1],[1,1,0]], l: 1.0 },
    bottom: { n: [0,-1, 0],    v: [[0,0,1],[0,0,0],[1,0,0],[1,0,1]], l: 0.55 },
    rx:     { n: [1, 0, 0],    v: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]], l: 0.8 },
    lx:     { n: [-1,0, 0],    v: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]], l: 0.8 },
    rz:     { n: [0, 0, 1],    v: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], l: 0.8 },
    bz:     { n: [0, 0,-1],    v: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]], l: 0.8 }
  };

  // ---------- Chunk storage & block helpers ----------
  const CHUNK_SIZE = 16;
  const WORLD_H = 80;
  const chunks = new Map();          // key "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
  const chunkMeshes = [];            // all chunk meshes for raycasting

  function chunkIndex(w) { return Math.floor(w / CHUNK_SIZE); }
  function localCoord(w) { return w - chunkIndex(w) * CHUNK_SIZE; }

  function getBlock(wx, wy, wz) {
    if (wy < 0 || wy > WORLD_H - 1) return 0;
    const cx = chunkIndex(wx), cz = chunkIndex(wz);
    const ch = chunks.get(cx + "," + cz);
    if (!ch || !ch.data) return 0;
    const lx = localCoord(wx), lz = localCoord(wz);
    return ch.data[lx + lz * CHUNK_SIZE + wy];
  }

  function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy > WORLD_H - 1) return;
    const cx = chunkIndex(wx), cz = chunkIndex(wz);
    const ch = chunks.get(cx + "," + cz);
    if (!ch || !ch.data) return;
    const lx = localCoord(wx), lz = localCoord(wz);
    ch.data[lx + lz * CHUNK_SIZE + wy] = id;
  }

  // ---------- Deterministic value noise ----------
  function hash2(x, z) {
    let h = ((x | 0) * 374761393) + ((z | 0) * 668265263) + 1013904223;
    h = (h ^ (h >> 13)) * 1274126177;
    h = h ^ (h >> 16);
    return (h >>> 0) / 4294967296;
  }
  function hash3(x, y, z) {
    let h = ((x | 0) * 374761393) + ((y | 0) * 668265263) + ((z | 0) * 1013904223) + 12345;
    h = (h ^ (h >> 13)) * 1274126177;
    h = h ^ (h >> 16);
    return (h >>> 0) / 4294967296;
  }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function smooth(t) { return t * t * (3 - 2 * t); }

  function noise2(x, z) {
    const xi = Math.floor(x), zi = Math.floor(z);
    const xf = x - xi, zf = z - zi;
    const u = smooth(xf), v = smooth(zf);
    const a = hash2(xi, zi), b = hash2(xi + 1, zi);
    const c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
    return lerp(lerp(a, b, u), lerp(c, d, u), v);
  }
  function noise3(x, y, z) {
    const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    const xf = smooth(x - xi), yf = smooth(y - yi), zf = smooth(z - zi);
    const g = (ix, iy, iz) => hash3(ix, iy, iz);
    const c000 = g(xi, yi, zi),     c100 = g(xi + 1, yi, zi);
    const c010 = g(xi, yi + 1, zi), c110 = g(xi + 1, yi + 1, zi);
    const c001 = g(xi, yi, zi + 1), c101 = g(xi + 1, yi, zi + 1);
    const c011 = g(xi, yi + 1, zi + 1), c111 = g(xi + 1, yi + 1, zi + 1);
    const x00 = lerp(c000, c100, xf),  x10 = lerp(c010, c110, xf);
    const x01 = lerp(c001, c101, xf),  x11 = lerp(c011, c111, xf);
    const y0 = lerp(x00, x10, yf), y1 = lerp(x01, x11, yf);
    return lerp(y0, y1, zf);
  }
  function fractal2(x, z, octaves, persistence) {
    let total = 0, amp = 1, freq = 1, maxA = 0;
    for (let i = 0; i < octaves; i++) {
      total += noise2(x * freq, z * freq) * amp;
      maxA += amp;
      amp *= persistence; freq *= 2;
    }
    return total / maxA;
  }

  // ---------- Terrain generation ----------
  function generateChunkData(cx, cz) {
    const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * WORLD_H);
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      for (let lz = 0; lz < CHUNK_SIZE; lz++) {
        const wx = cx * CHUNK_SIZE + lx;
        const wz = cz * CHUNK_SIZE + lz;
        const m = fractal2(wx * 0.004, wz * 0.004, 4, 0.5);
        const h = fractal2(wx * 0.02, wz * 0.02, 4, 0.5);
        const H = Math.floor(5 + m * m * 58 + h * 10);
        for (let y = 0; y < WORLD_H; y++) {
          let id = 0;
          if (y === 0) id = 3;
          else if (y < H - 3) id = 3;
          else if (y < H) {
            if (H <= 16) id = 4;
            else if (H >= 37) id = 3;
            else id = 2;
          } else if (y === H) {
            if (H >= 46) id = 7;
            else if (H >= 37) id = 3;
            else if (H <= 16) id = 4;
            else id = 1;
          }
          data[lx + lz * CHUNK_SIZE + y] = id;
        }
        // caves
        for (let y = 3; y < H - 2; y++) {
          if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
            data[lx + lz * CHUNK_SIZE + y] = 0;
          }
        }
        // trees on grass
        if (data[lx + lz * CHUNK_SIZE + H] === 1 && hash2(wx, wz) < 0.02 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13) {
          for (let y = H + 1; y <= H + 4; y++) {
            if (y < WORLD_H && data[lx + lz * CHUNK_SIZE + y] === 0) data[lx + lz * CHUNK_SIZE + y] = 5;
          }
          for (let layer = 0; layer < 2; layer++) {
            const y = H + 5 + layer;
            if (y < WORLD_H) {
              for (let dx = -2; dx <= 2; dx++) {
                for (let dz = -2; dz <= 2; dz++) {
                  if (y < WORLD_H && data[lx + lz * CHUNK_SIZE + y] === 0) data[lx + lz * CHUNK_SIZE + y] = 6;
                }
              }
            }
          }
          {
            const y = H + 7;
            if (y < WORLD_H) {
              for (let dx = -1; dx <= 1; dx++) {
                for (let dz = -1; dz <= 1; dz++) {
                  if (y < WORLD_H && data[lx + lz * CHUNK_SIZE + y] === 0) data[lx + lz * CHUNK_SIZE + y] = 6;
                }
              }
            }
          }
          {
            const y = H + 8;
            if (y < WORLD_H && data[lx + lz * CHUNK_SIZE + y] === 0) data[lx + lz * CHUNK_SIZE + y] = 6;
          }
        }
      }
    }
    chunks.set(cx + "," + cz, { data: data, mesh: null });
  }

  // ---------- Meshing ----------
  function buildChunkMesh(cx, cz) {
    const ch = chunks.get(cx + "," + cz);
    if (!ch || !ch.data) return;
    if (ch.mesh) {
      scene.remove(ch.mesh);
      ch.mesh.geometry.dispose();
      const idx = chunkMeshes.indexOf(ch.mesh);
      if (idx >= 0) chunkMeshes.splice(idx, 1);
      ch.mesh = null;
    }
    const data = ch.data;
    const positions = [], normals = [], colors = [], indices = [];
    const baseX = cx * CHUNK_SIZE, baseZ = cz * CHUNK_SIZE;
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      for (let lz = 0; lz < CHUNK_SIZE; lz++) {
        for (let y = 0; y < WORLD_H; y++) {
          const id = data[lx + lz * CHUNK_SIZE + y];
          if (id === 0) continue;
          const wx = baseX + lx, wz = baseZ + lz;
          const rgb = blockRGB[id];
          const neigh = [
            ["top", getBlock(wx, y + 1, wz)],
            ["bottom", getBlock(wx, y - 1, wz)],
            ["rx", getBlock(wx + 1, y, wz)],
            ["lx", getBlock(wx - 1, y, wz)],
            ["rz", getBlock(wx, y, z = wz + 1)],
            ["bz", getBlock(wx, y, wz - 1)]
          ];
          for (let fi = 0; fi < neigh.length; fi++) {
            const fname = neigh[fi][0], other = neigh[fi][1];
            if (other !== 0) continue;
            const F = FACES[fname];
            const i0 = positions.length / 3;
            for (let k = 0; k < 4; k++) {
              const vv = F.v[k];
              positions.push(wx + vv[0], y + vv[1], wz + vv[2]);
              normals.push(F.n[0], F.n[1], F.n[2]);
              colors.push(rgb[0] * F.l, rgb[1] * F.l, rgb[2] * F.l);
            }
            indices.push(i0, i0 + 1, i0 + 2, i0, i0 + 2, i0 + 3);
          }
        }
      }
    }
    if (indices.length === 0) return;
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    geom.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
    geom.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    geom.setIndex(indices);
    const mesh = new THREE.Mesh(geom, sharedMaterial);
    mesh.position.set(0, 0, 0);
    scene.add(mesh);
    ch.mesh = mesh;
    chunkMeshes.push(mesh);
  }

  function rebuildChunkById(cx, cz) {
    const ch = chunks.get(cx + "," + cz);
    if (!ch || !ch.data) return;
    buildChunkMesh(cx, cz);
  }

  function rebuildChunk(wx, wy, wz) {
    const cx = chunkIndex(wx), cz = chunkIndex(wz);
    rebuildChunkById(cx, cz);
    const lx = localCoord(wx), lz = localCoord(wz);
    if (lx === 0) rebuildChunkById(cx - 1, cz);
    if (lx === CHUNK_SIZE - 1) rebuildChunkById(cx + 1, cz);
    if (lz === 0) rebuildChunkById(cx, cz - 1);
    if (lz === CHUNK_SIZE - 1) rebuildChunkById(cx, cz + 1);
  }

  // ---------- World management each frame ----------
  function updateChunks() {
    const pcx = chunkIndex(player.x), pcz = chunkIndex(player.z);

    // generate block data for chunks within radius 5 (max 4/frame)
    let gen = 0, done = false;
    gloop: for (let dx = -5; dx <= 5 && !done; dx++) {
      for (let dz = -5; dz <= 5; dz++) {
        const cx = pcx + dx, cz = pcz + dz;
        const key = cx + "," + cz;
        if (!chunks.has(key)) {
          generateChunkData(cx, cz);
          if (++gen >= 4) { done = true; break gloop; }
        }
      }
    }

    // build meshes for chunks within radius 4 whose 4 orthogonal neighbors have data (max 2/frame)
    let meshCount = 0, mdone = false;
    mloop: for (let dx = -4; dx <= 4 && !mdone; dx++) {
      for (let dz = -4; dz <= 4; dz++) {
        const cx = pcx + dx, cz = pcz + dz;
        const ch = chunks.get(cx + "," + cz);
        if (ch && ch.data && !ch.mesh) {
          const nE = chunks.get((cx + 1) + "," + cz);
          const nW = chunks.get((cx - 1) + "," + cz);
          const nN = chunks.get(cx + "," + (cz + 1));
          const nS = chunks.get(cx + "," + (cz - 1));
          if (nE && nE.data && nW && nW.data && nN && nN.data && nS && nS.data) {
            buildChunkMesh(cx, cz);
            if (++meshCount >= 2) { mdone = true; break mloop; }
          }
        }
      }
    }

    // remove chunks farther than 7
    const removeKeys = [];
    for (const [key, ch] of chunks) {
      const cx = parseInt(key.split(",")[0]), cz = parseInt(key.split(",")[1]);
      if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
        if (ch.mesh) {
          scene.remove(ch.mesh);
          ch.mesh.geometry.dispose();
          const idx = chunkMeshes.indexOf(ch.mesh);
          if (idx >= 0) chunkMeshes.splice(idx, 1);
        }
        removeKeys.push(key);
      }
    }
    for (const k of removeKeys) chunks.delete(k);
  }

  // ---------- Player ----------
  const player = new THREE.Vector3();
  let vy = 0, onGround = false;
  let yaw = 0, pitch = 0;
  const keys = {};
  const spawnY = 40;

  function collides(px, py, pz) {
    const minX = Math.floor(px - 0.3), maxX = Math.floor(px + 0.3);
    const minY = Math.floor(py), maxY = Math.floor(py + 1.8);
    const minZ = Math.floor(pz - 0.3), maxZ = Math.floor(pz + 0.3);
    for (let bx = minX; bx <= maxX; bx++) {
      for (let by = minY; by <= maxY; by++) {
        for (let bz = minZ; bz <= maxZ; bz++) {
          if (getBlock(bx, by, bz) !== 0) return true;
        }
      }
    }
    return false;
  }

  function stepPhysics(dt) {
    vy -= 25 * dt;
    if (vy > 30) vy = 30;

    let mx = 0, mz = 0;
    if (pointerLocked) {
      const fwd = new THREE.Vector3();
      camera.getWorldDirection(fwd);
      fwd.y = 0; fwd.normalize();
      const right = new THREE.Vector3(fwd.z, 0, -fwd.x).normalize();
      if (keys["KeyW"]) { mx += fwd.x; mz += fwd.z; }
      if (keys["KeyS"]) { mx -= fwd.x; mz -= fwd.z; }
      if (keys["KeyD"]) { mx += right.x; mz += right.z; }
      if (keys["KeyA"]) { mx -= right.x; mz -= right.z; }
      const len = Math.hypot(mx, mz);
      if (len > 0) { mx = mx / len * 5.5 * dt; mz = mz / len * 5.5 * dt; }
      if (keys["Space"] && onGround) { vy = 8.5; onGround = false; }
    }

    // Vertical
    const ny = player.y + vy * dt;
    if (!collides(player.x, ny, player.z)) {
      player.y = ny; onGround = false;
    } else {
      if (vy < 0) {
        let ly = Math.floor(ny);
        while (ly < WORLD_H && collides(player.x, ly, player.z)) ly++;
        player.y = ly;
        vy = 0; onGround = true;
      } else {
        let testY = player.y;
        for (let s = 0; s < 40; s++) {
          testY -= 0.1;
          if (testY <= 0) break;
          if (!collides(player.x, testY, player.z)) { player.y = testY; break; }
        }
        vy = 0; onGround = false;
      }
    }

    // Horizontal X
    const nx = player.x + mx;
    if (!collides(nx, player.y, player.z)) player.x = nx;

    // Horizontal Z
    const nz = player.z + mz;
    if (!collides(player.x, player.y, nz)) player.z = nz;

    if (player.y < -20) {
      player.set(8, spawnY, 8);
      vy = 0;
    }
  }

  // ---------- Break / Place / Target ----------
  const outline = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(1.02, 1.02, 1.02)),
    new THREE.LineBasicMaterial({ color: 0x000000 })
  );
  outline.visible = false;
  scene.add(outline);

  const raycaster = new THREE.Raycaster();
  raycaster.near = 0.01;
  raycaster.far = 6;
  const camDir = new THREE.Vector3();
  let targetCell = null, placeCell = null;

  function updateTarget() {
    targetCell = null; placeCell = null;
    camera.getWorldDirection(camDir);
    raycaster.set(camera.position, camDir);
    const hits = raycaster.intersectObjects(chunkMeshes, false);
    if (hits.length > 0) {
      const p = hits[0].point;
      const n = hits[0].face.normal;
      targetCell = [Math.floor(p.x - n.x * 0.5), Math.floor(p.y - n.y * 0.5), Math.floor(p.z - n.z * 0.5)];
      placeCell = [Math.floor(p.x + n.x * 0.5), Math.floor(p.y + n.y * 0.5), Math.floor(p.z + n.z * 0.5)];
      outline.position.set(targetCell[0] + 0.5, targetCell[1] + 0.5, targetCell[2] + 0.5);
      outline.visible = true;
    } else {
      outline.visible = false;
    }
  }

  function overlapsPlayer(cell) {
    const bx = cell[0], by = cell[1], bz = cell[2];
    const minX = player.x - 0.3, maxX = player.x + 0.3;
    const minY = player.y, maxY = player.y + 1.8;
    const minZ = player.z - 0.3, maxZ = player.z + 0.3;
    return !(maxX < bx || minX > bx + 1 || maxY < by || minY > by + 1 || maxZ < bz || minZ > bz + 1);
  }

  function breakTarget() {
    if (!targetCell) return;
    if (targetCell[1] === 0) return;
    setBlock(targetCell[0], targetCell[1], targetCell[2], 0);
    rebuildChunk(targetCell[0], targetCell[1], targetCell[2]);
  }

  function placeTarget() {
    if (!placeCell) return;
    const x = placeCell[0], y = placeCell[1], z = placeCell[2];
    if (y < 0 || y > WORLD_H - 1) return;
    if (getBlock(x, y, z) !== 0) return;
    if (overlapsPlayer(placeCell)) return;
    setBlock(x, y, z, hotbarBlocks[selected.value]);
    rebuildChunk(x, y, z);
  }

  // ---------- Clouds & Water ----------
  const clouds = [];
  for (let i = 0; i < 25; i++) {
    const g = new THREE.Group();
    const parts = 2 + (i % 3);
    for (let j = 0; j < parts; j++) {
      const w = 3 + j * 2.5;
      const m = new THREE.Mesh(
        new THREE.BoxGeometry(w, 1, 3),
        new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.86 })
      );
      m.position.set(j * 3, 0, ((i * 13 + j * 7) % 7) - 3);
      g.add(m);
    }
    g.userData = { speed: 1.4 + (i % 4) * 0.3, relZ: ((i * 61) % 160) - 80 };
    scene.add(g);
    clouds.push(g);
  }

  const water = new THREE.Mesh(
    new THREE.PlaneGeometry(400, 400),
    new THREE.MeshLambertMaterial({ color: 0x2b6fd4, transparent: true, opacity: 0.62 })
  );
  water.rotation.x = -Math.PI / 2;
  scene.add(water);

  function updateClouds(dt) {
    for (const c of clouds) {
      c.userData.relX += c.userData.speed * dt;
      if (c.userData.relX > 80) c.userData.relX -= 160;
      c.position.set(player.x + c.userData.relX, 90, player.z + c.userData.relZ);
    }
  }

  // ---------- Hotbar UI ----------
  const hotbarEl = document.getElementById("hotbar");
  for (let i = 0; i < 7; i++) {
    const slot = document.createElement("div");
    slot.className = "slot";
    slot.style.background = "#" + BLOCK_COLORS[hotbarBlocks[i]].toString(16).padStart(6, "0");
    slot.innerHTML = '<span class="num">' + (i + 1) + '</span>';
    hotbarEl.appendChild(slot);
  }
  function updateHotbar() {
    const slots = hotbarEl.children;
    for (let i = 0; i < slots.length; i++) {
      slots[i].classList.toggle("selected", i === selected.value);
    }
  }
  updateHotbar();

  // ---------- Input / Pointer lock ----------
  const overlay = document.getElementById("overlay");
  let pointerLocked = false;

  overlay.addEventListener("click", function () {
    if (canvas.requestPointerLock) canvas.requestPointerLock();
  });

  document.addEventListener("pointerlockchange", function () {
    pointerLocked = (document.pointerLockElement === canvas);
    overlay.style.display = pointerLocked ? "none" : "flex";
  });

  document.addEventListener("mousemove", function (e) {
    if (!pointerLocked) return;
    yaw -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;
    const lim = Math.PI / 2 - 0.01;
    if (pitch > lim) pitch = lim;
    if (pitch < -lim) pitch = -lim;
  });

  document.addEventListener("mousedown", function (e) {
    if (!pointerLocked) return;
    if (e.button === 0) breakTarget();
    else if (e.button === 2) placeTarget();
  });

  document.addEventListener("contextmenu", function (e) { e.preventDefault(); });

  document.addEventListener("wheel", function (e) {
    if (!pointerLocked) return;
    selected.value = (selected.value + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
    updateHotbar();
  }, { passive: true });

  document.addEventListener("keydown", function (e) {
    if (e.key >= "1" && e.key <= "7") { selected.value = parseInt(e.key) - 1; updateHotbar(); }
    keys[e.code] = true;
  });
  document.addEventListener("keyup", function (e) { keys[e.code] = false; });

  window.addEventListener("resize", function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // ---------- Init ----------
  function init() {
    // generate block data around spawn
    for (let dx = -3; dx <= 3; dx++) {
      for (let dz = -3; dz <= 3; dz++) generateChunkData(dx, dz);
    }
    // find surface at spawn column (world 8,8)
    let sy = 79;
    while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
    while (sy < WORLD_H && getBlock(8, sy, 8) !== 0) sy++;
    player.set(8, sy, 8);
    spawnY_set = sy;

    // build initial meshes (radius 2)
    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) buildChunkMesh(dx, dz);
    }
  }
  let spawnY_set = 40;
  init();

  // ---------- Main loop ----------
  let last = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    const now = performance.now();
    let dt = (now - last) / 1000;
    last = now;
    if (dt > 0.1) dt = 0.1;
    if (dt < 0) dt = 0;

    // camera orientation
    camera.rotation.set(pitch, yaw, 0, "YXZ");

    stepPhysics(dt);

    updateChunks();

    if (pointerLocked) updateTarget();

    updateClouds(dt);
    water.position.set(player.x, 14.3, player.z);

    camera.position.set(player.x, player.y + 1.62, player.z);

    renderer.render(scene, camera);
  }
  animate();
})();
</script>
</body>
</html>
```