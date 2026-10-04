```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MC Voxel</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: #000; }
canvas { display: block; width: 100%; height: 100%; }
#overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7); display: flex; flex-direction: column;
    align-items: center; justify-content: center; z-index: 100;
    font-family: monospace; color: #fff; cursor: pointer;
}
#overlay h1 { font-size: 48px; margin-bottom: 20px; text-shadow: 2px 2px 4px #000; }
#overlay p { font-size: 16px; margin: 4px 0; }
#overlay .start { font-size: 24px; margin-top: 30px; color: #4caf50; }
#crosshair {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 20px; height: 20px; z-index: 50; pointer-events: none;
}
#crosshair::before, #crosshair::after {
    content: ''; position: absolute; background: #fff;
}
#crosshair::before { width: 2px; height: 20px; left: 9px; top: 0; }
#crosshair::after { width: 20px; height: 2px; top: 9px; left: 0; }
#hotbar {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; z-index: 50; pointer-events: none;
}
.slot {
    width: 48px; height: 48px; border: 2px solid #555;
    display: flex; align-items: center; justify-content: center;
    font-family: monospace; font-size: 14px; color: #fff;
    text-shadow: 1px 1px 2px #000; position: relative;
}
.slot.selected { border-color: #fff; box-shadow: 0 0 6px #fff; }
.slot span { position: absolute; top: 2px; left: 4px; font-size: 11px; }
</style>
</head>
<body>
<div id="overlay">
    <h1>MC Voxel</h1>
    <p>WASD – Move | Space – Jump | Mouse – Look</p>
    <p>Left Click – Break | Right Click – Place</p>
    <p>1-7 / Scroll – Select Block</p>
    <p class="start">Click to Play</p>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function() {
    // Constants
    const CHUNK_SIZE = 16;
    const CHUNK_HEIGHT = 80;
    const RENDER_DIST = 5;
    const MESH_DIST = 4;
    const UNLOAD_DIST = 7;
    const GRAVITY = 25;
    const JUMP_VEL = 8.5;
    const MOVE_SPEED = 5.5;
    const PLAYER_HALF = 0.3;
    const PLAYER_HEIGHT = 1.8;
    const EYE_HEIGHT = 1.62;
    const REACH = 6;
    const SENSITIVITY = 0.002;

    const BLOCK_COLORS = [0, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
    const BLOCK_NAMES = ['Air','Grass','Dirt','Stone','Sand','Wood','Leaves','Snow'];

    // Face definitions: [dirX,dirY,dirZ, light, [v0,v1,v2,v3]]
    const FACES = [
        { dir:[0,1,0], light:1.0, verts:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
        { dir:[0,-1,0], light:0.55, verts:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
        { dir:[1,0,0], light:0.8, verts:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]] },
        { dir:[-1,0,0], light:0.8, verts:[[0,0,1],[0,0,0],[0,1,0],[0,1,1]] },
        { dir:[0,0,1], light:0.8, verts:[[1,0,1],[0,0,1],[0,1,1],[1,1,1]] },
        { dir:[0,0,-1], light:0.8, verts:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]] }
    ];

    // State
    const chunks = new Map();
    const chunkMeshes = [];
    let scene, camera, renderer, material;
    let playerX = 8, playerY = 50, playerZ = 8;
    let velY = 0, onGround = false;
    let yaw = 0, pitch = 0;
    let locked = false;
    let selectedSlot = 0;
    let keys = {};
    let targetBlock = null;
    let outlineMesh;
    let cloudGroup;
    let waterPlane;
    let lastTime = performance.now();

    // Hash function
    function hash(x, y, z) {
        let n = (x * 374761393 + y * 668265263 + z * 1274126177) | 0;
        n = ((n ^ (n >> 13)) * 1274126177) | 0;
        n = (n ^ (n >> 16)) | 0;
        return (n & 0x7fffffff) / 0x7fffffff;
    }

    function smoothstep(t) { return t * t * (3 - 2 * t); }

    // 2D Value Noise
    function noise2D(x, z) {
        const ix = Math.floor(x), iz = Math.floor(z);
        const fx = x - ix, fz = z - iz;
        const sx = smoothstep(fx), sz = smoothstep(fz);
        const a = hash(ix, 0, iz);
        const b = hash(ix + 1, 0, iz);
        const c = hash(ix, 0, iz + 1);
        const d = hash(ix + 1, 0, iz + 1);
        return a + (b - a) * sx + (c - a) * sz + (a - b - c + d) * sx * sz;
    }

    function fractal2D(x, z) {
        let val = 0, amp = 0.5, freq = 1;
        for (let i = 0; i < 4; i++) {
            val += amp * noise2D(x * freq, z * freq);
            amp *= 0.5;
            freq *= 2;
        }
        return val;
    }

    // 3D Value Noise
    function noise3D(x, y, z) {
        const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
        const fx = x - ix, fy = y - iy, fz = z - iz;
        const sx = smoothstep(fx), sy = smoothstep(fy), sz = smoothstep(fz);
        const n000 = hash(ix, iy, iz);
        const n100 = hash(ix+1, iy, iz);
        const n010 = hash(ix, iy+1, iz);
        const n110 = hash(ix+1, iy+1, iz);
        const n001 = hash(ix, iy, iz+1);
        const n101 = hash(ix+1, iy, iz+1);
        const n011 = hash(ix, iy+1, iz+1);
        const n111 = hash(ix+1, iy+1, iz+1);
        const nx00 = n000 + (n100 - n000) * sx;
        const nx10 = n010 + (n110 - n010) * sx;
        const nx01 = n001 + (n101 - n001) * sx;
        const nx11 = n011 + (n111 - n011) * sx;
        const nxy0 = nx00 + (nx10 - nx00) * sy;
        const nxy1 = nx01 + (nx11 - nx01) * sy;
        return nxy0 + (nxy1 - nxy0) * sz;
    }

    function fractal3D(x, y, z) {
        let val = 0, amp = 0.5, freq = 1;
        for (let i = 0; i < 4; i++) {
            val += amp * noise3D(x * freq, y * freq, z * freq);
            amp *= 0.5;
            freq *= 2;
        }
        return val;
    }

    // Chunk helpers
    function chunkKey(cx, cz) { return cx + ',' + cz; }

    function getBlock(wx, wy, wz) {
        if (wy < 0 || wy >= CHUNK_HEIGHT) return 0;
        const cx = Math.floor(wx / CHUNK_SIZE);
        const cz = Math.floor(wz / CHUNK_SIZE);
        const chunk = chunks.get(chunkKey(cx, cz));
        if (!chunk || !chunk.data) return 0;
        const lx = wx - cx * CHUNK_SIZE;
        const lz = wz - cz * CHUNK_SIZE;
        return chunk.data[lx + lz * CHUNK_SIZE + wy * CHUNK_SIZE * CHUNK_SIZE];
    }

    function setBlock(wx, wy, wz, val) {
        if (wy < 0 || wy >= CHUNK_HEIGHT) return;
        const cx = Math.floor(wx / CHUNK_SIZE);
        const cz = Math.floor(wz / CHUNK_SIZE);
        const chunk = chunks.get(chunkKey(cx, cz));
        if (!chunk || !chunk.data) return;
        const lx = wx - cx * CHUNK_SIZE;
        const lz = wz - cz * CHUNK_SIZE;
        chunk.data[lx + lz * CHUNK_SIZE + wy * CHUNK_SIZE * CHUNK_SIZE] = val;
    }

    function getBlockLocal(cx, cz, lx, y, lz) {
        if (y < 0 || y >= CHUNK_HEIGHT) return 0;
        const chunk = chunks.get(chunkKey(cx, cz));
        if (!chunk || !chunk.data) return 0;
        return chunk.data[lx + lz * CHUNK_SIZE + y * CHUNK_SIZE * CHUNK_SIZE];
    }

    // Terrain generation
    function generateChunk(cx, cz) {
        const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * CHUNK_HEIGHT);
        for (let lx = 0; lx < CHUNK_SIZE; lx++) {
            for (let lz = 0; lz < CHUNK_SIZE; lz++) {
                const wx = cx * CHUNK_SIZE + lx;
                const wz = cz * CHUNK_SIZE + lz;
                const m = fractal2D(wx * 0.004, wz * 0.004);
                const h = fractal2D(wx * 0.02, wz * 0.02);
                const H = Math.floor(5 + m * m * 58 + h * 10);
                const clampedH = Math.min(H, CHUNK_HEIGHT - 1);

                for (let y = 0; y <= clampedH && y < CHUNK_HEIGHT; y++) {
                    let block;
                    if (y === 0) {
                        block = 3;
                    } else if (y >= clampedH) {
                        if (clampedH >= 46) block = 7;
                        else if (clampedH >= 37) block = 3;
                        else if (clampedH <= 16) block = 4;
                        else block = 1;
                    } else if (y >= clampedH - 3) {
                        if (clampedH <= 16) block = 4;
                        else if (clampedH >= 37) block = 3;
                        else block = 2;
                    } else {
                        block = 3;
                    }
                    // Caves
                    if (y >= 3 && y <= clampedH - 2) {
                        if (fractal3D(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
                            block = 0;
                        }
                    }
                    data[lx + lz * CHUNK_SIZE + y * CHUNK_SIZE * CHUNK_SIZE] = block;
                }

                // Trees
                if (clampedH > 16 && clampedH < 46) {
                    const th = hash(wx, 0, wz);
                    if (th < 0.02 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13) {
                        // Trunk: H+1 to H+4
                        for (let ty = clampedH + 1; ty <= clampedH + 4 && ty < CHUNK_HEIGHT; ty++) {
                            data[lx + lz * CHUNK_SIZE + ty * CHUNK_SIZE * CHUNK_SIZE] = 5;
                        }
                        // 5x5 leaves at H+5, H+6
                        for (let dy = 5; dy <= 6; dy++) {
                            const yy = clampedH + dy;
                            if (yy >= CHUNK_HEIGHT) continue;
                            for (let dx = -2; dx <= 2; dx++) {
                                for (let dz = -2; dz <= 2; dz++) {
                                    const lxx = lx + dx, lzz = lz + dz;
                                    if (lxx >= 0 && lxx < CHUNK_SIZE && lzz >= 0 && lzz < CHUNK_SIZE) {
                                        const idx = lxx + lzz * CHUNK_SIZE + yy * CHUNK_SIZE * CHUNK_SIZE;
                                        if (data[idx] === 0) data[idx] = 6;
                                    }
                                }
                            }
                        }
                        // 3x3 leaves at H+7
                        const yy7 = clampedH + 7;
                        if (yy7 < CHUNK_HEIGHT) {
                            for (let dx = -1; dx <= 1; dx++) {
                                for (let dz = -1; dz <= 1; dz++) {
                                    const lxx = lx + dx, lzz = lz + dz;
                                    if (lxx >= 0 && lxx < CHUNK_SIZE && lzz >= 0 && lzz < CHUNK_SIZE) {
                                        const idx = lxx + lzz * CHUNK_SIZE + yy7 * CHUNK_SIZE * CHUNK_SIZE;
                                        if (data[idx] === 0) data[idx] = 6;
                                    }
                                }
                            }
                        }
                        // 1 leaf at H+8
                        const yy8 = clampedH + 8;
                        if (yy8 < CHUNK_HEIGHT) {
                            const idx = lx + lz * CHUNK_SIZE + yy8 * CHUNK_SIZE * CHUNK_SIZE;
                            if (data[idx] === 0) data[idx] = 6;
                        }
                    }
                }
            }
        }
        return data;
    }

    // Mesh building
    function buildChunkMesh(cx, cz) {
        const positions = [];
        const normals = [];
        const colors = [];
        const key = chunkKey(cx, cz);
        const chunk = chunks.get(key);
        if (!chunk || !chunk.data) return null;

        for (let lx = 0; lx < CHUNK_SIZE; lx++) {
            for (let lz = 0; lz < CHUNK_SIZE; lz++) {
                for (let y = 0; y < CHUNK_HEIGHT; y++) {
                    const block = chunk.data[lx + lz * CHUNK_SIZE + y * CHUNK_SIZE * CHUNK_SIZE];
                    if (block === 0) continue;

                    const wx = cx * CHUNK_SIZE + lx;
                    const wz = cz * CHUNK_SIZE + lz;
                    const color = BLOCK_COLORS[block];
                    const cr = ((color >> 16) & 0xff) / 255;
                    const cg = ((color >> 8) & 0xff) / 255;
                    const cb = (color & 0xff) / 255;

                    for (let f = 0; f < FACES.length; f++) {
                        const face = FACES[f];
                        const nx = wx + face.dir[0];
                        const ny = y + face.dir[1];
                        const nz = wz + face.dir[2];
                        if (getBlock(nx, ny, nz) !== 0) continue;

                        const v = face.verts;
                        const tris = [0,1,2, 0,2,3];
                        for (let i = 0; i < 6; i++) {
                            const vi = tris[i];
                            positions.push(
                                wx + v[vi][0],
                                y + v[vi][1],
                                wz + v[vi][2]
                            );
                            normals.push(face.dir[0], face.dir[1], face.dir[2]);
                            colors.push(cr * face.light, cg * face.light, cb * face.light);
                        }
                    }
                }
            }
        }

        if (positions.length === 0) return null;

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

        const mesh = new THREE.Mesh(geometry, material);
        mesh.userData.cx = cx;
        mesh.userData.cz = cz;
        return mesh;
    }

    function rebuildChunk(cx, cz) {
        const key = chunkKey(cx, cz);
        const chunk = chunks.get(key);
        if (!chunk) return;
        // Remove old mesh
        if (chunk.mesh) {
            scene.remove(chunk.mesh);
            chunk.mesh.geometry.dispose();
            const idx = chunkMeshes.indexOf(chunk.mesh);
            if (idx !== -1) chunkMeshes.splice(idx, 1);
            chunk.mesh = null;
        }
        // Build new mesh
        const mesh = buildChunkMesh(cx, cz);
        if (mesh) {
            scene.add(mesh);
            chunkMeshes.push(mesh);
            chunk.mesh = mesh;
        }
    }

    // Collision
    function collides(px, py, pz) {
        const minX = Math.floor(px - PLAYER_HALF + 0.001);
        const maxX = Math.floor(px + PLAYER_HALF - 0.001);
        const minY = Math.floor(py + 0.001);
        const maxY = Math.floor(py + PLAYER_HEIGHT - 0.001);
        const minZ = Math.floor(pz - PLAYER_HALF + 0.001);
        const maxZ = Math.floor(pz + PLAYER_HALF - 0.001);
        for (let x = minX; x <= maxX; x++)
            for (let y = minY; y <= maxY; y++)
                for (let z = minZ; z <= maxZ; z++)
                    if (getBlock(x, y, z) !== 0) return true;
        return false;
    }

    // Find spawn
    function findSpawn() {
        const sx = 8, sz = 8;
        for (let y = CHUNK_HEIGHT - 1; y >= 0; y--) {
            if (getBlock(sx, y, sz) !== 0) return y + 1;
        }
        return 40;
    }

    // Init
    function init() {
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87ceeb);
        scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

        camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
        camera.rotation.order = 'YXZ';

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(renderer.domElement);

        material = new THREE.MeshLambertMaterial({ vertexColors: true });

        // Lights
        const ambient = new THREE.AmbientLight(0xffffff, 0.65);
        scene.add(ambient);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(50, 100, 30);
        scene.add(dirLight);

        // Outline
        const outlineGeo = new THREE.BoxGeometry(1.005, 1.005, 1.005);
        const edges = new THREE.EdgesGeometry(outlineGeo);
        outlineMesh = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 }));
        outlineMesh.visible = false;
        scene.add(outlineMesh);

        // Clouds
        cloudGroup = new THREE.Group();
        const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
        for (let i = 0; i < 25; i++) {
            const w = 10 + hash(i, 100, 0) * 30;
            const d = 8 + hash(i, 200, 0) * 20;
            const geo = new THREE.BoxGeometry(w, 1.5, d);
            const cloud = new THREE.Mesh(geo, cloudMat);
            cloud.position.set(
                (hash(i, 300, 0) - 0.5) * 300,
                88 + hash(i, 400, 0) * 4,
                (hash(i, 500, 0) - 0.5) * 300
            );
            cloudGroup.add(cloud);
        }
        scene.add(cloudGroup);

        // Water
        const waterGeo = new THREE.PlaneGeometry(600, 600);
        const waterMat = new THREE.MeshLambertMaterial({ color: 0x3399ff, transparent: true, opacity: 0.5 });
        waterPlane = new THREE.Mesh(waterGeo, waterMat);
        waterPlane.rotation.x = -Math.PI / 2;
        waterPlane.position.y = 14.3;
        scene.add(waterPlane);

        // Events
        setupEvents();
        setupHotbar();

        // Spawn player
        playerY = findSpawn() + 1;
        camera.position.set(playerX, playerY + EYE_HEIGHT, playerZ);

        lastTime = performance.now();
        requestAnimationFrame(loop);
    }

    // Events
    function setupEvents() {
        const overlay = document.getElementById('overlay');
        overlay.addEventListener('click', () => {
            renderer.domElement.requestPointerLock();
        });

        document.addEventListener('pointerlockchange', () => {
            locked = document.pointerLockElement === renderer.domElement;
            overlay.style.display = locked ? 'none' : 'flex';
        });

        document.addEventListener('mousemove', (e) => {
            if (!locked) return;
            yaw -= e.movementX * SENSITIVITY;
            pitch -= e.movementY * SENSITIVITY;
            pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, pitch));
        });

        document.addEventListener('mousedown', (e) => {
            if (!locked) return;
            e.preventDefault();
            if (e.button === 0) breakBlock();
            else if (e.button === 2) placeBlock();
        });

        document.addEventListener('contextmenu', (e) => e.preventDefault());

        document.addEventListener('keydown', (e) => {
            keys[e.code] = true;
            if (e.key >= '1' && e.key <= '7') {
                selectedSlot = parseInt(e.key) - 1;
                updateHotbar();
            }
        });

        document.addEventListener('keyup', (e) => { keys[e.code] = false; });

        document.addEventListener('wheel', (e) => {
            if (!locked) return;
            selectedSlot = (selectedSlot + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
            updateHotbar();
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    // Hotbar
    function setupHotbar() {
        const hotbar = document.getElementById('hotbar');
        for (let i = 0; i < 7; i++) {
            const slot = document.createElement('div');
            slot.className = 'slot' + (i === 0 ? ' selected' : '');
            slot.id = 'slot' + i;
            const color = BLOCK_COLORS[i + 1];
            slot.style.background = '#' + color.toString(16).padStart(6, '0');
            const span = document.createElement('span');
            span.textContent = (i + 1);
            slot.appendChild(span);
            hotbar.appendChild(slot);
        }
    }

    function updateHotbar() {
        for (let i = 0; i < 7; i++) {
            const el = document.getElementById('slot' + i);
            el.className = 'slot' + (i === selectedSlot ? ' selected' : '');
        }
    }

    // Break & Place
    function breakBlock() {
        if (!targetBlock) return;
        const { x, y, z } = targetBlock;
        if (y <= 0) return;
        setBlock(x, y, z, 0);
        rebuildAtWorld(x, y, z);
    }

    function placeBlock() {
        if (!targetBlock) return;
        const px2 = Math.floor(targetBlock.px + targetBlock.nx * 0.5);
        const py2 = Math.floor(targetBlock.py + targetBlock.ny * 0.5);
        const pz2 = Math.floor(targetBlock.pz + targetBlock.nz * 0.5);
        if (getBlock(px2, py2, pz2) !== 0) return;
        // Check overlap with player
        const minX = playerX - PLAYER_HALF, maxX = playerX + PLAYER_HALF;
        const minY = playerY, maxY = playerY + PLAYER_HEIGHT;
        const minZ = playerZ - PLAYER_HALF, maxZ = playerZ + PLAYER_HALF;
        if (px2 + 1 > minX && px2 < maxX && py2 + 1 > minY && py2 < maxY && pz2 + 1 > minZ && pz2 < maxZ) return;
        setBlock(px2, py2, pz2, selectedSlot + 1);
        rebuildAtWorld(px2, py2, pz2);
    }

    function rebuildAtWorld(wx, wy, wz) {
        const cx = Math.floor(wx / CHUNK_SIZE);
        const cz = Math.floor(wz / CHUNK_SIZE);
        const lx = wx - cx * CHUNK_SIZE;
        const lz = wz - cz * CHUNK_SIZE;
        rebuildChunk(cx, cz);
        if (lx === 0) rebuildChunk(cx - 1, cz);
        if (lx === CHUNK_SIZE - 1) rebuildChunk(cx + 1, cz);
        if (lz === 0) rebuildChunk(cx, cz - 1);
        if (lz === CHUNK_SIZE - 1) rebuildChunk(cx, cz + 1);
    }

    // Raycast
    const raycaster = new THREE.Raycaster();
    function doRaycast() {
        raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
        raycaster.far = REACH;
        const intersects = raycaster.intersectObjects(chunkMeshes);
        if (intersects.length > 0) {
            const hit = intersects[0];
            const p = hit.point;
            const n = hit.face.normal;
            // Break target: floor(p - n*0.5)
            const bx = Math.floor(p.x - n.x * 0.5);
            const by = Math.floor(p.y - n.y * 0.5);
            const bz = Math.floor(p.z - n.z * 0.5);
            // Place target: floor(p + n*0.5)
            const px2 = Math.floor(p.x + n.x * 0.5);
            const py2 = Math.floor(p.y + n.y * 0.5);
            const pz2 = Math.floor(p.z + n.z * 0.5);
            targetBlock = { x: bx, y: by, z: bz, px: p.x, py: p.y, pz: p.z, nx: n.x, ny: n.y, nz: n.z };
            outlineMesh.visible = true;
            outlineMesh.position.set(bx + 0.5, by + 0.5, bz + 0.5);
        } else {
            targetBlock = null;
            outlineMesh.visible = false;
        }
    }

    // Chunk management
    function updateChunks() {
        const pcx = Math.floor(playerX / CHUNK_SIZE);
        const pcz = Math.floor(playerZ / CHUNK_SIZE);
        let genCount = 0;
        let meshCount = 0;

        // Generate data for chunks within RENDER_DIST
        for (let dx = -RENDER_DIST; dx <= RENDER_DIST && genCount < 4; dx++) {
            for (let dz = -RENDER_DIST; dz <= RENDER_DIST && genCount < 4; dz++) {
                const cx = pcx + dx;
                const cz = pcz + dz;
                const key = chunkKey(cx, cz);
                if (!chunks.has(key)) {
                    chunks.set(key, { data: generateChunk(cx, cz), mesh: null });
                    genCount++;
                }
            }
        }

        // Build meshes for chunks within MESH_DIST with all 4 neighbors having data
        for (let dx = -MESH_DIST; dx <= MESH_DIST && meshCount < 2; dx++) {
            for (let dz = -MESH_DIST; dz <= MESH_DIST && meshCount < 2; dz++) {
                const cx = pcx + dx;
                const cz = pcz + dz;
                const key = chunkKey(cx, cz);
                const chunk = chunks.get(key);
                if (!chunk || !chunk.data) continue;
                if (chunk.mesh) continue;
                // Check 4 neighbors have data
                const n1 = chunks.get(chunkKey(cx - 1, cz));
                const n2 = chunks.get(chunkKey(cx + 1, cz));
                const n3 = chunks.get(chunkKey(cx, cz - 1));
                const n4 = chunks.get(chunkKey(cx, cz + 1));
                if (!n1 || !n1.data || !n2 || !n2.data || !n3 || !n3.data || !n4 || !n4.data) continue;
                const mesh = buildChunkMesh(cx, cz);
                if (mesh) {
                    scene.add(mesh);
                    chunkMeshes.push(mesh);
                    chunk.mesh = mesh;
                    meshCount++;
                }
            }
        }

        // Remove far chunks
        const toRemove = [];
        chunks.forEach((chunk, key) => {
            const parts = key.split(',');
            const cx = parseInt(parts[0]);
            const cz = parseInt(parts[1]);
            const dist = Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz));
            if (dist > UNLOAD_DIST) {
                toRemove.push(key);
            }
        });
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

    // Player update
    function updatePlayer(dt) {
        if (dt > 0.1) dt = 0.1;

        // Movement
        let mx = 0, mz = 0;
        if (keys['KeyW'] || keys['ArrowUp']) mz -= 1;
        if (keys['KeyS'] || keys['ArrowDown']) mz += 1;
        if (keys['KeyA'] || keys['ArrowLeft']) mx -= 1;
        if (keys['KeyD'] || keys['ArrowRight']) mx += 1;

        const sinY = Math.sin(yaw), cosY = Math.cos(yaw);
        let vx = (mx * cosY - mz * sinY) * MOVE_SPEED;
        let vz = (mx * sinY + mz * cosY) * MOVE_SPEED;

        // Gravity
        velY -= GRAVITY * dt;
        if (keys['Space'] && onGround) {
            velY = JUMP_VEL;
            onGround = false;
        }

        // Move X
        const newX = playerX + vx * dt;
        if (!collides(newX, playerY, playerZ)) {
            playerX = newX;
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

        // Move Z
        const newZ = playerZ + vz * dt;
        if (!collides(playerX, playerY, newZ)) {
            playerZ = newZ;
        }

        // Fall below world
        if (playerY < -20) {
            playerX = 8; playerZ = 8;
            playerY = findSpawn() + 1;
            velY = 0;
        }

        // Camera
        camera.position.set(playerX, playerY + EYE_HEIGHT, playerZ);
        camera.rotation.set(pitch, yaw, 0);
    }

    // Clouds update
    function updateClouds(dt) {
        cloudGroup.children.forEach((cloud, i) => {
            cloud.position.x += dt * 1.5;
            // Wrap around player
            const dx = cloud.position.x - playerX;
            if (dx > 200) cloud.position.x -= 400;
            if (dx < -200) cloud.position.x += 400;
            const dz = cloud.position.z - playerZ;
            if (dz > 200) cloud.position.z -= 400;
            if (dz < -200) cloud.position.z += 400;
        });
    }

    // Main loop
    function loop() {
        const now = performance.now();
        const dt = (now - lastTime) / 1000;
        lastTime = now;

        updatePlayer(dt);
        updateChunks();
        doRaycast();
        updateClouds(dt);

        // Water follows player
        waterPlane.position.x = playerX;
        waterPlane.position.z = playerZ;

        renderer.render(scene, camera);
        requestAnimationFrame(loop);
    }

    init();
})();
</script>
</body>
</html>
```