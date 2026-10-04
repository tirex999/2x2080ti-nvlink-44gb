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
    position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
    color: #fff; text-align: center; pointer-events: none;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
  }
  #ui h1 { font-size: 28px; margin-bottom: 4px; letter-spacing: 1px; }
  #ui p { font-size: 14px; opacity: 0.7; }
  #stats {
    position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
    color: #fff; font-size: 13px; opacity: 0.6; pointer-events: none;
    text-shadow: 0 1px 4px rgba(0,0,0,0.5);
  }
</style>
</head>
<body>
<div id="ui">
  <h1>🐹 Low-Poly Hamster Playground</h1>
  <p>Drag to rotate · Scroll to zoom</p>
</div>
<div id="stats"></div>

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

// ─── Scene Setup ──────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2d1b4e);
scene.fog = new THREE.FogExp2(0x2d1b4e, 0.018);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 200);
camera.position.set(12, 10, 14);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1.5, 0);
controls.minDistance = 6;
controls.maxDistance = 30;
controls.maxPolarAngle = Math.PI / 2.1;

// ─── Lighting ─────────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0x8888cc, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffeedd, 1.4);
dirLight.position.set(8, 15, 5);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.near = 1;
dirLight.shadow.camera.far = 40;
dirLight.shadow.camera.left = -12;
dirLight.shadow.camera.right = 12;
dirLight.shadow.camera.top = 12;
dirLight.shadow.camera.bottom = -12;
scene.add(dirLight);

const fillLight = new THREE.DirectionalLight(0x6688ff, 0.4);
fillLight.position.set(-5, 8, -5);
scene.add(fillLight);

const pointLight = new THREE.PointLight(0xff9966, 0.5, 20);
pointLight.position.set(0, 6, 0);
scene.add(pointLight);

// ─── Materials ────────────────────────────────────────────
function mat(color) {
  return new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.8, metalness: 0.1 });
}

// ─── Floor / Tray ─────────────────────────────────────────
const trayGeo = new THREE.CylinderGeometry(7, 7.2, 0.5, 16);
const tray = new THREE.Mesh(trayGeo, mat(0xf4a261));
tray.position.y = -0.25;
tray.receiveShadow = true;
scene.add(tray);

const floorGeo = new THREE.CylinderGeometry(6.8, 6.8, 0.1, 16);
const floor = new THREE.Mesh(floorGeo, mat(0xfce4b8));
floor.position.y = 0.05;
floor.receiveShadow = true;
scene.add(floor);

// ─── Bedding (scattered wood shavings) ────────────────────
const beddingColors = [0xe8c170, 0xd4a853, 0xf0d58c, 0xc9963a, 0xf5e6b8];
for (let i = 0; i < 80; i++) {
  const angle = Math.random() * Math.PI * 2;
  const r = Math.random() * 6.2;
  const s = 0.08 + Math.random() * 0.15;
  const chunk = new THREE.Mesh(
    new THREE.BoxGeometry(s, s * 0.4, s * 1.5),
    mat(beddingColors[Math.floor(Math.random() * beddingColors.length)])
  );
  chunk.position.set(Math.cos(angle) * r, 0.15, Math.sin(angle) * r);
  chunk.rotation.y = Math.random() * Math.PI;
  chunk.rotation.z = (Math.random() - 0.5) * 0.3;
  chunk.castShadow = true;
  chunk.receiveShadow = true;
  scene.add(chunk);
}

// ─── Cage Bars ────────────────────────────────────────────
const cageGroup = new THREE.Group();
const barMat = mat(0x88aacc);
barMat.metalness = 0.6;
barMat.roughness = 0.3;

const barCount = 24;
for (let i = 0; i < barCount; i++) {
  const angle = (i / barCount) * Math.PI * 2;
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 5, 5), barMat);
  bar.position.set(Math.cos(angle) * 7, 2.5, Math.sin(angle) * 7);
  bar.castShadow = true;
  cageGroup.add(bar);
}

// Top ring
const topRing = new THREE.Mesh(new THREE.TorusGeometry(7, 0.08, 6, 24), barMat);
topRing.position.y = 5;
topRing.rotation.x = Math.PI / 2;
cageGroup.add(topRing);

// Bottom ring
const botRing = new THREE.Mesh(new THREE.TorusGeometry(7, 0.08, 6, 24), barMat);
botRing.position.y = 0.2;
botRing.rotation.x = Math.PI / 2;
cageGroup.add(botRing);

// Middle ring
const midRing = new THREE.Mesh(new THREE.TorusGeometry(7, 0.06, 6, 24), barMat);
midRing.position.y = 2.5;
midRing.rotation.x = Math.PI / 2;
cageGroup.add(midRing);

// Top lid (partial)
const lidGeo = new THREE.RingGeometry(1, 7, 16);
const lidMat = mat(0x88aacc);
lidMat.side = THREE.DoubleSide;
lidMat.transparent = true;
lidMat.opacity = 0.3;
const lid = new THREE.Mesh(lidGeo, lidMat);
lid.position.y = 5.05;
lid.rotation.x = -Math.PI / 2;
cageGroup.add(lid);

scene.add(cageGroup);

// ─── Hamster Wheel ────────────────────────────────────────
const wheelGroup = new THREE.Group();
const wheelMat = mat(0xff6b6b);
wheelMat.metalness = 0.3;

// Outer ring
const outerRing = new THREE.Mesh(new THREE.TorusGeometry(1.4, 0.12, 5, 12), wheelMat);
wheelGroup.add(outerRing);

// Inner ring
const innerRing = new THREE.Mesh(new THREE.TorusGeometry(1.0, 0.06, 5, 12), mat(0xff8e8e));
wheelGroup.add(innerRing);

// Spokes
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.3, 0.06), mat(0xffaaaa));
  spoke.position.set(Math.cos(angle) * 0.65, Math.sin(angle) * 0.65, 0);
  spoke.rotation.z = angle;
  wheelGroup.add(spoke);
}

// Axle
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.6, 6), mat(0xcccccc));
axle.rotation.x = Math.PI / 2;
wheelGroup.add(axle);

// Stand
const standMat = mat(0x6c5ce7);
const standL = new THREE.Mesh(new THREE.BoxGeometry(0.15, 2.2, 0.15), standMat);
standL.position.set(0, -1.1, 0.35);
wheelGroup.add(standL);
const standR = new THREE.Mesh(new THREE.BoxGeometry(0.15, 2.2, 0.15), standMat);
standR.position.set(0, -1.1, -0.35);
wheelGroup.add(standR);
const standBase = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.15, 1.0), standMat);
standBase.position.set(0, -2.2, 0);
wheelGroup.add(standBase);

wheelGroup.position.set(4.5, 3.6, 0);
wheelGroup.castShadow = true;
scene.add(wheelGroup);

// ─── Food Bowl ────────────────────────────────────────────
const bowlGroup = new THREE.Group();
const bowlGeo = new THREE.CylinderGeometry(0.7, 0.5, 0.4, 8);
const bowl = new THREE.Mesh(bowlGeo, mat(0x6bcb77));
bowl.position.y = 0.2;
bowlGroup.add(bowl);

// Food pellets
for (let i = 0; i < 6; i++) {
  const a = (i / 6) * Math.PI * 2;
  const pellet = new THREE.Mesh(new THREE.SphereGeometry(0.1, 4, 3), mat(0xd4a017));
  pellet.position.set(Math.cos(a) * 0.25, 0.45, Math.sin(a) * 0.25);
  bowlGroup.add(pellet);
}
bowlGroup.position.set(-3.5, 0.1, 2);
scene.add(bowlGroup);

// ─── Tunnel ───────────────────────────────────────────────
const tunnelGroup = new THREE.Group();
const tunnelGeo = new THREE.CylinderGeometry(0.6, 0.6, 2.5, 8, 1, true);
const tunnelMat = mat(0x4ecdc4);
tunnelMat.side = THREE.DoubleSide;
const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
tunnel.rotation.z = Math.PI / 2;
tunnel.position.y = 0.6;
tunnelGroup.add(tunnel);

// Tunnel rings for detail
for (let i = -1; i <= 1; i++) {
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.05, 5, 8), mat(0x45b7aa));
  ring.position.set(i * 0.9, 0.6, 0);
  ring.rotation.y = Math.PI / 2;
  tunnelGroup.add(ring);
}
tunnelGroup.position.set(-2, 0.1, -3.5);
tunnelGroup.rotation.y = 0.5;
scene.add(tunnelGroup);

// ─── Water Bottle ─────────────────────────────────────────
const bottleGroup = new THREE.Group();
const bottleBody = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 1.2, 6), mat(0x74b9ff));
bottleBody.position.y = 1.5;
bottleGroup.add(bottleBody);
const bottleCap = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, 0.3, 6), mat(0xcccccc));
bottleCap.position.y = 0.75;
bottleGroup.add(bottleCap);
const spout = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.4, 4), mat(0xaaaaaa));
spout.position.set(0, 0.55, 0);
spout.rotation.x = Math.PI / 2;
spout.position.z = 0.15;
bottleGroup.add(spout);
bottleGroup.position.set(6.2, 1.5, 3);
scene.add(bottleGroup);

// ─── Hamster Factory ──────────────────────────────────────
const hamsterColors = [
  { body: 0xf5c77e, belly: 0xfff3d4, ear: 0xffb3ba },
  { body: 0xd4a373, belly: 0xfefae0, ear: 0xffa8a8 },
  { body: 0xf2e8cf, belly: 0xffffff, ear: 0xffc9d6 },
  { body: 0xc9b1ff, belly: 0xf0e6ff, ear: 0xffb3d9 },
  { body: 0x87ceeb, belly: 0xe0f7fa, ear: 0xffb6c1 },
];

function createHamster(colorScheme) {
  const group = new THREE.Group();
  const bodyMat = mat(colorScheme.body);
  const bellyMat = mat(colorScheme.belly);
  const earMat = mat(colorScheme.ear);
  const eyeMat = mat(0x1a1a1a);
  const noseMat = mat(0xff69b4);

  // Body (chubby sphere)
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.45, 6, 5), bodyMat);
  body.scale.set(1, 0.85, 1.2);
  body.position.y = 0.4;
  body.castShadow = true;
  group.add(body);

  // Belly
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.35, 6, 4), bellyMat);
  belly.scale.set(0.9, 0.8, 1.0);
  belly.position.set(0, 0.3, 0.12);
  group.add(belly);

  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.32, 6, 5), bodyMat);
  head.position.set(0, 0.65, 0.35);
  head.castShadow = true;
  group.add(head);

  // Cheeks (puffy!)
  const cheekL = new THREE.Mesh(new THREE.SphereGeometry(0.14, 5, 4), bellyMat);
  cheekL.position.set(-0.22, 0.55, 0.5);
  group.add(cheekL);
  const cheekR = new THREE.Mesh(new THREE.SphereGeometry(0.14, 5, 4), bellyMat);
  cheekR.position.set(0.22, 0.55, 0.5);
  group.add(cheekR);

  // Ears
  const earL = new THREE.Mesh(new THREE.SphereGeometry(0.1, 5, 4), earMat);
  earL.position.set(-0.2, 0.9, 0.25);
  earL.scale.set(1, 1.3, 0.6);
  group.add(earL);
  const earR = new THREE.Mesh(new THREE.SphereGeometry(0.1, 5, 4), earMat);
  earR.position.set(0.2, 0.9, 0.25);
  earR.scale.set(1, 1.3, 0.6);
  group.add(earR);

  // Eyes (big and cute)
  const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.07, 5, 4), eyeMat);
  eyeL.position.set(-0.12, 0.72, 0.58);
  group.add(eyeL);
  const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.07, 5, 4), eyeMat);
  eyeR.position.set(0.12, 0.72, 0.58);
  group.add(eyeR);

  // Eye highlights
  const hlMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const hlL = new THREE.Mesh(new THREE.SphereGeometry(0.025, 4, 3), hlMat);
  hlL.position.set(-0.1, 0.75, 0.63);
  group.add(hlL);
  const hlR = new THREE.Mesh(new THREE.SphereGeometry(0.025, 4, 3), hlMat);
  hlR.position.set(0.14, 0.75, 0.63);
  group.add(hlR);

  // Nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.04, 4, 3), noseMat);
  nose.position.set(0, 0.62, 0.65);
  group.add(nose);

  // Legs (stubby!)
  const legGeo = new THREE.CylinderGeometry(0.06, 0.07, 0.2, 4);
  const legMat = mat(colorScheme.body);
  const legPositions = [
    [-0.25, 0.1, 0.2], [0.25, 0.1, 0.2],
    [-0.25, 0.1, -0.2], [0.25, 0.1, -0.2]
  ];
  const legs = [];
  legPositions.forEach(pos => {
    const leg = new THREE.Mesh(legGeo, legMat);
    leg.position.set(...pos);
    leg.castShadow = true;
    group.add(leg);
    legs.push(leg);
  });

  // Tail (tiny nub)
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.06, 4, 3), earMat);
  tail.position.set(0, 0.35, -0.5);
  group.add(tail);

  group.userData = { legs, head, nose, body };
  return group;
}

// ─── Hamster Behavior System ──────────────────────────────
const STATES = { WALKING: 0, PAUSING: 1, TURNING: 2, WHEEL: 3, EATING: 4, TUNNEL: 5 };
const hamsters = [];

function createHamsterAgent(colorIdx) {
  const mesh = createHamster(hamsterColors[colorIdx]);
  const angle = Math.random() * Math.PI * 2;
  const r = 1.5 + Math.random() * 3.5;
  mesh.position.set(Math.cos(angle) * r, 0, Math.sin(angle) * r);
  mesh.rotation.y = Math.random() * Math.PI * 2;
  scene.add(mesh);

  const agent = {
    mesh,
    state: STATES.WALKING,
    stateTimer: 1 + Math.random() * 2,
    speed: 0.8 + Math.random() * 0.6,
    turnSpeed: 1.5 + Math.random() * 1.5,
    targetAngle: mesh.rotation.y,
    wheelSpin: 0,
    bobPhase: Math.random() * Math.PI * 2,
    noseWiggle: 0,
    stateCounts: { walking: 0, pausing: 0, wheel: 0, eating: 0 }
  };
  hamsters.push(agent);
  return agent;
}

// Create hamsters
for (let i = 0; i < 5; i++) {
  createHamsterAgent(i);
}

const wheelPos = new THREE.Vector3(4.5, 0, 0);
const bowlPos = new THREE.Vector3(-3.5, 0, 2);
const tunnelPos = new THREE.Vector3(-2, 0, -3.5);

function setState(agent, newState) {
  agent.state = newState;
  agent.stateTimer = 1.5 + Math.random() * 3;
}

function updateHamster(agent, dt, time) {
  const mesh = agent.mesh;
  const pos = mesh.position;
  const legs = mesh.userData.legs;
  const nose = mesh.userData.nose;

  agent.bobPhase += dt * 8;
  agent.noseWiggle = Math.sin(time * 12 + agent.bobPhase) * 0.02;
  nose.position.y = 0.62 + agent.noseWiggle;

  // Leg animation
  const legSpeed = agent.state === STATES.WALKING ? 8 : (agent.state === STATES.WHEEL ? 10 : 0);
  legs.forEach((leg, i) => {
    const phase = agent.bobPhase + (i % 2 === 0 ? 0 : Math.PI) + (i < 2 ? 0 : Math.PI * 0.5);
    leg.rotation.x = Math.sin(phase) * (legSpeed > 0 ? 0.4 : 0);
  });

  agent.stateTimer -= dt;

  switch (agent.state) {
    case STATES.WALKING: {
      agent.stateCounts.walking++;
      mesh.position.x += Math.sin(mesh.rotation.y) * agent.speed * dt;
      mesh.position.z += Math.cos(mesh.rotation.y) * agent.speed * dt;

      // Body bob
      mesh.position.y = Math.abs(Math.sin(agent.bobPhase)) * 0.04;

      // Keep in cage bounds
      const dist = Math.sqrt(pos.x * pos.x + pos.z * pos.z);
      if (dist > 5.8) {
        agent.targetAngle = Math.atan2(-pos.x, -pos.z);
        setState(agent, STATES.TURNING);
      }

      // Random direction change
      if (Math.random() < dt * 0.3) {
        agent.targetAngle = mesh.rotation.y + (Math.random() - 0.5) * Math.PI;
        setState(agent, STATES.TURNING);
      }

      // Random state transitions
      if (agent.stateTimer <= 0) {
        const roll = Math.random();
        if (roll < 0.35) setState(agent, STATES.PAUSING);
        else if (roll < 0.55) setState(agent, STATES.WHEEL);
        else if (roll < 0.7) setState(agent, STATES.EATING);
        else if (roll < 0.8) setState(agent, STATES.TUNNEL);
        else agent.stateTimer = 1 + Math.random() * 2; // keep walking
      }
      break;
    }

    case STATES.PAUSING: {
      agent.stateCounts.pausing++;
      mesh.position.y = 0;
      // Idle wiggle
      mesh.rotation.y += Math.sin(time * 2 + agent.bobPhase) * 0.005;
      if (agent.stateTimer <= 0) {
        agent.targetAngle = Math.random() * Math.PI * 2;
        setState(agent, STATES.TURNING);
      }
      break;
    }

    case STATES.TURNING: {
      let diff = agent.targetAngle - mesh.rotation.y;
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      mesh.rotation.y += diff * agent.turnSpeed * dt;

      if (Math.abs(diff) < 0.1 || agent.stateTimer <= 0) {
        setState(agent, STATES.WALKING);
      }
      break;
    }

    case STATES.WHEEL: {
      agent.stateCounts.wheel++;
      // Move toward wheel
      const toWheel = new THREE.Vector3().subVectors(wheelPos, pos);
      toWheel.y = 0;
      const distToWheel = toWheel.length();

      if (distToWheel > 1.5) {
        agent.targetAngle = Math.atan2(toWheel.x, toWheel.z);
        let diff = agent.targetAngle - mesh.rotation.y;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        mesh.rotation.y += diff * 3 * dt;
        mesh.position.x += Math.sin(mesh.rotation.y) * agent.speed * 1.3 * dt;
        mesh.position.z += Math.cos(mesh.rotation.y) * agent.speed * 1.3 * dt;
        mesh.position.y = Math.abs(Math.sin(agent.bobPhase)) * 0.05;
      } else {
        // On wheel! Spin it!
        agent.wheelSpin += dt * 6;
        mesh.position.y = Math.abs(Math.sin(agent.bobPhase * 2)) * 0.08;
        mesh.rotation.y = Math.atan2(wheelPos.x - pos.x, wheelPos.z - pos.z);
        // Hamster sits on wheel
        mesh.position.y = 2.8 + Math.sin(agent.bobPhase) * 0.1;
        const wAngle = agent.wheelSpin;
        mesh.position.x = wheelPos.x + Math.sin(wAngle) * 0;
        mesh.position.z = wheelPos.z + Math.cos(wAngle) * 0;
      }

      if (agent.stateTimer <= 0) {
        setState(agent, STATES.PAUSING);
        agent.wheelSpin = 0;
      }
      break;
    }

    case STATES.EATING: {
      agent.stateCounts.eating++;
      const toBowl = new THREE.Vector3().subVectors(bowlPos, pos);
      toBowl.y = 0;
      const distToBowl = toBowl.length();

      if (distToBowl > 1.0) {
        agent.targetAngle = Math.atan2(toBowl.x, toBowl.z);
        let diff = agent.targetAngle - mesh.rotation.y;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        mesh.rotation.y += diff * 3 * dt;
        mesh.position.x += Math.sin(mesh.rotation.y) * agent.speed * 1.2 * dt;
        mesh.position.z += Math.cos(mesh.rotation.y) * agent.speed * 1.2 * dt;
        mesh.position.y = Math.abs(Math.sin(agent.bobPhase)) * 0.04;
      } else {
        // Eating animation - head bobbing
        mesh.userData.head.position.y = 0.65 + Math.sin(time * 6) * 0.05;
        mesh.position.y = 0;
      }

      if (agent.stateTimer <= 0) {
        mesh.userData.head.position.y = 0.65;
        setState(agent, STATES.PAUSING);
      }
      break;
    }

    case STATES.TUNNEL: {
      const toTunnel = new THREE.Vector3().subVectors(tunnelPos, pos);
      toTunnel.y = 0;
      const distToTunnel = toTunnel.length();

      if (distToTunnel > 1.2) {
        agent.targetAngle = Math.atan2(toTunnel.x, toTunnel.z);
        let diff = agent.targetAngle - mesh.rotation.y;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        mesh.rotation.y += diff * 3 * dt;
        mesh.position.x += Math.sin(mesh.rotation.y) * agent.speed * 1.2 * dt;
        mesh.position.z += Math.cos(mesh.rotation.y) * agent.speed * 1.2 * dt;
        mesh.position.y = Math.abs(Math.sin(agent.bobPhase)) * 0.04;
      } else {
        // Inside tunnel - shrink and hide
        const s = 0.5 + Math.sin(time * 3) * 0.1;
        mesh.scale.setScalar(s);
        mesh.position.y = 0.1;
      }

      if (agent.stateTimer <= 0) {
        mesh.scale.setScalar(1);
        setState(agent, STATES.WALKING);
      }
      break;
    }
  }

  // Clamp to cage
  const d = Math.sqrt(pos.x * pos.x + pos.z * pos.z);
  if (d > 6.0) {
    pos.x *= 6.0 / d;
    pos.z *= 6.0 / d;
  }
}

// ─── Wheel Animation ──────────────────────────────────────
let wheelRotation = 0;
function updateWheel(dt) {
  // Check if any hamster is on the wheel
  let anyOnWheel = false;
  hamsters.forEach(h => {
    if (h.state === STATES.WHEEL) {
      const dist = h.mesh.position.distanceTo(new THREE.Vector3(wheelPos.x, h.mesh.position.y, wheelPos.z));
      if (dist < 2 && h.mesh.position.y > 1.5) {
        anyOnWheel = true;
        wheelRotation += dt * 6;
      }
    }
  });
  wheelGroup.rotation.z = wheelRotation;
}

// ─── Decorative Elements ──────────────────────────────────
// Small house/hideout
const houseGroup = new THREE.Group();
const houseBody = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.2, 1.5), mat(0xe17055));
houseBody.position.y = 0.6;
houseBody.castShadow = true;
houseGroup.add(houseBody);

// Roof
const roofGeo = new THREE.ConeGeometry(1.2, 0.8, 4);
const roof = new THREE.Mesh(roofGeo, mat(0xd63031));
roof.position.y = 1.6;
roof.rotation.y = Math.PI / 4;
roof.castShadow = true;
houseGroup.add(roof);

// Door
const door = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.7), mat(0x2d3436));
door.position.set(0, 0.35, 0.76);
houseGroup.add(door);

houseGroup.position.set(2, 0.1, -4);
houseGroup.rotation.y = 0.3;
scene.add(houseGroup);

// Small ramp to wheel
const rampGeo = new THREE.BoxGeometry(1.5, 0.1, 2.5);
const ramp = new THREE.Mesh(rampGeo, mat(0xfdcb6e));
ramp.position.set(3.8, 1.2, 0);
ramp.rotation.z = -0.4;
ramp.castShadow = true;
scene.add(ramp);

// ─── Particles (floating dust) ────────────────────────────
const particleCount = 50;
const particleGeo = new THREE.BufferGeometry();
const particlePositions = new Float32Array(particleCount * 3);
for (let i = 0; i < particleCount; i++) {
  particlePositions[i * 3] = (Math.random() - 0.5) * 14;
  particlePositions[i * 3 + 1] = Math.random() * 6 + 0.5;
  particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 14;
}
particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
const particleMat = new THREE.PointsMaterial({ color: 0xffeedd, size: 0.05, transparent: true, opacity: 0.5 });
const particles = new THREE.Points(particleGeo, particleMat);
scene.add(particles);

// ─── Animation Loop ───────────────────────────────────────
const clock = new THREE.Clock();
const statsEl = document.getElementById('stats');
let frameCount = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  // Update hamsters
  hamsters.forEach(agent => updateHamster(agent, dt, time));

  // Update wheel
  updateWheel(dt);

  // Animate particles
  const positions = particles.geometry.attributes.position.array;
  for (let i = 0; i < particleCount; i++) {
    positions[i * 3 + 1] += Math.sin(time + i) * 0.002;
    if (positions[i * 3 + 1] > 7) positions[i * 3 + 1] = 0.5;
  }
  particles.geometry.attributes.position.needsUpdate = true;

  // Subtle light animation
  pointLight.intensity = 0.5 + Math.sin(time * 0.5) * 0.1;

  // Stats
  frameCount++;
  if (frameCount % 30 === 0) {
    const stateNames = ['Walking', 'Pausing', 'Turning', 'On Wheel', 'Eating', 'In Tunnel'];
    const counts = {};
    hamsters.forEach(h => {
      const name = stateNames[h.state];
      counts[name] = (counts[name] || 0) + 1;
    });
    statsEl.textContent = Object.entries(counts).map(([k, v]) => `${k}: ${v}`).join('  ·  ');
  }

  controls.update();
  renderer.render(scene, camera);
}

animate();

// ─── Resize Handler ───────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## What's Included

**Scene Elements:**
- 🐹 **5 colorful low-poly hamsters** — each with unique color schemes (golden, brown, cream, lavender, blue) featuring chubby bodies, puffy cheeks, big shiny eyes, tiny ears, and stubby legs
- 🎡 **Hamster wheel** — spins when a hamster climbs on it, complete with a stand and ramp
- 🏠 **Little house** with a roof and door for the cage
- 🥣 **Food bowl** with pellets that attracts hamsters
- 🟢 **Tunnel** hamsters can crawl into (they shrink!)
- 💧 **Water bottle** on the cage wall
- 🪵 **Scattered bedding** (wood shavings) on the floor
- ✨ **Floating dust particles** for atmosphere

**Behavior System (State Machine):**
| State | Behavior |
|-------|----------|
| Walking | Moves forward with body bob & leg animation |
| Pausing | Stands still with idle wiggle |
| Turning | Smoothly rotates to new heading |
| Wheel | Walks to wheel → climbs on → wheel spins |
| Eating | Walks to bowl → head bobs (eating) |
| Tunnel | Walks to tunnel → shrinks (hides inside) |

**Controls:** Drag to orbit, scroll to zoom. The stats bar at the bottom shows real-time hamster activity!