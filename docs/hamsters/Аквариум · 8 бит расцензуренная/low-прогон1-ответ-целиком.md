

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
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        #info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        #info-panel h1 {
            font-size: 22px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #e040fb, #ffb74d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        }

        #info-panel .instructions {
            font-size: 12px;
            line-height: 1.8;
            opacity: 0.85;
            margin-bottom: 15px;
        }

        #info-panel .instructions span {
            display: inline-block;
            background: rgba(100, 180, 255, 0.15);
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 4px;
            font-size: 11px;
        }

        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .btn {
            padding: 8px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
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

        .btn-light.off {
            background: linear-gradient(135deg, #546e7a, #37474f);
            box-shadow: 0 4px 15px rgba(84, 110, 122, 0.4);
        }

        #stats-panel {
            top: 20px;
            right: 20px;
            min-width: 150px;
        }

        #stats-panel .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(100, 180, 255, 0.1);
            font-size: 13px;
        }

        #stats-panel .stat-item:last-child {
            border-bottom: none;
        }

        #stats-panel .stat-label {
            opacity: 0.7;
        }

        #stats-panel .stat-value {
            font-weight: 700;
            color: #64ffda;
        }

        #tooltip {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 30, 60, 0.8);
            backdrop-filter: blur(8px);
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 13px;
            color: rgba(200, 230, 255, 0.9);
            border: 1px solid rgba(100, 180, 255, 0.2);
            pointer-events: none;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.8; }
            50% { opacity: 1; }
        }

        @media (max-width: 768px) {
            #info-panel {
                max-width: 220px;
                padding: 15px;
            }
            #info-panel h1 {
                font-size: 18px;
            }
            #stats-panel {
                min-width: 120px;
                padding: 12px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel" id="info-panel">
        <h1>🐠 3D Аквариум</h1>
        <div class="instructions">
            <span>🖱️ ЛКМ</span> Вращение<br>
            <span>🖱️ ПКМ</span> Панорама<br>
            <span>⚙️ Колесо</span> Зум<br>
            <span>👆 Клик</span> Кормление
        </div>
        <div class="btn-group">
            <button class="btn btn-fish" onclick="addFish()">+ Рыбка</button>
            <button class="btn btn-bubbles" onclick="addBubbles()">+ Пузыри</button>
            <button class="btn btn-light" id="lightBtn" onclick="toggleLight()">💡 Свет</button>
        </div>
    </div>

    <div class="panel" id="stats-panel">
        <div class="stat-item">
            <span class="stat-label">Рыбки</span>
            <span class="stat-value" id="fish-count">15</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Пузыри</span>
            <span class="stat-value" id="bubble-count">30</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">FPS</span>
            <span class="stat-value" id="fps-counter">60</span>
        </div>
    </div>

    <div id="tooltip">Кликните по воде, чтобы покормить рыбок 🍤</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(0, 8, 35);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        // === CONTROLS ===
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 2, 0);

        // === LIGHTING ===
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 1.2);
        dirLight.position.set(10, 25, 15);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 80;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 25;
        dirLight.shadow.camera.bottom = -25;
        dirLight.shadow.bias = -0.001;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x00aaff, 0.8, 40);
        pointLight1.position.set(-10, 10, 5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x0066ff, 0.6, 35);
        pointLight2.position.set(10, 8, -5);
        scene.add(pointLight2);

        let lightOn = true;

        function toggleLight() {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.2 : 0.2;
            ambientLight.intensity = lightOn ? 0.4 : 0.15;
            document.getElementById('lightBtn').classList.toggle('off', !lightOn);
            document.getElementById('lightBtn').textContent = lightOn ? '💡 Свет' : '🌙 Тёмно';
        }

        // === AQUARIUM BOUNDS ===
        const AQUARIUM = { x: 18, y: 12, z: 10 };
        const FLOOR_Y = -AQUARIUM.y + 1;
        const CEIL_Y = AQUARIUM.y - 1;
        const WALL_X = AQUARIUM.x - 1;
        const WALL_Z = AQUARIUM.z - 1;

        // === BACKGROUND GRADIENT ===
        const bgCanvas = document.createElement('canvas');
        bgCanvas.width = 2;
        bgCanvas.height = 512;
        const bgCtx = bgCanvas.getContext('2d');
        const gradient = bgCtx.createLinearGradient(0, 0, 0, 512);
        gradient.addColorStop(0, '#0a1e3d');
        gradient.addColorStop(0.5, '#0d2d5e');
        gradient.addColorStop(1, '#071a35');
        bgCtx.fillStyle = gradient;
        bgCtx.fillRect(0, 0, 2, 512);
        const bgTexture = new THREE.CanvasTexture(bgCanvas);
        scene.background = bgTexture;

        // === GLASS CONTAINER ===
        function createAquariumTank() {
            const tankGeo = new THREE.BoxGeometry(AQUARIUM.x * 2, AQUARIUM.y * 2, AQUARIUM.z * 2);
            const tankMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                transparent: true,
                opacity: 0.08,
                roughness: 0.05,
                metalness: 0.1,
                side: THREE.DoubleSide
            });
            const tank = new THREE.Mesh(tankGeo, tankMat);
            tank.position.y = 0;
            scene.add(tank);

            // Wireframe edges
            const edgesGeo = new THREE.EdgesGeometry(tankGeo);
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x66aadd, transparent: true, opacity: 0.4 });
            const edges = new THREE.LineSegments(edgesGeo, edgesMat);
            edges.position.y = 0;
            scene.add(edges);
        }
        createAquariumTank();

        // === SANDY BOTTOM ===
        function createSandyBottom() {
            const sandGeo = new THREE.PlaneGeometry(AQUARIUM.x * 2, AQUARIUM.z * 2, 40, 40);
            const positions = sandGeo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                const x = positions.getX(i);
                const y = positions.getY(i);
                const noise = Math.sin(x * 0.5) * Math.cos(y * 0.3) * 0.15 +
                              Math.sin(x * 1.2 + y * 0.8) * 0.08 +
                              Math.random() * 0.05;
                positions.setZ(i, noise);
            }
            sandGeo.computeVertexNormals();

            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xd4a853,
                roughness: 0.95,
                metalness: 0.05
            });
            const sand = new THREE.Mesh(sandGeo, sandMat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = FLOOR_Y;
            sand.receiveShadow = true;
            scene.add(sand);
        }
        createSandyBottom();

        // === DECORATIVE ROCKS ===
        function createRocks() {
            const rockColors = [0x5a6b7a, 0x4a5a6a, 0x6b7b8a, 0x3a4a5a, 0x7a8a9a];
            for (let i = 0; i < 8; i++) {
                const size = 0.5 + Math.random() * 1.2;
                const geo = new THREE.DodecahedronGeometry(size, 1);
                const pos = geo.attributes.position;
                for (let j = 0; j < pos.count; j++) {
                    const x = pos.getX(j);
                    const y = pos.getY(j);
                    const z = pos.getZ(j);
                    const deform = 1 + (Math.random() - 0.5) * 0.4;
                    pos.setX(j, x * deform);
                    pos.setY(j, y * deform * (0.6 + Math.random() * 0.3));
                    pos.setZ(j, z * deform);
                }
                geo.computeVertexNormals();

                const mat = new THREE.MeshStandardMaterial({
                    color: rockColors[Math.floor(Math.random() * rockColors.length)],
                    roughness: 0.85,
                    metalness: 0.1
                });
                const rock = new THREE.Mesh(geo, mat);
                rock.position.set(
                    (Math.random() - 0.5) * (AQUARIUM.x * 1.6),
                    FLOOR_Y + size * 0.3,
                    (Math.random() - 0.5) * (AQUARIUM.z * 1.6)
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
        function createSeaweed(x, z) {
            const height = 2 + Math.random() * 4;
            const segments = 8;
            const points = [];
            for (let i = 0; i <= segments; i++) {
                const t = i / segments;
                points.push(new THREE.Vector3(
                    Math.sin(t * 3) * 0.3,
                    t * height,
                    Math.cos(t * 2) * 0.2
                ));
            }
            const curve = new THREE.CatmullRomCurve3(points);
            const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);
            const greenShade = 0.3 + Math.random() * 0.4;
            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color(0.1, greenShade, 0.15),
                roughness: 0.7,
                metalness: 0.05
            });
            const seaweed = new THREE.Mesh(tubeGeo, mat);
            seaweed.position.set(x, FLOOR_Y, z);
            seaweed.castShadow = true;
            scene.add(seaweed);
            seaweeds.push({ mesh: seaweed, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 });
        }

        for (let i = 0; i < 12; i++) {
            createSeaweed(
                (Math.random() - 0.5) * (AQUARIUM.x * 1.6),
                (Math.random() - 0.5) * (AQUARIUM.z * 1.6)
            );
        }

        // === FISH CREATION ===
        const fishColorSchemes = [
            { body: 0xff6600, fin: 0xffaa00, name: 'orange' },
            { body: 0x2196f3, fin: 0x64b5f6, name: 'blue' },
            { body: 0xffeb3b, fin: 0xf44336, name: 'yellow-red' },
            { body: 0x9c27b0, fin: 0xba68c8, name: 'purple' },
            { body: 0xf44336, fin: 0xef9a9a, name: 'red' },
            { body: 0x4caf50, fin: 0x81c784, name: 'green' },
            { body: 0xe91e63, fin: 0xf48fb1, name: 'pink' },
            { body: 0xffd700, fin: 0xfff176, name: 'gold' }
        ];

        const fishArray = [];

        function createFish(position) {
            const scheme = fishColorSchemes[Math.floor(Math.random() * fishColorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(0.5, 16, 12);
            bodyGeo.scale(1.8, 1, 0.8);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.4,
                metalness: 0.3
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.3, 0.6, 8);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.9
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.x = -1.0;
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.15, 0.4, 4);
            topFinGeo.rotateZ(Math.PI / 4);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.8
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0, 0.45, 0);
            group.add(topFin);

            // Left fin
            const leftFinGeo = new THREE.ConeGeometry(0.12, 0.35, 4);
            leftFinGeo.rotateX(Math.PI / 2);
            const leftFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.7
            });
            const leftFin = new THREE.Mesh(leftFinGeo, leftFinMat);
            leftFin.position.set(0.1, 0, 0.4);
            group.add(leftFin);

            // Right fin
            const rightFin = new THREE.Mesh(leftFinGeo.clone(), leftFinMat.clone());
            rightFin.position.set(0.1, 0, -0.4);
            rightFin.rotation.x = Math.PI;
            group.add(rightFin);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.08, 8, 8);
            const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.04, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            leftEye.position.set(0.55, 0.1, 0.2);
            group.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(0.62, 0.1, 0.2);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            rightEye.position.set(0.55, 0.1, -0.2);
            group.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(0.62, 0.1, -0.2);
            group.add(rightPupil);

            group.scale.setScalar(scale);
            if (position) {
                group.position.copy(position);
            } else {
                group.position.set(
                    (Math.random() - 0.5) * (AQUARIUM.x * 1.4),
                    FLOOR_Y + 2 + Math.random() * (AQUARIUM.y * 1.2),
                    (Math.random() - 0.5) * (AQUARIUM.z * 1.4)
                );
            }
            scene.add(group);

            const velocity = new THREE.Vector3(
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 0.5,
                (Math.random() - 0.5) * 2
            ).normalize().multiplyScalar(1.5 + Math.random() * 1.5);

            const fish = {
                mesh: group,
                tail: tail,
                topFin: topFin,
                leftFin: leftFin,
                rightFin: rightFin,
                velocity: velocity,
                speed: 1.5 + Math.random() * 1.5,
                tailSpeed: 4 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2 + Math.random() * 1.5,
                wanderTimer: Math.random() * 3,
                scale: scale
            };

            fishArray.push(fish);
            updateStats();
            return fish;
        }

        // Create initial fish
        for (let i = 0; i < 15; i++) {
            createFish();
        }

        // === BUBBLES ===
        const bubbles = [];
        const bubbleGeo = new THREE.SphereGeometry(0.1, 8, 8);
        const bubbleMat = new THREE.MeshPhysicalMaterial({
            color: 0xaaddff,
            transparent: true,
            opacity: 0.3,
            roughness: 0.1,
            metalness: 0.1
        });

        function createBubble() {
            const mesh = new THREE.Mesh(bubbleGeo, bubbleMat);
            const scale = 0.5 + Math.random() * 1.5;
            mesh.scale.setScalar(scale);
            mesh.position.set(
                (Math.random() - 0.5) * (AQUARIUM.x * 1.6),
                FLOOR_Y + Math.random() * (AQUARIUM.y * 1.5),
                (Math.random() - 0.5) * (AQUARIUM.z * 1.6)
            );
            scene.add(mesh);
            bubbles.push({
                mesh: mesh,
                speed: 0.5 + Math.random() * 1.0,
                phase: Math.random() * Math.PI * 2,
                amplitude: 0.2 + Math.random() * 0.5
            });
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        function addBubbles() {
            for (let i = 0; i < 10; i++) createBubble();
            updateStats();
        }

        // === FOOD SYSTEM ===
        const foodArray = [];
        const foodGeo = new THREE.SphereGeometry(0.15, 8, 8);
        const foodMat = new THREE.MeshStandardMaterial({ color: 0xff8844, roughness: 0.6, emissive: 0x442200 });

        function spawnFood(position) {
            const mesh = new THREE.Mesh(foodGeo, foodMat);
            mesh.position.copy(position);
            mesh.castShadow = true;
            scene.add(mesh);
            foodArray.push({
                mesh: mesh,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 0.5,
                    -0.5 - Math.random() * 0.5,
                    (Math.random() - 0.5) * 0.5
                ),
                life: 15
            });
        }

        // === RAYCASTER FOR CLICK ===
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let isDragging = false;
        let dragStart = new THREE.Vector2();

        renderer.domElement.addEventListener('mousedown', (e) => {
            dragStart.set(e.clientX, e.clientY);
            isDragging = false;
        });

        renderer.domElement.addEventListener('mousemove', (e) => {
            if (Math.abs(e.clientX - dragStart.x) > 5 || Math.abs(e.clientY - dragStart.y) > 5) {
                isDragging = true;
            }
        });

        renderer.domElement.addEventListener('click', (e) => {
            if (isDragging) return;
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
            const intersectPoint = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersectPoint);

            if (intersectPoint) {
                intersectPoint.x = THREE.MathUtils.clamp(intersectPoint.x, -WALL_X, WALL_X);
                intersectPoint.y = THREE.MathUtils.clamp(intersectPoint.y, FLOOR_Y + 1, CEIL_Y);
                intersectPoint.z = THREE.MathUtils.clamp(intersectPoint.z, -WALL_Z, WALL_Z);
                spawnFood(intersectPoint);
            }
        });

        // === ADD FISH BUTTON ===
        function addFish() {
            createFish();
        }

        // === STATS ===
        function updateStats() {
            document.getElementById('fish-count').textContent = fishArray.length;
            document.getElementById('bubble-count').textContent = bubbles.length;
        }

        // === ANIMATION LOOP ===
        const clock = new THREE.Clock();
        let fpsFrames = 0;
        let fpsTime = 0;

        function animate() {
            requestAnimationFrame(animate);
            const delta = Math.min(clock.getDelta(), 0.05);
            const elapsed = clock.elapsedTime;

            // FPS counter
            fpsFrames++;
            fpsTime += delta;
            if (fpsTime >= 0.5) {
                document.getElementById('fps-counter').textContent = Math.round(fpsFrames / fpsTime);
                fpsFrames = 0;
                fpsTime = 0;
            }

            // Update fish
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Wandering
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.wanderTimer = 2 + Math.random() * 4;
                    fish.velocity.x += (Math.random() - 0.5) * 0.8;
                    fish.velocity.y += (Math.random() - 0.5) * 0.3;
                    fish.velocity.z += (Math.random() - 0.5) * 0.8;
                }

                // Food seeking
                if (fish.targetFood) {
                    if (foodArray.includes(fish.targetFood)) {
                        const dir = fish.targetFood.mesh.position.clone().sub(pos);
                        const dist = dir.length();
                        if (dist > 0.5) {
                            dir.normalize();
                            fish.velocity.lerp(dir.multiplyScalar(fish.speed * 1.5), 0.05);
                        } else {
                            // Eat!
                            scene.remove(fish.targetFood.mesh);
                            fish.targetFood.mesh.geometry.dispose();
                            const idx = foodArray.indexOf(fish.targetFood);
                            if (idx !== -1) foodArray.splice(idx, 1);
                            fish.scale *= 1.05;
                            fish.mesh.scale.setScalar(fish.scale);
                            fish.targetFood = null;
                        }
                    } else {
                        fish.targetFood = null;
                    }
                } else {
                    // Check for nearby food
                    for (let f = 0; f < foodArray.length; f++) {
                        const dist = pos.distanceTo(foodArray[f].mesh.position);
                        if (dist < 15) {
                            fish.targetFood = foodArray[f];
                            break;
                        }
                    }
                }

                // Collision avoidance
                for (let j = i + 1; j < fishArray.length; j++) {
                    const other = fishArray[j];
                    const diff = pos.clone().sub(other.mesh.position);
                    const dist = diff.length();
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        diff.normalize();
                        const force = (fish.avoidanceRadius - dist) / fish.avoidanceRadius;
                        fish.velocity.add(diff.multiplyScalar(force * 2 * delta));
                        other.velocity.sub(diff.clone().normalize().multiplyScalar(force * 2 * delta));
                    }
                }

                // Wall bouncing
                if (pos.x > WALL_X) { fish.velocity.x -= 3 * delta; }
                if (pos.x < -WALL_X) { fish.velocity.x += 3 * delta; }
                if (pos.y > CEIL_Y) { fish.velocity.y -= 3 * delta; }
                if (pos.y < FLOOR_Y + 0.5) { fish.velocity.y += 3 * delta; }
                if (pos.z > WALL_Z) { fish.velocity.z -= 3 * delta; }
                if (pos.z < -WALL_Z) { fish.velocity.z += 3 * delta; }

                // Speed limit
                const spd = fish.velocity.length();
                if (spd > fish.speed) {
                    fish.velocity.normalize().multiplyScalar(fish.speed);
                }
                if (spd < 0.3) {
                    fish.velocity.setLength(0.3);
                }

                // Move
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Orient fish towards velocity
                if (fish.velocity.length() > 0.1) {
                    const targetQuat = new THREE.Quaternion();
                    const lookMatrix = new THREE.Matrix4();
                    const forward = fish.velocity.clone().normalize();
                    lookMatrix.lookAt(new THREE.Vector3(0, 0, 0), forward, new THREE.Vector3(0, 1, 0));
                    targetQuat.setFromRotationMatrix(lookMatrix);
                    fish.mesh.quaternion.slerp(targetQuat, 0.05);
                }

                // Tail animation
                fish.phase += fish.tailSpeed * delta;
                fish.tail.rotation.y = Math.sin(fish.phase) * 0.5;
                fish.topFin.rotation.z = Math.sin(fish.phase * 0.7) * 0.2;
                fish.leftFin.rotation.y = Math.sin(fish.phase * 0.8 + 1) * 0.3;
                fish.rightFin.rotation.y = Math.sin(fish.phase * 0.8 + 2) * 0.3;
            }

            // Update food
            for (let i = foodArray.length - 1; i >= 0; i--) {
                const food = foodArray[i];
                food.mesh.position.add(food.velocity.clone().multiplyScalar(delta));
                food.velocity.y -= 1.5 * delta; // gravity
                food.life -= delta;

                if (food.mesh.position.y <= FLOOR_Y + 0.2 || food.life <= 0) {
                    scene.remove(food.mesh);
                    food.mesh.geometry.dispose();
                    foodArray.splice(i, 1);
                    // Remove references
                    for (const fish of fishArray) {
                        if (fish.targetFood === food) fish.targetFood = null;
                    }
                }
            }

            // Update bubbles
            for (let i = 0; i < bubbles.length; i++) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * delta;
                b.mesh.position.x += Math.sin(elapsed * 2 + b.phase) * b.amplitude * delta;
                b.mesh.position.z += Math.cos(elapsed * 1.5 + b.phase) * b.amplitude * delta * 0.5;

                if (b.mesh.position.y > CEIL_Y) {
                    b.mesh.position.y = FLOOR_Y + 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * (AQUARIUM.x * 1.6);
                    b.mesh.position.z = (Math.random() - 0.5) * (AQUARIUM.z * 1.6);
                }
            }

            // Update seaweed
            for (const s of seaweeds) {
                s.mesh.rotation.x = Math.sin(elapsed * s.speed + s.phase) * 0.08;
                s.mesh.rotation.z = Math.cos(elapsed * s.speed * 0.7 + s.phase) * 0.06;
            }

            // Animate point lights subtly
            pointLight1.intensity = 0.7 + Math.sin(elapsed * 0.5) * 0.15;
            pointLight2.intensity = 0.5 + Math.cos(elapsed * 0.3) * 0.1;

            controls.update();
            renderer.render(scene, camera);
        }

        // === RESIZE ===
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
- Детализированная анатомия: тело (масштабированная сфера), хвост, верхний плавник, боковые плавники, глаза с зрачками
- 8 цветовых схем, случайный масштаб 0.6–1.2
- Анимация: махание хвостом, плавников, плавный поворот в сторону движения

### 🧠 ИИ поведения
- Избегание столкновений между рыбками
- Плавное отражение от стен аквариума
- Случайное блуждание с периодическим изменением курса
- Преследование корма в радиусе 15 единиц
- Рост на 5% после поедания корма

### 🌊 Окружение
- Стеклянный контейнер с wireframe-рамкой
- Песчаное дно с процедурными неровностями
- 8 декоративных камней (деформированные додекаэдры)
- 12 кустов водорослей (TubeGeometry + CatmullRomCurve3) с покачиванием

### 💭 Пузыри (30 шт.)
- Прозрачные сферы с движением вверх и синусоидальным покачиванием
- Автоматический сброс при достижении поверхности

### 🍽️ Кормление
- Клик по воде → создание корма с гравитацией
- Рыбки обнаруживают и плывут к еде
- Съедание → удаление + рост рыбки

### 🎮 Управление
- OrbitControls с damping, зумом, ограничением углов
- UI-панели: статистика, FPS, кнопки управления
- Переключаемое освещение