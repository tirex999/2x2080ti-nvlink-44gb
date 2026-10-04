

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mc.html - Voxel Sandbox</title>
<style>
  html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; }
  canvas { display: block; }
  #crosshair {
    position: fixed; left: 50%; top: 50%; width: 20px; height: 20px;
    transform: translate(-50%, -50%); pointer-events: none; z-index: 5;
  }
  #crosshair:before, #crosshair:after {
    content: ""; position: absolute; background: rgba(255,255,255,0.85);
  }
  #crosshair:before { left: 9px; top: 0; width: 2px; height: 20px; }
  #crosshair:after  { left: 0; top: 9px; width: 20px; height: 2px; }
  #hotbar {
    position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 4px; background: rgba(0,0,0,0.45);
    padding: 6px; border-radius: 6px; z-index: 5;
  }
  .slot {
    width: 46px; height: 46px; border: 2px solid rgba(255,255,255,0.3);
    border-radius: 4px; position: relative;
    display: flex; align-items: center; justify-content: center;
  }
  .slot.sel { border-color: #ffffff; box-shadow: 0 0 6px rgba(255,255,255,0.7); }
  .slot .num {
    position: absolute; top: 1px; left: 4px; color: #fff;
    font: bold 12px monospace; text-shadow: 1px 1px 0 #000;
  }
  .swatch { width: 28px; height: 28px; border-radius: 2px; box-shadow: inset 0 0 4px rgba(0,0,0,0.4); }
  #overlay {
    position: fixed; inset: 0; background: rgba(15,20,30,0.85); color: #fff;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    z-index: 10; cursor: pointer; text-align: center; font-family: sans-serif;
  }
  #overlay h1 { font-size: 52px; margin: 0 0 8px; letter-spacing: 3px; text-shadow: 3px 3px 0 #222; }
  #overlay ul { list-style: none; line-height: 1.9; font-size: 16px; color: #ddd; margin: 0 0 24px; }
  #overlay .play { font-size: 24px; color: #9f9; animation: pulse 1.2s infinite; }
  @keyframes pulse { 50% { opacity: 0.45; } }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MINECRAFT</h1>
  <ul>
    <li>W A S D &mdash; move</li>
    <li>Mouse &mdash; look around</li>
    <li>Space &mdash; jump</li>
    <li>Left click &mdash; break block</li>
    <li>Right click &mdash; place block</li>
    <li>1&ndash;7 / mouse wheel &mdash; select block</li>
  </ul>
  <div class="play">Click to play</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  "use strict";

  // ---------- Constants ----------
  var CHUNK = 16, HEIGHT = 80;
  var WATER_Y = 14.3;
  var GRAVITY = 25, JUMP_V = 8.5, WALK_SPEED = 5.5;
  var HALF_W = 0.3, P_HEIGHT = 1.8, EYE = 1.62;
  var REACH = 6;

  var BLOCK_COLORS = { 1: 0x4caf50, 2: 0x795548, 3: 0x9e9e9e, 4: 0xe7d9a8, 5: 0x8d6e63, 6: 0x2e7d32, 7: 0xffffff };
  var HOTBAR_IDS = [1, 2, 3, 4, 5, 6, 7];

  // ---------- Deterministic value noise ----------
  function hash2i(x, y) {
    var h = Math.imul(x, 374761393) ^ Math.imul(y, 668265263);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }
  function hash3i(x, y, z) {
    var h = Math.imul(x, 374761393) ^ Math.imul(y, 668265263) ^ Math.imul(z, 2147483629);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }
  function smoothstep(t) { return t * t * (3 - 2 * t); }

  function noise2(x, y) {
    var xi = Math.floor(x), yi = Math.floor(y);
    var xf = x - xi, yf = y - yi;
    var a = hash2i(xi, yi), b = hash2i(xi + 1, yi);
    var c = hash2i(xi, yi + 1), d = hash2i(xi + 1, yi + 1);
    var u = smoothstep(xf), v = smoothstep(yf);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }
  function noise3(x, y, z) {
    var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    var xf = x - xi, yf = y - yi, zf = z - zi;
    var u = smoothstep(xf), v = smoothstep(yf), w = smoothstep(zf);
    var c000 = hash3i(xi, yi, zi),     c100 = hash3i(xi + 1, yi, zi);
    var c010 = hash3i(xi, yi + 1, zi), c110 = hash3i(xi + 1, yi + 1, zi);
    var c001 = hash3i(xi, yi, zi + 1), c101 = hash3i(xi + 1, yi, zi + 1);
    var c011 = hash3i(xi, yi + 1, zi + 1), c111 = hash3i(xi + 1, yi + 1, zi + 1);
    var c00 = c000 + (c100 - c000) * u, c10 = c010 + (c110 - c010) * u;
    var c01 = c001 + (c101 - c001) * u, c11 = c011 + (c111 - c011) * u;
    var c0 = c00 + (c10 - c00) * v, c1 = c01 + (c11 - c01) * v;
    return c0 + (c1 - c0) * w;
  }
  function fractal2(x, y) {
    var sum = 0, amp = 1, freq = 1, norm = 0;
    for (var i = 0; i < 4; i++) {
      sum += noise2(x * freq, y * freq) * amp;
      norm += amp;
      amp *= 0.5;
      freq *= 2;
    }
    return sum / norm;
  }
  function columnHeight(x, z) {
    var m = fractal2(x * 0.004, z * 0.004);
    var h = fractal2(x * 0.02, z * 0.02);
    var H = Math.floor(5 + m * m * 58 + h * 10);
    if (H > HEIGHT - 1) H = HEIGHT - 1;
    if (H < 1) H = 1;
    return H;
  }

  // ---------- Chunk storage & global block access ----------
  var chunks = new Map();      // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
  var chunkMeshes = [];        // all live chunk meshes (for raycasting)

  function chunkKey(cx, cz) { return cx + "," + cz; }
  function localIndex(lx, y, lz) { return lx + lz * 16 + y * 256; }

  function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= HEIGHT) return 0;
    var cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
    var c = chunks.get(chunkKey(cx, cz));
    if (!c) return 0;
    var lx = wx - cx * 16, lz = wz - cz * 16;
    return c.data[localIndex(lx, wy, lz)];
  }
  function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= HEIGHT) return false;
    var cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
    var c = chunks.get(chunkKey(cx, cz));
    if (!c) return false;
    var lx = wx - cx * 16, lz = wz - cz * 16;
    c.data[localIndex(lx, wy, lz)] = id;
    return true;
  }

  // ---------- Terrain generation ----------
  function generateChunk(cx, cz) {
    var data = new Uint8Array(CHUNK * CHUNK * HEIGHT);
    var ox = cx * 16, oz = cz * 16;

    function setLocal(lx, y, lz, id) {
      if (lx < 0 || lx >= CHUNK || lz < 0 || lz >= CHUNK || y < 0 || y >= HEIGHT) return;
      data[localIndex(lx, y, lz)] = id;
    }
    function getLocal(lx, y, lz) {
      if (lx < 0 || lx >= CHUNK || lz < 0 || lz >= CHUNK || y < 0 || y >= HEIGHT) return 0;
      return data[localIndex(lx, y, lz)];
    }

    for (var lx = 0; lx < CHUNK; lx++) {
      for (var lz = 0; lz < CHUNK; lz++) {
        var wx = ox + lx, wz = oz + lz;
        var H = columnHeight(wx, wz);

        var surface = H >= 46 ? 7 : (H >= 37 ? 3 : (H <= 16 ? 4 : 1));   // snow / stone / sand / grass
        var sub = H <= 16 ? 4 : (H >= 37 ? 3 : 2);                        // sand / stone / dirt

        for (var y = 0; y <= H; y++) {
          var id;
          if (y === 0) id = 3;             // bedrock-ish unbreakable stone
          else if (y < H - 3) id = 3;      // stone
          else if (y < H) id = sub;        // 3 layers under surface
          else id = surface;               // surface
          data[localIndex(lx, y, lz)] = id;
        }

        // Caves
        for (var cy = 3; cy <= H - 2; cy++) {
          if (noise3(wx * 0.09, cy * 0.09, wz * 0.09) > 0.67) {
            data[localIndex(lx, cy, lz)] = 0;
          }
        }

        // Trees
        if (surface === 1 && H + 7 < HEIGHT &&
            lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 &&
            hash2i(wx, wz) < 0.02) {
          for (var t = 1; t <= 4; t++) setLocal(lx, H + t, lz, 5);        // trunk: 4 wood
          for (var dy = 4; dy <= 5; dy++)                                 // two 5x5 leaf layers
            for (var dx = -2; dx <= 2; dx++)
              for (var dz = -2; dz <= 2; dz++)
                if (getLocal(lx + dx, H + dy, lz + dz) === 0) setLocal(lx + dx, H + dy, lz + dz, 6);
          for (var dx3 = -1; dx3 <= 1; dx3++)                             // 3x3 layer
            for (var dz3 = -1; dz3 <= 1; dz3++)
              if (getLocal(lx + dx3, H + 6, lz + dz3) === 0) setLocal(lx + dx3, H + 6, lz + dz3, 6);
          if (getLocal(lx, H + 7, lz) === 0) setLocal(lx, H + 7, lz, 6);  // single top leaf
        }
      }
    }
    chunks.set(chunkKey(cx, cz), { data: data, mesh: null });
  }

  // ---------- Meshing ----------
  var voxelMat = new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide });

  // dir, shade, four corner offsets (unit cube at integer origin)
  var FACES = [
    { dir: [ 1, 0, 0], shade: 0.8,  verts: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]] },
    { dir: [-1, 0, 0], shade: 0.8,  verts: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]] },
    { dir: [ 0, 1, 0], shade: 1.0,  verts: [[0,1,0],[0,1,1],[1,1,1],[1,1,0]] },
    { dir: [ 0,-1, 0], shade: 0.55, verts: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
    { dir: [ 0, 0, 1], shade: 0.8,  verts: [[1,0,1],[1,1,1],[0,1,1],[0,0,1]] },
    { dir: [ 0, 0,-1], shade: 0.8,  verts: [[0,0,0],[0,1,0],[1,1,0],[1,0,0]] }
  ];
  var TRIS = [0, 1, 2, 0, 2, 3];
  var colorCache = {};

  function buildChunkMesh(cx, cz) {
    var c = chunks.get(chunkKey(cx, cz));
    if (!c) return;
    var pos = [], nor = [], col = [];
    var ox = cx * 16, oz = cz * 16;

    for (var y = 0; y < HEIGHT; y++) {
      for (var lz = 0; lz < CHUNK; lz++) {
        for (var lx = 0; lx < CHUNK; lx++) {
          var id = c.data[localIndex(lx, y, lz)];
          if (id === 0) continue;
          var wx = ox + lx, wy = y, wz = oz + lz;
          var base = colorCache[id] || (colorCache[id] = new THREE.Color(BLOCK_COLORS[id]));
          for (var fi = 0; fi < 6; fi++) {
            var f = FACES[fi];
            if (getBlock(wx + f.dir[0], wy + f.dir[1], wz + f.dir[2]) !== 0) continue;
            var r = base.r * f.shade, g = base.g * f.shade, b = base.b * f.shade;
            for (var ti = 0; ti < 6; ti++) {
              var v = f.verts[TRIS[ti]];
              pos.push(wx + v[0], wy + v[1], wz + v[2]);
              nor.push(f.dir[0], f.dir[1], f.dir[2]);
              col.push(r, g, b);
            }
          }
        }
      }
    }

    var geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
    geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
    var mesh = new THREE.Mesh(geo, voxelMat);
    mesh.position.set(0, 0, 0);
    scene.add(mesh);
    chunkMeshes.push(mesh);
    c.mesh = mesh;
  }

  function rebuildChunk(cx, cz) {
    var c = chunks.get(chunkKey(cx, cz));
    if (!c) return;
    if (c.mesh) {
      scene.remove(c.mesh);
      var i = chunkMeshes.indexOf(c.mesh);
      if (i >= 0) chunkMeshes.splice(i, 1);
      c.mesh.geometry.dispose();
      c.mesh = null;
    }
    buildChunkMesh(cx, cz);
  }

  function rebuildAround(wx, wy, wz) {
    var cx = Math.floor(wx / 16), cz = Math.floor(wz / 16);
    var lx = wx - cx * 16, lz = wz - cz * 16;
    rebuildChunk(cx, cz);
    if (lx === 0)  rebuildChunk(cx - 1, cz);
    if (lx === 15) rebuildChunk(cx + 1, cz);
    if (lz === 0)  rebuildChunk(cx, cz - 1);
    if (lz === 15) rebuildChunk(cx, cz + 1);
  }

  // ---------- Scene ----------
  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb);
  scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

  var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
  camera.rotation.order = "YXZ";

  var renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  document.body.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  var sun = new THREE.DirectionalLight(0xffffff, 0.8);
  sun.position.set(0.5, 1, 0.3);
  scene.add(sun);

  // Clouds
  var cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 });
  var clouds = [];
  for (var ci = 0; ci < 25; ci++) {
    var cg = new THREE.BoxGeometry(8 + Math.random() * 18, 1, 6 + Math.random() * 10);
    var cm = new THREE.Mesh(cg, cloudMat);
    cm.position.set((Math.random() - 0.5) * 300, 88 + Math.random() * 8, (Math.random() - 0.5) * 300);
    cm.userData.speed = 1 + Math.random() * 2;
    scene.add(cm);
    clouds.push(cm);
  }

  // Water plane (visual only)
  var water = new THREE.Mesh(
    new THREE.PlaneGeometry(300, 300),
    new THREE.MeshLambertMaterial({ color: 0x3060c8, transparent: true, opacity: 0.6 })
  );
  water.rotation.x = -Math.PI / 2;
  water.position.y = WATER_Y;
  scene.add(water);

  // Target outline
  var outline = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(1.02, 1.02, 1.02)),
    new THREE.LineBasicMaterial({ color: 0x000000 })
  );
  outline.visible = false;
  scene.add(outline);

  // ---------- Player ----------
  var player = { x: 8, y: 0, z: 8, vx: 0, vy: 0, vz: 0, yaw: 0, pitch: 0, onGround: false };

  function spawnHeight(x, z) {
    for (var y = HEIGHT - 1; y > 0; y--) {
      if (getBlock(x, y, z) !== 0) return y + 1;
    }
    return 40;
  }
  function respawn() {
    player.x = 8; player.z = 8;
    player.y = spawnHeight(8, 8);
    player.vx = player.vy = player.vz = 0;
  }

  function collides(px, py, pz) {
    var x0 = Math.floor(px - HALF_W), x1 = Math.floor(px + HALF_W);
    var y0 = Math.floor(py),           y1 = Math.floor(py + P_HEIGHT);
    var z0 = Math.floor(pz - HALF_W), z1 = Math.floor(pz + HALF_W);
    for (var X = x0; X <= x1; X++)
      for (var Y = y0; Y <= y1; Y++)
        for (var Z = z0; Z <= z1; Z++)
          if (getBlock(X, Y, Z) !== 0) return true;
    return false;
  }

  var keys = {};
  window.addEventListener("keydown", function (e) {
    keys[e.code] = true;
    if (e.code.indexOf("Digit") === 0) {
      var n = parseInt(e.code.slice(5), 10);
      if (n >= 1 && n <= 7) selectSlot(n - 1);
    }
    if (e.code === "Space") e.preventDefault();
  });
  window.addEventListener("keyup", function (e) { keys[e.code] = false; });
  window.addEventListener("blur", function () { for (var k in keys) keys[k] = false; });

  function updatePlayer(dt) {
    var f = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0);
    var r = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0);
    var sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
    var mx = (-sin * f + cos * r) * WALK_SPEED;
    var mz = (-cos * f - sin * r) * WALK_SPEED;

    if (keys.Space && player.onGround) player.vy = JUMP_V;
    player.vy -= GRAVITY * dt;
    if (player.vy < -50) player.vy = -50;

    // X axis
    player.x += mx * dt;
    if (collides(player.x, player.y, player.z)) player.x -= mx * dt;
    // Z axis
    player.z += mz * dt;
    if (collides(player.x, player.y, player.z)) player.z -= mz * dt;
    // Y axis
    player.onGround = false;
    player.y += player.vy * dt;
    if (collides(player.x, player.y, player.z)) {
      if (player.vy < 0) player.onGround = true;
      player.y -= player.vy * dt;
      player.vy = 0;
    }

    if (player.y < -20) respawn();

    camera.position.set(player.x, player.y + EYE, player.z);
    camera.rotation.set(player.pitch, player.yaw, 0);
  }

  // ---------- Pointer lock, mouse, input ----------
  var overlay = document.getElementById("overlay");
  var locked = false;

  overlay.addEventListener("click", function () {
    renderer.domElement.requestPointerLock();
  });
  document.addEventListener("pointerlockchange", function () {
    locked = (document.pointerLockElement === renderer.domElement);
    overlay.style.display = locked ? "none" : "flex";
    if (!locked) { for (var k in keys) keys[k] = false; }
  });
  document.addEventListener("mousemove", function (e) {
    if (!locked) return;
    player.yaw -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    var lim = Math.PI / 2 - 0.01;
    if (player.pitch > lim) player.pitch = lim;
    if (player.pitch < -lim) player.pitch = -lim;
  });
  document.addEventListener("mousedown", function (e) {
    if (!locked) return;
    if (e.button === 0) breakBlock();
    else if (e.button === 2) placeBlock();
  });
  document.addEventListener("contextmenu", function (e) { e.preventDefault(); });
  document.addEventListener("wheel", function (e) {
    e.preventDefault();
    selectSlot((selected + (e.deltaY > 0 ? 1 : 6)) % 7);
  }, { passive: false });

  // ---------- Hotbar ----------
  var selected = 0;
  var hotbarEl = document.getElementById("hotbar");
  var slotEls = [];
  HOTBAR_IDS.forEach(function (id, i) {
    var s = document.createElement("div");
    s.className = "slot";
    var hex = ("000000" + BLOCK_COLORS[id].toString(16)).slice(-6);
    s.innerHTML = '<span class="num">' + (i + 1) + '</span>' +
                  '<div class="swatch" style="background:#' + hex + '"></div>';
    hotbarEl.appendChild(s);
    slotEls.push(s);
  });
  function selectSlot(i) {
    selected = i;
    slotEls.forEach(function (s, j) { s.classList.toggle("sel", j === i); });
  }
  selectSlot(0);

  // ---------- Break / place ----------
  var raycaster = new THREE.Raycaster();
  raycaster.far = REACH;
  var centerVec2 = new THREE.Vector2(0, 0);
  var target = null;

  function updateTarget() {
    target = null;
    if (!locked) { outline.visible = false; return; }
    raycaster.setFromCamera(centerVec2, camera);
    var hits = raycaster.intersectObjects(chunkMeshes);
    if (hits.length > 0) {
      var hit = hits[0];
      var p = hit.point, n = hit.face.normal;
      target = {
        bx: Math.floor(p.x - n.x * 0.5),
        by: Math.floor(p.y - n.y * 0.5),
        bz: Math.floor(p.z - n.z * 0.5),
        px: Math.floor(p.x + n.x * 0.5),
        py: Math.floor(p.y + n.y * 0.5),
        pz: Math.floor(p.z + n.z * 0.5)
      };
      outline.position.set(target.bx + 0.5, target.by + 0.5, target.bz + 0.5);
      outline.visible = true;
    } else {
      outline.visible = false;
    }
  }

  function breakBlock() {
    if (!target) return;
    if (target.by <= 0) return; // unbreakable bottom layer
    if (setBlock(target.bx, target.by, target.bz, 0)) {
      rebuildAround(target.bx, target.by, target.bz);
    }
  }

  function placeBlock() {
    if (!target) return;
    var bx = target.px, by = target.py, bz = target.pz;
    if (getBlock(bx, by, bz) !== 0) return;
    // Must not overlap the player
    if (bx + 1 > player.x - HALF_W && bx < player.x + HALF_W &&
        by + 1 > player.y &&            by < player.y + P_HEIGHT &&
        bz + 1 > player.z - HALF_W && bz < player.z + HALF_W) return;
    if (setBlock(bx, by, bz, HOTBAR_IDS[selected])) {
      rebuildAround(bx, by, bz);
    }
  }

  // ---------- World streaming ----------
  function updateWorld() {
    var pcx = Math.floor(player.x / 16), pcz = Math.floor(player.z / 16);

    // Generate data within 5 chunks (max 4/frame)
    var gen = 0;
    for (var dz = -5; dz <= 5 && gen < 4; dz++) {
      for (var dx = -5; dx <= 5 && gen < 4; dx++) {
        var gx = pcx + dx, gz = pcz + dz;
        if (!chunks.has(chunkKey(gx, gz))) {
          generateChunk(gx, gz);
          gen++;
        }
      }
    }

    // Build meshes within 4 chunks once 4 neighbors have data (max 2/frame)
    var built = 0;
    for (var mz2 = -4; mz2 <= 4 && built < 2; mz2++) {
      for (var mx2 = -4; mx2 <= 4 && built < 2; mx2++) {
        var bx2 = pcx + mx2, bz2 = pcz + mz2;
        var c = chunks.get(chunkKey(bx2, bz2));
        if (c && !c.mesh &&
            chunks.has(chunkKey(bx2 + 1, bz2)) && chunks.has(chunkKey(bx2 - 1, bz2)) &&
            chunks.has(chunkKey(bx2, bz2 + 1)) && chunks.has(chunkKey(bx2, bz2 - 1))) {
          buildChunkMesh(bx2, bz2);
          built++;
        }
      }
    }

    // Remove chunks farther than 7
    for (var entry of Array.from(chunks.entries())) {
      var key = entry[0], ch = entry[1];
      var comma = key.indexOf(",");
      var cx = parseInt(key.slice(0, comma), 10), cz = parseInt(key.slice(comma + 1), 10);
      if (Math.max(Math.abs(cx - pcx), Math.abs(cz - pcz)) > 7) {
        if (ch.mesh) {
          scene.remove(ch.mesh);
          var mi = chunkMeshes.indexOf(ch.mesh);
          if (mi >= 0) chunkMeshes.splice(mi, 1);
          ch.mesh.geometry.dispose();
          ch.mesh = null;
        }
        chunks.delete(key);
      }
    }
  }

  // ---------- Clouds & water follow ----------
  function updateEnvironment(dt) {
    for (var i = 0; i < clouds.length; i++) {
      var cl = clouds[i];
      cl.position.x += cl.userData.speed * dt;
      if (cl.position.x > player.x + 160) cl.position.x = player.x - 160;
      if (cl.position.x < player.x - 160) cl.position.x = player.x + 160;
      if (cl.position.z > player.z + 160) cl.position.z = player.z - 160;
      if (cl.position.z < player.z - 160) cl.position.z = player.z + 160;
    }
    water.position.x = player.x;
    water.position.z = player.z;
  }

  // ---------- Init & main loop ----------
  window.addEventListener("resize", function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  generateChunk(0, 0); // ensure spawn terrain exists
  player.y = spawnHeight(8, 8);

  var clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    var dt = clock.getDelta();
    if (dt > 0.05) dt = 0.05;

    updateWorld();
    updatePlayer(dt);
    updateTarget();
    updateEnvironment(dt);

    renderer.render(scene, camera);
  }
  animate();
})();
</script>
</body>
</html>
```