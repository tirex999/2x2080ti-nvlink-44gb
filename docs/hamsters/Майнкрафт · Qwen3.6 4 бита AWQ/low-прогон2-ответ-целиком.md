

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>mc.html</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000;font-family:monospace}
canvas{display:block}
#overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.75);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;cursor:pointer;z-index:100;text-align:center;line-height:1.8}
#overlay h1{font-size:48px;margin-bottom:20px;text-shadow:2px 2px 4px #000}
#overlay p{font-size:16px;margin:4px 0}
#overlay.hidden{display:none}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);color:#fff;font-size:28px;font-weight:bold;pointer-events:none;text-shadow:0 0 3px #000;z-index:50}
#hotbar{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);display:flex;gap:3px;background:rgba(0,0,0,0.6);padding:5px;border-radius:4px;z-index:50}
.slot{width:46px;height:46px;border:2px solid rgba(255,255,255,0.25);display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;text-shadow:1px 1px 2px #000;border-radius:2px}
.slot.selected{border-color:#fff;border-width:3px}
</style>
</head>
<body>
<div id="overlay">
<h1>mc.html</h1>
<p>WASD &mdash; Move | Space &mdash; Jump</p>
<p>Left Click &mdash; Break Block</p>
<p>Right Click &mdash; Place Block</p>
<p>1&ndash;7 / Mouse Wheel &mdash; Select Block</p>
<br><p>Click to play</p>
</div>
<div id="crosshair">+</div>
<div id="hotbar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
"use strict";

/* ── constants ─────────────────────────────────────── */
var CHUNK_W = 16, CHUNK_H = 80, CHUNK_AREA = CHUNK_W * CHUNK_W;
var AIR=0,GRASS=1,DIRT=2,STONE=3,SAND=4,WOOD=5,LEAVES=6,SNOW=7;
var BLOCK_COLORS = [
  [0,0,0],
  [76/255,175/255,80/255],
  [121/255,85/255,72/255],
  [158/255,158/255,158/255],
  [231/255,217/255,168/255],
  [141/255,110/255,99/255],
  [46/255,125/255,50/255],
  [1,1,1]
];
var HOTBAR_BLOCKS = [GRASS,DIRT,STONE,SAND,WOOD,LEAVES,SNOW];
var PLAYER_HW = 0.3, PLAYER_H = 1.8, PLAYER_EYE = 1.62;
var GRAVITY = 25, JUMP_VEL = 8.5, MOVE_SPEED = 5.5;
var REACH = 6;

/* ── globals ───────────────────────────────────────── */
var scene, camera, renderer, canvasEl;
var chunks = new Map();
var chunkMeshes = [];
var sharedMat;
var player = {x:0,y:0,z:0,vx:0,vy:0,vz:0,yaw:0,pitch:0,onGround:false};
var keys = {};
var hotbarIdx = 0;
var lastHit = null;
var selBox;
var cloudArr = [];
var waterPlane;
var overlayEl;
var spawnX, spawnY, spawnZ;

/* ── noise ─────────────────────────────────────────── */
function hash2(x, y) {
  var h = Math.imul(x|0, 374761393) ^ Math.imul(y|0, 668265263);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) & 0x7fffffff) / 0x7fffffff;
}
function hash3(x, y, z) {
  var h = Math.imul(x|0, 374761393) ^ Math.imul(y|0, 668265263) ^ Math.imul(z|0, 2140136427);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) & 0x7fffffff) / 0x7fffffff;
}
function ss(t){ return t*t*(3-2*t); }
function lerp(a,b,t){ return a+(b-a)*t; }

function noise2d(x, y) {
  var ix=Math.floor(x), iy=Math.floor(y), fx=x-ix, fy=y-iy;
  var sx=ss(fx), sy=ss(fy);
  var n00=hash2(ix,iy), n10=hash2(ix+1,iy), n01=hash2(ix,iy+1), n11=hash2(ix+1,iy+1);
  return lerp(lerp(n00,n10,sx), lerp(n01,n11,sx), sy);
}
function noise3d(x, y, z) {
  var ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
  var fx=x-ix,fy=y-iy,fz=z-iz;
  var sx=ss(fx),sy=ss(fy),sz=ss(fz);
  var n000=hash3(ix,iy,iz),n100=hash3(ix+1,iy,iz),n010=hash3(ix,iy+1,iz),n110=hash3(ix+1,iy+1,iz);
  var n001=hash3(ix,iy,iz+1),n101=hash3(ix+1,iy,iz+1),n011=hash3(ix,iy+1,iz+1),n111=hash3(ix+1,iy+1,iz+1);
  var nx00=lerp(n000,n100,sx),nx10=lerp(n010,n110,sx),nx01=lerp(n001,n101,sx),nx11=lerp(n011,n111,sx);
  return lerp(lerp(nx00,nx10,sy),lerp(nx01,nx11,sy),sz);
}
function fbm2d(x,y,oct){
  var t=0,a=1,f=1,m=0;
  for(var i=0;i<oct;i++){t+=noise2d(x*f,y*f)*a;m+=a;a*=0.5;f*=2;}
  return t/m;
}
function fbm3d(x,y,z,oct){
  var t=0,a=1,f=1,m=0;
  for(var i=0;i<oct;i++){t+=noise3d(x*f,y*f,z*f)*a;m+=a;a*=0.5;f*=2;}
  return t/m;
}

/* ── chunk helpers ─────────────────────────────────── */
function ck(cx,cz){return cx+","+cz;}

function getBlock(wx,wy,wz){
  if(wy<0||wy>=CHUNK_H)return 0;
  var cx=Math.floor(wx/CHUNK_W),cz=Math.floor(wz/CHUNK_W);
  var ch=chunks.get(ck(cx,cz));
  if(!ch)return 0;
  var lx=((wx%CHUNK_W)+CHUNK_W)%CHUNK_W,lz=((wz%CHUNK_W)+CHUNK_W)%CHUNK_W;
  return ch.data[wy*CHUNK_AREA+lz*CHUNK_W+lx];
}

function setBlock(wx,wy,wz,id){
  if(wy<0||wy>=CHUNK_H)return;
  var cx=Math.floor(wx/CHUNK_W),cz=Math.floor(wz/CHUNK_W);
  var ch=chunks.get(ck(cx,cz));
  if(!ch)return;
  var lx=((wx%CHUNK_W)+CHUNK_W)%CHUNK_W,lz=((wz%CHUNK_W)+CHUNK_W)%CHUNK_W;
  ch.data[wy*CHUNK_AREA+lz*CHUNK_W+lx]=id;
}

function terrainH(wx,wz){
  var m=fbm2d(wx*0.004,wz*0.004,4);
  var h=fbm2d(wx*0.02,wz*0.02,4);
  return Math.floor(5+m*m*58+h*10);
}

/* ── chunk generation ──────────────────────────────── */
function genChunkData(cx,cz){
  var data=new Uint8Array(CHUNK_W*CHUNK_W*CHUNK_H);
  for(var lx=0;lx<CHUNK_W;lx++){
    for(var lz=0;lz<CHUNK_W;lz++){
      var wx=cx*CHUNK_W+lx, wz=cz*CHUNK_W+lz;
      var m=fbm2d(wx*0.004,wz*0.004,4);
      var h=fbm2d(wx*0.02,wz*0.02,4);
      var H=Math.floor(5+m*m*58+h*10);
      for(var y=0;y<CHUNK_H;y++){
        var bl=0;
        if(y===0){bl=STONE;}
        else if(y<H){
          if(y<H-3){bl=STONE;}
          else{
            if(H<=16)bl=SAND;
            else if(H>=37)bl=STONE;
            else bl=DIRT;
          }
        }
        else if(y===H){
          if(H>=46)bl=SNOW;
          else if(H>=37)bl=STONE;
          else if(H<=16)bl=SAND;
          else bl=GRASS;
        }
        if(y>=3&&y<=H-2&&bl!==0){
          var cv=fbm3d(wx*0.09,y*0.09,wz*0.09,3);
          if(cv>0.67)bl=0;
        }
        data[y*CHUNK_AREA+lz*CHUNK_W+lx]=bl;
      }
      /* trees */
      if(data[H*CHUNK_AREA+lz*CHUNK_W+lx]===GRASS&&lx>=2&&lx<=13&&lz>=2&&lz<=13&&H+8<CHUNK_H){
        var th=hash2(wx*7+13,wz*13+7);
        if(th<0.02){
          for(var ty=H+1;ty<=H+4;ty++) data[ty*CHUNK_AREA+lz*CHUNK_W+lx]=WOOD;
          var layers=[{y:H+5,s:5},{y:H+6,s:5},{y:H+7,s:3},{y:H+8,s:1}];
          for(var li=0;li<layers.length;li++){
            var half=Math.floor(layers[li].s/2);
            for(var dx=-half;dx<=half;dx++){
              for(var dz=-half;dz<=half;dz++){
                var nx=lx+dx,nz=lz+dz;
                if(nx>=0&&nx<CHUNK_W&&nz>=0&&nz<CHUNK_W){
                  var idx=layers[li].y*CHUNK_AREA+nz*CHUNK_W+nx;
                  if(data[idx]===0)data[idx]=LEAVES;
                }
              }
            }
          }
        }
      }
    }
  }
  return data;
}

/* ── mesh building ─────────────────────────────────── */
function addFace(pos,nrm,col,wx,wy,wz,nx,ny,nz,color,light){
  var c;
  if(ny===1)c=[[wx,wy+1,wz+1],[wx+1,wy+1,wz+1],[wx+1,wy+1,wz],[wx,wy+1,wz]];
  else if(ny===-1)c=[[wx,wy,wz],[wx+1,wy,wz],[wx+1,wy,wz+1],[wx,wy,wz+1]];
  else if(nz===-1)c=[[wx,wy+1,wz],[wx+1,wy+1,wz],[wx+1,wy,wz],[wx,wy,wz]];
  else if(nz===1)c=[[wx+1,wy,wz+1],[wx+1,wy+1,wz+1],[wx,wy+1,wz+1],[wx,wy,wz+1]];
  else if(nx===-1)c=[[wx,wy+1,wz],[wx,wy+1,wz+1],[wx,wy,wz+1],[wx,wy,wz]];
  else c=[[wx+1,wy,wz+1],[wx+1,wy+1,wz+1],[wx+1,wy+1,wz],[wx+1,wy,wz]];
  var tris=[[c[0],c[1],c[2]],[c[0],c[2],c[3]]];
  var cr=color[0]*light,cg=color[1]*light,cb=color[2]*light;
  for(var ti=0;ti<2;ti++){
    for(var vi=0;vi<3;vi++){
      pos.push(tris[ti][vi][0],tris[ti][vi][1],tris[ti][vi][2]);
      nrm.push(nx,ny,nz);
      col.push(cr,cg,cb);
    }
  }
}

function buildMesh(cx,cz,data){
  var pos=[],nrm=[],col=[];
  for(var y=0;y<CHUNK_H;y++){
    for(var z=0;z<CHUNK_W;z++){
      for(var x=0;x<CHUNK_W;x++){
        var bid=data[y*CHUNK_AREA+z*CHUNK_W+x];
        if(bid===0)continue;
        var wx=cx*CHUNK_W+x,wz=cz*CHUNK_W+z;
        var clr=BLOCK_COLORS[bid];
        function gn(nx,ny,nz){
          var lx=nx-cx*CHUNK_W,lz=nz-cz*CHUNK_W;
          if(lx>=0&&lx<CHUNK_W&&lz>=0&&lz<CHUNK_W&&ny>=0&&ny<CHUNK_H)
            return data[ny*CHUNK_AREA+lz*CHUNK_W+lx];
          return getBlock(nx,ny,nz);
        }
        if(gn(wx,y+1,wz)===0)addFace(pos,nrm,col,wx,y,wz,0,1,0,clr,1.0);
        if(gn(wx,y-1,wz)===0)addFace(pos,nrm,col,wx,y,wz,0,-1,0,clr,0.55);
        if(gn(wx,y,wz-1)===0)addFace(pos,nrm,col,wx,y,wz,0,0,-1,clr,0.8);
        if(gn(wx,y,wz+1)===0)addFace(pos,nrm,col,wx,y,wz,0,0,1,clr,0.8);
        if(gn(wx-1,y,wz)===0)addFace(pos,nrm,col,wx,y,wz,-1,0,0,clr,0.8);
        if(gn(wx+1,y,wz)===0)addFace(pos,nrm,col,wx,y,wz,1,0,0,clr,0.8);
      }
    }
  }
  if(pos.length===0)return null;
  var geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(nrm,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  return new THREE.Mesh(geo,sharedMat);
}

function rebuildChunk(cx,cz){
  var key=ck(cx,cz);
  var ch=chunks.get(key);
  if(!ch)return;
  if(ch.mesh){
    scene.remove(ch.mesh);
    ch.mesh.geometry.dispose();
    var idx=chunkMeshes.indexOf(ch.mesh);
    if(idx>=0)chunkMeshes.splice(idx,1);
  }
  ch.mesh=buildMesh(cx,cz,ch.data);
  if(ch.mesh){scene.add(ch.mesh);chunkMeshes.push(ch.mesh);}
}

function rebuildChunkAt(wx,wy,wz){
  var cx=Math.floor(wx/CHUNK_W),cz=Math.floor(wz/CHUNK_W);
  rebuildChunk(cx,cz);
  var lx=((wx%CHUNK_W)+CHUNK_W)%CHUNK_W,lz=((wz%CHUNK_W)+CHUNK_W)%CHUNK_W;
  if(lx===0)rebuildChunk(cx-1,cz);
  if(lx===15)rebuildChunk(cx+1,cz);
  if(lz===0)rebuildChunk(cx,cz-1);
  if(lz===15)rebuildChunk(cx,cz+1);
}

/* ── collision ─────────────────────────────────────── */
function collide(px,py,pz){
  var minX=Math.floor(px-PLAYER_HW),maxX=Math.floor(px+PLAYER_HW);
  var minY=Math.floor(py-0.0001),maxY=Math.floor(py+PLAYER_H-0.0001);
  var minZ=Math.floor(pz-PLAYER_HW),maxZ=Math.floor(pz+PLAYER_HW);
  for(var x=minX;x<=maxX;x++){
    for(var y=minY;y<=maxY;y++){
      for(var z=minZ;z<=maxZ;z++){
        if(x+1>px-PLAYER_HW&&x<px+PLAYER_HW&&
           y+1>py&&y<py+PLAYER_H&&
           z+1>pz-PLAYER_HW&&z<pz+PLAYER_HW){
          if(getBlock(x,y,z)!==0)return true;
        }
      }
    }
  }
  return false;
}

/* ── physics ───────────────────────────────────────── */
function updatePhysics(dt){
  var mx=0,mz=0;
  if(keys['w']){mx-=Math.sin(player.yaw);mz-=Math.cos(player.yaw);}
  if(keys['s']){mx+=Math.sin(player.yaw);mz+=Math.cos(player.yaw);}
  if(keys['a']){mx-=Math.cos(player.yaw);mz+=Math.sin(player.yaw);}
  if(keys['d']){mx+=Math.cos(player.yaw);mz-=Math.sin(player.yaw);}
  var len=Math.sqrt(mx*mx+mz*mz);
  if(len>0){mx=mx/len*MOVE_SPEED;mz=mz/len*MOVE_SPEED;}
  player.vx=mx;player.vz=mz;
  player.vy-=GRAVITY*dt;
  if(keys[' ']&&player.onGround){player.vy=JUMP_VEL;player.onGround=false;}
  /* X */
  player.x+=player.vx*dt;
  if(collide(player.x,player.y,player.z)){player.x-=player.vx*dt;player.vx=0;}
  /* Y */
  player.y+=player.vy*dt;
  player.onGround=false;
  if(collide(player.x,player.y,player.z)){
    player.y-=player.vy*dt;
    if(player.vy<0)player.onGround=true;
    player.vy=0;
  }
  /* Z */
  player.z+=player.vz*dt;
  if(collide(player.x,player.y,player.z)){player.z-=player.vz*dt;player.vz=0;}
  if(player.y<-20){player.x=spawnX;player.y=spawnY;player.z=spawnZ;player.vx=player.vy=player.vz=0;}
}

/* ── raycasting ────────────────────────────────────── */
var raycaster=new THREE.Raycaster();
raycaster.far=REACH;

function updateSelection(){
  raycaster.setFromCamera(new THREE.Vector2(0,0),camera);
  var hits=raycaster.intersectObjects(chunkMeshes);
  if(hits.length>0){
    var hit=hits[0];
    var p=hit.point,n=hit.face.normal;
    var bx=Math.floor(p.x-n.x*0.5),by=Math.floor(p.y-n.y*0.5),bz=Math.floor(p.z-n.z*0.5);
    selBox.position.set(bx+0.5,by+0.5,bz+0.5);
    selBox.visible=true;
    lastHit={bx:bx,by:by,bz:bz,
      px:Math.floor(p.x+n.x*0.5),py:Math.floor(p.y+n.y*0.5),pz:Math.floor(p.z+n.z*0.5)};
  }else{
    selBox.visible=false;
    lastHit=null;
  }
}

function breakBlock(){
  if(!lastHit||document.pointerLockElement!==canvasEl)return;
  if(lastHit.by===0)return;
  if(getBlock(lastHit.bx,lastHit.by,lastHit.bz)===0)return;
  setBlock(lastHit.bx,lastHit.by,lastHit.bz,0);
  rebuildChunkAt(lastHit.bx,lastHit.by,lastHit.bz);
}

function placeBlock(){
  if(!lastHit||document.pointerLockElement!==canvasEl)return;
  var px=lastHit.px,py=lastHit.py,pz=lastHit.pz;
  if(getBlock(px,py,pz)!==0)return;
  /* check player overlap */
  if(px+1>player.x-PLAYER_HW&&px<player.x+PLAYER_HW&&
     py+1>player.y&&py<player.y+PLAYER_H&&
     pz+1>player.z-PLAYER_HW&&pz<player.z+PLAYER_HW)return;
  setBlock(px,py,pz,HOTBAR_BLOCKS[hotbarIdx]);
  rebuildChunkAt(px,py,pz);
}

/* ── UI ────────────────────────────────────────────── */
function buildHotbar(){
  var hb=document.getElementById('hotbar');
  hb.innerHTML='';
  for(var i=0;i<7;i++){
    var d=document.createElement('div');
    d.className='slot'+(i===hotbarIdx?' selected':'');
    var hex='#'+BLOCK_COLORS[HOTBAR_BLOCKS[i]].map(function(c){
      return Math.round(c*255).toString(16).padStart(2,'0');
    }).join('');
    d.style.background=hex;
    d.innerHTML='<span>'+(i+1)+'</span>';
    hb.appendChild(d);
  }
}
function updateHotbarUI(){
  var slots=document.querySelectorAll('.slot');
  for(var i=0;i<slots.length;i++)
    slots[i].className='slot'+(i===hotbarIdx?' selected':'');
}

/* ── clouds & water ────────────────────────────────── */
function createClouds(){
  for(var i=0;i<25;i++){
    var w=8+Math.random()*12,d=8+Math.random()*12;
    var geo=new THREE.BoxGeometry(w,1,d);
    var mat=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.6});
    var m=new THREE.Mesh(geo,mat);
    m.position.set((Math.random()-0.5)*200,85+Math.random()*10,(Math.random()-0.5)*200);
    m.spd=0.3+Math.random()*0.8;
    scene.add(m);cloudArr.push(m);
  }
}
function updateClouds(dt){
  for(var i=0;i<cloudArr.length;i++){
    var c=cloudArr[i];
    c.position.x+=c.spd*dt;
    var dx=c.position.x-player.x;
    if(dx>100)c.position.x-=200;
    if(dx<-100)c.position.x+=200;
  }
}
function createWater(){
  var geo=new THREE.PlaneGeometry(200,200);
  var mat=new THREE.MeshLambertMaterial({color:0x3388ff,transparent:true,opacity:0.45,side:THREE.DoubleSide});
  waterPlane=new THREE.Mesh(geo,mat);
  waterPlane.rotation.x=-Math.PI/2;
  waterPlane.position.y=14.3;
  scene.add(waterPlane);
}
function updateWater(){
  waterPlane.position.x=player.x;
  waterPlane.position.z=player.z;
}

/* ── chunk manager ─────────────────────────────────── */
function updateChunks(){
  var pcx=Math.floor(player.x/CHUNK_W),pcz=Math.floor(player.z/CHUNK_W);
  /* generate */
  var tg=[];
  for(var dx=-5;dx<=5;dx++){
    for(var dz=-5;dz<=5;dz++){
      var cx=pcx+dx,cz=pcz+dz,key=ck(cx,cz);
      if(!chunks.has(key))tg.push({cx:cx,cz:cz,key:key,d:dx*dx+dz*dz});
    }
  }
  tg.sort(function(a,b){return a.d-b.d;});
  for(var i=0;i<Math.min(4,tg.length);i++){
    var e=tg[i];
    chunks.set(e.key,{data:genChunkData(e.cx,e.cz),mesh:null,cx:e.cx,cz:e.cz});
  }
  /* mesh */
  var tm=[];
  for(var dx=-4;dx<=4;dx++){
    for(var dz=-4;dz<=4;dz++){
      var cx=pcx+dx,cz=pcz+dz,key=ck(cx,cz);
      var ch=chunks.get(key);
      if(ch&&!ch.mesh){
        if(chunks.has(ck(cx-1,cz))&&chunks.has(ck(cx+1,cz))&&
           chunks.has(ck(cx,cz-1))&&chunks.has(ck(cx,cz+1)))
          tm.push({cx:cx,cz:cz,key:key,d:dx*dx+dz*dz});
      }
    }
  }
  tm.sort(function(a,b){return a.d-b.d;});
  for(var i=0;i<Math.min(2,tm.length);i++){
    var e=tm[i];
    var ch=chunks.get(e.key);
    ch.mesh=buildMesh(e.cx,e.cz,ch.data);
    if(ch.mesh){scene.add(ch.mesh);chunkMeshes.push(ch.mesh);}
  }
  /* unload */
  var all=Array.from(chunks.entries());
  for(var i=0;i<all.length;i++){
    var key=all[i][0],ch=all[i][1];
    var dx=ch.cx-pcx,dz=ch.cz-pcz;
    if(Math.abs(dx)>7||Math.abs(dz)>7){
      if(ch.mesh){
        scene.remove(ch.mesh);
        ch.mesh.geometry.dispose();
        var idx=chunkMeshes.indexOf(ch.mesh);
        if(idx>=0)chunkMeshes.splice(idx,1);
      }
      chunks.delete(key);
    }
  }
}

/* ── init ──────────────────────────────────────────── */
function init(){
  scene=new THREE.Scene();
  scene.background=new THREE.Color(0x87ceeb);
  scene.fog=new THREE.Fog(0x87ceeb,40,110);

  camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
  camera.rotation.order='YXZ';

  renderer=new THREE.WebGLRenderer({antialias:true});
  renderer.setSize(window.innerWidth,window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  canvasEl=renderer.domElement;
  document.body.appendChild(canvasEl);

  sharedMat=new THREE.MeshLambertMaterial({vertexColors:true});

  scene.add(new THREE.AmbientLight(0xffffff,0.65));
  var dl=new THREE.DirectionalLight(0xffffff,0.8);
  dl.position.set(1,1,0.5).normalize();
  scene.add(dl);

  /* selection outline */
  selBox=new THREE.LineSegments(
    new THREE.BoxGeometry(1.005,1.005,1.005),
    new THREE.LineBasicMaterial({color:0x000000})
  );
  selBox.visible=false;
  scene.add(selBox);

  /* spawn */
  spawnX=8.5;spawnZ=8.5;
  var sh=terrainH(8,8);
  spawnY=sh+2;
  player.x=spawnX;player.y=spawnY;player.z=spawnZ;

  /* pre-generate spawn area */
  var scx=Math.floor(spawnX/CHUNK_W),scz=Math.floor(spawnZ/CHUNK_W);
  for(var dx=-2;dx<=2;dx++){
    for(var dz=-2;dz<=2;dz++){
      var cx=scx+dx,cz=scz+dz,key=ck(cx,cz);
      if(!chunks.has(key))
        chunks.set(key,{data:genChunkData(cx,cz),mesh:null,cx:cx,cz:cz});
    }
  }
  for(var dx=-1;dx<=1;dx++){
    for(var dz=-1;dz<=1;dz++){
      rebuildChunk(scx+dx,scz+dz);
    }
  }

  createClouds();
  createWater();

  overlayEl=document.getElementById('overlay');
  buildHotbar();

  /* events */
  overlayEl.addEventListener('click',function(){canvasEl.requestPointerLock();});
  document.addEventListener('pointerlockchange',function(){
    if(document.pointerLockElement===canvasEl)overlayEl.classList.add('hidden');
    else overlayEl.classList.remove('hidden');
  });
  document.addEventListener('contextmenu',function(e){e.preventDefault();});
  document.addEventListener('mousemove',function(e){
    if(document.pointerLockElement!==canvasEl)return;
    player.yaw-=e.movementX*0.002;
    player.pitch-=e.movementY*0.002;
    player.pitch=Math.max(-Math.PI/2,Math.min(Math.PI/2,player.pitch));
  });
  canvasEl.addEventListener('mousedown',function(e){
    if(document.pointerLockElement!==canvasEl)return;
    if(e.button===0)breakBlock();
    if(e.button===2)placeBlock();
  });
  canvasEl.addEventListener('wheel',function(e){
    if(document.pointerLockElement!==canvasEl)return;
    if(e.deltaY>0)hotbarIdx=(hotbarIdx+1)%7;
    else if(e.deltaY<0)hotbarIdx=(hotbarIdx+6)%7;
    updateHotbarUI();
  });
  document.addEventListener('keydown',function(e){
    keys[e.key.toLowerCase()]=true;
    var k=e.key;
    if(k>='1'&&k<='7'){hotbarIdx=parseInt(k)-1;updateHotbarUI();}
  });
  document.addEventListener('keyup',function(e){keys[e.key.toLowerCase()]=false;});
  window.addEventListener('resize',function(){
    camera.aspect=window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth,window.innerHeight);
  });

  var lastTime=performance.now();
  (function animate(){
    requestAnimationFrame(animate);
    var now=performance.now();
    var dt=Math.min((now-lastTime)/1000,0.1);
    lastTime=now;
    updatePhysics(dt);
    updateChunks();
    updateSelection();
    updateClouds(dt);
    updateWater();
    camera.position.set(player.x,player.y+PLAYER_EYE,player.z);
    camera.rotation.set(player.pitch,player.yaw,0,'YXZ');
    renderer.render(scene,camera);
  })();
}
init();
</script>
</body>
</html>
```