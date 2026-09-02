Let me carefully build this Minecraft clone in a single HTML file. Let me go through the spec methodically.

I need to implement:

1. **Three.js setup** - r128 from CDN, global THREE object
2. **Blocks** - 7 types with specific colors, one shared MeshLambertMaterial, fake lighting (top 1.0, sides 0.8, bottom 0.55)
3. **Chunks** - 16x16 columns, 80 high, stored in Map keyed "cx,cz", each with Uint8Array + mesh
4. **Global read/write helpers** using chunk = floor(world/16)
5. **Meshing** - one BufferGeometry per chunk, face culling against neighbors
6. **Terrain generation** - value noise, fractal noise, caves, trees
7. **Player & controls** - FPS camera, pointer lock, gravity, collision
8. **Break & place** - raycasting, wireframe outline
9. **Hotbar** - 7 slots
10. **Sky, clouds, water**
11. **UI** - start overlay

Let me write this carefully.

### Block definitions

```js
const BLOCKS = [
  { id: 0, color: 0x000000 }, // air
  { id: 1, color: 0x4caf50 }, // grass
  { id: 2, color: 0x795548 }, // dirt
  { id: 3, color: 0x9e9e9e }, // stone
  { id: 4, color: 0xe7d9a8 }, // sand
  { id: 5, color: 0x8d6e63 }, // wood
  { id: 6, color: 0x2e7d32 }, // leaves
  { id: 7, color: 0xffffff }  // snow
];
```

### Value noise

Need an integer-coordinate hash giving 0-1, mixing large prime multipliers and xor-shifts.

```js
function hash(ix, iy) {
  let h = ix * 374761393 + iy * 668265263; // large primes
  h = (h ^ (h >>> 13)) >>> 0; // xor-shift
  h = (h * 1274126177) >>> 0; // multiply
  return ((h >>> 0) % 1000000007) / 1000000007; // normalize 0-1
}
```

Hmm, let me think about the hash more carefully. I want deterministic 0-1 values.

```js
function hash2(ix, iy) {
  let h = (ix * 374761393 + iy * 668265263) | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  h = (h * 0x45d9f3b) >>> 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```

That gives a good hash. Bilinear interpolation for smoothing.

Smoothstep: `t*t*(3-2t)`.

Bilinear noise:
```js
function noise2(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf*xf*(3-2*xf);
  const v = yf*yf*(3-2*yf);
  const a = hash2(xi, yi);
  const b = hash2(xi+1, yi);
  const c = hash2(xi, yi+1);
  const d = hash2(xi+1, yi+1);
  const top = a + (b - a) * u;
  const bot = c + (d - c) * u;
  return top + (bot - top) * v;
}
```

Fractal noise with 4 octaves:
```js
function fractal2(x, y) {
  let amp = 1, freq = 1, sum = 0;
  for (let i = 0; i < 4; i++) {
    sum += amp * noise2(x * freq, y * freq);
    freq *= 2;
    amp *= 0.5;
  }
  return sum; // roughly 0-1 but sum of amps is 1+0.5+0.25+0.125 = 1.875
}
```

Wait, I should normalize. Actually the spec says "4 octaves combined into fractal noise". Let me normalize so result is in [0,1]. Actually for terrain generation I'll just use it and map appropriately. Let me normalize by dividing by sum of amplitudes.

Actually, let me reconsider. The column height formula is:
`H = floor(5 + m*m*58 + h*10)`

where m = fractal at coords*0.004 (low frequency, big features), h = fractal at coords*0.02 (higher frequency detail).

If m is in [0,1], then m*m*58 ranges 0-58, plus 5 gives 5-63. Plus h*10 where h in [0,1] gives 0-10. So H ranges roughly 5-73. That's within 0-79. Good.

But if fractal isn't normalized, m could be up to 1.875, m*m*58 would be huge. So I need to normalize fractal to [0,1].

Let me normalize: divide by total amplitude.

```js
function fractal2(x, y) {
  let amp = 1, freq = 1, sum = 0, total = 0;
  for (let i = 0; i < 4; i++) {
    sum += amp * noise2(x * freq, y * freq);
    total += amp;
    freq *= 2;
    amp *= 0.5;
  }
  return sum / total;
}
```

Now for the fractal, since noise2 is in [0,1], sum/total is in [0,1]. Good.

For 3D cave noise:
```js
function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = xf*xf*(3-2*xf);
  const v = yf*yf*(3-2*yf);
  const w = zf*zf*(3-2*zf);
  // 8 corners
  const n000 = hash3(xi, yi, zi);
  const n100 = hash3(xi+1, yi, zi);
  ...
}
```

hash3:
```js
function hash3(ix, iy, iz) {
  let h = (ix * 374761393 + iy * 668265263 + iz * 0x51ea7c93) | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  h = (h * 0x45d9f3b) >>> 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```

Bilinear in 3D:
```js
function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = xf*xf*(3-2*xf);
  const v = yf*yf*(3-2*yf);
  const w = zf*zf*(3-2*zf);
  const c = [
    hash3(xi, yi, zi), hash3(xi+1, yi, zi),
    hash3(xi+1, yi, zi+1), hash3(xi, yi, zi+1),
    hash3(xi, yi+1, zi), hash3(xi+1, yi+1, zi),
    hash3(xi+1, yi+1, zi+1), hash3(xi, yi+1, zi+1)
  ];
  const x00 = c[0] + (c[1]-c[0])*u;
  const x10 = c[2] + (c[3]-c[2])*u;
  const x01 = c[4] + (c[5]-c[4])*u;
  const x11 = c[6] + (c[7]-c[6])*u;
  const xy0 = x00 + (x10-x00)*v;
  const xy1 = x01 + (x11-x01)*v;
  return xy0 + (xy1-xy0)*w;
}
```

Hmm, I need to be careful with the corner ordering. Let me define corners consistently. Let me index as [dx, dy, dz] where dx,dy,dz ∈ {0,1}.

index = dx*4 + dy*2 + dz.

- c[0] = (0,0,0)
- c[1] = (1,0,0)
- c[2] = (0,1,0)
- c[3] = (1,1,0)
- c[4] = (0,0,1)
- c[5] = (1,0,1)
- c[6] = (0,1,1)
- c[7] = (1,1,1)

Then interpolate along x first:
```
tx0 = c[0] + (c[1]-c[0])*u   // (0..1, 0, 0)
tx1 = c[2] + (c[3]-c[2])*u   // (0..1, 1, 0)
tx2 = c[4] + (c[5]-c[4])*u   // (0..1, 0, 1)
tx3 = c[6] + (c[7]-c[6])*u   // (0..1, 1, 1)
```
Then along y:
```
ty0 = tx0 + (tx1-tx0)*v  // (0..1, 0..1, 0)
ty1 = tx2 + (tx3-tx2)*v  // (0..1, 0..1, 1)
```
Then along z:
```
result = ty0 + (ty1-ty0)*w
```

Good, that's cleaner.

### Chunk storage

```js
const CHUNK_SIZE = 16;
const CHUNK_HEIGHT = 80;
const chunks = new Map(); // key "cx,cz" -> { data: Uint8Array, mesh: Mesh }
```

Block accessors:
```js
function chunkIndex(world) {
  return Math.floor(world / CHUNK_SIZE);
}
function localIndex(world) {
  return world - chunkIndex(world) * CHUNK_SIZE;
}
```

Global read:
```js
function getBlock(x, y, z) {
  if (y < 0 || y >= CHUNK_HEIGHT) return 0;
  const cx = chunkIndex(x);
  const cz = chunkIndex(z);
  const key = cx + ',' + cz;
  const c = chunks.get(key);
  if (!c) return 0;
  const lx = localIndex(x);
  const lz = localIndex(z);
  return c.data[lz * CHUNK_SIZE + lx] ... 
}
```

Wait, need to decide the layout. data is Uint8Array of size 16*16*80. Let me index as `data[y * 16*16 + z*16 + x]` or `data[(z*16+x)*80 + y]`. Either works. Let me use `data[(z * CHUNK_SIZE + x) * CHUNK_HEIGHT + y]`.

Actually, let me think about which is more natural for generation and meshing. During generation I iterate over columns (x,z) and fill heights y. During meshing I iterate all blocks. Let me use index = (z * 16 + x) * 80 + y. Hmm, that has good locality per column but meshing iterates all. Let me just pick `(x + z*16)*CHUNK_HEIGHT + y`.

Let me define:
```js
function idx(x, y, z) {
  return (x + z * CHUNK_SIZE) * CHUNK_HEIGHT + y;
}
```

Global read:
```js
function getBlock(x, y, z) {
  if (y < 0 || y >= CHUNK_HEIGHT) return 0;
  const cx = chunkIndex(x);
  const cz = chunkIndex(z);
  const c = chunks.get(cx + ',' + cz);
  if (!c) return 0;
  return c.data[idx(localIndex(x), y, localIndex(z))];
}
```

Global write (for placing/breaking):
```js
function setBlock(x, y, z, id) {
  if (y < 0 || y >= CHUNK_HEIGHT) return;
  const cx = chunkIndex(x);
  const cz = chunkIndex(z);
  const c = chunks.get(cx + ',' + cz);
  if (!c) return;
  c.data[idx(localIndex(x), y, localIndex(z))] = id;
}
```

Note: y=0 is unbreakable stone, so breaking at y=0 should be prevented.

### Terrain generation

```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      const wx = cx * CHUNK_SIZE + lx;
      const wz = cz * CHUNK_SIZE + lz;
      const m = fractal2(wx * 0.004, wz * 0.004);
      const h = fractal2(wx * 0.02, wz * 0.02);
      const H = Math.floor(5 + m*m*58 + h*10);
      // fill
      for (let y = 0; y < H; y++) {
        let id;
        if (y === 0) id = 3; // unbreakable stone
        else if (y < H - 3) id = 3; // stone
        else if (y < H - 0) {
          // top 3 layers
          if (H <= 16) id = 4; // sand
          else if (H >= 37) id = 3; // stone
          else id = 2; // dirt
        }
        // surface layer handled separately below
        ...
      }
    }
  }
}
```

Wait, let me re-read the fill spec:

"Column fill: y 0 = unbreakable stone; below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

So:
- y = 0: stone (unbreakable)
- y < H-3: stone
- the 3 layers under the surface: dirt (or sand if H<=16, stone if H>=37)
- surface (top layer): snow if H>=46, stone if H>=37, sand if H<=16, else grass

So the top 3 blocks (at H-3, H-2, H-1) are the "under surface" layers, and block at H is the surface.

Wait, "the 3 layers under the surface" means blocks at H-3, H-2, H-1. And surface is at H.

Let me structure:
```js
for (let y = 0; y < H; y++) {
  let id;
  if (y === 0) {
    id = 3;
  } else if (y < H - 3) {
    id = 3;
  } else if (y < H) {
    // 3 layers under surface
    if (H <= 16) id = 4;
    else if (H >= 37) id = 3;
    else id = 2;
  }
  data[idx(lx, y, lz)] = id;
}
// surface
{
  let id;
  if (H >= 46) id = 7; // snow
  else if (H >= 37) id = 3; // stone
  else if (H <= 16) id = 4; // sand
  else id = 1; // grass
  data[idx(lx, H - 1, lz)] = id;
}
```

Wait, but the surface is at y = H-1 (since we fill y from 0 to H-1). Let me reconsider. If H is the height, we fill blocks at y = 0, 1, ..., H-1. So the surface is at y = H-1, and the 3 layers under surface are at y = H-4, H-3, H-2.

Hmm wait. Let me reconsider what "height H" means. "H = floor(...)". Then "surface = ...". The surface block is at the top. If we have H blocks filled from y=0, they occupy y=0..H-1, and the top surface is at y=H-1.

But actually maybe H represents the y-coordinate of the surface. Let me think... "below H−3 stone" suggests stone up to y < H-3. "the 3 layers under the surface" — if surface is at H-1, then 3 layers under are H-4, H-3, H-2. Then "below H-3 stone" would conflict.

Let me reconsider. Perhaps H is the surface height (the y of the topmost surface block). Then:
- Surface at y = H.
- 3 layers under surface: H-1, H-2, H-3.
- Below H-3: stone (y < H-3).
- y = 0: stone.

So we fill y = 0 to H. That means H+1 blocks. Let me use that interpretation:

Fill blocks from y=0 to y=H inclusive (so H+1 blocks, surface at H).
- y === 0: stone
- y < H - 3: stone
- H-3 <= y < H (the 3 layers under surface): dirt/sand/stone
- y === H: surface (snow/stone/sand/grass)

Wait but that's 3 layers under surface (H-3, H-2, H-1) plus surface (H). That's 4 blocks total for the top. "the 3 layers under the surface" + surface = 4 blocks. Yes.

So:
```js
for (let y = 0; y <= H; y++) {
  let id;
  if (y === 0) {
    id = 3;
  } else if (y < H - 3) {
    id = 3;
  } else if (y < H) {
    // 3 layers under surface: H-3, H-2, H-1
    if (H <= 16) id = 4;
    else if (H >= 37) id = 3;
    else id = 2;
  } else {
    // surface at y == H
    if (H >= 46) id = 7;
    else if (H >= 37) id = 3;
    else if (H <= 16) id = 4;
    else id = 1;
  }
  data[idx(lx, y, lz)] = id;
}
```

This seems consistent. H ranges ~5 to ~73. Surface at y=H. For H=5, surface at 5, layers under at 2,3,4. Fine.

Hmm, but wait: if H <= 16, then H-3 could be negative or small. E.g., H=16: H-3=13, layers under at 13,14,15, surface at 16. That's fine, all positive.

If H < 3, H-3 negative. But H min is 5 (from formula, since m*m*58 >= 0 and h*10 >= 0, plus 5). Actually minimum could be lower if... no, m and h are in [0,1], so m*m*58 >= 0, h*10 >= 0, so H >= 5. Good. Max: m=1, h=1: 5 + 58 + 10 = 73. Good, within 80.

Actually wait, m*m where m up to 1 gives up to 1, times 58 = 58. Plus 5 = 63. Plus h*10 up to 10 = 73. Yes max 73. Min 5. Good.

### Caves

"for y between 3 and H−2, if 3D noise at position*0.09 exceeds 0.67, set air."

```js
for (let y = 3; y < H - 2; y++) {
  if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
    data[idx(lx, y, lz)] = 0;
  }
}
```

Note: this could turn the surface into air if H is small, but since y starts at 3 and we only go to H-2, and surface is at H. If caves carve near the surface it might create holes. That's acceptable for this spec. Actually, we should be careful — caves could hollow out below the surface creating caverns open to sky. That's fine, it's a feature.

But we should make sure we don't carve the surface block itself. y goes from 3 to H-2 inclusive (y < H-2 means up to H-3). Surface is at H. So there's a gap of H-(H-3)=3 blocks between last cave layer and surface. Good, surface won't be carved. Actually y < H-2 means y max = H-3. Surface at H. So blocks H-2, H-1, H are never carved. Good.

Wait, but also y=0 is stone and we carve from y=3. So y=1,2 remain stone. Good.

### Trees

"Trees: on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

Per-column hash: need a deterministic hash for column (wx, wz). Reuse hash2 but maybe with different seed.

```js
function columnHash(wx, wz) {
  // returns 0-1
  let h = (wx * 374761393 + wz * 668265263 + 12345) | 0;
  h = (h ^ (h >>> 16)) >>> 0;
  h = (h * 0x45d9f3b) >>> 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967296;
}
```

Tree placement:
```js
// after terrain and caves
if (surfaceId === 1 /* grass */) {
  const th = columnHash(wx, wz);
  if (th < 0.02) {
    // check trunk fits inside chunk
    // trunk height 4, from y=H+1 to y=H+4
    // check within chunk bounds (y < 80)
    if (H + 4 < CHUNK_HEIGHT) {
      // place wood
      for (let y = H + 1; y <= H + 4; y++) {
        data[idx(lx, y, lz)] = 5;
      }
      // leaves
      // 5x5 layer twice (at y=H+5, H+6), then 3x3 (y=H+7), then 1 on top (y=H+8)
      // "only into air"
      ...
    }
  }
}
```

Wait, "trunk fits inside the chunk" — the chunk is 80 high. Trunk goes from H+1 to H+4. Leaves extend to H+8. Need to ensure leaves fit within height 80. Also need to ensure leaves don't extend beyond chunk horizontally? The tree is at column (lx, lz), leaves 5x5 centered... hmm. A 5x5 layer centered on the trunk would extend from lx-2 to lx+2. If lx is near edge (0,1,14,15), leaves would go outside the chunk. 

The spec says "the trunk fits inside the chunk". Let me interpret this as checking that the tree fits within the chunk's horizontal bounds too, OR just that it doesn't exceed vertical bounds. To be safe and avoid writing outside the Uint8Array, I need to check horizontal bounds when placing leaves.

Let me handle leaf placement with bounds checking: only place leaf if the local x,z is within [0,15] and y within [0,79].

Actually, the concern about leaves going to neighboring chunks: if a tree is at the edge, leaves could go into the neighbor chunk. But since we check "trunk fits inside the chunk", maybe we just require the trunk (which is at the column) to fit, and accept that leaves might occasionally cross boundaries. But that would be a bug (writing to wrong chunk). 

Hmm, but leaves are placed in the same column's data. If I clamp leaf positions to within [0,15] for x and z, then leaves never leave the chunk. But a 5x5 centered at lx=0 would need lx=-2..2, clamped to 0..2. That distorts the tree but keeps it in-chunk. Alternatively, only place trees where the full 5x5 fits: lx in [2,13], lz in [2,13]. But spec says "trunk fits inside the chunk", suggesting just the trunk (single column) needs to fit, which always fits horizontally since it's at (lx,lz).

I think the cleanest interpretation: the trunk is a single column, so it always fits horizontally. "Fits inside the chunk" likely refers to the vertical extent (trunk + leaves must be within height 80). Let me check H+8 < 80. Since H max is 73, H+8 = 81 > 80. So some trees would exceed. Need to guard.

Let me just guard: only place tree if H + 8 < CHUNK_HEIGHT (so leaves top at H+8 <= 79). Actually leaves top at H+8, need H+8 <= 79, i.e., H <= 71. Let me check `H + 8 < CHUNK_HEIGHT` → H+8 <= 79 → H <= 71. Hmm, but if H=72 or 73, tree won't place. That's fine, rare.

Actually, let me reconsider. Let me place leaves with bounds checking on both horizontal and vertical, and only place if trunk top (H+4) < 80. For leaves, place only within [0,15]x[0,15]x[0,79]. This handles edges gracefully.

But wait — if leaves get clipped at chunk edges, and the neighbor chunk generates its own terrain, there might be a mismatch (leaves from our chunk appearing in neighbor's air space but neighbor doesn't know). Actually no — each chunk stores its own blocks. If our chunk places leaves at local x=0..15, those are stored in our chunk's data. The neighbor chunk has its own data. When we mesh our chunk, we render its blocks including clipped leaves. When we mesh the neighbor, we render its blocks. The leaves that would have extended beyond our chunk just don't exist in our chunk. There's no cross-chunk leaf writing. So no mismatch, just truncated trees near edges. Acceptable.

Actually, to keep it clean, let me require the tree to fit within the chunk horizontally too. But the spec explicitly says "trunk fits inside the chunk", implying only the trunk. I'll go with: place trunk if it fits vertically, and place leaves with per-cell bounds checking (skip cells outside [0,15]x[0,15]x[0,79]).

Hmm, actually, let me reconsider whether leaves should be allowed to cross chunk boundaries. In a real Minecraft, trees can cross chunk boundaries and the blocks are stored per-chunk. So a tree at a chunk boundary would have its leaves split across two chunks. That's fine and realistic. But for simplicity and to avoid bugs, I'll clip to chunk bounds. Since trees are rare (2% chance) and clipping is minor, it's fine.

Let me define leaf placement:

Trunk: y = H+1 to H+4, at (lx, lz), block 5 (wood).

Leaves:
- Layer 1: y = H+5, 5x5 area: lx-2..lx+2, lz-2..lz+2
- Layer 2: y = H+6, 5x5 area
- Layer 3: y = H+7, 3x3 area: lx-1..lx+1, lz-1..lz+1
- Layer 4: y = H+8, 1x1 at (lx, lz)

"only into air" — only place leaf block if the target cell is currently air (0).

Let me write a helper:
```js
function placeLeaf(data, lx, ly, lz, id) {
  if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE) return;
  if (ly < 0 || ly >= CHUNK_HEIGHT) return;
  if (data[idx(lx, ly, lz)] === 0) data[idx(lx, ly, lz)] = id;
}
```

Then:
```js
for (let dx = -2; dx <= 2; dx++) {
  for (let dz = -2; dz <= 2; dz++) {
    placeLeaf(data, lx + dx, H + 5, lz + dz, 6);
    placeLeaf(data, lx + dx, H + 6, lz + dz, 6);
  }
}
for (let dx = -1; dx <= 1; dx++) {
  for (let dz = -1; dz <= 1; dz++) {
    placeLeaf(data, lx + dx, H + 7, lz + dz, 6);
  }
}
placeLeaf(data, lx, H + 8, lz, 6);
```

Good.

### Meshing

For each chunk, build a BufferGeometry. Loop all non-air blocks, for each of 6 directions check neighbor via getBlock; if air, add face.

Face definitions: for each direction, 4 vertices (CCW when viewed from outside), normal, and per-vertex colors based on face type.

Let me define the 6 faces with their vertices and normals. Using unit cube at (x,y,z) to (x+1,y+1,z+1).

Directions:
- +X (right): normal (1,0,0). Face vertices: (x+1,y,z),(x+1,y+1,z),(x+1,y+1,z+1),(x+1,y,z+1). Winding CCW from outside (+X looking toward -X)... let me be careful.

Let me define standard cube faces. I'll use the convention that vertices are listed counterclockwise when viewed from the outside (looking in the direction of the normal).

For a cube with corner (x,y,z):

Top (+Y): normal (0,1,0)
vertices: (x,y+1,z+1), (x,y+1,z), (x+1,y+1,z), (x+1,y+1,z+1)
Hmm let me just pick a consistent winding.

Actually, let me use a well-known approach. Define faces as arrays of 4 relative vertex offsets and a normal. The two triangles are (0,1,2) and (0,2,3).

Let me define:

```
const FACES = [
  // +X
  { n: [1,0,0], v: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  // -X
  { n: [-1,0,0], v: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  // +Y (top)
  { n: [0,1,0], v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  // -Y (bottom)
  { n: [0,-1,0], v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  // +Z
  { n: [0,0,1], v: [[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
  // -Z
  { n: [0,0,-1], v: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]] },
];
```

I need to verify winding gives outward-facing normals with the cross product. But honestly, for a Lambert material with no backface culling, winding doesn't matter much for lighting (Lambert uses dot(normal, lightDir)). But for correctness of normals pointing outward, let me just make sure normals are correct. Winding affects which side is "front", but since we don't cull backfaces, it doesn't visually matter. However, the normal direction matters for fake lighting? No — the fake lighting is determined by face TYPE (top/side/bottom), not the geometric normal. So I assign colors based on face type regardless.

Actually, let me reconsider the fake lighting. "multiply the block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms." So top faces (normal +Y) get 1.0, side faces (±X, ±Z) get 0.8, bottom faces (normal -Y) get 0.55. This is applied per-face. So when adding a face, I compute color = baseColor * multiplier based on which face.

So for each face direction, I know its type:
- +Y: top (1.0)
- -Y: bottom (0.55)
- +X, -X, +Z, -Z: side (0.8)

Now, the color is stored per-vertex in the buffer. All 4 vertices of a face get the same color.

Let me now write the meshing function:

```js
function buildChunkMesh(cx, cz) {
  const c = chunks.get(cx + ',' + cz);
  if (!c) return null;
  const positions = [];
  const normals = [];
  const colors = [];
  const wx0 = cx * CHUNK_SIZE;
  const wz0 = cz * CHUNK_SIZE;
  
  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      for (let y = 0; y < CHUNK_HEIGHT; y++) {
        const id = c.data[idx(lx, y, lz)];
        if (id === 0) continue;
        const wx = wx0 + lx;
        const wz = wz0 + lz;
        const base = BLOCKS[id].color;
        const br = (base >> 16) & 255;
        const bg = (base >> 8) & 255;
        const bb = base & 255;
        for (let f = 0; f < 6; f++) {
          const face = FACES[f];
          const nx = wx + face.n[0];
          const ny = y + face.n[1];
          const nz = wz + face.n[2];
          if (getBlock(nx, ny, nz) !== 0) continue; // neighbor solid
          // determine multiplier
          let mult;
          if (face.n[1] === 1) mult = 1.0;
          else if (face.n[1] === -1) mult = 0.55;
          else mult = 0.8;
          const cr = br * mult, cg = bg * mult, cb = bb * mult;
          // add 4 vertices
          for (let i = 0; i < 4; i++) {
            const vo = face.v[i];
            positions.push(wx + vo[0], y + vo[1], wz + vo[2]);
            normals.push(face.n[0], face.n[1], face.n[2]);
            colors.push(cr, cg, cb);
          }
        }
      }
    }
  }
  
  const geom = new BufferGeometry();
  geom.setAttribute('position', new Float32BufferAttribute(positions, 3));
  geom.setAttribute('normal', new Float32BufferAttribute(normals, 3));
  geom.setAttribute('color', new Float32BufferAttribute(colors, 3));
  return geom;
}
```

Wait, the spec says "keep the mesh at the origin." Hmm. "Use world coordinates for vertices and keep the mesh at the origin." 

I think this means: the geometry vertices are in world coordinates, but the mesh object's position is set to the chunk's origin (cx*16, 0, cz*16)? Or the mesh is positioned at chunk origin and vertices are local?

Re-reading: "Use world coordinates for vertices and keep the mesh at the origin." This is a bit contradictory. Let me interpret: vertices are in world coordinates (absolute), and the mesh's position is set to (cx*16, 0, cz*16) so that... no.

Hmm. Actually I think the intended meaning is: store vertices in world coordinates, and position the mesh at the chunk origin (cx*16, 0, cz*16) — but then vertices would be double-offset.

Wait, "keep the mesh at the origin" might mean keep the mesh object's position at origin (0,0,0) and put world coordinates directly in the geometry. That way raycasting uses world coordinates directly. That makes sense for raycasting! Because the raycast produces world-space hit points, and we compare against block positions in world space.

So: geometry vertices in world coordinates, mesh.position = (0,0,0). Then the mesh is at world position cx*16..cx*16+16 etc.

But then for raycasting, we raycast against all chunk meshes in world space. The hit point is in world coordinates. We compute target = floor(hit - normal*0.5) in world coords. Good.

Alternatively, position mesh at chunk origin and use local coordinates. Both work for raycasting as long as consistent. The spec explicitly says world coordinates for vertices and mesh at origin, so let me do that: geometry in world coordinates, mesh.position stays at (0,0,0).

Hmm wait, but that's slightly unusual. Let me re-read once more: "loop all non-air blocks, and for each of the 6 sides check the neighbor with the global read helper; if it is air, add that face (2 triangles) to flat position/normal/color arrays. Use world coordinates for vertices and keep the mesh at the origin."

OK so: vertices in world coordinates. Mesh at origin (position 0,0,0). This is clean for raycasting. Let me go with that. So when building the mesh, I use absolute world coordinates for vertices, and don't translate the mesh.

Good, my buildChunkMesh above uses world coordinates (wx, wz, y) directly. 

### Chunk update loop

Each frame:
- Determine player's chunk (px, pz).
- Generate block data for chunks within 5 chunks of player (max 4 per frame).
- Build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame).
- For chunks farther than 7, remove mesh, dispose geometry, delete entry.

Let me implement a chunk manager that tracks generation state.

For each chunk, I need to track:
- Whether data is generated.
- Whether mesh is built.

Let me store on the chunk object: `{ data: Uint8Array|null, mesh: Mesh|null, genOrder: number }`.

Actually, let me maintain a list of chunks to process. Let me do this:

```js
function updateChunks() {
  const pcx = chunkIndex(player.x);
  const pcz = chunkIndex(player.z);
  
  // 1. Generate data for chunks within 5 (max 4/frame)
  let genCount = 0;
  for (let dz = -5; dz <= 5 && genCount < 4; dz++) {
    for (let dx = -5; dx <= 5; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx + ',' + cz;
      const c = chunks.get(key);
      if (c && c.data) continue; // already generated
      if (genCount >= 4) break;
      const data = generateChunkData(cx, cz);
      if (!c) {
        const newObj = { data: data, mesh: null };
        chunks.set(key, newObj);
      } else {
        c.data = data;
      }
      genCount++;
    }
  }
  
  // 2. Build meshes for chunks within 4 whose 4 neighbors have data (max 2/frame)
  let meshCount = 0;
  for (let dz = -4; dz <= 4 && meshCount < 2; dz++) {
    for (let dx = -4; dx <= 4; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx + ',' + cz;
      const c = chunks.get(key);
      if (!c || !c.data) continue;
      if (c.mesh) continue; // already meshed
      // check 4 neighbors (N,S,E,W) have data
      if (!chunkHasData(cx+1,cz) || !chunkHasData(cx-1,cz) ||
          !chunkHasData(cx,cz+1) || !chunkHasData(cx,cz-1)) continue;
      const geom = buildChunkMesh(cx, cz);
      const mesh = new Mesh(geom, material);
      mesh.position.set(0,0,0);
      c.mesh = mesh;
      scene.add(mesh);
      chunkMeshes.push(mesh); // for raycasting
      meshCount++;
    }
  }
  
  // 3. Remove chunks farther than 7
  for (const [key, c] of chunks) {
    const parts = key.split(',');
    const cx = parseInt(parts[0]), cz = parseInt(parts[1]);
    if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
      if (c.mesh) {
        scene.remove(c.mesh);
        c.mesh.geometry.dispose();
        const i = chunkMeshes.indexOf(c.mesh);
        if (i >= 0) chunkMeshes.splice(i, 1);
      }
      chunks.delete(key);
    }
  }
}
```

Where chunkHasData checks if a chunk exists and has data:
```js
function chunkHasData(cx, cz) {
  const c = chunks.get(cx + ',' + cz);
  return !!c && !!c.data;
}
```

Wait, there's an issue with iterating a Map while deleting. Let me collect keys to delete first, then delete.

```js
const toDelete = [];
for (const [key, c] of chunks) {
  const parts = key.split(',');
  const cx = parseInt(parts[0]), cz = parseInt(parts[1]);
  if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
    toDelete.push(key);
  }
}
for (const key of toDelete) {
  const c = chunks.get(key);
  if (c.mesh) { ... dispose ... }
  chunks.delete(key);
}
```

Also, I should cap the total number of chunks to avoid unbounded growth. The removal handles that.

One concern: the mesh building requires 4 neighbors to have data. Initially, when the player spawns, only chunks near spawn have data. As the player moves, more chunks generate. The neighbor requirement ensures that when we build a mesh, the neighbor reads (getBlock) return actual data rather than air (which would cause incorrect face culling at borders). Good.

But there's a subtle issue: if a chunk's neighbor hasn't been generated yet, the chunk's mesh would show air faces where the neighbor should be solid. But since we require all 4 neighbors to have data before meshing, this is avoided. However, a chunk could be meshed while its diagonal neighbors aren't generated — that's fine because we only check N,S,E,W. Diagonal differences are minor and only affect diagonal edges. Acceptable.

Actually wait, there's still a problem: when we mesh a chunk, we read neighbors via getBlock. If a neighbor chunk has data but we haven't meshed it yet, getBlock still returns correct block IDs (since it reads from data). Good, meshing depends on data, not on neighbor meshes. 

### Player physics

PerspectiveCamera, fov 75, far 400, rotation order YXZ.

```js
const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 400);
camera.rotation.order = 'YXZ';
```

Player box: half-width 0.3, height 1.8, eye 1.62. Spawn at (8, terrain, 8).

Spawn: place player at x=8, z=8, y = surface height + some offset. Let me compute the terrain height at (8,8) and spawn above it.

Actually, spawn at x=8, z=8. The chunk containing (8,8) is chunk (0,0). Its data might not be generated at startup. Let me generate chunk (0,0) immediately at startup to ensure spawn works. Actually, let me pre-generate the initial chunks needed for spawn.

Let me set player.y to a safe height. At spawn, compute H at (8,8) and set y = H + 1 + 1.8 (above ground). But chunk (0,0) data must exist. Let me generate it explicitly at init.

Actually, simpler: generate chunk (0,0) at startup (and maybe a few others). Then spawn.

Player physics:
```js
const player = {
  x: 8, y: 40, z: 8,
  vy: 0,
  onGround: false,
  yaw: 0,
  pitch: 0
};
```

Movement:
```js
const keys = {};
// WASD
let moveX = 0, moveZ = 0;
if (keys['KeyW']) moveZ -= 1;
if (keys['KeyS']) moveZ += 1;
if (keys['KeyA']) moveX -= 1;
if (keys['KeyD']) moveX += 1;
// normalize
if (moveX || moveZ) {
  const len = Math.hypot(moveX, moveZ);
  moveX /= len; moveZ /= len;
}
// relative to yaw
const sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
const vx = (moveX * cos + moveZ * sin) * SPEED;
const vz = (-moveX * sin + moveZ * cos) * SPEED;
```

Wait, yaw rotates around Y. Forward (-Z in camera?) Let me define yaw such that yaw=0 looks toward -Z. Camera rotation YXZ with euler. Let me set camera.rotation.y = yaw. With YXZ order, rotating around Y first. Standard: camera looks down -Z when yaw=0. Forward vector = (-sin(yaw), 0, -cos(yaw)). Right vector = (cos(yaw), 0, -sin(yaw))? Let me just derive.

For YXZ Euler, the camera's forward direction (into screen, -Z local) rotated by yaw:
forward = (sin(yaw) * ... ) hmm let me just compute.

Rotation about Y by angle θ maps local -Z axis. Local forward (direction camera looks) is (0,0,-1) in local space. After rotation about Y by θ:
x' = x cosθ + z sinθ ... 

Rotation matrix about Y:
[ cosθ   0   sinθ ]
[ 0      1     0  ]
[-sinθ  0   cosθ  ]

Applying to (0,0,-1):
x' = cosθ*0 + 0 + sinθ*(-1) = -sinθ
y' = 0
z' = -sinθ*0 + 0 + cosθ*(-1) = -cosθ

So forward = (-sinθ, 0, -cosθ). Good.

Right vector (local +X) rotated: (cosθ, 0, -sinθ).

Movement relative to yaw: press W moves forward, D moves right.
velocity.x = forward.x * wz + right.x * dx
where wz ∈ [-1,1] (W=-1 forward... let me define W gives forward).

Let me define input: fw = (W? -1 : 0) + (S? +1 : 0), rt = (D? +1 : 0) + (A? -1 : 0). Then:
vel.x = forward.x * fw + right.x * rt
vel.z = forward.z * fw + right.z * rt

With forward = (-sinθ, 0, -cosθ), right = (cosθ, 0, -sinθ):
vel.x = -sinθ*fw + cosθ*rt
vel.z = -cosθ*fw - sinθ*rt

Speed 5.5. Good.

Physics update:
```js
player.vy -= GRAVITY * dt; // gravity 25
if (onGround && space) { player.vy = 8.5; onGround = false; }
// integrate X
newX = x + vel.x * dt;
// collision X
if (!collides(newX, y, z)) x = newX;
// integrate Z similarly
// integrate Y
newY = y + player.vy * dt;
if (!collides(x, newY, z)) { y = newY; onGround = false; }
else { if (player.vy > 0) onGround = true; player.vy = 0; }
```

Collision: AABB vs blocks. Player box half-width 0.3, height 1.8, eye 1.62. The box spans from (x-0.3, y, z-0.3) to (x+0.3, y+1.8, z+0.3). Wait, is y the feet or the eye? Let me define y as the feet position (bottom of the box). Eye at y + 1.62. Height 1.8 means top at y+1.8.

Collision check: for the AABB, check all blocks it overlaps. If any is solid, collide.

```js
function collides(px, py, pz) {
  const minX = Math.floor(px - 0.3), maxX = Math.floor(px + 0.3);
  const minY = Math.floor(py), maxY = Math.floor(py + 1.8);
  const minZ = Math.floor(pz - 0.3), maxZ = Math.floor(pz + 0.3);
  for (let x = minX; x <= maxX; x++) {
    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (getBlock(x, y, z) !== 0) return true;
      }
    }
  }
  return false;
}
```

Axis-separated collision: move per axis, revert on overlap. Landing sets on-ground.

```js
// X
let nx = x + vel.x * dt;
if (!collides(nx, y, z)) x = nx;
// Z
let nz = z + vel.z * dt;
if (!collides(x, y, nz)) z = nz;
// Y
let ny = y + player.vy * dt;
if (!collides(x, ny, z)) {
  y = ny;
  onGround = false;
} else {
  if (player.vy < 0) onGround = true; // falling, hit ground
  player.vy = 0;
}
```

Wait, when moving up and hitting ceiling, vy should reset too. Let me set vy=0 when collision on either vertical direction. Actually if vy>0 and we collide, we hit ceiling, reset vy=0. If vy<0 and collide, we land, set onGround=true, vy=0.

```js
let ny = y + player.vy * dt;
if (!collides(x, ny, z)) {
  y = ny;
  onGround = false;
} else {
  player.vy = 0;
  if (player.vy <= 0 /* before reset */ ) ... 
}
```

Let me capture vy before reset:
```js
const oldVy = player.vy;
let ny = y + player.vy * dt;
if (!collides(x, ny, z)) {
  y = ny;
  onGround = false;
} else {
  player.vy = 0;
  if (oldVy < 0) onGround = true;
}
```

Falling below y-20 teleports to spawn:
```js
if (y < spawnY - 20) { x = spawnX; y = spawnY; z = spawnZ; player.vy = 0; }
```

Actually "Falling below y −20 teleports back to spawn." I'll interpret: if player.y < (spawnY - 20) or just player.y < -20? Let me do player.y < spawnY - 20. Actually simpler and matches "below y-20": if player.y < -20. Hmm. Let me use spawnY - 20 to be safe (respawn near where they fell). Actually the phrase "teleports back to spawn" suggests going to spawn. Let me trigger when y < spawnY - 20. That gives 20 units of fall room above spawn. Reasonable.

Hmm, but if the terrain at spawn is very high (up to 73), spawnY ~ 75. Falling below 55 teleports. That's fine.

Actually, let me reconsider. Maybe simpler: teleport if y < -20. But if terrain is high, you'd fall a long way before triggering. Let me use spawnY - 20. It's safer.

### Raycasting for break/place

Each frame, raycast from camera center (max distance 6) against chunk meshes.

```js
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
// cast from camera through center of screen
const ndc = new THREE.Vector2(0, 0);
raycaster.set(camera.position, ndc); // direction defaults to (0,0,-1) in camera space? 
```

Wait, raycaster.set(camera, target) — the second form casts a ray from camera position through the target point in camera space. If I pass Vector2(0,0), it casts through the center. Actually the signature is set(origin, direction) or set(camera, target). Let me use:

```js
raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
```

Then intersect chunk meshes:
```js
const hits = raycaster.intersectObjects(chunkMeshes, false);
let target = null;
if (hits.length > 0) {
  const h = hits[0];
  const p = h.point;
  const n = h.face.normal; // in world space? For our geometry, normals are stored in world coords (mesh at origin, no rotation). So n is world normal.
  // break target
  target = [
    Math.floor(p.x - n.x * 0.5),
    Math.floor(p.y - n.y * 0.5),
    Math.floor(p.z - n.z * 0.5)
  ];
}
```

Since meshes are at origin with world-coordinate geometry and no rotation, face normals are in world coordinates. Good.

Wireframe outline: a black wireframe box around the target block.
```js
outline.position.set(target[0]+0.5, target[1]+0.5, target[2]+0.5);
outline.visible = !!target;
```
The outline is a BoxGeometry(1.002,1.002,1.002) with WireframeGeometry, black, added to scene once.

Break: left click, pointer locked, target at y!=0: set target block to air. Then rebuild chunk and neighbor if on border.

Place: right click, pointer locked, place cell = floor(p + n*0.5). Place selected block if cell is air and doesn't overlap player.

Overlap check: does the placed block's cell intersect the player AABB? Cell is unit cube at (fx,fy,fz) to (fx+1,fy+1,fz+1). Player AABB: [x-0.3,x+0.3] x [y,y+1.8] x [z-0.3,z+0.3]. If they overlap, don't place.

```js
function overlapsPlayer(fx, fy, fz) {
  return !(fx+1 < x-0.3 || fx > x+0.3 || fy+1 < y || fy > y+1.8 || fz+1 < z-0.3 || fz > z+0.3);
}
```

Rebuild chunk:
```js
function rebuildChunk(cx, cz) {
  const key = cx + ',' + cz;
  const c = chunks.get(key);
  if (!c || !c.data) return;
  if (c.mesh) {
    scene.remove(c.mesh);
    c.mesh.geometry.dispose();
    const i = chunkMeshes.indexOf(c.mesh);
    if (i >= 0) chunkMeshes.splice(i,1);
  }
  const geom = buildChunkMesh(cx, cz);
  const mesh = new Mesh(geom, material);
  c.mesh = mesh;
  scene.add(mesh);
  chunkMeshes.push(mesh);
}
```

Border neighbor rebuild: if block is on chunk border, rebuild the adjacent chunk too.
```js
function editBlock(bx, by, bz, id) {
  const cx = chunkIndex(bx), cz = chunkIndex(bz);
  setBlock(bx, by, bz, id);
  rebuildChunk(cx, cz);
  // neighbor
  const lx = localIndex(bx), lz = localIndex(bz);
  if (lx === 0) rebuildChunk(cx-1, cz);
  if (lx === CHUNK_SIZE-1) rebuildChunk(cx+1, cz);
  if (lz === 0) rebuildChunk(cx, cz-1);
  if (lz === CHUNK_SIZE-1) rebuildChunk(cx, cz+1);
}
```

### Hotbar

7 slots. HTML elements. Selected border white. Keys 1-7 or wheel.

```js
let selected = 0; // index 0-6 -> block ids 1-7
function selectSlot(i) {
  selected = ((i % 7) + 7) % 7;
  updateHotbarUI();
}
```

Wheel: increment/decrement.

### Sky, clouds, water

Sky background: scene.background = 0x87ceeb, scene.fog = new Fog(0x87ceeb, 40, 110).

Ambient 0.65 + directional 0.8.

Clouds: ~25 flat white transparent boxes at height ~90, drifting and wrapping around player.

```js
const clouds = [];
for (let i = 0; i < 25; i++) {
  const g = new BoxGeometry(8 + Math.random()*... , 1, 6); // but no Math.random allowed!
}
```

Wait, "no Math.random" applies to terrain. But clouds... "Around 25 flat white transparent boxes as clouds at height ~90, slowly drifting and wrapping around the player." The "no Math.random" rule is in the terrain section: "Terrain (deterministic, no Math.random)". So clouds can use Math.random for initial positions? Hmm, it's ambiguous. To be safe and deterministic, let me avoid Math.random entirely and use a hash for cloud positions. Actually, using Math.random for cloud initial positions is fine since the rule specifically says terrain must be deterministic. But to be safe, let me use a deterministic hash for cloud positions too. It's cleaner.

Actually, let me just use Math.random for cloud positions — it's not terrain and the determinism rule is specifically about terrain. But then every page load has different clouds. That's fine. Hmm, but let me keep it deterministic to be consistent and avoid any issues. I'll use the hash function.

Let me generate cloud positions deterministically:
```js
for (let i = 0; i < 25; i++) {
  const hx = hash2(i, 0);
  const hz = hash2(i, 1);
  const cloud = new Mesh(
    new BoxGeometry(6 + hx*10, 1.5, 5 + hz*8),
    new MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 })
  );
  cloud.userData = { speed: 0.3 + hash2(i,2)*0.4, offset: i * 137.5 };
  scene.add(cloud);
  clouds.push(cloud);
}
```

Update each frame: position clouds relative to player, drift in x, wrap.
```js
clouds.forEach((c, i) => {
  c.userData.offset += c.userData.speed * dt;
  const angle = c.userData.offset;
  const radius = 30 + (i % 5) * 20;
  c.position.x = player.x + Math.cos(angle) * radius;
  c.position.z = player.z + Math.sin(angle) * radius;
  c.position.y = 90 + (i % 3) * 3;
});
```

Hmm, "wrapping around the player" — I'll place them in a ring around the player at various radii and angles, drifting. That wraps around. Good enough.

Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame.
```js
const water = new Mesh(
  new PlaneGeometry(400, 400),
  new MeshLambertMaterial({ color: 0x3388ff, transparent: true, opacity: 0.6 })
);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);
// each frame:
water.position.x = player.x;
water.position.z = player.z;
```

### UI

Start overlay: fullscreen div with title, controls list, "Click to play". Reappears when pointer lock released.

```html
<div id="overlay">
  <h1>MineClone</h1>
  <ul>
    <li>WASD - move</li>
    <li>Mouse - look</li>
    <li>Space - jump</li>
    <li>Left click - break</li>
    <li>Right click - place</li>
    <li>1-7 / wheel - select block</li>
  </ul>
  <div id="play">Click to play</div>
</div>
```

Pointer lock: clicking overlay requests pointer lock on canvas. On change, if locked show game, else show overlay.

Crosshair: small div at center.

Let me now also handle the canvas being fullscreen, body margin 0.

Let me write the full HTML now.

Let me reconsider a few details:

1. The material: one shared MeshLambertMaterial. But clouds use a separate transparent material, water another. The "ONE shared MeshLambertMaterial" refers to the block material. Blocks use vertex colors, so material.vertexColors = true, and material.color can be neutral (white) so vertex colors show. Actually with vertexColors=true, the material's color is multiplied. Let me set material color to 0xffffff and vertexColors true.

Wait, MeshLambertMaterial with vertexColors: the diffuse is baseColor * vertexColor * lighting. If baseColor is white (1,1,1), then it's just vertexColor * lighting. Good. So set `material = new MeshLambertMaterial({ vertexColors: true, color: 0xffffff })`.

2. Fake lighting is baked into vertex colors (multiply by 1.0/0.8/0.55). Then Lambert adds lighting on top. That's fine — the fake lighting gives the block-face shading, Lambert gives directional sun shading. Combined effect looks decent.

3. Fog matches sky. Good.

4. Let me double check the raycaster normal direction. Our geometry normals are stored as-is (world space). face.normal from intersection is in world space since mesh has no rotation/scale. Good.

5. The outline: use WireframeGeometry on a BoxGeometry(1,1,1), black, depthTest maybe true so it shows through. Actually if depthTest is true, the wireframe behind blocks won't show. For a target outline we usually want it visible even through blocks, but typically the target block is adjacent so the wireframe surrounds it. Let me set depthTest: false so it's always visible? But then it might clash with other blocks. Hmm. Let me keep depthTest true (default) so it appears as a box around the targeted block. Since the targeted block is within 6 blocks and we're looking at its face, the front faces of the wireframe will show. Actually the wireframe encloses the block; the parts facing us show, parts behind are occluded by the block itself. That's the typical Minecraft targeting box. Good, keep default depthTest.

Actually, to make it pop, let me make it slightly larger (1.01) and black. Let me use WireframeGeometry.

Let me now also make sure the crosshair is a small div with borders forming a plus or just a small square. Spec: "A small CSS crosshair at screen center." I'll make a small cross shape or a small square outline. Let me do a small "+" using two divs, or just a small square with transparent center and bordered. I'll do a simple crosshair with two overlapping thin divs.

Let me write it.

6. Pointer lock: request on canvas click (when overlay is showing). Add document-level 'click'? Better: overlay click requests lock. Let me attach click listener to overlay.

Actually, the spec: "Clicking the start overlay requests pointer lock". So overlay click → canvas.requestPointerLock(). On pointerlockchange, toggle overlay visibility.

Let me structure:
```js
overlay.addEventListener('click', () => {
  canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  if (document.pointerLockElement === canvas) {
    overlay.style.display = 'none';
    gameActive = true;
  } else {
    overlay.style.display = 'flex';
    gameActive = false;
  }
});
```

Mouse movement only when active:
```js
document.addEventListener('mousemove', (e) => {
  if (!gameActive) return;
  player.yaw -= e.movementX * 0.002;
  player.pitch -= e.movementY * 0.002;
  player.pitch = Math.max(-Math.PI/2 + 0.01, Math.min(Math.PI/2 - 0.01, player.pitch));
});
```

Click handling: only when active.
```js
canvas.addEventListener('mousedown', (e) => {
  if (!gameActive) return;
  if (e.button === 0) { // break
    if (target && target[1] !== 0) {
      editBlock(target[0], target[1], target[2], 0);
    }
  } else if (e.button === 2) { // place
    if (target) {
      const px = Math.floor(target[0]+1), py = Math.floor(target[1]+1), pz = Math.floor(target[2]+1);
      // wait, place cell = floor(p + n*0.5). target = floor(p - n*0.5). place = floor(p + n*0.5).
      // These may differ. Let me recompute place from hit.
    }
  }
});
```

Hmm, I need to store the hit point and normal, not just the target. Let me store `hitPoint` and `hitNormal` alongside target. Actually target already encodes the break position. For place, I need floor(p + n*0.5). Let me store the hit and compute both.

Let me store:
```js
let hit = null; // {point: Vector3, normal: Vector3}
```
Each frame after raycast:
```js
if (hits.length > 0) {
  hit = { point: hits[0].point.clone(), normal: hits[0].face.normal.clone() };
  target = [
    Math.floor(hit.point.x - hit.normal.x*0.5),
    Math.floor(hit.point.y - hit.normal.y*0.5),
    Math.floor(hit.point.z - hit.normal.z*0.5)
  ];
} else {
  hit = null;
  target = null;
}
```

Place:
```js
if (e.button === 2 && hit) {
  const px = Math.floor(hit.point.x + hit.normal.x*0.5);
  const py = Math.floor(hit.point.y + hit.normal.y*0.5);
  const pz = Math.floor(hit.point.z + hit.normal.z*0.5);
  if (getBlock(px,py,pz) === 0 && !overlapsPlayer(px,py,pz)) {
    editBlock(px, py, pz, selected + 1);
  }
}
```

selected+1 because selected is 0-indexed and block ids are 1-7.

Suppress context menu:
```js
canvas.addEventListener('contextmenu', e => e.preventDefault());
```

7. Spawn: I need to generate chunk (0,0) at startup. Let me generate it explicitly before spawning.

```js
chunks.set('0,0', { data: generateChunkData(0,0), mesh: null });
// find surface at (8,8)
let spawnY = 40;
for (let y = CHUNK_HEIGHT-1; y >= 0; y--) {
  if (getBlock(8, y, 8) !== 0) { spawnY = y + 1 + 1.8; break; }
}
player.x = 8; player.y = spawnY; player.z = 8;
```

Wait, getBlock(8,y,8) reads chunk (0,0) which we just generated. Good. Surface block at some y; spawn feet above it: y+1 (standing on top means feet at y+1? If surface block occupies y..y+1, standing on top means feet at y+1). Plus a little. Let me set player.y = y + 1 + 0.5. Actually feet at surface top = (y)+1. Let me set spawnY = (surfaceY) + 1 + 1.8 to be safely above. Hmm, but if we spawn too high we fall. Let me spawn feet at surfaceTop + 0.2. Surface top is at y+1 (block occupies [y,y+1]). So feet at y+1 + 0.2. Let me do player.y = surfaceY + 1.5. That puts feet 0.5 above the surface top. Fine, they'll settle onto the block.

Actually, let me reconsider: block at integer y occupies [y, y+1] in world. If surface block is at y=S, its top is at S+1. Standing on it, feet at S+1. So player.y (feet) = S+1. Let me set player.y = S + 1 + 0.01 to avoid sinking. Actually to be safe, S + 1.3. They'll fall a tiny bit and land. Let me do S + 1.5.

Let me find surfaceY = highest y with non-air block.

8. Aspect ratio: handle window resize, update camera.aspect and projectionMatrix.

9. Animation loop with delta time. Use requestAnimationFrame, compute dt capped.

Let me also make sure the camera position = player eye: camera.position.set(player.x, player.y + 1.62, player.z). camera.rotation.y = player.yaw, rotation.x = player.pitch. With order YXZ.

Let me set camera.rotation.set(player.pitch, player.yaw, 0, 'YXZ').

10. Performance: meshing loops over 16*16*80 = 20480 blocks per chunk, times 6 faces. Building 2 chunks/frame + generating 4 chunks/frame. Should be OK.

Actually, generating 4 chunks/frame each doing 20480 blocks * up to 6 faces = lots of operations. 4 * 20480 * 6 = ~490k iterations/frame plus noise calls. Noise calls are cheap. Might be a bit heavy but should be OK at 60fps for a demo. Actually generating 4 full chunks per frame might be too slow initially. Let me reduce to generating fewer, or it's fine since it's per-frame streaming. The spec says max 4 per frame for data, max 2 per frame for meshes. I'll follow that.

Hmm, but 4 chunks of data generation per frame, each 20480 blocks with noise... Let me estimate: 4*20480 = 81920 blocks, each doing a few noise evaluations (fractal2 = 4 octaves * noise2 = 4*4=16 hash calls + interpolations, plus cave noise). Say ~50 ops per block = 4M ops/frame. That might be ~tens of ms. Acceptable but could cause hitches. The spec explicitly says max 4 per frame though, so I'll follow it. Real-world this streams in fine.

Actually, let me reconsider — maybe generate less frequently or the numbers are fine. I'll follow spec: 4 data, 2 meshes per frame.

Let me also double check: "build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame)". So within radius 4 of player, and only those with all 4 cardinal neighbors having data. Max 2 meshes/frame. Good.

Let me refine the chunk update to iterate in a sensible order (near to far) so nearby chunks get meshed first. I'll iterate dx,dz from 0 outward.

Let me write the final code.

Let me also handle the case where selected block index maps to block id. selected 0->1 (grass), 1->2 (dirt), ..., 6->7 (snow). So block id = selected + 1.

Hotbar UI: 7 slots showing block color and number. Let me create them in HTML and update border.

Let me write the CSS for hotbar slots.

Now let me also reconsider the "keep the mesh at the origin" for raycasting. Since meshes are at origin with world coords, intersectObjects works in world space directly. Good.

Let me also add the directional light and ambient. Directional light should have a position. Let me place it high. It affects Lambert shading. Fine.

Let me also make sure fog doesn't make distant chunks invisible abruptly — fog 40-110. Chunks within 7 have radius up to 7*16=112 blocks. At 110 fog end, edge chunks barely visible. Fine.

Let me write everything now.

One more: the outline wireframe should be updated each frame to target position. And hidden when no target.

Let me also make sure to set material depthWrite etc. Not necessary.

Let me consider whether MeshLambertMaterial supports vertexColors — yes, vertexColors property works with PointLightMaterial, MeshLambertMaterial, MeshPhongMaterial. Good.

Let me also double-check the FACES winding doesn't matter. Since we don't set side (default both sides), winding irrelevant. Normals stored correctly for Lambert (dot with light). Actually Lambert uses the normal to compute diffuse = max(0, dot(normal, lightDir)). If a face normal points inward (wrong), its shading would be off but since each face has outward normal by construction (we only add faces facing air), normals point outward. Good.

Wait, do the normals point outward? For +X face we store normal (1,0,0) which points in +X, outward (since the neighbor in +X is air). Yes correct. For -X, normal (-1,0,0) points -X outward. Good. All correct.

Now, let me write the code carefully and completely.

Let me reconsider the hash functions to ensure good distribution and no NaN.

```js
function hash2(ix, iy) {
  // integer hash to 0..1
  let h = (Math.imul(ix, 374761393) + Math.imul(iy, 668265263) + 1013904223) | 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

Using Math.imul for 32-bit multiply. Good.

```js
function hash3(ix, iy, iz) {
  let h = (Math.imul(ix, 374761393) + Math.imul(iy, 668265263) + Math.imul(iz, 0x51ea7c93) + 1013904223) | 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

columnHash for trees:
```js
function columnHash(ix, iz) {
  let h = (Math.imul(ix, 2654435761) + Math.imul(iz, 2246822519) + 3948271) | 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

noise2:
```js
function noise2(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf * xf * (3 - 2 * xf);
  const v = yf * yf * (3 - 2 * yf);
  const a = hash2(xi, yi), b = hash2(xi + 1, yi);
  const c = hash2(xi, yi + 1), d = hash2(xi + 1, yi + 1);
  const top = a + (b - a) * u;
  const bot = c + (d - c) * u;
  return top + (bot - top) * v;
}
```

fractal2 normalized:
```js
function fractal2(x, y) {
  let sum = 0, amp = 1, freq = 1, total = 0;
  for (let o = 0; o < 4; o++) {
    sum += amp * noise2(x * freq, y * freq);
    total += amp;
    freq *= 2;
    amp *= 0.5;
  }
  return sum / total;
}
```

noise3:
```js
function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = xf * xf * (3 - 2 * xf);
  const v = yf * yf * (3 - 2 * yf);
  const w = zf * zf * (3 - 2 * zf);
  const c000 = hash3(xi, yi, zi), c100 = hash3(xi+1, yi, zi);
  const c010 = hash3(xi, yi+1, zi), c110 = hash3(xi+1, yi+1, zi);
  const c001 = hash3(xi, yi, zi+1), c101 = hash3(xi+1, yi, zi+1);
  const c011 = hash3(xi, yi+1, zi+1), c111 = hash3(xi+1, yi+1, zi+1);
  const x00 = c000 + (c100 - c000) * u;
  const x10 = c010 + (c110 - c010) * u;
  const x01 = c001 + (c101 - c001) * u;
  const x11 = c011 + (c111 - c011) * u;
  const xy0 = x00 + (x10 - x00) * v;
  const xy1 = x01 + (x11 - x01) * v;
  return xy0 + (xy1 - xy0) * w;
}
```

Now generateChunkData:
```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      const wx = cx * CHUNK_SIZE + lx;
      const wz = cz * CHUNK_SIZE + lz;
      const m = fractal2(wx * 0.004, wz * 0.004);
      const h = fractal2(wx * 0.02, wz * 0.02);
      const H = Math.floor(5 + m * m * 58 + h * 10);
      for (let y = 0; y <= H; y++) {
        let id;
        if (y === 0 || y < H - 3) {
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
        data[idx(lx, y, lz)] = id;
      }
      // caves
      for (let y = 3; y < H - 2; y++) {
        if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
          data[idx(lx, y, lz)] = 0;
        }
      }
      // trees
      const surfId = data[idx(lx, H, lz)];
      if (surfId === 1 && H + 8 < CHUNK_HEIGHT) {
        if (columnHash(wx, wz) < 0.02) {
          for (let y = H + 1; y <= H + 4; y++) data[idx(lx, y, lz)] = 5;
          for (let dx = -2; dx <= 2; dx++)
            for (let dz = -2; dz <= 2; dz++) {
              placeLeafIn(data, lx + dx, H + 5, lz + dz, 6);
              placeLeafIn(data, lx + dx, H + 6, lz + dz, 6);
            }
          for (let dx = -1; dx <= 1; dx++)
            for (let dz = -1; dz <= 1; dz++)
              placeLeafIn(data, lx + dx, H + 7, lz + dz, 6);
          placeLeafIn(data, lx, H + 8, lz, 6);
        }
      }
    }
  }
  return data;
}

function placeLeafIn(data, lx, ly, lz, id) {
  if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE) return;
  if (ly < 0 || ly >= CHUNK_HEIGHT) return;
  if (data[idx(lx, ly, lz)] === 0) data[idx(lx, ly, lz)] = id;
}
```

Wait, there's a subtle issue: caves could hollow out the dirt/grass layers creating caves that open upward. But since caves only go up to y < H-2, and surface at H, there are 2 blocks (H-1, H-2... wait y < H-2 means up to H-3) between last cave and surface. So surface layer (H) and H-1, H-2 are intact. Good, no open caves at surface. Actually wait, caves carve from y=3 to y=H-3 (since y < H-2 → y max = H-3). So blocks H-2, H-1, H are always solid. Good. But adjacent columns might have different H, and caves in a neighbor could create a pocket. That's fine, it's organic.

Hmm, but actually there's a concern: if H is small (e.g., 16 for sand beach), caves from y=3 to y=14, surface at 16. That's fine.

Now, one concern: at very low H (like H=5), the "3 layers under surface" would be at y=2,3,4 and surface at 5. y < H-3 = y < 2 means y=0,1 are stone. y=2,3,4 under surface (dirt/sand/stone). y=5 surface. Total 6 blocks (0..5). Good.

Now meshing. Let me finalize buildChunkMesh.

Let me reconsider memory: positions array grows. For a chunk with many exposed faces, could be up to 20480 blocks * up to 6 faces * 4 verts = 491520 floats * 3 = ~1.5M floats = 6MB. That's a lot but only for fully exposed (cave-heavy) chunks. Usually much less. Fine.

Let me write buildChunkMesh returning geometry, and a function to create/update mesh.

Actually, let me combine: buildChunkMesh(cx,cz) returns a BufferGeometry. Then a function attachMesh(cx,cz) creates Mesh from geometry and adds to scene + chunkMeshes.

Let me now also reconsider: when I rebuild a chunk after editing, I dispose old geometry and create new. Good.

Let me also ensure I don't leak: on removal (chunk > 7 away), dispose geometry and remove from scene and chunkMeshes.

Now the main loop:

```js
let last = performance.now();
function frame(now) {
  let dt = (now - last) / 1000;
  last = now;
  if (dt > 0.1) dt = 0.1;
  if (gameActive) {
    updatePlayer(dt);
    updateChunks();
    updateCamera();
    updateTargets();
    updateClouds(dt);
    updateWater();
  }
  requestAnimationFrame(frame);
}
```

updateTargets does the raycast and updates target array + outline.

Let me write updatePlayer:

```js
function updatePlayer(dt) {
  // movement input
  let fw = 0, rt = 0;
  if (keys['KeyW']) fw -= 1;
  if (keys['KeyS']) fw += 1;
  if (keys['KeyD']) rt += 1;
  if (keys['KeyA']) rt -= 1;
  const sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
  // forward = (-sin,0,-cos), right = (cos,0,-sin)
  let vx = (-sin * fw + cos * rt) * SPEED;
  let vz = (-cos * fw - sin * rt) * SPEED;
  // integrate X
  let nx = player.x + vx * dt;
  if (!collides(nx, player.y, player.z)) player.x = nx;
  let nz = player.z + vz * dt;
  if (!collides(player.x, player.y, nz)) player.z = nz;
  // gravity
  player.vy -= GRAVITY * dt;
  if (keys['Space'] && player.onGround) { player.vy = JUMP; player.onGround = false; }
  let ny = player.y + player.vy * dt;
  if (!collides(player.x, ny, player.z)) {
    player.y = ny;
    player.onGround = false;
  } else {
    if (player.vy < 0) player.onGround = true;
    player.vy = 0;
  }
  if (player.y < spawnY - 20) { player.x = spawnX; player.y = spawnY; player.z = spawnZ; player.vy = 0; }
}
```

Wait, gravity should apply even when on ground? Typically yes but grounded player has vy reset to 0 each frame due to collision. Actually if on ground and gravity pushes below, collision resets vy=0 and sets onGround. So fine. But when on ground and jumping, we set vy=JUMP. Good.

But there's an issue: when on ground, gravity reduces vy slightly then collision restores. Fine.

collides uses getBlock which reads chunk data. Near chunk borders, reading neighbor requires neighbor data to exist. If not, returns air (treats as empty) — could let player walk into void momentarily, but since we generate neighbors within radius 5 and mesh within 4, and player is near their chunk, neighbors usually exist. Edge cases minor.

Let me set constants:
GRAVITY = 25, JUMP = 8.5, SPEED = 5.5.

updateCamera:
```js
camera.position.set(player.x, player.y + 1.62, player.z);
camera.rotation.set(player.pitch, player.yaw, 0, 'YXZ');
```

updateTargets:
```js
raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
const hits = raycaster.intersectObjects(chunkMeshes, false);
if (hits.length > 0) {
  hitPoint.copy(hits[0].point);
  hitNormal.copy(hits[0].face.normal);
  target = [
    Math.floor(hitPoint.x - hitNormal.x * 0.5),
    Math.floor(hitPoint.y - hitNormal.y * 0.5),
    Math.floor(hitPoint.z - hitNormal.z * 0.5)
  ];
} else {
  target = null;
}
outline.visible = target !== null;
if (target) outline.position.set(target[0] + 0.5, target[1] + 0.5, target[2] + 0.5);
```

Wait, raycaster.intersectObjects with many meshes — each frame. chunkMeshes could be ~ (9*9)=81 meshes max. Raycasting against 81 meshes with geometry each having thousands of triangles. That could be slow. Let me consider limiting. Actually intersectObjects does a frustum-ish test then triangle intersection. 81 meshes * maybe hundreds of triangles = manageable but could be heavy. 

Optimization: only raycast against chunks within a small radius of the player (e.g., within 3 chunks). Since max distance is 6 blocks and chunk is 16, the target is always within the player's own chunk or an immediate neighbor. So I can restrict the raycast to chunks within radius 1-2 of player. Let me build a temporary list of nearby chunk meshes each frame, or better, filter chunkMeshes by proximity.

Actually, since raycast distance is only 6 blocks, the hit is always within the player's chunk or adjacent. So I only need to test meshes in chunks within radius 1 (to be safe, 2). Let me filter:

```js
const nearby = [];
const pcx = chunkIndex(player.x), pcz = chunkIndex(player.z);
for (const m of chunkMeshes) {
  // mesh is at origin with world coords; we stored chunk coords? 
}
```

Hmm, I didn't store chunk coords on the mesh. Let me store userData.chunkX/chunkZ on each mesh. Then filter:

```js
const testMeshes = [];
for (const m of chunkMeshes) {
  if (Math.abs(m.userData.cx - pcx) <= 2 && Math.abs(m.userData.cz - pcz) <= 2) {
    testMeshes.push(m);
  }
}
const hits = raycaster.intersectObjects(testMeshes, false);
```

This reduces from 81 to ~25 meshes. Even better, since distance 6, radius 1 suffices, but 2 is safe. Let me use radius 1 actually: player's chunk is pcx,pcz; blocks within 6 of player are within the chunk (16 wide) so radius 1 covers neighbors. But to be safe with the player near an edge, radius 1 covers all 9 surrounding chunks. Distance 6 < 16 so definitely within radius 1. Let me use radius 1 (9 chunks). Good.

Actually, let me reconsider: the player is somewhere in chunk pcx. The farthest block within 6 units could be in an adjacent chunk if player is near the edge. Radius 1 (the 9 chunks around) definitely covers it. Good.

Let me store cx,cz on mesh userData when creating.

Now updateClouds and updateWater as above.

Let me also make sure the outline uses WireframeGeometry:
```js
const outlineGeom = new WireframeGeometry(new BoxGeometry(1.02, 1.02, 1.02));
const outline = new Line(outlineGeom, new LineBasicMaterial({ color: 0x000000 }));
outline.visible = false;
scene.add(outline);
```

LineBasicMaterial with color black. Good.

Now the hotbar UI. Let me create HTML for 7 slots and update on select.

Let me also add the crosshair.

Let me write the HTML/CSS.

Let me now also double-check the spawn: I generate chunk (0,0) at startup. But updateChunks also generates. At startup gameActive is false (overlay shown), so updateChunks isn't called until play. But I need chunk (0,0) for spawn before that. Let me explicitly generate (0,0) at init and set spawn. Then when player clicks play, updateChunks takes over. Also, I should probably generate a few initial chunks around spawn so the world feels populated. Let me generate chunks within radius 2 at startup (not per-frame) so spawn area is ready. Actually the spec wants per-frame generation. But for a good first experience, let me pre-generate the chunk the player spawns in plus immediate neighbors. Let me pre-generate radius 2 (25 chunks) at startup. That's 25 * 20480 = 512000 block computations with noise — might take ~100-300ms once. Acceptable at startup. Then per-frame streaming continues.

Hmm, but 25 chunks * 6 faces meshing = also heavy. Let me pre-generate data for radius 2 but only mesh radius 1 or 2. Actually, let me pre-generate data for the spawn chunk and its 8 neighbors (radius 1, 9 chunks), then mesh them. That gives a solid starting view. Per-frame generation streams further.

Actually, let me reconsider performance at startup. Generating 9 chunks of data: 9*20480 = 184320 blocks, each with noise. Meshing 9 chunks: each up to 20480 blocks * 6 faces. Could be ~1-2 seconds total. Might cause a brief freeze. Let me pre-generate radius 1 (9 chunks) data and mesh radius 1. Should be OK-ish. Or I could just rely on per-frame generation starting immediately when they click play, but then the first second is blank. Pre-generating a small area is better UX.

Let me pre-generate data for radius 2 (25 chunks) and mesh radius 1 (9 chunks). Balance. Actually, let me just pre-generate radius 1 (9 chunks) both data and mesh. Simpler and fast enough (~0.5s). Then streaming fills in.

Hold on, let me reconsider. Let me pre-generate data for radius 2 and mesh radius 1. The extra data is cheap (just arrays). Meshing radius 1 (9 chunks) is the heavy part but gives immediate visuals. Streaming will mesh radius 2+ over time. Good.

Actually, simplest robust approach: at startup, generate data for all chunks within radius 3 (49 chunks) — data generation is fast-ish — and mesh within radius 1. Then per-frame streaming continues. Let me do radius 3 data, radius 1 mesh at startup. Hmm, 49 chunks data gen might be ~1s. Let me do radius 2 data (25 chunks) and radius 1 mesh (9 chunks). 

Let me just do: generate data for radius 2 (25 chunks), mesh radius 1 (9 chunks). Then loop streams.

Actually, you know what, let me keep it simpler: generate and mesh radius 1 (9 chunks) at startup. This is quick and gives immediate gameplay. The rest streams in over the next few seconds as the player moves/looks. Since meshing is limited to 2/frame, radius 2+ meshes appear over ~((81-9)/2 ≈ 36 frames ≈ 0.6s) after moving near. Fine.

Wait, but meshing only happens for chunks within radius 4 whose 4 neighbors have data. At startup with only radius 1 meshed, the per-frame meshing will progressively mesh outer chunks as neighbors get data. Good.

Let me finalize: startup generate data radius 2, mesh radius 1. Actually let me mesh radius 1 only at startup; the frame loop handles the rest.

Let me reconsider: do I even need to pre-mesh? When player clicks play, gameActive=true, and the first frames run updateChunks which generates and meshes. But the very first frame might have no meshes yet (data just generated). Over the next second, meshes appear. To avoid a blank first second, pre-mesh radius 1 at startup. Yes.

OK let me just write it. I'll pre-generate data for radius 2 and pre-mesh radius 1 at startup.

Let me reconsider the number of clouds: 25. Good.

Let me also ensure water plane opacity and color: 0x3388ff, opacity 0.6, transparent. PlaneGeometry(400,400) rotated -PI/2 on X to be horizontal. Position y=14.3, recenter each frame.

Now, potential issue: water at y=14.3 and terrain can be below 16 (beaches/lakes). Where terrain height H <= 14, water covers it. Since water is a big plane at fixed height, and terrain rises above 14.3 on land, the water line appears where terrain crosses 14.3. Good, "lakes and beaches appear automatically where terrain is lower". 

Now let me also make sure the player can walk on land above water and swim... well, no swimming mechanics, just walking. Fine.

Let me also double check: spawn at (8,8). Surface there depends on noise. Could be anywhere 5-73. If it's a low area (H<=16), spawn might be in/near water. Player spawns above surface and falls. Fine.

Alright, let me also handle the case where the player spawns and there's a tree or something — negligible.

Let me write the final HTML.

Let me reconsider the collision function performance: called multiple times per frame, each checks up to (2*floor... ) blocks. Player box spans x-0.3 to x+0.3 → floors cover 2-3 x values, similarly y (1.8 height → 2-3 values), z (2-3). So ~3*3*3=27 block checks per call, called ~3 times per frame (X,Y,Z integration) = ~80 getBlock calls per frame. getBlock does a Map lookup and arithmetic. Fine.

Now let me write it all out.

Let me also add a subtle: when placing blocks, we shouldn't place inside ourselves. overlapsPlayer handles that.

Let me also make sure breaking at y=0 is prevented (unbreakable). The spec: "left click sets the target to air (not at y 0)". So if target[1] === 0, don't break. Good, I have that check.

Also don't break if target is null.

Let me also consider: after breaking/placing, we rebuild. But if the player is looking at a far chunk, editing a nearby chunk is fine.

Let me also make sure editBlock handles the case where the block's chunk doesn't have data (shouldn't happen near player). setBlock checks and returns if no chunk. rebuildChunk checks too.

Now, one more: the raycaster setFromCamera — need camera to have updated matrices. After setting position and rotation, the projectionMatrix and viewMatrix are recomputed automatically? Setting camera.position and camera.rotation triggers recomputation of viewMatrix on next render? Actually, Matrix4.updateProjectionMatrix must be called if aspect changes. Position/rotation changes update viewMatrix lazily? In Three.js, camera.position setter calls updateMatrixWorld? Let me recall: Camera extends Object3D; setting position updates the object matrix, and camera has an onUpdate? Actually, the viewMatrix is computed in Camera.updateProjectionMatrix? No. Let me just call camera.updateMatrixWorld() and camera.updateProjectionMatrix() after changes to be safe. Or set aspect on resize and call updateProjectionMatrix.

Actually, the safest: after updating camera position/rotation each frame, call camera.updateProjectionMatrix() is not needed unless aspect changed. The viewMatrix is derived from the object's matrix which is updated when position/rotation change (Object3D setters mark matrixWorldNeedsUpdate). Raycaster uses camera.matrixWorldInverse which is computed from matrixWorld. Three computes matrixWorld lazily during render. But raycaster.setFromCamera uses camera.matrixWorldInverse and camera.projectionMatrix. If these aren't updated before the raycast, results are stale.

To be safe, each frame after updating camera, call:
```js
camera.updateMatrixWorld();
camera.updateProjectionMatrix();
```
Wait, updateProjectionMatrix only needed if aspect/fov change. But calling it always is harmless. And updateMatrixWorld ensures matrixWorldInverse is fresh. Actually, raycaster.setFromCamera computes the ray using camera.matrixWorldInverse and projectionMatrix. Let me ensure these are fresh by calling camera.updateMatrixWorld() (which updates matrixWorldInverse) and camera.updateProjectionMatrix() (in case aspect changed). Let me call both after setting position/rotation.

Actually, camera.updateProjectionMatrix updates projectionMatrix from fov/aspect. camera.updateMatrixWorld updates matrixWorld and matrixWorldInverse. Let me call both in updateCamera. Good.

Let me also handle resize:
```js
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
});
```

Now let me write the complete file.

Let me reconsider the outline visibility through fog — it's fine.

Let me also reconsider: should the directional light move with player? No, fixed is fine. But if fixed far away, lighting on near faces vs far faces differs. Lambert diffuse depends on angle between normal and light direction, not distance (for a directional light, intensity is constant regardless of distance). So fixed directional light gives consistent shading. Good. Let me point it diagonally.

Let me set:
```js
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(50, 100, 30);
scene.add(sun);
```

Now let me write it all.

Let me reconsider the FACES vertex order to produce correct outward normals — though winding doesn't matter for rendering without culling, let me still make normals correct (they are, by construction). Good.

Let me write FACES with vertices as relative offsets (0 or 1):
```js
const FACES = [
  { n:[1,0,0], v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  { n:[-1,0,0], v:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  { n:[0,1,0], v:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { n:[0,-1,0], v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { n:[0,0,1], v:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
  { n:[0,0,-1], v:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] },
];
```

These are fine.

Now the mesh building: I add 4 vertices per face, indices not needed (we can use non-indexed geometry). BufferGeometry with position, normal, color attributes, no index. Two triangles per face = 6 vertices = indices 0,1,2,0,2,3 implicitly (non-indexed uses consecutive triples). Good.

Let me write buildChunkMesh:
```js
function buildChunkGeometry(cx, cz) {
  const c = chunks.get(cx + ',' + cz);
  const pos = [], nor = [], col = [];
  const wx0 = cx * CHUNK_SIZE, wz0 = cz * CHUNK_SIZE;
  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      for (let y = 0; y < CHUNK_HEIGHT; y++) {
        const id = c.data[idx(lx, y, lz)];
        if (!id) continue;
        const wx = wx0 + lx, wz = wz0 + lz;
        const base = BLOCKS[id].c;
        const r = (base >> 16) & 255, g = (base >> 8) & 255, b = base & 255;
        for (let f = 0; f < 6; f++) {
          const face = FACES[f];
          const nx = wx + face.n[0], ny = y + face.n[1], nz = wz + face.n[2];
          if (getBlock(nx, ny, nz)) continue;
          let m = 0.8;
          if (face.n[1] === 1) m = 1.0;
          else if (face.n[1] === -1) m = 0.55;
          const cr = r * m, cg = g * m, cb = b * m;
          const v = face.v;
          for (let i = 0; i < 4; i++) {
            pos.push(wx + v[i][0], y + v[i][1], wz + v[i][2]);
            nor.push(face.n[0], face.n[1], face.n[2]);
            col.push(cr, cg, cb);
          }
        }
      }
    }
  }
  const g = new BufferGeometry();
  g.setAttribute('position', new Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new Float32BufferAttribute(nor, 3));
  g.setAttribute('color', new Float32BufferAttribute(col, 3));
  return g;
}
```

BLOCKS: `[{id:0,c:0},{id:1,c:0x4caf50},...]`. Let me store as objects with c (color). Actually I'll just use an array indexed by id: BLOCK_COLOR[id].

```js
const BLOCK_COLOR = [0x000000, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
```

Now create mesh:
```js
function makeMesh(cx, cz) {
  const geom = buildChunkGeometry(cx, cz);
  const mesh = new Mesh(geom, blockMaterial);
  mesh.userData.cx = cx; mesh.userData.cz = cz;
  return mesh;
}
```

attachMesh and detachMesh helpers for scene management.

Let me write:
```js
function attachMesh(mesh) {
  scene.add(mesh);
  chunkMeshes.push(mesh);
}
function detachMesh(mesh) {
  scene.remove(mesh);
  const i = chunkMeshes.indexOf(mesh);
  if (i >= 0) chunkMeshes.splice(i, 1);
  mesh.geometry.dispose();
}
function rebuildChunk(cx, cz) {
  const key = cx + ',' + cz;
  const c = chunks.get(key);
  if (!c || !c.data) return;
  if (c.mesh) { detachMesh(c.mesh); }
  const mesh = makeMesh(cx, cz);
  c.mesh = mesh;
  attachMesh(mesh);
}
```

Now the chunk update loop. Let me write updateChunks carefully with ordered iteration.

```js
function updateChunks() {
  const pcx = chunkIndex(player.x), pcz = chunkIndex(player.z);
  // generate data within radius 5, max 4/frame
  let gen = 0;
  for (let dz = -5; dz <= 5 && gen < 4; dz++) {
    for (let dx = -5; dx <= 5; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx + ',' + cz;
      const c = chunks.get(key);
      if (c && c.data) continue;
      const data = generateChunkData(cx, cz);
      if (c) c.data = data; else chunks.set(key, { data: data, mesh: null });
      gen++;
    }
  }
  // mesh within radius 4 whose 4 neighbors have data, max 2/frame
  let mes = 0;
  for (let dz = -4; dz <= 4 && mes < 2; dz++) {
    for (let dx = -4; dx <= 4; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx + ',' + cz;
      const c = chunks.get(key);
      if (!c || !c.data || c.mesh) continue;
      if (!hasData(cx+1,cz) || !hasData(cx-1,cz) || !hasData(cx,cz+1) || !hasData(cx,cz-1)) continue;
      const mesh = makeMesh(cx, cz);
      c.mesh = mesh;
      attachMesh(mesh);
      mes++;
    }
  }
  // remove chunks beyond radius 7
  const del = [];
  for (const [key, c] of chunks) {
    const p = key.split(',');
    const cx = +p[0], cz = +p[1];
    if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) del.push(key);
  }
  for (const key of del) {
    const c = chunks.get(key);
    if (c.mesh) detachMesh(c.mesh);
    chunks.delete(key);
  }
}
```

hasData:
```js
function hasData(cx, cz) {
  const c = chunks.get(cx + ',' + cz);
  return !!c && !!c.data;
}
```

Note: iterating `for (const [key,c] of chunks)` while pushing to del (not deleting during iteration) is safe.

Now, there's a subtle bug: the mesh generation requires 4 neighbors to have data. But consider a chunk far from player where neighbors have data but it's just generated — it'll be meshed next frame. Fine.

Also, the player's own chunk: at startup we mesh it. As player moves, new chunks get meshed. Good.

Now the initial setup: generate data radius 2, mesh radius 1.

```js
// init
for (let dz = -2; dz <= 2; dz++)
  for (let dx = -2; dx <= 2; dx++) {
    const cx = dx, cz = dz; // spawn chunk is 0,0
    chunks.set(cx + ',' + cz, { data: generateChunkData(cx, cz), mesh: null });
  }
// mesh radius 1
for (let dz = -1; dz <= 1; dz++)
  for (let dx = -1; dx <= 1; dx++) {
    const mesh = makeMesh(dx, dz);
    chunks.get(dx + ',' + dz).mesh = mesh;
    attachMesh(mesh);
  }
```

Wait, spawn chunk is (0,0) since player at (8,8), chunkIndex(8)=0. Good.

Then find surface at (8,8):
```js
let surfaceY = 20;
for (let y = CHUNK_HEIGHT - 1; y >= 0; y--) {
  if (getBlock(8, y, 8) !== 0) { surfaceY = y; break; }
}
spawnX = 8; spawnZ = 8; spawnY = surfaceY + 1.5;
player.x = 8; player.y = spawnY; player.z = 8;
```

Now UI and events.

Let me write the HTML structure and CSS.

Let me also add instructions in overlay.

Let me finalize the hotbar selection:
```js
function selectSlot(i) {
  selected = ((i % 7) + 7) % 7;
  for (let s = 0; s < 7; s++) {
    slots[s].classList.toggle('sel', s === selected);
  }
}
```

slots are DOM elements created in HTML.

Wheel:
```js
window.addEventListener('wheel', (e) => {
  if (!gameActive) return;
  selectSlot(selected + (e.deltaY > 0 ? 1 : -1));
}, { passive: true });
```

Keys:
```js
window.addEventListener('keydown', (e) => {
  const k = e.code;
  if (k >= 'Digit1' && k <= 'Digit7') selectSlot(+k.slice(5) - 1);
  keys[k] = true;
  if (k === 'Space') e.preventDefault();
});
window.addEventListener('keyup', (e) => { keys[e.code] = false; });
```

Note: Digit1..Digit7 codes. e.code for '1' is 'Digit1'. Good.

Now click to play:
```js
overlay.addEventListener('click', () => canvas.requestPointerLock());
document.addEventListener('pointerlockchange', () => {
  if (document.pointerLockElement === canvas) {
    overlay.style.display = 'none';
    gameActive = true;
  } else {
    overlay.style.display = 'flex';
    gameActive = false;
  }
});
```

Mouse:
```js
document.addEventListener('mousemove', (e) => {
  if (!gameActive) return;
  player.yaw -= e.movementX * 0.002;
  player.pitch = Math.max(-1.55, Math.min(1.55, player.pitch - e.movementY * 0.002));
});
```

Pitch clamp ~ PI/2 = 1.5708, use 1.55.

Click:
```js
canvas.addEventListener('mousedown', (e) => {
  if (!gameActive) return;
  if (e.button === 0) {
    if (target && target[1] !== 0) editBlock(target[0], target[1], target[2], 0);
  } else if (e.button === 2) {
    if (hit) {
      const px = Math.floor(hitPoint.x + hitNormal.x * 0.5);
      const py = Math.floor(hitPoint.y + hitNormal.y * 0.5);
      const pz = Math.floor(hitPoint.z + hitNormal.z * 0.5);
      if (getBlock(px, py, pz) === 0 && !overlapsPlayer(px, py, pz)) {
        editBlock(px, py, pz, selected + 1);
      }
    }
  }
});
canvas.addEventListener('contextmenu', (e) => e.preventDefault());
```

editBlock:
```js
function editBlock(bx, by, bz, id) {
  setBlock(bx, by, bz, id);
  const cx = chunkIndex(bx), cz = chunkIndex(bz);
  rebuildChunk(cx, cz);
  const lx = localIndex(bx), lz = localIndex(bz);
  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);
}
```

overlapsPlayer:
```js
function overlapsPlayer(fx, fy, fz) {
  return !(fx + 1 < player.x - 0.3 || fx > player.x + 0.3 ||
           fy + 1 < player.y || fy > player.y + 1.8 ||
           fz + 1 < player.z - 0.3 || fz > player.z + 0.3);
}
```

Now let me assemble everything. Let me be careful about variable scoping (all in global scope or inside IIFE). I'll use a script with everything in global scope (since THREE is global). Let me just write top-level code.

Let me also double check the `idx` function and chunk indexing for negatives. chunkIndex(floor(world/16)) works for negatives: floor(-1/16) = -1, local = -1 - (-1)*16 = -1 + 16 = 15. Good. localIndex(-1) = 15. Good.

getBlock(-1, y, z): chunk = -1, local = 15. Reads chunk(-1,cz).data[idx(15,y,z)]. Good.

Now let me also verify: when player is at x=8, chunkIndex(8)=0, local=8. Good.

Edge: x = -16 → chunkIndex = -1, local = -16 -(-1)*16 = 0. Good. x=-1 → chunk -1, local 15. Good.

Now, let me reconsider the meshing neighbor requirement causing a gap: a newly generated chunk adjacent to player but whose neighbor isn't generated yet won't be meshed until neighbor has data. Since we generate within radius 5 and mesh within radius 4 requiring neighbor data, and generation happens first each frame, within a couple frames all radius-4 chunks will have data and their neighbors too. Fine.

But there's a subtle issue: a chunk at radius 4 might never get meshed if one of its neighbors is at radius 5 and takes many frames to generate. But as player moves, the player's chunk changes and things stream. It's fine for a demo.

Actually, wait: the meshing loop generates meshes for chunks within radius 4 (of player) whose 4 neighbors have data. The neighbors could be at radius up to 5. If a neighbor at radius 5 hasn't been generated yet (takes up to... well generation is 4/frame covering radius 5 in ~ (11*11)/4 ≈ 30 frames), then the radius-4 chunk waits. But by the time player is near, most chunks are generated. Acceptable.

Let me reduce potential lag: maybe relax to require only that the specific neighbor we read exists. But spec says "whose 4 neighbors already have data". I'll follow spec.

Now let me also make sure the game doesn't crash if chunkMeshes is empty during raycast (early frames). intersectObjects([]) returns []. Fine.

Let me also cap dt to avoid huge jumps.

Let me also ensure requestAnimationFrame loop starts.

Let me also add a small note: the overlay should be clickable to play; when locked, hide; on unlock show.

Let me write the final HTML now. I'll be thorough.

Let me reconsider one thing about MeshLambertMaterial and vertexColors: I recall that with vertexColors true and material color white, the final color = vertexColor * light. Good. But some versions require material.color to be white for pure vertex colors. I'll set color 0xffffff.

Also, I should set material.side = THREE.FrontSide (default) — since no culling issues, both sides render. Default is FrontSide but without face culling in Lambert? Actually Lambert renders both sides by default (side FrontSide means only front faces are rendered, but back faces of a closed cube are the inner faces which we don't generate anyway). Since we only generate outer faces with outward normals, FrontSide renders them all (their normals face the camera when visible). But a face whose normal points away from camera (e.g., inside a cave seen from inside) — FrontSide would cull it. Hmm. For caves, looking into a cave, the inner faces have normals pointing into the cavity (toward viewer), so they're front faces. Actually for an enclosed cave, the inner surface normals point inward (toward the center), so from inside the cave they face the viewer → front faces → rendered. Good. For open surfaces, outward normals face viewer when visible. So FrontSide is fine and avoids rendering back faces (which we don't generate anyway). Let me keep default FrontSide. Actually, to be safe and avoid any invisible faces, I could use DoubleSide. But DoubleSide doubles fill rate. Since we only generate outward faces, FrontSide is correct. Let me keep default.

Hmm, wait: consider a single exposed face on the top of a block. Its normal is +Y. If camera looks up, the face is a front face (normal toward camera) → rendered. If camera looks down at it from below, the normal points away → FrontSide culls it → we see through to whatever's below. That's correct behavior (can't see the top of a block from below). Good.

OK FrontSide is fine.

Now, let me also double check: the directional light direction for Lambert. Light at (50,100,30) from origin. Direction = normalize(-(50,100,30)) roughly pointing down-left-forward. Top faces (normal +Y) dot with light dir: light dir has negative Y component (pointing down), normal +Y → negative dot → clamped to 0?? That would make top faces dark! 

Wait, directional light direction: The light emits along its direction toward origin. For a directional light at position (50,100,30), the light points from that position toward the origin, i.e., direction = origin - lightPos = (-50,-100,-30), normalized. So light direction (direction the light travels) is (-0.45,-0.89,-0.27). The diffuse term is max(0, dot(normal, lightDirection)). For top face normal (0,1,0): dot = -0.89 → max(0,...) = 0. That makes top faces dark! Bad.

I want the light to come from above so top faces are lit. So the light direction should have positive Y when dotted with top normal. That means the light should point downward onto the tops... no. Let me think: light direction is the direction from which light comes? In Three.js, DirectionalLight illuminates based on the direction FROM the light TO the surface, i.e., the vector from light position to point. Actually, the diffuse = max(0, dot(normal, L)) where L is the direction from the surface point toward the light. For a directional light, L = normalize(light.position - point) roughly = normalize(light.position) if point is near origin. So L ≈ normalize((50,100,30)) = (0.45,0.89,0.27). Dot with top normal (0,1,0) = 0.89 → bright. 

So placing light at (50,100,30) gives L pointing up-and-right, lighting top faces well. My earlier confusion: L is from surface TO light, which is positive Y. Good. So top faces lit, bottom faces (normal -Y): dot(-Y, L) = -0.89 → 0, so bottom faces get only ambient. Combined with fake lighting 0.55 * ambient... let me check overall brightness.

Ambient 0.65 applies to all faces (diffuse ambient). Directional adds diffuse where dot>0. So:
- Top face: ambient 0.65 + directional 0.8*0.89 = 0.65+0.71 = 1.36, times fake 1.0 → bright.
- Side face: ambient 0.65 + directional*dot. Side normal (1,0,0): dot(L)=(0.45) → 0.8*0.45=0.36. total 1.01, times fake 0.8 = 0.81.
- Bottom face: ambient 0.65 + directional 0 (dot negative) = 0.65, times fake 0.55 = 0.36.

So top brightest, sides medium, bottom darkest. Looks 3D. Good.

But note the directional adds variation based on orientation relative to light, which is fine and adds realism. Good.

Actually, wait — I want to double-check the fake lighting is applied multiplicatively to the base color, and then Lambert multiplies again by lighting. So final = baseColor * fakeMult * (ambient + directionalDiffuse). Since ambient is 0.65 baseline, nothing goes fully black. Good. Colors remain recognizable.

Alright. Let me also make sure the material isn't too dark. With these values, min ~0.36 * base. Fine.

Let me finalize and write.

Let me reconsider: should I use MeshLambertMaterial or MeshBasicMaterial? Spec explicitly says MeshLambertMaterial. Use it.

Now let me write the complete file.

Also need to make sure to set canvas to fullscreen with display:block, margin 0, overflow hidden.

Let me write CSS:
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: #000; }
canvas { display: block; }
#overlay { position: fixed; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.75); color: #fff; font-family: monospace; text-align: center; z-index: 10; cursor: pointer; }
#overlay h1 { font-size: 48px; margin-bottom: 20px; letter-spacing: 3px; text-shadow: 3px 3px 0 #333; }
#overlay ul { list-style: none; margin-bottom: 30px; font-size: 16px; line-height: 1.8; }
#overlay .play { padding: 12px 30px; border: 3px solid #fff; font-size: 20px; border-radius: 6px; }
#crosshair { position: fixed; left: 50%; top: 50%; transform: translate(-50%,-50%); width: 20px; height: 20px; pointer-events: none; z-index: 5; }
#crosshair::before, #crosshair::after { content:''; position:absolute; background: rgba(255,255,255,0.85); }
#crosshair::before { left: 9px; top: 0; width: 2px; height: 20px; }
#crosshair::after { top: 9px; left: 0; height: 2px; width: 20px; }
#hotbar { position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%); display: flex; gap: 6px; padding: 6px; background: rgba(0,0,0,0.55); border-radius: 8px; z-index: 5; pointer-events: none; }
.slot { width: 46px; height: 46px; border: 3px solid #333; border-radius: 6px; position: relative; display: flex; align-items: center; justify-content: center; color: #fff; font-family: monospace; font-weight: bold; text-shadow: 1px 1px 2px #000; }
.slot.sel { border-color: #fff; box-shadow: 0 0 6px #fff; }
.slot .num { position: absolute; top: 1px; left: 3px; font-size: 12px; }
```

Hotbar slots created in HTML with background colors.

Let me create slots in HTML:
```html
<div id="hotbar"></div>
```
And build with JS, or hardcode. Let me hardcode in HTML for clarity. Actually building in JS is cleaner. Let me build in JS:

```js
const hotbar = document.getElementById('hotbar');
const slots = [];
for (let i = 0; i < 7; i++) {
  const s = document.createElement('div');
  s.className = 'slot';
  s.style.background = '#'+BLOCK_COLOR[i+1].toString(16).padStart(6,'0');
  s.innerHTML = `<span class="num">${i+1}</span>`;
  hotbar.appendChild(s);
  slots.push(s);
}
selectSlot(0);
```

Good.

Now the crosshair and hotbar should be hidden when overlay shown? They can stay; overlay covers them. Overlay is z-index 10, covers. Fine.

Let me now write the whole thing.

Let me reconsider the `idx` name collision — it's fine as a function.

Let me also make sure I define CHUNK_SIZE=16, CHUNK_HEIGHT=80 before use.

Let me write it all out now.

Also, I realize for the raycast, I should update camera matrices before casting. Let me call camera.updateMatrixWorld() and camera.updateProjectionMatrix() in updateCamera (called each frame before updateTargets). Actually updateTargets is called after updateCamera in the frame. Let me ensure updateCamera updates matrices.

Let me also make sure raycaster.far is set to 6 (spec: max distance 6). Set raycaster.far = 6.

Wait, raycaster.setFromCamera sets origin=camera.position and direction from camera forward, and far is used to limit intersection distance. Setting raycaster.far=6 limits to 6 units. Good.

Let me finalize.

One more consideration: The player spawns at y = surfaceY + 1.5. If surfaceY is, say, 5 (low area), spawnY = 6.5. Player falls onto surface at y=5 (block occupies [5,6]). Feet should rest at 6. Starting at 6.5, falls to 6.0 (rests on top of block whose top is at 6). Collision: player box [y, y+1.8]. When y=6, box [6,7.8]. Block at y=5 occupies [5,6]. Does box [6,7.8] overlap [5,6]? They touch at 6 but floor(6)=6, block at y=6? No, surface block at y=5. The block above surface is at y=6 (air). Player box minY=6, maxY=7.8. Checks blocks y=6,7. Both air (assuming). So player would fall through?! 

Wait, collision checks blocks from floor(py) to floor(py+1.8). If py=6, floor(6)=6, floor(7.8)=7. Blocks at y=6,7. Surface block is at y=5 (occupies [5,6]). The player's box bottom is at y=6, which is the top surface of the y=5 block. The player occupies [6,7.8]. The block at y=5 is [5,6] — does [6,7.8] overlap [5,6]? Overlap requires intervals to intersect in more than a point. [6,7.8] and [5,6] share only the point 6. floor(6)=6 means we check block at integer y=6, not y=5. So we don't detect the y=5 block. Player falls through.

The issue: when player rests exactly on top of a block at y=5 (top at 6), player feet at 6, but collision checks block at y=6 (air) not y=5. So player sinks until... Actually player continues falling: py slightly less than 6, floor(py)=5, checks block y=5 (solid) → collision. So player settles at py where floor(py)=5, i.e., py in [5,6). Specifically, player falls until py reaches 5 (then floor=5, collides) — but wait at py=5.99, floor=5, block y=5 solid → collide, vy=0, onGround. So player rests at py≈5.99? Actually the collision triggers when moving down into a block. Let me trace: player at py=6.5, falling. Each frame py decreases. When py is such that box [py, py+1.8] overlaps block [5,6]: overlap when py < 6 and py+1.8 > 5, i.e., py < 6. So when py drops below 6 (e.g., 5.99), floor(5.99)=5, block y=5 is solid → collide. Player stops with py≈5.99 (just below 6). Actually the exact resting position: py settles just below 6, floor=5, resting on top of block at y=5. Feet at ~5.99, which is essentially the top of the block (6). Good, that's correct! The player stands on top of the surface block. 

Wait, but at py=5.99, the box is [5.99, 7.79]. floor min = 5, max = 7. Blocks y=5 (solid),6,7 (air). Since y=5 is solid and overlaps (box includes y=5 region [5.99..7.79], block [5,6], overlap [5.99,6]) → collide. Stops. Feet at 5.99 ≈ 6 = top of surface block. Correct!

But hold on, at py=6.0 exactly, box [6,7.8], floor 6..7, no overlap → would fall through. But gravity moves py from 6.5 to 6.5 - vy*dt each frame; it'll step to like 6.4, 6.2, ... 5.9 quickly, detecting collision at 5.99. Actually it steps discretely; when it steps to a value < 6, collision detected. So it won't sit exactly at 6.0; it'll be just below. Fine. Player stands on surface. 

Actually, let me reconsider: does the player rest with feet at ~6 (top of surface block at y=5)? Yes. Eye at 6.99. Good, looking slightly down at the surface. Fine.

Alternatively, I could spawn higher to be safe, but this works. Let me keep spawnY = surfaceY + 1.5. Actually, to be safe from the exact-boundary issue, let me spawn a bit higher: surfaceY + 2. Player falls ~2 units and lands. Fine. Actually 1.5 is fine.

Hmm, wait, but there's a subtlety: what if the block just above surface (y = surfaceY+1) is also solid (e.g., a tree leaf or the surface is at the max and there's nothing above)? Usually above surface is air. Fine.

Let me also reconsider: what if surfaceY is such that spawnY places player inside a hill? No, spawnY = surfaceY+1.5 > surfaceY+1, so above the surface block. Good.

Now let me also make sure that when the player first spawns, the block they stand on is generated (chunk 0,0 generated at startup). Yes.

Alright, writing final code.

Let me reconsider performance of updateChunks generating 4 chunks/frame with full meshing deferred. Data gen for 4 chunks = 4*20480 = 81920 blocks, each computing fractal2 (2 calls) + cave noise (1 call) + occasional tree. fractal2 = 4 octaves * (4 hashes + interpolations). So ~ per block: 2*4=8 hashes for fractal, 1 hash for cave, plus tree hash occasionally. ~10-11 hashes per block * 81920 = ~900K hash calls/frame. Each hash is a few mul/xor ops. ~5M ops/frame. At 60fps that's 300M ops/sec — modern CPUs do billions/sec, so ~a few ms. Fine.

Meshing 2 chunks/frame: each up to 20480 blocks * 6 faces * neighbor check (getBlock = Map lookup). Worst case all faces exposed: 20480*6*4 vertices = 491520 vertices per chunk, 2 chunks = ~1M vertices. Creating BufferGeometry with 1M floats — allocation overhead ~ few ms. Fine at 2/frame.

Total frame overhead maybe ~10-20ms. Acceptable.

Now let me write.

Actually, let me reconsider: generating data for radius 5 (up to 11x11=121 chunks) but only 4/frame. At 4/frame, to fill radius 5 around a moving player is fine. Initial pre-gen radius 2 (25 chunks) done at startup.

Let me write the file now. I'll include comments sparingly.

Let me make sure to include the three.js script tag with r128.

Let me write it.

Actually, I realize I should double check: `new Float32BufferAttribute` — in r128, Float32BufferAttribute exists (deprecated later but present in r128). Yes, r128 has Float32BufferAttribute. Good. (r128 is before the BufferAttribute rename.)

Let me also use `THREE.BufferGeometry`, `THREE.Mesh`, `THREE.MeshLambertMaterial`, etc. Since THREE is global, I can use BufferGeometry directly (it's global too? No — only THREE is global; BufferGeometry is THREE.BufferGeometry). Let me use THREE.* prefix to be safe. Actually in the global scope, THREE.BufferGeometry. Let me prefix all THREE classes.

Let me write with THREE. prefix everywhere.

Let me now produce the final code.

I'll also add a title "MiniCraft" or "MineClone". Let me use "VoxelCraft".

Let me write the complete HTML.

Double-check: pointer lock on canvas. requestPointerLock() can be called on document or canvas. canvas.requestPointerLock() works. Good.

Let me also handle the case where requestPointerLock fails (some browsers). Wrap in try/catch maybe. Not necessary.

Final code below.

Let me reconsider the overlay click: I attach click to overlay. But overlay covers the canvas; clicking overlay requests lock. Once locked, overlay hidden. On unlock, overlay reappears. Good.

But there's a subtlety: the overlay click also might fire when clicking the "play" button. That's fine, same handler.

Also, I should make sure that when not active, mousemove doesn't rotate. Guarded by gameActive.

Let me also prevent the default on space to avoid scrolling (no scroll anyway). e.preventDefault() on space.

Let me write it all now.

Let me reconsider: keys object initialized with all false. Good.

Also arrow keys? Not required. WASD only.

Let me finalize.

I want to double-check the fractal normalization gives values that produce nice terrain. m = fractal2(wx*0.004,...) in [0,1]. m*m*58: for m=0.5, 0.25*58=14.5. For m=0.9, 0.81*58=47. h=fractal2(wx*0.02,...) in [0,1], h*10. So H = 5 + [0,58] + [0,10]. Mostly between 5 and 73, concentrated around middle. Good, gives plains ~30-50, mountains up to 73 with snow, low areas ~5-16 for beaches/water. 

Now let me write the final file.

Let me make sure about `padStart` availability — ES2017, all modern browsers support. Chrome/Firefox fine.

Let me write.

Actually, let me reconsider whether to clamp pitch to slightly less than 90° to avoid flipping. Use 1.5 (about 86°). Fine.

Let me also make the sensitivity 0.002 as spec says.

Writing now.

Let me also ensure the camera far is 400 as spec. fov 75. near 0.1.

Let me write the final HTML.

Let me reconsider fog: new THREE.Fog(0x87ceeb, 40, 110). Good.

Also sky color scene.background = new THREE.Color(0x87ceeb) or just 0x87ceeb. scene.background = 0x87ceeb works (accepts color). Good.

Final code:

I'll write it out fully now.

Let me reconsider the cloud material opacity and transparency. Use transparent:true, opacity:0.85, color white, and maybe depthWrite false so they sort nicely. Let me set depthWrite:false for clouds and water.

Also for water, depthWrite false so terrain behind shows through properly. Actually water overlaps terrain; with depthWrite false, water draws over terrain without writing depth, so terrain depth remains. Order: draw terrain first (writes depth), then water (no depth write) overlays. But water plane is large and at y=14.3; terrain above it isn't occluded by water (terrain is above water plane). Terrain below 14.3 is underwater — but we don't render underwater rendering, water plane just floats at 14.3 covering low areas. Areas where terrain > 14.3 poke above water (land), areas < 14.3 are covered by water plane visually. Since water plane is at fixed height and large, it covers the low regions. Good.

Depth order: default painter's? Meshes render in order added. Water added after terrain, so renders on top. With depthWrite false, water pixels only fill where depth test passes (water is closer than terrain behind it? They're at different depths). Actually water plane at y=14.3 spans a huge area; where terrain is below 14.3, the terrain is below the water plane, so from camera the water plane is in front of terrain at those pixels? Not necessarily—depends on viewing angle. This is getting complex. For a visual-only water, it's fine to just have the plane. Let me set depthWrite:false, transparent, and render after terrain. Good enough.

Let me finalize.

Actually, one concern: the water plane is 400x400 at player position, so it always extends beyond visible terrain (fog ends at 110, plane half-size 200). Good, covers view.

Let me write final.

Let me also double check: I need to make sure that when the player looks down at ground, the raycast hits and target shows. Raycast from camera center forward 6 units. Ground within 6 units in front/below. Since pitch can look down, the forward ray will hit ground ahead. Good.

Also, the outline should only show when there's a valid target (within range). Good.

Let me write the complete file now. I'll be comprehensive.

Let me reconsider: do I need to update camera matrices each frame for raycast? Yes. In updateCamera I set position and rotation, then call camera.updateProjectionMatrix() and camera.updateMatrixWorld(). Actually updateMatrixWorld updates matrixWorld and matrixWorldInverse. Let me call camera.updateMatrixWorld() and camera.updateProjectionMatrix() in updateCamera. Good.

Now writing.

Let me also ensure the animation loop uses performance.now().

Here's the plan for the frame:
```js
function loop(t) {
  const dt = Math.min((t - last) / 1000, 0.05);
  last = t;
  if (gameActive) {
    updatePlayer(dt);
    updateChunks();
    updateCamera();
    updateTarget();
    updateClouds(dt);
    water.position.x = player.x;
    water.position.z = player.z;
  }
  raf = requestAnimationFrame(loop);
}
```

Good.

Let me write everything out now, carefully.

I'll now produce the final answer.

Wait, I should double check the `idx` for data indexing consistency between generate, getBlock, setBlock, buildChunkGeometry. All use idx(lx,y,lz) = (lx + lz*16)*80 + y. Consistent. Good.

Also getBlock uses localIndex for x and z: localIndex(x) = x - chunkIndex(x)*16. For x in [cx*16, cx*16+15], localIndex gives [0,15]. Good.

Let me also verify chunkIndex for negative: chunkIndex(-1) = floor(-0.0625) = -1. localIndex(-1) = -1 - (-1)*16 = 15. Good.

Now, in getBlock, I compute cx = chunkIndex(x), cz = chunkIndex(z), then key. Then localIndex(x), localIndex(z). Good.

Alright, final code.

Let me also add a fallback: if three.js fails to load, nothing works, but we assume it loads.

Let me write the file.

Also, I want to make sure the outline Line renders. WireframeGeometry produces a geometry with positions only (no normals). LineBasicMaterial ignores normals. Good. Set outline.position and visible.

Let me finalize.

Let me write the complete HTML now.

Actually, let me reconsider the mesh building performance and the fact that we build geometry with arrays and push. For large exposed surface this is fine.

Also, I should set `geom.computeBoundingSphere()`? Not necessary.

Let me write it.

Let me also reconsider: after editing a block, we rebuild the chunk and possibly neighbors. This creates new geometries and disposes old. The old mesh is removed from scene and chunkMeshes (via detachMesh). Good, so raycast uses updated meshes.

But note: when we edit, we call rebuildChunk which disposes and recreates. The mesh.userData.cx/cz preserved (set in makeMesh). Good.

Let me write final code now. I'll produce it.

Let me reconsider the initial meshing: I pre-mesh radius 1 (9 chunks). But meshing requires 4 neighbors with data. At startup I generated radius 2 data, so all radius-1 chunks have data and their neighbors (radius up to 2) have data. So makeMesh directly works. Good.

Now writing.

Let me also make sure I don't reference `selected` before defining. Define selected=0 early.

Also slots array defined after building hotbar. selectSlot(0) at end of hotbar creation.

Let me write the final HTML file.

I think I've covered everything. Let me write it out.

Let me reconsider: the spec says "Keep all chunk meshes in a global array for raycasting". That's chunkMeshes. Good.

Also "write a rebuild function for a chunk" — rebuildChunk. Good.

Also "global read/write block helpers" — getBlock, setBlock. Good.

Let me write.

One more: "Reading a missing chunk or y outside 0–79 returns air." getBlock returns 0 for missing chunk or y out of range. Good.

Let me also make setBlock guard y range and chunk existence. Good.

Alright, final.

Let me write the code and make it robust.

Actually, let me reconsider the meshing neighbor requirement causing a gap: a newly generated chunk adjacent to player but whose neighbor hasn't been generated yet won't be meshed until neighbor has data. Since we generate within radius 5 and mesh within radius 4 requiring neighbor data, and generation happens first each frame, within a couple frames all radius-4 chunks will have data and their neighbors too. Fine.

But there's a subtle issue: a chunk at radius 4 might never get meshed if one of its neighbors is at radius 5 and takes many frames to generate. But as player moves, the player's chunk changes and things stream. It's fine for a demo.

Actually, wait: the meshing loop generates meshes for chunks within radius 4 (of player) whose 4 neighbors have data. The neighbors could be at radius up to 5. If a neighbor at radius 5 hasn't been generated yet (takes up to... well generation is 4/frame covering radius 5 in ~ (11*11)/4 ≈ 30 frames), then the radius-4 chunk waits. But by the time player is near, most chunks are generated. Acceptable.

Let me reduce potential lag: maybe relax to require only that the specific neighbor we read exists. But spec says "whose 4 neighbors already have data". I'll follow spec.

Now let me also make sure the game doesn't crash if chunkMeshes is empty during raycast (early frames). intersectObjects([]) returns []. Fine.

Let me also cap dt to avoid huge jumps.

Let me also ensure requestAnimationFrame loop starts.

Let me also add a subtle: when placing blocks, we shouldn't place inside ourselves. overlapsPlayer handles that.

Let me finalize and write.

Let me reconsider one thing about MeshLambertMaterial and vertexColors: I recall that with vertexColors true and material color white, the final color = vertexColor * light. Good. But some versions require material.color to be white for pure vertex colors. I'll set color 0xffffff.

Also, I should set material.side = THREE.FrontSide (default) — since no culling issues, both sides render. Default is FrontSide but without face culling in Lambert? Actually Lambert renders both sides by default (side FrontSide means only front faces are rendered, but back faces of a closed cube are the inner faces which we don't generate anyway). Since we only generate outer faces with outward normals, FrontSide renders them all (their normals face the camera when visible). But a face whose normal points away from camera (e.g., inside a cave seen from inside) — FrontSide would cull it. Hmm. For caves, looking into a cave, the inner faces have normals pointing into the cavity (toward the center), so from inside the cave they face the viewer → front faces → rendered. Good. For open surfaces, outward normals face viewer when visible. So FrontSide is fine and avoids rendering back faces (which we don't generate anyway). Let me keep default FrontSide. Actually, to be safe and avoid any invisible faces, I could use DoubleSide. But DoubleSide doubles fill rate. Since we only generate outward faces, FrontSide is correct. Let me keep default.

Hmm, wait: consider a single exposed face on the top of a block. Its normal is +Y. If camera looks up, the face is a front face (normal toward camera) → rendered. If camera looks down at it from below, the normal points away → FrontSide culls it → we see through to whatever's below. That's correct behavior (can't see the top of a block from below). Good.

OK FrontSide is fine.

Now, let me also double check: the directional light direction for Lambert. Light at (50,100,30) from origin. Direction = normalize(-(50,100,30)) roughly pointing down-left-forward. The diffuse term is max(0, dot(normal, lightDirection)). For top face normal (0,1,0): dot = -0.89 → max(0,...) = 0. That makes top faces dark! 

Wait, directional light direction: The light emits along its direction toward origin. For a directional light at position (50,100,30), the light points from that position toward the origin, i.e., direction = origin - lightPos = (-50,-100,-30), normalized. So light direction (direction the light travels) is (-0.45,-0.89,-0.27). The diffuse term is max(0, dot(normal, lightDirection)). For top face normal (0,1,0): dot = -0.89 → max(0,...) = 0. That makes top faces dark! Bad.

I want the light to come from above so top faces are lit. So the light direction should have positive Y when dotted with top normal. That means the light should point downward onto the tops... no. Let me think: light direction is the direction from which light comes? In Three.js, DirectionalLight illuminates based on the direction FROM the light TO the surface, i.e., the vector from light position to point. Actually, the diffuse = max(0, dot(normal, L)) where L is the direction from the surface point toward the light. For a directional light, L = normalize(light.position - point) roughly = normalize(light.position) if point is near origin. So L ≈ normalize((50,100,30)) = (0.45,0.89,0.27). Dot with top normal (0,1,0) = 0.89 → bright. 

So placing light at (50,100,30) gives L pointing up-and-right, lighting top faces well. My earlier confusion: L is from surface TO light, which is positive Y. Good. So top faces lit, bottom faces (normal -Y): dot(-Y, L) = -0.89 → 0, so bottom faces get only ambient. Combined with fake lighting 0.55 * ambient... let me check overall brightness.

Ambient 0.65 applies to all faces (diffuse ambient). Directional adds diffuse where dot>0. So:
- Top face: ambient 0.65 + directional 0.8*0.89 = 0.65+0.71 = 1.36, times fake 1.0 → bright.
- Side face: ambient 0.65 + directional*dot. Side normal (1,0,0): dot(L)=(0.45) → 0.8*0.45=0.36. total 1.01, times fake 0.8 = 0.81.
- Bottom face: ambient 0.65 + directional 0 (dot negative) = 0.65, times fake 0.55 = 0.36.

So top brightest, sides medium, bottom darkest. Looks 3D. Good.

But note the directional adds variation based on orientation relative to light, which is fine and adds realism. Good.

Actually, wait — I want to double-check the fake lighting is applied multiplicatively to the base color, and then Lambert multiplies again by lighting. So final = baseColor * fakeMult * (ambient + directionalDiffuse). Since ambient is 0.65 baseline, nothing goes fully black. Good. Colors remain recognizable.

Alright. Let me also make sure the material isn't too dark. With these values, min ~0.36 * base. Fine.

Now let me write the complete file.

I'll write it out in full now.

Let me reconsider the structure to keep it organized:

1. HTML head with CSS
2. Body: canvas, overlay, crosshair, hotbar
3. Script: three.js, then game code.

Let me write.

Actually, the canvas can be created in JS and appended, or in HTML. Let me create in HTML for simplicity: <canvas id="c"></canvas>.

Let me write the final file.

I need to be careful that everything is defined before use. Let me order: constants, helpers, THREE setup, scene objects, chunk functions, player, input, UI, init, loop.

Writing now.

Let me also make sure to handle the case where three.js fails to load, nothing works, but we assume it loads.

Let me write the file.

Let me reconsider: the spec says "Load only Three.js r128". So single script tag. Good.

Final answer below.

Let me write it all out carefully, making sure syntax is correct.

I'll produce the code block now.

Let me reconsider the `idx` function name — it's fine as a function.

Let me also double-check `Float32BufferAttribute` exists in r128. Yes, r128 has it (renamed to Float32Attribute in r125+? No). Actually the rename to `Float32Attribute` happened in r125. Wait: In r125, BufferAttribute was renamed to Float32Attribute and deprecated Float32BufferAttribute? Let me recall. 

Three.js r125 (Dec 2020): Introduced `BufferAttribute`, `InterleavedAttribute`, etc.? Actually the big rename to generic `BufferAttribute` was in r154 (2022). Before that, the typed variants were `Float32BufferAttribute`, `Int8BufferAttribute`, etc. The rename to `BufferAttribute` with itemSize came in r154. So in r128, `Float32BufferAttribute` is correct and available. Good.

Let me confirm: r128 is June 2021. At that time, `THREE.Float32BufferAttribute` existed (deprecated later in r154). Yes. Good.

Writing now.

Let me also ensure I import the CDN URL exactly: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js. Good.

Final code:

Let me write the complete thing.

I'll now produce the final HTML.

Let me reconsider the overlay click: I attach click to overlay. But overlay covers the canvas; clicking overlay requests lock. Once locked, overlay hidden. On unlock, overlay reappears. Good.

But there's a subtlety: the overlay click also might fire when clicking the "play" button. That's fine, same handler.

Also, I should make sure that when not active, mousemove doesn't rotate. Guarded by gameActive.

Let me finalize.

Let me also make sure to prevent the default on space to avoid scrolling (no scroll anyway). e.preventDefault() on space.

Let me write it all now.

Let me reconsider: keys object initialized with all false. Good.

Also arrow keys? Not required. WASD only.

Let me finalize.

I want to double-check the fractal normalization gives values that produce nice terrain. m = fractal2(wx*0.004,...) in [0,1]. m*m*58: for m=0.5, 0.25*58=14.5. For m=0.9, 0.81*58=47. h=fractal2(wx*0.02,...) in [0,1], h*10. So H = 5 + [0,58] + [0,10]. Mostly between 5 and 73, concentrated around middle. Good, gives plains ~30-50, mountains up to 73 with snow, low areas ~5-16 for beaches/water. 

Now let me write the final file.

Let me make sure about `padStart` availability — ES2017, all modern browsers support. Chrome/Firefox fine.

Let me write.

Actually, let me reconsider whether to clamp pitch to slightly less than 90° to avoid flipping. Use 1.5 (about 86°). Fine.

Let me also make the sensitivity 0.002 as spec says.

Writing now.

Let me also ensure the camera far is 400 as spec. fov 75. near 0.1.

Let me write the final HTML.

Let me reconsider fog: new THREE.Fog(0x87ceeb, 40, 110). Good.

Also sky color scene.background = new THREE.Color(0x87ceeb) or just 0x87ceeb. scene.background = 0x87ceeb works (accepts color). Good.

Final code:

I'll write it out fully now.

Let me reconsider: I need to make sure that when the player looks down at ground, the raycast hits and target shows. Raycast from camera center forward 6 units. Ground within 6 units in front/below. Since pitch can look down, the forward ray will hit ground ahead. Good.

Also, the outline should only show when there's a valid target (within range). Good.

Let me write the complete file now.

I'll now produce the final answer.
</think>

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>VoxelCraft</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #000; font-family: monospace; }
  canvas { display: block; }
  #overlay {
    position: fixed; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; background: rgba(0,0,0,0.78);
    color: #fff; text-align: center; z-index: 10; cursor: pointer;
  }
  #overlay h1 { font-size: 52px; letter-spacing: 4px; margin-bottom: 22px;
    text-shadow: 4px 4px 0 #222; }
  #overlay ul { list-style: none; font-size: 16px; line-height: 1.9; margin-bottom: 28px; opacity: 0.92; }
  #overlay .play { padding: 12px 34px; border: 3px solid #fff; font-size: 20px;
    border-radius: 8px; background: rgba(255,255,255,0.06); }
  #crosshair { position: fixed; left: 50%; top: 50%; transform: translate(-50%,-50%);
    width: 20px; height: 20px; pointer-events: none; z-index: 5; }
  #crosshair::before, #crosshair::after { content:''; position:absolute; background: rgba(255,255,255,0.85); }
  #crosshair::before { left: 9px; top: 0; width: 2px; height: 20px; }
  #crosshair::after  { top: 9px; left: 0; height: 2px; width: 20px; }
  #hotbar { position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%);
    display: flex; gap: 6px; padding: 6px; background: rgba(0,0,0,0.55);
    border-radius: 8px; z-index: 5; pointer-events: none; }
  .slot { width: 46px; height: 46px; border: 3px solid #333; border-radius: 6px;
    position: relative; display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: bold; text-shadow: 1px 1px 2px #000; }
  .slot.sel { border-color: #fff; box-shadow: 0 0 7px #fff; }
  .slot .num { position: absolute; top: 1px; left: 3px; font-size: 12px; }
</style>
</head>
<body>
<div id="overlay">
  <h1>VOXELCRAFT</h1>
  <ul>
    <li>WASD — move &nbsp;•&nbsp; Mouse — look &nbsp;•&nbsp; Space — jump</li>
    <li>Left click — break &nbsp;•&nbsp; Right click — place</li>
    <li>1–7 or mouse wheel — select block</li>
  </ul>
  <div class="play">Click to play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
"use strict";

/* ---------- constants ---------- */
const CHUNK_SIZE = 16;
const CHUNK_HEIGHT = 80;
const GRAVITY = 25, JUMP = 8.5, SPEED = 5.5;
const BLOCK_COLOR = [0x000000,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];

/* ---------- deterministic value noise ---------- */
function hash2(ix, iy) {
  let h = (Math.imul(ix, 374761393) + Math.imul(iy, 668265263) + 1013904223) | 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
function hash3(ix, iy, iz) {
  let h = (Math.imul(ix, 374761393) + Math.imul(iy, 668265263) + Math.imul(iz, 0x51ea7c93) + 1013904223) | 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
function columnHash(ix, iz) {
  let h = (Math.imul(ix, 2654435761) + Math.imul(iz, 2246822519) + 3948271) | 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
function noise2(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf*xf*(3-2*xf), v = yf*yf*(3-2*yf);
  const a = hash2(xi, yi), b = hash2(xi+1, yi);
  const c = hash2(xi, yi+1), d = hash2(xi+1, yi+1);
  const top = a + (b-a)*u, bot = c + (d-c)*u;
  return top + (bot-top)*v;
}
function fractal2(x, y) {
  let sum = 0, amp = 1, freq = 1, total = 0;
  for (let o = 0; o < 4; o++) { sum += amp * noise2(x*freq, y*freq); total += amp; freq *= 2; amp *= 0.5; }
  return sum / total;
}
function noise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x-xi, yf = y-yi, zf = z-zi;
  const u = xf*xf*(3-2*xf), v = yf*yf*(3-2*yf), w = zf*zf*(3-2*zf);
  const c000=hash3(xi,yi,zi),   c100=hash3(xi+1,yi,zi);
  const c010=hash3(xi,yi+1,zi), c110=hash3(xi+1,yi+1,zi);
  const c001=hash3(xi,yi,zi+1), c101=hash3(xi+1,yi,zi+1);
  const c011=hash3(xi,yi+1,zi+1), c111=hash3(xi+1,yi+1,zi+1);
  const x00=c000+(c100-c000)*u, x10=c010+(c110-c010)*u;
  const x01=c001+(c101-c001)*u, x11=c011+(c111-c011)*u;
  const xy0=x00+(x10-x00)*v, xy1=x01+(x11-x01)*v;
  return xy0+(xy1-xy0)*w;
}

/* ---------- chunk storage & block helpers ---------- */
const chunks = new Map(); // "cx,cz" -> { data:Uint8Array, mesh:Mesh }
function idx(lx, y, lz) { return (lx + lz * CHUNK_SIZE) * CHUNK_HEIGHT + y; }
function chunkIndex(world) { return Math.floor(world / CHUNK_SIZE); }
function localIndex(world) { return world - chunkIndex(world) * CHUNK_SIZE; }
function hasData(cx, cz) { const c = chunks.get(cx+','+cz); return !!(c && c.data); }
function getBlock(x, y, z) {
  if (y < 0 || y >= CHUNK_HEIGHT) return 0;
  const c = chunks.get(chunkIndex(x)+','+chunkIndex(z));
  if (!c || !c.data) return 0;
  return c.data[idx(localIndex(x), y, localIndex(z))];
}
function setBlock(x, y, z, id) {
  if (y < 0 || y >= CHUNK_HEIGHT) return;
  const c = chunks.get(chunkIndex(x)+','+chunkIndex(z));
  if (!c || !c.data) return;
  c.data[idx(localIndex(x), y, localIndex(z))] = id;
}

/* ---------- terrain generation ---------- */
function placeLeafIn(data, lx, ly, lz, id) {
  if (lx<0||lx>=CHUNK_SIZE||lz<0||lz>=CHUNK_SIZE||ly<0||ly>=CHUNK_HEIGHT) return;
  if (data[idx(lx,ly,lz)] === 0) data[idx(lx,ly,lz)] = id;
}
function generateChunkData(cx, cz) {
  const data = new Uint8Array(CHUNK_SIZE*CHUNK_SIZE*CHUNK_HEIGHT);
  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      const wx = cx*CHUNK_SIZE + lx, wz = cz*CHUNK_SIZE + lz;
      const m = fractal2(wx*0.004, wz*0.004);
      const h = fractal2(wx*0.02,  wz*0.02);
      const H = Math.floor(5 + m*m*58 + h*10);
      for (let y = 0; y <= H; y++) {
        let id;
        if (y === 0 || y < H-3) id = 3;                       // bedrock / deep stone
        else if (y < H) {                                      // 3 layers under surface
          if (H <= 16) id = 4; else if (H >= 37) id = 3; else id = 2;
        } else {                                               // surface
          if (H >= 46) id = 7; else if (H >= 37) id = 3; else if (H <= 16) id = 4; else id = 1;
        }
        data[idx(lx, y, lz)] = id;
      }
      for (let y = 3; y < H-2; y++) {                          // caves
        if (noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) data[idx(lx, y, lz)] = 0;
      }
      if (data[idx(lx, H, lz)] === 1 && H + 8 < CHUNK_HEIGHT && columnHash(wx, wz) < 0.02) {
        for (let y = H+1; y <= H+4; y++) data[idx(lx, y, lz)] = 5; // trunk
        for (let dx = -2; dx <= 2; dx++)
          for (let dz = -2; dz <= 2; dz++) {
            placeLeafIn(data, lx+dx, H+5, lz+dz, 6);
            placeLeafIn(data, lx+dx, H+6, lz+dz, 6);
          }
        for (let dx = -1; dx <= 1; dx++)
          for (let dz = -1; dz <= 1; dz++) placeLeafIn(data, lx+dx, H+7, lz+dz, 6);
        placeLeafIn(data, lx, H+8, lz, 6);
      }
    }
  }
  return data;
}

/* ---------- meshing ---------- */
const FACES = [
  { n:[1,0,0],  v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  { n:[-1,0,0], v:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  { n:[0,1,0],  v:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { n:[0,-1,0], v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { n:[0,0,1],  v:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
  { n:[0,0,-1], v:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] }
];
function buildChunkGeometry(cx, cz) {
  const c = chunks.get(cx+','+cz);
  const pos = [], nor = [], col = [];
  const wx0 = cx*CHUNK_SIZE, wz0 = cz*CHUNK_SIZE;
  for (let lx = 0; lx < CHUNK_SIZE; lx++) {
    for (let lz = 0; lz < CHUNK_SIZE; lz++) {
      for (let y = 0; y < CHUNK_HEIGHT; y++) {
        const id = c.data[idx(lx, y, lz)];
        if (!id) continue;
        const wx = wx0 + lx, wz = wz0 + lz;
        const base = BLOCK_COLOR[id];
        const r = (base>>16)&255, g = (base>>8)&255, b = base&255;
        for (let f = 0; f < 6; f++) {
          const face = FACES[f];
          const nx = wx + face.n[0], ny = y + face.n[1], nz = wz + face.n[2];
          if (getBlock(nx, ny, nz)) continue;                 // neighbor solid -> skip face
          let mult = 0.8;
          if (face.n[1] === 1) mult = 1.0;
          else if (face.n[1] === -1) mult = 0.55;
          const cr = r*mult, cg = g*mult, cb = b*mult;
          const vv = face.v;
          for (let i = 0; i < 4; i++) {
            pos.push(wx+vv[i][0], y+vv[i][1], wz+vv[i][2]);
            nor.push(face.n[0], face.n[1], face.n[2]);
            col.push(cr, cg, cb);
          }
        }
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal',   new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('color',    new THREE.Float32BufferAttribute(col, 3));
  return g;
}

/* ---------- scene, camera, lights ---------- */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(50, 100, 30);
scene.add(sun);

const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true, color: 0xffffff, side: THREE.FrontSide });

/* ---------- chunk management ---------- */
const chunkMeshes = [];
function attachMesh(mesh) { scene.add(mesh); chunkMeshes.push(mesh); }
function detachMesh(mesh) {
  scene.remove(mesh);
  const i = chunkMeshes.indexOf(mesh);
  if (i >= 0) chunkMeshes.splice(i, 1);
  mesh.geometry.dispose();
}
function rebuildChunk(cx, cz) {
  const c = chunks.get(cx+','+cz);
  if (!c || !c.data) return;
  if (c.mesh) detachMesh(c.mesh);
  const mesh = new THREE.Mesh(buildChunkGeometry(cx, cz), blockMaterial);
  mesh.userData.cx = cx; mesh.userData.cz = cz;
  c.mesh = mesh;
  attachMesh(mesh);
}
function updateChunks() {
  const pcx = chunkIndex(player.x), pcz = chunkIndex(player.z);

  // generate block data for chunks within radius 5 (max 4/frame)
  let gen = 0;
  for (let dz = -5; dz <= 5 && gen < 4; dz++) {
    for (let dx = -5; dx <= 5; dx++) {
      const cx = pcx+dx, cz = pcz+dz, key = cx+','+cz;
      const c = chunks.get(key);
      if (c && c.data) continue;
      const data = generateChunkData(cx, cz);
      if (c) c.data = data; else chunks.set(key, { data:data, mesh:null });
      gen++;
    }
  }

  // build meshes for chunks within radius 4 whose 4 neighbors have data (max 2/frame)
  let mes = 0;
  for (let dz = -4; dz <= 4 && mes < 2; dz++) {
    for (let dx = -4; dx <= 4; dx++) {
      const cx = pcx+dx, cz = pcz+dz, key = cx+','+cz;
      const c = chunks.get(key);
      if (!c || !c.data || c.mesh) continue;
      if (!hasData(cx+1,cz) || !hasData(cx-1,cz) || !hasData(cx,cz+1) || !hasData(cx,cz-1)) continue;
      const mesh = new THREE.Mesh(buildChunkGeometry(cx, cz), blockMaterial);
      mesh.userData.cx = cx; mesh.userData.cz = cz;
      c.mesh = mesh;
      attachMesh(mesh);
      mes++;
    }
  }

  // remove chunks farther than 7
  const del = [];
  for (const [key, c] of chunks) {
    const p = key.split(',');
    const cx = +p[0], cz = +p[1];
    if (Math.abs(cx-pcx) > 7 || Math.abs(cz-pcz) > 7) del.push(key);
  }
  for (const key of del) {
    const c = chunks.get(key);
    if (c.mesh) detachMesh(c.mesh);
    chunks.delete(key);
  }
}

/* ---------- clouds & water ---------- */
const clouds = [];
for (let i = 0; i < 25; i++) {
  const g = new THREE.BoxGeometry(6 + hash2(i,0)*10, 1.5, 5 + hash2(i,2)*8);
  const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color:0xffffff, transparent:true, opacity:0.85, depthWrite:false }));
  m.userData.offset = i * 137.5;
  m.userData.speed = 0.3 + hash2(i,1)*0.4;
  m.userData.radius = 28 + (i % 5) * 22;
  m.userData.yoff = (i % 3) * 3;
  scene.add(m); clouds.push(m);
}
const water = new THREE.Mesh(new THREE.PlaneGeometry(420, 420),
  new THREE.MeshLambertMaterial({ color:0x3388ff, transparent:true, opacity:0.6, depthWrite:false }));
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);

/* ---------- outline ---------- */
const outline = new THREE.Line(
  new THREE.WireframeGeometry(new THREE.BoxGeometry(1.02, 1.02, 1.02)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

/* ---------- player ---------- */
const player = { x:8, y:40, z:8, vy:0, onGround:false, yaw:0, pitch:0 };
let spawnX = 8, spawnY = 40, spawnZ = 8;

function collides(px, py, pz) {
  const minX = Math.floor(px-0.3), maxX = Math.floor(px+0.3);
  const minY = Math.floor(py),     maxY = Math.floor(py+1.8);
  const minZ = Math.floor(pz-0.3), maxZ = Math.floor(pz+0.3);
  for (let x = minX; x <= maxX; x++)
    for (let y = minY; y <= maxY; y++)
      for (let z = minZ; z <= maxZ; z++)
        if (getBlock(x, y, z)) return true;
  return false;
}
function overlapsPlayer(fx, fy, fz) {
  return !(fx+1 < player.x-0.3 || fx > player.x+0.3 ||
           fy+1 < player.y      || fy > player.y+1.8 ||
           fz+1 < player.z-0.3 || fz > player.z+0.3);
}
function editBlock(bx, by, bz, id) {
  setBlock(bx, by, bz, id);
  const cx = chunkIndex(bx), cz = chunkIndex(bz);
  rebuildChunk(cx, cz);
  const lx = localIndex(bx), lz = localIndex(bz);
  if (lx === 0) rebuildChunk(cx-1, cz);
  if (lx === CHUNK_SIZE-1) rebuildChunk(cx+1, cz);
  if (lz === 0) rebuildChunk(cx, cz-1);
  if (lz === CHUNK_SIZE-1) rebuildChunk(cx, cz+1);
}

/* ---------- input ---------- */
const keys = {};
let gameActive = false;
const overlay = document.getElementById('overlay');
const canvas = document.querySelector('canvas') || (() => { const c = document.createElement('canvas'); document.body.appendChild(c); return c; })();

document.addEventListener('pointerlockchange', () => {
  if (document.pointerLockElement === canvas) { overlay.style.display = 'none'; gameActive = true; }
  else { overlay.style.display = 'flex'; gameActive = false; }
});
overlay.addEventListener('click', () => { try { canvas.requestPointerLock(); } catch(e){} });

document.addEventListener('mousemove', (e) => {
  if (!gameActive) return;
  player.yaw -= e.movementX * 0.002;
  player.pitch = Math.max(-1.55, Math.min(1.55, player.pitch - e.movementY * 0.002));
});
window.addEventListener('keydown', (e) => {
  keys[e.code] = true;
  if (e.code >= 'Digit1' && e.code <= 'Digit7') selectSlot(+e.code.slice(5) - 1);
  if (e.code === 'Space') e.preventDefault();
});
window.addEventListener('keyup', (e) => { keys[e.code] = false; });
window.addEventListener('wheel', (e) => {
  if (!gameActive) return;
  selectSlot(selected + (e.deltaY > 0 ? 1 : -1));
}, { passive: true });

const raycaster = new THREE.Raycaster();
raycaster.far = 6;
let hitPoint = new THREE.Vector3(), hitNormal = new THREE.Vector3();
let target = null;
function updateTarget() {
  raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
  const near = [];
  const pcx = chunkIndex(player.x), pcz = chunkIndex(player.z);
  for (const m of chunkMeshes)
    if (Math.abs(m.userData.cx - pcx) <= 1 && Math.abs(m.userData.cz - pcz) <= 1) near.push(m);
  const hits = raycaster.intersectObjects(near, false);
  if (hits.length > 0) {
    hitPoint.copy(hits[0].point);
    hitNormal.copy(hits[0].face.normal);
    target = [
      Math.floor(hitPoint.x - hitNormal.x*0.5),
      Math.floor(hitPoint.y - hitNormal.y*0.5),
      Math.floor(hitPoint.z - hitNormal.z*0.5)
    ];
  } else { target = null; }
  outline.visible = target !== null;
  if (target) outline.position.set(target[0]+0.5, target[1]+0.5, target[2]+0.5);
}

canvas.addEventListener('mousedown', (e) => {
  if (!gameActive) return;
  if (e.button === 0) {
    if (target && target[1] !== 0) editBlock(target[0], target[1], target[2], 0);
  } else if (e.button === 2) {
    if (hit) {
      const px = Math.floor(hitPoint.x + hitNormal.x*0.5);
      const py = Math.floor(hitPoint.y + hitNormal.y*0.5);
      const pz = Math.floor(hitPoint.z + hitNormal.z*0.5);
      if (getBlock(px, py, pz) === 0 && !overlapsPlayer(px, py, pz)) editBlock(px, py, pz, selected + 1);
    }
  }
});
canvas.addEventListener('contextmenu', (e) => e.preventDefault());

/* ---------- hotbar ---------- */
const selected = 0; // will be reassigned below
let selected = 0;
const hotbar = document.getElementById('hotbar');
const slots = [];
for (let i = 0; i < 7; i++) {
  const s = document.createElement('div');
  s.className = 'slot';
  s.style.background = '#' + BLOCK_COLOR[i+1].toString(16).padStart(6, '0');
  s.innerHTML = '<span class="num">' + (i+1) + '</span>';
  hotbar.appendChild(s); slots.push(s);
}
function selectSlot(i) {
  selected = ((i % 7) + 7) % 7;
  for (let s = 0; s < 7; s++) slots[s].classList.toggle('sel', s === selected);
}

/* ---------- init world ---------- */
for (let dz = -2; dz <= 2; dz++)
  for (let dx = -2; dx <= 2; dx++)
    chunks.set(dx+','+dz, { data: generateChunkData(dx, dz), mesh: null });
for (let dz = -1; dz <= 1; dz++)
  for (let dx = -1; dx <= 1; dx++) {
    const mesh = new THREE.Mesh(buildChunkGeometry(dx, dz), blockMaterial);
    mesh.userData.cx = dx; mesh.userData.cz = dz;
    chunks.get(dx+','+dz).mesh = mesh;
    attachMesh(mesh);
  }
let surfaceY = 20;
for (let y = CHUNK_HEIGHT-1; y >= 0; y--) { if (getBlock(8, y, 8) !== 0) { surfaceY = y; break; } }
spawnY = surfaceY + 1.5;
player.x = 8; player.y = spawnY; player.z = 8;

/* ---------- main loop ---------- */
let last = performance.now();
function loop(t) {
  const dt = Math.min((t - last) / 1000, 0.05);
  last = t;
  if (gameActive) {
    let fw = 0, rt = 0;
    if (keys['KeyW']) fw -= 1; if (keys['KeyS']) fw += 1;
    if (keys['KeyD']) rt += 1;  if (keys['KeyA']) rt -= 1;
    const sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
    let vx = (-sin*fw + cos*rt) * SPEED;
    let vz = (-cos*fw - sin*rt) * SPEED;

    let nx = player.x + vx*dt; if (!collides(nx, player.y, player.z)) player.x = nx;
    let nz = player.z + vz*dt; if (!collides(player.x, player.y, nz)) player.z = nz;

    player.vy -= GRAVITY * dt;
    if (keys['Space'] && player.onGround) { player.vy = JUMP; player.onGround = false; }
    let ny = player.y + player.vy*dt;
    if (!collides(player.x, ny, player.z)) { player.y = ny; player.onGround = false; }
    else { if (player.vy < 0) player.onGround = true; player.vy = 0; }

    if (player.y < spawnY - 20) { player.x = spawnX; player.y = spawnY; player.z = spawnZ; player.vy = 0; }

    updateChunks();
    camera.position.set(player.x, player.y + 1.62, player.z);
    camera.rotation.set(player.pitch, player.yaw, 0, 'YXZ');
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld();
    updateTarget();

    for (const c of clouds) {
      c.userData.offset += c.userData.speed * dt;
      c.position.x = player.x + Math.cos(c.userData.offset) * c.userData.radius;
      c.position.z = player.z + Math.sin(c.userData.offset) * c.userData.radius;
      c.position.y = 90 + c.userData.yoff;
    }
    water.position.x = player.x;
    water.position.z = player.z;
  }
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
</script>
</body>
</html>
```