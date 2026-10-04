

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
        #info h1 { font-size: 18px; margin-bottom: 4px; }
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
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 20, 50);

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
controls.maxDistance = 18;

// --- LIGHTING ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
dirLight.position.set(5, 10, 5);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.near = 1;
dirLight.shadow.camera.far = 30;
dirLight.shadow.camera.left = -8;
dirLight.shadow.camera.right = 8;
dirLight.shadow.camera.top = 8;
dirLight.shadow.camera.bottom = -8;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0x8ecae6, 0.3);
fillLight.position.set(-3, 4, -3);
scene.add(fillLight);

// --- MATERIALS ---
const mat = {
    wood: new THREE.MeshLambertMaterial({ color: 0x8B5E3C }),
    woodLight: new THREE.MeshLambertMaterial({ color: 0xC4956A }),
    tray: new THREE.MeshLambertMaterial({ color: 0x5D4037 }),
    bedding: new THREE.MeshLambertMaterial({ color: 0xF5DEB3 }),
    wire: new THREE.MeshLambertMaterial({ color: 0xB0BEC5 }),
    wheel: new THREE.MeshLambertMaterial({ color: 0xFF6B6B }),
    wheelSpoke: new THREE.MeshLambertMaterial({ color: 0xFFE66D }),
    bowl: new THREE.MeshLambertMaterial({ color: 0x4ECDC4 }),
    food: new THREE.MeshLambertMaterial({ color: 0xFFA502 }),
    tunnel: new THREE.MeshLambertMaterial({ color: 0xA29BFE }),
    grass: new THREE.MeshLambertMaterial({ color: 0x6BCB77 }),
};

// --- CAGE ---
function buildCage() {
    const group = new THREE.Group();
    const W = 6, D = 5, H = 3.5;

    // Tray (base)
    const trayGeo = new THREE.BoxGeometry(W + 0.4, 0.3, D + 0.4);
    const tray = new THREE.Mesh(trayGeo, mat.tray);
    tray.position.y = 0.15;
    tray.receiveShadow = true;
    group.add(tray);

    // Bedding layer
    const bedGeo = new THREE.BoxGeometry(W - 0.1, 0.15, D - 0.1);
    const bed = new THREE.Mesh(bedGeo, mat.bedding);
    bed.position.y = 0.37;
    bed.receiveShadow = true;
    group.add(bed);

    // Walls (wireframe style)
    const wallMat = new THREE.MeshBasicMaterial({ color: 0xB0BEC5, wireframe: true });
    
    // Back wall
    const backWall = new THREE.Mesh(new THREE.PlaneGeometry(W, H, 8, 6), wallMat);
    backWall.position.set(0, H / 2 + 0.3, -D / 2);
    group.add(backWall);

    // Left wall
    const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(D, H, 8, 6), wallMat);
    leftWall.rotation.y = Math.PI / 2;
    leftWall.position.set(-W / 2, H / 2 + 0.3, 0);
    group.add(leftWall);

    // Right wall
    const rightWall = new THREE.Mesh(new THREE.PlaneGeometry(D, H, 8, 6), wallMat);
    rightWall.rotation.y = -Math.PI / 2;
    rightWall.position.set(W / 2, H / 2 + 0.3, 0);
    group.add(rightWall);

    // Top frame
    const frameMat = new THREE.MeshLambertMaterial({ color: 0x78909C });
    const frameGeo = new THREE.CylinderGeometry(0.04, 0.04, W, 6);
    const frameTop1 = new THREE.Mesh(frameGeo, frameMat);
    frameTop1.rotation.z = Math.PI / 2;
    frameTop1.position.set(0, H + 0.3, -D / 2);
    group.add(frameTop1);
    const frameTop2 = new THREE.Mesh(frameGeo, frameMat);
    frameTop2.rotation.z = Math.PI / 2;
    frameTop2.position.set(0, H + 0.3, D / 2);
    group.add(frameTop2);

    const frameGeo2 = new THREE.CylinderGeometry(0.04, 0.04, D, 6);
    const frameTop3 = new THREE.Mesh(frameGeo2, frameMat);
    frameTop3.rotation.x = Math.PI / 2;
    frameTop3.position.set(-W / 2, H + 0.3, 0);
    group.add(frameTop3);
    const frameTop4 = new THREE.Mesh(frameGeo2, frameMat);
    frameTop4.rotation.x = Math.PI / 2;
    frameTop4.position.set(W / 2, H + 0.3, 0);
    group.add(frameTop4);

    // Vertical posts
    const postGeo = new THREE.CylinderGeometry(0.05, 0.05, H, 6);
    [[-W/2, -D/2], [W/2, -D/2], [-W/2, D/2], [W/2, D/2]].forEach(([x, z]) => {
        const post = new THREE.Mesh(postGeo, frameMat);
        post.position.set(x, H / 2 + 0.3, z);
        group.add(post);
    });

    return group;
}
scene.add(buildCage());

// --- GROUND (outside cage) ---
const groundGeo = new THREE.CircleGeometry(15, 32);
const groundMat = new THREE.MeshLambertMaterial({ color: 0x90EE90 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.01;
ground.receiveShadow = true;
scene.add(ground);

// --- RUNNING WHEEL ---
let wheelGroup;
let wheelSpinSpeed = 0;
function buildWheel() {
    const group = new THREE.Group();
    const radius = 0.7;

    // Outer ring
    const ringGeo = new THREE.TorusGeometry(radius, 0.06, 8, 16);
    const ring = new THREE.Mesh(ringGeo, mat.wheel);
    ring.castShadow = true;
    group.add(ring);

    // Spokes
    for (let i = 0; i < 6; i++) {
        const angle = (i / 6) * Math.PI * 2;
        const spokeGeo = new THREE.CylinderGeometry(0.025, 0.025, radius * 2, 6);
        const spoke = new THREE.Mesh(spokeGeo, mat.wheelSpoke);
        spoke.rotation.z = angle;
        spoke.castShadow = true;
        group.add(spoke);
    }

    // Center hub
    const hubGeo = new THREE.SphereGeometry(0.1, 8, 6);
    const hub = new THREE.Mesh(hubGeo, mat.wheelSpoke);
    group.add(hub);

    // Stand
    const standGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.5, 6);
    const standMat = new THREE.MeshLambertMaterial({ color: 0x696969 });
    const stand1 = new THREE.Mesh(standGeo, standMat);
    stand1.position.set(0, -radius - 0.25, 0);
    group.add(stand1);

    const baseGeo = new THREE.BoxGeometry(0.6, 0.08, 0.3);
    const base = new THREE.Mesh(baseGeo, standMat);
    base.position.set(0, -radius - 0.5, 0);
    base.castShadow = true;
    group.add(base);

    group.position.set(1.8, 1.2, -1.5);
    group.rotation.x = Math.PI / 2;
    scene.add(group);
    wheelGroup = group;
}
buildWheel();

// --- FOOD BOWL ---
function buildBowl() {
    const group = new THREE.Group();

    const bowlGeo = new THREE.CylinderGeometry(0.35, 0.25, 0.2, 8);
    const bowl = new THREE.Mesh(bowlGeo, mat.bowl);
    bowl.position.y = 0.1;
    bowl.castShadow = true;
    group.add(bowl);

    // Food pellets
    for (let i = 0; i < 5; i++) {
        const pelletGeo = new THREE.SphereGeometry(0.06, 6, 4);
        const pellet = new THREE.Mesh(pelletGeo, mat.food);
        const a = (i / 5) * Math.PI * 2;
        pellet.position.set(Math.cos(a) * 0.12, 0.2, Math.sin(a) * 0.12);
        group.add(pellet);
    }

    group.position.set(-1.5, 0.45, 1.2);
    scene.add(group);
    return group;
}
const bowlGroup = buildBowl();

// --- TUNNEL ---
function buildTunnel() {
    const group = new THREE.Group();
    const tunnelGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.5, 8, 1, true);
    const tunnel = new THREE.Mesh(tunnelGeo, mat.tunnel);
    tunnel.rotation.z = Math.PI / 2;
    tunnel.position.y = 0.3;
    tunnel.castShadow = true;
    group.add(tunnel);

    // End caps (open look)
    const capGeo = new THREE.RingGeometry(0.2, 0.3, 8);
    const capMat = new THREE.MeshLambertMaterial({ color: 0x6C5CE7, side: THREE.DoubleSide });
    const cap1 = new THREE.Mesh(capGeo, capMat);
    cap1.rotation.y = Math.PI / 2;
    cap1.position.set(0.75, 0.3, 0);
    group.add(cap1);
    const cap2 = new THREE.Mesh(capGeo, capMat);
    cap2.rotation.y = -Math.PI / 2;
    cap2.position.set(-0.75, 0.3, 0);
    group.add(cap2);

    group.position.set(-0.5, 0.45, -0.8);
    group.rotation.y = 0.4;
    scene.add(group);
}
buildTunnel();

// --- DECORATIONS ---
function addGrassTuft(x, z) {
    const group = new THREE.Group();
    for (let i = 0; i < 4; i++) {
        const bladeGeo = new THREE.ConeGeometry(0.03, 0.3 + Math.random() * 0.2, 4);
        const blade = new THREE.Mesh(bladeGeo, mat.grass);
        blade.position.set((Math.random() - 0.5) * 0.15, 0.15, (Math.random() - 0.5) * 0.15);
        blade.rotation.x = (Math.random() - 0.5) * 0.3;
        blade.rotation.z = (Math.random() - 0.5) * 0.3;
        group.add(blade);
    }
    group.position.set(x, 0.45, z);
    scene.add(group);
}
addGrassTuft(-2, -1.5);
addGrassTuft(0.5, 1.8);
addGrassTuft(2, 0.5);

// Small rocks
function addRock(x, z) {
    const geo = new THREE.DodecahedronGeometry(0.12 + Math.random() * 0.08, 0);
    const rockMat = new THREE.MeshLambertMaterial({ color: 0x95A5A6 });
    const rock = new THREE.Mesh(geo, rockMat);
    rock.position.set(x, 0.5, z);
    rock.castShadow = true;
    scene.add(rock);
}
addRock(-2.2, 0.3);
addRock(0.8, -1.8);
addRock(2.3, 1.5);

// --- HAMSTER MODEL ---
const hamsterColors = [
    { body: 0xFFA502, belly: 0xFFF3E0, ear: 0xFF6348 },
    { body: 0xDDBE89, belly: 0xFFF8E7, ear: 0xE17055 },
    { body: 0xF8F9FA, belly: 0xFFFFFF, ear: 0xFAB1A0 },
    { body: 0xE8A87C, belly: 0xFFE4C4, ear: 0xD4756B },
];

function createHamster(colorIndex) {
    const colors = hamsterColors[colorIndex % hamsterColors.length];
    const group = new THREE.Group();

    const bodyMat = new THREE.MeshLambertMaterial({ color: colors.body });
    const bellyMat = new THREE.MeshLambertMaterial({ color: colors.belly });
    const earMat = new THREE.MeshLambertMaterial({ color: colors.ear });
    const eyeMat = new THREE.MeshLambertMaterial({ color: 0x2d3436 });
    const noseMat = new THREE.MeshLambertMaterial({ color: 0xFF6B81 });

    // Body
    const bodyGeo = new THREE.SphereGeometry(0.22, 8, 6);
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.scale.set(1.3, 0.9, 1);
    body.position.y = 0.2;
    body.castShadow = true;
    group.add(body);

    // Belly patch
    const bellyGeo = new THREE.SphereGeometry(0.15, 6, 4);
    const belly = new THREE.Mesh(bellyGeo, bellyMat);
    belly.scale.set(1, 0.7, 0.8);
    belly.position.set(0.05, 0.15, 0);
    group.add(belly);

    // Head
    const headGeo = new THREE.SphereGeometry(0.16, 8, 6);
    const head = new THREE.Mesh(headGeo, bodyMat);
    head.position.set(0.25, 0.28, 0);
    head.castShadow = true;
    group.add(head);

    // Ears
    const earGeo = new THREE.ConeGeometry(0.06, 0.1, 5);
    const ear1 = new THREE.Mesh(earGeo, earMat);
    ear1.position.set(0.22, 0.42, 0.1);
    ear1.rotation.z = -0.3;
    group.add(ear1);
    const ear2 = new THREE.Mesh(earGeo, earMat);
    ear2.position.set(0.22, 0.42, -0.1);
    ear2.rotation.z = -0.3;
    group.add(ear2);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.03, 6, 4);
    const eye1 = new THREE.Mesh(eyeGeo, eyeMat);
    eye1.position.set(0.35, 0.3, 0.08);
    group.add(eye1);
    const eye2 = new THREE.Mesh(eyeGeo, eyeMat);
    eye2.position.set(0.35, 0.3, -0.08);
    group.add(eye2);

    // Nose
    const noseGeo = new THREE.SphereGeometry(0.025, 5, 4);
    const nose = new THREE.Mesh(noseGeo, noseMat);
    nose.position.set(0.4, 0.25, 0);
    group.add(nose);

    // Cheeks (puffy)
    const cheekGeo = new THREE.SphereGeometry(0.05, 5, 4);
    const cheekMat = new THREE.MeshLambertMaterial({ color: colors.belly });
    const cheek1 = new THREE.Mesh(cheekGeo, cheekMat);
    cheek1.position.set(0.3, 0.2, 0.12);
    group.add(cheek1);
    const cheek2 = new THREE.Mesh(cheekGeo, cheekMat);
    cheek2.position.set(0.3, 0.2, -0.12);
    group.add(cheek2);

    // Tiny legs
    const legGeo = new THREE.CylinderGeometry(0.03, 0.025, 0.1, 5);
    const legPositions = [
        [0.12, 0.05, 0.1], [0.12, 0.05, -0.1],
        [-0.12, 0.05, 0.1], [-0.12, 0.05, -0.1]
    ];
    legPositions.forEach(([lx, ly, lz]) => {
        const leg = new THREE.Mesh(legGeo, bodyMat);
        leg.position.set(lx, ly, lz);
        group.add(leg);
    });

    // Tail
    const tailGeo = new THREE.ConeGeometry(0.03, 0.08, 4);
    const tail = new THREE.Mesh(tailGeo, bodyMat);
    tail.position.set(-0.3, 0.2, 0);
    tail.rotation.z = Math.PI / 2;
    group.add(tail);

    return group;
}

// --- HAMSTER BEHAVIOR SYSTEM ---
const STATES = { WALKING: 0, PAUSED: 1, TURNING: 2, AT_WHEEL: 3, AT_BOWL: 4 };

class Hamster {
    constructor(index) {
        this.mesh = createHamster(index);
        this.mesh.position.set(
            (Math.random() - 0.5) * 4,
            0.45,
            (Math.random() - 0.5) * 3
        );
        this.mesh.rotation.y = Math.random() * Math.PI * 2;
        scene.add(this.mesh);

        this.state = STATES.WALKING;
        this.target = this.getRandomTarget();
        this.speed = 0.8 + Math.random() * 0.4;
        this.pauseTimer = 0;
        this.turnTimer = 0;
        this.interactTimer = 0;
        this.bobPhase = Math.random() * Math.PI * 2;
        this.wheelActive = false;
    }

    getRandomTarget() {
        const x = (Math.random() - 0.5) * 4.5;
        const z = (Math.random() - 0.5) * 3.5;
        return new THREE.Vector3(x, 0.45, z);
    }

    getWheelPos() { return new THREE.Vector3(1.8, 0.45, -1.5); }
    getBowlPos() { return new THREE.Vector3(-1.5, 0.45, 1.2); }

    update(dt) {
        this.bobPhase += dt * 8;

        switch (this.state) {
            case STATES.WALKING:
                this.walk(dt);
                break;
            case STATES.PAUSED:
                this.pause(dt);
                break;
            case STATES.TURNING:
                this.turn(dt);
                break;
            case STATES.AT_WHEEL:
                this.atWheel(dt);
                break;
            case STATES.AT_BOWL:
                this.atBowl(dt);
                break;
        }

        // Bob animation
        this.mesh.position.y = 0.45 + Math.sin(this.bobPhase) * 0.02;
    }

    walk(dt) {
        const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position);
        dir.y = 0;
        const dist = dir.length();

        if (dist < 0.3) {
            // Arrived - decide next action
            const roll = Math.random();
            if (roll < 0.15) {
                this.state = STATES.AT_WHEEL;
                this.target = this.getWheelPos();
                this.interactTimer = 2 + Math.random() * 2;
            } else if (roll < 0.3) {
                this.state = STATES.AT_BOWL;
                this.target = this.getBowlPos();
                this.interactTimer = 1.5 + Math.random() * 1.5;
            } else if (roll < 0.6) {
                this.state = STATES.PAUSED;
                this.pauseTimer = 1 + Math.random() * 2;
            } else {
                this.state = STATES.TURNING;
                this.turnTimer = 0.5 + Math.random() * 0.5;
            }
            return;
        }

        dir.normalize();
        this.mesh.position.addScaledVector(dir, this.speed * dt);

        // Smoothly face direction
        const targetAngle = Math.atan2(dir.x, dir.z);
        let angleDiff = targetAngle - this.mesh.rotation.y;
        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
        this.mesh.rotation.y += angleDiff * 5 * dt;

        // Walk bob
        this.mesh.position.y = 0.45 + Math.abs(Math.sin(this.bobPhase * 1.5)) * 0.03;
    }

    pause(dt) {
        this.pauseTimer -= dt;
        // Slight idle wobble
        this.mesh.rotation.y += Math.sin(this.bobPhase * 0.5) * 0.005;
        if (this.pauseTimer <= 0) {
            this.state = STATES.WALKING;
            this.target = this.getRandomTarget();
        }
    }

    turn(dt) {
        this.turnTimer -= dt;
        this.mesh.rotation.y += dt * 4;
        if (this.turnTimer <= 0) {
            this.state = STATES.WALKING;
            this.target = this.getRandomTarget();
        }
    }

    atWheel(dt) {
        this.interactTimer -= dt;
        const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position);
        dir.y = 0;
        const dist = dir.length();

        if (dist > 0.5) {
            dir.normalize();
            this.mesh.position.addScaledVector(dir, this.speed * dt);
            const targetAngle = Math.atan2(dir.x, dir.z);
            let angleDiff = targetAngle - this.mesh.rotation.y;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
            this.mesh.rotation.y += angleDiff * 5 * dt;
        } else {
            // At the wheel - face it and bounce
            const wheelAngle = Math.atan2(
                this.getWheelPos().x - this.mesh.position.x,
                this.getWheelPos().z - this.mesh.position.z
            );
            let angleDiff = wheelAngle - this.mesh.rotation.y;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
            this.mesh.rotation.y += angleDiff * 5 * dt;

            this.mesh.position.y = 0.45 + Math.abs(Math.sin(this.bobPhase * 2)) * 0.06;
            wheelSpinSpeed = Math.min(wheelSpinSpeed + dt * 3, 5);
        }

        if (this.interactTimer <= 0) {
            this.state = STATES.WALKING;
            this.target = this.getRandomTarget();
        }
    }

    atBowl(dt) {
        this.interactTimer -= dt;
        const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position);
        dir.y = 0;
        const dist = dir.length();

        if (dist > 0.5) {
            dir.normalize();
            this.mesh.position.addScaledVector(dir, this.speed * dt);
            const targetAngle = Math.atan2(dir.x, dir.z);
            let angleDiff = targetAngle - this.mesh.rotation.y;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
            this.mesh.rotation.y += angleDiff * 5 * dt;
        } else {
            // Eating animation - head bobs
            const bowlAngle = Math.atan2(
                this.getBowlPos().x - this.mesh.position.x,
                this.getBowlPos().z - this.mesh.position.z
            );
            let angleDiff = bowlAngle - this.mesh.rotation.y;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
            this.mesh.rotation.y += angleDiff * 5 * dt;

            this.mesh.position.y = 0.45 + Math.abs(Math.sin(this.bobPhase * 3)) * 0.04;
            // Slight lean forward
            this.mesh.rotation.x = Math.sin(this.bobPhase * 3) * 0.1;
        }

        if (this.interactTimer <= 0) {
            this.state = STATES.WALKING;
            this.target = this.getRandomTarget();
            this.mesh.rotation.x = 0;
        }
    }
}

// Create hamsters
const hamsters = [];
for (let i = 0; i < 4; i++) {
    hamsters.push(new Hamster(i));
}

// --- ANIMATION LOOP ---
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);

    // Update hamsters
    hamsters.forEach(h => h.update(dt));

    // Wheel spin decay
    wheelSpinSpeed *= 0.98;
    if (wheelSpinSpeed > 0.01) {
        wheelGroup.rotation.z += wheelSpinSpeed * dt;
    }

    // Subtle bowl wobble when being eaten from
    const bowlHamster = hamsters.find(h => h.state === STATES.AT_BOWL);
    if (bowlHamster) {
        bowlGroup.rotation.z = Math.sin(clock.elapsedTime * 10) * 0.03;
    } else {
        bowlGroup.rotation.z *= 0.9;
    }

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

This creates a complete, self-contained hamster playground with:

**Scene Elements:**
- **Cage** — wireframe walls with metal posts and a wooden tray base
- **Running wheel** — red torus with yellow spokes that spins when hamsters interact with it
- **Food bowl** — teal bowl with orange pellets that wobbles when eaten from
- **Tunnel** — purple half-cylinder tunnel
- **Decorations** — grass tufts and scattered rocks

**4 Low-Poly Hamsters** with distinct color schemes (orange, cream, white, peach), each featuring:
- Rounded body with belly patch
- Puffy cheeks, tiny ears, dot eyes, pink nose
- Little stubby legs and a tiny tail

**Autonomous Behavior (state machine):**
| State | Action |
|-------|--------|
| WALKING | Moves toward a random target with smooth turning |
| PAUSED | Stops and idles with subtle wobble |
| TURNING | Spins in place briefly |
| AT_WHEEL | Walks to wheel, bounces excitedly, wheel spins |
| AT_BOWL | Walks to bowl, eats with head-bobbing, bowl wobbles |

**Controls:** Drag to orbit, scroll to zoom, with damping for smooth feel.