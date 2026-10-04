```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>mc.html - voxel sandbox</title>
<style>
  html, body { margin:0; padding:0; height:100%; overflow:hidden; background:#000; font-family:Arial, Helvetica, sans-serif; }
  canvas { display:block; }
  #crosshair { position:fixed; left:50%; top:50%; width:1px; height:1px; z-index:5; pointer-events:none; }
  #crosshair:before, #crosshair:after { content:""; position:absolute; background:rgba(255,255,255,.85); }
  #crosshair:before { left:-1px; top:-9px; width:2px; height:18px; }
  #crosshair:after  { top:-1px; left:-9px; width:18px; height:2px; }
  #hotbar { position:fixed; bottom:10px; left:50%; transform:translateX(-50%); display:flex; gap:6px;
            background:rgba(0,0,0,.45); padding:8px; border-radius:6px; z-index:5; }
  .slot { width:44px; height:44px; border:2px solid rgba(255,255,255,.25); border-radius:4px;
          position:relative; box-sizing:border-box; }
  .slot.sel { border-color:#ffffff; }
  .slot span { position:absolute; left:3px; top:1px; color:#fff; font-size:11px; text-shadow:1px 1px 0 #000; }
  #overlay { position:fixed; left:0; top:0; right:0; bottom:0; background:rgba(8,12,22,.8);
             display:flex; align-items:center; justify-content:center; flex-direction:column;
             color:#fff; z-index:10; cursor:pointer; text-align:center; user-select:none; }
  #overlay h1 { margin:0 0 12px; font-size:44px; letter-spacing:3px; }
  #overlay p { margin:4px 0; color:#cfd8dc; font-size:15px; }
  #overlay .play { margin-top:22px; font-size:22px; color:#ffd54f; }
</style>
</head>
<body>

<div id="overlay">
  <h1>VOXELCRAFT</h1>
  <p>WASD &mdash; move &nbsp;&middot;&nbsp; Space &mdash; jump &nbsp;&middot;&nbsp; Mouse &mdash; look</p>
  <p>Left click &mdash; break block &nbsp;&middot;&nbsp; Right click &mdash; place block</p>
  <p>Keys 1&ndash;7 or mouse wheel &mdash; choose block from the hotbar</p>
  <div class="play">Click to play</div>
</div>

<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
'use strict';

/* ============================================================
   Renderer / scene / camera / lights
============================================================ */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
camera.rotation.order = 'YXZ';

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(60, 120, 40);
scene.add(sun);

/* One shared material for every chunk mesh */
const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

/* ============================================================
   Blocks
============================================================ */
const BLOCK_COLORS = [null, 0x4caf50, 0x795548, 0x9e9e9e, 0xe7d9a8, 0x8d6e63, 0x2e7d32, 0xffffff];
const RGB = BLOCK_COLORS.map((c, i) => i === 0 ? null
    : [(c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255]);

/* Face definitions: outward normal, brightness, 4 corner verts (CCW) */
const FACES = [
    { n: [ 1, 0, 0], b: 0.80, v: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]] },
    { n: [-1, 0, 0], b: 0.80, v: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
    { n: [ 0, 1, 0], b: 1.00, v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
    { n: [ 0,-1, 0], b: 0.55, v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
    { n: [ 0, 0, 1], b: 0.80, v: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]] },
    { n: [ 0, 0,-1], b: 0.80, v: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]] }
];

/* ============================================================
   Deterministic value noise (no Math.random)
============================================================ */
function hash2(x, z) {
    let n = Math.imul(x, 374761393) + Math.imul(z, 668265263);
    n = n ^ (n >>> 13);
    n = Math.imul(n, 1274126177);
    n = n ^ (n >>> 16);
    return (n >>> 0) / 4294967295;
}
function hash3(x, y, z) {
    let n = Math.imul(x, 374761393) + Math.imul(y, 1103515245) + Math.imul(z, 668265263);
    n = n ^ (n >>> 13);
    n = Math.imul(n, 1274126177);
    n = n ^ (n >>> 16);
    return (n >>> 0) / 4294967295;
}
function smooth(t) { return t * t * (3 - 2 * t); }

function noise2(x, z) {
    const xi = Math.floor(x), zi = Math.floor(z);
    const xf = x - xi, zf = z - zi;
    const u = smooth(xf), v = smooth(zf);
    const a = hash2(xi, zi),     b = hash2(xi + 1, zi);
    const c = hash2(xi, zi + 1), d = hash2(xi + 1, zi + 1);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function fbm2(x, z) {
    let total = 0, amp = 1, freq = 1, sum = 0;
    for (let i = 0; i < 4; i++) {
        total += amp * noise2(x * freq, z * freq);
        sum += amp; amp *= 0.5; freq *= 2;
    }
    return total / sum;
}
function noise3(x, y, z) {
    const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    const u = smooth(x - xi), v = smooth(y - yi), w = smooth(z - zi);
    const h = (a, b, c) => hash3(xi + a, yi + b, zi + c);
    const x00 = h(0,0,0) + (h(1,0,0) - h(0,0,0)) * u;
    const x10 = h(0,1,0) + (h(1,1,0) - h(0,1,0)) * u;
    const x01 = h(0,0,1) + (h(1,0,1) - h(0,0,1)) * u;
    const x11 = h(0,1,1) + (h(1,1,1) - h(0,1,1)) * u;
    const y0 = x00 + (x10 - x00) * v;
    const y1 = x01 + (x11 - x01) * v;
    return y0 + (y1 - y0) * w;
}

function terrainHeight(x, z) {
    const m = fbm2(x * 0.004, z * 0.004);
    const h = fbm2(x * 0.02, z * 0.02);
    return Math.floor(5 + m * m * 58 + h * 10);
}

/* ============================================================
   Chunks
============================================================ */
const CS = 16;          // chunk size (x,z)
const CH = 80;          // world height
const chunks = new Map();      // "cx,cz" -> {cx, cz, data:Uint8Array, mesh}
const chunkMeshes = [];        // all meshes for raycasting

function ckey(cx, cz) { return cx + ',' + cz; }
function didx(lx, y, lz) { return (y * CS + lz) * CS + lx; }

function getBlock(x, y, z) {
    x = Math.floor(x); y = Math.floor(y); z = Math.floor(z);
    if (y < 0 || y >= CH) return 0;
    const cx = Math.floor(x / CS), cz = Math.floor(z / CS);
    const c = chunks.get(ckey(cx, cz));
    if (!c) return 0;
    return c.data[didx(x - cx * CS, y, z - cz * CS)];
}
function setBlock(x, y, z, id) {
    x = Math.floor(x); y = Math.floor(y); z = Math.floor(z);
    if (y < 0 || y >= CH) return;
    const cx = Math.floor(x / CS), cz = Math.floor(z / CS);
    const c = chunks.get(ckey(cx, cz));
    if (!c) return;
    c.data[didx(x - cx * CS, y, z - cz * CS)] = id;
}

/* ---- terrain generation for one chunk ---- */
function genChunk(cx, cz) {
    const data = new Uint8Array(CS * CH * CS);
    for (let lx = 0; lx < CS; lx++) {
        for (let lz = 0; lz < CS; lz++) {
            const x = cx * CS + lx, z = cz * CS + lz;
            const H = terrainHeight(x, z);
            const top = Math.min(H, CH - 1);
            for (let y = 0; y <= top; y++) {
                let b;
                if (y === 0)          b = 3;                                  // bedrock stone
                else if (y < H - 3)   b = 3;                                  // deep stone
                else if (y < H)       b = (H <= 16) ? 4 : (H >= 37 ? 3 : 2);  // sub-surface
                else                  b = (H >= 46) ? 7 : (H >= 37 ? 3 : (H <= 16 ? 4 : 1));
                if (b && y >= 3 && y <= H - 2 &&
                    noise3(x * 0.09, y * 0.09, z * 0.09) > 0.67) b = 0;       // caves
                data[didx(lx, y, lz)] = b;
            }
            /* trees: grass columns, rare hash, fully inside this chunk */
            if (lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 && H < CH - 9) {
                if (data[didx(lx, H, lz)] === 1 && hash2(x * 5 + 911, z * 5 + 733) < 0.02) {
                    for (let i = 1; i <= 4; i++) data[didx(lx, H + i, lz)] = 5;   // trunk
                    for (let dy = 5; dy <= 6; dy++)
                        for (let dx = -2; dx <= 2; dx++)
                            for (let dz = -2; dz <= 2; dz++) {
                                const i = didx(lx + dx, H + dy, lz + dz);
                                if (data[i] === 0) data[i] = 6;
                            }
                    for (let dx = -1; dx <= 1; dx++)
                        for (let dz = -1; dz <= 1; dz++) {
                            const i = didx(lx + dx, H + 7, lz + dz);
                            if (data[i] === 0) data[i] = 6;
                        }
                    const t = didx(lx, H + 8, lz);
                    if (data[t] === 0) data[t] = 6;
                }
            }
        }
    }
    chunks.set(ckey(cx, cz), { cx: cx, cz: cz, data: data, mesh: null });
}

/* ---- meshing: one BufferGeometry per chunk, world-space verts ---- */
function makeMesh(c) {
    const positions = [], normals = [], colors = [];
    const baseX = c.cx * CS, baseZ = c.cz * CS;
    for (let y = 0; y < CH; y++) {
        for (let lz = 0; lz < CS; lz++) {
            for (let lx = 0; lx < CS; lx++) {
                const id = c.data[didx(lx, y, lz)];
                if (!id) continue;
                const x = baseX + lx, z = baseZ + lz;
                const col = RGB[id];
                for (let f = 0; f < 6; f++) {
                    const face = FACES[f];
                    if (getBlock(x + face.n[0], y + face.n[1], z + face.n[2]) !== 0) continue;
                    const r = col[0] * face.b, g = col[1] * face.b, b = col[2] * face.b;
                    const q = face.v;
                    const order = [0, 1, 2, 0, 2, 3];
                    for (let k = 0; k < 6; k++) {
                        const v = q[order[k]];
                        positions.push(x + v[0], y + v[1], z + v[2]);
                        normals.push(face.n[0], face.n[1], face.n[2]);
                        colors.push(r, g, b);
                    }
                }
            }
        }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('normal',   new THREE.Float32BufferAttribute(normals, 3));
    geo.setAttribute('color',    new THREE.Float32BufferAttribute(colors, 3));
    const mesh = new THREE.Mesh(geo, blockMaterial);
    mesh.userData.cx = c.cx;
    mesh.userData.cz = c.cz;
    scene.add(mesh);
    chunkMeshes.push(mesh);
    c.mesh = mesh;
}
function removeMesh(c) {
    if (!c.mesh) return;
    scene.remove(c.mesh);
    c.mesh.geometry.dispose();
    const i = chunkMeshes.indexOf(c.mesh);
    if (i >= 0) chunkMeshes.splice(i, 1);
    c.mesh = null;
}
function rebuildChunk(cx, cz) {
    const c = chunks.get(ckey(cx, cz));
    if (!c) return;
    removeMesh(c);
    makeMesh(c);
}
function rebuildAt(x, z) {
    const cx = Math.floor(x / CS), cz = Math.floor(z / CS);
    const lx = x - cx * CS, lz = z - cz * CS;
    rebuildChunk(cx, cz);
    if (lx === 0)  rebuildChunk(cx - 1, cz);
    if (lx === 15) rebuildChunk(cx + 1, cz);
    if (lz === 0)  rebuildChunk(cx, cz - 1);
    if (lz === 15) rebuildChunk(cx, cz + 1);
}

/* ---- streaming: sorted offsets, generation & meshing budgets ---- */
const OFF5 = [];
for (let dx = -5; dx <= 5; dx++)
    for (let dz = -5; dz <= 5; dz++)
        OFF5.push([dx, dz]);
OFF5.sort((a, b) => (a[0]*a[0] + a[1]*a[1]) - (b[0]*b[0] + b[1]*b[1]));
const OFF4 = OFF5.filter(o => Math.abs(o[0]) <= 4 && Math.abs(o[1]) <= 4);

function updateChunks() {
    const pcx = Math.floor(player.pos.x / CS), pcz = Math.floor(player.pos.z / CS);
    let n = 0;
    for (let i = 0; i < OFF5.length && n < 4; i++) {
        const cx = pcx + OFF5[i][0], cz = pcz + OFF5[i][1];
        if (!chunks.has(ckey(cx, cz))) { genChunk(cx, cz); n++; }
    }
    n = 0;
    for (let i = 0; i < OFF4.length && n < 2; i++) {
        const cx = pcx + OFF4[i][0], cz = pcz + OFF4[i][1];
        const c = chunks.get(ckey(cx, cz));
        if (c && !c.mesh &&
            chunks.has(ckey(cx - 1, cz)) && chunks.has(ckey(cx + 1, cz)) &&
            chunks.has(ckey(cx, cz - 1)) && chunks.has(ckey(cx, cz + 1))) {
            makeMesh(c);
            n++;
        }
    }
    for (const c of chunks.values()) {
        if (Math.max(Math.abs(c.cx - pcx), Math.abs(c.cz - pcz)) > 7) {
            removeMesh(c);
            chunks.delete(ckey(c.cx, c.cz));
        }
    }
}

/* ============================================================
   Player
============================================================ */
const HW = 0.3, PH = 1.8, EYE = 1.62;
const SPAWN = { x: 8.5, y: terrainHeight(8, 8) + 2, z: 8.5 };
const player = {
    pos: { x: SPAWN.x, y: SPAWN.y, z: SPAWN.z },
    vel: { x: 0, y: 0, z: 0 },
    yaw: 0, pitch: 0, onGround: false
};
const keys = {};

function collides(px, py, pz) {
    const x0 = Math.floor(px - HW), x1 = Math.floor(px + HW);
    const z0 = Math.floor(pz - HW), z1 = Math.floor(pz + HW);
    const y0 = Math.floor(py + 1e-4), y1 = Math.floor(py + PH - 1e-4);
    for (let x = x0; x <= x1; x++)
        for (let y = y0; y <= y1; y++)
            for (let z = z0; z <= z1; z++)
                if (getBlock(x, y, z)) return true;
    return false;
}

function updatePlayer(dt) {
    const p = player.pos, v = player.vel;
    const sinY = Math.sin(player.yaw), cosY = Math.cos(player.yaw);
    let fx = 0, fz = 0;
    if (keys['KeyW']) { fx -= sinY; fz -= cosY; }
    if (keys['KeyS']) { fx += sinY; fz += cosY; }
    if (keys['KeyD']) { fx += cosY; fz -= sinY; }
    if (keys['KeyA']) { fx -= cosY; fz += sinY; }
    const l = Math.hypot(fx, fz);
    if (l > 0) { fx = fx / l * 5.5; fz = fz / l * 5.5; }
    v.x = fx; v.z = fz;

    v.y -= 25 * dt;                                  // gravity
    if (keys['Space'] && player.onGround) { v.y = 8.5; player.onGround = false; }

    p.x += v.x * dt;                                 // X axis
    if (collides(p.x, p.y, p.z)) p.x -= v.x * dt;
    p.z += v.z * dt;                                 // Z axis
    if (collides(p.x, p.y, p.z)) p.z -= v.z * dt;
    p.y += v.y * dt;                                 // Y axis
    if (collides(p.x, p.y, p.z)) {
        if (v.y < 0) player.onGround = true;
        p.y -= v.y * dt;
        v.y = 0;
    } else {
        player.onGround = false;
    }

    if (p.y < -20) {                                 // fell out of the world
        p.x = SPAWN.x; p.y = SPAWN.y; p.z = SPAWN.z;
        v.x = 0; v.y = 0; v.z = 0;
    }
    camera.position.set(p.x, p.y + EYE, p.z);
}

/* ============================================================
   Pointer lock, mouse look
============================================================ */
let locked = false;
const overlay = document.getElementById('overlay');

overlay.addEventListener('click', () => renderer.domElement.requestPointerLock());
document.addEventListener('pointerlockchange', () => {
    locked = (document.pointerLockElement === renderer.domElement);
    overlay.style.display = locked ? 'none' : 'flex';
});
document.addEventListener('mousemove', e => {
    if (!locked) return;
    player.yaw   -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    const lim = Math.PI / 2 - 0.01;
    player.pitch = Math.max(-lim, Math.min(lim, player.pitch));
    camera.rotation.set(player.pitch, player.yaw, 0);
});
document.addEventListener('contextmenu', e => e.preventDefault());

/* ============================================================
   Raycasting: target block, outline, break & place
============================================================ */
const raycaster = new THREE.Raycaster();
raycaster.far = 6;
const outline = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(1.001, 1.001, 1.001)),
    new THREE.LineBasicMaterial({ color: 0x000000 })
);
outline.visible = false;
scene.add(outline);

let target = null, placeCell = null;
const rayDir = new THREE.Vector3();

function updateRay() {
    target = null; placeCell = null; outline.visible = false;
    camera.getWorldDirection(rayDir);
    raycaster.set(camera.position, rayDir);
    const hits = raycaster.intersectObjects(chunkMeshes, false);
    if (hits.length && hits[0].distance <= 6) {
        const h = hits[0];
        const n = h.face.normal, p = h.point;
        target = {
            x: Math.floor(p.x - n.x * 0.5),
            y: Math.floor(p.y - n.y * 0.5),
            z: Math.floor(p.z - n.z * 0.5)
        };
        placeCell = {
            x: Math.floor(p.x + n.x * 0.5),
            y: Math.floor(p.y + n.y * 0.5),
            z: Math.floor(p.z + n.z * 0.5)
        };
        outline.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
        outline.visible = true;
    }
}

function overlapsPlayer(c) {
    const p = player.pos;
    return c.x + 1 > p.x - HW && c.x < p.x + HW &&
           c.y + 1 > p.y      && c.y < p.y + PH &&
           c.z + 1 > p.z - HW && c.z < p.z + HW;
}

document.addEventListener('mousedown', e => {
    if (!locked) return;
    if (e.button === 0 && target) {                       // break
        if (target.y <= 0) return;                        // bedrock layer unbreakable
        if (getBlock(target.x, target.y, target.z) === 0) return;
        setBlock(target.x, target.y, target.z, 0);
        rebuildAt(target.x, target.z);
    } else if (e.button === 2 && placeCell) {             // place
        const c = placeCell;
        if (getBlock(c.x, c.y, c.z) !== 0) return;
        if (overlapsPlayer(c)) return;
        setBlock(c.x, c.y, c.z, selected + 1);
        rebuildAt(c.x, c.z);
    }
});

/* ============================================================
   Hotbar
============================================================ */
const hotbar = document.getElementById('hotbar');
let selected = 0;
const slotEls = [];
for (let i = 0; i < 7; i++) {
    const d = document.createElement('div');
    d.className = 'slot';
    d.style.background = '#' + BLOCK_COLORS[i + 1].toString(16).padStart(6, '0');
    const s = document.createElement('span');
    s.textContent = i + 1;
    d.appendChild(s);
    hotbar.appendChild(d);
    slotEls.push(d);
}
function updateSel() {
    for (let i = 0; i < 7; i++) slotEls[i].classList.toggle('sel', i === selected);
}
updateSel();

document.addEventListener('keydown', e => {
    keys[e.code] = true;
    if (e.key >= '1' && e.key <= '7') { selected = +e.key - 1; updateSel(); }
});
document.addEventListener('keyup', e => { keys[e.code] = false; });
document.addEventListener('wheel', e => {
    selected = (selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7;
    updateSel();
}, { passive: true });

/* ============================================================
   Sky: clouds + water
============================================================ */
const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 });
const clouds = [];
for (let i = 0; i < 25; i++) {
    const w = 15 + Math.random() * 35, d = 15 + Math.random() * 35;
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, 2, d), cloudMat);
    m.position.set(Math.random() * 800 - 400, 88 + Math.random() * 6, Math.random() * 800 - 400);
    scene.add(m);
    clouds.push(m);
}
function updateClouds(dt) {
    const p = player.pos;
    for (const c of clouds) {
        c.position.x += 1.5 * dt;
        if (c.position.x - p.x >  400) c.position.x -= 800;
        if (c.position.x - p.x < -400) c.position.x += 800;
        if (c.position.z - p.z >  400) c.position.z -= 800;
        if (c.position.z - p.z < -400) c.position.z += 800;
    }
}

const water = new THREE.Mesh(
    new THREE.PlaneGeometry(1000, 1000),
    new THREE.MeshLambertMaterial({ color: 0x3b7dd8, transparent: true, opacity: 0.55 })
);
water.rotation.x = -Math.PI / 2;
water.position.y = 14.3;
scene.add(water);

/* ============================================================
   Main loop
============================================================ */
const clock = new THREE.Clock();
function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    updatePlayer(dt);
    updateChunks();
    updateRay();
    updateClouds(dt);
    water.position.set(player.pos.x, 14.3, player.pos.z);
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```