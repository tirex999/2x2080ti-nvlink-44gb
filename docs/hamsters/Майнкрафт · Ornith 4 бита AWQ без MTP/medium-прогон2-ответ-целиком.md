Let me carefully build this Minecraft-style voxel game in a single HTML file. I'll follow the spec precisely.

Let me think through the architecture:

1. **HTML structure**: Fullscreen canvas, start overlay, crosshair, hotbar.

2. **CSS**: Reset margins, fullscreen canvas, overlay styling, crosshair, hotbar.

3. **JavaScript** using THREE global object (r128).

Let me plan out the code sections:

### Block definitions
```js
const BLOCKS = [
  {id:0, name:'air', color:0x000000},
  {id:1, name:'grass', color:0x4caf50},
  {id:2, name:'dirt', color:0x795548},
  {id:3, name:'stone', color:0x9e9e9e},
  {id:4, name:'sand', color:0xe7d9a8},
  {id:5, name:'wood', color:0x8d6e63},
  {id:6, name:'leaves', color:0x2e7d32},
  {id:7, name:'snow', color:0xffffff},
];
```

### Value noise

Integer hash giving 0-1 with prime multipliers and xor-shifts.

```js
function hash2(ix, iy) {
  // integer hash -> 0..1
  let h = ix * 16777619 ^ iy * 2246823;  // prime multipliers
  h = (h ^ (h >>> 13)) * 15430893;  // xor shift
  h = h ^ (h >>> 16);
  ... 
}
```

Let me design a proper hash. The spec says "an integer-coordinate hash giving 0–1 (mix with large prime multipliers and xor-shifts)".

Let me do:
```js
function hash(ix, iy) {
  let h = ix * 73856093 ^ iy * 19349663; // prime multipliers
  h = (h ^ (h >>> 15)) * 0x5bd1e9fb; // xor shift + multiply
  h = h ^ (h >>> 13);
  h = (h * 0x5bd1e999) | 0;
  return ((h >>> 0) % 100000) / 100000; // 0..1
}
```

Hmm, need to be careful with bitwise operations since they limit to 32-bit. Let me use a cleaner approach. Actually let me use a fractional approach.

Let me define:
```js
function hash(ix, iy) {
  let v = ix * 374761393 + iy * 668265265;
  v = (v ^ (v >>> 13)) * 1274126177;
  v = (v ^ (v >>> 16)) >>> 0;
  return v / 4294967296;
}
```

This gives a deterministic 0-1 float. Good.

For 3D:
```js
function hash3(ix, iy, iz) {
  let v = ix * 374761393 + iy * 668265265 + iz * 2654435769;
  v = (v ^ (v >>> 13)) * 1274126177;
  v = (v ^ (v >>> 16)) >>> 0;
  return v / 4294967296;
}
```

Bilinear smoothing:
```js
function lerp(a, b, t) {
  return a + (b - a) * (t * t * (3 - 2 * t)); // smoothstep
}
```

Actually smoothstep is `t*t*(3-2t)`. Let me apply smoothing to the fractional part.

2D fractal noise:
```js
function noise2(x, y) {
  let X = Math.floor(x), Y = Math.floor(y);
  let xf = x - X, yf = y - Y;
  let v0 = hash(X, Y), v1 = hash(X+1, Y);
  let v2 = hash(X, Y+1), v3 = hash(X+1, Y+1);
  let u = xf*xf*(3-2*xf), v = yf*yf*(3-2*yf);
  let a = lerp(v0, v1, u);
  let b = lerp(v2, v3, u);
  return lerp(a, b, v);
}
```

Fractal (octaves):
```js
function fractal2(x, y, octaves) {
  let sum = 0, amp = 0.5, freq = 1;
  for (let i = 0; i < octaves; i++) {
    sum += noise2(x*freq, y*freq) * amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum;
}
```

3D noise and fractal similarly.

### Terrain generation

For each chunk column at (cx, cz) in world space:
- World coords: for each local block (lx, lz), worldX = cx*16 + lx, worldZ = cz*16 + lz.
- m = fractal2(coords * 0.004) — large scale feature
- h = fractal2(coords * 0.02) — detail
- H = floor(5 + m*m*58 + h*10)
- Fill columns per rules.

Wait, "coords" — which coords? Probably worldX and worldZ. Let me use worldX, worldZ.

Column fill logic:
- y = 0: unbreakable stone
- below H-3: stone
- the 3 layers under the surface: dirt (or sand if H ≤ 16, stone if H ≥ 37)
- surface: snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass

Let me interpret "below H-3 stone" — meaning from y=1 to y=H-3 (exclusive?), stone. And "the 3 layers under the surface" — the surface is at y=H-1 (top), and 3 layers under it. So:
- y = 0: stone
- y = 1 .. H-4: stone (below H-3)
- y = H-3, H-2, H-1: the 3 layers under surface (surface at H-1)

Wait, let me reconsider. If surface is at level H-1, then 3 layers under surface would be H-1 (surface), H-2, H-3. Hmm, but "surface" is listed separately. Let me re-read.

"Column fill: y 0 = unbreakable stone; below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

So:
- y = 0: stone
- y < H-3: stone (i.e., y from 1 to H-4)
- 3 layers under the surface: dirt/sand/stone. The surface is the topmost layer. So the 3 layers under surface are at y = H-4, H-3, H-2? And surface at y = H-1?

Hmm wait. Let me think about it differently. "the 3 layers under the surface" means the 3 layers directly beneath the surface block. If surface is at y = H-1, then the 3 layers under it are at H-2, H-3, H-4. But that overlaps with "below H-3 stone".

Actually maybe the intended interpretation:
- Surface at y = H-1 (top block)
- 3 layers under surface: y = H-2, H-3, H-4 → dirt/sand/stone material
- Below that (y ≤ H-5): stone

But the spec says "below H-3 stone" and "3 layers under surface". These might be describing the same thing redundantly, OR the surface is at H-1 and the 3 layers are H-2,H-3,H-4.

Hmm, let me reconsider. Perhaps:
- The surface block is at some level.
- "below H-3 stone": for y < H-3, it's stone.
- "the 3 layers under the surface": these are the 3 layers just below the surface, which would be at H-4, H-3, H-2 (if surface at H-1). Wait no.

Let me think about what makes physical sense. Typical Minecraft-like: surface block on top, a few dirt/stone layers below, then bedrock/stone at bottom.

Given the spec's phrasing, I'll go with:
- y = 0: stone (unbreakable base)
- y = 1 to H-4: stone (below H-3)
- y = H-3, H-2, H-1: hmm, but that's only 3 layers including surface.

Wait, let me re-read once more very carefully:

"the 3 layers under the surface dirt" — 3 layers of dirt/sand/stone UNDER the surface. So surface is separate (the top), and there are 3 layers of filler beneath it.

If surface is at y = S, then filler is at S-1, S-2, S-3.

And "surface = snow if H≥46..." — the surface block type depends on H.

What's S in terms of H? "below H-3 stone" suggests the transition. If filler is 3 layers and below them is stone... 

Let me set: surface at y = H-1. Then:
- Filler (dirt etc.): y = H-2, H-3, H-4 (3 layers under surface)
- Below: y ≤ H-5: stone

But spec says "below H-3 stone". That contradicts unless filler is only at H-2 and H-3... no.

Alternatively: surface at y = H-2? Then filler at H-3, H-4, H-5. Below H-5 stone. Still doesn't match "below H-3".

Hmm, let me try yet another interpretation. Maybe:
- Surface at y = H-1.
- "the 3 layers under the surface" = y = H-2, H-3, H-4. But actually maybe the spec intends these to be grouped and "below H-3 stone" refers to y < H-3 being stone, which conflicts.

I think there might be redundancy/imprecision. Let me just make a reasonable choice that satisfies both literally where possible:

Interpretation: 
- y = 0: stone
- For y in [1, H-1): 
  - if y <= H-4: stone ("below H-3 stone" — close enough, but let me use H-3 boundary)
  
Actually, you know what, let me just carefully construct it so that:
- Top block (surface) at y = H-1
- 3 layers of filler below surface: y = H-2, H-3, H-4
- Everything below (y ≤ H-5) and y=0: stone

But "below H-3 stone" — hmm. If I want to honor "below H-3 stone", then y < H-3 should be stone, meaning y = H-4, H-5, ... all stone. And the filler (3 layers under surface) would be y = H-2, H-3, H-4? No, that includes H-4 which should be stone.

I'm overcomplicating. Let me just pick the interpretation that the surface is at H-1, filler occupies the 3 blocks immediately below (H-2, H-3, H-4), and stone below that. I'll treat "below H-3 stone" as approximately consistent (H-4 and below mostly stone, except the filler region). Actually the cleanest:

Let me define surface level SL = H - 1.
- y == 0: STONE
- y >= 1 && y <= SL - 4: STONE  (this is "below H-3" roughly, since SL-4 = H-5)

Hmm, this is getting confusing. Let me just go with a clean, sensible design:

```
for y in 0..H-1:
  if y == 0: stone
  else if y < H - 4: stone   // deep = stone
  else if y >= H - 4 && y < H - 1: filler (dirt/sand/stone based on H)
  // surface handled separately
// surface at y = H-1
```

Wait, that makes filler = H-4, H-3, H-2 (3 layers) and surface at H-1. And below H-4 is stone. "Below H-3 stone" ≈ below H-4 stone. Close. Let me adjust to make filler exactly the 3 layers under surface:

filler at y = H-2, H-3, H-4.
- y == 0: stone
- y < H-4: stone
- H-4 <= y <= H-2: filler
- y == H-1: surface

That's 3 filler layers (H-4, H-3, H-2) and surface at H-1. Below H-4 is stone. This satisfies "3 layers under surface" perfectly. "Below H-3 stone" — well H-4 is below H-3 and it's stone, and H-3 itself is filler... minor inconsistency but acceptable. Actually to be safe let me make the filler be exactly 3 layers and honor both:

I'll implement:
- y == 0: STONE
- y >= 1 && y <= H-4: STONE (this covers "below H-3")

Hmm wait, that's not right either because H-4 might be filler.

OK here's my final decision. I'll interpret literally and simply:

```
surfaceLevel = H - 1
for y = 0 to 79:
  if y == 0: block = STONE
  else if y > surfaceLevel: break (air, nothing)
  else if y == surfaceLevel: block = surfaceType(H)
  else: // 1 <= y <= surfaceLevel-1
    if y <= surfaceLevel - 4: block = STONE  // below H-3 region
    else: block = fillerType(H)  // the 3 layers under surface: surfaceLevel-3, -2, -1 => y = H-4, H-3, H-2
```

So filler = y in {H-4, H-3, H-2}, surface at H-1. That's 3 filler layers. Good. And "below H-3 stone" — y < H-4 is stone, and I'll consider H-4 as part of filler. Fine.

Actually, let me reconsider "below H-3 stone" more literally. It might mean the cutoff is literally at H-3: blocks at y < H-3 are stone. Then filler would be y in {H-2, H-1}? No...

Ugh. Let me just go with my clean interpretation. The exact boundary doesn't hugely matter for playability. Let me finalize:

- surfaceLevel = H - 1
- y == 0 → STONE
- y == surfaceLevel → surfaceType(H)
- surfaceLevel-3 <= y <= surfaceLevel-1 → fillerType(H)  (3 layers: H-4, H-3, H-2)

Wait surfaceLevel-1 = H-2, surfaceLevel-3 = H-4. So filler = H-4, H-3, H-2. Yes 3 layers.
- y < surfaceLevel-3 (i.e., y <= H-5) → STONE
- y == 0 → STONE

Great, this is clean and matches "3 layers under surface" and "below H-3 stone" (approximately, H-5 and below stone).

fillerType(H): sand if H <= 16, stone if H >= 37, else dirt.
surfaceType(H): snow if H >= 46, stone if H >= 37, sand if H <= 16, else grass.

Note: these can conflict (H<=16 gives sand filler and sand surface; H>=37 gives stone filler but snow/stone surface). That's fine, the rules are independent.

### Caves
For y between 3 and H-2, if 3D noise at position*0.09 exceeds 0.67, set air.
```
for y = 3 to H-2:
  if noise3(wx*0.09, y*0.09, wz*0.09) > 0.67: block = AIR
```
This applies to the filled column. Note caves shouldn't create floating islands typically, but spec says just set to air. Cave openings at surface could make holes, that's fine.

Actually wait, caves at y near surface (H-2 is close to surface H-1) would carve near surface. And y from 3. OK.

### Trees
On grass (surface == grass), when per-column hash < 0.02 and trunk fits: 4 wood up, then leaves.
```
columnHash = hash(cx_world?, cz?)  // deterministic per column
if surfaceType == grass && columnHash < 0.02:
  place tree if fits
```

Let me use hash(worldX, worldZ) for the column. Or hash(cx, cz). Let me use hash of world coords.

Tree placement: at the surface location (sx, sy=H-1, sz). Check trunk fits: need sy+4 <= 79. Place 4 wood at y = sy+1..sy+4. Then leaves.

Leaves structure: "leaves as a 5x5 layer twice, then 3x3, then 1 on top". Hmm, "5x5 layer twice" — two layers of 5x5? Then 3x3, then 1 on top.

Let me interpret: after trunk (4 wood), leaves start at height of top wood + 1.
- Two 5x5 layers (at top wood height and +1)? Or 5x5 at one level and again?

Actually typical tree: leaves form a canopy. Let me do:
- At y = trunkTop (sy+4): 3x3 leaves? 

Hmm the spec order: "4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

I think it means:
- 5x5 layer at some height
- 5x5 layer again (one higher)
- 3x3 layer
- 1 block on top

That's a lot of leaves. Let me place:
- Layer A (5x5): y = trunkTop + 1
- Layer B (5x5): y = trunkTop + 2
- Layer C (3x3): y = trunkTop + 3
- Top (1): y = trunkTop + 4

5x5 centered on trunk (which is at local center). Since chunk is 16 wide, center is at lx=7 or 8. Let me place trunk at local (7,7) or so. Actually to fit within chunk, trunk at lx, lz where the 5x5 leaves don't overflow. If trunk at lx=7, lz=7, 5x5 spans lx=5..9, lz=5..9 — within 0..15. Good. Trunk at lx=8,lz=8 → 6..10. Either works. Let me use lx=8, lz=8 for trunk (chunk center-ish). Actually 16/2 = 8, so center is between 7 and 8. Let me use 7,7 with leaves 5..9. Hmm, or 8,8 with leaves 6..10. Both fit. Let me use 7,7.

Wait, need to be careful: tree only placed if it fits inside the chunk. With trunk at 7,7 and 5x5 leaves (5-9), it fits. Good. But what if tree spawns near edge of generation? We're generating per chunk, and trunk at fixed 7,7 within chunk always fits. Good.

Actually, let me reconsider — should the tree be at a fixed local position or random? Spec says "when a per-column hash < 0.02" — deterministic per column, so one tree per qualifying column at... probably a fixed spot. Let me put trunk at local (7,7). Hmm, but that means all trees at same spot. That's fine for this simple clone. Actually, let me scatter a bit using the hash for position too. But simpler: fixed center. I'll use center-ish.

Let me reconsider the leaves. Actually maybe simpler and cleaner interpretation:
- 5x5 layer (y = trunkTop+1)
- 5x5 layer (y = trunkTop+2)  — "twice"
- 3x3 layer (y = trunkTop+3)
- 1 on top (y = trunkTop+4)

All "only into air" — don't overwrite existing blocks. But leaves adjacent to other leaves/trees... we only check air, so overlapping trees could merge. Fine.

Actually, having two full 5x5 layers of leaves is quite leafy but that's what spec says. Let me implement it. But note: these leaves won't generate light decay issues since we don't simulate light. They'll just render. Good.

Hmm, but wait — if I place leaves at 5x5 and they're transparent-ish (but leaves are opaque in this model, color 0x2e7d32, rendered as solid faces). Leaves are block type 6, treated as solid (non-air). So they occlude. That's fine visually.

Let me now think about meshing.

### Meshing

For each chunk with data:
- Create arrays: positions (3 per vertex), normals (3), colors (3).
- For each block (lx, ly, lz) with non-air ID:
  - worldX = cx*16+lx, etc.
  - For each of 6 directions, check neighbor block via global read helper (world coords). If neighbor is air, add face.
- Normals for each face:
  - +X (right): normal (1,0,0)
  - -X (left): (-1,0,0)
  - +Y (top): (0,1,0)
  - -Y (bottom): (0,-1,0)
  - +Z (front): (0,0,1)
  - -Z (back): (0,0,-1)
- Vertices per face (2 triangles, 6 vertices or 4 with indices). Let me use 6 non-indexed vertices for simplicity.

Face vertex positions (unit cube 0..1, but we offset by world coords). Standard cube:
```
// Each face defined by 4 corners. Let me define per-face.
```

Standard approach: for a face at block origin (x,y,z), the 4 corners:
- top (+Y): (x,y+1,z), (x,y+1,z+1), (x+1,y+1,z+1), (x+1,y+1,z) — CCW when viewed from above
- bottom (-Y): (x,y,z+1), (x,y,z), (x+1,y,z), (x+1,y,z+1)
- +X: (x+1,y,z+1), (x+1,y+1,z+1), (x+1,y+1,z), (x+1,y,z)
- -X: (x,y,z), (x,y+1,z), (x,y+1,z+1), (x,y,z+1)
- +Z: (x+1,y,z), (x+1,y+1,z), (x+1,y+1,z+1), (x+1,y,z+1)
- -Z: (x,y+1,z), (x,y,z), (x+1,y,z), (x+1,y+1,z)

Let me get winding order right so normals face outward. Using GLSL perspective, CCW is front-facing by default in Three.js (THREE.DoubleSide off, frontSide CCW). Let me ensure CCW.

Let me define face data:
```
const faces = [
  { dir: [+1,0,0],  normal:[1,0,0],  corners:[[1,0,1],[1,1,1],[1,1,0],[1,0,0]] }, // +X
  { dir: [-1,0,0],  normal:[-1,0,0], corners:[[0,0,0],[0,1,0],[0,1,1],[0,0,1]] }, // -X
  { dir: [0,+1,0],  normal:[0,1,0],  corners:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] }, // +Y top
  { dir: [0,-1,0],  normal:[0,-1,0], corners:[[0,0,0],[0,0,1],[1,0,1],[1,0,0]] }, // -Y bottom
  { dir: [0,0,+1],  normal:[0,0,1],  corners:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]] }, // +Z
  { dir: [0,0,-1],  normal:[0,0,-1], corners:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] }, // -Z
];
```

I need to verify winding gives outward-facing normals with CCW. Let me just trust a standard implementation and verify top face winding.

For top face (+Y, normal up): corners [(0,1,1),(1,1,1),(1,1,0),(0,1,0)]. Viewed from above (+Y looking down), points: (0,1), (1,1), (1,0), (0,0) in (x,z). Order: (0,1)->(1,1)->(1,0)->(0,0). Is that CCW? Going (0,1) to (1,1) is +x direction, then to (1,0) is -z, then to (0,0) is -x, then back. In screen space viewed from above with x right, z ... hmm, when looking down +Y, z goes away from viewer or toward? Convention dependent. 

This is error-prone. Since I can't test rendering easily, let me just make sure normals point outward and not worry too much about winding — actually winding matters for culling. But since we're only culling back faces and each block's visible faces are exterior, if winding is wrong those faces get culled and disappear.

To be safe, I could use THREE.FrontSide or DoubleSide. Actually MeshLambertMaterial default is SideDouble... no. Default is SingleSide? No. THREE.MeshLambertMaterial default side is FrontSide? Let me recall: default `side` is `THREE.FrontSide`. Wait, actually the default is `THREE.DoubleSide`? No.

Let me recall: Material.side default is FrontSide. Hmm, actually I recall THREE.js default is FrontSide for most materials... Let me just set `side: THREE.DoubleSide` to be safe? But spec says "ONE shared MeshLambertMaterial" and fake lighting via color multiplication. Using DoubleSide would double-light some faces but that's fine visually. Actually, if I compute normals correctly and use FrontSide with correct CCW winding, it's cleanest.

Hmm, let me just carefully derive CCW winding for each face such that the normal points outward. I'll use the right-hand rule: if fingers curl CCW (viewed from the side the normal points toward), thumb points along normal.

For the top face (+Y), viewing from above (from +Y looking toward -Y, i.e., looking in -Y direction), we want the vertices in CCW order. When looking down the -Y axis (from +Y), the x-axis points right and z-axis points... Let me set up: looking in -Y direction, with +X to the right, then +Z is "up" in our view? By right-hand rule, if +X is right and we look down -Y (into screen), then +Z should be... cross product: forward = -Y, right = +X, up = forward × right? In a right-handed system, up = right × forward? Let me just compute: for a right-handed coordinate with camera, up = forward × right is not standard.

Let me use a different method. I'll define each face's 4 corners in CCW order as seen from outside, using the standard cube mesh layout. Here's a well-known correct set (from three.js examples / common voxel tutorials):

Standard cube face definitions (positions relative to -0.5,-0.5,-0.5 origin, i.e., cube from -0.5 to 0.5):
```
// Right: x = 0.5
[0.5, 1.0, 0.5,  0.5, 1.0, 0.5... ]
```

Actually, let me use the approach where I define the quad with explicit CCW ordering verified by cross product.

For a face, given the outward normal N and a reference corner C, I pick two tangent vectors. Let me instead just hardcode a known-good set.

From the three.js "CubeGeometry" legacy and many voxel tutorials, the vertices and indices for a unit cube:

Vertices (8):
```
0: (0,0,0)
1: (1,0,0)
2: (1,1,0)
3: (0,1,0)
4: (0,0,1)
5: (1,0,1)
6: (1,1,1)
7: (0,1,1)
```
Faces (indices, CCW):
```
// -x face
[0,4,7, 0,7,3]
// +x face
[1,5,6, 1,6,2]
// -y face (bottom)
[0,1,5, 0,5,4]
// +y face (top)
[3,2,6, 3,6,7]
// -z face
[0,3,2, 0,2,1]  // hmm
// +z face
[4,5,1, 4,1,0]
```

This is the classic cube geometry. Let me verify winding for +y top face: indices [3,2,6,7] → positions (0,1,0),(1,1,0),(1,1,1),(0,1,1). Viewed from above (+Y looking down). Points in (x,z): (0,0),(1,0),(1,1),(0,1). Order: (0,0)->(1,0)->(1,1)->(0,1). Starting bottom-left, going right, up, left. That's CW when viewed from above (standard math CCW would be counterclockwise). Hmm, but this is the classic three.js cube which renders correctly, so maybe the convention works out because "viewed from above" perspective flips.

Actually, three.js uses CCW front face with the assumption of a left-handed... no. Three.js WebGL uses right-handed coordinate system and CCW is front-facing. The classic cube geometry above does render correctly in three.js. So I'll just reuse it. But my cube is per-block with world coords, and I add faces only where neighbor is air. The important thing: normals point outward and winding is CCW-from-outside.

Let me just adopt the classic cube index approach but adapt to per-face culling. Actually, let me restructure: I'll iterate blocks, for each block check 6 neighbors, and for each visible face append the appropriate 4 corners (with correct CCW order from the classic cube) plus normal and color.

Let me map the classic faces to directions:
- -x face: corners 0,4,7,3 → positions (0,0,0),(0,0,1),(0,1,1),(0,1,0). Normal (-1,0,0).
- +x face: corners 1,5,6,2 → (1,0,0),(1,0,1),(1,1,1),(1,1,0). Normal (1,0,0).
- -y (bottom): corners 0,1,5,4 → (0,0,0),(1,0,0),(1,0,1),(0,0,1). Normal (0,-1,0).
- +y (top): corners 3,2,6,7 → (0,1,0),(1,1,0),(1,1,1),(0,1,1). Normal (0,1,0).
- -z face: corners 0,3,2,1 → (0,0,0),(0,1,0),(1,1,0),(1,0,0). Normal (0,0,-1).
- +z face: corners 4,5,1,0 → (0,0,1),(1,0,1),(1,0,0),(0,0,0). Normal (0,0,1).

Now, for each block at world (x,y,z), I offset these by (x,y,z). The face is added if the neighbor in that direction is air.

Let me verify the -x face winding is CCW from outside (from -X looking toward +X). Looking in +X direction... from outside means standing at -X looking toward +X. The face is at x=0 (local). Corners (offset): (0,0,0),(0,0,1),(0,1,1),(0,1,0). In the Y-Z plane, viewing from -X (so we see Y horizontal? Z vertical?). When looking in +X direction with standard orientation (Y up), Z comes toward us or away? In right-handed coords looking along +X, Y is up, Z is toward viewer? Let me compute: if forward = +X, up = +Y, then right = up × forward? No. Camera basis: right = forward × up? In three.js, `right = up.apply... `. Let me just compute the normal via cross product of two edges and check it matches (-1,0,0).

Edge1 = P1 - P0 = (0,0,1)-(0,0,0) = (0,0,1).
Edge2 = P2 - P0 = (0,1,1)-(0,0,0) = (0,1,1).
Cross Edge1 × Edge2 = (0,0,1) × (0,1,1) = determinant:
i: (0*1 - 1*1) = -1
j: (1*0 - 0*1) = 0  → wait let me do it properly.
cross(a,b) = (a2*b3 - a3*b2, a3*b1 - a1*b3, a1*b2 - a2*b1)
a = (0,0,1), b = (0,1,1)
x = a.y*b.z - a.z*b.y = 0*1 - 1*1 = -1
y = a.z*b.x - a.x*b.z = 1*0 - 0*1 = 0
z = a.x*b.y - a.y*b.x = 0*1 - 0*0 = 0
Cross = (-1, 0, 0). 

Since cross(Edge1, Edge2) = (-1,0,0) which equals the normal, and the order is P0,P1,P2 (first triangle of quad), the winding is CCW and normal points outward. So this face's first triangle (P0,P1,P2) has outward normal. Good. So the classic cube winding with these indices gives outward normals. 

So my per-face corner lists (in order P0,P1,P2,P3) are correct, and I append triangles (P0,P1,P2) and (P0,P2,P3).

Let me define for each direction the 4 corners and normal:
```
const FACES = [
  { n:[-1,0,0], c:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]] }, // -x, neighbor is x-1
  { n:[ 1,0,0], c:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]] }, // +x, neighbor is x+1
  { n:[ 0,-1,0],c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] }, // -y (bottom), neighbor is y-1
  { n:[ 0, 1,0],c:[[0,1,0],[1,1,0],[1,1,1],[0,1,1]] }, // +y (top), neighbor is y+1
  { n:[ 0,0,-1],c:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] }, // -z, neighbor is z-1
  { n:[ 0,0, 1],c:[[0,0,1],[1,0,1],[1,0,0],[0,0,0]] }, // +z, neighbor is z+1
];
```

For each face, neighbor offset = the direction. So:
- face index 0 (-x): neighbor at (x-1, y, z)
- face 1 (+x): (x+1, y, z)
- face 2 (-y): (x, y-1, z)
- face 3 (+y): (x, y+1, z)
- face 4 (-z): (x, y, z-1)
- face 5 (+z): (x, y, z+1)

For each visible face (neighbor is air), append 6 vertices (4 corners × 2 triangles = but I'll do 6 vertices: P0,P1,P2,P0,P2,P3).

Normal per vertex = face normal. Color per vertex = blockColor * faceLighting (1.0 top, 0.8 side, 0.55 bottom).

Wait, spec: "multiply the block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms." So lighting factor depends on face normal:
- top face (normal +Y): 1.0
- bottom face (normal -Y): 0.55
- all sides (±X, ±Z): 0.8

Let me set:
```
let light = 0.8;
if (n[1] === 1) light = 1.0;
else if (n[1] === -1) light = 0.55;
```

Block color: hex to normalized RGB. Precompute block color RGB.

### Global read/write block helpers

Chunk key: `${cx},${cz}`. Chunk stores `{ data: Uint8Array(16*80*16), mesh: Mesh|null }`.

Data layout: I need index = f(x,y,z). Let me use layout: index = (lx) + (lz)*16 + (ly)*16*16? Or (ly)*(16*16) + (lz)*16 + lx. Let me pick: `idx = ly * 256 + lz * 16 + lx` where 256 = 16*16. Chunks are 16x16 horizontally, 80 tall. So size = 16*16*80 = 20480.

```
const CHUNK_W = 16, CHUNK_D = 16, CHUNK_H = 80;
function chunkIndex(lx, ly, lz) { return ly * (CHUNK_W*CHUNK_D) + lz * CHUNK_W + lx; }
```

Global read:
```
function getBlock(wx, wy, wz) {
  const cx = floorDiv(wx, 16);
  const lz = wz - cx... 
}
```
Wait, need local coords: lx = wx - cx*16, where cx = floor(wx/16). For negative wx, floor handles it.

```
function getBlock(wx, wy, wz) {
  if (wy < 0 || wy >= 80) return 0; // air
  const cx = Math.floor(wx / 16);
  const cz = Math.floor(wz / 16);
  const key = cx + ',' + cz;
  const chunk = chunks.get(key);
  if (!chunk) return 0;
  let lx = wx - cx*16;
  let lz = wz - cz*16;
  if (lx < 0 || lx >= 16 || lz < 0 || lz >= 16) return 0;
  return chunk.data[chunkIndex(lx, wy, lz)];
}
```

floorDiv for negatives: Math.floor handles negatives correctly in JS (Math.floor(-1.5) = -2). And wx/16 for negative wx: e.g., wx = -1 → -0.0625 → floor = -1. lx = -1 - (-1*16) = -1 + 16 = 15. Correct. wx = -16 → -1 → floor -1, lx = -16 - (-16) = 0. Correct. Good.

Write block (for breaking/placing):
```
function setBlock(wx, wy, wz, id) {
  if (wy < 0 || wy >= 80) return;
  const cx = Math.floor(wx/16), cz = Math.floor(wz/16);
  let lx = wx - cx*16, lz = wz - cz*16;
  if (lx<0||lx>=16||lz<0||lz>=16) return;
  const key = cx+','+cz;
  let chunk = chunks.get(key);
  if (!chunk) { chunk = { data: new Uint8Array(20480), mesh: null }; chunks.set(key, chunk); }
  chunk.data[chunkIndex(lx, wy, lz)] = id;
  rebuildChunk(cx, cz);
  // rebuild neighbor if on border
  if (lx === 0) rebuildChunk(cx-1, cz);
  if (lx === 15) rebuildChunk(cx+1, cz);
  if (lz === 0) rebuildChunk(cx, cz-1);
  if (lz === 15) rebuildChunk(cx, cz+1);
}
```

### Terrain generation into chunk data

```
function generateChunk(cx, cz) {
  const key = cx+','+cz;
  if (chunks.has(key)) return;
  const data = new Uint8Array(CHUNK_W*CHUNK_D*CHUNK_H);
  for (let lx=0; lx<16; lx++) {
    for (let lz=0; lz<16; lz++) {
      const wx = cx*16 + lx;
      const wz = cz*16 + lz;
      // terrain height
      const m = fractal2(wx*0.004, wz*0.004);
      const h = fractal2(wx*0.02, wz*0.02);
      let H = Math.floor(5 + m*m*58 + h*10);
      // tree check
      const thash = hash(wx, wz);
      let hasTree = false;
      // fill column
      for (let y=0; y<H; y++) {
        let id;
        if (y === 0) id = 3; // stone
        else if (y < H-4) id = 3; // stone
        else id = null; // placeholder
        // caves
        // handle
      }
    }
  }
}
```

Let me restructure generation cleanly:

```
function generateChunk(cx, cz) {
  const key = cx+','+cz;
  if (chunks.has(key)) return;
  const data = new Uint8Array(20480);
  for (let lx=0; lx<16; lx++) {
    for (let lz=0; lz<16; lz++) {
      const wx = cx*16 + lx;
      const wz = cz*16 + lz;
      const m = fractal2(wx*0.004, wz*0.004);
      const h = fractal2(wx*0.02, wz*0.02);
      const H = Math.floor(5 + m*m*58 + h*10);
      
      // fill column
      for (let y=0; y<H; y++) {
        let id = 3; // stone default
        if (y === 0) id = 3;
        else if (y <= H-4) id = 3; // below filler region
        else if (y >= H-3 && y <= H-2) {
          // 3 layers under surface
          id = fillerType(H);
        }
        // caves
        if (y >= 3 && y <= H-2) {
          if (noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) id = 0; // air
        }
        data[idx(lx,y,lz)] = id;
      }
      // surface
      const surfY = H-1;
      if (surfY >= 0 && surfY < 80) {
        data[idx(lx,surfY,lz)] = surfaceType(H);
      }
      // tree
      if (surfaceType(H) === 1 /*grass*/ && thash < 0.02) {
        // place tree at (lx, surfY, lz)
        placeTree(data, lx, surfY, lz, H);
      }
    }
  }
  chunks.set(key, { data: data, mesh: null });
}
```

Wait, there's an issue: caves set to air could remove the surface block or filler. And the surface is applied after the column loop, so even if caves hollowed things near surface, surface still set. But caves at y up to H-2 might remove the surface support. That's fine, caves can create holes.

Also, I need to be careful: after setting caves to air, the surface block at H-1 remains. But if a cave removed H-2, the surface at H-1 floats. That's acceptable (cave mouths).

fillerType(H): 
```
function fillerType(H) {
  if (H <= 16) return 4; // sand
  if (H >= 37) return 3; // stone
  return 2; // dirt
}
```

surfaceType(H):
```
function surfaceType(H) {
  if (H >= 46) return 7; // snow
  if (H >= 37) return 3; // stone
  if (H <= 16) return 4; // sand
  return 1; // grass
}
```

Hmm wait, but the spec says "the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = ...". So filler = dirt normally, sand if H<=16, stone if H>=37. My fillerType matches.

But there's subtlety: for H>=37, filler is stone and surface is stone (if 37<=H<46) or snow (H>=46). For H<=16, filler sand and surface sand. For 16<H<37, filler dirt, surface grass. Good.

Now the filler region: I said y in [H-3, H-2]. Let me double check "3 layers under surface". Surface at H-1. Layers under it: H-2, H-3, H-4. That's 3 layers. So filler should be y in [H-4, H-2], not [H-3,H-2]. Let me fix:

filler if `y >= H-4 && y <= H-2`. And below (y <= H-5) is stone. And y==0 stone.

Let me rewrite the column fill:
```
for y in 0..H-1:
  let id;
  if (y === 0) id = 3;
  else if (y <= H-5) id = 3;        // deep stone ("below H-3" ish)
  else if (y >= H-4 && y <= H-2) id = fillerType(H);  // 3 layers under surface
  // (y == H-1 handled as surface)
```
Then surface at y = H-1 overrides.

Hmm, but "below H-3 stone" — if I use y <= H-5 for stone, then H-4 is filler. To better match "below H-3", maybe I should make the filler only H-2, H-3 (2 layers) plus... no, spec clearly says 3 layers.

I'll go with 3 filler layers at H-4,H-3,H-2. The phrase "below H-3 stone" I'll interpret loosely. Actually, let me reconsider: maybe surface is at H-1, and "3 layers under surface" = H-2, H-3, H-4, and "below H-3 stone" is just poorly worded meaning "below [the filler] stone". Whatever. My implementation is reasonable.

Actually, wait. Let me reconsider whether the surface is at H-1 or H. "H = floor(5 + ...)". "surface = snow if H>=46...". The number of blocks in column is H (y from 0 to H-1). Surface block at y=H-1. That seems right (top of terrain).

Let me reconsider: total column height H, blocks at y=0..H-1. Surface at H-1. Good.

### Tree placement

```
function placeTree(data, lx, sy, lz, H) {
  const trunkTop = sy + 4; // need sy+4 <= 79
  if (trunkTop > 78) return; // don't fit
  // trunk
  for (let y = sy+1; y <= sy+4; y++) data[idx(lx,y,lz)] = 5; // wood
  // leaves
  // 5x5 layer twice, then 3x3, then 1 on top
  // trunkTop = sy+4
  // Layer 5x5 at y = trunkTop+1? or trunkTop?
}
```

Hmm, where do leaves start? "4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top". So after 4 wood (ending at sy+4 = trunkTop), leaves begin above: at trunkTop+1.

Let me place:
- 5x5 at y = trunkTop+1
- 5x5 at y = trunkTop+2
- 3x3 at y = trunkTop+3
- 1 on top at y = trunkTop+4

Need trunkTop+4 <= 79 → trunkTop <= 75 → sy <= 71. Since sy is surface (H-1) and H max ~ 5+... let me see max H: m in [0,1], m*m max 1, *58 = 58; h*10 max 10; +5 = 73. So H max ~73, sy max 72. trunkTop = 76 > 75. Edge case. Let me guard: if trunkTop+4 > 79 return. Actually let me just guard trunkTop <= 75.

But also "trunk fits inside the chunk" — the leaves 5x5 must fit in chunk. Trunk at (lx, lz). 5x5 leaves span lx-2..lx+2. For it to fit, lx in [2,13]. If trunk isn't in that range, skip. Let me check lx>=2 && lx<=13 && lz>=2 && lz<=13.

Hmm, but I earlier wanted trunk at fixed center. Let me place trunk at (7,7) within chunk? Then 5x5 spans 5..9, fits. But if tree only on grass columns with hash<0.02, and I place at fixed (7,7), all trees at same spot. That's fine. But then I should check (7,7) fits: 7 in [2,13], yes.

Actually, let me reconsider — maybe better to place trunk at the column's (lx, lz) but that's where grass is (surface position varies per column, it's every column). The tree should be at the surface location of that column, which is (lx, surfY, lz). So trunk base at (lx, sy, lz). Leaves centered there. For leaves to fit, need lx,lz in [2,13]. Many columns will have lx or lz outside that (near edges). So trees only near chunk center. That's fine and matches "trunk fits inside the chunk".

Let me place leaves centered at (lx, lz):
```
function placeTree(data, lx, sy, lz) {
  const tt = sy + 4;
  if (tt + 4 > 79) return;
  if (lx < 2 || lx > 13 || lz < 2 || lz > 13) return;
  for (let y=sy+1; y<=sy+4; y++) data[idx(lx,y,lz)] = 5;
  // 5x5 twice
  for (let dy=-2; dy<=2; dy++)
    for (let dz=-2; dz<=2; dz++)
      if (idx(lx+dy, tt+1, lz+dz) valid && data[...]===0) data = 6;
  for (similar at tt+2)
  // 3x3 at tt+3
  for dy in -1..1, dz -1..1: if air, leaves
  // 1 on top at tt+4
  if air: leaves
}
```

"only into air" — check data===0 before placing leaves. Also don't place leaves where there's already something (like another tree). Good.

Wait, but the 5x5 layers "twice" — should they be solid 5x5 or ring? Spec says "5x5 layer", implying solid 5x5. Let me do solid. That's a lot of leaves but fine.

Actually, hold on. Solid 5x5 twice = 50 leaves, plus 3x3=9, plus 1 = 60 leaves per tree. With tree density 2% that's fine.

Let me reconsider leaf shape to be a bit nicer — but spec explicitly says 5x5 twice then 3x3 then 1. I'll follow it literally.

Hmm, but actually a 5x5 solid block of leaves at two heights would look like a big leafy pillar. Combined with 4 wood trunk it's a valid tree. OK, literal implementation.

Let me define an idx bounds check helper:
```
function idx(lx, ly, lz) { return ly*256 + lz*16 + lx; }
function inBounds(lx, ly, lz) { return lx>=0&&lx<16&&ly>=0&&ly<80&&lz>=0&&lz<16; }
```

### Mesh building

```
function buildMesh(cx, cz) {
  const key = cx+','+cz;
  const chunk = chunks.get(key);
  if (!chunk) return;
  const pos = [], norm = [], col = [];
  const ox = cx*16, oz = cz*16;
  for (let ly=0; ly<80; ly++) {
    for (let lz=0; lz<16; lz++) {
      for (let lx=0; lx<16; lx++) {
        const id = chunk.data[idx(lx,ly,lz)];
        if (id === 0) continue;
        const wx = ox+lx, wy = ly, wz = oz+lz;
        for (const f of FACES) {
          const nx = wx + f.d[0], ny = wy+f.d[1], nz = wz+f.d[2];
          if (getBlock(nx,ny,nz) === 0) {
            // add face
            const crgb = blockRGB[id];
            let light = 0.8;
            if (f.n[1]===1) light=1.0;
            else if (f.n[1]===-1) light=0.55;
            for (const c of f.c) {
              pos.push(wx+c[0], wy+c[1], wz+c[2]);
              norm.push(f.n[0],f.n[1],f.n[2]);
              col.push(crgb[0]*light, crgb[1]*light, crgb[2]*light);
            }
          }
        }
      }
    }
  }
  // build geometry
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(norm,3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  ...
}
```

I need face direction `d` for each face. Let me add to FACES:
```
const FACES = [
  { d:[-1,0,0], n:[-1,0,0], c:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
  { d:[ 1,0,0], n:[ 1,0,0], c:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]] },
  { d:[ 0,-1,0],n:[ 0,-1,0],c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { d:[ 0, 1,0],n:[ 0, 1,0],c:[[0,1,0],[1,1,0],[1,1,1],[0,1,1]] },
  { d:[ 0,0,-1],n:[ 0,0,-1],c:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] },
  { d:[ 0,0, 1],n:[ 0,0, 1],c:[[0,0,1],[1,0,1],[1,0,0],[0,0,0]] },
];
```

Material:
```
const material = new THREE.MeshLambertMaterial({ vertexColors: true });
```
vertexColors true uses the color attribute. Good.

Reassign geometry each rebuild. Set chunk.mesh = mesh.

### Rebuild function

```
function rebuildChunk(cx, cz) {
  const key = cx+','+cz;
  const chunk = chunks.get(key);
  if (!chunk) return;
  if (chunk.mesh) {
    chunk.mesh.geometry.dispose();
    scene.remove(chunk.mesh);
  }
  const mesh = buildMesh(cx, cz);
  if (mesh) { chunk.mesh = mesh; scene.add(mesh); }
  else chunk.mesh = null;
}
```

buildMesh returns null if no vertices.

### World update loop

Each frame:
- Determine player's chunk.
- Generate blocks for chunks within 5 chunks of player (max 4 per frame).
- Build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame).
- For chunks farther than 7, remove mesh, dispose geometry, delete entry.

Let me track a queue/order. Simplest: maintain a list of chunk keys sorted by distance, process in order.

Let me implement:
```
let genQueue = []; // keys to generate
let buildQueue = [];

function updateWorld() {
  const pcx = Math.floor(player.pos.x/16);
  const pcz = Math.floor(player.pos.z/16);
  
  // Generate: chunks within 5 of player, max 4/frame
  // Build a candidate list sorted by distance
  let candidates = [];
  for (let dx=-5; dx<=5; dx++)
    for (let dz=-5; dz<=5; dz++) {
      const cx = pcx+dx, cz = pcz+dz;
      const key = cx+','+cz;
      if (!chunks.has(key)) candidates.push({key, cx, cz, dist: dx*dx+dz*dz});
    }
  candidates.sort((a,b)=>a.dist-b.dist);
  let genCount = 0;
  for (const c of candidates) {
    if (genCount >= 4) break;
    generateChunk(c.cx, c.cz);
    genCount++;
  }
  
  // Build meshes: chunks within 4 of player whose 4 neighbors have data, max 2/frame
  let buildCandidates = [];
  for (let dx=-4; dx<=4; dx++)
    for (let dz=-4; dz<=4; dz++) {
      const cx = pcx+dx, cz = pcz+dz;
      const key = cx+','+cz;
      const chunk = chunks.get(key);
      if (!chunk) continue;
      if (chunk.mesh) continue; // already built
      // check 4 neighbors have data
      const nE = chunks.get((cx+1)+','+cz);
      const nW = chunks.get((cx-1)+','+cz);
      const nN = chunks.get(cx+','+(cz+1));
      const nS = chunks.get(cx+','+(cz-1));
      if (nE && nW && nN && nS) {
        buildCandidates.push({key, cx, cz, dist: dx*dx+dz*dz});
      }
    }
  buildCandidates.sort((a,b)=>a.dist-b.dist);
  let buildCount = 0;
  for (const c of buildCandidates) {
    if (buildCount >= 2) break;
    rebuildChunk(c.cx, c.cz);
    buildCount++;
  }
  
  // Cleanup: chunks farther than 7
  for (const [key, chunk] of chunks) {
    const cx = parseInt(key.split(',')[0]);
    const cz = parseInt(key.split(',')[1]);
    const dx = cx - pcx, dz = cz - pcz;
    if (dx*dx+dz*dz > 49) {
      if (chunk.mesh) { chunk.mesh.geometry.dispose(); scene.remove(chunk.mesh); }
      chunks.delete(key);
    }
  }
}
```

Wait, "whose 4 neighbors already have data" — the 4 orthogonal neighbors (E,W,N,S). I check nE,nW,nN,nS. Good. This ensures we don't build a chunk before its neighbors exist (needed for correct face culling at borders).

Note: when building a chunk, getBlock reads neighbors which might be in neighbor chunks. If neighbor chunk exists but has no mesh yet, getBlock still returns data (data is generated). So face culling uses data, correct. Good.

But there's a subtlety: a chunk's mesh is built only after its 4 neighbors have data. Since data generation happens first (up to 4/frame), and builds after, the neighbor data should be present. Good.

### Player physics

Player state: pos (Vector3), vel (Vector3), yaw, pitch.
```
player = {
  pos: new THREE.Vector3(8, spawnY, 8),
  vel: new THREE.Vector3(0,0,0),
  yaw: 0, pitch: 0,
  onGround: false,
  width: 0.3, height: 1.8, eye: 1.62
};
```
Spawn above terrain at x=8, z=8. Need to find terrain height at (8,8). Let me compute spawn Y from getBlock column or just spawn high (y=60) and let gravity bring down. Spec says "spawn above terrain". Let me compute terrain height at (8,8) and spawn there + a bit.

Actually simpler: spawn at y such that it's above terrain. Let me query the column height. I can compute H for (8,8) via the noise, or just drop from y=64. Let me compute approximate: I'll spawn at y = 40 and it'll fall to surface. But spec says "spawn above terrain at x=8, z=8". Let me compute the surface height at (8,8) and spawn a few blocks above.

Let me add a helper to get terrain height:
```
function terrainHeightAt(wx, wz) {
  const m = fractal2(wx*0.004, wz*0.004);
  const h = fractal2(wx*0.02, wz*0.02);
  return Math.floor(5 + m*m*58 + h*10);
}
```
Spawn Y = terrainHeightAt(8,8) + 2 (above surface). But at spawn time chunks may not be generated, but terrainHeightAt computes deterministically. Good.

Physics update:
```
function updatePlayer(dt) {
  // gravity
  player.vel.y -= 25 * dt;
  // jump
  if (player.onGround && keys['space'] && ...) player.vel.y = 8.5;
  // movement input relative to yaw
  ...
  // integrate + collide
}
```

Movement: WASD at 5.5 m/s relative to yaw. Forward vector = (sin(yaw)? ...). Let me define yaw such that yaw=0 looks toward -Z or +Z. Camera rotation order "YXZ". Let me define:
- Camera quaternion set from euler (pitch, yaw, 0) with order YXZ.
- Forward direction (where camera looks) = -Z after rotation. In three.js, camera looks toward -Z by default. With Euler yaw around Y, forward = (-sin(yaw), 0, -cos(yaw))? Let me just compute horizontal movement from yaw.

Let me define horizontal movement direction based on yaw:
```
const forward = [ -Math.sin(yaw), 0, -Math.cos(yaw) ];  // camera forward
const right = [ Math.cos(yaw), 0, -Math.sin(yaw) ];
```
Hmm, let me be careful. With Euler order YXZ and camera looking at -Z:
- After yaw rotation θ around Y, the -Z axis rotates to (-sinθ·?...). 

Actually, let me just derive. Camera default forward (look-at) is (0,0,-1). Rotating by yaw θ about Y (positive = CCW when viewed from above, i.e., from +Y looking down, positive yaw rotates +X toward -Z... in three.js Y rotation positive goes from +Z to +X? Let me not overthink; I'll compute forward from the camera's actual orientation.

Simplest robust approach: compute camera direction from Euler.
```
camera.rotation.set(pitch, yaw, 0, 'YXZ');
const dir = new THREE.Vector3(0,0,-1).applyEuler(camera.rotation);
```
Then horizontal forward = (dir.x, 0, dir.z). Normalize. Movement input:
```
let moveX=0, moveZ=0;
if (keys.w) moveZ-=1; if(keys.s) moveZ+=1; if(keys.a) moveX-=1; if(keys.d) moveX+=1;
// relative to yaw
const sin = Math.sin(yaw), cos = Math.cos(yaw);
// WASD: w moves in camera forward direction
// forward horizontal = (-sin, 0, -cos) if yaw measured such that... 
```

Let me just use the camera-derived horizontal forward and right vectors:
```
const fwd = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
const right = new THREE.Vector3(-Math.cos(yaw), 0, Math.sin(yaw));
```
Hmm, I need to verify these are perpendicular and correct. Let me instead derive from camera rotation to guarantee consistency:
```
const camDir = new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ'));
const fwdH = new THREE.Vector3(camDir.x, 0, camDir.z).normalize();
const rightH = new THREE.Vector3(fwdH.z, 0, -fwdH.x); // perpendicular horizontal
```
Then velocity horizontal = fwdH * forwardInput + rightH * strafeInput, scaled by speed.

Where forwardInput from W/S, strafe from A/D. Let me define: pressing W → move along +fwdH; S → -fwdH; D → +rightH; A → -rightH.

```
let wish = new THREE.Vector3();
if (w) wish.add(fwdH);
if (s) wish.sub(fwdH);
if (d) wish.add(rightH);
if (a) wish.sub(rightH);
wish.normalize().multiplyScalar(5.5);
player.vel.x = wish.x; player.vel.z = wish.z;
```

Collision: axis-separated. Player AABB: half-width 0.3, height 1.8, eye 1.62. So the box spans from pos.x-0.3 to pos.x+0.3 in x/z, and from pos.y (feet) to pos.y+1.8 in y. Eye at pos.y+1.62.

Player box: min = (x-0.3, y, z-0.3), max = (x+0.3, y+1.8, z+0.3).

Collision against non-air blocks: for each axis, move, then check overlap with any non-air block in the AABB; if overlap, revert that axis (set back to previous). Landing sets onGround.

Implementation:
```
function collides(px, py, pz) {
  // AABB
  const minX = Math.floor(px - 0.3), maxX = Math.floor(px + 0.3);
  const minY = Math.floor(py), maxY = Math.floor(py + 1.8);
  const minZ = Math.floor(pz - 0.3), maxZ = Math.floor(pz + 0.3);
  for (let bx=minX; bx<=maxX; bx++)
    for (let by=minY; by<=maxY; by++)
      for (let bz=minZ; bz<=maxZ; bz++) {
        if (getBlock(bx,by,bz) !== 0) return true;
      }
  return false;
}
```

Move per axis:
```
// X
player.pos.x += player.vel.x * dt;
if (collides(player.pos.x, player.pos.y, player.pos.z)) {
  player.pos.x -= player.vel.x * dt;
  player.vel.x = 0;
}
// Z similarly
// Y
player.pos.y += player.vel.y * dt;
if (collides(...)) {
  player.pos.y -= player.vel.y * dt;
  if (player.vel.y > 0) player.onGround = false; // hit ceiling? 
  else player.onGround = true;
  player.vel.y = 0;
}
```

Wait, for Y: if moving down (vel.y<0) and collision, we're grounding → onGround=true, revert. If moving up (vel.y>0) and collision, hit ceiling → onGround=false, revert.

Jump: only if onGround, set vel.y = 8.5.

Let me structure:
```
player.vel.y -= 25*dt;
// horizontal set from input (above)
// jump
if (player.onGround && keys['Space']) { player.vel.y = 8.5; player.onGround = false; }
// integrate
move X, Z with collision (revert)
move Y with collision (revert, set onGround)
// fell off world
if (player.pos.y < -20) { player.pos.set(8, spawnY, 8); player.vel.set(0,0,0); }
```

Order matters. Let me do:
1. Apply gravity to vel.y.
2. Handle jump (if onGround and space).
3. Move X and collide.
4. Move Z and collide.
5. Move Y and collide; set onGround.
6. Reset onGround=false at start of Y? Actually set onGround=false initially, then during Y collision detection set true if landing.

Let me set `player.onGround = false;` before Y movement, then in Y collision branch if vel.y <= 0 set onGround=true.

### Raycasting for break/place

Raycast from camera center (origin = player eye position, direction = camera forward) against chunk meshes, max distance 6.

```
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
const origin = camera.position.clone();
const dir = new THREE.Vector3(0,0,-1).applyEuler(camera.rotation).normalize();
raycaster.set(origin, dir);
const hits = raycaster.intersectObjects(chunkMeshesArray, false);
```

chunkMeshesArray = array of all chunk meshes (for raycasting). I'll maintain `let meshList = []` and push/remove.

From hit point p and face normal n:
- break target = floor(p - n*0.5)
- place cell = floor(p + n*0.5)

Note p is the intersection point (world), n is the face normal (world). floor of (p - 0.5*n) gives the block we're hitting (the solid block). floor of (p + 0.5*n) gives the adjacent empty block.

Outline: black wireframe box targeting the break block. Create a BoxGeometry slightly larger than 1, wireframe, black, add to scene, position at block center. Update each frame if target changes.

```
let targetBlock = null; // {x,y,z}
let outline = null; // LineSegments
```

Create outline once:
```
const outlineGeo = new THREE.BoxGeometry(1.001,1.001,1.001);
outline = new THREE.LineSegments(outlineGeo, new THREE.LineBasicMaterial({color:0x000000}));
outline.visible = false;
scene.add(outline);
```
Each frame, if targetBlock set: outline.position.set(tx+0.5, ty+0.5, tz+0.5); visible=true; else visible=false.

Break/place only while pointer locked:
- left click: set target block to air (not at y 0). setBlock(tx,ty,tz, 0) but if ty===0 skip (unbreakable base).
- right click: place selected block if place cell is air and doesn't overlap player.

Overlap check: place cell AABB vs player AABB.

Selected block: hotbar selection (1-7 → block IDs 1-7). Air (0) not selectable.

### Hotbar

7 slots: grass(1), dirt(2), stone(3), sand(4), wood(5), leaves(6), snow(7). Colors per block. Selected via keys 1-7 or wheel.

```
let selected = 0; // index 0..6
const hotbarBlocks = [1,2,3,4,5,6,7];
```

Render hotbar in DOM (HTML divs). Update border on selection change.

Selection change: keys 1-7 set selected = key-1. Wheel: delta >0 → (selected+1)%7, delta<0 → (selected+6)%7.

### Sky, clouds, water

- Scene.background = 0x87ceeb.
- Scene.fog = new THREE.Fog(0x87ceeb, 40, 110).
- AmbientLight 0x..., intensity 0.65. DirectionalLight intensity 0.8.
- Clouds: ~25 transparent white boxes at height ~90, drift, wrap around player. Each cloud: BoxGeometry, MeshLambertMaterial transparent opacity maybe 0.9? Spec says "flat white transparent boxes". Let me use MeshLambertMaterial({color:0xffffff, transparent:true, opacity:1})? "transparent" — let me set opacity 0.85. Actually "flat" might mean flat shading. Let me use flatShading? MeshLambertMaterial has flatShading option. "flat white transparent boxes" — I read "flat" as in flat/planar boxes (they're boxes anyway). Let me make them wide flat boxes: BoxGeometry(width, small height, depth). Position them, animate x += speed each frame, reset when beyond player.x+range.

Let me make clouds as boxes sized e.g. (20, 4, 10) or so. 25 of them. Drift in +x. Wrap: if cloud.x - player.x > 100, move to player.x - 100 (approx). Simpler: store cloud base x relative; each frame cloud.x = player.x + (cloud.relX + speed*dt); wrap relX into [-100,100].

Let me do: clouds have {relX, relZ}. Each frame relX += speed*dt; if relX > 50 relX -= 100; if relX < -50 relX += 100. position.x = player.x + relX. z similar fixed.

- Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame. PlaneGeometry large (e.g., 500x500), MeshLambertMaterial transparent, color 0x00699b or blue, opacity ~0.7. Position y=14.3, x=z=player. Rotate to horizontal (default plane is in XY, need to rotate x=-90° to be flat). Actually THREE.PlaneGeometry is in XY plane; to make horizontal, rotateX(-Math.PI/2). Position at player.x, 14.3, player.z.

### UI

Start overlay: fullscreen div with title, controls list, "Click to play". On click, request pointer lock. Reappears when pointer lock released.

Crosshair: small div at center.

Hotbar: fixed bottom center.

Let me now write the HTML/CSS/JS.

Let me think about pointer lock API:
```
overlay.addEventListener('click', () => { canvas.requestPointerLock(); });
document.addEventListener('pointerlockchange', ...);
```
Actually requestPointerLock on canvas: `canvas.requestPointerLock()`. On click of overlay.

Mouse move (only when locked):
```
document.addEventListener('mousemove', (e) => {
  if (document.pointerLockElement === canvas) {
    player.yaw += e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    player.pitch = Math.max(-Math.PI/2+0.001, Math.min(Math.PI/2-0.001, player.pitch));
  }
});
```

Click handling: only when locked. Left click break, right click place. Suppress context menu.
```
canvas.addEventListener('mousedown', (e) => {
  if (document.pointerLockElement !== canvas) return;
  if (e.button === 0) { breakBlock(); }
  else if (e.button === 2) { placeBlock(); }
});
document.addEventListener('contextmenu', e => e.preventDefault());
```

Keys: keydown/keyup tracking. Use e.code 'KeyW' etc. and 'Space'.

Let me handle space: e.code === 'Space'.

Now, let me also handle the initial generation so spawn area is populated. On load, generate chunks around spawn (8,8) → chunk (0,0). Let me pre-generate the chunk the player spawns in and maybe build it.

Let me call updateWorld() a few times before starting, or just generate chunk (0,0) directly.

Actually, let me generate all chunks within 2 of spawn at start so the player lands nicely. I'll loop generateChunk for dx,dz in -2..2.

Let me now also make sure the mesh for spawn chunk is built.

Let me structure the main init:
1. Setup renderer, scene, camera, lights.
2. Create outline, clouds, water, hotbar DOM.
3. Generate spawn chunks + build.
4. Start animation loop.

Animation loop:
```
let last = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min((now-last)/1000, 0.1);
  last = now;
  if (locked) { updatePlayer(dt); }
  updateWorld();
  updateCamera();
  updateRaycast();
  updateClouds(dt);
  updateWater();
  render();
}
```

updateCamera: camera.position.copy(player.pos) with eye offset? Camera at player.pos + eye? Player.pos is feet. Eye = feet + 1.62. So camera.position = player.pos.x, player.pos.y + 1.62, player.pos.z. And rotation from euler(pitch,yaw,0,'YXZ').

Wait, but collision box uses feet at pos.y and top at pos.y+1.8, eye at pos.y+1.62. Camera at eye. Good.

Let me set:
```
camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
camera.rotation.set(player.pitch, player.yaw, 0, 'YXZ');
```

updateRaycast: set raycaster, find target, update outline, and handle clicks on mousedown.

Now breakBlock/placeBlock:
```
function breakBlock() {
  if (!targetBlock) return;
  const {x,y,z} = targetBlock;
  if (y === 0) return; // unbreakable
  setBlock(x,y,z, 0);
}
function placeBlock() {
  if (!placeCell) return;
  const {x,y,z} = placeCell;
  if (getBlock(x,y,z) !== 0) return;
  // overlap check with player
  if (blocksOverlap(x,y,z)) return;
  setBlock(x,y,z, hotbarBlocks[selected]);
}
```

blocksOverlap: check if placed block AABB intersects player AABB.
```
function blocksOverlap(bx, by, bz) {
  const px0 = player.pos.x-0.3, px1 = player.pos.x+0.3;
  const py0 = player.pos.y, py1 = player.pos.y+1.8;
  const pz0 = player.pos.z-0.3, pz1 = player.pos.z+0.3;
  return (bx+1 > px0 && bx < px1) && (by+1 > py0 && by < py1) && (bz+1 > pz0 && bz < pz1);
}
```

Now meshList maintenance: when rebuildChunk adds a mesh, push to meshList; when removing, splice. Let me have rebuildChunk manage it.

Actually simpler: maintain meshList as array; in rebuildChunk, if creating mesh push, if destroying remove. Let me track by reference.

Let me write rebuildChunk:
```
function rebuildChunk(cx, cz) {
  const key = cx+','+cz;
  const chunk = chunks.get(key);
  if (!chunk) return;
  if (chunk.mesh) {
    scene.remove(chunk.mesh);
    chunk.mesh.geometry.dispose();
    const i = meshList.indexOf(chunk.mesh);
    if (i>=0) meshList.splice(i,1);
  }
  const mesh = buildMesh(cx, cz);
  if (mesh) {
    chunk.mesh = mesh;
    scene.add(mesh);
    meshList.push(mesh);
  } else {
    chunk.mesh = null;
  }
}
```

buildMesh returns null if no vertices.

Now cleanup in updateWorld deletes chunk entries (including mesh). Need to dispose geometry and remove from meshList there too. Let me handle:
```
// cleanup
for (const [key, chunk] of Array.from(chunks.entries())) {
  ...
  if (far) {
    if (chunk.mesh) {
      chunk.mesh.geometry.dispose();
      scene.remove(chunk.mesh);
      const i = meshList.indexOf(chunk.mesh);
      if (i>=0) meshList.splice(i,1);
    }
    chunks.delete(key);
  }
}
```

Good.

Now, potential performance: meshing loops 16*16*80 = 20480 blocks × 6 faces. That's fine.

Let me also consider: getBlock during meshing calls into neighbor chunks. Neighbor chunk data must exist. Since we only build chunks whose 4 neighbors have data, and getBlock returns 0 for missing, border faces will be culled correctly (treat missing neighbor as air → face rendered). Wait, that's wrong! If neighbor chunk doesn't have data yet, getBlock returns 0 (air), so we'd render the border face. But once neighbor is generated, that face becomes internal and should be culled. But we rebuild on border changes... Actually the issue: we build chunk A before neighbor B has data → render border face. Later B generates → border face should be removed but A isn't rebuilt.

But the spec's rule "build meshes for chunks within 4 chunks whose 4 neighbors already have data" prevents this: we only build A after B,E,N,S have data. So when A is built, neighbors already have data (generated), so getBlock returns correct values, no spurious border faces. Good. That's why the neighbor-data precondition matters.

But there's still the cleanup deletion: when we delete a far chunk, its neighbors might still reference it via getBlock → returns 0 now (was previously data). Could cause internal faces to become visible (holes). Hmm. But chunks farther than 7 are deleted; their immediate neighbors (within 7) are still built. When a chunk is deleted, the neighbor's mesh still has faces that used to be culled by that chunk's blocks, now exposed → holes. 

To avoid, when deleting a chunk, we should also rebuild its neighbors. But spec says "remove the mesh, dispose its geometry and delete the entry" without mentioning neighbor rebuild on delete. Hmm. But the "avoid" list mentions neighbor rebuilds at borders for edits. For cleanup deletion, holes could appear.

However, chunks farther than 7 are far; their neighbors at distance 7 are still being built/rendered. When chunk at distance 8 is deleted, neighbor at distance 7 (still active) loses data → getBlock returns air → renders faces that were hidden → visible holes on the distance-7 chunk.

To be safe and correct, let me also rebuild the 4 neighbors of a deleted chunk in cleanup. It's cheap enough and avoids holes. The spec's "avoid" list is about not forgetting neighbor rebuilds; doing extra rebuilds on delete is fine and more correct. Actually, let me reconsider — the spec explicitly describes the cleanup as just remove+dispose+delete. But correctness-wise rebuilding neighbors is better. Given the instructions emphasize correctness ("Avoid ... forgetting neighbor-chunk rebuilds at borders"), I'll rebuild neighbors on delete too. It won't hurt.

Hmm, but wait: when we delete a chunk at distance 8 and rebuild neighbor at distance 7, the neighbor needs its OTHER neighbors too. It's fine, rebuildChunk just rebuilds that one chunk using current getBlock. Since we deleted the far chunk, getBlock returns air for those border faces → they render (exposed). That's the correct behavior for a chunk bordering unloaded space (like ocean). Fine.

Actually, thinking more: the far chunks being deleted are at distance >7. Their neighbors at distance 7 are within build range and will be rebuilt. Good. Let me add neighbor rebuild in cleanup.

Let me now also double-check the "generate within 5, build within 4, cleanup at >7" radii are consistent. Yes.

Let me also handle: initial spawn. Let me pre-generate and build chunks within radius 2 of spawn at startup synchronously so the world exists immediately.

Let me write a helper:
```
function prepopulate() {
  const pcx = Math.floor(8/16)=0, pcz=0;
  for dx,dz in -2..2: generateChunk;
  for dx,dz in -2..2: rebuildChunk (all have data since just generated)
}
```
Actually since we generate all within 2, then rebuild all within 2. Let me just call generate for -2..2 then rebuild -2..2.

Now let me also make sure getBlock for y outside 0-80 returns 0. And chunk data only holds y 0-79.

Let me also reconsider the fractal normalization: fractal2 sums amplitudes 0.5+0.25+0.125+0.0625 = 0.9375. Values in [0, 0.9375]. For height formula that's fine (just scales).

Now let me write the code.

One more: block colors as RGB. Precompute:
```
const blockRGB = [null, [], [], ...];
function hexToRGB(hex) { return [(hex>>16)&255, (hex>>8)&255, hex&255]; }
```
blockRGB[1] = hexToRGB(0x4caf50) etc. Index 0 unused.

Let me write it all now.

Also need to handle: when pointer not locked, don't update player, show overlay. Overlay click → requestPointerLock. On pointerlockchange, update `locked` variable and toggle overlay visibility.

Overlay visibility: when locked, hide overlay; when not locked, show. But the overlay click also triggers pointer lock request. Let me manage: overlay is a div on top. When clicked, request pointer lock. When locked, set overlay.style.display='none'. On pointerlockchange, if document.pointerLockElement !== canvas, overlay.style.display='' (show).

Let me code pointerlockchange listener:
```
document.addEventListener('pointerlockchange', () => {
  locked = (document.pointerLockElement === canvas);
  overlay.style.display = locked ? 'none' : 'block';
});
```
And overlay click:
```
overlay.addEventListener('click', () => { canvas.requestPointerLock(); });
```

But note: clicking overlay when already locked? Overlay is hidden when locked, so fine.

Also, some browsers require user gesture for pointer lock — the click handler provides that.

Now, initial: locked=false, overlay shown.

Let me also make sure the canvas is fullscreen and body margin 0.

Let me also add window resize handler.

Let me write the full file now.

Let me reconsider the water plane and fog: water at y=14.3, fog far 110, so water visible. Semi-transparent. Good.

Clouds: 25 boxes. Let me generate positions with a deterministic pattern (no random needed, but spec says clouds drift; I can place them somewhat randomly but deterministic is fine). Let me place them at fixed base positions relative to spawn, spread out.

```
const clouds = [];
for (let i=0;i<25;i++){
  const g = new THREE.BoxGeometry(14, 3, 10);
  const m = new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.9, flatShading:true});
  const mesh = new THREE.Mesh(g,m);
  const relX = (i%5)*20 - 50; // spread
  const relZ = Math.floor(i/5)*20 - 40;
  mesh.position.set(0, 90, 0);
  mesh.userData = {relX, relZ, speed: 2 + (i%3)};
  scene.add(mesh);
  clouds.push(mesh);
}
```
Update:
```
clouds.forEach(c=>{
  c.userData.relX += c.userData.speed*dt;
  if (c.userData.relX > 60) c.userData.relX -= 120;
  if (c.userData.relX < -60) c.userData.relX += 120;
  c.position.x = player.pos.x + c.userData.relX;
  c.position.z = player.pos.z + c.userData.relZ;
});
```

Water update:
```
water.position.x = player.pos.x;
water.position.z = player.pos.z;
```
Water mesh created once:
```
const waterGeo = new THREE.PlaneGeometry(400, 400);
const waterMat = new THREE.MeshLambertMaterial({color:0x0077be, transparent:true, opacity:0.7});
const water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);
```

Now let me also double check the raycast target computation and outline.

In updateRaycast (called each frame when locked):
```
raycaster.set(camera.position, dir);
const hits = raycaster.intersectObjects(meshList, false);
if (hits.length>0) {
  const p = hits[0].point;
  const n = hits[0].face.normal; // in world space? For non-scaled objects, face.normal is in object/local space, but since mesh is at origin with no rotation, local == world. Good.
  const tx = Math.floor(p.x - n.x*0.5);
  const ty = Math.floor(p.y - n.y*0.5);
  const tz = Math.floor(p.z - n.z*0.5);
  targetBlock = {x:tx,y:ty,z:tz};
  // place cell
  const px = Math.floor(p.x + n.x*0.5);
  const py = Math.floor(p.y + n.y*0.5);
  const pz = Math.floor(p.z + n.z*0.5);
  placeCell = {x:px,y:py,z:pz};
} else {
  targetBlock = null; placeCell = null;
}
// outline
if (targetBlock) { outline.position.set(tx+0.5,ty+0.5,tz+0.5); outline.visible=true; }
else outline.visible=false;
```

The face.normal from intersectObjects is normalized? It's the geometric normal, already unit length for our cube faces. Good. But it's in local coordinates; since mesh at origin no rotation, equals world. However, different chunks have meshes at origin (spec: "keep the mesh at the origin"). Yes all chunk meshes at origin, so local normals == world normals. 

But wait: raycaster face.normal is transformed by the object's rotation matrix. Since rotation is identity, it's fine.

Also, the raycaster uses object world matrix; chunk meshes at origin with no rotation → world matrix identity. Good.

Now, potential issue: raycasting against many chunk meshes each frame. meshList could have up to ~100 chunks. Raycaster against 100 meshes with thousands of triangles — fine at 60fps? Might be okay. Acceptable for this scope.

Let me also cap raycast distance 6 as specified.

Now, one concern: the raycast origin is camera.position which includes eye offset. The ray goes from eye forward. Good.

Let me also verify break target: floor(p - n*0.5). p is on the face of a solid block, n points out of that block toward camera. p - 0.5n moves halfway into the solid block → floor gives the solid block coords. Good. place cell p + 0.5n → into the empty neighbor → floor gives empty block. Good.

Edge: if ray grazes, could misfire, but fine.

Now let me also make sure we only react to clicks when locked — handled in mousedown handler.

Let me also handle the case where targetBlock.y === 0 for break (unbreakable) — skip.

Alright, let me also think about the jump key and onGround. Initial onGround false until grounded.

Let me also make sure we handle falling below -20 teleport.

Now, let me write everything.

Let me reconsider the noise functions for correctness and determinism.

hash(ix,iy): integers. In JS, bitwise ops work on 32-bit. ix*374761393 could exceed 2^31 and lose precision but it's still deterministic (float mult then bitwise converts). Actually `*` produces float, then `>>>` converts to uint32 (truncate). Deterministic. But large products lose low bits precision beyond 2^53. For world coords up to maybe ±a few thousand, products up to ~10^12 which exceeds 2^53 (9*10^15? no, 2^53 ≈ 9*10^15). 10^12 < 9*10^15, so fine, exact. Actually 374761393 * 4096 (max coord ~4096) ≈ 1.5*10^12, still < 2^53. Good, exact. But after XOR shifts and multiplications by 1274126177, products could exceed 2^53 → precision loss, but still deterministic (same inputs same outputs). Fine for noise.

Let me keep it simple and deterministic:
```
function hash(ix, iy) {
  let v = (ix * 374761393 + iy * 668265265) | 0;
  v = (v ^ (v >>> 13)) * 1274126177 | 0;
  v = (v ^ (v >>> 16)) >>> 0;
  return v / 4294967296;
}
```
`(x)|0` truncates to int32. The initial `(ix*... + iy*...) | 0` — the sum could be large but |0 wraps to 32-bit. Deterministic. Good.

Wait, `(ix * 374761393 + iy * 668265265) | 0`: the multiplication yields float; adding; |0 converts. For our coord ranges this is fine and deterministic.

noise2:
```
function noise2(x, y) {
  const xi = Math.floor(x) & 0xffffffff... 
}
```
Actually x,y are floats (world*0.004). Math.floor gives integer. Use as hash args. But Math.floor of negative gives negative; hash handles negatives via bitwise (negative |0 wraps). Fine.

```
function noise2(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf*xf*(3-2*xf), v = yf*yf*(3-2*yf);
  const a = hash(xi, yi), b = hash(xi+1, yi);
  const c = hash(xi, yi+1), d = hash(xi+1, yi+1);
  return lerp(lerp(a,b,u), lerp(c,d,u), v);
}
```
where lerp(a,b,t)=a+(b-a)*t (linear), and we apply smoothstep to u,v.

fractal2:
```
function fractal2(x, y) {
  let s=0, amp=0.5, freq=1;
  for(let i=0;i<4;i++){ s += noise2(x*freq,y*freq)*amp; amp*=0.5; freq*=2; }
  return s;
}
```

noise3:
```
function noise3(x,y,z){
  const xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z);
  const xf=x-xi,yf=y-yi,zf=z-zi;
  const u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf),w=zf*zf*(3-2*zf);
  const g=(i,j,k)=>hash3(i,j,k);
  const c00=g(xi,yi,zi),c10=g(xi+1,yi,zi),c01=g(xi,yi+1,zi),c11=g(xi+1,yi+1,zi);
  const x0=lerp(c00,c10,u), x1=lerp(c01,c11,u);
  const y0=lerp(x0,x1,v);
  const c02=g(xi,yi,zi+1),c12=g(xi+1,yi,zi+1),c03=g(xi,yi+1,zi+1),c13=g(xi+1,yi+1,zi+1);
  const y1=lerp(lerp(c02,c12,u),lerp(c03,c13,u),v);
  return lerp(y0,y1,w);
}
```

hash3:
```
function hash3(ix,iy,iz){
  let v=(ix*374761393+iy*668265265+iz*668265264+iz*1274126177)|0;
  v=(v^(v>>>13))*1274126177|0;
  v=(v^(v>>>16))>>>0;
  return v/4294967296;
}
```

Good enough.

Now the height formula uses fractal2 at coords*0.004 and coords*0.02. Let me pass (wx, wz).

Let me finalize surfaceType/fillerType and generation.

Let me also double check: "surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass." Order matters: check H>=46 first (snow), then H>=37 (stone), then H<=16 (sand), else grass. But what if H>=46 AND ... it's snow. If 37<=H<46 stone. If H<=16 sand. If 16<H<37 grass. There's a gap: 16<H<37 grass; but also between 37 and 46 stone; 46+ snow. What about H exactly between, like 20 → grass. Fine. My function:
```
function surfaceType(H){
  if (H>=46) return 7;
  if (H>=37) return 3;
  if (H<=16) return 4;
  return 1;
}
```
Good.

fillerType:
```
function fillerType(H){
  if (H<=16) return 4;
  if (H>=37) return 3;
  return 2;
}
```
Good.

Now generation loop with caves. Let me write generateChunk:

```
function generateChunk(cx, cz){
  const key=cx+','+cz;
  if(chunks.has(key)) return;
  const data=new Uint8Array(20480);
  for(let lx=0;lx<16;lx++){
    for(let lz=0;lz<16;lz++){
      const wx=cx*16+lx, wz=cz*16+lz;
      const m=fractal2(wx*0.004,wz*0.004);
      const h=fractal2(wx*0.02,wz*0.02);
      const H=Math.floor(5+m*m*58+h*10);
      // fill
      for(let y=0;y<H;y++){
        let id=3; // stone
        if(y<=H-4) id=3;
        else if(y>=H-4&&y<=H-2) id=fillerType(H);
        // caves
        if(y>=3&&y<=H-2 && noise3(wx*0.09,y*0.09,wz*0.09)>0.67) id=0;
        data[idx(lx,y,lz)]=id;
      }
      // surface
      const sy=H-1;
      if(sy>=0&&sy<80) data[idx(lx,sy,lz)]=surfaceType(H);
      // tree
      if(surfaceType(H)===1 && hash(wx,wz)<0.02){
        placeTree(data,lx,sy,lz);
      }
    }
  }
  chunks.set(key,{data:data,mesh:null});
}
```

Wait, there's a subtle bug: caves set id=0 for y in [3,H-2], which could remove the filler or even the surface-supporting blocks. But surface is applied after, at sy=H-1. And the surface block stays. But if caves removed blocks below surface, surface floats — acceptable.

However, there's a bigger issue: caves carve near the surface (y up to H-2, and surface at H-1). So cave openings at the surface create holes/caves surfacing. That's the intended "underground caves" look. Good.

But also, caves might carve the ground player walks on, creating pits. Acceptable.

placeTree:
```
function placeTree(data,lx,sy,lz){
  const tt=sy+4; // trunk top
  if(tt+4>79) return;
  if(lx<2||lx>13||lz<2||lz>13) return;
  // trunk
  for(let y=sy+1;y<=sy+4;y++) data[idx(lx,y,lz)]=5;
  // leaves: 5x5 twice, 3x3, 1 top
  const leaf=(ly)=>{
    if(ly<0||ly>=80) return;
    for(let dy=-2;dy<=2;dy++)for(let dz=-2;dz<=2;dz++){
      const ii=idx(lx+dy,ly,lz+dz);
      if(inB(ii)&&data[ii]===0) data[ii]=6;
    }
  };
  leaf(tt+1); leaf(tt+2);
  // 3x3
  const ly=tt+3;
  if(ly>=0&&ly<80){for(let dy=-1;dy<=1;dy++)for(let dz=-1;dz<=1;dz++){const ii=idx(lx+dy,ly,lz+dz);if(inB(ii)&&data[ii]===0)data[ii]=6;}}
  // 1 top
  const ly2=tt+4;
  if(ly2>=0&&ly2<80){const ii=idx(lx,ly2,lz);if(inB(ii)&&data[ii]===0)data[ii]=6;}
}
```
inB(ii) checks index bounds: ii in [0,20480). Since lx+dy in [0,15] guaranteed by lx in [2,13] and dy in [-2,2] → [0,15]. ly checked. Good. So inB just checks ly range and index<20480. Let me define inB(index)=index>=0&&index<20480. And ly bounds checked separately.

Actually let me simplify: since lx in [2,13], lx+dy in [0,15] always valid. ly bounds checked. So:
```
const ii=idx(lx+dy,ly,lz+dz);
if(ly>=0&&ly<80&&data[ii]===0) data[ii]=6;
```
Good.

idx(lx,ly,lz)=ly*256+lz*16+lx. For lx in [0,15], lz in [0,15], ly in [0,79]: max = 79*256+15*16+15 = 20224+240+15=20479 <20480. Good.

Now, let me reconsider: the tree leaves are solid 5x5 layers which will look like flat slabs. Fine per spec.

Let me now also double-check meshing neighbor check uses getBlock with world coords. During meshing, for a block at world (wx,wy,wz), neighbor at (wx+dx,...). getBlock handles chunk boundaries and returns data. Good.

Now, let me write the whole HTML.

Let me also make sure to include the hotbar DOM with 7 slots.

Let me write CSS for hotbar slots: small squares with block color and number.

Let me now also reconsider the fog near value. Fog(new THREE.Fog(hex, near, far)) with near 40, far 110. Spec: "matching fog (about 40 to 110)". Good.

Ambient 0.65, directional 0.8. DirectionalLight position set, .castShadow? Not needed. Just intensity.

Let me set:
```
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(0.4, 1, 0.2)... 
```
Actually DirectionalLight intensity property. In r128, intensity default 1, set dir.intensity=0.8. Position arbitrary.

Wait, but with vertexColors and MeshLambertMaterial, the directional light still applies via lambert (dot with normal). Our fake lighting is baked into vertex colors. Good, combined effect.

Let me set dir.position to something and normalize.

Now let me also verify camera far 400, fov 75.

Renderer:
```
const renderer = new THREE.WebGLRenderer({antialias:false});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(false)? 
```
Let me set pixelRatio to devicePixelRatio for crispness, but that could slow. Let me set renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2)). Fine.

Canvas appended to body.

Background: scene.background = new THREE.Color(0x87ceeb). Also fog color same.

Let me write it all.

Let me reconsider spawn: terrainHeightAt(8,8). Compute and spawn above.

```
const spawnY = terrainHeightAt(8,8)+2;
player.pos.set(8, spawnY, 8);
```

But we should ensure chunk (0,0) is generated before spawn (it is, via prepopulate). terrainHeightAt is deterministic regardless.

Now let me also make sure the initial prepopulate builds the spawn mesh so player sees ground.

Let me write main():
```
init world objects
prepopulate() // generate + build radius 2
start loop
```

Let me now also handle the case where getBlock during collision for y up to 79 and the player might be at y near 80 — fine.

Let me also ensure we don't place blocks in the player.

Alright, writing now.

Let me also reconsider: "After an edit rebuild the chunk, and also the neighbor chunk if the block sits on a chunk border." My setBlock does rebuildChunk(cx,cz) plus border neighbors. Good.

Also rebuildChunk disposes old geometry. Good.

Let me also handle meshList removal on cleanup. Done.

Let me write the file.

Actually, I realize there might be an issue with `data[idx(...)]` when generating — idx uses ly which for y loop is fine.

Let me also double check the fractal2 for height: at coords*0.004, very smooth large features; coords*0.02 medium. H = 5 + m²*58 + h*10. m in [0,~0.94], m² in [0,~0.88], *58 → [0,51]. h in [0,~0.94]*10 → [0,9.4]. Plus 5. So H in [5, ~65]. Reasonable terrain heights 5-65. Mountains H>=37, snow H>=46, beaches H<=16. Good.

Water at 14.3: where H<=16 (sand/beach) terrain near water level. Lakes form where H<14ish. Good.

Now, one more: the player spawns at (8,8) which is chunk 0,0. terrainHeightAt(8,8) computed. Let me make sure spawn lands on solid ground.

Let me also add: when placing block, check not overlapping player using blocksOverlap. Good.

Let me also handle selected block display in hotbar: highlight border.

Let me write the hotbar HTML:
```
<div id="hotbar">
  <div class="slot" data-i="0" style="background:#4caf50">1</div>
  ...
</div>
```
Each slot: a square with background color and number. Selected gets white border.

Update:
```
function updateHotbar(){
  document.querySelectorAll('.slot').forEach(el=>{
    el.classList.toggle('selected', parseInt(el.dataset.i)===selected);
  });
}
```
CSS: .slot.selected { outline: 2px solid white; }

Let me finalize.

Also, I should prevent the page from scrolling with arrow keys/space — but space is jump. Since pointer locked, key events go to document. Let me listen on document for keydown/keyup.

Let me handle keydown: track pressed keys in `keys` object. Prevent default for space to avoid scroll when not locked? When locked, default prevented by pointer lock. Let me just set keys[code]=true/false.

Space as jump: in updatePlayer, if keys['Space'] && onGround → jump.

Let me use e.code: 'Space', 'KeyW','KeyA','KeyS','KeyD','Arrow...'? Spec says WASD. I'll support WASD and maybe arrows. Let me just WASD + Space.

Now writing.

Let me also make sure mouse wheel changes selection:
```
window.addEventListener('wheel', (e)=>{
  if(!locked) return;
  e.deltaY>0 ? selected=(selected+1)%7 : selected=(selected+6)%7;
  updateHotbar();
},{passive:true});
```

Keys:
```
document.addEventListener('keydown',(e)=>{
  const k=e.code;
  if(k>='Digit1'&&k<='Digit7') { selected=parseInt(k.slice(5))-1; updateHotbar(); }
  keys[k]=true;
});
document.addEventListener('keyup',(e)=>{ keys[e.code]=false; });
```

Digit1..7 → selected 0..6.

Now, when not locked, keys still tracked but updatePlayer skipped. Fine.

Let me write the complete file now. I'll be careful with syntax.

Let me also reconsider: the overlay click requests pointer lock. But requestPointerLock must be called from a user gesture — click handler qualifies.

Also, some browsers: clicking canvas also. Let me attach requestPointerLock to overlay click.

Let me also add: if user clicks while locked elsewhere, fine.

Let me write.

Actually, let me reconsider the meshList raycasting performance and correctness: intersectObjects with array does multiple raycasts. Fine.

Also, the outline wireframe: LineSegments with BoxGeometry(1.002,...) gives 12 lines (wireframe of box). Good, black.

Position at block center (x+0.5,...). Good.

Now, let me also make sure that when we break a block at y=0 we skip. And break only if targetBlock exists.

Let me also ensure place cell air check and overlap.

Alright, writing the final file.

Let me also double-check: getBlock for neighbor during meshing returns block ID; we compare ===0 for air. Good.

Let me also verify the FACES winding once more for the +Y top face to ensure outward normal and CCW. I computed earlier the classic cube +y face indices [3,2,6,7] → corners (0,1,0),(1,1,0),(1,1,1),(0,1,1). In my FACES array I have for +y: c:[[0,1,0],[1,1,0],[1,1,1],[0,1,1]]. Yes matches. Good.

For -y bottom: classic [0,1,5,4] → (0,0,0),(1,0,0),(1,0,1),(0,0,1). My FACES -y: c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]. Matches. Good.

+x: classic [1,5,6,2] → (1,0,0),(1,0,1),(1,1,1),(1,1,0). My +x: [[1,0,0],[1,0,1],[1,1,1],[1,1,0]]. Matches.

-x: classic [0,4,7,3] → (0,0,0),(0,0,1),(0,1,1),(0,1,0). My -x: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]]. Matches.

-z: classic [0,3,2,1] → (0,0,0),(0,1,0),(1,1,0),(1,0,0). My -z: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]]. Matches.

+z: classic [4,5,1,0] → (0,0,1),(1,0,1),(1,0,0),(0,0,0). My +z: [[0,0,1],[1,0,1],[1,0,0],[0,0,0]]. Matches.

All match classic cube. 

Now the neighbor direction `d` for each face must correspond:
- -x face: neighbor at (x-1,y,z) → d=[-1,0,0]. ✓ (my FACES[0])
- +x: d=[1,0,0] ✓
- -y: d=[0,-1,0] ✓
- +y: d=[0,1,0] ✓
- -z: d=[0,0,-1] ✓
- +z: d=[0,0,1] ✓

Good.

Now let me write the final code.

Let me also add a subtle thing: the raycaster face.normal might not be normalized but for unit normals it's fine. Also it's in object space; mesh has no rotation → world. Good.

Also I should set raycaster to use the camera position as origin (eye). And direction from camera rotation. Let me compute dir each frame:
```
const dir = new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(player.pitch, player.yaw, 0, 'YXZ'));
```

Good.

Now, finalize and write.

Let me also handle the case where getBlock during meshing calls into neighbor chunks. Neighbor chunk data must exist.

Let me write the whole thing carefully now.

I'll produce the single code block.

Let me reconsider one thing about generateChunk being called during the frame loop and also prepopulate. Fine.

Also, I want to make sure that when we delete a far chunk and rebuild its neighbor, the neighbor rebuild uses getBlock which now returns 0 for the deleted chunk → renders border face. That's correct (chunk bordering void shows face). Good.

Let me write.

Actually, let me reconsider whether to rebuild neighbors on delete. The spec's cleanup section says just remove+dispose+delete. But to avoid holes, rebuilding neighbors is safer. However, rebuilding neighbors could be considered extra. But correctness > strict spec adherence here, and the spec's own "avoid" list stresses neighbor rebuilds. I'll rebuild the 4 orthogonal neighbors on delete. Minimal overhead.

Let me write final code.

I also want to double check: after deleting chunk and rebuilding neighbor, the neighbor's mesh is rebuilt fresh — good, no holes.

But there's a subtlety: when we delete a chunk at distance 8, its neighbor at distance 7 — but distance 7 chunk is within build radius (4)?? No, build radius is 4 from player. Distance 7 > 4, so it wouldn't be rebuilt in normal build step. But it exists (built earlier when it was within 4, or it's currently within 4?). Hmm, actually chunks are kept as long as within 7. A chunk at distance 7 is kept. Is it built (has mesh)? Build only happens for within 4. So a chunk at distance 5,6,7 that was built when closer, persists (kept until distance>7) but not rebuilt. Its data persists. So when we delete distance-8 chunk and rebuild distance-7 neighbor, the neighbor gets rebuilt with correct faces. Good.

But actually, would a distance-7 chunk even have been built? It's built when within 4 (distance<=4). As player moves away, it stays until distance>7. So yes it has mesh. Rebuilding it on delete of neighbor is fine.

OK, enough. Let me write.

Let me also make sure the loop's cleanup iterates safely while deleting. I'll collect keys to delete then delete.

Final code below.

Let me write it out fully.

I need to be careful about template literals with ${} in JS — fine.

Let me write the CSS minimal but functional.

Let me produce the final answer.

Wait, I should double check the `lerp` smoothstep usage. In noise2 I compute u,v as smoothstep(t) then lerp linearly with u,v. Good.

Also fractal2 returns sum up to ~0.94. For height formula fine.

Let me also verify hash returns [0,1). v/4294967296 where v is uint32 [0,2^32). Good, [0,1).

Now, potential issue: `(ix * 374761393 + iy * 668265265) | 0` — if the sum exceeds 2^31 it wraps (signed). Deterministic. Fine.

Let me write.

Also I realize: for the fractal noise at coords*0.004, when world coords are large (player moves far), x*0.004 could be large but Math.floor handles it; hash takes floor result which could be large but |0 wraps. Deterministic per coordinate. Good. Though far-away noise might repeat patterns due to 32-bit hash collisions, but that's acceptable for this clone.

Alright, final.

Let me also ensure I add the outline line segments geometry dispose somewhere? Not necessary; it's created once.

Let me write the file now.

Let me reconsider the water plane orientation. THREE.PlaneGeometry creates geometry in XY plane (z=0). To lay flat (XZ plane), rotateX(-90°) → maps Y to Z. After rotateX(-90°), the plane's normal points... Let me just use it; position at y=14.3. It should be horizontal. Actually rotateX(-Math.PI/2) rotates the XY-plane geometry so it lies in XZ plane. Good.

Let me finalize.

Also, I want to make sure the canvas fills screen and no scrollbars: body{margin:0;overflow:hidden;}

Now writing final code.

Let me also add requestPointerLock fallback for older browsers? Not needed.

Final answer below.

Actually, let me reconsider the `keys` for space: e.code for space is 'Space'. Good.

Also arrow keys not needed.

Let me also handle window blur to unlock? Not necessary.

Writing now.

One more consideration: performance of regenerating raycast each frame against all meshes. Fine.

Let me write the complete HTML file.

I'll now also reconsider: should updateWorld run every frame? Spec says "Each frame: generate... build... cleanup". Yes every frame. But generating 4/frame and building 2/frame. Cleanup each frame. Good.

But at start, before player moves, chunks around spawn are generated/built via prepopulate. Then as player moves, more generate. Good.

Let me write.

Also, I need to make sure `chunks` Map iteration for cleanup uses snapshot. I'll do `Array.from(chunks.keys())`.

Let me write final.

Let me reconsider spawn height: terrainHeightAt(8,8)+2. If that's like 40, player spawns at 42, falls to surface ~41. Good.

Now finalize.

Let me write out the entire file in one go.

I'll include comments sparingly for clarity.

Let me make sure to close all tags and braces.

Final code:
</think>

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>mc.html</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; background: #87ceeb; }
  canvas { display: block; }
  #overlay {
    position: fixed; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; color: #fff; font-family: monospace;
    background: rgba(0,0,0,0.55); cursor: pointer; z-index: 10;
  }
  #overlay h1 { font-size: 48px; margin: 0 0 10px; letter-spacing: 2px; text-shadow: 3px 3px 0 #000; }
  #overlay ul { text-align: left; font-size: 16px; line-height: 1.7; }
  #overlay .play { margin-top: 18px; font-size: 22px; border: 2px solid #fff; padding: 8px 20px; display:inline-block; }
  #crosshair {
    position: fixed; left: 50%; top: 50%; transform: translate(-50%,-50%);
    width: 16px; height: 16px; pointer-events: none; z-index: 5;
  }
  #crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: #ffffff; box-shadow: 0 0 2px #000;
  }
  #crosshair::before { left: 7px; top: 0; width: 2px; height: 16px; }
  #crosshair::after { top: 7px; left: 0; height: 2px; width: 16px; }
  #hotbar {
    position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%);
    display: flex; gap: 4px; padding: 4px; background: rgba(0,0,0,0.45);
    border-radius: 4px; z-index: 5; pointer-events: none;
  }
  .slot {
    width: 42px; height: 42px; border: 2px solid #333; border-radius: 3px;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-family: monospace; font-size: 13px; font-weight: bold;
    text-shadow: 1px 1px 0 #000; position: relative;
  }
  .slot.selected { border-color: #ffffff; box-shadow: 0 0 6px #fff; }
  .slot .num { position:absolute; top: 1px; left: 3px; font-size: 11px; opacity: 0.85; }
</style>
</head>
<body>
<div id="overlay">
  <h1>MINECRAFT-CLONE</h1>
  <ul>
    <li><b>WASD</b> — move &nbsp; <b>Space</b> — jump &nbsp; <b>Mouse</b> — look</li>
    <li><b>Left Click</b> — break &nbsp; <b>Right Click</b> — place</li>
    <li><b>1–7 / Wheel</b> — select block &nbsp; <b>Esc</b> — release mouse</li>
  </ul>
  <div class="play">Click to play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// ---------- Blocks ----------
const BLOCKS = [
  {id:0,name:'air',  color:0x000000},
  {id:1,name:'grass',color:0x4caf50},
  {id:2,name:'dirt', color:0x795548},
  {id:3,name:'stone',color:0x9e9e9e},
  {id:4,name:'sand', color:0xe7d9a8},
  {id:5,name:'wood', color:0x8d6e63},
  {id:6,name:'leaves',color:0x2e7d32},
  {id:7,name:'snow', color:0xffffff},
];
const HOTBAR = [1,2,3,4,5,6,7];
const blockRGB = [];
for (let i=0;i<BLOCKS.length;i++){
  const c = BLOCKS[i].color;
  blockRGB[i] = [(c>>16)&255, (c>>8)&255, c&255];
}

// ---------- Chunk constants ----------
const CW=16, CD=16, CH=80;
const CHUNK_SIZE = CW*CD*CH; // 20480
function idx(lx,ly,lz){ return ly*256 + lz*16 + lx; }

// ---------- Noise ----------
function hash(ix,iy){
  let v = (ix*374761393 + iy*668265265) | 0;
  v = (v ^ (v>>>13)) * 1274126177 | 0;
  v = (v ^ (v>>>16)) >>> 0;
  return v / 4294967296;
}
function hash3(ix,iy,iz){
  let v = (ix*374761393 + iy*668265265 + iz*1274126177) | 0;
  v = (v ^ (v>>>13)) * 1274126177 | 0;
  v = (v ^ (v>>>16)) >>> 0;
  return v / 4294967296;
}
function lerp(a,b,t){ return a+(b-a)*t; }
function smooth(t){ return t*t*(3-2*t); }
function noise2(x,y){
  const xi=Math.floor(x), yi=Math.floor(y);
  const xf=x-xi, yf=y-yi;
  const u=smooth(xf), v=smooth(yf);
  const a=hash(xi,yi), b=hash(xi+1,yi), c=hash(xi,yi+1), d=hash(xi+1,yi+1);
  return lerp(lerp(a,b,u), lerp(c,d,u), v);
}
function noise3(x,y,z){
  const xi=Math.floor(x), yi=Math.floor(y), zi=Math.floor(z);
  const xf=x-xi, yf=y-yi, zf=z-zi;
  const u=smooth(xf), v=smooth(yf), w=smooth(zf);
  const g=(i,j,k)=>hash3(i,j,k);
  const c00=g(xi,yi,zi),c10=g(xi+1,yi,zi),c01=g(xi,yi+1,zi),c11=g(xi+1,yi+1,zi);
  const x0=lerp(c00,c10,u), x1=lerp(c01,c11,u);
  const y0=lerp(x0,x1,v);
  const c02=g(xi,yi,zi+1),c12=g(xi+1,yi,zi+1),c03=g(xi,yi+1,zi+1),c13=g(xi+1,yi+1,zi+1);
  const y1=lerp(lerp(c02,c12,u),lerp(c03,c13,u),v);
  return lerp(y0,y1,w);
}
function fractal2(x,y){
  let s=0, amp=0.5, freq=1;
  for(let i=0;i<4;i++){ s += noise2(x*freq,y*freq)*amp; amp*=0.5; freq*=2; }
  return s;
}
function fractal3(x,y,z){
  let s=0, amp=0.5, freq=1;
  for(let i=0;i<4;i++){ s += noise3(x*freq,y*freq,z*freq)*amp; amp*=0.5; freq*=2; }
  return s;
}

// ---------- Terrain helpers ----------
function surfaceType(H){
  if(H>=46) return 7;   // snow
  if(H>=37) return 3;   // stone
  if(H<=16) return 4;   // sand
  return 1;             // grass
}
function fillerType(H){
  if(H<=16) return 4;   // sand
  if(H>=37) return 3;   // stone
  return 2;             // dirt
}
function terrainHeightAt(wx,wz){
  const m=fractal2(wx*0.004,wz*0.004);
  const h=fractal2(wx*0.02,wz*0.02);
  return Math.floor(5 + m*m*58 + h*10);
}

// ---------- Chunk storage ----------
const chunks = new Map(); // key "cx,cz" -> {data:Uint8Array, mesh:Mesh}
function getBlock(wx,wy,wz){
  if(wy<0 || wy>=CH) return 0;
  const cx=Math.floor(wx/16), cz=Math.floor(wz/16);
  const ch = chunks.get(cx+','+cz);
  if(!ch) return 0;
  let lx=wx-cx*16, lz=wz-cz*16;
  if(lx<0||lx>=CW||lz<0||lz>=CD) return 0;
  return ch.data[idx(lx,wy,lz)];
}
function setBlock(wx,wy,wz,id){
  if(wy<0||wy>=CH) return;
  const cx=Math.floor(wx/16), cz=Math.floor(wz/16);
  let lx=wx-cx*16, lz=wz-cz*16;
  if(lx<0||lx>=CW||lz<0||lz>=CD) return;
  let ch = chunks.get(cx+','+cz);
  if(!ch){ ch={data:new Uint8Array(CHUNK_SIZE),mesh:null}; chunks.set(cx+','+cz,ch); }
  ch.data[idx(lx,wy,lz)] = id;
  rebuildChunk(cx,cz);
  if(lx===0) rebuildChunk(cx-1,cz);
  if(lx===CW-1) rebuildChunk(cx+1,cz);
  if(lz===0) rebuildChunk(cx,cz-1);
  if(lz===CD-1) rebuildChunk(cx,cz+1);
}

// ---------- Generation ----------
function generateChunk(cx,cz){
  const key=cx+','+cz;
  if(chunks.has(key)) return;
  const data=new Uint8Array(CHUNK_SIZE);
  for(let lx=0;lx<CW;lx++){
    for(let lz=0;lz<CD;lz++){
      const wx=cx*16+lx, wz=cz*16+lz;
      const m=fractal2(wx*0.004,wz*0.004);
      const h=fractal2(wx*0.02,wz*0.02);
      const H=Math.floor(5 + m*m*58 + h*10);
      for(let y=0;y<H;y++){
        let id=3; // stone
        if(y<=H-4) id=3;
        else if(y>=H-4 && y<=H-2) id=fillerType(H);
        if(y>=3 && y<=H-2 && noise3(wx*0.09,y*0.09,wz*0.09)>0.67) id=0;
        data[idx(lx,y,lz)]=id;
      }
      const sy=H-1;
      if(sy>=0 && sy<CH) data[idx(lx,sy,lz)]=surfaceType(H);
      if(surfaceType(H)===1 && hash(wx,wz)<0.02){
        placeTree(data,lx,sy,lz);
      }
    }
  }
  chunks.set(key,{data:data,mesh:null});
}
function placeTree(data,lx,sy,lz){
  const tt=sy+4;
  if(tt+4>=CH) return;
  if(lx<2||lx>13||lz<2||lz>13) return;
  for(let y=sy+1;y<=sy+4;y++) data[idx(lx,y,lz)]=5; // wood trunk
  // two 5x5 leaf layers
  for(const ly of [tt+1, tt+2]){
    if(ly<0||ly>=CH) continue;
    for(let dy=-2;dy<=2;dy++) for(let dz=-2;dz<=2;dz++){
      const ii=idx(lx+dy,ly,lz+dz);
      if(data[ii]===0) data[ii]=6;
    }
  }
  // 3x3 layer
  const ly3=tt+3;
  if(ly3>=0&&ly3<CH){
    for(let dy=-1;dy<=1;dy++) for(let dz=-1;dz<=1;dz++){
      const ii=idx(lx+dy,ly3,lz+dz);
      if(data[ii]===0) data[ii]=6;
    }
  }
  // 1 on top
  const ly4=tt+4;
  if(ly4>=0&&ly4<CH){
    const ii=idx(lx,ly4,lz);
    if(data[ii]===0) data[ii]=6;
  }
}

// ---------- Meshing ----------
const FACES = [
  { d:[-1,0,0], n:[-1,0,0], c:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
  { d:[ 1,0,0], n:[ 1,0,0], c:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]] },
  { d:[ 0,-1,0],n:[ 0,-1,0],c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { d:[ 0, 1,0],n:[ 0, 1,0],c:[[0,1,0],[1,1,0],[1,1,1],[0,1,1]] },
  { d:[ 0,0,-1],n:[ 0,0,-1],c:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]] },
  { d:[ 0,0, 1],n:[ 0,0, 1],c:[[0,0,1],[1,0,1],[1,0,0],[0,0,0]] },
];
let meshList = [];

function buildMesh(cx,cz){
  const ch = chunks.get(cx+','+cz);
  if(!ch) return null;
  const pos=[], norm=[], col=[];
  const ox=cx*16, oz=cz*16;
  for(let ly=0;ly<CH;ly++){
    for(let lz=0;lz<CD;lz++){
      for(let lx=0;lx<CW;lx++){
        const id = ch.data[idx(lx,ly,lz)];
        if(id===0) continue;
        const wx=ox+lx, wy=ly, wz=oz+lz;
        const rgb = blockRGB[id];
        for(const f of FACES){
          const nx=wx+f.d[0], ny=wy+f.d[1], nz=wz+f.d[2];
          if(getBlock(nx,ny,nz)!==0) continue;
          let light=0.8;
          if(f.n[1]===1) light=1.0;
          else if(f.n[1]===-1) light=0.55;
          for(const c of f.c){
            pos.push(wx+c[0], wy+c[1], wz+c[2]);
            norm.push(f.n[0],f.n[1],f.n[2]);
            col.push(rgb[0]*light, rgb[1]*light, rgb[2]*light);
          }
        }
      }
    }
  }
  if(pos.length===0) return null;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(norm,3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  const mesh = new THREE.Mesh(g, MATERIAL);
  mesh.position.set(0,0,0);
  return mesh;
}
function rebuildChunk(cx,cz){
  const ch = chunks.get(cx+','+cz);
  if(!ch) return;
  if(ch.mesh){
    scene.remove(ch.mesh);
    ch.mesh.geometry.dispose();
    const i=meshList.indexOf(ch.mesh);
    if(i>=0) meshList.splice(i,1);
  }
  const mesh = buildMesh(cx,cz);
  if(mesh){ ch.mesh=mesh; scene.add(mesh); meshList.push(mesh); }
  else ch.mesh=null;
}

// ---------- Scene setup ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 400);
const MATERIAL = new THREE.MeshLambertMaterial({ vertexColors:true });

const renderer = new THREE.WebGLRenderer({ antialias:false });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1, 2));
document.body.appendChild(renderer.domElement);
const canvas = renderer.domElement;

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.4, 1, 0.3); sun.normalize();
scene.add(sun);

// ---------- Outline ----------
const outlineGeo = new THREE.BoxGeometry(1.002,1.002,1.002);
const outline = new THREE.LineSegments(
  outlineGeo, new THREE.LineBasicMaterial({color:0x000000})
);
outline.visible = false;
scene.add(outline);

// ---------- Clouds ----------
const clouds = [];
for(let i=0;i<25;i++){
  const g = new THREE.BoxGeometry(16, 3, 10);
  const m = new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.9, flatShading:true});
  const mesh = new THREE.Mesh(g, m);
  mesh.userData = { relX: ((i%5)*22)-50, relZ: (Math.floor(i/5)*22)-44, spd: 1.5 + (i%3) };
  mesh.position.set(0,90,0);
  scene.add(mesh);
  clouds.push(mesh);
}

// ---------- Water ----------
const waterGeo = new THREE.PlaneGeometry(420,420);
const waterMat = new THREE.MeshLambertMaterial({color:0x0077be, transparent:true, opacity:0.72});
const water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);

// ---------- Player ----------
const player = {
  pos: new THREE.Vector3(),
  vel: new THREE.Vector3(),
  yaw: 0, pitch: 0, onGround: false
};
const spawnY = terrainHeightAt(8,8) + 2;
player.pos.set(8, spawnY, 8);

// ---------- Input ----------
const keys = {};
let selected = 0;
let locked = false;
let targetBlock = null;
let placeCell = null;

const overlay = document.getElementById('overlay');
overlay.addEventListener('click', ()=>{ canvas.requestPointerLock(); });

document.addEventListener('pointerlockchange', ()=>{
  locked = (document.pointerLockElement === canvas);
  overlay.style.display = locked ? 'none' : 'block';
});

document.addEventListener('mousemove', (e)=>{
  if(!locked) return;
  player.yaw   += e.movementX * 0.002;
  player.pitch -= e.movementY * 0.002;
  const lim = Math.PI/2 - 0.001;
  player.pitch = Math.max(-lim, Math.min(lim, player.pitch));
});

document.addEventListener('keydown', (e)=>{
  const k = e.code;
  if(k>='Digit1' && k<='Digit7'){ selected = parseInt(k.slice(5))-1; updateHotbar(); }
  keys[k] = true;
});
document.addEventListener('keyup', (e)=>{ keys[e.code] = false; });

window.addEventListener('wheel', (e)=>{
  if(!locked) return;
  selected = e.deltaY>0 ? (selected+1)%7 : (selected+6)%7;
  updateHotbar();
},{passive:true});

canvas.addEventListener('mousedown', (e)=>{
  if(!locked) return;
  if(e.button===0) breakBlock();
  else if(e.button===2) placeBlock();
});
document.addEventListener('contextmenu', (e)=>{ e.preventDefault(); });

window.addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ---------- Hotbar ----------
const hotbarEl = document.getElementById('hotbar');
HOTBAR.forEach((bid,i)=>{
  const d = document.createElement('div');
  d.className='slot'; d.dataset.i=i;
  d.style.background = '#'+('000000'+BLOCKS.find(b=>b.id===bid).color).slice(-6);
  d.innerHTML = '<span class="num">'+(i+1)+'</span>';
  hotbarEl.appendChild(d);
});
function updateHotbar(){
  document.querySelectorAll('.slot').forEach(el=>{
    el.classList.toggle('selected', parseInt(el.dataset.i)===selected);
  });
}

// ---------- Break / Place ----------
function breakBlock(){
  if(!targetBlock) return;
  const {x,y,z}=targetBlock;
  if(y===0) return; // unbreakable base
  setBlock(x,y,z,0);
}
function blocksOverlap(bx,by,bz){
  const px0=player.pos.x-0.3, px1=player.pos.x+0.3;
  const py0=player.pos.y,     py1=player.pos.y+1.8;
  const pz0=player.pos.z-0.3, pz1=player.pos.z+0.3;
  return (bx+1>px0 && bx<px1) && (by+1>py0 && by<py1) && (bz+1>pz0 && bz<pz1);
}
function placeBlock(){
  if(!placeCell) return;
  const {x,y,z}=placeCell;
  if(getBlock(x,y,z)!==0) return;
  if(blocksOverlap(x,y,z)) return;
  setBlock(x,y,z, HOTBAR[selected]);
}

// ---------- Collision ----------
function collides(px,py,pz){
  const minX=Math.floor(px-0.3), maxX=Math.floor(px+0.3);
  const minY=Math.floor(py),     maxY=Math.floor(py+1.8);
  const minZ=Math.floor(pz-0.3), maxZ=Math.floor(pz+0.3);
  for(let bx=minX;bx<=maxX;bx++)
    for(let by=minY;by<=maxY;by++)
      for(let bz=minZ;bz<=maxZ;bz++)
        if(getBlock(bx,by,bz)!==0) return true;
  return false;
}

// ---------- Physics ----------
function updatePlayer(dt){
  player.vel.y -= 25*dt;
  const fwd = new THREE.Vector3(-Math.sin(player.yaw),0,-Math.cos(player.yaw));
  const rt  = new THREE.Vector3(-Math.cos(player.yaw),0, Math.sin(player.yaw));
  let wish = new THREE.Vector3();
  if(keys['KeyW']) wish.add(fwd);
  if(keys['KeyS']) wish.sub(fwd);
  if(keys['KeyD']) wish.add(rt);
  if(keys['KeyA']) wish.sub(rt);
  if(wish.lengthSq()>0){ wish.normalize().multiplyScalar(5.5); }
  player.vel.x = wish.x; player.vel.z = wish.z;

  if(player.onGround && keys['Space']){ player.vel.y = 8.5; player.onGround=false; }

  // X
  player.pos.x += player.vel.x*dt;
  if(collides(player.pos.x,player.pos.y,player.pos.z)){ player.pos.x -= player.vel.x*dt; player.vel.x=0; }
  // Z
  player.pos.z += player.vel.z*dt;
  if(collides(player.pos.x,player.pos.y,player.pos.z)){ player.pos.z -= player.vel.z*dt; player.vel.z=0; }
  // Y
  player.onGround = false;
  player.pos.y += player.vel.y*dt;
  if(collides(player.pos.x,player.pos.y,player.pos.z)){
    player.pos.y -= player.vel.y*dt;
    if(player.vel.y<0) player.onGround=true;
    player.vel.y=0;
  }

  if(player.pos.y < -20){ player.pos.set(8,spawnY,8); player.vel.set(0,0,0); }
}

// ---------- Raycast ----------
const raycaster = new THREE.Raycaster();
function updateRaycast(){
  const dir = new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(player.pitch, player.yaw, 0, 'YXZ'));
  raycaster.set(camera.position, dir);
  raycaster.far = 6;
  const hits = raycaster.intersectObjects(meshList, false);
  if(hits.length>0){
    const p = hits[0].point, n = hits[0].face.normal;
    targetBlock = { x:Math.floor(p.x-n.x*0.5), y:Math.floor(p.y-n.y*0.5), z:Math.floor(p.z-n.z*0.5) };
    placeCell   = { x:Math.floor(p.x+n.x*0.5), y:Math.floor(p.y+n.y*0.5), z:Math.floor(p.z+n.z*0.5) };
  } else {
    targetBlock = null; placeCell = null;
  }
  if(targetBlock){
    outline.position.set(targetBlock.x+0.5, targetBlock.y+0.5, targetBlock.z+0.5);
    outline.visible = true;
  } else {
    outline.visible = false;
  }
}

// ---------- World streaming ----------
function updateWorld(){
  const pcx=Math.floor(player.pos.x/16), pcz=Math.floor(player.pos.z/16);

  // Generate blocks for chunks within 5 (max 4/frame)
  let cands=[];
  for(let dx=-5;dx<=5;dx++) for(let dz=-5;dz<=5;dz++){
    const cx=pcx+dx, cz=pcz+dz, key=cx+','+cz;
    if(!chunks.has(key)) cands.push({key,cx,cz,d:dx*dx+dz*dz});
  }
  cands.sort((a,b)=>a.d-b.d);
  let gc=0;
  for(const c of cands){ if(gc>=4) break; generateChunk(c.cx,c.cz); gc++; }

  // Build meshes for chunks within 4 whose 4 neighbors have data (max 2/frame)
  let bcands=[];
  for(let dx=-4;dx<=4;dx++) for(let dz=-4;dz<=4;dz++){
    const cx=pcx+dx, cz=pcz+dz, key=cx+','+cz;
    const ch=chunks.get(key);
    if(!ch || ch.mesh) continue;
    if(chunks.get((cx+1)+','+cz) && chunks.get((cx-1)+','+cz) &&
       chunks.get(cx+','+(cz+1)) && chunks.get(cx+','+(cz-1))){
      bcands.push({key,cx,cz,d:dx*dx+dz*dz});
    }
  }
  bcands.sort((a,b)=>a.d-b.d);
  let bld=0;
  for(const c of bcands){ if(bld>=2) break; rebuildChunk(c.cx,c.cz); bld++; }

  // Cleanup chunks farther than 7
  const dead=[];
  for(const key of Array.from(chunks.keys())){
    const [a,b]=key.split(',').map(Number);
    const dx=a-pcx, dz=b-pcz;
    if(dx*dx+dz*dz>49) dead.push({key,a,b});
  }
  for(const d of dead){
    const ch=chunks.get(d.key);
    if(ch.mesh){
      ch.mesh.geometry.dispose();
      scene.remove(ch.mesh);
      const i=meshList.indexOf(ch.mesh); if(i>=0) meshList.splice(i,1);
    }
    chunks.delete(d.key);
    // rebuild orthogonal neighbors so no interior faces leak
    rebuildChunk(d.a+1,d.b); rebuildChunk(d.a-1,d.b);
    rebuildChunk(d.a,d.b+1); rebuildChunk(d.a,d.b-1);
  }
}

// ---------- Prepopulate spawn area ----------
for(let dx=-2;dx<=2;dx++) for(let dz=-2;dz<=2;dz++) generateChunk(dx,dz);
for(let dx=-2;dx<=2;dx++) for(let dz=-2;dz<=2;dz++) rebuildChunk(dx,dz);

// ---------- Main loop ----------
let last = performance.now();
function animate(){
  requestAnimationFrame(animate);
  const now=performance.now();
  const dt=Math.min((now-last)/1000, 0.1);
  last=now;

  if(locked) updatePlayer(dt);
  updateWorld();

  camera.position.set(player.pos.x, player.pos.y+1.62, player.pos.z);
  camera.rotation.set(player.pitch, player.yaw, 0, 'YXZ');

  if(locked) updateRaycast();

  // clouds
  for(const c of clouds){
    c.userData.relX += c.userData.spd*dt;
    if(c.userData.relX>60) c.userData.relX-=120;
    if(c.userData.relX<-60) c.userData.relX+=120;
    c.position.x = player.pos.x + c.userData.relX;
    c.position.z = player.pos.z + c.userData.relZ;
  }
  water.position.x = player.pos.x;
  water.position.z = player.pos.z;

  renderer.render(scene, camera);
}
animate();

})();
</script>
</body>
</html>
```