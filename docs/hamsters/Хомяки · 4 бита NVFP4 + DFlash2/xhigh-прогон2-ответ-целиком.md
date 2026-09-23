

Here's the complete project — save it as `index.html` and open it in any modern browser (it pulls Three.js from a CDN, so it needs internet on first load).

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Low-Poly Hamster Playground 🐹</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#33302e; --paper:#fffdf7; --coral:#ff8f6b; --sun:#ffb35c;
  }
  *{box-sizing:border-box;margin:0}
  html,body{height:100%}
  body{
    font-family:'Nunito',system-ui,sans-serif; color:var(--ink); overflow:hidden;
    background:linear-gradient(180deg,#9fd8ff 0%,#cdeedd 42%,#ffe3b8 78%,#ffd9a0 100%);
  }

  /* ---------- ambient sky layer (behind the 3D canvas) ---------- */
  .sky-decor{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
  .sun{position:absolute;top:7%;right:9%;width:200px;height:200px;border-radius:50%;
    background:radial-gradient(circle,#fff8da 0%,#ffe9a8 35%,rgba(255,224,140,0) 70%);
    animation:pulse 6s ease-in-out infinite}
  @keyframes pulse{50%{transform:scale(1.09)}}
  .cloud{position:absolute;background:rgba(255,255,255,.85);border-radius:999px;
    filter:blur(1px);animation:drift linear infinite}
  .cloud::before,.cloud::after{content:'';position:absolute;background:inherit;border-radius:50%}
  .cloud{width:130px;height:36px}
  .cloud::before{width:56px;height:56px;top:-26px;left:20px}
  .cloud::after{width:42px;height:42px;top:-18px;left:62px}
  .c1{top:13%;animation-duration:95s}
  .c2{top:26%;transform:scale(.65);opacity:.7;animation-duration:140s;animation-delay:-50s}
  .c3{top:6%;transform:scale(1.25);opacity:.55;animation-duration:120s;animation-delay:-85s}
  @keyframes drift{from{left:-22%}to{left:112%}}

  canvas{position:fixed;inset:0;z-index:1;display:block;cursor:grab}
  body.dragging canvas{cursor:grabbing}

  /* ---------- HUD ---------- */
  .hud-title{position:fixed;top:18px;left:18px;z-index:3;max-width:min(340px,80vw);
    background:var(--paper);border:3px solid var(--ink);border-radius:16px;
    padding:14px 18px 12px;box-shadow:6px 6px 0 rgba(51,48,46,.85);
    transform:rotate(-2deg);transition:transform .25s ease}
  .hud-title:hover{transform:rotate(0deg) translateY(-2px)}
  .eyebrow{font-weight:800;font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--coral)}
  h1{font-family:'Baloo 2','Nunito',sans-serif;font-weight:800;
    font-size:clamp(24px,3.6vw,38px);line-height:.98;margin:6px 0 5px}
  .hl{background:linear-gradient(transparent 58%,#ffe08a 58%)}
  .sub{font-size:12.5px;font-weight:600;opacity:.75}

  .counter{position:fixed;top:18px;right:18px;z-index:3;transform:rotate(1.5deg);
    background:var(--paper);border:3px solid var(--ink);border-radius:999px;
    padding:8px 15px;font-weight:800;font-size:13px;box-shadow:4px 4px 0 rgba(51,48,46,.85)}

  .feed{position:fixed;left:18px;bottom:18px;z-index:3;display:flex;flex-direction:column;gap:7px;align-items:flex-start}
  .chip{display:flex;align-items:center;gap:8px;max-width:270px;
    background:rgba(255,253,247,.93);border:2px solid var(--ink);border-radius:999px;
    padding:5px 13px 5px 8px;box-shadow:3px 3px 0 rgba(51,48,46,.7);font-size:12.5px}
  .chip b{font-family:'Baloo 2','Nunito',sans-serif;font-size:14.5px;font-weight:700}
  .chip .dot{width:12px;height:12px;border-radius:50%;border:2px solid var(--ink);flex:none}
  .chip .act{font-weight:700;opacity:.7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .chip.pop{animation:pop .35s cubic-bezier(.34,1.56,.64,1)}
  @keyframes pop{0%{transform:scale(.9)}60%{transform:scale(1.06)}100%{transform:scale(1)}}

  .actions{position:fixed;right:18px;bottom:18px;z-index:3;display:flex;flex-direction:column;align-items:flex-end;gap:9px}
  .btn{font-family:'Baloo 2','Nunito',sans-serif;font-weight:700;font-size:16px;color:var(--ink);
    background:var(--sun);border:3px solid var(--ink);border-radius:14px;padding:10px 18px;
    cursor:pointer;box-shadow:5px 5px 0 rgba(51,48,46,.85);transition:transform .12s,box-shadow .12s}
  .btn:hover{transform:translate(-2px,-2px);box-shadow:7px 7px 0 rgba(51,48,46,.85)}
  .btn:active{transform:translate(2px,2px);box-shadow:2px 2px 0 rgba(51,48,46,.85)}
  .hint{font-size:11px;font-weight:700;opacity:.65;text-align:right;max-width:320px;line-height:1.55}

  /* ---------- loader ---------- */
  #loader{position:fixed;inset:0;z-index:10;display:grid;place-items:center;
    background:linear-gradient(180deg,#9fd8ff 0%,#cdeedd 42%,#ffe3b8 78%,#ffd9a0 100%);
    transition:opacity .6s ease}
  #loader.done{opacity:0;pointer-events:none}
  #loader .card{text-align:center;background:var(--paper);border:3px solid var(--ink);
    border-radius:18px;padding:26px 36px;box-shadow:6px 6px 0 rgba(51,48,46,.85)}
  #loader .hop{font-size:46px;animation:hop 1s ease-in-out infinite;display:inline-block}
  @keyframes hop{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}
  #loader p{margin-top:10px;font-weight:700;font-size:14px}

  @media (max-width:640px){
    .hud-title{padding:10px 13px}
    .hint{display:none}
    .chip{font-size:11px;padding:4px 10px 4px 6px}
    .counter{font-size:11px;padding:6px 11px}
  }
</style>
</head>
<body>

  <div class="sky-decor" aria-hidden="true">
    <div class="sun"></div>
    <div class="cloud c1"></div><div class="cloud c2"></div><div class="cloud c3"></div>
  </div>

  <header class="hud-title">
    <div class="eyebrow">Pocket-sized · Big personalities</div>
    <h1>Low-Poly <span class="hl">Hamster</span> Playground</h1>
    <p class="sub">Four very busy rodents. One tiny terrarium. Zero chill.</p>
  </header>

  <div class="counter" id="counter">🐹 × 4 inside</div>
  <div class="feed" id="feed"></div>

  <div class="actions">
    <button id="snackBtn" class="btn">🌻 Toss a snack</button>
    <p class="hint">drag to orbit · scroll to zoom<br>click the bedding → toss a snack · click a hamster → boop</p>
  </div>

  <div id="loader"><div class="card"><div class="hop">🐹</div><p id="loadmsg">Warming up the cage…</p></div></div>

  <script>
    window.__pgStarted=false;
    setTimeout(function(){
      if(!window.__pgStarted){
        var m=document.getElementById('loadmsg');
        if(m) m.textContent='Still loading… this page needs internet access for the Three.js CDN.';
      }
    },7000);
  </script>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
    }
  }
  </script>

  <script type="module">
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

  /* ================= helpers ================= */
  const rand=(a,b)=>a+Math.random()*(b-a);
  const pick=a=>a[Math.floor(Math.random()*a.length)];
  const lerpAngle=(a,b,t)=>{const d=((b-a+Math.PI*3)%(Math.PI*2))-Math.PI;return a+d*t;};
  const M=(c,o={})=>new THREE.MeshStandardMaterial(Object.assign({color:c,flatShading:true,roughness:.9},o));

  /* ================= renderer / scene / camera ================= */
  let renderer;
  try{
    renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  }catch(e){
    document.getElementById('loadmsg').textContent="WebGL isn't available on this device 😿";
    throw e;
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.setSize(innerWidth,innerHeight);
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.12;
  document.body.appendChild(renderer.domElement);

  const scene=new THREE.Scene();
  scene.fog=new THREE.Fog(0xe6f2e4,16,34);

  const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.1,100);
  camera.position.set(8.6,6.4,9.6);

  const controls=new OrbitControls(camera,renderer.domElement);
  controls.target.set(0,1,0);
  controls.enableDamping=true; controls.dampingFactor=.06;
  controls.minDistance=5; controls.maxDistance=18;
  controls.maxPolarAngle=1.42; controls.minPolarAngle=.35;
  controls.autoRotate=true; controls.autoRotateSpeed=.55;
  controls.addEventListener('start',()=>{controls.autoRotate=false;document.body.classList.add('dragging');});
  controls.addEventListener('end',()=>document.body.classList.remove('dragging'));

  /* lights */
  scene.add(new THREE.HemisphereLight(0xfff3e0,0xbfe3c8,.95));
  const sunL=new THREE.DirectionalLight(0xffe6b8,1.7);
  sunL.position.set(7,11,6); sunL.castShadow=true;
  sunL.shadow.mapSize.set(2048,2048);
  Object.assign(sunL.shadow.camera,{left:-9,right:9,top:9,bottom:-9,near:2,far:30});
  sunL.shadow.bias=-0.0004;
  scene.add(sunL);
  const fill=new THREE.DirectionalLight(0xcfe8ff,.35); fill.position.set(-6,5,-6); scene.add(fill);

  /* ================= layout constants ================= */
  const FLOOR_Y=0.1;
  const WHEEL={x:-3.0,z:-1.5};
  const BOWL ={x:3.3, z:1.6};
  const TUN  ={x:1.9, z:-1.3, inX:0.7, outX:3.1};

  function isClear(x,z){
    if(Math.hypot(x-WHEEL.x,z-WHEEL.z)<1.4) return false;
    if(Math.hypot(x-BOWL.x, z-BOWL.z)  <1.05) return false;
    const t=THREE.MathUtils.clamp((x-TUN.inX)/(TUN.outX-TUN.inX),0,1);
    if(Math.hypot(x-(TUN.inX+t*(TUN.outX-TUN.inX)),z-TUN.z)<1.0) return false;
    return true;
  }

  /* ================= ground + cage ================= */
  const ground=new THREE.Mesh(new THREE.CircleGeometry(17,28),M(0x9ed6a1));
  ground.rotation.x=-Math.PI/2; ground.receiveShadow=true; scene.add(ground);

  const cage=new THREE.Group(); scene.add(cage);
  const wood=M(0xcf8f55), woodDark=M(0xb97a45);
  function box(w,h,d,m,x,y,z,parent=cage){
    const e=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);
    e.position.set(x,y,z); e.castShadow=true; e.receiveShadow=true; parent.add(e); return e;
  }
  box(10.5,.6,7.5,wood,0,-.3,0);                 // tray
  const bedding=box(10,.14,7,M(0xf3d9a4),0,FLOOR_Y-.07,0); // sand, top = FLOOR_Y

  const glassM=new THREE.MeshPhysicalMaterial({color:0xdff2ff,transparent:true,opacity:.16,
    roughness:.08,metalness:0,side:THREE.DoubleSide,depthWrite:false});
  function glass(w,h,d,x,y,z){const e=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),glassM);e.position.set(x,y,z);cage.add(e);}
  glass(10.3,2.5,.05, 0,FLOOR_Y+1.25, 3.55);
  glass(10.3,2.5,.05, 0,FLOOR_Y+1.25,-3.55);
  glass(.05,2.5,7.1, 5.05,FLOOR_Y+1.25,0);
  glass(.05,2.5,7.1,-5.05,FLOOR_Y+1.25,0);

  const fy=FLOOR_Y+2.62;
  box(10.6,.24,.24,woodDark,0,fy, 3.55);
  box(10.6,.24,.24,woodDark,0,fy,-3.55);
  box(.24,.24,7.4,woodDark, 5.05,fy,0);
  box(.24,.24,7.4,woodDark,-5.05,fy,0);
  for(const [x,z] of [[-5.05,3.55],[-5.05,-3.55],[5.05,3.55],[5.05,-3.55]])
    box(.28,FLOOR_Y+2.6,.28,woodDark,x,(FLOOR_Y+2.6)/2,z);

  // sand pebbles
  for(let i=0;i<20;i++){
    const x=rand(-4.4,4.4), z=rand(-2.9,2.9);
    if(!isClear(x,z)) continue;
    const p=new THREE.Mesh(new THREE.SphereGeometry(rand(.05,.1),6,5),M(pick([0xe3bd85,0xd8ab70,0xf7e6bd])));
    p.scale.y=.5; p.position.set(x,FLOOR_Y+.02,z); p.receiveShadow=true; scene.add(p);
  }

  /* ================= exercise wheel (drum style) ================= */
  const wheelStand=new THREE.Group(); wheelStand.position.set(WHEEL.x,FLOOR_Y,WHEEL.z); scene.add(wheelStand);
  const standM=M(0x8a6f5a), ringM=M(0xff8f6b,{roughness:.7}), spokeM=M(0xfff3e2);
  for(const sx of [-1,1]){
    const foot=new THREE.Mesh(new THREE.BoxGeometry(.34,.09,1.0),standM);
    foot.position.set(sx*.72,.045,0); foot.castShadow=true; wheelStand.add(foot);
    for(const sz of [-1,1]){
      const post=new THREE.Mesh(new THREE.CylinderGeometry(.05,.06,.52,6),standM);
      post.position.set(sx*.72,.26,sz*.4); post.castShadow=true; wheelStand.add(post);
    }
  }
  const wheelG=new THREE.Group(); wheelG.position.y=.95; wheelStand.add(wheelG);
  for(const sz of [-1,1]){
    const ring=new THREE.Mesh(new THREE.TorusGeometry(.85,.07,6,18),ringM);
    ring.position.z=sz*.45; ring.castShadow=true; wheelG.add(ring);
  }
  for(let i=0;i<6;i++){
    const a=i*Math.PI/3;
    const s=new THREE.Mesh(new THREE.BoxGeometry(.05,.05,.9),spokeM);
    s.position.set(Math.cos(a)*.42,Math.sin(a)*.42,0); wheelG.add(s);
  }
  const hub=new THREE.Mesh(new THREE.CylinderGeometry(.13,.13,.9,8),spokeM);
  hub.rotation.x=Math.PI/2; wheelG.add(hub);

  /* ================= food bowl + carrot pile ================= */
  const bowl=new THREE.Mesh(new THREE.CylinderGeometry(.5,.36,.26,9),M(0xb39ddb));
  bowl.position.set(BOWL.x,FLOOR_Y+.13,BOWL.z); bowl.castShadow=bowl.receiveShadow=true; scene.add(bowl);
  const carrots=new THREE.Group(); carrots.position.set(BOWL.x,FLOOR_Y+.16,BOWL.z); scene.add(carrots);
  const carM=M(0xff9f43), leafM=M(0x63c97a);
  function carrot(x,z,ry){
    const c=new THREE.Group();
    const body=new THREE.Mesh(new THREE.ConeGeometry(.085,.3,6),carM);
    body.rotation.x=Math.PI; body.position.y=.15; body.castShadow=true;
    const leaf=new THREE.Mesh(new THREE.ConeGeometry(.05,.14,5),leafM); leaf.position.y=.36;
    c.add(body,leaf); c.position.set(x,0,z); c.rotation.y=ry; carrots.add(c);
  }
  carrot(0,0,0); carrot(.14,.1,.7); carrot(-.15,.08,-.5); carrot(.05,-.15,2.1); carrot(-.06,-.13,1.2);

  /* ================= tunnel ================= */
  const tunM=M(0x45c4b0,{side:THREE.DoubleSide,roughness:.8});
  const tun=new THREE.Mesh(new THREE.CylinderGeometry(.7,.7,2.2,9,1,true,0,Math.PI),tunM);
  tun.rotation.z=Math.PI/2; tun.position.set(TUN.x,FLOOR_Y+.7,TUN.z); tun.castShadow=true; scene.add(tun);
  const rimM=M(0x2fa893);
  for(const sx of [-1,1]){
    const rim=new THREE.Mesh(new THREE.TorusGeometry(.7,.05,5,14),rimM);
    rim.rotation.y=Math.PI/2; rim.position.set(TUN.x+sx*1.1,FLOOR_Y+.7,TUN.z); scene.add(rim);
  }

  /* ================= garden props ================= */
  const flowers=[];
  function flower(x,z,c){
    const g=new THREE.Group();
    const st=new THREE.Mesh(new THREE.CylinderGeometry(.035,.05,.5,5),M(0x5fae6b));
    st.position.y=.25; st.castShadow=true;
    const hd=new THREE.Mesh(new THREE.IcosahedronGeometry(.15,0),M(c));
    hd.position.y=.58; hd.castShadow=true;
    const ct=new THREE.Mesh(new THREE.SphereGeometry(.07,6,5),M(0xffd166)); ct.position.y=.6;
    g.add(st,hd,ct); g.position.set(x,0,z); g.rotation.y=rand(0,6); scene.add(g); flowers.push(g);
  }
  flower(6.8,2.4,0xff8fb2); flower(-6.6,-2.8,0xffd166); flower(5.8,-4.2,0xff8f6b); flower(-6.2,3.4,0xc39bf0);
  for(const [x,z] of [[7.5,-1.5],[-7.4,1.2],[3.2,5.6]]){
    const p=new THREE.Mesh(new THREE.IcosahedronGeometry(rand(.14,.22),0),M(0xb9c9a8));
    p.position.set(x,.1,z); p.scale.y=.6; p.castShadow=true; scene.add(p);
  }

  /* ================= poof effects ================= */
  const poofs=Array.from({length:8},()=>{
    const m=new THREE.Mesh(new THREE.IcosahedronGeometry(.16,0),
      new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0,depthWrite:false}));
    m.visible=false; scene.add(m); return {m,t:1};
  });
  let poofIdx=0;
  function poof(x,y,z,c=0xffffff){
    const p=poofs[poofIdx++%poofs.length];
    p.m.visible=true; p.m.position.set(x,y,z);
    p.m.material.color.setHex(c); p.m.material.opacity=.9; p.t=0;
  }

  /* ================= hamsters ================= */
  const HAM_DEFS=[
    {name:'Mochi',   body:0xf6e7c9, head:0xfcf5e6, dot:'#f6e7c9'},
    {name:'Biscuit', body:0xf0a95c, head:0xf7c07f, dot:'#f0a95c'},
    {name:'Pepper',  body:0x9aa0ae, head:0xb9bec9, dot:'#9aa0ae'},
    {name:'Clover',  body:0xfdf3e3, head:0xffffff, dot:'#9fd8a0'},
  ];
  const OFFS=[0,Math.PI,Math.PI,0];
  const hamsters=[];

  function makeHamster(def,x,z){
    const root=new THREE.Group(); root.position.set(x,FLOOR_Y,z);
    const bodyM=M(def.body), headM=M(def.head), pinkM=M(0xf7a8b8), darkM=M(0x2b2233,{roughness:.4});

    const body=new THREE.Mesh(new THREE.SphereGeometry(.34,8,6),bodyM);
    body.scale.set(1.05,.95,1.2); body.position.y=.3; body.castShadow=true;
    const head=new THREE.Mesh(new THREE.SphereGeometry(.24,8,6),headM);
    head.position.set(0,.42,.3); head.castShadow=true;
    const nose=new THREE.Mesh(new THREE.SphereGeometry(.04,6,5),pinkM); nose.position.set(0,.40,.545);
    const tail=new THREE.Mesh(new THREE.SphereGeometry(.06,6,5),bodyM); tail.position.set(0,.3,-.44);
    body.add(nose,tail);

    const eyes=[],cheeks=[],ears=[];
    for(const s of [-1,1]){
      const e=new THREE.Mesh(new THREE.SphereGeometry(.036,6,5),darkM);
      e.position.set(s*.105,.47,.5); head.add(e); eyes.push(e);
      const c=new THREE.Mesh(new THREE.SphereGeometry(.075,6,5),M(0xffc2cd));
      c.position.set(s*.17,.35,.42); body.add(c); cheeks.push(c);
      const er=new THREE.Mesh(new THREE.ConeGeometry(.09,.15,5),headM);
      er.position.set(s*.17,.6,.16); er.rotation.set(.15,0,-s*.4); er.castShadow=true;
      head.add(er); ears.push(er);
    }
    const feet=[];
    for(const [fx,fz] of [[-.15,.2],[.15,.2],[-.15,-.22],[.15,-.22]]){
      const f=new THREE.Mesh(new THREE.BoxGeometry(.1,.07,.13),bodyM);
      f.position.set(fx,.045,fz); body.add(f); feet.push(f);
    }
    root.add(body,head); scene.add(root);

    const h={root,body,head,eyes,cheeks,ears,feet,name:def.name,dot:def.dot,
      state:'idle',timer:rand(.5,1.5),tx:0,tz:0,phase:rand(0,6),speed:rand(1.05,1.45),
      seed:rand(0,10),crouchL:1,puffL:1,hop:0,poke:0,
      blinkT:rand(2,5),blinkA:0,twT:rand(2,6),twA:0,
      snack:null,_idleLbl:'',earBase:ears.map(e=>e.rotation.z)};
    root.traverse(o=>o.userData.ham=h);
    hamsters.push(h);
    return h;
  }
  makeHamster(HAM_DEFS[0],-1.6,.9);
  makeHamster(HAM_DEFS[1], 1.4,-.6);
  makeHamster(HAM_DEFS[2],-.4,-1.7);
  makeHamster(HAM_DEFS[3], 2.3,1.0);

  /* status chips */
  const feedEl=document.getElementById('feed');
  hamsters.forEach(h=>{
    const el=document.createElement('div'); el.className='chip';
    el.innerHTML=`<span class="dot" style="background:${h.dot}"></span><b>${h.name}</b><span class="act"></span>`;
    feedEl.appendChild(el); h.chip=el; h.actEl=el.querySelector('.act');
  });
  const LABELS={idle:'daydreaming',wander:'scurrying around',toWheel:'zooming to the wheel',
    wheel:'marathon mode 🏃',leaveWheel:'cooling off',toBowl:'smells carrots 🥕',eat:'munch munch',
    toTunnel:'tunnel time',tunnel:'whoosh — gone!',toSnack:'snack detected 🌻',eatSnack:'nom nom nom'};
  const IDLE_LBL=['napping 💤','staring at nothing','sniffing the air','plotting escape 👀','being a loaf'];
  function setChip(h){
    let txt;
    if(h.poke>0) txt='booped! 😳';
    else if(h.state==='idle') txt=h._idleLbl||pick(IDLE_LBL);
    else txt=LABELS[h.state];
    if(h.actEl.textContent!==txt){
      h.actEl.textContent=txt;
      h.chip.classList.remove('pop'); void h.chip.offsetWidth; h.chip.classList.add('pop');
    }
  }
  function setState(h,s,dur){ h.state=s; h.timer=dur; if(s!=='idle') h._idleLbl=''; setChip(h); }

  /* ================= snacks ================= */
  const snacks=[];
  const seedGeo=new THREE.SphereGeometry(.05,6,5), seedMat=M(0x6b4a2f);
  function updateCounter(){
    document.getElementById('counter').textContent='🐹 × 4 inside'+(snacks.length?` · 🌻 × ${snacks.length}`:'');
  }
  function spawnSnack(x,z){
    if(snacks.length>=4) removeSnack(snacks[0],false);
    const m=new THREE.Mesh(seedGeo,seedMat); m.scale.set(1,1.5,.8); m.castShadow=true;
    m.position.set(x,1.8,z); scene.add(m);
    snacks.push({mesh:m,x,z,vy:0,done:false,claimer:null});
    updateCounter();
  }
  function removeSnack(s,eaten){
    const i=snacks.indexOf(s); if(i<0) return;
    snacks.splice(i,1);
    poof(s.mesh.position.x,s.mesh.position.y+.08,s.mesh.position.z,eaten?0xfff1c9:0xffffff);
    scene.remove(s.mesh);
    if(s.claimer){
      const h=s.claimer; h.snack=null;
      if(h.state==='toSnack'||h.state==='eatSnack') setState(h,'idle',.6);
    }
    updateCounter();
  }
  function updateSnacks(dt){
    for(const s of [...snacks]){
      if(s.done) continue;
      s.vy-=24*dt; s.mesh.position.y+=s.vy*dt;
      if(s.mesh.position.y<=FLOOR_Y+.07){
        s.mesh.position.y=FLOOR_Y+.07;
        if(Math.abs(s.vy)>2){ s.vy*=-.35; s.mesh.scale.set(1.2,.9,.96); }
        else { s.vy=0; s.done=true; s.mesh.scale.set(1,1.5,.8); poof(s.x,FLOOR_Y+.15,s.z,0xfff6e0); }
      }
    }
  }

  /* ================= behaviour ================= */
  let riders=0, eaters=0, wheelSpeed=0;
  let foodLevel=1, refillT=14, foodPop=0;

  function steer(h,tx,tz,dt){
    const dx=tx-h.root.position.x, dz=tz-h.root.position.z;
    const d=Math.hypot(dx,dz);
    if(d>1e-4){
      h.root.rotation.y=lerpAngle(h.root.rotation.y,Math.atan2(dx,dz),1-Math.exp(-9*dt));
      const st=Math.min(h.speed*dt,d);
      h.root.position.x+=dx/d*st; h.root.position.z+=dz/d*st;
      h.phase+=st*9;
    }
    return d;
  }
  function pickTarget(h){
    for(let i=0;i<14;i++){
      const x=rand(-4.2,4.2), z=rand(-2.7,2.7);
      if(isClear(x,z)){ h.tx=x; h.tz=z; return; }
    }
    h.tx=rand(-4.2,4.2); h.tz=rand(-2.7,2.7);
  }
  function claimSnack(h){
    let best=null,bd=1e9;
    for(const s of snacks){
      if(s.claimer) continue;
      const d=Math.hypot(s.x-h.root.position.x,s.z-h.root.position.z);
      if(d<bd){ bd=d; best=s; }
    }
    if(best){ best.claimer=h; h.snack=best; }
    return best;
  }
  function decide(h){
    const s=claimSnack(h);
    if(s){ setState(h,'toSnack',99); return; }
    const r=Math.random();
    if(r<.40){ pickTarget(h); setState(h,'wander',99); }
    else if(r<.54) setState(h,'idle',rand(.8,2.4));
    else if(r<.70 && riders<1) setState(h,'toWheel',99);
    else if(r<.85 && foodLevel>.05 && eaters<1) setState(h,'toBowl',99);
    else if(r<.95) setState(h,'toTunnel',99);
    else { pickTarget(h); setState(h,'wander',99); }
  }

  function updateHamster(h,dt,t){
    h.timer-=dt;
    const walking=['wander','toWheel','toBowl','toTunnel','toSnack','leaveWheel'].includes(h.state);

    switch(h.state){
      case 'idle':     if(h.timer<=0) decide(h); break;
      case 'wander':   if(steer(h,h.tx,h.tz,dt)<.14) setState(h,'idle',rand(.5,1.8)); break;
      case 'toWheel':  if(steer(h,-4.35,WHEEL.z,dt)<.16){
                         if(riders<1){ riders++; setState(h,'wheel',rand(4,7)); }
                         else setState(h,'idle',rand(.5,1.2));
                       } break;
      case 'wheel':
        h.root.position.set(WHEEL.x,FLOOR_Y+Math.abs(Math.sin(t*8+h.seed))*.05,WHEEL.z);
        h.root.rotation.y=Math.PI/2; h.phase+=dt*11;
        if(h.timer<=0) setState(h,'leaveWheel',99);
        break;
      case 'leaveWheel': if(steer(h,-4.35,WHEEL.z,dt)<.16){ riders--; setState(h,'idle',rand(.5,1.6)); } break;
      case 'toBowl':
        if(steer(h,BOWL.x,BOWL.z+.75,dt)<.2){
          if(eaters<1){ eaters++; setState(h,'eat',rand(2.6,4.2)); }
          else setState(h,'idle',rand(.5,1.2));
        } break;
      case 'eat':{
        const a=Math.atan2(BOWL.x-h.root.position.x,BOWL.z-h.root.position.z);
        h.root.rotation.y=lerpAngle(h.root.rotation.y,a,1-Math.exp(-6*dt));
        foodLevel=Math.max(0,foodLevel-dt/4);
        if(h.timer<=0||foodLevel<=.02){ eaters--; setState(h,'idle',rand(.6,1.6)); }
        break;}
      case 'toTunnel': if(steer(h,TUN.inX,TUN.z,dt)<.16) setState(h,'tunnel',1.6); break;
      case 'tunnel':{
        h.root.visible=false;
        const p=1-h.timer/1.6, e=p*p*(3-2*p);
        h.root.position.set(THREE.MathUtils.lerp(TUN.inX,TUN.outX,e),FLOOR_Y,TUN.z);
        h.root.rotation.y=Math.PI/2;
        if(h.timer<=0){
          h.root.visible=true; h.hop=.35;
          poof(TUN.outX,FLOOR_Y+.4,TUN.z,0xaef0e6);
          setState(h,'idle',.8);
        }
        break;}
      case 'toSnack':
        if(!h.snack){ setState(h,'idle',.5); break; }
        if(steer(h,h.snack.x,h.snack.z,dt)<.24) setState(h,'eatSnack',1.4);
        break;
      case 'eatSnack':
        if(h.timer<=0){ const s=h.snack; h.snack=null; removeSnack(s,true); setState(h,'idle',rand(.5,1.4)); }
        break;
    }

    /* ---- shared animation ---- */
    const eating=(h.state==='eat'||h.state==='eatSnack');
    h.crouchL+=((eating?.8:1)-h.crouchL)*Math.min(1,dt*7);
    h.body.scale.y=.95*h.crouchL;
    h.puffL+=((eating?1.9:1)-h.puffL)*Math.min(1,dt*6);
    h.cheeks.forEach(c=>c.scale.setScalar(h.puffL));
    h.head.rotation.x+=((eating?.45+Math.sin(t*9+h.seed)*.18:0)-h.head.rotation.x)*Math.min(1,dt*8);

    if(walking){
      h.body.position.y=.3+Math.abs(Math.sin(h.phase))*.05;
      h.body.rotation.z=Math.sin(h.phase)*.06;
      h.feet.forEach((f,i)=>f.rotation.x=Math.sin(h.phase+OFFS[i])*.55);
    } else if(h.state==='wheel'){
      h.body.position.y=.3+Math.abs(Math.sin(h.phase))*.04;
      h.feet.forEach((f,i)=>f.rotation.x=Math.sin(h.phase+OFFS[i])*.8);
    } else {
      h.body.position.y=.3+Math.sin(t*2+h.seed)*.012;
      h.body.rotation.z*=(1-Math.min(1,dt*6));
      h.feet.forEach(f=>f.rotation.x*=(1-Math.min(1,dt*8)));
    }

    if(h.hop>0){ h.hop-=dt; h.root.position.y=FLOOR_Y+Math.sin((1-h.hop/.35)*Math.PI)*.28; }
    else if(h.state!=='wheel') h.root.position.y=FLOOR_Y;

    h.blinkT-=dt;
    if(h.blinkT<=0){ h.blinkT=rand(2.2,5.5); h.blinkA=.14; }
    if(h.blinkA>0){ h.blinkA-=dt; h.eyes.forEach(e=>e.scale.y=.15); }
    else h.eyes.forEach(e=>e.scale.y=1);

    h.twT-=dt;
    if(h.twT<=0){ h.twT=rand(2.5,6); h.twA=.18; }
    if(h.twA>0){ h.twA-=dt; h.ears[0].rotation.z=h.earBase[0]+Math.sin((1-h.twA/.18)*Math.PI)*.5; }
    else h.ears[0].rotation.z=h.earBase[0];

    if(h.poke>0){ h.poke-=dt; h.root.rotation.y+=dt*13; if(h.poke<=0) setChip(h); }
  }

  function updateWheel(dt){
    wheelSpeed+=((riders>0?6.5:0)-wheelSpeed)*Math.min(1,dt*1.8);
    wheelG.rotation.z-=wheelSpeed*dt;
  }
  function updateBowl(dt){
    if(foodLevel<=.001){
      refillT-=dt;
      if(refillT<=0){ foodLevel=1; refillT=14; foodPop=.4; poof(BOWL.x,FLOOR_Y+.4,BOWL.z,0xffb35c); }
    }
    foodPop=Math.max(0,foodPop-dt);
    const fs=Math.max(.001,foodLevel*(foodPop>0?1+Math.sin((1-foodPop/.4)*Math.PI)*.5:1));
    carrots.scale.setScalar(fs);
  }

  /* ================= picking: boop + toss ================= */
  const ray=new THREE.Raycaster(), ptr=new THREE.Vector2();
  let downPt=null;
  renderer.domElement.addEventListener('pointerdown',e=>{ downPt=[e.clientX,e.clientY]; });
  renderer.domElement.addEventListener('pointerup',e=>{
    if(!downPt) return;
    const dx=e.clientX-downPt[0], dy=e.clientY-downPt[1]; downPt=null;
    if(dx*dx+dy*dy>49) return; // was a drag, not a click
    ptr.set((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);
    ray.setFromCamera(ptr,camera);
    const roots=hamsters.map(h=>h.root).filter(r=>r.visible);
    const hh=ray.intersectObjects(roots,true)[0];
    if(hh){
      const h=hh.object.userData.ham;
      if(h){ h.poke=.55; poof(h.root.position.x,FLOOR_Y+.85,h.root.position.z,0xffc2cd); setChip(h); return; }
    }
    const fb=ray.intersectObject(bedding)[0];
    if(fb){
      const p=fb.point;
      if(Math.abs(p.x)<4.3 && Math.abs(p.z)<2.9 && isClear(p.x,p.z)) spawnSnack(p.x,p.z);
      else poof(p.x,FLOOR_Y+.2,p.z,0xffd166);
    }
  });
  document.getElementById('snackBtn').addEventListener('click',()=>{
    for(let i=0;i<24;i++){
      const x=rand(-3.9,3.9), z=rand(-2.5,2.5);
      if(isClear(x,z)){ spawnSnack(x,z); return; }
    }
  });

  /* ================= boot + loop ================= */
  hamsters.forEach(setChip);
  setState(hamsters[0],'toWheel',99);
  pickTarget(hamsters[1]); setState(hamsters[1],'wander',99);
  setState(hamsters[2],'toBowl',99);
  setState(hamsters[3],'idle',rand(1.2,2.2));

  addEventListener('resize',()=>{
    camera.aspect=innerWidth/innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth,innerHeight);
  });

  const clock=new THREE.Clock();
  let started=false;
  function tick(){
    requestAnimationFrame(tick);
    const dt=Math.min(clock.getDelta(),.05), t=clock.elapsedTime;
    controls.update();
    updateWheel(dt);
    updateBowl(dt);
    for(const h of hamsters) updateHamster(h,dt,t);
    updateSnacks(dt);
    for(const p of poofs){
      if(p.t>=1) continue;
      p.t+=dt/.5; const k=Math.min(1,p.t);
      p.m.scale.setScalar(.4+k*1.5);
      p.m.material.opacity=.9*(1-k);
      if(k>=1) p.m.visible=false;
    }
    flowers.forEach((f,i)=>f.rotation.z=Math.sin(t*1.3+i*1.7)*.07);
    renderer.render(scene,camera);
    if(!started){
      started=true; window.__pgStarted=true;
      document.getElementById('loader').classList.add('done');
    }
  }
  tick();
  </script>
</body>
</html>
```

**What's inside**

- **The cage** — wooden tray with sand bedding and pebbles, glass walls, dark-wood frame and posts, sitting on a mint meadow with swaying low-poly flowers.
- **Four named hamsters** (Mochi, Biscuit, Pepper, Clover), each built from flat-shaded primitives with blinking eyes, ear twitches, cheek puffs, trotting feet, and a little tail.
- **Three interactive props**: a drum-style wheel (spin-ups, hamster bobs inside, dismounts after a lap), a lavender bowl with a carrot pile that gets eaten down and magically refills, and a teal tunnel they sprint through and pop out of with a hop.
- **Autonomous AI** — a small state machine (wander / idle / wheel / eat / tunnel / chase-snack) with soft steering, so the cage always has something happening.
- **You can join in**: drag to orbit (auto-rotates until you touch it), scroll to zoom, **click the bedding** to drop a sunflower seed that bounces down and gets claimed, **click a hamster** to boop it (it does a dizzy spin), or hit the *Toss a snack* button.
- **Live status feed** — each hamster has a chip in the corner narrating what it's doing ("marathon mode 🏃", "whoosh — gone!"), updating with a little pop.

**Notes**: it needs an internet connection for the Three.js CDN and Google Fonts; everything else is self-contained in the single file. If WebGL is unavailable or the CDN is unreachable, the loader tells you why instead of hanging silently.