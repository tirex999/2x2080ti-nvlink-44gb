

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

        canvas {
            display: block;
        }

        .panel {
            position: absolute;
            background: rgba(10, 25, 50, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(100, 180, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .info-panel {
            top: 20px;
            left: 20px;
            width: 280px;
            z-index: 100;
        }

        .info-panel h1 {
            font-size: 22px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #4fc3f7, #81c784, #fff176);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .info-panel p {
            font-size: 12px;
            line-height: 1.6;
            color: #90caf9;
            margin-bottom: 8px;
        }

        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }

        .btn {
            padding: 8px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            color: white;
            transition: all 0.3s ease;
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
            transition: left 0.5s;
        }

        .btn:hover::after {
            left: 100%;
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6f00, #ffa000);
            box-shadow: 0 4px 15px rgba(255, 111, 0, 0.4);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 111, 0, 0.6);
        }

        .btn-bubble {
            background: linear-gradient(135deg, #0288d1, #4fc3f7);
            box-shadow: 0 4px 15px rgba(2, 136, 209, 0.4);
        }

        .btn-bubble:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(2, 136, 209, 0.6);
        }

        .btn-light {
            background: linear-gradient(135deg, #f9a825, #ffee58);
            box-shadow: 0 4px 15px rgba(249, 168, 37, 0.4);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(249, 168, 37, 0.6);
        }

        .stats-panel {
            top: 20px;
            right: 20px;
            min-width: 160px;
            z-index: 100;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(100, 180, 255, 0.1);
        }

        .stat-item:last-child {
            border-bottom: none;
        }

        .stat-label {
            font-size: 12px;
            color: #90caf9;
        }

        .stat-value {
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
        }

        .hint {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 25, 50, 0.6);
            backdrop-filter: blur(8px);
            padding: 10px 24px;
            border-radius: 24px;
            border: 1px solid rgba(100, 180, 255, 0.15);
            color: #90caf9;
            font-size: 13px;
            z-index: 100;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.8; }
            50% { opacity: 1; }
        }

        @media (max-width: 768px) {
            .info-panel {
                width: 220px;
                padding: 14px;
            }
            .info-panel h1 {
                font-size: 16px;
            }
            .stats-panel {
                min-width: 120px;
                padding: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <p><strong>Управление:</strong></p>
        <p>🖱️ ЛКМ — вращение камеры</p>
        <p>🖱️ ПКМ — панорамирование</p>
        <p>🖱️ Колесо — зум</p>
        <p>👆 Клик — бросить корм</p>
        <div class="btn-group">
            <button class="btn btn-fish" onclick="addFish()">+ Рыбка</button>
            <button class="btn btn-bubble" onclick="addBubbles()">+ Пузыри</button>
            <button class="btn btn-light" onclick="toggleLight()">💡 Свет</button>
        </div>
    </div>

    <div class="panel stats-panel">
        <div class="stat-item">
            <span class="stat-label">Рыбки</span>
            <span class="stat-value" id="fishCount">15</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Пузыри</span>
            <span class="stat-value" id="bubbleCount">30</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Корм</span>
            <span class="stat-value" id="foodCount">0</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">FPS</span>
            <span class="stat-value" id="fpsCounter">60</span>
        </div>
    </div>

    <div class="hint">Кликните по воде, чтобы покормить рыбок 🍽️</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === СЦЕНА ===
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a1628);
        scene.fog = new THREE.FogExp2(0x0a1628, 0.015);

        // === КАМЕРА ===
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(0, 15, 35);

        // === РЕНДЕРЕР ===
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        // === КОНТРОЛЫ ===
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 5, 0);

        // === ОСВЕЩЕНИЕ ===
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(10, 30, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 100;
        dirLight.shadow.camera.left = -25;
        dirLight.shadow.camera.right = 25;
        dirLight.shadow.camera.top = 25;
        dirLight.shadow.camera.bottom = -25;
        scene.add(dirLight);

        const pointLight1 = new THREE.PointLight(0x4488ff, 0.6, 30);
        pointLight1.position.set(-10, 15, 0);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x2244aa, 0.4, 25);
        pointLight2.position.set(10, 10, 5);
        scene.add(pointLight2);

        // === РАЗМЕРЫ АКВАРИУМА ===
        const TANK_W = 36;
        const TANK_H = 24;
        const TANK_D = 20;
        const TANK_MIN_X = -TANK_W / 2;
        const TANK_MAX_X = TANK_W / 2;
        const TANK_MIN_Y = 0;
        const TANK_MAX_Y = TANK_H;
        const TANK_MIN_Z = -TANK_D / 2;
        const TANK_MAX_Z = TANK_D / 2;

        // === СТЕКЛЯННЫЙ КОНТЕЙНЕР ===
        function createTank() {
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                transparent: true,
                opacity: 0.08,
                roughness: 0,
                metalness: 0,
                side: THREE.DoubleSide,
                transmission: 0.95,
                thickness: 0.5
            });

            const geo = new THREE.BoxGeometry(TANK_W, TANK_H, TANK_D);
            const tank = new THREE.Mesh(geo, glassMat);
            tank.position.set(0, TANK_H / 2, 0);
            scene.add(tank);

            // Wireframe edges
            const edgesGeo = new THREE.EdgesGeometry(geo);
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x4488cc, transparent: true, opacity: 0.5 });
            const edges = new THREE.LineSegments(edgesGeo, edgesMat);
            edges.position.copy(tank.position);
            scene.add(edges);
        }
        createTank();

        // === ПЕСЧАНОЕ ДНО ===
        function createSand() {
            const geo = new THREE.PlaneGeometry(TANK_W - 0.5, TANK_D - 0.5, 32, 32);
            const pos = geo.attributes.position;
            for (let i = 0; i < pos.count; i++) {
                const x = pos.getX(i);
                const y = pos.getY(i);
                pos.setZ(i, Math.sin(x * 0.5) * 0.15 + Math.cos(y * 0.7) * 0.1 + Math.random() * 0.08);
            }
            geo.computeVertexNormals();

            const mat = new THREE.MeshStandardMaterial({
                color: 0xc2a66b,
                roughness: 0.95,
                metalness: 0.0
            });

            const sand = new THREE.Mesh(geo, mat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = 0.1;
            sand.receiveShadow = true;
            scene.add(sand);
        }
        createSand();

        // === КАМНИ ===
        function createRocks() {
            const rockMat = new THREE.MeshStandardMaterial({
                color: 0x555566,
                roughness: 0.85,
                metalness: 0.1
            });

            for (let i = 0; i < 8; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const geo = new THREE.DodecahedronGeometry(size, 1);
                const pos = geo.attributes.position;
                for (let j = 0; j < pos.count; j++) {
                    pos.setX(j, pos.getX(j) * (0.8 + Math.random() * 0.4));
                    pos.setY(j, pos.getY(j) * (0.7 + Math.random() * 0.5));
                    pos.setZ(j, pos.getZ(j) * (0.8 + Math.random() * 0.4));
                }
                geo.computeVertexNormals();

                const rock = new THREE.Mesh(geo, rockMat.clone());
                rock.material.color.setHSL(0.6 + Math.random() * 0.1, 0.1, 0.25 + Math.random() * 0.15);
                rock.position.set(
                    (Math.random() - 0.5) * (TANK_W - 6),
                    size * 0.5,
                    (Math.random() - 0.5) * (TANK_D - 6)
                );
                rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
                rock.castShadow = true;
                rock.receiveShadow = true;
                scene.add(rock);
            }
        }
        createRocks();

        // === ВОДОРОССИ ===
        const seaweeds = [];
        function createSeaweed(x, z) {
            const height = 3 + Math.random() * 5;
            const segments = 8;
            const points = [];
            for (let i = 0; i <= segments; i++) {
                const t = i / segments;
                points.push(new THREE.Vector3(
                    Math.sin(t * 2) * 0.3 * t,
                    t * height,
                    Math.cos(t * 3) * 0.2 * t
                ));
            }
            const curve = new THREE.CatmullRomCurve3(points);
            const geo = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);
            const color = new THREE.Color().setHSL(0.3 + Math.random() * 0.1, 0.7, 0.3 + Math.random() * 0.2);
            const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0.0 });
            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(x, 0.1, z);
            mesh.castShadow = true;
            scene.add(mesh);
            seaweeds.push({ mesh, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 1.0 });
        }

        for (let i = 0; i < 12; i++) {
            createSeaweed((Math.random() - 0.5) * (TANK_W - 8), (Math.random() - 0.5) * (TANK_D - 8));
        }

        // === ЦВЕТОВЫЕ СХЕМЫ РЫБОК ===
        const FISH_COLORS = [
            { body: 0xff6600, fin: 0xff9933, name: 'Оранжевая' },
            { body: 0x2266ff, fin: 0x4499ff, name: 'Синяя' },
            { body: 0xffcc00, fin: 0xff4400, name: 'Жёлто-красная' },
            { body: 0x9933cc, fin: 0xbb66ee, name: 'Фиолетовая' },
            { body: 0xdd2222, fin: 0xff5555, name: 'Красная' },
            { body: 0x22aa44, fin: 0x44dd66, name: 'Зелёная' },
            { body: 0xff66aa, fin: 0xff99cc, name: 'Розовая' },
            { body: 0xd4a820, fin: 0xf0cc44, name: 'Золотая' }
        ];

        // === СОЗДАНИЕ РЫБКИ ===
        const fishArray = [];

        function createFish(colorIndex, scale) {
            const scheme = FISH_COLORS[colorIndex % FISH_COLORS.length];
            const group = new THREE.Group();

            // Тело
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.8, 1, 0.7);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.3,
                metalness: 0.4
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Глаза
            const eyeGeo = new THREE.SphereGeometry(0.2, 8, 8);
            const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.1, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1, metalness: 0.3 });

            const eyeL = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            eyeL.position.set(1.2, 0.2, 0.45);
            const pupilL = new THREE.Mesh(pupilGeo, pupilMat);
            pupilL.position.set(0.12, 0, 0);
            eyeL.add(pupilL);
            group.add(eyeL);

            const eyeR = new THREE.Mesh(eyeGeo, eyeWhiteMat);
            eyeR.position.set(1.2, 0.2, -0.45);
            const pupilR = new THREE.Mesh(pupilGeo, pupilMat);
            pupilR.position.set(0.12, 0, 0);
            eyeR.add(pupilR);
            group.add(eyeR);

            // Хвост
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.4,
                metalness: 0.2,
                transparent: true,
                opacity: 0.85
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.8, 0, 0);
            group.add(tail);

            // Верхний плавник
            const topFinGeo = new THREE.ConeGeometry(0.4, 0.8, 4);
            topFinGeo.rotateZ(Math.PI / 2);
            const topFin = new THREE.Mesh(topFinGeo, tailMat.clone());
            topFin.position.set(0, 0.7, 0);
            topFin.rotation.z = -0.3;
            group.add(topFin);

            // Боковые плавники
            const finGeo = new THREE.ConeGeometry(0.3, 0.6, 4);
            finGeo.rotateZ(Math.PI / 2);
            const leftFin = new THREE.Mesh(finGeo, tailMat.clone());
            leftFin.position.set(0.2, -0.3, 0.5);
            leftFin.rotation.y = 0.4;
            group.add(leftFin);

            const rightFin = new THREE.Mesh(finGeo, tailMat.clone());
            rightFin.position.set(0.2, -0.3, -0.5);
            rightFin.rotation.y = -0.4;
            group.add(rightFin);

            // Позиция
            const startX = (Math.random() - 0.5) * (TANK_W - 8);
            const startY = 2 + Math.random() * (TANK_H - 6);
            const startZ = (Math.random() - 0.5) * (TANK_D - 6);
            group.position.set(startX, startY, startZ);

            // Направление
            const angle = Math.random() * Math.PI * 2;
            group.rotation.y = angle;

            group.scale.setScalar(scale || (0.6 + Math.random() * 0.6));

            scene.add(group);

            const fishData = {
                mesh: group,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                topFin: topFin,
                velocity: new THREE.Vector3(Math.cos(angle), 0, Math.sin(angle)).multiplyScalar(0.5),
                speed: 0.3 + Math.random() * 0.4,
                tailSpeed: 3 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2 + Math.random() * 2,
                wanderTimer: Math.random() * 3,
                scale: scale || (0.6 + Math.random() * 0.6)
            };

            fishArray.push(fishData);
            updateStats();
            return fishData;
        }

        // Создание 15 рыбок
        for (let i = 0; i < 15; i++) {
            createFish(i % 8, 0.6 + Math.random() * 0.6);
        }

        // === ПУЗЫРИ ===
        const bubbles = [];
        const bubbleGeo = new THREE.SphereGeometry(0.15, 8, 8);
        const bubbleMat = new THREE.MeshPhysicalMaterial({
            color: 0xaaddff,
            transparent: true,
            opacity: 0.4,
            roughness: 0,
            metalness: 0.1,
            transmission: 0.8
        });

        function createBubble() {
            const bubble = new THREE.Mesh(bubbleGeo, bubbleMat);
            bubble.position.set(
                (Math.random() - 0.5) * (TANK_W - 4),
                0.5 + Math.random() * 2,
                (Math.random() - 0.5) * (TANK_D - 4)
            );
            const data = {
                mesh: bubble,
                speed: 0.5 + Math.random() * 1.5,
                phase: Math.random() * Math.PI * 2,
                amplitude: 0.2 + Math.random() * 0.4
            };
            scene.add(bubble);
            bubbles.push(data);
            return data;
        }

        for (let i = 0; i < 30; i++) {
            createBubble();
        }

        // === СИСТЕМА КОРМА ===
        const foodArray = [];
        const foodGeo = new THREE.SphereGeometry(0.2, 8, 8);
        const foodMat = new THREE.MeshStandardMaterial({ color: 0xff8800, emissive: 0x442200, roughness: 0.5 });

        function createFood(x, y, z) {
            const food = new THREE.Mesh(foodGeo, foodMat);
            food.position.set(x, y, z);
            scene.add(food);
            const data = {
                mesh: food,
                velocity: new THREE.Vector3(0, -1, 0).multiplyScalar(0.5 + Math.random() * 0.5)
            };
            foodArray.push(data);
            updateStats();
        }

        // === RAYCASTER ДЛЯ КЛИКОВ ===
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let isDragging = false;
        let mouseDownPos = new THREE.Vector2();

        renderer.domElement.addEventListener('mousedown', (e) => {
            mouseDownPos.set(e.clientX, e.clientY);
            isDragging = false;
        });

        renderer.domElement.addEventListener('mousemove', (e) => {
            if (Math.abs(e.clientX - mouseDownPos.x) > 5 || Math.abs(e.clientY - mouseDownPos.y) > 5) {
                isDragging = true;
            }
        });

        renderer.domElement.addEventListener('mouseup', (e) => {
            if (isDragging) return;

            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            // Проверка пересечения с плоскостью воды
            const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -TANK_H * 0.7);
            const intersectPoint = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersectPoint);

            if (intersectPoint &&
                intersectPoint.x > TANK_MIN_X + 1 && intersectPoint.x < TANK_MAX_X - 1 &&
                intersectPoint.z > TANK_MIN_Z + 1 && intersectPoint.z < TANK_MAX_Z - 1) {
                createFood(intersectPoint.x, TANK_H * 0.85, intersectPoint.z);
            } else {
                // Бросаем в центр если не попали
                createFood(
                    (Math.random() - 0.5) * (TANK_W - 10),
                    TANK_H * 0.85,
                    (Math.random() - 0.5) * (TANK_D - 10)
                );
            }
        });

        // === УПРАВЛЕНИЕ ===
        let lightOn = true;

        function addFish() {
            createFish(Math.floor(Math.random() * 8), 0.6 + Math.random() * 0.6);
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
            ambientLight.intensity = lightOn ? 0.4 : 0.15;
            pointLight1.intensity = lightOn ? 0.6 : 1.2;
            pointLight2.intensity = lightOn ? 0.4 : 0.8;
        }

        function updateStats() {
            document.getElementById('fishCount').textContent = fishArray.length;
            document.getElementById('bubbleCount').textContent = bubbles.length;
            document.getElementById('foodCount').textContent = foodArray.length;
        }

        // === FPS ===
        let frameCount = 0;
        let lastFpsTime = performance.now();
        let currentFps = 60;

        // === АНИМАЦИЯ ===
        const clock = new THREE.Clock();
        let time = 0;

        function animate() {
            requestAnimationFrame(animate);

            const delta = clock.getDelta();
            time += delta;

            // FPS
            frameCount++;
            const now = performance.now();
            if (now - lastFpsTime >= 1000) {
                currentFps = frameCount;
                frameCount = 0;
                lastFpsTime = now;
                document.getElementById('fpsCounter').textContent = currentFps;
            }

            // === АНИМАЦИЯ РЫБОК ===
            for (let i = fishArray.length - 1; i >= 0; i--) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Махание хвостом
                fish.tail.rotation.z = Math.sin(time * fish.tailSpeed + fish.phase) * 0.5;
                fish.leftFin.rotation.y = 0.4 + Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.2;
                fish.rightFin.rotation.y = -0.4 - Math.sin(time * fish.tailSpeed * 0.7 + fish.phase) * 0.2;
                fish.topFin.rotation.z = -0.3 + Math.sin(time * fish.tailSpeed * 0.5 + fish.phase) * 0.1;

                // Избегание других рыбок
                let avoidForce = new THREE.Vector3();
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j].mesh.position;
                    const diff = new THREE.Vector3().subVectors(pos, other);
                    const dist = diff.length();
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        avoidForce.add(diff.normalize().multiplyScalar((fish.avoidanceRadius - dist) / fish.avoidanceRadius));
                    }
                }
                fish.velocity.add(avoidForce.multiplyScalar(0.3 * delta));

                // Отражение от стен
                const margin = 1.5;
                if (pos.x < TANK_MIN_X + margin) fish.velocity.x += (TANK_MIN_X + margin - pos.x) * 2 * delta;
                if (pos.x > TANK_MAX_X - margin) fish.velocity.x -= (pos.x - TANK_MAX_X + margin) * 2 * delta;
                if (pos.y < TANK_MIN_Y + margin) fish.velocity.y += (TANK_MIN_Y + margin - pos.y) * 2 * delta;
                if (pos.y > TANK_MAX_Y - margin) fish.velocity.y -= (pos.y - TANK_MAX_Y + margin) * 2 * delta;
                if (pos.z < TANK_MIN_Z + margin) fish.velocity.z += (TANK_MIN_Z + margin - pos.z) * 2 * delta;
                if (pos.z > TANK_MAX_Z - margin) fish.velocity.z -= (pos.z - TANK_MAX_Z + margin) * 2 * delta;

                // Случайное блуждание
                fish.wanderTimer -= delta;
                if (fish.wanderTimer <= 0) {
                    fish.wanderTimer = 2 + Math.random() * 4;
                    fish.velocity.x += (Math.random() - 0.5) * 0.3;
                    fish.velocity.y += (Math.random() - 0.5) * 0.2;
                    fish.velocity.z += (Math.random() - 0.5) * 0.3;
                }

                // Поиск корма
                fish.targetFood = null;
                let closestDist = 15;
                for (let f = 0; f < foodArray.length; f++) {
                    const fd = pos.distanceTo(foodArray[f].mesh.position);
                    if (fd < closestDist) {
                        closestDist = fd;
                        fish.targetFood = foodArray[f];
                    }
                }

                if (fish.targetFood) {
                    const toFood = new THREE.Vector3().subVectors(fish.targetFood.mesh.position, pos);
                    toFood.normalize();
                    fish.velocity.lerp(toFood.multiplyScalar(fish.speed * 1.5), 0.05);

                    // Съедание
                    if (closestDist < 0.8) {
                        scene.remove(fish.targetFood.mesh);
                        foodArray.splice(foodArray.indexOf(fish.targetFood), 1);
                        // Рост
                        fish.scale *= 1.05;
                        fish.mesh.scale.setScalar(fish.scale);
                        updateStats();
                    }
                }

                // Ограничение скорости
                const speed = fish.velocity.length();
                if (speed > fish.speed * 2) {
                    fish.velocity.normalize().multiplyScalar(fish.speed * 2);
                }

                // Обновление позиции
                pos.add(fish.velocity.clone().multiplyScalar(delta * 3));

                // Поворот в направлении движения
                if (speed > 0.01) {
                    const targetAngle = Math.atan2(fish.velocity.x, fish.velocity.z);
                    let currentAngle = fish.mesh.rotation.y;
                    let diff = targetAngle - currentAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    fish.mesh.rotation.y += diff * 3 * delta;

                    // Небольшой наклон
                    fish.mesh.rotation.z = fish.velocity.x * 0.1;
                    fish.mesh.rotation.x = fish.velocity.y * 0.05;
                }
            }

            // === АНИМАЦИЯ КОРМА ===
            for (let i = foodArray.length - 1; i >= 0; i--) {
                const food = foodArray[i];
                food.velocity.y -= 2 * delta; // Гравитация
                food.mesh.position.add(food.velocity.clone().multiplyScalar(delta));

                // Удаление при достижении дна
                if (food.mesh.position.y <= 0.3) {
                    scene.remove(food.mesh);
                    foodArray.splice(i, 1);
                    updateStats();
                }
            }

            // === АНИМАЦИЯ ПУЗЫРЕЙ ===
            for (let i = bubbles.length - 1; i >= 0; i--) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * delta;
                b.mesh.position.x += Math.sin(time * 2 + b.phase) * b.amplitude * delta;
                b.mesh.position.z += Math.cos(time * 1.5 + b.phase) * b.amplitude * delta;

                // Сброс
                if (b.mesh.position.y > TANK_H - 0.5) {
                    b.mesh.position.y = 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * (TANK_W - 4);
                    b.mesh.position.z = (Math.random() - 0.5) * (TANK_D - 4);
                }
            }

            // === АНИМАЦИЯ ВОДОРОССЕЙ ===
            for (const sw of seaweeds) {
                sw.mesh.rotation.x = Math.sin(time * sw.speed + sw.phase) * 0.08;
                sw.mesh.rotation.z = Math.cos(time * sw.speed * 0.7 + sw.phase) * 0.06;
            }

            // === АНИМАЦИЯ СВЕТА ===
            pointLight1.intensity = (lightOn ? 0.6 : 1.2) + Math.sin(time * 1.5) * 0.1;
            pointLight2.intensity = (lightOn ? 0.4 : 0.8) + Math.cos(time * 2) * 0.08;

            // Обновление контролов
            controls.update();

            renderer.render(scene, camera);
        }

        // === RESIZE ===
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Старт
        updateStats();
        animate();
    </script>
</body>
</html>
```

## Что реализовано:

### 🐠 Рыбки (15 шт.)
- Детализированная анатомия: тело, глаза с зрачками, хвост, верхний и боковые плавники
- 8 цветовых схем с индивидуальными размерами (0.6–1.2)
- Плавная анимация махания хвостом и плавниками

### 🧠 ИИ
- Избегание столкновений между рыбками
- Отражение от стенок аквариума
- Случайное блуждание
- Преследование и поедание корма
- Рост на 5% после еды

### 🌊 Окружение
- Стеклянный контейнер с wireframe-рамкой
- Песчаное дно с процедурными неровностями
- 8 деформированных камней
- 12 водорослей (TubeGeometry + CatmullRomCurve3) с покачиванием

### 💭 Пузыри (30 шт.)
- Прозрачные сферы с движением вверх и покачиванием
- Автоматический сброс на поверхность

### 🍽️ Кормление
- Клик по воде создаёт корм
- Физика падения (гравитация)
- Рыбки преследуют и едят

### 💡 Освещение
- AmbientLight + DirectionalLight с тенями (PCFSoftShadowMap, 2048²)
- 2 PointLight с пульсацией
- Переключаемый режим

### 🖥️ UI
- Glass-панели с backdrop-filter
- Градиентные кнопки с hover-эффектами
- Статистика: рыбки, пузыри, корм, FPS