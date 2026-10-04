Let me carefully build this Minecraft-style voxel game in a single HTML file. I'll follow the spec precisely.

Let me break down the requirements:

1. **Loading**: Three.js r128 from CDN, global THREE object. No modules.

2. **Blocks**: IDs 0-7 with specific colors. Unit cubes, vertex colors, ONE shared MeshLambertMaterial. Fake lighting: top faces 1.0, sides 0.8, bottoms 0.55.

3. **Chunks & endless world**: 16x16 columns, 80 blocks high. Global Map keyed "cx,cz". Uint8Array of block IDs + mesh. Global read/write block helpers using chunk = floor(world/16), local = world - chunk*16. Negative coords work. Missing chunk or y outside 0-79 returns air. Each frame: generate block data for chunks within 5 (max 4/frame); build meshes for chunks within 4 whose 4 neighbors have data (max 2/frame); chunks farther than 7 remove mesh, dispose geometry, delete entry.

4. **Meshing**: ONE BufferGeometry per chunk. Loop all non-air blocks, for each of 6 sides check neighbor with global read helper; if air, add face (2 triangles) to flat position/normal/color arrays. World coordinates for vertices, mesh at origin. All chunk meshes in global array for raycasting. Rebuild function for chunk.

5. **Terrain (deterministic)**: 
   - Value noise: integer-coordinate hash 0-1 (mix with large prime multipliers and xor-shifts), smoothed 2D noise via bilinear interpolation with smoothstep, 4 octaves combined into fractal noise, plus 3D version for caves.
   - Column height: m = fractal at coords*0.004, h = fractal at coords*0.02, H = floor(5 + m*m*58 + h*10).
   - Column fill: y 0 = unbreakable stone; below H-3 stone; the 3 layers under surface (sand if H≤16, stone if H≥37); surface = snow if H≥46, stone if H≥37, sand if H≤16, otherwise grass.
   - Caves: for y between 3 and H-2, if 3D noise at position*0.09 exceeds 0.67, set air.
   - Trees: on grass, when per-column hash < 0.02 and trunk fits: 4 wood up, leaves as 5x5 layer twice, then 3x3, then 1 on top (only into air).

6. **Player & controls**: PerspectiveCamera (fov 75, far 400), rotation order "YXZ" driven by yaw/pitch. Clicking start overlay requests pointer lock; mouse look only while locked (sensitivity ~0.002, clamp pitch). Player box: half-width 0.3, height 1.8, eye 1.62; spawn above terrain at x=8, z=8. Gravity 25/s, jump Space (velocity 8.5), WASD at 5.5 m/s relative to yaw. Axis-separated collision against all non-air blocks (move per axis, revert on overlap; landing sets on-ground). Falling below y -20 teleports back to spawn.

7. **Break & place**: CSS crosshair at center. Each frame raycast from camera center (max distance 6) against chunk meshes. From hit point p and face normal n: break target = floor(p - n*0.5), place cell = floor(p + n*0.5), per component. Outline targeted block with black wireframe box. Only while pointer locked: left click sets target to air (not at y 0); right click places selected block if cell is air and doesn't overlap player. After edit rebuild the chunk, also neighbor chunk if block on chunk border. Suppress context menu.

8. **Hotbar**: Fixed bottom center: 7 slots (grass, dirt, sand, wood, leaves, snow)... wait let me recount. The spec says "7 slots (grass, dirt, stone, sand, wood, leaves, snow)". So: grass, dirt, stone, sand, wood, leaves, snow. Each a small square in block color with its number, on dark semi-transparent bar. Selected slot gets white border. Select with keys 1-7 or mouse wheel (wraps).

9. **Sky, clouds, water**: Sky-blue background 0x87ceeb with matching fog (~40 to 110). Ambient 0.65 + directional 0.8. ~25 flat white transparent boxes as clouds at height ~90, slowly drifting and wrapping around player. Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame — visual only.

10. **UI**: Fullscreen start overlay with title, controls list, "Click to play"; reappears whenever pointer lock released. Body without margins, fullscreen canvas, window resize handled.

Let me now write this carefully.

### Block colors and lighting

Block IDs:
- 0 air
- 1 grass 0x4caf50
- 2 dirt 0x795548
- 3 stone 0x9e9e9e
- 4 sand 0xe7d9a8
- 5 wood 0x8d6e63
- 6 leaves 0x2e7d32
- 7 snow 0xffffff

For vertex colors, each face gets color * lighting factor.

### Meshing details

For each block at (x,y,z) in chunk, if non-air, for each of 6 directions, check neighbor. If neighbor is air, add face.

The 6 directions and their vertices. Let me define a standard cube face layout.

Actually, let me think about how to build the geometry efficiently. For each block, I iterate 6 faces. For each face that needs rendering (neighbor is air), I add 2 triangles (6 vertices).

Let me define face data. Each face has:
- direction (normal)
- 4 corner offsets

Standard approach: define the 6 faces with their vertex positions relative to block center or corner.

Let me use the approach where each face is defined by 4 corners. I'll compute them based on the face normal.

Faces:
- +X (right): normal (1,0,0)
- -X (left): normal (-1,0,0)
- +Y (top): normal (0,1,0)
- -Y (bottom): normal (0,-1,0)
- +Z (front): normal (0,0,1)
- -Z (back): normal (0,0,-1)

For lighting:
- Top (+Y): 1.0
- Sides (+X, -X, +Z, -Z): 0.8
- Bottom (-Y): 0.55

Now for the face vertices, I need to be careful about winding order for correct culling (front faces should be visible). MeshLambertMaterial uses double-sided by default? Actually MeshLambertMaterial is not double-sided by default; it's single-sided and culls back faces. Wait, actually MeshLambertMaterial renders both sides by default? Let me recall. In Three.js, MeshBasicMaterial and MeshLambertMaterial have `side` property defaulting to `THREE.FrontSide`. Hmm, actually the default side is FrontSide which means only front faces render. But without back faces rendered... 

Wait, let me reconsider. Actually the default for most materials is `THREE.FrontSide`. But we want all visible faces. Since we only add faces where neighbor is air, and we orient them correctly, FrontSide should work. But we need correct winding.

Actually, let me just set side to DoubleSide to be safe? No wait, the spec says keep it simple. Let me think.

Actually, let me reconsider. If I set the material to FrontSide (default), I need the winding order to be counter-clockwise when viewed from outside. Let me make sure my face vertices are wound correctly.

Hmm, but actually there might be an issue. Let me just use the standard Minecraft-style face generation.

Let me define each face with its 4 corners in CCW order when viewed from outside.

For +X face (normal pointing +X, viewed from +X looking toward -X):
Corners (using block origin at min corner, so block spans [0,1] in local):
Actually let me use the block's world position and add offsets.

Let me define a helper that given a face type returns {offsets, normals}.

Standard face definitions (from various voxel implementations):

```
const faces = [
  { dir: [1,0,0],  corners: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },  // +X
  { dir: [-1,0,0], corners: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },  // -X
  { dir: [0,1,0],  corners: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },  // +Y top
  { dir: [0,-1,0], corners: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },  // -Y bottom
  { dir: [0,0,1],  corners: [[1,0,1],[0,0,1],[0,1,1],[1,1,1]] },  // +Z
  { dir: [0,0,-1], corners: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]] },  // -Z
];
```

I need to verify winding order produces CCW from outside. Let me just trust these standard definitions and set side to FrontSide. Actually, to be safe and avoid culling issues, I could set `side: THREE.DoubleSide`. But DoubleSide is slower and can have z-fighting. Since we only draw exterior faces, FrontSide is fine and more efficient.

Hmm, but if I get winding wrong, faces won't render. Let me think about whether to test. Actually, let me use FrontSide but I'll carefully verify one face.

For +Y top face, viewed from above (+Y looking down -Y direction). When looking down the -Y axis, we see the top. The camera looks along... For a face to be front-facing, its normal points toward viewer (+Y). We view from +Y looking toward -Y. In a right-handed coordinate system looking down -Y... 

This is getting complicated. Let me just define the faces and verify winding with the right-hand rule / standard convention.

Actually, a cleaner way: I'll define faces such that the 4 corners go counter-clockwise as seen from the outside. Let me use a well-known set.

From the Three.js examples / common voxel code:

```javascript
function buildFace(dir, corners) {
  // dir is normal, corners are 4 points
}
```

Let me use this known-correct set (from a popular implementation):

```
const FACES = [
  // name, normal, 4 corners (CCW from outside)
  ['top',    [ 0, 1, 0], [[0,1,1],[1,1,1],[1,1,0],[0,1,0]]],
  ['bottom', [ 0,-1, 0], [[0,0,0],[1,0,0],[1,0,1],[0,0,1]]],
  ['north',  [ 0, 0, 1], [[1,0,1],[0,0,1],[0,1,1],[1,1,1]]],
  ['south',  [ 0, 0,-1], [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]],
  ['east',   [ 1, 0, 0], [[1,0,1],[1,0,0],[1,1,0],[1,1,1]]],
  ['west',   [-1, 0, 0], [[0,0,1],[0,0,0],[0,1,0],[0,1,1]]],
];
```

Let me verify the top face winding. Corners: [0,1,1],[1,1,1],[1,1,0],[0,1,0]. These are in XY... no wait they're (x,z) varying, y=1 fixed. Looking from above (+Y looking down -Y):

When we look down -Y in a right-handed system, X points right, Z points... Let me set up. Standard three.js is right-handed, Y up. Looking down the -Y axis (from +Y toward origin), with X to the right. Then Z would point down-left? In right-handed coords, if X is right and Y is up, Z is toward viewer (out of screen) normally. When we look down -Y, we rotate. Hmm.

Let me think differently. The winding order matters for the dot product of the normal with the cross product of edge vectors. If we go corner0->corner1->corner2, and the resulting normal (via right-hand rule) matches the face normal, it's front-facing.

Cross product approach: For triangle (c0, c1, c2), normal = normalize(cross(c1-c0, c2-c0)).

Top face: c0=[0,1,1], c1=[1,1,1], c2=[1,1,0].
c1-c0 = [1,0,0]
c2-c0 = [1,0,-1]
cross([1,0,0],[1,0,-1]) = [0*(-1)-0*0, 0*1-1*(-1), 1*0-0*1] = [0, 1, 0]. ✓ Matches normal [0,1,0]. 

So top face is correctly wound (front-facing with FrontSide).

Let me verify bottom face: c0=[0,0,0], c1=[1,0,0], c2=[1,0,1].
c1-c0=[1,0,0], c2-c0=[1,0,1]
cross([1,0,0],[1,0,1]) = [0*1-0*0, 0*1-1*1, 1*0-0*1] = [0,-1,0]. ✓ Matches [0,-1,0].

North face (+Z): c0=[1,0,1], c1=[0,0,1], c2=[0,1,1].
c1-c0=[-1,0,0], c2-c0=[-1,0,0]... wait c2-c0 = [0-1,1-1,1-1] = [-1,0,0]. Both same?! That gives zero cross product. Let me recompute.

c0=[1,0,1], c1=[0,0,1], c2=[0,1,1].
c1-c0 = [0-1, 0-0, 1-1] = [-1,0,0].
c2-c0 = [0-1, 1-0, 1-1] = [-1,1,0].
cross([-1,0,0],[-1,1,0]) = [0*0-0*1, 0*(-1)-(-1)*0, (-1)*1-0*(-1)] = [0, 0, -1].

Normal should be [0,0,1] but we got [0,0,-1]. That's backwards! So north face as I defined is incorrectly wound. Let me fix by reversing the corner order.

Hmm, let me reconsider. Let me recompute more carefully.

cross(a,b) where a=[a0,a1,a2], b=[b0,b1,b2]:
result = [a1*b2 - a2*b1, a2*b0 - a0*b2, a0*b1 - a1*b0]

a = c1-c0 = [-1,0,0]
b = c2-c0 = [-1,1,0]
result[0] = a1*b2 - a2*b1 = 0*0 - 0*1 = 0
result[1] = a2*b0 - a0*b2 = 0*(-1) - (-1)*0 = 0
result[2] = a0*b1 - a1*b0 = (-1)*1 - 0*(-1) = -1
So cross = [0,0,-1]. Normal is [0,0,1], so this is back-facing. Need to reverse.

Let me reverse north corners to [1,0,1],[0,1,1],[0,0,1],[1,1,1].
c0=[1,0,1], c1=[0,1,1], c2=[0,0,1].
c1-c0 = [-1,1,0], c2-c0 = [-1,0,0].
cross: 
result[0] = 1*0 - 0*0 = 0
result[1] = 0*(-1) - (-1)*0 = 0
result[2] = (-1)*0 - 1*(-1) = 1
cross = [0,0,1]. ✓ Correct now.

OK so my initial set had some wrong windings. Let me redo all of them carefully and derive correct winding.

Actually, this is error-prone. Let me take a different, more systematic approach. I'll define each face by its normal and two tangent vectors, then compute the 4 corners consistently.

For a face with normal N, I need two in-plane vectors U and V perpendicular to each other and to N. The 4 corners are:
base + 0*U + 0*V
base + 1*U + 0*V
base + 1*U + 1*V
base + 0*U + 1*V

where base is the corner where U and V are zero. The winding base->u0->u1 should give normal via right-hand rule = N.

Let me handle each:

**+Y top**: N = [0,1,0]. Choose U = [1,0,0], V = [0,0,1]? Check cross(U,V) = cross([1,0,0],[0,0,1]) = [0*1-0*0, 0*0-1*1, 1*0-0*0] = [0,-1,0]. That's -N. So swap: V = [0,0,-1]? cross([1,0,0],[0,0,-1]) = [0*(-1)-0*0, 0*0-1*(-1), 1*0-0*0] = [0,1,0] = N. ✓
So U=[1,0,0], V=[0,0,-1], base = (0,1,0) [the zero-U-zero-V corner is at min where x=0,y=1,z=0].
Corners:
c0 = base = (0,1,0)
c1 = base + U = (1,1,0)
c2 = base + U + V = (1,1,-1)
c3 = base + V = (0,1,-1)
Triangle (c0,c1,c2): c1-c0=[1,0,0], c2-c0=[1,0,-1], cross = [0*−1−0·0, 0·1−1·(−1), 1·0−0·1] = [0,1,0] ✓.

Hmm wait, this introduces negative coordinates. That's fine for the geometry since we add world position later. But let me reconsider—maybe simpler to just carefully assign.

Actually, let me just define all 6 with explicit correct winding by computing U, V, base for each.

General method: Given N, pick U = normalize(any vector not parallel to N). V = cross(N, U)? or cross(U,N)? Let me figure out. We want cross(c1-c0, c2-c0) = N. With c1-c0 = U and c2-c0 = U+V... hmm that's not simply U and V.

Let me reconsider. If c0 = base, c1 = base + U, c2 = base + U + V, c3 = base + V:
Triangle 1: c0, c1, c2. Edge vectors: e1 = c1-c0 = U, e2 = c2-c0 = U+V.
cross(e1, e2) = cross(U, U+V) = cross(U,U) + cross(U,V) = 0 + cross(U,V) = cross(U,V).
So we need cross(U,V) = N. Good, so just need cross(U,V)=N.

Also triangle 2: c1, c2, c3. e1 = c2-c1 = V, e2 = c3-c1 = V - U.
cross(V, V-U) = cross(V,V) - cross(V,U) = 0 - cross(V,U) = cross(U,V) = N. ✓ Same.

Great, so I just need two vectors U, V with cross(U,V) = N.

For each face:
- **+Y** N=[0,1,0]: U=[1,0,0], V=[0,0,1]? cross([1,0,0],[0,0,1]) = [0*1-0*0, 0*0-1*1, 1*0-0*0] = [0,-1,0] = -N. So V=[0,0,-1]. cross([1,0,0],[0,0,-1])=[0,1,0]=N ✓. base = the corner where both U and V are 0: that's (x_min, 1, z_min). Let me use base = (0,1,0) meaning x=0,y=1,z=0. Then:
  - c0 = (0,1,0)
  - c1 = (1,1,0)
  - c2 = (1,1,-1)
  - c3 = (0,1,-1)
  
  Hmm negative z. Let me instead choose base = (0,1,1) and adjust. Actually the base is where U and V are zero. U goes in +x, V goes in -z. So starting from base, x increases and z decreases. To keep coordinates in [0,1], let base = (0,1,1): then c0=(0,1,1), c1=(1,1,1), c2=(1,1,0), c3=(0,1,0). That's clean! Let me verify cross(U,V): U=[1,0,0], V = c3-c0 = (0,1,0)-(0,1,1) = [0,0,-1]. cross([1,0,0],[0,0,-1]) = [0*−1−0·0, 0·0−1·(−1), 1·0−0·0] = [0,1,0] = N ✓.
  
  So top: c0=(0,1,1), c1=(1,1,1), c2=(1,1,0), c3=(0,1,0).

- **-Y** N=[0,-1,0]: need U,V with cross(U,V)=[0,-1,0]. Try U=[1,0,0], V=[0,0,-1]: cross([1,0,0],[0,0,-1])=[0,1,0]. That's +N, wrong. Try V=[0,0,1]: cross([1,0,0],[0,0,1])=[0,-1,0] ✓. base where U,V zero: x_min, y=0, and V in +z so z_max. base=(0,0,1): c0=(0,0,1), c1=(1,0,1), c2=(1,0,0), c3=(0,0,0). Verify: U=c1-c0=[1,0,0], V=c3-c0=[0,0,-1]. cross([1,0,0],[0,0,-1])=[0,1,0]. Hmm that's +N but we want -N! 

  Wait, I think I mismatched. Let me recompute. base=(0,0,1). c3 = base + V. V should be [0,0,1] direction. c3 = (0,0,1)+[0,0,1] = (0,0,2)? That's wrong. Let me redo.

  I'm confusing myself. Let me restart this systematically.

  For -Y face, N = [0,-1,0]. I want cross(U,V) = N = [0,-1,0].
  Let me pick U = [1,0,0]. Then I need V such that cross([1,0,0], V) = [0,-1,0].
  cross([1,0,0],[vx,vy,vz]) = [0*vz-0*vy, 0*vx-1*vz, 1*vy-0*vx] = [0, -vz, vy].
  Set equal to [0,-1,0]: -vz = -1 => vz=1; vy=0. So V=[0,0,1].
  Check: cross([1,0,0],[0,0,1]) = [0*1-0*0, 0*0-1*1, 1*0-0*0] = [0,-1,0] ✓.
  Now base: c0 = base + 0*U + 0*V = base. c1 = base + U. c2 = base + U + V. c3 = base + V.
  To keep in [0,1]: base should have x=0 (since U adds +x), and z such that adding V (which is +z) keeps ≤1. So base z=0: c0=(0,0,0), c1=(1,0,0), c2=(1,0,1), c3=(0,0,1).
  Verify winding with triangle c0,c1,c2: e1=c1-c0=[1,0,0], e2=c2-c0=[1,0,1]. cross = [0*1-0*1, 0*1-1*1, 1*0-0*1] = [0,-1,0] = N ✓.
  
  So bottom: c0=(0,0,0), c1=(1,0,0), c2=(1,0,1), c3=(0,0,1).

- **+X** N=[1,0,0]: need cross(U,V)=[1,0,0]. Pick U=[0,0,1] (along z). Then cross([0,0,1],V)=[1,0,0]. cross([0,0,1],[vx,vy,vz]) = [0*vz-1*vy, 1*vx-0*vz, 0*vy-0*vx] = [-vy, vx, 0]. Set = [1,0,0]: -vy=1=>vy=-1, vx=0. V=[0,-1,0].
  Check cross([0,0,1],[0,-1,0]) = [0*0-1*(-1), 1*0-0*0, 0*(-1)-0*0] = [1,0,0] ✓.
  base: U adds +z, V adds -y. base z=0 (so c0.z=0, and U increases z), base y=1 (so V decreases y stays ≥0). base=(1,1,0).
  c0=(1,1,0), c1=(1,1,1), c2=(1,0,1), c3=(1,0,0).
  Verify triangle c0,c1,c2: e1=c1-c0=[0,0,1], e2=c2-c0=[0,-1,1]. cross([0,0,1],[0,-1,1]) = [0*1-1*(-1), 1*0-0*1, 0*(-1)-0*0] = [1,0,0] ✓.
  
  So +X: c0=(1,1,0), c1=(1,1,1), c2=(1,0,1), c3=(1,0,0).

- **-X** N=[-1,0,0]: need cross(U,V)=[-1,0,0]. Pick U=[0,0,1]. cross([0,0,1],V)=[-1,0,0]. From above cross([0,0,1],V)=[-vy,vx,0]. Set=[-1,0,0]: -vy=-1=>vy=1, vx=0. V=[0,1,0].
  Check cross([0,0,1],[0,1,0]) = [0*0-1*1, 1*0-0*0, 0*1-0*0] = [-1,0,0] ✓.
  base: U adds +z, V adds +y. base z=0, y=0. base=(0,0,0).
  c0=(0,0,0), c1=(0,0,1), c2=(0,1,1), c3=(0,1,0).
  Verify triangle c0,c1,c2: e1=[0,0,1], e2=[0,1,1]. cross([0,0,1],[0,1,1]) = [0*1-1*1, 1*0-0*1, 0*1-0*0] = [-1,0,0] ✓.
  
  So -X: c0=(0,0,0), c1=(0,0,1), c2=(0,1,1), c3=(0,1,0).

- **+Z** N=[0,0,1]: need cross(U,V)=[0,0,1]. Pick U=[1,0,0]. cross([1,0,0],V)=[0,0,1]. cross([1,0,0],[vx,vy,vz]) = [0*vz-0*vy, 0*vx-1*vz, 1*vy-0*vx] = [0,-vz,vy]. Set=[0,0,1]: -vz=0=>vz=0, vy=1. V=[0,1,0].
  Check cross([1,0,0],[0,1,0]) = [0*0-0*1, 0*0-1*0, 1*1-0*0] = [0,0,1] ✓.
  base: U adds +x, V adds +y. base x=0,y=0. base=(0,0,0).
  c0=(0,0,0), c1=(1,0,0), c2=(1,1,0), c3=(0,1,0).
  Verify triangle c0,c1,c2: e1=[1,0,0], e2=[1,1,0]. cross([1,0,0],[1,1,0]) = [0*0-0*1, 0*1-1*0, 1*1-0*1] = [0,0,1] ✓.
  
  So +Z: c0=(0,0,0), c1=(1,0,0), c2=(1,1,0), c3=(0,1,0).

- **-Z** N=[0,0,-1]: need cross(U,V)=[0,0,-1]. Pick U=[1,0,0]. cross([1,0,0],V)=[0,0,-1]. From formula [0,-vz,vy]=[0,0,-1]: -vz=0=>vz=0, vy=-1. V=[0,-1,0].
  Check cross([1,0,0],[0,-1,0]) = [0*0-0*(-1), 0*0-1*0, 1*(-1)-0*0] = [0,0,-1] ✓.
  base: U adds +x, V adds -y. base x=0, y=1. base=(0,1,0).
  c0=(0,1,0), c1=(1,1,0), c2=(1,0,0), c3=(0,0,0).
  Verify triangle c0,c1,c2: e1=[1,0,0], e2=[1,-1,0]. cross([1,0,0],[1,-1,0]) = [0*0-0*(-1), 0*1-1*0, 1*(-1)-0*1] = [0,0,-1] ✓.
  
  So -Z: c0=(0,1,0), c1=(1,1,0), c2=(1,0,0), c3=(0,0,0).

Great, now I have all 6 faces with correct winding (front-facing with FrontSide). Let me compile:

```
const FACES = [
  // index, normal, lighting, corners (local, 0..1)
  [0, [0, 1, 0], 1.0,  [[0,1,1],[1,1,1],[1,1,0],[0,1,0]]],  // top
  [1, [1, 0, 0], 0.8,  [[1,1,0],[1,1,1],[1,0,1],[1,0,0]]],  // +X
  [2, [-1, 0, 0],0.8,  [[0,0,0],[0,0,1],[0,1,1],[0,1,0]]],  // -X
  [3, [0, 0, 1], 0.8,  [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]],  // +Z
  [4, [0, 0,-1], 0.8,  [[0,1,0],[1,1,0],[1,0,0],[0,0,0]]],  // -Z
  [5, [0,-1, 0], 0.55, [[0,0,0],[1,0,0],[1,0,1],[0,0,1]]],  // bottom
];
```

Wait, I need to double check the -X face. Earlier I derived -X: c0=(0,0,0), c1=(0,0,1), c2=(0,1,1), c3=(0,1,0). As an array of 4 corners: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]]. Yes matches index 2 above. Good.

And +Z: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]] matches index 3. Good.
-Z: [[0,1,0],[1,1,0],[1,0,0],[0,0,0]] matches index 4. Good.
Bottom: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] matches index 5. Good.
+X: [[1,1,0],[1,1,1],[1,0,1],[1,0,0]] matches index 1. Good.
Top: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] matches index 0. Good.

Now for meshing, for each non-air block at (x,y,z), for each face, check neighbor. Neighbor world coord = (x+nx, y+ny, z+nz). Read it via global read helper. If air, add the face.

For each face, add 4 vertices (position, normal, color). Position = world block pos + corner offset. Normal = face normal. Color = blockColor * lighting.

Then add 2 triangles: (v0,v1,v2) and (v0,v2,v3).

Now the global read helper. Chunk stores Uint8Array of block IDs. I need a way to read block at world (x,y,z). chunk = floor(x/16) etc. But careful: floor for negatives. JavaScript Math.floor works correctly for negatives (Math.floor(-0.5) = -1). Good.

local = x - chunk*16. For x=-1: chunk = floor(-1/16) = floor(-0.0625) = -1. local = -1 - (-1)*16 = -1 + 16 = 15. Good, in [0,15].

Chunk key = cx+","+cz. Data stored as Uint8Array of size 16*80*16 = 20480. Index = (cx*16 + lx) + cz*16*80 + ly... let me define: index = (ly * 16 * 16) + (lz * 16) + lx? Or better: for a column-based storage, index = (lx + lz*16) + ly*(16*16). Let me use: idx = (ly * 256) + (lz * 16) + lx. Total = 80*256 = 20480. Good.

Actually let me reconsider the indexing to match "Uint8Array of block IDs". I'll store as [y][z][x] with y outermost: idx = (y * 16 + z) * 16 + x = y*256 + z*16 + x. That works.

Global read:
```
function getBlock(wx, wy, wz) {
  if (wy < 0 || wy >= 80) return 0;
  const cx = Math.floor(wx / 16);
  const cz = Math.floor(wz / 16);
  const key = cx + "," + cz;
  const chunk = chunkData.get(key);
  if (!chunk) return 0;
  const lx = wx - cx*16;
  const lz = wz - cz*16;
  if (lx < 0 || lx >= 16 || lz < 0 || lz >= 16) return 0; // shouldn't happen
  return chunk.data[(wy * 16 + lz) * 16 + lx];
}
```

Global write:
```
function setBlock(wx, wy, wz, id) {
  if (wy < 0 || wy >= 80) return;
  const cx = Math.floor(wx / 16);
  const cz = Math.floor(wz / 16);
  const key = cx + "," + cz;
  let chunk = chunkData.get(key);
  if (!chunk) { chunk = { data: new Uint8Array(20480), mesh: null }; chunkData.set(key, chunk); }
  const lx = wx - cx*16;
  const lz = wz - cz*16;
  chunk.data[(wy * 16 + lz) * 16 + lx] = id;
}
```

Now generation. For a chunk at (cx, cz), generate all block data. The spec says "generate block data for all chunks within 5 chunks of the player (max 4 per frame)". So generation is limited to 4 chunks/frame. And meshing limited to 2 chunks/frame.

Let me structure the update loop:
- Compute player chunk (pcx, pcz).
- Determine candidate chunks within radius 5: from pcx-5 to pcx+5, cz-5 to pcz+5. That's 11x11 = 121 chunks. Generate up to 4 per frame.
- For meshing: chunks within 4 whose 4 neighbors already have data. Up to 2 per frame.
- Chunks farther than 7: remove mesh, dispose geometry, delete entry.

Let me implement generation:
```
function generateChunk(cx, cz) {
  const data = new Uint8Array(20480);
  // for each column (x,z) in chunk
  for (let lz=0; lz<16; lz++) {
    for (let lx=0; lx<16; lx++) {
      const wx = cx*16 + lx;
      const wz = cz*16 + lz;
      // compute height
      const H = columnHeight(wx, wz);
      // fill
      for (let y=0; y<H; y++) {
        let id = 3; // stone
        if (y === 0) id = 3; // unbreakable stone (still stone, id 3)
        // caves
        if (y >= 3 && y <= H-2) {
          if (noise3D(wx*0.09, y*0.09, wz*0.09) > 0.67) continue; // air
        }
        // below H-3 stone
        if (y < H-3) { id = 3; }
        else {
          // 3 layers under surface
          // determine surface type
          ...
        }
      }
    }
  }
}
```

Hmm, let me re-read the fill rules carefully:

"Column fill: y 0 = unbreakable stone; below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = snow if H ≥ 46, stone if H ≥ 37, sand if H ≤ 16, otherwise grass."

So:
- y=0: stone (id 3), unbreakable.
- below H-3: stone.
- the 3 layers under the surface: dirt (sand if H≤16, stone if H≥37). So these are the 3 blocks just below the surface block. Material depends on H.
- surface (y=H-1): snow if H≥46, stone if H≥37, sand if H≤16, otherwise grass.

Wait, "the 3 layers under the surface dirt". So there are 3 layers beneath the surface, and they're made of dirt, but the material is swapped: sand if H≤16, stone if H≥37. Actually re-reading: "the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37)". So the 3 sub-surface layers are dirt normally, but sand if H≤16 or stone if H≥37.

And the surface itself: snow if H≥46, stone if H≥37, sand if H≤16, otherwise grass.

So the logic per column:
- For y from 0 to H-1:
  - if y == 0: stone (unbreakable)
  - else if y < H-3: stone
  - else if y >= H-3 and y <= H-2 (i.e., the 3 layers under surface, which are y = H-4, H-3, H-2): dirt/sand/stone depending on H
    - Actually "3 layers under the surface": surface is at H-1. So layers under surface are H-2, H-3, H-4. Three layers.
  - else if y == H-1 (surface): snow/stone/sand/grass depending on H.

Wait, but what about the range between H-3 and H-2? Let me think. "below H−3 stone" means y < H-3 is stone. Then "the 3 layers under the surface" — these are the 3 blocks directly under the surface. Surface is the top block at y=H-1. So 3 layers under = y = H-2, H-3, H-4. Hmm, but "below H-3" covers y=0..H-4. So there's overlap.

Let me reconsider. Let me define:
- y < H-3: stone (this covers y=0 up to y=H-4)
- y = H-3, H-2, H-1? No...

Hmm, "the 3 layers under the surface". If surface is at y=H-1, the 3 layers under are H-2, H-3, H-4. Combined with "below H-3 stone" (y<H-4, i.e., y ≤ H-5)... 

Wait, "below H-3" means y < H-3, i.e., y ≤ H-4. So y=H-4 is included in "below H-3"? H-4 < H-3 yes. So y=H-4 is stone by the "below H-3" rule. But then the "3 layers under surface" would be H-2, H-3, H-4, but H-4 is already stone. Contradiction.

Let me re-read very carefully: "below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = ..."

Maybe the intended interpretation:
- y < H-3: stone (blocks 0..H-4)
- y = H-3, H-2, H-1... no.

Actually maybe "the 3 layers under the surface" refers to y = H-4, H-3, H-2 (3 layers), and surface = H-1. And "below H-3 stone" is just describing the general case but the 3-layer rule overrides for H-4..H-2.

Hmm, but that conflicts. Let me think about it as: the top block (surface) at H-1, and 3 blocks below it (H-2, H-3, H-4) are the "sub-surface" layer, rest (y ≤ H-5) is stone.

Actually wait. Let me reconsider "below H-3". Maybe it means y <= H-3 inclusive? In casual reading "below H-3" = y < H-3. But maybe the author means the region. Let me just implement it as a clean layered model:

For a column with height H (surface at y=H-1):
- y = 0: stone (id 3)
- y from 1 to H-5: stone (id 3)  [deep]
- y = H-4, H-3, H-2: sub-surface (dirt, or sand/stone by H)
- y = H-1: surface (snow/stone/sand/grass by H)

But this requires H large enough. What if H is small (like 5-10)? Then H-4 could be negative. Let me handle gracefully: iterate y from 0 to H-1, and decide each.

Let me define a function surfaceMaterial(H) and subSurfaceMaterial(H):
- subSurfaceMaterial(H) = (H <= 16) ? 4 (sand) : (H >= 37 ? 3 (stone) : 2 (dirt))
- surfaceMaterial(H) = (H >= 46) ? 7 (snow) : (H >= 37 ? 3 (stone) : (H <= 16 ? 4 (sand) : 1 (grass)))

Wait but for H>=37, surface is stone and sub-surface is stone. For H<=16, surface is sand and sub-surface is sand. For 16<H<37, surface is grass and sub-surface is dirt. Makes sense.

Now the loop:
```
for (y = 0; y < H; y++) {
  // cave check first
  if (y >= 3 && y <= H-2) {
    if (noise3D(...) > 0.67) continue; // becomes air
  }
  let id;
  if (y === 0) id = 3;
  else if (y === H-1) id = surfaceMaterial(H);
  else if (y >= H-4) id = subSurfaceMaterial(H); // y = H-4, H-3, H-2
  else id = 3; // stone
  data[idx] = id;
}
```

Wait, but "below H-3 stone" — with my loop, y from 1 to H-5 would be stone (else branch), and H-4,H-3,H-2 sub-surface. But the spec says "below H-3 stone; the 3 layers under the surface". If I interpret literally: below H-3 (y<H-3, i.e. y≤H-4) is stone, then 3 layers under surface... but that's contradictory because H-4 is both below H-3 (stone) and part of 3 layers under surface.

I think the cleanest consistent interpretation that matches typical Minecraft-ish terrain:
- Deep (y < H-3): stone. This is y=0..H-4.

Hold on. Let me reconsider. Actually maybe the "3 layers under the surface" ARE the blocks from H-3 to H-1 minus surface? No...

Ugh. Let me just go with a reasonable interpretation and move on. I'll interpret:
- y=0: stone (unbreakable)
- y in [1, H-4]: stone  ("below H-3")
- y in [H-3, H-2]: sub-surface (the 3 layers... wait that's only 2)

Hmm, "3 layers under the surface". Surface at H-1. Under it: H-2, H-3, H-4 = 3 layers. So:
- y in [H-4, H-2]: sub-surface material
- y = H-1: surface

And "below H-3 stone" — I'll interpret as the deep stone, which combined means y in [1, H-5] is stone. But there's ambiguity at H-4.

You know what, let me just go with:
- y=0: stone
- y in [1, H-5]: stone (deep, "below H-3")
- y in [H-4, H-2]: sub-surface (3 layers: H-4, H-3, H-2)
- y=H-1: surface

This gives exactly 3 sub-surface layers and treats the rest as stone. For small H where H-4 < 1, the ranges just collapse sensibly. E.g., H=5: y=0 stone, y=1..0 none, y=1..3 sub-surface? Wait H-4=1, H-2=3, so y=1,2,3 sub-surface, y=4 surface. And y=0 stone. That fills 0-4 = 5 blocks. Good.

Actually for H=5, "below H-3" = y<2 = y=0,1. And 3 layers under surface = y=1,2,3. Overlap at y=1. My interpretation makes y=1 sub-surface. Fine.

Let me just go with my clean interpretation. It produces nice terrain.

Actually, wait. Let me reconsider once more. Let me re-read: "below H−3 stone; the 3 layers under the surface dirt (sand if H ≤ 16, stone if H ≥ 37); surface = ...". 

I think the semicolons separate three statements:
1. "below H−3 stone" → y < H-3 is stone
2. "the 3 layers under the surface dirt (...)" → the 3 layers beneath surface are dirt (with H-dependent variant)
3. "surface = ..." → surface block material

The tension is real but I think the author intends:
- y < H-3: stone
- H-3 ≤ y ≤ H-1... no.

Actually maybe the 3 layers are H-3, H-2, H-1? No, H-1 is surface.

Hmm, let me reconsider: maybe "surface" isn't a single block. In many generators, surface = top few blocks. But here it says "surface = snow if H≥46..." implying single value.

I'll go with my interpretation (3 sub-surface layers at H-4..H-2, deep stone below, surface at H-1). It's the most sensible. Let me proceed.

Hmm wait, actually let me reconsider whether "below H-3" might mean y <= H-3 (inclusive). If "below H-3" means y <= H-3, then stone covers 0..H-3, and 3 layers under surface = H-4,H-3,H-2 overlaps again at H-3.

No. Let me just go with my clean version. Moving on.

Now columnHeight:
"m = fractal at coords*0.004, h = fractal at coords*0.02, H = floor(5 + m*m*58 + h*10)."

So m = fractalNoise(wx*0.004, wz*0.004), h = fractalNoise(wx*0.02, wz*0.02). Then H = floor(5 + m*m*58 + h*10).

fractalNoise is the 2D fractal (value noise with 4 octaves).

Now trees: "on grass, when a per-column hash < 0.02 and the trunk fits inside the chunk: 4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

Per-column hash: an integer hash of (wx, wz) giving 0-1. If < 0.02, place tree (if on grass block and trunk fits).

Trunk: 4 wood blocks up from surface. So at surface y (H-1) which is grass, place wood at y=H-1..H+3? Wait, "4 wood blocks up". The trunk starts from the ground. The surface grass block is at H-1. Trunk goes up 4: H-1, H, H+1, H+2? Or H, H+1, H+2, H+3? 

"4 wood blocks up" — I'll place 4 wood blocks starting from the surface block's y up to y+3, i.e., replacing... no, only into air. The grass block stays. So wood at y = surface_y+1 to surface_y+4? That's 4 blocks. Let me place wood at (H-1)+1 ... (H-1)+4 = H to H+3. But need to fit inside chunk (y+something < 80). "trunk fits inside the chunk" means the leaves at top don't exceed y=79. Leaves extend up to surface_y + 4 + 2 = surface_y+6 roughly. Let me just check that surface_y + 7 < 80 or so. Actually "fits inside the chunk" probably means the tree height fits within the 0-79 range. Let me check: if surface_y + 6 >= 80, skip. Actually let me be careful: leaves top at surface_y + 6 (4 wood + 2 for the 5x5 layers). Let me define tree structure precisely.

Tree structure:
- Trunk: 4 wood blocks. From surface_y+1 to surface_y+4 (4 blocks). Actually let me reconsider — maybe trunk from surface_y to surface_y+3 (including the grass level)? No, grass stays. Let me do wood at surface_y+1 .. surface_y+4.

Hmm, but actually maybe the trunk replaces from the ground. Let me place wood blocks at y = surface_y+1 through surface_y+4 (4 blocks). Then leaves:
- "leaves as a 5x5 layer twice" — two layers of 5x5 leaves at the top. At surface_y+5 and surface_y+6, place 5x5 leaves centered on trunk.
- "then 3x3" — a 3x3 layer? Where? "as a 5x5 layer twice, then 3x3, then 1 on top". So after the two 5x5 layers, a 3x3 layer, then 1 on top. That's 2 + 1 + 1 = 5 leaf layers above the trunk top (surface_y+4). So leaves at surface_y+5 (5x5), surface_y+6 (5x5), surface_y+7 (3x3), surface_y+8 (1x1)? That's quite tall (total tree height ~9 from ground). That seems too tall.

Let me re-read: "4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top (only into air)."

Hmm, maybe it's: 4 wood up, then leaves. The leaves consist of: two 5x5 layers, then a 3x3 layer, then 1 on top. So the canopy is layered. Let me count total height: 4 (wood) + leaves layers. If leaves are at +5,+6 (5x5), +7 (3x3), +8 (1), total height from ground = 8. That's tall but OK for a stylized tree.

But "fits inside the chunk" — with height 8 above ground, need surface_y + 8 <= 79, i.e. surface_y <= 71. Since surface_y ≈ H-1 and H max is floor(5 + 1*58 + 1*10) = 73, so H up to ~78? Let me compute max H: m in [0,1], m*m in [0,1], so m*m*58 in [0,58]. h*10 in [0,10]. H = floor(5 + up to 58 + up to 10) = floor(73) = 73. So H max ~73, surface_y = 72. Tree top at 72+8 = 80. That's exactly at boundary (y must be < 80). So 72+8=80 is invalid (needs y<=79). Hmm. So I need to be careful.

Let me reconsider the tree height. Maybe leaves are closer. Let me re-read once more: "4 wood blocks up, leaves as a 5x5 layer twice, then 3x3, then 1 on top".

Alternative interpretation: The leaves form a shape: two 5x5 layers near the top, then going down... no. Let me think of it as a canopy from y=+5 to y=+8:
- +5: 5x5
- +6: 5x5
- +7: 3x3
- +8: 1x1

Total tree height = 4 wood + 4 leaf layers = 8 blocks above ground. Ground at surface_y. So top at surface_y+8.

To fit: surface_y + 8 <= 79 → surface_y <= 71 → H <= 72. Since H can be up to 73, occasionally skip. Let me require surface_y + 7 < 80 (i.e., surface_y + 8 <= 80, top at surface_y+8 which must be ≤ 79... wait y index max 79). Let me require (surface_y + 8) <= 79, i.e. surface_y <= 71. Actually if top leaf is at surface_y+8, that index must be ≤ 79. So surface_y+8 ≤ 79 → surface_y ≤ 71.

Hmm, but let me reconsider—maybe I'm overcomplicating. Let me just place leaves more compactly and check bounds. Let me define tree generation:

```
function placeTree(data, wx, wz, surfaceY) {
  // wood trunk 4 blocks
  for (let i=1;i<=4;i++) {
    const y = surfaceY + i;
    if (y >= 80) return false;
    data[idx(wx,wz,y)] = 5; // wood
  }
  // leaves
  // two 5x5 layers
  for (let layer=0; layer<2; layer++) {
    const y = surfaceY + 5 + layer; // y = surfaceY+5, surfaceY+6
    if (y >= 80) return false;
    placeLayer5x5(data, wx, wz, y);
  }
  // 3x3
  const y3 = surfaceY + 7;
  if (y3 < 80) placeLayer3x3(data, wx, wz, y3);
  // 1 on top
  const y1 = surfaceY + 8;
  if (y1 < 80) setBlockLocal(data, wx, wz, y1, 6);
  return true;
}
```

Where placeLayer5x5 places leaves in a 5x5 area centered on trunk, only into air (id 0). Similarly 3x3 and single.

"only into air" means we don't replace existing blocks (wood, grass, etc.), only fill empty spaces.

Let me define these helpers operating on the chunk data array with local coordinates. Since tree must fit inside chunk, and we checked trunk fits, but the 5x5 leaves might extend beyond chunk boundaries (lx from 0..15). If the trunk is at lx=0, the 5x5 leaves (spanning lx-2..lx+2) would go to lx=-2 which is out of chunk. So I need to check bounds within the chunk data for leaf placement too. "and the trunk fits inside the chunk" — the spec only mentions trunk fitting. But leaves extending out would be a problem. Let me just guard all leaf placements with bounds checks (0<=lx<16, 0<=lz<16). If out of bounds, skip that block. This naturally handles edges.

Actually, "trunk fits inside the chunk" likely means the trunk (4 blocks up) fits, AND implicitly we should guard leaves. Let me guard everything with bounds checks.

Now let me reconsider: the tree is placed during chunk generation. But the surface must be grass for a tree. So condition: surface block (y=H-1) is grass (id 1), and hash < 0.02.

Let me now also handle the noise functions.

**Value noise:**
"an integer-coordinate hash giving 0–1 (mix with large prime multipliers and xor-shifts), smoothed 2D noise via bilinear interpolation with smoothstep, 4 octaves combined into fractal noise, plus a 3D version for caves."

Let me implement:

Integer hash function:
```
function hash21(x, y) {
  // integer hash -> 0..1
  let h = x * 3747613937 + y * 707198113; // large primes
  h = (h ^ (h >>> 13)) >>> 0; // xor-shift
  h = (Math.imul(h, 4294967291)) >>> 0; // multiply by large prime
  h = (h ^ (h >>> 15)) >>> 0;
  return h / 4294967296; // 0..1
}
```

Hmm, Math.imul is available. But let me keep it simpler and robust. Let me use:
```
function hash2(x, y) {
  let h = (x * 1600130857 + y * 1335313933 + 1013333311) >>> 0;
  h = (h ^ (h >>> 13)) >>> 0;
  h = (Math.imul(h, 0x5bd1e9f5)) >>> 0;
  h = (h ^ (h >>> 15)) >>> 0;
  return h / 4294967296;
}
```

This gives a deterministic 0-1 value at integer coordinates.

Smoothed 2D noise (value noise):
```
function valueNoise2D(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const v00 = hash2(xi, yi);
  const v10 = hash2(xi+1, yi);
  const v01 = hash2(xi, yi+1);
  const v11 = hash2(xi+1, yi+1);
  // smoothing (smoothstep)
  const u = fade(xf), v = fade(yf);
  const x00 = lerp(v00, v10, u);
  const x01 = lerp(v01, v11, u);
  // wait, need to interpolate y first then x, or combine
  const top = lerp(v00, v10, u); // actually let me do proper bilinear
  ...
}
```

Proper bilinear:
```
function valueNoise2D(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const val00 = hash2(xi, yi);
  const val10 = hash2(xi+1, yi);
  const val01 = hash2(xi, yi+1);
  const val11 = hash2(xi+1, yi+1);
  const u = fade(xf), v = fade(yf);
  const i0 = lerp(val00, val10, u);
  const i1 = lerp(val01, val11, u);
  return lerp(i0, i1, v);
}
```

where fade(t) = t*t*t*(t*(t*6-15)+10) (smoothstep quintic) or simpler 3t²-2t³. The spec says "smoothstep", so I'll use smoothstep: fade(t) = t*t*(3-2t). Actually "smoothstep" typically t²(3-2t). Let me use that.

lerp(a,b,t) = a + (b-a)*t.

Fractal noise (4 octaves):
```
function fractalNoise2D(x, y) {
  let amp = 1, freq = 1, sum = 0, norm = 0;
  for (let o=0;o<4;o++) {
    sum += amp * valueNoise2D(x*freq, y*freq);
    norm += amp;
    amp *= 0.5; freq *= 2;
  }
  return sum / norm; // 0..1
}
```

3D noise for caves:
```
function valueNoise3D(x, y, z) {
  const xi=Math.floor(x), yi=Math.floor(y), zi=Math.floor(z);
  const xf=x-xi, yf=y-yi, zf=z-zi;
  // 8 corners
  const c000=hash3(xi,yi,zi), c100=hash3(xi+1,yi,zi), c010=hash3(xi,yi+1,zi), c110=hash3(xi+1,yi+1,zi);
  const c001=hash3(xi,yi,zi+1), c101=hash3(xi+1,yi,zi+1), c011=hash3(xi,yi+1,zi+1), c111=hash3(xi+1,yi+1,zi+1);
  const u=fade(xf),v=fade(yf),w=fade(zf);
  const i00=lerp(c000,c100,u), i10=lerp(c010,c110,u);
  const i01=lerp(c001,c101,u), i11=lerp(c011,c111,u);
  const j00=lerp(i00,i10,v), j10=lerp(i01,i11,v);
  return lerp(j00,j10,w);
}
function fractalNoise3D(x,y,z) {
  let amp=1,freq=1,sum=0,norm=0;
  for(let o=0;o<4;o++){sum+=amp*valueNoise3D(x*freq,y*freq,z*freq);norm+=amp;amp*=0.5;freq*=2;}
  return sum/norm;
}
```

hash3:
```
function hash3(x,y,z){
  let h=(x*1600130857+y*1335313933+z*1013333311+1013333311)>>>0;
  h=(h^(h>>>13))>>>0;
  h=(Math.imul(h,0x5bd1e9f5))>>>0;
  h=(h^(h>>>15))>>>0;
  return h/4294967296;
}
```

Hash for tree (per-column):
```
function columnHash(x,z){ return hash2(x,z); }
```
Use < 0.02.

Now let me think about the player physics and collision.

Player box: half-width 0.3, height 1.8, eye 1.62. So the player extends from feet to feet+1.8. Eye at feet+1.62. Half-width 0.3 means x and z extent ±0.3.

Spawn at x=8, z=8 (above terrain). So we find terrain height at (8,8) and spawn above it.

Physics:
- velocity.y -= gravity (25) each frame (or integrate).
- Position updated per-axis with collision.

Collision: AABB vs blocks. Move per axis:
- Move X: newX = player.x + vx*dt. Check collision with player box. If collide, revert x.
- Similarly Y, Z.

For Y: if moving down and collide, we're on a block → onGround = true, revert y. If moving up and collide, revert.

Let me implement collision check: given player AABB (minX,minY,minZ)-(maxX,maxY,maxZ), check if it overlaps any non-air block. Iterate over blocks in range.

```
function collides(px, py, pz) {
  // AABB
  const minX = px - 0.3, maxX = px + 0.3;
  const minY = py, maxY = py + 1.8;
  const minZ = pz - 0.3, maxZ = pz + 0.3;
  // block range
  const bx0 = Math.floor(minX), bx1 = Math.floor(maxX);
  const by0 = Math.floor(minY), by1 = Math.floor(maxY);
  const bz0 = Math.floor(minZ), bz1 = Math.floor(maxZ);
  for (let bx=bx0;bx<=bx1;bx++)
  for (let by=by0;by<=by1;by++)
  for (let bz=bz0;bz<=bz1;bz++) {
    if (getBlock(bx,by,bz) !== 0) return true;
  }
  return false;
}
```

Player position stored as feet position (px, py, pz) where py is feet y. Camera is at py + 1.62.

Movement:
```
velocity.y -= 25 * dt;
// move per axis
let nx = px + dx * speed * dt (relative to yaw)
...
```

Let me use delta time. Actually, let me simplify: use fixed-ish steps with dt from requestAnimationFrame.

Let me structure update:
```
const dx = (forward? ...) * speed * dt;
const dz = ...;
// apply gravity to dy
dy -= 25 * dt;
if (space && onGround) dy = 8.5;

// Move X
px += dx;
if (collides(px,py,pz)) px -= dx; // revert (assuming dx sign)
// Actually need to handle both directions. Let me revert properly.
```

Better approach: try moving along each axis; if new position collides, undo that axis move.

```
// X
let nx = px + dx;
if (!collides(nx, py, pz)) px = nx;
// Z
let nz = pz + dz;
if (!collides(px, py, nz)) pz = nz;
// Y
let ny = py + dy;
if (!collides(px, ny, pz)) { py = ny; onGround = false; }
else {
  if (dy < 0) onGround = true; // was falling, hit ground
  py = py; // revert
  dy = 0;
}
```

Wait, but this doesn't distinguish up collision. If dy>0 and collides, we bump head, revert and set dy=0. If dy<0 and collides, we landed, revert, onGround=true, dy=0. Let me refine:
```
let ny = py + dy;
if (!collides(px, ny, pz)) {
  py = ny;
  onGround = false;
} else {
  if (dy < 0) onGround = true;
  dy = 0;
}
```

Hmm but when dy>0 and collides, we should also reset dy to 0 (can't keep going up). The else sets dy=0. Good.

Speed relative to yaw: WASD moves relative to camera yaw (horizontal direction). Forward = -Z in world? Depends on camera. Let me define yaw such that forward vector = (sin(yaw), 0, cos(yaw)) or similar. Let me define:
- Camera looks in direction determined by yaw (Y rotation) and pitch (X rotation).
- Movement: forward vector projected on XZ plane.

Let me define:
```
const forward = [ -sin(yaw), 0, -cos(yaw) ]? 
```

Hmm, let me think. With rotation order YXZ and Euler, the camera direction is:
dir = [ sin(yaw)*cos(pitch), sin(pitch), -cos(yaw)*cos(pitch) ]? 

Let me just define movement direction independent of pitch (horizontal movement):
```
const sinYaw = Math.sin(yaw), cosYaw = Math.cos(yaw);
// forward (W) moves toward -Z when yaw=0? 
let mx=0, mz=0;
if (forward) { mx -= sinYaw; mz -= cosYaw; } // W
if (back) { mx += sinYaw; mz += cosYaw; } // S
if (right) { mx += cosYaw; mz -= sinYaw; } // D
if (left) { mx -= cosYaw; mz += sinYaw; } // A
```

This is standard. Let me verify: yaw=0, W → mx=0, mz=-1 (moving -Z). Camera at yaw=0 looks toward... with dir=[sin(yaw)cos(pitch)...], at yaw=0 pitch=0, dir=[0,0,-1]? Let me check camera direction.

With THREE.Euler(0,0,0,'YXZ') and a camera, default camera looks toward -Z. After rotating by yaw around Y, the forward becomes... Let me just align movement with the actual camera forward computed from the quaternion. Actually simpler: I'll compute camera forward from euler and use horizontal projection for movement. But to keep it robust, let me just use the trig above and ensure camera forward matches.

Camera direction from Euler (YXZ, degrees→radians):
```
const e = new THREE.Euler(pitch, yaw, 0, 'YXZ');
camera.quaternion.copy(e);
const dir = new THREE.Vector3();
camera.getWorldDirection(dir);
```
At yaw=0, pitch=0: camera looks toward -Z (0,0,-1). Movement W should move in that direction: mx=0, mz=-1. My formula gives W: mx=-sin(0)=0, mz=-cos(0)=-1. ✓. 

Now raycasting for break/place. Raycast from camera center (near point) in camera forward direction, distance 6. Use THREE.Raycaster. But the chunk meshes use vertex colors and one material. Raycaster should work.

```
const ray = new THREE.Raycaster();
ray.set(camera.position, forwardVector);
const hits = ray.intersectObjects(chunkMeshArray);
```

Wait, but the spec says "raycast from the camera center (max distance 6)". Camera center = camera position, direction = forward. Let me use camera.position and the camera's forward vector.

Actually "camera center" might mean the center of the screen (crosshair), which corresponds to straight ahead from camera. So ray from camera.position along camera forward. Yes.

From hit point p and face normal n:
- break target = floor(p - n*0.5)
- place cell = floor(p + n*0.5)

"per component" — floor each component of the resulting vector.

```
const p = hit.point;
const n = hit.face.normal;
const breakTarget = [Math.floor(p.x - n.x*0.5), Math.floor(p.y - n.y*0.5), Math.floor(p.z - n.z*0.5)];
const placeCell = [Math.floor(p.x + n.x*0.5), Math.floor(p.y + n.y*0.5), Math.floor(p.z + n.z*0.5)];
```

Outline: black wireframe box at breakTarget. Use THREE.LineSegments with EdgesGeometry or BoxGeometry wireframe. Position at breakTarget + 0.5 (center). 

Only while locked:
- Left click: set breakTarget to air (if not y==0).
- Right click: place selected block if placeCell is air and doesn't overlap player.

After edit rebuild the chunk, and also neighbor chunk if on border.

Rebuild function:
```
function rebuildChunk(cx, cz) {
  const key = cx+","+cz;
  const chunk = chunkData.get(key);
  if (!chunk) return;
  // build mesh from data
  const mesh = buildChunkMesh(chunk);
  // dispose old
  if (chunk.mesh) { scene.remove(chunk.mesh); chunk.mesh.geometry.dispose(); }
  scene.add(mesh);
  chunk.mesh = mesh;
}
```

buildChunkMesh iterates all blocks, builds BufferGeometry with position/normal/color (vertexColors) attributes.

Let me now write buildChunkMesh:
```
function buildChunkMesh(chunk) {
  const cx = ..., cz = ...;
  const positions = [];
  const normals = [];
  const colors = [];
  const data = chunk.data;
  for (let ly=0; ly<80; ly++) {
    for (let lz=0; lz<16; lz++) {
      for (let lx=0; lx<16; lx++) {
        const idx = (ly*16 + lz)*16 + lx;
        const id = data[idx];
        if (id === 0) continue;
        const wx = cx*16 + lx;
        const wy = ly;
        const wz = cz*16 + lz;
        for (const face of FACES) {
          const n = face[1];
          const nx = wx+n[0], ny = wy+n[1], nz = wz+n[2];
          if (getBlock(nx,ny,nz) === 0) {
            // add face
            const col = blockColors[id];
            const light = face[2];
            const r = (col>>16)&255, g=(col>>8)&255, b=col&255;
            for (const corner of face[3]) {
              positions.push(wx+corner[0], wy+corner[1], wz+corner[2]);
              normals.push(n[0],n[1],n[2]);
              colors.push(r*light/255, g*light/255, b*light/255);
            }
          }
        }
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals,3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors,3));
  const mat = blockMaterial; // shared
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(0,0,0); // at origin (chunk local)
  return mesh;
}
```

Wait, the mesh should be at chunk origin. Since vertices are in world coords and chunk spans [cx*16, cx*16+16], the mesh naturally sits at world position. Setting mesh.position to origin is correct because vertices already have world coords. Good.

blockColors: map id -> 0xRRGGBB. And I precompute per-id RGB.

Let me precompute:
```
const BLOCK = {AIR:0,GRASS:1,DIRT:2,STONE:3,SAND:4,WOOD:5,LEAVES:6,SNOW:7};
const blockColorRGB = {};
blockColorRGB[1] = [0x4caf50]; // store as [r,g,b] normalized? 
```

Actually let me store as [r,g,b] 0-1 multiplied by light. Let me precompute base RGB 0-1:
```
const BASE_RGB = {
  1: [0x4caf50], ...
};
```
Let me just convert:
```
function rgb(hex){ return [((hex>>16)&255)/255, ((hex>>8)&255)/255, (hex&255)/255 ]; }
```

blockColors[id] = rgb(hex).

Now the material: ONE shared MeshLambertMaterial with vertexColors true.
```
const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

vertexColors: true means it uses the 'color' attribute. Good.

Now the scene setup:
- renderer: THREE.WebGLRenderer, antialias maybe.
- background 0x87ceeb, fog THREE.Fog(0x87ceeb, 40, 110).
- ambient 0.65, directional 0.8.

Clouds: ~25 white transparent boxes at height ~90, drifting, wrapping around player.
```
const clouds = [];
for (i in 25) { create box mesh at random-ish position (deterministic), y~90, scale small. }
```
Each frame, recenter clouds around player x,z (wrap). Drift in x.

Water: one large semi-transparent blue plane at height 14.3, re-centered on player each frame. Visual only.
```
const water = new THREE.Mesh(planeGeo, new THREE.MeshLambertMaterial({color:0x..., transparent:true, opacity:...}));
water.rotation.x = -Math.PI/2; // flat
water.position.y = 14.3;
```
Recenter x,z on player each frame.

Hotbar UI: 7 slots, colors of blocks, numbers 1-7. Selected slot white border. Keys 1-7 or wheel select.

Start overlay: fullscreen, title, controls, "Click to play". On click, request pointer lock. Reappears when lock released.

Let me now also handle the cloud water and everything in the animate loop.

Let me also handle pointer lock events:
- Click overlay → overlay.style.display='none' + document.documentElement.requestPointerLock() (or element.requestPointerLock()).
- document.addEventListener('pointerlockchange', ...) → if not locked, show overlay.
- Mouse move → if locked, adjust yaw/pitch.
- Mouse down → if locked, break (left) or place (right). Also suppress context menu on contextmenu event.

Let me handle the "click to play" — clicking on the overlay. Since overlay is on top initially, and pointer not locked, clicking it requests lock. Once locked, subsequent clicks go to canvas.

Let me set up:
```
overlay.addEventListener('click', () => {
  overlay.style.display = 'none';
  document.documentElement.requestPointerLock();
});
```

Hmm, requestPointerLock should be called on a user gesture. Click works.

Pointer lock change:
```
document.addEventListener('pointerlockchange', () => {
  if (!document.pointerLockElement) {
    overlay.style.display = 'flex';
  }
});
```

Mouse move:
```
document.addEventListener('mousemove', (e) => {
  if (!document.pointerLockElement) return;
  yaw -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  pitch = Math.max(-Math.PI/2 + 0.001, Math.min(Math.PI/2 - 0.001));
});
```

Rotation order YXZ: camera quaternion set from Euler(pitch, yaw, 0, 'YXZ'). Let me set:
```
camera.quaternion.setFromEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ'));
```

Wait, order YXZ means Y first, then X, then Z. Euler(x,y,z,order) interprets as the order of intrinsic rotations. Let me just use it and verify camera looks right. With pitch around X and yaw around Y. Should be fine.

MouseDown:
```
document.addEventListener('mousedown', (e) => {
  if (!document.pointerLockElement) return;
  if (e.button === 0) { // left break
    // use current breakTarget
    if (breakTarget && breakTarget.y !== 0) {
      setBlock(bt[0],bt[1],bt[2], 0);
      rebuildAt(bt[0],bt[1],bt[2]);
    }
  } else if (e.button === 2) { // right place
    if (placeCell && getBlock(pc)===0 && !overlapsPlayer(placeCell)) {
      setBlock(pc[0],pc[1],pc[2], selectedBlock);
      rebuildAt(...);
    }
  }
});
```

Context menu:
```
document.addEventListener('contextmenu', e => e.preventDefault());
```

rebuildAt(x,y,z): determine chunk and neighbors.
```
function rebuildAt(x,y,z){
  const cx=Math.floor(x/16), cz=Math.floor(z/16);
  rebuildChunk(cx,cz);
  // neighbors if on border
  const lx = x-cx*16, lz=z-cz*16;
  if (lx===0) rebuildChunk(cx-1,cz);
  if (lx===15) rebuildChunk(cx+1,cz);
  if (lz===0) rebuildChunk(cx,cz-1);
  if (lz===15) rebuildChunk(cx,cz+1);
}
```

Now the main loop update for chunks:
```
function updateWorld() {
  const pcx = Math.floor(player.x/16);
  const pcz = Math.floor(player.z/16);
  // generate up to 4 chunks within radius 5
  let genCount = 0;
  for (let dz=-5;dz<=5;dz++)
  for (let dx=-5;dx<=5;dx++) {
    const cx=pcx+dx, cz=pcz+dz;
    if (genCount>=4) break;
    const key=cx+","+cz;
    if (!chunkData.has(key)) {
      generateChunk(cx,cz);
      genCount++;
    }
  }
  // mesh up to 2 chunks within 4 whose 4 neighbors have data
  let meshCount = 0;
  for (let dz=-4;dz<=4;dz++)
  for (let dx=-4;dx<=4;dx++) {
    if (meshCount>=2) break;
    const cx=pcx+dx, cz=pcz+dz;
    const key=cx+","+cz;
    if (chunkData.has(key) && !chunkData.get(key).mesh) {
      // check 4 neighbors
      if (chunkData.has((cx-1)+","+cz) && chunkData.has((cx+1)+","+cz) &&
          chunkData.has(cx+","+((cz-1))) && chunkData.has(cx+","+((cz+1)))) {
        rebuildChunk(cx,cz);
        meshCount++;
      }
    }
  }
  // cleanup chunks farther than 7
  for (const [key, chunk] of chunkData) {
    const cx=parseInt(key.split(',')[0]), cz=parseInt(key.split(',')[1]);
    const d = Math.max(Math.abs(cx-pcx), Math.abs(cz-pcz));
    if (d>7) {
      if (chunk.mesh) { scene.remove(chunk.mesh); chunk.mesh.geometry.dispose(); }
      chunkData.delete(key);
    }
  }
}
```

Wait, there's an issue: generating a chunk creates its data but not mesh. Meshing requires the chunk to have data AND 4 neighbors have data. But neighbors might not be generated yet. So a chunk might wait several frames until its neighbors are generated. That's fine per spec.

But there's a subtlety: when we generate a chunk, we should also rebuild any adjacent chunks whose neighbor (this one) now has data, so they can mesh. The spec says "build meshes for chunks within 4 chunks whose 4 neighbors already have data (max 2 per frame)". So the meshing loop checks neighbors. Since generation happens first, a newly generated chunk provides data for neighbors. But the meshing loop runs after generation in the same frame, so neighbors that just got generated will satisfy. But we only mesh 2/frame, so it takes time. That's acceptable — chunks appear gradually.

However, there's a potential issue: if I only ever run the generic meshing loop, and it only meshes chunks whose 4 neighbors all have data, then when I generate a chunk, the 4 adjacent chunks (up/down/left/right) become eligible. But those adjacent chunks already existed (had data) but no mesh. Now they can mesh. Good.

But wait — the very first chunks near spawn: player spawns at (8,8), so pcx=0, pcz=0. The chunk (0,0) needs neighbors (-1,0),(1,0),(0,-1),(0,1) to have data. Initially none. Generation order: I iterate dx,dz from -5. First generated might be (-5,-5) etc. Hmm, that's far. Actually the loop generates in order dx=-5..5, so first is dx=-5,dz=-5 → chunk (-5,-5). That's far from spawn. It'll take many frames to get to (0,0).

Let me reorder generation to prioritize near chunks. Let me sort by distance. Or iterate in a spiral/order by proximity. Let me just iterate distance from 0 upward:
```
// generate nearest first
let distList = [];
for dz,dx in -5..5: distList.push({dx,dz,d:abs(dx)+abs(dz)});
sort by d;
for item of sorted: if genCount<4 and !has: generate; genCount++;
```

That way spawn chunk gets generated early. Good.

Actually, let me reconsider. The meshing loop also iterates and picks nearest eligible. With generation prioritizing near, and meshing picking near-with-neighbors, the world pops in around the player. Good.

Let me also make sure spawn area is solid: spawn at (8,8), which is chunk (0,0). Need (0,0) meshed to know terrain height. But we spawn above terrain — we compute terrain height independently via columnHeight(8,8). So we can spawn regardless of meshing. Good. Spawn y = H(8,8) + 2 or so.

Let me now write the full code. Let me be careful about performance and correctness.

Let me also add the selection outline (wireframe box). Create once, reuse:
```
const outlineGeo = new THREE.BoxGeometry(1.01,1.01,1.01);
const outlineMat = new THREE.LineBasicMaterial({color:0x000000});
const outline = new THREE.LineSegments(outlineGeo, outlineMat);
outline.visible = false;
scene.add(outline);
```
Position at breakTarget+0.5. Update visibility each frame based on whether we have a valid target.

Now let me also double-check the raycast. The chunk meshes are in chunkMeshArray. But note: some chunks have data but no mesh yet (waiting for neighbors). Those won't be in the array (mesh null). Raycast only against meshes with geometry. That's fine.

Actually, I store chunk.mesh. Let me maintain a separate array `chunkMeshes` of meshes for raycasting, or iterate chunkData. Let me maintain `activeMeshes = []` and push/remove. Or just iterate chunkData entries where mesh exists. Simpler: keep array.

Let me maintain:
```
const chunkMeshes = []; // THREE.Mesh[]
```
In rebuildChunk, after creating mesh, push to chunkMeshes. But duplicates if called twice. Let me manage: when rebuilding, if there's an old mesh dispose and remove from array, add new. Let me handle in rebuildChunk.

Actually, let me just collect meshes from chunkData each raycast? That's cheap enough (few chunks). But cleaner to maintain array. Let me maintain array in rebuildChunk:
```
function rebuildChunk(cx,cz){
  const key=cx+","+cz;
  const chunk = chunkData.get(key);
  if(!chunk || !chunk.data) return;
  // dispose old
  if (chunk.mesh) {
    const i = chunkMeshes.indexOf(chunk.mesh);
    if(i>=0) chunkMeshes.splice(i,1);
    scene.remove(chunk.mesh);
    chunk.mesh.geometry.dispose();
  }
  const mesh = buildChunkMesh(cx,cz,chunk.data);
  scene.add(mesh);
  chunkMeshes.push(mesh);
  chunk.mesh = mesh;
}
```

Good.

Now, one concern: buildChunkMesh uses getBlock for neighbor checks, which reads other chunks. That's why neighbors need data. Good.

Let me also handle the water plane and clouds recentering each frame.

Clouds:
```
for each cloud: position.x = player.x + offset (mod wrap), position.z similarly, y=90. drift x += speed*dt. Wrap around player within some range.
```
Let me implement wrap: cloud base position relative to player, e.g., within ±500. Each frame x += drift; if (cloud.x - player.x > 500) cloud.x -= 1000; if < -500 add 1000.

Actually simpler: place clouds at player-relative positions and drift; wrap into [-R, R] around player.

Let me just do: cloud.position.x = player.x + (cloud.localX); cloud.position.z = player.z + (cloud.localZ); where localX, localZ are initial offsets in [-400,400]. Drift localX += speed; wrap localX into [-400,400].

Water plane:
```
water.position.x = player.x;
water.position.z = player.z;
```

Now let me write the HTML/CSS for hotbar and overlay.

CSS:
```
body { margin:0; overflow:hidden; background:#000; font-family:sans-serif; }
canvas { display:block; }
#crosshair { position:fixed; top:50%; left:50%; width:2px; height:16px; margin:-8px 0 0 -1px; background:rgba(255,255,255,0.8); }
Actually let me make a nicer crosshair: two crossing lines.
```

Let me make crosshair as a + shape:
```
#crosshair { position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); pointer-events:none; }
#crosshair::before, #crosshair::after { content:''; position:absolute; background:rgba(255,255,255,0.8); }
#crosshair::before { left:0; right:0; top:50%; height:2px; margin-top:-1px; }
#crosshair::after { top:0; bottom:0; left:50%; width:2px; margin-left:-1px; }
```

Hotbar:
```
#hotbar { position:fixed; bottom:10px; left:50%; transform:translateX(-50%); display:flex; gap:4px; background:rgba(0,0,0,0.6); padding:4px; border-radius:4px; }
.slot { width:40px; height:40px; border:2px solid rgba(255,255,255,0.3); display:flex; align-items:center; justify-content:center; color:#fff; font-size:12px; position:relative; }
.slot.selected { border-color:#fff; }
.slot .color { position:absolute; inset:4px; border-radius:2px; }
.slot .num { position:absolute; top:2px; left:3px; font-size:10px; text-shadow:1px 1px 1px #000; }
```

Overlay:
```
#overlay { position:fixed; inset:0; background:rgba(0,0,0,0.8); display:flex; flex-direction:column; align-items:center; justify-content:center; color:#fff; text-align:center; }
#overlay.hidden { display:none; }
```

Now the hotbar selection: selectedSlot starts 0 (grass). Keys 1-7 map to slot index 0-6. Wheel changes selection (wrap).

```
let selectedSlot = 0;
const hotbarBlocks = [1,2,3,4,5,6,7]; // grass,dirt,stone,sand,wood,leaves,snow
```

Update hotbar DOM to show selected border.

Wheel:
```
window.addEventListener('wheel', (e) => {
  if (!document.pointerLockElement) return;
  selectedSlot = (selectedSlot + (e.deltaY>0?1:-1) + 7) % 7;
  updateHotbar();
});
```

Keys:
```
window.addEventListener('keydown', (e) => {
  const n = parseInt(e.key);
  if (n>=1 && n<=7) { selectedSlot = n-1; updateHotbar(); }
});
```

updateHotbar rebuilds slot borders.

Now let me assemble everything. Let me also make sure I request animation frame loop.

Let me consider the camera direction for raycasting. I'll compute forward vector from camera quaternion:
```
const forward = new THREE.Vector3();
camera.getWorldDirection(forward);
```
Then:
```
ray.set(camera.position, forward);
```

Actually, using camera position directly. The eye is at py+1.62. Camera position should be set to eye position. Let me set camera.position.set(player.x, player.py + 1.62, player.z) each frame. And quaternion from euler.

Let me now also verify the raycast hit parsing and that we only act when locked.

Edge: raycast might hit nothing (no block within 6). Then breakTarget undefined; don't show outline.

Let me finalize the outline update:
```
if (locked && hit) {
  outline.position.set(bt[0]+0.5, bt[1]+0.5, bt[2]+0.5);
  outline.visible = true;
} else {
  outline.visible = false;
}
```

Now, one more consideration: the raycast uses intersectObjects with chunkMeshes. But water plane and clouds are separate; we don't want to hit those. chunkMeshes only has terrain meshes. Good.

Let me also ensure the raycaster distance is 6: ray.set(origin, dir) then ray.far = 6? Actually Raycaster distance: set(origin, direction, near, far). Or after set, set ray.far. Let me use ray.set(camera.position, forward) and then the default far is Infinity; I need to limit to 6. Let me pass far: ray.set(camera.position, forward, 0, 6)? The signature is set(cameraOrigin, direction, near, far). Actually THREE.Raycaster.set(origin, direction, near=1, far=Infinity). So ray.set(pos, dir, 1, 6).

Hmm, but direction should be normalized. getWorldDirection returns normalized. Good.

Let me write it all out now.

Let me also double check: getBlock returns 0 for air. When placing water visually it doesn't affect getBlock. Good.

Let me also handle the "falling below y -20 teleports back to spawn":
```
if (player.py < -20) { player.py = spawnY; player.px = 8; player.pz = 8; player.dy = 0; }
```

spawnY = columnHeight(8,8) + 1. Let me compute at init.

Now let me also make sure the initial spawn works: at start, no chunks generated. columnHeight(8,8) computes deterministically. Good. Spawn y = H+1 (standing on top). Actually let me spawn at H+2 to be safe above any water? Just H+1.5 or so. Let me do spawnY = H(8,8) + 1.

Wait, but if there's water at 14.3 and terrain below, spawning at H+1 might be underwater if H<14. Let me spawn a bit higher, H+2. Fine.

Let me now write everything.

Let me reconsider the fractal noise normalization. Each octave valueNoise returns 0..1. Weighted sum / norm of amps returns 0..1. Good.

For column height, m and h are fractal values in [0,1]. H = floor(5 + m*m*58 + h*10). With m,h in [0,1], H in [5, 73]. Good.

Let me reconsider caves: "for y between 3 and H−2, if 3D noise at position*0.09 exceeds 0.67, set air." So noise3D(wx*0.09, wy*0.09, wz*0.09) > 0.67 → air. I use fractalNoise3D. Good.

But wait, fractalNoise3D with 4 octaves and freq multiplier: at position*0.09, octaves sample at 0.09, 0.18, 0.36, 0.72. That's fine for cave carving.

Now trees: columnHash = hash2(wx, wz) < 0.02. On grass block (surface is grass, id 1). Place tree.

Let me make sure tree leaves only replace air. During generation, after filling column, we place tree. The trunk occupies y=H..H+3 (4 blocks above surface at H-1). Wait surface at H-1, trunk from H to H+3 (4 blocks). Then leaves at H+4,H+5 (5x5), H+6 (3x3), H+7 (1). Let me recompute offsets.

Trunk: 4 wood blocks "up". Starting just above surface (surface at y=H-1). So trunk at y = H, H+1, H+2, H+3 (that's 4 blocks: H through H+3). 

Leaves: "5x5 layer twice" at y = H+4 and H+5. "then 3x3" at y=H+6. "then 1 on top" at y=H+7.

Total height from surface: 4 (trunk) + 4 (leaf layers) = up to H+7. Top leaf at H+7. Need H+7 <= 79 → H <= 72. Since H max 73, occasionally skip if H+7 >= 80.

Let me guard: if (H + 7 >= 80) skip. Actually let me check each layer as I place, but simplest: require surfaceY + 8 <= 80 where surfaceY = H-1, i.e., H+7 <= 79 → H <= 72. Let me use if (wy + 8 > 79) skip where wy=H-1... let me just compute topY = surfaceY + 8 = H+7. If topY > 79, skip tree.

Hmm wait, let me recount leaf layers heights: trunk top at H+3. Leaves: 5x5 at H+4, H+5; 3x3 at H+6; 1 at H+7. So highest block is H+7. topY = H+7. Condition to fit: H+7 <= 79 → H <= 72.

Let me place:
```
if (isGrass && hash<0.02 && (H+7) <= 79) {
  // trunk
  for (let t=0;t<4;t++) setLocal(wx,wz, surfaceY+1+t, 5); // y=H..H+3
  // leaves 5x5 twice
  for (let t=0;t<2;t++) place5x5(wx,wz, surfaceY+5+t);
  // 3x3
  place3x3(wx,wz, surfaceY+7);
  // 1 on top
  setLocal(wx,wz, surfaceY+8, 6);
}
```

Wait surfaceY = H-1. surfaceY+1+3 = H+3 (trunk top). surfaceY+5 = H+4 (first 5x5). surfaceY+5+1 = H+5 (second 5x5). surfaceY+7 = H+6 (3x3). surfaceY+8 = H+7 (top). Good.

place5x5(cx,cz,y): for dx in -2..2, dz in -2..2, if not on trunk center (0,0) maybe skip? The spec says "5x5 layer" — a full 5x5 of leaves. But the trunk is in the middle. "only into air" — so we fill leaves only where air; the trunk blocks (wood) won't be overwritten. So a full 5x5 minus where wood already is. Let me just fill 5x5, checking air (set only if current is air). Center (0,0) is wood, so it stays wood. Good.

```
function place5x5(wx,wz,y){
  for (let dx=-2;dx<=2;dx++)
  for (let dz=-2;dz<=2;dz++){
    const lx=wx+dx, lz=wz+dz;
    if (lx<0||lx>=16||lz<0||lz>=16) continue;
    if (getLocal(lx,lz,y)===0) setLocal(lx,lz,y,6);
  }
}
```

Wait, need local coords for bounds check. lx = wx+dx, but that's world. Local = (wx+dx) - cx*16. Since wx=cx*16+olx, lx_world = cx*16+olx+dx. If dx makes it cross chunk boundary, local goes out of [0,16). Let me compute local properly:
```
const nlx = (wx+dx) - cx*16;
const nlz = (wz+dz) - cz*16;
if (nlx<0||nlx>=16||nlz<0||nlz>=16) continue;
setLocal(nlx,nlz,y,6);
```

setLocal(lx,lz,y,id): data[(y*16+lz)*16+lx]=id.

getLocal similar returns data[...].

Let me define these helpers operating on the chunk data array with local coordinates.

place3x3 similar with dx,dz in -1..1.

Now, importantly, tree placement happens within generateChunk, which has the data array. I'll inline or use closures. Let me pass data, and also cx,cz for local conversion. Actually since tree is within the same chunk and trunk fits, but leaves may cross into neighbor chunk (edge). If a leaf would go into neighbor chunk, we skip it (bounds check). That's fine — tree just clips at chunk boundary. Acceptable.

But actually, there's a subtle issue: the spec says "the trunk fits inside the chunk". This suggests they only check trunk, assuming leaves also fit because trunk is usually not at the very edge. But with random chunk positions, trunk could be near edge. My bounds check on leaves handles it gracefully. Good.

Let me now also double check: generateChunk fills the column loop and then does tree. Order: fill columns (heightmap + caves), then for each grass column attempt tree. Let me structure:

```
function generateChunk(cx,cz){
  const data = new Uint8Array(20480);
  for (let lz=0;lz<16;lz++){
    for (let lx=0;lx<16;lx++){
      const wx=cx*16+lx, wz=cz*16+lz;
      const H = columnHeight(wx,wz);
      for (let y=0;y<H;y++){
        let id;
        if (y===0) id=3;
        else if (y===H-1) id = surfaceMat(H);
        else if (y>=H-4) id = subMat(H);
        else id=3;
        // cave
        if (y>=3 && y<=H-2){
          if (fractalNoise3D(wx*0.09,y*0.09,wz*0.09) > 0.67) continue;
        }
        data[(y*16+lz)*16+lx] = id;
      }
      // tree
      const surfId = data[(（H-1)*16+lz)*16+lx];
      if (surfId===1 && hash2(wx,wz) < 0.02 && (H+7)<=79){
        // trunk
        for (let t=0;t<4;t++) if ((H-1)+1+t < 80) data[((H+t)*16+lz)*16+lx]=5;
        ...
      }
    }
  }
  chunkData.set(cx+","+cz, {data, mesh:null});
}
```

Hmm, careful with index computation. Let me define a local index function inside generateChunk:
```
const idx = (y,lx,lz) => (y*16+lz)*16+lx;
```

Let me write tree placement using this idx and local coords for leaves.

Let me also reconsider: for trunk, the block at (H-1) is grass (surface). Trunk goes from H to H+3. So set idx(H, lx, lz)=5, idx(H+1,..)=5, idx(H+2,..)=5, idx(H+3,..)=5. That's 4 blocks. Good. But wait, should the trunk include the surface grass level? Typically tree trunk stands on the ground. Here surface is grass at H-1, trunk starts at H (above grass). So the grass block remains as the "ground" and trunk rises above it. That's fine visually.

Hmm, but actually maybe the trunk should start AT the surface. Let me reconsider: "4 wood blocks up". If we place 4 wood from H-1 to H+2, that replaces the grass block with wood. But then there's no grass. The spec says trees are "on grass", and leaves replace only air. If trunk replaces grass, then the base is wood. That might be fine too. But "only into air" applies to leaves, not trunk. The trunk presumably replaces whatever's there (grass). Let me place trunk from H-1+1 = H to H+3 (4 blocks above grass), leaving grass at H-1. That keeps a grass block at the base which is more natural. Actually, either is acceptable. Let me leave grass at H-1 and trunk above. 

Hmm, but then the 5x5 leaf layers at H+4,H+5 don't touch the grass. Fine.

Wait, actually, let me reconsider. If trunk is at H..H+3 and leaves at H+4+, then there's a gap? No: trunk H..H+3, leaves H+4..H+7 contiguous. Good, no gap.

Let me finalize tree:
```
// trunk
for (let t=0;t<4;t++) data[idx(H+t, lx, lz)] = 5;
// leaves
for (let t=0;t<2;t++) place5x5(data, idx, cx,cz, wx,wz, H+4+t);
place3x3(data, idx, cx,cz, wx, wz, H+6);
data[idx(H+7, lx, lz)] = 6;
```

place5x5:
```
function place5x5(data, idx, cx,cz, wx,wz, y){
  for (let dx=-2;dx<=2;dx++){
    for (let dz=-2;dz<=2;dz++){
      const nlx = (wx+dx) - cx*16;
      const nlz = (wz+dz) - cz*16;
      if (nlx<0||nlx>=16||nlz<0||nlz>=16) continue;
      if (data[idx(y,nlx,nlz)] === 0) data[idx(y,nlx,nlz)] = 6;
    }
  }
}
```

place3x3 similar with -1..1.

Note: the center block (dx=dz=0) at y=H+4 is idx(H+4, lx, lz) which is air (above trunk top H+3), so it becomes leaf. Good.

Now, there's a subtlety: H+4 might be >= 80 for large H even if H+7<=79 check passed? No, if H+7<=79 then H+4<=76<80. Fine. But let me guard anyway with checks in place5x5 (y<80). Actually y is always <80 here. But let me add y>=80 guards to be safe. I'll add a check.

Let me now write the whole thing out cleanly.

Let me also reconsider the meshing neighbor requirement and make sure spawn chunk gets meshed. Player at (8,8), pcx=0,pcz=0. Chunk (0,0) neighbors: (-1,0),(1,0),(0,-1),(0,1). These need data. Generation prioritizes near chunks. Distance of (-1,0) from (0,0) is 1, so it'll be generated early (within first 4). Then (0,0) can mesh after all 4 neighbors generated. With 4/frame generation, neighbors at distance 1 generated in frame 1 (all four distance-1 chunks: (±1,0),(0,±1) have distance 1, that's 4 chunks — exactly the 4 we generate per frame!). So frame 1 generates (-1,0),(1,0),(0,-1),(0,1). Frame 2: next nearest distance-2 chunks. Meanwhile meshing: frame 1 after gen, chunk (0,0) neighbors? Only if they have data — they're generated at end of frame 1's generation loop. The meshing loop runs after, so (0,0) now has all 4 neighbors with data → eligible. Meshing picks nearest eligible: (0,0) distance 0. So frame 1 meshes (0,0)! Great, spawn chunk appears immediately.

Wait, but generation generates 4 chunks per frame. Distance-1 chunks: there are exactly 4 ((-1,0),(1,0),(0,-1),(0,1)). Plus (0,0) itself is distance 0 but already... no, (0,0) has no data initially, so it'd be generated too. Let me recount. Distances from (0,0):
- 0: (0,0) — 1 chunk
- 1: (±1,0),(0,±1) — 4 chunks
- 2: (±2,0),(0,±2),(±1,±1) — 8 chunks
...

Generation prioritizes nearest. Frame 1 (genCount 0→4): generate distance-0 (0,0), then distance-1: (-1,0),(1,0),(0,-1),(0,1). That's 5 chunks but limit 4! So we generate (0,0) and 3 of the distance-1 chunks. Then (0,0) is missing one neighbor. Hmm.

Order matters. If I sort by distance and iterate, (0,0) first (dist 0), then 4 dist-1 chunks but only 3 fit (limit 4 total). So one dist-1 chunk not generated this frame. Say (0,1) not generated. Then (0,0) missing (0,1) neighbor → can't mesh. Frame 2: generate remaining dist-1 (0,1) and others. Then (0,0) can mesh. So spawn chunk appears frame 2. Fine, minor delay.

Actually, let me reconsider: should I generate (0,0) first? It's distance 0, nearest. Yes. Then dist-1. With limit 4: (0,0), (-1,0),(1,0),(0,-1). Missing (0,1). Frame 2: (0,1) and next. Then mesh (0,0). OK.

Alternatively, I could mesh (0,0) as soon as possible. It works out. Fine.

Let me make sure the meshing loop also prioritizes nearest. I'll sort the meshing candidates by distance too. Or iterate distance outward. Let me iterate dx,dz and compute distance, sort, pick first 2 eligible.

Actually simpler: iterate distance d from 0 to 4, inner loops, and break when meshCount reaches 2.

Let me restructure generation and meshing with distance ordering.

Let me write a helper to get ordered chunk coords within radius:
Actually let me just do nested loops with distance sorting inline.

Let me write:
```
function updateWorld(){
  const pcx=Math.floor(px/16), pcz=Math.floor(pz/16);
  // gather candidate chunk coords
  const gens = [];
  for(let dz=-5;dz<=5;dz++) for(let dx=-5;dx<=5;dx++){
    gens.push({cx:pcx+dx, cz:pcz+dz, d:Math.abs(dx)+Math.abs(dz)});
  }
  gens.sort((a,b)=>a.d-b.d);
  let gc=0;
  for(const c of gens){
    if(gc>=4) break;
    const key=c.cx+","+c.cz;
    if(!chunkData.has(key)){ generateChunk(c.cx,c.cz); gc++; }
  }
  // mesh
  const mes = [];
  for(let dz=-4;dz<=4;dz++) for(let dx=-4;dx<=4;dx++){
    mes.push({cx:pcx+dx,cz:pcz+dz,d:Math.abs(dx)+Math.abs(dz)});
  }
  mes.sort((a,b)=>a.d-b.d);
  let mc=0;
  for(const c of mes){
    if(mc>=2) break;
    const key=c.cx+","+c.cz;
    const ch = chunkData.get(key);
    if(ch && !ch.mesh){
      if(chunkData.has((c.cx-1)+","+c.cz) && chunkData.has((c.cx+1)+","+c.cz) &&
         chunkData.has(c.cx+","+((c.cz-1))) && chunkData.has(c.cx+","+((c.cz+1)))){
        rebuildChunk(c.cx,c.cz); mc++;
      }
    }
  }
  // cleanup
  for(const [key,ch] of chunkData){
    const [ks,kz]=key.split(','); const cx=+ks,cz=+kz;
    if(Math.max(Math.abs(cx-pcx),Math.abs(cz-pcz))>7){
      if(ch.mesh){ scene.remove(ch.mesh); ch.mesh.geometry.dispose(); }
      const i=chunkMeshes.indexOf(ch.mesh); if(i>=0)chunkMeshes.splice(i,1);
      chunkData.delete(key);
    }
  }
}
```

Good.

Now let me write buildChunkMesh(cx,cz,data):
```
function buildChunkMesh(cx,cz,data){
  const pos=[],nor=[],col=[];
  for(let ly=0;ly<80;ly++){
    for(let lz=0;lz<16;lz++){
      for(let lx=0;lx<16;lx++){
        const id=data[(ly*16+lz)*16+lx];
        if(id===0) continue;
        const wx=cx*16+lx, wz=cz*16+lz;
        for(let f=0;f<6;f++){
          const face=FACES[f];
          const nx=wx+face.nx, ny=ly+face.ny, nz=wz+face.nz;
          if(getBlock(nx,ny,nz)===0){
            const base=BASE_RGB[id];
            const light=face.light;
            for(let v=0;v<4;v++){
              const corner=face.corners[v];
              pos.push(wx+corner[0], ly+corner[1], wz+corner[2]);
              nor.push(face.nx,face.ny,face.nz);
              col.push(base[0]*light, base[1]*light, base[2]*light);
            }
          }
        }
      }
    }
  }
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(nor,3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  const mesh=new THREE.Mesh(geo, blockMaterial);
  return mesh;
}
```

FACES with nx,ny,nz and corners. Let me define FACES as objects:
```
const FACES = [
  { nx:0, ny:1, nz:0, light:1.0, corners:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { nx:1, ny:0, nz:0, light:0.8, corners:[[1,1,0],[1,1,1],[1,0,1],[1,0,0]] },
  { nx:-1,ny:0, nz:0, light:0.8, corners:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
  { nx:0, ny:0, nz:1, light:0.8, corners:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]] },
  { nx:0, ny:0, nz:-1, light:0.8, corners:[[0,1,0],[1,1,0],[1,0,0],[0,0,0]] },
  { nx:0, ny:-1, nz:0, light:0.55, corners:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
];
```

BASE_RGB:
```
const BASE_RGB = {
  1:[0x4caf50], 2:[0x795548], 3:[0x9e9e9e], 4:[0xe7d9a8],
  5:[0x8d6e63], 6:[0x2e7d32], 7:[0xffffff]
};
```
Convert each to [r/255,g/255,b/255].

Let me define a helper:
```
function toRGB(hex){ return [((hex>>16)&255)/255, ((hex>>8)&255)/255, (hex&255)/255 ]; }
```

Apply to each.

Now the material:
```
const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
```

vertexColors: true means it uses the 'color' attribute. Good.

Now let me write the complete file.

Let me also add the selection outline (wireframe box). Create once, reuse:

Now the animate loop:
```
function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(delta/1000, 0.25);
  update(dt);
  render();
}
```

update(dt):
```
// movement
... compute input direction ...
// gravity
dy -= 25*dt;
// jump
if (keys.space && onGround) { dy = 8.5; onGround=false; }
// move per axis
let nx = px + dirX*speed*dt;
if(!collides(nx,py,pz)) px=nx;
let nz = pz + dirZ*speed*dt;
if(!collides(px,py,nz)) pz=nz;
let ny = py + dy*dt;
if(!collides(px,ny,pz)){ py=ny; onGround=false; } else { if(dy<0) onGround=true; dy=0; }
// fall respawn
if(py < -20){ py=spawnY; px=8; pz=8; dy=0; }
// camera
camera.position.set(px, py+1.62, pz);
camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));
// world
updateWorld();
// raycast
updateTarget();
// outline
...
// clouds/water recenter
```

Let me handle input direction:
```
let mx=0,mz=0;
if(keys.w) { mx-=sinY; mz-=cosY; }
if(keys.s) { mx+=sinY; mz+=cosY; }
if(keys.d) { mx+=cosY; mz-=sinY; }
if(keys.a) { mx-=cosY; mz+=sinY; }
// normalize horizontal
const len=Math.hypot(mx,mz);
if(len>0){ mx/=len; mz/=len; }
dirX=mx; dirZ=mz;
```

speed=5.5.

Now the keydown/keyup for WASD and space:
```
const keys={};
window.addEventListener('keydown', e=>{
  keys[e.code]=true;
  const n=parseInt(e.key);
  if(!isNaN(n)&&n>=1&&n<=7){ selectedSlot=n-1; updateHotbar(); }
});
window.addEventListener('keyup', e=>{ keys[e.code]=false; });
```

Note space: e.code === 'Space'. Let me use keys['Space'].

Let me set:
```
if (keys['Space'] && onGround){ dy=8.5; onGround=false; }
```

Now mouse:
```
document.addEventListener('mousemove', e=>{
  if(!document.pointerLockElement) return;
  yaw -= e.movementX*0.002;
  pitch -= e.movementY*0.002;
  pitch=Math.max(-1.5708+1e-4, Math.min(1.5708-1e-4, pitch));
});
```

mousedown:
```
document.addEventListener('mousedown', e=>{
  if(!document.pointerLockElement) return;
  if(e.button===0){ // break
    if(outline.visible && bt[1]!==0){
      setBlock(bt[0],bt[1],bt[2],0);
      rebuildAt(bt[0],bt[1],bt[2]);
    }
  } else if(e.button===2){ // place
    if(outline.visible){
      const pc=placeCell;
      if(getBlock(pc[0],pc[1],pc[2])===0 && !playerOverlaps(pc[0],pc[1],pc[2])){
        setBlock(pc[0],pc[1],pc[2], hotbarBlocks[selectedSlot]);
        rebuildAt(pc[0],pc[1],pc[2]);
      }
    }
  }
});
```

playerOverlaps(x,y,z): check if the placed block's AABB overlaps player box.
```
function playerOverlaps(bx,by,bz){
  const minX=px-0.3, maxX=px+0.3;
  const minY=py, maxY=py+1.8;
  const minZ=pz-0.3, maxZ=pz+0.3;
  return !(bx+1<=minX || bx>=maxX || by+1<=minY || by>=maxY || bz+1<=minZ || bz>=maxZ);
}
```

contextmenu:
```
document.addEventListener('contextmenu', e=>e.preventDefault());
```

pointer lock:
```
overlay.addEventListener('click', ()=>{
  overlay.classList.add('hidden');
  document.documentElement.requestPointerLock();
});
document.addEventListener('pointerlockchange', ()=>{
  if(!document.pointerLockElement) overlay.classList.remove('hidden');
});
```

Wait, requestPointerLock might fail if not from user gesture. The click handler is a user gesture, good.

Also, clicking on canvas (not overlay) should request lock if not locked. Let me add canvas mousedown to request lock when not locked:
Actually, the overlay covers fullscreen initially. Once clicked, lock requested. If lock released, overlay reappears. So clicking overlay again re-locks. Good. But what about clicking the canvas when overlay hidden but not locked? Shouldn't happen normally. Let me add a safety: on canvas mousedown when not locked, request lock. But since overlay is hidden when locked, and shown when not, clicking when shown triggers re-lock. Fine.

Let me also handle window resize:
```
window.addEventListener('resize', ()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
```

Now let me write the HTML structure and CSS.

Let me also make sure the canvas is fullscreen and body no margin.

Let me write the full code now. I'll be thorough.

Let me reconsider one thing: the raycaster direction. I'll compute forward from camera each frame:
```
const fwd = new THREE.Vector3();
camera.getWorldDirection(fwd);
ray.set(camera.position, fwd);
ray.far = 6;
```
Actually ray.set(pos, dir, near, far). Let me do ray.set(camera.position, fwd, 0.01, 6).

Hmm, near 0.01 to avoid self-hit. Good.

hits = ray.intersectObjects(chunkMeshes, false).

If hits.length>0: hit=hits[0]; p=hit.point; n=hit.face.normal.
Compute bt and pc.

Let me store bt and placeCell as arrays.

Now, note: hit.face.normal is in object space but for these axis-aligned meshes aligned to world, it equals world normal. Good.

Let me write it all.

Also need to double-check: getBlock for neighbor in buildChunkMesh reads other chunks. During generation we don't mesh, so no neighbor reads. During rebuild, neighbor reads happen. Fine.

Let me also make sure setBlock creates chunk entry if missing (it does).

Now, about the water plane: 
```
const waterGeo = new THREE.PlaneGeometry(2000, 2000);
const waterMat = new THREE.MeshLambertMaterial({ color:0x3fa3e0, transparent:true, opacity:0.7, side:THREE.DoubleSide });
const water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);
```
Recenter each frame: water.position.x = px; water.position.z = pz.

Clouds:
```
const clouds = [];
for(let i=0;i<25;i++){
  const size = 20 + (i%5)*10;
  const geo = new THREE.BoxGeometry(size, 8, size*0.7);
  const mat = new THREE.MeshLambertMaterial({ color:0xffffff, transparent:true, opacity:0.85 });
  const m = new THREE.Mesh(geo, mat);
  const ang = i*137.5*Math.PI/180; // spread
  const rad = 150 + i*7;
  m.userData = { rx: Math.cos(ang)*rad, rz: Math.sin(ang)*rad, speed: 5 + (i%3)*2 };
  scene.add(m);
  clouds.push(m);
}
```
Recenter: 
```
for(const c of clouds){
  c.position.x = px + c.userData.rx;
  c.position.z = pz + c.userData.rz;
  c.position.y = 90;
  c.userData.rx += c.userData.speed*dt;
  // wrap into [-300,300]
  if(c.userData.rx > 300) c.userData.rx -= 600;
  if(c.userData.rx < -300) c.userData.rx += 600;
}
```

Good.

Now let me finalize and write the complete HTML.

Let me reconsider the collision function performance: it's called 3x per frame, iterating block ranges. For a player, range is small (~1 block). Fine.

Let me also ensure that when we break a block at y=0 we don't (spec: "left click sets the target to air (not at y 0)"). So guard bt[1]!==0.

Now, one more: after breaking/placing, we call rebuildAt which rebuilds chunk and possibly neighbors. Good.

Let me also handle the case where placeCell overlaps player — skip (already guarded).

Let me write the final code.

Actually, let me reconsider the player spawn and initial state. Before any chunks generated, collides() will read getBlock which returns 0 (air) for missing chunks. So player falls through "empty" space until terrain. But terrain isn't meshed yet, and getBlock returns 0 for ungenerated chunks. So player would fall forever until a chunk generates and has solid blocks below. Actually, at spawn we compute H(8,8) and spawn at H+2. The block at H+1 (feet region) — is it solid? getBlock(8, H+1, 8): chunk (0,0) not generated yet → returns 0. So player falls. Next frame, generation creates chunk (0,0) with data, so getBlock(8, H+1, 8) returns the actual block (probably air if it's above surface or the surface block). Eventually player lands on terrain. Good, this is fine — player spawns and falls to ground.

But there's a catch: generation creates chunk (0,0) data but meshing takes another frame. getBlock reads data (available after generation), so collision works once data exists. Good.

Let me set spawnY at init:
```
const spawnH = columnHeight(8,8);
let spawnY = spawnH + 1.5;
let px=8, py=spawnY, pz=8;
```

Actually let me spawn at spawnH + 2 to be safe.

Let me now also verify columnHeight uses fractalNoise2D which uses valueNoise2D which uses hash2. All defined. Good.

Let me write the code fully now.

Let me also double check: the material vertexColors requires the geometry to have a color attribute, which it does. And MeshLambertMaterial supports vertexColors. Good.

One concern: Float32BufferAttribute is available as THREE.Float32BufferAttribute in r128. Yes.

Another: THREE.Euler, THREE.Vector3, THREE.Raycaster, THREE.LineSegments, THREE.BoxGeometry, THREE.LineBasicMaterial, THREE.EdgesGeometry — all in r128. Yes.

Let me also add antialias and pixelRatio for crispness.

Let me write it.

Actually, let me reconsider the "far 400" camera. near should be small, like 0.1. far 400. Fog 40-110. Good.

Let me also make sure the directional light has a position and casts shadows? Not needed. Just intensity 0.8. Ambient 0.65.

Let me write:
```
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(0.3, 1, 0.5).normalize();
scene.add(dir);
```

Now let me write the complete HTML file.

Let me be careful with template literals and escaping in the single code block. I'll use regular strings mostly.

Let me write it all out.

Actually, I realize I should double-check the winding for the +X and -X and +Z/-Z faces once more since I derived them, but let me trust the cross-product verification I did. Let me re-verify +X quickly:
FACES +X: corners [[1,1,0],[1,1,1],[1,0,1],[1,0,0]], normal [1,0,0].
Triangle c0,c1,c2: c0=[1,1,0],c1=[1,1,1],c2=[1,0,1].
e1=c1-c0=[0,0,1], e2=c2-c0=[0,-1,1].
cross(e1,e2) = [0*1-1*(-1), 1*0-0*1, 0*(-1)-0*0] = [0+1, 0-0, 0] = [1,0,0] ✓.

-X: corners [[0,0,0],[0,0,1],[0,1,1],[0,1,0]], normal [-1,0,0].
c0=[0,0,0],c1=[0,0,1],c2=[0,1,1]. e1=[0,0,1],e2=[0,1,1]. cross([0,0,1],[0,1,1])=[0*1-1*1,1*0-0*1,0*1-0*0]=[-1,0,0] ✓.

+Z: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]], normal[0,0,1].
c0,c1=[1,0,0],c2=[1,1,0]. e1=[1,0,0],e2=[1,1,0]. cross=[0*0-0*1,0*1-1*0,1*1-0*1]=[0,0,1] ✓.

-Z: [[0,1,0],[1,1,0],[1,0,0],[0,0,0]], normal[0,0,-1].
c0=[0,1,0],c1=[1,1,0],c2=[1,0,0]. e1=[1,0,0],e2=[1,-1,0]. cross([1,0,0],[1,-1,0])=[0*0-0*(-1),0*1-1*0,1*(-1)-0*1]=[0,0,-1] ✓.

Top and bottom verified earlier. All good.

Now let me write the final file.

Let me reconsider the fractal noise normalization. Each octave valueNoise returns 0..1. Weighted sum / norm of amps returns 0..1. Good.

For column height, m and h are fractal values in [0,1]. H = floor(5 + m*m*58 + h*10). With m,h in [0,1], H in [5, 73]. Good.

Let me write the complete file now with all sections.

I need to be careful about one thing: requestPointerLock from document.documentElement. In some browsers need to be called in user gesture. The overlay click is a gesture. Good.

Also, I should prevent the default on the overlay click to avoid any weirdness — not necessary.

Let me also make sure clicking doesn't select text etc. Body overflow hidden.

Let me write it all now.

Let me reconsider: do I need to handle the case where the raycast hits a block that's part of a chunk without a mesh? No, raycast only against chunkMeshes which have geometry. Fine.

Also, I should make sure the outline box is slightly larger than 1 to avoid z-fitting with block faces. Use 1.01 or use EdgesGeometry. Let me use LineSegments with BoxGeometry(1.02) and basic material black, linewidth maybe. Actually LineBasicMaterial linewidth doesn't work well in WebGL (always 1). That's fine, thin line visible.

Alternatively use EdgesGeometry(BoxGeometry(1,1,1)) for crisp lines. Let me use that:
```
const outlineGeo = new THREE.BoxGeometry(1.01,1.01,1.01);
const outline = new THREE.LineSegments(outlineGeo, new THREE.LineBasicMaterial({color:0x000000}));
```

OK.

Let me finalize.

Let me also reconsider: should movement use dt clamped? Yes, dt = min(delta/1000, 0.1) maybe. Let me use 0.1 max to avoid tunneling.

Also gravity 25 and jump 8.5. With these, terminal velocity from falling could be high; collision per-axis with small dt should be fine.

Let me write the complete file.

Let me also double check: I need to include the block colors for hotbar slots. hotbarBlocks = [1,2,3,4,5,6,7]. Slot color = BASE_HEX. Let me store hex values for UI:
```
const BLOCK_COLORS = {1:0x4caf50,2:0x795548,3:0x9e9e9e,4:0xe7d9a8,5:0x8d6e63,6:0x2e7d32,7:0xffffff};
```

updateHotbar:
```
function updateHotbar(){
  const slots = document.querySelectorAll('.slot');
  slots.forEach((s,i)=>{
    s.style.borderColor = i===selectedSlot ? '#fff' : 'rgba(255,255,255,0.3)';
  });
}
```

Build hotbar HTML with 7 slots, each with color inline and number.

Let me generate hotbar slots in JS or HTML. Let me do in HTML statically with data-index.

Actually let me build them in JS for clarity. Or static HTML. Let me do static:
```
<div id="hotbar"></div>
```
and populate:
```
const hotbar = document.getElementById('hotbar');
hotbarBlocks.forEach((bid,i)=>{
  const s=document.createElement('div'); s.className='slot'; s.dataset.i=i;
  s.innerHTML = `<span class="num">${i+1}</span><span class="color" style="background:#${bid.toString(16).padStart(2,'0')}..."></span>`;
  ...
});
```

Hmm, hex formatting. Let me store hex strings. Let me define:
```
const BLOCK_HEX = {1:'4caf50',2:'795548',3:'9e9e9e',4:'e7d9a8',5:'8d6e63',6:'2e7d32',7:'ffffff'};
```

Then color = '#'+BLOCK_HEX[bid].

Let me finalize.

I think I've covered everything. Let me write the complete file now.

Let me write it out fully and carefully.

One more: the fog. THREE.Fog(0x87ceeb, 40, 110). renderer.setClearColor or scene.background = 0x87ceeb. Let me set scene.background = new THREE.Color(0x87ceeb) and scene.fog = new THREE.Fog(0x87ceeb, 40, 110).

Let me write.

Also, I want to make sure the game loop calls updateWorld every frame (it's cheap-ish, does generation/meshing/cleanup). Yes.

Let me also ensure I don't regenerate chunks that have data.

Alright, writing now.

Let me reconsider the meshing neighbor requirement and make sure spawn chunk gets meshed. Already covered above.

Let me write the complete HTML file.

I'll produce the final answer as a single ```code block containing the entire mc.html.

Let me write it all out.
</think>

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>mc.html</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; width: 100%; height: 100%; background: #000; font-family: sans-serif; }
  canvas { display: block; }
  #crosshair { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); pointer-events: none; z-index: 10; }
  #crosshair::before, #crosshair::after { content: ''; position: absolute; background: rgba(255,255,255,0.85); }
  #crosshair::before { left: 0; right: 0; top: 50%; height: 2px; margin-top: -1px; }
  #crosshair::after { top: 0; bottom: 0; left: 50%; width: 2px; margin-left: -1px; }
  #hotbar { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%); display: flex; gap: 4px; padding: 5px; background: rgba(0,0,0,0.55); border-radius: 4px; z-index: 10; }
  .slot { width: 44px; height: 44px; border: 2px solid rgba(255,255,255,0.35); border-radius: 3px; position: relative; display: flex; align-items: center; justify-content: center; }
  .slot.selected { border-color: #fff; }
  .slot .swatch { position: absolute; inset: 5px; border-radius: 2px; }
  .slot .num { position: absolute; top: 2px; left: 4px; color: #fff; font-size: 11px; line-height: 1; text-shadow: 1px 1px 1px #000; }
  #overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.75); display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; text-align: center; z-index: 20; cursor: pointer; }
  #overlay h1 { font-size: 48px; margin: 0 0 10px; letter-spacing: 4px; }
  #overlay ul { text-align: left; line-height: 1.8; font-size: 15px; opacity: 0.9; }
  #overlay .play { margin-top: 20px; font-size: 20px; border: 2px solid #fff; padding: 10px 24px; border-radius: 4px; }
  #overlay.hidden { display: none; }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MC</h1>
  <ul>
    <li><b>WASD</b> — move &nbsp; <b>Space</b> — jump</li>
    <li><b>Mouse</b> — look &nbsp; <b>Scroll / 1-7</b> — select block</li>
    <li><b>Left click</b> — break &nbsp; <b>Right click</b> — place</li>
  </ul>
  <div class="play">Click to play</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

/* ---------- Blocks ---------- */
const AIR=0, GRASS=1, DIRT=2, STONE=3, SAND=4, WOOD=5, LEAVES=6, SNOW=7;
const BLOCK_HEX = {1:'4caf50',2:'795548',3:'9e9e9e',4:'e7d9a8',5:'8d6e63',6:'2e7d32',7:'ffffff'};
const BLOCK_COLORS = [0,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
const BASE_RGB = {};
for (let i=1;i<=7;i++){ const h=BLOCK_COLORS[i]; BASE_RGB[i]=[((h>>16)&255)/255,((h>>8)&255)/255,(h&255)/255]; }
const HOTBAR_BLOCKS = [GRASS,DIRT,STONE,SAND,WOOD,LEAVES,SNOW];

/* ---------- Noise ---------- */
function hash2(x,y){
  let h = (x*1600130857 + y*1335313933 + 1013333311) | 0;
  h = Math.imul(h ^ (h >>> 13), 0x5bd1e9f5);
  h = h ^ (h >>> 15);
  return (h >>> 0) / 4294967296;
}
function hash3(x,y,z){
  let h = (x*1600130857 + y*1335313933 + z*1013333311 + 1013333311) | 0;
  h = Math.imul(h ^ (h >>> 13), 0x5bd1e9f5);
  h = h ^ (h >>> 15);
  return (h >>> 0) / 4294967296;
}
function fade(t){ return t*t*(3-2*t); }
function lerp(a,b,t){ return a+(b-a)*t; }
function valueNoise2D(x,y){
  const xi=Math.floor(x), yi=Math.floor(y);
  const xf=x-xi, yf=y-yi;
  const v00=hash2(xi,yi), v10=hash2(xi+1,yi), v01=hash2(xi,yi+1), v11=hash2(xi+1,yi+1);
  const u=fade(xf), v=fade(yf);
  const a=lerp(v00,v10,u), b=lerp(v01,v11,u);
  return lerp(a,b,v);
}
function fractalNoise2D(x,y){
  let amp=1, freq=1, sum=0, norm=0;
  for(let o=0;o<4;o++){ sum+=amp*valueNoise2D(x*freq,y*freq); norm+=amp; amp*=0.5; freq*=2; }
  return sum/norm;
}
function valueNoise3D(x,y,z){
  const xi=Math.floor(x), yi=Math.floor(y), zi=Math.floor(z);
  const xf=x-xi, yf=y-yi, zf=z-zi;
  const c000=hash3(xi,yi,zi),c100=hash3(xi+1,yi,zi),c010=hash3(xi,yi+1,zi),c110=hash3(xi+1,yi+1,zi);
  const c001=hash3(xi,yi,zi+1),c101=hash3(xi+1,yi,zi+1),c011=hash3(xi,yi+1,zi+1),c111=hash3(xi+1,yi+1,zi+1);
  const u=fade(xf),v=fade(yf),w=fade(zf);
  const i00=lerp(c000,c100,u), i10=lerp(c010,c110,u);
  const i01=lerp(c001,c101,u), i11=lerp(c011,c111,u);
  const j00=lerp(i00,i10,v), j10=lerp(i01,i11,v);
  return lerp(j00,j10,w);
}
function fractalNoise3D(x,y,z){
  let amp=1, freq=1, sum=0, norm=0;
  for(let o=0;o<4;o++){ sum+=amp*valueNoise3D(x*freq,y*freq,z*freq); norm+=amp; amp*=0.5; freq*=2; }
  return sum/norm;
}

/* ---------- Terrain helpers ---------- */
function columnHeight(wx,wz){
  const m = fractalNoise2D(wx*0.004, wz*0.004);
  const h = fractalNoise2D(wx*0.02,  wz*0.02);
  return Math.floor(5 + m*m*58 + h*10);
}
function surfaceMat(H){
  if(H>=46) return SNOW;
  if(H>=37) return STONE;
  if(H<=16) return SAND;
  return GRASS;
}
function subMat(H){
  if(H<=16) return SAND;
  if(H>=37) return STONE;
  return DIRT;
}

/* ---------- Chunk storage ---------- */
const CHUNK=16, HEIGHT=80;
const chunkData = new Map(); // key "cx,cz" -> { data:Uint8Array, mesh:null }
const chunkMeshes = [];

function chunkIndex(cx,cz){ return cx+","+cz; }
function idxOf(y,lx,lz){ return (y*CHUNK + lz)*CHUNK + lx; }

function getBlock(wx,wy,wz){
  if(wy<0 || wy>=HEIGHT) return AIR;
  const cx=Math.floor(wx/CHUNK), cz=Math.floor(wz/CHUNK);
  const key=chunkIndex(cx,cz);
  const ch=chunkData.get(key);
  if(!ch) return AIR;
  const lx=wx-cx*CHUNK, lz=wz-cz*CHUNK;
  if(lx<0||lx>=CHUNK||lz<0||lz>=CHUNK) return AIR;
  return ch.data[idxOf(wy,lx,lz)];
}
function setBlock(wx,wy,wz,id){
  if(wy<0||wy>=HEIGHT) return;
  const cx=Math.floor(wx/CHUNK), cz=Math.floor(wz/CHUNK);
  const key=chunkIndex(cx,cz);
  let ch=chunkData.get(key);
  if(!ch){ ch={data:new Uint8Array(CHUNK*HEIGHT*CHUNK), mesh:null}; chunkData.set(key,ch); }
  const lx=wx-cx*CHUNK, lz=wz-cz*CHUNK;
  ch.data[idxOf(wy,lx,lz)]=id;
}

/* ---------- Generation ---------- */
function generateChunk(cx,cz){
  const data=new Uint8Array(CHUNK*HEIGHT*CHUNK);
  for(let lz=0;lz<CHUNK;lz++){
    for(let lx=0;lx<CHUNK;lx++){
      const wx=cx*CHUNK+lx, wz=cz*CHUNK+lz;
      const H=columnHeight(wx,wz);
      for(let y=0;y<H;y++){
        let id;
        if(y===0) id=STONE;
        else if(y===H-1) id=surfaceMat(H);
        else if(y>=H-4) id=subMat(H);
        else id=STONE;
        if(y>=3 && y<=H-2){
          if(fractalNoise3D(wx*0.09, y*0.09, wz*0.09) > 0.67) continue;
        }
        data[idxOf(y,lx,lz)]=id;
      }
      // trees
      if(data[idxOf(H-1,lx,lz)]===GRASS && hash2(wx,wz)<0.02 && (H+7)<=HEIGHT){
        const sy=H-1;
        for(let t=0;t<4;t++) data[idxOf(sy+1+t,lx,lz)]=WOOD;
        for(let t=0;t<2;t++) placeLayer5x5(data,cx,cz,wx,wz,sy+5+t);
        placeLayer3x3(data,cx,cz,wx,wz,sy+7);
        data[idxOf(sy+8,lx,lz)]=LEAVES;
      }
    }
  }
  chunkData.set(chunkIndex(cx,cz), {data:data, mesh:null});
}
function placeLayer5x5(data,cx,cz,wx,wz,y){
  for(let dx=-2;dx<=2;dx++){
    for(let dz=-2;dz<=2;dz++){
      const nlx=(wx+dx)-cx*CHUNK, nlz=(wz+dz)-cz*CHUNK;
      if(nlx<0||lx>=CHUNK||nlz<0||nlz>=CHUNK) continue;
      if(nlx<0||nlx>=CHUNK||nlz<0||nlz>=CHUNK) continue;
      if(y>=HEIGHT) continue;
      if(data[idxOf(y,nlx,nlz)]===AIR) data[idxOf(y,nlx,nlz)]=LEAVES;
    }
  }
}
function placeLayer3x3(data,cx,cz,wx,wz,y){
  for(let dx=-1;dx<=1;dx++){
    for(let dz=-1;dz<=1;dz++){
      const nlx=(wx+dx)-cx*CHUNK, nlz=(wz+dz)-cz*CHUNK;
      if(nlx<0||nlx>=CHUNK||nlz<0||nlz>=CHUNK) continue;
      if(y>=HEIGHT) continue;
      if(data[idxOf(y,nlx,nlz)]===AIR) data[idxOf(y,nlx,nlz)]=LEAVES;
    }
  }
}

/* ---------- Meshing ---------- */
const FACES = [
  { nx:0,  ny:1, nz:0,  light:1.00, corners:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
  { nx:1,  ny:0, nz:0,  light:0.80, corners:[[1,1,0],[1,1,1],[1,0,1],[1,0,0]] },
  { nx:-1, ny:0, nz:0,  light:0.80, corners:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
  { nx:0,  ny:0, nz:1,  light:0.80, corners:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]] },
  { nx:0,  ny:0, nz:-1, light:0.80, corners:[[0,1,0],[1,1,0],[1,0,0],[0,0,0]] },
  { nx:0,  ny:-1, nz:0, light:0.55, corners:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
];
function buildChunkMesh(cx,cz,data){
  const pos=[], nor=[], col=[];
  for(let ly=0;ly<HEIGHT;ly++){
    for(let lz=0;lz<CHUNK;lz++){
      for(let lx=0;lx<CHUNK;lx++){
        const id=data[idxOf(ly,lx,lz)];
        if(id===AIR) continue;
        const wx=cx*CHUNK+lx, wz=cz*CHUNK+lz;
        for(let f=0;f<6;f++){
          const face=FACES[f];
          const nx=wx+face.nx, ny=ly+face.ny, nz=wz+face.nz;
          if(getBlock(nx,ny,nz)===AIR){
            const base=BASE_RGB[id];
            const L=face.light;
            for(let v=0;v<4;v++){
              const c=face.corners[v];
              pos.push(wx+c[0], ly+c[1], wz+c[2]);
              nor.push(face.nx, face.ny, face.nz);
              col.push(base[0]*L, base[1]*L, base[2]*L);
            }
          }
        }
      }
    }
  }
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(nor,3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  const mesh=new THREE.Mesh(geo, blockMaterial);
  return mesh;
}
function rebuildChunk(cx,cz){
  const key=chunkIndex(cx,cz);
  const ch=chunkData.get(key);
  if(!ch) return;
  if(ch.mesh){
    const i=chunkMeshes.indexOf(ch.mesh); if(i>=0) chunkMeshes.splice(i,1);
    scene.remove(ch.mesh);
    ch.mesh.geometry.dispose();
  }
  const mesh=buildChunkMesh(cx,cz,ch.data);
  scene.add(mesh);
  chunkMeshes.push(mesh);
  ch.mesh=mesh;
}
function rebuildAt(x,y,z){
  const cx=Math.floor(x/CHUNK), cz=Math.floor(z/CHUNK);
  rebuildChunk(cx,cz);
  const lx=x-cx*CHUNK, lz=z-cz*CHUNK;
  if(lx===0) rebuildChunk(cx-1,cz);
  if(lx===CHUNK-1) rebuildChunk(cx+1,cz);
  if(lz===0) rebuildChunk(cx,cz-1);
  if(lz===CHUNK-1) rebuildChunk(cx,cz+1);
}

/* ---------- Scene ---------- */
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 400);

const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors:true });
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(0.3,1,0.5).normalize();
scene.add(dir);

/* Clouds */
const clouds=[];
for(let i=0;i<25;i++){
  const size=24+(i%5)*10;
  const geo=new THREE.BoxGeometry(size, 8, size*0.7);
  const mat=new THREE.MeshLambertMaterial({ color:0xffffff, transparent:true, opacity:0.85 });
  const m=new THREE.Mesh(geo,mat);
  const ang=i*137.5*Math.PI/180;
  const rad=150+i*7;
  m.userData={ rx:Math.cos(ang)*rad, rz:Math.sin(ang)*rad, speed:5+(i%3)*2 };
  scene.add(m); clouds.push(m);
}

/* Water */
const waterGeo=new THREE.PlaneGeometry(2000,2000);
const waterMat=new THREE.MeshLambertMaterial({ color:0x3fa3e0, transparent:true, opacity:0.7, side:THREE.DoubleSide });
const water=new THREE.Mesh(waterGeo,waterMat);
water.rotation.x=-Math.PI/2;
water.position.y=14.3;
scene.add(water);

/* Outline */
const outlineGeo=new THREE.BoxGeometry(1.02,1.02,1.02);
const outlineMat=new THREE.LineBasicMaterial({ color:0x000000 });
const outline=new THREE.LineSegments(outlineGeo,outlineMat);
outline.visible=false;
scene.add(outline);

/* ---------- Player ---------- */
let px=8, py=0, pz=8, dy=0, yaw=0, pitch=0, onGround=false;
const spawnH = columnHeight(8,8);
py = spawnH + 2;
const spawnY = py;

/* ---------- Input ---------- */
const keys={};
window.addEventListener('keydown', e=>{
  keys[e.code]=true;
  const n=parseInt(e.key);
  if(!isNaN(n) && n>=1 && n<=7){ selectedSlot=n-1; updateHotbar(); }
});
window.addEventListener('keyup', e=>{ keys[e.code]=false; });

/* ---------- Break / place state ---------- */
let bt=null, placeCell=null;
const raycaster = new THREE.Raycaster();
const camPos = new THREE.Vector3();
const fwd = new THREE.Vector3();

function updateTarget(){
  camPos.copy(camera.position);
  camera.getWorldDirection(fwd);
  raycaster.set(camPos, fwd, 0.01, 6);
  const hits=raycaster.intersectObjects(chunkMeshes, false);
  if(hits.length>0){
    const h=hits[0], p=h.point, n=h.face.normal;
    bt=[Math.floor(p.x-n.x*0.5), Math.floor(p.y-n.y*0.5), Math.floor(p.z-n.z*0.5)];
    placeCell=[Math.floor(p.x+n.x*0.5), Math.floor(p.y+n.y*0.5), Math.floor(p.z+n.z*0.5)];
    outline.position.set(bt[0]+0.5, bt[1]+0.5, bt[2]+0.5);
    outline.visible=true;
  } else {
    bt=null; placeCell=null;
    outline.visible=false;
  }
}

function collides(x,y,z){
  const minX=x-0.3, maxX=x+0.3;
  const minY=y, maxY=y+1.8;
  const minZ=z-0.3, maxZ=z+0.3;
  const bx0=Math.floor(minX), bx1=Math.floor(maxX);
  const by0=Math.floor(minY), by1=Math.floor(maxY);
  const bz0=Math.floor(minZ), bz1=Math.floor(maxZ);
  for(let bx=bx0;bx<=bx1;bx++)
  for(let by=by0;by<=by1;by++)
  for(let bz=bz0;bz<=bz1;bz++){
    if(getBlock(bx,by,bz)!==AIR) return true;
  }
  return false;
}
function playerOverlaps(bx,by,bz){
  const minX=px-0.3, maxX=px+0.3;
  const minY=py, maxY=py+1.8;
  const minZ=pz-0.3, maxZ=pz+0.3;
  return !(bx+1<=minX || bx>=maxX || by+1<=minY || by>=maxY || bz+1<=minZ || bz>=maxZ);
}

/* ---------- World update ---------- */
function updateWorld(){
  const pcx=Math.floor(px/CHUNK), pcz=Math.floor(pz/CHUNK);
  // generate (nearest first, max 4/frame)
  const gens=[];
  for(let dz=-5;dz<=5;dz++) for(let dx=-5;dx<=5;dx++){
    gens.push({cx:pcx+dx, cz:pcz+dz, d:Math.abs(dx)+Math.abs(dz)});
  }
  gens.sort((a,b)=>a.d-b.d);
  let gc=0;
  for(const c of gens){
    if(gc>=4) break;
    if(!chunkData.has(chunkIndex(c.cx,c.cz))){ generateChunk(c.cx,c.cz); gc++; }
  }
  // mesh (nearest first, max 2/frame)
  const mes=[];
  for(let dz=-4;dz<=4;dz++) for(let dx=-4;dx<=4;dx++){
    mes.push({cx:pcx+dx, cz:pcz+dz, d:Math.abs(dx)+Math.abs(dz)});
  }
  mes.sort((a,b)=>a.d-b.d);
  let mc=0;
  for(const c of mes){
    if(mc>=2) break;
    const ch=chunkData.get(chunkIndex(c.cx,c.cz));
    if(ch && !ch.mesh){
      if(chunkData.has(chunkIndex(c.cx-1,c.cz)) && chunkData.has(chunkIndex(c.cx+1,c.cz)) &&
         chunkData.has(chunkIndex(c.cx,c.cz-1)) && chunkData.has(chunkIndex(c.cx,c.cz+1))){
        rebuildChunk(c.cx,c.cz); mc++;
      }
    }
  }
  // cleanup far chunks
  for(const [key,ch] of chunkData){
    const parts=key.split(','); const cx=+parts[0], cz=+parts[1];
    if(Math.max(Math.abs(cx-pcx), Math.abs(cz-pcz))>7){
      if(ch.mesh){ scene.remove(ch.mesh); ch.mesh.geometry.dispose(); }
      const i=chunkMeshes.indexOf(ch.mesh); if(i>=0) chunkMeshes.splice(i,1);
      chunkData.delete(key);
    }
  }
}

/* ---------- Hotbar UI ---------- */
let selectedSlot=0;
const hotbarEl=document.getElementById('hotbar');
HOTBAR_BLOCKS.forEach((bid,i)=>{
  const s=document.createElement('div');
  s.className='slot'; s.dataset.i=i;
  s.innerHTML='<span class="num">'+(i+1)+'</span><span class="swatch" style="background:#'+BLOCK_HEX[bid]+'"></span>';
  hotbarEl.appendChild(s);
});
function updateHotbar(){
  const slots=hotbarEl.querySelectorAll('.slot');
  slots.forEach((s,i)=>{ s.classList.toggle('selected', i===selectedSlot); });
}
updateHotbar();
window.addEventListener('wheel', e=>{
  if(!document.pointerLockElement) return;
  selectedSlot=(selectedSlot + (e.deltaY>0?1:-1) + 7) % 7;
  updateHotbar();
}, {pass:true});

/* ---------- Pointer lock & clicks ---------- */
const overlay=document.getElementById('overlay');
overlay.addEventListener('click', ()=>{
  overlay.classList.add('hidden');
  document.documentElement.requestPointerLock();
});
document.addEventListener('pointerlockchange', ()=>{
  if(!document.pointerLockElement) overlay.classList.remove('hidden');
});
document.addEventListener('mousemove', e=>{
  if(!document.pointerLockElement) return;
  yaw -= e.movementX*0.002;
  pitch -= e.movementY*0.002;
  pitch=Math.max(-1.5708+1e-4, Math.min(1.5708-1e-4, pitch));
});
document.addEventListener('mousedown', e=>{
  if(!document.pointerLockElement) return;
  if(e.button===0){
    if(outline.visible && bt && bt[1]!==0){
      setBlock(bt[0],bt[1],bt[2],AIR);
      rebuildAt(bt[0],bt[1],bt[2]);
    }
  } else if(e.button===2){
    if(outline.visible && placeCell){
      const pc=placeCell;
      if(getBlock(pc[0],pc[1],pc[2])===AIR && !playerOverlaps(pc[0],pc[1],pc[2])){
        setBlock(pc[0],pc[1],pc[2], HOTBAR_BLOCKS[selectedSlot]);
        rebuildAt(pc[0],pc[1],pc[2]);
      }
    }
  }
});
document.addEventListener('contextmenu', e=>e.preventDefault());

/* ---------- Resize ---------- */
window.addEventListener('resize', ()=>{
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ---------- Loop ---------- */
let last=performance.now();
function animate(){
  requestAnimationFrame(animate);
  const now=performance.now();
  let dt=(now-last)/1000; last=now;
  if(dt>0.25) dt=0.25; if(dt<=0) dt=1/60;

  // movement
  const sinY=Math.sin(yaw), cosY=Math.cos(yaw);
  let mx=0, mz=0;
  if(keys['KeyW']){ mx-=sinY; mz-=cosY; }
  if(keys['KeyS']){ mx+=sinY; mz+=cosY; }
  if(keys['KeyD']){ mx+=cosY; mz-=sinY; }
  if(keys['KeyA']){ mx-=cosY; mz+=sinY; }
  const len=Math.hypot(mx,mz);
  if(len>0){ mx/=len; mz/=len; }
  const speed=5.5;
  dy -= 25*dt;
  if(keys['Space'] && onGround){ dy=8.5; onGround=false; }

  let nx=px+mx*speed*dt; if(!collides(nx,py,pz)) px=nx;
  let nz=pz+mz*speed*dt; if(!collides(px,py,nz)) pz=nz;
  let ny=py+dy*dt;
  if(!collides(px,ny,pz)){ py=ny; onGround=false; }
  else { if(dy<0) onGround=true; dy=0; }

  if(py<-20){ py=spawnY; px=8; pz=8; dy=0; }

  camera.position.set(px, py+1.62, pz);
  camera.quaternion.setFromEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ'));

  updateWorld();
  updateTarget();

  // clouds
  for(const c of clouds){
    c.position.x = px + c.userData.rx;
    c.position.z = pz + c.userData.rz;
    c.position.y = 90;
    c.userData.rx += c.userData.speed*dt;
    if(c.userData.rx>300) c.userData.rx-=600;
    if(c.userData.rx<-300) c.userData.rx+=600;
  }
  water.position.x=px; water.position.z=pz;

  renderer.render(scene, camera);
}
animate();

})();
</script>
</body>
</html>
```