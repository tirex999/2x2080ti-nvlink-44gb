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
            background: linear-gradient(180deg, #0a1628 0%, #0d2137 50%, #1a3a5c 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            background: rgba(10, 25, 50, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            z-index: 100;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        #info-panel {
            top: 20px;
            left: 20px;
            max-width: 280px;
        }

        #info-panel h1 {
            font-size: 22px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #4fc3f7, #81c784, #ffb74d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        #info-panel .instructions {
            font-size: 12px;
            line-height: 1.8;
            opacity: 0.85;
            margin-bottom: 15px;
        }

        #info-panel .instructions span {
            display: block;
            padding-left: 8px;
            border-left: 2px solid rgba(79, 195, 247, 0.4);
            margin-bottom: 4px;
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

        .btn::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s ease;
        }

        .btn:hover::after {
            left: 100%;
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b35, #ff9a56);
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.5);
        }

        .btn-bubbles {
            background: linear-gradient(135deg, #2196f3, #64b5f6);
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
        }

        .btn-bubbles:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(33, 150, 243, 0.5);
        }

        .btn-light {
            background: linear-gradient(135deg, #ffc107, #ffeb3b);
            box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
            color: #333;
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 193, 7, 0.5);
        }

        .btn-light.off {
            background: linear-gradient(135deg, #546e7a, #78909c);
            box-shadow: 0 4px 15px rgba(84, 110, 122, 0.3);
            color: #ccc;
        }

        #stats-panel {
            top: 20px;
            right: 20px;
            min-width: 160px;
        }

        #stats-panel h2 {
            font-size: 14px;
            margin-bottom: 10px;
            color: #4fc3f7;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 13px;
        }

        .stat-row:last-child {
            border-bottom: none;
        }

        .stat-label {
            opacity: 0.7;
        }

        .stat-value {
            font-weight: 700;
            color: #81c784;
        }

        #food-hint {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 25, 50, 0.6);
            backdrop-filter: blur(8px);
            padding: 10px 20px;
            border-radius: 20px;
            color: rgba(224, 240, 255, 0.7);
            font-size: 13px;
            z-index: 100;
            border: 1px solid rgba(100, 180, 255, 0.15);
            animation: pulse 2s ease-in-out infinite;
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
                font-size: 16px;
            }
            #info-panel .instructions {
                display: none;
            }
            #stats-panel {
                min-width: 120px;
                padding: 14px;
            }
            .btn {
                padding: 6px 10px;
                font-size: 11px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel" id="info-panel">
        <h1>🐠 3D Аквариум</h1>
        <div class="instructions">
            <span>🖱️ ЛКМ — вращение камеры</span>
            <span>🖱️ ПКМ — панорамирование</span>
            <span>🔄 Колесо — зум</span>
            <span>👆 Клик — бросить корм</span>
        </div>
        <div class="btn-group">
            <button class="btn btn-fish" id="btn-add-fish">+ Рыбка</button>
            <button class="btn btn-bubbles" id="btn-add-bubbles">+ Пузыри</button>
            <button class="btn btn-light" id="btn-toggle-light">☀️ Свет</button>
        </div>
    </div>

    <div class="panel" id="stats-panel">
        <h2>Статистика</h2>
        <div class="stat-row">
            <span class="stat-label">Рыбки</span>
            <span class="stat-value" id="stat-fish">15</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Пузыри</span>
            <span class="stat-value" id="stat-bubbles">30</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Корм</span>
            <span class="stat-value" id="stat-food">0</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">FPS</span>
            <span class="stat-value" id="stat-fps">60</span>
        </div>
    </div>

    <div id="food-hint">🍽️ Кликните по аквариуму, чтобы покормить рыбок</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === SCENE SETUP ===
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a1e3a, 0.008);
        scene.background = new THREE.Color(0x0a1628);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(30, 20, 35);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        // === CONTROLS ===
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 0, 0);

        // === LIGHTING ===
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 1.0);
        dirLight.position.set(15, 25, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 80;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 25;
        dirLight.shadow.camera.bottom = -25;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x4488ff, 0.6, 40);
        pointLight1.position.set(-10, 10, 5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2266cc, 0.4, 35);
        pointLight2.position.set(10, 5, -8);
        scene.add(pointLight2);

        // === AQUARIUM DIMENSIONS ===
        const AQUA_W = 36;
        const AQUA_H = 24;
        const AQUA_D = 20;
        const HALF_W = AQUA_W / 2;
        const HALF_H = AQUA_H / 2;
        const HALF_D = AQUA_D / 2;

        // === GLASS CONTAINER ===
        function createAquarium() {
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                metalness: 0.0,
                roughness: 0.05,
                transmission: 0.95,
                thickness: 0.5,
                transparent: true,
                opacity: 0.15,
                side: THREE.DoubleSide
            });

            const glassGeo = new THREE.BoxGeometry(AQUA_W, AQUA_H, AQUA_D);
            const glassMesh = new THREE.Mesh(glassGeo, glassMat);
            glassMesh.position.y = 0;
            scene.add(glassMesh);

            // Edges
            const edgesGeo = new THREE.EdgesGeometry(glassGeo);
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x4488aa, transparent: true, opacity: 0.5 });
            const edges = new THREE.LineSegments(edgesGeo, edgesMat);
            edges.position.y = 0;
            scene.add(edges);
        }
        createAquarium();

        // === SANDY BOTTOM ===
        function createSand() {
            const sandGeo = new THREE.PlaneGeometry(AQUA_W, AQUA_D, 32, 32);
            const positions = sandGeo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                positions.setZ(i, (Math.random() - 0.5) * 0.4);
            }
            sandGeo.computeVertexNormals();

            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xc2a66b,
                roughness: 0.95,
                metalness: 0.0
            });

            const sand = new THREE.Mesh(sandGeo, sandMat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = -HALF_H + 0.2;
            sand.receiveShadow = true;
            scene.add(sand);
        }
        createSand();

        // === ROCKS ===
        function createRocks() {
            for (let i = 0; i < 8; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const geo = new THREE.DodecahedronGeometry(size, 1);
                // Deform vertices
                const pos = geo.attributes.position;
                for (let j = 0; j < pos.count; j++) {
                    const x = pos.getX(j) * (0.7 + Math.random() * 0.6);
                    const y = pos.getY(j) * (0.6 + Math.random() * 0.5);
                    const z = pos.getZ(j) * (0.7 + Math.random() * 0.6);
                    pos.setXYZ(j, x, y, z);
                }
                geo.computeVertexNormals();

                const colors = [0x555555, 0x666666, 0x445566, 0x556677, 0x667788];
                const mat = new THREE.MeshStandardMaterial({
                    color: colors[Math.floor(Math.random() * colors.length)],
                    roughness: 0.85,
                    metalness: 0.1
                });

                const rock = new THREE.Mesh(geo, mat);
                rock.position.set(
                    (Math.random() - 0.5) * (AQUA_W - 6),
                    -HALF_H + size * 0.3,
                    (Math.random() - 0.5) * (AQUA_D - 6)
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
        function createSeaweed() {
            for (let i = 0; i < 12; i++) {
                const height = 3 + Math.random() * 5;
                const points = [];
                const segments = 6;
                for (let j = 0; j <= segments; j++) {
                    const t = j / segments;
                    points.push(new THREE.Vector3(
                        Math.sin(t * Math.PI * 2) * 0.3,
                        t * height,
                        Math.cos(t * Math.PI * 1.5) * 0.2
                    ));
                }
                const curve = new THREE.CatmullRomCurve3(points);
                const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.15 + Math.random() * 0.1, 5, false);

                const greenShades = [0x2d8a4e, 0x3a9d5c, 0x1e7a3e, 0x4aad6a, 0x2a8a50];
                const mat = new THREE.MeshStandardMaterial({
                    color: greenShades[Math.floor(Math.random() * greenShades.length)],
                    roughness: 0.7,
                    metalness: 0.0
                });

                const weed = new THREE.Mesh(tubeGeo, mat);
                weed.position.set(
                    (Math.random() - 0.5) * (AQUA_W - 8),
                    -HALF_H + 0.2,
                    (Math.random() - 0.5) * (AQUA_D - 8)
                );
                weed.castShadow = true;
                scene.add(weed);
                seaweeds.push({ mesh: weed, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 });
            }
        }
        createSeaweed();

        // === FISH SYSTEM ===
        const fishArray = [];
        const foodArray = [];

        const colorSchemes = [
            { body: 0xff6b35, fin: 0xffa040, name: 'orange' },
            { body: 0x2196f3, fin: 0x64b5f6, name: 'blue' },
            { body: 0xffd54f, fin: 0xf44336, name: 'yellow-red' },
            { body: 0x9c27b0, fin: 0xba68c8, name: 'purple' },
            { body: 0xe53935, fin: 0xef5350, name: 'red' },
            { body: 0x4caf50, fin: 0x81c784, name: 'green' },
            { body: 0xec407a, fin: 0xf48fb1, name: 'pink' },
            { body: 0xffc107, fin: 0xffab00, name: 'gold' }
        ];

        function createFish(x, y, z) {
            const scheme = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
            const scale = 0.6 + Math.random() * 0.6;
            const group = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(1, 12, 10);
            bodyGeo.scale(1.8, 0.9, 0.7);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.3,
                metalness: 0.2
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 6);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                metalness: 0.1,
                transparent: true,
                opacity: 0.9
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.x = -1.8;
            tail.castShadow = true;
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 4);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.8
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0.2, 0.8, 0);
            topFin.rotation.z = -0.3;
            group.add(topFin);

            // Left fin
            const leftFinGeo = new THREE.ConeGeometry(0.25, 0.7, 4);
            const leftFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.8
            });
            const leftFin = new THREE.Mesh(leftFinGeo, leftFinMat);
            leftFin.position.set(0.3, -0.2, 0.5);
            leftFin.rotation.x = Math.PI / 2;
            leftFin.rotation.z = 0.5;
            group.add(leftFin);

            // Right fin
            const rightFinGeo = new THREE.ConeGeometry(0.25, 0.7, 4);
            const rightFinMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.8
            });
            const rightFin = new THREE.Mesh(rightFinGeo, rightFinMat);
            rightFin.position.set(0.3, -0.2, -0.5);
            rightFin.rotation.x = -Math.PI / 2;
            rightFin.rotation.z = -0.5;
            group.add(rightFin);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.08, 6, 6);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
            eyeL.position.set(1.2, 0.15, 0.35);
            group.add(eyeL);
            const pupilL = new THREE.Mesh(pupilGeo, pupilMat);
            pupilL.position.set(1.3, 0.15, 0.42);
            group.add(pupilL);

            const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
            eyeR.position.set(1.2, 0.15, -0.35);
            group.add(eyeR);
            const pupilR = new THREE.Mesh(pupilGeo, pupilMat);
            pupilR.position.set(1.3, 0.15, -0.42);
            group.add(pupilR);

            group.scale.setScalar(scale);
            group.position.set(x || (Math.random() - 0.5) * (AQUA_W - 8), y || (Math.random() - 0.5) * (AQUA_H - 8), z || (Math.random() - 0.5) * (AQUA_D - 8));

            scene.add(group);

            const fish = {
                mesh: group,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                topFin: topFin,
                velocity: new THREE.Vector3((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 0.5, (Math.random() - 0.5) * 2),
                speed: 1.5 + Math.random() * 2,
                tailSpeed: 4 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2 + Math.random() * 2,
                baseScale: scale,
                wanderTimer: 0,
                wanderInterval: 2 + Math.random() * 3
            };

            fishArray.push(fish);
            return fish;
        }

        // Create initial 15 fish
        for (let i = 0; i < 15; i++) {
            createFish();
        }

        // === BUBBLES ===
        const bubbles = [];
        function createBubble(x, y, z) {
            const size = 0.1 + Math.random() * 0.25;
            const geo = new THREE.SphereGeometry(size, 8, 8);
            const mat = new THREE.MeshPhysicalMaterial({
                color: 0xaaddff,
                metalness: 0.0,
                roughness: 0.1,
                transmission: 0.9,
                transparent: true,
                opacity: 0.4,
                clearcoat: 1.0
            });
            const bubble = new THREE.Mesh(geo, mat);
            bubble.position.set(
                x !== undefined ? x : (Math.random() - 0.5) * (AQUA_W - 4),
                y !== undefined ? y : -HALF_H + 1,
                z !== undefined ? z : (Math.random() - 0.5) * (AQUA_D - 4)
            );
            scene.add(bubble);

            bubbles.push({
                mesh: bubble,
                speed: 1 + Math.random() * 2,
                phase: Math.random() * Math.PI * 2,
                swayAmount: 0.3 + Math.random() * 0.5
            });
        }

        for (let i = 0; i < 30; i++) {
            createBubble(undefined, -HALF_H + 1 + Math.random() * (AQUA_H - 2));
        }

        // === FOOD SYSTEM ===
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function createFood(position) {
            const geo = new THREE.SphereGeometry(0.2, 6, 6);
            const mat = new THREE.MeshStandardMaterial({
                color: 0x8b4513,
                roughness: 0.8,
                emissive: 0x331100
            });
            const food = new THREE.Mesh(geo, mat);
            food.position.copy(position);
            scene.add(food);

            foodArray.push({
                mesh: food,
                velocity: new THREE.Vector3(0, -0.5, 0),
                life: 10
            });
        }

        renderer.domElement.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            // Intersect with a plane at the center of the aquarium
            const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
            const intersection = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersection);

            if (intersection) {
                // Clamp to aquarium bounds
                intersection.x = THREE.MathUtils.clamp(intersection.x, -HALF_W + 2, HALF_W - 2);
                intersection.y = THREE.MathUtils.clamp(intersection.y, -HALF_H + 2, HALF_H - 2);
                intersection.z = THREE.MathUtils.clamp(intersection.z, -HALF_D + 2, HALF_D - 2);
                createFood(intersection);
            }
        });

        // === UI BUTTONS ===
        let lightOn = true;

        document.getElementById('btn-add-fish').addEventListener('click', () => {
            createFish();
            updateStats();
        });

        document.getElementById('btn-add-bubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
            updateStats();
        });

        document.getElementById('btn-toggle-light').addEventListener('click', function () {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.0 : 0.1;
            ambientLight.intensity = lightOn ? 0.4 : 0.15;
            pointLight1.intensity = lightOn ? 0.6 : 0.2;
            pointLight2.intensity = lightOn ? 0.4 : 0.15;
            this.textContent = lightOn ? '☀️ Свет' : '🌙 Тёмно';
            this.classList.toggle('off', !lightOn);
        });

        function updateStats() {
            document.getElementById('stat-fish').textContent = fishArray.length;
            document.getElementById('stat-bubbles').textContent = bubbles.length;
            document.getElementById('stat-food').textContent = foodArray.length;
        }

        // === ANIMATION LOOP ===
        const clock = new THREE.Clock();
        let fpsFrames = 0;
        let fpsTime = 0;
        let currentFPS = 60;

        function animate() {
            requestAnimationFrame(animate);
            const delta = Math.min(clock.getDelta(), 0.05);
            const elapsed = clock.getElapsedTime();

            // FPS counter
            fpsFrames++;
            fpsTime += delta;
            if (fpsTime >= 0.5) {
                currentFPS = Math.round(fpsFrames / fpsTime);
                document.getElementById('stat-fps').textContent = currentFPS;
                fpsFrames = 0;
                fpsTime = 0;
            }

            // Update fish
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Check for food
                if (!fish.targetFood) {
                    for (let f = 0; f < foodArray.length; f++) {
                        const food = foodArray[f];
                        const dist = pos.distanceTo(food.mesh.position);
                        if (dist < 15) {
                            fish.targetFood = food;
                            break;
                        }
                    }
                }

                // Move towards food
                if (fish.targetFood) {
                    const foodPos = fish.targetFood.mesh.position;
                    const dir = new THREE.Vector3().subVectors(foodPos, pos).normalize();
                    fish.velocity.lerp(dir.multiplyScalar(fish.speed * 1.5), delta * 3);

                    // Eat food
                    if (pos.distanceTo(foodPos) < 1.0) {
                        scene.remove(fish.targetFood.mesh);
                        fish.targetFood.mesh.geometry.dispose();
                        fish.targetFood.mesh.material.dispose();
                        foodArray.splice(foodArray.indexOf(fish.targetFood), 1);
                        fish.targetFood = null;

                        // Grow fish
                        const newScale = fish.baseScale * 1.05;
                        fish.baseScale = Math.min(newScale, 2.0);
                        fish.mesh.scale.setScalar(fish.baseScale);
                    }
                } else {
                    // Random wandering
                    fish.wanderTimer += delta;
                    if (fish.wanderTimer > fish.wanderInterval) {
                        fish.wanderTimer = 0;
                        fish.wanderInterval = 2 + Math.random() * 4;
                        fish.velocity.x += (Math.random() - 0.5) * 2;
                        fish.velocity.y += (Math.random() - 0.5) * 1;
                        fish.velocity.z += (Math.random() - 0.5) * 2;
                    }

                    // Normalize speed
                    const spd = fish.velocity.length();
                    if (spd > fish.speed) {
                        fish.velocity.multiplyScalar(fish.speed / spd);
                    }
                    if (spd < fish.speed * 0.3) {
                        fish.velocity.multiplyScalar(1.05);
                    }
                }

                // Collision avoidance
                for (let j = i + 1; j < fishArray.length; j++) {
                    const other = fishArray[j];
                    const diff = new THREE.Vector3().subVectors(pos, other.mesh.position);
                    const dist = diff.length();
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const force = diff.normalize().multiplyScalar((fish.avoidanceRadius - dist) / fish.avoidanceRadius * 2);
                        fish.velocity.add(force);
                        other.velocity.sub(force);
                    }
                }

                // Wall reflection
                const margin = 2;
                if (pos.x > HALF_W - margin) fish.velocity.x -= delta * 5;
                if (pos.x < -HALF_W + margin) fish.velocity.x += delta * 5;
                if (pos.y > HALF_H - margin) fish.velocity.y -= delta * 5;
                if (pos.y < -HALF_H + margin) fish.velocity.y += delta * 5;
                if (pos.z > HALF_D - margin) fish.velocity.z -= delta * 5;
                if (pos.z < -HALF_D + margin) fish.velocity.z += delta * 5;

                // Apply velocity
                pos.addScaledVector(fish.velocity, delta);

                // Orient fish towards movement direction
                if (fish.velocity.length() > 0.1) {
                    const targetQuat = new THREE.Quaternion();
                    const lookDir = fish.velocity.clone().normalize();
                    const m = new THREE.Matrix4();
                    m.lookAt(new THREE.Vector3(0, 0, 0), lookDir, new THREE.Vector3(0, 1, 0));
                    targetQuat.setFromRotationMatrix(m);
                    fish.mesh.quaternion.slerp(targetQuat, delta * 3);
                }

                // Animate tail
                fish.phase += delta * fish.tailSpeed;
                fish.tail.rotation.y = Math.sin(fish.phase) * 0.6;

                // Animate fins
                fish.leftFin.rotation.z = 0.5 + Math.sin(fish.phase * 0.7 + 1) * 0.3;
                fish.rightFin.rotation.z = -0.5 + Math.sin(fish.phase * 0.7 + 2) * 0.3;
                fish.topFin.rotation.z = -0.3 + Math.sin(fish.phase * 0.5) * 0.15;
            }

            // Update food
            for (let i = foodArray.length - 1; i >= 0; i--) {
                const food = foodArray[i];
                food.mesh.position.addScaledVector(food.velocity, delta);
                food.velocity.y -= 2 * delta; // gravity

                // Remove if hits bottom
                if (food.mesh.position.y < -HALF_H + 0.5) {
                    scene.remove(food.mesh);
                    food.mesh.geometry.dispose();
                    food.mesh.material.dispose();
                    foodArray.splice(i, 1);
                }

                // Lifetime
                food.life -= delta;
                if (food.life <= 0) {
                    scene.remove(food.mesh);
                    food.mesh.geometry.dispose();
                    food.mesh.material.dispose();
                    foodArray.splice(i, 1);
                }
            }

            // Update bubbles
            for (let i = bubbles.length - 1; i >= 0; i--) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * delta;
                b.mesh.position.x += Math.sin(elapsed * 2 + b.phase) * b.swayAmount * delta;
                b.mesh.position.z += Math.cos(elapsed * 1.5 + b.phase) * b.swayAmount * delta;

                // Reset if reaches top
                if (b.mesh.position.y > HALF_H - 0.5) {
                    b.mesh.position.y = -HALF_H + 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * (AQUA_W - 4);
                    b.mesh.position.z = (Math.random() - 0.5) * (AQUA_D - 4);
                }
            }

            // Animate seaweed
            for (let i = 0; i < seaweeds.length; i++) {
                const s = seaweeds[i];
                s.mesh.rotation.x = Math.sin(elapsed * s.speed + s.phase) * 0.08;
                s.mesh.rotation.z = Math.cos(elapsed * s.speed * 0.7 + s.phase) * 0.06;
            }

            // Subtle light animation
            pointLight1.intensity = (lightOn ? 0.6 : 0.2) + Math.sin(elapsed * 0.5) * 0.1;
            pointLight2.intensity = (lightOn ? 0.4 : 0.15) + Math.cos(elapsed * 0.7) * 0.08;

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
        animate();
    </script>
</body>
</html>
```

## Что реализовано

| Компонент | Детали |
|-----------|--------|
| **🐠 Рыбки** | 15 штук, 8 цветовых схем, тело + хвост + плавники + глаза, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, отражение от стен, случайное блуждание, преследование корма, рост на 5% |
| **🌊 Окружение** | Стеклянный контейнер (transmission 0.95), песчаное дно с неровностями, 8 камней, 12 водорослей (TubeGeometry) |
| **💭 Пузыри** | 30 шт., MeshPhysicalMaterial, синусоидальное покачивание, сброс наверху |
| **🍽️ Кормление** | Клик → raycaster → корм падает с гравитацией → рыбки преследуют → рост |
| **💡 Свет** | Ambient + Directional (тени 2048²) + 2 PointLight, кнопка вкл/выкл |
| **🎮 Камера** | OrbitControls, damping, zoom 10–60, ограничение полярного угла |
| **🖥️ UI** | Glass-панели, FPS, счётчики, 3 кнопки с hover-эффектами |
| **🎨 Эффекты** | FogExp2, анимация водорослей, пульсация света, градиентный фон |

Просто сохраните как `.html` и откройте в браузере — всё работает без сборки.