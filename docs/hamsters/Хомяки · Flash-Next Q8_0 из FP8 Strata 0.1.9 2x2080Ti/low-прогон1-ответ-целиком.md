```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Low-Poly Hamster Playground</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { overflow: hidden; background: #1a1a2e; font-family: 'Segoe UI', sans-serif; }
        canvas { display: block; }
        #ui {
            position: absolute; top: 20px; left: 20px;
            color: #fff; background: rgba(0,0,0,0.5);
            padding: 12px 18px; border-radius: 12px;
            font-size: 14px; pointer-events: none;
        }
        #ui h1 { font-size: 18px; margin-bottom: 4px; }
        #ui p { opacity: 0.7; font-size: 12px; }
    </style>
</head>
<body>
    <div id="ui">
        <h1>🐹 Hamster Playground</h1>
        <p>Drag to rotate • Scroll to zoom</p>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    // ============ SETUP ============
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB);
    scene.fog = new THREE.Fog(0x87CEEB, 25, 50);

    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(8, 7, 10);
    camera.lookAt(0, 0.5, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    // ============ ORBIT CONTROLS (inline) ============
    let isDragging = false, prevMouse = { x: 0, y: 0 };
    let spherical = { theta: 0.8, phi: 1.0, radius: 14 };

    function updateCamera() {
        camera.position.x = spherical.radius * Math.sin(spherical.phi) * Math.sin(spherical.theta);
        camera.position.y = spherical.radius * Math.cos(spherical.phi);
        camera.position.z = spherical.radius * Math.sin(spherical.phi) * Math.cos(spherical.theta);
        camera.lookAt(0, 0.5, 0);
    }
    updateCamera();

    renderer.domElement.addEventListener('mousedown', e => { isDragging = true; prevMouse = { x: e.clientX, y: e.clientY }; });
    window.addEventListener('mouseup', () => isDragging = false);
    window.addEventListener('mousemove', e => {
        if (!isDragging) return;
        spherical.theta -= (e.clientX - prevMouse.x) * 0.005;
        spherical.phi = Math.max(0.3, Math.min(1.4, spherical.phi + (e.clientY - prevMouse.y) * 0.005));
        prevMouse = { x: e.clientX, y: e.clientY };
        updateCamera();
    });
    renderer.domElement.addEventListener('wheel', e => {
        spherical.radius = Math.max(6, Math.min(25, spherical.radius + e.deltaY * 0.01));
        updateCamera();
    });
    renderer.domElement.addEventListener('touchstart', e => { isDragging = true; prevMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY }; });
    renderer.domElement.addEventListener('touchend', () => isDragging = false);
    renderer.domElement.addEventListener('touchmove', e => {
        if (!isDragging) return;
        spherical.theta -= (e.touches[0].clientX - prevMouse.x) * 0.005;
        spherical.phi = Math.max(0.3, Math.min(1.4, spherical.phi + (e.touches[0].clientY - prevMouse.y) * 0.005));
        prevMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
        updateCamera();
    });

    // ============ LIGHTING ============
    const ambientLight = new THREE.AmbientLight(0xfff5e6, 0.6);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 5);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(2048, 2048);
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 30;
    dirLight.shadow.camera.left = -10;
    dirLight.shadow.camera.right = 10;
    dirLight.shadow.camera.top = 10;
    dirLight.shadow.camera.bottom = -10;
    scene.add(dirLight);

    const fillLight = new THREE.DirectionalLight(0x88aaff, 0.3);
    fillLight.position.set(-3, 4, -5);
    scene.add(fillLight);

    // ============ MATERIALS ============
    const mat = (color) => new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0.1 });

    // ============ FLOOR / TRAY ============
    const trayGeo = new THREE.CylinderGeometry(5, 5.2, 0.4, 32);
    const tray = new THREE.Mesh(trayGeo, mat(0xf4e4c1));
    tray.position.y = -0.2;
    tray.receiveShadow = true;
    scene.add(tray);

    // Bedding bumps
    for (let i = 0; i < 40; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = Math.random() * 4.5;
        const bump = new THREE.Mesh(
            new THREE.SphereGeometry(0.1 + Math.random() * 0.15, 6, 4),
            mat(0xe8d5a3)
        );
        bump.position.set(Math.cos(angle) * r, 0.02, Math.sin(angle) * r);
        bump.scale.y = 0.4;
        bump.receiveShadow = true;
        scene.add(bump);
    }

    // ============ CAGE ============
    const cageGroup = new THREE.Group();
    const barMat = mat(0x6b8cce);
    const numBars = 24;
    const cageRadius = 5.1;
    const cageHeight = 4;

    for (let i = 0; i < numBars; i++) {
        const angle = (i / numBars) * Math.PI * 2;
        const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, cageHeight, 6), barMat);
        bar.position.set(Math.cos(angle) * cageRadius, cageHeight / 2, Math.sin(angle) * cageRadius);
        bar.castShadow = true;
        cageGroup.add(bar);
    }

    // Top ring
    const topRing = new THREE.Mesh(new THREE.TorusGeometry(cageRadius, 0.06, 8, numBars), barMat);
    topRing.position.y = cageHeight;
    topRing.rotation.x = Math.PI / 2;
    cageGroup.add(topRing);

    // Middle ring
    const midRing = new THREE.Mesh(new THREE.TorusGeometry(cageRadius, 0.05, 8, numBars), barMat);
    midRing.position.y = cageHeight * 0.5;
    midRing.rotation.x = Math.PI / 2;
    cageGroup.add(midRing);

    // Bottom ring
    const botRing = new THREE.Mesh(new THREE.TorusGeometry(cageRadius, 0.06, 8, numBars), barMat);
    botRing.position.y = 0.05;
    botRing.rotation.x = Math.PI / 2;
    cageGroup.add(botRing);

    scene.add(cageGroup);

    // ============ HAMSTER WHEEL ============
    const wheelGroup = new THREE.Group();
    const wheelColor = mat(0xff6b9d);
    const wheelRadius = 1.4;

    // Outer ring
    const outerRing = new THREE.Mesh(new THREE.TorusGeometry(wheelRadius, 0.12, 8, 24), wheelColor);
    wheelGroup.add(outerRing);

    // Inner ring
    const innerRing = new THREE.Mesh(new THREE.TorusGeometry(wheelRadius * 0.3, 0.08, 6, 16), mat(0xffb3c9));
    wheelGroup.add(innerRing);

    // Spokes
    for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2;
        const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, wheelRadius * 0.7, 4), wheelColor);
        spoke.position.set(Math.cos(angle) * wheelRadius * 0.65, Math.sin(angle) * wheelRadius * 0.65, 0);
        spoke.rotation.z = angle + Math.PI / 2;
        wheelGroup.add(spoke);
    }

    // Running surface (steps)
    for (let i = 0; i < 16; i++) {
        const angle = (i / 16) * Math.PI * 2;
        const step = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.06, 0.5), mat(0xffd4e0));
        step.position.set(Math.cos(angle) * (wheelRadius - 0.15), Math.sin(angle) * (wheelRadius - 0.15), 0);
        step.rotation.z = angle;
        wheelGroup.add(step);
    }

    // Stand
    const standMat = mat(0x8b7355);
    const stand1 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.2, 6), standMat);
    stand1.position.set(0, -wheelRadius - 0.5, -0.4);
    stand1.rotation.x = 0.1;
    wheelGroup.add(stand1);
    const stand2 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.2, 6), standMat);
    stand2.position.set(0, -wheelRadius - 0.5, 0.4);
    stand2.rotation.x = -0.1;
    wheelGroup.add(stand2);

    wheelGroup.position.set(3.2, wheelRadius + 0.2, -2.5);
    wheelGroup.rotation.y = 0.5;
    scene.add(wheelGroup);

    // Axle
    const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.2, 8), mat(0xcccccc));
    axle.position.copy(wheelGroup.position);
    axle.rotation.x = Math.PI / 2;
    axle.rotation.z = 0.5;
    scene.add(axle);

    // ============ FOOD BOWL ============
    const bowlGroup = new THREE.Group();
    const bowlOuter = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.35, 0.4, 12), mat(0xff4757));
    bowlOuter.position.y = 0.2;
    bowlGroup.add(bowlOuter);
    const bowlInner = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.3, 0.2, 12), mat(0xff6b7a));
    bowlInner.position.y = 0.35;
    bowlGroup.add(bowlInner);

    // Food pellets
    for (let i = 0; i < 8; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = Math.random() * 0.25;
        const pellet = new THREE.Mesh(new THREE.SphereGeometry(0.07, 5, 4), mat(0x8B4513));
        pellet.position.set(Math.cos(angle) * r, 0.4, Math.sin(angle) * r);
        pellet.scale.y = 0.6;
        bowlGroup.add(pellet);
    }

    bowlGroup.position.set(-2, 0, 2);
    scene.add(bowlGroup);

    // ============ TUNNEL ============
    const tunnelGroup = new THREE.Group();
    const tunnelOuter = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 2.5, 12, 1, true), mat(0x7c4dff));
    tunnelOuter.rotation.z = Math.PI / 2;
    tunnelGroup.add(tunnelOuter);
    const tunnelRim1 = new THREE.Mesh(new THREE.TorusGeometry(0.6, 0.08, 8, 12), mat(0x9c7cff));
    tunnelRim1.position.x = -1.25;
    tunnelRim1.rotation.y = Math.PI / 2;
    tunnelGroup.add(tunnelRim1);
    const tunnelRim2 = new THREE.Mesh(new THREE.TorusGeometry(0.6, 0.08, 8, 12), mat(0x9c7cff));
    tunnelRim2.position.x = 1.25;
    tunnelRim2.rotation.y = Math.PI / 2;
    tunnelGroup.add(tunnelRim2);

    tunnelGroup.position.set(-1, 0.6, -3);
    tunnelGroup.rotation.y = 0.8;
    scene.add(tunnelGroup);

    // ============ WATER BOTTLE ============
    const bottleGroup = new THREE.Group();
    const bottle = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 1.2, 8), mat(0x4fc3f7));
    bottle.position.y = 1;
    bottleGroup.add(bottle);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 0.2, 8), mat(0xffa726));
    cap.position.y = 1.7;
    bottleGroup.add(cap);
    const spout = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.4, 6), mat(0xcccccc));
    spout.position.set(0, 0.3, 0);
    bottleGroup.add(spout);
    bottleGroup.position.set(4.5, 0.5, 1);
    scene.add(bottleGroup);

    // ============ HAMSTER FACTORY ============
    const hamsterColors = [0xf5deb3, 0xdaa520, 0xffffff, 0x808080, 0xd2691e];
    const hamsters = [];

    function createHamster(color, x, z) {
        const group = new THREE.Group();
        const bodyMat = mat(color);

        // Body
        const body = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 6), bodyMat);
        body.scale.set(1.2, 0.9, 1);
        body.position.y = 0.3;
        body.castShadow = true;
        group.add(body);

        // Head
        const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), bodyMat);
        head.position.set(0.35, 0.4, 0);
        head.castShadow = true;
        group.add(head);

        // Ears
        const earMat = mat(0xffb6c1);
        const ear1 = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 5), earMat);
        ear1.position.set(0.3, 0.62, -0.1);
        group.add(ear1);
        const ear2 = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 5), earMat);
        ear2.position.set(0.3, 0.62, 0.1);
        group.add(ear2);

        // Eyes
        const eyeMat = mat(0x1a1a1a);
        const eye1 = new THREE.Mesh(new THREE.SphereGeometry(0.04, 6, 5), eyeMat);
        eye1.position.set(0.52, 0.45, -0.08);
        group.add(eye1);
        const eye2 = new THREE.Mesh(new THREE.SphereGeometry(0.04, 6, 5), eyeMat);
        eye2.position.set(0.52, 0.45, 0.08);
        group.add(eye2);

        // Eye shine
        const shineMat = mat(0xffffff);
        const shine1 = new THREE.Mesh(new THREE.SphereGeometry(0.015, 4, 4), shineMat);
        shine1.position.set(0.545, 0.47, -0.07);
        group.add(shine1);
        const shine2 = new THREE.Mesh(new THREE.SphereGeometry(0.015, 4, 4), shineMat);
        shine2.position.set(0.545, 0.47, 0.09);
        group.add(shine2);

        // Nose
        const nose = new THREE.Mesh(new THREE.SphereGeometry(0.035, 5, 4), mat(0xff69b4));
        nose.position.set(0.57, 0.38, 0);
        group.add(nose);

        // Cheeks
        const cheekMat = mat(0xffccaa);
        const cheek1 = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 5), cheekMat);
        cheek1.position.set(0.45, 0.32, -0.12);
        group.add(cheek1);
        const cheek2 = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 5), cheekMat);
        cheek2.position.set(0.45, 0.32, 0.12);
        group.add(cheek2);

        // Legs
        const legMat = mat(0xdaa520);
        const legs = [];
        const legPositions = [
            { x: 0.2, z: -0.15 }, { x: 0.2, z: 0.15 },
            { x: -0.2, z: -0.15 }, { x: -0.2, z: 0.15 }
        ];
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.04, 0.15, 5), legMat);
            leg.position.set(pos.x, 0.08, pos.z);
            group.add(leg);
            legs.push(leg);
        });

        // Tail
        const tail = new THREE.Mesh(new THREE.SphereGeometry(0.05, 5, 4), bodyMat);
        tail.position.set(-0.42, 0.25, 0);
        group.add(tail);

        // Belly (lighter)
        const belly = new THREE.Mesh(new THREE.SphereGeometry(0.28, 7, 5), mat(0xfff8dc));
        belly.scale.set(1.1, 0.7, 0.9);
        belly.position.set(0, 0.22, 0);
        group.add(belly);

        group.position.set(x, 0, z);
        scene.add(group);

        return {
            mesh: group,
            legs: legs,
            state: 'idle',
            stateTimer: Math.random() * 3,
            direction: Math.random() * Math.PI * 2,
            speed: 0.015 + Math.random() * 0.01,
            targetPos: null,
            bobPhase: Math.random() * Math.PI * 2,
            color: color
        };
    }

    // Create hamsters
    for (let i = 0; i < 5; i++) {
        const angle = (i / 5) * Math.PI * 2 + Math.random() * 0.5;
        const r = 1.5 + Math.random() * 2;
        hamsters.push(createHamster(hamsterColors[i], Math.cos(angle) * r, Math.sin(angle) * r));
    }

    // ============ DECORATIONS ============
    // Small wood shavings / toys scattered around
    for (let i = 0; i < 15; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = 1 + Math.random() * 3.5;
        const shaving = new THREE.Mesh(
            new THREE.BoxGeometry(0.15 + Math.random() * 0.2, 0.03, 0.05),
            mat(0xdeb887)
        );
        shaving.position.set(Math.cos(angle) * r, 0.02, Math.sin(angle) * r);
        shaving.rotation.y = Math.random() * Math.PI;
        scene.add(shaving);
    }

    // Small colorful ball toy
    const ballToy = new THREE.Mesh(new THREE.SphereGeometry(0.15, 8, 6), mat(0x4ecdc4));
    ballToy.position.set(1.5, 0.15, 2.5);
    ballToy.castShadow = true;
    scene.add(ballToy);

    // Another toy - small star
    const starShape = new THREE.Shape();
    for (let i = 0; i < 5; i++) {
        const angle = (i / 5) * Math.PI * 2 - Math.PI / 2;
        const outerX = Math.cos(angle) * 0.2;
        const outerY = Math.sin(angle) * 0.2;
        const innerAngle = angle + Math.PI / 5;
        const innerX = Math.cos(innerAngle) * 0.08;
        const innerY = Math.sin(innerAngle) * 0.08;
        if (i === 0) starShape.moveTo(outerX, outerY);
        else starShape.lineTo(outerX, outerY);
        starShape.lineTo(innerX, innerY);
    }
    starShape.closePath();
    const starGeo = new THREE.ExtrudeGeometry(starShape, { depth: 0.05, bevelEnabled: false });
    const star = new THREE.Mesh(starGeo, mat(0xffd700));
    star.position.set(-3, 0.1, 0.5);
    star.rotation.x = -Math.PI / 2;
    scene.add(star);

    // ============ HAMSTER BEHAVIOR ============
    const CAGE_RADIUS = 4.5;
    const WHEEL_POS = new THREE.Vector3(3.2, 0, -2.5);
    const BOWL_POS = new THREE.Vector3(-2, 0, 2);

    function updateHamster(h, dt) {
        h.stateTimer -= dt;

        // State transitions
        if (h.stateTimer <= 0) {
            const rand = Math.random();
            if (h.state === 'idle') {
                if (rand < 0.4) {
                    h.state = 'walking';
                    h.direction = Math.random() * Math.PI * 2;
                    h.stateTimer = 2 + Math.random() * 3;
                } else if (rand < 0.6) {
                    h.state = 'going_to_wheel';
                    h.targetPos = WHEEL_POS.clone();
                    h.stateTimer = 6;
                } else if (rand < 0.8) {
                    h.state = 'going_to_bowl';
                    h.targetPos = BOWL_POS.clone();
                    h.stateTimer = 6;
                } else {
                    h.state = 'idle';
                    h.stateTimer = 1 + Math.random() * 2;
                }
            } else if (h.state === 'walking') {
                h.state = 'idle';
                h.stateTimer = 0.5 + Math.random() * 2;
            } else if (h.state === 'running_wheel') {
                h.state = 'idle';
                h.stateTimer = 1 + Math.random() * 2;
            } else if (h.state === 'eating') {
                h.state = 'idle';
                h.stateTimer = 1 + Math.random() * 2;
            } else if (h.state === 'going_to_wheel' || h.state === 'going_to_bowl') {
                h.state = 'idle';
                h.stateTimer = 0.5;
            }
        }

        const pos = h.mesh.position;

        if (h.state === 'walking') {
            // Turn slightly randomly
            h.direction += (Math.random() - 0.5) * 0.1;
            pos.x += Math.cos(h.direction) * h.speed;
            pos.z += Math.sin(h.direction) * h.speed;

            // Stay in cage
            const dist = Math.sqrt(pos.x * pos.x + pos.z * pos.z);
            if (dist > CAGE_RADIUS) {
                h.direction = Math.atan2(-pos.z, -pos.x) + (Math.random() - 0.5) * 0.5;
                pos.x = Math.cos(Math.atan2(pos.z, pos.x)) * CAGE_RADIUS;
                pos.z = Math.sin(Math.atan2(pos.z, pos.x)) * CAGE_RADIUS;
            }

            // Face direction of movement
            h.mesh.rotation.y = -h.direction + Math.PI / 2;

            // Leg animation
            h.bobPhase += dt * 12;
            h.legs.forEach((leg, i) => {
                leg.position.y = 0.08 + Math.sin(h.bobPhase + i * Math.PI) * 0.03;
            });

        } else if (h.state === 'going_to_wheel') {
            const target = WHEEL_POS.clone();
            const dx = target.x - pos.x;
            const dz = target.z - pos.z;
            const dist = Math.sqrt(dx * dx + dz * dz);

            if (dist < 0.5) {
                h.state = 'running_wheel';
                h.stateTimer = 3 + Math.random() * 4;
            } else {
                h.direction = Math.atan2(dz, dx);
                pos.x += Math.cos(h.direction) * h.speed * 1.5;
                pos.z += Math.sin(h.direction) * h.speed * 1.5;
                h.mesh.rotation.y = -h.direction + Math.PI / 2;
                h.bobPhase += dt * 14;
                h.legs.forEach((leg, i) => {
                    leg.position.y = 0.08 + Math.sin(h.bobPhase + i * Math.PI) * 0.04;
                });
            }

        } else if (h.state === 'running_wheel') {
            // Snap to wheel position and rotate
            const wheelAngle = performance.now() * 0.003;
            pos.x = WHEEL_POS.x + Math.cos(wheelAngle) * 0.3;
            pos.z = WHEEL_POS.z + Math.sin(wheelAngle) * 0.3;
            pos.y = Math.max(0, Math.sin(wheelAngle) * 0.8);
            h.mesh.rotation.y = -wheelAngle + Math.PI;

            // Spin the wheel
            wheelGroup.children.forEach(child => {
                if (child !== stand1 && child !== stand2) {
                    // We'll rotate the whole inner part separately
                }
            });

            h.bobPhase += dt * 16;
            h.legs.forEach((leg, i) => {
                leg.position.y = 0.08 + Math.sin(h.bobPhase + i * Math.PI) * 0.05;
            });

        } else if (h.state === 'going_to_bowl') {
            const target = BOWL_POS.clone();
            const dx = target.x - pos.x;
            const dz = target.z - pos.z;
            const dist = Math.sqrt(dx * dx + dz * dz);

            if (dist < 0.6) {
                h.state = 'eating';
                h.stateTimer = 3 + Math.random() * 3;
            } else {
                h.direction = Math.atan2(dz, dx);
                pos.x += Math.cos(h.direction) * h.speed * 1.2;
                pos.z += Math.sin(h.direction) * h.speed * 1.2;
                h.mesh.rotation.y = -h.direction + Math.PI / 2;
                h.bobPhase += dt * 10;
                h.legs.forEach((leg, i) => {
                    leg.position.y = 0.08 + Math.sin(h.bobPhase + i * Math.PI) * 0.03;
                });
            }

        } else if (h.state === 'eating') {
            // Face the bowl and bob head
            h.mesh.rotation.y = Math.atan2(-(BOWL_POS.z - pos.z), -(BOWL_POS.x - pos.x)) + Math.PI / 2;
            h.bobPhase += dt * 8;
            pos.y = Math.sin(h.bobPhase) * 0.02;
            // Reset legs
            h.legs.forEach(leg => { leg.position.y = 0.08; });

        } else {
            // Idle - gentle bobbing
            h.bobPhase += dt * 2;
            pos.y = Math.sin(h.bobPhase) * 0.015;
            h.legs.forEach(leg => { leg.position.y = 0.08; });

            // Occasionally look around
            if (Math.random() < 0.01) {
                h.mesh.rotation.y += (Math.random() - 0.5) * 0.5;
            }
        }
    }

    // ============ ANIMATION LOOP ============
    let lastTime = performance.now();
    let wheelRotation = 0;

    function animate() {
        requestAnimationFrame(animate);

        const now = performance.now();
        const dt = Math.min((now - lastTime) / 1000, 0.05);
        lastTime = now;

        // Check if any hamster is running on wheel
        let wheelActive = false;
        hamsters.forEach(h => {
            if (h.state === 'running_wheel') wheelActive = true;
            updateHamster(h, dt);
        });

        // Rotate wheel when active
        if (wheelActive) {
            wheelRotation += dt * 4;
        } else {
            wheelRotation += dt * 0.2; // Slow idle spin
        }

        // Apply wheel rotation (rotate the torus and steps around z-axis)
        outerRing.rotation.z = wheelRotation;
        innerRing.rotation.z = wheelRotation;
        wheelGroup.children.forEach(child => {
            if (child.geometry && child.geometry.type === 'TorusGeometry') {
                child.rotation.z = wheelRotation;
            }
        });

        // Gentle camera auto-rotation when not dragging
        if (!isDragging) {
            spherical.theta += dt * 0.05;
            updateCamera();
        }

        // Ball toy gentle roll
        ballToy.position.x = 1.5 + Math.sin(now * 0.001) * 0.1;
        ballToy.rotation.z += dt * 0.5;

        renderer.render(scene, camera);
    }

    animate();

    // ============ RESIZE ============
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    </script>
</body>
</html>
```

This creates a complete **Low-Poly Hamster Playground** with:

### 🐹 Scene Elements
- **5 cute hamsters** in different colors (cream, golden, white, gray, brown) with round bodies, tiny ears, shiny eyes, pink noses, and chubby cheeks
- **Circular wire cage** with vertical bars and horizontal rings
- **Sand-colored tray/floor** with scattered bedding bumps
- **Running wheel** (pink) with steps that spins when hamsters use it
- **Food bowl** (red) with pellets that attracts hungry hamsters
- **Purple tunnel**, water bottle, ball toy, and star decoration

### 🧠 Autonomous Behavior (State Machine)
Each hamster independently cycles through:
- **Idle** — gentle bobbing, occasional head turns
- **Walking** — random wandering with leg animation
- **Going to wheel → Running on wheel** — walks over, then runs while the wheel spins
- **Going to bowl → Eating** — walks to food and bobs its head

### 🎮 Controls
- **Drag** to orbit the camera
- **Scroll** to zoom in/out
- Camera slowly auto-rotates when idle