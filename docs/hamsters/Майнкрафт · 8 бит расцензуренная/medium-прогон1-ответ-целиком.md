

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Voxel Craft</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; width: 100%; height: 100%; background: #000; }
  canvas { display: block; }
  #overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.65);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: #fff; font-family: Arial, Helvetica, sans-serif; z-index: 10; cursor: pointer; text-align: center;
  }
  #overlay h1 { font-size: 52px; margin: 0 0 24px; text-shadow: 3px 3px 0 #000; letter-spacing: 2px; }
  #overlay .controls {
    background: rgba(0,0,0,0.45); padding: 16px 28px; border-radius: 8px;
    line-height: 1.8; font-size: 15px; border: 1px solid rgba(255,255,255,0.15);
  }
  #overlay .play { margin-top: 28px; font-size: 24px; color: #ffd54f; text-shadow: 2px 2px 0 #000; animation: pulse 1.2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.45; } }
  #crosshair {
    position: fixed; left: 50%; top: 50%; width: 20px; height: 20px;
    transform: translate(-50%, -50%); pointer-events: none; z-index: 5;
  }
  #crosshair::before, #crosshair::after { content: ''; position: absolute; background: rgba(255,255,255,0.85); }
  #crosshair::before { left: 9px; top: 0; width: 2px; height: 20px; }
  #crosshair::after { left: 0; top: 9px; width: 20px; height: 2px; }
  #hotbar {
    position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 5px; background: rgba(0,0,0,0.5); padding: 7px;
    border-radius: 6px; z-index: 5;
  }
  .slot {
    width: 46px; height: 46px; position: relative;
    border: 2px solid rgba(255,255,255,0.25); border-radius: 4px;
  }
  .slot.selected { border-color: #fff; box-shadow: 0 0 6px rgba(255,255,255,0.7); }
  .slot span {
    position: absolute; left: 5px; top: 2px; font: bold 12px Arial, sans-serif;
    color: #fff; text-shadow: 1px 1px 1px #000;
  }
</style>
</head>
<body>
<div id="overlay">
  <h1>&#9935; VOXEL CRAFT</h1>
  <div class="controls">
    <b>W A S D</b> &mdash; move &nbsp;|&nbsp; <b>Space</b> &mdash; jump<br>
    <b>Mouse</b> &mdash; look &nbsp;|&nbsp; <b>Left click</b> &mdash; break block &nbsp;|&nbsp; <b>Right click</b> &mdash; place block<br>
    <b>1&ndash;7</b> or <b>wheel</b> &mdash; select block
  </div>
  <div class="play">Click to play</div>
</div>
<div id="crosshair"></div>
<div id="hotbar"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  'use strict';

  // ---------------- Constants ----------------
  var CHUNK = 16, HEIGHT = 80;
  var BLOCKS = {
    1: { name: 'Grass',  color: 0x4caf50 },
    2: { name: 'Dirt',   color: 0x795548 },
    3: { name: 'Stone',  color: 0x9e9e9e },
    4: { name: 'Sand',   color: 0xe7d9a8 },
    5: { name: 'Wood',   color: 0x8d6e63 },
    6: { name: 'Leaves', color: 0x2e7d32 },
    7: { name: 'Snow',   color: 0xffffff }
  };
  var HOTBAR = [1, 2, 3, 4, 5, 6, 7];
  var selected = 0;

  var BLOCK_RGB = {};
  for (var k in BLOCKS) {
    var c = BLOCKS[k].color;
    BLOCK_RGB[k] = [(c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255];
  }

  // Face table: outward normal, 4 CCW-from-outside corners, brightness factor.
  var FACES = [
    { d: [ 1, 0, 0], v: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]], shade: 0.8  },
    { d: [-1, 0, 0], v: [[0,0,1],[0,1,1],[0,1,0],[0,0,0]], shade: 0.8  },
    { d: [ 0, 1, 0], v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]], shade: 1.0  },
    { d: [ 0,-1, 0], v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], shade: 0.55 },
    { d: [ 0, 0, 1], v: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], shade: 0.8  },
    { d: [ 0, 0,-1], v: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]], shade: 0.8  }
  ];

  // ---------------- Deterministic value noise ----------------
  function hash2i(x, y) {
    var n = Math.imul(x, 374761393) + Math.imul(y, 668265263);
    n = Math.imul(n ^ (n >>> 13), 1274126177);
    n ^= n >>> 16;
    return (n >>> 0) / 4294967296;
  }
  function hash3i(x, y, z) {
    var n = Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(z, 1440662683);
    n = Math.imul(n ^ (n >>> 13), 1274126177);
    n ^= n >>> 16;
    return (n >>> 0) / 4294967296;
  }
  function smoothstep(t) { return t * t * (3 - 2 * t); }

  function noise2(x, y) {
    var xi = Math.floor(x), yi = Math.floor(y);
    var xf = x - xi, yf = y - yi;
    var a = hash2i(xi, yi),     b = hash2i(xi + 1, yi);
    var c = hash2i(xi, yi + 1), d = hash2i(xi + 1, yi + 1);
    var u = smoothstep(xf), v = smoothstep(yf);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }

  function fractal2(x, y) {
    var f = 0, amp = 0.5, freq = 1;
    for (var i = 0; i < 4; i++) {
      f += amp * noise2(x * freq, y * freq);
      freq *= 2; amp *= 0.5;
    }
    return f;
  }

  function noise3(x, y, z) {
    var xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    var xf = x - xi, yf = y - yi, zf = z - zi;
    var u = smoothstep(xf), v = smoothstep(yf), w = smoothstep(zf);
    var c000 = hash3i(xi, yi, zi),     c100 = hash3i(xi + 1, yi, zi);
    var c010 = hash3i(xi, yi + 1, zi), c110 = hash3i(xi + 1, yi + 1, zi);
    var c001 = hash3i(xi, yi, zi + 1), c101 = hash3i(xi + 1, yi, zi + 1);
    var c011 = hash3i(xi, yi + 1, zi + 1), c111 = hash3i(xi + 1, yi + 1, zi + 1);
    var x00 = c000 + (c100 - c000) * u, x10 = c010 + (c110 - c010) * u;
    var x01 = c001 + (c101 - c001) * u, x11 = c011 + (c111 - c011) * u;
    var y0 = x00 + (x10 - x00) * v,    y1 = x01 + (x11 - x01) * v;
    return y0 + (y1 - y0) * w;
  }

  function columnHeight(x, z) {
    var m = fractal2(x * 0.004, z * 0.004);
    var h = fractal2(x * 0.02 + 37.7, z * 0.02 + 91.3);
    return Math.floor(5 + m * m * 58 + h * 10);
  }

  // ---------------- Chunk storage ----------------
  var chunks = new Map();       // "cx,cz" -> { data: Uint8Array, mesh: Mesh|null }
  var chunkMeshes = [];         // all live chunk meshes (for raycasting)
  var material = new THREE.MeshLambertMaterial({ vertexColors: true });

  function idx(lx, y, lz) { return (y * CHUNK + lz) * CHUNK + lx; }

  function getBlock(wx, wy, wz) {
    if (wy < 0 || wy >= HEIGHT) return 0;
    var cx = Math.floor(wx / CHUNK), cz = Math.floor(wz / CHUNK);
    var c = chunks.get(cx + ',' + cz);
    if (!c || !c.data) return 0;
    var lx = wx - cx * CHUNK, lz = wz - cz * CHUNK;
    return c.data[idx(lx, wy, lz)];
  }

  function setBlock(wx, wy, wz, id) {
    if (wy < 0 || wy >= HEIGHT) return false;
    var cx = Math.floor(wx / CHUNK), cz = Math.floor(wz / CHUNK);
    var c = chunks.get(cx + ',' + cz);
    if (!c || !c.data) return false;
    var lx = wx - cx * CHUNK, lz = wz - cz * CHUNK;
    c.data[idx(lx, wy, lz)] = id;
    return true;
  }

  // ---------------- Terrain generation ----------------
  function generateData(cx, cz) {
    var data = new Uint8Array(CHUNK * HEIGHT * CHUNK);
    for (var lx = 0; lx < CHUNK; lx++) {
      for (var lz = 0; lz < CHUNK; lz++) {
        var wx = cx * CHUNK + lx, wz = cz * CHUNK + lz;
        var H = columnHeight(wx, wz);
        var beach = H <= 16, rock = H >= 37, snow = H >= 46;
        for (var y = 0; y < H && y < HEIGHT; y++) {
          var id;
          if (y === 0) id = 3;
          else if (y === H - 1) id = snow ? 7 : (rock ? 3 : (beach ? 4 : 1));
          else if (y >= H - 4) id = beach ? 4 : (rock ? 3 : 2);
          else id = 3;
          if (y >= 3 && y <= H - 2 && noise3(wx * 0.09, y * 0.09, wz * 0.09) > 0.67) id = 0;
          data[idx(lx, y, lz)] = id;
        }
        // Trees
        var surf = (H - 1 >= 0 && H - 1 < HEIGHT) ? data[idx(lx, H - 1, lz)] : 0;
        if (surf === 1 && H + 5 < HEIGHT && hash2i(wx * 3 + 11, wz * 3 + 7) < 0.02) {
          for (var ty = H; ty < H + 4; ty++) data[idx(lx, ty, lz)] = 5; // trunk
          for (var dy = 2; dy <= 3; dy++) {                              // 5x5 layers x2
            for (var ox = -2; ox <= 2; ox++) for (var oz = -2; oz <= 2; oz++) {
              var nx = lx + ox, nz = lz + oz;
              if (nx < 0 || nx >= CHUNK || nz < 0 || nz >= CHUNK) continue;
              if (data[idx(nx, H + dy, nz)] === 0) data[idx(nx, H + dy, nz)] = 6;
            }
          }
          for (var ox2 = -1; ox2 <= 1; ox2++) for (var oz2 = -1; oz2 <= 1; oz2++) { // 3x3
            var nx2 = lx + ox2, nz2 = lz + oz2;
            if (nx2 < 0 || nx2 >= CHUNK || nz2 < 0 || nz2 >= CHUNK) continue;
            if (data[idx(nx2, H + 4, nz2)] === 0) data[idx(nx2, H + 4, nz2)] = 6;
          }
          if (data[idx(lx, H + 5, lz)] === 0) data[idx(lx, H + 5, lz)] = 6; // 1 on top
        }
      }
    }
    return data;
  }

  // ---------------- Scene ----------------
  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb);
  scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

  var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 400);
  camera.rotation.order = 'YXZ';

  var renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  var sun = new THREE.DirectionalLight(0xffffff, 0.8);
  sun.position.set(0.5, 1, 0.3);
  scene.add(sun);

  // Water plane (visual only)
  var water = new THREE.Mesh(
    new THREE.PlaneGeometry(400, 400),
    new THREE.MeshLambertMaterial({ color: 0x2f7fd4, transparent: true, opacity: 0.6, depthWrite: false })
  );
  water.rotation.x = -Math.PI / 2;
  scene.add(water);

  // Clouds
  var clouds = [];
  var cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
  for (var ci = 0; ci < 25; ci++) {
    var cg = new THREE.BoxGeometry(10 + Math.random() * 25, 1, 8 + Math.random() * 15);
    var cm = new THREE.Mesh(cg, cloudMat);
    cm.position.set((Math.random() - 0.5) * 320, 88 + Math.random() * 12, (Math.random() - 0.5) * 320);
    cm.userData.speed = 1 + Math.random() * 2;
    scene.add(cm);
    clouds.push(cm);
  }

  // Target outline
  var targetBox = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
    new THREE.LineBasicMaterial({ color: 0x000000 })
  );
  targetBox.visible = false;
  scene.add(targetBox);

  // ---------------- Meshing ----------------
  function buildChunkMesh(key) {
    var c = chunks.get(key);
    if (!c || !c.data) return;
    if (c.mesh) {
      scene.remove(c.mesh);
      c.mesh.geometry.dispose();
      var mi = chunkMeshes.indexOf(c.mesh);
      if (mi >= 0) chunkMeshes.splice(mi, 1);
      c.mesh = null;
    }
    var parts = key.split(',');
    var cx = +parts[0], cz = +parts[1];
    var pos = [], nor = [], col = [];
    for (var y = 0; y < HEIGHT; y++) {
      for (var lz = 0; lz < CHUNK; lz++) {
        for (var lx = 0; lx < CHUNK; lx++) {
          var id = c.data[idx(lx, y, lz)];
          if (!id) continue;
          var wx = cx * CHUNK + lx, wy = y, wz = cz * CHUNK + lz;
          var rgb = BLOCK_RGB[id];
          for (var f = 0; f < 6; f++) {
            var fc = FACES[f];
            if (getBlock(wx + fc.d[0], wy + fc.d[1], wz + fc.d[2]) !== 0) continue;
            var s = fc.shade;
            var r = rgb[0] * s, g = rgb[1] * s, b = rgb[2] * s;
            var order = [0, 1, 2, 0, 2, 3];
            for (var i = 0; i < 6; i++) {
              var vi = fc.v[order[i]];
              pos.push(wx + vi[0], wy + vi[1], wz + vi[2]);
              nor.push(fc.d[0], fc.d[1], fc.d[2]);
              col.push(r, g, b);
            }
          }
        }
      }
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    var mesh = new THREE.Mesh(geo, material);
    scene.add(mesh);
    chunkMeshes.push(mesh);
    c.mesh = mesh;
  }

  function rebuildAt(x, y, z) {
    var cx = Math.floor(x / CHUNK), cz = Math.floor(z / CHUNK);
    var lx = x - cx * CHUNK, lz = z - cz * CHUNK;
    buildChunkMesh(cx + ',' + cz);
    if (lx === 0)  buildChunkMesh((cx - 1) + ',' + cz);
    if (lx === 15) buildChunkMesh((cx + 1) + ',' + cz);
    if (lz === 0)  buildChunkMesh(cx + ',' + (cz - 1));
    if (lz === 15) buildChunkMesh(cx + ',' + (cz + 1));
  }

  // ---------------- World streaming ----------------
  function updateWorld() {
    var pcx = Math.floor(player.pos.x / CHUNK), pcz = Math.floor(player.pos.z / CHUNK);

    // Generate data within 5 chunks (max 4/frame, nearest first)
    var toGen = [];
    for (var dx = -5; dx <= 5; dx++) for (var dz = -5; dz <= 5; dz++) {
      var key = (pcx + dx) + ',' + (pcz + dz);
      if (!chunks.has(key)) toGen.push([Math.abs(dx) + Math.abs(dz), key]);
    }
    toGen.sort(function (a, b) { return a[0] - b[0]; });
    var genCount = 0;
    for (var gi = 0; gi < toGen.length && genCount < 4; gi++) {
      var gp = toGen[gi][1].split(',');
      chunks.set(toGen[gi][1], { data: generateData(+gp[0], +gp[1]), mesh: null });
      genCount++;
    }

    // Build meshes within 4 chunks whose 4 neighbors have data (max 2/frame)
    var toBuild = [];
    for (var bx = -4; bx <= 4; bx++) for (var bz = -4; bz <= 4; bz++) {
      var ccx = pcx + bx, ccz = pcz + bz;
      var ckey = ccx + ',' + ccz;
      var cc = chunks.get(ckey);
      if (!cc || !cc.data || cc.mesh) continue;
      if (!chunks.has((ccx - 1) + ',' + ccz) || !chunks.has((ccx + 1) + ',' + ccz) ||
          !chunks.has(ccx + ',' + (ccz - 1)) || !chunks.has(ccx + ',' + (ccz + 1))) continue;
      toBuild.push([Math.abs(bx) + Math.abs(bz), ckey]);
    }
    toBuild.sort(function (a, b) { return a[0] - b[0]; });
    var buildCount = 0;
    for (var bi = 0; bi < toBuild.length && buildCount < 2; bi++) {
      buildChunkMesh(toBuild[bi][1]);
      buildCount++;
    }

    // Remove chunks farther than 7
    var dead = [];
    chunks.forEach(function (c, key) {
      var kp = key.split(',');
      var d = Math.max(Math.abs(+kp[0] - pcx), Math.abs(+kp[1] - pcz));
      if (d > 7) dead.push(key);
    });
    for (var di = 0; di < dead.length; di++) {
      var dc = chunks.get(dead[di]);
      if (dc.mesh) {
        scene.remove(dc.mesh);
        dc.mesh.geometry.dispose();
        var dm = chunkMeshes.indexOf(dc.mesh);
        if (dm >= 0) chunkMeshes.splice(dm, 1);
      }
      chunks.delete(dead[di]);
    }
  }

  // ---------------- Player ----------------
  var player = {
    pos: new THREE.Vector3(8, columnHeight(8, 8) + 0.1, 8),
    vel: new THREE.Vector3(0, 0, 0),
    onGround: false,
    yaw: 0,
    pitch: 0
  };
  var SPAWN = { x: 8, z: 8 };
  var keys = {};

  function collides(x, y, z) {
    var hw = 0.3;
    var x0 = Math.floor(x - hw), x1 = Math.floor(x + hw);
    var y0 = Math.floor(y),     y1 = Math.floor(y + 1.7999);
    var z0 = Math.floor(z - hw), z1 = Math.floor(z + hw);
    for (var bx = x0; bx <= x1; bx++)
      for (var by = y0; by <= y1; by++)
        for (var bz = z0; bz <= z1; bz++)
          if (getBlock(bx, by, bz) !== 0) return true;
    return false;
  }

  function respawn() {
    player.pos.set(SPAWN.x, columnHeight(SPAWN.x, SPAWN.z) + 0.1, SPAWN.z);
    player.vel.set(0, 0, 0);
  }

  function updatePlayer(dt) {
    var speed = 5.5;
    var fx = 0, fz = 0;
    if (keys['KeyW']) fz += 1;
    if (keys['KeyS']) fz -= 1;
    if (keys['KeyA']) fx -= 1;
    if (keys['KeyD']) fx += 1;
    var sin = Math.sin(player.yaw), cos = Math.cos(player.yaw);
    var vx = 0, vz = 0;
    if (fx !== 0 || fz !== 0) {
      var len = Math.sqrt(fx * fx + fz * fz);
      fx /= len; fz /= len;
      vx = (fx * cos - fz * sin) * speed;
      vz = (-fx * sin - fz * cos) * speed;
    }
    player.vel.x = vx;
    player.vel.z = vz;
    player.vel.y -= 25 * dt;
    if (keys['Space'] && player.onGround) {
      player.vel.y = 8.5;
      player.onGround = false;
    }

    // X axis
    var nx = player.pos.x + player.vel.x * dt;
    if (!collides(nx, player.pos.y, player.pos.z)) player.pos.x = nx;
    else player.vel.x = 0;
    // Z axis
    var nz = player.pos.z + player.vel.z * dt;
    if (!collides(player.pos.x, player.pos.y, nz)) player.pos.z = nz;
    else player.vel.z = 0;
    // Y axis
    var ny = player.pos.y + player.vel.y * dt;
    if (!collides(player.pos.x, ny, player.pos.z)) {
      player.pos.y = ny;
      player.onGround = false;
    } else {
      if (player.vel.y < 0) player.onGround = true;
      player.vel.y = 0;
    }

    if (player.pos.y < -20) respawn();

    camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
    camera.rotation.set(player.pitch, player.yaw, 0);
  }

  // ---------------- Interaction ----------------
  var raycaster = new THREE.Raycaster();
  raycaster.far = 6;
  var centerV2 = new THREE.Vector2(0, 0);
  var currentTarget = null;

  function updateTarget() {
    raycaster.setFromCamera(centerV2, camera);
    var hits = raycaster.intersectObjects(chunkMeshes);
    if (hits.length > 0) {
      var h = hits[0];
      var n = h.face.normal;
      var p = h.point;
      var bx = Math.floor(p.x - n.x * 0.5);
      var by = Math.floor(p.y - n.y * 0.5);
      var bz = Math.floor(p.z - n.z * 0.5);
      currentTarget = { x: bx, y: by, z: bz };
      targetBox.position.set(bx + 0.5, by + 0.5, bz + 0.5);
      targetBox.visible = true;
    } else {
      currentTarget = null;
      targetBox.visible = false;
    }
  }

  function isLocked() { return document.pointerLockElement === renderer.domElement; }

  function breakBlock() {
    if (!currentTarget) return;
    var t = currentTarget;
    if (t.y === 0) return;
    if (getBlock(t.x, t.y, t.z) === 0) return;
    setBlock(t.x, t.y, t.z, 0);
    rebuildAt(t.x, t.y, t.z);
  }

  function placeBlock() {
    if (!currentTarget) return;
    var t = currentTarget;
    if (getBlock(t.x, t.y, t.z) !== 0) return;
    var p = player.pos;
    if (t.x < p.x + 0.3 && t.x + 1 > p.x - 0.3 &&
        t.y < p.y + 1.8 && t.y + 1 > p.y &&
        t.z < p.z + 0.3 && t.z + 1 > p.z - 0.3) return;
    setBlock(t.x, t.y, t.z, HOTBAR[selected]);
    rebuildAt(t.x, t.y, t.z);
  }

  // ---------------- Input ----------------
  document.addEventListener('contextmenu', function (e) { e.preventDefault(); });

  document.addEventListener('mousedown', function (e) {
    if (!isLocked()) return;
    if (e.button === 0) breakBlock();
    else if (e.button === 2) placeBlock();
  });

  document.addEventListener('mousemove', function (e) {
    if (!isLocked()) return;
    player.yaw -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    var lim = Math.PI / 2 - 0.01;
    if (player.pitch > lim) player.pitch = lim;
    if (player.pitch < -lim) player.pitch = -lim;
  });

  window.addEventListener('wheel', function (e) {
    selected = ((selected + (e.deltaY > 0 ? 1 : -1)) % 7 + 7) % 7;
    updateHotbar();
  }, { passive: true });

  document.addEventListener('keydown', function (e) {
    keys[e.code] = true;
    if (e.code === 'Space') e.preventDefault();
    if (e.code >= 'Digit1' && e.code <= 'Digit7') {
      selected = +e.code.charAt(5) - 1;
      updateHotbar();
    }
  });
  document.addEventListener('keyup', function (e) { keys[e.code] = false; });

  var overlay = document.getElementById('overlay');
  overlay.addEventListener('click', function () {
    renderer.domElement.requestPointerLock();
  });
  document.addEventListener('pointerlockchange', function () {
    overlay.style.display = isLocked() ? 'none' : 'flex';
  });

  // ---------------- Hotbar UI ----------------
  var hotbarEl = document.getElementById('hotbar');
  HOTBAR.forEach(function (id, i) {
    var d = document.createElement('div');
    d.className = 'slot';
    d.style.background = '#' + BLOCKS[id].color.toString(16).padStart(6, '0');
    var s = document.createElement('span');
    s.textContent = i + 1;
    d.appendChild(s);
    hotbarEl.appendChild(d);
  });
  function updateHotbar() {
    var kids = hotbarEl.children;
    for (var i = 0; i < kids.length; i++) kids[i].classList.toggle('selected', i === selected);
  }
  updateHotbar();

  // ---------------- Misc per-frame ----------------
  function updateClouds(dt) {
    for (var i = 0; i < clouds.length; i++) {
      var c = clouds[i];
      c.position.x += c.userData.speed * dt;
      if (c.position.x - player.pos.x > 180) c.position.x -= 360;
      if (c.position.x - player.pos.x < -180) c.position.x += 360;
      if (c.position.z - player.pos.z > 180) c.position.z -= 360;
      if (c.position.z - player.pos.z < -180) c.position.z += 360;
    }
  }

  window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // ---------------- Main loop ----------------
  var last = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    var now = performance.now();
    var dt = (now - last) / 1000;
    last = now;
    if (dt > 0.05) dt = 0.05;

    updateWorld();
    updatePlayer(dt);
    updateTarget();
    water.position.set(player.pos.x, 14.3, player.pos.z);
    updateClouds(dt);
    renderer.render(scene, camera);
  }
  animate();
})();
</script>
</body>
</html>
```