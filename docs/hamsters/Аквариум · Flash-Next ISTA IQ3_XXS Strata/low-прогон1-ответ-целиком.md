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
            background: rgba(10, 30, 60, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            z-index: 100;
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

        .panel-title {
            font-size: 1.4em;
            font-weight: 700;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64b5f6, #42a5f5, #1e88e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 20px rgba(100, 181, 246, 0.3);
        }

        .instructions {
            font-size: 0.85em;
            line-height: 1.6;
            color: rgba(200, 230, 255, 0.8);
            margin-bottom: 15px;
        }

        .instructions li {
            list-style: none;
            padding: 3px 0;
        }

        .instructions li::before {
            content: '• ';
            color: #64b5f6;
        }

        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .btn {
            padding: 10px 16px;
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
            background: linear-gradient(135deg, #ff6b35, #f7931a);
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
            transform: translateY(0px) scale(0.97);
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(100, 180, 255, 0.1);
        }

        .stat-label {
            font-size: 0.85em;
            color: rgba(200, 230, 255, 0.7);
        }

        .stat-value {
            font-size: 1.1em;
            font-weight: 700;
            color: #64b5f6;
        }

        .stat-value.fps {
            color: #69f0ae;
        }

        .stat-value.food {
            color: #ffd54f;
        }

        @media (max-width: 768px) {
            .info-panel {
                max-width: 200px;
                padding: 14px;
            }
            .stats-panel {
                min-width: 140px;
                padding: 14px;
            }
            .panel-title {
                font-size: 1.1em;
            }
            .btn {
                padding: 8px 12px;
                font-size: 0.8em;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="glass-panel info-panel">
        <div class="panel-title">🐠 3D Аквариум</div>
        <ul class="instructions">
            <li>ЛКМ + движение — вращение</li>
            <li>ПКМ + движение — панорама</li>
            <li>Колесо мыши — зум</li>
            <li>Клик по аквариуму — корм</li>
        </ul>
        <div class="btn-group">
            <button class="btn btn-fish" id="btnAddFish">🐟 Добавить рыбку</button>
            <button class="btn btn-bubbles" id="btnAddBubbles">💨 Больше пузырей</button>
            <button class="btn btn-light" id="btnLight">💡 Свет</button>
        </div>
    </div>

    <div class="glass-panel stats-panel">
        <div class="panel-title">📊 Статистика</div>
        <div class="stat-row">
            <span class="stat-label">Рыбки</span>
            <span class="stat-value" id="fishCount">15</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Корм</span>
            <span class="stat-value food" id="foodCount">0</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Пузыри</span>
            <span class="stat-value" id="bubbleCount">30</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">FPS</span>
            <span class="stat-value fps" id="fpsCounter">60</span>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // ==================== SCENE SETUP ====================
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a1628);
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

        // ==================== CONTROLS ====================
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

        const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.0);
        dirLight.position.set(15, 30, 10);
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

        const pointLight1 = new THREE.PointLight(0x4488ff, 0.6, 40);
        pointLight1.position.set(-10, 15, -5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2266cc, 0.4, 35);
        pointLight2.position.set(10, 12, 8);
        scene.add(pointLight2);

        // ==================== AQUARIUM BOUNDS ====================
        const AQUARIUM = {
            width: 36,
            height: 24,
            depth: 20,
            halfW: 18,
            halfH: 12,
            halfD: 10
        };

        // ==================== GLASS CONTAINER ====================
        function createGlassContainer() {
            const glassMaterial = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                transparent: true,
                opacity: 0.15,
                transmission: 0.95,
                roughness: 0.05,
                metalness: 0,
                side: THREE.DoubleSide,
                depthWrite: false
            });

            // Front and back
            const frontBackGeo = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.height);
            const front = new THREE.Mesh(frontBackGeo, glassMaterial);
            front.position.set(0, AQUARIUM.halfH, AQUARIUM.halfD);
            scene.add(front);

            const back = new THREE.Mesh(frontBackGeo, glassMaterial);
            back.position.set(0, AQUARIUM.halfH, -AQUARIUM.halfD);
            back.rotation.y = Math.PI;
            scene.add(back);

            // Left and right
            const sideGeo = new THREE.PlaneGeometry(AQUARIUM.depth, AQUARIUM.height);
            const left = new THREE.Mesh(sideGeo, glassMaterial);
            left.position.set(-AQUARIUM.halfW, AQUARIUM.halfH, 0);
            left.rotation.y = Math.PI / 2;
            scene.add(left);

            const right = new THREE.Mesh(sideGeo, glassMaterial);
            right.position.set(AQUARIUM.halfW, AQUARIUM.halfH, 0);
            right.rotation.y = -Math.PI / 2;
            scene.add(right);

            // Top
            const topGeo = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth);
            const top = new THREE.Mesh(topGeo, glassMaterial);
            top.position.set(0, AQUARIUM.height, 0);
            top.rotation.x = -Math.PI / 2;
            scene.add(top);

            // Wireframe edges
            const edgesGeo = new THREE.BoxGeometry(AQUARIUM.width, AQUARIUM.height, AQUARIUM.depth);
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x4488aa, transparent: true, opacity: 0.4 });
            const edges = new THREE.LineSegments(new THREE.EdgesGeometry(edgesGeo), edgesMat);
            edges.position.set(0, AQUARIUM.halfH, 0);
            scene.add(edges);
        }
        createGlassContainer();

        // ==================== SANDY BOTTOM ====================
        function createSandyBottom() {
            const sandGeo = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth, 40, 30);
            const positions = sandGeo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                const x = positions.getX(i);
                const y = positions.getY(i);
                const noise = Math.sin(x * 0.5) * Math.cos(y * 0.7) * 0.3 +
                              Math.sin(x * 1.2 + y * 0.8) * 0.15 +
                              Math.random() * 0.1;
                positions.setZ(i, noise);
            }
            sandGeo.computeVertexNormals();

            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xc2a060,
                roughness: 0.9,
                metalness: 0.0,
                flatShading: false
            });

            const sand = new THREE.Mesh(sandGeo, sandMat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = 0;
            sand.receiveShadow = true;
            scene.add(sand);
        }
        createSandyBottom();

        // ==================== ROCKS ====================
        function createRocks() {
            for (let i = 0; i < 8; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const rockGeo = new THREE.DodecahedronGeometry(size, 1);
                const positions = rockGeo.attributes.position;
                for (let j = 0; j < positions.count; j++) {
                    positions.setX(j, positions.getX(j) + (Math.random() - 0.5) * 0.3);
                    positions.setY(j, positions.getY(j) + (Math.random() - 0.5) * 0.3);
                    positions.setZ(j, positions.getZ(j) + (Math.random() - 0.5) * 0.3);
                }
                rockGeo.computeVertexNormals();

                const rockMat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.3, 0.3 + Math.random() * 0.2),
                    roughness: 0.85,
                    metalness: 0.05
                });

                const rock = new THREE.Mesh(rockGeo, rockMat);
                rock.position.set(
                    (Math.random() - 0.5) * (AQUARIUM.width - 6),
                    size * 0.4,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 6)
                );
                rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
                rock.castShadow = true;
                rock.receiveShadow = true;
                scene.add(rock);
            }
        }
        createRocks();

        // ==================== SEAWEED ====================
        const seaweeds = [];
        function createSeaweeds() {
            for (let i = 0; i < 12; i++) {
                const height = 3 + Math.random() * 5;
                const segments = 8 + Math.floor(Math.random() * 4);
                const points = [];
                const baseX = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                const baseZ = (Math.random() - 0.5) * (AQUARIUM.depth - 4);

                for (let j = 0; j <= segments; j++) {
                    const t = j / segments;
                    points.push(new THREE.Vector3(
                        baseX + Math.sin(t * 3 + i) * 0.5,
                        t * height,
                        baseZ + Math.cos(t * 2.5 + i * 0.7) * 0.4
                    ));
                }

                const curve = new THREE.CatmullRomCurve3(points);
                const tubeGeo = new THREE.TubeGeometry(curve, segments, 0.15 + Math.random() * 0.1, 6, false);
                const hue = 0.25 + Math.random() * 0.15;
                const tubeMat = new THREE.MeshStandardMaterial({
                    color: new THREE.Color().setHSL(hue, 0.7, 0.35),
                    roughness: 0.7,
                    metalness: 0.0,
                    side: THREE.DoubleSide
                });

                const seaweed = new THREE.Mesh(tubeGeo, tubeMat);
                seaweed.castShadow = true;
                seaweed.receiveShadow = true;
                seaweed.userData = { baseX: baseX, baseZ: baseZ, height: height, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 };
                scene.add(seaweed);
                seaweeds.push(seaweed);
            }
        }
        createSeaweeds();

        // ==================== FISH CREATION ====================
        const fishArray = [];
        const fishColors = [
            { body: 0xff6b35, fin: 0xff8c5a, eye: 0xffffff },   // оранжевая
            { body: 0x2196f3, fin: 0x64b5f6, eye: 0xffffff },   // синяя
            { body: 0xffeb3b, fin: 0xff5722, eye: 0xffffff },   // желто-красная
            { body: 0x9c27b0, fin: 0xce93d8, eye: 0xffffff },   // фиолетовая
            { body: 0xf44336, fin: 0xef9a9a, eye: 0xffffff },   // красная
            { body: 0x4caf50, fin: 0x81c784, eye: 0xffffff },   // зеленая
            { body: 0xe91e63, fin: 0xf48fb1, eye: 0xffffff },   // розовая
            { body: 0xffc107, fin: 0xffd54f, eye: 0xffffff }    // золотая
        ];

        function createFish(colorIndex) {
            const color = fishColors[colorIndex % fishColors.length];
            const scale = 0.6 + Math.random() * 0.6;
            const group = new THREE.Group();

            // Body - elongated sphere
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.6, 0.7, 0.5);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: color.body,
                roughness: 0.4,
                metalness: 0.1
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: color.fin,
                roughness: 0.5,
                metalness: 0.05,
                side: THREE.DoubleSide
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.8, 0, 0);
            tail.castShadow = true;
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.3, 0.8, 6);
            const topFinMat = new THREE.MeshStandardMaterial({
                color: color.fin,
                roughness: 0.5,
                side: THREE.DoubleSide
            });
            const topFin = new THREE.Mesh(topFinGeo, topFinMat);
            topFin.position.set(0.2, 0.7, 0);
            topFin.rotation.z = -0.3;
            group.add(topFin);

            // Left fin
            const finGeo = new THREE.ConeGeometry(0.25, 0.6, 6);
            finGeo.rotateZ(Math.PI / 2);
            const finMat = new THREE.MeshStandardMaterial({
                color: color.fin,
                roughness: 0.5,
                side: THREE.DoubleSide
            });
            const leftFin = new THREE.Mesh(finGeo, finMat);
            leftFin.position.set(0.3, -0.1, 0.5);
            leftFin.rotation.x = 0.3;
            group.add(leftFin);

            // Right fin
            const rightFin = new THREE.Mesh(finGeo.clone(), finMat);
            rightFin.position.set(0.3, -0.1, -0.5);
            rightFin.rotation.x = -0.3;
            group.add(rightFin);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.18, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: color.eye, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.09, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
            eyeL.position.set(1.2, 0.15, 0.25);
            group.add(eyeL);
            const pupilL = new THREE.Mesh(pupilGeo, pupilMat);
            pupilL.position.set(1.35, 0.15, 0.25);
            group.add(pupilL);

            const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
            eyeR.position.set(1.2, 0.15, -0.25);
            group.add(eyeR);
            const pupilR = new THREE.Mesh(pupilGeo, pupilMat);
            pupilR.position.set(1.35, 0.15, -0.25);
            group.add(pupilR);

            group.scale.setScalar(scale);

            const fishData = {
                mesh: group,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                topFin: topFin,
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
                wanderTimer: Math.random() * 3,
                scale: scale
            };

            group.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 8),
                3 + Math.random() * (AQUARIUM.height - 8),
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );

            scene.add(group);
            fishArray.push(fishData);
            return fishData;
        }

        // Create initial 15 fish
        for (let i = 0; i < 15; i++) {
            createFish(i);
        }

        // ==================== BUBBLES ====================
        const bubbles = [];
        function createBubble() {
            const size = 0.15 + Math.random() * 0.35;
            const bubbleGeo = new THREE.SphereGeometry(size, 12, 12);
            const bubbleMat = new THREE.MeshPhysicalMaterial({
                color: 0xaaddff,
                transparent: true,
                opacity: 0.4,
                transmission: 0.8,
                roughness: 0.1,
                metalness: 0.0,
                clearcoat: 1.0
            });
            const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
            bubble.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                Math.random() * AQUARIUM.height,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            bubble.userData = {
                speed: 0.5 + Math.random() * 1.0,
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
        function createFood(x, y, z) {
            const foodGeo = new THREE.SphereGeometry(0.25, 8, 8);
            const foodMat = new THREE.MeshStandardMaterial({
                color: 0xffcc00,
                emissive: 0x442200,
                roughness: 0.6
            });
            const food = new THREE.Mesh(foodGeo, foodMat);
            food.position.set(x, y, z);
            food.userData = {
                velocity: new THREE.Vector3(0, 0, 0),
                gravity: -3.0,
                eaten: false
            };
            scene.add(food);
            foods.push(food);
        }

        // ==================== RAYCASTER FOR CLICK ====================
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        renderer.domElement.addEventListener('click', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            // Create food at intersection with a virtual plane or at a point in the aquarium
            const dir = raycaster.ray.direction.clone();
            const origin = raycaster.ray.origin.clone();

            // Find a point inside the aquarium
            let t = 15;
            const point = origin.clone().add(dir.multiplyScalar(t));

            // Clamp to aquarium bounds
            point.x = Math.max(-AQUARIUM.halfW + 2, Math.min(AQUARIUM.halfW - 2, point.x));
            point.y = Math.max(2, Math.min(AQUARIUM.height - 2, point.y));
            point.z = Math.max(-AQUARIUM.halfD + 2, Math.min(AQUARIUM.halfD - 2, point.z));

            createFood(point.x, point.y, point.z);
        });

        // ==================== UI BUTTONS ====================
        document.getElementById('btnAddFish').addEventListener('click', () => {
            createFish(Math.floor(Math.random() * 8));
            document.getElementById('fishCount').textContent = fishArray.length;
        });

        document.getElementById('btnAddBubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
            document.getElementById('bubbleCount').textContent = bubbles.length;
        });

        let lightOn = true;
        document.getElementById('btnLight').addEventListener('click', () => {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.0 : 0.1;
            ambientLight.intensity = lightOn ? 0.4 : 0.15;
            document.getElementById('btnLight').textContent = lightOn ? '💡 Свет' : '🌙 Ночь';
        });

        // ==================== ANIMATION LOOP ====================
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
            if (fpsTime >= 1.0) {
                document.getElementById('fpsCounter').textContent = frameCount;
                frameCount = 0;
                fpsTime = 0;
            }

            // Update controls
            controls.update();

            // ---- FISH BEHAVIOR ----
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Wandering - periodic direction change
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.velocity.x += (Math.random() - 0.5) * 2;
                    fish.velocity.y += (Math.random() - 0.5) * 0.8;
                    fish.velocity.z += (Math.random() - 0.5) * 2;
                    fish.wanderTimer = 1 + Math.random() * 3;
                }

                // Food chasing
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
                    const dir = fish.targetFood.position.clone().sub(pos).normalize();
                    fish.velocity.add(dir.multiplyScalar(3.0 * delta));

                    // Eat food
                    if (closestDist < 1.2) {
                        fish.targetFood.userData.eaten = true;
                        scene.remove(fish.targetFood);
                        const idx = foods.indexOf(fish.targetFood);
                        if (idx > -1) foods.splice(idx, 1);
                        // Growth
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                    }
                }

                // Collision avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const repel = pos.clone().sub(other.mesh.position).normalize();
                        const force = (fish.avoidanceRadius - dist) / fish.avoidanceRadius;
                        fish.velocity.add(repel.multiplyScalar(force * 4.0 * delta));
                    }
                }

                // Wall reflection
                const margin = 2;
                if (pos.x > AQUARIUM.halfW - margin) fish.velocity.x -= 3.0 * delta;
                if (pos.x < -AQUARIUM.halfW + margin) fish.velocity.x += 3.0 * delta;
                if (pos.y > AQUARIUM.height - margin) fish.velocity.y -= 3.0 * delta;
                if (pos.y < 2) fish.velocity.y += 3.0 * delta;
                if (pos.z > AQUARIUM.halfD - margin) fish.velocity.z -= 3.0 * delta;
                if (pos.z < -AQUARIUM.halfD + margin) fish.velocity.z += 3.0 * delta;

                // Speed limiting
                const speed = fish.velocity.length();
                if (speed > fish.speed) {
                    fish.velocity.multiplyScalar(fish.speed / speed);
                }

                // Apply velocity
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Clamp position
                pos.x = Math.max(-AQUARIUM.halfW + 1, Math.min(AQUARIUM.halfW - 1, pos.x));
                pos.y = Math.max(1.5, Math.min(AQUARIUM.height - 1, pos.y));
                pos.z = Math.max(-AQUARIUM.halfD + 1, Math.min(AQUARIUM.halfD - 1, pos.z));

                // Rotation - face direction of movement
                if (speed > 0.1) {
                    const targetAngle = Math.atan2(fish.velocity.z, fish.velocity.x);
                    const currentAngle = fish.mesh.rotation.y;
                    let diff = targetAngle - currentAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    fish.mesh.rotation.y += diff * 3.0 * delta;

                    // Slight tilt based on vertical velocity
                    const targetTilt = Math.atan2(fish.velocity.y, Math.sqrt(fish.velocity.x * fish.velocity.x + fish.velocity.z * fish.velocity.z));
                    fish.mesh.rotation.z += (targetTilt - fish.mesh.rotation.z) * 2.0 * delta;
                }

                // Tail animation
                fish.phase += delta;
                const tailAngle = Math.sin(fish.phase * fish.tailSpeed) * 0.5;
                fish.tail.rotation.y = tailAngle;

                // Fin animation
                const finAngle = Math.sin(fish.phase * fish.tailSpeed * 0.7) * 0.3;
                fish.leftFin.rotation.x = 0.3 + finAngle;
                fish.rightFin.rotation.x = -0.3 - finAngle;
                fish.topFin.rotation.z = -0.3 + Math.sin(fish.phase * 2) * 0.15;
            }

            // ---- BUBBLES ----
            for (let i = 0; i < bubbles.length; i++) {
                const bubble = bubbles[i];
                const data = bubble.userData;
                bubble.position.y += data.speed * delta;
                bubble.position.x += Math.sin(data.wobblePhase + bubble.position.y * data.wobbleSpeed) * data.wobbleAmp * delta;
                bubble.position.z += Math.cos(data.wobblePhase + bubble.position.y * data.wobbleSpeed * 0.7) * data.wobbleAmp * delta * 0.5;

                // Reset at top
                if (bubble.position.y > AQUARIUM.height - 0.5) {
                    bubble.position.y = 0.5;
                    bubble.position.x = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                    bubble.position.z = (Math.random() - 0.5) * (AQUARIUM.depth - 4);
                }
            }

            // ---- FOOD PHYSICS ----
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                if (food.userData.eaten) continue;
                food.userData.velocity.y += food.userData.gravity * delta;
                food.position.add(food.userData.velocity.clone().multiplyScalar(delta));

                // Remove if hits bottom
                if (food.position.y < 0.3) {
                    scene.remove(food);
                    foods.splice(i, 1);
                }
            }

            // ---- SEAWEED ANIMATION ----
            for (let i = 0; i < seaweeds.length; i++) {
                const sw = seaweeds[i];
                const data = sw.userData;
                sw.rotation.x = Math.sin(data.phase + now * 0.001 * data.speed) * 0.08;
                sw.rotation.z = Math.cos(data.phase + now * 0.0008 * data.speed) * 0.06;
            }

            // ---- UPDATE UI ----
            document.getElementById('fishCount').textContent = fishArray.length;
            document.getElementById('foodCount').textContent = foods.length;
            document.getElementById('bubbleCount').textContent = bubbles.length;

            renderer.render(scene, camera);
        }

        animate();

        // ==================== RESIZE ====================
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```

Этот файл представляет собой полностью автономный 3D аквариум. Вот что реализовано:

**🐠 Рыбки (15 шт.):**
- Детализированная анатомия: тело, хвост, 3 плавника, глаза с зрачками
- 8 цветовых схем, случайный масштаб 0.6–1.2
- Анимация хвоста и плавников с индивидуальной частотой

**🧠 ИИ поведение:**
- Избегание столкновений между рыбками
- Отражение от стен аквариума
- Случайное блуждание с периодической сменой направления
- Преследование корма в радиусе 15 единиц
- Рост на 5% после поедания корма

**🌊 Окружение:**
- Стеклянный контейнер 36×24×20 с wireframe рамкой
- Песчаное дно с процедурными неровностями
- 8 деформированных камней с тенями
- 12 кустов водорослей с анимацией покачивания

**💭 Пузыри (30 шт.):**
- Прозрачные сферы с эффектом стекла
- Движение вверх с синусоидальным покачиванием
- Автоматический сброс при достижении поверхности

**🍽️ Кормление:**
- Клик создаёт корм с гравитацией
- Рыбки обнаруживают и преследуют корм
- Удаление при достижении дна

**💡 Освещение:**
- Ambient + Directional (с тенями 2048×2048) + 2 PointLight
- Переключаемый режим день/ночь

**🎮 Управление:**
- OrbitControls с damping, зумом и ограничением угла
- Кнопки добавления рыбок, пузырей и переключения света