

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
            left: 50%;
            transform: translateX(-50%);
            color: #fff;
            background: rgba(0,0,0,0.5);
            padding: 10px 24px;
            border-radius: 20px;
            font-size: 14px;
            pointer-events: none;
            backdrop-filter: blur(4px);
        }
        #info h1 { font-size: 18px; margin-bottom: 2px; }
    </style>
</head>
<body>
<div id="info">
    <h1>🐹 Low-Poly Hamster Playground</h1>
    <span>Drag to rotate • Scroll to zoom</span>
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

// --- SCENE SETUP ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87CEEB);
scene.fog = new THREE.Fog(0x87CEEB, 20, 40);

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
controls.maxPolarAngle = Math.PI / 2.1;
controls.minDistance = 4;
controls.maxDistance = 18;
controls.target.set(0, 1, 0);

// --- LIGHTING ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
dirLight.position.set(5, 10, 5);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.left = -8;
dirLight.shadow.camera.right = 8;
dirLight.shadow.camera.top = 8;
dirLight.shadow.camera.bottom = -8;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0xa0d8ff, 0.3);
fillLight.position.set(-3, 5, -3);
scene.add(fillLight);

// --- MATERIALS ---
function mat(color, opts = {}) {
    return new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.8, metalness: 0.1, ...opts });
}

// --- FLOOR / TRAY ---
function createFloor() {
    const group = new THREE.Group();

    // Base tray
    const trayGeo = new THREE.BoxGeometry(8, 0.4, 6);
    const tray = new THREE.Mesh(trayGeo, mat(0x8B6914));
    tray.position.y = -0.2;
    tray.receiveShadow = true;
    group.add(tray);

    // Wood shavings (small scattered boxes)
    const shavingColors = [0xDEB887, 0xD2A679, 0xC49A6C, 0xE8C9A0];
    for (let i = 0; i < 60; i++) {
        const s = 0.1 + Math.random() * 0.15;
        const geo = new THREE.BoxGeometry(s, 0.05, s * 0.6);
        const m = new THREE.Mesh(geo, mat(shavingColors[Math.floor(Math.random() * shavingColors.length)]));
        m.position.set((Math.random() - 0.5) * 7.5, 0.03, (Math.random() - 0.5) * 5.5);
        m.rotation.y = Math.random() * Math.PI;
        m.receiveShadow = true;
        group.add(m);
    }

    return group;
}
scene.add(createFloor());

// --- CAGE ---
function createCage() {
    const group = new THREE.Group();
    const W = 8, H = 4, D = 6;
    const barMat = mat(0x555555, { metalness: 0.6, roughness: 0.3 });
    const glassMat = new THREE.MeshStandardMaterial({
        color: 0xaaddff, transparent: true, opacity: 0.12, roughness: 0.1, metalness: 0.3, side: THREE.DoubleSide
    });

    // Glass panels
    const panels = [
        { size: [W, H], pos: [0, H/2, -D/2], rot: [0, 0, 0] },
        { size: [W, H], pos: [0, H/2, D/2], rot: [0, 0, 0] },
        { size: [D, H], pos: [-W/2, H/2, 0], rot: [0, Math.PI/2, 0] },
        { size: [D, H], pos: [W/2, H/2, 0], rot: [0, Math.PI/2, 0] },
    ];
    panels.forEach(p => {
        const geo = new THREE.PlaneGeometry(...p.size);
        const mesh = new THREE.Mesh(geo, glassMat);
        mesh.position.set(...p.pos);
        mesh.rotation.set(...p.rot);
        group.add(mesh);
    });

    // Bars (edges)
    const barR = 0.06;
    function addBar(from, to) {
        const dir = new THREE.Vector3().subVectors(to, from);
        const len = dir.length();
        const geo = new THREE.CylinderGeometry(barR, barR, len, 6);
        const bar = new THREE.Mesh(geo, barMat);
        bar.position.copy(from).add(to).multiplyScalar(0.5);
        bar.lookAt(to);
        bar.rotateX(Math.PI / 2);
        bar.castShadow = true;
        group.add(bar);
    }

    const corners = [
        [-W/2, 0, -D/2], [W/2, 0, -D/2], [W/2, 0, D/2], [-W/2, 0, D/2],
        [-W/2, H, -D/2], [W/2, H, -D/2], [W/2, H, D/2], [-W/2, H, D/2]
    ];
    // Vertical bars
    for (let i = 0; i < 4; i++) {
        addBar(new THREE.Vector3(...corners[i]), new THREE.Vector3(...corners[i + 4]));
    }
    // Top horizontal
    for (let i = 4; i < 8; i++) {
        addBar(new THREE.Vector3(...corners[i]), new THREE.Vector3(...corners[(i + 1) % 4 + 4]));
    }
    // Bottom horizontal
    for (let i = 0; i < 4; i++) {
        addBar(new THREE.Vector3(...corners[i]), new THREE.Vector3(...corners[(i + 1) % 4]));
    }

    // Vertical grid bars on sides
    for (let i = 1; i < 6; i++) {
        const x = -W/2 + (W / 6) * i;
        addBar(new THREE.Vector3(x, 0, -D/2), new THREE.Vector3(x, H, -D/2));
        addBar(new THREE.Vector3(x, 0, D/2), new THREE.Vector3(x, H, D/2));
    }
    for (let i = 1; i < 4; i++) {
        const z = -D/2 + (D / 4) * i;
        addBar(new THREE.Vector3(-W/2, 0, z), new THREE.Vector3(-W/2, H, z));
        addBar(new THREE.Vector3(W/2, 0, z), new THREE.Vector3(W/2, H, z));
    }

    // Horizontal mid bars
    for (let j = 1; j < 3; j++) {
        const y = (H / 3) * j;
        addBar(new THREE.Vector3(-W/2, y, -D/2), new THREE.Vector3(W/2, y, -D/2));
        addBar(new THREE.Vector3(-W/2, y, D/2), new THREE.Vector3(W/2, y, D/2));
        addBar(new THREE.Vector3(-W/2, y, -D/2), new THREE.Vector3(-W/2, y, D/2));
        addBar(new THREE.Vector3(W/2, y, -D/2), new THREE.Vector3(W/2, y, D/2));
    }

    return group;
}
scene.add(createCage());

// --- WHEEL ---
let wheel;
function createWheel() {
    const group = new THREE.Group();
    const wheelMat = mat(0xFF6B9D, { metalness: 0.2 });
    const frameMat = mat(0x444444, { metalness: 0.5, roughness: 0.4 });

    // Wheel rim (torus)
    const rimGeo = new THREE.TorusGeometry(1, 0.08, 6, 12);
    const rim = new THREE.Mesh(rimGeo, wheelMat);
    rim.castShadow = true;
    group.add(rim);

    // Spokes
    for (let i = 0; i < 6; i++) {
        const angle = (i / 6) * Math.PI * 2;
        const spokeGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.9, 4);
        const spoke = new THREE.Mesh(spokeGeo, frameMat);
        spoke.position.set(Math.cos(angle) * 0.5, Math.sin(angle) * 0.5, 0);
        spoke.rotation.z = angle - Math.PI / 2;
        group.add(spoke);
    }

    // Center hub
    const hubGeo = new THREE.SphereGeometry(0.12, 6, 4);
    const hub = new THREE.Mesh(hubGeo, frameMat);
    group.add(hub);

    // Stand
    const standGeo = new THREE.CylinderGeometry(0.05, 0.05, 1.2, 6);
    const standL = new THREE.Mesh(standGeo, frameMat);
    standL.position.set(-0.5, -1.5, 0);
    group.add(standL);
    const standR = standL.clone();
    standR.position.x = 0.5;
    group.add(standR);

    // Base
    const baseGeo = new THREE.BoxGeometry(1.4, 0.1, 0.6);
    const base = new THREE.Mesh(baseGeo, frameMat);
    base.position.y = -2.1;
    group.add(base);

    group.position.set(-2.5, 2.1, -1.5);
    group.rotation.y = Math.PI / 6;
    scene.add(group);
    return group;
}
wheel = createWheel();

// --- FOOD BOWL ---
function createFoodBowl() {
    const group = new THREE.Group();
    const bowlMat = mat(0x4ECDC4);

    // Bowl (flattened cylinder)
    const bowlGeo = new THREE.CylinderGeometry(0.5, 0.35, 0.3, 8);
    const bowl = new THREE.Mesh(bowlGeo, bowlMat);
    bowl.castShadow = true;
    group.add(bowl);

    // Food pellets
    const pelletColors = [0xFF8C42, 0xFFD93D, 0x6BCB77];
    for (let i = 0; i < 8; i++) {
        const pGeo = new THREE.SphereGeometry(0.06, 4, 3);
        const p = new THREE.Mesh(pGeo, mat(pelletColors[i % 3]));
        const a = (i / 8) * Math.PI * 2;
        p.position.set(Math.cos(a) * 0.2, 0.15, Math.sin(a) * 0.2);
        group.add(p);
    }

    group.position.set(2.5, 0.15, 1.5);
    scene.add(group);
    return group;
}
scene.add(createFoodBowl());

// --- TUNNEL ---
function createTunnel() {
    const group = new THREE.Group();
    const tunnelMat = mat(0xA78BFA);

    // Half cylinder tunnel
    const tunnelGeo = new THREE.CylinderGeometry(0.5, 0.5, 2, 8, 1, false, 0, Math.PI);
    const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
    tunnel.rotation.z = Math.PI / 2;
    tunnel.rotation.y = Math.PI / 2;
    tunnel.castShadow = true;
    group.add(tunnel);

    // End caps (rings)
    const ringGeo = new THREE.TorusGeometry(0.5, 0.06, 6, 8, Math.PI);
    const ring1 = new THREE.Mesh(ringGeo, tunnelMat);
    ring1.position.x = 1;
    ring1.rotation.z = Math.PI / 2;
    group.add(ring1);
    const ring2 = ring1.clone();
    ring2.position.x = -1;
    ring2.rotation.z = -Math.PI / 2;
    group.add(ring2);

    group.position.set(0.5, 0.5, -1.5);
    group.rotation.y = -0.3;
    scene.add(group);
    return group;
}
scene.add(createTunnel());

// --- HAMSTER FACTORY ---
const HAMSTER_COLORS = [
    { body: 0xFFB347, belly: 0xFFF5E1, ear: 0xFF8C69 },
    { body: 0xF5F0E8, belly: 0xFFFFFF, ear: 0xFFB6C1 },
    { body: 0xDEA583, belly: 0xFFF0DB, ear: 0xC68B59 },
    { body: 0xFFDAB9, belly: 0xFFF8F0, ear: 0xFF9E7D },
];

function createHamster(colorIdx) {
    const c = HAMSTER_COLORS[colorIdx % HAMSTER_COLORS.length];
    const group = new THREE.Group();
    const bodyMat = mat(c.body);
    const bellyMat = mat(c.belly);
    const earMat = mat(c.ear);
    const eyeMat = mat(0x222222, { roughness: 0.3 });

    // Body
    const bodyGeo = new THREE.SphereGeometry(0.35, 6, 5);
    bodyGeo.scale(1.3, 0.9, 1);
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 0.35;
    body.castShadow = true;
    group.add(body);

    // Belly patch
    const bellyGeo = new THREE.SphereGeometry(0.28, 5, 4);
    bellyGeo.scale(1.1, 0.7, 0.8);
    const belly = new THREE.Mesh(bellyGeo, bellyMat);
    belly.position.set(0.1, 0.25, 0);
    group.add(belly);

    // Head
    const headGeo = new THREE.SphereGeometry(0.25, 6, 5);
    const head = new THREE.Mesh(headGeo, bodyMat);
    head.position.set(0.45, 0.45, 0);
    head.castShadow = true;
    group.add(head);

    // Snout
    const snoutGeo = new THREE.SphereGeometry(0.1, 4, 3);
    const snout = new THREE.Mesh(snoutGeo, bellyMat);
    snout.position.set(0.65, 0.38, 0);
    group.add(snout);

    // Nose
    const noseGeo = new THREE.SphereGeometry(0.04, 4, 3);
    const nose = new THREE.Mesh(noseGeo, mat(0xFF6B9D));
    nose.position.set(0.72, 0.4, 0);
    group.add(nose);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.05, 4, 3);
    const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(0.55, 0.52, 0.12);
    group.add(eyeL);
    const eyeR = eyeL.clone();
    eyeR.position.z = -0.12;
    group.add(eyeR);

    // Cheeks (blush)
    const cheekGeo = new THREE.SphereGeometry(0.06, 4, 3);
    const cheekMat = mat(0xFFB6C1, { transparent: true, opacity: 0.6 });
    const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
    cheekL.position.set(0.55, 0.38, 0.18);
    group.add(cheekL);
    const cheekR = cheekL.clone();
    cheekR.position.z = -0.18;
    group.add(cheekR);

    // Ears
    const earGeo = new THREE.ConeGeometry(0.08, 0.12, 4);
    const earL = new THREE.Mesh(earGeo, earMat);
    earL.position.set(0.4, 0.68, 0.14);
    earL.rotation.z = -0.3;
    group.add(earL);
    const earR = earL.clone();
    earR.position.z = -0.14;
    earR.rotation.z = 0.3;
    group.add(earR);

    // Feet (tiny)
    const footGeo = new THREE.SphereGeometry(0.06, 4, 3);
    const footMat = mat(c.ear);
    const positions = [[0.3, 0.05, 0.12], [0.3, 0.05, -0.12], [-0.2, 0.05, 0.12], [-0.2, 0.05, -0.12]];
    positions.forEach(p => {
        const foot = new THREE.Mesh(footGeo, footMat);
        foot.position.set(...p);
        group.add(foot);
    });

    // Tail
    const tailGeo = new THREE.ConeGeometry(0.04, 0.1, 4);
    const tail = new THREE.Mesh(tailGeo, bodyMat);
    tail.position.set(-0.45, 0.35, 0);
    tail.rotation.z = Math.PI / 2;
    group.add(tail);

    return group;
}

// --- HAMSTER BEHAVIOR ---
class Hamster {
    constructor(idx) {
        this.mesh = createHamster(idx);
        this.mesh.position.set(
            (Math.random() - 0.5) * 5,
            0,
            (Math.random() - 0.5) * 4
        );
        this.mesh.rotation.y = Math.random() * Math.PI * 2;
        scene.add(this.mesh);

        this.state = 'WALKING';
        this.stateTimer = 0;
        this.speed = 0.8 + Math.random() * 0.5;
        this.targetAngle = Math.random() * Math.PI * 2;
        this.pauseDuration = 1 + Math.random() * 2;
        this.wobblePhase = Math.random() * Math.PI * 2;
        this.wheelCooldown = 0;
        this.isInWheel = false;
    }

    update(dt, time) {
        this.stateTimer -= dt;
        if (this.wheelCooldown > 0) this.wheelCooldown -= dt;

        switch (this.state) {
            case 'WALKING':
                this.walk(dt, time);
                if (this.stateTimer <= 0) {
                    this.state = 'PAUSED';
                    this.stateTimer = this.pauseDuration;
                }
                break;
            case 'PAUSED':
                if (this.stateTimer <= 0) {
                    this.state = 'WALKING';
                    this.stateTimer = 2 + Math.random() * 3;
                    this.targetAngle = Math.random() * Math.PI * 2;
                }
                break;
            case 'AT_WHEEL':
                this.atWheel(dt, time);
                break;
            case 'AT_BOWL':
                this.atBowl(dt, time);
                break;
        }

        // Wobble animation
        this.mesh.position.y = Math.abs(Math.sin(time * 8 + this.wobblePhase)) * 0.03;

        // Clamp to cage bounds
        const p = this.mesh.position;
        p.x = THREE.MathUtils.clamp(p.x, -3.5, 3.5);
        p.z = THREE.MathUtils.clamp(p.z, -2.5, 2.5);
    }

    walk(dt, time) {
        // Move toward target angle
        const currentAngle = this.mesh.rotation.y;
        let angleDiff = this.targetAngle - currentAngle;
        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;

        if (Math.abs(angleDiff) > 0.1) {
            this.mesh.rotation.y += angleDiff * dt * 2;
        }

        // Move forward
        const dir = new THREE.Vector3(Math.sin(this.mesh.rotation.y), 0, Math.cos(this.mesh.rotation.y));
        this.mesh.position.addScaledVector(dir, this.speed * dt);

        // Check if near wheel
        const wheelPos = wheel.position;
        const distToWheel = this.mesh.position.distanceTo(new THREE.Vector3(wheelPos.x, 0, wheelPos.z));
        if (distToWheel < 1.2 && this.wheelCooldown <= 0 && !this.isInWheel) {
            this.state = 'AT_WHEEL';
            this.stateTimer = 3 + Math.random() * 3;
            this.isInWheel = true;
            this.wheelCooldown = 8 + Math.random() * 5;
            // Position at wheel
            this.mesh.position.set(wheelPos.x, 0, wheelPos.z);
            this.mesh.rotation.y = wheel.rotation.y;
            return;
        }

        // Check if near bowl
        const bowlPos = new THREE.Vector3(2.5, 0, 1.5);
        const distToBowl = this.mesh.position.distanceTo(bowlPos);
        if (distToBowl < 1.0 && this.wheelCooldown <= 0) {
            this.state = 'AT_BOWL';
            this.stateTimer = 2 + Math.random() * 2;
            this.mesh.position.set(2.2, 0, 1.2);
            this.mesh.rotation.y = Math.atan2(bowlPos.x - this.mesh.position.x, bowlPos.z - this.mesh.position.z);
            return;
        }
    }

    atWheel(dt, time) {
        // Face the wheel
        this.mesh.rotation.y = wheel.rotation.y;
        // Animate running in place (fast wobble)
        this.mesh.position.y = Math.abs(Math.sin(time * 15 + this.wobblePhase)) * 0.08;
        // Spin the wheel
        wheel.rotation.x += dt * 5;

        if (this.stateTimer <= 0) {
            this.state = 'WALKING';
            this.stateTimer = 2 + Math.random() * 3;
            this.targetAngle = Math.random() * Math.PI * 2;
            this.isInWheel = false;
            // Step away from wheel
            this.mesh.position.x += (Math.random() - 0.5) * 0.5;
            this.mesh.position.z += (Math.random() - 0.5) * 0.5;
        }
    }

    atBowl(dt, time) {
        // Nibble animation (head bob)
        this.mesh.rotation.x = Math.sin(time * 10) * 0.1;
        this.mesh.position.y = Math.abs(Math.sin(time * 6 + this.wobblePhase)) * 0.02;

        if (this.stateTimer <= 0) {
            this.state = 'WALKING';
            this.stateTimer = 2 + Math.random() * 3;
            this.targetAngle = Math.random() * Math.PI * 2;
            this.mesh.rotation.x = 0;
        }
    }
}

// Create hamsters
const hamsters = [];
for (let i = 0; i < 4; i++) {
    hamsters.push(new Hamster(i));
}

// --- DECORATIVE ELEMENTS ---
// Small plants
function createPlant(x, z) {
    const group = new THREE.Group();
    const potGeo = new THREE.CylinderGeometry(0.15, 0.12, 0.2, 6);
    const pot = new THREE.Mesh(potGeo, mat(0xE07A5F));
    pot.position.y = 0.1;
    group.add(pot);

    const leafGeo = new THREE.ConeGeometry(0.12, 0.3, 5);
    const leaf = new THREE.Mesh(leafGeo, mat(0x52B788));
    leaf.position.y = 0.35;
    group.add(leaf);
    const leaf2 = leaf.clone();
    leaf2.position.y = 0.5;
    leaf2.scale.setScalar(0.7);
    group.add(leaf2);

    group.position.set(x, 0, z);
    scene.add(group);
}
createPlant(-3, 2);
createPlant(3.2, -2);
createPlant(-3.2, -2.2);

// Small toy ball
const ballGeo = new THREE.IcosahedronGeometry(0.15, 0);
const ball = new THREE.Mesh(ballGeo, mat(0xFFD93D));
ball.position.set(1, 0.15, 0.5);
ball.castShadow = true;
scene.add(ball);

// --- ANIMATION LOOP ---
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.getElapsedTime();

    // Update hamsters
    hamsters.forEach(h => h.update(dt, time));

    // Slowly stop wheel when no hamster is in it
    let anyInWheel = hamsters.some(h => h.isInWheel);
    if (!anyInWheel) {
        wheel.rotation.x += dt * 0.5; // slow decay
    }

    // Ball bounces gently
    ball.position.y = 0.15 + Math.abs(Math.sin(time * 2)) * 0.05;
    ball.rotation.y += dt * 0.5;

    controls.update();
    renderer.render(scene, camera);
}
animate();

// --- RESIZE ---
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

## What's Included

| Element | Details |
|---------|---------|
| **Cage** | Wire-frame bars + transparent glass panels |
| **Floor** | Wooden tray with scattered wood shavings |
| **4 Hamsters** | Different color schemes, low-poly bodies with ears, cheeks, eyes, feet, tails |
| **Wheel** | Spinning pink wheel with spokes — hamsters approach it and "run" |
| **Food Bowl** | Teal bowl with colorful pellets — hamsters nibble at it |
| **Tunnel** | Purple half-cylinder tunnel (decorative) |
| **Plants & Ball** | Small potted plants and a bouncing icosahedron ball |

## Behavior System

Each hamster runs a simple state machine:
- **WALKING** → moves forward, picks up wheel/bowl when nearby
- **PAUSED** → stops and idles
- **AT_WHEEL** → faces wheel, rapid wobble, wheel spins fast
- **AT_BOWL** → heads bob as if eating

Just save as `index.html` and open in any modern browser. Drag to orbit, scroll to zoom.