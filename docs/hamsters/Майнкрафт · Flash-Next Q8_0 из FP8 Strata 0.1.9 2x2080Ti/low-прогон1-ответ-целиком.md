```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Minecraft</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000}
canvas{display:block}
#overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.75);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;font-family:monospace;z-index:10;cursor:pointer}
#overlay h1{font-size:52px;margin-bottom:20px;text-shadow:2px 2px 4px #000}
#overlay p{font-size:16px;margin:4px;color:#ccc}
#overlay .start{margin-top:30px;font-size:24px;color:#fff;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
#hotbar{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);display:flex;gap:3px;background:rgba(0,0,0,0.55);padding:6px;border-radius:4px;z-index:5}
.slot{width:42px;height:42px;display:flex;align-items:center;justify-content:center;color:#fff;font-family:monospace;font-weight:bold;font-size:13px;border:2px solid rgba(255,255,255,0.3);border-radius:3px;text-shadow:1px 1px 2px #000}
.slot.selected{border-color:#fff}
#crosshair{position:fixed;top:50%;left:50%;width:20px;height:20px;transform:translate(-50%,-50%);z-index:5;pointer-events:none;display:none}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:#fff}
#crosshair::before{top:50%;left:0;width:100%;height:2px;transform:translateY(-50%)}
#crosshair::after{left:50%;top:0;height:100%;width:2px;transform:translateX(-50%)}
</style>
</head>
<body>
<div id="overlay">
<h1>Minecraft</h1>
<p>WASD - Move | Space - Jump | Mouse - Look</p>
<p>Left Click - Break | Right Click - Place</p>
<p>1-7 / Scroll - Select Block</p>
<p class="start">Click to play</p>
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
const RENDER_DIST_DATA = 5;
const RENDER_DIST_MESH = 4;
const UNLOAD_DIST = 7;
const MAX_GEN_PER_FRAME = 4;
const MAX_MESH_PER_FRAME = 2;
const GRAVITY = 25;
const JUMP_VEL = 8.5;
const MOVE_SPEED = 5.5;
const PLAYER_HALF_W = 0.3;
const PLAYER_HEIGHT = 1.8;
const PLAYER_EYE = 1.62;
const REACH = 6;
const WATER_LEVEL = 14.3;

// Block colors
const BLOCK_COLORS = [
    0x000000, // 0 air
    0x4caf50, // 1 grass
    0x795548, // 2 dirt
    0x9e9e9e, // 3 stone
    0xe7d9a8, // 4 sand
    0x8d6e63, // 5 wood
    0x2e7d32, // 6 leaves
    0xffffff  // 7 snow
];

// Face definitions: [dirX, dirY, dirZ], vertices (4 corners), shade
const FACES = [
    { dir:[0,1,0], verts:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]], shade:1.0 },
    { dir:[0,-1,0], verts:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]], shade:0.55 },
    { dir:[0,0,-1], verts:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]], shade:0.8 },
    { dir:[0,0,1], verts:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]], shade:0.8 },
    { dir:[1,0,0], verts:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]], shade:0.8 },
    { dir:[-1,0,0], verts:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]], shade:0.8 }
];

// Hash functions for noise
function hash2(x, y) {
    var h = (x * 374761393 + y * 668265263) | 0;
    h = ((h ^ (h >> 13)) * 1274126177) | 0;
    h = (h ^ (h >> 16)) | 0;
    return (h & 0x7fffffff) / 0x7fffffff;
}

function hash3(x, y, z) {
    var h = (x * 374761393 + y * 668265263 + z * 1274126177) | 0;
    h = ((h ^ (h >> 13)) * 1274126177) | 0;
    h = (h ^ (h >> 16)) | 0;
    return (h & 0x7fffffff) / 0x7fffffff;
}

function smoothstep(t) {
    return t * t * (3 - 2 * t);
}

function noise2D(x, y) {
    var ix = Math.floor(x), iy = Math.floor(y);
    var fx = smoothstep(x - ix), fy = smoothstep(y - iy);
    var a = hash2(ix, iy), b = hash2(ix+1, iy), c = hash2(ix, iy+1), d = hash2(ix+1, iy+1);
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy;
}

function fractal2D(x, y) {
    var val = 0, amp = 1, freq = 1, total = 0;
    for (var i = 0; i < 4; i++) {
        val += noise2D(x * freq, y * freq) * amp;
        total += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return val / total;
}

function noise3D(x, y, z) {
    var ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    var fx = smoothstep(x - ix), fy = smoothstep(y - iy), fz = smoothstep(z - iz);
    var n000 = hash3(ix, iy, iz), n100 = hash3(ix+1, iy, iz);
    var n010 = hash3(ix, iy+1, iz), n110 = hash3(ix+1, iy+1, iz);
    var n001 = hash3(ix, iy, iz+1), n101 = hash3(ix+1, iy, iz+1);
    var n011 = hash3(ix, iy+1, iz+1), n111 = hash3(ix+1, iy+1, iz+1);
    var nx00 = n000 + (n100 - n000) * fx;
    var nx10 = n010 + (n110 - n010) * fx;
    var nx01 = n001 + (n101 - n001) * fx;
    var nx11 = n011 + (n111 - n011) * fx;
    var nxy0 = nx00 + (nx10 - nx00) * fy;
    var nxy1 = nx01 + (nx11 - nx01) * fy;
    return nxy0 + (nxy1 - nxy0) * fz;
}

function fractal3D(x, y, z) {
    var val = 0, amp = 1, freq = 1, total = 0;
    for (var i = 0; i < 4; i++) {
        val += noise3D(x * freq, y * freq, z * freq) * amp;
        total += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return val / total;
}

// Height function
function getTerrainHeight(wx, wz) {
    var m = fractal2D(wx * 0.004, wz * 0.004);
    var h = fractal2D(wx * 0.02, wz * 0.02);
    return Math.floor(5 + m * m * 58 + h * 10);
}

// Chunk storage
var chunks = new Map();
var chunkMeshes = []; // array of meshes for raycasting

function chunkKey(cx, cz) { return cx + "," + cz; }

function getChunk(cx, cz) {
    return chunks.get(chunkKey(cx, cz));
}

function createChunkData(cx, cz) {
    var data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
    var baseX = cx * CHUNK_SIZE;
    var baseZ = cz * CHUNK_SIZE;

    for (var lx = 0; lx < CHUNK_SIZE; lx++) {
        for (var lz = 0; lz < CHUNK_SIZE; lz++) {
            var wx = baseX + lx;
            var wz = baseZ + lz;
            var H = getTerrainHeight(wx, wz);
            if (H > CHUNK_HEIGHT - 1) H = CHUNK_HEIGHT - 1;
            if (H < 1) H = 1;

            for (var y = 0; y < CHUNK_HEIGHT; y++) {
                var idx = (lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + y;
                if (y === 0) {
                    data[idx] = 3; // unbreakable stone at bottom
                } else if (y <= H) {
                    if (y < H - 3) {
                        data[idx] = 3; // stone
                    } else if (y < H) {
                        // sub-surface layers
                        if (H <= 16) data[idx] = 4; // sand
                        else if (H >= 37) data[idx] = 3; // stone
                        else data[idx] = 2; // dirt
                    } else {
                        // surface
                        if (H >= 46) data[idx] = 7; // snow
                        else if (H >= 37) data[idx] = 3; // stone
                        else if (H <= 16) data[idx] = 4; // sand
                        else data[idx] = 1; // grass
                    }
                } else {
                    data[idx] = 0; // air
                }
            }

            // Caves
            for (var y = 3; y < H - 2; y++) {
                var idx2 = (lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + y;
                if (data[idx2] !== 0) {
                    if (fractal3D(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
                        data[idx2] = 0;
                    }
                }
            }
        }
    }

    // Trees
    for (var lx = 2; lx < CHUNK_SIZE - 2; lx++) {
        for (var lz = 2; lz < CHUNK_SIZE - 2; lz++) {
            var wx = baseX + lx;
            var wz = baseZ + lz;
            var H = getTerrainHeight(wx, wz);
            if (H <= 16 || H >= 37) continue; // only on grass
            var surfIdx = (lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + H;
            if (data[surfIdx] !== 1) continue; // must be grass surface
            if (hash2(wx, wz) >= 0.02) continue;
            if (H + 8 >= CHUNK_HEIGHT) continue;

            // Place trunk
            var placed = true;
            for (var ty = 1; ty <= 4; ty++) {
                var ti = (lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + H + ty;
                if (data[ti] !== 0) { placed = false; break; }
            }
            if (!placed) continue;

            for (var ty = 1; ty <= 4; ty++) {
                var ti = (lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + H + ty;
                data[ti] = 5; // wood
            }

            // Leaves: 5x5 at y=H+5 and H+6
            for (var dy = 5; dy <= 6; dy++) {
                for (var dx = -2; dx <= 2; dx++) {
                    for (var dz = -2; dz <= 2; dz++) {
                        var nlx = lx + dx, nlz = lz + dz;
                        if (nlx < 0 || nlx >= CHUNK_SIZE || nlz < 0 || nlz >= CHUNK_SIZE) continue;
                        var ni = (nlx * CHUNK_SIZE + nlz) * CHUNK_HEIGHT + H + dy;
                        if (data[ni] === 0) data[ni] = 6;
                    }
                }
            }
            // 3x3 at y=H+7
            for (var dx = -1; dx <= 1; dx++) {
                for (var dz = -1; dz <= 1; dz++) {
                    var nlx = lx + dx, nlz = lz + dz;
                    if (nlx < 0 || nlx >= CHUNK_SIZE || nlz < 0 || nlz >= CHUNK_SIZE) continue;
                    var ni = (nlx * CHUNK_SIZE + nlz) * CHUNK_HEIGHT + H + 7;
                    if (data[ni] === 0) data[ni] = 6;
                }
            }
            // 1 on top at y=H+8
            var topI = (lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + H + 8;
            if (data[topI] === 0) data[topI] = 6;
        }
    }

    return data;
}

// Global block read/write
function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= CHUNK_HEIGHT) return 0;
    var cx = Math.floor(wx / CHUNK_SIZE);
    var cz = Math.floor(wz / CHUNK_SIZE);
    var chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk || !chunk.data) return 0;
    var lx = wx - cx * CHUNK_SIZE;
    var lz = wz - cz * CHUNK_SIZE;
    return chunk.data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + wy];
}

function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= CHUNK_HEIGHT) return;
    var cx = Math.floor(wx / CHUNK_SIZE);
    var cz = Math.floor(wz / CHUNK_SIZE);
    var chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk || !chunk.data) return;
    var lx = wx - cx * CHUNK_SIZE;
    var lz = wz - cz * CHUNK_SIZE;
    chunk.data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + wy] = id;
}

// Mesh building
function buildChunkMesh(cx, cz) {
    var chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk || !chunk.data) return;

    // Remove old mesh
    if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        var idx = chunkMeshes.indexOf(chunk.mesh);
        if (idx >= 0) chunkMeshes.splice(idx, 1);
        chunk.mesh = null;
    }

    var positions = [];
    var normals = [];
    var colors = [];
    var baseX = cx * CHUNK_SIZE;
    var baseZ = cz * CHUNK_SIZE;

    for (var lx = 0; lx < CHUNK_SIZE; lx++) {
        for (var lz = 0; lz < CHUNK_SIZE; lz++) {
            for (var y = 0; y < CHUNK_HEIGHT; y++) {
                var blockId = chunk.data[(lx * CHUNK_SIZE + lz) * CHUNK_HEIGHT + y];
                if (blockId === 0) continue;

                var wx = baseX + lx;
                var wz = baseZ + lz;
                var color = BLOCK_COLORS[blockId];
                var r = ((color >> 16) & 0xff) / 255;
                var g = ((color >> 8) & 0xff) / 255;
                var b = (color & 0xff) / 255;

                for (var f = 0; f < 6; f++) {
                    var face = FACES[f];
                    var nx = wx + face.dir[0];
                    var ny = y + face.dir[1];
                    var nz = wz + face.dir[2];
                    var neighbor = getBlock(nx, ny, nz);
                    if (neighbor !== 0) continue;

                    var shade = face.shade;
                    var fr = r * shade, fg = g * shade, fb = b * shade;

                    // Add two triangles: [0,1,2] and [0,2,3]
                    var vi = [0, 1, 2, 0, 2, 3];
                    for (var t = 0; t < 6; t++) {
                        var v = face.verts[vi[t]];
                        positions.push(wx + v[0], y + v[1], wz + v[2]);
                        normals.push(face.dir[0], face.dir[1], face.dir[2]);
                        colors.push(fr, fg, fb);
                    }
                }
            }
        }
    }

    if (positions.length === 0) return;

    var geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    var mesh = new THREE.Mesh(geometry, blockMaterial);
    scene.add(mesh);
    chunk.mesh = mesh;
    chunkMeshes.push(mesh);
}

function rebuildChunk(cx, cz) {
    buildChunkMesh(cx, cz);
}

function rebuildAtBlock(wx, wy, wz) {
    var cx = Math.floor(wx / CHUNK_SIZE);
    var cz = Math.floor(wz / CHUNK_SIZE);
    var lx = wx - cx * CHUNK_SIZE;
    var lz = wz - cz * CHUNK_SIZE;

    rebuildChunk(cx, cz);

    if (lx === 0) rebuildChunk(cx - 1, cz);
    if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
    if (lz === 0) rebuildChunk(cx, cz - 1);
    if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);
}

// Three.js setup
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

// Lights
var ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambientLight);
var dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(100, 200, 80);
scene.add(dirLight);

// Block material
var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

// Water plane
var waterGeo = new THREE.PlaneGeometry(600, 600);
var waterMat = new THREE.MeshBasicMaterial({ color: 0x3388cc, transparent: true, opacity: 0.55, side: THREE.DoubleSide });
var waterPlane = new THREE.Mesh(waterGeo, waterMat);
waterPlane.rotation.x = -Math.PI / 2;
waterPlane.position.y = WATER_LEVEL;
scene.add(waterPlane);

// Clouds
var clouds = [];
for (var i = 0; i < 25; i++) {
    var cw = 8 + Math.random() * 16;
    var cd = 6 + Math.random() * 12;
    var cloudGeo = new THREE.BoxGeometry(cw, 1.5, cd);
    var cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
    var cloud = new THREE.Mesh(cloudGeo, cloudMat);
    cloud.position.set(
        (Math.random() - 0.5) * 300,
        88 + Math.random() * 6,
        (Math.random() - 0.5) * 300
    );
    cloud.userData.speed = 0.5 + Math.random() * 1.0;
    scene.add(cloud);
    clouds.push(cloud);
}

// Block outline
var outlineGeo = new THREE.BoxGeometry(1.001, 1.001, 1.001);
var outlineEdges = new THREE.EdgesGeometry(outlineGeo);
var outlineMat = new THREE.LineBasicMaterial({ color: 0x000000 });
var outlineBox = new THREE.LineSegments(outlineEdges, outlineMat);
outlineBox.visible = false;
scene.add(outlineBox);

// Player state
var player = {
    x: 8, y: 60, z: 8,
    vx: 0, vy: 0, vz: 0,
    yaw: 0, pitch: 0,
    onGround: false
};

// Compute spawn height
var spawnH = getTerrainHeight(8, 8);
player.y = spawnH + 2;

// Input state
var keys = {};
var pointerLocked = false;
var selectedSlot = 0;

// Hotbar
var hotbarEl = document.getElementById('hotbar');
var slotColors = [0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
var slotIds = [1, 2, 3, 4, 5, 6, 7];
for (var i = 0; i < 7; i++) {
    var slot = document.createElement('div');
    slot.className = 'slot' + (i === 0 ? ' selected' : '');
    slot.style.backgroundColor = '#' + slotColors[i].toString(16).padStart(6, '0');
    slot.textContent = (i + 1);
    hotbarEl.appendChild(slot);
}

function selectSlot(n) {
    if (n < 0) n = 6;
    if (n > 6) n = 0;
    selectedSlot = n;
    var slots = hotbarEl.querySelectorAll('.slot');
    for (var i = 0; i < 7; i++) {
        slots[i].className = 'slot' + (i === selectedSlot ? ' selected' : '');
    }
}

// Pointer lock
var overlay = document.getElementById('overlay');
var crosshair = document.getElementById('crosshair');

overlay.addEventListener('click', function() {
    renderer.domElement.requestPointerLock();
});

document.addEventListener('pointerlockchange', function() {
    pointerLocked = document.pointerLockElement === renderer.domElement;
    overlay.style.display = pointerLocked ? 'none' : 'flex';
    crosshair.style.display = pointerLocked ? 'block' : 'none';
});

// Mouse look
document.addEventListener('mousemove', function(e) {
    if (!pointerLocked) return;
    player.yaw -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    if (player.pitch > Math.PI / 2 - 0.01) player.pitch = Math.PI / 2 - 0.01;
    if (player.pitch < -Math.PI / 2 + 0.01) player.pitch = -Math.PI / 2 + 0.01;
});

// Keyboard
document.addEventListener('keydown', function(e) {
    keys[e.code] = true;
    if (e.code >= 'Digit1' && e.code <= 'Digit7') {
        selectSlot(parseInt(e.code.charAt(5)) - 1);
    }
});
document.addEventListener('keyup', function(e) { keys[e.code] = false; });

// Mouse wheel for hotbar
document.addEventListener('wheel', function(e) {
    if (!pointerLocked) return;
    if (e.deltaY > 0) selectSlot(selectedSlot + 1);
    else selectSlot(selectedSlot - 1);
});

// Suppress context menu
document.addEventListener('contextmenu', function(e) { e.preventDefault(); });

// Raycaster
var raycaster = new THREE.Raycaster();
raycaster.far = REACH;
var centerVec = new THREE.Vector2(0, 0);

// Break and place
document.addEventListener('mousedown', function(e) {
    if (!pointerLocked) return;
    
    raycaster.setFromCamera(centerVec, camera);
    var intersects = raycaster.intersectObjects(chunkMeshes);
    if (intersects.length === 0) return;

    var hit = intersects[0];
    var p = hit.point;
    var n = hit.face.normal;

    var breakX = Math.floor(p.x - n.x * 0.5);
    var breakY = Math.floor(p.y - n.y * 0.5);
    var breakZ = Math.floor(p.z - n.z * 0.5);

    if (e.button === 0) { // Left click - break
        if (breakY === 0) return; // unbreakable bottom layer
        if (getBlock(breakX, breakY, breakZ) === 0) return;
        setBlock(breakX, breakY, breakZ, 0);
        rebuildAtBlock(breakX, breakY, breakZ);
    } else if (e.button === 2) { // Right click - place
        var placeX = Math.floor(p.x + n.x * 0.5);
        var placeY = Math.floor(p.y + n.y * 0.5);
        var placeZ = Math.floor(p.z + n.z * 0.5);

        if (getBlock(placeX, placeY, placeZ) !== 0) return;
        if (placeY < 0 || placeY >= CHUNK_HEIGHT) return;

        // Check player overlap
        var px = player.x, py = player.y, pz = player.z;
        if (px + PLAYER_HALF_W > placeX && px - PLAYER_HALF_W < placeX + 1 &&
            py + PLAYER_HEIGHT > placeY && py < placeY + 1 &&
            pz + PLAYER_HALF_W > placeZ && pz - PLAYER_HALF_W < placeZ + 1) {
            return;
        }

        setBlock(placeX, placeY, placeZ, slotIds[selectedSlot]);
        rebuildAtBlock(placeX, placeY, placeZ);
    }
});

// Collision detection
function collides(px, py, pz) {
    var minX = Math.floor(px - PLAYER_HALF_W);
    var maxX = Math.floor(px + PLAYER_HALF_W);
    var minY = Math.floor(py);
    var maxY = Math.floor(py + PLAYER_HEIGHT);
    var minZ = Math.floor(pz - PLAYER_HALF_W);
    var maxZ = Math.floor(pz + PLAYER_HALF_W);

    for (var bx = minX; bx <= maxX; bx++) {
        for (var by = minY; by <= maxY; by++) {
            for (var bz = minZ; bz <= maxZ; bz++) {
                if (getBlock(bx, by, bz) !== 0) {
                    // AABB overlap check
                    if (px - PLAYER_HALF_W < bx + 1 && px + PLAYER_HALF_W > bx &&
                        py < by + 1 && py + PLAYER_HEIGHT > by &&
                        pz - PLAYER_HALF_W < bz + 1 && pz + PLAYER_HALF_W > bz) {
                        return true;
                    }
                }
            }
        }
    }
    return false;
}

// Update chunk loading/unloading
function updateChunks() {
    var pcx = Math.floor(player.x / CHUNK_SIZE);
    var pcz = Math.floor(player.z / CHUNK_SIZE);

    // Generate data
    var genCount = 0;
    for (var dx = -RENDER_DIST_DATA; dx <= RENDER_DIST_DATA && genCount < MAX_GEN_PER_FRAME; dx++) {
        for (var dz = -RENDER_DIST_DATA; dz <= RENDER_DIST_DATA && genCount < MAX_GEN_PER_FRAME; dz++) {
            var cx = pcx + dx, cz = pcz + dz;
            var key = chunkKey(cx, cz);
            if (!chunks.has(key)) {
                chunks.set(key, { data: createChunkData(cx, cz), mesh: null });
                genCount++;
            }
        }
    }

    // Build meshes
    var meshCount = 0;
    for (var dx = -RENDER_DIST_MESH; dx <= RENDER_DIST_MESH && meshCount < MAX_MESH_PER_FRAME; dx++) {
        for (var dz = -RENDER_DIST_MESH; dz <= RENDER_DIST_MESH && meshCount < MAX_MESH_PER_FRAME; dz++) {
            var cx = pcx + dx, cz = pcz + dz;
            var key = chunkKey(cx, cz);
            var chunk = chunks.get(key);
            if (!chunk || !chunk.data || chunk.mesh) continue;
            // Check all 4 neighbors have data
            var n1 = chunks.get(chunkKey(cx-1, cz));
            var n2 = chunks.get(chunkKey(cx+1, cz));
            var n3 = chunks.get(chunkKey(cx, cz-1));
            var n4 = chunks.get(chunkKey(cx, cz+1));
            if (n1 && n1.data && n2 && n2.data && n3 && n3.data && n4 && n4.data) {
                buildChunkMesh(cx, cz);
                meshCount++;
            }
        }
    }

    // Unload far chunks
    var toRemove = [];
    chunks.forEach(function(chunk, key) {
        var parts = key.split(',');
        var cx = parseInt(parts[0]), cz = parseInt(parts[1]);
        var dist = Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz));
        if (dist > UNLOAD_DIST) {
            toRemove.push(key);
        }
    });
    for (var i = 0; i < toRemove.length; i++) {
        var chunk = chunks.get(toRemove[i]);
        if (chunk.mesh) {
            scene.remove(chunk.mesh);
            chunk.mesh.geometry.dispose();
            var idx = chunkMeshes.indexOf(chunk.mesh);
            if (idx >= 0) chunkMeshes.splice(idx, 1);
        }
        chunks.delete(toRemove[i]);
    }
}

// Game loop
var lastTime = performance.now();

function update() {
    requestAnimationFrame(update);

    var now = performance.now();
    var dt = (now - lastTime) / 1000;
    if (dt > 0.1) dt = 0.1;
    lastTime = now;

    // Movement
    var moveX = 0, moveZ = 0;
    if (keys['KeyW']) { moveX -= Math.sin(player.yaw); moveZ -= Math.cos(player.yaw); }
    if (keys['KeyS']) { moveX += Math.sin(player.yaw); moveZ += Math.cos(player.yaw); }
    if (keys['KeyA']) { moveX -= Math.cos(player.yaw); moveZ += Math.sin(player.yaw); }
    if (keys['KeyD']) { moveX += Math.cos(player.yaw); moveZ -= Math.sin(player.yaw); }

    var len = Math.sqrt(moveX * moveX + moveZ * moveZ);
    if (len > 0) { moveX /= len; moveZ /= len; }

    player.vx = moveX * MOVE_SPEED;
    player.vz = moveZ * MOVE_SPEED;

    // Gravity
    player.vy -= GRAVITY * dt;
    if (player.vy < -50) player.vy = -50;

    // Jump
    if (keys['Space'] && player.onGround) {
        player.vy = JUMP_VEL;
        player.onGround = false;
    }

    // Move X
    var newX = player.x + player.vx * dt;
    if (!collides(newX, player.y, player.z)) {
        player.x = newX;
    } else {
        player.vx = 0;
    }

    // Move Y
    var newY = player.y + player.vy * dt;
    if (!collides(player.x, newY, player.z)) {
        player.y = newY;
        player.onGround = false;
    } else {
        if (player.vy < 0) player.onGround = true;
        player.vy = 0;
    }

    // Move Z
    var newZ = player.z + player.vz * dt;
    if (!collides(player.x, player.y, newZ)) {
        player.z = newZ;
    } else {
        player.vz = 0;
    }

    // Fall below world
    if (player.y < -20) {
        player.x = 8;
        player.y = getTerrainHeight(8, 8) + 2;
        player.z = 8;
        player.vy = 0;
    }

    // Camera
    camera.position.set(player.x, player.y + PLAYER_EYE, player.z);
    camera.rotation.set(player.pitch, player.yaw, 0);

    // Update chunks
    updateChunks();

    // Water follows player
    waterPlane.position.x = player.x;
    waterPlane.position.z = player.z;

    // Clouds
    for (var i = 0; i < clouds.length; i++) {
        var c = clouds[i];
        c.position.x += c.userData.speed * dt;
        // Wrap around player
        if (c.position.x > player.x + 200) c.position.x -= 400;
        if (c.position.x < player.x - 200) c.position.x += 400;
        if (c.position.z > player.z + 200) c.position.z -= 400;
        if (c.position.z < player.z - 200) c.position.z += 400;
    }

    // Block outline
    if (pointerLocked) {
        raycaster.setFromCamera(centerVec, camera);
        var intersects = raycaster.intersectObjects(chunkMeshes);
        if (intersects.length > 0) {
            var hit = intersects[0];
            var p = hit.point;
            var n = hit.face.normal;
            var bx = Math.floor(p.x - n.x * 0.5);
            var by = Math.floor(p.y - n.y * 0.5);
            var bz = Math.floor(p.z - n.z * 0.5);
            outlineBox.position.set(bx + 0.5, by + 0.5, bz + 0.5);
            outlineBox.visible = true;
        } else {
            outlineBox.visible = false;
        }
    } else {
        outlineBox.visible = false;
    }

    renderer.render(scene, camera);
}

// Resize
window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

update();

})();
</script>
</body>
</html>
```