# 🐠 Живой аквариум — один файл, ноль зависимостей кроме Three.js

Ниже — полностью рабочий `index.html`. Откройте его в браузере: рыбки плавают, прячутся друг от друга, носятся к корму и растут, стекло преломляет свет, стебли водорослей качаются, пузыри срываются с грунта.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>АКВАРИУМ №7 — живая среда</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Manrope:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --abyss:#02101a;
    --deep:#082838;
    --line:rgba(120,220,255,.16);
    --foam:#e9fbff;
    --mute:#8fb6c9;
    --cyan:#5fe3ff;
    --coral:#ff7a3d;
    --sand:#f0c48a;
    --panel:linear-gradient(158deg,rgba(9,34,48,.86),rgba(4,18,28,.62));
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden;background:var(--abyss)}
  body{font-family:'Manrope',system-ui,sans-serif;color:var(--foam);-webkit-font-smoothing:antialiased}
  canvas{display:block;position:fixed;inset:0}

  /* мягкая виньетка поверх сцены */
  .vignette{position:fixed;inset:0;pointer-events:none;z-index:2;
    background:radial-gradient(120% 90% at 50% 40%,transparent 42%,rgba(1,8,14,.62) 100%);
    mix-blend-mode:multiply}

  .hud{position:fixed;inset:0;z-index:3;pointer-events:none;padding:20px;
    display:grid;grid-template-columns:minmax(240px,300px) 1fr minmax(180px,220px);
    grid-template-rows:auto 1fr auto;gap:16px;align-content:space-between}

  .panel{pointer-events:auto;background:var(--panel);border:1px solid var(--line);
    backdrop-filter:blur(16px) saturate(1.35);-webkit-backdrop-filter:blur(16px) saturate(1.35);
    clip-path:polygon(0 0,calc(100% - 16px) 0,100% 16px,100% 100%,16px 100%,0 calc(100% - 16px));
    padding:16px 18px 18px;box-shadow:0 24px 60px -28px rgba(0,0,0,.9),inset 0 1px 0 rgba(255,255,255,.07)}
  @keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
  .panel{animation:rise .8s cubic-bezier(.2,.9,.2,1) both}
  .p1{animation-delay:.05s}.p2{animation-delay:.16s}.p3{animation-delay:.28s}.p4{animation-delay:.4s}

  .kicker{font:700 10px/1 'Manrope';letter-spacing:.26em;text-transform:uppercase;color:var(--cyan);opacity:.85}
  h1{font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(30px,3.6vw,50px);line-height:.84;
    letter-spacing:-.03em;margin:10px 0 6px}
  h1 em{display:block;font-style:italic;font-weight:600;font-size:.42em;letter-spacing:.01em;color:var(--sand)}
  .lede{font-size:12.5px;line-height:1.5;color:var(--mute);max-width:34ch}
  .lede b{color:var(--foam);font-weight:700}

  ul.keys{list-style:none;margin-top:14px;display:grid;gap:7px}
  ul.keys li{display:flex;align-items:center;gap:9px;font-size:11.5px;color:var(--mute)}
  ul.keys kbd{font:700 10px/1 'Syne';background:rgba(95,227,255,.1);border:1px solid var(--line);
    color:var(--cyan);padding:5px 7px;min-width:26px;text-align:center;
    clip-path:polygon(0 0,calc(100% - 5px) 0,100% 5px,100% 100%,5px 100%,0 calc(100% - 5px))}

  /* статистика */
  .stats{pointer-events:auto;display:grid;gap:10px;align-content:start}
  .stat{background:var(--panel);border:1px solid var(--line);padding:11px 14px;
    clip-path:polygon(0 0,calc(100% - 12px) 0,100% 12px,100% 100%,0 100%);
    animation:rise .8s cubic-bezier(.2,.9,.2,1) both}
  .stat span{display:block;font:700 9px/1 'Manrope';letter-spacing:.2em;text-transform:uppercase;color:var(--mute);opacity:.8}
  .stat b{font-family:'Syne',sans-serif;font-weight:800;font-size:30px;line-height:1;font-variant-numeric:tabular-nums;
    display:block;margin-top:4px;letter-spacing:-.02em}
  .stat b i{font-style:normal;font-size:13px;color:var(--mute);font-weight:700}
  .stat.hot b{color:var(--coral)} .stat.cool b{color:var(--cyan)}

  /* нижняя панель управления */
  .dock{grid-column:1/3;justify-self:start;align-self:end}
  .btns{display:flex;flex-wrap:wrap;gap:9px;margin-top:12px}
  .btn{font-family:'Syne',sans-serif;font-weight:700;font-size:12px;letter-spacing:.02em;color:var(--foam);
    background:rgba(255,255,255,.05);border:1px solid var(--line);padding:10px 13px;cursor:pointer;
    clip-path:polygon(0 0,calc(100% - 9px) 0,100% 9px,100% 100%,9px 100%,0 calc(100% - 9px));
    transition:transform .18s cubic-bezier(.2,.9,.2,1),background .18s,box-shadow .18s,color .18s;
    display:flex;align-items:center;gap:7px}
  .btn:hover{transform:translateY(-3px);background:rgba(95,227,255,.14);border-color:rgba(95,227,255,.5);
    box-shadow:0 12px 26px -14px rgba(95,227,255,.85);color:#fff}
  .btn:active{transform:translateY(0) scale(.97)}
  .btn.off{opacity:.5}
  .btn u{text-decoration:none;font:700 9px/1 'Manrope';letter-spacing:.12em;color:var(--cyan);opacity:.75}

  .slider{display:flex;align-items:center;gap:10px;margin-top:14px;font-size:10.5px;
    letter-spacing:.18em;text-transform:uppercase;color:var(--mute)}
  input[type=range]{-webkit-appearance:none;appearance:none;width:120px;height:3px;border-radius:3px;
    background:linear-gradient(90deg,var(--cyan),var(--coral));outline:none;cursor:pointer}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;
    background:var(--foam);border:2px solid var(--deep);box-shadow:0 0 12px rgba(95,227,255,.9);transition:transform .15s}
  input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.25)}
  input[type=range]::-moz-range-thumb{width:13px;height:13px;border:2px solid var(--deep);border-radius:50%;background:var(--foam)}

  /* правый нижний блок */
  .readouts{grid-column:3;align-self:end;justify-self:stretch}
  .ro{margin-bottom:11px}
  .ro:last-child{margin-bottom:0}
  .ro .lab{display:flex;justify-content:space-between;font:700 9px/1 'Manrope';letter-spacing:.18em;
    text-transform:uppercase;color:var(--mute)}
  .ro .lab b{color:var(--foam);font-variant-numeric:tabular-nums}
  .bar{height:3px;margin-top:6px;background:rgba(255,255,255,.09);overflow:hidden}
  .bar i{display:block;height:100%;background:linear-gradient(90deg,var(--cyan),rgba(95,227,255,0));
    transition:width .6s cubic-bezier(.2,.9,.2,1)}

  /* подсказка-комментарий */
  .hint{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:4;pointer-events:none;
    font:700 10px/1 'Manrope';letter-spacing:.24em;text-transform:uppercase;color:var(--mute);
    background:rgba(2,16,26,.6);border:1px solid var(--line);padding:9px 14px;backdrop-filter:blur(8px);
    clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 8px));
    transition:opacity .6s,transform .6s}
  .hint b{color:var(--coral)}
  .hint.gone{opacity:0;transform:translate(-50%,14px)}

  /* карточка рыбки при наведении */
  .tip{position:fixed;left:0;top:0;z-index:5;pointer-events:none;opacity:0;transition:opacity .18s;
    background:rgba(3,20,30,.86);border:1px solid rgba(255,122,61,.45);padding:8px 11px;backdrop-filter:blur(6px);
    clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 8px));white-space:nowrap}
  .tip.on{opacity:1}
  .tip strong{display:block;font-family:'Syne',sans-serif;font-weight:800;font-size:14px;letter-spacing:-.01em}
  .tip small{display:block;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin-top:3px}

  @media (max-width:880px){
    .hud{grid-template-columns:1fr;grid-template-rows:auto auto auto;padding:12px;gap:10px}
    .readouts{grid-column:1}
    h1{font-size:30px}
    ul.keys{display:none}
  }
</style>
</head>
<body>
<canvas id="aqua"></canvas>
<div class="vignette"></div>

<div class="hud">

  <section class="panel p1">
    <div class="kicker">Живая среда · сектор 07</div>
    <h1>АКВАРИУМ<br><em>тридцать шесть литров света</em></h1>
    <p class="lede">Кликните по воде — корм утонет, стая его найдёт. Наведите курсор на рыбку, чтобы прочитать её карточку. Толкните — <b>шарахнётся</b>.</p>
    <ul class="keys">
      <li><kbd>ЛКМ</kbd> вращение камеры</li>
      <li><kbd>ПКМ</kbd> панорама</li>
      <li><kbd>колесо</kbd> приближение</li>
      <li><kbd>F</kbd> корм <kbd>B</kbd> пузыри <kbd>R</kbd> рыбка <kbd>L</kbd> свет</li>
    </ul>
  </section>

  <div></div>

  <aside class="stats">
    <div class="stat p2 hot"><span>Рыбок в воде</span><b id="sFish">0</b></div>
    <div class="stat p2 cool"><span>Кадры в секунду</span><b id="sFps">60<i> fps</i></b></div>
    <div class="stat p2"><span>Съедено</span><b id="sFed">0</b></div>
    <div class="stat p2"><span>Пузырьков</span><b id="sBub">0</b></div>
  </aside>

  <section class="panel dock p3">
    <div class="kicker">Пульт станции</div>
    <div class="btns">
      <button class="btn" data-act="fish">＋ Рыбка <u>R</u></button>
      <button class="btn" data-act="feed">Корм ×5 <u>F</u></button>
      <button class="btn" data-act="bubbles">＋ Пузыри <u>B</u></button>
      <button class="btn" data-act="light" id="btnLight">Свет <u>L</u></button>
      <button class="btn off" data-act="auto">Облёт <u>A</u></button>
      <button class="btn" data-act="clear">Убрать корм <u>C</u></button>
    </div>
    <label class="slider">Темп течения
      <input type="range" id="spd" min="0.15" max="2.2" step="0.05" value="1">
    </label>
  </section>

  <aside class="panel readouts p4">
    <div class="ro"><div class="lab"><span>Кислород</span><b id="rOxy">—</b></div><div class="bar"><i id="bOxy" style="width:70%"></i></div></div>
    <div class="ro"><div class="lab"><span>Солёность</span><b id="rSal">—</b></div><div class="bar"><i id="bSal" style="width:55%"></i></div></div>
    <div class="ro"><div class="lab"><span>Турбулентность</span><b id="rTur">—</b></div><div class="bar"><i id="bTur" style="width:40%"></i></div></div>
  </aside>

</div>

<div class="hint" id="hint">Кликните по воде, чтобы <b>бросить корм</b></div>
<div class="tip" id="tip"><strong id="tipName">—</strong><small id="tipMeta">—</small></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
/* ══════════════════════════════════ 0 · утилиты ══════════════════════════════════ */
const rand=(a,b)=>a+Math.random()*(b-a);
const pick=a=>a[Math.floor(Math.random()*a.length)];
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const $=id=>document.getElementById(id);

const TANK={w:36,h:24,d:20};
const B={x:TANK.w/2-2.4, y:TANK.h/2-2.8, z:TANK.d/2-2.4};
const FLOOR=-TANK.h/2+1.25;
const WATER=TANK.h/2-2.6;

/* ══════════════════════════════════ 1 · рендерер ══════════════════════════════════ */
const canvas=$('aqua');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.08;

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0x052233,0.0165);
scene.background=(()=>{
  const c=document.createElement('canvas');c.width=4;c.height=256;const g=c.getContext('2d');
  const gr=g.createLinearGradient(0,0,0,256);
  gr.addColorStop(0,'#0c4a63');gr.addColorStop(.35,'#0a3550');gr.addColorStop(.72,'#062234');gr.addColorStop(1,'#010a12');
  g.fillStyle=gr;g.fillRect(0,0,4,256);
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;return t;
})();

const camera=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,.1,400);
camera.position.set(26,11,33);

const controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.06;
controls.minDistance=10;controls.maxDistance=60;
controls.maxPolarAngle=Math.PI/1.8;
controls.autoRotateSpeed=.55;controls.autoRotate=false;
controls.target.set(0,-.5,0);
canvas.addEventListener('contextmenu',e=>e.preventDefault());

/* ══════════════════════════════════ 2 · свет ══════════════════════════════════ */
const ambient=new THREE.AmbientLight(0x404040,0.4); scene.add(ambient);
const hemi=new THREE.HemisphereLight(0x8fdfff,0x03141d,.45); scene.add(hemi);

const sun=new THREE.DirectionalLight(0xdff4ff,1.55);
sun.position.set(14,26,16); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048); sun.shadow.bias=-0.0008; sun.shadow.radius=3;
const sc=sun.shadow.camera; sc.left=-26;sc.right=26;sc.top=20;sc.bottom=-20;sc.near=1;sc.far=90;
scene.add(sun);

const aq1=new THREE.PointLight(0x2f7bff,1.15,70,2); aq1.position.set(-14,7,6);  scene.add(aq1);
const aq2=new THREE.PointLight(0x00d8ff,0.95,62,2); aq2.position.set(13,-6,-5); scene.add(aq2);
const glow=new THREE.PointLight(0xff9a52,.55,34,2); glow.position.set(0,WATER-1,0); scene.add(glow);

const state={speed:1,lightOn:true,lightTarget:1.55,fed:0};

/* ══════════════════════════════════ 3 · среда ══════════════════════════════════ */
/* — подиум и пол за стеклом — */
const ground=new THREE.Mesh(new THREE.PlaneGeometry(240,240),
  new THREE.MeshStandardMaterial({color:0x061b26,roughness:.95,metalness:0}));
ground.rotation.x=-Math.PI/2; ground.position.y=-TANK.h/2-2.2; ground.receiveShadow=true; scene.add(ground);

const plinth=new THREE.Mesh(new THREE.BoxGeometry(TANK.w+3,2.4,TANK.d+3),
  new THREE.MeshStandardMaterial({color:0x0b2129,roughness:.6,metalness:.45}));
plinth.position.y=-TANK.h/2-1.2; plinth.castShadow=plinth.receiveShadow=true; scene.add(plinth);

/* — стекло — */
const glass=new THREE.Mesh(new THREE.BoxGeometry(TANK.w,TANK.h,TANK.d),
  new THREE.MeshPhysicalMaterial({color:0xbfeeff,roughness:.06,metalness:0,transmission:.95,
    thickness:5,ior:1.33,clearcoat:1,clearcoatRoughness:.05,transparent:false,side:THREE.FrontSide}));
scene.add(glass);

/* — силовая рама из 12 балок — */
const frameMat=new THREE.MeshStandardMaterial({color:0x123343,roughness:.34,metalness:.85});
const fw=.55;
(function frame(){
  const w=TANK.w,h=TANK.h,d=TANK.d,t=fw;
  const add=(sx,sy,sz,x,y,z,rot)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),frameMat);
    m.position.set(x,y,z);if(rot)m.rotation.y=Math.PI/2;m.castShadow=true;scene.add(m);};
  for(const sz of [-d/2,d/2]) add(w+t,t,t,0,h/2,sz), add(w+t,t,t,0,-h/2,sz);
  for(const sx of [-w/2,w/2]) add(t,h,t,sx,0,d/2), add(t,h,t,sx,0,-d/2), add(t,t,d,0,h/2,sx*0+0),0;
  add(t,t,d,-w/2,h/2,0); add(t,t,d,w/2,h/2,0); // вертикальные углы усилены сверху
})();

/* — песчаное дно с процедурным рельефом — */
function sandTexture(){
  const c=document.createElement('canvas');c.width=c.height=512;const g=c.getContext('2d');
  g.fillStyle='#c8a173';g.fillRect(0,0,512,512);
  for(let i=0;i<80;i++){const x=Math.random()*512,y=Math.random()*512,r=rand(16,64);
    const rg=g.createRadialGradient(x,y,0,x,y,r);
    rg.addColorStop(0,'rgba(255,242,214,.26)');rg.addColorStop(1,'rgba(255,242,214,0)');
    g.fillStyle=rg;g.beginPath();g.arc(x,y,r,0,7);g.fill();}
  for(let i=0;i<11000;i++){g.fillStyle=Math.random()<.5?'rgba(62,40,22,.2)':'rgba(255,238,206,.18)';
    g.fillRect(Math.random()*512,Math.random()*512,1.5,1.5);}
  const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(3,2);
  t.encoding=THREE.sRGBEncoding;return t;
}
const sandTex=sandTexture();
const sandGeo=new THREE.PlaneGeometry(TANK.w,TANK.d,64,36);
sandGeo.rotateX(-Math.PI/2);
{ const p=sandGeo.attributes.position;
  for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i);
    p.setY(i,-1.4+Math.sin(x*.42)*.42+Math.cos(z*.55)*.34+Math.sin((x+z)*.9)*.16);}
  sandGeo.computeVertexNormals(); }
const sand=new THREE.Mesh(sandGeo,new THREE.MeshStandardMaterial({map:sandTex,roughness:.96,metalness:0}));
sand.position.y=FLOOR; sand.receiveShadow=true; scene.add(sand);

/* — камни: деформированные додекаэдры — */
const rockMat=new THREE.MeshStandardMaterial({color:0x59697a,roughness:.9,metalness:.08,flatShading:true});
for(let i=0;i<8;i++){
  const g=new THREE.DodecahedronGeometry(rand(.9,2.3),0);
  const p=g.attributes.position, v=new THREE.Vector3();
  for(let k=0;k<p.count;k++){v.fromBufferAttribute(p,k).multiplyScalar(rand(.78,1.24));p.setXYZ(k,v.x,v.y,v.z);}
  g.computeVertexNormals();
  const m=new THREE.Mesh(g,rockMat);
  m.position.set(rand(-15,15),FLOOR+rand(-.5,.3),rand(-7.5,7.5));
  m.rotation.set(rand(0,6),rand(0,6),rand(0,6));
  m.castShadow=m.receiveShadow=true; scene.add(m);
}

/* — водоросли: TubeGeometry по CatmullRomCurve3 — */
const plants=[];
const leafColors=[0x2ea36a,0x1f8f7a,0x5fbf52,0x2f7f6a,0x86c74a,0x1c6f86];
for(let i=0;i<12;i++){
  const bush=new THREE.Group();
  const x=(Math.abs(rand(0,1))<1)?rand(-15.5,15.5):0;
  bush.position.set(x,FLOOR-0.2,rand(-8,8));
  const blades=3+Math.floor(Math.random()*3);
  for(let b=0;b<blades;b++){
    const h=rand(3.2,8.4), bend=rand(-1.3,1.3), pts=[];
    for(let s=0;s<5;s++){const t=s/4;
      pts.push(new THREE.Vector3(Math.sin(t*2.4)*bend, t*h, Math.cos(t*2.1)*bend*.55));}
    const geo=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),10,rand(.09,.19),5,false);
    const m=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({
      color:pick(leafColors),roughness:.72,metalness:.05,
      transparent:true,opacity:.92,side:THREE.DoubleSide}));
    m.position.set(rand(-.9,.9),0,rand(-.9,.9)); m.castShadow=true; bush.add(m);
  }
  bush.userData={phase:rand(0,6.3),amp:rand(.08,.19),rate:rand(.5,1.1)};
  scene.add(bush); plants.push(bush);
}

/* — планктон (фоновая взвесь) — */
const moteGeo=new THREE.BufferGeometry();
{ const n=520,arr=new Float32Array(n*3);
  for(let i=0;i<n;i++){arr[i*3]=rand(-17,17);arr[i*3+1]=rand(-11,11);arr[i*3+2]=rand(-9,9);}
  moteGeo.setAttribute('position',new THREE.BufferAttribute(arr,3)); }
const motes=new THREE.Points(moteGeo,new THREE.PointsMaterial({color:0xa8ecff,size:.13,
  sizeAttenuation:true,transparent:true,opacity:.5,blending:THREE.AdditiveBlending,depthWrite:false}));
scene.add(motes);

/* — поверхность воды — */
const surface=new THREE.Mesh(new THREE.PlaneGeometry(TANK.w,TANK.d,1,1),
  new THREE.ShaderMaterial({
    uniforms:{uTime:{value:0},uShallow:{value:new THREE.Color(0x9ff0ff)},uDeep:{value:new THREE.Color(0x0a4a68)}},
    transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,
    vertexShader:`varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`uniform float uTime;uniform vec3 uShallow,uDeep;varying vec2 vUv;
      void main(){vec2 p=vUv*14.0;
        float w=sin(p.x+uTime*1.1)*cos(p.y*1.3-uTime*.8)+.5*sin((p.x+p.y)*1.7+uTime*1.7);
        w=w*.5+.5;
        float e=smoothstep(0.,.05,vUv.x)*smoothstep(1.,.95,vUv.x)*smoothstep(0.,.05,vUv.y)*smoothstep(1.,.95,vUv.y);
        gl_FragColor=vec4(mix(uDeep,uShallow,w),(0.10+w*0.34)*e);}`
  }));
surface.rotation.x=-Math.PI/2; surface.position.y=WATER; scene.add(surface);

/* ══════════════════════════════════ 4 · рыбка ══════════════════════════════════ */
const PALETTES=[
 {name:'Оранжевый клоун', body:0xff7a2e, fin:0xffd9b0, pat:0xfff4e8, mode:'stripes'},
 {name:'Синий хирург',    body:0x1f6feb, fin:0x9fd7ff, pat:0xffd23f, mode:'plain'},
 {name:'Жёлто-красный',   body:0xffc53d, fin:0xff7a2e, pat:0xe2382f, mode:'band'},
 {name:'Аметист',         body:0x9b5cff, fin:0xe6d4ff, pat:0x28e0c8, mode:'spots'},
 {name:'Рубин',           body:0xe23b3b, fin:0xffc1c1, pat:0xffd9a0, mode:'plain'},
 {name:'Малахит',         body:0x2fbf6a, fin:0xd9ff5c, pat:0x0f6b45, mode:'stripes'},
 {name:'Лосось',          body:0xff77b5, fin:0xffe0ef, pat:0xfff0a8, mode:'spots'},
 {name:'Золото',          body:0xf5b23a, fin:0xfff2cf, pat:0x8a4a12, mode:'band'},
];
const NAMES=['Немо','Аврора','Гроза','Кобальт','Ирис','Люмен','Тайфун','Персик','Вольта','Сирень',
  'Янтарь','Оникс','Фея','Гром','Мира','Криль','Шторм','Астра','Жемчуг','Комета','Изумруд','Стрела'];

const eyeWhite=new THREE.MeshStandardMaterial({color:0xf7fdff,roughness:.28,metalness:.05});
const eyeDark =new THREE.MeshStandardMaterial({color:0x0a1218,roughness:.15,metalness:.2});
const pickables=[];
const fishArray=[];

function makeFish(scale){
  const pal=pick(PALETTES);
  const g=new THREE.Group();

  const bodyMat=new THREE.MeshStandardMaterial({color:pal.body,roughness:.4,metalness:.14});
  const finMat =new THREE.MeshStandardMaterial({color:pal.fin,roughness:.55,metalness:.04,
    transparent:true,opacity:.9,side:THREE.DoubleSide});
  const patMat =new THREE.MeshStandardMaterial({color:pal.pat,roughness:.5,metalness:.06});

  // тело — вытянутая сфера, нос смотрит в +Z
  const bg=new THREE.SphereGeometry(.6,20,16); bg.scale(.86,1.02,1.95); bg.computeVertexNormals();
  const body=new THREE.Mesh(bg,bodyMat); body.castShadow=true; g.add(body);

  // хвост
  const tail=new THREE.Object3D(); tail.position.z=-1.05; g.add(tail);
  const tg=new THREE.ConeGeometry(.6,1.15,4,1); tg.rotateX(-Math.PI/2); tg.scale(.17,1.12,.95);
  const tm=new THREE.Mesh(tg,finMat); tm.castShadow=true; tail.add(tm);

  // грудные плавники
  const mkFin=(sx)=>{
    const p=new THREE.Object3D(); p.position.set(sx*.44,-.05,.16); g.add(p);
    const fg=new THREE.ConeGeometry(.34,.72,4,1); fg.rotateX(-Math.PI/2); fg.scale(.12,.9,1);
    const m=new THREE.Mesh(fg,finMat); m.position.z=-.22; m.rotation.y=sx*.5; m.castShadow=true; p.add(m); return p;
  };
  const leftFin=mkFin(-1), rightFin=mkFin(1);

  // спинной и анальный
  const dg=new THREE.ConeGeometry(.42,.9,4,1); dg.rotateX(0); dg.scale(.16,1,.62);
  const dorsal=new THREE.Mesh(dg,finMat); dorsal.position.set(0,.62,-.05); dorsal.castShadow=true; g.add(dorsal);
  const ag=new THREE.ConeGeometry(.3,.6,4,1); ag.scale(.14,1,.55);
  const anal=new THREE.Mesh(ag,finMat); anal.position.set(0,-.58,-.35); anal.rotation.x=Math.PI; g.add(anal);

  // глаза
  for(const sx of [-1,1]){
    const w=new THREE.Mesh(new THREE.SphereGeometry(.165,12,10),eyeWhite);
    w.position.set(sx*.34,.13,.62); g.add(w);
    const p=new THREE.Mesh(new THREE.SphereGeometry(.085,10,8),eyeDark);
    p.position.set(sx*.4,.13,.74); g.add(p);
  }
  // рот
  const mouth=new THREE.Mesh(new THREE.TorusGeometry(.11,.045,6,12),eyeDark);
  mouth.position.set(0,-.1,1.1); g.add(mouth);

  // узор
  if(pal.mode==='stripes'||pal.mode==='band'){
    [.5,-.05,-.62].forEach((z,i)=>{
      const t=new THREE.Mesh(new THREE.TorusGeometry(.44-i*.05,.075,6,16),patMat);
      t.rotation.y=Math.PI/2; t.position.z=z; g.add(t);});
  } else if(pal.mode==='spots'){
    for(let i=0;i<7;i++){
      const s=new THREE.Mesh(new THREE.SphereGeometry(.1,8,6),patMat);
      s.position.set(rand(-.4,.4),rand(-.35,.35),rand(-.7,.8)); s.scale.z=.5; g.add(s);}
  }

  g.userData.pal=pal;
  return {group:g,body,tail,leftFin,rightFin,dorsal,palette:pal};
}

function spawnFish(){
  if(fishArray.length>=42) return;
  const sc=rand(.6,1.2);
  const m=makeFish(sc);
  m.group.scale.setScalar(sc);
  m.group.position.set(rand(-B.x*.7,B.x*.7),rand(-B.y*.5,B.y*.5),rand(-B.z*.6,B.z*.6));
  const f={
    mesh:m.group, body:m.body, tail:m.tail, leftFin:m.leftFin, rightFin:m.rightFin, dorsal:m.dorsal,
    velocity:new THREE.Vector3(rand(-1,1),rand(-.3,.3),rand(-1,1)),
    speed:rand(1.9,4.4), tailSpeed:rand(4.5,9.5), phase:rand(0,6.28),
    targetFood:null, avoidanceRadius:rand(2.6,4.6),
    scale:sc, baseScale:sc, name:pick(NAMES)+', '+'#'+Math.floor(rand(10,99)),
    wander:new THREE.Vector3(rand(-1,1),rand(-.4,.4),rand(-1,1)).normalize(),
    wanderTimer:rand(0,3), startle:0
  };
  m.group.userData.fish=f;
  m.body.userData.fish=f;
  scene.add(m.group); pickables.push(m.body); fishArray.push(f);
  updateStats();
}

/* ══════════════════════════════════ 5 · пузыри ══════════════════════════════════ */
const bubbleGeo=new THREE.SphereGeometry(1,12,10);
const bubbleMat=new THREE.MeshPhysicalMaterial({color:0xdff8ff,roughness:.05,metalness:0,
  transmission:.92,thickness:.6,ior:1.05,transparent:true,opacity:.9});
const bubbles=[];
function spawnBubble(){
  const m=new THREE.Mesh(bubbleGeo,bubbleMat);
  const r=rand(.14,.4); m.scale.setScalar(r);
  m.position.set(rand(-16,16),rand(-11,WATER),rand(-8.4,8.4));
  m.userData={v:rand(1.3,3.1),ph:rand(0,6.3),amp:rand(.15,.7),r};
  scene.add(m); bubbles.push(m);
}
for(let i=0;i<30;i++) spawnBubble();

/* ══════════════════════════════════ 6 · корм ══════════════════════════════════ */
const foodGeo=new THREE.IcosahedronGeometry(.19,0);
const foodMat=new THREE.MeshStandardMaterial({color:0xc0762f,roughness:.85,metalness:0,
  emissive:0x2a1205,emissiveIntensity:.5});
const foods=[];
function dropFood(x,z,y){
  if(foods.length>46) return;
  const m=new THREE.Mesh(foodGeo,foodMat);
  m.position.set(clamp(x,-B.x,B.x),clamp(y,FLOOR+.6,WATER-.4),clamp(z,-B.z,B.z));
  m.castShadow=true;
  m.userData={vel:new THREE.Vector3(rand(-.5,.5),rand(-.3,.2),rand(-.5,.5)),spin:rand(-3,3),dying:0};
  scene.add(m); foods.push(m);
}
const effects=[];
const ringGeo=new THREE.RingGeometry(.5,1,20);
function popRing(pos,color){
  const m=new THREE.Mesh(ringGeo,new THREE.MeshBasicMaterial({color,transparent:true,opacity:.95,
    side:THREE.DoubleSide,blending:THREE.AdditiveBlending,depthWrite:false}));
  m.position.copy(pos); m.quaternion.copy(camera.quaternion); m.userData={t:0};
  scene.add(m); effects.push(m);
}

/* ══════════════════════════════════ 7 · поведение ══════════════════════════════════ */
const _v=new THREE.Vector3(), _d=new THREE.Vector3();
function updateFish(f,dt,t){
  const p=f.mesh.position;
  const a=_v.set(0,0,0);

  f.wanderTimer-=dt;
  if(f.wanderTimer<=0){f.wanderTimer=rand(1.8,5.2);
    f.wander.set(rand(-1,1),rand(-.5,.5),rand(-1,1)).normalize();}
  a.addScaledVector(f.wander,2.4);

  // избегание соседей
  for(let j=0;j<fishArray.length;j++){
    const o=fishArray[j]; if(o===f) continue;
    _d.copy(p).sub(o.mesh.position);
    const d=_d.length();
    if(d<f.avoidanceRadius&&d>1e-4){ a.addScaledVector(_d.divideScalar(d),(1-d/f.avoidanceRadius)*14); }
  }
  // стены
  const m=3.0;
  if(p.x> B.x-m)a.x-=(p.x-(B.x-m))*4.5; if(p.x< -B.x+m)a.x+=( (m-B.x)-p.x)*-4.5*-1;
  if(p.x< -B.x+m)a.x+=( -B.x+m-p.x)*4.5;
  if(p.y> B.y-m)a.y-=(p.y-(B.y-m))*4.5;
  if(p.y< FLOOR+1.6)a.y+=(FLOOR+1.6-p.y)*5.5;
  if(p.z> B.z-m)a.z-=(p.z-(B.z-m))*4.5;
  if(p.z< -B.z+m)a.z+=( -B.z+m-p.z)*4.5;

  // корм
  let best=null,bd=15,bp=null;
  for(const fd of foods){
    if(fd.userData.dying>0) continue;
    const d=p.distanceTo(fd.position);
    if(d<bd){bd=d;best=fd;bp=fd.position;}
  }
  if(best){
    f.targetFood=best;
    _d.copy(bp).sub(p).normalize();
    a.addScaledVector(_d,10*(1-bd/15)+4);
    if(bd<1.25*f.scale){ // съедено
      f.scale=Math.min(2.3,f.scale*1.05); f.mesh.scale.setScalar(f.scale);
      f.startle=1.1; state.fed++; $('sFed').textContent=state.fed;
      popRing(best.position,0xffb35c);
      scene.remove(best); foods.splice(foods.indexOf(best),1);
      updateStats();
    }
  } else f.targetFood=null;

  // интегрирование
  f.startle=Math.max(0,f.startle-dt*1.4);
  f.velocity.addScaledVector(a,dt);
  const maxS=f.speed*(1+f.startle*1.7);
  if(f.velocity.length()>maxS) f.velocity.setLength(maxS);
  f.velocity.y=clamp(f.velocity.y,-maxS*.7,maxS*.7);
  p.addScaledVector(f.velocity,dt*state.speed);
  p.x=clamp(p.x,-B.x,B.x); p.y=clamp(p.y,FLOOR+.5,WATER-.5); p.z=clamp(p.z,-B.z,B.z);

  if(f.velocity.lengthSq()>1e-5){ _d.copy(p).add(f.velocity); f.mesh.lookAt(_d); }

  const sp=f.velocity.length();
  const wag=(.32+sp*.11)*(1+f.startle);
  const w=t*(f.tailSpeed*(1+f.startle*.8))+f.phase;
  f.tail.rotation.y=Math.sin(w)*wag;
  f.leftFin.rotation.y =Math.sin(w*.9+f.phase)*.55;
  f.rightFin.rotation.y=-Math.sin(w*.9+f.phase)*.55;
  f.dorsal.rotation.z=Math.sin(w*.65)*.22;
  f.body.rotation.z=Math.sin(w*.5)*.05;
}

/* ══════════════════════════════════ 8 · ввод ══════════════════════════════════ */
const ray=new THREE.Raycaster(); const ndc=new THREE.Vector2();
const plane=new THREE.Plane(); const hit=new THREE.Vector3(); const camDir=new THREE.Vector3();
let down=null, hovered=null;

function pickAt(cx,cy){
  ndc.x=(cx/innerWidth)*2-1; ndc.y=-(cy/innerHeight)*2+1;
  ray.setFromCamera(ndc,camera);
  const list=ray.intersectObjects(pickables,false);
  return list.length?list[0].object.userData.fish:null;
}
canvas.addEventListener('pointerdown',e=>{down={x:e.clientX,y:e.clientY,t:performance.now()};});
canvas.addEventListener('pointermove',e=>{
  if(down) return;
  ndc.x=(e.clientX/innerWidth)*2-1; ndc.y=-(e.clientY/innerHeight)*2+1;
  ray.setFromCamera(ndc,camera);
  const list=ray.intersectObjects(pickables,false);
  const f=list.length?list[0].object.userData.fish:null;
  hovered=f;
  const tip=$('tip');
  if(f){ $('tipName').textContent=f.mesh.userData.pal.name;
    $('tipMeta').textContent=f.name+'  ·  размер '+f.scale.toFixed(2)+'  ·  скорость '+f.speed.toFixed(1);
    tip.classList.add('on'); }
  else tip.classList.remove('on');
});
canvas.addEventListener('pointerup',e=>{
  if(!down) return;
  const moved=Math.hypot(e.clientX-down.x,e.clientY-down.y);
  const quick=performance.now()-down.t<420; down=null;
  if(moved>8||!quick) return;
  ndc.x=(e.clientX/innerWidth)*2-1; ndc.y=-(e.clientY/innerHeight)*2+1;
  ray.setFromCamera(ndc,camera);
  const list=ray.intersectObjects(pickables,false);
  if(list.length){ // толкнули рыбку
    const f=list[0].object.userData.fish;
    f.startle=1.6;
    camera.getWorldDirection(camDir);
    f.velocity.copy(camDir).multiplyScalar(-f.speed*2.4);
    popRing(f.mesh.position,0x5fe3ff);
    return;
  }
  camera.getWorldDirection(camDir);
  plane.setFromNormalAndCoplanarPoint(camDir.clone().negate(),controls.target);
  if(ray.ray.intersectPlane(plane,hit)){
    dropFood(hit.x,hit.z,clamp(hit.y,FLOOR+1,WATER-.6));
    popRing(new THREE.Vector3(clamp(hit.x,-B.x,B.x),WATER-.3,clamp(hit.z,-B.z,B.z)),0x9ff0ff);
    $('hint').classList.add('gone');
  }
});

document.querySelectorAll('.btn').forEach(b=>b.addEventListener('click',()=>act(b.dataset.act,b)));
function act(a,btn){
  if(a==='fish'){spawnFish(); popRing(new THREE.Vector3(rand(-10,10),rand(-4,4),rand(-5,5)),0xff7a3d);}
  if(a==='feed'){for(let i=0;i<5;i++) dropFood(rand(-13,13),rand(-7,7),WATER-.6);}
  if(a==='bubbles'){for(let i=0;i<10;i++) spawnBubble(); updateStats();}
  if(a==='light'){state.lightOn=!state.lightOn; state.lightTarget=state.lightOn?1.55:.14;
    (btn||$('btnLight')).classList.toggle('off',!state.lightOn);}
  if(a==='auto'){controls.autoRotate=!controls.autoRotate;
    document.querySelector('[data-act=auto]').classList.toggle('off',!controls.autoRotate);}
  if(a==='clear'){while(foods.length){const m=foods.pop();scene.remove(m);} updateStats();}
}
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k==='f')act('feed'); if(k==='b')act('bubbles'); if(k==='r')act('fish');
  if(k==='l')act('light',$('btnLight')); if(k==='a')act('auto'); if(k==='c')act('clear');
});
$('spd').addEventListener('input',e=>state.speed=parseFloat(e.target.value));

/* ══════════════════════════════════ 9 · интерфейс ══════════════════════════════════ */
function updateStats(){
  $('sFish').textContent=fishArray.length;
  $('sBub').textContent=bubbles.length;
  $('sFed').textContent=state.fed;
}
let roT=0;
function readouts(t){
  const o=(68+Math.sin(t*.6)*9+fishArray.length*.15).toFixed(1);
  const s=(33.4+Math.sin(t*.31+1.4)*1.6).toFixed(1);
  const u=(42+Math.sin(t*1.1)*18).toFixed(0);
  $('rOxy').textContent=o+'%'; $('bOxy').style.width=o+'%';
  $('rSal').textContent=s+' ‰'; $('bSal').style.width=clamp(s*1.6,5,100)+'%';
  $('rTur').textContent=u+'%'; $('bTur').style.width=u+'%';
}

/* ══════════════════════════════════ 10 · цикл ══════════════════════════════════ */
for(let i=0;i<15;i++) spawnFish();
updateStats();

let last=performance.now(), fpsAcc=0, fpsN=0, fpsT=0;
const tipEl=$('tip'), tipPos=new THREE.Vector3();
function tick(now){
  requestAnimationFrame(tick);
  const dt=Math.min(.05,(now-last)/1000); last=now; const t=now/1000;

  fpsAcc+=1/Math.max(dt,1e-4); fpsN++;
  if(now-fpsT>450){$('sFps').innerHTML=Math.round(fpsAcc/fpsN)+'<i> fps</i>';fpsAcc=0;fpsN=0;fpsT=now;}

  sun.intensity+= (state.lightTarget-sun.intensity)*Math.min(1,dt*3);
  aq1.intensity=THREE.MathUtils.lerp(aq1.intensity,state.lightOn?1.15:2.5,dt*2);
  aq2.intensity=THREE.MathUtils.lerp(aq2.intensity,state.lightOn?.95:2.1,dt*2);
  glow.intensity=THREE.MathUtils.lerp(glow.intensity,state.lightOn?.55:1.4,dt*2);
  sandTex.offset.x+=dt*.005; sandTex.offset.y+=dt*.003;
  surface.material.uniforms.uTime.value=t;

  for(const f of fishArray) updateFish(f,dt,t);
  if(hovered){
    const k=fishArray.includes(hovered)?hovered:null;
    const target=k?k.baseScale*1.18:0;
    if(k){ k.mesh.scale.setScalar(THREE.MathUtils.lerp(k.mesh.scale.x,k.baseScale*1.18,dt*6)); }
    if(k){ tipPos.copy(k.mesh.position).project(camera);
      tipEl.style.transform=`translate(-50%,-135%) translate(${(tipPos.x*.5+.5)*innerWidth}px,${(-tipPos.y*.5+.5)*innerHeight}px)`; }
    for(const f of fishArray) if(f!==hovered) f.mesh.scale.setScalar(THREE.MathUtils.lerp(f.mesh.scale.x,f.baseScale,dt*6));
    if(!k&&hovered){hovered=null;tipEl.classList.remove('on');}
  }

  // корм: гравитация + снос
  for(let i=foods.length-1;i>=0;i--){
    const m=foods[i], u=m.userData;
    if(u.dying>0){ u.dying+=dt; m.scale.multiplyScalar(1-dt*2.4); m.material.opacity=1;
      m.visible=u.dying<1.1;
      if(u.dying>1.1){scene.remove(m);foods.splice(i,1);updateStats();}
      continue; }
    u.vel.y-=6.5*dt; u.vel.y=Math.max(u.vel.y,-2.6);
    u.vel.x+=Math.sin(t*1.6+u.spin)*.4*dt; u.vel.z+=Math.cos(t*1.3+u.spin)*.4*dt;
    m.position.addScaledVector(u.vel,dt*state.speed);
    m.rotation.x+=u.spin*dt; m.rotation.y+=u.spin*dt*.7;
    if(m.position.y<=FLOOR+.28){u.dying=.001;popRing(m.position,0x8fdfff);}
  }

  // пузыри
  for(const b of bubbles){
    const u=b.userData;
    b.position.y+=u.v*dt;
    b.position.x+=Math.sin(t*1.4+u.ph)*u.amp*dt*2.2;
    b.position.z+=Math.cos(t*1.1+u.ph)*u.amp*dt*2.2;
    b.scale.setScalar(u.r*(1+Math.sin(t*3+u.ph)*.06));
    if(b.position.y>WATER-.4){
      b.position.set(rand(-16,16),-TANK.h/2+rand(0,1.5),rand(-8.4,8.4));
      b.userData.r=rand(.14,.4); b.scale.setScalar(b.userData.r);
    }
  }

  // вспышки
  for(let i=effects.length-1;i>=0;i--){
    const e=effects[i]; e.userData.t+=dt;
    e.scale.setScalar(.35+e.userData.t*7);
    e.material.opacity=Math.max(0,.95-e.userData.t*2.1);
    e.quaternion.copy(camera.quaternion);
    if(e.userData.t>.5){scene.remove(e);e.material.dispose();effects.splice(i,1);}
  }

  motes.rotation.y+=dt*.03;
  motes.position.y=Math.sin(t*.35)*.5;
  for(const p of plants){const u=p.userData;
    p.rotation.x=Math.sin(t*u.rate+u.phase)*u.amp;
    p.rotation.z=Math.cos(t*u.rate*.86+u.phase)*u.amp;}

  controls.update();
  renderer.render(scene,camera);
}
requestAnimationFrame(tick);

setInterval(()=>readouts(performance.now()/1000),450); readouts(0);
setTimeout(()=>$('hint').classList.add('gone'),11000);

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
</script>
</body>
</html>
```

**Что внутри, помимо ТЗ:**

- **Анатомия рыбки** — тело-сфера, хвост-конус на отдельном пивоте, две грудные плавниковые оси, спинной и анальный плавники, склера + зрачок, губы-торус и узор (полосы/пятна) из 8 цветовых схем.
- **Поведение** — странствие по таймеру, сепарация по соседям, мягкая отталкивающая стена у стекла, преследование корма в радиусе 15, рост на 5 % после еды, рыскание при развороте.
- **Взаимодействие** — наведение на рыбку показывает карточку с её именем и параметрами, клик по ней заставляет её шарахнуться с кольцевой вспышкой; клик по воде роняет гранулу корма.
- **Живой фон** — дрейфующая взвесь планктона, шейдерная рябь на поверхности воды, «каустика», ползущая по песку, качающиеся кустики, автоповорот камеры по клавише `A`.

Управление: `ЛКМ` — орбита, `ПКМ` — панорама, колесо — зум (10–60), `F/B/R/L/A/C` — корм, пузыри, рыбка, свет, облёт, чистка.