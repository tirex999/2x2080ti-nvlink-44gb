Причина: игрок спавнился на фиксированной высоте y=60, тогда как поверхность рельефа в точке (8,8) лежит примерно на y≈20–25 — камера смотрит горизонтально, поэтому вся земля оказывается ниже нижней границы экрана и скрывается туманом; видны только облака на y=90 и небо. Нужно спавнить игрока на уровне поверхности.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Minecraft Clone</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; width: 100vw; height: 100vh; }
canvas { display: block; }
#crosshair {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 20px; height: 20px; pointer-events: none; z-index: 10;
}
#crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: rgba(255,255,255,0.8);
}
#crosshair::before { width: 2px; height: 20px; left: 9px; top: 0; }
#crosshair::after { width: 20px; height: 2px; top: 9px; left: 0; }
#hotbar {
    position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; padding: 6px; background: rgba(0,0,0,0.5);
    border-radius: 6px; z-index: 10;
}
.slot {
    width: 48px; height: 48px; border: 2px solid rgba(255,255,255,0.3);
    border-radius: 4px; display: flex; align-items: center; justify-content: center;
    position: relative;
}
.slot.selected { border-color: #fff; border-width: 3px; }
.slot .swatch { width: 32px; height: 32px; border-radius: 3px; }
.slot .num {
    position: absolute; top: 2px; left: 4px; font-size: 10px;
    color: rgba(255,255,255,0.8); font-family: monospace;
}
#overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.75); display: flex; flex-direction: column;
    align-items: center; justify-content: center; z-index: 100; cursor: pointer;
}
#overlay h1 { color: #fff; font-size: 48px; font-family: monospace; margin-bottom: 20px; }
#overlay p { color: #ccc; font-size: 16px; font-family: monospace; margin: 4px 0; }
#overlay .play { color: #ff0; font-size: 24px; margin-top: 30px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
    <h1>MC Clone</h1>
    <p>WASD — Move &nbsp;|&nbsp; Mouse — Look &nbsp;|&nbsp; Space — Jump</p>
    <p>Left Click — Break &nbsp;|&nbsp; Right Click — Place</p>
    <p>1–7 / Scroll — Select Block</p>
    <p class="play">Click to Play</p>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// --- Constants ---
const CHUNK_SIZE = 16;
const CHUNK_HEIGHT = 80;
const CHUNK_VOL = CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT;
const GRAVITY = 25;
const JUMP_VEL = 8.5;
const WALK_SPEED = 5.5;
const PLAYER_HW = 0.3;
const PLAYER_H = 1.8;
const EYE_H = 1.62;
const REACH = 6;
const MOUSE_SENS = 0.002;

const BLOCK_COLORS = {
    1: [0x4c/255, 0xaf/255, 0x50/255],
    2: [0x79/255, 0x55/255, 0x48/255],
    3: [0x9e/255, 0x9e/255, 0x9e/255],
    4: [0xe7/255, 0xd9/255, 0xa8/255],
    5: [0x8d/255, 0x6e/255, 0x63/255],
    6: [0x2e/255, 0x7d/255, 0x32/255],
    7: [1, 1, 1]
};

const HOTBAR_BLOCKS = [1, 2, 3, 4, 5, 6, 7];

// --- Noise ---
function hash2(x, z) {
    let n = (x | 0) * 374761393 + (z | 0) * 668265263;
    n = ((n >> 13) ^ n) * 1274126177;
    n = (n >> 16) ^ n;
    return (n & 0x7fffffff) / 0x7fffffff;
}

function hash3(x, y, z) {
    let n = (x | 0) * 374761393 + (y | 0) * 668265263 + (z | 0) * 1013904223;
    n = ((n >> 13) ^ n) * 1274126177;
    n = (n >> 16) ^ n;
    return (n & 0x7fffffff) / 0x7fffffff;
}

function smoothstep(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
    const ix = Math.floor(x), iz = Math.floor(z);
    const fx = x - ix, fz = z - iz;
    const sx = smoothstep(fx), sz = smoothstep(fz);
    const a = hash2(ix, iz), b = hash2(ix + 1, iz);
    const c = hash2(ix, iz + 1), d = hash2(ix + 1, iz + 1);
    return a + (b - a) * sx + (c - a) * sz + (a - b - c + d) * sx * sz;
}

function fractal2(x, z) {
    let val = 0, amp = 1, freq = 1, max = 0;
    for (let i = 0; i < 4; i++) {
        val += noise2(x * freq, z * freq) * amp;
        max += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return val / max;
}

function noise3(x, y, z) {
    const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    const fx = x - ix, fy = y - iy, fz = z - iz;
    const sx = smoothstep(fx), sy = smoothstep(fy), sz = smoothstep(fz);
    const c000 = hash3(ix, iy, iz), c100 = hash3(ix+1, iy, iz);
    const c010 = hash3(ix, iy+1, iz), c110 = hash3(ix+1, iy+1, iz);
    const c001 = hash3(ix, iy, iz+1), c101 = hash3(ix+1, iy, iz+1);
    const c011 = hash3(ix, iy+1, iz+1), c111 = hash3(ix+1, iy+1, iz+1);
    const c00 = c000 + (c100 - c000) * sx;
    const c10 = c010 + (c110 - c010) * sx;
    const c01 = c001 + (c101 - c001) * sx;
    const c11 = c011 + (c111 - c011) * sx;
    const c0 = c00 + (c10 - c00) * sy;
    const c1 = c01 + (c11 - c01) * sy;
    return c0 + (c1 - c0) * sz;
}

// --- Chunk System ---
const chunks = new Map();
const allMeshes = [];

function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= CHUNK_HEIGHT) return 0;
    const cx = Math.floor(wx / CHUNK_SIZE);
    const cz = Math.floor(wz / CHUNK_SIZE);
    const chunk = chunks.get(cx + ',' + cz);
    if (!chunk) return 0;
    const lx = wx - cx * CHUNK_SIZE;
    const lz = wz - cz * CHUNK_SIZE;
    if (lx < 0 || lx >= 16 || lz < 0 || lz >= 16) return 0;
    return chunk.data[wy * 256 + lz * 16 + lx];
}

function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= CHUNK_HEIGHT) return;
    const cx = Math.floor(wx / CHUNK_SIZE);
    const cz = Math.floor(wz / CHUNK_SIZE);
    const chunk = chunks.get(cx + ',' + cz);
    if (!chunk) return;
    const lx = wx - cx * CHUNK_SIZE;
    const lz = wz - cz * CHUNK_SIZE;
    if (lx < 0 || lx >= 16 || lz < 0 || lz >= 16) return;
    chunk.data[wy * 256 + lz * 16 + lx] = id;
}

// --- Terrain Generation ---
function generateChunk(cx, cz) {
    const data = new Uint8Array(CHUNK_VOL);
    for (let lx = 0; lx < 16; lx++) {
        for (let lz = 0; lz < 16; lz++) {
            const wx = cx * 16 + lx;
            const wz = cz * 16 + lz;
            const m = fractal2(wx * 0.004, wz * 0.004);
            const h = fractal2(wx * 0.02, wz * 0.02);
            const H = Math.floor(5 + m * m * 58 + h * 10);

            for (let y = 0; y < CHUNK_HEIGHT; y++) {
                let block = 0;
                if (y === 0) {
                    block = 3;
                } else if (y < H - 3) {
                    block = 3;
                } else if (y < H) {
                    if (H <= 16) block = 4;
                    else if (H >= 37) block = 3;
                    else block = 2;
                } else if (y === H) {
                    if (H >= 46) block = 7;
                    else if (H >= 37) block = 3;
                    else if (H <= 16) block = 4;
                    else block = 1;
                }

                if (block !== 0 && y >= 3 && y < H - 2) {
                    if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
                        block = 0;
                    }
                }
                data[y * 256 + lz * 16 + lx] = block;
            }
        }
    }

    // Trees
    for (let lx = 0; lx < 16; lx++) {
        for (let lz = 0; lz < 16; lz++) {
            const wx = cx * 16 + lx;
            const wz = cz * 16 + lz;
            let surfaceY = -1;
            for (let y = CHUNK_HEIGHT - 1; y >= 0; y--) {
                if (data[y * 256 + lz * 16 + lx] !== 0) { surfaceY = y; break; }
            }
            if (surfaceY < 0 || data[surfaceY * 256 + lz * 16 + lx] !== 1) continue;
            if (surfaceY + 6 >= CHUNK_HEIGHT) continue;

            const th = hash2(wx * 7 + 13, wz * 7 + 29);
            if (th >= 0.02) continue;

            // Trunk
            for (let ty = 1; ty <= 4; ty++) {
                data[(surfaceY + ty) * 256 + lz * 16 + lx] = 5;
            }
            // Leaves 5x5 at surfaceY+3
            for (let dx = -2; dx <= 2; dx++) {
                for (let dz = -2; dz <= 2; dz++) {
                    const nx = lx + dx, nz = lz + dz;
                    if (nx >= 0 && nx < 16 && nz >= 0 && nz < 16) {
                        const idx = (surfaceY + 3) * 256 + nz * 16 + nx;
                        if (data[idx] === 0) data[idx] = 6;
                    }
                }
            }
            // Leaves 5x5 at surfaceY+4
            for (let dx = -2; dx <= 2; dx++) {
                for (let dz = -2; dz <= 2; dz++) {
                    const nx = lx + dx, nz = lz + dz;
                    if (nx >= 0 && nx < 16 && nz >= 0 && nz < 16) {
                        const idx = (surfaceY + 4) * 256 + nz * 16 + nx;
                        if (data[idx] === 0) data[idx] = 6;
                    }
                }
            }
            // Leaves 3x3 at surfaceY+5
            for (let dx = -1; dx <= 1; dx++) {
                for (let dz = -1; dz <= 1; dz++) {
                    const nx = lx + dx, nz = lz + dz;
                    if (nx >= 0 && nx < 16 && nz >= 0 && nz < 16) {
                        const idx = (surfaceY + 5) * 256 + nz * 16 + nx;
                        if (data[idx] === 0) data[idx] = 6;
                    }
                }
            }
            // 1 leaf at surfaceY+6
            {
                const idx = (surfaceY + 6) * 256 + lz * 16 + lx;
                if (data[idx] === 0) data[idx] = 6;
            }
        }
    }
    return data;
}

// --- Meshing ---
const FACES = [
    { dir: [0, 1, 0],  corners: [[0,1,0],[0,1,1],[1,1,1],[1,1,0]], shade: 1.0 },
    { dir: [0,-1, 0],  corners: [[0,0,1],[0,0,0],[1,0,0],[1,0,1]], shade: 0.55 },
    { dir: [0, 0, 1],  corners: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], shade: 0.8 },
    { dir: [0, 0,-1],  corners: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]], shade: 0.8 },
    { dir: [1, 0, 0],  corners: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]], shade: 0.8 },
    { dir: [-1,0, 0],  corners: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]], shade: 0.8 }
];

const material = new THREE.MeshLambertMaterial({ vertexColors: true });

function buildChunkMesh(cx, cz) {
    const key = cx + ',' + cz;
    const chunk = chunks.get(key);
    if (!chunk || !chunk.data) return;

    if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        const mi = allMeshes.indexOf(chunk.mesh);
        if (mi !== -1) allMeshes.splice(mi, 1);
        chunk.mesh = null;
    }

    const positions = [];
    const normals = [];
    const colors = [];

    for (let lx = 0; lx < 16; lx++) {
        for (let lz = 0; lz < 16; lz++) {
            for (let y = 0; y < CHUNK_HEIGHT; y++) {
                const blockId = chunk.data[y * 256 + lz * 16 + lx];
                if (blockId === 0) continue;

                const wx = cx * 16 + lx;
                const wz = cz * 16 + lz;
                const col = BLOCK_COLORS[blockId];

                for (let f = 0; f < 6; f++) {
                    const face = FACES[f];
                    const nx = wx + face.dir[0];
                    const ny = y + face.dir[1];
                    const nz = wz + face.dir[2];

                    if (getBlock(nx, ny, nz) !== 0) continue;

                    const sh = face.shade;
                    const r = col[0] * sh, g = col[1] * sh, b = col[2] * sh;

                    for (let i = 0; i < 6; i++) {
                        const ci = i < 3 ? i : (i === 3 ? 0 : i === 4 ? 2 : 3);
                        const c = face.corners[ci];
                        positions.push(wx + c[0], y + c[1], wz + c[2]);
                        normals.push(face.dir[0], face.dir[1], face.dir[2]);
                        colors.push(r, g, b);
                    }
                }
            }
        }
    }

    if (positions.length === 0) return;

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    chunk.mesh = new THREE.Mesh(geo, material);
    scene.add(chunk.mesh);
    allMeshes.push(chunk.mesh);
}

function rebuildChunk(cx, cz) {
    const key = cx + ',' + cz;
    if (!chunks.has(key)) return;
    buildChunkMesh(cx, cz);
}

function rebuildChunkAt(wx, wz) {
    const cx = Math.floor(wx / 16);
    const cz = Math.floor(wz / 16);
    rebuildChunk(cx, cz);
    const lx = wx - cx * 16;
    const lz = wz - cz * 16;
    if (lx === 0) rebuildChunk(cx - 1, cz);
    if (lx === 15) rebuildChunk(cx + 1, cz);
    if (lz === 0) rebuildChunk(cx, cz - 1);
    if (lz === 15) rebuildChunk(cx, cz + 1);
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
const canvas = renderer.domElement;

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(1, 2, 1);
scene.add(dirLight);

// Water
const waterGeo = new THREE.PlaneGeometry(200, 200);
waterGeo.rotateX(-Math.PI / 2);
const waterMat = new THREE.MeshLambertMaterial({ color: 0x3388cc, transparent: true, opacity: 0.6 });
const waterPlane = new THREE.Mesh(waterGeo, waterMat);
waterPlane.position.y = 14.3;
scene.add(waterPlane);

// Clouds
const cloudGroup = new THREE.Group();
const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
for (let i = 0; i < 25; i++) {
    const w = 8 + hash2(i, 100) * 12;
    const d = 8 + hash2(i, 200) * 12;
    const geo = new THREE.BoxGeometry(w, 1, d);
    const cloud = new THREE.Mesh(geo, cloudMat);
    cloud.position.set((hash2(i, 300) - 0.5) * 200, 90, (hash2(i, 400) - 0.5) * 200);
    cloudGroup.add(cloud);
}
scene.add(cloudGroup);

// Outline
const outlineGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01, 1.01, 1.01));
const outlineMat = new THREE.LineBasicMaterial({ color: 0x000000 });
const outlineBox = new THREE.LineSegments(outlineGeo, outlineMat);
outlineBox.visible = false;
scene.add(outlineBox);

// --- Player ---
const player = { x: 8.5, y: 40, z: 8.5, vx: 0, vy: 0, vz: 0, onGround: false, yaw: 0, pitch: 0 };

function getSpawnY() {
    for (let y = CHUNK_HEIGHT - 1; y >= 0; y--) {
        if (getBlock(8, y, 8) !== 0) return y + 1;
    }
    return 40;
}

function spawnPlayer() {
    player.x = 8.5;
    player.z = 8.5;
    player.y = getSpawnY();
    player.vx = 0; player.vy = 0; player.vz = 0;
    player.onGround = false;
}

// --- Input ---
const keys = {};
document.addEventListener('keydown', e => { keys[e.code] = true; });
document.addEventListener('keyup', e => { keys[e.code] = false; });

let selectedSlot = 0;
document.addEventListener('keydown', e => {
    if (e.code >= 'Digit1' && e.code <= 'Digit7') {
        selectedSlot = parseInt(e.code.charAt(5)) - 1;
        updateHotbar();
    }
});

document.addEventListener('wheel', e => {
    if (document.pointerLockElement !== canvas) return;
    if (e.deltaY > 0) selectedSlot = (selectedSlot + 1) % 7;
    else selectedSlot = (selectedSlot + 6) % 7;
    updateHotbar();
});

document.addEventListener('mousemove', e => {
    if (document.pointerLockElement !== canvas) return;
    player.yaw -= e.movementX * MOUSE_SENS;
    player.pitch -= e.movementY * MOUSE_SENS;
    player.pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, player.pitch));
});

document.addEventListener('contextmenu', e => e.preventDefault());

document.addEventListener('mousedown', e => {
    if (document.pointerLockElement !== canvas) return;
    const target = getTargetBlock();
    if (!target) return;
    if (e.button === 0) {
        const [bx, by, bz] = target.break;
        if (by !== 0) {
            setBlock(bx, by, bz, 0);
            rebuildChunkAt(bx, bz);
        }
    } else if (e.button === 2) {
        const [px, py, pz] = target.place;
        if (getBlock(px, py, pz) === 0 && !overlapsPlayer(px, py, pz)) {
            setBlock(px, py, pz, HOTBAR_BLOCKS[selectedSlot]);
            rebuildChunkAt(px, pz);
        }
    }
});

// Overlay / Pointer Lock
const overlay = document.getElementById('overlay');
overlay.addEventListener('click', () => {
    canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
    if (document.pointerLockElement === canvas) {
        overlay.style.display = 'none';
    } else {
        overlay.style.display = 'flex';
    }
});

// --- Hotbar UI ---
const hotbarEl = document.getElementById('hotbar');
function buildHotbar() {
    hotbarEl.innerHTML = '';
    for (let i = 0; i < 7; i++) {
        const slot = document.createElement('div');
        slot.className = 'slot' + (i === selectedSlot ? ' selected' : '');
        const swatch = document.createElement('div');
        swatch.className = 'swatch';
        const c = BLOCK_COLORS[HOTBAR_BLOCKS[i]];
        swatch.style.background = 'rgb(' + Math.round(c[0]*255) + ',' + Math.round(c[1]*255) + ',' + Math.round(c[2]*255) + ')';
        const num = document.createElement('span');
        num.className = 'num';
        num.textContent = i + 1;
        slot.appendChild(swatch);
        slot.appendChild(num);
        hotbarEl.appendChild(slot);
    }
}
function updateHotbar() { buildHotbar(); }
buildHotbar();

// --- Collision ---
function checkCollision() {
    const px = player.x, py = player.y, pz = player.z;
    const minX = Math.floor(px - PLAYER_HW);
    const maxX = Math.floor(px + PLAYER_HW);
    const minY = Math.floor(py);
    const maxY = Math.floor(py + PLAYER_H);
    const minZ = Math.floor(pz - PLAYER_HW);
    const maxZ = Math.floor(pz + PLAYER_HW);

    for (let bx = minX; bx <= maxX; bx++) {
        for (let by = minY; by <= maxY; by++) {
            for (let bz = minZ; bz <= maxZ; bz++) {
                if (getBlock(bx, by, bz) !== 0) return true;
            }
        }
    }
    return false;
}

function overlapsPlayer(bx, by, bz) {
    const pMinX = player.x - PLAYER_HW, pMaxX = player.x + PLAYER_HW;
    const pMinY = player.y, pMaxY = player.y + PLAYER_H;
    const pMinZ = player.z - PLAYER_HW, pMaxZ = player.z + PLAYER_HW;
    const bMinX = bx, bMaxX = bx + 1;
    const bMinY = by, bMaxY = by + 1;
    const bMinZ = bz, bMaxZ = bz + 1;
    return pMaxX > bMinX && pMinX < bMaxX && pMaxY > bMinY && pMinY < bMaxY && pMaxZ > bMinZ && pMinZ < bMaxZ;
}

// --- Physics ---
function movePlayer(dt) {
    player.vy -= GRAVITY * dt;

    let mx = 0, mz = 0;
    if (keys['KeyW']) mz -= 1;
    if (keys['KeyS']) mz += 1;
    if (keys['KeyA']) mx -= 1;
    if (keys['KeyD']) mx += 1;

    const len = Math.sqrt(mx * mx + mz * mz);
    if (len > 0) { mx /= len; mz /= len; }

    const sy = Math.sin(player.yaw), cy = Math.cos(player.yaw);
    const dx = (mx * cy - mz * sy) * WALK_SPEED * dt;
    const dz = (mx * sy + mz * cy) * WALK_SPEED * dt;
    const dy = player.vy * dt;

    // X
    player.x += dx;
    if (checkCollision()) { player.x -= dx; }

    // Z
    player.z += dz;
    if (checkCollision()) { player.z -= dz; }

    // Y
    player.y += dy;
    if (checkCollision()) {
        player.y -= dy;
        if (player.vy < 0) player.onGround = true;
        player.vy = 0;
    } else {
        if (player.vy < 0) player.onGround = false;
    }

    if (keys['Space'] && player.onGround) {
        player.vy = JUMP_VEL;
        player.onGround = false;
    }

    if (player.y < -20) spawnPlayer();
}

// --- Raycast Target ---
const raycaster = new THREE.Raycaster();
raycaster.far = REACH;
const centerVec = new THREE.Vector2(0, 0);

function getTargetBlock() {
    raycaster.setFromCamera(centerVec, camera);
    const hits = raycaster.intersectObjects(allMeshes);
    if (hits.length === 0) return null;
    const hit = hits[0];
    const p = hit.point;
    const n = hit.face.normal;

    const bx = Math.floor(p.x - n.x * 0.5);
    const by = Math.floor(p.y - n.y * 0.5);
    const bz = Math.floor(p.z - n.z * 0.5);
    const px = Math.floor(p.x + n.x * 0.5);
    const py = Math.floor(p.y + n.y * 0.5);
    const pz = Math.floor(p.z + n.z * 0.5);

    return { break: [bx, by, bz], place: [px, py, pz] };
}

// --- Chunk Management ---
function updateChunks() {
    const pcx = Math.floor(player.x / 16);
    const pcz = Math.floor(player.z / 16);

    // Generate data (max 4/frame, within 5)
    let genCount = 0;
    for (let dx = -5; dx <= 5 && genCount < 4; dx++) {
        for (let dz = -5; dz <= 5 && genCount < 4; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = cx + ',' + cz;
            if (!chunks.has(key)) {
                chunks.set(key, { data: generateChunk(cx, cz), mesh: null });
                genCount++;
            }
        }
    }

    // Build meshes (max 2/frame, within 4, neighbors must exist)
    let meshCount = 0;
    for (let dx = -4; dx <= 4 && meshCount < 2; dx++) {
        for (let dz = -4; dz <= 4 && meshCount < 2; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = cx + ',' + cz;
            const chunk = chunks.get(key);
            if (!chunk || !chunk.data) continue;
            if (chunk.mesh) continue;

            if (!chunks.has((cx-1)+','+cz)) continue;
            if (!chunks.has((cx+1)+','+cz)) continue;
            if (!chunks.has(cx+','+(cz-1))) continue;
            if (!chunks.has(cx+','+(cz+1))) continue;

            buildChunkMesh(cx, cz);
            meshCount++;
        }
    }

    // Remove far chunks (> 7)
    const toDelete = [];
    for (const [key, chunk] of chunks) {
        const parts = key.split(',');
        const cx = parseInt(parts[0]), cz = parseInt(parts[1]);
        const dist = Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz));
        if (dist > 7) toDelete.push(key);
    }
    for (const key of toDelete) {
        const chunk = chunks.get(key);
        if (chunk.mesh) {
            scene.remove(chunk.mesh);
            chunk.mesh.geometry.dispose();
            const mi = allMeshes.indexOf(chunk.mesh);
            if (mi !== -1) allMeshes.splice(mi, 1);
        }
        chunks.delete(key);
    }
}

// --- Clouds ---
function updateClouds(dt) {
    for (const cloud of cloudGroup.children) {
        cloud.position.x += dt * 2;
        if (cloud.position.x - player.x > 100) cloud.position.x -= 200;
        if (cloud.position.x - player.x < -100) cloud.position.x += 200;
        if (cloud.position.z - player.z > 100) cloud.position.z -= 200;
        if (cloud.position.z - player.z < -100) cloud.position.z += 200;
    }
}

// --- Resize ---
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- Pre-generate initial chunks ---
for (let dx = -1; dx <= 1; dx++) {
    for (let dz = -1; dz <= 1; dz++) {
        const key = dx + ',' + dz;
        if (!chunks.has(key)) {
            chunks.set(key, { data: generateChunk(dx, dz), mesh: null });
        }
    }
}
// Build center mesh
buildChunkMesh(0, 0);

// Set player to actual terrain height
player.y = getSpawnY();

// --- Main Loop ---
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);

    if (document.pointerLockElement === canvas) {
        movePlayer(dt);
    }

    camera.position.set(player.x, player.y + EYE_H, player.z);
    camera.rotation.y = player.yaw;
    camera.rotation.x = player.pitch;

    updateChunks();

    // Target outline
    if (document.pointerLockElement === canvas) {
        const target = getTargetBlock();
        if (target) {
            outlineBox.visible = true;
            outlineBox.position.set(target.break[0] + 0.5, target.break[1] + 0.5, target.break[2] + 0.5);
        } else {
            outlineBox.visible = false;
        }
    } else {
        outlineBox.visible = false;
    }

    updateClouds(dt);
    waterPlane.position.x = player.x;
    waterPlane.position.z = player.z;

    renderer.render(scene, camera);
}

animate();

})();
</script>
</body>
</html>
```