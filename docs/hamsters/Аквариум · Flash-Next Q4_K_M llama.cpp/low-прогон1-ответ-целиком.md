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
            background: rgba(10, 25, 50, 0.65);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        .stats-panel {
            top: 20px;
            right: 20px;
            min-width: 180px;
        }

        .panel h2 {
            font-size: 1.3em;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #42a5f5, #1e88e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
        }

        .panel p {
            font-size: 0.85em;
            line-height: 1.6;
            color: #a0c8e8;
            margin-bottom: 8px;
        }

        .btn {
            display: block;
            width: 100%;
            padding: 10px 16px;
            margin: 8px 0;
            border: none;
            border-radius: 10px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.5);
        }

        .btn-bubbles {
            background: linear-gradient(135deg, #4fc3f7, #0288d1);
            box-shadow: 0 4px 15px rgba(79, 195, 247, 0.3);
        }

        .btn-bubbles:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79, 195, 247, 0.5);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd54f, #ff8f00);
            box-shadow: 0 4px 15px rgba(255, 213, 79, 0.3);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 213, 79, 0.5);
        }

        .btn:active {
            transform: translateY(0);
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(100, 180, 255, 0.1);
        }

        .stat-row:last-child {
            border-bottom: none;
        }

        .stat-label {
            color: #80b0d0;
            font-size: 0.85em;
        }

        .stat-value {
            color: #64b5f6;
            font-weight: 700;
            font-size: 1.1em;
        }

        .hint {
            font-size: 0.75em;
            color: #607d99;
            font-style: italic;
            margin-top: 8px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .pulse {
            animation: pulse 2s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel info-panel">
        <h2>🐠 3D Аквариум</h2>
        <p>🖱️ Левый клик + движение — вращение</p>
        <p>🖱️ Правый клик + движение — панорама</p>
        <p>🖱️ Колесо мыши — масштаб</p>
        <p>👆 Клик по аквариуму — кормление</p>
        <button class="btn btn-fish" id="btnAddFish">🐟 Добавить рыбку</button>
        <button class="btn btn-bubbles" id="btnAddBubbles">💨 Больше пузырей</button>
        <button class="btn btn-light" id="btnLight">💡 Свет вкл/выкл</button>
        <p class="hint">Кликните по воде, чтобы бросить корм</p>
    </div>

    <div class="panel stats-panel">
        <h2>📊 Статистика</h2>
        <div class="stat-row">
            <span class="stat-label">Рыбки:</span>
            <span class="stat-value" id="fishCount">15</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Пузыри:</span>
            <span class="stat-value" id="bubbleCount">30</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Корм:</span>
            <span class="stat-value" id="foodCount">0</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">FPS:</span>
            <span class="stat-value" id="fpsCounter">60</span>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a1628, 0.015);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(30, 15, 35);

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
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(15, 30, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 100;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 20;
        dirLight.shadow.camera.bottom = -20;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x4fc3f7, 0.6, 40);
        pointLight1.position.set(-10, 15, 5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x1565c0, 0.5, 40);
        pointLight2.position.set(10, 10, -5);
        scene.add(pointLight2);

        let lightOn = true;

        // === AQUARIUM GLASS BOX ===
        const tankWidth = 36, tankHeight = 24, tankDepth = 20;

        const glassMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x88ccff,
            transparent: true,
            opacity: 0.1,
            transmission: 0.95,
            roughness: 0.05,
            metalness: 0,
            side: THREE.DoubleSide
        });

        const glassBox = new THREE.Mesh(
            new THREE.BoxGeometry(tankWidth, tankHeight, tankDepth),
            glassMaterial
        );
        glassBox.position.y = tankHeight / 2;
        scene.add(glassBox);

        const edgesGeometry = new THREE.EdgesGeometry(new THREE.BoxGeometry(tankWidth, tankHeight, tankDepth));
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x64b5f6, transparent: true, opacity: 0.4 });
        const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        edges.position.y = tankHeight / 2;
        scene.add(edges);

        // === SAND FLOOR ===
        const sandGeometry = new THREE.PlaneGeometry(tankWidth, tankDepth, 32, 32);
        const sandPositions = sandGeometry.attributes.position;
        for (let i = 0; i < sandPositions.count; i++) {
            sandPositions.setZ(i, (Math.random() - 0.5) * 0.5);
        }
        sandGeometry.computeVertexNormals();

        const sandMaterial = new THREE.MeshStandardMaterial({
            color: 0xc2a060,
            roughness: 0.9,
            metalness: 0.1
        });
        const sandFloor = new THREE.Mesh(sandGeometry, sandMaterial);
        sandFloor.rotation.x = -Math.PI / 2;
        sandFloor.position.y = 0.2;
        sandFloor.receiveShadow = true;
        scene.add(sandFloor);

        // === ROCKS ===
        function createRock() {
            const geo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 0.6, 1);
            const positions = geo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                positions.setX(i, positions.getX(i) + (Math.random() - 0.5) * 0.3);
                positions.setY(i, positions.getY(i) + (Math.random() - 0.5) * 0.3);
                positions.setZ(i, positions.getZ(i) + (Math.random() - 0.5) * 0.3);
            }
            geo.computeVertexNormals();

            const colors = [0x6b7b8a, 0x8a7b6b, 0x5a6a5a, 0x7a6a5a, 0x6a7a7a];
            const mat = new THREE.MeshStandardMaterial({
                color: colors[Math.floor(Math.random() * colors.length)],
                roughness: 0.9,
                metalness: 0.1
            });
            const rock = new THREE.Mesh(geo, mat);
            rock.castShadow = true;
            rock.receiveShadow = true;
            return rock;
        }

        for (let i = 0; i < 8; i++) {
            const rock = createRock();
            rock.position.set(
                (Math.random() - 0.5) * (tankWidth - 6),
                0.5 + Math.random() * 0.5,
                (Math.random() - 0.5) * (tankDepth - 6)
            );
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.scale.setScalar(0.8 + Math.random() * 1.2);
            scene.add(rock);
        }

        // === PLANTS ===
        const plants = [];
        function createPlant() {
            const group = new THREE.Group();
            const height = 3 + Math.random() * 4;
            const segments = 8;
            const points = [];
            const curve = new THREE.CatmullRomCurve3([
                new THREE.Vector3(0, 0, 0),
                new THREE.Vector3((Math.random() - 0.5) * 1, height * 0.3, (Math.random() - 0.5) * 1),
                new THREE.Vector3((Math.random() - 0.5) * 1.5, height * 0.6, (Math.random() - 0.5) * 1.5),
                new THREE.Vector3((Math.random() - 0.5) * 0.5, height, (Math.random() - 0.5) * 0.5)
            ]);

            const tubeGeo = new THREE.TubeGeometry(curve, segments, 0.15 + Math.random() * 0.1, 6, false);
            const greenColors = [0x2e7d32, 0x388e3c, 0x43a047, 0x66bb6a, 0x1b5e20];
            const mat = new THREE.MeshStandardMaterial({
                color: greenColors[Math.floor(Math.random() * greenColors.length)],
                roughness: 0.7,
                metalness: 0
            });
            const tube = new THREE.Mesh(tubeGeo, mat);
            tube.castShadow = true;
            group.add(tube);

            // Add leaf
            const leafGeo = new THREE.SphereGeometry(0.4 + Math.random() * 0.3, 6, 6);
            const leafMat = new THREE.MeshStandardMaterial({
                color: greenColors[Math.floor(Math.random() * greenColors.length)],
                roughness: 0.7
            });
            const leaf = new THREE.Mesh(leafGeo, leafMat);
            leaf.position.y = height * 0.7;
            leaf.scale.set(1, 1.5, 0.3);
            group.add(leaf);

            return group;
        }

        for (let i = 0; i < 12; i++) {
            const plant = createPlant();
            plant.position.set(
                (Math.random() - 0.5) * (tankWidth - 8),
                0.3,
                (Math.random() - 0.5) * (tankDepth - 6)
            );
            plant.userData = {
                baseRotX: (Math.random() - 0.5) * 0.3,
                baseRotZ: (Math.random() - 0.5) * 0.3,
                speed: 0.5 + Math.random() * 1.5,
                phase: Math.random() * Math.PI * 2
            };
            scene.add(plant);
            plants.push(plant);
        }

        // === FISH CREATION ===
        const fishArray = [];
        const fishColors = [
            { body: 0xff6b35, fin: 0xff8a50 },
            { body: 0x2196f3, fin: 0x64b5f6 },
            { body: 0xffeb3b, fin: 0xff5722 },
            { body: 0x9c27b0, fin: 0xce93d9 },
            { body: 0xf44336, fin: 0xef9a9a },
            { body: 0x4caf50, fin: 0xa5d6a7 },
            { body: 0xe91e63, fin: 0xf48fb1 },
            { body: 0xffc107, fin: 0xffd54f }
        ];

        function createFish() {
            const group = new THREE.Group();
            const colorScheme = fishColors[Math.floor(Math.random() * fishColors.length)];
            const scale = 0.6 + Math.random() * 0.6;

            // Body
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.4, 0.8, 0.6);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: colorScheme.body,
                roughness: 0.3,
                metalness: 0.2
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Eye
            const eyeGeo = new THREE.SphereGeometry(0.2, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const eye = new THREE.Mesh(eyeGeo, eyeMat);
            eye.position.set(0.9, 0.15, 0.25);
            group.add(eye);

            const pupilGeo = new THREE.SphereGeometry(0.1, 6, 6);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });
            const pupil = new THREE.Mesh(pupilGeo, pupilMat);
            pupil.position.set(1.0, 0.15, 0.3);
            group.add(pupil);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
            const tailMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.9
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.5, 0, 0);
            tail.rotation.z = Math.PI / 2;
            tail.castShadow = true;
            group.add(tail);

            // Left fin
            const finGeo = new THREE.ConeGeometry(0.3, 0.7, 6);
            const finMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.85
            });
            const leftFin = new THREE.Mesh(finGeo, finMat);
            leftFin.position.set(0.2, 0, 0.6);
            leftFin.rotation.x = Math.PI / 2;
            group.add(leftFin);

            // Right fin
            const rightFin = new THREE.Mesh(finGeo, finMat.clone());
            rightFin.position.set(0.2, 0, -0.6);
            rightFin.rotation.x = -Math.PI / 2;
            group.add(rightFin);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.25, 0.6, 6);
            const topFin = new THREE.Mesh(topFinGeo, finMat.clone());
            topFin.position.set(-0.2, 0.7, 0);
            group.add(topFin);

            group.scale.setScalar(scale);
            group.castShadow = true;

            return {
                mesh: group,
                tail: tail,
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
                avoidanceRadius: 3 + Math.random() * 2,
                wanderTimer: 0,
                wanderInterval: 2 + Math.random() * 3
            };
        }

        // Spawn initial fish
        for (let i = 0; i < 15; i++) {
            const fish = createFish();
            fish.mesh.position.set(
                (Math.random() - 0.5) * (tankWidth - 8),
                3 + Math.random() * (tankHeight - 8),
                (Math.random() - 0.5) * (tankDepth - 6)
            );
            scene.add(fish.mesh);
            fishArray.push(fish);
        }

        // === BUBBLES ===
        const bubbles = [];
        function createBubble() {
            const size = 0.1 + Math.random() * 0.25;
            const geo = new THREE.SphereGeometry(size, 8, 8);
            const mat = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.4,
                transmission: 0.8,
                roughness: 0.1,
                metalness: 0,
                clearcoat: 1
            });
            const bubble = new THREE.Mesh(geo, mat);
            bubble.position.set(
                (Math.random() - 0.5) * (tankWidth - 4),
                Math.random() * tankHeight,
                (Math.random() - 0.5) * (tankDepth - 4)
            );
            bubble.userData = {
                speed: 0.5 + Math.random() * 1.5,
                wobbleSpeed: 1 + Math.random() * 3,
                wobbleAmount: 0.3 + Math.random() * 0.5,
                phase: Math.random() * Math.PI * 2
            };
            scene.add(bubble);
            bubbles.push(bubble);
            return bubble;
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // === FOOD ===
        const foodItems = [];
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function createFood(point) {
            const geo = new THREE.SphereGeometry(0.25, 6, 6);
            const mat = new THREE.MeshStandardMaterial({
                color: 0x8d6e63,
                roughness: 0.8
            });
            const food = new THREE.Mesh(geo, mat);
            food.position.set(point.x, tankHeight - 1, point.z);
            food.userData = {
                vy: 0,
                gravity: -2,
                active: true
            };
            scene.add(food);
            foodItems.push(food);
            updateStats();
        }

        // === RAYCASTER CLICK ===
        let isMouseDown = false;
        let mouseDownTime = 0;
        let mouseDownPos = { x: 0, y: 0 };

        renderer.domElement.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseDownTime = Date.now();
            mouseDownPos = { x: e.clientX, y: e.clientY };
        });

        renderer.domElement.addEventListener('mouseup', (e) => {
            const elapsed = Date.now() - mouseDownTime;
            const dx = e.clientX - mouseDownPos.x;
            const dy = e.clientY - mouseDownPos.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (elapsed < 300 && dist < 10) {
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
                raycaster.setFromCamera(mouse, camera);

                const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
                const point = new THREE.Vector3();
                raycaster.ray.intersectPlane(plane, point);

                if (Math.abs(point.x) < tankWidth / 2 && Math.abs(point.z) < tankDepth / 2) {
                    createFood(point);
                }
            }
            isMouseDown = false;
        });

        // === UI BUTTONS ===
        document.getElementById('btnAddFish').addEventListener('click', () => {
            const fish = createFish();
            fish.mesh.position.set(
                (Math.random() - 0.5) * (tankWidth - 8),
                3 + Math.random() * (tankHeight - 8),
                (Math.random() - 0.5) * (tankDepth - 6)
            );
            scene.add(fish.mesh);
            fishArray.push(fish);
            updateStats();
        });

        document.getElementById('btnAddBubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
            updateStats();
        });

        document.getElementById('btnLight').addEventListener('click', () => {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 0.8 : 0;
            ambientLight.intensity = lightOn ? 0.4 : 0.1;
        });

        function updateStats() {
            document.getElementById('fishCount').textContent = fishArray.length;
            document.getElementById('bubbleCount').textContent = bubbles.length;
            document.getElementById('foodCount').textContent = foodItems.length;
        }

        // === ANIMATION LOOP ===
        let lastTime = performance.now();
        let frameCount = 0;
        let fpsTime = 0;

        function animate(currentTime) {
            requestAnimationFrame(animate);

            const delta = Math.min((currentTime - lastTime) / 1000, 0.05);
            lastTime = currentTime;

            // FPS counter
            frameCount++;
            fpsTime += delta;
            if (fpsTime >= 1) {
                document.getElementById('fpsCounter').textContent = Math.round(frameCount / fpsTime);
                frameCount = 0;
                fpsTime = 0;
            }

            const time = currentTime * 0.001;

            // === ANIMATE FISH ===
            fishArray.forEach(fish => {
                const mesh = fish.mesh;
                const pos = mesh.position;

                // Wander behavior
                fish.wanderTimer += delta;
                if (fish.wanderTimer > fish.wanderInterval) {
                    fish.wanderTimer = 0;
                    fish.velocity.x += (Math.random() - 0.5) * 2;
                    fish.velocity.y += (Math.random() - 0.5) * 1;
                    fish.velocity.z += (Math.random() - 0.5) * 2;
                    fish.wanderInterval = 2 + Math.random() * 3;
                }

                // Food seeking
                fish.targetFood = null;
                let closestDist = 15;
                foodItems.forEach(food => {
                    if (!food.userData.active) return;
                    const dist = pos.distanceTo(food.position);
                    if (dist < closestDist) {
                        closestDist = dist;
                        fish.targetFood = food;
                    }
                });

                if (fish.targetFood) {
                    const dir = new THREE.Vector3().subVectors(fish.targetFood.position, pos).normalize();
                    fish.velocity.lerp(dir.multiplyScalar(fish.speed * 2), delta * 3);

                    if (pos.distanceTo(fish.targetFood.position) < 1.5) {
                        fish.targetFood.userData.active = false;
                        scene.remove(fish.targetFood);
                        const idx = foodItems.indexOf(fish.targetFood);
                        if (idx > -1) foodItems.splice(idx, 1);
                        const newScale = mesh.scale.x * 1.05;
                        mesh.scale.setScalar(Math.min(newScale, 2.5));
                        fish.targetFood = null;
                        updateStats();
                    }
                }

                // Avoidance
                fishArray.forEach(other => {
                    if (other === fish) return;
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const push = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        push.multiplyScalar((fish.avoidanceRadius - dist) / fish.avoidanceRadius * 3);
                        fish.velocity.add(push.multiplyScalar(delta * 5));
                    }
                });

                // Wall bounce
                const margin = 2;
                const hw = tankWidth / 2 - margin;
                const hh = tankHeight / 2;
                const hd = tankDepth / 2 - margin;

                if (pos.x > hw) { fish.velocity.x -= delta * 10; }
                if (pos.x < -hw) { fish.velocity.x += delta * 10; }
                if (pos.y > hh - 1) { fish.velocity.y -= delta * 10; }
                if (pos.y < 2) { fish.velocity.y += delta * 10; }
                if (pos.z > hd) { fish.velocity.z -= delta * 10; }
                if (pos.z < -hd) { fish.velocity.z += delta * 10; }

                // Damping
                fish.velocity.multiplyScalar(0.98);

                // Clamp velocity
                const maxSpeed = fish.speed * 1.5;
                if (fish.velocity.length() > maxSpeed) {
                    fish.velocity.normalize().multiplyScalar(maxSpeed);
                }

                // Update position
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Clamp position
                pos.x = Math.max(-hw, Math.min(hw, pos.x));
                pos.y = Math.max(1.5, Math.min(hh - 1, pos.y));
                pos.z = Math.max(-hd, Math.min(hd, pos.z));

                // Rotate to face movement direction
                if (fish.velocity.length() > 0.1) {
                    const targetAngle = Math.atan2(-fish.velocity.z, fish.velocity.x);
                    mesh.rotation.y += (targetAngle - mesh.rotation.y) * delta * 3;
                }

                // Tail animation
                const tailWag = Math.sin(time * fish.tailSpeed + fish.phase) * 0.5;
                fish.tail.rotation.y = tailWag;

                // Fin animation
                fish.leftFin.rotation.z = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.3;
                fish.rightFin.rotation.z = -Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.3;

                // Slight body wobble
                mesh.rotation.z = Math.sin(time * fish.tailSpeed * 0.5 + fish.phase) * 0.05;
            });

            // === ANIMATE BUBBLES ===
            bubbles.forEach(bubble => {
                const ud = bubble.userData;
                bubble.position.y += ud.speed * delta;
                bubble.position.x += Math.sin(time * ud.wobbleSpeed + ud.phase) * ud.wobbleAmount * delta;
                bubble.position.z += Math.cos(time * ud.wobbleSpeed * 0.7 + ud.phase) * ud.wobbleAmount * delta * 0.5;

                if (bubble.position.y > tankHeight + 1) {
                    bubble.position.y = -1;
                    bubble.position.x = (Math.random() - 0.5) * (tankWidth - 4);
                    bubble.position.z = (Math.random() - 0.5) * (tankDepth - 4);
                }
            });

            // === ANIMATE FOOD ===
            for (let i = foodItems.length - 1; i >= 0; i--) {
                const food = foodItems[i];
                if (!food.userData.active) continue;
                food.userData.vy += food.userData.gravity * delta;
                food.position.y += food.userData.vy * delta;
                food.rotation.x += delta * 2;
                food.rotation.z += delta * 1.5;

                if (food.position.y <= 0.5) {
                    food.userData.active = false;
                    scene.remove(food);
                    foodItems.splice(i, 1);
                    updateStats();
                }
            }

            // === ANIMATE PLANTS ===
            plants.forEach(plant => {
                const ud = plant.userData;
                plant.rotation.x = ud.baseRotX + Math.sin(time * ud.speed + ud.phase) * 0.1;
                plant.rotation.z = ud.baseRotZ + Math.cos(time * ud.speed * 0.8 + ud.phase) * 0.08;
            });

            // === CAUSTIC LIGHT EFFECT ===
            pointLight1.intensity = 0.5 + Math.sin(time * 0.5) * 0.15;
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

        // Start
        updateStats();
        animate(performance.now());
    </script>
</body>
</html>
```

Этот файл представляет собой полностью самодостаточный 3D аквариум. Вот что реализовано:

**🐠 Рыбки (15 штук):**
- Детализированная анатомия (тело, глаза, хвост, 3 плавника)
- 8 цветовых схем, случайный масштаб
- Анимация хвоста и плавников с разной частотой
- Поворот в направлении движения

**🧠 Поведение:**
- Избегание столкновений между рыбками
- Отражение от стен аквариума
- Случайное блуждание с таймером
- Преследование корма (радиус 15)
- Рост на 5% после поедания корма

**🌊 Окружение:**
- Стеклянный контейнер с `transmission: 0.95`
- Песчаное дно с процедурными неровностями
- 8 деформированных камней
- 12 водорослей (TubeGeometry + CatmullRomCurve3) с покачиванием

**💭 Пузыри:** 30 штук с движением вверх и покачиванием

**🍽️ Кормление:** Raycaster по клику, физика падения, рост рыбок

**💡 Освещение:** Ambient + Directional (тени 2048×2048) + 2 PointLight с пульсацией

**🎮 Управление:** OrbitControls с damping, ограничениями зума и угла