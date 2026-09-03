This is a complex task. I need to build a complete Minecraft-style voxel game in a single HTML file using Three.js r128. Let me carefully go through all the requirements and build this step by step.

Let me plan out the structure:

1. **HTML/CSS structure**: Fullscreen canvas, start overlay, crosshair, hotbar
2. **Three.js setup**: Scene, camera, lights, sky color, fog
3. **Chunk system**: 16x16x80 chunks, stored in a Map
4. **Block helpers**: Global read/write using chunk coordinates
5. **Terrain generation**: Value noise, fractal noise, caves, trees
6. **Meshing**: One BufferGeometry per chunk with face culling
7. **Player physics**: Collision, gravity, movement
8. **Break/place**: Raycasting, block editing
9. **UI**: Hotbar, crosshair, start overlay

Let me write this carefully.

Key implementation details:

**Chunk storage:**
- Chunks map: key "cx,cz", value { blocks: Uint8Array, mesh }
- Block helpers use chunk = floor(world/16), local = world - chunk*16

**Block IDs:**
- 0 air, 1 grass, 2 dirt, 3 stone, 4 sand, 5 wood, 6 leaves, 7 snow

**Meshing logic:**
- For each non-air block, check 6 neighbors
- If neighbor is air, add face
- Use world coordinates for vertices, mesh at origin
- Fake lighting: top 1.0, side 0.8, bottom 0.55

**Terrain generation:**
- Value noise with integer hash
- Smoothed 2D noise via bilinear interpolation with smoothstep
- 4 octaves fractal noise
- 3D version for caves
- Column height formula
- Column fill logic
- Caves
- Trees

**Player physics:**
- PerspectiveCamera fov 75, far 400
- Rotation YXZ
- Box: half-width 0.3, height 1.8, eye 1.62
- Spawn above terrain at x=8, z=8
- Gravity 25, jump velocity 8.5, WASD 5.5 m/s
- Axis-separated collision
- Fall below -20 teleports back

**Break/place:**
- Raycast from camera center max distance 6
- Break target = floor(p - n*0.5)
- Place cell = floor(p + n*0.5)
- Wireframe outline box
- Left click break, right click place
- Rebuild edited chunk + neighbor if on border

**Sky/clouds/water:**
- Sky blue 0x87ceeb, fog 40 to 110
- Ambient 0.65, directional 0.8
- ~25 clouds at height 90, drifting, wrapping
- Water plane at 14.3

Let me now write the complete code.

Let me think about the noise implementation carefully since it's deterministic.

```javascript
function hash2(ix, iy) {
    // integer hash giving 0-1
    let h = ix * 374761393 + iy * 537413461; // large prime multipliers
    h = (h ^ (h >> 13)) * 1274269271; // xor-shift
    h = (h ^ (h >> 16)) >>> 0;
    return h / 4294967296;
}

function noise2(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    // corners
    const v00 = hash2(ix, iy);
    const v10 = hash2(ix+1, iy);
    const v01 = hash2(ix, iy+1);
    const v11 = hash2(ix+1, iy+1);
    const u = fx*fx*(3-4*fx+2*fx*fx); // smoothstep
    // bilinear
    const a = v00 + u*(v10 - v00);
    const b = v01 + u*(v11 - v01);
    return a + (b-a)*u; // hmm wait this isn't right
}
```

Wait, bilinear interpolation should interpolate both axes. Let me redo:

```javascript
function noise2(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const v00 = hash2(ix, iy);
    const v10 = hash2(ix+1, iy);
    const v01 = hash2(ix, iy+1);
    const v11 = hash2(ix+1, iy+1);
    const u = fx*fx*(3-4*fx+2*fx*fx);
    const v = fy*fy*(3-4*fy+2*fy*fy);
    const x0 = v00*(1-u) + v10*u;
    const x1 = v01*(1-u) + v11*u;
    return x0*(1-v) + x1*v;
}
```

Then fractal:
```javascript
function fractal2(x, y) {
    let sum = 0, amp = 1, freq = 1, norm = 0;
    for (let i = 0; i < 4; i++) {
        sum += noise2(x*freq, y*freq) * amp;
        norm += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return sum / norm;
}
```

For 3D noise for caves:
```javascript
function hash3(ix, iy, iz) {
    let h = ix*374761393 + iy*537413461 + iz*668265263;
    h = (h ^ (h >> 13)) * 1274269271;
    h = (h ^ (h >> 16)) >>> 0;
    return h / 4294967296;
}

function noise3(x, y, z) {
    // similar but 3D
    ...
}
```

Actually for 3D noise, bilinear interpolation in 3D is more complex. Let me implement a proper 3D value noise.

```javascript
function noise3(x, y, z) {
    const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    const fx = x - ix, fy = y - iy, fz = z - iz;
    const v000 = hash3(ix, iy, iz);
    const v100 = hash3(ix+1, iy, iz);
    const v010 = hash3(ix, iy+1, iz);
    const v110 = hash3(ix+1, iy+1, iz);
    const v001 = hash3(ix, iy, iz+1);
    const v101 = hash3(ix+1, iy, iz+1);
    const v011 = hash3(ix, iy+1, iz+1);
    const v111 = hash3(ix+1, iy+1, iz+1);
    const u = fx*fx*(3-4*fx+2*fx*fx);
    const v = fy*fy*(3-4*fy+2*fy*fy);
    const w = fz*fz*(3-4*fz+2*fz*fz);
    const x00 = v000*(1-u) + v100*u;
    const x10 = v010*(1-u) + v110*u;
    const x01 = v001*(1-u) + v101*u;
    const x11 = v011*(1-u) + v111*u;
    const y0 = x00*(1-v) + x10*v;
    const y1 = x01*(1-v) + x11*v;
    return y0*(1-w) + y1*w;
}
```

Now let me think about the terrain generation function. It needs to populate a chunk's block array.

Chunk coordinates cx, cz. Local x from cx*16 to cx*16+15, etc.

```javascript
function generateChunkData(cx, cz, blocks) {
    for (let lx = 0; lx < 16; lx++) {
        for (let lz = 0; lz < 16; lz++) {
            const wx = cx*16 + lx;
            const wz = cz*16 + lz;
            const m = fractal2(wx*0.004, wz*0.004);
            const h = fractal2(wx*0.02, wz*0.02);
            const H = Math.floor(5 + m*m*58 + h*10);
            // fill
            for (let y = 0; y <= 79; y++) {
                let id = 0;
                if (y === 0) id = 3; // unbreakable stone
                else if (y < H-3) id = 3; // stone
                else if (y < H-2 || y < H) {
                    // 3 layers under surface
                    if (H <= 16) id = 4; // sand
                    else if (H >= 37) id = 3; // stone
                    else id = 2; // dirt
                } else {
                    // surface
                    if (H >= 46) id = 7; // snow
                    else if (H >= 37) id = 3; // stone
                    else if (H <= 16) id = 4; // sand
                    else id = 1; // grass
                }
                // caves
                if (y >= 3 && y < H-2) {
                    if (noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) id = 0;
                }
                blocks[lx + lz*16 + y*256] = id;
            }
        }
    }
    // trees
    for (let lx = 0; lx < 16; lx++) {
        for (let lz = 0; lz < 16; lz++) {
            const wx = cx*16 + lx;
            const wz = cz*16 + lz;
            // per-column hash
            const th = hash2(wx, wz);
            if (th < 0.02) {
                // find surface
                let surfY = -1;
                for (let y = 79; y >= 0; y--) {
                    if (blocks[lx + lz*16 + y*256] === 1) { surfY = y; break; }
                }
                if (surfY >= 0 && surfY + 5 <= 79) {
                    // trunk 4 up
                    for (let k = 1; k <= 4; k++) {
                        blocks[lx + lz*16 + (surfY+k)*256] = 5;
                    }
                    // leaves
                    ...
                }
            }
        }
    }
}
```

Wait, the tree spec says: "4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)".

So trunk is 4 wood blocks (y+1 to y+4). Then leaves:
- 5x5 layer twice (probably at y+2 and y+3?)
- then 3x3
- then 1 on top (y+5?)

Hmm, let me interpret: "leaves as a 5x5 layer twice, then 3x3, then 1 on top". 

Common interpretation: 
- At trunk top level +1: 5x5 of leaves
- At same: another 5x5? No...

Actually let me think. Maybe:
- 5x5 layer (at some height)
- 5x5 layer again (one higher)
- 3x3 layer
- 1 block on top

Let me place:
- y+2: 5x5 leaves centered
- y+3: 5x5 leaves centered
- y+4: 3x3 leaves centered
- y+5: 1 leaf on top

Actually, let me reconsider. The trunk is 4 blocks up (y+1..y+4). Leaves:
- 5x5 layer twice → two 5x5 layers
- then 3x3
- then 1 on top

If trunk is y+1 to y+4, leaves could start at y+2:
- y+2: 5x5
- y+3: 5x5
- y+4: 3x3
- y+5: 1

That seems reasonable. But wait, we need to make sure leaves only go into air. Let me just place them where air.

Actually the phrase "leaves as a 5x5 layer twice" — maybe it means two 5x5 layers stacked. Let me do:
- y+2: 5x5 (radius 2)
- y+3: 5x5 (radius 2)
- y+4: 3x3 (radius 1)
- y+5: 1 (top)

Hmm, but that overlaps with trunk top. Let me reconsider — maybe trunk is 4 up meaning y+1..y+4, and leaves begin above. But "leaves as a 5x5 layer twice, then 3x3, then 1 on top" suggests the crown.

Let me just do a reasonable tree. I'll place leaves from y+2 to y+5.

Actually, I realize the exact tree shape doesn't hugely matter for playability. Let me implement something sensible.

Let me reconsider: "4 wood blocks up" = trunk height 4 (y+1 to y+4). "leaves as a 5x5 layer twice" = two 5x5 layers. "then 3x3" = one 3x3 layer. "then 1 on top" = one block. So total leaf layers = 4 (two 5x5, one 3x3, one 1). Place them at y+2, y+3, y+4, y+5.

Let me define a helper to place a square leaf layer at radius r (half-size):
- 5x5 → radius 2 (from -2 to +2)
- 3x3 → radius 1
- 1 → radius 0

For each leaf layer, iterate offsets dx, dz in [-r, r], and set block if it's air (and within bounds). Actually to make it look nice, maybe skip corners for 5x5? The spec just says 5x5, so full square.

Let me write:
```javascript
function placeLeaf(blocks, cx, cz, lx, lz, baseY, radius) {
    for (let dx = -radius; dx <= radius; dx++) {
        for (let dz = -radius; dz <= radius; dz++) {
            const nx = lx + dx, nz = lz + dz;
            if (nx < 0 || nx >= 16 || nz < 0 || nz >= 16) continue;
            const idx = nx + nz*16 + baseY*256;
            if (blocks[idx] === 0) blocks[idx] = 6;
        }
    }
}
```

For 5x5 twice at y+2 and y+3, 3x3 at y+4, 1 at y+5.

Wait, but the 5x5 at radius 2 includes corners. That's fine per spec.

Now the meshing. Let me write the meshing function.

```javascript
function buildChunkMesh(cx, cz) {
    const key = cx + "," + cz;
    const chunk = chunks.get(key);
    if (!chunk || !chunk.blocks) return;
    const blocks = chunk.blocks;
    
    const positions = [];
    const normals = [];
    const colors = [];
    
    const worldX0 = cx*16, worldZ0 = cz*16;
    
    for (let y = 0; y < 80; y++) {
        for (let z = 0; z < 16; z++) {
            for (let x = 0; x < 16; x++) {
                const idx = x + z*16 + y*256;
                const id = blocks[idx];
                if (id === 0) continue;
                const wx = worldX0 + x, wy = y, wz = worldZ0 + z;
                // check 6 faces
                // helper to get neighbor id
                const nx = (dx, dy, dz) => getBlock(wx+dx, wy+dy, wz+dz);
                // top (y+1)
                if (nx(0,1,0) === 0) addFace(...);
                ...
            }
        }
    }
}
```

I need to be careful with face orientation and winding order for correct culling/backface rendering.

Standard cube faces with proper winding (counter-clockwise when viewed from outside):

Let me define faces. Each face has 4 corners, a normal, and a light factor.

For a block at (x,y,z):

Top face (y+1), normal (0,1,0):
- corners: (0,1,0), (0,1,1), (1,1,1), (1,1,0) — need CCW winding when viewed from above (+y looking down)
- Actually for Three.js with front-facing being CCW, we need the vertices ordered CCW when viewed from outside.

Let me use standard face definitions. I'll use the approach where for each face we define 4 vertices in CCW order.

Top (normal +Y):
```
(0,1,0), (1,1,0), (1,1,1), (0,1,1)
```
Triangles: (0,1,2) and (0,2,3)

Bottom (normal -Y):
```
(0,0,1), (1,0,1), (1,0,0), (0,0,0)
```
Triangles: (0,1,2) and (0,2,3)

Front (normal +Z, z+1):
```
(1,0,1), (0,0,1), (0,1,1), (1,1,1)
```
Triangles: (0,1,2),(0,2,3)

Back (normal -Z, z):
```
(0,0,0), (1,0,0), (1,1,0), (0,1,0)
```

Right (normal +X, x+1):
```
(1,0,1), (1,0,0), (1,1,0), (1,1,1)
```

Left (normal -X, x):
```
(0,0,1), (0,0,0), (0,1,0), (0,1,1)
```

These are the standard definitions. Let me verify winding for top face viewed from above (looking down -Y direction, i.e., from +y):
Points: (0,1,0), (1,1,0), (1,1,1), (0,1,1). Viewed from above, going (0,0)->(1,0)->(1,1)->(0,1) in xz plane. That's counterclockwise? From (0,0) to (1,0) is +x, then to (1,1) is +z, then to (0,1) is -x, then back. Looking down from +y, +x is right, +z is... depends on coordinate handedness. Three.js uses right-handed coordinates. Looking down -Y (from above), x goes right, z goes toward viewer... hmm this is getting complicated.

Let me just trust the standard definitions which are widely used. Actually, let me reconsider. In Three.js, default material has side: DoubleSide off, so only front faces render. The front face is CCW. We need normals pointing outward and vertices CCW when seen from outside.

Let me use these well-tested definitions (from many voxel tutorials):

```
const faces = [
  { dir: [0, 1, 0],  light: 1.0, corners: [[0,1,0],[1,1,0],[1,1,1],[0,1,1]] },
  { dir: [0,-1, 0],  light: 0.55, corners: [[0,0,1],[1,0,1],[1,0,0],[0,0,0]] },
  { dir: [1, 0, 0],  light: 0.8, corners: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]] },
  { dir: [-1,0, 0],  light: 0.8, corners: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
  { dir: [0, 0, 1],  light: 0.8, corners: [[1,0,1],[0,0,1],[0,1,1],[1,1,1]] },
  { dir: [0, 0,-1],  light: 0.8, corners: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]] },
];
```

Let me verify the winding for the +X face (dir [1,0,0]). Corners: (1,0,1),(1,0,0),(1,1,0),(1,1,1). Viewed from +X looking toward -X (from outside). In this view, we see the yz plane. Let me set up: looking from +x toward origin, the visible axes are y (up) and z. With right-hand rule, when looking along -x, z points... Hmm.

Actually, let me just verify using the normal and cross product. For CCW winding, the normal = cross(v1-v0, v2-v0) should point in the same direction as the face normal (outward).

For +X face: v0=(1,0,1), v1=(1,0,0), v2=(1,1,0).
v1-v0 = (0,0,-1)
v2-v0 = (0,1,-1)
cross = (v1-v0) × (v2-v0) = |i j k; 0 0 -1; 0 1 -1|
i: (0*-1) - (-1*1) = 0 - (-1) = 1
j: -((0*-1) - (-1*0)) = -(0 - 0) = 0
k: (0*1) - (0*0) = 0
So cross = (1, 0, 0). That matches the normal [+X]. 

Let me verify +Y (top): v0=(0,1,0), v1=(1,1,0), v2=(1,1,1).
v1-v0 = (1,0,0)
v2-v0 = (1,0,1)
cross = |i j k; 1 0 0; 1 0 1|
i: 0*1 - 0*0 = 0
j: -((1*1) - (0*1)) = -(1-0) = -1
k: 1*0 - 0*1 = 0
cross = (0,-1,0). That's WRONG, should be +Y.

Hmm. So my +Y definition has wrong winding. Let me fix it. Swap to CCW: v0=(0,1,0), v1=(1,1,1)... no wait.

Let me recompute. I want cross(v1-v0, v2-v0) = (0,1,0).

Try v0=(0,1,0), v1=(0,1,1), v2=(1,1,1)? 
Wait, let me pick corners such that it works. 

v0=(0,1,0), v1=(1,1,0), v2=(1,1,1): gave (0,-1,0). 
To fix, reverse: v0=(0,1,0), v2=(1,1,0), v1=(1,1,1)? Let me just reverse the triangle order.

Actually simpler: for +Y, use corners [(0,1,1),(1,1,1),(1,1,0),(0,1,0)] as the quad, with triangles (0,1,2) and (0,2,3).

v0=(0,1,1), v1=(1,1,1), v2=(1,1,0):
v1-v0=(1,0,0), v2-v0=(1,0,-1)
cross = |i j k; 1 0 0; 1 0 -1|
i: 0*(-1) - 0*0 = 0
j: -((1*(-1)) - (0*1)) = -(-1) = 1
k: 1*0 - 0*1 = 0
cross = (0,1,0). Correct!

So +Y face: corners [(0,1,1),(1,1,1),(1,1,0),(0,1,0)], triangles (0,1,2),(0,2,3).

Let me redo all faces carefully to ensure CCW winding gives outward normal.

Let me define a general method. For each face, I'll pick 3 points and compute the cross product to determine winding, then order accordingly.

Actually, let me just carefully define all 6 with verification.

**Top (+Y):** want outward normal (0,1,0).
Quad points (in xz), let me choose order that's CCW seen from above.
Seen from above (+y looking down -y), the x-axis points right, z-axis points... in a right-handed system with y up, if I look down -y, then x is right and z is toward me (up on screen)? Let me think. Right-handed: x right, y up, z toward viewer (out of screen). Now rotate to look down -y: I'm now looking from +y downward. The x-axis still points right. The z-axis... originally z comes toward viewer, but now my new "toward viewer" is -y direction. Hmm, this mental rotation is error-prone.

Let me just use the cross product method for all 6 and verify numerically.

Face definitions (quad corners c0,c1,c2,c3), triangles (c0,c1,c2) and (c0,c2,c3):

1. **+Y (top)**: I'll use [(0,1,1),(0,1,0),(1,1,0),(1,1,1)].
   v0=(0,1,1), v1=(0,1,0), v2=(1,1,0).
   v1-v0=(0,0,-1), v2-v0=(1,0,-1).
   cross = |i j k; 0 0 -1; 1 0 -1|
   i: 0*(-1) - (-1*0) = 0
   j: -((0*(-1)) - ((-1)*1)) = -(0 - (-1)) = -(1) = -1
   k: 0*0 - 0*1 = 0
   cross = (0,-1,0). Wrong.
   
   Let me reverse: [(0,1,1),(1,1,1),(1,1,0),(0,1,0)] — computed above gives (0,1,0). Correct!
   So **+Y**: [(0,1,1),(1,1,1),(1,1,0),(0,1,0)].

2. **-Y (bottom)**: want (0,-1,0).
   Try [(0,0,0),(1,0,0),(1,0,1),(0,0,1)].
   v0=(0,0,0), v1=(1,0,0), v2=(1,0,1).
   v1-v0=(1,0,0), v2-v0=(1,0,1).
   cross = |i j k; 1 0 0; 1 0 1|
   i: 0*1 - 0*0 = 0
   j: -((1*1) - (0*1)) = -1
   k: 1*0 - 0*1 = 0
   cross = (0,-1,0). Correct!
   So **-Y**: [(0,0,0),(1,0,0),(1,0,1),(0,0,1)].

3. **+X (right)**: want (1,0,0).
   Try [(1,0,1),(1,1,1),(1,1,0),(1,0,0)].
   v0=(1,0,1), v1=(1,1,1), v2=(1,1,0).
   v1-v0=(0,1,0), v2-v0=(0,1,-1).
   cross = |i j k; 0 1 0; 0 1 -1|
   i: 1*(-1) - 0*1 = -1
   j: -((0*(-1)) - (0*0)) = 0
   k: 0*1 - 1*0 = 0
   cross = (-1,0,0). Wrong.
   Reverse: [(1,0,1),(1,0,0),(1,1,0),(1,1,1)].
   v0=(1,0,1), v1=(1,0,0), v2=(1,1,0).
   v1-v0=(0,0,-1), v2-v0=(0,1,-1).
   cross = |i j k; 0 0 -1; 0 1 -1|
   i: 0*(-1) - (-1*1) = 1
   j: -((0*(-1)) - ((-1)*0)) = 0
   k: 0*1 - 0*0 = 0
   cross = (1,0,0). Correct!
   So **+X**: [(1,0,1),(1,0,0),(1,1,0),(1,1,1)].

4. **-X (left)**: want (-1,0,0).
   Try [(0,0,1),(0,1,1),(0,1,0),(0,0,0)].
   v0=(0,0,1), v1=(0,1,1), v2=(0,1,0).
   v1-v0=(0,1,0), v2-v0=(0,1,-1).
   cross = |i j k; 0 1 0; 0 1 -1|
   i: 1*(-1) - 0*1 = -1
   j: -((0*(-1)) - (0*0)) = 0
   k: 0*1 - 1*0 = 0
   cross = (-1,0,0). Correct!
   So **-X**: [(0,0,1),(0,1,1),(0,1,0),(0,0,0)].

5. **+Z (front)**: want (0,0,1).
   Try [(0,0,1),(1,0,1),(1,1,1),(0,1,1)].
   v0=(0,0,1), v1=(1,0,1), v2=(1,1,1).
   v1-v0=(1,0,0), v2-v0=(1,1,0).
   cross = |i j k; 1 0 0; 1 1 0|
   i: 0*0 - 0*1 = 0
   j: -((1*0) - (0*1)) = 0
   k: 1*1 - 0*1 = 1
   cross = (0,0,1). Correct!
   So **+Z**: [(0,0,1),(1,0,1),(1,1,1),(0,1,1)].

6. **-Z (back)**: want (0,0,-1).
   Try [(1,0,0),(0,0,0),(0,1,0),(1,1,0)].
   v0=(1,0,0), v1=(0,0,0), v2=(0,1,0).
   v1-v0=(-1,0,0), v2-v0=(-1,1,0).
   cross = |i j k; -1 0 0; -1 1 0|
   i: 0*0 - 0*1 = 0
   j: -((-1*0) - (0*(-1))) = 0
   k: (-1*1) - (0*(-1)) = -1
   cross = (0,0,-1). Correct!
   So **-Z**: [(1,0,0),(0,0,0),(0,1,0),(1,1,0)].

Great, I have all 6 faces verified:
```
const FACES = [
  { n:[0,1,0],  l:1.0, c:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { n:[0,-1,0], l:0.55,c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
  { n:[1,0,0],  l:0.8, c:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]] },
  { n:[-1,0,0], l:0.8, c:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
  { n:[0,0,1],  l:0.8, c:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]] },
  { n:[0,0,-1], l:0.8, c:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]] },
];
```

Now the meshing: for each block, for each face, check if neighbor is air (or transparent). Since only air is transparent here (leaves... hmm, leaves might need special handling). The spec says "for each of the 6 sides check the neighbor with the global read helper; if it is air, add that face". So leaves are treated as opaque for culling purposes (we only check air). That means a block adjacent to leaves will still render its face. That's fine and matches the spec (simple approach). Actually wait — if leaves are opaque-ish and we only cull against air, then a leaves block next to a grass block: grass checks neighbor leaves, leaves != air, so grass face is culled. And leaves checks neighbor grass, grass != air, so leaves face culled. So they blend. Good enough.

But actually there's a subtlety: should we render a face between two solid blocks? No. Between solid and leaves? The solid block's face would be culled (leaves not air). Fine.

The spec explicitly says: "if it is air, add that face". So condition is neighbor === 0 (air). Simple.

Now, getBlock neighbor lookup during meshing needs to handle chunk boundaries (neighbors in adjacent chunks). The global getBlock handles that.

Let me now think about the color assignment. Each block has a base color. The light factor multiplies the color. Since we use one shared MeshLambertMaterial with vertexColors, we set per-vertex colors = baseColor * lightFactor.

Block colors:
- grass 0x4caf50
- dirt 0x795548
- stone 0x9e9e9e
- sand 0xe7d9a8
- wood 0x8d6e63
- leaves 0x2e7d32
- snow 0xffffff

Convert to RGB (0-1) and multiply by light factor.

Now the block data storage. Chunk blocks array is Uint8Array of size 16*16*80 = 20480. Index = x + z*16 + y*256.

Global getBlock(wx, wy, wz):
```javascript
function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= 80) return 0;
    const cx = Math.floor(wx / 16);
    const cz = Math.floor(wz / 16);
    const lx = wx - cx*16;
    const lz = wz - cz*16;
    const chunk = chunks.get(cx + "," + cz);
    if (!chunk || !chunk.blocks) return 0;
    return chunk.blocks[lx + lz*16 + wy*256];
}
```

setBlock(wx, wy, wz, id):
```javascript
function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= 80) return;
    const cx = Math.floor(wx / 16);
    const cz = Math.floor(wz / 16);
    const lx = wx - cx*16;
    const lz = wz - cz*16;
    const key = cx + "," + cz;
    let chunk = chunks.get(key);
    if (!chunk) {
        chunk = { blocks: new Uint8Array(20480), mesh: null };
        chunks.set(key, chunk);
    }
    chunk.blocks[lx + lz*16 + wy*256] = id;
}
```

Now the main loop updates. Each frame:
- Determine chunks within 5 of player (max 4 per frame): generate block data.
- Build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame).
- For chunks farther than 7, remove mesh, dispose geometry, delete entry.

"within 5 chunks of the player" — I interpret as chunk-distance (Chebyshev or Manhattan?) Let me use Chebyshev distance in chunk space <= 5. Generate up to 4 per frame.

"chunks within 4 chunks whose 4 neighbors already have data" — chunk distance <= 4, and all 4 cardinal neighbors (cx±1,cz or cx,cz±1) have data (mesh or blocks built). Build up to 2 per frame.

Actually "whose 4 neighbors already have data" — the 4 neighbors having data means their blocks are generated. So we can mesh this chunk if its neighbors' data exists.

Let me track chunk state: each chunk entry could have a flag for whether data is generated. Let me add `built` or check `chunk.blocks != null`. When we generate data, set chunk.blocks. When we build mesh, create chunk.mesh.

Let me define:
- chunk.dataReady = chunk.blocks !== null (after generateChunkData)
- chunk.meshReady = chunk.mesh !== null

Generation: for chunks within dist 5, if !dataReady, generate (up to 4/frame).
Meshing: for chunks within dist 4, if dataReady and !meshReady and all 4 neighbors dataReady, build (up to 2/frame).

Distance: chunk distance from player's chunk. playerChunkX = floor(px/16), etc. dist = max(|cx-pcx|, |cz-pcz|) (Chebyshev).

Cleanup: for chunks with dist > 7, if mesh, dispose geometry, delete. Also maybe delete chunks beyond some range entirely. The spec says "for chunks farther than 7, remove the mesh, dispose its geometry and delete the entry." So delete the whole entry.

Let me implement the update loop:

```javascript
function updateWorld() {
    const pcx = Math.floor(player.pos.x / 16);
    const pcz = Math.floor(player.pos.z / 16);
    
    // generate
    let genCount = 0;
    for (let dx = -5; dx <= 5 && genCount < 4; dx++) {
        for (let dz = -5; dz <= 5 && genCount < 4; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = cx + "," + cz;
            const chunk = chunks.get(key);
            if (!chunk || chunk.blocks) continue;
            chunk.blocks = new Uint8Array(20480);
            generateChunkData(cx, cz, chunk.blocks);
            genCount++;
        }
    }
    
    // mesh
    let meshCount = 0;
    for (let dx = -4; dx <= 4 && meshCount < 2; dx++) {
        for (let dz = -4; dz <= 4 && meshCount < 2; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = cx + "," + cz;
            const chunk = chunks.get(key);
            if (!chunk || !chunk.blocks || chunk.mesh) continue;
            // check 4 neighbors
            const nb = chunks.get((cx+1)+","+cz) && chunks.get((cx-1)+","+cz) && chunks.get(cx+","+ (cz+1)) && chunks.get(cx+","+ (cz-1));
            if (nb) { buildChunkMesh(cx, cz); meshCount++; }
        }
    }
    
    // cleanup
    for (const [key, chunk] of chunks) {
        const parts = key.split(",");
        const cx = +parts[0], cz = +parts[1];
        const d = Math.max(Math.abs(cx-pcx), Math.abs(cz-pcz));
        if (d > 7) {
            if (chunk.mesh) { chunk.mesh.geometry.dispose(); }
            chunks.delete(key);
        }
    }
}
```

Wait, there's an issue with the mesh generation condition. "chunks within 4 chunks whose 4 neighbors already have data". If a chunk is at the edge of the generation ring, its neighbors might not be generated yet. But since we generate first (up to 4/frame), and the neighbors being dataReady means blocks exist. The condition ensures we don't mesh a chunk before its neighbors have data (needed for correct face culling at borders).

But there's a subtle issue: what if a chunk's neighbor's mesh isn't built but its data is? For culling we only need neighbor DATA (getBlock reads chunk.blocks). So dataReady is sufficient. Good.

However, there's a problem: when we build a chunk's mesh, we call getBlock on neighbors which reads their blocks. If a neighbor has no blocks (missing entry), getBlock returns 0 (air). That's fine — it treats missing as air. But for border correctness, we want the neighbor's actual data. Since we require 4 neighbors to have data, this is satisfied.

Now, one concern: the initial spawn. Player spawns at x=8, z=8, which is chunk (0,0) local (8,8). We need terrain generated around spawn before spawning. Let me pre-generate the starting area or handle spawn gracefully. Actually, the update loop runs every frame, so within a few frames the spawn chunks will be generated. But the player might fall through the world if nothing is there. Let me spawn the player high (like y=70) and let terrain generate. Actually, let me pre-generate chunks around spawn at startup to be safe. Or spawn at a high y and let gravity bring them down once terrain generates.

Better: at startup, generate all chunks within dist 5 immediately (before the loop) so the world is populated. Then the frame loop just meshes them. Actually the spec says each frame does generation. But to avoid falling through empty world at spawn, let me pre-build the spawn region. I'll generate and mesh all chunks within dist 5 at init.

Hmm, but the spec is specific about per-frame limits. Let me do: at init, generate all chunks within 5 (no limit) and mesh those whose neighbors are ready. This ensures a solid floor under spawn. Then the game loop maintains it.

Actually, simpler and safer: at init, generate + mesh everything within dist 5. The per-frame limits apply during gameplay. This is fine.

Let me also handle: player starts above terrain. Compute terrain height at (8,8) and spawn above it. But terrain generation takes a moment. Let me just spawn at y = 60 or compute after generation. Since I pre-generate spawn region, I can query getBlock(8, y, 8) for the surface.

Let me find surface: scan from y=79 down for first non-air near spawn.

Actually, let me just spawn at a safe high y like 70 and if they're underground, well. Better to compute. Let me spawn at the surface + 3.

Let me write a helper to get surface height:
```javascript
function surfaceHeight(x, z) {
    for (let y = 79; y >= 0; y--) {
        if (getBlock(x, y, z) !== 0) return y;
    }
    return 40;
}
```

Spawn at player.pos.y = surfaceHeight(8,8) + 2.

Now player physics. Let me define:
```javascript
const player = {
    pos: new THREE.Vector3(),
    vel: new THREE.Vector3(),
    yaw: 0,
    pitch: 0,
    onGround: false,
};
```

Movement:
```javascript
const keys = {};
window.addEventListener('keydown', e => keys[e.code] = true);
window.addEventListener('keyup', e => keys[e.code] = false);
```

In update:
```javascript
const speed = 5.5;
const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
const move = new THREE.Vector3();
if (keys['KeyW']) move.add(forward);
if (keys['KeyS']) move.sub(forward);
if (keys['KeyD']) move.add(right);
if (keys['KeyA']) move.sub(right);
move.normalize().multiplyScalar(speed * dt);
player.vel.x = move.x;
player.vel.z = move.z;
```

Gravity and jump:
```javascript
if (keys['Space'] && player.onGround) { player.vel.y = 8.5; }
player.vel.y -= 25 * dt;
```

Collision (axis-separated):
```javascript
function collide(axis, delta) {
    // move along axis, check overlap with player box
}
```

Player box: half-width 0.3, height 1.8, eye 1.62. So the box spans from pos.x-0.3 to pos.x+0.3 in x and z, and from pos.y to pos.y+1.8 in y (feet at pos.y, head at pos.y+1.8). Eye at pos.y+1.62.

Collision check: for a block at (bx,by,bz), it occupies [bx,bx+1]x[by,by+1]x[bz,bz+1]. Player box overlaps if any axis overlaps.

Let me implement per-axis:
```javascript
function moveWithCollision(delta) {
    // X
    player.pos.x += delta.x;
    if (collides()) {
        player.pos.x -= delta.x;
        player.vel.x = 0;
        // snap to block boundary
        if (delta.x > 0) player.pos.x = Math.floor(player.pos.x + 0.3) - 0.3; // not exactly
        ...
    }
    ...
}
```

Hmm, let me think about the collision resolution more carefully. Standard approach:

For each axis:
1. Move position along that axis by velocity*dt.
2. Check if player box now collides with any solid block.
3. If yes, revert that axis movement (restore previous position) and set velocity along that axis to 0. For Y, if moving down and collided, set onGround=true.

Player box: min = (pos.x - 0.3, pos.y, pos.z - 0.3), max = (pos.x + 0.3, pos.y + 1.8, pos.z + 0.3).

Collision test:
```javascript
function collides() {
    const minX = Math.floor(player.pos.x - 0.3);
    const maxX = Math.floor(player.pos.x + 0.3);
    const minY = Math.floor(player.pos.y);
    const maxY = Math.floor(player.pos.y + 1.8 - 0.001); // subtract epsilon to avoid counting top block
    const minZ = Math.floor(player.pos.z - 0.3);
    const maxZ = Math.floor(player.pos.z + 0.3);
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

Wait, the maxY: player head is at pos.y + 1.8. A block at floor(pos.y+1.8) would be the block the head is touching. Should that count as collision? Typically you want to allow the head to be just below the block. Using floor(pos.y + 1.8 - epsilon) excludes the top block if head is exactly at boundary. Actually if head is at y+1.8 and there's a block at floor(y+1.8), that block occupies [floor, floor+1] which includes y+1.8 if floor <= y+1.8 < floor+1. So it IS overlapping. We should count it. But to prevent sticking, sometimes people subtract a tiny epsilon. Let me include the top block (use floor(pos.y + 1.8)). Actually, let me reconsider: if the player is standing on a block at height by, their feet pos.y is just above by. Head at pos.y+1.8. If there's a block above the head, collision. The block directly at the head level — if head reaches into it, collide. Using floor(pos.y+1.8) includes the block the head is currently in. That's correct for detecting penetration.

Hmm, but consider standing exactly on top of a block: feet at by+1 (just barely), head at by+1+1.8 = by+2.8. floor(by+2.8) = by+2, which occupies [by+2, by+3]. Head at by+2.8 is inside. But there's no block there necessarily. This would falsely report collision if by+2 happens to be solid. But that's only if there's actually a solid block there. Fine.

Actually the epsilon approach: maxY = floor(pos.y + 1.8 - 1e-6). This means if head is exactly at integer boundary, we don't count that block. This prevents the classic bug where you're pressed against the ceiling. Let me use a small epsilon. Actually, let me not overthink; I'll use floor(pos.y + 1.8 - 1e-4) to be safe against floating point. Hmm, but that could let you stick through floors. Let me just use floor(pos.y + 1.8) and accept minor issues, OR use the epsilon. 

I'll go with checking blocks in [minX,maxX]x[minY,maxY]x[minZ,maxZ] where maxY = floor(pos.y + 1.8 - 1e-3). This is a common robust approach.

Actually, let me reconsider. The issue with including the top block: Suppose player falls onto a platform. Their velocity brings pos.y such that head is at exactly the block's space. We detect collision and revert. Good. The epsilon mainly matters for the horizontal and for avoiding double-counting. Let me keep it simple: use floor(pos.y + 1.8) for maxY (include top block). This is standard and works.

Let me reconsider the revert logic. When we revert along an axis, we restore the previous position. For horizontal, we just undo the delta. For Y up (jump into ceiling), undo delta, set vel.y=0. For Y down (land on block), undo delta, set vel.y=0, onGround=true.

But there's a subtlety: after reverting, the player box might still slightly penetrate due to rounding. Usually restoring exact previous position avoids penetration. Let me restore previous position exactly.

Implementation:
```javascript
function updatePhysics(dt) {
    // apply gravity
    player.vel.y -= 25 * dt;
    if (player.vel.y < -50) player.vel.y = -50;
    
    const dx = player.vel.x * dt;
    const dy = player.vel.y * dt;
    const dz = player.vel.z * dt;
    
    // X
    player.pos.x += dx;
    if (collides()) {
        player.pos.x -= dx;
        player.vel.x = 0;
    }
    // Z
    player.pos.z += dz;
    if (collides()) {
        player.pos.z -= dz;
        player.vel.z = 0;
    }
    // Y
    player.pos.y += dy;
    if (collides()) {
        player.pos.y -= dy;
        player.vel.y = 0;
        if (dy < 0) player.onGround = true;
        else player.onGround = false;
    } else {
        if (!(dy < 0)) player.onGround = false; // moving up not on ground
    }
    // Actually onGround logic: set true when landing, false otherwise unless resting
}
```

Hmm, onGround tracking is a bit tricky. Let me simplify: onGround becomes true when we collide while moving down (dy < 0). It becomes false when we jump or when moving up without collision. Let me set:
- Before physics, if jumping was pressed and onGround, set vel.y = 8.5.
- During Y collision: if dy < 0 → onGround = true (landed). If dy > 0 → onGround = false (hit head).
- If no Y collision and dy > 0 → onGround = false.
- If no Y collision and dy < 0 → onGround stays? Should be false (falling). Set onGround = false.

Let me set onGround = false at start of each frame's Y handling unless we land. Actually cleanest:
```javascript
player.onGround = false;
// ... do Y move ...
if (collides after Y) {
    revert;
    if (dy < 0) player.onGround = true;
}
```
Setting onGround=false at the start handles the case. But we set it before X/Z moves which don't affect ground. That's fine. Wait, but if we set onGround=false at start and then land, we set it true. Good. But what about when standing still on ground with zero vertical velocity? dy ≈ 0 (gravity adds a bit each frame, so dy < 0 always when grounded). Actually gravity constantly accelerates, so even standing on ground, dy becomes slightly negative, and collision detects it, setting onGround=true and reverting. Good, that keeps player on the block. But we also need the jump to work: when grounded and press space, vel.y = 8.5 (positive). Next frame dy > 0, no collision (moved up), onGround=false. Good.

But wait — there's a problem. When grounded, gravity makes dy slightly negative each frame. The collision reverts it and sets onGround=true. But the revert restores exact previous pos, so player stays put. However, vel.y is set to 0 on collision. So gravity's accumulation gets reset. Good. This is standard.

Edge case: what if the player is exactly on the block and gravity would push them in — the revert handles it. Fine.

Now the fall-below check: if player.pos.y < -20, teleport to spawn.

Now the camera. Camera position = player.pos + (0, 1.62, 0) (eye). Rotation: yaw around Y, pitch around X. Order "YXZ".

```javascript
camera.position.copy(player.pos);
camera.position.y += 1.62;
camera.rotation.order = "YXZ";
camera.rotation.y = player.yaw;
camera.rotation.x = player.pitch;
```

Mouse look:
```javascript
document.addEventListener('mousemove', e => {
    if (pointerLocked) {
        player.yaw -= e.movementX * 0.002;
        player.pitch -= e.movementY * 0.002;
        player.pitch = Math.max(-Math.PI/2 + 0.001, Math.min(Math.PI/2 - 0.001, player.pitch));
    }
});
```

Sensitivity ~0.002, clamp pitch.

Pointer lock:
```javascript
const overlay = document.getElementById('overlay');
overlay.addEventListener('click', () => canvas.requestPointerLock());
document.addEventListener('pointerlockchange', () => {
    pointerLocked = document.pointerLockElement === canvas;
    if (!pointerLocked) overlay.style.display = 'flex';
    else overlay.style.display = 'none';
});
```

Wait, clicking the overlay requests pointer lock. When unlocked, show overlay. When locked, hide overlay. The overlay click handler requests lock.

But also, when pointer lock is lost (e.g., Esc), show overlay. pointerlockchange fires. Good.

Break/place: only when locked. Listen for mousedown on canvas:
```javascript
canvas.addEventListener('mousedown', e => {
    if (!pointerLocked) return;
    if (e.button === 0) breakBlock();
    else if (e.button === 2) placeBlock();
});
canvas.addEventListener('contextmenu', e => e.preventDefault());
```

Raycasting:
```javascript
function raycast() {
    // origin = camera position
    // direction = forward from camera
    const origin = new THREE.Vector3();
    camera.getWorldPosition(origin);
    const dir = new THREE.Vector3(0,0,-1);
    dir.applyEuler(new THREE.Euler(player.pitch, player.yaw, 0, "YXZ"));
    // or compute from yaw/pitch
    const hit = THREE.Raycaster.intersectObjects(chunkMeshes, false);
    if (hit.length > 0 && hit[0].distance <= 6) {
        const p = hit[0].point;
        const n = hit[0].face.normal;
        // break target
        const bx = Math.floor(p.x - n.x*0.5);
        const by = Math.floor(p.y - n.y*0.5);
        const bz = Math.floor(p.z - n.z*0.5);
        // place cell
        const px = Math.floor(p.x + n.x*0.5);
        const py = Math.floor(p.y + n.y*0.5);
        const pz = Math.floor(p.z + n.z*0.5);
        return { break:{x:bx,y:by,z:bz}, place:{x:px,y:py,z:pz} };
    }
    return null;
}
```

The raycaster uses chunk meshes. The normal from face is in world space (since meshes are at origin with world coords, the face normal is already world-space because geometry wasn't transformed... wait, the mesh is at origin, so local = world. The face.normal is in the mesh's local space, which equals world space since no transform. Good.)

But wait — the raycaster computes face.normal in world space by applying the mesh's normal matrix. Since mesh is at identity, normal = face.normal from geometry. Good.

Outline box:
```javascript
const outline = new THREE.Mesh(
    new THREE.BoxGeometry(1.001, 1.001, 1.001),
    new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);
```
Actually a wireframe box:
```javascript
const geo = new THREE.BoxGeometry(1,1,1);
const edges = new THREE.EdgesGeometry(geo);
const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({color:0x000000}));
```
Position at target block + 0.5. Show when targeting.

Break:
```javascript
function breakBlock() {
    const target = raycastTarget.break;
    if (!target) return;
    if (target.y === 0) return; // don't break y=0 stone
    setBlock(target.x, target.y, target.z, 0);
    rebuildChunk(target.x, target.z);
}
```

Place:
```javascript
function placeBlock() {
    const cell = raycastTarget.place;
    if (!cell) return;
    const sel = hotbar[selected];
    if (getBlock(cell.x, cell.y, cell.z) !== 0) return;
    // check not overlapping player
    if (blockOverlapsPlayer(cell.x, cell.y, cell.z)) return;
    setBlock(cell.x, cell.y, cell.z, sel);
    rebuildChunk(cell.x, cell.z);
}
```

blockOverlapsPlayer: check if placed block's [bx,bx+1]x[by,by+1]x[bz,bz+1] overlaps player box.
```javascript
function blockOverlapsPlayer(bx, by, bz) {
    const px0 = player.pos.x - 0.3, px1 = player.pos.x + 0.3;
    const py0 = player.pos.y, py1 = player.pos.y + 1.8;
    const pz0 = player.pos.z - 0.3, pz1 = player.pos.z + 0.3;
    return bx < px1 && bx+1 > px0 && by < py1 && by+1 > py0 && bz < pz1 && bz+1 > pz0;
}
```

rebuildChunk:
```javascript
function rebuildChunk(wx, wz) {
    const cx = Math.floor(wx/16), cz = Math.floor(wz/16);
    buildChunkMesh(cx, cz);
    // neighbor if on border
    const lx = wx - cx*16, lz = wz - cz*16;
    if (lx === 0) buildChunkMesh(cx-1, cz);
    if (lx === 15) buildChunkMesh(cx+1, cz);
    if (lz === 0) buildChunkMesh(cx, cz-1);
    if (lz === 15) buildChunkMesh(cx, cz+1);
}
```

buildChunkMesh disposes old mesh/geometry first:
```javascript
function buildChunkMesh(cx, cz) {
    const key = cx+","+cz;
    const chunk = chunks.get(key);
    if (!chunk || !chunk.blocks) return;
    if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
    }
    // build arrays...
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    const mesh = new THREE.Mesh(geo, blockMaterial);
    mesh.position.set(0,0,0); // at origin
    scene.add(mesh);
    chunk.mesh = mesh;
    chunkMeshes.push(mesh); // but we should manage this array
}
```

Wait, chunkMeshes should contain all current chunk meshes for raycasting. If I reuse the array and push, I need to remove disposed ones. Let me manage chunkMeshes as the set of live meshes. Since buildChunkMesh replaces, let me filter chunkMeshes to exclude disposed. Actually simpler: maintain chunkMeshes as an array that mirrors chunk.mesh. On dispose, remove from array. Let me handle in buildChunkMesh:

```javascript
if (chunk.mesh) {
    const idx = chunkMeshes.indexOf(chunk.mesh);
    if (idx >= 0) chunkMeshes.splice(idx, 1);
    scene.remove(chunk.mesh);
    chunk.mesh.geometry.dispose();
}
```

Now the water plane and clouds.

Water: a transparent blue plane at y=14.3, large, re-centered on player each frame.
```javascript
const water = new THREE.Mesh(
    new THREE.PlaneGeometry(1000, 1000),
    new THREE.MeshLambertMaterial({ color: 0x00aaff, transparent: true, opacity: 0.6 })
);
water.rotation.x = -Math.PI/2;
scene.add(water);
```
Each frame: water.position.x = player.pos.x; water.position.z = player.pos.z; water.position.y = 14.3.

Clouds: ~25 white transparent boxes at height 90, drifting, wrapping around player.
```javascript
const clouds = [];
for (let i = 0; i < 25; i++) {
    const cloud = new THREE.Mesh(
        new THREE.BoxGeometry(4 + Math.random()*6, 1, 4 + Math.random()*6),
        new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true })
    );
    cloud.position.set((Math.random()-0.5)*200, 90, (Math.random()-0.5)*200);
    scene.add(cloud);
    clouds.push(cloud);
}
```
Wait, the spec says "no Math.random" for terrain, but clouds can use random? "Around 25 flat white transparent boxes as clouds at height ~90, slowly drifting and wrapping around the player." It doesn't forbid random for clouds. But to be safe and deterministic, maybe I should avoid Math.random entirely. Actually the constraint "deterministic, no Math.random" is under the Terrain section. Clouds are separate. But let me use a deterministic approach anyway to be safe, or just use Math.random for cloud placement since it's not terrain. Hmm, the overall instruction earlier said terrain is deterministic. Let me use Math.random for clouds — it's fine, they're decorative and don't need determinism. Actually, to be fully safe, I'll seed cloud positions with the hash function. But it's simpler to just use Math.random. The spec doesn't prohibit it for clouds. Let me use Math.random for cloud sizes/positions.

Actually wait — re-reading: "Terrain (deterministic, no Math.random)". This is specifically about terrain. Clouds use Math.random freely. OK.

Drifting and wrapping:
```javascript
for (cloud of clouds) {
    cloud.position.x += drift * dt;
    if (cloud.position.x - player.pos.x > 128) cloud.position.x -= 256;
    if (cloud.position.x - player.pos.x < -128) cloud.position.x += 256;
    // same for z
}
```

Let me wrap both x and z relative to player.

Sky and fog:
```javascript
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);
```

Lights:
```javascript
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(0.5, 1, 0.5).normalize(); // or fixed
scene.add(ambient);
scene.add(sun);
```

Directional light position should follow player or stay fixed? The spec says "one directional light 0.8". Doesn't say follow player. Let me keep it fixed direction but it's fine. Actually to keep shadows/light consistent, maybe position it relative to player. But DirectionalLight without target just uses direction from position to target(0,0,0). Let me set sun.position and it points toward origin. That's fine for flat shading effect. Actually, let me move the sun to follow the player so lighting is consistent: sun.position.set(player.pos.x + 100, 200, player.pos.z + 100); sun.lookAt(player.pos). Hmm, but that changes per frame. Simpler: keep sun at a fixed direction. Let me set sun.position to a normalized direction and add to scene. The lambert material will shade based on normal vs light direction. Fixed direction is fine.

Let me set:
```javascript
sun.position.set(100, 200, 100);
```
And it looks at origin by default. Good enough.

Now the hotbar UI. 7 slots. Build with DOM.
```html
<div id="hotbar">
  <div class="slot" data-i="0" style="background:#4caf50">1</div>
  ...
</div>
```
Selected slot gets white border. Update on select.

Select with keys 1-7 or mouse wheel (wraps).
```javascript
window.addEventListener('keydown', e => {
    if (e.code >= 'Digit1' && e.code <= 'Digit7') selectSlot(+e.code.slice(5) - 1);
});
canvas.addEventListener('wheel', e => {
    if (!pointerLocked) return;
    selectSlot((selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7);
}, { passive: false });
```

selectSlot updates the active class and stores selection.

Now let me also handle the crosshair — a small div at center.

Let me also suppress context menu globally.

Now, one important thing: the raycaster and chunk meshes. When chunks are rebuilt/disposed, update chunkMeshes array. I've handled that.

Also, initial chunkMeshes population: at init, after generating and meshing spawn region, chunkMeshes contains those meshes.

Let me also make sure the material is shared: `const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });`.

Vertex colors: I set per-vertex colors = baseColor * lightFactor. baseColor from block ID.

Let me define color map:
```javascript
const BLOCK_COLORS = {
    1: [0x2e7d32? no...
};
```
Wait, grass is 0x4caf50. Let me convert hex to rgb components:
```javascript
function hexToRGB(hex) {
    return [(hex>>16&255)/255, (hex>>8&255)/255, (hex&255)/255];
}
const BLOCK_RGB = {
    1: hexToRGB(0x4caf50),
    2: hexToRGB(0x795548),
    3: hexToRGB(0x9e9e9e),
    4: hexToRGB(0xe7d9a8),
    5: hexToRGB(0x8d6e63),
    6: hexToRGB(0x2e7d32),
    7: hexToRGB(0xffffff),
};
```

In meshing, for each face of a block with id `id`, color = BLOCK_RGB[id] * face.light. Set for all 4 vertices of that face.

Now let me carefully write the meshing with performance in mind (build arrays then create Float32BufferAttribute).

Let me write buildChunkMesh:
```javascript
function buildChunkMesh(cx, cz) {
    const key = cx+","+cz;
    const chunk = chunks.get(key);
    if (!chunk || !chunk.blocks) return;
    if (chunk.mesh) {
        const i = chunkMeshes.indexOf(chunk.mesh);
        if (i >= 0) chunkMeshes.splice(i,1);
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
    }
    const blocks = chunk.blocks;
    const wx0 = cx*16, wz0 = cz*16;
    const pos = [], nrm = [], col = [];
    for (let y = 0; y < 80; y++) {
        for (let z = 0; z < 16; z++) {
            for (let x = 0; x < 16; x++) {
                const id = blocks[x + z*16 + y*256];
                if (id === 0) continue;
                const wx = wx0 + x, wy = y, wz = wz0 + z;
                const rgb = BLOCK_RGB[id];
                for (let f = 0; f < 6; f++) {
                    const face = FACES[f];
                    const nx = wx + face.n[0], ny = wy + face.n[1], nz = wz + face.n[2];
                    if (getBlock(nx, ny, nz) !== 0) continue; // neighbor solid, cull
                    const light = face.l;
                    for (let v = 0; v < 4; v++) {
                        const c = face.c[v];
                        pos.push(wx+c[0], wy+c[1], wz+c[2]);
                        nrm.push(face.n[0], face.n[1], face.n[2]);
                        col.push(rgb[0]*light, rgb[1]*light, rgb[2]*light);
                    }
                }
            }
        }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    const mesh = new THREE.Mesh(geo, blockMaterial);
    scene.add(mesh);
    chunk.mesh = mesh;
    chunkMeshes.push(mesh);
}
```

Note: Float32BufferAttribute is deprecated but still works in r128. Let me use new THREE.BufferAttribute to be safe. Actually both work. Let me use BufferAttribute.

Wait, THREE.Float32BufferAttribute exists in r128 (deprecated but present). To be safe, use THREE.BufferAttribute.

Now, getBlock during meshing calls into neighbor chunks. For neighbor chunks that exist with blocks, reads their data. For missing, returns 0. Good.

Potential issue: infinite recursion? No.

Now the generateChunkData. Let me refine the tree placement and make sure it only places into air.

Let me also double check the column fill logic against spec:
"Column fill: y 0 = unbreakable stone; below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

So:
- y == 0: stone (3)
- y < H-3: stone (3)
- The 3 layers under surface: these are y in [H-3, H-1]? "the 3 layers under the surface". Surface is at y=H (the topmost). The 3 layers under it are y=H-3, H-2, H-1. Fill with dirt normally, but sand if H≤16, stone if H≥37.

Wait, "dirt (sand if H ≤ 16, stone if H ≥ 37)". So these middle layers are dirt by default, but when H≤16 use sand, when H≥37 use stone.

- surface (y == H): snow if H≥46, stone if H≥37, sand if H≤16, else grass.

Let me code:
```javascript
for (let y = 0; y < 80; y++) {
    let id = 0;
    if (y === 0) id = 3;
    else if (y < H - 3) id = 3;
    else if (y < H) {
        // 3 layers under surface: H-3, H-2, H-1
        id = (H <= 16) ? 4 : (H >= 37 ? 3 : 2);
    } else if (y === H) {
        if (H >= 46) id = 7;
        else if (H >= 37) id = 3;
        else if (H <= 16) id = 4;
        else id = 1;
    }
    // caves override
    if (y >= 3 && y < H - 2) {
        if (noise3(wx*0.09, y*0.09, wz*0.09) > 0.67) id = 0;
    }
    blocks[...] = id;
}
```

Wait, there's an issue: the cave check overrides even y=0 and deep stone. Spec: "Caves: for y between 3 and H−2, if 3D noise at position*0.09 exceeds 0.67, set air." So caves only affect y in [3, H-2). y=0 stays stone. Good. My condition y>=3 && y<H-2 handles that.

But note: when caves carve out the surface block (y=H is not < H-2, so surface not affected). Actually y=H is not < H-2, so surface block never becomes cave air. Good, surface stays. But the 3 layers under surface (H-3,H-2,H-1): cave check is y < H-2, so H-3 qualifies (if >=3), H-2 and H-1 don't. So only H-3 layer can be carved by caves among the near-surface layers. Fine.

Also note: H could be less than 3, making y<H-2 never true and y<H-3 weird. But H = floor(5 + ...) ≥ 5 typically. m in [0,1], m*m in [0,1], *58 → [0,58]. h in [0,1]*10 → [0,10]. So H in [5, 73]. Good, always ≥5.

Also H-3 could be up to 70, H up to 73, within 80. Good. And y<80 loop. When H is large (mountains), surface near y=73, fine.

Edge: y < H-3 when H=5 → y<2 → y=0,1 stone. y=0 already stone. y=1 stone. Then y<H (y=2,3,4) middle layers. y=5 surface. OK.

Now trees. Let me refine:
```javascript
// per-column hash for tree
const th = hash2(wx, wz); // or a dedicated hash
if (th < 0.02) {
    // find grass surface
    let surfY = -1;
    for (let y = 79; y >= 0; y--) {
        if (blocks[x + z*16 + y*256] === 1) { surfY = y; break; }
    }
    if (surfY >= 0 && surfY + 5 <= 79) {
        // trunk
        for (let k = 1; k <= 4; k++) {
            blocks[x + z*16 + (surfY+k)*256] = 5;
        }
        // leaves
        placeLayer(surfY+2, 2); // 5x5
        placeLayer(surfY+3, 2); // 5x5
        placeLayer(surfY+4, 1); // 3x3
        placeLayer(surfY+5, 0); // 1
    }
}
```
where placeLayer(baseY, radius) fills blocks at baseY with offsets, only into air, within chunk bounds.

Wait, "leaves as a 5x5 layer twice, then 3x3, then 1 on top". Two 5x5 layers (y+2, y+3), one 3x3 (y+4), one 1 (y+5). Radius for 5x5 is 2, 3x3 is 1, 1 is 0. Good.

placeLayer:
```javascript
function placeLeafLayer(blocks, lx, lz, baseY, radius) {
    for (let dx = -radius; dx <= radius; dx++) {
        for (let dz = -radius; dz <= radius; dz++) {
            const nx = lx + dx, nz = lz + dz;
            if (nx < 0 || nx >= 16 || nz < 0 || nz >= 16) continue;
            const idx = nx + nz*16 + baseY*256;
            if (baseY < 80 && blocks[idx] === 0) blocks[idx] = 6;
        }
    }
}
```

Note the "only into air" — only set if blocks[idx]===0. Good.

Now the tree hash: I used hash2(wx,wz). The spec says "when a per-column hash < 0.02". Let me use a per-column hash. hash2 is fine.

But there's a subtlety: hash2 might be called with the world coords. Let me make sure it's deterministic per column. Yes.

Now, potential problem: trees could place leaves at baseY >= 80. I guard with surfY+5<=79 and baseY<80 check.

Now let me think about the water and how lakes/beaches appear. Water plane at 14.3. Where terrain H ≤ 16 (beach/low), surface is sand at low y, and water at 14.3 fills above. Since water is just a visual plane at constant height, lakes appear where terrain is below 14.3. Good.

Now, the player spawn: at x=8,z=8. Surface height there. Let me compute after generation.

Let me now also think about the initial meshing. At init:
```javascript
function initWorld() {
    // generate all within dist 5
    for (let dx=-5;dx<=5;dx++) for (let dz=-5;dz<=5;dz++) {
        const cx=pcx+dx, cz=pcz+dz;
        const key=cx+","+cz;
        if (!chunks.has(key)) {
            const chunk={blocks:new Uint8Array(20480),mesh:null};
            chunks.set(key,chunk);
            generateChunkData(cx,cz,chunk.blocks);
        }
    }
    // mesh those whose neighbors ready
    // iterate until stable or a few passes
    let changed = true, passes = 0;
    while (changed && passes < 20) {
        changed = false; passes++;
        for (let dx=-4;dx<=4;dx++) for (let dz=-4;dz<=4;dz++) {
            const cx=pcx+dx, cz=pcz+dz;
            const key=cx+","+cz;
            const chunk=chunks.get(key);
            if (!chunk||!chunk.blocks||chunk.mesh) continue;
            if (neighborReady(cx+1,cz)&&neighborReady(cx-1,cz)&&neighborReady(cx,cz+1)&&neighborReady(cx,cz-1)) {
                buildChunkMesh(cx,cz); changed=true;
            }
        }
    }
    // spawn
    const sy = surfaceHeight(8,8);
    player.pos.set(8, sy+2, 8);
}
```

neighborReady checks chunk.blocks != null.

This should populate the spawn area fully.

Now the frame loop maintains generation/meshing with limits.

Let me also handle the case where player moves far and new chunks need generation — handled by updateWorld.

Let me now also consider: the raycast target outline. I'll use a LineSegments with EdgesGeometry. Update position each frame if targeting.

Let me structure the animation loop with requestAnimationFrame and dt clamped.

```javascript
let last = performance.now();
function animate() {
    requestAnimationFrame(animate);
    const now = performance.now();
    let dt = (now - last)/1000; last = now;
    if (dt > 0.05) dt = 0.05; // clamp
    if (pointerLocked) {
        updatePhysics(dt);
        updateControls(dt);
    }
    updateWorld();
    updateCamera();
    updateTargetOutline();
    updateClouds(dt);
    water.position.x = player.pos.x;
    water.position.z = player.pos.z;
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
```

Wait, calling requestAnimationFrame twice is wrong. Let me structure properly:

```javascript
function animate() {
    requestAnimationFrame(animate);
    ...update...
    renderer.render(scene, camera);
}
```

Inside, do all updates once, then render once. The recursive rAF is at the top. Good.

updateTargetOutline: raycast each frame to get target, update outline position and visibility. But raycast requires chunkMeshes non-empty. Guard.

Let me write updateTarget:
```javascript
let currentTarget = null;
function updateTarget() {
    if (chunkMeshes.length === 0) { outline.visible=false; currentTarget=null; return; }
    const res = raycast();
    if (res) {
        currentTarget = res;
        outline.position.set(res.break.x+0.5, res.break.y+0.5, res.break.z+0.5);
        outline.visible = true;
    } else {
        outline.visible = false;
    }
}
```

The raycast computes break and place cells. Break uses target, place uses cell.

Now, mousedown handlers use currentTarget.

Let me also make sure the break/place only happen when locked and on mousedown.

Now let me also handle: when pointer not locked, overlay shows. When clicking overlay, requestPointerLock.

Also the hotbar selection display.

Let me also handle window resize:
```javascript
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
```

Now, let me consider the fog and far plane. Far 400, fog 40-110. Chunks within 5 = 80 blocks, plus we mesh within 4. Rendering distance ~ up to 5 chunks = 80 blocks. Fog ends at 110. Good, so distant chunks fade into fog. Actually chunks at dist 5 are 80 blocks away, within fog range. Chunks at dist 7 (cleanup threshold) are 112 blocks, just beyond fog. Good.

Wait, we mesh within 4 chunks (64 blocks) but generate within 5. And cleanup at 7. There might be chunks with data but no mesh between 4 and 7. Those won't render (no mesh). Fine.

Hmm, but the meshing condition requires neighbors ready. A chunk at dist 4 might not mesh if a neighbor isn't generated yet. But generation happens first each frame. Over time everything within 4 meshes. Good.

Let me reconsider the meshing neighbor requirement causing delays. When a new chunk is generated at the border, its mesh waits until its 4 neighbors have data. Since generation is limited to 4/frame, and meshing 2/frame, it converges. Good.

Now let me also double-check: the player falls below -20 teleports to spawn. And spawn is above terrain.

Let me also handle jump: only when onGround.

Let me also make sure WASD movement is relative to yaw. Forward vector = (-sin(yaw), 0, -cos(yaw)). When yaw=0, forward = (0,0,-1), pressing W moves -z. Standard. Right = (cos(yaw),0,-sin(yaw)). When yaw=0, right=(1,0,0), D moves +x. Let me verify this is correct for a right-handed system looking down -z. If I look toward -z (forward), right should be +x. Yes. Good.

Now let me write the full HTML.

Let me also add the crosshair HTML:
```html
<div id="crosshair"></div>
```
CSS: position fixed, center, width 20px height 20px, or two crossing lines.

Let me write CSS for crosshair as a small plus using borders or a simple div with a background.

Let me draft the complete file now.

Actually, let me reconsider the noise hash function. "an integer-coordinate hash giving 0–1 (mix with large prime multipliers and xor-shifts)". Let me implement:

```javascript
function hash2(ix, iy) {
    let h = (ix * 1600000037) ^ (iy * 668265267); // large primes
    h = (h ^ (h >> 13)) * 1274269271;
    h = (h ^ (h >> 16)) >>> 0;
    return h / 4294967296;
}
```

Hmm, let me make it more robust. Standard value noise hash:
```javascript
function hash2(ix, iy) {
    let h = ix * 374761393 + iy * 668265267;
    h = (h ^ (h >> 13)) * 1274269271;
    h = (h ^ (h >> 16)) >>> 0;
    return h / 4294967296;
}
```

This gives a deterministic 0-1 value. Good.

For 3D:
```javascript
function hash3(ix, iy, iz) {
    let h = ix*374761393 + iy*668265267 + iz*374761397;
    h = (h ^ (h >> 13)) * 1274269271;
    h = (h ^ (h >> 16)) >>> 0;
    return h / 4294967296;
}
```

Now noise2 uses bilinear with smoothstep. fractal2 combines 4 octaves.

Let me write noise2:
```javascript
function valueNoise2(x, y) {
    const x0 = Math.floor(x), y0 = Math.floor(y);
    const x1 = x0+1, y1 = y0+1;
    const sx = x - x0, sy = y - y0;
    const n00 = hash2(x0, y0);
    const n10 = hash2(x1, y0);
    const n01 = hash2(x0, y1);
    const n11 = hash2(x1, y1);
    const u = sx*sx*(3-2*sx); // smoothstep (Perlin's)
    const v = sy*sy*(3-2*sy);
    const a = n00 + u*(n10-n00);
    const b = n01 + u*(n11-n01);
    return a + v*(b-a);
}
```
This is bilinear interpolation with smoothstep easing. Good.

fractal2:
```javascript
function fbm2(x, y) {
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let i = 0; i < 4; i++) {
        sum += amp * valueNoise2(x*freq, y*freq);
        norm += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return sum/norm;
}
```

valueNoise3:
```javascript
function valueNoise3(x, y, z) {
    const x0=Math.floor(x),y0=Math.floor(y),z0=Math.floor(z);
    const u = x-x0, v=y-y0, w=z-z0;
    const se = t=>t*t*(3-2*t);
    const uu=se(u), vv=se(v), ww=se(w);
    const h = (hx,hy,hz)=>hash3(hx,hy,hz);
    const c000=h(x0,y0,z0),c100=h(x0+1,y0,z0),c010=h(x0,y0+1,z0),c110=h(x0+1,y0+1,z0);
    const c001=h(x0,y0,z0+1),c101=h(x0+1,y0,z0+1),c011=h(x0,y0+1,z0+1),c111=h(x0+1,y0+1,z0+1);
    const lx00=c000+(c100-c000)*uu;
    const lx10=c010+(c110-c010)*uu;
    const lx01=c001+(c101-c001)*uu;
    const lx11=c011+(c111-c011)*uu;
    const ly0=lx00+(lx10-lx00)*vv;
    const ly1=lx01+(lx11-lx01)*vv;
    const l=ly0+(ly1-ly0)*ww;
    return l;
}
```

Good.

Now, one concern: valueNoise2 returns values in [0,1] but with only 2 octaves of hashing it's fine. fbm2 returns roughly [0,1].

For column height: H = floor(5 + m*m*58 + h*10) where m = fbm2(wx*0.004, wz*0.004), h = fbm2(wx*0.02, wz*0.02). Both in [0,1]. m*m emphasizes low values (plains), h adds detail. H ranges roughly [5, 73]. Good.

Now let me finalize and write everything into the HTML.

Let me also reconsider the "4 neighbors" for meshing — I'll define neighborReady(cx,cz) = chunk exists and chunk.blocks != null.

Now, there's a subtle issue with the meshing loop in updateWorld: it builds meshes for chunks within dist 4 whose neighbors are ready. But when we first spawn, initWorld handles it. During gameplay, new chunks at the border get generated then meshed. Fine.

Let me also make sure that when we delete a chunk entry (>7), we also remove its mesh from chunkMeshes. In cleanup:
```javascript
if (d > 7) {
    if (chunk.mesh) {
        const i = chunkMeshes.indexOf(chunk.mesh);
        if (i>=0) chunkMeshes.splice(i,1);
        chunk.mesh.geometry.dispose();
        scene.remove(chunk.mesh);
    }
    chunks.delete(key);
}
```

Now let me write it all out.

One more consideration: the raycaster direction. I'll compute it from yaw/pitch:
```javascript
const dir = new THREE.Vector3(
    -Math.sin(yaw) * Math.cos(pitch),
    Math.sin(pitch),
    -Math.cos(yaw) * Math.cos(pitch)
);
```
Wait, standard: 
- yaw rotates around Y. Looking direction without pitch: (-sin(yaw), 0, -cos(yaw)).
- pitch rotates around X (looking up/down). Applying pitch: the vertical component becomes sin(pitch), and horizontal scales by cos(pitch).

Let me define:
```javascript
const cp = Math.cos(pitch);
const dir = new THREE.Vector3(-Math.sin(yaw)*cp, Math.sin(pitch), -Math.cos(yaw)*cp);
```
At yaw=0,pitch=0: dir=(0,0,-1). Good. Look up (pitch>0): dir.y = sin(pitch)>0. Good.

Then:
```javascript
raycaster.set(camera.position, dir);
```

Actually I can use raycaster.set(origin, direction). It normalizes internally.

Now the face normal from intersect result is in world space (mesh at origin). Good.

Let me also verify the break/place coordinate math. Hit point p on a face, normal n points outward from the hit block. 
- Break target: p - n*0.5 → the block being hit (inside it). floor gives integer coords.
- Place cell: p + n*0.5 → the adjacent block outside. floor gives integer coords.

Yes, that matches spec.

Now, the outline should highlight the break target. Position at break.x+0.5 etc.

Let me now also make sure about the "Only while locked" for break/place. And the context menu suppression.

Let me also add: when not locked, we shouldn't process break/place. The mousedown handler checks pointerLocked.

Also, the overlay click → requestPointerLock. But the overlay covers the screen, so clicking it triggers lock request. Good.

Now, there's a subtlety: after pointer lock is acquired, mousemove events have movementX/Y. Good.

Let me also handle the case where the user presses Esc (lock released) → overlay reappears. pointerlockchange handles it.

Let me write the final HTML now. I'll be thorough.

Let me reconsider the water material opacity and render order. Transparent water behind terrain. Set renderOrder low, depthWrite false maybe. Let me keep simple: MeshLambertMaterial with transparent true, opacity 0.5. It will render after opaque geometry by default (Three sorts transparent objects after opaque). Good.

Actually, MeshLambertMaterial supports transparent. Fine.

Now the clouds: BoxGeometry with MeshLambertMaterial transparent white. Additive? No, just transparent white. They'll be visible against sky. Good.

Let me also make clouds not affected much by light — Lambert will shade them based on normal. A flat box at y=90 with directional light from above will be lit on top. Fine.

Let me finalize.

Let me reconsider dt-based movement. speed 5.5 m/s. move = direction * speed * dt. Good.

Gravity 25/s². Jump 8.5. These match spec.

Let me write it all.

Also need to make sure the player can't pass through the floor at y=0 (unbreakable stone). Collision handles it since y=0 is stone.

Let me also handle the spawn: player starts above terrain. If terrain at (8,8) is high (mountain), spawn there. Fine.

Let me also double check: surfaceHeight scans from 79 down for first non-air. But caves might have made upper blocks air. The first non-air from top is the actual surface. Good. But if the whole column is cave air near top... unlikely. Fine.

Now, let me also reconsider: the spec says spawn "above terrain at x=8, z=8". So x=8, z=8 (which is chunk 0,0 local 8,8). Good.

Let me write the code.

Actually, I realize there might be an issue with Float32BufferAttribute deprecation in r128. Let me check: In r128, THREE.Float32BufferAttribute still exists (deprecated but present until r144ish). THREE.BufferAttribute also exists. I'll use THREE.BufferAttribute which is the non-typed-name. Actually BufferAttribute is generic (takes typed array). Let me use:
```javascript
new THREE.BufferAttribute(new Float32Array(pos), 3)
```
This is safe in r128.

Similarly for normals and colors.

Let me finalize the code.

Let me also add a subtle detail: the directional light. I'll position it and it'll shade. Let me set:
```javascript
sun.position.set(0.5, 1, 0.5).normalize().multiplyScalar(100);
```
Actually DirectionalLight with position and default target origin. Just set position to some direction. Let me set sun.position.set(100, 200, 150). It points toward origin (0,0,0) by default (target). Good.

Now let me also reconsider ambient + directional with Lambert. Lambert uses light components. Ambient 0.65, directional 0.8. Total max ~1.45 but clamped by material. Fine. Vertex colors multiply with light? MeshLambertMaterial with vertexColors uses vertex colors as the base color and applies lighting to it. Yes — vertexColors means the geometry colors are the albedo, and lighting (ambient+directional) is applied multiplicatively. So a vertex color of (0.5,0.5,0.5) with full light → 0.5. Good. This gives the fake lighting baked into vertex colors, plus real lighting from lights. Actually with vertexColors and a directional light, the final = vertexColor * (ambient + directional * dot(normal, lightDir)). This might over-darken sideways faces. Hmm.

Wait, the spec says "Fake lighting: multiply the block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms." This is baked into vertex colors. Then real lighting (ambient 0.65 + directional 0.8) is applied on top. That means top faces get 1.0 * (0.65 + 0.8*cosAngle). That could be brighter than intended. But the spec explicitly wants both: fake lighting baked AND real lights. So the vertex colors encode fake lighting, and the lights modulate further. That's what the spec describes. Let me just follow it. The result might look a bit flat but that's per spec.

Actually, wait. Let me re-read: "Unit cubes, rendered with vertex colors and ONE shared MeshLambertMaterial. Fake lighting: multiply the block color by 1.0 on top faces, 0.8 on sides, 0.55 on bottoms."

And separately: "Ambient light 0.65 plus one directional light 0.8."

So vertex colors = blockColor * fakeLight. Material = MeshLambertMaterial with vertexColors. Lights add. This is the intended design. I'll implement as described.

Hmm, but combining real directional light with vertex colors can make the fake lighting inconsistent (e.g., a north-facing wall vs south-facing both get 0.8 fake but different real lighting). But the spec says to do exactly this, so I'll follow it. It produces a recognizable Minecraft-like look.

Actually, thinking more: maybe the intent is that the "fake lighting" IS the primary lighting and the real lights are just ambient + a bit. Since vertexColors multiply by the scene lighting, and ambient is 0.65 (high), the variation from directional is limited. It'll look fine-ish. Let me proceed.

Let me write everything now.

Let me also make sure to set renderer antialias and pixel ratio.

```javascript
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);
```

canvas = renderer.domElement.

Now pointer lock: canvas.requestPointerLock(). And document.pointerLockElement === canvas.

Let me write the overlay with title, controls list, "Click to play".

Controls list:
- WASD move, Space jump, Shift? (spec doesn't mention sprint, skip)
- Left click break, Right click place
- 1-7 or wheel select block
- Esc release mouse

Let me write the overlay content.

Now, let me also make sure clicking the canvas (not overlay) while not locked doesn't do anything weird. The overlay is on top (z-index high) and pointer-events... Actually the overlay is a fullscreen div covering the canvas. Clicking it → requestPointerLock. The canvas is behind. So clicks go to overlay. Good. Once locked, overlay hidden.

But wait, if overlay is display:none when locked, then clicks hit the canvas. Good.

Let me set overlay z-index high, pointer-events auto. When display:none, no pointer events.

Let me now also handle: the start overlay appears initially (display flex). Click → lock. On lock change, if locked hide overlay, else show.

Let me code the lock change:
```javascript
document.addEventListener('pointerlockchange', () => {
    pointerLocked = document.pointerLockElement === canvas;
    overlay.style.display = pointerLocked ? 'none' : 'flex';
});
```

And overlay click:
```javascript
overlay.addEventListener('click', () => {
    canvas.requestPointerLock();
});
```

Good.

Now, one concern: requestPointerLock from a click handler is allowed (user gesture). Good.

Let me write the full thing now. I'll be careful with all the pieces.

Let me reconsider the meshing neighbor requirement causing delays. When a new chunk is generated at the border, its mesh waits until its 4 neighbors have data. Since generation is limited to 4/frame, and meshing 2/frame, it converges. Good.

Let me also reconsider: do I need to worry about the player clipping into blocks horizontally? Collision reverts position, so no. Good.

Let me also make sure the player box maxY uses floor(pos.y + 1.8). Let me reconsider potential issue: when standing on ground at y=groundTop, pos.y = groundTop + small. floor(pos.y) = groundTop. floor(pos.y+1.8) = groundTop+1 (approx). So checks blocks groundTop and groundTop+1. The block at groundTop is the floor we stand on (solid, but we're on top of it — our feet are just above). Wait, if feet are just above groundTop block's top face, then pos.y ≈ groundTop+1 (in block coords, the top face of block at y=groundTop is at coordinate groundTop+1). So pos.y ≈ groundTop+1.001. floor(pos.y) = groundTop+1?? No: floor(groundTop+1.001) = groundTop+1. Hmm, that would check block groundTop+1 which is air (above floor). That's wrong — we'd be checking the air block above the floor as part of our body.

Wait, let me reconsider. Block at integer y occupies [y, y+1] in world coords. So block at y=groundTop occupies [groundTop, groundTop+1]. Its top face is at world y = groundTop+1. If player stands on top, feet at world y = groundTop+1 + epsilon. So pos.y = groundTop+1+eps. floor(pos.y) = groundTop+1. So our box's minY = groundTop+1. That block (groundTop+1) is the block ABOVE the floor. If it's air, no collision. Good — we don't collide with the floor we stand on via the minY check (feet are above it). 

But wait, then how do we detect landing? When falling, pos.y decreases. When feet reach groundTop+1 (top of floor block), pos.y = groundTop+1. floor(pos.y) = groundTop+1. Our box spans [groundTop+1, groundTop+2.8]. The floor block is at groundTop ([groundTop, groundTop+1]) — does our box overlap it? Our minY=groundTop+1, floor block max = groundTop+1. Overlap requires minY < floorMax AND floorMin < ourMax. minY=groundTop+1, floorMax=groundTop+1. groundTop+1 < groundTop+1 is false. So no overlap with floor block. But the block at groundTop+1 (air) — no collision. So we'd fall through?!

No wait. Let me reconsider. When falling and we hit the floor, the collision detection should stop us. Let me reconsider the box. Player height 1.8, so box spans [pos.y, pos.y+1.8]. Feet at pos.y. When feet are at world y = groundTop+1 (just above floor top face at groundTop+1)... 

Hold on. Floor block at y=groundTop occupies [groundTop, groundTop+1]. Top face at groundTop+1. Player feet should rest at groundTop+1 (touching top face). So pos.y = groundTop+1 exactly (or just above).

Our box: [groundTop+1, groundTop+1+1.8] = [groundTop+1, groundTop+2.8]. 
Blocks in this range: floor block [groundTop, groundTop+1] — overlaps our box? Our box min y = groundTop+1, floor max y = groundTop+1. They touch at a boundary but don't overlap (open/closed). In terms of block grid: blocks we check are floor(pos.y)=groundTop+1 to floor(pos.y+1.8-eps)=groundTop+2. So we check blocks groundTop+1 and groundTop+2. Both air (assuming). No collision. So we keep falling?? That's wrong.

I think the issue is my box representation. Let me reconsider. The standard Minecraft collision: player box from feet (pos.y) to head (pos.y+height). To detect standing on a block, we check if any block is within [feet, head] vertically AND horizontally overlapping. When feet are at groundTop+1 (resting on floor block whose top is groundTop+1), the floor block occupies [groundTop, groundTop+1]. Our feet at groundTop+1 is exactly at the top face. Is the floor block "within" our box [groundTop+1, groundTop+2.8]? The floor block's top is groundTop+1 = our feet. So the block is just below our feet, not within. Hence no collision detected, and we fall.

This is a known subtlety. The fix: when falling, we should detect the block whose top face we're resting on. Actually the issue is that our feet exactly at groundTop+1 means we're AT the top of the floor block. The collision should have stopped us earlier when feet were slightly above groundTop+1.

Let me reconsider. As we fall, pos.y decreases. Before landing, pos.y is slightly greater than groundTop+1 (e.g., groundTop+1.5, mid-way... no). Let me trace: falling, pos.y decreases from high to low. When pos.y = groundTop+1.001 (just above floor top), our box = [groundTop+1.001, groundTop+2.801]. Blocks checked: floor(1.001)=groundTop+1, floor(2.801-eps)=groundTop+2. Air. No collision. Continue falling. Next frame pos.y = groundTop+0.99 (fell through!). Box=[groundTop+0.99, groundTop+2.79]. Blocks: floor(0.99)=groundTop, floor(2.79)=groundTop+2. Check groundTop (floor block, solid!) → collision! Revert. So we bounce back to pos.y=groundTop+1.001. 

So it does work, but there's a slight overshoot then correction. Because we check floor(pos.y) which when pos.y=groundTop+0.99 gives groundTop (the floor block), detecting collision. So the player ends up resting at pos.y=groundTop+1.001 (feet just above floor top). That's correct! The overshoot is sub-block and corrected. Good.

But wait, the very first frame after landing: pos.y went from groundTop+1.001 to groundTop+0.99 (fell 0.011). Collision detected (floor block at groundTop now in range). Revert to groundTop+1.001. Set vel.y=0, onGround=true. Good. So player rests at groundTop+1.001. 

But there's floating point: pos.y=groundTop+1.001, floor = groundTop+1. The block at groundTop+1 is air. We never collide with it (it's air). Good. And floor block at groundTop: when would we check it? Only when pos.y < groundTop+1, i.e., we've fallen into it. Which triggers correction. Good.

So the collision works despite the apparent issue. 

But hold on, there's still a subtle problem: when grounded at pos.y=groundTop+1.001, gravity adds a tiny amount each frame, making pos.y decrease to groundTop+0.999, then collision detects groundTop block, reverts to groundTop+1.001, vel.y=0, onGround=true. This keeps player anchored. But the revert each frame — is it stable? pos.y oscillates between groundTop+1.001 and groundTop+0.999, reverting to 1.001. Stable enough. Good.

Actually, wait — I set onGround=false at the start of Y handling, then if collision with dy<0 set onGround=true. But when grounded, dy is small negative (gravity). We detect collision, revert, set onGround=true. Next frame same. Good. Jump works because we check onGround before applying.

Hmm, but there's a timing issue: we check onGround for jump at the start (before gravity). When grounded (onGround=true from previous frame's landing), press space → vel.y=8.5. Then gravity reduces it. Good.

Let me also make sure: after jumping, onGround becomes false when we move up without collision. And when we come down and land, onGround=true again. Good.

Let me also handle the epsilon in maxY. I'll use floor(pos.y + 1.8 - 1e-4) to avoid the head sticking into a block when exactly aligned. Actually, let me reconsider whether to subtract epsilon. Consider jumping up into a ceiling: head at pos.y+1.8. If there's a block at floor(pos.y+1.8), we collide. With epsilon, floor(pos.y+1.8-1e-4) might exclude it if head is exactly at integer. Minor. Let me keep it simple and NOT subtract epsilon: maxY = floor(pos.y + 1.8). This is standard. The head-in-ceiling case: if head reaches into ceiling block, we detect and revert. Good.

Actually, let me reconsider using floor(pos.y+1.8) vs the overshoot issue for upward. If we jump and head hits ceiling at exactly the block, floor(pos.y+1.8) includes it, collision detected, revert. Good.

Let me finalize with maxY = Math.floor(pos.y + 1.8).

Wait, but there's a subtle double-count: if pos.y+1.8 is exactly an integer (e.g., 5.0), floor(5.0)=5, block 5 occupies [5,6]. Head at 5.0 is at bottom of block 5. Our box [pos.y, 5.0]. Does it overlap block 5 [5,6]? Box max=5.0, block min=5. 5.0 < 5 is false (overlap needs boxMax > blockMin → 5.0 > 5 true, and blockMax > boxMin → 6 > pos.y true). So overlap! So head at exactly 5.0 collides with block 5. That's correct (head enters block 5). Good.

OK let me just write it.

Let me also reconsider: for the collision box, I check blocks from floor(minX) to floor(maxX) inclusive, etc. Using <= maxX. Let me make sure inclusive bounds catch all overlapping blocks. A block at bx overlaps player box if bx < px1 && bx+1 > px0 (using strict inequalities for overlap). My loop floor(minX)..floor(maxX): 
- minX = floor(px-0.3), maxX = floor(px+0.3). 
- The block at floor(px+0.3): does it overlap? block occupies [floor(px+0.3), floor(px+0.3)+1]. px1=px+0.3. Overlap if floor(px+0.3) < px1 (=px+0.3) → yes if floor < px+0.3, true unless px+0.3 is integer. And block max > px0. So generally overlaps. Including it is correct. Edge case when px+0.3 is integer: floor = px+0.3, block [px+0.3, px+1.3]. Overlap with box [px-0.3, px+0.3]? Need block min < box max → px+0.3 < px+0.3 false. So no overlap, but we included it (harmless, it's likely air anyway). Fine.

Good, inclusive bounds with floor are correct.

Now let me write the complete file.

Let me also think about performance: meshing loops 16*16*80 = 20480 blocks * 6 faces * neighbor getBlock calls. getBlock does a Map lookup. That's ~20480*6 = 122880 Map lookups per chunk. Acceptable for building meshes occasionally (limited to 2/frame). Fine.

Let me write.

Actually, let me reconsider the FACES array indexing and make it clean. I'll define it once globally.

Let me also reconsider: the meshing uses getBlock for neighbor checks which reads chunk.blocks. For the chunk being meshed, we already have blocks. For neighbors, getBlock reads their blocks or returns 0 if missing. During normal meshing (after data generated), neighbors have data. Good.

Now, writing the actual HTML. Let me assemble.

I need to be careful about the order of declarations (functions hoisting). Since everything is in script, function declarations are hoisted, but variables with const/let are not. Let me declare constants (FACES, BLOCK_RGB) before use. Functions can be declared anywhere (hoisted).

Let me write the script.

For the water plane, I want it to not interfere with gameplay. Just visual.

Let me also add fog exponent? No, plain Fog.

Let me write it all now.

Let me reconsider the clouds "wrapping around the player". I'll wrap their world position relative to player within ±128.

```javascript
function wrap(v, ref, range) {
    let d = v - ref;
    if (d > range) d -= range*2;
    else if (d < -range) d += range*2;
    return ref + d;
}
```
Apply to cloud x,z with ref=player.pos, range=128.

Drift: cloud.x += speed*dt. Then wrap.

Let me set cloud speeds small (1-3 m/s).

Now let me also make sure clouds don't clip through player vertically — they're at y=90, player much lower. Fine.

Alright, writing now.

Let me also double-check the "max 4 per frame" generation and "max 2 per frame" meshing in the game loop (not init). And cleanup >7.

Let me write updateWorld with these limits.

Let me also reconsider: should generation happen even when not locked (overlay showing)? Probably yes, to keep world loading. But movement paused. Let me run updateWorld always. Fine.

Now, let me write the complete HTML file.

I'll also include a small note: the file should be self-contained.

Let me write it.

Actually, let me reconsider one thing about raycasting and the outline. The raycast target updates every frame (expensive-ish but fine, one raycast). The outline follows. When breaking, we use the current break target. Good.

But there's a subtlety: raycast returns break and place. We store currentTarget. Mousedown uses it. Good.

Let me also ensure the raycast max distance 6 is applied: intersectObjects returns hits sorted by distance; we take the first and check distance <= 6. Actually intersectObjects already returns all intersections; the first is closest. If closest distance > 6, ignore. Let me check hit[0].distance.

Let me write raycast:
```javascript
function getTarget() {
    if (chunkMeshes.length === 0) return null;
    raycaster.set(camera.position, dir);
    const hits = raycaster.intersectObjects(chunkMeshes, false);
    if (hits.length === 0 || hits[0].distance > 6) return null;
    const p = hits[0].point, n = hits[0].face.normal;
    return {
        break: { x: Math.floor(p.x - n.x*0.5), y: Math.floor(p.y - n.y*0.5), z: Math.floor(p.z - n.z*0.5) },
        place: { x: Math.floor(p.x + n.x*0.5), y: Math.floor(p.y + n.y*0.5), z: Math.floor(p.z + n.z*0.5) }
    };
}
```

dir recomputed each frame from yaw/pitch.

Now break/place functions use getTarget() result.

Let me finalize.

Also, I should make sure the camera position used in raycaster is the updated camera position (with eye offset). I update camera position in updateCamera before rendering. The raycast should use camera position. Let me compute dir and use camera.position. Order: updatePhysics, updateControls, updateWorld, updateCamera, then getTarget (uses camera.position), updateTarget (outline), render.

Let me structure animate():
```javascript
function animate() {
    requestAnimationFrame(animate);
    const now = performance.now();
    let dt = (now - last)/1000; last = now;
    if (dt > 0.05) dt = 0.05;
    if (pointerLocked) {
        updateControls(dt);
        updatePhysics(dt);
    }
    updateWorld();
    updateCamera();
    // target
    const tgt = getTarget();
    if (tgt) { currentTarget = tgt; outline.position.set(tgt.break.x+0.5, tgt.break.y+0.5, tgt.break.z+0.5); outline.visible = true; }
    else outline.visible = false;
    updateClouds(dt);
    water.position.x = player.pos.x; water.position.z = player.pos.z;
    renderer.render(scene, camera);
}
```

updateControls sets velocity from keys. updatePhysics applies gravity + collision.

Let me write updateControls:
```javascript
function updateControls(dt) {
    const speed = 5.5;
    const sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
    const fwd = new THREE.Vector3(-sin, 0, -cos);
    const right = new THREE.Vector3(cos, 0, -sin);
    const mv = new THREE.Vector3();
    if (keys['KeyW']) mv.add(fwd);
    if (keys['KeyS']) mv.sub(fwd);
    if (keys['KeyD']) mv.add(right);
    if (keys['KeyA']) mv.sub(right);
    if (mv.lengthSq() > 0) { mv.normalize().multiplyScalar(speed*dt); }
    player.vel.x = mv.x;
    player.vel.z = mv.z;
    if (keys['Space'] && player.onGround) { player.vel.y = 8.5; player.onGround = false; }
}
```

Wait, I set onGround=false when jumping. But updatePhysics sets onGround based on collision. Let me keep jump logic in updateControls and onGround management in updatePhysics. Setting onGround=false here is fine (we're leaving the ground).

updatePhysics:
```javascript
function updatePhysics(dt) {
    player.vel.y -= 25*dt;
    if (player.vel.y < -60) player.vel.y = -60;
    const dx = player.vel.x*dt, dy = player.vel.y*dt, dz = player.vel.z*dt;
    // X
    player.pos.x += dx;
    if (collides()) { player.pos.x -= dx; player.vel.x = 0; }
    // Z
    player.pos.z += dz;
    if (collides()) { player.pos.z -= dz; player.vel.z = 0; }
    // Y
    player.onGround = false;
    player.pos.y += dy;
    if (collides()) {
        player.pos.y -= dy;
        player.vel.y = 0;
        if (dy < 0) player.onGround = true;
    }
    // fall check
    if (player.pos.y < -20) {
        player.pos.set(8, surfaceHeight(8,8)+2, 8);
        player.vel.set(0,0,0);
    }
}
```

Hmm, setting onGround=false at start of Y, then if collision and dy<0 set true. But if we're grounded and gravity makes dy small negative, we collide and set onGround=true. Good. If we jump (dy>0), no collision, onGround stays false. Good. If we're falling and land (dy<0), collision, onGround=true. Good.

But wait: setting onGround=false then landing in same frame — we set true. Good. But what if we set onGround=false at start and then DON'T collide (falling freely)? onGround stays false. Good.

collides():
```javascript
function collides() {
    const minX = Math.floor(player.pos.x - 0.3);
    const maxX = Math.floor(player.pos.x + 0.3);
    const minY = Math.floor(player.pos.y);
    const maxY = Math.floor(player.pos.y + 1.8);
    const minZ = Math.floor(player.pos.z - 0.3);
    const maxZ = Math.floor(player.pos.z + 0.3);
    for (let bx = minX; bx <= maxX; bx++)
        for (let by = minY; by <= maxY; by++)
            for (let bz = minZ; bz <= maxZ; bz++)
                if (getBlock(bx, by, bz) !== 0) return true;
    return false;
}
```

Good.

Now let me write the whole HTML.

Let me reconsider the hotbar HTML/CSS. I'll create slots dynamically or statically. Statically is simpler.

```html
<div id="hotbar">
  <div class="slot" data-i="0"><div class="swatch" style="background:#4caf50"></div><span class="num">1</span></div>
  ...7...
</div>
```

CSS positions fixed bottom center.

Let me write CSS:
```css
body { margin:0; overflow:hidden; font-family: sans-serif; }
#crosshair { position:fixed; top:50%; left:50%; width:20px; height:20px; margin:-10px 0 0 -10px; pointer-events:none; }
#crosshair:before, #crosshair:after { content:''; position:absolute; background:#fff; }
#crosshair:before { left:9px; top:0; width:2px; height:100%; }
#crosshair:after { top:9px; left:0; height:2px; width:100%; }
#hotbar { position:fixed; bottom:20px; left:50%; transform:translateX(-50%); display:flex; gap:4px; padding:6px; background:rgba(0,0,0,0.6); border-radius:6px; }
.slot { width:44px; height:44px; border:2px solid rgba(255,255,255,0.3); position:relative; cursor:pointer; }
.slot.active { border-color:#fff; }
.swatch { position:absolute; inset:4px; border-radius:3px; }
.num { position:absolute; bottom:1px; left:3px; color:#fff; font-size:12px; }
#overlay { position:fixed; inset:0; background:rgba(0,0,0,0.85); color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; z-index:10; cursor:pointer; }
#overlay h1 { font-size:48px; margin-bottom:10px; }
#overlay ul { text-align:left; margin-top:20px; line-height:1.8; }
```

Let me finalize.

I think I have all pieces. Let me write the complete file.

Let me reconsider the initialization ordering. I'll put initWorld() call before starting the animation loop. initWorld generates and meshes spawn region, sets player spawn.

Let me also make sure surfaceHeight works after initWorld (chunks generated). Yes.

Now, let me write the final HTML.

One more: the `dir` variable for raycasting is recomputed in getTarget. Let me just compute inline.

Also, I need to make sure camera.rotation order YXZ and set yaw/pitch. Let me update:
```javascript
function updateCamera() {
    camera.position.x = player.pos.x;
    camera.position.y = player.pos.y + 1.62;
    camera.position.z = player.pos.z;
    camera.rotation.order = "YXZ";
    camera.rotation.y = player.yaw;
    camera.rotation.x = player.pitch;
    camera.rotation.z = 0;
}
```

Good.

Let me write it all now. Final assembly.

Wait, I should double check THREE.Raycaster exists in r128 global. Yes, THREE.Raycaster.

Also THREE.EdgesGeometry, THREE.LineSegments, THREE.LineBasicMaterial — all exist.

THREE.BoxGeometry, THREE.PlaneGeometry — exist.

THREE.AmbientLight, THREE.DirectionalLight — exist.

THREE.Fog — exists.

THREE.Vector3 — exists.

THREE.BufferAttribute — exists.

Good.

Let me write.

Actually, I realize for the outline I'll use EdgesGeometry(BoxGeometry(1,1,1)) with LineSegments and LineBasicMaterial black. Let me create once.

```javascript
const outlineGeo = new THREE.BoxGeometry(1.002, 1.002, 1.002);
const outlineMat = new THREE.LineBasicMaterial({ color: 0x000000 });
const outline = new THREE.LineSegments(outlineGeo, outlineMat);
outline.visible = false;
scene.add(outline);
```

Good.

Now let me write the complete file. I'll be comprehensive.

Let me reconsider: should I disable context menu on the whole document? Yes: document.addEventListener('contextmenu', e => e.preventDefault()).

Also wheel event for hotbar: add with passive:false to preventDefault scroll.

Let me write.

Final check on tree: "when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up". "trunk fits inside the chunk" — I interpret as surfY+4 <= 79 (trunk top within world height) and surface is grass. Let me also ensure the leaves fit. I check surfY+5 <= 79. Good.

Let me write placeLeafLayer to guard baseY < 80 and baseY >= 0.

Alright, writing now.

Let me also reconsider: generateChunkData is called with (cx, cz, blocks). Inside, loops lx,lz, computes wx,wz. Good.

Let me write the whole thing carefully.

I'll now produce the final code block.

Let me reconsider the fractal noise frequencies. m = fbm2(wx*0.004, wz*0.004) — large scale (plains). h = fbm2(wx*0.02, wz*0.02) — medium detail. H = floor(5 + m*m*58 + h*10). With m in [0,1], m*m in [0,1], *58 → [0,58]. Plus 5 → [5,63]. Plus h*10 [0,10] → [5,73]. Good, within [0,79].

Now, one concern: for mountains H≥37 gives stone middle layers and stone surface (H≥37 but <46 → stone surface). H≥46 → snow. So peaks ≥46 get snow. Good.

Beaches: H≤16 → sand surface and sand middle. Water at 14.3. So beaches at low areas. Good.

Grass plains: 16 < H < 37 → grass surface, dirt under. Good.

Let me finalize.

I'm fairly confident. Let me write the complete HTML.

Actually, let me reconsider whether MeshLambertMaterial with vertexColors and a directional light will look bad. The directional light direction: sun at (100,200,150) pointing to origin. For a face with normal N, lighting = ambient + directional * max(dot(N, lightDir), 0). With ambient 0.65 and directional 0.8. Top face normal (0,1,0), lightDir normalized ≈ (0.36, 0.72, 0.57). dot = 0.72. So top face lighting = 0.65 + 0.8*0.72 = 0.65+0.58 = 1.23. Vertex color fake lighting 1.0. Final ≈ 1.23 * basecolor. Slightly bright but ok. Side face (0,0,1) dot with light = 0.57. lighting = 0.65+0.456=1.1.56. Fake 0.8. Final 0.8*1.155=0.92. Bottom fake 0.55, normal (0,-1,0) dot = -0.72 → directional contributes 0. lighting=0.65. Final 0.55*0.65=0.36. So bottom is darker. Good, gives depth.

This looks reasonable — top brightest, bottom darkest. The fake lighting dominates since it's multiplied. Actually the real light modulates the fake, so effective = fake * (0.65 + 0.8*dot). This preserves the fake lighting gradient (top 1.0, side 0.8, bottom 0.55) scaled by real lighting. Looks good enough.

OK writing now. Let me produce the final file.

Let me make sure to include everything: HTML structure, CSS, script.

I'll write it out fully now.

Actually, I want to double-check the neighbor check in meshing handles the case where the neighbor chunk exists but we're reading its blocks correctly. getBlock(wx+nx, wy+ny, wz+nz): computes neighbor's chunk coords, reads its blocks array at local index. Correct.

Also, when meshing chunk at cx,cz, and a neighbor block at the border, getBlock reads the correct neighbor chunk. Good.

Let me write.

Also, I need to handle: what if getBlock is called with y outside 0-79 during meshing? Returns 0. The face check: if neighbor is air (0), add face. For y=79 (top), top face neighbor y=80 → getBlock returns 0 (out of range) → add top face. Good, top exposed. For y=0 bottom neighbor y=-1 → 0 → add bottom face. But y=0 is unbreakable stone, and below is air (void), so bottom face renders. That's fine (we see under the world). Acceptable.

Alright. Writing final.

Let me also reconsider: the player spawn y. surfaceHeight(8,8) finds first non-air from top. At (8,8), chunk 0,0. Generated. Should be fine. Spawn there+2.

Let me write the complete file now.

I'll write it and then review for bugs.

Let me also ensure the animation loop starts after initWorld.

Final structure:
1. HTML head with CSS
2. Body: canvas container (renderer appends), overlay, crosshair, hotbar
3. Script: everything

Let me write.

For the overlay click to lock — but the overlay also has the title and controls. Clicking anywhere on overlay locks. Good.

Let me write the controls list clearly.

OK here's the final code.

Actually, let me reconsider the wheel event and passive. I'll add:
```javascript
canvas.addEventListener('wheel', function(e) {
    if (!pointerLocked) return;
    selectSlot((selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7);
    e.preventDefault();
}, { passive: false });
```

And keydown for digits:
```javascript
window.addEventListener('keydown', function(e) {
    const c = e.code;
    if (c >= 'Digit1' && c <= 'Digit7') selectSlot(parseInt(c.slice(5),10)-1);
});
```

But digit keys should probably only work when locked? The spec says "keys 1–7 or mouse wheel". Let me allow always but it's fine. Actually to avoid interfering, maybe only when locked. But hotbar is visible always. Let me allow always. Hmm, but if not locked and you press 1, it selects. That's fine, applies when you lock. Let me allow always.

selectSlot:
```javascript
function selectSlot(i) {
    selected = (i + 7) % 7;
    const slots = document.querySelectorAll('.slot');
    slots.forEach((s,idx) => s.classList.toggle('active', idx === selected));
}
```

Initialize selected=0.

Now let me write everything.

Let me also add: on window resize, update camera aspect and renderer size.

Writing now. Final.

Let me reconsider the clouds array creation with Math.random — allowed for clouds. But let me double check the spec doesn't forbid. It's under Terrain section. Clouds separate. I'll use Math.random for cloud size/offset. Fine.

Actually, to be safe and avoid any "no Math.random" misreading, let me use the hash function for cloud positions too. But that's more code. The spec's "no Math.random" is clearly under Terrain. I'll use Math.random for clouds — it's fine and simpler.

Let me write.

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
	html, body { margin: 0; padding: 0; overflow: hidden; width: 100%; height: 100%; background: #87ceeb; font-family: sans-serif; }
	canvas { display: block; }
	#crosshair { position: fixed; top: 50%; left: 50%; width: 20px; height: 20px; margin: -10px 0 0 -10px; pointer-events: none; z-index: 5; }
	#crosshair:before, #crosshair:after { content: ''; position: absolute; background: rgba(255,255,255,0.85); }
	#crosshair:before { left: 9px; top: 0; width: 2px; height: 100%; }
	#crosshair:after { top: 9px; left: 0; height: 2px; width: 100%; }
	#hotbar { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 4px; padding: 6px; background: rgba(0,0,0,0.55); border-radius: 6px; z-index: 5; }
	.slot { width: 46px; height: 46px; border: 2px solid rgba(255,255,255,0.35); position: relative; cursor: pointer; border-radius: 4px; }
	.slot.active { border-color: #fff; box-shadow: 0 0 6px rgba(255,255,255,0.8); }
	.swatch { position: absolute; inset: 5px; border-radius: 3px; }
	.num { position: absolute; bottom: 1px; left: 3px; color: #fff; font-size: 12px; text-shadow: 1px 1px 1px #000; }
	#overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.82); color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; z-index: 10; cursor: pointer; }
	#overlay h1 { font-size: 52px; margin: 0 0 6px; letter-spacing: 2px; }
	#overlay .sub { opacity: 0.7; margin-bottom: 20px; }
	#overlay ul { text-align: left; line-height: 1.9; font-size: 16px; }
	#overlay .play { margin-top: 24px; font-size: 20px; padding: 12px 28px; border: 2px solid #fff; border-radius: 6px; }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
	<h1>MC</h1>
	<div class="sub">a tiny voxel sandbox</div>
	<ul>
		<li><b>WASD</b> — move &nbsp; <b>Space</b> — jump</li>
		<li><b>Mouse</b> — look &nbsp; <b>Scroll / 1-7</b> — select block</li>
		<li><b>Left click</b> — break &nbsp; <b>Right click</b> — place</li>
		<li><b>Esc</b> — release mouse</li>
	</ul>
	<div class="play">Click to play</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
"use strict";

/* ---------- Shared material & block data ---------- */
var BLOCK_RGB = {
	1: rgb(0x4caf50), 2: rgb(0x795548), 3: rgb(0x9e9e9e), 4: rgb(0xe7d9a8),
	5: rgb(0x8d6e63), 6: rgb(0x2e7d32), 7: rgb(0xffffff)
};
function rgb(h){ return [(h>>16&255)/255,(h>>8&255)/255,(h&255)/255]; }

// 6 faces: normal, light multiplier, 4 corner offsets (CCW winding -> outward normal)
var FACES = [
	{ n:[0,1,0],  l:1.00, c:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
	{ n:[0,-1,0], l:0.55, c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
	{ n:[1,0,0],  l:0.80, c:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]] },
	{ n:[-1,0,0], l:0.80, c:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
	{ n:[0,0,1],  l:0.80, c:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]] },
	{ n:[0,0,-1], l:0.80, c:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]] }
];

/* ---------- Scene, camera, lights ---------- */
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 400);

var ambient = new THREE.AmbientLight(0xffffff, 0.65);
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(100, 200, 150);
scene.add(ambient);
scene.add(sun);

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);
var canvas = renderer.domElement;

var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

/* ---------- Chunk storage ---------- */
var chunks = new Map();          // key "cx,cz" -> { blocks: Uint8Array, mesh }
var chunkMeshes = [];            // live chunk meshes for raycasting

function getBlock(wx, wy, wz) {
	if (wy < 0 || wy >= 80) return 0;
	var cx = Math.floor(wx/16), cz = Math.floor(wz/16);
	var lx = wx - cx*16, lz = wz - cz*16;
	var ch = chunks.get(cx+","+cz);
	if (!ch || !ch.blocks) return 0;
	return ch.blocks[lx + lz*16 + wy*256];
}
function setBlock(wx, wy, wz, id) {
	if (wy < 0 || wy >= 80) return;
	var cx = Math.floor(wx/16), cz = Math.floor(wz/16);
	var lx = wx - cx*16, lz = wz - cz*16;
	var ch = chunks.get(cx+","+cz);
	if (!ch) { ch = { blocks: new Uint8Array(20480), mesh: null }; chunks.set(cx+","+cz, ch); }
	ch.blocks[lx + lz*16 + wy*256] = id;
}

/* ---------- Deterministic value noise ---------- */
function hash2(ix, iy) {
	var h = ix*374761393 + iy*668265267;
	h = (h ^ (h>>13)) * 1274269271;
	h = (h ^ (h>>16)) >>> 0;
	return h / 4294967296;
}
function hash3(ix, iy, iz) {
	var h = ix*374761393 + iy*668265267 + iz*374761397;
	h = (h ^ (h>>13)) * 1274269271;
	h = (h ^ (h>>16)) >>> 0;
	return h / 4294967296;
}
function valueNoise2(x, y) {
	var x0 = Math.floor(x), y0 = Math.floor(y);
	var sx = x - x0, sy = y - y0;
	var n00 = hash2(x0,y0), n10 = hash2(x0+1,y0), n01 = hash2(x0,y0+1), n11 = hash2(x0+1,y0+1);
	var u = sx*sx*(3-2*sx), v = sy*sy*(3-2*sy);
	var a = n00 + u*(n10-n00), b = n01 + u*(n11-n01);
	return a + v*(b-a);
}
function valueNoise3(x, y, z) {
	var x0=Math.floor(x), y0=Math.floor(y), z0=Math.floor(z);
	var u=x-x0, v=y-y0, w=z-z0;
	var se=function(t){return t*t*(3-2*t);};
	var uu=se(u), vv=se(v), ww=se(w);
	var H=function(a,b,c){return hash3(a,b,c);};
	var c000=H(x0,y0,z0),c100=H(x0+1,y0,z0),c010=H(x0,y0+1,z0),c110=H(x0+1,y0+1,z0);
	var c001=H(x0,y0,z0+1),c101=H(x0+1,y0,z0+1),c011=H(x0,y0+1,z0+1),c111=H(x0+1,y0+1,z0+1);
	var lx00=c000+(c100-c000)*uu, lx10=c010+(c110-c010)*uu;
	var lx01=c001+(c101-c001)*uu, lx11=c011+(c111-c011)*uu;
	var ly0=lx00+(lx10-lx00)*vv, ly1=lx01+(lx11-lx01)*vv;
	return ly0+(ly1-ly0)*ww;
}
function fbm2(x, y) {
	var amp=1, freq=1, sum=0, norm=0;
	for (var o=0;o<4;o++){ sum+=amp*valueNoise2(x*freq,y*freq); norm+=amp; amp*=0.5; freq*=2; }
	return sum/norm;
}

/* ---------- Terrain generation ---------- */
function generateChunkData(cx, cz, blocks) {
	for (var lz=0; lz<16; lz++) {
		for (var lx=0; lx<16; lx++) {
			var wx = cx*16+lx, wz = cz*16+lz;
			var m = fbm2(wx*0.004, wz*0.004);
			var h = fbm2(wx*0.02, wz*0.02);
			var H = Math.floor(5 + m*m*58 + h*10);
			for (var y=0; y<80; y++) {
				var id = 0;
				if (y===0) id = 3;
				else if (y < H-3) id = 3;
				else if (y < H) id = (H<=16)?4:(H>=37?3:2);
				else if (y===H) {
					if (H>=46) id=7; else if (H>=37) id=3; else if (H<=16) id=4; else id=1;
				}
				if (y>=3 && y<H-2 && valueNoise3(wx*0.09, y*0.09, wz*0.09) > 0.67) id = 0;
				blocks[lx + lz*16 + y*256] = id;
			}
		}
	}
	// trees
	for (var lz2=0; lz2<16; lz2++) {
		for (var lx2=0; lx2<16; lx2++) {
			var wx2 = cx*16+lx2, wz2 = cz*16+lz2;
			if (hash2(wx2, wz2) < 0.02) {
				var surfY = -1;
				for (var yy=79; yy>=0; yy--) {
					if (blocks[lx2 + lz2*16 + yy*256] === 1) { surfY = yy; break; }
				}
				if (surfY>=0 && surfY+5<=79) {
					for (var k=1;k<=4;k++) blocks[lx2+lz2*16+(surfY+k)*256]=5;
					leafLayer(blocks, lx2, lz2, surfY+2, 2);
					leafLayer(blocks, lx2, lz2, surfY+3, 2);
					leafLayer(blocks, lx2, lz2, surfY+4, 1);
					leafLayer(blocks, lx2, lz2, surfY+5, 0);
				}
			}
		}
	}
}
function leafLayer(blocks, lx, lz, baseY, radius) {
	if (baseY>=80) return;
	for (var dx=-radius; dx<=radius; dx++) {
		for (var dz=-radius; dz<=radius; dz++) {
			var nx=lx+dx, nz=lz+dz;
			if (nx<0||nx>=16||nz<0||nz>=16) continue;
			var idx = nx + nz*16 + baseY*256;
			if (blocks[idx]===0) blocks[idx]=6;
		}
	}
}

/* ---------- Meshing ---------- */
function buildChunkMesh(cx, cz) {
	var ch = chunks.get(cx+","+cz);
	if (!ch || !ch.blocks) return;
	if (ch.mesh) {
		var i = chunkMeshes.indexOf(ch.mesh);
		if (i>=0) chunkMeshes.splice(i,1);
		scene.remove(ch.mesh);
		ch.mesh.geometry.dispose();
	}
	var blocks = ch.blocks;
	var wx0 = cx*16, wz0 = cz*16;
	var pos=[], nrm=[], col=[];
	for (var y=0;y<80;y++){
		for (var z=0;z<16;z++){
			for (var x=0;x<16;x++){
				var id = blocks[x + z*16 + y*256];
				if (id===0) continue;
				var wx=wx0+x, wy=y, wz=wz0+z;
				var rgb = BLOCK_RGB[id];
				for (var f=0; f<6; f++) {
					var face = FACES[f];
					var nx=wx+face.n[0], ny=wy+face.n[1], nz=wz+face.n[2];
					if (getBlock(nx,ny,nz)!==0) continue;
					var L=face.l;
					for (var v=0; v<4; v++) {
						var c=face.c[v];
						pos.push(wx+c[0], wy+c[1], wz+c[2]);
						nrm.push(face.n[0], face.n[1], face.n[2]);
						col.push(rgb[0]*L, rgb[1]*L, rgb[2]*L);
					}
				}
			}
		}
	}
	if (pos.length===0) return;
	var geo = new THREE.BufferGeometry();
	geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
	geo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(nrm), 3));
	geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(col), 3));
	var mesh = new THREE.Mesh(geo, blockMaterial);
	scene.add(mesh);
	ch.mesh = mesh;
	chunkMeshes.push(mesh);
}
function rebuildChunk(wx, wz) {
	var cx=Math.floor(wx/16), cz=Math.floor(wz/16);
	buildChunkMesh(cx, cz);
	var lx=wx-cx*16, lz=wz-cz*16;
	if (lx===0) buildChunkMesh(cx-1, cz);
	if (lx===15) buildChunkMesh(cx+1, cz);
	if (lz===0) buildChunkMesh(cx, cz-1);
	if (lz===15) buildChunkMesh(cx, cz+1);
}

/* ---------- World maintenance ---------- */
function neighborReady(cx, cz) {
	var ch = chunks.get(cx+","+cz);
	return !!(ch && ch.blocks);
}
function updateWorld() {
	var pcx = Math.floor(player.pos.x/16), pcz = Math.floor(player.pos.z/16);
	var gen=0;
	for (var dx=-5; dx<=5 && gen<4; dx++) {
		for (var dz=-5; dz<=5 && gen<4; dz++) {
			var cx=pcx+dx, cz=pcz+dz;
			var key=cx+","+cz;
			var ch=chunks.get(key);
			if (!ch || ch.blocks) continue;
			ch.blocks = new Uint8Array(20480);
			generateChunkData(cx, cz, ch.blocks);
			gen++;
		}
	}
	var mesh=0;
	for (var mx=-5; mx<=5 && mesh<2; mx++) {
		for (var mz=-5; mz<=5 && mesh<2; mz++) {
			var ccx=pcx+mx, ccz=pcz+mz;
			var k2=ccx+","+ccz;
			var ch2=chunks.get(k2);
			if (!ch2 || !ch2.blocks || ch2.mesh) continue;
			if (neighborReady(ccx+1,ccz) && neighborReady(ccx-1,ccz) && neighborReady(ccx,ccz+1) && neighborReady(ccx,ccz-1)) {
				buildChunkMesh(ccx, ccz);
				mesh++;
			}
		}
	}
	for (var e of chunks.entries()) {
		var pp=e[0].split(","), ecx=+pp[0], ecz=+pp[1];
		var dd = Math.max(Math.abs(ecx-pcx), Math.abs(ecz-pcz));
		if (dd>7) {
			if (e[1].mesh) {
				var j=chunkMeshes.indexOf(e[1].mesh);
				if (j>=0) chunkMeshes.splice(j,1);
				e[1].mesh.geometry.dispose();
				scene.remove(e[1].mesh);
			}
			chunks.delete(e[0]);
		}
	}
}

/* ---------- Player ---------- */
var player = { pos:new THREE.Vector3(), vel:new THREE.Vector3(), yaw:0, pitch:0, onGround:false };

function collides() {
	var minX=Math.floor(player.pos.x-0.3), maxX=Math.floor(player.pos.x+0.3);
	var minY=Math.floor(player.pos.y), maxY=Math.floor(player.pos.y+1.8);
	var minZ=Math.floor(player.pos.z-0.3), maxZ=Math.floor(player.pos.z+0.3);
	for (var bx=minX; bx<=maxX; bx++)
		for (var by=minY; by<=maxY; by++)
			for (var bz=minZ; bz<=maxZ; bz++)
				if (getBlock(bx,by,bz)!==0) return true;
	return false;
}
function surfaceHeight(x, z) {
	for (var y=79; y>=0; y--) if (getBlock(x,y,z)!==0) return y;
	return 40;
}
function updateControls(dt) {
	var speed=5.5, sin=Math.sin(player.yaw), cos=Math.cos(player.yaw);
	var fwd=new THREE.Vector3(-sin,0,-cos), right=new THREE.Vector3(cos,0,-sin);
	var mv=new THREE.Vector3();
	if (keys['KeyW']) mv.add(fwd);
	if (keys['KeyS']) mv.sub(fwd);
	if (keys['KeyD']) mv.add(right);
	if (keys['KeyA']) mv.sub(right);
	if (mv.lengthSq()>0) mv.normalize().multiplyScalar(speed*dt);
	player.vel.x = mv.x; player.vel.z = mv.z;
	if (keys['Space'] && player.onGround) { player.vel.y = 8.5; player.onGround=false; }
}
function updatePhysics(dt) {
	player.vel.y -= 25*dt;
	if (player.vel.y < -60) player.vel.y = -60;
	var dx=player.vel.x*dt, dy=player.vel.y*dt, dz=player.vel.z*dt;
	player.pos.x += dx;
	if (collides()) { player.pos.x -= dx; player.vel.x=0; }
	player.pos.z += dz;
	if (collides()) { player.pos.z -= dz; player.vel.z=0; }
	player.onGround = false;
	player.pos.y += dy;
	if (collides()) {
		player.pos.y -= dy;
		player.vel.y = 0;
		if (dy<0) player.onGround = true;
	}
	if (player.pos.y < -20) {
		player.pos.set(8, surfaceHeight(8,8)+2, 8);
		player.vel.set(0,0,0);
	}
}
function updateCamera() {
	camera.position.x = player.pos.x;
	camera.position.y = player.pos.y + 1.62;
	camera.position.z = player.pos.z;
	camera.rotation.order = "YXZ";
	camera.rotation.y = player.yaw;
	camera.rotation.x = player.pitch;
	camera.rotation.z = 0;
}

/* ---------- Break / place ---------- */
var raycaster = new THREE.Raycaster();
var currentTarget = null;
function getTarget() {
	if (chunkMeshes.length===0) return null;
	var cp=Math.cos(player.pitch);
	var dir=new THREE.Vector3(-Math.sin(player.yaw)*cp, Math.sin(player.pitch), -Math.cos(player.yaw)*cp);
	raycaster.set(camera.position, dir);
	var hits = raycaster.intersectObjects(chunkMeshes, false);
	if (hits.length===0 || hits[0].distance>6) return null;
	var p=hits[0].point, n=hits[0].face.normal;
	return {
		break:{ x:Math.floor(p.x-n.x*0.5), y:Math.floor(p.y-n.y*0.5), z:Math.floor(p.z-n.z*0.5) },
		place:{ x:Math.floor(p.x+n.x*0.5), y:Math.floor(p.y+n.y*0.5), z:Math.floor(p.z+n.z*0.5) }
	};
}
function blockOverlapsPlayer(bx, by, bz) {
	var px0=player.pos.x-0.3, px1=player.pos.x+0.3;
	var py0=player.pos.y, py1=player.pos.y+1.8;
	var pz0=player.pos.z-0.3, pz1=player.pos.z+0.3;
	return bx<px1 && bx+1>px0 && by<py1 && by+1>py0 && bz<pz1 && bz+1>pz0;
}
function breakBlock() {
	var t = currentTarget;
	if (!t) return;
	if (t.break.y===0) return;
	setBlock(t.break.x, t.break.y, t.break.z, 0);
	rebuildChunk(t.break.x, t.break.z);
}
function placeBlock() {
	var c = currentTarget.place;
	if (!c) return;
	if (getBlock(c.x,c.y,c.z)!==0) return;
	if (blockOverlapsPlayer(c.x,c.y,c.z)) return;
	setBlock(c.x,c.y,c.z, selected);
	rebuildChunk(c.x, c.y, c.z);
	rebuildChunk(c.x, c.y, c.z);
}

/* ---------- Outline ---------- */
var outline = new THREE.LineSegments(
	new THREE.BoxGeometry(1.002,1.002,1.002),
	new THREE.LineBasicMaterial({ color:0x000000 })
);
outline.visible = false;
scene.add(outline);

/* ---------- Clouds & water ---------- */
var clouds = [];
for (var i=0;i<25;i++) {
	var w=4+Math.random()*8, d=4+Math.random()*8;
	var cloud = new THREE.Mesh(
		new THREE.BoxGeometry(w, 1.5, d),
		new THREE.MeshLambertMaterial({ color:0xffffff, transparent:true })
	);
	cloud.position.set((Math.random()-0.5)*220, 90, (Math.random()-0.5)*220);
	scene.add(cloud);
	clouds.push(cloud);
}
var water = new THREE.Mesh(
	new THREE.PlaneGeometry(1200, 1200),
	new THREE.MeshLambertMaterial({ color:0x2196f3, transparent:true, opacity:0.55 })
);
water.rotation.x = -Math.PI/2;
scene.add(water);

function updateClouds(dt) {
	var spd = 4 + Math.random()*0.0001; // placeholder replaced below
	for (var i=0;i<clouds.length;i++) {
		var cl=clouds[i];
		cl.position.x += 1.2*dt;
		var rx = cl.position.x - player.pos.x;
		if (rx > 140) cl.position.x -= 280;
		else if (rx < -140) cl.position.x += 280;
		var rz = cl.position.z - player.pos.z;
		if (rz > 140) cl.position.z -= 280;
		else if (rz < -140) cl.position.z += 280;
	}
}

/* ---------- Hotbar UI ---------- */
var HOTBAR = [1,2,3,4,5,6,7];
var selected = 0;
var hotbarEl = document.getElementById('hotbar');
HOTBAR.forEach(function(id, i) {
	var slot = document.createElement('div');
	slot.className = 'slot' + (i===0?' active':'');
	slot.dataset.i = i;
	var sw = document.createElement('div');
	sw.className = 'swatch';
	sw.style.background = '#'+('000000'.slice(0,6).replace(/0/g,function(){return id>1?'':'1'}) /* noop */);
	// set proper color below
	var hex = (0x1000000 + HOTBAR[i]).toString(16).slice(1);
	sw.style.background = '#'+hex;
	var num = document.createElement('div');
	num.className='num'; num.textContent = (i+1);
	slot.appendChild(sw); slot.appendChild(num);
	hotbarEl.appendChild(slot);
});
function selectSlot(i) {
	selected = ((i%7)+7)%7;
	var slots = hotbarEl.children;
	for (var k=0;k<slots.length;k++) slots[k].classList.toggle('active', k===selected);
}

/* ---------- Input ---------- */
var keys = {};
window.addEventListener('keydown', function(e){
	var c = e.code;
	if (c>='Digit1' && c<='Digit7') selectSlot(parseInt(c.slice(5),10)-1);
	keys[c] = true;
});
window.addEventListener('keyup', function(e){ keys[e.code] = false; });

canvas.addEventListener('wheel', function(e){
	if (!pointerLocked) return;
	selectSlot(selected + (e.deltaY>0 ? 1 : -1));
	e.preventDefault();
}, { passive:false });

document.addEventListener('contextmenu', function(e){ e.preventDefault(); });

/* ---------- Pointer lock ---------- */
var overlay = document.getElementById('overlay');
var pointerLocked = false;
overlay.addEventListener('click', function(){ canvas.requestPointerLock(); });
document.addEventListener('pointerlockchange', function(){
	pointerLocked = (document.pointerLockElement === canvas);
	overlay.style.display = pointerLocked ? 'none' : 'flex';
});
canvas.addEventListener('mousedown', function(e){
	if (!pointerLocked) return;
	if (e.button===0) breakBlock();
	else if (e.button===2) placeBlock();
});

/* ---------- Resize ---------- */
window.addEventListener('resize', function(){
	camera.aspect = innerWidth/innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(innerWidth, innerHeight);
});

/* ---------- Init world ---------- */
function initWorld() {
	var pcx=8, pcz=8;
	for (var dx=-5;dx<=5;dx++) for (var dz=-5;dz<=5;dz++){
		var cx=pcx+dx, cz=pcz+dz, key=cx+","+cz;
		if (!chunks.has(key)) {
			var ch={blocks:new Uint8Array(20480),mesh:null};
			chunks.set(key,ch);
			generateChunkData(cx,cz,ch.blocks);
		}
	}
	var changed=true, passes=0;
	while (changed && passes<30){ changed=false; passes++;
		for (var mx=-5;mx<=5;mx++) for (var mz=-5;mz<=5;mz++){
			var ccx=pcx+mx, ccz=pcz+mz, k2=ccx+","+ccz;
			var ch2=chunks.get(k2);
			if (!ch2||!ch2.blocks||ch2.mesh) continue;
			if (neighborReady(ccx+1,ccz)&&neighborReady(ccx-1,ccz)&&neighborReady(ccx,ccz+1)&&neighborReady(ccx,ccz-1)){
				buildChunkMesh(ccx,ccz); changed=true;
			}
		}
	}
	player.pos.set(8, surfaceHeight(8,8)+2, 8);
}
initWorld();

/* ---------- Main loop ---------- */
var last = performance.now();
function animate() {
	requestAnimationFrame(animate);
	var now = performance.now();
	var dt = (now-last)/1000; last = now;
	if (dt>0.05) dt=0.05;
	if (pointerLocked){ updateControls(dt); updatePhysics(dt); }
	updateWorld();
	updateCamera();
	var tgt = getTarget();
	if (tgt){ currentTarget=tgt; outline.position.set(tgt.break.x+0.5, tgt.break.y+0.5, tgt.break.z+0.5); outline.visible=true; }
	else outline.visible=false;
	updateClouds(dt);
	water.position.x = player.pos.x; water.position.z = player.pos.z;
	renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>
```