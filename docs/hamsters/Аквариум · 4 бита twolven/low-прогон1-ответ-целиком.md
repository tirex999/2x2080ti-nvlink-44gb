

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Аквариум — Реалистичные Рыбки</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(180deg, #0a1628 0%, #1a3a5c 50%, #2a5a8c 100%);
        }

        #canvas-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }

        .glass-panel {
            background: rgba(10, 30, 60, 0.65);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .info-panel {
            position: fixed;
            top: 20px;
            left: 20px;
            width: 280px;
            padding: 20px;
            z-index: 100;
            color: #e0f0ff;
        }

        .info-panel h1 {
            font-size: 1.4em;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #42a5f5, #1e88e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        .info-panel .instructions {
            font-size: 0.82em;
            line-height: 1.7;
            color: #a0c8e8;
            margin-bottom: 16px;
        }

        .info-panel .instructions strong {
            color: #7ecfff;
            font-weight: 600;
        }

        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .btn {
            padding: 8px 14px;
            border: none;
            border-radius: 10px;
            font-size: 0.78em;
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
            transition: left 0.5s ease;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.6);
        }

        .btn-bubbles {
            background: linear-gradient(135deg, #00b4d8, #0077b6);
            box-shadow: 0 4px 15px rgba(0, 180, 216, 0.4);
        }

        .btn-bubbles:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 180, 216, 0.6);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6);
        }

        .stats-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 20px;
            z-index: 100;
            color: #e0f0ff;
            min-width: 140px;
            text-align: center;
        }

        .stats-panel .stat-item {
            margin-bottom: 8px;
            font-size: 0.9em;
        }

        .stats-panel .stat-value {
            font-size: 1.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #4fc3f7, #29b6f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stats-panel .stat-label {
            font-size: 0.7em;
            color: #80b0d0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stats-panel .fps {
            font-size: 0.85em;
            color: #69f0ae;
        }

        @media (max-width: 768px) {
            .info-panel {
                width: calc(100% - 40px);
                max-height: 50vh;
                overflow-y: auto;
            }

            .stats-panel {
                top: auto;
                bottom: 20px;
                right: 20px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <!-- Info Panel -->
    <div class="glass-panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <div class="instructions">
            <strong>🖱️ ЛКМ + движение:</strong> вращение камеры<br>
            <strong>🖱️ ПКМ + движение:</strong> панорамирование<br>
            <strong>🖱️ Колесо:</strong> зум (10–60)<br>
            <strong>🍽️ Клик по воде:</strong> бросить корм<br>
            <strong>📈 Рост:</strong> рыбки растут при кормлении
        </div>
        <div class="btn-group">
            <button class="btn btn-fish" onclick="addFish()">+ Рыбка</button>
            <button class="btn btn-bubbles" onclick="addBubbles()">+ Пузыри</button>
            <button class="btn btn-light" onclick="toggleLight()">💡 Свет</button>
        </div>
    </div>

    <!-- Stats Panel -->
    <div class="glass-panel stats-panel">
        <div class="stat-item">
            <div class="stat-value" id="fish-count">15</div>
            <div class="stat-label">Рыбок</div>
        </div>
        <div class="stat-item">
            <div class="fps" id="fps-counter">60 FPS</div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        // ==================== GLOBALS ====================
        let scene, camera, renderer, controls;
        let clock = new THREE.Clock();
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();

        let fishArray = [];
        let bubbles = [];
        let foodItems = [];
        let seaweeds = [];
        let stones = [];

        let dirLight, pointLight1, pointLight2;
        let lightOn = true;

        // Aquarium dimensions
        const AQUA_W = 36;
        const AQUA_H = 24;
        const AQUA_D = 20;
        const FLOOR_Y = -AQUA_H / 2;
        const CEIL_Y = AQUA_H / 2;

        // Color schemes for fish
        const FISH_COLORS = [
            { body: 0xff6b35, fin: 0xffa040, name: "Оранжевая" },
            { body: 0x2196f3, fin: 0x64b5f6, name: "Синяя" },
            { body: 0xffeb3b, fin: 0xf44336, name: "Жёлто-красная" },
            { body: 0x9c27b0, fin: 0xce93d8, name: "Фиолетовая" },
            { body: 0xf44336, fin: 0xef9a9a, name: "Красная" },
            { body: 0x4caf50, fin: 0xa5d6a7, name: "Зелёная" },
            { body: 0xf48fb1, fin: 0xfce4ec, name: "Розовая" },
            { body: 0xffd700, fin: 0xfff176, name: "Золотая" }
        ];

        // FPS tracking
        let frameCount = 0;
        let lastFpsTime = 0;

        // ==================== INITIALIZATION ====================
        function init() {
            // Scene
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x0a2a4a, 0.008);

            // Camera
            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 200);
            camera.position.set(0, 5, 42);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.outputEncoding = THREE.sRGBEncoding;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.06;
            controls.minDistance = 10;
            controls.maxDistance = 60;
            controls.maxPolarAngle = Math.PI / 1.8;
            controls.target.set(0, 0, 0);

            // Build scene
            buildAquarium();
            buildLighting();
            createInitialFish(15);
            createInitialBubbles(30);
            createSeaweed(12);
            createStones(8);

            // Events
            window.addEventListener('resize', onResize);
            renderer.domElement.addEventListener('click', onClickCanvas);
            renderer.domElement.addEventListener('mousemove', onMouseMove);

            // Start
            lastFpsTime = performance.now();
            animate();
        }

        // ==================== AQUARIUM ENVIRONMENT ====================
        function buildAquarium() {
            // Glass container
            const glassGeo = new THREE.BoxGeometry(AQUA_W, AQUA_H, AQUA_D);
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                transparent: true,
                opacity: 0.12,
                roughness: 0.05,
                metalness: 0.1,
                transmission: 0.95,
                thickness: 0.5,
                side: THREE.DoubleSide
            });
            const glassBox = new THREE.Mesh(glassGeo, glassMat);
            glassBox.position.y = 0;
            scene.add(glassBox);

            // Wireframe edges
            const edgesGeo = new THREE.EdgesGeometry(glassGeo);
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x4488cc, transparent: true, opacity: 0.5 });
            const wireframe = new THREE.LineSegments(edgesGeo, edgesMat);
            wireframe.position.y = 0;
            scene.add(wireframe);

            // Sandy floor
            const floorGeo = new THREE.PlaneGeometry(AQUA_W, AQUA_D, 24, 16);
            const posAttr = floorGeo.attributes.position;
            for (let i = 0; i < posAttr.count; i++) {
                const x = posAttr.getX(i);
                const y = posAttr.getY(i);
                const noise = Math.sin(x * 0.4) * Math.cos(y * 0.3) * 0.3 + Math.random() * 0.08;
                posAttr.setZ(i, noise);
            }
            floorGeo.computeVertexNormals();

            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xc2a661,
                roughness: 0.9,
                metalness: 0.05
            });
            const floor = new THREE.Mesh(floorGeo, sandMat);
            floor.rotation.x = -Math.PI / 2;
            floor.position.y = FLOOR_Y;
            floor.receiveShadow = true;
            scene.add(floor);
        }

        // ==================== LIGHTING ====================
        function buildLighting() {
            // Ambient
            const ambient = new THREE.AmbientLight(0x404040, 0.4);
            scene.add(ambient);

            // Directional (sun)
            dirLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
            dirLight.position.set(15, 30, 10);
            dirLight.castShadow = true;
            dirLight.shadow.mapSize.width = 2048;
            dirLight.shadow.mapSize.height = 2048;
            dirLight.shadow.camera.near = 1;
            dirLight.shadow.camera.far = 80;
            dirLight.shadow.camera.left = -25;
            dirLight.shadow.camera.right = 25;
            dirLight.shadow.camera.top = 20;
            dirLight.shadow.camera.bottom = -20;
            scene.add(dirLight);

            // Underwater point lights
            pointLight1 = new THREE.PointLight(0x44aaff, 0.8, 40);
            pointLight1.position.set(-10, 5, 5);
            scene.add(pointLight1);

            pointLight2 = new THREE.PointLight(0x2266cc, 0.6, 35);
            pointLight2.position.set(10, -3, -5);
            scene.add(pointLight2);
        }

        // ==================== FISH CREATION ====================
        function createFish(colorIndex, scale) {
            const group = new THREE.Group();
            const colors = FISH_COLORS[colorIndex % FISH_COLORS.length];

            // Body (scaled sphere)
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.4, 0.85, 0.7);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: colors.body,
                roughness: 0.4,
                metalness: 0.3
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.18, 12, 10);
            const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.09, 10, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            leftEye.position.set(0.7, 0.15, 0.45);
            group.add(leftEye);

            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(0.78, 0.15, 0.5);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            rightEye.position.set(0.7, 0.15, -0.45);
            group.add(rightEye);

            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(0.78, 0.15, -0.5);
            group.add(rightPupil);

            // Tail (animated)
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
            tailGeo.rotateZ(Math.PI);
            const tailMat = new THREE.MeshStandardMaterial({
                color: colors.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.85
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.5, 0, 0);
            tail.name = 'tail';
            group.add(tail);

            // Dorsal fin (top)
            const dorsalGeo = new THREE.ConeGeometry(0.35, 0.7, 6);
            const dorsalMat = new THREE.MeshStandardMaterial({
                color: colors.fin,
                transparent: true,
                opacity: 0.75,
                roughness: 0.5
            });
            const dorsalFin = new THREE.Mesh(dorsalGeo, dorsalMat);
            dorsalFin.position.set(-0.1, 0.7, 0);
            dorsalFin.name = 'dorsalFin';
            group.add(dorsalFin);

            // Side fins
            const finGeo = new THREE.ConeGeometry(0.25, 0.5, 5);
            finGeo.rotateZ(Math.PI / 2);
            const finMat = new THREE.MeshStandardMaterial({
                color: colors.fin,
                transparent: true,
                opacity: 0.7,
                roughness: 0.5
            });

            const leftFin = new THREE.Mesh(finGeo, finMat);
            leftFin.position.set(0.2, -0.1, 0.5);
            leftFin.rotation.z = 0.3;
            leftFin.name = 'leftFin';
            group.add(leftFin);

            const rightFin = new THREE.Mesh(finGeo, finMat);
            rightFin.position.set(0.2, -0.1, -0.5);
            rightFin.rotation.z = -0.3;
            rightFin.name = 'rightFin';
            group.add(rightFin);

            // Apply random scale and position
            const s = scale || (0.6 + Math.random() * 0.6);
            group.scale.setScalar(s);
            group.position.set(
                (Math.random() - 0.5) * (AQUA_W - 6),
                (Math.random() - 0.5) * (AQUA_H - 6),
                (Math.random() - 0.5) * (AQUA_D - 6)
            );

            // Random initial orientation
            group.rotation.y = Math.random() * Math.PI * 2;

            scene.add(group);

            return {
                mesh: group,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                dorsalFin: dorsalFin,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 2,
                    (Math.random() - 0.5) * 0.5,
                    (Math.random() - 0.5) * 2
                ),
                speed: 1.5 + Math.random() * 2.0,
                tailSpeed: 4 + Math.random() * 3,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2.5 + Math.random() * 1.5,
                wanderTimer: Math.random() * 3,
                baseScale: s
            };
        }

        function createInitialFish(count) {
            for (let i = 0; i < count; i++) {
                const colorIdx = i % FISH_COLORS.length;
                const scale = 0.6 + Math.random() * 0.6;
                const fish = createFish(colorIdx, scale);
                fishArray.push(fish);
            }
            updateStats();
        }

        // ==================== BUBBLES ====================
        function createBubble(x, y, z) {
            const size = 0.1 + Math.random() * 0.25;
            const geo = new THREE.SphereGeometry(size, 10, 8);
            const mat = new THREE.MeshPhysicalMaterial({
                color: 0x88ddff,
                transparent: true,
                opacity: 0.4,
                roughness: 0.1,
                metalness: 0.1,
                transmission: 0.8
            });
            const bubble = new THREE.Mesh(geo, mat);
            bubble.position.set(x, y, z);
            scene.add(bubble);

            bubbles.push({
                mesh: bubble,
                vy: 0.5 + Math.random() * 1.0,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 2 + Math.random() * 2,
                wobbleAmp: 0.2 + Math.random() * 0.3
            });
        }

        function createInitialBubbles(count) {
            for (let i = 0; i < count; i++) {
                createBubble(
                    (Math.random() - 0.5) * (AQUA_W - 4),
                    FLOOR_Y + Math.random() * (AQUA_H - 2),
                    (Math.random() - 0.5) * (AQUA_D - 4)
                );
            }
        }

        // ==================== SEAWED ====================
        function createSeaweed(count) {
            for (let i = 0; i < count; i++) {
                const height = 2 + Math.random() * 4;
                const points = [];
                const segments = 6;
                for (let j = 0; j <= segments; j++) {
                    const t = j / segments;
                    const sway = Math.sin(t * 3) * 0.3;
                    points.push(new THREE.Vector3(
                        sway,
                        t * height,
                        Math.cos(t * 2) * 0.2
                    ));
                }
                const curve = new THREE.CatmullRomCurve3(points);
                const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);

                const hue = 0.25 + Math.random() * 0.15;
                const sat = 0.5 + Math.random() * 0.3;
                const lig = 0.25 + Math.random() * 0.15;
                const mat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color().setHSL(hue, sat, lig),
                    roughness: 0.7,
                    transparent: true,
                    opacity: 0.85
                });

                const weed = new THREE.Mesh(tubeGeo, mat);
                weed.position.set(
                    (Math.random() - 0.5) * (AQUA_W - 6),
                    FLOOR_Y,
                    (Math.random() - 0.5) * (AQUA_D - 6)
                );
                weed.castShadow = true;
                scene.add(weed);

                seaweeds.push({
                    mesh: weed,
                    phase: Math.random() * Math.PI * 2,
                    speed: 0.5 + Math.random() * 0.5,
                    ampX: 0.02 + Math.random() * 0.03,
                    ampZ: 0.02 + Math.random() * 0.03
                });
            }
        }

        // ==================== STONES ====================
        function createStones(count) {
            for (let i = 0; i < count; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const geo = new THREE.DodecahedronGeometry(size, 1);

                // Deform vertices randomly
                const pos = geo.attributes.position;
                for (let v = 0; v < pos.count; v++) {
                    const x = pos.getX(v);
                    const y = pos.getY(v);
                    const z = pos.getZ(v);
                    const deform = 0.85 + Math.random() * 0.3;
                    pos.setXYZ(v, x * deform, y * deform * 0.7, z * deform);
                }
                geo.computeVertexNormals();

                const hue = 0.05 + Math.random() * 0.1;
                const mat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color().setHSL(hue, 0.2, 0.3 + Math.random() * 0.2),
                    roughness: 0.85,
                    metalness: 0.05
                });

                const stone = new THREE.Mesh(geo, mat);
                stone.position.set(
                    (Math.random() - 0.5) * (AQUA_W - 8),
                    FLOOR_Y + size * 0.3,
                    (Math.random() - 0.5) * (AQUA_D - 8)
                );
                stone.rotation.set(
                    Math.random() * Math.PI,
                    Math.random() * Math.PI,
                    Math.random() * Math.PI
                );
                stone.castShadow = true;
                stone.receiveShadow = true;
                scene.add(stone);
                stones.push(stone);
            }
        }

        // ==================== FOOD SYSTEM ====================
        function spawnFood(x, y, z) {
            const geo = new THREE.SphereGeometry(0.25, 8, 6);
            const mat = new THREE.MeshStandardMaterial({
                color: 0x8bc34a,
                emissive: 0x4a7c1f,
                roughness: 0.5
            });
            const food = new THREE.Mesh(geo, mat);
            food.position.set(x, y, z);
            scene.add(food);

            foodItems.push({
                mesh: food,
                velocity: new THREE.Vector3(0, -1, 0),
                alive: true
            });
        }

        // ==================== INTERACTION ====================
        function onClickCanvas(event) {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            // Check intersection with a plane at z=0 or use the aquarium bounds
            const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
            const intersectPoint = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersectPoint);

            if (intersectPoint) {
                // Clamp to aquarium bounds
                intersectPoint.x = THREE.MathUtils.clamp(intersectPoint.x, -AQUA_W / 2 + 2, AQUA_W / 2 - 2);
                intersectPoint.y = THREE.MathUtils.clamp(intersectPoint.y, FLOOR_Y + 1, CEIL_Y - 1);
                intersectPoint.z = THREE.MathUtils.clamp(intersectPoint.z, -AQUA_D / 2 + 2, AQUA_D / 2 - 2);

                spawnFood(intersectPoint.x, intersectPoint.y, intersectPoint.z);
            }
        }

        function onMouseMove(event) {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        }

        // ==================== UI BUTTONS ====================
        function addFish() {
            const colorIdx = Math.floor(Math.random() * FISH_COLORS.length);
            const scale = 0.6 + Math.random() * 0.6;
            const fish = createFish(colorIdx, scale);
            fishArray.push(fish);
            updateStats();
        }

        function addBubbles() {
            for (let i = 0; i < 10; i++) {
                createBubble(
                    (Math.random() - 0.5) * (AQUA_W - 4),
                    FLOOR_Y + Math.random() * 3,
                    (Math.random() - 0.5) * (AQUA_D - 4)
                );
            }
        }

        function toggleLight() {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.2 : 0.15;
            pointLight1.intensity = lightOn ? 0.8 : 0.3;
            pointLight2.intensity = lightOn ? 0.6 : 0.2;
        }

        function updateStats() {
            document.getElementById('fish-count').textContent = fishArray.length;
        }

        // ==================== ANIMATION LOOP ====================
        function animate() {
            requestAnimationFrame(animate);
            const dt = Math.min(clock.getDelta(), 0.05);
            const elapsed = clock.elapsedTime;

            // Update fish
            updateFish(dt, elapsed);

            // Update bubbles
            updateBubbles(dt, elapsed);

            // Update food
            updateFood(dt);

            // Update seaweed
            updateSeaweed(dt, elapsed);

            // Animate point lights subtly
            pointLight1.position.x = -10 + Math.sin(elapsed * 0.3) * 3;
            pointLight1.position.y = 5 + Math.sin(elapsed * 0.5) * 2;
            pointLight2.position.x = 10 + Math.cos(elapsed * 0.4) * 2;
            pointLight2.position.y = -3 + Math.cos(elapsed * 0.6) * 1.5;

            // Controls
            controls.update();

            // Render
            renderer.render(scene, camera);

            // FPS
            frameCount++;
            const now = performance.now();
            if (now - lastFpsTime >= 1000) {
                const fps = Math.round(frameCount * 1000 / (now - lastFpsTime));
                document.getElementById('fps-counter').textContent = fps + ' FPS';
                frameCount = 0;
                lastFpsTime = now;
            }
        }

        // ==================== FISH UPDATE ====================
        function updateFish(dt, time) {
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;
                const vel = fish.velocity;

                // --- Tail animation ---
                const tailAngle = Math.sin(time * fish.tailSpeed + fish.phase) * 0.5;
                fish.tail.rotation.z = tailAngle;

                // Fin animation
                const finAngle = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase + 1) * 0.25;
                fish.leftFin.rotation.z = 0.3 + finAngle;
                fish.rightFin.rotation.z = -0.3 - finAngle;
                fish.dorsalFin.rotation.z = Math.sin(time * fish.tailSpeed * 0.5 + fish.phase) * 0.1;

                // --- Random wandering ---
                fish.wanderTimer -= dt;
                if (fish.wanderTimer <= 0) {
                    fish.wanderTimer = 2 + Math.random() * 4;
                    vel.x += (Math.random() - 0.5) * 1.5;
                    vel.y += (Math.random() - 0.5) * 0.5;
                    vel.z += (Math.random() - 0.5) * 1.5;
                }

                // --- Wall reflection ---
                const margin = 2;
                if (pos.x > AQUA_W / 2 - margin) vel.x -= 2 * dt;
                if (pos.x < -AQUA_W / 2 + margin) vel.x += 2 * dt;
                if (pos.y > CEIL_Y - margin) vel.y -= 1.5 * dt;
                if (pos.y < FLOOR_Y + margin) vel.y += 1.5 * dt;
                if (pos.z > AQUA_D / 2 - margin) vel.z -= 2 * dt;
                if (pos.z < -AQUA_D / 2 + margin) vel.z += 2 * dt;

                // --- Food chasing ---
                fish.targetFood = null;
                let closestDist = 15;
                for (let f = 0; f < foodItems.length; f++) {
                    if (!foodItems[f].alive) continue;
                    const dist = pos.distanceTo(foodItems[f].mesh.position);
                    if (dist < closestDist) {
                        closestDist = dist;
                        fish.targetFood = foodItems[f];
                    }
                }

                if (fish.targetFood) {
                    const dir = new THREE.Vector3().subVectors(fish.targetFood.mesh.position, pos).normalize();
                    vel.lerp(dir.multiplyScalar(fish.speed * 1.5), 3 * dt);

                    // Eat food
                    if (closestDist < 1.2) {
                        fish.targetFood.alive = false;
                        scene.remove(fish.targetFood.mesh);
                        foodItems.splice(foodItems.indexOf(fish.targetFood), 1);

                        // Grow 5%
                        const newScale = fish.baseScale * 1.05;
                        fish.baseScale = Math.min(newScale, 2.0);
                        fish.mesh.scale.setScalar(fish.baseScale);
                    }
                }

                // --- Collision avoidance ---
                for (let j = i + 1; j < fishArray.length; j++) {
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    const avoidDist = (fish.avoidanceRadius + other.avoidanceRadius) * 0.5;

                    if (dist < avoidDist && dist > 0.01) {
                        const pushDir = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        const strength = (avoidDist - dist) / avoidDist;
                        vel.add(pushDir.multiplyScalar(strength * 3 * dt));
                        other.velocity.sub(pushDir.clone().multiplyScalar(strength * 3 * dt));
                    }
                }

                // --- Speed limit & damping ---
                const speed = vel.length();
                if (speed > fish.speed) {
                    vel.normalize().multiplyScalar(fish.speed);
                }
                vel.multiplyScalar(1 - 0.3 * dt);

                // --- Update position ---
                pos.add(vel.clone().multiplyScalar(dt));

                // --- Face direction of movement ---
                if (speed > 0.1) {
                    const targetQuat = new THREE.Quaternion();
                    const lookAtMatrix = new THREE.Matrix4();
                    const forward = vel.clone().normalize();
                    lookAtMatrix.lookAt(new THREE.Vector3(), forward, new THREE.Vector3(0, 1, 0));
                    targetQuat.setFromRotationMatrix(lookAtMatrix);
                    fish.mesh.quaternion.slerp(targetQuat, 2.5 * dt);
                }

                // --- Subtle vertical bobbing ---
                fish.mesh.position.y += Math.sin(time * 1.5 + fish.phase) * 0.003;
            }
        }

        // ==================== BUBBLES UPDATE ====================
        function updateBubbles(dt, time) {
            for (let i = bubbles.length - 1; i >= 0; i--) {
                const b = bubbles[i];
                b.mesh.position.y += b.vy * dt;

                // Wobble
                b.mesh.position.x += Math.sin(time * b.wobbleSpeed + b.wobblePhase) * b.wobbleAmp * dt;
                b.mesh.position.z += Math.cos(time * b.wobbleSpeed * 0.7 + b.wobblePhase) * b.wobbleAmp * 0.5 * dt;

                // Reset when reaching surface
                if (b.mesh.position.y > CEIL_Y - 0.5) {
                    b.mesh.position.set(
                        (Math.random() - 0.5) * (AQUA_W - 4),
                        FLOOR_Y + 0.5,
                        (Math.random() - 0.5) * (AQUA_D - 4)
                    );
                    b.wobblePhase = Math.random() * Math.PI * 2;
                }
            }
        }

        // ==================== FOOD UPDATE ====================
        function updateFood(dt) {
            for (let i = foodItems.length - 1; i >= 0; i--) {
                const food = foodItems[i];
                if (!food.alive) continue;

                // Gravity
                food.velocity.y -= 3 * dt;
                food.mesh.position.add(food.velocity.clone().multiplyScalar(dt));

                // Remove when hitting floor
                if (food.mesh.position.y < FLOOR_Y + 0.3) {
                    scene.remove(food.mesh);
                    foodItems.splice(i, 1);
                }
            }
        }

        // ==================== SEAWED UPDATE ====================
        function updateSeaweed(dt, time) {
            for (let i = 0; i < seaweeds.length; i++) {
                const s = seaweeds[i];
                s.mesh.rotation.x = Math.sin(time * s.speed + s.phase) * s.ampX;
                s.mesh.rotation.z = Math.cos(time * s.speed * 0.8 + s.phase) * s.ampZ;
            }
        }

        // ==================== RESIZE ====================
        function onResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // ==================== START ====================
        init();
    </script>
</body>
</html>
```

## Что реализовано

| Компонент | Детали |
|---|---|
| **🐠 15 рыбок** | Тело (масштабированная сфера), глаза с зрачками, анимируемый хвост, спинной и боковые плавники, 8 цветовых схем, случайный масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, отражение от стен, случайное блуждание, преследование корма (радиус 15), рост на 5% при поедании |
| **🌊 Окружение** | Стеклянный контейнер (transmission 0.95, wireframe), песчаное дно с процедурными неровностями, 8 деформированных камней, 12 водорослей (TubeGeometry + CatmullRomCurve3) |
| **💭 30 пузырей** | MeshPhysicalMaterial, движение вверх + синусоидальное покачивание, сброс при достижении поверхности |
| **🍽️ Кормление** | Клик → Raycaster → spawn корма, гравитация, обнаружение рыбками, съедание → рост |
| **💡 Освещение** | Ambient + Directional (2048 shadow, PCFSoft) + 2 PointLight (анимированные), кнопка вкл/выкл |
| **🎮 OrbitControls** | Дампинг, зум 10–60, maxPolarAngle π/1.8 |
| **🖥️ UI** | Glass-morphism панели, градиентные кнопки с hover, счётчик рыбок, FPS counter |
| **🎨 Эффекты** | FogExp2, градиентный фон, backdrop-filter blur, glow-тени |

Просто сохраните как `.html` и откройте в браузере — всё работает без сборки.