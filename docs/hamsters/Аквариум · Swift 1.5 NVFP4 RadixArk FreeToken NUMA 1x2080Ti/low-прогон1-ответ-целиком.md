

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Аквариум с Реалистичными Рыбками</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(180deg, #0a1628 0%, #1a3a5c 50%, #0d2847 100%);
        }

        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
        }

        .panel {
            position: fixed;
            padding: 20px;
            border-radius: 16px;
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            color: #e0f0ff;
            z-index: 100;
            transition: all 0.3s ease;
        }

        .panel:hover {
            border-color: rgba(100, 180, 255, 0.4);
            box-shadow: 0 8px 40px rgba(0, 100, 255, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }

        .info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        .info-panel h1 {
            font-size: 1.4em;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #42a5f5, #1e88e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
        }

        .info-panel p {
            font-size: 0.82em;
            line-height: 1.6;
            opacity: 0.85;
            margin-bottom: 6px;
        }

        .info-panel .instructions {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(100, 180, 255, 0.15);
        }

        .stats-panel {
            top: 20px;
            right: 20px;
            min-width: 160px;
        }

        .stats-panel h2 {
            font-size: 1em;
            margin-bottom: 10px;
            color: #64b5f6;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 0.85em;
        }

        .stat-value {
            color: #4fc3f7;
            font-weight: bold;
        }

        .btn-group {
            margin-top: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.82em;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, #1565c0, #1976d2, #1e88e5);
            box-shadow: 0 4px 15px rgba(21, 101, 192, 0.4);
            transition: all 0.25s ease;
            text-align: center;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(21, 101, 192, 0.6);
            background: linear-gradient(135deg, #1976d2, #1e88e5, #42a5f5);
        }

        .btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 10px rgba(21, 101, 192, 0.3);
        }

        .btn-green {
            background: linear-gradient(135deg, #2e7d32, #388e3c, #43a047);
            box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);
        }

        .btn-green:hover {
            background: linear-gradient(135deg, #388e3c, #43a047, #4caf50);
            box-shadow: 0 6px 20px rgba(46, 125, 50, 0.6);
        }

        .btn-purple {
            background: linear-gradient(135deg, #6a1b9a, #7b1fa2, #8e24aa);
            box-shadow: 0 4px 15px rgba(106, 27, 154, 0.4);
        }

        .btn-purple:hover {
            background: linear-gradient(135deg, #7b1fa2, #8e24aa, #ab47bc);
            box-shadow: 0 6px 20px rgba(106, 27, 154, 0.6);
        }

        .btn-orange {
            background: linear-gradient(135deg, #e65100, #ef6c00, #f57c00);
            box-shadow: 0 4px 15px rgba(230, 81, 0, 0.4);
        }

        .btn-orange:hover {
            background: linear-gradient(135deg, #ef6c00, #f57c00, #fb8c00);
            box-shadow: 0 6px 20px rgba(230, 81, 0, 0.6);
        }

        .light-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4caf50;
            margin-right: 6px;
            box-shadow: 0 0 6px #4caf50;
        }

        .light-indicator.off {
            background: #f44336;
            box-shadow: 0 0 6px #f44336;
        }

        @media (max-width: 768px) {
            .info-panel {
                max-width: 220px;
                padding: 14px;
            }
            .info-panel h1 {
                font-size: 1.1em;
            }
            .info-panel p {
                font-size: 0.75em;
            }
            .stats-panel {
                min-width: 130px;
                padding: 14px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>Интерактивный 3D аквариум с реалистичными рыбками</p>
        <div class="instructions">
            <p>🖱️ Левый клик + движение — вращение</p>
            <p>🖱️ Правый клик + движение — панорама</p>
            <p>🖱️ Колесо мыши — масштаб</p>
            <p>🍽️ Клик по аквариуму — кормление</p>
        </div>
        <div class="btn-group">
            <button class="btn btn-green" onclick="addFish()">🐟 Добавить рыбку</button>
            <button class="btn btn-purple" onclick="addBubbles()">💭 Больше пузырей</button>
            <button class="btn btn-orange" onclick="toggleLight()">
                <span class="light-indicator" id="lightIndicator"></span>Свет вкл/выкл
            </button>
        </div>
    </div>

    <div class="panel stats-panel">
        <h2>📊 Статистика</h2>
        <div class="stat-item">
            <span>Рыбки:</span>
            <span class="stat-value" id="fishCount">0</span>
        </div>
        <div class="stat-item">
            <span>Пузыри:</span>
            <span class="stat-value" id="bubbleCount">0</span>
        </div>
        <div class="stat-item">
            <span>Корм:</span>
            <span class="stat-value" id="foodCount">0</span>
        </div>
        <div class="stat-item">
            <span>FPS:</span>
            <span class="stat-value" id="fpsCounter">60</span>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
        let scene, camera, renderer, controls;
        let fishArray = [];
        let bubbles = [];
        let foodItems = [];
        let seaweeds = [];
        let raycaster, mouse;
        let clock;
        let directionalLight;
        let lightOn = true;
        let frameCount = 0;
        let lastTime = performance.now();

        // Границы аквариума
        const AQUARIUM = { width: 36, height: 24, depth: 20 };
        const HALF = { x: AQUARIUM.width / 2, y: AQUARIUM.height / 2, z: AQUARIUM.depth / 2 };

        // Цветовые схемы рыбок
        const FISH_COLORS = [
            { body: 0xff6600, fin: 0xff9933, name: 'orange' },
            { body: 0x2266cc, fin: 0x4488ee, name: 'blue' },
            { body: 0xffcc00, fin: 0xff3300, name: 'yellow-red' },
            { body: 0x8833cc, fin: 0xaa55ee, name: 'purple' },
            { body: 0xcc2222, fin: 0xff4444, name: 'red' },
            { body: 0x22aa44, fin: 0x44cc66, name: 'green' },
            { body: 0xff66aa, fin: 0xff88cc, name: 'pink' },
            { body: 0xddaa22, fin: 0xffcc44, name: 'gold' }
        ];

        // === ИНИЦИАЛИЗАЦИЯ ===
        function init() {
            clock = new THREE.Clock();
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1e3d);
            scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

            // Камера
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
            camera.position.set(30, 18, 35);

            // Рендерер
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // Контролы
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.08;
            controls.minDistance = 10;
            controls.maxDistance = 60;
            controls.maxPolarAngle = Math.PI / 1.8;
            controls.target.set(0, 0, 0);

            // Raycaster
            raycaster = new THREE.Raycaster();
            mouse = new THREE.Vector2();

            // Создание сцены
            createLighting();
            createAquarium();
            createSandyBottom();
            createRocks();
            createSeaweeds();
            createInitialFish();
            createInitialBubbles();

            // События
            window.addEventListener('resize', onResize);
            renderer.domElement.addEventListener('click', onClickFeed);

            // Запуск
            animate();
            updateStats();
        }

        // === ОСВЕЩЕНИЕ ===
        function createLighting() {
            // Фоновое освещение
            const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
            scene.add(ambientLight);

            // Направленный свет (солнце)
            directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(15, 30, 10);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            directionalLight.shadow.camera.near = 1;
            directionalLight.shadow.camera.far = 80;
            directionalLight.shadow.camera.left = -25;
            directionalLight.shadow.camera.right = 25;
            directionalLight.shadow.camera.top = 25;
            directionalLight.shadow.camera.bottom = -25;
            directionalLight.shadow.bias = -0.001;
            scene.add(directionalLight);

            // Подводные точечные источники света
            const pointLight1 = new THREE.PointLight(0x4488ff, 0.6, 40);
            pointLight1.position.set(-10, 8, 5);
            scene.add(pointLight1);

            const pointLight2 = new THREE.PointLight(0x2266cc, 0.5, 35);
            pointLight2.position.set(10, -5, -5);
            scene.add(pointLight2);

            // Каустика (имитация через дополнительные источники)
            const causticLight = new THREE.PointLight(0x66ccff, 0.3, 30);
            causticLight.position.set(0, 12, 0);
            scene.add(causticLight);
        }

        // === АКВАРИУМ (СТЕКЛО) ===
        function createAquarium() {
            // Стеклянные стенки
            const glassMaterial = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                transparent: true,
                opacity: 0.15,
                transmission: 0.95,
                roughness: 0.05,
                metalness: 0,
                side: THREE.DoubleSide
            });

            const wallThickness = 0.3;

            // Задняя стенка
            const backWall = new THREE.Mesh(
                new THREE.BoxGeometry(AQUARIUM.width, AQUARIUM.height, wallThickness),
                glassMaterial
            );
            backWall.position.set(0, 0, -HALF.z);
            scene.add(backWall);

            // Передняя стенка
            const frontWall = new THREE.Mesh(
                new THREE.BoxGeometry(AQUARIUM.width, AQUARIUM.height, wallThickness),
                glassMaterial
            );
            frontWall.position.set(0, 0, HALF.z);
            scene.add(frontWall);

            // Левая стенка
            const leftWall = new THREE.Mesh(
                new THREE.BoxGeometry(wallThickness, AQUARIUM.height, AQUARIUM.depth),
                glassMaterial
            );
            leftWall.position.set(-HALF.x, 0, 0);
            scene.add(leftWall);

            // Правая стенка
            const rightWall = new THREE.Mesh(
                new THREE.BoxGeometry(wallThickness, AQUARIUM.height, AQUARIUM.depth),
                glassMaterial
            );
            rightWall.position.set(HALF.x, 0, 0);
            scene.add(rightWall);

            // Верхняя рамка (wireframe)
            const edgesGeometry = new THREE.EdgesGeometry(
                new THREE.BoxGeometry(AQUARIUM.width, AQUARIUM.height, AQUARIUM.depth)
            );
            const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.6 });
            const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
            scene.add(edges);
        }

        // === ПЕСЧАНОЕ ДНО ===
        function createSandyBottom() {
            const sandGeometry = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth, 40, 40);
            const positions = sandGeometry.attributes.position;

            for (let i = 0; i < positions.count; i++) {
                const x = positions.getX(i);
                const y = positions.getY(i);
                const z = Math.sin(x * 0.5) * 0.3 + Math.cos(y * 0.7) * 0.2 + Math.random() * 0.15;
                positions.setZ(i, z);
            }
            sandGeometry.computeVertexNormals();

            const sandMaterial = new THREE.MeshStandardMaterial({
                color: 0xd4a855,
                roughness: 0.9,
                metalness: 0.1
            });

            const sand = new THREE.Mesh(sandGeometry, sandMaterial);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = -HALF.y + 0.1;
            sand.receiveShadow = true;
            scene.add(sand);
        }

        // === КАМНИ ===
        function createRocks() {
            for (let i = 0; i < 8; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const geometry = new THREE.DodecahedronGeometry(size, 1);
                const positions = geometry.attributes.position;

                for (let j = 0; j < positions.count; j++) {
                    positions.setX(j, positions.getX(j) + (Math.random() - 0.5) * 0.3);
                    positions.setY(j, positions.getY(j) + (Math.random() - 0.5) * 0.3);
                    positions.setZ(j, positions.getZ(j) + (Math.random() - 0.5) * 0.3);
                }
                geometry.computeVertexNormals();

                const gray = 0.3 + Math.random() * 0.3;
                const material = new THREE.MeshStandardMaterial({
                    color: new THREE.Color(gray, gray * 0.9, gray * 0.8),
                    roughness: 0.85,
                    metalness: 0.05
                });

                const rock = new THREE.Mesh(geometry, material);
                rock.position.set(
                    (Math.random() - 0.5) * (AQUARIUM.width - 6),
                    -HALF.y + size * 0.5,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                );
                rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
                rock.castShadow = true;
                rock.receiveShadow = true;
                scene.add(rock);
            }
        }

        // === ВОДОРОСЛИ ===
        function createSeaweeds() {
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
                const tubeGeometry = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);

                const green = 0.3 + Math.random() * 0.4;
                const material = new THREE.MeshStandardMaterial({
                    color: new THREE.Color(0.1, green, 0.15),
                    roughness: 0.7,
                    metalness: 0.0,
                    side: THREE.DoubleSide
                });

                const seaweed = new THREE.Mesh(tubeGeometry, material);
                seaweed.position.set(
                    (Math.random() - 0.5) * (AQUARIUM.width - 4),
                    -HALF.y + 0.2,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 3)
                );
                seaweed.castShadow = true;
                scene.add(seaweed);

                seaweeds.push({
                    mesh: seaweed,
                    phase: Math.random() * Math.PI * 2,
                    speed: 0.5 + Math.random() * 1.0,
                    amplitude: 0.03 + Math.random() * 0.04
                });
            }
        }

        // === СОЗДАНИЕ РЫБКИ ===
        function createFish(colorScheme, position) {
            const group = new THREE.Group();
            const scale = 0.6 + Math.random() * 0.6;

            // Тело
            const bodyGeometry = new THREE.SphereGeometry(1, 16, 12);
            bodyGeometry.scale(1.4, 0.7, 0.5);
            const bodyMaterial = new THREE.MeshStandardMaterial({
                color: colorScheme.body,
                roughness: 0.3,
                metalness: 0.2,
                emissive: colorScheme.body,
                emissiveIntensity: 0.05
            });
            const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
            body.castShadow = true;
            group.add(body);

            // Глаза
            const eyeGeometry = new THREE.SphereGeometry(0.2, 8, 8);
            const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeometry = new THREE.SphereGeometry(0.1, 6, 6);
            const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
            leftEye.position.set(0.9, 0.15, 0.3);
            group.add(leftEye);

            const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
            leftPupil.position.set(1.0, 0.15, 0.35);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
            rightEye.position.set(0.9, 0.15, -0.3);
            group.add(rightEye);

            const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
            rightPupil.position.set(1.0, 0.15, -0.35);
            group.add(rightPupil);

            // Хвост
            const tailGeometry = new THREE.ConeGeometry(0.5, 1.2, 6);
            tailGeometry.rotateZ(Math.PI / 2);
            const tailMaterial = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                metalness: 0.1,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.85
            });
            const tail = new THREE.Mesh(tailGeometry, tailMaterial);
            tail.position.set(-1.6, 0, 0);
            tail.castShadow = true;
            group.add(tail);

            // Верхний плавник
            const topFinGeometry = new THREE.ConeGeometry(0.3, 0.8, 4);
            const topFinMaterial = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.8
            });
            const topFin = new THREE.Mesh(topFinGeometry, topFinMaterial);
            topFin.position.set(0.2, 0.6, 0);
            topFin.rotation.z = -0.2;
            group.add(topFin);

            // Боковые плавники
            const sideFinGeometry = new THREE.ConeGeometry(0.25, 0.6, 4);
            sideFinGeometry.rotateX(Math.PI / 2);

            const leftFin = new THREE.Mesh(sideFinGeometry, topFinMaterial.clone());
            leftFin.position.set(0.2, -0.2, 0.45);
            leftFin.rotation.z = 0.3;
            group.add(leftFin);

            const rightFin = new THREE.Mesh(sideFinGeometry, topFinMaterial.clone());
            rightFin.position.set(0.2, -0.2, -0.45);
            rightFin.rotation.z = -0.3;
            group.add(rightFin);

            // Нос (рот)
            const noseGeometry = new THREE.SphereGeometry(0.25, 6, 6);
            const noseMaterial = new THREE.MeshStandardMaterial({
                color: colorScheme.body,
                roughness: 0.3,
                metalness: 0.2
            });
            const nose = new THREE.Mesh(noseGeometry, noseMaterial);
            nose.position.set(1.3, 0, 0);
            nose.scale.set(0.8, 0.6, 0.6);
            group.add(nose);

            group.scale.setScalar(scale);
            group.position.copy(position);
            scene.add(group);

            const fishData = {
                mesh: group,
                tail: tail,
                topFin: topFin,
                leftFin: leftFin,
                rightFin: rightFin,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 2,
                    (Math.random() - 0.5) * 0.5,
                    (Math.random() - 0.5) * 2
                ).normalize(),
                speed: 1.5 + Math.random() * 2.5,
                tailSpeed: 3 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 3 + Math.random() * 2,
                scale: scale,
                wanderTimer: Math.random() * 5,
                wanderInterval: 2 + Math.random() * 4
            };

            fishArray.push(fishData);
            return fishData;
        }

        // === НАЧАЛЬНЫЕ РЫБКИ ===
        function createInitialFish() {
            for (let i = 0; i < 15; i++) {
                const colorScheme = FISH_COLORS[i % FISH_COLORS.length];
                const position = new THREE.Vector3(
                    (Math.random() - 0.5) * (AQUARIUM.width - 8),
                    (Math.random() - 0.5) * (AQUARIUM.height - 6),
                    (Math.random() - 0.5) * (AQUARIUM.depth - 6)
                );
                createFish(colorScheme, position);
            }
        }

        // === ПУЗЫРИ ===
        function createBubble(position) {
            const size = 0.1 + Math.random() * 0.25;
            const geometry = new THREE.SphereGeometry(size, 8, 8);
            const material = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3,
                transmission: 0.9,
                roughness: 0.0,
                metalness: 0.0,
                ior: 1.33
            });
            const bubble = new THREE.Mesh(geometry, material);
            bubble.position.copy(position);
            scene.add(bubble);

            bubbles.push({
                mesh: bubble,
                speed: 0.5 + Math.random() * 1.5,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 1 + Math.random() * 2,
                wobbleAmplitude: 0.3 + Math.random() * 0.5
            });
        }

        function createInitialBubbles() {
            for (let i = 0; i < 30; i++) {
                const position = new THREE.Vector3(
                    (Math.random() - 0.5) * (AQUARIUM.width - 4),
                    (Math.random() - 0.5) * (AQUARIUM.height - 4),
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                );
                createBubble(position);
            }
        }

        // === КОРМ ===
        function createFood(position) {
            const geometry = new THREE.SphereGeometry(0.2, 6, 6);
            const material = new THREE.MeshStandardMaterial({
                color: 0x8B4513,
                roughness: 0.8
            });
            const food = new THREE.Mesh(geometry, material);
            food.position.copy(position);
            food.position.y = HALF.y - 1;
            scene.add(food);

            foodItems.push({
                mesh: food,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 0.5,
                    0,
                    (Math.random() - 0.5) * 0.5
                ),
                gravity: -2.0
            });
        }

        // === ОБНОВЛЕНИЕ РЫБОК ===
        function updateFish(delta, time) {
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;
                let steer = new THREE.Vector3(0, 0, 0);

                // 1. Избегание столкновений
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j].mesh.position;
                    const dist = pos.distanceTo(other);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const repel = pos.clone().sub(other).normalize();
                        repel.multiplyScalar(1.0 / Math.max(dist, 0.5));
                        steer.add(repel);
                    }
                }

                // 2. Преследование корма
                fish.targetFood = null;
                let closestFoodDist = 15;
                for (let k = 0; k < foodItems.length; k++) {
                    const food = foodItems[k];
                    const dist = pos.distanceTo(food.mesh.position);
                    if (dist < closestFoodDist) {
                        closestFoodDist = dist;
                        fish.targetFood = food;
                    }
                    // Съедание
                    if (dist < 1.0) {
                        scene.remove(food.mesh);
                        foodItems.splice(k, 1);
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                        k--;
                    }
                }

                if (fish.targetFood) {
                    const toFood = fish.targetFood.mesh.position.clone().sub(pos).normalize();
                    steer.add(toFood.multiplyScalar(3.0));
                }

                // 3. Случайное блуждание
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.wanderTimer = fish.wanderInterval;
                    fish.velocity.x += (Math.random() - 0.5) * 1.5;
                    fish.velocity.y += (Math.random() - 0.5) * 0.8;
                    fish.velocity.z += (Math.random() - 0.5) * 1.5;
                }

                // 4. Отражение от стен
                const margin = 3;
                if (pos.x > HALF.x - margin) steer.x -= 2.0;
                if (pos.x < -HALF.x + margin) steer.x += 2.0;
                if (pos.y > HALF.y - margin) steer.y -= 2.0;
                if (pos.y < -HALF.y + margin) steer.y += 2.0;
                if (pos.z > HALF.z - margin) steer.z -= 2.0;
                if (pos.z < -HALF.z + margin) steer.z += 2.0;

                // Применение steering
                fish.velocity.add(steer.multiplyScalar(delta * 2.0));

                // Ограничение скорости
                const maxSpeed = fish.speed * (fish.targetFood ? 1.5 : 1.0);
                if (fish.velocity.length() > maxSpeed) {
                    fish.velocity.normalize().multiplyScalar(maxSpeed);
                }

                // Ограничение Y (не выходить за дно)
                fish.velocity.y = Math.max(fish.velocity.y, -1.0);

                // Обновление позиции
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Жесткое ограничение
                pos.x = Math.max(-HALF.x + 1, Math.min(HALF.x - 1, pos.x));
                pos.y = Math.max(-HALF.y + 1, Math.min(HALF.y - 1, pos.y));
                pos.z = Math.max(-HALF.z + 1, Math.min(HALF.z - 1, pos.z));

                // Поворот в направлении движения
                if (fish.velocity.length() > 0.1) {
                    const targetAngle = Math.atan2(fish.velocity.z, fish.velocity.x);
                    const currentAngle = fish.mesh.rotation.y;
                    let angleDiff = targetAngle - currentAngle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                    fish.mesh.rotation.y += angleDiff * delta * 3.0;

                    // Наклон
                    fish.mesh.rotation.z = -fish.velocity.y * 0.15;
                }

                // Анимация хвоста
                fish.tail.rotation.y = Math.sin(time * fish.tailSpeed + fish.phase) * 0.6;
                fish.tail.rotation.z = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.2;

                // Анимация плавников
                fish.topFin.rotation.x = Math.sin(time * fish.tailSpeed * 0.5 + fish.phase) * 0.15;
                fish.leftFin.rotation.x = Math.sin(time * fish.tailSpeed * 0.8 + fish.phase + 1) * 0.3;
                fish.rightFin.rotation.x = Math.sin(time * fish.tailSpeed * 0.8 + fish.phase + 1) * -0.3;
            }
        }

        // === ОБНОВЛЕНИЕ ПУЗЫРЕЙ ===
        function updateBubbles(delta, time) {
            for (let i = bubbles.length - 1; i >= 0; i--) {
                const bubble = bubbles[i];
                const pos = bubble.mesh.position;

                pos.y += bubble.speed * delta;
                pos.x += Math.sin(time * bubble.wobbleSpeed + bubble.wobblePhase) * bubble.wobbleAmplitude * delta;
                pos.z += Math.cos(time * bubble.wobbleSpeed * 0.7 + bubble.wobblePhase) * bubble.wobbleAmplitude * delta;

                // Сброс при достижении поверхности
                if (pos.y > HALF.y - 0.5) {
                    pos.y = -HALF.y + 1;
                    pos.x = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                    pos.z = (Math.random() - 0.5) * (AQUARIUM.depth - 4);
                }
            }
        }

        // === ОБНОВЛЕНИЕ КОРМА ===
        function updateFood(delta) {
            for (let i = foodItems.length - 1; i >= 0; i--) {
                const food = foodItems[i];
                food.velocity.y += food.gravity * delta;
                food.mesh.position.add(food.velocity.clone().multiplyScalar(delta));

                // Удаление при достижении дна
                if (food.mesh.position.y < -HALF.y + 0.5) {
                    scene.remove(food.mesh);
                    foodItems.splice(i, 1);
                }
            }
        }

        // === ОБНОВЛЕНИЕ ВОДОРОСЛЕЙ ===
        function updateSeaweeds(time) {
            for (let i = 0; i < seaweeds.length; i++) {
                const sw = seaweeds[i];
                sw.mesh.rotation.x = Math.sin(time * sw.speed + sw.phase) * sw.amplitude;
                sw.mesh.rotation.z = Math.cos(time * sw.speed * 0.8 + sw.phase) * sw.amplitude * 0.7;
            }
        }

        // === АНИМАЦИЯ ===
        function animate() {
            requestAnimationFrame(animate);

            const delta = Math.min(clock.getDelta(), 0.05);
            const time = clock.getElapsedTime();

            updateFish(delta, time);
            updateBubbles(delta, time);
            updateFood(delta);
            updateSeaweeds(time);

            controls.update();
            renderer.render(scene, camera);

            // FPS
            frameCount++;
            const now = performance.now();
            if (now - lastTime >= 1000) {
                document.getElementById('fpsCounter').textContent = frameCount;
                frameCount = 0;
                lastTime = now;
                updateStats();
            }
        }

        // === КЛИК ДЛЯ КОРМЛЕНИЯ ===
        function onClickFeed(event) {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            // Создаем корм в точке, где луч пересекает верхнюю плоскость аквариума
            const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -(HALF.y - 1));
            const intersection = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersection);

            if (intersection) {
                intersection.x = Math.max(-HALF.x + 2, Math.min(HALF.x - 2, intersection.x));
                intersection.z = Math.max(-HALF.z + 2, Math.min(HALF.z - 2, intersection.z));
                createFood(intersection);
            }
        }

        // === КНОПКИ ===
        function addFish() {
            const colorScheme = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
            const position = new THREE.Vector3(
                (Math.random() - 0.5) * (AQUARIUM.width - 8),
                (Math.random() - 0.5) * (AQUARIUM.height - 6),
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            createFish(colorScheme, position);
            updateStats();
        }

        function addBubbles() {
            for (let i = 0; i < 10; i++) {
                const position = new THREE.Vector3(
                    (Math.random() - 0.5) * (AQUARIUM.width - 4),
                    -HALF.y + 1 + Math.random() * 3,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                );
                createBubble(position);
            }
            updateStats();
        }

        function toggleLight() {
            lightOn = !lightOn;
            directionalLight.intensity = lightOn ? 0.8 : 0.1;
            const indicator = document.getElementById('lightIndicator');
            indicator.className = lightOn ? 'light-indicator' : 'light-indicator off';
        }

        function updateStats() {
            document.getElementById('fishCount').textContent = fishArray.length;
            document.getElementById('bubbleCount').textContent = bubbles.length;
            document.getElementById('foodCount').textContent = foodItems.length;
        }

        // === RESIZE ===
        function onResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // === ЗАПУСК ===
        init();
    </script>
</body>
</html>
```

Этот файл содержит полноценный интерактивный 3D аквариум со всеми запрошенными функциями:

**🐠 Рыбки (15 на старте):**
- Детализированная анатомия: тело, глаза с зрачками, хвост, верхний и боковые плавники, нос
- 8 цветовых схем, случайный масштаб 0.6–1.2
- Плавная анимация хвоста и плавников с индивидуальной частотой

**🧠 ИИ:**
- Избегание столкновений, отражение от стен, случайное блуждание
- Преследование корма в радиусе 15 единиц, рост на 5% при поедании

**🌊 Окружение:**
- Стеклянный аквариум 36×24×20 с wireframe рамкой
- Песчаное дно с процедурными неровностями
- 8 деформированных камней, 12 анимированных водорослей

**💭 Пузыри:** 30 штук с эффектом стекла, движение вверх с покачиванием

**🍽️ Кормление:** клик создаёт корм с гравитацией, рыбки его обнаруживают и едят

**💡 Освещение:** Ambient + Directional (с тенями 2048×2048) + 2 PointLight, переключатель

**🎮 OrbitControls:** вращение, панорама, зум с damping

**🖥️ UI:** glass-панели с градиентами, статистика, FPS-счётчик, кнопки управления