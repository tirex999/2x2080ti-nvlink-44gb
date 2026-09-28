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
    position: absolute; top: 20px; left: 20px; color: #fff;
    background: rgba(0,0,0,0.5); padding: 16px 22px; border-radius: 14px;
    backdrop-filter: blur(8px); pointer-events: none;
  }
  #ui h1 { font-size: 20px; margin-bottom: 6px; color: #ffd6a5; }
  #ui p { font-size: 13px; opacity: 0.8; }
  #hamster-names {
    position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 12px; pointer-events: none;
  }
  .name-tag {
    background: rgba(0,0,0,0.55); color: #fff; padding: 6px 14px;
    border-radius: 20px; font-size: 13px; backdrop-filter: blur(6px);
  }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Hamster Playground</h1>
  <p>Drag to rotate · Scroll to zoom</p>
</div>
<div id="hamster-names">
  <div class="name-tag" style="border-bottom:3px solid #ffd6a5;">Nugget</div>
  <div class="name-tag" style="border-bottom:3px solid #c9b1ff;">Pumpkin</div>
  <div class="name-tag" style="border-bottom:3px solid #a8e6cf;">Biscuit</div>
  <div class="name-tag" style="border-bottom:3px solid #ffb7b2;">Peanut</div>
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

// --- SCENE SETUP ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2d1b4e);
scene.fog = new THREE.Fog(0x2d1b4e, 25, 45);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(10, 9, 12);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1.5, 0);
controls.minDistance = 5;
controls.maxDistance = 25;
controls.maxPolarAngle = Math.PI / 2.1;

// --- LIGHTING ---
const ambientLight = new THREE.AmbientLight(0xffeedd, 0.5);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xfff5e6, 1.4);
dirLight.position.set(8, 12, 6);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.near = 1;
dirLight.shadow.camera.far = 30;
dirLight.shadow.camera.left = -10;
dirLight.shadow.camera.right = 10;
dirLight.shadow.camera.top = 10;
dirLight.shadow.camera.bottom = -10;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0xaaccff, 0.4);
fillLight.position.set(-5, 6, -4);
scene.add(fillLight);

const pointLight = new THREE.PointLight(0xff9944, 0.6, 15);
pointLight.position.set(0, 5, 0);
scene.add(pointLight);

// --- MATERIALS ---
function mat(color) {
  return new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.8, metalness: 0.1 });
}

// --- CAGE ---
const cageGroup = new THREE.Group();
const cageW = 12, cageD = 10, cageH = 5;
const barMat = new THREE.MeshStandardMaterial({ color: 0x888899, flatShading: true, roughness: 0.4, metalness: 0.7 });

// Floor tray
const trayGeo = new THREE.BoxGeometry(cageW + 1, 0.6, cageD + 1);
const trayMat = mat(0xd4a574);
const tray = new THREE.Mesh(trayGeo, trayMat);
tray.position.y = -0.3;
tray.receiveShadow = true;
cageGroup.add(tray);

// Bedding layer
const beddingGeo = new THREE.BoxGeometry(cageW - 0.2, 0.15, cageD - 0.2);
const beddingMat = mat(0xf5e6c8);
const bedding = new THREE.Mesh(beddingGeo, beddingMat);
bedding.position.y = 0.07;
bedding.receiveShadow = true;
cageGroup.add(bedding);

// Wood shavings (scattered)
for (let i = 0; i < 60; i++) {
  const sGeo = new THREE.BoxGeometry(
    0.1 + Math.random() * 0.2,
    0.05,
    0.05 + Math.random() * 0.15
  );
  const colors = [0xf0d9a0, 0xe8c878, 0xfaf0d4, 0xd4b876];
  const sMat = mat(colors[Math.floor(Math.random() * colors.length)]);
  const shaving = new THREE.Mesh(sGeo, sMat);
  shaving.position.set(
    (Math.random() - 0.5) * (cageW - 2),
    0.18,
    (Math.random() - 0.5) * (cageD - 2)
  );
  shaving.rotation.y = Math.random() * Math.PI;
  cageGroup.add(shaving);
}

// Vertical bars
const barGeo = new THREE.CylinderGeometry(0.06, 0.06, cageH, 6);
function addBar(x, z) {
  const bar = new THREE.Mesh(barGeo, barMat);
  bar.position.set(x, cageH / 2 + 0.3, z);
  bar.castShadow = true;
  cageGroup.add(bar);
}

const spacingX = cageW / 7;
const spacingZ = cageD / 6;
for (let i = 0; i <= 7; i++) {
  addBar(-cageW / 2 + i * spacingX, -cageD / 2);
  addBar(-cageW / 2 + i * spacingX, cageD / 2);
}
for (let i = 1; i < 6; i++) {
  addBar(-cageW / 2, -cageD / 2 + i * spacingZ);
  addBar(cageW / 2, -cageD / 2 + i * spacingZ);
}

// Top frame
const frameMat = new THREE.MeshStandardMaterial({ color: 0x666677, flatShading: true, roughness: 0.3, metalness: 0.8 });
const topFrameGeo1 = new THREE.BoxGeometry(cageW + 0.4, 0.2, 0.2);
const topFrameGeo2 = new THREE.BoxGeometry(0.2, 0.2, cageD + 0.4);
[[-cageD/2, cageH+0.3], [cageD/2, cageH+0.3]].forEach(([z, y]) => {
  const f = new THREE.Mesh(topFrameGeo1, frameMat);
  f.position.set(0, y, z);
  cageGroup.add(f);
});
[[-cageW/2, cageH+0.3], [cageW/2, cageH+0.3]].forEach(([x, y]) => {
  const f = new THREE.Mesh(topFrameGeo2, frameMat);
  f.position.set(x, y, 0);
  cageGroup.add(f);
});

// Horizontal bars (middle)
const hBarGeo1 = new THREE.CylinderGeometry(0.04, 0.04, cageW, 6);
const hBarGeo2 = new THREE.CylinderGeometry(0.04, 0.04, cageD, 6);
[1.5, 3.0, 4.5].forEach(y => {
  [-cageD/2, cageD/2].forEach(z => {
    const b = new THREE.Mesh(hBarGeo1, barMat);
    b.rotation.z = Math.PI / 2;
    b.position.set(0, y + 0.3, z);
    cageGroup.add(b);
  });
  [-cageW/2, cageW/2].forEach(x => {
    const b = new THREE.Mesh(hBarGeo2, barMat);
    b.rotation.x = Math.PI / 2;
    b.position.set(x, y + 0.3, 0);
    cageGroup.add(b);
  });
});

scene.add(cageGroup);

// --- HAMSTER WHEEL ---
const wheelGroup = new THREE.Group();
wheelGroup.position.set(4, 1.8, -3);

const wheelRadius = 1.6;
const wheelMat = mat(0x5bc0eb);

// Wheel ring (torus)
const ringGeo = new THREE.TorusGeometry(wheelRadius, 0.12, 8, 16);
const ring = new THREE.Mesh(ringGeo, wheelMat);
wheelGroup.add(ring);

// Inner ring
const innerRingGeo = new THREE.TorusGeometry(wheelRadius - 0.3, 0.06, 6, 12);
const innerRing = new THREE.Mesh(innerRingGeo, mat(0x4aa8d8));
wheelGroup.add(innerRing);

// Spokes
for (let i = 0; i < 8; i++) {
  const spokeGeo = new THREE.BoxGeometry(0.06, wheelRadius * 2 - 0.3, 0.06);
  const spoke = new THREE.Mesh(spokeGeo, mat(0x4aa8d8));
  spoke.rotation.z = (i / 8) * Math.PI;
  wheelGroup.add(spoke);
}

// Axle
const axleGeo = new THREE.CylinderGeometry(0.15, 0.15, 0.8, 8);
const axle = new THREE.Mesh(axleGeo, mat(0x888899));
axle.rotation.z = Math.PI / 2;
wheelGroup.add(axle);

// Stand
const standMat = mat(0x666677);
const standGeo = new THREE.BoxGeometry(0.3, 1.8, 0.3);
const stand1 = new THREE.Mesh(standGeo, standMat);
stand1.position.set(0, -0.9, 0.4);
wheelGroup.add(stand1);
const stand2 = stand1.clone();
stand2.position.set(0, -0.9, -0.4);
wheelGroup.add(stand2);

// Base
const baseGeo = new THREE.BoxGeometry(1.5, 0.2, 1.2);
const base = new THREE.Mesh(baseGeo, standMat);
base.position.set(0, -1.7, 0);
wheelGroup.add(base);

scene.add(wheelGroup);

// --- FOOD BOWL ---
const bowlGroup = new THREE.Group();
bowlGroup.position.set(-4, 0.15, 2);

const bowlGeo = new THREE.CylinderGeometry(0.7, 0.45, 0.5, 8);
const bowlMat = mat(0xff6b6b);
const bowl = new THREE.Mesh(bowlGeo, bowlMat);
bowlGroup.add(bowl);

// Food pellets inside
for (let i = 0; i < 8; i++) {
  const pelletGeo = new THREE.SphereGeometry(0.1, 4, 4);
  const pelletColors = [0xd4a056, 0x8B7355, 0xc9a96e];
  const pellet = new THREE.Mesh(pelletGeo, mat(pelletColors[i % 3]));
  const angle = (i / 8) * Math.PI * 2;
  const r = 0.2 + Math.random() * 0.2;
  pellet.position.set(Math.cos(angle) * r, 0.2, Math.sin(angle) * r);
  bowlGroup.add(pellet);
}
scene.add(bowlGroup);

// --- WATER BOTTLE ---
const bottleGroup = new THREE.Group();
bottleGroup.position.set(-5.5, 2.5, 0);

const bottleGeo = new THREE.CylinderGeometry(0.25, 0.25, 1.8, 8);
const bottleMat = new THREE.MeshStandardMaterial({ color: 0x88ccff, flatShading: true, transparent: true, opacity: 0.7 });
const bottle = new THREE.Mesh(bottleGeo, bottleMat);
bottleGroup.add(bottle);

const capGeo = new THREE.CylinderGeometry(0.15, 0.25, 0.3, 8);
const cap = new THREE.Mesh(capGeo, mat(0xcc4444));
cap.position.y = -1.0;
bottleGroup.add(cap);

const tubeGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.6, 6);
const tube = new THREE.Mesh(tubeGeo, mat(0xaaaaaa));
tube.position.y = -1.4;
bottleGroup.add(tube);

scene.add(bottleGroup);

// --- TUNNEL ---
const tunnelGroup = new THREE.Group();
tunnelGroup.position.set(-2, 0.5, -3);
tunnelGroup.rotation.y = Math.PI / 4;

const tunnelGeo = new THREE.CylinderGeometry(0.6, 0.6, 2.5, 8, 1, true);
const tunnelMat = new THREE.MeshStandardMaterial({ color: 0xffb347, flatShading: true, side: THREE.DoubleSide });
const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
tunnel.rotation.z = Math.PI / 2;
tunnelGroup.add(tunnel);

// Tunnel rings
for (let i = -1; i <= 1; i++) {
  const tRingGeo = new THREE.TorusGeometry(0.65, 0.08, 6, 8);
  const tRing = new THREE.Mesh(tRingGeo, mat(0xe89b30));
  tRing.position.x = i * 0.8;
  tRing.rotation.y = Math.PI / 2;
  tunnelGroup.add(tRing);
}
scene.add(tunnelGroup);

// --- HAMSTER CREATION ---
function createHamster(bodyColor, cheekColor) {
  const group = new THREE.Group();
  const bodyMat = mat(bodyColor);
  const bellyMat = mat(0xfff5e6);
  const earMat = mat(cheekColor || 0xffaaaa);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.2 });
  const noseMat = mat(0xff8888);

  // Body (rounded box)
  const bodyGeo = new THREE.SphereGeometry(0.45, 6, 5);
  bodyGeo.scale(1.3, 0.9, 0.85);
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.position.y = 0.4;
  body.castShadow = true;
  group.add(body);

  // Belly
  const bellyGeo = new THREE.SphereGeometry(0.35, 5, 4);
  bellyGeo.scale(1.1, 0.7, 0.7);
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.position.set(0.05, 0.32, 0);
  group.add(belly);

  // Head
  const headGeo = new THREE.SphereGeometry(0.32, 6, 5);
  headGeo.scale(1.1, 1, 0.95);
  const head = new THREE.Mesh(headGeo, bodyMat);
  head.position.set(0.5, 0.55, 0);
  head.castShadow = true;
  group.add(head);

  // Cheeks (puffy)
  const cheekGeo = new THREE.SphereGeometry(0.15, 5, 4);
  const cheekL = new THREE.Mesh(cheekGeo, bodyMat);
  cheekL.position.set(0.55, 0.45, 0.22);
  group.add(cheekL);
  const cheekR = cheekL.clone();
  cheekR.position.z = -0.22;
  group.add(cheekR);

  // Ears
  const earGeo = new THREE.SphereGeometry(0.12, 5, 4);
  earGeo.scale(1, 1.3, 0.6);
  const earL = new THREE.Mesh(earGeo, earMat);
  earL.position.set(0.4, 0.82, 0.18);
  group.add(earL);
  const earR = earL.clone();
  earR.position.z = -0.18;
  group.add(earR);

  // Inner ears
  const innerEarGeo = new THREE.SphereGeometry(0.07, 4, 3);
  const iEarL = new THREE.Mesh(innerEarGeo, mat(0xff9999));
  iEarL.position.set(0.42, 0.84, 0.19);
  group.add(iEarL);
  const iEarR = iEarL.clone();
  iEarR.position.z = -0.19;
  group.add(iEarR);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.07, 5, 4);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(0.72, 0.6, 0.14);
  group.add(eyeL);
  const eyeR = eyeL.clone();
  eyeR.position.z = -0.14;
  group.add(eyeR);

  // Eye shine
  const shineGeo = new THREE.SphereGeometry(0.025, 4, 3);
  const shineMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0.5 });
  const shineL = new THREE.Mesh(shineGeo, shineMat);
  shineL.position.set(0.76, 0.63, 0.16);
  group.add(shineL);
  const shineR = shineL.clone();
  shineR.position.z = -0.12;
  group.add(shineR);

  // Nose
  const noseGeo = new THREE.SphereGeometry(0.05, 4, 3);
  const nose = new THREE.Mesh(noseGeo, noseMat);
  nose.position.set(0.82, 0.52, 0);
  group.add(nose);

  // Feet
  const footGeo = new THREE.BoxGeometry(0.15, 0.08, 0.12);
  const feet = [];
  const footPositions = [
    [0.25, 0.04, 0.2], [0.25, 0.04, -0.2],
    [-0.2, 0.04, 0.2], [-0.2, 0.04, -0.2]
  ];
  footPositions.forEach(pos => {
    const foot = new THREE.Mesh(footGeo, mat(0xffaaaa));
    foot.position.set(...pos);
    group.add(foot);
    feet.push(foot);
  });

  // Tail (tiny nub)
  const tailGeo = new THREE.SphereGeometry(0.08, 4, 3);
  const tail = new THREE.Mesh(tailGeo, bodyMat);
  tail.position.set(-0.55, 0.35, 0);
  group.add(tail);

  // Whiskers (tiny lines)
  const whiskerMat = new THREE.LineBasicMaterial({ color: 0x444444 });
  for (let side of [-1, 1]) {
    for (let i = 0; i < 3; i++) {
      const points = [
        new THREE.Vector3(0.8, 0.5, side * 0.08),
        new THREE.Vector3(1.05, 0.48 + i * 0.04, side * (0.2 + i * 0.05))
      ];
      const wGeo = new THREE.BufferGeometry().setFromPoints(points);
      const whisker = new THREE.Line(wGeo, whiskerMat);
      group.add(whisker);
    }
  }

  return { group, feet, body, head, tail };
}

// --- HAMSTER BEHAVIOR ---
const BOUNDS = { x: 5, z: 4 };
const WHEEL_POS = new THREE.Vector3(4, 0, -3);
const BOWL_POS = new THREE.Vector3(-4, 0, 2);

class Hamster {
  constructor(bodyColor, cheekColor, startPos) {
    const parts = createHamster(bodyColor, cheekColor);
    this.model = parts.group;
    this.feet = parts.feet;
    this.body = parts.body;
    this.head = parts.head;
    this.tail = parts.tail;

    this.model.position.set(startPos.x, 0.15, startPos.z);
    scene.add(this.model);

    this.state = 'WANDER';
    this.stateTimer = Math.random() * 3 + 1;
    this.direction = Math.random() * Math.PI * 2;
    this.speed = 0.8 + Math.random() * 0.4;
    this.target = null;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.earWiggle = 0;
    this.interactType = null; // 'wheel' or 'bowl'
  }

  update(dt, time) {
    this.stateTimer -= dt;
    this.bobPhase += dt * (this.state === 'RUNNING' ? 12 : 4);
    this.earWiggle = Math.sin(time * 3 + this.bobPhase) * 0.05;

    switch (this.state) {
      case 'WANDER':
        this.wander(dt, time);
        break;
      case 'PAUSE':
        this.pause(dt, time);
        break;
      case 'TURN':
        this.turn(dt, time);
        break;
      case 'GO_WHEEL':
        this.goToTarget(WHEEL_POS, dt, time);
        break;
      case 'RUNNING':
        this.runOnWheel(dt, time);
        break;
      case 'GO_BOWL':
        this.goToTarget(BOWL_POS, dt, time);
        break;
      case 'EATING':
        this.eat(dt, time);
        break;
    }

    // Animate feet
    const isMoving = this.state === 'WANDER' || this.state === 'RUNNING' || this.state === 'GO_WHEEL' || this.state === 'GO_BOWL';
    this.feet.forEach((foot, i) => {
      if (isMoving) {
        foot.position.y = 0.04 + Math.abs(Math.sin(this.bobPhase + i * 1.5)) * 0.08;
      } else {
        foot.position.y = 0.04;
      }
    });

    // Tail wiggle
    this.tail.position.x = -0.55 + Math.sin(time * 5) * 0.02;
    this.tail.position.z = Math.sin(time * 4) * 0.03;

    // Ear wiggle
    this.model.children.forEach(child => {
      if (child.geometry && child.geometry.type === 'SphereGeometry' && child.position.y > 0.75) {
        child.rotation.z = this.earWiggle;
      }
    });
  }

  wander(dt, time) {
    const moveX = Math.cos(this.direction) * this.speed * dt;
    const moveZ = Math.sin(this.direction) * this.speed * dt;
    this.model.position.x += moveX;
    this.model.position.z += moveZ;

    // Bob body while walking
    this.body.position.y = 0.4 + Math.sin(this.bobPhase) * 0.03;

    // Face direction of movement
    this.model.rotation.y = -this.direction + Math.PI / 2;

    // Check bounds
    if (Math.abs(this.model.position.x) > BOUNDS.x || Math.abs(this.model.position.z) > BOUNDS.z) {
      this.state = 'TURN';
      this.stateTimer = 0.5;
    }

    // Random state changes
    if (this.stateTimer <= 0) {
      const r = Math.random();
      if (r < 0.3) {
        this.state = 'PAUSE';
        this.stateTimer = 1 + Math.random() * 2;
      } else if (r < 0.5) {
        this.state = 'TURN';
        this.stateTimer = 0.6;
      } else if (r < 0.7 && !this.target) {
        // Go to wheel or bowl
        if (Math.random() < 0.5) {
          this.state = 'GO_WHEEL';
          this.interactType = 'wheel';
        } else {
          this.state = 'GO_BOWL';
          this.interactType = 'bowl';
        }
      } else {
        this.direction += (Math.random() - 0.5) * Math.PI;
        this.stateTimer = 1 + Math.random() * 3;
      }
    }
  }

  pause(dt, time) {
    // Idle animation - slight body bob for breathing
    this.body.position.y = 0.4 + Math.sin(time * 2) * 0.01;
    if (this.stateTimer <= 0) {
      this.state = 'WANDER';
      this.direction += (Math.random() - 0.5) * Math.PI * 1.5;
      this.stateTimer = 1 + Math.random() * 3;
    }
  }

  turn(dt, time) {
    this.model.rotation.y += dt * 3;
    this.direction += dt * 3;
    if (this.stateTimer <= 0) {
      this.state = 'WANDER';
      this.stateTimer = 1 + Math.random() * 3;
    }
  }

  goToTarget(targetPos, dt, time) {
    const dx = targetPos.x - this.model.position.x;
    const dz = targetPos.z - this.model.position.z;
    const dist = Math.sqrt(dx * dx + dz * dz);

    if (dist < 1.2) {
      if (this.interactType === 'wheel') {
        this.state = 'RUNNING';
        this.stateTimer = 3 + Math.random() * 4;
      } else {
        this.state = 'EATING';
        this.stateTimer = 2 + Math.random() * 3;
      }
      return;
    }

    const angle = Math.atan2(dz, dx);
    this.model.position.x += Math.cos(angle) * this.speed * dt;
    this.model.position.z += Math.sin(angle) * this.speed * dt;
    this.model.rotation.y = -angle + Math.PI / 2;
    this.body.position.y = 0.4 + Math.sin(this.bobPhase) * 0.03;

    // Timeout fallback
    if (this.stateTimer === undefined) this.stateTimer = 10;
    this.stateTimer -= dt;
    if (this.stateTimer < -5) {
      this.state = 'WANDER';
      this.stateTimer = 1 + Math.random() * 2;
    }
  }

  runOnWheel(dt, time) {
    // Face the wheel
    const targetAngle = -Math.atan2(WHEEL_POS.z - this.model.position.z, WHEEL_POS.x - this.model.position.x) + Math.PI / 2;
    this.model.rotation.y += (targetAngle - this.model.rotation.y) * dt * 5;

    // Fast bobbing (running)
    this.body.position.y = 0.4 + Math.sin(this.bobPhase) * 0.06;
    this.head.position.y = 0.55 + Math.sin(this.bobPhase * 0.5) * 0.02;

    // Spin the wheel
    const ringChildren = wheelGroup.children;
    for (let i = 0; i < 10; i++) {
      if (ringChildren[i]) {
        // handled externally
      }
    }

    if (this.stateTimer <= 0) {
      this.state = 'WANDER';
      this.direction = Math.random() * Math.PI * 2;
      this.stateTimer = 1 + Math.random() * 3;
      this.interactType = null;
    }
  }

  eat(dt, time) {
    // Face the bowl
    const targetAngle = -Math.atan2(BOWL_POS.z - this.model.position.z, BOWL_POS.x - this.model.position.x) + Math.PI / 2;
    this.model.rotation.y += (targetAngle - this.model.rotation.y) * dt * 5;

    // Head bobbing (eating motion)
    this.head.position.y = 0.55 + Math.sin(this.bobPhase * 1.5) * 0.06;
    this.body.position.y = 0.4 + Math.sin(this.bobPhase * 0.7) * 0.02;

    if (this.stateTimer <= 0) {
      this.state = 'WANDER';
      this.direction = Math.random() * Math.PI * 2;
      this.stateTimer = 1 + Math.random() * 3;
      this.interactType = null;
    }
  }
}

// Create hamsters
const hamsters = [
  new Hamster(0xf5d6a0, 0xffb8b8, { x: 0, z: 0 }),      // Golden - Nugget
  new Hamster(0xc9a0dc, 0xffaaaa, { x: 2, z: 1 }),       // Purple-ish - Pumpkin
  new Hamster(0xb8d4a8, 0xffccbb, { x: -2, z: -1 }),     // Green-ish - Biscuit
  new Hamster(0xf0f0f0, 0xff9999, { x: -1, z: 2 }),      // White - Peanut
];

// --- ANIMATION LOOP ---
let wheelSpin = 0;
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.getElapsedTime();

  // Update hamsters
  hamsters.forEach(h => h.update(dt, time));

  // Check if any hamster is running on wheel
  const anyRunning = hamsters.some(h => h.state === 'RUNNING');
  if (anyRunning) {
    wheelSpin += dt * 8;
  } else {
    wheelSpin += dt * 0.3; // slow idle spin
  }

  // Rotate wheel (only the ring and spokes, not the stand)
  const wheelParts = wheelGroup.children.slice(0, 10); // ring, inner ring, spokes, axle
  wheelParts.forEach(child => {
    child.rotation.x = wheelSpin;
  });

  // Gentle light flicker
  pointLight.intensity = 0.6 + Math.sin(time * 2) * 0.1;

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

This creates a complete **Low-Poly Hamster Playground** with:

### 🐹 Features:
- **4 cute low-poly hamsters** (Nugget, Pumpkin, Biscuit, Peanut) with distinct pastel colors, puffy cheeks, tiny ears with inner ear detail, whiskers, eye shine highlights, and animated feet/tails/ears
- **Autonomous AI behavior** — each hamster wanders, pauses to breathe, turns around, and randomly decides to visit the wheel or food bowl
- **Interactive hamster wheel** that spins fast when a hamster "runs" on it (with fast bobbing animation) and slowly idles otherwise
- **Food bowl** with pellets — hamsters go there and do an eating head-bob animation
- **Full cage** with vertical bars, horizontal rails, top frame, wooden tray base, and scattered wood shavings for bedding
- **Water bottle**, **tunnel**, and atmospheric lighting with fog

### 🎮 Controls:
- **Drag** to orbit the camera
- **Scroll** to zoom in/out
- Camera is clamped so you can't go below the floor

### 🎨 Visual Style:
- Flat-shaded low-poly geometry throughout
- Warm pastel color palette
- Soft shadows and ACES tone mapping
- Cozy purple-blue background with fog