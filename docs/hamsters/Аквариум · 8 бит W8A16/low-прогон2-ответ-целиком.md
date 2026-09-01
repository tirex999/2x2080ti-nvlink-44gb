

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Аквариум</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a1628;
        }

        canvas {
            display: block;
        }

        .info-panel {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            max-width: 280px;
            z-index: 100;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .info-panel h1 {
            font-size: 22px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #e91e63, #ffb74d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        .info-panel p {
            font-size: 12px;
            line-height: 1.6;
            color: rgba(200, 220, 255, 0.8);
            margin-bottom: 8px;
        }

        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 14px;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b35, #f7c948);
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.6);
        }

        .btn-bubbles {
            background: linear-gradient(135deg, #42a5f5, #7c4dff);
            box-shadow: 0 4px 15px rgba(66, 165, 245, 0.4);
        }

        .btn-bubbles:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(66, 165, 245, 0.6);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd54f, #ff8a65);
            box-shadow: 0 4px 15px rgba(255, 213, 79, 0.4);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 213, 79, 0.6);
        }

        .stats-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 16px 20px;
            color: #e0f0ff;
            z-index: 100;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            min-width: 140px;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 13px;
        }

        .stat-item:last-child {
            margin-bottom: 0;
        }

        .stat-label {
            color: rgba(200, 220, 255, 0.7);
        }

        .stat-value {
            font-weight: 700;
            color: #64ffda;
            font-size: 15px;
        }

        @media (max-width: 768px) {
            .info-panel {
                max-width: 220px;
                padding: 14px;
            }
            .info-panel h1 {
                font-size: 18px;
            }
            .stats-panel {
                padding: 12px 14px;
            }
        }
    </style>
</head>
<body>
    <div class="info-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>🖱️ ЛКМ + движение — вращение<br>
           🖱️ ПКМ + движение — панорама<br>
           🖱️ Колесо — зум<br>
           🖱️ Клик по воде — кормление</p>
        <div class="btn-group">
            <button class="btn btn-fish" id="btnAddFish">+ Добавить рыбку</button>
            <button class="btn btn-bubbles" id="btnBubbles">+ Больше пузырей</button>
            <button class="btn btn-light" id="btnLight">💡 Свет: ВКЛ</button>
        </div>
    </div>

    <div class="stats-panel">
        <div class="stat-item">
            <span class="stat-label">Рыбки:</span>
            <span class="stat-value" id="fishCount">15</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">FPS:</span>
            <span class="stat-value" id="fpsCounter">60</span>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(0, 15, 45);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.body.appendChild(renderer.domElement);

        // === CONTROLS ===
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 5, 0);

        // === TANK DIMENSIONS ===
        const TANK_W = 36;
        const TANK_H = 24;
        const TANK_D = 20;
        const TANK_MIN_X = -TANK_W / 2 + 1;
        const TANK_MAX_X = TANK_W / 2 - 1;
        const TANK_MIN_Y = 1;
        const TANK_MAX_Y = TANK_H - 1;
        const TANK_MIN_Z = -TANK_D / 2 + 1;
        const TANK_MAX_Z = TANK_D / 2 - 1;

        // === LIGHTING ===
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 1.2);
        dirLight.position.set(10, 30, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 80;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 25;
        dirLight.shadow.camera.bottom = -25;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x4488ff, 0.8, 40);
        pointLight1.position.set(-10, 18, 0);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2266cc, 0.6, 35);
        pointLight2.position.set(10, 15, -5);
        scene.add(pointLight2);

        let lightOn = true;

        // === BACKGROUND GRADIENT ===
        const bgCanvas = document.createElement('canvas');
        bgCanvas.width = 2;
        bgCanvas.height = 512;
        const bgCtx = bgCanvas.getContext('2d');
        const gradient = bgCtx.createLinearGradient(0, 0, 0, 512);
        gradient.addColorStop(0, '#0a2a4a');
        gradient.addColorStop(0.5, '#0d3b6e');
        gradient.addColorStop(1, '#071a30');
        bgCtx.fillStyle = gradient;
        bgCtx.fillRect(0, 0, 2, 512);
        const bgTexture = new THREE.CanvasTexture(bgCanvas);
        scene.background = bgTexture;

        // === GLASS TANK ===
        function createTank() {
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccee,
                metalness: 0,
                roughness: 0.05,
                transmission: 0.95,
                thickness: 0.5,
                transparent: true,
                opacity: 0.15,
                side: THREE.DoubleSide
            });

            const tankGeo = new THREE.BoxGeometry(TANK_W, TANK_H, TANK_D);
            const tankMesh = new THREE.Mesh(tankGeo, glassMat);
            tankMesh.position.y = TANK_H / 2;
            scene.add(tankMesh);

            // Wireframe edges
            const edgesGeo = new THREE.EdgesGeometry(tankGeo);
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x66aadd, transparent: true, opacity: 0.4 });
            const edges = new THREE.LineSegments(edgesGeo, edgesMat);
            edges.position.y = TANK_H / 2;
            scene.add(edges);
        }
        createTank();

        // === SAND FLOOR ===
        function createSand() {
            const sandGeo = new THREE.PlaneGeometry(TANK_W - 1, TANK_D - 1, 32, 32);
            const positions = sandGeo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                const x = positions.getX(i);
                const y = positions.getY(i);
                const noise = Math.sin(x * 0.5) * Math.cos(y * 0.3) * 0.15 +
                              Math.sin(x * 1.2 + y * 0.8) * 0.08;
                positions.setZ(i, noise);
            }
            sandGeo.computeVertexNormals();

            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xc2a66b,
                roughness: 0.9,
                metalness: 0.05
            });
            const sand = new THREE.Mesh(sandGeo, sandMat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = 0.1;
            sand.receiveShadow = true;
            scene.add(sand);
        }
        createSand();

        // === ROCKS ===
        function createRocks() {
            const rockColors = [0x666666, 0x777777, 0x555555, 0x887766, 0x665544];
            for (let i = 0; i < 8; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const geo = new THREE.DodecahedronGeometry(size, 1);
                const pos = geo.attributes.position;
                for (let j = 0; j < pos.count; j++) {
                    const x = pos.getX(j);
                    const y = pos.getY(j);
                    const z = pos.getZ(j);
                    const scale = 0.8 + Math.random() * 0.4;
                    pos.setXYZ(j, x * scale, y * (0.6 + Math.random() * 0.3), z * scale);
                }
                geo.computeVertexNormals();

                const mat = new THREE.MeshStandardMaterial({
                    color: rockColors[Math.floor(Math.random() * rockColors.length)],
                    roughness: 0.85,
                    metalness: 0.1
                });
                const rock = new THREE.Mesh(geo, mat);
                rock.position.set(
                    (Math.random() - 0.5) * (TANK_W - 6),
                    size * 0.4,
                    (Math.random() - 0.5) * (TANK_D - 4)
                );
                rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
                rock.castShadow = true;
                rock.receiveShadow = true;
                scene.add(rock);
            }
        }
        createRocks();

        // === SEAWEED ===
        const seaweeds = [];
        function createSeaweed() {
            const colors = [0x2d8a4e, 0x3cb371, 0x228b22, 0x006400, 0x32cd32];
            for (let i = 0; i < 12; i++) {
                const height = 3 + Math.random() * 5;
                const segments = 8;
                const points = [];
                for (let j = 0; j <= segments; j++) {
                    const t = j / segments;
                    points.push(new THREE.Vector3(
                        Math.sin(t * 2) * 0.3,
                        t * height,
                        Math.cos(t * 3) * 0.2
                    ));
                }
                const curve = new THREE.CatmullRomCurve3(points);
                const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.15 + Math.random() * 0.1, 6, false);
                const mat = new THREE.MeshStandardMaterial({
                    color: colors[Math.floor(Math.random() * colors.length)],
                    roughness: 0.7,
                    side: THREE.DoubleSide
                });
                const seaweed = new THREE.Mesh(tubeGeo, mat);
                seaweed.position.set(
                    (Math.random() - 0.5) * (TANK_W - 8),
                    0.2,
                    (Math.random() - 0.5) * (TANK_D - 4)
                );
                seaweed.castShadow = true;
                scene.add(seaweed);
                seaweeds.push({ mesh: seaweed, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 });
            }
        }
        createSeaweed();

        // === FISH SYSTEM ===
        const fishArray = [];
        const colorSchemes = [
            { body: 0xff6b35, fin: 0xffaa00, name: 'orange' },
            { body: 0x2196f3, fin: 0x64b5f6, name: 'blue' },
            { body: 0xffeb3b, fin: 0xf44336, name: 'yellow-red' },
            { body: 0x9c27b0, fin: 0xce93d8, name: 'purple' },
            { body: 0xf44336, fin: 0xff8a65, name: 'red' },
            { body: 0x4caf50, fin: 0x81c784, name: 'green' },
            { body: 0xe91e63, fin: 0xf48fb1, name: 'pink' },
            { body: 0xffd700, fin: 0xffab00, name: 'gold' }
        ];

        function createFish(position) {
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(0.8, 16, 12);
            bodyGeo.scale(1.8, 1, 0.7);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.4,
                metalness: 0.3
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.12, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.06, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
            leftEye.position.set(0.9, 0.15, 0.35);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(0.95, 0.15, 0.38);
            group.add(leftEye, leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
            rightEye.position.set(0.9, 0.15, -0.35);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(0.95, 0.15, -0.38);
            group.add(rightEye, rightPupil);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.4, 0.8, 4);
            tailGeo.rotateX(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.85
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.5, 0, 0);
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.6, 3);
            topFinGeo.rotateZ(Math.PI);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                transparent: true,
                opacity: 0.7
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0, 0.7, 0);
            group.add(topFin);

            // Side fins
            const finGeo = new THREE.ConeGeometry(0.2, 0.5, 3);
            const leftFin = new THREE.Mesh(finGeo, topFinMat.clone());
            leftFin.position.set(0.2, -0.1, 0.5);
            leftFin.rotation.x = Math.PI / 4;
            group.add(leftFin);

            const rightFin = new THREE.Mesh(finGeo, topFinMat.clone());
            rightFin.position.set(0.2, -0.1, -0.5);
            rightFin.rotation.x = -Math.PI / 4;
            group.add(rightFin);

            group.scale.setScalar(scale);
            group.position.copy(position || new THREE.Vector3(
                (Math.random() - 0.5) * (TANK_W - 6),
                3 + Math.random() * (TANK_H - 8),
                (Math.random() - 0.5) * (TANK_D - 6)
            ));

            scene.add(group);

            const fish = {
                mesh: group,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                topFin: topFin,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 2,
                    (Math.random() - 0.5) * 0.5,
                    (Math.random() - 0.5) * 2
                ),
                speed: 2 + Math.random() * 2,
                tailSpeed: 4 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2.5 + Math.random() * 1.5,
                wanderTimer: Math.random() * 3,
                baseScale: scale
            };

            fishArray.push(fish);
            return fish;
        }

        // Create initial fish
        for (let i = 0; i < 15; i++) {
            createFish();
        }

        // === BUBBLES ===
        const bubbles = [];
        const bubbleGeo = new THREE.SphereGeometry(0.15, 8, 8);
        const bubbleMat = new THREE.MeshPhysicalMaterial({
            color: 0xaaddff,
            metalness: 0,
            roughness: 0,
            transmission: 0.9,
            transparent: true,
            opacity: 0.4,
            side: THREE.DoubleSide
        });

        function createBubble() {
            const mesh = new THREE.Mesh(bubbleGeo, bubbleMat);
            const scale = 0.5 + Math.random() * 1.5;
            mesh.scale.setScalar(scale);
            mesh.position.set(
                (Math.random() - 0.5) * (TANK_W - 4),
                1 + Math.random() * TANK_H,
                (Math.random() - 0.5) * (TANK_D - 4)
            );
            scene.add(mesh);
            bubbles.push({
                mesh: mesh,
                speed: 1 + Math.random() * 2,
                phase: Math.random() * Math.PI * 2,
                wobbleAmp: 0.3 + Math.random() * 0.5
            });
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // === FOOD SYSTEM ===
        const foods = [];
        const foodGeo = new THREE.SphereGeometry(0.2, 8, 8);
        const foodMat = new THREE.MeshStandardMaterial({ color: 0xff8844, emissive: 0x442200, roughness: 0.6 });

        function createFood(position) {
            const mesh = new THREE.Mesh(foodGeo, foodMat);
            mesh.position.copy(position);
            scene.add(mesh);
            foods.push({
                mesh: mesh,
                velocity: new THREE.Vector3(0, -1, 0),
                eaten: false
            });
        }

        // === RAYCASTER FOR CLICKING ===
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const clickPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
        const intersectPoint = new THREE.Vector3();

        renderer.domElement.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            // Intersect with a plane at the center of the tank
            const tankCenter = new THREE.Vector3(0, TANK_H / 2, 0);
            const planeNormal = camera.getWorldDirection(new THREE.Vector3()).negate();
            const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(planeNormal, tankCenter);

            if (raycaster.ray.intersectPlane(plane, intersectPoint)) {
                // Clamp to tank bounds
                intersectPoint.x = Math.max(TANK_MIN_X, Math.min(TANK_MAX_X, intersectPoint.x));
                intersectPoint.y = Math.max(TANK_MIN_Y + 2, Math.min(TANK_MAX_Y, intersectPoint.y));
                intersectPoint.z = Math.max(TANK_MIN_Z, Math.min(TANK_MAX_Z, intersectPoint.z));
                createFood(intersectPoint);
            }
        });

        // === UI BUTTONS ===
        document.getElementById('btnAddFish').addEventListener('click', () => {
            createFish();
            updateStats();
        });

        document.getElementById('btnBubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) createBubble();
        });

        document.getElementById('btnLight').addEventListener('click', function () {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.2 : 0.2;
            this.textContent = lightOn ? '💡 Свет: ВКЛ' : '💡 Свет: ВЫКЛ';
        });

        function updateStats() {
            document.getElementById('fishCount').textContent = fishArray.length;
        }

        // === ANIMATION LOOP ===
        const clock = new THREE.Clock();
        let frameCount = 0;
        let lastFpsUpdate = 0;

        function animate() {
            requestAnimationFrame(animate);
            const delta = Math.min(clock.getDelta(), 0.05);
            const time = clock.elapsedTime;

            // FPS counter
            frameCount++;
            if (time - lastFpsUpdate >= 0.5) {
                const fps = Math.round(frameCount / (time - lastFpsUpdate));
                document.getElementById('fpsCounter').textContent = fps;
                frameCount = 0;
                lastFpsUpdate = time;
            }

            // === UPDATE FISH ===
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Wander
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.velocity.x += (Math.random() - 0.5) * 1.5;
                    fish.velocity.y += (Math.random() - 0.5) * 0.5;
                    fish.velocity.z += (Math.random() - 0.5) * 1.5;
                    fish.wanderTimer = 2 + Math.random() * 4;
                }

                // Avoid other fish
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j].mesh.position;
                    const dx = pos.x - other.x;
                    const dy = pos.y - other.y;
                    const dz = pos.z - other.z;
                    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const force = (fish.avoidanceRadius - dist) / fish.avoidanceRadius;
                        fish.velocity.x += (dx / dist) * force * 3 * delta;
                        fish.velocity.y += (dy / dist) * force * 3 * delta;
                        fish.velocity.z += (dz / dist) * force * 3 * delta;
                    }
                }

                // Wall reflection
                const wallForce = 3;
                if (pos.x < TANK_MIN_X + 2) fish.velocity.x += wallForce * delta;
                if (pos.x > TANK_MAX_X - 2) fish.velocity.x -= wallForce * delta;
                if (pos.y < TANK_MIN_Y + 2) fish.velocity.y += wallForce * delta;
                if (pos.y > TANK_MAX_Y - 2) fish.velocity.y -= wallForce * delta;
                if (pos.z < TANK_MIN_Z + 2) fish.velocity.z += wallForce * delta;
                if (pos.z > TANK_MAX_Z - 2) fish.velocity.z -= wallForce * delta;

                // Seek food
                fish.targetFood = null;
                let closestDist = 15;
                for (let f = 0; f < foods.length; f++) {
                    if (foods[f].eaten) continue;
                    const fd = pos.distanceTo(foods[f].mesh.position);
                    if (fd < closestDist) {
                        closestDist = fd;
                        fish.targetFood = foods[f];
                    }
                }

                if (fish.targetFood) {
                    const foodPos = fish.targetFood.mesh.position;
                    const dir = new THREE.Vector3().subVectors(foodPos, pos).normalize();
                    fish.velocity.add(dir.multiplyScalar(4 * delta));

                    // Eat food
                    if (closestDist < 1.0) {
                        fish.targetFood.eaten = true;
                        const idx = foods.indexOf(fish.targetFood);
                        if (idx !== -1) {
                            scene.remove(foods[idx].mesh);
                            foods.splice(idx, 1);
                        }
                        // Grow
                        const newScale = fish.baseScale * 1.05;
                        fish.baseScale = Math.min(newScale, 2.0);
                        fish.mesh.scale.setScalar(fish.baseScale);
                    }
                }

                // Limit speed
                const speed = fish.velocity.length();
                const maxSpeed = fish.speed * (fish.targetFood ? 1.5 : 1);
                if (speed > maxSpeed) {
                    fish.velocity.multiplyScalar(maxSpeed / speed);
                }

                // Update position
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Orient fish in direction of movement
                if (speed > 0.1) {
                    const targetQuat = new THREE.Quaternion();
                    const lookAtMatrix = new THREE.Matrix4();
                    const forward = fish.velocity.clone().normalize();
                    const up = new THREE.Vector3(0, 1, 0);
                    const right = new THREE.Vector3().crossVectors(up, forward).normalize();
                    const actualUp = new THREE.Vector3().crossVectors(forward, right);
                    lookAtMatrix.makeBasis(right, actualUp, forward.negate());
                    targetQuat.setFromRotationMatrix(lookAtMatrix);
                    fish.mesh.quaternion.slerp(targetQuat, 3 * delta);
                }

                // Tail animation
                fish.phase += fish.tailSpeed * delta;
                fish.tail.rotation.y = Math.sin(fish.phase) * 0.5;
                fish.tail.rotation.x = Math.sin(fish.phase * 0.7) * 0.2;

                // Fin animation
                fish.leftFin.rotation.z = Math.sin(fish.phase * 0.8 + 0.5) * 0.3;
                fish.rightFin.rotation.z = Math.sin(fish.phase * 0.8 + 1.5) * 0.3;
                fish.topFin.rotation.z = Math.sin(fish.phase * 0.5) * 0.15;

                // Slight body undulation
                fish.mesh.children[0].rotation.z = Math.sin(fish.phase * 0.6) * 0.05;
            }

            // === UPDATE FOODS ===
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                if (food.eaten) continue;
                food.velocity.y -= 2 * delta; // gravity
                food.mesh.position.add(food.velocity.clone().multiplyScalar(delta));

                // Remove if hits bottom
                if (food.mesh.position.y < 0.5) {
                    scene.remove(food.mesh);
                    foods.splice(i, 1);
                }
            }

            // === UPDATE BUBBLES ===
            for (let i = 0; i < bubbles.length; i++) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * delta;
                b.mesh.position.x += Math.sin(time * 2 + b.phase) * b.wobbleAmp * delta;
                b.mesh.position.z += Math.cos(time * 1.5 + b.phase) * b.wobbleAmp * delta;

                if (b.mesh.position.y > TANK_H - 0.5) {
                    b.mesh.position.y = 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * (TANK_W - 4);
                    b.mesh.position.z = (Math.random() - 0.5) * (TANK_D - 4);
                }
            }

            // === UPDATE SEAWEED ===
            for (let i = 0; i < seaweeds.length; i++) {
                const s = seaweeds[i];
                s.mesh.rotation.x = Math.sin(time * s.speed + s.phase) * 0.08;
                s.mesh.rotation.z = Math.cos(time * s.speed * 0.7 + s.phase) * 0.06;
            }

            // === POINT LIGHT ANIMATION ===
            pointLight1.intensity = 0.6 + Math.sin(time * 0.5) * 0.2;
            pointLight2.intensity = 0.5 + Math.cos(time * 0.3) * 0.15;

            controls.update();
            renderer.render(scene, camera);
        }

        // === RESIZE HANDLER ===
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

## Что реализовано

### 🐠 Рыбки (15 шт.)
- Детализированная анатомия: вытянутое тело, глаза с зрачками, хвост, верхний и боковые плавники
- 8 цветовых схем (оранжевая, синяя, жёлто-красная, фиолетовая, красная, зелёная, розовая, золотая)
- Индивидуальный масштаб (0.6–1.2), скорость, фаза анимации

### 🧠 ИИ поведения
- **Избегание столкновений** — отталкивание при сближении
- **Отражение от стен** — плавная сила у границ
- **Случайное блуждание** — периодическое изменение курса
- **Преследование корма** — в радиусе 15 единиц
- **Рост** — +5% размера после поедания (максимум ×2)

### 🌊 Окружение
- Стеклянный аквариум с `transmission: 0.95` и wireframe-рамкой
- Песчаное дно с процедурными неровностями
- 8 деформированных камней (додекаэдры)
- 12 водорослей на `TubeGeometry` + `CatmullRomCurve3` с покачиванием

### 💭 Пузыри (30 шт.)
- Прозрачные сферы, движение вверх с синусоидальным покачиванием
- Сброс при достижении поверхности

### 🍽️ Кормление
- Клик → создание корма с гравитацией
- Рыбки плывут к еде, съедают при сближении < 1.0
- Корм исчезает при ударе о дно

### 💡 Освещение
- Ambient + Directional (тени 2048², PCFSoft)
- 2 пульсирующих PointLight (подводный эффект)
- Переключение основного света кнопкой

### 🎮 Управление
- OrbitControls с damping, ограничением зума (10–60) и угла
- Кнопки: добавить рыбку, +10 пузырей, свет вкл/выкл
- Панель статистики: количество рыбок + FPS