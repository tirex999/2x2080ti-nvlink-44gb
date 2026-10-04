

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
            top: 16px;
            left: 50%;
            transform: translateX(-50%);
            color: #fff;
            background: rgba(0,0,0,0.5);
            padding: 10px 24px;
            border-radius: 20px;
            font-size: 14px;
            pointer-events: none;
            backdrop-filter: blur(4px);
        }
        #info h1 { font-size: 18px; margin-bottom: 4px; }
        #info p { font-size: 12px; opacity: 0.8; }
    </style>
</head>
<body>
    <div id="info">
        <h1>🐹 Low-Poly Hamster Playground</h1>
        <p>Drag to rotate • Scroll to zoom • Watch them play!</p>
    </div>

    <script type="importmap">
    {
        "imports": {
            "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
            "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
        }
    }
    </script>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

        // ─── SCENE SETUP ───────────────────────────────────────────────
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB);
        scene.fog = new THREE.Fog(0x87CEEB, 20, 40);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(8, 7, 10);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.target.set(0, 1.5, 0);
        controls.maxPolarAngle = Math.PI / 2.1;
        controls.minDistance = 5;
        controls.maxDistance = 20;

        // ─── LIGHTING ──────────────────────────────────────────────────
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xfff5e6, 1.2);
        dirLight.position.set(5, 10, 5);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.set(2048, 2048);
        dirLight.shadow.camera.near = 1;
        dirLight.shadow.camera.far = 30;
        dirLight.shadow.camera.left = -8;
        dirLight.shadow.camera.right = 8;
        dirLight.shadow.camera.top = 8;
        dirLight.shadow.camera.bottom = -8;
        scene.add(dirLight);

        const fillLight = new THREE.DirectionalLight(0xb0d4ff, 0.3);
        fillLight.position.set(-3, 5, -5);
        scene.add(fillLight);

        // ─── MATERIALS ─────────────────────────────────────────────────
        const mat = {
            wood: new THREE.MeshLambertMaterial({ color: 0xDEB887 }),
            woodDark: new THREE.MeshLambertMaterial({ color: 0xA0722D }),
            wire: new THREE.MeshLambertMaterial({ color: 0xC0C0C0 }),
            sand: new THREE.MeshLambertMaterial({ color: 0xF5DEB3 }),
            grass: new THREE.MeshLambertMaterial({ color: 0x90EE90 }),
            bowl: new THREE.MeshLambertMaterial({ color: 0xFF6B6B }),
            food: new THREE.MeshLambertMaterial({ color: 0xFFA500 }),
            wheel: new THREE.MeshLambertMaterial({ color: 0x6EC6FF }),
            wheelFrame: new THREE.MeshLambertMaterial({ color: 0x4A90D9 }),
            tunnel: new THREE.MeshLambertMaterial({ color: 0xFFB347 }),
            water: new THREE.MeshLambertMaterial({ color: 0x87CEEB }),
        };

        // ─── CAGE CONSTRUCTION ─────────────────────────────────────────
        const CAGE_W = 8, CAGE_H = 4, CAGE_D = 6;

        function buildCage() {
            const group = new THREE.Group();

            // Floor tray
            const floor = new THREE.Mesh(
                new THREE.BoxGeometry(CAGE_W, 0.3, CAGE_D),
                mat.wood
            );
            floor.position.y = 0.15;
            floor.receiveShadow = true;
            group.add(floor);

            // Sand bedding
            const sand = new THREE.Mesh(
                new THREE.BoxGeometry(CAGE_W - 0.4, 0.15, CAGE_D - 0.4),
                mat.sand
            );
            sand.position.y = 0.37;
            sand.receiveShadow = true;
            group.add(sand);

            // Wooden frame posts
            const postGeo = new THREE.BoxGeometry(0.2, CAGE_H, 0.2);
            const positions = [
                [-CAGE_W/2, CAGE_H/2, -CAGE_D/2],
                [CAGE_W/2, CAGE_H/2, -CAGE_D/2],
                [-CAGE_W/2, CAGE_H/2, CAGE_D/2],
                [CAGE_W/2, CAGE_H/2, CAGE_D/2]
            ];
            positions.forEach(p => {
                const post = new THREE.Mesh(postGeo, mat.woodDark);
                post.position.set(...p);
                post.castShadow = true;
                group.add(post);
            });

            // Top frame beams
            const beamH = new THREE.BoxGeometry(CAGE_W, 0.15, 0.15);
            const beamV = new THREE.BoxGeometry(0.15, 0.15, CAGE_D);
            [[-CAGE_D/2],[CAGE_D/2]].forEach(([z]) => {
                const b = new THREE.Mesh(beamH, mat.woodDark);
                b.position.set(0, CAGE_H, z);
                group.add(b);
            });
            [[-CAGE_W/2],[CAGE_W/2]].forEach(([x]) => {
                const b = new THREE.Mesh(beamV, mat.woodDark);
                b.position.set(x, CAGE_H, 0);
                group.add(b);
            });

            // Wire mesh walls (front and back)
            const wireMat = new THREE.MeshBasicMaterial({ color: 0xD0D0D0, wireframe: true });
            const wallGeo = new THREE.PlaneGeometry(CAGE_W, CAGE_H, 12, 6);
            
            const frontWall = new THREE.Mesh(wallGeo, wireMat);
            frontWall.position.set(0, CAGE_H/2 + 0.3, CAGE_D/2);
            group.add(frontWall);

            const backWall = new THREE.Mesh(wallGeo, wireMat);
            backWall.position.set(0, CAGE_H/2 + 0.3, -CAGE_D/2);
            group.add(backWall);

            // Side walls
            const sideGeo = new THREE.PlaneGeometry(CAGE_D, CAGE_H, 8, 6);
            const leftWall = new THREE.Mesh(sideGeo, wireMat);
            leftWall.rotation.y = Math.PI / 2;
            leftWall.position.set(-CAGE_W/2, CAGE_H/2 + 0.3, 0);
            group.add(leftWall);

            const rightWall = new THREE.Mesh(sideGeo, wireMat);
            rightWall.rotation.y = Math.PI / 2;
            rightWall.position.set(CAGE_W/2, CAGE_H/2 + 0.3, 0);
            group.add(rightWall);

            // Top (open - no roof for visibility)
            return group;
        }

        scene.add(buildCage());

        // ─── INTERACTIVE OBJECTS ───────────────────────────────────────

        // Running Wheel
        const wheelGroup = new THREE.Group();
        const wheelRadius = 1.0;
        const wheelSegments = 16;

        // Wheel rim
        const rimGeo = new THREE.TorusGeometry(wheelRadius, 0.06, 8, wheelSegments);
        const rim = new THREE.Mesh(rimGeo, mat.wheel);
        rim.castShadow = true;
        wheelGroup.add(rim);

        // Wheel spokes
        const spokeGeo = new THREE.CylinderGeometry(0.03, 0.03, wheelRadius * 2, 6);
        for (let i = 0; i < 6; i++) {
            const spoke = new THREE.Mesh(spokeGeo, mat.wheel);
            spoke.rotation.z = (i / 6) * Math.PI;
            spoke.castShadow = true;
            wheelGroup.add(spoke);
        }

        // Wheel stand
        const standGeo = new THREE.CylinderGeometry(0.08, 0.12, 0.8, 8);
        const stand = new THREE.Mesh(standGeo, mat.wheelFrame);
        stand.position.set(0, -wheelRadius - 0.4, 0);
        stand.castShadow = true;
        wheelGroup.add(stand);

        const baseGeo = new THREE.CylinderGeometry(0.3, 0.35, 0.1, 8);
        const base = new THREE.Mesh(baseGeo, mat.wheelFrame);
        base.position.set(0, -wheelRadius - 0.8, 0);
        base.castShadow = true;
        wheelGroup.add(base);

        wheelGroup.position.set(-2.8, 1.5, 0);
        wheelGroup.rotation.y = Math.PI / 2;
        scene.add(wheelGroup);

        // Food Bowl
        const bowlGroup = new THREE.Group();
        const bowlGeo = new THREE.SphereGeometry(0.4, 8, 6, 0, Math.PI * 2, 0, Math.PI / 2);
        const bowl = new THREE.Mesh(bowlGeo, mat.bowl);
        bowl.rotation.x = Math.PI;
        bowl.castShadow = true;
        bowlGroup.add(bowl);

        // Food pellets
        const pelletGeo = new THREE.SphereGeometry(0.08, 5, 4);
        for (let i = 0; i < 6; i++) {
            const pellet = new THREE.Mesh(pelletGeo, mat.food);
            pellet.position.set(
                (Math.random() - 0.5) * 0.3,
                0.05,
                (Math.random() - 0.5) * 0.3
            );
            pellet.scale.setScalar(0.8 + Math.random() * 0.4);
            bowlGroup.add(pellet);
        }

        bowlGroup.position.set(2.5, 0.45, 1.5);
        scene.add(bowlGroup);

        // Tunnel
        const tunnelGroup = new THREE.Group();
        const tunnelGeo = new THREE.CylinderGeometry(0.4, 0.4, 2.5, 8, 1, true, 0, Math.PI);
        const tunnel = new THREE.Mesh(tunnelGeo, mat.tunnel);
        tunnel.rotation.z = Math.PI / 2;
        tunnel.castShadow = true;
        tunnelGroup.add(tunnel);

        // Tunnel ends (rings)
        const ringGeo = new THREE.TorusGeometry(0.4, 0.05, 6, 8);
        const ring1 = new THREE.Mesh(ringGeo, mat.tunnel);
        ring1.position.x = 1.25;
        ring1.rotation.y = Math.PI / 2;
        tunnelGroup.add(ring1);
        const ring2 = new THREE.Mesh(ringGeo, mat.tunnel);
        ring2.position.x = -1.25;
        ring2.rotation.y = Math.PI / 2;
        tunnelGroup.add(ring2);

        tunnelGroup.position.set(0, 0.85, -1.5);
        scene.add(tunnelGroup);

        // Water bottle
        const bottleGroup = new THREE.Group();
        const bottleBody = new THREE.Mesh(
            new THREE.CylinderGeometry(0.15, 0.15, 0.5, 8),
            new THREE.MeshLambertMaterial({ color: 0xB0E0FF, transparent: true, opacity: 0.7 })
        );
        bottleBody.castShadow = true;
        bottleGroup.add(bottleBody);

        const nozzle = new THREE.Mesh(
            new THREE.ConeGeometry(0.08, 0.2, 6),
            mat.wire
        );
        nozzle.position.y = -0.35;
        nozzle.rotation.x = Math.PI;
        bottleGroup.add(nozzle);

        bottleGroup.position.set(3.5, 2.0, -2.0);
        scene.add(bottleGroup);

        // Small grass tufts
        const grassGeo = new THREE.ConeGeometry(0.08, 0.3, 4);
        for (let i = 0; i < 12; i++) {
            const tuft = new THREE.Mesh(grassGeo, mat.grass);
            tuft.position.set(
                (Math.random() - 0.5) * (CAGE_W - 1),
                0.5,
                (Math.random() - 0.5) * (CAGE_D - 1)
            );
            tuft.rotation.y = Math.random() * Math.PI;
            tuft.castShadow = true;
            scene.add(tuft);
        }

        // ─── HAMSTER FACTORY ───────────────────────────────────────────

        const HAMSTER_COLORS = [
            { body: 0xFFB347, belly: 0xFFF5E1, ear: 0xFF8C69 },  // Golden
            { body: 0xF5F5DC, belly: 0xFFFFFF, ear: 0xFFB6C1 },  // White
            { body: 0xC68642, belly: 0xDEB887, ear: 0x8B4513 },  // Brown
            { body: 0xD3D3D3, belly: 0xF0F0F0, ear: 0x999999 },  // Grey
            { body: 0xFF69B4, belly: 0xFFB6C1, ear: 0xFF1493 },  // Pink (funny!)
        ];

        function createHamster(colorIdx) {
            const c = HAMSTER_COLORS[colorIdx % HAMSTER_COLORS.length];
            const group = new THREE.Group();

            const bodyMat = new THREE.MeshLambertMaterial({ color: c.body });
            const bellyMat = new THREE.MeshLambertMaterial({ color: c.belly });
            const earMat = new THREE.MeshLambertMaterial({ color: c.ear });
            const eyeMat = new THREE.MeshLambertMaterial({ color: 0x1a1a1a });
            const noseMat = new THREE.MeshLambertMaterial({ color: 0xFF69B4 });

            // Body (elongated sphere)
            const body = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), bodyMat);
            body.scale.set(1, 0.85, 1.3);
            body.position.y = 0.3;
            body.castShadow = true;
            group.add(body);

            // Belly patch
            const belly = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 4), bellyMat);
            belly.scale.set(0.9, 0.7, 1.1);
            belly.position.set(0, 0.25, 0.05);
            group.add(belly);

            // Head
            const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), bodyMat);
            head.position.set(0, 0.42, 0.3);
            head.castShadow = true;
            group.add(head);

            // Cheeks (big round cheeks - very hamster)
            const cheekGeo = new THREE.SphereGeometry(0.12, 6, 4);
            const cheekL = new THREE.Mesh(cheekGeo, bellyMat);
            cheekL.position.set(-0.15, 0.35, 0.38);
            cheekL.scale.set(1, 0.8, 0.9);
            group.add(cheekL);
            const cheekR = new THREE.Mesh(cheekGeo, bellyMat);
            cheekR.position.set(0.15, 0.35, 0.38);
            cheekR.scale.set(1, 0.8, 0.9);
            group.add(cheekR);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.04, 6, 4);
            const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
            eyeL.position.set(-0.09, 0.48, 0.46);
            group.add(eyeL);
            const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
            eyeR.position.set(0.09, 0.48, 0.46);
            group.add(eyeR);

            // Eye shine
            const shineGeo = new THREE.SphereGeometry(0.015, 4, 3);
            const shineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const shineL = new THREE.Mesh(shineGeo, shineMat);
            shineL.position.set(-0.08, 0.5, 0.49);
            group.add(shineL);
            const shineR = new THREE.Mesh(shineGeo, shineMat);
            shineR.position.set(0.1, 0.5, 0.49);
            group.add(shineR);

            // Nose
            const nose = new THREE.Mesh(new THREE.SphereGeometry(0.03, 5, 4), noseMat);
            nose.position.set(0, 0.42, 0.52);
            group.add(nose);

            // Ears
            const earGeo = new THREE.ConeGeometry(0.07, 0.12, 5);
            const earL = new THREE.Mesh(earGeo, earMat);
            earL.position.set(-0.12, 0.6, 0.25);
            earL.rotation.z = 0.3;
            earL.castShadow = true;
            group.add(earL);
            const earR = new THREE.Mesh(earGeo, earMat);
            earR.position.set(0.12, 0.6, 0.25);
            earR.rotation.z = -0.3;
            earR.castShadow = true;
            group.add(earR);

            // Legs (stubby)
            const legGeo = new THREE.CylinderGeometry(0.04, 0.05, 0.12, 5);
            const legPositions = [
                [-0.12, 0.08, 0.2], [0.12, 0.08, 0.2],
                [-0.12, 0.08, -0.2], [0.12, 0.08, -0.2]
            ];
            const legs = [];
            legPositions.forEach(p => {
                const leg = new THREE.Mesh(legGeo, bodyMat);
                leg.position.set(...p);
                leg.castShadow = true;
                group.add(leg);
                legs.push(leg);
            });

            // Tiny tail
            const tail = new THREE.Mesh(new THREE.SphereGeometry(0.05, 5, 4), bodyMat);
            tail.position.set(0, 0.3, -0.42);
            tail.scale.set(0.8, 0.6, 1.2);
            group.add(tail);

            return { group, legs, body, head, cheeks: [cheekL, cheekR] };
        }

        // ─── HAMSTER BEHAVIOR SYSTEM ───────────────────────────────────

        const STATES = { WALKING: 0, PAUSED: 1, TURNING: 2, EATING: 3, RUNNING_WHEEL: 4, HIDE_TUNNEL: 5 };

        class Hamster {
            constructor(colorIdx, startPos) {
                const h = createHamster(colorIdx);
                this.group = h.group;
                this.legs = h.legs;
                this.body = h.body;
                this.head = h.head;
                this.cheeks = h.cheeks;
                this.group.position.copy(startPos);
                this.group.position.y = 0.45;

                this.state = STATES.WALKING;
                this.stateTimer = 0;
                this.speed = 0.3 + Math.random() * 0.3;
                this.heading = Math.random() * Math.PI * 2;
                this.turnSpeed = 0;
                this.walkCycle = 0;
                this.bobAmount = 0;
                this.name = `Hamster ${colorIdx + 1}`;

                // Boundaries
                this.bounds = { x: CAGE_W/2 - 0.5, z: CAGE_D/2 - 0.5 };

                scene.add(this.group);
            }

            update(dt) {
                this.stateTimer -= dt;
                this.walkCycle += dt * 8;

                switch (this.state) {
                    case STATES.WALKING:
                        this.doWalk(dt);
                        break;
                    case STATES.PAUSED:
                        this.doPause(dt);
                        break;
                    case STATES.TURNING:
                        this.doTurn(dt);
                        break;
                    case STATES.EATING:
                        this.doEat(dt);
                        break;
                    case STATES.RUNNING_WHEEL:
                        this.doRunWheel(dt);
                        break;
                    case STATES.HIDE_TUNNEL:
                        this.doHideTunnel(dt);
                        break;
                }

                // Bob animation
                const bob = Math.sin(this.walkCycle) * 0.03 * (this.state === STATES.WALKING || this.state === STATES.RUNNING_WHEEL ? 1 : 0.2);
                this.group.position.y = 0.45 + bob;

                // Leg animation
                if (this.state === STATES.WALKING || this.state === STATES.RUNNING_WHEEL) {
                    const swing = Math.sin(this.walkCycle) * 0.3;
                    this.legs[0].rotation.x = swing;
                    this.legs[3].rotation.x = swing;
                    this.legs[1].rotation.x = -swing;
                    this.legs[2].rotation.x = -swing;
                } else {
                    this.legs.forEach(l => l.rotation.x *= 0.9);
                }

                // Squish animation when paused
                if (this.state === STATES.PAUSED) {
                    const squish = 1 + Math.sin(this.walkCycle * 0.5) * 0.05;
                    this.body.scale.y = 0.85 * squish;
                } else {
                    this.body.scale.y = 0.85;
                }
            }

            doWalk(dt) {
                this.group.position.x += Math.sin(this.heading) * this.speed * dt;
                this.group.position.z += Math.cos(this.heading) * this.speed * dt;
                this.group.rotation.y = this.heading;

                // Bounce off walls
                if (Math.abs(this.group.position.x) > this.bounds.x) {
                    this.group.position.x = Math.sign(this.group.position.x) * this.bounds.x;
                    this.heading = Math.PI - this.heading;
                }
                if (Math.abs(this.group.position.z) > this.bounds.z) {
                    this.group.position.z = Math.sign(this.group.position.z) * this.bounds.z;
                    this.heading = -this.heading;
                }

                if (this.stateTimer <= 0) {
                    this.nextState();
                }
            }

            doPause(dt) {
                // Slight idle wobble
                this.group.rotation.y += Math.sin(this.walkCycle * 0.3) * 0.002;
                if (this.stateTimer <= 0) {
                    this.nextState();
                }
            }

            doTurn(dt) {
                this.group.rotation.y += this.turnSpeed * dt;
                if (this.stateTimer <= 0) {
                    this.state = STATES.WALKING;
                    this.stateTimer = 1 + Math.random() * 2;
                }
            }

            doEat(dt) {
                // Move toward bowl
                const target = new THREE.Vector3(2.5, 0.45, 1.5);
                const dir = target.clone().sub(this.group.position);
                dir.y = 0;
                const dist = dir.length();

                if (dist > 0.5) {
                    dir.normalize();
                    this.group.position.add(dir.multiplyScalar(this.speed * 0.5 * dt));
                    this.group.rotation.y = Math.atan2(dir.x, dir.z);
                } else {
                    // Eating - chew animation (cheeks puff up)
                    const chew = Math.sin(this.walkCycle * 2) * 0.3 + 0.3;
                    this.cheeks[0].scale.setScalar(1 + chew);
                    this.cheeks[1].scale.setScalar(1 + chew);
                    this.group.rotation.y = Math.atan2(
                        2.5 - this.group.position.x,
                        1.5 - this.group.position.z
                    );
                }

                if (this.stateTimer <= 0) {
                    this.cheeks[0].scale.set(1, 0.8, 0.9);
                    this.cheeks[1].scale.set(1, 0.8, 0.9);
                    this.nextState();
                }
            }

            doRunWheel(dt) {
                // Position at wheel
                const wheelPos = new THREE.Vector3(-2.8, 1.5, 0);
                this.group.position.lerp(wheelPos, 0.05);
                this.group.rotation.y = Math.PI / 2;

                // Spin the wheel
                wheelGroup.rotation.x += dt * 5;

                // Fast leg movement
                this.walkCycle += dt * 10;

                if (this.stateTimer <= 0) {
                    this.group.position.set(
                        -2 + Math.random() * 2,
                        0.45,
                        (Math.random() - 0.5) * 3
                    );
                    this.nextState();
                }
            }

            doHideTunnel(dt) {
                const tunnelPos = new THREE.Vector3(0, 0.85, -1.5);
                const dir = tunnelPos.clone().sub(this.group.position);
                dir.y = 0;
                const dist = dir.length();

                if (dist > 0.3) {
                    dir.normalize();
                    this.group.position.add(dir.multiplyScalar(this.speed * 0.4 * dt));
                    this.group.rotation.y = Math.atan2(dir.x, dir.z);
                } else {
                    // Peek out animation
                    const peek = Math.sin(this.walkCycle * 0.8) * 0.5 + 0.5;
                    this.head.position.z = 0.3 + peek * 0.15;
                }

                if (this.stateTimer <= 0) {
                    this.head.position.z = 0.3;
                    this.nextState();
                }
            }

            nextState() {
                const roll = Math.random();
                if (roll < 0.4) {
                    this.state = STATES.WALKING;
                    this.stateTimer = 1.5 + Math.random() * 2;
                    this.heading = Math.random() * Math.PI * 2;
                } else if (roll < 0.6) {
                    this.state = STATES.PAUSED;
                    this.stateTimer = 1 + Math.random() * 2;
                } else if (roll < 0.75) {
                    this.state = STATES.TURNING;
                    this.stateTimer = 0.5 + Math.random() * 0.5;
                    this.turnSpeed = (Math.random() - 0.5) * 4;
                } else if (roll < 0.87) {
                    this.state = STATES.EATING;
                    this.stateTimer = 2 + Math.random() * 2;
                } else if (roll < 0.95) {
                    this.state = STATES.RUNNING_WHEEL;
                    this.stateTimer = 2 + Math.random() * 3;
                } else {
                    this.state = STATES.HIDE_TUNNEL;
                    this.stateTimer = 2 + Math.random() * 2;
                }
            }
        }

        // ─── CREATE HAMSTERS ───────────────────────────────────────────
        const hamsters = [];
        const startPositions = [
            new THREE.Vector3(-1, 0.45, 1),
            new THREE.Vector3(1.5, 0.45, -1),
            new THREE.Vector3(0, 0.45, 2),
            new THREE.Vector3(-2, 0.45, -1.5),
            new THREE.Vector3(2, 0.45, 0.5),
        ];

        for (let i = 0; i < 5; i++) {
            hamsters.push(new Hamster(i, startPositions[i]));
        }

        // ─── GROUND PLANE (outside cage) ───────────────────────────────
        const groundGeo = new THREE.PlaneGeometry(40, 40);
        const groundMat = new THREE.MeshLambertMaterial({ color: 0x7EC850 });
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.01;
        ground.receiveShadow = true;
        scene.add(ground);

        // Decorative clouds
        const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
        function makeCloud(x, y, z) {
            const g = new THREE.Group();
            for (let i = 0; i < 4; i++) {
                const s = new THREE.Mesh(new THREE.SphereGeometry(0.3 + Math.random() * 0.3, 6, 4), cloudMat);
                s.position.set(i * 0.4 - 0.6, Math.random() * 0.15, Math.random() * 0.2);
                s.scale.y = 0.6;
                g.add(s);
            }
            g.position.set(x, y, z);
            scene.add(g);
            return g;
        }
        const clouds = [makeCloud(-6, 6, -4), makeCloud(5, 7, -6), makeCloud(0, 6.5, 5)];

        // ─── ANIMATION LOOP ────────────────────────────────────────────
        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const dt = Math.min(clock.getDelta(), 0.05);

            // Update hamsters
            hamsters.forEach(h => h.update(dt));

            // Animate clouds
            clouds.forEach((c, i) => {
                c.position.x += dt * 0.1 * (i + 1);
                if (c.position.x > 12) c.position.x = -12;
            });

            // Subtle wheel idle spin
            if (!hamsters.some(h => h.state === STATES.RUNNING_WHEEL)) {
                wheelGroup.rotation.x += dt * 0.1;
            }

            controls.update();
            renderer.render(scene, camera);
        }

        animate();

        // ─── RESIZE HANDLER ────────────────────────────────────────────
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```

## What You Get

| Feature | Details |
|---------|---------|
| **5 Cute Hamsters** | Golden, White, Brown, Grey, and a silly Pink one — each with big cheeks, shiny eyes, stubby legs, and a tiny tail |
| **Running Wheel** | Spins when a hamster decides to run in it; legs animate fast |
| **Food Bowl** | Hamsters walk over, face it, and their cheeks puff up while "chewing" |
| **Tunnel** | Hamsters wander in and peek out with a head-poking animation |
| **Water Bottle** | Decorative element on the cage wall |
| **Autonomous AI** | State machine: Walk → Pause → Turn → Eat → Run Wheel → Hide in Tunnel (random weighted transitions) |
| **Visual Polish** | Soft shadows, fog, animated clouds, pastel palette, grass tufts, damped orbit controls |

Just save as `index.html` and open in any modern browser — no build step needed.