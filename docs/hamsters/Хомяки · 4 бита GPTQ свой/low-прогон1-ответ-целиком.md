

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
        #info {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: #fff;
            background: rgba(0,0,0,0.5);
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 14px;
            pointer-events: none;
            text-align: center;
        }
        #info h1 { font-size: 18px; margin-bottom: 4px; color: #ffd89b; }
        #info p { font-size: 12px; opacity: 0.8; }
    </style>
</head>
<body>
    <div id="info">
        <h1>🐹 Low-Poly Hamster Playground</h1>
        <p>Drag to rotate • Scroll to zoom • Watch the hamsters play!</p>
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

        // --- SCENE SETUP ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x2d1b69);
        scene.fog = new THREE.Fog(0x2d1b69, 15, 30);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(6, 5, 8);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.target.set(0, 1, 0);
        controls.maxPolarAngle = Math.PI / 2.1;
        controls.minDistance = 4;
        controls.maxDistance = 15;

        // --- LIGHTS ---
        const ambientLight = new THREE.AmbientLight(0xffeedd, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xfff5e6, 1.2);
        dirLight.position.set(5, 8, 4);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.set(1024, 1024);
        dirLight.shadow.camera.near = 1;
        dirLight.shadow.camera.far = 20;
        dirLight.shadow.camera.left = -5;
        dirLight.shadow.camera.right = 5;
        dirLight.shadow.camera.top = 5;
        dirLight.shadow.camera.bottom = -5;
        scene.add(dirLight);

        const pointLight = new THREE.PointLight(0xff9944, 0.5, 10);
        pointLight.position.set(-3, 4, -2);
        scene.add(pointLight);

        // --- MATERIALS ---
        function mat(color) {
            return new THREE.MeshLambertMaterial({ color, flatShading: true });
        }

        // --- FLOOR / TRAY ---
        const CAGE_W = 6, CAGE_D = 5, CAGE_H = 3;

        const floorGeo = new THREE.BoxGeometry(CAGE_W, 0.2, CAGE_D);
        const floorMat = mat(0x8B6914);
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.position.y = -0.1;
        floor.receiveShadow = true;
        scene.add(floor);

        // Wood shavings (small colored boxes scattered)
        const shavingColors = [0xd4a55a, 0xc9944a, 0xb8843a, 0xe0b86a];
        for (let i = 0; i < 40; i++) {
            const s = 0.08 + Math.random() * 0.1;
            const g = new THREE.BoxGeometry(s, 0.03, s * 2);
            const m = mat(shavingColors[Math.floor(Math.random() * shavingColors.length)]);
            const mesh = new THREE.Mesh(g, m);
            mesh.position.set(
                (Math.random() - 0.5) * (CAGE_W - 0.5),
                0.02,
                (Math.random() - 0.5) * (CAGE_D - 0.5)
            );
            mesh.rotation.y = Math.random() * Math.PI;
            scene.add(mesh);
        }

        // --- CAGE WALLS (wire frame) ---
        function createWall(width, height, x, z, rotY) {
            const group = new THREE.Group();
            const barMat = new THREE.MeshLambertMaterial({ color: 0xaaaacc, flatShading: true });
            const barCount = Math.floor(width / 0.4);
            const barGeo = new THREE.CylinderGeometry(0.015, 0.015, height, 4);

            for (let i = 0; i <= barCount; i++) {
                const bar = new THREE.Mesh(barGeo, barMat);
                bar.position.set(-width / 2 + (i * width / barCount), height / 2, 0);
                group.add(bar);
            }

            // Top and bottom rails
            const railGeo = new THREE.CylinderGeometry(0.02, 0.02, width, 4);
            const topRail = new THREE.Mesh(railGeo, barMat);
            topRail.rotation.z = Math.PI / 2;
            topRail.position.y = height;
            group.add(topRail);

            const botRail = new THREE.Mesh(railGeo, barMat);
            botRail.rotation.z = Math.PI / 2;
            botRail.position.y = 0;
            group.add(botRail);

            // Middle rail
            const midRail = new THREE.Mesh(railGeo, barMat);
            midRail.rotation.z = Math.PI / 2;
            midRail.position.y = height / 2;
            group.add(midRail);

            group.position.set(x, 0, z);
            group.rotation.y = rotY;
            return group;
        }

        scene.add(createWall(CAGE_W, CAGE_H, 0, -CAGE_D / 2, 0));
        scene.add(createWall(CAGE_W, CAGE_H, 0, CAGE_D / 2, 0));
        scene.add(createWall(CAGE_D, CAGE_H, -CAGE_W / 2, 0, Math.PI / 2));
        scene.add(createWall(CAGE_D, CAGE_H, CAGE_W / 2, 0, Math.PI / 2));

        // --- WHEEL ---
        const wheelGroup = new THREE.Group();
        const wheelRadius = 0.8;

        // Wheel rim
        const rimGeo = new THREE.TorusGeometry(wheelRadius, 0.04, 6, 16);
        const rimMat = mat(0x44ccff);
        const rim = new THREE.Mesh(rimGeo, rimMat);
        wheelGroup.add(rim);

        // Spokes
        const spokeMat = mat(0x66ddff);
        for (let i = 0; i < 6; i++) {
            const spokeGeo = new THREE.CylinderGeometry(0.02, 0.02, wheelRadius * 2, 4);
            const spoke = new THREE.Mesh(spokeGeo, spokeMat);
            spoke.rotation.z = (i / 6) * Math.PI;
            wheelGroup.add(spoke);
        }

        // Center hub
        const hubGeo = new THREE.SphereGeometry(0.08, 6, 4);
        const hub = new THREE.Mesh(hubGeo, mat(0xffffff));
        wheelGroup.add(hub);

        // Stand
        const standMat = mat(0x8888aa);
        const standGeo = new THREE.CylinderGeometry(0.03, 0.04, 0.5, 6);
        const standL = new THREE.Mesh(standGeo, standMat);
        standL.position.set(0, -0.25, -wheelRadius - 0.1);
        wheelGroup.add(standL);
        const standR = new THREE.Mesh(standGeo, standMat);
        standR.position.set(0, -0.25, wheelRadius + 0.1);
        wheelGroup.add(standR);

        // Base bar
        const baseGeo = new THREE.CylinderGeometry(0.03, 0.03, wheelRadius * 2 + 0.3, 6);
        const baseBar = new THREE.Mesh(baseGeo, standMat);
        baseBar.rotation.x = Math.PI / 2;
        baseBar.position.y = -0.5;
        wheelGroup.add(baseBar);

        wheelGroup.position.set(2, 0.8, -1.5);
        scene.add(wheelGroup);

        let wheelSpeed = 0;
        let wheelTargetSpeed = 0;

        // --- FOOD BOWL ---
        const bowlGroup = new THREE.Group();
        const bowlGeo = new THREE.CylinderGeometry(0.3, 0.2, 0.15, 8);
        const bowl = new THREE.Mesh(bowlGeo, mat(0xff6644));
        bowl.position.y = 0.075;
        bowlGroup.add(bowl);

        // Seeds in bowl
        const seedColors = [0xffcc00, 0xff8800, 0xcc6600, 0x88cc44];
        for (let i = 0; i < 8; i++) {
            const seedGeo = new THREE.SphereGeometry(0.04, 4, 3);
            const seed = new THREE.Mesh(seedGeo, mat(seedColors[i % seedColors.length]));
            const angle = (i / 8) * Math.PI * 2;
            seed.position.set(Math.cos(angle) * 0.12, 0.14, Math.sin(angle) * 0.12);
            bowlGroup.add(seed);
        }

        bowlGroup.position.set(-2, 0, 1.5);
        scene.add(bowlGroup);

        // --- TUNNEL ---
        const tunnelGroup = new THREE.Group();
        const tunnelGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.5, 8, 1, true);
        const tunnelMat = new THREE.MeshLambertMaterial({
            color: 0xff88cc, flatShading: true, side: THREE.DoubleSide
        });
        const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
        tunnel.rotation.z = Math.PI / 2;
        tunnel.position.y = 0.3;
        tunnelGroup.add(tunnel);

        // Tunnel end caps (openings)
        const capGeo = new THREE.RingGeometry(0.2, 0.3, 8);
        const capMat = mat(0xdd66aa);
        const capL = new THREE.Mesh(capGeo, capMat);
        capL.position.set(-0.75, 0.3, 0);
        capL.rotation.y = Math.PI / 2;
        tunnelGroup.add(capL);
        const capR = new THREE.Mesh(capGeo, capMat);
        capR.position.set(0.75, 0.3, 0);
        capR.rotation.y = -Math.PI / 2;
        tunnelGroup.add(capR);

        tunnelGroup.position.set(-1, 0, -1);
        tunnelGroup.rotation.y = 0.3;
        scene.add(tunnelGroup);

        // --- HAMSTER FACTORY ---
        function createHamster(bodyColor, bellyColor, earColor) {
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(0.25, 6, 5);
            const body = new THREE.Mesh(bodyGeo, mat(bodyColor));
            body.position.y = 0.25;
            body.scale.set(1, 0.9, 1.2);
            body.castShadow = true;
            group.add(body);

            // Belly
            const bellyGeo = new THREE.SphereGeometry(0.18, 5, 4);
            const belly = new THREE.Mesh(bellyGeo, mat(bellyColor));
            belly.position.set(0, 0.2, 0.08);
            belly.scale.set(0.9, 0.8, 1);
            group.add(belly);

            // Head
            const headGeo = new THREE.SphereGeometry(0.16, 6, 5);
            const head = new THREE.Mesh(headGeo, mat(bodyColor));
            head.position.set(0, 0.35, 0.22);
            head.castShadow = true;
            group.add(head);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.04, 4, 3);
            const eyeMat = mat(0x222222);
            const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
            eyeL.position.set(-0.08, 0.38, 0.34);
            group.add(eyeL);
            const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
            eyeR.position.set(0.08, 0.38, 0.34);
            group.add(eyeR);

            // Eye shine
            const shineGeo = new THREE.SphereGeometry(0.015, 3, 2);
            const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const shineL = new THREE.Mesh(shineGeo, shineMat);
            shineL.position.set(-0.06, 0.4, 0.37);
            group.add(shineL);
            const shineR = new THREE.Mesh(shineGeo, shineMat);
            shineR.position.set(0.1, 0.4, 0.37);
            group.add(shineR);

            // Nose
            const noseGeo = new THREE.SphereGeometry(0.025, 4, 3);
            const nose = new THREE.Mesh(noseGeo, mat(0xff8888));
            nose.position.set(0, 0.33, 0.37);
            group.add(nose);

            // Ears
            const earGeo = new THREE.ConeGeometry(0.06, 0.1, 4);
            const earL = new THREE.Mesh(earGeo, mat(earColor));
            earL.position.set(-0.1, 0.48, 0.15);
            earL.rotation.z = 0.3;
            group.add(earL);
            const earR = new THREE.Mesh(earGeo, mat(earColor));
            earR.position.set(0.1, 0.48, 0.15);
            earR.rotation.z = -0.3;
            group.add(earR);

            // Inner ears
            const innerEarGeo = new THREE.ConeGeometry(0.035, 0.06, 4);
            const innerEarMat = mat(0xffaaaa);
            const innerEarL = new THREE.Mesh(innerEarGeo, innerEarMat);
            innerEarL.position.set(-0.1, 0.47, 0.18);
            innerEarL.rotation.z = 0.3;
            group.add(innerEarL);
            const innerEarR = new THREE.Mesh(innerEarGeo, innerEarMat);
            innerEarR.position.set(0.1, 0.47, 0.18);
            innerEarR.rotation.z = -0.3;
            group.add(innerEarR);

            // Feet (tiny)
            const footGeo = new THREE.SphereGeometry(0.04, 4, 3);
            const footMat = mat(0xffcccc);
            const positions = [[-0.1, 0.04, 0.15], [0.1, 0.04, 0.15], [-0.1, 0.04, -0.12], [0.1, 0.04, -0.12]];
            positions.forEach(p => {
                const foot = new THREE.Mesh(footGeo, footMat);
                foot.position.set(...p);
                foot.scale.set(1, 0.6, 1.2);
                group.add(foot);
            });

            // Tail (tiny nub)
            const tailGeo = new THREE.SphereGeometry(0.03, 3, 2);
            const tail = new THREE.Mesh(tailGeo, mat(bodyColor));
            tail.position.set(0, 0.22, -0.28);
            group.add(tail);

            return group;
        }

        // --- CREATE HAMSTERS ---
        const hamsterColors = [
            { body: 0xffb347, belly: 0xfff5e0, ear: 0xff8866 },  // Golden
            { body: 0xffffff, belly: 0xffeedd, ear: 0xffaaaa },    // White
            { body: 0xcc8844, belly: 0xffddaa, ear: 0xaa6633 },   // Brown
            { body: 0xff9966, belly: 0xffccaa, ear: 0xdd7744 },   // Orange
        ];

        const hamsters = [];
        const targetPoints = [
            { x: 2, z: -1.5, type: 'wheel' },
            { x: -2, z: 1.5, type: 'food' },
            { x: -1, z: -1, type: 'tunnel' },
            { x: 0, z: 0, type: 'roam' },
            { x: 1.5, z: 1, type: 'roam' },
            { x: -1.5, z: 0.5, type: 'roam' },
            { x: 0.5, z: -2, type: 'roam' },
        ];

        for (let i = 0; i < 4; i++) {
            const c = hamsterColors[i];
            const hamster = createHamster(c.body, c.belly, c.ear);
            hamster.position.set(
                (Math.random() - 0.5) * 3,
                0,
                (Math.random() - 0.5) * 3
            );
            scene.add(hamster);

            hamsters.push({
                mesh: hamster,
                state: 'idle',
                stateTimer: Math.random() * 2,
                target: null,
                speed: 0.5 + Math.random() * 0.3,
                walkPhase: Math.random() * Math.PI * 2,
                bobAmount: 0,
            });
        }

        // --- DECORATIVE ELEMENTS ---
        // Little platform
        const platGeo = new THREE.BoxGeometry(0.8, 0.1, 0.8);
        const plat = new THREE.Mesh(platGeo, mat(0x66aa44));
        plat.position.set(2, 0.05, 1.5);
        plat.castShadow = true;
        scene.add(plat);

        // Small ball toy
        const ballGeo = new THREE.IcosahedronGeometry(0.12, 0);
        const ball = new THREE.Mesh(ballGeo, mat(0xff44aa));
        ball.position.set(0.5, 0.12, 0.8);
        ball.castShadow = true;
        scene.add(ball);

        // --- ANIMATION ---
        const clock = new THREE.Clock();
        let elapsed = 0;

        function getNewTarget(h) {
            const available = targetPoints.filter(tp => {
                const dx = tp.x - h.mesh.position.x;
                const dz = tp.z - h.mesh.position.z;
                return Math.sqrt(dx * dx + dz * dz) > 0.5;
            });
            if (available.length === 0) return { x: (Math.random() - 0.5) * 4, z: (Math.random() - 0.5) * 3, type: 'roam' };
            return available[Math.floor(Math.random() * available.length)];
        }

        function updateHamster(h, dt) {
            h.stateTimer -= dt;

            switch (h.state) {
                case 'idle':
                    // Slight wobble
                    h.mesh.rotation.z = Math.sin(elapsed * 3 + h.walkPhase) * 0.05;
                    if (h.stateTimer <= 0) {
                        h.state = 'walking';
                        h.target = getNewTarget(h);
                        h.stateTimer = 3 + Math.random() * 4;
                    }
                    break;

                case 'walking': {
                    const dx = h.target.x - h.mesh.position.x;
                    const dz = h.target.z - h.mesh.position.z;
                    const dist = Math.sqrt(dx * dx + dz * dz);

                    if (dist < 0.2) {
                        // Arrived
                        if (h.target.type === 'wheel') {
                            h.state = 'wheel';
                            h.stateTimer = 3 + Math.random() * 3;
                            wheelTargetSpeed = 4;
                            // Position at wheel
                            h.mesh.position.set(2, 0, -1.5);
                            h.mesh.rotation.y = Math.PI;
                        } else if (h.target.type === 'food') {
                            h.state = 'eating';
                            h.stateTimer = 2 + Math.random() * 2;
                            h.mesh.position.set(-2, 0, 1.5);
                            h.mesh.rotation.y = Math.atan2(0 - (-2), 0 - 1.5);
                        } else if (h.target.type === 'tunnel') {
                            h.state = 'tunnel';
                            h.stateTimer = 2 + Math.random() * 2;
                        } else {
                            h.state = 'idle';
                            h.stateTimer = 1 + Math.random() * 3;
                        }
                    } else {
                        // Move toward target
                        const nx = dx / dist;
                        const nz = dz / dist;
                        h.mesh.position.x += nx * h.speed * dt;
                        h.mesh.position.z += nz * h.speed * dt;

                        // Face direction
                        const targetRot = Math.atan2(nx, nz);
                        let diff = targetRot - h.mesh.rotation.y;
                        while (diff > Math.PI) diff -= Math.PI * 2;
                        while (diff < -Math.PI) diff += Math.PI * 2;
                        h.mesh.rotation.y += diff * 5 * dt;

                        // Walk bob
                        h.walkPhase += dt * 10;
                        h.bobAmount = Math.sin(h.walkPhase) * 0.03;
                        h.mesh.position.y = h.bobAmount;
                        h.mesh.rotation.z = Math.sin(h.walkPhase) * 0.08;
                    }

                    // Clamp to cage bounds
                    h.mesh.position.x = THREE.MathUtils.clamp(h.mesh.position.x, -CAGE_W / 2 + 0.3, CAGE_W / 2 - 0.3);
                    h.mesh.position.z = THREE.MathUtils.clamp(h.mesh.position.z, -CAGE_D / 2 + 0.3, CAGE_D / 2 - 0.3);

                    if (h.stateTimer <= 0) {
                        h.state = 'idle';
                        h.stateTimer = 1 + Math.random() * 2;
                        h.mesh.position.y = 0;
                        h.mesh.rotation.z = 0;
                    }
                    break;
                }

                case 'wheel': {
                    // Spin in place
                    h.walkPhase += dt * 15;
                    h.mesh.position.y = Math.abs(Math.sin(h.walkPhase)) * 0.05;
                    h.mesh.rotation.z = Math.sin(h.walkPhase * 0.5) * 0.15;

                    if (h.stateTimer <= 0) {
                        h.state = 'idle';
                        h.stateTimer = 1 + Math.random() * 2;
                        h.mesh.position.y = 0;
                        h.mesh.rotation.z = 0;
                        wheelTargetSpeed = 0;
                    }
                    break;
                }

                case 'eating': {
                    // Nibble animation
                    h.walkPhase += dt * 8;
                    h.mesh.position.y = Math.abs(Math.sin(h.walkPhase)) * 0.02;
                    h.mesh.rotation.x = Math.sin(h.walkPhase) * 0.1;

                    if (h.stateTimer <= 0) {
                        h.state = 'idle';
                        h.stateTimer = 1 + Math.random() * 2;
                        h.mesh.position.y = 0;
                        h.mesh.rotation.x = 0;
                    }
                    break;
                }

                case 'tunnel': {
                    // Peek in and out
                    h.walkPhase += dt * 4;
                    const t = Math.sin(h.walkPhase * 0.5) * 0.3;
                    h.mesh.position.x = -1 + t * Math.cos(0.3);
                    h.mesh.position.z = -1 + t * Math.sin(0.3);
                    h.mesh.position.y = 0.02;

                    if (h.stateTimer <= 0) {
                        h.state = 'idle';
                        h.stateTimer = 1 + Math.random() * 2;
                        h.mesh.position.y = 0;
                    }
                    break;
                }
            }
        }

        // --- ANIMATE ---
        function animate() {
            requestAnimationFrame(animate);
            const dt = Math.min(clock.getDelta(), 0.05);
            elapsed += dt;

            // Update wheel
            wheelSpeed += (wheelTargetSpeed - wheelSpeed) * 3 * dt;
            wheelGroup.rotation.x += wheelSpeed * dt;

            // If no hamster is on wheel, slow down
            const anyOnWheel = hamsters.some(h => h.state === 'wheel');
            if (!anyOnWheel) wheelTargetSpeed = 0;

            // Update hamsters
            hamsters.forEach(h => updateHamster(h, dt));

            // Ball bounces gently
            ball.position.y = 0.12 + Math.abs(Math.sin(elapsed * 2)) * 0.05;
            ball.rotation.y += dt * 0.5;

            // Subtle light flicker
            pointLight.intensity = 0.4 + Math.sin(elapsed * 3) * 0.1;

            controls.update();
            renderer.render(scene, camera);
        }

        // --- RESIZE ---
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    </script>
</body>
</html>
```

## What's Included

| Element | Description |
|---------|-------------|
| **Cage** | Wire-frame walls with horizontal rails, wood-shaving floor |
| **4 Hamsters** | Golden, white, brown, and orange — each with eyes, ears, belly, feet, and tail |
| **Wheel** | Spinning exercise wheel that accelerates when a hamster uses it |
| **Food Bowl** | Red bowl with colorful seeds; hamsters stop to "eat" |
| **Tunnel** | Pink half-cylinder tunnel; hamsters peek in and out |
| **Ball Toy** | Bouncing pink icosahedron for visual interest |
| **Platform** | Small green platform for extra detail |

## Behavior System

Each hamster runs a simple state machine:
- **Idle** → wobbles in place, waits 1–3s
- **Walking** → picks a random target (wheel/food/tunnel/roam point), walks there with bobbing animation
- **Wheel** → spins in place, wheel accelerates
- **Eating** → nibbles at the bowl
- **Tunnel** → peeks in and out of the tunnel

## How to Run

Save as `index.html` and open in any modern browser. Drag to orbit, scroll to zoom. No build step needed — everything loads from CDN.