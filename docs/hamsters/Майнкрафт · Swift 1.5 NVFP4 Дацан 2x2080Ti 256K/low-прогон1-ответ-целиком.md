```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MC Voxel</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #000; font-family: sans-serif; }
canvas { display: block; }
#overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7); display: flex; align-items: center;
    justify-content: center; z-index: 100; cursor: pointer;
}
#overlay .panel {
    background: rgba(30,30,30,0.95); padding: 40px 60px; border-radius: 8px;
    text-align: center; color: #fff;
}
#overlay h1 { font-size: 48px; margin-bottom: 20px; color: #4caf50; }
#overlay p { font-size: 16px; line-height: 1.8; color: #ccc; }
#overlay .click { margin-top: 20px; font-size: 20px; color: #fff; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
#crosshair {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    z-index: 50; pointer-events: none;
}
#crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: #fff;
}
#crosshair::before { width: 2px; height: 16px; left: -1px; top: -8px; }
#crosshair::after { width: 16px; height: 2px; left: -8px; top: -1px; }
#hotbar {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; z-index: 50; background: rgba(0,0,0,0.6);
    padding: 6px; border-radius: 6px;
}
.slot {
    width: 48px; height: 48px; border: 2px solid #555; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; color: #fff; font-weight: bold; position: relative;
}
.slot.selected { border-color: #fff; border-width: 3px; }
.slot span { position: absolute; top: 2px; left: 4px; font-size: 10px; text-shadow: 1px 1px 1px #000; }
</style>
</head>
<body>
<div id="overlay">
<div class="panel">
<h1>MC Voxel</h1>
<p>WASD – Move &nbsp;|&nbsp; Space – Jump<br>
Left Click – Break Block &nbsp;|&nbsp; Right Click – Place Block<br>
Mouse Wheel / Keys 1-7 – Select Block<br>
Mouse – Look Around</p>
<div class="click">Click to Play</div>
</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){

// === NOISE ===
function hash2(x, y) {
    var n = (x * 374761393 + y * 668265263) | 0;
    n = ((n ^ (n >>> 13)) * 1274126177) | 0;
    n = n ^ (n >>> 16);
    return (n & 0x7fffffff) / 0x7fffffff;
}

function hash3(x, y, z) {
    var n = (x * 374761393 + y * 668265263 + z * 1274126177) | 0;
    n = ((n ^ (n >>> 13)) * 1274126177) | 0;
    n = n ^ (n >>> 16);
    return (n & 0x7fffffff) / 0x7fffffff;
}

function smoothstep(t) { return t * t * (3 - 2 * t); }

function noise2D(x, y) {
    var ix = Math.floor(x), iy = Math.floor(y);
    var fx = x - ix, fy = y - iy;
    fx = smoothstep(fx); fy = smoothstep(fy);
    var a = hash2(ix, iy), b = hash2(ix+1, iy);
    var c = hash2(ix, iy+1), d = hash2(ix+1, iy+1);
    return a + (b-a)*fx + (c-a)*fy + (a-b-c+d)*fx*fy;
}

function noise3D(x, y, z) {
    var ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    var fx = x - ix, fy = y - iy, fz = z - iz;
    fx = smoothstep(fx); fy = smoothstep(fy); fz = smoothstep(fz);
    function h(dx,dy,dz){ return hash3(ix+dx, iy+dy, iz+dz); }
    var v000=h(0,0,0),v100=h(1,0,0),v010=h(0,1,0),v110=h(1,1,0);
    var v001=h(0,0,1),v101=h(1,0,1),v011=h(0,1,1),v111=h(1,1,1);
    var x00=v000+(v100-v000)*fx, x10=v010+(v110-v010)*fx;
    var x01=v001+(v101-v001)*fx, x11=v011+(v111-v011)*fx;
    var xy0=x00+(x10-x00)*fy, xy1=x01+(x11-x01)*fy;
    return xy0+(xy1-xy0)*fz;
}

function fractal2D(x, y, octaves) {
    var val = 0, amp = 1, freq = 1, total = 0;
    for (var i = 0; i < octaves; i++) {
        val += noise2D(x * freq, y * freq) * amp;
        total += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return val / total;
}

function fractal3D(x, y, z, octaves) {
    var val = 0, amp = 1, freq = 1, total = 0;
    for (var i = 0; i < octaves; i++) {
        val += noise3D(x * freq, y * freq, z * freq) * amp;
        total += amp;
        amp *= 0.5;
        freq *= 2;
    }
    return val / total;
}

// === TERRAIN ===
function getHeight(wx, wz) {
    var m = fractal2D(wx * 0.004, wz * 0.004, 4);
    var h = fractal2D(wx * 0.02, wz * 0.02, 4);
    return Math.floor(5 + m * m * 58 + h * 10);
}

// === CHUNKS ===
var chunks = new Map();
var chunkMeshes = [];
var genQueue = [];
var meshQueue = [];

function chunkKey(cx, cz) { return cx + "," + cz; }

function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= 80) return 0;
    var cx = Math.floor(wx / 16);
    var cz = Math.floor(wz / 16);
    var chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return 0;
    var lx = wx - cx * 16;
    var lz = wz - cz * 16;
    return chunk.data[lx * 80 * 16 + wy * 16 + lz];
}

function setBlock(wx, wy, wz, val) {
    if (wy < 0 || wy >= 80) return;
    var cx = Math.floor(wx / 16);
    var cz = Math.floor(wz / 16);
    var chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return;
    var lx = wx - cx * 16;
    var lz = wz - cz * 16;
    chunk.data[lx * 80 * 16 + wy * 16 + lz] = val;
}

function generateChunkData(cx, cz) {
    var data = new Uint8Array(16 * 80 * 16);
    for (var lx = 0; lx < 16; lx++) {
        for (var lz = 0; lz < 16; lz++) {
            var wx = cx * 16 + lx;
            var wz = cz * 16 + lz;
            var H = getHeight(wx, wz);
            for (var y = 0; y < 80; y++) {
                var block = 0;
                if (y === 0) { block = 3; }
                else if (y < H - 3) { block = 3; }
                else if (y < H) {
                    if (H <= 16) block = 4;
                    else if (H >= 37) block = 3;
                    else block = 2;
                } else if (y === H) {
                    if (H >= 46) block = 7;
                    else if (H >= 37) block = 3;
                    else if (H <= 16) block = 4;
                    else block = 1;
                }
                // Caves
                if (y >= 3 && y < H - 2) {
                    if (fractal3D(wx * 0.09, y * 0.09, wz * 0.09, 2) > 0.67) {
                        block = 0;
                    }
                }
                data[lx * 80 * 16 + y * 16 + lz] = block;
            }
        }
    }
    // Trees
    for (var lx = 2; lx < 14; lx++) {
        for (var lz = 2; lz < 14; lz++) {
            var wx = cx * 16 + lx;
            var wz = cz * 16 + lz;
            var H = getHeight(wx, wz);
            if (H > 16 && H < 37) {
                var idx = lx * 80 * 16 + H * 16 + lz;
                if (data[idx] === 1 && hash2(wx, wz) < 0.02) {
                    // Trunk
                    for (var ty = H + 1; ty <= H + 4; ty++) {
                        if (ty < 80) data[lx * 80 * 16 + ty * 16 + lz] = 5;
                    }
                    // Leaves 5x5 at H+3, H+4
                    for (var ly = H + 3; ly <= H + 4; ly++) {
                        for (var dx = -2; dx <= 2; dx++) {
                            for (var dz = -2; dz <= 2; dz++) {
                                var nx = lx + dx, nz = lz + dz;
                                if (nx >= 0 && nx < 16 && nz >= 0 && nz < 16 && ly < 80) {
                                    var ti = nx * 80 * 16 + ly * 16 + nz;
                                    if (data[ti] === 0) data[ti] = 6;
                                }
                            }
                        }
                    }
                    // 3x3 at H+5
                    if (H + 5 < 80) {
                        for (var dx = -1; dx <= 1; dx++) {
                            for (var dz = -1; dz <= 1; dz++) {
                                var nx = lx + dx, nz = lz + dz;
                                if (nx >= 0 && nx < 16 && nz >= 0 && nz < 16) {
                                    var ti = nx * 80 * 16 + (H+5) * 16 + nz;
                                    if (data[ti] === 0) data[ti] = 6;
                                }
                            }
                        }
                    }
                    // 1 on top at H+6
                    if (H + 6 < 80) {
                        var ti = lx * 80 * 16 + (H+6) * 16 + lz;
                        if (data[ti] === 0) data[ti] = 6;
                    }
                }
            }
        }
    }
    return data;
}

// === MESHING ===
var BLOCK_COLORS = {
    1: [0x4c/255, 0xaf/255, 0x50/255],
    2: [0x79/255, 0x55/255, 0x48/255],
    3: [0x9e/255, 0x9e/255, 0x9e/255],
    4: [0xe7/255, 0xd9/255, 0xa8/255],
    5: [0x8d/255, 0x6e/255, 0x63/255],
    6: [0x2e/255, 0x7d/255, 0x32/255],
    7: [1.0, 1.0, 1.0]
};

var FACES = [
    { dir: [1,0,0],  verts: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]], light: 0.8 },
    { dir: [-1,0,0], verts: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]], light: 0.8 },
    { dir: [0,1,0],  verts: [[0,1,0],[0,1,1],[1,1,1],[1,1,0]], light: 1.0 },
    { dir: [0,-1,0], verts: [[0,0,1],[0,0,0],[1,0,0],[1,0,1]], light: 0.55 },
    { dir: [0,0,1],  verts: [[1,0,1],[1,1,1],[0,1,1],[0,0,1]], light: 0.8 },
    { dir: [0,0,-1], verts: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]], light: 0.8 }
];

function buildChunkMesh(cx, cz) {
    var chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return;
    var positions = [];
    var normals = [];
    var colors = [];

    for (var lx = 0; lx < 16; lx++) {
        for (var y = 0; y < 80; y++) {
            for (var lz = 0; lz < 16; lz++) {
                var block = chunk.data[lx * 80 * 16 + y * 16 + lz];
                if (block === 0) continue;
                var wx = cx * 16 + lx;
                var wz = cz * 16 + lz;
                var col = BLOCK_COLORS[block];
                for (var f = 0; f < 6; f++) {
                    var face = FACES[f];
                    var nx = wx + face.dir[0];
                    var ny = y + face.dir[1];
                    var nz = wz + face.dir[2];
                    if (getBlock(nx, ny, nz) !== 0) continue;
                    var light = face.light;
                    var r = col[0] * light;
                    var g = col[1] * light;
                    var b = col[2] * light;
                    var v = face.verts;
                    // Triangle 1: v[0], v[1], v[2]
                    positions.push(wx+v[0][0], y+v[0][1], wz+v[0][2]);
                    positions.push(wx+v[1][0], y+v[1][1], wz+v[1][2]);
                    positions.push(wx+v[2][0], y+v[2][1], wz+v[2][2]);
                    // Triangle 2: v[0], v[2], v[3]
                    positions.push(wx+v[0][0], y+v[0][1], wz+v[0][2]);
                    positions.push(wx+v[2][0], y+v[2][1], wz+v[2][2]);
                    positions.push(wx+v[3][0], y+v[3][1], wz+v[3][2]);
                    for (var i = 0; i < 6; i++) {
                        normals.push(face.dir[0], face.dir[1], face.dir[2]);
                        colors.push(r, g, b);
                    }
                }
            }
        }
    }

    // Remove old mesh
    if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        var idx = chunkMeshes.indexOf(chunk.mesh);
        if (idx >= 0) chunkMeshes.splice(idx, 1);
    }

    if (positions.length === 0) { chunk.mesh = null; return; }

    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    var mesh = new THREE.Mesh(geo, sharedMaterial);
    scene.add(mesh);
    chunkMeshes.push(mesh);
    chunk.mesh = mesh;
}

// === THREE.JS SETUP ===
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

var ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambientLight);
var dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(50, 100, 30);
scene.add(dirLight);

var sharedMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

// === PLAYER ===
var player = {
    x: 8, y: 50, z: 8,
    vx: 0, vy: 0, vz: 0,
    yaw: 0, pitch: 0,
    onGround: false,
    halfW: 0.3,
    height: 1.8,
    eye: 1.62
};

// Spawn above terrain
(function(){
    var h = getHeight(8, 8);
    player.y = h + 2;
})();

// === CONTROLS ===
var keys = {};
var locked = false;

document.addEventListener('keydown', function(e) { keys[e.code] = true; });
document.addEventListener('keyup', function(e) { keys[e.code] = false; });

document.addEventListener('mousemove', function(e) {
    if (!locked) return;
    player.yaw -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    player.pitch = Math.max(-Math.PI/2 + 0.01, Math.min(Math.PI/2 - 0.01, player.pitch));
});

var overlay = document.getElementById('overlay');
overlay.addEventListener('click', function() {
    renderer.domElement.requestPointerLock();
});

document.addEventListener('pointerlockchange', function() {
    locked = document.pointerLockElement === renderer.domElement;
    overlay.style.display = locked ? 'none' : 'flex';
});

document.addEventListener('contextmenu', function(e) { e.preventDefault(); });

// === HOTBAR ===
var hotbarBlocks = [1,2,3,4,5,6,7];
var hotbarColors = ['#4caf50','#795548','#9e9e9e','#e7d9a8','#8d6e63','#2e7d32','#ffffff'];
var selectedSlot = 0;

(function(){
    var bar = document.getElementById('hotbar');
    for (var i = 0; i < 7; i++) {
        var s = document.createElement('div');
        s.className = 'slot' + (i === 0 ? ' selected' : '');
        s.style.background = hotbarColors[i];
        s.innerHTML = '<span>' + (i+1) + '</span>';
        bar.appendChild(s);
    }
})();

function updateHotbar() {
    var slots = document.querySelectorAll('.slot');
    for (var i = 0; i < 7; i++) {
        slots[i].className = 'slot' + (i === selectedSlot ? ' selected' : '');
    }
}

document.addEventListener('keydown', function(e) {
    if (e.code >= 'Digit1' && e.code <= 'Digit7') {
        selectedSlot = parseInt(e.code.charAt(5)) - 1;
        updateHotbar();
    }
});

document.addEventListener('wheel', function(e) {
    if (!locked) return;
    selectedSlot = (selectedSlot + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
    updateHotbar();
});

// === RAYCASTING & INTERACTION ===
var raycaster = new THREE.Raycaster();
raycaster.far = 6;
var outlineBox;

(function(){
    var geo = new THREE.BoxGeometry(1.005, 1.005, 1.005);
    var edges = new THREE.EdgesGeometry(geo);
    outlineBox = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x000000 }));
    outlineBox.visible = false;
    scene.add(outlineBox);
})();

var targetBlock = null;
var placeCell = null;

document.addEventListener('mousedown', function(e) {
    if (!locked) return;
    e.preventDefault();
    if (e.button === 0 && targetBlock) {
        // Break
        var bx = targetBlock[0], by = targetBlock[1], bz = targetBlock[2];
        if (by === 0) return; // unbreakable
        setBlock(bx, by, bz, 0);
        rebuildAt(bx, by, bz);
    } else if (e.button === 2 && placeCell) {
        // Place
        var px = placeCell[0], py = placeCell[1], pz = placeCell[2];
        if (getBlock(px, py, pz) !== 0) return;
        // Check overlap with player
        var pw = player.halfW;
        if (px + 1 > player.x - pw && px < player.x + pw &&
            py + 1 > player.y && py < player.y + player.height &&
            pz + 1 > player.z - pw && pz < player.z + pw) return;
        setBlock(px, py, pz, hotbarBlocks[selectedSlot]);
        rebuildAt(px, py, pz);
    }
});

function rebuildAt(wx, wy, wz) {
    var cx = Math.floor(wx / 16);
    var cz = Math.floor(wz / 16);
    buildChunkMesh(cx, cz);
    // Rebuild neighbors if on border
    var lx = wx - cx * 16;
    var lz = wz - cz * 16;
    if (lx === 0) buildChunkMesh(cx - 1, cz);
    if (lx === 15) buildChunkMesh(cx + 1, cz);
    if (lz === 0) buildChunkMesh(cx, cz - 1);
    if (lz === 15) buildChunkMesh(cx, cz + 1);
}

// === COLLISION ===
function collides(px, py, pz) {
    var hw = player.halfW;
    var minX = Math.floor(px - hw), maxX = Math.floor(px + hw);
    var minY = Math.floor(py), maxY = Math.floor(py + player.height - 0.001);
    var minZ = Math.floor(pz - hw), maxZ = Math.floor(pz + hw);
    for (var x = minX; x <= maxX; x++)
        for (var y = minY; y <= maxY; y++)
            for (var z = minZ; z <= maxZ; z++)
                if (getBlock(x, y, z) !== 0) return true;
    return false;
}

// === CLOUDS ===
var clouds = [];
(function(){
    var cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 });
    for (var i = 0; i < 25; i++) {
        var w = 8 + hash2(i, 100) * 16;
        var d = 6 + hash2(i, 200) * 12;
        var h = 2 + hash2(i, 300) * 3;
        var geo = new THREE.BoxGeometry(w, h, d);
        var mesh = new THREE.Mesh(geo, cloudMat);
        mesh.position.set(
            (hash2(i, 400) - 0.5) * 300,
            88 + hash2(i, 500) * 6,
            (hash2(i, 600) - 0.5) * 300
        );
        scene.add(mesh);
        clouds.push(mesh);
    }
})();

// === WATER PLANE ===
var waterGeo = new THREE.PlaneGeometry(400, 400);
var waterMat = new THREE.MeshLambertMaterial({ color: 0x3399ff, transparent: true, opacity: 0.5 });
var waterPlane = new THREE.Mesh(waterGeo, waterMat);
waterPlane.rotation.x = -Math.PI / 2;
waterPlane.position.y = 14.3;
scene.add(waterPlane);

// === WORLD MANAGEMENT ===
function updateWorld() {
    var pcx = Math.floor(player.x / 16);
    var pcz = Math.floor(player.z / 16);

    // Generate chunks within 5
    var genCount = 0;
    for (var dx = -5; dx <= 5 && genCount < 4; dx++) {
        for (var dz = -5; dz <= 5 && genCount < 4; dz++) {
            var cx = pcx + dx, cz = pcz + dz;
            var key = chunkKey(cx, cz);
            if (!chunks.has(key)) {
                var data = generateChunkData(cx, cz);
                chunks.set(key, { data: data, mesh: null });
                genCount++;
            }
        }
    }

    // Build meshes for chunks within 4 (need all 4 neighbors)
    var meshCount = 0;
    for (var dx = -4; dx <= 4 && meshCount < 2; dx++) {
        for (var dz = -4; dz <= 4 && meshCount < 2; dz++) {
            var cx = pcx + dx, cz = pcz + dz;
            var key = chunkKey(cx, cz);
            var chunk = chunks.get(key);
            if (!chunk || chunk.mesh) continue;
            // Check neighbors exist
            if (!chunks.has(chunkKey(cx-1,cz)) || !chunks.has(chunkKey(cx+1,cz)) ||
                !chunks.has(chunkKey(cx,cz-1)) || !chunks.has(chunkKey(cx,cz+1))) continue;
            buildChunkMesh(cx, cz);
            meshCount++;
        }
    }

    // Remove far chunks
    var toDelete = [];
    chunks.forEach(function(chunk, key) {
        var parts = key.split(',');
        var cx = parseInt(parts[0]), cz = parseInt(parts[1]);
        if (Math.abs(cx - pcx) > 7 || Math.abs(cz - pcz) > 7) {
            toDelete.push(key);
        }
    });
    for (var i = 0; i < toDelete.length; i++) {
        var chunk = chunks.get(toDelete[i]);
        if (chunk.mesh) {
            scene.remove(chunk.mesh);
            chunk.mesh.geometry.dispose();
            var idx = chunkMeshes.indexOf(chunk.mesh);
            if (idx >= 0) chunkMeshes.splice(idx, 1);
        }
        chunks.delete(toDelete[i]);
    }
}

// === GAME LOOP ===
var lastTime = performance.now();

function update() {
    var now = performance.now();
    var dt = Math.min((now - lastTime) / 1000, 0.05);
    lastTime = now;

    // Movement
    var speed = 5.5;
    var mx = 0, mz = 0;
    if (keys['KeyW']) { mx -= Math.sin(player.yaw); mz -= Math.cos(player.yaw); }
    if (keys['KeyS']) { mx += Math.sin(player.yaw); mz += Math.cos(player.yaw); }
    if (keys['KeyA']) { mx -= Math.cos(player.yaw); mz += Math.sin(player.yaw); }
    if (keys['KeyD']) { mx += Math.cos(player.yaw); mz -= Math.sin(player.yaw); }

    var len = Math.sqrt(mx*mx + mz*mz);
    if (len > 0) { mx = mx/len * speed; mz = mz/len * speed; }

    player.vx = mx;
    player.vz = mz;
    player.vy -= 25 * dt;

    if (keys['Space'] && player.onGround) {
        player.vy = 8.5;
        player.onGround = false;
    }

    // Axis-separated collision
    var nx = player.x + player.vx * dt;
    if (!collides(nx, player.y, player.z)) { player.x = nx; }

    var ny = player.y + player.vy * dt;
    if (!collides(player.x, ny, player.z)) {
        player.y = ny;
        player.onGround = false;
    } else {
        if (player.vy < 0) player.onGround = true;
        player.vy = 0;
    }

    var nz = player.z + player.vz * dt;
    if (!collides(player.x, player.y, nz)) { player.z = nz; }

    // Fall below -20
    if (player.y < -20) {
        player.x = 8; player.z = 8;
        player.y = getHeight(8, 8) + 2;
        player.vy = 0;
    }

    // Camera
    camera.position.set(player.x, player.y + player.eye, player.z);
    camera.rotation.y = player.yaw;
    camera.rotation.x = player.pitch;

    // Update world
    updateWorld();

    // Raycast
    raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
    var hits = raycaster.intersectObjects(chunkMeshes);
    if (hits.length > 0) {
        var hit = hits[0];
        var p = hit.point;
        var n = hit.face.normal;
        var bx = Math.floor(p.x - n.x * 0.5);
        var by = Math.floor(p.y - n.y * 0.5);
        var bz = Math.floor(p.z - n.z * 0.5);
        targetBlock = [bx, by, bz];
        placeCell = [
            Math.floor(p.x + n.x * 0.5),
            Math.floor(p.y + n.y * 0.5),
            Math.floor(p.z + n.z * 0.5)
        ];
        outlineBox.visible = true;
        outlineBox.position.set(bx + 0.5, by + 0.5, bz + 0.5);
    } else {
        targetBlock = null;
        placeCell = null;
        outlineBox.visible = false;
    }

    // Clouds drift
    for (var i = 0; i < clouds.length; i++) {
        clouds[i].position.x += 1.5 * dt;
        // Wrap around player
        var dx = clouds[i].position.x - player.x;
        var dz = clouds[i].position.z - player.z;
        if (dx > 150) clouds[i].position.x -= 300;
        if (dx < -150) clouds[i].position.x += 300;
        if (dz > 150) clouds[i].position.z -= 300;
        if (dz < -150) clouds[i].position.z += 300;
    }

    // Water follows player
    waterPlane.position.x = player.x;
    waterPlane.position.z = player.z;

    renderer.render(scene, camera);
    requestAnimationFrame(update);
}

// === RESIZE ===
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