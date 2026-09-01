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
            background: linear-gradient(180deg, #0a1628 0%, #0d2137 50%, #0a3d5c 100%);
        }

        canvas {
            display: block;
        }

        .panel {
            position: absolute;
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            z-index: 100;
        }

        .info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        .info-panel h1 {
            font-size: 22px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #4dd0e1, #81c784);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .info-panel .instructions {
            font-size: 12px;
            line-height: 1.8;
            opacity: 0.85;
            margin-bottom: 16px;
        }

        .info-panel .instructions span {
            display: inline-block;
            background: rgba(100, 180, 255, 0.15);
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 4px;
            font-size: 11px;
        }

        .stats-panel {
            top: 20px;
            right: 20px;
            min-width: 160px;
            text-align: center;
        }

        .stats-panel .stat-item {
            margin-bottom: 8px;
            font-size: 14px;
        }

        .stats-panel .stat-value {
            font-size: 24px;
            font-weight: bold;
            background: linear-gradient(135deg, #ffd54f, #ffab40);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stats-panel .stat-label {
            font-size: 11px;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 12px;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
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
            background: linear-gradient(135deg, #ff7043, #ff5722);
            box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 87, 34, 0.6);
        }

        .btn-bubble {
            background: linear-gradient(135deg, #42a5f5, #1e88e5);
            box-shadow: 0 4px 15px rgba(30, 136, 229, 0.4);
        }

        .btn-bubble:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(30, 136, 229, 0.6);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd54f, #ffb300);
            box-shadow: 0 4px 15px rgba(255, 179, 0, 0.4);
            color: #333;
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 179, 0, 0.6);
        }

        .btn-light.off {
            background: linear-gradient(135deg, #546e7a, #37474f);
            color: #aaa;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .fps-counter {
            font-size: 11px;
            opacity: 0.6;
            margin-top: 4px;
        }

        @media (max-width: 768px) {
            .info-panel {
                max-width: 200px;
                padding: 14px;
            }
            .info-panel h1 {
                font-size: 16px;
            }
            .stats-panel {
                min-width: 120px;
                padding: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <div class="instructions">
            <span>ЛКМ</span> Вращение камеры<br>
            <span>ПКМ</span> Панорамирование<br>
            <span>Колесо</span> Зум<br>
            <span>Клик</span> Кормление рыбок
        </div>
        <div class="btn-group">
            <button class="btn btn-fish" id="btnAddFish">🐟 Добавить рыбку</button>
            <button class="btn btn-bubble" id="btnBubbles">💨 Больше пузырей</button>
            <button class="btn btn-light" id="btnLight">💡 Свет: ВКЛ</button>
        </div>
    </div>

    <div class="panel stats-panel">
        <div class="stat-item">
            <div class="stat-value" id="fishCount">15</div>
            <div class="stat-label">Рыбок</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" id="foodCount">0</div>
            <div class="stat-label">Корма</div>
        </div>
        <div class="fps-counter" id="fpsCounter">60 FPS</div>
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
        controls.dampingFactor = 0.08;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 5, 0);

        // === LIGHTING ===
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 1.2);
        dirLight.position.set(10, 30, 15);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 100;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 25;
        dirLight.shadow.camera.bottom = -25;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x4488ff, 0.8, 40);
        pointLight1.position.set(-10, 15, 0);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2266cc, 0.6, 40);
        pointLight2.position.set(10, 10, -5);
        scene.add(pointLight2);

        // === AQUARIUM DIMENSIONS ===
        const AQ_W = 36, AQ_H = 24, AQ_D = 20;
        const HALF_W = AQ_W / 2, HALF_H = AQ_H / 2, HALF_D = AQ_D / 2;

        // === GLASS CONTAINER ===
        function createAquarium() {
            const glassGeo = new THREE.BoxGeometry(AQ_W, AQ_H, AQ_D);
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccee,
                metalness: 0,
                roughness: 0,
                transmission: 0.95,
                thickness: 0.5,
                transparent: true,
                opacity: 0.15,
                side: THREE.DoubleSide
            });
            const glassBox = new THREE.Mesh(glassGeo, glassMat);
            glassBox.position.y = AQ_H / 2;
            scene.add(glassBox);

            // Wireframe edges
            const edges = new THREE.EdgesGeometry(glassGeo);
            const lineMat = new THREE.LineBasicMaterial({ color: 0x88ccee, transparent: true, opacity: 0.4 });
            const wireframe = new THREE.LineSegments(edges, lineMat);
            wireframe.position.copy(glassBox.position);
            scene.add(wireframe);
        }
        createAquarium();

        // === SAND BOTTOM ===
        function createSand() {
            const sandGeo = new THREE.PlaneGeometry(AQ_W - 1, AQ_D - 1, 40, 40);
            const posAttr = sandGeo.attributes.position;
            for (let i = 0; i < posAttr.count; i++) {
                const x = posAttr.getX(i);
                const y = posAttr.getY(i);
                const noise = Math.sin(x * 0.5) * Math.cos(y * 0.7) * 0.3 +
                              Math.sin(x * 1.2 + y * 0.8) * 0.15 +
                              Math.random() * 0.1;
                posAttr.setZ(i, noise);
            }
            sandGeo.computeVertexNormals();

            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xd4a855,
                roughness: 0.9,
                metalness: 0.05
            });
            const sand = new THREE.Mesh(sandGeo, sandMat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = 0.2;
            sand.receiveShadow = true;
            scene.add(sand);
        }
        createSand();

        // === ROCKS ===
        function createRocks() {
            for (let i = 0; i < 8; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const rockGeo = new THREE.DodecahedronGeometry(size, 1);
                const posAttr = rockGeo.attributes.position;
                for (let j = 0; j < posAttr.count; j++) {
                    const x = posAttr.getX(j);
                    const y = posAttr.getY(j);
                    const z = posAttr.getZ(j);
                    const deform = 1 + (Math.random() - 0.5) * 0.4;
                    posAttr.setXYZ(j, x * deform, y * deform * 0.7, z * deform);
                }
                rockGeo.computeVertexNormals();

                const gray = 0.3 + Math.random() * 0.3;
                const rockMat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color(gray, gray * 0.95, gray * 0.9),
                    roughness: 0.85,
                    metalness: 0.1
                });
                const rock = new THREE.Mesh(rockGeo, rockMat);
                rock.position.set(
                    (Math.random() - 0.5) * (AQ_W - 6),
                    size * 0.3,
                    (Math.random() - 0.5) * (AQ_D - 6)
                );
                rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
                rock.castShadow = true;
                rock.receiveShadow = true;
                scene.add(rock);
            }
        }
        createRocks();

        // === SEAWEEED ===
        const seaweeds = [];
        function createSeaweed() {
            for (let i = 0; i < 12; i++) {
                const height = 3 + Math.random() * 5;
                const segments = 8;
                const points = [];
                for (let j = 0; j <= segments; j++) {
                    const t = j / segments;
                    points.push(new THREE.Vector3(
                        Math.sin(t * Math.PI * 2) * 0.3,
                        t * height,
                        Math.cos(t * Math.PI * 1.5) * 0.2
                    ));
                }
                const curve = new THREE.CatmullRomCurve3(points);
                const tubeGeo = new THREE.TubeGeometry(curve, 16, 0.15 + Math.random() * 0.1, 6, false);

                const green = 0.3 + Math.random() * 0.3;
                const seaweedMat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color(0.1, green, 0.15),
                    roughness: 0.7,
                    side: THREE.DoubleSide
                });
                const seaweed = new THREE.Mesh(tubeGeo, seaweedMat);
                seaweed.position.set(
                    (Math.random() - 0.5) * (AQ_W - 8),
                    0.3,
                    (Math.random() - 0.5) * (AQ_D - 8)
                );
                seaweed.castShadow = true;
                scene.add(seaweed);
                seaweeds.push({
                    mesh: seaweed,
                    baseRotX: seaweed.rotation.x,
                    baseRotZ: seaweed.rotation.z,
                    phase: Math.random() * Math.PI * 2,
                    speed: 0.5 + Math.random() * 0.5
                });
            }
        }
        createSeaweed();

        // === FISH COLORS ===
        const FISH_COLORS = [
            { body: 0xff6600, fin: 0xff8833, name: 'orange' },
            { body: 0x2196f3, fin: 0x64b5f6, name: 'blue' },
            { body: 0xffeb3b, fin: 0xf44336, name: 'yellow-red' },
            { body: 0x9c27b0, fin: 0xba68c8, name: 'purple' },
            { body: 0xf44336, fin: 0xef5350, name: 'red' },
            { body: 0x4caf50, fin: 0x81c784, name: 'green' },
            { body: 0xe91e63, fin: 0xf48fb1, name: 'pink' },
            { body: 0xffc107, fin: 0xffd54f, name: 'gold' }
        ];

        // === FISH CREATION ===
        const fishArray = [];

        function createFish(colorIndex, scale) {
            const colors = FISH_COLORS[colorIndex % FISH_COLORS.length];
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.5, 0.8, 0.6);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: colors.body,
                roughness: 0.4,
                metalness: 0.3
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
            tailGeo.rotateX(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: colors.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.9
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.x = -1.5;
            tail.castShadow = true;
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 4);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: colors.fin,
                roughness: 0.5,
                transparent: true,
                opacity: 0.8
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0, 0.7, 0);
            topFin.rotation.z = Math.PI * 0.1;
            group.add(topFin);

            // Left fin
            const leftFinGeo = new THREE.ConeGeometry(0.25, 0.6, 4);
            leftFinGeo.rotateZ(Math.PI / 2);
            const leftFin = new THREE.Mesh(leftFinGeo, topFinMat.clone());
            leftFin.position.set(0.2, -0.2, -0.5);
            leftFin.rotation.x = -0.3;
            group.add(leftFin);

            // Right fin
            const rightFinGeo = new THREE.ConeGeometry(0.25, 0.6, 4);
            rightFinGeo.rotateZ(Math.PI / 2);
            const rightFin = new THREE.Mesh(rightFinGeo, topFinMat.clone());
            rightFin.position.set(0.2, -0.2, 0.5);
            rightFin.rotation.x = 0.3;
            group.add(rightFin);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.08, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
            leftEye.position.set(0.8, 0.2, -0.35);
            group.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(0.9, 0.2, -0.35);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
            rightEye.position.set(0.8, 0.2, 0.35);
            group.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(0.9, 0.2, 0.35);
            group.add(rightPupil);

            // Position fish randomly
            const sx = scale || (0.6 + Math.random() * 0.6);
            group.scale.setScalar(sx);
            group.position.set(
                (Math.random() - 0.5) * (AQ_W - 8),
                2 + Math.random() * (AQ_H - 6),
                (Math.random() - 0.5) * (AQ_D - 8)
            );

            scene.add(group);

            const fish = {
                mesh: group,
                tail: tail,
                topFin: topFin,
                leftFin: leftFin,
                rightFin: rightFin,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 2,
                    (Math.random() - 0.5) * 0.5,
                    (Math.random() - 0.5) * 2
                ),
                speed: 2 + Math.random() * 2,
                tailSpeed: 4 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2 + Math.random() * 1.5,
                wanderTimer: 0,
                wanderInterval: 2 + Math.random() * 3,
                currentScale: sx
            };
            fishArray.push(fish);
            return fish;
        }

        // Initial fish
        for (let i = 0; i < 15; i++) {
            createFish(i, 0.6 + Math.random() * 0.6);
        }

        // === BUBBLES ===
        const bubbles = [];
        function createBubble() {
            const size = 0.1 + Math.random() * 0.25;
            const bubbleGeo = new THREE.SphereGeometry(size, 8, 8);
            const bubbleMat = new THREE.MeshPhysicalMaterial({
                color: 0xaaddff,
                metalness: 0,
                roughness: 0,
                transmission: 0.9,
                transparent: true,
                opacity: 0.4,
                side: THREE.DoubleSide
            });
            const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
            bubble.position.set(
                (Math.random() - 0.5) * (AQ_W - 4),
                Math.random() * AQ_H,
                (Math.random() - 0.5) * (AQ_D - 4)
            );
            scene.add(bubble);
            bubbles.push({
                mesh: bubble,
                speed: 1 + Math.random() * 2,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 2 + Math.random() * 3,
                wobbleAmp: 0.3 + Math.random() * 0.5
            });
        }

        for (let i = 0; i < 30; i++) createBubble();

        // === FOOD SYSTEM ===
        const foodArray = [];
        const foodGeo = new THREE.SphereGeometry(0.2, 8, 8);
        const foodMat = new THREE.MeshStandardMaterial({ color: 0xff4444, roughness: 0.5 });

        function spawnFood(position) {
            const food = new THREE.Mesh(foodGeo, foodMat.clone());
            food.material.color.setHSL(0.05 + Math.random() * 0.1, 0.8, 0.5);
            food.position.copy(position);
            food.castShadow = true;
            scene.add(food);
            foodArray.push({
                mesh: food,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 0.5,
                    -1 - Math.random(),
                    (Math.random() - 0.5) * 0.5
                )
            });
            updateStats();
        }

        // === RAYCASTER FOR CLICKING ===
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const clickPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);

        renderer.domElement.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            // Create a plane at the center of the aquarium facing the camera
            const camDir = new THREE.Vector3();
            camera.getWorldDirection(camDir);
            const planeNormal = camDir.clone().negate();
            const planePoint = new THREE.Vector3(0, AQ_H / 2, 0);
            const plane = new THREE.Plane(planeNormal, -planeNormal.dot(planePoint));

            const intersection = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersection);

            if (intersection) {
                // Clamp to aquarium bounds
                intersection.x = THREE.MathUtils.clamp(intersection.x, -HALF_W + 2, HALF_W - 2);
                intersection.y = THREE.MathUtils.clamp(intersection.y, 2, AQ_H - 2);
                intersection.z = THREE.MathUtils.clamp(intersection.z, -HALF_D + 2, HALF_D - 2);
                spawnFood(intersection);
            }
        });

        // === FISH AI UPDATE ===
        function updateFish(dt, time) {
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Wander timer
                fish.wanderTimer += dt;
                if (fish.wanderTimer > fish.wanderInterval) {
                    fish.wanderTimer = 0;
                    fish.wanderInterval = 2 + Math.random() * 4;
                    fish.velocity.x += (Math.random() - 0.5) * 2;
                    fish.velocity.y += (Math.random() - 0.5) * 0.5;
                    fish.velocity.z += (Math.random() - 0.5) * 2;
                }

                // Food seeking
                let nearestFood = null;
                let nearestDist = Infinity;
                for (let f = 0; f < foodArray.length; f++) {
                    const d = pos.distanceTo(foodArray[f].mesh.position);
                    if (d < 15 && d < nearestDist) {
                        nearestDist = d;
                        nearestFood = foodArray[f];
                    }
                }

                if (nearestFood) {
                    const dir = new THREE.Vector3().subVectors(nearestFood.mesh.position, pos).normalize();
                    fish.velocity.lerp(dir.multiplyScalar(fish.speed * 1.5), 0.05);
                } else {
                    // Normalize velocity to maintain speed
                    const velLen = fish.velocity.length();
                    if (velLen > 0) {
                        fish.velocity.normalize().multiplyScalar(fish.speed);
                    }
                }

                // Collision avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j].mesh.position;
                    const dist = pos.distanceTo(other);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const away = new THREE.Vector3().subVectors(pos, other).normalize();
                        const force = (fish.avoidanceRadius - dist) / fish.avoidanceRadius;
                        fish.velocity.add(away.multiplyScalar(force * 3 * dt));
                    }
                }

                // Wall reflection (soft)
                const margin = 2;
                if (pos.x > HALF_W - margin) fish.velocity.x -= (pos.x - (HALF_W - margin)) * 2 * dt;
                if (pos.x < -HALF_W + margin) fish.velocity.x -= (pos.x + HALF_W - margin) * 2 * dt;
                if (pos.y > AQ_H - margin) fish.velocity.y -= (pos.y - (AQ_H - margin)) * 2 * dt;
                if (pos.y < margin) fish.velocity.y -= (pos.y - margin) * 2 * dt;
                if (pos.z > HALF_D - margin) fish.velocity.z -= (pos.z - (HALF_D - margin)) * 2 * dt;
                if (pos.z < -HALF_D + margin) fish.velocity.z -= (pos.z + HALF_D - margin) * 2 * dt;

                // Clamp velocity
                const maxSpeed = fish.speed * 2;
                if (fish.velocity.length() > maxSpeed) {
                    fish.velocity.normalize().multiplyScalar(maxSpeed);
                }

                // Update position
                pos.add(fish.velocity.clone().multiplyScalar(dt));

                // Hard clamp
                pos.x = THREE.MathUtils.clamp(pos.x, -HALF_W + 1, HALF_W - 1);
                pos.y = THREE.MathUtils.clamp(pos.y, 1, AQ_H - 1);
                pos.z = THREE.MathUtils.clamp(pos.z, -HALF_D + 1, HALF_D - 1);

                // Orient fish toward movement direction
                if (fish.velocity.length() > 0.1) {
                    const targetQuat = new THREE.Quaternion();
                    const lookAtMatrix = new THREE.Matrix4();
                    const forward = fish.velocity.clone().normalize();
                    lookAtMatrix.lookAt(pos, pos.clone().add(forward), new THREE.Vector3(0, 1, 0));
                    targetQuat.setFromRotationMatrix(lookAtMatrix);
                    fish.mesh.quaternion.slerp(targetQuat, 0.05);
                }

                // Tail animation
                const tailAngle = Math.sin(time * fish.tailSpeed + fish.phase) * 0.5;
                fish.tail.rotation.z = tailAngle;

                // Fin animation
                const finAngle = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase + 1) * 0.3;
                fish.leftFin.rotation.x = -0.3 + finAngle;
                fish.rightFin.rotation.x = 0.3 - finAngle;
                fish.topFin.rotation.z = Math.PI * 0.1 + Math.sin(time * fish.tailSpeed * 0.5 + fish.phase) * 0.1;

                // Slight body bob
                fish.mesh.position.y += Math.sin(time * 2 + fish.phase) * 0.002;

                // Check if eating food
                if (nearestFood && nearestDist < 0.8) {
                    scene.remove(nearestFood.mesh);
                    foodArray.splice(foodArray.indexOf(nearestFood), 1);
                    // Growth
                    fish.currentScale *= 1.05;
                    const maxScale = 2.0;
                    if (fish.currentScale > maxScale) fish.currentScale = maxScale;
                    fish.mesh.scale.setScalar(fish.currentScale);
                    updateStats();
                }
            }
        }

        // === BUBBLE UPDATE ===
        function updateBubbles(dt, time) {
            for (let i = 0; i < bubbles.length; i++) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * dt;
                b.mesh.position.x += Math.sin(time * b.wobbleSpeed + b.wobblePhase) * b.wobbleAmp * dt;
                b.mesh.position.z += Math.cos(time * b.wobbleSpeed * 0.7 + b.wobblePhase) * b.wobbleAmp * dt * 0.5;

                if (b.mesh.position.y > AQ_H - 0.5) {
                    b.mesh.position.y = 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * (AQ_W - 4);
                    b.mesh.position.z = (Math.random() - 0.5) * (AQ_D - 4);
                }
            }
        }

        // === FOOD UPDATE ===
        function updateFood(dt) {
            for (let i = foodArray.length - 1; i >= 0; i--) {
                const food = foodArray[i];
                food.velocity.y -= 2 * dt; // gravity
                food.mesh.position.add(food.velocity.clone().multiplyScalar(dt));

                // Bounce on floor
                if (food.mesh.position.y < 0.5) {
                    food.mesh.position.y = 0.5;
                    food.velocity.y = 0;
                    food.velocity.x *= 0.9;
                    food.velocity.z *= 0.9;
                }

                // Remove if on bottom too long or out of bounds
                if (food.mesh.position.y <= 0.51 && Math.abs(food.velocity.y) < 0.1) {
                    food.mesh.position.y -= 0.01; // slowly sink
                    if (food.mesh.position.y < 0.3) {
                        scene.remove(food.mesh);
                        foodArray.splice(i, 1);
                        updateStats();
                    }
                }
            }
        }

        // === SEAWEEED UPDATE ===
        function updateSeaweeds(time) {
            for (let i = 0; i < seaweeds.length; i++) {
                const s = seaweeds[i];
                s.mesh.rotation.x = s.baseRotX + Math.sin(time * s.speed + s.phase) * 0.08;
                s.mesh.rotation.z = s.baseRotZ + Math.cos(time * s.speed * 0.7 + s.phase) * 0.06;
            }
        }

        // === UI BUTTONS ===
        document.getElementById('btnAddFish').addEventListener('click', () => {
            const colorIdx = Math.floor(Math.random() * FISH_COLORS.length);
            createFish(colorIdx, 0.6 + Math.random() * 0.4);
            updateStats();
        });

        document.getElementById('btnBubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) createBubble();
        });

        let lightOn = true;
        document.getElementById('btnLight').addEventListener('click', function () {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.2 : 0.1;
            this.textContent = lightOn ? '💡 Свет: ВКЛ' : '💡 Свет: ВЫКЛ';
            this.classList.toggle('off', !lightOn);
        });

        function updateStats() {
            document.getElementById('fishCount').textContent = fishArray.length;
            document.getElementById('foodCount').textContent = foodArray.length;
        }

        // === FPS COUNTER ===
        let frameCount = 0;
        let lastFpsTime = performance.now();

        function updateFPS() {
            frameCount++;
            const now = performance.now();
            if (now - lastFpsTime >= 1000) {
                document.getElementById('fpsCounter').textContent = frameCount + ' FPS';
                frameCount = 0;
                lastFpsTime = now;
            }
        }

        // === ANIMATION LOOP ===
        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const dt = Math.min(clock.getDelta(), 0.05);
            const time = clock.elapsedTime;

            updateFish(dt, time);
            updateBubbles(dt, time);
            updateFood(dt);
            updateSeaweeds(time);

            // Animate point lights slightly
            pointLight1.position.x = -10 + Math.sin(time * 0.3) * 3;
            pointLight1.position.z = Math.cos(time * 0.2) * 3;
            pointLight2.position.x = 10 + Math.cos(time * 0.25) * 2;
            pointLight2.position.z = -5 + Math.sin(time * 0.35) * 2;

            controls.update();
            renderer.render(scene, camera);
            updateFPS();
        }

        // === RESIZE HANDLER ===
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Start
        animate();
    </script>
</body>
</html>
```

## Что реализовано:

### 🐠 Рыбки (15 шт.)
- Детализированная анатомия: тело, хвост, 3 плавника, глаза с зрачками
- 8 цветовых схем, случайный масштаб 0.6–1.2
- Плавная анимация хвоста и плавников с индивидуальной фазой
- Ориентация в направлении движения через slerp кватернионов

### 🧠 ИИ поведения
- Избегание столкновений между рыбками
- Мягкое отражение от стенок
- Случайное блуждание с таймером
- Преследование корма в радиусе 15 единиц
- Рост на 5% при поедании (максимум ×2)

### 🌊 Окружение
- Стеклянный контейнер с `transmission: 0.95` + wireframe
- Процедурный песок с шумом вершин
- 8 деформированных камней (додекаэдры)
- 12 водорослей из `TubeGeometry` с покачиванием

### 💭 Пузыри (30 шт.)
- Прозрачный материал, покачивание синусом/косинусом
- Автоматический сброс на дно при достижении поверхности

### 🍽️ Кормление
- Клик → рэйкастинг → создание корма
- Гравитация, отскок от дна, медленное затопление
- Рыбки плывут к ближайшему корму

### 💡 Освещение
- Ambient + Directional (тени 2048², PCFSoft)
- 2 подвижных PointLight (подводный эффект)
- Переключатель света

### 🎮 UI
- Glass-morphism панели с blur
- Градиентные кнопки с hover-эффектами
- Счётчики рыбок/корма + FPS