```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>mc</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #87ceeb;
    font-family: sans-serif;
  }

  canvas {
    display: block;
  }

  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.68);
    color: #fff;
    z-index: 10;
    text-align: center;
    user-select: none;
  }

  #overlay h1 {
    margin: 0 0 12px 0;
    font-size: 54px;
    letter-spacing: 2px;
  }

  #overlay p {
    margin: 4px 0;
    font-size: 18px;
  }

  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 2px;
    height: 2px;
    background: #fff;
    transform: translate(-50%, -50%);
    z-index: 5;
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.65);
    pointer-events: none;
  }

  #hotbar {
    position: fixed;
    left: 50%;
    bottom: 12px;
    transform: translateX(-50%);
    display: flex;
    gap: 4px;
    padding: 6px;
    background: rgba(0, 0, 0, 0.45);
    border-radius: 4px;
    z-index: 5;
    user-select: none;
  }

  .slot {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #555;
    color: #fff;
    font-weight: bold;
    text-shadow: 0 1px 2px #000;
  }

  .slot.selected {
    border-color: #fff;
  }
</style>
</head>
<body>
<div id="overlay">
  <h1>MC</h1>
  <p>Click to play</p>
  <p>WASD move, Space jump, mouse look</p>
  <p>Left click break, right click place</p>
  <p>Keys 1-7 or mouse wheel select block</p>
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
    0x000000,
    0x4caf50,
    0x795548,
    0x9e9e9e,
    0xe7d9a8,
    0x8d6e63,
    0x2e7d32,
    0xffffff
  ];

  const BLOCK_COLORS = BLOCK_HEX.map(function (hex) {
    return [
      ((hex >> 16) & 255) / 255,
      ((hex >> 8) & 255) / 255,
      (hex & 255) / 255
    ];
  });

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
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  document.body.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(0.5, 1, 0.25);
  scene.add(dirLight);

  const chunks = new Map();
  const meshList = [];
  const blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

  function key(cx, cz) {
    return cx + "," + cz;
  }

  function smooth(t) {
    return t * t * (3 - 2 * t);
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function hash2(x, z) {
    let h = Math.imul(x | 0, 374761393);
    h ^= Math.imul((z + 0x9e3779b9) | 0, 668265263);
    h ^= h >>> 13;
    h = Math.imul(h, 1274126177);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }

  function hash3(x, y, z) {
    let h = Math.imul(x | 0, 374761393) ^
            Math.imul(y | 0, 1103515245) ^
            Math.imul(z | 0, 668265263);
    h ^= h >>> 13;
    h = Math.imul(h, 1274126177);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }

  function noise2(x, z) {
    const x0 = Math.floor(x);
    const z0 = Math.floor(z);
    const xf = x - x0;
    const zf = z - z0;

    const sx = smooth(xf);
    const sz = smooth(zf);

    const v00 = hash2(x0, z0);
    const v10 = hash2(x0 + 1, z0);
    const v01 = hash2(x0, z0 + 1);
    const v11 = hash2(x0 + 1, z0 + 1);

    const a = lerp(v00, v10, sx);
    const b = lerp(v01, v11, sx);
    return lerp(a, b, sz);
  }

  function fbm2(x, z) {
    let total = 0;
    let amp = 1;
    let freq = 1;
    let norm = 0;

    for (let i = 0; i < 4; i++) {
      total += noise2(x * freq, z * freq) * amp;
      norm += amp;
      amp *= 0.5;
      freq *= 2;
    }

    return total / norm;
  }

  function noise3(x, y, z) {
    const x0 = Math.floor(x);
    const y0 = Math.floor(y);
    const z0 = Math.floor(z);

    const xf = x - x0;
    const yf = y - y0;
    const zf = z - z0;

    const sx = smooth(xf);
    const sy = smooth(yf);
    const sz = smooth(zf);

    const c000 = hash3(x0, y0, z0);
    const c100 = hash3(x0 + 1, y0, z0);
    const c010 = hash3(x0, y0 + 1, z0);
    const c110 = hash3(x0 + 1, y0 + 1, z0);
    const c001 = hash3(x0, y0, z0 + 1);
    const c101 = hash3(x0 + 1, y0, z0 + 1);
    const c011 = hash3(x0, y0 + 1, z0 + 1);
    const c111 = hash3(x0 + 1, y0 + 1, z0 + 1);

    const x00 = lerp(c000, c100, sx);
    const x10 = lerp(c010, c110, sx);
    const x01 = lerp(c001, c101, sx);
    const x11 = lerp(c011, c111, sx);

    const y0v = lerp(x00, x10, sy);
    const y1v = lerp(x01, x11, sy);

    return lerp(y0v, y1v, sz);
  }

  function terrainHeight(x, z) {
    const m = fbm2(x * 0.004, z * 0.004);
    const h = fbm2(x * 0.02, z * 0.02);
    return Math.floor(5 + m * m * 58 + h * 10);
  }

  function generateChunkData(cx, cz) {
    const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * WORLD_HEIGHT);

    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      for (let lz = 0; lz < CHUNK_SIZE; lz++) {
        const wx = cx * CHUNK_SIZE + lx;
        const wz = cz * CHUNK_SIZE + lz;
        const H = terrainHeight(wx, wz);

        for (let y = 0; y < H && y < WORLD_HEIGHT; y++) {
          let id;

          if (y === 0) {
            id = STONE;
          } else if (y >= H - 1) {
            if (H >= 46) id = SNOW;
            else if (H >= 37) id = STONE;
            else if (H <= 16) id = SAND;
            else id = GRASS;
          } else if (y >= H - 4) {
            if (H <= 16) id = SAND;
            else if (H >= 37) id = STONE;
            else id = DIRT;
          } else {
            id = STONE;
          }

          data[lx + CHUNK_SIZE * (lz + CHUNK_SIZE * y)] = id;
        }

        for (let y = 3; y <= H - 2 && y < WORLD_HEIGHT; y++) {
          const idx = lx + CHUNK_SIZE * (lz + CHUNK_SIZE * y);
          if (data[idx] !== AIR) {
            if (noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) {
              data[idx] = AIR;
            }
          }
        }
      }
    }

    for (let lx = 2; lx < 14; lx++) {
      for (let lz = 2; lz < 14; lz++) {
        const wx = cx * CHUNK_SIZE + lx;
        const wz = cz * CHUNK_SIZE + lz;
        const H = terrainHeight(wx, wz);

        if (H >= 17 && H <= 36 && hash2(wx + 12345, wz - 6789) < 0.02) {
          const base = H;

          if (base + 5 < WORLD_HEIGHT) {
            for (let dy = 0; dy < 4; dy++) {
              const y = base + dy;
              const idx = lx + CHUNK_SIZE * (lz + CHUNK_SIZE * y);
              data[idx] = WOOD;
            }

            const setLeaf = function (lx2, lz2, y) {
              if (lx2 < 0 || lx2 >= CHUNK_SIZE) return;
              if (lz2 < 0 || lz2 >= CHUNK_SIZE) return;
              if (y < 0 || y >= WORLD_HEIGHT) return;

              const idx = lx2 + CHUNK_SIZE * (lz2 + CHUNK_SIZE * y);
              if (data[idx] === AIR) data[idx] = LEAVES;
            };

            for (let dy = 2; dy <= 3; dy++) {
              const y = base + dy;
              for (let dx = -2; dx <= 2; dx++) {
                for (let dz = -2; dz <= 2; dz++) {
                  setLeaf(lx + dx, lz + dz, y);
                }
              }
            }

            const y3 = base + 4;
            for (let dx = -1; dx <= 1; dx++) {
              for (let dz = -1; dz <= 1; dz++) {
                setLeaf(lx + dx, lz + dz, y3);
              }
            }

            setLeaf(lx, lz, base + 5);
          }
        }
      }
    }

    return data;
  }

  function hasChunkData(cx, cz) {
    return chunks.has(key(cx, cz));
  }

  function hasAllNeighbors(cx, cz) {
    return (
      hasChunkData(cx + 1, cz) &&
      hasChunkData(cx - 1, cz) &&
      hasChunkData(cx, cz + 1) &&
      hasChunkData(cx, cz - 1)
    );
  }

  function readBlock(x, y, z) {
    if (y < 0 || y >= WORLD_HEIGHT) return AIR;

    const cx = Math.floor(x / CHUNK_SIZE);
    const cz = Math.floor(z / CHUNK_SIZE);
    const chunk = chunks.get(key(cx, cz));

    if (!chunk || !chunk.data) return AIR;

    const lx = x - cx * CHUNK_SIZE;
    const lz = z - cz * CHUNK_SIZE;

    return chunk.data[lx + CHUNK_SIZE * (lz + CHUNK_SIZE * y)];
  }

  function writeBlock(x, y, z, id) {
    if (y < 0 || y >= WORLD_HEIGHT) return null;

    const cx = Math.floor(x / CHUNK_SIZE);
    const cz = Math.floor(z / CHUNK_SIZE);
    const k = key(cx, cz);

    let chunk = chunks.get(k);
    if (!chunk) {
      chunk = {
        cx: cx,
        cz: cz,
        data: generateChunkData(cx, cz),
        mesh: null
      };
      chunks.set(k, chunk);
    }

    const lx = x - cx * CHUNK_SIZE;
    const lz = z - cz * CHUNK_SIZE;

    chunk.data[lx + CHUNK_SIZE * (lz + CHUNK_SIZE * y)] = id;

    return {
      cx: cx,
      cz: cz,
      lx: lx,
      lz: lz
    };
  }

  const FACES = [
    {
      n: [0, 1, 0],
      light: 1.0,
      corners: [
        [0, 1, 0],
        [0, 1, 1],
        [1, 1, 1],
        [1, 1, 0]
      ]
    },
    {
      n: [0, -1, 0],
      light: 0.55,
      corners: [
        [0, 0, 0],
        [1, 0, 0],
        [1, 0, 1],
        [0, 0, 1]
      ]
    },
    {
      n: [1, 0, 0],
      light: 0.8,
      corners: [
        [1, 0, 0],
        [1, 1, 0],
        [1, 1, 1],
        [1, 0, 1]
      ]
    },
    {
      n: [-1, 0, 0],
      light: 0.8,
      corners: [
        [0, 0, 1],
        [0, 1, 1],
        [0, 1, 0],
        [0, 0, 0]
      ]
    },
    {
      n: [0, 0, 1],
      light: 0.8,
      corners: [
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
        [0, 0, 1]
      ]
    },
    {
      n: [0, 0, -1],
      light: 0.8,
      corners: [
        [0, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
        [1, 0, 0]
      ]
    }
  ];

  function removeChunkMesh(chunk) {
    if (!chunk.mesh) return;

    scene.remove(chunk.mesh);

    const i = meshList.indexOf(chunk.mesh);
    if (i >= 0) meshList.splice(i, 1);

    chunk.mesh.geometry.dispose();
    chunk.mesh = null;
  }

  function buildChunkMesh(cx, cz) {
    const chunk = chunks.get(key(cx, cz));
    if (!chunk) return;

    removeChunkMesh(chunk);

    if (!chunk.data || !hasAllNeighbors(cx, cz)) return;

    const positions = [];
    const normals = [];
    const colors = [];

    const wxBase = cx * CHUNK_SIZE;
    const wzBase = cz * CHUNK_SIZE;

    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      for (let lz = 0; lz < CHUNK_SIZE; lz++) {
        for (let y = 0; y < WORLD_HEIGHT; y++) {
          const idx = lx + CHUNK_SIZE * (lz + CHUNK_SIZE * y);
          const id = chunk.data[idx];

          if (id === AIR) continue;

          const wx = wxBase + lx;
          const wz = wzBase + lz;
          const base = BLOCK_COLORS[id];

          for (let f = 0; f < FACES.length; f++) {
            const face = FACES[f];

            const nx = wx + face.n[0];
            const ny = y + face.n[1];
            const nz = wz + face.n[2];

            if (readBlock(nx, ny, nz) !== AIR) continue;

            const r = base[0] * face.light;
            const g = base[1] * face.light;
            const b = base[2] * face.light;

            const c = face.corners;
            const n0 = face.n[0];
            const n1 = face.n[1];
            const n2 = face.n[2];

            positions.push(wx + c[0][0], y + c[0][1], wz + c[0][2]);
            normals.push(n0, n1, n2);
            colors.push(r, g, b);

            positions.push(wx + c[1][0], y + c[1][1], wz + c[1][2]);
            normals.push(n0, n1, n2);
            colors.push(r, g, b);

            positions.push(wx + c[2][0], y + c[2][1], wz + c[2][2]);
            normals.push(n0, n1, n2);
            colors.push(r, g, b);

            positions.push(wx + c[0][0], y + c[0][1], wz + c[0][2]);
            normals.push(n0, n1, n2);
            colors.push(r, g, b);

            positions.push(wx + c[2][0], y + c[2][1], wz + c[2][2]);
            normals.push(n0, n1, n2);
            colors.push(r, g, b);

            positions.push(wx + c[3][0], y + c[3][1], wz + c[3][2]);
            normals.push(n0, n1, n2);
            colors.push(r, g, b);
          }
        }
      }
    }

    if (positions.length > 0) {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
      geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

      const mesh = new THREE.Mesh(geometry, blockMaterial);
      scene.add(mesh);
      meshList.push(mesh);
      chunk.mesh = mesh;
    }
  }

  function rebuildChunk(cx, cz) {
    buildChunkMesh(cx, cz);
  }

  function updateChunks() {
    const pcx = Math.floor(player.x / CHUNK_SIZE);
    const pcz = Math.floor(player.z / CHUNK_SIZE);

    const gen = [];
    for (let dx = -5; dx <= 5; dx++) {
      for (let dz = -5; dz <= 5; dz++) {
        const cx = pcx + dx;
        const cz = pcz + dz;

        if (!hasChunkData(cx, cz)) {
          gen.push({ cx: cx, cz: cz, d: dx * dx + dz * dz });
        }
      }
    }

    gen.sort(function (a, b) {
      return a.d - b.d;
    });

    for (let i = 0; i < gen.length && i < 4; i++) {
      const cx = gen[i].cx;
      const cz = gen[i].cz;
      chunks.set(key(cx, cz), {
        cx: cx,
        cz: cz,
        data: generateChunkData(cx, cz),
        mesh: null
      });
    }

    const build = [];
    for (let dx = -4; dx <= 4; dx++) {
      for (let dz = -4; dz <= 4; dz++) {
        const cx = pcx + dx;
        const cz = pcz + dz;
        const chunk = chunks.get(key(cx, cz));

        if (chunk && !chunk.mesh && hasAllNeighbors(cx, cz)) {
          build.push({ cx: cx, cz: cz, d: dx * dx + dz * dz });
        }
      }
    }

    build.sort(function (a, b) {
      return a.d - b.d;
    });

    for (let i = 0; i < build.length && i < 2; i++) {
      buildChunkMesh(build[i].cx, build[i].cz);
    }

    for (const [k, chunk] of chunks) {
      if (Math.max(Math.abs(chunk.cx - pcx), Math.abs(chunk.cz - pcz)) > 7) {
        removeChunkMesh(chunk);
        chunks.delete(k);
      }
    }
  }

  const player = {
    x: 8,
    y: terrainHeight(8, 8) + 0.1,
    z: 8,
    vx: 0,
    vy: 0,
    vz: 0,
    onGround: false
  };

  let yaw = 0;
  let pitch = 0;
  let locked = false;
  const keys = {};

  camera.position.set(player.x, player.y + 1.62, player.z);
  camera.rotation.set(pitch, yaw, 0);

  function collides(px, py, pz) {
    const eps = 1e-4;

    const minX = px - 0.3;
    const maxX = px + 0.3;
    const minY = py;
    const maxY = py + 1.8;
    const minZ = pz - 0.3;
    const maxZ = pz + 0.3;

    for (let x = Math.floor(minX); x <= Math.floor(maxX - eps); x++) {
      for (let y = Math.floor(minY); y <= Math.floor(maxY - eps); y++) {
        for (let z = Math.floor(minZ); z <= Math.floor(maxZ - eps); z++) {
          if (readBlock(x, y, z) !== AIR) return true;
        }
      }
    }

    return false;
  }

  function updatePlayer(dt) {
    if (locked) {
      const forward = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0);
      const strafe = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0);

      const speed = 5.5;

      if (forward !== 0 || strafe !== 0) {
        const fx = -Math.sin(yaw);
        const fz = -Math.cos(yaw);
        const rx = Math.cos(yaw);
        const rz = -Math.sin(yaw);

        player.vx = (forward * fx + strafe * rx) * speed;
        player.vz = (forward * fz + strafe * rz) * speed;
      } else {
        player.vx = 0;
        player.vz = 0;
      }

      if (keys.Space && player.onGround) {
        player.vy = 8.5;
        player.onGround = false;
      }
    } else {
      player.vx = 0;
      player.vz = 0;
    }

    player.vy -= 25 * dt;

    player.x += player.vx * dt;
    if (collides(player.x, player.y, player.z)) {
      player.x -= player.vx * dt;
      player.vx = 0;
    }

    player.z += player.vz * dt;
    if (collides(player.x, player.y, player.z)) {
      player.z -= player.vz * dt;
      player.vz = 0;
    }

    player.y += player.vy * dt;
    if (collides(player.x, player.y, player.z)) {
      if (player.vy < 0) player.onGround = true;
      player.y -= player.vy * dt;
      player.vy = 0;
    } else {
      player.onGround = false;
    }

    if (player.y < -20) {
      player.x = 8;
      player.y = terrainHeight(8, 8) + 0.1;
      player.z = 8;
      player.vx = 0;
      player.vy = 0;
      player.vz = 0;
    }

    camera.position.set(player.x, player.y + 1.62, player.z);
  }

  const raycaster = new THREE.Raycaster();
  raycaster.far = 6;
  const screenCenter = new THREE.Vector2(0, 0);

  const outlineGeometry = new THREE.BoxGeometry(1.001, 1.001, 1.001);
  const outlineEdges = new THREE.EdgesGeometry(outlineGeometry);
  const outlineMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
  const outline = new THREE.LineSegments(outlineEdges, outlineMaterial);
  outline.visible = false;
  scene.add(outline);

  let targetBlock = null;
  let placeCell = null;

  function updateTarget() {
    outline.visible = false;
    targetBlock = null;
    placeCell = null;

    if (!locked) return;

    raycaster.setFromCamera(screenCenter, camera);
    const hits = raycaster.intersectObjects(meshList, false);

    if (hits.length > 0) {
      const hit = hits[0];

      if (hit.face && hit.distance <= 6) {
        const p = hit.point;
        const n = hit.face.normal;

        const bx = Math.floor(p.x - n.x * 0.5);
        const by = Math.floor(p.y - n.y * 0.5);
        const bz = Math.floor(p.z - n.z * 0.5);

        const px = Math.floor(p.x + n.x * 0.5);
        const py = Math.floor(p.y + n.y * 0.5);
        const pz = Math.floor(p.z + n.z * 0.5);

        targetBlock = { x: bx, y: by, z: bz };
        placeCell = { x: px, y: py, z: pz };

        outline.position.set(bx + 0.5, by + 0.5, bz + 0.5);
        outline.visible = true;
      }
    }
  }

  function rebuildAround(info, x, z) {
    if (!info) return;

    rebuildChunk(info.cx, info.cz);

    const lx = x - info.cx * CHUNK_SIZE;
    const lz = z - info.cz * CHUNK_SIZE;

    if (lx === 0) rebuildChunk(info.cx - 1, info.cz);
    if (lx === CHUNK_SIZE - 1) rebuildChunk(info.cx + 1, info.cz);
    if (lz === 0) rebuildChunk(info.cx, info.cz - 1);
    if (lz === CHUNK_SIZE - 1) rebuildChunk(info.cx, info.cz + 1);
  }

  function breakBlock() {
    if (!targetBlock) return;

    const x = targetBlock.x;
    const y = targetBlock.y;
    const z = targetBlock.z;

    if (y === 0) return;

    const info = writeBlock(x, y, z, AIR);
    rebuildAround(info, x, z);
  }

  function intersectsPlayer(x, y, z) {
    return (
      x < player.x + 0.3 &&
      x + 1 > player.x - 0.3 &&
      y < player.y + 1.8 &&
      y + 1 > player.y &&
      z < player.z + 0.3 &&
      z + 1 > player.z - 0.3
    );
  }

  function placeBlock() {
    if (!placeCell) return;

    const x = placeCell.x;
    const y = placeCell.y;
    const z = placeCell.z;

    if (readBlock(x, y, z) !== AIR) return;
    if (intersectsPlayer(x, y, z)) return;

    const info = writeBlock(x, y, z, selected + 1);
    rebuildAround(info, x, z);
  }

  const hotbar = document.getElementById("hotbar");
  let selected = 0;

  for (let i = 0; i < 7; i++) {
    const slot = document.createElement("div");
    slot.className = "slot";
    slot.textContent = String(i + 1);
    slot.style.background = "#" + BLOCK_HEX[i + 1].toString(16).padStart(6, "0");
    hotbar.appendChild(slot);
  }

  function updateHotbar() {
    for (let i = 0; i < 7; i++) {
      const slot = hotbar.children[i];
      if (i === selected) slot.classList.add("selected");
      else slot.classList.remove("selected");
    }
  }

  updateHotbar();

  const clouds = [];
  const cloudMaterial = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.75
  });

  for (let i = 0; i < 25; i++) {
    const w = 16 + hash2(i * 17 + 3, i * 31 + 7) * 24;
    const d = 16 + hash2(i * 19 + 11, i * 23 + 5) * 24;
    const geometry = new THREE.BoxGeometry(w, 2, d);
    const cloud = new THREE.Mesh(geometry, cloudMaterial);

    cloud.position.set(
      (hash2(i, 1) - 0.5) * 300,
      90,
      (hash2(i, 2) - 0.5) * 300
    );

    scene.add(cloud);
    clouds.push(cloud);
  }

  const waterGeometry = new THREE.PlaneGeometry(800, 800);
  const waterMaterial = new THREE.MeshBasicMaterial({
    color: 0x3399ff,
    transparent: true,
    opacity: 0.55,
    depthWrite: false
  });
  const water = new THREE.Mesh(waterGeometry, waterMaterial);
  water.rotation.x = -Math.PI / 2;
  water.position.y = 14.3;
  scene.add(water);

  function updateClouds(dt) {
    for (let i = 0; i < clouds.length; i++) {
      const cloud = clouds[i];

      cloud.position.x += 1.2 * dt;
      cloud.position.z += 0.4 * dt;

      const dx = cloud.position.x - player.x;
      if (dx > 150) cloud.position.x -= 300;
      else if (dx < -150) cloud.position.x += 300;

      const dz = cloud.position.z - player.z;
      if (dz > 150) cloud.position.z -= 300;
      else if (dz < -150) cloud.position.z += 300;
    }
  }

  const overlay = document.getElementById("overlay");

  overlay.addEventListener("click", function () {
    renderer.domElement.requestPointerLock();
  });

  document.addEventListener("pointerlockchange", function () {
    locked = document.pointerLockElement === renderer.domElement;
    overlay.style.display = locked ? "none" : "flex";

    if (!locked) {
      keys.KeyW = false;
      keys.KeyA = false;
      keys.KeyS = false;
      keys.KeyD = false;
      keys.Space = false;
    }
  });

  document.addEventListener("mousemove", function (e) {
    if (!locked) return;

    yaw -= e.movementX * 0.002;
    pitch -= e.movementY * 0.002;

    const limit = Math.PI / 2 - 0.01;
    pitch = Math.max(-limit, Math.min(limit, pitch));

    camera.rotation.set(pitch, yaw, 0);
  });

  document.addEventListener("mousedown", function (e) {
    if (!locked) return;

    e.preventDefault();

    if (e.button === 0) breakBlock();
    else if (e.button === 2) placeBlock();
  });

  document.addEventListener("contextmenu", function (e) {
    e.preventDefault();
  });

  document.addEventListener("keydown", function (e) {
    keys[e.code] = true;

    if (e.code === "Space" && locked) {
      e.preventDefault();
    }

    if (e.code.indexOf("Digit") === 0) {
      const n = parseInt(e.code.slice(5), 10);
      if (n >= 1 && n <= 7) {
        selected = n - 1;
        updateHotbar();
      }
    }
  });

  document.addEventListener("keyup", function (e) {
    keys[e.code] = false;
  });

  document.addEventListener("wheel", function (e) {
    if (!locked) return;

    e.preventDefault();

    let dir = 0;
    if (e.deltaY > 0) dir = 1;
    else if (e.deltaY < 0) dir = -1;

    if (dir !== 0) {
      selected = (selected + dir + 7) % 7;
      updateHotbar();
    }
  }, { passive: false });

  window.addEventListener("resize", function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  function initWorld() {
    const pcx = Math.floor(player.x / CHUNK_SIZE);
    const pcz = Math.floor(player.z / CHUNK_SIZE);

    for (let dx = -4; dx <= 4; dx++) {
      for (let dz = -4; dz <= 4; dz++) {
        const cx = pcx + dx;
        const cz = pcz + dz;

        if (!hasChunkData(cx, cz)) {
          chunks.set(key(cx, cz), {
            cx: cx,
            cz: cz,
            data: generateChunkData(cx, cz),
            mesh: null
          });
        }
      }
    }

    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        const cx = pcx + dx;
        const cz = pcz + dz;

        if (hasAllNeighbors(cx, cz)) {
          buildChunkMesh(cx, cz);
        }
      }
    }
  }

  initWorld();

  let last = performance.now();

  function animate(now) {
    requestAnimationFrame(animate);

    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;

    updatePlayer(dt);
    updateChunks();
    updateTarget();
    updateClouds(dt);

    water.position.set(player.x, 14.3, player.z);

    renderer.render(scene, camera);
  }

  requestAnimationFrame(animate);
})();
</script>
</body>
</html>
```