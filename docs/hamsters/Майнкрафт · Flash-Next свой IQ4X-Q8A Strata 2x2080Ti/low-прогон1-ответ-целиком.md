```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MC Voxel</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: #000; }
canvas { display: block; }
#overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7); display: flex; flex-direction: column;
    align-items: center; justify-content: center; z-index: 100;
    color: #fff; font-family: monospace; font-size: 16px; cursor: pointer;
}
#overlay h1 { font-size: 48px; margin-bottom: 20px; color: #4caf50; }
#overlay ul { list-style: none; margin-bottom: 20px; text-align: left; }
#overlay li { margin: 4px 0; }
#overlay .start { font-size: 24px; color: #ffeb3b; }
#hotbar {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; padding: 6px; background: rgba(0,0,0,0.6);
    border-radius: 6px; z-index: 50;
}
.slot {
    width: 40px; height: 40px; border: 2px solid #555; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-family: monospace; font-size: 12px; font-weight: bold;
    text-shadow: 1px 1px 1px #000;
}
.slot.sel { border-color: #fff; }
#crosshair {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 20px; height: 20px; z-index: 50; pointer-events: none;
}
#crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: rgba(255,255,255,0.8);
}
#crosshair::before { width: 2px; height: 20px; left: 9px; top: 0; }
#crosshair::after { width: 20px; height: 2px; top: 9px; left: 0; }
</style>
</head>
<body>
<div id="overlay">
    <h1>MC Voxel</h1>
    <ul>
        <li>WASD – Move</li>
        <li>Space – Jump</li>
        <li>Mouse – Look</li>
        <li>Left Click – Break block</li>
        <li>Right Click – Place block</li>
        <li>1-7 / Scroll – Select block</li>
    </ul>
    <div class="start">Click to play</div>
</div>
<div id="hotbar"></div>
<div id="crosshair"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// Constants
const CHUNK_SIZE = 16;
const CHUNK_HEIGHT = 80;
const RENDER_DIST = 4;
const GEN_DIST = 5;
const CLEANUP_DIST = 7;
const GRAVITY = 25;
const JUMP_VEL = 8.5;
const MOVE_SPEED = 5.5;
const PLAYER_HW = 0.3;
const PLAYER_H = 1.8;
const EYE_HEIGHT = 1.62;
const REACH = 6;
const WATER_LEVEL = 14.3;

const BLOCK_COLORS = [0, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
const BLOCK_NAMES = ['Air','Grass','Dirt','Stone','Sand','Wood','Leaves','Snow'];

// Face definitions
const FACES = [
    { dir:[1,0,0],  corners:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]], light:0.8 },
    { dir:[-1,0,0], corners:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]], light:0.8 },
    { dir:[0,1,0],  corners:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]], light:1.0 },
    { dir:[0,-1,0], corners:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]], light:0.55 },
    { dir:[0,0,1],  corners:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]], light:0.8 },
    { dir:[0,0,-1], corners:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]], light:0.8 }
];

// Noise
function hash2D(x, y) {
    let h = (x * 374761393 + y * 668265263) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    h = h ^ (h >>> 16);
    return (h & 0x7fffffff) / 0x7fffffff;
}

function hash3D(x, y, z) {
    let h = (x * 374761393 + y * 668265263 + z * 1274126177) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    h = h ^ (h >>> 16);
    return (h & 0x7fffffff) / 0x7fffffff;
}

function smoothstep(t) { return t * t * (3 - 2 * t); }

function noise2D(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const sx = smoothstep(fx), sy = smoothstep(fy);
    const n00 = hash2D(ix, iy);
    const n10 = hash2D(ix + 1, iy);
    const n01 = hash2D(ix, iy + 1);
    const n11 = hash2D(ix + 1, iy + 1);
    const nx0 = n00 + (n10 - n00) * sx;
    const nx1 = n01 + (n11 - n01) * sx;
    return nx0 + (nx1 - nx0) * sy;
}

function noise3D(x, y, z) {
    const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    const fx = x - ix, fy = y - iy, fz = z - iz;
    const sx = smoothstep(fx), sy = smoothstep(fy), sz = smoothstep(fz);
    const n000 = hash3D(ix, iy, iz);
    const n100 = hash3D(ix+1, iy, iz);
    const n010 = hash3D(ix, iy+1, iz);
    const n110 = hash3D(ix+1, iy+1, iz);
    const n001 = hash3D(ix, iy, iz+1);
    const n101 = hash3D(ix+1, iy, iz+1);
    const n011 = hash3D(ix, iy+1, iz+1);
    const n111 = hash3D(ix+1, iy+1, iz+1);
    const nx00 = n000 + (n100 - n000) * sx;
    const nx10 = n010 + (n110 - n010) * sx;
    const nx01 = n001 + (n101 - n001) * sx;
    const nx11 = n011 + (n111 - n011) * sx;
    const nxy0 = nx00 + (nx10 - nx00) * sy;
    const nxy1 = nx01 + (nx11 - nx01) * sy;
    return nxy0 + (nxy1 - nxy0) * sz;
}

function fractal2D(x, y) {
    let val = 0, amp = 1, freq = 1, total = 0;
    for (let i = 0; i < 4; i++) {
        val += noise2D(x * freq, y * freq) * amp;
        total += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return val / total;
}

function getHeight(wx, wz) {
    const m = fractal2D(wx * 0.004, wz * 0.004);
    const h = fractal2D(wx * 0.02, wz * 0.02);
    return Math.floor(5 + m * m * 58 + h * 10);
}

// World storage
const chunks = new Map();
let meshList = [];

function chunkKey(cx, cz) { return cx + ',' + cz; }

function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= CHUNK_HEIGHT) return 0;
    const cx = Math.floor(wx / CHUNK_SIZE);
    const cz = Math.floor(wz / CHUNK_SIZE);
    const chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk || !chunk.data) return 0;
    const lx = wx - cx * CHUNK_SIZE;
    const lz = wz - cz * CHUNK_SIZE;
    return chunk.data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + wy];
}

function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= CHUNK_HEIGHT) return;
    const cx = Math.floor(wx / CHUNK_SIZE);
    const cz = Math.floor(wz / CHUNK_SIZE);
    const chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk || !chunk.data) return;
    const lx = wx - cx * CHUNK_SIZE;
    const lz = wz - cz * CHUNK_SIZE;
    chunk.data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + wy] = id;
}

function generateChunk(cx, cz) {
    const key = chunkKey(cx, cz);
    if (chunks.has(key) && chunks.get(key).data) return;
    const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
    
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
        for (let lz = 0; lz < CHUNK_SIZE; lz++) {
            const wx = cx * CHUNK_SIZE + lx;
            const wz = cz * CHUNK_SIZE + lz;
            const H = getHeight(wx, wz);
            
            for (let y = 0; y < CHUNK_HEIGHT; y++) {
                let block = 0;
                if (y === 0) {
                    block = 3;
                } else if (y <= H) {
                    if (y < H - 3) {
                        block = 3;
                    } else if (y < H) {
                        if (H <= 16) block = 4;
                        else if (H >= 37) block = 3;
                        else block = 2;
                    } else {
                        if (H >= 46) block = 7;
                        else if (H >= 37) block = 3;
                        else if (H <= 16) block = 4;
                        else block = 1;
                    }
                }
                
                if (y >= 3 && y <= H - 2 && block !== 0) {
                    if (noise3D(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
                        block = 0;
                    }
                }
                
                data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + y] = block;
            }
            
            // Trees
            if (H > 16 && H < 37) {
                const th = hash2D(wx * 7 + 13, wz * 13 + 7);
                if (th < 0.02 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13) {
                    for (let ty = H + 1; ty <= H + 4 && ty < CHUNK_HEIGHT; ty++) {
                        data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + ty] = 5;
                    }
                    for (let dy = 3; dy <= 4; dy++) {
                        for (let dx = -2; dx <= 2; dx++) {
                            for (let dz = -2; dz <= 2; dz++) {
                                const ny = H + dy;
                                const nlx = lx + dx, nlz = lz + dz;
                                if (ny < CHUNK_HEIGHT && nlx >= 0 && nlx < CHUNK_SIZE && nlz >= 0 && nlz < CHUNK_SIZE) {
                                    const idx = (nlx * CHUNK_SIZE + nlz) * CHUNK_HEIGHT + ny;
                                    if (data[idx] === 0) data[idx] = 6;
                                }
                            }
                        }
                    }
                    for (let dx = -1; dx <= 1; dx++) {
                        for (let dz = -1; dz <= 1; dz++) {
                            const ny = H + 5;
                            const nlx = lx + dx, nlz = lz + dz;
                            if (ny < CHUNK_HEIGHT && nlx >= 0 && nlx < CHUNK_SIZE && nlz >= 0 && nlz < CHUNK_SIZE) {
                                const idx = (nlx * CHUNK_SIZE + nlz) * CHUNK_HEIGHT + ny;
                                if (data[idx] === 0) data[idx] = 6;
                            }
                        }
                    }
                    const ny = H + 6;
                    if (ny < CHUNK_HEIGHT) {
                        const idx = (lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + ny;
                        if (data[idx] === 0) data[idx] = 6;
                    }
                }
            }
        }
    }
    
    if (!chunks.has(key)) chunks.set(key, { data: data, mesh: null });
    else chunks.get(key).data = data;
}

function buildChunkMesh(cx, cz) {
    const key = chunkKey(cx, cz);
    const chunk = chunks.get(key);
    if (!chunk || !chunk.data) return;
    
    const positions = [];
    const normals = [];
    const colors = [];
    
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
        for (let lz = 0; lz < CHUNK_SIZE; lz++) {
            const wx = cx * CHUNK_SIZE + lx;
            const wz = cz * CHUNK_SIZE + lz;
            for (let y = 0; y < CHUNK_HEIGHT; y++) {
                const block = chunk.data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + y];
                if (block === 0) continue;
                
                const color = BLOCK_COLORS[block];
                const br = ((color >> 16) & 0xff) / 255;
                const bg = ((color >> 8) & 0xff) / 255;
                const bb = (color & 0xff) / 255;
                
                for (let f = 0; f < 6; f++) {
                    const face = FACES[f];
                    const nx = wx + face.dir[0];
                    const ny = y + face.dir[1];
                    const nz = wz + face.dir[2];
                    
                    if (getBlock(nx, ny, nz) !== 0) continue;
                    
                    const light = face.light;
                    const cr = br * light;
                    const cg = bg * light;
                    const cb = bb * light;
                    
                    const c = face.corners;
                    const tri = [0,1,2,0,2,3];
                    for (let i = 0; i < 6; i++) {
                        const ci = tri[i];
                        positions.push(wx + c[ci][0], y + c[ci][1], wz + c[ci][2]);
                        normals.push(face.dir[0], face.dir[1], face.dir[2]);
                        colors.push(cr, cg, cb);
                    }
                }
            }
        }
    }
    
    if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        chunk.mesh = null;
    }
    
    if (positions.length === 0) return;
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    chunk.mesh = mesh;
}

function rebuildChunk(cx, cz) {
    buildChunkMesh(cx, cz);
    updateMeshList();
}

function updateMeshList() {
    meshList = [];
    chunks.forEach(function(chunk) {
        if (chunk.mesh) meshList.push(chunk.mesh);
    });
}

function onBlockChanged(wx, wy, wz) {
    const cx = Math.floor(wx / CHUNK_SIZE);
    const cz = Math.floor(wz / CHUNK_SIZE);
    rebuildChunk(cx, cz);
    const lx = wx - cx * CHUNK_SIZE;
    const lz = wz - cz * CHUNK_SIZE;
    if (lx === 0) rebuildChunk(cx - 1, cz);
    if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
    if (lz === 0) rebuildChunk(cx, cz - 1);
    if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);
}

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(0.5, 1, 0.3);
scene.add(dirLight);

const material = new THREE.MeshLambertMaterial({ vertexColors: true });

// Outline
const outlineGeo = new THREE.BoxGeometry(1.001, 1.001, 1.001);
const outlineEdges = new THREE.EdgesGeometry(outlineGeo);
const outlineMat = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });
const outlineMesh = new THREE.LineSegments(outlineEdges, outlineMat);
outlineMesh.visible = false;
scene.add(outlineMesh);

// Water plane
const waterGeo = new THREE.PlaneGeometry(500, 500);
const waterMat = new THREE.MeshLambertMaterial({ color: 0x3399ff, transparent: true, opacity: 0.5 });
const waterMesh = new THREE.Mesh(waterGeo, waterMat);
waterMesh.rotation.x = -Math.PI / 2;
waterMesh.position.y = WATER_LEVEL;
scene.add(waterMesh);

// Clouds
const clouds = [];
const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
for (let i = 0; i < 25; i++) {
    const w = 10 + hash2D(i * 3, 7) * 20;
    const d = 8 + hash2D(i * 5, 11) * 15;
    const geo = new THREE.BoxGeometry(w, 2, d);
    const mesh = new THREE.Mesh(geo, cloudMat);
    mesh.position.set(
        (hash2D(i, 1) - 0.5) * 300,
        88 + hash2D(i, 2) * 4,
        (hash2D(i, 3) - 0.5) * 300
    );
    scene.add(mesh);
    clouds.push(mesh);
}

// Player state
let playerX = 8, playerZ = 8;
let playerY = getHeight(8, 8) + 3;
let velY = 0;
let yaw = 0, pitch = 0;
let onGround = false;
let selectedSlot = 0;
let pointerLocked = false;

const keys = {};
document.addEventListener('keydown', function(e) { keys[e.code] = true; });
document.addEventListener('keyup', function(e) { keys[e.code] = false; });

// Hotbar
const hotbarEl = document.getElementById('hotbar');
const slotColors = [0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
for (let i = 0; i < 7; i++) {
    const slot = document.createElement('div');
    slot.className = 'slot' + (i === 0 ? ' sel' : '');
    slot.style.background = '#' + slotColors[i].toString(16).padStart(6, '0');
    slot.textContent = (i + 1);
    hotbarEl.appendChild(slot);
}

function selectSlot(idx) {
    selectedSlot = ((idx % 7) + 7) % 7;
    const slots = hotbarEl.querySelectorAll('.slot');
    for (let i = 0; i < 7; i++) {
        slots[i].className = 'slot' + (i === selectedSlot ? ' sel' : '');
    }
}

// Pointer lock
const overlay = document.getElementById('overlay');
overlay.addEventListener('click', function() {
    renderer.domElement.requestPointerLock();
});

document.addEventListener('pointerlockchange', function() {
    pointerLocked = document.pointerLockElement === renderer.domElement;
    overlay.style.display = pointerLocked ? 'none' : 'flex';
});

document.addEventListener('mousemove', function(e) {
    if (!pointerLocked) return;
    yaw -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;
    pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, pitch));
});

document.addEventListener('wheel', function(e) {
    if (!pointerLocked) return;
    selectSlot(selectedSlot + (e.deltaY > 0 ? 1 : -1));
});

document.addEventListener('keydown', function(e) {
    if (e.code >= 'Digit1' && e.code <= 'Digit7') {
        selectSlot(parseInt(e.code.charAt(5)) - 1);
    }
});

document.addEventListener('contextmenu', function(e) { e.preventDefault(); });

// Raycaster
const raycaster = new THREE.Raycaster();
raycaster.far = REACH;
const center = new THREE.Vector2(0, 0);

let targetBlock = null;
let placeBlock = null;

function doRaycast() {
    raycaster.setFromCamera(center, camera);
    const intersects = raycaster.intersectObjects(meshList);
    targetBlock = null;
    placeBlock = null;
    outlineMesh.visible = false;
    
    if (intersects.length > 0) {
        const hit = intersects[0];
        const p = hit.point;
        const n = hit.face.normal;
        
        const bx = Math.floor(p.x - n.x * 0.5);
        const by = Math.floor(p.y - n.y * 0.5);
        const bz = Math.floor(p.z - n.z * 0.5);
        
        const px = Math.floor(p.x + n.x * 0.5);
        const py = Math.floor(p.y + n.y * 0.5);
        const pz = Math.floor(p.z + n.z * 0.5);
        
        targetBlock = { x: bx, y: by, z: bz };
        placeBlock = { x: px, y: py, z: pz };
        
        outlineMesh.position.set(bx + 0.5, by + 0.5, bz + 0.5);
        outlineMesh.visible = true;
    }
}

document.addEventListener('mousedown', function(e) {
    if (!pointerLocked) return;
    
    if (e.button === 0) {
        // Break
        if (targetBlock && targetBlock.y > 0) {
            setBlock(targetBlock.x, targetBlock.y, targetBlock.z, 0);
            onBlockChanged(targetBlock.x, targetBlock.y, targetBlock.z);
        }
    } else if (e.button === 2) {
        // Place
        if (placeBlock) {
            const bx = placeBlock.x, by = placeBlock.y, bz = placeBlock.z;
            if (by >= 0 && by < CHUNK_HEIGHT && getBlock(bx, by, bz) === 0) {
                // Check overlap with player
                if (!(bx + 1 > playerX - PLAYER_HW && bx < playerX + PLAYER_HW &&
                      by + 1 > playerY && by < playerY + PLAYER_H &&
                      bz + 1 > playerZ - PLAYER_HW && bz < playerZ + PLAYER_HW)) {
                    setBlock(bx, by, bz, selectedSlot + 1);
                    onBlockChanged(bx, by, bz);
                }
            }
        }
    }
});

// Collision
function collides(px, py, pz) {
    const minX = Math.floor(px - PLAYER_HW);
    const maxX = Math.floor(px + PLAYER_HW);
    const minY = Math.floor(py);
    const maxY = Math.floor(py + PLAYER_H - 0.001);
    const minZ = Math.floor(pz - PLAYER_HW);
    const maxZ = Math.floor(pz + PLAYER_HW);
    
    for (let x = minX; x <= maxX; x++) {
        for (let y = minY; y <= maxY; y++) {
            for (let z = minZ; z <= maxZ; z++) {
                if (getBlock(x, y, z) !== 0) return true;
            }
        }
    }
    return false;
}

// Chunk management
let genQueue = [];
let meshQueue = [];

function updateChunks() {
    const pcx = Math.floor(playerX / CHUNK_SIZE);
    const pcz = Math.floor(playerZ / CHUNK_SIZE);
    
    // Build generation queue
    genQueue = [];
    for (let dx = -GEN_DIST; dx <= GEN_DIST; dx++) {
        for (let dz = -GEN_DIST; dz <= GEN_DIST; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = chunkKey(cx, cz);
            if (!chunks.has(key) || !chunks.get(key).data) {
                genQueue.push([cx, cz]);
            }
        }
    }
    genQueue.sort(function(a, b) {
        const da = (a[0]-pcx)*(a[0]-pcx) + (a[1]-pcz)*(a[1]-pcz);
        const db = (b[0]-pcx)*(b[0]-pcx) + (b[1]-pcz)*(b[1]-pcz);
        return da - db;
    });
    
    // Build mesh queue
    meshQueue = [];
    for (let dx = -RENDER_DIST; dx <= RENDER_DIST; dx++) {
        for (let dz = -RENDER_DIST; dz <= RENDER_DIST; dz++) {
            const cx = pcx + dx, cz = pcz + dz;
            const key = chunkKey(cx, cz);
            const chunk = chunks.get(key);
            if (!chunk || !chunk.data) continue;
            if (chunk.mesh) continue;
            // Check 4 neighbors have data
            const n1 = chunks.get(chunkKey(cx-1, cz));
            const n2 = chunks.get(chunkKey(cx+1, cz));
            const n3 = chunks.get(chunkKey(cx, cz-1));
            const n4 = chunks.get(chunkKey(cx, cz+1));
            if (n1 && n1.data && n2 && n2.data && n3 && n3.data && n4 && n4.data) {
                meshQueue.push([cx, cz]);
            }
        }
    }
    meshQueue.sort(function(a, b) {
        const da = (a[0]-pcx)*(a[0]-pcx) + (a[1]-pcz)*(a[1]-pcz);
        const db = (b[0]-pcx)*(b[0]-pcx) + (b[1]-pcz)*(b[1]-pcz);
        return da - db;
    });
    
    // Process generation (max 4)
    for (let i = 0; i < Math.min(4, genQueue.length); i++) {
        generateChunk(genQueue[i][0], genQueue[i][1]);
    }
    
    // Process meshing (max 2)
    for (let i = 0; i < Math.min(2, meshQueue.length); i++) {
        buildChunkMesh(meshQueue[i][0], meshQueue[i][1]);
    }
    updateMeshList();
    
    // Cleanup far chunks
    const toDelete = [];
    chunks.forEach(function(chunk, key) {
        const parts = key.split(',');
        const cx = parseInt(parts[0]), cz = parseInt(parts[1]);
        const dist = Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz));
        if (dist > CLEANUP_DIST) {
            if (chunk.mesh) {
                scene.remove(chunk.mesh);
                chunk.mesh.geometry.dispose();
            }
            toDelete.push(key);
        }
    });
    for (let i = 0; i < toDelete.length; i++) {
        chunks.delete(toDelete[i]);
    }
    if (toDelete.length > 0) updateMeshList();
}

// Game loop
let lastTime = performance.now();
let chunkTimer = 0;

function update(dt) {
    // Movement
    let mx = 0, mz = 0;
    if (keys['KeyW']) { mx -= Math.sin(yaw); mz -= Math.cos(yaw); }
    if (keys['KeyS']) { mx += Math.sin(yaw); mz += Math.cos(yaw); }
    if (keys['KeyA']) { mx -= Math.cos(yaw); mz += Math.sin(yaw); }
    if (keys['KeyD']) { mx += Math.cos(yaw); mz -= Math.sin(yaw); }
    
    const len = Math.sqrt(mx * mx + mz * mz);
    if (len > 0) { mx = mx / len * MOVE_SPEED; mz = mz / len * MOVE_SPEED; }
    
    // Gravity
    velY -= GRAVITY * dt;
    if (keys['Space'] && onGround) {
        velY = JUMP_VEL;
        onGround = false;
    }
    
    // Move X
    const newX = playerX + mx * dt;
    if (!collides(newX, playerY, playerZ)) {
        playerX = newX;
    }
    
    // Move Z
    const newZ = playerZ + mz * dt;
    if (!collides(playerX, playerY, newZ)) {
        playerZ = newZ;
    }
    
    // Move Y
    const newY = playerY + velY * dt;
    if (!collides(playerX, newY, playerZ)) {
        playerY = newY;
        onGround = false;
    } else {
        if (velY < 0) onGround = true;
        velY = 0;
    }
    
    // Fall below -20
    if (playerY < -20) {
        playerX = 8; playerZ = 8;
        playerY = getHeight(8, 8) + 3;
        velY = 0;
    }
    
    // Camera
    camera.position.set(playerX, playerY + EYE_HEIGHT, playerZ);
    camera.rotation.set(pitch, yaw, 0);
    
    // Water follows player
    waterMesh.position.x = playerX;
    waterMesh.position.z = playerZ;
    
    // Clouds drift
    for (let i = 0; i < clouds.length; i++) {
        clouds[i].position.x += dt * 1.5;
        // Wrap around player
        const dx = clouds[i].position.x - playerX;
        const dz = clouds[i].position.z - playerZ;
        if (dx > 150) clouds[i].position.x -= 300;
        if (dx < -150) clouds[i].position.x += 300;
        if (dz > 150) clouds[i].position.z -= 300;
        if (dz < -150) clouds[i].position.z += 300;
    }
    
    // Chunk updates
    chunkTimer += dt;
    if (chunkTimer > 0.1) {
        chunkTimer = 0;
        updateChunks();
    }
    
    // Raycast
    doRaycast();
}

function loop() {
    requestAnimationFrame(loop);
    const now = performance.now();
    let dt = (now - lastTime) / 1000;
    lastTime = now;
    if (dt > 0.1) dt = 0.1;
    
    update(dt);
    renderer.render(scene, camera);
}

// Resize
window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Initial chunk generation around spawn
(function initWorld() {
    const pcx = Math.floor(8 / CHUNK_SIZE);
    const pcz = Math.floor(8 / CHUNK_SIZE);
    for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
            generateChunk(pcx + dx, pcz + dz);
        }
    }
    for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
            buildChunkMesh(pcx + dx, pcz + dz);
        }
    }
    updateMeshList();
    playerY = getHeight(8, 8) + 2;
})();

loop();

})();
</script>
</body>
</html>
```