Save the following as **`index.html`** and open it in a modern browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Low-Poly Hamster Playground</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #ffe9f0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    canvas {
      display: block;
    }

    #ui {
      position: fixed;
      top: 16px;
      left: 16px;
      color: #5b3a4a;
      pointer-events: none;
      text-shadow: 0 1px 0 rgba(255, 255, 255, 0.75);
    }

    #ui h1 {
      margin: 0 0 6px;
      font-size: clamp(20px, 4vw, 34px);
    }

    #ui p {
      margin: 0;
      font-size: 14px;
      opacity: 0.85;
    }
  </style>
</head>
<body>
  <div id="ui">
    <h1>Low-Poly Hamster Playground</h1>
    <p>Drag to rotate • Scroll to zoom</p>
  </div>

  <script type="module">
    import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

    // ---------------------------------------------------------------------
    // Basic scene setup
    // ---------------------------------------------------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#ffe9f0");
    scene.fog = new THREE.Fog("#ffe9f0", 22, 55);

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    );

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.domElement.style.touchAction = "none";
    document.body.appendChild(renderer.domElement);

    // ---------------------------------------------------------------------
    // Lights
    // ---------------------------------------------------------------------
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0xffd1dc, 1.15);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.25);
    dirLight.position.set(8, 14, 10);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(1024, 1024);
    dirLight.shadow.camera.left = -12;
    dirLight.shadow.camera.right = 12;
    dirLight.shadow.camera.top = 14;
    dirLight.shadow.camera.bottom = -2;
    dirLight.shadow.camera.near = 1;
    dirLight.shadow.camera.far = 40;
    scene.add(dirLight);

    // ---------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------
    function rand(min, max) {
      return min + Math.random() * (max - min);
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function lerpAngle(a, b, t) {
      let diff = b - a;
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      return a + diff * t;
    }

    const floorTop = 0.62;

    // ---------------------------------------------------------------------
    // Cage tray, bedding, and bars
    // ---------------------------------------------------------------------
    const cage = new THREE.Group();
    scene.add(cage);

    const tray = new THREE.Mesh(
      new THREE.BoxGeometry(11, 0.5, 8),
      new THREE.MeshStandardMaterial({
        color: "#f6e2c4",
        flatShading: true,
        roughness: 0.9
      })
    );
    tray.position.y = 0.25;
    tray.receiveShadow = true;
    cage.add(tray);

    const bedding = new THREE.Mesh(
      new THREE.BoxGeometry(10.4, 0.12, 7.4),
      new THREE.MeshStandardMaterial({
        color: "#e7d0a1",
        flatShading: true,
        roughness: 1.0
      })
    );
    bedding.position.y = 0.56;
    bedding.receiveShadow = true;
    cage.add(bedding);

    // Little bedding chips for extra low-poly charm
    for (let i = 0; i < 35; i++) {
      const s = rand(0.12, 0.28);
      const chip = new THREE.Mesh(
        new THREE.BoxGeometry(s, s * 0.35, s * rand(0.8, 1.4)),
        new THREE.MeshStandardMaterial({
          color: new THREE.Color().setHSL(0.1, 0.45, rand(0.55, 0.75)),
          flatShading: true
        })
      );
      chip.position.set(rand(-4.6, 4.6), 0.63, rand(-3.2, 3.2));
      chip.rotation.y = rand(0, Math.PI);
      cage.add(chip);
    }

    const barMat = new THREE.MeshStandardMaterial({
      color: "#9fc3d8",
      transparent: true,
      opacity: 0.55,
      roughness: 0.35,
      metalness: 0.15,
      flatShading: true
    });

    const barGeo = new THREE.CylinderGeometry(0.06, 0.06, 3.0, 6);
    const xHalf = 5.0;
    const zHalf = 3.8;
    const barY = 2.0;

    function addBar(x, z) {
      const bar = new THREE.Mesh(barGeo, barMat);
      bar.position.set(x, barY, z);
      cage.add(bar);
    }

    for (let x = -xHalf; x <= xHalf + 0.01; x += 1.0) {
      addBar(x, -zHalf);
      addBar(x, zHalf);
    }

    for (let z = -zHalf + 1.0; z <= zHalf - 1.0 + 0.01; z += 1.0) {
      addBar(-xHalf, z);
      addBar(xHalf, z);
    }

    const frameMat = new THREE.MeshStandardMaterial({
      color: "#7fa8c0",
      flatShading: true,
      roughness: 0.4,
      metalness: 0.2
    });

    const topXGeo = new THREE.BoxGeometry(11, 0.12, 0.12);
    const topZGeo = new THREE.BoxGeometry(0.12, 0.12, 8);

    for (const z of [-zHalf, zHalf]) {
      const frame = new THREE.Mesh(topXGeo, frameMat);
      frame.position.set(0, 3.5, z);
      cage.add(frame);
    }

    for (const x of [-xHalf, xHalf]) {
      const frame = new THREE.Mesh(topZGeo, frameMat);
      frame.position.set(x, 3.5, 0);
      cage.add(frame);
    }

    // ---------------------------------------------------------------------
    // Interactive wheel
    // ---------------------------------------------------------------------
    const wheelCenter = new THREE.Vector3(3.4, 2.05, 0);
    const wheelRunPos = new THREE.Vector3(3.4, 1.05, 0);
    const wheelTarget = new THREE.Vector3(1.2, 0, 0);

    const wheelGroup = new THREE.Group();
    wheelGroup.position.copy(wheelCenter);
    scene.add(wheelGroup);

    const wheelSpin = new THREE.Group();
    wheelGroup.add(wheelSpin);

    const rim = new THREE.Mesh(
      new THREE.TorusGeometry(1.3, 0.08, 6, 16),
      new THREE.MeshStandardMaterial({
        color: "#ff7aa2",
        flatShading: true,
        roughness: 0.55
      })
    );
    rim.castShadow = true;
    wheelSpin.add(rim);

    // Small colored bumps around the wheel
    for (let i = 0; i < 8; i++) {
      const dot = new THREE.Mesh(
        new THREE.BoxGeometry(0.14, 0.14, 0.14),
        new THREE.MeshStandardMaterial({
          color: "#ffd166",
          flatShading: true
        })
      );
      dot.position.set(
        Math.cos(i * Math.PI / 4) * 1.3,
        Math.sin(i * Math.PI / 4) * 1.3,
        0
      );
      dot.castShadow = true;
      wheelSpin.add(dot);
    }

    const axle = new THREE.Mesh(
      new THREE.CylinderGeometry(0.05, 0.05, 1.7, 8),
      new THREE.MeshStandardMaterial({
        color: "#8d99ae",
        flatShading: true,
        metalness: 0.25,
        roughness: 0.45
      })
    );
    axle.rotation.x = Math.PI / 2;
    axle.castShadow = true;
    wheelGroup.add(axle);

    const standMat = new THREE.MeshStandardMaterial({
      color: "#c9a27a",
      flatShading: true,
      roughness: 0.85
    });

    for (const z of [-0.75, 0.75]) {
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.2, 1.45, 0.2), standMat);
      post.position.set(3.4, 1.345, z);
      post.castShadow = true;
      scene.add(post);
    }

    // ---------------------------------------------------------------------
    // Food bowl
    // ---------------------------------------------------------------------
    const bowlGroupPos = new THREE.Vector3(-3.0, 0.8, 2.0);
    const bowlRunPos = new THREE.Vector3(-1.4, floorTop, 2.0);
    const bowlTarget = new THREE.Vector3(-1.4, 0, 2.0);
    const bowlFaceTarget = new THREE.Vector3(-3.0, 0, 2.0);

    const bowlGroup = new THREE.Group();
    bowlGroup.position.copy(bowlGroupPos);
    scene.add(bowlGroup);

    const bowl = new THREE.Mesh(
      new THREE.CylinderGeometry(0.55, 0.42, 0.35, 8),
      new THREE.MeshStandardMaterial({
        color: "#7ec8e3",
        flatShading: true,
        roughness: 0.6
      })
    );
    bowl.castShadow = true;
    bowlGroup.add(bowl);

    const pellets = [];
    for (let i = 0; i < 6; i++) {
      const pellet = new THREE.Mesh(
        new THREE.IcosahedronGeometry(0.08, 0),
        new THREE.MeshStandardMaterial({
          color: "#d9a066",
          flatShading: true
        })
      );
      pellet.position.set(rand(-0.25, 0.25), 0.2, rand(-0.25, 0.25));
      pellet.castShadow = true;
      bowlGroup.add(pellet);
      pellets.push(pellet);
    }

    // ---------------------------------------------------------------------
    // Low-poly hamster factory
    // ---------------------------------------------------------------------
    function createHamster(color) {
      const group = new THREE.Group();

      const mainColor = new THREE.Color(color);
      const bodyMat = new THREE.MeshStandardMaterial({
        color: mainColor,
        flatShading: true,
        roughness: 0.85
      });

      const darkMat = new THREE.MeshStandardMaterial({
        color: mainColor.clone().multiplyScalar(0.72),
        flatShading: true,
        roughness: 0.85
      });

      const lightMat = new THREE.MeshStandardMaterial({
        color: mainColor.clone().lerp(new THREE.Color("#ffffff"), 0.35),
        flatShading: true,
        roughness: 0.85
      });

      // Body
      const body = new THREE.Mesh(new THREE.IcosahedronGeometry(0.45, 1), bodyMat);
      body.scale.set(1.2, 0.85, 1.35);
      body.position.y = 0.45;
      group.add(body);

      // Head
      const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.32, 1), bodyMat);
      head.position.set(0, 0.52, 0.48);
      group.add(head);

      // Cheeks
      const cheekGeo = new THREE.IcosahedronGeometry(0.16, 0);
      const cheekL = new THREE.Mesh(cheekGeo, lightMat);
      cheekL.position.set(-0.38, 0.48, 0.55);
      group.add(cheekL);

      const cheekR = new THREE.Mesh(cheekGeo, lightMat);
      cheekR.position.set(0.38, 0.48, 0.55);
      group.add(cheekR);

      // Ears
      const earGeo = new THREE.ConeGeometry(0.1, 0.16, 5);
      const earL = new THREE.Mesh(earGeo, darkMat);
      earL.position.set(-0.18, 0.78, 0.45);
      earL.rotation.z = 0.45;
      group.add(earL);

      const earR = new THREE.Mesh(earGeo, darkMat);
      earR.position.set(0.18, 0.78, 0.45);
      earR.rotation.z = -0.45;
      group.add(earR);

      // Eyes
      const eyeMat = new THREE.MeshStandardMaterial({
        color: "#222222",
        flatShading: true
      });
      const eyeGeo = new THREE.IcosahedronGeometry(0.05, 0);

      const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
      eyeL.position.set(-0.12, 0.56, 0.76);
      group.add(eyeL);

      const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
      eyeR.position.set(0.12, 0.56, 0.76);
      group.add(eyeR);

      // Nose
      const nose = new THREE.Mesh(
        new THREE.IcosahedronGeometry(0.045, 0),
        new THREE.MeshStandardMaterial({
          color: "#ff9aa2",
          flatShading: true
        })
      );
      nose.position.set(0, 0.52, 0.82);
      group.add(nose);

      // Tiny tail
      const tail = new THREE.Mesh(new THREE.IcosahedronGeometry(0.07, 0), darkMat);
      tail.position.set(0, 0.35, -0.65);
      group.add(tail);

      // Legs
      const legs = [];
      const legGeo = new THREE.BoxGeometry(0.11, 0.22, 0.11);
      const legPositions = [
        [-0.24, 0.11, 0.32],
        [0.24, 0.11, 0.32],
        [-0.24, 0.11, -0.32],
        [0.24, 0.11, -0.32]
      ];

      for (const p of legPositions) {
        const leg = new THREE.Mesh(legGeo, darkMat);
        leg.position.set(p[0], p[1], p[2]);
        group.add(leg);
        legs.push(leg);
      }

      group.traverse((obj) => {
        if (obj.isMesh) obj.castShadow = true;
      });

      group.userData = {
        body,
        head,
        legs,
        phase: Math.random() * Math.PI * 2
      };

      return group;
    }

    // ---------------------------------------------------------------------
    // Hamster behavior
    // ---------------------------------------------------------------------
    let wheelOccupied = false;

    class Hamster {
      constructor(color, scale, position) {
        this.group = createHamster(color);
        this.group.scale.setScalar(scale);
        this.group.position.copy(position);
        this.group.rotation.y = rand(0, Math.PI * 2);

        this.state = "idle";
        this.timer = rand(0.5, 2.5);
        this.target = new THREE.Vector3();
        this.targetType = "random";

        this.speed = rand(0.7, 1.3);
        this.turnDir = 1;
        this.wheelTimer = 0;
        this.eatTimer = 0;
        this.phase = this.group.userData.phase;
      }

      chooseTarget() {
        const r = Math.random();

        if (!wheelOccupied && r < 0.28) {
          this.target.copy(wheelTarget);
          this.targetType = "wheel";
        } else if (r < 0.58) {
          this.target.copy(bowlTarget);
          this.targetType = "bowl";
        } else {
          let x, z;
          do {
            x = rand(-3.8, 3.8);
            z = rand(-2.8, 2.8);
          } while (
            Math.hypot(x - wheelCenter.x, z - wheelCenter.z) < 2.2 ||
            Math.hypot(x - bowlFaceTarget.x, z - bowlFaceTarget.z) < 1.6
          );

          this.target.set(x, 0, z);
          this.targetType = "random";
        }
      }

      update(dt) {
        const pos = this.group.position;

        if (this.state === "idle") {
          this.timer -= dt;

          if (this.timer <= 0) {
            if (Math.random() < 0.22) {
              this.state = "turn";
              this.timer = rand(0.6, 1.8);
              this.turnDir = Math.random() < 0.5 ? -1 : 1;
            } else {
              this.chooseTarget();
              this.state = "walk";
            }
          }
        } else if (this.state === "turn") {
          this.group.rotation.y += this.turnDir * 1.6 * dt;
          this.timer -= dt;

          if (this.timer <= 0) {
            this.state = "idle";
            this.timer = rand(0.5, 2.0);
          }
        } else if (this.state === "walk") {
          const dir = new THREE.Vector3(
            this.target.x - pos.x,
            0,
            this.target.z - pos.z
          );

          const dist = dir.length();

          if (dist < 0.25) {
            if (this.targetType === "wheel") {
              if (!wheelOccupied) {
                wheelOccupied = true;
                this.state = "wheel";
                this.wheelTimer = rand(4, 8);
              } else {
                this.chooseTarget();
              }
            } else if (this.targetType === "bowl") {
              this.state = "eat";
              this.eatTimer = rand(2, 4);
            } else {
              this.state = "idle";
              this.timer = rand(0.8, 2.5);
            }
          } else {
            dir.normalize();

            const desiredAngle = Math.atan2(dir.x, dir.z);
            this.group.rotation.y = lerpAngle(
              this.group.rotation.y,
              desiredAngle,
              1 - Math.exp(-8 * dt)
            );

            pos.x += dir.x * this.speed * dt;
            pos.z += dir.z * this.speed * dt;

            // Simple object avoidance so hamsters do not wander through props
            if (this.targetType !== "wheel") {
              const dx = pos.x - wheelCenter.x;
              const dz = pos.z - wheelCenter.z;
              const d = Math.hypot(dx, dz);

              if (d < 1.8 && d > 0.001) {
                const push = 1.8 - d;
                pos.x += (dx / d) * push;
                pos.z += (dz / d) * push;
              }
            }

            if (this.state !== "eat") {
              const dx = pos.x - bowlFaceTarget.x;
              const dz = pos.z - bowlFaceTarget.z;
              const d = Math.hypot(dx, dz);

              if (d < 1.2 && d > 0.001) {
                const push = 1.2 - d;
                pos.x += (dx / d) * push;
                pos.z += (dz / d) * push;
              }
            }

            pos.x = clamp(pos.x, -4.2, 4.2);
            pos.z = clamp(pos.z, -3.0, 3.0);
          }
        } else if (this.state === "wheel") {
          this.wheelTimer -= dt;

          const lerp = 1 - Math.exp(-8 * dt);
          pos.lerp(wheelRunPos, lerp);
          this.group.rotation.y = lerpAngle(this.group.rotation.y, 0, lerp);

          if (this.wheelTimer <= 0) {
            wheelOccupied = false;
            pos.copy(wheelTarget);
            pos.y = floorTop;
            this.state = "idle";
            this.timer = rand(0.5, 2.0);
          }
        } else if (this.state === "eat") {
          this.eatTimer -= dt;

          const lerp = 1 - Math.exp(-6 * dt);
          pos.lerp(bowlRunPos, lerp);

          const desiredAngle = Math.atan2(
            bowlFaceTarget.x - pos.x,
            bowlFaceTarget.z - pos.z
          );
          this.group.rotation.y = lerpAngle(
            this.group.rotation.y,
            desiredAngle,
            lerp
          );

          if (this.eatTimer <= 0) {
            this.state = "idle";
            this.timer = rand(0.8, 2.5);
          }
        }

        this.animate(dt);
      }

      animate(dt) {
        const data = this.group.userData;
        const walking = this.state === "walk" || this.state === "wheel";
        const rate = this.state === "wheel" ? 14 : this.state === "walk" ? 9 : 1.2;

        this.phase += dt * rate;

        data.legs.forEach((leg, i) => {
          const gait = i === 0 || i === 3 ? 0 : Math.PI;
          const amp = walking ? 0.65 : 0.04;
          leg.rotation.x = Math.sin(this.phase + gait) * amp;
        });

        const bob = walking
          ? Math.sin(this.phase * 2) * 0.035
          : Math.sin(this.phase * 0.7) * 0.012;

        data.body.position.y = 0.45 + bob;

        const headBob =
          this.state === "eat"
            ? Math.sin(this.phase * 8) * 0.09
            : bob * 0.6;

        data.head.position.y = 0.52 + headBob;
      }
    }

    // ---------------------------------------------------------------------
    // Create hamsters
    // ---------------------------------------------------------------------
    const hamsters = [];
    const hamsterColors = [
      "#f4a261",
      "#e76f51",
      "#f8f3e6",
      "#8d99ae",
      "#ffd166"
    ];

    for (let i = 0; i < 5; i++) {
      let x, z;

      do {
        x = rand(-3.5, 2.5);
        z = rand(-2.5, 2.5);
      } while (
        Math.hypot(x - wheelCenter.x, z - wheelCenter.z) < 2.2 ||
        Math.hypot(x - bowlFaceTarget.x, z - bowlFaceTarget.z) < 1.6
      );

      const start = new THREE.Vector3(x, floorTop, z);
      const hamster = new Hamster(hamsterColors[i], rand(0.8, 1.05), start);
      hamsters.push(hamster);
      scene.add(hamster.group);
    }

    // ---------------------------------------------------------------------
    // Simple camera controls: drag to rotate, scroll to zoom
    // ---------------------------------------------------------------------
    let theta = 0.75;
    let phi = 1.1;
    let radius = 15;
    const cameraTarget = new THREE.Vector3(0, 1.7, 0);

    function updateCamera() {
      camera.position.set(
        cameraTarget.x + radius * Math.sin(phi) * Math.sin(theta),
        cameraTarget.y + radius * Math.cos(phi),
        cameraTarget.z + radius * Math.sin(phi) * Math.cos(theta)
      );
      camera.lookAt(cameraTarget);
    }

    updateCamera();

    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    renderer.domElement.addEventListener("pointerdown", (e) => {
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      renderer.domElement.setPointerCapture(e.pointerId);
    });

    renderer.domElement.addEventListener("pointermove", (e) => {
      if (!dragging) return;

      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;

      theta -= dx * 0.005;
      phi = clamp(phi - dy * 0.005, 0.35, 1.45);
      updateCamera();
    });

    renderer.domElement.addEventListener("pointerup", (e) => {
      dragging = false;
      try {
        renderer.domElement.releasePointerCapture(e.pointerId);
      } catch (err) {
        // Ignore release errors.
      }
    });

    renderer.domElement.addEventListener("pointercancel", () => {
      dragging = false;
    });

    renderer.domElement.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        radius = clamp(radius + e.deltaY * 0.01, 8, 24);
        updateCamera();
      },
      { passive: false }
    );

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // ---------------------------------------------------------------------
    // Animation loop
    // ---------------------------------------------------------------------
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const dt = Math.min(clock.getDelta(), 0.05);
      const time = clock.elapsedTime;

      for (const hamster of hamsters) {
        hamster.update(dt);
      }

      wheelSpin.rotation.z += (wheelOccupied ? 3.5 : 0.18) * dt;

      const eating = hamsters.some((h) => h.state === "eat");
      for (let i = 0; i < pellets.length; i++) {
        const scale = eating ? 1 + Math.sin(time * 8 + i) * 0.12 : 1;
        pellets[i].scale.setScalar(scale);
      }

      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```