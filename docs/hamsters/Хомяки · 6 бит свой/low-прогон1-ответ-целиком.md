```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Low-Poly Hamster Playground</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { overflow: hidden; background: #1a1a2e; font-family: 'Segoe UI', sans-serif; }
        canvas { display: block; }
        #ui {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            pointer-events: none;
        }
        #ui h1 {
            color: #fff;
            font-size: 1.6rem;
            text-shadow: 0 2px 8px rgba(0,0,0,0.5);
            letter-spacing: 1px;
        }
        #ui p {
            color: rgba(255,255,255,0.7);
            font-size: 0.85rem;
            margin-top: 4px;
        }
        #status {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255,255,255,0.5);
            font-size: 0.75rem;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="ui">
        <h1>🐹 Low-Poly Hamster Playground</h1>
        <p>Drag to rotate • Scroll to zoom</p>
    </div>
    <div id="status">3 hamsters are playing...</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // ============ SCENE SETUP ============
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x2d2d44);
        scene.fog = new THREE.Fog(0x2d2d44, 15, 30);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(5, 4, 6);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.target.set(0, 1, 0);
        controls.maxPolarAngle = Math.PI * 0.45;
        controls.minDistance = 3;
        controls.maxDistance = 15;

        // ============ LIGHTING ============
        const ambientLight = new THREE.AmbientLight(0xfff5e6, 0.5);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 0.9);
        dirLight.position.set(5, 8, 3);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.set(1024, 1024);
        dirLight.shadow.camera.near = 1;
        dirLight.shadow.camera.far = 20;
        dirLight.shadow.camera.left = -5;
        dirLight.shadow.camera.right = 5;
        dirLight.shadow.camera.top = 5;
        dirLight.shadow.camera.bottom = -5;
        scene.add(dirLight);

        const pointLight = new THREE.PointLight(0xffcc88, 0.4, 10);
        pointLight.position.set(-2, 3, -2);
        scene.add(pointLight);

        // ============ MATERIALS HELPER ============
        function mat(color) {
            return new THREE.MeshLambertMaterial({ color, flatShading: true });
        }

        // ============ CAGE ============
        const cageGroup = new THREE.Group();
        scene.add(cageGroup);

        // Base tray
        const trayGeo = new THREE.BoxGeometry(6, 0.3, 4);
        const trayMat = mat(0x5c3d2e);
        const tray = new THREE.Mesh(trayGeo, trayMat);
        tray.position.y = -0.15;
        tray.receiveShadow = true;
        cageGroup.add(tray);

        // Bedding (colorful floor)
        const beddingGeo = new THREE.BoxGeometry(5.8, 0.15, 3.8);
        const beddingMat = mat(0xf5deb3);
        const bedding = new THREE.Mesh(beddingGeo, beddingMat);
        bedding.position.y = 0.075;
        bedding.receiveShadow = true;
        cageGroup.add(bedding);

        // Bedding particles (small colorful bits)
        const beddingColors = [0xf5deb3, 0xfaebd7, 0xdeb887, 0xffe4b5];
        for (let i = 0; i < 40; i++) {
            const s = 0.08 + Math.random() * 0.08;
            const bit = new THREE.Mesh(
                new THREE.BoxGeometry(s, s * 0.5, s),
                mat(beddingColors[Math.floor(Math.random() * beddingColors.length)])
            );
            bit.position.set(
                (Math.random() - 0.5) * 5.4,
                0.16,
                (Math.random() - 0.5) * 3.4
            );
            bit.rotation.y = Math.random() * Math.PI;
            cageGroup.add(bit);
        }

        // Cage walls (wire frame)
        function createWire(x1, y1, z1, x2, y2, z2, radius = 0.02) {
            const dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;
            const len = Math.sqrt(dx*dx + dy*dy + dz*dz);
            const geo = new THREE.CylinderGeometry(radius, radius, len, 5);
            const m = mat(0xaaaaaa);
            const wire = new THREE.Mesh(geo, m);
            wire.position.set((x1+x2)/2, (y1+y2)/2, (z1+z2)/2);
            const mid = new THREE.Vector3(0, len/2, 0);
            const dir = new THREE.Vector3(dx, dy, dz).normalize();
            const quat = new THREE.Quaternion().setFromUnitVectors(mid, dir);
            wire.quaternion.copy(quat);
            return wire;
        }

        const cageW = 5.8, cageH = 3, cageD = 3.8;
        const hw = cageW/2, hd = cageD/2;
        const barSpacing = 0.7;

        // Vertical bars - front and back
        for (let x = -hw; x <= hw; x += barSpacing) {
            cageGroup.add(createWire(x, 0, hd, x, cageH, hd));
            cageGroup.add(createWire(x, 0, -hd, x, cageH, -hd));
        }
        // Vertical bars - sides
        for (let z = -hd; z <= hd; z += barSpacing) {
            cageGroup.add(createWire(hw, 0, z, hw, cageH, z));
            cageGroup.add(createWire(-hw, 0, z, -hw, cageH, z));
        }
        // Top horizontal bars
        for (let x = -hw; x <= hw; x += barSpacing) {
            cageGroup.add(createWire(x, cageH, -hd, x, cageH, hd));
        }
        for (let z = -hd; z <= hd; z += barSpacing) {
            cageGroup.add(createWire(-hw, cageH, z, hw, cageH, z));
        }
        // Corner posts (thicker)
        const postR = 0.04;
        [[-hw,-hd],[hw,-hd],[-hw,hd],[hw,hd]].forEach(([x,z]) => {
            cageGroup.add(createWire(x, 0, z, x, cageH, z, postR));
        });

        // ============ RUNNING WHEEL ============
        const wheelGroup = new THREE.Group();
        wheelGroup.position.set(-2, 0.9, -1);
        cageGroup.add(wheelGroup);

        // Wheel stand
        const standMat = mat(0x4488cc);
        const standBase = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.1, 0.8), standMat);
        standBase.position.y = -0.85;
        wheelGroup.add(standBase);
        const standPost = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.7, 6), standMat);
        standPost.position.y = -0.5;
        wheelGroup.add(standPost);

        // Wheel ring
        const wheelRing = new THREE.Mesh(
            new THREE.TorusGeometry(0.5, 0.05, 6, 12),
            mat(0x66aaff)
        );
        wheelRing.position.y = 0;
        wheelGroup.add(wheelRing);

        // Wheel spokes
        for (let i = 0; i < 6; i++) {
            const angle = (i / 6) * Math.PI * 2;
            const spoke = new THREE.Mesh(
                new THREE.CylinderGeometry(0.02, 0.02, 0.95, 4),
                mat(0x88bbff)
            );
            spoke.position.y = 0;
            spoke.rotation.z = angle;
            spoke.position.x = Math.cos(angle) * 0.25;
            spoke.position.y = Math.sin(angle) * 0.25;
            spoke.rotation.z = angle + Math.PI/2;
            // Simpler: just rotate around center
            spoke.position.set(Math.cos(angle)*0.25, Math.sin(angle)*0.25, 0);
            spoke.lookAt(0, 0, 0);
            spoke.rotateX(Math.PI/2);
            wheelGroup.add(spoke);
        }

        // Wheel hub
        const hub = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 4), mat(0x4488cc));
        wheelGroup.add(hub);

        let wheelSpeed = 0;
        let wheelTargetSpeed = 0;

        // ============ FOOD BOWL ============
        const bowlGroup = new THREE.Group();
        bowlGroup.position.set(2, 0.15, 1.2);
        cageGroup.add(bowlGroup);

        const bowl = new THREE.Mesh(
            new THREE.CylinderGeometry(0.3, 0.2, 0.15, 8),
            mat(0xff6688)
        );
        bowlGroup.add(bowl);

        // Food pellets
        for (let i = 0; i < 6; i++) {
            const pellet = new THREE.Mesh(
                new THREE.SphereGeometry(0.04, 5, 3),
                mat(0xcc8844)
            );
            pellet.position.set(
                (Math.random()-0.5)*0.2,
                0.08,
                (Math.random()-0.5)*0.2
            );
            bowlGroup.add(pellet);
        }

        // ============ TUNNEL ============
        const tunnelGroup = new THREE.Group();
        tunnelGroup.position.set(0.5, 0.3, -1.2);
        tunnelGroup.rotation.y = 0.4;
        cageGroup.add(tunnelGroup);

        const tunnelBody = new THREE.Mesh(
            new THREE.CylinderGeometry(0.3, 0.3, 1.2, 8, 1, false, 0, Math.PI),
            mat(0x88ddaa)
        );
        tunnelBody.rotation.z = Math.PI / 2;
        tunnelBody.rotation.y = Math.PI / 2;
        tunnelGroup.add(tunnelBody);

        // Tunnel ends
        [-0.6, 0.6].forEach(x => {
            const end = new THREE.Mesh(
                new THREE.CircleGeometry(0.3, 8, 0, Math.PI),
                mat(0x66bb88)
            );
            end.position.x = x;
            end.rotation.y = x > 0 ? -Math.PI/2 : Math.PI/2;
            end.rotation.x = Math.PI/2;
            tunnelGroup.add(end);
        });

        // ============ WATER BOTTLE ============
        const bottleGroup = new THREE.Group();
        bottleGroup.position.set(2.5, 1.2, -1.5);
        cageGroup.add(bottleGroup);

        const bottle = new THREE.Mesh(
            new THREE.CylinderGeometry(0.12, 0.15, 0.5, 6),
            new THREE.MeshLambertMaterial({ color: 0x88ccff, transparent: true, opacity: 0.7 })
        );
        bottleGroup.add(bottle);

        const nozzle = new THREE.Mesh(
            new THREE.CylinderGeometry(0.03, 0.05, 0.15, 5),
            mat(0x999999)
        );
        nozzle.position.y = -0.3;
        bottleGroup.add(nozzle);

        // ============ HAMSTER FACTORY ============
        function createHamster(bodyColor, bellyColor, earColor) {
            const group = new THREE.Group();

            // Body
            const body = new THREE.Mesh(
                new THREE.SphereGeometry(0.25, 7, 5),
                mat(bodyColor)
            );
            body.scale.set(1.3, 0.9, 1);
            body.position.y = 0.25;
            body.castShadow = true;
            group.add(body);

            // Belly
            const belly = new THREE.Mesh(
                new THREE.SphereGeometry(0.18, 6, 4),
                mat(bellyColor)
            );
            belly.scale.set(1.1, 0.7, 0.8);
            belly.position.set(0.05, 0.15, 0);
            group.add(belly);

            // Head
            const head = new THREE.Mesh(
                new THREE.SphereGeometry(0.18, 6, 5),
                mat(bodyColor)
            );
            head.position.set(0.3, 0.3, 0);
            head.castShadow = true;
            group.add(head);

            // Snout
            const snout = new THREE.Mesh(
                new THREE.SphereGeometry(0.08, 5, 4),
                mat(bellyColor)
            );
            snout.position.set(0.44, 0.26, 0);
            group.add(snout);

            // Nose
            const nose = new THREE.Mesh(
                new THREE.SphereGeometry(0.03, 4, 3),
                mat(0xff88aa)
            );
            nose.position.set(0.5, 0.27, 0);
            group.add(nose);

            // Eyes
            [-1, 1].forEach(side => {
                const eye = new THREE.Mesh(
                    new THREE.SphereGeometry(0.035, 4, 3),
                    mat(0x222222)
                );
                eye.position.set(0.38, 0.35, side * 0.1);
                group.add(eye);

                // Eye shine
                const shine = new THREE.Mesh(
                    new THREE.SphereGeometry(0.012, 3, 2),
                    mat(0xffffff)
                );
                shine.position.set(0.4, 0.37, side * 0.11);
                group.add(shine);
            });

            // Ears
            [-1, 1].forEach(side => {
                const ear = new THREE.Mesh(
                    new THREE.SphereGeometry(0.07, 5, 4),
                    mat(earColor)
                );
                ear.position.set(0.25, 0.48, side * 0.12);
                group.add(ear);

                const innerEar = new THREE.Mesh(
                    new THREE.SphereGeometry(0.04, 4, 3),
                    mat(0xffaacc)
                );
                innerEar.position.set(0.26, 0.49, side * 0.13);
                group.add(innerEar);
            });

            // Cheeks (fluffy)
            [-1, 1].forEach(side => {
                const cheek = new THREE.Mesh(
                    new THREE.SphereGeometry(0.08, 5, 4),
                    mat(bellyColor)
                );
                cheek.position.set(0.35, 0.22, side * 0.15);
                group.add(cheek);
            });

            // Legs
            const legPositions = [
                [0.15, 0.05, 0.1],
                [0.15, 0.05, -0.1],
                [-0.15, 0.05, 0.1],
                [-0.15, 0.05, -0.1]
            ];
            legPositions.forEach(pos => {
                const leg = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.03, 0.025, 0.1, 4),
                    mat(bellyColor)
                );
                leg.position.set(...pos);
                group.add(leg);
            });

            // Tail
            const tail = new THREE.Mesh(
                new THREE.SphereGeometry(0.04, 4, 3),
                mat(earColor)
            );
            tail.position.set(-0.35, 0.25, 0);
            group.add(tail);

            return group;
        }

        // ============ HAMSTERS ============
        const hamsterConfigs = [
            { body: 0xf5a623, belly: 0xfff5e6, ear: 0xe8943a, name: "Nugget" },
            { body: 0xffffff, belly: 0xfff0f5, ear: 0xffccdd, name: "Snowball" },
            { body: 0xc68e5c, belly: 0xede0d4, ear: 0xa0704a, name: "Cocoa" },
        ];

        const hamsters = [];
        const states = { IDLE: 0, WALKING: 1, TURNING: 2, AT_WHEEL: 3, EATING: 4 };

        hamsterConfigs.forEach((cfg, i) => {
            const hamster = createHamster(cfg.body, cfg.belly, cfg.ear);
            hamster.position.set(
                (Math.random() - 0.5) * 3,
                0,
                (Math.random() - 0.5) * 2
            );
            hamster.rotation.y = Math.random() * Math.PI * 2;
            scene.add(hamster);

            hamsters.push({
                mesh: hamster,
                name: cfg.name,
                state: states.IDLE,
                speed: 0.4 + Math.random() * 0.3,
                direction: Math.random() * Math.PI * 2,
                stateTimer: 1 + Math.random() * 3,
                turnSpeed: 0,
                bobPhase: Math.random() * Math.PI * 2,
                atWheel: false
            });
        });

        // ============ BEHAVIOR AI ============
        function updateHamster(h, dt) {
            h.stateTimer -= dt;
            h.bobPhase += dt * 8;

            const pos = h.mesh.position;
            const bounds = { x: 2.5, z: 1.5 };

            switch (h.state) {
                case states.IDLE:
                    // Slight bobbing
                    h.mesh.position.y = Math.sin(h.bobPhase * 0.5) * 0.01;
                    if (h.stateTimer <= 0) {
                        // Decide next action
                        const roll = Math.random();
                        if (roll < 0.5) {
                            h.state = states.WALKING;
                            h.direction = Math.random() * Math.PI * 2;
                            h.stateTimer = 2 + Math.random() * 3;
                        } else if (roll < 0.7) {
                            h.state = states.TURNING;
                            h.turnSpeed = (Math.random() > 0.5 ? 1 : -1) * (1 + Math.random());
                            h.stateTimer = 0.5 + Math.random() * 0.5;
                        } else if (roll < 0.85 && !hamsters.some(o => o.atWheel)) {
                            h.state = states.AT_WHEEL;
                            h.atWheel = true;
                            wheelTargetSpeed = 3;
                            h.stateTimer = 4 + Math.random() * 3;
                        } else {
                            h.state = states.EATING;
                            h.stateTimer = 2 + Math.random() * 2;
                        }
                    }
                    break;

                case states.WALKING:
                    // Move forward
                    const moveX = Math.sin(h.direction) * h.speed * dt;
                    const moveZ = Math.cos(h.direction) * h.speed * dt;
                    pos.x += moveX;
                    pos.z += moveZ;

                    // Bob while walking
                    h.mesh.position.y = Math.abs(Math.sin(h.bobPhase)) * 0.03;

                    // Face direction
                    h.mesh.rotation.y = h.direction + Math.PI;

                    // Boundary check
                    if (Math.abs(pos.x) > bounds.x || Math.abs(pos.z) > bounds.z) {
                        h.direction = Math.PI - h.direction + (Math.random()-0.5)*1.5;
                        pos.x = THREE.MathUtils.clamp(pos.x, -bounds.x, bounds.x);
                        pos.z = THREE.MathUtils.clamp(pos.z, -bounds.z, bounds.z);
                    }

                    // Random direction change
                    if (Math.random() < 0.01) {
                        h.direction += (Math.random() - 0.5) * 1.5;
                    }

                    if (h.stateTimer <= 0) {
                        h.state = states.IDLE;
                        h.stateTimer = 1 + Math.random() * 2;
                    }
                    break;

                case states.TURNING:
                    h.mesh.rotation.y += h.turnSpeed * dt;
                    h.mesh.position.y = Math.sin(h.bobPhase) * 0.01;
                    if (h.stateTimer <= 0) {
                        h.state = states.IDLE;
                        h.stateTimer = 0.5 + Math.random() * 1.5;
                    }
                    break;

                case states.AT_WHEEL:
                    // Move to wheel position
                    const wheelPos = new THREE.Vector3(-2, 0.5, -1);
                    const toWheel = wheelPos.clone().sub(pos);
                    toWheel.y = 0;
                    const dist = toWheel.length();

                    if (dist > 0.3) {
                        pos.lerp(wheelPos, 2 * dt);
                        h.mesh.rotation.y = Math.atan2(toWheel.x, toWheel.z) + Math.PI;
                        h.mesh.position.y = Math.abs(Math.sin(h.bobPhase)) * 0.02;
                    } else {
                        // At the wheel - spin animation
                        pos.set(wheelPos.x, 0.4 + Math.sin(h.bobPhase * 1.5) * 0.1, wheelPos.z);
                        h.mesh.rotation.y += dt * 2;
                        h.mesh.scale.setScalar(0.8 + Math.sin(h.bobPhase) * 0.05);
                    }

                    if (h.stateTimer <= 0) {
                        h.state = states.IDLE;
                        h.atWheel = false;
                        wheelTargetSpeed = 0;
                        h.stateTimer = 1 + Math.random() * 2;
                        h.mesh.scale.setScalar(1);
                        // Walk away
                        h.direction = Math.random() * Math.PI * 2;
                        h.state = states.WALKING;
                        h.stateTimer = 2 + Math.random() * 2;
                    }
                    break;

                case states.EATING:
                    // Move toward bowl
                    const bowlPos = new THREE.Vector3(2, 0, 1.2);
                    const toBowl = bowlPos.clone().sub(pos);
                    toBowl.y = 0;
                    const bDist = toBowl.length();

                    if (bDist > 0.4) {
                        pos.lerp(bowlPos, 2 * dt);
                        h.mesh.rotation.y = Math.atan2(toBowl.x, toBowl.z) + Math.PI;
                    } else {
                        // Eating animation
                        h.mesh.position.y = Math.abs(Math.sin(h.bobPhase * 2)) * 0.02;
                        h.mesh.rotation.y = Math.atan2(bowlPos.x - pos.x, bowlPos.z - pos.z) + Math.PI;
                        // Head bob
                        const headBob = Math.sin(h.bobPhase * 3) * 0.03;
                        h.mesh.children[1].position.y = 0.15 + headBob; // belly
                    }

                    if (h.stateTimer <= 0) {
                        h.state = states.IDLE;
                        h.stateTimer = 1 + Math.random() * 2;
                    }
                    break;
            }
        }

        // ============ DECORATIONS ============
        // Small toys
        const toyColors = [0xff6b6b, 0x4ecdc4, 0xffe66d];
        for (let i = 0; i < 3; i++) {
            const toy = new THREE.Mesh(
                new THREE.IcosahedronGeometry(0.1, 0),
                mat(toyColors[i])
            );
            toy.position.set(
                (Math.random()-0.5) * 4,
                0.2,
                (Math.random()-0.5) * 2.5
            );
            toy.castShadow = true;
            cageGroup.add(toy);
        }

        // Small hay pile
        const hayPile = new THREE.Mesh(
            new THREE.SphereGeometry(0.3, 5, 3),
            mat(0xd4a843)
        );
        hayPile.scale.set(1.5, 0.4, 1);
        hayPile.position.set(-1.5, 0.15, 1.3);
        cageGroup.add(hayPile);

        // ============ ANIMATION LOOP ============
        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const dt = Math.min(clock.getDelta(), 0.05);
            const time = clock.elapsedTime;

            // Update hamsters
            hamsters.forEach(h => updateHamster(h, dt));

            // Update wheel
            wheelSpeed += (wheelTargetSpeed - wheelSpeed) * dt * 2;
            wheelRing.rotation.x += wheelSpeed * dt;
            // Rotate spokes too
            wheelGroup.children.forEach((child, i) => {
                if (i >= 1 && i <= 7) { // spokes
                    child.rotation.x += wheelSpeed * dt;
                }
            });

            // Subtle light animation
            pointLight.intensity = 0.3 + Math.sin(time * 0.5) * 0.1;

            controls.update();
            renderer.render(scene, camera);
        }

        animate();

        // ============ RESIZE ============
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```

## What's Included

| Feature | Details |
|---------|---------|
| **Cage** | Wire-frame rectangular cage with corner posts, base tray, and colorful bedding |
| **3 Hamsters** | Nugget (golden), Snowball (white/pink), Cocoa (brown) — each with body, head, ears, eyes, cheeks, legs, and tail |
| **Running Wheel** | Spinning wheel with stand — a hamster will occasionally go "run" on it |
| **Food Bowl** | Pink bowl with pellets — hamsters walk over to eat |
| **Tunnel** | Green half-cylinder tunnel as decoration |
| **Water Bottle** | Semi-transparent bottle on the wall |
| **Toys & Hay** | Scattered colorful icosahedron toys and a hay pile |

## Behavior System

Each hamster cycles through states:
- **IDLE** → pauses, bobs gently
- **WALKING** → moves in a direction, bounces, bounces off walls
- **TURNING** → spins in place
- **AT_WHEEL** → walks to the wheel, spins on it (wheel accelerates!)
- **EATING** → walks to the food bowl, head-bobs

Only one hamster can use the wheel at a time. The wheel smoothly accelerates/decelerates based on whether a hamster is using it.

## Controls
- **Left-click drag** → orbit camera
- **Scroll** → zoom in/out
- Camera is constrained to stay above the floor