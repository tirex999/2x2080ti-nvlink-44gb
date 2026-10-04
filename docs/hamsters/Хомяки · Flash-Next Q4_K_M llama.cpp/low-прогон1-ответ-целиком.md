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
            color: #fff; font-size: 14px;
            background: rgba(0,0,0,0.5); padding: 12px 18px;
            border-radius: 12px; backdrop-filter: blur(4px);
        }
        #ui h1 { font-size: 18px; margin-bottom: 4px; color: #ffb6c1; }
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
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
    }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- Scene Setup ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2d1b4e);
scene.fog = new THREE.Fog(0x2d1b4e, 20, 40);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
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

// --- Lights ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffeedd, 1.2);
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

const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3);
fillLight.position.set(-3, 5, -5);
scene.add(fillLight);

const pointLight = new THREE.PointLight(0xff9999, 0.5, 10);
pointLight.position.set(0, 4, 0);
scene.add(pointLight);

// --- Materials ---
function mat(color, opts = {}) {
    return new THREE.MeshStandardMaterial({
        color, flatShading: true, roughness: 0.8, metalness: 0.0, ...opts
    });
}

// --- Cage Floor / Tray ---
const trayGeo = new THREE.BoxGeometry(10, 0.6, 8);
const trayMat = mat(0xf4a0c0);
const tray = new THREE.Mesh(trayGeo, trayMat);
tray.position.y = 0.3;
tray.receiveShadow = true;
scene.add(tray);

// Tray rim
const rimGeo = new THREE.BoxGeometry(10.4, 0.8, 8.4);
const rimMat = mat(0xe888aa);
const rim = new THREE.Mesh(rimGeo, rimMat);
rim.position.y = 0.1;
rim.receiveShadow = true;
scene.add(rim);

// --- Cage Bars ---
const barMat = mat(0xcccccc, { metalness: 0.6, roughness: 0.3 });
const barGeo = new THREE.CylinderGeometry(0.04, 0.04, 6, 6);

for (let x = -4.5; x <= 4.5; x += 1.5) {
    for (let z of [-3.8, 3.8]) {
        const bar = new THREE.Mesh(barGeo, barMat);
        bar.position.set(x, 3.3, z);
        bar.castShadow = true;
        scene.add(bar);
    }
}
for (let z = -3.5; z <= 3.5; z += 1.5) {
    for (let x of [-4.8, 4.8]) {
        const bar = new THREE.Mesh(barGeo, barMat);
        bar.position.set(x, 3.3, z);
        bar.castShadow = true;
        scene.add(bar);
    }
}

// Top cross bars
const topBarGeo = new THREE.CylinderGeometry(0.05, 0.05, 10, 6);
for (let z = -3.5; z <= 3.5; z += 1.75) {
    const bar = new THREE.Mesh(topBarGeo, barMat);
    bar.rotation.z = Math.PI / 2;
    bar.position.set(0, 6.3, z);
    scene.add(bar);
}
const topBarGeo2 = new THREE.CylinderGeometry(0.05, 0.05, 8, 6);
for (let x = -4.5; x <= 4.5; x += 1.75) {
    const bar = new THREE.Mesh(topBarGeo2, barMat);
    bar.rotation.x = Math.PI / 2;
    bar.position.set(x, 6.3, 0);
    scene.add(bar);
}

// --- Bedding (scattered wood shavings) ---
const beddingGeo = new THREE.BoxGeometry(0.15, 0.05, 0.08);
const beddingMat = mat(0xd4a574);
for (let i = 0; i < 80; i++) {
    const b = new THREE.Mesh(beddingGeo, beddingMat);
    b.position.set(
        (Math.random() - 0.5) * 9,
        0.65,
        (Math.random() - 0.5) * 7
    );
    b.rotation.y = Math.random() * Math.PI;
    b.rotation.x = (Math.random() - 0.5) * 0.5;
    scene.add(b);
}

// --- Hamster Wheel ---
const wheelGroup = new THREE.Group();
wheelGroup.position.set(3, 1.8, 0);

const wheelRingGeo = new THREE.TorusGeometry(1.4, 0.12, 8, 16);
const wheelRingMat = mat(0x66ccff);
const wheelRing = new THREE.Mesh(wheelRingGeo, wheelRingMat);
wheelRing.castShadow = true;
wheelGroup.add(wheelRing);

// Wheel spokes
const spokeGeo = new THREE.BoxGeometry(0.06, 0.06, 2.6);
const spokeMat = mat(0x55bbee);
for (let i = 0; i < 8; i++) {
    const spoke = new THREE.Mesh(spokeGeo, spokeMat);
    spoke.rotation.z = (i / 8) * Math.PI;
    spoke.position.z = 0;
    wheelGroup.add(spoke);
}

// Wheel axle
const axleGeo = new THREE.CylinderGeometry(0.1, 0.1, 0.8, 8);
const axleMat = mat(0x888888, { metalness: 0.5 });
const axle = new THREE.Mesh(axleGeo, axleMat);
axle.rotation.x = Math.PI / 2;
wheelGroup.add(axle);

// Wheel stand
const standGeo = new THREE.BoxGeometry(0.3, 2.5, 0.3);
const standMat = mat(0x888888, { metalness: 0.3 });
const stand1 = new THREE.Mesh(standGeo, standMat);
stand1.position.set(0, -0.8, 0.5);
wheelGroup.add(stand1);
const stand2 = new THREE.Mesh(standGeo, standMat);
stand2.position.set(0, -0.8, -0.5);
wheelGroup.add(stand2);

scene.add(wheelGroup);
let wheelSpinSpeed = 0;
let wheelTargetSpin = 0;

// --- Food Bowl ---
const bowlGroup = new THREE.Group();
bowlGroup.position.set(-2.5, 0.6, 1.5);

const bowlOuter = new THREE.CylinderGeometry(0.6, 0.4, 0.4, 8);
const bowlMat = mat(0xff6666);
const bowl = new THREE.Mesh(bowlOuter, bowlMat);
bowl.castShadow = true;
bowlGroup.add(bowl);

// Food pellets inside
const pelletGeo = new THREE.IcosahedronGeometry(0.08, 0);
const pelletMat = mat(0x8B4513);
for (let i = 0; i < 12; i++) {
    const p = new THREE.Mesh(pelletGeo, pelletMat);
    const angle = Math.random() * Math.PI * 2;
    const r = Math.random() * 0.3;
    p.position.set(Math.cos(angle) * r, 0.15, Math.sin(angle) * r);
    bowlGroup.add(p);
}
scene.add(bowlGroup);

// --- Water Bottle ---
const bottleGroup = new THREE.Group();
bottleGroup.position.set(-4.5, 2.5, -1);

const bottleBody = new THREE.CylinderGeometry(0.25, 0.25, 1.5, 8);
const bottleMat = mat(0x88ddff, { transparent: true, opacity: 0.6 });
const bottleBodyMesh = new THREE.Mesh(bottleBody, bottleMat);
bottleGroup.add(bottleBodyMesh);

const bottleCap = new THREE.CylinderGeometry(0.12, 0.18, 0.3, 8);
const bottleCapMat = mat(0xff8888);
const bottleCapMesh = new THREE.Mesh(bottleCap, bottleCapMat);
bottleCapMesh.position.y = -0.9;
bottleGroup.add(bottleCapMesh);

// Tube
const tubeGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.5, 6);
const tubeMat = mat(0xaaaaaa, { metalness: 0.5 });
const tube = new THREE.Mesh(tubeGeo, tubeMat);
tube.position.y = -1.2;
bottleGroup.add(tube);

scene.add(bottleGroup);

// --- Hamster Factory ---
const hamsterColors = [
    { body: 0xffcc88, belly: 0xffe8cc },
    { body: 0xeeeeee, belly: 0xffffff },
    { body: 0xcc8844, belly: 0xffdd99 },
    { body: 0xff9999, belly: 0xffcccc },
];

function createHamster(colorScheme, name) {
    const group = new THREE.Group();
    group.userData = {
        state: 'idle',
        timer: Math.random() * 3,
        direction: new THREE.Vector3(Math.random() - 0.5, 0, Math.random() - 0.5).normalize(),
        speed: 0.8 + Math.random() * 0.4,
        targetPoint: null,
        name,
        bobPhase: Math.random() * Math.PI * 2,
        earWiggle: 0,
    };

    // Body
    const bodyGeo = new THREE.IcosahedronGeometry(0.4, 1);
    bodyGeo.scale(1.2, 0.9, 1.0);
    const bodyMat2 = mat(colorScheme.body);
    const body = new THREE.Mesh(bodyGeo, bodyMat2);
    body.castShadow = true;
    group.add(body);

    // Belly
    const bellyGeo = new THREE.IcosahedronGeometry(0.3, 1);
    bellyGeo.scale(1.0, 0.8, 0.9);
    const bellyMesh = new THREE.Mesh(bellyGeo, mat(colorScheme.belly));
    bellyMesh.position.set(0.1, -0.1, 0);
    group.add(bellyMesh);

    // Head
    const headGeo = new THREE.IcosahedronGeometry(0.28, 1);
    const head = new THREE.Mesh(headGeo, bodyMat2);
    head.position.set(0.45, 0.1, 0);
    head.castShadow = true;
    group.add(head);

    // Cheeks
    const cheekGeo = new THREE.IcosahedronGeometry(0.1, 1);
    const cheekMat = mat(0xffaaaa);
    const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
    cheekL.position.set(0.55, -0.05, 0.15);
    group.add(cheekL);
    const cheekR = new THREE.Mesh(cheekGeo, cheekMat);
    cheekR.position.set(0.55, -0.05, -0.15);
    group.add(cheekR);

    // Ears
    const earGeo = new THREE.SphereGeometry(0.1, 5, 4);
    const earMat = mat(0xffaaaa);
    const earL = new THREE.Mesh(earGeo, earMat);
    earL.position.set(0.35, 0.3, 0.18);
    earL.scale.set(1, 1.3, 0.6);
    group.add(earL);
    const earR = new THREE.Mesh(earGeo, earMat);
    earR.position.set(0.35, 0.3, -0.18);
    earR.scale.set(1, 1.3, 0.6);
    group.add(earR);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.05, 6, 6);
    const eyeMat = mat(0x111111);
    const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    eyeL.position.set(0.62, 0.12, 0.1);
    group.add(eyeL);
    const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
    eyeR.position.set(0.62, 0.12, -0.1);
    group.add(eyeR);

    // Nose
    const noseGeo = new THREE.SphereGeometry(0.04, 5, 5);
    const nose = new THREE.Mesh(noseGeo, mat(0xff6688));
    nose.position.set(0.72, 0.05, 0);
    group.add(nose);

    // Legs (4 tiny stubs)
    const legGeo = new THREE.CylinderGeometry(0.06, 0.05, 0.2, 5);
    const legMat = mat(colorScheme.body);
    const legPositions = [
        [0.2, -0.35, 0.15], [0.2, -0.35, -0.15],
        [-0.2, -0.35, 0.15], [-0.2, -0.35, -0.15],
    ];
    legPositions.forEach((pos, i) => {
        const leg = new THREE.Mesh(legGeo, legMat);
        leg.position.set(...pos);
        leg.userData.legIndex = i;
        group.add(leg);
    });

    // Tail (tiny nub)
    const tailGeo = new THREE.SphereGeometry(0.07, 4, 4);
    const tail = new THREE.Mesh(tailGeo, bodyMat2);
    tail.position.set(-0.48, 0, 0);
    group.add(tail);

    return group;
}

// --- Create Hamsters ---
const hamsters = [];
const hamsterNames = ['Nibbles', 'Peanut', 'Cinnamon', 'Snowball'];

for (let i = 0; i < 4; i++) {
    const h = createHamster(hamsterColors[i], hamsterNames[i]);
    const angle = (i / 4) * Math.PI * 2;
    h.position.set(Math.cos(angle) * 2, 1.0, Math.sin(angle) * 2);
    h.rotation.y = Math.random() * Math.PI * 2;
    scene.add(h);
    hamsters.push(h);
}

// --- Small Toy Ball ---
const toyBallGeo = new THREE.IcosahedronGeometry(0.25, 1);
const toyBallMat = mat(0x66ff66);
const toyBall = new THREE.Mesh(toyBallGeo, toyBallMat);
toyBall.position.set(0, 0.85, -1.5);
toyBall.castShadow = true;
scene.add(toyBall);
let toyBallVel = new THREE.Vector2(0, 0);

// --- Hideout (small house) ---
const houseGroup = new THREE.Group();
houseGroup.position.set(1.5, 0.6, -2);

const houseBody = new THREE.BoxGeometry(1.2, 0.9, 1.0);
const houseMat = mat(0xffaa44);
const houseBodyMesh = new THREE.Mesh(houseBody, houseMat);
houseBodyMesh.castShadow = true;
houseGroup.add(houseBodyMesh);

const roofGeo = new THREE.ConeGeometry(0.9, 0.6, 4);
const roofMat = mat(0xff6666);
const roof = new THREE.Mesh(roofGeo, roofMat);
roof.position.y = 0.7;
roof.rotation.y = Math.PI / 4;
roof.castShadow = true;
houseGroup.add(roof);

// Door hole
const doorGeo = new THREE.BoxGeometry(0.3, 0.4, 0.05);
const doorMat = mat(0x332211);
const door = new THREE.Mesh(doorGeo, doorMat);
door.position.set(0, -0.1, 0.5);
houseGroup.add(door);

scene.add(houseGroup);

// --- Behavior Update ---
const CAGE_BOUNDS = { x: 4.0, z: 3.0 };
const WHEEL_POS = new THREE.Vector3(3, 1.0, 0);
const BOWL_POS = new THREE.Vector3(-2.5, 0.6, 1.5);

function updateHamster(hamster, dt, time) {
    const ud = hamster.userData;
    ud.timer -= dt;

    // State transitions
    if (ud.timer <= 0) {
        const roll = Math.random();
        if (ud.state === 'idle') {
            if (roll < 0.4) {
                ud.state = 'walking';
                ud.direction.set(Math.random() - 0.5, 0, Math.random() - 0.5).normalize();
                ud.timer = 1 + Math.random() * 2;
            } else if (roll < 0.7) {
                ud.state = 'approach_wheel';
                ud.targetPoint = new THREE.Vector3(3, 1.0, (Math.random() - 0.5) * 0.5);
                ud.timer = 4 + Math.random() * 3;
            } else if (roll < 0.9) {
                ud.state = 'approach_bowl';
                ud.targetPoint = new THREE.Vector3(-2.5 + (Math.random()-0.5)*0.5, 0.6, 1.5 + (Math.random()-0.5)*0.5);
                ud.timer = 3 + Math.random() * 2;
            } else {
                ud.state = 'walking';
                ud.direction.set(Math.random() - 0.5, 0, Math.random() - 0.5).normalize();
                ud.timer = 1 + Math.random() * 2;
            }
        } else if (ud.state === 'walking') {
            ud.state = 'idle';
            ud.timer = 0.5 + Math.random() * 2;
        } else if (ud.state === 'approach_wheel') {
            ud.state = 'running_wheel';
            ud.timer = 3 + Math.random() * 3;
        } else if (ud.state === 'running_wheel') {
            ud.state = 'idle';
            ud.timer = 1 + Math.random() * 2;
            ud.targetPoint = null;
        } else if (ud.state === 'approach_bowl') {
            ud.state = 'eating';
            ud.timer = 2 + Math.random() * 2;
        } else if (ud.state === 'eating') {
            ud.state = 'idle';
            ud.timer = 1 + Math.random() * 2;
            ud.targetPoint = null;
        }
    }

    // Movement
    let speed = 0;
    if (ud.state === 'walking') {
        speed = ud.speed;
        // Bounce off walls
        if (Math.abs(hamster.position.x) > CAGE_BOUNDS.x) {
            ud.direction.x *= -1;
            hamster.position.x = Math.sign(hamster.position.x) * CAGE_BOUNDS.x;
        }
        if (Math.abs(hamster.position.z) > CAGE_BOUNDS.z) {
            ud.direction.z *= -1;
            hamster.position.z = Math.sign(hamster.position.z) * CAGE_BOUNDS.z;
        }
        hamster.position.x += ud.direction.x * speed * dt;
        hamster.position.z += ud.direction.z * speed * dt;
    } else if (ud.state === 'approach_wheel' || ud.state === 'approach_bowl') {
        if (ud.targetPoint) {
            const dir = ud.targetPoint.clone().sub(hamster.position);
            dir.y = 0;
            const dist = dir.length();
            if (dist > 0.5) {
                dir.normalize();
                speed = ud.speed * 1.2;
                hamster.position.x += dir.x * speed * dt;
                hamster.position.z += dir.z * speed * dt;
            }
        }
    } else if (ud.state === 'running_wheel') {
        // Stay near wheel, bounce slightly
        const toCenter = WHEEL_POS.clone().sub(hamster.position);
        toCenter.y = 0;
        if (toCenter.length() > 1.0) {
            hamster.position.lerp(WHEEL_POS, dt * 3);
        }
        wheelTargetSpin = 8;
    }

    // Rotate to face movement direction
    if (ud.state === 'walking' || ud.state === 'approach_wheel' || ud.state === 'approach_bowl') {
        const targetRot = Math.atan2(ud.direction.x, ud.direction.z);
        let diff = targetRot - hamster.rotation.y;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        hamster.rotation.y += diff * dt * 5;
    }

    // Bob animation when walking
    if (ud.state === 'walking' || ud.state === 'approach_wheel' || ud.state === 'approach_bowl') {
        hamster.position.y = 1.0 + Math.sin(time * 8 + ud.bobPhase) * 0.05;
    } else {
        hamster.position.y += (1.0 - hamster.position.y) * dt * 5;
    }

    // Idle wiggle (ears)
    if (ud.state === 'idle') {
        ud.earWiggle = Math.sin(time * 3 + ud.bobPhase) * 0.1;
    } else {
        ud.earWiggle *= 0.9;
    }

    // Clamp position
    hamster.position.x = Math.max(-CAGE_BOUNDS.x, Math.min(CAGE_BOUNDS.x, hamster.position.x));
    hamster.position.z = Math.max(-CAGE_BOUNDS.z, Math.min(CAGE_BOUNDS.z, hamster.position.z));
}

// --- Toy Ball Interaction ---
function updateToyBall(dt) {
    toyBall.position.x += toyBallVel.x * dt;
    toyBall.position.z += toyBallVel.y * dt;
    toyBallVel.multiplyScalar(0.95);

    // Bounce off bounds
    if (Math.abs(toyBall.position.x) > CAGE_BOUNDS.x) {
        toyBallVel.x *= -0.7;
        toyBall.position.x = Math.sign(toyBall.position.x) * CAGE_BOUNDS.x;
    }
    if (Math.abs(toyBall.position.z) > CAGE_BOUNDS.z) {
        toyBallVel.y *= -0.7;
        toyBall.position.z = Math.sign(toyBall.position.z) * CAGE_BOUNDS.z;
    }

    // Hamster collision with ball
    hamsters.forEach(h => {
        const dist = new THREE.Vector2(h.position.x - toyBall.position.x, h.position.z - toyBall.position.z).length();
        if (dist < 0.6) {
            const push = new THREE.Vector2(
                toyBall.position.x - h.position.x,
                toyBall.position.z - h.position.z
            ).normalize().multiplyScalar(2.5);
            toyBallVel.x += push.x;
            toyBallVel.y += push.y;
        }
    });

    // Ball rolling rotation
    const speed2 = Math.sqrt(toyBallVel.x * toyBallVel.x + toyBallVel.y * toyBallVel.y);
    if (speed2 > 0.01) {
        toyBall.rotation.z -= toyBallVel.x * dt * 3;
        toyBall.rotation.x += toyBallVel.y * dt * 3;
    }
}

// --- Animation Loop ---
const clock = new THREE.Clock();
let time = 0;

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    time += dt;

    // Update hamsters
    hamsters.forEach(h => updateHamster(h, dt, time));

    // Wheel spin
    wheelSpinSpeed += (wheelTargetSpin - wheelSpinSpeed) * dt * 3;
    wheelRing.rotation.z += wheelSpinSpeed * dt;
    wheelTargetSpin *= 0.98; // decay

    // Toy ball
    updateToyBall(dt);

    // Gentle scene sway
    pointLight.intensity = 0.5 + Math.sin(time * 0.5) * 0.1;

    controls.update();
    renderer.render(scene, camera);
}

animate();

// --- Resize ---
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
- 🟪 **Cage** — wireframe bars on all sides with a crossbar top
- 🟫 **Tray/Floor** — pink base with scattered wood shaving bedding
- 🐹 **4 Hamsters** — each with unique colors (golden, white, brown, pink), built from low-poly icosahedrons with cheeks, ears, eyes, nose, legs, and tail nub
- 🎡 **Wheel** — spinning wheel on a stand that activates when hamsters approach
- 🥣 **Food Bowl** — with tiny pellet meshes inside
- 💧 **Water Bottle** — translucent cylinder mounted on cage wall
- 🏠 **Hideout House** — small box with a pyramid roof and door
- ⚽ **Toy Ball** — a green ball that hamsters push around

**Behavior System:**
- State machine: `idle` → `walking` → `approach_wheel` → `running_wheel` → `idle` (and similar for bowl)
- Hamsters wander, bounce off walls, approach the wheel to make it spin, and seek the food bowl
- Walking bob animation, ear wiggle when idle
- Ball gets pushed by hamster collisions with physics-like velocity decay

**Controls:** Drag to orbit camera, scroll to zoom.