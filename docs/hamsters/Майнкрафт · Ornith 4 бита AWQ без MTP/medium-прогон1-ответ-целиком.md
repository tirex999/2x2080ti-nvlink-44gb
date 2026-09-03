Let me carefully build this Minecraft-style voxel game in a single HTML file. I need to follow the spec precisely.

Let me break down the requirements:

1. **Single HTML file** `mc.html`
2. **Three.js r128** loaded via script tag from CDN (global THREE)
3. Works from disk (file://)
4. First-person voxel sandbox

Let me plan out the components:

### Blocks
- IDs: 0 air, 1 grass 0x4caf50, 2 dirt 0x795548, 3 stone 0x9e9e9e, 4 sand 0xe7d9a8, 5 wood 0x8d6e63, 6 leaves 0x2e7d32, 7 snow 0xffffff
- Unit cubes, vertex colors, ONE shared MeshLambertMaterial
- Fake lighting: multiply block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms

### Chunks & endless world
- Chunks 16x16 columns, 80 blocks high
- Global Map keyed "cx,cz" → {Uint8Array block IDs + mesh}
- Block helpers using chunk = floor(world/16), local = world − chunk*16, negative coords work
- Missing chunk or y outside 0-79 returns air
- Each frame: generate block data for chunks within 5 of player (max 4/frame)
- Build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2/frame)
- For chunks farther than 7, remove mesh, dispose geometry, delete entry

### Meshing
- ONE BufferGeometry per chunk
- Loop all non-air blocks, for each of 6 sides check neighbor with global read helper; if air, add face (2 triangles) to flat position/normal/color arrays
- World coords for vertices, mesh at origin
- Keep all chunk meshes in global array for raycasting
- Rebuild function for a chunk

### Terrain (deterministic)
- Value noise: integer hash 0-1 (prime multipliers, xor-shifts), smoothed 2D noise via bilinear + smoothstep, 4 octaves fractal, 3D version for caves
- Column height: m = fractal at coords*0.004, h = fractal at coords*0.02, H = floor(5 + m*m*58 + h*10)
- Column fill:
  - y 0 = unbreakable stone
  - below H−3 stone
  - the 3 layers under surface: dirt (sand if H ≤ 16, stone if H ≥ 37)
  - surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass
- Caves: y between 3 and H−2, if 3D noise at position*0.09 exceeds 0.67, set air
- Trees: on grass, when per-column hash < 0.02 and trunk fits: 4 wood up, leaves as 5x5 layer twice, then 3x3, then 1 on top (only into air)

### Player & controls
- PerspectiveCamera (fov 75, far 400), rotation order "YXZ" driven by yaw/pitch
- Clicking start overlay requests pointer lock
- Mouse look only while locked (sensitivity ~0.002, clamp pitch)
- Player box: half-width 0.3, height 1.8, eye 1.62
- Spawn above terrain at x=8, z=8
- Gravity 25/s, jump Space (velocity 8.5), WASD at 5.5 m/s relative to yaw
- Axis-separated collision against all non-air blocks (move per axis, revert on overlap; landing sets on-ground)
- Falling below y −20 teleports back to spawn

### Break & place
- CSS crosshair at screen center
- Each frame raycast from camera center (max distance 6) against chunk meshes
- From hit point p and face normal n: break target = floor(p − n*0.5), place cell = floor(p + n*0.5), per component
- Outline targeted block with black wireframe box
- Only while pointer locked: left click sets target to air (not at y 0); right click places selected block if cell is air and doesn't overlap player
- After edit rebuild the chunk, also neighbor chunk if block on chunk border
- Suppress context menu on right click

### Hotbar
- Fixed bottom center: 7 slots (grass, dirt, sand... wait: grass, dirt, stone, sand, wood, leaves, snow), each small square in block color with its number, on dark semi-transparent bar
- Selected slot gets white border
- Select with keys 1-7 or mouse wheel (wraps)

### Sky, clouds, water
- Sky-blue background 0x87ceeb with matching fog (~40 to 110)
- Ambient light 0.65 + directional light 0.8
- ~25 flat white transparent boxes as clouds at height ~90, slowly drifting, wrapping around player
- Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame — visual only

### UI
- Fullscreen start overlay with title, controls list, "Click to play"
- Reappears whenever pointer lock released
- Body without margins, fullscreen canvas, window resize

Let me now write this carefully.

Let me start with the structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>mc.html</title>
<style>
/* styles */
</style>
</head>
<body>
<!-- UI -->
<script src="...three.js"></script>
<script>
// game code
</script>
</body>
</html>
```

Now let me think through the details.

### Noise functions

I need:
- Integer hash function giving 0-1 (mix with large prime multipliers and xor-shifts)
- Smoothed 2D noise via bilinear interpolation with smoothstep
- 4 octaves combined into fractal noise
- 3D version for caves

Let me implement:

```js
function hash2(ix, iy) {
  // integer hash
  let h = ix * 73856092 ^ iy * 19328891;
  // xor shifts
  h = (h ^ (h >> 13)) * 127;
  return ((h & 0x7fffffff) / 0x7fffffff);
}
```

Actually let me make a proper value noise. Let me define:

```js
function vhash(x, y) {
  let h = (Math.imul(x, 374761393) ^ (y * 668265265));
  h = (h ^ (h >>> 13)) * 1274126177;
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

For 2D noise with bilinear interpolation and smoothstep:

```js
function noise2(x, y) {
  const X = Math.floor(x) & 255;
  const Y = Math.floor(y) & 255;
  const xf = x - Math.floor(x);
  const yf = y - Math.floor(y);
  const u = xf * xf * (3 - 2 * xf); // smoothstep
  const v = yf * yf * (3 - 2 * yf);
  const aa = vhash(X, Y);
  const ba = vhash(X + 1, Y);
  const ab = vhash(X, Y + 1);
  const bb = vhash(X + 1, Y + 1);
  const x1 = aa + u * (ba - aa);
  const x2 = ab + u * (bb - ab);
  return x1 + v * (x2 - x1);
}
```

Fractal noise (4 octaves):

```js
function fractal2(x, y) {
  let amp = 1, freq = 1, sum = 0, norm = 0;
  for (let i = 0; i < 4; i++) {
    sum += amp * noise2(x * freq, y * freq);
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / norm;
}
```

3D noise for caves:

```js
function noise3(x, y, z) {
  ... similar but with 8 corners
}
function fractal3(x, y, z) { ... }
```

Let me write the 3D version:

```js
function noise3(x, y, z) {
  const X = Math.floor(x) & 255;
  const Y = Math.floor(y) & 255;
  const Z = Math.floor(z) & 255;
  const xf = x - Math.floor(x);
  const yf = y - Math.floor(y);
  const zf = z - Math.floor(z);
  const u = xf * xf * (3 - 2 * xf);
  const v = yf * yf * (3 - 2 * yf);
  const w = zf * zf * (3 - 2 * zf);
  const c000 = vhash(X, Y); // need 3D hash
  ...
}
```

Hmm, I need a 3D hash too. Let me just make a hash function that takes 3 ints:

```js
function vhash3(x, y, z) {
  let h = (Math.imul(x, 374761393) ^ Math.imul(y, 668265265) ^ Math.imul(z, 2147043723));
  h = (h ^ (h >>> 13)) * 1274126177;
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

Then 3D noise trilinear:

```js
function noise3(x, y, z) {
  const X0 = Math.floor(x) & 255, X1 = X0 + 1;
  const Y0 = Math.floor(y) & 255, Y1 = Y0 + 1;
  const Z0 = Math.floor(z) & 255, Z1 = Z0 + 1;
  const xf = x - Math.floor(x), yf = y - Math.floor(y), zf = z - Math.floor(z);
  const u = xf*xf*(3-2*xf), v = yf*yf*(3-2*yf), w = zf*zf*(3-2*zf);
  const c000 = vhash3(X0, Y0, Z0), c100 = vhash3(X1, Y0, Z0);
  const c010 = vhash3(X0, Y1, Z0), c110 = vhash3(X1, Y1, Z0);
  const c001 = vhash3(X0, Y0, Z1), c101 = vhash3(X1, Y0, Z1);
  const c011 = vhash3(X0, Y1, Z1), c111 = vhash3(X1, Y1, Z1);
  const x00 = c000 + u*(c100-c000);
  const x10 = c010 + u*(c110-c010);
  const x01 = c001 + u*(c101-c001);
  const x11 = c011 + u*(c111-c011);
  const y0 = x00 + v*(x10-x00);
  const y1 = x01 + v*(x11-x01);
  const z = y0 + w*(y1-y0);
  return z;
}
```

OK. Now terrain generation.

Column height:
```
m = fractal2(coords.x * 0.004, coords.z * 0.004)
h = fractal2(coords.x * 0.02, coords.z * 0.02)
H = floor(5 + m*m*58 + h*10)
```

Column fill for y from 0 to H-1:
- y == 0: stone (unbreakable)
- y < H-3: stone
- The 3 layers under surface: these are y = H-4, H-3, H-2? Wait let me re-read.

"below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = ..."

So the structure from bottom:
- y 0: stone
- below H-3: stone (i.e., y from 1 to H-4 are stone)
- the 3 layers under the surface: dirt (or sand/stone based on H) — these would be y = H-3, H-2, H-1 (3 layers)
- surface: y = H — the top layer

Wait, "the 3 layers under the surface" means the 3 layers directly beneath the surface block. So surface is at y=H, and the 3 layers under it are y=H-1, H-2, H-3. These are dirt (with variant).

Then surface at y=H:
- snow if H >= 46
- stone if H >= 37
- sand if H <= 16
- otherwise grass

Let me code the column generation:

```js
function generateColumn(cx, cz) {
  const arr = new Uint8Array(16 * 16 * 80);
  const sx = cx * 16, sz = cz * 16;
  for (let lx = 0; lx < 16; lx++) {
    for (let lz = 0; lz < 16; lz++) {
      const wx = sx + lx, wz = sz + lz;
      const m = fractal2(wx * 0.004, wz * 0.004);
      const h = fractal2(wx * 0.02, wz * 0.02);
      let H = Math.floor(5 + m*m*58 + h*10);
      // tree check
      const treeHash = vhash(wx, wz); // per column hash
      for (let y = 0; y < 80; y++) {
        let id = 0;
        if (y === 0) {
          id = 3; // stone
        } else if (y < H - 3) {
          id = 3; // stone
        } else if (y >= H - 3 && y <= H - 1) {
          // 3 layers under surface
          if (H <= 16) id = 4; // sand
          else if (H >= 37) id = 3; // stone
          else id = 2; // dirt
        } else if (y === H) {
          // surface
          if (H >= 46) id = 7; // snow
          else if (H >= 37) id = 3; // stone
          else if (H <= 16) id = 4; // sand
          else id = 1; // grass
        }
        arr[idx(lx, y, lz)] = id;
      }
      // Trees
      if (treeHash < 0.02) {
        // check surface is grass
        ... 
      }
    }
  }
}
```

Wait, but I need to be careful about the y range. Heightmap H is the surface level. Blocks go from 0 to H-1 below surface, and surface is at y=H. But max height is 80, so H can be up to... floor(5 + m*m*58 + h*10). With m,h in [0,1], max is 5+58+10 = 73. Min is 5. So H ranges 5 to 73, all within 80. Good.

But wait, what if H is such that H-3 goes negative? If H=5, then H-3=2. y<2 is stone (y=0,1), y=2,3,4 are the 3 layers under surface (dirt since H=5 not <=16... wait H=5 <=16 so sand), y=5 surface (H<=16 so sand). OK fine.

Actually wait, let me reconsider. When H is small like 5, the "3 layers under surface" are y=2,3,4 and surface is y=5. That works since we loop y from 0 to 79 but most will be air (id=0) above H.

Hold on, actually there's an issue. The condition `y >= H-3 && y <= H-1` handles the 3 sub-surface layers, and `y === H` handles surface. But what about y > H? Those should be air (id stays 0). Good. And the conditions for y < H-3 handle stone. And y==0 stone. So the logic covers all cases:
- y==0: stone
- 0 < y < H-3: stone
- H-3 <= y <= H-1: dirt/sand/stone
- y == H: surface type
- y > H: air

But there's overlap concern: if H-3 <= 0, e.g., H=2, then H-3 = -1. y < -1 never true for y>=0. Hmm, but H min is 5, so H-3 min is 2. Fine. Actually let me double check: could H be less than 3? H = floor(5 + ...) >= 5 always. So H-3 >= 2. Good.

Let me restructure more cleanly:

```js
for (let y = 0; y < 80; y++) {
  let id = 0;
  if (y === 0 || y < H - 3) {
    id = 3; // stone (y=0 unbreakable, below H-3 stone)
  } else if (y >= H - 3 && y < H) {
    // 3 layers under surface (H-3, H-2, H-1)
    if (H <= 16) id = 4;
    else if (H >= 37) id = 3;
    else id = 2;
  } else if (y === H) {
    if (H >= 46) id = 7;
    else if (H >= 37) id = 3;
    else if (H <= 16) id = 4;
    else id = 1;
  }
  arr[getIdx(lx, y, lz)] = id;
}
```

Wait, `y === 0 || y < H-3`: for y=0, stone. For y in 1..H-4, stone. Good. But note y=0 is also covered by y<H-3 when H>3. It's fine, redundant.

Actually, let me simplify: since H >= 5, y < H-3 includes y=0. So I don't even need the separate y===0 check, but I'll keep it for clarity/safety. Actually the spec says "y 0 = unbreakable stone" explicitly, so keeping it makes intent clear.

Now trees. "Trees: on grass, when a per-column hash < .02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

So tree generates only if surface block is grass (id=1). Surface at y=H. Check arr[surface] === 1.

Tree:
- trunk: 4 wood blocks up starting at y=H+1 (on top of grass). So y = H+1, H+2, H+3, H+4 = wood.
- "the trunk fits inside the chunk" — meaning H+4 < 80? Actually "fits inside the chunk" probably means the tree doesn't extend beyond the 80-block height. So H+4 <= 79, i.e., H <= 75. Since H max is 73, always fits. But let me keep the check anyway.

Actually, wait. Let me reconsider "fits inside the chunk". The chunk is 16x16x80. The tree is placed at the column's surface. Since we generate per-column (all 16x16), the x,z always fit. The only constraint is height: H+4 must be < 80. So "trunk fits" = H+4 < 80.

Leaves:
- "leaves as a 5x5 layer twice" — two layers of 5x5 leaves at the top of the trunk.
- "then 3x3" — a 3x3 layer
- "then 1 on top" — 1 leaf block at the very top

Let me think about placement. Trunk top at y=H+4. 

Two 5x5 layers: probably at y=H+4 and y=H+5? Or y=H+3 and H+4? Let me think. Typically these trees have leaves near the top. "4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top."

Reading order: first 4 wood up (trunk, y=H+1..H+4), then leaves 5x5 twice, then 3x3, then 1 on top.

So leaves from bottom to top:
- 5x5 layer 1
- 5x5 layer 2
- 3x3 layer
- 1 on top

That's 4 leaf layers total. Placed above the trunk top (y=H+4). So:
- 5x5 layer at y=H+5
- 5x5 layer at y=H+6
- 3x3 layer at y=H+7
- 1 on top at y=H+8

Hmm, that seems tall. Let me reconsider. Maybe the 5x5 layers are centered. A 5x5 layer centered at (lx, lz) with the trunk in the middle. The column is 16 wide, trunk at some (lx,lz). 5x5 extends ±2. If trunk is at edge of column (lx=0), 5x5 would extend to lx=-2 which is out of bounds (into neighbor chunk). But since we generate per-column and trees only replace air, and the spec says "into air", maybe we just skip blocks outside chunk or into non-air.

Actually, "only into air" means we place leaves only where the block is air. So if a leaf would go into a trunk or ground block, skip it. And if it's outside the chunk bounds, we... hmm. Since we're generating the whole column, we can place it. But if it extends into neighbor chunk's area, we'd overwrite neighbor data. That's a problem for correctness.

But given the spec says to generate per-column and place leaves "only into air", and doesn't mention splitting trees across chunks, I think we should just place within the chunk bounds and only into air blocks. If a leaf position is outside [0,16)x[0,80), skip it. Actually, to be safe, I'll place leaves only within the current chunk's local coordinates, and only into air.

Hmm, but a 5x5 layer at the column edge would try to write to lx=-2..-1 or lx=14..15. Writing to lx=14,15 is fine (within chunk). Writing to lx=-2,-1 is out. Let me just clamp/skip out-of-bounds.

Actually, let me reconsider the tree height. Maybe simpler interpretation:
- Trunk: 4 wood at y = H+1 to H+4.
- Leaves: two 5x5 layers at y=H+4 and y=H+5? No...

Let me just go with a reasonable interpretation. The exact leaf pattern isn't critical for "playability". Let me do:

Trunk top at yt = H+4.
- Layer 1 (5x5): y = yt (H+4)
- Layer 2 (5x5): y = yt+1 (H+5)
- Layer 3 (3x3): y = yt+2 (H+6)
- Layer 4 (1): y = yt+3 (H+7)

Each layer centered on the trunk column (lx, lz). 5x5 spans lx-2..lx+2, lz-2..lz+2. 3x3 spans lx-1..lx+1. 1 spans lx, lz.

Place only into air, and only within chunk bounds (0<=lx'<16, 0<=lz'<16, 0<=y<80).

This gives a nice tree. Let me code it.

```js
if (treeHash < 0.02) {
  if (arr[getIdx(lx, H, lz)] === 1 && H + 4 < 80) {
    // trunk
    for (let t = 1; t <= 4; t++) arr[getIdx(lx, H+t, lz)] = 5;
    const yt = H + 4;
    // 5x5 layers
    for (let l = 0; l < 2; l++) {
      const ly = yt + 1 + l;
      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          const nx = lx + dx, nz = lz + dz;
          if (nx>=0 && nx<16 && nz>=0 && nz<16 && ly < 80) {
            if (arr[getIdx(nx, ly, nz)] === 0) arr[getIdx(nx, ly, nz)] = 6;
          }
        }
      }
    }
    // 3x3
    const ly3 = yt + 3;
    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        const nx = lx + dx, nz = lz + dz;
        if (nx>=0 && nx<16 && nz>=0 && nz<16 && ly3 < 80) {
          if (arr[getIdx(nx, ly3, nz)] === 0) arr[getIdx(nx, ly3, nz)] = 6;
        }
      }
    }
    // 1 on top
    const ly1 = yt + 4;
    if (ly1 < 80 && arr[getIdx(lx, ly1, lz)] === 0) arr[getIdx(lx, ly1, lz)] = 6;
  }
}
```

Good enough.

### Block index helper

```js
function getIdx(lx, y, lz) {
  return (lx * 80 + y) * 16 + lz;
}
```

Chunk array size = 16*80*16 = 20480. Good.

### Global read/write block helpers

```js
const chunkMap = new Map(); // key "cx,cz" -> { data: Uint8Array, mesh: ... }

function getChunkKey(cx, cz) { return cx + "," + cz; }

function getBlock(wx, wy, wz) {
  const cx = Math.floor(wx / 16);
  const cz = Math.floor(wz / 16);
  const key = getChunkKey(cx, cz);
  const c = chunkMap.get(key);
  if (!c) return 0; // missing chunk → air
  const lx = wx - cx * 16;
  const lz = wz - cz * 16;
  if (lx < 0 || lx >= 16 || lz < 0 || lz >= 16) return 0; // shouldn't happen
  if (wy < 0 || wy >= 80) return 0;
  return c.data[getIdx(lx, wy, lz)];
}

function setBlock(wx, wy, wz, id) {
  const cx = Math.floor(wx / 16);
  const cz = Math.floor(wz / 16);
  const key = getChunkKey(cx, cz);
  let c = chunkMap.get(key);
  if (!c) {
    c = { data: new Uint8Array(16*80*16), mesh: null };
    chunkMap.set(key, c);
  }
  const lx = wx - cx * 16;
  const lz = wz - cz * 16;
  c.data[getIdx(lx, wy, lz)] = id;
}
```

Note: Math.floor for negative numbers works correctly (floor(-1/16) = floor(-0.0625) = -1). Good, so negative coords work.

### Chunk generation

```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(16*80*16);
  const sx = cx * 16, sz = cz * 16;
  for (let lx = 0; lx < 16; lx++) {
    for (let lz = 0; lz < 16; lz++) {
      const wx = sx + lx, wz = sz + lz;
      const m = fractal2(wx * 0.004, wz * 0.004);
      const h = fractal2(wx * 0.02, wz * 0.02);
      let H = Math.floor(5 + m*m*58 + h*10);
      for (let y = 0; y < 80; y++) {
        let id = 0;
        if (y === 0 || y < H - 3) {
          id = 3;
        } else if (y >= H - 3 && y < H) {
          if (H <= 16) id = 4;
          else if (H >= 37) id = 3;
          else id = 2;
        } else if (y === H) {
          if (H >= 46) id = 7;
          else if (H >= 37) id = 3;
          else if (H <= 16) id = 4;
          else id = 1;
        }
        data[getIdx(lx, y, lz)] = id;
      }
      // caves
      for (let y = 3; y < H - 2; y++) {
        if (fractal3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
          data[getIdx(lx, y, lz)] = 0;
        }
      }
      // trees
      const treeHash = vhash(wx, wz);
      if (treeHash < 0.02 && data[getIdx(lx, H, lz)] === 1 && H + 4 < 80) {
        ... (as above)
      }
    }
  }
  return data;
}
```

Wait, there's a subtlety with caves. Caves use 3D noise. The spec says "for y between 3 and H−2, if 3D noise at position*0.09 exceeds 0.67, set air." So caves only carved down to H-2, meaning the surface layers aren't caved. Good.

But wait, I'm applying caves AFTER setting the column fill. So caves remove blocks. But then the "surface" might get removed by cave carving, leaving dirt/under-surface exposed. That's fine, it's just how caves look.

Hmm, but actually there's an issue: if a cave removes the surface grass block, then the tree generation check `data[...] === 1` for that column would fail. That's fine.

Also, one concern: caves could carve out the dirt layers and leave stone exposed, which looks like natural erosion. Fine.

### Meshing

For each chunk, build ONE BufferGeometry. For each non-air block, for each of 6 faces, check neighbor. If neighbor is air, add the face.

The 6 faces with their normals and vertices. Standard cube faces. Let me define face data.

For a block at (bx, by, bz), the 6 faces:
- +X (right): normal (1,0,0), vertices at x=bx+1
- -X (left): normal (-1,0,0), vertices at x=bx
- +Y (top): normal (0,1,0), vertices at y=by+1
- -Y (bottom): normal (0,-1,0), vertices at y=by
- +Z (front): normal (0,0,1), vertices at z=bz+1
- -Z (back): normal (0,0,-1), vertices at z=bz

Lighting factors: top 1.0, sides 0.8, bottom 0.55.

Colors: block color multiplied by light factor.

Let me define the 6 faces with their 4 corner offsets. I'll use the standard approach where each face has 4 vertices forming 2 triangles.

Let me define face templates. Each face: normal vector, and 4 relative vertex positions (unit square), and the light factor.

```js
const FACES = [
  { dir: [ 1, 0, 0], light: 0.8, verts: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  { dir: [-1, 0, 0], light: 0.8, verts: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  { dir: [ 0, 1, 0], light: 1.0, verts: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { dir: [ 0,-1, 0], light: 0.55, verts: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { dir: [ 0, 0, 1], light: 0.8, verts: [[1,0,1],[0,0,1],[0,1,1],[1,1,1]] },
  { dir: [ 0, 0,-1], light: 0.8, verts: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]] },
];
```

Wait, I need to make sure the winding order is correct (CCW when viewed from outside) so faces aren't culled incorrectly. Let me be careful.

For the +X face (normal pointing +X, i.e., looking from +X toward origin, we see the face). Vertices should be CCW when viewed from the +X direction.

Hmm, this is getting complicated. Let me use a well-known correct face definition.

Standard approach (from various voxel tutorials):

For each face, define 4 vertices and 2 triangles (indices 0,1,2 and 0,2,3).

Let me use this common set (ensuring correct winding):

Face +X (right): 
```
v0 = (1, 0, 0)
v1 = (1, 0, 1)
v2 = (1, 1, 1)
v3 = (1, 1, 0)
```
Normal (1,0,0). Winding v0→v1→v2→v3 should be CCW viewed from +X.

Face -X (left):
```
v0 = (0, 0, 0)
v1 = (0, 0, 1)
v2 = (0, 1, 1)
v3 = (0, 1, 0)
```
Normal (-1,0,0).

Face +Y (top):
```
v0 = (0, 1, 1)
v1 = (1, 1, 1)
v2 = (1, 1, 0)
v3 = (0, 1, 0)
```
Normal (0,1,0).

Face -Y (bottom):
```
v0 = (0, 0, 0)
v1 = (1, 0, 0)
v2 = (1, 0, 1)
v3 = (0, 0, 1)
```
Normal (0,-1,0).

Face +Z (front):
```
v0 = (1, 0, 1)
v1 = (0, 0, 1)
v2 = (0, 1, 1)
v3 = (1, 1, 1)
```
Normal (0,0,1).

Face -Z (back):
```
v0 = (0, 0, 0)
v1 = (1, 0, 0)
v2 = (1, 1, 0)
v3 = (0, 1, 0)
```
Normal (0,0,-1).

Let me verify winding for +X. Viewed from +X (looking in -X direction), the Y axis points up, and Z axis... when looking from +X toward origin, Z appears to go... Let me set up: camera at (large, 0, 0) looking at origin. Up is +Y. Then right hand rule: x toward viewer (out of screen toward us is +X, but we're looking in -X so screen-x is... ). Ugh.

Let me just trust a known-good implementation. Actually, the safest is to not rely on winding and instead... no, we need correct winding for backface culling.

Let me think again more carefully using a concrete method.

For the +X face, the face lies on plane x=1 (local). The four corners are at x=1, and (y,z) ∈ {(0,0),(0,1),(1,1),(1,0)}. When we look at this face from the +X side (from far positive x looking toward -x), we see the yz-plane. In this view, let's say y is up and z is to the... 

When looking along -X direction (from +x to origin) with up=+Y:
- The horizontal screen axis corresponds to... using cross product. If forward = -X = (-1,0,0) and up = (0,1,0), then right = up × forward... actually right = forward × up? Let me compute. In a right-handed system with camera, right = normalize(cross(up, -forward))? 

Let me just use the standard result. I recall that a commonly used and correct face layout is:

```
const faces = [
  // name, normal, [4 vertices as [dx,dy,dz] offsets], light
  ['right',  [1,0,0], [[1,0,0],[1,1,0],[1,1,1],[1,0,1]], 0.8],
  ['left',   [-1,0,0],[[0,0,1],[0,1,1],[0,1,0],[0,0,1].map... ]
];
```

I'll take a different, robust approach. Let me define each face by its normal and 4 corner offsets, and verify the winding produces outward-facing CCW using the right-hand rule: for a face with normal N and two edge vectors E1, E2 (from v0→v1 and v0→v3), we need E1 × E2 to point along N (for CCW in right-handed coords with front face... Three.js default is counter-clockwise front faces, culling back faces).

Actually Three.js uses clockwise winding for front faces by default? Let me recall: THREE.WebGLRenderer with forceCullTemplate... no. By default, three.js treats CCW as front-facing (standard OpenGL convention with glFrontFace). Backfaces (CW) are culled.

So for each face, going v0→v1→v2→v3 should be counterclockwise when viewed from the side the normal points toward.

Right-hand rule: if I curl the fingers of my right hand from v0→v1→v2, my thumb points in the direction of the normal (for CCW). So I need (v1-v0) × (v3-v0) to be parallel to the normal (pointing outward).

Let me verify +X face with:
v0=(1,0,0), v1=(1,1,0), v2=(1,1,1), v3=(1,0,1)
e1 = v1-v0 = (0,1,0)
e3 = v3-v0 = (0,0,1)
cross(e1,e3) = (1*1-0*0, 0*0-0*1, 0*0-1*0) = (1, 0, 0). ✓ Points along +X. 

Let me verify -X face:
v0=(0,0,1), v1=(0,1,1), v2=(0,1,0), v3=(0,0,0)
e1 = v1-v0 = (0,1,0)
e3 = v3-v0 = (0,0,-1)
cross(e1,e3) = (1*(-1)-0*0, 0*0-0*(-1), 0*0-1*0) = (-1, 0, 0). ✓ Along -X.

+Y face:
v0=(0,1,1), v1=(1,1,1), v2=(1,1,0), v3=(0,1,0)
e1 = v1-v0 = (1,0,0)
e3 = v3-v0 = (0,0,-1)
cross(e1,e3) = (0*(-1)-0*0, 0*0-1*(-1), 1*0-0*0) = (0, 1, 0). ✓ Along +Y.

-Y face:
v0=(0,0,0), v1=(1,0,0), v2=(1,0,1), v3=(0,0,1)
e1 = v1-v0 = (1,0,0)
e3 = v3-v0 = (0,0,1)
cross(e1,e3) = (0*1-0*0, 0*0-1*1, 1*0-0*0) = (0, -1, 0). ✓ Along -Y.

+Z face:
v0=(1,0,1), v1=(0,0,1), v2=(0,1,1), v3=(1,1,1)
e1 = v1-v0 = (-1,0,0)
e3 = v3-v0 = (0,1,0)
cross(e1,e3) = (0*0-0*1, 0*0-(-1)*0, (-1)*1-0*0) = (0, 0, -1). ✗ Along -Z, but normal should be +Z!

So +Z face winding is wrong. Let me swap v3 and v1 for +Z:
v0=(1,0,1), v1=(1,1,1), v2=(0,1,1), v3=(0,0,1)
e1 = v1-v0 = (0,1,0)
e3 = v3-v0 = (-1,0,0)
cross(e1,e3) = (1*0-0*0, 0*(-1)-0*0, 0*0-1*(-1)) = (0, 0, 1). ✓ Along +Z.

-Z face:
v0=(0,0,0), v1=(0,1,0), v2=(1,1,0), v3=(1,0,0)
e1 = v1-v0 = (0,1,0)
e3 = v3-v0 = (1,0,0)
cross(e1,e3) = (1*0-0*0, 0*1-0*0, 0*0-1*1) = (0, 0, -1). ✓ Along -Z.

Great, so corrected face definitions:

```js
const FACES = [
  { n:[1,0,0], l:0.8, v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  { n:[-1,0,0], l:0.8, v:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  { n:[0,1,0], l:1.0, v:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { n:[0,-1,0], l:0.55, v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { n:[0,0,1], l:0.8, v:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
  { n:[0,0,-1], l:0.8, v:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] },
];
```

Now, the meshing algorithm. For each block (bx,by,bz) with non-air id, for each face f:
- neighbor block position = (bx + n[0], by + n[1], bz + n[2])
- getBlock(neighbor) → if air (0), add face.

But wait — there's a subtlety with transparency. Leaves should be opaque here (they're rendered with the same material and fake lighting). The spec doesn't mention alpha for leaves, so treat leaves as opaque. Also water is separate (a plane), not block water. So all blocks are opaque. Good, so "if neighbor is air, add face" — but should we also add faces adjacent to leaves? If leaves are opaque, then a block next to leaves shouldn't show a face (it's occluded). And leaves themselves show faces toward air. Simplest: only draw faces where neighbor is air (0). Since leaves are opaque, this is consistent.

Actually, hold on. Should we consider leaves as blocking faces? If we treat leaves as opaque (block everything except air), then yes. The spec says "if it is air, add that face". So the rule is purely: neighbor air → draw face. Leaves block. Good, simplest.

Now, building the geometry. For each drawn face, add 4 vertices (position, normal, color) and 6 indices.

Position = block position + face vertex offset. Since mesh is at chunk origin, and block world position = (cx*16+bx, by, cz*16+bz)... wait, but the mesh is at origin. So we use local block coords (bx, by, lz) directly as world-ish coords for the geometry, since the mesh Object3D is positioned at chunk world location.

Actually, the chunk mesh should be positioned at (cx*16, 0, cz*16) and the geometry uses local block coordinates (0..15, 0..79, 0..15). Raycasting uses world coordinates though. Hmm.

Let me reconsider. The spec says: "Use world coordinates for vertices and keep the mesh at the origin."

So the geometry stores WORLD coordinates (worldX = cx*16 + bx, etc.), but the mesh's position is at origin (0,0,0)? That doesn't quite make sense unless the mesh is added as a child of a group, or the mesh position IS set to chunk location.

Wait, "keep the mesh at the origin" — I think this means the geometry vertices are in world space, and the mesh object itself is translated to the chunk's world position. But if vertices are world coords and mesh is at chunk world pos, that doubles up.

Let me re-read: "loop all non-air blocks, and for each of the 6 sides check the neighbor... if it is air, add that face (2 triangles) to flat position/normal/color arrays. Use world coordinates for vertices and keep the mesh at the origin."

Hmm, "keep the mesh at the origin" — maybe it means keep the geometry's local position at origin but the vertices are world coords, and then you set mesh.position = (cx*16, 0, cz*16)? No...

Actually I think the intended meaning: The BufferGeometry holds world-space coordinates. Each chunk mesh is created and its .position is NOT set (stays at origin 0,0,0)? That would put all chunks at origin overlapping. That can't be right.

Wait, maybe they mean: the mesh object is added at the chunk's world position, so effectively "the mesh is at the origin [of its local coordinate system which coincides with world coords because vertices are world coords]". 

Let me interpret it as: vertices are world coordinates, and mesh.position = (cx*16, 0, cz*16). Since vertices are already world coords, setting position to chunk location would shift them. That's wrong.

Alternative: vertices are LOCAL coords (0..15), mesh.position = chunk world pos. This is the standard approach. But spec says "world coordinates for vertices".

Hmm, let me reconcile. Perhaps: vertices are world coordinates, and the mesh is positioned at origin (0,0,0) but... no.

Actually, you know what, I bet the intended design is:
- Chunk mesh position = (cx*16, 0, cz*16)
- Vertices stored as LOCAL coordinates relative to chunk (0..15)

OR

- Chunk mesh position = (0,0,0)
- Vertices stored as WORLD coordinates

These give identical results IF the mesh position matches. The phrase "keep the mesh at the origin" strongly suggests mesh.position = (0,0,0), hence vertices must be world coords.

But if all chunk meshes are at (0,0,0) with world coords, they'd overlap! Unless... they're not all added to the scene at once. Actually they ARE added to the scene. So overlapping is a problem.

Wait, unless the mesh.position is set to the chunk location AND vertices are local. Let me reconsider: maybe "keep the mesh at the origin" refers to something else — like during rebuild, reset the geometry to origin. Or it's poorly worded.

Let me just do the standard correct thing that makes raycasting work: 
- mesh.position = (cx*16, 0, cz*16)
- vertices are LOCAL (0..15 range)

Then raycasting in world space: the ray origin and directions are in world space, and meshes are positioned correctly. This works perfectly.

But the spec explicitly says "Use world coordinates for vertices and keep the mesh at the origin." 

Hmm, if I want to follow literally: vertices = world coords, mesh.position = (0,0,0). All chunks at origin → overlap. That's clearly wrong for rendering multiple chunks.

Unless... they add each chunk mesh as a child of a parent group positioned at chunk location? No.

Let me reconsider. Maybe the design is: there's ONE big container, and chunk meshes are positioned at chunk world coords, and "keep the mesh at the origin" means the GEOMETRY is built in the mesh's local space which equals world coords because... no.

OK here's another thought. What if "keep the mesh at the origin" means the mesh.position stays (0,0,0) and vertices are world coords, BUT chunks are only rendered when the player is near, and... no, they still overlap at origin.

I think the cleanest interpretation that satisfies "world coordinates for vertices" AND makes the game work is:

Actually, wait. Let me reconsider — maybe they DO want mesh.position = chunk location and vertices = world coords, but that's redundant/wrong. OR mesh.position = chunk location and vertices = local. 

Given the ambiguity, and that raycasting needs correct world positions, I'll go with:
- mesh.position = (cx*16, 0, cz*16)  
- vertices = LOCAL coordinates (relative to chunk)

This is the standard, correct, working approach. The raycaster operates in world space and finds intersections correctly.

But to honor "world coordinates for vertices," I could store world coords in the geometry AND set mesh.position = (0,0,0) for the geometry... no.

Hmm, let me reconsider once more. Actually, maybe the intended approach: The geometry vertices are world coordinates. The mesh is added to the scene. To position it, you DON'T set mesh.position (leave at origin). But then all chunks overlap.

Unless chunks are children of a Group, and the Group is positioned. Like:
```
const chunkGroup = new THREE.Group();
chunkGroup.position.set(cx*16, 0, cz*16);
chunkGroup.add(mesh);  // mesh at origin within group
```
Then mesh.local vertices = local coords. Same as setting mesh.position.

I think the spec wording is just imprecise. Let me go with the WORKING approach:
- mesh.position = (cx*16, 0, cz*16)
- geometry vertices = local block coords (0..15, 0..79, 0..15)

Raycasting will work because three.js raycaster transforms world rays into mesh local space using matrixWorld.

Actually, wait. Let me reconsider whether to use world coords in geometry. If I use world coords in geometry and set mesh.position = (0,0,0), all chunks overlap — BAD. If I use world coords and mesh.position = chunk loc, vertices get shifted by chunk loc — BAD (double). If I use local coords and mesh.position = chunk loc — GOOD. If I use local coords and mesh.position = 0 — all overlap BAD.

So the only correct option is local coords + mesh.position = chunk loc. I'll do that. I'll note in comments that "world coordinates" effectively means the coords correspond to world positions (since local+position = world).

Hmm, but actually, let me reconsider. There's a subtle possibility: maybe they intend vertices in world coords, and mesh.position = chunk location, but they made an error, OR they intend the geometry to be built once per chunk and the chunk's world position is baked into vertices, with mesh at origin — and chunks are managed such that only relevant chunks exist but they're all at origin... no.

I'll go with local coords + mesh.position = chunk loc. This is definitely correct and works. Let me move on.

Actually, let me reconsider the raycast. The raycaster is created with ray.set(origin, direction). It intersectsObjects(meshes) where meshes are in world space. Three.js computes the model-view-projection and does the intersection in world space correctly accounting for each mesh's matrixWorld (position). So local coords + position works. 

Now, the highlight box. "Outline the targeted block with a black wireframe box." Create a BoxGeometry slightly larger than 1 unit (e.g., 1.002) with wireframe, black color, and position it at the targeted block's world position. Update each frame.

```js
const highlight = new THREE.LineSegments(
  new THREE.EdgeGeometry(new THREE.BoxGeometry(1.01,1.01,1.01)),
  new THREE.LineBasicMaterial({color:0x000000})
);
highlight.visible = false;
scene.add(highlight);
```

Position at (targetX+0.5, targetY+0.5, targetZ+0.5).

### Raycasting for break/place

Each frame (while locked), cast ray from camera center. Camera direction from Euler yaw/pitch.

```js
const camDir = new THREE.Vector3();
camera.getWorldDirection(camDir);
ray.set(camera.position, camDir);
const hits = ray.intersectObjects(chunkMeshes, false);
let target = null;
if (hits.length > 0 && hits[0].distance < 6) {
  const hit = hits[0];
  const p = hit.point;
  const n = hit.face.normal;
  const breakBlock = new THREE.Vector3(
    Math.floor(p.x - n.x*0.5),
    Math.floor(p.y - n.y*0.5),
    Math.floor(p.z - n.z*0.5)
  );
  const placeCell = new THREE.Vector3(
    Math.floor(p.x + n.x*0.5),
    Math.floor(p.y + n.y*0.5),
    Math.floor(p.z + n.z*0.5)
  );
  target = breakBlock;
}
```

The hit.face.normal is in local space but transformed to world by three.js? Actually, intersectObjects returns face normal in world coordinates (three.js transforms normals by the inverse-normal matrix / world orientation). For position-preserving transforms, the normal is world-space. Yes, three.js provides world-space normals in the intersection result. Good.

### Player physics

Player state:
```js
const player = {
  pos: new THREE.Vector3(8, ..., 8),
  vel: new THREE.Vector3(),
  yaw: 0, pitch: 0,
  onGround: false,
};
```

Spawn above terrain at x=8, z=8. Need to find terrain height there. Compute at spawn: chunk (0,0), sample height. Or just spawn high (y=60) and let gravity bring down. But better to spawn on surface. Let me sample the surface at (8,8).

Actually, spawning: I'll generate the spawn chunk and find the surface. Simpler: spawn at y = some high value like 50 and let it fall. But spec says "spawn above terrain". Let me find terrain height at spawn.

To find terrain height at (8,8): I need chunk (0,0) data. It may not be generated yet. Let me generate it upfront (the spawn chunk). Or compute height via noise directly.

Let me just compute height at spawn using the same formula:
```js
function surfaceHeightAt(wx, wz) {
  const m = fractal2(wx*0.004, wz*0.004);
  const h = fractal2(wx*0.02, wz*0.02);
  return Math.floor(5 + m*m*58 + h*10);
}
```
Spawn at y = that + 1 (so standing on top). Actually player eye is 1.62, and player box height 1.8. Standing on surface at y=H means feet at y=H, and the block occupies [H, H+1]. Player feet should be at H (top of surface block). So player.pos.y = H (feet) ... let me define pos.y as the feet position or the eye? Let me define pos.y as the player's eye position? Or feet?

Common approach: pos.y = feet (bottom of player box). Player box from pos.y (feet) to pos.y + 1.8 (head). Eye at pos.y + 1.62.

If standing on a surface block at y=H (block spans [H, H+1]), the player's feet should be at y=H (resting exactly on top). So pos.y = H. Then eye = H + 1.62. Camera at eye.

But "spawn above terrain" — let me spawn feet at surface height H. Let me set player.pos.y = surfaceHeightAt(8,8). Hmm, but if there's water at 14.3, and surface is at H, and H could be < 14 for beaches. Spawning feet on top is fine.

Actually, let me reconsider: I'll spawn at y = H + 1 maybe, or H. Let me use H (feet exactly on surface top). But to be safe against floating point, spawn at H. If H is computed as floor(...), the surface block top is at H (block occupies [H, H+1)). Feet at H rests on top. Good.

Wait, actually if feet at exactly y=H and the block occupies y in [H, H+1), then feet is inside the block (at its bottom face). That would cause immediate collision. Better: feet at y = H (top of block is at H+1, so resting on top means feet at H+1? No...).

Let me think. A block at grid position y=H occupies the cube from y=H to y=H+1. Its top surface is at y=H+1. If a player stands "on" this block, their feet are at y=H+1 (on the top surface). So feet y = H+1 = surfaceGridY + 1.

Hmm wait, that's if the surface block's grid index is H. Let me clarify: "surface = ... at y=H" means the block at grid coordinate y=H is the surface block. That block occupies cube [H, H+1). Its top is at H+1. So to stand on top, feet at y = H+1.

So spawn feet at y = H + 1. Player.pos.y (feet) = H+1.

Let me define player.pos.y as feet position. Camera eye = pos.y + 1.62.

Hmm, but actually many implementations use pos.y as eye level or as the bottom of the box. Let me be explicit and use feet.

Let me define:
- player.pos: Vector3, where y is the FEET position (bottom of player AABB).
- Player AABB: x±0.3, y from pos.y to pos.y+1.8, z±0.3.
- Camera eye: pos.y + 1.62.

Collision: check AABB against solid blocks. For each axis, move and test overlap; if overlap, revert (or snap).

Collision test function:
```js
function collides(pos) {
  // pos is feet position
  const minX = Math.floor(pos.x - 0.3), maxX = Math.floor(pos.x + 0.3);
  const minY = Math.floor(pos.y), maxY = Math.floor(pos.y + 1.8);
  const minZ = Math.floor(pos.z - 0.3), maxZ = Math.floor(pos.z + 0.3);
  for (let bx = minX; bx <= maxX; bx++)
    for (let by = minY; by <= maxY; by++)
      for (let bz = minZ; bz <= maxZ; bz++)
        if (getBlock(bx, by, bz) !== 0) return true;
  return false;
}
```

Movement per axis:
```js
// X
let np = player.pos.clone();
np.x += vx * dt;
if (!collides(np)) player.pos.x = np.x;
// Z similarly
// Y
let np2 = player.pos.clone();
np2.y += vy * dt;
if (!collides(np2)) { player.pos.y = np2.y; player.onGround = false; }
else {
  if (vy < 0) player.onGround = true; // landing
  vy = 0;
}
```

Actually the standard approach: move along each axis separately and resolve collisions. Let me implement carefully.

Let me use fixed dt or clamp dt. I'll use a fixed step or just dt with clamp.

Actually for simplicity and reliability, let me use a fixed timestep for physics (e.g., 1/60) via accumulator, or just use dt and hope it's stable enough. Given the spec wants specific values (gravity 25, jump 8.5, speed 5.5), let me use dt directly but clamp to avoid tunneling.

Let me use delta time clamped to ~0.1.

Movement:
```js
const speed = 5.5;
const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
// WASD
```

Wait, need to define forward based on yaw. With yaw rotation order YXZ and camera, let me define:
- Moving forward (W) should move in the direction the camera faces (projected on XZ).
- Camera direction: from Euler (pitch, yaw) with order YXZ.

Let me compute camera forward:
```js
const forward = new THREE.Vector3(
  -Math.sin(yaw) * Math.cos(pitch),
  Math.sin(pitch),
  -Math.cos(yaw) * Math.cos(pitch)
);
```
For horizontal movement, zero out the y component and normalize:
```js
const hforward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw)).normalize();
const hright = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw)).normalize();
```

WASD:
```js
const move = new THREE.Vector3();
if (W) move.add(hforward);
if (S) move.sub(hforward);
if (D) move.add(hright);
if (A) move.sub(hright);
move.multiplyScalar(speed);
```

Apply horizontal velocity (set pos velocity directly, or integrate). Let me set:
```js
player.vel.x = move.x;
player.vel.z = move.z;
```
And gravity affects vel.y:
```js
player.vel.y -= 25 * dt;
if (onGround && space) player.vel.y = 8.5;
```

Then move per axis using vel.

Let me structure the physics update:
```js
function updatePhysics(dt) {
  // gravity
  player.vel.y -= 25 * dt;
  // horizontal input
  ... compute desired horizontal velocity ...
  player.vel.x = desiredX;
  player.vel.z = desiredZ;
  // move with collision
  // X
  player.pos.x += player.vel.x * dt;
  if (collides(player.pos)) { player.pos.x -= player.vel.x * dt; player.vel.x = 0; }
  // Z
  player.pos.z += player.vel.z * dt;
  if (collides(player.pos)) { player.pos.z -= player.vel.z * dt; player.vel.z = 0; }
  // Y
  player.pos.y += player.vel.y * dt;
  if (collides(player.pos)) {
    player.pos.y -= player.vel.y * dt;
    if (player.vel.y < 0) player.onGround = true;
    player.vel.y = 0;
  }
  // fall off check
  if (player.pos.y < -20) { player.pos.set(8, spawnY, 8); player.vel.set(0,0,0); }
}
```

Hmm, but moving by vel*dt and reverting on collision is a bit crude. The standard AABB resolution moves incrementally. This should work for typical speeds. Let me keep it but be careful.

Actually, a cleaner approach for axis-separated collision: move one axis at a time, and if collision, snap to the block boundary. But reverting also works and is simpler. Let me use revert (undo the move on collision). This prevents embedding. It can cause slight jitter but is fine.

Wait, there's a subtlety: if I revert on collision, and the player is walking into a wall, they stop. Good. If falling into floor, revert puts them back on top. Good. Landing detection: when moving down and colliding, set onGround=true. Good.

Let me refine: I'll compute the full intended position then test. Actually per-axis incremental is what I described. Let me keep it.

Jump: only if onGround. Set vel.y = 8.5 upward.

### Camera rotation

Mouse movement while locked:
```js
document.addEventListener('mousemove', (e) => {
  if (pointerLocked) {
    player.yaw -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    player.pitch = Math.max(-Math.PI/2 + 0.001, Math.min(Math.PI/2 - 0.001));
  }
});
```

Set camera rotation: camera.rotation.order = 'YXZ'; camera.rotation.y = player.yaw; camera.rotation.x = player.pitch; camera.rotation.z = 0.

Eye position: camera.position.copy(player.pos) then y += 1.62.

### Clouds

~25 white transparent boxes at height ~90, drifting, wrapping around player.

```js
const clouds = [];
for (let i = 0; i < 25; i++) {
  const g = new THREE.PlaneGeometry? 
```

Spec says "flat white transparent boxes". So boxes (BoxGeometry), not planes. Let me use BoxGeometry with transparent, opacity < 1, and depthWrite false.

```js
const cloudMat = new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.85, depthWrite:false});
for (let i=0;i<25;i++){
  const cloud = new THREE.Mesh(new THREE.BoxGeometry(?, ?, ?), cloudMat);
  cloud.position.set(random-ish, 90, random-ish);
  cloud.userData.offset = ...;
  scene.add(cloud);
  clouds.push(cloud);
}
```

But no Math.random allowed! "Terrain (deterministic, no Math.random)". The restriction is about terrain determinism. For clouds, I can use deterministic positions via hash. Let me use vhash for cloud positions.

Clouds wrap around player: each frame, reposition clouds relative to player so they stay in view. Simple approach: cloud.x = player.x + (hash(i)*something - offset). Actually "drifting and wrapping around the player" — clouds move in +x slowly, and if they go too far behind/beyond player, wrap them around.

Let me do: each cloud has a base offset relative to player. Position = player.pos + offset, where offset is fixed per cloud (deterministic). They drift by increasing offset.x over time, and when offset.x exceeds some bound, wrap. Actually simpler: clouds positioned at player-relative offsets that slowly increase x; wrap when beyond ±some range.

Let me do:
```js
cloud.position.set(player.pos.x + cloud.offX, 90, player.pos.z + cloud.offZ);
cloud.offX += drift * dt;
if (cloud.offX > 60) cloud.offX -= 120; // wrap
```
With offX, offZ set deterministically from hash in [-60, 60].

Hmm, but "wrapping around the player" might just mean they follow the player (stay on screen). Following with offsets and wrapping keeps them near player. Good.

### Water

One semi-transparent blue plane at height 14.3, re-centered on player each frame. Visual only.

```js
const waterMat = new THREE.MeshLambertMaterial({color:0x00aaFF? , transparent:true, opacity:0.7, depthWrite:false});
const water = new THREE.Mesh(new THREE.PlaneGeometry(?, ?, ?), waterMat);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
```

Re-center: water.position.x = player.pos.x; water.position.z = player.pos.z. Each frame.

Plane size: large, e.g., 512x512 or based on render distance. Let me use 400x400.

Water is visual only, so no collision. Good.

### Fog & lights

```js
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);
scene.background = 0x87ceeb;
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(0, 1, 0)? 
```

Directional light position should be set. Let me put it at an angle. Since it's directional, position matters for direction. dir.position.set(0.5,1,0.3).normalize() — but with intensity only, position doesn't affect lighting much for DirectionalLight (it uses position as direction). Let me set a fixed direction.

Actually the fake lighting already darkens sides/bottoms, so the directional light mostly affects tops. Fine.

### Materials & colors

One shared MeshLambertMaterial:
```js
const material = new THREE.MeshLambertMaterial();
```
Vertex colors are set per-vertex in the geometry (geometry.setAttribute('color', ...)). MeshLambertMaterial with vertexColors uses the color attribute. Default mesh material vertexColors is false, but MeshLambertMaterial supports vertexColors property. Let me set:
```js
const material = new THREE.MeshLambertMaterial({vertexColors: true});
```

Block colors (RGB 0-1):
```js
const BLOCK_COLORS = {
  1: 0x4caf50,
  2: 0x795548,
  3: 0x9e9e9e,
  4: 0xe7d9a8,
  5: 0x8d6e63,
  6: 0x2e7d32,
  7: 0xffffff,
};
```
Convert to RGB:
```js
function rgb(hex){ return [(hex>>16&255)/255, (hex>>8&255)/255, (hex&255)/255]; }
```

For each face vertex, color = blockColor * lightFactor. Set per-vertex (all 4 vertices of a face get same color).

### Mesh rebuild function

```js
function rebuildChunk(cx, cz) {
  const key = getChunkKey(cx, cz);
  const c = chunkMap.get(key);
  if (!c) return;
  // dispose old
  if (c.mesh) {
    c.mesh.geometry.dispose();
    scene.remove(c.mesh);
  }
  const data = c.data;
  const positions = [];
  const normals = [];
  const colors = [];
  const indices = [];
  let vi = 0;
  for (let lx=0; lx<16; lx++)
  for (let y=0; y<80; y++)
  for (let lz=0; lz<16; lz++) {
    const id = data[getIdx(lx,y,lz)];
    if (id === 0) continue;
    const wx = cx*16+lx, wz = cz*16+lz;
    const col = rgb(BLOCK_COLORS[id]);
    for (let f=0; f<6; f++) {
      const face = FACES[f];
      const nx = wx + face.n[0], ny = y + face.n[1], nz = wz + face.n[2];
      if (getBlock(nx,ny,nz) === 0) {
        for (let v=0; v<4; v++) {
          const vo = face.v[v];
          positions.push(wx+vo[0], y+vo[1], wz+vo[2]);
          normals.push(face.n[0], face.n[1], face.n[2]);
          colors.push(col[0]*face.l, col[1]*face.l, col[2]*face.l);
        }
        indices.push(vi, vi+1, vi+2, vi, vi+2, vi+3);
        vi += 4;
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.set(cx*16, 0, cz*16);
  c.mesh = mesh;
  scene.add(mesh);
  chunkMeshes.push(mesh);
}
```

Wait, I'm pushing to chunkMeshes every rebuild, which could duplicate. Let me manage chunkMeshes array properly. Actually, let me keep chunkMeshes as the array of all current chunk meshes, and rebuild updates it. But rebuilding disposes old and adds new, so I need to remove old from chunkMeshes and add new. Let me restructure: chunkMeshes is rebuilt or I filter.

Better: maintain chunkMeshes by filtering out disposed meshes and adding new ones. Or, since each chunk has one mesh, let me store mesh reference on the chunk object (c.mesh) and derive chunkMeshes array when needed for raycasting.

For raycasting, I need an array of meshes. Let me just build it each frame or maintain it. Simplest: keep a global array `meshList`, and in rebuild, splice out the old mesh and push the new. Let me do that.

Actually, let me reconsider. The spec says "Keep all chunk meshes in a global array for raycasting". So I maintain a global array. On rebuild: remove old mesh from array (if present), dispose, create new, add to array.

Let me handle it:
```js
if (c.mesh && meshList.indexOf(c.mesh) !== -1) meshList.splice(meshList.indexOf(c.mesh), 1);
...
meshList.push(mesh);
```

### Chunk management each frame

"Each frame: generate block data for all chunks within 5 chunks of the player (max 4 per frame); build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame); for chunks farther than 7, remove the mesh, dispose its geometry and delete the entry."

So per frame:
1. Determine player's chunk (pcx, pcz).
2. Chunks within 5 (Chebyshev distance <= 5) need data generation. We can generate up to 4 per frame.
3. Chunks within 4 whose 4 direct neighbors (up/down/left/right) all have data → build mesh. Up to 2 per frame.
4. Chunks farther than 7 from player → remove mesh, dispose geometry, delete entry.

Let me implement chunk distance as Chebyshev (max of dx, dz) or Euclidean? "within 5 chunks of the player" — let me use Chebyshev distance (max(|dx|,|dz|)) for simplicity, or Euclidean. Let me use Euclidean-ish. Actually let me use Chebyshev for the "within N chunks" checks since it's simpler and standard for chunk rings.

Hmm, but the neighbor requirement "chunks within 4 chunks whose 4 neighbors already have data" — the 4 neighbors are the chunk at (cx±1, cz) and (cx, cz±1). For a chunk near the map edge, a neighbor might not be generated yet. So we wait until all 4 neighbors have data.

Let me implement:

```js
function updateChunks() {
  const pcx = Math.floor(player.pos.x / 16);
  const pcz = Math.floor(player.pos.z / 16);
  
  // 4. Remove far chunks (>7)
  for (const [key, c] of chunkMap.entries()) {
    const [cx, cz] = key.split(',').map(Number);
    const d = Math.max(Math.abs(cx-pcx), Math.abs(cz-pcz));
    if (d > 7) {
      if (c.mesh) { c.mesh.geometry.dispose(); scene.remove(c.mesh); }
      const idx = meshList.indexOf(c.mesh);
      if (idx !== -1) meshList.splice(idx, 1);
      chunkMap.delete(key);
    }
  }
  
  // 1. Generate data for chunks within 5 (up to 4/frame)
  let genCount = 0;
  for (let dx=-5; dx<=5 && genCount<4; dx++) {
    for (let dz=-5; dz<=5 && genCount<4; dz++) {
      const cx = pcx+dx, cz = pcz+dz;
      const key = getChunkKey(cx, cz);
      if (!chunkMap.has(key)) {
        chunkMap.set(key, { data: null, mesh: null });
        generateChunkDataInto(cx, cz); // fills data
        genCount++;
      }
    }
  }
  ...
}
```

Hmm, but I need to store chunks with data=null until generated, OR generate immediately. Let me generate immediately when adding to map to keep it simple. But "max 4 per frame" limits generation rate. Let me generate into the data array.

Let me restructure: when adding a chunk to map, allocate data=null (placeholder). Then in the generation loop, if data is null, generate it (fill the Uint8Array). This way the map tracks existence but data may be null.

Actually, let me simplify: generate data immediately when first creating the chunk entry, but limit to 4 per frame. So:

```js
function ensureChunkData(cx, cz) {
  const key = getChunkKey(cx, cz);
  let c = chunkMap.get(key);
  if (!c) {
    c = { data: null, mesh: null };
    chunkMap.set(key, c);
  }
  if (c.data === null) {
    c.data = generateChunkData(cx, cz);
    return true; // freshly generated this call
  }
  return false;
}
```

Frame update:
```js
// Generate up to 4 chunks' data
let genBudget = 4;
for (let dx=-5; dx<=5 && dx<=genBudget... ) {...}
```

Let me write the loops carefully with budget counters.

Generation loop (budget 4):
```js
let genBudget = 4;
outer: for (let dx = -5; dx <= 5; dx++) {
  for (let dz = -5; dz <= 5; dz++) {
    if (genBudget <= 0) break outer;
    const cx = pcx + dx, cz = pcz + dz;
    if (Math.max(Math.abs(dx), Math.abs(dz)) > 5) continue;
    ensureChunkData(cx, cz);
    genBudget--;
  }
}
```

Mesh building loop (budget 2): chunks within 4 whose 4 neighbors have data.
```js
let meshBudget = 2;
for (let dx=-4; dx<=4 && meshBudget>0; dx++) {
  for (let dz=-4; dz<=4; dz++) {
    if (meshBudget<=0) break;
    const cx = pcx+dx, cz = pcz+dz;
    if (Math.max(Math.abs(dx),Math.abs(dz)) > 4) continue;
    const key = getChunkKey(cx, cz);
    const c = chunkMap.get(key);
    if (!c || !c.data) continue;
    if (c.mesh) continue; // already built
    // check 4 neighbors have data
    const nE = chunkMap.get(getChunkKey(cx+1, cz));
    const nW = chunkMap.get(getChunkKey(cx-1, cz));
    const nN = chunkMap.get(getChunkKey(cx, cz+1));
    const nS = chunkMap.get(getChunkKey(cx, cz-1));
    if (nE && nE.data && nW && nW.data && nN && nN.data && nS && nS.data) {
      rebuildChunk(cx, cz);
      meshBudget--;
    }
  }
}
```

Wait, but the neighbor check requires the 4 neighbors to have data. But if those neighbors are at the edge, they might be far chunks not yet generated. The check ensures they exist with data. Good. But there's a subtlety: a chunk's neighbor might have data but not be "within 5" of player yet — but that's fine, if it has data we can build.

However, there's a potential deadlock: a chunk needs neighbor data, but the neighbor is far and won't get data until the player moves. That's acceptable — meshes build up as player moves.

Also, initial spawn: player spawns at (8,8), chunk (0,0). Its neighbors (1,0),(-1,0),(0,1),(0,-1) need data. The generation loop generates chunks within 5, so neighbors get data within a few frames. Then mesh builds. Good.

But to make the game start reasonably, maybe pre-generate the spawn region. Let me pre-generate a small area at startup to avoid a blank start. Actually, let me just let the frame update handle it; within a few frames the spawn area renders. But the very first frame might show nothing. Let me pre-warm: generate and build chunks within 2 of spawn at startup synchronously. That gives immediate content.

Let me add an init step that generates chunks within radius 3 and builds what's possible, before the animation loop. Actually building requires neighbor data which requires generation. Let me just loop generation for a fixed radius several times in init.

Hmm, let me keep it simple: in init, call updateChunks a few times, or manually generate all chunks within radius 3 and build those whose neighbors are ready. Let me write an init that generates within radius 3 fully, then builds within radius 2.

Actually, let me just run the per-frame update loop a handful of times synchronously in init. Or better, write a warmup that fills a small radius.

Let me do a warmup:
```js
function warmup(radius) {
  for (let pass=0; pass<4; pass++) {
    for (let dx=-radius; dx<=radius; dx++)
      for (let dz=-radius; dz<=radius; dz++)
        ensureChunkData(pcx+dx, pcz+dz);
  }
  for (let dx=-radius; dx<=radius; dx++)
    for (let dz=-radius; dz<=radius; dz++) {
      // build if neighbors ready
    }
}
```

This is getting complex. Let me simplify warmup: generate all chunks within radius R, then build all chunks within radius R-1 (whose neighbors are all generated). Since generation fills all within R first, the neighbor check passes for those within R-1.

```js
function warmup(R) {
  for (let dx=-R; dx<=R; dx++)
    for (let dz=-R; dz<=R; dz++)
      ensureChunkData(pcx+dx, pcz+dz);
  for (let dx=-R; dx<=R; dx++)
    for (let dz=-R; dz<=R; dz++) {
      const cx=pcx+dx, cz=pcz+dz;
      const c = chunkMap.get(getChunkKey(cx,cz));
      if (c && !c.mesh) {
        // check neighbors
        if (chunkMap.get(getChunkKey(cx+1,cz))?.data &&
            chunkMap.get(getChunkKey(cx-1,cz))?.data &&
            chunkMap.get(getChunkKey(cx,cz+1))?.data &&
            chunkMap.get(getChunkKey(cx,cz-1))?.data) {
          rebuildChunk(cx, cz);
        }
      }
    }
}
```

With R=3 or 4. This gives a visible world at start. Good.

But careful: warmup radius 4 means generating 9x9=81 chunks, each with 20480 bytes = fine. Building meshes for ~49 chunks. That's OK performance-wise for init.

Actually generating 81 chunks each doing 16*80*16 = 20480 iterations with noise calls... 81 * 20480 = ~1.6M noise evaluations, each involving several hash calls. That might take a bit but acceptable (< 1s). Let me use R=3 (49 chunks) to be safe. Actually let me reconsider — building 49 chunk meshes each frame is heavy, but warmup is one-time. Building a mesh involves iterating all blocks and neighbors. 49 * 20480 * 6 = 6M neighbor checks, each a getBlock (Map lookup). That could be slowish but one-time. Let me use R=3.

Hmm, actually the neighbor check via getBlock does a Map lookup per face. 6M Map lookups might take ~1s. Let me optimize later or reduce. For init it's fine. During gameplay, only 2 meshes rebuild per frame, so it's fine.

Actually, let me reconsider the meshing performance during normal play. Rebuilding 2 chunks/frame: each chunk 20480 blocks * 6 faces = 122k getBlock calls * 2 = 244k Map lookups per frame. That's fine (< 1ms typically). Good.

### Block editing & rebuild

On break/place:
```js
function editBlock(bx, by, bz) {
  // determine chunk and neighbors to rebuild
  const cx = Math.floor(bx/16), cz = Math.floor(bz/16);
  rebuildChunk(cx, cz);
  const lx = ((bx % 16) + 16) % 16;
  const lz = ((bz % 16) + 16) % 16;
  if (lx === 0) rebuildChunk(cx-1, cz);
  if (lx === 15) rebuildChunk(cx+1, cz);
  if (lz === 0) rebuildChunk(cx, cz-1);
  if (lz === 15) rebuildChunk(cx, cz+1);
}
```

Wait, but rebuildChunk only rebuilds if the chunk has data and builds a mesh. If neighbor chunk has no data yet, rebuildChunk returns early. That's fine — it'll rebuild when data arrives. But for correctness of the immediate edit, the edited chunk must have data. Since the player is near, the edited chunk has data. Good.

Actually, let me make rebuildChunk robust: if chunk has data, rebuild mesh. If it already has a mesh, dispose old first.

### Break/place input handling

While locked:
- Left click: set target block to air, but not at y=0.
- Right click: place selected block at place cell if air and doesn't overlap player.

```js
document.addEventListener('mousedown', (e) => {
  if (!pointerLocked) return;
  if (e.button === 0) { // left: break
    if (target && target.y > 0) {
      setBlock(target.x, target.y, target.z, 0);
      editBlock(target.x, target.y, target.z);
    }
  } else if (e.button === 2) { // right: place
    if (place && getBlock(place.x, place.y, place.z) === 0) {
      // check not overlapping player
      const pb = new THREE.Box3();
      // player AABB
      ... test if place cell overlaps player box ...
      if (!overlapsPlayer(place)) {
        setBlock(place.x, place.y, place.z, selectedBlock);
        editBlock(place.x, place.y, place.z);
      }
    }
  }
});
```

OverlapsPlayer check: create AABB for the placed block (full block) and test against player AABB.

```js
function overlapsPlayer(bx, by, bz) {
  const box = new THREE.Box3(
    new THREE.Vector3(bx, by, bz),
    new THREE.Vector3(bx+1, by+1, bz+1)
  );
  const pmin = new THREE.Vector3(player.pos.x-0.3, player.pos.y, player.pos.z-0.3);
  const pmax = new THREE.Vector3(player.pos.x+0.3, player.pos.y+1.8, player.pos.z+0.3);
  const pbox = new THREE.Box3(pmin, pmax);
  return box.intersectsBox(pbox);
}
```

Selected block: hotbar selection (1-7 maps to block ids 1-7).

### Hotbar

7 slots: grass(1), dirt(2), stone(3), sand(4), wood(5), leaves(6), snow(7).
Selected slot changes with keys 1-7 or mouse wheel.

HTML/CSS for hotbar. Update border on selection change.

```js
let selected = 1; // block id
const hotbarSlots = [1,2,3,4,5,6,7];
function selectSlot(n) { // n 1..7
  selected = hotbarSlots[n-1];
  updateHotbarUI();
}
```

Mouse wheel:
```js
document.addEventListener('wheel', (e) => {
  if (!pointerLocked) return;
  const dir = e.deltaY > 0 ? 1 : -1;
  selected = ((selected - 1 + dir + 7) % 7) + 1;
  updateHotbarUI();
});
```

Keys 1-7:
```js
document.addEventListener('keydown', (e) => {
  if (e.code.startsWith('Digit')) {
    const n = parseInt(e.code.slice(5));
    if (n>=1 && n<=7) selectSlot(n);
  }
});
```

### Start overlay & pointer lock

```js
const overlay = document.getElementById('overlay');
overlay.addEventListener('click', () => {
  canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  pointerLocked = (document.pointerLockElement === canvas);
  overlay.style.display = pointerLocked ? 'none' : 'block';
});
```

requestPointerLock on overlay click. When pointer lock released, overlay reappears.

Canvas:
```js
const canvas = document.createElement('canvas');
document.body.appendChild(canvas);
const renderer = new THREE.WebGLRenderer({canvas});
renderer.setSize(innerWidth, innerHeight);
```

requestPointerLock on element. canvas.requestPointerLock().

### Resize

```js
window.addEventListener('resize', () => {
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
```

### Animation loop

```js
let last = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min((now - last)/1000, 0.1);
  last = now;
  
  updateControls(dt);
  updatePhysics(dt);
  updateChunks();
  updateClouds(dt);
  updateWater();
  updateHighlight();
  updateTargetRaycast();
  
  renderer.render(scene, camera);
}
```

Wait, I need to be careful: pointer lock look uses movementX which is only available while locked. Movement input (WASD) should work only while locked? The spec says "mouse look only while locked". WASD — probably also only while playing (locked). Let me track keys pressed and apply only when locked. Actually, let me apply movement always but it naturally stops when... hmm. Let me only process keyboard movement when locked to match "reacting to clicks while pointer not locked" avoidance. Actually the spec emphasizes clicks while locked. For movement, let me allow it always but it's fine either way. Let me only move when locked to be safe and consistent.

Let me track key states:
```js
const keys = {};
document.addEventListener('keydown', (e) => { keys[e.code] = true; });
document.addEventListener('keyup', (e) => { keys[e.code] = false; });
```

Movement while locked:
```js
if (pointerLocked) {
  const fwd = ...;
  ...
}
```

### Target raycast update each frame

```js
function updateTargetRaycast() {
  highlight.visible = false;
  if (!pointerLocked) { target=null; place=null; return; }
  const origin = camera.position.clone();
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);
  ray.set(origin, dir);
  const hits = ray.intersectObjects(meshList, false);
  target = null; place = null;
  if (hits.length > 0 && hits[0].distance <= 6) {
    const hit = hits[0];
    const p = hit.point;
    const n = hit.face.normal;
    target = new THREE.Vector3(
      Math.floor(p.x - n.x*0.5),
      Math.floor(p.y - n.y*0.5),
      Math.floor(p.z - n.z*0.5)
    );
    place = new THREE.Vector3(
      Math.floor(p.x + n.x*0.5),
      Math.floor(p.y + n.y*0.5),
      Math.floor(p.z + n.z*0.5)
    );
    highlight.visible = true;
    highlight.position.set(target.x+0.5, target.y+0.5, target.z+0.5);
  }
}
```

### Water re-center

```js
function updateWater() {
  water.position.x = player.pos.x;
  water.position.z = player.pos.z;
}
```

### Clouds drift

```js
function updateClouds(dt) {
  for (const cloud of clouds) {
    cloud.position.x = player.pos.x + cloud.offX;
    cloud.position.z = player.pos.z + cloud.offZ;
    cloud.offX += dt * 2; // drift
    if (cloud.offX > 80) cloud.offX -= 160;
  }
}
```

Hmm, clouds should be at height 90. cloud.position.y = 90.

offX, offZ deterministic from hash.

### Let me now also handle the "eye" camera position

camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z).

### Now, about the raycast normal being world-space

In three.js, when you do ray.intersectObjects, the returned face.normal is in world coordinates (transformed). Actually, let me double check: THREE.Raycaster.intersectObjects computes intersection in world space, and face.normal in the result is the world-space normal (it applies the rotation part of matrixWorld to the local normal). For meshes with uniform scale and no non-uniform rotation, this is fine. Our meshes have rotation identity, only translation. So normal is world-space. Good.

Actually, I recall that in older three.js the face normal in the intersection was in local space and you had to transform it. Let me check r128. In r128, Raycaster uses Ray.intersectBox or the triangle... Actually r128 uses `intersectObjects` → `ray.intersectObjects` → for each object, creates a ray in local space using matrixWorldInverse and ray.matrixWorldInverse... The resulting PointCloudRay or the intersection point is world-space. The face.normal... hmm.

Let me look: In r128, `Raycaster.intersectObject` → `intersectObjects` → `ray.intersectTriangle`? Actually it uses `Ray.prototype.intersectBox` no...

Let me recall the r128 implementation. Three.js r128 Raycaster:
- `intersectObjects(objects, recursive)` iterates.
- For each object, it computes `ray.origin.applyMatrix4(matrixWorldInverse)` and `ray.direction.applyMatrix4(matrixWorld, true)` (vector transform, no translation) to get the ray in the object's local space.
- Then `ray.intersectTriangle(appliedMatrixWorld, ...)` — it transforms the triangle's local vertices to world via matrixWorld, then does ray-triangle intersection in world space.
- The returned `point`, `distance`, `face`, `faceNormal`, `faceIndex`, `vertexIndex` are all in WORLD space.

Yes — in r128, the intersection results (point, faceNormal) are in world coordinates. Good. So hit.face.normal is world-space. 

Wait, let me double-check by recalling the actual code. In r128:

```js
Raycaster.prototype.intersectObject = function (object, recursive, intersectionArray) {
  ...
  ray.applyMatrix4(matrixWorldInverse);
  ...
  for each face in geometry:
    ray.intersectTriangle(faceVertexA, faceVertexB, faceVertexC, backSideIntersectionTest, intersectionArray, faceIndex, vertexIndex);
}
```

And `intersectTriangle`:
```js
Ray.prototype.intersectTriangle = function (appliedMatrixWorld, a, b, c, testBackFaces, dstArray, faceIndex, vertexIndexOut) {
  ...
  // Transform to world space...
  p1.applyMatrix4(worldMatrix).sub(p0)... 
  // Actually it computes in world space
  this.ray.origin.applyMatrix4(worldMatrix); // no
  ...
  // Returns faceNormal = n (which was transformed to world via appliedMatrixWorld normal?)
}
```

Hmm, let me recall more carefully. In r128, `intersectTriangle`:
```js
Ray.prototype.intersectTriangle = function (appliedMatrixWorld, a, b, c, testBackFaces, dstArray, faceIndex, vertexIndexOut) {
  var sp = raySpaceVectorA();
    sq = raySpaceVectorB();
  ...
  // Ray in local space (already transformed via ray.applyMatrix4(matrixWorldInverse))
  // Solve via Möller–Trumbore
  ...
  // normal in local space:
  var nlocal = ...; // face normal
  // Transform normal to world:
  nlocal.applyMatrix4(appliedMatrixWorld).normalize();
  var n = nlocal;
  ...
  // Result faceNormal = n (world space)
  // Result point:
  var wp = tempV.copy(pointLocal).applyMatrix4(worldMatrix);
  ...
}
```

Wait, I think in r128 the normal is transformed by appliedMatrixWorld (which is matrixWorld) and the point by worldMatrix. So both are world-space. Good.

Hmm, but actually I'm now unsure whether appliedMatrixWorld is matrixWorld or matrixWorldInverse. Let me not overthink; the key point is the result point and normal are in world coordinates in r128. I'm fairly confident.

Actually, let me reconsider. There's a well-known behavior: in three.js, `raycaster.intersectObjects` returns `intersection.face.normal` which is in the OBJECT's local space in older versions but transformed to world in newer. Let me just be safe and transform the normal myself if needed. But if it's already world, transforming again would be wrong.

Given uncertainty, let me handle it robustly: since our meshes have pure translation (no rotation/scale), the world-space normal equals the local-space normal. So regardless of whether three.js returns local or world normal, for our translation-only meshes they're identical! Because rotation part of matrixWorld is identity. So hit.face.normal is (±1,0,0) etc. in both local and world. 

So I don't need to worry. The normal will be correct (one of the 6 face normals) because the mesh has no rotation. 

### Let me also double check the raycast distance and block range

Max distance 6. Good.

### Now let me write the CSS

```css
html, body {
  margin: 0; padding: 0; overflow: hidden;
  width: 100%; height: 100%;
}
canvas { display: block; }
#crosshair {
  position: fixed; top: 50%; left: 50%;
  width: 20px; height: 20px;
  margin: -10px 0 0 -10px;
  pointer-events: none; z-index: 10;
}
#crosshair::before, #crosshair::after {
  content: ''; position: absolute; background: #fff;
}
#crosshair::before { top: 9px; left: 0; width: 20px; height: 2px; }
#crosshair::after { left: 9px; top: 0; width: 2px; height: 20px; }
#hotbar {
  position: fixed; bottom: 20px; left: 50%;
  transform: translateX(-50%);
  display: flex; gap: 4px; padding: 4px;
  background: rgba(0,0,0,0.5); border-radius: 4px;
  pointer-events: none; z-index: 10;
}
.slot {
  width: 44px; height: 44px; border: 2px solid rgba(255,255,255,0.3);
  position: relative; display: flex; align-items: center; justify-content: center;
}
.slot .swatch { width: 30px; height: 30px; border: 1px solid rgba(0,0,0,0.5); }
.slot .num { position: absolute; bottom: 1px; right: 3px; color: #fff; font: 12px monospace; }
.slot.selected { border-color: #fff; }
#overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.85);
  color: #fff; display: flex; flex-direction: column;
  align-items: center; justify-content: center; text-align: center;
  z-index: 20; cursor: pointer; font-family: sans-serif;
}
#overlay h1 { font-size: 48px; margin: 0 0 10px; }
#overlay ul { text-align: left; line-height: 1.8; }
```

### Let me now write the full file.

Let me be careful about a few things:

1. The `getBlock` for neighbor checks during meshing uses the global helper. Good.

2. When placing water plane, it should be behind blocks visually. Since water is transparent with depthWrite false, and blocks are opaque, blocks render first (depth written), then water (no depth write, blends). Good. Order independence via depthWrite false on water.

3. Clouds: transparent boxes at y=90. depthWrite false. They render among themselves. Fine.

4. Fog: applies to all objects including transparent. Water and clouds get fogged. Good.

Let me also make sure the directional light doesn't get too dark. With ambient 0.65 and directional 0.8, and fake lighting multipliers, tops are bright, sides medium, bottom dim. Should look fine.

MeshLambertMaterial lighting: diffuse color * (ambient + directional contributions). With vertexColors, the vertex color is the diffuse. So the fake lighting colors serve as the base color, and lights modulate. Top faces have high color (1.0 * blockColor), lit more. Bottoms 0.55 * blockColor, dimmer. This gives the blocky look. Good.

Wait, but MeshLambertMaterial with vertexColors: the vertex colors multiply the material's lighting. So a top face with color (0.24, 0.48, 0.30) [grass * 1.0] gets lit by ambient+directional. A bottom face (0.24*0.55, ...) gets same light but lower base → darker. Good, this achieves the fake lighting.

Let me double check grass color: 0x4caf50 → (76, 175, 80)/255 = (0.298, 0.686, 0.314). Times 1.0 top. Times 0.8 side = (0.238, 0.549, 0.251). Times 0.55 bottom = (0.164, 0.377, 0.173). Good.

### One concern: MeshLambertMaterial vertexColors and the `vertexColors` property

In three.js, to use per-vertex colors, set material.vertexColors = true. MeshLambertMaterial supports it. And the geometry must have a 'color' attribute. I set that. Good.

### Let me reconsider spawn and terrain height at (8,8)

surfaceHeightAt(8,8): m = fractal2(8*0.004, 8*0.004) = fractal2(0.032, 0.032). h = fractal2(0.16, 0.16). H = floor(5 + m²*58 + h*10). Deterministic. Whatever it is, spawn feet at H+1.

Actually, I realize I should spawn the player and ensure the spawn chunk is generated so collision works. Warmup radius 3 generates chunk (0,0) and neighbors. Good. Player at (8, 8) is in chunk (0,0). Collision checks getBlock(0,0) which has data. Good.

### Player box collision detail

When I move and test collides, I test the player AABB against blocks. Player AABB: x in [pos.x-0.3, pos.x+0.3], y in [pos.y, pos.y+1.8], z in [pos.z-0.3, pos.z+0.3]. Blocks checked: floor(minX)..floor(maxX) etc. Note: if pos.x=8.0 exactly, minX=7.7→floor 7, maxX=8.3→floor 8. So checks blocks 7 and 8. Good.

Edge case: pos.x at exactly integer, e.g., 8.0. minX=7.7 floor 7, maxX=8.3 floor 8. Fine.

If player is at pos.x=7.3 (0.3 from block boundary): minX=7.0 floor 7, maxX=7.6 floor 7. Only block 7. Good.

### Jump and onGround

onGround starts false. After spawning at H+1, if there's a block at H (surface), then falling, when we collide going down, onGround=true. Initially onGround=false so player falls a bit then lands. Good.

Actually, spawn at feet=H+1. The surface block occupies [H, H+1). Feet at H+1 is exactly on top. Next frame, gravity pulls down, we move down, test collision: player AABB y in [H+1 - tiny, H+1-tiny+1.8]. The block at y=H occupies [H,H+1]. Player bottom H+1-ε is above H+1? No: H+1-ε < H+1, so player bottom is just below H+1, i.e., just above the block top (block top is H+1). Wait block occupies [H, H+1), top at H+1. Player bottom at H+1-ε is below H+1-... hmm let me think numerically. H=30. Block y=30 occupies [30,31). Top at 31. Player feet spawn at 31. Player AABB y in [31, 32.8]. Move down by vy*dt (small). New feet = 31 - δ. AABB y in [31-δ, 32.8-δ]. Does it intersect block [30,31)? Block spans y [30,31). Player spans [31-δ, ...]. Overlap if 31-δ < 31 → yes (δ>0). So collision detected. Revert → feet back to 31. onGround=true. Good, lands on top.

But wait, that means even a tiny fall triggers collision and snaps back to exactly 31. Good, no sinking.

But there's the issue: at feet=31 exactly (spawn), AABB y in [31, 32.8]. Block at y=31? If surface is at H=30, then y=31 is air (above surface). So no collision at spawn. Good. Player falls, lands at 31.

Hmm, but what if H is such that there's no block immediately? E.g., water/beach. If surface is sand at H=15 and water at 14.3, feet spawn at 16. Block at y=15 is sand ([15,16)). Player at feet 16, AABB [16,17.8]. Falls, collides with sand at y=15 ([15,16))? Player bottom 16-δ < 16, block top 16. Overlap. Lands at 16. Good.

### Water plane at 14.3

Visual only. Where terrain is below 14.3, water shows. Good.

### Let me reconsider the meshing neighbor check for faces

When checking neighbor for a face, I call getBlock(nx,ny,nz). For a block at chunk edge (lx=0), nx = wx-1 = (cx-1)*16 + 15, which is in chunk (cx-1, cz). getBlock handles that (computes cx-1, looks up neighbor chunk). If neighbor chunk has no data, getBlock returns 0 (air) → we draw the face. That's the correct behavior (invisible chunk treated as air, so its boundary faces are drawn). Good.

But there's a subtle issue: if the neighbor chunk hasn't generated yet, we draw its boundary faces using OUR block colors. Later when neighbor generates, we rebuild and it's consistent. Fine.

### Potential issue: getBlock returns 0 for y outside 0-79. During meshing, ny could be -1 (bottom face of y=0 block) → getBlock returns 0 → draw bottom face. Good (we see below). And ny=80 (top face of y=79 block) → returns 0 → draw. Good.

### Let me also handle the highlight box geometry

THREE.EdgeGeometry(BoxGeometry) gives wireframe lines. Or use BoxHelper. Let me use EdgeGeometry for a clean black outline. Actually simpler: 
```js
highlight = new THREE.LineSegments(
  new THREE.EdgeGeometry(new THREE.BoxGeometry(1.005, 1.005, 1.005)),
  new THREE.LineBasicMaterial({color:0x000000})
);
```
Position at block center. Good.

### Context menu suppression

```js
canvas.addEventListener('contextmenu', (e) => e.preventDefault());
```

Also on the document.

### Pointer lock on overlay click

overlay.addEventListener('click', () => canvas.requestPointerLock()).

But canvas.requestPointerLock requires user gesture — click provides it. Good.

### Let me also ensure the canvas is focusable / captures mouse. Not strictly needed.

### Movement keys

WASD: code KeyW, KeyA, KeyS, KeyD. Space: Space. 

### Let me write it all out now.

Let me also reconsider: the spec says "spawn above terrain at x=8, z=8". So x=8, z=8. Feet y = surfaceHeightAt(8,8)+1.

Let me also make sure the camera look uses the correct sign. With yaw increasing turning left or right? Standard: yaw around Y. Let me define camera rotation.y = yaw, rotation.x = pitch. Mouse movementX decreases yaw (move right → yaw decreases → camera turns right). Let me match typical FPS: mouse moves right → view rotates right → yaw decreases. I'll use player.yaw -= movementX * sens. And pitch -= movementY * sens (mouse up → pitch decreases → look up). Let me verify: looking up should decrease pitch (if pitch is measured from horizontal, looking up = negative pitch in a right-handed system where +x is right, +y up, +z toward back). Camera forward with pitch: dir.y = sin(pitch)? Let me define:

camera rotation order YXZ. rotation.y = yaw, rotation.x = pitch.
Forward direction after rotations: 
- Rotate around Y by yaw: x' = -sin(yaw)... 
Actually let me just compute camera.getWorldDirection and trust it.

For pitch: when pitch is negative, does the camera look up? In three.js, rotating around X (right axis) by a negative angle tilts the view up. Let me verify: rotation.x = pitch. A positive pitch rotates the camera so it looks down (in the default YXZ order, +X rotation brings the top toward the viewer... hmm).

Let me just test mentally: camera initially looks along -Z (forward = (0,0,-1)). Rotate around X axis by angle θ. The rotation matrix around X:
[1 0 0; 0 cosθ -sinθ; 0 sinθ cosθ]
Applied to (0,0,-1): 
y' = cosθ*0 - sinθ*(-1) = sinθ
z' = sinθ*0 + cosθ*(-1) = -cosθ
So forward becomes (0, sinθ, -cosθ). For θ>0, y-component positive → forward points up. So positive pitch looks UP.

But I set pitch -= movementY. When mouse moves up (movementY negative), pitch increases → looks up. Wait movementY when mouse moves up is negative (cursor goes up = negative y movement). So pitch -= (negative) = pitch increases → looks up. Correct!

And clamp pitch to (-π/2+eps, π/2-eps) to prevent flipping.

For yaw: rotate around Y by yaw. Matrix:
[cosθ 0 sinθ; 0 1 0; -sinθ 0 cosθ]
Applied to forward (0,0,-1) after Y rotation:
x' = cosθ*0 + sinθ*(-1) = -sinθ
z' = -sinθ*0 + cosθ*(-1) = -cosθ
So after Y rotation, forward = (-sinθ, 0, -cosθ). For θ=0, forward=(0,0,-1) ✓. For θ increasing, x becomes negative → moves left? Let me see: yaw += turns camera... The horizontal movement: forward = (-sin(yaw), 0, -cos(yaw)). If yaw increases, -sin(yaw) becomes more negative → forward.x negative. Moving forward (W) adds forward to velocity → moves in -x direction. 

Mouse movementX (move right = positive) → player.yaw -= movementX → yaw decreases → -sin(yaw) becomes positive → forward.x positive → move forward moves +x → camera turns right. Correct!

Good, so:
- player.yaw -= movementX * sens
- player.pitch -= movementY * sens

And camera.rotation.y = player.yaw, camera.rotation.x = player.pitch, order YXZ.

Let me set camera.rotation.order = 'YXZ' once.

### getWorldDirection

After setting rotation, camera.getWorldDirection(dir) gives the forward. I use it for raycast. Consistent.

### Let me finalize and write.

Actually, let me reconsider one thing about meshing performance and the "max 2 per frame" for building. Building a mesh iterates all 20480 blocks and does up to 6 getBlock calls each = 122k Map.get calls. At 2/frame that's 244k/frame, fine. But the FIRST time a chunk is built, it's a one-time cost of ~122k lookups, negligible.

But wait, there's a concern: building the mesh also allocates Float32Arrays and creates buffer attributes. For 2/frame it's fine.

Let me also make sure I don't rebuild a chunk that has no data. rebuildChunk checks c.data. Good.

### Let me also double-check the "chunks within 4 whose 4 neighbors already have data" — the neighbor chunks themselves need data, which the generation loop (within 5) provides. But generation is limited to 4/frame, and meshing to 2/frame. So it ramps up. Warmup handles initial.

### Let me write the final code.

Let me also reconsider: should movement be disabled when not locked? Yes, I'll gate WASD under pointerLocked. But keydown/keyup tracking is fine always.

Also, when pointer unlocks, overlay reappears. Good.

### Edge: requestPointerLock might throw if not in a secure context? file:// is considered potentially trustworthy? Actually pointer lock from file:// should work in Chrome/Firefox on user gesture (click). The overlay click is a user gesture. Good.

Let me now also handle the case where clicking the overlay but canvas isn't the pointer lock element. I set canvas.requestPointerLock(). After lock, document.pointerLockElement === canvas. Good.

### Let me write everything.

Actually, let me reconsider the water plane size and the fog. Fog range 40-110. Water plane 400x400 centered on player. At distance, water gets fogged to sky color. Good.

Clouds at y=90, within ~80 of player. Fog kicks in at 40, so distant clouds fog out. Fine.

### Let me reconsider the number of clouds and their size. 25 boxes. Size maybe 12x3x8 or so. Let me use BoxGeometry(14, 4, 10). Positioned at y=90.

### Final code writing.

Let me also add: suppress default on space to avoid page scroll (though overflow hidden). And prevent arrows/etc. Not critical.

Let me write the file now.

One more consideration: The `ray` for raycasting — I create it once. ray.set(origin, direction). origin = camera.position. But camera.position is a Vector3 that I reuse; I should clone or set fresh each frame to avoid mutation. ray.set(origin, dir) uses references? Ray.set copies origin and direction into internal vectors. Actually Ray.set(origin, direction) sets this.origin.copy(origin) and this.direction.copy(direction). So it copies. Good, no aliasing. But I pass camera.position which is fine.

For direction, I compute camera.getWorldDirection(dir). Let me make dir a reusable vector.

Let me code:
```js
const _rayDir = new THREE.Vector3();
function updateTargetRaycast() {
  ...
  camera.getWorldDirection(_rayDir);
  ray.set(camera.position, _rayDir);
  ...
}
```

Good.

### Let me also reconsider: when breaking, "not at y 0". So if target.y === 0, skip. Good.

### Place: "places the selected block if the cell is air and does not overlap the player." Check getBlock(place)===0 and !overlapsPlayer(place). Then setBlock and editBlock.

### Let me make sure setBlock creates the chunk if missing. Yes.

### editBlock rebuilds edited chunk + bordering chunks. But rebuildChunk only rebuilds if data exists. For the edited chunk, data exists (player near). For bordering chunks, they should have data (player near a border means neighbor is close). If not, they rebuild later. Fine.

### Alright, writing now.

Let me also think: do I need to handle the case where the same block edit is on a chunk border and I rebuild both? Yes, editBlock handles it.

Let me also make sure rebuildChunk doesn't crash if meshList manipulation. Let me store mesh on c.mesh and also push to meshList. On rebuild, remove old from meshList.

Let me write a helper to remove a mesh from meshList safely.

### Let me also double check: initial chunkMap empty. Warmup populates. Good.

### Also, I should make sure the game loop starts only after scene/camera setup.

### Let me write the HTML.

Let me carefully compose the JS. I'll write it section by section.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>mc.html</title>
<style>
* { margin: 0; }
html, body { width:100%; height:100%; overflow:hidden; background:#000; }
canvas { display:block; position:fixed; inset:0; }
#crosshair { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10; }
#crosshair::before, #crosshair::after {
  content:""; position:absolute; background:#ffffff; box-shadow:0 0 2px rgba(0,0,0,0.8);
}
#crosshair::before { top:50%; left:50%; width:18px; height:2px; margin:-1px 0 0 -9px; }
#crosshair::after { top:50%; left:50%; width:2px; height:18px; margin:-9px 0 0 -1px; }
#hotbar {
  position:fixed; bottom:18px; left:50%; transform:translateX(-50%);
  display:flex; gap:4px; padding:4px; background:rgba(0,0,0,0.55);
  border-radius:6px; pointer-events:none; z-index:10;
}
.slot {
  width:46px; height:46px; border:2px solid rgba(255,255,255,0.25);
  border-radius:4px; position:relative;
}
.slot .swatch {
  position:absolute; inset:5px; border:1px solid rgba(0,0,0,0.4); border-radius:2px;
}
.slot .num {
  position:absolute; bottom:1px; right:3px; color:#ddd; font:12px/1 monospace; text-shadow:0 0 2px #000;
}
.slot.selected { border-color:#ffffff; box-shadow:0 0 6px rgba(255,255,255,0.7); }
#overlay {
  position:fixed; inset:0; background:rgba(0,0,0,0.82); color:#fff;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  text-align:center; z-index:20; cursor:pointer; font-family: "Segoe UI", Arial, sans-serif;
}
#overlay h1 { font-size:52px; margin:0 0 8px; letter-spacing:2px; }
#overlay .sub { color:#bbb; margin-bottom:18px; }
#overlay ul { text-align:left; line-height:2; font-size:16px; color:#ddd; }
#overlay .play { margin-top:22px; font-size:20px; color:#fff; border:2px solid #fff; padding:10px 24px; border-radius:6px; }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MC</h1>
  <div class="sub">a tiny Minecraft-style voxel demo</div>
  <ul>
    <li><b>Move</b> — W A S D</li>
    <li><b>Look</b> — mouse</li>
    <li><b>Jump</b> — Space</li>
    <li><b>Break</b> — left click</li>
    <li><b>Place</b> — right click</li>
    <li><b>Select</b> — 1–7 or mouse wheel</li>
  </ul>
  <div class="play">Click to play</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
"use strict";
// ... game code ...
</script>
</body>
</html>
```

Now the JS. Let me write it.

```js
(function () {
var THREE_global = THREE; // not needed, THREE is global
```

Actually THREE is global from the script tag. Good.

Let me write the game code as a big IIFE or just top-level. I'll use top-level with var declarations.

Let me write:

```js
// ---------- Noise ----------
function vhash(ix, iy, iz) {
  var h = (Math.imul(ix | 0, 374761393) ^ (Math.imul(iy | 0, 668265265)) ^ (Math.imul(iz | 0, 2147043723 || 1)));
  h = (Math.imul(h ^ (h >>> 13), 1274126177));
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

Hmm, iz defaults. Let me just make vhash take x,y and a separate vhash3 for 3D. Actually let me unify: vhash(x,y,[z=0]).

```js
function vhash(x, y, z) {
  z = z || 0;
  var h = (Math.imul(x | 0, 374761393) ^ (Math.imul(y | 0, 668265265)) ^ (Math.imul(z | 0, 2147043723)));
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
```

2D noise:
```js
function smooth(t){ return t*t*(3-2*t); }
function noise2(x, y) {
  var x0 = Math.floor(x) & 255, y0 = Math.floor(y) & 255;
  var x1 = (x0+1)&255, y1 = (y0+1)&255;
  var xf = x - Math.floor(x), yf = y - Math.floor(y);
  var u = smooth(xf), v = smooth(yf);
  var aa = vhash(x0, y0), ba = vhash(x1, y0);
  var ab = vhash(x0, y1), bb = vhash(x1, y1);
  var x1v = aa + u*(ba-aa), x2v = ab + u*(bb-ab);
  return x1v + v*(x2v - x1v);
}
```

Wait, I masked x0 with &255 but then x1=(x0+1)&255. If x0 after &255 is 255, x1=0. That's the wrap-around of the hash table (256 entries). This is fine for value noise as long as we interpolate between the masked indices. Actually the standard permutation-based value noise masks indices to 255 and interpolates vhash(maskedX, maskedY). The smoothing is over the fractional part. This works but the noise isn't continuous across the 256 boundary — but for our purposes (terrain) it's fine, deterministic.

Hmm, but there's a subtlety: I compute x0 = floor(x) & 255. Then base point for interpolation is at (floor(x), floor(y)) in continuous space, but I use hashed values at masked indices. The interpolation weights u,v are based on fractional part. The result is a value between vhash(maskedX,y0) and vhash(maskedX+1,y0) etc. This is correct value noise with a 256-wide permutation field. Good.

Fractal 2D:
```js
function fractal2(x, y) {
  var amp = 1, freq = 1, sum = 0, norm = 0;
  for (var o = 0; o < 4; o++) {
    sum += amp * noise2(x*freq, y*freq);
    norm += amp;
    amp *= 0.5; freq *= 2;
  }
  return sum / norm;
}
```

noise3:
```js
function noise3(x, y, z) {
  var x0 = Math.floor(x)&255, y0 = Math.floor(y)&255, z0 = Math.floor(z)&255;
  var x1=(x0+1)&255, y1=(y0+1)&255, z1=(z0+1)&255;
  var xf=x-Math.floor(x), yf=y-Math.floor(y), zf=z-Math.floor(z);
  var u=smooth(xf), v=smooth(yf), w=smooth(zf);
  var c000=vhash(x0,y0,z0), c100=vhash(x1,y0,z0);
  var c010=vhash(x0,y1,z0), c110=vhash(x1,y1,z0);
  var c001=vhash(x0,y0,z1), c101=vhash(x1,y0,z1);
  var c011=vhash(x0,y1,z1), c111=vhash(x1,y1,z1);
  var l00=c000+u*(c100-c000), l10=c010+u*(c110-c010);
  var l01=c001+u*(c101-c001), l11=c011+u*(c111-c011);
  var m0=l00+v*(l10-l00), m1=l01+v*(l11-l01);
  return m0+w*(m1-m0);
}
function fractal3(x, y, z) {
  var amp=1, freq=1, sum=0, norm=0;
  for (var o=0;o<4;o++){ sum+=amp*noise3(x*freq,y*freq,z*freq); norm+=amp; amp*=0.5; freq*=2; }
  return sum/norm;
}
```

Wait, the &255 masking in vhash — I pass x0 (already masked) to vhash, and vhash does x|0 etc. Fine. But note: I mask inside noise2/noise3 with &255, and vhash internally does x|0 (which for masked values 0-255 is same). Good.

Hmm, but there's a concern: Math.floor(x)&255 — if x is negative, floor gives negative, &255 gives a value 0-255 (JS bitwise & on negative uses two's complement 32-bit, so -1 & 255 = 255). Good, negative coords handled.

### Column generation

```js
function idx(lx, y, lz) { return (lx*80 + y)*16 + lz; }

function generateChunk(cx, cz) {
  var data = new Uint8Array(16*80*16);
  var sx = cx*16, sz = cz*16;
  for (var lx=0; lx<16; lx++) {
    for (var lz=0; lz<16; lz++) {
      var wx = sx+lx, wz = sz+lz;
      var m = fractal2(wx*0.004, wz*0.004);
      var h = fractal2(wx*0.02, wz*0.02);
      var H = Math.floor(5 + m*m*58 + h*10);
      for (var y=0; y<80; y++) {
        var id = 0;
        if (y===0 || y < H-3) {
          id = 3;
        } else if (y >= H-3 && y < H) {
          if (H <= 16) id = 4;
          else if (H >= 37) id = 3;
          else id = 2;
        } else if (y === H) {
          if (H >= 46) id = 7;
          else if (H >= 37) id = 3;
          else if (H <= 16) id = 4;
          else id = 1;
        }
        data[idx(lx,y,lz)] = id;
      }
      // caves
      for (var cy=3; cy < H-2; cy++) {
        if (fractal3(wx*0.09, cy*0.09, wz*0.09) > 0.67) {
          data[idx(lx,cy,lz)] = 0;
        }
      }
      // trees
      if (vhash(wx, wz, 12345) < 0.02 && data[idx(lx,H,lz)] === 1 && H+4 < 80) {
        for (var t=1; t<=4; t++) data[idx(lx,H+t,lz)] = 5;
        var yt = H+4;
        for (var l=0; l<2; l++) {
          var ly = yt+1+l;
          for (var dx=-2; dx<=2; dx++) for (var dz=-2; dz<=2; dz++) {
            var nx=wx+dx*0? ... 
          }
        }
      }
    }
  }
}
```

Wait, in the tree leaves, I use lx±dx (local), not wx. Let me use local coords for tree (within chunk). Trunk at (lx, lz). Leaves at lx+dx, lz+dz.

```js
if (vhash(wx, wz, 12345) < 0.02 && data[idx(lx,H,lz)] === 1 && H+4 < 80) {
  for (var tt=1; tt<=4; tt++) data[idx(lx, H+tt, lz)] = 5; // wood trunk
  var yt = H+4;
  // two 5x5 layers
  for (var l=0; l<2; l++) {
    var ly = yt+1+l;
    for (var llx=-2; llx<=2; llx++) for (var llz=-2; llz<=2; llz++) {
      var alx = lx+llx, alz = lz+llz;
      if (alx>=0 && alx<16 && alz>=0 && alz<16 && ly<80) {
        if (data[idx(alx, ly, alz)] === 0) data[idx(alx, ly, alz)] = 6;
      }
    }
  }
  // 3x3
  var ly3 = yt+3;
  for (var mlx=-1; mlx<=1; mlx++) for (var mlz=-1; mlz<=1; mlz++) {
    var blx=lx+mlx, blz=lz+mlz;
    if (blx>=0 && blx<16 && blz>=0 && blz<16 && ly3<80) {
      if (data[idx(blx, ly3, blz)] === 0) data[idx(blx, ly3, blz)] = 6;
    }
  }
  // 1 on top
  var ly1 = yt+4;
  if (ly1<80 && data[idx(lx, ly1, lz)] === 0) data[idx(lx, ly1, lz)] = 6;
}
```

Good.

### Block helpers

```js
var chunkMap = new Map();
function ckey(cx, cz){ return cx+","+cz; }
function getBlock(wx, wy, wz) {
  var cx = Math.floor(wx/16), cz = Math.floor(wz/16);
  var c = chunkMap.get(ckey(cx,cz));
  if (!c || !c.data) return 0;
  var lx = wx - cx*16, lz = wz - cz*16;
  if (lx<0||lx>=16||lz<0||lz>=16||wy<0||wy>=80) return 0;
  return c.data[idx(lx,wy,lz)];
}
function setBlock(wx, wy, wz, id) {
  var cx = Math.floor(wx/16), cz = Math.floor(wz/16);
  var key = ckey(cx,cz);
  var c = chunkMap.get(key);
  if (!c) { c = {data:null, mesh:null}; chunkMap.set(key, c); }
  if (!c.data) c.data = new Uint8Array(16*80*16);
  var lx = wx-cx*16, lz = wz-cz*16;
  c.data[idx(lx,wy,lz)] = id;
}
```

### Meshing

```js
var FACES = [
  {n:[1,0,0], l:0.8, v:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]]},
  {n:[-1,0,0], l:0.8, v:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]]},
  {n:[0,1,0], l:1.0, v:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]]},
  {n:[0,-1,0], l:0.55, v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
  {n:[0,0,1], l:0.8, v:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]]},
  {n:[0,0,-1], l:0.8, v:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]]},
];
var BLOCK_COLORS = {1:[0.298,0.686,0.314], 2:[0.475,0.333,0.282], 3:[0.620,0.620,0.620], 4:[0.906,0.851,0.659], 5:[0.553,0.431,0.388], 6:[0.180,0.490,0.196], 7:[1,1,1]};
```

Wait, let me compute RGB for each block color properly:
- 1 grass 0x4caf50: r=0x4c=76, g=0xaf=175, b=0x50=80 → (76/255,175/255,80/255) = (0.298,0.686,0.314) ✓
- 2 dirt 0x795548: r=0x79=121, g=0x55=85, b=0x48=72 → (0.475,0.333,0.282) ✓
- 3 stone 0x9e9e9e: (158,158,158) → (0.620,0.620,0.620) ✓
- 4 sand 0xe7d9a8: r=0xe7=231, g=0xd9=217, b=0xa8=168 → (0.906,0.851,0.659) ✓
- 5 wood 0x8d6e63: r=0x8d=141, g=0x6e=110, b=0x63=99 → (0.553,0.431,0.388) ✓
- 6 leaves 0x2e7d32: r=0x2e=46, g=0x7d=125, b=0x32=50 → (0.180,0.490,0.196) ✓
- 7 snow 0xffffff: (1,1,1) ✓

Good.

rebuildChunk:
```js
var meshList = [];
function rebuildChunk(cx, cz) {
  var key = ckey(cx,cz);
  var c = chunkMap.get(key);
  if (!c || !c.data) return;
  if (c.mesh) {
    if (meshList.indexOf(c.mesh) !== -1) meshList.splice(meshList.indexOf(c.mesh),1);
    c.mesh.geometry.dispose();
    scene.remove(c.mesh);
  }
  var data = c.data;
  var positions=[], normals=[], colors=[], indices=[];
  var vi=0;
  for (var lx=0; lx<16; lx++) for (var y=0; y<80; y++) for (var lz=0; lz<16; lz++) {
    var id = data[idx(lx,y,lz)];
    if (id===0) continue;
    var wx=cx*16+lx, wz=cz*16+lz;
    var col = BLOCK_COLORS[id];
    for (var f=0; f<6; f++) {
      var face = FACES[f];
      var nb = getBlock(wx+face.n[0], y+face.n[1], wz+face.n[2]);
      if (nb===0) {
        for (var k=0; k<4; k++) {
          var vo = face.v[k];
          positions.push(wx+vo[0], y+vo[1], wz+vo[2]);
          normals.push(face.n[0], face.n[1], face.n[2]);
          colors.push(col[0]*face.l, col[1]*face.l, col[2]*face.l);
        }
        indices.push(vi, vi+1, vi+2, vi, vi+2, vi+3);
        vi += 4;
      }
    }
  }
  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals,3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors,3));
  geo.setIndex(indices);
  var mesh = new THREE.Mesh(geo, material);
  mesh.position.set(cx*16, 0, cz*16);
  c.mesh = mesh;
  scene.add(mesh);
  meshList.push(mesh);
}
```

Float32BufferAttribute is deprecated in newer three but in r128 it still exists (THREE.Float32BufferAttribute). Yes r128 has it. Good.

### Chunk management

```js
function ensureData(cx, cz) {
  var key = ckey(cx,cz);
  var c = chunkMap.get(key);
  if (!c) { c={data:null,mesh:null}; chunkMap.set(key,c); }
  if (!c.data) c.data = generateChunk(cx,cz);
}

function updateChunks() {
  var pcx = Math.floor(player.pos.x/16), pcz = Math.floor(player.pos.z/16);
  // remove far
  chunkMap.forEach(function(c, key){
    var p = key.split(','); var cx=+p[0], cz=+p[1];
    if (Math.max(Math.abs(cx-pcx), Math.abs(cz-pcz)) > 7) {
      if (c.mesh) { c.mesh.geometry.dispose(); scene.remove(c.mesh); var i=meshList.indexOf(c.mesh); if(i!==-1)meshList.splice(i,1); }
      chunkMap.delete(key);
    }
  });
  // generate within 5, budget 4
  var gen=4;
  gendone: for (var dx=-5; dx<=5; dx++) {
    for (var dz=-5; dz<=5; dz++) {
      if (gen<=0) break gendone;
      if (Math.max(Math.abs(dx),Math.abs(dz))>5) continue;
      ensureData(pcx+dx, pcz+dz);
      gen--;
    }
  }
  // build within 4, budget 2
  var meshB=2;
  buildone: for (var bx=-4; bx<=4; bx++) {
    for (var bz=-4; bz<=4; bz++) {
      if (meshB<=0) break buildone;
      if (Math.max(Math.abs(bx),Math.abs(bz))>4) continue;
      var ccx=pcx+bx, ccz=pcz+bz;
      var cc = chunkMap.get(ckey(ccx,ccz));
      if (!cc || !cc.data || cc.mesh) continue;
      var nE = chunkMap.get(ckey(ccx+1,ccz)), nW=chunkMap.get(ckey(ccx-1,ccz));
      var nN = chunkMap.get(ckey(ccx,ccz+1)), nS=chunkMap.get(ckey(ccx,ccz-1));
      if (nE&&nE.data && nW&&nW.data && nN&&nN.data && nS&&nS.data) {
        rebuildChunk(ccx,ccz);
        meshB--;
      }
    }
  }
}
```

### Edit

```js
function editBlock(bx, by, bz) {
  var cx = Math.floor(bx/16), cz = Math.floor(bz/16);
  rebuildChunk(cx,cz);
  var lx = ((bx%16)+16)%16, lz = ((bz%16)+16)%16;
  if (lx===0) rebuildChunk(cx-1, cz);
  if (lx===15) rebuildChunk(cx+1, cz);
  if (lz===0) rebuildChunk(cx, cz-1);
  if (lz===15) rebuildChunk(cx, cz+1);
}
```

### Player

```js
var player = { pos:new THREE.Vector3(8,0,8), vel:new THREE.Vector3(), yaw:0, pitch:0, onGround:false };
```

Set spawn y later after computing surface height.

```js
function surfaceHeight(wx, wz) {
  var m = fractal2(wx*0.004, wz*0.004);
  var h = fractal2(wx*0.02, wz*0.02);
  return Math.floor(5 + m*m*58 + h*10);
}
```

Spawn: player.pos.y = surfaceHeight(8,8) + 1. But need chunk(0,0) data. Warmup handles it.

### Collision

```js
function collides(pos) {
  var minX=Math.floor(pos.x-0.3), maxX=Math.floor(pos.x+0.3);
  var minY=Math.floor(pos.y), maxY=Math.floor(pos.y+1.8);
  var minZ=Math.floor(pos.z-0.3), maxZ=Math.floor(pos.z+0.3);
  for (var x=minX;x<=maxX;x++) for (var y=minY;y<=maxY;y++) for (var z=minZ;z<=maxZ;z++)
    if (getBlock(x,y,z)!==0) return true;
  return false;
}
```

### Physics update

```js
var GRAV=25, JUMP=8.5, SPEED=5.5;
function updatePlayer(dt) {
  // input
  var fx = -Math.sin(player.yaw), fz = -Math.cos(player.yaw);
  var rx = Math.cos(player.yaw), rz = -Math.sin(player.yaw);
  var mx=0, mz=0;
  if (keys['KeyW']) { mx+=fx; mz+=fz; }
  if (keys['KeyS']) { mx-=fx; mz-=fz; }
  if (keys['KeyD']) { mx+=rx; mz+=rz; }
  if (keys['KeyA']) { mx-=rx; mz-=rz; }
  var len=Math.hypot(mx,mz);
  if (len>0) { mx=mx/len*SPEED; mz=mz/len*SPEED; }
  player.vel.x = mx; player.vel.z = mz;
  player.vel.y -= GRAV*dt;
  if (player.onGround && keys['Space']) player.vel.y = JUMP;
  // move X
  player.pos.x += player.vel.x*dt;
  if (collides(player.pos)) { player.pos.x -= player.vel.x*dt; player.vel.x=0; }
  // move Z
  player.pos.z += player.vel.z*dt;
  if (collides(player.pos)) { player.pos.z -= player.vel.z*dt; player.vel.z=0; }
  // move Y
  player.pos.y += player.vel.y*dt;
  if (collides(player.pos)) {
    player.pos.y -= player.vel.y*dt;
    if (player.vel.y<0) player.onGround=true;
    player.vel.y=0;
  } else if (player.vel.y>=0? false : ...) {
    player.onGround=false;
  }
  ...
}
```

Hmm the onGround reset. Let me set: after moving Y, if collision and moving down → onGround=true; if no collision → onGround=false. But if collision and moving up (jump apex), onGround stays false. Let me:

```js
player.pos.y += player.vel.y*dt;
if (collides(player.pos)) {
  player.pos.y -= player.vel.y*dt;
  if (player.vel.y < 0) player.onGround = true;
  player.vel.y = 0;
} else {
  player.onGround = false;
}
```

But there's an issue: when jumping, initially vel.y>0, we move up, no collision → onGround=false (good). At apex vel.y≈0, moving up slightly, no collision → onGround false. Then falling vel.y<0, eventually collides → onGround=true. Good.

But the "else onGround=false" runs every non-colliding frame including when standing still on ground? No—if standing on ground, moving down by gravity would collide (vel.y<0) → onGround=true. But right after landing, next frame gravity adds downward vel, we move down, collide again → onGround stays true. Good. When would onGround become false while on ground? Only if moving up (jump). So the logic is fine.

Wait, actually there's a subtle bug: when onGround and pressing space, we set vel.y=JUMP. Then we move up. The "else onGround=false" sets onGround=false. Good, leaves ground.

But consider: player on ground, vel.y was set to 0 after landing. Next frame: gravity → vel.y = -25*dt (small negative). Move down → collide → onGround=true. Fine.

Hmm, but the jump: when onGround and space pressed, vel.y=8.5. But this frame we already applied gravity (vel.y = previous - 25dt). If previous vel.y was 0 (just landed), now -25dt, then space sets +8.5. Good.

Fall-off:
```js
if (player.pos.y < -20) { player.pos.set(8, spawnY, 8); player.vel.set(0,0,0); }
```

spawnY computed once.

### Camera

```js
camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
camera.rotation.order = 'YXZ';
camera.rotation.y = player.yaw;
camera.rotation.x = player.pitch;
camera.rotation.z = 0;
```

### Input

```js
var keys = {};
document.addEventListener('keydown', function(e){ keys[e.code]=true; if(e.code==='Space') e.preventDefault(); });
document.addEventListener('keyup', function(e){ keys[e.code]=false; });
document.addEventListener('mousemove', function(e){
  if (!pointerLocked) return;
  player.yaw -= e.movementX * 0.002;
  player.pitch -= e.movementY * 0.002;
  var lim = Math.PI/2 - 0.0001;
  if (player.pitch>lim) player.pitch=lim;
  if (player.pitch<-lim) player.pitch=-lim;
});
```

### Raycast target

```js
var ray = new THREE.Raycaster();
var target=null, place=null;
function updateTarget() {
  highlight.visible=false; target=null; place=null;
  if (!pointerLocked) return;
  camera.getWorldDirection(_dir);
  ray.set(camera.position, _dir);
  var hits = ray.intersectObjects(meshList, false);
  if (hits.length>0 && hits[0].distance<=6) {
    var hit=hits[0];
    var p=hit.point, n=hit.face.normal;
    target = new THREE.Vector3(Math.floor(p.x-n.x*0.5), Math.floor(p.y-n.y*0.5), Math.floor(p.z-n.z*0.5));
    place = new THREE.Vector3(Math.floor(p.x+n.x*0.5), Math.floor(p.y+n.y*0.5), Math.floor(p.z+n.z*0.5));
    highlight.visible=true;
    highlight.position.set(target.x+0.5, target.y+0.5, target.z+0.5);
  }
}
```

_dir reused vector.

### Break/place click

```js
document.addEventListener('mousedown', function(e){
  if (!pointerLocked) return;
  if (e.button===0) { // break
    if (target && target.y>0) {
      setBlock(target.x,target.y,target.z, 0);
      editBlock(target.x,target.y,target.z);
    }
  } else if (e.button===2) { // place
    if (place && getBlock(place.x,place.y,place.z)===0 && !overlapsPlayer(place)) {
      setBlock(place.x,place.y,place.z, selected);
      editBlock(place.x,place.y,place.z);
    }
  }
});
```

overlapsPlayer:
```js
function overlapsPlayer(b) {
  var bmin=new THREE.Vector3(b.x, b.y, b.z);
  var bmax=new THREE.Vector3(b.x+1, b.y+1, b.z+1);
  var pbox = new THREE.Box3(new THREE.Vector3(player.pos.x-0.3, player.pos.y, player.pos.z-0.3), new THREE.Vector3(player.pos.x+0.3, player.pos.y+1.8, player.pos.z+0.3));
  return new THREE.Box3(bmin,bmax).intersectsBox(pbox);
}
```

### Context menu + wheel + hotbar

```js
document.addEventListener('contextmenu', function(e){ e.preventDefault(); });
document.addEventListener('wheel', function(e){
  if (!pointerLocked) return;
  var dir = e.deltaY>0 ? 1 : -1;
  selected = ((selected-1+dir+7)%7)+1;
  refreshHotbar();
});
document.addEventListener('keydown', function(e){
  var m = /^Digit([1-7])$/.exec(e.code);
  if (m) { selected=+m[1]; refreshHotbar(); }
});
```

Wait, keydown for Digit handled twice (once for preventDefault space, once for digit). Let me combine. Actually separate listeners are fine; the digit one triggers for Digit1-7.

### Hotbar UI

```js
var HOTBAR = [1,2,3,4,5,6,7];
var selected = 1;
var hotbarEl = document.getElementById('hotbar');
function refreshHotbar() {
  hotbarEl.innerHTML = '';
  for (var i=0;i<7;i++){
    var slot = document.createElement('div');
    slot.className = 'slot' + (HOTBAR[i]===selected ? ' selected':'');
    var sw = document.createElement('div'); sw.className='swatch';
    sw.style.background = 'rgb('+rgb255(BLOCK_COLORS[HOTBAR[i]][0])+','+rgb255(BLOCK_COLORS[HOTBAR[i]][1])+','+rgb255(BLOCK_COLORS[HOTBAR[i]][2])+')';
    var num = document.createElement('span'); num.className='num'; num.textContent=(i+1);
    slot.appendChild(sw); slot.appendChild(num);
    hotbarEl.appendChild(slot);
  }
}
function rgb255(v){ return Math.round(v*255); }
```

### Overlay & pointer lock

```js
var overlay = document.getElementById('overlay');
var pointerLocked = false;
overlay.addEventListener('click', function(){ canvas.requestPointerLock(); });
document.addEventListener('pointerlockchange', function(){
  pointerLocked = (document.pointerLockElement === canvas);
  overlay.style.display = pointerLocked ? 'none' : 'block';
});
```

### Clouds, water

```js
var clouds = [];
for (var i=0;i<25;i++){
  var cmesh = new THREE.Mesh(new THREE.BoxGeometry(16,4,10), new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.9, depthWrite:false}));
  cmesh.position.set(0,90,0);
  cmesh.userData = { ox:(vhash(i,0)-0.5)*160, oz:(vhash(i,1,99)-0.5)*160 };
  scene.add(cmesh); clouds.push(cmesh);
}
var water = new THREE.Mesh(new THREE.PlaneGeometry(480,480), new THREE.MeshLambertMaterial({color:0x3388ff, transparent:true, opacity:0.75, depthWrite:false}));
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);
```

Update:
```js
function updateClouds(dt){
  for (var i=0;i<clouds.length;i++){
    var c=clouds[i];
    c.position.x = player.pos.x + c.userData.ox;
    c.position.z = player.pos.z + c.userData.oz;
    c.userData.ox += dt*1.5;
    if (c.userData.ox > 90) c.userData.ox -= 180;
  }
  water.position.x = player.pos.x;
  water.position.z = player.pos.z;
}
```

### Highlight

```js
var highlight = new THREE.LineSegments(
  new THREE.EdgeGeometry(new THREE.BoxGeometry(1.005,1.005,1.005)),
  new THREE.LineBasicMaterial({color:0x000000})
);
scene.add(highlight);
```

### Scene, renderer

```js
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);
var camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 400);
var material = new THREE.MeshLambertMaterial({vertexColors:true});
var ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.4, 1, 0.3); // direction normalized internally
scene.add(sun);
var canvas = document.createElement('canvas');
document.body.appendChild(canvas);
var renderer = new THREE.WebGLRenderer({canvas});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
```

### Main loop

```js
var clock = new THREE.Clock();
function loop(){
  requestAnimationFrame(loop);
  var dt = Math.min(clock.getDelta(), 0.1);
  updatePlayer(dt);
  updateTarget();
  updateChunks();
  updateClouds(dt);
  camera.position.set(player.pos.x, player.pos.y+1.62, player.pos.z);
  camera.rotation.order='YXZ';
  camera.rotation.y=player.yaw;
  camera.rotation.x=player.pitch;
  renderer.render(scene, camera);
}
```

### Init / warmup

```js
function warmup(R){
  for (var dx=-R;dx<=R;dx++) for (var dz=-R;dz<=R;dz++) ensureData(pcx+dx, pcz+dz);
  for (var dx2=-R;dx2<=R;dx2++) for (var dz2=-R;dz2<=R;dz2++){
    var ccx=pcx+dx2, ccz=pcz+dz2;
    var c=chunkMap.get(ckey(ccx,ccz));
    if (c && !c.mesh && c.data &&
        chunkMap.get(ckey(ccx+1,ccz))&&chunkMap.get(ckey(ccx+1,ccz)).data &&
        chunkMap.get(ckey(ccx-1,ccz))&&chunkMap.get(ckey(ccx-1,ccz)).data &&
        chunkMap.get(ckey(ccx,ccz+1))&&chunkMap.get(ckey(ccx,ccz+1)).data &&
        chunkMap.get(ckey(ccx,ccz-1))&&chunkMap.get(ckey(ccx,ccz-1)).data){
      rebuildChunk(ccx,ccz);
    }
  }
}
```

pcx, pcz = floor(8/16)=0, floor(8/16)=0. So spawn chunk (0,0).

Warmup R=3: generate 7x7=49 chunks, build those with neighbors ready (radius 2 → 5x5=25, plus edges). Should render spawn area.

Then loop starts.

### Resize

```js
window.addEventListener('resize', function(){
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
```

### Order of operations

I need to define everything, then compute spawnY (needs chunk data), warmup, set player.pos.y, then start loop.

Let me set spawnY = surfaceHeight(8,8)+1 after warmup ensures chunk(0,0) data. Actually surfaceHeight doesn't need data, just noise. But to be consistent with actual terrain, better to sample actual data. Let me sample actual: find surface at (8,8) by scanning chunk(0,0) data for the topmost non-air... no, the surface block. Let me just use surfaceHeight for spawn, it's deterministic and matches.

Actually, let me spawn at the actual block surface to be safe: after warmup, scan column (8,8) from top down for first non-air, set feet to that+1. But surfaceHeight should match. Let me use actual:

```js
function findSurface(wx, wz){
  var cx=Math.floor(wx/16), cz=Math.floor(wz/16);
  var lx=wx-cx*16, lz=wz-cz*16;
  for (var y=79; y>=0; y--){ if (getBlock(cx*16+lx, y, cz*16+lz)!==0) return y+1; }
  return 30;
}
```

This returns the y of the topmost non-air block +1 (feet position). Uses actual data. Good. Call after warmup.

Let me set player.pos.y = findSurface(8,8).

Then spawn.

### Let me assemble and write the final file.

Let me reconsider potential runtime errors:
- Math.imul with large constants: fine in JS.
- vhash with iz default: `z = z || 0` — if z is 0, uses 0. But vhash(wx, wz) called with 2 args → iz undefined → z=0. Good. vhash(i,0) in clouds → iz=0. Good.
- EdgeGeometry exists in r128. Yes.
- Float32BufferAttribute exists in r128. Yes.
- LineBasicMaterial, LineSegments exist. Yes.
- Box3, Vector3 exist. Yes.

Let me double check the tree hash: vhash(wx, wz, 12345). Fine.

Let me reconsider the "fits inside the chunk" for trees. H+4 < 80 ensures trunk top (H+4) is within bounds. Leaves extend to yt+4 = H+8. Need H+8 < 80. Since H max 73, H+8=81 > 80 possible! If H=73, yt=77, ly1=yt+4=81 → 81<80 false, so top leaf skipped. ly3=80 → 80<80 false, 3x3 skipped. ly=yt+1=78, ly=yt+2=79 → 79<80 true, so two 5x5 layers at 78,79. Hmm H=73 is rare (needs m,h near 1). Most H are lower. Anyway, bounds checks prevent crashes. Good.

Actually wait, for H=73: trunk at H+1..H+4 = 74,75,76,77. yt=77. 5x5 layers at 78,79. ly3=80 (skip). ly1=81 (skip). So leaves only at 78,79. Fine, no crash.

Most trees have H around 20-45, so H+8 up to 53, well within 80. Good.

### Let me reconsider the water plane opacity and fog. Water opacity 0.75, transparent, depthWrite false. Renders after opaque blocks. Fog applies. Good.

### Directional light position normalization: DirectionalLight uses position as the light direction (normalized internally each frame). Setting position (0.4,1,0.3) is fine.

### Let me write it all out cleanly now.

Actually, I realize there might be an issue with `camera.getWorldDirection` when the camera hasn't been positioned/rotated yet in the first frame. But I set rotation before calling it in the loop. In updateTarget I call getWorldDirection after setting rotation (I set rotation before render, but updateTarget is called before setting camera position/rotation in my loop order). Let me reorder: set camera position/rotation BEFORE updateTarget, so the raycast uses correct direction.

Let me reorder loop:
```js
updatePlayer(dt);
updateChunks();
updateClouds(dt);
camera.position.set(...); camera.rotation...;
updateTarget(); // now camera has correct direction
renderer.render(...);
```

Yes, set camera first, then updateTarget. Good.

### Also, `_dir` vector for getWorldDirection. Define once.

### Let me also make sure pointer lock works: canvas.requestPointerLock(). In some browsers need to be user gesture — click provides. Good.

### Also, I should add `tabindex` or focus? Not needed for requestPointerLock.

### Let me finalize.

Let me also reconsider: the spec says "Clicking the start overlay requests pointer lock". So overlay click → requestPointerLock. Good. And "it reappears whenever pointer lock is released" → pointerlockchange handler sets overlay display. Good.

### One more: "Suppress the browser context menu." Added contextmenu preventDefault. Good. Also on canvas specifically. Document-level covers it.

### Let me write the final HTML now.

Let me make sure I include everything and it's syntactically correct.

Actually, I want to double-check the face winding once more with a concrete rendering. I verified cross products point outward for all 6 faces. Three.js culls back faces (default) and renders front faces (CCW). Since our faces are CCW when viewed from outside (verified via cross product = outward normal), they'll be seen. Good.

Wait, let me re-examine: cross(e1, e3) where e1 = v1-v0, e3 = v3-v0. For CCW winding v0→v1→v2→v3, the normal should be cross(v1-v0, v3-v0)? Let me verify the relationship. For a quad v0,v1,v2,v3 (CCW), the normal = cross(v1-v0, v2-v0)? or cross(v1-v0, v3-v0)?

The two triangles are (v0,v1,v2) and (v0,v2,v3). Normal of triangle (v0,v1,v2) = cross(v1-v0, v2-v0). For CCW this points outward.

I computed cross(v1-v0, v3-v0) earlier and got outward normals. But the actual triangle normal is cross(v1-v0, v2-v0). Are these the same direction? For a planar quad, cross(v1-v0, v2-v0) and cross(v1-v0, v3-v0) should be parallel (both perpendicular to the face) and same direction if the quad is planar and convex. Let me verify for +X face:
v0=(1,0,0), v1=(1,1,0), v2=(1,1,1), v3=(1,0,1).
cross(v1-v0, v2-v0) = cross((0,1,0),(0,1,1)) = (1*1-0*1, 0*0-0*1, 0*1-1*0) = (1,0,0). ✓ Outward.
Good, matches. So winding is correct.

### Final assembly.

Let me write the complete file. I'll be thorough.

Let me reconsider the `ensureData` returning and the generation budget. In updateChunks, generation budget 4, but ensureData generates if data is null. After warmup, most nearby chunks have data. As player moves, new chunks need data, generated at 4/frame. Good.

There's a subtle issue: the generation loop iterates dx from -5 to 5, dz -5 to 5, but skips if distance > 5 (redundant since loop already ≤5). The `continue` is harmless. Budget 4 limits how many are generated per frame. Good.

Building loop: budget 2, within 4, needs 4 neighbors with data. Good.

### Let me also double check: when player is at a chunk border, pcx/pcz computed from pos. Fine.

### Also, "Falling below y −20 teleports back to spawn." Handled.

### Let me write.

Actually, I realize the warmup function references pcx, pcz which I'll define. Let me define pcx,pcz = (0,0) (spawn chunk) explicitly.

Also, I want to make sure the game doesn't start with an empty screen before warmup finishes. Warmup is synchronous and quick for R=3. Then loop starts. Good.

Let me also guard: if WebGL isn't available it'd error, but assume it is.

Let me write the final code. I'll inline everything.

Let me reconsider variable naming to avoid conflicts with the IIFE. I'll use a plain script (no IIFE) with function declarations and vars. Since it's a single script at end of body, and THREE is global, this works.

Let me write it out fully now.

Actually, I want to reconsider the fog near/far: "matching fog (about 40 to 110)". THREE.Fog(color, near, far) = Fog(0x87ceeb, 40, 110). Good.

Camera far is 400. Fog far 110. Objects beyond 110 fully fogged. Good.

### Let me also reconsider: should directional light intensity 0.8 with MeshLambert produce enough brightness? Ambient 0.65 + directional 0.8 (dot product with normal). For top faces (normal up, light direction ~ (0.4,1,0.3) normalized ≈ (0.34,0.85,0.27)), dot = 0.85. So directional contributes 0.8*0.85=0.68. Total ~1.33 * vertexColor. Could be slightly over 1 but Lambert clamps? Actually MeshLambertMaterial multiplies, values can exceed 1 (clamped by gamma? In r128 without ToneMapping, values >1 just clip to white). Tops might look a bit blown but fine. Acceptable.

### Final code.

Let me write it all.

Wait, I should double-check `new THREE.Float32BufferAttribute`. In r128, this exists (deprecated in favor of BufferAttribute in later versions, but present in r128). Yes.

Also `THREE.EdgeGeometry` — exists in r128. Yes.

Also, I use `geo.setIndex(indices)` with a plain array — fine.

Let me also ensure I dispose old geometries properly to avoid leaks, but for a demo it's fine.

Let me write the final file.

Let me reconsider: I reference `material`, `scene`, `camera` in rebuildChunk and elsewhere — they're defined before the loop. Order in code: define scene, camera, material, lights, renderer, canvas, THEN define functions, THEN warmup, THEN loop. Functions can reference variables declared later due to hoisting? Function declarations are hoisted, but variable assignments (var scene = ...) are NOT hoisted (the assignment happens where written, though declaration is hoisted). So if rebuildChunk references `scene` but scene is assigned after rebuildChunk is defined, that's fine because rebuildChunk is only CALLED after scene is assigned (during warmup/loop). The reference resolves at call time. Good.

But `var material = new THREE.MeshLambertMaterial(...)` must be assigned before rebuildChunk is called. I'll assign it early. Good.

Let me lay out the code order:
1. Noise functions
2. Constants (FACES, BLOCK_COLORS, HOTBAR, physics vars)
3. chunkMap, getBlock, setBlock, idx, generateChunk
4. scene, camera, material, lights, renderer, canvas setup
5. meshList, rebuildChunk
6. ensureData, updateChunks, editBlock
7. player, collides, updatePlayer, findSurface
8. ray, target, place, updateTarget, overlapsPlayer
9. clouds, water, highlight, updateClouds
10. input handlers (keys, mouse, click, wheel, contextmenu, pointerlock, overlay)
11. hotbar UI, refreshHotbar
12. warmup, spawn, loop, resize
13. start

Since functions are hoisted, I can define them in any order as long as variables they reference are assigned before first call. Let me just write logically and assign scene/camera/material early.

Let me write it all now in one go.

Let me reconsider `camera.getWorldDirection(_dir)` — _dir must be defined. Define `var _dir = new THREE.Vector3();` before loop.

Also for the raycast, `ray.set(camera.position, _dir)` — camera.position is Vector3, _dir is Vector3. ray.set copies them. Good.

Alright, writing.

Let me also reconsider: when the player places a block, I check getBlock(place)===0. But place could be at y=0? If placing at y=0, that's fine (spec doesn't forbid placing at y=0, only breaking at y=0). Actually the spec says break "not at y 0". For place, no such restriction. But placing at y=0 stone cell... it's air (we check getBlock===0), so place there. Fine. Though y=0 is always stone normally, so getBlock(…,0,…) is 3 (stone) unless caved. So placing at y=0 only if caved. Edge case, fine.

Let me also make sure place cell doesn't place inside the player (overlapsPlayer check). Good.

### Writing final code now.

Let me carefully write the hotbar swatch colors using the BLOCK_COLORS.

Also, I realize I should double check: the hotbar shows block colors. Slot colors: grass(green), dirt(brown), stone(gray), sand(tan), wood(brownish), leaves(dark green), snow(white). Good.

Let me write.

Actually, let me reconsider whether to gate WASD movement under pointerLocked. If not locked, keys tracked but movement not applied. Good. But when you click to play and lock, movement starts. Good.

Also, the overlay should be hidden when locked. pointerlockchange handler does that.

Let me also add: on keydown for arrow keys or others, preventDefault to avoid scrolling. Not necessary since overflow hidden. Skip.

Final code below.

Oh wait, I need to double-check the `wheel` event for selecting: "Select with keys 1–7 or the mouse wheel (wraps around)." My wheel handler wraps selected 1-7. Good. But wheel fires even when not locked; I gate under pointerLocked. When unlocked, overlay covers, so wheel interactions go to overlay. Fine.

Also, keys 1-7: I gate under pointerLocked? The spec implies selection during play. Let me gate keydown digit selection under pointerLocked too, to avoid changing selection while on overlay. Actually, if not locked, overlay is on top, so keydown might still reach document. Let me gate under pointerLocked. Hmm, but then you can't select while overlay shown — that's fine, you click to play first.

Wait, but the overlay click transitions to locked. Before that, no selection needed. Gate under pointerLocked. Good.

Let me finalize.

Let me reconsider the spawn height computation once more. findSurface scans from y=79 down for first non-air at column (8,8). Returns y+1. This is the feet position (top of highest block +1). Good. If somehow all air (shouldn't happen), fallback 30.

Alright.

Let me also verify: player spawns at x=8, z=8, which is in chunk (0,0) at local (8,8). findSurface(8,8) uses chunk(0,0) data. Warmup generates chunk(0,0). Good.

Writing now. Let me produce the final HTML.

Let me reconsider one detail in updateChunks removal: `chunkMap.forEach` while deleting — Map.forEach with delete during iteration is safe in JS (deletes are allowed). Good.

Also, I iterate chunkMap.forEach for removal each frame — O(chunks). Fine.

Let me write.

Actually, let me reconsider the meshList management on removal: I do meshList.indexOf(c.mesh) and splice. But c.mesh might be null. Guard with `if (c.mesh)`. Good.

Let me also make sure that when I dispose geometry on removal and rebuild, no dangling references. Fine.

Final code:

Let me write it completely and carefully.

I'll now also reconsider: do I need `renderer.setPixelRatio`? It helps crispness. Include it. But on some systems devicePixelRatio could be huge; fine.

Let me write.

One more: the `sun` directional light — I set position but for it to affect, material must use it. MeshLambertMaterial uses lights by default (it's a lit material). Good. Ambient + directional included via onBeforeRender / default lights. Actually, lights added to scene are included automatically for lit materials. Good.

Also, I should add the lights to scene: scene.add(ambient), scene.add(sun). Done.

Writing final now.

Let me make sure about `THREE.LineBasicMaterial` — exists. And `LineSegments`. Good.

Let me produce the code.

Actually, I realize there may be an issue with `camera.getWorldDirection` returning a direction that, combined with ray.set, then intersectObjects. The ray direction should be normalized. getWorldDirection returns normalized vector. Good.

Also, ray distance: intersectObjects returns hits sorted by distance. hits[0] is nearest. distance <= 6 check. Good.

Let me finalize and write the complete file.

I think I've covered everything. Let me write it out.

Let me reconsider the total length — it'll be long but that's expected.

Let me write the complete mc.html.
</think>

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>mc.html</title>
<style>
html, body { width:100%; height:100%; overflow:hidden; background:#000; margin:0; padding:0; }
canvas { display:block; position:fixed; inset:0; }
#crosshair { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10; }
#crosshair::before, #crosshair::after { content:""; position:absolute; background:#ffffff; box-shadow:0 0 3px rgba(0,0,0,0.9); }
#crosshair::before { top:50%; left:50%; width:18px; height:2px; margin:-1px 0 0 -9px; }
#crosshair::after  { top:50%; left:50%; width:2px; height:18px; margin:-9px 0 0 -1px; }
#hotbar {
  position:fixed; bottom:18px; left:50%; transform:translateX(-50%);
  display:flex; gap:4px; padding:4px; background:rgba(0,0,0,0.55);
  border-radius:6px; pointer-events:none; z-index:10;
}
.slot { width:46px; height:46px; border:2px solid rgba(255,255,255,0.25); border-radius:4px; position:relative; }
.slot .swatch { position:absolute; inset:5px; border:1px solid rgba(0,0,0,0.4); border-radius:2px; }
.slot .num { position:absolute; bottom:1px; right:3px; color:#ddd; font:12px/1 monospace; text-shadow:0 0 2px #000; }
.slot.selected { border-color:#ffffff; box-shadow:0 0 6px rgba(255,255,255,0.75); }
#overlay {
  position:fixed; inset:0; background:rgba(0,0,0,0.82); color:#fff;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  text-align:center; z-index:20; cursor:pointer; font-family:"Segoe UI",Arial,sans-serif;
}
#overlay h1 { font-size:52px; margin:0 0 8px; letter-spacing:2px; }
#overlay .sub { color:#bbb; margin-bottom:18px; }
#overlay ul { text-align:left; line-height:2; font-size:16px; color:#ddd; }
#overlay .play { margin-top:22px; font-size:20px; color:#fff; border:2px solid #fff; padding:10px 24px; border-radius:6px; }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MC</h1>
  <div class="sub">a tiny Minecraft-style voxel demo</div>
  <ul>
    <li><b>Move</b> — W A S D</li>
    <li><b>Look</b> — mouse</li>
    <li><b>Jump</b> — Space</li>
    <li><b>Break</b> — left click</li>
    <li><b>Place</b> — right click</li>
    <li><b>Select</b> — 1–7 or mouse wheel</li>
  </ul>
  <div class="play">Click to play</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
"use strict";

/* ------------------------------------------------------------------ */
/*  Deterministic value noise                                          */
/* ------------------------------------------------------------------ */
function vhash(x, y, z) {
  z = z || 0;
  var h = (Math.imul(x | 0, 374761393) ^ (Math.imul(y | 0, 668265265)) ^ (Math.imul(z | 0, 2147043723)));
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296;
}
function smooth(t) { return t * t * (3 - 2 * t); }
function noise2(x, y) {
  var x0 = Math.floor(x) & 255, y0 = Math.floor(y) & 255;
  var x1 = (x0 + 1) & 255, y1 = (y0 + 1) & 255;
  var xf = x - Math.floor(x), yf = y - Math.floor(y);
  var u = smooth(xf), v = smooth(yf);
  var aa = vhash(x0, y0), ba = vhash(x1, y0);
  var ab = vhash(x0, y1), bb = vhash(x1, y1);
  var p = aa + u * (ba - aa), q = ab + u * (bb - ab);
  return p + v * (q - p);
}
function noise3(x, y, z) {
  var x0 = Math.floor(x) & 255, y0 = Math.floor(y) & 255, z0 = Math.floor(z) & 255;
  var x1 = (x0 + 1) & 255, y1 = (y0 + 1) & 255, z1 = (z0 + 1) & 255;
  var xf = x - Math.floor(x), yf = y - Math.floor(y), zf = z - Math.floor(z);
  var u = smooth(xf), w = smooth(yf), s = smooth(zf);
  var c000 = vhash(x0, y0, z0), c100 = vhash(x1, y0, z0);
  var c010 = vhash(x0, y1, z0), c110 = vhash(x1, y1, z0);
  var c001 = vhash(x0, y0, z1), c101 = vhash(x1, y0, z1);
  var c011 = vhash(x0, y1, z1), c111 = vhash(x1, y1, z1);
  var l00 = c000 + u * (c100 - c000), l10 = c010 + u * (c110 - c010);
  var l01 = c001 + u * (c101 - c001), l11 = c011 + u * (c111 - c011);
  var m0 = l00 + w * (l10 - l00), m1 = l01 + w * (l11 - l01);
  return m0 + s * (m1 - m0);
}
function fractal2(x, y) {
  var amp = 1, freq = 1, sum = 0, norm = 0;
  for (var o = 0; o < 4; o++) { sum += amp * noise2(x * freq, y * freq); norm += amp; amp *= 0.5; freq *= 2; }
  return sum / norm;
}
function fractal3(x, y, z) {
  var amp = 1, freq = 1, sum = 0, norm = 0;
  for (var o = 0; o < 4; o++) { sum += amp * noise3(x * freq, y * freq, z * freq); norm += amp; amp *= 0.5; freq *= 2; }
  return sum / norm;
}

/* ------------------------------------------------------------------ */
/*  Block tables                                                       */
/* ------------------------------------------------------------------ */
var FACES = [
  { n: [ 1, 0, 0], l: 0.8, v: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  { n: [-1, 0, 0], l: 0.8, v: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  { n: [ 0, 1, 0], l: 1.0, v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { n: [ 0,-1, 0], l: 0.55, v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { n: [ 0, 0, 1], l: 0.8, v: [[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
  { n: [ 0, 0,-1], l: 0.8, v: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]] }
];
var BLOCK_COLORS = {
  1: [0.298, 0.686, 0.314],
  2: [0.475, 0.333, 0.282],
  3: [0.620, 0.620, 0.620],
  4: [0.906, 0.851, 0.659],
  5: [0.553, 0.431, 0.388],
  6: [0.180, 0.490, 0.196],
  7: [1.000, 1.000, 1.000]
};
var HOTBAR = [1, 2, 3, 4, 5, 6, 7];

/* ------------------------------------------------------------------ */
/*  Chunk storage + block access                                       */
/* ------------------------------------------------------------------ */
var chunkMap = new Map();
function idx(lx, y, lz) { return (lx * 80 + y) * 16 + lz; }
function ckey(cx, cz) { return cx + "," + cz; }

function getBlock(wx, wy, wz) {
  var cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
  var c = chunkMap.get(ckey(cx, cz));
  if (!c || !c.data) return 0;
  var lx = wx - cx * 16, lz = wz - cz * 16;
  if (lx < 0 || lx >= 16 || lz < 0 || lz >= 16 || wy < 0 || wy >= 80) return 0;
  return c.data[idx(lx, wy, lz)];
}
function setBlock(wx, wy, wz, id) {
  var cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
  var key = ckey(cx, cz);
  var c = chunkMap.get(key);
  if (!c) { c = { data: null, mesh: null }; chunkMap.set(key, c); }
  if (!c.data) c.data = new Uint8Array(16 * 80 * 16);
  var lx = wx - cx * 16, lz = wz - cz * 16;
  c.data[idx(lx, wy, lz)] = id;
}

function generateChunk(cx, cz) {
  var data = new Uint8Array(16 * 80 * 16);
  var sx = cx * 16, sz = cz * 16;
  for (var lx = 0; lx < 16; lx++) {
    for (var lz = 0; lz < 16; lz++) {
      var wx = sx + lx, wz = sz + lz;
      var m = fractal2(wx * 0.004, wz * 0.004);
      var h = fractal2(wx * 0.02, wz * 0.02);
      var H = Math.floor(5 + m * m * 58 + h * 10);
      for (var y = 0; y < 80; y++) {
        var id = 0;
        if (y === 0 || y < H - 3) {
          id = 3;
        } else if (y >= H - 3 && y < H) {
          if (H <= 16) id = 4;
          else if (H >= 37) id = 3;
          else id = 2;
        } else if (y === H) {
          if (H >= 46) id = 7;
          else if (H >= 37) id = 3;
          else if (H <= 16) id = 4;
          else id = 1;
        }
        data[idx(lx, y, lz)] = id;
      }
      for (var cy = 3; cy < H - 2; cy++) {
        if (fractal3(wx * 0.09, cy * 0.09, wz * 0.09) > 0.67) data[idx(lx, cy, lz)] = 0;
      }
      if (vhash(wx, wz, 12345) < 0.02 && data[idx(lx, H, lz)] === 1 && H + 4 < 80) {
        for (var t = 1; t <= 4; t++) data[idx(lx, H + t, lz)] = 5;
        var yt = H + 4;
        for (var l = 0; l < 2; l++) {
          var ly = yt + 1 + l;
          for (var a = -2; a <= 2; a++) for (var b = -2; b <= 2; b++) {
            var alx = lx + a, alz = lz + b;
            if (alx >= 0 && alx < 16 && alz >= 0 && alz < 16 && ly < 80)
              if (data[idx(alx, ly, alz)] === 0) data[idx(alx, ly, alz)] = 6;
          }
        }
        var ly3 = yt + 3;
        for (var c2 = -1; c2 <= 1; c2++) for (var d2 = -1; d2 <= 1; d2++) {
          var blx = lx + c2, blz = lz + d2;
          if (blx >= 0 && blx < 16 && blz >= 0 && blz < 16 && ly3 < 80)
            if (data[idx(blx, ly3, blz)] === 0) data[idx(blx, ly3, blz)] = 6;
        }
        var ly1 = yt + 4;
        if (ly1 < 80 && data[idx(lx, ly1, lz)] === 0) data[idx(lx, ly1, lz)] = 6;
      }
    }
  }
  return data;
}

/* ------------------------------------------------------------------ */
/*  Scene, camera, material, lights, renderer                          */
/* ------------------------------------------------------------------ */
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
var material = new THREE.MeshLambertMaterial({ vertexColors: true });

var ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.4, 1, 0.3);
scene.add(sun);

var canvas = document.createElement('canvas');
document.body.appendChild(canvas);
var renderer = new THREE.WebGLRenderer({ canvas: canvas });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

/* ------------------------------------------------------------------ */
/*  Chunk meshing                                                      */
/* ------------------------------------------------------------------ */
var meshList = [];
function rebuildChunk(cx, cz) {
  var key = ckey(cx, cz);
  var c = chunkMap.get(key);
  if (!c || !c.data) return;
  if (c.mesh) {
    var i = meshList.indexOf(c.mesh);
    if (i !== -1) meshList.splice(i, 1);
    c.mesh.geometry.dispose();
    scene.remove(c.mesh);
  }
  var data = c.data;
  var positions = [], normals = [], colors = [], indices = [];
  var vi = 0;
  for (var lx = 0; lx < 16; lx++) {
    for (var y = 0; y < 80; y++) {
      for (var lz = 0; lz < 16; lz++) {
        var id = data[idx(lx, y, lz)];
        if (id === 0) continue;
        var wx = cx * 16 + lx, wz = cz * 16 + lz;
        var col = BLOCK_COLORS[id];
        for (var f = 0; f < 6; f++) {
          var face = FACES[f];
          if (getBlock(wx + face.n[0], y + face.n[1], wz + face.n[2]) === 0) {
            for (var k = 0; k < 4; k++) {
              var vo = face.v[k];
              positions.push(wx + vo[0], y + vo[1], wz + vo[2]);
              normals.push(face.n[0], face.n[1], face.n[2]);
              colors.push(col[0] * face.l, col[1] * face.l, col[2] * face.l);
            }
            indices.push(vi, vi + 1, vi + 2, vi, vi + 2, vi + 3);
            vi += 4;
          }
        }
      }
    }
  }
  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices);
  var mesh = new THREE.Mesh(geo, material);
  mesh.position.set(cx * 16, 0, cz * 16);
  c.mesh = mesh;
  scene.add(mesh);
  meshList.push(mesh);
}

function ensureData(cx, cz) {
  var key = ckey(cx, cz);
  var c = chunkMap.get(key);
  if (!c) { c = { data: null, mesh: null }; chunkMap.set(key, c); }
  if (!c.data) c.data = generateChunk(cx, cz);
}

function updateChunks() {
  var pcx = Math.floor(player.pos.x / 16), pcz = Math.floor(player.pos.z / 16);

  // remove chunks farther than 7
  chunkMap.forEach(function (c, key) {
    var p = key.split(','), cx = +p[0], cz = +p[1];
    if (Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz)) > 7) {
      if (c.mesh) {
        c.mesh.geometry.dispose();
        scene.remove(c.mesh);
        var i = meshList.indexOf(c.mesh);
        if (i !== -1) meshList.splice(i, 1);
      }
      chunkMap.delete(key);
    }
  });

  // generate block data for chunks within 5 (max 4 per frame)
  var gen = 4;
  genLoop: for (var dx = -5; dx <= 5; dx++) {
    for (var dz = -5; dz <= 5; dz++) {
      if (gen <= 0) break genLoop;
      if (Math.max(Math.abs(dx), Math.abs(dz)) > 5) continue;
      ensureData(pcx + dx, pcz + dz);
      gen--;
    }
  }

  // build meshes for chunks within 4 whose 4 neighbors already have data (max 2 per frame)
  var mb = 2;
  buildLoop: for (var ex = -4; ex <= 4; ex++) {
    for (var ez = -4; ez <= 4; ez++) {
      if (mb <= 0) break buildLoop;
      if (Math.max(Math.abs(ex), Math.abs(ez)) > 4) continue;
      var ccx = pcx + ex, ccz = pcz + ez;
      var c = chunkMap.get(ckey(ccx, ccz));
      if (!c || !c.data || c.mesh) continue;
      var nE = chunkMap.get(ckey(ccx + 1, ccz)), nW = chunkMap.get(ckey(ccx - 1, ccz));
      var nN = chunkMap.get(ckey(ccx, ccz + 1)), nS = chunkMap.get(ckey(ccx, ccz - 1));
      if (nE && nE.data && nW && nW.data && nN && nN.data && nS && nS.data) {
        rebuildChunk(ccx, ccz);
        mb--;
      }
    }
  }
}

function editBlock(bx, by, bz) {
  var cx = Math.floor(bx / 16), cz = Math.floor(bz / 16);
  rebuildChunk(cx, cz);
  var lx = ((bx % 16) + 16) % 16, lz = ((bz % 16) + 16) % 16;
  if (lx === 0) rebuildChunk(cx - 1, cz);
  if (lx === 15) rebuildChunk(cx + 1, cz);
  if (lz === 0) rebuildChunk(cx, cz - 1);
  if (lz === 15) rebuildChunk(cx, cz + 1);
}

/* ------------------------------------------------------------------ */
/*  Player                                                             */
/* ------------------------------------------------------------------ */
var player = { pos: new THREE.Vector3(8, 0, 8), vel: new THREE.Vector3(), yaw: 0, pitch: 0, onGround: false };
var GRAV = 25, JUMP = 8.5, SPEED = 5.5;

function collides(pos) {
  var minX = Math.floor(pos.x - 0.3), maxX = Math.floor(pos.x + 0.3);
  var minY = Math.floor(pos.y), maxY = Math.floor(pos.y + 1.8);
  var minZ = Math.floor(pos.z - 0.3), maxZ = Math.floor(pos.z + 0.3);
  for (var x = minX; x <= maxX; x++)
    for (var y = minY; y <= maxY; y++)
      for (var z = minZ; z <= maxZ; z++)
        if (getBlock(x, y, z) !== 0) return true;
  return false;
}

function findSurface(wx, wz) {
  var cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
  var lx = wx - cx * 16, lz = wz - cz * 16;
  for (var y = 79; y >= 0; y--)
    if (getBlock(cx * 16 + lx, y, cz * 16 + lz) !== 0) return y + 1;
  return 30;
}

function updatePlayer(dt) {
  var fx = -Math.sin(player.yaw), fz = -Math.cos(player.yaw);
  var rx = Math.cos(player.yaw), rz = -Math.sin(player.yaw);
  var mx = 0, mz = 0;
  if (keys['KeyW']) { mx += fx; mz += fz; }
  if (keys['KeyS']) { mx -= fx; mz -= fz; }
  if (keys['KeyD']) { mx += rx; mz += rz; }
  if (keys['KeyA']) { mx -= rx; mz -= rz; }
  var len = Math.hypot(mx, mz);
  if (len > 0) { mx = mx / len * SPEED; mz = mz / len * SPEED; }
  player.vel.x = mx; player.vel.z = mz;
  player.vel.y -= GRAV * dt;
  if (player.onGround && keys['Space']) player.vel.y = JUMP;

  player.pos.x += player.vel.x * dt;
  if (collides(player.pos)) { player.pos.x -= player.vel.x * dt; player.vel.x = 0; }

  player.pos.z += player.vel.z * dt;
  if (collides(player.pos)) { player.pos.z -= player.vel.z * dt; player.vel.z = 0; }

  player.pos.y += player.vel.y * dt;
  if (collides(player.pos)) {
    player.pos.y -= player.vel.y * dt;
    if (player.vel.y < 0) player.onGround = true;
    player.vel.y = 0;
  } else {
    player.onGround = false;
  }

  if (player.pos.y < -20) { player.pos.set(8, spawnY, 8); player.vel.set(0, 0, 0); }
}

/* ------------------------------------------------------------------ */
/*  Targeting / raycast                                                */
/* ------------------------------------------------------------------ */
var ray = new THREE.Raycaster();
var target = null, place = null;
var _dir = new THREE.Vector3();

function updateTarget() {
  highlight.visible = false;
  target = null;
  place = null;
  if (!pointerLocked) return;
  camera.getWorldDirection(_dir);
  ray.set(camera.position, _dir);
  var hits = ray.intersectObjects(meshList, false);
  if (hits.length > 0 && hits[0].distance <= 6) {
    var p = hits[0].point, n = hits[0].face.normal;
    target = new THREE.Vector3(Math.floor(p.x - n.x * 0.5), Math.floor(p.y - n.y * 0.5), Math.floor(p.z - n.z * 0.5));
    place = new THREE.Vector3(Math.floor(p.x + n.x * 0.5), Math.floor(p.y + n.y * 0.5), Math.floor(p.z + n.z * 0.5));
    highlight.visible = true;
    highlight.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
  }
}

function overlapsPlayer(b) {
  var pbox = new THREE.Box3(
    new THREE.Vector3(player.pos.x - 0.3, player.pos.y, player.pos.z - 0.3),
    new THREE.Vector3(player.pos.x + 0.3, player.pos.y + 1.8, player.pos.z + 0.3)
  );
  return new THREE.Box3(
    new THREE.Vector3(b.x, b.y, b.z),
    new THREE.Vector3(b.x + 1, b.y + 1, b.z + 1)
  ).intersectsBox(pbox);
}

/* ------------------------------------------------------------------ */
/*  Sky, clouds, water, highlight                                      */
/* ------------------------------------------------------------------ */
var clouds = [];
for (var ci = 0; ci < 25; ci++) {
  var cmesh = new THREE.Mesh(
    new THREE.BoxGeometry(16, 4, 10),
    new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.9, depthWrite: false })
  );
  cmesh.position.set(0, 90, 0);
  cmesh.userData = { ox: (vhash(ci, 0) - 0.5) * 160, oz: (vhash(ci, 1, 99) - 0.5) * 160 };
  scene.add(cmesh);
  clouds.push(cmesh);
}
var water = new THREE.Mesh(
  new THREE.PlaneGeometry(480, 480),
  new THREE.MeshLambertMaterial({ color: 0x3388ff, transparent: true, opacity: 0.75, depthWrite: false })
);
water.rotation.x = -Math.PI / 2;
water.position.y = 14.3;
scene.add(water);

var highlight = new THREE.LineSegments(
  new THREE.EdgeGeometry(new THREE.BoxGeometry(1.005, 1.005, 1.005)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
scene.add(highlight);

function updateWorlds(dt) {
  for (var i = 0; i < clouds.length; i++) {
    var c = clouds[i];
    c.position.x = player.pos.x + c.userData.ox;
    c.position.z = player.pos.z + c.userData.oz;
    c.userData.ox += dt * 1.5;
    if (c.userData.ox > 90) c.userData.ox -= 180;
  }
  water.position.x = player.pos.x;
  water.position.z = player.pos.z;
}

/* ------------------------------------------------------------------ */
/*  Input                                                              */
/* ------------------------------------------------------------------ */
var keys = {};
var pointerLocked = false;
var selected = 1;

document.addEventListener('keydown', function (e) {
  keys[e.code] = true;
  if (e.code === 'Space') e.preventDefault();
  if (pointerLocked) {
    var m = /^Digit([1-7])$/.exec(e.code);
    if (m) { selected = +m[1]; refreshHotbar(); }
  }
});
document.addEventListener('keyup', function (e) { keys[e.code] = false; });
document.addEventListener('mousemove', function (e) {
  if (!pointerLocked) return;
  player.yaw -= e.movementX * 0.002;
  player.pitch -= e.movementY * 0.002;
  var lim = Math.PI / 2 - 0.0001;
  if (player.pitch > lim) player.pitch = lim;
  else if (player.pitch < -lim) player.pitch = -lim;
});
document.addEventListener('mousedown', function (e) {
  if (!pointerLocked) return;
  if (e.button === 0) {
    if (target && target.y > 0) {
      setBlock(target.x, target.y, target.z, 0);
      editBlock(target.x, target.y, target.z);
    }
  } else if (e.button === 2) {
    if (place && getBlock(place.x, place.y, place.z) === 0 && !overlapsPlayer(place)) {
      setBlock(place.x, place.y, place.z, selected);
      editBlock(place.x, place.y, place.z);
    }
  }
});
document.addEventListener('wheel', function (e) {
  if (!pointerLocked) return;
  var dir = e.deltaY > 0 ? 1 : -1;
  selected = ((selected - 1 + dir + 7) % 7) + 1;
  refreshHotbar();
});
document.addEventListener('contextmenu', function (e) { e.preventDefault(); });

/* ------------------------------------------------------------------ */
/*  Hotbar UI                                                          */
/* ------------------------------------------------------------------ */
var hotbarEl = document.getElementById('hotbar');
function refreshHotbar() {
  hotbarEl.innerHTML = '';
  for (var i = 0; i < 7; i++) {
    var slot = document.createElement('div');
    slot.className = 'slot' + (HOTBAR[i] === selected ? ' selected' : '');
    var sw = document.createElement('div');
    sw.className = 'swatch';
    var col = BLOCK_COLORS[HOTBAR[i]];
    sw.style.background = 'rgb(' + Math.round(col[0] * 255) + ',' + Math.round(col[1] * 255) + ',' + Math.round(col[2] * 255) + ')';
    var num = document.createElement('span');
    num.className = 'num';
    num.textContent = (i + 1);
    slot.appendChild(sw);
    slot.appendChild(num);
    hotbarEl.appendChild(slot);
  }
}
refreshHotbar();

/* ------------------------------------------------------------------ */
/*  Overlay / pointer lock                                             */
/* ------------------------------------------------------------------ */
var overlay = document.getElementById('overlay');
overlay.addEventListener('click', function () { canvas.requestPointerLock(); });
document.addEventListener('pointerlockchange', function () {
  pointerLocked = (document.pointerLockElement === canvas);
  overlay.style.display = pointerLocked ? 'none' : 'block';
});

/* ------------------------------------------------------------------ */
/*  Startup                                                            */
/* ------------------------------------------------------------------ */
var pcx = 0, pcz = 0;
function warmup(R) {
  for (var dx = -R; dx <= R; dx++)
    for (var dz = -R; dz <= R; dz++)
      ensureData(pcx + dx, pcz + dz);
  for (var ax = -R; ax <= R; ax++)
    for (var az = -R; az <= R; az++) {
      var wx = pcx + ax, wz = pcz + az;
      var c = chunkMap.get(ckey(wx, wz));
      if (c && !c.mesh && c.data &&
          chunkMap.get(ckey(wx + 1, wz)) && chunkMap.get(ckey(wx + 1, wz)).data &&
          chunkMap.get(ckey(wx - 1, wz)) && chunkMap.get(ckey(wx - 1, wz)).data &&
          chunkMap.get(ckey(wx, wz + 1)) && chunkMap.get(ckey(wx, wz + 1)).data &&
          chunkMap.get(ckey(wx, wz - 1)) && chunkMap.get(ckey(wx, wz - 1)).data) {
        rebuildChunk(wx, wz);
      }
    }
}

warmup(3);
spawnY = findSurface(8, 8);
player.pos.set(8, spawnY, 8);

window.addEventListener('resize', function () {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

var clock = new THREE.Clock();
function loop() {
  requestAnimationFrame(loop);
  var dt = Math.min(clock.getDelta(), 0.1);

  updatePlayer(dt);
  updateChunks();
  updateWorlds(dt);

  camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
  camera.rotation.order = 'YXZ';
  camera.rotation.y = player.yaw;
  camera.rotation.x = player.pitch;
  camera.rotation.z = 0;

  updateTarget();

  renderer.render(scene, camera);
}
loop();
</script>
</body>
</html>
```