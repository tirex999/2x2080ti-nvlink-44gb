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
            background: linear-gradient(180deg, #0a1628 0%, #1a3a5c 100%);
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
            background: rgba(10, 30, 60, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            z-index: 100;
        }

        .info-panel {
            top: 20px;
            left: 20px;
            width: 280px;
        }

        .info-panel h1 {
            font-size: 1.4em;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #00d4ff, #7b68ee, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        .info-panel p {
            font-size: 0.82em;
            line-height: 1.6;
            opacity: 0.85;
            margin-bottom: 8px;
        }

        .stats-panel {
            top: 20px;
            right: 20px;
            min-width: 160px;
        }

        .stats-panel h3 {
            font-size: 1em;
            margin-bottom: 10px;
            color: #7bceff;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 0.85em;
        }

        .stat-value {
            color: #00d4ff;
            font-weight: 600;
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
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            box-shadow: 0 4px 15px rgba(238, 90, 36, 0.4);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(238, 90, 36, 0.6);
        }

        .btn-bubble {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: white;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
        }

        .btn-bubble:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.6);
        }

        .btn-light {
            background: linear-gradient(135deg, #f9ca24, #f0932b);
            color: white;
            box-shadow: 0 4px 15px rgba(249, 202, 36, 0.4);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(249, 202, 36, 0.6);
        }

        .btn:active {
            transform: translateY(0);
        }

        .hint {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(8px);
            padding: 10px 24px;
            border-radius: 30px;
            color: rgba(200, 230, 255, 0.8);
            font-size: 0.8em;
            border: 1px solid rgba(100, 180, 255, 0.15);
            z-index: 100;
            pointer-events: none;
        }

        @media (max-width: 768px) {
            .info-panel {
                width: 220px;
                padding: 14px;
            }
            .info-panel h1 {
                font-size: 1.1em;
            }
            .stats-panel {
                top: auto;
                bottom: 70px;
                right: 10px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>🖱️ Левый клик + движение — вращение</p>
        <p>🖱️ Правый клик + движение — панорама</p>
        <p>🖱️ Колесо мыши — масштаб</p>
        <p>🍽️ Клик по аквариуму — кормление</p>
        <div class="btn-group">
            <button class="btn btn-fish" onclick="addFish()">🐟 Добавить рыбку</button>
            <button class="btn btn-bubble" onclick="addBubbles()">🫧 Больше пузырей</button>
            <button class="btn btn-light" onclick="toggleLight()">💡 Свет</button>
        </div>
    </div>

    <div class="panel stats-panel">
        <h3>📊 Статистика</h3>
        <div class="stat-item">
            <span>Рыбки:</span>
            <span class="stat-value" id="fish-count">15</span>
        </div>
        <div class="stat-item">
            <span>Пузыри:</span>
            <span class="stat-value" id="bubble-count">30</span>
        </div>
        <div class="stat-item">
            <span>Корм:</span>
            <span class="stat-value" id="food-count">0</span>
        </div>
        <div class="stat-item">
            <span>FPS:</span>
            <span class="stat-value" id="fps-counter">60</span>
        </div>
    </div>

    <div class="hint">💡 Кликните по аквариуму, чтобы покормить рыбок</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(25, 18, 30);

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
        controls.target.set(0, 5, 0);

        // === AQUARIUM DIMENSIONS ===
        const AQUARIUM = { width: 36, height: 24, depth: 20 };
        const HALF = { x: AQUARIUM.width / 2, y: AQUARIUM.height / 2, z: AQUARIUM.depth / 2 };

        // === LIGHTING ===
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(15, 30, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 1;
        dirLight.shadow.camera.far = 80;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 25;
        dirLight.shadow.camera.bottom = -25;
        dirLight.shadow.bias = -0.001;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x0088ff, 0.6, 40);
        pointLight1.position.set(-10, 15, 5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x0044aa, 0.4, 35);
        pointLight2.position.set(10, 8, -5);
        scene.add(pointLight2);

        let lightOn = true;

        // === AQUARIUM GLASS ===
        const glassGeometry = new THREE.BoxGeometry(AQUARIUM.width, AQUARIUM.height, AQUARIUM.depth);
        const glassMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x88ccff,
            transparent: true,
            opacity: 0.08,
            transmission: 0.95,
            roughness: 0.05,
            metalness: 0,
            side: THREE.BackSide
        });
        const glassBox = new THREE.Mesh(glassGeometry, glassMaterial);
        glassBox.position.y = HALF.y;
        scene.add(glassBox);

        // Wireframe edges
        const edgesGeometry = new THREE.EdgesGeometry(glassGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x4488cc, transparent: true, opacity: 0.5 });
        const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        edges.position.y = HALF.y;
        scene.add(edges);

        // === SANDY BOTTOM ===
        const sandGeometry = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth, 40, 40);
        const sandPositions = sandGeometry.attributes.position;
        for (let i = 0; i < sandPositions.count; i++) {
            const x = sandPositions.getX(i);
            const y = sandPositions.getY(i);
            const noise = Math.sin(x * 0.5) * Math.cos(y * 0.3) * 0.3 +
                         Math.sin(x * 1.2 + y * 0.8) * 0.15;
            sandPositions.setZ(i, noise);
        }
        sandGeometry.computeVertexNormals();
        const sandMaterial = new THREE.MeshStandardMaterial({
            color: 0xd4a574,
            roughness: 0.9,
            metalness: 0.0
        });
        const sand = new THREE.Mesh(sandGeometry, sandMaterial);
        sand.rotation.x = -Math.PI / 2;
        sand.position.y = 0.1;
        sand.receiveShadow = true;
        scene.add(sand);

        // === ROCKS ===
        for (let i = 0; i < 8; i++) {
            const rockGeo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.2, 1);
            const rockPositions = rockGeo.attributes.position;
            for (let j = 0; j < rockPositions.count; j++) {
                rockPositions.setX(j, rockPositions.getX(j) + (Math.random() - 0.5) * 0.3);
                rockPositions.setY(j, rockPositions.getY(j) + (Math.random() - 0.5) * 0.3);
                rockPositions.setZ(j, rockPositions.getZ(j) + (Math.random() - 0.5) * 0.3);
            }
            rockGeo.computeVertexNormals();
            const rockMat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.2, 0.3 + Math.random() * 0.2),
                roughness: 0.85,
                metalness: 0.1
            });
            const rock = new THREE.Mesh(rockGeo, rockMat);
            rock.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 6),
                0.5 + Math.random() * 0.5,
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.castShadow = true;
            rock.receiveShadow = true;
            scene.add(rock);
        }

        // === SEAWEED ===
        const seaweeds = [];
        for (let i = 0; i < 12; i++) {
            const height = 3 + Math.random() * 5;
            const points = [];
            const segments = 8;
            for (let j = 0; j <= segments; j++) {
                const t = j / segments;
                points.push(new THREE.Vector3(
                    Math.sin(t * 2) * 0.3,
                    t * height,
                    Math.cos(t * 1.5) * 0.2
                ));
            }
            const curve = new THREE.CatmullRomCurve3(points);
            const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);
            const hue = 0.25 + Math.random() * 0.15;
            const tubeMat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(hue, 0.7, 0.35),
                roughness: 0.7,
                metalness: 0.0
            });
            const seaweed = new THREE.Mesh(tubeGeo, tubeMat);
            seaweed.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                0,
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

        // === FISH COLOR SCHEMES ===
        const colorSchemes = [
            { body: 0xff6b35, fin: 0xff9f43, eye: 0xffffff },   // оранжевая
            { body: 0x2e86de, fin: 0x54a0ff, eye: 0xffffff },   // синяя
            { body: 0xf6e58d, fin: 0xff6348, eye: 0xffffff },   // желто-красная
            { body: 0x8854d0, fin: 0xa29bfe, eye: 0xffffff },   // фиолетовая
            { body: 0xe74c3c, fin: 0xff7979, eye: 0xffffff },   // красная
            { body: 0x27ae60, fin: 0x6ab04c, eye: 0xffffff },   // зеленая
            { body: 0xfd79a8, fin: 0xf8a5c2, eye: 0xffffff },   // розовая
            { body: 0xf39c12, fin: 0xffd32a, eye: 0xffffff },   // золотая
        ];

        // === FISH CREATION ===
        const fishArray = [];

        function createFish(colorScheme, scale) {
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.6, 0.7, 0.5);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: colorScheme.body,
                roughness: 0.3,
                metalness: 0.2
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.18, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: colorScheme.eye, roughness: 0.1 });
            const pupilGeo = new THREE.SphereGeometry(0.09, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
            leftEye.position.set(1.1, 0.15, 0.25);
            group.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(1.25, 0.15, 0.28);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
            rightEye.position.set(1.1, 0.15, -0.25);
            group.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(1.25, 0.15, -0.28);
            group.add(rightPupil);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 4);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                metalness: 0.1,
                transparent: true,
                opacity: 0.85
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.6, 0, 0);
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 3);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.8
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0.2, 0.55, 0);
            group.add(topFin);

            // Side fins
            const finGeo = new THREE.ConeGeometry(0.2, 0.6, 3);
            const finMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.75
            });

            const leftFin = new THREE.Mesh(finGeo, finMat);
            leftFin.position.set(0.3, -0.1, 0.4);
            leftFin.rotation.x = Math.PI / 4;
            group.add(leftFin);

            const rightFin = new THREE.Mesh(finGeo, finMat);
            rightFin.position.set(0.3, -0.1, -0.4);
            rightFin.rotation.x = -Math.PI / 4;
            group.add(rightFin);

            group.scale.setScalar(scale);

            return { group, tail, leftFin, rightFin };
        }

        function spawnFish() {
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;
            const { group, tail, leftFin, rightFin } = createFish(scheme, scale);

            group.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 8),
                3 + Math.random() * (AQUARIUM.height - 8),
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );

            scene.add(group);

            const angle = Math.random() * Math.PI * 2;
            const speed = 1.5 + Math.random() * 2.5;

            fishArray.push({
                mesh: group,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                velocity: new THREE.Vector3(
                    Math.cos(angle) * speed,
                    (Math.random() - 0.5) * 0.5,
                    Math.sin(angle) * speed
                ),
                speed: speed,
                tailSpeed: 3 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 3 + Math.random() * 2,
                scale: scale,
                wanderTimer: Math.random() * 3,
                wanderInterval: 2 + Math.random() * 3
            });

            updateStats();
        }

        // Spawn initial fish
        for (let i = 0; i < 15; i++) {
            spawnFish();
        }

        // === BUBBLES ===
        const bubbles = [];

        function createBubble() {
            const size = 0.1 + Math.random() * 0.25;
            const geo = new THREE.SphereGeometry(size, 12, 12);
            const mat = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3,
                transmission: 0.9,
                roughness: 0.0,
                metalness: 0.0,
                clearcoat: 1.0
            });
            const bubble = new THREE.Mesh(geo, mat);
            bubble.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                Math.random() * AQUARIUM.height,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            scene.add(bubble);
            bubbles.push({
                mesh: bubble,
                speed: 0.5 + Math.random() * 1.5,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 1 + Math.random() * 2,
                wobbleAmp: 0.3 + Math.random() * 0.5
            });
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // === FOOD SYSTEM ===
        const foods = [];

        function createFood(point) {
            const geo = new THREE.SphereGeometry(0.2, 8, 8);
            const mat = new THREE.MeshStandardMaterial({
                color: 0x8B4513,
                roughness: 0.8
            });
            const food = new THREE.Mesh(geo, mat);
            food.position.copy(point);
            food.position.y = Math.min(food.position.y + 2, AQUARIUM.height - 1);
            scene.add(food);
            foods.push({
                mesh: food,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 0.5,
                    0,
                    (Math.random() - 0.5) * 0.5
                ),
                gravity: -2.0
            });
            updateStats();
        }

        // === RAYCASTER FOR CLICKS ===
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let isMouseDown = false;
        let mouseDownTime = 0;

        renderer.domElement.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseDownTime = Date.now();
        });

        renderer.domElement.addEventListener('mouseup', (e) => {
            if (Date.now() - mouseDownTime < 200 && e.button === 0) {
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
                raycaster.setFromCamera(mouse, camera);

                // Check intersection with aquarium volume
                const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
                const intersectPoint = new THREE.Vector3();
                raycaster.ray.intersectPlane(plane, intersectPoint);

                if (intersectPoint) {
                    // Clamp to aquarium bounds
                    intersectPoint.x = Math.max(-HALF.x + 2, Math.min(HALF.x - 2, intersectPoint.x));
                    intersectPoint.y = Math.max(2, Math.min(AQUARIUM.height - 2, intersectPoint.y));
                    intersectPoint.z = Math.max(-HALF.z + 2, Math.min(HALF.z - 2, intersectPoint.z));
                    createFood(intersectPoint);
                }
            }
            isMouseDown = false;
        });

        // === UI FUNCTIONS ===
        function addFish() {
            spawnFish();
        }

        function addBubbles() {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
            updateStats();
        }

        function toggleLight() {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 0.8 : 0.1;
            pointLight1.intensity = lightOn ? 0.6 : 0.3;
            pointLight2.intensity = lightOn ? 0.4 : 0.2;
        }

        function updateStats() {
            document.getElementById('fish-count').textContent = fishArray.length;
            document.getElementById('bubble-count').textContent = bubbles.length;
            document.getElementById('food-count').textContent = foods.length;
        }

        // === FPS COUNTER ===
        let frameCount = 0;
        let lastFpsTime = performance.now();

        function updateFPS() {
            frameCount++;
            const now = performance.now();
            if (now - lastFpsTime >= 1000) {
                document.getElementById('fps-counter').textContent = frameCount;
                frameCount = 0;
                lastFpsTime = now;
            }
        }

        // === ANIMATION LOOP ===
        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const delta = Math.min(clock.getDelta(), 0.05);
            const time = clock.getElapsedTime();

            // Update fish
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Tail animation
                fish.tail.rotation.y = Math.sin(time * fish.tailSpeed + fish.phase) * 0.6;

                // Fin animation
                fish.leftFin.rotation.z = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.3;
                fish.rightFin.rotation.z = -Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.3;

                // Food seeking
                let nearestFood = null;
                let nearestDist = 15;
                for (let f = 0; f < foods.length; f++) {
                    const dist = pos.distanceTo(foods[f].mesh.position);
                    if (dist < nearestDist) {
                        nearestDist = dist;
                        nearestFood = foods[f];
                    }
                }

                if (nearestFood) {
                    fish.targetFood = nearestFood;
                    const dir = new THREE.Vector3().subVectors(nearestFood.mesh.position, pos).normalize();
                    fish.velocity.lerp(dir.multiplyScalar(fish.speed * 1.5), 0.05);

                    // Eat food
                    if (nearestDist < 1.2) {
                        scene.remove(nearestFood.mesh);
                        foods.splice(foods.indexOf(nearestFood), 1);
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                        fish.targetFood = null;
                        updateStats();
                    }
                } else {
                    fish.targetFood = null;

                    // Wander
                    fish.wanderTimer -= delta;
                    if (fish.wanderTimer <= 0) {
                        fish.wanderTimer = fish.wanderInterval;
                        const angle = Math.random() * Math.PI * 2;
                        const vertAngle = (Math.random() - 0.5) * 0.5;
                        fish.velocity.x += Math.cos(angle) * 0.5;
                        fish.velocity.y += vertAngle * 0.3;
                        fish.velocity.z += Math.sin(angle) * 0.5;
                    }
                }

                // Avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0) {
                        const push = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        push.multiplyScalar(0.3 / dist);
                        fish.velocity.add(push);
                    }
                }

                // Wall avoidance
                const margin = 3;
                if (pos.x > HALF.x - margin) fish.velocity.x -= 0.1;
                if (pos.x < -HALF.x + margin) fish.velocity.x += 0.1;
                if (pos.y > AQUARIUM.height - margin) fish.velocity.y -= 0.1;
                if (pos.y < margin) fish.velocity.y += 0.1;
                if (pos.z > HALF.z - margin) fish.velocity.z -= 0.1;
                if (pos.z < -HALF.z + margin) fish.velocity.z += 0.1;

                // Speed limit
                const currentSpeed = fish.velocity.length();
                if (currentSpeed > fish.speed * 2) {
                    fish.velocity.normalize().multiplyScalar(fish.speed * 2);
                }

                // Damping
                fish.velocity.multiplyScalar(0.995);

                // Move
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Hard clamp
                pos.x = Math.max(-HALF.x + 1, Math.min(HALF.x - 1, pos.x));
                pos.y = Math.max(1, Math.min(AQUARIUM.height - 1, pos.y));
                pos.z = Math.max(-HALF.z + 1, Math.min(HALF.z - 1, pos.z));

                // Rotate to face direction
                if (fish.velocity.lengthSq() > 0.01) {
                    const targetAngle = Math.atan2(fish.velocity.z, fish.velocity.x);
                    const currentAngle = fish.mesh.rotation.y;
                    let diff = targetAngle - currentAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    fish.mesh.rotation.y -= diff * 0.05;

                    // Slight tilt based on vertical velocity
                    fish.mesh.rotation.z = -fish.velocity.y * 0.1;
                }
            }

            // Update bubbles
            for (let i = 0; i < bubbles.length; i++) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * delta;
                b.mesh.position.x += Math.sin(time * b.wobbleSpeed + b.wobblePhase) * b.wobbleAmp * delta;
                b.mesh.position.z += Math.cos(time * b.wobbleSpeed * 0.7 + b.wobblePhase) * b.wobbleAmp * delta;

                if (b.mesh.position.y > AQUARIUM.height - 1) {
                    b.mesh.position.y = 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                    b.mesh.position.z = (Math.random() - 0.5) * (AQUARIUM.depth - 4);
                }
            }

            // Update food
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                food.velocity.y += food.gravity * delta;
                food.mesh.position.add(food.velocity.clone().multiplyScalar(delta));

                if (food.mesh.position.y < 0.5) {
                    scene.remove(food.mesh);
                    foods.splice(i, 1);
                    updateStats();
                }
            }

            // Update seaweed
            for (let i = 0; i < seaweeds.length; i++) {
                const sw = seaweeds[i];
                sw.mesh.rotation.x = Math.sin(time * sw.speed + sw.phase) * sw.amplitude;
                sw.mesh.rotation.z = Math.cos(time * sw.speed * 0.8 + sw.phase) * sw.amplitude;
            }

            // Animate point lights subtly
            pointLight1.position.x = -10 + Math.sin(time * 0.3) * 3;
            pointLight2.position.z = -5 + Math.cos(time * 0.4) * 3;

            controls.update();
            renderer.render(scene, camera);
            updateFPS();
        }

        animate();

        // === RESIZE ===
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```

Этот файл содержит полноценный интерактивный 3D аквариум со всеми запрошенными функциями:

**🐠 Рыбки:** 15 тропических рыбок с детализированной анатомией (тело, глаза с зрачками, хвост, плавники), 8 цветовых схем, случайный размер.

**🧠 ИИ:** Избегание столкновений, отражение от стен, случайное блуждание, преследование корма, рост при поедании.

**🌊 Окружение:** Стеклянный контейнер с прозрачностью, песчаное дно с неровностями, 8 камней, 12 кустов водорослей с анимацией покачивания.

**💭 Пузыри:** 30 пузырей с эффектом стекла, движение вверх с покачиванием.

**🍽️ Кормление:** Клик создаёт корм с гравитацией, рыбки обнаруживают и преследуют его.

**💡 Освещение:** Ambient + Directional (с тенями 2048×2048) + 2 PointLight, переключаемый свет.

**🎮 Управление:** OrbitControls с демпфированием, зумом и ограничениями.