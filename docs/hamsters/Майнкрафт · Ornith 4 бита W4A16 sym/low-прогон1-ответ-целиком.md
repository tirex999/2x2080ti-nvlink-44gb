Let me build this carefully. It's a big spec. Let me write the complete mc.html.

Let me think through all the components:

1. HTML structure: canvas, crosshair, hotbar, start overlay
2. CSS: fullscreen, styling
3. JS: Three.js setup, chunk system, terrain generation, meshing, player physics, controls, break/place, clouds, water

Let me write it step by step.

Key details from spec:

**Blocks**: IDs 0-7 with colors.
- 0 air
- 1 grass 0x4caf50
- 2 dirt 0x795548
- 3 stone 0x9e9e9e
- 4 sand 0xe7d9a8
- 5 wood 0x8d6e63
- 6 leaves 0x2e7d32
- 7 snow 0xffffff

Unit cubes, vertex colors, ONE shared MeshLambertMaterial. Fake lighting: top 1.0, sides 0.8, bottom 0.55.

**Chunks & endless world**: Chunks 16x16 columns, 80 blocks high. Global Map key "cx,cz", value: Uint8Array of block IDs plus mesh. Block helpers: chunk = floor(world/16), local = world - chunk*16. Negative coords work. Reading missing chunk or y outside 0-79 returns air.

Each frame: generate block data for chunks within 5 of player (max 4/frame); build meshes for chunks within 4 whose 4 neighbors have data (max 2/frame); chunks farther than 7, remove mesh, dispose geometry, delete entry.

**Meshing**: One BufferGeometry per chunk. Loop all non-air blocks, for each of 6 sides check neighbor; if air, add face (2 triangles) to flat position/normal/color arrays. World coords for vertices, mesh at origin. Keep chunk meshes in global array for raycasting. Rebuild function for a chunk.

Wait - MeshLambertMaterial with vertex colors and fake lighting baked into colors. So we bake the lighting factor into the color values. Good.

**Terrain (deterministic)**: value noise. Integer-coordinate hash 0-1 (mix with large prime multipliers and xor-shifts). Smoothed 2D noise via bilinear interpolation with smoothstep. 4 octaves into fractal noise. 3D version for caves.

Column height: m = fractal(coords*0.004), h = fractal(coords*0.02), H = floor(5 + m*m*58 + h*10).

Column fill:
- y=0 = unbreakable stone
- below H-3 = stone
- the 3 layers under the surface: dirt (sand if H≤16, stone if H≥37)
- surface: snow if H≥46, stone if H≥37, sand if H≤16, otherwise grass

Wait, let me re-read. "below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

So the top surface block is at y = H-1 (since below H-3 is stone, then 3 layers under surface... hmm). Let me think. If surface is at level S, then "the 3 layers under the surface" would be S-1, S-2, S-3. And "below H-3 stone" means y < H-3 is stone. So surface S = H-3? Then 3 layers under surface: S-1=H-4, S-2=H-5, S-3=H-6. Hmm, that overlaps with "below H-3 stone".

Actually let me reconsider. Maybe surface is at H-1. Let's see: "below H-3 stone" → y ≤ H-4 is stone (or y < H-3). "the 3 layers under the surface" → if surface at H-1, layers under are H-2, H-3, H-4. That conflicts with "below H-3 stone" which says H-4 is stone.

Hmm. Let me interpret it more loosely. I think:
- y = 0: stone
- For y from 1 to H-1: mostly stone, with the top few being dirt/sand.

Let me define:
- y = 0: stone
- y < H-3: stone
- The 3 layers just below surface: dirt (or sand/stone). Surface at H-1. So H-2, H-3, H-4 are the "3 layers under the surface"? But "below H-3 stone" contradicts.

Actually maybe surface is at H. Let me try surface at H-1.

Let me just go with a clean interpretation:
- y = 0: stone (unbreakable)
- if y <= H-4: stone ("below H-3")
- if y in {H-3, H-2, H-1}: these are the 3 layers under surface → dirt/sand/stone based on rule
- if y == H-1... wait that's included above.

Hmm, there's ambiguity about whether surface is H-1 or H. Let me re-read once more very carefully.

"Column fill: y 0 = unbreakable stone; below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

OK here's my interpretation:
- y = 0: stone
- y < H-3 (i.e., y <= H-4): stone
- The 3 layers under the surface: these are y = H-3, H-2, H-1? No wait.

Actually "the 3 layers under the surface" — the surface is the topmost block. So 3 layers under it = surface-1, surface-2, surface-3. If surface is at y = H-1, then 3 layers under = H-2, H-3, H-4. But "below H-3 stone" says H-4 is stone. Contradiction again.

If surface is at y = H, then 3 layers under = H-1, H-2, H-3. And "below H-3 stone" = y <= H-4 is stone. That's consistent! Surface at H, dirt layers at H-1, H-2, H-3, and stone below (y <= H-4).

Wait but then "below H-3 stone" includes y = H-3 itself? "below H-3" typically means y < H-3, i.e., y <= H-4. So H-3 is NOT below H-3, it's part of the dirt layers. So dirt layers = H-1, H-2, H-3 (3 layers). Surface = H. Below (y <= H-4) = stone. 

Hmm, but actually let me reconsider. Let me reconsider: maybe surface at H-1.

Actually, you know what, let me just pick a consistent interpretation and make it work. I'll go with:
- y = 0: stone
- y in [1, H-1]: 
  - if y <= H-4: stone
  - else (y in H-3, H-2, H-1): dirt-type (3 layers)
- y = H: surface type (snow/stone/sand/grass)

Wait, that gives surface at H and 3 dirt layers at H-1, H-2, H-3. And "below H-3 stone" = y <= H-4. Consistent! Good.

But hold on, what if H is small like H=5 (from formula floor(5 + m*m*58 + h*10), minimum is 5 when m=h=0, but they're noise so >0). Actually m and h are in [0,1], so H >= 5. With m=m*58... m*m*58, min 0. So H ranges from 5 up. For H=5: surface at y=5, dirt at y=2,3,4 (H-3=2, H-2=3, H-1=4), stone at y=0 and y<=H-4=1. So y=1 stone, y=2,3,4 dirt, y=5 surface. Good.

Actually wait, "below H-3 stone" — for H=5, H-3=2, below 2 is y<=1. So y=0,1 stone. Then dirt at 2,3,4. Surface at 5. That's 3 dirt layers. 

Let me now handle the edge: what about when H-4 < 1? E.g., H=5, H-4=1, so y<=1 stone. Fine. H could be as low as 5. y=0 always stone regardless.

Now, the "3 layers under the surface" material rule: "dirt (sand if H ≤ 16, stone if H ≥ 37)". So sub-surface material:
- sand if H <= 16
- stone if H >= 37
- else dirt

And surface:
- snow if H >= 46
- stone if H >= 37
- sand if H <= 16
- else grass

Caves: for y between 3 and H-2, if 3D noise at position*0.09 exceeds 0.67, set air.

Trees: on grass (surface is grass), when per-column hash < 0.02 and trunk fits inside chunk: 4 wood up, leaves as 5x5 layer twice, then 3x3, then 1 on top (only into air).

Let me think about tree placement. "when a per-column hash < 0.02 and the trunk fits inside the chunk". So we need the tree at column (x,z) to fit within the chunk boundaries. Trunk height 4, so we need enough space. Let me place trees only if the column is far enough from chunk edges. Actually the trunk is at the column itself, 4 blocks up (not horizontal spread issue). The leaves are 5x5 centered on trunk at certain heights. So horizontally we need the column to be at least 2 away from chunk edge (since 5x5 = ±2). Let me check "trunk fits inside the chunk" — maybe just means the column itself, but to be safe I'll require distance >= 2 from edges. Actually let me just check the column is within chunk (always true since we're generating per chunk) and leaves don't go outside chunk horizontally. To avoid gaps, require 2 <= x_local <= 13 and 2 <= z_local <= 13. Hmm, but spec says "trunk fits inside the chunk". Let me be a bit lenient but ensure leaves stay in chunk: require x_local in [2,13], z_local in [2,13].

Actually, trees spanning chunk boundaries would look fine anyway since adjacent chunks render. But leaves going outside chunk means they'd be culled (not rendered in this chunk). Since we only build mesh for chunks whose neighbors have data, and we mesh independently, a tree near edge would have leaves cut off. To avoid that, better to constrain. But it's minor. Let me constrain to keep within chunk for cleanliness. I'll use x_local in [2,13] and z_local in [2,13].

Tree structure:
- 4 wood blocks up from surface+1 to surface+4.
- leaves as a 5x5 layer twice (at trunk top, two layers of 5x5 centered)
- then 3x3
- then 1 on top

Let me define heights. Surface at y = H (grass). Trunk from H+1 to H+4 (4 wood). Then leaves:
- 5x5 layer at y=H+5 and y=H+6 (two layers)
- 3x3 layer at y=H+7
- 1 block at y=H+8

Let me implement leaf placement: for a given layer size s (odd, s=5 or 3), half = s/2 (floor). Place leaves at dx in [-half, half], dz in [-half, half], only into air.

For 5x5: half=2, dx,dz in [-2,2]. Two layers.
For 3x3: half=1.
For 1: just center.

**Player & controls**: PerspectiveCamera fov 75, far 400, rotation order YXZ, yaw/pitch. Pointer lock on start overlay click. Mouse look only while locked, sensitivity 0.002, clamp pitch. Player box: half-width 0.3, height 1.8, eye 1.62. Spawn above terrain at x=8,z=8. Gravity 25, jump Space velocity 8.5, WASD 5.5 relative to yaw. Axis-separated collision against all non-air blocks (move per axis, revert on overlap; landing sets on-ground). Falling below y-20 teleports to spawn.

**Break & place**: crosshair center. Each frame raycast from camera center (max dist 6) against chunk meshes. From hit point p and face normal n: break target = floor(p - n*0.5), place cell = floor(p + n*0.5), per component. Outline targeted block with black wireframe box. Only while pointer locked: left click sets target to air (not at y=0); right click places selected block if cell is air and doesn't overlap player. After edit rebuild chunk, and also neighbor chunk if block on chunk border. Suppress context menu.

**Hotbar**: bottom center, 7 slots (grass, dirt, stone, sand, wood, leaves, snow), each small square in block color with number, on dark semi-transparent bar. Selected slot white border. Keys 1-7 or mouse wheel (wraps).

**Sky, clouds, water**: Sky-blue bg 0x87ceeb with matching fog (40 to 110). Ambient 0.65 + directional 0.8. ~25 flat white transparent boxes as clouds at height ~90, drifting and wrapping around player. Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame.

**UI**: fullscreen start overlay with title, controls list, "Click to play"; reappears when pointer lock released. Body no margins, fullscreen canvas, resize handled.

Let me now write the code.

Let me plan the data structures:

```js
const CHUNK_SIZE = 16;
const CHUNK_HEIGHT = 80;
const chunks = new Map(); // key "cx,cz" -> { data: Uint8Array, mesh: Mesh }
```

Block helpers:
```js
function getChunk(cx, cz) {
  return chunks.get(cx + "," + cz);
}
function getBlock(x, y, z) {
  if (y < 0 || y >= CHUNK_HEIGHT) return 0;
  const cx = Math.floor(x / CHUNK_SIZE);
  const lz = ((z % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE;
  const lx = ((x % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE;
  // careful with negative modulo
  const chunk = getChunk(cx, cz);
  if (!chunk) return 0;
  return chunk.data[lx + lz * CHUNK_SIZE];
}
```

Wait, need to compute cx and cz correctly for negatives. `Math.floor(x/16)` works for negatives. Then local = x - cx*16, which is always in [0,15]. That's cleaner than modulo:
```js
const cx = Math.floor(x / CHUNK_SIZE);
const cz = Math.floor(z / CHUNK_SIZE);
const lx = x - cx * CHUNK_SIZE;
const lz = z - cz * CHUNK_SIZE;
```
This guarantees lx, lz in [0,15]. Good.

setBlock:
```js
function setBlock(x, y, z, id) {
  if (y < 0 || y >= CHUNK_HEIGHT) return;
  const cx = Math.floor(x / CHUNK_SIZE);
  const cz = Math.floor(z / CHUNK_SIZE);
  const lx = x - cx * CHUNK_SIZE;
  const lz = z - cz * CHUNK_SIZE;
  const chunk = getChunk(cx, cz);
  if (!chunk) return;
  chunk.data[lx + lz * CHUNK_SIZE] = id;
  rebuildChunk(cx, cz);
}
```

Now terrain generation. Hash function:
```js
function hash2(ix, iz) {
  // integer hash -> 0..1
  let h = ix * 374761393 + iz * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
```
Using large prime multipliers and xor-shifts. Good.

Value noise 2D:
```js
function valueNoise2(x, z) {
  const xi = Math.floor(x), zi = Math.floor(z);
  const xf = x - xi, zf = z - zi;
  const v00 = hash2(xi, zi);
  const v10 = hash2(xi+1, zi);
  const v01 = hash2(xi, zi+1);
  const v11 = hash2(xi+1, zi+1);
  const u = smoothstep(xf);
  const w = smoothstep(zf);
  const top = v00*(1-u) + v10*u;
  const bot = v01*(1-u) + v11*u;
  return top*(1-w) + bot*w;
}
```

smoothstep:
```js
function smoothstep(t){ return t*t*(3-2*t); }
```

Fractal (octaves):
```js
function fractal2(x, z, octaves, persistence) {
  let amp = 1, freq = 1, sum = 0, norm = 0;
  for (let i = 0; i < octaves; i++) {
    sum += amp * valueNoise2(x*freq, z*freq);
    norm += amp;
    amp *= persistence;
    freq *= 2;
  }
  return sum / norm;
}
```

3D noise for caves:
```js
function hash3(ix, iy, iz) { ... }
function valueNoise3(x,y,z) { trilinear }
function fractal3(x,y,z) { ... }
```

Let me implement hash3:
```js
function hash3(ix, iy, iz) {
  let h = ix * 374761393 + iy * 668265263 + iz * 1274126177;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
```

valueNoise3 with trilinear:
```js
function valueNoise3(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x-xi, yf=y-yi, zf=z-zi;
  const c = (dx,dy,dz) => hash3(xi+dx, yi+dy, zi+dz);
  const a = c(0,0,0), b=c(1,0,0), d=c(0,1,0), e=c(1,1,0), f=c(0,0,1), g=c(1,0,1), hh=c(0,1,1), k=c(1,1,1);
  const su = t=>t*t*(3-2*t);
  const u=su(xf), v=su(yf), w=su(zf);
  const nx00 = a*(1-u)+b*u; const nx10 = d*(1-u)+e*u;
  const nx01 = f*(1-u)+g*u; const nx11 = hh*(1-u)+k*u;
  const ny0 = nx00*(1-v)+nx10*v; const ny1 = nx01*(1-v)+nx11*v;
  return ny0*(1-w)+ny1*w;
}
function fractal3(x,y,z,octaves,persistence){...}
```

Now terrain generation for a chunk:
```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
  const idx = (x,y,z) => x + y*CHUNK_SIZE + z... 
```
Wait, need consistent indexing. Let me use index = lx + lz*CHUNK_SIZE + ly*CHUNK_SIZE*CHUNK_SIZE. Or simpler: index = (ly * CHUNK_SIZE + lz) * CHUNK_SIZE + lx. Let me define helper.

Actually let me store as data[x + z*16 + y*16*16]? Let me use:
```js
function di(x, y, z) { return (y * CHUNK_SIZE + z) * CHUNK_SIZE + x; }
```
where x,z in [0,15], y in [0,79].

Generation:
```js
function generateChunkData(cx, cz) {
  const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
  for (let lz = 0; lz < CHUNK_SIZE; lz++) {
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      const wx = cx*CHUNK_SIZE + lx;
      const wz = cz*CHUNK_SIZE + lz;
      const m = fractal2(wx*0.004, wz*0.004);
      const h = fractal2(wx*0.02, wz*0.02);
      const H = Math.floor(5 + m*m*58 + h*10);
      for (let y = 0; y < H; y++) {
        let id = 0;
        if (y === 0) id = 3; // stone unbreakable
        else if (y < H-3) id = 3; // stone
        else if (y < H) {
          // 3 layers under surface
          if (H <= 16) id = 4; // sand
          else if (H >= 37) id = 3; // stone
          else id = 2; // dirt
        } else {
          // surface at y == H
          if (H >= 46) id = 7; // snow
          else if (H >= 37) id = 3; // stone
          else if (H <= 16) id = 4; // sand
          else id = 1; // grass
        }
        data[di(lx, y, lz)] = id;
      }
      // caves
      for (let y = 3; y < H-2; y++) {
        const n = fractal3(wx*0.09, y*0.09, wz*0.09);
        if (n > 0.67) data[di(lx, y, lz)] = 0;
      }
      // trees
      const surfId = data[di(lx, H-1, lz)]; // surface block
      if (surfId === 1) { // grass
        const th = hash2(wx*7 + 1, wz*11 + 3); // per-column hash
        if (th < 0.02 && lx>=2 && lx<=13 && lz>=2 && lz<=13) {
          const base = H; // ground level (surface at H-1, so top of ground is H-1, trunk starts H)
          // Wait, surface block is at y = H-1. Let me recompute.
        }
      }
    }
  }
  return data;
}
```

Wait, I need to reconcile surface height. Earlier I decided surface at y=H. Let me recheck.

I had:
- y=0: stone
- y <= H-4: stone
- y in {H-3, H-2, H-1}: 3 dirt layers
- y == H: surface

So the surface block is at y = H, and the last dirt block is at H-1. So "surface" block index = di(lx, H, lz). And the block just below (H-1) is dirt.

Hmm wait, but then the number of blocks filled is H+1 (y from 0 to H inclusive). And the "3 layers under surface" are H-1, H-2, H-3. And "below H-3 stone" means y < H-3 → y <= H-4 is stone. So:
- y <= H-4: stone (this includes y=0)
- y in {H-3, H-2, H-1}: dirt-type
- y == H: surface

Let me rewrite:
```js
for (let y = 0; y <= H; y++) {
  let id;
  if (y <= H-4) id = 3; // stone (includes y=0)
  else if (y <= H-1) {
    // 3 layers under surface
    if (H <= 16) id = 4;
    else if (H >= 37) id = 3;
    else id = 2;
  } else {
    // y == H: surface
    if (H >= 46) id = 7;
    else if (H >= 37) id = 3;
    else if (H <= 16) id = 4;
    else id = 1;
  }
  data[di(lx, y, lz)] = id;
}
```

Wait, but the spec says "y 0 = unbreakable stone; below H−3 stone". With my formula y <= H-4 is stone. Is y=0 always covered? H >= 5, so H-4 >= 1, thus y=0 <= H-4 always true. Good, y=0 is stone.

But wait, "below H-3" — does it mean y < H-3 (y <= H-4) or y <= H-3? "Below H-3" should be strictly less than H-3, i.e., y <= H-4. So y = H-3 is not below, it's a dirt layer. That matches my "3 layers under surface" = H-3, H-2, H-1. 

Hmm, but actually, let me reconsider whether surface is at H or H-1. Let me reconsider the phrase "the 3 layers under the surface". If surface at H-1, then 3 layers under = H-2, H-3, H-4. And "below H-3 stone" = y <= H-4 stone. Conflict at H-4 (dirt vs stone). If surface at H, 3 layers under = H-1,H-2,H-3, below H-3 = y<=H-4 stone. No conflict. So surface at H. Good, my interpretation stands.

But actually, thinking about it more, maybe the intended reading is: surface at H-1. Because "below H-3" might mean y <= H-3 (inclusive-ish), and "3 layers under surface" would be H-2, H-3, H-4. Ugh, ambiguous.

Let me just go with surface at H. It's clean and consistent. The exact surface height doesn't hugely matter for gameplay.

Hmm, wait. Let me reconsider. Actually there might be an even simpler reading: the surface is at level H-1, and there are 3 blocks of dirt below it (H-2, H-3, H-4), and everything below H-4 is stone. Let me check "below H-3 stone": if this means y <= H-4... no. If surface at H-1 and dirt at H-2,H-3,H-4, then "below H-3" can't include H-4 as it's dirt.

I'll go with surface at H. Moving on. Actually, let me reconsider one more time because it affects where trees spawn and where water (y=14) shows.

With H = floor(5 + m²·58 + h·10). m in [0,1] so m² in [0,1], m²·58 in [0,58]. h in [0,1], h·10 in [0,10]. So H in [5, 73]. Average maybe around 5 + 0.33·58 + 0.5·10 ≈ 5+19+5 = 29. So terrain average height ~29. Water at 14.3 is well below average, so it'll show in low areas (beaches/lakes). Good.

Now trees: surface block at y=H (id=1 if grass). Trunk goes up from H+1 to H+4. Leaves above. Let me implement:

```js
// after filling terrain
if (surfId === 1 && th < 0.02 && lx>=2 && lx<=13 && lz>=2 && lz<=13) {
  // trunk
  for (let ty = 1; ty <= 4; ty++) {
    const y = H + ty;
    if (y < CHUNK_HEIGHT) data[di(lx, y, lz)] = 5; // wood
  }
  // leaves
  const leafBase = H + 5;
  // two 5x5 layers
  for (let ly = 0; ly < 2; ly++) {
    placeLeaves(data, lx, lz, leafBase + ly, 2);
  }
  // 3x3
  placeLeaves(data, lx, lz, leafBase + 2, 1);
  // 1 on top
  const ytop = leafBase + 3;
  if (ytop < CHUNK_HEIGHT) data[di(lx, ytop, lz)] = 6;
}
```

placeLeaves:
```js
function placeLeaves(data, lx, lz, y, half) {
  for (let dx = -half; dx <= half; dx++) {
    for (let dz = -half; dz <= half; dz++) {
      const nx = lx + dx, nz = lz + dz;
      if (nx < 0 || nx >= CHUNK_SIZE || nz < 0 || nz >= CHUNK_SIZE) continue;
      if (data[di(nx, y, nz)] === 0) data[di(nx, y, nz)] = 6;
    }
  }
}
```

Wait, but the leaves at the two 5x5 layers would overlap with the 3x3 and top. That's fine, we just overwrite air. But actually the 3x3 at leafBase+2 and the second 5x5 at leafBase+1 — the 3x3 sits on top of 5x5. And top at leafBase+3. Good.

Hmm, but "leaves as a 5x5 layer twice" — two full 5x5 layers. Then "then 3x3" then "1 on top". My placement: 5x5 at leafBase, 5x5 at leafBase+1, 3x3 at leafBase+2, 1 at leafBase+3. Good.

Actually wait, should the 3x3 and top overwrite existing leaves? They're placed after, and placeLeaves only fills air, but for the 3x3 and top I directly assign. Since those positions are above the 5x5 layers (higher y), they're air unless... no, they're at higher y so they were air. Fine. Actually the top block at leafBase+3 center — direct assign is fine.

Now meshing. Build one BufferGeometry per chunk. For each non-air block, check 6 neighbors; if neighbor is air, add face.

Vertex colors: bake lighting. Top faces (normal +y): 1.0. Side faces (±x, ±z): 0.8. Bottom (-y): 0.55.

Colors: base color * factor. Colors are 0xRRGGBB. Let me precompute colored vertices.

Let me define block colors:
```js
const BLOCK_COLORS = [
  null,
  0x4caf50, // grass
  0x795548, // dirt
  0x9e9e9e, // stone
  0xe7d9a8, // sand
  0x8d6e63, // wood
  0x2e7d32, // leaves
  0xffffff, // snow
];
```

For each block face, the 4 corners have the same color. I'll add 6 vertices per quad (2 triangles: 0,1,2, 2,3,4... wait standard: vertices 0,1,2 form triangle 1, and 2,3,0? Let me do proper quad: 6 vertices, indices [0,1,2, 2,3,0] but BufferGeometry with separate index array. Actually for MeshLambertMaterial I can use indexed geometry.

Let me build position, normal, color arrays, and index array.

Quad vertices for a face. Let me define the 4 corners CCW when viewed from outside (correct winding for front-facing).

For each direction:
- +X face (normal (1,0,0)): the face at x+1. Corners (in y,z): Let me define. The block occupies [x,x+1]×[y,y+1]×[z,z+1]. +X face is at X=x+1. Its 4 corners: (x+1, y, z), (x+1, y, z+1), (x+1, y+1, z+1), (x+1, y+1, z). Winding: viewed from +X (looking in -X direction), need CCW. Let me just pick winding that faces outward. Standard approach:

Let me define a function that given a face returns 4 points and normal, ensuring correct winding.

Actually, let me use a known-correct set. For a cube face, I'll define:

+Y (top), normal (0,1,0):
points: (0,1,1),(1,1,1),(1,1,0),(0,1,0) → but need CCW from outside (above). Looking down from +Y, CCW... Let me just trust a standard cube generation.

Let me use this common scheme (from many voxel tutorials):

```
const faces = [
  { dir: [ 1, 0, 0], corners: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]] }, // +X
  { dir: [-1, 0, 0], corners: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]] }, // -X
  { dir: [ 0, 1, 0], corners: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] }, // +Y (top)
  { dir: [ 0,-1, 0], corners: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] }, // -Y (bottom)
  { dir: [ 0, 0, 1], corners: [[1,0,1],[1,1,1],[0,1,1],[0,0,1]] }, // +Z
  { dir: [ 0, 0,-1], corners: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]] }, // -Z
];
```

These are relative offsets (0 or 1). For each, add base (block x,y,z). Winding should be correct (CCW from outside). I've seen these schemes work. Let me verify one: +Y top, corners [[0,1,1],[1,1,1],[1,1,0],[0,1,0]]. Viewed from above (+Y looking down), points: (0,1,1)→(1,1,1)→(1,1,0)→(0,1,0). In the XZ plane from above (with Z up... hmm hard to visualize). I'll trust it; if backfaces appear wrong I can flip. Actually for robustness, since we only render faces toward air and use default material (side: double?), let me set material side to FrontSide and rely on correct winding. If issues, use DoubleSide. To be safe and avoid culling issues, I could use `material.side = THREE.DoubleSide`. But that's slightly less efficient. The spec says one shared MeshLambertMaterial. Doesn't specify side. Let me use FrontSide with correct winding, but I'm fairly confident in the scheme above. Actually, to be safe against winding mistakes, let me use DoubleSide. Hmm, but DoubleSide can look odd with lighting. For a voxel game, FrontSide is standard. Let me go with the scheme and FrontSide. Actually, let me reduce risk: I'll keep FrontSide but make sure winding is right by testing mentally one face.

Let me verify +X face, normal (1,0,0), viewed from +X axis looking toward -X (i.e., camera at large X looking in -X direction). In this view, the screen has X going... let me set up: we look along -X. Let's define screen coordinates: up = +Y, and to the right = ? When looking along -X with up +Y, right hand rule: forward = -X, up = +Y, right = up × forward? Cross product. Actually for a viewer, right = forward × up? Let me just think of it as: looking in -X direction, +Y is up. Then +Z is to the left or right? Using right-handed coords, if forward is -X and up is +Y, then right = forward × up = (-X) × (+Y) = -(X×Y) = -Z. So right = -Z. So on screen, rightward is -Z, upward is +Y.

Corners: (1,0,0),(1,1,0),(1,1,1),(1,0,1). Project to screen (right=-Z, up=+Y):
- (1,0,0): right=0, up=0 → (0,0)
- (1,1,0): right=0, up=1 → (0,1)
- (1,1,1): right=-1, up=1 → (-1,1)
- (1,0,1): right=-1, up=0 → (-1,0)

Order: (0,0)→(0,1)→(-1,1)→(-1,0). Going: bottom-right → top-right → top-left → bottom-left. That's counterclockwise? From (0,0) up to (0,1), then left to (-1,1), then down to (-1,0), then right to (0,0). That traces CCW? Starting bottom-right, going up (to top-right), then left (to top-left), then down (bottom-left), then right (back). This is counterclockwise. Yes! CCW when viewed from outside (+X). Correct winding. 

Now triangles: quad vertices v0,v1,v2,v3. Triangles: (v0,v1,v2) and (v0,v2,v3). Both CCW. Good.

Now the color array: for each vertex, set RGB = baseColor * factor. Factor depends on face direction.

Let me write rebuildChunk:
```js
function rebuildChunk(cx, cz) {
  const chunk = getChunk(cx, cz);
  if (!chunk) return;
  // dispose old
  if (chunk.mesh) {
    scene.remove(chunk.mesh);
    chunk.mesh.geometry.dispose();
  }
  const positions = [];
  const normals = [];
  const colors = [];
  const indices = [];
  let vi = 0;
  const data = chunk.data;
  for (let lz = 0; lz < CHUNK_SIZE; lz++) {
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      for (let ly = 0; ly < CHUNK_HEIGHT; ly++) {
        const id = data[di(lx, ly, lz)];
        if (id === 0) continue;
        const wx = cx*CHUNK_SIZE + lx;
        const wz = cz*CHUNK_SIZE + lz;
        const baseCol = BLOCK_COLORS[id];
        for (let f = 0; f < 6; f++) {
          const face = faces[f];
          const nx = wx + face.dir[0];
          const ny = ly + face.dir[1];
          const nz = wz + face.dir[2];
          if (getBlock(nx, ny, nz) !== 0) continue; // neighbor solid, skip
          // lighting factor
          let factor;
          if (face.dir[1] === 1) factor = 1.0;
          else if (face.dir[1] === -1) factor = 0.55;
          else factor = 0.8;
          const r = ((baseCol >> 16) & 255) * factor;
          const g = ((baseCol >> 8) & 255) * factor;
          const b = (baseCol & 255) * factor;
          for (let c = 0; c < 4; c++) {
            const p = face.corners[c];
            positions.push(wx + p[0], ly + p[1], wz + p[2]);
            normals.push(face.dir[0], face.dir[1], face.dir[2]);
            colors.push(r, g, b);
          }
          indices.push(vi, vi+1, vi+2, vi, vi+2, vi+3);
          vi += 4;
        }
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices);
  const mesh = new THREE.Mesh(geo, blockMaterial);
  mesh.position.set(cx*CHUNK_SIZE, 0, cz*CHUNK_SIZE);
  chunk.mesh = mesh;
  scene.add(mesh);
}
```

Wait, the mesh position — spec says "keep the mesh at the origin". Hmm. "Use world coordinates for vertices and keep the mesh at the origin." So the mesh should be at origin (0,0,0) with world coords as vertices. That way raycasting uses world coords directly. OK so don't translate mesh. Let me set mesh.position to (0,0,0) (default). Good.

But then the chunk data index di uses local x,y,z. And positions use world coords. Good.

Now, the blockMaterial:
```js
const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

Now the management loop each frame.

State:
```js
let pendingGen = []; // chunks needing data
let pendingMesh = []; // chunks needing mesh
```

Actually let me manage with counters. Let me maintain:
- chunks map: key -> {data, mesh}

Each frame:
1. Determine player chunk. Generate data for chunks within 5 (Manhattan or Chebyshev?) of player, that don't have data yet. Max 4 per frame.
2. Build meshes for chunks within 4 whose 4 neighbors have data. Max 2 per frame.
3. Remove chunks farther than 7 from player: dispose mesh, delete entry.

Let me compute distances in chunk units. Player chunk = (floor(px/16), floor(pz/16)).

For generation: iterate over a ring/window of radius 5 around player chunk. For each chunk without data, add to gen queue. Process up to 4.

For meshing: for chunks WITH data but no mesh, if all 4 orthogonal neighbors (N,S,E,W) have data, add to mesh queue. Process up to 2.

Removal: for chunks in map with chunk-distance > 7, remove.

Let me define chunk distance as max(|dcx|, |dcz|) (Chebyshev) or Manhattan? Spec: "within 5 chunks of the player" and "farther than 7". Let me use Chebyshev (max of abs diffs) for simplicity, or Manhattan. I'll use Chebyshev (max(|dcx|,|dcz|)).

Let me write the update:
```js
function updateWorld(px, pz) {
  const pcx = Math.floor(px / CHUNK_SIZE);
  const pcz = Math.floor(pz / CHUNK_SIZE);

  // Generate data
  let genBudget = 4;
  for (let dc = -5; dc <= 5 && genBudget > 0; dc++) {
    for (let dz = -5; dz <= 5 && genBudget > 0; dz++) {
      const cx = pcx + dc, cz = pcz + dz;
      const key = cx + "," + cz;
      if (!chunks.has(key)) {
        chunks.set(key, { data: generateChunkData(cx, cz), mesh: null });
        genBudget--;
      }
    }
  }
  ...
}
```

Hmm, but iterating -5..5 is 11x11=121 iterations, checking has(). That's fine. But order matters for meshing (neighbors). Let me first do generation, then meshing.

For meshing:
```js
let meshBudget = 2;
for (const [key, chunk] of chunks) {
  if (meshBudget <= 0) break;
  if (chunk.mesh) continue;
  const [cx, cz] = key.split(",").map(Number);
  // check 4 neighbors have data
  if (chunks.has((cx-1)+","+cz) && chunks.has((cx+1)+","+cz) &&
      chunks.has(cx+","+(cz-1)) && chunks.has(cx+","+(cz+1))) {
    rebuildChunk(cx, cz);
    meshBudget--;
  }
}
```

For removal:
```js
for (const [key, chunk] of chunks) {
  const [cx, cz] = key.split(",").map(Number);
  const d = Math.max(Math.abs(cx-pcx), Math.abs(cz-pcz));
  if (d > 7) {
    if (chunk.mesh) {
      scene.remove(chunk.mesh);
      chunk.mesh.geometry.dispose();
    }
    chunks.delete(key);
  }
}
```

Note: iterating and deleting from Map simultaneously — JS Map allows deletion during iteration. Should be fine.

But there's a subtlety: we generate data for up to radius 5, remove beyond 7. Between 5 and 7, chunks may exist without data (waiting). That's fine.

Wait, but there's a concern: a chunk at radius 6 exists (no data) because it was generated earlier when player was closer, and now player moved away. It won't be regenerated (out of gen radius 5) but also not removed (within 7). It stays as no-data. That's fine, memory bounded.

Also, chunks at radius 5 might not all get data in one frame (budget 4). Over frames they fill. Good.

Now, initial generation: on start, we want the player's chunk and neighbors available quickly so the game is playable immediately. Let me pre-generate a bunch at startup. Actually, let me just generate a fixed set at start (e.g., radius 3 or so) so the player isn't falling through the world on load. Let me generate all chunks within radius 3 at start, and build their meshes too. That gives immediate playability.

Actually, to be safe, let me generate and mesh a larger area at start. Let me generate radius 4 and mesh those with valid neighbors. That's quick.

Let me do at startup:
```js
function initWorld(px, pz) {
  const pcx = Math.floor(px/16), pcz = Math.floor(pz/16);
  for (let dc=-4; dc<=4; dc++) for (let dz=-4; dz<=4; dz++) {
    const cx=pcx+dc, cz=pcz+dz;
    const key=cx+","+cz;
    if(!chunks.has(key)) chunks.set(key,{data:generateChunkData(cx,cz),mesh:null});
  }
  // mesh those with neighbors present
  for (const [key,chunk] of chunks) {
    const [cx,cz]=key.split(",").map(Number);
    if (chunks.has((cx-1)+","+cz)&&chunks.has((cx+1)+","+cz)&&chunks.has(cx+","+(cz-1))&&chunks.has(cx+","+(cz+1))) {
      rebuildChunk(cx,cz);
    }
  }
}
```

Good.

Now player physics. State:
```js
const player = {
  pos: new THREE.Vector3(8, ?, 8),
  vel: new THREE.Vector3(),
  onGround: false,
  yaw: 0,
  pitch: 0,
};
```

Spawn above terrain at x=8, z=8. Need to find terrain height at (8,8). Compute via getBlock or via generation. Let me generate the column and find top. Actually simpler: spawn at a high y and let gravity drop them. But better to spawn on surface. Let me find surface: generate chunk for (8,8) region and scan. Or just spawn at y = 60 and fall. Let me spawn at a computed height.

Let me compute surface height at (8,8):
```js
function surfaceHeightAt(x, z) {
  for (let y = CHUNK_HEIGHT-1; y >= 0; y--) {
    if (getBlock(x, y, z) !== 0) return y+1; // top of solid +1
  }
  return 20;
}
```
Then spawn pos.y = that. But getBlock requires chunk data. At spawn we generate chunks first. (8,8) is in chunk (0,0). Let me ensure chunk (0,0) generated before spawn. In initWorld with radius 4, yes.

Actually (8,8): floor(8/16)=0. So chunk 0,0. Generated. Good.

Physics update:
```js
function updatePlayer(dt) {
  // gravity
  player.vel.y -= GRAVITY * dt;
  // movement input relative to yaw
  const move = new THREE.Vector3();
  if (keys['w']) move.z -= 1;
  if (keys['s']) move.z += 1;
  if (keys['a']) move.x -= 1;
  if (keys['d']) move.x += 1;
  if (move.lengthSq() > 0) move.normalize();
  // rotate move by yaw
  const sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
  // In three.js, positive yaw rotates... let me define forward.
  const mx = move.x * cos - move.z * sin; // hmm
  ...
}
```

Let me define yaw such that yaw=0 looks toward -Z (standard). Camera rotation order YXZ: camera.rotation.set(pitch, yaw, 0, 'YXZ'). With YXZ order, the Y rotation (yaw) is applied first (in local), then X (pitch). Actually rotation order 'YXZ' means rotations compose as R = Rz? No. Three.js rotation order 'YXZ': the object is rotated about Y, then X, then Z, in the sense that the final rotation matrix is R = R_y * R_x * R_z? Let me recall. In THREE, `rotation.order = 'YXZ'` means the rotations are applied in the order Y, then X, then Z, but as intrinsic rotations. The resulting effect: yaw about Y, pitch about X (local). For FPS, we set yaw (Y) then pitch (X). Camera looks down -Z by default. Rotating about Y by angle θ turns to... Let me just test: camera at origin looking -Z. Rotate about Y by +θ (counterclockwise when viewed from above). After rotation, forward direction = (sinθ, 0, -cosθ)? Let me compute: initial forward = (0,0,-1). Rotation about Y by θ: 
R_y(θ) = [[cosθ,0,sinθ],[0,1,0],[-sinθ,0,cosθ]].
Apply to (0,0,-1): x = cosθ*0 + 0*0 + sinθ*(-1) = -sinθ. y=0. z = -sinθ*0 + 0 + cosθ*(-1) = -cosθ. So forward = (-sinθ, 0, -cosθ).

Hmm so moving "forward" (positive move.z after our mapping) should be along forward direction (-sinθ, 0, -cosθ). Let me define movement: player moves in the direction they look (horizontally). 

Let me define: forwardHoriz = (-sin(yaw), 0, -cos(yaw)). rightHoriz = cross(forward, up)? = (forward x up)... Let me just compute right = (cos(yaw), 0, -sin(yaw))? Let me get right as forward rotated -90 about Y. Actually right = (cosθ, 0, -sinθ)? Let me verify: at θ=0, right should be (+X)=(1,0,0). cos0=1, -sin0=0 → (1,0,0). Good. At θ=90°, forward=(-1,0,0) (looking -X), right should be (0,0,1)? If you turn left 90° (θ=+90), your right hand points... forward was -Z, now -X. Right = forward rotated -90 about Y = (cos90, 0, -sin90) = (0,0,-1). Hmm. Let me not overthink; I'll define:

moveDir.x = sin(yaw) for strafe? Let me just define clearly:
- Forward (keydown W) direction: dx = -sin(yaw), dz = -cos(yaw).
- Strafe right (keydown D): dx = cos(yaw), dz = -sin(yaw).

Check D at yaw=0: dx=1, dz=0 → moves +X. Right of forward(-Z) is +X. Correct.
Check D at yaw=90°: dx=cos90=0, dz=-sin90=-1 → moves -Z. At yaw=90, forward=-X. Right of -X (looking -X, up +Y) is... right = forward × up? Let me use right = normalize(cross(forward, up)). forward=(-1,0,0), up=(0,1,0). cross(forward,up) = (fy*uz-fz*uy, fz*ux-fx*uz, fx*uy-fy*ux) = (0*1-0*0, 0*0-(-1)*1, (-1)*1-0*0) = (0, 1, -1). Hmm that's not right. Let me use cross(up, forward): up×forward = (uy*fz-uz*fy, uz*fx-ux*fz, ux*fy-uy*fx) = (1*(-1)-0, 0-0, 0-(-1)*1)... let me recompute. up=(0,1,0), forward=(-1,0,0). cross(up,forward) = (uy*fz - uz*fy, uz*fx - ux*fz, ux*fy - uy*fx) = (1*0 - 0*0, 0*(-1) - 0*0, 0*0 - 1*(-1)) = (0, 0, 1). So right = (0,0,1). But my formula gave (0,0,-1) for D. Discrepancy.

Ugh, sign conventions. Let me just pick a convention and make W/D consistent with camera. The key requirement: pressing W moves toward where you look, D strafes right. As long as it's consistent it's playable. Let me define based on camera forward and use a clean derivation.

Camera forward (unit, horizontal) = (-sin(yaw), 0, -cos(yaw)) as derived.
Camera right = (cos(yaw), 0, -sin(yaw))? Let me verify with cross(forward, up) properly. Actually right-hand: if forward is F and up is U=(0,1,0), then right R = F × U? For a right-handed system where right × up = forward... no. Let me use: right = U × F won't... 

Standard: For a camera, right = normalize(cross(forward, up))? Let me test with forward=(0,0,-1) (yaw=0), up=(0,1,0). cross(forward, up) = (fz*uy - fu... ) let me carefully: cross(A,B) = (Ay*Bz - Az*By, Az*Bx - Ax*Bz, Ax*By - Ay*Bx). A=forward=(0,0,-1), B=up=(0,1,0). 
x = Ay*Bz - Az*By = 0*0 - (-1)*1 = 1.
y = Az*Bx - Ax*Bz = (-1)*0 - 0*0 = 0.
z = Ax*By - Ay*Bx = 0*1 - 0*0 = 0.
So cross(forward,up) = (1,0,0) = +X. Good, right = +X at yaw 0. Correct.

So right = cross(forward, up) = cross((-sinθ,0,-cosθ),(0,1,0)).
x = Ay*Bz - Az*By = 0*0 - (-cosθ)*1 = cosθ.
y = Az*Bx - Ax*Bz = (-cosθ)*0 - (-sinθ)*0 = 0.
z = Ax*By - Ay*Bx = (-sinθ)*1 - 0*0 = -sinθ.
So right = (cosθ, 0, -sinθ). 

So:
- W (forward): dir = (-sinθ, 0, -cosθ)
- D (right): dir = (cosθ, 0, -sinθ)
- S (backward): dir = (sinθ, 0, cosθ)
- A (left): dir = (-cosθ, 0, sinθ)

Move vector = (W_pos - S_neg)*forward + (D - A)*strafe. Let me just accumulate:
```js
let fx=0, fz=0;
if (W) { fx -= sin; fz -= cos; }
if (S) { fx += sin; fz += cos; }
if (D) { fx += cos; fz -= sin; }
if (A) { fx -= cos; fz += sin; }
```
Then normalize (fx,fz) and multiply by speed.

Now collision. Player box: half-width 0.3, height 1.8, eye 1.62. So the box spans from pos.x±0.3, pos.y to pos.y+1.8 (feet to top), pos.z±0.3. Eye at pos.y + 1.62.

Collision: for each axis, move, then check overlap with any solid block intersecting the box; if overlap, revert that axis.

Check function: does player box overlap block (bx,by,bz)? Box: [px-0.3, px+0.3] × [py, py+1.8] × [pz-0.3, pz+0.3]. Block: [bx, bx+1]×[by,by+1]×[bz,bz+1]. Overlap if intervals intersect on all axes.
```js
function overlapsBlock(px, py, pz, bx, by, bz) {
  return px+0.3 > bx && px-0.3 < bx+1 &&
         py > by && py-1.8 < by+1 &&   // careful: box y from py to py+1.8? 
         ...
}
```
Wait, let me define box as feet at py, head at py+1.8. So y-range [py, py+1.8]. Overlap with block y [by, by+1]: py < by+1 && py+1.8 > by.
```js
function boxOverlapsBlock(px, py, pz, bx, by, bz) {
  return (px + HW > bx) && (px - HW < bx+1) &&
         (py < by+1) && (py + PH > by) &&
         (pz + HW > bz) && (pz - HW < bz+1);
}
```
HW=0.3, PH=1.8.

To check collision, we need to find all blocks in range of the player box and test. Range: from floor(px-0.3)-1 to floor(px+0.3)+1 etc. Let me iterate over candidate block coordinates.

```js
function resolveCollision() {
  const px=player.pos.x, py=player.pos.y, pz=player.pos.z;
  const minX = Math.floor(px-HW)-1, maxX = Math.floor(px+HW)+1;
  const minY = Math.floor(py)-1, maxY = Math.floor(py+PH)+1;
  const minZ = Math.floor(pz-HW)-1, maxZ = Math.floor(pz+HW)+1;
  for (let bx=minX; bx<=maxX; bx++)
  for (let by=minY; by<=maxY; by++)
  for (let bz=minZ; bz<=maxZ; bz++) {
    if (getBlock(bx,by,bz)!==0 && boxOverlapsBlock(px,py,pz,bx,by,bz)) {
      // collision on this block
    }
  }
}
```

Axis-separated movement: move along X first, check collisions, if any overlap set vx displacement reverted (pos.x back). Then Y, then Z.

```js
// X
player.pos.x += player.vel.x * dt;
if (collides()) { player.pos.x -= player.vel.x * dt; player.vel.x = 0; }
// Y
player.pos.y += player.vel.y * dt;
if (collides()) {
  if (player.vel.y < 0) player.onGround = true; // landing
  player.pos.y -= player.vel.y * dt;
  player.vel.y = 0;
} else {
  player.onGround = false;
}
// Z similar
```

Where collides() checks boxOverlapsBlock against all candidate blocks with current player.pos.

Jump: if onGround and Space, vel.y = JUMP_SPEED (8.5), onGround=false.

Fall reset: if player.pos.y < -20, teleport to spawn (pos = spawn pos, vel=0).

Now camera: camera.position.copy(player.pos); camera.position.y += EYE (1.62). camera.rotation.set(pitch, yaw, 0, 'YXZ').

Mouse look: on mousemove while locked, yaw -= sensitivity * dx, pitch -= sensitivity * dy, clamp pitch to [-π/2+eps, π/2-eps].

Wait, need to check sign. Mouse move right (dx>0) should yaw to the right (turn right). Turning right = yaw increases or decreases? Earlier forward=(-sinθ,0,-cosθ). If we turn right (clockwise from above), forward should rotate toward +X. At θ=0 forward=-Z. Turn right → forward should go toward... right is +X. Rotating forward toward +X means θ becomes negative? forward(-sinθ,...): at small negative θ, -sinθ = positive → +x component. So θ negative = turn right. So yaw decreases when moving mouse right (dx>0). So yaw -= sensitivity*dx. Yes matches.

Pitch: mouse up (dy<0, since screen y down) should look up. Looking up = pitch negative? With rotation order YXZ and X rotation. Camera looks -Z. Rotating about X (local) by pitch. Let me figure: after yaw applied, camera looks horizontally. Then pitch about X. Positive X rotation (right-hand, +X points right when looking... ). Let me just define pitch such that mouse-down (dy>0) looks down. Let me set pitch -= sensitivity*dy. Then mouse down (dy>0) → pitch decreases. Need to check if decreasing pitch looks down.

Camera default forward after yaw=0: (0,0,-1) roughly (ignoring pitch). Apply pitch rotation about X. R_x(p) = [[1,0,0],[0,cos p,-sin p],[0,sin p,cos p]]. Apply to (0,0,-1): x=0, y = cos p*0 - sin p*(-1) = sin p. z = sin p*0 + cos p*(-1) = -cos p. So forward = (0, sin p, -cos p). At p=0: (0,0,-1)水平. At p>0: y = sin p >0 → looks up. At p<0: looks down.

So looking up needs p>0. Mouse up = dy<0. pitch -= sensitivity*dy → pitch += sensitivity*|dy| → pitch increases → looks up. Correct!

So: yaw -= sensitivity*dx; pitch -= sensitivity*dy. Clamp pitch to [-1.5, 1.5] approx (slightly less than π/2).

Now raycasting for break/place. Each frame, raycast from camera center (camera position, direction = camera forward) against all chunk meshes, max distance 6.

```js
const raycaster = new THREE.Raycaster();
raycaster.far = 6; // actually near/far
function getTarget() {
  raycaster.set(camera.position, cameraForward);
  raycaster.far = 6;
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length > 0) return hits[0];
  return null;
}
```

cameraForward: from camera rotation. Since camera.rotation set, camera.getWorldDirection(vec). Let me use a vec3 and camera.getWorldDirection.

From hit point p and face normal n: break target = floor(p - n*0.5), place cell = floor(p + n*0.5), per component.

```js
const hit = getTarget();
if (hit) {
  const p = hit.point;
  const n = hit.face.normal; // in local coords; but mesh at origin so local=world for normal. Good.
  const bx = Math.floor(p.x - n.x*0.5);
  const by = Math.floor(p.y - n.y*0.5);
  const bz = Math.floor(p.z - n.z*0.5);
  // outline
  outlineBox.position.set(bx+0.5, by+0.5, bz+0.5);
  outlineBox.visible = true;
  targetBlock = {x:bx,y:by,z:bz};
}
```

Wait, hit.face.normal is in the mesh's local coordinate space. Since mesh is at origin (no translation, no rotation), local normals = world normals. Good. But the normal direction: for a face, face.normal points outward from the face. Since we only render outward faces (toward air), the normal points into the empty space toward the player. So p - n*0.5 goes INTO the block (break target), p + n*0.5 goes into the air (place cell). Correct.

Outline: a BoxGeometry(1,1,1) with EdgesGeometry or WireframeGeometry, black, maybe transparent. Let me use:
```js
const outlineGeo = new THREE.BoxGeometry(1.01,1.01,1.01);
const outlineMat = new THREE.LineBasicMaterial({color:0x000000});
const outline = new THREE.LineSegments(new THREE.EdgesGeometry(outlineGeo), outlineMat);
```
EdgesGeometry gives just the 12 edges, cleaner. Position at block center.

Break on left click (while locked): set target to air, but not at y=0.
```js
if (targetBlock && targetBlock.y > 0) {
  setBlock(targetBlock.x, targetBlock.y, targetBlock.z, 0);
}
```

Place on right click (while locked): place selected block if cell is air and doesn't overlap player.
```js
if (targetBlock) {
  const cell = placeCell; // from p + n*0.5
  if (getBlock(cell.x,cell.y,cell.z)===0 && !boxOverlapsBlockAt(cell)) {
    setBlock(cell.x,cell.y,cell.z, selectedBlock);
  }
}
```

boxOverlapsBlockAt: check if placing at cell overlaps player box. Player box [px±0.3, py..py+1.8, pz±0.3]. Block cell [cx,cx+1]... Let me reuse boxOverlapsBlock(player.pos.x, player.pos.y