```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MC</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #000; }
canvas { display: block; }
#overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7); display: flex; flex-direction: column;
    align-items: center; justify-content: center; z-index: 100;
    font-family: monospace; color: #fff; cursor: pointer;
}
#overlay h1 { font-size: 48px; margin-bottom: 20px; color: #4caf50; }
#overlay p { font-size: 16px; margin: 4px 0; }
#overlay .start { font-size: 24px; margin-top: 30px; color: #fff; border: 2px solid #fff; padding: 10px 30px; }
#crosshair {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 20px; height: 20px; z-index: 50; pointer-events: none;
}
#crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: rgba(255,255,255,0.8);
}
#crosshair::before { width: 2px; height: 20px; left: 9px; top: 0; }
#crosshair::after { width: 20px; height: 2px; top: 9px; left: 0; }
#hotbar {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 2px; z-index: 50; background: rgba(0,0,0,0.6);
    padding: 4px; border-radius: 4px; pointer-events: none;
}
.slot {
    width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;
    font-family: monospace; font-size: 14px; color: #fff; text-shadow: 1px 1px 1px #000;
    border: 2px solid rgba(255,255,255,0.3); border-radius: 3px; position: relative;
}
.slot.selected { border-color: #fff; }
.slot span { position: absolute; top: 1px; left: 3px; font-size: 10px; }
</style>
</head>
<body>
<div id="overlay">
    <h1>MC</h1>
    <p>WASD - Move | Space - Jump</p>
    <p>Left Click - Break | Right Click - Place</p>
    <p>1-7 / Mouse Wheel - Select Block</p>
    <p>Mouse - Look Around</p>
    <div class="start">Click to Play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function() {
    // === CONSTANTS ===
    const CHUNK_SIZE = 16;
    const CHUNK_HEIGHT = 80;
    const RENDER_DIST = 5;
    const MESH_DIST = 4;
    const UNLOAD_DIST = 7;
    const GRAVITY = 25;
    const JUMP_VEL = 8.5;
    const MOVE_SPEED = 5.5;
    const PLAYER_HALF_W = 0.3;
    const PLAYER_HEIGHT = 1.8;
    const EYE_HEIGHT = 1.62;
    const REACH = 6;
    const SENSITIVITY = 0.002;

    const BLOCK_COLORS = {
        1: [0x4c/255, 0xaf/255, 0x50/255],
        2: [0x79/255, 0x55/255, 0x48/255],
        3: [0x9e/255, 0x9e/255, 0x9e/255],
        4: [0xe7/255, 0xd9/255, 0xa8/255],
        5: [0x8d/255, 0x6e/255, 0x63/255],
        6: [0x2e/255, 0x7d/255, 0x32/255],
        7: [0xff/255, 0xff/255, 0xff/255]
    };

    const FACES = [
        { dir: [1,0,0], light: 0.8, corners: [[1,1,1],[1,0,1],[1,1,0],[1,0,0]] },
        { dir: [-1,0,0], light: 0.8, corners: [[0,1,0],[0,0,0],[0,1,1],[0,0,1]] },
        { dir: [0,1,0], light: 1.0, corners: [[0,1,1],[1,1,1],[0,1,0],[1,1,0]] },
        { dir: [0,-1,0], light: 0.55, corners: [[0,0,0],[1,0,0],[0,0,1],[1,0,1]] },
        { dir: [0,0,1], light: 0.8, corners: [[0,1,1],[0,0,1],[1,1,1],[1,0,1]] },
        { dir: [0,0,-1], light: 0.8, corners: [[1,1,0],[1,0,0],[0,1,0],[0,0,0]] }
    ];

    // === THREE.JS SETUP ===
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
    dirLight.position.set(50, 100, 30);
    scene.add(dirLight);

    const sharedMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

    // === NOISE ===
    function hash3(ix, iy, iz) {
        let n = ix * 374761393 + iy * 668265263 + iz * 1440662683;
        n = ((n >> 13) ^ n);
        n = (n * (n * n * 60493 + 19990303) + 1376312589) & 0x7fffffff;
        return n / 0x7fffffff;
    }

    function smoothstep(t) { return t * t * (3 - 2 * t); }

    function noise2D(x, y) {
        let ix = Math.floor(x), iy = Math.floor(y);
        let fx = x - ix, fy = y - iy;
        fx = smoothstep(fx); fy = smoothstep(fy);
        let a = hash3(ix, 0, iy), b = hash3(ix+1, 0, iy);
        let c = hash3(ix, 0, iy+1), d = hash3(ix+1, 0, iy+1);
        return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy;
    }

    function noise3D(x, y, z) {
        let ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
        let fx = x - ix, fy = y - iy, fz = z - iz;
        fx = smoothstep(fx); fy = smoothstep(fy); fz = smoothstep(fz);
        let n000 = hash3(ix, iy, iz), n100 = hash3(ix+1, iy, iz);
        let n010 = hash3(ix, iy+1, iz), n110 = hash3(ix+1, iy+1, iz);
        let n001 = hash3(ix, iy, iz+1), n101 = hash3(ix+1, iy, iz+1);
        let n011 = hash3(ix, iy+1, iz+1), n111 = hash3(ix+1, iy+1, iz+1);
        let nx00 = n000 + (n100 - n000) * fx;
        let nx10 = n010 + (n110 - n010) * fx;
        let nx01 = n001 + (n101 - n001) * fx;
        let nx11 = n011 + (n111 - n011) * fx;
        let nxy0 = nx00 + (nx10 - nx00) * fy;
        let nxy1 = nx01 + (nx11 - nx01) * fy;
        return nxy0 + (nxy1 - nxy0) * fz;
    }

    function fractal2D(x, y) {
        let sum = 0, amp = 1, freq = 1, max = 0;
        for (let i = 0; i < 4; i++) {
            sum += noise2D(x * freq, y * freq) * amp;
            max += amp;
            amp *= 0.5;
            freq *= 2;
        }
        return sum / max;
    }

    function fractal3D(x, y, z) {
        let sum = 0, amp = 1, freq = 1, max = 0;
        for (let i = 0; i < 4; i++) {
            sum += noise3D(x * freq, y * freq, z * freq) * amp;
            max += amp;
            amp *= 0.5;
            freq *= 2;
        }
        return sum / max;
    }

    // === CHUNK DATA ===
    const chunks = new Map();
    const chunkMeshes = [];

    function chunkKey(cx, cz) { return cx + ',' + cz; }

    function getChunkData(cx, cz) {
        return chunks.get(chunkKey(cx, cz));
    }

    function readBlock(wx, wy, wz) {
        if (wy < 0 || wy >= CHUNK_HEIGHT) return 0;
        let cx = Math.floor(wx / CHUNK_SIZE);
        let cz = Math.floor(wz / CHUNK_SIZE);
        let chunk = chunks.get(chunkKey(cx, cz));
        if (!chunk) return 0;
        let lx = wx - cx * CHUNK_SIZE;
        let lz = wz - cz * CHUNK_SIZE;
        return chunk.data[lx + lz * CHUNK_SIZE + wy * CHUNK_SIZE * CHUNK_SIZE];
    }

    function writeBlock(wx, wy, wz, val) {
        if (wy < 0 || wy >= CHUNK_HEIGHT) return;
        let cx = Math.floor(wx / CHUNK_SIZE);
        let cz = Math.floor(wz / CHUNK_SIZE);
        let chunk = chunks.get(chunkKey(cx, cz));
        if (!chunk) return;
        let lx = wx - cx * CHUNK_SIZE;
        let lz = wz - cz * CHUNK_SIZE;
        chunk.data[lx + lz * CHUNK_SIZE + wy * CHUNK_SIZE * CHUNK_SIZE] = val;
    }

    // === TERRAIN GENERATION ===
    function generateChunk(cx, cz) {
        let key = chunkKey(cx, cz);
        if (chunks.has(key)) return;
        let data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
        let baseX = cx * CHUNK_SIZE;
        let baseZ = cz * CHUNK_SIZE;

        for (let lx = 0; lx < CHUNK_SIZE; lx++) {
            for (let lz = 0; lz < CHUNK_SIZE; lz++) {
                let wx = baseX + lx;
                let wz = baseZ + lz;
                let m = fractal2D(wx * 0.004, wz * 0.004);
                let h = fractal2D(wx * 0.02, wz * 0.02);
                let H = Math.floor(5 + m * m * 58 + h * 10);
                if (H < 1) H = 1;
                if (H > CHUNK_HEIGHT - 1) H = CHUNK_HEIGHT - 1;

                for (let y = 0; y <= H && y < CHUNK_HEIGHT; y++) {
                    let block = 0;
                    if (y === 0) {
                        block = 3; // unbreakable stone at bottom
                    } else if (y >= H - 2 && y < H) {
                        // 3 layers under surface: dirt, or sand if beach, or stone if mountain
                        if (H <= 16) block = 4; // sand
                        else if (H >= 37) block = 3; // stone
                        else block = 2; // dirt
                    } else if (y < H - 2) {
                        block = 3; // stone below
                    } else { // y === H, surface
                        if (H >= 46) block = 7; // snow
                        else if (H >= 37) block = 3; // stone
                        else if (H <= 16) block = 4; // sand
                        else block = 1; // grass
                    }

                    // Caves
                    if (y > 0 && y >= 3 && y < H - 2) {
                        let caveVal = fractal3D(wx * 0.09, y * 0.09, wz * 0.09);
                        if (caveVal > 0.67) block = 0;
                    }

                    data[lx + lz * CHUNK_SIZE + y * CHUNK_SIZE * CHUNK_SIZE] = block;
                }

                // Trees
                let surfaceBlock = data[lx + lz * CHUNK_SIZE + H * CHUNK_SIZE * CHUNK_SIZE];
                if (surfaceBlock === 1 && H > 16 && H < 37) {
                    let treeHash = hash3(wx, 0, wz);
                    if (treeHash < 0.02) {
                        // Check trunk fits (5x5 leaves need 2 blocks margin)
                        if (lx >= 2 && lx <= CHUNK_SIZE - 3 && lz >= 2 && lz <= CHUNK_SIZE - 3) {
                            let trunkTop = H + 4;
                            if (trunkTop < CHUNK_HEIGHT) {
                                // Place trunk
                                for (let ty = H + 1; ty <= H + 4; ty++) {
                                    data[lx + lz * CHUNK_SIZE + ty * CHUNK_SIZE * CHUNK_SIZE] = 5;
                                }
                                // Leaves: 5x5 at H+4 and H+5
                                for (let ly = H + 4; ly <= H + 5; ly++) {
                                    if (ly >= CHUNK_HEIGHT) continue;
                                    for (let dx = -2; dx <= 2; dx++) {
                                        for (let dz = -2; dz <= 2; dz++) {
                                            let nlx = lx + dx, nlz = lz + dz;
                                            if (nlx < 0 || nlx >= CHUNK_SIZE || nlz < 0 || nlz >= CHUNK_SIZE) continue;
                                            let idx = nlx + nlz * CHUNK_SIZE + ly * CHUNK_SIZE * CHUNK_SIZE;
                                            if (data[idx] === 0) data[idx] = 6;
                                        }
                                    }
                                }
                                // 3x3 at H+6
                                let ly = H + 6;
                                if (ly < CHUNK_HEIGHT) {
                                    for (let dx = -1; dx <= 1; dx++) {
                                        for (let dz = -1; dz <= 1; dz++) {
                                            let nlx = lx + dx, nlz = lz + dz;
                                            if (nlx < 0 || nlx >= CHUNK_SIZE || nlz < 0 || nlz >= CHUNK_SIZE) continue;
                                            let idx = nlx + nlz * CHUNK_SIZE + ly * CHUNK_SIZE * CHUNK_SIZE;
                                            if (data[idx] === 0) data[idx] = 6;
                                        }
                                    }
                                }
                                // 1 on top at H+7
                                ly = H + 7;
                                if (ly < CHUNK_HEIGHT) {
                                    let idx = lx + lz * CHUNK_SIZE + ly * CHUNK_SIZE * CHUNK_SIZE;
                                    if (data[idx] === 0) data[idx] = 6;
                                }
                            }
                        }
                    }
                }
            }
        }

        chunks.set(key, { data: data, mesh: null });
    }

    // === MESH BUILDING ===
    function buildChunkMesh(cx, cz) {
        let key = chunkKey(cx, cz);
        let chunk = chunks.get(key);
        if (!chunk) return;

        if (chunk.mesh) {
            scene.remove(chunk.mesh);
            chunk.mesh.geometry.dispose();
            let idx = chunkMeshes.indexOf(chunk.mesh);
            if (idx !== -1) chunkMeshes.splice(idx, 1);
            chunk.mesh = null;
        }

        // Check all 4 neighbors have data
        if (!chunks.has(chunkKey(cx-1, cz)) || !chunks.has(chunkKey(cx+1, cz)) ||
            !chunks.has(chunkKey(cx, cz-1)) || !chunks.has(chunkKey(cx, cz+1))) return;

        let positions = [];
        let normals = [];
        let colors = [];
        let baseX = cx * CHUNK_SIZE;
        let baseZ = cz * CHUNK_SIZE;

        for (let lx = 0; lx < CHUNK_SIZE; lx++) {
            for (let lz = 0; lz < CHUNK_SIZE; lz++) {
                for (let y = 0; y < CHUNK_HEIGHT; y++) {
                    let block = chunk.data[lx + lz * CHUNK_SIZE + y * CHUNK_SIZE * CHUNK_SIZE];
                    if (block === 0) continue;

                    let wx = baseX + lx;
                    let wz = baseZ + lz;
                    let col = BLOCK_COLORS[block];
                    if (!col) continue;

                    for (let f = 0; f < 6; f++) {
                        let face = FACES[f];
                        let nx = wx + face.dir[0];
                        let ny = y + face.dir[1];
                        let nz = wz + face.dir[2];
                        let neighbor = readBlock(nx, ny, nz);
                        if (neighbor !== 0) continue;

                        let light = face.light;
                        let r = col[0] * light;
                        let g = col[1] * light;
                        let b = col[2] * light;
                        let c = face.corners;

                        // Triangle 1: A, B, C
                        positions.push(
                            wx + c[0][0], y + c[0][1], wz + c[0][2],
                            wx + c[1][0], y + c[1][1], wz + c[1][2],
                            wx + c[2][0], y + c[2][1], wz + c[2][2]
                        );
                        normals.push(face.dir[0], face.dir[1], face.dir[2],
                                     face.dir[0], face.dir[1], face.dir[2],
                                     face.dir[0], face.dir[1], face.dir[2]);
                        colors.push(r, g, b, r, g, b, r, g, b);

                        // Triangle 2: B, D, C
                        positions.push(
                            wx + c[1][0], y + c[1][1], wz + c[1][2],
                            wx + c[3][0], y + c[3][1], wz + c[3][2],
                            wx + c[2][0], y + c[2][1], wz + c[2][2]
                        );
                        normals.push(face.dir[0], face.dir[1], face.dir[2],
                                     face.dir[0], face.dir[1], face.dir[2],
                                     face.dir[0], face.dir[1], face.dir[2]);
                        colors.push(r, g, b, r, g, b, r, g, b);
                    }
                }
            }
        }

        if (positions.length === 0) return;

        let geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

        let mesh = new THREE.Mesh(geometry, sharedMaterial);
        mesh.position.set(0, 0, 0);
        scene.add(mesh);
        chunk.mesh = mesh;
        chunkMeshes.push(mesh);
    }

    function rebuildChunk(cx, cz) {
        buildChunkMesh(cx, cz);
    }

    // === PLAYER ===
    let playerX = 8, playerY = 50, playerZ = 8;
    let velY = 0;
    let onGround = false;
    let yaw = 0, pitch = 0;
    let keys = {};
    let locked = false;
    let selectedSlot = 0;
    const blockTypes = [1, 2, 3, 4, 5, 6, 7];

    // Find spawn Y
    function getTerrainHeight(wx, wz) {
        for (let y = CHUNK_HEIGHT - 1; y >= 0; y--) {
            if (readBlock(wx, y, wz) !== 0) return y;
        }
        return 0;
    }

    // === CLOUDS ===
    const clouds = [];
    for (let i = 0; i < 25; i++) {
        let w = 20 + Math.random() * 40;
        let d = 10 + Math.random() * 30;
        let geo = new THREE.BoxGeometry(w, 2, d);
        let mat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
        let cloud = new THREE.Mesh(geo, mat);
        cloud.position.set(
            (Math.random() - 0.5) * 300,
            88 + Math.random() * 6,
            (Math.random() - 0.5) * 300
        );
        scene.add(cloud);
        clouds.push({ mesh: cloud, speed: 0.5 + Math.random() * 1 });
    }

    // === WATER PLANE ===
    let waterGeo = new THREE.PlaneGeometry(400, 400);
    let waterMat = new THREE.MeshLambertMaterial({ color: 0x3399ff, transparent: true, opacity: 0.6 });
    let waterPlane = new THREE.Mesh(waterGeo, waterMat);
    waterPlane.rotation.x = -Math.PI / 2;
    waterPlane.position.y = 14.3;
    scene.add(waterPlane);

    // === BLOCK OUTLINE ===
    let outlineGeo = new THREE.BoxGeometry(1.005, 1.005, 1.005);
    let outlineMat = new THREE.MeshBasicMaterial({ color: 0x000000, wireframe: true });
    let outlineMesh = new THREE.Mesh(outlineGeo, outlineMat);
    outlineMesh.visible = false;
    scene.add(outlineMesh);

    // === HOTBAR UI ===
    const hotbarEl = document.getElementById('hotbar');
    const slotColors = ['#4caf50','#795548','#9e9e9e','#e7d9a8','#8d6e63','#2e7d32','#ffffff'];
    for (let i = 0; i < 7; i++) {
        let slot = document.createElement('div');
        slot.className = 'slot' + (i === 0 ? ' selected' : '');
        slot.style.background = slotColors[i];
        slot.innerHTML = '<span>' + (i + 1) + '</span>';
        hotbarEl.appendChild(slot);
    }

    function updateHotbar() {
        let slots = hotbarEl.querySelectorAll('.slot');
        for (let i = 0; i < 7; i++) {
            slots[i].className = 'slot' + (i === selectedSlot ? ' selected' : '');
        }
    }

    // === POINTER LOCK & INPUT ===
    const overlay = document.getElementById('overlay');

    overlay.addEventListener('click', function() {
        renderer.domElement.requestPointerLock();
    });

    document.addEventListener('pointerlockchange', function() {
        locked = document.pointerLockElement === renderer.domElement;
        overlay.style.display = locked ? 'none' : 'flex';
    });

    document.addEventListener('mousemove', function(e) {
        if (!locked) return;
        yaw -= e.movementX * SENSITIVITY;
        pitch -= e.movementY * SENSITIVITY;
        pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, pitch));
    });

    document.addEventListener('keydown', function(e) {
        keys[e.code] = true;
        if (e.code >= 'Digit1' && e.code <= 'Digit7') {
            selectedSlot = parseInt(e.code.charAt(5)) - 1;
            updateHotbar();
        }
    });

    document.addEventListener('keyup', function(e) {
        keys[e.code] = false;
    });

    document.addEventListener('wheel', function(e) {
        if (!locked) return;
        selectedSlot = ((selectedSlot + (e.deltaY > 0 ? 1 : -1)) % 7 + 7) % 7;
        updateHotbar();
    });

    document.addEventListener('contextmenu', function(e) { e.preventDefault(); });

    // === RAYCASTING & INTERACTION ===
    const raycaster = new THREE.Raycaster();
    raycaster.far = REACH;
    let targetBlock = null;

    document.addEventListener('mousedown', function(e) {
        if (!locked) return;
        if (e.button === 0 && targetBlock) {
            // Break
            let bx = targetBlock.x, by = targetBlock.y, bz = targetBlock.z;
            if (by === 0) return; // unbreakable bottom
            writeBlock(bx, by, bz, 0);
            let cx = Math.floor(bx / CHUNK_SIZE);
            let cz = Math.floor(bz / CHUNK_SIZE);
            rebuildChunk(cx, cz);
            let lx = bx - cx * CHUNK_SIZE;
            let lz = bz - cz * CHUNK_SIZE;
            if (lx === 0) rebuildChunk(cx - 1, cz);
            if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
            if (lz === 0) rebuildChunk(cx, cz - 1);
            if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);
        } else if (e.button === 2 && targetBlock) {
            // Place
            let px = targetBlock.px, py = targetBlock.py, pz = targetBlock.pz;
            if (readBlock(px, py, pz) !== 0) return;
            // Check doesn't overlap player
            let pMinX = playerX - PLAYER_HALF_W, pMaxX = playerX + PLAYER_HALF_W;
            let pMinY = playerY, pMaxY = playerY + PLAYER_HEIGHT;
            let pMinZ = playerZ - PLAYER_HALF_W, pMaxZ = playerZ + PLAYER_HALF_W;
            if (px + 1 > pMinX && px < pMaxX && py + 1 > pMinY && py < pMaxY && pz + 1 > pMinZ && pz < pMaxZ) return;
            writeBlock(px, py, pz, blockTypes[selectedSlot]);
            let cx = Math.floor(px / CHUNK_SIZE);
            let cz = Math.floor(pz / CHUNK_SIZE);
            rebuildChunk(cx, cz);
            let lx = px - cx * CHUNK_SIZE;
            let lz = pz - cz * CHUNK_SIZE;
            if (lx === 0) rebuildChunk(cx - 1, cz);
            if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
            if (lz === 0) rebuildChunk(cx, cz - 1);
            if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);
        }
    });

    // === COLLISION ===
    function collidesAt(x, y, z) {
        let minX = Math.floor(x - PLAYER_HALF_W);
        let maxX = Math.floor(x + PLAYER_HALF_W);
        let minY = Math.floor(y);
        let maxY = Math.floor(y + PLAYER_HEIGHT);
        let minZ = Math.floor(z - PLAYER_HALF_W);
        let maxZ = Math.floor(z + PLAYER_HALF_W);
        for (let bx = minX; bx <= maxX; bx++) {
            for (let by = minY; by <= maxY; by++) {
                for (let bz = minZ; bz <= maxZ; bz++) {
                    if (readBlock(bx, by, bz) !== 0) return true;
                }
            }
        }
        return false;
    }

    // === CHUNK MANAGEMENT ===
    function updateChunks() {
        let pcx = Math.floor(playerX / CHUNK_SIZE);
        let pcz = Math.floor(playerZ / CHUNK_SIZE);
        let generated = 0;
        let meshed = 0;

        // Generate data
        for (let dx = -RENDER_DIST; dx <= RENDER_DIST && generated < 4; dx++) {
            for (let dz = -RENDER_DIST; dz <= RENDER_DIST && generated < 4; dz++) {
                let cx = pcx + dx, cz = pcz + dz;
                if (!chunks.has(chunkKey(cx, cz))) {
                    generateChunk(cx, cz);
                    generated++;
                }
            }
        }

        // Build meshes
        for (let dx = -MESH_DIST; dx <= MESH_DIST && meshed < 2; dx++) {
            for (let dz = -MESH_DIST; dz <= MESH_DIST && meshed < 2; dz++) {
                let cx = pcx + dx, cz = pcz + dz;
                let chunk = chunks.get(chunkKey(cx, cz));
                if (chunk && !chunk.mesh) {
                    buildChunkMesh(cx, cz);
                    meshed++;
                }
            }
        }

        // Unload far chunks
        let toRemove = [];
        chunks.forEach(function(val, key) {
            let parts = key.split(',');
            let cx = parseInt(parts[0]), cz = parseInt(parts[1]);
            let dist = Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz));
            if (dist > UNLOAD_DIST) {
                toRemove.push(key);
            }
        });
        toRemove.forEach(function(key) {
            let chunk = chunks.get(key);
            if (chunk && chunk.mesh) {
                scene.remove(chunk.mesh);
                chunk.mesh.geometry.dispose();
                let idx = chunkMeshes.indexOf(chunk.mesh);
                if (idx !== -1) chunkMeshes.splice(idx, 1);
            }
            chunks.delete(key);
        });
    }

    // === GAME LOOP ===
    let lastTime = performance.now();
    let spawnY = 50;

    function update() {
        requestAnimationFrame(update);

        let now = performance.now();
        let dt = Math.min((now - lastTime) / 1000, 0.05);
        lastTime = now;

        // Movement
        let moveX = 0, moveZ = 0;
        if (keys['KeyW'] || keys['ArrowUp']) { moveX -= Math.sin(yaw); moveZ -= Math.cos(yaw); }
        if (keys['KeyS'] || keys['ArrowDown']) { moveX += Math.sin(yaw); moveZ += Math.cos(yaw); }
        if (keys['KeyA'] || keys['ArrowLeft']) { moveX -= Math.cos(yaw); moveZ += Math.sin(yaw); }
        if (keys['KeyD'] || keys['ArrowRight']) { moveX += Math.cos(yaw); moveZ -= Math.sin(yaw); }

        let len = Math.sqrt(moveX * moveX + moveZ * moveZ);
        if (len > 0) { moveX /= len; moveZ /= len; }

        let speed = MOVE_SPEED * dt;

        // Move X
        let newX = playerX + moveX * speed;
        if (!collidesAt(newX, playerY, playerZ)) playerX = newX;

        // Move Z
        let newZ = playerZ + moveZ * speed;
        if (!collidesAt(playerX, playerY, newZ)) playerZ = newZ;

        // Gravity & Jump
        if (keys['Space'] && onGround) {
            velY = JUMP_VEL;
            onGround = false;
        }
        velY -= GRAVITY * dt;
        let newY = playerY + velY * dt;

        if (!collidesAt(playerX, newY, playerZ)) {
            playerY = newY;
            onGround = false;
        } else {
            if (velY < 0) onGround = true;
            velY = 0;
        }

        // Fall below world
        if (playerY < -20) {
            playerX = 8; playerZ = 8;
            playerY = spawnY;
            velY = 0;
        }

        // Camera
        camera.position.set(playerX, playerY + EYE_HEIGHT, playerZ);
        camera.rotation.y = yaw;
        camera.rotation.x = pitch;

        // Update chunks
        updateChunks();

        // Raycast for target
        raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
        let intersects = raycaster.intersectObjects(chunkMeshes);
        if (intersects.length > 0 && locked) {
            let hit = intersects[0];
            let p = hit.point;
            let n = hit.face.normal;
            let bx = Math.floor(p.x - n.x * 0.5);
            let by = Math.floor(p.y - n.y * 0.5);
            let bz = Math.floor(p.z - n.z * 0.5);
            let px = Math.floor(p.x + n.x * 0.5);
            let py = Math.floor(p.y + n.y * 0.5);
            let pz = Math.floor(p.z + n.z * 0.5);
            targetBlock = { x: bx, y: by, z: bz, px: px, py: py, pz: pz };
            outlineMesh.visible = true;
            outlineMesh.position.set(bx + 0.5, by + 0.5, bz + 0.5);
        } else {
            targetBlock = null;
            outlineMesh.visible = false;
        }

        // Clouds
        clouds.forEach(function(c) {
            c.mesh.position.x += c.speed * dt;
            // Wrap around player
            let dx = c.mesh.position.x - playerX;
            if (dx > 150) c.mesh.position.x -= 300;
            if (dx < -150) c.mesh.position.x += 300;
            let dz = c.mesh.position.z - playerZ;
            if (dz > 150) c.mesh.position.z -= 300;
            if (dz < -150) c.mesh.position.z += 300;
        });

        // Water follows player
        waterPlane.position.x = playerX;
        waterPlane.position.z = playerZ;

        renderer.render(scene, camera);
    }

    // === RESIZE ===
    window.addEventListener('resize', function() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // === INIT ===
    // Generate initial chunks around spawn
    let initCx = Math.floor(8 / CHUNK_SIZE);
    let initCz = Math.floor(8 / CHUNK_SIZE);
    for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
            generateChunk(initCx + dx, initCz + dz);
        }
    }
    for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
            buildChunkMesh(initCx + dx, initCz + dz);
        }
    }

    // Find spawn height
    spawnY = getTerrainHeight(8, 8) + 2;
    playerY = spawnY;

    update();
})();
</script>
</body>
</html>
```