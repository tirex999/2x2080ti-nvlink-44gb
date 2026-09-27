

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐹 Low-Poly Hamster Playground</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{overflow:hidden;background:#87CEEB}
  canvas{display:block}
  #ui{position:fixed;top:20px;left:20px;color:#fff;font-family:'Segoe UI',Tahoma,sans-serif;pointer-events:none;z-index:10}
  #ui h1{font-size:26px;text-shadow:0 2px 8px rgba(0,0,0,.35);margin-bottom:4px}
  #ui p{font-size:13px;opacity:.8;text-shadow:0 1px 4px rgba(0,0,0,.3)}
</style>
</head>
<body>
<div id="ui"><h1>🐹 Hamster Playground</h1><p>Drag to rotate · Scroll to zoom</p></div>

<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>

<script type="module">
import*as THREE from'three';
import{OrbitControls}from'three/addons/controls/OrbitControls.js';

/* ── helpers ─────────────────────────────────────────── */
const M=(c)=>new THREE.MeshLambertMaterial({color:c,flatShading:true});

/* ── scene / camera / renderer ───────────────────────── */
const scene=new THREE.Scene();
const bgC=document.createElement('canvas');bgC.width=2;bgC.height=512;
const bgX=bgC.getContext('2d');const gr=bgX.createLinearGradient(0,0,0,512);
gr.addColorStop(0,'#6BB8E8');gr.addColorStop(.55,'#A8D8F0');gr.addColorStop(1,'#E8F4FF');
bgX.fillStyle=gr;bgX.fillRect(0,0,2,512);
scene.background=new THREE.CanvasTexture(bgC);
scene.fog=new THREE.Fog(0xC8E8F8,28,55);

const camera=new THREE.PerspectiveCamera(48,innerWidth/innerHeight,.1,100);
camera.position.set(10,8,12);

const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth,innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.15;
document.body.appendChild(renderer.domElement);

const ctrl=new OrbitControls(camera,renderer.domElement);
ctrl.target.set(0,1.4,0);ctrl.enableDamping=true;ctrl.dampingFactor=.07;
ctrl.maxPolarAngle=Math.PI/2.05;ctrl.minDistance=5;ctrl.maxDistance=24;ctrl.update();

/* ── lights ──────────────────────────────────────────── */
scene.add(new THREE.AmbientLight(0xfff5e6,.65));
scene.add(new THREE.HemisphereLight(0x87CEEB,0xDEB887,.35));
const sun=new THREE.DirectionalLight(0xffffff,1.9);
sun.position.set(6,14,8);sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
const sc=sun.shadow.camera;sc.left=-10;sc.right=10;sc.top=10;sc.bottom=-10;sc.near=1;sc.far=35;
sun.shadow.bias=-.0008;scene.add(sun);
const fill=new THREE.DirectionalLight(0xadd8ff,.35);fill.position.set(-6,5,-6);scene.add(fill);

/* ── table ───────────────────────────────────────────── */
const table=new THREE.Mesh(new THREE.BoxGeometry(32,.35,32),M(0xD2B48C));
table.position.y=-.175;table.receiveShadow=true;scene.add(table);

/* ── cage ────────────────────────────────────────────── */
function buildCage(){
  const g=new THREE.Group(),W=7,D=5,wH=.55,bH=3.6,tw=.13;
  const tM=M(0x7EC8E3),wM=M(0x5BA3C4),bM=M(0xC0C0C0),fM=M(0xB0B0B0);
  const bot=new THREE.Mesh(new THREE.BoxGeometry(W,.14,D),tM);
  bot.position.y=.07;bot.receiveShadow=true;g.add(bot);
  [[0,.14+wH/2,D/2-tw/2,W,wH,tw],[0,.14+wH/2,-(D/2-tw/2),W,wH,tw],
   [-(W/2-tw/2),.14+wH/2,0,tw,wH,D],[W/2-tw/2,.14+wH/2,0,tw,wH,D]].forEach(d=>{
    const m=new THREE.Mesh(new THREE.BoxGeometry(d[3],d[4],d[5]),wM);
    m.position.set(d[0],d[1],d[2]);g.add(m);
  });
  const barG=new THREE.CylinderGeometry(.028,.028,bH,5);
  const bY=.14+wH+bH/2;
  for(let x=-W/2+.5;x<=W/2-.3;x+=.52){
    [D/2-.06,-(D/2-.06)].forEach(z=>{const b=new THREE.Mesh(barG,bM);b.position.set(x,bY,z);g.add(b)});
  }
  for(let z=-D/2+.5;z<=D/2-.3;z+=.52){
    [W/2-.06,-(W/2-.06)].forEach(x=>{const b=new THREE.Mesh(barG,bM);b.position.set(x,bY,z);g.add(b)});
  }
  const tY=.14+wH+bH;
  const fG1=new THREE.BoxGeometry(W+.06,.07,.07),fG2=new THREE.BoxGeometry(.07,.07,D+.06);
  [D/2,-(D/2)].forEach(z=>{const f=new THREE.Mesh(fG1,fM);f.position.set(0,tY,z);g.add(f)});
  [W/2,-(W/2)].forEach(x=>{const f=new THREE.Mesh(fG2,fM);f.position.set(x,tY,0);g.add(f)});
  for(let x=-W/2+.9;x<=W/2-.6;x+=.85){
    const cb=new THREE.Mesh(new THREE.BoxGeometry(.04,.04,D-.1),fM);cb.position.set(x,tY,0);g.add(cb);
  }
  return g;
}
scene.add(buildCage());

/* ── bedding ─────────────────────────────────────────── */
{const g=new THREE.Group(),geo=new THREE.BoxGeometry(.19,.04,.09);
 const cols=[0xDEB887,0xF5DEB3,0xD2B48C,0xFAEBD7,0xC4A882,0xE8D5B5];
 for(let i=0;i<90;i++){const m=new THREE.Mesh(geo,M(cols[i%cols.length]));
  m.position.set((Math.random()-.5)*6.2,.15+Math.random()*.03,(Math.random()-.5)*4.2);
  m.rotation.set(Math.random()*.3-.15,Math.random()*Math.PI,Math.random()*.2-.1);g.add(m);}
 scene.add(g);}

/* ── wheel ───────────────────────────────────────────── */
function buildWheel(){
  const g=new THREE.Group(),spin=new THREE.Group();
  const rM=M(0x4FC3F7),sM=M(0xFF8A65);
  const rG=new THREE.TorusGeometry(1,.055,6,14);
  [-.24,.24].forEach(z=>{const r=new THREE.Mesh(rG,rM);r.rotation.x=Math.PI/2;r.position.z=z;spin.add(r)});
  const sG=new THREE.CylinderGeometry(1,1,.48,14,1,true);
  const srf=new THREE.Mesh(sG,new THREE.MeshLambertMaterial({color:0x81D4FA,flatShading:true,side:THREE.DoubleSide,transparent:true,opacity:.25}));
  srf.rotation.x=Math.PI/2;spin.add(srf);
  for(let i=0;i<6;i++){const s=new THREE.Mesh(new THREE.CylinderGeometry(.025,.025,.92,4),sM);
    s.position.y=.46;const p=new THREE.Group();p.add(s);p.rotation.z=i/6*Math.PI*2;spin.add(p);}
  const ax=new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,.65,6),M(0xaaa));ax.rotation.x=Math.PI/2;spin.add(ax);
  g.add(spin);
  const stM=M(0x999);
  [-.3,.3].forEach(z=>{const s=new THREE.Mesh(new THREE.BoxGeometry(.07,1.2,.07),stM);s.position.set(0,-.6,z);g.add(s)});
  const base=new THREE.Mesh(new THREE.BoxGeometry(.55,.07,.75),stM);base.position.y=-1.2;g.add(base);
  g.userData={spin};return g;
}
const wheel=buildWheel();wheel.position.set(-.8,1.35,-2.2);scene.add(wheel);

/* ── bowl ────────────────────────────────────────────── */
function buildBowl(){
  const g=new THREE.Group();
  const b=new THREE.Mesh(new THREE.CylinderGeometry(.38,.26,.2,8),M(0xFF6B6B));b.position.y=.1;b.castShadow=true;g.add(b);
  const r=new THREE.Mesh(new THREE.TorusGeometry(.38,.035,5,8),M(0xE55555));r.rotation.x=Math.PI/2;r.position.y=.2;g.add(r);
  const pG=new THREE.SphereGeometry(.055,4,3),cs=[0x8B4513,0xDAA520,0x228B22,0xFF6347,0xCD853F];
  for(let i=0;i<12;i++){const p=new THREE.Mesh(pG,M(cs[i%5]));
    const a=i/12*Math.PI*2+Math.random()*.4,rd=.06+Math.random()*.16;
    p.position.set(Math.cos(a)*rd,.22+Math.random()*.04,Math.sin(a)*rd);g.add(p);}
  return g;
}
const bowl=buildBowl();bowl.position.set(2.3,.15,1.1);scene.add(bowl);

/* ── hideout ─────────────────────────────────────────── */
{const g=new THREE.Group();
 const bx=new THREE.Mesh(new THREE.BoxGeometry(1.3,.85,1.1),M(0xCD853F));bx.position.y=.425;bx.castShadow=true;g.add(bx);
 const rf=new THREE.Mesh(new THREE.BoxGeometry(1.5,.13,1.3),M(0xA0522D));rf.position.y=.92;g.add(rf);
 const dr=new THREE.Mesh(new THREE.BoxGeometry(.38,.45,.06),M(0x1a0e05));dr.position.set(0,.32,.56);g.add(dr);
 g.position.set(-2.2,.15,-.8);scene.add(g);}

/* ── water bottle ────────────────────────────────────── */
{const g=new THREE.Group();
 const b=new THREE.Mesh(new THREE.CylinderGeometry(.13,.13,.75,6),
   new THREE.MeshLambertMaterial({color:0xADD8E6,transparent:true,opacity:.55,flatShading:true}));
 b.position.y=.375;g.add(b);
 const c=new THREE.Mesh(new THREE.CylinderGeometry(.06,.13,.13,6),M(0xFF6B6B));c.position.y=.82;g.add(c);
 const t=new THREE.Mesh(new THREE.CylinderGeometry(.018,.018,.35,4),M(0xbbb));t.position.y=-.18;g.add(t);
 g.position.set(3.38,1.6,0);scene.add(g);}

/* ── toy ball ────────────────────────────────────────── */
{const ball=new THREE.Mesh(new THREE.SphereGeometry(.16,6,5),M(0xFF69B4));
 ball.position.set(1.2,.31,.6);ball.castShadow=true;scene.add(ball);}

/* ── hamster model ───────────────────────────────────── */
function buildHamster(bc,bc2,ec){
  const g=new THREE.Group(),bM=M(bc),blM=M(bc2),eM=M(ec||0xFFB6C1),dk=M(0x1a1a1a);

  const body=new THREE.Mesh(new THREE.SphereGeometry(.42,7,5),bM);
  body.scale.set(1,.82,1.18);body.position.y=.4;body.castShadow=true;g.add(body);

  const belly=new THREE.Mesh(new THREE.SphereGeometry(.33,6,4),blM);
  belly.scale.set(.88,.68,1);belly.position.set(0,.3,.08);g.add(belly);

  const head=new THREE.Mesh(new THREE.SphereGeometry(.32,6,5),bM);
  head.position.set(0,.6,.34);head.castShadow=true;g.add(head);

  const cG=new THREE.SphereGeometry(.14,5,4);
  const lC=new THREE.Mesh(cG,blM);lC.position.set(-.2,.5,.5);g.add(lC);
  const rC=new THREE.Mesh(cG,blM);rC.position.set(.2,.5,.5);g.add(rC);

  const eG=new THREE.SphereGeometry(.095,5,4);
  const lE=new THREE.Mesh(eG,eM);lE.position.set(-.17,.84,.24);lE.scale.set(1,1.3,.55);g.add(lE);
  const rE=new THREE.Mesh(eG,eM);rE.position.set(.17,.84,.24);rE.scale.set(1,1.3,.55);g.add(rE);

  const eyG=new THREE.SphereGeometry(.05,5,4);
  g.add(Object.assign(new THREE.Mesh(eyG,dk),{position:new THREE.Vector3(-.12,.64,.58)}));
  g.add(Object.assign(new THREE.Mesh(eyG,dk),{position:new THREE.Vector3(.12,.64,.58)}));
  const hG=new THREE.SphereGeometry(.02,4,3),hM=new THREE.MeshBasicMaterial({color:0xffffff});
  g.add(Object.assign(new THREE.Mesh(hG,hM),{position:new THREE.Vector3(-.1,.66,.61)}));
  g.add(Object.assign(new THREE.Mesh(hG,hM),{position:new THREE.Vector3(.14,.66,.61)}));

  const nose=new THREE.Mesh(new THREE.SphereGeometry(.04,4,3),M(0xFF8FAB));
  nose.position.set(0,.55,.65);g.add(nose);

  const wM=new THREE.LineBasicMaterial({color:0x999});
  [[[-.09,.53,.64],[-.38,.56,.72]],[[-.09,.51,.64],[-.36,.49,.74]],
   [[.09,.53,.64],[.38,.56,.72]],[[.09,.51,.64],[.36,.49,.74]]].forEach(([a,b])=>{
    g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]),wM));});

  const lG=new THREE.CylinderGeometry(.06,.05,.19,5),lM=M(bc);
  const legs=[];
  [[-.22,.095,.24],[.22,.095,.24],[-.22,.095,-.24],[.22,.095,-.24]].forEach(p=>{
    const l=new THREE.Mesh(lG,lM);l.position.set(...p);l.castShadow=true;g.add(l);legs.push(l);});

  const tail=new THREE.Mesh(new THREE.SphereGeometry(.055,4,3),bM);
  tail.position.set(0,.36,-.55);g.add(tail);

  g.userData={body,head,legs};return g;
}

/* ── hamster agent ───────────────────────────────────── */
const BND={xMin:-2.7,xMax:2.7,zMin:-1.7,zMax:1.7},FY=.16;

class Agent{
  constructor(mesh,pos,wheel=false){
    this.mesh=mesh;this.legs=mesh.userData.legs;this.body=mesh.userData.body;this.head=mesh.userData.head;
    this.isWheel=wheel;this.st='IDLE';this.t=0;this.time=Math.random()*99;
    this.spd=.55+Math.random()*.45;this.baseY=FY;
    if(!wheel){mesh.position.set(pos.x,FY,pos.z);mesh.rotation.y=Math.random()*Math.PI*2;}
  }
  go(s){this.st=s;this.t=0;}
  pick(){const r=Math.random();if(r<.38)this.go('WALK');else if(r<.6)this.go('TURN');
    else if(r<.72)this.go('POPCORN');else this.go('IDLE');}
  update(dt){
    this.time+=dt;this.t+=dt;
    if(this.isWheel){this.wheelRun(dt);return;}
    switch(this.st){
      case'IDLE':this.idle(dt);break;case'WALK':this.walk(dt);break;
      case'TURN':this.turn(dt);break;case'POPCORN':this.pop(dt);break;
    }
    const b=1+Math.sin(this.time*3)*.018;
    this.body.scale.set(1*b,.82,1.18*b);
  }
  idle(dt){
    this.mesh.rotation.z=Math.sin(this.time*1.4)*.03;
    if(this.t>1.8+Math.random()*3)this.pick();
  }
  walk(dt){
    const d=new THREE.Vector3(0,0,1).applyAxisAngle(new THREE.Vector3(0,1,0),this.mesh.rotation.y);
    this.mesh.position.addScaledVector(d,this.spd*dt);
    this.mesh.position.y=FY+Math.sin(this.time*10)*.022;
    this.mesh.rotation.z=Math.sin(this.time*8)*.04;
    this.legs.forEach((l,i)=>{const ph=(i<2?0:Math.PI)+(i%2?Math.PI:0);l.rotation.x=Math.sin(this.time*13+ph)*.45;});
    const p=this.mesh.position;
    if(p.x<BND.xMin||p.x>BND.xMax||p.z<BND.zMin||p.z>BND.zMax)this.go('TURN');
    if(this.t>1.5+Math.random()*2.5)this.pick();
  }
  turn(dt){
    this.mesh.rotation.y+=(2.2+Math.random()*.5)*dt;
    this.mesh.rotation.z=Math.sin(this.time*6)*.06;
    if(this.t>.5+Math.random()*.4)this.go('WALK');
  }
  pop(dt){
    const p=this.t/.38;
    if(p<1){this.mesh.position.y=FY+Math.sin(p*Math.PI)*.38;this.mesh.rotation.x=Math.sin(p*Math.PI)*.25;}
    else{this.mesh.position.y=FY;this.mesh.rotation.x=0;}
    this.legs.forEach(l=>l.rotation.x=-.45);
    if(this.t>.5){this.legs.forEach(l=>l.rotation.x=0);this.go('IDLE');}
  }
  wheelRun(dt){
    this.legs.forEach((l,i)=>{const ph=(i<2?0:Math.PI)+(i%2?Math.PI:0);l.rotation.x=Math.sin(this.time*19+ph)*.5;});
    this.mesh.position.y=this.baseY+Math.sin(this.time*19)*.012;
    if(Math.random()<.004)this.spd=.4+Math.random()*1.1;
  }
}

/* ── spawn hamsters ──────────────────────────────────── */
const cfgs=[
  {c:0xF5DEB3,b:0xFFF8F0,e:0xFFB6C1,p:{x:.6,z:.6},w:false,s:1.15},
  {c:0xE8A317,b:0xFFF5E0,e:0xFFB6C1,p:{x:-1.4,z:1.1},w:false,s:1.25},
  {c:0xFFF5EE,b:0xFFE4E1,e:0xFFB6C1,p:{x:1.6,z:-.6},w:false,s:1.05},
  {c:0xD2691E,b:0xF5DEB3,e:0xFFB6C1,p:{x:0,z:0},w:true,s:1.2},
];
const agents=[];
cfgs.forEach(c=>{
  const m=buildHamster(c.c,c.b,c.e);m.scale.setScalar(c.s);scene.add(m);
  const a=new Agent(m,c.p,c.w);agents.push(a);
  if(c.w){
    m.position.set(wheel.position.x,wheel.position.y-1.0+.12,wheel.position.z);
    m.rotation.y=0;a.baseY=m.position.y;
  }
});

/* ── loop ────────────────────────────────────────────── */
const clock=new THREE.Clock();
(function anim(){
  requestAnimationFrame(anim);
  const dt=Math.min(clock.getDelta(),.05);
  agents.forEach(a=>a.update(dt));
  const ws=agents.find(a=>a.isWheel)?.spd||.8;
  wheel.userData.spin.rotation.z-=ws*dt*2.2;
  ctrl.update();renderer.render(scene,camera);
})();

/* ── resize ──────────────────────────────────────────── */
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
</script>
</body>
</html>
```

**What you get when you open this file:**

| Element | Details |
|---|---|
| **4 low-poly hamsters** | Cream, golden, white, and cinnamon — each with puffy cheeks, tiny ears, whiskers, eye highlights, and stubby legs |
| **Autonomous AI** | Walk → Turn → Idle → **Popcorn jump** 🍿 (hamsters randomly do tiny vertical hops, just like real ones) |
| **Spinning wheel** | One golden hamster runs on a blue wheel with orange spokes; the wheel speed varies randomly |
| **Full cage** | Wire bars, plastic tray, top frame with cross-bars |
| **Accessories** | Food bowl with colorful pellets, wooden hideout, water bottle, pink toy ball, scattered wood-shaving bedding |
| **Lighting** | Warm directional sun + cool fill + hemisphere + soft shadows |
| **Sky gradient** | Canvas-generated blue-to-white background with distance fog |

**Controls:** drag to orbit, scroll to zoom. Everything runs at 60 fps with no build step needed.