

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Low-Poly Hamster Playground</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; background: #2a1f3a; font-family: 'Segoe UI', sans-serif; }
  canvas { display: block; }
  #info {
    position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
    color: #fff; background: rgba(0,0,0,0.4); padding: 8px 20px;
    border-radius: 20px; font-size: 14px; pointer-events: none;
    backdrop-filter: blur(4px);
  }
</style>
</head>
<body>
<div id="info">🐹 Drag to orbit · Scroll to zoom</div>

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

// ─── SCENE SETUP ───────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87CEEB);
scene.fog = new THREE.Fog(0x87CEEB, 15, 30);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(5, 4, 6);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI / 2.1;
controls.minDistance = 3;
controls.maxDistance = 15;

// ─── LIGHTING ──────────────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0xfff5e6, 0.6);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xffeedd, 1.2);
sunLight.position.set(5, 8, 3);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.near = 1;
sunLight.shadow.camera.far = 20;
sunLight.shadow.camera.left = -5;
sunLight.shadow.camera.right = 5;
sunLight.shadow.camera.top = 5;
sunLight.shadow.camera.bottom = -5;
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xaaccff, 0.3);
fillLight.position.set(-3, 4, -2);
scene.add(fillLight);

// ─── MATERIALS HELPER ──────────────────────────────────────────
function mat(color, opts = {}) {
  return new THREE.MeshLambertMaterial({ color, ...opts });
}

// ─── CAGE / FLOOR ──────────────────────────────────────────────
function buildCage() {
  const group = new THREE.Group();

  // Base tray
  const trayGeo = new THREE.BoxGeometry(5, 0.3, 4);
  const tray = new THREE.Mesh(trayGeo, mat(0x8B5E3C));
  tray.position.y = 0.15;
  tray.receiveShadow = true;
  group.add(tray);

  // Inner floor (wood shavings look)
  const floorGeo = new THREE.BoxGeometry(4.6, 0.05, 3.6);
  const floor = new THREE.Mesh(floorGeo, mat(0xDEB887));
  floor.position.y = 0.32;
  floor.receiveShadow = true;
  group.add(floor);

  // Wood shaving bits (tiny colored boxes scattered)
  const shavingColors = [0xD2A679, 0xC49A6C, 0xE8C896, 0xBFA06A];
  for (let i = 0; i < 40; i++) {
    const s = 0.04 + Math.random() * 0.06;
    const geo = new THREE.BoxGeometry(s, s * 0.3, s * 2);
    const m = new THREE.Mesh(geo, mat(shavingColors[i % shavingColors.length]));
    m.position.set(
      (Math.random() - 0.5) * 4,
      0.36,
      (Math.random() - 0.5) * 3
    );
    m.rotation.y = Math.random() * Math.PI;
    group.add(m);
  }

  // Wire walls (thin cylinders as posts + horizontal bars)
  const postMat = mat(0xAAAAAA);
  const postGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.2, 6);

  // Corner posts
  const corners = [[-2.3, 1.9], [2.3, 1.9], [-2.3, -1.9], [2.3, -1.9]];
  corners.forEach(([x, z]) => {
    const post = new THREE.Mesh(postGeo, postMat);
    post.position.set(x, 0.9, z);
    group.add(post);
  });

  // Top frame bars
  const barGeoH = new THREE.CylinderGeometry(0.02, 0.02, 4.6, 4);
  const barGeoW = new THREE.CylinderGeometry(0.02, 0.02, 3.8, 4);

  const topBar1 = new THREE.Mesh(barGeoH, postMat);
  topBar1.rotation.z = Math.PI / 2;
  topBar1.position.set(0, 1.5, 1.9);
  group.add(topBar1);

  const topBar2 = new THREE.Mesh(barGeoH, postMat);
  topBar2.rotation.z = Math.PI / 2;
  topBar2.position.set(0, 1.5, -1.9);
  group.add(topBar2);

  const topBar3 = new THREE.Mesh(barGeoW, postMat);
  topBar3.rotation.x = Math.PI / 2;
  topBar3.position.set(2.3, 1.5, 0);
  group.add(topBar3);

  const topBar4 = new THREE.Mesh(barGeoW, postMat);
  topBar4.rotation.x = Math.PI / 2;
  topBar4.position.set(-2.3, 1.5, 0);
  group.add(topBar4);

  // Mid-level bars (horizontal)
  const midBar1 = new THREE.Mesh(barGeoH, postMat);
  midBar1.rotation.z = Math.PI / 2;
  midBar1.position.set(0, 0.9, 1.9);
  group.add(midBar1);

  const midBar2 = new THREE.Mesh(barGeoH, postMat);
  midBar2.rotation.z = Math.PI / 2;
  midBar2.position.set(0, 0.9, -1.9);
  group.add(midBar2);

  const midBar3 = new THREE.Mesh(barGeoW, postMat);
  midBar3.rotation.x = Math.PI / 2;
  midBar3.position.set(2.3, 0.9, 0);
  group.add(midBar3);

  const midBar4 = new THREE.Mesh(barGeoW, postMat);
  midBar4.rotation.x = Math.PI / 2;
  midBar4.position.set(-2.3, 0.9, 0);
  group.add(midBar4);

  // Vertical wire bars on sides (sparse)
  const vBarGeo = new THREE.CylinderGeometry(0.015, 0.015, 1.2, 4);
  for (let i = 1; i <= 3; i++) {
    const x = -2.3 + i * (4.6 / 4);
    // Front
    const b1 = new THREE.Mesh(vBarGeo, postMat);
    b1.position.set(x, 0.9, 1.9);
    group.add(b1);
    // Back
    const b2 = new THREE.Mesh(vBarGeo, postMat);
    b2.position.set(x, 0.9, -1.9);
    group.add(b2);
  }
  for (let i = 1; i <= 2; i++) {
    const z = -1.9 + i * (3.8 / 3);
    // Left
    const b1 = new THREE.Mesh(vBarGeo, postMat);
    b1.position.set(-2.3, 0.9, z);
    group.add(b1);
    // Right
    const b2 = new THREE.Mesh(vBarGeo, postMat);
    b2.position.set(2.3, 0.9, z);
    group.add(b2);
  }

  scene.add(group);
}

// ─── INTERACTIVE OBJECTS ───────────────────────────────────────
let wheelGroup;
let wheelSpin = 0;
let wheelSpeed = 0;

function buildWheel() {
  wheelGroup = new THREE.Group();

  // Axle
  const axleGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.0, 6);
  const axle = new THREE.Mesh(axleGeo, mat(0x999999));
  axle.rotation.z = Math.PI / 2;
  wheelGroup.add(axle);

  // Wheel rim
  const rimGeo = new THREE.TorusGeometry(0.5, 0.04, 6, 12);
  const rim = new THREE.Mesh(rimGeo, mat(0xFF6B6B));
  wheelGroup.add(rim);

  // Spokes
  const spokeGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.5, 4);
  for (let i = 0; i < 5; i++) {
    const spoke = new THREE.Mesh(spokeGeo, mat(0xFF8888));
    const angle = (i / 5) * Math.PI * 2;
    spoke.position.set(Math.cos(angle) * 0.25, Math.sin(angle) * 0.25, 0);
    spoke.rotation.z = angle + Math.PI / 2;
    wheelGroup.add(spoke);
  }

  // Center hub
  const hubGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.1, 6);
  const hub = new THREE.Mesh(hubGeo, mat(0xFF4444));
  hub.rotation.x = Math.PI / 2;
  wheelGroup.add(hub);

  // Stand
  const standGeo = new THREE.BoxGeometry(0.15, 0.4, 0.15);
  const standL = new THREE.Mesh(standGeo, mat(0x777777));
  standL.position.set(-0.4, -0.5, 0);
  wheelGroup.add(standL);
  const standR = new THREE.Mesh(standGeo, mat(0x777777));
  standR.position.set(0.4, -0.5, 0);
  wheelGroup.add(standR);

  // Base
  const baseGeo = new THREE.BoxGeometry(1.1, 0.06, 0.3);
  const base = new THREE.Mesh(baseGeo, mat(0x666666));
  base.position.y = -0.72;
  wheelGroup.add(base);

  wheelGroup.position.set(1.5, 0.75, -1.2);
  scene.add(wheelGroup);
}

// Food bowl
const BOWL_POS = new THREE.Vector3(-1.5, 0.35, 1.0);

function buildFoodBowl() {
  const group = new THREE.Group();

  // Bowl
  const bowlGeo = new THREE.CylinderGeometry(0.25, 0.15, 0.12, 8);
  const bowl = new THREE.Mesh(bowlGeo, mat(0x4ECDC4));
  bowl.position.y = 0.06;
  bowl.castShadow = true;
  group.add(bowl);

  // Food pellets
  const pelletGeo = new THREE.SphereGeometry(0.04, 4, 3);
  const pelletColors = [0xFFD700, 0xFFA500, 0x90EE90];
  for (let i = 0; i < 5; i++) {
    const p = new THREE.Mesh(pelletGeo, mat(pelletColors[i % 3]));
    p.position.set((Math.random() - 0.5) * 0.2, 0.14, (Math.random() - 0.5) * 0.2);
    p.scale.set(1, 0.7, 1);
    group.add(p);
  }

  group.position.copy(BOWL_POS);
  scene.add(group);
}

// Tunnel
const TUNNEL_POS = new THREE.Vector3(0.5, 0.35, 1.3);

function buildTunnel() {
  const group = new THREE.Group();

  const tunnelGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.8, 8, 1, false, 0, Math.PI);
  const tunnel = new THREE.Mesh(tunnelGeo, mat(0x98D1C8, { side: THREE.DoubleSide }));
  tunnel.rotation.z = Math.PI / 2;
  tunnel.position.y = 0.2;
  tunnel.castShadow = true;
  group.add(tunnel);

  // End caps
  const capGeo = new THREE.CircleGeometry(0.2, 8, 0, Math.PI);
  const capMat = mat(0x78B8A8, { side: THREE.DoubleSide });
  const cap1 = new THREE.Mesh(capGeo, capMat);
  cap1.rotation.y = Math.PI / 2;
  cap1.position.set(0.4, 0.2, 0);
  group.add(cap1);
  const cap2 = new THREE.Mesh(capGeo, capMat);
  cap2.rotation.y = -Math.PI / 2;
  cap2.position.set(-0.4, 0.2, 0);
  group.add(cap2);

  group.position.copy(TUNNEL_POS);
  scene.add(group);
}

// Small ball toy
const BALL_POS = new THREE.Vector3(-0.5, 0.4, -0.8);
let ball;

function buildBall() {
  const ballGeo = new THREE.IcosahedronGeometry(0.12, 0);
  ball = new THREE.Mesh(ballGeo, mat(0xFF69B4));
  ball.position.copy(BALL_POS);
  ball.castShadow = true;
  scene.add(ball);
}

// ─── HAMSTER FACTORY ───────────────────────────────────────────
function createHamster(bodyColor, bellyColor, cheekColor) {
  const group = new THREE.Group();

  // Body (main blob)
  const bodyGeo = new THREE.SphereGeometry(0.22, 6, 5);
  const body = new THREE.Mesh(bodyGeo, mat(bodyColor));
  body.scale.set(1, 0.85, 1.15);
  body.position.y = 0.22;
  body.castShadow = true;
  group.add(body);

  // Belly patch
  const bellyGeo = new THREE.SphereGeometry(0.15, 5, 4);
  const belly = new THREE.Mesh(bellyGeo, mat(bellyColor));
  belly.scale.set(0.9, 0.7, 1.0);
  belly.position.set(0, 0.18, 0.08);
  group.add(belly);

  // Head (slightly forward)
  const headGeo = new THREE.SphereGeometry(0.15, 6, 5);
  const head = new THREE.Mesh(headGeo, mat(bodyColor));
  head.position.set(0, 0.3, 0.18);
  head.castShadow = true;
  group.add(head);

  // Ears
  const earGeo = new THREE.SphereGeometry(0.06, 4, 3);
  const earMat = mat(cheekColor);
  const earL = new THREE.Mesh(earGeo, earMat);
  earL.position.set(-0.09, 0.42, 0.12);
  earL.scale.set(1, 1.2, 0.8);
  group.add(earL);
  const earR = new THREE.Mesh(earGeo, earMat);
  earR.position.set(0.09, 0.42, 0.12);
  earR.scale.set(1, 1.2, 0.8);
  group.add(earR);

  // Inner ears
  const innerEarGeo = new THREE.SphereGeometry(0.035, 4, 3);
  const innerEarMat = mat(0xFFB6C1);
  const ieL = new THREE.Mesh(innerEarGeo, innerEarMat);
  ieL.position.set(-0.09, 0.43, 0.14);
  group.add(ieL);
  const ieR = new THREE.Mesh(innerEarGeo, innerEarMat);
  ieR.position.set(0.09, 0.43, 0.14);
  group.add(ieR);

  // Eyes
  const eyeGeo = new THREE.SphereGeometry(0.03, 4, 3);
  const eyeMat = mat(0x222222);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.07, 0.33, 0.3);
  group.add(eyeL);
  const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
  eyeR.position.set(0.07, 0.33, 0.3);
  group.add(eyeR);

  // Eye highlights
  const hlGeo = new THREE.SphereGeometry(0.012, 3, 2);
  const hlMat = mat(0xFFFFFF);
  const hlL = new THREE.Mesh(hlGeo, hlMat);
  hlL.position.set(-0.06, 0.34, 0.32);
  group.add(hlL);
  const hlR = new THREE.Mesh(hlGeo, hlMat);
  hlR.position.set(0.08, 0.34, 0.32);
  group.add(hlR);

  // Nose
  const noseGeo = new THREE.SphereGeometry(0.025, 4, 3);
  const nose = new THREE.Mesh(noseGeo, mat(0xFF6B9D));
  nose.position.set(0, 0.28, 0.33);
  group.add(nose);

  // Cheeks (puffy!)
  const cheekGeo = new THREE.SphereGeometry(0.08, 5, 4);
  const cheekMat = mat(cheekColor);
  const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
  cheekL.position.set(-0.12, 0.24, 0.2);
  cheekL.scale.set(0.8, 0.9, 0.8);
  group.add(cheekL);
  const cheekR = new THREE.Mesh(cheekGeo, cheekMat);
  cheekR.position.set(0.12, 0.24, 0.2);
  cheekR.scale.set(0.8, 0.9, 0.8);
  group.add(cheekR);

  // Tiny feet
  const footGeo = new THREE.SphereGeometry(0.04, 4, 3);
  const footMat = mat(0xFFB6C1);
  const positions = [[-0.08, 0.04, 0.1], [0.08, 0.04, 0.1], [-0.08, 0.04, -0.1], [0.08, 0.04, -0.1]];
  positions.forEach(([x, y, z]) => {
    const f = new THREE.Mesh(footGeo, footMat);
    f.position.set(x, y, z);
    f.scale.set(1, 0.6, 1);
    group.add(f);
  });

  // Tiny tail
  const tailGeo = new THREE.SphereGeometry(0.03, 3, 2);
  const tail = new THREE.Mesh(tailGeo, mat(bodyColor));
  tail.position.set(0, 0.2, -0.25);
  group.add(tail);

  return group;
}

// ─── HAMSTER AI ────────────────────────────────────────────────
const BOUNDS = { x: 2.0, z: 1.6 };

class HamsterAI {
  constructor(mesh, name) {
    this.mesh = mesh;
    this.name = name;
    this.state = 'idle';
    this.timer = 0;
    this.target = new THREE.Vector3();
    this.speed = 0.6 + Math.random() * 0.4;
    this.idleTime = 0;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.wheelBoost = 0;

    // Start at random position
    this.mesh.position.set(
      (Math.random() - 0.5) * 3,
      0.35,
      (Math.random() - 0.5) * 2.5
    );
    this.setState('walk');
  }

  setState(state) {
    this.state = state;
    this.timer = 0;
    switch (state) {
      case 'walk':
        this.pickRandomTarget();
        break;
      case 'idle':
        this.idleTime = 0.5 + Math.random() * 2.0;
        break;
      case 'wheel':
        this.target.set(1.5, 0.35, -1.2);
        break;
      case 'eat':
        this.target.copy(BOWL_POS);
        break;
      case 'tunnel':
        this.target.copy(TUNNEL_POS);
        break;
    }
  }

  pickRandomTarget() {
    this.target.set(
      (Math.random() - 0.5) * BOUNDS.x * 2,
      0.35,
      (Math.random() - 0.5) * BOUNDS.z * 2
    );
  }

  update(dt) {
    this.bobPhase += dt * 8;
    const pos = this.mesh.position;

    // Bob animation (cute waddle)
    const bobAmount = this.state === 'walk' ? 0.03 : 0.01;
    this.mesh.position.y = 0.35 + Math.sin(this.bobPhase) * bobAmount;

    switch (this.state) {
      case 'walk': this.updateWalk(dt); break;
      case 'idle': this.updateIdle(dt); break;
      case 'wheel': this.updateWheel(dt); break;
      case 'eat': this.updateEat(dt); break;
      case 'tunnel': this.updateTunnel(dt); break;
    }

    // Clamp to bounds
    pos.x = THREE.MathUtils.clamp(pos.x, -BOUNDS.x, BOUNDS.x);
    pos.z = THREE.MathUtils.clamp(pos.z, -BOUNDS.z, BOUNDS.z);
  }

  updateWalk(dt) {
    const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position);
    dir.y = 0;
    const dist = dir.length();

    if (dist < 0.15) {
      this.setState('idle');
      return;
    }

    dir.normalize();
    this.mesh.position.addScaledVector(dir, this.speed * dt);

    // Rotate to face movement direction
    const angle = Math.atan2(dir.x, dir.z);
    this.mesh.rotation.y = THREE.MathUtils.lerp(
      this.mesh.rotation.y, angle, 5 * dt
    );

    // Random state change after a while
    this.timer += dt;
    if (this.timer > 2 + Math.random() * 3) {
      const r = Math.random();
      if (r < 0.15) this.setState('wheel');
      else if (r < 0.3) this.setState('eat');
      else if (r < 0.4) this.setState('tunnel');
      else this.setState('walk');
    }
  }

  updateIdle(dt) {
    this.timer += dt;
    if (this.timer > this.idleTime) {
      const r = Math.random();
      if (r < 0.2) this.setState('wheel');
      else if (r < 0.35) this.setState('eat');
      else this.setState('walk');
    }
    // Slight random rotation while idle
    this.mesh.rotation.y += Math.sin(this.bobPhase * 0.3) * 0.01;
  }

  updateWheel(dt) {
    const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position);
    dir.y = 0;
    const dist = dir.length();

    if (dist < 0.3) {
      // At the wheel - spin it!
      wheelSpeed = Math.max(wheelSpeed, 3 + Math.random() * 2);
      this.wheelBoost = 1;
      this.timer += dt;
      if (this.timer > 2 + Math.random() * 3) {
        this.wheelBoost = 0;
        this.setState('walk');
      }
    } else {
      dir.normalize();
      this.mesh.position.addScaledVector(dir, this.speed * 1.2 * dt);
      const angle = Math.atan2(dir.x, dir.z);
      this.mesh.rotation.y = THREE.MathUtils.lerp(this.mesh.rotation.y, angle, 5 * dt);
    }
  }

  updateEat(dt) {
    const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position);
    dir.y = 0;
    const dist = dir.length();

    if (dist < 0.3) {
      // Eating! Scurry in place
      this.mesh.rotation.y += Math.sin(this.bobPhase * 2) * 0.1;
      this.timer += dt;
      if (this.timer > 1.5 + Math.random() * 2) {
        this.setState('walk');
      }
    } else {
      dir.normalize();
      this.mesh.position.addScaledVector(dir, this.speed * 1.3 * dt);
      const angle = Math.atan2(dir.x, dir.z);
      this.mesh.rotation.y = THREE.MathUtils.lerp(this.mesh.rotation.y, angle, 5 * dt);
    }
  }

  updateTunnel(dt) {
    const dir = new THREE.Vector3().subVectors(this.target, this.mesh.position);
    dir.y = 0;
    const dist = dir.length();

    if (dist < 0.4) {
      // In tunnel - wiggle through
      this.mesh.position.z += Math.sin(this.bobPhase * 3) * 0.005;
      this.timer += dt;
      if (this.timer > 1 + Math.random()) {
        // Pop out the other side
        this.mesh.position.z = TUNNEL_POS.z - 0.5;
        this.setState('walk');
      }
    } else {
      dir.normalize();
      this.mesh.position.addScaledVector(dir, this.speed * 1.1 * dt);
      const angle = Math.atan2(dir.x, dir.z);
      this.mesh.rotation.y = THREE.MathUtils.lerp(this.mesh.rotation.y, angle, 5 * dt);
    }
  }
}

// ─── BUILD THE WORLD ───────────────────────────────────────────
buildCage();
buildWheel();
buildFoodBowl();
buildTunnel();
buildBall();

// Create hamsters with different colors
const hamsterConfigs = [
  { body: 0xFFA040, belly: 0xFFF0E0, cheek: 0xFF8030, name: 'Nugget' },
  { body: 0xF5F0E8, belly: 0xFFFFFF, cheek: 0xFFD0B0, name: 'Snowball' },
  { body: 0x8B6914, belly: 0xC4A050, cheek: 0xA07828, name: 'Cocoa' },
  { body: 0xF5DEB3, belly: 0xFFF8F0, cheek: 0xE8C880, name: 'Butter' },
];

const hamsters = [];
hamsterConfigs.forEach(cfg => {
  const mesh = createHamster(cfg.body, cfg.belly, cfg.cheek);
  scene.add(mesh);
  const ai = new HamsterAI(mesh, cfg.name);
  hamsters.push(ai);
});

// ─── ANIMATION LOOP ────────────────────────────────────────────
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  // Update hamsters
  hamsters.forEach(h => h.update(dt));

  // Wheel physics
  if (wheelSpeed > 0.01) {
    wheelSpin += wheelSpeed * dt;
    wheelSpeed *= (1 - 0.5 * dt); // friction
  }
  if (wheelGroup) {
    wheelGroup.children[1].rotation.z = wheelSpin; // rim
    for (let i = 2; i < 7; i++) {
      if (wheelGroup.children[i]) {
        wheelGroup.children[i].rotation.z = wheelSpin + (i - 2) * (Math.PI * 2 / 5);
      }
    }
  }

  // Ball bounce (subtle)
  if (ball) {
    ball.rotation.y += dt * 0.5;
    ball.position.y = BALL_POS.y + Math.abs(Math.sin(clock.elapsedTime * 2)) * 0.05;
  }

  controls.update();
  renderer.render(scene, camera);
}

animate();

// ─── RESIZE ────────────────────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## What You Get

| Feature | Details |
|---------|---------|
| **4 Hamsters** | Nugget (orange), Snowball (white), Cocoa (brown), Butter (cream) — each with puffy cheeks, tiny feet, pink noses, and glossy eyes |
| **Cage** | Wooden tray base, scattered wood-shaving bits, wire-bar walls with corner posts |
| **Wheel** | Red-rimmed with 5 spokes on a grey stand — spins up when a hamster approaches, decays with friction |
| **Food Bowl** | Teal bowl with colorful pellets; hamsters waddle over and scurry in place |
| **Tunnel** | Mint-green half-pipe; hamsters enter, wiggle, and pop out the far side |
| **Ball Toy** | Pink icosahedron that gently bobs and rotates |
| **AI States** | `walk → idle → wheel / eat / tunnel → walk` with randomized timing and speeds |
| **Camera** | OrbitControls with damping, polar-angle clamp, and zoom limits |

Just save as `index.html` and open in any modern browser — no build step needed.