

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
            background: linear-gradient(180deg, #0a1628 0%, #1a3a5c 50%, #0d2847 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            background: linear-gradient(135deg, #64b5f6, #42a5f5, #1e88e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
            text-shadow: 0 0 30px rgba(100, 181, 246, 0.3);
        }

        #info-panel p {
            color: rgba(180, 220, 255, 0.8);
            font-size: 0.82em;
            line-height: 1.6;
            margin-bottom: 8px;
        }

        .btn {
            display: inline-block;
            padding: 10px 18px;
            margin: 4px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(135deg, #1565c0, #0d47a1);
            color: #e3f2fd;
            font-size: 0.85em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(21, 101, 192, 0.3);
            font-weight: 500;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(21, 101, 192, 0.5), 0 0 15px rgba(100, 181, 246, 0.2);
            background: linear-gradient(135deg, #1976d2, #1565c0);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn.active {
            background: linear-gradient(135deg, #42a5f5, #1e88e5);
            box-shadow: 0 4px 20px rgba(66, 165, 245, 0.5);
        }

        #stats-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
            text-align: right;
        }

        #stats-panel .stat {
            color: #64b5f6;
            font-size: 0.9em;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
        }

        #stats-panel .stat-value {
            color: #fff;
            font-weight: bold;
            font-size: 1.1em;
        }

        .stat-icon {
            font-size: 1.1em;
        }

        #food-hint {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(180, 220, 255, 0.7);
            font-size: 0.9em;
            z-index: 100;
            animation: pulse 2s infinite;
            pointer-events: none;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
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
            #info-panel p {
                font-size: 0.75em;
            }
            .btn {
                padding: 8px 12px;
                font-size: 0.75em;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="info-panel" class="glass-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>🖱️ Левый клик — вращение</p>
        <p>🖱️ Правый клик — панорама</p>
        <p>🖱️ Колесо — масштаб</p>
        <p>🍽️ Клик по воде — корм</p>
        <div style="margin-top: 12px;">
            <button class="btn" id="btn-add-fish">🐟 Добавить рыбку</button>
            <button class="btn" id="btn-add-bubbles">💭 Пузыри</button>
            <button class="btn" id="btn-light">💡 Свет</button>
        </div>
    </div>

    <div id="stats-panel" class="glass-panel">
        <div class="stat">
            <span class="stat-icon">🐟</span>
            <span>Рыбки:</span>
            <span class="stat-value" id="fish-count">15</span>
        </div>
        <div class="stat">
            <span class="stat-icon">🍽️</span>
            <span>Корм:</span>
            <span class="stat-value" id="food-count">0</span>
        </div>
        <div class="stat">
            <span class="stat-icon">⚡</span>
            <span>FPS:</span>
            <span class="stat-value" id="fps-counter">60</span>
        </div>
    </div>

    <div id="food-hint">💡 Кликните по аквариуму, чтобы покормить рыбок</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // ==================== SCENE SETUP ====================
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a1e3d, 0.012);

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

        // ==================== CONTROLS ====================
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 2, 0);

        // ==================== AQUARIUM DIMENSIONS ====================
        const AQUARIUM = { width: 36, height: 24, depth: 20 };
        const HALF = { x: AQUARIUM.width / 2, y: AQUARIUM.height / 2, z: AQUARIUM.depth / 2 };

        // ==================== LIGHTING ====================
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffeedd, 0.8);
        directionalLight.position.set(15, 30, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 80;
        directionalLight.shadow.camera.left = -25;
        directionalLight.shadow.camera.right = 25;
        directionalLight.shadow.camera.top = 20;
        directionalLight.shadow.camera.bottom = -20;
        directionalLight.shadow.bias = -0.001;
        scene.add(directionalLight);

        const pointLight1 = new THREE.PointLight(0x4fc3f7, 0.6, 40);
        pointLight1.position.set(-10, 10, -5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x1565c0, 0.4, 35);
        pointLight2.position.set(10, 5, 8);
        scene.add(pointLight2);

        let lightOn = true;

        // ==================== AQUARIUM GLASS ====================
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

        // Glass edges
        const edgesGeometry = new THREE.EdgesGeometry(glassGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x4fc3f7, transparent: true, opacity: 0.4 });
        const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        edges.position.y = HALF.y;
        scene.add(edges);

        // ==================== SANDY BOTTOM ====================
        const sandGeometry = new THREE.PlaneGeometry(AQUARIUM.width - 1, AQUARIUM.depth - 1, 40, 40);
        const sandVertices = sandGeometry.attributes.position;
        for (let i = 0; i < sandVertices.count; i++) {
            sandVertices.setZ(i, (Math.random() * 0.3 - 0.15));
        }
        sandGeometry.computeVertexNormals();
        const sandMaterial = new THREE.MeshStandardMaterial({
            color: 0xd4a76a,
            roughness: 0.9,
            metalness: 0.05
        });
        const sand = new THREE.Mesh(sandGeometry, sandMaterial);
        sand.rotation.x = -Math.PI / 2;
        sand.position.y = 0.1;
        sand.receiveShadow = true;
        scene.add(sand);

        // ==================== ROCKS ====================
        const rocks = [];
        for (let i = 0; i < 8; i++) {
            const rockGeom = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.2, 1);
            const rockVertices = rockGeom.attributes.position;
            for (let j = 0; j < rockVertices.count; j++) {
                rockVertices.setX(j, rockVertices.getX(j) * (0.7 + Math.random() * 0.6));
                rockVertices.setY(j, rockVertices.getY(j) * (0.5 + Math.random() * 0.5));
                rockVertices.setZ(j, rockVertices.getZ(j) * (0.7 + Math.random() * 0.6));
            }
            rockGeom.computeVertexNormals();
            const rockMat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.2, 0.25 + Math.random() * 0.15),
                roughness: 0.85,
                metalness: 0.05
            });
            const rock = new THREE.Mesh(rockGeom, rockMat);
            rock.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 6),
                0.5 + Math.random() * 0.5,
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.castShadow = true;
            rock.receiveShadow = true;
            scene.add(rock);
            rocks.push(rock);
        }

        // ==================== SEAWEED ====================
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
            const tubeGeom = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.1, 6, false);
            const hue = 0.25 + Math.random() * 0.15;
            const tubeMat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(hue, 0.7, 0.3 + Math.random() * 0.15),
                roughness: 0.7,
                metalness: 0.05,
                side: THREE.DoubleSide
            });
            const seaweed = new THREE.Mesh(tubeGeom, tubeMat);
            seaweed.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                0,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            seaweed.castShadow = true;
            seaweed.userData = { phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 };
            scene.add(seaweed);
            seaweeds.push(seaweed);
        }

        // ==================== FISH CREATION ====================
        const colorSchemes = [
            { body: 0xff6600, fin: 0xff9933, belly: 0xffcc66, name: 'orange' },
            { body: 0x2266ff, fin: 0x4499ff, belly: 0x88ccff, name: 'blue' },
            { body: 0xffdd00, fin: 0xff4400, belly: 0xffee88, name: 'yellow-red' },
            { body: 0x8833cc, fin: 0xaa55ee, belly: 0xcc99ff, name: 'purple' },
            { body: 0xee2222, fin: 0xff5555, belly: 0xff9999, name: 'red' },
            { body: 0x22aa44, fin: 0x44cc66, belly: 0x88ee99, name: 'green' },
            { body: 0xff66aa, fin: 0xff88cc, belly: 0xffbbdd, name: 'pink' },
            { body: 0xddaa00, fin: 0xffcc33, belly: 0xffee99, name: 'gold' }
        ];

        const fishArray = [];

        function createFish(colorScheme, scale) {
            const group = new THREE.Group();

            // Body
            const bodyGeom = new THREE.SphereGeometry(1, 16, 12);
            bodyGeom.scale(1.5, 0.7, 0.5);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: colorScheme.body,
                roughness: 0.3,
                metalness: 0.2
            });
            const body = new THREE.Mesh(bodyGeom, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Belly
            const bellyGeom = new THREE.SphereGeometry(0.85, 12, 8);
            bellyGeom.scale(1.3, 0.5, 0.45);
            const bellyMat = new THREE.MeshStandardMaterial({
                color: colorScheme.belly,
                roughness: 0.4,
                metalness: 0.1
            });
            const belly = new THREE.Mesh(bellyGeom, bellyMat);
            belly.position.y = -0.15;
            group.add(belly);

            // Eyes
            const eyeGeom = new THREE.SphereGeometry(0.18, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1, metalness: 0.1 });
            const pupilGeom = new THREE.SphereGeometry(0.09, 6, 6);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeom, eyeMat);
            leftEye.position.set(1.0, 0.15, 0.3);
            group.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeom, pupilMat);
            leftPupil.position.set(1.12, 0.15, 0.32);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeom, eyeMat);
            rightEye.position.set(1.0, 0.15, -0.3);
            group.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeom, pupilMat);
            rightPupil.position.set(1.12, 0.15, -0.32);
            group.add(rightPupil);

            // Tail
            const tailGeom = new THREE.ConeGeometry(0.6, 1.2, 4);
            tailGeom.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                metalness: 0.1,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.85
            });
            const tail = new THREE.Mesh(tailGeom, tailMat);
            tail.position.set(-1.7, 0, 0);
            tail.scale.set(0.8, 1, 0.3);
            group.add(tail);

            // Dorsal fin (top)
            const dorsalGeom = new THREE.ConeGeometry(0.4, 0.8, 3);
            const dorsalMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.8
            });
            const dorsal = new THREE.Mesh(dorsalGeom, dorsalMat);
            dorsal.position.set(0.2, 0.65, 0);
            dorsal.scale.set(1.5, 1, 0.2);
            group.add(dorsal);

            // Left pectoral fin
            const finGeom = new THREE.ConeGeometry(0.35, 0.7, 3);
            const finMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.75
            });
            const leftFin = new THREE.Mesh(finGeom, finMat);
            leftFin.position.set(0.3, -0.1, 0.5);
            leftFin.rotation.x = Math.PI / 4;
            leftFin.scale.set(0.8, 1, 0.2);
            group.add(leftFin);

            // Right pectoral fin
            const rightFin = new THREE.Mesh(finGeom, finMat);
            rightFin.position.set(0.3, -0.1, -0.5);
            rightFin.rotation.x = -Math.PI / 4;
            rightFin.scale.set(0.8, 1, 0.2);
            group.add(rightFin);

            // Mouth
            const mouthGeom = new THREE.SphereGeometry(0.12, 6, 6);
            const mouthMat = new THREE.MeshStandardMaterial({ color: 0x331111 });
            const mouth = new THREE.Mesh(mouthGeom, mouthMat);
            mouth.position.set(1.45, -0.05, 0);
            group.add(mouth);

            group.scale.setScalar(scale);
            group.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 8),
                3 + Math.random() * (AQUARIUM.height - 8),
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );

            scene.add(group);

            const fish = {
                mesh: group,
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
                scale: scale,
                wanderTimer: Math.random() * 5,
                colorScheme: colorScheme
            };

            fishArray.push(fish);
            return fish;
        }

        // Create initial 15 fish
        for (let i = 0; i < 15; i++) {
            const scheme = colorSchemes[i % colorSchemes.length];
            const scale = 0.6 + Math.random() * 0.6;
            createFish(scheme, scale);
        }

        // ==================== BUBBLES ====================
        const bubbles = [];

        function createBubble(x, y, z) {
            const size = 0.15 + Math.random() * 0.35;
            const bubbleGeom = new THREE.SphereGeometry(size, 12, 12);
            const bubbleMat = new THREE.MeshPhysicalMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3,
                transmission: 0.9,
                roughness: 0.0,
                metalness: 0.0,
                clearcoat: 1.0
            });
            const bubble = new THREE.Mesh(bubbleGeom, bubbleMat);
            bubble.position.set(
                x !== undefined ? x : (Math.random() - 0.5) * (AQUARIUM.width - 4),
                y !== undefined ? y : Math.random() * (AQUARIUM.height - 4) + 1,
                z !== undefined ? z : (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            bubble.userData = {
                speed: 1 + Math.random() * 2,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 1 + Math.random() * 2,
                wobbleAmp: 0.3 + Math.random() * 0.5
            };
            scene.add(bubble);
            bubbles.push(bubble);
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // ==================== FOOD SYSTEM ====================
        const foods = [];
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function createFood(x, y, z) {
            const foodGeom = new THREE.SphereGeometry(0.25, 8, 8);
            const foodMat = new THREE.MeshStandardMaterial({
                color: 0xff8844,
                roughness: 0.6,
                emissive: 0x441100,
                emissiveIntensity: 0.3
            });
            const food = new THREE.Mesh(foodGeom, foodMat);
            food.position.set(x, y, z);
            food.userData = {
                velocity: new THREE.Vector3(
                    (Math.random() - 0.5) * 0.5,
                    0,
                    (Math.random() - 0.5) * 0.5
                ),
                gravity: -2.5,
                life: 15
            };
            scene.add(food);
            foods.push(food);
        }

        // Click to feed
        renderer.domElement.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObject(glassBox);

            if (intersects.length > 0) {
                const point = intersects[0].point;
                const foodX = Math.max(-HALF.x + 2, Math.min(HALF.x - 2, point.x));
                const foodY = Math.min(AQUARIUM.height - 2, point.y);
                const foodZ = Math.max(-HALF.z + 2, Math.min(HALF.z - 2, point.z));
                createFood(foodX, foodY, foodZ);
            } else {
                // Create food at random position near top
                createFood(
                    (Math.random() - 0.5) * (AQUARIUM.width - 6),
                    AQUARIUM.height - 3,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                );
            }
        });

        // ==================== UI BUTTONS ====================
        document.getElementById('btn-add-fish').addEventListener('click', () => {
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;
            createFish(scheme, scale);
            document.getElementById('fish-count').textContent = fishArray.length;
        });

        document.getElementById('btn-add-bubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
        });

        document.getElementById('btn-light').addEventListener('click', function () {
            lightOn = !lightOn;
            directionalLight.intensity = lightOn ? 0.8 : 0.1;
            this.classList.toggle('active', lightOn);
        });

        // ==================== ANIMATION LOOP ====================
        let lastTime = performance.now();
        let frameCount = 0;
        let fpsTime = 0;

        function animate(currentTime) {
            requestAnimationFrame(animate);

            const deltaTime = Math.min((currentTime - lastTime) / 1000, 0.05);
            lastTime = currentTime;

            // FPS counter
            frameCount++;
            fpsTime += deltaTime;
            if (fpsTime >= 1) {
                document.getElementById('fps-counter').textContent = frameCount;
                frameCount = 0;
                fpsTime = 0;
            }

            // Update fish
            updateFish(deltaTime);

            // Update bubbles
            updateBubbles(deltaTime);

            // Update food
            updateFood(deltaTime);

            // Update seaweed
            updateSeaweed(currentTime);

            // Update lights animation
            pointLight1.intensity = 0.5 + Math.sin(currentTime * 0.001) * 0.15;
            pointLight2.intensity = 0.35 + Math.cos(currentTime * 0.0008) * 0.1;

            controls.update();
            renderer.render(scene, camera);
        }

        function updateFish(dt) {
            const time = performance.now() * 0.001;

            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;
                const vel = fish.velocity;

                // Wandering behavior
                fish.wanderTimer -= dt;
                if (fish.wanderTimer <= 0) {
                    fish.wanderTimer = 2 + Math.random() * 4;
                    vel.x += (Math.random() - 0.5) * 2;
                    vel.y += (Math.random() - 0.5) * 1;
                    vel.z += (Math.random() - 0.5) * 2;
                }

                // Food seeking
                fish.targetFood = null;
                let closestDist = 15;
                for (let f = 0; f < foods.length; f++) {
                    const dist = pos.distanceTo(foods[f].position);
                    if (dist < closestDist) {
                        closestDist = dist;
                        fish.targetFood = foods[f];
                    }
                }

                if (fish.targetFood) {
                    const dir = new THREE.Vector3().subVectors(fish.targetFood.position, pos).normalize();
                    vel.x += dir.x * 8 * dt;
                    vel.y += dir.y * 8 * dt;
                    vel.z += dir.z * 8 * dt;

                    // Eat food
                    if (closestDist < 1.5) {
                        scene.remove(fish.targetFood);
                        foods.splice(foods.indexOf(fish.targetFood), 1);
                        // Growth
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                        fish.targetFood = null;
                    }
                }

                // Avoidance from other fish
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const push = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        push.multiplyScalar((fish.avoidanceRadius - dist) * 3 * dt);
                        vel.add(push);
                    }
                }

                // Wall avoidance (soft boundary)
                const margin = 3;
                if (pos.x > HALF.x - margin) vel.x -= (pos.x - (HALF.x - margin)) * 2 * dt;
                if (pos.x < -HALF.x + margin) vel.x += ((-HALF.x + margin) - pos.x) * 2 * dt;
                if (pos.y > AQUARIUM.height - margin) vel.y -= (pos.y - (AQUARIUM.height - margin)) * 2 * dt;
                if (pos.y < 2) vel.y += (2 - pos.y) * 2 * dt;
                if (pos.z > HALF.z - margin) vel.z -= (pos.z - (HALF.z - margin)) * 2 * dt;
                if (pos.z < -HALF.z + margin) vel.z += ((-HALF.z + margin) - pos.z) * 2 * dt;

                // Damping
                vel.multiplyScalar(0.98);

                // Speed limit
                const currentSpeed = vel.length();
                if (currentSpeed > fish.speed) {
                    vel.normalize().multiplyScalar(fish.speed);
                }

                // Update position
                pos.add(vel.clone().multiplyScalar(dt));

                // Hard boundary clamp
                pos.x = Math.max(-HALF.x + 1, Math.min(HALF.x - 1, pos.x));
                pos.y = Math.max(1, Math.min(AQUARIUM.height - 1, pos.y));
                pos.z = Math.max(-HALF.z + 1, Math.min(HALF.z - 1, pos.z));

                // Rotate to face direction
                if (vel.length() > 0.1) {
                    const targetAngle = Math.atan2(-vel.z, vel.x);
                    const currentAngle = fish.mesh.rotation.y;
                    let diff = targetAngle - currentAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    fish.mesh.rotation.y += diff * 3 * dt;

                    // Slight pitch based on vertical velocity
                    const targetPitch = Math.atan2(vel.y, Math.sqrt(vel.x * vel.x + vel.z * vel.z)) * 0.3;
                    fish.mesh.rotation.z += (targetPitch - fish.mesh.rotation.z) * 2 * dt;
                }

                // Tail animation
                fish.phase += dt * fish.tailSpeed;
                fish.tail.rotation.y = Math.sin(fish.phase) * 0.6;

                // Fin animation
                fish.leftFin.rotation.x = Math.PI / 4 + Math.sin(fish.phase * 1.5) * 0.3;
                fish.rightFin.rotation.x = -Math.PI / 4 - Math.sin(fish.phase * 1.5) * 0.3;
            }
        }

        function updateBubbles(dt) {
            const time = performance.now() * 0.001;
            for (let i = 0; i < bubbles.length; i++) {
                const b = bubbles[i];
                const data = b.userData;

                b.position.y += data.speed * dt;
                b.position.x += Math.sin(time * data.wobbleSpeed + data.wobblePhase) * data.wobbleAmp * dt;
                b.position.z += Math.cos(time * data.wobbleSpeed * 0.7 + data.wobblePhase) * data.wobbleAmp * 0.5 * dt;

                // Reset at top
                if (b.position.y > AQUARIUM.height - 1) {
                    b.position.y = 1;
                    b.position.x = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                    b.position.z = (Math.random() - 0.5) * (AQUARIUM.depth - 4);
                }
            }
        }

        function updateFood(dt) {
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                const data = food.userData;

                data.velocity.y += data.gravity * dt;
                food.position.add(data.velocity.clone().multiplyScalar(dt));

                // Slight horizontal drift
                food.position.x += Math.sin(performance.now() * 0.002 + i) * 0.3 * dt;
                food.position.z += Math.cos(performance.now() * 0.0015 + i) * 0.3 * dt;

                // Remove if hits bottom or expires
                data.life -= dt;
                if (food.position.y < 0.5 || data.life <= 0) {
                    scene.remove(food);
                    foods.splice(i, 1);
                }
            }
            document.getElementById('food-count').textContent = foods.length;
        }

        function updateSeaweed(time) {
            for (let i = 0; i < seaweeds.length; i++) {
                const sw = seaweeds[i];
                const data = sw.userData;
                sw.rotation.x = Math.sin(time * 0.001 * data.speed + data.phase) * 0.08;
                sw.rotation.z = Math.cos(time * 0.0008 * data.speed + data.phase) * 0.06;
            }
        }

        // ==================== WINDOW RESIZE ====================
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // ==================== START ====================
        animate(performance.now());

        // Hide hint after 8 seconds
        setTimeout(() => {
            document.getElementById('food-hint').style.opacity = '0';
            document.getElementById('food-hint').style.transition = 'opacity 1s';
        }, 8000);
    </script>
</body>
</html>
```

## Что реализовано:

### 🐠 Рыбки (15 штук)
- **Анатомия**: тело (сфера), глаза с зрачками, хвост (конус), dorsal fin, боковые плавники, рот
- **8 цветовых схем**: оранжевая, синяя, жёлто-красная, фиолетовая, красная, зелёная, розовая, золотая
- **Анимация**: махание хвостом, движение плавников, поворот по направлению движения

### 🧠 ИИ поведения
- **Избегание столкновений** — рыбки отталкиваются друг от друга
- **Отражение от стен** — мягкое отталкивание у границ
- **Случайное блуждание** — периодическое изменение траектории
- **Преследование корма** — радиус обнаружения 15 единиц
- **Рост** — +5% размера после поедания

### 🌊 Окружение
- Стеклянный контейнер (36×24×20) с `transmission: 0.95`
- Песчаное дно с процедурными неровностями
- 8 деформированных камней
- 12 кустов водорослей (TubeGeometry + CatmullRomCurve3)

### 💭 Пузыри (30 шт)
- Прозрачные сферы с `MeshPhysicalMaterial`
- Движение вверх с покачиванием, сброс у поверхности

### 🍽️ Кормление
- Клик по аквариуму создаёт корм с гравитацией
- Рыбки преследуют и съедают корм

### 🎮 Управление
- OrbitControls с damping, ограничениями зума и угла
- Кнопки: добавить рыбку, пузыри, переключение света
- Статистика: рыбки, корм, FPS