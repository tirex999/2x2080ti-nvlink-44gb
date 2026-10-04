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
            background: linear-gradient(180deg, #0a1628 0%, #1a3a5c 100%);
        }

        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
        }

        .glass-panel {
            position: fixed;
            background: rgba(10, 30, 60, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 12px;
            padding: 16px 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            z-index: 100;
        }

        .info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        .info-panel h1 {
            font-size: 1.3em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #4fc3f7, #81d4fa, #b3e5fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .info-panel p {
            font-size: 0.8em;
            line-height: 1.5;
            opacity: 0.85;
            margin-bottom: 12px;
        }

        .stats-panel {
            top: 20px;
            right: 20px;
            text-align: right;
        }

        .stats-panel .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
            font-size: 0.85em;
        }

        .stats-panel .stat-label {
            opacity: 0.7;
        }

        .stats-panel .stat-value {
            color: #4fc3f7;
            font-weight: bold;
        }

        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 12px;
        }

        .btn {
            padding: 8px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.8em;
            font-weight: 600;
            transition: all 0.3s ease;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b35, #ff8c42);
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.6);
        }

        .btn-bubble {
            background: linear-gradient(135deg, #4fc3f7, #29b6f6);
            box-shadow: 0 4px 15px rgba(79, 195, 247, 0.4);
        }

        .btn-bubble:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79, 195, 247, 0.6);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffd54f, #ffb300);
            box-shadow: 0 4px 15px rgba(255, 213, 79, 0.4);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 213, 79, 0.6);
        }

        .btn:active {
            transform: translateY(0px) scale(0.97);
        }

        .feed-hint {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 30, 60, 0.7);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 20px;
            padding: 8px 20px;
            color: #b3e5fc;
            font-size: 0.8em;
            z-index: 100;
            animation: pulse-hint 2s ease-in-out infinite;
        }

        @keyframes pulse-hint {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        @media (max-width: 768px) {
            .info-panel {
                max-width: 200px;
                padding: 10px 14px;
            }
            .info-panel h1 {
                font-size: 1em;
            }
            .info-panel p {
                font-size: 0.7em;
            }
            .btn {
                padding: 6px 10px;
                font-size: 0.7em;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="glass-panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>
            🖱️ ЛКМ — вращение камеры<br>
            🖱️ ПКМ — панорамирование<br>
            ⚙️ Колесо — зум<br>
            👆 Клик по воде — кормить рыб
        </p>
        <div class="btn-group">
            <button class="btn btn-fish" id="btnAddFish">🐟 Добавить рыбку</button>
            <button class="btn btn-bubble" id="btnAddBubble">💨 Больше пузырей</button>
            <button class="btn btn-light" id="btnLight">💡 Свет вкл/выкл</button>
        </div>
    </div>

    <div class="glass-panel stats-panel">
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

    <div class="feed-hint">💡 Кликните по аквариуму чтобы покормить рыбок!</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // ==================== SCENE SETUP ====================
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a1628);
        scene.fog = new THREE.FogExp2(0x1a3a5c, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(20, 18, 30);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 5, 0);

        // ==================== LIGHTING ====================
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xfff8e1, 0.8);
        directionalLight.position.set(15, 30, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 1;
        directionalLight.shadow.camera.far = 80;
        directionalLight.shadow.camera.left = -30;
        directionalLight.shadow.camera.right = 30;
        directionalLight.shadow.camera.top = 30;
        directionalLight.shadow.camera.bottom = -30;
        directionalLight.shadow.bias = -0.001;
        scene.add(directionalLight);

        const pointLight1 = new THREE.PointLight(0x4fc3f7, 0.6, 40);
        pointLight1.position.set(-10, 15, -8);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2962ff, 0.4, 35);
        pointLight2.position.set(12, 12, 10);
        scene.add(pointLight2);

        let lightOn = true;

        // ==================== AQUARIUM ====================
        const AQUARIUM = { width: 36, height: 24, depth: 20 };

        // Glass container
        const glassMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x88ccff,
            transparent: true,
            opacity: 0.15,
            transmission: 0.95,
            roughness: 0.05,
            metalness: 0,
            side: THREE.DoubleSide
        });

        const glassGeometry = new THREE.BoxGeometry(AQUARIUM.width, AQUARIUM.height, AQUARIUM.depth);
        const glassMesh = new THREE.Mesh(glassGeometry, glassMaterial);
        glassMesh.position.set(0, AQUARIUM.height / 2, 0);
        scene.add(glassMesh);

        // Wireframe edges
        const wireframeGeo = new THREE.EdgesGeometry(glassGeometry);
        const wireframeMat = new THREE.LineBasicMaterial({ color: 0x4fc3f7, transparent: true, opacity: 0.5 });
        const wireframe = new THREE.LineSegments(wireframeGeo, wireframeMat);
        wireframe.position.copy(glassMesh.position);
        scene.add(wireframe);

        // Sand floor
        const sandGeometry = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth, 32, 32);
        const positions = sandGeometry.attributes.position;
        for (let i = 0; i < positions.count; i++) {
            positions.setZ(i, Math.random() * 0.3 - 0.15);
        }
        sandGeometry.computeVertexNormals();

        const sandMaterial = new THREE.MeshStandardMaterial({
            color: 0xc2b280,
            roughness: 0.9,
            metalness: 0.1
        });
        const sandFloor = new THREE.Mesh(sandGeometry, sandMaterial);
        sandFloor.rotation.x = -Math.PI / 2;
        sandFloor.position.y = 0.1;
        sandFloor.receiveShadow = true;
        scene.add(sandFloor);

        // Rocks
        const rocks = [];
        for (let i = 0; i < 8; i++) {
            const rockGeo = new THREE.DodecahedronGeometry(1 + Math.random() * 1.5, 1);
            const posAttr = rockGeo.attributes.position;
            for (let j = 0; j < posAttr.count; j++) {
                posAttr.setX(j, posAttr.getX(j) * (0.7 + Math.random() * 0.6));
                posAttr.setY(j, posAttr.getY(j) * (0.5 + Math.random() * 0.4));
                posAttr.setZ(j, posAttr.getZ(j) * (0.7 + Math.random() * 0.6));
            }
            rockGeo.computeVertexNormals();

            const rockMat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.3, 0.35 + Math.random() * 0.15),
                roughness: 0.85,
                metalness: 0.05
            });
            const rock = new THREE.Mesh(rockGeo, rockMat);
            rock.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 6),
                1 + Math.random() * 1.5,
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.castShadow = true;
            rock.receiveShadow = true;
            scene.add(rock);
            rocks.push(rock);
        }

        // Seaweed
        const seaweeds = [];
        const seaweedColors = [0x2e7d32, 0x388e3c, 0x43a047, 0x1b5e20, 0x4caf50, 0x66bb6a];

        for (let i = 0; i < 12; i++) {
            const height = 4 + Math.random() * 8;
            const baseX = (Math.random() - 0.5) * (AQUARIUM.width - 4);
            const baseZ = (Math.random() - 0.5) * (AQUARIUM.depth - 4);

            const points = [];
            const segments = 8;
            for (let j = 0; j <= segments; j++) {
                const t = j / segments;
                points.push(new THREE.Vector3(
                    Math.sin(t * Math.PI * 1.5) * 0.5,
                    t * height,
                    Math.cos(t * Math.PI * 1.2) * 0.3
                ));
            }

            const curve = new THREE.CatmullRomCurve3(points);
            const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.15 + Math.random() * 0.15, 6, false);
            const tubeMat = new THREE.MeshStandardMaterial({
                color: seaweedColors[Math.floor(Math.random() * seaweedColors.length)],
                roughness: 0.7,
                metalness: 0.0,
                side: THREE.DoubleSide
            });
            const seaweed = new THREE.Mesh(tubeGeo, tubeMat);
            seaweed.position.set(baseX, 0.2, baseZ);
            seaweed.castShadow = true;
            seaweed.userData.baseHeight = height;
            seaweed.userData.phaseOffset = Math.random() * Math.PI * 2;
            seaweed.userData.swaySpeed = 0.5 + Math.random() * 0.8;
            scene.add(seaweed);
            seaweeds.push(seaweed);
        }

        // ==================== FISH SYSTEM ====================
        const fishArray = [];
        const colorSchemes = [
            { body: 0xff6b35, fin: 0xff8c42 },   // оранжевая
            { body: 0x1565c0, fin: 0x42a5f5 },   // синяя
            { body: 0xffeb3b, fin: 0xff5722 },   // желто-красная
            { body: 0x7b1fa2, fin: 0xba68c8 },   // фиолетовая
            { body: 0xc62828, fin: 0xef5350 },   // красная
            { body: 0x2e7d32, fin: 0x66bb6a },   // зеленая
            { body: 0xd81b60, fin: 0xf48fb1 },   // розовая
            { body: 0xf9a825, fin: 0xffd54f }    // золотая
        ];

        function createFish(position) {
            const fishGroup = new THREE.Group();
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;

            // Body - elongated sphere
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.4, 0.7, 0.5);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.4,
                metalness: 0.2,
                envMapIntensity: 0.5
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            fishGroup.add(body);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.1,
                side: THREE.DoubleSide
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.6, 0, 0);
            tail.castShadow = true;
            fishGroup.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 6);
            topFinGeo.rotateZ(-Math.PI / 2);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                side: THREE.DoubleSide
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0.2, 0.6, 0);
            fishGroup.add(topFin);

            // Left fin
            const leftFinGeo = new THREE.ConeGeometry(0.25, 0.7, 6);
            leftFinGeo.rotateX(Math.PI / 2);
            const leftFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                side: THREE.DoubleSide
            });
            const leftFin = new THREE.Mesh(leftFinGeo, leftFinMat);
            leftFin.position.set(0.2, -0.1, 0.5);
            fishGroup.add(leftFin);

            // Right fin
            const rightFin = new THREE.Mesh(leftFinGeo.clone(), leftFinMat.clone());
            rightFin.position.set(0.2, -0.1, -0.5);
            fishGroup.add(rightFin);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.08, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
            eyeL.position.set(1.1, 0.15, 0.25);
            fishGroup.add(eyeL);

            const pupilL = new THREE.Mesh(pupilGeo, pupilMat);
            pupilL.position.set(1.2, 0.15, 0.25);
            fishGroup.add(pupilL);

            const eyeR = new THREE.Mesh(eyeGeo.clone(), eyeMat.clone());
            eyeR.position.set(1.1, 0.15, -0.25);
            fishGroup.add(eyeR);

            const pupilR = new THREE.Mesh(pupilGeo.clone(), pupilMat.clone());
            pupilR.position.set(1.2, 0.15, -0.25);
            fishGroup.add(pupilR);

            fishGroup.position.copy(position);
            fishGroup.scale.setScalar(scale);
            scene.add(fishGroup);

            const fishData = {
                mesh: fishGroup,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                topFin: topFin,
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 2,
                    (Math.random() - 0.5) * 1,
                    (Math.random() - 0.5) * 2
                ),
                speed: 1.5 + Math.random() * 2.5,
                tailSpeed: 3 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2 + Math.random() * 1.5,
                wanderTimer: Math.random() * 3,
                scale: scale
            };

            fishArray.push(fishData);
            return fishData;
        }

        // Create initial fish
        for (let i = 0; i < 15; i++) {
            const pos = new THREE.Vector3(
                (Math.random() - 0.5) * (AQUARIUM.width - 8),
                4 + Math.random() * (AQUARIUM.height - 10),
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            createFish(pos);
        }

        // ==================== BUBBLES ====================
        const bubbles = [];

        function createBubble(position) {
            const size = 0.15 + Math.random() * 0.35;
            const bubbleGeo = new THREE.SphereGeometry(size, 12, 12);
            const bubbleMat = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3,
                transmission: 0.9,
                roughness: 0.1,
                metalness: 0,
                clearcoat: 1.0,
                clearcoatRoughness: 0.1
            });
            const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
            bubble.position.copy(position || new THREE.Vector3(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                1 + Math.random() * 3,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            ));
            bubble.userData.speed = 0.8 + Math.random() * 1.5;
            bubble.userData.wobblePhase = Math.random() * Math.PI * 2;
            bubble.userData.wobbleSpeed = 1 + Math.random() * 2;
            bubble.userData.wobbleAmp = 0.3 + Math.random() * 0.5;
            scene.add(bubble);
            bubbles.push(bubble);
            return bubble;
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // ==================== FOOD SYSTEM ====================
        const foods = [];

        function createFood(position) {
            const foodGeo = new THREE.SphereGeometry(0.25, 8, 8);
            const foodMat = new THREE.MeshStandardMaterial({
                color: 0x8d6e63,
                roughness: 0.8
            });
            const food = new THREE.Mesh(foodGeo, foodMat);
            food.position.copy(position);
            food.userData.velocityY = 0;
            food.userData.lifetime = 0;
            scene.add(food);
            foods.push(food);
            return food;
        }

        // ==================== RAYCASTER FOR FEEDING ====================
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function onMouseClick(event) {
            if (event.target.tagName === 'BUTTON') return;

            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            const intersects = raycaster.intersectObject(glassMesh);
            if (intersects.length > 0) {
                const point = intersects[0].point.clone();
                point.y = Math.min(point.y, AQUARIUM.height - 2);
                point.y = Math.max(point.y, 3);
                point.x = Math.max(Math.min(point.x, AQUARIUM.width / 2 - 1), -AQUARIUM.width / 2 + 1);
                point.z = Math.max(Math.min(point.z, AQUARIUM.depth / 2 - 1), -AQUARIUM.depth / 2 + 1);
                createFood(point);
            }
        }

        renderer.domElement.addEventListener('click', onMouseClick);

        // ==================== UI BUTTONS ====================
        document.getElementById('btnAddFish').addEventListener('click', () => {
            const pos = new THREE.Vector3(
                (Math.random() - 0.5) * (AQUARIUM.width - 8),
                4 + Math.random() * (AQUARIUM.height - 10),
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            createFish(pos);
        });

        document.getElementById('btnAddBubble').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
        });

        document.getElementById('btnLight').addEventListener('click', () => {
            lightOn = !lightOn;
            directionalLight.intensity = lightOn ? 0.8 : 0.1;
            ambientLight.intensity = lightOn ? 0.4 : 0.15;
        });

        // ==================== ANIMATION LOOP ====================
        let lastTime = performance.now();
        let frameCount = 0;
        let fpsTime = 0;
        let currentFPS = 60;

        function animate() {
            requestAnimationFrame(animate);

            const now = performance.now();
            const delta = Math.min((now - lastTime) / 1000, 0.05);
            lastTime = now;

            // FPS counter
            frameCount++;
            fpsTime += delta;
            if (fpsTime >= 0.5) {
                currentFPS = Math.round(frameCount / fpsTime);
                frameCount = 0;
                fpsTime = 0;
                document.getElementById('fpsCounter').textContent = currentFPS;
            }

            const time = now * 0.001;

            // ---- FISH BEHAVIOR ----
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;
                const vel = fish.velocity;

                // Wandering - periodically change direction
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.wanderTimer = 2 + Math.random() * 4;
                    vel.x += (Math.random() - 0.5) * 3;
                    vel.y += (Math.random() - 0.5) * 1.5;
                    vel.z += (Math.random() - 0.5) * 3;
                }

                // Food chasing
                fish.targetFood = null;
                let closestFoodDist = 15;
                for (let f = 0; f < foods.length; f++) {
                    const food = foods[f];
                    const dist = pos.distanceTo(food.position);
                    if (dist < closestFoodDist) {
                        closestFoodDist = dist;
                        fish.targetFood = food;
                    }
                }

                if (fish.targetFood) {
                    const dir = new THREE.Vector3().subVectors(fish.targetFood.position, pos).normalize();
                    vel.x += dir.x * 4 * delta;
                    vel.y += dir.y * 3 * delta;
                    vel.z += dir.z * 4 * delta;

                    // Eat food
                    if (closestFoodDist < 1.0) {
                        scene.remove(fish.targetFood);
                        foods.splice(foods.indexOf(fish.targetFood), 1);
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                        fish.targetFood = null;
                    }
                }

                // Collision avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const repel = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        const force = (fish.avoidanceRadius - dist) * 2;
                        vel.x += repel.x * force * delta;
                        vel.y += repel.y * force * delta;
                        vel.z += repel.z * force * delta;
                    }
                }

                // Wall reflection (soft bounce)
                const hw = AQUARIUM.width / 2 - 2;
                const hh = AQUARIUM.height / 2 - 2;
                const hd = AQUARIUM.depth / 2 - 2;

                if (pos.x > hw) vel.x -= (pos.x - hw) * 2 * delta;
                if (pos.x < -hw) vel.x -= (pos.x + hw) * 2 * delta;
                if (pos.y > hh + 5) vel.y -= (pos.y - hh - 5) * 2 * delta;
                if (pos.y < 2) vel.y -= (pos.y - 2) * 2 * delta;
                if (pos.z > hd) vel.z -= (pos.z - hd) * 2 * delta;
                if (pos.z < -hd) vel.z -= (pos.z + hd) * 2 * delta;

                // Speed limiting
                const speedMag = vel.length();
                if (speedMag > fish.speed) {
                    vel.normalize().multiplyScalar(fish.speed);
                }

                // Apply velocity
                pos.x += vel.x * delta;
                pos.y += vel.y * delta;
                pos.z += vel.z * delta;

                // Clamp position
                pos.x = Math.max(Math.min(pos.x, hw), -hw);
                pos.y = Math.max(Math.min(pos.y, hh + 5), 2);
                pos.z = Math.max(Math.min(pos.z, hd), -hd);

                // Rotate fish to face velocity direction
                if (speedMag > 0.1) {
                    const targetAngle = Math.atan2(vel.z, vel.x);
                    const currentAngle = fish.mesh.rotation.y;
                    let angleDiff = targetAngle - currentAngle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                    fish.mesh.rotation.y += angleDiff * 3 * delta;

                    // Slight vertical tilt based on vertical velocity
                    fish.mesh.rotation.z = Math.max(-0.4, Math.min(0.4, -vel.y * 0.15));
                }

                // Tail animation
                const tailAngle = Math.sin(time * fish.tailSpeed + fish.phase) * 0.5;
                fish.tail.rotation.y = tailAngle;

                // Fin animations
                const finAngle = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase + 1) * 0.3;
                fish.leftFin.rotation.x = finAngle;
                fish.rightFin.rotation.x = -finAngle;
                fish.topFin.rotation.z = Math.sin(time * fish.tailSpeed * 0.5 + fish.phase + 2) * 0.2;

                // Slight body undulation
                fish.mesh.position.y += Math.sin(time * 2 + fish.phase) * 0.01;
            }

            // ---- BUBBLES ----
            for (let i = bubbles.length - 1; i >= 0; i--) {
                const bubble = bubbles[i];
                bubble.position.y += bubble.userData.speed * delta;

                // Wobble
                const wobbleT = time * bubble.userData.wobbleSpeed + bubble.userData.wobblePhase;
                bubble.position.x += Math.sin(wobbleT) * bubble.userData.wobbleAmp * delta;
                bubble.position.z += Math.cos(wobbleT * 0.7) * bubble.userData.wobbleAmp * delta * 0.5;

                // Reset at top
                if (bubble.position.y > AQUARIUM.height - 1) {
                    bubble.position.set(
                        (Math.random() - 0.5) * (AQUARIUM.width - 4),
                        1 + Math.random() * 2,
                        (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                    );
                }
            }

            // ---- FOOD PHYSICS ----
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                food.userData.velocityY -= 3 * delta;
                food.position.y += food.userData.velocityY * delta;
                food.userData.lifetime += delta;

                // Slight horizontal drift
                food.position.x += Math.sin(time * 2 + i) * 0.3 * delta;
                food.position.z += Math.cos(time * 1.5 + i) * 0.2 * delta;

                // Remove at bottom or after too long
                if (food.position.y < 0.5 || food.userData.lifetime > 15) {
                    scene.remove(food);
                    foods.splice(i, 1);
                }
            }

            // ---- SEAWEED ANIMATION ----
            for (let i = 0; i < seaweeds.length; i++) {
                const sw = seaweeds[i];
                const swayX = Math.sin(time * sw.userData.swaySpeed + sw.userData.phaseOffset) * 0.06;
                const swayZ = Math.cos(time * sw.userData.swaySpeed * 0.7 + sw.userData.phaseOffset + 1) * 0.04;
                sw.rotation.x = swayX;
                sw.rotation.z = swayZ;
            }

            // ---- UPDATE UI ----
            document.getElementById('fishCount').textContent = fishArray.length;
            document.getElementById('bubbleCount').textContent = bubbles.length;
            document.getElementById('foodCount').textContent = foods.length;

            controls.update();
            renderer.render(scene, camera);
        }

        animate();

        // ==================== RESIZE HANDLER ====================
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```

Этот файл представляет собой полностью функциональный 3D аквариум со всеми запрошенными функциями:

**Что реализовано:**

| Функция | Описание |
|---------|----------|
| 🐠 15 рыбок | Детализированные модели с телом, хвостом, плавниками, глазами и зрачками |
| 🧠 ИИ | Избегание столкновений, отражение от стен, блуждание, преследование корма, рост |
| 🌊 Окружение | Стеклянный контейнер с transmission, песчаное дно с неровностями, 8 камней, 12 водорослей |
| 💭 Пузыри | 30 пузырей с glass-материалом и покачиванием |
| 🍽️ Кормление | Клик создаёт корм с гравитацией, рыбки его находят и съедают |
| 💡 Освещение | Ambient + Directional (с тенями) + 2 PointLight, переключение кнопкой |
| 🎮 Камера | OrbitControls с damping, ограничениями зума и угла |
| 🖥️ UI | Стеклянные панели, статистика, кнопки управления, FPS-счётчик |
| 🎨 Эффекты | FogExp2, ACES tone mapping, PCFSoftShadowMap, glow-кнопки |