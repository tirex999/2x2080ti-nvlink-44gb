```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Low-Poly Hamster Playground</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { overflow: hidden; background: #2a1f3d; font-family: 'Segoe UI', sans-serif; }
        canvas { display: block; }
        #info {
            position: absolute; top: 15px; left: 15px;
            color: #fff; background: rgba(0,0,0,0.5);
            padding: 10px 16px; border-radius: 12px;
            font-size: 14px; pointer-events: none;
        }
        #info h3 { margin-bottom: 4px; color: #ffcc66; }
    </style>
</head>
<body>
<div id="info">
    <h3>🐹 Hamster Playground</h3>
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

// ─── Scene Setup ───────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x3d2b56);
scene.fog = new THREE.Fog(0x3d2b56, 18, 35);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(7, 6, 9);

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
controls.maxDistance = 20;
controls.target.set(0, 1, 0);

// ─── Lights ────────────────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0xffeedd, 0.5);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.2);
dirLight.position.set(5, 8, 4);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(1024, 1024);
dirLight.shadow.camera.near = 1;
dirLight.shadow.camera.far = 25;
dirLight.shadow.camera.left = -8;
dirLight.shadow.camera.right = 8;
dirLight.shadow.camera.top = 8;
dirLight.shadow.camera.bottom = -8;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0xaaccff, 0.3);
fillLight.position.set(-4, 3, -3);
scene.add(fillLight);

const pointLight = new THREE.PointLight(0xffaa44, 0.6, 10);
pointLight.position.set(0, 4, 0);
scene.add(pointLight);

// ─── Materials ─────────────────────────────────────────────────
const mat = (color) => new THREE.MeshStandardMaterial({ color, flatShading: true });
const matEmissive = (color, intensity) => new THREE.MeshStandardMaterial({ 
    color, flatShading: true, emissive: color, emissiveIntensity: intensity 
});

// ─── Floor / Tray ──────────────────────────────────────────────
const trayGroup = new THREE.Group();

// Main tray base
const trayBase = new THREE.Mesh(
    new THREE.CylinderGeometry(4.5, 4.5, 0.4, 8),
    mat(0xf4e6c8)
);
trayBase.position.y = 0.2;
trayBase.receiveShadow = true;
trayGroup.add(trayBase);

// Bedding (small scattered cubes for texture)
for (let i = 0; i < 40; i++) {
    const size = 0.15 + Math.random() * 0.2;
    const bedding = new THREE.Mesh(
        new THREE.BoxGeometry(size, 0.08, size),
        mat([0xfce8b2, 0xe8d5a0, 0xfff3cc, 0xf0dcc0][Math.floor(Math.random() * 4)])
    );
    const angle = Math.random() * Math.PI * 2;
    const dist = Math.random() * 3.8;
    bedding.position.set(Math.cos(angle) * dist, 0.44, Math.sin(angle) * dist);
    bedding.rotation.y = Math.random() * Math.PI;
    bedding.receiveShadow = true;
    trayGroup.add(bedding);
}

scene.add(trayGroup);

// ─── Cage Bars ─────────────────────────────────────────────────
const cageGroup = new THREE.Group();
const barMat = mat(0x888899);

for (let i = 0; i < 16; i++) {
    const angle = (i / 16) * Math.PI * 2;
    const bar = new THREE.Mesh(
        new THREE.CylinderGeometry(0.04, 0.04, 3.5, 6),
        barMat
    );
    bar.position.set(Math.cos(angle) * 4.4, 2.15, Math.sin(angle) * 4.4);
    cageGroup.add(bar);
}

// Top ring
const topRing = new THREE.Mesh(
    new THREE.TorusGeometry(4.4, 0.06, 8, 16),
    barMat
);
topRing.position.y = 3.9;
topRing.rotation.x = Math.PI / 2;
cageGroup.add(topRing);

// Bottom ring
const bottomRing = new THREE.Mesh(
    new THREE.TorusGeometry(4.4, 0.06, 8, 16),
    barMat
);
bottomRing.position.y = 0.5;
bottomRing.rotation.x = Math.PI / 2;
cageGroup.add(bottomRing);

// Middle ring
const midRing = new THREE.Mesh(
    new THREE.TorusGeometry(4.4, 0.05, 8, 16),
    barMat
);
midRing.position.y = 2.2;
midRing.rotation.x = Math.PI / 2;
cageGroup.add(midRing);

// Lid handle
const handle = new THREE.Mesh(
    new THREE.TorusGeometry(0.4, 0.06, 8, 12),
    mat(0xaaaacc)
);
handle.position.y = 4.1;
cageGroup.add(handle);

scene.add(cageGroup);

// ─── Hamster Wheel ─────────────────────────────────────────────
const wheelGroup = new THREE.Group();

// Wheel rim (torus)
const wheelRim = new THREE.Mesh(
    new THREE.TorusGeometry(1.1, 0.12, 8, 24),
    mat(0xff6b9d)
);
wheelRim.castShadow = true;
wheelGroup.add(wheelRim);

// Wheel spokes
for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2;
    const spoke = new THREE.Mesh(
        new THREE.CylinderGeometry(0.03, 0.03, 1.05, 4),
        mat(0xff8ab5)
    );
    spoke.position.set(Math.cos(angle) * 0.52, Math.sin(angle) * 0.52, 0);
    spoke.rotation.z = angle + Math.PI / 2;
    wheelGroup.add(spoke);
}

// Wheel center hub
const hub = new THREE.Mesh(
    new THREE.CylinderGeometry(0.15, 0.15, 0.3, 8),
    mat(0xcc4477)
);
hub.rotation.x = Math.PI / 2;
wheelGroup.add(hub);

// Wheel stand (A-frame)
const standMat = mat(0x7c6b5a);
const standL = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.2, 6), standMat);
standL.position.set(-1.0, 1.1, 0);
standL.rotation.z = 0.3;
wheelGroup.add(standL);

const standR = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.2, 6), standMat);
standR.position.set(1.0, 1.1, 0);
standR.rotation.z = -0.3;
wheelGroup.add(standR);

wheelGroup.position.set(2.8, 1.5, -1.5);
wheelGroup.rotation.y = -0.4;
scene.add(wheelGroup);

// ─── Food Bowl ─────────────────────────────────────────────────
const bowlGroup = new THREE.Group();
const bowl = new THREE.Mesh(
    new THREE.CylinderGeometry(0.5, 0.35, 0.35, 8),
    mat(0x4ecdc4)
);
bowl.position.y = 0.6;
bowl.castShadow = true;
bowlGroup.add(bowl);

// Food pellets inside bowl
for (let i = 0; i < 6; i++) {
    const pellet = new THREE.Mesh(
        new THREE.DodecahedronGeometry(0.08, 0),
        mat([0xd4a574, 0xb8956a, 0xc9a87c][i % 3])
    );
    const a = (i / 6) * Math.PI * 2;
    pellet.position.set(Math.cos(a) * 0.2, 0.72, Math.sin(a) * 0.2);
    bowlGroup.add(pellet);
}

bowlGroup.position.set(-2.5, 0, 1.5);
scene.add(bowlGroup);

// ─── Tunnel ────────────────────────────────────────────────────
const tunnelGroup = new THREE.Group();
const tunnelOuter = new THREE.Mesh(
    new THREE.CylinderGeometry(0.55, 0.55, 2.2, 8, 1, true),
    mat(0x95e1d3)
);
tunnelOuter.rotation.z = Math.PI / 2;
tunnelGroup.add(tunnelOuter);

// Tunnel end caps (rings)
const ringMat = mat(0x6bc4b5);
const ring1 = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.06, 6, 12), ringMat);
ring1.position.x = 1.1;
ring1.rotation.y = Math.PI / 2;
tunnelGroup.add(ring1);

const ring2 = new THREE.Mesh(new THREE.TorusGeometry(0.55, 0.06, 6, 12), ringMat);
ring2.position.x = -1.1;
ring2.rotation.y = Math.PI / 2;
tunnelGroup.add(ring2);

tunnelGroup.position.set(-1.5, 0.75, -2.2);
tunnelGroup.rotation.y = 0.6;
scene.add(tunnelGroup);

// ─── Create Hamster Function ───────────────────────────────────
function createHamster(color, size = 1) {
    const hamster = new THREE.Group();
    const bodyColor = mat(color);
    const bellyColor = mat(new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.4));

    // Body (main ellipsoid)
    const body = new THREE.Mesh(
        new THREE.SphereGeometry(0.35 * size, 6, 5),
        bodyColor
    );
    body.scale.set(1.3, 1.0, 1.1);
    body.position.y = 0.35 * size;
    body.castShadow = true;
    hamster.add(body);

    // Belly (lighter underside)
    const belly = new THREE.Mesh(
        new THREE.SphereGeometry(0.28 * size, 6, 4),
        bellyColor
    );
    belly.scale.set(1.2, 0.7, 1.0);
    belly.position.y = 0.22 * size;
    hamster.add(belly);

    // Head
    const head = new THREE.Mesh(
        new THREE.SphereGeometry(0.22 * size, 6, 5),
        bodyColor
    );
    head.scale.set(1.1, 1.0, 1.1);
    head.position.set(0.35 * size, 0.42 * size, 0);
    head.castShadow = true;
    hamster.add(head);

    // Cheeks (puffy!)
    const cheekL = new THREE.Mesh(
        new THREE.SphereGeometry(0.12 * size, 5, 4),
        bellyColor
    );
    cheekL.position.set(0.42 * size, 0.38 * size, 0.12 * size);
    hamster.add(cheekL);

    const cheekR = new THREE.Mesh(
        new THREE.SphereGeometry(0.12 * size, 5, 4),
        bellyColor
    );
    cheekR.position.set(0.42 * size, 0.38 * size, -0.12 * size);
    hamster.add(cheekR);

    // Ears
    const earMat = mat(new THREE.Color(color).lerp(new THREE.Color(0xffaaaa), 0.3));
    const earL = new THREE.Mesh(new THREE.SphereGeometry(0.09 * size, 5, 4), earMat);
    earL.position.set(0.28 * size, 0.62 * size, 0.12 * size);
    earL.scale.set(1, 1.3, 0.7);
    hamster.add(earL);

    const earR = new THREE.Mesh(new THREE.SphereGeometry(0.09 * size, 5, 4), earMat);
    earR.position.set(0.28 * size, 0.62 * size, -0.12 * size);
    earR.scale.set(1, 1.3, 0.7);
    hamster.add(earR);

    // Eyes (big cute eyes!)
    const eyeMat = matEmissive(0x222222, 0.1);
    const eyeWhiteMat = mat(0xffffff);
    
    const eyeWhiteL = new THREE.Mesh(new THREE.SphereGeometry(0.06 * size, 6, 5), eyeWhiteMat);
    eyeWhiteL.position.set(0.52 * size, 0.48 * size, 0.1 * size);
    hamster.add(eyeWhiteL);

    const eyeWhiteR = new THREE.Mesh(new THREE.SphereGeometry(0.06 * size, 6, 5), eyeWhiteMat);
    eyeWhiteR.position.set(0.52 * size, 0.48 * size, -0.1 * size);
    hamster.add(eyeWhiteR);

    const pupilL = new THREE.Mesh(new THREE.SphereGeometry(0.035 * size, 6, 5), eyeMat);
    pupilL.position.set(0.56 * size, 0.48 * size, 0.1 * size);
    hamster.add(pupilL);

    const pupilR = new THREE.Mesh(new THREE.SphereGeometry(0.035 * size, 6, 5), eyeMat);
    pupilR.position.set(0.56 * size, 0.48 * size, -0.1 * size);
    hamster.add(pupilR);

    // Nose (tiny pink)
    const nose = new THREE.Mesh(
        new THREE.SphereGeometry(0.03 * size, 5, 4),
        mat(0xff8899)
    );
    nose.position.set(0.58 * size, 0.4 * size, 0);
    hamster.add(nose);

    // Tiny legs
    const legMat = mat(new THREE.Color(color).lerp(new THREE.Color(0x666666), 0.2));
    const legPositions = [
        { x: 0.15, z: 0.15 }, { x: 0.15, z: -0.15 },
        { x: -0.2, z: 0.15 }, { x: -0.2, z: -0.15 }
    ];
    const legs = [];
    legPositions.forEach(pos => {
        const leg = new THREE.Mesh(
            new THREE.CylinderGeometry(0.04 * size, 0.035 * size, 0.2 * size, 5),
            legMat
        );
        leg.position.set(pos.x * size, 0.1 * size, pos.z * size);
        hamster.add(leg);
        legs.push(leg);
    });

    // Tail (tiny nub)
    const tail = new THREE.Mesh(
        new THREE.SphereGeometry(0.06 * size, 5, 4),
        bodyColor
    );
    tail.position.set(-0.45 * size, 0.3 * size, 0);
    tail.scale.set(0.8, 0.8, 0.8);
    hamster.add(tail);

    return { group: hamster, legs, body, head };
}

// ─── Create Hamsters ───────────────────────────────────────────
const hamsterColors = [0xf4a460, 0xc9b896, 0x8b7355, 0xffccaa, 0xbbaa88, 0xe8c9a0];
const hamsters = [];

for (let i = 0; i < 6; i++) {
    const h = createHamster(hamsterColors[i], 0.9 + Math.random() * 0.3);
    const angle = (i / 6) * Math.PI * 2 + Math.random() * 0.5;
    const dist = 1.5 + Math.random() * 2;
    h.group.position.set(Math.cos(angle) * dist, 0.44, Math.sin(angle) * dist);
    h.group.rotation.y = angle + Math.PI;
    scene.add(h.group);

    hamsters.push({
        mesh: h.group,
        legs: h.legs,
        speed: 0.3 + Math.random() * 0.4,
        state: 'walk', // walk, pause, turn, wheel
        targetAngle: Math.random() * Math.PI * 2,
        timer: Math.random() * 3,
        walkTime: 2 + Math.random() * 3,
        pauseTime: 1 + Math.random() * 2,
        legPhase: Math.random() * Math.PI * 2,
        assignedWheel: i < 2, // first two use the wheel
        bobPhase: Math.random() * Math.PI * 2,
        size: 0.9 + Math.random() * 0.3
    });
}

// ─── Animation Loop ────────────────────────────────────────────
const clock = new THREE.Clock();
let wheelRotation = 0;
let wheelActive = false;

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;

    // Update hamsters
    let anyOnWheel = false;

    hamsters.forEach((h, idx) => {
        h.timer -= dt;

        if (h.state === 'walk') {
            // Move forward
            const speed = h.speed * dt;
            h.mesh.position.x += Math.cos(h.mesh.rotation.y) * speed;
            h.mesh.position.z += Math.sin(h.mesh.rotation.y) * speed;

            // Keep inside cage bounds
            const distFromCenter = Math.sqrt(
                h.mesh.position.x ** 2 + h.mesh.position.z ** 2
            );
            if (distFromCenter > 3.6) {
                // Turn back toward center
                const angleToCenter = Math.atan2(-h.mesh.position.z, -h.mesh.position.x);
                h.mesh.rotation.y = angleToCenter;
            }

            // Leg animation (walking bob)
            h.legPhase += dt * 10;
            h.legs.forEach((leg, li) => {
                const offset = (li % 2 === 0 ? 1 : -1) * Math.sin(h.legPhase) * 0.03;
                leg.position.y = 0.1 * h.size + offset;
            });

            // Body bob
            h.mesh.position.y = 0.44 + Math.sin(h.legPhase) * 0.015;

            // Check timer for state change
            if (h.timer <= 0) {
                if (h.assignedWheel && !anyOnWheel) {
                    // Head to wheel
                    h.state = 'turn';
                    h.targetAngle = Math.atan2(
                        -1.5 - h.mesh.position.z,
                        2.8 - h.mesh.position.x
                    );
                    h.timer = 1.5;
                } else {
                    h.state = 'pause';
                    h.timer = h.pauseTime;
                }
            }

        } else if (h.state === 'pause') {
            // Idle - slight head bob
            h.mesh.position.y = 0.44 + Math.sin(time * 2 + h.bobPhase) * 0.01;
            
            // Occasional look around
            h.mesh.rotation.y += Math.sin(time * 0.5 + idx) * 0.005;

            if (h.timer <= 0) {
                h.state = 'walk';
                h.timer = h.walkTime;
                h.targetAngle = h.mesh.rotation.y + (Math.random() - 0.5) * 1.5;
            }

        } else if (h.state === 'turn') {
            // Smoothly turn toward target angle
            let diff = h.targetAngle - h.mesh.rotation.y;
            while (diff > Math.PI) diff -= Math.PI * 2;
            while (diff < -Math.PI) diff += Math.PI * 2;
            h.mesh.rotation.y += diff * dt * 3;

            if (h.timer <= 0) {
                if (h.assignedWheel && !anyOnWheel) {
                    h.state = 'wheel';
                    anyOnWheel = true;
                    // Position on wheel
                    h.mesh.position.set(2.8, 1.5, -1.5);
                    h.mesh.rotation.y = -0.4 + Math.PI / 2;
                } else {
                    h.state = 'walk';
                    h.timer = h.walkTime;
                }
            }

        } else if (h.state === 'wheel') {
            anyOnWheel = true;
            // Running on wheel animation
            h.legPhase += dt * 15;
            h.legs.forEach((leg, li) => {
                const offset = (li % 2 === 0 ? 1 : -1) * Math.sin(h.legPhase) * 0.04;
                leg.position.y = 0.1 * h.size + offset;
            });

            // Slight body bob while running
            h.mesh.position.y = 1.5 + Math.sin(h.legPhase * 2) * 0.02;

            // Occasionally stop and go back
            if (Math.random() < 0.003) {
                h.state = 'walk';
                h.timer = h.walkTime;
                h.mesh.position.set(2.8 + Math.random() - 0.5, 0.44, -1.5 + Math.random() - 0.5);
            }
        }

        // Wheel hamsters get a slight lean
        if (h.state === 'wheel') {
            h.mesh.rotation.z = Math.sin(h.legPhase * 0.5) * 0.05;
        } else {
            h.mesh.rotation.z *= 0.95; // ease back
        }
    });

    // Rotate wheel when hamster is on it
    if (anyOnWheel) {
        wheelRotation += dt * 4;
    } else {
        wheelRotation += dt * 0.2; // slow idle spin
    }
    wheelGroup.rotation.z = wheelRotation;

    // Gentle cage sway (very subtle)
    cageGroup.rotation.y = Math.sin(time * 0.3) * 0.01;

    // Bowl wobble when hamster near it
    const bowlDist = hamsters.reduce((min, h) => {
        const d = Math.sqrt(
            (h.mesh.position.x - (-2.5)) ** 2 + 
            (h.mesh.position.z - 1.5) ** 2
        );
        return Math.min(min, d);
    }, Infinity);
    if (bowlDist < 1.2) {
        bowlGroup.rotation.z = Math.sin(time * 5) * 0.05;
    } else {
        bowlGroup.rotation.z *= 0.9;
    }

    controls.update();
    renderer.render(scene, camera);
}

animate();

// ─── Resize Handler ────────────────────────────────────────────
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
- 🐹 **6 low-poly hamsters** with puffy cheeks, big eyes, tiny ears, and stubby legs
- 🎡 **A spinning wheel** that two hamsters run on (it speeds up when they're active)
- 🥣 **A food bowl** with pellets that wobbles when hamsters get close
- 🕳️ **A tunnel** for visual interest
- 🏠 **A round cage** with bars, rings, and a handle

**Hamster Behavior:**
- **Walking** — hamsters roam the tray, legs animate with a walking cycle
- **Pausing** — they stop, bob their heads, and look around
- **Turning** — smoothly rotate toward the wheel or new directions
- **Wheel running** — two designated hamsters climb onto the wheel and run (legs spin fast, body bobs)

**Visual Style:**
- Flat shading for a crisp low-poly look
- Warm pastel colors (peach, tan, cream)
- Soft shadows and fog for depth
- Bedding scattered across the tray floor

Just save as `index.html` and open in any modern browser — no build step needed.