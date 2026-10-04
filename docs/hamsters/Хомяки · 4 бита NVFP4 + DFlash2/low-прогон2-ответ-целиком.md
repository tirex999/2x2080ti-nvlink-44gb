

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
        #info {
            position: absolute;
            top: 16px;
            left: 16px;
            color: #fff;
            background: rgba(0,0,0,0.5);
            padding: 12px 18px;
            border-radius: 10px;
            font-size: 14px;
            line-height: 1.6;
            pointer-events: none;
        }
        #info h1 { font-size: 18px; margin-bottom: 4px; color: #ffd93d; }
        #info span { color: #a8e6cf; }
    </style>
</head>
<body>
<div id="info">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <span>Drag</span> to rotate · <span>Scroll</span> to zoom<br>
    Watch the hamsters run the wheel!
</div>

<script type="importmap">
{
    "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
    }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ─── SCENE SETUP ───────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 15, 30);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(6, 5, 8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1, 0);
controls.maxPolarAngle = Math.PI / 2.1;
controls.minDistance = 4;
controls.maxDistance = 15;

// ─── LIGHTING ──────────────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff5e6, 1.2);
dirLight.position.set(5, 8, 4);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.near = 1;
dirLight.shadow.camera.far = 20;
dirLight.shadow.camera.left = -6;
dirLight.shadow.camera.right = 6;
dirLight.shadow.camera.top = 6;
dirLight.shadow.camera.bottom = -6;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0xb8d4ff, 0.3);
fillLight.position.set(-3, 4, -2);
scene.add(fillLight);

// ─── MATERIALS ─────────────────────────────────────────────────
function mat(color, opts = {}) {
    return new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0.05, ...opts });
}

// ─── CAGE ──────────────────────────────────────────────────────
const CAGE_W = 7, CAGE_D = 5, CAGE_H = 2.5;

function buildCage() {
    const group = new THREE.Group();

    // Floor tray
    const floor = new THREE.Mesh(
        new THREE.BoxGeometry(CAGE_W, 0.2, CAGE_D),
        mat(0xd4a574)
    );
    floor.position.y = 0.1;
    floor.receiveShadow = true;
    group.add(floor);

    // Bedding layer
    const bedding = new THREE.Mesh(
        new THREE.BoxGeometry(CAGE_W - 0.3, 0.1, CAGE_D - 0.3),
        mat(0xf5deb3)
    );
    bedding.position.y = 0.25;
    bedding.receiveShadow = true;
    group.add(bedding);

    // Walls (semi-transparent)
    const wallMat = new THREE.MeshPhysicalMaterial({
        color: 0xaaddff, transparent: true, opacity: 0.15,
        roughness: 0.1, metalness: 0
    });

    const wallGeo = new THREE.PlaneGeometry(CAGE_W, CAGE_H);
    const wallGeoSide = new THREE.PlaneGeometry(CAGE_D, CAGE_H);

    // Back wall
    const backWall = new THREE.Mesh(wallGeo, wallMat);
    backWall.position.set(0, CAGE_H / 2 + 0.2, -CAGE_D / 2);
    group.add(backWall);

    // Left wall
    const leftWall = new THREE.Mesh(wallGeoSide, wallMat);
    leftWall.position.set(-CAGE_W / 2, CAGE_H / 2 + 0.2, 0);
    leftWall.rotation.y = Math.PI / 2;
    group.add(leftWall);

    // Right wall
    const rightWall = new THREE.Mesh(wallGeoSide, wallMat);
    rightWall.position.set(CAGE_W / 2, CAGE_H / 2 + 0.2, 0);
    rightWall.rotation.y = -Math.PI / 2;
    group.add(rightWall);

    // Bars
    const barMat = mat(0xcccccc, { metalness: 0.6, roughness: 0.3 });
    const barGeo = new THREE.CylinderGeometry(0.03, 0.03, CAGE_H, 6);

    // Front bars
    for (let i = 0; i <= 14; i++) {
        const x = -CAGE_W / 2 + (CAGE_W / 14) * i;
        const bar = new THREE.Mesh(barGeo, barMat);
        bar.position.set(x, CAGE_H / 2 + 0.2, CAGE_D / 2);
        group.add(bar);
    }

    // Side bars
    for (let i = 0; i <= 10; i++) {
        const z = -CAGE_D / 2 + (CAGE_D / 10) * i;
        const barL = new THREE.Mesh(barGeo, barMat);
        barL.position.set(-CAGE_W / 2, CAGE_H / 2 + 0.2, z);
        group.add(barL);

        const barR = new THREE.Mesh(barGeo, barMat);
        barR.position.set(CAGE_W / 2, CAGE_H / 2 + 0.2, z);
        group.add(barR);
    }

    // Top frame
    const frameGeoH = new THREE.CylinderGeometry(0.05, 0.05, CAGE_W, 6);
    const frameGeoV = new THREE.CylinderGeometry(0.05, 0.05, CAGE_D, 6);

    [[-CAGE_D/2, 0], [CAGE_D/2, 0]].forEach(([z]) => {
        const bar = new THREE.Mesh(frameGeoH, barMat);
        bar.rotation.z = Math.PI / 2;
        bar.position.set(0, CAGE_H + 0.2, z);
        group.add(bar);
    });
    [[-CAGE_W/2, 0], [CAGE_W/2, 0]].forEach(([x]) => {
        const bar = new THREE.Mesh(frameGeoV, barMat);
        bar.rotation.x = Math.PI / 2;
        bar.position.set(x, CAGE_H + 0.2, 0);
        group.add(bar);
    });

    return group;
}

scene.add(buildCage());

// ─── WHEEL ─────────────────────────────────────────────────────
const WHEEL_POS = new THREE.Vector3(-2.5, 0.8, -1.5);
let wheelGroup;
let wheelSpinning = false;
let wheelSpeed = 0;

function buildWheel() {
    const group = new THREE.Group();

    // Stand
    const standMat = mat(0xff6b6b, { metalness: 0.3 });
    const standBase = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.1, 0.8), standMat);
    standBase.position.y = 0.05;
    group.add(standBase);

    const standPost = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.7, 6), standMat);
    standPost.position.y = 0.45;
    group.add(standPost);

    // Wheel ring
    const wheelRing = new THREE.Mesh(
        new THREE.TorusGeometry(0.5, 0.04, 6, 16),
        mat(0xffd93d, { metalness: 0.2 })
    );
    wheelRing.position.y = 0.75;
    group.add(wheelRing);

    // Spokes
    const spokeMat = mat(0xffeaa7);
    for (let i = 0; i < 4; i++) {
        const spoke = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.0, 4), spokeMat);
        spoke.rotation.z = (i / 4) * Math.PI;
        spoke.position.y = 0.75;
        group.add(spoke);
    }

    // Runners (small bumps on inside)
    const runnerMat = mat(0xffa502);
    for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2;
        const runner = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.03), runnerMat);
        runner.position.set(Math.cos(angle) * 0.48, 0.75 + Math.sin(angle) * 0.48, 0);
        runner.lookAt(0, 0.75, 0);
        group.add(runner);
    }

    group.position.copy(WHEEL_POS);
    group.position.y = 0.3;
    group.traverse(c => { if (c.isMesh) c.castShadow = true; });

    return group;
}

wheelGroup = buildWheel();
scene.add(wheelGroup);

// ─── FOOD BOWL ─────────────────────────────────────────────────
const BOWL_POS = new THREE.Vector3(2.5, 0.35, 1.5);

function buildBowl() {
    const group = new THREE.Group();

    const bowl = new THREE.Mesh(
        new THREE.CylinderGeometry(0.3, 0.2, 0.15, 8),
        mat(0x6c5ce7, { roughness: 0.4 })
    );
    bowl.position.y = 0.075;
    bowl.castShadow = true;
    group.add(bowl);

    // Food pellets
    const pelletMat = mat(0xf39c12);
    for (let i = 0; i < 5; i++) {
        const pellet = new THREE.Mesh(new THREE.SphereGeometry(0.05, 5, 4), pelletMat);
        pellet.position.set(
            (Math.random() - 0.5) * 0.2,
            0.14,
            (Math.random() - 0.5) * 0.2
        );
        group.add(pellet);
    }

    group.position.copy(BOWL_POS);
    return group;
}

scene.add(buildBowl());

// ─── TUNNEL ────────────────────────────────────────────────────
function buildTunnel() {
    const group = new THREE.Group();
    const tunnelMat = mat(0x00b894);

    // Half-cylinder tunnel
    const tunnel = new THREE.Mesh(
        new THREE.CylinderGeometry(0.35, 0.35, 1.5, 8, 1, false, 0, Math.PI),
        tunnelMat
    );
    tunnel.rotation.z = Math.PI / 2;
    tunnel.rotation.y = Math.PI / 4;
    tunnel.position.y = 0.35;
    tunnel.castShadow = true;
    group.add(tunnel);

    // End caps
    const capGeo = new THREE.CircleGeometry(0.35, 8, 0, Math.PI);
    const cap1 = new THREE.Mesh(capGeo, tunnelMat);
    cap1.position.set(0.75 * Math.cos(Math.PI/4), 0.35, -0.75 * Math.sin(Math.PI/4));
    cap1.rotation.y = Math.PI / 4 + Math.PI / 2;
    group.add(cap1);

    const cap2 = new THREE.Mesh(capGeo, tunnelMat);
    cap2.position.set(-0.75 * Math.cos(Math.PI/4), 0.35, 0.75 * Math.sin(Math.PI/4));
    cap2.rotation.y = Math.PI / 4 - Math.PI / 2;
    group.add(cap2);

    group.position.set(1.5, 0.3, -1.5);
    return group;
}

scene.add(buildTunnel());

// ─── SCATTERED SEEDS & DECORATIONS ────────────────────────────
function addDecorations() {
    const seedMat = mat(0xe17055);
    const leafMat = mat(0x55efc4);

    for (let i = 0; i < 12; i++) {
        const seed = new THREE.Mesh(new THREE.SphereGeometry(0.04, 4, 3), seedMat);
        seed.position.set(
            (Math.random() - 0.5) * (CAGE_W - 1),
            0.32,
            (Math.random() - 0.5) * (CAGE_D - 1)
        );
        scene.add(seed);
    }

    // Small plants
    for (let i = 0; i < 4; i++) {
        const plant = new THREE.Group();
        const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.09, 0.15, 6), mat(0xd63031));
        pot.position.y = 0.075;
        plant.add(pot);
        const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.25, 5), leafMat);
        leaf.position.y = 0.28;
        plant.add(leaf);
        plant.position.set(
            (Math.random() - 0.5) * (CAGE_W - 2),
            0.3,
            (Math.random() - 0.5) * (CAGE_D - 2)
        );
        scene.add(plant);
    }
}

addDecorations();

// ─── HAMSTER FACTORY ───────────────────────────────────────────
const HAMSTER_COLORS = [
    { body: 0xffb347, belly: 0xfff5e6, ear: 0xff7675 },
    { body: 0xdfe6e9, belly: 0xffffff, ear: 0xfd79a8 },
    { body: 0xffeaa7, belly: 0xfff9c4, ear: 0xff7979 },
    { body: 0xfab1a0, belly: 0xffe4e1, ear: 0xe17055 }
];

function createHamster(colorSet) {
    const group = new THREE.Group();

    // Body
    const body = new THREE.Mesh(
        new THREE.SphereGeometry(0.25, 7, 5),
        mat(colorSet.body)
    );
    body.scale.set(1.3, 0.9, 1);
    body.position.y = 0.25;
    body.castShadow = true;
    group.add(body);

    // Belly
    const belly = new THREE.Mesh(
        new THREE.SphereGeometry(0.18, 6, 4),
        mat(colorSet.belly)
    );
    belly.scale.set(1.1, 0.7, 0.9);
    belly.position.set(0, 0.18, 0.08);
    group.add(belly);

    // Head
    const head = new THREE.Mesh(
        new THREE.SphereGeometry(0.18, 7, 5),
        mat(colorSet.body)
    );
    head.position.set(0.28, 0.32, 0);
    head.castShadow = true;
    group.add(head);

    // Snout
    const snout = new THREE.Mesh(
        new THREE.SphereGeometry(0.08, 5, 4),
        mat(colorSet.belly)
    );
    snout.position.set(0.42, 0.28, 0);
    group.add(snout);

    // Nose
    const nose = new THREE.Mesh(
        new THREE.SphereGeometry(0.03, 4, 3),
        mat(0xff6b6b)
    );
    nose.position.set(0.48, 0.28, 0);
    group.add(nose);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.035, 5, 4);
    const eyeMat = mat(0x2d3436);
    [-1, 1].forEach(side => {
        const eye = new THREE.Mesh(eyeGeo, eyeMat);
        eye.position.set(0.36, 0.38, side * 0.1);
        group.add(eye);
    });

    // Ears
    const earGeo = new THREE.SphereGeometry(0.07, 5, 4);
    const earMat = mat(colorSet.ear);
    [-1, 1].forEach(side => {
        const ear = new THREE.Mesh(earGeo, earMat);
        ear.position.set(0.22, 0.48, side * 0.12);
        ear.scale.set(0.8, 1.2, 0.8);
        group.add(ear);
    });

    // Cheeks (fluffy)
    const cheekGeo = new THREE.SphereGeometry(0.06, 5, 4);
    const cheekMat = mat(colorSet.belly);
    [-1, 1].forEach(side => {
        const cheek = new THREE.Mesh(cheekGeo, cheekMat);
        cheek.position.set(0.35, 0.25, side * 0.14);
        group.add(cheek);
    });

    // Feet
    const footGeo = new THREE.SphereGeometry(0.05, 4, 3);
    const footMat = mat(colorSet.ear);
    const footPositions = [
        [0.15, 0.05, 0.1], [0.15, 0.05, -0.1],
        [-0.15, 0.05, 0.1], [-0.15, 0.05, -0.1]
    ];
    footPositions.forEach(([x, y, z]) => {
        const foot = new THREE.Mesh(footGeo, footMat);
        foot.position.set(x, y, z);
        foot.scale.set(1, 0.6, 1);
        group.add(foot);
    });

    // Tiny tail
    const tail = new THREE.Mesh(
        new THREE.ConeGeometry(0.04, 0.1, 4),
        mat(colorSet.body)
    );
    tail.position.set(-0.35, 0.25, 0);
    tail.rotation.z = Math.PI / 2 + 0.3;
    group.add(tail);

    return group;
}

// ─── HAMSTER AI ────────────────────────────────────────────────
const STATES = { WALKING: 0, PAUSED: 1, TURNING: 2, AT_WHEEL: 3, EATING: 4 };

class Hamster {
    constructor(index) {
        this.mesh = createHamster(HAMSTER_COLORS[index % HAMSTER_COLORS.length]);
        this.mesh.position.set(
            (Math.random() - 0.5) * (CAGE_W - 2),
            0.3,
            (Math.random() - 0.5) * (CAGE_D - 2)
        );
        this.mesh.rotation.y = Math.random() * Math.PI * 2;
        scene.add(this.mesh);

        this.state = STATES.WALKING;
        this.stateTimer = Math.random() * 2;
        this.speed = 0.8 + Math.random() * 0.5;
        this.turnSpeed = 0;
        this.wobblePhase = Math.random() * Math.PI * 2;
        this.name = ['Nibbles', 'Biscuit', 'Mochi', 'Peanut'][index];
    }

    update(dt, time) {
        this.stateTimer -= dt;

        switch (this.state) {
            case STATES.WALKING:
                this.mesh.position.x += Math.sin(this.mesh.rotation.y) * this.speed * dt;
                this.mesh.position.z += Math.cos(this.mesh.rotation.y) * this.speed * dt;
                this.wobble(time);
                this.checkBounds();
                if (this.stateTimer <= 0) this.changeState();
                break;

            case STATES.PAUSED:
                this.wobble(time);
                if (this.stateTimer <= 0) this.changeState();
                break;

            case STATES.TURNING:
                this.mesh.rotation.y += this.turnSpeed * dt;
                if (this.stateTimer <= 0) {
                    this.state = STATES.WALKING;
                    this.stateTimer = 1 + Math.random() * 3;
                }
                break;

            case STATES.AT_WHEEL:
                this.goToWheel(dt);
                if (this.stateTimer <= 0) {
                    this.state = STATES.WALKING;
                    this.stateTimer = 2 + Math.random() * 3;
                    wheelSpinning = false;
                }
                break;

            case STATES.EATING:
                this.goToBowl(dt);
                if (this.stateTimer <= 0) {
                    this.state = STATES.WALKING;
                    this.stateTimer = 2 + Math.random() * 3;
                }
                break;
        }
    }

    wobble(time) {
        const wobble = Math.sin(time * 8 + this.wobblePhase) * 0.03;
        this.mesh.rotation.z = wobble;
        this.mesh.position.y = 0.3 + Math.abs(Math.sin(time * 6 + this.wobblePhase)) * 0.03;
    }

    checkBounds() {
        const halfW = CAGE_W / 2 - 0.5;
        const halfD = CAGE_D / 2 - 0.5;
        if (Math.abs(this.mesh.position.x) > halfW || Math.abs(this.mesh.position.z) > halfD) {
            this.state = STATES.TURNING;
            this.stateTimer = 0.5 + Math.random() * 0.5;
            this.turnSpeed = (Math.random() > 0.5 ? 1 : -1) * (2 + Math.random() * 2);
        }
    }

    changeState() {
        const r = Math.random();
        if (r < 0.3) {
            this.state = STATES.PAUSED;
            this.stateTimer = 1 + Math.random() * 2;
        } else if (r < 0.5) {
            this.state = STATES.TURNING;
            this.stateTimer = 0.5 + Math.random() * 0.5;
            this.turnSpeed = (Math.random() > 0.5 ? 1 : -1) * (2 + Math.random() * 2);
        } else if (r < 0.7 && !wheelSpinning) {
            this.state = STATES.AT_WHEEL;
            this.stateTimer = 3 + Math.random() * 3;
            wheelSpinning = true;
        } else if (r < 0.85) {
            this.state = STATES.EATING;
            this.stateTimer = 2 + Math.random() * 2;
        } else {
            this.state = STATES.WALKING;
            this.stateTimer = 2 + Math.random() * 4;
        }
    }

    goToWheel(dt) {
        const target = WHEEL_POS.clone();
        target.y = 0.3;
        const dir = target.clone().sub(this.mesh.position);
        const dist = dir.length();

        if (dist > 0.5) {
            dir.normalize();
            this.mesh.position.addScaledVector(dir, this.speed * 1.5 * dt);
            this.mesh.rotation.y = Math.atan2(dir.x, dir.z);
        } else {
            // At the wheel - face it and bounce
            this.mesh.rotation.y = Math.atan2(
                WHEEL_POS.x - this.mesh.position.x,
                WHEEL_POS.z - this.mesh.position.z
            );
            this.mesh.position.y = 0.3 + Math.abs(Math.sin(Date.now() * 0.01)) * 0.05;
            this.mesh.rotation.z = Math.sin(Date.now() * 0.008) * 0.1;
        }
    }

    goToBowl(dt) {
        const target = BOWL_POS.clone();
        target.y = 0.3;
        const dir = target.clone().sub(this.mesh.position);
        const dist = dir.length();

        if (dist > 0.4) {
            dir.normalize();
            this.mesh.position.addScaledVector(dir, this.speed * dt);
            this.mesh.rotation.y = Math.atan2(dir.x, dir.z);
        } else {
            // Eating - head bob
            this.mesh.rotation.y = Math.atan2(
                BOWL_POS.x - this.mesh.position.x,
                BOWL_POS.z - this.mesh.position.z
            );
            this.mesh.rotation.x = Math.sin(Date.now() * 0.005) * 0.15;
            this.mesh.position.y = 0.3 + Math.sin(Date.now() * 0.008) * 0.02;
        }
    }
}

// ─── CREATE HAMSTERS ───────────────────────────────────────────
const hamsters = [];
for (let i = 0; i < 4; i++) {
    hamsters.push(new Hamster(i));
}

// ─── ANIMATION LOOP ────────────────────────────────────────────
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;

    // Update hamsters
    hamsters.forEach(h => h.update(dt, time));

    // Spin wheel
    if (wheelSpinning) {
        wheelSpeed = Math.min(wheelSpeed + dt * 3, 4);
    } else {
        wheelSpeed = Math.max(wheelSpeed - dt * 1.5, 0);
    }
    if (wheelSpeed > 0.01) {
        // Rotate the wheel ring and spokes
        wheelGroup.children.forEach((child, i) => {
            if (i >= 2) { // Skip stand parts
                child.rotation.x += wheelSpeed * dt;
            }
        });
        // Better: rotate a sub-group. For simplicity, rotate the torus and spokes
        const ring = wheelGroup.children[2]; // torus
        if (ring.geometry.type === 'TorusGeometry') {
            ring.rotation.x += wheelSpeed * dt;
        }
        // Rotate spokes
        for (let i = 3; i < 7; i++) {
            if (wheelGroup.children[i]) {
                wheelGroup.children[i].rotation.x += wheelSpeed * dt;
            }
        }
        // Rotate runners
        for (let i = 7; i < 15; i++) {
            if (wheelGroup.children[i]) {
                wheelGroup.children[i].rotation.x += wheelSpeed * dt;
            }
        }
    }

    // Subtle camera float
    controls.update();
    renderer.render(scene, camera);
}

animate();

// ─── RESIZE ────────────────────────────────────────────────────
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

## What You Get

| Feature | Details |
|---------|---------|
| **4 Hamsters** | Nibbles, Biscuit, Mochi, Peanut — each with unique colors, fluffy cheeks, tiny tails |
| **Cage** | Glass-like walls, metal bars, wood floor, bedding layer |
| **Running Wheel** | Spins up when a hamster approaches, spins down when they leave |
| **Food Bowl** | Purple bowl with orange pellets — hamsters go eat |
| **Tunnel** | Green half-cylinder for visual interest |
| **Decorations** | Scattered seeds and tiny potted plants |
| **AI States** | Walking → Paused → Turning → At Wheel → Eating (random transitions) |
| **Controls** | Drag to orbit, scroll to zoom, damped smooth camera |

Just save as `index.html` and open in any modern browser. No build step needed.