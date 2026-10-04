```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>mc.html</title>
<style>
  html, body { margin:0; padding:0; overflow:hidden; width:100%; height:100%; background:#000; font-family:Arial,Helvetica,sans-serif; }
  canvas { display:block; }
  #crosshair { position:fixed; left:50%; top:50%; width:2px; height:22px; margin:-11px 0 0 -1px; background:#fff; pointer-events:none; z-index:10; box-shadow:0 0 2px #000; }
  #crosshair::after { content:""; position:absolute; left:-10px; top:10px; width:22px; height:2px; background:#fff; box-shadow:0 0 2px #000; }
  #hotbar { position:fixed; bottom:12px; left:50%; transform:translateX(-50%); display:flex; gap:4px; padding:6px; background:rgba(0,0,0,0.55); border-radius:6px; z-index:10; }
  .slot { width:44px; height:44px; border:2px solid rgba(255,255,255,0.25); border-radius:4px; position:relative; box-sizing:border-box; }
  .slot.sel { border-color:#fff; }
  .slot span { position:absolute; left:3px; top:1px; color:#fff; font-size:11px; text-shadow:1px 1px 1px #000; }
  #overlay { position:fixed; inset:0; background:rgba(0,0,0,0.65); color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:20; cursor:pointer; text-align:center; }
  #overlay h1 { font-size:48px; margin:0 0 18px; letter-spacing:2px; text-shadow:3px 3px 0 #333; }
  #overlay ul { list-style:none; padding:0; font-size:15px; line-height:1.7; margin-bottom:22px; }
  #overlay .play { font-size:22px; color:#ffe082; }
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
  <h1>MINECRAFT</h1>
  <ul>
    <li><b>WASD</b> — move, <b>Space</b> — jump</li>
    <li><b>Mouse</b> — look around</li>
    <li><b>Left click</b> — break block, <b>Right click</b> — place block</li>
    <li><b>1–7</b> or <b>mouse wheel</b> — select block</li>
  </ul>
  <div class="play">Click to play</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// ---------- constants ----------
var AIR=0, GRASS=1, DIRT=2, STONE=3, SAND=4, WOOD=5, LEAVES=6, SNOW=7;
var CHUNK=16, HEIGHT=80;
var GEN_R=5, MESH_R=4, UNLOAD_R=7;
var BLOCK_COLORS = {};
BLOCK_COLORS[GRASS]=0x4caf50; BLOCK_COLORS[DIRT]=0x795548; BLOCK_COLORS[STONE]=0x9e9e9e;
BLOCK_COLORS[SAND]=0xe7d9a8; BLOCK_COLORS[WOOD]=0x8d6e63; BLOCK_COLORS[LEAVES]=0x2e7d32;
BLOCK_COLORS[SNOW]=0xffffff;
var HOTBAR_IDS=[GRASS,DIRT,STONE,SAND,WOOD,LEAVES,SNOW];

// precompute rgb per block
var RGB={};
for(var id in BLOCK_COLORS){
  var c=BLOCK_COLORS[id];
  RGB[id]=[(c>>16&255)/255,(c>>8&255)/255,(c&255)/255];
}

// ---------- faces ----------
// corners relative to block origin, triangles (0,1,2) & (0,2,3)
var FACES=[
  { n:[0,1,0],  c:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]], light:1.0 },   // top
  { n:[0,-1,0], c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]], light:0.55 },  // bottom
  { n:[1,0,0],  c:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]], light:0.8 },   // +x
  { n:[-1,0,0], c:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]], light:0.8 },   // -x
  { n:[0,0,1],  c:[[1,0,1],[1,1,1],[0,1,1],[0,0,1]], light:0.8 },   // +z
  { n:[0,0,-1], c:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]], light:0.8 }    // -z
];

// ---------- noise ----------
function hash(x,y,z){
  var h=(x*374761393 + y*668265263 + z*1274126177)|0;
  h=(h ^ (h>>>13))|0;
  h=(h*1274126177)|0;
  h=(h ^ (h>>>16))>>>0;
  return h/4294967296;
}
function smooth(t){ return t*t*(3-2*t); }
function noise2(x,z){
  var ix=Math.floor(x), iz=Math.floor(z);
  var fx=x-ix, fz=z-iz;
  var sx=smooth(fx), sz=smooth(fz);
  var a=hash(ix,0,iz), b=hash(ix+1,0,iz), c=hash(ix,0,iz+1), d=hash(ix+1,0,iz+1);
  return a+(b-a)*sx+(c-a)*sz+(a-b-c+d)*sx*sz;
}
function noise3(x,y,z){
  var ix=Math.floor(x), iy=Math.floor(y), iz=Math.floor(z);
  var fx=x-ix, fy=y-iy, fz=z-iz;
  var sx=smooth(fx), sy=smooth(fy), sz=smooth(fz);
  function lerp(t,a,b){ return a+(b-a)*t; }
  var n00=lerp(sz,hash(ix,iy,iz),hash(ix,iy,iz+1));
  var n10=lerp(sz,hash(ix+1,iy,iz),hash(ix+1,iy,iz+1));
  var n01=lerp(sz,hash(ix,iy+1,iz),hash(ix,iy+1,iz+1));
  var n11=lerp(sz,hash(ix+1,iy+1,iz),hash(ix+1,iy+1,iz+1));
  var n0=lerp(sy,n00,n01), n1=lerp(sy,n10,n11);
  return lerp(sx,n0,n1);
}
function fbm2(x,z){
  var sum=0, amp=0.5, f=1;
  for(var i=0;i<4;i++){ sum+=noise2(x*f,z*f)*amp; amp*=0.5; f*=2; }
  return sum/0.9375;
}
function heightAt(wx,wz){
  var m=fbm2(wx*0.004,wz*0.004);
  var h=fbm2(wx*0.02,wz*0.02);
  var H=Math.floor(5 + m*m*58 + h*10);
  if(H<1)H=1; if(H>HEIGHT-2)H=HEIGHT-2;
  return H;
}

// ---------- chunks ----------
var CHUNKS=new Map();   // "cx,cz" -> { data:Uint8Array, mesh:Mesh|null }
var meshes=[];          // global array of chunk meshes for raycasting

function ckey(cx,cz){ return cx+","+cz; }
function idx(lx,lz,y){ return lx + lz*16 + y*256; }

function readBlock(x,y,z){
  if(y<0||y>=HEIGHT) return AIR;
  var cx=Math.floor(x/16), cz=Math.floor(z/16);
  var e=CHUNKS.get(ckey(cx,cz));
  if(!e) return AIR;
  return e.data[idx(x-cx*16, z-cz*16, y)];
}
function writeBlock(x,y,z,id){
  if(y<0||y>=HEIGHT) return false;
  var cx=Math.floor(x/16), cz=Math.floor(z/16);
  var e=CHUNKS.get(ckey(cx,cz));
  if(!e) return false;
  e.data[idx(x-cx*16, z-cz*16, y)]=id;
  return true;
}

function genChunk(cx,cz){
  var data=new Uint8Array(16*16*HEIGHT);
  for(var lx=0;lx<16;lx++){
    for(var lz=0;lz<16;lz++){
      var wx=cx*16+lx, wz=cz*16+lz;
      var H=heightAt(wx,wz);
      for(var y=0;y<=H;y++){
        var id;
        if(y===0) id=STONE;
        else if(y<H-3) id=STONE;
        else if(y<H) id = (H<=16)?SAND:((H>=37)?STONE:DIRT);
        else id = (H>=46)?SNOW:((H>=37)?STONE:((H<=16)?SAND:GRASS));
        if(id!==AIR && y>=3 && y<=H-2 && noise3(wx*0.09,y*0.09,wz*0.09)>0.67) id=AIR;
        data[idx(lx,lz,y)]=id;
      }
      // trees on grass columns
      if(H>16 && H<37 && hash(wx,987,wz)<0.02 && lx>=2 && lx<=13 && lz>=2 && lz<=13){
        for(var t=1;t<=4;t++){ data[idx(lx,lz,H+t)]=WOOD; }
        function leaf(dx,dy,dz){
          var nx=lx+dx, nz=lz+dz, ny=H+dy;
          if(nx<0||nx>15||nz<0||nz>15||ny<0||ny>=HEIGHT) return;
          if(data[idx(nx,nz,ny)]===AIR) data[idx(nx,nz,ny)]=LEAVES;
        }
        for(var dy=2;dy<=3;dy++)
          for(var dx=-2;dx<=2;dx++) for(var dz=-2;dz<=2;dz++) leaf(dx,dy,dz);
        for(var dx2=-1;dx2<=1;dx2++) for(var dz2=-1;dz2<=1;dz2++) leaf(dx2,4,dz2);
        leaf(0,5,0);
      }
    }
  }
  return data;
}

// ---------- meshing ----------
var blockMaterial = new THREE.MeshLambertMaterial({ vertexColors:true });

function buildChunkGeometry(data,cx,cz){
  var positions=[], normals=[], colors=[];
  for(var y=0;y<HEIGHT;y++){
    for(var lz=0;lz<16;lz++){
      for(var lx=0;lx<16;lx++){
        var id=data[idx(lx,lz,y)];
        if(id===AIR) continue;
        var wx=cx*16+lx, wz=cz*16+lz;
        var rgb=RGB[id];
        for(var fi=0;fi<6;fi++){
          var f=FACES[fi];
          if(readBlock(wx+f.n[0], y+f.n[1], wz+f.n[2])!==AIR) continue;
          var l=f.light;
          var tri=[0,1,2,0,2,3];
          for(var k=0;k<6;k++){
            var c=f.c[tri[k]];
            positions.push(wx+c[0], y+c[1], wz+c[2]);
            normals.push(f.n[0], f.n[1], f.n[2]);
            colors.push(rgb[0]*l, rgb[1]*l, rgb[2]*l);
          }
        }
      }
    }
  }
  var geo=new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute("normal", new THREE.Float32BufferAttribute(normals,3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(colors,3));
  return geo;
}

function makeChunkMesh(cx,cz){
  var e=CHUNKS.get(ckey(cx,cz));
  if(!e || e.mesh) return;
  var geo=buildChunkGeometry(e.data,cx,cz);
  var mesh=new THREE.Mesh(geo, blockMaterial);
  mesh.position.set(0,0,0);
  mesh.userData={cx:cx,cz:cz};
  e.mesh=mesh;
  meshes.push(mesh);
  scene.add(mesh);
}

function removeChunkMesh(cx,cz){
  var e=CHUNKS.get(ckey(cx,cz));
  if(!e || !e.mesh) return;
  var i=meshes.indexOf(e.mesh);
  if(i>=0) meshes.splice(i,1);
  scene.remove(e.mesh);
  e.mesh.geometry.dispose();
  e.mesh=null;
}

function rebuildChunk(cx,cz){
  var e=CHUNKS.get(ckey(cx,cz));
  if(!e || !e.mesh) return;   // data updated; mesh will be built later
  removeChunkMesh(cx,cz);
  makeChunkMesh(cx,cz);
}

function editBlock(x,y,z,id){
  if(!writeBlock(x,y,z,id)) return;
  var cx=Math.floor(x/16), cz=Math.floor(z/16);
  rebuildChunk(cx,cz);
  var lx=x-cx*16, lz=z-cz*16;
  if(lx===0) rebuildChunk(cx-1,cz);
  if(lx===15) rebuildChunk(cx+1,cz);
  if(lz===0) rebuildChunk(cx,cz-1);
  if(lz===15) rebuildChunk(cx,cz+1);
}

// ---------- scene ----------
var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb, 40, 110);

var camera=new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 400);
camera.rotation.order="YXZ";

var renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x87ceeb);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));
var sun=new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(60,120,40);
scene.add(sun);

// water plane (visual only)
var waterMat=new THREE.MeshLambertMaterial({color:0x3f86d1, transparent:true, opacity:0.55});
var waterGeo=new THREE.PlaneGeometry(700,700);
waterGeo.rotateX(-Math.PI/2);
var water=new THREE.Mesh(waterGeo, waterMat);
water.position.y=14.3;
scene.add(water);

// clouds
var clouds=[];
var cloudMat=new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.75});
for(var ci=0;ci<25;ci++){
  var w=18+hash(ci*131,7,3)*30;
  var d=14+hash(ci*131,11,5)*26;
  var g=new THREE.BoxGeometry(w,2.5,d);
  var m=new THREE.Mesh(g, cloudMat);
  m.position.set(hash(ci,1,2)*700-350, 88+hash(ci,3,4)*6, hash(ci,5,6)*700-350);
  m.userData.speed=1.5+hash(ci,9,9)*2;
  clouds.push(m);
  scene.add(m);
}

// block outline
var outlineGeo=new THREE.EdgesGeometry(new THREE.BoxGeometry(1.005,1.005,1.005));
var outline=new THREE.LineSegments(outlineGeo, new THREE.LineBasicMaterial({color:0x000000}));
outline.visible=false;
scene.add(outline);

// ---------- player ----------
var HW=0.3, PH=1.8, EYE=1.62;
var spawn={x:8.5, z:8.5, y:heightAt(8,8)+1};
var player={
  x:spawn.x, y:spawn.y, z:spawn.z,
  vy:0, onGround:false, yaw:0, pitch:0
};
var keys={};
var locked=false;
var selected=0;

function solidAt(x,y,z){ return readBlock(x,y,z)!==AIR; }

function playerCollides(px,py,pz){
  var x0=Math.floor(px-HW+1e-4), x1=Math.floor(px+HW-1e-4);
  var y0=Math.floor(py+1e-4), y1=Math.floor(py+PH-1e-4);
  var z0=Math.floor(pz-HW+1e-4), z1=Math.floor(pz+HW-1e-4);
  for(var bx=x0;bx<=x1;bx++)
    for(var by=y0;by<=y1;by++)
      for(var bz=z0;bz<=z1;bz++)
        if(solidAt(bx,by,bz)) return true;
  return false;
}

function aabbOverlapsCell(px,py,pz,bx,by,bz){
  return px-HW < bx+1 && px+HW > bx &&
         py < by+1 && py+PH > by &&
         pz-HW < bz+1 && pz+HW > bz;
}

function moveAxis(axis, amount){
  if(amount===0) return;
  var steps=Math.max(1, Math.ceil(Math.abs(amount)/0.2));
  var inc=amount/steps;
  for(var s=0;s<steps;s++){
    var ox=player.x, oy=player.y, oz=player.z;
    if(axis===0) player.x+=inc;
    else if(axis===1) player.y+=inc;
    else player.z+=inc;
    if(playerCollides(player.x, player.y, player.z)){
      player.x=ox; player.y=oy; player.z=oz;
      if(axis===1){
        if(player.vy<0){ player.onGround=true; }
        player.vy=0;
      }
      return;
    }
  }
}

// ---------- controls ----------
var overlay=document.getElementById("overlay");
var canvasEl=renderer.domElement;

overlay.addEventListener("click", function(){
  canvasEl.requestPointerLock();
});
document.addEventListener("pointerlockchange", function(){
  locked = (document.pointerLockElement===canvasEl);
  overlay.style.display = locked ? "none" : "flex";
});
document.addEventListener("mousemove", function(e){
  if(!locked) return;
  player.yaw -= e.movementX*0.002;
  player.pitch -= e.movementY*0.002;
  if(player.pitch>1.55) player.pitch=1.55;
  if(player.pitch<-1.55) player.pitch=-1.55;
});
document.addEventListener("keydown", function(e){
  keys[e.code]=true;
  if(e.code>="Digit1" && e.code<="Digit7"){
    selected = parseInt(e.code.charAt(5),10)-1;
    updateHotbar();
  }
  if(e.code==="Space") e.preventDefault();
});
document.addEventListener("keyup", function(e){ keys[e.code]=false; });
window.addEventListener("wheel", function(e){
  selected=(selected + (e.deltaY>0?1:-1) + HOTBAR_IDS.length) % HOTBAR_IDS.length;
  updateHotbar();
}, {passive:true});
document.addEventListener("contextmenu", function(e){ e.preventDefault(); });

var raycaster=new THREE.Raycaster();
raycaster.far=6;
var currentHit=null;

document.addEventListener("mousedown", function(e){
  if(!locked) return;
  if(!currentHit) return;
  var p=currentHit.point, n=currentHit.face.normal;
  if(e.button===0){
    var bx=Math.floor(p.x - n.x*0.5);
    var by=Math.floor(p.y - n.y*0.5);
    var bz=Math.floor(p.z - n.z*0.5);
    if(by>0) editBlock(bx,by,bz,AIR);
  } else if(e.button===2){
    var px2=Math.floor(p.x + n.x*0.5);
    var py2=Math.floor(p.y + n.y*0.5);
    var pz2=Math.floor(p.z + n.z*0.5);
    if(readBlock(px2,py2,pz2)===AIR && !aabbOverlapsCell(player.x,player.y,player.z,px2,py2,pz2)){
      editBlock(px2,py2,pz2,HOTBAR_IDS[selected]);
    }
  }
});

// ---------- hotbar UI ----------
var hotbar=document.getElementById("hotbar");
var slotEls=[];
(function(){
  for(var i=0;i<HOTBAR_IDS.length;i++){
    var d=document.createElement("div");
    d.className="slot";
    d.style.background="#"+("000000"+BLOCK_COLORS[HOTBAR_IDS[i]].toString(16)).slice(-6);
    var s=document.createElement("span");
    s.textContent=(i+1);
    d.appendChild(s);
    hotbar.appendChild(d);
    slotEls.push(d);
  }
})();
function updateHotbar(){
  for(var i=0;i<slotEls.length;i++){
    slotEls[i].className = "slot" + (i===selected?" sel":"");
  }
}
updateHotbar();

// ---------- resize ----------
window.addEventListener("resize", function(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- chunk management per frame ----------
function manageChunks(){
  var pcx=Math.floor(player.x/16), pcz=Math.floor(player.z/16);

  // generate data (max 4 per frame)
  var genCount=0;
  for(var dx=-GEN_R; dx<=GEN_R && genCount<4; dx++){
    for(var dz=-GEN_R; dz<=GEN_R && genCount<4; dz++){
      var cx=pcx+dx, cz=pcz+dz, k=ckey(cx,cz);
      if(!CHUNKS.has(k)){
        CHUNKS.set(k, {data:genChunk(cx,cz), mesh:null});
        genCount++;
      }
    }
  }

  // build meshes (max 2 per frame) for chunks whose 4 neighbors have data
  var meshCount=0;
  for(var dx2=-MESH_R; dx2<=MESH_R && meshCount<2; dx2++){
    for(var dz2=-MESH_R; dz2<=MESH_R && meshCount<2; dz2++){
      var cx2=pcx+dx2, cz2=pcz+dz2;
      var e=CHUNKS.get(ckey(cx2,cz2));
      if(!e || e.mesh) continue;
      var n1=CHUNKS.get(ckey(cx2-1,cz2)), n2=CHUNKS.get(ckey(cx2+1,cz2));
      var n3=CHUNKS.get(ckey(cx2,cz2-1)), n4=CHUNKS.get(ckey(cx2,cz2+1));
      if(n1&&n2&&n3&&n4){ makeChunkMesh(cx2,cz2); meshCount++; }
    }
  }

  // unload far chunks
  var toDelete=[];
  CHUNKS.forEach(function(e,k){
    var parts=k.split(",");
    var cx3=parseInt(parts[0],10), cz3=parseInt(parts[1],10);
    if(Math.abs(cx3-pcx)>UNLOAD_R || Math.abs(cz3-pcz)>UNLOAD_R){
      removeChunkMesh(cx3,cz3);
      toDelete.push(k);
    }
  });
  for(var i=0;i<toDelete.length;i++) CHUNKS.delete(toDelete[i]);
}

// ---------- main loop ----------
var lastTime=performance.now();

function step(){
  requestAnimationFrame(step);
  var now=performance.now();
  var dt=(now-lastTime)/1000;
  lastTime=now;
  if(dt>0.05) dt=0.05;

  manageChunks();

  // movement
  if(locked){
    var speed=5.5;
    var fwdX=-Math.sin(player.yaw), fwdZ=-Math.cos(player.yaw);
    var rightX=Math.cos(player.yaw), rightZ=-Math.sin(player.yaw);
    var mx=0, mz=0;
    if(keys["KeyW"]){ mx+=fwdX; mz+=fwdZ; }
    if(keys["KeyS"]){ mx-=fwdX; mz-=fwdZ; }
    if(keys["KeyD"]){ mx+=rightX; mz+=rightZ; }
    if(keys["KeyA"]){ mx-=rightX; mz-=rightZ; }
    var len=Math.sqrt(mx*mx+mz*mz);
    if(len>0){ mx=mx/len*speed*dt; mz=mz/len*speed*dt; }
    moveAxis(0,mx);
    moveAxis(2,mz);
    if(keys["Space"] && player.onGround){ player.vy=8.5; player.onGround=false; }
    player.vy-=25*dt;
    if(player.vy<-30) player.vy=-30;
    if(player.vy>0) player.onGround=false;
    moveAxis(1, player.vy*dt);
  }

  // fell out of world
  if(player.y<-20){
    player.x=spawn.x; player.y=spawn.y; player.z=spawn.z;
    player.vy=0; player.onGround=false;
  }

  // camera
  camera.position.set(player.x, player.y+EYE, player.z);
  camera.rotation.set(player.pitch, player.yaw, 0);

  // raycast targeting
  raycaster.setFromCamera({x:0,y:0}, camera);
  var hits=raycaster.intersectObjects(meshes);
  currentHit = (hits.length>0) ? hits[0] : null;
  if(currentHit && locked){
    outline.visible=true;
    var p=currentHit.point, n=currentHit.face.normal;
    var bx=Math.floor(p.x-n.x*0.5), by=Math.floor(p.y-n.y*0.5), bz=Math.floor(p.z-n.z*0.5);
    outline.position.set(bx+0.5, by+0.5, bz+0.5);
  } else {
    outline.visible=false;
  }

  // clouds drift & wrap around player
  for(var ci=0;ci<clouds.length;ci++){
    var cld=clouds[ci];
    cld.position.x += cld.userData.speed*dt;
    if(cld.position.x > player.x+350) cld.position.x -= 700;
    if(cld.position.z > player.z+350) cld.position.z -= 700;
    if(cld.position.z < player.z-350) cld.position.z += 700;
  }

  // water follows the player
  water.position.set(player.x, 14.3, player.z);

  renderer.render(scene, camera);
}

// pre-generate initial chunks around spawn so the world is ready
manageChunks();
step();

})();
</script>
</body>
</html>
```