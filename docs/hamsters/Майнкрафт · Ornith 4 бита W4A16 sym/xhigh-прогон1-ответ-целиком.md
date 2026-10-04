Let me build this Minecraft-style voxel game in a single HTML file. This is a complex task, but I have a detailed spec to follow. Let me carefully implement each part.

Let me plan out the structure:

1. HTML/CSS setup
   - Fullscreen canvas
   - Start overlay with title, controls, "Click to play"
   - Crosshair
   - Hotbar
   - Fog, sky color

2. Game logic in JavaScript:
   - Noise functions (value noise, fractal noise, 3D noise)
   - Chunk management (Map of chunks)
   - Block read/write helpers
   - Terrain generation
   - Meshing (BufferGeometry per chunk)
   - Player physics (gravity, collision, movement)
   - Raycasting for break/place
   - Controls (pointer lock, keyboard, mouse)
   - Hotbar selection
   - Sky, clouds, water
   - Main game loop

Let me write this carefully.

Key technical details:
- Three.js r128 loaded from CDN
- Blocks: 0 air, 1 grass 0x4caf50, 2 dirt 0x795548, 3 stone 0x9e9e9e, 4 sand 0xe7d9a8, 5 wood 0x8d6e63, 6 leaves 0x2e7d32, 7 snow 0xffffff
- Chunks: 16x16, 80 high
- Global Map key "cx,cz" -> { data: Uint8Array, mesh }
- Meshing: one BufferGeometry per chunk, vertex colors, fake lighting
- Shared MeshLambertMaterial

Let me write the code.

For the noise function:
- Integer-coordinate hash giving 0-1 using prime multipliers and xor-shifts
- Bilinear interpolation with smoothstep
- 4 octaves fractal noise
- 3D version for caves

Let me think about the hash function:

```javascript
function hash(x, y) {
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
```

For smoothstep: `t * t * (3 - 2*t)`

Bilinear interpolation:

```javascript
function noise2D(x, y) {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const xf = x - xi;
  const yf = y - yi;
  const u = smoothstep(xf);
  const v = smoothstep(yf);
  const a = hash(xi, yi);
  const b = hash(xi + 1, yi);
  const c = hash(xi, yi + 1);
  const d = hash(xi + 1, yi + 1);
  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}
```

Fractal noise:

```javascript
function fractal2D(x, y, octaves, scale) {
  let sum = 0;
  let amp = 1;
  let freq = scale;
  let max = 0;
  for (let i = 0; i < octaves; i++) {
    sum += amp * noise2D(x * freq, y * freq);
    max += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / max;
}
```

Wait, let me reconsider. The spec says "fractal at coords*0.004" for m, and "fractal at coords*0.02" for h. So fractal2D takes the coordinate and multiplies by scale internally? Or the caller passes scaled coords?

Let me define fractal2D to take (x, y) directly and do the octaves. Then the caller does fractal2D(x*0.004, y*0.004). Actually, let me make it flexible. Let me have the fractal function multiply internally by a frequency parameter.

Actually, let me just make fractal2D(x, y) where x, y are already scaled. Then caller passes coords*0.004.

Hmm, but the octaves need different frequencies. Let me define:

```javascript
function fractal2D(x, y, octaves) {
  let sum = 0;
  let amp = 1;
  let freq = 1;
  let max = 0;
  for (let i = 0; i < octaves; i++) {
    sum += amp * noise2D(x * freq, y * freq);
    max += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / max;
}
```

Then call fractal2D(coords.x * 0.004, coords.z * 0.004, 4).

For 3D caves noise, similar but 3D:

```javascript
function noise3D(x, y, z) {
  // ...
}
function fractal3D(x, y, z, octaves) {
  // ...
}
```

For 3D noise, I'll interpolate over the 8 corners of a unit cube.

Now the terrain generation:

Column height: 
- m = fractal at coords*0.004
- h = fractal at coords*0.02
- H = floor(5 + m*m*58 + h*10)

Column fill:
- y 0 = unbreakable stone
- below H-3: stone
- the 3 layers under the surface: dirt (sand if H ≤ 16, stone if H ≥ 37)
- surface: snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass

Let me think about the ordering. For a column from y=0 to y=H-1:
- y = 0: stone (unbreakable)
- y from 1 to H-4 (below H-3): stone
- y from H-3 to H-1: the 3 layers under surface
  - if H ≤ 16: sand
  - if H ≥ 37: stone
  - else: dirt
- surface (y = H-1): 
  - if H ≥ 46: snow
  - if H ≥ 37: stone
  - if H ≤ 16: sand
  - otherwise: grass

Wait, let me re-read: "the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37)". So the 3 layers beneath the surface are dirt normally, but sand if H≤16, stone if H≥37.

And surface is snow if H≥46, stone if H≥37, sand if H≤16, otherwise grass.

So for H between 17 and 36, surface is grass. For H between 37 and 45, surface is stone. Etc.

Let me structure the fill loop:

```javascript
for (let y = 0; y < H; y++) {
  if (y === 0) {
    data[y] = 3; // stone
  } else if (y < H - 3) {
    data[y] = 3; // stone
  } else if (y < H) {
    // 3 layers under surface
    if (H <= 16) data[y] = 4; // sand
    else if (H >= 37) data[y] = 3; // stone
    else data[y] = 2; // dirt
  }
}
// surface
if (H >= 46) data[H-1] = 7; // snow
else if (H >= 37) data[H-1] = 3; // stone
else if (H <= 16) data[H-1] = 4; // sand
else data[H-1] = 1; // grass
```

Wait, but there's a subtlety. The "3 layers under the surface" — if H is very small (like H=5), then H-3 = 2, so y from 1 to 1 would be stone, and y=2,3,4 would be... the surface layers. But H-1 = 4 is the surface. Let me handle edge cases. Actually with H = floor(5 + ...) minimum is 5, so H-1 minimum is 4. That's fine.

But wait, we need to be careful: the "3 layers under surface" assumes H >= 3. Since min H is 5, that's fine. But what if H-3 <= 0? H=5, H-3=2, so y=1 is stone (below H-3), y=2,3,4 are surface layers. Good.

Actually, let me reconsider. What if H is small such that H-3 <= 0? With min H=5, H-3=2 > 0. Good.

Hmm, but actually there might be an issue where the surface layers and below overlap. Let me just be careful with the conditions. Let me use:

```javascript
for (let y = 0; y < H; y++) {
  if (y < H - 3) {
    data[y] = 3; // stone below
  } else {
    // surface layers (y >= H-3 and y < H)
    if (H <= 16) data[y] = 4;
    else if (H >= 37) data[y] = 3;
    else data[y] = 2;
  }
}
// surface
if (H >= 46) data[H-1] = 7;
else if (H >= 37) data[H-1] = 3;
else if (H <= 16) data[H-1] = 4;
else data[H-1] = 1;
```

This handles y=0 as stone too since 0 < H-3 for H>=5 (H-3>=2). Good.

Caves: for y between 3 and H-2, if 3D noise at position*0.09 exceeds 0.67, set air.

```javascript
for (let y = 3; y <= H - 2; y++) {
  const cave = fractal3D(x*0.09, y*0.09, z*0.09, 3);
  if (cave > 0.67) data[y] = 0;
}
```

Trees: on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood up, leaves as 5x5 layer twice, then 3x3, then 1 on top (only into air).

Let me think about tree placement. The tree is placed at the surface. Surface is at y = H-1. Trunk goes up 4 blocks, so from y=H to y=H+3. Leaves layers above.

"the trunk fits inside the chunk" — meaning H+4 <= 80? Or the tree doesn't exceed chunk height. Let me check: trunk 4 blocks up from surface. If surface is at H-1, trunk occupies H to H+3, top of trunk at H+3. Then leaves start at H+4. For the tree to fit, we need H+something <= 79. Let me just check that the top leaves don't exceed 79.

Per-column hash: hash(x, z) < 0.02.

Let me write tree generation:

```javascript
function placeTree(data, x, z, baseY) {
  // baseY is the surface y (H-1), trunk starts at baseY+1
  const trunkHeight = 4;
  for (let i = 1; i <= trunkHeight; i++) {
    const ty = baseY + i;
    if (ty < 80) data[ty] = 5; // wood
  }
  // leaves
  const leafStart = baseY + trunkHeight; // H-1+4 = H+3
  // 5x5 layer twice
  for (let ly = 0; ly < 2; ly++) {
    const layerY = leafStart + 1 + ly;
    addLeafLayer(data, x, z, layerY, 2); // half width 2
  }
  // 3x3
  const layerY3 = leafStart + 3;
  addLeafLayer(data, x, z, layerY3, 1);
  // 1 on top
  const topY = leafStart + 4;
  if (topY < 80) data[topY] = 6;
}
```

Hmm, let me reconsider the leaf structure. "leaves as a 5x5 layer twice, then 3x3, then 1 on top". 

5x5 layer twice: two layers of 5x5 leaves.
3x3 layer: one layer of 3x3 leaves.
1 on top: one block.

Let me place them. The 5x5 layers centered on the trunk. Half-size 2 (so -2 to +2).

Let me define addLeafLayer that fills a square of given half-size at a y level:

```javascript
function addLeafLayer(data, cx, cz, y, half) {
  for (let dx = -half; dx <= half; dx++) {
    for (let dz = -half; dz <= half; dz++) {
      const lx = cx + dx;
      const lz = cz + dz;
      const lxLocal = lx - chunkCx*16;
      const lzLocal = lz - chunkCz*16;
      if (lxLocal < 0 || lxLocal >= 16 || lzLocal < 0 || lzLocal >= 16) continue; // only into chunk
      if (y < 80 && data[lxLocal + lzLocal*16] !== 0) {
        data[lxLocal + lzLocal*16] = 6;
      }
    }
  }
}
```

Wait, but the tree is placed within a chunk, and I need to know the chunk's cx, cz. Let me pass those in. Also "only into air" means only replace if currently air.

Let me reconsider the whole chunk generation. When generating a chunk at (cx, cz), I iterate over all 16x16x80 positions. For each column (x, z) in the chunk, I compute terrain height H using world coords (cx*16 + x, cz*16 + z), fill the column, add caves, and maybe a tree.

But the tree "fits inside the chunk" — the leaf layers extend ±2 from the trunk. If the trunk is near the chunk edge, leaves would go outside. The spec says "and the trunk fits inside the chunk". Hmm, maybe it means the trunk position isn't on the border? Or maybe it just checks height. Let me interpret "trunk fits inside the chunk" as: the column is not on the chunk boundary (so leaves stay inside), OR simply that the tree height fits. 

Actually, re-reading: "when a per-column hash < 0.02 and the trunk fits inside the chunk". I think this means the tree can be placed if the trunk column is fully within the chunk (not on the edge), so all leaf blocks stay within the chunk. Let me require the column to be at least 2 blocks from each edge. Actually, to be safe, let me check that the leaf layers won't overflow. Since leaves extend ±2, I need x in [2, 13] and z in [2, 13]. And height: H + 4 + ... let me just check the top leaves fit (< 80).

Actually, let me simplify: require the column x,z (local) to be in range [2, 13] both axes, and check H + 8 < 80 for the top leaf. Hmm, but that might be overly restrictive. Let me just check local x,z in [2,13] and the top of tree (baseY + 4 + 4 = H-1+8 = H+7) < 80, i.e., H < 73. Actually leaves: trunk 4 (H to H+3), then 2 layers of 5x5 (H+4, H+5), then 3x3 (H+6), then 1 (H+7). So top at H+7. Need H+7 < 80, H < 73.

Let me just check `H + 8 <= 80`.

Now, the meshing. For each chunk, build one BufferGeometry. Loop all non-air blocks, for each of 6 directions check neighbor via global read helper; if air, add face.

Let me define the 6 directions:
- +x, -x
- +y, -y
- +z, -z

For each direction, the face has 4 vertices and a normal. The fake lighting depends on the face: top (normal +y) = 1.0, bottom (normal -y) = 0.55, sides = 0.8.

Let me define the face vertices. For a block at (bx, by, bz), the block spans [bx, bx+1] x [by, by+1] x [bz, bz+1].

For +x face (right, normal (1,0,0)): the face is at x = bx+1. Vertices:
(bx+1, by, bz), (bx+1, by, bz+1), (bx+1, by+1, bz+1), (bx+1, by+1, bz)
Normal (1,0,0).

I need to be careful about winding order for front-facing. With MeshLambertMaterial and default side (double?), winding doesn't matter much, but let me use double side to be safe. Actually, let me use TWO_SIDED. In r128, MeshLambertMaterial has side property: FrontSide, BackSide, DoubleSide. Default is FrontSide. Let me set side: THREE.DoubleSide to avoid culling issues. Actually for proper lighting, front side is better, but double side is safer. Hmm, but double side with the lighting might look off. Let me think.

Actually, for a voxel game, standard approach uses FrontSide with correct winding. But to be safe and avoid backface issues, I could use DoubleSide. Let me use DoubleSide to avoid any culling problems. The lighting will still work per-face.

Wait, but with DoubleSide, each face is lit from both sides which could look weird for interior faces. But since we only render faces adjacent to air, and use fake lighting based on normal direction, it should be fine. Let me go with DoubleSide for robustness. Actually, let me reconsider — the fake lighting multiplies color by direction factor. With DoubleSide the normals are used for lighting regardless of facing. Top faces get factor 1.0, etc. This gives the voxel look. Good.

Hmm, actually there's a subtlety. If I use DoubleSide and the geometry has consistent normals, lighting is fine. Let me just make sure normals are set correctly per face.

Let me define the face data:

```javascript
const faces = [
  { dir: [1, 0, 0], normal: [1, 0, 0], shade: 0.8, verts: [...] },
  ...
];
```

Let me define each face's 4 vertices (CCW when viewed from outside) and normal.

For a block corner at (x, y, z):

+x face (normal (1,0,0)), at X=x+1:
v0 = (x+1, y, z)
v1 = (x+1, y, z+1)
v2 = (x+1, y+1, z+1)
v3 = (x+1, y+1, z)
Triangles: (v0,v1,v2) and (v0,v2,v3). Order for CCW from +x looking toward -x... let me not worry too much, use DoubleSide.

Actually let me just define all 6 faces with their vertices and use consistent ordering. Let me write a helper.

Let me define offsets. For each face, I'll specify the normal and 4 corner offsets relative to block origin:

```javascript
const FACES = [
  // +X
  { n: [1,0,0], s: 0.8, v: [[1,0,0],[1,0,1],[1,1,1],[1,1,0]] },
  // -X
  { n: [-1,0,0], s: 0.8, v: [[0,0,1],[0,0,0],[0,1,0],[0,1,1]] },
  // +Y (top)
  { n: [0,1,0], s: 1.0, v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  // -Y (bottom)
  { n: [0,-1,0], s: 0.55, v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  // +Z
  { n: [0,0,1], s: 0.8, v: [[1,0,1],[0,0,1],[0,1,1],[1,1,1]] },
  // -Z
  { n: [0,0,-1], s: 0.8, v: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]] },
];
```

I need to verify winding so normals point outward, but with DoubleSide it doesn't matter for rendering. However, for the wireframe outline I'll use a separate BoxHelper or LineSegments.

Actually, for the crosshair target outline, I'll create a Box3 for the target block and add a wireframe. Let me use a THREE.LineSegments with EdgesGeometry(BoxGeometry(1,1,1)).

Now the raycasting. Each frame, raycast from camera center (near clip) through center of screen (0.5, 0.5) against chunk meshes, max distance 6. Use THREE.Raycaster.

```javascript
raycaster.set(camera.position, cameraDirection);
raycaster.far = 6; // hmm, need to set far properly
const hits = raycaster.intersectObjects(chunkMeshes, false);
```

Wait, Raycaster far is relative to the ray origin. Let me set it appropriately. Actually Raycaster has a `far` property but it's often set via setFar. Let me just intersect and check distance manually.

From hit point p and face normal n:
- break target = floor(p - n*0.5), per component
- place cell = floor(p + n*0.5), per component

The hit point is in world coordinates. floor of (p - n*0.5) gives the block being hit. floor of (p + n*0.5) gives the adjacent block behind the face (where to place).

Let me implement.

Now player physics:
- PerspectiveCamera fov 75, far 400
- rotation order YXZ, yaw/pitch
- Player box: half-width 0.3, height 1.8, eye 1.62
- Spawn above terrain at x=8, z=8
- Gravity 25, jump velocity 8.5, WASD 5.5 m/s relative to yaw
- Axis-separated collision
- Fall below y-20 teleport to spawn

Collision: player box from (x-hw, y, z-hw) to (x+hw, y+h, z+hw) where y is feet position. Check all non-air blocks overlapping this box; if overlap, push out along the axis moved.

Standard AABB vs voxel collision: for each axis, move the player, then check if the new box intersects any solid block; if so, revert that axis movement (or snap).

Let me implement axis-separated collision:

```javascript
function collide(dx, dy, dz) {
  // move player by (dx,dy,dz)
  // check collisions per axis
}
```

Actually, the typical approach:
1. Move along X: newX = x + dx. Check collision with new X. If collide, newX = x.
2. Move along Y: newY = y + dy. Check. If collide, newY = y, set onGround if falling.
3. Move along Z similarly.

Collision check: does player AABB at (newX, y, z) overlap any solid voxel?

Player AABB: [x-hw, x+hw] x [y, y+h] x [z-hw, z+hw].

For a voxel at (vx, vy, vz) occupying [vx, vx+1] x [vy, vy+1] x [vz, vz+1], overlap if:
x-hw < vx+1 && x+hw > vx && y < vy+1 && y+h > vy && z-hw < vz+1 && z+hw > vz.

To check efficiently, I only need to check voxels near the player. Let me compute the range of voxels to check.

Let me write a function isSolidAt(vx, vy, vz) that returns true if block is non-air (and vy in range). Uses global read helper.

For collision, iterate over voxels in the bounding box of the player AABB:

```javascript
function collides(px, py, pz) {
  const hw = 0.3, h = 1.8;
  const minX = Math.floor(px - hw), maxX = Math.floor(px + hw);
  const minY = Math.floor(py), maxY = Math.floor(py + h);
  const minZ = Math.floor(pz - hw), maxZ = Math.floor(pz + hw);
  for (let vx = minX; vx <= maxX; vx++)
    for (let vy = minY; vy <= maxY; vy++)
      for (let vz = minZ; vz <= maxZ; vz++) {
        if (getBlock(vx, vy, vz) !== 0) {
          // AABB overlap check
          if (px - hw < vx + 1 && px + hw > vx &&
              py < vy + 1 && py + h > vy &&
              pz - hw < vz + 1 && pz + hw > vz) {
            return true;
          }
        }
      }
  return false;
}
```

Then in movement:
```javascript
// X
if (!collides(nx, y, z)) x = nx;
// Y
if (!collides(x, ny, z)) {
  y = ny;
} else {
  if (vy < 0) onGround = true;
  vy = 0;
}
// Z
if (!collides(x, y, nz)) z = nz;
```

Wait, but for Y collision, I need to distinguish landing vs hitting head. If vy < 0 (moving down) and collision, we're on ground. If vy > 0 (jumping) and collision, hit head.

Let me refine:
```javascript
// vertical
ny = y + vy * dt;
if (!collides(x, ny, z)) {
  y = ny;
} else {
  if (vy < 0) onGround = true;
  vy = 0;
}
```

But there's an issue: if moving fast, we might tunnel through. With gravity 25 and dt ~ 1/60, step ~ 0.4, and block size 1, should be okay. Player box height 1.8, half-width 0.3. Let me use fixed timestep or cap velocity. Should be fine for this.

Also, spawning: spawn above terrain at x=8, z=8. I need to find terrain height there. Let me compute after world generation. Actually, I'll spawn and then let gravity bring them down, or compute the height. Let me compute the surface height at (8, 8) and spawn a few blocks above.

Let me handle spawn: after the first chunk generation, getBlock(8, y, 8) to find surface. Or just spawn at y=60 and fall. But better to spawn on ground. Let me find the highest non-air block at (8,8) and spawn feet just above.

Actually, let me spawn at y = some computed height. Let me search downward from y=79 for the first solid block at (8,8), then set player.y = that + 1 + small.

Let me now think about the chunk generation and meshing loop.

Each frame:
1. Generate block data for all chunks within 5 chunks of player (max 4 per frame).
2. Build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame).
3. For chunks farther than 7, remove mesh, dispose geometry, delete entry.

"within 5 chunks of the player" — playerChunk = (floor(player.x/16), floor(player.z/16)). Chunks with |cx - playerCX| <= 5 and |cz - playerCZ| <= 5. That's 11x11 = 121 chunks. Generate max 4 per frame.

"chunks within 4 chunks" — |cx - playerCX| <= 4 and |cz - playerCZ| <= 4, 9x9 = 81 chunks. Build mesh if 4 neighbors have data. Neighbors: (cx±1, cz), (cx, cz±1)? Or all 4 diagonal? "whose 4 neighbors already have data" — probably the 4 orthogonal neighbors (up, down, left, right). Let me use the 4 orthogonal: (cx+1,cz),(cx-1,cz),(cx,cz+1),(cx,cz-1).

"for chunks farther than 7" — |cx - playerCX| > 7 or |cz - playerCZ| > 7. Remove.

Let me maintain the Map and process.

Let me structure:

```javascript
const chunks = new Map(); // key -> { data: Uint8Array, mesh }

function getOrCreateChunk(cx, cz) {
  const key = cx + "," + cz;
  if (!chunks.has(key)) {
    const data = new Uint8Array(16*16*80);
    generateChunkData(cx, cz, data);
    chunks.set(key, { data: data, mesh: null });
  }
  return chunks.get(key);
}
```

Global read helper:
```javascript
function getBlock(x, y, z) {
  if (y < 0 || y > 79) return 0;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const key = cx + "," + cz;
  const chunk = chunks.get(key);
  if (!chunk) return 0;
  const lx = x - cx*16;
  const lz = z - cz*16;
  return chunk.data[lx + lz*16 + y];
}
```

Wait, index = lx + lz*16 + y. Let me confirm: 16*16*80 array, layout [x][z][y]? Let me use lx + lz*16 + y*16*16. Hmm, need consistency. Let me define index = (y*16 + lz)*16 + lx = y*256 + lz*16 + lx. Any consistent layout works. Let me use lx + lz*16 + y*256.

Actually simpler: index = y * 256 + lz * 16 + lx. Let me use that.

Write helper:
```javascript
function setBlock(x, y, z, id) {
  if (y < 0 || y > 79) return;
  const cx = Math.floor(x/16), cz = Math.floor(z/16);
  const key = cx+","+cz;
  const chunk = chunks.get(key);
  if (!chunk) return;
  const lx = x - cx*16, lz = z - cz*16;
  chunk.data[y*256 + lz*16 + lx] = id;
}
```

Now generation. generateChunkData(cx, cz, data):

```javascript
function generateChunkData(cx, cz, data) {
  for (let lx = 0; lx < 16; lx++) {
    for (let lz = 0; lz < 16; lz++) {
      const wx = cx*16 + lx;
      const wz = cz*16 + lz;
      const m = fractal2D(wx*0.004, wz*0.004, 4);
      const h = fractal2D(wx*0.02, wz*0.02, 4);
      const H = Math.floor(5 + m*m*58 + h*10);
      // fill
      for (let y = 0; y < H; y++) {
        if (y < H - 3) {
          data[y*256 + lz*16 + lx] = 3;
        } else {
          if (H <= 16) data[y*256 + lz*16 + lx] = 4;
          else if (H >= 37) data[y*256 + lz*16 + lx] = 3;
          else data[y*256 + lz*16 + lx] = 2;
        }
      }
      // surface
      const si = (H-1)*256 + lz*16 + lx;
      if (H >= 46) data[si] = 7;
      else if (H >= 37) data[si] = 3;
      else if (H <= 16) data[si] = 4;
      else data[si] = 1;
      // caves
      for (let y = 3; y <= H - 2; y++) {
        if (fractal3D(wx*0.09, y*0.09, wz*0.09, 3) > 0.67) {
          data[y*256 + lz*16 + lx] = 0;
        }
      }
      // trees
      if (data[(H-1)*256 + lz*16 + lx] === 1 && hash(wx, wz) < 0.02) {
        if (lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 && H + 8 <= 80) {
          // place tree
          for (let i = 1; i <= 4; i++) {
            const ty = H - 1 + i;
            data[ty*256 + lz*16 + lx] = 5;
          }
          // 5x5 twice
          for (let ly = 0; ly < 2; ly++) {
            const layerY = H + 3 + ly; // H+4, H+5
            for (let dx = -2; dx <= 2; dx++)
              for (let dz = -2; dz <= 2; dz++) {
                const ty = layerY*256 + (lz+dz)*16 + (lx+dx);
                if (data[ty] === 0) data[ty] = 6;
              }
          }
          // 3x3
          const layerY3 = H + 5;
          for (let dx = -1; dx <= 1; dx++)
            for (let dz = -1; dz <= 1; dz++) {
              const ty = (layerY3)*256 + (lz+dz)*16 + (lx+dx);
              if (data[ty] === 0) data[ty] = 6;
            }
          // 1 on top
          const topY = H + 6;
          data[topY*256 + lz*16 + lx] = 6;
        }
      }
    }
  }
}
```

Wait, let me recompute leaf heights. Trunk: surface at H-1, trunk blocks at H, H+1, H+2, H+3 (i from 1 to 4: H-1+i). So trunk top at H+3.

Leaves: "5x5 layer twice" at H+4, H+5. "3x3" at H+6. "1 on top" at H+7.

Let me fix:
- 5x5 layer 1: H+4
- 5x5 layer 2: H+5
- 3x3: H+6
- 1 on top: H+7

Let me rewrite:
```javascript
// 5x5 twice
for (let ly = 0; ly < 2; ly++) {
  const layerY = H + 4 + ly; // H+4, H+5
  ...
}
// 3x3
const layerY3 = H + 6;
...
// 1 on top
const topY = H + 7;
```

Need H+7 < 80, so H < 73. My check H+8 <= 80 means H <= 72, so H+7 <= 79. Good.

Now meshing. buildMesh(chunk):

```javascript
function buildMesh(cx, cz) {
  const key = cx+","+cz;
  const chunk = chunks.get(key);
  if (!chunk || !chunk.data) return;
  const data = chunk.data;
  const positions = [];
  const normals = [];
  const colors = [];
  const blockColors = [null, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
  
  for (let y = 0; y < 80; y++) {
    for (let lz = 0; lz < 16; lz++) {
      for (let lx = 0; lx < 16; lx++) {
        const id = data[y*256 + lz*16 + lx];
        if (id === 0) continue;
        const wx = cx*16 + lx;
        const wz = cz*16 + lz;
        const col = blockColors[id];
        const cr = (col >> 16) & 255;
        const cg = (col >> 8) & 255;
        const cb = col & 255;
        for (const f of FACES) {
          const nx = wx + f.n[0];
          const ny = y + f.n[1];
          const nz = wz + f.n[2];
          if (getBlock(nx, ny, nz) === 0) {
            // add face
            const shade = f.s;
            for (const vt of f.v) {
              positions.push(wx + vt[0], y + vt[1], wz + vt[2]);
              normals.push(f.n[0], f.n[1], f.n[2]);
              colors.push((cr*shade)/255, (cg*shade)/255, (cb*shade)/255);
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
  const mesh = new THREE.Mesh(geo, sharedMaterial);
  mesh.position.set(cx*16, 0, cz*16);
  chunk.mesh = mesh;
  chunk.geo = geo;
  scene.add(mesh);
  chunkMeshes.push(mesh);
}
```

Wait, "keep the mesh at the origin" — the spec says "Use world coordinates for vertices and keep the mesh at the origin." So the mesh position should be (0,0,0) and vertices in world coordinates. Let me set mesh.position to (0,0,0) and use world coords in vertices. That simplifies raycasting since world coords = mesh-local coords.

Let me set mesh.position.set(0,0,0).

Now, the shared material:
```javascript
const sharedMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

Clouds: 25 flat white transparent boxes at height ~90, drifting and wrapping around player.

```javascript
const clouds = [];
for (let i = 0; i < 25; i++) {
  const w = 5 + Math.random()*10; // wait, no Math.random allowed?
  ...
}
```

Hmm, the spec says "deterministic, no Math.random" for terrain. For clouds, it's probably fine to use Math.random for initial placement since it's not terrain. But to be safe, let me use a deterministic pseudo-random for cloud placement too. Actually, the "no Math.random" rule is specifically about terrain determinism. Clouds can use random initial positions. But let me just use deterministic values to be safe and clean. Actually, let me use a hash-based pseudo-random for cloud positions.

Let me generate clouds with deterministic positions spread out.

Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame.

```javascript
const waterGeo = new THREE.PlaneGeometry(500, 500);
const waterMat = new THREE.MeshLambertMaterial({ color: 0x2b7fff, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
const water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);
```

Re-center each frame: water.position.x = player.x, water.position.z = player.z.

Now controls. Pointer lock. On clicking start overlay, requestPointerLock. Mouse move updates yaw/pitch when locked. Clicks (mousedown) break/place when locked. Suppress context menu.

```javascript
document.addEventListener('contextmenu', e => e.preventDefault());
canvas.addEventListener('click', () => {
  if (!pointerLocked) canvas.requestPointerLock();
});
document.addEventListener('mousemove', e => {
  if (!pointerLocked) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  pitch = Math.max(-Math.PI/2 + 0.01, Math.min(Math.PI/2 - 0.01, pitch));
});
```

Wait, sensitivity ~0.002. Standard: yaw -= movementX * sensitivity. Let me use 0.002.

Pointer lock change:
```javascript
document.addEventListener('pointerlockchange', () => {
  pointerLocked = (document.pointerLockElement === canvas);
});
```

When pointer lock released, show overlay again.

Mouse buttons:
```javascript
canvas.addEventListener('mousedown', e => {
  if (!pointerLocked) return;
  if (e.button === 0) { // left - break
    if (targetBlock) {
      const [bx,by,bz] = targetBlock;
      if (by !== 0) {
        setBlock(bx, by, bz, 0);
        rebuildChunk(bx, bz);
      }
    }
  } else if (e.button === 2) { // right - place
    if (placeCell) {
      const [px,py,pz] = placeCell;
      if (getBlock(px,py,pz) === 0 && !playerOverlaps(px,py,pz)) {
        setBlock(px,py,pz, selectedBlock);
        rebuildChunk(px, pz);
      }
    }
  }
});
```

rebuildChunk(x, z): rebuild the chunk containing (x,z), and neighbor chunks if on border.

```javascript
function rebuildChunk(x, z) {
  const cx = Math.floor(x/16), cz = Math.floor(z/16);
  rebuildChunkMesh(cx, cz);
  // check borders
  const lx = x - cx*16, lz = z - cz*16;
  if (lx === 0) rebuildChunkMesh(cx-1, cz);
  if (lx === 15) rebuildChunkMesh(cx+1, cz);
  if (lz === 0) rebuildChunkMesh(cx, cz-1);
  if (lz === 15) rebuildChunkMesh(cx, cz+1);
}
```

rebuildChunkMesh(cx, cz): dispose old geometry/mesh, build new.

```javascript
function rebuildChunkMesh(cx, cz) {
  const key = cx+","+cz;
  const chunk = chunks.get(key);
  if (!chunk) return;
  if (chunk.mesh) {
    const idx = chunkMeshes.indexOf(chunk.mesh);
    if (idx >= 0) chunkMeshes.splice(idx, 1);
    scene.remove(chunk.mesh);
    if (chunk.geo) chunk.geo.dispose();
    chunk.mesh = null;
    chunk.geo = null;
  }
  buildMesh(cx, cz);
}
```

Now the hotbar. 7 slots. Selected with keys 1-7 or mouse wheel.

```javascript
let selectedBlock = 1;
const hotbarBlocks = [1,2,3,4,5,6,7];
document.addEventListener('keydown', e => {
  if (e.key >= '1' && e.key <= '7') {
    selectedBlock = parseInt(e.key);
    updateHotbar();
  }
});
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  selectedBlock += e.deltaY > 0 ? 1 : -1;
  selectedBlock = ((selectedBlock - 1) % 7 + 7) % 7 + 1;
  updateHotbar();
}, { passive: false });
```

updateHotbar(): update the border highlight.

Now the main loop:

```javascript
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  let dt = (now - lastTime) / 1000;
  lastTime = now;
  dt = Math.min(dt, 0.05);
  
  if (pointerLocked) {
    updatePlayer(dt);
  }
  updateWorldGeneration();
  updateClouds();
  updateWater();
  updateTargetOutline();
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
}
```

Player update:
```javascript
function updatePlayer(dt) {
  // movement input
  let mx = 0, mz = 0;
  if (keys['w']) mz -= 1;
  if (keys['s']) mz += 1;
  if (keys['a']) mx -= 1;
  if (keys['d']) mx += 1;
  // normalize
  const len = Math.hypot(mx, mz);
  if (len > 0) { mx /= len; mz /= len; }
  // relative to yaw
  const sinY = Math.sin(yaw), cosY = Math.cos(yaw);
  const wx = mx * cosY + mz * sinY;
  const wz = mz * cosY - mx * sinY; // need to check
  // velocity
  player.vx = wx * 5.5;
  player.vz = wz * 5.5;
  // gravity
  player.vy -= 25 * dt;
  // jump
  if (keys[' '] && onGround) { player.vy = 8.5; onGround = false; }
  // integrate with collision
  ...
  // fall teleport
  if (player.y < cameraY - 20) respawn();
}
```

Let me be careful with the movement direction. Camera looks along yaw. With rotation order YXZ:
- yaw rotates around Y (Y axis)
- pitch rotates around X

Standard FPS: forward vector = (sin(yaw), sin(pitch)... wait let me think.

Actually, let me define: yaw is rotation around Y axis. When yaw=0, looking along... let me define forward horizontal = (sin(yaw), 0, cos(yaw))? Or (-sin, 0, cos)? Depends on convention.

Let me think about Three.js. Camera default looks along -Z. If I apply rotateY(yaw), then rotateX(pitch), with order YXZ...

Let me use Euler order 'YXZ'. camera.rotation.set(pitch, yaw, 0, 'YXZ').

Forward vector: For a camera with rotation (pitch around X, yaw around Y):
- Without pitch (pitch=0), yaw=0: camera looks along -Z.
- Forward horizontal direction after yaw: rotating -Z by yaw around Y. -Z rotated by yaw: (sin(yaw)*... let me compute. Rotation around Y by angle θ maps (x,y,z) to (x cosθ + z sinθ, y, -x sinθ + z cosθ). Starting direction -Z = (0,0,-1). After rotation: (sinθ*(-1)... wait: x' = 0*cosθ + (-1)*sinθ = -sinθ, z' = -0*sinθ + (-1)*cosθ = -cosθ. So forward = (-sinθ, 0, -cosθ) at pitch=0.

Hmm, that's the forward direction. So moving "forward" (W) should move in direction (-sin(yaw), 0, -cos(yaw)).

Let me define:
- forward = (sin(yaw), 0, cos(yaw))? No.

Let me just carefully derive. Actually, let me use the approach where I compute the forward vector from camera.rotation.

camera.getWorldDirection(vec) gives the forward direction. But that includes pitch. For horizontal movement, I want the horizontal projection.

Let me compute forward horizontal:
```javascript
const forward = new THREE.Vector3(
  Math.sin(yaw) * Math.cos(pitch)... 
);
```

Hmm, let me think more carefully. Let me define yaw and pitch such that:
- Horizontal forward (when pitch=0): (sin(yaw), 0, cos(yaw))? 

Actually let me just derive from the Euler. With order YXZ and Euler (yaw, pitch, 0):
Rotation matrix R = Ry(yaw) * Rx(pitch) * Rz(0).

The camera's local -Z axis (forward) transformed by R:
R * (0, 0, -1).

Ry(yaw) = [[cos, 0, sin],[0,1,0],[-sin,0,cos]]
Rx(pitch) = [[1,0,0],[0,cp,-sp],[0,sp,cp]]

Rx(pitch) * (0,0,-1) = (0, sp, -cp) [since row2: 0*0 + cp*0 + (-sp)*(-1)=sp... let me compute:
Rx * (0,0,-1):
- x: 1*0 + 0*0 + 0*(-1) = 0
- y: 0*0 + cp*0 + (-sp)*(-1) = sp
- z: 0*0 + sp*0 + cp*(-1) = -cp
So (0, sp, -cp).

Then Ry(yaw) * (0, sp, -cp):
Ry = [[cos,0,sin],[0,1,0],[-sin,0,cos]]
- x: cos*0 + 0*sp + sin*(-cp) = -sin*cp
- y: 0 + sp + 0 = sp
- z: -sin*0 + 0*sp + cos*(-cp) = -cos*cp
So forward = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)).

At pitch=0: forward = (-sin(yaw), 0, -cos(yaw)). OK matches earlier.

So horizontal forward = (-sin(yaw), 0, -cos(yaw)). Moving forward moves in this direction.

Let me define movement:
```javascript
const sinY = Math.sin(yaw), cosY = Math.cos(yaw);
// forward horizontal
const fx = -sinY, fz = -cosY;
// right = forward rotated -90 around Y = (-cosY, 0, sinY)? Let me compute. Right vector is camera's +X axis.
```

Actually, let me compute the right vector too. Camera's +X axis transformed by R:
R * (1, 0, 0):
Rx*(1,0,0) = (1, 0, 0).
Ry*(1,0,0) = (cos, 0, -sin).
So right = (cos(yaw), 0, -sin(yaw)).

So:
- forward horizontal: (fx, fz) = (-sinY, -cosY)
- right: (rx, rz) = (cosY, -sinY)

Movement with W (forward), D (right):
moveX = fx * wInput + rx * dInput
moveZ = fz * wInput + rz * dInput

Where wInput is forward amount (positive = forward), dInput is right amount.

With keys: W -> forward (+1), S -> backward (-1), D -> right (+1), A -> left (-1).

```javascript
let fwd = 0, right = 0;
if (keys['w']) fwd += 1;
if (keys['s']) fwd -= 1;
if (keys['d']) right += 1;
if (keys['a']) right -= 1;
// normalize
const len = Math.hypot(fwd, right);
if (len > 0) { fwd /= len; right /= len; }
const speed = 5.5;
const mvx = (fx * fwd + rx * right) * speed;
const mvz = (fz * fwd + rz * right) * speed;
```

OK. Now collision integration. Let me do axis-separated:

```javascript
// X
let nx = player.x + mvx * dt;
if (!collides(nx, player.y, player.z)) player.x = nx;
// Z
let nz = player.z + mvz * dt;
if (!collides(player.x, player.y, nz)) player.z = nz;
// Y
player.vy -= 25 * dt;
let ny = player.y + player.vy * dt;
if (!collides(player.x, ny, player.z)) {
  player.y = ny;
  onGround = false;
} else {
  if (player.vy < 0) onGround = true;
  player.vy = 0;
}
```

Wait, but gravity should apply even when on ground (it's balanced by ground). That's fine, vy gets reset to 0 on collision. When on ground and pressing jump, vy = 8.5.

Actually, let me apply gravity before the Y integration:
```javascript
player.vy -= 25 * dt;
```

Then integrate Y. Good.

But there's a subtle bug: if onGround and gravity makes vy negative, then we try to move down, collision detected, vy reset to 0, onGround stays true. Good.

Eye height: camera at player.y + 1.62.

```javascript
camera.position.set(player.x, player.y + 1.62, player.z);
camera.rotation.set(pitch, yaw, 0, 'YXZ');
```

Respawn:
```javascript
function respawn() {
  // find terrain height at (8, 8)
  let sy = 79;
  while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
  player.x = 8; player.z = 8; player.y = sy + 1.5; player.vy = 0;
}
```

Hmm, spawn at x=8, z=8. Let me compute the surface.

Now the target outline. Each frame, after raycasting, if there's a hit, draw wireframe at target block.

```javascript
let targetBox = null; // the LineSegments
// create once
const targetGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(1,1,1));
targetBox = new THREE.LineSegments(targetGeo, new THREE.LineBasicMaterial({color: 0x000000}));
targetBox.visible = false;
scene.add(targetBox);
```

Update each frame:
```javascript
if (targetBlock && pointerLocked) {
  targetBox.position.set(targetBlock[0]+0.5, targetBlock[1]+0.5, targetBlock[2]+0.5);
  targetBox.visible = true;
} else {
  targetBox.visible = false;
}
```

Raycasting:
```javascript
function updateRaycast() {
  raycaster.set(camera.position, cameraDir);
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  targetBlock = null;
  placeCell = null;
  if (hits.length > 0) {
    const hit = hits[0];
    const p = hit.point;
    const n = hit.face.normal; // in local space; since mesh at origin, same as world
    // break target
    targetBlock = [Math.floor(p.x - n.x*0.5), Math.floor(p.y - n.y*0.5), Math.floor(p.z - n.z*0.5)];
    placeCell = [Math.floor(p.x + n.x*0.5), Math.floor(p.y + n.y*0.5), Math.floor(p.z + n.z*0.5)];
  }
}
```

Wait, hit.face.normal is in the mesh's local coordinate system. Since the mesh is at origin (position 0,0,0) with no rotation, local normals = world normals. Good.

cameraDir: I need the forward direction of the camera. Let me compute from pitch/yaw:
cameraDir = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)) as derived. But wait, that was forward = R*(0,0,-1). Let me recompute: forward = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)). Yes.

Let me use a Vector3 and set it each frame.

Now the world generation loop each frame. Let me implement:

```javascript
let genQueue = [];
let meshQueue = [];

function updateWorldGeneration() {
  const pcx = Math.floor(player.x / 16);
  const pcz = Math.floor(player.z / 16);
  
  // Generate block data for chunks within 5 chunks (max 4 per frame)
  let genCount = 0;
  for (let dz = -5; dz <= 5 && genCount < 4; dz++) {
    for (let dx = -5; dx <= 5 && genCount < 4; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx+","+cz;
      if (!chunks.has(key)) {
        generateAndStore(cx, cz);
        genCount++;
      }
    }
  }
  
  // Build meshes for chunks within 4 chunks whose 4 neighbors have data (max 2 per frame)
  let meshCount = 0;
  for (let dz = -4; dz <= 4 && meshCount < 2; dz++) {
    for (let dx = -4; dx <= 4 && meshCount < 2; dx++) {
      const cx = pcx + dx, cz = pcz + dz;
      const key = cx+","+cz;
      if (chunks.has(key) && !chunks.get(key).mesh) {
        // check 4 neighbors
        if (chunks.has((cx+1)+","+cz) && chunks.has((cx-1)+","+cz) &&
            chunks.has(cx+","+((cz+1))) && chunks.has(cx+","+((cz-1)))) {
          buildMesh(cx, cz);
          meshCount++;
        }
      }
    }
  }
  
  // Remove chunks farther than 7
  for (const [key, chunk] of chunks) {
    const parts = key.split(",");
    const cx = parseInt(parts[0]), cz = parseInt(parts[1]);
    if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
      if (chunk.mesh) {
        const idx = chunkMeshes.indexOf(chunk.mesh);
        if (idx >= 0) chunkMeshes.splice(idx, 1);
        scene.remove(chunk.mesh);
        if (chunk.geo) chunk.geo.dispose();
      }
      chunks.delete(key);
    }
  }
}
```

generateAndStore:
```javascript
function generateAndStore(cx, cz) {
  const data = new Uint8Array(16*16*80);
  generateChunkData(cx, cz, data);
  chunks.set(cx+","+cz, { data: data, mesh: null, geo: null });
}
```

Now, initial setup. Before the first frame, I should generate chunks around spawn so the player lands on terrain. Let me pre-generate all chunks within some radius before starting, or generate enough. Actually, the player spawns at (8,8) which is in chunk (0,0). Let me pre-generate chunks in a small radius at startup so the player has terrain to stand on and can see around.

Let me pre-generate all chunks within, say, 3 chunks and build their meshes at startup. That ensures immediate playability.

Actually, let me pre-generate a radius of chunks (e.g., 4) and build meshes for those whose neighbors exist. At startup, generate all within radius 4 first (not limited to 4/frame), then build meshes.

```javascript
function initWorld() {
  // generate all chunks within radius 4
  for (let dz = -4; dz <= 4; dz++)
    for (let dx = -4; dx <= 4; dx++)
      generateAndStore(dx, dz);
  // build meshes
  for (let dz = -4; dz <= 4; dz++)
    for (let dx = -4; dx <= 4; dx++)
      buildMesh(dx, dz);
  // find spawn height
  let sy = 79;
  while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
  player.x = 8; player.z = 8; player.y = sy + 1.5;
}
```

This generates 9x9 = 81 chunks at startup. Each chunk has up to 16*16*80 = 20480 bytes = 20KB, so 81 chunks = ~1.6MB. Fine.

Meshing 81 chunks at startup might take a moment but acceptable.

Now let me think about the overlay. Start overlay with title, controls list, "Click to play". Reappears when pointer lock released.

```html
<div id="overlay">
  <h1>Minecraft Clone</h1>
  <ul>
    <li>WASD - Move</li>
    <li>Mouse - Look</li>
    <li>Space - Jump</li>
    <li>Left Click - Break block</li>
    <li>Right Click - Place block</li>
    <li>1-7 / Wheel - Select block</li>
  </ul>
  <div>Click to play</div>
</div>
```

CSS to style it fullscreen.

Crosshair:
```html
<div id="crosshair"></div>
```
CSS: centered, two lines.

Hotbar:
```html
<div id="hotbar">
  <div class="slot" data-i="0">...</div>
  ...
</div>
```
Build with JS or static HTML. Let me build with JS for the border highlight.

Let me now write the full HTML.

Let me reconsider the FACES winding to ensure normals are outward and triangles render. Since I'm using DoubleSide, winding doesn't affect visibility, but affects lighting? No—with vertex colors and Lambert, lighting uses normals regardless of winding. And DoubleSide renders both sides. So winding is irrelevant for correctness here. Good. But let me still make them reasonable.

Actually wait, there's a concern with DoubleSide and the fake lighting. With DoubleSide, a top face (normal +Y, shade 1.0) is lit bright. Its underside (viewed from below) also uses the same normal +Y, so also bright. That's fine visually. Bottom faces (normal -Y, shade 0.55) dark from both sides. Fine.

Let me keep DoubleSide.

Now, one concern: performance. Each chunk can have many faces. With 81 chunks visible, and each chunk having maybe a few thousand faces, total could be a few million triangles. MeshLambertMaterial with vertex colors should handle that. Three.js r128 with a single draw call per chunk (81 draw calls) is fine.

Actually, chunk mesh counts: a 16x16x80 chunk with terrain might have ~16*16*some faces. Exposed faces maybe ~1000-3000 per chunk. 81 chunks * 2000 faces * 2 tris = ~324k triangles. Fine.

Let me also make sure I set the camera far to 400 and fog accordingly.

Fog: THREE.Fog(0x87ceeb, 40, 110). Sky color 0x87ceeb.

Lights: ambient 0.65 (white), directional 0.8.

```javascript
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(50, 100, 30);
scene.add(sun);
```

Background: scene.background = new THREE.Color(0x87ceeb).

Now let me handle the water re-centering and clouds.

Clouds:
```javascript
const cloudGroup = new THREE.Group();
for (let i = 0; i < 25; i++) {
  const w = 8 + (i*37 % 20);
  const d = 6 + (i*53 % 15);
  const geo = new THREE.BoxGeometry(w, 2, d);
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
  const cloud = new THREE.Mesh(geo, mat);
  cloud.position.set((i*137 % 300) - 150, 90, (i*211 % 300) - 150);
  clouds.push(cloud);
  scene.add(cloud);
}
```

Update: drift in x, wrap around player.
```javascript
function updateClouds() {
  for (const c of clouds) {
    c.position.x += 0.5 * dt; // drift
    // wrap around player
    if (c.position.x - player.x > 200) c.position.x -= 400;
    if (c.position.x - player.x < -200) c.position.x += 400;
    if (c.position.z - player.z > 200) c.position.z -= 400;
    if (c.position.z - player.z < -200) c.position.z += 400;
  }
}
```

Hmm, but clouds should be at fixed world positions that wrap. Let me keep it simple: drift x, and if too far from player in x or z, snap back.

Actually, let me reconsider. The clouds are added directly to scene (not a group), and I recenter them relative to player. Let me just move them so they stay near the player but drift.

Let me store initial positions and drift, computing wrap based on player.

Water re-center:
```javascript
water.position.x = player.x;
water.position.z = player.z;
```

Now let me also handle the case where the player is below water or the water plane is huge (500x500). Re-centered on player. Good.

Let me also double check the "eye 1.62" — camera.y = player.y + 1.62.

Spawn: player.y = sy + 1.5 (feet above surface). Then camera at sy + 1.5 + 1.62 = sy + 3.12. The surface block top is at sy (block occupies [sy, sy+1]). So player feet at sy+1.5 is inside... wait. If surface block is at y=sy (occupying [sy, sy+1]), then the ground top is at sy+1. Player feet should be at sy+1 (just above ground) or slightly higher. Let me set player.y = sy + 1 + 0.5 = sy + 1.5. That places feet at sy+1.5, which is inside the surface block region? No: surface block occupies [sy, sy+1]. Player feet at sy+1.5 is above sy+1, so above the surface block. Good, but the player box extends from feet to feet+1.8 = sy+1.5 to sy+3.3. The surface block [sy, sy+1] doesn't overlap [sy+1.5, sy+3.3]. Good. But wait, will gravity immediately push player down onto the block? Player falls until feet reach sy+1 (block top). At feet=sy+1, box is [sy+1, sy+2.8], block [sy, sy+1] — they touch at sy+1 but overlap check: py < vy+1 (sy+1 < sy+1? No, equal, not <). Hmm, my collision uses strict inequalities. Let me check: overlap requires py < vy+1 AND py+h > vy. py=sy+1, vy=sy: py < vy+1 => sy+1 < sy+1 => false. So no overlap detected, player falls through!

This is a problem with strict inequalities. I need to handle the boundary. Let me use <= for one side. Actually, the issue is floating point and exact boundaries. Let me reconsider.

AABB overlap for voxel [vx, vx+1] and player [px-hw, px+hw] etc. The condition for overlap (closed intervals) is:
px-hw <= vx+1 && px+hw >= vx && ...

But if I use <= and >=, then touching counts as overlap, and the player would stop exactly at the boundary. But then there's the reverse problem: if player is exactly at boundary and tries to move, it might get stuck.

Let me use the standard approach: overlap if (px-hw < vx+1) && (px+hw > vx) etc. with strict inequalities, but ensure the player doesn't spawn inside.

Actually the real issue is when the player lands exactly on top. Let me think about how the collision resolves. When falling, player.y decreases. At some point collides() returns true. We set vy=0 and onGround=true, keeping player.y at the last non-colliding position.

Let me trace: player at feet y where box [y, y+1.8]. Block [sy, sy+1]. Overlap if y < sy+1 && y+1.8 > sy, i.e., y < sy+1 and y > sy-1.8. So for y in (sy-1.8, sy+1), overlap. 

If player falls from above, the first y where overlap occurs: as y decreases from large values, overlap starts when y < sy+1. So at y slightly less than sy+1, e.g., y = sy+1 - epsilon. collides true. We revert: player.y stays at previous (non-colliding) y. The previous y was >= sy+1 (the step before). Hmm, but with dt, the player moves by vy*dt each frame. If vy is small near landing, the player might step to y = sy+1 exactly or just above.

Actually, the issue: if at y = sy+1 exactly, no overlap (boundary). Player continues falling to y = sy+1 - vy*dt. If vy*dt is small, player is at sy+1 - small, which overlaps. Then we revert to sy+1. But sy+1 has no overlap (boundary, not strictly overlapping), so player stands at y=sy+1, box [sy+1, sy+2.8]. That's fine—feet exactly at block top sy+1. Camera at sy+1+1.62 = sy+2.62. Good, standing on ground.

But wait, at y=sy+1, is there really no overlap? Block [sy, sy+1], player box [sy+1, sy+2.8]. They share the boundary plane y=sy+1. With strict inequality py < vy+1 => sy+1 < sy+1 false. So no overlap. Player can stand there. But then next frame, gravity applies, vy becomes negative, player tries y = sy+1 - step. If step is tiny, y = sy+1 - tiny overlaps, revert to sy+1. So player oscillates around sy+1. That's acceptable—player effectively stands at sy+1.

But there's a risk: if the player spawns at y = sy+1.5 and the very first thing is gravity, they fall a bit and land at sy+1. Fine.

Hmm, but actually I realize the spawn at sy+1.5: box [sy+1.5, sy+3.3]. Block [sy, sy+1]. No overlap (sy+1.5 > sy+1). Good, player starts above ground, falls, lands at sy+1. 

But actually, let me reconsider whether strict inequality causes the player to fall through thin gaps. Consider a ledge: player walks off and needs to land on a block whose top is at sy+1. Player approaches horizontally. As player moves toward the ledge, the vertical collision only triggers when the box overlaps. With horizontal movement, the player's box might slide. This is getting complicated but standard voxel collision with strict inequalities generally works for landing on top because gravity pulls down and the boundary case stops the player.

Actually, let me reconsider. The cleaner approach: use inclusive comparison but snap. Let me think about what happens with the "revert on overlap" approach and strict inequalities.

The concern is tunneling: if player moves down by more than 1 block per frame, they could skip past a block. With gravity 25 and dt capped at 0.05, max vy in one frame ~ 25*0.05 = 1.25 plus existing velocity. Could exceed 1 block. Let me cap vy or use substeps. Actually, terminal velocity: vy starts at 0, after several frames reaches ~25*0.05=1.25 per frame if we cap dt. Actually vy accumulates: vy = 25*t. Over 0.05s, Δy = 0.5*25*0.05^2 ≈ 0.03 per frame initially, growing. Terminal when drag... there's no drag, so vy keeps increasing! vy = 25*t, after 1 second vy=25, Δy per frame = 25*0.05 = 1.25 > 1. Tunneling risk when falling from great height.

But the fall-below-20 teleport prevents extreme falls. Still, during a fall from moderate height, vy could exceed 1 block/frame. Let me cap vy to something like 3-4 blocks/frame, or use substeps.

Let me cap terminal velocity to a reasonable value, say 20 m/s (vy >= -20). Even at 20 m/s, Δy per 0.05 frame = 1.0, borderline. Let me use smaller dt substeps or cap vy at ~10. Let me cap vy at -15. Δy = 15*0.05 = 0.75 < 1. Safe-ish. But to be really safe, let me do multiple collision substeps based on distance.

Alternatively, I'll just cap dt to 0.03 and cap vy to -12. Δy = 12*0.03 = 0.36. Safe. Let me do that. Actually, let me keep dt cap 0.05 but cap vy at -10. Δy = 0.5. Good enough.

Hmm, but jumping to -10 cap might feel odd. It's fine for a demo. Let me cap vy at -12 and dt at 0.033. Let me use dt cap = 1/30.

Actually, let me just do a simple approach: cap dt to 0.05, and do the collision with a check. To mitigate tunneling, I'll limit the vertical step. Actually, simplest robust solution: substep the movement. Divide the frame into N steps based on max step size. But that complicates. Let me just cap vy and dt. I'll cap vy at -16 and dt at 0.05 → step 0.8 < 1. Acceptable.

Hmm, let me reconsider. Let me cap dt to 0.05 and vy to -16. Max vertical step 0.8 blocks. Should prevent tunneling in most cases. Combined with the fact that the player mostly lands gently. OK.

Actually, you know what, let me just be safe and cap vy at -10. Δy max = 10*0.05 = 0.5. Very safe. Terminal velocity 10 m/s with gravity 25 means reaches terminal in 0.4s. Fine.

Let me now also reconsider: the collision check iterates voxels. For performance, only check nearby voxels. Player box spans a few voxels. Fine.

Let me also make sure collides() uses getBlock which returns 0 for out of range (y>79 or missing chunk). For y>79, getBlock returns 0 (air), so player can be in the sky. Good. For the unbreakable floor at y=0, getBlock returns stone, so player can't go below y=0... but player feet could be at y=0? Player box [0, 1.8], block [0,1] overlaps. So player would be pushed up to y=0? Let me check: at y=0, box [0,1.8], block [0,1]: py=0 < vy+1=1 true, py+h=1.8 > vy=0 true → overlap. So player can't reach y=0 exactly; they'd be pushed to y=epsilon. Actually the lowest they can go: find smallest y with no overlap. Box [y, y+1.8], floor block [0,1]. Overlap when y < 1 and y+1.8 > 0, i.e., y > -1.8 and y < 1. So for y in (-1.8, 1), overlap. Lowest non-overlapping y: y >= 1 (box [1, 2.8], floor [0,1], touch at 1, no strict overlap). So player stands at y=1 on the floor. Good, floor at y=0 acts as bedrock.

Now, let me write everything out.

Let me reconsider the raycaster. In Three.js r128, Raycaster.set(origin, direction). Direction should be normalized. Let me normalize cameraDir.

Also, intersectObjects with recursive=false. chunkMeshes is a flat array of meshes. Good.

The hit.point is in world coordinates (since meshes at origin, world = local). hit.face.normal is in mesh-local coords = world coords (mesh at origin, no rotation). Good.

But wait—there's a subtlety. When multiple chunks are merged conceptually but stored as separate meshes, the raycast hits one mesh. The normal from that mesh's face is correct for that face. Good.

However, there's a potential issue: adjacent chunk faces. If chunk A's block at edge is exposed to chunk B's air, the face is rendered in chunk A's mesh (since we check neighbor via getBlock which reads chunk B). Good, the face exists. The raycast hits chunk A's mesh at that face. Normal correct.

Now, another subtlety: the raycast might hit a face that's shared but the geometry from two chunks could have coincident vertices at boundaries, causing z-fighting or ray ambiguity. Minor, acceptable.

Let me also consider: should I disable the raycast when not locked? Yes, only break/place when locked. But the outline—I'll show it only when locked too, or always? Spec says outline the targeted block. Let me show it when there's a target and pointer is locked. Actually, let me show the outline whenever there's a valid target regardless, but only act on clicks when locked. Hmm, but raycasting every frame even when not locked is fine performance-wise. Let me update the raycast every frame and show outline when locked (since that's when it matters). Actually, let me always update raycast and outline; it doesn't hurt. But to be safe per spec ("Only while the pointer is locked: left click..."), the outline can be shown anytime. Let me show outline when locked.

Let me finalize the code.

One more: the hotbar HTML. Let me create 7 slots with colors and numbers.

```html
<div id="hotbar"></div>
```
Build in JS:
```javascript
const blockNames = ['Grass','Dirt','Stone','Sand','Wood','Leaves','Snow'];
const blockColorsHex = ['#4caf50','#795548','#9e9e9e','#e7d9a8','#8d6e63','#2e7d32','#ffffff'];
const hotbarEl = document.getElementById('hotbar');
for (let i = 0; i < 7; i++) {
  const slot = document.createElement('div');
  slot.className = 'slot';
  slot.dataset.i = i;
  slot.innerHTML = `<div class="swatch" style="background:${blockColorsHex[i]}"></div><span class="num">${i+1}</span><span class="label">${blockNames[i]}</span>`;
  hotbarEl.appendChild(slot);
}
function updateHotbar() {
  const slots = hotbarEl.children;
  for (let i = 0; i < 7; i++) {
    slots[i].classList.toggle('selected', (i+1) === selectedBlock);
  }
}
```

CSS for slots, swatch, num, label, selected border.

Now let me write the CSS for the overlay, crosshair, hotbar.

Overlay:
```css
#overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.75);
  color: #fff;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  font-family: sans-serif;
  z-index: 10;
  cursor: pointer;
}
#overlay h1 { font-size: 48px; margin-bottom: 20px; letter-spacing: 2px; }
#overlay ul { list-style: none; font-size: 18px; line-height: 1.8; }
#overlay .play { margin-top: 30px; font-size: 22px; border: 2px solid #fff; padding: 10px 20px; }
```

Crosshair:
```css
#crosshair {
  position: fixed; left: 50%; top: 50%; transform: translate(-50%, -50%);
  width: 20px; height: 20px; z-index: 5; pointer-events: none;
}
#crosshair::before, #crosshair::after {
  content: ''; position: absolute; background: #fff;
}
#crosshair::before { left: 50%; top: 0; width: 2px; height: 100%; transform: translateX(-50%); }
#crosshair::after { top: 50%; left: 0; height: 2px; width: 100%; transform: translateY(-50%); }
```

Hotbar:
```css
#hotbar {
  position: fixed; left: 50%; bottom: 20px; transform: translateX(-50%);
  display: flex; gap: 4px; padding: 6px; background: rgba(0,0,0,0.5);
  border-radius: 6px; z-index: 5; pointer-events: none;
}
.slot {
  width: 48px; height: 48px; position: relative;
  border: 3px solid transparent; border-radius: 4px; background: rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
}
.slot.selected { border-color: #fff; }
.swatch { width: 34px; height: 34px; border-radius: 3px; border: 1px solid rgba(0,0,0,0.3); }
.num { position: absolute; top: 1px; left: 3px; color: #fff; font-family: sans-serif; font-size: 12px; }
.label { position: absolute; bottom: 0; width: 100%; text-align: center; color: #fff; font-family: sans-serif; font-size: 9px; }
```

Canvas:
```css
body { margin: 0; overflow: hidden; }
canvas { display: block; }
```

Now let me assemble the full file.

Let me reconsider the noise functions for correctness.

hash function:
```javascript
function hash2(ix, iy) {
  let h = ix * 374761393 + iy * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}
```

This gives 0-1. Good.

noise2D:
```javascript
function smoothstep(t) { return t * t * (3 - 2 * t); }
function lerp(a, b, t) { return a + (b - a) * t; }

function noise2D(x, y) {
  const ix = Math.floor(x), iy = Math.floor(y);
  const fx = x - ix, fy = y - iy;
  const u = smoothstep(fx), v = smoothstep(fy);
  const a = hash2(ix, iy);
  const b = hash2(ix + 1, iy);
  const c = hash2(ix, iy + 1);
  const d = hash2(ix + 1, iy + 1);
  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}
```

fractal2D:
```javascript
function fractal2D(x, y, oct) {
  let sum = 0, amp = 1, freq = 1, norm = 0;
  for (let i = 0; i < oct; i++) {
    sum += amp * noise2D(x * freq, y * freq);
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / norm;
}
```

noise3D:
```javascript
function noise3D(x, y, z) {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
  const fx = x - ix, fy = y - iy, fz = z - iz;
  const u = smoothstep(fx), v = smoothstep(fy), w = smoothstep(fz);
  const c = [
    hash2(ix, iy) /* ignore z? */ ...
  ];
}
```

For 3D, I need 8 corners. Let me define a hash3:
```javascript
function hash3(ix, iy, iz) {
  let h = ix * 374761393 + iy * 668265263 + iz * 2147483647;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return (h >>> 0) / 4294967296;
}

function noise3D(x, y, z) {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
  const fx = x - ix, fy = y - iy, fz = z - iz;
  const u = smoothstep(fx), v = smoothstep(fy), w = smoothstep(fz);
  const c000 = hash3(ix, iy, iz);
  const c100 = hash3(ix+1, iy, iz);
  const c010 = hash3(ix, iy+1, iz);
  const c110 = hash3(ix+1, iy+1, iz);
  const c001 = hash3(ix, iy, iz+1);
  const c101 = hash3(ix+1, iy, iz+1);
  const c011 = hash3(ix, iy+1, iz+1);
  const c111 = hash3(ix+1, iy+1, iz+1);
  const x00 = lerp(c000, c100, u);
  const x10 = lerp(c010, c110, u);
  const x01 = lerp(c001, c101, u);
  const x11 = lerp(c011, c111, u);
  const y0 = lerp(x00, x10, v);
  const y1 = lerp(x01, x11, v);
  return lerp(y0, y1, w);
}
```

fractal3D:
```javascript
function fractal3D(x, y, z, oct) {
  let sum = 0, amp = 1, freq = 1, norm = 0;
  for (let i = 0; i < oct; i++) {
    sum += amp * noise3D(x*freq, y*freq, z*freq);
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return sum / norm;
}
```

Caves use fractal3D(wx*0.09, y*0.09, wz*0.09, 3). Good.

Now, let me double-check the tree placement and the "only into air" for leaves. In addLeaf, I check data[ty] === 0 before setting. Good.

Wait, there's an issue with the tree leaf layers and the chunk boundary check. I restricted lx in [2,13] and lz in [2,13], so leaves (±2) stay within [0,15]. Good. And the trunk is at lx,lz. Good.

Let me also reconsider: the tree check `data[(H-1)*256 + lz*16 + lx] === 1` ensures surface is grass. Good.

Now, potential issue: trees generated near chunk borders. Since I restrict to lx,lz in [2,13], trees are well within the chunk. But trees at the very edge of the world (chunk border) won't generate because the column is within [2,13] of the chunk. That's fine—trees still appear, just not exactly on borders.

Hmm wait, actually there's a subtle issue: a tree column at lx=2 is fine (leaves extend to lx=0). But what about a tree that would need to be at the border for continuity? Not important.

Let me also handle: when placing leaves, the layerY for 5x5 is H+4 and H+5. Wait let me recompute. Surface at H-1. Trunk from H to H+3 (4 blocks). Then leaves: 5x5 twice at H+4, H+5. 3x3 at H+6. Top at H+7.

Wait, I said earlier trunk is 4 blocks: i from 1 to 4, ty = H-1+i = H, H+1, H+2, H+3. So trunk occupies H to H+3. Leaves start at H+4. Good.

Let me rewrite the tree code cleanly:
```javascript
if (data[(H-1)*256 + lz*16 + lx] === 1 && hash(wx, wz) < 0.02 &&
    lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 && H + 7 <= 78) {
  // trunk
  for (let i = 0; i < 4; i++) {
    const ty = H + i; // H, H+1, H+2, H+3
    data[ty*256 + lz*16 + lx] = 5;
  }
  // 5x5 leaves twice
  for (let ly = 0; ly < 2; ly++) {
    const ly_ = H + 4 + ly;
    for (let dx = -2; dx <= 2; dx++)
      for (let dz = -2; dz <= 2; dz++) {
        const ti = ly_*256 + (lz+dz)*16 + (lx+dx);
        if (data[ti] === 0) data[ti] = 6;
      }
  }
  // 3x3
  const ly3 = H + 6;
  for (let dx = -1; dx <= 1; dx++)
    for (let dz = -1; dz <= 1; dz++) {
      const ti = ly3*256 + (lz+dz)*16 + (lx+dx);
      if (data[ti] === 0) data[ti] = 6;
    }
  // top
  const top = H + 7;
  const ti = top*256 + lz*16 + lx;
  if (data[ti] === 0) data[ti] = 6;
}
```

H+7 <= 78 means top at H+7 <= 78 < 80. Good. Actually let me use H+7 <= 79, i.e., H <= 72. Let me use H + 7 <= 79.

Wait, data array size is 16*16*80 = 20480, indices 0..20479. Index for y=79: 79*256 + ... = 20224 + up to 405 = up to 20629? Wait that's wrong! 79*256 = 20224, + lz*16 (max 240) + lx (max 15) = 20224+240+15 = 20479. OK good, max index 20479 < 20480. Good. So y up to 79 valid. H+7 <= 79 → top at 79 valid.

Let me use H + 7 <= 79.

Now let me reconsider: the array index y*256 + lz*16 + lx. For y=79, lz=15, lx=15: 79*256 + 15*16 + 15 = 20224 + 240 + 15 = 20479. Array length 20480. Valid. 

Now let me write the meshing with correct indexing.

Let me also reconsider the FACES vertex definitions to avoid inverted faces. Actually with DoubleSide it's fine. Let me just define them reasonably.

Let me define FACES with normal and 4 vertices (as offsets from block origin), ensuring they form a proper quad. I'll pick order that's CCW from outside, but it doesn't matter with DoubleSide.

```javascript
const FACES = [
  { n: [ 1, 0, 0], s: 0.80, v: [[1,0,0],[1,0,1],[1,1,1],[1,1,0]] },
  { n: [-1, 0, 0], s: 0.80, v: [[0,0,1],[0,0,0],[0,1,0],[0,1,1]] },
  { n: [ 0, 1, 0], s: 1.00, v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { n: [ 0,-1, 0], s: 0.55, v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { n: [ 0, 0, 1], s: 0.80, v: [[1,0,1],[0,0,1],[0,1,1],[1,1,1]] },
  { n: [ 0, 0,-1], s: 0.80, v: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]] },
];
```

These are fine.

Now, let me consider the direction of the directional light. Position (50,100,30) pointing origin. Fine.

Let me also make sure fog doesn't hide the player's immediate surroundings. Fog 40 to 110. Player sees up to 110 blocks. With chunks within 4 (64 blocks) plus neighbor data within 5, visibility is okay. But chunks at distance 4-5 might be in fog. That's fine, atmospheric.

Actually, the meshing builds chunks within 4 (with neighbor data). Fog far is 110. Chunk at distance 4 = 64 blocks away, within fog. Chunk at 5 = 80 blocks, partially foggy. Since we generate within 5 but only mesh within 4, the 5-ring has no mesh. That's fine—fog hides beyond ~110 anyway.

Wait, but generating within 5 and meshing within 4: the visible range is chunks within 4 = up to 4*16=64 blocks from chunk center, plus player offset. Player can be up to 16 blocks into a chunk, so max distance to a meshed chunk edge ~ 4*16 + 16 = 80 blocks. Within fog 110. Good.

Let me now also double check the raycast max distance 6. The raycaster far: I'll set raycaster.far = 6? Actually Raycaster.far defaults to Infinity. Let me set it. In r128, Raycaster has `this.far = Infinity` and method `setFar(far)`. Let me set raycaster.set(origin, dir) then raycaster.far = 6. Actually, let me just intersect and filter by distance manually to be safe.

```javascript
const hits = raycaster.intersectObjects(chunkMeshes, false);
let closest = null;
for (const h of hits) {
  if (h.distance <= 6) { closest = h; break; } // intersectObjects returns sorted by distance
}
```

intersectObjects returns sorted by distance ascending, so first hit within 6 is the closest. Good.

Now let me write it all.

Let me also handle window resize:
```javascript
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

Renderer:
```javascript
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);
```

Scene:
```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);
```

Camera:
```javascript
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 400);
```

Now, the overlay click to play:
```javascript
const overlay = document.getElementById('overlay');
overlay.addEventListener('click', () => {
  canvas.requestPointerLock();
});
```

And pointerlockchange shows/hides overlay:
```javascript
document.addEventListener('pointerlockchange', () => {
  pointerLocked = (document.pointerLockElement === canvas);
  overlay.style.display = pointerLocked ? 'none' : 'flex';
});
```

Wait, but clicking the overlay requests pointer lock, which then triggers pointerlockchange hiding the overlay. Good. When ESC pressed, pointer lock released, overlay reappears. Good.

Now, the mousedown for break/place:
```javascript
canvas.addEventListener('mousedown', (e) => {
  if (!pointerLocked) return;
  if (e.button === 0) {
    // break
    if (targetBlock) {
      const [bx, by, bz] = targetBlock;
      if (by !== 0) {
        setBlock(bx, by, bz, 0);
        rebuildChunk(bx, bz);
      }
    }
  } else if (e.button === 2) {
    // place
    if (placeCell) {
      const [px, py, pz] = placeCell;
      if (getBlock(px, py, pz) === 0 && !playerOverlapsBlock(px, py, pz)) {
        setBlock(px, py, pz, selectedBlock);
        rebuildChunk(px, pz);
      }
    }
  }
});
```

playerOverlapsBlock: check if placing a block at (px,py,pz) overlaps player box.
```javascript
function playerOverlapsBlock(bx, by, bz) {
  const hw = 0.3, h = 1.8;
  // player box [x-hw,x+hw] x [y,y+h] x [z-hw,z+hw]
  // block [bx,bx+1] x [by,by+1] x [bz,bz+1]
  return (player.x - hw < bx+1 && player.x + hw > bx &&
          player.y < by+1 && player.y + h > by &&
          player.z - hw < bz+1 && player.z + hw > bz);
}
```

Note: for placed blocks, we should also prevent placing inside the player. This handles it.

Now rebuildChunk for place/break: rebuild the chunk containing the edited block, plus neighbors if on border.

Let me finalize rebuildChunk:
```javascript
function rebuildChunkEdit(x, z) {
  const cx = Math.floor(x/16), cz = Math.floor(z/16);
  rebuildSingleMesh(cx, cz);
  const lx = x - cx*16, lz = z - cz*16;
  if (lx === 0) rebuildSingleMesh(cx-1, cz);
  else if (lx === 15) rebuildSingleMesh(cx+1, cz);
  if (lz === 0) rebuildSingleMesh(cx, cz-1);
  else if (lz === 15) rebuildSingleMesh(cx, cz+1);
}
```

rebuildSingleMesh disposes old and builds new.

Now let me make sure I don't rebuild meshes that don't exist (return early).

Let me also make sure the chunkMeshes array is properly maintained (add on build, remove on rebuild/remove).

Let me write buildMesh to NOT push to chunkMeshes if mesh already exists; and rebuildSingleMesh removes old first.

Let me restructure: buildMesh creates mesh and pushes to chunkMeshes. rebuildSingleMesh removes old mesh (from scene and chunkMeshes), disposes geo, then calls buildMesh.

Let me write it.

Also, I realize when I generateAndStore at startup and then buildMesh for all, that's fine.

Let me also handle the initial generation timing. Generating 81 chunks and meshing 81 chunks at startup could take ~1-2 seconds. During that time the overlay is showing (pointer not locked). After initWorld(), the overlay is hidden on first click. Actually, the overlay appears and waits for click. But initWorld runs synchronously before the first frame. Since initWorld is called before animate() starts, by the time user clicks, world is ready. Good.

Wait, but initWorld meshes 81 chunks. Meshing involves building BufferGeometry with potentially millions of vertices. Let me estimate: 81 chunks, each maybe 2000-5000 faces, each face 6 vertices (2 triangles * 4? no, 2 triangles = 6 vertices). So 5000 faces * 6 = 30000 vertices per chunk * 81 = 2.4M vertices. Float32BufferAttribute creation for that... should be okay, maybe 0.5-1s. Acceptable for startup.

Hmm, actually let me reduce. Not all 81 chunks will be fully meshed with max faces. Many faces are internal. Exposed faces maybe 1000-3000 per chunk. Let me not worry.

Actually, wait. Let me reconsider building 81 meshes at once. It might cause a noticeable hitch. But it's a one-time cost. Alternatively, I could pre-generate data for a smaller radius and let the frame loop build meshes. But then the player might spawn in air if the spawn chunk isn't meshed yet. Let me pre-generate data for radius 4 and build meshes for radius 2 (25 chunks) at startup, so the player definitely has terrain below and around. Then the frame loop builds the rest.

Actually, simpler: pre-generate data for radius 3 (49 chunks) and build meshes for radius 2 (25 chunks). Player at (8,8) in chunk (0,0), which is meshed. Player sees neighbors. Good.

Let me do: initWorld generates data for radius 3, builds meshes for radius 2. Actually, to be safe for visibility, let me build meshes for radius 2 and generate data for radius 4. The frame loop continues.

Hmm, let me just pre-generate all data for radius 3 and build all meshes for radius 2. Let me code:

```javascript
function initWorld() {
  for (let dz = -3; dz <= 3; dz++)
    for (let dx = -3; dx <= 3; dx++)
      generateAndStore(dx, dz);
  for (let dz = -2; dz <= 2; dz++)
    for (let dx = -2; dx <= 2; dx++)
      buildMesh(dx, dz);
  // spawn
  let sy = 79;
  while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
  player.x = 8; player.z = 8; player.y = sy + 1.5;
}
```

Good. Radius 2 meshed = 25 chunks. Player at center.

Now let me write the whole thing.

Let me reconsider the cameraDir computation and make sure raycasting points in the look direction.

cameraDir = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)).

At yaw=0, pitch=0: cameraDir = (0, 0, -1). Camera looks along -Z. Correct (Three.js default).

Let me verify camera.rotation.set(pitch, yaw, 0, 'YXZ') gives look direction cameraDir. Earlier I derived forward = R*(0,0,-1) = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)). And camera.rotation uses Euler (pitch, yaw, 0) in YXZ order, meaning rotation = Ry(yaw) * Rx(pitch) * Rz(0). Wait, Euler order 'YXZ' with angles (x=pitch, y=yaw, z=0) means the rotations are applied in order Z, then X, then Y? The order specifies the sequence. In Three.js, Euler order 'YXZ' means rotate around Y first, then X, then Z. The resulting matrix is R = Rz * Rx * Ry? No...

Let me recall: For order 'XYZ', the matrix is R = Rx * Ry * Rz (first rotation rightmost). For order 'YXZ', R = Rz * Rx * Ry. With z=0, Rz=I, so R = Rx * Ry.

Hmm, that changes things. Let me recompute with R = Rx(pitch) * Ry(yaw).

forward = R * (0,0,-1) = Rx(pitch) * Ry(yaw) * (0,0,-1).
Ry(yaw)*(0,0,-1) = (-sin(yaw), 0, -cos(yaw)) [computed earlier].
Rx(pitch) * (-sin(yaw), 0, -cos(yaw)):
Rx = [[1,0,0],[0,cp,-sp],[0,sp,cp]]
- x: -sin(yaw)
- y: cp*0 - sp*(-cos(yaw)) = sp*cos(yaw)
- z: sp*0 + cp*(-cos(yaw)) = -cp*cos(yaw)
So forward = (-sin(yaw), sin(pitch)*cos(yaw), -cos(pitch)*cos(yaw)).

Hmm, that's different from before. The difference is whether pitch affects y via cos(pitch) or the yaw. Let me just test empirically in my head... this is getting confusing. Let me instead compute the forward vector using camera.getWorldDirection() which is unambiguous.

Actually, the cleanest: after setting camera.position and camera.rotation, compute forward via:
```javascript
const dir = new THREE.Vector3(0, 0, -1).applyEuler(camera.rotation).normalize();
```

applyEuler applies the rotation to the vector. This gives the exact look direction. Let me use that. It's robust.

```javascript
lookDir.set(0, 0, -1).applyEuler(camera.rotation).normalize();
raycaster.set(camera.position, lookDir);
```

And for movement, I need horizontal forward/right. Let me compute:
```javascript
const forwardH = new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(0, yaw, 0, 'YXZ'));
```
Hmm, but I need to be careful about yaw sign. Let me just derive horizontal movement from yaw directly, using the known convention.

Actually, let me define yaw such that moving W moves the camera in the direction it's looking (horizontally). Let me compute the horizontal forward from camera.rotation:
```javascript
const fwd = new THREE.Vector3(0, 0, -1).applyEuler(camera.rotation);
fwd.y = 0; fwd.normalize();
const right = new THREE.Vector3(1, 0, 0).applyEuler(camera.rotation);
right.y = 0; right.normalize();
```

Then movement = fwd * wInput + right * dInput. This is robust and matches the camera orientation exactly. Let me use this in updatePlayer. But computing Euler applications each frame is a bit costly but negligible.

Actually, applyEuler on a fresh Euler each frame is fine.

Wait, but I set camera.rotation AFTER computing movement? Let me set camera rotation first, then derive fwd/right from it. Or derive from yaw/pitch directly. Let me set camera.rotation first in updatePlayer, then compute fwd/right. Actually movement doesn't depend on camera position, only rotation. Let me compute fwd/right from camera.rotation at the start of updatePlayer (camera.rotation is set from previous frame or initial). Let me just compute from yaw/pitch using applyEuler with a cached Euler.

Let me use a cached Euler object:
```javascript
const tmpEuler = new THREE.Euler(0, 0, 0, 'YXZ');
```
In updatePlayer:
```javascript
tmpEuler.set(pitch, yaw, 0, 'YXZ');
const fwd = new THREE.Vector3(0,0,-1).applyEuler(tmpEuler);
fwd.y = 0; fwd.normalize();
const right = new THREE.Vector3(1,0,0).applyEuler(tmpEuler);
right.y = 0; right.normalize();
```

Then mvx = (fwd.x * w + right.x * d) * speed, etc.

And camera.rotation.copy(tmpEuler) or set(pitch, yaw, 0, 'YXZ').

And lookDir for raycast:
```javascript
lookDir.set(0,0,-1).applyEuler(tmpEuler).normalize();
```

Good, reuse tmpEuler.

Let me put this together in updatePlayer.

Now, let me reconsider: initial yaw/pitch = 0. fwd = (0,0,-1). Moving W moves -Z. Fine.

Let me now write the complete file.

Let me also add a subtle detail: the directional light should perhaps follow or be static. Static is fine.

Let me also make sure water doesn't render opaque—it's transparent. MeshLambertMaterial with transparent:true, opacity 0.6, side DoubleSide.

Now let me also double check: the water plane is 500x500 at y=14.3. Where terrain H <= 14 (roughly), water appears as lakes/beaches. Since water is a flat plane at 14.3, any terrain below 14.3 is "underwater" visually. Beaches (sand, H<=16) near water level will have water up to ~14.3. Good.

But the water plane at 14.3 might intersect terrain blocks (rendering through them). Since it's transparent and behind, it's fine visually. The spec says "water is visual only." Good.

Now, let me write it all out. Let me be thorough.

Actually, let me reconsider one thing about the collision and the `collides` function performance. It's called 3 times per frame, each iterating over a small voxel range. Fine.

Let me also make sure getBlock handles y correctly. y from 0 to 79. For y=0, that's the unbreakable stone. For y>79 or y<0, return 0.

Let me write getBlock:
```javascript
function getBlock(x, y, z) {
  if (y < 0 || y > 79) return 0;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk) return 0;
  const lx = x - cx * 16;
  const lz = z - cz * 16;
  return chunk.data[y * 256 + lz * 16 + lx];
}
```

setBlock:
```javascript
function setBlock(x, y, z, id) {
  if (y < 0 || y > 79) return;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk) return;
  const lx = x - cx * 16;
  const lz = z - cz * 16;
  chunk.data[y * 256 + lz * 16 + lx] = id;
}
```

Good.

Now, let me reconsider the meshing neighbor check. When meshing chunk (cx,cz), for a block at local (lx,lz,y), world coords (wx,wz,y). Neighbor in +x direction: (wx+1, y, wz). getBlock(wx+1, y, wz) reads the neighboring chunk if lx+1 == 16. Good, getBlock handles chunk boundaries.

Let me write buildMesh:
```javascript
const BLOCK_COLORS = [null, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];

function buildMesh(cx, cz) {
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk || !chunk.data) return;
  const data = chunk.data;
  const pos = [], norm = [], col = [];
  for (let y = 0; y < 80; y++) {
    for (let lz = 0; lz < 16; lz++) {
      for (let lx = 0; lx < 16; lx++) {
        const id = data[y * 256 + lz * 16 + lx];
        if (id === 0) continue;
        const wx = cx * 16 + lx;
        const wz = cz * 16 + lz;
        const c = BLOCK_COLORS[id];
        const r = ((c >> 16) & 255) / 255;
        const g = ((c >> 8) & 255) / 255;
        const b = (c & 255) / 255;
        for (let f = 0; f < 6; f++) {
          const face = FACES[f];
          const nx = wx + face.n[0];
          const ny = y + face.n[1];
          const nz = wz + face.n[2];
          if (getBlock(nx, ny, nz) === 0) {
            const s = face.s;
            for (let vi = 0; vi < 4; vi++) {
              const vt = face.v[vi];
              pos.push(wx + vt[0], y + vt[1], wz + vt[2]);
              norm.push(face.n[0], face.n[1], face.n[2]);
              col.push(r * s, g * s, b * s);
            }
          }
        }
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(norm, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  const mesh = new THREE.Mesh(geo, sharedMaterial);
  mesh.position.set(0, 0, 0);
  chunk.mesh = mesh;
  chunk.geo = geo;
  scene.add(mesh);
  chunkMeshes.push(mesh);
}
```

rebuildSingleMesh:
```javascript
function rebuildSingleMesh(cx, cz) {
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk) return;
  if (chunk.mesh) {
    scene.remove(chunk.mesh);
    const idx = chunkMeshes.indexOf(chunk.mesh);
    if (idx >= 0) chunkMeshes.splice(idx, 1);
    chunk.geo.dispose();
    chunk.mesh = null;
    chunk.geo = null;
  }
  buildMesh(cx, cz);
}
```

rebuildChunkEdit:
```javascript
function rebuildChunkEdit(x, z) {
  const cx = Math.floor(x / 16), cz = Math.floor(z / 16);
  rebuildSingleMesh(cx, cz);
  const lx = x - cx * 16, lz = z - cz * 16;
  if (lx === 0) rebuildSingleMesh(cx - 1, cz);
  else if (lx === 15) rebuildSingleMesh(cx + 1, cz);
  if (lz === 0) rebuildSingleMesh(cx, cz - 1);
  else if (lz === 15) rebuildSingleMesh(cx, cz + 1);
}
```

Now the world update loop. Let me refine to avoid rebuilding meshes that already exist.

In the mesh-build loop, I check `!chunks.get(key).mesh`. Good.

In the removal loop, I dispose and delete. Good.

Now let me also make sure that when a chunk's mesh is built, subsequent frames don't rebuild it (the `!mesh` check). Good.

Let me also handle the case where mesh building is limited to 2 per frame but there are many chunks needing meshes. That's fine, it builds gradually.

Now, one concern: the mesh-build loop iterates dz/dx from -4 to 4. For each chunk within 4 that lacks a mesh, if 4 neighbors have data, build. But the 4 neighbors' data existence: since we generate within 5 (max 4/frame), the neighbors might not have data yet on the first frames. But over several frames, data propagates. Since generation is 4/frame within radius 5, and meshing is 2/frame within radius 4 requiring neighbor data, it converges over ~30-60 frames as the player moves. At startup, we pre-build radius 2, so it's fine.

Hmm, but there's a subtle issue: the mesh-build loop requires ALL 4 orthogonal neighbors to have data. If a chunk at the edge of the generated region has a neighbor without data, it won't be meshed until that neighbor generates. Since generation radius (5) > meshing radius (4), the neighbors within radius 4+1=5 will eventually all have data. So convergence happens. Good.

Let me now also reconsider: should the mesh-build check neighbors' data or mesh? Spec: "build meshes for chunks within 4 chunks whose 4 neighbors already have data". So neighbors' data. Good, I check chunks.has for neighbors (which implies data exists since generateAndStore adds data immediately).

Let me write generateAndStore to add to map with data immediately.

Now let me write the final file.

Let me also add the water and clouds to the scene.

Let me also make sure I set renderer to handle alpha or not. Default opaque. Background color set on scene.

Let me also consider pixel ratio for performance: Math.min(devicePixelRatio, 2).

Let me write the animate loop with delta time.

```javascript
let lastTime = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  let dt = (now - lastTime) / 1000;
  lastTime = now;
  if (dt > 0.05) dt = 0.05;
  if (dt < 0) dt = 0;
  
  updatePlayer(dt);
  updateWorldGeneration();
  updateRaycast();
  updateClouds(dt);
  updateWater();
  updateOutline();
  
  renderer.render(scene, camera);
}
requestAnimationFrame(animate);
```

Wait, updatePlayer should only run when pointerLocked? The spec says movement via WASD. If pointer not locked, player shouldn't move. But gravity/collision... Let me only update player when locked. Actually, if not locked, the overlay covers the screen, so player state doesn't matter visually. But to be safe, let me update player physics only when locked. Actually, let me always apply gravity? No—if not locked, player is frozen (overlay). Let me gate movement on locked but it doesn't matter. Let me just update always; when not locked, keys aren't processed (well, they could be, but player is behind overlay). Hmm, if I allow WASD when not locked, the player could walk into the overlay. Let me gate on locked.

Actually, simpler: only update player when pointerLocked. When not locked, freeze.

But there's a subtlety: when pointer lock is released (ESC), the player should stay where they are. Freezing handles that. Good.

Let me gate updatePlayer on pointerLocked.

```javascript
if (pointerLocked) updatePlayer(dt);
```

Now updateRaycast: I'll always compute (cheap), and updateOutline based on target. But target outline should only show when locked. Let me compute raycast always, show outline when locked and target exists.

Actually, let me only compute raycast when locked to save a bit, but it's cheap. Let me compute always for simplicity, show outline when locked.

Hmm, but if not locked, camera might be at spawn. Raycast from spawn is fine. Let me just compute always.

Let me write updateOutline:
```javascript
function updateOutline() {
  if (targetBlock && pointerLocked) {
    targetBox.position.set(targetBlock[0] + 0.5, targetBlock[1] + 0.5, targetBlock[2] + 0.5);
    targetBox.visible = true;
  } else {
    targetBox.visible = false;
  }
}
```

Now updatePlayer:
```javascript
function updatePlayer(dt) {
  // input
  let w = 0, d = 0;
  if (keys['w'] || keys['W']) w += 1;
  if (keys['s'] || keys['S']) w -= 1;
  if (keys['d'] || keys['D']) d += 1;
  if (keys['a'] || keys['A']) d -= 1;
  const len = Math.hypot(w, d);
  if (len > 0) { w /= len; d /= len; }
  
  tmpEuler.set(pitch, yaw, 0, 'YXZ');
  const fwd = new THREE.Vector3(0, 0, -1).applyEuler(tmpEuler);
  fwd.y = 0; fwd.normalize();
  const right = new THREE.Vector3(1, 0, 0).applyEuler(tmpEuler);
  right.y = 0; right.normalize();
  
  const speed = 5.5;
  const mvx = (fwd.x * w + right.x * d) * speed;
  const mvz = (fwd.z * w + right.z * d) * speed;
  
  // X
  const nx = player.x + mvx * dt;
  if (!collides(nx, player.y, player.z)) player.x = nx;
  // Z
  const nz = player.z + mvz * dt;
  if (!collides(player.x, player.y, nz)) player.z = nz;
  // Y
  player.vy -= 25 * dt;
  if (player.vy > 10) player.vy = 10; // cap fall (negative)
  if (player.vy < -10) player.vy = -10;
  const ny = player.y + player.vy * dt;
  if (!collides(player.x, ny, player.z)) {
    player.y = ny;
    onGround = false;
  } else {
    if (player.vy < 0) onGround = true;
    player.vy = 0;
  }
  // jump
  if (keys[' '] && onGround) { player.vy = -8.5; onGround = false; }
  
  // camera
  camera.position.set(player.x, player.y + 1.62, player.z);
  camera.rotation.copy(tmpEuler);
  
  // fall respawn
  if (player.y < camera.position.y - 20) respawn();
}
```

Wait, jump velocity 8.5 upward means vy = -8.5 (since -Y is up in Three.js). Let me set player.vy = -8.5 for jump. And gravity vy -= 25*dt makes vy more negative (downward). Wait, gravity should pull down (negative y). vy -= 25*dt → vy becomes negative. Then ny = player.y + vy*dt → decreases. So negative vy = falling down. Jump: vy = -8.5 (up). Cap: vy < -10 → -10 (falling fast). vy > 10 → 10 (rising fast, but jump is -8.5 so won't exceed 10 unless... never). Let me cap vy in [-10, ...]. Actually upward velocity from jump is -8.5, and gravity reduces it. Max upward is -8.5. Max downward capped at -10. So range roughly [-10, 0] mostly. Let me cap vy >= -10 (min) and no upper cap needed. Let me write:
```javascript
if (player.vy < -10) player.vy = -10;
```

Jump: player.vy = -8.5. Good.

Respawn: player.y < camera.y - 20. camera.y = player.y + 1.62. So player.y < player.y + 1.62 - 20 → 0 < 1.62 - 20 → always true?? No wait, that's comparing the same player.y. Let me reconsider. The condition should be: if player falls below a certain absolute height. "Falling below y −20 teleports back to spawn." I think it means if player.y < spawnY - 20, or if player.y < some threshold like -20. Let me interpret: if player.y < -20, respawn. Or relative to spawn. Let me use absolute: if (player.y < -20) respawn(). Actually "below y −20" literally means y < -20. Let me use player.y < -20.

But the player can't go below y=0 due to bedrock (floor at y=0 pushes player up to y~1). Unless there's a cave or the terrain has holes. Actually with bedrock at y=0, player can't fall below y≈1. So the respawn condition y < -20 would never trigger. Hmm.

Wait, but the player could fall into a cave and get stuck, or the terrain might have overhangs. Actually, since y=0 is always stone (unbreakable floor), the player can never go below y≈0. So the fall-respawn is basically dead code unless the player tunnels up... no.

Let me reconsider. Maybe the intent is: if the player falls too far below the terrain/spawn (e.g., fell into a deep hole or out of the world). Given the bedrock floor, this is unusual. But let me implement it as: if player.y < spawnHeight - 20 or player.y < -20. Let me track spawn height and use relative. Actually, let me just do: if (player.y < -20) respawn(). It satisfies the spec literally. Even if rarely triggered, it's there.

Hmm, but actually maybe the player CAN go below 0 if... no, bedrock at y=0. Let me keep player.y < -20 check. It's harmless.

Actually, wait. Let me reconsider the bedrock. y=0 is stone. Player box [y, y+1.8]. If player.y = 0, box [0, 1.8], block [0,1] overlaps → pushed up. So player.y min ≈ 1 (box [1, 2.8], block [0,1] touch at 1, no strict overlap → stands at y=1). So player can't go below y=1. Respawn at y<-20 never triggers. That's fine—it's a safety net.

Let me keep it. respawn sets player to (8, 8, surface+1.5).

Now, respawn:
```javascript
function respawn() {
  let sy = 79;
  while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
  player.x = 8; player.z = 8; player.y = sy + 1.5; player.vy = 0;
}
```

Now updateClouds:
```javascript
function updateClouds(dt) {
  for (const c of clouds) {
    c.position.x += 2.0 * dt;
    if (c.position.x - player.x > 220) c.position.x -= 440;
    if (c.position.x - player.x < -220) c.position.x += 440;
    if (c.position.z - player.z > 220) c.position.z -= 440;
    if (c.position.z - player.z < -220) c.position.z += 440;
  }
}
```

updateWater:
```javascript
function updateWater() {
  water.position.x = player.x;
  water.position.z = player.z;
}
```

Now updateRaycast:
```javascript
function updateRaycast() {
  lookDir.set(0, 0, -1).applyEuler(tmpEuler).normalize();
  raycaster.set(camera.position, lookDir);
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  targetBlock = null;
  placeCell = null;
  if (hits.length > 0 && hits[0].distance <= 6) {
    const h = hits[0];
    const n = h.face.normal;
    targetBlock = [Math.floor(h.point.x - n.x * 0.5), Math.floor(h.point.y - n.y * 0.5), Math.floor(h.point.z - n.z * 0.5)];
    placeCell = [Math.floor(h.point.x + n.x * 0.5), Math.floor(h.point.y + n.y * 0.5), Math.floor(h.point.z + n.z * 0.5)];
  }
}
```

Wait, tmpEuler is set in updatePlayer. If not locked, updatePlayer doesn't run, so tmpEuler is stale (from last frame or initial 0). For raycast when not locked, using stale tmpEuler is fine (outline hidden anyway). But let me set tmpEuler in the raycast too, or just rely on camera.rotation. Actually, let me compute lookDir from camera.rotation directly to be safe:
```javascript
lookDir.set(0, 0, -1).applyEuler(camera.rotation).normalize();
```
camera.rotation is always current (set in updatePlayer, initial 0). Good. Let me use camera.rotation for raycast.

Now, the mousedown handler uses targetBlock/placeCell computed in updateRaycast. Since updateRaycast runs every frame (even when not locked), targetBlock is current. But we only act on mousedown when locked. Good.

Let me make sure updateRaycast runs always. Yes, in animate I call it unconditionally.

Now keys handling:
```javascript
const keys = {};
document.addEventListener('keydown', (e) => {
  keys[e.key.toLowerCase()] = true;
  if (e.key >= '1' && e.key <= '7') {
    selectedBlock = parseInt(e.key, 10);
    updateHotbar();
  }
  if (e.key === ' ') e.preventDefault();
});
document.addEventListener('keyup', (e) => {
  keys[e.key.toLowerCase()] = false;
});
```

Wheel:
```javascript
window.addEventListener('wheel', (e) => {
  if (!pointerLocked) return;
  e.preventDefault();
  selectedBlock += e.deltaY > 0 ? 1 : -1;
  selectedBlock = ((selectedBlock - 1 + 7) % 7) + 1;
  updateHotbar();
}, { passive: false });
```

Hmm, but the wheel event listener on window with passive:false and preventDefault to prevent page scroll. Good. But if not locked, we ignore. Actually, let me allow wheel selection always? The spec says select with mouse wheel. Probably while playing (locked). Let me gate on locked. Actually, let me not gate—allow selecting hotbar anytime. But if not locked, overlay covers screen. Let me gate on locked to avoid confusion. Actually, let me just allow it; harmless. Let me gate on locked for cleanliness.

Hmm, let me not gate wheel—simplest. Actually if not locked, the overlay is on top and wheel would scroll the page (preventDefault stops it) but selectedBlock changes invisibly. Minor. Let me gate on locked.

Mouse move:
```javascript
document.addEventListener('mousemove', (e) => {
  if (!pointerLocked) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  const limit = Math.PI / 2 - 0.01;
  if (pitch > limit) pitch = limit;
  if (pitch < -limit) pitch = -limit;
});
```

Context menu suppression:
```javascript
document.addEventListener('contextmenu', (e) => e.preventDefault());
```

Pointer lock:
```javascript
document.addEventListener('pointerlockchange', () => {
  pointerLocked = (document.pointerLockElement === canvas);
  overlay.style.display = pointerLocked ? 'none' : 'flex';
});
canvas.addEventListener('click', () => {
  if (!pointerLocked) canvas.requestPointerLock();
});
```

Wait, canvas.requestPointerLock requires a user gesture in some browsers. The click handler is a user gesture. Good.

But there's a subtlety: clicking the canvas (not the overlay) also requests lock. Initially overlay covers canvas (z-index 10 vs canvas 0). So first click is on overlay. After lock, overlay hidden, clicks hit canvas. Good.

Now the mousedown for break/place is on canvas. Good.

Let me also prevent default on mousedown to avoid text selection etc. Actually, mousedown on canvas is fine.

Let me also handle the case where e.movementX might not exist if not locked—guarded by pointerLocked check.

Now, let me assemble the CSS and HTML.

Let me reconsider the overlay: it should be clickable to start. z-index above canvas. When locked, display none.

Let me also add a subtle instruction that clicking resumes.

Let me write the complete HTML now.

Let me also double-check the meshing neighbor check. When meshing chunk (cx,cz), for a block at local (lx,lz,y), world coords (wx,wz,y). Neighbor in +x direction: (wx+1, y, wz). getBlock(wx+1, y, wz) reads the neighboring chunk if lx+1 == 16. Good, getBlock handles chunk boundaries.

Let me write buildMesh (done above).

Let me also make sure I don't rebuild meshes that don't exist (return early).

Let me also make sure the chunkMeshes array is properly maintained (add on build, remove on rebuild/remove).

Let me write buildMesh to NOT push to chunkMeshes if mesh already exists; and rebuildSingleMesh removes old first.

Let me restructure: buildMesh creates mesh and pushes to chunkMeshes. rebuildSingleMesh removes old mesh (from scene and chunkMeshes), disposes geo, then calls buildMesh.

Let me write it.

Also, I realize when I generateAndStore at startup and then buildMesh for all, that's fine.

Let me also handle the initial generation timing. Generating 81 chunks and meshing 81 chunks at startup could take ~1-2 seconds. During that time the overlay is showing (pointer not locked). After initWorld(), the overlay is hidden on first click. Actually, the overlay appears and waits for click. But initWorld runs synchronously before the first frame. Since initWorld is called before animate() starts, by the time user clicks, world is ready. Good.

Wait, but initWorld meshes 81 chunks. Meshing involves building BufferGeometry with potentially millions of vertices. Let me estimate: 81 chunks, each maybe 2000-5000 faces, each face 6 vertices (2 triangles * 4? no, 2 triangles = 6 vertices). So 5000 faces * 6 = 30000 vertices per chunk * 81 = 2.4M vertices. Float32BufferAttribute creation for that... should be okay, maybe 0.5-1s. Acceptable for startup.

Hmm, actually let me reduce. Not all 81 chunks will be fully meshed with max faces. Many faces are internal. Exposed faces maybe 1000-3000 per chunk. Let me not worry.

Actually, wait. Let me reconsider building 81 meshes at once. It might cause a noticeable hitch. But it's a one-time cost. Alternatively, I could pre-generate data for a smaller radius and let the frame loop build meshes. But then the player might spawn in air if the spawn chunk isn't meshed yet. Let me pre-generate data for radius 4 and build meshes for radius 2 (25 chunks) at startup, so the player definitely has terrain below and around. Then the frame loop builds the rest.

Actually, simpler: pre-generate data for radius 3 (49 chunks) and build meshes for radius 2 (25 chunks). Player at (8,8) in chunk (0,0), which is meshed. Player sees neighbors. Good.

Let me do: initWorld generates data for radius 3, builds meshes for radius 2. Actually, to be safe for visibility, let me build meshes for radius 2 and generate data for radius 4. The frame loop continues.

Hmm, let me just pre-generate all data for radius 3 and build all meshes for radius 2. Let me code:

```javascript
function initWorld() {
  for (let dz = -3; dz <= 3; dz++)
    for (let dx = -3; dx <= 3; dx++)
      generateAndStore(dx, dz);
  for (let dz = -2; dz <= 2; dz++)
    for (let dx = -2; dx <= 2; dx++)
      buildMesh(dx, dz);
  // spawn
  let sy = 79;
  while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
  player.x = 8; player.z = 8; player.y = sy + 1.5;
}
```

Good. Radius 2 meshed = 25 chunks. Player at center.

Now let me write the whole thing.

Let me reconsider the cameraDir computation and make sure raycasting points in the look direction.

cameraDir = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)).

At yaw=0, pitch=0: cameraDir = (0, 0, -1). Camera looks along -Z. Correct (Three.js default).

Let me verify camera.rotation.set(pitch, yaw, 0, 'YXZ') gives look direction cameraDir. Earlier I derived forward = R*(0,0,-1) = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)). And camera.rotation uses Euler (pitch, yaw, 0) in YXZ order, meaning rotation = Ry(yaw) * Rx(pitch) * Rz(0)? No...

Let me recall: For order 'XYZ', the matrix is R = Rx * Ry * Rz (first rotation rightmost). For order 'YXZ', R = Rz * Rx * Ry. With z=0, Rz=I, so R = Rx * Ry.

Hmm, that changes things. Let me recompute with R = Rx(pitch) * Ry(yaw).

forward = R * (0,0,-1) = Rx(pitch) * Ry(yaw) * (0,0,-1).
Ry(yaw)*(0,0,-1) = (-sin(yaw), 0, -cos(yaw)) [computed earlier].
Rx(pitch) * (-sin(yaw), 0, -cos(yaw)):
Rx = [[1,0,0],[0,cp,-sp],[0,sp,cp]]
- x: -sin(yaw)
- y: cp*0 - sp*(-cos(yaw)) = sp*cos(yaw)
- z: sp*0 + cp*(-cos(yaw)) = -cp*cos(yaw)
So forward = (-sin(yaw), sin(pitch)*cos(yaw), -cos(pitch)*cos(yaw)).

Hmm, that's different from before. The difference is whether pitch affects y via cos(pitch) or the yaw. Let me just test empirically in my head... this is getting confusing. Let me instead compute the forward vector using camera.getWorldDirection() which is unambiguous.

Actually, the cleanest: after setting camera.position and camera.rotation, compute forward via:
```javascript
const dir = new THREE.Vector3(0, 0, -1).applyEuler(camera.rotation).normalize();
```

applyEuler applies the rotation to the vector. This gives the exact look direction. Let me use that. It's robust.

```javascript
lookDir.set(0, 0, -1).applyEuler(camera.rotation).normalize();
raycaster.set(camera.position, lookDir);
```

And for movement, I need horizontal forward/right. Let me compute:
```javascript
const forwardH = new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(0, yaw, 0, 'YXZ'));
```
Hmm, but I need to be careful about yaw sign. Let me just derive horizontal movement from yaw directly, using the known convention.

Actually, let me define yaw such that moving W moves the camera in the direction it's looking (horizontally). Let me compute the horizontal forward from camera.rotation:
```javascript
const fwd = new THREE.Vector3(0, 0, -1).applyEuler(camera.rotation);
fwd.y = 0; fwd.normalize();
const right = new THREE.Vector3(1, 0, 0).applyEuler(camera.rotation);
right.y = 0; right.normalize();
```

Then movement = fwd * wInput + right * dInput. This is robust and matches the camera orientation exactly. Let me use this in updatePlayer. But computing Euler applications each frame is a bit costly but negligible.

Actually, applyEuler on a fresh Euler each frame is fine.

Wait, but I set camera.rotation AFTER computing movement? Let me set camera rotation first, then derive fwd/right from it. Or derive from yaw/pitch directly. Let me set camera.rotation first in updatePlayer, then compute fwd/right. Actually movement doesn't depend on camera position, only rotation. Let me compute fwd/right from camera.rotation at the start of updatePlayer (camera.rotation is set from previous frame or initial). Let me just compute from yaw/pitch using applyEuler with a cached Euler.

Let me use a cached Euler object:
```javascript
const tmpEuler = new THREE.Euler(0, 0, 0, 'YXZ');
```
In updatePlayer:
```javascript
tmpEuler.set(pitch, yaw, 0, 'YXZ');
const fwd = new THREE.Vector3(0,0,-1).applyEuler(tmpEuler);
fwd.y = 0; fwd.normalize();
const right = new THREE.Vector3(1,0,0).applyEuler(tmpEuler);
right.y = 0; right.normalize();
```

Then mvx = (fwd.x * w + right.x * d) * speed, etc.

And camera.rotation.copy(tmpEuler) or set(pitch, yaw, 0, 'YXZ').

And lookDir for raycast:
```javascript
lookDir.set(0,0,-1).applyEuler(tmpEuler).normalize();
```

Good, reuse tmpEuler.

Let me put this together in updatePlayer.

Now, let me reconsider: initial yaw/pitch = 0. fwd = (0,0,-1). Moving W moves -Z. Fine.

Let me now write the complete file.

Let me also add a subtle detail: the directional light should perhaps follow or be static. Static is fine.

Let me also make sure water doesn't render opaque—it's transparent. MeshLambertMaterial with transparent:true, opacity 0.6, side DoubleSide.

Now, let me also double check: the water plane is 500x500 at y=14.3. Where terrain H <= 14 (roughly), water appears as lakes/beaches. Since water is a flat plane at 14.3, any terrain below 14.3 is "underwater" visually. Beaches (sand, H<=16) near water level will have water up to ~14.3. Good.

But the water plane at 14.3 might intersect terrain blocks (rendering through them). Since it's transparent and behind, it's fine visually. The spec says "water is visual only." Good.

Now, let me write it all out. Let me be thorough.

Actually, let me reconsider one thing about the collision and the `collides` function performance. It's called 3 times per frame, each iterating over a small voxel range. Fine.

Let me also make sure getBlock handles y correctly. y from 0 to 79. For y=0, that's the unbreakable stone. For y>79 or y<0, return 0.

Let me write getBlock:
```javascript
function getBlock(x, y, z) {
  if (y < 0 || y > 79) return 0;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk) return 0;
  const lx = x - cx * 16;
  const lz = z - cz * 16;
  return chunk.data[y * 256 + lz * 16 + lx];
}
```

setBlock:
```javascript
function setBlock(x, y, z, id) {
  if (y < 0 || y > 79) return;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk) return;
  const lx = x - cx * 16;
  const lz = z - cz * 16;
  chunk.data[y * 256 + lz * 16 + lx] = id;
}
```

Good.

Now, let me reconsider the meshing neighbor check. When meshing chunk (cx,cz), for a block at local (lx,lz,y), world coords (wx,wz,y). Neighbor in +x direction: (wx+1, y, wz). getBlock(wx+1, y, wz) reads the neighboring chunk if lx+1 == 16. Good, getBlock handles chunk boundaries.

Let me write buildMesh:
```javascript
const BLOCK_COLORS = [null, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];

function buildMesh(cx, cz) {
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk || !chunk.data) return;
  const data = chunk.data;
  const pos = [], norm = [], col = [];
  for (let y = 0; y < 80; y++) {
    for (let lz = 0; lz < 16; lz++) {
      for (let lx = 0; lx < 16; lx++) {
        const id = data[y * 256 + lz * 16 + lx];
        if (id === 0) continue;
        const wx = cx * 16 + lx;
        const wz = cz * 16 + lz;
        const c = BLOCK_COLORS[id];
        const r = ((c >> 16) & 255) / 255;
        const g = ((c >> 8) & 255) / 255;
        const b = (c & 255) / 255;
        for (let f = 0; f < 6; f++) {
          const face = FACES[f];
          const nx = wx + face.n[0];
          const ny = y + face.n[1];
          const nz = wz + face.n[2];
          if (getBlock(nx, ny, nz) === 0) {
            const s = face.s;
            for (let vi = 0; vi < 4; vi++) {
              const vt = face.v[vi];
              pos.push(wx + vt[0], y + vt[1], wz + vt[2]);
              norm.push(face.n[0], face.n[1], face.n[2]);
              col.push(r * s, g * s, b * s);
            }
          }
        }
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(norm, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  const mesh = new THREE.Mesh(geo, sharedMaterial);
  mesh.position.set(0, 0, 0);
  chunk.mesh = mesh;
  chunk.geo = geo;
  scene.add(mesh);
  chunkMeshes.push(mesh);
}
```

rebuildSingleMesh:
```javascript
function rebuildSingleMesh(cx, cz) {
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk) return;
  if (chunk.mesh) {
    scene.remove(chunk.mesh);
    const idx = chunkMeshes.indexOf(chunk.mesh);
    if (idx >= 0) chunkMeshes.splice(idx, 1);
    chunk.geo.dispose();
    chunk.mesh = null;
    chunk.geo = null;
  }
  buildMesh(cx, cz);
}
```

rebuildChunkEdit:
```javascript
function rebuildChunkEdit(x, z) {
  const cx = Math.floor(x / 16), cz = Math.floor(z / 16);
  rebuildSingleMesh(cx, cz);
  const lx = x - cx * 16, lz = z - cz * 16;
  if (lx === 0) rebuildSingleMesh(cx - 1, cz);
  else if (lx === 15) rebuildSingleMesh(cx + 1, cz);
  if (lz === 0) rebuildSingleMesh(cx, cz - 1);
  else if (lz === 15) rebuildSingleMesh(cx, cz + 1);
}
```

Now the world update loop. Let me refine to avoid rebuilding meshes that already exist.

In the mesh-build loop, I check `!chunks.get(key).mesh`. Good.

In the removal loop, I dispose and delete. Good.

Now let me also make sure that when a chunk's mesh is built, subsequent frames don't rebuild it (the `!mesh` check). Good.

Let me also handle the case where mesh building is limited to 2 per frame but there are many chunks needing meshes. That's fine, it builds gradually.

Now, one concern: the mesh-build loop iterates dz/dx from -4 to 4. For each chunk within 4 that lacks a mesh, if 4 neighbors have data, build. But the 4 neighbors' data existence: since we generate within 5 (max 4/frame), the neighbors might not have data yet on the first frames. But over several frames, data propagates. Since generation is 4/frame within radius 5, and meshing is 2/frame within radius 4 requiring neighbor data, it converges over ~30-60 frames as the player moves. At startup, we pre-build radius 2, so it's fine.

Hmm, but there's a subtle issue: the mesh-build loop requires ALL 4 orthogonal neighbors to have data. If a chunk at the edge of the generated region has a neighbor without data, it won't be meshed until that neighbor generates. Since generation radius (5) > meshing radius (4), the neighbors within radius 4+1=5 will eventually all have data. So convergence happens. Good.

Let me now also reconsider: should the mesh-build check neighbors' data or mesh? Spec: "build meshes for chunks within 4 chunks whose 4 neighbors already have data". So neighbors' data. Good, I check chunks.has for neighbors (which implies data exists since generateAndStore adds data immediately).

Let me write generateAndStore to add to map with data immediately.

Now let me write the final file.

Let me also add the water and clouds to the scene.

Let me also make sure I set renderer to handle alpha or not. Default opaque. Background color set on scene.

Let me also consider pixel ratio for performance: Math.min(devicePixelRatio, 2).

Let me write the animate loop with delta time.

```javascript
let lastTime = performance.now();
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  let dt = (now - lastTime) / 1000;
  lastTime = now;
  if (dt > 0.05) dt = 0.05;
  if (dt < 0) dt = 0;
  
  if (pointerLocked) updatePlayer(dt);
  updateWorldGeneration();
  updateRaycast();
  updateClouds(dt);
  updateWater();
  updateOutline();
  
  renderer.render(scene, camera);
}
requestAnimationFrame(animate);
```

Wait, updatePlayer should only run when pointerLocked? The spec says movement via WASD. If pointer not locked, player shouldn't move. But gravity/collision... Let me only update player when locked. Actually, if not locked, the overlay covers the screen, so player state doesn't matter visually. But to be safe, let me update player physics only when locked. Actually, let me always apply gravity? No—if not locked, player is frozen (overlay). Let me gate movement on locked but it doesn't matter. Let me just update player when locked.

Actually, let me always apply gravity? No—if not locked, player is frozen (overlay). Let me gate on locked.

Actually, simpler: only update player when pointerLocked. When not locked, freeze.

But there's a subtlety: when pointer lock is released (ESC), the player should stay where they are. Freezing handles that. Good.

Let me gate updatePlayer on pointerLocked.

```javascript
if (pointerLocked) updatePlayer(dt);
```

Now updateRaycast: I'll always compute (cheap), and updateOutline based on target. But target outline should only show when locked. Let me compute raycast always, show outline when locked and target exists.

Actually, let me only compute raycast when locked to save a bit, but it's cheap. Let me compute always for simplicity, show outline when locked.

Hmm, but if not locked, camera might be at spawn. Raycast from spawn is fine. Let me just compute always.

Let me write updateOutline:
```javascript
function updateOutline() {
  if (targetBlock && pointerLocked) {
    targetBox.position.set(targetBlock[0] + 0.5, targetBlock[1] + 0.5, targetBlock[2] + 0.5);
    targetBox.visible = true;
  } else {
    targetBox.visible = false;
  }
}
```

Now updatePlayer:
```javascript
function updatePlayer(dt) {
  // input
  let w = 0, d = 0;
  if (keys['w'] || keys['W']) w += 1;
  if (keys['s'] || keys['S']) w -= 1;
  if (keys['d'] || keys['D']) d += 1;
  if (keys['a'] || keys['A']) d -= 1;
  const len = Math.hypot(w, d);
  if (len > 0) { w /= len; d /= len; }
  
  tmpEuler.set(pitch, yaw, 0, 'YXZ');
  const fwd = new THREE.Vector3(0, 0, -1).applyEuler(tmpEuler);
  fwd.y = 0; fwd.normalize();
  const right = new THREE.Vector3(1, 0, 0).applyEuler(tmpEuler);
  right.y = 0; right.normalize();
  
  const speed = 5.5;
  const mvx = (fwd.x * w + right.x * d) * speed;
  const mvz = (fwd.z * w + right.z * d) * speed;
  
  // X
  const nx = player.x + mvx * dt;
  if (!collides(nx, player.y, player.z)) player.x = nx;
  // Z
  const nz = player.z + mvz * dt;
  if (!collides(player.x, player.y, nz)) player.z = nz;
  // Y
  player.vy -= 25 * dt;
  if (player.vy < -10) player.vy = -10;
  const ny = player.y + player.vy * dt;
  if (!collides(player.x, ny, player.z)) {
    player.y = ny;
    onGround = false;
  } else {
    if (player.vy < 0) onGround = true;
    player.vy = 0;
  }
  // jump
  if (keys[' '] && onGround) { player.vy = -8.5; onGround = false; }
  
  // camera
  camera.position.set(player.x, player.y + 1.62, player.z);
  camera.rotation.copy(tmpEuler);
  
  // fall respawn
  if (player.y < -20) respawn();
}
```

Wait, jump velocity 8.5 upward means vy = -8.5 (since -Y is up in Three.js). Let me set player.vy = -8.5 for jump. And gravity vy -= 25*dt makes vy more negative (downward). Wait, gravity should pull down (negative y). vy -= 25*dt → vy becomes negative. Then ny = player.y + vy*dt → decreases. So negative vy = falling down. Jump: vy = -8.5 (up). Cap: vy < -10 → -10 (falling fast). vy > 10 → 10 (rising fast, but jump is -8.5 so won't exceed 10 unless... never). Let me cap vy in [-10, ...]. Actually upward velocity from jump is -8.5, and gravity reduces it. Max upward is -8.5. Max downward capped at -10. So range roughly [-10, 0] mostly. Let me cap vy >= -10 (min) and no upper cap needed. Let me write:
```javascript
if (player.vy < -10) player.vy = -10;
```

Jump: player.vy = -8.5. Good.

Respawn: player.y < camera.y - 20. camera.y = player.y + 1.62. So player.y < player.y + 1.62 - 20 → 0 < 1.62 - 20 → always true?? No wait, that's comparing the same player.y. Let me reconsider. The condition should be: if player falls below a certain absolute height. "Falling below y −20 teleports back to spawn." I think it means if player.y < spawnY - 20, or if player.y < some threshold like -20. Let me interpret: if player.y < -20, respawn. Or relative to spawn. Let me use absolute: if (player.y < -20) respawn(). Actually "below y −20" literally means y < -20. Let me use player.y < -20.

But the player can't go below y=0 due to bedrock (floor at y=0 pushes player up to y~1). Unless there's a cave or the terrain has overhangs. Actually with bedrock at y=0, player can't fall below y≈1. So the respawn condition y < -20 would never trigger. Hmm.

Wait, but the player could fall into a cave and get stuck, or the terrain might have overhangs. Actually, since y=0 is always stone (unbreakable floor), the player can never go below y≈0. So the fall-respawn is basically dead code unless the player tunnels up... no.

Let me reconsider. Maybe the intent is: if the player falls too far below the terrain/spawn (e.g., fell into a deep hole or out of the world). Given the bedrock floor, this is unusual. But let me implement it as: if player.y < spawnHeight - 20 or player.y < -20. Let me track spawn height and use relative. Actually, let me just do: if (player.y < -20) respawn(). It satisfies the spec literally. Even if rarely triggered, it's there.

Hmm, but actually maybe the player CAN go below 0 if... no, bedrock at y=0. Let me keep player.y < -20 check. It's harmless.

Actually, wait. Let me reconsider the bedrock. y=0 is stone. Player box [y, y+1.8]. If player.y = 0, box [0, 1.8], block [0,1] overlaps → pushed up. So player.y min ≈ 1 (box [1, 2.8], block [0,1] touch at 1, no strict overlap → stands at y=1). So player can't go below y=1. Respawn at y<-20 never triggers. That's fine—it's a safety net.

Let me keep it. respawn sets player to (8, 8, surface+1.5).

Now, respawn:
```javascript
function respawn() {
  let sy = 79;
  while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
  player.x = 8; player.z = 8; player.y = sy + 1.5; player.vy = 0;
}
```

Now updateClouds:
```javascript
function updateClouds(dt) {
  for (const c of clouds) {
    c.position.x += 2.0 * dt;
    if (c.position.x - player.x > 220) c.position.x -= 440;
    if (c.position.x - player.x < -220) c.position.x += 440;
    if (c.position.z - player.z > 220) c.position.z -= 440;
    if (c.position.z - player.z < -220) c.position.z += 440;
  }
}
```

updateWater:
```javascript
function updateWater() {
  water.position.x = player.x;
  water.position.z = player.z;
}
```

Now updateRaycast:
```javascript
function updateRaycast() {
  lookDir.set(0, 0, -1).applyEuler(camera.rotation).normalize();
  raycaster.set(camera.position, lookDir);
  const hits = raycaster.intersectObjects(chunkMeshes, false);
  targetBlock = null;
  placeCell = null;
  if (hits.length > 0 && hits[0].distance <= 6) {
    const h = hits[0];
    const n = h.face.normal;
    targetBlock = [Math.floor(h.point.x - n.x * 0.5), Math.floor(h.point.y - n.y * 0.5), Math.floor(h.point.z - n.z * 0.5)];
    placeCell = [Math.floor(h.point.x + n.x * 0.5), Math.floor(h.point.y + n.y * 0.5), Math.floor(h.point.z + n.z * 0.5)];
  }
}
```

Wait, tmpEuler is set in updatePlayer. If not locked, updatePlayer doesn't run, so tmpEuler is stale (from last frame or initial 0). For raycast when not locked, using stale tmpEuler is fine (outline hidden anyway). But let me set tmpEuler in the raycast too, or just rely on camera.rotation. Actually, let me compute lookDir from camera.rotation directly to be safe:
```javascript
lookDir.set(0, 0, -1).applyEuler(camera.rotation).normalize();
```
camera.rotation is always current (set in updatePlayer, initial 0). Good. Let me use camera.rotation for raycast.

Now, the mousedown handler uses targetBlock/placeCell computed in updateRaycast. Since updateRaycast runs every frame (even when not locked), targetBlock is current. But we only act on mousedown when locked. Good.

Let me make sure updateRaycast runs always. Yes, in animate I call it unconditionally.

Now, keys handling:
```javascript
const keys = {};
document.addEventListener('keydown', (e) => {
  keys[e.key.toLowerCase()] = true;
  if (e.key >= '1' && e.key <= '7') {
    selectedBlock = parseInt(e.key, 10);
    updateHotbar();
  }
  if (e.key === ' ') e.preventDefault();
});
document.addEventListener('keyup', (e) => {
  keys[e.key.toLowerCase()] = false;
});
```

Wheel:
```javascript
window.addEventListener('wheel', (e) => {
  if (!pointerLocked) return;
  e.preventDefault();
  selectedBlock += e.deltaY > 0 ? 1 : -1;
  selectedBlock = ((selectedBlock - 1 + 7) % 7) + 1;
  updateHotbar();
}, { passive: false });
```

Hmm, but the wheel event listener on window with passive:false and preventDefault to prevent page scroll. Good. But if not locked, we ignore. Actually, let me allow wheel selection always? The spec says select with mouse wheel. Probably while playing (locked). Let me gate on locked. Actually, let me not gate—allow selecting hotbar anytime. But if not locked, overlay covers screen. Let me gate on locked to avoid confusion. Actually, let me just allow it; harmless. Let me gate on locked for cleanliness.

Hmm, let me not gate wheel—simplest. Actually if not locked, the overlay is on top and wheel would scroll the page (preventDefault stops it) but selectedBlock changes invisibly. Minor. Let me gate on locked.

Mouse move:
```javascript
document.addEventListener('mousemove', (e) => {
  if (!pointerLocked) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  const limit = Math.PI / 2 - 0.01;
  if (pitch > limit) pitch = limit;
  if (pitch < -limit) pitch = -limit;
});
```

Context menu suppression:
```javascript
document.addEventListener('contextmenu', (e) => e.preventDefault());
```

Pointer lock:
```javascript
document.addEventListener('pointerlockchange', () => {
  pointerLocked = (document.pointerLockElement === canvas);
  overlay.style.display = pointerLocked ? 'none' : 'flex';
});
canvas.addEventListener('click', () => {
  if (!pointerLocked) canvas.requestPointerLock();
});
```

Wait, canvas.requestPointerLock requires a user gesture in some browsers. The click handler is a user gesture. Good.

But there's a subtlety: clicking the canvas (not the overlay) also requests lock. Initially overlay covers canvas (z-index 10 vs canvas 0). So first click is on overlay. After lock, overlay hidden, clicks hit canvas. Good.

Now the mousedown for break/place is on canvas. Good.

Let me also prevent default on mousedown to avoid text selection etc. Actually, mousedown on canvas is fine.

Let me also handle the case where e.movementX might not exist if not locked—guarded by pointerLocked check.

Now, let me assemble the CSS and HTML.

Let me reconsider the overlay: it should be clickable to start. z-index above canvas. When locked, display none.

Let me also add a subtle instruction that clicking resumes.

Let me write the complete HTML now.

Let me also double-check the meshing neighbor check. When meshing chunk (cx,cz), for a block at local (lx,lz,y), world coords (wx,wz,y). Neighbor in +x direction: (wx+1, y, wz). getBlock(wx+1, y, wz) reads the neighboring chunk if lx+1 == 16. Good, getBlock handles chunk boundaries.

Let me write buildMesh (done above).

Let me also make sure I don't rebuild meshes that don't exist (return early).

Let me also make sure the chunkMeshes array is properly maintained (add on build, remove on rebuild/remove).

Let me write buildMesh to NOT push to chunkMeshes if mesh already exists; and rebuildSingleMesh removes old first.

Let me restructure: buildMesh creates mesh and pushes to chunkMeshes. rebuildSingleMesh removes old mesh (from scene and chunkMeshes), disposes geo, then calls buildMesh.

Let me write it.

Also, I realize when I generateAndStore at startup and then buildMesh for all, that's fine.

Let me also handle the initial generation timing. Generating 81 chunks and meshing 81 chunks at startup could take ~1-2 seconds. During that time the overlay is showing (pointer not locked). After initWorld(), the overlay is hidden on first click. Actually, the overlay appears and waits for click. But initWorld runs synchronously before the first frame. Since initWorld is called before animate() starts, by the time user clicks, world is ready. Good.

Wait, but initWorld meshes 81 chunks. Meshing involves building BufferGeometry with potentially millions of vertices. Let me estimate: 81 chunks, each maybe 2000-5000 faces, each face 6 vertices (2 triangles * 4? no, 2 triangles = 6 vertices). So 5000 faces * 6 = 30000 vertices per chunk * 81 = 2.4M vertices. Float32BufferAttribute creation for that... should be okay, maybe 0.5-1s. Acceptable for startup.

Hmm, actually let me reduce. Not all 81 chunks will be fully meshed with max faces. Many faces are internal. Exposed faces maybe 1000-3000 per chunk. Let me not worry.

Actually, wait. Let me reconsider building 81 meshes at once. It might cause a noticeable hitch. But it's a one-time cost. Alternatively, I could pre-generate data for a smaller radius and let the frame loop build meshes. But then the player might spawn in air if the spawn chunk isn't meshed yet. Let me pre-generate data for radius 4 and build meshes for radius 2 (25 chunks) at startup, so the player definitely has terrain below and around. Then the frame loop builds the rest.

Actually, simpler: pre-generate data for radius 3 (49 chunks) and build meshes for radius 2 (25 chunks). Player at (8,8) in chunk (0,0), which is meshed. Player sees neighbors. Good.

Let me do: initWorld generates data for radius 3, builds meshes for radius 2. Actually, to be safe for visibility, let me build meshes for radius 2 and generate data for radius 4. The frame loop continues.

Hmm, let me just pre-generate all data for radius 3 and build all meshes for radius 2. Let me code:

```javascript
function initWorld() {
  for (let dz = -3; dz <= 3; dz++)
    for (let dx = -3; dx <= 3; dx++)
      generateAndStore(dx, dz);
  for (let dz = -2; dz <= 2; dz++)
    for (let dx = -2; dx <= 2; dx++)
      buildMesh(dx, dz);
  // spawn
  let sy = 79;
  while (sy > 0 && getBlock(8, sy, 8) === 0) sy--;
  player.x = 8; player.z = 8; player.y = sy + 1.5;
}
```

Good. Radius 2 meshed = 25 chunks. Player at center.

Now let me write the whole thing.

Let me reconsider the cameraDir computation and make sure raycasting points in the look direction.

cameraDir = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)).

At yaw=0, pitch=0: cameraDir = (0, 0, -1). Camera looks along -Z. Correct (Three.js default).

Let me verify camera.rotation.set(pitch, yaw, 0, 'YXZ') gives look direction cameraDir. Earlier I derived forward = R*(0,0,-1) = (-sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch)). And camera.rotation uses Euler (pitch, yaw, 0) in YXZ order, meaning rotation = Ry(yaw) * Rx(pitch) * Rz(0)? No...

Let me recall: For order 'XYZ', the matrix is R = Rx * Ry * Rz (first rotation rightmost). For order 'YXZ', R = Rz * Rx * Ry. With z=0, Rz=I, so R = Rx * Ry.

Hmm, that changes things. Let me recompute with R = Rx(pitch) * Ry(yaw).

forward = R * (0,0,-1) = Rx(pitch) * Ry(yaw) * (0,0,-1).
Ry(yaw)*(0,0,-1) = (-sin(yaw), 0, -cos(yaw)) [computed earlier].
Rx(pitch) * (-sin(yaw), 0, -cos(yaw)):
Rx = [[1,0,0],[0,cp,-sp],[0,sp,cp]]
- x: -sin(yaw)
- y: cp*0 - sp*(-cos(yaw)) = sp*cos(yaw)
- z: sp*0 + cp*(-cos(yaw)) = -cp*cos(yaw)
So forward = (-sin(yaw), sin(pitch)*cos(yaw), -cos(pitch)*cos(yaw)).

Hmm, that's different from before. The difference is whether pitch affects y via cos(pitch) or the yaw. Let me just test empirically in my head... this is getting confusing. Let me instead compute the forward vector using camera.getWorldDirection() which is unambiguous.

Actually, the cleanest: after setting camera.position and camera.rotation, compute forward via:
```javascript
const dir = new THREE.Vector3(0, 0, -1).applyEuler(camera.rotation).normalize();
```

applyEuler applies the rotation to the vector. This gives the exact look direction. Let me use that. It's robust.

```javascript
lookDir.set(0, 0, -1).applyEuler(camera.rotation).normalize();
raycaster.set(camera.position, lookDir);
```

And for movement, I need horizontal forward/right. Let me compute:
```javascript
const forwardH = new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(0, yaw, 0, 'YXZ'));
```
Hmm, but I need to be careful about yaw sign. Let me just derive horizontal movement from yaw directly, using the known convention.

Actually, let me define yaw such that moving W moves the camera in the direction it's looking (horizontally). Let me compute the horizontal forward from camera.rotation:
```javascript
const fwd = new THREE.Vector3(0, 0, -1).applyEuler(camera.rotation);
fwd.y = 0; fwd.normalize();
const right = new THREE.Vector3(1, 0, 0).applyEuler(camera.rotation);
right.y = 0; right.normalize();
```

Then movement = fwd * wInput + right * dInput. This is robust and matches the camera orientation exactly. Let me use this in updatePlayer. But computing Euler applications each frame is a bit costly but negligible.

Actually, applyEuler on a fresh Euler each frame is fine.

Wait, but I set camera.rotation AFTER computing movement? Let me set camera rotation first, then derive fwd/right from it. Or derive from yaw/pitch directly. Let me set camera.rotation first in updatePlayer, then compute fwd/right. Actually movement doesn't depend on camera position, only rotation. Let me compute fwd/right from camera.rotation at the start of updatePlayer (camera.rotation is set from previous frame or initial). Let me just compute from yaw/pitch using applyEuler with a cached Euler.

Let me use a cached Euler object:
```javascript
const tmpEuler = new THREE.Euler(0, 0, 0, 'YXZ');
```
In updatePlayer:
```javascript
tmpEuler.set(pitch, yaw, 0, 'YXZ');
const fwd = new THREE.Vector3(0,0,-1).applyEuler(tmpEuler);
fwd.y = 0; fwd.normalize();
const right = new THREE.Vector3(1,0,0).applyEuler(tmpEuler);
right.y = 0; right.normalize();
```

Then mvx = (fwd.x * w + right.x * d) * speed, etc.

And camera.rotation.copy(tmpEuler) or set(pitch, yaw, 0, 'YXZ').

And lookDir for raycast:
```javascript
lookDir.set(0,0,-1).applyEuler(tmpEuler).normalize();
```

Good, reuse tmpEuler.

Let me put this together in updatePlayer.

Now, let me reconsider: initial yaw/pitch = 0. fwd = (0,0,-1). Moving W moves -Z. Fine.

Let me now write the complete file.

Let me also add a subtle detail: the directional light should perhaps follow or be static. Static is fine.

Let me also make sure water doesn't render opaque—it's transparent. MeshLambertMaterial with transparent:true, opacity 0.6, side DoubleSide.

Now, let me also double check: the water plane is 500x500 at y=14.3. Where terrain H <= 14 (roughly), water appears as lakes/beaches. Since water is a flat plane at 14.3, any terrain below 14.3 is "underwater" visually. Beaches (sand, H<=16) near water level will have water up to ~14.3. Good.

But the water plane at 14.3 might intersect terrain blocks (rendering through them). Since it's transparent and behind, it's fine visually. The spec says "water is visual only." Good.

Now, let me write it all out. Let me be thorough.

Actually, let me reconsider one thing about the collision and the `collides` function performance. It's called 3 times per frame, each iterating over a small voxel range. Fine.

Let me also make sure getBlock handles y correctly. y from 0 to 79. For y=0, that's the unbreakable stone. For y>79 or y<0, return 0.

Let me write getBlock:
```javascript
function getBlock(x, y, z) {
  if (y < 0 || y > 79) return 0;
  const cx = Math.floor(x / 16);
  const cz = Math.floor(z / 16);
  const chunk = chunks.get(cx + "," + cz);
  if (!chunk) return 0;
  const lx = x - cx * 16;
  const lz = z - cz * 16;
  return chunk.data[y * 256