

# 🐠 3D Аквариум с Реалистичными Рыбками

Готовое решение в одном HTML-файле:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; }
    #canvas-container { width: 100vw; height: 100vh; }

    .panel {
        position: absolute;
        background: rgba(10, 30, 60, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 200, 255, 0.25);
        border-radius: 14px;
        padding: 16px 20px;
        color: #dceeff;
        box-shadow: 0 8px 32px rgba(0, 20, 60, 0.5), inset 0 0 20px rgba(80, 180, 255, 0.08);
        z-index: 10;
    }

    #info-panel { top: 20px; left: 20px; max-width: 300px; }
    #info-panel h1 {
        font-size: 22px;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #4dd0ff, #a78bfa, #ff9d6c);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    #info-panel p { font-size: 12.5px; line-height: 1.6; opacity: 0.85; }
    #info-panel .key { color: #7fdcff; font-weight: 600; }

    #stats-panel { top: 20px; right: 20px; min-width: 180px; }
    #stats-panel .stat { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 6px; }
    #stats-panel .val { color: #7fdcff; font-weight: 700; }

    .btn-row { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
    button {
        cursor: pointer;
        border: none;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
    }
    button:hover { transform: translateY(-2px); filter: brightness(1.15); }
    button:active { transform: translateY(0); }

    #btn-fish   { background: linear-gradient(135deg, #ff7e5f, #feb47b); box-shadow: 0 4px 14px rgba(255,126,95,.4); }
    #btn-bubble { background: linear-gradient(135deg, #36d1dc, #5b86e5); box-shadow: 0 4px 14px rgba(54,209,220,.4); }
    #btn-light  { background: linear-gradient(135deg, #f7971e, #ffd200); box-shadow: 0 4px 14px rgba(255,210,0,.4); }

    @media (max-width: 640px) {
        #info-panel { max-width: 200px; padding: 10px 14px; }
        #info-panel h1 { font-size: 16px; }
        #info-panel p { font-size: 11px; }
    }
</style>
</head>
<body>
<div id="canvas-container"></div>

<div class="panel" id="info-panel">
    <h1>🐠 3D Аквариум</h1>
    <p>
        <span class="key">ЛКМ + движение</span> — вращение камеры<br>
        <span class="key">ПКМ + движение</span> — панорама<br>
        <span class="key">Колесо</span> — зум<br>
        <span class="key">Клик по воде</span> — покормить рыбок 🍤
    </p>
    <div class="btn-row">
        <button id="btn-fish">➕ Добавить рыбку</button>
        <button id="btn-bubble">💧 Больше пузырей</button>
        <button id="btn-light">💡 Свет: ВКЛ</button>
    </div>
</div>

<div class="panel" id="stats-panel">
    <div class="stat"><span>🐟 Рыбки:</span><span class="val" id="fish-count">0</span></div>
    <div class="stat"><span>📊 FPS:</span><span class="val" id="fps">0</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
//  БАЗОВЫЕ НАСТРОЙКИ
// ============================================================
const TANK = { w: 36, h: 24, d: 20 };            // размеры аквариума
const FISH_COUNT = 15, BUBBLE_COUNT = 30;
const FOOD_DETECT_RADIUS = 15, FOOD_EAT_RADIUS = 1.2;

const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x0a2a4a, 0.012);

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
camera.position.set(0, 12, 42);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// Градиентный фон
(function makeGradient() {
    const c = document.createElement('canvas');
    c.width = 2; c.height = 256;
    const ctx = c.getContext('2d');
    const g = ctx.createLinearGradient(0, 0, 0, 256);
    g.addColorStop(0, '#0b3d6e');
    g.addColorStop(1, '#041428');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 2, 256);
    scene.background = new THREE.CanvasTexture(c);
})();

// ============================================================
//  КАМЕРА / КОНТРОЛЫ
// ============================================================
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 10;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 1.8;
controls.target.set(0, 2, 0);

// ============================================================
//  ОСВЕЩЕНИЕ
// ============================================================
scene.add(new THREE.AmbientLight(0x404040, 0.4));

const sunLight = new THREE.DirectionalLight(0xbfe8ff, 1.1);
sunLight.position.set(15, 30, 10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -25; sunLight.shadow.camera.right = 25;
sunLight.shadow.camera.top = 25;   sunLight.shadow.camera.bottom = -25;
scene.add(sunLight);

const underwater1 = new THREE.PointLight(0x33ccff, 0.7, 50);
underwater1.position.set(-10, 8, 5);
scene.add(underwater1);
const underwater2 = new THREE.PointLight(0x2255ff, 0.5, 50);
underwater2.position.set(10, 4, -5);
scene.add(underwater2);

// ============================================================
//  АКВАРИУМ: СТЕКЛО, ПЕСОК, КАМНИ, ВОДОРОСЛИ
// ============================================================
const hw = TANK.w / 2, hh = TANK.h / 2, hd = TANK.d / 2;

// Стеклянный контейнер
const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xaaddff, transmission: 0.95, transparent: true,
    opacity: 0.25, roughness: 0.05, metalness: 0, side: THREE.DoubleSide
});
const glass = new THREE.Mesh(new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d), glassMat);
glass.position.y = hh;
scene.add(glass);

// Рамка (wireframe)
const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(glass.geometry),
    new THREE.LineBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.5 })
);
edges.position.copy(glass.position);
scene.add(edges);

// Песчаное дно с процедурными неровностями
const sandGeo = new THREE.PlaneGeometry(TANK.w, TANK.d, 40, 30);
{
    const pos = sandGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), y = pos.getY(i);
        pos.setZ(i, Math.sin(x * 0.5) * 0.25 + Math.cos(y * 0.7) * 0.2 + Math.random() * 0.15);
    }
    sandGeo.computeVertexNormals();
}
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({ color: 0xd9c08a, roughness: 0.95 }));
sand.rotation.x = -Math.PI / 2;
sand.receiveShadow = true;
scene.add(sand);

// Декоративные камни (8)
for (let i = 0; i < 8; i++) {
    const s = 0.8 + Math.random() * 1.4;
    const rockGeo = new THREE.DodecahedronGeometry(s, 0);
    const rp = rockGeo.attributes.position;
    for (let v = 0; v < rp.count; v++) {
        rp.setXYZ(v,
            rp.getX(v) * (0.8 + Math.random() * 0.4),
            rp.getY(v) * (0.6 + Math.random() * 0.4),
            rp.getZ(v) * (0.8 + Math.random() * 0.4));
    }
    rockGeo.computeVertexNormals();
    const rock = new THREE.Mesh(rockGeo, new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.15, 0.3 + Math.random() * 0.2),
        roughness: 0.9
    }));
    rock.position.set((Math.random() - 0.5) * (TANK.w - 6), 0.4, (Math.random() - 0.5) * (TANK.d - 6));
    rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
    rock.castShadow = rock.receiveShadow = true;
    scene.add(rock);
}

// Водоросли (12) — TubeGeometry + CatmullRomCurve3
const algaeList = [];
for (let i = 0; i < 12; i++) {
    const h = 3 + Math.random() * 5;
    const pts = [];
    for (let j = 0; j <= 5; j++) {
        pts.push(new THREE.Vector3(
            Math.sin(j * 1.2) * 0.3, j * (h / 5), Math.cos(j * 0.9) * 0.3));
    }
    const curve = new THREE.CatmullRomCurve3(pts);
    const tube = new THREE.Mesh(
        new THREE.TubeGeometry(curve, 12, 0.12 + Math.random() * 0.1, 5),
        new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.3 + Math.random() * 0.1, 0.7, 0.3 + Math.random() * 0.15),
            roughness: 0.7
        })
    );
    tube.position.set((Math.random() - 0.5) * (TANK.w - 8), 0, (Math.random() - 0.5) * (TANK.d - 8));
    tube.castShadow = true;
    scene.add(tube);
    algaeList.push({ mesh: tube, phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() });
}

// ============================================================
//  РЫБКИ
// ============================================================
const COLOR_SCHEMES = [
    { body: 0xff7733, fin: 0xffaa66 },  // оранжевая
    { body: 0x3366ff, fin: 0x66aaff },  // синяя
    { body: 0xffcc00, fin: 0xff4444 },  // жёлто-красная
    { body: 0xaa44ff, fin: 0xdd99ff },  // фиолетовая
    { body: 0xff3344, fin: 0xff8899 },  // красная
    { body: 0x33cc66, fin: 0x88ffaa },  // зелёная
    { body: 0xff77bb, fin: 0xffbbdd },  // розовая
    { body: 0xffb700, fin: 0xffe066 }   // золотая
];

function createFish(scale) {
    scale = scale || 0.6 + Math.random() * 0.6;
    const scheme = COLOR_SCHEMES[Math.floor(Math.random() * COLOR_SCHEMES.length)];
    const group = new THREE.Group();

    // Тело — вытянутая сфера
    const body = new THREE.Mesh(
        new THREE.SphereGeometry(0.8, 12, 10),
        new THREE.MeshStandardMaterial({ color: scheme.body, roughness: 0.4, metalness: 0.15 })
    );
    body.scale.set(1.8, 1, 0.9);
    body.castShadow = true;
    group.add(body);

    // Глаза с зрачками
    [-1, 1].forEach(side => {
        const eye = new THREE.Mesh(
            new THREE.SphereGeometry(0.16, 8, 8),
            new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 }));
        eye.position.set(1.1, 0.15, side * 0.5);
        const pupil = new THREE.Mesh(
            new THREE.SphereGeometry(0.08, 6, 6),
            new THREE.MeshBasicMaterial({ color: 0x111111 }));
        pupil.position.z = side * 0.13;
        eye.add(pupil);
        group.add(eye);
    });

    // Хвост (анимируется по Z)
    const tail = new THREE.Mesh(
        new THREE.ConeGeometry(0.55, 1.1, 8),
        new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.9 })
    );
    tail.rotation.z = Math.PI / 2;
    tail.position.x = -1.7;
    group.add(tail);

    // Верхний плавник
    const topFin = new THREE.Mesh(
        new THREE.ConeGeometry(0.4, 0.9, 6),
        new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85 })
    );
    topFin.position.set(0, 0.75, 0);
    group.add(topFin);

    // Боковые плавники
    const finGeo = new THREE.ConeGeometry(0.35, 0.7, 5);
    const finMat = new THREE.MeshStandardMaterial({ color: scheme.fin, roughness: 0.5, transparent: true, opacity: 0.85 });
    const leftFin = new THREE.Mesh(finGeo, finMat);
    leftFin.rotation.z = Math.PI / 2.3;
    leftFin.position.set(0.2, -0.25, 0.7);
    const rightFin = new THREE.Mesh(finGeo, finMat);
    rightFin.rotation.z = Math.PI / 2.3;
    rightFin.position.set(0.2, -0.25, -0.7);
    group.add(leftFin, rightFin);

    group.scale.setScalar(scale);
    group.position.set(
        (Math.random() - 0.5) * (TANK.w - 8),
        3 + Math.random() * (TANK.h - 8),
        (Math.random() - 0.5) * (TANK.d - 8)
    );
    scene.add(group);

    return {
        mesh: group, tail, leftFin, rightFin,
        velocity: new THREE.Vector3(Math.random() - 0.5, (Math.random() - 0.5) * 0.3, Math.random() - 0.5).normalize(),
        speed: 3 + Math.random() * 3,
        tailSpeed: 6 + Math.random() * 4,
        phase: Math.random() * Math.PI * 2,
        wanderTimer: Math.random() * 3,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5
    };
}

const fishArray = [];
for (let i = 0; i < FISH_COUNT; i++) fishArray.push(createFish());

// ============================================================
//  ПУЗЫРИ
// ============================================================
const bubbleMat = new THREE.MeshPhysicalMaterial({
    color: 0xcceeff, transmission: 0.9, transparent: true, opacity: 0.4,
    roughness: 0, metalness: 0
});
const bubbles = [];

function createBubble() {
    const r = 0.08 + Math.random() * 0.22;
    const b = new THREE.Mesh(new THREE.SphereGeometry(r, 8, 8), bubbleMat);
    b.position.set(
        (Math.random() - 0.5) * (TANK.w - 4),
        Math.random() * TANK.h,
        (Math.random() - 0.5) * (TANK.d - 4)
    );
    b.userData = {
        speed: 1.5 + Math.random() * 2.5,
        phase: Math.random() * Math.PI * 2,
        baseX: b.position.x, baseZ: b.position.z
    };
    scene.add(b);
    bubbles.push(b);
}
for (let i = 0; i < BUBBLE_COUNT; i++) createBubble();

// ============================================================
//  СИСТЕМА КОРМЛЕНИЯ
// ============================================================
const foodArray = [];
const foodMat = new THREE.MeshStandardMaterial({ color: 0xcc8844, roughness: 0.8 });

function spawnFood(pos) {
    const f = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 6), foodMat);
    f.position.copy(pos);
    f.userData.velocity = new THREE.Vector3((Math.random() - 0.5) * 0.5, -0.5, (Math.random() - 0.5) * 0.5);
    scene.add(f);
    foodArray.push(f);
}

// Клик по воде → корм
const raycaster = new THREE.Raycaster();
const clickPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -hh); // поверхность воды
const mouseNDC = new THREE.Vector2();

renderer.domElement.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;
    mouseNDC.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    raycaster.setFromCamera(mouseNDC, camera);
    const hit = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(clickPlane, hit)) {
        hit.x = THREE.MathUtils.clamp(hit.x, -hw + 1, hw - 1);
        hit.z = THREE.MathUtils.clamp(hit.z, -hd + 1, hd - 1);
        spawnFood(hit);
    }
});

// ============================================================
//  UI
// ============================================================
document.getElementById('btn-fish').onclick = () => fishArray.push(createFish());
document.getElementById('btn-bubble').onclick = () => { for (let i = 0; i < 10; i++) createBubble(); };

let lightOn = true;
document.getElementById('btn-light').onclick = function () {
    lightOn = !lightOn;
    sunLight.intensity = lightOn ? 1.1 : 0.1;
    this.textContent = '💡 Свет: ' + (lightOn ? 'ВКЛ' : 'ВЫКЛ');
};

const fishCountEl = document.getElementById('fish-count');
const fpsEl = document.getElementById('fps');
let frames = 0, fpsTime = 0;

// ============================================================
//  ЦИКЛ АНИМАЦИИ
// ============================================================
const clock = new THREE.Clock();
const tmpDir = new THREE.Vector3();

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    // --- FPS ---
    frames++; fpsTime += dt;
    if (fpsTime >= 0.5) {
        fpsEl.textContent = Math.round(frames / fpsTime);
        fishCountEl.textContent = fishArray.length;
        frames = 0; fpsTime = 0;
    }

    // --- Водоросли ---
    for (const a of algaeList) {
        a.mesh.rotation.x = Math.sin(t * a.speed + a.phase) * 0.08;
        a.mesh.rotation.z = Math.cos(t * a.speed * 0.8 + a.phase) * 0.08;
    }

    // --- Пузыри ---
    for (const b of bubbles) {
        const u = b.userData;
        b.position.y += u.speed * dt;
        b.position.x = u.baseX + Math.sin(t * 2 + u.phase) * 0.4;
        b.position.z = u.baseZ + Math.cos(t * 1.6 + u.phase) * 0.4;
        if (b.position.y > TANK.h - 0.5) {
            b.position.y = 0.3;
            u.baseX = (Math.random() - 0.5) * (TANK.w - 4);
            u.baseZ = (Math.random() - 0.5) * (TANK.d - 4);
        }
    }

    // --- Корм: гравитация ---
    for (let i = foodArray.length - 1; i >= 0; i--) {
        const f = foodArray[i];
        f.userData.velocity.y -= 4 * dt;          // гравитация
        f.position.addScaledVector(f.userData.velocity, dt);
        if (f.position.y < 0.3) {                 // упал на дно
            scene.remove(f);
            foodArray.splice(i, 1);
        }
    }

    // --- Рыбки ---
    for (let i = 0; i < fishArray.length; i++) {
        const fish = fishArray[i];
        const p = fish.mesh.position;

        // Поиск корма
        fish.targetFood = null;
        let bestDist = FOOD_DETECT_RADIUS;
        for (const f of foodArray) {
            const d = p.distanceTo(f.position);
            if (d < bestDist) { bestDist = d; fish.targetFood = f; }
        }

        // Направление
        if (fish.targetFood) {
            tmpDir.copy(fish.targetFood.position).sub(p).normalize();
            fish.velocity.lerp(tmpDir, 0.08);
            fish.velocity.normalize();
        } else {
            // Случайное блуждание
            fish.wanderTimer -= dt;
            if (fish.wanderTimer <= 0) {
                fish.wanderTimer = 2 + Math.random() * 4;
                fish.velocity.x += (Math.random() - 0.5) * 0.8;
                fish.velocity.y += (Math.random() - 0.5) * 0.4;
                fish.velocity.z += (Math.random() - 0.5) * 0.8;
                fish.velocity.normalize();
            }
        }

        // Избегание других рыбок
        for (let j = 0; j < fishArray.length; j++) {
            if (i === j) continue;
            const other = fishArray[j].mesh.position;
            const dist = p.distanceTo(other);
            if (dist < fish.avoidanceRadius && dist > 0.001) {
                tmpDir.copy(p).sub(other).normalize();
                fish.velocity.addScaledVector(tmpDir, (fish.avoidanceRadius - dist) * 0.05);
            }
        }

        // Отражение от стен (плавное)
        const m = 1.5;
        if (p.x < -hw + m) fish.velocity.x += 0.15;
        if (p.x >  hw - m) fish.velocity.x -= 0.15;
        if (p.y <  m)     fish.velocity.y += 0.15;
        if (p.y >  TANK.h - m) fish.velocity.y -= 0.15;
        if (p.z < -hd + m) fish.velocity.z += 0.15;
        if (p.z >  hd - m) fish.velocity.z -= 0.15;
        fish.velocity.normalize();

        // Движение (быстрее при кормлении)
        const spd = fish.targetFood ? fish.speed * 1.8 : fish.speed;
        p.addScaledVector(fish.velocity, spd * dt);
        p.x = THREE.MathUtils.clamp(p.x, -hw + 0.8, hw - 0.8);
        p.y = THREE.MathUtils.clamp(p.y, 0.8, TANK.h - 0.8);
        p.z = THREE.MathUtils.clamp(p.z, -hd + 0.8, hd - 0.8);

        // Поворот в направлении движения
        tmpDir.copy(fish.velocity);
        fish.mesh.lookAt(p.x + tmpDir.x, p.y + tmpDir.y, p.z + tmpDir.z);
        // Компенсация: lookAt смотрит носом (+X тела) — переворачиваем
        fish.mesh.rotateY(Math.PI);

        // Анимация хвоста и плавников
        const wag = Math.sin(t * fish.tailSpeed + fish.phase);
        fish.tail.rotation.y = wag * 0.6;
        fish.leftFin.rotation.x  =  Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.4;
        fish.rightFin.rotation.x = -Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.4;

        // Поедание корма
        if (fish.targetFood && p.distanceTo(fish.targetFood.position) < FOOD_EAT_RADIUS) {
            scene.remove(fish.targetFood);
            foodArray.splice(foodArray.indexOf(fish.targetFood), 1);
            fish.mesh.scale.multiplyScalar(1.05);   // рост на 5%
            fish.targetFood = null;
        }
    }

    controls.update();
    renderer.render(scene, camera);
}
animate();

// ============================================================
//  RESIZE
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

## ✨ Что реализовано

| Система | Детали |
|---|---|
| **🐠 Рыбки** | 15 шт., тело-сфера, глаза с зрачками, хвост (конус, анимация по Y/Z), 3 плавника, 8 цветовых схем, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание соседей (индивидуальный радиус), плавное отражение от стен, блуждание с таймером, преследование корма (радиус 15, скорость ×1.8), рост +5% за корм |
| **🌊 Окружение** | Стекло с `transmission: 0.95` + wireframe-рамка, песок с процедурным шумом вершин, 8 деформированных додекаэдров, 12 водорослей из `TubeGeometry` с покачиванием |
| **💭 Пузыри** | 30 шт., физический материал, синусоидальное покачивание, респаун у дна |
| **🍽️ Кормление** | Клик → raycast на плоскость воды → корм падает с гравитацией, удаляется при съедании или касании дна |
| **💡 Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 PointLight, кнопка переключения |
| **🎮 Камера** | OrbitControls: damping, зум 10–60, ограничение полярного угла |
| **🖥️ UI** | Glass-панели с blur, градиентный заголовок, счётчики рыбок/FPS, 3 градиентные кнопки |

Просто сохраните как `aquarium.html` и откройте в браузере! 🚀