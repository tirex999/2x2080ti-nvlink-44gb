

# 🐠 3D Аквариум с Реалистичными Рыбками

Готовое решение — один HTML-файл со всем функционалом:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐠 3D Аквариум</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #0a1e3d; }
    canvas { display: block; }

    .panel {
        position: absolute;
        background: rgba(10, 30, 60, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(100, 200, 255, 0.25);
        border-radius: 16px;
        padding: 18px 20px;
        color: #dceeff;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(50, 150, 255, 0.1) inset;
        z-index: 10;
    }

    #infoPanel { top: 20px; left: 20px; max-width: 280px; }
    #statsPanel { top: 20px; right: 20px; text-align: center; min-width: 150px; }

    h1 {
        font-size: 22px;
        margin-bottom: 12px;
        background: linear-gradient(90deg, #4fc3f7, #81d4fa, #fff176);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .instructions { font-size: 12px; line-height: 1.7; opacity: 0.85; margin-bottom: 14px; }
    .instructions b { color: #81d4fa; }

    .btn-row { display: flex; flex-direction: column; gap: 8px; }
    button {
        padding: 10px 14px;
        border: none;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        color: #fff;
        background: linear-gradient(135deg, #1976d2, #0288d1);
        transition: all 0.25s ease;
        box-shadow: 0 4px 12px rgba(2, 136, 209, 0.35);
    }
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(2, 136, 209, 0.55), 0 0 12px rgba(100, 200, 255, 0.4);
        filter: brightness(1.15);
    }
    button:active { transform: translateY(0); }

    .stat { font-size: 15px; margin: 6px 0; }
    .stat span { font-weight: bold; color: #ffd54f; font-size: 18px; }
    #fps { color: #69f0ae !important; }

    @media (max-width: 640px) {
        #infoPanel { max-width: 200px; padding: 12px; }
        .instructions { display: none; }
    }
</style>
</head>
<body>

<div class="panel" id="infoPanel">
    <h1>🐠 3D Аквариум</h1>
    <div class="instructions">
        <b>🖱 ЛКМ + движение</b> — вращение камеры<br>
        <b>🖱 ПКМ + движение</b> — панорамирование<br>
        <b>🖱 Колесо</b> — зум<br>
        <b>👆 Клик по воде</b> — бросить корм
    </div>
    <div class="btn-row">
        <button id="addFishBtn">➕ Добавить рыбку</button>
        <button id="addBubblesBtn">🫧 Больше пузырей</button>
        <button id="lightBtn">💡 Свет: ВКЛ</button>
    </div>
</div>

<div class="panel" id="statsPanel">
    <div class="stat">🐟 Рыбок: <span id="fishCount">0</span></div>
    <div class="stat">📊 FPS: <span id="fps">--</span></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ============================================================
//  ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ============================================================
const TANK = { w: 36, h: 24, d: 20 }; // размеры аквариума
let scene, camera, renderer, controls;
let clock = new THREE.Clock();
let fishArray = [];
let bubbleArray = [];
let foodArray = [];
let algaeArray = [];
let dirLight, lightOn = true;

// 8 цветовых схем: [тело, плавники]
const FISH_COLORS = [
    [0xff8c00, 0xffa726],  // оранжевая
    [0x2196f3, 0x64b5f6],  // синяя
    [0xffeb3b, 0xf44336],  // жёлто-красная
    [0x9c27b0, 0xba68c8],  // фиолетовая
    [0xe53935, 0xef9a9a],  // красная
    [0x43a047, 0x81c784],  // зелёная
    [0xec407a, 0xf48fb1],  // розовая
    [0xffc107, 0xffd54f],  // золотая
];

// ============================================================
//  СЦЕНА, КАМЕРА, РЕНДЕРЕР
// ============================================================
function initScene() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a1e3d);
    scene.fog = new THREE.FogExp2(0x0d2b52, 0.012);

    camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 200);
    camera.position.set(0, 12, 42);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(innerWidth, innerHeight);
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.target.set(0, 0, 0);

    window.addEventListener('resize', () => {
        camera.aspect = innerWidth / innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(innerWidth, innerHeight);
    });
}

// ============================================================
//  ОСВЕЩЕНИЕ
// ============================================================
function initLights() {
    scene.add(new THREE.AmbientLight(0x404040, 0.4));

    dirLight = new THREE.DirectionalLight(0xfff5e0, 1.1);
    dirLight.position.set(15, 30, 10);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(2048, 2048);
    dirLight.shadow.camera.left = -25;
    dirLight.shadow.camera.right = 25;
    dirLight.shadow.camera.top = 25;
    dirLight.shadow.camera.bottom = -25;
    scene.add(dirLight);

    const p1 = new THREE.PointLight(0x4fc3f7, 0.6, 60);
    p1.position.set(-12, 8, 6);
    scene.add(p1);

    const p2 = new THREE.PointLight(0x2979ff, 0.6, 60);
    p2.position.set(12, 6, -6);
    scene.add(p2);
}

// ============================================================
//  ОКРУЖЕНИЕ: СТЕКЛО, ДНО, КАМНИ, ВОДОРОСЛИ
// ============================================================
function buildTank() {
    // --- Стеклянный контейнер ---
    const glassGeo = new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d);
    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0xbfe8ff,
        transparent: true,
        opacity: 0.12,
        roughness: 0.05,
        metalness: 0,
        transmission: 0.95,
        thickness: 0.5,
        side: THREE.DoubleSide
    });
    const glass = new THREE.Mesh(glassGeo, glassMat);
    glass.renderOrder = 10;
    scene.add(glass);

    // Рамка (wireframe)
    const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(glassGeo),
        new THREE.LineBasicMaterial({ color: 0x80deea, transparent: true, opacity: 0.6 })
    );
    scene.add(edges);

    // --- Песчаное дно ---
    const sandGeo = new THREE.PlaneGeometry(TANK.w - 1, TANK.d - 1, 32, 24);
    const pos = sandGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        pos.setZ(i, Math.sin(pos.getX(i) * 0.8) * 0.15 + Math.cos(pos.getY(i) * 1.1) * 0.15 + Math.random() * 0.1);
    }
    sandGeo.computeVertexNormals();
    const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({ color: 0xd9b878, roughness: 1 }));
    sand.rotation.x = -Math.PI / 2;
    sand.position.y = -TANK.h / 2 + 0.2;
    sand.receiveShadow = true;
    scene.add(sand);

    // --- Декоративные камни ---
    for (let i = 0; i < 8; i++) {
        const s = 0.8 + Math.random() * 1.4;
        const rockGeo = new THREE.DodecahedronGeometry(s, 1);
        const rp = rockGeo.attributes.position;
        for (let j = 0; j < rp.count; j++) {
            rp.setXYZ(j,
                rp.getX(j) * (0.8 + Math.random() * 0.4),
                rp.getY(j) * (0.6 + Math.random() * 0.3),
                rp.getZ(j) * (0.8 + Math.random() * 0.4));
        }
        rockGeo.computeVertexNormals();
        const rock = new THREE.Mesh(rockGeo, new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 0.15, 0.25 + Math.random() * 0.15),
            roughness: 0.9
        }));
        rock.position.set(
            (Math.random() - 0.5) * (TANK.w - 6),
            -TANK.h / 2 + s * 0.35,
            (Math.random() - 0.5) * (TANK.d - 5)
        );
        rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
        rock.castShadow = rock.receiveShadow = true;
        scene.add(rock);
    }

    // --- Водоросли ---
    for (let i = 0; i < 12; i++) {
        const group = new THREE.Group();
        const strands = 2 + Math.floor(Math.random() * 3);
        const hue = 0.32 + Math.random() * 0.1;
        for (let s = 0; s < strands; s++) {
            const h = 3 + Math.random() * 5;
            const pts = [];
            for (let k = 0; k <= 6; k++) {
                pts.push(new THREE.Vector3(
                    Math.sin(k * 0.9) * 0.3,
                    (k / 6) * h,
                    Math.cos(k * 0.7) * 0.3
                ));
            }
            const curve = new THREE.CatmullRomCurve3(pts);
            const tube = new THREE.Mesh(
                new THREE.TubeGeometry(curve, 12, 0.12, 5),
                new THREE.MeshStandardMaterial({ color: new THREE.Color().setHSL(hue, 0.7, 0.35), roughness: 0.8 })
            );
            tube.position.x = (Math.random() - 0.5) * 0.6;
            tube.position.z = (Math.random() - 0.5) * 0.6;
            group.add(tube);
        }
        group.position.set(
            (Math.random() - 0.5) * (TANK.w - 6),
            -TANK.h / 2 + 0.3,
            (Math.random() - 0.5) * (TANK.d - 5)
        );
        group.userData.phase = Math.random() * Math.PI * 2;
        algaeArray.push(group);
        scene.add(group);
    }
}

// ============================================================
//  СОЗДАНИЕ РЫБКИ
// ============================================================
function createFish(position) {
    const colors = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
    const group = new THREE.Group();
    const scale = 0.6 + Math.random() * 0.6;

    const bodyMat = new THREE.MeshStandardMaterial({ color: colors[0], roughness: 0.35, metalness: 0.15 });
    const finMat = new THREE.MeshStandardMaterial({
        color: colors[1], roughness: 0.5, transparent: true, opacity: 0.8, side: THREE.DoubleSide
    });

    // Тело — вытянутая сфера
    const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), bodyMat);
    body.scale.set(1.8, 1, 0.9);
    body.castShadow = true;
    group.add(body);

    // Хвост — конус, вращаемый по Z
    const tail = new THREE.Mesh(new THREE.ConeGeometry(0.7, 1.2, 8), finMat);
    tail.rotation.z = Math.PI / 2;
    tail.position.x = -1.9;
    group.add(tail);

    // Верхний плавник
    const topFin = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1, 6), finMat);
    topFin.rotation.z = -0.4;
    topFin.position.set(0.2, 0.95, 0);
    group.add(topFin);

    // Боковые плавники
    const finGeo = new THREE.CircleGeometry(0.55, 8);
    const leftFin = new THREE.Mesh(finGeo, finMat);
    leftFin.rotation.y = Math.PI / 2;
    leftFin.position.set(0.3, -0.1, 0.85);
    leftFin.scale.set(1, 0.7, 0.4);
    group.add(leftFin);

    const rightFin = leftFin.clone();
    rightFin.position.z = -0.85;
    group.add(rightFin);

    // Глаза
    const eyeWhiteMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const pupilMat = new THREE.MeshBasicMaterial({ color: 0x111111 });
    [0.55, -0.55].forEach(z => {
        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 8), eyeWhiteMat);
        eye.position.set(1.15, 0.25, z);
        group.add(eye);
        const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 6), pupilMat);
        pupil.position.set(1.32, 0.25, z);
        group.add(pupil);
    });

    group.scale.setScalar(scale);
    if (position) group.position.copy(position);
    else {
        group.position.set(
            (Math.random() - 0.5) * (TANK.w - 8),
            (Math.random() - 0.5) * (TANK.h - 8),
            (Math.random() - 0.5) * (TANK.d - 8)
        );
    }
    scene.add(group);

    const angle = Math.random() * Math.PI * 2;
    fishArray.push({
        mesh: group,
        tail, leftFin, rightFin,
        velocity: new THREE.Vector3(Math.cos(angle), 0, Math.sin(angle)),
        speed: 4 + Math.random() * 3,
        tailSpeed: 6 + Math.random() * 4,
        phase: Math.random() * Math.PI * 2,
        targetFood: null,
        avoidanceRadius: 2.5 + Math.random() * 1.5,
        wanderTimer: Math.random() * 3
    });

    updateStats();
}

// ============================================================
//  БУБРЕШКИ
// ============================================================
function createBubble(x, y, z) {
    const geo = new THREE.SphereGeometry(0.12 + Math.random() * 0.2, 8, 8);
    const mat = new THREE.MeshPhysicalMaterial({
        color: 0xcfeaff, transparent: true, opacity: 0.35,
        roughness: 0, transmission: 0.8, metalness: 0
    });
    const b = new THREE.Mesh(geo, mat);
    b.position.set(
        x !== undefined ? x : (Math.random() - 0.5) * (TANK.w - 4),
        y !== undefined ? y : -TANK.h / 2 + 1,
        z !== undefined ? z : (Math.random() - 0.5) * (TANK.d - 4)
    );
    b.userData = {
        speed: 1.5 + Math.random() * 2,
        phase: Math.random() * Math.PI * 2,
        baseX: b.position.x,
        baseZ: b.position.z
    };
    scene.add(b);
    bubbleArray.push(b);
}

// ============================================================
//  СИСТЕМА КОРМЛЕНИЯ
// ============================================================
const raycaster = new THREE.Raycaster();
const feedPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);

renderer_click_handler_setup();
function renderer_click_handler_setup() {
    let downPos = null;
    renderer && document.addEventListener('pointerdown', e => downPos = { x: e.clientX, y: e.clientY });
    document.addEventListener('pointerup', e => {
        if (!downPos || e.button !== 0) return;
        const dx = e.clientX - downPos.x, dy = e.clientY - downPos.y;
        if (dx * dx + dy * dy > 25) return; // это было вращение, не клик

        const mouse = new THREE.Vector2(
            (e.clientX / innerWidth) * 2 - 1,
            -(e.clientY / innerHeight) * 2 + 1
        );
        raycaster.setFromCamera(mouse, camera);
        const point = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(feedPlane, point)) {
            // Ограничиваем точку внутри аквариума
            point.x = THREE.MathUtils.clamp(point.x, -TANK.w/2 + 2, TANK.w/2 - 2);
            point.z = THREE.MathUtils.clamp(point.z, -TANK.d/2 + 2, TANK.d/2 - 2);
            spawnFood(point);
        }
    });
}

function spawnFood(pos) {
    for (let i = 0; i < 5; i++) {
        const pellet = new THREE.Mesh(
            new THREE.SphereGeometry(0.15, 8, 6),
            new THREE.MeshStandardMaterial({ color: 0x8d6e63, roughness: 0.9 })
        );
        pellet.position.set(
            pos.x + (Math.random() - 0.5) * 1.5,
            Math.min(pos.y + 2, TANK.h/2 - 1),
            pos.z + (Math.random() - 0.5) * 1.5
        );
        pellet.userData = { vel: new THREE.Vector3((Math.random()-0.5)*0.5, -1, (Math.random()-0.5)*0.5) };
        scene.add(pellet);
        foodArray.push(pellet);
    }
}

// ============================================================
//  ИИ РЫБОК
// ============================================================
function updateFish(dt, t) {
    const halfW = TANK.w/2 - 2, halfH = TANK.h/2 - 2, halfD = TANK.d/2 - 2;

    for (const fish of fishArray) {
        const m = fish.mesh;
        const v = fish.velocity;

        // --- Поиск корма ---
        if (!fish.targetFood || !foodArray.includes(fish.targetFood)) {
            fish.targetFood = null;
            for (const f of foodArray) {
                if (f.position.distanceTo(m.position) < 15) { fish.targetFood = f; break; }
            }
        }
        if (fish.targetFood) {
            const dir = fish.targetFood.position.clone().sub(m.position).normalize();
            v.lerp(dir.multiplyScalar(fish.speed * 1.5), dt * 2);
            // Съедание
            if (m.position.distanceTo(fish.targetFood.position) < 1.2 * m.scale.x) {
                scene.remove(fish.targetFood);
                fish.targetFood.geometry.dispose();
                fish.targetFood.material.dispose();
                foodArray.splice(foodArray.indexOf(fish.targetFood), 1);
                fish.targetFood = null;
                m.scale.multiplyScalar(1.05); // рост на 5%
            }
        } else {
            // --- Случайное блуждание ---
            fish.wanderTimer -= dt;
            if (fish.wanderTimer <= 0) {
                v.x += (Math.random() - 0.5) * 2;
                v.y += (Math.random() - 0.5) * 1;
                v.z += (Math.random() - 0.5) * 2;
                fish.wanderTimer = 1.5 + Math.random() * 3;
            }
            v.setLength(THREE.MathUtils.lerp(v.length(), fish.speed, dt));
        }

        // --- Избегание других рыбок ---
        for (const other of fishArray) {
            if (other === fish) continue;
            const dist = m.position.distanceTo(other.mesh.position);
            const minDist = fish.avoidanceRadius + other.mesh.scale.x;
            if (dist < minDist && dist > 0.001) {
                const push = m.position.clone().sub(other.mesh.position).normalize()
                    .multiplyScalar((minDist - dist) * 3);
                v.add(push.multiplyScalar(dt));
            }
        }

        // --- Отражение от стен (плавное) ---
        const wallForce = 4;
        if (m.position.x >  halfW) v.x -= wallForce * dt;
        if (m.position.x < -halfW) v.x += wallForce * dt;
        if (m.position.y >  halfH) v.y -= wallForce * dt;
        if (m.position.y < -halfH) v.y += wallForce * dt;
        if (m.position.z >  halfD) v.z -= wallForce * dt;
        if (m.position.z < -halfD) v.z += wallForce * dt;

        // Жёсткий кламп
        m.position.x = THREE.MathUtils.clamp(m.position.x, -halfW, halfW);
        m.position.y = THREE.MathUtils.clamp(m.position.y, -halfH, halfH);
        m.position.z = THREE.MathUtils.clamp(m.position.z, -halfD, halfD);

        // --- Движение ---
        m.position.addScaledVector(v, dt);

        // Поворот в направлении движения
        if (v.lengthSq() > 0.01) {
            const targetQuat = new THREE.Quaternion();
            const lookAt = new THREE.Matrix4().lookAt(m.position, m.position.clone().add(v), new THREE.Vector3(0, 1, 0));
            targetQuat.setFromRotationMatrix(lookAt);
            targetQuat.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), Math.PI / 2));
            m.quaternion.slerp(targetQuat, Math.min(1, dt * 4));
        }

        // --- Анимация хвоста и плавников ---
        const tailAmp = 0.5;
        fish.tail.rotation.y = Math.sin(t * fish.tailSpeed + fish.phase) * tailAmp;
        fish.leftFin.rotation.x = Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.4;
        fish.rightFin.rotation.x = -Math.sin(t * fish.tailSpeed * 0.7 + fish.phase) * 0.4;
        // Лёгкое покачивание тела
        m.rotation.z += Math.sin(t * 2 + fish.phase) * 0.002;
    }
}

// ============================================================
//  ОБНОВЛЕНИЕ БУБРЕШЕК И КОРМА
// ============================================================
function updateBubbles(dt, t) {
    for (let i = bubbleArray.length - 1; i >= 0; i--) {
        const b = bubbleArray[i];
        const u = b.userData;
        b.position.y += u.speed * dt;
        b.position.x = u.baseX + Math.sin(t * 1.5 + u.phase) * 0.4;
        b.position.z = u.baseZ + Math.cos(t * 1.2 + u.phase) * 0.4;
        if (b.position.y > TANK.h / 2 - 0.5) {
            // Сброс вниз
            b.position.y = -TANK.h / 2 + 0.5;
            u.baseX = (Math.random() - 0.5) * (TANK.w - 4);
            u.baseZ = (Math.random() - 0.5) * (TANK.d - 4);
            b.position.x = u.baseX;
            b.position.z = u.baseZ;
        }
    }
}

function updateFood(dt) {
    for (let i = foodArray.length - 1; i >= 0; i--) {
        const f = foodArray[i];
        f.userData.vel.y -= 2.5 * dt; // гравитация
        f.position.addScaledVector(f.userData.vel, dt);
        if (f.position.y < -TANK.h / 2 + 0.4) {
            scene.remove(f);
            f.geometry.dispose();
            f.material.dispose();
            foodArray.splice(i, 1);
        }
    }
}

// ============================================================
//  UI
// ============================================================
function updateStats() {
    document.getElementById('fishCount').textContent = fishArray.length;
}

document.getElementById('addFishBtn').onclick = () => createFish();
document.getElementById('addBubblesBtn').onclick = () => {
    for (let i = 0; i < 10; i++) createBubble();
};
document.getElementById('lightBtn').onclick = function () {
    lightOn = !lightOn;
    dirLight.intensity = lightOn ? 1.1 : 0.15;
    this.textContent = lightOn ? '💡 Свет: ВКЛ' : '💡 Свет: ВЫКЛ';
};

// FPS
let frames = 0, fpsTime = 0;
function updateFPS(dt) {
    frames++;
    fpsTime += dt;
    if (fpsTime >= 0.5) {
        document.getElementById('fps').textContent = Math.round(frames / fpsTime);
        frames = 0; fpsTime = 0;
    }
}

// ============================================================
//  ГЛАВНЫЙ ЦИКЛ
// ============================================================
function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    updateFish(dt, t);
    updateBubbles(dt, t);
    updateFood(dt);

    // Покачивание водорослей
    for (const a of algaeArray) {
        a.rotation.x = Math.sin(t * 0.8 + a.userData.phase) * 0.08;
        a.rotation.z = Math.cos(t * 0.6 + a.userData.phase) * 0.08;
    }

    controls.update();
    updateFPS(dt);
    renderer.render(scene, camera);
}

// ============================================================
//  ЗАПУСК
// ============================================================
initScene();
initLights();
buildTank();
for (let i = 0; i < 15; i++) createFish();
for (let i = 0; i < 30; i++) createBubble();
updateStats();
animate();
</script>
</body>
</html>
```

## ✨ Что реализовано

| Система | Детали |
|---|---|
| **🐠 Рыбки** | 15 шт., тело/хвост/3 плавника/глаза с зрачками, 8 цветовых схем, масштаб 0.6–1.2 |
| **🧠 ИИ** | Избегание столкновений, плавное отражение от стен, блуждание, преследование корма (радиус 15), рост +5% |
| **🌊 Окружение** | Стекло с `transmission: 0.95`, wireframe-рамка, процедурный песок, 8 камней, 12 водорослей (TubeGeometry) |
| **💭 Пузыри** | 30 шт., синусоидальное покачивание, сброс на поверхности |
| **🍽️ Кормление** | Клик → 5 гранул с гравитацией, съедание → рост, удаление у дна |
| **💡 Свет** | Ambient + Directional (тени 2048², PCFSoft) + 2 PointLight, переключаемый |
| **🎮 Камера** | OrbitControls: вращение, панорама, зум 10–60, damping, ограничение угла |
| **🖥️ UI** | Glass-панели, статистика, FPS, 3 кнопки с hover-эффектами |

## 💡 Возможные улучшения
- **WebAudio**: бульканье и звуки кормления
- **Подсветка рыбок** при приближении курсора (raycast на каждую рыбку)
- **Сохранение состояния** в localStorage (размеры/цвета рыбок)
- **Генерация корма из разных точек** (поверхность воды vs. центр)

Просто сохраните код как `aquarium.html` и откройте в браузере! 🚀