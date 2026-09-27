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
            background: linear-gradient(180deg, #0a1628 0%, #0d2847 50%, #1a4a7a 100%);
        }

        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
        }

        .glass-panel {
            background: rgba(10, 30, 60, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        #info-panel {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 100;
            max-width: 280px;
        }

        #info-panel h1 {
            font-size: 1.4em;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #00d4ff, #7b68ee, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        #info-panel p {
            font-size: 0.8em;
            line-height: 1.6;
            opacity: 0.8;
            margin-bottom: 15px;
        }

        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.85em;
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

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b35, #ff8c42);
        }

        .btn-bubbles {
            background: linear-gradient(135deg, #00b4d8, #0077b6);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd60a, #ff9500);
        }

        .btn-feed {
            background: linear-gradient(135deg, #7b68ee, #9b59b6);
        }

        #stats-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
            min-width: 160px;
        }

        #stats-panel h3 {
            font-size: 0.9em;
            margin-bottom: 10px;
            color: #7dd3fc;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(100, 180, 255, 0.1);
            font-size: 0.8em;
        }

        .stat-row:last-child {
            border-bottom: none;
        }

        .stat-value {
            color: #7dd3fc;
            font-weight: 700;
            font-size: 1.1em;
        }

        #feed-hint {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 100;
            padding: 12px 24px;
            font-size: 0.85em;
            opacity: 0.8;
            pointer-events: none;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        @media (max-width: 768px) {
            #info-panel {
                max-width: 200px;
                padding: 14px;
            }
            #info-panel h1 {
                font-size: 1.1em;
            }
            #stats-panel {
                min-width: 120px;
                padding: 14px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="info-panel" class="glass-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>
            🖱️ Левый клик — вращение<br>
            🖱️ Правый клик — панорама<br>
            🖱️ Колесо — зум<br>
            🍽️ Клик по воде — кормить
        </p>
        <div class="btn-group">
            <button class="btn btn-fish" onclick="addFish()">🐟 Добавить рыбку</button>
            <button class="btn btn-bubbles" onclick="addBubbles()">💨 Больше пузырей</button>
            <button class="btn btn-light" onclick="toggleLight()">💡 Свет</button>
            <button class="btn btn-feed" onclick="feedAll()">🍽️ Покормить всех</button>
        </div>
    </div>

    <div id="stats-panel" class="glass-panel">
        <h3>📊 Статистика</h3>
        <div class="stat-row">
            <span>Рыбки:</span>
            <span class="stat-value" id="fish-count">15</span>
        </div>
        <div class="stat-row">
            <span>Пузыри:</span>
            <span class="stat-value" id="bubble-count">30</span>
        </div>
        <div class="stat-row">
            <span>Корм:</span>
            <span class="stat-value" id="food-count">0</span>
        </div>
        <div class="stat-row">
            <span>FPS:</span>
            <span class="stat-value" id="fps-counter">60</span>
        </div>
    </div>

    <div id="feed-hint" class="glass-panel">
        💡 Кликните по аквариуму, чтобы бросить корм!
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === GLOBALS ===
        let scene, camera, renderer, controls;
        let fishArray = [];
        let bubbles = [];
        let foods = [];
        let seaweeds = [];
        let rocks = [];
        let directionalLight;
        let lightOn = true;
        let clock = new THREE.Clock();
        let frameCount = 0;
        let lastFpsTime = 0;

        // Aquarium dimensions
        const AQUARIUM = { width: 36, height: 24, depth: 20 };
        const HALF = { x: AQUARIUM.width / 2, y: AQUARIUM.height / 2, z: AQUARIUM.depth / 2 };

        // Color schemes
        const COLOR_SCHEMES = [
            { body: 0xff6b35, fin: 0xff8c42, name: 'orange' },
            { body: 0x2196f3, fin: 0x64b5f6, name: 'blue' },
            { body: 0xffeb3b, fin: 0xf44336, name: 'yellow-red' },
            { body: 0x9c27b0, fin: 0xce93d8, name: 'purple' },
            { body: 0xf44336, fin: 0xff7961, name: 'red' },
            { body: 0x4caf50, fin: 0x81c784, name: 'green' },
            { body: 0xe91e63, fin: 0xf48fb1, name: 'pink' },
            { body: 0xffd700, fin: 0xffab00, name: 'gold' }
        ];

        // === INIT ===
        function init() {
            // Scene
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);
            scene.background = new THREE.Color(0x0a1628);

            // Camera
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
            camera.position.set(30, 15, 35);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.08;
            controls.minDistance = 10;
            controls.maxDistance = 60;
            controls.maxPolarAngle = Math.PI / 1.8;
            controls.target.set(0, 0, 0);

            // Lighting
            setupLighting();

            // Aquarium
            createAquarium();

            // Environment
            createSand();
            createRocks();
            createSeaweeds();

            // Fish
            for (let i = 0; i < 15; i++) {
                createFish();
            }

            // Bubbles
            for (let i = 0; i < 30; i++) {
                createBubble();
            }

            // Events
            window.addEventListener('resize', onResize);
            renderer.domElement.addEventListener('click', onFeedClick);

            // Start
            animate();
        }

        // === LIGHTING ===
        function setupLighting() {
            // Ambient
            const ambient = new THREE.AmbientLight(0x404060, 0.4);
            scene.add(ambient);

            // Directional (sun)
            directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(10, 30, 10);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            directionalLight.shadow.camera.near = 1;
            directionalLight.shadow.camera.far = 80;
            directionalLight.shadow.camera.left = -25;
            directionalLight.shadow.camera.right = 25;
            directionalLight.shadow.camera.top = 20;
            directionalLight.shadow.camera.bottom = -20;
            directionalLight.shadow.bias = -0.001;
            scene.add(directionalLight);

            // Underwater point lights
            const pointLight1 = new THREE.PointLight(0x00bfff, 0.6, 40);
            pointLight1.position.set(-10, 5, 0);
            scene.add(pointLight1);

            const pointLight2 = new THREE.PointLight(0x4169e1, 0.5, 40);
            pointLight2.position.set(10, -5, 5);
            scene.add(pointLight2);

            // Subtle rim light
            const rimLight = new THREE.PointLight(0x00ffcc, 0.3, 30);
            rimLight.position.set(0, 10, -10);
            scene.add(rimLight);
        }

        // === AQUARIUM ===
        function createAquarium() {
            // Glass box
            const glassGeo = new THREE.BoxGeometry(AQUARIUM.width, AQUARIUM.height, AQUARIUM.depth);
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                transparent: true,
                opacity: 0.08,
                transmission: 0.95,
                roughness: 0.05,
                metalness: 0,
                side: THREE.BackSide,
                depthWrite: false
            });
            const glass = new THREE.Mesh(glassGeo, glassMat);
            glass.position.y = 0;
            scene.add(glass);

            // Wireframe edges
            const edgesGeo = new THREE.EdgesGeometry(glassGeo);
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x4488cc, transparent: true, opacity: 0.4 });
            const edges = new THREE.LineSegments(edgesGeo, edgesMat);
            scene.add(edges);

            // Frame (thicker edges)
            const frameMat = new THREE.MeshStandardMaterial({ color: 0x334455, metalness: 0.8, roughness: 0.3 });
            const frameThickness = 0.3;

            // Vertical edges
            const vertGeo = new THREE.BoxGeometry(frameThickness, AQUARIUM.height, frameThickness);
            const positions = [
                [-HALF.x, 0, -HALF.z], [HALF.x, 0, -HALF.z],
                [-HALF.x, 0, HALF.z], [HALF.x, 0, HALF.z]
            ];
            positions.forEach(pos => {
                const frame = new THREE.Mesh(vertGeo, frameMat);
                frame.position.set(...pos);
                frame.castShadow = true;
                scene.add(frame);
            });

            // Top frame
            const topFrameGeo1 = new THREE.BoxGeometry(AQUARIUM.width + frameThickness, frameThickness, frameThickness);
            const topFrameGeo2 = new THREE.BoxGeometry(frameThickness, frameThickness, AQUARIUM.depth + frameThickness);
            [-HALF.z, HALF.z].forEach(z => {
                const f = new THREE.Mesh(topFrameGeo1, frameMat);
                f.position.set(0, HALF.y, z);
                scene.add(f);
            });
            [-HALF.x, HALF.x].forEach(x => {
                const f = new THREE.Mesh(topFrameGeo2, frameMat);
                f.position.set(x, HALF.y, 0);
                scene.add(f);
            });
        }

        // === SAND ===
        function createSand() {
            const sandGeo = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth, 40, 40);
            const vertices = sandGeo.attributes.position.array;
            for (let i = 0; i < vertices.length; i += 3) {
                vertices[i + 2] += (Math.random() - 0.5) * 0.3;
            }
            sandGeo.computeVertexNormals();

            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xd4a574,
                roughness: 0.9,
                metalness: 0.0
            });
            const sand = new THREE.Mesh(sandGeo, sandMat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = -HALF.y + 0.1;
            sand.receiveShadow = true;
            scene.add(sand);
        }

        // === ROCKS ===
        function createRocks() {
            for (let i = 0; i < 8; i++) {
                const size = 0.5 + Math.random() * 1.2;
                const rockGeo = new THREE.DodecahedronGeometry(size, 1);

                // Deform vertices
                const verts = rockGeo.attributes.position.array;
                for (let j = 0; j < verts.length; j += 3) {
                    verts[j] += (Math.random() - 0.5) * size * 0.4;
                    verts[j + 1] += (Math.random() - 0.5) * size * 0.3;
                    verts[j + 2] += (Math.random() - 0.5) * size * 0.4;
                }
                rockGeo.computeVertexNormals();

                const rockMat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.2, 0.3 + Math.random() * 0.2),
                    roughness: 0.9,
                    metalness: 0.1
                });

                const rock = new THREE.Mesh(rockGeo, rockMat);
                rock.position.set(
                    (Math.random() - 0.5) * (AQUARIUM.width - 4),
                    -HALF.y + size * 0.5,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                );
                rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
                rock.castShadow = true;
                rock.receiveShadow = true;
                scene.add(rock);
                rocks.push(rock);
            }
        }

        // === SEAWEED ===
        function createSeaweeds() {
            for (let i = 0; i < 12; i++) {
                const height = 3 + Math.random() * 5;
                const segments = 8;
                const points = [];

                for (let j = 0; j <= segments; j++) {
                    const t = j / segments;
                    points.push(new THREE.Vector3(
                        Math.sin(t * 2) * 0.3,
                        t * height,
                        Math.cos(t * 1.5) * 0.2
                    ));
                }

                const curve = new THREE.CatmullRomCurve3(points);
                const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.15 + Math.random() * 0.1, 6, false);

                const hue = 0.25 + Math.random() * 0.15;
                const tubeMat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color().setHSL(hue, 0.7, 0.35),
                    roughness: 0.7,
                    metalness: 0.0,
                    side: THREE.DoubleSide
                });

                const seaweed = new THREE.Mesh(tubeGeo, tubeMat);
                seaweed.position.set(
                    (Math.random() - 0.5) * (AQUARIUM.width - 6),
                    -HALF.y + 0.1,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                );
                seaweed.castShadow = true;
                scene.add(seaweed);

                seaweeds.push({
                    mesh: seaweed,
                    phase: Math.random() * Math.PI * 2,
                    speed: 0.5 + Math.random() * 0.5,
                    amplitude: 0.03 + Math.random() * 0.04
                });
            }
        }

        // === FISH ===
        function createFish(customPos) {
            const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
            const scale = 0.6 + Math.random() * 0.6;

            const fishGroup = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.4, 0.7, 0.5);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.3,
                metalness: 0.4,
                emissive: scheme.body,
                emissiveIntensity: 0.05
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            fishGroup.add(body);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.18, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1 });
            const pupilGeo = new THREE.SphereGeometry(0.1, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            [-1, 1].forEach(side => {
                const eye = new THREE.Mesh(eyeGeo, eyeMat);
                eye.position.set(0.9, 0.15, side * 0.3);
                fishGroup.add(eye);

                const pupil = new THREE.Mesh(pupilGeo, pupilMat);
                pupil.position.set(1.0, 0.15, side * 0.3);
                fishGroup.add(pupil);
            });

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 4);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                metalness: 0.2,
                transparent: true,
                opacity: 0.85,
                side: THREE.DoubleSide
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.5, 0, 0);
            fishGroup.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 3);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.8,
                side: THREE.DoubleSide
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0.2, 0.6, 0);
            topFin.rotation.z = -0.3;
            fishGroup.add(topFin);

            // Side fins
            const sideFinGeo = new THREE.ConeGeometry(0.2, 0.6, 3);
            const leftFin = new THREE.Mesh(sideFinGeo, topFinMat.clone());
            leftFin.position.set(0.2, -0.1, 0.5);
            leftFin.rotation.x = 0.5;
            leftFin.rotation.z = 0.3;
            fishGroup.add(leftFin);

            const rightFin = new THREE.Mesh(sideFinGeo, topFinMat.clone());
            rightFin.position.set(0.2, -0.1, -0.5);
            rightFin.rotation.x = -0.5;
            rightFin.rotation.z = 0.3;
            fishGroup.add(rightFin);

            // Position
            const pos = customPos || new THREE.Vector3(
                (Math.random() - 0.5) * (AQUARIUM.width - 6),
                (Math.random() - 0.5) * (AQUARIUM.height - 6),
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            fishGroup.position.copy(pos);
            fishGroup.scale.setScalar(scale);
            scene.add(fishGroup);

            const fish = {
                mesh: fishGroup,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                topFin: topFin,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 2,
                    (Math.random() - 0.5) * 0.5,
                    (Math.random() - 0.5) * 2
                ).normalize(),
                speed: 1.5 + Math.random() * 2.5,
                tailSpeed: 3 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2.5 + Math.random() * 1.5,
                scale: scale,
                wanderTimer: Math.random() * 3,
                wanderInterval: 2 + Math.random() * 4
            };

            fishArray.push(fish);
            updateStats();
        }

        // === BUBBLES ===
        function createBubble(customPos) {
            const size = 0.1 + Math.random() * 0.25;
            const bubbleGeo = new THREE.SphereGeometry(size, 12, 12);
            const bubbleMat = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3,
                transmission: 0.9,
                roughness: 0.0,
                metalness: 0.0,
                clearcoat: 1.0
            });

            const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
            const pos = customPos || new THREE.Vector3(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                -HALF.y + Math.random() * AQUARIUM.height,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            bubble.position.copy(pos);
            scene.add(bubble);

            bubbles.push({
                mesh: bubble,
                speed: 0.5 + Math.random() * 1.5,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 1 + Math.random() * 2,
                wobbleAmp: 0.3 + Math.random() * 0.5
            });
        }

        // === FOOD ===
        function createFood(position) {
            const foodGeo = new THREE.SphereGeometry(0.2, 8, 8);
            const foodMat = new THREE.MeshStandardMaterial({
                color: 0x8B4513,
                roughness: 0.8,
                emissive: 0x4a2000,
                emissiveIntensity: 0.3
            });
            const food = new THREE.Mesh(foodGeo, foodMat);
            food.position.copy(position);
            food.castShadow = true;
            scene.add(food);

            foods.push({
                mesh: food,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 0.5,
                    0,
                    (Math.random() - 0.5) * 0.5
                ),
                gravity: -2.0,
                eaten: false
            });
            updateStats();
        }

        // === FEEDING ===
        function onFeedClick(event) {
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            // Intersect with a plane at y=0 (water surface area)
            const planeGeo = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth);
            const planeMesh = new THREE.Mesh(planeGeo);
            planeMesh.rotation.x = -Math.PI / 2;
            planeMesh.position.y = HALF.y - 1;

            const intersects = raycaster.intersectObject(planeMesh);

            if (intersects.length > 0) {
                const point = intersects[0].point.clone();
                point.x = Math.max(-HALF.x + 2, Math.min(HALF.x - 2, point.x));
                point.z = Math.max(-HALF.z + 2, Math.min(HALF.z - 2, point.z));
                point.y = HALF.y - 1;

                // Create multiple food particles
                for (let i = 0; i < 3 + Math.floor(Math.random() * 3); i++) {
                    const offset = new THREE.Vector3(
                        (Math.random() - 0.5) * 2,
                        0,
                        (Math.random() - 0.5) * 2
                    );
                    createFood(point.clone().add(offset));
                }
            }

            planeMesh.geometry.dispose();
        }

        function feedAll() {
            for (let i = 0; i < 8; i++) {
                const pos = new THREE.Vector3(
                    (Math.random() - 0.5) * (AQUARIUM.width - 6),
                    HALF.y - 1,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                );
                createFood(pos);
            }
        }

        // === UPDATE FISH ===
        function updateFish(delta, time) {
            fishArray.forEach(fish => {
                const pos = fish.mesh.position;

                // Food seeking
                let nearestFood = null;
                let nearestDist = 15;

                foods.forEach(food => {
                    if (food.eaten) return;
                    const dist = pos.distanceTo(food.mesh.position);
                    if (dist < nearestDist) {
                        nearestDist = dist;
                        nearestFood = food;
                    }
                });

                if (nearestFood) {
                    fish.targetFood = nearestFood;
                    const dir = new THREE.Vector3().subVectors(nearestFood.mesh.position, pos).normalize();
                    fish.velocity.lerp(dir, 0.05);

                    // Eat food
                    if (nearestDist < 1.5) {
                        nearestFood.eaten = true;
                        scene.remove(nearestFood.mesh);
                        nearestFood.mesh.geometry.dispose();
                        fish.targetFood = null;
                        // Grow fish
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                        updateStats();
                    }
                } else {
                    fish.targetFood = null;
                }

                // Wandering
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.wanderTimer = fish.wanderInterval;
                    const wander = new THREE.Vector3(
                        (Math.random() - 0.5) * 2,
                        (Math.random() - 0.5) * 0.8,
                        (Math.random() - 0.5) * 2
                    ).normalize();
                    fish.velocity.lerp(wander, 0.3);
                }

                // Avoidance
                fishArray.forEach(other => {
                    if (other === fish) return;
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0) {
                        const repel = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        repel.multiplyScalar(0.05 / Math.max(dist, 0.5));
                        fish.velocity.add(repel);
                    }
                });

                // Wall avoidance
                const margin = 2;
                const wallForce = new THREE.Vector3(0, 0, 0);
                if (pos.x > HALF.x - margin) wallForce.x -= 0.1;
                if (pos.x < -HALF.x + margin) wallForce.x += 0.1;
                if (pos.y > HALF.y - margin) wallForce.y -= 0.1;
                if (pos.y < -HALF.y + margin) wallForce.y += 0.1;
                if (pos.z > HALF.z - margin) wallForce.z -= 0.1;
                if (pos.z < -HALF.z + margin) wallForce.z += 0.1;
                fish.velocity.add(wallForce);

                // Normalize and apply speed
                fish.velocity.normalize();
                const speed = fish.targetFood ? fish.speed * 1.5 : fish.speed;
                pos.add(fish.velocity.clone().multiplyScalar(speed * delta));

                // Clamp position
                pos.x = Math.max(-HALF.x + 1, Math.min(HALF.x - 1, pos.x));
                pos.y = Math.max(-HALF.y + 1, Math.min(HALF.y - 1, pos.y));
                pos.z = Math.max(-HALF.z + 1, Math.min(HALF.z - 1, pos.z));

                // Rotate to face direction
                const targetAngle = Math.atan2(fish.velocity.z, fish.velocity.x);
                fish.mesh.rotation.y = -targetAngle + Math.PI;

                // Slight tilt based on vertical velocity
                fish.mesh.rotation.z = -fish.velocity.y * 0.3;

                // Animate tail
                const tailAngle = Math.sin(time * fish.tailSpeed + fish.phase) * 0.5;
                fish.tail.rotation.y = tailAngle;

                // Animate fins
                const finAngle = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase + 1) * 0.3;
                fish.leftFin.rotation.x = 0.5 + finAngle;
                fish.rightFin.rotation.x = -0.5 - finAngle;
                fish.topFin.rotation.z = -0.3 + Math.sin(time * 2 + fish.phase) * 0.1;
            });
        }

        // === UPDATE BUBBLES ===
        function updateBubbles(delta, time) {
            bubbles.forEach(bubble => {
                bubble.mesh.position.y += bubble.speed * delta;
                bubble.mesh.position.x += Math.sin(time * bubble.wobbleSpeed + bubble.wobblePhase) * bubble.wobbleAmp * delta;
                bubble.mesh.position.z += Math.cos(time * bubble.wobbleSpeed * 0.7 + bubble.wobblePhase) * bubble.wobbleAmp * delta * 0.5;

                // Reset if at top
                if (bubble.mesh.position.y > HALF.y - 0.5) {
                    bubble.mesh.position.y = -HALF.y + 0.5;
                    bubble.mesh.position.x = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                    bubble.mesh.position.z = (Math.random() - 0.5) * (AQUARIUM.depth - 4);
                }
            });
        }

        // === UPDATE FOOD ===
        function updateFood(delta) {
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                if (food.eaten) {
                    foods.splice(i, 1);
                    continue;
                }

                food.velocity.y += food.gravity * delta;
                food.mesh.position.add(food.velocity.clone().multiplyScalar(delta));

                // Remove if hits bottom
                if (food.mesh.position.y < -HALF.y + 0.5) {
                    scene.remove(food.mesh);
                    food.mesh.geometry.dispose();
                    foods.splice(i, 1);
                    updateStats();
                }
            }
        }

        // === UPDATE SEAWEED ===
        function updateSeaweeds(time) {
            seaweeds.forEach(sw => {
                sw.mesh.rotation.x = Math.sin(time * sw.speed + sw.phase) * sw.amplitude;
                sw.mesh.rotation.z = Math.cos(time * sw.speed * 0.8 + sw.phase) * sw.amplitude * 0.7;
            });
        }

        // === UI ===
        function addFish() {
            createFish();
        }

        function addBubbles() {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
            updateStats();
        }

        function toggleLight() {
            lightOn = !lightOn;
            directionalLight.intensity = lightOn ? 0.8 : 0.1;
        }

        function updateStats() {
            document.getElementById('fish-count').textContent = fishArray.length;
            document.getElementById('bubble-count').textContent = bubbles.length;
            document.getElementById('food-count').textContent = foods.length;
        }

        // === RESIZE ===
        function onResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // === ANIMATE ===
        function animate() {
            requestAnimationFrame(animate);

            const delta = Math.min(clock.getDelta(), 0.05);
            const time = clock.getElapsedTime();

            // FPS counter
            frameCount++;
            if (time - lastFpsTime >= 1) {
                document.getElementById('fps-counter').textContent = frameCount;
                frameCount = 0;
                lastFpsTime = time;
            }

            updateFish(delta, time);
            updateBubbles(delta, time);
            updateFood(delta);
            updateSeaweeds(time);

            controls.update();
            renderer.render(scene, camera);
        }

        // === START ===
        init();
    </script>
</body>
</html>
```

Этот файл содержит полноценный интерактивный 3D аквариум со всеми запрошенными функциями:

**🐠 Рыбки (15 шт.):**
- Детализированная анатомия: тело, глаза с зрачками, хвост, верхний и боковые плавники
- 8 цветовых схем, случайный масштаб 0.6–1.2
- Анимация хвоста и плавников с индивидуальной частотой

**🧠 ИИ поведение:**
- Избегание столкновений между рыбками
- Отражение от стен аквариума
- Случайное блуждание с таймером
- Преследование корма в радиусе 15 единиц
- Рост на 5% при поедании корма

**🌊 Окружение:**
- Стеклянный контейнер 36×24×20 с `transmission: 0.95`
- Песчаное дно с процедурными неровностями
- 8 деформированных камней с тенями
- 12 кустов водорослей (TubeGeometry + CatmullRomCurve3) с анимацией покачивания

**💭 Пузыри:** 30 прозрачных сфер с эффектом стекла, движущихся вверх с покачиванием

**🍽️ Кормление:** клик по аквариуму создаёт корм с гравитацией

**💡 Освещение:** Ambient + Directional (с тенями 2048×2048) + 2 PointLight + переключаемый режим

**🎮 Управление:** OrbitControls с damping, зумом и ограничениями