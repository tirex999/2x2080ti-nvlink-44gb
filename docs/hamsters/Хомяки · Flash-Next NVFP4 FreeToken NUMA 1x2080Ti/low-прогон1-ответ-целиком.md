

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
            backdrop-filter: blur(4px);
        }
        #ui h1 { font-size: 18px; margin-bottom: 4px; color: #ffb3d9; }
        #ui p { opacity: 0.8; font-size: 12px; }
    </style>
</head>
<body>
    <div id="ui">
        <h1>🐹 Hamster Playground</h1>
        <p>Drag to rotate • Scroll to zoom</p>
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

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 20, 40);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(8, 7, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.target.set(0, 1.5, 0);
controls.maxPolarAngle = Math.PI / 2.1;
controls.minDistance = 5;
controls.maxDistance = 20;

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
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

const fillLight = new THREE.DirectionalLight(0xadd8ff, 0.3);
fillLight.position.set(-3, 5, -5);
scene.add(fillLight);

// Materials
const mat = (color) => new THREE.MeshLambertMaterial({ color, flatShading: true });

// Ground
const groundGeo = new THREE.PlaneGeometry(50, 50);
const groundMat = new THREE.MeshLambertMaterial({ color: 0x90c695 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

// Tray / Cage floor
const trayGeo = new THREE.BoxGeometry(8, 0.4, 6);
const trayMat = mat(0xf5c842);
const tray = new THREE.Mesh(trayGeo, trayMat);
tray.position.y = 0.2;
tray.receiveShadow = true;
tray.castShadow = true;
scene.add(tray);

// Tray rim
const rimMat = mat(0xe8a832);
const rimGeo1 = new THREE.BoxGeometry(8.4, 0.6, 0.3);
const rimGeo2 = new THREE.BoxGeometry(0.3, 0.6, 6.4);
const rim1 = new THREE.Mesh(rimGeo1, rimMat); rim1.position.set(0, 0.5, 3.05); rim1.castShadow = true; scene.add(rim1);
const rim2 = new THREE.Mesh(rimGeo1, rimMat); rim2.position.set(0, 0.5, -3.05); rim2.castShadow = true; scene.add(rim2);
const rim3 = new THREE.Mesh(rimGeo2, rimMat); rim3.position.set(4.05, 0.5, 0); rim3.castShadow = true; scene.add(rim3);
const rim4 = new THREE.Mesh(rimGeo2, rimMat); rim4.position.set(-4.05, 0.5, 0); rim4.castShadow = true; scene.add(rim4);

// Bedding (wood chips)
const beddingGeo = new THREE.BoxGeometry(7.6, 0.15, 5.6);
const beddingMat = mat(0xd4a574);
const bedding = new THREE.Mesh(beddingGeo, beddingMat);
bedding.position.y = 0.47;
bedding.receiveShadow = true;
scene.add(bedding);

// Scatter some wood chips
for (let i = 0; i < 40; i++) {
    const chipGeo = new THREE.BoxGeometry(
        0.1 + Math.random() * 0.2,
        0.05,
        0.05 + Math.random() * 0.1
    );
    const chip = new THREE.Mesh(chipGeo, mat(0xc49a6c));
    chip.position.set(
        (Math.random() - 0.5) * 7,
        0.55,
        (Math.random() - 0.5) * 5
    );
    chip.rotation.y = Math.random() * Math.PI;
    scene.add(chip);
}

// Cage bars
const barMat = mat(0x888899);
const barGeo = new THREE.CylinderGeometry(0.04, 0.04, 4, 6);
const cageWidth = 8, cageDepth = 6, cageHeight = 4;

for (let i = 0; i <= 8; i++) {
    const x = -cageWidth / 2 + (cageWidth / 8) * i;
    // Front
    const barF = new THREE.Mesh(barGeo, barMat);
    barF.position.set(x, cageHeight / 2 + 0.4, cageDepth / 2);
    barF.castShadow = true;
    scene.add(barF);
    // Back
    const barB = new THREE.Mesh(barGeo, barMat);
    barB.position.set(x, cageHeight / 2 + 0.4, -cageDepth / 2);
    barB.castShadow = true;
    scene.add(barB);
}
for (let i = 0; i <= 6; i++) {
    const z = -cageDepth / 2 + (cageDepth / 6) * i;
    // Left
    const barL = new THREE.Mesh(barGeo, barMat);
    barL.position.set(-cageWidth / 2, cageHeight / 2 + 0.4, z);
    barL.castShadow = true;
    scene.add(barL);
    // Right
    const barR = new THREE.Mesh(barGeo, barMat);
    barR.position.set(cageWidth / 2, cageHeight / 2 + 0.4, z);
    barR.castShadow = true;
    scene.add(barR);
}

// Top bars (horizontal)
const topBarGeo1 = new THREE.CylinderGeometry(0.04, 0.04, cageWidth, 6);
const topBarGeo2 = new THREE.CylinderGeometry(0.04, 0.04, cageDepth, 6);
for (let i = 0; i <= 6; i++) {
    const z = -cageDepth / 2 + (cageDepth / 6) * i;
    const tb = new THREE.Mesh(topBarGeo1, barMat);
    tb.rotation.z = Math.PI / 2;
    tb.position.set(0, cageHeight + 0.4, z);
    scene.add(tb);
}
for (let i = 0; i <= 8; i++) {
    const x = -cageWidth / 2 + (cageWidth / 8) * i;
    const tb = new THREE.Mesh(topBarGeo2, barMat);
    tb.rotation.x = Math.PI / 2;
    tb.position.set(x, cageHeight + 0.4, 0);
    scene.add(tb);
}

// Hamster Wheel
const wheelGroup = new THREE.Group();
const wheelMat = mat(0xff6b9d);
const wheelRadius = 1.4;
const wheelGeo = new THREE.TorusGeometry(wheelRadius, 0.08, 8, 16);
const wheel = new THREE.Mesh(wheelGeo, wheelMat);
wheel.castShadow = true;
wheelGroup.add(wheel);

// Wheel spokes
const spokeGeo = new THREE.CylinderGeometry(0.04, 0.04, wheelRadius * 2, 6);
for (let i = 0; i < 6; i++) {
    const spoke = new THREE.Mesh(spokeGeo, mat(0xffa0c0));
    spoke.rotation.z = (Math.PI / 6) * i;
    spoke.castShadow = true;
    wheelGroup.add(spoke);
}

// Wheel stand
const standMat = mat(0x666677);
const standGeo = new THREE.CylinderGeometry(0.06, 0.06, 2.5, 6);
const stand1 = new THREE.Mesh(standGeo, standMat);
stand1.position.set(0, -1.25, 0.3);
stand1.rotation.x = 0.15;
wheelGroup.add(stand1);
const stand2 = new THREE.Mesh(standGeo, standMat);
stand2.position.set(0, -1.25, -0.3);
stand2.rotation.x = -0.15;
wheelGroup.add(stand2);

// Wheel base
const baseGeo = new THREE.BoxGeometry(0.6, 0.15, 1.2);
const base = new THREE.Mesh(baseGeo, standMat);
base.position.y = -2.5;
wheelGroup.add(base);

wheelGroup.position.set(-2.5, 3.2, -2);
scene.add(wheelGroup);

// Food bowl
const bowlGroup = new THREE.Group();
const bowlGeo = new THREE.SphereGeometry(0.5, 8, 6, 0, Math.PI * 2, 0, Math.PI / 2);
const bowl = new THREE.Mesh(bowlGeo, mat(0x6bcf7f));
bowl.rotation.x = Math.PI;
bowl.position.y = 0.5;
bowl.castShadow = true;
bowlGroup.add(bowl);

// Food pellets in bowl
for (let i = 0; i < 8; i++) {
    const pelletGeo = new THREE.IcosahedronGeometry(0.08, 0);
    const pellet = new THREE.Mesh(pelletGeo, mat(0xd4a017));
    pellet.position.set(
        (Math.random() - 0.5) * 0.4,
        0.35 + Math.random() * 0.1,
        (Math.random() - 0.5) * 0.4
    );
    bowlGroup.add(pellet);
}
bowlGroup.position.set(2.5, 0.55, 1.5);
scene.add(bowlGroup);

// Tunnel
const tunnelGroup = new THREE.Group();
const tunnelGeo = new THREE.CylinderGeometry(0.6, 0.6, 2.5, 8, 1, true);
const tunnelMat = new THREE.MeshLambertMaterial({ color: 0x9b59b6, side: THREE.DoubleSide, flatShading: true });
const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
tunnel.rotation.z = Math.PI / 2;
tunnel.castShadow = true;
tunnelGroup.add(tunnel);

// Tunnel rings
const ringGeo = new THREE.TorusGeometry(0.65, 0.06, 6, 12);
const ring1 = new THREE.Mesh(ringGeo, mat(0x8e44ad));
ring1.rotation.y = Math.PI / 2;
ring1.position.x = -1.2;
tunnelGroup.add(ring1);
const ring2 = new THREE.Mesh(ringGeo, mat(0x8e44ad));
ring2.rotation.y = Math.PI / 2;
ring2.position.x = 1.2;
tunnelGroup.add(ring2);

tunnelGroup.position.set(1.5, 1.15, -1.5);
scene.add(tunnelGroup);

// Water bottle
const bottleGroup = new THREE.Group();
const bottleGeo = new THREE.CylinderGeometry(0.2, 0.2, 1.2, 8);
const bottleMat = new THREE.MeshLambertMaterial({ color: 0x74b9ff, transparent: true, opacity: 0.7 });
const bottle = new THREE.Mesh(bottleGeo, bottleMat);
bottleGroup.add(bottle);
const capGeo = new THREE.CylinderGeometry(0.1, 0.15, 0.2, 8);
const cap = new THREE.Mesh(capGeo, mat(0x333333));
cap.position.y = 0.7;
bottleGroup.add(cap);
const spoutGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.4, 6);
const spout = new THREE.Mesh(spoutGeo, mat(0xaaaaaa));
spout.position.y = -0.8;
bottleGroup.add(spout);
bottleGroup.position.set(3.8, 2.5, 0);
bottleGroup.rotation.z = 0.1;
scene.add(bottleGroup);

// Hamster creation function
function createHamster(color, name) {
    const group = new THREE.Group();
    group.userData = { name, state: 'idle', timer: 0, targetAngle: 0, speed: 0 };

    // Body
    const bodyGeo = new THREE.IcosahedronGeometry(0.4, 1);
    const body = new THREE.Mesh(bodyGeo, mat(color));
    body.scale.set(1.3, 0.9, 1);
    body.position.y = 0.35;
    body.castShadow = true;
    group.add(body);

    // Head
    const headGeo = new THREE.IcosahedronGeometry(0.28, 1);
    const head = new THREE.Mesh(headGeo, mat(color));
    head.position.set(0.45, 0.4, 0);
    head.castShadow = true;
    group.add(head);

    // Ears
    const earGeo = new THREE.SphereGeometry(0.1, 6, 4);
    const earMat = mat(0xffb6c1);
    const earL = new THREE.Mesh(earGeo, earMat);
    earL.position.set(0.4, 0.65, 0.15);
    group.add(earL);
    const earR = new THREE.Mesh(earGeo, earMat);
    earR.position.set(0.4, 0.65, -0.15);
    group.add(earR);

    // Inner ears
    const innerEarGeo = new THREE.SphereGeometry(0.06, 6, 4);
    const innerEarMat = mat(0xff8fa3);
    const innerL = new THREE.Mesh(innerEarGeo, innerEarMat);
    innerL.position.set(0.42, 0.67, 0.15);
    group.add(innerL);
    const innerR = new THREE.Mesh(innerEarGeo, innerEarMat);
    innerR.position.set(0.42, 0.67, -0.15);
    group.add(innerR);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.05, 6, 4);
    const eyeMat = mat(0x222222);
    const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(0.65, 0.45, 0.1);
    group.add(eyeL);
    const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
    eyeR.position.set(0.65, 0.45, -0.1);
    group.add(eyeR);

    // Eye shine
    const shineGeo = new THREE.SphereGeometry(0.02, 4, 4);
    const shineMat = mat(0xffffff);
    const shineL = new THREE.Mesh(shineGeo, shineMat);
    shineL.position.set(0.67, 0.47, 0.11);
    group.add(shineL);
    const shineR = new THREE.Mesh(shineGeo, shineMat);
    shineR.position.set(0.67, 0.47, -0.09);
    group.add(shineR);

    // Nose
    const noseGeo = new THREE.SphereGeometry(0.04, 6, 4);
    const nose = new THREE.Mesh(noseGeo, mat(0xff6b9d));
    nose.position.set(0.73, 0.38, 0);
    group.add(nose);

    // Cheeks (chubby!)
    const cheekGeo = new THREE.SphereGeometry(0.12, 6, 4);
    const cheekMat = mat(color);
    const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
    cheekL.position.set(0.55, 0.32, 0.2);
    group.add(cheekL);
    const cheekR = new THREE.Mesh(cheekGeo, cheekMat);
    cheekR.position.set(0.55, 0.32, -0.2);
    group.add(cheekR);

    // Belly
    const bellyGeo = new THREE.IcosahedronGeometry(0.25, 1);
    const belly = new THREE.Mesh(bellyGeo, mat(0xfff5e6));
    belly.position.set(0, 0.25, 0);
    belly.scale.set(1, 0.7, 0.8);
    group.add(belly);

    // Legs
    const legGeo = new THREE.CylinderGeometry(0.05, 0.04, 0.2, 6);
    const legMat = mat(0xffb6c1);
    const legPositions = [
        [0.25, 0.1, 0.15], [0.25, 0.1, -0.15],
        [-0.25, 0.1, 0.15], [-0.25, 0.1, -0.15]
    ];
    const legs = [];
    legPositions.forEach(pos => {
        const leg = new THREE.Mesh(legGeo, legMat);
        leg.position.set(...pos);
        leg.castShadow = true;
        group.add(leg);
        legs.push(leg);
    });
    group.userData.legs = legs;

    // Tail (tiny nub)
    const tailGeo = new THREE.SphereGeometry(0.06, 5, 4);
    const tail = new THREE.Mesh(tailGeo, mat(color));
    tail.position.set(-0.55, 0.35, 0);
    group.add(tail);

    return group;
}

// Create hamsters
const hamsters = [];
const hamsterColors = [0xf4a460, 0xffe4b5, 0xdeb887, 0xf5deb3, 0xe8c39e];
const hamsterNames = ['Peanut', 'Biscuit', 'Nugget', 'Waffles', 'Mochi'];

for (let i = 0; i < 5; i++) {
    const h = createHamster(hamsterColors[i], hamsterNames[i]);
    const angle = (i / 5) * Math.PI * 2;
    h.position.set(
        Math.cos(angle) * 2,
        0.55,
        Math.sin(angle) * 2
    );
    h.rotation.y = -angle + Math.PI / 2;
    scene.add(h);
    hamsters.push(h);
}

// Hamster AI
const states = ['idle', 'walk', 'turn', 'explore_wheel', 'explore_bowl'];

function updateHamster(h, dt, time) {
    const d = h.userData;
    d.timer -= dt;

    // Boundary check
    const bounds = { x: 3.2, z: 2.2 };
    if (Math.abs(h.position.x) > bounds.x || Math.abs(h.position.z) > bounds.z) {
        d.state = 'turn';
        d.timer = 0.5;
        d.targetAngle = Math.atan2(-h.position.z, -h.position.x) + Math.PI;
    }

    switch (d.state) {
        case 'idle':
            // Bobbing animation
            h.position.y = 0.55 + Math.sin(time * 2 + h.position.x) * 0.02;
            if (d.timer <= 0) {
                const rand = Math.random();
                if (rand < 0.5) {
                    d.state = 'walk';
                    d.timer = 1 + Math.random() * 2;
                    d.targetAngle = Math.random() * Math.PI * 2;
                    d.speed = 0.8 + Math.random() * 0.5;
                } else if (rand < 0.7) {
                    d.state = 'explore_wheel';
                    d.timer = 3 + Math.random() * 2;
                    d.targetAngle = Math.atan2(
                        wheelGroup.position.z - h.position.z,
                        wheelGroup.position.x - h.position.x
                    );
                    d.speed = 0.6;
                } else if (rand < 0.85) {
                    d.state = 'explore_bowl';
                    d.timer = 2 + Math.random() * 2;
                    d.targetAngle = Math.atan2(
                        bowlGroup.position.z - h.position.z,
                        bowlGroup.position.x - h.position.x
                    );
                    d.speed = 0.6;
                } else {
                    d.state = 'turn';
                    d.timer = 0.8;
                    d.targetAngle = h.rotation.y + (Math.random() - 0.5) * Math.PI;
                }
            }
            break;

        case 'walk':
            // Smooth turn toward target
            let diff = d.targetAngle - h.rotation.y;
            while (diff > Math.PI) diff -= Math.PI * 2;
            while (diff < -Math.PI) diff += Math.PI * 2;
            h.rotation.y += diff * 3 * dt;

            h.position.x += Math.cos(h.rotation.y) * d.speed * dt;
            h.position.z += Math.sin(h.rotation.y) * d.speed * dt;

            // Walking bob
            h.position.y = 0.55 + Math.sin(time * 8) * 0.03;

            // Leg animation
            d.legs.forEach((leg, i) => {
                leg.position.y = 0.1 + Math.sin(time * 10 + i * Math.PI / 2) * 0.03;
            });

            if (d.timer <= 0) {
                d.state = 'idle';
                d.timer = 0.5 + Math.random() * 1.5;
                d.legs.forEach(leg => leg.position.y = 0.1);
            }
            break;

        case 'turn':
            let diff2 = d.targetAngle - h.rotation.y;
            while (diff2 > Math.PI) diff2 -= Math.PI * 2;
            while (diff2 < -Math.PI) diff2 += Math.PI * 2;
            h.rotation.y += diff2 * 4 * dt;

            if (d.timer <= 0) {
                d.state = 'walk';
                d.timer = 1 + Math.random() * 2;
                d.targetAngle = h.rotation.y + (Math.random() - 0.5) * 1;
                d.speed = 0.8 + Math.random() * 0.5;
            }
            break;

        case 'explore_wheel':
            let diff3 = d.targetAngle - h.rotation.y;
            while (diff3 > Math.PI) diff3 -= Math.PI * 2;
            while (diff3 < -Math.PI) diff3 += Math.PI * 2;
            h.rotation.y += diff3 * 3 * dt;

            const distToWheel = Math.sqrt(
                (h.position.x - wheelGroup.position.x) ** 2 +
                (h.position.z - wheelGroup.position.z) ** 2
            );

            if (distToWheel > 1.2) {
                h.position.x += Math.cos(h.rotation.y) * d.speed * dt;
                h.position.z += Math.sin(h.rotation.y) * d.speed * dt;
                h.position.y = 0.55 + Math.sin(time * 8) * 0.03;
            } else {
                // At wheel - spin it!
                wheelGroup.rotation.z += dt * 4;
                h.position.y = 0.55 + Math.sin(time * 12) * 0.05;
            }

            if (d.timer <= 0) {
                d.state = 'idle';
                d.timer = 1 + Math.random() * 2;
            }
            break;

        case 'explore_bowl':
            let diff4 = d.targetAngle - h.rotation.y;
            while (diff4 > Math.PI) diff4 -= Math.PI * 2;
            while (diff4 < -Math.PI) diff4 += Math.PI * 2;
            h.rotation.y += diff4 * 3 * dt;

            const distToBowl = Math.sqrt(
                (h.position.x - bowlGroup.position.x) ** 2 +
                (h.position.z - bowlGroup.position.z) ** 2
            );

            if (distToBowl > 0.8) {
                h.position.x += Math.cos(h.rotation.y) * d.speed * dt;
                h.position.z += Math.sin(h.rotation.y) * d.speed * dt;
                h.position.y = 0.55 + Math.sin(time * 8) * 0.03;
            } else {
                // Eating animation - head bob
                h.position.y = 0.55 + Math.sin(time * 10) * 0.04;
                // Nudge bowl slightly
                bowlGroup.position.x += Math.sin(time * 5) * 0.001;
            }

            if (d.timer <= 0) {
                d.state = 'idle';
                d.timer = 1 + Math.random() * 2;
            }
            break;
    }
}

// Decorative elements - small plants outside cage
function createPlant(x, z, color) {
    const g = new THREE.Group();
    const potGeo = new THREE.CylinderGeometry(0.3, 0.2, 0.4, 6);
    const pot = new THREE.Mesh(potGeo, mat(0xd35400));
    pot.position.y = 0.2;
    pot.castShadow = true;
    g.add(pot);

    for (let i = 0; i < 5; i++) {
        const leafGeo = new THREE.ConeGeometry(0.15, 0.5, 5);
        const leaf = new THREE.Mesh(leafGeo, mat(color));
        leaf.position.set(
            (Math.random() - 0.5) * 0.2,
            0.5 + Math.random() * 0.3,
            (Math.random() - 0.5) * 0.2
        );
        leaf.rotation.x = (Math.random() - 0.5) * 0.5;
        leaf.rotation.z = (Math.random() - 0.5) * 0.5;
        g.add(leaf);
    }
    g.position.set(x, 0, z);
    scene.add(g);
}
createPlant(-6, 2, 0x27ae60);
createPlant(6, -2, 0x2ecc71);
createPlant(-5, -3, 0x27ae60);

// Floating particles (dust motes)
const particleGeo = new THREE.BufferGeometry();
const particleCount = 50;
const positions = new Float32Array(particleCount * 3);
for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 10;
    positions[i * 3 + 1] = Math.random() * 5 + 0.5;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 8;
}
particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
const particleMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.03, transparent: true, opacity: 0.6 });
const particles = new THREE.Points(particleGeo, particleMat);
scene.add(particles);

// Animation loop
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.getElapsedTime();

    // Update hamsters
    hamsters.forEach(h => updateHamster(h, dt, time));

    // Gentle wheel idle spin
    wheelGroup.rotation.z += dt * 0.2;

    // Particle drift
    const pos = particles.geometry.attributes.position.array;
    for (let i = 0; i < particleCount; i++) {
        pos[i * 3 + 1] += Math.sin(time + i) * 0.001;
        pos[i * 3] += Math.cos(time * 0.5 + i) * 0.0005;
    }
    particles.geometry.attributes.position.needsUpdate = true;

    controls.update();
    renderer.render(scene, camera);
}

animate();

// Handle resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
    </script>
</body>
</html>
```

This creates a complete, self-contained low-poly hamster playground with:

**Scene Elements:**
- 🟡 Yellow tray with rim and wood chip bedding
- 🏗️ Wire cage with vertical and horizontal bars
- 🎡 Pink spinning wheel with spokes and stand
- 🥗 Green food bowl with pellets
- 🟣 Purple tunnel with decorative rings
- 💧 Translucent water bottle
- 🌿 Decorative plants outside the cage
- ✨ Floating dust particles

**5 Cute Hamsters** (Peanut, Biscuit, Nugget, Waffles, Mochi) with:
- Chubby bodies, big cheeks, tiny ears with pink insides
- Shiny eyes, pink noses, tiny nub tails
- Animated legs that move while walking

**Autonomous AI Behaviors:**
- **Idle** — gentle bobbing
- **Walk** — smooth turning + movement with leg animation
- **Turn** — reorienting direction
- **Explore Wheel** — walks to the wheel and makes it spin
- **Explore Bowl** — walks to the food bowl and "eats" (head bobbing + bowl nudging)

**Interaction:** Drag to orbit, scroll to zoom. The camera is damped for smooth movement.