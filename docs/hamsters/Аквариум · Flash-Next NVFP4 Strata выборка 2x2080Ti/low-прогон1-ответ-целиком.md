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

        canvas {
            display: block;
        }

        .panel {
            position: fixed;
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 180, 255, 0.3);
            border-radius: 12px;
            padding: 16px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        .info-panel h1 {
            font-size: 20px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #64b5f6, #42a5f5, #1e88e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
        }

        .info-panel p {
            font-size: 12px;
            line-height: 1.6;
            opacity: 0.85;
            margin-bottom: 12px;
        }

        .stats-panel {
            top: 20px;
            right: 20px;
            min-width: 160px;
        }

        .stats-panel .stat {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 13px;
        }

        .stats-panel .stat-value {
            color: #64b5f6;
            font-weight: bold;
        }

        .btn {
            display: block;
            width: 100%;
            padding: 10px 16px;
            margin-top: 8px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            color: white;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6f00, #ff8f00);
            box-shadow: 0 4px 15px rgba(255, 111, 0, 0.3);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 111, 0, 0.5);
        }

        .btn-bubble {
            background: linear-gradient(135deg, #0288d1, #039be5);
            box-shadow: 0 4px 15px rgba(2, 136, 209, 0.3);
        }

        .btn-bubble:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(2, 136, 209, 0.5);
        }

        .btn-light {
            background: linear-gradient(135deg, #f9a825, #fbc02d);
            box-shadow: 0 4px 15px rgba(249, 168, 37, 0.3);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(249, 168, 37, 0.5);
        }

        .btn:active {
            transform: translateY(0px);
        }

        .click-hint {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 180, 255, 0.3);
            border-radius: 20px;
            padding: 10px 24px;
            color: #90caf9;
            font-size: 13px;
            pointer-events: none;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        @media (max-width: 768px) {
            .info-panel {
                max-width: 200px;
                padding: 12px;
            }
            .info-panel h1 {
                font-size: 16px;
            }
            .info-panel p {
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
    <div class="panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>
            🖱️ ЛКМ + движение — вращение<br>
            🖱️ ПКМ + движение — панорама<br>
            🖱️ Колесо — масштаб<br>
            🖱️ Клик по аквариуму — корм
        </p>
        <button class="btn btn-fish" onclick="addFish()">🐟 Добавить рыбку</button>
        <button class="btn btn-bubble" onclick="addBubbles()">🫧 Больше пузырей</button>
        <button class="btn btn-light" onclick="toggleLight()">💡 Свет</button>
    </div>

    <div class="panel stats-panel">
        <div class="stat">
            <span>🐟 Рыбки:</span>
            <span class="stat-value" id="fishCount">0</span>
        </div>
        <div class="stat">
            <span>🍽️ Корм:</span>
            <span class="stat-value" id="foodCount">0</span>
        </div>
        <div class="stat">
            <span>🫧 Пузыри:</span>
            <span class="stat-value" id="bubbleCount">0</span>
        </div>
        <div class="stat">
            <span>⚡ FPS:</span>
            <span class="stat-value" id="fpsCounter">60</span>
        </div>
    </div>

    <div class="click-hint">💡 Кликните по аквариуму, чтобы покормить рыбок</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a1628);
        scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(30, 18, 35);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
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
        controls.target.set(0, 0, 0);

        // === CONSTANTS ===
        const AQUARIUM = { width: 36, height: 24, depth: 20 };
        const HALF = { x: AQUARIUM.width / 2, y: AQUARIUM.height / 2, z: AQUARIUM.depth / 2 };

        // === COLOR SCHEMES ===
        const colorSchemes = [
            { body: 0xff6600, fin: 0xff9933, eye: 0x000000 },   // оранжевая
            { body: 0x2266cc, fin: 0x4488ee, eye: 0x000000 },   // синяя
            { body: 0xffcc00, fin: 0xff4400, eye: 0x000000 },   // желто-красная
            { body: 0x9933cc, fin: 0xbb66ee, eye: 0x000000 },   // фиолетовая
            { body: 0xcc2222, fin: 0xff4444, eye: 0x000000 },   // красная
            { body: 0x22aa44, fin: 0x44cc66, eye: 0x000000 },   // зеленая
            { body: 0xff66aa, fin: 0xff99cc, eye: 0x000000 },   // розовая
            { body: 0xffaa00, fin: 0xffdd44, eye: 0x000000 },   // золотая
        ];

        // === LIGHTING ===
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 30, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 80;
        directionalLight.shadow.camera.left = -25;
        directionalLight.shadow.camera.right = 25;
        directionalLight.shadow.camera.top = 25;
        directionalLight.shadow.camera.bottom = -25;
        scene.add(directionalLight);

        const pointLight1 = new THREE.PointLight(0x4488ff, 0.6, 40);
        pointLight1.position.set(-10, 8, -5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2266cc, 0.4, 35);
        pointLight2.position.set(10, -5, 8);
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
        scene.add(glassBox);

        // Wireframe edges
        const edgesGeometry = new THREE.EdgesGeometry(glassGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x4488aa, transparent: true, opacity: 0.6 });
        const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        scene.add(edges);

        // === SANDY BOTTOM ===
        const sandGeometry = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth, 40, 40);
        const sandPositions = sandGeometry.attributes.position;
        for (let i = 0; i < sandPositions.count; i++) {
            const x = sandPositions.getX(i);
            const y = sandPositions.getY(i);
            sandPositions.setZ(i, Math.sin(x * 0.5) * 0.2 + Math.cos(y * 0.7) * 0.15 + Math.random() * 0.1);
        }
        sandGeometry.computeVertexNormals();
        const sandMaterial = new THREE.MeshStandardMaterial({
            color: 0xd4a855,
            roughness: 0.9,
            metalness: 0.0
        });
        const sand = new THREE.Mesh(sandGeometry, sandMaterial);
        sand.rotation.x = -Math.PI / 2;
        sand.position.y = -HALF.y + 0.1;
        sand.receiveShadow = true;
        scene.add(sand);

        // === ROCKS ===
        for (let i = 0; i < 8; i++) {
            const rockGeometry = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.2, 1);
            const rockPositions = rockGeometry.attributes.position;
            for (let j = 0; j < rockPositions.count; j++) {
                rockPositions.setX(j, rockPositions.getX(j) * (0.7 + Math.random() * 0.6));
                rockPositions.setY(j, rockPositions.getY(j) * (0.5 + Math.random() * 0.5));
                rockPositions.setZ(j, rockPositions.getZ(j) * (0.7 + Math.random() * 0.6));
            }
            rockGeometry.computeVertexNormals();
            const rockMaterial = new THREE.MeshStandardMaterial({
                color: new THREE.Color(0.3 + Math.random() * 0.2, 0.25 + Math.random() * 0.15, 0.2 + Math.random() * 0.1),
                roughness: 0.95,
                metalness: 0.05
            });
            const rock = new THREE.Mesh(rockGeometry, rockMaterial);
            rock.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                -HALF.y + 0.5 + Math.random() * 0.5,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.castShadow = true;
            rock.receiveShadow = true;
            scene.add(rock);
        }

        // === SEAWEED ===
        const seaweeds = [];
        for (let i = 0; i < 12; i++) {
            const height = 2 + Math.random() * 4;
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
            const tubeGeometry = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);
            const seaweedMaterial = new THREE.MeshStandardMaterial({
                color: new THREE.Color(0.1 + Math.random() * 0.2, 0.4 + Math.random() * 0.3, 0.1 + Math.random() * 0.15),
                roughness: 0.8,
                metalness: 0.0,
                side: THREE.DoubleSide
            });
            const seaweed = new THREE.Mesh(tubeGeometry, seaweedMaterial);
            seaweed.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 6),
                -HALF.y + 0.1,
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            seaweed.castShadow = true;
            seaweed.userData = { phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 };
            scene.add(seaweed);
            seaweeds.push(seaweed);
        }

        // === FISH CREATION ===
        const fishArray = [];

        function createFish() {
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;

            const fishGroup = new THREE.Group();

            // Body
            const bodyGeometry = new THREE.SphereGeometry(1, 16, 12);
            bodyGeometry.scale(1.4, 0.7, 0.5);
            const bodyMaterial = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.3,
                metalness: 0.2
            });
            const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
            body.castShadow = true;
            fishGroup.add(body);

            // Tail
            const tailGeometry = new THREE.ConeGeometry(0.5, 1.2, 4);
            const tailMaterial = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                metalness: 0.1,
                side: THREE.DoubleSide
            });
            const tail = new THREE.Mesh(tailGeometry, tailMaterial);
            tail.position.x = -1.6;
            tail.rotation.z = Math.PI / 2;
            tail.scale.set(0.3, 1, 0.6);
            fishGroup.add(tail);

            // Dorsal fin (top)
            const dorsalGeometry = new THREE.ConeGeometry(0.3, 0.8, 4);
            const dorsalMaterial = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                side: THREE.DoubleSide
            });
            const dorsal = new THREE.Mesh(dorsalGeometry, dorsalMaterial);
            dorsal.position.set(0.2, 0.6, 0);
            dorsal.scale.set(0.3, 1, 0.5);
            fishGroup.add(dorsal);

            // Left fin
            const finGeometry = new THREE.ConeGeometry(0.25, 0.6, 4);
            const finMaterial = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                side: THREE.DoubleSide
            });
            const leftFin = new THREE.Mesh(finGeometry, finMaterial);
            leftFin.position.set(0.2, -0.1, 0.5);
            leftFin.rotation.x = -0.5;
            leftFin.scale.set(0.3, 1, 0.4);
            fishGroup.add(leftFin);

            // Right fin
            const rightFin = new THREE.Mesh(finGeometry.clone(), finMaterial.clone());
            rightFin.position.set(0.2, -0.1, -0.5);
            rightFin.rotation.x = 0.5;
            rightFin.scale.set(0.3, 1, 0.4);
            fishGroup.add(rightFin);

            // Eyes
            const eyeGeometry = new THREE.SphereGeometry(0.18, 8, 8);
            const eyeWhiteMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeometry = new THREE.SphereGeometry(0.09, 8, 8);
            const pupilMaterial = new THREE.MeshStandardMaterial({ color: scheme.eye, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeometry, eyeWhiteMaterial);
            leftEye.position.set(0.9, 0.15, 0.35);
            fishGroup.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
            leftPupil.position.set(1.05, 0.15, 0.4);
            fishGroup.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeometry.clone(), eyeWhiteMaterial.clone());
            rightEye.position.set(0.9, 0.15, -0.35);
            fishGroup.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeometry.clone(), pupilMaterial.clone());
            rightPupil.position.set(1.05, 0.15, -0.4);
            fishGroup.add(rightPupil);

            fishGroup.scale.setScalar(scale);
            fishGroup.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 6),
                (Math.random() - 0.5) * (AQUARIUM.height - 6),
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );

            scene.add(fishGroup);

            const fish = {
                mesh: fishGroup,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 2,
                    (Math.random() - 0.5) * 0.5,
                    (Math.random() - 0.5) * 2
                ),
                speed: 2 + Math.random() * 3,
                tailSpeed: 3 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 3 + Math.random() * 2,
                scale: scale
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

        function createBubble() {
            const size = 0.1 + Math.random() * 0.25;
            const bubbleGeometry = new THREE.SphereGeometry(size, 12, 12);
            const bubbleMaterial = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3,
                transmission: 0.9,
                roughness: 0.0,
                metalness: 0.0,
                clearcoat: 1.0
            });
            const bubble = new THREE.Mesh(bubbleGeometry, bubbleMaterial);
            bubble.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                -HALF.y + Math.random() * AQUARIUM.height,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            bubble.userData = {
                speed: 1 + Math.random() * 2,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 1 + Math.random() * 2,
                wobbleAmount: 0.3 + Math.random() * 0.5
            };
            scene.add(bubble);
            bubbles.push(bubble);
            return bubble;
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // === FOOD SYSTEM ===
        const foods = [];
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function createFood(point) {
            const foodGeometry = new THREE.SphereGeometry(0.25, 8, 8);
            const foodMaterial = new THREE.MeshStandardMaterial({
                color: 0x8B4513,
                roughness: 0.8
            });
            const food = new THREE.Mesh(foodGeometry, foodMaterial);
            food.position.copy(point);
            food.position.y = HALF.y - 1;
            food.userData = {
                velocityY: 0,
                gravity: -3,
                eaten: false
            };
            scene.add(food);
            foods.push(food);
        }

        // === CLICK HANDLER ===
        let isMouseDown = false;
        let mouseDownTime = 0;
        let mouseDownPos = { x: 0, y: 0 };

        renderer.domElement.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseDownTime = Date.now();
            mouseDownPos = { x: e.clientX, y: e.clientY };
        });

        renderer.domElement.addEventListener('mouseup', (e) => {
            const timeDiff = Date.now() - mouseDownTime;
            const distDiff = Math.sqrt(
                Math.pow(e.clientX - mouseDownPos.x, 2) +
                Math.pow(e.clientY - mouseDownPos.y, 2)
            );

            if (timeDiff < 300 && distDiff < 5) {
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObject(glassBox);

                if (intersects.length > 0) {
                    const point = intersects[0].point.clone();
                    point.x = Math.max(-HALF.x + 2, Math.min(HALF.x - 2, point.x));
                    point.z = Math.max(-HALF.z + 2, Math.min(HALF.z - 2, point.z));
                    createFood(point);
                } else {
                    // Create food at center top if no intersection
                    const dir = new THREE.Vector3();
                    raycaster.ray.direction.normalize();
                    const point = raycaster.ray.origin.clone().add(
                        raycaster.ray.direction.multiplyScalar(30)
                    );
                    point.x = Math.max(-HALF.x + 2, Math.min(HALF.x - 2, point.x));
                    point.z = Math.max(-HALF.z + 2, Math.min(HALF.z - 2, point.z));
                    createFood(point);
                }
            }
            isMouseDown = false;
        });

        // === UI FUNCTIONS ===
        function addFish() {
            createFish();
            updateStats();
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
            document.getElementById('fishCount').textContent = fishArray.length;
            document.getElementById('foodCount').textContent = foods.length;
            document.getElementById('bubbleCount').textContent = bubbles.length;
        }

        // === ANIMATION ===
        let lastTime = performance.now();
        let frameCount = 0;
        let fpsTime = 0;

        function animate() {
            requestAnimationFrame(animate);

            const now = performance.now();
            const delta = Math.min((now - lastTime) / 1000, 0.05);
            lastTime = now;

            // FPS counter
            frameCount++;
            fpsTime += delta;
            if (fpsTime >= 1) {
                document.getElementById('fpsCounter').textContent = frameCount;
                frameCount = 0;
                fpsTime = 0;
                updateStats();
            }

            const time = now * 0.001;

            // === UPDATE FISH ===
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Tail animation
                fish.tail.rotation.y = Math.sin(time * fish.tailSpeed + fish.phase) * 0.6;

                // Fin animation
                fish.leftFin.rotation.z = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.3;
                fish.rightFin.rotation.z = -Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.3;

                // Food targeting
                fish.targetFood = null;
                let closestDist = 15;
                for (let f = 0; f < foods.length; f++) {
                    if (foods[f].userData.eaten) continue;
                    const dist = pos.distanceTo(foods[f].position);
                    if (dist < closestDist) {
                        closestDist = dist;
                        fish.targetFood = foods[f];
                    }
                }

                if (fish.targetFood) {
                    // Chase food
                    const dir = new THREE.Vector3().subVectors(fish.targetFood.position, pos).normalize();
                    fish.velocity.lerp(dir.multiplyScalar(fish.speed * 1.5), 0.05);

                    // Eat food
                    if (closestDist < 1.5) {
                        fish.targetFood.userData.eaten = true;
                        scene.remove(fish.targetFood);
                        const idx = foods.indexOf(fish.targetFood);
                        if (idx > -1) foods.splice(idx, 1);
                        // Grow fish
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                        fish.targetFood = null;
                    }
                } else {
                    // Random wandering
                    if (Math.random() < 0.02) {
                        fish.velocity.x += (Math.random() - 0.5) * 1.5;
                        fish.velocity.y += (Math.random() - 0.5) * 0.5;
                        fish.velocity.z += (Math.random() - 0.5) * 1.5;
                    }

                    // Limit speed
                    const currentSpeed = fish.velocity.length();
                    if (currentSpeed > fish.speed) {
                        fish.velocity.normalize().multiplyScalar(fish.speed);
                    }
                }

                // Collision avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0) {
                        const pushDir = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        const pushForce = (fish.avoidanceRadius - dist) / fish.avoidanceRadius * 0.5;
                        fish.velocity.add(pushDir.multiplyScalar(pushForce));
                    }
                }

                // Wall avoidance
                const margin = 2;
                if (pos.x > HALF.x - margin) fish.velocity.x -= 0.3;
                if (pos.x < -HALF.x + margin) fish.velocity.x += 0.3;
                if (pos.y > HALF.y - margin) fish.velocity.y -= 0.2;
                if (pos.y < -HALF.y + margin + 1) fish.velocity.y += 0.3;
                if (pos.z > HALF.z - margin) fish.velocity.z -= 0.3;
                if (pos.z < -HALF.z + margin) fish.velocity.z += 0.3;

                // Apply velocity
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Clamp position
                pos.x = Math.max(-HALF.x + 1, Math.min(HALF.x - 1, pos.x));
                pos.y = Math.max(-HALF.y + 1.5, Math.min(HALF.y - 1, pos.y));
                pos.z = Math.max(-HALF.z + 1, Math.min(HALF.z - 1, pos.z));

                // Rotate towards velocity
                if (fish.velocity.length() > 0.1) {
                    const targetAngle = Math.atan2(fish.velocity.z, fish.velocity.x);
                    const currentAngle = fish.mesh.rotation.y;
                    let angleDiff = targetAngle - currentAngle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                    fish.mesh.rotation.y += angleDiff * 0.05;

                    // Slight pitch based on vertical velocity
                    fish.mesh.rotation.z = -fish.velocity.y * 0.05;
                }
            }

            // === UPDATE BUBBLES ===
            for (let i = 0; i < bubbles.length; i++) {
                const bubble = bubbles[i];
                const ud = bubble.userData;

                bubble.position.y += ud.speed * delta;
                bubble.position.x += Math.sin(time * ud.wobbleSpeed + ud.wobblePhase) * ud.wobbleAmount * delta;
                bubble.position.z += Math.cos(time * ud.wobbleSpeed * 0.7 + ud.wobblePhase) * ud.wobbleAmount * delta;

                // Reset when reaching top
                if (bubble.position.y > HALF.y - 1) {
                    bubble.position.y = -HALF.y + 1;
                    bubble.position.x = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                    bubble.position.z = (Math.random() - 0.5) * (AQUARIUM.depth - 4);
                }
            }

            // === UPDATE FOOD ===
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                food.userData.velocityY += food.userData.gravity * delta;
                food.position.y += food.userData.velocityY * delta;

                // Remove if hits bottom
                if (food.position.y < -HALF.y + 0.5) {
                    scene.remove(food);
                    foods.splice(i, 1);
                }
            }

            // === UPDATE SEAWEED ===
            for (let i = 0; i < seaweeds.length; i++) {
                const sw = seaweeds[i];
                const ud = sw.userData;
                sw.rotation.x = Math.sin(time * ud.speed + ud.phase) * 0.1;
                sw.rotation.z = Math.cos(time * ud.speed * 0.8 + ud.phase) * 0.08;
            }

            // === UPDATE LIGHTS ===
            pointLight1.intensity = 0.6 + Math.sin(time * 0.5) * 0.15;
            pointLight2.intensity = 0.4 + Math.cos(time * 0.7) * 0.1;

            controls.update();
            renderer.render(scene, camera);
        }

        // === RESIZE ===
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // === START ===
        updateStats();
        animate();
    </script>
</body>
</html>
```

Этот файл содержит полностью функциональный 3D аквариум со всеми запрошенными функциями:

**Что реализовано:**

| Функция | Статус |
|---------|--------|
| 15 рыбок с анатомией (тело, глаза, хвост, плавники) | ✅ |
| 8 цветовых схем | ✅ |
| Анимация хвоста и плавников | ✅ |
| Поворот в направлении движения | ✅ |
| Избегание столкновений | ✅ |
| Отражение от стен | ✅ |
| Случайное блуждание | ✅ |
| Преследование корма + рост | ✅ |
| Стеклянный контейнер (transmission) | ✅ |
| Песчаное дно с неровностями | ✅ |
| 8 деформированных камней | ✅ |
| 12 водорослей (TubeGeometry) с анимацией | ✅ |
| 30 пузырей с физикой | ✅ |
| Клик = корм с гравитацией | ✅ |
| Тени (PCFSoftShadowMap, 2048×2048) | ✅ |
| Туман (FogExp2) | ✅ |
| OrbitControls с damping | ✅ |
| UI: кнопки, статистика, FPS | ✅ |
| Glass UI с backdrop-filter | ✅ |

Просто сохраните как `.html` и откройте в браузере.