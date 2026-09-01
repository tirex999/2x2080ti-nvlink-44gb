

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

        #canvas-container {
            width: 100vw;
            height: 100vh;
        }

        .panel {
            position: absolute;
            top: 20px;
            padding: 20px;
            border-radius: 16px;
            background: rgba(10, 25, 50, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        #info-panel {
            left: 20px;
            max-width: 280px;
        }

        #stats-panel {
            right: 20px;
            min-width: 180px;
        }

        .panel h2 {
            font-size: 18px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #42a5f5, #90caf9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .panel p {
            font-size: 12px;
            line-height: 1.6;
            color: rgba(200, 230, 255, 0.8);
            margin-bottom: 8px;
        }

        .panel ul {
            list-style: none;
            padding: 0;
            margin-bottom: 12px;
        }

        .panel ul li {
            font-size: 11px;
            padding: 3px 0;
            color: rgba(180, 220, 255, 0.7);
        }

        .panel ul li::before {
            content: "• ";
            color: #42a5f5;
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
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b35, #f7c948);
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.5);
        }

        .btn-bubbles {
            background: linear-gradient(135deg, #42a5f5, #7c4dff);
            box-shadow: 0 4px 15px rgba(66, 165, 245, 0.3);
        }

        .btn-bubbles:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(66, 165, 245, 0.5);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd54f, #ffb300);
            box-shadow: 0 4px 15px rgba(255, 213, 79, 0.3);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 213, 79, 0.5);
        }

        .btn-light.off {
            background: linear-gradient(135deg, #546e7a, #37474f);
            box-shadow: 0 4px 15px rgba(84, 110, 122, 0.3);
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(100, 180, 255, 0.1);
        }

        .stat-item:last-child {
            border-bottom: none;
        }

        .stat-label {
            font-size: 12px;
            color: rgba(180, 220, 255, 0.7);
        }

        .stat-value {
            font-size: 14px;
            font-weight: 700;
            color: #64b5f6;
        }

        @media (max-width: 768px) {
            .panel {
                padding: 12px;
                border-radius: 12px;
            }

            #info-panel {
                max-width: 200px;
                top: 10px;
                left: 10px;
            }

            #stats-panel {
                top: 10px;
                right: 10px;
                min-width: 140px;
            }

            .panel h2 {
                font-size: 14px;
            }

            .panel p, .panel ul li {
                font-size: 10px;
            }

            .btn {
                padding: 8px 12px;
                font-size: 11px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel" id="info-panel">
        <h2>🐠 3D Аквариум</h2>
        <p>Интерактивный подводный мир</p>
        <ul>
            <li>ЛКМ — вращение камеры</li>
            <li>ПКМ — панорамирование</li>
            <li>Колесо — зум</li>
            <li>Клик по воде — кормление</li>
        </ul>
        <div class="btn-group">
            <button class="btn btn-fish" id="btn-add-fish">+ Добавить рыбку</button>
            <button class="btn btn-bubbles" id="btn-bubbles">+ Больше пузырей</button>
            <button class="btn btn-light" id="btn-light">☀ Свет: Вкл</button>
        </div>
    </div>

    <div class="panel" id="stats-panel">
        <h2>📊 Статистика</h2>
        <div class="stat-item">
            <span class="stat-label">Рыбки</span>
            <span class="stat-value" id="fish-count">15</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Пузыри</span>
            <span class="stat-value" id="bubble-count">30</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Корм</span>
            <span class="stat-value" id="food-count">0</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">FPS</span>
            <span class="stat-value" id="fps-counter">60</span>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a2a4a, 0.008);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(0, 15, 45);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        // Background gradient
        const bgCanvas = document.createElement('canvas');
        bgCanvas.width = 2;
        bgCanvas.height = 512;
        const bgCtx = bgCanvas.getContext('2d');
        const bgGrad = bgCtx.createLinearGradient(0, 0, 0, 512);
        bgGrad.addColorStop(0, '#0a1628');
        bgGrad.addColorStop(0.5, '#0d2847');
        bgGrad.addColorStop(1, '#0a3060');
        bgCtx.fillStyle = bgGrad;
        bgCtx.fillRect(0, 0, 2, 512);
        const bgTexture = new THREE.CanvasTexture(bgCanvas);
        scene.background = bgTexture;

        // === CONTROLS ===
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 5, 0);

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

        const pointLight1 = new THREE.PointLight(0x4488ff, 0.6, 40);
        pointLight1.position.set(-10, 15, 5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2266cc, 0.5, 40);
        pointLight2.position.set(10, 10, -5);
        scene.add(pointLight2);

        // === AQUARIUM ENVIRONMENT ===
        const AQUARIUM_WIDTH = 36;
        const AQUARIUM_HEIGHT = 24;
        const AQUARIUM_DEPTH = 20;
        const AQUARIUM_Y_OFFSET = AQUARIUM_HEIGHT / 2;

        // Glass container
        const glassGeometry = new THREE.BoxGeometry(AQUARIUM_WIDTH, AQUARIUM_HEIGHT, AQUARIUM_DEPTH);
        const glassMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x88ccee,
            metalness: 0,
            roughness: 0.05,
            transmission: 0.95,
            thickness: 0.5,
            transparent: true,
            opacity: 0.15,
            side: THREE.DoubleSide
        });
        const glassBox = new THREE.Mesh(glassGeometry, glassMaterial);
        glassBox.position.y = AQUARIUM_Y_OFFSET;
        scene.add(glassBox);

        // Wireframe edges
        const edgesGeometry = new THREE.EdgesGeometry(glassGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.4 });
        const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        edges.position.y = AQUARIUM_Y_OFFSET;
        scene.add(edges);

        // Sandy bottom
        const sandGeometry = new THREE.PlaneGeometry(AQUARIUM_WIDTH - 1, AQUARIUM_DEPTH - 1, 32, 32);
        const sandPositions = sandGeometry.attributes.position;
        for (let i = 0; i < sandPositions.count; i++) {
            const x = sandPositions.getX(i);
            const y = sandPositions.getY(i);
            sandPositions.setZ(i, Math.sin(x * 0.5) * 0.15 + Math.cos(y * 0.7) * 0.1 + Math.random() * 0.08);
        }
        sandGeometry.computeVertexNormals();
        const sandMaterial = new THREE.MeshStandardMaterial({
            color: 0xd4b483,
            roughness: 0.9,
            metalness: 0.05
        });
        const sand = new THREE.Mesh(sandGeometry, sandMaterial);
        sand.rotation.x = -Math.PI / 2;
        sand.position.y = 0.2;
        sand.receiveShadow = true;
        scene.add(sand);

        // Rocks
        const rockMaterial = new THREE.MeshStandardMaterial({ color: 0x556677, roughness: 0.8, metalness: 0.1 });
        for (let i = 0; i < 8; i++) {
            const size = 0.8 + Math.random() * 1.5;
            const rockGeo = new THREE.DodecahedronGeometry(size, 1);
            const rockPos = rockGeo.attributes.position;
            for (let j = 0; j < rockPos.count; j++) {
                rockPos.setX(j, rockPos.getX(j) * (0.7 + Math.random() * 0.6));
                rockPos.setY(j, rockPos.getY(j) * (0.5 + Math.random() * 0.5));
                rockPos.setZ(j, rockPos.getZ(j) * (0.7 + Math.random() * 0.6));
            }
            rockGeo.computeVertexNormals();
            const rock = new THREE.Mesh(rockGeo, rockMaterial.clone());
            rock.material.color.setHSL(0.55 + Math.random() * 0.1, 0.1 + Math.random() * 0.1, 0.3 + Math.random() * 0.2);
            rock.position.set(
                (Math.random() - 0.5) * (AQUARIUM_WIDTH - 6),
                size * 0.4,
                (Math.random() - 0.5) * (AQUARIUM_DEPTH - 6)
            );
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.castShadow = true;
            rock.receiveShadow = true;
            scene.add(rock);
        }

        // Seaweed
        const seaweeds = [];
        const seaweedColors = [0x2d8a4e, 0x3cb371, 0x228b22, 0x008000, 0x32cd32];
        for (let i = 0; i < 12; i++) {
            const height = 3 + Math.random() * 5;
            const points = [];
            const segments = 8;
            for (let j = 0; j <= segments; j++) {
                const t = j / segments;
                points.push(new THREE.Vector3(
                    Math.sin(t * 3) * 0.3,
                    t * height,
                    Math.cos(t * 2) * 0.2
                ));
            }
            const curve = new THREE.CatmullRomCurve3(points);
            const tubeGeo = new THREE.TubeGeometry(curve, 16, 0.15 + Math.random() * 0.1, 6, false);
            const seaweedMat = new THREE.MeshStandardMaterial({
                color: seaweedColors[Math.floor(Math.random() * seaweedColors.length)],
                roughness: 0.7,
                metalness: 0.05
            });
            const seaweed = new THREE.Mesh(tubeGeo, seaweedMat);
            seaweed.position.set(
                (Math.random() - 0.5) * (AQUARIUM_WIDTH - 4),
                0.2,
                (Math.random() - 0.5) * (AQUARIUM_DEPTH - 4)
            );
            seaweed.castShadow = true;
            scene.add(seaweed);
            seaweeds.push({
                mesh: seaweed,
                phase: Math.random() * Math.PI * 2,
                speed: 0.5 + Math.random() * 0.5
            });
        }

        // === FISH SYSTEM ===
        const fishArray = [];
        const foodArray = [];
        const bubbleArray = [];

        const colorSchemes = [
            { body: 0xff6633, fin: 0xff9966, name: 'orange' },
            { body: 0x3366ff, fin: 0x6699ff, name: 'blue' },
            { body: 0xffcc00, fin: 0xff3333, name: 'yellow-red' },
            { body: 0x9933cc, fin: 0xcc66ff, name: 'purple' },
            { body: 0xdd2222, fin: 0xff6644, name: 'red' },
            { body: 0x22aa44, fin: 0x66dd88, name: 'green' },
            { body: 0xff6699, fin: 0xff99bb, name: 'pink' },
            { body: 0xdaa520, fin: 0xffd700, name: 'gold' }
        ];

        function createFish(position) {
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(0.8, 12, 10);
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
            const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.08, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
            leftEye.position.set(0.9, 0.15, 0.35);
            group.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(1.0, 0.15, 0.42);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
            rightEye.position.set(0.9, 0.15, -0.35);
            group.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(1.0, 0.15, -0.42);
            group.add(rightPupil);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 6);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.9
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.5, 0, 0);
            tail.rotation.z = Math.PI / 2;
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 4);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                transparent: true,
                opacity: 0.8
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0, 0.6, 0);
            topFin.rotation.z = -0.3;
            group.add(topFin);

            // Side fins
            const sideFinGeo = new THREE.ConeGeometry(0.25, 0.6, 4);
            const leftFin = new THREE.Mesh(sideFinGeo, topFinMat.clone());
            leftFin.position.set(0.2, -0.1, 0.5);
            leftFin.rotation.x = Math.PI / 2.5;
            leftFin.rotation.z = 0.5;
            group.add(leftFin);

            const rightFin = new THREE.Mesh(sideFinGeo, topFinMat.clone());
            rightFin.position.set(0.2, -0.1, -0.5);
            rightFin.rotation.x = -Math.PI / 2.5;
            rightFin.rotation.z = 0.5;
            group.add(rightFin);

            group.scale.setScalar(scale);
            if (position) {
                group.position.copy(position);
            } else {
                group.position.set(
                    (Math.random() - 0.5) * (AQUARIUM_WIDTH - 6),
                    3 + Math.random() * (AQUARIUM_HEIGHT - 6),
                    (Math.random() - 0.5) * (AQUARIUM_DEPTH - 6)
                );
            }
            scene.add(group);

            const fishData = {
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
                speed: 1.5 + Math.random() * 1.5,
                tailSpeed: 4 + Math.random() * 3,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2.5 + Math.random() * 1.5,
                wanderTimer: Math.random() * 3,
                scale: scale
            };

            fishArray.push(fishData);
            return fishData;
        }

        // Create initial fish
        for (let i = 0; i < 15; i++) {
            createFish();
        }

        // === BUBBLE SYSTEM ===
        function createBubble() {
            const size = 0.08 + Math.random() * 0.2;
            const bubbleGeo = new THREE.SphereGeometry(size, 8, 8);
            const bubbleMat = new THREE.MeshPhysicalMaterial({
                color: 0xaaddff,
                metalness: 0,
                roughness: 0,
                transmission: 0.9,
                transparent: true,
                opacity: 0.4,
                clearcoat: 1
            });
            const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
            bubble.position.set(
                (Math.random() - 0.5) * (AQUARIUM_WIDTH - 4),
                0.5 + Math.random() * 2,
                (Math.random() - 0.5) * (AQUARIUM_DEPTH - 4)
            );
            scene.add(bubble);

            bubbleArray.push({
                mesh: bubble,
                speed: 0.5 + Math.random() * 1.0,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 1 + Math.random() * 2,
                baseX: bubble.position.x,
                baseZ: bubble.position.z
            });
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // === FOOD SYSTEM ===
        function createFood(position) {
            const foodGeo = new THREE.SphereGeometry(0.15, 6, 6);
            const foodMat = new THREE.MeshStandardMaterial({
                color: 0xff8844,
                emissive: 0xff4400,
                emissiveIntensity: 0.3
            });
            const food = new THREE.Mesh(foodGeo, foodMat);
            food.position.copy(position);
            scene.add(food);

            foodArray.push({
                mesh: food,
                velocity: new THREE.Vector3(0, -1, 0)
            });
        }

        // === RAYCASTER ===
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const waterPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

        renderer.domElement.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            // Check if clicking on UI
            if (event.target !== renderer.domElement) return;

            // Intersect with a virtual plane at mid-height
            const intersectPoint = new THREE.Vector3();
            const planeAtMidHeight = new THREE.Plane(new THREE.Vector3(0, 1, 0), -AQUARIUM_Y_OFFSET);
            raycaster.ray.intersectPlane(planeAtMidHeight, intersectPoint);

            if (intersectPoint) {
                // Clamp to aquarium bounds
                intersectPoint.x = Math.max(-AQUARIUM_WIDTH / 2 + 2, Math.min(AQUARIUM_WIDTH / 2 - 2, intersectPoint.x));
                intersectPoint.y = Math.max(2, Math.min(AQUARIUM_HEIGHT - 2, AQUARIUM_Y_OFFSET));
                intersectPoint.z = Math.max(-AQUARIUM_DEPTH / 2 + 2, Math.min(AQUARIUM_DEPTH / 2 - 2, intersectPoint.z));
                createFood(intersectPoint);
            }
        });

        // === UI BUTTONS ===
        let lightOn = true;

        document.getElementById('btn-add-fish').addEventListener('click', () => {
            createFish();
            updateStats();
        });

        document.getElementById('btn-bubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) createBubble();
            updateStats();
        });

        document.getElementById('btn-light').addEventListener('click', () => {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.2 : 0.2;
            const btn = document.getElementById('btn-light');
            btn.textContent = lightOn ? '☀ Свет: Вкл' : '🌙 Свет: Выкл';
            btn.classList.toggle('off', !lightOn);
        });

        function updateStats() {
            document.getElementById('fish-count').textContent = fishArray.length;
            document.getElementById('bubble-count').textContent = bubbleArray.length;
            document.getElementById('food-count').textContent = foodArray.length;
        }

        // === ANIMATION LOOP ===
        const clock = new THREE.Clock();
        let frameCount = 0;
        let lastFpsTime = 0;

        function animate() {
            requestAnimationFrame(animate);
            const delta = clock.getDelta();
            const elapsed = clock.getElapsedTime();

            // FPS counter
            frameCount++;
            if (elapsed - lastFpsTime >= 1) {
                document.getElementById('fps-counter').textContent = frameCount;
                frameCount = 0;
                lastFpsTime = elapsed;
            }

            // Update fish
            for (let i = fishArray.length - 1; i >= 0; i--) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Wander
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.velocity.x += (Math.random() - 0.5) * 2;
                    fish.velocity.y += (Math.random() - 0.5) * 0.5;
                    fish.velocity.z += (Math.random() - 0.5) * 2;
                    fish.wanderTimer = 2 + Math.random() * 3;
                }

                // Food seeking
                if (foodArray.length > 0) {
                    if (!fish.targetFood || !fish.targetFood.mesh.parent) {
                        fish.targetFood = null;
                    }
                    if (!fish.targetFood) {
                        for (const food of foodArray) {
                            const dist = pos.distanceTo(food.mesh.position);
                            if (dist < 15) {
                                fish.targetFood = food;
                                break;
                            }
                        }
                    }
                    if (fish.targetFood && fish.targetFood.mesh.parent) {
                        const dir = fish.targetFood.mesh.position.clone().sub(pos).normalize();
                        fish.velocity.add(dir.multiplyScalar(3 * delta));

                        // Eat food
                        if (pos.distanceTo(fish.targetFood.mesh.position) < 1.0) {
                            scene.remove(fish.targetFood.mesh);
                            const idx = foodArray.indexOf(fish.targetFood);
                            if (idx !== -1) foodArray.splice(idx, 1);
                            fish.targetFood = null;

                            // Grow
                            fish.scale *= 1.05;
                            fish.mesh.scale.setScalar(fish.scale);
                            updateStats();
                        }
                    }
                }

                // Collision avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j].mesh.position;
                    const dist = pos.distanceTo(other);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const away = pos.clone().sub(other).normalize();
                        fish.velocity.add(away.multiplyScalar(2 * delta));
                    }
                }

                // Wall reflection
                const margin = 2;
                const halfW = AQUARIUM_WIDTH / 2 - margin;
                const halfH = AQUARIUM_HEIGHT / 2 - margin;
                const halfD = AQUARIUM_DEPTH / 2 - margin;

                if (pos.x > halfW) fish.velocity.x -= 3 * delta;
                if (pos.x < -halfW) fish.velocity.x += 3 * delta;
                if (pos.y > halfH) fish.velocity.y -= 3 * delta;
                if (pos.y < 1) fish.velocity.y += 3 * delta;
                if (pos.z > halfD) fish.velocity.z -= 3 * delta;
                if (pos.z < -halfD) fish.velocity.z += 3 * delta;

                // Clamp position
                pos.x = Math.max(-halfW, Math.min(halfW, pos.x));
                pos.y = Math.max(1, Math.min(halfH, pos.y));
                pos.z = Math.max(-halfD, Math.min(halfD, pos.z));

                // Limit speed
                const speed = fish.velocity.length();
                if (speed > fish.speed) {
                    fish.velocity.normalize().multiplyScalar(fish.speed);
                }

                // Move
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Orient fish towards velocity direction
                if (speed > 0.1) {
                    const targetQuat = new THREE.Quaternion();
                    const lookDir = fish.velocity.clone().normalize();
                    const m = new THREE.Matrix4();
                    m.lookAt(new THREE.Vector3(0, 0, 0), lookDir, new THREE.Vector3(0, 1, 0));
                    targetQuat.setFromRotationMatrix(m);
                    fish.mesh.quaternion.slerp(targetQuat, 3 * delta);
                }

                // Tail animation
                fish.phase += fish.tailSpeed * delta;
                fish.tail.rotation.y = Math.sin(fish.phase) * 0.5;

                // Fin animation
                fish.leftFin.rotation.x = Math.PI / 2.5 + Math.sin(fish.phase * 0.7) * 0.2;
                fish.rightFin.rotation.x = -Math.PI / 2.5 + Math.sin(fish.phase * 0.7 + 0.5) * 0.2;
                fish.topFin.rotation.z = -0.3 + Math.sin(fish.phase * 0.5) * 0.1;
            }

            // Update bubbles
            for (let i = bubbleArray.length - 1; i >= 0; i--) {
                const bubble = bubbleArray[i];
                bubble.mesh.position.y += bubble.speed * delta;
                bubble.mesh.position.x = bubble.baseX + Math.sin(elapsed * bubble.wobbleSpeed + bubble.wobblePhase) * 0.3;
                bubble.mesh.position.z = bubble.baseZ + Math.cos(elapsed * bubble.wobbleSpeed * 0.7 + bubble.wobblePhase) * 0.2;

                if (bubble.mesh.position.y > AQUARIUM_HEIGHT - 1) {
                    bubble.mesh.position.y = 0.5;
                    bubble.baseX = (Math.random() - 0.5) * (AQUARIUM_WIDTH - 4);
                    bubble.baseZ = (Math.random() - 0.5) * (AQUARIUM_DEPTH - 4);
                    bubble.mesh.position.x = bubble.baseX;
                    bubble.mesh.position.z = bubble.baseZ;
                }
            }

            // Update food
            for (let i = foodArray.length - 1; i >= 0; i--) {
                const food = foodArray[i];
                food.mesh.position.y += food.velocity.y * delta;
                food.velocity.y -= 2 * delta;

                // Slight drift
                food.mesh.position.x += Math.sin(elapsed * 2 + i) * 0.005;
                food.mesh.position.z += Math.cos(elapsed * 1.5 + i) * 0.005;

                if (food.mesh.position.y < 0.5) {
                    scene.remove(food.mesh);
                    foodArray.splice(i, 1);
                    updateStats();
                }
            }

            // Animate seaweed
            for (const sw of seaweeds) {
                sw.mesh.rotation.x = Math.sin(elapsed * sw.speed + sw.phase) * 0.08;
                sw.mesh.rotation.z = Math.cos(elapsed * sw.speed * 0.8 + sw.phase) * 0.06;
            }

            // Animate lights subtly
            pointLight1.intensity = 0.5 + Math.sin(elapsed * 0.5) * 0.1;
            pointLight2.intensity = 0.4 + Math.cos(elapsed * 0.7) * 0.1;

            controls.update();
            renderer.render(scene, camera);
        }

        // === RESIZE HANDLER ===
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Start
        updateStats();
        animate();
    </script>
</body>
</html>
```

## Что реализовано

| Компонент | Детали |
|-----------|--------|
| **Рыбки** | 15 штук, 8 цветовых схем, тело/глаза/хвост/плавники, анимация махания |
| **ИИ** | Избегание столкновений, отражение от стен, случайное блуждание, преследование корма, рост |
| **Аквариум** | Стеклянный контейнер (transmission), wireframe-рамка, песчаное дно с процедурными неровностями |
| **Декор** | 8 деформированных камней, 12 водорослей из TubeGeometry с покачиванием |
| **Пузыри** | 30 шт., прозрачные сферы, движение вверх с покачиванием, сброс на поверхности |
| **Кормление** | Клик → корм падает с гравитацией, рыбки в радиусе 15 плывут к нему, при поедании рост +5% |
| **Освещение** | Ambient + Directional (тени 2048²) + 2 PointLight, переключение кнопкой |
| **Камера** | OrbitControls: вращение, панорама, зум (10–60), damping, ограничение угла |
| **UI** | Панель управления (слева), статистика с FPS (справа), glass-morphism стиль |
| **Эффекты** | FogExp2, градиентный фон, ACES tone mapping, PCFSoftShadowMap |

Просто сохраните код в `.html` файл и откройте в браузере — всё работает без сборки.