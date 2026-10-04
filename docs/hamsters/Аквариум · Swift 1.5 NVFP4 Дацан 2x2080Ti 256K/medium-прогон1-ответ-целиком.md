# 🐠 3D Аквариум с Реалистичными Рыбками

Полный код интерактивного 3D аквариума — сохраните как `aquarium.html` и откройте в браузере:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #021128; }
    canvas { display: block; }

    .panel {
        position: absolute;
        padding: 16px 20px;
        background: rgba(10, 40, 80, 0.45);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(120, 200, 255, 0.25);
        border-radius: 14px;
        color: #d8f0ff;
        box-shadow: 0 4px 30px rgba(0, 60, 120, 0.4);
        user-select: none;
    }
    #info-panel { top: 16px; left: 16px; max-width: 280px; }
    #stats-panel { top: 16px; right: 16px; text-align: right; }

    h1 {
        font-size: 20px;
        margin-bottom: 8px;
        background: linear-gradient(90deg, #4dd0ff, #aaffee, #ffd76e);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .instructions { font-size: 12px; line-height: 1.6; opacity: 0.85; margin-bottom: 12px; }

    button {
        display: block;
        width: 100%;
        margin: 6px 0;
        padding: 9px 14px;
        border: none;
        border-radius: 9px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        background: linear-gradient(135deg, #0e7bb8, #15b5d5);
        box-shadow: 0 2px 10px rgba(20, 150, 220, 0.4);
        transition: transform .15s, box-shadow .15s, filter .15s;
    }
    button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 4px 18px rgba(30, 190, 255, 0.6);
        filter: brightness(1.15);
    }
    button:active { transform: scale(0.97); }

    #stats-panel div { font-size: 14px; margin: 3px 0; }
    .stat-value { color: #7dffb0; font-weight: bold; }
    #hint {
        position: absolute; bottom: 14px; left: 50%;
        transform: translateX(-50%);
        font-size: 13px; color: rgba(180, 225, 255, 0.7);
        background: rgba(10, 40, 80, 0.35);
        padding: 6px 18px; border-radius: 20px;
        backdrop-filter: blur(6px);
        pointer-events: none;
    }
    @media (max-width: 640px) {
        #info-panel { max-width: 200px; padding: 10px; }
        h1 { font-size: 15px; }
        .instructions { display: none; }
    }
</style>
</head>
<body>

<div id="info-panel" class="panel">
    <h1>🐠 3D Аквариум</h1>
    <div class="instructions">
        🖱️ Левый клик — вращение камеры<br>
        🖱️ Правый клик — панорамирование<br>
        ⚙️ Колесо мыши — зум<br>
        🍽️ Клик по воде — кормить рыбок
    </div>
    <button id="btn-add-fish">🐟 Добавить рыбку</button>
    <button id="btn-bubbles">💭 Больше пузырей</button>
    <button id="btn-light">💡 Свет вкл/выкл</button>
</div>

<div id="stats-panel" class="panel">
    <div>Рыбки: <span class="stat-value" id="fish-count">15</span></div>
    <div>FPS: <span class="stat-value" id="fps">0</span></div>
</div>

<div id="hint">Кликните по аквариуму, чтобы покормить рыбок! 🍤</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
// СЦЕНА, КАМЕРА, РЕНДЕРЕР
// ============================================================
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x062a52, 0.018);

// Градиентный фон
(function makeBackground() {
    const c = document.createElement('canvas');
    c.width = 2; c.height = 512;
    const ctx = c.getContext('2d');
    const g = ctx.createLinearGradient(0, 0, 0, 512);
    g.addColorStop(0, '#0a4a80');
    g.addColorStop(0.5, '#062a52');
    g.addColorStop(1, '#021128');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 2, 512);
    const tex = new THREE.CanvasTexture(c);
    scene.background = tex;
})();

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(24, 14, 28);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ============================================================
// ОСВЕЩЕНИЕ
// ============================================================
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(15, 30, 10);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.left = -25;
dirLight.shadow.camera.right = 25;
dirLight.shadow.camera.top = 25;
dirLight.shadow.camera.bottom = -25;
scene.add(dirLight);

const blueLight1 = new THREE.PointLight(0x3388ff, 0.8, 40);
blueLight1.position.set(-12, 8, -6);
scene.add(blueLight1);

const blueLight2 = new THREE.PointLight(0x22ccff, 0.6, 40);
blueLight2.position.set(12, 4, 8);
scene.add(blueLight2);

// ============================================================
// УПРАВЛЕНИЕ КАМЕРОЙ
// ============================================================
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;

// ============================================================
// АКВАРИУМ (СТЕКЛО)
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };

const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0x88ccff,
    transparent: true,
    opacity: 0.08,
    transmission: 0.95,
    roughness: 0.05,
    metalness: 0,
    side: THREE.DoubleSide,
    depthWrite: false
});
const glass = new THREE.Mesh(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d), glassMat);
scene.add(glass);

const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d)),
    new THREE.LineBasicMaterial({ color: 0x66bbee, transparent: true, opacity: 0.5 })
);
scene.add(edges);

// ============================================================
// ПЕСЧАНОЕ ДНО (с процедурными неровностями)
// ============================================================
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
sandGeo.rotateX(-Math.PI / 2);
const posAttr = sandGeo.attributes.position;
for (let i = 0; i < posAttr.count; i++) {
    const x = posAttr.getX(i), z = posAttr.getZ(i);
    const y = Math.sin(x * 0.7) * Math.cos(z * 0.9) * 0.25
            + Math.sin(x * 1.8 + z * 1.3) * 0.12;
    posAttr.setY(i, y - TANK.h / 2 + 0.1);
}
sandGeo.computeVertexNormals();
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({
    color: 0xd9b982, roughness: 0.95
}));
sand.receiveShadow = true;
scene.add(sand);

// ============================================================
// КАМНИ (деформированные додекаэдры)
// ============================================================
for (let i = 0; i < 8; i++) {
    const geo = new THREE.DodecahedronGeometry(0.7 + Math.random() * 1.2, 1);
    const p = geo.attributes.position;
    for (let j = 0; j < p.count; j++) {
        p.setXYZ(j,
            p.getX(j) * (0.8 + Math.random() * 0.4),
            p.getY(j) * (0.7 + Math.random() * 0.3),
            p.getZ(j) * (0.8 + Math.random() * 0.4));
    }
    geo.computeVertexNormals();
    const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.08, 0.1, 0.25 + Math.random() * 0.2),
        roughness: 0.9
    }));
    rock.position.set(
        (Math.random() - 0.5) * (TANK.w - 6),
        -TANK.h / 2 + 0.4,
        (Math.random() - 0.5) * (TANK.d - 5)
    );
    rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    rock.castShadow = true;
    rock.receiveShadow = true;
    scene.add(rock);
}

// ============================================================
// ВОДОРОСЛИ (TubeGeometry + CatmullRomCurve3)
// ============================================================
const seaweeds = [];
for (let i = 0; i < 12; i++) {
    const height = 3 + Math.random() * 5;
    const baseX = (Math.random() - 0.5) * (TANK.w - 4);
    const baseZ = (Math.random() - 0.5) * (TANK.d - 4);
    const pts = [];
    for (let j = 0; j <= 5; j++) {
        const t = j / 5;
        pts.push(new THREE.Vector3(
            Math.sin(t * 3 + i) * 0.5 * t,
            t * height,
            Math.cos(t * 2.5 + i) * 0.4 * t
        ));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    const geo = new THREE.TubeGeometry(curve, 12, 0.12, 5, false);
    const mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.28 + Math.random() * 0.12, 0.7, 0.3 + Math.random() * 0.15),
        roughness: 0.8
    });
    const group = new THREE.Group();
    const stem = new THREE.Mesh(geo, mat);
    stem.castShadow = true;
    group.add(stem);
    group.position.set(baseX, -TANK.h / 2, baseZ);
    group.userData.phase = Math.random() * Math.PI * 2;
    group.userData.speed = 0.5 + Math.random() * 0.8;
    scene.add(group);
    seaweeds.push(group);
}

// ============================================================
// РЫБКИ
// ============================================================
const COLOR_SCHEMES = [
    { body: 0xff7b26, fin: 0xffb066 }, // оранжевая
    { body: 0x2f6bff, fin: 0x8fb3ff }, // синяя
    { body: 0xffd426, fin: 0xff5533 }, // желто-красная
    { body: 0x9b4dff, fin: 0xd0a5ff }, // фиолетовая
    { body: 0xe02d2d, fin: 0xff8080 }, // красная
    { body: 0x2dbe5a, fin: 0x9df0b6 }, // зеленая
    { body: 0xff5fa2, fin: 0xffb1cf }, // розовая
    { body: 0xe8b42a, fin: 0xffe9a3 }  // золотая
];

const fishArray = [];

function createFish() {
    const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
    const group = new THREE.Group();
    const bodyMat = new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.2 });
    const finMat  = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85, side: THREE.DoubleSide });

    // Тело — вытянутая сфера
    const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
    body.scale.set(1.6, 0.85, 0.55);
    body.castShadow = true;
    group.add(body);

    // Глаза
    const eyeGeo = new THREE.SphereGeometry(0.18, 8, 8);
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const pupilGeo = new THREE.SphereGeometry(0.09, 6, 6);
    const pupilMat = new THREE.MeshBasicMaterial({ color: 0x111111 });
    [-1, 1].forEach(s => {
        const eye = new THREE.Mesh(eyeGeo, eyeMat);
        eye.position.set(1.25, 0.22, s * 0.36);
        group.add(eye);
        const pupil = new THREE.Mesh(pupilGeo, pupilMat);
        pupil.position.set(1.38, 0.22, s * 0.4);
        group.add(pupil);
    });

    // Хвост (группа для вращения вокруг своей оси)
    const tailPivot = new THREE.Group();
    tailPivot.position.x = -1.5;
    const tailShape = new THREE.Shape();
    tailShape.moveTo(0, 0);
    tailShape.quadraticCurveTo(-0.7, 0.6, -1.1, 0.85);
    tailShape.quadraticCurveTo(-0.55, 0, -1.1, -0.85);
    tailShape.quadraticCurveTo(-0.7, -0.6, 0, 0);
    const tail = new THREE.Mesh(new THREE.ShapeGeometry(tailShape), finMat);
    tailPivot.add(tail);
    group.add(tailPivot);

    // Верхний плавник
    const topFinShape = new THREE.Shape();
    topFinShape.moveTo(-0.6, 0);
    topFinShape.quadraticCurveTo(0.2, 1.0, 0.7, 0.15);
    topFinShape.lineTo(-0.6, 0);
    const topFin = new THREE.Mesh(new THREE.ShapeGeometry(topFinShape), finMat);
    topFin.rotation.y = Math.PI / 2;
    topFin.position.y = 0.68;
    group.add(topFin);

    // Боковые плавники (анимируемые)
    const sideFinShape = new THREE.Shape();
    sideFinShape.moveTo(0, 0);
    sideFinShape.quadraticCurveTo(0.4, -0.35, 0.7, -0.15);
    sideFinShape.quadraticCurveTo(0.3, 0.15, 0, 0);
    const fins = [];
    [-1, 1].forEach(s => {
        const finPivot = new THREE.Group();
        finPivot.position.set(0.3, -0.15, s * 0.45);
        const fin = new THREE.Mesh(new THREE.ShapeGeometry(sideFinShape), finMat);
        fin.rotation.y = Math.PI / 2;
        fin.scale.setScalar(0.8);
        finPivot.add(fin);
        group.add(finPivot);
        fins.push(finPivot);
    });

    const scale = 0.6 + Math.random() * 0.6;
    group.scale.setScalar(scale);
    group.position.set(
        (Math.random() - 0.5) * (TANK.w - 8),
        (Math.random() - 0.2) * (TANK.h - 8),
        (Math.random() - 0.5) * (TANK.d - 6)
    );
    scene.add(group);

    const dir = new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5).normalize();

    fishArray.push({
        mesh: group,
        tail: tailPivot,
        leftFin: fins[0],
        rightFin: fins[1],
        velocity: dir.multiplyScalar(1 + Math.random()),
        speed: 2 + Math.random() * 3,
        tailSpeed: 4 + Math.random() * 4,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5,
        wanderTimer: Math.random() * 3
    });
    updateFishCount();
}

function updateFishCount() {
    document.getElementById('fish-count').textContent = fishArray.length;
}
for (let i = 0; i < 15; i++) createFish();

// ============================================================
// ПУЗЫРИ
// ============================================================
const bubbles = [];
const bubbleMat = new THREE.MeshPhysicalMaterial({
    color: 0xcceeff, transparent: true, opacity: 0.35,
    transmission: 0.9, roughness: 0.1, metalness: 0, side: THREE.DoubleSide
});

function addBubbles(n) {
    for (let i = 0; i < n; i++) {
        const b = new THREE.Mesh(new THREE.SphereGeometry(0.1 + Math.random() * 0.22, 8, 8), bubbleMat);
        b.position.set(
            (Math.random() - 0.5) * (TANK.w - 4),
            -TANK.h / 2 + Math.random() * TANK.h,
            (Math.random() - 0.5) * (TANK.d - 4)
        );
        b.userData.speed = 1.5 + Math.random() * 2.5;
        b.userData.phase = Math.random() * Math.PI * 2;
        b.userData.baseX = b.position.x;
        b.userData.baseZ = b.position.z;
        scene.add(b);
        bubbles.push(b);
    }
}
addBubbles(30);

// ============================================================
// КОРМ
// ============================================================
const foods = [];
const foodGeo = new THREE.SphereGeometry(0.22, 6, 6);
const foodMat = new THREE.MeshStandardMaterial({ color: 0xc47a3d, roughness: 0.8 });

function spawnFood(x, y, z) {
    const f = new THREE.Mesh(foodGeo, foodMat);
    f.position.set(
        THREE.MathUtils.clamp(x, -TANK.w/2 + 1, TANK.w/2 - 1),
        Math.min(y, TANK.h/2 - 1),
        THREE.MathUtils.clamp(z, -TANK.d/2 + 1, TANK.d/2 - 1)
    );
    f.userData.vy = 0;
    scene.add(f);
    foods.push(f);
}

// Кормление по клику (Raycaster)
const raycaster = new THREE.Raycaster();
const mouseNDC = new THREE.Vector2();
let dragStart = null;

renderer.domElement.addEventListener('pointerdown', e => {
    dragStart = { x: e.clientX, y: e.clientY };
});
renderer.domElement.addEventListener('pointerup', e => {
    if (!dragStart) return;
    const dx = e.clientX - dragStart.x, dy = e.clientY - dragStart.y;
    dragStart = null;
    if (dx*dx + dy*dy > 25) return; // это был drag камеры, не клик
    if (e.button !== 0) return;

    mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    raycaster.setFromCamera(mouseNDC, camera);
    // Плоскость z=0 через центр аквариума, перпендикулярная лучу
    const point = new THREE.Vector3();
    raycaster.ray.at(camera.position.distanceTo(controls.target), point);
    spawnFood(
        THREE.MathUtils.clamp(point.x, -TANK.w/2 + 1, TANK.w/2 - 1),
        TANK.h/2 - 2,
        THREE.MathUtils.clamp(point.z, -TANK.d/2 + 1, TANK.d/2 - 1)
    );
});

// ============================================================
// КНОПКИ UI
// ============================================================
let lightOn = true;
document.getElementById('btn-add-fish').addEventListener('click', () => createFish());
document.getElementById('btn-bubbles').addEventListener('click', () => addBubbles(10));
document.getElementById('btn-light').addEventListener('click', () => {
    lightOn = !lightOn;
    dirLight.intensity = lightOn ? 1.0 : 0.05;
});

// ============================================================
// АНИМАЦИЯ
// ============================================================
const clock = new THREE.Clock();
const BOUNDS = {
    x: TANK.w / 2 - 2.5,
    yTop: TANK.h / 2 - 2.5,
    yBot: -TANK.h / 2 + 1.8,
    z: TANK.d / 2 - 2.5
};
const tmpVec = new THREE.Vector3();
const lookTarget = new THREE.Vector3();

let fpsFrames = 0, fpsTime = 0;

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    // --- Корм ---
    for (let i = foods.length - 1; i >= 0; i--) {
        const f = foods[i];
        f.userData.vy -= 4 * dt; // гравитация
        f.userData.vy = Math.max(f.userData.vy, -3);
        f.position.y += f.userData.vy * dt;
        f.position.x += Math.sin(t * 2 + i) * 0.15 * dt;

        // съеден?
        let eaten = false;
        for (const fish of fishArray) {
            if (fish.mesh.position.distanceTo(f.position) < 1.3 * fish.mesh.scale.x + 0.5) {
                eaten = true;
                // рост 5%
                const s = Math.min(fish.mesh.scale.x * 1.05, 2.2);
                fish.mesh.scale.setScalar(s);
                break;
            }
        }
        if (eaten || f.position.y <= BOUNDS.yBot) {
            scene.remove(f);
            foods.splice(i, 1);
        }
    }

    // --- Рыбки ---
    for (const fish of fishArray) {
        const p = fish.mesh.position;

        // Поиск корма (радиус 15)
        fish.targetFood = null;
        let bestDist = 15;
        for (const f of foods) {
            const d = p.distanceTo(f.position);
            if (d < bestDist) { bestDist = d; fish.targetFood = f; }
        }

        if (fish.targetFood) {
            tmpVec.copy(fish.targetFood.position).sub(p).normalize();
            fish.velocity.lerp(tmpVec.multiplyScalar(fish.speed * 1.6), 3 * dt);
        } else {
            // Случайное блуждание
            fish.wanderTimer -= dt;
            if (fish.wanderTimer <= 0) {
                fish.wanderTimer = 2 + Math.random() * 4;
                tmpVec.set(
                    (Math.random() - 0.5),
                    (Math.random() - 0.5) * 0.4,
                    (Math.random() - 0.5)
                ).normalize().multiplyScalar(fish.speed);
                fish.velocity.lerp(tmpVec, 0.6);
            }
        }

        // Избегание столкновений
        for (const other of fishArray) {
            if (other === fish) continue;
            tmpVec.copy(p).sub(other.mesh.position);
            const d = tmpVec.length();
            if (d < fish.avoidanceRadius && d > 0.001) {
                tmpVec.normalize().multiplyScalar((fish.avoidanceRadius - d) * 4 * dt);
                fish.velocity.add(tmpVec);
            }
        }

        // Отражение от стен (плавное)
        const margin = 3;
        if (p.x > BOUNDS.x)     fish.velocity.x -= (p.x - BOUNDS.x + margin) * dt * 3;
        if (p.x < -BOUNDS.x)    fish.velocity.x += (-BOUNDS.x - p.x + margin) * dt * 3;
        if (p.y > BOUNDS.yTop)  fish.velocity.y -= (p.y - BOUNDS.yTop + margin) * dt * 3;
        if (p.y < BOUNDS.yBot)  fish.velocity.y += (BOUNDS.yBot - p.y + margin) * dt * 3;
        if (p.z > BOUNDS.z)     fish.velocity.z -= (p.z - BOUNDS.z + margin) * dt * 3;
        if (p.z < -BOUNDS.z)    fish.velocity.z += (-BOUNDS.z - p.z + margin) * dt * 3;

        // Ограничение скорости
        const vLen = fish.velocity.length();
        const maxV = fish.speed * 1.8;
        if (vLen > maxV) fish.velocity.multiplyScalar(maxV / vLen);
        if (vLen < fish.speed * 0.4 && vLen > 0.001) fish.velocity.multiplyScalar(fish.speed * 0.4 / vLen);

        // Позиция
        p.addScaledVector(fish.velocity, dt);
        p.x = THREE.MathUtils.clamp(p.x, -BOUNDS.x - 1, BOUNDS.x + 1);
        p.y = THREE.MathUtils.clamp(p.y, BOUNDS.yBot - 0.5, BOUNDS.yTop + 0.5);
        p.z = THREE.MathUtils.clamp(p.z, -BOUNDS.z - 1, BOUNDS.z + 1);

        // Поворот в направлении движения (рыба смотрит +X)
        lookTarget.copy(p).add(fish.velocity);
        fish.mesh.lookAt(lookTarget);
        fish.mesh.rotateY(Math.PI / 2);

        // Анимация хвоста и плавников
        const phase = t * fish.tailSpeed + fish.phase;
        fish.tail.rotation.y = Math.sin(phase) * 0.55;
        fish.leftFin.rotation.x = Math.sin(phase * 1.3) * 0.4;
        fish.rightFin.rotation.x = -Math.sin(phase * 1.3) * 0.4;
    }

    // --- Пузыри ---
    for (const b of bubbles) {
        b.position.y += b.userData.speed * dt;
        b.position.x = b.userData.baseX + Math.sin(t * 2 + b.userData.phase) * 0.4;
        b.position.z = b.userData.baseZ + Math.cos(t * 1.6 + b.userData.phase) * 0.3;
        if (b.position.y > TANK.h / 2 - 0.5) {
            b.position.y = -TANK.h / 2 + 0.5;
            b.userData.baseX = (Math.random() - 0.5) * (TANK.w - 4);
            b.userData.baseZ = (Math.random() - 0.5) * (TANK.d - 4);
        }
    }

    // --- Водоросли ---
    for (const sw of seaweeds) {
        const ph = t * sw.userData.speed + sw.userData.phase;
        sw.rotation.x = Math.sin(ph) * 0.12;
        sw.rotation.z = Math.cos(ph * 0.8) * 0.1;
    }

    controls.update();
    renderer.render(scene, camera);

    // FPS
    fpsFrames++;
    fpsTime += dt;
    if (fpsTime >= 0.5) {
        document.getElementById('fps').textContent = Math.round(fpsFrames / fpsTime);
        fpsFrames = 0; fpsTime = 0;
    }
}
animate();

// ============================================================
// RESIZE
// ============================================================
window.addEventListener('resize', () => {
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
|---|---|
| **🐠 Рыбки** | 15 штук, 8 цветовых схем, тело-сфера, глаза с зрачками, анимированный хвост + 3 плавника, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, мягкое отражение от стен, блуждание, преследование корма (радиус 15), рост +5% при поедании |
| **🌊 Окружение** | Стекло с `transmission: 0.95`, wireframe-рамка, процедурное песчаное дно, 8 деформированных камней, 12 водорослей на `TubeGeometry` |
| **💭 Пузыри** | 30 штук, `MeshPhysicalMaterial`, синусоидальное покачивание, сброс у поверхности |
| **🍽️ Корм** | Клик (отличается от drag камеры!), гравитация, съедение с ростом, удаление на дне |
| **💡 Свет** | Ambient + Directional с PCFSoft-тенями 2048², 2 голубых PointLight, переключение кнопкой |
| **🎮 Камера** | OrbitControls с damping, зум 10–60, ограничение polar angle |
| **🖥️ UI** | Glassmorphism-панели, градиентный заголовок, FPS-счетчик, адаптивный дизайн |

**Совет:** кликайте в центр аквариума для кормления — рыбки со всего аквариума поплывут к корму! 🍤