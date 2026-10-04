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
            box-shadow: 0 8px 32px rgba(0, 50, 100, 0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        }

        .info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        .info-panel h1 {
            font-size: 1.4em;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #00d4ff, #7b68ee, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
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
            font-size: 0.95em;
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
            font-weight: bold;
        }

        .controls {
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
            background: linear-gradient(135deg, #ff6b35, #ff8c42);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.5);
        }

        .btn-bubble {
            background: linear-gradient(135deg, #00b4d8, #0077b6);
            color: white;
            box-shadow: 0 4px 15px rgba(0, 180, 216, 0.3);
        }

        .btn-bubble:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 180, 216, 0.5);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            color: #333;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5);
        }

        .btn:active {
            transform: translateY(0);
        }

        .instructions {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid rgba(100, 180, 255, 0.15);
        }

        .instructions p {
            font-size: 0.75em;
            opacity: 0.7;
        }

        @media (max-width: 768px) {
            .info-panel {
                max-width: 200px;
                padding: 14px;
            }
            .stats-panel {
                min-width: 130px;
                padding: 14px;
            }
            .info-panel h1 {
                font-size: 1.1em;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>Интерактивный подводный мир с реалистичными рыбками и физикой.</p>
        <div class="controls">
            <button class="btn btn-fish" onclick="addFish()">🐟 Добавить рыбку</button>
            <button class="btn btn-bubble" onclick="addBubbles()">💨 Больше пузырей</button>
            <button class="btn btn-light" onclick="toggleLight()">💡 Свет</button>
        </div>
        <div class="instructions">
            <p>🖱️ ЛКМ + движение — вращение</p>
            <p>🖱️ ПКМ + движение — панорама</p>
            <p>⚙️ Колесо — зум</p>
            <p>👆 Клик по воде — кормить</p>
        </div>
    </div>

    <div class="panel stats-panel">
        <h3>📊 Статистика</h3>
        <div class="stat-item">
            <span>Рыбки:</span>
            <span class="stat-value" id="fish-count">0</span>
        </div>
        <div class="stat-item">
            <span>Пузыри:</span>
            <span class="stat-value" id="bubble-count">0</span>
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

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);
        scene.background = new THREE.Color(0x0a2a4a);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(20, 12, 25);

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

        // === LIGHTING ===
        const ambientLight = new THREE.AmbientLight(0x404060, 0.5);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 1.0);
        dirLight.position.set(15, 30, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 80;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 20;
        dirLight.shadow.camera.bottom = -10;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x00aaff, 0.6, 40);
        pointLight1.position.set(-10, 15, -5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x0066ff, 0.4, 35);
        pointLight2.position.set(10, 8, 8);
        scene.add(pointLight2);

        // === AQUARIUM BOUNDS ===
        const AQUARIUM = { x: 18, y: 12, z: 10 };

        // === GLASS CONTAINER ===
        const glassGeometry = new THREE.BoxGeometry(AQUARIUM.x * 2, AQUARIUM.y * 2, AQUARIUM.z * 2);
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
        glassBox.position.y = AQUARIUM.y;
        scene.add(glassBox);

        const edgesGeometry = new THREE.EdgesGeometry(glassGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x4488cc, transparent: true, opacity: 0.4 });
        const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        edges.position.y = AQUARIUM.y;
        scene.add(edges);

        // === SAND FLOOR ===
        const sandGeometry = new THREE.PlaneGeometry(AQUARIUM.x * 2, AQUARIUM.z * 2, 40, 40);
        const sandPositions = sandGeometry.attributes.position;
        for (let i = 0; i < sandPositions.count; i++) {
            sandPositions.setZ(i, Math.random() * 0.3 + Math.sin(sandPositions.getX(i) * 0.5) * 0.2);
        }
        sandGeometry.computeVertexNormals();
        const sandMaterial = new THREE.MeshStandardMaterial({
            color: 0xd4a853,
            roughness: 0.9,
            metalness: 0.0
        });
        const sandFloor = new THREE.Mesh(sandGeometry, sandMaterial);
        sandFloor.rotation.x = -Math.PI / 2;
        sandFloor.position.y = 0.1;
        sandFloor.receiveShadow = true;
        scene.add(sandFloor);

        // === ROCKS ===
        function createRock(x, y, z) {
            const geo = new THREE.DodecahedronGeometry(1 + Math.random() * 1.2, 1);
            const pos = geo.attributes.position;
            for (let i = 0; i < pos.count; i++) {
                pos.setX(i, pos.getX(i) * (0.7 + Math.random() * 0.6));
                pos.setY(i, pos.getY(i) * (0.5 + Math.random() * 0.4));
                pos.setZ(i, pos.getZ(i) * (0.7 + Math.random() * 0.6));
            }
            geo.computeVertexNormals();
            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(0.05 + Math.random() * 0.1, 0.2, 0.3 + Math.random() * 0.2),
                roughness: 0.85,
                metalness: 0.05
            });
            const rock = new THREE.Mesh(geo, mat);
            rock.position.set(x, y, z);
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.castShadow = true;
            rock.receiveShadow = true;
            scene.add(rock);
        }

        for (let i = 0; i < 8; i++) {
            createRock(
                (Math.random() - 0.5) * AQUARIUM.x * 1.6,
                0.5 + Math.random() * 0.5,
                (Math.random() - 0.5) * AQUARIUM.z * 1.6
            );
        }

        // === SEAWEED ===
        const seaweeds = [];
        function createSeaweed(x, z) {
            const height = 3 + Math.random() * 5;
            const points = [];
            for (let i = 0; i <= 8; i++) {
                points.push(new THREE.Vector3(
                    Math.sin(i * 0.3) * 0.3,
                    i * (height / 8),
                    Math.cos(i * 0.4) * 0.2
                ));
            }
            const curve = new THREE.CatmullRomCurve3(points);
            const geo = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);
            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(0.3 + Math.random() * 0.15, 0.7, 0.25 + Math.random() * 0.15),
                roughness: 0.7,
                side: THREE.DoubleSide
            });
            const seaweed = new THREE.Mesh(geo, mat);
            seaweed.position.set(x, 0.2, z);
            seaweed.castShadow = true;
            scene.add(seaweed);
            seaweeds.push({ mesh: seaweed, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 });
        }

        for (let i = 0; i < 12; i++) {
            createSeaweed(
                (Math.random() - 0.5) * AQUARIUM.x * 1.6,
                (Math.random() - 0.5) * AQUARIUM.z * 1.6
            );
        }

        // === FISH COLOR SCHEMES ===
        const colorSchemes = [
            { body: 0xff6b35, fin: 0xff8c42 },   // Orange
            { body: 0x2196f3, fin: 0x64b5f6 },   // Blue
            { body: 0xffeb3b, fin: 0xff5722 },   // Yellow-Red
            { body: 0x9c27b0, fin: 0xce93d8 },   // Purple
            { body: 0xf44336, fin: 0xef9a9a },   // Red
            { body: 0x4caf50, fin: 0xa5d6a7 },   // Green
            { body: 0xe91e63, fin: 0xf48fb1 },   // Pink
            { body: 0xffd700, fin: 0xffa000 }    // Gold
        ];

        // === FISH CREATION ===
        const fishArray = [];

        function createFish(x, y, z) {
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.5, 0.7, 0.5);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.3,
                metalness: 0.2
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.2, 8, 8);
            const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1 });
            const pupilGeo = new THREE.SphereGeometry(0.1, 6, 6);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            leftEye.position.set(0.9, 0.2, 0.3);
            group.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(1.05, 0.2, 0.35);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            rightEye.position.set(0.9, 0.2, -0.3);
            group.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(1.05, 0.2, -0.35);
            group.add(rightPupil);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 4);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.85,
                side: THREE.DoubleSide
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.6, 0, 0);
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 3);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.75,
                side: THREE.DoubleSide
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0.2, 0.6, 0);
            topFin.rotation.z = -0.3;
            group.add(topFin);

            // Side fins
            const finGeo = new THREE.ConeGeometry(0.2, 0.6, 3);
            const finMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.7,
                side: THREE.DoubleSide
            });

            const leftFin = new THREE.Mesh(finGeo, finMat);
            leftFin.position.set(0.2, -0.1, 0.45);
            leftFin.rotation.x = Math.PI / 2;
            leftFin.rotation.z = 0.5;
            group.add(leftFin);

            const rightFin = new THREE.Mesh(finGeo, finMat);
            rightFin.position.set(0.2, -0.1, -0.45);
            rightFin.rotation.x = -Math.PI / 2;
            rightFin.rotation.z = -0.5;
            group.add(rightFin);

            group.position.set(x, y, z);
            group.scale.setScalar(scale);
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
                speed: 1.5 + Math.random() * 2.5,
                tailSpeed: 3 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2.5 + Math.random() * 1.5,
                wanderTimer: 0,
                wanderInterval: 2 + Math.random() * 4,
                scale: scale
            };
            fishArray.push(fish);
            return fish;
        }

        // Create initial 15 fish
        for (let i = 0; i < 15; i++) {
            createFish(
                (Math.random() - 0.5) * AQUARIUM.x * 1.4,
                2 + Math.random() * (AQUARIUM.y * 1.6),
                (Math.random() - 0.5) * AQUARIUM.z * 1.4
            );
        }

        // === BUBBLES ===
        const bubbles = [];
        function createBubble(x, y, z) {
            const size = 0.1 + Math.random() * 0.25;
            const geo = new THREE.SphereGeometry(size, 12, 12);
            const mat = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3,
                transmission: 0.9,
                roughness: 0.0,
                metalness: 0.0,
                ior: 1.3
            });
            const bubble = new THREE.Mesh(geo, mat);
            bubble.position.set(x, y, z);
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
            createBubble(
                (Math.random() - 0.5) * AQUARIUM.x * 1.6,
                Math.random() * AQUARIUM.y * 1.8,
                (Math.random() - 0.5) * AQUARIUM.z * 1.6
            );
        }

        // === FOOD SYSTEM ===
        const foods = [];
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function createFood(point) {
            const geo = new THREE.SphereGeometry(0.2, 8, 8);
            const mat = new THREE.MeshStandardMaterial({
                color: 0x8b4513,
                roughness: 0.8
            });
            const food = new THREE.Mesh(geo, mat);
            food.position.copy(point);
            scene.add(food);
            foods.push({
                mesh: food,
                velocityY: 0,
                gravity: -2.5,
                eaten: false
            });
        }

        renderer.domElement.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -AQUARIUM.y * 1.5);
            const intersectPoint = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersectPoint);

            if (intersectPoint) {
                intersectPoint.x = Math.max(-AQUARIUM.x + 1, Math.min(AQUARIUM.x - 1, intersectPoint.x));
                intersectPoint.z = Math.max(-AQUARIUM.z + 1, Math.min(AQUARIUM.z - 1, intersectPoint.z));
                createFood(intersectPoint);
            }
        });

        // === UI FUNCTIONS ===
        function addFish() {
            createFish(
                (Math.random() - 0.5) * AQUARIUM.x,
                3 + Math.random() * AQUARIUM.y,
                (Math.random() - 0.5) * AQUARIUM.z
            );
        }

        function addBubbles() {
            for (let i = 0; i < 10; i++) {
                createBubble(
                    (Math.random() - 0.5) * AQUARIUM.x * 1.6,
                    0.5,
                    (Math.random() - 0.5) * AQUARIUM.z * 1.6
                );
            }
        }

        let lightOn = true;
        function toggleLight() {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.0 : 0.15;
        }

        // === ANIMATION ===
        const clock = new THREE.Clock();
        let frameCount = 0;
        let lastFpsTime = 0;
        let fps = 60;

        function animate() {
            requestAnimationFrame(animate);
            const delta = Math.min(clock.getDelta(), 0.05);
            const time = clock.getElapsedTime();

            // FPS counter
            frameCount++;
            if (time - lastFpsTime >= 1) {
                fps = frameCount;
                frameCount = 0;
                lastFpsTime = time;
                document.getElementById('fps-counter').textContent = fps;
            }

            // Update fish
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;
                const vel = fish.velocity;

                // Tail animation
                fish.tail.rotation.y = Math.sin(time * fish.tailSpeed + fish.phase) * 0.6;
                fish.leftFin.rotation.z = 0.5 + Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.3;
                fish.rightFin.rotation.z = -0.5 + Math.sin(time * fish.tailSpeed * 0.7 + fish.phase + 1) * 0.3;

                // Wandering behavior
                fish.wanderTimer += delta;
                if (fish.wanderTimer > fish.wanderInterval) {
                    fish.wanderTimer = 0;
                    fish.wanderInterval = 2 + Math.random() * 4;
                    vel.x += (Math.random() - 0.5) * 2;
                    vel.y += (Math.random() - 0.5) * 0.8;
                    vel.z += (Math.random() - 0.5) * 2;
                }

                // Food chasing
                fish.targetFood = null;
                let closestDist = 15;
                for (let f = 0; f < foods.length; f++) {
                    if (foods[f].eaten) continue;
                    const dist = pos.distanceTo(foods[f].mesh.position);
                    if (dist < closestDist) {
                        closestDist = dist;
                        fish.targetFood = foods[f];
                    }
                }

                if (fish.targetFood) {
                    const dir = new THREE.Vector3().subVectors(fish.targetFood.mesh.position, pos).normalize();
                    vel.add(dir.multiplyScalar(3 * delta));
                    fish.speed = Math.min(fish.speed + delta * 2, 6);

                    // Eat food
                    if (pos.distanceTo(fish.targetFood.mesh.position) < 1.0) {
                        fish.targetFood.eaten = true;
                        scene.remove(fish.targetFood.mesh);
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                    }
                } else {
                    fish.speed = Math.max(fish.speed - delta * 0.5, 1.5);
                }

                // Avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius) {
                        const pushDir = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        const force = (fish.avoidanceRadius - dist) / fish.avoidanceRadius;
                        vel.add(pushDir.multiplyScalar(force * 4 * delta));
                    }
                }

                // Wall avoidance
                const margin = 2;
                if (pos.x > AQUARIUM.x - margin) vel.x -= 3 * delta;
                if (pos.x < -AQUARIUM.x + margin) vel.x += 3 * delta;
                if (pos.y > AQUARIUM.y * 2 - margin) vel.y -= 3 * delta;
                if (pos.y < 1.5) vel.y += 3 * delta;
                if (pos.z > AQUARIUM.z - margin) vel.z -= 3 * delta;
                if (pos.z < -AQUARIUM.z + margin) vel.z += 3 * delta;

                // Normalize and apply velocity
                vel.normalize().multiplyScalar(fish.speed);
                pos.add(vel.clone().multiplyScalar(delta));

                // Clamp position
                pos.x = Math.max(-AQUARIUM.x + 0.5, Math.min(AQUARIUM.x - 0.5, pos.x));
                pos.y = Math.max(1, Math.min(AQUARIUM.y * 2 - 0.5, pos.y));
                pos.z = Math.max(-AQUARIUM.z + 0.5, Math.min(AQUARIUM.z - 0.5, pos.z));

                // Rotate fish to face direction
                if (vel.lengthSq() > 0.01) {
                    const targetAngle = Math.atan2(vel.z, vel.x);
                    let currentAngle = fish.mesh.rotation.y;
                    let diff = targetAngle - currentAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    fish.mesh.rotation.y += diff * 3 * delta;

                    // Slight pitch based on vertical velocity
                    fish.mesh.rotation.z = -vel.y * 0.1;
                }
            }

            // Update bubbles
            for (let i = 0; i < bubbles.length; i++) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * delta;
                b.mesh.position.x += Math.sin(time * b.wobbleSpeed + b.wobblePhase) * b.wobbleAmp * delta;
                b.mesh.position.z += Math.cos(time * b.wobbleSpeed * 0.7 + b.wobblePhase) * b.wobbleAmp * delta;

                if (b.mesh.position.y > AQUARIUM.y * 2 - 0.5) {
                    b.mesh.position.y = 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * AQUARIUM.x * 1.6;
                    b.mesh.position.z = (Math.random() - 0.5) * AQUARIUM.z * 1.6;
                }
            }

            // Update food
            for (let i = foods.length - 1; i >= 0; i--) {
                const f = foods[i];
                if (f.eaten) continue;
                f.velocityY += f.gravity * delta;
                f.mesh.position.y += f.velocityY * delta;

                if (f.mesh.position.y < 0.3) {
                    scene.remove(f.mesh);
                    foods.splice(i, 1);
                }
            }

            // Update seaweed
            for (let i = 0; i < seaweeds.length; i++) {
                const sw = seaweeds[i];
                sw.mesh.rotation.x = Math.sin(time * sw.speed + sw.phase) * 0.08;
                sw.mesh.rotation.z = Math.cos(time * sw.speed * 0.8 + sw.phase) * 0.06;
            }

            // Update stats
            document.getElementById('fish-count').textContent = fishArray.length;
            document.getElementById('bubble-count').textContent = bubbles.length;
            document.getElementById('food-count').textContent = foods.filter(f => !f.eaten).length;

            controls.update();
            renderer.render(scene, camera);
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

Этот файл содержит полностью функциональный 3D аквариум. Вот что реализовано:

**🐠 Рыбки (15 на старте):**
- Детализированная анатомия: тело, глаза с зрачками, хвост, верхний и боковые плавники
- 8 цветовых схем, случайный масштаб 0.6–1.2
- Анимация хвоста и плавников с индивидуальной частотой

**🧠 ИИ поведение:**
- Избегание столкновений между рыбками
- Отражение от стен аквариума
- Случайное блуждание с таймером
- Преследование корма в радиусе 15 единиц
- Рост на 5% при поедании

**🌊 Окружение:**
- Стеклянный контейнер (36×24×20) с transmission
- Песчаное дно с процедурными неровностями
- 8 деформированных камней, 12 кустов водорослей (TubeGeometry)

**💭 Пузыри (30):** прозрачные сферы, движение вверх с покачиванием

**🍽️ Кормление:** клик по аквариуму создаёт корм с гравитацией

**💡 Освещение:** ambient + directional (с тенями 2048²) + 2 point lights, переключение кнопкой

**🎮 Управление:** OrbitControls с damping, зумом и ограничениями