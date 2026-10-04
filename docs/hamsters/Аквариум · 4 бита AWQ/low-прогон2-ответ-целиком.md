

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
            background: linear-gradient(180deg, #0a1628 0%, #0d2847 50%, #1a4a7a 100%);
        }

        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: relative;
        }

        canvas {
            display: block;
        }

        .panel {
            position: absolute;
            background: rgba(10, 25, 50, 0.75);
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

        .stats-panel {
            top: 20px;
            right: 20px;
            width: 200px;
            text-align: center;
        }

        .panel h1 {
            font-size: 22px;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #64c8ff, #a78bfa, #64c8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        .panel h2 {
            font-size: 14px;
            margin-bottom: 8px;
            color: #8bc8ff;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .instructions {
            font-size: 12px;
            line-height: 1.8;
            color: #a0c8e8;
        }

        .instructions span {
            color: #64c8ff;
            font-weight: 600;
        }

        .stats-value {
            font-size: 32px;
            font-weight: 700;
            color: #64c8ff;
            text-shadow: 0 0 20px rgba(100, 200, 255, 0.5);
            margin: 8px 0;
        }

        .stats-label {
            font-size: 11px;
            color: #7ab0d0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .fps-value {
            font-size: 18px;
            font-weight: 600;
            color: #4ade80;
            margin-top: 8px;
        }

        .buttons {
            margin-top: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn-fish {
            background: linear-gradient(135deg, #f97316, #fb923c);
            color: white;
            box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
        }

        .btn-fish:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(249, 115, 22, 0.6);
        }

        .btn-bubbles {
            background: linear-gradient(135deg, #06b6d4, #22d3ee);
            color: white;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
        }

        .btn-bubbles:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(6, 182, 212, 0.6);
        }

        .btn-light {
            background: linear-gradient(135deg, #8b5cf6, #a78bfa);
            color: white;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        }

        .btn-light:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(139, 92, 246, 0.6);
        }

        .btn-light.off {
            background: linear-gradient(135deg, #4b5563, #6b7280);
            box-shadow: 0 4px 15px rgba(75, 85, 99, 0.4);
        }

        .click-hint {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 25, 50, 0.7);
            backdrop-filter: blur(8px);
            padding: 12px 24px;
            border-radius: 30px;
            color: #a0c8e8;
            font-size: 13px;
            border: 1px solid rgba(100, 180, 255, 0.2);
            animation: pulse 2s infinite;
            z-index: 100;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        @media (max-width: 768px) {
            .info-panel {
                width: 220px;
                padding: 14px;
            }
            .stats-panel {
                width: 150px;
                padding: 14px;
            }
            .panel h1 {
                font-size: 18px;
            }
            .stats-value {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel info-panel">
        <h1>🐠 3D Аквариум</h1>
        <h2>Управление</h2>
        <div class="instructions">
            <span>ЛКМ + движение</span> — вращение<br>
            <span>ПКМ + движение</span> — панорама<br>
            <span>Колесо</span> — зум<br>
            <span>Клик</span> — покормить рыб
        </div>
        <div class="buttons">
            <button class="btn btn-fish" id="btnAddFish">+ Добавить рыбку</button>
            <button class="btn btn-bubbles" id="btnBubbles">+ Больше пузырей</button>
            <button class="btn btn-light" id="btnLight">💡 Свет: Вкл</button>
        </div>
    </div>

    <div class="panel stats-panel">
        <div class="stats-label">Рыбки</div>
        <div class="stats-value" id="fishCount">15</div>
        <div class="fps-value" id="fpsCounter">60 FPS</div>
    </div>

    <div class="click-hint" id="clickHint">🍽️ Кликните по воде чтобы покормить рыбок</div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // ============ SCENE SETUP ============
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a2040, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
        camera.position.set(0, 15, 40);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.1;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        // ============ CONTROLS ============
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 10;
        controls.maxDistance = 60;
        controls.maxPolarAngle = Math.PI / 1.8;
        controls.target.set(0, 5, 0);

        // ============ AQUARIUM DIMENSIONS ============
        const AQ_W = 36, AQ_H = 24, AQ_D = 20;
        const HALF_W = AQ_W / 2, HALF_H = AQ_H / 2, HALF_D = AQ_D / 2;

        // ============ LIGHTING ============
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffeedd, 1.2);
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

        const pointLight1 = new THREE.PointLight(0x00aaff, 0.6, 40);
        pointLight1.position.set(-10, 18, 0);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x0066ff, 0.5, 40);
        pointLight2.position.set(10, 18, -5);
        scene.add(pointLight2);

        let lightOn = true;

        // ============ GLASS TANK ============
        function createTank() {
            const group = new THREE.Group();

            // Glass walls
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0x88ccff,
                metalness: 0,
                roughness: 0.05,
                transmission: 0.95,
                thickness: 0.5,
                transparent: true,
                opacity: 0.15,
                side: THREE.DoubleSide,
                ior: 1.5
            });

            const walls = [
                { size: [AQ_W, AQ_H], pos: [0, 0, -HALF_D], rot: [0, 0, 0] },
                { size: [AQ_W, AQ_H], pos: [0, 0, HALF_D], rot: [0, 0, 0] },
                { size: [AQ_D, AQ_H], pos: [-HALF_W, 0, 0], rot: [0, Math.PI / 2, 0] },
                { size: [AQ_D, AQ_H], pos: [HALF_W, 0, 0], rot: [0, Math.PI / 2, 0] },
                { size: [AQ_W, AQ_D], pos: [0, HALF_H, 0], rot: [Math.PI / 2, 0, 0] },
                { size: [AQ_W, AQ_D], pos: [0, -HALF_H, 0], rot: [Math.PI / 2, 0, 0] }
            ];

            walls.forEach(w => {
                const geo = new THREE.PlaneGeometry(w.size[0], w.size[1]);
                const mesh = new THREE.Mesh(geo, glassMat);
                mesh.position.set(...w.pos);
                mesh.rotation.set(...w.rot);
                group.add(mesh);
            });

            // Wireframe edges
            const edgesGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(AQ_W, AQ_H, AQ_D));
            const edgesMat = new THREE.LineBasicMaterial({ color: 0x4488cc, transparent: true, opacity: 0.5 });
            const edges = new THREE.LineSegments(edgesGeo, edgesMat);
            group.add(edges);

            return group;
        }
        scene.add(createTank());

        // ============ SANDY BOTTOM ============
        function createSand() {
            const geo = new THREE.PlaneGeometry(AQ_W, AQ_D, 40, 30);
            const positions = geo.attributes.position;
            for (let i = 0; i < positions.count; i++) {
                const x = positions.getX(i);
                const y = positions.getY(i);
                const noise = Math.sin(x * 0.5) * Math.cos(y * 0.7) * 0.3 +
                              Math.sin(x * 1.2 + y * 0.8) * 0.15 +
                              Math.random() * 0.1;
                positions.setZ(i, noise);
            }
            geo.computeVertexNormals();

            const mat = new THREE.MeshStandardMaterial({
                color: 0xd4a855,
                roughness: 0.95,
                metalness: 0.0
            });

            const sand = new THREE.Mesh(geo, mat);
            sand.rotation.x = -Math.PI / 2;
            sand.position.y = -HALF_H + 0.1;
            sand.receiveShadow = true;
            return sand;
        }
        scene.add(createSand());

        // ============ ROCKS ============
        function createRocks() {
            const rocks = [];
            const rockColors = [0x666666, 0x887766, 0x556655, 0x776655, 0x445566];

            for (let i = 0; i < 8; i++) {
                const size = 0.8 + Math.random() * 1.5;
                const geo = new THREE.DodecahedronGeometry(size, 1);
                const pos = geo.attributes.position;
                for (let j = 0; j < pos.count; j++) {
                    const x = pos.getX(j);
                    const y = pos.getY(j);
                    const z = pos.getZ(j);
                    const noise = 1 + (Math.random() - 0.5) * 0.4;
                    pos.setX(j, x * noise);
                    pos.setY(j, y * noise * 0.7);
                    pos.setZ(j, z * noise);
                }
                geo.computeVertexNormals();

                const mat = new THREE.MeshStandardMaterial({
                    color: rockColors[i % rockColors.length],
                    roughness: 0.85,
                    metalness: 0.1
                });

                const rock = new THREE.Mesh(geo, mat);
                rock.position.set(
                    (Math.random() - 0.5) * (AQ_W - 4),
                    -HALF_H + 0.5 + Math.random() * 0.5,
                    (Math.random() - 0.5) * (AQ_D - 4)
                );
                rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
                rock.castShadow = true;
                rock.receiveShadow = true;
                scene.add(rock);
                rocks.push(rock);
            }
            return rocks;
        }
        const rocks = createRocks();

        // ============ SEAWEED ============
        const seaweeds = [];
        function createSeaweed() {
            const seaweedGroup = new THREE.Group();
            const colors = [0x22aa44, 0x33bb55, 0x119933, 0x44cc66, 0x228844];

            for (let i = 0; i < 12; i++) {
                const height = 3 + Math.random() * 5;
                const points = [];
                const segments = 8;
                for (let j = 0; j <= segments; j++) {
                    const t = j / segments;
                    points.push(new THREE.Vector3(
                        Math.sin(t * 3 + i) * 0.3 * t,
                        t * height,
                        Math.cos(t * 2 + i) * 0.2 * t
                    ));
                }
                const curve = new THREE.CatmullRomCurve3(points);
                const tubeGeo = new THREE.TubeGeometry(curve, 12, 0.15 + Math.random() * 0.1, 5);
                const mat = new THREE.MeshStandardMaterial({
                    color: colors[i % colors.length],
                    roughness: 0.7,
                    side: THREE.DoubleSide
                });
                const tube = new THREE.Mesh(tubeGeo, mat);
                tube.castShadow = true;

                const x = (Math.random() - 0.5) * (AQ_W - 6);
                const z = (Math.random() - 0.5) * (AQ_D - 6);
                tube.position.set(x, -HALF_H + 0.2, z);

                seaweedGroup.add(tube);
                seaweeds.push({ mesh: tube, baseRotationX: 0, baseRotationZ: 0, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 });
            }
            scene.add(seaweedGroup);
        }
        createSeaweed();

        // ============ FISH SYSTEM ============
        const fishArray = [];
        const colorSchemes = [
            { body: 0xff6600, fin: 0xffaa00, eye: 0xffffff },   // Orange
            { body: 0x0066ff, fin: 0x00aaff, eye: 0xffffff },   // Blue
            { body: 0xffcc00, fin: 0xff3300, eye: 0xffffff },   // Yellow-Red
            { body: 0x9933ff, fin: 0xcc66ff, eye: 0xffffff },   // Purple
            { body: 0xff0033, fin: 0xff6666, eye: 0xffffff },   // Red
            { body: 0x00cc66, fin: 0x66ffaa, eye: 0xffffff },   // Green
            { body: 0xff66aa, fin: 0xffaacc, eye: 0xffffff },   // Pink
            { body: 0xffaa00, fin: 0xffdd44, eye: 0xffffff }    // Gold
        ];

        function createFish(index) {
            const scheme = colorSchemes[index % colorSchemes.length];
            const scale = 0.6 + Math.random() * 0.6;
            const group = new THREE.Group();

            // Body - elongated sphere
            const bodyGeo = new THREE.SphereGeometry(1, 12, 10);
            bodyGeo.scale(1.8, 0.8, 0.7);
            const bodyMat = new THREE.MeshStandardMaterial({
                color: scheme.body,
                roughness: 0.4,
                metalness: 0.3
            });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.castShadow = true;
            group.add(body);

            // Belly (lighter)
            const bellyGeo = new THREE.SphereGeometry(0.85, 10, 8);
            bellyGeo.scale(1.6, 0.5, 0.55);
            const bellyMat = new THREE.MeshStandardMaterial({
                color: new THREE.Color(scheme.body).lerp(new THREE.Color(0xffffff), 0.4),
                roughness: 0.5,
                metalness: 0.2
            });
            const belly = new THREE.Mesh(bellyGeo, bellyMat);
            belly.position.y = -0.15;
            group.add(belly);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.18, 8, 8);
            const eyeMat = new THREE.MeshStandardMaterial({ color: scheme.eye, roughness: 0.1, metalness: 0.5 });
            const pupilGeo = new THREE.SphereGeometry(0.09, 6, 6);
            const pupilMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.1 });

            const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
            leftEye.position.set(1.2, 0.15, 0.4);
            group.add(leftEye);
            const leftPupil = new THREE.Mesh(pupilGeo, pupilMat);
            leftPupil.position.set(1.35, 0.15, 0.4);
            group.add(leftPupil);

            const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
            rightEye.position.set(1.2, 0.15, -0.4);
            group.add(rightEye);
            const rightPupil = new THREE.Mesh(pupilGeo, pupilMat);
            rightPupil.position.set(1.35, 0.15, -0.4);
            group.add(rightPupil);

            // Tail
            const tailGeo = new THREE.ConeGeometry(0.6, 1.2, 6);
            tailGeo.rotateX(Math.PI / 2);
            const tailMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.9
            });
            const tail = new THREE.Mesh(tailGeo, tailMat);
            tail.position.set(-1.8, 0, 0);
            tail.name = 'tail';
            group.add(tail);

            // Top fin
            const topFinGeo = new THREE.ConeGeometry(0.4, 0.8, 4);
            topFinGeo.rotateZ(Math.PI / 2);
            const finMat = new THREE.MeshStandardMaterial({
                color: scheme.fin,
                roughness: 0.5,
                metalness: 0.2,
                transparent: true,
                opacity: 0.8
            });
            const topFin = new THREE.Mesh(topFinGeo, finMat);
            topFin.position.set(0, 0.6, 0);
            topFin.name = 'topFin';
            group.add(topFin);

            // Left fin
            const leftFinGeo = new THREE.ConeGeometry(0.3, 0.7, 4);
            leftFinGeo.rotateX(Math.PI / 2);
            leftFinGeo.rotateZ(Math.PI / 4);
            const leftFin = new THREE.Mesh(leftFinGeo, finMat.clone());
            leftFin.position.set(0.3, -0.3, 0.5);
            leftFin.name = 'leftFin';
            group.add(leftFin);

            // Right fin
            const rightFinGeo = new THREE.ConeGeometry(0.3, 0.7, 4);
            rightFinGeo.rotateX(Math.PI / 2);
            rightFinGeo.rotateZ(-Math.PI / 4);
            const rightFin = new THREE.Mesh(rightFinGeo, finMat.clone());
            rightFin.position.set(0.3, -0.3, -0.5);
            rightFin.name = 'rightFin';
            group.add(rightFin);

            group.scale.setScalar(scale);
            group.position.set(
                (Math.random() - 0.5) * (AQ_W - 6),
                (Math.random() - 0.5) * (AQ_H - 6),
                (Math.random() - 0.5) * (AQ_D - 6)
            );

            scene.add(group);

            const fishData = {
                mesh: group,
                tail: tail,
                topFin: topFin,
                leftFin: leftFin,
                rightFin: rightFin,
                velocity: new THREE.Vector3((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 0.5, (Math.random() - 0.5) * 2),
                speed: 1.5 + Math.random() * 2,
                tailSpeed: 4 + Math.random() * 4,
                phase: Math.random() * Math.PI * 2,
                targetFood: null,
                avoidanceRadius: 2.5 + Math.random() * 1.5,
                wanderTimer: 0,
                wanderInterval: 2 + Math.random() * 4,
                currentScale: scale
            };

            fishArray.push(fishData);
            return fishData;
        }

        // Create initial 15 fish
        for (let i = 0; i < 15; i++) {
            createFish(i);
        }

        // ============ BUBBLES ============
        const bubbles = [];
        function createBubble() {
            const size = 0.1 + Math.random() * 0.25;
            const geo = new THREE.SphereGeometry(size, 8, 8);
            const mat = new THREE.MeshPhysicalMaterial({
                color: 0xaaddff,
                metalness: 0,
                roughness: 0,
                transmission: 0.9,
                transparent: true,
                opacity: 0.4,
                ior: 1.33
            });
            const bubble = new THREE.Mesh(geo, mat);
            bubble.position.set(
                (Math.random() - 0.5) * (AQ_W - 4),
                -HALF_H + Math.random() * AQ_H,
                (Math.random() - 0.5) * (AQ_D - 4)
            );
            scene.add(bubble);

            bubbles.push({
                mesh: bubble,
                speed: 0.5 + Math.random() * 1,
                swayPhase: Math.random() * Math.PI * 2,
                swayAmp: 0.3 + Math.random() * 0.5
            });
        }

        for (let i = 0; i < 30; i++) createBubble();

        // ============ FOOD SYSTEM ============
        const foodItems = [];
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const clickPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

        function createFood(position) {
            const geo = new THREE.SphereGeometry(0.2, 6, 6);
            const mat = new THREE.MeshStandardMaterial({
                color: 0xff8844,
                emissive: 0xff4400,
                emissiveIntensity: 0.3,
                roughness: 0.6
            });
            const food = new THREE.Mesh(geo, mat);
            food.position.copy(position);
            scene.add(food);

            foodItems.push({
                mesh: food,
                velocity: new THREE.Vector3(0, -1, 0),
                life: 10
            });
        }

        // ============ INTERACTION ============
        let hintTimeout;
        document.addEventListener('click', (e) => {
            if (e.target.closest('.panel') || e.target.closest('.btn')) return;

            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            // Try to intersect with tank volume
            const intersects = raycaster.intersectObjects(scene.children, true);
            let point = null;

            // Find intersection within tank bounds
            for (const hit of intersects) {
                if (hit.point.x > -HALF_W && hit.point.x < HALF_W &&
                    hit.point.y > -HALF_H && hit.point.y < HALF_H &&
                    hit.point.z > -HALF_D && hit.point.z < HALF_D) {
                    point = hit.point;
                    break;
                }
            }

            // If no direct hit, project onto center plane
            if (!point) {
                const target = new THREE.Vector3();
                raycaster.ray.intersectPlane(clickPlane, target);
                if (target && Math.abs(target.x) < HALF_W && Math.abs(target.z) < HALF_D && target.y < HALF_H) {
                    point = target;
                } else {
                    point = new THREE.Vector3(0, HALF_H - 2, 0);
                }
            }

            // Clamp to tank
            point.x = Math.max(-HALF_W + 1, Math.min(HALF_W - 1, point.x));
            point.y = Math.max(-HALF_H + 1, Math.min(HALF_H - 1, point.y));
            point.z = Math.max(-HALF_D + 1, Math.min(HALF_D - 1, point.z));

            createFood(point);

            // Hide hint after first click
            const hint = document.getElementById('clickHint');
            if (hint && !hintTimeout) {
                hintTimeout = setTimeout(() => {
                    hint.style.opacity = '0';
                    hint.style.transition = 'opacity 1s';
                    setTimeout(() => hint.remove(), 1000);
                }, 3000);
            }
        });

        // ============ UI BUTTONS ============
        document.getElementById('btnAddFish').addEventListener('click', () => {
            createFish(fishArray.length);
            updateStats();
        });

        document.getElementById('btnBubbles').addEventListener('click', () => {
            for (let i = 0; i < 10; i++) createBubble();
        });

        document.getElementById('btnLight').addEventListener('click', function () {
            lightOn = !lightOn;
            dirLight.intensity = lightOn ? 1.2 : 0.1;
            this.textContent = lightOn ? '💡 Свет: Вкл' : '💡 Свет: Выкл';
            this.classList.toggle('off', !lightOn);
        });

        function updateStats() {
            document.getElementById('fishCount').textContent = fishArray.length;
        }

        // ============ ANIMATION LOOP ============
        const clock = new THREE.Clock();
        let fpsFrames = 0;
        let fpsTime = 0;

        function animate() {
            requestAnimationFrame(animate);
            const delta = Math.min(clock.getDelta(), 0.05);
            const elapsed = clock.elapsedTime;

            // FPS counter
            fpsFrames++;
            fpsTime += delta;
            if (fpsTime >= 0.5) {
                const fps = Math.round(fpsFrames / fpsTime);
                document.getElementById('fpsCounter').textContent = fps + ' FPS';
                fpsFrames = 0;
                fpsTime = 0;
            }

            // ============ UPDATE FISH ============
            for (let i = 0; i < fishArray.length; i++) {
                const fish = fishArray[i];
                const pos = fish.mesh.position;

                // Wander
                fish.wanderTimer += delta;
                if (fish.wanderTimer > fish.wanderInterval) {
                    fish.wanderTimer = 0;
                    fish.wanderInterval = 2 + Math.random() * 4;
                    fish.velocity.x += (Math.random() - 0.5) * 1.5;
                    fish.velocity.y += (Math.random() - 0.5) * 0.5;
                    fish.velocity.z += (Math.random() - 0.5) * 1.5;
                }

                // Food seeking
                if (foodItems.length > 0) {
                    let closestFood = null;
                    let closestDist = 15;
                    for (let f = 0; f < foodItems.length; f++) {
                        const d = pos.distanceTo(foodItems[f].mesh.position);
                        if (d < closestDist) {
                            closestDist = d;
                            closestFood = foodItems[f];
                        }
                    }
                    if (closestFood) {
                        const dir = closestFood.mesh.position.clone().sub(pos).normalize();
                        fish.velocity.add(dir.multiplyScalar(3 * delta));
                        fish.targetFood = closestFood;
                    } else {
                        fish.targetFood = null;
                    }
                }

                // Collision avoidance
                for (let j = i + 1; j < fishArray.length; j++) {
                    const other = fishArray[j];
                    const diff = pos.clone().sub(other.mesh.position);
                    const dist = diff.length();
                    if (dist < fish.avoidanceRadius && dist > 0.01) {
                        const force = diff.normalize().multiplyScalar((fish.avoidanceRadius - dist) * 2 * delta);
                        fish.velocity.add(force);
                        other.velocity.sub(force);
                    }
                }

                // Wall reflection
                const margin = 1;
                if (pos.x > HALF_W - margin) fish.velocity.x -= 3 * delta;
                if (pos.x < -HALF_W + margin) fish.velocity.x += 3 * delta;
                if (pos.y > HALF_H - margin) fish.velocity.y -= 3 * delta;
                if (pos.y < -HALF_H + margin) fish.velocity.y += 3 * delta;
                if (pos.z > HALF_D - margin) fish.velocity.z -= 3 * delta;
                if (pos.z < -HALF_D + margin) fish.velocity.z += 3 * delta;

                // Speed limit
                const speed = fish.velocity.length();
                const maxSpeed = fish.speed * 2;
                if (speed > maxSpeed) {
                    fish.velocity.multiplyScalar(maxSpeed / speed);
                }

                // Damping
                fish.velocity.multiplyScalar(0.98);

                // Ensure minimum speed
                if (fish.velocity.length() < 0.3) {
                    fish.velocity.x += (Math.random() - 0.5) * 0.5;
                    fish.velocity.z += (Math.random() - 0.5) * 0.5;
                }

                // Update position
                pos.add(fish.velocity.clone().multiplyScalar(delta));

                // Clamp position
                pos.x = Math.max(-HALF_W + 0.5, Math.min(HALF_W - 0.5, pos.x));
                pos.y = Math.max(-HALF_H + 0.5, Math.min(HALF_H - 0.5, pos.y));
                pos.z = Math.max(-HALF_D + 0.5, Math.min(HALF_D - 0.5, pos.z));

                // Orient fish towards velocity
                if (fish.velocity.length() > 0.1) {
                    const lookTarget = pos.clone().add(fish.velocity);
                    fish.mesh.lookAt(lookTarget);
                }

                // Tail animation
                const tailAngle = Math.sin(elapsed * fish.tailSpeed + fish.phase) * 0.5;
                fish.tail.rotation.y = tailAngle;

                // Fin animation
                const finAngle = Math.sin(elapsed * fish.tailSpeed * 0.7 + fish.phase) * 0.3;
                fish.topFin.rotation.z = finAngle;
                fish.leftFin.rotation.x = finAngle * 0.5;
                fish.rightFin.rotation.x = -finAngle * 0.5;

                // Slight body bob
                fish.mesh.position.y += Math.sin(elapsed * 2 + fish.phase) * 0.002;
            }

            // ============ UPDATE FOOD ============
            for (let i = foodItems.length - 1; i >= 0; i--) {
                const food = foodItems[i];
                food.life -= delta;

                // Gravity
                food.velocity.y -= 3 * delta;
                food.mesh.position.add(food.velocity.clone().multiplyScalar(delta));

                // Check if eaten by fish
                let eaten = false;
                for (let f = 0; f < fishArray.length; f++) {
                    const fish = fishArray[f];
                    if (fish.mesh.position.distanceTo(food.mesh.position) < 1.0 * fish.currentScale) {
                        // Fish eats food
                        fish.currentScale *= 1.05;
                        fish.mesh.scale.setScalar(fish.currentScale);
                        eaten = true;
                        break;
                    }
                }

                // Remove if on bottom or expired
                if (eaten || food.mesh.position.y < -HALF_H + 0.3 || food.life <= 0) {
                    scene.remove(food.mesh);
                    food.mesh.geometry.dispose();
                    food.mesh.material.dispose();
                    foodItems.splice(i, 1);
                }
            }

            // ============ UPDATE BUBBLES ============
            for (let i = 0; i < bubbles.length; i++) {
                const b = bubbles[i];
                b.mesh.position.y += b.speed * delta;
                b.mesh.position.x += Math.sin(elapsed * 2 + b.swayPhase) * b.swayAmp * delta;
                b.mesh.position.z += Math.cos(elapsed * 1.5 + b.swayPhase) * b.swayAmp * delta;

                // Reset to bottom
                if (b.mesh.position.y > HALF_H - 0.5) {
                    b.mesh.position.y = -HALF_H + 0.5;
                    b.mesh.position.x = (Math.random() - 0.5) * (AQ_W - 4);
                    b.mesh.position.z = (Math.random() - 0.5) * (AQ_D - 4);
                }
            }

            // ============ UPDATE SEAWEED ============
            for (let i = 0; i < seaweeds.length; i++) {
                const s = seaweeds[i];
                s.mesh.rotation.x = Math.sin(elapsed * s.speed + s.phase) * 0.08;
                s.mesh.rotation.z = Math.cos(elapsed * s.speed * 0.7 + s.phase) * 0.06;
            }

            // ============ ANIMATE LIGHTS ============
            pointLight1.intensity = 0.5 + Math.sin(elapsed * 0.5) * 0.15;
            pointLight2.intensity = 0.4 + Math.cos(elapsed * 0.7) * 0.1;

            controls.update();
            renderer.render(scene, camera);
        }

        // ============ RESIZE ============
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
| **Рыбки** | 15 штук, 8 цветовых схем, тело + брюшко + глаза с зрачками + хвост + 3 плавника, случайный масштаб 0.6–1.2 |
| **ИИ** | Избегание столкновений, отражение от стен, случайное блуждание, преследование корма (радиус 15), рост +5% при поедании |
| **Аквариум** | Стеклянные стены (transmission 0.95), wireframe-рамка, размеры 36×24×20 |
| **Дно** | Песчаная плоскость с процедурным шумом, принимает тени |
| **Камни** | 8 деформированных додекаэдров, случайные позиции/вращения, тени |
| **Водоросли** | 12 кустов через TubeGeometry + CatmullRomCurve3, покачивание |
| **Пузыри** | 30 штук, MeshPhysicalMaterial, движение вверх + синусоидальное покачивание, сброс на дно |
| **Кормление** | Клик → корм с гравитацией, рыбы плывут к нему, съедают → рост, удаление на дне |
| **Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 PointLight с пульсацией, кнопка вкл/выкл |
| **Камера** | OrbitControls: вращение, панорама, зум 10–60, damping, ограничение polar angle |
| **UI** | Glass-панели, статистика (рыбки + FPS), 3 кнопки с hover-эффектами, подсказка о клике |
| **Эффекты** | FogExp2, ACESFilmicToneMapping, адаптивный resize |

Просто сохраните как `.html` и откройте в браузере — всё работает без сборки.