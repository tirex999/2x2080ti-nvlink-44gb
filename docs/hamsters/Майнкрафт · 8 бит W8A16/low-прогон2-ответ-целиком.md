

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Minecraft Clone</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; width: 100vw; height: 100vh; }
canvas { display: block; }
#overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7); display: flex; flex-direction: column;
    align-items: center; justify-content: center; z-index: 100;
    color: #fff; font-family: monospace; cursor: pointer;
}
#overlay h1 { font-size: 48px; margin-bottom: 20px; text-shadow: 2px 2px 4px #000; }
#overlay .controls { font-size: 16px; line-height: 1.8; text-align: center; margin-bottom: 20px; }
#overlay .play { font-size: 24px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
#crosshair {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    z-index: 50; pointer-events: none;
}
#crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: rgba(255,255,255,0.8);
}
#crosshair::before { width: 2px; height: 16px; left: -1px; top: -8px; }
#crosshair::after { width: 16px; height: 2px; left: -8px; top: -1px; }
#hotbar {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 2px; background: rgba(0,0,0,0.5);
    padding: 4px; border-radius: 4px; z-index: 50;
}
.slot {
    width: 48px; height: 48px; border: 2px solid #555;
    display: flex; align-items: center; justify-content: center;
    font-family: monospace; font-size: 12px; color: #fff;
    position: relative;
}
.slot.selected { border-color: #fff; border-width: 3px; }
.slot .color {
    width: 32px; height: 32px; position: absolute; top: 4px; left: 4px;
}
.slot .num {
    position: relative; z-index: 1; text-shadow: 1px 1px 2px #000;
    font-size: 11px;
}
</style>
</head>
<body>
<div id="overlay">
    <h1>MC Clone</h1>
    <div class="controls">
        WASD - Move<br>
        Mouse - Look<br>
        Left Click - Break<br>
        Right Click - Place<br>
        Space - Jump<br>
        1-7 / Scroll - Select Block
    </div>
    <div class="play">Click to Play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
'use strict';

const CS = 16, CH = 80;
const BLOCK_COLORS = [
    0x000000,
    0x4caf50, // 1 grass
    0x795548, // 2 dirt
    0x9e9e9e, // 3 stone
    0xe7d9a8, // 4 sand
    0x8d6e63, // 5 wood
    0x2e7d32, // 6 leaves
    0xffffff  // 7 snow
];
const HOTBAR_BLOCKS = [1,2,3,4,5,6,7];

// --- Noise ---
function hash2(x, y) {
    let n = (x * 374761393 + y * 668265263) | 0;
    n = ((n ^ (n >>> 13)) * 1274126177) | 0;
    n = (n ^ (n >>> 16)) | 0;
    return (n & 0x7fffffff) / 0x7fffffff;
}
function hash3(x, y, z) {
    let n = (x * 374761393 + y * 668265263 + z * 1274126177) | 0;
    n = ((n ^ (n >>> 13)) * 1274126177) | 0;
    n = (n ^ (n >>> 16)) | 0;
    return (n & 0x7fffffff) / 0x7fffffff;
}
function smoothstep(t) { return t * t * (3 - 2 * t); }
function noise2(x, y) {
    const xi = Math.floor(x), yi = Math.floor(y);
    const xf = x - xi, yf = y - yi;
    const u = smoothstep(xf), v = smoothstep(yf);
    const a = hash2(xi, yi), b = hash2(xi+1, yi);
    const c = hash2(xi, yi+1), d = hash2(xi+1, yi+1);
    return a*(1-u)*(1-v) + b*u*(1-v) + c*(1-u)*v + d*u*v;
}
function noise3(x, y, z) {
    const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    const xf = x - xi, yf = y - yi, zf = z - zi;
    const u = smoothstep(xf), v = smoothstep(yf), w = smoothstep(zf);
    const c000 = hash3(xi,yi,zi), c100 = hash3(xi+1,yi,zi);
    const c010 = hash3(xi,yi+1,zi), c110 = hash3(xi+1,yi+1,zi);
    const c001 = hash3(xi,yi,zi+1), c101 = hash3(xi+1,yi,zi+1);
    const c011 = hash3(xi,yi+1,zi+1), c111 = hash3(xi+1,yi+1,zi+1);
    const x00 = c000*(1-u)+c100*u, x10 = c010*(1-u)+c110*u;
    const x01 = c001*(1-u)+c101*u, x11 = c011*(1-u)+c111*u;
    const y0 = x00*(1-v)+x10*v, y1 = x01*(1-v)+x11*v;
    return y0*(1-w)+y1*w;
}
function fractal2(x, y) {
    let val = 0, amp = 1, freq = 1, total = 0;
    for (let i = 0; i < 4; i++) {
        val += noise2(x*freq, y*freq) * amp;
        total += amp; amp *= 0.5; freq *= 2;
    }
    return val / total;
}
function fractal3(x, y, z) {
    let val = 0, amp = 1, freq = 1, total = 0;
    for (let i = 0; i < 4; i++) {
        val += noise3(x*freq, y*freq, z*freq) * amp;
        total += amp; amp *= 0.5; freq *= 2;
    }
    return val / total;
}

// --- Chunk System ---
const chunks = new Map();
const chunkMeshes = [];

function chunkKey(cx, cz) { return cx + ',' + cz; }

function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= CH) return 0;
    const cx = Math.floor(wx / CS), cz = Math.floor(wz / CS);
    const chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return 0;
    const lx = wx - cx * CS, lz = wz - cz * CS;
    return chunk.data[lx + CS * lz + CS * CS * wy];
}

function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= CH) return;
    const cx = Math.floor(wx / CS), cz = Math.floor(wz / CS);
    const chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return;
    const lx = wx - cx * CS, lz = wz - cz * CS;
    chunk.data[lx + CS * lz + CS * CS * wy] = id;
}

function generateChunkData(cx, cz) {
    const data = new Uint8Array(CS * CS * CH);
    const heights = new Int16Array(CS * CS);

    for (let lx = 0; lx < CS; lx++) {
        for (let lz = 0; lz < CS; lz++) {
            const wx = cx * CS + lx, wz = cz * CS + lz;
            const m = fractal2(wx * 0.004, wz * 0.004);
            const h = fractal2(wx * 0.02, wz * 0.02);
            const H = Math.floor(5 + m * m * 58 + h * 10);
            heights[lx + CS * lz] = H;

            let surface, sub;
            if (H >= 46) { surface = 7; sub = 3; }
            else if (H >= 37) { surface = 3; sub = 3; }
            else if (H <= 16) { surface = 4; sub = 4; }
            else { surface = 1; sub = 2; }

            for (let y = 0; y < CH; y++) {
                let b;
                if (y > H) b = 0;
                else if (y === 0) b = 3;
                else if (y === H) b = surface;
                else if (y >= H - 2) b = sub;
                else b = 3;

                if (b !== 0 && y >= 3 && y < H) {
                    if (fractal3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) b = 0;
                }
                data[lx + CS * lz + CS * CS * y] = b;
            }
        }
    }

    // Trees
    for (let lx = 2; lx < CS - 2; lx++) {
        for (let lz = 2; lz < CS - 2; lz++) {
            const wx = cx * CS + lx, wz = cz * CS + lz;
            let sy = -1;
            for (let y = CH - 1; y >= 0; y--) {
                if (data[lx + CS * lz + CS * CS * y] !== 0) { sy = y; break; }
            }
            if (sy < 0) continue;
            if (data[lx + CS * lz + CS * CS * sy] !== 1) continue;
            if (sy + 7 >= CH) continue;
            if (hash2(wx, wz) >= 0.02) continue;

            // Trunk
            for (let ty = 1; ty <= 4; ty++) {
                const idx = lx + CS * lz + CS * CS * (sy + ty);
                if (data[idx] === 0) data[idx] = 5;
            }
            // 5x5 at sy+3
            for (let dx = -2; dx <= 2; dx++)
                for (let dz = -2; dz <= 2; dz++) {
                    const idx = (lx+dx) + CS*(lz+dz) + CS*CS*(sy+3);
                    if (data[idx] === 0) data[idx] = 6;
                }
            // 5x5 at sy+4
            for (let dx = -2; dx <= 2; dx++)
                for (let dz = -2; dz <= 2; dz++) {
                    const idx = (lx+dx) + CS*(lz+dz) + CS*CS*(sy+4);
                    if (data[idx] === 0) data[idx] = 6;
                }
            // 3x3 at sy+5
            for (let dx = -1; dx <= 1; dx++)
                for (let dz = -1; dz <= 1; dz++) {
                    const idx = (lx+dx) + CS*(lz+dz) + CS*CS*(sy+5);
                    if (data[idx] === 0) data[idx] = 6;
                }
            // 1 at sy+6
            {
                const idx = lx + CS*lz + CS*CS*(sy+6);
                if (data[idx] === 0) data[idx] = 6;
            }
        }
    }
    return data;
}

// --- Meshing ---
const mat = new THREE.MeshLambertMaterial({ vertexColors: true });

function buildChunkMesh(cx, cz) {
    const chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return;
    if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        const idx = chunkMeshes.indexOf(chunk.mesh);
        if (idx !== -1) chunkMeshes.splice(idx, 1);
        chunk.mesh = null;
    }

    const positions = [], normals = [], colors = [];
    const wx0 = cx * CS, wz0 = cz * CS;

    for (let lx = 0; lx < CS; lx++) {
        for (let lz = 0; lz < CS; lz++) {
            for (let y = 0; y < CH; y++) {
                const id = chunk.data[lx + CS * lz + CS * CS * y];
                if (id === 0) continue;
                const wx = wx0 + lx, wz = wz0 + lz;
                const r = ((BLOCK_COLORS[id] >> 16) & 255) / 255;
                const g = ((BLOCK_COLORS[id] >> 8) & 255) / 255;
                const b = (BLOCK_COLORS[id] & 255) / 255;

                // Top +y
                if (getBlock(wx, y+1, wz) === 0) {
                    addFace(positions, normals, colors,
                        wx, y+1, wz, wx, y+1, wz+1, wx+1, y+1, wz+1, wx+1, y+1, wz,
                        0, 1, 0, r, g, b, 1.0);
                }
                // Bottom -y
                if (getBlock(wx, y-1, wz) === 0) {
                    addFace(positions, normals, colors,
                        wx, y, wz, wx+1, y, wz, wx+1, y, wz+1, wx, y, wz+1,
                        0, -1, 0, r, g, b, 0.55);
                }
                // Front +z
                if (getBlock(wx, y, wz+1) === 0) {
                    addFace(positions, normals, colors,
                        wx, y, wz+1, wx+1, y, wz+1, wx+1, y+1, wz+1, wx, y+1, wz+1,
                        0, 0, 1, r, g, b, 0.8);
                }
                // Back -z
                if (getBlock(wx, y, wz-1) === 0) {
                    addFace(positions, normals, colors,
                        wx+1, y, wz, wx, y, wz, wx, y+1, wz, wx+1, y+1, wz,
                        0, 0, -1, r, g, b, 0.8);
                }
                // Right +x
                if (getBlock(wx+1, y, wz) === 0) {
                    addFace(positions, normals, colors,
                        wx+1, y, wz+1, wx+1, y, wz, wx+1, y+1, wz, wx+1, y+1, wz+1,
                        1, 0, 0, r, g, b, 0.8);
                }
                // Left -x
                if (getBlock(wx-1, y, wz) === 0) {
                    addFace(positions, normals, colors,
                        wx, y, wz, wx, y, wz+1, wx, y+1, wz+1, wx, y+1, wz,
                        -1, 0, 0, r, g, b, 0.8);
                }
            }
        }
    }

    if (positions.length === 0) { chunk.mesh = null; return; }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(0, 0, 0);
    scene.add(mesh);
    chunkMeshes.push(mesh);
    chunk.mesh = mesh;
}

function addFace(pos, nor, col,
    x1,y1,z1, x2,y2,z2, x3,y3,z3, x4,y4,z4,
    nx,ny,nz, r,g,b, light) {
    const cr = r * light, cg = g * light, cb = b * light;
    pos.push(x1,y1,z1, x2,y2,z2, x3,y3,z3, x1,y1,z1, x3,y3,z3, x4,y4,z4);
    for (let i = 0; i < 6; i++) nor.push(nx, ny, nz);
    for (let i = 0; i < 6; i++) col.push(cr, cg, cb);
}

function rebuildChunk(cx, cz) {
    const key = chunkKey(cx, cz);
    if (!chunks.has(key)) return;
    buildChunkMesh(cx, cz);
}

// --- Scene Setup ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: false });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(1, 2, 0.5);
scene.add(dirLight);

// Clouds
const clouds = [];
const cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 });
for (let i = 0; i < 25; i++) {
    const w = 8 + hash2(i, 77) * 12;
    const d = 6 + hash2(i, 88) * 10;
    const geo = new THREE.BoxGeometry(w, 1, d);
    const cloud = new THREE.Mesh(geo, cloudMat);
    cloud.position.set(
        (hash2(i, 11) - 0.5) * 200,
        88 + hash2(i, 22) * 10,
        (hash2(i, 33) - 0.5) * 200
    );
    scene.add(cloud);
    clouds.push(cloud);
}

// Water
const waterGeo = new THREE.PlaneGeometry(512, 512);
waterGeo.rotateX(-Math.PI / 2);
const waterMat = new THREE.MeshLambertMaterial({ color: 0x3388cc, transparent: true, opacity: 0.6 });
const waterPlane = new THREE.Mesh(waterGeo, waterMat);
waterPlane.position.y = 14.3;
scene.add(waterPlane);

// Outline
const outlineGeo = new THREE.BoxGeometry(1.005, 1.005, 1.005);
const outlineEdges = new THREE.EdgesGeometry(outlineGeo);
const outlineLine = new THREE.LineSegments(outlineEdges, new THREE.LineBasicMaterial({ color: 0x000000 }));
outlineLine.visible = false;
scene.add(outlineLine);

// --- Player ---
let yaw = 0, pitch = 0;
let playerPos = { x: 8, y: 50, z: 8 };
let velY = 0;
let onGround = false;
const SPAWN = { x: 8, y: 50, z: 8 };

function findSpawnY() {
    for (let y = CH - 1; y >= 0; y--) {
        if (getBlock(SPAWN.x, y, SPAWN.z) !== 0) return y + 1;
    }
    return 20;
}

// --- Input ---
const keys = {};
let pointerLocked = false;
let selectedSlot = 0;

document.addEventListener('keydown', e => { keys[e.code] = true; });
document.addEventListener('keyup', e => { keys[e.code] = false; });
document.addEventListener('contextmenu', e => e.preventDefault());

const overlay = document.getElementById('overlay');
overlay.addEventListener('click', () => {
    renderer.domElement.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
    pointerLocked = (document.pointerLockElement === renderer.domElement);
    overlay.style.display = pointerLocked ? 'none' : 'flex';
});
document.addEventListener('mousemove', e => {
    if (!pointerLocked) return;
    yaw -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;
    pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, pitch));
});

document.addEventListener('mousedown', e => {
    if (!pointerLocked) return;
    if (e.button === 0) breakBlock();
    else if (e.button === 2) placeBlock();
});

document.addEventListener('wheel', e => {
    if (!pointerLocked) return;
    if (e.deltaY > 0) selectedSlot = (selectedSlot + 1) % 7;
    else selectedSlot = (selectedSlot + 6) % 7;
    updateHotbar();
});

document.addEventListener('keydown', e => {
    if (e.code >= 'Digit1' && e.code <= 'Digit7') {
        selectedSlot = parseInt(e.code.charAt(5)) - 1;
        updateHotbar();
    }
});

// --- Hotbar UI ---
const hotbarEl = document.getElementById('hotbar');
function buildHotbar() {
    hotbarEl.innerHTML = '';
    for (let i = 0; i < 7; i++) {
        const slot = document.createElement('div');
        slot.className = 'slot' + (i === selectedSlot ? ' selected' : '');
        const colorDiv = document.createElement('div');
        colorDiv.className = 'color';
        colorDiv.style.background = '#' + BLOCK_COLORS[HOTBAR_BLOCKS[i]].toString(16).padStart(6, '0');
        slot.appendChild(colorDiv);
        const numSpan = document.createElement('span');
        numSpan.className = 'num';
        numSpan.textContent = i + 1;
        slot.appendChild(numSpan);
        hotbarEl.appendChild(slot);
    }
}
function updateHotbar() {
    const slots = hotbarEl.children;
    for (let i = 0; i < 7; i++) {
        slots[i].className = 'slot' + (i === selectedSlot ? ' selected' : '');
    }
}
buildHotbar();

// --- Raycasting ---
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
const centerVec = new THREE.Vector2(0, 0);

function getTarget() {
    raycaster.setFromCamera(centerVec, camera);
    const hits = raycaster.intersectObjects(chunkMeshes);
    if (hits.length === 0) return null;
    const hit = hits[0];
    const n = hit.face.normal;
    const p = hit.point;
    return {
        bx: Math.floor(p.x - n.x * 0.5),
        by: Math.floor(p.y - n.y * 0.5),
        bz: Math.floor(p.z - n.z * 0.5),
        px: Math.floor(p.x + n.x * 0.5),
        py: Math.floor(p.y + n.y * 0.5),
        pz: Math.floor(p.z + n.z * 0.5)
    };
}

function breakBlock() {
    const t = getTarget();
    if (!t) return;
    if (t.by <= 0) return;
    setBlock(t.bx, t.by, t.bz, 0);
    const cx = Math.floor(t.bx / CS), cz = Math.floor(t.bz / CS);
    rebuildChunk(cx, cz);
    const lx = t.bx - cx * CS, lz = t.bz - cz * CS;
    if (lx === 0) rebuildChunk(cx - 1, cz);
    if (lx === CS - 1) rebuildChunk(cx + 1, cz);
    if (lz === 0) rebuildChunk(cx, cz - 1);
    if (lz === CS - 1) rebuildChunk(cx, cz + 1);
}

function placeBlock() {
    const t = getTarget();
    if (!t) return;
    if (getBlock(t.px, t.py, t.pz) !== 0) return;
    // Check overlap with player
    const px = playerPos.x, py = playerPos.y, pz = playerPos.z;
    const hw = 0.3, hh = 1.8;
    if (t.px + 1 > px - hw && t.px < px + hw &&
        t.py + 1 > py && t.py < py + hh &&
        t.pz + 1 > pz - hw && t.pz < pz + hw) return;
    setBlock(t.px, t.py, t.pz, HOTBAR_BLOCKS[selectedSlot]);
    const cx = Math.floor(t.px / CS), cz = Math.floor(t.pz / CS);
    rebuildChunk(cx, cz);
    const lx = t.px - cx * CS, lz = t.pz - cz * CS;
    if (lx === 0) rebuildChunk(cx - 1, cz);
    if (lx === CS - 1) rebuildChunk(cx + 1, cz);
    if (lz === 0) rebuildChunk(cx, cz - 1);
    if (lz === CS - 1) rebuildChunk(cx, cz + 1);
}

// --- Collision ---
function collides(px, py, pz) {
    const hw = 0.3, hh = 1.8;
    const minX = Math.floor(px - hw), maxX = Math.floor(px + hw);
    const minY = Math.floor(py), maxY = Math.floor(py + hh);
    const minZ = Math.floor(pz - hw), maxZ = Math.floor(pz + hw);
    for (let x = minX; x <= maxX; x++)
        for (let y = minY; y <= maxY; y++)
            for (let z = minZ; z <= maxZ; z++)
                if (getBlock(x, y, z) !== 0) return true;
    return false;
}

function moveAxis(axis, amount) {
    if (amount === 0) return;
    if (axis === 'x') playerPos.x += amount;
    else if (axis === 'y') playerPos.y += amount;
    else playerPos.z += amount;

    if (collides(playerPos.x, playerPos.y, playerPos.z)) {
        if (axis === 'x') playerPos.x -= amount;
        else if (axis === 'y') {
            playerPos.y -= amount;
            if (amount < 0) onGround = true;
            velY = 0;
        }
        else playerPos.z -= amount;
    }
}

// --- Chunk Management ---
function updateChunks() {
    const pcx = Math.floor(playerPos.x / CS);
    const pcz = Math.floor(playerPos.z / CS);

    // Generate data for chunks within radius 5 (max 4 per frame)
    let genCount = 0;
    for (let dx = -5; dx <= 5 && genCount < 4; dx++) {
        for (let dz = -5; dz <= 5 && genCount < 4; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = chunkKey(cx, cz);
            if (!chunks.has(key)) {
                chunks.set(key, { data: generateChunkData(cx, cz), mesh: null });
                genCount++;
            }
        }
    }

    // Build meshes for chunks within radius 4 that have all 4 neighbors (max 2 per frame)
    let meshCount = 0;
    for (let dx = -4; dx <= 4 && meshCount < 2; dx++) {
        for (let dz = -4; dz <= 4 && meshCount < 2; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = chunkKey(cx, cz);
            const chunk = chunks.get(key);
            if (!chunk || chunk.mesh) continue;
            // Check 4 neighbors have data
            if (!chunks.has(chunkKey(cx-1, cz))) continue;
            if (!chunks.has(chunkKey(cx+1, cz))) continue;
            if (!chunks.has(chunkKey(cx, cz-1))) continue;
            if (!chunks.has(chunkKey(cx, cz+1))) continue;
            buildChunkMesh(cx, cz);
            meshCount++;
        }
    }

    // Remove chunks beyond radius 7
    const toRemove = [];
    for (const [key, chunk] of chunks) {
        const parts = key.split(',');
        const cx = parseInt(parts[0]), cz = parseInt(parts[1]);
        const dist = Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz));
        if (dist > 7) toRemove.push(key);
    }
    for (const key of toRemove) {
        const chunk = chunks.get(key);
        if (chunk.mesh) {
            scene.remove(chunk.mesh);
            chunk.mesh.geometry.dispose();
            const idx = chunkMeshes.indexOf(chunk.mesh);
            if (idx !== -1) chunkMeshes.splice(idx, 1);
        }
        chunks.delete(key);
    }
}

// --- Update Loop ---
const clock = new THREE.Clock();

function updatePlayer(dt) {
    // Movement
    let mx = 0, mz = 0;
    if (keys['KeyW']) { mx += -Math.sin(yaw); mz += -Math.cos(yaw); }
    if (keys['KeyS']) { mx += Math.sin(yaw); mz += Math.cos(yaw); }
    if (keys['KeyA']) { mx += -Math.cos(yaw); mz += Math.sin(yaw); }
    if (keys['KeyD']) { mx += Math.cos(yaw); mz += -Math.sin(yaw); }
    const len = Math.sqrt(mx * mx + mz * mz);
    if (len > 0) { mx /= len; mz /= len; }
    const speed = 5.5 * dt;
    moveAxis('x', mx * speed);
    moveAxis('z', mz * speed);

    // Gravity & jump
    velY -= 25 * dt;
    if (velY < -30) velY = -30;
    if (keys['Space'] && onGround) {
        velY = 8.5;
        onGround = false;
    }
    onGround = false;
    moveAxis('y', velY * dt);

    // Fall below -20
    if (playerPos.y < -20) {
        playerPos.x = SPAWN.x;
        playerPos.y = findSpawnY();
        playerPos.z = SPAWN.z;
        velY = 0;
    }

    // Update camera
    camera.position.set(playerPos.x, playerPos.y + 1.62, playerPos.z);
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
}

function updateClouds(dt) {
    for (const cloud of clouds) {
        cloud.position.x += dt * 1.5;
        // Wrap around player
        if (cloud.position.x - playerPos.x > 120) cloud.position.x -= 240;
        if (cloud.position.x - playerPos.x < -120) cloud.position.x += 240;
        if (cloud.position.z - playerPos.z > 120) cloud.position.z -= 240;
        if (cloud.position.z - playerPos.z < -120) cloud.position.z += 240;
    }
}

function updateOutline() {
    const t = getTarget();
    if (t) {
        outlineLine.visible = true;
        outlineLine.position.set(t.bx + 0.5, t.by + 0.5, t.bz + 0.5);
    } else {
        outlineLine.visible = false;
    }
}

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);

    if (pointerLocked) {
        updatePlayer(dt);
    }

    updateChunks();
    updateClouds(dt);
    waterPlane.position.set(playerPos.x, 14.3, playerPos.z);
    updateOutline();

    renderer.render(scene, camera);
}

// --- Init ---
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Force generate spawn chunk
const scx = Math.floor(SPAWN.x / CS), scz = Math.floor(SPAWN.z / CS);
chunks.set(chunkKey(scx, scz), { data: generateChunkData(scx, scz), mesh: null });
// Also generate neighbors for meshing
for (let dx = -1; dx <= 1; dx++)
    for (let dz = -1; dz <= 1; dz++) {
        const k = chunkKey(scx+dx, scz+dz);
        if (!chunks.has(k)) chunks.set(k, { data: generateChunkData(scx+dx, scz+dz), mesh: null });
    }
// Build spawn chunk mesh immediately
buildChunkMesh(scx, scz);

playerPos.y = findSpawnY();
camera.position.set(playerPos.x, playerPos.y + 1.62, playerPos.z);

animate();

})();
</script>
</body>
</html>
```