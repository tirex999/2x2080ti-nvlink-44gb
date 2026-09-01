

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Minecraft Clone</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;width:100vw;height:100vh}
canvas{display:block}
#overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.75);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;font-family:Arial,sans-serif;z-index:100;cursor:pointer}
#overlay h1{font-size:48px;margin-bottom:20px;text-shadow:2px 2px 4px #000}
#overlay p{font-size:16px;margin:4px 0;opacity:0.9}
#overlay .play{margin-top:24px;font-size:22px;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:24px;height:24px;pointer-events:none;z-index:50}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:rgba(255,255,255,0.8)}
#crosshair::before{width:2px;height:24px;left:11px;top:0}
#crosshair::after{width:24px;height:2px;left:0;top:11px}
#hotbar{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);display:flex;gap:3px;background:rgba(0,0,0,0.55);padding:5px;border-radius:6px;z-index:50}
.slot{width:50px;height:50px;border:2px solid #555;display:flex;align-items:center;justify-content:center;position:relative;border-radius:3px}
.slot.selected{border-color:#fff;box-shadow:0 0 6px rgba(255,255,255,0.5)}
.slot .swatch{width:34px;height:34px;border-radius:3px;border:1px solid rgba(0,0,0,0.3)}
.slot .num{position:absolute;top:2px;left:4px;font-size:11px;color:#fff;font-family:monospace;text-shadow:1px 1px 1px #000}
</style>
</head>
<body>
<div id="overlay">
<h1>&#9632; Minecraft Clone</h1>
<p>WASD &mdash; Move</p>
<p>Space &mdash; Jump</p>
<p>Mouse &mdash; Look</p>
<p>Left Click &mdash; Break Block</p>
<p>Right Click &mdash; Place Block</p>
<p>1&ndash;7 / Scroll &mdash; Select Block</p>
<p class="play">Click to Play</p>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// ===== CONSTANTS =====
const CHUNK_W = 16, CHUNK_H = 80;
const GEN_RADIUS = 5, MESH_RADIUS = 4, UNLOAD_RADIUS = 7;
const MAX_GEN_PER_FRAME = 4, MAX_MESH_PER_FRAME = 2;
const GRAVITY = 25, JUMP_VEL = 8.5, MOVE_SPEED = 5.5;
const PLAYER_HW = 0.3, PLAYER_H = 1.8, EYE_H = 1.62;
const REACH = 6;
const SPAWN_X = 8, SPAWN_Z = 8;

const BLOCK_COLORS = [
    null,
    [0x4c/255, 0xaf/255, 0x50/255],
    [0x79/255, 0x55/255, 0x48/255],
    [0x9e/255, 0x9e/255, 0x9e/255],
    [0xe7/255, 0xd9/255, 0xa8/255],
    [0x8d/255, 0x6e/255, 0x63/255],
    [0x2e/255, 0x7d/255, 0x32/255],
    [1, 1, 1]
];

const FACES = [
    {dir:[0,1,0],  corners:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]], bright:1.0},
    {dir:[0,-1,0], corners:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]], bright:0.55},
    {dir:[1,0,0],  corners:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]], bright:0.8},
    {dir:[-1,0,0], corners:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]], bright:0.8},
    {dir:[0,0,1],  corners:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]], bright:0.8},
    {dir:[0,0,-1], corners:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]], bright:0.8}
];

// ===== NOISE =====
function hash2(x, z) {
    let n = (x * 374761393 + z * 668265263) | 0;
    n = ((n ^ (n >> 13)) * 1274126177) | 0;
    n = (n ^ (n >> 16)) | 0;
    return (n & 0x7fffffff) / 0x7fffffff;
}

function hash3(x, y, z) {
    let n = (x * 374761393 + y * 668265263 + z * 1274126177) | 0;
    n = ((n ^ (n >> 13)) * 1274126177) | 0;
    n = (n ^ (n >> 16)) | 0;
    return (n & 0x7fffffff) / 0x7fffffff;
}

function smoothstep(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
    const xi = Math.floor(x), zi = Math.floor(z);
    const xf = x - xi, zf = z - zi;
    const u = smoothstep(xf), v = smoothstep(zf);
    const a = hash2(xi, zi), b = hash2(xi+1, zi);
    const c = hash2(xi, zi+1), d = hash2(xi+1, zi+1);
    return a + (b-a)*u + (c-a)*v + (a-b-c+d)*u*v;
}

function fractal2(x, z) {
    let val = 0, amp = 1, freq = 1, max = 0;
    for (let i = 0; i < 4; i++) {
        val += noise2(x*freq, z*freq) * amp;
        max += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return val / max;
}

function noise3(x, y, z) {
    const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    const xf = x-xi, yf = y-yi, zf = z-zi;
    const u = smoothstep(xf), v = smoothstep(yf), w = smoothstep(zf);
    const c000=hash3(xi,yi,zi), c100=hash3(xi+1,yi,zi);
    const c010=hash3(xi,yi+1,zi), c110=hash3(xi+1,yi+1,zi);
    const c001=hash3(xi,yi,zi+1), c101=hash3(xi+1,yi,zi+1);
    const c011=hash3(xi,yi+1,zi+1), c111=hash3(xi+1,yi+1,zi+1);
    const x00=c000+(c100-c000)*u, x10=c010+(c110-c010)*u;
    const x01=c001+(c101-c001)*u, x11=c011+(c111-c011)*u;
    const y0=x00+(x10-x00)*v, y1=x01+(x11-x01)*v;
    return y0+(y1-y0)*w;
}

// ===== CHUNK STORAGE =====
const chunks = new Map();
const chunkMeshes = [];

function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= CHUNK_H) return 0;
    const cx = Math.floor(wx / CHUNK_W);
    const cz = Math.floor(wz / CHUNK_W);
    const chunk = chunks.get(cx + ',' + cz);
    if (!chunk) return 0;
    const lx = wx - cx * CHUNK_W;
    const lz = wz - cz * CHUNK_W;
    return chunk.data[wy * 256 + lz * 16 + lx];
}

function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= CHUNK_H) return;
    const cx = Math.floor(wx / CHUNK_W);
    const cz = Math.floor(wz / CHUNK_W);
    const chunk = chunks.get(cx + ',' + cz);
    if (!chunk) return;
    const lx = wx - cx * CHUNK_W;
    const lz = wz - cz * CHUNK_W;
    chunk.data[wy * 256 + lz * 16 + lx] = id;
}

// ===== TERRAIN GENERATION =====
function generateChunkData(cx, cz) {
    const data = new Uint8Array(CHUNK_W * CHUNK_W * CHUNK_H);

    for (let lx = 0; lx < CHUNK_W; lx++) {
        for (let lz = 0; lz < CHUNK_W; lz++) {
            const wx = cx * CHUNK_W + lx;
            const wz = cz * CHUNK_W + lz;
            const m = fractal2(wx * 0.004, wz * 0.004);
            const h = fractal2(wx * 0.02, wz * 0.02);
            const H = Math.floor(5 + m * m * 58 + h * 10);

            let surface, sub;
            if (H >= 46) { surface = 7; sub = 3; }
            else if (H >= 37) { surface = 3; sub = 3; }
            else if (H <= 16) { surface = 4; sub = 4; }
            else { surface = 1; sub = 2; }

            for (let y = 0; y <= Math.min(H, CHUNK_H - 1); y++) {
                let block;
                if (y === 0) block = 3;
                else if (y < H - 3) block = 3;
                else if (y < H) block = sub;
                else block = surface;

                if (y >= 3 && y <= H - 2) {
                    if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) block = 0;
                }
                data[y * 256 + lz * 16 + lx] = block;
            }
        }
    }

    // Trees
    for (let lx = 2; lx <= 13; lx++) {
        for (let lz = 2; lz <= 13; lz++) {
            const wx = cx * CHUNK_W + lx;
            const wz = cz * CHUNK_W + lz;
            const m = fractal2(wx * 0.004, wz * 0.004);
            const h = fractal2(wx * 0.02, wz * 0.02);
            const H = Math.floor(5 + m * m * 58 + h * 10);

            if (H > 16 && H < 37 && H < CHUNK_H - 8) {
                const sIdx = H * 256 + lz * 16 + lx;
                if (data[sIdx] === 1 && hash2(wx, wz) < 0.02) {
                    // Trunk
                    for (let ty = 1; ty <= 4; ty++) {
                        const ti = (H + ty) * 256 + lz * 16 + lx;
                        data[ti] = 5;
                    }
                    // Leaves 5x5 at H+4 and H+5
                    for (let dy = 4; dy <= 5; dy++) {
                        for (let dx = -2; dx <= 2; dx++) {
                            for (let dz = -2; dz <= 2; dz++) {
                                const tx = lx + dx, tz = lz + dz, ty = H + dy;
                                if (tx >= 0 && tx < 16 && tz >= 0 && tz < 16 && ty < CHUNK_H) {
                                    const li = ty * 256 + tz * 16 + tx;
                                    if (data[li] === 0) data[li] = 6;
                                }
                            }
                        }
                    }
                    // 3x3 at H+6
                    for (let dx = -1; dx <= 1; dx++) {
                        for (let dz = -1; dz <= 1; dz++) {
                            const tx = lx + dx, tz = lz + dz, ty = H + 6;
                            if (tx >= 0 && tx < 16 && tz >= 0 && tz < 16 && ty < CHUNK_H) {
                                const li = ty * 256 + tz * 16 + tx;
                                if (data[li] === 0) data[li] = 6;
                            }
                        }
                    }
                    // 1 at H+7
                    if (H + 7 < CHUNK_H) {
                        const li = (H + 7) * 256 + lz * 16 + lx;
                        if (data[li] === 0) data[li] = 6;
                    }
                }
            }
        }
    }
    return data;
}

// ===== MESH BUILDING =====
const sharedMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

function rebuildChunk(cx, cz) {
    const key = cx + ',' + cz;
    const chunk = chunks.get(key);
    if (!chunk) return;

    if (chunk.mesh) {
        scene.remove(chunk.mesh);
        const idx = chunkMeshes.indexOf(chunk.mesh);
        if (idx !== -1) chunkMeshes.splice(idx, 1);
        chunk.mesh.geometry.dispose();
        chunk.mesh = null;
    }

    const positions = [], normals = [], colors = [];

    for (let y = 0; y < CHUNK_H; y++) {
        for (let lz = 0; lz < CHUNK_W; lz++) {
            for (let lx = 0; lx < CHUNK_W; lx++) {
                const bid = chunk.data[y * 256 + lz * 16 + lx];
                if (bid === 0) continue;
                const wx = cx * CHUNK_W + lx;
                const wz = cz * CHUNK_W + lz;
                const col = BLOCK_COLORS[bid];

                for (let f = 0; f < 6; f++) {
                    const face = FACES[f];
                    const nx = wx + face.dir[0];
                    const ny = y + face.dir[1];
                    const nz = wz + face.dir[2];
                    if (getBlock(nx, ny, nz) !== 0) continue;

                    const c = face.corners;
                    const br = face.bright;
                    const tri = [0,1,2, 0,2,3];
                    for (let t = 0; t < 6; t++) {
                        const ci = tri[t];
                        positions.push(wx + c[ci][0], y + c[ci][1], wz + c[ci][2]);
                        normals.push(face.dir[0], face.dir[1], face.dir[2]);
                        colors.push(col[0]*br, col[1]*br, col[2]*br);
                    }
                }
            }
        }
    }

    if (positions.length > 0) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        const mesh = new THREE.Mesh(geo, sharedMaterial);
        scene.add(mesh);
        chunk.mesh = mesh;
        chunkMeshes.push(mesh);
    }
}

// ===== SCENE SETUP =====
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: false });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);
const canvas = renderer.domElement;

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(0.5, 1, 0.3).normalize();
scene.add(dirLight);

// Water plane
const waterGeo = new THREE.PlaneGeometry(300, 300);
waterGeo.rotateX(-Math.PI / 2);
const waterMat = new THREE.MeshLambertMaterial({ color: 0x3388cc, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
const waterMesh = new THREE.Mesh(waterGeo, waterMat);
waterMesh.position.y = 14.3;
scene.add(waterMesh);

// Clouds
const cloudGroup = new THREE.Group();
const cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.75 });
const clouds = [];
for (let i = 0; i < 25; i++) {
    const cw = 6 + hash2(i, 7) * 10;
    const cd = 4 + hash2(i, 13) * 8;
    const geo = new THREE.BoxGeometry(cw, 0.5, cd);
    const cm = new THREE.Mesh(geo, cloudMat);
    const angle = (i / 25) * Math.PI * 2;
    const dist = 30 + hash2(i, 3) * 80;
    cm.position.set(Math.cos(angle) * dist, 88 + hash2(i, 11) * 8, Math.sin(angle) * dist);
    cloudGroup.add(cm);
    clouds.push(cm);
}
scene.add(cloudGroup);

// Outline box
const outlineGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(1.005, 1.005, 1.005));
const outline = new THREE.LineSegments(outlineGeo, new THREE.LineBasicMaterial({ color: 0x000000 }));
outline.visible = false;
scene.add(outline);

// ===== PLAYER STATE =====
let playerX = SPAWN_X, playerY = 50, playerZ = SPAWN_Z;
let velY = 0;
let yaw = 0, pitch = 0;
let onGround = false;
let spawnY = 50;

// Generate spawn chunk
(function initSpawn() {
    const scx = Math.floor(SPAWN_X / CHUNK_W);
    const scz = Math.floor(SPAWN_Z / CHUNK_W);
    chunks.set(scx + ',' + scz, { data: generateChunkData(scx, scz), mesh: null });
    for (let y = CHUNK_H - 1; y >= 0; y--) {
        if (getBlock(SPAWN_X, y, SPAWN_Z) !== 0) {
            spawnY = y + 1;
            break;
        }
    }
    playerY = spawnY;
})();

// ===== INPUT =====
const keys = {};
let pointerLocked = false;

document.addEventListener('keydown', e => { keys[e.code] = true; });
document.addEventListener('keyup', e => { keys[e.code] = false; });

document.addEventListener('mousemove', e => {
    if (!pointerLocked) return;
    yaw -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;
    pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, pitch));
});

const overlay = document.getElementById('overlay');
overlay.addEventListener('click', () => {
    canvas.requestPointerLock();
});

document.addEventListener('pointerlockchange', () => {
    pointerLocked = (document.pointerLockElement === canvas);
    overlay.style.display = pointerLocked ? 'none' : 'flex';
});

document.addEventListener('contextmenu', e => e.preventDefault());

// ===== HOTBAR =====
const hotbarItems = [
    { id: 1, color: '#4caf50' },
    { id: 2, color: '#795548' },
    { id: 3, color: '#9e9e9e' },
    { id: 4, color: '#e7d9a8' },
    { id: 5, color: '#8d6e63' },
    { id: 6, color: '#2e7d32' },
    { id: 7, color: '#ffffff' }
];
let selectedSlot = 0;
const hotbarEl = document.getElementById('hotbar');
hotbarItems.forEach((item, i) => {
    const slot = document.createElement('div');
    slot.className = 'slot' + (i === 0 ? ' selected' : '');
    slot.innerHTML = '<div class="swatch" style="background:' + item.color + '"></div><span class="num">' + (i+1) + '</span>';
    hotbarEl.appendChild(slot);
});

function updateHotbarUI() {
    const slots = hotbarEl.children;
    for (let i = 0; i < slots.length; i++) {
        slots[i].className = 'slot' + (i === selectedSlot ? ' selected' : '');
    }
}

document.addEventListener('keydown', e => {
    if (e.code >= 'Digit1' && e.code <= 'Digit7') {
        selectedSlot = parseInt(e.code.charAt(5)) - 1;
        updateHotbarUI();
    }
});

document.addEventListener('wheel', e => {
    if (!pointerLocked) return;
    if (e.deltaY > 0) selectedSlot = (selectedSlot + 1) % 7;
    else selectedSlot = (selectedSlot + 6) % 7;
    updateHotbarUI();
});

// ===== COLLISION =====
function collides(px, py, pz) {
    const minX = Math.floor(px - PLAYER_HW);
    const maxX = Math.floor(px + PLAYER_HW);
    const minY = Math.floor(py);
    const maxY = Math.floor(py + PLAYER_H);
    const minZ = Math.floor(pz - PLAYER_HW);
    const maxZ = Math.floor(pz + PLAYER_HW);
    for (let x = minX; x <= maxX; x++)
        for (let y = minY; y <= maxY; y++)
            for (let z = minZ; z <= maxZ; z++)
                if (getBlock(x, y, z) !== 0) return true;
    return false;
}

// ===== RAYCAST & BLOCK INTERACTION =====
const raycaster = new THREE.Raycaster();
raycaster.far = REACH;
const centerVec = new THREE.Vector2(0, 0);

let targetBlock = null;

function updateTarget() {
    raycaster.setFromCamera(centerVec, camera);
    const hits = raycaster.intersectObjects(chunkMeshes);
    if (hits.length > 0) {
        const hit = hits[0];
        const n = hit.face.normal;
        const nx = Math.round(n.x), ny = Math.round(n.y), nz = Math.round(n.z);
        const p = hit.point;
        const bx = Math.floor(p.x - nx * 0.5);
        const by = Math.floor(p.y - ny * 0.5);
        const bz = Math.floor(p.z - nz * 0.5);
        targetBlock = { x: bx, y: by, z: bz, nx: nx, ny: ny, nz: nz };
        outline.position.set(bx + 0.5, by + 0.5, bz + 0.5);
        outline.visible = true;
    } else {
        targetBlock = null;
        outline.visible = false;
    }
}

function editChunkRebuild(wx, wy, wz) {
    const cx = Math.floor(wx / CHUNK_W);
    const cz = Math.floor(wz / CHUNK_W);
    rebuildChunk(cx, cz);
    const lx = wx - cx * CHUNK_W;
    const lz = wz - cz * CHUNK_W;
    if (lx === 0) rebuildChunk(cx - 1, cz);
    if (lx === CHUNK_W - 1) rebuildChunk(cx + 1, cz);
    if (lz === 0) rebuildChunk(cx, cz - 1);
    if (lz === CHUNK_W - 1) rebuildChunk(cx, cz + 1);
}

canvas.addEventListener('mousedown', e => {
    if (!pointerLocked || !targetBlock) return;
    const t = targetBlock;
    if (e.button === 0) {
        // Break
        if (t.y > 0) {
            setBlock(t.x, t.y, t.z, 0);
            editChunkRebuild(t.x, t.y, t.z);
        }
    } else if (e.button === 2) {
        // Place
        const px = t.x + t.nx;
        const py = t.y + t.ny;
        const pz = t.z + t.nz;
        if (getBlock(px, py, pz) === 0) {
            // Check overlap with player
            const bMinX = px, bMaxX = px + 1;
            const bMinY = py, bMaxY = py + 1;
            const bMinZ = pz, bMaxZ = pz + 1;
            const pMinX = playerX - PLAYER_HW, pMaxX = playerX + PLAYER_HW;
            const pMinY = playerY, pMaxY = playerY + PLAYER_H;
            const pMinZ = playerZ - PLAYER_HW, pMaxZ = playerZ + PLAYER_HW;
            const overlap = pMinX < bMaxX && pMaxX > bMinX && pMinY < bMaxY && pMaxY > bMinY && pMinZ < bMaxZ && pMaxZ > bMinZ;
            if (!overlap) {
                setBlock(px, py, pz, hotbarItems[selectedSlot].id);
                editChunkRebuild(px, py, pz);
            }
        }
    }
});

// ===== CHUNK MANAGEMENT =====
function updateChunks() {
    const pcx = Math.floor(playerX / CHUNK_W);
    const pcz = Math.floor(playerZ / CHUNK_W);

    // Generate
    let genCount = 0;
    const genList = [];
    for (let dx = -GEN_RADIUS; dx <= GEN_RADIUS; dx++) {
        for (let dz = -GEN_RADIUS; dz <= GEN_RADIUS; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            if (!chunks.has(cx + ',' + cz)) {
                genList.push({ cx, cz, d: dx*dx + dz*dz });
            }
        }
    }
    genList.sort((a, b) => a.d - b.d);
    for (let i = 0; i < Math.min(MAX_GEN_PER_FRAME, genList.length); i++) {
        chunks.set(genList[i].cx + ',' + genList[i].cz, { data: generateChunkData(genList[i].cx, genList[i].cz), mesh: null });
        genCount++;
    }

    // Mesh
    let meshCount = 0;
    const meshList = [];
    for (let dx = -MESH_RADIUS; dx <= MESH_RADIUS; dx++) {
        for (let dz = -MESH_RADIUS; dz <= MESH_RADIUS; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = cx + ',' + cz;
            const ch = chunks.get(key);
            if (ch && !ch.mesh) {
                if (chunks.has((cx-1)+','+cz) && chunks.has((cx+1)+','+cz) &&
                    chunks.has(cx+','+(cz-1)) && chunks.has(cx+','+(cz+1))) {
                    meshList.push({ cx, cz, d: dx*dx + dz*dz });
                }
            }
        }
    }
    meshList.sort((a, b) => a.d - b.d);
    for (let i = 0; i < Math.min(MAX_MESH_PER_FRAME, meshList.length); i++) {
        rebuildChunk(meshList[i].cx, meshList[i].cz);
        meshCount++;
    }

    // Unload
    for (const [key, chunk] of chunks) {
        const parts = key.split(',');
        const cx = parseInt(parts[0]), cz = parseInt(parts[1]);
        const adx = Math.abs(cx - pcx), adz = Math.abs(cz - pcz);
        if (adx > UNLOAD_RADIUS || adz > UNLOAD_RADIUS) {
            if (chunk.mesh) {
                scene.remove(chunk.mesh);
                const mi = chunkMeshes.indexOf(chunk.mesh);
                if (mi !== -1) chunkMeshes.splice(mi, 1);
                chunk.mesh.geometry.dispose();
            }
            chunks.delete(key);
        }
    }
}

// ===== MAIN LOOP =====
let lastTime = performance.now();

function gameLoop() {
    requestAnimationFrame(gameLoop);
    const now = performance.now();
    let dt = (now - lastTime) / 1000;
    lastTime = now;
    if (dt > 0.1) dt = 0.1;

    // Update player
    if (pointerLocked) {
        velY -= GRAVITY * dt;
        if (keys['Space'] && onGround) {
            velY = JUMP_VEL;
            onGround = false;
        }

        let mx = 0, mz = 0;
        if (keys['KeyW']) { mx += -Math.sin(yaw); mz += -Math.cos(yaw); }
        if (keys['KeyS']) { mx += Math.sin(yaw); mz += Math.cos(yaw); }
        if (keys['KeyD']) { mx += Math.cos(yaw); mz += -Math.sin(yaw); }
        if (keys['KeyA']) { mx += -Math.cos(yaw); mz += Math.sin(yaw); }

        const ml = Math.sqrt(mx*mx + mz*mz);
        if (ml > 0) { mx = mx/ml * MOVE_SPEED * dt; mz = mz/ml * MOVE_SPEED * dt; }

        // X
        const nx = playerX + mx;
        if (!collides(nx, playerY, playerZ)) playerX = nx;

        // Z
        const nz = playerZ + mz;
        if (!collides(playerX, playerY, nz)) playerZ = nz;

        // Y
        const ny = playerY + velY * dt;
        if (!collides(playerX, ny, playerZ)) {
            playerY = ny;
            onGround = false;
        } else {
            if (velY < 0) onGround = true;
            velY = 0;
        }

        // Fall out
        if (playerY < -20) {
            playerX = SPAWN_X;
            playerY = spawnY;
            playerZ = SPAWN_Z;
            velY = 0;
        }
    }

    // Camera
    camera.position.set(playerX, playerY + EYE_H, playerZ);
    camera.rotation.set(pitch, yaw, 0);

    // Water follows player
    waterMesh.position.x = playerX;
    waterMesh.position.z = playerZ;

    // Clouds drift
    for (let i = 0; i < clouds.length; i++) {
        clouds[i].position.x += 0.3 * dt;
        const dx = clouds[i].position.x - playerX;
        const dz = clouds[i].position.z - playerZ;
        if (dx > 120) clouds[i].position.x -= 240;
        if (dx < -120) clouds[i].position.x += 240;
        if (dz > 120) clouds[i].position.z -= 240;
        if (dz < -120) clouds[i].position.z += 240;
    }

    // Chunks
    updateChunks();

    // Target
    updateTarget();

    renderer.render(scene, camera);
}

// ===== RESIZE =====
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Start
gameLoop();

})();
</script>
</body>
</html>
```