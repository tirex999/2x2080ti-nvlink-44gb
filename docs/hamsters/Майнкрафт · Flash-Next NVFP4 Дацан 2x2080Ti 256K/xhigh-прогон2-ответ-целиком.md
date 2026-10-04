```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>mc.html</title>
<style>
html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #87ceeb;
    user-select: none;
}

canvas {
    display: block;
}

#overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.65);
    color: white;
    font-family: monospace, sans-serif;
    z-index: 20;
    cursor: pointer;
    text-align: center;
}

#overlay.hidden {
    display: none;
}

.panel {
    padding: 24px 32px;
    border: 2px solid rgba(255, 255, 255, 0.25);
    background: rgba(0, 0, 0, 0.35);
}

.panel h1 {
    margin: 0 0 16px;
    font-size: 48px;
    letter-spacing: 4px;
    text-shadow: 3px 3px #000;
}

.panel p {
    margin: 8px 0;
    font-size: 16px;
}

.play {
    margin-top: 18px;
    font-size: 22px;
    color: #aaffaa;
}

#crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 22px;
    height: 22px;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 10;
}

#crosshair::before,
#crosshair::after {
    content: "";
    position: absolute;
    background: white;
    box-shadow: 0 0 2px black;
}

#crosshair::before {
    left: 50%;
    top: 0;
    width: 2px;
    height: 100%;
    transform: translateX(-50%);
}

#crosshair::after {
    top: 50%;
    left: 0;
    height: 2px;
    width: 100%;
    transform: translateY(-50%);
}

#hotbar {
    position: fixed;
    left: 50%;
    bottom: 16px;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    padding: 6px;
    background: rgba(0, 0, 0, 0.45);
    border-radius: 6px;
    pointer-events: none;
    z-index: 10;
}

.slot {
    box-sizing: border-box;
    width: 48px;
    height: 48px;
    border: 2px solid rgba(255, 255, 255, 0.25);
    color: white;
    font-family: monospace;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-shadow: 1px 1px black;
}

.slot.selected {
    border: 3px solid white;
}
</style>
</head>
<body>
<div id="overlay">
    <div class="panel">
        <h1>mc.html</h1>
        <p>WASD move · Space jump · Mouse look</p>
        <p>Left click break · Right click place</p>
        <p>Keys 1-7 or mouse wheel select block</p>
        <p class="play">Click to play</p>
    </div>
</div>

<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
    const CHUNK_SIZE = 16;
    const WORLD_HEIGHT = 80;

    const AIR = 0;
    const GRASS = 1;
    const DIRT = 2;
    const STONE = 3;
    const SAND = 4;
    const WOOD = 5;
    const LEAVES = 6;
    const SNOW = 7;

    const BLOCK_HEX = [
        0,
        0x4caf50,
        0x795548,
        0x9e9e9e,
        0xe7d9a8,
        0x8d6e63,
        0x2e7d32,
        0xffffff
    ];

    const BLOCK_COLORS = BLOCK_HEX.map(function (hex) {
        if (hex === 0) return [0, 0, 0];
        return [
            ((hex >> 16) & 255) / 255,
            ((hex >> 8) & 255) / 255,
            (hex & 255) / 255
        ];
    });

    const SELECTED_BLOCKS = [GRASS, DIRT, STONE, SAND, WOOD, LEAVES, SNOW];
    let selected = 0;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

    const camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        400
    );
    camera.rotation.order = "YXZ";

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    const canvas = renderer.domElement;

    scene.add(new THREE.AmbientLight(0xffffff, 0.65));
    const sun = new THREE.DirectionalLight(0xffffff, 0.8);
    sun.position.set(0.5, 1, 0.35);
    scene.add(sun);

    const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

    const PLAYER_HALF = 0.3;
    const PLAYER_HEIGHT = 1.8;
    const EYE = 1.62;
    const GRAVITY = 25;
    const JUMP = 8.5;
    const SPEED = 5.5;
    const EPS = 1e-4;

    const player = { position: new THREE.Vector3(8.5, 0, 8.5) };
    let yaw = 0;
    let pitch = 0;
    let velY = 0;
    let onGround = false;

    function hashInt(x, y, z) {
        x |= 0;
        y |= 0;
        z |= 0;

        let n =
            Math.imul(x, 0x27d4eb2d) ^
            Math.imul(y, 0x165667b1) ^
            Math.imul(z, 0x9e3779b1);

        n ^= n >>> 16;
        n = Math.imul(n, 0x85ebca6b);
        n ^= n >>> 13;
        n = Math.imul(n, 0xc2b2ae35);
        n ^= n >>> 16;

        return (n >>> 0) / 4294967296;
    }

    function smooth(t) {
        return t * t * (3 - 2 * t);
    }

    function noise2(x, y) {
        const x0 = Math.floor(x);
        const y0 = Math.floor(y);
        const fx = smooth(x - x0);
        const fy = smooth(y - y0);

        const v00 = hashInt(x0, y0, 0);
        const v10 = hashInt(x0 + 1, y0, 0);
        const v01 = hashInt(x0, y0 + 1, 0);
        const v11 = hashInt(x0 + 1, y0 + 1, 0);

        const a = v00 + (v10 - v00) * fx;
        const b = v01 + (v11 - v01) * fx;
        return a + (b - a) * fy;
    }

    function fractal2(x, y) {
        let amp = 1;
        let freq = 1;
        let sum = 0;
        let max = 0;

        for (let i = 0; i < 4; i++) {
            sum += amp * noise2(x * freq, y * freq);
            max += amp;
            amp *= 0.5;
            freq *= 2;
        }

        return sum / max;
    }

    function noise3(x, y, z) {
        const x0 = Math.floor(x);
        const y0 = Math.floor(y);
        const z0 = Math.floor(z);
        const fx = smooth(x - x0);
        const fy = smooth(y - y0);
        const fz = smooth(z - z0);

        const c000 = hashInt(x0, y0, z0);
        const c100 = hashInt(x0 + 1, y0, z0);
        const c010 = hashInt(x0, y0 + 1, z0);
        const c110 = hashInt(x0 + 1, y0 + 1, z0);
        const c001 = hashInt(x0, y0, z0 + 1);
        const c101 = hashInt(x0 + 1, y0, z0 + 1);
        const c011 = hashInt(x0, y0 + 1, z0 + 1);
        const c111 = hashInt(x0 + 1, y0 + 1, z0 + 1);

        const x00 = c000 + (c100 - c000) * fx;
        const x10 = c010 + (c110 - c010) * fx;
        const x01 = c001 + (c101 - c001) * fx;
        const x11 = c011 + (c111 - c011) * fx;

        const y00 = x00 + (x10 - x00) * fy;
        const y01 = x01 + (x11 - x01) * fy;

        return y00 + (y01 - y00) * fz;
    }

    function columnHeight(wx, wz) {
        const m = fractal2(wx * 0.004, wz * 0.004);
        const h = fractal2(wx * 0.02, wz * 0.02);
        return Math.floor(5 + m * m * 58 + h * 10);
    }

    const chunks = new Map();
    const chunkMeshes = [];

    function chunkKey(cx, cz) {
        return cx + "," + cz;
    }

    function floorChunk(v) {
        return Math.floor(v / CHUNK_SIZE);
    }

    function chunkIndex(lx, y, lz) {
        return (y * CHUNK_SIZE + lz) * CHUNK_SIZE + lx;
    }

    function getBlock(wx, wy, wz) {
        if (wy < 0 || wy >= WORLD_HEIGHT) return AIR;

        const cx = floorChunk(wx);
        const cz = floorChunk(wz);
        const chunk = chunks.get(chunkKey(cx, cz));
        if (!chunk) return AIR;

        const lx = wx - cx * CHUNK_SIZE;
        const lz = wz - cz * CHUNK_SIZE;
        return chunk.data[chunkIndex(lx, wy, lz)];
    }

    function setBlock(wx, wy, wz, id) {
        if (wy < 0 || wy >= WORLD_HEIGHT) return false;

        const cx = floorChunk(wx);
        const cz = floorChunk(wz);
        const chunk = ensureChunkData(cx, cz);

        const lx = wx - cx * CHUNK_SIZE;
        const lz = wz - cz * CHUNK_SIZE;

        chunk.data[chunkIndex(lx, wy, lz)] = id;
        chunk.dirty = true;
        return true;
    }

    function ensureChunkData(cx, cz) {
        const key = chunkKey(cx, cz);
        let chunk = chunks.get(key);

        if (!chunk) {
            chunk = {
                cx: cx,
                cz: cz,
                data: generateChunkData(cx, cz),
                mesh: null,
                built: false,
                dirty: true
            };
            chunks.set(key, chunk);
            markNeighborsDirty(cx, cz);
        }

        return chunk;
    }

    function markNeighborsDirty(cx, cz) {
        const pcx = floorChunk(player.position.x);
        const pcz = floorChunk(player.position.z);
        const dirs = [
            [1, 0],
            [-1, 0],
            [0, 1],
            [0, -1]
        ];

        for (let i = 0; i < dirs.length; i++) {
            const neighbor = chunks.get(chunkKey(cx + dirs[i][0], cz + dirs[i][1]));
            if (!neighbor) continue;

            neighbor.dirty = true;
            neighbor.built = false;

            if (neighbor.mesh) {
                const dist = Math.max(
                    Math.abs(neighbor.cx - pcx),
                    Math.abs(neighbor.cz - pcz)
                );

                if (dist > 4) {
                    scene.remove(neighbor.mesh);
                    neighbor.mesh.geometry.dispose();
                    neighbor.mesh = null;
                } else {
                    neighbor.mesh.visible = false;
                }
            }
        }
    }

    function hasAllNeighbors(cx, cz) {
        return (
            chunks.has(chunkKey(cx + 1, cz)) &&
            chunks.has(chunkKey(cx - 1, cz)) &&
            chunks.has(chunkKey(cx, cz + 1)) &&
            chunks.has(chunkKey(cx, cz - 1))
        );
    }

    function setLocalIfAir(data, lx, y, lz, id) {
        if (y < 0 || y >= WORLD_HEIGHT) return;
        if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE) return;

        const i = chunkIndex(lx, y, lz);
        if (data[i] === AIR) data[i] = id;
    }

    function addLeafLayer(data, lx, lz, y, r) {
        for (let dz = -r; dz <= r; dz++) {
            for (let dx = -r; dx <= r; dx++) {
                setLocalIfAir(data, lx + dx, y, lz + dz, LEAVES);
            }
        }
    }

    function generateChunkData(cx, cz) {
        const data = new Uint8Array(CHUNK_SIZE * WORLD_HEIGHT * CHUNK_SIZE);
        const heights = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE);

        for (let lz = 0; lz < CHUNK_SIZE; lz++) {
            for (let lx = 0; lx < CHUNK_SIZE; lx++) {
                const wx = cx * CHUNK_SIZE + lx;
                const wz = cz * CHUNK_SIZE + lz;
                const H = columnHeight(wx, wz);
                heights[lz * CHUNK_SIZE + lx] = H;

                const top = Math.min(H, WORLD_HEIGHT);

                for (let y = 0; y < top; y++) {
                    let id = AIR;

                    if (y === 0) {
                        id = STONE;
                    } else if (y < H) {
                        if (y < H - 3) {
                            id = STONE;
                        } else {
                            if (H <= 16) id = SAND;
                            else if (H >= 37) id = STONE;
                            else id = DIRT;
                        }

                        if (y === H - 1) {
                            if (H >= 46) id = SNOW;
                            else if (H >= 37) id = STONE;
                            else if (H <= 16) id = SAND;
                            else id = GRASS;
                        }

                        if (id !== AIR && y >= 3 && y <= H - 2) {
                            if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
                                id = AIR;
                            }
                        }
                    }

                    data[chunkIndex(lx, y, lz)] = id;
                }
            }
        }

        for (let lz = 0; lz < CHUNK_SIZE; lz++) {
            for (let lx = 0; lx < CHUNK_SIZE; lx++) {
                if (lx < 2 || lx > 13 || lz < 2 || lz > 13) continue;

                const wx = cx * CHUNK_SIZE + lx;
                const wz = cz * CHUNK_SIZE + lz;

                if (Math.abs(wx - 8) <= 1 && Math.abs(wz - 8) <= 1) continue;

                const H = heights[lz * CHUNK_SIZE + lx];
                if (H < 17 || H >= 37) continue;
                if (data[chunkIndex(lx, H - 1, lz)] !== GRASS) continue;
                if (hashInt(wx, 12345, wz) >= 0.02) continue;

                const topY = H + 3;
                if (topY + 3 >= WORLD_HEIGHT) continue;

                for (let i = 0; i < 4; i++) {
                    setLocalIfAir(data, lx, H + i, lz, WOOD);
                }

                addLeafLayer(data, lx, lz, topY, 2);
                addLeafLayer(data, lx, lz, topY + 1, 2);
                addLeafLayer(data, lx, lz, topY + 2, 1);
                setLocalIfAir(data, lx, topY + 3, lz, LEAVES);
            }
        }

        return data;
    }

    const TRIANGLE_ORDER = [0, 1, 2, 0, 2, 3];

    const FACES = [
        {
            dir: [1, 0, 0],
            shade: 0.8,
            verts: [
                [1, 0, 0],
                [1, 1, 0],
                [1, 1, 1],
                [1, 0, 1]
            ]
        },
        {
            dir: [-1, 0, 0],
            shade: 0.8,
            verts: [
                [0, 0, 1],
                [0, 1, 1],
                [0, 1, 0],
                [0, 0, 0]
            ]
        },
        {
            dir: [0, 1, 0],
            shade: 1.0,
            verts: [
                [0, 1, 1],
                [1, 1, 1],
                [1, 1, 0],
                [0, 1, 0]
            ]
        },
        {
            dir: [0, -1, 0],
            shade: 0.55,
            verts: [
                [0, 0, 0],
                [1, 0, 0],
                [1, 0, 1],
                [0, 0, 1]
            ]
        },
        {
            dir: [0, 0, 1],
            shade: 0.8,
            verts: [
                [0, 0, 1],
                [1, 0, 1],
                [1, 1, 1],
                [0, 1, 1]
            ]
        },
        {
            dir: [0, 0, -1],
            shade: 0.8,
            verts: [
                [1, 0, 0],
                [0, 0, 0],
                [0, 1, 0],
                [1, 1, 0]
            ]
        }
    ];

    function getBlockNeighbor(chunk, lx, ly, lz) {
        if (ly < 0 || ly >= WORLD_HEIGHT) return AIR;

        if (lx >= 0 && lx < CHUNK_SIZE && lz >= 0 && lz < CHUNK_SIZE) {
            return chunk.data[chunkIndex(lx, ly, lz)];
        }

        return getBlock(
            chunk.cx * CHUNK_SIZE + lx,
            ly,
            chunk.cz * CHUNK_SIZE + lz
        );
    }

    function addFace(positions, normals, colors, x, y, z, face, rgb) {
        const r = rgb[0] * face.shade;
        const g = rgb[1] * face.shade;
        const b = rgb[2] * face.shade;

        for (let i = 0; i < TRIANGLE_ORDER.length; i++) {
            const v = face.verts[TRIANGLE_ORDER[i]];

            positions.push(x + v[0], y + v[1], z + v[2]);
            normals.push(face.dir[0], face.dir[1], face.dir[2]);
            colors.push(r, g, b);
        }
    }

    function buildChunkMesh(chunk) {
        if (chunk.mesh) {
            scene.remove(chunk.mesh);
            chunk.mesh.geometry.dispose();
            chunk.mesh = null;
        }

        if (!hasAllNeighbors(chunk.cx, chunk.cz)) {
            chunk.built = false;
            chunk.dirty = true;
            return;
        }

        const positions = [];
        const normals = [];
        const colors = [];
        const data = chunk.data;

        for (let y = 0; y < WORLD_HEIGHT; y++) {
            for (let z = 0; z < CHUNK_SIZE; z++) {
                for (let x = 0; x < CHUNK_SIZE; x++) {
                    const id = data[chunkIndex(x, y, z)];
                    if (id === AIR) continue;

                    const wx = chunk.cx * CHUNK_SIZE + x;
                    const wz = chunk.cz * CHUNK_SIZE + z;
                    const rgb = BLOCK_COLORS[id];

                    for (let f = 0; f < FACES.length; f++) {
                        const face = FACES[f];
                        const nx = x + face.dir[0];
                        const ny = y + face.dir[1];
                        const nz = z + face.dir[2];

                        const neighbor = getBlockNeighbor(chunk, nx, ny, nz);
                        if (neighbor === AIR) {
                            addFace(positions, normals, colors, wx, y, wz, face, rgb);
                        }
                    }
                }
            }
        }

        chunk.built = true;
        chunk.dirty = false;

        if (positions.length === 0) return;

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute(
            "position",
            new THREE.BufferAttribute(new Float32Array(positions), 3)
        );
        geometry.setAttribute(
            "normal",
            new THREE.BufferAttribute(new Float32Array(normals), 3)
        );
        geometry.setAttribute(
            "color",
            new THREE.BufferAttribute(new Float32Array(colors), 3)
        );
        geometry.computeBoundingSphere();

        const mesh = new THREE.Mesh(geometry, blockMaterial);
        mesh.visible = true;
        scene.add(mesh);
        chunk.mesh = mesh;
    }

    function collides(x, y, z) {
        const minX = Math.floor(x - PLAYER_HALF + EPS);
        const maxX = Math.floor(x + PLAYER_HALF - EPS);
        const minY = Math.floor(y + EPS);
        const maxY = Math.floor(y + PLAYER_HEIGHT - EPS);
        const minZ = Math.floor(z - PLAYER_HALF + EPS);
        const maxZ = Math.floor(z + PLAYER_HALF - EPS);

        for (let ix = minX; ix <= maxX; ix++) {
            for (let iy = minY; iy <= maxY; iy++) {
                for (let iz = minZ; iz <= maxZ; iz++) {
                    if (getBlock(ix, iy, iz) !== AIR) return true;
                }
            }
        }

        return false;
    }

    function blockOverlapsPlayer(bx, by, bz) {
        const minX = player.position.x - PLAYER_HALF;
        const maxX = player.position.x + PLAYER_HALF;
        const minY = player.position.y;
        const maxY = player.position.y + PLAYER_HEIGHT;
        const minZ = player.position.z - PLAYER_HALF;
        const maxZ = player.position.z + PLAYER_HALF;

        return (
            bx + 1 > minX &&
            bx < maxX &&
            by + 1 > minY &&
            by < maxY &&
            bz + 1 > minZ &&
            bz < maxZ
        );
    }

    function respawn() {
        const sx = 8.5;
        const sz = 8.5;
        const H = columnHeight(8, 8);

        player.position.set(sx, H + 1, sz);
        velY = 0;
        onGround = false;

        const cx = floorChunk(sx);
        const cz = floorChunk(sz);

        for (let dz = -1; dz <= 1; dz++) {
            for (let dx = -1; dx <= 1; dx++) {
                ensureChunkData(cx + dx, cz + dz);
            }
        }
    }

    respawn();

    function updatePlayer(dt) {
        const forwardInput = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0);
        const strafeInput = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0);

        const fwdX = -Math.sin(yaw);
        const fwdZ = -Math.cos(yaw);
        const rightX = Math.cos(yaw);
        const rightZ = -Math.sin(yaw);

        let mx = fwdX * forwardInput + rightX * strafeInput;
        let mz = fwdZ * forwardInput + rightZ * strafeInput;

        const len = Math.sqrt(mx * mx + mz * mz);
        if (len > 0) {
            mx = (mx / len) * SPEED * dt;
            mz = (mz / len) * SPEED * dt;
        }

        const nx = player.position.x + mx;
        if (!collides(nx, player.position.y, player.position.z)) {
            player.position.x = nx;
        }

        const nz = player.position.z + mz;
        if (!collides(player.position.x, player.position.y, nz)) {
            player.position.z = nz;
        }

        if (keys.Space && onGround) {
            velY = JUMP;
            onGround = false;
        }

        velY -= GRAVITY * dt;
        const dy = velY * dt;
        const steps = Math.max(1, Math.ceil(Math.abs(dy) / 0.25));
        const step = dy / steps;

        onGround = false;

        for (let i = 0; i < steps; i++) {
            const oldY = player.position.y;
            const ny = oldY + step;

            if (!collides(player.position.x, ny, player.position.z)) {
                player.position.y = ny;
            } else {
                if (step < 0) {
                    let low = ny;
                    let high = oldY;

                    for (let j = 0; j < 10; j++) {
                        const mid = (low + high) / 2;
                        if (collides(player.position.x, mid, player.position.z)) {
                            low = mid;
                        } else {
                            high = mid;
                        }
                    }

                    player.position.y = high;
                    onGround = true;
                } else {
                    let low = oldY;
                    let high = ny;

                    for (let j = 0; j < 10; j++) {
                        const mid = (low + high) / 2;
                        if (collides(player.position.x, mid, player.position.z)) {
                            high = mid;
                        } else {
                            low = mid;
                        }
                    }

                    player.position.y = low;
                }

                velY = 0;
                break;
            }
        }

        if (player.position.y < -20) respawn();
    }

    function updateChunks() {
        const pcx = floorChunk(player.position.x);
        const pcz = floorChunk(player.position.z);

        let generated = 0;

        for (let r = 0; r <= 5 && generated < 4; r++) {
            for (let dx = -r; dx <= r && generated < 4; dx++) {
                for (let dz = -r; dz <= r && generated < 4; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;

                    const key = chunkKey(pcx + dx, pcz + dz);
                    if (!chunks.has(key)) {
                        ensureChunkData(pcx + dx, pcz + dz);
                        generated++;
                    }
                }
            }
        }

        let built = 0;

        for (let r = 0; r <= 4 && built < 2; r++) {
            for (let dx = -r; dx <= r && built < 2; dx++) {
                for (let dz = -r; dz <= r && built < 2; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;

                    const chunk = chunks.get(chunkKey(pcx + dx, pcz + dz));
                    if (chunk && (!chunk.built || chunk.dirty)) {
                        if (hasAllNeighbors(chunk.cx, chunk.cz)) {
                            buildChunkMesh(chunk);
                            built++;
                        }
                    }
                }
            }
        }

        const remove = [];

        chunks.forEach(function (chunk, key) {
            const dist = Math.max(
                Math.abs(chunk.cx - pcx),
                Math.abs(chunk.cz - pcz)
            );

            if (dist > 7) {
                if (chunk.mesh) {
                    scene.remove(chunk.mesh);
                    chunk.mesh.geometry.dispose();
                    chunk.mesh = null;
                }
                remove.push(key);
            }
        });

        for (let i = 0; i < remove.length; i++) {
            chunks.delete(remove[i]);
        }
    }

    function rebuildAt(wx, wy, wz) {
        const cx = floorChunk(wx);
        const cz = floorChunk(wz);
        const lx = wx - cx * CHUNK_SIZE;
        const lz = wz - cz * CHUNK_SIZE;

        ensureChunkData(cx, cz);

        if (lx === 0) ensureChunkData(cx - 1, cz);
        if (lx === CHUNK_SIZE - 1) ensureChunkData(cx + 1, cz);
        if (lz === 0) ensureChunkData(cx, cz - 1);
        if (lz === CHUNK_SIZE - 1) ensureChunkData(cx, cz + 1);

        buildChunkMesh(chunks.get(chunkKey(cx, cz)));

        if (lx === 0) buildChunkMesh(chunks.get(chunkKey(cx - 1, cz)));
        if (lx === CHUNK_SIZE - 1) buildChunkMesh(chunks.get(chunkKey(cx + 1, cz)));
        if (lz === 0) buildChunkMesh(chunks.get(chunkKey(cx, cz - 1)));
        if (lz === CHUNK_SIZE - 1) buildChunkMesh(chunks.get(chunkKey(cx, cz + 1)));
    }

    const outlineGeo = new THREE.EdgesGeometry(
        new THREE.BoxGeometry(1.001, 1.001, 1.001)
    );
    const outline = new THREE.LineSegments(
        outlineGeo,
        new THREE.LineBasicMaterial({ color: 0x000000 })
    );
    outline.visible = false;
    scene.add(outline);

    const raycaster = new THREE.Raycaster();
    const center = new THREE.Vector2(0, 0);

    const targetBlock = { x: 0, y: 0, z: 0 };
    const placeCell = { x: 0, y: 0, z: 0 };
    let hasTarget = false;

    function updateRaycast() {
        chunkMeshes.length = 0;
        chunks.forEach(function (chunk) {
            if (chunk.mesh && chunk.mesh.visible) {
                chunkMeshes.push(chunk.mesh);
            }
        });

        raycaster.near = 0;
        raycaster.far = 6;
        raycaster.setFromCamera(center, camera);

        const hits = raycaster.intersectObjects(chunkMeshes, false);

        if (hits.length > 0 && hits[0].face) {
            const p = hits[0].point;
            const n = hits[0].face.normal;

            targetBlock.x = Math.floor(p.x - n.x * 0.5);
            targetBlock.y = Math.floor(p.y - n.y * 0.5);
            targetBlock.z = Math.floor(p.z - n.z * 0.5);

            placeCell.x = Math.floor(p.x + n.x * 0.5);
            placeCell.y = Math.floor(p.y + n.y * 0.5);
            placeCell.z = Math.floor(p.z + n.z * 0.5);

            if (
                targetBlock.y >= 0 &&
                targetBlock.y < WORLD_HEIGHT &&
                getBlock(targetBlock.x, targetBlock.y, targetBlock.z) !== AIR
            ) {
                hasTarget = true;
                outline.visible = true;
                outline.position.set(
                    targetBlock.x + 0.5,
                    targetBlock.y + 0.5,
                    targetBlock.z + 0.5
                );
            } else {
                hasTarget = false;
                outline.visible = false;
            }
        } else {
            hasTarget = false;
            outline.visible = false;
        }
    }

    function breakBlock() {
        if (!hasTarget) return;

        const t = targetBlock;
        if (t.y === 0) return;
        if (getBlock(t.x, t.y, t.z) === AIR) return;

        setBlock(t.x, t.y, t.z, AIR);
        rebuildAt(t.x, t.y, t.z);
        updateRaycast();
    }

    function placeBlock() {
        if (!hasTarget) return;

        const c = placeCell;
        if (c.y < 0 || c.y >= WORLD_HEIGHT) return;
        if (getBlock(c.x, c.y, c.z) !== AIR) return;
        if (blockOverlapsPlayer(c.x, c.y, c.z)) return;

        setBlock(c.x, c.y, c.z, SELECTED_BLOCKS[selected]);
        rebuildAt(c.x, c.y, c.z);
        updateRaycast();
    }

    const clouds = [];
    const cloudMaterial = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.75,
        depthWrite: false
    });

    for (let i = 0; i < 25; i++) {
        const sx = 8 + hashInt(i, 100, 0) * 16;
        const sz = 8 + hashInt(i, 200, 0) * 16;

        const cloudGeo = new THREE.BoxGeometry(sx, 1, sz);
        const cloud = new THREE.Mesh(cloudGeo, cloudMaterial);

        cloud.position.set(
            hashInt(i, 300, 0) * 400 - 200,
            90 + hashInt(i, 400, 0) * 8,
            hashInt(i, 500, 0) * 400 - 200
        );

        scene.add(cloud);
        clouds.push(cloud);
    }

    const water = new THREE.Mesh(
        new THREE.PlaneGeometry(800, 800),
        new THREE.MeshBasicMaterial({
            color: 0x3b82f6,
            transparent: true,
            opacity: 0.55,
            depthWrite: false,
            side: THREE.DoubleSide
        })
    );
    water.rotation.x = -Math.PI / 2;
    water.position.y = 14.3;
    scene.add(water);

    function updateClouds(dt) {
        for (let i = 0; i < clouds.length; i++) {
            const cloud = clouds[i];

            cloud.position.x += 2 * dt;

            if (cloud.position.x > player.position.x + 200) {
                cloud.position.x -= 400;
            }
            if (cloud.position.x < player.position.x - 200) {
                cloud.position.x += 400;
            }

            if (cloud.position.z > player.position.z + 200) {
                cloud.position.z -= 400;
            }
            if (cloud.position.z < player.position.z - 200) {
                cloud.position.z += 400;
            }
        }

        water.position.set(player.position.x, 14.3, player.position.z);
    }

    function syncCamera() {
        camera.position.set(
            player.position.x,
            player.position.y + EYE,
            player.position.z
        );
        camera.rotation.set(pitch, yaw, 0);
        camera.updateMatrixWorld();
    }

    const overlay = document.getElementById("overlay");
    const hotbar = document.getElementById("hotbar");
    const slotEls = [];

    function hexString(hex) {
        let s = hex.toString(16);
        while (s.length < 6) s = "0" + s;
        return "#" + s;
    }

    SELECTED_BLOCKS.forEach(function (id, i) {
        const el = document.createElement("div");
        el.className = "slot";
        el.style.background = hexString(BLOCK_HEX[id]);
        el.textContent = String(i + 1);
        hotbar.appendChild(el);
        slotEls.push(el);
    });

    function updateHotbar() {
        slotEls.forEach(function (el, i) {
            el.classList.toggle("selected", i === selected);
        });
    }

    updateHotbar();

    let active = false;
    const keys = {};

    overlay.addEventListener("click", function () {
        if (canvas.requestPointerLock) canvas.requestPointerLock();
    });

    document.addEventListener("pointerlockchange", function () {
        active = document.pointerLockElement === canvas;
        overlay.classList.toggle("hidden", active);

        if (!active) {
            for (const k in keys) keys[k] = false;
            velY = 0;
        }
    });

    document.addEventListener("mousemove", function (e) {
        if (!active) return;

        yaw -= e.movementX * 0.002;
        pitch -= e.movementY * 0.002;

        const limit = Math.PI / 2 - 0.01;
        pitch = Math.max(-limit, Math.min(limit, pitch));
    });

    document.addEventListener("mousedown", function (e) {
        if (!active) return;

        syncCamera();
        updateRaycast();

        if (e.button === 0) {
            breakBlock();
        } else if (e.button === 2) {
            placeBlock();
        }
    });

    window.addEventListener("keydown", function (e) {
        keys[e.code] = true;

        if (e.code === "Space") e.preventDefault();

        if (e.code.indexOf("Digit") === 0) {
            const n = parseInt(e.code.slice(5), 10);
            if (n >= 1 && n <= 7) {
                selected = n - 1;
                updateHotbar();
            }
        }
    });

    window.addEventListener("keyup", function (e) {
        keys[e.code] = false;
    });

    window.addEventListener("wheel", function (e) {
        if (!active) return;

        selected = (selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
        updateHotbar();
    }, { passive: true });

    window.addEventListener("resize", function () {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    document.addEventListener("contextmenu", function (e) {
        e.preventDefault();
    });

    let last = performance.now();

    function animate() {
        requestAnimationFrame(animate);

        const now = performance.now();
        let dt = (now - last) / 1000;
        last = now;

        if (dt > 0.05) dt = 0.05;

        updateChunks();

        if (active) {
            updatePlayer(dt);
        }

        updateClouds(dt);
        syncCamera();
        updateRaycast();

        renderer.render(scene, camera);
    }

    animate();
})();
</script>
</body>
</html>
```