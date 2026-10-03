Save the following as **`index.html`** and open it in a modern browser. It uses Three.js from a CDN and runs immediately.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Low-Poly Hamster Playground</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: #ffe3f0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    canvas {
      display: block;
      width: 100%;
      height: 100%;
      touch-action: none;
    }

    #ui {
      position: fixed;
      top: 14px;
      left: 14px;
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.72);
      border-radius: 16px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
      pointer-events: none;
      max-width: min(330px, calc(100vw - 28px));
    }

    #ui h1 {
      margin: 0 0 5px;
      font-size: 18px;
      color: #6b3b55;
    }

    #ui p {
      margin: 0;
      font-size: 13px;
      line-height: 1.45;
      color: #7a4f63;
    }

    .kbd {
      display: inline-block;
      border-radius: 6px;
      background: #ffe3f0;
      padding: 1px 6px;
      font-weight: 600;
      color: #6b3b55;
    }
  </style>
</head>
<body>
  <div id="ui">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <p>
      <span class="kbd">Drag</span> to rotate •
      <span class="kbd">Scroll / pinch</span> to zoom.<br>
      The hamsters wander, pause, spin, run on the wheel, and snack from the bowl.
    </p>
  </div>

  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
      }
    }
  </script>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const canvas = document.createElement('canvas');
    document.body.appendChild(canvas);

    function addShadow(mesh) {
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      return mesh;
    }

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#ffe3f0');
    scene.fog = new THREE.Fog('#ffe3f0', 18, 42);

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    );
    camera.position.set(7.5, 6.2, 8.5);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 1.2, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enablePan = false;
    controls.minDistance = 4;
    controls.maxDistance = 22;
    controls.maxPolarAngle = Math.PI * 0.49;

    scene.add(new THREE.AmbientLight(0xffffff, 0.65));

    const hemi = new THREE.HemisphereLight(0xfff0f8, 0x9fd0ff, 0.45);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff4e6, 1.15);
    sun.position.set(6, 10, 4);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.camera.near = 1;
    sun.shadow.camera.far = 30;
    sun.shadow.camera.left = -10;
    sun.shadow.camera.right = 10;
    sun.shadow.camera.top = 10;
    sun.shadow.camera.bottom = -10;
    scene.add(sun);

    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(60, 60),
      new THREE.MeshStandardMaterial({
        color: '#ffe3f0',
        roughness: 1,
        flatShading: true
      })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.21;
    ground.receiveShadow = true;
    scene.add(ground);

    const obstacles = [
      { x: 3.15, z: 0, r: 0.85 },
      { x: -2.3, z: 1.6, r: 0.55 },
      { x: 0, z: -2.3, r: 0.45 }
    ];

    function isBlocked(x, z, margin) {
      for (const o of obstacles) {
        const dx = x - o.x;
        const dz = z - o.z;
        if (Math.hypot(dx, dz) < o.r + margin) return true;
      }
      return false;
    }

    const cage = new THREE.Group();
    scene.add(cage);

    const tray = new THREE.Mesh(
      new THREE.CylinderGeometry(5.6, 5.8, 0.4, 16),
      new THREE.MeshStandardMaterial({
        color: '#f6e2c7',
        flatShading: true,
        roughness: 0.95
      })
    );
    tray.position.y = -0.2;
    tray.receiveShadow = true;
    cage.add(tray);

    const barMat = new THREE.MeshStandardMaterial({
      color: '#7fb2ff',
      flatShading: true,
      roughness: 0.55,
      metalness: 0.15
    });

    const barGeo = new THREE.CylinderGeometry(0.06, 0.06, 3, 6);
    for (let i = 0; i < 24; i++) {
      const a = (i / 24) * Math.PI * 2;
      const bar = new THREE.Mesh(barGeo, barMat);
      bar.position.set(Math.cos(a) * 5.2, 1.5, Math.sin(a) * 5.2);
      addShadow(bar);
      cage.add(bar);
    }

    const ringGeoTop = new THREE.TorusGeometry(5.2, 0.08, 6, 24);
    ringGeoTop.rotateX(Math.PI / 2);

    const topRing = new THREE.Mesh(ringGeoTop, barMat);
    topRing.position.y = 3;
    addShadow(topRing);
    cage.add(topRing);

    const bottomRing = new THREE.Mesh(ringGeoTop.clone(), barMat);
    bottomRing.position.y = 0.03;
    addShadow(bottomRing);
    cage.add(bottomRing);

    const beddingPalette = [
      '#fff1c7',
      '#ffe0b2',
      '#d8f3dc',
      '#e0c3fc',
      '#ffd6e8'
    ];

    for (let i = 0; i < 32; i++) {
      let x = 0, z = 0, tries = 0;
      do {
        const r = Math.sqrt(Math.random()) * 4.75;
        const a = Math.random() * Math.PI * 2;
        x = Math.cos(a) * r;
        z = Math.sin(a) * r;
        tries++;
      } while (isBlocked(x, z, 0.6) && tries < 25);

      const size = 0.12 + Math.random() * 0.22;
      const mat = new THREE.MeshStandardMaterial({
        color: beddingPalette[i % beddingPalette.length],
        flatShading: true,
        roughness: 1
      });

      const bed = new THREE.Mesh(new THREE.IcosahedronGeometry(size, 0), mat);
      bed.position.set(x, size * 0.75, z);
      bed.rotation.y = Math.random() * Math.PI;
      addShadow(bed);
      cage.add(bed);
    }

    const wheelGroup = new THREE.Group();
    wheelGroup.position.set(3.15, 1.25, 0);
    scene.add(wheelGroup);

    const frameMat = new THREE.MeshStandardMaterial({
      color: '#ff9ec7',
      flatShading: true,
      roughness: 0.6,
      metalness: 0.1
    });

    const ringGeo = new THREE.TorusGeometry(1.15, 0.08, 6, 16);

    const ringFront = new THREE.Mesh(ringGeo, frameMat);
    ringFront.position.z = 0.26;
    addShadow(ringFront);
    wheelGroup.add(ringFront);

    const ringBack = ringFront.clone();
    ringBack.position.z = -0.26;
    wheelGroup.add(ringBack);

    const axleGeo = new THREE.CylinderGeometry(0.07, 0.07, 0.8, 6);
    axleGeo.rotateX(Math.PI / 2);
    const axle = new THREE.Mesh(axleGeo, frameMat);
    addShadow(axle);
    wheelGroup.add(axle);

    const wheelSpin = new THREE.Group();
    wheelGroup.add(wheelSpin);

    const discGeo = new THREE.CylinderGeometry(1.0, 1.0, 0.28, 12);
    discGeo.rotateX(Math.PI / 2);

    const disc = new THREE.Mesh(
      discGeo,
      new THREE.MeshStandardMaterial({
        color: '#fff3b0',
        flatShading: true,
        roughness: 0.7
      })
    );
    addShadow(disc);
    wheelSpin.add(disc);

    for (let i = 0; i < 4; i++) {
      const spokeGeo = new THREE.BoxGeometry(2.0, 0.09, 0.09);
      const spoke = new THREE.Mesh(spokeGeo, frameMat);
      spoke.rotation.z = i * Math.PI / 4;
      addShadow(spoke);
      wheelSpin.add(spoke);
    }

    const postGeo = new THREE.BoxGeometry(0.12, 1.25, 0.12);
    for (let s = -1; s <= 1; s += 2) {
      const post = new THREE.Mesh(postGeo, frameMat);
      post.position.set(0, -0.625, s * 0.3);
      addShadow(post);
      wheelGroup.add(post);
    }

    const bowlGroup = new THREE.Group();
    bowlGroup.position.set(-2.3, 0, 1.6);
    scene.add(bowlGroup);

    const bowl = new THREE.Mesh(
      new THREE.CylinderGeometry(0.7, 0.48, 0.35, 8),
      new THREE.MeshStandardMaterial({
        color: '#ff8fa3',
        flatShading: true,
        roughness: 0.7
      })
    );
    bowl.position.y = 0.175;
    addShadow(bowl);
    bowlGroup.add(bowl);

    const rimGeo = new THREE.TorusGeometry(0.69, 0.06, 5, 12);
    rimGeo.rotateX(Math.PI / 2);

    const rim = new THREE.Mesh(
      rimGeo,
      new THREE.MeshStandardMaterial({
        color: '#ff6b8b',
        flatShading: true
      })
    );
    rim.position.y = 0.35;
    addShadow(rim);
    bowlGroup.add(rim);

    const pellets = [];
    const pelletMat = new THREE.MeshStandardMaterial({
      color: '#c98f4a',
      flatShading: true,
      roughness: 0.8
    });

    for (let i = 0; i < 7; i++) {
      const pellet = new THREE.Mesh(new THREE.IcosahedronGeometry(0.12, 1), pelletMat);
      const a = Math.random() * Math.PI * 2;
      const r = Math.random() * 0.35;
      pellet.position.set(Math.cos(a) * r, 0.4, Math.sin(a) * r);
      addShadow(pellet);
      bowlGroup.add(pellet);
      pellets.push(pellet);
    }

    const toy = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.42, 1),
      new THREE.MeshStandardMaterial({
        color: '#9fe8ff',
        flatShading: true,
        roughness: 0.6
      })
    );
    toy.position.set(0, 0.35, -2.3);
    addShadow(toy);
    scene.add(toy);

    const interactives = [
      { target: { x: 1.8, z: 0 }, type: 'wheel' },
      { target: { x: -1.7, z: 2.1 }, type: 'eat' }
    ];

    function makeHamster(bodyColor, accentColor) {
      const g = new THREE.Group();

      const bodyMat = new THREE.MeshStandardMaterial({
        color: bodyColor,
        flatShading: true,
        roughness: 0.85
      });

      const accentMat = new THREE.MeshStandardMaterial({
        color: accentColor,
        flatShading: true,
        roughness: 0.8
      });

      const legMat = new THREE.MeshStandardMaterial({
        color: '#7a5142',
        flatShading: true,
        roughness: 0.9
      });

      const darkMat = new THREE.MeshStandardMaterial({
        color: '#3b2b2b',
        flatShading: true,
        roughness: 0.6
      });

      const noseMat = new THREE.MeshStandardMaterial({
        color: '#ff8fa3',
        flatShading: true
      });

      const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 1), bodyMat);
      body.scale.set(1.18, 0.85, 1.45);
      body.position.y = 0.52;
      addShadow(body);
      g.add(body);

      const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1), bodyMat);
      head.scale.set(1.05, 1, 1.1);
      head.position.set(0, 0.63, 0.78);
      addShadow(head);
      g.add(head);

      const earGeo = new THREE.ConeGeometry(0.17, 0.24, 4);
      for (let s = -1; s <= 1; s += 2) {
        const ear = new THREE.Mesh(earGeo, accentMat);
        ear.position.set(s * 0.25, 0.95, 0.58);
        ear.rotation.z = -s * 0.35;
        ear.rotation.x = -0.15;
        addShadow(ear);
        g.add(ear);
      }

      const eyeGeo = new THREE.IcosahedronGeometry(0.07, 1);
      for (let s = -1; s <= 1; s += 2) {
        const eye = new THREE.Mesh(eyeGeo, darkMat);
        eye.position.set(s * 0.17, 0.68, 1.15);
        addShadow(eye);
        g.add(eye);
      }

      const nose = new THREE.Mesh(new THREE.IcosahedronGeometry(0.07, 1), noseMat);
      nose.position.set(0, 0.54, 1.22);
      addShadow(nose);
      g.add(nose);

      const cheekGeo = new THREE.IcosahedronGeometry(0.15, 1);
      for (let s = -1; s <= 1; s += 2) {
        const cheek = new THREE.Mesh(cheekGeo, bodyMat);
        cheek.scale.set(1, 0.8, 1);
        cheek.position.set(s * 0.24, 0.52, 0.95);
        addShadow(cheek);
        g.add(cheek);
      }

      const tail = new THREE.Mesh(new THREE.IcosahedronGeometry(0.11, 1), bodyMat);
      tail.position.set(0, 0.45, -0.78);
      addShadow(tail);
      g.add(tail);

      const legGeo = new THREE.BoxGeometry(0.12, 0.22, 0.12);
      const legs = [];

      for (let sx = -1; sx <= 1; sx += 2) {
        for (let sz = -1; sz <= 1; sz += 2) {
          const pivot = new THREE.Group();
          pivot.position.set(sx * 0.25, 0.22, sz * 0.48);

          const leg = new THREE.Mesh(legGeo, legMat);
          leg.position.y = -0.11;
          addShadow(leg);

          pivot.add(leg);
          g.add(pivot);
          legs.push(pivot);
        }
      }

      g.scale.setScalar(0.85);

      return {
        group: g,
        head,
        legs,
        speed: 0.7 + Math.random() * 0.55,
        heading: Math.random() * Math.PI * 2,
        state: 'idle',
        stateTimer: 1 + Math.random() * 2,
        turnTimer: 1,
        walkPhase: Math.random() * 10,
        phase: Math.random() * Math.PI * 2,
        spinDir: 1,
        target: null,
        interactType: null
      };
    }

    const hamsters = [];
    const bodyColors = ['#ffd7b8', '#f8c6a9', '#e2c3ff', '#bfe8ff', '#fff2a8'];
    const accentColors = ['#ffb7c5', '#ff9aa8', '#d1a6ff', '#9fd0ff', '#ffd479'];

    for (let i = 0; i < 5; i++) {
      const h = makeHamster(bodyColors[i % bodyColors.length], accentColors[i % accentColors.length]);

      let x = 0, z = 0, tries = 0;
      do {
        const r = Math.sqrt(Math.random()) * 3.2;
        const a = Math.random() * Math.PI * 2;
        x = Math.cos(a) * r;
        z = Math.sin(a) * r;
        tries++;
      } while (isBlocked(x, z, 1.0) && tries < 30);

      h.group.position.set(x, 0, z);
      h.heading = Math.atan2(-x, -z) + (Math.random() - 0.5) * 1.2;
      h.group.rotation.y = h.heading;

      scene.add(h.group);
      hamsters.push(h);
    }

    const maxRadius = 4.15;

    function angleLerp(a, b, t) {
      let d = b - a;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      return a + d * Math.min(1, t);
    }

    function moveForward(h, dist) {
      h.group.position.x += Math.sin(h.heading) * dist;
      h.group.position.z += Math.cos(h.heading) * dist;
    }

    function avoidObstacles(h) {
      const pos = h.group.position;

      for (const o of obstacles) {
        const dx = pos.x - o.x;
        const dz = pos.z - o.z;
        const d = Math.hypot(dx, dz);
        const min = o.r + 0.45;

        if (d < min) {
          if (d < 1e-4) {
            h.heading += (Math.random() - 0.5) * 2;
          } else {
            h.heading = Math.atan2(dx, dz) + (Math.random() - 0.5) * 0.6;
            pos.x = o.x + (dx / d) * min;
            pos.z = o.z + (dz / d) * min;
          }
        }
      }
    }

    function chooseNextAction(h) {
      const roll = Math.random();

      if (roll < 0.22) {
        const obj = interactives[Math.floor(Math.random() * interactives.length)];
        h.state = 'approach';
        h.target = obj.target;
        h.interactType = obj.type;
        h.stateTimer = 7 + Math.random() * 5;
      } else if (roll < 0.72) {
        h.state = 'walk';
        h.stateTimer = 2.5 + Math.random() * 3.5;
        h.turnTimer = 0.8 + Math.random() * 1.6;
      } else if (roll < 0.84) {
        h.state = 'spin';
        h.stateTimer = 0.7 + Math.random() * 1.2;
        h.spinDir = Math.random() < 0.5 ? -1 : 1;
      } else {
        h.state = 'pause';
        h.stateTimer = 1.2 + Math.random() * 2.2;
      }
    }

    let elapsed = 0;
    let wheelBoostCount = 0;
    let eatBoostCount = 0;
    let wheelAngularVelocity = 0.4;

    function updateHamster(h, dt) {
      const pos = h.group.position;

      if (h.stateTimer > 0) h.stateTimer -= dt;

      let desiredHead = 0;
      let desiredY = 0;
      let moving = false;

      switch (h.state) {
        case 'idle':
          h.heading += Math.sin(elapsed * 2 + h.phase) * dt * 0.35;
          if (h.stateTimer <= 0) chooseNextAction(h);
          break;

        case 'pause':
          if (h.stateTimer <= 0) chooseNextAction(h);
          break;

        case 'spin':
          h.heading += dt * 2.2 * h.spinDir;
          if (h.stateTimer <= 0) chooseNextAction(h);
          break;

        case 'walk':
          moving = true;
          h.turnTimer -= dt;

          if (h.turnTimer <= 0) {
            h.heading += (Math.random() - 0.5) * 1.4;
            h.turnTimer = 0.8 + Math.random() * 1.8;
          }

          moveForward(h, h.speed * dt);
          desiredY = Math.abs(Math.sin(h.walkPhase)) * 0.03;

          if (h.stateTimer <= 0) chooseNextAction(h);
          break;

        case 'approach':
          moving = true;

          const desired = Math.atan2(h.target.x - pos.x, h.target.z - pos.z);
          h.heading = angleLerp(h.heading, desired, dt * 3.5);

          moveForward(h, h.speed * 1.25 * dt);
          desiredY = Math.abs(Math.sin(h.walkPhase)) * 0.03;

          if (
            Math.hypot(pos.x - h.target.x, pos.z - h.target.z) < 0.75 ||
            h.stateTimer <= 0
          ) {
            h.state = h.interactType;
            h.stateTimer =
              h.interactType === 'wheel'
                ? 2 + Math.random() * 2.5
                : 1.5 + Math.random() * 2;
          }
          break;

        case 'wheel':
          wheelBoostCount++;
          desiredY = Math.abs(Math.sin(elapsed * 10 + h.phase)) * 0.14;
          if (h.stateTimer <= 0) chooseNextAction(h);
          break;

        case 'eat':
          eatBoostCount++;
          desiredHead = Math.sin(elapsed * 12 + h.phase) * 0.35;
          desiredY = Math.abs(Math.sin(elapsed * 12 + h.phase)) * 0.04;
          if (h.stateTimer <= 0) chooseNextAction(h);
          break;
      }

      h.group.rotation.y = angleLerp(
        h.group.rotation.y,
        h.heading,
        Math.min(1, dt * 8)
      );

      if (moving) {
        h.walkPhase += dt * (7 + h.speed * 4);
      } else {
        h.walkPhase += dt * 1.5;
      }

      if (h.state === 'walk' || h.state === 'approach') {
        avoidObstacles(h);
      }

      const r = Math.hypot(pos.x, pos.z);
      if (r > maxRadius) {
        pos.x *= maxRadius / r;
        pos.z *= maxRadius / r;
        h.heading = Math.atan2(-pos.x, -pos.z) + (Math.random() - 0.5) * 0.5;
      }

      for (let i = 0; i < h.legs.length; i++) {
        const target = moving
          ? Math.sin(h.walkPhase + i * Math.PI / 2) * 0.65
          : 0;

        h.legs[i].rotation.x +=
          (target - h.legs[i].rotation.x) * Math.min(1, dt * 8);
      }

      h.head.rotation.x += (desiredHead - h.head.rotation.x) * Math.min(1, dt * 8);
      pos.y += (desiredY - pos.y) * Math.min(1, dt * 8);
    }

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const dt = Math.min(clock.getDelta(), 0.05);
      elapsed += dt;

      wheelBoostCount = 0;
      eatBoostCount = 0;

      for (const h of hamsters) {
        updateHamster(h, dt);
      }

      const targetWheelSpeed = 0.35 + wheelBoostCount * 4.2;
      wheelAngularVelocity +=
        (targetWheelSpeed - wheelAngularVelocity) * Math.min(1, dt * 4);

      wheelSpin.rotation.z += wheelAngularVelocity * dt;

      for (let i = 0; i < pellets.length; i++) {
        const s =
          eatBoostCount > 0
            ? 1 + Math.sin(elapsed * 8 + i) * 0.15
            : 1 + Math.sin(elapsed * 0.7 + i) * 0.03;

        pellets[i].scale.setScalar(s);
      }

      toy.rotation.y += dt * 0.4;

      controls.update();
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