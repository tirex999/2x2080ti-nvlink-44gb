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
            background: linear-gradient(180deg, #0a1628 0%, #0d2847 100%);
        }

        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
        }

        .glass-panel {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 20px;
            color: #e0f0ff;
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
            margin-bottom: 12px;
            background: linear-gradient(135deg, #00d4ff, #7b68ee, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        #info-panel p {
            font-size: 0.82em;
            line-height: 1.6;
            opacity: 0.85;
            margin-bottom: 8px;
        }

        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 14px;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.3s ease;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .btn-fish {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            box-shadow: 0 4px 15px rgba(238, 90, 36, 0.4);
        }

        .btn-bubble {
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            box-shadow: 0 4px 15px rgba(9, 132, 227, 0.4);
        }

        .btn-light {
            background: linear-gradient(135deg, #fdcb6e, #f39c12);
            box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4);
        }

        .btn:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
        }

        .btn:active {
            transform: translateY(0) scale(0.98);
        }

        #stats-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
            min-width: 160px;
        }

        #stats-panel h3 {
            font-size: 0.9em;
            margin-bottom: 10px;
            color: #74b9ff;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            font-size: 0.82em;
        }

        .stat-value {
            font-weight: 700;
            color: #00d4ff;
        }

        #food-hint {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 100;
            padding: 10px 24px;
            font-size: 0.85em;
            opacity: 0.7;
            transition: opacity 0.5s;
        }

        @media (max-width: 768px) {
            #info-panel {
                max-width: 200px;
                padding: 14px;
            }
            #info-panel h1 {
                font-size: 1.1em;
            }
            #stats-panel {
                padding: 14px;
                min-width: 130px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="info-panel" class="glass-panel">
        <h1>🐠 3D Аквариум</h1>
        <p>🖱️ ЛКМ — вращение камеры</p>
        <p>🖱️ ПКМ — панорамирование</p>
        <p>⚙️ Колесо — масштаб</p>
        <p>👆 Клик по воде — кормление</p>
        <div class="btn-group">
            <button class="btn btn-fish" onclick="addFish()">🐟 Добавить рыбку</button>
            <button class="btn btn-bubble" onclick="addBubbles()">💨 Больше пузырей</button>
            <button class="btn btn-light" onclick="toggleLight()">💡 Свет вкл/выкл</button>
        </div>
    </div>

    <div id="stats-panel" class="glass-panel">
        <h3>📊 Статистика</h3>
        <div class="stat-row"><span>Рыбки:</span><span class="stat-value" id="fish-count">15</span></div>
        <div class="stat-row"><span>Пузыри:</span><span class="stat-value" id="bubble-count">30</span></div>
        <div class="stat-row"><span>Корм:</span><span class="stat-value" id="food-count">0</span></div>
        <div class="stat-row"><span>FPS:</span><span class="stat-value" id="fps-counter">60</span></div>
    </div>

    <div id="food-hint" class="glass-panel">💡 Кликните по аквариуму, чтобы покормить рыбок!</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // === GLOBAL VARIABLES ===
        let scene, camera, renderer, controls;
        let fishArray = [];
        let bubbleArray = [];
        let foodArray = [];
        let seaweedArray = [];
        let raycaster, mouse;
        let clock;
        let dirLight;
        let lightOn = true;
        let frameCount = 0;
        let lastTime = performance.now();
        let fps = 60;

        const AQUARIUM = { width: 36, height: 24, depth: 20 };
        const FISH_COLORS = [
            { body: 0xff6b35, fin: 0xff9f1c },   // оранжевая
            { body: 0x2e86de, fin: 0x54a0ff },   // синяя
            { body: 0xffc312, fin: 0xff4757 },   // желто-красная
            { body: 0x8854d0, fin: 0xa29bfe },   // фиолетовая
            { body: 0xe74c3c, fin: 0xff7675 },   // красная
            { body: 0x10ac84, fin: 0x1dd1a1 },   // зеленая
            { body: 0xff6b81, fin: 0xffa8b8 },   // розовая
            { body: 0xf9ca24, fin: 0xffd32a }    // золотая
        ];

        // === INITIALIZATION ===
        function init() {
            clock = new THREE.Clock();
            raycaster = new THREE.Raycaster();
            mouse = new THREE.Vector2();

            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1628);
            scene.fog = new THREE.FogExp2(0x0a2a4a, 0.008);

            // Camera
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
            camera.position.set(30, 15, 30);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.08;
            controls.minDistance = 10;
            controls.maxDistance = 60;
            controls.maxPolarAngle = Math.PI / 1.8;
            controls.target.set(0, 2, 0);

            // Lighting
            setupLighting();

            // Aquarium
            createAquarium();

            // Fish
            for (let i = 0; i < 15; i++) {
                createFish();
            }

            // Bubbles
            for (let i = 0; i < 30; i++) {
                createBubble();
            }

            // Events
            window.addEventListener('resize', onResize);
            renderer.domElement.addEventListener('click', onClick);

            // Hide hint after 5 seconds
            setTimeout(() => {
                document.getElementById('food-hint').style.opacity = '0';
            }, 6000);

            animate();
        }

        // === LIGHTING ===
        function setupLighting() {
            const ambient = new THREE.AmbientLight(0x404040, 0.4);
            scene.add(ambient);

            dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(15, 25, 10);
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
            pointLight1.position.set(-10, 8, -5);
            scene.add(pointLight1);

            const pointLight2 = new THREE.PointLight(0x0066ff, 0.4, 35);
            pointLight2.position.set(10, 5, 8);
            scene.add(pointLight2);
        }

        // === AQUARIUM ===
        function createAquarium() {
            // Glass walls
            const glassMaterial = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                transparent: true,
                opacity: 0.15,
                transmission: 0.95,
                roughness: 0.05,
                metalness: 0,
                side: THREE.DoubleSide
            });

            // Bottom glass (sand floor)
            const sandGeo = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.depth);
            const sandMat = new THREE.MeshStandardMaterial({
                color: 0xd4a574,
                roughness: 0.9,
                metalness: 0
            });
            // Add procedural bumps to sand
            const positions = sandGeo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                positions.setZ(i, Math.random() * 0.3 - 0.15);
            }
            sandGeo.computeVertexNormals();
            const sand = new THREE.Mesh(sandGeo, sandMat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = -AQUARIUM.height / 2 + 0.5;
            sand.receiveShadow = true;
            scene.add(sand);

            // Glass walls (4 sides + top wireframe)
            const w = AQUARIUM.width, h = AQUARIUM.height, d = AQUARIUM.depth;
            const wallConfigs = [
                { size: [w, h], pos: [0, 0, -d/2], rot: [0, 0, 0] },
                { size: [w, h], pos: [0, 0, d/2], rot: [0, 0, 0] },
                { size: [d, h], pos: [-w/2, 0, 0], rot: [0, Math.PI/2, 0] },
                { size: [d, h], pos: [w/2, 0, 0], rot: [0, Math.PI/2, 0] }
            ];

            wallConfigs.forEach(cfg => {
                const geo = new THREE.PlaneGeometry(cfg.size[0], cfg.size[1]);
                const wall = new THREE.Mesh(geo, glassMaterial);
                wall.position.set(...cfg.pos);
                wall.rotation.set(...cfg.rot);
                scene.add(wall);
            });

            // Wireframe edges
            const boxGeo = new THREE.BoxGeometry(w, h, d);
            const edges = new THREE.EdgesGeometry(boxGeo);
            const lineMat = new THREE.LineBasicMaterial({ color: 0x4488aa, transparent: true, opacity: 0.5 });
            const wireframe = new THREE.LineSegments(edges, lineMat);
            scene.add(wireframe);

            // Rocks
            for (let i = 0; i < 8; i++) {
                createRock();
            }

            // Seaweed
            for (let i = 0; i < 12; i++) {
                createSeaweed();
            }
        }

        function createRock() {
            const geo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 0.8, 1);
            const positions = geo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                positions.setX(i, positions.getX(i) + (Math.random() - 0.5) * 0.3);
                positions.setY(i, positions.getY(i) + (Math.random() - 0.5) * 0.3);
                positions.setZ(i, positions.getZ(i) + (Math.random() - 0.5) * 0.3);
            }
            geo.computeVertexNormals();

            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(0.08, 0.2, 0.25 + Math.random() * 0.15),
                roughness: 0.85,
                metalness: 0.1
            });

            const rock = new THREE.Mesh(geo, mat);
            rock.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                -AQUARIUM.height / 2 + 0.5 + Math.random() * 0.5,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );
            rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
            rock.castShadow = true;
            rock.receiveShadow = true;
            scene.add(rock);
        }

        function createSeaweed() {
            const height = 3 + Math.random() * 4;
            const points = [];
            for (let i = 0; i <= 10; i++) {
                const t = i / 10;
                points.push(new THREE.Vector3(
                    Math.sin(t * 2) * 0.3,
                    t * height,
                    Math.cos(t * 3) * 0.2
                ));
            }

            const curve = new THREE.CatmullRomCurve3(points);
            const geo = new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.08, 6, false);
            const hue = 0.3 + Math.random() * 0.15;
            const mat = new THREE.MeshStandardMaterial({
                color: new THREE.Color().setHSL(hue, 0.7, 0.35),
                roughness: 0.7,
                side: THREE.DoubleSide
            });

            const seaweed = new THREE.Mesh(geo, mat);
            seaweed.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 6),
                -AQUARIUM.height / 2 + 0.5,
                (Math.random() - 0.5) * (AQUARIUM.depth - 6)
            );
            seaweed.castShadow = true;

            const seaweedData = {
                mesh: seaweed,
                phase: Math.random() * Math.PI * 2,
                speed: 0.5 + Math.random() * 0.8
            };
            seaweedArray.push(seaweedData);
            scene.add(seaweed);
        }

        // === FISH CREATION ===
        function createFish() {
            const colorScheme = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
            const scale = 0.6 + Math.random() * 0.6;

            const fishGroup = new THREE.Group();

            // Body
            const bodyGeo = new THREE.SphereGeometry(1, 16, 12);
            bodyGeo.scale(1.4, 0.7, 0.6);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: colorScheme.body,
                roughness: 0.3,
                metalness: 0.4,
                emissive: colorScheme.body,
                emissiveIntensity: 0.1
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            fishGroup.add(body);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
            const pupilGeo = new THREE.SphereGeometry(0.08, 8, 8);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
            leftEye.position.set(0.9, 0.2, 0.35);
            fishGroup.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(1.0, 0.2, 0.42);
            fishGroup.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
            rightEye.position.set(0.9, 0.2, -0.35);
            fishGroup.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(1.0, 0.2, -0.42);
            fishGroup.add(rightPupil);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.5, 1.2, 4);
            tailGeo.rotateZ(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                metalness: 0.2,
                transparent: true,
                opacity: 0.85,
                side: THREE.DoubleSide
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.6, 0, 0);
            tail.scale.set(1, 1.2, 0.3);
            fishGroup.add(tail);

            // Dorsal fin (top)
            const dorsalGeo = new THREE.ConeGeometry(0.4, 0.8, 3);
            const dorsalMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.75,
                side: THREE.DoubleSide
            });
            const dorsalFin = new THREE.Mesh(dorsalGeo, dorsalMat);
            dorsalFin.position.set(0.2, 0.7, 0);
            dorsalFin.scale.set(1.5, 1, 0.3);
            fishGroup.add(dorsalFin);

            // Side fins
            const finGeo = new THREE.ConeGeometry(0.3, 0.6, 3);
            const finMat = new THREE.MeshStandardMaterial({
                color: colorScheme.fin,
                roughness: 0.4,
                transparent: true,
                opacity: 0.7,
                side: THREE.DoubleSide
            });

            const leftFin = new THREE.Mesh(finGeo, finMat);
            leftFin.position.set(0.3, -0.2, 0.5);
            leftFin.rotation.x = Math.PI / 4;
            leftFin.scale.set(1, 1, 0.3);
            fishGroup.add(leftFin);

            const rightFin = new THREE.Mesh(finGeo.clone(), finMat.clone());
            rightFin.position.set(0.3, -0.2, -0.5);
            rightFin.rotation.x = -Math.PI / 4;
            rightFin.scale.set(1, 1, 0.3);
            fishGroup.add(rightFin);

            fishGroup.scale.setScalar(scale);

            // Random position inside aquarium
            const margin = 3;
            fishGroup.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - margin * 2),
                (Math.random() - 0.5) * (AQUARIUM.height - margin * 2),
                (Math.random() - 0.5) * (AQUARIUM.depth - margin * 2)
            );

            scene.add(fishGroup);

            const fish = {
                mesh: fishGroup,
                tail: tail,
                leftFin: leftFin,
                rightFin: rightFin,
                dorsalFin: dorsalFin,
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
                currentScale: scale
            };

            fishArray.push(fish);
            updateStats();
        }

        // === BUBBLES ===
        function createBubble() {
            const radius = 0.1 + Math.random() * 0.25;
            const geo = new THREE.SphereGeometry(radius, 12, 12);
            const mat = new THREE.MeshPhysicalMaterial({
                color: 0xaaddff,
                transparent: true,
                opacity: 0.4,
                transmission: 0.8,
                roughness: 0.1,
                metalness: 0,
                emissive: 0x4488aa,
                emissiveIntensity: 0.2
            });

            const bubble = new THREE.Mesh(geo, mat);
            bubble.position.set(
                (Math.random() - 0.5) * (AQUARIUM.width - 4),
                -AQUARIUM.height / 2 + Math.random() * AQUARIUM.height,
                (Math.random() - 0.5) * (AQUARIUM.depth - 4)
            );

            scene.add(bubble);
            bubbleArray.push({
                mesh: bubble,
                speed: 1 + Math.random() * 2,
                wobblePhase: Math.random() * Math.PI * 2,
                wobbleSpeed: 1 + Math.random() * 2,
                wobbleAmount: 0.3 + Math.random() * 0.5
            });
            updateStats();
        }

        // === FOOD ===
        function createFood(position) {
            const geo = new THREE.SphereGeometry(0.2, 8, 8);
            const mat = new THREE.MeshStandardMaterial({
                color: 0x8B4513,
                roughness: 0.8,
                emissive: 0x4a2500,
                emissiveIntensity: 0.3
            });

            const food = new THREE.Mesh(geo, mat);
            food.position.copy(position);
            scene.add(food);

            foodArray.push({
                mesh: food,
                velocityY: 0,
                gravity: -2,
                eaten: false
            });
            updateStats();
        }

        // === INTERACTION ===
        function onClick(event) {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            // Create an invisible plane at the center of the aquarium to find intersection
            const planeGeo = new THREE.PlaneGeometry(AQUARIUM.width, AQUARIUM.height);
            const planeMesh = new THREE.Mesh(planeGeo, new THREE.MeshBasicMaterial({ visible: false }));
            planeMesh.position.set(0, 0, 0);

            // Try to intersect with a vertical plane facing camera
            const dir = camera.getWorldDirection(new THREE.Vector3());
            planeMesh.lookAt(camera.position);
            planeMesh.updateMatrixWorld();

            const intersects = raycaster.intersectObject(planeMesh);

            if (intersects.length > 0) {
                let point = intersects[0].point.clone();
                // Clamp to aquarium bounds
                point.x = Math.max(-AQUARIUM.width / 2 + 1, Math.min(AQUARIUM.width / 2 - 1, point.x));
                point.y = Math.max(-AQUARIUM.height / 2 + 1, Math.min(AQUARIUM.height / 2 - 1, point.y));
                point.z = Math.max(-AQUARIUM.depth / 2 + 1, Math.min(AQUARIUM.depth / 2 - 1, point.z));
                createFood(point);
            } else {
                // Fallback: create food at random position near top
                createFood(new THREE.Vector3(
                    (Math.random() - 0.5) * (AQUARIUM.width - 4),
                    AQUARIUM.height / 2 - 2,
                    (Math.random() - 0.5) * (AQUARIUM.depth - 4)
                ));
            }
        }

        // === UI FUNCTIONS ===
        function addFish() {
            createFish();
        }

        function addBubbles() {
            for (let i = 0; i < 10; i++) {
                createBubble();
            }
        }

        function toggleLight() {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 0.8 : 0.1;
        }

        function updateStats() {
            document.getElementById('fish-count').textContent = fishArray.length;
            document.getElementById('bubble-count').textContent = bubbleArray.length;
            document.getElementById('food-count').textContent = foodArray.length;
        }

        // === ANIMATION LOOP ===
        function animate() {
            requestAnimationFrame(animate);

            const delta = Math.min(clock.getDelta(), 0.05);
            const time = clock.elapsedTime;

            // FPS counter
            frameCount++;
            const now = performance.now();
            if (now - lastTime >= 1000) {
                fps = frameCount;
                frameCount = 0;
                lastTime = now;
                document.getElementById('fps-counter').textContent = fps;
            }

            // Update fish
            updateFish(delta, time);

            // Update bubbles
            updateBubbles(delta, time);

            // Update food
            updateFood(delta);

            // Update seaweed
            updateSeaweed(time);

            controls.update();
            renderer.render(scene, camera);
        }

        function updateFish(delta, time) {
            const halfW = AQUARIUM.width / 2 - 2;
            const halfH = AQUARIUM.height / 2 - 2;
            const halfD = AQUARIUM.depth / 2 - 2;

            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Wandering behavior
                fish.wanderTimer += delta;
                if (fish.wanderTimer > fish.wanderInterval) {
                    fish.wanderTimer = 0;
                    fish.wanderInterval = 2 + Math.random() * 4;
                    fish.velocity.x += (Math.random() - 0.5) * 2;
                    fish.velocity.y += (Math.random() - 0.5) * 0.8;
                    fish.velocity.z += (Math.random() - 0.5) * 2;
                }

                // Food seeking
                fish.targetFood = null;
                let closestDist = 15;
                for (let f = 0; f < foodArray.length; f++) {
                    if (foodArray[f].eaten) continue;
                    const dist = pos.distanceTo(foodArray[f].mesh.position);
                    if (dist < closestDist) {
                        closestDist = dist;
                        fish.targetFood = foodArray[f];
                    }
                }

                if (fish.targetFood) {
                    const dir = new THREE.Vector3().subVectors(fish.targetFood.mesh.position, pos).normalize();
                    fish.velocity.lerp(dir.multiplyScalar(fish.speed * 2), delta * 3);

                    // Eat food
                    if (closestDist < 1.5) {
                        fish.targetFood.eaten = true;
                        scene.remove(fish.targetFood.mesh);
                        fish.currentScale *= 1.05;
                        fish.mesh.scale.setScalar(fish.currentScale);
                    }
                }

                // Avoidance
                for (let j = 0; j < fishArray.length; j++) {
                    if (i === j) continue;
                    const other = fishArray[j];
                    const dist = pos.distanceTo(other.mesh.position);
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const pushDir = new THREE.Vector3().subVectors(pos, other.mesh.position).normalize();
                        fish.velocity.add(pushDir.multiplyScalar(delta * 8 / Math.max(dist, 0.5)));
                    }
                }

                // Wall reflection (soft)
                if (pos.x > halfW) fish.velocity.x -= delta * 5;
                if (pos.x < -halfW) fish.velocity.x += delta * 5;
                if (pos.y > halfH) fish.velocity.y -= delta * 5;
                if (pos.y < -halfH) fish.velocity.y += delta * 5;
                if (pos.z > halfD) fish.velocity.z -= delta * 5;
                if (pos.z < -halfD) fish.velocity.z += delta * 5;

                // Clamp velocity
                const vel = fish.velocity.length();
                if (vel > fish.speed) {
                    fish.velocity.normalize().multiplyScalar(fish.speed);
                }

                // Apply velocity
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Hard clamp position
                pos.x = Math.max(-halfW, Math.min(halfW, pos.x));
                pos.y = Math.max(-halfH, Math.min(halfH, pos.y));
                pos.z = Math.max(-halfD, Math.min(halfD, pos.z));

                // Rotate fish to face direction of movement
                if (fish.velocity.length() > 0.1) {
                    const targetAngle = Math.atan2(fish.velocity.z, fish.velocity.x);
                    let currentAngle = fish.mesh.rotation.y;
                    let diff = targetAngle - currentAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    fish.mesh.rotation.y += diff * delta * 3;

                    // Slight pitch based on vertical velocity
                    const targetPitch = -Math.atan2(fish.velocity.y, Math.sqrt(fish.velocity.x * fish.velocity.x + fish.velocity.z * fish.velocity.z)) * 0.5;
                    fish.mesh.rotation.z += (targetPitch - fish.mesh.rotation.z) * delta * 2;
                }

                // Animate tail
                const tailAngle = Math.sin(time * fish.tailSpeed + fish.phase) * 0.5;
                fish.tail.rotation.y = tailAngle;

                // Animate fins
                const finAngle = Math.sin(time * fish.tailSpeed * 0.7 + fish.phase + 1) * 0.3;
                fish.leftFin.rotation.z = finAngle;
                fish.rightFin.rotation.z = -finAngle;
            }
        }

        function updateBubbles(delta, time) {
            for (let i = 0; i < bubbleArray.length; i++) {
                const bubble = bubbleArray[i];
                const pos = bubble.mesh.position;

                pos.y += bubble.speed * delta;

                // Wobble
                pos.x += Math.sin(time * bubble.wobbleSpeed + bubble.wobblePhase) * bubble.wobbleAmount * delta;
                pos.z += Math.cos(time * bubble.wobbleSpeed * 0.7 + bubble.wobblePhase) * bubble.wobbleAmount * delta;

                // Reset when reaching top
                if (pos.y > AQUARIUM.height / 2 - 1) {
                    pos.y = -AQUARIUM.height / 2 + 1;
                    pos.x = (Math.random() - 0.5) * (AQUARIUM.width - 4);
                    pos.z = (Math.random() - 0.5) * (AQUARIUM.depth - 4);
                }
            }
        }

        function updateFood(delta) {
            const bottomY = -AQUARIUM.height / 2 + 1;

            for (let i = foodArray.length - 1; i >= 0; i--) {
                const food = foodArray[i];
                if (food.eaten) {
                    foodArray.splice(i, 1);
                    continue;
                }

                food.velocityY += food.gravity * delta;
                food.mesh.position.y += food.velocityY * delta;

                // Remove if hits bottom
                if (food.mesh.position.y <= bottomY) {
                    scene.remove(food.mesh);
                    foodArray.splice(i, 1);
                }
            }
            updateStats();
        }

        function updateSeaweed(time) {
            for (let i = 0; i < seaweedArray.length; i++) {
                const sw = seaweedArray[i];
                sw.mesh.rotation.x = Math.sin(time * sw.speed + sw.phase) * 0.1;
                sw.mesh.rotation.z = Math.cos(time * sw.speed * 0.8 + sw.phase) * 0.08;
            }
        }

        // === RESIZE ===
        function onResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // === START ===
        init();
    </script>
</body>
</html>
```

Этот файл представляет собой полностью автономный интерактивный 3D аквариум. Вот что реализовано:

**🐠 Рыбки (15 на старте):**
- Детализированные модели с телом, глазами, зрачками, хвостом и плавниками
- 8 цветовых схем, случайный размер (0.6–1.2)
- Анимация хвоста и плавников, поворот в направлении движения

**🧠 ИИ поведение:**
- Избегание столкновений между рыбками
- Плавное отражение от стен аквариума
- Случайное блуждание с периодической сменой траектории
- Преследование корма в радиусе 15 единиц
- Рост на 5% после поедания

**🌊 Окружение:**
- Стеклянный контейнер (36×24×20) с wireframe рамкой
- Песчаное дно с процедурными неровностями
- 8 деформированных камней, 12 кустов водорослей с анимацией

**💭 Пузыри и 🍽️ Кормление:**
- 30 пузырей с покачиванием и сбросом при достижении поверхности
- Клик создаёт корм, падающий с гравитацией

**💡 Освещение и 🎮 Управление:**
- Ambient + Directional (с тенями PCFSoft) + 2 PointLight
- OrbitControls с damping, зумом и ограничениями
- Glass UI панель со статистикой, FPS и кнопками управления