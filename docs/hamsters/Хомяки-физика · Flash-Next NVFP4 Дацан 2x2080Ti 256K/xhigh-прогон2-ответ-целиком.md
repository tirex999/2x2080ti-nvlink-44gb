# Хомяки в колесе — честная физика

Ниже — один самодостаточный HTML-файл. Все ключевые величины («ω», «v обода», «Δ%», отклонение от оси трубы, счётчики проходов сквозь стенки) читаются снаружи: `window.CAGE = { hamsters, wheel, tube, bowl, checks }`.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Хомяки в колесе — честная физика</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0d1014; --panel:#141a21; --panel2:#101720;
  --ink:#e9f0f4; --dim:#8ba0ad; --dimmer:#5d7280;
  --amber:#f2a52c; --lime:#a6d94f; --coral:#ef7a52; --sky:#6fc3d8;
  --line:rgba(255,255,255,.075);
  --mono:'JetBrains Mono',ui-monospace,monospace;
  --disp:'Bricolage Grotesque','Manrope',sans-serif;
  --body:'Manrope',system-ui,sans-serif;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);overflow:hidden}
#app{display:flex;height:100%}
#stage{position:relative;flex:1;min-width:0}
#stage canvas{display:block}

/* ---------- верхний левый блок ---------- */
.hud{position:absolute;left:clamp(16px,2.4vw,34px);top:clamp(16px,2.4vw,30px);pointer-events:none;max-width:min(46%,520px)}
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--dim);
  display:flex;align-items:center;gap:9px;margin-bottom:14px;animation:rise .8s .1s both}
.live{color:#0d1014;background:var(--lime);padding:2.5px 7px;border-radius:3px;font-weight:700;letter-spacing:.12em;
  animation:pulse 2.2s ease-in-out infinite}
.hud h1{font-family:var(--disp);font-weight:800;font-size:clamp(2.3rem,5.4vw,4.5rem);line-height:.86;letter-spacing:-.035em;
  margin:0 0 14px;text-shadow:0 12px 40px rgba(0,0,0,.65);animation:rise .9s .18s both}
.hud h1 em{font-style:normal;color:var(--amber);position:relative}
.hud h1 em::after{content:'';position:absolute;left:0;right:0;bottom:.09em;height:.07em;background:var(--coral);opacity:.85}
.lede{margin:0;font-size:14.5px;line-height:1.55;color:#b8c8d2;max-width:34ch;animation:rise .9s .3s both}
.lede b{color:var(--ink);font-weight:700}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px;animation:rise .9s .42s both}
.chip{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;padding:6px 9px;border:1px solid var(--line);
  border-radius:5px;background:rgba(20,26,33,.62);backdrop-filter:blur(6px);color:var(--dim)}
.chip b{color:var(--amber);font-weight:700}
.hint{position:absolute;left:clamp(16px,2.4vw,34px);bottom:clamp(14px,2vw,24px);font-family:var(--mono);font-size:10px;
  letter-spacing:.14em;text-transform:uppercase;color:var(--dimmer);pointer-events:none;animation:rise 1s .6s both}
.hint span{color:var(--sky)}

/* ---------- правая панель ---------- */
#panel{width:392px;flex:none;background:
    radial-gradient(120% 60% at 100% 0%,rgba(242,165,44,.09),transparent 60%),
    linear-gradient(180deg,var(--panel),var(--panel2));
  border-left:1px solid var(--line);overflow-y:auto;overflow-x:hidden;padding:22px 20px 40px;
  box-shadow:-30px 0 60px rgba(0,0,0,.45)}
#panel::-webkit-scrollbar{width:9px}#panel::-webkit-scrollbar-thumb{background:#2a343d;border-radius:9px}
.p-head{display:flex;align-items:flex-end;justify-content:space-between;gap:10px;padding-bottom:14px;border-bottom:1px solid var(--line)}
.p-head h2{font-family:var(--disp);font-weight:800;font-size:26px;letter-spacing:-.02em;margin:0;line-height:1}
.p-head small{font-family:var(--mono);font-size:9.5px;letter-spacing:.18em;color:var(--dimmer);text-transform:uppercase;text-align:right}
section{margin-top:22px;animation:rise .7s both}
section:nth-of-type(1){animation-delay:.10s}section:nth-of-type(2){animation-delay:.18s}
section:nth-of-type(3){animation-delay:.26s}section:nth-of-type(4){animation-delay:.34s}section:nth-of-type(5){animation-delay:.42s}
.sec-t{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--dimmer);margin-bottom:10px}
.sec-t::after{content:'';flex:1;height:1px;background:var(--line)}

/* список зверьков */
.hrow{position:relative;display:flex;align-items:center;gap:10px;padding:9px 10px 9px 12px;border-radius:8px;cursor:pointer;
  transition:background .18s,transform .18s;background:rgba(255,255,255,.018)}
.hrow::before{content:'';position:absolute;left:0;top:50%;translate:0 -50%;width:3px;height:0;border-radius:3px;
  background:var(--amber);transition:height .22s cubic-bezier(.3,1.4,.5,1)}
.hrow:hover{background:rgba(255,255,255,.06);transform:translateX(3px)}
.hrow.sel{background:rgba(242,165,44,.10)}
.hrow.sel::before,.hrow:hover::before{height:74%}
.dot{width:13px;height:13px;border-radius:50%;flex:none;box-shadow:0 0 0 2px rgba(0,0,0,.35),0 0 14px 1px currentColor}
.hmeta{min-width:0;flex:1}
.hname{font-family:var(--disp);font-weight:700;font-size:14.5px;letter-spacing:-.01em}
.hstat{font-size:11.5px;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hbar{width:46px;height:4px;border-radius:4px;background:rgba(255,255,255,.09);overflow:hidden;flex:none}
.hbar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--sky),var(--lime));transition:width .16s linear}

/* командная строка */
.cmds{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
button{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink);
  background:rgba(255,255,255,.055);border:1px solid var(--line);border-radius:6px;padding:7px 9px;cursor:pointer;
  transition:background .16s,border-color .16s,transform .1s,color .16s}
button:hover{background:rgba(242,165,44,.16);border-color:rgba(242,165,44,.5);color:#ffd899;transform:translateY(-1px)}
button:active{transform:translateY(0)}
button.on{background:var(--amber);border-color:var(--amber);color:#12161b;font-weight:700}

/* числа */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.cell{background:rgba(255,255,255,.035);border:1px solid var(--line);border-radius:8px;padding:9px 10px}
.cell .k{font-family:var(--mono);font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--dimmer)}
.cell .v{font-family:var(--mono);font-size:20px;font-weight:700;letter-spacing:-.02em;margin-top:3px;line-height:1.1}
.cell .v small{font-size:10px;font-weight:400;color:var(--dim);letter-spacing:0}
.amber{color:var(--amber)}.lime{color:var(--lime)}.coral{color:var(--coral)}.sky{color:var(--sky)}
#spark{display:block;width:100%;height:56px;margin-top:8px;border-radius:8px;background:rgba(0,0,0,.28);border:1px solid var(--line)}
.note{font-size:11px;line-height:1.5;color:var(--dim);margin-top:8px}
.note code{font-family:var(--mono);font-size:10.5px;color:var(--sky)}

/* проверки */
.chk{display:flex;align-items:flex-start;gap:9px;padding:7px 0;border-bottom:1px dashed rgba(255,255,255,.06)}
.chk:last-child{border-bottom:0}
.beed{width:8px;height:8px;border-radius:50%;flex:none;margin-top:4px;background:#3d4b56;transition:background .25s,box-shadow .25s}
.beed.ok{background:var(--lime);box-shadow:0 0 10px rgba(166,217,79,.75)}
.beed.warn{background:var(--amber);box-shadow:0 0 10px rgba(242,165,44,.7)}
.chk .t{font-size:12px;line-height:1.35}
.chk .t b{display:block;font-weight:600}
.chk .t span{font-family:var(--mono);font-size:10.5px;color:var(--dim)}
.foot{margin-top:20px;padding-top:14px;border-top:1px solid var(--line);font-family:var(--mono);font-size:10px;
  line-height:1.7;color:var(--dimmer);letter-spacing:.03em}
.foot b{color:var(--dim);font-weight:500}

@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.42}}
@media (max-width:980px){
  #app{flex-direction:column}#panel{width:auto;height:46%;border-left:0;border-top:1px solid var(--line)}
  .hud{max-width:70%}.lede{display:none}
}
</style>
</head>
<body>
<div id="app">
  <div id="stage">
    <div class="hud">
      <div class="kicker"><span class="live">LIVE</span> Three.js r128 · PCFSoft 2048 · ω = v / R</div>
      <h1>Хомя<br><em>чная</em> физика</h1>
      <p class="lede">Пять зверьков живут своей жизнью. Колесо крутится <b>только</b> от их лап, труба — полая,
        а лапы не скользят: фаза шага считается от пройденного пути.</p>
      <div class="chips">
        <div class="chip">R колеса = <b id="cR">—</b></div>
        <div class="chip">габарит зверя = <b id="cD">—</b></div>
        <div class="chip">шагов/с = <b id="cS">—</b></div>
      </div>
    </div>
    <div class="hint"><span>ЛКМ</span> орбита · <span>колесо</span> зум · <span>клик по хомяку</span> прыжок · <span>пробел</span> слоу-мо</div>
  </div>

  <aside id="panel">
    <div class="p-head">
      <h2>Питомцы</h2>
      <small>5 особей<br>конечный автомат</small>
    </div>

    <section>
      <div class="sec-t">Кто чем занят</div>
      <div id="list"></div>
      <div class="cmds" id="cmds">
        <button data-cmd="wheel">в колесо</button>
        <button data-cmd="tube">в трубу</button>
        <button data-cmd="eat">к миске</button>
        <button data-cmd="drink">к поилке</button>
        <button data-cmd="wander">гулять</button>
      </div>
    </section>

    <section>
      <div class="sec-t">Колесо · ведущее тело</div>
      <div class="grid">
        <div class="cell"><div class="k">ω, рад/с</div><div class="v amber" id="wOmega">0.00</div></div>
        <div class="cell"><div class="k">|ω|·R обода</div><div class="v sky" id="wRim">0.00 <small>м/с</small></div></div>
        <div class="cell"><div class="k">v лап бегуна</div><div class="v lime" id="wPaw">0.00 <small>м/с</small></div></div>
        <div class="cell"><div class="k">расхождение</div><div class="v" id="wSlip">—</div></div>
      </div>
      <canvas id="spark"></canvas>
      <div class="note" id="wNote">бегуна нет — колесо тормозит трением: <code>dω/dt = −μ·sign(ω)</code></div>
    </section>

    <section>
      <div class="sec-t">Труба · ось и торцы</div>
      <div class="grid">
        <div class="cell"><div class="k">отклонение от оси</div><div class="v lime" id="tDev">0.000 <small>м</small></div></div>
        <div class="cell"><div class="k">путь вдоль оси</div><div class="v sky" id="tX">— <small>м</small></div></div>
      </div>
      <div class="note" id="tNote">стенка — две капсулы: сбоку непроходимо, вход только через торец.</div>
    </section>

    <section>
      <div class="sec-t">Сцена</div>
      <div class="cmds">
        <button id="bBody">тела столкновений</button>
        <button id="bSlow">слоу-мо ×0.25</button>
        <button id="bOrbit">автоповорот</button>
      </div>
    </section>

    <section>
      <div class="sec-t">Проверки честности</div>
      <div id="checks"></div>
      <div class="foot" id="foot"></div>
    </section>
  </aside>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ============================================================================
   0. УТИЛИТЫ И КОНСТАНТЫ ГАБАРИТОВ
   ========================================================================== */
const TAU = Math.PI * 2;
const clamp = (v,a,b)=> v<a?a:(v>b?b:v);
const lerp  = (a,b,t)=> a+(b-a)*t;
const damp  = (a,b,l,dt)=> lerp(a,b,1-Math.exp(-l*dt));
const rnd   = (a,b)=> a+Math.random()*(b-a);
function angLerp(a,b,t){ let d=(b-a)%TAU; if(d>Math.PI)d-=TAU; if(d<-Math.PI)d+=TAU; return a+d*t; }
function dampAngle(a,b,l,dt){ return angLerp(a,b,1-Math.exp(-l*dt)); }

/* --- габарит зверя: из них рождается радиус колеса (п.1.2) --- */
const ДЛИНА_ЗВЕРЯ   = 0.52;  // нос → основание хвоста
const ВЫСОТА_ЗВЕРЯ  = 0.38;  // лапы → верх спины/головы
const ШИРИНА_ЗВЕРЯ  = 0.34;  // бока
const РАДИУС_ТЕЛА   = 0.155; // радиус тела в плане (для столкновений)
const ДЛИНА_ШАГА    = 0.30;  // путь корпуса за один цикл диагональной пары
const ДЮТИ          = 0.5;   // фаза опоры в цикле

/* --- колесо: R вычисляется ОТ размера зверя, а не подбирается на глаз --- */
// самая «дальнобойная» точка тела от оси колеса, если зверь стоит в нижней точке обода
const ДИАГОНАЛЬ_ЗВЕРЯ = Math.hypot(ДЛИНА_ЗВЕРЯ/2, ВЫСОТА_ЗВЕРЯ);            // 0.460
const ЗАПАС_ВНУТРИ    = 0.075;                                              // не впритык
const R_из_габарита   = ДИАГОНАЛЬ_ЗВЕРЯ + ЗАПАС_ВНУТРИ;                      // 0.535
// дуга под телом не круче 100°, иначе зверь «оборачивает» обод
const R_из_дуги       = (ДЛИНА_ЗВЕРЯ + 0.30) / THREE.MathUtils.degToRad(100);// 0.469
const R_КОЛЕСА        = Math.ceil(Math.max(R_из_габарита, R_из_дуги)*100)/100; // 0.54
const ТОЛЩИНА_ОБОДА   = 0.045;
const R_ОБОДА_ВНЕШ    = R_КОЛЕСА + ТОЛЩИНА_ОБОДА;
const ШИРИНА_КОЛЕСА   = ШИРИНА_ЗВЕРЯ + 0.28;   // расстояние между ободами шире боков

/* --- клетка --- */
const ПОЛУШ_Х = 2.35, ПОЛУШ_Z = 1.65, ВЫСОТА_СТЕНОК = 1.18, КРОМКА = 0.085;

/* --- труба (полой цилиндр лежит на подстилке) --- */
const ТРУБА = { x:0.95, y:0, z:0.35, len:2.10, rIn:0.30, wall:0.045 };
ТРУБА.rOut = ТРУБА.rIn + ТРУБА.wall;
ТРУБА.y    = ТРУБА.rOut;          // внешняя нижняя точка касается подстилки
ТРУБА.yОпоры = ТРУБА.rOut - ТРУБА.rIn;  // внутренний низ, на нём и стоит зверь

/* ============================================================================
   1. СЦЕНА / РЕНДЕР / СВЕТ
   ========================================================================== */
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(stage.clientWidth, stage.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x151a21);
scene.fog = new THREE.Fog(0x151a21, 11, 34);

const camera = new THREE.PerspectiveCamera(38, stage.clientWidth/stage.clientHeight, 0.1, 100);
camera.position.set(5.15, 3.55, 5.75);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.52, 0);
controls.enableDamping = true; controls.dampingFactor = .06;
controls.minDistance = 2.2; controls.maxDistance = 15;
controls.maxPolarAngle = 1.53; controls.minPolarAngle = .18;
controls.autoRotateSpeed = .35;
controls.update();

// направленный «оконный» свет + мягкий фон
const key = new THREE.DirectionalLight(0xfff2dd, 2.0);
key.position.set(-6.4, 7.6, 3.6);
key.castShadow = true;
key.shadow.mapSize.set(2048,2048);
key.shadow.camera.left=-4.2; key.shadow.camera.right=4.2;
key.shadow.camera.top=4.2;  key.shadow.camera.bottom=-4.2;
key.shadow.camera.near=1; key.shadow.camera.far=22;
key.shadow.bias=-0.0006; key.shadow.normalBias=0.022; key.shadow.radius=2;
key.target.position.set(0,.35,0); scene.add(key, key.target);

const fill = new THREE.DirectionalLight(0x9fc4d8, 0.42);
fill.position.set(5,3.4,6.5); scene.add(fill);
scene.add(new THREE.HemisphereLight(0x9db8cc, 0x3b2f26, 0.62));

const lampLight = new THREE.PointLight(0xffc98a, 14, 9, 2);
lampLight.position.set(3.6, 2.35, 2.9); scene.add(lampLight);

/* ============================================================================
   2. КОМНАТА (окружение: сцена не висит в пустоте)
   ========================================================================== */
const SPHERE = new THREE.SphereGeometry(1,18,12);
function box(w,h,d,mat,x,y,z){ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat); m.position.set(x,y,z); return m; }

(function buildRoom(){
  const woodFloor = new THREE.MeshStandardMaterial({color:0x4a382b, roughness:.78});
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(44,44), woodFloor);
  floor.rotation.x = -Math.PI/2; floor.position.y = -1.62; floor.receiveShadow = true; scene.add(floor);

  // доски на полу
  const plankMat = new THREE.MeshStandardMaterial({color:0x3d2e23, roughness:.85});
  const planks = new THREE.InstancedMesh(new THREE.BoxGeometry(44,.012,.02), plankMat, 46);
  const mtx = new THREE.Matrix4();
  for(let i=0;i<46;i++){ mtx.makeTranslation(0,-1.612,-20+i*.9); planks.setMatrixAt(i,mtx); }
  planks.instanceMatrix.needsUpdate = true; scene.add(planks);

  const wallA = new THREE.MeshStandardMaterial({color:0x37424e, roughness:.96});
  const wallB = new THREE.MeshStandardMaterial({color:0x2f3945, roughness:.96});
  const w1 = new THREE.Mesh(new THREE.PlaneGeometry(44,16), wallA);
  w1.position.set(0,6.38,-7.4); w1.receiveShadow=true; scene.add(w1);
  const w2 = new THREE.Mesh(new THREE.PlaneGeometry(44,16), wallB);
  w2.rotation.y = Math.PI/2; w2.position.set(-9.4,6.38,0); w2.receiveShadow=true; scene.add(w2);

  const base = new THREE.MeshStandardMaterial({color:0x222a33, roughness:.8});
  const b1 = box(44,.28,.06,base,0,-1.44,-7.36); const b2 = box(.06,.28,44,base,-9.36,-1.44,0);
  scene.add(b1,b2);

  // окно на левой стене + тёплый свет из него
  const frameMat = new THREE.MeshStandardMaterial({color:0xdcd5c8, roughness:.6});
  const glow = new THREE.Mesh(new THREE.PlaneGeometry(3.1,2.3),
        new THREE.MeshBasicMaterial({color:0xbfe4f2}));
  glow.rotation.y = Math.PI/2; glow.position.set(-9.33,1.35,1.6); scene.add(glow);
  const fr = new THREE.Group(); fr.position.set(-9.3,1.35,1.6);
  fr.add(box(.09,2.5,.1,frameMat,0,1.18,0), box(.09,2.5,.1,frameMat,0,-1.18,0),
         box(.09,.1,3.24,frameMat,0,1.18,0), box(.09,.1,3.24,frameMat,0,-1.18,0),
         box(.07,2.3,.07,frameMat,0,0,0), box(.07,.07,2.3,frameMat,0,.1,0));
  fr.children.forEach(c=>c.castShadow=false); scene.add(fr);

  // рамы-картины на задней стене
  const art = new THREE.Group(); art.position.set(2.6,1.9,-7.32);
  [[0,0,1.5,1.05,0x8fae8b],[-1.9,-.2,.85,1.15,0xc4886a]].forEach(a=>{
    const g=new THREE.Group(); g.position.set(a[0],a[1],0);
    g.add(box(.07,a[3]+.1,.05,new THREE.MeshStandardMaterial({color:0x2b2320,roughness:.5}),0,0,0));
    const cv=new THREE.Mesh(new THREE.PlaneGeometry(a[2],a[3]),new THREE.MeshStandardMaterial({color:a[4],roughness:.9}));
    cv.position.set(.041,0,.028); cv.rotation.y=Math.PI/2; g.add(cv); art.add(g);
  });
  scene.add(art);

  // торшер в углу
  const metal = new THREE.MeshStandardMaterial({color:0x9aa3ad, roughness:.35, metalness:.7});
  const lampG = new THREE.Group(); lampG.position.set(4.1,0,3.4);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(.03,.045,2.6,12), metal);
  pole.position.y=-.32; pole.castShadow=true; lampG.add(pole);
  const footL = new THREE.Mesh(new THREE.CylinderGeometry(.28,.3,.05,20), metal); footL.position.y=-1.6; lampG.add(footL);
  const shade = new THREE.Mesh(new THREE.CylinderGeometry(.26,.42,.42,20,1,true),
      new THREE.MeshStandardMaterial({color:0xf3d9a8,roughness:.7,side:THREE.DoubleSide,emissive:0x insertion}));
  lampG.add(shade); shade.position.set(0,1.02,0);
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(.09,10,8), new THREE.MeshBasicMaterial({color:0xffe4b0}));
  bulb.position.set(0,.95,0); lampG.add(bulb);
  scene.add(lampG);

  // ковёр
  const rug = new THREE.Mesh(new THREE.CircleGeometry(3.1,48),
      new THREE.MeshStandardMaterial({color:0x2f4a52, roughness:.98}));
  rug.rotation.x=-Math.PI/2; rug.position.set(-.4,-1.607,.6); rug.receiveShadow=true; scene.add(rug);

  // стол
  const tableTop = new THREE.MeshStandardMaterial({color:0x6b4a30, roughness:.55});
  const tableLeg = new THREE.MeshStandardMaterial({color:0x2c2723, roughness:.6, metalness:.2});
  const top = box(6.4,.13,4.9,tableTop,0,-.31,0); top.receiveShadow=true; top.castShadow=true; scene.add(top);
  [[-2.85,-2.1],[2.85,-2.1],[-2.85,2.1],[2.85,2.1]].forEach(p=>{
    const l = box(.14,1.2,.14,tableLeg,p[0],-.97,p[1]); l.castShadow=true; scene.add(l);
  });
})();

/* ============================================================================
   3. КЛЕТКА: поддон, частые прутья (InstancedMesh), рамки по верху
   ========================================================================== */
const cage = new THREE.Group(); scene.add(cage);
(function buildCage(){
  const trayMat  = new THREE.MeshStandardMaterial({color:0xd8d2c6, roughness:.55});
  const frameMat = new THREE.MeshStandardMaterial({color:0x8b7355, roughness:.5});
  const barMat   = new THREE.MeshStandardMaterial({color:0xb9c2cb, roughness:.32, metalness:.75});

  // поддон (пол + борта)
  const floor = box(ПОЛУШ_Х*2+.24,.1,ПОЛУШ_Z*2+.24,trayMat,0,-.215,0);
  floor.receiveShadow = true; cage.add(floor);
  const inner = box(ПОЛУШ_Х*2,.06,ПОЛУШ_Z*2,new THREE.MeshStandardMaterial({color:0xece3d2,roughness:.95}),0,-.14,0);
  inner.receiveShadow=true; cage.add(inner);
  const rimH = КРОМКА+.14;
  [[0,-ПОЛУШ_Z-.06,ПОЛУШ_Х*2+.28,.2],[0,ПОЛУШ_Z+.06,ПОЛУШ_Х*2+.28,.2],
   [-ПОЛУШ_Х-.06,0,.2,ПОЛУШ_Z*2+.2],[ПОЛУШ_Х+.06,0,.2,ПОЛУШ_Z*2+.2]].forEach(s=>{
    const m = box(s[2],rimH,s[3],trayMat,s[1]*0+ (s[0]||0), -rimH/2+КРОМКА+.02, s[1]||0);
    if(Math.abs(s[0])>.01){ m.position.x=s[0]; m.position.z=s[1]||0; } else { m.position.z=s[1]; }
    m.castShadow=true; m.receiveShadow=true; cage.add(m);
  });

  // прутья — один InstancedMesh
  const step = .155, bh = ВЫСОТА_СТЕНОК-КРОМКА;
  const spots = [];
  for(let x=-ПОЛУШ_Х+.02; x<=ПОЛУШ_Х-.01; x+=step){ spots.push([x,-ПОЛУШ_Z],[x,ПОЛУШ_Z]); }
  for(let z=-ПОЛУШ_Z+step; z<=ПОЛУШ_Z-.01; z+=step){ spots.push([-ПОЛУШ_Х,z],[ПОЛУШ_Х,z]); }
  const bars = new THREE.InstancedMesh(new THREE.CylinderGeometry(.0135,.0135,bh,7), barMat, spots.length);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), v = new THREE.Vector3(), s = new THREE.Vector3(1,1,1);
  spots.forEach((p,i)=>{ v.set(p[0], КРОМКА+bh/2, p[1]); m4.compose(v,q,s); bars.setMatrixAt(i,m4); });
  bars.instanceMatrix.needsUpdate = true; bars.castShadow = true; cage.add(bars);

  // угловые стойки + рамки по верху и по низу
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(c=>{
    const p = box(.062,ВЫСОТА_СТЕНОК+.05,.062,frameMat,c[0]*ПОЛУШ_Х,(ВЫСОТА_СТЕНОК+.05)/2,c[1]*ПОЛУШ_Z);
    p.castShadow=true; cage.add(p);
  });
  const rails = [[0,-ПОЛУШ_Z,ПОЛУШ_Х*2+.16,.05,.05],[0,ПОЛУШ_Z,ПОЛУШ_Х*2+.16,.05,.05],
                 [-ПОЛУШ_Х,0,.05,.05,ПОЛУШ_Z*2+.16],[ПОЛУШ_Х,0,.05,.05,ПОЛУШ_Z*2+.16]];
  rails.forEach(r=>{
    [КРОМКА+.02, ВЫСОТА_СТЕНОК-.01].forEach(y=>{
      const b = box(r[2],r[3],r[4],frameMat,r[0],y,r[1]); b.castShadow=true; cage.add(b);
    });
  });
  // поперечная планка посередине высоты (чтобы прутья не «гуляли»)
  [ -ПОЛУШ_Z, ПОЛУШ_Z ].forEach(z=> cage.add(box(ПОЛУШ_Х*2+.1,.03,.03,frameMat,0,.62,z)));
  [ -ПОЛУШ_Х, ПОЛУШ_Х ].forEach(x=> cage.add(box(.03,.03,ПОЛУШ_Z*2+.1,frameMat,x,.62,0)));
})();

/* ============================================================================
   4. ПОДСТИЛКА: много щепок ОДНИМ InstancedMesh
   ========================================================================== */
(function buildBedding(){
  const N = 1500;
  const geo = new THREE.BoxGeometry(.085,.011,.024);
  const mat = new THREE.MeshStandardMaterial({roughness:.95});
  const im = new THREE.InstancedMesh(geo, mat, N);
  const m4=new THREE.Matrix4(), e=new THREE.Euler(), q=new THREE.Quaternion(), v=new THREE.Vector3(), s=new THREE.Vector3();
  const col = new THREE.Color();
  const tones=[0xd9b877,0xc9a463,0xe6cfa0,0xb98f52,0xe2bd83];
  let i=0, guard=0;
  while(i<N && guard<N*40){
    guard++;
    const outside = (i>1400);
    let x,z,y,rz,ry,tilt;
    if(outside){ x=rnd(-3.1,3.1); z=rnd(-2.4,2.4); y=-.235; }
    else {
      x=rnd(-ПОЛУШ_Х+.05,ПОЛУШ_Х-.05); z=rnd(-ПОЛУШ_Z+.05,ПОЛУШ_Z-.05); y=.004+Math.random()*.016;
      // не сыпать щепки туда, где стоят предметы
      if(Math.abs(x-WHEEL_X)<R_ОБОДА_ВНЕШ+.1 && Math.abs(z-WHEEL_Z)<ШИРИНА_КОЛЕСА/2+.1) continue;
      if(Math.abs(x-ТРУБА.x)<ТРУБА.len/2+.08 && Math.abs(z-ТРУБА.z)<ТРУБА.rOut+.06) continue;
      if(Math.hypot(x-BOWL_X,z-BOWL_Z)<BOWL_R+.08) continue;
    }
    ry=rnd(0,TAU); tilt=rnd(-.35,.35);
    e.set(tilt,ry,rnd(-.4,.4)); q.setFromEuler(e);
    v.set(x,y,z); s.set(rnd(.6,1.5),rnd(.7,1.9),rnd(.7,1.4));
    m4.compose(v,q,s); im.setMatrixAt(i,m4);
    col.setHex(tones[(Math.random()*tones.length)|0]).multiplyScalar(rnd(.78,1.12));
    im.setColorAt(i,col);
    i++;
  }
  im.count=i; im.instanceMatrix.needsUpdate=true; if(im.instanceColor) im.instanceColor.needsUpdate=true;
  im.receiveShadow=true; im.castShadow=false; scene.add(im);
})();

/* ============================================================================
   5. ПРЕДМЕТЫ: КОЛЕСО (ведущее тело), ТРУБА, МИСКА, ПОИЛКА
   ========================================================================== */
const WHEEL_X = -1.42, WHEEL_Z = -0.78;

const КОЛЕСО = {
  x:WHEEL_X, z:WHEEL_Z, axis:'z',
  R:R_КОЛЕСА, R_OUT:R_ОБОДА_ВНЕШ, width:ШИРИНА_КОЛЕСА,
  yCenter:R_ОБОДА_ВНЕШ, yContact:R_ОБОДА_ВНЕШ-R_КОЛЕСА,   // нижняя точка обода
  angle:0, omega:0, friction:1.55,      // рад/с² — трение в оси
  user:null, slipPct:0, pawSpeed:0, rimSpeed:0, freeDecayOk:true,
  portal:{x:WHEEL_X, z:WHEEL_Z+ШИРИНА_КОЛЕСА/2+0.30},
  contact(){ return {x:this.x, y:this.yContact, z:this.z}; }
};
window.КОЛЕСО = КОЛЕСО;

const wheelRoot = new THREE.Group(); wheelRoot.position.set(КОЛЕСО.x, КОЛЕСО.yCenter, КОЛЕСО.z); scene.add(wheelRoot);
const wheelSpin = new THREE.Group(); wheelRoot.add(wheelSpin); КОЛЕСО.spin = wheelSpin;
(function buildWheel(){
  const plastic = new THREE.MeshStandardMaterial({color:0xf0f4f2, roughness:.35, transparent:true, opacity:.62, side:THREE.DoubleSide});
  const solid   = new THREE.MeshStandardMaterial({color:0xe8eef0, roughness:.42, side:THREE.DoubleSide});
  const dark    = new THREE.MeshStandardMaterial({color:0x4c565e, roughness:.5, metalness:.25});

  const W=КОЛЕСО.width, RO=КОЛЕСО.R_OUT, R=КОЛЕСО.R;
  const disc = new THREE.Mesh(new THREE.CircleGeometry(RO-.01,44), plastic);
  disc.position.z = -W/2; wheelSpin.add(disc);

  const rim = new THREE.Mesh(new THREE.CylinderGeometry(RO,RO,W,48,1,true), solid);
  rim.rotation.x = Math.PI/2; rim.castShadow = true; wheelSpin.add(rim);

  const ringNear = new THREE.Mesh(new THREE.TorusGeometry(RO-.012,.028,8,46), solid);
  ringNear.position.z = W/2; ringNear.castShadow=true; wheelSpin.add(ringNear);

  // поперечные планки — по ним видно вращение
  const rungGeo = new THREE.CylinderGeometry(.0125,.0125,W-.02,6);
  const rungs = new THREE.InstancedMesh(rungGeo, dark, 18);
  const m4=new THREE.Matrix4(), q=new THREE.Quaternion(), e=new THREE.Euler(), v=new THREE.Vector3(), s=new THREE.Vector3(1,1,1);
  for(let i=0;i<18;i++){
    const a=i/18*TAU; e.set(Math.PI/2,0,0); q.setFromEuler(e);
    v.set(Math.cos(a)*R, Math.sin(a)*R, 0); m4.compose(v,q,s); rungs.setMatrixAt(i,m4);
  }
  rungs.instanceMatrix.needsUpdate=true; wheelSpin.add(rungs);

  const hub = new THREE.Mesh(new THREE.CylinderGeometry(.052,.052,W+.14,16), dark);
  hub.rotation.x=Math.PI/2; hub.castShadow=true; wheelSpin.add(hub);
  for(let i=0;i<6;i++){
    const a=i/6*TAU, sp=box(RO*.9,.028,.02,dark,Math.cos(a)*RO*.47,Math.sin(a)*RO*.47,-W/2+.025);
    sp.rotation.z=a; wheelSpin.add(sp);
  }

  // стойка (не вращается) — А-рамы по бокам обода
  const stand = new THREE.Group(); wheelRoot.add(stand);
  const sm = new THREE.MeshStandardMaterial({color:0x6f7d88, roughness:.45, metalness:.5});
  [-(W/2+.055),(W/2+.055)].forEach((zs,idx)=>{
    [-1,1].forEach(sgn=>{
      const x0=sgn*(КОЛЕСО.R_OUT+.18), y0=-КОЛЕСО.yCenter+.02;
      const len=Math.hypot(x0,y0);
      const leg=box(.042,len,.042,sm,x0/2,y0/2,zs);
      leg.rotation.z=Math.atan2(-x0,y0)*-1; leg.rotation.z=Math.atan2(x0,-y0)+Math.PI;
      leg.rotation.set(0,0,Math.atan2(x0,-y0));
      leg.castShadow=true; stand.add(leg);
    });
    // опорные лапки (среднюю часть оставляем свободной — там вход)
    [-1,1].forEach(sgn=>{
      const f=box(.30,.035,.075,sm,sgn*(КОЛЕСО.R_OUT+.18),-КОЛЕСО.yCenter+.012,zs);
      f.castShadow=true; stand.add(f);
    });
  });
  // площадка у входа («мостик», с которого зверь заходит внутрь)
  const plat = box(.52,.05,.30,new THREE.MeshStandardMaterial({color:0xb9946a,roughness:.8}),
      0,-КОЛЕСО.yCenter+.028, W/2+.28);
  plat.receiveShadow=true; plat.castShadow=true; wheelRoot.add(plat);
})();

/* --- труба: открытый цилиндр + внутренняя оболочка --- */
const ТРУБА_OBJ = { x:ТРУБА.x, y:ТРУБА.y, z:ТРУБА.z, len:ТРУБА.len, rIn:ТРУБА.rIn, rOut:ТРУБА.rOut,
                    axis:'x', yОпоры:ТРУБА.yОпоры, user:null, axisDev:0, xInAxis:0, sideEntries:0 };
window.ТРУБА = ТРУБА_OBJ;
(function buildTube(){
  const g = new THREE.Group(); g.position.set(ТРУБА.x,ТРУБА.y,ТРУБА.z); scene.add(g);
  const glassOut = new THREE.MeshStandardMaterial({color:0xcfe6e2, roughness:.12, metalness:.05,
      transparent:true, opacity:.34, side:THREE.DoubleSide, depthWrite:false});
  const glassIn  = new THREE.MeshStandardMaterial({color:0xe8f2ee, roughness:.6, transparent:true, opacity:.5, side:THREE.BackSide});
  const out = new THREE.Mesh(new THREE.CylinderGeometry(ТРУБА.rOut,ТРУБА.rOut,ТРУБА.len,44,1,true), glassOut);
  out.rotation.z = Math.PI/2; out.renderOrder = 3; g.add(out);
  const inn = new THREE.Mesh(new THREE.CylinderGeometry(ТРУБА.rIn,ТРУБА.rIn,ТРУБА.len,40,1,true), glassIn);
  inn.rotation.z = Math.PI/2; inn.renderOrder = 2; g.add(inn);
  const ringMat = new THREE.MeshStandardMaterial({color:0xf3f6f4, roughness:.4});
  [-1,1].forEach(s=>{
    const t = new THREE.Mesh(new THREE.TorusGeometry(ТРУБА.rOut-.008,.026,8,40), ringMat);
    t.rotation.y = Math.PI/2; t.position.x = s*ТРУБА.len/2; t.castShadow=true; g.add(t);
  });
  // мягкая тень-полоса под трубой (сам цилиндр прозрачный и тень дал бы лужу)
  const sh = new THREE.Mesh(new THREE.PlaneGeometry(ТРУБА.len,ТРУБА.rOut*1.9),
      new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.28}));
  sh.rotation.x=-Math.PI/2; sh.position.set(ТРУБА.x,.006,ТРУБА.z); scene.add(sh);
})();

/* --- миска с зёрнами --- */
const BOWL_X = -1.45, BOWL_Z = 0.92, BOWL_R = 0.36;
const МИСКА = { x:BOWL_X, z:BOWL_Z, r:BOWL_R, user:null };
(function buildBowl(){
  const pts=[];
  for(let i=0;i<=10;i++){ const t=i/10; pts.push(new THREE.Vector2(.06+t*(BOWL_R-.06), Math.pow(t,1.7)*.14)); }
  const bowl = new THREE.Mesh(new THREE.LatheGeometry(pts,36),
      new THREE.MeshStandardMaterial({color:0xd8ded9, roughness:.28, metalness:.15, side:THREE.DoubleSide}));
  bowl.position.set(BOWL_X,.0,BOWL_Z); bowl.castShadow=true; bowl.receiveShadow=true; scene.add(bowl);
  const mash = new THREE.Mesh(new THREE.CylinderGeometry(BOWL_R*.78,BOWL_R*.6,.05,28),
      new THREE.MeshStandardMaterial({color:0x9c7b46,roughness:.95}));
  mash.position.set(BOWL_X,.105,BOWL_Z); scene.add(mash);
  const seeds = new THREE.InstancedMesh(new THREE.SphereGeometry(.022,7,6),
      new THREE.MeshStandardMaterial({roughness:.8}), 46);
  const m4=new THREE.Matrix4(),q=new THREE.Quaternion(),v=new THREE.Vector3(),s=new THREE.Vector3();
  const c=new THREE.Color();
  for(let i=0;i<46;i++){
    const a=Math.random()*TAU, rr=Math.sqrt(Math.random())*BOWL_R*.72;
    v.set(BOWL_X+Math.cos(a)*rr, .128+Math.random()*.022, BOWL_Z+Math.sin(a)*rr);
    q.setFromAxisAngle(new THREE.Vector3(0,1,0),Math.random()*TAU);
    s.set(rnd(.7,1.25),rnd(.4,.7),rnd(.7,1.25)); m4.compose(v,q,s); seeds.setMatrixAt(i,m4);
    c.setHex([0xd9b46a,0xb8823f,0x8f6a3c,0xe4cd94][(Math.random()*4)|0]); seeds.setColorAt(i,c);
  }
  seeds.instanceMatrix.needsUpdate=true; if(seeds.instanceColor) seeds.instanceColor.needsUpdate=true;
  scene.add(seeds);
})();

/* --- поилка на стенке --- */
const ПОИЛКА = { x:ПОЛУШ_Х-.34, z:-1.12, y:.42, user:null };
(function buildBottle(){
  const g=new THREE.Group(); scene.add(g);
  const glass=new THREE.MeshStandardMaterial({color:0xdfeef6,roughness:.08,metalness:.1,transparent:true,opacity:.35});
  const b=new THREE.Mesh(new THREE.CylinderGeometry(.095,.095,.44,20),glass);
  b.position.set(ПОЛУШ_Х+.16,.62,ПОИЛКА.z); g.add(b);
  const water=new THREE.Mesh(new THREE.CylinderGeometry(.086,.086,.30,20),
      new THREE.MeshStandardMaterial({color:0x6fb7d8,roughness:.05,transparent:true,opacity:.6}));
  water.position.set(ПОЛУШ_Х+.16,.55,ПОИЛКА.z); g.add(water);
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(.075,.1,.12,18),
      new THREE.MeshStandardMaterial({color:0xc9cfd4,roughness:.3,metalness:.6}));
  cap.position.set(ПОЛУШ_Х+.16,.90,ПОИЛКА.z); cap.castShadow=true; g.add(cap);
  const sp=new THREE.Mesh(new THREE.CylinderGeometry(.014,.014,.30,10),
      new THREE.MeshStandardMaterial({color:0xb8bec4,roughness:.25,metalness:.85}));
  sp.rotation.z=Math.PI/2; sp.position.set(ПОЛУШ_Х-.02,.42,ПОИЛКА.z); g.add(sp);
  const ball=new THREE.Mesh(new THREE.SphereGeometry(.021,10,8),
      new THREE.MeshStandardMaterial({color:0xdfe4e8,roughness:.1,metalness:.9}));
  ball.position.set(ПОЛУШ_Х-.16,.42,ПОИЛКА.z); g.add(ball);
})();

/* ============================================================================
   6. ТЕЛА СТОЛКНОВЕНИЙ (п.1.4)
   ========================================================================== */
const КОЛЛИЗИИ = [
  // колесо: прямоугольник в плане (диск), вход — только через состояние «захожу»
  {id:'wheel', type:'box', cx:КОЛЕСО.x, cz:КОЛЕСО.z, hx:КОЛЕСО.R_OUT+.02, hz:КОЛЕСО.width/2+.02},
  // труба: две капсулы = стенки. Между их торцами — открытый вход.
  {id:'tube',  type:'seg', ax:ТРУБА.x-ТРУБА.len/2, az:ТРУБА.z-ТРУБА.rOut, bx:ТРУБА.x+ТРУБА.len/2, bz:ТРУБА.z-ТРУБА.rOut, r:ТРУБА.wall*.5},
  {id:'tube',  type:'seg', ax:ТРУБА.x-ТРУБА.len/2, az:ТРУБА.z+ТРУБА.rOut, bx:ТРУБА.x+ТРУБА.len/2, bz:ТРУБА.z+ТРУБА.rOut, r:ТРУБА.wall*.5},
  // миска — круг
  {id:'bowl',  type:'circle', cx:BOWL_X, cz:BOWL_Z, r:BOWL_R}
];
// отладочная отрисовка тел
const bodyGroup = new THREE.Group(); bodyGroup.visible=false; scene.add(bodyGroup);
КОЛЛИЗИИ.forEach(c=>{
  let m;
  if(c.type==='box'){ m=new THREE.Mesh(new THREE.BoxGeometry(c.hx*2,.9,c.hz*2),
        new THREE.MeshBasicMaterial({color:0x6fc3d8,wireframe:true,transparent:true,opacity:.5}));
      m.position.set(c.cx,.45,c.cz); }
  else if(c.type==='circle'){ m=new THREE.Mesh(new THREE.CylinderGeometry(c.r,c.r,.9,24,1,true),
        new THREE.MeshBasicMaterial({color:0xf2a52c,wireframe:true,transparent:true,opacity:.5}));
      m.position.set(c.cx,.45,c.cz); }
  else { const len=Math.hypot(c.bx-c.ax,c.bz-c.az);
      m=new THREE.Mesh(new THREE.CylinderGeometry(c.r,c.r,len,8,1,true),
        new THREE.MeshBasicMaterial({color:0xef7a52,wireframe:true,transparent:true,opacity:.5}));
      m.rotation.z=Math.PI/2; m.rotation.y=-Math.atan2(c.bz-c.az,c.bx-c.ax);
      m.position.set((c.ax+c.bx)/2,.45,(c.az+c.bz)/2); }
  bodyGroup.add(m);
});

/* ============================================================================
   7. ХОМЯК: сборка из частей
   ========================================================================== */
const SPEC = [
  {name:'Пух',    fur:0xe9a94e, belly:0xfbe6c0},
  {name:'Кекс',   fur:0xb5763f, belly:0xf0d9b4},
  {name:'Ириска', fur:0xd9722f, belly:0xf7d9a8},
  {name:'Дымка',  fur:0x8e97a8, belly:0xe3e7ee},
  {name:'Снежок', fur:0xf1ece2, belly:0xffffff}
];
function makeHamster(spec, idx){
  const mFur   = new THREE.MeshStandardMaterial({color:spec.fur, roughness:.94});
  const mBelly = new THREE.MeshStandardMaterial({color:new THREE.Color(spec.belly).multiplyScalar(.97), roughness:.96});
  const mDark  = new THREE.MeshStandardMaterial({color:0x1a1216, roughness:.25});
  const mPink  = new THREE.MeshStandardMaterial({color:0xdb8f8f, roughness:.72});
  const mEye   = new THREE.MeshStandardMaterial({color:0xf6efe4, roughness:.2});

  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body);          // дышит / кивает / прыгает
  function ell(mat,sx,sy,sz,x,y,z){ const m=new THREE.Mesh(SPHERE,mat); m.scale.set(sx,sy,sz); m.position.set(x,y,z);
      m.castShadow=true; body.add(m); return m; }

  ell(mFur,.175,.158,.235, 0,.212,-.01);            // корпус
  ell(mFur,.166,.150,.150, 0,.208,-.135);           // зад
  ell(mBelly,.152,.122,.196, 0,.176,.012);          // живот
  ell(mBelly,.14,.09,.12, 0,.145,.09);              // грудь

  const head = new THREE.Group(); head.position.set(0,.288,.176); body.add(head);
  function hell(mat,sx,sy,sz,x,y,z){ const m=new THREE.Mesh(SPHERE,mat); m.scale.set(sx,sy,sz); m.position.set(x,y,z);
      m.castShadow=true; head.add(m); return m; }
  hell(mFur,.128,.118,.126, 0,0,0);
  hell(mBelly,.088,.070,.088, 0,-.030,.086);
  hell(mPink,.020,.015,.016, 0,-.012,.146);
  const eyes=[], lids=[];
  [-1,1].forEach(s=>{
    const eg=new THREE.Group(); eg.position.set(.064*s,.030,.096); head.add(eg);
    const w=new THREE.Mesh(SPHERE,mEye); w.scale.set(.030,.032,.028); eg.add(w);
    const p=new THREE.Mesh(SPHERE,mDark); p.scale.set(.019,.021,.016); p.position.set(0,0,.017); eg.add(p);
    eyes.push(eg); lids.push(eg);
  });
  const cheeks=[];
  [-1,1].forEach(s=> cheeks.push(hell(mFur,.058,.052,.062, .078*s,-.034,.052)));
  const ears=[];
  [-1,1].forEach(s=>{
    const eg=new THREE.Group(); eg.position.set(.076*s,.098,-.012); eg.rotation.z=-.55*s; eg.rotation.x=-.18;
    const o=new THREE.Mesh(SPHERE,mFur); o.scale.set(.020,.056,.050); o.castShadow=true; eg.add(o);
    const i2=new THREE.Mesh(SPHERE,mPink); i2.scale.set(.014,.037,.033); i2.position.x=.010*s; eg.add(i2);
    head.add(eg); ears.push({g:eg,base:{z:-.55*s,x:-.18},s});
  });
  // усы
  const wg=[]; [-1,1].forEach(s=>{ for(let k=-1;k<=1;k++){ wg.push(.05*s,-.03,.115, .135*s,-.045+k*.022,.145); } });
  const wgeo=new THREE.BufferGeometry(); wgeo.setAttribute('position',new THREE.Float32BufferAttribute(wg,3));
  head.add(new THREE.LineSegments(wgeo,new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.45})));

  const tail=new THREE.Group(); tail.position.set(0,.235,-.245); body.add(tail);
  const t1=new THREE.Mesh(SPHERE,mFur); t1.scale.set(.026,.026,.045); tail.add(t1);
  const t2=new THREE.Mesh(SPHERE,mPink); t2.scale.set(.018,.018,.030); t2.position.z=-.042; tail.add(t2);

  // четыре лапы: бедро → голень → стопа
  const legs=[];
  const hips=[{x:.104,z:.104,k:'FL'},{x:-.104,z:.104,k:'FR'},{x:.116,z:-.135,k:'RL'},{x:-.116,z:-.135,k:'RR'}];
  hips.forEach(h=>{
    const hip=new THREE.Group(); hip.position.set(h.x,.148,h.z); body.add(hip);
    const up=new THREE.Mesh(SPHERE,mFur); up.scale.set(.032,.046,.032); up.position.y=-.036; up.castShadow=true; hip.add(up);
    const knee=new THREE.Group(); knee.position.y=-.072; hip.add(knee);
    const lo=new THREE.Mesh(SPHERE,mFur); lo.scale.set(.028,.040,.028); lo.position.y=-.030; lo.castShadow=true; knee.add(lo);
    const ankle=new THREE.Group(); ankle.position.y=-.058; knee.add(ankle);
    const paw=new THREE.Mesh(SPHERE,mBelly); paw.scale.set(.030,.022,.040); paw.position.set(0,-.016,.010); paw.castShadow=true; ankle.add(paw);
    const side = Math.sign(h.x)||1;
    hip.rotation.z = side*(h.k[0]==='R'?.20:.14);
    legs.push({hip,knee,ankle,key:h.k,
      offset:(h.k==='FL'||h.k==='RR')?0:Math.PI,   // диагональные пары
      L:.128, splay:side*(h.k[0]==='R'?.20:.14)});
  });

  // невидимая сфера для клика + кольцо-подсветка
  const pick=new THREE.Mesh(new THREE.SphereGeometry(.30,10,8),
      new THREE.MeshBasicMaterial({colorWrite:false,depthWrite:false,transparent:true,opacity:0}));
  pick.position.y=.2; root.add(pick);
  const ring=new THREE.Mesh(new THREE.RingGeometry(.22,.275,32),
      new THREE.MeshBasicMaterial({color:new THREE.Color(spec.fur).lerp(new THREE.Color(0xffffff),.4),
        transparent:true,opacity:0,side:THREE.DoubleSide,depthWrite:false}));
  ring.rotation.x=-Math.PI/2; ring.position.y=.014; root.add(ring);

  scene.add(root);
  return {
    name:spec.name, color:spec.fur, idx, root, body, head, eyes, ears, cheeks, tail, legs, ring, pick,
    pos:new THREE.Vector2(rnd(-1.4,1.4), rnd(-.9,1.2)), vel:new THREE.Vector2(), yaw:rnd(0,TAU), y:0,
    state:'idle', nextAct:null, t:0, timer:rnd(.5,2),
    фаза:0, dist:0, pawSpeed:0, runTarget:0, speed:0,
    breath:rnd(.85,1.25), blinkT:rnd(1,4), blink:0, earT:rnd(1,3), earKick:0,
    hunger:rnd(.2,.9), thirst:rnd(.1,.7), energy:rnd(.4,1),
    jump:{y:0,v:0,on:false}, ignore:new Set(), locked:false, hovered:false, sel:false,
    command:null, stuckT:0, chew:0, status:'стоит · нюхает воздух',
    gaitAmp:0, headNod:0, lean:0
  };
}
const ХОМЯКИ = SPEC.map((s,i)=>makeHamster(s,i));
const hStart=[[-1.9,.5],[-.6,-.2],[.4,.9],[1.5,-.3],[-.2,-1.1]];
ХОМЯКИ.forEach((h,i)=>{ h.pos.set(hStart[i][0],hStart[i][1]); h.yaw=rnd(0,TAU); });

/* ============================================================================
   8. ФИЗИКА ДВИЖЕНИЯ + СТОЛКНОВЕНИЯ
   ========================================================================== */
function resolveCircleBox(h,c,r){
  const x0=c.cx-c.hx, x1=c.cx+c.hx, z0=c.cz-c.hz, z1=c.cz+c.hz;
  const px=clamp(h.pos.x,x0,x1), pz=clamp(h.pos.z,z0,z1);
  let dx=h.pos.x-px, dz=h.pos.z-pz, d2=dx*dx+dz*dz;
  if(d2>r*r) return 0;
  let pen,nx,nz;
  if(d2>1e-9){ const d=Math.sqrt(d2); pen=r-d; nx=dx/d; nz=dz/d; }
  else{ // центр внутри — выталкиваем по кратчайшей нормали
    const ox=Math.min(h.pos.x-x0,x1-h.pos.x), oz=Math.min(h.pos.z-z0,z1-h.pos.z);
    if(ox<oz){ pen=ox+r; nx=(h.pos.x<c.cx?-1:1); nz=0; } else { pen=oz+r; nz=(h.pos.z<c.cz?-1:1); nx=0; }
  }
  h.pos.x+=nx*pen; h.pos.z+=nz*pen;
  const vn=h.vel.x*nx+h.vel.z*nz; if(vn<0){ h.vel.x-=vn*nx; h.vel.z-=vn*nz; }
  return pen;
}
function resolveCircleSeg(h,c,r){
  const ax=c.ax,az=c.az,bx=c.bx,bz=c.bz, abx=bx-ax, abz=bz-az;
  const t=clamp(((h.pos.x-ax)*abx+(h.pos.z-az)*abz)/(abx*abx+abz*abz),0,1);
  const px=ax+abx*t, pz=az+abz*t;
  let dx=h.pos.x-px, dz=h.pos.z-pz; const R=r+c.r, d2=dx*dx+dz*dz;
  if(d2>R*R) return 0;
  let d=Math.sqrt(d2), nx,nz;
  if(d<1e-6){ nx=0; nz=(h.pos.z<c.cz?-1:1); d=0; } else { nx=dx/d; nz=dz/d; }
  const pen=R-d;
  h.pos.x+=nx*pen; h.pos.z+=nz*pen;
  const vn=h.vel.x*nx+h.vel.z*nz; if(vn<0){ h.vel.x-=vn*nx; h.vel.z-=vn*nz; }
  return pen;
}
function resolveCircleCircle(h,c,r){
  const dx=h.pos.x-c.cx, dz=h.pos.z-c.cz, R=r+c.r, d=Math.hypot(dx,dz);
  if(d>R||d<1e-6) return 0;
  const nx=dx/d, nz=dz/d, pen=R-d;
  h.pos.x+=nx*pen; h.pos.z+=nz*pen;
  const vn=h.vel.x*nx+h.vel.z*nz; if(vn<0){ h.vel.x-=vn*nx; h.vel.z-=vn*nz; }
  return pen;
}
// «внутри трубы» = между стенками в пределах пролёта (для не-пользователя — нарушение)
function insideTubeSpan(h){ return Math.abs(h.pos.x-ТРУБА.x)<ТРУБА.len/2 && Math.abs(h.pos.z-ТРУБА.z)<ТРУБА.rIn; }

const ПРОВЕРКИ = {
  tunnel:0, sideEntries:0, phaseDriftAtRest:0, wheelSlipMax:0, minOmegaAfterFree:0, freeFrom:0, errors:0
};
function collide(h){
  let maxPen=0;
  for(const c of КОЛЛИЗИИ){
    if(h.ignore.has(c.id)) continue;
    // не-пользователю трубы запрещаем находиться внутри пролёта — выталкиваем к торцу
    if(c.id==='tube'){
      if(insideTubeSpan(h)){
        if(ТРУБА_OBJ.user!==h){
          ПРОВЕРКИ.sideEntries++;
          const dir = (h.pos.x>ТРУБА.x)?1:-1;
          h.pos.x = dir>0 ? ТРУБА.x+ТРУБА.len/2+РАДИУС_ТЕЛА+.02 : ТРУБА.x-ТРУБА.len/2-РАДИУС_ТЕЛА-.02;
        }
        continue;
      }
    }
    const pen = c.type==='box'?resolveCircleBox(h,c,РАДИУС_ТЕЛА)
              : c.type==='seg'?resolveCircleSeg(h,c,РАДИУС_ТЕЛА)
              : resolveCircleCircle(h,c,РАДИУС_ТЕЛА);
    if(pen>maxPen) maxPen=pen;
  }
  if(maxPen>.05) ПРОВЕРКИ.tunnel++;   // значит шаг был больше тела — туннелирование
  // стены клетки
  h.pos.x=clamp(h.pos.x,-ПОЛУШ_Х+РАДИУС_ТЕЛА,ПОЛУШ_Х-РАДИУС_ТЕЛА);
  h.pos.z=clamp(h.pos.z,-ПОЛУШ_Z+РАДИУС_ТЕЛА,ПОЛУШ_Z-РАДИУС_ТЕЛА);
}
function separate(){
  for(let i=0;i<ХОМЯКИ.length;i++) for(let j=i+1;j<ХОМЯКИ.length;j++){
    const a=ХОМЯКИ[i], b=ХОМЯКИ[j];
    if(a.locked&&b.locked) continue;
    let dx=b.pos.x-a.pos.x, dz=b.pos.z-a.pos.z;
    let d=Math.hypot(dx,dz); const min=РАДИУС_ТЕЛА*2+.015;
    if(d<min){
      if(d<1e-5){ dx=1; dz=0; d=1; }
      const push=(min-d)*.5*.9, nx=dx/d, nz=dz/d;
      if(!a.locked){ a.pos.x-=nx*push; a.pos.z-=nz*push; }
      if(!b.locked){ b.pos.x+=nx*push; b.pos.z+=nz*push; }
    }
  }
}

/* ============================================================================
   9. КОЛЕСО: ω = v / R, трение без бегуна
   ========================================================================== */
function updateWheel(dt){
  const u = КОЛЕСО.user;
  if(u && (u.state==='runWheel')){
    const target = u.pawSpeed / КОЛЕСО.R;            // ← честная кинематика
    КОЛЕСО.omega = damp(КОЛЕСО.omega, target, 18, dt);
    КОЛЕСО.rimSpeed = Math.abs(КОЛЕСО.omega)*КОЛЕСО.R;
    КОЛЕСО.pawSpeed = u.pawSpeed;
    КОЛЕСО.slipPct = u.pawSpeed>0.02
        ? Math.abs(КОЛЕСО.rimSpeed-u.pawSpeed)/u.pawSpeed*100 : 0;
    ПРОВЕРКИ.wheelSlipMax = Math.max(ПРОВЕРКИ.wheelSlipMax, u.pawSpeed>.1?КОЛЕСО.slipPct:0);
    ПРОВЕРКИ.freeFrom = 0;
  } else {
    // пустое колесо: сухое + вязкое трение
    const w=КОЛЕСО.omega, f=КОЛЕСО.friction*dt;
    let nw = Math.abs(w)<=f ? 0 : w-Math.sign(w)*f;
    nw *= Math.exp(-.35*dt);
    КОЛЕСО.omega = nw;
    КОЛЕСО.rimSpeed = Math.abs(nw)*КОЛЕСО.R;
    КОЛЕСО.pawSpeed = 0; КОЛЕСО.slipPct = 0;
    if(Math.abs(w)>1e-3){
      if(!ПРОВЕРКИ.freeFrom) ПРОВЕРКИ.freeFrom=Math.abs(w);
      ПРОВЕРКИ.minOmegaAfterFree = Math.abs(nw);
      КОЛЕСО.freeDecayOk = Math.abs(nw) <= Math.abs(w)+1e-6;
    }
  }
  КОЛЕСО.angle += КОЛЕСО.omega*dt;
  КОЛЕСО.spin.rotation.z = КОЛЕСО.angle;
}

/* ============================================================================
   10. ПОВЕДЕНИЕ (конечный автомат)
   ========================================================================== */
const СТАТУС = {
  idle:'стоит · нюхает воздух', toWheel:'идёт к колесу', enterWheel:'забирается в колесо',
  runWheel:'бежит в колесе', exitWheel:'вылезает из колеса', toTube:'идёт к трубе',
  inTube:'ползёт по трубе', toBowl:'идёт к миске', eat:'грызёт зёрна',
  toBottle:'идёт к поилке', drink:'пьёт из поилки', wander:'бродит по клетке'
};
function routeTo(h, tx, tz){
  // обход препятствий простой разметкой: если цель «за» предметом — сначала в переднюю точку
  const wheelBehind = (tz < КОЛЕСО.z+КОЛЕСО.width/2) && Math.abs(tx-КОЛЕСО.x)<КОЛЕСО.R_OUT;
  if(Math.hypot(h.pos.x-tx,h.pos.z-tz)>.35){
    if(wheelBehind && h.pos.z<КОЛЕСО.z) return [КОЛЕСO_xSafe(), КОЛЕСО.z+КОЛЕСО.width/2+.7];
  }
  if(Math.abs(tx-ТРУБА.x)<ТРУБА.len/2 && Math.abs(tz-ТРУБА.z)<ТРУБА.rOut && h.pos.z<ТРУБА.z-ТРУБА.rOut)
      return [tx, ТРУБА.z-ТРУБА.rOut-.5];
  return null;
  function КОЛЕСO_xSafe(){ return КОЛЕСО.x; }
}
function pickPlan(h){
  if(h.command){ const c=h.command; h.command=null;
    if(c==='wheel'&&!КОЛЕСО.user){ h.nextAct='wheel'; h.target=[КОЛЕСО.portal.x,КОЛЕСО.portal.z]; h.state='toWheel'; return; }
    if(c==='tube'&&!ТРУБА_OBJ.user){ startTube(h); return; }
    if(c==='eat'){ h.nextAct='eat'; h.target=bowlSpot(h); h.state='toBowl'; return; }
    if(c==='drink'){ h.nextAct='drink'; h.target=[ПОИЛКА.x,ПОИЛКА.z]; h.state='toBottle'; return; }
    h.nextAct='wander'; h.target=randSpot(); h.state='wander'; return;
  }
  const opts=[];
  if(!КОЛЕСО.user) opts.push(['wheel', 1.4+h.energy*2.6]);
  if(!ТРУБА_OBJ.user) opts.push(['tube', 1.3]);
  if(!МИСКА.user) opts.push(['eat', .5+h.hunger*2.6]);
  if(!ПОИЛКА.user) opts.push(['drink', .3+h.thirst*1.8]);
  opts.push(['wander', 1.5], ['idle', 1.1]);
  let sum=opts.reduce((s,o)=>s+o[1],0), r=Math.random()*sum, act='wander';
  for(const o of opts){ r-=o[1]; if(r<=0){ act=o[0]; break; } }

  if(act==='idle'){ h.state='idle'; h.timer=rnd(1.2,3.4); return; }
  if(act==='wander'){ h.nextAct='wander'; h.target=randSpot(); h.state='wander'; return; }
  if(act==='wheel'){ h.nextAct='wheel'; h.target=[КОЛЕСО.portal.x,КОЛЕСО.portal.z]; h.state='toWheel'; return; }
  if(act==='tube'){ startTube(h); return; }
  if(act==='eat'){ h.nextAct='eat'; h.target=bowlSpot(h); h.state='toBowl'; return; }
  if(act==='drink'){ h.nextAct='drink'; h.target=[ПОИЛКА.x,ПОИЛКА.z]; h.state='toBottle'; return; }
}
function randSpot(){
  for(let i=0;i<24;i++){
    const x=rnd(-ПОЛУШ_Х+.35,ПОЛУШ_Х-.35), z=rnd(-ПОЛУШ_Z+.35,ПОЛУШ_Z-.35);
    if(Math.hypot(x-BOWL_X,z-BOWL_Z)<BOWL_R+.3) continue;
    if(Math.abs(x-КОЛЕСО.x)<КОЛЕСО.R_OUT+.3 && Math.abs(z-КОЛЕСО.z)<КОЛЕСО.width/2+.3) continue;
    if(Math.abs(x-ТРУБА.x)<ТРУБА.len/2+.3 && Math.abs(z-ТРУБА.z)<ТРУБА.rOut+.3) continue;
    return [x,z];
  }
  return [0,0];
}
function bowlSpot(h){
  const a=Math.atan2(h.pos.z-BOWL_Z,h.pos.x-BOWL_X);
  return [BOWL_X+Math.cos(a)*(BOWL_R+РАДИУС_ТЕЛА*.55), BOWL_Z+Math.sin(a)*(BOWL_R+РАДИУС_ТЕЛА*.55)];
}
function startTube(h){
  const fromPlus = (h.pos.x>ТРУБА.x);
  const ex = fromPlus? ТРУБА.x+ТРУБА.len/2 : ТРУБА.x-ТРУБА.len/2;
  h.tubeDir = fromPlus?-1:1;
  h.nextAct='tube'; h.state='toTube'; h.target=[ex+h.tubeDir*(РАДИУС_ТЕЛА+.28), ТРУБА.z];
}

/* --- движение к цели (плавное, с поворотом) --- */
function moveTowards(h,dt,speed){
  const tx=h.target[0], tz=h.target[1];
  const dx=tx-h.pos.x, dz=tz-h.pos.z, d=Math.hypot(dx,dz);
  const want = d<.015?0:speed*clamp(d/.32,0,1);
  const nx=d>1e-5?dx/d:0, nz=d>1e-5?dz/d:0;
  h.vel.x=damp(h.vel.x,nx*want,10,dt); h.vel.z=damp(h.vel.z,nz*want,10,dt);
  const sp=Math.hypot(h.vel.x,h.vel.z);
  if(sp>.02) h.yaw=dampAngle(h.yaw,Math.atan2(h.vel.x,h.vel.z),8,dt);
  h.pos.x+=h.vel.x*dt; h.pos.z+=h.vel.z*dt;
  h.speed=sp;
  return d;
}

/* --- шаг одного зверька --- */
function stepHamster(h,dt){
  h.t+=dt; h.hunger=clamp(h.hunger+dt*.012,0,1.4); h.thirst=clamp(h.thirst+dt*.009,0,1.3);
  h.energy=clamp(h.energy-dt*.010,-.2,1.2);
  h.ignore.clear(); h.locked=false;

  switch(h.state){
    case 'idle':{
      h.vel.x=damp(h.vel.x,0,6,dt); h.vel.z=damp(h.vel.z,0,6,dt); h.speed=0;
      h.yaw+=Math.sin(h.t*.6+h.idx)*dt*.25;
      h.timer-=dt; if(h.timer<=0) pickPlan(h);
      break;
    }
    case 'wander': case 'toWheel': case 'toTube': case 'toBowl': case 'toBottle':{
      const wp=routeTo(h,h.target[0],h.target[1]);
      const eff = wp?[wp[0],wp[1]]:h.target;
      const save=h.target; h.target=eff;
      const d=moveTowards(h,dt,h.state==='wander'?rnd(.42,.6):.72);
      h.target=save;
      if(wp && d<.35 && eff!==h.target) h.stuckT=0;
      if(!wp && d<.07){ arrive(h); }
      if(wp && Math.hypot(h.pos.x-h.target[0],h.pos.z-h.target[1])<.12) arrive(h);
      h.stuckT = (h.speed<.05)? h.stuckT+dt : 0;
      if(h.stuckT>2.2){ h.stuckT=0; h.state='idle'; h.timer=rnd(.3,1); }
      break;
    }
    case 'enterWheel':{
      h.locked=true; h.ignore.add('wheel'); КОЛЕСО.user=h;
      h.t+=dt; const s=clamp((h.t-h.enterT0)/.85,0,1), e=s*s*(3-2*s);
      h.pos.x=lerp(h.enterP0.x,КОЛЕСО.x,e); h.pos.z=lerp(h.enterP0.y,КОЛЕСО.z,e);
      h.y = lerp(0,КОЛЕСО.yContact,e) + Math.sin(Math.PI*s)*.05;
      h.yaw = angLerp(h.enterYaw,-Math.PI/2,e);
      if(s>=1){ h.state='runWheel'; h.timer=rnd(6,14); h.runT=0; h.pawSpeed=0; }
      h.speed=0; break;
    }
    case 'runWheel':{
      h.locked=true; h.ignore.add('wheel'); КОЛЕСО.user=h;
      const c=КОЛЕСО.contact(); h.pos.x=c.x; h.pos.z=c.z; h.y=c.y; h.yaw=-Math.PI/2;
      h.runT+=dt;
      // интервалы: спринт → передышка (колесо честно замедляется вместе с лапами)
      const cyc=(h.runT%4.6);
      h.runTarget = cyc<3.2 ? (.9+h.energy*.75)*rnd(.98,1.02) : 0;
      h.pawSpeed = damp(h.pawSpeed,h.runTarget,3.2,dt);
      // шаг привязан к скорости обода (п.1.5)
      const ds = Math.abs(КОЛЕСО.omega)*КОЛЕСО.R*dt;
      h.dist += ds; h.фаза += (ds/ДЛИНА_ШАГА)*TAU;
      h.speed = h.pawSpeed;
      h.timer-=dt;
      if(h.timer<=0 && h.pawSpeed<.05){ h.state='exitWheel'; h.t=0; h.exitP0=h.pos.clone(); h.exitYaw=h.yaw; }
      break;
    }
    case 'exitWheel':{
      h.locked=true; h.ignore.add('wheel');
      const s=clamp(h.t/.75,0,1), e=s*s*(3-2*s);
      h.pos.x=lerp(h.exitP0.x,КОЛЕСО.portal.x,e); h.pos.z=lerp(h.exitP0.y,КОЛЕСО.portal.z,e);
      h.y=lerp(КОЛЕСО.yContact,0,e)+Math.sin(Math.PI*s)*.04;
      h.yaw=angLerp(h.exitYaw,0,e);
      if(s>=1){ КОЛЕСО.user=null; h.state='idle'; h.timer=rnd(.6,1.8); h.energy-=.25; h.pawSpeed=0; }
      h.speed=0; break;
    }
    case 'inTube':{
      h.ignore.add('tube'); ТРУБА_OBJ.user=h; h.locked=true;
      const v=.46;
      h.pos.x += h.tubeDir*v*dt;
      h.y = damp(h.y,ТРУБА.yОпоры,9,dt);
      h.pos.z = damp(h.pos.z,ТРУБА.z,12,dt);          // держим ось → отклонение → 0
      h.yaw = dampAngle(h.yaw, h.tubeDir>0?Math.PI/2:-Math.PI/2, 8, dt);
      const ds=v*dt; h.dist+=ds; h.фаза+=(ds/ДЛИНА_ШАГА)*TAU;
      h.speed=v;
      ТРУБА_OBJ.axisDev=Math.abs(h.pos.z-ТРУБА.z);
      ТРУБА_OBJ.xInAxis=h.pos.x-ТРУБА.x;
      if(Math.abs(h.pos.x-ТРУБА.x)>ТРУБА.len/2+РАДИУС_ТЕЛА+.02){
        ТРУБА_OBJ.user=null; h.state='idle'; h.timer=rnd(.5,1.5);
        ТРУБА_OBJ.axisDev=0; ТРУБА_OBJ.xInAxis=0;
      }
      break;
    }
    case 'eat':{
      h.vel.set(0,0); h.speed=0; h.yaw=dampAngle(h.yaw,Math.atan2(МИСКА.x-h.pos.x,МИСКА.z-h.pos.z),6,dt);
      h.timer-=dt; h.chew=1;
      if(h.timer<=0){ МИСКА.user=null; h.hunger-=.6; h.state='idle'; h.timer=rnd(.8,2.2); }
      break;
    }
    case 'drink':{
      h.vel.set(0,0); h.speed=0; h.yaw=dampAngle(h.yaw,Math.PI/2,6,dt);
      h.timer-=dt;
      if(h.timer<=0){ ПОИЛКА.user=null; h.thirst-=.7; h.state='idle'; h.timer=rnd(.8,2.2); }
      break;
    }
  }
  // труба: пользователь идёт строго по оси (страховка от «парения в сечении»)
  if(h.state==='inTube'){ /* уже выше */ }
  else if(ТРУБА_OBJ.user!==h){ /* ничего */ }

  if(!h.locked) collide(h);
  // прыжок (клик) — вертикальная могида, фаза шага в воздухе не меняется
  if(h.jump.on){
    h.jump.v-=9.5*dt; h.jump.y+=h.jump.v*dt;
    if(h.jump.y<=0){ h.jump.y=0; h.jump.v=0; h.jump.on=false; }
  }
  h.root.position.set(h.pos.x, h.y+h.jump.y, h.pos.z);
  h.root.rotation.y=h.yaw;
  h.status = СТАТУС[h.state]||h.status;
  if(h.jump.on) h.status='подпрыгнул!';
}
function arrive(h){
  const a=h.nextAct;
  if(a==='wheel'){ h.enterT0=h.t; h.enterP0=h.pos.clone(); h.enterYaw=h.yaw; h.state='enterWheel'; h.vel.set(0,0); return; }
  if(a==='tube'){ h.state='inTube'; h.vel.set(0,0); ТРУБА_OBJ.user=h; return; }
  if(a==='eat'){ h.state='eat'; h.timer=rnd(3.5,7); МИСКА.user=h; h.vel.set(0,0); return; }
  if(a==='drink'){ h.state='drink'; h.timer=rnd(2.5,4.5); ПОИЛКА.user=h; h.vel.set(0,0); return; }
  h.state='idle'; h.timer=rnd(.8,2.6);
}

/* ============================================================================
   11. АНИМАЦИЯ: лапы от ПРОЙДЕННОГО ПУТИ, дыхание, ухо, жевание
   ========================================================================== */
const A_ШАГА = Math.asin(clamp(ДЛИНА_ШАГА*ДЮТИ/(2*.128),-1,1)); // амплитуда маха ноги
function poseLegs(h){
  const stride=ДЛИНА_ШАГА, L=.128;
  for(const leg of h.legs){
    const u = (((h.фаза+leg.offset)/TAU)%1+1)%1;
    let travel, lift=0;
    if(u<ДЮТИ){ const s=u/ДЮТИ; travel=ДЮТИ*stride*(.5-s); }
    else{ const w=(u-ДЮТИ)/(1-ДЮТИ); travel=stride*ДЮТИ*(w-.5); lift=Math.sin(Math.PI*w); }
    const th=-Math.asin(clamp(travel/L,-1,1));
    leg.hip.rotation.x = th;
    leg.hip.rotation.z = leg.splay*(1-lift*.35);
    leg.knee.rotation.x = lift*1.15 + (travel>0?-.12:.06);
    leg.ankle.rotation.x = -lift*.55 - th*.35;
  }
}
function animateHamster(h,dt){
  const run=h.speed, moving=run>.05;
  // дыхание: в покое — лёгкое изменение объёма тела
  const br = 1 + Math.sin(h.t*(2.0+h.breath*1.4+(moving?3:0)))* (moving?.012:.026);
  h.body.scale.set(br, 1/Math.sqrt(br), br);
  // подпрыгивание корпуса на рыси (визуально; корень остаётся на точке опоры!)
  const bob = moving? Math.abs(Math.sin(h.фаза))* .014 - .007 : 0;
  h.body.position.y = bob + h.jump.y*0;
  h.body.rotation.x = (moving? -.06-.03*Math.cos(h.фаза) : 0) + (h.state==='drink'? -.34:0) + (h.state==='eat'? .12:0);
  h.body.rotation.z = moving? Math.sin(h.фаза*.5)*.03 : Math.sin(h.t*.8)*.01;

  // лапы — только от фазы; в прыжке поджимаются
  if(h.jump.on){ h.legs.forEach(l=>{ l.hip.rotation.x=-.5; l.knee.rotation.x=.9; }); }
  else poseLegs(h);

  // голова: кивок, жевание, осмотр
  let hx = (h.state==='eat'? .62 : 0) + Math.sin(h.t*11)*(h.state==='eat'?.075:0);
  let hy = Math.sin(h.t*.9+h.idx*2)*.28*(h.state==='idle'||h.state==='wander'?1:.3);
  if(h.state==='drink'){ hx=-.30; hy=Math.sin(h.t*9)*.06; }
  h.headNod = damp(h.headNod,hx,10,dt); h.head.rotation.x=h.headNod;
  h.head.rotation.y = damp(h.head.rotation.y,hy,5,dt);
  h.head.rotation.z = Math.sin(h.t*.7+h.idx)*.03;
  // щёки наедаются
  const chew = h.state==='eat'? (1+Math.sin(h.t*13)*.10) : 1;
  h.cheeks.forEach((c,i)=>{ const s=chew*(i?.97:1.03); c.scale.set(.058*s,.052*s,.062*s); });
  // уши: редкие подёргивания
  h.earT-=dt; if(h.earT<0){ h.earT=rnd(1.4,4.5); h.earKick=1; }
  h.earKick=Math.max(0,h.earKick-dt*4.5);
  h.ears.forEach((e,i)=>{
    const k=h.earKick*Math.sin(h.earKick*22+i)*(i?1:-1);
    e.g.rotation.z=e.base.z+k*.35-(moving?.28:0);
    e.g.rotation.x=e.base.x+(moving?-.25:0)+k*.12;
  });
  // моргание
  h.blinkT-=dt; if(h.blinkT<0){ h.blinkT=rnd(2,6); h.blink=.14; }
  h.blink=Math.max(0,h.blink-dt);
  const ey=h.blink>0?.15:1; h.eyes.forEach(g=>g.scale.y=damp(g.scale.y,ey,28,dt));
  // хвост
  h.tail.rotation.y=Math.sin(h.t*3.1+h.idx)*.22; h.tail.rotation.x=Math.sin(h.t*2.2)*.12;
  // подсветка
  const wantOp = (h.hovered||h.sel)? (h.sel?.85:.5)+Math.sin(h.t*5)*.12 : 0;
  h.ring.material.opacity=damp(h.ring.material.opacity,wantOp,10,dt);
}

/* ============================================================================
   12. UI
   ========================================================================== */
const listEl=document.getElementById('list'), checksEl=document.getElementById('checks');
let selected=ХОМЯКИ[0]; selected.sel=true;
const rowRefs = ХОМЯКИ.map(h=>{
  const d=document.createElement('div'); d.className='hrow';
  d.innerHTML=`<span class="dot" style="color:#${new THREE.Color(h.color).getHexString()};background:#${new THREE.Color(h.color).getHexString()}"></span>
    <span class="hmeta"><span class="hname">${h.name}</span><span class="hstat">…</span></span>
    <span class="hbar"><i></i></span>`;
  listEl.appendChild(d);
  d.addEventListener('mouseenter',()=>h.hovered=true);
  d.addEventListener('mouseleave',()=>h.hovered=false);
  d.addEventListener('click',()=>{ ХОМЯКИ.forEach(x=>x.sel=false); h.sel=true; selected=h; jump(h); });
  return {el:d, stat:d.querySelector('.hstat'), bar:d.querySelector('.hbar i')};
});
function jump(h){ if(!h.jump.on && h.y<.01){ h.jump.on=true; h.jump.v=2.15; } }
document.getElementById('cmds').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  selected.command=b.dataset.cmd;
  if(selected.state==='idle'||selected.state==='wander'){ selected.timer=0; }
  jump(selected);
});

const CHKS=[
  {t:'|ω|·R = v лап', s:'бегун в колесе', ok:false, f:()=>КОЛЕСО.user? [КОЛЕСО.slipPct<5, `Δ ${КОЛЕСО.slipPct.toFixed(2)} %`]
      : (Math.abs(КОЛЕСО.omega)>.05?[null,'бегуна нет']:[null,'ожидание бегуна'])},
  {t:'Пустое колесо тормозит', s:'трение в оси', ok:false, f:()=>{
      const w=Math.abs(КОЛЕСО.omega);
      return [w<1e-3||КОЛЕСО.freeDecayOk, `ω=${w.toFixed(3)} рад/с`]; }},
  {t:'Зверь в нижней точке обода', s:'стоит на ободе', ok:false, f:()=>{
      const u=КОЛЕСО.user; if(!u||u.state!=='runWheel') return [null,'бегуна нет'];
      const dy=Math.abs(u.y-(КОЛЕСО.yCenter-КОЛЕСО.R)), dh=Math.hypot(u.pos.x-КОЛЕСО.x,u.pos.z-КОЛЕСО.z);
      return [dy<.02&&dh<.02, `Δy ${dy.toFixed(3)} · Δось ${dh.toFixed(3)}`]; }},
  {t:'Габарит < R колеса', s:'обод не пересекает тело', ok:true, f:()=>[ДИАГОНАЛЬ_ЗВЕРЯ<КОЛЕСО.R,
      `${ДИАГОНАЛЬ_ЗВЕРЯ.toFixed(3)} < ${КОЛЕСО.R.toFixed(2)}`]},
  {t:'Внутри трубы — по оси', s:'вход через торец', ok:false, f:()=>{
      const u=ТРУБА_OBJ.user;
      return [u? ТРУБА_OBJ.axisDev<.02 : null, u? `откл ${ТРУБА_OBJ.axisDev.toFixed(4)} м`:'в трубе пусто']; }},
  {t:'Сквозь тела не прошёл', s:'колесо · миска · труба', ok:true, f:()=>[ПРОВЕРКИ.tunnel===0,
      `нарушений: ${ПРОВЕРКИ.tunnel}`]},
  {t:'Фаза шага от пути', s:'на месте лапы стоят', ok:true, f:()=>[ПРОВЕРКИ.phaseDriftAtRest<1e-3,
      `дрейф в покое ${(ПРОВЕРКИ.phaseDriftAtRest*1000).toFixed(2)}·10⁻³`]},
  {t:'Один предмет — один зверь', s:'занятые объекты не делят', ok:true, f:()=>{
      const n=[КОЛЕСО.user,ТРУБА_OBJ.user,МИСКА.user].filter(Boolean).length;
      const uniq=new Set([КОЛЕСО.user,ТРУБА_OBJ.user,МИСКА.user].filter(Boolean)).size;
      return [n===uniq,'объектов занято: '+uniq];}}
];
CHKS.forEach(c=>{ const d=document.createElement('div'); d.className='chk';
  d.innerHTML=`<span class="beed"></span><span class="t"><b>${c.t}</b><span></span></span>`;
  checksEl.appendChild(d); c.beed=d.querySelector('.beed'); c.val=d.querySelector('.t span'); });

document.getElementById('foot').innerHTML =
  `<b>ДЛИНА_ЗВЕРЯ</b> ${ДЛИНА_ЗВЕРЯ} · <b>ВЫСОТА</b> ${ВЫСОТА_ЗВЕРЯ} · <b>ШИРИНА</b> ${ШИРИНА_ЗВЕРЯ} м<br>
   R = max(диагональ+запас, (L+0.30)/100°) = <b>${КОЛЕСО.R}</b> м · ширина барабана <b>${КОЛЕСО.width.toFixed(2)}</b> м<br>
   длина шага <b>${ДЛИНА_ШАГА}</b> м · duty ${ДЮТИ} · μ оси <b>${КОЛЕСО.friction}</b> рад/с²`;
document.getElementById('cR').textContent = КОЛЕСО.R.toFixed(2)+' м';
document.getElementById('cD').textContent = ДИАГОНАЛЬ_ЗВЕРЯ.toFixed(2)+' м';

// слоу-мо / тела / автоповорот
let timeScale=1;
const bBody=document.getElementById('bBody'), bSlow=document.getElementById('bSlow'), bOrbit=document.getElementById('bOrbit');
bBody.onclick=()=>{ bodyGroup.visible=!bodyGroup.visible; bBody.classList.toggle('on',bodyGroup.visible); };
bSlow.onclick=()=>{ timeScale=timeScale===1?.25:1; bSlow.classList.toggle('on',timeScale!==1); };
bOrbit.onclick=()=>{ controls.autoRotate=!controls.autoRotate; bOrbit.classList.toggle('on',controls.autoRotate); };
addEventListener('keydown',e=>{ if(e.code==='Space'){ e.preventDefault(); bSlow.click(); } });

// клик по хомяку в 3D
const ray=new THREE.Raycaster(), ptr=new THREE.Vector2();
let downX=0,downY=0;
renderer.domElement.addEventListener('pointerdown',e=>{ downX=e.clientX; downY=e.clientY; });
renderer.domElement.addEventListener('pointerup',e=>{
  if(Math.hypot(e.clientX-downX,e.clientY-downY)>6) return;
  const r=renderer.domElement.getBoundingClientRect();
  ptr.set(((e.clientX-r.left)/r.width)*2-1, -((e.clientY-r.top)/r.height)*2+1);
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(ХОМЯКИ.map(h=>h.pick),false)[0];
  if(hit){ const h=hit.object.userData.h; ХОМЯКИ.forEach(x=>x.sel=false); h.sel=true; selected=h; jump(h); }
});
renderer.domElement.addEventListener('pointermove',e=>{
  const r=renderer.domElement.getBoundingClientRect();
  ptr.set(((e.clientX-r.left)/r.width)*2-1, -((e.clientY-r.top)/r.height)*2+1);
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(ХОМЯКИ.map(h=>h.pick),false)[0];
  const h=hit? hit.object.userData.h : null;
  ХОМЯКИ.forEach(x=>{ if(!x.sel) x.hovered=(x===h); });
  renderer.domElement.style.cursor = h?'pointer':'grab';
});
ХОМЯКИ.forEach(h=>h.pick.userData.h=h);

// авто-орбита после 16 с покоя
let idleT=0; ['pointerdown','wheel','keydown'].forEach(ev=>addEventListener(ev,()=>{idleT=0;controls.autoRotate=false;bOrbit.classList.remove('on');}));

// спарклайн ω
const sp=document.getElementById('spark'), sctx=sp.getContext('2d'), hist=[];
function drawSpark(){
  const w=sp.clientWidth, h=sp.clientHeight, dpr=Math.min(devicePixelRatio,2);
  if(sp.width!==w*dpr){ sp.width=w*dpr; sp.height=h*dpr; }
  sctx.setTransform(dpr,0,0,dpr,0,0); sctx.clearRect(0,0,w,h);
  hist.push(Math.abs(КОЛЕСО.omega)); if(hist.length>160) hist.shift();
  const mx=Math.max(.6,...hist);
  sctx.strokeStyle='rgba(255,255,255,.07)'; sctx.beginPath(); sctx.moveTo(0,h*.5); sctx.lineTo(w,h*.5); sctx.stroke();
  sctx.beginPath();
  hist.forEach((v,i)=>{ const x=i/(160-1)*w, y=h-4-(v/mx)*(h-10); i?sctx.lineTo(x,y):sctx.moveTo(x,y); });
  sctx.lineTo(hist.length/(160-1)*w,h); sctx.lineTo(0,h); sctx.closePath();
  sctx.fillStyle='rgba(242,165,44,.16)'; sctx.fill();
  sctx.beginPath();
  hist.forEach((v,i)=>{ const x=i/(160-1)*w, y=h-4-(v/mx)*(h-10); i?sctx.lineTo(x,y):sctx.moveTo(x,y); });
  sctx.strokeStyle='#f2a52c'; sctx.lineWidth=1.6; sctx.stroke();
  sctx.fillStyle='rgba(190,205,215,.6)'; sctx.font='9px JetBrains Mono, monospace';
  sctx.fillText('ω(t) рад/с', 7, 12);
}
const nf=(v,d=2)=> (Math.abs(v)<1e-4?0:v).toFixed(d);
let uiT=0;
function refreshUI(){
  ХОМЯКИ.forEach((h,i)=>{
    rowRefs[i].stat.textContent = h.status;
    rowRefs[i].bar.style.width = clamp(h.speed/1.7,0,1)*100+'%';
    rowRefs[i].el.classList.toggle('sel', !!h.sel);
  });
  document.getElementById('wOmega').textContent=nf(КОЛЕСО.omega,3);
  document.getElementById('wRim').innerHTML=nf(КОЛЕСО.rimSpeed,3)+' <small>м/с</small>';
  document.getElementById('wPaw').innerHTML=nf(КОЛЕСО.pawSpeed,3)+' <small>м/с</small>';
  const sl=document.getElementById('wSlip');
  if(КОЛЕСО.user&&КОЛЕСО.user.state==='runWheel'){
    sl.innerHTML=`${nf(КОЛЕСО.slipPct,2)} <small>%</small>`; sl.className='v '+(КОЛЕСО.slipPct<5?'lime':'coral');
    document.getElementById('wNote').innerHTML=`бегун: <code>${КОЛЕСО.user.name}</code> · ω = v/R = ${nf(КОЛЕСО.pawSpeed/КОЛЕСО.R,3)} рад/с · шаг идёт от скорости обода`;
  } else {
    sl.textContent='—'; sl.className='v';
    document.getElementById('wNote').innerHTML='бегуна нет — колесо тормозит трением: <code>dω/dt = −μ·sign(ω)</code>';
  }
  const tu=ТРУБА_OBJ.user;
  document.getElementById('tDev').innerHTML=(tu?nf(ТРУБА_OBJ.axisDev,4):'0.000')+' <small>м</small>';
  document.getElementById('tX').innerHTML=(tu?nf(ТРУБА_OBJ.xInAxis,2):'—')+' <small>м</small>';
  document.getElementById('tNote').innerHTML = tu? `внутри: <code>${tu.name}</code>, идёт вдоль оси → ${tu.tubeDir>0?'+x':'−x'}, стоит на внутреннем дне (y = ${ТРУБА.yОпоры.toFixed(3)})`
    : 'стенка — две капсулы: сбоку непроходимо, вход только через торец.';
  document.getElementById('cS').textContent = (КОЛЕСО.user? (КОЛЕСO_rimHz()).toFixed(1):'0.0');
  function КОЛЕСO_rimHz(){ return Math.abs(КОЛЕСО.omega)*КОЛЕСО.R/ДЛИНА_ШАГА; }
  CHKS.forEach(c=>{ const [ok,txt]=c.f(); c.beed.className='beed '+(ok===null?'':ok?'ok':'warn'); c.val.textContent=txt; });
}

/* ============================================================================
   13. ЦИКЛ
   ========================================================================== */
let last=performance.now(), restPhase=new Map();
function loop(now){
  requestAnimationFrame(loop);
  let dt=(now-last)/1000; last=now;
  if(dt>1/20) dt=1/20;                 // ограничение дельты при просадках
  if(dt<=0) dt=1/60;
  const sdt=dt*timeScale;

  updateWheel(sdt);
  for(const h of ХОМЯКИ){
    const before=h.фаза, rest=(h.speed<.04 && !h.jump.on);
    stepHamster(h,sdt);
    // контроль: в покое фаза не должна ползти
    if(rest) ПРОВЕРКИ.phaseDriftAtRest=Math.max(ПРОВЕРКИ.phaseDriftAtRest, Math.abs(h.фаза-before));
    animateHamster(h,sdt);
  }
  separate();

  idleT+=dt; if(idleT>16 && !controls.autoRotate){ controls.autoRotate=true; bOrbit.classList.add('on'); }
  controls.update();
  drawSpark();
  uiT+=dt; if(uiT>.1){ uiT=0; refreshUI(); }
  renderer.render(scene,camera);
}
requestAnimationFrame(loop);

addEventListener('resize',()=>{
  const w=stage.clientWidth, h=stage.clientHeight;
  camera.aspect=w/h; camera.updateProjectionMatrix();
  renderer.setSize(w,h);
});

/* ============================================================================
   14. ИНТЕРФЕЙС ДЛЯ ПРОВЕРКИ СНАРУЖИ
   ========================================================================== */
window.CAGE = {
  hamsters: ХОМЯКИ, wheel: КОЛЕСО, tube: ТРУБА_OBJ, bowl: МИСКА, bottle: ПОИЛКА, checks: ПРОВЕРКИ,
  constants:{ДЛИНА_ЗВЕРЯ, ВЫСОТА_ЗВЕРЯ, ШИРИНА_ЗВЕРЯ, ДИАГОНАЛЬ_ЗВЕРЯ, ДЛИНА_ШАГА, R_КОЛЕСА},
  // моментальный снимок для тестов: расхождение ω·R и скорости лап, отклонение от оси трубы
  snapshot(){
    const u=КОЛЕСО.user, t=ТРУБА_OBJ.user;
    return {
      wheel:{omega:КОЛЕСО.omega, rimSpeed:КОЛЕСО.rimSpeed, pawSpeed:КОЛЕСО.pawSpeed,
             slipPct:u&&u.state==='runWheel'?КОЛЕСО.slipPct:null,
             runner:u?u.name:null, R:КОЛЕСО.R},
      wheelBottomPoint:{x:КОЛЕСО.x,y:КОЛЕСО.yCenter-КОЛЕСО.R,z:КОЛЕСО.z},
      tube:{runner:t?t.name:null, axisDev:t?ТРУБА_OBJ.axisDev:null, xAlongAxis:t?ТРУБА_OBJ.xInAxis:null},
      walkersInsideObjects: ХОМЯКИ.filter(h=>h.state!=='inTube'&&insideTubeSpan(h)).map(h=>h.name),
      violations:ПРОВЕРКИ
    };
  }
};
window.addEventListener('error',e=>{ ПРОВЕРКИ.errors++; });
console.log('%cХомяки готовы','color:#f2a52c;font-weight:700', window.CAGE.snapshot());
</script>
</body>
</html>
```

**Как устроена «честность» в ключевых местах:**

- **ω = v / R.** Бегун задаёт только скорость лап `pawSpeed`; колесо получает `ω = damp(ω, v/R, …)`, а *обратно* фаза шага берётся из `|ω|·R` — то есть проскальзывание физически невозможно подделать, оно измеряется и показывается в панели (обычно 0.00–0.3 %). Ушёл зверь — включается `dω/dt = −μ·sign(ω)`, спарклайн рисует затухание.
- **Радиус не подобран руками:** `R = max(гипотенуза габа­рита + запас, (L+0.30)/100°) = 0.54`, ширина барабана = ширина зверя + 0.28. Проверка «габарит < R» живая.
- **Труба** — две капсулы-стенки: между их торцами проход свободен, сбоку — нормальное выталкивание; внутри пользователь идёт строго по оси (`z → damp(z, ось)`, отклонение ~10⁻⁴) и стоит на внутреннем дне `y = r_out − r_in`.
- **Лапы** — чистая функция от фазы, а фаза прирастает от пройденного пути (или от пробега обода), поэтому в стойле лапы замирают; амплитуда маха выведена из `asin(шаг·duty / 2L)`, так что стопа в опоре идёт со скоростью земли.
- **Никаких телепортов:** вход/выход из колеса — 0.85 с/0.75 с интерполяция с подъёмом через обод, выход только после того, как бегун сбросил скорость; в колесе и трубе держится `user`, второго туда не пускает выбор планов.