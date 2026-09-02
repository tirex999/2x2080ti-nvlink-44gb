Let me build this Minecraft clone carefully. I need to write a complete, single-file HTML with Three.js r128.

Let me plan out all the components based on the spec:

1. **HTML/CSS structure**: Fullscreen canvas, crosshair, hotbar, start overlay
2. **Three.js setup**: Camera, renderer, lights, sky, fog
3. **Value noise**: Hash function, bilinear interpolation, smoothstep, fractal noise, 3D noise
4. **Chunk system**: 16x16x80 chunks, Map storage
5. **Meshing**: BufferGeometry per chunk, face culling
6. **Terrain generation**: Column height, fill, caves, trees
7. **Player physics**: Camera, gravity, collision, movement
8. **Break/place**: Raycasting, outline
9. **Hotbar**: 7 slots
10. **Clouds, water**

Let me write this carefully.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MC</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #87ceeb; }
  canvas { display: block; }
  
  #crosshair {
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 20px; height: 20px;
    pointer-events: none;
    z-index: 10;
  }
  #crosshair::before, #crosshair::after {
    content: '';
    position: absolute;
    background: rgba(0,0,0,0.7);
  }
  #crosshair::before {
    top: 50%; left: 0;
    width: 100%; height: 2px;
    transform: translateY(-50%);
  }
  #crosshair::after {
    left: 50%; top: 0;
    height: 100%; width: 2px;
    transform: translateX(-50%);
  }
  
  #hotbar {
    position: fixed;
    bottom: 20px; left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 4px;
    padding: 6px;
    background: rgba(0,0,0,0.55);
    border-radius: 6px;
    z-index: 10;
    pointer-events: none;
  }
  .slot {
    width: 46px; height: 46px;
    border: 2px solid rgba(255,255,255,0.35);
    border-radius: 4px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: monospace;
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px black;
  }
  .slot .num {
    position: absolute;
    top: 1px; left: 3px;
    font-size: 12px;
  }
  .slot.selected {
    border-color: white;
    box-shadow: 0 0 6px white;
  }
  
  #overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.75);
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 20;
    font-family: sans-serif;
    text-align: center;
  }
  #overlay h1 { font-size: 48px; margin-bottom: 20px; letter-spacing: 2px; }
  #overlay ul { text-align: left; font-size: 16px; line-height: 1.8; margin-bottom: 24px; }
  #overlay .play {
    font-size: 22px;
    padding: 12px 28px;
    border: 2px solid white;
    border-radius: 8px;
    cursor: pointer;
  }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MC</h1>
  <ul>
    <li>WASD — move</li>
    <li>Mouse — look</li>
    <li>Space — jump</li>
    <li>Left click — break block</li>
    <li>Right click — place block</li>
    <li>1-7 / wheel — select block</li>
  </ul>
  <div class="play">Click to play</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ... game code
</script>
</body>
</html>
```

Now let me write the game logic. Let me think through each part carefully.

### Noise functions

```js
function hash(ix, iy) {
  // deterministic hash -> 0..1
  let h = ix * 374761393 + iy * 668265263;
  h = (h ^ (h >>> 13)) * 1274126177;
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}

function hash3(ix, iy, iz) {
  let h = ix * 374761393 + iy * 668265263 + iz * 668265263;
  h = (h ^ (h >>> 13)) * 1274126177;
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

Wait, let me be careful with the hash. The spec says "mix with large prime multipliers and xor-shifts". Let me make a good hash.

```js
function hash(ix, iy) {
  let h = (ix * 374761393 + iy * 668265263) | 0;
  h = Math.imul(h ^ (h >>> 16), 0x89e7d5ddbf8ad4c1);
  h = Math.imul(h ^ (h >>> 13), 0x89e7d5ddbf8ad4c1);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

Hmm, Math.imul might be slow but fine. Actually let me just use simpler arithmetic with bitwise ops to avoid issues.

Actually, let me use a straightforward approach:

```js
function hash(ix, iy) {
  let h = (ix * 374761393 + iy * 668265263);
  h = (h ^ (h >>> 13));
  h = (Math.imul(h, 1274126177));
  h = (h ^ (h >>> 16));
  return (h >>> 0) / 4294967296;
}
```

This should give a decent distribution.

For bilinear interpolation:

```js
function smoothstep(t) {
  return t * t * (3 - 2 * t);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function noise2(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = smoothstep(xf), v = smoothstep(yf);
  const a = hash(xi, yi);
  const b = hash(xi + 1, yi);
  const c = hash(xi, yi + 1);
  const d = hash(xi + 1, yi + 1);
  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}

function fractal2(x, y, octaves) {
  let amp = 0.5, freq = 1, sum = 0, norm = 0;
  for (let i = 0; i < octaves; i++) {
    sum += amp * noise2(x * freq, y * freq);
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / norm;
}
```

For 3D cave noise:

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
function columnHeight(cx, cz) {
  const m = fractal2(cx * 0.004, cz * 0.004, 4);
  const h = fractal2(cx * 0.02, cz * 0.02, 4);
  return Math.floor(5 + m * m * 58 + h * 10);
}
```

Fill logic given height H:
- y = 0: stone (unbreakable)
- below H-3: stone
- 3 layers under surface: dirt (sand if H <= 16, stone if H >= 37)
- surface: snow if H >= 46, stone if H >= 37, sand if H <= 16, else grass

Let me define a function that returns the block type at a given position:

```js
function blockAt(cx, cy, cz) {
  // cx, cy, cz are world coordinates
  // returns block ID
  const H = columnHeight(cx, cz);
  if (cy === 0) return 3; // stone unbreakable
  if (cy < H - 3) return 3; // stone deep
  // caves
  if (cy >= 3 && cy < H - 2) {
    if (noise3(cx * 0.09, cy * 0.09, cz * 0.09) > 0.67) return 0; // air
  }
  // surface layers
  if (cy >= H) {
    // surface
    if (H >= 46) return 7; // snow
    if (H >= 37) return 3; // stone
    if (H <= 16) return 4; // sand
    return 1; // grass
  }
  // 3 layers under surface
  if (cy >= H - 3) {
    if (H <= 16) return 4; // sand
    if (H >= 37) return 3; // stone
    return 2; // dirt
  }
  return 0; // air (shouldn't reach here normally)
}
```

Wait, let me reconsider. The condition `cy < H - 3` covers "below H-3 stone". Then "the 3 layers under the surface" would be y = H-3, H-2, H-1. And surface is y = H. So:
- y = 0: stone
- y from 1 to H-4: stone (below H-3 means y < H-3, i.e., y <= H-4)
- y = H-3, H-2, H-1: dirt/sand/stone depending on H
- y = H: surface type

Wait but there's the cave check too. Let me integrate caves properly. Caves apply "for y between 3 and H-2". So y from 3 to H-2 inclusive. If cave noise > 0.67, air.

Let me rewrite:

```js
function blockAt(cx, cy, cz) {
  if (cy < 0 || cy > 79) return 0;
  const H = columnHeight(cx, cz);
  // unbreakable floor
  if (cy === 0) return 3;
  // caves
  if (cy >= 3 && cy <= H - 2) {
    if (noise3(cx * 0.09, cy * 0.09, cz * 0.09) > 0.67) return 0;
  }
  if (cy < H - 3) return 3; // deep stone
  if (cy <= H - 1) {
    // 3 layers under surface (H-3, H-2, H-1)
    if (H <= 16) return 4; // sand
    if (H >= 37) return 3; // stone
    return 2; // dirt
  }
  // surface (cy == H)
  if (H >= 46) return 7; // snow
  if (H >= 37) return 3; // stone
  if (H <= 16) return 4; // sand
  return 1; // grass
}
```

Hmm wait, "the 3 layers under the surface" — these are the three blocks just below the surface. Surface is at y=H. So the three layers under are y = H-3, H-2, H-1. That means `cy >= H-3 && cy <= H-1`. But I also have `cy < H-3` returning stone. So the boundary: at cy = H-3, it's in the "under surface" group. Good. At cy = H-4 or less, stone. 

But wait, what about when cy = H-3? `cy < H - 3` is false (since H-3 is not < H-3). So it falls through to the next check `cy <= H - 1` which is true. Good.

Actually, there's a subtle issue. What if the caves hollowed out the dirt layers? That's fine, caves take priority via the early return.

Let me double check the surface conditions. "surface = snow if H >= 46, stone if H >= 37, sand if H <= 16, otherwise grass". These are checked in order. Good.

For the under-surface layers: "the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37)". So dirt normally, sand if H<=16, stone if H>=37. Good.

### Trees

Trees placed on grass. Per-column hash < 0.02 and trunk fits inside chunk. 4 wood up, then leaves.

Let me think about tree placement. For each column (cx, cz) we compute a hash. If hash < 0.02 and there's grass at surface and the trunk can fit (height >= 4 + some margin, and within chunk bounds), place a tree.

Actually, "when a per-column hash < 0.02 and the trunk fits inside the chunk". So we need the tree to fit within the chunk horizontally too? Or vertically? Let me interpret: the tree must fit within the chunk (both horizontally and vertically). The trunk is 4 blocks, plus leaves. Let me require the surface height H >= 4 (so trunk of 4 fits, actually need room for leaves too).

Actually "trunk fits inside the chunk" probably means the vertical space. Let me require H >= 8 or so to fit the whole tree. Actually let me think: trunk 4 blocks (y = H+1 to H+4), then leaves. Leaves occupy y = H+5, H+6 (5x5 layers), then H+7 (3x3), then H+8 (1). So tree total height ~8-9 blocks above surface. We need H + 9 <= 80, so H <= 71. And horizontally the leaves extend 2 blocks in each direction, so the tree center must be at least 2 blocks from chunk edge. Hmm, but trees are per-column, and a column spans the whole chunk vertically. So a tree at column (cx,cz) occupies x from cx-2 to cx+2 within... no wait, the column is a single (x,z) point. The leaves spread horizontally. If the tree is near the chunk border, leaves could spill into neighboring chunk. The spec says "the trunk fits inside the chunk" — maybe just checking the trunk position.

Let me keep it simple: place tree if hash < 0.02, surface is grass, H >= 6 (enough room), and the column is not too close to chunk edge (so leaves stay in chunk). Actually, let me just check that the column x,z allows the leaf canopy. Let me require the column to be at least 2 blocks from chunk edges in x and z. Hmm, but that reduces tree density. 

Actually, let me re-read: "Trees: on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

I think "trunk fits inside the chunk" refers to the vertical extent — the trunk (4 blocks) plus leaves must fit within the 80-block height. Let me require H + 9 <= 80. Actually, let me require the full tree to fit: the top of tree is at H+8, need H+8 < 80, i.e., H <= 71. Also need enough below? No.

Also need the leaves to fit horizontally within the chunk. Let me require that the column's local x and z are between 2 and 13 (0-indexed), so 2-block leaf overhang stays within [0,15]. Actually if local x is 2, leaves from x-2 to x+2 = 0 to 4, fine. If local x = 13, leaves = 11 to 15, fine. So local x in [2, 13]. Similarly z.

Hmm, but that might be too restrictive. Let me just allow leaves to extend into neighboring chunks — the meshing handles that because we check neighbor blocks. Actually the issue is generating leaves in a neighboring chunk's data. If I only generate trees within the current chunk's column bounds, leaves won't spill. But if a tree is at the edge, its leaves would be in the neighbor. Since each chunk generates its own columns independently (with the same deterministic hashes based on global coords), the neighbor chunk would generate the same tree. Wait, no — the tree is tied to a specific column (x,z). Both chunks contain that column? No. A column at global (x,z) belongs to exactly one chunk: cx = floor(x/16). So if I place a tree at column (x,z), it's generated only in the chunk containing (x,z). Its leaves could extend into adjacent columns which might belong to a different chunk.

To avoid gaps, either (a) restrict trees to be far from chunk borders, or (b) generate trees across chunk boundaries (harder). Let me go with (a): restrict tree columns to local x,z in [2,13] so the 2-wide leaf canopy stays within the chunk. This guarantees no leaf gaps at chunk borders. Good.

Actually, wait. Even simpler: since leaves only grow "into air", and the meshing checks neighbors, if a neighbor chunk has the same tree generated... but it won't unless we generate it there. So restriction (a) is cleanest. Let me use local range [2, 13] for both x and z. Actually let me widen slightly — canopy is 5 wide (radius 2), so to keep all 5 columns within [0,15], need local x in [2, 13]. Yes.

Let me now write the chunk generation:

```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(16 * 16 * 80);
  const x0 = cx * 16, z0 = cz * 16;
  for (let lz = 0; lz < 16; lz++) {
    for (let lx = 0; lx < 16; lx++) {
      const wx = x0 + lx;
      const wz = z0 + lz;
      const H = columnHeight(wx, wz);
      for (let y = 0; y < 80; y++) {
        data[(y * 16 + lz) * 16 + lx] = blockAt(wx, y, wz);
      }
      // trees
      const th = blockAt(wx, H, wz);
      if (th === 1 && H >= 6 && H <= 71 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13) {
        const colHash = hash(wx, wz);
        if (colHash < 0.02) {
          // trunk
          for (let t = 1; t <= 4; t++) {
            const yy = H + t;
            if (yy < 80) data[(yy * 16 + lz) * 16 + lx] = 5; // wood
          }
          // leaves: 5x5 at H+5, H+6; 3x3 at H+7; 1 at H+8
          const leafLayers = [
            { y: H + 5, s: 2 },
            { y: H + 6, s: 2 },
            { y: H + 7, s: 1 },
            { y: H + 8, s: 0 }
          ];
          for (const L of leafLayers) {
            for (let dx = -L.s; dx <= L.s; dx++) {
              for (let dz = -L.s; dz <= L.s; dz++) {
                const ly = H + 5 + (L.y - (H+5)); // hmm messy
              }
            }
          }
        }
      }
    }
  }
  return data;
}
```

Let me redo the leaves part cleanly:

```js
// leaves
// two 5x5 layers (offset 0 and 1), then 3x3, then 1
const leafSpecs = [
  { dy: 5, r: 2 },
  { dy: 6, r: 2 },
  { dy: 7, r: 1 },
  { dy: 8, r: 0 }
];
for (const ls of leafSpecs) {
  for (let dx = -ls.r; dx <= ls.r; dx++) {
    for (let dz = -ls.r; dz <= ls.r; dz++) {
      const ly = H + ls.dy;
      const lx2 = lx + dx;
      const lz2 = lz + dz;
      if (lx2 < 0 || lx2 >= 16 || lz2 < 0 || lz2 >= 16) continue;
      if (ly >= 80) continue;
      const idx = (ly * 16 + lz2) * 16 + lx2;
      if (data[idx] === 0) data[idx] = 6; // leaves
    }
  }
}
```

This looks good. The leaves only fill air ("only into air").

### Chunk storage and meshing

```js
const chunkMap = new Map(); // key "cx,cz" -> { data: Uint8Array, mesh: Mesh }
const chunkMeshList = []; // all meshes for raycasting
```

Block read/write helpers:

```js
function getBlock(x, y, z) {
  if (y < 0 || y >= 80) return 0;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const entry = chunkMap.get(cx + "," + cz);
  if (!entry || !entry.data) return 0;
  const lx = x - cx * 16;
  const lz = z - cz * 16;
  return entry.data[(y * 16 + lz) * 16 + lx];
}

function setBlock(x, y, z, id) {
  if (y < 0 || y >= 80) return;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const entry = chunkMap.get(cx + "," + cz);
  if (!entry || !entry.data) return;
  const lx = x - cx * 16;
  const lz = z - cz * 16;
  entry.data[(y * 16 + lz) * 16 + lx] = id;
}
```

Meshing:

```js
const BLOCK_COLORS = {
  1: 0x4caf50, 2: 0x795548, 3: 0x9e9e9e, 4: 0xe7d9a8,
  5: 0x8d6e63, 6: 0x2e7d32, 7: 0xffffff
};

const FACE_DIRS = [
  [1, 0, 0], [-1, 0, 0],
  [0, 1, 0], [0, -1, 0],
  [0, 0, 1], [0, 0, -1]
];

// vertex offsets for each face of a cube
const FACE_VERTS = [
  // +x
  [[1,0,0],[1,1,0],[1,1,1],[1,0,1]],
  // -x
  [[0,0,1],[0,1,1],[0,1,0],[0,0,0]],
  // +y
  [[0,1,0],[0,1,1],[1,1,1],[1,1,0]],
  // -y
  [[0,0,1],[1,0,1],[1,0,0],[0,0,0]],
  // +z
  [[1,0,1],[1,1,1],[0,1,1],[0,0,1]],
  // -z
  [[0,0,0],[0,1,0],[1,1,0],[1,0,0]]
];
```

Hmm, I need to get the winding order right for correct culling (backface culling). In Three.js, MeshLambertMaterial with `side: FrontSide` (default) shows faces whose vertices counterclockwise when viewed from front. Let me make sure the normals point outward and vertices are CCW when viewed from outside.

Let me define each face with outward normal and CCW-ordered vertices (as seen from outside).

Standard cube faces (from three.js BoxGeometry):

For +X face (normal +x): vertices should be CCW when viewed from +x looking toward -x.
Points: (1,0,0), (1,0,1), (1,1,1), (1,1,0)? Let me think.

Actually, let me just carefully construct them. For a unit cube from (0,0,0) to (1,1,1):

Face +X (x=1), looking from outside (from +x toward -x, i.e., looking in -x direction):
The four corners are (1,0,0), (1,0,1), (1,1,1), (1,1,0). For CCW when viewed from +x side... When looking in the -x direction (from positive x), the y axis points up and the z axis... Let me set up: viewer at +x looking toward origin. Up is +y. Then right is... using right-hand rule, if forward is -x and up is +y, then right = forward × up? Let me just compute cross products.

Actually, let me use a known-good set. From three.js BoxGeometry source, the vertex positions and indices per face:

Actually, simpler: I'll define normals and vertices such that the cross product of (v1-v0) × (v2-v0) equals the normal. That guarantees correct winding for FrontSide rendering.

Let me define for each face:
- normal N
- 4 vertices v0,v1,v2,v3
- ensure (v1-v0)×(v2-v0) is parallel to N (same direction)

Let me do +X:
Normal = (1,0,0).
Let me pick v0=(1,0,0), v1=(1,0,1), v2=(1,1,1).
(v1-v0) = (0,0,1). (v2-v0) = (0,1,1). Cross = (0,0,1)×(0,1,1) = 
i: (0*1 - 1*1) = -1
j: (1*0 - 0*1) = 0... 

wait let me compute cross product (a×b) where a=(0,0,1), b=(0,1,1):
a×b = (a_y*b_z - a_z*b_y, a_z*b_x - a_x*b_z, a_x*b_y - a_y*b_x)
= (0*1 - 1*1, 1*0 - 0*1, 0*1 - 0*0)
= (-1, 0, 0).
That points in -x, opposite of desired. So swap v1 and v2: v0=(1,0,0), v1=(1,1,1), v2=(1,0,1).
(v1-v0)=(0,1,1), (v2-v0)=(0,0,1). Cross = (1*1-1*0, 1*0-0*1, 0*0-1*0) = (1,0,0). 

So +X face: v0=(1,0,0), v1=(1,1,1), v2=(1,0,1), and v3 = v0 + (v2-v0) + (v1-v0)... actually for a quad we need 4 points. v3 = v1 + (v2 - v0) = (1,1,1)+(0,0,1)-(0,0,0)... hmm let me just define all 4 directly.

Let me define quads as pairs of triangles: (v0,v1,v2) and (v2,v1,v3). Need v3 to complete the quad.

For +X: v0=(1,0,0), v1=(1,1,1), v2=(1,0,1). The fourth point v3 should make it a planar quad. v3 = v0 + (v1 - v2) = (1,0,0)+(0,-1,0) = (1,-1,0)? That's wrong.

Let me reconsider. A quad has 4 corners. Two triangles share a diagonal. Triangle 1: (v0, v1, v2). Triangle 2: (v2, v1, v3) — wait this shares edge v1-v2. Hmm.

Let me just lay out 4 corners in order around the quad: p0, p1, p2, p3 (CCW). Then triangles (p0,p1,p2) and (p0,p2,p3).

For +X face, the 4 corners at x=1: (1,0,0), (1,1,0), (1,1,1), (1,0,1). Order them CCW when viewed from +x (looking in -x direction). 

Looking from +x toward -x with +y up: The horizontal axis... when looking in -x direction with up=+y, the right direction is +z? Let's see: right = up × look_direction? In a right-handed system, if we look along -x (forward = -x), and up = +y, then right = forward × up is not right. Standard: camera right = normalize(cross(up, forward))? Let me recall: for a camera, right = cross(forward, up)? Actually three.js: right = cross(z, y) where z is forward... this is getting complicated.

Let me just directly verify winding with the cross product method and pick consistent ordering.

For +X face, corners (in some order): A=(1,0,0), B=(1,1,0), C=(1,1,1), D=(1,0,1).
Try order A,B,C,D. Triangles (A,B,C) and (A,C,D).
(A,B,C): (B-A)=(0,1,0), (C-A)=(0,1,1). Cross = (1*1-0*1, 0*0-0*1, 0*1-1*0) = (1, 0, 0). Points +X. Good, so triangle ABC has outward normal.
So order A,B,C for first triangle gives +X normal. Then second triangle (A,C,D): (C-A)=(0,1,1), (D-A)=(0,0,1). Cross = (1*1-1*0, 0*0-0*1, 0*0-1*0) = (1,0,0). Good.
So +X: p0=A=(1,0,0), p1=B=(1,1,0), p2=C=(1,1,1), p3=D=(1,0,1). Triangles (0,1,2),(0,2,3).

Hmm wait, but is A,B,C,D actually going around the quad in order (not crossing)? A=(1,0,0) bottom-front, B=(1,1,0) top-front, C=(1,1,1) top-back, D=(1,0,1) bottom-back. Yes that's CCW-ish around the face. Good.

This is getting tedious. Let me just define all 6 faces with verified winding. Actually, let me use a cleaner approach: for each face, I'll specify the normal and 4 vertices, and I'll trust the following pattern. Let me define them so that consecutive vertices go around, and I'll verify each normal via cross product mentally.

Let me set up a coordinate reference: x east (+x is +x), y up, z south (+z is +z).

Face +X (normal +x, facing east):
The face is the plane x=1. Vertices: (1,0,0),(1,1,0),(1,1,1),(1,0,1).
As computed, order [(1,0,0),(1,1,0),(1,1,1),(1,0,1)] gives outward normal. ✓

Face -X (normal -x, facing west):
Plane x=0. Vertices should be ordered so normal is -x. By symmetry, reverse: [(0,0,0),(0,0,1),(0,1,1),(0,1,0)].
Check: (B-A)=(0,0,1), (C-A)=(0,1,1). Cross = (0*1-1*1, 1*0-0*1, 0*1-0*0) = (-1,0,0). ✓ (-x).
So -X: [(0,0,0),(0,0,1),(0,1,1),(0,1,0)]. ✓

Face +Y (normal +y, facing up):
Plane y=1. Vertices: (0,1,0),(1,1,0),(1,1,1),(0,1,1)? 
Check (B-A)=(1,0,0),(C-A)=(1,0,1). Cross = (0*1-0*1, 0*1-1*1, 1*0-0*1) = (0,-1,0). That's -y, wrong.
Reverse: [(0,1,0),(0,1,1),(1,1,1),(1,1,0)].
(B-A)=(0,0,1),(C-A)=(0,0,1)... wait (C-A) where C=(1,1,1), A=(0,1,0): (1,0,1). (B-A)=(0,0,1). Cross = (0*1-1*0, 1*1-0*1, 0*0-0*0)... let me redo. a=(0,0,1), b=(1,0,1). a×b = (a_y*b_z - a_z*b_y, a_z*b_x - a_x*b_z, a_x*b_y - a_y*b_x) = (0*1 - 1*0, 1*1 - 0*1, 0*0 - 0*1) = (0, 1, 0). ✓ +y.
So +Y: [(0,1,0),(0,1,1),(1,1,1),(1,1,0)]. ✓

Face -Y (normal -y, facing down):
Plane y=0. Vertices: [(0,0,0),(1,0,0),(1,0,1),(0,0,1)].
(B-A)=(1,0,0),(C-A)=(1,0,1). a=(1,0,0), b=(1,0,1). a×b = (0*1-0*0, 0*1-1*1, 1*0-0*1) = (0,-1,0). ✓ -y.
So -Y: [(0,0,0),(1,0,0),(1,0,1),(0,0,1)]. ✓

Face +Z (normal +z, facing south):
Plane z=1. Vertices: [(1,0,0),(1,1,0),(0,1,1),(0,0,1)]? Let me find correct order.
Try [(1,0,0),(0,0,0),(0,1,0)... no wait those are at z=0. Let me use z=1 plane points: (0,0,1),(1,0,1),(1,1,1),(0,1,1).
Check order [(0,0,1),(1,0,1),(1,1,1),(0,1,1)]: (B-A)=(1,0,0),(C-A)=(1,1,0). a×b = (0*0-0*1, 0*1-1*0, 1*1-0*1) = (0,0,1). ✓ +z.
So +Z: [(0,0,1),(1,0,1),(1,1,1),(0,1,1)]. ✓

Face -Z (normal -z, facing north):
Plane z=0. Points (0,0,0),(1,0,0),(1,1,0),(0,1,0).
Check order [(0,0,0),(0,1,0),(1,1,0),(1,0,0)]: (B-A)=(0,1,0),(C-A)=(1,1,0). a×b = (1*0-0*1, 0*1-0*0, 0*1-1*1) = (0,0,-1). ✓ -z.
So -Z: [(0,0,0),(0,1,0),(1,1,0),(1,0,0)]. ✓

Great, now I have all 6 faces with correct winding. Let me store them:

```js
const FACES = [
  // index 0: +X
  { n:[1,0,0], v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  // index 1: -X
  { n:[0,0,0]... }
];
```

Wait let me relabel with my findings:
- 0 (+X): n=[1,0,0], v=[[1,0,0],[1,1,0],[1,1,1],[1,0,1]]
- 1 (-X): n=[0,0,0]... n=[0,0,0]? No, n=[-1,0,0], v=[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]
- 2 (+Y): n=[0,1,0], v=[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]
- 3 (-Y): n=[0,-1,0], v=[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]
- 4 (+Z): n=[0,0,1], v=[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]
- 5 (-Z): n=[0,0,-1], v=[[0,0,0],[0,1,0],[1,1,0],[1,0,0]]

Now the meshing loop. For each block (x,y,z) that is non-air, for each of 6 faces, check neighbor. If neighbor is air (or out of range? out of range returns air, so treat as air → show face), add the face.

Actually, for neighbor check: if neighbor is air OR neighbor chunk doesn't exist (missing), we show the face. Because if the neighbor chunk isn't built yet, we'd see a hole. But per spec, we only build meshes for chunks whose 4 neighbors have data. So by the time we mesh a chunk, neighbors exist. But to be safe, treat missing neighbor as air (show face). That's the standard approach.

Wait, but there's subtlety: if we show faces toward missing chunks, and later the chunk gets built, we'd have internal faces. But since we rebuild affected chunks when neighbors change, and we only mesh when neighbors exist, it's fine. Actually the spec says "build meshes for chunks within 4 chunks whose 4 neighbors already have data". So we ensure neighbors have data before meshing. Good. But still, treating missing as air is correct behavior.

Let me write the meshing:

```js
function buildChunkMesh(cx, cz) {
  const key = cx + "," + cz;
  const entry = chunkMap.get(key);
  if (!entry || !entry.data) return;
  
  const positions = [];
  const normals = [];
  const colors = [];
  const indices = [];
  let vi = 0;
  
  const x0 = cx * 16, z0 = cz * 16;
  
  for (let lz = 0; lz < 16; lz++) {
    for (let lx = 0; lx < 16; lx++) {
      for (let y = 0; y < 80; y++) {
        const id = entry.data[(y * 16 + lz) * 16 + lx];
        if (id === 0) continue;
        const wx = x0 + lx, wz = z0 + lz;
        const baseColor = BLOCK_COLORS[id];
        const cr = ((baseColor >> 16) & 255) / 255;
        const cg = ((baseColor >> 8) & 255) / 255;
        const cb = (baseColor & 255) / 255;
        
        for (let f = 0; f < 6; f++) {
          const face = FACES[f];
          const nx = wx + face.n[0];
          const ny = y + face.n[1];
          const nz = wz + face.n[2];
          const nid = getBlock(nx, ny, nz);
          if (nid !== 0) continue; // neighbor present, cull
          
          // lighting factor by face direction
          let light;
          if (f === 2) light = 1.0;       // +Y top
          else if (f === 3) light = 0.55; // -Y bottom
          else light = 0.8;              // sides
          
          for (let i = 0; i < 4; i++) {
            const vp = face.v[i];
            positions.push(wx + vp[0], y + vp[1], wz + vp[2]);
            normals.push(face.n[0], face.n[1], face.n[2]);
            colors.push(cr * light, cg * light, cb * light);
          }
          indices.push(vi, vi+1, vi+2, vi, vi+2, vi+3);
          vi += 4;
        }
      }
    }
  }
  
  // build geometry
  let geom = entry.geom;
  if (!geom) {
    geom = new THREE.BufferGeometry();
    entry.geom = geom;
  }
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geom.setIndex(indices);
  geom.computeBoundingSphere();
}
```

Wait, the spec says "Keep all chunk meshes in a global array for raycasting". And I need a separate wireframe for the outline. Let me keep the main mesh material as shared MeshLambertMaterial.

Actually, one concern: the spec says "ONE shared MeshLambertMaterial". So one material used for all chunk meshes. Good.

Now the wireframe outline for targeted block. I'll create a separate LineSegments or EdgesGeometry wireframe box, positioned at the target block, toggled visible.

### Player physics

Camera with perspective. Position stored as a vector. Yaw and pitch. Movement.

Collision: player box half-width 0.3, height 1.8, eye 1.62. So feet at camera.y - 1.62. Player occupies x ± 0.3, z ± 0.3, y from feet to feet+1.8.

Collision check against blocks: for a given player AABB, check all blocks overlapping. Move per axis.

Let me implement collision:

```js
function collide(px, py, pz) {
  // px,py,pz is player feet position (bottom center)
  const hw = 0.3, h = 1.8;
  const minX = Math.floor(px - hw), maxX = Math.floor(px + hw);
  const minY = Math.floor(py), maxY = Math.floor(py + h - 0.001); // avoid top float
  const minZ = Math.floor(pz - hw), maxZ = Math.floor(pz + hw);
  for (let x = minX; x <= maxX; x++)
    for (let y = minY; y <= maxY; y++)
      for (let z = minZ; z <= maxZ; z++)
        if (getBlock(x,y,z) !== 0) return true;
  return false;
}
```

Movement per axis:
```js
// horizontal
let nx = px + dx * dt * speed;
if (!collide(nx, py, pz)) px = nx;
else dx = 0; // stop velocity in that axis
// similar for z
// vertical
ny = py + vy * dt;
if (!collide(ny... )) py = ny; else { if (vy < 0) onGround = true; vy = 0; }
```

Hmm, need to handle landing. When moving down and hits, set vy=0 and onGround=true. When moving up and hits, vy=0.

Let me write the physics update:

```js
function updatePlayer(dt) {
  // determine movement direction
  const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
  let moveX = 0, moveZ = 0;
  if (keys['w']) { moveX += forward.x; moveZ += forward.z; }
  if (keys['s']) { moveX -= forward.x; moveZ -= forward.z; }
  if (keys['d']) { moveX += right.x; moveZ += right.z; }
  if (keys['a']) { moveX -= right.x; moveZ -= right.z; }
  // normalize
  const len = Math.hypot(moveX, moveZ);
  if (len > 0) { moveX /= len; moveZ /= len; }
  
  const px = player.position.x;
  const pz = player.position.z;
  const feet = player.position.y - EYE;
  
  // horizontal move
  let nx = px + moveX * SPEED * dt;
  if (!collide(nx, feet, pz)) player.position.x = nx;
  let nz = pz + moveZ * SPEED * dt;
  if (!collide(player.position.x, feet, nz)) player.position.z = nz;
  
  // gravity
  vy -= GRAVITY * dt;
  if (keys[' '] && onGround) { vy = JUMP_SPEED; onGround = false; }
  vy = Math.max(vy, -50); // terminal
  
  let ny = feet + vy * dt;
  if (!collide(player.position.x, ny, player.position.z)) {
    player.position.y = ny + EYE;
    onGround = false;
  } else {
    if (vy < 0) onGround = true;
    vy = 0;
    player.position.y = ny + EYE; // snap
  }
  
  if (player.position.y < -20) { player.position.set(8, terrainHeightAt(8,8)+2, 8); vy = 0; }
}
```

Wait, collision uses feet position. Let me store player.position.y as the eye height (camera height). Then feet = y - EYE. The AABB for collision is [feet, feet+1.8]. When I check collide(nx, feet, pz), I pass feet as the y of the bottom. Good.

terrainHeightAt: compute column height at (x,z), spawn above it.

Let me refine the collision snapping. When vy < 0 and we hit ground, we want to snap to land on top of the block. The collide check with ny would fail (overlap). To snap precisely, I can decrement ny until it doesn't collide, or just set feet to the top of the block + epsilon. Simpler: when collision detected with vy<0, step back ny upward in small increments until no collision. But that's costly. Alternative: snap feet to Math.floor of the block top.

Actually, a clean approach: after computing ny, if collide, walk ny up in tiny steps (like 0.1) until not colliding, then set. Let me do a small loop:

```js
let step = 0.1;
while (step > 0.001 && collide(px, ny, pz)) ny += step; // no, this overshoots
```

Hmm, that walks up too far. Better: since we're falling and hit, the ground is just below. Let me instead snap: feet should be at the top surface of the block we landed on. 

Alternative clean approach used in many voxel games: move in small steps. But let me just do the incremental snap for landing:

When vy < 0 and collide at ny:
```js
// snap onto surface
let snapNy = ny;
while (snapNy < feet && collide(px, snapNy, pz)) snapNy += 0.05;
// snapNy is now just above ground (last failing)... 
```
This is getting messy. Let me do the standard: try progressively smaller downward adjustments.

Actually simplest robust method: after determining vy and proposed ny, if collide:
- if vy >= 0 (going up): set ny so that feet align to bottom of blocking block. Actually just set vy=0 and leave position (it'll push out). Hmm.
- if vy < 0 (falling): find the ground. The block we hit has its top at floor(ny) + 1 roughly. Set feet = floor(ny) + 1 + epsilon... but ny includes the feet position which is already at ground level.

Let me think again. feet is the y-coordinate of the bottom of the player. When falling, feet decreases. When feet reaches a level where the block below (at floor(feet)) exists, we collide. The top of that blocking block is at floor(feet)+1 (if feet is not integer). Actually if feet = 16.2, floor = 16, the block at y=16 occupies [16,17], top at 17. So landing means feet = 17. So set feet = floor(ny) + 1 when falling and colliding? But only if there's a block. Let me do:

```js
if (vy < 0) {
  // landing: snap feet to top of block below
  const blockBelowY = Math.floor(ny);
  // top of that block is blockBelowY + 1
  player.position.y = (blockBelowY + 1) + EYE;
  onGround = true;
  vy = 0;
} else {
  // hit head
  vy = 0;
  // leave position or snap down slightly
}
```

Wait but this assumes the block is directly below. When falling, the collision happens because a block occupies the space the feet would enter. The feet at ny=16.2 collides because block at y=16 fills [16,17] and feet region [16.2, 18.0] overlaps. Landing on top means feet should be at 17 (top of block 16). So feet = floor(ny) + 1 = 17. Yes! That works when the block's top is at an integer. Since blocks are unit cubes at integer positions, block at y=k occupies [k, k+1], top at k+1. floor(ny)=16, +1 = 17. Correct.

But what if ny is exactly integer, like 17.0? floor(17)=17, +1=18. But if feet=17.0 exactly and there's a block at y=17 ([17,18]), then feet=17 is exactly at the top, not overlapping (boundary). Should be fine, feet=17 lands exactly on top of block 16's... no. Hmm. If feet = 17.0, the player occupies [17, 18.8]. Block at 17 occupies [17,18]. They share the boundary y=17. Is that a collision? My collide uses Math.floor(px±0.3) etc. floor(17)=17, so it checks block at y=17 which exists → collision. But physically feet=17 is standing exactly on top. Setting feet=18 would put player floating. So the boundary case is tricky.

Let me add a small epsilon: treat collision only if strictly overlapping. In collide, use maxY = floor(py + h - 1e-6) so that exact-top doesn't count. And for landing, feet = floor(ny) + 1 when the block at floor(ny) exists... 

Actually, let me simplify by using a small epsilon in the landing snap: feet = floor(ny + 1e-4) + 1? No.

Let me reconsider. The cleanest: when falling and about to collide, snap feet to the nearest surface. Let me just do iterative stepping down from ny until no collision, but that's for the "no collision" branch. Ugh.

New plan: Use continuous-ish approach with sub-stepping is overkill. Let me just do:

```js
// vertical
let newY = feet + vy*dt;
if (collide(px, newY, pz)) {
  if (vy < 0) {
    // land: feet to top of the block we're pressing into
    // find the highest block top <= newY within the player footprint
    // simplest: feet = ceil(newY - epsilon)... 
  }
}
```

Honestly, the floor(ny)+1 approach works for the common case. Let me handle the boundary by using a tiny epsilon in collide:

In collide, compute maxY = Math.floor(py + H - 1e-3). This means if the player's top is exactly at an integer boundary, it won't count the block above. For landing, when vy<0 and collide, set feet = floor(newY) + 1. But if newY is exactly integer (rare due to float), floor(newY)=integer, +1 gives one block up. Edge case acceptable.

Actually, let me reconsider whether feet = floor(ny)+1 is even right when ny is like 16.99. floor(16.99)=16, +1=17. feet=17, occupying [17,18.8]. Block at 16 is [16,17], top at 17. Player bottom at 17 = block top. Standing on it. 

And if ny = 17.0 exactly (shouldn't happen often), floor=17, +1=18. Player [18,19.8], block 17 [17,18], top at 18. Player bottom 18 = top of block 17. Still standing on it! Because block 17 is the one being collided with. Wait, if feet=17.0 exactly and collide returned true, that means block at y=17 exists (occupies [17,18]) and player [17,18.8] overlaps it (shares boundary at 17). With epsilon in collide (maxY excludes exact top), would collide return true? maxY = floor(17.0 + 1.8 - 0.001) = floor(18.799) = 18. Checks blocks y=17,18. Block 17 exists → collide true. Then feet = floor(17.0)+1 = 18. Player [18,19.8]. Block 17 [17,18], top 18. Standing on top of block 17. But wait, we wanted to stand on top of whatever's below feet=17. If block 17 exists, feet can't be at 17 (that's inside block 17's lower part). Actually feet=17 is the bottom edge of block 17. Standing on block 17 means feet=18 (on top of block 17). But there might be block 16 below too. The point is feet=18 stands on top of block 17. That's consistent IF block 17 exists. If block 17 doesn't exist (feet fell through), collide wouldn't trigger at feet=17... 

OK this is an extreme edge case. Let me just go with feet = floor(newY) + 1 when falling and colliding, plus epsilon in collide. It'll work for practical gameplay.

Actually, let me reconsider and use a cleaner landing that doesn't rely on exact integer assumptions. I'll snap by walking up:

```js
if (collide(px, newY, pz)) {
  if (vy < 0) {
    // snap onto surface
    let s = newY;
    for (let i = 0; i < 20 && collide(px, s, pz); i++) s += 0.1;
    player.position.y = s + EYE;
    onGround = true;
    vy = 0;
  } else {
    vy = 0;
  }
} else {
  player.position.y = newY + EYE;
  onGround = false;
}
```

Wait, walking up while colliding: start at newY (colliding), add 0.1 each step until not colliding. This finds the lowest position above newY where there's no collision, i.e., resting on top of the obstacle. This is robust and simple. 20 steps of 0.1 = 2 units max, plenty. Good. Let me use this.

Similarly for horizontal, if collide, just don't move (don't snap). That's fine for horizontal.

Actually for horizontal I could also snap but stopping is fine.

Let me also handle: when falling and the snap loop, if it never resolves (tunneling), just cap. Fine.

### Raycasting

Each frame, raycast from camera center (ray direction = camera forward) against all chunk meshes, max distance 6. Get hit point and face normal.

```js
const raycaster = new THREE.Raycaster();
raycaster.far = 6;

function updateTarget() {
  raycaster.set(camera.position, camera.getWorldDirection(new THREE.Vector3()));
  const hits = raycaster.intersectObjects(chunkMeshList, false);
  if (hits.length > 0) {
    const hit = hits[0];
    hitPoint.copy(hit.point);
    hitNormal.copy(hit.face.normal);
    hasTarget = true;
  } else {
    hasTarget = false;
  }
}
```

Then target block = floor(hitPoint - hitNormal*0.5), place cell = floor(hitPoint + hitNormal*0.5).

Outline: position a wireframe box at target block center.

```js
outline.position.set(targetX + 0.5, targetY + 0.5, targetZ + 0.5);
outline.visible = hasTarget;
```

Use THREE.EdgesGeometry on a BoxGeometry(1,1,1) for crisp lines, or a WireframeGeometry. EdgesGeometry is cleaner.

### Break/place actions

On left click (pointer locked): set target block to air (if not y=0). Rebuild chunk and neighbor if on border.

On right click (pointer locked): place selected block in place cell if air and doesn't overlap player.

```js
function breakBlock() {
  if (!hasTarget) return;
  const x = Math.floor(hitPoint.x - hitNormal.x * 0.5);
  const y = Math.floor(hitPoint.y - hitNormal.y * 0.5);
  const z = Math.floor(hitPoint.z - hitNormal.z * 0.5);
  if (y === 0) return; // unbreakable floor
  setBlock(x, y, z, 0);
  rebuildChunkAt(x, y, z);
}

function placeBlock() {
  if (!hasTarget) return;
  const x = Math.floor(hitPoint.x + hitNormal.x * 0.5);
  const y = Math.floor(hitPoint.y + hitNormal.y * 0.5);
  const z = Math.floor(hitPoint.z + hitNormal.z * 0.5);
  if (getBlock(x,y,z) !== 0) return;
  // check overlap with player
  const feet = player.position.y - EYE;
  const hw = 0.32, h = 1.8;
  if (x+1 > player.position.x - hw && x < player.position.x + hw &&
      y+1 > feet && y < feet + h &&
      z+1 > player.position.z - hw && z < player.position.z + hw) return;
  setBlock(x, y, z, selectedBlock);
  rebuildChunkAt(x, y, z);
}
```

rebuildChunkAt:
```js
function rebuildChunkAt(x, y, z) {
  const cx = Math.floor(x/16), cz = Math.floor(z/16);
  rebuildChunk(cx, cz);
  // neighbor if on border
  const lx = x - cx*16, lz = z - cz*16;
  if (lx === 0) rebuildChunk(cx-1, cz);
  if (lx === 15) rebuildChunk(cx+1, cz);
  if (lz === 0) rebuildChunk(cx, cz-1);
  if (lz === 15) rebuildChunk(cx, cz+1);
}
```

But rebuildChunk requires the chunk to have data. If neighbor doesn't have data yet, skip (or generate it). Let me guard: only rebuild if entry.data exists.

### World management per frame

```js
function updateWorld() {
  const pcx = Math.floor(player.position.x / 16);
  const pcz = Math.floor(player.position.z / 16);
  
  // generate data for chunks within 5 (max 4/frame)
  let genCount = 0;
  for (let dz = -5; dz <= 5 && genCount < 4; dz++) {
    for (let dx = -5; dx <= 5; dx++) {
      if (Math.abs(dx) > 5 || Math.abs(dz) > 5) continue;
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx + "," + cz;
      if (!chunkMap.has(key)) {
        chunkMap.set(key, { data: generateChunkData(cx, cz), mesh: null, geom: null });
        genCount++;
      }
    }
  }
  
  // build meshes for chunks within 4 whose 4 neighbors have data (max 2/frame)
  let meshCount = 0;
  for (let dz = -4; dz <= 4 && meshCount < 2; dz++) {
    for (let dx = -4; dx <= 4; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      if (Math.abs(dx) > 4 || Math.abs(dz) > 4) continue;
      const key = cx + "," + cz;
      const entry = chunkMap.get(key);
      if (!entry || entry.mesh) continue;
      // check 4 neighbors have data
      const n = [
        chunkMap.get((cx+1)+","+cz),
        chunkMap.get((cx-1)+","+cz),
        chunkMap.get(cx+","+（cz+1)),
        chunkMap.get(cx+","+（cz-1))
      ];
      if (n.every(e => e && e.data)) {
        buildChunkMesh(cx, cz);
        meshCount++;
      }
    }
  }
  
  // remove far chunks (> 7)
  for (const [key, entry] of chunkMap) {
    const parts = key.split(",");
    const cx = +parts[0], cz = +parts[1];
    if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
      if (entry.mesh) {
        scene.remove(entry.mesh);
        if (entry.geom) entry.geom.dispose();
        const idx = chunkMeshList.indexOf(entry.mesh);
        if (idx >= 0) chunkMeshList.splice(idx, 1);
      }
      chunkMap.delete(key);
    }
  }
}
```

Wait, the neighbor check for meshing: "build meshes for chunks within 4 chunks whose 4 neighbors already have data". The 4 neighbors are the orthogonal neighbors (N,S,E,W). Diagonal not required. Good, matches my n array.

But there's a subtlety: when we build a chunk mesh, we call buildChunkMesh which reads getBlock for neighbors. If a neighbor's data exists but mesh doesn't, that's fine — data is what matters for block values. Good.

However, there's a bootstrapping issue: at start, only a few chunks have data. We build meshes only when all 4 neighbors have data. So the central chunk builds once its neighbors populate. Fine.

Also, when we generate a chunk's data but it's on the border and its neighbor lacks data, we hold off meshing until neighbor has data. Good.

One more: after placing/breaking a block, we rebuild the chunk and neighbors. If a neighbor lacks data, we can't rebuild meaningfully (no geometry). But the edit is in data; when neighbor eventually gets data+mesh, it'll include the change. However, to be safe, if neighbor lacks data, we could generate it. But let me keep simple: rebuild only if data exists. Actually, for correctness when editing near an ungenerated border, the change won't show until that chunk is meshed. Since meshing requires neighbors to have data, and we're editing near border, the neighbor will get data soon and mesh including the edit. Acceptable. But to be safe, let me also generate neighbor data on edit if missing. Hmm, let me just rebuild existing ones; the neighbor will catch up. Actually, let me generate neighbor data if missing to make edits visible immediately:

Let me not overcomplicate. I'll rebuild chunks that have data. For the immediate neighbor without data, it'll be generated next frame and meshed. There might be a 1-frame delay. Fine.

Actually, to be safe and correct, in rebuildChunkAt, if a neighbor lacks data, generate it (so it can be meshed next frame with the edit). Let me add that.

Hmm, but generateChunkData reads surrounding columns? No, my generateChunkData only reads its own columns (columnHeight and blockAt only depend on the column's x,z for height, and blockAt for the whole column). Wait, blockAt for a column depends only on that column's height (which depends on x,z). Caves depend on x,y,z of that column. Trees depend on column. So each column is independent! Great, no neighbor dependency in generation. So generating a chunk is self-contained. Good.

So on edit near border, I can generate neighbor data immediately and it'll be correct. Let me make rebuildChunkAt generate missing neighbor data too. Actually simpler: in rebuildChunkAt, for each of the 4 chunks (self + border neighbors), if no data, generate it; then rebuild mesh if all its neighbors have data. Let me just call rebuild for those with data and let the normal world loop handle the rest. But the edited block needs to appear. Since we rebuild the owning chunk's mesh (which has data), it'll show. The neighbor will show next frame. Acceptable but let me generate neighbor data to be prompt.

Let me write:
```js
function rebuildChunk(cx, cz) {
  const entry = chunkMap.get(cx+","+cz);
  if (!entry || !entry.data) {
    // generate if missing (needed for edits at borders)
    if (entry) { entry.data = generateChunkData(cx,cz); }
    else return; // don't generate blindly during normal loop
    return;
  }
  buildChunkMesh(cx, cz);
}
```

Hmm, this is getting complicated. Let me simplify: rebuildChunkAt regenerates the owning chunk's data from scratch? No, that would overwrite player edits elsewhere. Bad.

Better approach: rebuild only rebuilds geometry from existing data. For edits, we modify data then rebuild. For the owning chunk (has data), rebuild works. For neighbors on border that lack data, we should generate their data so they can later mesh with the edit. Let me just generate missing neighbor data in rebuildChunkAt:

```js
function rebuildChunkAt(x, y, z) {
  const cx = Math.floor(x/16), cz = Math.floor(z/16);
  rebuildMesh(cx, cz);
  const lx = x - cx*16, lz = z - cz*16;
  if (lx === 0) ensureChunkData(cx-1, cz);
  if (lx === 15) ensureChunkData(cx+1, cz);
  if (lz === 0) ensureChunkData(cx, cz-1);
  if (lz === 15) ensureChunkData(cx, cz+1);
}
function ensureChunkData(cx, cz) {
  const key = cx+","+cz;
  if (!chunkMap.has(key)) {
    chunkMap.set(key, { data: generateChunkData(cx,cz), mesh: null, geom: null });
  }
}
function rebuildMesh(cx, cz) {
  const entry = chunkMap.get(cx+","+cz);
  if (entry && entry.data) buildChunkMesh(cx, cz);
}
```

This way, edits at borders generate neighbor data, and next frame's world loop will mesh them (once their other neighbors have data). Good enough.

### Clouds

25 flat white transparent boxes at height ~90, drifting, wrapping around player.

```js
const clouds = [];
for (let i = 0; i < 25; i++) {
  const g = new THREE.BoxGeometry(8 + Math.random()*... );
```
No Math.random allowed! Use deterministic. Let me use a counter-based offset.

```js
for (let i = 0; i < 25; i++) {
  const w = 6 + (i % 4) * 3;
  const d = 6 + (i % 3) * 2;
  const g = new THREE.BoxGeometry(w, 1.5, d);
  const m = new THREE.Mesh(g, cloudMaterial);
  const seedX = ((i * 131.7) % 80);
  const seedZ = ((i * 257.3) % 80);
  m.position.set(seedX, 90, seedZ);
  scene.add(m);
  clouds.push(m);
}
```

Update: position relative to player, wrap within a range. Drift in x.

```js
clouds.forEach((c, i) => {
  c.position.x += drift * dt;
  // keep within player±60, wrap
  const baseX = ((c.baseX + c.driftTotal) % 120 + 120) % 120 - 60;
  ...
});
```

Let me store base offsets relative to spawn and just recompute relative to player each frame with wrapping:

```js
clouds.forEach((c) => {
  const rx = c.rx + c.speed * elapsed; // drift
  const rz = c.rz;
  // wrap around player
  let x = player.position.x + rx;
  x = ((x - (player.position.x - 60)) % 120 + 120) % 120 + (player.position.x - 60);
  ...
});
```

This is fiddly. Let me do simpler: store cloud's local offset (rx, rz) and speed. Each frame:
```
cloud.x = player.x + (rx + speed*t) wrapped to [-60,60]
cloud.z = player.z + rz wrapped to [-60,60]
```
Wrap function:
```js
function wrap(v, center, half) {
  let d = v - center;
  d = ((d + half) % (2*half) + 2*half) % (2*half) - half;
  return center + d;
}
```
Then cloud.x = wrap(player.x + rx + speed*t, player.x, 60) = player.x + wrap(rx+speed*t, 0, 60). Let me just compute local then wrap local:
```
let lx = rx + speed*t;
lx = ((lx + 60) % 120 + 120) % 120 - 60;
cloud.position.x = player.x + lx;
cloud.position.z = player.z + rz; // rz static, wrap once
```
Good enough. rz also wrap:
```
let lz = rz;
lz = ((lz + 60) % 120 + 120) % 120 - 60;
cloud.position.z = player.z + lz;
```

Water plane: one large semi-transparent blue plane at height 14.3, re-centered on player each frame.

```js
water.position.x = player.position.x;
water.position.z = player.position.z;
```
Size like 200x200.

### Hotbar UI

Create 7 slots in DOM. Update selection highlight.

```js
const HOTBAR_COLORS = [0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
const hotbarEl = document.getElementById('hotbar');
for (let i = 0; i < 7; i++) {
  const slot = document.createElement('div');
  slot.className = 'slot';
  slot.style.background = '#'+HOTBAR_COLORS[i].toString(16).padStart(6,'0');
  slot.innerHTML = `<span class="num">${i+1}</span>`;
  hotbarEl.appendChild(slot);
}
function updateHotbar() {
  [...hotbarEl.children].forEach((s,i) => s.classList.toggle('selected', i===selectedBlock-1));
}
```

Selected block default 1 (grass). Keys 1-7 set selectedBlock. Wheel changes with wrap.

### Input

Pointer lock on overlay click. Mouse move when locked → adjust yaw/pitch. Keys tracked in a set. Suppress context menu.

```js
document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('mousedown', e => {
  if (!pointerLocked) return;
  if (e.button === 0) breakBlock();
  else if (e.button === 2) placeBlock();
});
document.addEventListener('mousemove', e => {
  if (!pointerLocked) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  pitch = Math.max(-Math.PI/2 + 0.01, Math.min(Math.PI/2 - 0.01, pitch));
});
document.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key >= '1' && e.key <= '7') { selectedBlock = +e.key; updateHotbar(); }
});
document.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });
document.addEventListener('wheel', e => {
  if (!pointerLocked) return;
  selectedBlock += e.deltaY > 0 ? 1 : -1;
  if (selectedBlock < 1) selectedBlock = 7;
  if (selectedBlock > 7) selectedBlock = 1;
  updateHotbar();
});
```

Overlay click to play:
```js
overlay.addEventListener('click', () => {
  canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  pointerLocked = (document.pointerLockElement === canvas);
  overlay.style.display = pointerLocked ? 'none' : 'flex';
});
```

### Setup

```js
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
body.appendChild(renderer.domElement);
const canvas = renderer.domElement;

const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
 Sun
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.direction.set(0.5, 1, 0.3).normalize();
scene.add(sun);

const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

Player spawn:
```js
const EYE = 1.62;
const player = new THREE.Object3D();
player.position.set(8, terrainHeightAt(8,8) + 2, 8);
scene.add(player);
camera.position.set(0, EYE, 0);
player.add(camera);
```

Wait, camera rotation order YXZ driven by yaw/pitch. If I put camera in player object and set camera.rotation.order='YXZ', then set camera.rotation.y = yaw, camera.rotation.x = pitch. The player object just holds position. Let me set camera.rotation.order = 'YXZ' and update camera.rotation.y/x.

Actually simpler: set player.rotation? No. Let me put camera directly and set its position and rotation. But then collision uses player.position which is camera.position. Let me just use camera as player.

```js
camera.position.set(8, terrainHeightAt(8,8)+2, 8);
camera.rotation.order = 'YXZ';
```
And use camera.position for physics. Good. EYE is baked in (camera is at eye height). Feet = camera.position.y - EYE.

Wireframe outline:
```js
const outlineGeo = new THREE.BoxGeometry(1.001, 1.001, 1.001);
const outlineMat = new THREE.LineBasicMaterial({ color: 0x000000 });
const outline = new THREE.LineSegments(new THREE.EdgesGeometry(outlineGeo), outlineMat);
outline.visible = false;
scene.add(outline);
```

Water:
```js
const waterMat = new THREE.MeshLambertMaterial({ color: 0x3388ff, transparent: true, opacity: 0.6 });
const water = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), waterMat);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);
```

Clouds as described.

### Animation loop

```js
let last = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  let dt = (now - last) / 1000;
  last = now;
  dt = Math.min(dt, 0.05); // clamp
  
  if (pointerLocked) {
    updatePlayer(dt);
  }
  updateWorld();
  updateTarget();
  if (hasTarget) {
    const tx = Math.floor(hitPoint.x - hitNormal.x*0.5);
    const ty = Math.floor(hitPoint.y - hitNormal.y*0.5);
    const tz = Math.floor(hitPoint.z - hitNormal.z*0.5);
    outline.position.set(tx+0.5, ty+0.5, tz+0.5);
    outline.visible = true;
  } else {
    outline.visible = false;
  }
  // clouds
  clouds.forEach(...)
  // water
  water.position.x = camera.position.x;
  water.position.z = camera.position.z;
  
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
```

terrainHeightAt:
```js
function terrainHeightAt(x, z) {
  return columnHeight(Math.round(x), Math.round(z));
}
```
Spawn at x=8,z=8 → columnHeight(8,8). Spawn above it +2.

Let me double check the collision function signature — I pass feet as the y. Let me finalize collide:

```js
function collides(px, feet, pz) {
  const hw = 0.3, h = 1.8, E = 1e-3;
  const minX = Math.floor(px - hw), maxX = Math.floor(px + hw);
  const minY = Math.floor(feet), maxY = Math.floor(feet + h - E);
  const minZ = Math.floor(pz - hw), maxZ = Math.floor(pz + hw);
  for (let x = minX; x <= maxX; x++)
    for (let y = minY; y <= maxY; y++)
      for (let z = minZ; z <= maxZ; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}
```

Now updatePlayer:
```js
function updatePlayer(dt) {
  const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
  let mx = 0, mz = 0;
  if (keys['w']) { mx += forward.x; mz += forward.z; }
  if (keys['s']) { mx -= forward.x; mz -= forward.z; }
  if (keys['d']) { mx += right.x; mz += right.z; }
  if (keys['a']) { mx -= right.x; mz -= right.z; }
  const len = Math.hypot(mx, mz);
  if (len > 0) { mx /= len; mz /= len; }
  
  const px = camera.position.x, pz = camera.position.z;
  const feet = camera.position.y - EYE;
  
  let nx = px + mx * SPEED * dt;
  if (!collides(nx, feet, pz)) camera.position.x = nx;
  let nz = pz + mz * SPEED * dt;
  if (!collides(camera.position.x, feet, nz)) camera.position.z = nz;
  
  vy -= GRAVITY * dt;
  if (keys[' '] && onGround) { vy = JUMP_SPEED; onGround = false; }
  if (vy < -50) vy = -50;
  
  let ny = feet + vy * dt;
  if (collides(camera.position.x, ny, camera.position.z)) {
    if (vy < 0) {
      // land
      let s = ny;
      for (let i = 0; i < 24 && collides(camera.position.x, s, camera.position.z); i++) s += 0.1;
      camera.position.y = s + EYE;
      onGround = true;
      vy = 0;
    } else {
      vy = 0;
    }
  } else {
    camera.position.y = ny + EYE;
    onGround = false;
  }
  
  if (camera.position.y < -20) {
    camera.position.set(8, terrainHeightAt(8,8)+2, 8);
    vy = 0; onGround = true;
  }
}
```

Constants:
```js
const SPEED = 5.5, GRAVITY = 25, JUMP_SPEED = 8.5, EYE = 1.62;
let vy = 0, onGround = true;
let yaw = 0, pitch = 0;
```

Initial onGround: spawn above terrain, so maybe onGround=false initially so they fall. Let me set onGround=false at start so gravity applies. Actually spawn at terrainHeight+2, so they'll fall onto the surface. onGround=false is correct.

Now, the forward/right vectors: with yaw=0, forward = (0,0,-1) → moving W goes -z. Right = (1,0,0) → D goes +x. Standard. Good.

Let me double check camera rotation: rotation.order='YXZ', set camera.rotation.y = yaw, camera.rotation.x = pitch. With YXZ order, rotation applied: Z then X then Y? Order 'YXZ' means rotate around Y first, then X, then Z. Since we only set Y and X, result is yaw around Y then pitch around X (local). This gives standard FPS look. Good.

Let me verify getWorldDirection isn't needed since I set rotation directly. For raycast I need camera forward. I can compute from rotation: with order YXZ, forward = ... Let me just compute manually:
forward.x = -sin(yaw)*cos(pitch)
forward.y = sin(pitch)
forward.z = -cos(yaw)*cos(pitch)

Let me use that for raycast to be safe:
```js
const fwd = new THREE.Vector3(
  -Math.sin(yaw)*Math.cos(pitch),
  Math.sin(pitch),
  -Math.cos(yaw)*Math.cos(pitch)
);
raycaster.set(camera.position, fwd);
```

That's reliable.

Now let me reconsider the meshing neighbor cull: getBlock returns air for missing chunks. So at chunk borders with ungenerated neighbors, faces toward them are shown. Once neighbor generates+meshes, those internal faces get culled and neighbor's outer faces shown. But we won't rebuild our mesh when neighbor generates. That means briefly we show extra faces at borders until... hmm. Actually when neighbor gets data and meshes, our chunk still shows faces toward it (extra geometry) until we rebuild. But we rebuild our chunk on edits only. So there could be persistent extra faces at borders between generated-but-unmeshed regions.

Wait, but meshing only happens when all 4 neighbors have data. So when our chunk meshes, all neighbors have data (but may not have meshes yet). Our faces toward neighbors: neighbor has data, so getBlock returns neighbor's block → culled correctly. Good, no extra faces at the moment we mesh. Later if neighbor edits, both rebuild. So it's consistent. The only issue is if neighbor's data differs from what we assumed — but data is deterministic and stable. So fine.

But consider: we mesh chunk A when its neighbors have data. Later, does neighbor's data ever change? Only via player edits, which trigger rebuild of both. So no stale faces. Good.

Now, potential performance: meshing 2 chunks/frame, generating 4 chunks/frame. As player moves, this streams terrain. Fine.

Let me reconsider the generation rate vs movement. Player moves 5.5 m/s = 0.35 chunks/s. Each chunk is 16 wide. So player crosses a chunk every ~45 frames. We generate 4 chunks/frame, so plenty ahead. Good.

Now let me reconsider chunk mesh building cost: each chunk up to 16*16*80 = 20480 blocks, but most are air/culled. Building ~ up to a few thousand faces. 2/frame is fine.

Let me reconsider the "fractal noise" for height. m = fractal2(cx*0.004, cz*0.004, 4) in [0,1]. H = floor(5 + m*m*58 + h*10) where h = fractal2 at *0.02. m in [0,1], m*m in [0,1], so m*m*58 in [0,58]. h*10 in [0,10]. So H in [5, 73]. Good, mountains up to ~73, below 80. Snow at H>=46. Good. Beaches/water at H<=16. Plains grass in between.

Wait, but the noise fractal average — fractal2 returns weighted average of octaves each in [0,1], so result in [0,1]. Good. But note low-frequency (0.004) gives broad terrain variation, high-freq (0.02) adds detail. m dominates height (scaled by 58). Reasonable.

Let me reconsider: with m in [0,1], mean ~0.5, m*m ~0.25, H ~ 5 + 14.5 + (h~0.5*10=5) ≈ 24. So typical height ~24, above water at 14.3. Good, grass plains above water. Mountains higher. Beaches low.

Now caves: noise3 at *0.09 > 0.67 → air, for y in [3, H-2]. At high frequency 0.09, caves are small pockets. 0.67 threshold makes them sparse. Good.

Trees: hash(wx,wz) < 0.02 → 2% of grass columns get trees, but only if local x,z in [2,13] (so 10x10 = 100 of 256 columns per chunk qualify) and H in [6,71] and surface is grass. So trees appear on grass plains. Good.

Hmm, wait: the tree leaf canopy is 5 wide (radius 2) and we require local x in [2,13]. At x=2, canopy x from 0 to 4. At x=13, canopy 11 to 15. All within [0,15]. Good. But we also need the trunk leaves to not need neighboring columns' data — they're within this chunk. Good.

But actually, I realize the leaves might extend vertically above 80 for tall trees near mountaintops, but we cap H<=71 and top leaf at H+8=79 < 80. Good. And trunk top at H+4. Leaves from H+5 to H+8. At H=71, top leaf at 79. OK within [0,79]. Good.

Let me also make sure leaves only grow into air — yes, we check data[idx]===0 before placing. And we place trunk first (wood), then leaves into remaining air. Good.

Now, one concern: tree leaves placed in the same chunk's data — but what about a tree near local x=2..13 — fine. But two trees could be close; leaves just overwrite air. Fine.

Let me now also double-check the blockAt for the surface when there's a tree: surface block at y=H is grass (id 1). Tree trunk starts at H+1. Good, trunk sits on grass.

Now let me reconsider getBlock for y up to 79 and the data indexing. data index = (y*16 + lz)*16 + lx. For y=79, lz=15, lx=15: (79*16+15)*16+15 = (1264+15)*16+15 = 1279*16+15 = 20464+15 = 20479. Array length 20480. Good, index 20479 valid.

Now let me write the complete file. Let me also handle the initial world generation at spawn so the player isn't in void. On load, generate chunks around (8,8) and build meshes. Actually the per-frame loop will generate and mesh over a few frames. But to avoid spawning in mid-air with no ground visible, let me pre-generate a small radius at startup.

Let me pre-generate chunks within radius 2 at startup synchronously, then let the loop continue. That ensures ground under player.

```js
// initial generation
for (let dz=-2; dz<=2; dz++)
  for (let dx=-2; dx<=2; dx++) {
    const cx=8/16+dx... 
  }
```
Wait spawn x=8 → cx = floor(8/16)=0. So chunk (0,0) contains spawn. Generate chunks cx in [-2,2]? Let me generate within a few chunks so meshes can build. Let me generate cx,cz in [-3,3] and then build meshes for those whose neighbors have data (which after full generation, all do). Let me just generate then call buildChunkMesh for all generated.

Actually, let me generate a radius and then mesh. Simplest: generate chunks within radius R, then build meshes for all of them (since all neighbors will have data). Let me do radius 3: generate 7x7=49 chunks, then mesh all 49 (all have data and neighbors). That gives a nice starting view. Might be a bit heavy but OK (49 * few thousand faces). Let me reduce to radius 2 (5x5=25 chunks) to be safe on initial load performance. Actually 25 chunks each up to maybe 2000 faces = 50k faces, fine.

Hmm, but meshing 25 chunks at once is fine. Let me do radius 2.

Wait, but meshing requires 4 neighbors to have data. After generating radius 2 (chunks -2..2 in both), all interior chunks have neighbors. Border chunks (at ±2) have neighbors at ±3 which aren't generated. So those border chunks can't mesh (missing neighbor data). That's fine — they'll mesh as player moves and more generate. So I'll mesh all chunks in radius 2 that have all 4 neighbors present. The central 3x3 (ch -1..1) definitely mesh. Border ones won't until neighbors generate. That's acceptable; the player at center sees the central area fully.

Let me just run the same generate+mesh logic at startup for a radius, then rely on the loop.

Let me write an initWorld() that generates radius 3 and meshes those with complete neighbor data.

Actually simpler: at startup, generate chunks within radius 3 synchronously (49 chunks), then attempt to mesh each (buildChunkMesh only needs data, and culling reads getBlock which returns air for missing — so even border chunks mesh fine visually, just showing faces toward ungenerated areas which get filled later). Wait, but if I mesh a border chunk showing faces toward ungenerated neighbor, and later the neighbor generates and meshes, my border chunk won't auto-rebuild → shows stale extra faces. 

To avoid that, at startup I should only mesh chunks whose 4 neighbors have data (like the loop). So generate radius 3, then mesh only those with all neighbors present (interior 5x5 = chunks -2..2 have neighbors at -3..3 which are generated → all 25 have data neighbors → mesh all 25). Wait radius 3 generates -3..3 (7 values). Chunks at ±2 have neighbors at ±3 which exist. So all 25 chunks in radius 2 have all 4 neighbors present (since neighbors are within -3..3). Actually chunk at cx=2 has neighbor cx=3 which is generated. cx=-3 has neighbor -4 which is NOT generated. So chunks at the very edge (±3) lack neighbors, but we only mesh radius 2 chunks (±2), whose neighbors are within ±3, all generated. So meshing all 25 radius-2 chunks works. 

Let me generate radius 3 and mesh radius 2. Then loop continues.

Actually, let me just generate radius 3 and mesh all chunks where all 4 orthogonal neighbors exist in the map. Clean.

Let me now also double check: the initial spawn height terrainHeightAt(8,8). columnHeight(8,8): m=fractal2(0.032,0.032,4), h=fractal2(0.16,0.16,4). Some value. H ~ 20ish. Spawn at H+2. Good, player stands on ground.

Let me also ensure the player doesn't spawn inside a tree or cave. Could spawn in a cave (air) → falls. Fine, lands on floor. Could spawn on a tree? Only if surface is grass and a tree grew there — but tree occupies above surface, surface itself is grass block, player at H+2 is above leaves possibly. Leaves top at H+8. If H small, player at H+2 might be within leaf canopy! E.g., H=10, leaves from 15 to 18, player spawns at 12, falls through leaves onto... grass at 10? But grass at 10 was replaced by trunk? No—trunk is 11-14, leaves 15-18. Grass at 10 remains (surface). Player spawns at 12 (inside trunk region!) → falls, hits trunk, slides off. Messy but not fatal. To reduce this, spawn at H+3 or check. Let me spawn at H+3 and also it's rare. Actually let me spawn higher: terrainHeightAt + 3. And the fall will settle. It's fine functionally. But spawning inside a trunk block could cause collision jitter. Rare (2% of grass cols with the specific hash). Acceptable. Alternatively spawn at max(H+2, leafTop+1). Overkill. Let me just do H+3.

Hmm, actually if player spawns inside solid blocks, the first physics step might get stuck. Let me spawn at H+4 to clear typical trees (leaves down to H+5). At H+4, player feet at H+4, occupies [H+4, H+5.8]. Leaves start at H+5. Slight overlap at H+5. Meh. Let me just spawn at H+3 and accept occasional minor snag. Realistically trees are 2% and this is a demo. Fine.

Actually, let me make spawn robust: find the surface height and spawn 2 above, but if that's blocked, keep going up. Simple loop:
```js
let sy = terrainHeightAt(8,8) + 2;
while (getBlock(8, sy, 8) !== 0 && sy < 80) sy++;
camera.position.set(8, sy + 0.5, 8);
```
This climbs out of any obstruction. Good. Let me use that.

Now let me also reconsider: do I need to worry about the player spawning in water? If H <= 16 (beach/lake), surface is sand at y<=16, water at 14.3. Player spawns at H+2 ~ 18, above water. Falls to land or water surface (visual). Fine.

Let me finalize and write the code. Let me be careful with template literals and escaping in the HTML (no backticks issues since it's plain JS in script).

Let me also make sure requestPointerLock works on click even though overlay covers canvas. The overlay click handler calls canvas.requestPointerLock(). Good.

One more: after pointer lock, the overlay should hide. pointerlockchange sets overlay display none when locked. Good. And reappears when unlocked.

Let me also add a crosshair always visible (even during overlay? overlay covers screen so crosshair behind is fine). The crosshair is pointer-events:none and z-index 10, overlay z-index 20 covers it. Fine.

Let me write it all out now.

Let me reconsider the hashing to ensure good distribution and determinism. Using integer math:

```js
function hash(ix, iy) {
  let h = (ix * 374761393 + iy * 668265263) | 0;
  h = Math.imul(h ^ (h >>> 13), 2246822507);
  h = Math.imul(h ^ (h >>> 16), 3266489909);
  return (h >>> 0) / 4294967296;
}
```

Math.imul is supported in all modern browsers and Firefox/Chrome. Good. Let me use it.

hash3:
```js
function hash3(ix, iy, iz) {
  let h = (ix * 374761393 + iy * 668265263 + iz * 1523486461) | 0;
  h = Math.imul(h ^ (h >>> 13), 2246822507);
  h = Math.imul(h ^ (h >>> 16), 3266489909);
  return (h >>> 0) / 4294967296;
}
```

These are deterministic and well-distributed.

Now noise2 uses hash at integer grid points. Good.

Let me reconsider fractal2 normalization: sum of amps / sum of amps. With amp starting 0.5 halving: 0.5,0.25,0.125,0.0625 sum=0.9375. Good.

Let me write noise2 and noise3 carefully.

```js
function noise2(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = smoothstep(xf), v = smoothstep(yf);
  const a = hash(xi, yi);
  const b = hash(xi+1, yi);
  const c = hash(xi, yi+1);
  const d = hash(xi+1, yi+1);
  return lerp(lerp(a,b,u), lerp(c,d,u), v);
}
```

Good.

Now let me assemble everything. Let me also make sure I dispose geometries properly when removing far chunks (spec requires disposing geometry). Done.

Let me write the final file.

Actually, I realize I should double check the raycast hit normal. THREE raycast gives hit.face.normal in object space, but for box geometry (axis-aligned unit cubes at integer positions), the normal in world space equals object space normal (since boxes aren't rotated). Our chunk mesh is a collection of box faces; the hit.normal is the face normal in the mesh's local (which is world, since mesh at origin with no rotation). So hit.normal is world normal. Good. And hit.point is world position. Good.

But wait, our geometry isn't individual boxes—it's a merged BufferGeometry. The face normals are stored per-vertex (we pushed normals). Raycasting uses these per-triangle normals. For a merged mesh, intersectObjects computes per-triangle normal from geometry 'normal' attribute. Since we set normals correctly, hit.face.normal is correct world normal. Good.

Actually, THREE's intersectObjects on a BufferGeometry: it returns face.normal from the normal attribute for that triangle. Yes. Good.

Let me also confirm hit.point is in world coordinates. Since the mesh has no transform (at origin, no parent transform), local = world. Good.

Now the outline positioning: target block center at (tx+0.5, ty+0.5, tz+0.5). Good.

Let me also make the outline use EdgesGeometry for clean lines. EdesGeometry(BoxGeometry(1,1,1)). Position at block center. Good.

Alright, writing final code.

Let me reconsider the "far 400" and fog 40-110. Good. Sky color matches fog. Good.

Let me reconsider directional light direction—fixed is fine (fake lighting is per-face anyway).

Let me also ensure the water plane is below terrain surfaces generally at 14.3. Where terrain <= 14, water shows. Good.

Let me write it all.

Also need to handle: when pointer not locked, still render scene (so overlay shows behind? overlay is opaque anyway). We render every frame regardless. Good.

Let me also pause physics when not locked (player freezes). Yes, updatePlayer only when locked.

Let me write final.

Also, I want to make sure the initial meshing at startup doesn't hang. Generating 49 chunks and meshing ~25 is fine.

Let me also add pixel ratio cap to avoid perf issues on high-DPI.

Let me write the complete HTML now.

Let me reconsider the hotbar selection display and default selectedBlock = 1.

Also keys object: track lowercase key strings. Space is ' '. Arrow keys not needed.

Let me also prevent the page from scrolling with space/arrows. Not critical but let me add e.preventDefault on space maybe. Actually space causes scroll; let me preventDefault for game keys. I'll add preventDefault in keydown for space and arrows. Minor.

Let me finalize.

One more consideration: the spec says "Clicking the start overlay requests pointer lock". So overlay click → requestPointerLock. Also maybe clicking canvas directly, but overlay covers it initially. Fine.

Let me also make sure that when we break a block at y==0 we don't. Spec: "left click sets the target to air (not at y 0)". Good.

Also "right click places the selected block if the cell is air and does not overlap the player." Good.

Let me write it.

Actually, let me reconsider whether to include Math.imul — it's standard. Fine.

Let me also double-check smoothstep and lerp defined before use. Define all helper functions first.

Let me also make the fractal for caves 3D with octaves? Spec says "plus a 3D version for caves". I'll make noise3 single octave (or a couple). Single 3D value noise is fine for cave noise. Let me keep single octave for caves (noise3). Actually let me make it a light fractal too for more natural caves. Spec just says 3D version. I'll do a 2-octave version for better look. Actually simpler: single octave noise3. Let me do 2 octaves to be nice. Hmm, but threshold 0.67 with single octave is fine. Let me keep single octave for caves to match "0.67" threshold sensibly. Single octave.

Let me write final code now.

Let me reconsider: In generateChunkData, I call blockAt for each y. blockAt calls columnHeight which calls fractal2 twice. That's 2 fractal2 (4 octaves each = 16 noise2 calls with hash) per column, times 80 rows but height is per-column so I compute it once per column. Let me compute H once per column and reuse. In my loop I call blockAt per row which recomputes H each time. Let me optimize: compute H once per column, then loop rows calling a lighter function. But blockAt recomputes H each call → 80x per column = wasteful but only 4 chunks/frame * 256 columns * 80 = 81920 height calcs/frame. Each height calc is 32 hash+lerp ops. ~2.6M ops/frame. Might be okay but let me optimize by precomputing H per column and a cave-noise inline.

Let me refactor: 
```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(16*16*80);
  const x0 = cx*16, z0 = cz*16;
  for (let lz=0; lz<16; lz++) {
    for (let lx=0; lx<16; lx++) {
      const wx = x0+lx, wz = z0+lz;
      const H = columnHeight(wx, wz);
      for (let y=0; y<80; y++) {
        let id;
        if (y===0) id=3;
        else if (y>=3 && y<=H-2) {
          id = (noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) ? 0 : blockTypeUnderSurface(wx,y,wz,H);
        } else {
          id = blockTypeUnderSurface(wx,y,wz,H);
        }
        data[(y*16+lz)*16+lx] = id;
      }
      // trees...
    }
  }
  return data;
}
```
where blockTypeUnderSurface returns the non-cave block type given y and H:
```js
function blockTypeUnderSurface(wx,y,wz,H) {
  if (y < H-3) return 3;
  if (y <= H-1) {
    if (H<=16) return 4;
    if (H>=37) return 3;
    return 2;
  }
  // surface y==H
  if (H>=46) return 7;
  if (H>=37) return 3;
  if (H<=16) return 4;
  return 1;
}
```
And blockAt (for reading during meshing) can just call blockTypeUnderSurface plus cave check. But meshing reads getBlock which reads stored data, not recomputing. So blockAt is only used... actually getBlock reads stored data, never calls blockAt. So I don't even need blockAt function! The stored data already reflects everything. Let me drop blockAt and just use generateChunkData + blockTypeUnderSurface internally. Good, cleaner.

Wait, do I need blockAt anywhere? getBlock reads data. setBlock writes data. Meshing uses getBlock. Editing uses setBlock. So blockAt not needed. Remove it.

Let me finalize blockTypeUnderSurface and generateChunkData.

Edge: when H is small (<= some), H-3 could be negative; y<H-3 with H=10 → y<7. y=0 handled separately. Fine. When H-2 < 3 (H<5), the cave loop `y>=3 && y<=H-2` never true (H-2<3). Fine. H min ~5.

When y <= H-1 but y could be 0? y=0 handled earlier (returns 3). For y>=1, blockTypeUnderSurface handles. Good. But note for y between 1 and H-4 (below H-3), returns 3 (stone). For y=H-3..H-1 returns dirt/sand/stone. For y=H returns surface. Good.

Wait, but what about when y < H-3 but y is like 1..(H-4): stone. And the "3 layers under surface" are H-3,H-2,H-1. And surface H. Total column: 0 stone, 1..H-4 stone, H-3..H-1 fill, H surface. Consistent.

Now trees placed after filling column. Good.

Let me write final code.

Let me reconsider tree height requirement: I said H>=6 and H<=71. Trunk 4 blocks (H+1..H+4), leaves H+5..H+8. Top leaf at H+8 <= 79 requires H<=71. And need H>=? trunk needs to fit: H+4 <= 79 → H<=75. Leaves H+8<=79 → H<=71. Also need surface grass (th===1). And local x,z in [2,13]. Let me require H>=5 for trunk to be above surface meaningfully; but if H is small, leaves might be below water—but that's fine visually. Let me require H>=5. Actually let me require the trunk to be at least above surface; any H works as long as <=71. But very low H (like 5) means leaves at 10-13, underwater maybe. Fine. Let me just require H>=4 and H<=71 and surface grass and hash<0.02 and local in range.

Hmm, but if H is like 5 and there's water at 14.3, the tree would be underwater—fine, still looks OK. Let me not over-constrain. Require H in [4,71].

Actually, wait—if H <= 16 it's sand/beach, surface sand not grass, so no trees there anyway (th must be grass=1). Trees only on grass (H in (16,46) roughly, plus mountain grass up to 45). So H typically 17-45 for trees. Good, H>=4 is redundant but harmless.

Let me finalize.

Let me also reconsider: the leaves placement loops dx,dz from -r to r. For r=2 that's 25 cells per layer, 2 layers = 50, plus r=1 (9) + r=0(1) = 60 leaf placements per tree. Fine.

Now let me write the whole thing.

Let me also make sure to set camera.rotation order and initial yaw/pitch. yaw=0, pitch=0.

Let me write it all out cleanly.

Also, I should double check: requestPointerLock may require user gesture; click provides it. Good.

Let me also handle the case where requestPointerLock fails (some browsers). We just stay on overlay. Fine.

Final code below.

Let me reconsider performance of updateWorld generating 4 and meshing 2 per frame while also doing initial 25 meshes. Fine.

Let me also add: when editing, we should update the outline immediately (it will next frame). Fine.

Let me write.

Actually, let me reconsider the meshing "within 4 chunks" — I interpreted as Chebyshev distance <= 4. And generation "within 5 chunks" Chebyshev <= 5. And removal ">7". Let me keep Chebyshev (abs(dx)<=N and abs(dz)<=N). Good.

Let me also make sure generation and meshing loops skip already-existing data/mesh appropriately and respect limits.

Let me write the final HTML.

Let me reconsider: for meshing, I check `if (entry.mesh) continue;` to skip already-meshed. And require all 4 neighbors have data. Good.

Also for generation, `if (!chunkMap.has(key))` generate. Good.

Now, the removal loop iterates chunkMap and deletes far entries. Deleting during iteration of a Map is allowed in JS (safe to delete current). Good.

Let me write it.

Let me also ensure outline material color black and visible toggling. Good.

Let me write final and double-check syntax.

I'll now produce the full file.

Let me reconsider the water: PlaneGeometry rotated -PI/2 lies in XZ plane. Position y=14.3. Re-center x,z each frame. Size 200. Good. Make it render maybe behind transparent. opacity 0.6. Good.

Also, should water be affected by fog? Yes automatically. Good.

Let me also add that clouds use a material that's additive-ish white transparent. MeshLambertMaterial with color white, transparent opacity 0.85, and maybe depthWrite false so they blend. Let me set cloud material: new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.9, depthWrite:false}). Good.

Now finalize.

Let me reconsider initial spawn: terrainHeightAt(8,8) uses columnHeight(8,8). Fine.

Let me write the code carefully with correct variable names.

I think I'm ready. Let me produce the final single code block.

Let me write out the JS in full:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MC</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:hidden;background:#87ceeb;font-family:sans-serif}
canvas{display:block}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:20px;height:20px;pointer-events:none;z-index:10}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:rgba(0,0,0,.7)}
#crosshair::before{top:50%;left:0;width:100%;height:2px;transform:translateY(-50%)}
#crosshair::after{left:50%;top:0;height:100%;width:2px;transform:translateX(-50%)}
#hotbar{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);display:flex;gap:4px;padding:6px;background:rgba(0,0,0,.55);border-radius:6px;z-index:10;pointer-events:none}
.slot{width:46px;height:46px;border:2px solid rgba(255,255,255,.35);border-radius:4px;position:relative;display:flex;align-items:center;justify-content:center;background:#000}
.slot .num{position:absolute;top:1px;left:3px;color:#fff;font-size:12px;font-weight:bold;text-shadow:1px 1px 2px #000}
.slot.sel{border-color:#fff;box-shadow:0 0 8px #fff}
#overlay{position:fixed;inset:0;background:rgba(0,0,0,.78);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:20;text-align:center}
#overlay h1{font-size:52px;letter-spacing:3px;margin-bottom:22px;text-shadow:2px 2px 0 #000}
#overlay ul{text-align:left;font-size:16px;line-height:1.9;margin-bottom:26px;list-style:none}
#overlay li::before{content:'» ';}
#overlay .play{font-size:22px;padding:12px 30px;border:2px solid #fff;border-radius:8px;cursor:pointer;background:rgba(255,255,255,.08)}
#overlay .play:hover{background:rgba(255,255,255,.2)}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MC</h1>
  <ul>
    <li>WASD — move</li>
    <li>Mouse — look around</li>
    <li>Space — jump</li>
    <li>Left click — break block</li>
    <li>Right click — place block</li>
    <li>Keys 1–7 or wheel — select block</li>
  </ul>
  <div class="play">Click to play</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// ---------- noise ----------
function smoothstep(t){return t*t*(3-2*t);}
function lerp(a,b,t){return a+(b-a)*t;}
function hash(ix,iy){
  var h=(ix*374761393+iy*668265263)|0;
  h=Math.imul(h^(h>>>13),2246822507);
  h=Math.imul(h^(h>>>16),3266489909);
  return (h>>>0)/4294967296;
}
function hash3(ix,iy,iz){
  var h=(ix*374761393+iy*668265263+iz*1523486461)|0;
  h=Math.imul(h^(h>>>13),2246822507);
  h=Math.imul(h^(h>>>16),3266489909);
  return (h>>>0)/4294967296;
}
function noise2(x,y){
  var xi=Math.floor(x),yi=Math.floor(y);
  var xf=x-xi,yf=y-yi;
  var u=smoothstep(xf),v=smoothstep(yf);
  var a=hash(xi,yi),b=hash(xi+1,yi),c=hash(xi,yi+1),d=hash(xi+1,yi+1);
  return lerp(lerp(a,b,u),lerp(c,d,u),v);
}
function fractal2(x,y,o){
  var amp=0.5,freq=1,sum=0,norm=0;
  for(var i=0;i<o;i++){sum+=amp*noise2(x*freq,y*freq);norm+=amp;amp*=0.5;freq*=2;}
  return sum/norm;
}
function noise3(x,y,z){
  var xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z);
  var xf=x-xi,yf=y-yi,zf=z-zi;
  var u=smoothstep(xf),v=smoothstep(yf),w=smoothstep(zf);
  var c00=hash(xi,yi),c10=hash(xi+1,yi),c01=hash(xi,yi+1),c11=hash(xi+1,yi+1);
  var x0=lerp(c00,c10,u),x1=lerp(c01,c11,u);
  var y0=lerp(x0,x1,v);
  var c00b=hash(xi,zi),c10b=hash(xi+1,zi),c01b=hash(xi,yi+1,zi),c11b=hash(xi+1,yi+1,zi);
  ...
}
```

Hmm wait, my noise3 needs 8 corner hashes. Let me redo properly:

```js
function noise3(x,y,z){
  var xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z);
  var xf=x-xi,yf=y-yi,zf=z-zi;
  var u=smoothstep(xf),v=smoothstep(yf),w=smoothstep(zf);
  function g(a,b,c){return hash3(a,b,c);}
  var c000=g(xi,yi,zi),c100=g(xi+1,yi,zi),c010=g(xi,yi+1,zi),c110=g(xi+1,yi+1,zi);
  var c001=g(xi,yi,zi+1),c101=g(xi+1,yi,zi+1),c011=g(xi,yi+1,zi+1),c111=g(xi+1,yi+1,zi+1);
  var x00=lerp(c000,c100,u),x10=lerp(c010,c110,u);
  var x01=lerp(c001,c101,u),x11=lerp(c011,c111,u);
  var y0=lerp(x00,x10,v),y1=lerp(x01,x11,v);
  return lerp(y0,y1,w);
}
```

Good.

Now terrain:

```js
function columnHeight(cx,cz){
  var m=fractal2(cx*0.004,cz*0.004,4);
  var h=fractal2(cx*0.02,cz*0.02,4);
  return Math.floor(5 + m*m*58 + h*10);
}
function blockType(y,H){
  if(y<H-3) return 3;
  if(y<=H-1){
    if(H<=16) return 4;
    if(H>=37) return 3;
    return 2;
  }
  if(H>=46) return 7;
  if(H>=37) return 3;
  if(H<=16) return 4;
  return 1;
}
```

generateChunkData:

```js
function generateChunkData(cx,cz){
  var data=new Uint8Array(16*16*80);
  var x0=cx*16,z0=cz*16;
  for(var lz=0;lz<16;lz++){
    for(var lx=0;lx<16;lx++){
      var wx=x0+lx,wz=z0+lz;
      var H=columnHeight(wx,wz);
      for(var y=0;y<80;y++){
        var id;
        if(y===0) id=3;
        else if(y>=3 && y<=H-2){
          id = (noise3(wx*0.09,y*0.09,wz*0.09) > 0.67) ? 0 : blockType(y,H);
        } else {
          id = blockType(y,H);
        }
        data[(y*16+lz)*16+lx]=id;
      }
      // trees
      if(blockType(H,H)===1 && H>=4 && H<=71 && lx>=2 && lx<=13 && lz>=2 && lz<=13){
        if(hash(wx,wz)<0.02){
          for(var t=1;t<=4;t++){
            var ty=H+t;
            if(ty<80) data[(ty*16+lz)*16+lx]=5;
          }
          var specs=[{dy:5,r:2},{dy:6,r:2},{dy:7,r:1},{dy:8,r:0}];
          for(var s=0;s<specs.length;s++){
            var sp=specs[s];
            for(var dx=-sp.r;dx<=sp.r;dx++){
              for(var dz=-sp.r;dz<=sp.r;dz++){
                var ly=H+sp.dy, lx2=lx+dx, lz2=lz+dz;
                if(lx2<0||lx2>=16||lz2<0||lz2>=16||ly>=80) continue;
                var li=(ly*16+lz2)*16+lx2;
                if(data[li]===0) data[li]=6;
              }
            }
          }
        }
      }
    }
  }
  return data;
}
```

Note blockType(H,H): for y==H, blockType returns surface type (since y<=H-1 is false when y==H, goes to surface branch). Good. blockType(H,H) returns grass if appropriate.

Chunk map and helpers:

```js
var chunkMap=new Map();
var chunkMeshList=[];
var blockMaterial=new THREE.MeshLambertMaterial({vertexColors:true});

function getBlock(x,y,z){
  if(y<0||y>=80) return 0;
  var cx=Math.floor(x/16),cz=Math.floor(z/16);
  var e=chunkMap.get(cx+","+cz);
  if(!e||!e.data) return 0;
  return e.data[(y*16+(z-cz*16))*16+(x-cx*16)];
}
function setBlock(x,y,z,id){
  if(y<0||y>=80) return;
  var cx=Math.floor(x/16),cz=Math.floor(z/16);
  var e=chunkMap.get(cx+","+cz);
  if(!e||!e.data) return;
  e.data[(y*16+(z-cz*16))*16+(x-cx*16)]=id;
}
```

buildChunkMesh:

```js
var FACES=[
  {n:[1,0,0],v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]]},
  {n:[-1,0,0],v:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]},
  {n:[0,1,0],v:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]},
  {n:[0,-1,0],v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
  {n:[0,0,1],v:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]},
  {n:[0,0,-1],v:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]]}
];
var BLOCK_COLORS=[0,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];

function buildChunkMesh(cx,cz){
  var e=chunkMap.get(cx+","+cz);
  if(!e||!e.data) return;
  var pos=[],nor=[],col=[],idx=[];
  var vi=0;
  var x0=cx*16,z0=cz*16;
  for(var lz=0;lz<16;lz++){
    for(var lx=0;lx<16;lx++){
      for(var y=0;y<80;y++){
        var id=e.data[(y*16+lz)*16+lx];
        if(id===0) continue;
        var wx=x0+lx,wz=z0+lz;
        var bc=BLOCK_COLORS[id];
        var cr=((bc>>16)&255)/255, cg=((bc>>8)&255)/255, cb=(bc&255)/255;
        for(var f=0;f<6;f++){
          var face=FACES[f];
          var nid=getBlock(wx+face.n[0], y+face.n[1], wz+face.n[2]);
          if(nid!==0) continue;
          var light = (f===2)?1.0 : (f===3)?0.55 : 0.8;
          for(var k=0;k<4;k++){
            var vp=face.v[k];
            pos.push(wx+vp[0], y+vp[1], wz+vp[2]);
            nor.push(face.n[0], face.n[1], face.n[2]);
            col.push(cr*light, cg*light, cb*light);
          }
          idx.push(vi,vi+1,vi+2, vi,vi+2,vi+3);
          vi+=4;
        }
      }
    }
  }
  var geom=e.geom || (e.geom=new THREE.BufferGeometry());
  geom.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(nor,3));
  geom.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  geom.setIndex(idx);
  geom.computeBoundingSphere();
  if(!e.mesh){
    e.mesh=new THREE.Mesh(geom, blockMaterial);
    e.mesh.frustumCulled=false;
    scene.add(e.mesh);
    chunkMeshList.push(e.mesh);
  }
}
```

Wait, computeBoundingSphere with empty attributes might error. If a chunk has no visible blocks (all air), pos is empty. Float32BufferAttribute with empty array is fine, but computeBoundingSphere on empty might throw. Let me guard: if pos.length===0, skip computeBoundingSphere and maybe still create mesh (empty). Actually an empty mesh is fine. Let me guard computeBoundingSphere.

Actually, setIndex with empty idx is fine. computeBoundingSphere with no vertices → might return undefined sphere. Let me wrap in try or check length. I'll check if pos.length===0, skip computeBoundingSphere.

rebuild functions:

```js
function ensureChunkData(cx,cz){
  var key=cx+","+cz;
  if(!chunkMap.has(key)){
    chunkMap.set(key,{data:generateChunkData(cx,cz),mesh:null,geom:null});
  }
}
function rebuildMesh(cx,cz){
  var e=chunkMap.get(cx+","+cz);
  if(e&&e.data){ buildChunkMesh(cx,cz); }
}
function rebuildChunkAt(x,y,z){
  var cx=Math.floor(x/16),cz=Math.floor(z/16);
  rebuildMesh(cx,cz);
  var lx=x-cx*16,lz=z-cz*16;
  if(lx===0) ensureChunkData(cx-1,cz);
  if(lx===15) ensureChunkData(cx+1,cz);
  if(lz===0) ensureChunkData(cx,cz-1);
  if(lz===15) ensureChunkData(cx,cz+1);
}
```

World update:

```js
function updateWorld(){
  var pcx=Math.floor(camera.position.x/16),pcz=Math.floor(camera.position.z/16);
  var gen=0;
  for(var dz=-5;dz<=5;dz++){
    for(var dx=-5;dx<=5;dx++){
      if(gen>=4) break;
      if(Math.abs(dx)>5||Math.abs(dz)>5) continue;
      var cx=pcx+dx,cz=pcz+dz;
      if(!chunkMap.has(cx+","+cz)){
        chunkMap.set(cx+","+cz,{data:generateChunkData(cx,cz),mesh:null,geom:null});
        gen++;
      }
    }
  }
  var mes=0;
  for(var dz2=-4;dz2<=4;dz2++){
    for(var dx2=-4;dx2<=4;dx2++){
      if(mes>=2) break;
      if(Math.abs(dx2)>4||Math.abs(dz2)>4) continue;
      var mx=pcx+dx2,mz=pcz+dz2;
      var ee=chunkMap.get(mx+","+mz);
      if(!ee||ee.mesh) continue;
      if(chunkMap.get((mx+1)+","+mz)&&chunkMap.get((mx-1)+","+mz)&&
         chunkMap.get(mx+","+(mz+1))&&chunkMap.get(mx+","+(mz-1))){
        buildChunkMesh(mx,mz);
        mes++;
      }
    }
  }
  for(var kv of chunkMap){
    var k=kv[0], en=kv[1];
    var pp=k.split(",");
    var rcx=+pp[0],rcz=+pp[1];
    if(Math.abs(rcx-pcx)>7||Math.abs(rcz-pcz)>7){
      if(en.mesh){
        scene.remove(en.mesh);
        if(en.geom) en.geom.dispose();
        var ci=chunkMeshList.indexOf(en.mesh);
        if(ci>=0) chunkMeshList.splice(ci,1);
      }
      chunkMap.delete(k);
    }
  }
}
```

Note: `for (var kv of chunkMap)` — kv is [key,value]. Good. Deleting current entry during iteration is safe.

Player physics:

```js
var EYE=1.62, SPEED=5.5, GRAVITY=25, JUMP=8.5;
var yaw=0, pitch=0, vy=0, onGround=false;
var keys={};
function collides(px,feet,pz){
  var hw=0.3,h=1.8,E=1e-3;
  var minX=Math.floor(px-hw),maxX=Math.floor(px+hw);
  var minY=Math.floor(feet),maxY=Math.floor(feet+h-E);
  var minZ=Math.floor(pz-hw),maxZ=Math.floor(pz+hw);
  for(var x=minX;x<=maxX;x++)
    for(var y=minY;y<=maxY;y++)
      for(var z=minZ;z<=maxZ;z++)
        if(getBlock(x,y,z)!==0) return true;
  return false;
}
function updatePlayer(dt){
  var fx=-Math.sin(yaw), fz=-Math.cos(yaw);
  var rx=Math.cos(yaw), ry=-Math.sin(yaw);
  var mx=0,mz=0;
  if(keys['w']){mx+=fx;mz+=fz;}
  if(keys['s']){mx-=fx;mz-=fz;}
  if(keys['d']){mx+=rx;mz+=ry;}
  if(keys['a']){mx-=rx;mz-=ry;}
  var len=Math.hypot(mx,mz);
  if(len>0){mx/=len;mz/=len;}
  var px=camera.position.x,pz=camera.position.z, feet=camera.position.y-EYE;
  var nx=px+mx*SPEED*dt;
  if(!collides(nx,feet,pz)) camera.position.x=nx;
  var nz=pz+mz*SPEED*dt;
  if(!collides(camera.position.x,feet,nz)) camera.position.z=nz;
  vy-=GRAVITY*dt;
  if(keys[' ']&&onGround){vy=JUMP;onGround=false;}
  if(vy<-50) vy=-50;
  var ny=feet+vy*dt;
  if(collides(camera.position.x,ny,camera.position.z)){
    if(vy<0){
      var s=ny;
      for(var i=0;i<24&&collides(camera.position.x,s,camera.position.z);i++) s+=0.1;
      camera.position.y=s+EYE; onGround=true; vy=0;
    } else { vy=0; }
  } else {
    camera.position.y=ny+EYE; onGround=false;
  }
  if(camera.position.y<-20){
    var sh=terrainHeightAt(8,8)+2;
    while(getBlock(8,sh,8)!==0 && sh<80) sh++;
    camera.position.set(8,sh+0.5,8); vy=0; onGround=true;
  }
}
function terrainHeightAt(x,z){ return columnHeight(Math.round(x),Math.round(z)); }
```

Raycast/target:

```js
var raycaster=new THREE.Raycaster();
var hitPoint=new THREE.Vector3(), hitNormal=new THREE.Vector3();
var hasTarget=false;
function updateTarget(){
  raycaster.set(camera.position, new THREE.Vector3(-Math.sin(yaw)*Math.cos(pitch), Math.sin(pitch), -Math.cos(yaw)*Math.cos(pitch)));
  raycaster.far=6;
  var hs=raycaster.intersectObjects(chunkMeshList,false);
  if(hs.length>0){
    hitPoint.copy(hs[0].point);
    hitNormal.copy(hs[0].face.normal);
    hasTarget=true;
  } else { hasTarget=false; }
}
```

Break/place:

```js
var selectedBlock=1;
function breakBlock(){
  if(!hasTarget) return;
  var x=Math.floor(hitPoint.x-hitNormal.x*0.5);
  var y=Math.floor(hitPoint.y-hitNormal.y*0.5);
  var z=Math.floor(hitPoint.z-hitNormal.z*0.5);
  if(y===0) return;
  setBlock(x,y,z,0);
  rebuildChunkAt(x,y,z);
}
function placeBlock(){
  if(!hasTarget) return;
  var x=Math.floor(hitPoint.x+hitNormal.x*0.5);
  var y=Math.floor(hitPoint.y+hitNormal.y*0.5);
  var z=Math.floor(hitPoint.z+hitNormal.z*0.5);
  if(getBlock(x,y,z)!==0) return;
  var feet=camera.position.y-EYE, hw=0.32,h=1.8;
  if(x+1>camera.position.x-hw && x<camera.position.x+hw &&
     y+1>feet && y<feet+h &&
     z+1>camera.position.z-hw && z<camera.position.z+hw) return;
  setBlock(x,y,z,selectedBlock);
  rebuildChunkAt(x,y,z);
}
```

Setup scene, camera, lights, outline, water, clouds, hotbar, input, loop.

```js
var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);
var camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order="YXZ";
var renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth/window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
document.body.appendChild(renderer.domElement);
var canvas=renderer.domElement;
scene.add(new THREE.AmbientLight(0xffffff,0.65));
var sun=new THREE.DirectionalLight(0xffffff,0.8);
sun.direction.set(0.5,1,0.3).normalize();
scene.add(sun);

// outline
var outline=new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01,1.01,1.01)),
  new THREE.LineBasicMaterial({color:0x000000})
);
outline.visible=false;
scene.add(outline);

// water
var water=new THREE.Mesh(new THREE.PlaneGeometry(200,200),
  new THREE.MeshLambertMaterial({color:0x3388ff,transparent:true,opacity:0.6,depthWrite:false}));
water.rotation.x=-Math.PI/2;
water.position.y=14.3;
scene.add(water);

// clouds
var clouds=[];
for(var i=0;i<25;i++){
  var cw=6+(i%4)*3, cd=6+(i%3)*2;
  var cm=new THREE.Mesh(new THREE.BoxGeometry(cw,1.5,cd),
    new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.9,depthWrite:false}));
  cm.userData={rx:((i*131.7)%120)-60, rz:((i*217.3)%120)-60, speed:2+(i%4)*0.5, t:0};
  cm.position.set(0,92,0);
  scene.add(cm);
  clouds.push(cm);
}

// hotbar
var HOT=[0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
var hotbarEl=document.getElementById('hotbar');
for(var j=0;j<7;j++){
  var s=document.createElement('div');
  s.className='slot';
  s.style.background='#'+HOT[j].toString(16).padStart(6,'0');
  s.innerHTML='<span class="num">'+(j+1)+'</span>';
  hotbarEl.appendChild(s);
}
function updateHotbar(){
  var ch=hotbarEl.children;
  for(var k=0;k<7;k++) ch[k].classList.toggle('sel', k===selectedBlock-1);
}
updateHotbar();

// spawn
var sh=terrainHeightAt(8,8)+2;
while(getBlock(8,sh,8)!==0 && sh<80) sh++;
camera.position.set(8,sh+0.5,8);

// input
var pointerLocked=false;
var overlay=document.getElementById('overlay');
overlay.addEventListener('click', function(){ canvas.requestPointerLock(); });
document.addEventListener('pointerlockchange', function(){
  pointerLocked=(document.pointerLockElement===canvas);
  overlay.style.display=pointerLocked?'none':'flex';
});
document.addEventListener('mousemove', function(e){
  if(!pointerLocked) return;
  yaw-=e.movementX*0.002;
  pitch-=e.movementY*0.002;
  if(pitch>Math.PI/2-0.01) pitch=Math.PI/2-0.01;
  if(pitch<-Math.PI/2+0.01) pitch=-Math.PI/2+0.01;
});
document.addEventListener('mousedown', function(e){
  if(!pointerLocked) return;
  if(e.button===0) breakBlock();
  else if(e.button===2) placeBlock();
});
document.addEventListener('keydown', function(e){
  var k=e.key.toLowerCase();
  keys[k]=true;
  if(e.key.length===1 && e.key>='1' && e.key<='7'){ selectedBlock=parseInt(e.key,10); updateHotbar(); }
  if(k===' '||e.key==='ArrowUp'||e.key==='ArrowDown'||e.key==='ArrowLeft'||e.key==='ArrowRight') e.preventDefault();
});
document.addEventListener('keyup', function(e){ keys[e.key.toLowerCase()]=false; });
document.addEventListener('wheel', function(e){
  if(!pointerLocked) return;
  selectedBlock += e.deltaY>0?1:-1;
  if(selectedBlock<1) selectedBlock=7;
  if(selectedBlock>7) selectedBlock=1;
  updateHotbar();
},{passive:true});
document.addEventListener('contextmenu', function(e){ e.preventDefault(); });

// initial world
for(var gz=-3;gz<=3;gz++){
  for(var gx=-3;gx<=3;gx++){
    ensureChunkData(gx,gz);
  }
}
for(var mz=-2;mz<=2;mz++){
  for(var mx2=-2;mx2<=2;mx2++){
    if(chunkMap.get((mx2+1)+","+mz)&&chunkMap.get((mx2-1)+","+mz)&&
       chunkMap.get(mx2+","+(mz+1))&&chunkMap.get(mx2+","+(mz-1))){
      buildChunkMesh(mx2,mz);
    }
  }
}

// loop
var last=performance.now();
function animate(){
  requestAnimationFrame(animate);
  var now=performance.now();
  var dt=(now-last)/1000; last=now;
  if(dt>0.05) dt=0.05;
  if(pointerLocked) updatePlayer(dt);
  updateWorld();
  updateTarget();
  if(hasTarget){
    var bx=Math.floor(hitPoint.x-hitNormal.x*0.5);
    var by=Math.floor(hitPoint.y-hitNormal.y*0.5);
    var bz=Math.floor(hitPoint.z-hitNormal.z*0.5);
    outline.position.set(bx+0.5,by+0.5,bz+0.5);
    outline.visible=true;
  } else { outline.visible=false; }
  for(var c=0;c<clouds.length;c++){
    var cl=clouds[c], u=cl.userData;
    u.t+=dt;
    var lx=u.rx+u.speed*u.t;
    lx=((lx+60)%120+120)%120-60;
    var lz2=u.rz;
    lz2=((lz2+60)%120+120)%120-60;
    cl.position.x=camera.position.x+lx;
    cl.position.z=camera.position.z+lz2;
  }
  water.position.x=camera.position.x;
  water.position.z=camera.position.z;
  renderer.render(scene,camera);
}
animate();

window.addEventListener('resize', function(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth>window.innerHeight?window.innerWidth:1, window.innerHeight);
});
})();
```

Wait, the resize setSize with weird condition—just use window.innerWidth/innerHeight. Let me fix:
```js
renderer.setSize(window.innerWidth, window.innerHeight);
```

Now, a concern: computeBoundingSphere on empty geometry. Let me guard in buildChunkMesh:
```js
if(pos.length>0) geom.computeBoundingSphere();
```

Also, an empty chunk (all air) would create an empty mesh in chunkMeshList. That's fine but adds to raycast list. Minor. Could skip creating mesh if pos.length===0. Let me skip mesh creation if no faces, to save memory. Actually if pos.length===0, don't add mesh. Let me adjust:

```js
if(pos.length>0){
  ... set attributes, setIndex, computeBoundingSphere
  if(!e.mesh){ e.mesh=new THREE.Mesh(geom,blockMaterial); scene.add(e.mesh); chunkMeshList.push(e.mesh); }
  else { /* rebuild geom */ }
}
```

But if a chunk had a mesh and becomes empty (after breaking all blocks), we should remove it. Hmm. Edge case. Let me handle: if pos.length===0 and e.mesh exists, remove it. Otherwise create/reuse.

Let me restructure buildChunkMesh:
```js
if(pos.length===0){
  if(e.mesh){ scene.remove(e.mesh); var ci=chunkMeshList.indexOf(e.mesh); if(ci>=0) chunkMeshList.splice(ci,1); if(e.geom) e.geom.dispose(); e.mesh=null; e.geom=null; }
  return;
}
... set attributes ...
if(!e.mesh){ e.mesh=new THREE.Mesh(geom,blockMaterial); e.mesh.frustumCulled=false; scene.add(e.mesh); chunkMeshList.push(e.mesh); }
```
Reuse geom (e.geom) — set e.geom=geom when first created.

This handles empty chunks. Good.

Now let me reconsider: when we break a block, the chunk still has other blocks, so pos.length>0, we rebuild. Good. When we clear an entire small chunk (unlikely), it removes. Fine.

Let me also double check: the initial meshing loop uses buildChunkMesh which now may skip empty chunks. Good.

Let me reconsider performance of intersectObjects with many meshes (~25-50). Each raycast does a ray-vs-bounds test per mesh. With frustumCulled=false but bounding box tests still happen. 50 meshes is fine.

Now, potential issue: the raycaster intersectObjects uses each mesh's bounding volume. Since we set frustumCulled=false but bounding box is still used for ray intersection (computeBoundingBox). We called computeBoundingSphere; raycaster uses boundingBox. Let me call computeBoundingBox too, or it auto-computes. THREE auto-computes boundingBox lazily if null. Actually Raycaster uses geometry.boundingBox; if null it computes from positions. So fine. But to be safe, call geom.computeBoundingBox(). Let me add it.

Now let me reconsider the collision when spawning: at spawn, onGround=false, vy=0. First frame gravity pulls down. Player falls onto terrain. Good.

Let me reconsider: camera.position.y is eye height. feet = y - 1.62. When standing on surface at height H, feet should be ~H (top of surface block). Player eye at H+1.62. Spawn at sh+0.5 where sh is surface height (first non-air from above? no—sh starts at terrainHeightAt+2 and decrements? Actually I do sh=terrainHeightAt+2 then `while(getBlock(8,sh,8)!==0 && sh<80) sh++;` This INCREMENTS sh until empty. That's wrong! I want to find the surface from below. Let me reconsider.

terrainHeightAt(8,8) gives H (surface height). Spawn at H+2 which is above surface. That's fine—player spawns above and falls onto surface. So I don't need the while loop incrementing. The while loop I wrote increments sh while block is solid, which from H+2 (solid? H is surface, H+1, H+2 are air usually) → immediately stops at H+2. So camera spawns at H+2+0.5 = H+2.5. Falls to surface. Fine. Actually simpler: camera.position.y = terrainHeightAt(8,8)+2. Let me just do that. The while loop is unnecessary and potentially harmful (increments into sky if H+2 happened to be solid, unlikely). Let me remove the while and just set H+2.

Actually, could H+1 or H+2 be solid? Only if a tree's leaves/trunk extended that high at column (8,8). Rare. If so, spawning inside. Let me do a small descent: start at H+3, decrement while solid to find clear spot above ground. 
```js
var sy=terrainHeightAt(8,8)+3;
while(sy>0 && getBlock(8,sy,8)!==0) sy--;
camera.position.set(8, sy+1, 8);
```
This finds the first empty cell going down from H+3, then places player just above it. Good. Handles trees. Let me use this.

Let me finalize that.

Now let me reconsider the "far 400" — spec says far 400. Good. Fog 40-110. Good.

Let me reconsider directional light: set direction then normalize. Good.

Now, I realize there might be an issue with MeshLambertMaterial and vertexColors: need material.vertexColors=true (set). Yes.

Also, lambert needs normals (we provide). Good.

Let me also ensure the material is shared (one instance) — yes, blockMaterial used for all meshes. Good.

Let me also double-check the FACE winding once more for at least +Y (top) since snow/grass top should be brightest. Our +Y face n=[0,1,0] light=1.0. Good.

Now, one more: the spec says "Keep the mesh at the origin." Our chunk mesh vertices are world coords but the mesh object itself is at origin (position 0,0,0) with no rotation. Yes, we create mesh without setting position, so it's at origin, vertices in world space. Good. That's what "keep the mesh at the origin" means.

Now let me reconsider the raycast hit.normal for our merged geometry. When THREE raycasts a BufferGeometry, it finds the triangle and returns face.normal from the normal attribute (per-vertex normals, interpolated? Actually for BufferGeometry, face.normal is the normal of that triangle from the attribute). Since all 4 vertices of a face share the same normal, it's exact. Good.

But wait—there's a subtlety: THREE's intersectObjects for BufferGeometry returns intersections with face.normal being the triangle's normal. Good. And point is world (mesh at origin). Good.

Let me also make sure we reset raycaster per frame (set position/dir). Yes.

Alright. Let me also reconsider: after breaking/placing, we should update the outline immediately? It updates next frame in render. Fine.

Let me also handle the scenario where pointer is locked but we're rendering—overlay hidden. Good.

Let me reconsider the initial meshing: I generate radius 3 (7x7=49 chunks) then mesh radius 2 (5x5=25) that have all neighbors (they do, since radius 3 generated). Actually radius 2 chunks have neighbors within radius 3, all generated. So all 25 mesh. But some may be empty (all air) → skipped. Good.

Wait, but radius 2 chunk at (2,2) has neighbor (3,2) which is in radius 3 (generated). Good. So all 25 have data neighbors → mesh attempted. Good.

Now the loop's generation (radius 5, 4/frame) and meshing (radius 4, 2/frame) will stream forward. Good.

Let me reconsider: is radius 5 generation too aggressive? 4 per frame is the cap, so fine.

Let me also double check the removal: chunks beyond 7 removed. So world cache bounded to radius 7. Good.

Now, let me reconsider a subtle bug: in updateWorld, the generation loop `for dz, for dx, if(gen>=4) break;` — the break exits inner dx loop when gen reaches 4, but then outer dz continues and inner dx runs again but immediately breaks (gen>=4). That wastes iterations but fine. Actually it breaks inner loop each dz iteration. OK.

Let me also ensure we don't generate the same chunk twice: `if(!chunkMap.has(...))`. Good.

Alright, I'm fairly confident. Let me also add a small note: requestPointerLock might need to be called on the canvas which is renderer.domElement. Yes.

Let me also make sure the overlay click works: overlay is on top (z-index 20), covers canvas. Clicking it triggers overlay click handler → requestPointerLock. After lock, overlay hidden. Subsequent clicks hit canvas (locked). Good.

Let me also prevent default on canvas for drag etc. Not necessary.

Let me also consider mobile—not required.

Let me write the final file now, carefully.

Actually, I realize the resize handler has a leftover weird ternary; fix to plain.

Also, I should double check `.padStart` is available—yes, ES2017, all modern browsers. Good.

Let me also reconsider: `e.key.length===1 && e.key>='1' && e.key<='7'` — for number keys '1'..'7'. Good. But Shift+1 gives '!' etc. Ignore. Fine.

Also wheel: passive listener to avoid scroll prevention issues. Good.

Let me also make sure keys object persists. Yes.

Now, let me reconsider gravity/jump feel: gravity 25, jump 8.5. Time to peak: 8.5/25=0.34s, height=8.5*0.34/2≈1.44m. Reasonable. Movement 5.5 m/s. Good.

Let me also double-check collision uses feet correctly. When standing on surface at height H (say 24), feet≈24, camera.y≈25.62. collides checks blocks y from floor(25.62-1.62)=24 to floor(25.62-1.62+1.8-0.001)=floor(25.8)=25. So checks y=24,25. Block at 24 (surface) solid → collision prevents moving down. Good. Moving up into air (y=25 air) no collision. Good.

When jumping, vy positive, feet increases, no collision until apex then falls. Good.

Walking off a cliff: vy negative, falls. Good.

Now, let me also reconsider: when player walks into a wall, horizontal collision stops penetration. Good.

Alright, finalize.

Let me reconsider the outline visibility when hasTarget but target block is out of build range—fine, just shows at that position.

Also, the outline uses EdgesGeometry of a slightly oversized box (1.01) to avoid z-fighting with block faces. Good.

Let me write the final code, making sure all functions are defined before use (JS hoists function declarations, so order is flexible, but let me keep logical order).

Let me also reconsider: `for (var kv of chunkMap)` — using var in for-of is fine. kv is [key,val]. Good.

Let me produce final.

Actually, let me reconsider computeBoundingBox call. I'll add geom.computeBoundingBox() after setIndex. And guard computeBoundingSphere for empty.

Let me also make sure that when reusing geom (e.geom exists), we still set attributes fresh each rebuild. Yes we always set attributes. Good.

Let me write final file now.

Let me reconsider the cloud count and positions: 25 clouds, each with random-ish offsets via deterministic formula. Good. They wrap around player. Good.

Also water opacity 0.6, color blue. Good.

I think it's complete. Let me write it out fully and cleanly.

Let me reconsider one thing about the initial spawn descent: 
```js
var sy=terrainHeightAt(8,8)+3;
while(sy>0 && getBlock(8,sy,8)!==0) sy--;
camera.position.set(8, sy+1, 8);
```
If terrainHeightAt(8,8)=H, sy=H+3. If H+3 solid (tree leaves), decrement until empty. Then place at sy+1. Good. If nothing solid above, sy stays H+3, place at H+4. Fine.

Edge: if entire column is solid (shouldn't be, surface is air-ish or top block), sy goes to 0, place at 1. Unlikely. Fine.

Now, final code. Let me write it.

Let me make sure I include `use strict` and wrap in IIFE to avoid polluting global (except THREE is global). Good.

Let me also double-check that I reference `scene` before defining it in buildChunkMesh — since these are function declarations hoisted, and they're called after scene is defined, it's fine. But blockMaterial is referenced in buildChunkMesh; it's defined before the loop calls. Good. Actually buildChunkMesh references scene, blockMaterial, chunkMeshList, chunkMap — all defined as vars/functions before the initial meshing loop runs. Good.

Wait, function declarations are hoisted, but `var blockMaterial=...` is initialized at execution point. buildChunkMesh is only CALLED after all var initializations (during initial meshing loop which is after all definitions). So fine.

Let me finalize.

Let me reconsider whether to use `THREE.Float32BufferAttribute` — in r128 it exists. Yes.

Also `THREE.EdgesGeometry`, `THREE.LineSegments`, `THREE.LineBasicMaterial` — all in r128. Good.

`THREE.MeshLambertMaterial`, `THREE.PerspectiveCamera`, `THREE.WebGLRenderer`, `THREE.AmbientLight`, `THREE.DirectionalLight`, `THREE.Fog`, `THREE.Scene`, `THREE.Vector3`, `THREE.Raycaster`, `THREE.BoxGeometry`, `THREE.PlaneGeometry`, `THREE.Mesh` — all in r128. Good.

Alright, writing final.

Let me reconsider the resize: just setSize(innerWidth, innerHeight).

Final code below. Let me be thorough and complete.

Actually, let me reconsider the meshing neighbor check using chunkMap.get returns the entry object (truthy) or undefined. `chunkMap.get(...) && ...` evaluates to the object (truthy) or undefined (falsy). In boolean context fine. Good.

Let me write it out.

Also, I want to double check: after building initial meshes, the first animate() frame calls updateWorld which generates more. Fine.

Let me also ensure requestPointerLock is called only on overlay click (user gesture). Good.

Let me also add focus handling—not needed.

Writing now. I'll produce the single code block.

Let me reconsider: should the crosshair be visible over the overlay? Overlay z-index 20 > crosshair 10, so overlay covers crosshair. That's fine (player sees overlay). Once playing, overlay hidden, crosshair visible. Good.

Also hotbar z-index 10, overlay 20 covers it during overlay. Fine.

Final.

Let me write the complete file carefully now, ensuring no syntax errors.

I'll double-check the noise3 function once more and the fractal.

Also, I realize I should double check that `Math.imul` exists in the browsers—yes, ES2015, Chrome and Firefox support it. Good.

Let me write.

One more: the spec says "clamp pitch" — I clamp to ±(π/2 - 0.01). Good.

Also sensitivity ~0.002 — I use 0.002. Good.

Alright, final answer.

Let me also reconsider: when the pointer is not locked, we still call updateTarget and render outline? The outline would show based on last raycast. Minor. But when not locked, we might not want outline. Let me only show outline when pointerLocked. Actually it's fine either way; but to be clean, show outline only when locked. Let me gate: `if(pointerLocked && hasTarget)`. Hmm but during play we want it. When overlay shows, pointer not locked, hide outline. Let me do: outline.visible = pointerLocked && hasTarget. Good.

Let me finalize.

Also, I'll make sure to request animation frame and render continuously even when not locked (so overlay has... well overlay is opaque DOM, no need to render behind, but rendering is cheap). Keep rendering.

Final code:
</think>

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MC</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:hidden;background:#87ceeb;font-family:sans-serif}
canvas{display:block}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:20px;height:20px;pointer-events:none;z-index:10}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:rgba(0,0,0,.7)}
#crosshair::before{top:50%;left:0;width:100%;height:2px;transform:translateY(-50%)}
#crosshair::after{left:50%;top:0;height:100%;width:2px;transform:translateX(-50%)}
#hotbar{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);display:flex;gap:4px;padding:6px;background:rgba(0,0,0,.55);border-radius:6px;z-index:10;pointer-events:none}
.slot{width:46px;height:46px;border:2px solid rgba(255,255,255,.35);border-radius:4px;position:relative;display:flex;align-items:center;justify-content:center;background:#000}
.slot .num{position:absolute;top:1px;left:3px;color:#fff;font-size:12px;font-weight:bold;text-shadow:1px 1px 2px #000}
.slot.sel{border-color:#fff;box-shadow:0 0 8px #fff}
#overlay{position:fixed;inset:0;background:rgba(0,0,0,.78);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:20;text-align:center}
#overlay h1{font-size:52px;letter-spacing:3px;margin-bottom:22px;text-shadow:2px 2px 0 #000}
#overlay ul{text-align:left;font-size:16px;line-height:1.9;margin-bottom:26px;list-style:none}
#overlay li::before{content:'» '}
#overlay .play{font-size:22px;padding:12px 30px;border:2px solid #fff;border-radius:8px;cursor:pointer;background:rgba(255,255,255,.08)}
#overlay .play:hover{background:rgba(255,255,255,.2)}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MC</h1>
  <ul>
    <li>WASD — move</li>
    <li>Mouse — look around</li>
    <li>Space — jump</li>
    <li>Left click — break block</li>
    <li>Right click — place block</li>
    <li>Keys 1–7 or wheel — select block</li>
  </ul>
  <div class="play">Click to play</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

/* ---------------- noise ---------------- */
function smoothstep(t){return t*t*(3-2*t);}
function lerp(a,b,t){return a+(b-a)*t;}
function hash(ix,iy){
  var h=(ix*374761393+iy*668265263)|0;
  h=Math.imul(h^(h>>>13),2246822507);
  h=Math.imul(h^(h>>>16),3266489909);
  return (h>>>0)/4294967296;
}
function hash3(ix,iy,iz){
  var h=(ix*374761393+iy*668265263+iz*1523486461)|0;
  h=Math.imul(h^(h>>>13),2246822507);
  h=Math.imul(h^(h>>>16),3266489909);
  return (h>>>0)/4294967296;
}
function noise2(x,y){
  var xi=Math.floor(x),yi=Math.floor(y);
  var xf=x-xi,yf=y-yi;
  var u=smoothstep(xf),v=smoothstep(yf);
  var a=hash(xi,yi),b=hash(xi+1,yi),c=hash(xi,yi+1),d=hash(xi+1,yi+1);
  return lerp(lerp(a,b,u),lerp(c,d,u),v);
}
function fractal2(x,y,o){
  var amp=0.5,freq=1,sum=0,norm=0;
  for(var i=0;i<o;i++){sum+=amp*noise2(x*freq,y*freq);norm+=amp;amp*=0.5;freq*=2;}
  return sum/norm;
}
function noise3(x,y,z){
  var xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z);
  var xf=x-xi,yf=y-yi,zf=z-zi;
  var u=smoothstep(xf),v=smoothstep(yf),w=smoothstep(zf);
  var c00=hash3(xi,yi,zi),c10=hash3(xi+1,yi,zi),c01=hash3(xi,yi+1,zi),c11=hash3(xi+1,yi+1,zi);
  var x0=lerp(c00,c10,u),x1=lerp(c01,c11,u);
  var y0=lerp(x0,x1,v),y1=lerp(x01||0,x11||0,w);
  var c00b=hash3(xi,yi,zi+1),c10b=hash3(xi+1,yi,zi+1),c01b=hash3(xi,yi+1,zi+1),c11b=hash3(xi+1,yi+1,zi+1);
  var xb0=lerp(c00b,c10b,u),xb1=lerp(c01b,c11b,u);
  var yb0=lerp(x0,xb0,v),yb1=lerp(x1,xb1,v);
  return lerp(yb0,yb1,w);
}

/* ---------------- terrain ---------------- */
function columnHeight(cx,cz){
  var m=fractal2(cx*0.004,cz*0.004,4);
  var h=fractal2(cx*0.02,cz*0.02,4);
  return Math.floor(5 + m*m*58 + h*10);
}
function blockType(y,H){
  if(y<H-3) return 3;
  if(y<=H-1){
    if(H<=16) return 4;
    if(H>=37) return 3;
    return 2;
  }
  if(H>=46) return 7;
  if(H>=37) return 3;
  if(H<=16) return 4;
  return 1;
}
function generateChunkData(cx,cz){
  var data=new Uint8Array(16*16*80);
  var x0=cx*16,z0=cz*16;
  for(var lz=0;lz<16;lz++){
    for(var lx=0;lx<16;lx++){
      var wx=x0+lx,wz=z0+lz;
      var H=columnHeight(wx,wz);
      for(var y=0;y<80;y++){
        var id;
        if(y===0) id=3;
        else if(y>=3 && y<=H-2){
          id=(noise3(wx*0.09,y*0.09,wz*0.09)>0.67)?0:blockType(y,H);
        } else {
          id=blockType(y,H);
        }
        data[(y*16+lz)*16+lx]=id;
      }
      if(blockType(H,H)===1 && H>=4 && H<=71 && lx>=2 && lx<=13 && lz>=2 && lz<=13){
        if(hash(wx,wz)<0.02){
          for(var t=1;t<=4;t++){var ty=H+t;if(ty<80)data[(ty*16+lz)*16+lx]=5;}
          var specs=[{dy:5,r:2},{dy:6,r:2},{dy:7,r:1},{dy:8,r:0}];
          for(var s=0;s<specs.length;s++){
            var sp=specs[s];
            for(var dx=-sp.r;dx<=sp.r;dx++){
              for(var dz=-sp.r;dz<=sp.r;dz++){
                var ly=H+sp.dy,lx2=lx+dx,lz2=lz+dz;
                if(lx2<0||lx2>=16||lz2<0||lz2>=16||ly>=80)continue;
                var li=(ly*16+lz2)*16+lx2;
                if(data[li]===0)data[li]=6;
              }
            }
          }
        }
      }
    }
  }
  return data;
}

/* ---------------- chunk storage / access ---------------- */
var chunkMap=new Map();
var chunkMeshList=[];
var blockMaterial=new THREE.MeshLambertMaterial({vertexColors:true});

function getBlock(x,y,z){
  if(y<0||y>=80)return 0;
  var cx=Math.floor(x/16),cz=Math.floor(z/16);
  var e=chunkMap.get(cx+","+cz);
  if(!e||!e.data)return 0;
  return e.data[(y*16+(z-cz*16))*16+(x-cx*16)];
}
function setBlock(x,y,z,id){
  if(y<0||y>=80)return;
  var cx=Math.floor(x/16),cz=Math.floor(z/16);
  var e=chunkMap.get(cx+","+cz);
  if(!e||!e.data)return;
  e.data[(y*16+(z-cz*16))*16+(x-cx*16)]=id;
}

/* ---------------- meshing ---------------- */
var FACES=[
  {n:[1,0,0],v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]]},
  {n:[-1,0,0],v:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]},
  {n:[0,1,0],v:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]},
  {n:[0,-1,0],v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
  {n:[0,0,1],v:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]},
  {n:[0,0,-1],v:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]]}
];
var BLOCK_COLORS=[0,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];

function buildChunkMesh(cx,cz){
  var e=chunkMap.get(cx+","+cz);
  if(!e||!e.data)return;
  var pos=[],nor=[],col=[],idx=[];
  var vi=0;
  var x0=cx*16,z0=cz*16;
  for(var lz=0;lz<16;lz++){
    for(var lx=0;lx<16;lx++){
      for(var y=0;y<80;y++){
        var id=e.data[(y*16+lz)*16+lx];
        if(id===0)continue;
        var wx=x0+lx,wz=z0+lz;
        var bc=BLOCK_COLORS[id];
        var cr=((bc>>16)&255)/255, cg=((bc>>8)&255)/255, cb=(bc&255)/255;
        for(var f=0;f<6;f++){
          var face=FACES[f];
          if(getBlock(wx+face.n[0],y+face.n[1],wz+face.n[2])!==0)continue;
          var light=(f===2)?1.0:(f===3)?0.55:0.8;
          for(var k=0;k<4;k++){
            var vp=face.v[k];
            pos.push(wx+vp[0],y+vp[1],wz+vp[2]);
            nor.push(face.n[0],face.n[1],face.n[2]);
            col.push(cr*light,cg*light,cb*light);
          }
          idx.push(vi,vi+1,vi+2,vi,vi+2,vi+3);
          vi+=4;
        }
      }
    }
  }
  if(pos.length===0){
    if(e.mesh){
      scene.remove(e.mesh);
      var ci=chunkMeshList.indexOf(e.mesh);
      if(ci>=0)chunkMeshList.splice(ci,1);
      if(e.geom)e.geom.dispose();
      e.mesh=null;e.geom=null;
    }
    return;
  }
  var geom=e.geom||(e.geom=new THREE.BufferGeometry());
  geom.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  geom.setAttribute('normal',new THREE.Float32BufferAttribute(nor,3));
  geom.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  geom.setIndex(idx);
  geom.computeBoundingSphere();
  geom.computeBoundingBox();
  if(!e.mesh){
    e.mesh=new THREE.Mesh(geom,blockMaterial);
    e.mesh.frustumCulled=false;
    scene.add(e.mesh);
    chunkMeshList.push(e.mesh);
  }
}

function ensureChunkData(cx,cz){
  var key=cx+","+cz;
  if(!chunkMap.has(key))chunkMap.set(key,{data:generateChunkData(cx,cz),mesh:null,geom:null});
}
function rebuildMesh(cx,cz){
  var e=chunkMap.get(cx+","+cz);
  if(e&&e.data)buildChunkMesh(cx,cz);
}
function rebuildChunkAt(x,y,z){
  var cx=Math.floor(x/16),cz=Math.floor(z/16);
  rebuildMesh(cx,cz);
  var lx=x-cx*16,lz=z-cz*16;
  if(lx===0)ensureChunkData(cx-1,cz);
  if(lx===15)ensureChunkData(cx+1,cz);
  if(lz===0)ensureChunkData(cx,cz-1);
  if(lz===15)ensureChunkData(cx,cz+1);
}

function updateWorld(){
  var pcx=Math.floor(camera.position.x/16),pcz=Math.floor(camera.position.z/16);
  var gen=0;
  for(var dz=-5;dz<=5;dz++){
    for(var dx=-5;dx<=5;dx++){
      if(gen>=4)break;
      if(Math.abs(dx)>5||Math.abs(dz)>5)continue;
      var cx=pcx+dx,cz=pcz+dz;
      if(!chunkMap.has(cx+","+cz)){
        chunkMap.set(cx+","+cz,{data:generateChunkData(cx,cz),mesh:null,geom:null});
        gen++;
      }
    }
  }
  var mes=0;
  for(var dz2=-4;dz2<=4;dz2++){
    for(var dx2=-4;dx2<=4;dx2++){
      if(mes>=2)break;
      if(Math.abs(dx2)>4||Math.abs(dz2)>4)continue;
      var mx=pcx+dx2,mz=pcz+dz2;
      var ee=chunkMap.get(mx+","+mz);
      if(!ee||ee.mesh)continue;
      if(chunkMap.get((mx+1)+","+mz)&&chunkMap.get((mx-1)+","+mz)&&
         chunkMap.get(mx+","+(mz+1))&&chunkMap.get(mx+","+(mz-1))){
        buildChunkMesh(mx,mz);
        mes++;
      }
    }
  }
  for(var kv of chunkMap){
    var k=kv[0],en=kv[1];
    var pp=k.split(","),rcx=+pp[0],rcz=+pp[1];
    if(Math.abs(rcx-pcx)>7||Math.abs(rcz-pcz)>7){
      if(en.mesh){
        scene.remove(en.mesh);
        var ci2=chunkMeshList.indexOf(en.mesh);
        if(ci2>=0)chunkMeshList.splice(ci2,1);
        if(en.geom)en.geom.dispose();
      }
      chunkMap.delete(k);
    }
  }
}

/* ---------------- player ---------------- */
var EYE=1.62,SPEED=5.5,GRAVITY=25,JUMP=8.5;
var yaw=0,pitch=0,vy=0,onGround=false;
var keys={};
function collides(px,feet,pz){
  var hw=0.3,h=1.8,E=1e-3;
  var minX=Math.floor(px-hw),maxX=Math.floor(px+hw);
  var minY=Math.floor(feet),maxY=Math.floor(feet+h-E);
  var minZ=Math.floor(pz-hw),maxZ=Math.floor(pz+hw);
  for(var x=minX;x<=maxX;x++)
    for(var y=minY;y<=maxY;y++)
      for(var z=minZ;z<=maxZ;z++)
        if(getBlock(x,y,z)!==0)return true;
  return false;
}
function terrainHeightAt(x,z){return columnHeight(Math.round(x),Math.round(z));}
function updatePlayer(dt){
  var fx=-Math.sin(yaw),fz=-Math.cos(yaw);
  var rx=Math.cos(yaw),ry=-Math.sin(yaw);
  var mx=0,mz=0;
  if(keys['w']){mx+=fx;mz+=fz;}
  if(keys['s']){mx-=fx;mz-=fz;}
  if(keys['d']){mx+=rx;mz+=ry;}
  if(keys['a']){mx-=rx;mz-=ry;}
  var len=Math.hypot(mx,mz);
  if(len>0){mx/=len;mz/=len;}
  var px=camera.position.x,pz=camera.position.z,feet=camera.position.y-EYE;
  var nx=px+mx*SPEED*dt;
  if(!collides(nx,feet,pz))camera.position.x=nx;
  var nz=pz+mz*SPEED*dt;
  if(!collides(camera.position.x,feet,nz))camera.position.z=nz;
  vy-=GRAVITY*dt;
  if(keys[' ']&&onGround){vy=JUMP;onGround=false;}
  if(vy<-50)vy=-50;
  var ny=feet+vy*dt;
  if(collides(camera.position.x,ny,camera.position.z)){
    if(vy<0){
      var s=ny;
      for(var i=0;i<24&&collides(camera.position.x,s,camera.position.z);i++)s+=0.1;
      camera.position.y=s+EYE;onGround=true;vy=0;
    } else {vy=0;}
  } else {
    camera.position.y=ny+EYE;onGround=false;
  }
  if(camera.position.y<-20){
    var sh=terrainHeightAt(8,8)+3;
    while(sh>0&&getBlock(8,sh,8)!==0)sh--;
    camera.position.set(8,sh+1,8);vy=0;onGround=true;
  }
}

/* ---------------- targeting / editing ---------------- */
var raycaster=new THREE.Raycaster();
var hitPoint=new THREE.Vector3(),hitNormal=new THREE.Vector3();
var hasTarget=false;
function updateTarget(){
  raycaster.set(camera.position,new THREE.Vector3(-Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),-Math.cos(yaw)*Math.cos(pitch)));
  raycaster.far=6;
  var hs=raycaster.intersectObjects(chunkMeshList,false);
  if(hs.length>0){hitPoint.copy(hs[0].point);hitNormal.copy(hs[0].face.normal);hasTarget=true;}
  else hasTarget=false;
}
var selectedBlock=1;
function breakBlock(){
  if(!hasTarget)return;
  var x=Math.floor(hitPoint.x-hitNormal.x*0.5);
  var y=Math.floor(hitPoint.y-hitNormal.y*0.5);
  var z=Math.floor(hitPoint.z-hitNormal.z*0.5);
  if(y===0)return;
  setBlock(x,y,z,0);
  rebuildChunkAt(x,y,z);
}
function placeBlock(){
  if(!hasTarget)return;
  var x=Math.floor(hitPoint.x+hitNormal.x*0.5);
  var y=Math.floor(hitPoint.y+hitNormal.y*0.5);
  var z=Math.floor(hitPoint.z+hitNormal.z*0.5);
  if(getBlock(x,y,z)!==0)return;
  var feet=camera.position.y-EYE,hw=0.32,h=1.8;
  if(x+1>camera.position.x-hw&&x<camera.position.x+hw&&
     y+1>feet&&y<feet+h&&
     z+1>camera.position.z-hw&&z<camera.position.z+hw)return;
  setBlock(x,y,z,selectedBlock);
  rebuildChunkAt(x,y,z);
}

/* ---------------- scene setup ---------------- */
var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);
var camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order="YXZ";
var renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
document.body.appendChild(renderer.domElement);
var canvas=renderer.domElement;
scene.add(new THREE.AmbientLight(0xffffff,0.65));
var sun=new THREE.DirectionalLight(0xffffff,0.8);
sun.direction.set(0.5,1,0.3).normalize();
scene.add(sun);

var outline=new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01,1.01,1.01)),
  new THREE.LineBasicMaterial({color:0x000000})
);
outline.visible=false;
scene.add(outline);

var water=new THREE.Mesh(new THREE.PlaneGeometry(200,200),
  new THREE.MeshLambertMaterial({color:0x3388ff,transparent:true,opacity:0.6,depthWrite:false}));
water.rotation.x=-Math.PI/2;
water.position.y=14.3;
scene.add(water);

var clouds=[];
for(var i=0;i<25;i++){
  var cw=6+(i%4)*3,cd=6+(i%3)*2;
  var cm=new THREE.Mesh(new THREE.BoxGeometry(cw,1.5,cd),
    new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.9,depthWrite:false}));
  cm.userData={rx:((i*131.7)%120)-60,rz:((i*217.3)%120)-60,speed:2+(i%4)*0.5,t:0};
  cm.position.set(0,92,0);
  scene.add(cm);
  clouds.push(cm);
}

var HOT=[0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
var hotbarEl=document.getElementById('hotbar');
for(var j=0;j<7;j++){
  var s=document.createElement('div');
  s.className='slot';
  s.style.background='#'+HOT[j].toString(16).padStart(6,'0');
  s.innerHTML='<span class="num">'+(j+1)+'</span>';
  hotbarEl.appendChild(s);
}
function updateHotbar(){var ch=hotbarEl.children;for(var k=0;k<7;k++)ch[k].classList.toggle('sel',k===selectedBlock-1);}
updateHotbar();

var sy=terrainHeightAt(8,8)+3;
while(sy>0&&getBlock(8,sy,8)!==0)sy--;
camera.position.set(8,sy+1,8);

/* ---------------- input ---------------- */
var pointerLocked=false;
var overlay=document.getElementById('overlay');
overlay.addEventListener('click',function(){canvas.requestPointerLock();});
document.addEventListener('pointerlockchange',function(){
  pointerLocked=(document.pointerLockElement===canvas);
  overlay.style.display=pointerLocked?'none':'flex';
});
document.addEventListener('mousemove',function(e){
  if(!pointerLocked)return;
  yaw-=e.movementX*0.002;
  pitch-=e.movementY*0.002;
  if(pitch>Math.PI/2-0.01)pitch=Math.PI/2-0.01;
  if(pitch<-Math.PI/2+0.01)pitch=-Math.PI/2+0.01;
});
document.addEventListener('mousedown',function(e){
  if(!pointerLocked)return;
  if(e.button===0)breakBlock();
  else if(e.button===2)placeBlock();
});
document.addEventListener('keydown',function(e){
  var k=e.key.toLowerCase();
  keys[k]=true;
  if(e.key.length===1&&e.key>='1'&&e.key<='7'){selectedBlock=parseInt(e.key,10);updateHotbar();}
  if(k===' '||e.key==='ArrowUp'||e.key==='ArrowDown'||e.key==='ArrowLeft'||e.key==='ArrowRight')e.preventDefault();
});
document.addEventListener('keyup',function(e){keys[e.key.toLowerCase()]=false;});
document.addEventListener('wheel',function(e){
  if(!pointerLocked)return;
  selectedBlock+=e.deltaY>0?1:-1;
  if(selectedBlock<1)selectedBlock=7;
  if(selectedBlock>7)selectedBlock=1;
  updateHotbar();
},{passive:true});
document.addEventListener('contextmenu',function(e){e.preventDefault();});

/* ---------------- initial world ---------------- */
for(var gz=-3;gz<=3;gz++)for(var gx=-3;gx<=3;gx++)ensureChunkData(gx,gz);
for(var mz=-2;mz<=2;mz++)for(var mx2=-2;mx2<=2;mx2++){
  if(chunkMap.get((mx2+1)+","+mz)&&chunkMap.get((mx2-1)+","+mz)&&
     chunkMap.get(mx2+","+(mz+1))&&chunkMap.get(mx2+","+(mz-1)))buildChunkMesh(mx2,mz);
}

/* ---------------- loop ---------------- */
var last=performance.now();
function animate(){
  requestAnimationFrame(animate);
  var now=performance.now();
  var dt=(now-last)/1000;last=now;
  if(dt>0.05)dt=0.05;
  if(pointerLocked)updatePlayer(dt);
  updateWorld();
  updateTarget();
  if(pointerLocked&&hasTarget){
    var bx=Math.floor(hitPoint.x-hitNormal.x*0.5);
    var by=Math.floor(hitPoint.y-hitNormal.y*0.5);
    var bz=Math.floor(hitPoint.z-hitNormal.z*0.5);
    outline.position.set(bx+0.5,by+0.5,bz+0.5);
    outline.visible=true;
  } else outline.visible=false;
  for(var c=0;c<clouds.length;c++){
    var cl=clouds[c],u=cl.userData;
    u.t+=dt;
    var lx=u.rx+u.speed*u.t;
    lx=((lx+60)%120+120)%120-60;
    var lz2=u.rz;
    lz2=((lz2+60)%120+120)%120-60;
    cl.position.x=camera.position.x+lx;
    cl.position.z=camera.position.z+lz2;
  }
  water.position.x=camera.position.x;
  water.position.z=camera.position.z;
  renderer.render(scene,camera);
}
animate();

window.addEventListener('resize',function(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});
})();
</script>
</body>
</html>
```