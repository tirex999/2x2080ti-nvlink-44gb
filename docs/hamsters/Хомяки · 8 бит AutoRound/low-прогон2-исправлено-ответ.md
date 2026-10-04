**Причина:** страница использует `importmap` + ES-модули с CDN (unpkg.com). При открытии файла через `file://` или при недоступности/задержке CDN браузер молча не выполняет весь `<script type="module">` — Three.js не загружается, сцена не создаётся, остаётся только тёмный фон.

**Исправление:** заменил модульный импорт на обычные `<script src=…>` теги (глобальный UMD-билд Three.js r128 + OrbitControls из `examples/js`). Теперь файл работает и через `file://`, и без importmap.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Low-Poly Hamster Playground</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; background: #1a1a2e; font-family: 'Segoe UI', sans-serif; }
canvas { display: block; }
#info {
  position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
  color: #fff; background: rgba(0,0,0,0.5); padding: 10px 24px;
  border-radius: 20px; font-size: 14px; pointer-events: none;
  backdrop-filter: blur(4px);
}
</style>
</head>
<body>
<div id="info">🐹 Drag to rotate • Scroll to zoom</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
(function () {
  // --- SCENE SETUP ---
  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb);
  scene.fog = new THREE.Fog(0x87ceeb, 15, 30);

  var camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(6, 5, 8);

  var renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);

  var controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxPolarAngle = Math.PI / 2.1;
  controls.minDistance = 4;
  controls.maxDistance = 15;
  controls.target.set(0, 1, 0);

  // --- LIGHTS ---
  var ambientLight = new THREE.AmbientLight(0xfff5e6, 0.6);
  scene.add(ambientLight);

  var sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
  sunLight.position.set(5, 10, 5);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(1024, 1024);
  sunLight.shadow.camera.near = 1;
  sunLight.shadow.camera.far = 25;
  sunLight.shadow.camera.left = -6;
  sunLight.shadow.camera.right = 6;
  sunLight.shadow.camera.top = 6;
  sunLight.shadow.camera.bottom = -6;
  scene.add(sunLight);

  var fillLight = new THREE.DirectionalLight(0xffd4a0, 0.3);
  fillLight.position.set(-3, 4, -3);
  scene.add(fillLight);

  // --- MATERIAL HELPER ---
  function mat(color) {
    return new THREE.MeshStandardMaterial({ color: color, flatShading: true, roughness: 0.8, metalness: 0.05 });
  }

  // --- CAGE ---
  function createCage() {
    var group = new THREE.Group();
    var W = 7, H = 3.5, D = 5;
    var barMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, flatShading: true, roughness: 0.3, metalness: 0.6 });

    var trayGeo = new THREE.BoxGeometry(W + 0.3, 0.3, D + 0.3);
    var tray = new THREE.Mesh(trayGeo, mat(0x4a90d9));
    tray.position.y = -0.15;
    tray.receiveShadow = true;
    group.add(tray);

    var floorGeo = new THREE.BoxGeometry(W, 0.15, D);
    var floor = new THREE.Mesh(floorGeo, mat(0xf5deb3));
    floor.position.y = 0.075;
    floor.receiveShadow = true;
    group.add(floor);

    var barRadius = 0.03;
    var barGeoV = new THREE.CylinderGeometry(barRadius, barRadius, H, 6);
    var spacingX = W / 8;
    var spacingZ = D / 6;

    for (var i = 0; i <= 8; i++) {
      var x = -W / 2 + i * spacingX;
      var barF = new THREE.Mesh(barGeoV, barMat);
      barF.position.set(x, H / 2, D / 2);
      group.add(barF);
      var barB = new THREE.Mesh(barGeoV, barMat);
      barB.position.set(x, H / 2, -D / 2);
      group.add(barB);
    }
    for (var j = 1; j <= 5; j++) {
      var z = -D / 2 + j * spacingZ;
      var barL = new THREE.Mesh(barGeoV, barMat);
      barL.position.set(-W / 2, H / 2, z);
      group.add(barL);
      var barR = new THREE.Mesh(barGeoV, barMat);
      barR.position.set(W / 2, H / 2, z);
      group.add(barR);
    }

    var barGeoH = new THREE.CylinderGeometry(barRadius, barRadius, W, 6);
    barGeoH.rotateZ(Math.PI / 2);
    var hLevels = [0.5, 1.2, 1.9, 2.6, 3.3];
    for (var k = 0; k < hLevels.length; k++) {
      var y = hLevels[k];
      var barTop = new THREE.Mesh(barGeoH, barMat);
      barTop.position.set(0, y, D / 2);
      group.add(barTop);
      var barBot = new THREE.Mesh(barGeoH, barMat);
      barBot.position.set(0, y, -D / 2);
      group.add(barBot);
    }

    var barGeoSide = new THREE.CylinderGeometry(barRadius, barRadius, D, 6);
    barGeoSide.rotateX(Math.PI / 2);
    for (var k2 = 0; k2 < hLevels.length; k2++) {
      var y2 = hLevels[k2];
      var barSL = new THREE.Mesh(barGeoSide, barMat);
      barSL.position.set(-W / 2, y2, 0);
      group.add(barSL);
      var barSR = new THREE.Mesh(barGeoSide, barMat);
      barSR.position.set(W / 2, y2, 0);
      group.add(barSR);
    }

    var topBarGeo = new THREE.CylinderGeometry(0.05, 0.05, W, 6);
    topBarGeo.rotateZ(Math.PI / 2);
    var topF = new THREE.Mesh(topBarGeo, barMat);
    topF.position.set(0, H, D / 2);
    group.add(topF);
    var topB = new THREE.Mesh(topBarGeo, barMat);
    topB.position.set(0, H, -D / 2);
    group.add(topB);

    var topSideGeo = new THREE.CylinderGeometry(0.05, 0.05, D, 6);
    topSideGeo.rotateX(Math.PI / 2);
    var topL = new THREE.Mesh(topSideGeo, barMat);
    topL.position.set(-W / 2, H, 0);
    group.add(topL);
    var topR = new THREE.Mesh(topSideGeo, barMat);
    topR.position.set(W / 2, H, 0);
    group.add(topR);

    return group;
  }

  // --- BEDDING ---
  function createBedding() {
    var group = new THREE.Group();
    var colors = [0xf5deb3, 0xdeb887, 0xd2b48c, 0xc4a882];
    for (var i = 0; i < 60; i++) {
      var size = 0.08 + Math.random() * 0.1;
      var geo = new THREE.DodecahedronGeometry(size, 0);
      var m = new THREE.Mesh(geo, mat(colors[Math.floor(Math.random() * colors.length)]));
      m.position.set(
        (Math.random() - 0.5) * 6.5,
        0.15 + Math.random() * 0.05,
        (Math.random() - 0.5) * 4.5
      );
      m.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
      m.receiveShadow = true;
      group.add(m);
    }
    return group;
  }

  // --- EXERCISE WHEEL ---
  function createWheel() {
    var group = new THREE.Group();
    var metalMat = new THREE.MeshStandardMaterial({ color: 0xe0e0e0, flatShading: true, roughness: 0.3, metalness: 0.5 });

    var ringGeo = new THREE.TorusGeometry(0.7, 0.06, 6, 12);
    var ring = new THREE.Mesh(ringGeo, metalMat);
    ring.position.y = 0.7;
    group.add(ring);

    var spokesGroup = new THREE.Group();
    spokesGroup.position.y = 0.7;
    var spokeGeo = new THREE.CylinderGeometry(0.025, 0.025, 1.3, 5);
    for (var i = 0; i < 6; i++) {
      var spoke = new THREE.Mesh(spokeGeo, metalMat);
      spoke.rotation.z = (i / 6) * Math.PI;
      spokesGroup.add(spoke);
    }
    group.add(spokesGroup);

    var hubGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.15, 8);
    hubGeo.rotateX(Math.PI / 2);
    var hub = new THREE.Mesh(hubGeo, metalMat);
    hub.position.y = 0.7;
    group.add(hub);

    var standGeo = new THREE.CylinderGeometry(0.05, 0.05, 0.7, 6);
    var standL = new THREE.Mesh(standGeo, metalMat);
    standL.position.set(0, 0.35, 0.3);
    group.add(standL);
    var standR = new THREE.Mesh(standGeo, metalMat);
    standR.position.set(0, 0.35, -0.3);
    group.add(standR);

    var baseGeo = new THREE.BoxGeometry(0.8, 0.08, 0.7);
    var base = new THREE.Mesh(baseGeo, metalMat);
    base.position.y = 0.04;
    group.add(base);

    group.position.set(2.2, 0.15, -1.5);
    group.rotation.y = Math.PI / 6;

    group.userData.ring = ring;
    group.userData.spokesGroup = spokesGroup;

    return group;
  }

  // --- FOOD BOWL ---
  function createFoodBowl() {
    var group = new THREE.Group();

    var bowlGeo = new THREE.CylinderGeometry(0.35, 0.25, 0.2, 8, 1, false);
    var bowl = new THREE.Mesh(bowlGeo, mat(0xff6b6b));
    bowl.position.y = 0.1;
    bowl.castShadow = true;
    group.add(bowl);

    var pelletGeo = new THREE.SphereGeometry(0.05, 5, 4);
    var pelletColors = [0x8b4513, 0xdaa520, 0x228b22];
    for (var i = 0; i < 8; i++) {
      var pellet = new THREE.Mesh(pelletGeo, mat(pelletColors[i % 3]));
      var angle = (i / 8) * Math.PI * 2;
      var r = 0.12 + Math.random() * 0.08;
      pellet.position.set(Math.cos(angle) * r, 0.22, Math.sin(angle) * r);
      group.add(pellet);
    }

    group.position.set(-2, 0.15, 1.2);
    return group;
  }

  // --- TUNNEL ---
  function createTunnel() {
    var group = new THREE.Group();

    var tunnelGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.2, 8, 1, false);
    var tunnelMat = mat(0x90ee90);
    tunnelMat.side = THREE.DoubleSide;
    var tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
    tunnel.rotation.z = Math.PI / 2;
    tunnel.position.y = 0.3;
    tunnel.castShadow = true;
    group.add(tunnel);

    var capGeo = new THREE.TorusGeometry(0.3, 0.04, 6, 8);
    var capL = new THREE.Mesh(capGeo, mat(0x3cb371));
    capL.position.set(-0.6, 0.3, 0);
    group.add(capL);
    var capR = new THREE.Mesh(capGeo, mat(0x3cb371));
    capR.position.set(0.6, 0.3, 0);
    group.add(capR);

    group.position.set(-0.5, 0.15, -1.8);
    group.rotation.y = -Math.PI / 5;
    return group;
  }

  // --- HAMSTER FACTORY ---
  function createHamster(bodyColor, bellyColor) {
    var group = new THREE.Group();

    var bodyGeo = new THREE.SphereGeometry(0.25, 7, 6);
    var body = new THREE.Mesh(bodyGeo, mat(bodyColor));
    body.scale.set(1.2, 0.9, 1);
    body.position.y = 0.25;
    body.castShadow = true;
    group.add(body);

    var bellyGeo = new THREE.SphereGeometry(0.18, 6, 5);
    var belly = new THREE.Mesh(bellyGeo, mat(bellyColor));
    belly.scale.set(1.1, 0.7, 0.8);
    belly.position.set(0, 0.18, 0.08);
    group.add(belly);

    var headGeo = new THREE.SphereGeometry(0.18, 7, 6);
    var head = new THREE.Mesh(headGeo, mat(bodyColor));
    head.position.set(0, 0.35, 0.22);
    head.castShadow = true;
    group.add(head);

    var earGeo = new THREE.SphereGeometry(0.07, 5, 4);
    var earMat = mat(bellyColor);
    var earL = new THREE.Mesh(earGeo, earMat);
    earL.position.set(-0.1, 0.48, 0.18);
    earL.scale.set(1, 1.3, 0.6);
    group.add(earL);
    var earR = new THREE.Mesh(earGeo, earMat);
    earR.position.set(0.1, 0.48, 0.18);
    earR.scale.set(1, 1.3, 0.6);
    group.add(earR);

    var innerEarGeo = new THREE.SphereGeometry(0.04, 4, 3);
    var innerEarMat = mat(0xffb6c1);
    var innerEarL = new THREE.Mesh(innerEarGeo, innerEarMat);
    innerEarL.position.set(-0.1, 0.48, 0.2);
    group.add(innerEarL);
    var innerEarR = new THREE.Mesh(innerEarGeo, innerEarMat);
    innerEarR.position.set(0.1, 0.48, 0.2);
    group.add(innerEarR);

    var eyeGeo = new THREE.SphereGeometry(0.035, 5, 4);
    var eyeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, flatShading: true });
    var eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(-0.08, 0.38, 0.35);
    group.add(eyeL);
    var eyeR = new THREE.Mesh(eyeGeo, eyeMat);
    eyeR.position.set(0.08, 0.38, 0.35);
    group.add(eyeR);

    var shineGeo = new THREE.SphereGeometry(0.012, 4, 3);
    var shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    var shineL = new THREE.Mesh(shineGeo, shineMat);
    shineL.position.set(-0.07, 0.39, 0.37);
    group.add(shineL);
    var shineR = new THREE.Mesh(shineGeo, shineMat);
    shineR.position.set(0.09, 0.39, 0.37);
    group.add(shineR);

    var noseGeo = new THREE.SphereGeometry(0.025, 4, 3);
    var nose = new THREE.Mesh(noseGeo, mat(0xff69b4));
    nose.position.set(0, 0.33, 0.38);
    group.add(nose);

    var whiskerMat = new THREE.LineBasicMaterial({ color: 0xffffff });
    for (var side = -1; side <= 1; side += 2) {
      for (var w = 0; w < 3; w++) {
        var pts = [
          new THREE.Vector3(side * 0.05, 0.33 + w * 0.02 - 0.02, 0.36),
          new THREE.Vector3(side * 0.2, 0.32 + w * 0.03 - 0.02, 0.42)
        ];
        var wg = new THREE.BufferGeometry().setFromPoints(pts);
        var line = new THREE.Line(wg, whiskerMat);
        group.add(line);
      }
    }

    var footGeo = new THREE.SphereGeometry(0.05, 5, 4);
    var footMat = mat(bellyColor);
    var footPositions = [
      [-0.1, 0.05, 0.15], [0.1, 0.05, 0.15],
      [-0.1, 0.05, -0.15], [0.1, 0.05, -0.15]
    ];
    for (var fi = 0; fi < footPositions.length; fi++) {
      var foot = new THREE.Mesh(footGeo, footMat);
      foot.position.set(footPositions[fi][0], footPositions[fi][1], footPositions[fi][2]);
      foot.scale.set(1, 0.7, 1.2);
      group.add(foot);
    }

    var tailGeo = new THREE.SphereGeometry(0.04, 4, 3);
    var tail = new THREE.Mesh(tailGeo, mat(bodyColor));
    tail.position.set(0, 0.22, -0.25);
    tail.scale.set(0.8, 0.8, 1.2);
    group.add(tail);

    var cheekGeo = new THREE.SphereGeometry(0.08, 5, 4);
    var cheekMat = mat(bellyColor);
    var cheekL = new THREE.Mesh(cheekGeo, cheekMat);
    cheekL.position.set(-0.14, 0.3, 0.28);
    cheekL.scale.set(0.8, 1, 0.8);
    group.add(cheekL);
    var cheekR = new THREE.Mesh(cheekGeo, cheekMat);
    cheekR.position.set(0.14, 0.3, 0.28);
    cheekR.scale.set(0.8, 1, 0.8);
    group.add(cheekR);

    return group;
  }

  // --- BUILD SCENE ---
  scene.add(createCage());
  scene.add(createBedding());
  var wheel = createWheel();
  scene.add(wheel);
  scene.add(createFoodBowl());
  scene.add(createTunnel());

  var groundGeo = new THREE.PlaneGeometry(30, 30);
  var ground = new THREE.Mesh(groundGeo, mat(0x7ec850));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.35;
  ground.receiveShadow = true;
  scene.add(ground);

  function createFlower(fx, fz, fcolor) {
    var g = new THREE.Group();
    var stemGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.5, 5);
    var stem = new THREE.Mesh(stemGeo, mat(0x228b22));
    stem.position.y = 0.25;
    g.add(stem);
    var petalGeo = new THREE.SphereGeometry(0.12, 5, 4);
    var petal = new THREE.Mesh(petalGeo, mat(fcolor));
    petal.position.y = 0.55;
    petal.scale.set(1, 0.7, 1);
    g.add(petal);
    var centerGeo = new THREE.SphereGeometry(0.05, 4, 3);
    var center = new THREE.Mesh(centerGeo, mat(0xffd700));
    center.position.y = 0.58;
    g.add(center);
    g.position.set(fx, -0.35, fz);
    return g;
  }
  var flowerColors = [0xff69b4, 0xff6347, 0xda70d6, 0xffa07a];
  for (var fi2 = 0; fi2 < 8; fi2++) {
    var fa = (fi2 / 8) * Math.PI * 2;
    var fr = 6 + Math.random() * 3;
    scene.add(createFlower(Math.cos(fa) * fr, Math.sin(fa) * fr, flowerColors[fi2 % 4]));
  }

  // --- HAMSTERS ---
  var hamsterConfigs = [
    { body: 0xf4a460, belly: 0xffe4c4, name: 'Nugget' },
    { body: 0xffffff, belly: 0xfff0f0, name: 'Snowball' },
    { body: 0x8b6914, belly: 0xdeb887, name: 'Cocoa' },
    { body: 0xffb6c1, belly: 0xfff0f5, name: 'Blush' }
  ];

  var CAGE_BOUNDS = { minX: -3, maxX: 3, minZ: -2, maxZ: 2 };
  var WHEEL_POS = new THREE.Vector3(2.2, 0.15, -1.5);
  var FOOD_POS = new THREE.Vector3(-2, 0.15, 1.2);

  var hamsters = [];

  for (var hi = 0; hi < hamsterConfigs.length; hi++) {
    (function (cfg) {
      var mesh = createHamster(cfg.body, cfg.belly);
      var sx = (Math.random() - 0.5) * 4;
      var sz = (Math.random() - 0.5) * 3;
      mesh.position.set(sx, 0.15, sz);
      mesh.rotation.y = Math.random() * Math.PI * 2;
      scene.add(mesh);

      var h = {
        mesh: mesh,
        name: cfg.name,
        state: 'wander',
        target: new THREE.Vector3(sx, 0.15, sz),
        speed: 0.4 + Math.random() * 0.3,
        pauseTimer: 0,
        stateTimer: 0,
        bobPhase: Math.random() * Math.PI * 2,
        earWigglePhase: Math.random() * Math.PI * 2
      };
      pickNewTarget(h);
      hamsters.push(h);
    })(hamsterConfigs[hi]);
  }

  function pickNewTarget(h) {
    var roll = Math.random();
    if (roll < 0.2) {
      h.state = 'wheel';
      h.target.copy(WHEEL_POS).add(new THREE.Vector3((Math.random() - 0.5) * 0.5, 0, (Math.random() - 0.5) * 0.5));
    } else if (roll < 0.35) {
      h.state = 'food';
      h.target.copy(FOOD_POS).add(new THREE.Vector3((Math.random() - 0.5) * 0.5, 0, (Math.random() - 0.5) * 0.5));
    } else {
      h.state = 'wander';
      h.target.set(
        CAGE_BOUNDS.minX + Math.random() * (CAGE_BOUNDS.maxX - CAGE_BOUNDS.minX),
        0.15,
        CAGE_BOUNDS.minZ + Math.random() * (CAGE_BOUNDS.maxZ - CAGE_BOUNDS.minZ)
      );
    }
    h.stateTimer = 3 + Math.random() * 5;
  }

  function updateHamster(h, dt, time) {
    var pos = h.mesh.position;
    var target = h.target;
    var dist = pos.distanceTo(target);

    h.stateTimer -= dt;
    if (h.stateTimer <= 0) {
      if (h.state === 'pause') {
        pickNewTarget(h);
      } else {
        h.state = 'pause';
        h.pauseTimer = 1 + Math.random() * 2;
        h.stateTimer = h.pauseTimer;
      }
      return;
    }

    if (h.state === 'pause') {
      return;
    }

    if (dist > 0.3) {
      var dir = new THREE.Vector3().subVectors(target, pos);
      dir.y = 0;
      dir.normalize();

      var targetAngle = Math.atan2(dir.x, dir.z);
      var angleDiff = targetAngle - h.mesh.rotation.y;
      while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
      while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
      h.mesh.rotation.y += angleDiff * Math.min(dt * 5, 1);

      pos.addScaledVector(dir, h.speed * dt);

      h.bobPhase += dt * 12;
      h.mesh.position.y = 0.15 + Math.abs(Math.sin(h.bobPhase)) * 0.03;
      h.mesh.rotation.z = Math.sin(h.bobPhase * 0.5) * 0.05;
    } else {
      h.bobPhase += dt * 4;
      h.mesh.position.y = 0.15 + Math.sin(h.bobPhase) * 0.01;
      h.mesh.rotation.z *= 0.9;
    }

    h.earWigglePhase += dt * 3;
    var earWiggle = Math.sin(h.earWigglePhase) * 0.05;
    h.mesh.children[3].rotation.z = earWiggle;
    h.mesh.children[4].rotation.z = -earWiggle;

    pos.x = Math.max(CAGE_BOUNDS.minX, Math.min(CAGE_BOUNDS.maxX, pos.x));
    pos.z = Math.max(CAGE_BOUNDS.minZ, Math.min(CAGE_BOUNDS.maxZ, pos.z));
  }

  // --- ANIMATION ---
  var wheelAngle = 0;
  var clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    var dt = Math.min(clock.getDelta(), 0.05);
    var time = clock.elapsedTime;

    for (var i = 0; i < hamsters.length; i++) {
      updateHamster(hamsters[i], dt, time);
    }

    wheelAngle += dt * 0.5;
    wheel.userData.ring.rotation.z = wheelAngle;
    wheel.userData.spokesGroup.rotation.z = wheelAngle;

    scene.rotation.y = Math.sin(time * 0.1) * 0.01;

    controls.update();
    renderer.render(scene, camera);
  }

  animate();

  // --- RESIZE ---
  window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

})();
</script>
</body>
</html>
```