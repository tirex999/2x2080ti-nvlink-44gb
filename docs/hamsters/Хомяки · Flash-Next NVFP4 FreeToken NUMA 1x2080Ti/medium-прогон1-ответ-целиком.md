

# Low-Poly Hamster Playground 🐹

A complete single-file project. Save as `index.html` and open in any modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #bfe3ff; }
  canvas { display: block; }
  #ui {
    position: fixed; top: 14px; left: 16px; font-family: "Comic Sans MS", "Segoe UI", sans-serif;
    color: #5a3d2b; pointer-events: none; user-select: none;
  }
  #ui h1 { margin: 0; font-size: 22px; text-shadow: 0 2px 0 rgba(255,255,255,.6); }
  #ui p  { margin: 4px 0 0; font-size: 13px; opacity: .85; }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>drag to rotate &nbsp;•&nbsp; scroll to zoom &nbsp;•&nbsp; click the wheel to spin it!</p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  "use strict";

  // ---------- Basics ----------
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe3ff);
  scene.fog = new THREE.Fog(0xbfe3ff, 25, 60);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);

  const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
  const target = new THREE.Vector3(0, 1.6, 0);

  // Lights
  scene.add(new THREE.HemisphereLight(0xfff4e0, 0x8fbf6f, 0.75));
  const sun = new THREE.DirectionalLight(0xfff0d0, 0.9);
  sun.position.set(8, 14, 6);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -10; sun.shadow.camera.right = 10;
  sun.shadow.camera.top = 10;  sun.shadow.camera.bottom = -10;
  scene.add(sun);

  // ---------- Helpers ----------
  const mat = (color, rough = 0.9) =>
    new THREE.MeshStandardMaterial({ color, roughness: rough, flatShading: true });
  const rnd = (a, b) => a + Math.random() * (b - a);

  function mesh(geo, material, x = 0, y = 0, z = 0, parent = scene) {
    const m = new THREE.Mesh(geo, material);
    m.position.set(x, y, z);
    m.castShadow = m.receiveShadow = true;
    parent.add(m);
    return m;
  }

  // ---------- World ----------
  const FLOOR_Y = 0.5;          // top of the tray
  const CAGE_R  = 6.2;

  // Grass ground
  const ground = mesh(new THREE.CircleGeometry(40, 24), mat(0x9ed36a), 0, 0, 0);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true; ground.castShadow = false;

  // Tray
  mesh(new THREE.CylinderGeometry(6.8, 6.5, 0.5, 20), mat(0xf3a6b8), 0, 0.25, 0);
  // Bedding
  const bedding = mesh(new THREE.CylinderGeometry(6.2, 6.2, 0.1, 20), mat(0xf0dcae), 0, FLOOR_Y - 0.03, 0);

  // Cage bars + rings
  const barMat = mat(0x8fd6e8, 0.6);
  const cage = new THREE.Group(); scene.add(cage);
  for (let i = 0; i < 26; i++) {
    const a = (i / 26) * Math.PI * 2;
    mesh(new THREE.CylinderGeometry(0.07, 0.07, 3.4, 5), barMat,
      Math.cos(a) * CAGE_R, FLOOR_Y + 1.7, Math.sin(a) * CAGE_R, cage);
  }
  [FLOOR_Y + 3.35, FLOOR_Y + 1.8].forEach(y => {
    const ring = mesh(new THREE.TorusGeometry(CAGE_R, 0.09, 5, 40), barMat, 0, y, 0, cage);
    ring.rotation.x = Math.PI / 2;
  });
  // Cute little roof ring
  const roofRing = mesh(new THREE.TorusGeometry(1.4, 0.1, 5, 20), barMat, 0, FLOOR_Y + 4.0, 0, cage);
  roofRing.rotation.x = Math.PI / 2;
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    const spoke = mesh(new THREE.CylinderGeometry(0.06, 0.06, 5.2, 4), barMat, 0, 0, 0, cage);
    spoke.position.set(Math.cos(a) * 0.7, FLOOR_Y + 3.7, Math.sin(a) * 0.7);
    spoke.lookAt(0, FLOOR_Y + 4.0, 0);
    spoke.rotateX(Math.PI / 2);
  }

  // ---------- Exercise wheel (interactive) ----------
  const wheelRoot = new THREE.Group();
  wheelRoot.position.set(4, FLOOR_Y, 0);
  scene.add(wheelRoot);

  // Stand
  [-0.5, 0.5].forEach(z => {
    const leg = mesh(new THREE.BoxGeometry(0.18, 1.9, 0.18), mat(0xc98a5b), 0.1, 0.95, z, wheelRoot);
    leg.rotation.z = -0.12;
  });

  const wheelRun = new THREE.Group();       // this part spins
  wheelRun.position.set(0, 1.65, 0);
  wheelRun.rotation.y = Math.PI / 2;        // spin around world X
  wheelRoot.add(wheelRun);

  const wheelMat = mat(0xffd166, 0.6);
  const tire = mesh(new THREE.TorusGeometry(1.5, 0.14, 6, 18), wheelMat, 0, 0, 0, wheelRun);
  const hub = mesh(new THREE.CylinderGeometry(0.12, 0.12, 1.1, 8), mat(0xc98a5b), 0, 0, 0, wheelRun);
  hub.rotation.z = Math.PI / 2;
  for (let i = 0; i < 6; i++) {
    const sp = mesh(new THREE.BoxGeometry(0.05, 0.05, 2.9), wheelMat, 0, 0, 0, wheelRun);
    sp.rotation.y = (i / 6) * Math.PI;
  }
  // Running platform (back disc)
  const disc = mesh(new THREE.CylinderGeometry(1.38, 1.38, 0.1, 16), mat(0xe8a94b), 0, 0.25, 0, wheelRun);
  disc.rotation.x = Math.PI / 2;
  // Grip rungs
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    mesh(new THREE.BoxGeometry(0.5, 0.07, 0.07), wheelMat,
      0, Math.sin(a) * 1.15, Math.cos(a) * 1.15, wheelRun);
  }

  let wheelVel = 0, wheelAngle = 0;

  // ---------- Food bowl ----------
  const BOWL = new THREE.Vector3(-3.2, FLOOR_Y, 2.4);
  const bowlG = new THREE.Group(); bowlG.position.copy(BOWL); scene.add(bowlG);
  mesh(new THREE.CylinderGeometry(0.75, 0.5, 0.42, 10), mat(0x7ec8e3), 0, 0.21, 0, bowlG);
  mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.1, 10), mat(0x5aa9c9), 0, 0.36, 0, bowlG);
  for (let i = 0; i < 7; i++) {
    const a = rnd(0, Math.PI * 2), r = rnd(0, 0.35);
    mesh(new THREE.IcosahedronGeometry(0.13, 0), mat(0xd98c4f),
      Math.cos(a) * r, 0.45, Math.sin(a) * r, bowlG);
  }

  // ---------- Tunnel ----------
  const tunnel = mesh(new THREE.CylinderGeometry(0.75, 0.75, 2.8, 10, 1, true), mat(0xb39ddb), -2.4, FLOOR_Y + 0.72, -2.6);
  tunnel.rotation.x = Math.PI / 2;
  const tunnelCap = mesh(new THREE.TorusGeometry(0.75, 0.09, 5, 14), mat(0x8e6cc9), -2.4, FLOOR_Y + 0.72, -1.2);

  // ---------- Wooden blocks toy ----------
  const blockColors = [0xff8fa3, 0x8fd6e8, 0xffd166];
  blockColors.forEach((c, i) => {
    const b = mesh(new THREE.BoxGeometry(0.7, 0.7, 0.7), mat(c), 1.2 + i * 0.15, FLOOR_Y + 0.35 + i * 0.68, -3.2);
    b.rotation.y = rnd(-0.3, 0.3);
  });

  // ---------- Hamsters ----------
  function buildHamster(colorHex) {
    const g = new THREE.Group();
    const body = mat(colorHex);
    const cream = mat(0xfff4e0);

    const torso = mesh(new THREE.SphereGeometry(0.46, 6, 4), body, 0, 0.5, 0, g);
    torso.scale.set(1.05, 0.9, 1.3);
    mesh(new THREE.SphereGeometry(0.3, 6, 4), body, 0, 0.62, 0.42, g);          // head
    mesh(new THREE.SphereGeometry(0.09, 5, 3), cream, 0.2, 0.55, 0.5, g);       // cheeks
    mesh(new THREE.SphereGeometry(0.09, 5, 3), cream, -0.2, 0.55, 0.5, g);
    mesh(new THREE.SphereGeometry(0.11, 5, 3), body, 0.18, 0.86, 0.36, g);      // ears
    mesh(new THREE.SphereGeometry(0.11, 5, 3), body, -0.18, 0.86, 0.36, g);
    mesh(new THREE.SphereGeometry(0.05, 5, 3), body, 0.18, 0.86, 0.34, g).material = mat(0xf5b7c4);
    mesh(new THREE.SphereGeometry(0.05, 5, 3), body, -0.18, 0.86, 0.34, g).material = mat(0xf5b7c4);
    const eyeM = mat(0x222222, 0.3);
    mesh(new THREE.SphereGeometry(0.045, 5, 3), eyeM, 0.13, 0.66, 0.64, g);     // eyes
    mesh(new THREE.SphereGeometry(0.045, 5, 3), eyeM, -0.13, 0.66, 0.64, g);
    mesh(new THREE.SphereGeometry(0.05, 5, 3), mat(0xf5879e), 0, 0.58, 0.71, g);// nose
    mesh(new THREE.SphereGeometry(0.07, 5, 3), body, 0, 0.5, -0.62, g);         // tail nub

    const legs = [];
    [[0.22, 0.32], [-0.22, 0.32], [0.22, -0.32], [-0.22, -0.32]].forEach(([x, z]) => {
      legs.push(mesh(new THREE.BoxGeometry(0.13, 0.24, 0.13), body, x, 0.12, z, g));
    });

    g.scale.setScalar(0.85);
    scene.add(g);
    return { group: g, legs, head: g.children[2] };
  }

  class Hamster {
    constructor(color, x, z) {
      const parts = buildHamster(color);
      this.g = parts.group; this.legs = parts.legs; this.head = parts.head;
      this.g.position.set(x, FLOOR_Y, z);
      this.state = "idle";
      this.timer = rnd(0, 2);
      this.heading = rnd(0, Math.PI * 2);
      this.speed = rnd(1.1, 1.7);
      this.phase = 0;
      this.target = new THREE.Vector3();
    }

    pickWanderTarget() {
      const a = rnd(0, Math.PI * 2), r = rnd(1, 5);
      this.target.set(Math.cos(a) * r, FLOOR_Y, Math.sin(a) * r);
    }

    faceTowards(p, dt) {
      const want = Math.atan2(p.x - this.g.position.x, p.z - this.g.position.z);
      let d = want - this.heading;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      this.heading += THREE.MathUtils.clamp(d, -4 * dt, 4 * dt);
      return Math.abs(d) < 0.15;
    }

    walkStep(dt) {
      const arrived = this.faceTowards(this.target, dt);
      if (arrived) {
        const d = this.g.position.distanceTo(this.target);
        if (d < 0.25) return true;
      }
      this.g.position.x += Math.sin(this.heading) * this.speed * dt;
      this.g.position.z += Math.cos(this.heading) * this.speed * dt;
      this.phase += dt * 12;
      this.g.position.y = FLOOR_Y + Math.abs(Math.sin(this.phase)) * 0.07; // hoppy waddle
      this.legs.forEach((l, i) => l.rotation.x = Math.sin(this.phase * 1.6 + i * Math.PI) * 0.7);
      return false;
    }

    settle() {
      this.g.position.y = FLOOR_Y;
      this.legs.forEach(l => l.rotation.x = 0);
      this.head.rotation.x = 0;
    }

    update(dt) {
      this.timer -= dt;
      this.g.rotation.y = this.heading;

      switch (this.state) {
        case "idle":
          this.settle();
          this.g.position.y = FLOOR_Y + Math.sin(Date.now() * 0.003 + this.speed * 9) * 0.015; // breathing
          if (this.timer <= 0) {
            const roll = Math.random();
            if (roll < 0.22 && !wheel.occupant) {
              this.state = "toWheel";
              this.target.set(wheelRoot.position.x - 1.1, FLOOR_Y, wheelRoot.position.z);
            } else if (roll < 0.42) {
              this.state = "toBowl";
              this.target.set(BOWL.x + 0.95, FLOOR_Y, BOWL.z + 0.4);
            } else {
              this.pickWanderTarget();
              this.state = "walk";
              this.timer = 12;
            }
          }
          break;

        case "walk":
          if (this.walkStep(dt) || this.timer <= 0) { this.state = "idle"; this.timer = rnd(0.8, 3); }
          break;

        case "toWheel":
          if (this.walkStep(dt)) {
            this.state = "onWheel";
            this.timer = rnd(4, 9);
            wheel.occupant = this;
            this.g.position.set(wheelRoot.position.x, FLOOR_Y + 0.28, wheelRoot.position.z);
            this.heading = Math.PI / 2; // face +? tangent direction
          } else if (this.timer < -15) this.state = "idle";
          break;

        case "onWheel": {
          this.g.rotation.y = this.heading;
          this.phase += dt * 16;
          this.legs.forEach((l, i) => l.rotation.x = Math.sin(this.phase + i * Math.PI) * 1.1);
          this.g.position.y = FLOOR_Y + 0.28 + Math.abs(Math.sin(this.phase)) * 0.03;
          if (this.timer <= 0) {
            wheel.occupant = null;
            this.state = "walk";
            this.timer = 10;
            this.pickWanderTarget();
            this.g.position.set(wheelRoot.position.x - 1.2, FLOOR_Y, wheelRoot.position.z + 0.6);
          }
          break;
        }

        case "toBowl":
          if (this.walkStep(dt)) {
            this.state = "eat";
            this.timer = rnd(2.5, 5);
            this.heading = Math.atan2(BOWL.x - this.g.position.x, BOWL.z - this.g.position.z);
          } else if (this.timer < -15) this.state = "idle";
          break;

        case "eat":
          this.settle();
          this.faceTowards(BOWL, dt);
          this.head.rotation.x = Math.sin(Date.now() * 0.02) * 0.28 + 0.25; // munching head bob
          if (this.timer <= 0) { this.state = "idle"; this.timer = rnd(1, 3); }
          break;
      }
    }
  }

  const wheel = { occupant: null };

  const hamsters = [
    new Hamster(0xf6c66b,  1.0,  1.5),  // golden
    new Hamster(0xefe6d8, -1.5, -1.0),  // cream
    new Hamster(0xc98a5b,  0.5, -2.5),  // cinnamon
    new Hamster(0xbfb6ae, -0.5,  3.0),  // pearl
  ];

  // ---------- Simple orbit camera ----------
  let theta = 0.7, phi = 1.05, dist = 15;
  let dragging = false, px = 0, py = 0, downX = 0, downY = 0;

  function updateCamera() {
    phi = THREE.MathUtils.clamp(phi, 0.15, 1.45);
    dist = THREE.MathUtils.clamp(dist, 7, 28);
    camera.position.set(
      target.x + dist * Math.sin(phi) * Math.sin(theta),
      target.y + dist * Math.cos(phi),
      target.z + dist * Math.sin(phi) * Math.cos(theta)
    );
    camera.lookAt(target);
  }
  updateCamera();

  const el = renderer.domElement;
  el.addEventListener("pointerdown", e => { dragging = true; px = downX = e.clientX; py = downY = e.clientY; });
  window.addEventListener("pointermove", e => {
    if (!dragging) return;
    theta -= (e.clientX - px) * 0.006;
    phi   -= (e.clientY - py) * 0.005;
    px = e.clientX; py = e.clientY;
    updateCamera();
  });
  window.addEventListener("pointerup", e => {
    if (dragging && Math.hypot(e.clientX - downX, e.clientY - downY) < 6) handleClick(e);
    dragging = false;
  });
  el.addEventListener("wheel", e => { e.preventDefault(); dist += e.deltaY * 0.01; updateCamera(); }, { passive: false });

  // Click the wheel to spin it!
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  function handleClick(e) {
    pointer.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    if (raycaster.intersectObject(wheelRun, true).length) wheelVel += 7;
  }

  // ---------- Loop ----------
  let last = performance.now();
  function animate(now) {
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;

    hamsters.forEach(h => h.update(dt));

    // Wheel physics
    if (wheel.occupant && wheel.occupant.state === "onWheel") {
      wheelAngle -= 5.5 * dt; // powered by tiny hamster engine
    } else {
      wheelAngle -= wheelVel * dt;
      wheelVel *= Math.max(0, 1 - dt * 0.9);
    }
    wheelRun.rotation.x = wheelAngle;

    // Gentle auto-rotate when idle-ish
    if (!dragging) { theta += dt * 0.03; updateCamera(); }

    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);

  window.addEventListener("resize", () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });
})();
</script>
</body>
</html>
```

## What's inside

| Feature | Details |
|---|---|
| **Scene** | Round cage with bars + rings, pink tray, sandy bedding, grass ground, soft shadows, fog |
| **4 hamsters** | Golden, cream, cinnamon, pearl — built from flat-shaded low-poly spheres (chubby body, cheeks, ears, tiny tail nub, 4 legs) |
| **Autonomous AI** | State machine: `idle → walk / toWheel / toBowl → onWheel / eat → idle`, with turn smoothing, hoppy waddle walk, animated legs, breathing idle, and munching head-bob at the food bowl |
| **Interactive wheel** | Click it to spin (raycast click, drag-vs-click detection). Hamsters occasionally climb in and power it with their tiny legs 🐹 |
| **Extras** | Tunnel, food bowl with kibble, stacking blocks, cute roof accent |
| **Camera** | Custom minimal orbit controls (drag / scroll / touch), gentle auto-rotate, clamped angles |

No build step, no modules — just open the file. Runs at 60fps on any modern browser.