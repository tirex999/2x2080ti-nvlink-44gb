# Хомяки в колесе — честная физика

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ХОМЯКИ · клетка с честной физикой</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;800&family=Manrope:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#0a0f13; --ink2:#111a20; --line:rgba(255,255,255,.10);
  --txt:#eef3f2; --dim:#8ea0a8; --dim2:#5f7178;
  --amber:#f7b32b; --mint:#48d8a4; --coral:#ff6f52; --sky:#79c2ff; --plum:#c48cff;
  --mono:'JetBrains Mono',ui-monospace,monospace;
  --disp:'Unbounded','Manrope',system-ui,sans-serif;
  --body:'Manrope',system-ui,-apple-system,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:var(--ink);color:var(--txt);font-family:var(--body)}
canvas#c{position:fixed;inset:0;display:block;width:100%;height:100%}

/* ---------- атмосферные слои поверх сцены ---------- */
.vignette,.grain,.scan{position:fixed;inset:0;pointer-events:none}
.vignette{background:
  radial-gradient(120% 90% at 50% 42%,transparent 38%,rgba(4,7,9,.55) 88%),
  radial-gradient(60% 40% at 78% 8%,rgba(247,179,43,.10),transparent 70%);
  z-index:2}
.grain{z-index:4;opacity:.055;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)'/%3E%3C/svg%3E")}
.scan{z-index:3;opacity:.25;background:repeating-linear-gradient(180deg,rgba(255,255,255,.03) 0 1px,transparent 1px 3px)}

/* ---------- HUD ---------- */
.hud{position:fixed;inset:0;z-index:6;pointer-events:none;padding:clamp(14px,2.2vw,30px);
  display:grid;grid-template-columns:minmax(280px,25vw) 1fr minmax(280px,23vw);
  grid-template-rows:auto 1fr auto;gap:16px;
  transition:opacity .45s ease, filter .45s ease}
.hud.hidden{opacity:0;filter:blur(6px)}

.panel{pointer-events:auto;background:linear-gradient(180deg,rgba(20,29,35,.93),rgba(10,16,20,.93));
  border:1px solid var(--line);border-radius:14px;position:relative;overflow:hidden;
  box-shadow:0 24px 60px -28px rgba(0,0,0,.9), inset 0 1px 0 rgba(255,255,255,.05);
  animation:rise .8s cubic-bezier(.16,.84,.28,1) backwards}
.panel::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--amber),var(--coral) 35%,var(--mint) 70%,transparent)}
@keyframes rise{from{opacity:0;transform:translateY(18px) scale(.985)}}

/* masthead */
.masthead{grid-column:1;grid-row:1;padding:16px 18px 14px;animation-delay:.05s}
.kicker{font-family:var(--mono);font-size:9.5px;letter-spacing:.22em;text-transform:uppercase;
  color:var(--dim);display:flex;align-items:center;gap:8px}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--mint);box-shadow:0 0 0 0 rgba(72,216,164,.6);
  animation:pulse 2.2s infinite}
@keyframes pulse{70%{box-shadow:0 0 0 9px rgba(72,216,164,0)}100%{box-shadow:0 0 0 0 rgba(72,216,164,0)}}
.masthead h1{font-family:var(--disp);font-weight:800;font-size:clamp(38px,5.1vw,68px);line-height:.82;
  letter-spacing:-.045em;text-transform:uppercase;margin:8px 0 6px}
.masthead h1 span{color:transparent;-webkit-text-stroke:1.6px var(--amber)}
.lede{font-size:12.5px;line-height:1.5;color:var(--dim);max-width:34ch}
.lede b{color:var(--txt);font-family:var(--mono);font-size:12px;background:rgba(247,179,43,.12);
  border:1px solid rgba(247,179,43,.3);padding:1px 6px;border-radius:5px}

/* roster */
.roster{grid-column:1;grid-row:2;align-self:end;padding:12px 10px 10px;animation-delay:.2s}
.ph{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--dim2);
  padding:2px 8px 10px;display:flex;justify-content:space-between}
#rosterList{list-style:none;display:flex;flex-direction:column;gap:4px}
.hrow{--c:#fff;opacity:0;animation:rowIn .6s ease forwards;border-radius:10px}
@keyframes rowIn{to{opacity:1}}
.hbtn{width:100%;display:grid;grid-template-columns:auto 1fr auto auto;align-items:center;gap:9px;
  background:transparent;border:0;border-left:2px solid transparent;color:inherit;cursor:pointer;
  padding:8px 9px;border-radius:0 10px 10px 0;text-align:left;font:inherit;
  transition:background .22s,border-color .22s,transform .22s}
.hbtn:hover,.hrow.sel .hbtn{background:rgba(255,255,255,.05);border-left-color:var(--c);transform:translateX(3px)}
.dot{width:11px;height:11px;border-radius:50%;background:var(--c);box-shadow:0 0 12px -1px var(--c)}
.hm b{display:block;font-family:var(--disp);font-weight:800;font-size:12.5px;letter-spacing:.01em}
.hm .st{display:block;font-size:11px;color:var(--dim);line-height:1.35;min-height:15px}
.hm .st.hot{color:var(--amber)}
.gait{display:flex;gap:3px}
.gait i{width:5px;height:12px;border-radius:2px;background:#fff;opacity:.16;display:block}
.sp{width:34px;height:4px;border-radius:3px;background:rgba(255,255,255,.09);overflow:hidden}
.sp i{display:block;height:100%;width:0;background:var(--c);border-radius:3px;transition:width .12s linear}

/* telemetry */
.telemetry{grid-column:3;grid-row:1 / span 2;align-self:start;padding:12px 12px 10px;animation-delay:.32s;
  max-height:calc(100vh - 60px);overflow:auto;scrollbar-width:thin}
.sect{padding:8px 8px 12px;border-top:1px solid rgba(255,255,255,.07)}
.sect:first-of-type{border-top:0}
.sect h3{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--dim2);
  margin-bottom:9px;display:flex;align-items:center;gap:7px}
.sect h3 em{font-style:normal;font-size:9px;color:var(--ink);background:var(--mint);padding:2px 5px;border-radius:4px;letter-spacing:.06em}
.sect h3 em.off{background:#3b4a52;color:var(--dim)}
.kv{display:grid;grid-template-columns:1fr auto;gap:2px 8px;font-size:11.5px;color:var(--dim);margin-bottom:5px}
.kv b{font-family:var(--mono);font-weight:700;color:var(--txt);font-variant-numeric:tabular-nums;text-align:right}
.kv b.ok{color:var(--mint)} .kv b.bad{color:var(--coral)}
.bar2{height:5px;border-radius:3px;background:rgba(255,255,255,.08);overflow:hidden;margin:6px 0 3px;display:flex}
.bar2 i{display:block;height:100%}
.chips{display:flex;flex-direction:column;gap:5px}
.chk{display:grid;grid-template-columns:auto 1fr auto;gap:8px;align-items:center;font-size:11px;color:var(--dim);
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:8px;padding:6px 8px;
  transition:border-color .3s,background .3s}
.chk s{width:7px;height:7px;border-radius:50%;background:#41535c;text-decoration:none}
.chk.pass{border-color:rgba(72,216,164,.35);background:rgba(72,216,164,.07)}
.chk.pass s{background:var(--mint);box-shadow:0 0 8px var(--mint)}
.chk.warn{border-color:rgba(255,111,82,.4);background:rgba(255,111,82,.08)}
.chk.warn s{background:var(--coral)}
.chk b{font-family:var(--mono);font-size:11px;color:var(--txt);font-variant-numeric:tabular-nums}
#log{list-style:none;font-family:var(--mono);font-size:10px;line-height:1.7;color:var(--dim2);
  display:flex;flex-direction:column-reverse;gap:1px;min-height:56px}
#log li{animation:fin .4s ease} #log li:first-child{color:var(--amber)}
@keyframes fin{from{opacity:0;transform:translateX(-8px)}}

/* hints + buttons */
.hints{grid-column:1 / span 3;grid-row:3;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;
  justify-content:space-between;animation:none}
.tools{display:flex;gap:7px;flex-wrap:wrap;pointer-events:auto}
.btn{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);
  background:rgba(20,29,35,.9);border:1px solid var(--line);padding:8px 12px;border-radius:999px;cursor:pointer;
  transition:.22s}
.btn:hover{color:var(--ink);background:var(--amber);border-color:var(--amber);transform:translateY(-2px)}
.btn:active{transform:scale(.96)}
.keys{font-family:var(--mono);font-size:10px;color:var(--dim2);letter-spacing:.08em}
.keys kbd{background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:4px;padding:1px 5px;color:var(--dim)}
@media (max-width:1080px){
  .hud{grid-template-columns:1fr auto}
  .masthead{grid-column:1}.telemetry{grid-column:2;grid-row:1 / span 2;width:270px}
  .roster{grid-column:1;max-width:340px}
}
@media (max-width:760px){
  .hud{grid-template-columns:1fr;grid-template-rows:auto auto 1fr auto;padding:10px}
  .telemetry{grid-column:1;grid-row:2;width:auto;max-height:33vh}
  .roster{grid-column:1;grid-row:3;align-self:end;max-width:none}
  .masthead h1{font-size:34px}.lede{display:none}
  .hints{grid-column:1}
}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="scan"></div><div class="vignette"></div><div class="grain"></div>

<div class="hud" id="hud">
  <header class="panel masthead">
    <p class="kicker"><span class="pulse"></span>диорама · three.js r128 · ω = v / R</p>
    <h1>ХОМЯ<span>КИ</span></h1>
    <p class="lede">Клетка на столе, пять зверей, одно колесо и одна труба.
      Колесо крутит тот, кто в нём бежит; обод под лапами уходит назад; в трубу входят только через торец.</p>
  </header>

  <section class="panel roster">
    <div class="ph"><span>звери · кто чем занят</span><span id="fps">— fps</span></div>
    <ul id="rosterList"></ul>
  </section>

  <section class="panel telemetry">
    <div class="sect">
      <h3>колесо <em id="wMode">ожидает</em></h3>
      <div class="kv"><span>бегун</span><b id="wUser">—</b></div>
      <div class="kv"><span>ω, рад/с</span><b id="wOmega">0.000</b></div>
      <div class="kv"><span>скорость лап v, ед/с</span><b id="wFoot">0.000</b></div>
      <div class="kv"><span>обод |ω|·R, ед/с</span><b id="wRim">0.000</b></div>
      <div class="kv"><span>расхождение</span><b id="wDiff">—</b></div>
      <div class="bar2"><i id="wBar1" style="background:var(--amber);width:0%"></i></div>
      <div class="bar2"><i id="wBar2" style="background:var(--sky);width:0%"></i></div>
      <div class="kv"><span>R обода / габарит тела</span><b id="wFit">—</b></div>
      <div class="kv"><span>лапы в нижней точке, ошибка</span><b id="wLow">—</b></div>
    </div>
    <div class="sect">
      <h3>труба <em id="tMode">свободна</em></h3>
      <div class="kv"><span>внутри</span><b id="tUser">—</b></div>
      <div class="kv"><span>отклонение от оси (X)</span><b id="tDev">—</b></div>
      <div class="kv"><span>лапы над внутр. дном</span><b id="tFloor">—</b></div>
      <div class="kv"><span>путь вдоль оси, %</span><b id="tAlong">—</b></div>
    </div>
    <div class="sect">
      <h3>проверки <em id="cAll">live</em></h3>
      <div class="chips" id="checks"></div>
    </div>
    <div class="sect">
      <h3>журнал</h3>
      <ul id="log"></ul>
    </div>
  </section>

  <div class="hints">
    <div class="tools">
      <button class="btn" id="bSpin">⟳ раскрутить колесо</button>
      <button class="btn" id="bFeed">все к миске</button>
      <button class="btn" id="bPause">⏸ пауза</button>
      <button class="btn" id="bView">сброс камеры</button>
    </div>
    <div class="keys"><kbd>клик по зверю</kbd> прыжок · <kbd>1…5</kbd> следить · <kbd>H</kbd> интерфейс · <kbd>R</kbd> вид</div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ==========================================================================
   ХОМЯКИ В КЛЕТКЕ — честная физика.
   Ключевые объекты вынесены наружу: window.hamsters, window.wheel, window.tube,
   window.sim, window.runChecks()  → их можно читать из консоли браузера.
   ========================================================================== */
(function(){
'use strict';
const TAU = Math.PI*2;
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const easeIO=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
function angLerp(a,b,t){let d=((b-a+Math.PI)%TAU+TAU)%TAU-Math.PI;return a+d*t;}
function approach(cur,tgt,maxD){const d=tgt-cur;return Math.abs(d)<=maxD?tgt:cur+Math.sign(d)*maxD;}
const rnd=(a,b)=>a+Math.random()*(b-a);

/* ─────────────────────────── 1. ГАБАРИТЫ ЗВЕРЯ ────────────────────────────
   Всё в «дециметрах». Дюжи константы, от которых считаются радиусы. */
const ДЛИНА_ЗВЕРЯ  = 1.70;   // от носа до хвоста
const ВЫСОТА_ЗВЕРЯ = 1.15;   // в стойке на внутренней поверхности обода (с ушами)
const ШИРИНА_ЗВЕРЯ = 0.95;   // ширина боков/плеч

/* Минимальный радиус окружности, в которую вписан прямоугольник L×H, стоящий
   нижней гранью на внутренней поверхности:  (L/2)² + (R−H)² ≤ R²
   ⇒ R ≥ ((L/2)² + H²) / (2H) */
function minRadius(len,hgt){ return (Math.pow(len*.5,2)+hgt*hgt)/(2*hgt); }

const R_МИН      = minRadius(ДЛИНА_ЗВЕРЯ, ВЫСОТА_ЗВЕРЯ);          // ≈0.89
const КОЛЕСО_R   = +(R_МИН*1.95).toFixed(3);                       // ≈1.73 — вдвое больше габарита
const КОЛЕСО_Ш   = +(Math.max(ШИРИНА_ЗВЕРЯ*2.2, ДЛИНА_ЗВЕРЯ*1.25)).toFixed(3); // зазор между ободами шире боков в 2.2 раза

const ТР_МИН   = minRadius(ШИРИНА_ЗВЕРЯ, ВЫСОТА_ЗВЕРЯ);           // ≈0.63
const ТРУБА_R  = +(ТР_МИН*1.8).toFixed(3);                         // ≈1.13
const ТРУБА_L  = 7.2;

/* ─────────────────────────── 2. СЦЕНА ───────────────────────────────────── */
const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.06;

const scene=new THREE.Scene();
scene.background=new THREE.Color(0x0d1418);
scene.fog=new THREE.Fog(0x0d1418,52,150);

const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.4,400);
camera.position.set(30,26,46);

const controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.06;
controls.target.set(0,3.2,0); controls.minDistance=14; controls.maxDistance=95;
controls.maxPolarAngle=Math.PI*.495; controls.autoRotateSpeed=.35; controls.enabled=false;

/* ── текстуры, нарисованные на canvas (никаких внешних файлов) ── */
function noiseTex(size,fn){
  const c=document.createElement('canvas');c.width=c.height=size;const x=c.getContext('2d');
  fn(x,size);const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=4;return t;
}
const woodTex=noiseTex(512,(x,s)=>{
  x.fillStyle='#6b4a30';x.fillRect(0,0,s,s);
  for(let i=0;i<260;i++){
    x.globalAlpha=rnd(.03,.14);x.fillStyle=Math.random()<.5?'#3d2716':'#8a6440';
    const y=rnd(0,s);x.beginPath();x.moveTo(0,y);
    for(let px=0;px<=s;px+=24)x.lineTo(px,y+Math.sin(px*.02+i)*rnd(1,5));
    x.lineWidth=rnd(.6,3.2);x.strokeStyle=x.fillStyle;x.stroke();
  }
  x.globalAlpha=1;
});
const furTex=noiseTex(128,(x,s)=>{
  const d=x.createImageData(s,s);
  for(let i=0;i<d.data.length;i+=4){const v=128+Math.random()*90;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255;}
  x.putImageData(d,0,0);
});
const wallTex=noiseTex(256,(x,s)=>{
  x.fillStyle='#3a4650';x.fillRect(0,0,s,s);
  for(let i=0;i<4000;i++){x.globalAlpha=rnd(.01,.06);x.fillStyle=Math.random()<.5?'#fff':'#000';
    x.fillRect(rnd(0,s),rnd(0,s),rnd(1,4),rnd(1,4));}
});
const dotTex=noiseTex(64,(x,s)=>{
  const g=x.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
  g.addColorStop(0,'rgba(255,240,210,1)');g.addColorStop(1,'rgba(255,240,210,0)');
  x.fillStyle=g;x.fillRect(0,0,s,s);
});

/* ── свет ── */
scene.add(new THREE.HemisphereLight(0xbcd8f0,0x4a3a2c,.55));
const key=new THREE.DirectionalLight(0xffe6c0,1.5);
key.position.set(17,26,14);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);
key.shadow.camera.left=-20;key.shadow.camera.right=20;key.shadow.camera.top=20;key.shadow.camera.bottom=-20;
key.shadow.camera.near=1;key.shadow.camera.far=75;key.shadow.bias=-.0007;key.shadow.normalBias=.03;
scene.add(key);
const fill=new THREE.DirectionalLight(0x9fc4ff,.42);fill.position.set(-18,12,-10);scene.add(fill);
const lampLight=new THREE.PointLight(0xffcf90,.75,60,2);lampLight.position.set(-3.5,13.5,3);scene.add(lampLight);
const bounce=new THREE.PointLight(0x8fb6d8,.3,40,2);bounce.position.set(6,1,-8);scene.add(bounce);

/* ── комната: стол, пол, стены, плакат, лампа, мелочи ── */
const MAT={
  wood:new THREE.MeshStandardMaterial({map:(()=>{const t=woodTex.clone();t.needsUpdate=true;t.repeat.set(4,3);return t;})(),roughness:.72,metalness:0}),
  tableWood:new THREE.MeshStandardMaterial({map:(()=>{const t=woodTex.clone();t.needsUpdate=true;t.repeat.set(8,6);return t;})(),roughness:.55}),
  wall:new THREE.MeshStandardMaterial({map:(()=>{const t=wallTex.clone();t.needsUpdate=true;t.repeat.set(6,4);return t;})(),roughness:.95}),
  metal:new THREE.MeshStandardMaterial({color:0xbfc7cc,roughness:.28,metalness:.92}),
  metalDark:new THREE.MeshStandardMaterial({color:0x6c767c,roughness:.4,metalness:.85}),
  tray:new THREE.MeshStandardMaterial({color:0x2b3a44,roughness:.55,metalness:.15}),
  straw:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.94}),
  plastic:new THREE.MeshStandardMaterial({color:0xdff0f6,roughness:.12,metalness:0,transparent:true,opacity:.32,side:THREE.DoubleSide}),
  water:new THREE.MeshStandardMaterial({color:0x6fc2e8,roughness:.05,transparent:true,opacity:.6}),
  ceramic:new THREE.MeshStandardMaterial({color:0xd9704f,roughness:.35,side:THREE.DoubleSide}),
  seed:new THREE.MeshStandardMaterial({color:0xd8b25a,roughness:.8}),
  wood2:new THREE.MeshStandardMaterial({color:0x8c6239,roughness:.85}),
  wood3:new THREE.MeshStandardMaterial({color:0x6d4a2b,roughness:.9}),
  wheelPlastic:new THREE.MeshStandardMaterial({color:0xf0f4f6,roughness:.3,metalness:.05,side:THREE.DoubleSide}),
  wheelSlat:new THREE.MeshStandardMaterial({color:0xdfe7ea,roughness:.5}),
  pink:new THREE.MeshStandardMaterial({color:0xf0a6ac,roughness:.6}),
  eyeW:new THREE.MeshStandardMaterial({color:0xf7f3ea,roughness:.15}),
  eyeB:new THREE.MeshStandardMaterial({color:0x14100f,roughness:.05}),
  glow:new THREE.MeshBasicMaterial({color:0xffe2ad})
};

const room=new THREE.Group();scene.add(room);
(function buildRoom(){
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(300,300),new THREE.MeshStandardMaterial({color:0x21292f,roughness:.95}));
  floor.rotation.x=-Math.PI/2;floor.position.y=-18;floor.receiveShadow=true;room.add(floor);

  const table=new THREE.Mesh(new THREE.BoxGeometry(64,2.2,44),MAT.tableWood);
  table.position.set(0,-2.7,0);table.receiveShadow=true;table.castShadow=true;room.add(table);
  const legG=new THREE.BoxGeometry(2.4,15.5,2.4);
  [[-28,-18],[28,-18],[-28,18],[28,18]].forEach(p=>{const l=new THREE.Mesh(legG,MAT.wood3);
    l.position.set(p[0],-11.5,p[1]);l.castShadow=true;room.add(l);});

  const back=new THREE.Mesh(new THREE.PlaneGeometry(160,80),MAT.wall);
  back.position.set(0,22,-34);back.receiveShadow=true;room.add(back);
  const side=new THREE.Mesh(new THREE.PlaneGeometry(120,80),MAT.wall);
  side.rotation.y=Math.PI/2;side.position.set(-52,22,0);room.add(side);
  const base=new THREE.Mesh(new THREE.BoxGeometry(160,3,.9),MAT.wood3);
  base.position.set(0,4.6,-33.4);room.add(base);

  /* плакат с формулой — «характеристика» места */
  const pc=document.createElement('canvas');pc.width=512;pc.height=384;const p=pc.getContext('2d');
  p.fillStyle='#101c24';p.fillRect(0,0,512,384);
  p.strokeStyle='rgba(121,194,255,.16)';p.lineWidth=1;
  for(let i=0;i<=512;i+=32){p.beginPath();p.moveTo(i,0);p.lineTo(i,384);p.stroke();}
  for(let j=0;j<=384;j+=32){p.beginPath();p.moveTo(0,j);p.lineTo(512,j);p.stroke();}
  p.strokeStyle='#79c2ff';p.lineWidth=4;p.beginPath();p.arc(150,215,86,0,TAU);p.stroke();
  p.strokeStyle='#f7b32b';p.lineWidth=3;p.beginPath();p.moveTo(150,215);p.lineTo(228,150);p.stroke();
  p.fillStyle='#f7b32b';p.beginPath();p.arc(150,301,7,0,TAU);p.fill();
  p.fillStyle='#48d8a4';p.font='bold 30px monospace';p.fillText('v',236,146);
  p.fillStyle='#eef3f2';p.font='bold 54px monospace';p.fillText('ω = v / R',272,215);
  p.font='20px monospace';p.fillStyle='#7d95a3';p.fillText('обод уходит НАЗАД от морды',272,255);
  p.fillText('фаза шага ← пройденный путь',272,286);
  p.fillStyle='#f7b32b';p.font='bold 26px monospace';p.fillText('ЛАБОРАТОРИЯ ХОМЯЧНОЙ МЕХАНИКИ',28,54);
  const poster=new THREE.Mesh(new THREE.PlaneGeometry(18,13.5),
    new THREE.MeshStandardMaterial({map:new THREE.CanvasTexture(pc),roughness:.9}));
  poster.position.set(16,17,-33.3);room.add(poster);
  const frame=new THREE.Mesh(new THREE.BoxGeometry(19.2,14.7,.5),MAT.wood3);
  frame.position.set(16,17,-33.6);room.add(frame);

  /* лампа над клеткой */
  const shade=new THREE.Mesh(new THREE.ConeGeometry(4.2,3.4,26,1,true),
    new THREE.MeshStandardMaterial({color:0x2f3a42,roughness:.5,metalness:.4,side:THREE.DoubleSide}));
  shade.position.set(-3.5,15.2,3);shade.rotation.x=Math.PI;room.add(shade);
  const bulb=new THREE.Mesh(new THREE.SphereGeometry(.9,16,12),MAT.glow);
  bulb.position.set(-3.5,14.1,3);room.add(bulb);
  const cord=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,16,6),MAT.metalDark);
  cord.position.set(-3.5,24.5,3);room.add(cord);

  /* книги и кружка на столе */
  const bookCols=[0x9e3b3b,0x2f6b63,0xc78b2e];
  bookCols.forEach((c,i)=>{const b=new THREE.Mesh(new THREE.BoxGeometry(7.4,.75,5),
    new THREE.MeshStandardMaterial({color:c,roughness:.8}));
    b.position.set(-21,-1.22+i*.78,-9);b.rotation.y=.16*i;b.castShadow=true;b.receiveShadow=true;room.add(b);});
  const mug=new THREE.Mesh(new THREE.CylinderGeometry(1.35,1.2,2.4,20),
    new THREE.MeshStandardMaterial({color:0xdfe7ea,roughness:.3}));
  mug.position.set(20,-.6,10);mug.castShadow=true;room.add(mug);
  const handle=new THREE.Mesh(new THREE.TorusGeometry(.8,.18,8,18),mug.material);
  handle.position.set(21.4,-.6,10);handle.rotation.y=Math.PI/2;room.add(handle);

  /* тёплое пятно света на стене */
  const patch=new THREE.Mesh(new THREE.PlaneGeometry(26,16),
    new THREE.MeshBasicMaterial({color:0xffd9a0,transparent:true,opacity:.055,blending:THREE.AdditiveBlending}));
  patch.position.set(-14,15,-33.2);room.add(patch);
})();

/* ─────────────────────────── 3. КЛЕТКА ──────────────────────────────────── */
const CAGE={hx:11,hz:7.5,barH:7.2};
const cage=new THREE.Group();scene.add(cage);
(function buildCage(){
  /* поддон */
  const tray=new THREE.Mesh(new THREE.BoxGeometry(CAGE.hx*2+1.6,2.0,CAGE.hz*2+1.6),MAT.tray);
  tray.position.set(0,-1.7,0);tray.castShadow=true;tray.receiveShadow=true;cage.add(tray);
  const lip=new THREE.Mesh(new THREE.BoxGeometry(CAGE.hx*2+1.4,.9,CAGE.hz*2+1.4),MAT.metalDark);
  lip.position.set(0,.15,0);lip.castShadow=true;lip.receiveShadow=true;cage.add(lip);
  const bedding=new THREE.Mesh(new THREE.PlaneGeometry(CAGE.hx*2,CAGE.hz*2),
    new THREE.MeshStandardMaterial({color:0xa8946e,roughness:1}));
  bedding.rotation.x=-Math.PI/2;bedding.position.y=.02;bedding.receiveShadow=true;cage.add(bedding);

  /* подстилка: ОДИН InstancedMesh со щепками */
  const N=1050;
  const chip=new THREE.InstancedMesh(new THREE.BoxGeometry(.36,.045,.11),MAT.straw,N);
  chip.castShadow=false;chip.receiveShadow=true;
  const m=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),p=new THREE.Vector3(),s=new THREE.Vector3();
  const col=new THREE.Color();
  for(let i=0;i<N;i++){
    p.set(rnd(-CAGE.hx+.5,CAGE.hx-.5),rnd(.03,.13),rnd(-CAGE.hz+.5,CAGE.hz-.5));
    e.set(rnd(-.4,.4),rnd(0,TAU),rnd(-.4,.4));q.setFromEuler(e);
    s.set(rnd(.6,1.7),rnd(.7,1.6),rnd(.6,1.5));
    m.compose(p,q,s);chip.setMatrixAt(i,m);
    col.setHSL(rnd(.09,.13),rnd(.24,.46),rnd(.38,.62));chip.setColorAt(i,col);
  }
  chip.instanceMatrix.needsUpdate=true;cage.add(chip);

  /* прутья: InstancedMesh */
  const gap=.52, barPos=[];
  for(let x=-CAGE.hx;x<=CAGE.hx+.01;x+=gap) {barPos.push([x,-CAGE.hz]);barPos.push([x,CAGE.hz]);}
  for(let z=-CAGE.hz+gap;z<=CAGE.hz-.01;z+=gap){barPos.push([-CAGE.hx,z]);barPos.push([CAGE.hx,z]);}
  const bars=new THREE.InstancedMesh(new THREE.CylinderGeometry(.075,.075,CAGE.barH,7),MAT.metal,barPos.length);
  bars.castShadow=true;
  barPos.forEach((b,i)=>{e.set(0,0,0);q.setFromEuler(e);p.set(b[0],CAGE.barH/2+.55,b[1]);s.set(1,1,1);
    m.compose(p,q,s);bars.setMatrixAt(i,m);});
  bars.instanceMatrix.needsUpdate=true;cage.add(bars);

  /* рамки: низ, верх, средние, угловые стойки, крышка */
  const rail=(w,h,d,x,y,z)=>{const r=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),MAT.metal);
    r.position.set(x,y,z);r.castShadow=true;r.receiveShadow=true;cage.add(r);};
  const W=CAGE.hx*2+.5,D=CAGE.hz*2+.5;
  rail(W,.34,.34,0,.78,-CAGE.hz-.15);rail(W,.34,.34,0,.78,CAGE.hz+.15);
  rail(.34,.34,D,-CAGE.hx-.15,.78,0);rail(.34,.34,D,CAGE.hx+.15,.78,0);
  const TY=CAGE.barH+.62;
  rail(W,.4,.4,0,TY,-CAGE.hz-.15);rail(W,.4,.4,0,TY,CAGE.hz+.15);
  rail(.4,.4,D+.6,-CAGE.hx-.15,TY,0);rail(.4,.4,D+.6,CAGE.hx+.15,TY,0);
  rail(W,.28,.28,0,TY*.55,-CAGE.hz-.15);rail(W,.28,.28,0,TY*.55,CAGE.hz+.15);
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(c=>{
    const post=new THREE.Mesh(new THREE.CylinderGeometry(.19,.19,CAGE.barH+1.1,10),MAT.metal);
    post.position.set(c[0]*(CAGE.hx+.15),(CAGE.barH+1.1)/2+.4,c[1]*(CAGE.hz+.15));post.castShadow=true;cage.add(post);});
  for(let x=-CAGE.hx+.6;x<=CAGE.hx;x+=2.2){const l=new THREE.Mesh(new THREE.CylinderGeometry(.07,.07,D,6),MAT.metal);
    l.rotation.x=Math.PI/2;l.position.set(x,TY+.25,0);l.castShadow=true;cage.add(l);}

  /* домик-укрытие (декор + твёрдое тело) */
  const hut=new THREE.Group();hut.position.set(-8.2,0,-4.9);cage.add(hut);
  const hm=MAT.wood2;
  const wall=(w,h,d,x,y,z)=>{const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),hm);
    b.position.set(x,y,z);b.castShadow=true;b.receiveShadow=true;hut.add(b);return b;};
  wall(3.6,.18,3.2,0,1.75,0);
  wall(.2,1.7,3.2,-1.7,.9,0);wall(.2,1.7,3.2,1.7,.9,0);
  wall(3.6,1.7,.2,0,.9,-1.55);
  wall(1.15,1.7,.2,-1.22,.9,1.55);wall(1.15,1.7,.2,1.22,.9,1.55);
  wall(1.3,.45,.2,0,1.5,1.55);
  const roof=new THREE.Mesh(new THREE.BoxGeometry(4.1,.22,3.7),MAT.wood3);
  roof.position.set(0,2.02,0);roof.rotation.z=.06;roof.castShadow=true;hut.add(roof);
})();

/* ─────────────────────────── 4. КОЛЕСО ──────────────────────────────────── */
const wheel={
  R:КОЛЕСО_R, width:КОЛЕСО_Ш, halfW:КОЛЕСО_Ш/2+.09,
  center:new THREE.Vector3(7.0,КОЛЕСО_R+.16,-2.6),
  contactY:.16,              // верх беговой поверхности над подстилкой
  angle:0, omega:0, rimSpeed:0, footSpeed:0, mismatchPct:0,
  user:null,                 // эксклюзивный «пользователь» колеса
  sign:+1,                   // +1 ⇒ зверь мордой к +Z, обод уходит к −Z
  dryFriction:.62, viscFriction:1.15,
  bodyRadius:0, lowErr:0,
  get fits(){ return this.bodyRadius < this.R; },
  get driving(){ return !!(this.user && this.user.state===ST.WHEEL_RUN); }
};
wheel.center.y=wheel.R+wheel.contactY;
const wheelGroup=new THREE.Group();wheelGroup.position.copy(wheel.center);scene.add(wheelGroup);
const drum=new THREE.Group();wheelGroup.add(drum);
(function buildWheel(){
  const R=wheel.R,H2=wheel.width/2;
  /* оболочка (беговой барабан), ось вдоль X */
  const shell=new THREE.Mesh(new THREE.CylinderGeometry(R+.12,R+.12,wheel.width,34,1,true),MAT.wheelPlastic);
  shell.rotation.z=Math.PI/2;shell.castShadow=true;shell.receiveShadow=true;drum.add(shell);
  /* поперечные рейки — по ним бегут лапы */
  const n=16, rg=new THREE.BoxGeometry(wheel.width-.04,.09,.2);
  for(let i=0;i<n;i++){const th=i/n*TAU;const r=new THREE.Mesh(rg,MAT.wheelSlat);
    r.position.set(0,Math.cos(th)*(R-.03),Math.sin(th)*(R-.03));r.rotation.x=th;
    r.castShadow=true;r.receiveShadow=true;drum.add(r);}
  /* боковые обода */
  [-1,1].forEach(s=>{const t=new THREE.Mesh(new THREE.TorusGeometry(R+.06,.085,8,42),MAT.wheelPlastic);
    t.rotation.y=Math.PI/2;t.position.x=s*H2;t.castShadow=true;drum.add(t);});
  /* спицы задней стенки */
  for(let i=0;i<7;i++){const sp=new THREE.Mesh(new THREE.BoxGeometry(.06,R-.1,.16),MAT.wheelPlastic);
    const th=i/7*TAU;sp.position.set(-H2+.05,Math.cos(th)*(R*.55),Math.sin(th)*(R*.55));
    sp.rotation.x=th;sp.castShadow=true;drum.add(sp);}
  /* ступица + ось */
  const hub=new THREE.Mesh(new THREE.CylinderGeometry(.3,.3,wheel.width+.3,16),MAT.metalDark);
  hub.rotation.z=Math.PI/2;hub.castShadow=true;drum.add(hub);
  const axle=new THREE.Mesh(new THREE.CylinderGeometry(.12,.12,wheel.width+2.4,10),MAT.metal);
  axle.rotation.z=Math.PI/2;axle.castShadow=true;wheelGroup.add(axle);
  /* кронштейн-консоль со стороны −X (чтобы вход был свободен с другой стороны) */
  const post=new THREE.Mesh(new THREE.BoxGeometry(.4,wheel.center.y+.1,.5),MAT.metalDark);
  post.position.set(-wheel.halfW-1.0,-wheel.center.y/2+.05,-.0);post.castShadow=true;wheelGroup.add(post);
  const arm=new THREE.Mesh(new THREE.BoxGeometry(1.3,.28,.34),MAT.metalDark);
  arm.position.set(-wheel.halfW-.1,0,0);arm.castShadow=true;wheelGroup.add(arm);
  const foot=new THREE.Mesh(new THREE.BoxGeometry(1.5,.24,1.6),MAT.metalDark);
  foot.position.set(-wheel.halfW-1.0,-wheel.center.y+.1,0);foot.castShadow=true;wheelGroup.add(foot);
})();
/* ступальни у входа в колесо (зверь поднимается на 0.16 и входит в проём) */
(function steps(){
  const s1=new THREE.Mesh(new THREE.BoxGeometry(1.5,.18,3.0),MAT.wood2);
  s1.position.set(wheel.center.x-wheel.halfW-1.9,.06,wheel.center.z);s1.receiveShadow=true;s1.castShadow=true;scene.add(s1);
  const s2=new THREE.Mesh(new THREE.BoxGeometry(1.3,.2,2.6),MAT.wood3);
  s2.position.set(wheel.center.x-wheel.halfW-1.0,.08,wheel.center.z);s2.receiveShadow=true;s2.castShadow=true;scene.add(s2);
})();
wheel.stand=new THREE.Vector3(wheel.center.x-wheel.halfW-2.0,0,wheel.center.z);

/* ─────────────────────────── 5. ТРУБА (полая) ───────────────────────────── */
const tube={
  R:ТРУБА_R, L:ТРУБА_L, axis:new THREE.Vector3(0,0,1),
  center:new THREE.Vector3(-5.4,ТРУБА_R,.8),
  user:null, devX:0, footAboveFloor:0, alongPct:0,
  get innerFloorY(){ return this.center.y-this.R; }
};
(function buildTube(){
  const g=new THREE.CylinderGeometry(tube.R,tube.R,tube.L,30,1,true);
  const outer=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:0x9c6b41,roughness:.85,side:THREE.DoubleSide}));
  outer.rotation.x=Math.PI/2;outer.position.copy(tube.center);outer.castShadow=true;outer.receiveShadow=true;scene.add(outer);
  const inner=new THREE.Mesh(new THREE.CylinderGeometry(tube.R-.07,tube.R-.07,tube.L,28,1,true),
    new THREE.MeshStandardMaterial({color:0x5c3b22,roughness:.95,side:THREE.BackSide}));
  inner.rotation.x=Math.PI/2;inner.position.copy(tube.center);inner.receiveShadow=true;scene.add(inner);
  [-1,1].forEach(s=>{const rim=new THREE.Mesh(new THREE.TorusGeometry(tube.R-.03,.08,8,30),MAT.wood3);
    rim.position.set(tube.center.x,tube.center.y,tube.center.z+s*tube.L/2);rim.castShadow=true;scene.add(rim);});
  /* упоры, чтобы не катилась */
  [-2.4,2.4].forEach(o=>{const ch=new THREE.Mesh(new THREE.BoxGeometry(tube.R*2.5,.3,.5),MAT.wood3);
    ch.position.set(tube.center.x,.14,tube.center.z+o);ch.receiveShadow=true;ch.castShadow=true;scene.add(ch);});
})();

/* ─────────────────────────── 6. МИСКА + ПОИЛКА ──────────────────────────── */
const bowl={x:.8,z:5.0,r:1.15,eater:null};
(function buildBowl(){
  const pts=[];for(let i=0;i<=12;i++){const t=i/12;pts.push(new THREE.Vector2(.14+t*1.0,.02+t*t*.44));}
  const b=new THREE.Mesh(new THREE.LatheGeometry(pts,34),MAT.ceramic);
  b.position.set(bowl.x,0,bowl.z);b.castShadow=true;b.receiveShadow=true;scene.add(b);
  const seeds=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.075,0),MAT.seed,110);
  const m=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),p=new THREE.Vector3(),s=new THREE.Vector3(1,1,1);
  bowl.seeds=[];
  for(let i=0;i<110;i++){const a=rnd(0,TAU),rr=Math.sqrt(Math.random())*.86;
    const y=.05+rr*rr*.42+rnd(0,.09);
    p.set(bowl.x+Math.cos(a)*rr,y,bowl.z+Math.sin(a)*rr);e.set(rnd(0,TAU),rnd(0,TAU),rnd(0,TAU));q.setFromEuler(e);
    m.compose(p,q,s);seeds.setMatrixAt(i,m);bowl.seeds.push({p:p.clone(),q:q.clone(),y:y,eat:0});}
  seeds.instanceMatrix.needsUpdate=true;seeds.castShadow=true;scene.add(seeds);bowl.mesh=seeds;
})();

const water={x:10.4,z:5.6,spot:new THREE.Vector3(9.15,0,5.6),dripT:0};
(function buildWater(){
  const g=new THREE.Group();g.position.set(water.x,0,water.z);scene.add(g);
  const bot=new THREE.Mesh(new THREE.CylinderGeometry(.44,.44,2.1,20,1,true),MAT.plastic);
  bot.position.y=1.95;g.add(bot);
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(.46,.46,.22,20),MAT.metalDark);cap.position.y=3.05;g.add(cap);
  const wtr=new THREE.Mesh(new THREE.CylinderGeometry(.4,.4,1.55,20),MAT.water);wtr.position.y=1.62;g.add(wtr);
  const spout=new THREE.Mesh(new THREE.CylinderGeometry(.075,.06,.5,10),MAT.metal);spout.position.y=.66;g.add(spout);
  const ball=new THREE.Mesh(new THREE.SphereGeometry(.1,12,10),MAT.metal);ball.position.y=.42;g.add(ball);
  [-.5,.5].forEach(s=>{const w=new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,3.2,6),MAT.metal);
    w.position.set(0,1.9,s*.52);g.add(w);});
  const holder=new THREE.Mesh(new THREE.BoxGeometry(.3,.3,1.6),MAT.metalDark);holder.position.set(.45,2.6,0);g.add(holder);
  water.drip=new THREE.Mesh(new THREE.SphereGeometry(.07,8,6),MAT.water);scene.add(water.drip);
  water.drip.visible=false;
})();

/* деревянный мостик-пандус для красоты (декор, без коллизии высоты) */
(function bridge(){
  const b=new THREE.Mesh(new THREE.BoxGeometry(5.2,.16,1.5),MAT.wood2);
  b.position.set(2.6,.34,-5.6);b.rotation.y=.25;b.castShadow=true;b.receiveShadow=true;scene.add(b);
  [[-.9],[.9]].forEach(o=>{const l=new THREE.Mesh(new THREE.BoxGeometry(.28,.34,1.6),MAT.wood3);
    l.position.set(2.6+o[0]*2.2,.17,-5.6+ (o[0]>0?-.55:.55));l.castShadow=true;scene.add(l);});
})();

/* пылинки в луче света */
const dust=(function(){
  const N=420,pos=new Float32Array(N*3),vel=[];
  for(let i=0;i<N;i++){pos[i*3]=rnd(-16,16);pos[i*3+1]=rnd(.5,17);pos[i*3+2]=rnd(-11,11);vel.push(rnd(.08,.3));}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const p=new THREE.Points(g,new THREE.PointsMaterial({size:.16,map:dotTex,transparent:true,opacity:.5,
    depthWrite:false,blending:THREE.AdditiveBlending,color:0xffe4bb}));
  scene.add(p);return {p:g,vel:vel,N:N};
})();

/* ─────────────────────────── 7. ХОМЯК ───────────────────────────────────── */
const FURS=[
 {name:'ПЫЖ',    fur:0xd9973f, belly:0xf7e4c6, patch:0xc07f2d, tag:0xf7b32b, css:'#f7b32b'},
 {name:'БУБЛИК', fur:0xb85f2e, belly:0xf0d7ba, patch:0x9a4a20, tag:0xff6f52, css:'#ff6f52'},
 {name:'ТУМБА',  fur:0x8a8177, belly:0xdcd6cb, patch:0x6e655c, tag:0x79c2ff, css:'#79c2ff'},
 {name:'СНЕЖАНА',fur:0xece0cf, belly:0xffffff, patch:0xbfb3a2, tag:0x48d8a4, css:'#48d8a4'},
 {name:'ГРАФ',   fur:0x4a3a31, belly:0xa9927c, patch:0x35281f, tag:0xc48cff, css:'#c48cff'}
];

function makeHamster(cfg,i){
  const root=new THREE.Group();scene.add(root);
  const fur=new THREE.MeshStandardMaterial({color:cfg.fur,roughness:.95,bumpMap:furTex,bumpScale:.012});
  const patch=new THREE.MeshStandardMaterial({color:cfg.patch,roughness:.95,bumpMap:furTex,bumpScale:.012});
  const bellyM=new THREE.MeshStandardMaterial({color:cfg.belly,roughness:.97});
  const tagM=new THREE.MeshStandardMaterial({color:cfg.tag,roughness:.35,emissive:cfg.tag,emissiveIntensity:.25});

  const body=new THREE.Group();root.add(body);

  const torso=new THREE.Mesh(new THREE.SphereGeometry(.6,24,18),fur);
  torso.scale.set(ШИРИНА_ЗВЕРЯ/.6*.5, .72, 1.30);torso.position.set(0,.5,-.05);
  torso.castShadow=true;torso.receiveShadow=true;body.add(torso);

  const saddle=new THREE.Mesh(new THREE.SphereGeometry(.585,22,16),patch);
  saddle.scale.set(ШИРИНА_ЗВЕРЯ/.6*.49,.62,1.16);saddle.position.set(0,.63,-.12);
  saddle.castShadow=true;body.add(saddle);

  const belly=new THREE.Mesh(new THREE.SphereGeometry(.585,22,16),bellyM);
  belly.scale.set(ШИРИНА_ЗВЕРЯ/.6*.49,.66,1.20);belly.position.set(0,.41,.02);
  belly.castShadow=true;body.add(belly);

  /* голова — отдельной группой, чтобы кивать/наклонять */
  const head=new THREE.Group();head.position.set(0,.63,.62);body.add(head);
  const skull=new THREE.Mesh(new THREE.SphereGeometry(.345,22,16),fur);
  skull.scale.set(1,.94,1.06);skull.castShadow=true;head.add(skull);
  const muzzle=new THREE.Mesh(new THREE.SphereGeometry(.185,16,12),bellyM);
  muzzle.position.set(0,-.06,.26);muzzle.scale.set(1,.78,.95);muzzle.castShadow=true;head.add(muzzle);
  const nose=new THREE.Mesh(new THREE.SphereGeometry(.055,10,8),MAT.pink);nose.position.set(0,-.02,.42);head.add(nose);
  const cheeks=[];[-1,1].forEach(s=>{const c=new THREE.Mesh(new THREE.SphereGeometry(.165,14,12),bellyM);
    c.position.set(s*.2,-.07,.14);c.scale.set(1,.9,1.05);c.castShadow=true;head.add(c);cheeks.push(c);});
  const eyes=[],eyeGroups=[];
  [-1,1].forEach(s=>{
    const eg=new THREE.Group();eg.position.set(s*.175,.075,.265);head.add(eg);
    const e=new THREE.Mesh(new THREE.SphereGeometry(.082,14,12),MAT.eyeW);eg.add(e);
    const pu=new THREE.Mesh(new THREE.SphereGeometry(.052,12,10),MAT.eyeB);pu.position.set(s*.012,-.005,.055);eg.add(pu);
    const gl=new THREE.Mesh(new THREE.SphereGeometry(.018,8,6),MAT.glow);gl.position.set(s*.03,.035,.07);eg.add(gl);
    eyes.push(eg);eyeGroups.push(eg);
  });
  const ears=[];
  [-1,1].forEach(s=>{
    const eg=new THREE.Group();eg.position.set(s*.2,.26,-.02);head.add(eg);
    const o=new THREE.Mesh(new THREE.SphereGeometry(.145,14,10),fur);o.scale.set(1,.35,.85);o.castShadow=true;eg.add(o);
    const inn=new THREE.Mesh(new THREE.SphereGeometry(.1,12,8),MAT.pink);inn.position.set(0,.045,.02);inn.scale.set(1,.3,.8);eg.add(inn);
    const tag=new THREE.Mesh(new THREE.BoxGeometry(.055,.05,.09),tagM);tag.position.set(0,.02,-.11);eg.add(tag);
    ears.push(eg);
  });
  /* усы */
  (function whiskers(){
    const v=[];[-1,1].forEach(s=>{for(let k=0;k<3;k++){
      v.push(s*.08,-.03+k*.035,.42, s*.42, -.09+k*.055, .5+k*.03);}});
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));
    head.add(new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.5})));
  })();

  /* четыре лапы */
  const legs=[];
  [[-1,.44,'FL'],[1,.44,'FR'],[-1,-.5,'BL'],[1,-.5,'BR']].forEach(L=>{
    const g=new THREE.Group();g.position.set(L[0]*.31,.33,L[1]);body.add(g);
    const up=new THREE.Mesh(new THREE.CylinderGeometry(.095,.085,.24,10),fur);
    up.position.y=-.11;up.castShadow=true;g.add(up);
    const paw=new THREE.Mesh(new THREE.SphereGeometry(.105,12,10),bellyM);
    paw.position.set(0,-.235,.035);paw.scale.set(1,.72,1.25);paw.castShadow=true;g.add(paw);
    g.userData.hipY=.33;legs.push(g);
  });

  /* хвост */
  const tail=new THREE.Group();tail.position.set(0,.46,-.78);body.add(tail);
  const t1=new THREE.Mesh(new THREE.SphereGeometry(.1,10,8),fur);t1.scale.set(.8,.8,1.2);tail.add(t1);
  const t2=new THREE.Mesh(new THREE.SphereGeometry(.065,8,6),fur);t2.position.set(0,.02,-.13);tail.add(t2);

  /* невидимый «пикер» для клика */
  const pick=new THREE.Mesh(new THREE.SphereGeometry(.95,10,8),
    new THREE.MeshBasicMaterial({colorWrite:false,depthWrite:false,transparent:true,opacity:0}));
  pick.position.set(0,.6,0);root.add(pick);

  /* кольцо-подсветка */
  const ring=new THREE.Mesh(new THREE.RingGeometry(.72,1.0,28),
    new THREE.MeshBasicMaterial({color:cfg.tag,transparent:true,opacity:0,side:THREE.DoubleSide,depthWrite:false}));
  ring.rotation.x=-Math.PI/2;scene.add(ring);

  const h={
    name:cfg.name, css:cfg.css, index:i, root:root, ring:ring,
    parts:{body:body,torso:torso,belly:belly,saddle:saddle,head:head,ears:ears,eyes:eyeGroups,legs:legs,tail:tail,cheeks:cheeks},
    pos:new THREE.Vector3(rnd(-3,3),0,rnd(-4,4)), yaw:rnd(0,TAU), speed:0,
    state:'idle', stateT:0, intent:null, goal:new THREE.Vector3(), arriveEps:.28, arrived:false,
    maxSpeed:rnd(2.15,2.85), accel:5.4,
    stepPhase:rnd(0,TAU), stepLength:1.12, footSpeed:0, phaseRate:0, prevPhase:0,
    runSpeed:0, runTarget:false, runMax:rnd(3.2,4.6), runTime:0,
    breathRate:rnd(1.5,2.1), blinkT:rnd(1,4), blink:0, earT:0, nextEar:rnd(1,5),
    jumpV:0, jumpY:0, air:false, squash:0,
    idleWait:rnd(.6,2.4), eatTime:0, drinkTime:0, note:'', noteT:0,
    exempt:false, tubeDir:1, enterT:0, exitT:0, followMe:false,
    wheelSign:+1
  };
  pick.userData.h=h;root.userData.h=h;
  return h;
}
const hamsters=FURS.map(makeHamster);
let pickables=[];hamsters.forEach(h=>h.root.traverse(o=>{if(o.geometry&&o.material&&o.material.colorWrite===false)pickables.push(o);}));

/* ─────────────────────────── 8. ТЕЛА СТОЛКНОВЕНИЙ ───────────────────────── */
const PAD=.52; // «радиус» зверя для раздувания тел (Minkowski)
const colliders=[
 {id:'колесо', type:'box',
  minx:wheel.center.x-wheel.halfW-.06, maxx:wheel.center.x+wheel.halfW+.06,
  minz:wheel.center.z-wheel.R-.14,     maxz:wheel.center.z+wheel.R+.14},
 {id:'труба', type:'box',
  minx:tube.center.x-tube.R, maxx:tube.center.x+tube.R,
  minz:tube.center.z-tube.L/2, maxz:tube.center.z+tube.L/2},
 {id:'миска', type:'circle', x:bowl.x, z:bowl.z, r:bowl.r+.06},
 {id:'домик', type:'box', minx:-10.1,maxx:-6.3,minz:-6.7,maxz:-3.1},
 {id:'поилка',type:'circle', x:water.x, z:water.z, r:.5}
];
const sim={
  pushouts:0, violations:0, paused:false, t:0, frames:0, fps:60,
  selected:null, intro:true, introT:0, idleCam:0, lastInput:0
};

/* ─────────────────────────── 9. ПОВЕДЕНИЕ (конечный автомат) ────────────── */
const ST={IDLE:'idle',WALK:'walk',WHEEL_IN:'wheel_in',WHEEL_RUN:'wheel_run',WHEEL_OUT:'wheel_out',
          TUBE:'tube',EAT:'eat',DRINK:'drink'};
const TXT={[ST.IDLE]:'стоит, обнюхивает воздух',[ST.WHEEL_IN]:'лезет в колесо',
  [ST.WHEEL_RUN]:'бежит в колесе',[ST.WHEEL_OUT]:'вылезает из колеса',
  [ST.TUBE]:'ползёт по трубе',[ST.EAT]:'грызёт зёрна',[ST.DRINK]:'пьёт из поилки'};

function setNote(h,s){h.note=s;h.noteT=3.4;}
function log(m){const ul=document.getElementById('log');const li=document.createElement('li');
  li.textContent='› '+m;ul.prepend(li);while(ul.children.length>5)ul.lastChild.remove();}

function insideAny(x,z,pad){
  for(const c of colliders){
    if(c.type==='box'){if(x>c.minx-pad&&x<c.maxx+pad&&z>c.minz-pad&&z<c.maxz+pad)return c.id;}
    else{if(Math.hypot(x-c.x,z-c.z)<c.r+pad)return c.id;}
  } return null;
}
function freeSpot(pad){
  for(let k=0;k<40;k++){
    const x=rnd(-CAGE.hx+1.4,CAGE.hx-1.4), z=rnd(-CAGE.hz+1.4,CAGE.hz-1.4);
    if(!insideAny(x,z,pad||1.5))return new THREE.Vector3(x,0,z);
  }
  return new THREE.Vector3(0,0,0);
}
function toState(h,s){h.state=s;h.stateT=0;h.exempt=(s===ST.WHEEL_IN||s===ST.WHEEL_RUN||s===ST.WHEEL_OUT||s===ST.TUBE);}
function toIdle(h,note){toState(h,ST.IDLE);h.idleWait=rnd(.8,3.2);h.speed=0;if(note)setNote(h,note);}

function chooseActivity(h){
  const opts=[];
  if(!wheel.user&&Math.abs(wheel.omega)<.3)opts.push('wheel','wheel');
  if(!tube.user)opts.push('tube');
  opts.push('bowl','wander','wander','water');
  let it=opts[(Math.random()*opts.length)|0];
  if(it==='wheel'&&wheel.user){setNote(h,'колесо занято — иду бродить');it='wander';}
  if(it==='tube'&&tube.user){setNote(h,'труба занята');it='wander';}
  startIntent(h,it);
}
function startIntent(h,it){
  h.intent=it;
  if(it==='wheel'){toState(h,ST.WALK);h.goal.copy(wheel.stand);h.arriveEps=.3;
    h.statusTxt='идёт к колесу';}
  else if(it==='tube'){
    const nearEnd=(h.pos.z<tube.center.z)?-1:1;
    h.tubeDir=nearEnd;
    toState(h,ST.WALK);
    h.goal.set(tube.center.x,0,tube.center.z+nearEnd*(tube.L/2+1.7));h.arriveEps=.3;
    h.statusTxt='идёт к трубе';
  }
  else if(it==='bowl'){
    const d=new THREE.Vector3(h.pos.x-bowl.x,0,h.pos.z-bowl.z);
    if(d.lengthSq()<.01)d.set(0,0,1);d.normalize();
    toState(h,ST.WALK);h.goal.set(bowl.x+d.x*(bowl.r+.72),0,bowl.z+d.z*(bowl.r+.72));h.arriveEps=.3;
    h.statusTxt='идёт к миске';
  }
  else if(it==='water'){toState(h,ST.WALK);h.goal.copy(water.spot);h.arriveEps=.32;h.statusTxt='идёт к поилке';}
  else{toState(h,ST.WALK);h.goal.copy(freeSpot(1.4));h.arriveEps=.5;h.statusTxt='бродит по клетке';}
}
function onArrive(h){
  if(h.intent==='wheel'){
    if(wheel.user||Math.abs(wheel.omega)>.3){startIntent(h,'wander');setNote(h,'колесо недоступно');return;}
    wheel.user=h;h.enterT=0;toState(h,ST.WHEEL_IN);h.runSpeed=0;log(h.name+': входит в колесо');
  } else if(h.intent==='tube'){
    if(tube.user){startIntent(h,'wander');setNote(h,'труба занята');return;}
    tube.user=h;toState(h,ST.TUBE);log(h.name+': входит в трубу через торец');
  } else if(h.intent==='bowl'){
    toState(h,ST.EAT);h.eatTime=rnd(4.5,8.5);bowl.eater=h;log(h.name+' у миски');
  } else if(h.intent==='water'){
    toState(h,ST.DRINK);h.drinkTime=rnd(2.5,4.5);log(h.name+' пьёт');
  } else {
    toIdle(h);
  }
}
function startWheelExit(h){
  toState(h,ST.WHEEL_OUT);h.exitT=0;log(h.name+': выходит из колеса');
}

/* ─────────────── 10. ФИЗИКА КОЛЕСА: ω берётся ИЗ скорости лап ─────────────── */
const RUN_ACCEL=3.4;
function updateWheel(dt){
  const d=wheel.driving?wheel.user:null;
  if(d){
    /* линейная скорость лап зверя (разгон/торможение с ограниченным ускорением) */
    d.runSpeed=approach(d.runSpeed,d.runTarget?d.runMax:0,RUN_ACCEL*dt);
    wheel.footSpeed=d.runSpeed;
    wheel.omega=d.wheelSign*d.runSpeed/wheel.R;      // ← ω = v / R
  }else{
    wheel.footSpeed=wheel.driving?wheel.footSpeed:0;
    /* пустое колесо: сухое + вязкое трение ⇒ ω затухает к нулю */
    const mag=Math.abs(wheel.omega), dec=(wheel.dryFriction+wheel.viscFriction*mag)*dt;
    wheel.omega = mag<=dec ? 0 : wheel.omega-Math.sign(wheel.omega)*dec;
  }
  wheel.angle+=wheel.omega*dt;
  drum.rotation.x=wheel.angle;
  wheel.rimSpeed=Math.abs(wheel.omega)*wheel.R;
  wheel.mismatchPct=wheel.footSpeed>.06?Math.abs(wheel.rimSpeed-wheel.footSpeed)/wheel.footSpeed*100:0;
}

/* ─────────────── 11. ДВИЖЕНИЕ ────────────────────────────────────────────── */
function advancePhase(h,dist){
  h.prevPhase=h.stepPhase;
  h.stepPhase+=(dist/h.stepLength)*TAU;             // ← фаза от ПРОЙДЕННОГО ПУТИ
}
function resolveObstacles(h){
  if(h.exempt)return;
  for(let it=0;it<2;it++)for(const c of colliders){
    let hit=false;
    if(c.type==='box'){
      const a=c.minx-PAD,b=c.maxx+PAD,cc=c.minz-PAD,d2=c.maxz+PAD,p=h.pos;
      if(p.x>a&&p.x<b&&p.z>cc&&p.z<d2){
        const l=p.x-a,r=b-p.x,u=p.z-cc,dd=d2-p.z,m=Math.min(l,r,u,dd);
        if(m===l)p.x=a;else if(m===r)p.x=b;else if(m===u)p.z=cc;else p.z=d2;
        hit=true;
      }
    }else{
      const dx=h.pos.x-c.x,dz=h.pos.z-c.z,rr=c.r+PAD,dd=Math.hypot(dx,dz);
      if(dd<rr){const nx=dd<1e-4?0:dx/dd,nz=dd<1e-4?1:dz/dd;
        h.pos.x=c.x+nx*rr;h.pos.z=c.z+nz*rr;hit=true;}
    }
    if(hit&&it===0){sim.pushouts++;if(h.stateT<.35)log(h.name+' вытолкнут: '+c.id);}
  }
  /* проверка «не прошёл насквозь»: истинное попадание в тело */
  if(!h.exempt&&insideAny(h.pos.x,h.pos.z,0)){sim.violations++;
    const s=freeSpot(1.6);h.pos.x=s.x;h.pos.z=s.z;}
}
function separate(){
  const minD=.94;
  for(let i=0;i<hamsters.length;i++)for(let j=i+1;j<hamsters.length;j++){
    const A=hamsters[i],B=hamsters[j];
    if(A.exempt&&B.exempt)continue;
    let dx=B.pos.x-A.pos.x,dz=B.pos.z-A.pos.z,d=Math.hypot(dx,dz);
    if(d<minD&&d>1e-4){
      const ov=(minD-d)*.5,nx=dx/d,nz=dz/d;
      if(!A.exempt&&!B.exempt){A.pos.x-=nx*ov;A.pos.z-=nz*ov;B.pos.x+=nx*ov;B.pos.z+=nz*ov;}
      else if(!A.exempt){A.pos.x-=nx*ov*2;A.pos.z-=nz*ov*2;}
      else {B.pos.x+=nx*ov*2;B.pos.z+=nz*ov*2;}
    }else if(d<=1e-4&&!A.exempt){A.pos.x+=rnd(-.2,.2);A.pos.z+=rnd(-.2,.2);}
  }
}
function clampCage(h){
  h.pos.x=clamp(h.pos.x,-CAGE.hx+.75,CAGE.hx-.75);
  h.pos.z=clamp(h.pos.z,-CAGE.hz+.75,CAGE.hz-.75);
}
function integrateJump(h,dt){
  if(h.air){h.jumpV-=26*dt;h.jumpY+=h.jumpV*dt;
    if(h.jumpY<=0){h.jumpY=0;h.air=false;h.squash=1;}}
}
function steerFree(h,dt){
  const to=new THREE.Vector3().copy(h.goal);to.y=0;
  const d=to.distanceTo(h.pos);
  if(d<h.arriveEps){h.arrived=true;h.speed=approach(h.speed,0,9*dt);}
  else{
    h.arrived=false;
    to.sub(h.pos).normalize();
    const tgt=h.maxSpeed*clamp(d/1.5,.28,1);
    h.speed=approach(h.speed,tgt,h.accel*dt);
    h.yaw=angLerp(h.yaw,Math.atan2(to.x,to.z),1-Math.exp(-7.5*dt));
  }
  const bx=h.pos.x,bz=h.pos.z;
  if(h.speed>.0008){h.pos.x+=Math.sin(h.yaw)*h.speed*dt;h.pos.z+=Math.cos(h.yaw)*h.speed*dt;}
  resolveObstacles(h);clampCage(h);
  const moved=Math.hypot(h.pos.x-bx,h.pos.z-bz);
  advancePhase(h,moved);
  h.footSpeed=lerp(h.footSpeed,moved/dt,.35);
}
/* позы внутри колеса/трубы — без единой телепортации */
function scripted(h,dt){
  const bx=h.pos.x,bz=h.pos.z;
  if(h.state===ST.WHEEL_IN){
    h.enterT=Math.min(1,h.enterT+dt/1.5);
    const t=h.enterT;
    let x,z,yaw;
    if(t<.62){const u=easeIO(t/.62);
      x=lerp(wheel.stand.x,wheel.center.x-.15,u);z=wheel.center.z;yaw=-Math.PI/2;}
    else{const u=easeIO((t-.62)/.38);
      x=lerp(wheel.center.x-.15,wheel.center.x,u);z=wheel.center.z;yaw=angLerp(-Math.PI/2,0,u);}
    h.pos.x=x;h.pos.z=z;h.yaw=yaw;
    h.pos.y=lerp(0,wheel.contactY,sstep(.05,.6,t));
    advancePhase(h,Math.hypot(h.pos.x-bx,h.pos.z-bz)+.0);
    h.footSpeed=lerp(h.footSpeed,Math.hypot(h.pos.x-bx,h.pos.z-bz)/dt,.3);
    if(t>=1){toState(h,ST.WHEEL_RUN);h.runTarget=true;h.runTime=rnd(6,15);log(h.name+' бежит: ω = v/R');}
  }
  else if(h.state===ST.WHEEL_RUN){
    /* зверь стоит НИЖНЕЙ точкой обода; лапы шагают со скорости обода */
    h.pos.set(wheel.center.x,wheel.contactY,wheel.center.z);
    h.yaw=angLerp(h.yaw,0,1-Math.exp(-9*dt));
    advancePhase(h,wheel.rimSpeed*dt);              // ← шаг привязан к ободу
    h.footSpeed=wheel.rimSpeed;
  }
  else if(h.state===ST.WHEEL_OUT){
    h.exitT=Math.min(1,h.exitT+dt/1.05);
    const t=h.exitT;let x,z,yaw;
    if(t<.42){const u=easeIO(t/.42);
      x=wheel.center.x;z=wheel.center.z;yaw=angLerp(0,-Math.PI/2,u);}
    else{const u=easeIO((t-.42)/.58);
      x=lerp(wheel.center.x,wheel.stand.x,u);z=wheel.center.z;yaw=-Math.PI/2;}
    h.pos.x=x;h.pos.z=z;h.yaw=yaw;
    h.pos.y=lerp(wheel.contactY,0,sstep(.35,1,t));
    advancePhase(h,wheel.rimSpeed*dt+Math.hypot(h.pos.x-bx,h.pos.z-bz));
    h.footSpeed=lerp(h.footSpeed,wheel.rimSpeed,.3);
    if(t>=1){h.pos.y=0;wheel.user=null;toIdle(h,'выбежал');}
  }
  else if(h.state===ST.TUBE){
    const dir=h.tubeDir;
    const zEnd=tube.center.z-dir*(tube.L/2+1.9);
    h.pos.x=lerp(h.pos.x,tube.center.x,1-Math.exp(-10*dt));   // точно по оси
    h.pos.z+=dir*1.9*dt;
    h.yaw=angLerp(h.yaw,dir>0?0:Math.PI,1-Math.exp(-9*dt));
    /* лапы — на внутреннем дне трубы */
    h.pos.y=lerp(h.pos.y,tube.innerFloorY,1-Math.exp(-12*dt));
    advancePhase(h,1.9*dt);
    h.footSpeed=lerp(h.footSpeed,1.9,.3);
    if((dir>0&&h.pos.z>zEnd)||(dir<0&&h.pos.z<zEnd)){
      tube.user=null;h.pos.y=0;toIdle(h,'вылез из трубы');log(h.name+': вышел из трубы через торец');
    }
  }
}
/* ─────────────── 12. АНИМАЦИЯ ЗВЕРЯ ──────────────────────────────────────── */
const OFF=[0,Math.PI,Math.PI,0];   // диагональные пары: FL+BR, FR+BL
function pose(h,dt,t){
  const P=h.parts;
  let speedN=clamp(h.footSpeed/2.6,0,1.5);
  if(h.state===ST.WHEEL_RUN)speedN=clamp(wheel.rimSpeed/2.6,0,1.5);
  const amp=.52*clamp(speedN,0,1.25);
  P.legs.forEach((L,i)=>{
    const ph=h.stepPhase+OFF[i];
    const air=h.air?.35:1;
    L.rotation.x=Math.sin(ph)*amp*air + (h.air?(i<2?-.5:.5):0);
    L.position.y=L.userData.hipY+Math.max(0,Math.cos(ph))*.055*amp*air;
  });
  /* дыхание и покачивание */
  const rest=(h.state===ST.IDLE);
  const br=1+Math.sin(t*h.breathRate+h.index)*(rest?.04:.014);
  P.body.scale.set(1,br,1);
  const bob=h.air?0:Math.abs(Math.sin(h.stepPhase))*.035*clamp(speedN,0,1);
  P.body.position.y=bob;
  h.squash=Math.max(0,h.squash-dt*4.5);
  if(h.squash>0)P.body.scale.y*= (1-h.squash*.16);

  /* голова: кивок, наклон за едой, подъём к поилке, осмотр */
  let hx=Math.sin(h.stepPhase)* .06*clamp(speedN,0,1), hz=0, hy=Math.sin(t*.7+h.index*2)*.08;
  if(h.state===ST.EAT){hx=-.62+Math.sin(t*11)*.09;hy=0;}
  if(h.state===ST.DRINK){hx=.55+Math.sin(t*13)*.07;hy=0;}
  if(h.state===ST.IDLE){hy=Math.sin(t*.55+h.index)*.5*Math.max(0,Math.sin(t*.28+h.index));}
  if(h.air)hx=-.3;
  P.head.rotation.x=lerp(P.head.rotation.x,hx,1-Math.exp(-9*dt));
  P.head.rotation.y=lerp(P.head.rotation.y,hy,1-Math.exp(-6*dt));
  P.head.rotation.z=lerp(P.head.rotation.z,hz,1-Math.exp(-6*dt));
  /* жуёт у миски */
  if(h.state===ST.EAT){const ch=Math.abs(Math.sin(t*11))*.09;P.cheeks.forEach(c=>c.scale.z=1.05+ch);}
  else P.cheeks.forEach(c=>c.scale.z=lerp(c.scale.z,1.05,1-Math.exp(-8*dt)));

  /* уши: редкие подёргивания */
  h.nextEar-=dt;
  if(h.nextEar<=0){h.earT=.45;h.nextEar=rnd(1.6,6);}
  if(h.earT>0){h.earT-=dt;const s=Math.sin(h.earT*42)*h.earT;P.ears[0].rotation.z=s*.9;P.ears[1].rotation.z=-s*.6;}
  else{P.ears[0].rotation.z=lerp(P.ears[0].rotation.z,0,1-Math.exp(-6*dt));
       P.ears[1].rotation.z=lerp(P.ears[1].rotation.z,0,1-Math.exp(-6*dt));}
  P.ears[0].rotation.x=P.ears[1].rotation.x=Math.sin(t*1.3+h.index)*.06;

  /* моргание */
  h.blinkT-=dt;
  if(h.blinkT<=0){h.blink=.13;h.blinkT=rnd(2,6);}
  if(h.blink>0)h.blink-=dt;
  const es=h.blink>0?.12:(h.state===ST.EAT&&h.stateT>h.eatTime-1.2?.25:1);
  P.eyes.forEach(e=>e.scale.y=lerp(e.scale.y,es,1-Math.exp(-22*dt)));

  /* хвост */
  P.tail.rotation.y=Math.sin(t*2.2+h.index)*.28;
  P.tail.rotation.x=-.2+Math.sin(t*1.7)*.12;

  /* прыжок: лапы врозь, тельце сжимается при посадке */
  const jy=h.jumpY;
  h.root.position.set(h.pos.x,h.pos.y+jy,h.pos.z);
  h.root.rotation.y=h.yaw;
  h.root.rotation.z=lerp(h.root.rotation.z,clamp(-(h.yawDiff||0)*.02,-.14,.14),1-Math.exp(-6*dt));

  /* кольцо выделения */
  const sel=(sim.selected===h);
  h.ring.position.set(h.pos.x,h.pos.y+.05,h.pos.z);
  h.ring.material.opacity=lerp(h.ring.material.opacity,sel?.55:0,1-Math.exp(-8*dt));
  h.ring.rotation.z+=dt*(sel?1.6:.4);
  h.ring.scale.setScalar(1+Math.sin(t*3)*.04);
}

/* ─────────────── 13. МЫСЛЬ ───────────────────────────────────────────────── */
function think(h,dt){
  h.stateT+=dt;
  if(h.noteT>0)h.noteT-=dt;else h.note='';
  switch(h.state){
    case ST.IDLE:
      if(h.stateT>h.idleWait)chooseActivity(h);
      break;
    case ST.WALK:
      if(h.arrived)onArrive(h);
      if(h.stateT>20){h.goal.copy(freeSpot(1.4));h.stateT=0;setNote(h,'заблудился, иду иначе');}
      break;
    case ST.EAT:
      if(h.stateT>h.eatTime){bowl.eater=null;toIdle(h,'наелся');}
      break;
    case ST.DRINK:
      if(h.stateT>h.drinkTime)toIdle(h);
      break;
    case ST.WHEEL_RUN:
      if(h.stateT>h.runTime)h.runTarget=false;
      if(!h.runTarget&&h.runSpeed<.06)startWheelExit(h);
      break;
  }
}

/* ─────────────── 14. ПРОВЕРКИ (читаются снаружи) ─────────────────────────── */
const _box=new THREE.Box3(),_v=new THREE.Vector3();
function measure(){
  /* габарит бегуна против радиуса обода + ошибка нижней точки */
  const r=wheel.driving?wheel.user:(wheel.user||null);
  if(r){
    _box.setFromObject(r.parts.body);
    let maxR=0;
    for(let i=0;i<8;i++){
      _v.set(i&1?_box.max.x:_box.min.x, i&2?_box.max.y:_box.min.y, i&4?_box.max.z:_box.min.z);
      const dz=_v.z-wheel.center.z, dy=_v.y-wheel.center.y;
      maxR=Math.max(maxR,Math.hypot(dy,dz));
    }
    wheel.bodyRadius=maxR;
    wheel.lowErr=Math.hypot(r.pos.x-wheel.center.x,r.pos.z-wheel.center.z)
                +Math.abs(-(r.pos.y-wheel.center.y)-wheel.R);
  }else{wheel.bodyRadius=0;wheel.lowErr=0;}
  /* труба */
  const tu=tube.user;
  if(tu&&tu.state===ST.TUBE){
    tube.devX=Math.abs(tu.pos.x-tube.center.x);
    tube.footAboveFloor=tu.pos.y-tube.innerFloorY;
    tube.alongPct=clamp((tu.pos.z-(tube.center.z-tube.tubeDir*tube.L/2))/(tube.DirLen||tube.L)*100,-40,140);
  }else{tube.devX=0;tube.footAboveFloor=0;}
  tube.DirLen=tube.L;
  /* фаза в покое */
  let idleRate=0,anyIdle=false;
  for(const h of hamsters)if(h.state===ST.IDLE){anyIdle=true;idleRate=Math.max(idleRate,h.phaseRate);}
  sim.idlePhaseRate=anyIdle?idleRate:null;
}
function runChecks(){
  const running=wheel.driving;
  return {
    wheel:{R:+wheel.R.toFixed(3),omega:+wheel.omega.toFixed(4),footSpeed:+wheel.footSpeed.toFixed(4),
      rimSpeed:+wheel.rimSpeed.toFixed(4),mismatchPct:+wheel.mismatchPct.toFixed(4),
      bodyMaxRadius:+wheel.bodyRadius.toFixed(3),fits:wheel.bodyRadius<wheel.R,
      lowestPointError:+wheel.lowErr.toFixed(6)},
    tube:{R:+tube.R.toFixed(3),axisDeviationX:+tube.devX.toFixed(6),footAboveInnerFloor:+tube.footAboveFloor.toFixed(4)},
    world:{obstaclePenetrations:sim.violations,pushouts:sim.pushouts,
      idlePhaseRatePerSec:sim.idlePhaseRate===null?null:+sim.idlePhaseRate.toFixed(6)}
  };
}

/* ─────────────── 15. HUD ─────────────────────────────────────────────────── */
const rosterList=document.getElementById('rosterList');
hamsters.forEach((h,i)=>{
  const li=document.createElement('li');li.className='hrow';li.style.setProperty('--c',h.css);
  li.style.animationDelay=(0.35+i*.07)+'s';
  li.innerHTML=`<button class="hbtn"><span class="dot"></span>
    <div class="hm"><b>${h.name}</b><span class="st">…</span></div>
    <div class="gait">${'<i></i>'.repeat(4)}</div><div class="sp"><i></i></div></button>`;
  rosterList.appendChild(li);
  h.ui={row:li,st:li.querySelector('.st'),dots:[...li.querySelectorAll('.gait i')],bar:li.querySelector('.sp i')};
  li.addEventListener('click',()=>{toggleFollow(h);});
});
const CHK=[
 {k:'rim',  t:'|ω|·R = v лап (<5 %)'},
 {k:'decay',t:'пустое колесо: ω→0'},
 {k:'fit',  t:'габарит < R, лапы внизу'},
 {k:'axis', t:'в трубе — по оси, вход с торца'},
 {k:'solid',t:'сквозь тела не проходит'},
 {k:'phase',t:'в покое фаза стоит'}
];
const checksEl=document.getElementById('checks');
checksEl.innerHTML=CHK.map(c=>`<div class="chk" data-k="${c.k}"><s></s><span>${c.t}</span><b>—</b></div>`).join('');
const chkEls={};[...checksEl.children].forEach(el=>chkEls[el.dataset.k]={el,b:el.querySelector('b')});
const $=id=>document.getElementById(id);

function toggleFollow(h){
  const on=!h.followMe;
  hamsters.forEach(x=>x.followMe=false);
  hamsters.forEach(x=>x.ui.row.classList.toggle('sel',x===h&&on));
  h.followMe=on;sim.selected=on?h:null;
  if(on)log('камера следит за: '+h.name);else log('камера свободна');
}
function statusText(h){
  if(h.note)return h.note;
  if(h.state===ST.WALK)return h.statusTxt||'идёт';
  if(h.state===ST.IDLE)return ['стоит, обнюхивает воздух','умывает мордочку','замер, слушает','копает носом подстилку'][h.index%4];
  return TXT[h.state]||'';
}
let hudTick=0;
function hud(dt){
  hudTick+=dt;if(hudTick<.06)return;hudTick=0;
  hamsters.forEach(h=>{
    const s=statusText(h);
    if(h.ui.st.textContent!==s)h.ui.st.textContent=s;
    h.ui.st.classList.toggle('hot',h.state===ST.WHEEL_RUN||h.state===ST.TUBE);
    const sp=(h.state===ST.WHEEL_RUN?wheel.rimSpeed:h.footSpeed);
    h.ui.bar.style.width=clamp(sp/4.6*100,0,100)+'%';
    h.ui.dots.forEach((d,i)=>{const v=Math.sin(h.stepPhase+OFF[i]);
      d.style.opacity=(.18+Math.max(0,v)*.82).toFixed(2);
      d.style.transform='scaleY('+(1+Math.max(0,v)*.5).toFixed(2)+')';});
  });
  const u=wheel.driving?wheel.user:(wheel.user||null);
  $('wMode').textContent=wheel.driving?'под бегуном':(wheel.user?'вход/выход':'на выбеге');
  $('wMode').className=wheel.driving?'':'off';
  $('wUser').textContent=u?u.name:'—';
  $('wOmega').textContent=(wheel.omega>=0?'+':'')+wheel.omega.toFixed(3);
  $('wFoot').textContent=wheel.footSpeed.toFixed(3);
  $('wRim').textContent=wheel.rimSpeed.toFixed(3);
  const dm=$('wDiff');
  dm.textContent=u?wheel.mismatchPct.toFixed(2)+' %':'—';
  dm.className=u?(wheel.mismatchPct<5?'ok':'bad'):'';
  $('wBar1').style.width=clamp(wheel.footSpeed/5*100,0,100)+'%';
  $('wBar2').style.width=clamp(wheel.rimSpeed/5*100,0,100)+'%';
  $('wFit').textContent=u?(wheel.bodyRadius.toFixed(2)+' / '+wheel.R.toFixed(2)):'—';
  $('wFit').className=u?(wheel.bodyRadius<wheel.R?'ok':'bad'):'';
  $('wLow').textContent=u?wheel.lowErr.toFixed(4):'—';

  const tu=tube.user&&tube.user.state===ST.TUBE?tube.user:null;
  $('tMode').textContent=tu?'занята':'свободна';$('tMode').className=tu?'':'off';
  $('tUser').textContent=tu?tu.name:'—';
  $('tDev').textContent=tu?tube.devX.toFixed(4):'—';
  $('tDev').className=tu?(tube.devX<.06?'ok':'bad'):'';
  $('tFloor').textContent=tu?tube.footAboveFloor.toFixed(3):'—';
  $('tAlong').textContent=tu?clamp((tu.pos.z-(tube.center.z-tu.tubeDir*tube.L/2))/tube.L*100,-30,130).toFixed(0)+' %':'—';

  /* чипы проверок */
  const setChip=(k,cls,val)=>{chkEls[k].el.className='chk '+cls;chkEls[k].b.textContent=val;};
  if(u)setChip('rim',wheel.mismatchPct<5?'pass':'warn',wheel.mismatchPct.toFixed(2)+' %');
  else setChip('rim','','—');
  if(!wheel.user)setChip('decay',Math.abs(wheel.omega)<.02?'pass':'',Math.abs(wheel.omega)<.02?'0.000':wheel.omega.toFixed(3));
  else setChip('decay','','ожид.');
  if(u)setChip('fit',(wheel.bodyRadius<wheel.R&&wheel.lowErr<.02)?'pass':'warn',wheel.bodyRadius.toFixed(2)+'/'+wheel.R.toFixed(2));
  else setChip('fit','','—');
  if(tu)setChip('axis',(tube.devX<.06)?'pass':'warn',tube.devX.toFixed(4));
  else setChip('axis','','—');
  setChip('solid',sim.violations===0?'pass':'warn',sim.violations+' / '+sim.pushouts);
  if(sim.idlePhaseRate!==null)setChip('phase',sim.idlePhaseRate<1e-3?'pass':'warn',sim.idlePhaseRate.toFixed(5));
  else setChip('phase','','—');
  $('fps').textContent=sim.fps.toFixed(0)+' fps';
}

/* ─────────────── 16. ВВОД ────────────────────────────────────────────────── */
const ray=new THREE.Raycaster(),ptr=new THREE.Vector2();
function jump(h){
  if(h.air)return;
  h.air=true;h.jumpV=rnd(5.2,6.6);log(h.name+' подпрыгнул');
}
function startle(h){
  if(h.state===ST.WHEEL_RUN){h.runTarget=false;jump(h);}
  else if(h.state===ST.TUBE){setNote(h,'замер в трубе');}
  else jump(h);
}
renderer.domElement.addEventListener('pointerdown',e=>{
  sim.lastInput=performance.now();
  ptr.x=(e.clientX/innerWidth)*2-1;ptr.y=-(e.clientY/innerHeight)*2+1;
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(pickables,false);
  if(hit.length){const h=hit[0].object.userData.h;sim.selected=h;startle(h);}
});
renderer.domElement.addEventListener('wheel',()=>{sim.lastInput=performance.now();},{passive:true});
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k>='1'&&k<='5'){const h=hamsters[+k-1];h.followMe?toggleFollow(h):toggleFollow(h);}
  if(k==='h')document.getElementById('hud').classList.toggle('hidden');
  if(k==='r')resetView();
  if(k===' '){sim.paused=!sim.paused;$('bPause').textContent=sim.paused?'▶ пуск':'⏸ пауза';}
});
$('bSpin').onclick=()=>{wheel.user=null;wheel.omega=3.4;log('колесо раскручено вручную: ω=3.4');};
$('bFeed').onclick=()=>{hamsters.forEach(h=>{
  if(h.state===ST.WHEEL_RUN){h.runTarget=false;}
  else if(h.state===ST.TUBE||h.state===ST.WHEEL_IN||h.state===ST.WHEEL_OUT){}
  else startIntent(h,'bowl');});log('все к миске');};
$('bPause').onclick=()=>{sim.paused=!sim.paused;$('bPause').textContent=sim.paused?'▶ пуск':'⏸ пауза';};
$('bView').onclick=resetView;
const HOME={p:new THREE.Vector3(21,15,26),t:new THREE.Vector3(0,3.2,0)};
function resetView(){
  hamsters.forEach(h=>h.followMe=false);sim.selected=null;
  hamsters.forEach(h=>h.ui.row.classList.remove('sel'));
  camera.position.copy(HOME.p);controls.target.copy(HOME.t);controls.autoRotate=false;
}

/* ─────────────── 17. ЦИКЛ ────────────────────────────────────────────────── */
const clock=new THREE.Clock();
function frame(){
  requestAnimationFrame(frame);
  let dt=clock.getDelta();
  dt=Math.min(dt,.05);                       // ограничение дельты при просадках
  sim.fps=lerp(sim.fps,1/Math.max(dt,1e-4),.08);

  /* вступительный наезд камеры */
  if(sim.intro){
    sim.introT+=dt/2.6;const t=easeIO(clamp(sim.introT,0,1));
    camera.position.lerpVectors(new THREE.Vector3(46,34,62),HOME.p,t);
    controls.target.lerpVectors(new THREE.Vector3(0,8,0),HOME.t,t);
    if(sim.introT>=1){sim.intro=false;controls.enabled=true;}
  }else{
    controls.autoRotate=(performance.now()-sim.lastInput>14000)&&!hamsters.some(h=>h.followMe);
    const f=hamsters.find(h=>h.followMe);
    if(f){controls.target.lerp(new THREE.Vector3(f.pos.x,f.pos.y+1.1,f.pos.z),1-Math.exp(-3*dt));}
    else controls.target.lerp(HOME.t,1-Math.exp(-1.2*dt));
  }
  controls.update();

  if(!sim.paused){
    sim.t+=dt;
    for(const h of hamsters)think(h,dt);
    updateWheel(dt);
    for(const h of hamsters){
      if(h.exempt)scripted(h,dt); else steerFree(h,dt);
      integrateJump(h,dt);
      h.phaseRate=Math.abs(h.stepPhase-h.prevPhase)/dt;
    }
    separate();
    for(const h of hamsters)clampCage(h);
    for(const h of hamsters)pose(h,dt,sim.t);
    measure();

    /* зёрна в миске шевелятся, когда кто-то ест */
    if(bowl.eater){
      const m=new THREE.Matrix4(),q=new THREE.Quaternion();
      for(let k=0;k<6;k++){
        const i=(Math.random()*bowl.seeds.length)|0,sd=bowl.seeds[i];
        sd.y=Math.max(.05,sd.y-rnd(.01,.05));
        if(sd.y<=.051)sd.y=rnd(.28,.45);
        m.compose(sd.p.clone().setY(sd.y),sd.q,new THREE.Vector3(1,1,1));
        bowl.mesh.setMatrixAt(i,m);
      }
      bowl.mesh.instanceMatrix.needsUpdate=true;
    }
    /* капля из поилки */
    water.dripT-=dt;
    if(water.dripT<=0&&!water.drip.visible){water.drip.visible=true;water.dripY=.42;water.dripT=rnd(3,7);}
    if(water.drip.visible){water.dripY-=dt*1.9;water.drip.position.set(water.x,water.dripY,water.z);
      if(water.dripY<.02)water.drip.visible=false;}
    /* пылинки */
    const pos=dust.p.geometry.attributes.position;
    for(let i=0;i<dust.N;i++){
      let y=pos.array[i*3+1]+dust.vel[i]*dt*.5;
      if(y>18)y=.4;pos.array[i*3+1]=y;
      pos.array[i*3]+=Math.sin(sim.t*.3+i)*.002;
    }
    pos.needsUpdate=true;
    lampLight.intensity=.72+Math.sin(sim.t*2.3)*.03+Math.sin(sim.t*7.1)*.015;
  }
  hud(dt);
  renderer.render(scene,camera);
}
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
});

/* стартовое расселение: один уже бежит, остальные в делах */
(function seed(){
  hamsters[0].pos.set(wheel.center.x,wheel.contactY,wheel.center.z);
  hamsters[0].yaw=0;wheel.user=hamsters[0];toState(hamsters[0],ST.WHEEL_RUN);
  hamsters[0].runTarget=true;hamsters[0].runTime=14;
  hamsters[1].pos.set(tube.center.x,tube.innerFloorY,tube.center.z-tube.L/2+.6);
  tube.user=hamsters[1];hamsters[1].tubeDir=1;toState(hamsters[1],ST.TUBE);
  hamsters[2].pos.set(bowl.x-.2,0,bowl.z+bowl.r+.75);hamsters[2].yaw=Math.PI;toState(hamsters[2],ST.EAT);
  hamsters[2].eatTime=7;bowl.eater=hamsters[2];
  hamsters[3].pos.copy(freeSpot(1.6));toIdle(hamsters[3]);
  hamsters[4].pos.copy(freeSpot(1.6));toIdle(hamsters[4]);hamsters[4].idleWait=.4;
})();

/* наружу — для проверки числами из консоли */
window.hamsters=hamsters; window.wheel=wheel; window.tube=tube; window.bowl=bowl;
window.sim=sim; window.colliders=colliders; window.runChecks=runChecks;
window.GABARIT={ДЛИНА_ЗВЕРЯ:ДЛИНА_ЗВЕРЯ,ВЫСОТА_ЗВЕРЯ:ВЫСОТА_ЗВЕРЯ,ШИРИНА_ЗВЕРЯ:ШИРИНА_ЗВЕРЯ,
  R_МИН:R_МИН,КОЛЕСО_R:КОЛЕСО_R,КОЛЕСО_Ш:КОЛЕСО_Ш,ТРУБА_R:ТРУБА_R};
log('готово: 5 зверей, ω = v / R');
frame();
})();
</script>
</body>
</html>
```

**Как это читать из консоли:** `runChecks()` отдаёт живые числа — `wheel.mismatchPct`, `wheel.bodyMaxRadius / fits`, `wheel.lowestPointError`, `tube.axisDeviationX`, `tube.footAboveInnerFloor`, `world.obstaclePenetrations`, `world.idlePhaseRatePerSec`. Кнопка «раскрутить колесо» отдаёт барабан на свободное выбегание — видно, как ω затухает от сухого и вязкого трения до нуля.