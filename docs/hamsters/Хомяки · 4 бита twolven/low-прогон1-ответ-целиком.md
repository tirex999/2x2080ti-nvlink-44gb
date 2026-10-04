

# Low-Poly Hamster Playground

Here's the complete single-file project:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Low-Poly Hamster Playground</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; background: #fce4d4; font-family: sans-serif; }
    canvas { display: block; }
    #info {
      position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
      background: rgba(255,255,255,.85); padding: 10px 22px; border-radius: 20px;
      font-size: 14px; color: #7a4a2a; pointer-events: none;
      box-shadow: 0 2px 12px rgba(0,0,0,.08);
    }
  </style>
</head>
<body>
  <div id="info">🐹 Drag to orbit · Hamsters are alive!</div>

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

  // ─── Renderer ───────────────────────────────────────
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);

  // ─── Scene & Camera ─────────────────────────────────
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xffe8d6);
  scene.fog = new THREE.Fog(0xffe8d6, 25, 50);

  const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
  camera.position.set(9, 8, 11);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1.5, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxPolarAngle = Math.PI * 0.48;
  controls.minDistance = 6;
  controls.maxDistance = 22;

  // ─── Lights ─────────────────────────────────────────
  const ambient = new THREE.AmbientLight(0xfff0e0, 0.6);
  scene.add(ambient);

  const sun = new THREE.DirectionalLight(0xfff5e0, 1.2);
  sun.position.set(6, 12, 4);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.left = -8;
  sun.shadow.camera.right = 8;
  sun.shadow.camera.top = 8;
  sun.shadow.camera.bottom = -8;
  scene.add(sun);

  const fill = new THREE.DirectionalLight(0xd0e8ff, 0.3);
  fill.position.set(-4, 6, -3);
  scene.add(fill);

  // ─── Materials helper ─────────────────────────────────
  const mat = (color, opts = {}) => new THREE.MeshStandardMaterial({
    color, roughness: opts.rough ?? 0.8, metalness: opts.metal ?? 0.05,
    flatShading: true, ...opts.extra
  });

  // ─── CAGE ─────────────────────────────────────────────
  const CAGE_W = 9, CAGE_D = 7, CAGE_H = 4.5;

  function buildCage() {
    const g = new THREE.Group();

    // Floor / tray
    const floorGeo = new THREE.BoxGeometry(CAGE_W, 0.5, CAGE_D);
    const floorMat = mat(0xf5deb3);
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.position.y = 0.25;
    floor.receiveShadow = true;
    g.add(floor);

    // Bedding particles (wood shavings look)
    const bedColors = [0xf5deb3, 0xffe4b5, 0xdeb887, 0xfaebd7, 0xf0e0c0];
    const bedCount = 80;
    for (let i = 0; i < bedCount; i++) {
      const s = 0.08 + Math.random() * 0.12;
      const geo = new THREE.IcosahedronGeometry(s, 0);
      const m = mat(bedColors[i % bedColors.length]);
      const p = new THREE.Mesh(geo, m);
      p.position.set(
        (Math.random() - 0.5) * (CAGE_W - 0.6),
        0.52 + Math.random() * 0.04,
        (Math.random() - 0.5) * (CAGE_D - 0.6)
      );
      p.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
      g.add(p);
    }

    // Walls (transparent glass look)
    const wallMat = new THREE.MeshStandardMaterial({
      color: 0xcceeff, transparent: true, opacity: 0.15,
      roughness: 0.1, metalness: 0.3, side: THREE.DoubleSide
    });

    // Back wall
    const bw = new THREE.Mesh(new THREE.PlaneGeometry(CAGE_W, CAGE_H), wallMat);
    bw.position.set(0, CAGE_H / 2 + 0.5, -CAGE_D / 2);
    g.add(bw);

    // Left wall
    const lw = new THREE.Mesh(new THREE.PlaneGeometry(CAGE_D, CAGE_H), wallMat);
    lw.rotation.y = Math.PI / 2;
    lw.position.set(-CAGE_W / 2, CAGE_H / 2 + 0.5, 0);
    g.add(lw);

    // Right wall
    const rw = new THREE.Mesh(new THREE.PlaneGeometry(CAGE_D, CAGE_H), wallMat);
    rw.rotation.y = -Math.PI / 2;
    rw.position.set(CAGE_W / 2, CAGE_H / 2 + 0.5, 0);
    g.add(rw);

    // Wire frame edges
    const edgeGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(CAGE_W, CAGE_H, CAGE_D));
    const edgeMat = new THREE.LineBasicMaterial({ color: 0x8899aa });
    const edges = new THREE.LineSegments(edgeGeo, edgeMat);
    edges.position.y = CAGE_H / 2 + 0.5;
    g.add(edges);

    // Vertical wire bars on front (open side)
    const barMat = new THREE.MeshStandardMaterial({ color: 0x99aabb, roughness: 0.4, metalness: 0.5 });
    const barCount = 10;
    for (let i = 0; i <= barCount; i++) {
      const x = -CAGE_W / 2 + (CAGE_W / barCount) * i;
      const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, CAGE_H, 6), barMat);
      bar.position.set(x, CAGE_H / 2 + 0.5, CAGE_D / 2);
      g.add(bar);
    }

    // Top horizontal bars
    for (let i = 0; i < 3; i++) {
      const z = -CAGE_D / 2 + (CAGE_D / 2) * i;
      const barH = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, CAGE_W, 6), barMat);
      barH.rotation.z = Math.PI / 2;
      barH.position.set(0, CAGE_H + 0.5, z);
      g.add(barH);
    }

    return g;
  }

  const cage = buildCage();
  scene.add(cage);

  // ─── RUNNING WHEEL ──────────────────────────────────────
  const WHEEL_POS = new THREE.Vector3(-2.5, 0.5, -2.2);
  let wheelSpinSpeed = 0;

  function buildWheel() {
    const g = new THREE.Group();
    const wheelR = 1.2;
    const spokeMat = mat(0xcccccc, { metal: 0.3, rough: 0.5 });
    const rimMat = mat(0xdddddd, { metal: 0.4, rough: 0.4 });

    // Rim (torus)
    const rim = new THREE.Mesh(new THREE.TorusGeometry(wheelR, 0.08, 8, 24), rimMat);
    g.add(rim);

    // Spokes
    const spokeCount = 6;
    for (let i = 0; i < spokeCount; i++) {
      const angle = (i / spokeCount) * Math.PI * 2;
      const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, wheelR, 6), spokeMat);
      spoke.position.set(0, 0, 0);
      // Position spoke along the radius
      spoke.position.x = Math.cos(angle) * wheelR * 0.5;
      spoke.position.y = Math.sin(angle) * wheelR * 0.5;
      spoke.rotation.z = angle + Math.PI / 2;
      g.add(spoke);
    }

    // Center hub
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.15, 8), rimMat);
    hub.rotation.x = Math.PI / 2;
    g.add(hub);

    // Stand / axle support
    const standMat = mat(0x8899aa, { metal: 0.4, rough: 0.5 });
    // Two vertical supports
    const supportH = 1.5;
    const standL = new THREE.Mesh(new THREE.BoxGeometry(0.12, supportH, 0.12), standMat);
    standL.position.set(-0.5, supportH / 2, 0);
    g.add(standL);
    const standR = new THREE.Mesh(new THREE.BoxGeometry(0.12, supportH, 0.12), standMat);
    standR.position.set(0.5, supportH / 2, 0);
    g.add(standR);

    // Base
    const base = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.1, 0.8), standMat);
    base.position.y = 0.05;
    g.add(base);

    // Position the wheel group so the wheel center is at the right height
    g.position.copy(WHEEL_POS);
    g.position.y = WHEEL_POS.y + 1.5; // wheel center above the base

    return g;
  }

  const wheelGroup = buildWheel();
  scene.add(wheelGroup);

  // ─── FOOD BOWL ──────────────────────────────────────────
  function buildFoodBowl(pos) {
    const g = new THREE.Group();
    const bowlMat = mat(0xff6688, { rough: 0.5 });
    const foodMat = mat(0xffcc44);

    // Bowl (cylinder)
    const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.4, 0.3, 8), bowlMat);
    bowl.position.y = 0.15;
    bowl.castShadow = true;
    g.add(bowl);

    // Food pellets inside
    for (let i = 0; i < 5; i++) {
      const pellet = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 4), foodMat);
      pellet.position.set(
        (Math.random() - 0.5) * 0.5,
        0.32,
        (Math.random() - 0.5) * 0.5
      );
      g.add(pellet);
    }

    g.position.copy(pos);
    return g;
  }

  const foodBowl = buildFoodBowl(new THREE.Vector3(2.5, 0.5, 1.5));
  scene.add(foodBowl);

  // ─── LOW-POLY HAMSTER ─────────────────────────────────────
  function buildHamster(color = 0xffa54f) {
    const g = new THREE.Group();
    const bodyMat = mat(color);
    const bellyMat = mat(0xffe0b2);
    const earMat = mat(0xffab91);
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.3 });
    const noseMat = mat(0xff8899);

    // Body (squashed sphere)
    const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.6, 1), bodyMat);
    body.scale.set(1.2, 0.8, 1);
    body.position.y = 0.5;
    body.castShadow = true;
    g.add(body);

    // Belly (lighter, slightly forward)
    const belly = new THREE.Mesh(new THREE.IcosahedronGeometry(0.45, 1), bellyMat);
    belly.scale.set(1, 0.7, 0.9);
    belly.position.set(0, 0.42, 0.15);
    g.add(belly);

    // Head
    const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1), bodyMat);
    head.position.set(0, 0.75, 0.45);
    head.castShadow = true;
    g.add(head);

    // Muzzle / snout area
    const muzzle = new THREE.Mesh(new THREE.IcosahedronGeometry(0.2, 1), bellyMat);
    muzzle.position.set(0, 0.65, 0.75);
    g.add(muzzle);

    // Ears
    const earGeo = new THREE.ConeGeometry(0.15, 0.25, 6);
    const earL = new THREE.Mesh(earGeo, earMat);
    earL.position.set(-0.25, 1.1, 0.4);
    earL.rotation.z = 0.3;
    g.add(earL);

    const earR = new THREE.Mesh(earGeo, earMat);
    earR.position.set(0.25, 1.1, 0.4);
    earR.rotation.z = -0.3;
    g.add(earR);

    // Inner ears (pink circles)
    const innerEarGeo = new THREE.CircleGeometry(0.08, 6);
    const innerEarMat = mat(0xff8899);
    const ieL = new THREE.Mesh(innerEarGeo, innerEarMat);
    ieL.position.set(-0.25, 1.08, 0.48);
    ieL.rotation.x = -0.2;
    g.add(ieL);
    const ieR = new THREE.Mesh(innerEarGeo, innerEarMat);
    ieR.position.set(0.25, 1.08, 0.48);
    ieR.rotation.x = -0.2;
    g.add(ieR);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.07, 8, 6);
    const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(-0.18, 0.82, 0.78);
    g.add(eyeL);
    const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
    eyeR.position.set(0.18, 0.82, 0.78);
    g.add(eyeR);

    // Eye highlights (tiny white dots)
    const hlGeo = new THREE.SphereGeometry(0.025, 6, 4);
    const hlMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const hlL = new THREE.Mesh(hlGeo, hlMat);
    hlL.position.set(-0.16, 0.84, 0.82);
    g.add(hlL);
    const hlR = new THREE.Mesh(hlGeo, hlMat);
    hlR.position.set(0.2, 0.84, 0.82);
    g.add(hlR);

    // Nose
    const nose = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 4), noseMat);
    nose.position.set(0, 0.62, 0.88);
    g.add(nose);

    // Whiskers (thin lines)
    const whiskerMat = new THREE.LineBasicMaterial({ color: 0xdddddd });
    for (let side of [-1, 1]) {
      for (let i = 0; i < 3; i++) {
        const pts = [
          new THREE.Vector3(side * 0.1, 0.6 + i * 0.03, 0.85),
          new THREE.Vector3(side * 0.5, 0.55 + i * 0.05, 0.95)
        ];
        const wg = new THREE.BufferGeometry().setFromPoints(pts);
        const wl = new THREE.Line(wg, whiskerMat);
        g.add(wl);
      }
    }

    // Legs (4 tiny stubby cylinders)
    const legGeo = new THREE.CylinderGeometry(0.08, 0.06, 0.25, 6);
    const legPositions = [
      [-0.25, 0.15, 0.35], [0.25, 0.15, 0.35],
      [-0.25, 0.15, -0.3], [0.25, 0.15, -0.3]
    ];
    for (const [lx, ly, lz] of legPositions) {
      const leg = new THREE.Mesh(legGeo, bodyMat);
      leg.position.set(lx, ly, lz);
      g.add(leg);
    }

    // Tiny tail
    const tail = new THREE.Mesh(new THREE.ConeGeometry(0.08, 0.2, 6), bodyMat);
    tail.position.set(0, 0.45, -0.55);
    tail.rotation.x = Math.PI / 2;
    g.add(tail);

    // Cheeks (fluffy hamster cheeks!)
    const cheekMat = mat(0xffcc80);
    const cheekGeo = new THREE.SphereGeometry(0.15, 6, 4);
    const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
    cheekL.position.set(-0.28, 0.6, 0.65);
    cheekL.scale.set(1, 0.8, 0.7);
    g.add(cheekL);
    const cheekR = new THREE.Mesh(cheekGeo, cheekMat);
    cheekR.position.set(0.28, 0.6, 0.65);
    cheekR.scale.set(1, 0.8, 0.7);
    g.add(cheekR);

    return g;
  }

  // ─── INSTANTIATE HAMSTERS ─────────────────────────────────
  const HAMSTER_COLORS = [0xffa54f, 0xffcc80, 0xe8a87c, 0xffb347, 0xd4a574];
  const hamsters = [];
  const hamsterCount = 5;

  for (let i = 0; i < hamsterCount; i++) {
    const h = buildHamster(HAMSTER_COLORS[i % HAMSTER_COLORS.length]);
    
    // Random starting position within the cage
    const startX = (Math.random() - 0.5) * (CAGE_W - 2);
    const startZ = (Math.random() - 0.5) * (CAGE_D - 2);
    h.position.set(startX, 0.5, startZ);
    
    // Random initial facing direction
    const angle = Math.random() * Math.PI * 2;
    h.rotation.y = angle;
    
    scene.add(h);
    
    // AI state
    hamsters.push({
      mesh: h,
      dir: angle,
      speed: 0.008 + Math.random() * 0.008,
      state: 'WALKING',
      stateTimer: 60 + Math.random() * 120,
      targetDir: angle,
      turnSpeed: 0,
      bobPhase: Math.random() * Math.PI * 2,
      bobAmp: 0.03 + Math.random() * 0.02,
      isAtWheel: false,
      wheelBounce: 0
    });
  }

  // ─── SCATTERED FOOD PARTICLES (on the floor) ────────────────
  const foodParticleMat = mat(0xffcc44);
  for (let i = 0; i < 12; i++) {
    const fp = new THREE.Mesh(new THREE.SphereGeometry(0.05, 6, 4), foodParticleMat);
    fp.position.set(
      (Math.random() - 0.5) * (CAGE_W - 1),
      0.56,
      (Math.random() - 0.5) * (CAGE_D - 1)
    );
    scene.add(fp);
  }

  // ─── ANIMATION LOOP ─────────────────────────────────────
  const clock = new THREE.Clock();
  let wheelAngle = 0;

  function updateHamsterAI(dt) {
    const halfW = CAGE_W / 2 - 1;
    const halfD = CAGE_D / 2 - 1;

    for (const h of hamsters) {
      h.stateTimer -= dt * 60;

      // Bob animation (walking bounce)
      h.bobPhase += dt * 8;
      const bobY = Math.sin(h.bobPhase) * h.bobAmp;
      
      if (h.state === 'WALKING') {
        // Move forward
        h.mesh.position.x += Math.sin(h.dir) * h.speed;
        h.mesh.position.z += Math.cos(h.dir) * h.speed;

        // Boundary check – turn around if hitting a wall
        if (Math.abs(h.mesh.position.x) > halfW || Math.abs(h.mesh.position.z) > halfD) {
          h.dir += Math.PI * (0.7 + Math.random() * 0.6);
          h.state = 'TURNING';
          h.stateTimer = 30 + Math.random() * 30;
        }

        // Random events
        if (h.stateTimer <= 0) {
          const r = Math.random();
          if (r < 0.3) {
            h.state = 'PAUSED';
            h.stateTimer = 40 + Math.random() * 80;
          } else if (r < 0.6) {
            h.state = 'TURNING';
            h.stateTimer = 25 + Math.random() * 25;
            h.targetDir = h.dir + (Math.random() - 0.5) * Math.PI;
          } else {
            // Go to the wheel!
            h.state = 'AT_WHEEL';
            h.stateTimer = 200 + Math.random() * 100;
          }
        }
      }

      else if (h.state === 'PAUSED') {
        // Just stand still (maybe a little wiggle)
        if (h.stateTimer <= 0) {
          h.state = 'WALKING';
          h.stateTimer = 80 + Math.random() * 100;
        }
      }

      else if (h.state === 'TURNING') {
        // Rotate toward target direction
        let diff = h.targetDir - h.dir;
        // Normalize to [-PI, PI]
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;

        const turnAmount = 0.04;
        if (Math.abs(diff) < turnAmount) {
          h.dir = h.targetDir;
          h.state = 'WALKING';
          h.stateTimer = 60 + Math.random() * 100;
        } else {
          h.dir += Math.sign(diff) * turnAmount;
        }
        h.mesh.rotation.y = h.dir;
      }

      else if (h.state === 'AT_WHEEL') {
        // Move toward the wheel
        const wp = WHEEL_POS;
        const dx = wp.x - h.mesh.position.x;
        const dz = wp.z - h.mesh.position.z;
        const dist = Math.sqrt(dx * dx + dz * dz);

        if (dist > 1.2) {
          // Walk toward wheel
          const targetAngle = Math.atan2(dx, dz);
          let diff = targetAngle - h.dir;
          while (diff > Math.PI) diff -= Math.PI * 2;
          while (diff < -Math.PI) diff += Math.PI * 2;
          h.dir += Math.sign(diff) * 0.05;
          h.mesh.rotation.y = h.dir;
          
          h.mesh.position.x += Math.sin(h.dir) * h.speed * 1.5;
          h.mesh.position.z += Math.cos(h.dir) * h.speed * 1.5;
        } else {
          // At the wheel – "running" animation
          h.isAtWheel = true;
          h.wheelBounce = Math.sin(clock.elapsedTime * 12) * 0.08;
          wheelSpinSpeed = 3;

          // Face the wheel
          h.dir = Math.atan2(wp.x - h.mesh.position.x, wp.z - h.mesh.position.z);
          h.mesh.rotation.y = h.dir;
        }

        if (h.stateTimer <= 0) {
          h.state = 'WALKING';
          h.stateTimer = 80 + Math.random() * 80;
          h.isAtWheel = false;
          h.wheelBounce = 0;
        }
      }

      // Apply rotation
      h.mesh.rotation.y = h.dir;

      // Apply bob
      h.mesh.position.y = 0.5 + bobY + h.wheelBounce;
    }
  }

  // ─── MAIN RENDER LOOP ─────────────────────────────────────
  function animate() {
    requestAnimationFrame(animate);

    const dt = clock.getDelta();

    // Update hamster AI
    updateHamsterAI(dt);

    // Wheel spin
    if (wheelSpinSpeed > 0.1) {
      wheelAngle += wheelSpinSpeed * dt;
      wheelGroup.children[0].rotation.z = wheelAngle; // rim
      // Also rotate spokes
      for (let i = 1; i < 7; i++) {
        if (wheelGroup.children[i]) {
          wheelGroup.children[i].rotation.z += wheelSpinSpeed * dt;
        }
      }
    } else {
      // Slow decay
      wheelSpinSpeed *= 0.98;
    }

    // Gentle scene breathing (optional subtle camera drift)
    controls.update();

    renderer.render(scene, camera);
  }

  // ─── RESIZE HANDLER ─────────────────────────────────────
  window.addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });

  // Start!
  animate();

  </script>
</body>
</html>
```

## What's included

| Element | Details |
|---|---|
| **Cage** | Glass-style transparent walls, wire-bar front, edge outlines |
| **Floor / tray** | Box geometry + 80 scattered "wood shaving" particles in warm tones |
| **Running wheel** | Torus rim, 6 spokes, hub, two-post stand — **spins when a hamster reaches it** |
| **Food bowl** | Pink cylinder with 5 yellow pellet spheres inside |
| **5 hamsters** | Icosahedron body + head, cone ears, sphere eyes with highlights, pink nose, whisker lines, stubby legs, fluffy cheeks, tiny tail |

## Hamster AI states

- **WALKING** → moves forward, bobs up/down, hits a wall → turns
- **PAUSED** → stands still for a random duration
- **TURNING** → smoothly rotates toward a new heading
- **AT_WHEEL** → walks toward the wheel, then "runs" in place (fast bob + wheel spins) before resuming normal wandering

## How to run

Save the code as `index.html` and open it in any modern browser (Chrome, Firefox, Safari, Edge). No build step, no server needed — just double-click the file.

**Drag** to orbit the camera. Watch the hamsters wander, pause, turn, and occasionally head to the wheel. 🐹