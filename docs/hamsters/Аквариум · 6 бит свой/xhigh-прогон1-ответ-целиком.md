

Готово — полный самодостаточный файл `index.html`. Сохраните и откройте в браузере (нужен интернет для CDN Three.js и шрифтов).

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="color-scheme" content="dark" />
<title>3D Аквариум — интерактивная симуляция</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🐠</text></svg>" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Unbounded:wght@500;700;900&display=swap" rel="stylesheet" />
<style>
  :root{ --ink:#dceefb; --muted:#7fb2d6; --line:rgba(120,205,255,.22); }
  *{ box-sizing:border-box; }
  html,body{ height:100%; }
  body{
    margin:0; overflow:hidden; background:#041226;
    font-family:'Manrope', system-ui, sans-serif; color:var(--ink);
  }
  canvas{ display:block; cursor:crosshair; }

  /* мягкая виньетка поверх сцены */
  #vignette{
    position:fixed; inset:0; z-index:4; pointer-events:none;
    background:radial-gradient(120% 95% at 50% 42%, transparent 52%, rgba(2,8,20,.55) 100%);
  }

  #hud{ position:fixed; inset:0; z-index:10; pointer-events:none; }
  .panel{
    position:absolute; pointer-events:auto;
    background:rgba(5,19,38,.55);
    -webkit-backdrop-filter:blur(14px); backdrop-filter:blur(14px);
    border:1px solid var(--line); border-radius:16px;
    box-shadow:0 14px 44px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.07);
  }
  .panel::before{
    content:''; position:absolute; top:-1px; left:18px; right:18px; height:1px;
    background:linear-gradient(90deg, transparent, rgba(150,225,255,.65), transparent);
  }

  /* ---- информационная панель ---- */
  .info{
    top:18px; left:18px; width:min(292px, calc(100vw - 36px));
    padding:18px 18px 16px;
    animation:slideL .8s cubic-bezier(.22,1,.36,1) .15s both;
  }
  .info header{ display:flex; flex-direction:column; gap:6px; }
  h1{
    margin:0; font-family:'Unbounded', sans-serif; font-weight:900;
    font-size:clamp(16px, 2.1vw, 21px); letter-spacing:.02em;
    background:linear-gradient(94deg, #9df2ff 5%, #4db4ff 55%, #ff9d6b 118%);
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .tag{
    margin:0; display:flex; align-items:center; gap:8px;
    font-size:10.5px; font-weight:700; letter-spacing:.16em;
    text-transform:uppercase; color:var(--muted);
  }
  .live{
    width:7px; height:7px; border-radius:50%; background:#5cff9d;
    box-shadow:0 0 10px #5cff9d; animation:blink 1.8s ease-in-out infinite;
  }
  .controls{
    list-style:none; margin:14px 0 15px; padding:14px 0 0;
    border-top:1px solid rgba(120,205,255,.14); display:grid; gap:8px;
  }
  .controls li{ display:flex; align-items:center; gap:10px; font-size:12.5px; font-weight:600; color:#a9cfe8; }
  .key{
    flex:0 0 auto; min-width:60px; text-align:center; padding:4px 8px; border-radius:7px;
    font-size:10px; font-weight:800; letter-spacing:.1em; color:#d9f2ff;
    background:rgba(120,200,255,.1); border:1px solid rgba(120,200,255,.28);
  }
  .btn-row{ display:flex; gap:8px; flex-wrap:wrap; }

  .btn{
    appearance:none; border:1px solid rgba(150,225,255,.4); border-radius:11px;
    padding:10px 13px; font:800 12.5px/1 'Manrope', sans-serif; letter-spacing:.02em;
    color:#032238; cursor:pointer;
    background:linear-gradient(165deg, #7deaff 0%, #2f9ee8 100%);
    box-shadow:0 5px 18px rgba(40,160,235,.35), inset 0 1px 0 rgba(255,255,255,.55);
    transition:transform .16s ease, box-shadow .2s ease, filter .16s ease, background .2s ease;
  }
  .btn:hover{ transform:translateY(-2px); filter:brightness(1.07);
    box-shadow:0 10px 26px rgba(95,224,255,.45), inset 0 1px 0 rgba(255,255,255,.55); }
  .btn:active{ transform:translateY(0) scale(.94); }
  .btn:focus-visible{ outline:2px solid #9df2ff; outline-offset:2px; }
  .btn:disabled{ opacity:.4; cursor:not-allowed; transform:none; filter:none; }
  .btn.ghost{
    background:rgba(12,38,66,.55); color:#bfe6ff; border-color:rgba(120,205,255,.3);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.06);
  }
  .btn.ghost:hover{ background:rgba(24,60,98,.65); box-shadow:0 8px 22px rgba(95,224,255,.18); }
  .btn.off{ background:rgba(8,16,32,.75); color:#8fd4ff; border-color:rgba(120,200,255,.45); }

  /* ---- статистика ---- */
  .stats{ top:18px; right:18px; display:flex; padding:12px 6px;
    animation:slideR .8s cubic-bezier(.22,1,.36,1) .3s both; }
  .stat{ padding:2px 16px; display:flex; flex-direction:column; gap:4px; text-align:center; }
  .stat + .stat{ border-left:1px solid rgba(120,205,255,.14); }
  .value{ display:block; font-family:'Unbounded', sans-serif; font-weight:700;
    font-size:21px; line-height:1; color:#eef9ff; }
  .value.pop{ animation:pop .45s cubic-bezier(.3,1.5,.5,1); }
  .label{ font-size:9.5px; font-weight:800; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); }
  .pulse{ display:inline-block; width:6px; height:6px; border-radius:50%; margin-left:5px;
    background:#5cff9d; box-shadow:0 0 8px #5cff9d; animation:blink 1.4s ease-in-out infinite; }

  /* ---- подсказка ---- */
  .hint{
    position:absolute; bottom:24px; left:50%; transform:translateX(-50%);
    background:rgba(6,22,44,.6); -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px);
    border:1px solid rgba(120,205,255,.25); border-radius:999px;
    padding:10px 20px; font-size:13px; font-weight:700; color:#cfeaff; white-space:nowrap;
    box-shadow:0 10px 30px rgba(0,0,0,.35);
    transition:opacity .6s ease, transform .6s ease;
    animation:riseIn .7s cubic-bezier(.22,1,.36,1) 1s both, bob 2.8s ease-in-out 2s infinite;
  }
  .hint.hide{ animation:none; opacity:0; transform:translateX(-50%) translateY(16px); pointer-events:none; }

  #err{
    position:fixed; inset:0; z-index:50; display:none; align-items:center; justify-content:center;
    background:rgba(3,10,22,.85); font-size:15px; text-align:center; padding:24px; line-height:1.6;
  }

  @keyframes slideL{ from{ opacity:0; transform:translateX(-26px);} to{ opacity:1; transform:none;} }
  @keyframes slideR{ from{ opacity:0; transform:translateX(26px);} to{ opacity:1; transform:none;} }
  @keyframes riseIn{ from{ opacity:0; transform:translateX(-50%) translateY(18px);} to{ opacity:1; transform:translateX(-50%) translateY(0);} }
  @keyframes bob{ 50%{ transform:translateX(-50%) translateY(-7px);} }
  @keyframes blink{ 50%{ opacity:.3; } }
  @keyframes pop{ 35%{ transform:scale(1.35); color:#7de8ff; } }

  @media (max-width:640px){
    .info{ top:12px; left:12px; width:calc(100vw - 24px); padding:14px; }
    .controls li:nth-child(-n+3){ display:none; }
    .stats{ top:12px; right:12px; padding:8px 2px; }
    .stat{ padding:2px 10px; }
    .value{ font-size:16px; }
    .hint{ bottom:14px; font-size:12px; padding:9px 16px; }
  }
  @media (prefers-reduced-motion:reduce){
    *, *::before, *::after{ animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; }
  }
</style>
</head>
<body>
  <div id="vignette"></div>

  <div id="hud">
    <aside class="panel info">
      <header>
        <h1>3D Аквариум</h1>
        <p class="tag"><i class="live"></i> живая сцена · three.js</p>
      </header>
      <ul class="controls">
        <li><span class="key">ЛКМ</span> вращение камеры</li>
        <li><span class="key">ПКМ</span> панорамирование</li>
        <li><span class="key">КОЛЕСО</span> зум</li>
        <li><span class="key">КЛИК</span> бросить корм</li>
      </ul>
      <div class="btn-row">
        <button class="btn" id="btnFish">+ Рыбка</button>
        <button class="btn ghost" id="btnBubbles">Пузыри +10</button>
        <button class="btn ghost" id="btnLight">💡 Свет</button>
      </div>
    </aside>

    <aside class="panel stats">
      <div class="stat"><span class="value" id="stFish">0</span><span class="label">Рыбки</span></div>
      <div class="stat"><span class="value" id="stFood">0</span><span class="label">Корм</span></div>
      <div class="stat"><span class="value" id="stFps">—</span><span class="label">FPS<i class="pulse" id="fpsDot"></i></span></div>
    </aside>

    <div class="hint" id="hint">🍤 Кликните по воде — рыбки придут на корм</div>
  </div>

  <div id="err">⚠️ Не удалось загрузить Three.js из CDN.<br>Проверьте интернет-соединение и обновите страницу.</div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script>
  (function(){
    'use strict';
    if (!window.THREE || !THREE.OrbitControls){
      document.getElementById('err').style.display = 'flex';
      return;
    }

    /* ================= утилиты ================= */
    const rand  = (a, b) => a + Math.random() * (b - a);
    const clamp = THREE.MathUtils.clamp;

    const stFish = document.getElementById('stFish');
    const stFood = document.getElementById('stFood');
    const stFps  = document.getElementById('stFps');
    const fpsDot = document.getElementById('fpsDot');
    const hintEl = document.getElementById('hint');
    const btnFish    = document.getElementById('btnFish');
    const btnBubbles = document.getElementById('btnBubbles');
    const btnLight   = document.getElementById('btnLight');

    function popValue(el){ el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); }

    /* ================= рендерер / сцена / камера ================= */
    const renderer = new THREE.WebGLRenderer({ antialias:true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    document.body.appendChild(renderer.domElement);

    const scene = new THREE.Scene();

    // градиентный фон: тёмно-синий -> синий
    (function(){
      const c = document.createElement('canvas'); c.width = 2; c.height = 512;
      const ctx = c.getContext('2d');
      const g = ctx.createLinearGradient(0, 0, 0, 512);
      g.addColorStop(0, '#0e4180');
      g.addColorStop(0.55, '#07294f');
      g.addColorStop(1, '#020c1c');
      ctx.fillStyle = g; ctx.fillRect(0, 0, 2, 512);
      scene.background = new THREE.CanvasTexture(c);
    })();
    scene.fog = new THREE.FogExp2(0x08284e, 0.011);

    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 300);
    const CAM_A = new THREE.Vector3(46, 30, 54);   // старт интро
    const CAM_B = new THREE.Vector3(26, 18, 32);   // рабочая позиция
    camera.position.copy(CAM_A);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 11, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 10;
    controls.maxDistance = 60;
    controls.maxPolarAngle = Math.PI / 1.8;
    controls.enabled = false; // включится после интро-подлёта

    /* ================= свет ================= */
    const ambLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambLight);

    const dirLight = new THREE.DirectionalLight(0xfff3e0, 1.15);
    dirLight.position.set(18, 38, 12);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(2048, 2048);
    dirLight.shadow.camera.left = -26; dirLight.shadow.camera.right = 26;
    dirLight.shadow.camera.top  =  26; dirLight.shadow.camera.bottom = -26;
    dirLight.shadow.camera.near = 1;   dirLight.shadow.camera.far = 100;
    dirLight.shadow.bias = -0.0005;
    dirLight.target.position.set(0, 10, 0);
    scene.add(dirLight, dirLight.target);

    const pl1 = new THREE.PointLight(0x33bbff, 0.55, 70);
    pl1.position.set(-11, 7, -6);
    const pl2 = new THREE.PointLight(0x1188ff, 0.5, 70);
    pl2.position.set(12, 15, 7);
    scene.add(pl1, pl2);

    /* ================= аквариум ================= */
    const TANK = { w:36, h:24, d:20 };
    const BOUNDS = { x:16.8, z:8.8, yMin:1.6, yMax:22.2 };

    // стеклянная коробка с преломлением + рамка
    const glass = new THREE.Mesh(
      new THREE.BoxGeometry(TANK.w, TANK.h, TANK.d),
      new THREE.MeshPhysicalMaterial({
        color:0x9fd4ff, metalness:0, roughness:0.06,
        transmission:0.95, transparent:true, opacity:0.14,
        clearcoat:1, clearcoatRoughness:0.1, depthWrite:false
      })
    );
    glass.position.y = TANK.h / 2;
    scene.add(glass);

    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(glass.geometry),
      new THREE.LineBasicMaterial({ color:0x9fd8ff, transparent:true, opacity:0.45 })
    );
    edges.position.copy(glass.position);
    scene.add(edges);

    // плёнка на поверхности воды
    const surface = new THREE.Mesh(
      new THREE.PlaneGeometry(TANK.w - 0.4, TANK.d - 0.4),
      new THREE.MeshBasicMaterial({ color:0xbfe9ff, transparent:true, opacity:0.07, side:THREE.DoubleSide, depthWrite:false })
    );
    surface.rotation.x = -Math.PI / 2;
    surface.position.y = TANK.h - 0.15;
    scene.add(surface);

    // песчаное дно с процедурными неровностями
    (function(){
      const geo = new THREE.PlaneGeometry(TANK.w - 0.5, TANK.d - 0.5, 48, 32);
      geo.rotateX(-Math.PI / 2);
      const p = geo.attributes.position;
      for (let i = 0; i < p.count; i++){
        const x = p.getX(i), z = p.getZ(i);
        p.setY(i, (Math.sin(x*0.55)*Math.cos(z*0.7) + 0.4*Math.sin(x*1.7+1.3) + 0.3*Math.cos(z*1.9+0.5)) * 0.22);
      }
      geo.computeVertexNormals();
      const sand = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color:0xd9c28f, roughness:1 }));
      sand.position.y = 0.3;
      sand.receiveShadow = true;
      scene.add(sand);
    })();

    // камни: деформированные додекаэдры (детерминированная деформация — без трещин)
    (function(){
      const cols = [0x6d7684, 0x7a7268, 0x5f6b78, 0x837a6e];
      const v = new THREE.Vector3();
      for (let i = 0; i < 8; i++){
        const r = 0.9 + Math.random() * 1.2;
        const seed = Math.random() * 10;
        const geo = new THREE.DodecahedronGeometry(r, 0);
        const p = geo.attributes.position;
        for (let j = 0; j < p.count; j++){
          v.fromBufferAttribute(p, j).normalize();
          const s = 1 + 0.26*Math.sin(v.x*4.3+seed) + 0.2*Math.cos(v.y*5.1+seed*1.7) + 0.16*Math.sin(v.z*3.9+seed*2.3);
          p.setXYZ(j, v.x*r*s, v.y*r*s, v.z*r*s);
        }
        geo.computeVertexNormals();
        const rock = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color:cols[i%4], roughness:0.95, flatShading:true }));
        rock.position.set(rand(-14,14), 0.5 + r*0.3, rand(-7,7));
        rock.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, Math.random()*Math.PI);
        rock.castShadow = rock.receiveShadow = true;
        scene.add(rock);
      }
    })();

    // водоросли: TubeGeometry по CatmullRomCurve3, покачивание от основания
    const seaweed = [];
    (function(){
      const cols = [0x1f9d55, 0x2fbf6b, 0x157a45, 0x3ad07f, 0x0f8f5f];
      for (let i = 0; i < 12; i++){
        const gx = rand(-14.5, 14.5), gz = rand(-7.5, 7.5);
        const blades = 1 + Math.floor(Math.random() * 3);
        for (let b = 0; b < blades; b++){
          const h = 2.6 + Math.random() * 3.6;
          const pts = [];
          for (let k = 0; k <= 5; k++){
            const t = k / 5;
            pts.push(new THREE.Vector3(
              Math.sin(t*2.6 + i*1.7 + b) * 0.35 * t,
              h * t,
              Math.cos(t*2.2 + i*1.1 + b*2) * 0.35 * t
            ));
          }
          const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 12, 0.09 + Math.random()*0.09, 5, false);
          const grp = new THREE.Group();
          grp.position.set(gx + rand(-0.5, 0.5), 0.35, gz + rand(-0.5, 0.5));
          const blade = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            color:cols[(i+b) % cols.length], roughness:0.85, side:THREE.DoubleSide,
            emissive:0x062a18, emissiveIntensity:0.35
          }));
          blade.castShadow = true;
          grp.add(blade);
          scene.add(grp);
          seaweed.push({ mesh:grp, phase:Math.random()*6.28, speed:0.5 + Math.random()*0.9 });
        }
      }
    })();

    /* ================= пузыри ================= */
    const bubbles = [];
    const bubbleGeo = new THREE.SphereGeometry(1, 10, 8);
    const bubbleMat = new THREE.MeshPhysicalMaterial({
      color:0xcfeeff, transparent:true, opacity:0.3, roughness:0.05,
      metalness:0, clearcoat:1, depthWrite:false
    });
    function spawnBubble(x, y, z, r){
      if (bubbles.length > 110) scene.remove(bubbles.shift().mesh);
      const m = new THREE.Mesh(bubbleGeo, bubbleMat);
      m.scale.setScalar(r);
      scene.add(m);
      bubbles.push({
        mesh:m, x0:x, z0:z, y:y,
        speed:1.2 + Math.random()*1.6,
        sway:0.8 + Math.random()*1.2,
        amp:0.25 + Math.random()*0.5,
        phase:Math.random()*6.28
      });
    }
    for (let i = 0; i < 30; i++) spawnBubble(rand(-15,15), rand(1,22), rand(-7.5,7.5), 0.12 + Math.random()*0.28);

    function updateBubbles(dt, t){
      for (const b of bubbles){
        b.y += b.speed * dt;
        if (b.y > 22.8){ b.y = 0.8; b.x0 = rand(-15,15); b.z0 = rand(-7.5,7.5); }
        b.mesh.position.set(
          b.x0 + Math.sin(t*b.sway + b.phase) * b.amp,
          b.y,
          b.z0 + Math.cos(t*b.sway*0.85 + b.phase) * b.amp
        );
      }
    }

    /* ================= рыбки ================= */
    const fishArray = [];
    const FISH_PALETTES = [
      { body:0xff8c2e, fin:0xffc06a }, // оранжевая
      { body:0x2f7bff, fin:0x8fc1ff }, // синяя
      { body:0xffd23e, fin:0xff5a3c }, // жёлто-красная
      { body:0xa05cff, fin:0xd3b0ff }, // фиолетовая
      { body:0xff4444, fin:0xff9d9d }, // красная
      { body:0x35d97b, fin:0xa4ffce }, // зелёная
      { body:0xff7ec2, fin:0xffc9e6 }, // розовая
      { body:0xffc93c, fin:0xffe9a8 }  // золотая
    ];
    const FWD = new THREE.Vector3(1, 0, 0); // рыбка смотрит вдоль +X
    const _v = new THREE.Vector3();
    const _q = new THREE.Quaternion();

    function createFish(){
      const pal = FISH_PALETTES[Math.floor(Math.random() * FISH_PALETTES.length)];
      const g = new THREE.Group();

      const bodyMat = new THREE.MeshStandardMaterial({ color:pal.body, roughness:0.35, metalness:0.2, emissive:pal.body, emissiveIntensity:0.08 });
      const finMat  = new THREE.MeshStandardMaterial({ color:pal.fin, roughness:0.55, metalness:0.05, transparent:true, opacity:0.88, side:THREE.DoubleSide, emissive:pal.fin, emissiveIntensity:0.06 });

      // вытянутое тело
      const body = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), bodyMat);
      body.scale.set(1.5, 0.9, 0.72);
      body.castShadow = true;
      g.add(body);

      // хвост на шарнире
      const tail = new THREE.Group();
      tail.position.set(-1.35, 0, 0);
      const tailMesh = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), finMat);
      tailMesh.scale.set(0.42, 0.75, 0.09);
      tailMesh.position.set(-0.5, 0, 0);
      tail.add(tailMesh);
      g.add(tail);

      // спинной плавник
      const dorsal = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 6), finMat);
      dorsal.scale.set(0.55, 0.42, 0.06);
      dorsal.position.set(-0.2, 0.82, 0);
      dorsal.rotation.z = -0.25;
      g.add(dorsal);

      // анальный плавник
      const anal = new THREE.Mesh(new THREE.SphereGeometry(1, 8, 5), finMat);
      anal.scale.set(0.3, 0.22, 0.05);
      anal.position.set(-0.55, -0.62, 0);
      g.add(anal);

      // грудные плавники
      const mkFin = (side) => {
        const fin = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 6), finMat);
        fin.scale.set(0.34, 0.06, 0.45);
        fin.position.set(0.42, -0.12, side * 0.55);
        fin.rotation.y = -side * 0.65;
        g.add(fin);
        return fin;
      };
      const leftFin = mkFin(1);
      const rightFin = mkFin(-1);

      // глаза с зрачками
      const eyeMat = new THREE.MeshStandardMaterial({ color:0xf5f9ff, roughness:0.25 });
      const pupMat = new THREE.MeshStandardMaterial({ color:0x0a0d12, roughness:0.3 });
      for (const s of [1, -1]){
        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 8), eyeMat);
        eye.position.set(0.98, 0.26, s * 0.42);
        g.add(eye);
        const pup = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 6), pupMat);
        pup.position.set(1.1, 0.26, s * 0.47);
        g.add(pup);
      }

      const scale = 0.6 + Math.random() * 0.6;
      g.scale.setScalar(scale);
      g.position.set(rand(-13,13), rand(4,19), rand(-6.5,6.5));
      scene.add(g);

      const f = {
        mesh:g, body, tail, leftFin, rightFin, dorsal,
        velocity:new THREE.Vector3(rand(-1,1), rand(-0.4,0.4), rand(-1,1)).normalize().multiplyScalar(3),
        wander:new THREE.Vector3(1, 0, 0),
        wanderT:Math.random() * 2,
        speed:2.6 + Math.random() * 2.4,
        tailSpeed:5 + Math.random() * 5,
        phase:Math.random() * Math.PI * 2,
        targetFood:null,
        avoidanceRadius:2.2 + Math.random() * 1.6,
        scale
      };
      fishArray.push(f);
      stFish.textContent = fishArray.length;
      popValue(stFish);
      btnFish.disabled = fishArray.length >= 40;
      return f;
    }

    for (let i = 0; i < 15; i++) createFish();

    /* ================= корм ================= */
    const foodArray = [];
    const foodGeo = new THREE.SphereGeometry(0.3, 10, 8);
    const foodMat = new THREE.MeshStandardMaterial({ color:0xe09a4a, roughness:0.7, emissive:0x8a4a10, emissiveIntensity:0.25 });

    let fedOnce = false;
    function hideHint(){ if (!fedOnce){ fedOnce = true; hintEl.classList.add('hide'); } }

    function spawnFood(pt){
      if (foodArray.length >= 25) return;
      const m = new THREE.Mesh(foodGeo, foodMat);
      m.position.copy(pt);
      m.castShadow = true;
      scene.add(m);
      foodArray.push({ mesh:m, vy:-0.5, vx:rand(-0.3,0.3), vz:rand(-0.3,0.3), phase:Math.random()*6.28 });
      ping(pt);
      stFood.textContent = foodArray.length;
      popValue(stFood);
      hideHint();
    }
    function removeFood(fd){
      const i = foodArray.indexOf(fd);
      if (i !== -1){ foodArray.splice(i, 1); scene.remove(fd.mesh); }
      stFood.textContent = foodArray.length;
    }
    function updateFood(dt, t){
      for (let i = foodArray.length - 1; i >= 0; i--){
        const fd = foodArray[i];
        fd.vy = Math.max(fd.vy - 4.5 * dt, -4); // гравитация + сопротивление воды
        const p = fd.mesh.position;
        p.y += fd.vy * dt;
        p.x += (fd.vx + Math.sin(t*2   + fd.phase) * 0.4) * dt;
        p.z += (fd.vz + Math.cos(t*1.7 + fd.phase) * 0.4) * dt;
        p.x = clamp(p.x, -16.5, 16.5);
        p.z = clamp(p.z, -8.5, 8.5);
        fd.mesh.rotation.x += dt;
        if (p.y < 0.9) removeFood(fd); // упало на дно — исчезает
      }
    }
    function eat(f, fd){
      f.scale = Math.min(f.scale * 1.05, 2.6); // рост на 5%
      f.mesh.scale.setScalar(f.scale);
      const p = fd.mesh.position;
      for (let k = 0; k < 3; k++)
        spawnBubble(p.x + rand(-0.3,0.3), p.y, p.z + rand(-0.3,0.3), 0.1 + Math.random()*0.1);
      removeFood(fd);
    }

    /* ================= ИИ рыбок ================= */
    function updateFish(f, dt, t){
      const p = f.mesh.position, v = f.velocity;

      // случайное блуждание: периодическая смена курса
      f.wanderT -= dt;
      if (f.wanderT <= 0){
        f.wanderT = 1.2 + Math.random() * 2.6;
        f.wander.set(rand(-1,1), rand(-0.6,0.6), rand(-1,1)).normalize();
      }
      v.addScaledVector(f.wander, 2.0 * dt);

      // избегание столкновений
      for (let i = 0; i < fishArray.length; i++){
        const o = fishArray[i];
        if (o === f) continue;
        _v.subVectors(p, o.mesh.position);
        const d = _v.length();
        const r = f.avoidanceRadius * (0.6 + 0.4 * o.scale);
        if (d < r && d > 1e-4)
          v.addScaledVector(_v.divideScalar(d), (1 - d / r) * 7 * dt);
      }

      // поиск корма в радиусе 15
      let best = null, bd = 15;
      for (let i = 0; i < foodArray.length; i++){
        const d = p.distanceTo(foodArray[i].mesh.position);
        if (d < bd){ bd = d; best = foodArray[i]; }
      }
      f.targetFood = best;
      if (best){
        _v.subVectors(best.mesh.position, p).normalize();
        v.addScaledVector(_v, 6.5 * dt);
        if (bd < 1.2 + 1.0 * f.scale){ eat(f, best); best = null; }
      }

      // плавное отражение от стен
      const M = 3, W = 12 * dt;
      if (p.x >  BOUNDS.x - M)   v.x -= W * Math.min(1, (p.x - (BOUNDS.x - M)) / M + 0.4);
      if (p.x < -BOUNDS.x + M)   v.x += W * Math.min(1, (-BOUNDS.x + p.x) / M + 0.4);
      if (p.z >  BOUNDS.z - M)   v.z -= W * Math.min(1, (p.z - (BOUNDS.z - M)) / M + 0.4);
      if (p.z < -BOUNDS.z + M)   v.z += W * Math.min(1, (-BOUNDS.z + p.z) / M + 0.4);
      if (p.y >  BOUNDS.yMax - M) v.y -= W * Math.min(1, (p.y - (BOUNDS.yMax - M)) / M + 0.4);
      if (p.y <  BOUNDS.yMin + M) v.y += W * Math.min(1, (BOUNDS.yMin + p.y) / M + 0.4);

      // ограничение скорости (разгоняются за кормом)
      const maxS = f.speed * (best ? 1.85 : 1);
      const s = v.length();
      if (s > maxS) v.multiplyScalar(maxS / s);
      else if (s < 1.1 && s > 1e-5) v.multiplyScalar(1.1 / s);

      p.addScaledVector(v, dt);
      p.x = clamp(p.x, -BOUNDS.x, BOUNDS.x);
      p.y = clamp(p.y, BOUNDS.yMin, BOUNDS.yMax);
      p.z = clamp(p.z, -BOUNDS.z, BOUNDS.z);

      // плавный поворот в направлении движения
      if (s > 1e-4){
        _q.setFromUnitVectors(FWD, _v.copy(v).normalize());
        f.mesh.quaternion.slerp(_q, 1 - Math.pow(0.03, dt));
      }

      // анимация: хвост, изгиб тела, плавники
      const wag = Math.sin(t * f.tailSpeed + f.phase);
      f.tail.rotation.y = wag * 0.55;
      f.body.rotation.y = wag * 0.1;
      const flut = Math.sin(t * f.tailSpeed * 1.25 + f.phase * 1.7);
      f.leftFin.rotation.y  = -0.65 + flut * 0.4;
      f.rightFin.rotation.y =  0.65 - flut * 0.4;
      f.dorsal.rotation.x = Math.sin(t * f.tailSpeed * 0.7 + f.phase) * 0.08;
    }

    /* ================= кольцо-«пинг» в точке клика ================= */
    const pings = [];
    function ping(pos){
      const m = new THREE.Mesh(
        new THREE.RingGeometry(0.4, 0.55, 40),
        new THREE.MeshBasicMaterial({ color:0xaef1ff, transparent:true, opacity:0.85, side:THREE.DoubleSide, depthWrite:false })
      );
      m.position.copy(pos);
      m.lookAt(camera.position);
      scene.add(m);
      pings.push({ m, life:0.55 });
    }
    function updatePings(dt){
      for (let i = pings.length - 1; i >= 0; i--){
        const pg = pings[i];
        pg.life -= dt;
        if (pg.life <= 0){
          scene.remove(pg.m);
          pg.m.geometry.dispose();
          pg.m.material.dispose();
          pings.splice(i, 1);
          continue;
        }
        const k = 1 - pg.life / 0.55;
        pg.m.scale.setScalar(1 + k * 2.6);
        pg.m.material.opacity = 0.85 * (pg.life / 0.55);
      }
    }

    /* ================= кормление кликом (различаем клик и драг камеры) ================= */
    const raycaster = new THREE.Raycaster();
    const ndc = new THREE.Vector2();
    let down = null;

    renderer.domElement.addEventListener('pointerdown', (e) => {
      if (e.button === 0) down = { x:e.clientX, y:e.clientY, t:performance.now() };
    });
    renderer.domElement.addEventListener('pointerup', (e) => {
      if (e.button !== 0 || !down) return;
      const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y);
      const quick = performance.now() - down.t < 350;
      down = null;
      if (moved > 6 || !quick) return; // это было вращение камеры
      ndc.set((e.clientX / window.innerWidth) * 2 - 1, -(e.clientY / window.innerHeight) * 2 + 1);
      raycaster.setFromCamera(ndc, camera);
      const hits = raycaster.intersectObject(glass, false);
      if (!hits.length) return;
      const pt = hits[0].point;
      pt.x = clamp(pt.x, -16, 16);
      pt.y = clamp(pt.y, 1.2, 22.4);
      pt.z = clamp(pt.z, -8, 8);
      spawnFood(pt);
    });

    /* ================= UI ================= */
    btnFish.addEventListener('click', () => { if (fishArray.length < 40) createFish(); });
    btnBubbles.addEventListener('click', () => {
      for (let i = 0; i < 10; i++)
        spawnBubble(rand(-15,15), rand(1,22), rand(-7.5,7.5), 0.12 + Math.random()*0.28);
    });

    let lightsOn = true;
    btnLight.addEventListener('click', () => {
      lightsOn = !lightsOn;
      dirLight.intensity = lightsOn ? 1.15 : 0.1;
      ambLight.intensity = lightsOn ? 0.4 : 0.15;
      pl1.intensity = lightsOn ? 0.55 : 0.95; // ночью голубые огни выходят на первый план
      pl2.intensity = lightsOn ? 0.5 : 0.85;
      btnLight.classList.toggle('off', !lightsOn);
      btnLight.textContent = lightsOn ? '💡 Свет' : '🌙 Свет';
    });

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    /* ================= главный цикл ================= */
    const clock = new THREE.Clock();
    let introT = 0, frames = 0, acc = 0;

    function animate(){
      requestAnimationFrame(animate);
      const dt = Math.min(clock.getDelta(), 0.05);
      const t = clock.elapsedTime;

      // интро: медленный подлёт камеры
      if (introT < 1){
        introT = Math.min(1, introT + dt / 1.8);
        const e = 1 - Math.pow(1 - introT, 3);
        camera.position.lerpVectors(CAM_A, CAM_B, e);
        if (introT >= 1) controls.enabled = true;
      }

      for (const f of fishArray) updateFish(f, dt, t);
      updateFood(dt, t);
      updateBubbles(dt, t);
      updatePings(dt);

      for (const s of seaweed){
        s.mesh.rotation.x = Math.sin(t * s.speed + s.phase) * 0.1;
        s.mesh.rotation.z = Math.cos(t * s.speed * 0.8 + s.phase) * 0.1;
      }

      if (lightsOn){ // лёгкое «дыхание» подводных огней
        pl1.intensity = 0.55 + Math.sin(t * 1.3) * 0.07;
        pl2.intensity = 0.5 + Math.cos(t * 1.1 + 2) * 0.07;
      }

      controls.update();
      renderer.render(scene, camera);

      // FPS
      frames++; acc += dt;
      if (acc >= 0.5){
        const fps = Math.round(frames / acc);
        stFps.textContent = fps;
        const col = fps >= 50 ? '#5cff9d' : fps >= 30 ? '#ffd23e' : '#ff5c5c';
        fpsDot.style.background = col;
        fpsDot.style.boxShadow = '0 0 8px ' + col;
        frames = 0; acc = 0;
      }
    }
    animate();
  })();
  </script>
</body>
</html>
```

**Что внутри**

- **Рыбки (15 на старте, до 40):** тело, глаза с зрачками, хвост на шарнире, спинной/грудной/анальный плавники; 8 палитр, масштаб 0.6–1.2, у каждой свои скорость, фаза и радиус избегания. ИИ: разлёт при сближении, мягкий отскок от стен, блуждание, погоня за кормом (радиус 15) с разгоном, рост +5% за каждую частицу.
- **Окружение:** стекло с `transmission: 0.95` + wireframe-рамка, процедурный песок, 8 гранёных камней с тенями, 12 кустов водорослей (TubeGeometry, покачиваются от основания), 30 пузырей с синусоидным дрейфом.
- **Кормление:** клик по воде (клики отделены от вращения камеры) — частица падает с гравитацией и сопротивлением, всплывает кольцо-«пинг», съевшая рыбка получает мини-всплеск пузырей.
- **Свет:** ambient + directional (тени 2048², PCFSoft) + два «дышащих» point-light; кнопка «Свет» переключает день/ночь — ночью сценой управляют голубые огни.
- **UI:** панель управления слева, живая статистика справа (рыбки / корм / FPS с цветным индикатором), подсказка, исчезающая после первого кормления; интро-подлёт камеры при загрузке.

**Точки настройки:** размеры аквариума — `TANK`, границы плава — `BOUNDS`, характер ИИ — константы в `updateFish` (сила разгона `6.5`, радиус поиска `15`, радиус съедания), палитры — `FISH_PALETTES`.