# 🐠 3D Аквариум с Реалистичными Рыбками

Вот полная реализация интерактивного 3D аквариума:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #0a1a3a; }
    #canvas-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; }

    .panel {
        position: fixed;
        background: rgba(10, 30, 70, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 180, 255, 0.25);
        border-radius: 16px;
        padding: 18px;
        color: #e0f0ff;
        box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5), inset 0 1px 0 rgba(255,255,255,0.1);
        z-index: 10;
    }
    #info-panel { top: 20px; left: 20px; max-width: 280px; }
    #stats-panel { top: 20px; right: 20px; min-width: 160px; text-align: center; }

    h1 {
        font-size: 22px;
        background: linear-gradient(90deg, #4dd0ff, #a78bfa, #ff8ac2);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .instructions { font-size: 12.5px; line-height: 1.7; opacity: 0.85; margin-bottom: 14px; }
    .instructions b { color: #7dd3fc; }

    .btn {
        display: block;
        width: 100%;
        margin: 8px 0;
        padding: 10px 14px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 13.5px;
        font-weight: 600;
        color: white;
        background: linear-gradient(135deg, #0ea5e9, #2563eb);
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35);
        transition: all 0.25s ease;
    }
    .btn:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6), 0 0 12px rgba(56, 189, 248, 0.4);
    }
    .btn:active { transform: translateY(0) scale(0.98); }
    .btn.purple { background: linear-gradient(135deg, #8b5cf6, #d946ef); box-shadow: 0 4px 14px rgba(139, 92, 246, 0.35); }
    .btn.purple:hover { box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6); }
    .btn.amber { background: linear-gradient(135deg, #f59e0b, #ef4444); box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35); }
    .btn.amber:hover { box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6); }

    .stat { margin: 8px 0; font-size: 13px; }
    .stat-value {
        display: block;
        font-size: 26px;
        font-weight: 700;
        color: #7dd3fc;
        text-shadow: 0 0 12px rgba(125, 211, 252, 0.5);
    }
    #fps-value { color: #86efac; text-shadow: 0 0 12px rgba(134, 239, 172, 0.5); }

    #feed-hint {
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(10, 30, 70, 0.55);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(100, 180, 255, 0.25);
        border-radius: 30px;
        padding: 10px 26px;
        color: #bae6fd;
        font-size: 14px;
        z-index: 10;
        animation: pulse 2.5s infinite;
        pointer-events: none;
    }
    @keyframes pulse {
        0%, 100% { opacity: 0.75; box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }
        50% { opacity: 1; box-shadow: 0 0 24px rgba(56, 189, 248, 0.5); }
    }
    @media (max-width: 640px) {
        #info-panel { max-width: 200px; padding: 12px; }
        h1 { font-size: 16px; }
        .instructions { display: none; }
    }
</style>
</head>
<body>
<div id="canvas-container"></div>

<div class="panel" id="info-panel">
    <h1>🐠 3D Аквариум</h1>
    <div class="instructions">
        <b>ЛКМ + движение</b> — вращение камеры<br>
        <b>ПКМ + движение</b> — панорамирование<br>
        <b>Колесо мыши</b> — приближение / отдаление<br>
        <b>Клик по аквариуму</b> — бросить корм 🍤
    </div>
    <button class="btn" id="btn-fish">🐟 Добавить рыбку</button>
    <button class="btn purple" id="btn-bubbles">💭 Больше пузырей</button>
    <button class="btn amber" id="btn-light">💡 Свет: ВКЛ</button>
</div>

<div class="panel" id="stats-panel">
    <div class="stat">Рыбки<span class="stat-value" id="fish-count">15</span></div>
    <div class="stat">FPS<span class="stat-value" id="fps-value">60</span></div>
</div>

<div id="feed-hint">🍤 Кликайте по аквариуму, чтобы покормить рыбок!</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// БАЗОВАЯ СЦЕНА
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a2a5a, 0.012);

// Градиентный фон через canvas
(function makeBackground() {
    const c = document.createElement('canvas');
    c.width = 2; c.height = 512;
    const ctx = c.getContext('2d');
    const g = ctx.createLinearGradient(0, 0, 0, 512);
    g.addColorStop(0, '#1e4a8a');
    g.addColorStop(0.5, '#0e2f66');
    g.addColorStop(1, '#051530');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 2, 512);
    const tex = new THREE.CanvasTexture(c);
    scene.background = tex;
})();

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 200);
camera.position.set(28, 14, 30);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById('canvas-container').appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// ============================================================
// ОСВЕЩЕНИЕ
// ============================================================
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sunLight = new THREE.DirectionalLight(0xffffff, 1.0);
sunLight.position.set(20, 35, 15);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -30;
sunLight.shadow.camera.right = 30;
sunLight.shadow.camera.top = 30;
sunLight.shadow.camera.bottom = -30;
sunLight.shadow.camera.far = 100;
scene.add(sunLight);

const blueLight1 = new THREE.PointLight(0x4488ff, 0.8, 50);
blueLight1.position.set(-12, 10, 0);
scene.add(blueLight1);

const blueLight2 = new THREE.PointLight(0x2266cc, 0.6, 50);
blueLight2.position.set(12, -6, 5);
scene.add(blueLight2);

// ============================================================
// АКВАРИУМ (СТЕКЛО)
// ============================================================
const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xaaddff,
    transparent: true,
    opacity: 0.12,
    transmission: 0.95,
    roughness: 0.05,
    metalness: 0,
    side: THREE.DoubleSide,
    depthWrite: false
});
const glass = new THREE.Mesh(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d), glassMat);
scene.add(glass);

const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(glass.geometry),
    new THREE.LineBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.6 })
);
scene.add(edges);

// ============================================================
// ПЕСЧАНОЕ ДНО (с procedural неровностями)
// ============================================================
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
sandGeo.rotateX(-Math.PI / 2);
const pos = sandGeo.attributes.position;
for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    if (Math.abs(x) < TANK.w / 2 - 0.3 && Math.abs(z) < TANK.d / 2 - 0.3) {
        pos.setY(i, Math.sin(x * 0.7) * Math.cos(z * 0.9) * 0.35 + Math.random() * 0.15);
    }
}
sandGeo.computeVertexNormals();
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({ color: 0xd9b98a, roughness: 1 }));
sand.position.y = -TANK.h / 2 + 0.2;
sand.receiveShadow = true;
scene.add(sand);

// ============================================================
// КАМНИ
// ============================================================
for (let i = 0; i < 8; i++) {
    const geo = new THREE.DodecahedronGeometry(0.8 + Math.random() * 1.4, 0);
    const p = geo.attributes.position;
    for (let j = 0; j < p.count; j++) {
        p.setXYZ(j,
            p.getX(j) * (0.7 + Math.random() * 0.6),
            p.getY(j) * (0.6 + Math.random() * 0.5),
            p.getZ(j) * (0.7 + Math.random() * 0.6));
    }
    geo.computeVertexNormals();
    const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.08, 0.1, 0.25 + Math.random() * 0.2), roughness: 0.95
    }));
    rock.position.set(
        (Math.random() - 0.5) * (TANK.w - 6),
        -TANK.h / 2 + 0.7,
        (Math.random() - 0.5) * (TANK.d - 5)
    );
    rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    rock.castShadow = true;
    rock.receiveShadow = true;
    scene.add(rock);
}

// ============================================================
// ВОДОРОСЛИ
// ============================================================
const seaweeds = [];
for (let i = 0; i < 12; i++) {
    const height = 3 + Math.random() * 6;
    const baseX = (Math.random() - 0.5) * (TANK.w - 4);
    const baseZ = (Math.random() - 0.5) * (TANK.d - 4);
    const pts = [];
    for (let j = 0; j <= 6; j++) {
        pts.push(new THREE.Vector3(
            Math.sin(j * 0.8) * 0.4,
            (height / 6) * j,
            Math.cos(j * 0.6) * 0.3
        ));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    const geo = new THREE.TubeGeometry(curve, 12, 0.18, 6, false);
    const mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.28 + Math.random() * 0.14, 0.7, 0.3 + Math.random() * 0.15),
        roughness: 0.8
    });
    const stem = new THREE.Mesh(geo, mat);
    stem.position.set(baseX, -TANK.h / 2 + 0.3, baseZ);
    stem.castShadow = true;
    stem.userData.phase = Math.random() * Math.PI * 2;
    stem.userData.speed = 0.5 + Math.random() * 0.8;
    scene.add(stem);
    seaweeds.push(stem);
}

// ============================================================
// ПУЗЫРИ
// ============================================================
const bubbles = [];
const bubbleGeo = new THREE.SphereGeometry(0.2, 10, 10);
const bubbleMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, transparent: true, opacity: 0.35,
    transmission: 0.9, roughness: 0.1, metalness: 0.1
});
function spawnBubble() {
    const b = new THREE.Mesh(bubbleGeo, bubbleMat);
    const s = 0.5 + Math.random() * 1.2;
    b.scale.setScalar(s);
    b.position.set(
        (Math.random() - 0.5) * (TANK.w - 4),
        -TANK.h / 2 + Math.random() * TANK.h,
        (Math.random() - 0.5) * (TANK.d - 4)
    );
    b.userData = { speed: 1.5 + Math.random() * 2.5, phase: Math.random() * Math.PI * 2, amp: 0.3 + Math.random() * 0.6 };
    scene.add(b);
    bubbles.push(b);
}
for (let i = 0; i < 30; i++) spawnBubble();

// ============================================================
// РЫБКИ
// ============================================================
const fishArray = [];
const COLOR_SCHEMES = [
    { body: 0xff7a1a, fin: 0xffb066 }, // оранжевая
    { body: 0x2266ff, fin: 0x88bbff }, // синяя
    { body: 0xffdd00, fin: 0xff4422 }, // желто-красная
    { body: 0x9944ff, fin: 0xcc99ff }, // фиолетовая
    { body: 0xee2233, fin: 0xff8899 }, // красная
    { body: 0x22bb55, fin: 0x88eeaa }, // зеленая
    { body: 0xff66bb, fin: 0xffbbee }, // розовая
    { body: 0xddaa22, fin: 0xffee88 }, // золотая
];

function createFish() {
    const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
    const group = new THREE.Group();
    const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.25 });
    const finMat = new THREE.MeshStandardMaterial({
        color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide
    });

    // Тело
    const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
    body.scale.set(1.6, 0.85, 0.6);
    body.castShadow = true;
    group.add(body);

    // Глаза
    const eyeGeo = new THREE.SphereGeometry(0.2, 8, 8);
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
    const pupilGeo = new THREE.SphereGeometry(0.1, 6, 6);
    const pupilMat = new THREE.MeshStandardMaterial({ color: 0x000000, roughness: 0.1 });
    [1, -1].forEach(side => {
        const eye = new THREE.Mesh(eyeGeo, eyeMat);
        eye.position.set(1.15, 0.22, 0.42 * side);
        group.add(eye);
        const pupil = new THREE.Mesh(pupilGeo, pupilMat);
        pupil.position.set(1.3, 0.22, 0.46 * side);
        group.add(pupil);
    });

    // Хвост (пивот для вращения вокруг Z у заднего края)
    const tailPivot = new THREE.Group();
    tailPivot.position.set(-1.5, 0, 0);
    const tailShape = new THREE.Shape();
    tailShape.moveTo(0, 0);
    tailShape.quadraticCurveTo(-0.6, 0.6, -1.0, 0.75);
    tailShape.quadraticCurveTo(-0.55, 0, -1.0, -0.75);
    tailShape.quadraticCurveTo(-0.6, -0.6, 0, 0);
    const tail = new THREE.Mesh(new THREE.ShapeGeometry(tailShape), finMat);
    tailPivot.add(tail);
    group.add(tailPivot);

    // Верхний плавник
    const topFinShape = new THREE.Shape();
    topFinShape.moveTo(-0.6, 0);
    topFinShape.quadraticCurveTo(0.1, 0.9, 0.7, 0.15);
    topFinShape.lineTo(-0.6, 0);
    const topFin = new THREE.Mesh(new THREE.ShapeGeometry(topFinShape), finMat);
    topFin.rotation.y = Math.PI / 2;
    topFin.position.set(0.1, 0.7, 0);
    group.add(topFin);

    // Боковые плавники
    const sideFinGeo = new THREE.ConeGeometry(0.25, 0.8, 6);
    const fins = [];
    [1, -1].forEach(side => {
        const fin = new THREE.Mesh(sideFinGeo, finMat);
        fin.position.set(0.3, -0.15, 0.55 * side);
        fin.rotation.x = Math.PI / 2 * side + (side > 0 ? 0 : Math.PI);
        fin.rotation.z = -0.5;
        fin.scale.set(1, 1, 0.35);
        group.add(fin);
        fins.push(fin);
    });

    const scale = 0.6 + Math.random() * 0.6;
    group.scale.setScalar(scale);
    group.position.set(
        (Math.random() - 0.5) * (TANK.w - 8),
        (Math.random() - 0.5) * (TANK.h - 8),
        (Math.random() - 0.5) * (TANK.d - 6)
    );

    scene.add(group);
    fishArray.push({
        mesh: group,
        tail: tailPivot,
        leftFin: fins[0],
        rightFin: fins[1],
        velocity: new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5).normalize(),
        speed: 1.5 + Math.random() * 2.5,
        tailSpeed: 4 + Math.random() * 5,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5,
        wanderTimer: Math.random() * 3,
        scale: scale
    });
    updateFishCount();
}

function updateFishCount() {
    document.getElementById('fish-count').textContent = fishArray.length;
}
for (let i = 0; i < 15; i++) createFish();

// ============================================================
// КОРМ
// ============================================================
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.25, 6, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xcc6633, roughness: 0.9 });

const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let mouseDownPos = null;

renderer.domElement.addEventListener('mousedown', e => {
    mouseDownPos = { x: e.clientX, y: e.clientY };
});
renderer.domElement.addEventListener('mouseup', e => {
    if (!mouseDownPos) return;
    const dx = e.clientX - mouseDownPos.x, dy = e.clientY - mouseDownPos.y;
    mouseDownPos = null;
    if (dx * dx + dy * dy > 25) return; // это было вращение камеры
    if (e.button !== 0) return;

    mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    raycaster.setFromCamera(mouseNDC, camera);

    // Плоскость z=0 через центр аквариума (перпендикулярна камере у центра)
    const plane = new THREE.Plane();
    const camDir = new THREE.Vector3();
    camera.getWorldDirection(camDir);
    plane.setFromNormalAndCoplanarPoint(camDir.negate(), new THREE.Vector3(0, 0, 0));
    const hit = new THREE.Vector3();
    if (!raycaster.ray.intersectPlane(plane, hit)) return;

    // Ограничение границами аквариума
    hit.x = THREE.MathUtils.clamp(hit.x, -TANK.w / 2 + 1, TANK.w / 2 - 1);
    hit.y = THREE.MathUtils.clamp(hit.y, -TANK.h / 2 + 3, TANK.h / 2 - 1);
    hit.z = THREE.MathUtils.clamp(hit.z, -TANK.d / 2 + 1, TANK.d / 2 - 1);

    for (let i = 0; i < 3; i++) {
        const f = new THREE.Mesh(foodGeo, foodMat);
        f.position.copy(hit).add(new THREE.Vector3(
            (Math.random() - 0.5) * 1.2,
            Math.random() * 0.8,
            (Math.random() - 0.5) * 1.2
        ));
        f.userData.velocity = new THREE.Vector3((Math.random() - 0.5) * 1.5, 1.5 + Math.random(), (Math.random() - 0.5) * 1.5);
        f.userData.vy = 0;
        scene.add(f);
        foods.push(f);
    }
});

// ============================================================
// UI КНОПКИ
// ============================================================
document.getElementById('btn-fish').addEventListener('click', () => createFish());
document.getElementById('btn-bubbles').addEventListener('click', () => { for (let i = 0; i < 10; i++) spawnBubble(); });
let lightOn = true;
document.getElementById('btn-light').addEventListener('click', function () {
    lightOn = !lightOn;
    sunLight.intensity = lightOn ? 1.0 : 0.15;
    this.textContent = lightOn ? '💡 Свет: ВКЛ' : '🌙 Свет: ВЫКЛ';
});

// ============================================================
// АНИМАЦИЯ
// ============================================================
const clock = new THREE.Clock();
let fpsTime = 0, fpsFrames = 0;
const tmpVec = new THREE.Vector3();

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    // --- Рыбки ---
    const halfW = TANK.w / 2 - 2, halfH = TANK.h / 2 - 1.5, halfD = TANK.d / 2 - 1.5;

    for (const fish of fishArray) {
        const m = fish.mesh;
        const steer = new THREE.Vector3();

        // 1. Поиск корма
        fish.targetFood = null;
        let bestDist = 15;
        for (let i = 0; i < foods.length; i++) {
            const d = m.position.distanceTo(foods[i].position);
            if (d < bestDist) { bestDist = d; fish.targetFood = foods[i]; }
        }
        if (fish.targetFood) {
            tmpVec.copy(fish.targetFood.position).sub(m.position).normalize();
            steer.add(tmpVec.multiplyScalar(3.0));
            // Съедание
            if (bestDist < 1.2) {
                scene.remove(fish.targetFood);
                foods.splice(foods.indexOf(fish.targetFood), 1);
                fish.scale = Math.min(fish.scale * 1.05, 2.0);
            }
        }

        // 2. Избегание столкновений
        for (const other of fishArray) {
            if (other === fish) continue;
            const d = m.position.distanceTo(other.mesh.position);
            if (d < fish.avoidanceRadius && d > 0.001) {
                tmpVec.copy(m.position).sub(other.mesh.position).normalize().multiplyScalar((fish.avoidanceRadius - d) / fish.avoidanceRadius * 2.5);
                steer.add(tmpVec);
            }
        }

        // 3. Случайное блуждание
        fish.wanderTimer -= dt;
        if (fish.wanderTimer <= 0) {
            fish.wanderTimer = 2 + Math.random() * 3;
            fish.velocity.x += (Math.random() - 0.5) * 0.8;
            fish.velocity.y += (Math.random() - 0.5) * 0.4;
            fish.velocity.z += (Math.random() - 0.5) * 0.8;
        }

        // 4. Отражение от стен (плавный разворот у границ)
        const margin = 3;
        if (m.position.x > halfW) steer.x -= (m.position.x - halfW + margin) * 0.8;
        if (m.position.x < -halfW) steer.x += (-halfW - m.position.x + margin) * 0.8;
        if (m.position.y > halfH) steer.y -= (m.position.y - halfH + margin) * 0.8;
        if (m.position.y < -halfH + 1) steer.y += (-halfH + 1 - m.position.y + margin) * 0.8;
        if (m.position.z > halfD) steer.z -= (m.position.z - halfD + margin) * 0.8;
        if (m.position.z < -halfD) steer.z += (-halfD - m.position.z + margin) * 0.8;

        fish.velocity.add(steer.multiplyScalar(dt));
        fish.velocity.y *= 0.995; // рыбы реже плавают строго вверх/вниз
        fish.velocity.normalize();

        m.position.addScaledVector(fish.velocity, fish.speed * dt);

        // Поворот в направлении движения
        const targetYaw = Math.atan2(-fish.velocity.z, fish.velocity.x);
        let dyaw = targetYaw - m.rotation.y;
        while (dyaw > Math.PI) dyaw -= Math.PI * 2;
        while (dyaw < -Math.PI) dyaw += Math.PI * 2;
        m.rotation.y += dyaw * Math.min(dt * 4, 1);
        m.rotation.z = THREE.MathUtils.lerp(m.rotation.z, THREE.MathUtils.clamp(-fish.velocity.y * 0.8, -0.5, 0.5), dt * 3);

        // Анимация хвоста и плавников
        const wave = Math.sin(t * fish.tailSpeed + fish.phase);
        fish.tail.rotation.y = wave * 0.6;
        fish.leftFin.rotation.z = -0.5 + wave * 0.3;
        fish.rightFin.rotation.z = -0.5 - wave * 0.3;
        m.position.y += Math.sin(t * 2 + fish.phase) * 0.003;
    }

    // --- Корм (гравитация) ---
    for (let i = foods.length - 1; i >= 0; i--) {
        const f = foods[i];
        f.userData.vy -= 3.0 * dt;
        f.position.y += f.userData.vy * dt;
        f.position.x += Math.sin(t * 3 + i) * 0.005;
        f.rotation.x += dt * 2;
        if (f.position.y < -TANK.h / 2 + 0.5) {
            scene.remove(f);
            foods.splice(i, 1);
        }
    }

    // --- Пузыри ---
    for (const b of bubbles) {
        b.position.y += b.userData.speed * dt;
        b.position.x += Math.sin(t * 2 + b.userData.phase) * b.userData.amp * dt;
        b.position.z += Math.cos(t * 1.5 + b.userData.phase) * b.userData.amp * dt;
        if (b.position.y > TANK.h / 2 - 0.5) {
            b.position.y = -TANK.h / 2 + 0.5;
            b.position.x = (Math.random() - 0.5) * (TANK.w - 4);
            b.position.z = (Math.random() - 0.5) * (TANK.d - 4);
        }
    }

    // --- Водоросли ---
    for (const s of seaweeds) {
        s.rotation.x = Math.sin(t * s.userData.speed + s.userData.phase) * 0.12;
        s.rotation.z = Math.cos(t * s.userData.speed * 0.7 + s.userData.phase) * 0.1;
    }

    // --- FPS ---
    fpsFrames++;
    fpsTime += dt;
    if (fpsTime >= 0.5) {
        document.getElementById('fps-value').textContent = Math.round(fpsFrames / fpsTime);
        fpsFrames = 0; fpsTime = 0;
    }

    controls.update();
    renderer.render(scene, camera);
}
animate();

addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

## ✨ Реализованные возможности

| Система | Детали |
|---------|--------|
| **🐠 Рыбки** | 15 штук, 8 цветовых схем, анатомия (тело, глаза с зрачками, хвост на пивоте, верхний + боковые плавники) |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен с маргином, блуждание по таймеру, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Окружение** | Стекло с `transmission: 0.95`, wireframe-рамка, процедурное песчаное дно, 8 деформированных камней, 12 TubeGeometry-водорослей |
| **💭 Пузыри** | 30 штук, MeshPhysicalMaterial, синусоидальное покачивание, сброс у поверхности |
| **🍽️ Корм** | Raycaster + плоскость → 3颗粒ки с гравитацией, клики отделены от вращения камеры (порог 5px) |
| **💡 Свет** | Ambient + Directional с PCFSoftShadow 2048², 2 голубых PointLight, переключатель |
| **🎨 Эффекты** | FogExp2, градиентный canvas-фон, glass UI с backdrop-blur, glow-кнопки |

Просто сохраните как `.html` и откройте в браузере! 🚀