Let me carefully build this Minecraft clone in a single HTML file. Let me think through all the requirements.

This is a complex task. Let me plan out the structure:

1. HTML/CSS skeleton: body, canvas, crosshair, hotbar, start overlay
2. Load Three.js r128
3. Game logic:
   - Block definitions
   - Chunk storage (Map)
   - Global read/write block helpers
   - Terrain generation (value noise)
   - Meshing
   - Player physics & controls
   - Break & place
   - Hotbar
   - Sky, clouds, water
   - UI

Let me write this carefully.

### Block IDs
- 0 air
- 1 grass 0x4caf50
- 2 dirt 0x795548
- 3 stone 0x9e9e9e
- 4 sand 0xe7d9a8
- 5 wood 0x8d6e63
- 6 leaves 0x2e7d32
- 7 snow 0xffffff

### Chunk storage
- Chunks are 16x16 columns, 80 blocks high
- Global Map keyed "cx,cz" -> { blocks: Uint8Array, mesh }
- blocks size = 16 * 80 * 16 = 20480 bytes

Wait, chunk is 16 wide (x), 80 high (y), 16 deep (z). So block count = 16 * 80 * 16 = 20480.

### Block helpers
Global read/write using chunk = floor(world/16), local = world - chunk*16.

```
function getChunk(cx, cz) { return chunkMap.get(cx + "," + cz); }

function setBlockAt(cx, cz, x, y, z, id) {
  let c = chunkMap.get(cx + "," + cz);
  if (!c) { c = { blocks: new Uint8Array(16*80*16), mesh: null }; chunkMap.set(cx+","+cz, c); }
  c.blocks[(y*16+z)*16+x + y] = id; // hmm need to figure indexing
}
```

Actually let me define local indexing. Local coords x,y,z where x,z in [0,16), y in [0,80). Index = (y*16 + z)*16 + x? Let's see: for a given y, we have a 16x16 row. Row stride = 16*16 = 256. Within row, z*16 + x. So index = y*256 + z*16 + x. Total = 80*256 = 20480. Good.

So:
```
function localIndex(x, y, z) { return (y*16 + z)*16 + x; }
```

Wait that's y*256 + z*16 + x. Yes (y*16+z)*16+x = y*256 + z*16 + x. Good.

Read global:
```
function getBlock(wx, wy, wz) {
  const cx = floorDiv(wx, 16);
  const cz = floorDiv(wz, 16);
  const lx = wx - cx*16;
  const lz = wz - cz*16;
  const c = chunkMap.get(cx+","+cz);
  if (!c || wy < 0 || wy >= 80) return 0;
  return c.blocks[(wy*16+lz)*16+lx];
}
```

floorDiv handles negatives: `Math.floor(a/16)`. In JS, Math.floor works for negatives correctly (returns floor). So `Math.floor(wx/16)`.

Write:
```
function setBlock(wx, wy, wz, id) {
  const cx = Math.floor(wx/16);
  const cz = Math.floor(wz/16);
  const lx = wx - cx*16;
  const lz = wz - cz*16;
  let c = chunkMap.get(cx+","+cz);
  if (!c) return; // ignore writes to non-existent chunks? Actually should create
  ...
}
```

Hmm, but writing to a non-existent chunk... For break/place we operate on existing chunks (within render distance). Let me create the chunk if needed.

Actually for simplicity, if chunk doesn't exist, we can create it (which triggers generation). But generation is separate. Let me just handle it: setBlock creates chunk if missing.

### Terrain generation

Value noise:
- Integer hash giving 0-1 (mix with large prime multipliers and xor-shifts)
- Smoothed 2D noise via bilinear interpolation with smoothstep
- 4 octaves combined into fractal noise
- 3D version for caves

Let me implement:

```
function hash2(ix, iy) {
  // integer hash
  ix ^= (ix * 0x2754) ... 
}
```

Let me design a proper hash. The spec says "an integer-coordinate hash giving 0–1 (mix with large prime multipliers and xor-shifts)".

```
function hash(ix, iy) {
  let h = ix * 3747613937 + iy * 668265265; // prime multipliers
  h = (h ^ (h >> 13)) * 12243567; // xor-shift
  h = (h ^ (h >> 16));
  return ((h >>> 0) % 65536) / 65536; // 0..1
}
```

Hmm let me make it produce 0-1. Let me do:
```
function hash(ix, iy) {
  let h = ix * 1600000007 + iy * 668265263;
  h = (h ^ (h >>> 13)) * 2246822519;
  h = (h ^ (h >>> 16));
  return (h >>> 0) / 4294967296;
}
```

That gives 0..1.

Smooth 2D noise:
```
function lerp(a, b, t) { return a + (b-a)*t; }
function smooth(t) { return t*t*(3-2*t); }
function noise2(ix, iy) {
  const xi = Math.floor(ix), yi = Math.floor(iy);
  const xf = ix - xi, yf = iy - yi;
  const u = smooth(xf), v = smooth(yf);
  const g00 = hash(xi, yi), g10 = hash(xi+1, yi);
  const g01 = hash(xi, yi+1), g11 = hash(xi+1, yi+1);
  const x0 = lerp(g00, g10, u);
  const x1 = lerp(g01, g11, u);
  return lerp(x0, x1, v);
}
```

Fractal 4 octaves:
```
function fractal2(ix, iy) {
  let amp = 1, freq = 1, sum = 0, norm = 0;
  for (let o = 0; o < 4; o++) {
    sum += amp * noise2(ix*freq, iy*freq);
    norm += amp;
    amp *= 0.5; freq *= 2;
  }
  return sum / norm;
}
```

3D noise for caves:
```
function noise3(ix, iy, iz) {
  // interpolate over 3D grid
  ...
}
```

For 3D noise I'll do trilinear interpolation over 8 corners.

```
function hash3(ix, iy, iz) {
  let h = ix * 1600000007 + iy * 668265263 + iz * 3815841965;
  h = (h ^ (h >>> 13)) * 2246822519;
  h = (h ^ (h >>> 16));
  return (h >>> 0) / 4294967296;
}

function noise3(ix, iy, iz) {
  const xi = Math.floor(ix), yi = Math.floor(iy), zi = Math.floor(iz);
  const xf = ix - xi, yf = iy - yi, zf = iz - zi;
  const u = smooth(xf), v = smooth(yf), w = smooth(zf);
  const c = [
    hash3(xi, yi, zi), hash3(xi+1, yi, zi), hash3(xi, yi+1, zi), hash3(xi+1, yi+1, zi),
    hash3(xi, yi, zi+1), hash3(xi+1, yi, zi+1), hash3(xi, yi+1, zi+1), hash3(xi+1, yi+1, zi+1)
  ];
  const d00 = lerp(c[0], c[1], u);
  const d10 = lerp(c[2], c[3], u);
  const d01 = lerp(c[4], c[5], u);
  const d11 = lerp(c[6], c[7], u);
  const e0 = lerp(d00, d10, v);
  const e1 = lerp(d01, d11, v);
  return lerp(e0, e1, w);
}
```

Now terrain generation per column. Given world coords wx, wz (the column origin), compute:
- m = fractal2 at (wx*0.004, wz*0.004)
- h = fractal2 at (wx*0.02, wz*0.02)
- H = floor(5 + m*m*58 + h*10)

Then fill column from y=0 to 79.

But wait, generation needs to happen for a chunk. Let me write generateChunk(cx, cz) that fills the blocks array.

Actually, the meshing happens per chunk. Let me structure generation to run on a chunk when we need data.

Let me define:
```
function generateChunk(cx, cz) {
  const c = getOrCreateChunk(cx, cz);
  const blocks = c.blocks;
  for (let x = 0; x < 16; x++) {
    for (let z = 0; z < 16; z++) {
      const wx = cx*16 + x;
      const wz = cz*16 + z;
      const m = fractal2(wx*0.004, wz*0.004);
      const h = fractal2(wx*0.02, wz*0.02);
      let H = Math.floor(5 + m*m*58 + h*10);
      // fill
      for (let y = 0; y <= 79; y++) {
        let id = 0;
        if (y === 0) id = 3; // stone at y0
        else if (y < H-3) id = 3; // stone
        else if (y < H-3+3) id = (H <= 16 ? 4 : (H >= 37 ? 3 : 2)); // dirt/stone/sand layers under surface
        else if (y === H-1) { // surface
          if (H >= 46) id = 7;
          else if (H >= 37) id = 3;
          else if (H <= 16) id = 4;
          else id = 1;
        }
        // caves
        if (y >= 3 && y < H-2) {
          const cv = noise3(wx*0.09, y*0.09, wz*0.09);
          if (cv > 0.67) id = 0;
        }
        blocks[(y*16+z)*16+x] = id;
      }
      // trees
      // tree on grass when per-column hash < 0.02 and trunk fits
      ...
    }
  }
}
```

Wait, the spec says: "below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = ...". Let me re-read.

"Column fill: y 0 = unbreakable stone; below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

So:
- y = 0: stone (3)
- y < H-3: stone (3)
- the 3 layers under the surface (y from H-4 to H-1? no wait). "the 3 layers under the surface dirt" — dirt occupies the 3 layers just below the surface. Surface is at y = H-1 (topmost). So dirt layers are at y = H-4, H-3, H-2? Hmm, "below H-3 stone" means y < H-3 is stone, i.e., y <= H-4 is stone. Then dirt is at y = H-3, H-2, H-1? That's 3 layers. But then surface would be part of dirt? No.

Wait, let me reconsider. Actually "surface" is the topmost block. Let me reconsider the indices.

If H is the height, and surface is at y = H-1 (0-indexed, top block), then:
- The 3 layers under the surface: y = H-4, H-3, H-2 → dirt
- Surface: y = H-1

Hmm, but that means the top 4 blocks are: 3 dirt + 1 surface. Let me check: "the 3 layers under the surface dirt" = 3 layers of dirt beneath the surface block. Surface block is separate.

So:
- y < H-4: stone (this covers "below H-3 stone"? Let me reconcile)

Hmm, "below H-3 stone" — y < H-3 means y <= H-4. Then dirt at y = H-3, H-2, H-1? That's only if surface is at H-1... 

Actually there's ambiguity. Let me interpret with H being the surface height (surface at y = H-1):

Option A:
- y = 0: stone
- 0 < y < H-4: stone ("below H-3")
- H-4 <= y < H-1: dirt (3 layers: H-4, H-3, H-2)... wait that's H-4, H-3, H-2 = 3 layers, and surface at H-1.

Hold on. If dirt is the 3 layers under surface, and surface is at H-1, then dirt is at H-2, H-3, H-4. Stone below H-4. That matches "below H-3 stone" loosely (H-4 < H-3).

Hmm, but "below H-3" strictly means y < H-3 i.e. y <= H-4. So stone for y <= H-4. Dirt for H-3, H-2, H-1? But then surface isn't separate.

I think the intended interpretation:
- surface height H, surface block at y = H-1
- 3 dirt layers below: y = H-4, H-3, H-2
- stone below: y <= H-5? 

Ugh. Let me just go with a clean interpretation that satisfies the letter as much as possible:

Let me define surface at y = H-1.
- y = 0 → stone
- y < H-3 → stone (i.e., y = 1..H-4)

Wait that conflicts. Let me reconsider: maybe H is such that surface is at y = H-1, and "below H-3" is a typo/shorthand. Let me just pick:

- y = 0: stone
- y = 1 .. H-4: stone  (this is "below H-3")
- y = H-3, H-2, H-1: these 3 layers... 

No. Let me re-read one more time very carefully:

"Column fill: y 0 = unbreakable stone; below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

OK so parsing semicolon-separated clauses:
1. "y 0 = unbreakable stone" → y=0 is stone
2. "below H−3 stone" → y < H-3 is stone
3. "the 3 layers under the surface dirt (...)" → the 3 layers under the surface are dirt
4. "surface = ..." → the surface block type depends on H

So surface is at the top. If there are 3 dirt layers "under the surface", and the surface is the top block at y = H-1, then:
- surface: y = H-1
- dirt (3 layers): y = H-2, H-3, H-4
- stone below: y <= H-5

But clause 2 says "below H-3 stone" which would be y <= H-4. Contradiction with y=H-4 being dirt.

Unless... the surface is at y = H (not H-1). Let me try: if surface at y = H:
- surface: y = H
- dirt (3 layers under): y = H-1, H-2, H-3
- stone below: y <= H-4 → "below H-3"?? No, that's "below H-4".

Hmm, still off by one.

Let me try yet another interpretation. What if the loops treat H as the number of filled rows, with surface at y = H-1, and the "3 layers under the surface" being y = H-4, H-3, H-2, and "below H-3" meaning y < H-3 (i.e. y <= H-4) is stone, BUT there's overlap at y = H-4.

The cleanest reconciliation: 
- y <= H-5: stone (or y < H-4)
- y in {H-4, H-3, H-2}: dirt
- y = H-1: surface

And clause "below H-3 stone" is approximate. Since the exact boundary doesn't hugely matter for gameplay, and the spec's own wording is slightly inconsistent, I'll implement:

- y = 0: stone
- y < H-4: stone
- H-4 <= y < H-1: dirt (3 layers)
- y = H-1: surface

Wait, "below H-3 stone" — if I want to honor it literally AND have 3 dirt layers, maybe:
- y < H-3: stone → y = 1..H-4
- y in {H-3, H-2}: dirt? That's only 2 layers.

Hmm. Let me just go with: stone for y < H-4, dirt for H-4 <= y < H-1 (3 layers), surface at H-1. Actually you know what, let me reconsider whether "below H-3" might mean "for y from 1 up to H-3 inclusive, i.e., y < H-3". And the 3 dirt layers are H-3, H-2, H-1 but H-1 is surface...

I'll make a decision and move on. The gameplay impact is minimal. Let me do:

```
if (y === 0) id = 3;
else if (y < H - 4) id = 3;          // stone (below H-3, roughly)
else if (y < H - 1) id = surfaceLayerType;  // dirt (3 layers: H-4,H-3,H-2)
else /* y === H-1 */ id = surfaceType;
```

Where surfaceLayerType:
- sand if H <= 16
- stone if H >= 37
- else dirt

And surfaceType:
- snow if H >= 46
- stone if H >= 37
- sand if H <= 16
- else grass

Wait, but the dirt layer type says "(sand if H ≤ 16, stone if H ≥ 37)". So for the 3 dirt layers, use sand/stone/dirt based on H. And separately the surface.

Hmm, but actually the surface and the dirt-type are related. When H >= 37, both dirt layers and surface become stone. When H <= 16, both become sand. Otherwise dirt layers are dirt, surface is grass (if H < 46) or snow (if H >= 46).

Let me simplify: compute a "material" for the column based on H, then apply.

Actually, let me just follow the spec literally with a slight adjustment. Let me use H-3 as the boundary for stone vs dirt, and interpret "3 layers under the surface" as y = H-4, H-3, H-2 being dirt... no.

OK final decision — I'll interpret it as:
- surface at y = H - 1
- The 3 layers immediately below surface (y = H-4, H-3, H-2) are the "dirt" layers (with material choice)
- Below that (y <= H-5, and specifically "below H-3" — I'll use y < H-4) is stone
- y = 0 is stone

Actually, let me reconsider once more. There might be a cleaner reading:

"below H−3 stone; the 3 layers under the surface dirt"

Maybe it means: for y below H-3, it's stone. The 3 layers under the surface are dirt. Where's the surface? At H-1. So the 3 layers under the surface = H-2, H-3, H-4? No wait, "under the surface" directly under = H-2, H-3, H-4 (3 layers). And "below H-3 stone" — but H-4 is below H-3 and it's dirt now. Contradiction again.

Alternatively surface at H-1, 3 dirt layers = H-2, H-3, H-4, and "below H-3" is just wrong/approximate for "below H-4". 

I'm confident enough. Let me go with:
- y == 0: stone
- y < H-4: stone
- H-4 <= y < H-1: dirt-layer-material
- y == H-1: surface-material

Actually, wait. Let me reconsider by thinking about what makes physical sense and the numbers. H ranges roughly 5 to ~63. With m in [0,1], m*m in [0,1], so m*m*58 in [0,58]. Plus h*10 in [0,10]. Plus 5. So H in [5, 68ish]. Wait max m=1 → 58, max h=1 → 10, +5 = 73. So H in roughly [5, 73].

With H around 30-40 typical. H-4 around 26-36. Surface around 29-39. That seems reasonable for a terrain where sea level is 14-16.

Water plane at 14.3. Beaches where H <= 16. Mountains where H >= 37. Snow where H >= 46.

OK this all makes sense. Let me finalize.

For the "below H-3" I'll actually use y < H-3 for stone to honor the literal text, but then dirt would be H-3, H-2, and surface H-1 — only 2 dirt layers. That contradicts "3 layers".

Argh. Let me just go with 3 dirt layers and y < H-4 for stone. The discrepancy is minor and won't affect playability. Actually, let me reconsider — maybe I should honor "below H-3" literally and put dirt at H-3, H-2, H-1 with surface being... no, surface is separate.

You know, let me just go with a version that has exactly 3 dirt layers and stone below, and not worry about the exact H-3 vs H-4. Final:

```
// material for dirt layers
let dirtMat = 2; // dirt
if (H <= 16) dirtMat = 4;       // sand
else if (H >= 37) dirtMat = 3;  // stone

// surface
let surfMat;
if (H >= 46) surfMat = 7;       // snow
else if (H >= 37) surfMat = 3;  // stone
else if (H <= 16) surfMat = 4;  // sand
else surfMat = 1;               // grass
```

Fill:
```
for y in 0..79:
  if y == 0: id = 3
  else if y < H-4: id = 3
  else if y < H-1: id = dirtMat
  else: id = surfMat
```

Then caves override.

Hmm wait, but if H is small (like 5), H-4 = 1, H-1 = 4. So dirt at y=1,2,3, surface at y=4. Fine.

Now trees. "on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

So tree requires surface == grass (id 1). Per-column hash computed from (wx, wz). Let me compute hash2(wx, wz) < 0.02.

Trunk: 4 wood blocks up from surface. Surface at y = H-1. Trunk from y=H-1+1 to H-1+4 = H..H+3. Need H+3 <= 79, i.e., H <= 76. Always true since H <= 73. But "trunk fits inside the chunk" — the x,z are fine since tree is at column position. Actually the trunk is at (x, z) same as the column cell. It fits as long as y range within [0,79]. Let me check H+3 < 80 → H < 77. OK.

Leaves: "leaves as a 5x5 layer twice, then 3x3, then 1 on top". So at trunk top (y = H+4), place a 5x5 layer of leaves (in x,z around trunk), then another 5x5 layer (one lower?), then 3x3, then 1 on top.

Let me interpret: The leaf canopy starts at trunk top. Let me place:
- At y = H+4 (top of trunk): 5x5 layer centered at trunk (x-2..x+2, z-2..z+2)
- At y = H+3: 5x5 layer
- At y = H+2: 3x3 layer
- At y = H+1: 1 (center)

Hmm, "then 1 on top" — maybe the 1 is above the 3x3. Let me reconsider. Typical tree:
```
    X
   XXX
  XXXXX
  XXXXX
 XXXXX
XXXXXXX  <- wait
```

Let me just do:
- y = top+1 (H+5): 1 leaf at center
- y = top (H+4): 3x3? 

The spec order: "5x5 layer twice, then 3x3, then 1 on top". So from bottom to top or top to bottom? "on top" suggests the 1 is at the very top. So:
- Bottom: 5x5
- next: 5x5
- next: 3x3
- top: 1

Let me place from trunk top downward. Trunk top is at y = H+3 (4th wood block: H, H+1, H+2, H+3). Leaves start at H+4.

- y = H+4: 5x5 (radius 2)
- y = H+3: 5x5 (radius 2) — but H+3 is wood! Conflict. 

Hmm. Let me reconsider. 4 wood blocks up: y = H, H+1, H+2, H+3 (surface at H-1, so trunk from H-1+1=H to H+3). Top of trunk at H+3.

Leaves should be above H+3. So:
- y = H+4: 5x5
- y = H+5: 5x5? 

But then "then 3x3, then 1 on top" would be even higher, which is weird (canopy narrower at top is fine, but having 5x5 below 3x3 below 1 is a tapering cone — reasonable).

Wait, but that puts the widest part at the bottom of the canopy and narrows going up. That's a valid tree shape (like a pine/cone). Let me go with:
- y = H+4: 5x5 (radius 2)
- y = H+5: 5x5 (radius 2)  -- "twice"
- y = H+6: 3x3 (radius 1)
- y = H+7: 1 (center)

Total canopy height 4 blocks (H+4 to H+7). Hmm, but "then 1 on top" being at H+7 with 3x3 at H+6 below it. That's fine.

But wait, this might exceed y=79 for tall trees. H max ~73, H+7 = 80. That's out of bounds (0..79). Edge case. Let me guard: only generate leaves where y < 80.

Actually, let me reconsider the tree shape to be more standard. A common simple tree:
```
     X          (1 on top)
    XXX         (3x3)
   XXXXX        (5x5)
   XXXXX        (5x5)
    X           trunk
```
Leaves from top: 1, then 3x3, then 5x5, then 5x5. Placed at trunk-top+1 upward:
- y = top+1: 1 (center)
- y = top+2: 3x3
- y = top+3: 5x5
- y = top+4: 5x5

Where top = H+3 (trunk top). So:
- y = H+4: 1 leaf
- y = H+5: 3x3
- y = H+6: 5x5
- y = H+7: 5x5

Hmm the spec says "5x5 layer twice, then 3x3, then 1 on top". Reading bottom-to-top: 5x5, 5x5, 3x3, 1. So bottom is 5x5, top is 1. That means:
- y = H+4: 5x5
- y = H+5: 5x5
- y = H+6: 3x3
- y = H+7: 1

That matches my first interpretation. Let me go with that (widest at bottom, tapering to 1 at top). It's a bit unusual but matches the spec's described order.

Actually, re-reading: "leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)". I think this describes building from the trunk upward: first two layers are 5x5, then a 3x3, then a single block on top. So yes:
- H+4: 5x5
- H+5: 5x5
- H+6: 3x3
- H+7: 1

Let me place leaves "only into air" — i.e., don't overwrite wood or other blocks, only fill empty cells.

For the 5x5 layer centered at (x, z): fill dx in [-2,2], dz in [-2,2] → but that's 5x5=25 cells. Center at (x,z). Place leaf if cell is air.

For 3x3: dx in [-1,1], dz in [-1,1].
For 1: just (x,z).

Let me write tree generation:
```
if (surfMat === 1 /* grass */) {
  const th = hash2(wx, wz);
  if (th < 0.02) {
    const top = H - 1; // surface y
    // trunk
    for (let ty = top+1; ty <= top+4; ty++) {
      if (ty < 80) setLocal(x, ty, z, 5);
    }
    // leaves
    const lt = top + 4;
    // 5x5 twice
    for (let dy = 0; dy < 2; dy++) {
      const ly = lt + dy;
      if (ly >= 80) continue;
      for (let dx = -2; dx <= 2; dx++)
        for (let dz = -2; dz <= 2; dz++)
          if (ly < 80) setLeaf(x+dx, ly, z+dz, 6);
    }
    // 3x3
    const ly3 = lt + 2;
    if (ly3 < 80)
      for (let dx = -1; dx <= 1; dx++)
        for (let dz = -1; dz <= 1; dz++)
          setLeaf(x+dx, ly3, z+dz, 6);
    // 1 on top
    const ly1 = lt + 3;
    if (ly1 < 80) setLeaf(x, ly1, z, 6);
  }
}
```

where setLeaf only sets if air.

Note: hash2 uses wx, wz. Good, deterministic per column.

### Meshing

Build one BufferGeometry per chunk. Loop all non-air blocks, for each of 6 sides check neighbor with global read; if air, add face. World coords for vertices, mesh at origin.

I need a function that given a chunk's blocks array produces a BufferGeometry.

Faces: 6 directions. For each, define 4 corner offsets and normal.

```
const FACES = [
  { dir: [+1,0,0], corners: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]], normal: [1,0,0] },
  { dir: [-1,0,0], corners: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]], normal: [-1,0,0] },
  { dir: [0,+1,0], corners: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]], normal: [0,1,0] },
  { dir: [0,-1,0], corners: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], normal: [0,-1,0] },
  { dir: [0,0,+1], corners: [[1,0,1],[1,1,1],[0,1,1],[0,0,1]], normal: [0,0,1] },
  { dir: [0,0,-1], corners: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]], normal: [0,0,-1] },
];
```

Hmm, I need to be careful with winding order for correct culling/facing. Let me think.

Actually, for MeshLambertMaterial with face culling (default frontSide? no, DoubleSide off means backSide culled). We want faces visible from outside, so normals point outward and winding is CCW when viewed from outside.

Let me define each face with 4 vertices in CCW order as seen from outside. Let me use a standard approach.

For a face at +X (right), the outward normal is +X. Vertices (as seen from +X looking toward -X, i.e., from outside):
- bottom-front? Let me use a known-good set.

Standard cube face vertex data (from three.js BoxGeometry):

Actually, let me just use a well-known face layout. I'll define positions and ensure CCW.

Let me use this approach: for each face, I store 4 points (unit cube corners) in an order that forms CCW winding when viewed from the direction of the normal.

Face +X (normal pointing +X):
Points: 
v0 = (1, 0, 0)
v1 = (1, 1, 0)
v2 = (1, 1, 1)
v3 = (1, 0, 1)
Viewed from +X (looking in -X direction), is v0→v1→v2→v3 CCW? Looking from +X toward origin, the z-axis points... hmm. Let me just trust and verify winding later; correctness matters less than not having backfaces. Actually if winding is wrong, faces pointing away from player get culled incorrectly and we'd see holes. To be safe, I could set material side = DoubleSide. But spec says ONE shared MeshLambertMaterial. It doesn't forbid DoubleSide. But DoubleSide doubles draw cost and can have z-fighting. For correctness though, let me get winding right.

Let me carefully derive. We view a face from outside, meaning from the side the normal points to. For the face to be visible, its 4 vertices must be listed in counter-clockwise order when projected onto the screen with the viewer on the normal side.

Convention: In three.js (right-handed, camera looks at -Z), a face is front-facing if its vertices are in CCW order when viewed from the front (from the normal side).

For +X face, normal = (1,0,0). Viewer at large +X looking toward -X. In this view, the screen's "right" is... let me set up: viewer eye at (large, 0, 0) looking at origin. Up is +Y. The view direction is -X. Screen right vector = up × viewDir? Let me use: right = normalize(cross(viewDir, up))? Actually screenRight = cross(up, -viewDir)... this is getting complicated.

Let me just use a concrete known-correct table. From the "cube face" pattern used in many voxel engines:

```
const dirs = [
  // [x, y, z], four corners (CCW from outside)
  [ 1, 0, 0], [[1,0,0],[1,1,0],[1,1,1],[1,0,1]],
  [-1, 0, 0], [[0,0,1],[0,1,1],[0,1,0],[0,0,1].reverse()...]
];
```

Hmm, let me look at this differently. I recall a common implementation:

```
const faces = [
  { normal:[1,0,0], verts:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  { normal:[-1,0,0], verts:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  { normal:[0,1,0], verts:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { normal:[0,-1,0], verts:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { normal:[0,0,1], verts:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
  { normal:[0,0,-1], verts:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] },
];
```

Let me verify winding for +X face. Vertices (in local, before adding block pos):
v0=(1,0,0), v1=(1,1,0), v2=(1,1,1), v3=(1,0,1).
Normal (1,0,0). 

To check CCW from outside: compute the signed area or use the fact that for a convex face, going CCW around the normal. Take edges: e1 = v1-v0 = (0,1,0), e2 = v2-v1 = (0,0,1). Cross product e1×e2 = (1*1-0*0, 0*0-0*1, 0*0-1*0) = (1, 0, 0). This equals the normal. For CCW winding with the right-hand rule, the cross of consecutive edge vectors (e1 × e2 where the triangle is v0,v1,v2) should point toward the viewer (same as normal). Here e1×e2 = (1,0,0) = normal. 

But wait, we have a quad, not triangle. The quad v0,v1,v2,v3 splits into triangles (v0,v1,v2) and (v0,v2,v3). For triangle (v0,v1,v2): cross((v1-v0),(v2-v0)) = cross((0,1,0),(0,1,1)) = (1*1-0*1, 0*0-0*1, 0*1-1*0) = (1,0,0). = normal. Good, front-facing. Triangle (v0,v2,v3): cross((v2-v0),(v3-v0)) = cross((0,1,1),(0,0,1)) = (1*1-1*0, 1*0-0*1, 0*0-1*0) = (1, 0, 0). Wait recompute: cross(a,b) = (a2*b3 - a3*b2, a3*b1 - a1*b3, a1*b2 - a2*b1). a=(0,1,1), b=(0,0,1). 
- x = a.y*b.z - a.z*b.y = 1*1 - 1*0 = 1
- y = a.z*b.x - a.x*b.z = 1*0 - 0*1 = 0
- z = a.x*b.y - a.y*b.x = 0*0 - 1*0 = 0
= (1,0,0) = normal. 

So +X face is correct CCW. Let me assume the others follow a consistent pattern and verify a couple.

-X face: verts [[0,0,1],[0,1,1],[0,1,0],[0,0,0]], normal (-1,0,0).
Triangle (v0,v1,v2): v0=(0,0,1),v1=(0,1,1),v2=(0,1,0).
cross((v1-v0),(v2-v0)) = cross((0,1,0),(0,1,-1)).
- x = 1*(-1) - 0*1 = -1
- y = 0*0 - 0*(-1) = 0
- z = 0*1 - 1*0 = 0
= (-1,0,0) = normal. 

+Y face: verts [[0,1,1],[1,1,1],[1,1,0],[0,1,0]], normal (0,1,0).
v0=(0,1,1),v1=(1,1,1),v2=(1,1,0).
cross((v1-v0),(v2-v0)) = cross((1,0,0),(1,0,-1)).
- x = 0*(-1) - 0*0 = 0
- y = 0*1 - 1*(-1) = 1
- z = 1*0 - 0*1 = 0
= (0,1,0) = normal. 

-Y face: verts [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], normal (0,-1,0).
v0=(0,0,0),v1=(1,0,0),v2=(1,0,1).
cross((1,0,0),(1,0,1)).
- x = 0*1 - 0*0 = 0
- y = 0*1 - 1*1 = -1
- z = 1*0 - 0*1 = 0
= (0,-1,0) = normal. 

+Z face: verts [[1,0,1],[1,1,1],[0,1,1],[0,0,1]], normal (0,0,1).
v0=(1,0,1),v1=(1,1,1),v2=(0,1,1).
cross((v1-v0),(v2-v0)) = cross((0,1,0),(-1,1,0)).
- x = 1*0 - 0*1 = 0
- y = 0*(-1) - 0*0 = 0
- z = 0*1 - 1*(-1) = 1
= (0,0,1) = normal. 

-Z face: verts [[0,0,0],[0,1,0],[1,1,0],[1,0,0]], normal (0,0,-1).
v0=(0,0,0),v1=(0,1,0),v2=(1,1,0).
cross((0,1,0),(1,1,0)).
- x = 1*0 - 0*1 = 0
- y = 0*1 - 0*0 = 0
- z = 0*1 - 1*1 = -1
= (0,0,-1) = normal. 

All 6 faces verified CCW. Now I need to assign per-vertex normals equal to the face normal, and per-vertex colors equal to the base color multiplied by lighting factor based on face.

Lighting factors: top faces 1.0, sides 0.8, bottoms 0.55.
- +Y (up): 1.0
- -Y (down): 0.55
- others (±X, ±Z): 0.8

For each visible face, the 4 corners get the same color (base color * factor). Normals = face normal.

Now the meshing algorithm:
```
function buildChunkMesh(cx, cz) {
  const c = getChunk(cx, cz);
  if (!c || !c.blocks) return; // no data
  const positions = [];
  const normals = [];
  const colors = [];
  const indices = [];
  for (let x = 0; x < 16; x++)
    for (let y = 0; y < 80; y++)
      for (let z = 0; z < 16; z++) {
        const id = c.blocks[(y*16+z)*16+x];
        if (id === 0) continue;
        const wx = cx*16 + x, wy = y, wz = cz*16 + z;
        for (const face of FACES) {
          const nx = wx + face.dir[0], ny = wy + face.dir[1], nz = wz + face.dir[2];
          if (getBlock(nx, ny, nz) === 0) {
            // visible face
            const color = new Color(blockColors[id]);
            const factor = faceLight(face);
            color.multiplyScalar(factor);
            for (const c of face.corners) {
              positions.push(wx + c[0], wy + c[1], wz + c[2]);
              normals.push(...face.normal);
              colors.push(color.r, color.g, color.b);
            }
            indices.push(...); // 2 triangles: 0,1,2, 0,2,3
          }
        }
      }
  const geo = new BufferGeometry();
  geo.setAttribute('position', new Float32Array(positions));
  geo.setAttribute('normal', new Float32Array(normals));
  geo.setAttribute('color', new Float32Array(colors));
  geo.setIndex(indices);
  ...
  if (c.mesh) { dispose }
  c.mesh = new Mesh(geo, blockMaterial);
  scene.add(c.mesh);
}
```

Wait, but the mesh should be "at the origin" — meaning we add it to scene at (0,0,0) and use world coordinates in the geometry. Since chunk cx, cz covers world [cx*16, cx*16+16) etc., and geometry uses world coords, placing mesh at scene origin (0,0,0) means the geometry occupies the correct world region. 

But wait — there's subtlety. If the mesh is at origin and geometry has world coords, then for chunk at cx=1 (world x=16..31), the mesh at (0,0,0) has geometry spanning x=16..31. Correct. Good.

Hmm, but actually there's a concern: chunks can have negative cx. E.g., cx=-1 → world x=-16..-1. Geometry spans those. Mesh at origin. Correct.

Now, "keep the mesh at the origin" — yes, add to scene at position (0,0,0).

blockMaterial = new MeshLambertMaterial({ vertexColors: true }).

Wait, vertexColors with a color attribute. In r128, MeshLambertMaterial supports vertexColors. Good.

Now neighbor checking for meshing: "build meshes for chunks within 4 chunks whose 4 neighbors already have data". So when we have data for a chunk, we need to check its 4 horizontal neighbors' blocks for face culling (a block on the border might have an air neighbor in the adjacent chunk that's actually solid). The global getBlock reads across chunk boundaries, so it works regardless. But we only build a chunk's mesh if its neighbors have data (so the border faces are correct). Actually, since getBlock reads neighbor chunk data, if the neighbor has no data (air), the border face would be treated as air → we'd draw the face. That's wrong if the neighbor actually has a solid block but hasn't generated yet. Hence the requirement: build mesh only if 4 neighbors have data.

Let me structure the update loop:

Per frame:
1. Determine player's chunk (pcx, pcz).
2. Chunks within 5 of player (in terms of Chebyshev or Euclidean distance?) "within 5 chunks of the player (max 4 per frame)". Let me use a radius and queue by distance.

Let me collect all chunk keys within radius 5 (Chebyshev: |dcx|<=5, |dcz|<=5), compute distance, sort ascending, take up to 4, generate their data (generateChunk), mark ready.

3. Build meshes: among chunks with data, those within 4 of player whose 4 neighbors have data, take up to 2, build mesh.

4. Cleanup: chunks farther than 7 from player → remove mesh, dispose geometry, delete entry.

Wait, "for chunks farther than 7, remove the mesh, dispose its geometry and delete the entry." So radius for keeping is 7. But generation radius is 5, mesh radius 4. Let me reconcile: we generate within 5, mesh within 4, but keep entries up to 7. That's a bit odd but fine — chunks between 5 and 7 stay (mesh stays? or just entry?). "remove the mesh, dispose its geometry and delete the entry" for farther than 7. So chunks within 7 keep their entry and mesh; beyond 7 removed. Generation happens within 5, meshing within 4. Chunks 5-7 have data and mesh but aren't regenerated... hmm, actually they'd still have their mesh from before. Let me just implement straightforwardly:

- generateQueue: chunks with |dc| <= 5, sorted by dist, take 4, generate data.
- meshQueue: chunks with data, |dc| <= 4, and 4 neighbors have data, sorted by dist, take 2, build mesh.
- cleanup: chunks with |dc| > 7: dispose mesh, delete entry.

Actually wait, if we only keep within 7 but generate within 5, then a chunk at distance 6 wouldn't get generated this frame but might already have data from before. That's fine.

Hmm, but there's a subtle issue: we never generate chunks between 5 and 7 unless they were previously generated. Since the player moves, chunks come into the 5-radius over time, so they get generated. Chunks at 5-7 that had data keep it. Fine.

Let me use Euclidean distance for sorting (dcx^2 + dcz^2).

Actually, let me reconsider: "within 5 chunks of the player" — I'll use Chebyshev distance <= 5 for inclusion, then sort by Euclidean for priority. Or just Euclidean <= 5. Let me use Euclidean <= 5 for generation, <= 4 for meshing, and > 7 for removal. Actually to be safe with the "max 4 per frame" and "max 2 per frame", let me:

```
function updateChunks() {
  const pcx = floor(playerChunkX), pcz = floor(playerChunkZ);
  // gather candidate keys
  const gens = [], meshes = [];
  for (let dx=-7; dx<=7; dx++) for (let dz=-7; dz<=7; dz++) {
    const cx = pcx+dx, cz = pcz+dz;
    const key = cx+","+cz;
    const c = chunkMap.get(key);
    const d2 = dx*dx+dz*dz;
    if (d2 > 49) continue; // > 7
    if (c && c.mesh) {
      // keep; maybe rebuild not needed
    }
    if (d2 <= 25 && (!c || !c.blocks)) { gens.push({cx,cz,d2,key}); }
    if (c && c.blocks && d2 <= 16) {
      // check neighbors
      if (neighborHasData(cx-1,cz) && neighborHasData(cx+1,cz) && neighborHasData(cx,cz-1) && neighborHasData(cx,cz+1)) {
        meshes.push({cx,cz,d2,key});
      }
    }
  }
  gens.sort((a,b)=>a.d2-b.d2);
  for (let i=0;i<Math.min(4,gens.length);i++) generateChunk(gens[i].cx, gens[i].cz);
  meshes.sort((a,b)=>a.d2-b.d2);
  for (let i=0;i<Math.min(2,meshes.length);i++) buildChunkMesh(meshes[i].cx, meshes[i].cz);
  // cleanup
  for (const [key, c] of chunkMap) {
    const [cs, czs] = key.split(',').map(Number);
    if (Math.abs(cs-pcx)>7 || Math.abs(czs-pcz)>7) {
      if (c.mesh) { scene.remove(c.mesh); c.mesh.geometry.dispose(); }
      chunkMap.delete(key);
    }
  }
}
```

Hmm wait, there's a problem: when I delete a chunk entry beyond radius 7, but a neighboring chunk within radius 4 needs it for neighbor data... Actually the neighbor check uses getBlock which reads neighbor chunk data. If neighbor was deleted, getBlock returns air. But we only delete beyond 7, and mesh within 4, so neighbors within 4 are always present. Fine.

But there's another subtlety: the neighborHasData check — I check the 4 horizontal neighbors. But what about vertical? Not needed since height is fixed 80 and top/bottom faces don't cross chunk boundaries horizontally. Actually top/bottom faces are within the same chunk (y from 0-79). Only X/Z neighbors matter for border faces. Good.

Now, generating data: generateChunk fills blocks. But I also need getOrCreateChunk to create the entry. Let me have generateChunk create it.

Also initial spawn: player spawns at x=8, z=8, above terrain. Chunk (0,0) needs data. On start, I should pre-generate some chunks so the world exists. Let me generate chunks around spawn upfront (before the game loop) so the player doesn't fall through. Let me generate a handful of chunks near spawn at init.

Actually, the player needs terrain under them to spawn on. Let me generate chunks in a small area at init (e.g., within radius 1 or 2) so spawn is safe.

Let me generate at init: chunks within radius 2 of (0,0) → 25 chunks. That's fast enough.

### Player physics

PerspectiveCamera fov 75, far 400. Rotation order YXZ. yaw/pitch.

Player box: half-width 0.3, height 1.8, eye 1.62. Spawn above terrain at x=8, z=8.

Gravity 25, jump velocity 8.5, WASD 5.5 m/s relative to yaw.

Axis-separated collision against all non-air blocks. Move per axis, revert on overlap; landing sets on-ground.

Falling below y=-20 teleports to spawn.

Let me implement collision. Player AABB: from (x-wx, y, z-wz) to (x+wx, y+1.8, z+wz) where wx=0.3, wz=0.3, and y is feet position. Eye at y+1.62.

Collision: for each axis, move, then check if AABB overlaps any solid block. If yes, revert that axis (and set velocity appropriately).

To check overlap, I need to test all blocks within the player's AABB. For each integer block position in the AABB range, check getBlock != 0.

Let me write:
```
function collides(ax, ay, az, vx, vy, vz) {
  // AABB from (ax,ay,az) to (ax+0.6, ay+1.8, az+0.6)
  const minX = Math.floor(ax), maxX = Math.floor(ax+0.6);
  const minY = Math.floor(ay), maxY = Math.floor(ay+1.8);
  const minZ = Math.floor(az), maxZ = Math.floor(az+0.6);
  for (let x=minX;x<=maxX;x++) for (let y=minY;y<=maxY;y++) for (let z=minZ;z<=maxZ;z++) {
    if (getBlock(x,y,z) !== 0) return true;
  }
  return false;
}
```

Movement:
```
// horizontal first? or full? Let me do per-axis full movement.
// Move X
if (!collides(px,py,pz, px+dx, py, pz)) px += dx; else { /* blocked */ }
```

Actually let me do the standard: move each axis independently, reverting if collision.

```
function moveAxis(axis, amount) {
  if (axis === 'x') {
    if (!collides(px,py,pz, px+amount, py, pz)) px += amount;
  } else if (axis === 'y') {
    if (!collides(px,py,pz, px, py+amount, pz)) { py += amount; onGround = false; }
    else { if (amount < 0) onGround = true; } // landed or jumped
  } else if (axis === 'z') {
    if (!collides(px,py,pz, px, py, pz+amount)) pz += amount;
  }
}
```

Hmm, but the collision check during movement uses current py. When moving Y, if no collision, py += amount. If collision, revert. But we also need to detect landing: if moving down and blocked, set onGround = true. If moving up and blocked, stop upward.

Actually the collides check should be against the proposed new position. Let me refine:

```
// X
let nx = px + dx;
if (!collides(px,py,pz, nx, py, pz)) px = nx;
// Z
let nz = pz + dz;
if (!collides(px,py,pz, px, py, nz)) pz = nz;
// Y
let ny = py + dy;
if (!collides(px,py,pz, px, ny, pz)) {
  py = ny;
  onGround = false;
} else {
  if (dy < 0) onGround = true; // moving down, hit ground
  // if dy>0, just blocked, stay
}
```

Wait, but collides(px,py,pz, px, ny, pz) — the third param is the proposed position. Let me define collides as collides(curX,curY,curZ, newX,newY,newZ) returning true if the AABB at (newX,newY,newZ) overlaps any solid. Actually simpler: collides(posX, posY, posZ) checks if AABB at that position overlaps solids. Let me redefine:

```
function collides(posX, posY, posZ) {
  const minX = Math.floor(posX), maxX = Math.floor(posX + 0.6);
  const minY = Math.floor(posY), maxY = Math.floor(posY + 1.8);
  const minZ = Math.floor(posZ), maxZ = Math.floor(posZ + 0.6);
  for (x..) for (y..) for (z..) if (getBlock(x,y,z) !== 0) return true;
  return false;
}
```

Then:
```
if (!collides(px+dx, py, pz)) px += dx;
if (!collides(px, py+dy, pz)) py += dy; else { if (dy < 0) onGround = true; }
if (!collides(px, py, pz+dz)) pz += dz;
```

This is cleaner. When dy<0 and collides at py+dy, we set onGround=true (landed). When dy>0 and collides, we're headbutting, stay. When we move and don't collide, py updates.

But there's an issue: when onGround and we move up a block (1 block high), py+1 might collide, good. But sliding along walls: moving X while against a wall → blocked, Z free → moves. Good. Moving diagonally into corner might get stuck but acceptable.

Now gravity and jumping:
```
vy -= gravity * dt; // gravity 25
vy = min(vy, ...)? 
if (onGround && jumpPressed) vy = 8.5;
py += vy * dt (via moveAxis y)
if (py < -20) { reset to spawn }
```

Actually let me integrate: py += vy*dt each frame, applying collision.

Jump: onGround and space pressed → vy = 8.5.

Let me handle jump as: if (onGround && jump) vy = 8.5. onGround resets when we move up.

Input: WASD movement relative to yaw. Forward = -Z in world? Let me define: yaw is rotation around Y. Camera forward direction based on yaw. When pressing W, move in forward direction (horizontal). 

Direction: 
- forward.x = -sin(yaw)? Let me think. In three.js, camera with rotation YXZ. yaw rotates around Y. Default camera looks at -Z. After yaw rotation, forward = (sin(yaw)... ). Let me define:
  - moveForward vector: ( -sin(yaw) * ... ). Hmm.

Let me define movement based on yaw:
```
const forward = { x: -Math.sin(yaw), z: -Math.cos(yaw) };  // hmm
```

Actually let me think physically. If yaw=0, camera looks along -Z (toward negative z). Moving "forward" (W) should move toward -Z. So forward vector at yaw=0 = (0, 0, -1). 

General: forward = (-sin(yaw)??). Let me parametrize yaw as angle rotated from -Z toward +X. Rotating around Y by angle θ: a vector (0,0,-1) rotated by θ around Y becomes (sin θ? ). Rotation around Y: x' = x cosθ + z sinθ... wait. Rotation matrix around Y:
[ cosθ, 0, sinθ ]
[ 0,    1, 0    ]
[-sinθ, 0, cosθ ]
Applied to (0,0,-1): x' = cosθ*0 + 0 + sinθ*(-1) = -sinθ. z' = -sinθ*0 + 0 + cosθ*(-1) = -cosθ. So forward = (-sinθ, 0, -cosθ). At θ=0: (0,0,-1). Good. At θ=90° (π/2): (-1, 0, 0) — looking toward -X. 

So forward = (-sin(yaw), 0, -cos(yaw)). Right vector (strafe) = forward rotated -90° around Y = (cosθ, 0, -sinθ)? Let me compute: right = cross(forward, up)? In a right-handed system, right = cross(forward, up)?? Let me just define right = (cos(yaw), 0, -sin(yaw)). At θ=0: (1, 0, 0) pointing +X, which is to the right when looking -Z. Good.

Movement:
```
const speed = 5.5;
let ix = 0, iz = 0;
if (W) { ix += forward.x; iz += forward.z; }
if (S) { ix -= forward.x; iz -= forward.z; }
if (D) { ix += right.x; iz += right.z; }
if (A) { ix -= right.x; iz -= right.z; }
normalize (ix, iz); multiply by speed.
```

Horizontal movement is direct (no collision-based damping needed, but we apply collision per axis).

Now camera: position = (px, py + 1.62, pz). Rotation via euler with order YXZ. Set euler.set(yaw, pitch, 0, 'YXZ'). camera.rotation.copy(euler).

Mouse look: on mousemove while locked, yaw -= sensitivity * dx, pitch -= sensitivity * dy, clamp pitch to [-π/2+eps, π/2-eps].

Wait, sensitivity ~0.002. Look around: moving mouse right should turn yaw right (view rotates). Standard: yaw -= dx * sens. pitch -= dy * sens. Clamping pitch.

### Break & place

Raycast from camera center (max distance 6) against chunk meshes. Three.js Raycaster with scene. But we need to cast against all chunk meshes. Raycaster.set(camera.position, direction). intersectObjects(chunkMeshes, false). Get first hit with distance <= 6.

From hit point p and face normal n:
- break target = floor(p - n*0.5)
- place cell = floor(p + n*0.5)

per component: floor each coordinate.

Outline targeted block with black wireframe box. Create a BoxHelper or LineSegments wireframe. Position it at the targeted block's world center.

Only while locked:
- left click → set target to air (not at y 0). setBlock(btx, bty, btz, 0). If bty === 0, skip (unbreakable floor).
- right click → place selected block if cell is air and doesn't overlap player.

After edit rebuild the chunk, and also neighbor chunk if block on chunk border.

Rebuild function:
```
function rebuildChunk(cx, cz) {
  const c = getChunk(cx, cz);
  if (!c) return;
  buildChunkMesh(cx, cz); // rebuilds mesh (disposes old)
}
```

Border check: if btx in {0,15} → rebuild neighbor in X. If btz in {0,15} → rebuild neighbor in Z. Similarly for place cell.

Let me combine: after editing block at (bt,bt,bb), determine which chunk it's in (should be same chunk). Rebuild that chunk. Also if x==0 rebuild cx-1 chunk, if x==15 rebuild cx+1. Same for z.

Actually the edited block is in chunk (floor(bt/16), floor(bb/16)). Rebuild it. If x==0 → neighbor (cx-1). If x==15 → (cx+1). If z==0 → (cz-1). If z==15 → (cz+1).

### Hotbar

7 slots: grass, dirt, stone, sand, wood, leaves, snow → block IDs 1,2,3,4,5,6,7. Each a colored square with number. Selected slot white border. Keys 1-7 or mouse wheel (wraps).

Selected slot stored in `selected` (0-6). Map to block ID = selected+1.

Mouse wheel: change selected by ±1, wrap.

### Sky, clouds, water

- Background 0x87ceeb, fog 0x87ceeb, far 400 → fog near maybe 40? "matching fog (about 40 to 110)". Fog exp? Let me use Fog(0x87ceeb, 40, 110).
- Ambient 0.65 + directional 0.8.
- ~25 flat white transparent clouds at height ~90, drifting, wrapping around player.
- Water: large semi-transparent blue plane at height 14.3, re-centered on player each frame.

Clouds: 25 boxes, transparent white, at y~90. Each frame, reposition to stay around player (x, 90, z) wrapping — "drifting and wrapping around the player". Let me have clouds drift in X, and reposition Z around player. Actually "wrapping around the player" — keep clouds near player. Let me just move clouds slowly in +X, and if a cloud moves too far from player in x or z, wrap it back. Simpler: each cloud has a base position; each frame set cloud.position.x = (cloud.x + speed) but keep relative to player by wrapping. Let me do: cloud.pos.x += drift*dt; then if (cloud.pos.x - player.x > 80) cloud.pos.x -= 160; similarly for z maybe not. Let me keep it simple: clouds are a group; move group in X; wrap group relative to player.

Actually simplest robust approach: maintain each cloud's position; each frame, cloud.x += drift; if cloud.x < player.x - 60, cloud.x += 120; if cloud.x > player.x + 60, cloud.x -= 120. Same for z optionally. This keeps clouds around player.

Water plane: PlaneGeometry large (e.g., 200x200), rotation -Math.PI/2 (to be horizontal), material transparent blue with opacity ~0.7. Position y=14.3, re-center x,z on player each frame.

### UI

Start overlay: title, controls list, "Click to play". Reappears when pointer lock released.

Body no margins, fullscreen canvas, resize handler.

### Pointer lock

Clicking start overlay requests pointer lock. Mouse look only while locked. On pointerlockchange, if not locked, show overlay.

Let me set up: overlay click → document.pointerLockElement requested. Add mousemove listener (checks document.pointerLockElement). mousedown listeners for left/right click (check locked). Context menu suppressed (preventDefault on contextmenu).

Now let me also handle: clicking while locked should also request pointer lock? No — once locked, clicking doesn't unlock. The overlay appears when unlocked.

Let me structure the code.

Let me also make sure raycasting uses the chunk meshes array (global). Keep `chunkMeshes = []`. When building a mesh, push to array (and remove disposed ones). Actually simpler: iterate over chunkMap values that have mesh. But raycaster needs an array. Let me maintain chunkMeshes array; when building mesh push; when disposing splice.

Let me maintain a helper to add/remove.

Now let me write the actual code.

Let me also double check the block color lighting: "multiply the block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms." So per-face factor. Implemented in meshing.

Let me now also consider the "ONE shared MeshLambertMaterial". vertexColors: true. Good.

Now, about generateChunk creating chunks and the initial state. Let me write getOrCreateChunk:
```
function getOrCreateChunk(cx, cz) {
  const key = cx+","+cz;
  let c = chunkMap.get(key);
  if (!c) { c = { blocks: new Uint8Array(16*80*16), mesh: null }; chunkMap.set(key, c); }
  return c;
}
```

generateChunk(cx, cz):
```
function generateChunk(cx, cz) {
  const c = getOrCreateChunk(cx, cz);
  if (c.blocksGen) return; // already generated
  c.blocksGen = true;
  const b = c.blocks;
  for (let x=0;x<16;x++) for (let z=0;z<16;z++) {
    const wx = cx*16+x, wz = cz*16+z;
    const m = fractal2(wx*0.004, wz*0.004);
    const h = fractal2(wx*0.02, wz*0.02);
    const H = Math.floor(5 + m*m*58 + h*10);
    let dirtMat = 2;
    if (H <= 16) dirtMat = 4; else if (H >= 37) dirtMat = 3;
    let surf;
    if (H >= 46) surf = 7; else if (H >= 37) surf = 3; else if (H <= 16) surf = 4; else surf = 1;
    for (let y=0;y<80;y++) {
      let id;
      if (y===0) id=3;
      else if (y < H-4) id=3;
      else if (y < H-1) id=dirtMat;
      else id=surf;
      // caves
      if (y>=3 && y<H-2) {
        if (noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) id=0;
      }
      b[(y*16+z)*16+x] = id;
    }
    // trees
    if (surf === 1 && hash2(wx, wz) < 0.02) {
      const top = H-1;
      for (let ty=top+1; ty<=top+4; ty++) if (ty<80) b[(ty*16+z)*16+x]=5;
      const lt = top+4;
      for (let dy=0; dy<2; dy++) {
        const ly = lt+dy; if (ly>=80) continue;
        for (let dx=-2;dx<=2;dx++) for (let dz=-2;dz<=2;dz++)
          if (ly<80 && b[(ly*16+(z+dz+16)%16)*16+((x+dx+16)%16)]===0) b[...]=6;
      }
      ...
    }
  }
}
```

Wait, tree leaves use local coords x,z within chunk. Since x is already 0-15 and dx in -2..2, x+dx can be -2..17. But tree should be within the chunk? "the trunk fits inside the chunk" — the trunk is at (x,z) which is within chunk. Leaves extend 2 blocks out, possibly into neighbor chunk. That's fine because leaves in neighbor chunk would need that chunk's data. Hmm, but if leaves cross into neighbor chunk and neighbor isn't generated/meshed, we might have issues. Actually leaves are just blocks; if they're placed in this chunk's array at wrapped coordinates, that's wrong — a block at x=-1 belongs to the previous chunk.

To avoid this complexity, let me restrict leaf placement to within the current chunk (clamp or skip out-of-range). Actually, "only into air" and within chunk. Let me place leaves only where 0 <= x+dx < 16 and 0 <= z+dz < 16. This keeps leaves in-chunk. The tree might look slightly clipped at chunk borders but that's acceptable and avoids cross-chunk issues.

Actually, better: place leaves with wrapping into the chunk array using modulo, but that scatters them weirdly. Let me just clamp: only place if in-bounds. Simplest and safe.

Let me write leaf placement:
```
function placeLeaf(b, x, y, z, id) {
  if (x<0||x>=16||z<0||z>=16||y<0||y>=80) return;
  if (b[(y*16+z)*16+x] === 0) b[(y*16*z)*16+x]=id; // typo
}
```
Fix: `b[(y*16+z)*16+x]`.

OK. Let me finalize tree:
```
if (surf === 1 && hash2(wx, wz) < 0.02) {
  const top = H - 1;
  // trunk
  for (let ty = top+1; ty <= top+4; ty++) if (ty < 80) b[(ty*16+z)*16+x] = 5;
  // canopy
  const lt = top + 4;
  for (let dy = 0; dy < 2; dy++) {
    const ly = lt + dy;
    if (ly >= 80) continue;
    for (let dx = -2; dx <= 2; dx++) for (let dz = -2; dz <= 2; dz++)
      placeLeaf(b, x+dx, ly, z+dz, 6);
  }
  const ly3 = lt + 2;
  if (ly3 < 80) {
    for (let dx=-1;dx<=1;dx++) for (let dz=-1;dz<=1;dz++) placeLeaf(b, x+dx, ly3, z+dz, 6);
  }
  const ly1 = lt + 3;
  if (ly1 < 80) placeLeaf(b, x, ly1, z, 6);
}
```

Good.

Now, the hash2 for trees uses wx, wz (global). Deterministic per column. Good.

Let me now also reconsider the fractal noise normalization and that m*m gives the right range. fractal2 returns 0..1. m*m in [0,1]. H = 5 + m²·58 + h·10. Good.

Now meshing details. Let me write buildChunkMesh:
```
function buildChunkMesh(cx, cz) {
  const c = getChunk(cx, cz);
  if (!c || !c.blocks || !c.blocksGen) return;
  const pos=[], nor=[], col=[], idx=[];
  for (let x=0;x<16;x++) for (let y=0;y<80;y++) for (let z=0;z<16;z++) {
    const id = c.blocks[(y*16+z)*16+x];
    if (!id) continue;
    const wx=cx*16+x, wy=y, wz=cz*16+z;
    for (let f=0;f<6;f++) {
      const face = FACES[f];
      const nx=wx+face.dir[0], ny=wy+face.dir[1], nz=wz+face.dir[2];
      if (getBlock(nx,ny,nz) === 0) {
        const color = new THREE.Color(blockColors[id]);
        color.multiplyScalar(face.light);
        for (let k=0;k<4;k++) {
          const c2 = face.corners[k];
          pos.push(wx+c2[0], wy+c2[1], wz+c2[2]);
          nor.push(face.normal[0], face.normal[1], face.normal[2]);
          col.push(color.r, color.g, color.b);
        }
        idx.push(pos.length/3-4, pos.length/3-3, pos.length/3-2);
        idx.push(pos.length/3-4, pos.length/3-2, pos.length/3-1);
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32Array(pos));
  geo.setAttribute('normal', new THREE.Float32Array(nor));
  geo.setAttribute('color', new THREE.Float32Array(col));
  geo.setIndex(idx);
  geo.computeBoundingSphere?.(); // optional
  if (c.mesh) { 
    chunkMeshes.splice(chunkMeshes.indexOf(c.mesh), 1);
    scene.remove(c.mesh); c.mesh.geometry.dispose();
  }
  const mesh = new THREE.Mesh(geo, blockMaterial);
  mesh.position.set(0,0,0);
  scene.add(mesh);
  c.mesh = mesh;
  chunkMeshes.push(mesh);
}
```

Wait, indices: I push 4 vertices per face, so after pushing, pos.length/3 is the count. The 4 new indices are (count-4),(count-3),(count-2),(count-1). Triangles: (0,1,2),(0,2,3) → (count-4,count-3,count-2) and (count-4,count-2,count-1). Yes that's what I wrote. Good.

blockColors: array indexed by id (1-7). blockColors = [0, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff].

FACES with light:
```
const FACES = [
  { dir:[1,0,0], normal:[1,0,0], light:0.8, corners:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
  { dir:[-1,0,0], normal:[-1,0,0], light:0.8, corners:[[0,0,1],[0,1,1],[0,1,0],[0,0,1].reverse()...] }
];
```
Wait I need the correct corners from my verification. Let me list:
- f0 (+X): normal [1,0,0], light 0.8, corners [[1,0,0],[1,1,0],[1,1,1],[1,0,1]]
- f1 (-X): normal [-1,0,0], light 0.8, corners [[0,0,1],[0,1,1],[0,1,0],[0,0,0]]
- f2 (+Y): normal [0,1,0], light 1.0, corners [[0,1,1],[1,1,1],[1,1,0],[0,1,0]]
- f3 (-Y): normal [0,-1,0], light 0.55, corners [[0,0,0],[1,0,0],[1,0,1],[0,0,1]]
- f4 (+Z): normal [0,0,1], light 0.8, corners [[1,0,1],[1,1,1],[0,1,1],[0,0,1]]
- f5 (-Z): normal [0,0,-1], light 0.8, corners [[0,0,0],[0,1,0],[1,1,0],[1,0,0]]

Good.

Now the raycast for break/place. Let me use THREE.Raycaster.

```
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
function updateTarget() {
  raycaster.set(camera.position, camera.getWorldDirection(vec));
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  let hit = null;
  for (const h of hits) if (h.distance <= 6) { hit = h; break; }
  target = hit;
}
```

Actually intersectObjects returns all intersections; I want the closest with distance <= 6. intersectObjects sorts by distance already. So hits[0] is closest. Check hits[0].distance <= 6.

```
function updateTarget() {
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);
  raycaster.set(camera.position, dir);
  raycaster.far = 6;
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length && hits[0].distance <= 6) {
    target = hits[0];
  } else target = null;
}
```

target.hit.point = p (Vector3), target.face.normal = n (Vector3).

Break target: floor(p - n*0.5). Place: floor(p + n*0.5).

```
const bt = new THREE.Vector3().copy(p).addScaledVector(n, -0.5);
const bx = Math.floor(bt.x), by = Math.floor(bt.y), bz = Math.floor(bt.z);
const pc = new THREE.Vector3().copy(p).addScaledVector(n, 0.5);
const px2 = Math.floor(pc.x), py2 = Math.floor(pc.y), pz2 = Math.floor(pc.z);
```

Wireframe outline: use THREE.BoxGeometry(1.001,1.001,1.001) + WireframeGeometry, or BoxHelper. Let me use a LineSegments with WireframeGeometry:
```
outlineGeo = new THREE.WireframeGeometry(new THREE.BoxGeometry(1,1,1));
outline = new THREE.LineSegments(outlineGeo, new THREE.LineBasicMaterial({color:0x000000}));
outline.visible = false;
scene.add(outline);
```
Position at (bx+0.5, by+0.5, bz+0.5) when targeting.

Actually WireframeGeometry might be deprecated in r128? Let me check. In r128, WireframeGeometry exists. Alternatively use BoxHelper. BoxHelper needs setFromObject or setFromCenteredSphere. Let me use a simpler approach: create a BoxGeometry and get its EdgesGeometry? Hmm. Let me just use THREE.BoxHelper:
```
outline = new THREE.BoxHelper(new THREE.Object3D(), 0x000000);
outline.visible = false;
```
BoxHelper takes an object and color. setBoundsFromObject? Actually BoxHelper.fromMatrixOmitted... Let me use:
```
const helperObj = new THREE.Object3D();
scene.add(helperObj);
outline = new THREE.BoxHelper(helperObj, 0x000000);
```
Then each frame if targeting: outline.position.set(bx+0.5,by+0.5,bz+0.5); outline.update(); visible=true. BoxHelper scales to bounding box of the object's matrix. If I set position to block center and call update, it creates a 1-unit box around it? BoxHelper uses the object's world matrix bounding box. An Object3D at (bx+0.5,...) with no scale has an implicit bounding box? Object3D default geometry bounding sphere is null... BoxHelper might not work well with empty Object3D.

Let me use WireframeGeometry approach which is reliable:
```
const box = new THREE.BoxGeometry(1.002,1.002,1.002);
const wf = new THREE.WireframeGeometry(box);
outline = new THREE.LineSegments(wf, new THREE.LineBasicMaterial({color:0x000000}));
outline.visible = false;
scene.add(outline);
```
Position at block center. This draws a wireframe cube slightly larger than 1 unit. Good.

But WireframeGeometry in newer three.js is deprecated but still in r128. Let me verify r128 has it. Yes, WireframeGeometry exists up to around r152ish, deprecated later. r128 fine.

Actually, to be safe, let me construct line segments manually from BoxGeometry.attributes.position with index. Simpler: use WireframeGeometry. I'll trust r128.

Hmm, let me reconsider — maybe safer to use THREE.EdgesGeometry? That also exists. Or just build LineSegments from a BoxGeometry's position attribute (non-indexed). BoxGeometry(1) is indexed. Let me use non-indexed: `new THREE.BoxGeometry(1,1,1)` — in r128 BoxGeometry is indexed by default. To get non-indexed, need .toNonIndexed() or use a different approach.

Let me just use WireframeGeometry. It's cleanest.

Actually, I realize there might be an even simpler robust method: create the wireframe from a plain BoxGeometry and use its index. Let me do:
```
const g = new THREE.BoxGeometry(1.01,1.01,1.01);
const wf = new THREE.WireframeGeometry(g); // r128 has this
outline = new THREE.LineSegments(wf, new THREE.LineBasicMaterial({color:0x000000, depthTest:false}));
```
depthTest false so it shows through blocks. Good.

Now break/place handling on click:
```
document.addEventListener('mousedown', (e) => {
  if (!document.pointerLockElement) return;
  if (e.button === 0) { // break
    if (target && target.hit) {
      const [bx,by,bz] = breakCoords;
      if (by !== 0) {
        setBlock(bx,by,bz,0);
        editChunk(bx,bz);
      }
    }
  } else if (e.button === 2) { // place
    if (target && target.hit) {
      const [px,py,pz] = placeCoords;
      if (getBlock(px,py,pz) === 0) {
        // check not overlapping player
        if (!aabbOverlapsBlock(px,py,pz)) {
          setBlock(px,py,pz, selectedBlockId);
          editChunk(px,pz);
        }
      }
    }
  }
});
```

Wait, setBlock needs the chunk to exist. For break, target block is within a mesh chunk, so it exists. For place, the cell is adjacent; if it's air and within a generated chunk, fine. But if the cell is in an ungenerated chunk, setBlock would create an empty chunk (no terrain) — we shouldn't place there. Let me guard: only place if the chunk at that block has data. Actually, the raycast hits generated chunk meshes, so the adjacent place cell is within/border of a generated chunk. Since we only build meshes for chunks with data and their neighbors have data, the place cell (p + n*0.5) is within 0.5 of the surface, so within the same chunk or immediate neighbor which has data. So setBlock on existing chunk is fine. But to be safe, let me check the target chunk exists (c.blocksGen). If not, skip.

setBlock:
```
function setBlock(wx, wy, wz, id) {
  if (wy < 0 || wy >= 80) return;
  const cx = Math.floor(wx/16), cz = Math.floor(wz/16);
  const lx = ((wx % 16)+16)%16, lz = ((wz%16)+16)%16;
  const c = getChunk(cx, cz);
  if (!c || !c.blocksGen) return;
  c.blocks[(wy*16+lz)*16+lx] = id;
}
```

editChunk(wx, wz): rebuild the chunk containing the block and neighbors if on border.
```
function editChunk(wx, wz) {
  const cx = Math.floor(wx/16), cz = Math.floor(wz/16);
  rebuildChunk(cx, cz);
  const lx = ((wx%16)+16)%16, lz = ((wz%16)+16)%16;
  if (lx === 0) rebuildChunk(cx-1, cz);
  else if (lx === 15) rebuildChunk(cx+1, cz);
  if (lz === 0) rebuildChunk(cx, cz-1);
  else if (lz === 15) rebuildChunk(cx, cz+1);
}
```

rebuildChunk:
```
function rebuildChunk(cx, cz) {
  const c = getChunk(cx, cz);
  if (!c || !c.blocksGen) return;
  buildChunkMesh(cx, cz);
}
```

aabbOverlapsBlock(bx, by, bz): check if block at (bx,by,bz) overlaps player AABB.
```
function aabbOverlapsBlock(bx, by, bz) {
  return (px+0.3 > bx && px-0.3 < bx+1) &&
         (py+1.8 > by && py < by+1) &&
         (pz+0.3 > bz && pz-0.3 < bz+1);
}
```

Now the game loop with dt. Let me use requestAnimationFrame with delta.

Let me handle pointer lock and overlay.

HTML structure:
```
<div id="overlay">
  <h1>MC</h1>  (title)
  <ul>controls</ul>
  <div>Click to play</div>
</div>
<canvas id="game"></canvas>
<div id="crosshair"></div>
<div id="hotbar"></div>
```

CSS: body margin 0, overflow hidden, canvas display block, fullscreen. Overlay absolute center. Crosshair absolute center small. Hotbar absolute bottom center.

Let me write CSS.

Overlay:
```
#overlay { position:fixed; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; background:rgba(0,0,0,0.6); color:#fff; font-family:sans-serif; z-index:10; cursor:pointer; }
```

Crosshair:
```
#crosshair { position:fixed; left:50%; top:50%; width:20px; height:20px; margin:-10px 0 0 -10px; pointer-events:none; z-index:5; }
```
Draw a plus with ::before/::after or use an SVG. Let me use two divs or a simple cross with border. Let me do:
```
#crosshair { position:fixed; left:50%; top:50%; transform:translate(-50%,-50%); width:20px;height:20px; pointer-events:none; z-index:5; }
#crosshair::before, #crosshair::after { content:''; position:absolute; background:#ddd; }
#crosshair::before { left:9px; top:0; width:2px; height:20px; }
#crosshair::after { top:9px; left:0; height:2px; width:20px; }
```

Hotbar:
```
#hotbar { position:fixed; left:50%; bottom:20px; transform:translateX(-50%); display:flex; gap:4px; padding:4px; background:rgba(0,0,0,0.5); border-radius:4px; z-index:5; pointer-events:none; }
.slot { width:40px; height:40px; border:2px solid #333; display:flex; align-items:center; justify-content:center; color:#fff; font-family:sans-serif; font-size:12px; border-radius:2px; position:relative; }
.slot.sel { border-color:#fff; }
.slot .num { position:absolute; top:1px; left:3px; font-size:11px; }
```

Each slot colored by block color. Generate 7 divs.

Now let me also make sure the canvas resizes:
```
function resize() { canvas.width = innerWidth; canvas.height = innerHeight; camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); }
window.addEventListener('resize', resize);
```

Renderer: THREE.WebGLRenderer(canvas). antialias? Let me set. pixelRatio.

Now the clouds:
```
const clouds = [];
for (let i=0;i<25;i++) {
  const g = new THREE.PlaneGeometry? No, spec says "flat white transparent boxes". So BoxGeometry with scale. Let me use BoxGeometry(some, small, some). Transparent white.
  const m = new THREE.MeshBasicMaterial({color:0xffffff, transparent:true, opacity:0.9, side:DoubleSide});
  const box = new THREE.Mesh(g, m);
  box.position.set(rand-ish..., 90, rand...);
  scene.add(box);
  clouds.push(box);
}
```
But no Math.random allowed! "deterministic, no Math.random". So place clouds deterministically. Use i to spread:
```
const angle = i * 2.399; // golden ratio-ish
box.position.set(-40 + (i*13)%80, 90, -40 + (i*29)%80);
```
Whatever, deterministic spread. Each cloud: scale x large, y small, z medium to look flat.

Update clouds each frame: drift in x, wrap around player:
```
for (const cl of clouds) {
  cl.position.x += 2*dt; // drift
  if (cl.position.x < player.x - 60) cl.position.x -= 120;
  if (cl.position.x > player.x + 60) cl.position.x -= 120; // hmm
  // keep z around player
  if (cl.position.z < player.z - 60) cl.position.z += 120;
  if (cl.position.z > player.z + 60) cl.position.z -= 120;
}
```
Wait that subtract logic is off. Let me handle wrapping cleanly:
```
function wrap(v, center, half) {
  if (v < center - half) v += 2*half;
  else if (v > center + half) v -= 2*half;
  return v;
}
cl.position.x = wrap(cl.position.x, player.x, 60);
```
But adding drift then wrapping: position.x += drift; position.x = wrap(...). Good.

Water plane:
```
const water = new THREE.Mesh(new THREE.PlaneGeometry(300,300), new THREE.MeshLambertMaterial({color:0x3388ff, transparent:true, opacity:0.7}));
water.rotation.x = -Math.PI/2;
scene.add(water);
```
Each frame: water.position.set(player.x, 14.3, player.z).

Sky/fog/light:
```
renderer.setPixelRatio(window.devicePixelRatio);
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(50, 100, 30);
scene.add(dir);
```

Now let me assemble everything. Also need to generate initial chunks near spawn so player spawns on ground.

At init:
```
for (let dx=-2;dx<=2;dx++) for (let dz=-2;dz<=2;dz++) generateChunk(dx, dz);
```
Then find spawn height: at (8, ?, 8). Chunk 0,0. Local x=8, z=8. Find surface y. Let me just spawn player at y = 70 (above max terrain ~73) and let gravity bring them down. Actually "spawn above terrain". Let me compute the surface height at (8,8) and spawn there + something. Simpler: spawn at y=64 and gravity handles the rest. But if terrain there is higher... H max ~73, so y=75 is safe above. Let me spawn at y = 85 to be safe, gravity pulls down to surface. Actually if I spawn too high and there's nothing, they fall — fine. Let me spawn at y = 75.

Hmm, but player falls below -20 → teleport. Spawning at 75 then falling to surface (~30) is fine.

Let me compute exact spawn: find highest non-air at (8,8). Actually let me just do: for y from 79 down, find first non-air at (8, *, 8). Spawn at that y + 1.0 + 1.8 (above the box). Let me just spawn at surfaceY + 2.

Actually simpler and robust: spawn at y=70. Let me verify terrain at (8,8): m and h... unknown, but H likely 20-40. y=70 is above. They'll fall to surface. Good enough. But to be safe let me compute.

Let me compute spawn height properly:
```
function surfaceYAt(wx, wz) {
  const cx=Math.floor(wx/16), cz=Math.floor(wz/16);
  const lx=((wx%16)+16)%16, lz=((wz%16)+16)%16;
  const c = chunkMap.get(cx+","+cz);
  if (!c || !c.blocksGen) return 64;
  for (let y=79;y>=0;y--) if (c.blocks[(y*16+lz)*16+lx] !== 0) return y;
  return 64;
}
```
Spawn: px=8, pz=8, py = surfaceYAt(8,8) + 1.0. Eye adds 1.62.

Let me set player start:
```
px = 8; pz = 8; py = surfaceYAt(8,8) + 1.5;
```

Now let me write the full file.

Let me be careful about the meshing neighbor-data requirement and initial build. After generating initial chunks (radius 2), build their meshes. Let me call buildChunkMesh for those.

Also, I realize there might be an issue: the meshing "chunks within 4 chunks whose 4 neighbors already have data". At init with radius 2 generated, border chunks of that region have neighbors outside radius 2 without data → won't mesh. That's fine; they'll mesh as player moves. But the player is at center so central chunks mesh fine.

Let me now also double-check: getBlock reads neighbor chunk. For a chunk at border, if neighbor not generated, getBlock returns 0 (air) → we'd draw border faces that shouldn't be there. But we only build mesh if 4 neighbors have data, avoiding that. Good.

Now the updateChunks function runs every frame. Let me make sure it doesn't regenerate already-generated chunks (blocksGen flag). Good.

One concern: performance. Generating up to 4 chunks/frame, meshing 2/frame. Each chunk meshing loops 16*80*16 = 20480 blocks * up to 6 faces. That's ~120k face checks per chunk, each doing a getBlock (Map lookup + array access). 2 chunks/frame = 240k getBlock calls. Fine.

Generation: 4 chunks * 20480 * (fractal2 calls). fractal2 does 4 octaves * noise2 (hash + lerps). ~20480*4 = 81920 noise2 evals per chunk * 4 chunks = 327k. Plus caves noise3 for interior. Fine.

Let me write it all out now.

Let me also handle the "suppress context menu":
```
document.addEventListener('contextmenu', e => e.preventDefault());
```

And pointer lock change:
```
document.addEventListener('pointerlockchange', () => {
  if (document.pointerLockElement !== canvas) {
    overlay.style.display = 'flex'; // show
  } else {
    overlay.style.display = 'none';
  }
});
```

Overlay click:
```
overlay.addEventListener('click', () => {
  canvas.requestPointerLock();
});
```

Mouse move:
```
document.addEventListener('mousemove', (e) => {
  if (document.pointerLockElement !== canvas) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  pitch = Math.max(-Math.PI/2 + 0.001, Math.min(Math.PI/2 - 0.001, pitch));
});
```

Wait, sensitivity 0.002. e.movementX is pixels. yaw -= movementX * 0.002. Good.

Keys: track WASD and space.
```
const keys = {};
addEventListener('keydown', e => {
  keys[e.code] = true;
  if (e.code >= 'Digit1' && e.code <= 'Digit7') { selected = parseInt(e.code[5])-1; updateHotbar(); }
});
addEventListener('keyup', e => { keys[e.code] = false; });
```
Hmm e.code[5] for 'Digit1' → '1'. Actually 'Digit1'[5] = '1'. Let me use e.code.replace('Digit','') → '1'..'7'. selected = that - 1.

Mouse wheel:
```
addEventListener('wheel', e => {
  e.preventDefault();
  selected = (selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
  updateHotbar();
}, { passive: false });
```
Need preventDefault to avoid page scroll. But wheel should work even when not locked? Probably only when locked. Let me allow always but preventDefault. Actually if not locked, wheel shouldn't change selection necessarily. Let me gate on locked:
```
addEventListener('wheel', e => {
  if (document.pointerLockElement !== canvas) return;
  e.preventDefault();
  selected = (selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
  updateHotbar();
}, { passive:false });
```

selectedBlockId = selected + 1.

Movement dt integration:
```
const dt = Math.min(delta/1000, 0.5);
// input direction
let mx=0, mz=0;
if (keys['KeyW']) { mx += -Math.sin(yaw); mz += -Math.cos(yaw); }
if (keys['KeyS']) { mx -= -Math.sin(yaw); mz -= -Math.cos(yaw); }
if (keys['KeyD']) { mx += Math.cos(yaw); mz += -Math.sin(yaw); }
if (keys['KeyA']) { mx -= Math.cos(yaw); mz -= -Math.sin(yaw); }
// normalize
const len = Math.hypot(mx, mz);
if (len > 0.0001) { mx/=len; mz/=len; }
const speed = 5.5;
let dvx = mx*speed, dvz = mz*speed;
// gravity
vy -= 25*dt;
if (onGround && keys['Space']) vy = 8.5;
// move axes
move('x', dvx*dt);
move('z', dvz*dt);
move('y', vy*dt);
```

Wait, jumping sets onGround false via move y when it moves up. Let me handle in move('y'):
```
function move(axis, amt) {
  if (axis==='x') { if (!collides(px+amt, py, pz)) px+=amt; }
  else if (axis==='z') { if (!collides(px, py, pz+amt)) pz+=amt; }
  else if (axis==='y') {
    if (!collides(px, py+amt, pz)) { py+=amt; onGround=false; }
    else if (amt < 0) onGround = true;
  }
}
```

But there's an issue: when onGround and we jump (vy=8.5), move('y', positive) → no collision → py+=amt, onGround=false. Good. Next frames gravity reduces vy; when vy negative and we hit ground, move detects collision with amt<0 → onGround=true. Good.

But what about when vy is very negative (terminal velocity)? Let me clamp vy to maybe -50. Not necessary but fine.

Also, when moving into a wall horizontally, collides returns true, we don't move. Good. Sliding works because we move x then z separately.

Teleport if py < -20:
```
if (py < -20) { px=8; pz=8; py=surfaceYAt(8,8)+1.5; vy=0; }
```

Camera:
```
camera.position.set(px, py+1.62, pz);
camera.rotation.set(0,0,0,'YXZ'); // reset
euler.set(yaw, pitch, 0, 'YXZ');
camera.rotation.copy(euler);
```
Or directly camera.rotation.set(yaw, pitch, 0, 'YXZ'). Let me do that.

updateTarget each frame (even when not locked? only meaningful when locked). Let me call it each frame; outline updates only when locked and target exists.

Actually raycast requires camera set. Let me set camera first, then updateTarget.

Outline:
```
if (locked && target) {
  outline.position.set(bx+0.5, by+0.5, bz+0.5);
  outline.visible = true;
} else {
  outline.visible = false;
}
```
where bx,by,bz from target. Compute each frame.

Let me compute break/place coords from target each frame for the outline.

Let me now write the complete file.

Let me reconsider the fractal2 normalization: sum of amps = 1+0.5+0.25+0.125 = 1.875. Divide by 1.875. Good, result in [0,1].

noise2 uses hash which returns [0,1). lerp between. Good.

Let me also make sure hash handles negative inputs (for caves, coordinates are positive since world coords can be negative but *0.09 small; but ix = wx*0.09 could be negative). Math.floor of negative works. hash with negative ix,iy: multiplication of negatives is fine, bitwise ops on 32-bit. Let me ensure hash uses 32-bit int operations. `(h >>> 0)` converts to unsigned 32-bit. But h could be large; JS bitwise works on 32-bit two's complement. Let me cast: `h = (h|0)` first? Multiplication may overflow 32-bit but bitwise wraps anyway. Let me structure hash to use |0:

```
function hash(ix, iy) {
  let h = (ix * 1600000007 | 0) + (iy * 668265263 | 0);
  h = (h ^ (h >>> 13));
  h = (h * 2246822519 | 0);
  h = (h ^ (h >>> 16));
  return (h >>> 0) / 4294967296;
}
```
Hmm, `ix * 1600000007 | 0` — ix is float, *big, then |0 truncates to 32-bit. Then + iy term |0. XOR shift. Multiply |0. XOR. >>>0 gives unsigned. Good.

But ix, iy are floats (from wx*0.09). Bitwise ops convert to int32 (truncate). Fine, deterministic.

Let me write hash more simply and robustly:
```
function hash(ix, iy) {
  ix = ix | 0; iy = iy | 0;
  let h = ix * 2654435761 ^ iy * 39420331;
  h = (h ^ (h >>> 13)) * 2654435761;
  h = (h ^ (h >>> 16));
  return (h >>> 0) / 4294967296;
}
```
ix|0 truncates. Good. Large primes 2654435761 (knuth) and 39420331.

For hash3 similar with 3 args.

Let me finalize noise functions.

Actually, careful: `ix * 2654435761` — ix is int32, times large → becomes float (since 2654435761 > 2^31, product is float). Then `^ iy*39420331` — but operator precedence: * before ^. So `ix*2654435761 ^ iy*39420331`. Both products are floats; ^ converts to int32. OK. Then h is int32. `(h ^ (h>>>13)) * 2654435761` → float again, then... I need |0 to keep int. Let me add |0:
```
function hash(ix, iy) {
  ix |= 0; iy |= 0;
  let h = ((ix * 2654435761) ^ (iy * 39420331)) | 0;
  h = ((h ^ (h >>> 13)) * 2654435761) | 0;
  h = (h ^ (h >>> 16)) | 0;
  return (h >>> 0) / 4294967296;
}
```
Good.

noise3:
```
function hash3(ix, iy, iz) {
  ix |= 0; iy |= 0; iz |= 0;
  let h = ((ix * 2654435761) ^ (iy * 39420331) ^ (iz * 1322318389)) | 0;
  h = ((h ^ (h >>> 13)) * 2654435761) | 0;
  h = (h ^ (h >>> 16)) | 0;
  return (h >>> 0) / 4294967296;
}
```

noise2:
```
function noise2(ix, iy) {
  const xi = Math.floor(ix), yi = Math.floor(iy);
  const xf = ix - xi, yf = iy - yi;
  const u = xf*xf*(3-2*xf), v = yf*yf*(3-2*yf);
  const g00 = hash(xi, yi), g10 = hash(xi+1, yi);
  const g01 = hash(xi, yi+1), g11 = hash(xi+1, yi+1);
  const nx0 = g00*(1-u)+g10*u;  // lerp
  const nx1 = g01*(1-u)+g11*u;
  return nx0*(1-v)+nx1*v;
}
```

fractal2:
```
function fractal2(ix, iy) {
  let amp=1,freq=1,sum=0,norm=0;
  for(let o=0;o<4;o++){ sum += amp*noise2(ix*freq, iy*freq); norm += amp; amp*=0.5; freq*=2; }
  return sum/norm;
}
```

noise3:
```
function noise3(ix, iy, iz) {
  const xi=Math.floor(ix), yi=Math.floor(iy), zi=Math.floor(iz);
  const xf=ix-xi, yf=iy-yi, zf=iz-zi;
  const u=xf*xf*(3-2*xf), v=yf*yf*(3-2*yf), w=zf*zf*(3-2*zf);
  const c000=hash3(xi,yi,zi), c100=hash3(xi+1,yi,zi), c010=hash3(xi,yi+1,zi), c110=hash3(xi+1,yi+1,zi);
  const c001=hash3(xi,yi,zi+1), c101=hash3(xi+1,yi,zi+1), c011=hash3(xi,yi+1,zi+1), c111=hash3(xi+1,yi+1,zi+1);
  const d00=c000*(1-u)+c100*u, d10=c010*(1-u)+c110*u;
  const d01=c001*(1-u)+c101*u, d11=c011*(1-u)+c111*u;
  const e0=d00*(1-v)+d10*v, e1=d01*(1-v)+d11*v;
  return e0*(1-w)+e1*w;
}
```

Good.

Now let me write the whole thing. I'll be thorough.

Let me reconsider the "spawn above terrain at x=8, z=8" and initial gen. I'll generate radius 2 at init and build meshes for all of them (they're central, neighbors within radius 2 have data except the outer ring). For outer ring (dx=±2 or dz=±2), neighbors at dx=±3 lack data → won't pass neighbor check. But I'll just build all generated meshes directly at init regardless (skip neighbor check for init). Let me build meshes for the radius-2 chunks directly.

Actually, let me just call buildChunkMesh for each generated chunk at init. That builds them (border faces might be missing-correct if neighbor has data, but neighbors at ±3 don't exist → getBlock returns 0 → we draw the border face, which is fine because beyond radius 2 there's no terrain yet; it'll be corrected when those chunks generate and mesh). Acceptable.

Let me now also ensure the meshing neighbor-data requirement and initial build. After generating initial chunks (radius 2), build their meshes.

Let me write final code.

One more consideration: `THREE.Color.multiplyScalar` mutates. Good.

Also vertexColors in r128 MeshLambertMaterial: yes supported.

Let me also add `renderer.toneMapping = THREE.NoToneMapping;` to avoid auto exposure darkening (PEQ). In r128, default toneMapping is ACESFilmic which auto-exposes and can darken. Let me set NoToneMapping and linear encoding? Let me set:
```
renderer.toneMapping = THREE.NoToneMapping;
```
This ensures colors match our vertex colors directly. Good.

Also set outputEncoding? Not necessary.

Let me write the file now.

Let me reconsider the overlay controls list. Provide:
- WASD move, Space jump, Shift? (spec doesn't mention sprint/shift, but let me not add). Actually spec lists WASD, Space, mouse look, left/right click, 1-7, wheel. Let me list those.

Controls list:
- Move: W A S D
- Jump: Space
- Look: Mouse
- Break block: Left click
- Place block: Right click
- Select block: 1-7 or Mouse Wheel

Title: "Voxel Game" or "MC". Let me use "VOXEL CRAFT" or just "MINECRAFT-STYLE". Let me use "VOXEL SANDBOX".

Now let me also double check the raycast direction via camera.getWorldDirection. camera is updated each frame. Good.

Let me also ensure we only break/place when locked and target.valid.

Let me write it all.

Also, need to handle the case where raycast hits nothing (target null) — outline hidden.

Let me also make sure that when we break a block at y=0 we skip (unbreakable). And place only if cell air and not overlapping player and chunk has data.

Let me also reconsider: after break/place, we call setBlock then editChunk. editChunk rebuilds the affected chunk and border neighbors. Good.

Now, potential infinite: the chunk update loop deletes entries beyond radius 7. But if a chunk that the player's current mesh depends on is deleted while player is near? No, deletion is beyond 7, meshing within 4, safe.

Also, when we delete a chunk, we should remove it from chunkMeshes array. Handled in dispose.

Let me also make sure that when building a mesh that already exists (rebuild), we dispose old and update chunkMeshes. Handled.

Let me write the code.

Actually, let me reconsider whether to include Shift for sprint — spec doesn't require. Skip.

Let me also reconsider jump: "jump with Space (velocity 8.5)". Good.

Let me also handle onGround detection when moving: if vy is negative and we're standing on a block, move('y', negative) collides → onGround=true. But if we're on ground and vy computed as small negative (just landed), good. If vy positive (jumping), no collision → moves up. Good.

Edge: when standing on ground, vy after gravity is negative; move('y') with negative amt → collides → onGround true, py unchanged. Good.

Now let me also make sure that when onGround and we jump (vy=8.5), move('y', positive) → no collision → py+=amt, onGround=false. Good.

Let me write the file now. I'll produce it fully.

Let me reconsider the water plane orientation: PlaneGeometry is in XY plane; rotating x=-π/2 makes it horizontal (facing -Z? after rotation it lies in XZ plane). position y=14.3. Good. Material semi-transparent blue.

Clouds: use BoxGeometry. Let me scale them flat: geometry scaled via mesh.scale (x=large, y=small, z=medium). Or create with BoxGeometry(l, small, w). Let me use BoxGeometry and set scale.

Let me write everything.

Also, I should double check: THREE.Color in r128 constructor accepts hex. new THREE.Color(0x4caf50). Good.

Let me also ensure blockMaterial vertexColors true works with color attribute named 'color'. Yes.

Let me write the final HTML.

Actually, I want to double-check the collision bounding for floor detection doesn't falsely trigger. Player half-width 0.3, so AABB x from px-0.3 to px+0.3 (width 0.6). For block test, minX=floor(px-0.3), maxX=floor(px+0.3+epsilon). Using Math.floor(posX+0.6) where posX is the proposed center. Wait my collides uses width 0.6 (px+0.6). But AABB is px-0.3 to px+0.3 = width 0.6. floor(px) to floor(px+0.6)? If px=8.0, px+0.6=8.6, floor=8. But actual max is px+0.3=8.3, floor=8. And min px-0.3=7.7 floor=7. So blocks 7 and 8 tested. Using floor(px)=8 and floor(px+0.6)=8 → only block 8 tested, missing block 7! Bug.

I need minX=floor(px-0.3), maxX=floor(px+0.3). Let me fix collides to use explicit half extents:
```
function collides(cx, cy, cz) {
  const minX=Math.floor(cx-0.3), maxX=Math.floor(cx+0.3);
  const minY=Math.floor(cy), maxY=Math.floor(cy+1.8);
  const minZ=Math.floor(cz-0.3), maxZ=Math.floor(cz+0.3);
  ...
}
```
Here cx is the proposed center x. So AABB = [cx-0.3, cx+0.3]. minX=floor(cx-0.3), maxX=floor(cx+0.3). For cx=8.0: minX=floor(7.7)=7, maxX=floor(8.3)=8. Blocks 7,8. Good. For cx=8.3 (moved): minX=floor(8.0)=8, maxX=floor(8.6)=8. Block 8. Good.

Wait but when we call collides(px+amt, py, pz), the new center is px+amt. AABB [px+amt-0.3, px+amt+0.3]. Good.

Let me use this corrected collides.

Similarly aabbOverlapsBlock uses px-0.3..px+0.3 etc. Good.

Let me finalize.

Let me reconsider maxY: floor(py+1.8). For py=30, height 1.8 → top at 31.8, floor=31. minY=floor(30)=30. Blocks 30,31. Good (2 blocks tall).

Now writing.

Let me also make sure the initial spawn finds terrain. I generate radius 2 chunks (including chunk containing 8,8 = chunk 0,0). surfaceYAt(8,8) reads chunk 0,0 blocks. Good.

Let me write the complete file now.

I'll include a comment header maybe. Let me keep it clean.

Let me write.

Actually, I realize for the outline wireframe, depthTest:false might cause it to render behind blocks sometimes. Better keep depthTest true and depthWrite false so it renders on top of existing depth but doesn't write. Let me use:
```
new THREE.LineBasicMaterial({ color: 0x000000, depthTest:true, depthWrite:false })
```
This way it draws on top of geometry without writing depth, so it's visible even flush. Good.

Let me finalize the code.

Let me also handle resize for renderer size and pixel ratio.

Writing now.

Let me make sure I reference `scene`, `camera`, `renderer`, `blockMaterial`, `chunkMeshes`, `outline`, `water`, `clouds`, `player` variables consistently as globals.

Let me write the JS in a way that all functions are hoisted (function declarations) so order is fine.

Final code below.

Let me reconsider one thing about generateChunk and the `blocksGen` flag combined with the update loop deleting chunks. When a chunk is deleted (beyond radius 7), its blocksGen flag is gone (entry deleted). If player comes back, it regenerates. Good.

Also, when we call getOrCreateChunk in setBlock for a chunk that exists but not generated (has empty blocks array, blocksGen false), we set into it. But that could place a block in an ungenerated chunk. For place, we guard by checking blocksGen. For break, target is in generated chunk. Good.

Let me also make editChunk robust: rebuildChunk checks blocksGen.

Alright, writing final.

Let me also double check: the mesh for a chunk is added to scene at origin with geometry in world coords. When player moves, chunks stay put (world coords). Good. Camera moves. Raycast against static meshes. Good.

Let me write it all out now, carefully.

I'll now produce the single code block.

Let me reconsider the fractal2 normalization once more and that m*m gives the right range — already covered.

Let me write the final file.

For robustness, wrap main init in DOMContentLoaded? Since script at end of body, elements exist. I'll place script at end of body.

Let me write.

Actually, I want to double-check THREE.BufferGeometry setAttribute signature in r128: setAttribute(name, buffer) where buffer is a BufferAttribute. new THREE.BufferAttribute(Float32Array, itemSize). Good.

Let me write final code.

I think I've covered everything. Let me produce the file.

Let me reconsider the water plane orientation — already covered.

Clouds: use BoxGeometry. Already decided.

Let me write everything now in one go.
</think>

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mc</title>
<style>
	html,body{margin:0;padding:0;overflow:hidden;background:#87ceeb;}
	body{font-family:sans-serif;}
	canvas{display:block;position:fixed;top:0;left:0;}
	#overlay{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
		background:rgba(0,0,0,0.55);color:#fff;text-align:center;z-index:20;cursor:pointer;}
	#overlay h1{font-size:48px;margin:0 0 10px;letter-spacing:2px;text-shadow:2px 2px 0 #000;}
	#overlay ul{text-align:left;line-height:1.8;font-size:15px;}
	#overlay div.sub{margin-top:14px;font-size:18px;}
	#crosshair{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:20px;height:20px;
		pointer-events:none;z-index:5;}
	#crosshair::before,#crosshair::after{content:'';position:absolute;background:#eee;box-shadow:0 0 2px #000;}
	#crosshair::before{left:9px;top:0;width:2px;height:20px;}
	#crosshair::after{top:9px;left:0;height:2px;width:20px;}
	#hotbar{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);display:flex;gap:4px;
		padding:4px;background:rgba(0,0,0,0.5);border-radius:4px;z-index:5;pointer-events:none;}
	.slot{width:42px;height:42px;border:2px solid #333;border-radius:3px;display:flex;align-items:center;
		justify-content:center;color:#fff;font-size:11px;font-weight:bold;position:relative;text-shadow:1px 1px 0 #000;}
	.slot.sel{border-color:#fff;}
	.slot .n{position:absolute;top:1px;left:3px;font-size:10px;opacity:.85;}
</style>
</head>
<body>
<div id="overlay">
	<h1>VOXEL CRAFT</h1>
	<ul>
		<li><b>W A S D</b> — move</li>
		<li><b>Space</b> — jump</li>
		<li><b>Mouse</b> — look around</li>
		<li><b>Left click</b> — break block</li>
		<li><b>Right click</b> — place block</li>
		<li><b>1–7 / Wheel</b> — select block</li>
	</ul>
	<div class="sub">Click to play</div>
</div>
<canvas id="game"></canvas>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

/* ---------- canvas / renderer / camera ---------- */
const canvas = document.getElementById("game");
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.NoToneMapping;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 400);

/* ---------- lights ---------- */
scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(60, 120, 40);
scene.add(sun);

/* ---------- block colors & material ---------- */
const BLOCK_COLORS = [0,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
const blockMaterial = new THREE.MeshLambertMaterial({vertexColors:true});

/* ---------- faces: dir, normal, lighting factor, 4 corners (CCW from outside) ---------- */
const FACES = [
	{dir:[ 1,0,0], normal:[ 1,0,0], light:0.80, corners:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]]},
	{dir:[-1,0,0], normal:[-1,0,0], light:0.80, corners:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]]},
	{dir:[ 0,1,0], normal:[ 0,1,0], light:1.00, corners:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]]},
	{dir:[ 0,-1,0],normal:[ 0,-1,0],light:0.55, corners:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
	{dir:[ 0,0, 1],normal:[ 0,0, 1],light:0.80, corners:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]]},
	{dir:[ 0,0,-1],normal:[ 0,0,-1],light:0.80, corners:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]]},
];

/* ---------- chunk storage ---------- */
const chunkMap = new Map();           // key "cx,cz" -> {blocks:Uint8Array, mesh, blocksGen}
const chunkMeshes = [];               // flat list for raycasting

function getChunk(cx,cz){ return chunkMap.get(cx+","+cz); }
function getOrCreateChunk(cx,cz){
	const key = cx+","+cz;
	let c = chunkMap.get(key);
	if(!c){ c={blocks:new Uint8Array(16*80*16),mesh:null,blocksGen:false}; chunkMap.set(key,c); }
	return c;
}

/* ---------- global block read (negative coords OK) ---------- */
function getBlock(wx,wy,wz){
	const cx = Math.floor(wx/16), cz = Math.floor(wz/16);
	const lx = wx - cx*16, lz = wz - cz*16;
	const c = chunkMap.get(cx+","+cz);
	if(!c || wy<0 || wy>=80) return 0;
	return c.blocks[(wy*16+lz)*16+lx];
}

function setBlock(wx,wy,wz,id){
	if(wy<0||wy>=80) return;
	const cx = Math.floor(wx/16), cz = Math.floor(wz/16);
	const lx = ((wx%16)+16)%16, lz = ((wz%16)+16)%16;
	const c = getOrCreateChunk(cx,cz);
	if(!c.blocksGen) return;
	c.blocks[(wy*16+lz)*16+lx] = id;
}

/* ---------- value noise ---------- */
function hash(ix,iy){
	ix|=0; iy|=0;
	let h = ((ix*2654435761)^(iy*39420331))|0;
	h = ((h^(h>>>13))*2654435761)|0;
	h = (h^(h>>>16))|0;
	return (h>>>0)/4294967296;
}
function hash3(ix,iy,iz){
	ix|=0; iy|=0; iz|=0;
	let h = ((ix*2654435761)^(iy*39420331)^(iz*1322318389))|0;
	h = ((h^(h>>>13))*2654435761)|0;
	h = (h^(h>>>16))|0;
	return (h>>>0)/4294967296;
}
function noise2(ix,iy){
	const xi=Math.floor(ix), yi=Math.floor(iy);
	const xf=ix-xi, yf=iy-yi;
	const u=xf*xf*(3-2*xf), v=yf*yf*(3-2*yf);
	const a=hash(xi,yi), b=hash(xi+1,yi), c=hash(xi,yi+1), d=hash(xi+1,yi+1);
	const nx0=a+(b-a)*u, nx1=c+(d-c)*u;
	return nx0+(nx1-nx0)*v;
}
function noise3(ix,iy,iz){
	const xi=Math.floor(ix), yi=Math.floor(iy), zi=Math.floor(iz);
	const xf=ix-xi, yf=iy-yi, zf=iz-zi;
	const u=xf*xf*(3-2*xf), v=yf*yf*(3-2*yf), w=zf*zf*(3-2*zf);
	const c000=hash3(xi,yi,zi),c100=hash3(xi+1,yi,zi),c010=hash3(xi,yi+1,zi),c110=hash3(xi+1,yi+1,zi);
	const c001=hash3(xi,yi,zi+1),c101=hash3(xi+1,yi,zi+1),c011=hash3(xi,yi+1,zi+1),c111=hash3(xi+1,yi+1,zi+1);
	const d00=c000+(c100-c000)*u, d10=c010+(c110-c010)*u;
	const d01=c001+(c101-c001)*u, d11=c011+(c111-c011)*u;
	const e0=d00+(d10-d00)*v, e1=d01+(d11-d01)*v;
	return e0+(e1-e0)*w;
}
function fractal2(ix,iy){
	let amp=1,freq=1,sum=0,norm=0;
	for(let o=0;o<4;o++){ sum+=amp*noise2(ix*freq,iy*freq); norm+=amp; amp*=0.5; freq*=2; }
	return sum/norm;
}

/* ---------- terrain generation ---------- */
function generateChunk(cx,cz){
	const c = getOrCreateChunk(cx,cz);
	if(c.blocksGen) return;
	c.blocksGen = true;
	const b = c.blocks;
	for(let x=0;x<16;x++){
		for(let z=0;z<16;z++){
			const wx=cx*16+x, wz=cz*16+z;
			const m = fractal2(wx*0.004, wz*0.004);
			const h = fractal2(wx*0.02,  wz*0.02);
			const H = Math.floor(5 + m*m*58 + h*10);
			let dirtMat = 2;
			if(H<=16) dirtMat=4; else if(H>=37) dirtMat=3;
			let surf;
			if(H>=46) surf=7; else if(H>=37) surf=3; else if(H<=16) surf=4; else surf=1;
			for(let y=0;y<80;y++){
				let id;
				if(y===0) id=3;
				else if(y<H-4) id=3;
				else if(y<H-1) id=dirtMat;
				else id=surf;
				if(y>=3 && y<H-2){
					if(noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) id=0;
				}
				b[(y*16+z)*16+x]=id;
			}
			/* trees */
			if(surf===1 && hash(wx,wz)<0.02){
				const top=H-1;
				for(let ty=top+1;ty<=top+4;ty++) if(ty<80) b[(ty*16+z)*16+x]=5;
				const lt=top+4;
				for(let dy=0;dy<2;dy++){
					const ly=lt+dy; if(ly>=80) continue;
					for(let dx=-2;dx<=2;dx++) for(let dz=-2;dz<=2;dz++)
						if(b[(ly*16+(z+dz+16)%16)*16+((x+dx+16)%16)]===0)
							b[(ly*16+(z+dz+16)%16)*16+((x+dx+16)%16)]=6;
				}
				const ly3=lt+2; if(ly3<80){
					for(let dx=-1;dx<=1;dx++) for(let dz=-1;dz<=1;dz++)
						if(b[(ly3*16+(z+dz+16)%16)*16+((x+dx+16)%16)]===0)
							b[(ly3*16+(z+dz+16)%16)*16+((x+dx+16)%16)]=6;
				}
				const ly1=lt+3; if(ly1<80){
					const tx=((x+0+16)%16), tz=((z+0+16)%16);
					if(b[(ly1*16+tz)*16+tx]===0) b[(ly1*16+tz)*16+tx]=6;
				}
			}
		}
	}
}

/* ---------- meshing ---------- */
function buildChunkMesh(cx,cz){
	const c = getChunk(cx,cz);
	if(!c || !c.blocksGen) return;
	const pos=[], nor=[], col=[], idx=[];
	for(let x=0;x<16;x++){
		for(let y=0;y<80;y++){
			for(let z=0;z<16;z++){
				const id = c.blocks[(y*16+z)*16+x];
				if(!id) continue;
				const wx=cx*16+x, wy=y, wz=cz*16+z;
				for(let f=0;f<6;f++){
					const face=FACES[f];
					const nx=wx+face.dir[0], ny=wy+face.dir[1], nz=wz+face.dir[2];
					if(getBlock(nx,ny,nz)===0){
						const color=new THREE.Color(BLOCK_COLORS[id]);
						color.multiplyScalar(face.light);
						const base=pos.length/3;
						for(let k=0;k<4;k++){
							const cc=face.corners[k];
							pos.push(wx+cc[0], wy+cc[1], wz+cc[2]);
							nor.push(face.normal[0], face.normal[1], face.normal[2]);
							col.push(color.r, color.g, color.b);
						}
						idx.push(base, base+1, base+2, base, base+2, base+3);
					}
				}
			}
		}
	}
	const geo=new THREE.BufferGeometry();
	geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos),3));
	geo.setAttribute('normal',   new THREE.BufferAttribute(new Float32Array(nor),3));
	geo.setAttribute('color',    new THREE.BufferAttribute(new Float32Array(col),3));
	geo.setIndex(idx);
	if(c.mesh){
		const i=chunkMeshes.indexOf(c.mesh); if(i>=0) chunkMeshes.splice(i,1);
		scene.remove(c.mesh); c.mesh.geometry.dispose();
	}
	const mesh=new THREE.Mesh(geo, blockMaterial);
	mesh.position.set(0,0,0);
	scene.add(mesh);
	c.mesh=mesh;
	chunkMeshes.push(mesh);
}

/* ---------- chunk streaming ---------- */
function neighborHasData(cx,cz){ const c=getChunk(cx,cz); return c && c.blocksGen; }

function updateChunks(){
	const pcx=Math.floor(player.px/16), pcz=Math.floor(player.pz/16);
	const gens=[], meshes=[];
	for(let dx=-7;dx<=7;dx++){
		for(let dz=-7;dz<=7;dz++){
			const d2=dx*dx+dz*dz;
			if(d2>49) continue;
			const cx=pcx+dx, cz=pcz+dz;
			const c=getChunk(cx,cz);
			if(d2<=25 && (!c || !c.blocksGen)){ gens.push({cx,cz,d2}); }
			if(c && c.blocksGen && d2<=16){
				if(neighborHasData(cx-1,cz)&&neighborHasData(cx+1,cz)&&neighborHasData(cx,cz-1)&&neighborHasData(cx,cz+1)){
					meshes.push({cx,cz,d2});
				}
			}
		}
	}
	gens.sort((a,b)=>a.d2-b.d2);
	for(let i=0;i<Math.min(4,gens.length);i++) generateChunk(gens[i].cx,gens[i].cz);
	meshes.sort((a,b)=>a.d2-b.d2);
	for(let i=0;i<Math.min(2,meshes.length);i++) buildChunkMesh(meshes[i].cx,meshes[i].cz);
	/* cleanup far chunks */
	for(const [key,c] of chunkMap){
		const parts=key.split(','), cs=+parts[0], czs=+parts[1];
		if(Math.abs(cs-pcx)>7 || Math.abs(czs-pcz)>7){
			if(c.mesh){ scene.remove(c.mesh); c.mesh.geometry.dispose(); }
			const i=chunkMeshes.indexOf(c.mesh); if(i>=0) chunkMeshes.splice(i,1);
			chunkMap.delete(key);
		}
	}
}

/* ---------- player ---------- */
const player = {px:8, py:64, pz:8, vy:0, yaw:0, pitch:0, onGround:false};
const PW=0.3, PH=1.8, EYE=1.62;

function collides(cx,cy,cz){
	const minX=Math.floor(cx-PW), maxX=Math.floor(cx+PW);
	const minY=Math.floor(cy),   maxY=Math.floor(cy+PH);
	const minZ=Math.floor(cz-PW), maxZ=Math.floor(cz+PW);
	for(let x=minX;x<=maxX;x++) for(let y=minY;y<=maxY;y++) for(let z=minZ;z<=maxZ;z++){
		if(getBlock(x,y,z)!==0) return true;
	}
	return false;
}
function moveAxis(amt,axis){
	if(axis==='x'){ if(!collides(player.px+amt,player.py,player.pz)) player.px+=amt; }
	else if(axis==='z'){ if(!collides(player.px,player.py,player.pz+amt)) player.pz+=amt; }
	else if(axis==='y'){
		if(!collides(player.px,player.py+amt,player.pz)){ player.py+=amt; player.onGround=false; }
		else if(amt<0) player.onGround=true;
	}
}

function surfaceYAt(wx,wz){
	const cx=Math.floor(wx/16), cz=Math.floor(wz/16);
	const lx=((wx%16)+16)%16, lz=((wz%16)+16)%16;
	const c=getChunk(cx,cz);
	if(!c||!c.blocksGen) return 60;
	for(let y=79;y>=0;y--) if(c.blocks[(y*16+lz)*16+lx]!==0) return y;
	return 60;
}

/* ---------- break / place ---------- */
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
let target=null;
let bx=0,by=0,bz=0; // break target coords

function updateTarget(){
	const dir=new THREE.Vector3();
	camera.getWorldDirection(dir);
	raycaster.set(camera.position, dir);
	const hits=raycaster.intersectObjects(chunkMeshes,false);
	if(hits.length && hits[0].distance<=6){
		target=hits[0];
		const p=target.hit.point, n=target.face.normal;
		bx=Math.floor(p.x - n.x*0.5);
		by=Math.floor(p.y - n.y*0.5);
		bz=Math.floor(p.z - n.z*0.5);
	}else{ target=null; }
}

function editChunk(wx,wz){
	const cx=Math.floor(wx/16), cz=Math.floor(wz/16);
	buildChunkMesh(cx,cz);
	const lx=((wx%16)+16)%16, lz=((wz%16)+16)%16;
	if(lx===0) buildChunkMesh(cx-1,cz);
	else if(lx===15) buildChunkMesh(cx+1,cz);
	if(lz===0) buildChunkMesh(cx,cz-1);
	else if(lz===15) buildChunkMesh(cx,cz+1);
}
function aabbBlock(bx,by,bz){
	return (player.px+PW>bx && player.px-PW<bx+1) &&
		   (player.py+PH>by && player.py<by+1) &&
		   (player.pz+PW>bz && player.pz-PW<bz+1);
}

/* ---------- outline ---------- */
const outlineGeo = new THREE.WireframeGeometry(new THREE.BoxGeometry(1.01,1.01,1.01));
const outline = new THREE.LineSegments(outlineGeo,
	new THREE.LineBasicMaterial({color:0x000000, depthTest:true, depthWrite:false}));
outline.visible=false;
scene.add(outline);

/* ---------- clouds ---------- */
const clouds=[];
for(let i=0;i<25;i++){
	const g=new THREE.BoxGeometry(24, 4, 16);
	const m=new THREE.MeshBasicMaterial({color:0xffffff, transparent:true, opacity:0.85, side:DoubleSide});
	const box=new THREE.Mesh(g,m);
	box.position.set(-40 + (i*13)%90, 90, -40 + (i*29)%90);
	clouds.push(box);
	scene.add(box);
}

/* ---------- water ---------- */
const water=new THREE.Mesh(new THREE.PlaneGeometry(300,300),
	new THREE.MeshLambertMaterial({color:0x3388ff, transparent:true, opacity:0.7}));
water.rotation.x=-Math.PI/2;
scene.add(water);

/* ---------- hotbar ---------- */
const HOTBAR=[1,2,3,4,5,6,7];
let selected=0;
const hotbarEl=document.getElementById("hotbar");
function buildHotbar(){
	hotbarEl.innerHTML="";
	for(let i=0;i<7;i++){
		const s=document.createElement("div");
		s.className="slot"+(i===selected?" sel":"");
		s.style.background="#"+BLOCK_COLORS[HOTBAR[i]].toString(16).padStart(2,"0");
		const n=document.createElement("span"); n.className="n"; n.textContent=(i+1); s.appendChild(n);
		hotbarEl.appendChild(s);
	}
}
function updateHotbar(){
	const slots=hotbarEl.children;
	for(let i=0;i<7;i++) slots[i].classList.toggle("sel", i===selected);
}
const selectedBlockId=()=>HOTBAR[selected];

/* ---------- input ---------- */
const keys={};
const overlay=document.getElementById("overlay");

overlay.addEventListener("click",()=>{ canvas.requestPointerLock(); });

document.addEventListener("pointerlockchange",()=>{
	if(document.pointerLockElement!==canvas){ overlay.style.display="flex"; }
	else{ overlay.style.display="none"; }
});

document.addEventListener("mousemove",(e)=>{
	if(document.pointerLockElement!==canvas) return;
	player.yaw  -= e.movementX*0.002;
	player.pitch-= e.movementY*0.002;
	const lim=Math.PI/2-0.001;
	player.pitch=Math.max(-lim, Math.min(lim, player.pitch));
});

document.addEventListener("mousedown",(e)=>{
	if(document.pointerLockElement!==canvas) return;
	if(e.button===0){ // break
		if(target && by!==0){ setBlock(bx,by,bz,0); editChunk(bx,bz); }
	}else if(e.button===2){ // place
		const pcx=Math.floor((target.hit.point.x+target.face.normal.x*0.5));
		const pcy=Math.floor((target.hit.point.y+target.face.normal.y*0.5));
		const pcz=Math.floor((target.hit.point.z+target.face.normal.z*0.5));
		if(getBlock(pcx,pcy,pcz)===0 && !aabbBlock(pcx,pcy,pcz)){
			setBlock(pcx,pcy,pcz, selectedBlockId());
			editChunk(pcx,pcz);
		}
	}
});
document.addEventListener("contextmenu",e=>e.preventDefault());

addEventListener("keydown",(e)=>{
	keys[e.code]=true;
	if(e.code>="Digit1"&&e.code<="Digit7"){
		selected=parseInt(e.code.slice(5),10)-1;
		updateHotbar();
	}
});
addEventListener("keyup",(e)=>{ keys[e.code]=false; });

addEventListener("wheel",(e)=>{
	if(document.pointerLockElement!==canvas) return;
	e.preventDefault();
	selected=(selected + (e.deltaY>0?1:-1) + 7)%7;
	updateHotbar();
},{passive:false});

/* ---------- resize ---------- */
function resize(){
	renderer.setSize(window.innerWidth, window.innerHeight);
	camera.aspect=window.innerWidth/window.innerHeight;
	camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);

/* ---------- init world ---------- */
for(let dx=-2;dx<=2;dx++) for(let dz=-2;dz<=2;dz++) generateChunk(dx,dz);
for(let dx=-2;dx<=2;dx++) for(let dz=-2;dz<=2;dz++) buildChunkMesh(dx,dz);

player.px=8; player.pz=8;
player.py=surfaceYAt(8,8)+1.0;
player.vy=0; player.onGround=false;

/* ---------- game loop ---------- */
let last=performance.now();
function animate(){
	requestAnimationFrame(animate);
	const now=performance.now();
	const dt=Math.min((now-last)/1000, 0.5);
	last=now;

	updateChunks();

	/* movement */
	let ix=0, iz=0;
	if(keys["KeyW"]){ ix+=-Math.sin(player.yaw); iz+=-Math.cos(player.yaw); }
	if(keys["KeyS"]){ ix-= -Math.sin(player.yaw); iz-= -Math.cos(player.yaw); }
	if(keys["KeyD"]){ ix+= Math.cos(player.yaw); iz+= -Math.sin(player.yaw); }
	if(keys["KeyA"]){ ix-= Math.cos(player.yaw); iz-= -Math.sin(player.yaw); }
	const len=Math.hypot(ix,iz);
	if(len>0.0001){ ix/=len; iz/=len; }
	const speed=5.5;
	player.vy-=25*dt;
	if(player.onGround && keys["Space"]) player.vy=8.5;

	moveAxis(ix*speed*dt,"x");
	moveAxis(iz*speed*dt,"z");
	moveAxis(player.vy*dt,"y");

	if(player.py<-20){ player.px=8; player.pz=8; player.py=surfaceYAt(8,8)+1.0; player.vy=0; }

	/* camera */
	camera.position.set(player.px, player.py+EYE, player.pz);
	camera.rotation.set(0,0,0,"YXZ");
	camera.rotation.y=player.yaw;
	camera.rotation.x=player.pitch;

	/* target / outline */
	updateTarget();
	if(document.pointerLockElement===canvas && target){
		outline.position.set(bx+0.5, by+0.5, bz+0.5);
		outline.visible=true;
	}else{ outline.visible=false; }

	/* clouds drift & follow */
	for(const cl of clouds){
		cl.position.x += 3*dt;
		if(cl.position.x < player.px-60) cl.position.x += 120;
		if(cl.position.x > player.px+60) cl.position.x -= 120;
		if(cl.position.z < player.pz-60) cl.position.z += 120;
		if(cl.position.z > player.pz+60) cl.position.z -= 120;
	}
	water.position.set(player.px, 14.3, player.pz);

	renderer.render(scene, camera);
}
buildHotbar();
animate();

})();
</script>
</body>
</html>
```