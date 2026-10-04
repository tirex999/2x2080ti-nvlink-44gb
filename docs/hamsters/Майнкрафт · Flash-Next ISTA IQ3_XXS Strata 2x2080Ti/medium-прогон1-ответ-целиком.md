```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>mc.html - Voxel Sandbox</title>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; height: 100%; background: #000; font-family: Arial, Helvetica, sans-serif; }
  canvas { display: block; }
  #crosshair { position: fixed; left: 50%; top: 50%; width: 2px; height: 20px; background: rgba(255,255,255,0.9); transform: translate(-50%,-50%); pointer-events: none; z-index: 10; }
  #crosshairH { position: fixed; left: 50%; top: 50%; width: 20px; height: 2px; background: rgba(255,255,255,0.9); transform: translate(-50%,-50%); pointer-events: none; z-index: 10; }
  #hotbar { position: fixed; left: 50%; bottom: 14px; transform: translateX(-50%); display: flex; gap: 6px; background: rgba(0,0,0,0.55); padding: 8px; border-radius: 6px; z-index: 10; }
  .slot { width: 44px; height: 44px; border: 2px solid rgba(255,255,255,0.25); border-radius: 4px; position: relative; box-sizing: border-box; }
  .slot.sel { border-color: #ffffff; box-shadow: 0 0 8px rgba(255,255,255,0.6); }
  .slot span { position: absolute; left: 3px; top: 1px; color: #fff; font-size: 11px; text-shadow: 1px 1px 1px #000; }
  #overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.65); color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 20; cursor: pointer; text-align: center; }
  #overlay h1 { font-size: 42px; margin: 0 0 18px 0; letter-spacing: 2px; }
  #overlay ul { list-style: none; padding: 0; margin: 0 0 22px 0; line-height: 1.7; font-size: 15px; color: #ddd; }
  #overlay .play { font-size: 22px; color: #fff; background: rgba(255,255,255,0.12); padding: 10px 26px; border-radius: 6px; }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="crosshairH"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>VOXELCRAFT</h1>
  <ul>
    <li>WASD — move &nbsp;|&nbsp; Space — jump</li>
    <li>Mouse — look around (after click)</li>
    <li>Left click — break block &nbsp;|&nbsp; Right click — place block</li>
    <li>Keys 1–7 or mouse wheel — select block</li>
    <li>Esc — release mouse</li>
  </ul>
  <div class="play">Click to play</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

/* ---------------- constants ---------------- */
var CHUNK = 16, HEIGHT = 80;
var COLORS = {1:0x4caf50, 2:0x795548, 3:0x9e9e9e, 4:0xe7d9a8, 5:0x8d6e63, 6:0x2e7d32, 7:0xffffff};
var HOTBAR_IDS = [1,2,3,4,5,6,7];
var HOTBAR_NAMES = ["Grass","Dirt","Stone","Sand","Wood","Leaves","Snow"];

/* ---------------- three.js scene ---------------- */
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 110);

var camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 400);
camera.rotation.order = "YXZ";

var renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1, 2));
document.body.appendChild(renderer.domElement);
var canvas = renderer.domElement;

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(60, 120, 40);
scene.add(sun);

var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });

/* target outline */
var outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.003,1.003,1.003)),
  new THREE.LineBasicMaterial({color:0x000000})
);
outline.visible = false;
scene.add(outline);

/* water plane */
var water = new THREE.Mesh(
  new THREE.PlaneGeometry(400,400),
  new THREE.MeshBasicMaterial({color:0x3b7dd8, transparent:true, opacity:0.55})
);
water.rotation.x = -Math.PI/2;
water.position.y = 14.3;
scene.add(water);

/* clouds */
var clouds = [];
var cloudMat = new THREE.MeshBasicMaterial({color:0xffffff, transparent:true, opacity:0.8, fog:false});
for (var ci=0; ci<25; ci++){
  var cw = 12 + hash3(ci,7,3)*22;
  var cd = 12 + hash3(ci,11,5)*22;
  var cm = new THREE.Mesh(new THREE.BoxGeometry(cw, 2.5, cd), cloudMat);
  cm.position.set((hash3(ci,1,1)-0.5)*320, 90, (hash3(ci,2,2)-0.5)*320);
  scene.add(cm);
  clouds.push(cm);
}

/* ---------------- noise ---------------- */
function hash3(x,y,z){
  var h = Math.imul(x|0, 374761393) ^ Math.imul(y|0, 668265263) ^ Math.imul(z|0, 1274126177);
  h = Math.imul(h ^ (h>>>13), 1274126177);
  h = h ^ (h>>>16);
  return (h>>>0) / 4294967296;
}
function smoothstep(t){ return t*t*(3-2*t); }
function noise2(x,z){
  var xi=Math.floor(x), zi=Math.floor(z);
  var xf=x-xi, zf=z-zi;
  var a=hash3(xi,0,zi), b=hash3(xi+1,0,zi), c=hash3(xi,0,zi+1), d=hash3(xi+1,0,zi+1);
  var u=smoothstep(xf), v=smoothstep(zf);
  return a*(1-u)*(1-v) + b*u*(1-v) + c*(1-u)*v + d*u*v;
}
function fractal2(x,z){
  var sum=0, amp=1, tot=0, f=1;
  for (var o=0;o<4;o++){ sum += noise2(x*f, z*f)*amp; tot+=amp; amp*=0.5; f*=2; }
  return sum/tot;
}
function noise3(x,y,z){
  var xi=Math.floor(x), yi=Math.floor(y), zi=Math.floor(z);
  var xf=x-xi, yf=y-yi, zf=z-zi;
  var u=smoothstep(xf), v=smoothstep(yf), w=smoothstep(zf);
  var c000=hash3(xi,yi,zi),   c100=hash3(xi+1,yi,zi);
  var c010=hash3(xi,yi+1,zi), c110=hash3(xi+1,yi+1,zi);
  var c001=hash3(xi,yi,zi+1), c101=hash3(xi+1,yi,zi+1);
  var c011=hash3(xi,yi+1,zi+1), c111=hash3(xi+1,yi+1,zi+1);
  var x00=c000*(1-u)+c100*u, x10=c010*(1-u)+c110*u;
  var x01=c001*(1-u)+c101*u, x11=c011*(1-u)+c111*u;
  var y0=x00*(1-v)+x10*v, y1=x01*(1-v)+x11*v;
  return y0*(1-w)+y1*w;
}

/* ---------------- chunks ---------------- */
var chunks = new Map();          // key -> {data:Uint8Array, mesh:Mesh|null}
var chunkMeshes = [];            // global array for raycasting

function key(cx,cz){ return cx + "," + cz; }
function getChunk(cx,cz){ return chunks.get(key(cx,cz)); }

function readBlock(x,y,z){
  if (y < 0 || y >= HEIGHT) return 0;
  var cx = Math.floor(x/16), cz = Math.floor(z/16);
  var c = chunks.get(key(cx,cz));
  if (!c) return 0;
  var lx = x - cx*16, lz = z - cz*16;
  return c.data[lx + lz*16 + y*256];
}
function writeBlock(x,y,z,id){
  if (y < 0 || y >= HEIGHT) return;
  var cx = Math.floor(x/16), cz = Math.floor(z/16);
  var c = chunks.get(key(cx,cz));
  if (!c) return;
  var lx = x - cx*16, lz = z - cz*16;
  c.data[lx + lz*16 + y*256] = id;
}

function genChunk(cx,cz){
  var data = new Uint8Array(16*16*HEIGHT);
  function setLocal(lx,y,lz,id){ if(y>=0&&y<HEIGHT) data[lx + lz*16 + y*256] = id; }
  function setIfAir(lx,y,lz,id){
    if(y<0||y>=HEIGHT||lx<0||lx>15||lz<0||lz>15) return;
    var i = lx + lz*16 + y*256;
    if (data[i] === 0) data[i] = id;
  }
  for (var lx=0; lx<16; lx++){
    for (var lz=0; lz<16; lz++){
      var wx = cx*16 + lx, wz = cz*16 + lz;
      var m = fractal2(wx*0.004, wz*0.004);
      var h = fractal2(wx*0.02, wz*0.02);
      var H = Math.floor(5 + m*m*58 + h*10);
      if (H > HEIGHT-10) H = HEIGHT-10;
      for (var y=0; y<=H; y++){
        var id;
        if (y === 0) id = 3;
        else if (y < H-3) id = 3;
        else if (y < H) id = (H <= 16) ? 4 : (H >= 37 ? 3 : 2);
        else id = (H >= 46) ? 7 : (H >= 37) ? 3 : (H <= 16) ? 4 : 1;
        data[lx + lz*16 + y*256] = id;
      }
      // caves
      for (var cy=3; cy<=H-2; cy++){
        var idx = lx + lz*16 + cy*256;
        if (data[idx] !== 0 && noise3(wx*0.09, cy*0.09, wz*0.09) > 0.67) data[idx] = 0;
      }
      // trees on grass columns
      if (H > 16 && H < 37 && lx >= 2 && lx <= 13 && lz >= 2 && lz <= 13 && hash3(wx,999,wz) < 0.02){
        for (var t=1; t<=4; t++) setLocal(lx, H+t, lz, 5);
        for (var dy=5; dy<=6; dy++)
          for (var dx=-2; dx<=2; dx++)
            for (var dz=-2; dz<=2; dz++)
              setIfAir(lx+dx, H+dy, lz+dz, 6);
        for (var dx2=-1; dx2<=1; dx2++)
          for (var dz2=-1; dz2<=1; dz2++)
            setIfAir(lx+dx2, H+7, lz+dz2, 6);
        setIfAir(lx, H+8, lz, 6);
      }
    }
  }
  return data;
}

/* face table: normal + 4 corner offsets (wound CCW from outside) */
var FACES = [
  {n:[ 1,0,0], v:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]]},
  {n:[-1,0,0], v:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]},
  {n:[0, 1,0], v:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]]},
  {n:[0,-1,0], v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
  {n:[0,0, 1], v:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]},
  {n:[0,0,-1], v:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]]}
];

function removeMesh(c){
  if (c.mesh){
    scene.remove(c.mesh);
    var i = chunkMeshes.indexOf(c.mesh);
    if (i >= 0) chunkMeshes.splice(i,1);
    c.mesh.geometry.dispose();
    c.mesh = null;
  }
}

function buildChunkMesh(cx,cz){
  var c = chunks.get(key(cx,cz));
  if (!c) return;
  removeMesh(c);
  var pos=[], nor=[], col=[];
  for (var lx=0; lx<16; lx++){
    for (var lz=0; lz<16; lz++){
      for (var y=0; y<HEIGHT; y++){
        var id = c.data[lx + lz*16 + y*256];
        if (id === 0) continue;
        var x = cx*16 + lx, z = cz*16 + lz;
        var base = COLORS[id];
        var r = ((base>>16)&255)/255, g = ((base>>8)&255)/255, b = (base&255)/255;
        for (var fi=0; fi<6; fi++){
          var f = FACES[fi];
          if (readBlock(x+f.n[0], y+f.n[1], z+f.n[2]) !== 0) continue;
          var shade = (f.n[1] === 1) ? 1.0 : (f.n[1] === -1 ? 0.55 : 0.8);
          var cr = r*shade, cg = g*shade, cb = b*shade;
          var order = [0,1,2,0,2,3];
          for (var oi=0; oi<6; oi++){
            var v = f.v[order[oi]];
            pos.push(x+v[0], y+v[1], z+v[2]);
            nor.push(f.n[0], f.n[1], f.n[2]);
            col.push(cr, cg, cb);
          }
        }
      }
    }
  }
  if (pos.length === 0) return;
  var geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos,3));
  geo.setAttribute("normal", new THREE.Float32BufferAttribute(nor,3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col,3));
  var mesh = new THREE.Mesh(geo, blockMaterial);
  mesh.position.set(0,0,0);
  mesh.matrixAutoUpdate = false; mesh.updateMatrix();
  scene.add(mesh);
  c.mesh = mesh;
  chunkMeshes.push(mesh);
}

function rebuildAt(cx,cz){ buildChunkMesh(cx,cz); }

function editBlock(x,y,z,id){
  writeBlock(x,y,z,id);
  var cx = Math.floor(x/16), cz = Math.floor(z/16);
  var lx = x - cx*16, lz = z - cz*16;
  rebuildAt(cx,cz);
  if (lx === 0)  rebuildAt(cx-1,cz);
  if (lx === 15) rebuildAt(cx+1,cz);
  if (lz === 0)  rebuildAt(cx,cz-1);
  if (lz === 15) rebuildAt(cx,cz+1);
}

function updateChunks(){
  var pcx = Math.floor(player.x/16), pcz = Math.floor(player.z/16);
  // generate data within 5 chunks, max 4 per frame
  var gen = 0;
  for (var dx=-5; dx<=5 && gen<4; dx++){
    for (var dz=-5; dz<=5 && gen<4; dz++){
      var cx = pcx+dx, cz = pcz+dz;
      var k = key(cx,cz);
      if (!chunks.has(k)){
        chunks.set(k, {data: genChunk(cx,cz), mesh:null});
        gen++;
      }
    }
  }
  // build meshes within 4 chunks if all 4 neighbors have data, max 2 per frame
  var built = 0;
  for (var bx=-4; bx<=4 && built<2; bx++){
    for (var bz=-4; bz<=4 && built<2; bz++){
      var cx2 = pcx+bx, cz2 = pcz+bz;
      var c = chunks.get(key(cx2,cz2));
      if (c && !c.mesh &&
          chunks.has(key(cx2+1,cz2)) && chunks.has(key(cx2-1,cz2)) &&
          chunks.has(key(cx2,cz2+1)) && chunks.has(key(cx2,cz2-1))){
        buildChunkMesh(cx2,cz2);
        built++;
      }
    }
  }
  // unload beyond 7
  var toDelete = [];
  chunks.forEach(function(c,k){
    var p = k.split(",");
    var cx3 = parseInt(p[0],10), cz3 = parseInt(p[1],10);
    if (Math.abs(cx3-pcx) > 7 || Math.abs(cz3-pcz) > 7){
      removeMesh(c);
      toDelete.push(k);
    }
  });
  for (var di=0; di<toDelete.length; di++) chunks.delete(toDelete[di]);
}

/* ---------------- player ---------------- */
var player = { x:8, y:60, z:8, vx:0, vy:0, vz:0, onGround:false };
var yaw = 0, pitch = 0;
var HALF = 0.3, PH = 1.8, EYE = 1.62;

function collides(x,y,z){
  var eps = 1e-6;
  var x0 = Math.floor(x-HALF), x1 = Math.floor(x+HALF-eps);
  var y0 = Math.floor(y), y1 = Math.floor(y+PH-eps);
  var z0 = Math.floor(z-HALF), z1 = Math.floor(z+HALF-eps);
  for (var bx=x0; bx<=x1; bx++)
    for (var by=y0; by<=y1; by++)
      for (var bz=z0; bz<=z1; bz++)
        if (readBlock(bx,by,bz) !== 0) return true;
  return false;
}

function terrainTop(x,z){
  for (var y=HEIGHT-1; y>=0; y--) if (readBlock(x,y,z) !== 0) return y;
  return 0;
}

/* pre-generate spawn area */
for (var sx=-1; sx<=1; sx++)
  for (var sz=-1; sz<=1; sz++)
    chunks.set(key(sx,sz), {data: genChunk(sx,sz), mesh:null});
player.y = terrainTop(8,8) + 1;

/* ---------------- input ---------------- */
var keys = {};
var locked = false;
var overlay = document.getElementById("overlay");

overlay.addEventListener("click", function(){ canvas.requestPointerLock(); });
document.addEventListener("pointerlockchange", function(){
  locked = (document.pointerLockElement === canvas);
  overlay.style.display = locked ? "none" : "flex";
});
document.addEventListener("mousemove", function(e){
  if (!locked) return;
  yaw   -= e.movementX * 0.002;
  pitch -= e.movementY * 0.002;
  if (pitch > 1.55) pitch = 1.55;
  if (pitch < -1.55) pitch = -1.55;
});
document.addEventListener("keydown", function(e){
  keys[e.code] = true;
  if (e.code === "Space"){ e.preventDefault(); }
  if (e.key >= "1" && e.key <= "7") selectSlot(parseInt(e.key,10)-1);
});
document.addEventListener("keyup", function(e){ keys[e.code] = false; });
document.addEventListener("contextmenu", function(e){ e.preventDefault(); });
document.addEventListener("wheel", function(e){
  if (!locked) return;
  selectSlot((selected + (e.deltaY > 0 ? 1 : -1) + 7) % 7);
});

/* ---------------- hotbar ---------------- */
var selected = 0;
var hotbarEl = document.getElementById("hotbar");
var slotEls = [];
for (var hi=0; hi<7; hi++){
  var d = document.createElement("div");
  d.className = "slot";
  var hex = "#" + COLORS[HOTBAR_IDS[hi]].toString(16).padStart(6,"0");
  d.style.background = hex;
  var sp = document.createElement("span");
  sp.textContent = (hi+1);
  d.appendChild(sp);
  d.title = HOTBAR_NAMES[hi];
  hotbarEl.appendChild(d);
  slotEls.push(d);
}
function selectSlot(i){
  selected = i;
  for (var s=0; s<7; s++) slotEls[s].classList.toggle("sel", s===i);
}
selectSlot(0);

/* ---------------- raycast / break / place ---------------- */
var raycaster = new THREE.Raycaster();
raycaster.far = 6;
var center = new THREE.Vector2(0,0);
var targetBlock = null;   // {x,y,z} block being looked at
var placeCell = null;     // {x,y,z} cell for placement

function updateTarget(){
  targetBlock = null; placeCell = null; outline.visible = false;
  if (!locked) return;
  raycaster.setFromCamera(center, camera);
  var hits = raycaster.intersectObjects(chunkMeshes, false);
  if (hits.length === 0) return;
  var hit = hits[0];
  if (hit.distance > 6) return;
  var p = hit.point, n = hit.face.normal;
  var bx = Math.floor(p.x - n.x*0.5);
  var by = Math.floor(p.y - n.y*0.5);
  var bz = Math.floor(p.z - n.z*0.5);
  targetBlock = {x:bx, y:by, z:bz};
  placeCell = {
    x: Math.floor(p.x + n.x*0.5),
    y: Math.floor(p.y + n.y*0.5),
    z: Math.floor(p.z + n.z*0.5)
  };
  outline.position.set(bx+0.5, by+0.5, bz+0.5);
  outline.visible = true;
}

function overlapsPlayer(bx,by,bz){
  return bx < player.x+HALF && bx+1 > player.x-HALF &&
         by < player.y+PH   && by+1 > player.y &&
         bz < player.z+HALF && bz+1 > player.z-HALF;
}

document.addEventListener("mousedown", function(e){
  if (!locked) return;
  if (e.button === 0){
    if (targetBlock && targetBlock.y > 0){
      editBlock(targetBlock.x, targetBlock.y, targetBlock.z, 0);
    }
  } else if (e.button === 2){
    if (placeCell && readBlock(placeCell.x, placeCell.y, placeCell.z) === 0 &&
        !overlapsPlayer(placeCell.x, placeCell.y, placeCell.z)){
      editBlock(placeCell.x, placeCell.y, placeCell.z, HOTBAR_IDS[selected]);
    }
  }
});

/* ---------------- physics ---------------- */
function updatePlayer(dt){
  if (!locked) { player.vx = 0; player.vz = 0; }
  var speed = 5.5;
  var fwd = 0, str = 0;
  if (keys["KeyW"]) fwd += 1;
  if (keys["KeyS"]) fwd -= 1;
  if (keys["KeyD"]) str += 1;
  if (keys["KeyA"]) str -= 1;
  var sinY = Math.sin(yaw), cosY = Math.cos(yaw);
  // forward = (-sin yaw, 0, -cos yaw), right = (cos yaw, 0, -sin yaw)
  var wx = (-sinY*fwd + cosY*str);
  var wz = (-cosY*fwd - sinY*str);
  var wl = Math.sqrt(wx*wx + wz*wz);
  if (wl > 0){ wx = wx/wl*speed; wz = wz/wl*speed; }
  player.vx = wx; player.vz = wz;

  player.vy -= 25*dt;
  if (player.vy < -50) player.vy = -50;
  if (keys["Space"] && player.onGround){ player.vy = 8.5; player.onGround = false; }

  // X axis
  var nx = player.x + player.vx*dt;
  if (!collides(nx, player.y, player.z)) player.x = nx;

  // Y axis
  var ny = player.y + player.vy*dt;
  if (!collides(player.x, ny, player.z)){
    player.y = ny;
    player.onGround = false;
  } else {
    if (player.vy < 0) player.onGround = true;
    player.vy = 0;
  }

  // Z axis
  var nz = player.z + player.vz*dt;
  if (!collides(player.x, player.y, nz)) player.z = nz;

  if (player.y < -20){
    player.x = 8; player.z = 8;
    player.y = terrainTop(8,8) + 1;
    player.vy = 0;
  }

  camera.position.set(player.x, player.y + EYE, player.z);
  camera.rotation.set(pitch, yaw, 0);
}

/* ---------------- clouds & water ---------------- */
function updateWorld(dt){
  for (var i=0; i<clouds.length; i++){
    var c = clouds[i];
    c.position.x += (2 + (i%5)*0.6) * dt;
    var rx = c.position.x - player.x, rz = c.position.z - player.z;
    if (rx > 160) c.position.x -= 320;
    if (rx < -160) c.position.x += 320;
    if (rz > 160) c.position.z -= 320;
    if (rz < -160) c.position.z += 320;
  }
  water.position.x = player.x;
  water.position.z = player.z;
}

/* ---------------- resize ---------------- */
window.addEventListener("resize", function(){
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ---------------- main loop ---------------- */
var clock = new THREE.Clock();
function loop(){
  requestAnimationFrame(loop);
  var dt = Math.min(clock.getDelta(), 0.05);
  updatePlayer(dt);
  updateChunks();
  updateTarget();
  updateWorld(dt);
  renderer.render(scene, camera);
}
loop();

})();
</script>
</body>
</html>
```