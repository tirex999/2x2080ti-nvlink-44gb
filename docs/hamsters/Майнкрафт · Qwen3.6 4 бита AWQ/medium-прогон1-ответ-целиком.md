

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>mc.html</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000;font-family:'Courier New',monospace}
canvas{display:block}
#overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.75);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;z-index:100;cursor:pointer}
#overlay h1{font-size:48px;margin-bottom:20px;text-shadow:2px 2px #000}
#overlay p{font-size:16px;margin:4px 0;color:#ccc}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);color:#fff;font-size:24px;pointer-events:none;z-index:10;text-shadow:0 0 2px #000}
#hotbar{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:2px;background:rgba(0,0,0,0.6);padding:4px;border-radius:4px;z-index:10}
.slot{width:48px;height:48px;display:flex;align-items:center;justify-content:center;border:2px solid #555;border-radius:2px;font-size:12px;color:#fff;font-weight:bold;text-shadow:1px 1px #000}
.slot.selected{border-color:#fff}
</style>
</head>
<body>
<div id="overlay">
<h1>mc.html</h1>
<p>WASD - Move | Space - Jump</p>
<p>Left Click - Break Block</p>
<p>Right Click - Place Block</p>
<p>1-7 / Scroll - Select Block</p>
<p style="margin-top:20px;font-size:20px;color:#fff">Click to Play</p>
</div>
<div id="crosshair">+</div>
<div id="hotbar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// ===== BLOCK IDS =====
var AIR=0,GRASS=1,DIRT=2,STONE=3,SAND=4,WOOD=5,LEAVES=6,SNOW=7;
var BLOCK_COLORS=[0x000000,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
var BLOCK_NAMES=['','Grass','Dirt','Stone','Sand','Wood','Leaves','Snow'];
var HOTBAR_BLOCKS=[GRASS,DIRT,STONE,SAND,WOOD,LEAVES,SNOW];

// ===== NOISE FUNCTIONS =====
function hashCoord(x,y){
  var h=(x*374761393+y*668265263+1013904223)|0;
  h=((h^(h>>>13))*1274126177)|0;
  h=((h^(h>>>16))|0);
  return(h&0x7fffffff)/0x7fffffff;
}

function hashCoord3(x,y,z){
  var h=(x*374761393+y*668265263+z*1013904223+12345)|0;
  h=((h^(h>>>13))*1274126177)|0;
  h=((h^(h>>>16))|0);
  return(h&0x7fffffff)/0x7fffffff;
}

function smoothstep(t){return t*t*(3-2*t)}

function lerp(a,b,t){return a+(b-a)*t}

function noise2D(x,y){
  var ix=Math.floor(x),iy=Math.floor(y);
  var fx=x-ix,fy=y-iy;
  var sx=smoothstep(fx),sy=smoothstep(fy);
  var v00=hashCoord(ix,iy),v10=hashCoord(ix+1,iy);
  var v01=hashCoord(ix,iy+1),v11=hashCoord(ix+1,iy+1);
  return lerp(lerp(v00,v10,sx),lerp(v01,v11,sx),sy);
}

function noise3D(x,y,z){
  var ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
  var fx=x-ix,fy=y-iy,fz=z-iz;
  var sx=smoothstep(fx),sy=smoothstep(fy),sz=smoothstep(fz);
  var v000=hashCoord3(ix,iy,iz),v100=hashCoord3(ix+1,iy,iz);
  var v010=hashCoord3(ix,iy+1,iz),v110=hashCoord3(ix+1,iy+1,iz);
  var v001=hashCoord3(ix,iy,iz+1),v101=hashCoord3(ix+1,iy,iz+1);
  var v011=hashCoord3(ix,iy+1,iz+1),v111=hashCoord3(ix+1,iy+1,iz+1);
  var a=lerp(v000,v100,sx),b=lerp(v010,v110,sx);
  var c=lerp(v001,v101,sx),d=lerp(v011,v111,sx);
  return lerp(lerp(a,b,sy),lerp(c,d,sy),sz);
}

function fractalNoise2D(x,y,octaves){
  var val=0,amp=1,freq=1,max=0;
  for(var i=0;i<octaves;i++){
    val+=noise2D(x*freq,y*freq)*amp;
    max+=amp;
    amp*=0.5;
    freq*=2;
  }
  return val/max;
}

function fractalNoise3D(x,y,z,octaves){
  var val=0,amp=1,freq=1,max=0;
  for(var i=0;i<octaves;i++){
    val+=noise3D(x*freq,y*freq,z*freq)*amp;
    max+=amp;
    amp*=0.5;
    freq*=2;
  }
  return val/max;
}

// ===== CHUNK SYSTEM =====
var CHUNK_SIZE=16;
var CHUNK_HEIGHT=80;
var chunks=new Map();
var chunkMeshes=[];
var chunksToGenerate=[];
var chunksToMesh=[];

function chunkKey(cx,cz){return cx+','+cz}

function getBlock(wx,wy,wz){
  if(wy<0||wy>=CHUNK_HEIGHT)return AIR;
  var cx=Math.floor(wx/CHUNK_SIZE);
  var cz=Math.floor(wz/CHUNK_SIZE);
  var key=chunkKey(cx,cz);
  var ch=chunks.get(key);
  if(!ch)return AIR;
  var lx=((wx%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  var lz=((wz%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  return ch.data[lx+lz*CHUNK_SIZE+wy*CHUNK_SIZE*CHUNK_SIZE];
}

function setBlock(wx,wy,wz,id){
  if(wy<0||wy>=CHUNK_HEIGHT)return;
  var cx=Math.floor(wx/CHUNK_SIZE);
  var cz=Math.floor(wz/CHUNK_SIZE);
  var key=chunkKey(cx,cz);
  var ch=chunks.get(key);
  if(!ch)return;
  var lx=((wx%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  var lz=((wz%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  ch.data[lx+lz*CHUNK_SIZE+wy*CHUNK_SIZE*CHUNK_SIZE]=id;
}

function createChunk(cx,cz){
  var data=new Uint8Array(CHUNK_SIZE*CHUNK_SIZE*CHUNK_HEIGHT);
  var key=chunkKey(cx,cz);
  chunks.set(key,{data:data,mesh:null});
}

// ===== TERRAIN GENERATION =====
function generateChunkData(cx,cz){
  var key=chunkKey(cx,cz);
  var ch=chunks.get(key);
  if(!ch)return;
  var data=ch.data;
  var ox=cx*CHUNK_SIZE;
  var oz=cz*CHUNK_SIZE;

  for(var lx=0;lx<CHUNK_SIZE;lx++){
    for(var lz=0;lz<CHUNK_SIZE;lz++){
      var wx=ox+lx;
      var wz=oz+lz;

      // Column height
      var m=fractalNoise2D(wx*0.004,wz*0.004,4);
      var h=fractalNoise2D(wx*0.02,wz*0.02,4);
      var H=Math.floor(5+m*m*58+h*10);

      // Fill column
      for(var y=0;y<CHUNK_HEIGHT;y++){
        var idx=lx+lz*CHUNK_SIZE+y*CHUNK_SIZE*CHUNK_SIZE;
        if(y===0){
          data[idx]=STONE; // unbreakable base
        } else if(y<H-3){
          data[idx]=STONE;
        } else if(y<H){
          // dirt or sand layers
          if(H<=16){
            data[idx]=SAND;
          } else {
            data[idx]=DIRT;
          }
        } else if(y===H){
          // surface
          if(H>=46){
            data[idx]=SNOW;
          } else if(H>=37){
            data[idx]=STONE;
          } else if(H<=16){
            data[idx]=SAND;
          } else {
            data[idx]=GRASS;
          }
        } else {
          data[idx]=AIR;
        }

        // Caves
        if(y>=3&&y<H-2&&data[idx]!==AIR){
          var cave=fractalNoise3D(wx*0.09,y*0.09,wz*0.09,3);
          if(cave>0.67){
            data[idx]=AIR;
          }
        }
      }

      // Trees
      if(data[lx+lz*CHUNK_SIZE+H*CHUNK_SIZE*CHUNK_SIZE]===GRASS){
        var treeHash=hashCoord(wx*7+wz*13,H);
        if(treeHash<0.02){
          // Check trunk fits in chunk
          var trunkTop=H+4;
          if(trunkTop<CHUNK_SIZE){
            // Only place if trunk is within this chunk's vertical range
            // Trunk: 4 blocks up from surface
            for(var ty=H+1;ty<=H+4;ty++){
              var idx2=lx+lz*CHUNK_SIZE+ty*CHUNK_SIZE*CHUNK_SIZE;
              if(data[idx2]===AIR)data[idx2]=WOOD;
            }
            // Leaves
            // 5x5 layer at H+5 and H+6
            for(var ly=H+5;ly<=H+6;ly++){
              for(var dx=-2;dx<=2;dx++){
                for(var dz=-2;dz<=2;dz++){
                  var nlx=lx+dx,nlz=lz+dz;
                  if(nlx>=0&&nlx<CHUNK_SIZE&&nlz>=0&&nlz<CHUNK_SIZE){
                    var idx3=nlx+nlz*CHUNK_SIZE+ly*CHUNK_SIZE*CHUNK_SIZE;
                    if(data[idx3]===AIR)data[idx3]=LEAVES;
                  }
                }
              }
            }
            // 3x3 at H+7
            var ly2=H+7;
            for(var dx=-1;dx<=1;dx++){
              for(var dz=-1;dz<=1;dz++){
                var nlx=lx+dx,nlz=lz+dz;
                if(nlx>=0&&nlx<CHUNK_SIZE&&nlz>=0&&nlz<CHUNK_SIZE){
                  var idx3=nlx+nlz*CHUNK_SIZE+ly2*CHUNK_SIZE*CHUNK_SIZE;
                  if(data[idx3]===AIR)data[idx3]=LEAVES;
                }
              }
            }
            // 1 on top at H+8
            var ly3=H+8;
            if(ly3<CHUNK_HEIGHT){
              var idx4=lx+lz*CHUNK_SIZE+ly3*CHUNK_SIZE*CHUNK_SIZE;
              if(data[idx4]===AIR)data[idx4]=LEAVES;
            }
          }
        }
      }
    }
  }
}

// ===== MESHING =====
var faceDirs=[
  {dir:[1,0,0],verts:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],light:0.8},
  {dir:[-1,0,0],verts:[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],light:0.8},
  {dir:[0,1,0],verts:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]],light:1.0},
  {dir:[0,-1,0],verts:[[0,0,1],[0,0,0],[1,0,0],[1,0,1]],light:0.55},
  {dir:[0,0,1],verts:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]],light:0.8},
  {dir:[0,0,-1],verts:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]],light:0.8}
];

function buildChunkMesh(cx,cz){
  var key=chunkKey(cx,cz);
  var ch=chunks.get(key);
  if(!ch)return;

  var positions=[],normals=[],colors=[];
  var ox=cx*CHUNK_SIZE;
  var oz=cz*CHUNK_SIZE;
  var data=ch.data;

  for(var lx=0;lx<CHUNK_SIZE;lx++){
    for(var lz=0;lz<CHUNK_SIZE;lz++){
      for(var y=0;y<CHUNK_HEIGHT;y++){
        var idx=lx+lz*CHUNK_SIZE+y*CHUNK_SIZE*CHUNK_SIZE;
        var block=data[idx];
        if(block===AIR)continue;

        var color=BLOCK_COLORS[block];
        var r=((color>>16)&0xff)/255;
        var g=((color>>8)&0xff)/255;
        var b=(color&0xff)/255;

        for(var f=0;f<6;f++){
          var fd=faceDirs[f];
          var nx=lx+fd.dir[0];
          var ny=y+fd.dir[1];
          var nz=lz+fd.dir[2];

          var neighbor=AIR;
          if(nx>=0&&nx<CHUNK_SIZE&&ny>=0&&ny<CHUNK_HEIGHT&&nz>=0&&nz<CHUNK_SIZE){
            neighbor=data[nx+nz*CHUNK_SIZE+ny*CHUNK_SIZE*CHUNK_SIZE];
          } else {
            neighbor=getBlock(ox+nx,ny,oz+nz);
          }

          if(neighbor===AIR){
            var wx=ox+lx;
            var wz=oz+lz;
            var light=fd.light;
            var cr=r*light,cg=g*light,cb=b*light;

            for(var v=0;v<4;v++){
              var vert=fd.verts[v];
              positions.push(wx+vert[0],y+vert[1],wz+vert[2]);
              normals.push(fd.dir[0],fd.dir[1],fd.dir[2]);
              colors.push(cr,cg,cb);
            }
            // Two triangles: 0,1,2 and 0,2,3
            var base=positions.length/3-6;
            // Already added 4 vertices, need indices
          }
        }
      }
    }
  }

  // Rebuild with indices
  positions=[];normals=[];colors=[];
  var indices=[];
  var vertCount=0;

  for(var lx=0;lx<CHUNK_SIZE;lx++){
    for(var lz=0;lz<CHUNK_SIZE;lz++){
      for(var y=0;y<CHUNK_HEIGHT;y++){
        var idx=lx+lz*CHUNK_SIZE+y*CHUNK_SIZE*CHUNK_SIZE;
        var block=data[idx];
        if(block===AIR)continue;

        var color=BLOCK_COLORS[block];
        var r=((color>>16)&0xff)/255;
        var g=((color>>8)&0xff)/255;
        var b=(color&0xff)/255;

        for(var f=0;f<6;f++){
          var fd=faceDirs[f];
          var nx=lx+fd.dir[0];
          var ny=y+fd.dir[1];
          var nz=lz+fd.dir[2];

          var neighbor=AIR;
          if(nx>=0&&nx<CHUNK_SIZE&&ny>=0&&ny<CHUNK_HEIGHT&&nz>=0&&nz<CHUNK_SIZE){
            neighbor=data[nx+nz*CHUNK_SIZE+ny*CHUNK_SIZE*CHUNK_SIZE];
          } else {
            neighbor=getBlock(ox+nx,ny,oz+nz);
          }

          if(neighbor===AIR){
            var wx=ox+lx;
            var wz=oz+lz;
            var light=fd.light;
            var cr=r*light,cg=g*light,cb=b*light;

            for(var v=0;v<4;v++){
              var vert=fd.verts[v];
              positions.push(wx+vert[0],y+vert[1],wz+vert[2]);
              normals.push(fd.dir[0],fd.dir[1],fd.dir[2]);
              colors.push(cr,cg,cb);
            }
            indices.push(vertCount,vertCount+1,vertCount+2,vertCount,vertCount+2,vertCount+3);
            vertCount+=4;
          }
        }
      }
    }
  }

  if(ch.mesh){
    scene.remove(ch.mesh);
    ch.mesh.geometry.dispose();
    chunkMeshes=chunkMeshes.filter(function(m){return m!==ch.mesh});
  }

  if(positions.length===0){
    ch.mesh=null;
    return;
  }

  var geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  geo.setIndex(indices);
  geo.computeBoundingSphere();

  var mat=new THREE.MeshLambertMaterial({vertexColors:true});
  var mesh=new THREE.Mesh(geo,mat);
  scene.add(mesh);
  ch.mesh=mesh;
  chunkMeshes.push(mesh);
}

function rebuildChunk(cx,cz){
  var key=chunkKey(cx,cz);
  var ch=chunks.get(key);
  if(!ch||!ch.data)return;
  buildChunkMesh(cx,cz);
}

// ===== THREE.JS SETUP =====
var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);

var camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order='YXZ';

var renderer=new THREE.WebGLRenderer({antialias:false});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
document.body.appendChild(renderer.domElement);

// Lights
var ambientLight=new THREE.AmbientLight(0xffffff,0.65);
scene.add(ambientLight);
var dirLight=new THREE.DirectionalLight(0xffffff,0.8);
dirLight.position.set(50,100,30);
scene.add(dirLight);

// Water plane
var waterGeo=new THREE.PlaneGeometry(300,300);
var waterMat=new THREE.MeshLambertMaterial({color:0x3388cc,transparent:true,opacity:0.5,side:THREE.DoubleSide});
var waterMesh=new THREE.Mesh(waterGeo,waterMat);
waterMesh.rotation.x=-Math.PI/2;
waterMesh.position.y=14.3;
scene.add(waterMesh);

// Clouds
var clouds=[];
for(var i=0;i<25;i++){
  var cw=8+Math.floor(hashCoord(i*3,i*7)*20);
  var cd=4+Math.floor(hashCoord(i*5,i*11)*12);
  var cloudGeo=new THREE.BoxGeometry(cw,1,cd);
  var cloudMat=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.8});
  var cloud=new THREE.Mesh(cloudGeo,cloudMat);
  cloud.position.set(
    (hashCoord(i*13,i*17)-0.5)*200,
    88+hashCoord(i*19,i*23)*8,
    (hashCoord(i*29,i*31)-0.5)*200
  );
  cloud.userData.speed=0.3+hashCoord(i*37,i*41)*0.7;
  scene.add(cloud);
  clouds.push(cloud);
}

// Selection outline
var outlineGeo=new THREE.EdgesGeometry(new THREE.BoxGeometry(1.005,1.005,1.005));
var outlineMat=new THREE.LineBasicMaterial({color:0x000000,linewidth:2});
var outline=new THREE.LineSegments(outlineGeo,outlineMat);
outline.visible=false;
scene.add(outline);

// ===== PLAYER =====
var player={
  x:8,y:60,z:8,
  vx:0,vy:0,vz:0,
  yaw:0,pitch:0,
  onGround:false,
  halfWidth:0.3,
  height:1.8,
  eyeHeight:1.62,
  selectedSlot:0
};

// Find spawn height
function findSpawnHeight(){
  var H=Math.floor(5+fractalNoise2D(8*0.004,8*0.004,4)*fractalNoise2D(8*0.004,8*0.004,4)*58+fractalNoise2D(8*0.02,8*0.02,4)*10);
  return H+2;
}

// ===== CONTROLS =====
var keys={};
var pointerLocked=false;

document.addEventListener('keydown',function(e){
  keys[e.code]=true;
  if(e.code>='Digit1'&&e.code<='Digit7'){
    player.selectedSlot=parseInt(e.code.charAt(5))-1;
    updateHotbar();
  }
});
document.addEventListener('keyup',function(e){keys[e.code]=false});

document.addEventListener('mousemove',function(e){
  if(!pointerLocked)return;
  player.yaw-=e.movementX*0.002;
  player.pitch-=e.movementY*0.002;
  player.pitch=Math.max(-Math.PI/2+0.01,Math.min(Math.PI/2-0.01,player.pitch));
});

document.addEventListener('wheel',function(e){
  if(!pointerLocked)return;
  if(e.deltaY>0){
    player.selectedSlot=(player.selectedSlot+1)%7;
  } else {
    player.selectedSlot=(player.selectedSlot+6)%7;
  }
  updateHotbar();
});

document.addEventListener('contextmenu',function(e){e.preventDefault()});

// Pointer lock
var overlay=document.getElementById('overlay');
overlay.addEventListener('click',function(){
  renderer.domElement.requestPointerLock();
});

document.addEventListener('pointerlockchange',function(){
  pointerLocked=!!document.pointerLockElement;
  overlay.style.display=pointerLocked?'none':'flex';
});

// Mouse buttons
document.addEventListener('mousedown',function(e){
  if(!pointerLocked)return;
  if(e.button===0)breakBlock();
  if(e.button===2)placeBlock();
});

// ===== RAYCASTING =====
var raycaster=new THREE.Raycaster();
raycaster.far=6;

function getRayHit(){
  var camPos=camera.position;
  var dir=new THREE.Vector3(0,0,-1);
  dir.applyQuaternion(camera.quaternion);
  raycaster.set(camPos,dir);
  var hits=raycaster.intersectObjects(chunkMeshes,false);
  if(hits.length===0)return null;
  return hits[0];
}

function breakBlock(){
  var hit=getRayHit();
  if(!hit)return;
  var p=hit.point;
  var n=hit.face.normal;
  var tx=Math.floor(p.x-n.x*0.5);
  var ty=Math.floor(p.y-n.y*0.5);
  var tz=Math.floor(p.z-n.z*0.5);

  if(ty===0)return; // unbreakable

  var block=getBlock(tx,ty,tz);
  if(block===AIR)return;

  setBlock(tx,ty,tz,AIR);

  // Rebuild affected chunks
  var cx1=Math.floor((tx>=0?tx:tx-15)/CHUNK_SIZE);
  var cz1=Math.floor((tz>=0?tz:tz-15)/CHUNK_SIZE);
  rebuildChunk(cx1,cz1);

  // Check if on chunk border
  var lx=((tx%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  var lz=((tz%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  if(lx===0){rebuildChunk(cx1-1,cz1)}
  if(lx===CHUNK_SIZE-1){rebuildChunk(cx1+1,cz1)}
  if(lz===0){rebuildChunk(cx1,cz1-1)}
  if(lz===CHUNK_SIZE-1){rebuildChunk(cx1,cz1+1)}
}

function placeBlock(){
  var hit=getRayHit();
  if(!hit)return;
  var p=hit.point;
  var n=hit.face.normal;
  var px=Math.floor(p.x+n.x*0.5);
  var py=Math.floor(p.y+n.y*0.5);
  var pz=Math.floor(p.z+n.z*0.5);

  if(getBlock(px,py,pz)!==AIR)return;

  // Check player overlap
  var phw=player.halfWidth;
  var ph=player.height;
  var pe=player.eyeHeight;
  var pw=player.x,py2=player.y,pz2=player.z;
  if(px>=pw-phw&&px<=pw+phw&&py>=py2&&py<=py2+pe&&pz>=pz2-phw&&pz<=pz2+phw)return;

  setBlock(px,py,pz,HOTBAR_BLOCKS[player.selectedSlot]);

  var cx1=Math.floor((px>=0?px:px-15)/CHUNK_SIZE);
  var cz1=Math.floor((pz>=0?pz:pz-15)/CHUNK_SIZE);
  rebuildChunk(cx1,cz1);

  var lx=((px%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  var lz=((pz%CHUNK_SIZE)+CHUNK_SIZE)%CHUNK_SIZE;
  if(lx===0){rebuildChunk(cx1-1,cz1)}
  if(lx===CHUNK_SIZE-1){rebuildChunk(cx1+1,cz1)}
  if(lz===0){rebuildChunk(cx1,cz1-1)}
  if(lz===CHUNK_SIZE-1){rebuildChunk(cx1,cz1+1)}
}

// ===== COLLISION =====
function collidesAt(x,y,z){
  var hw=player.halfWidth;
  var h=player.height;
  var minX=Math.floor(x-hw);
  var maxX=Math.floor(x+hw);
  var minY=Math.floor(y);
  var maxY=Math.floor(y+h);
  var minZ=Math.floor(z-hw);
  var maxZ=Math.floor(z+hw);

  for(var bx=minX;bx<=maxX;bx++){
    for(var bz=minZ;bz<=maxZ;bz++){
      for(var by=minY;by<maxY;by++){
        if(getBlock(bx,by,bz)!==AIR)return true;
      }
    }
  }
  return false;
}

// ===== GAME LOOP =====
var lastTime=performance.now();
var spawnY=findSpawnHeight();
player.y=spawnY;

function update(dt){
  // Movement
  var moveSpeed=5.5;
  var forward=new THREE.Vector3(-Math.sin(player.yaw),0,-Math.cos(player.yaw));
  var right=new THREE.Vector3(Math.cos(player.yaw),0,-Math.sin(player.yaw));

  var mx=0,mz=0;
  if(keys['KeyW']){mx+=forward.x;mz+=forward.z}
  if(keys['KeyS']){mx-=forward.x;mz-=forward.z}
  if(keys['KeyA']){mx-=right.x;mz-=right.z}
  if(keys['KeyD']){mx+=right.x;mz+=right.z}

  var len=Math.sqrt(mx*mx+mz*mz);
  if(len>0){mx/=len;mz/=len}

  player.vx=mx*moveSpeed;
  player.vz=mz*moveSpeed;

  // Gravity
  player.vy-=25*dt;

  // Jump
  if(keys['Space']&&player.onGround){
    player.vy=8.5;
    player.onGround=false;
  }

  // Move per axis with collision
  // X axis
  var newX=player.x+player.vx*dt;
  if(!collidesAt(newX,player.y,player.z)){
    player.x=newX;
  } else {
    player.vx=0;
  }

  // Z axis
  var newZ=player.z+player.vz*dt;
  if(!collidesAt(player.x,player.y,newZ)){
    player.z=newZ;
  } else {
    player.vz=0;
  }

  // Y axis
  var newY=player.y+player.vy*dt;
  if(!collidesAt(player.x,newY,player.z)){
    player.y=newY;
    player.onGround=false;
  } else {
    if(player.vy<0){
      player.onGround=true;
    }
    player.vy=0;
  }

  // Teleport if fallen too far
  if(player.y<-20){
    player.x=8;player.y=spawnY;player.z=8;
    player.vx=0;player.vy=0;player.vz=0;
  }

  // Update camera
  camera.position.set(player.x,player.y+player.eyeHeight,player.z);
  camera.rotation.set(player.pitch,player.yaw,0,'YXZ');

  // Update water position
  waterMesh.position.x=player.x;
  waterMesh.position.z=player.z;

  // Update clouds
  for(var i=0;i<clouds.length;i++){
    var c=clouds[i];
    c.position.x+=c.userData.speed*dt;
    if(c.position.x-player.x>120)c.position.x-=240;
    if(c.position.x-player.x<-120)c.position.x+=240;
  }

  // Update selection outline
  var hit=getRayHit();
  if(hit){
    var p=hit.point;
    var n=hit.face.normal;
    var tx=Math.floor(p.x-n.x*0.5);
    var ty=Math.floor(p.y-n.y*0.5);
    var tz=Math.floor(p.z-n.z*0.5);
    outline.position.set(tx+0.5,ty+0.5,tz+0.5);
    outline.visible=true;
  } else {
    outline.visible=false;
  }
}

// ===== CHUNK MANAGEMENT =====
function manageChunks(){
  var pcx=Math.floor(player.x/CHUNK_SIZE);
  var pcz=Math.floor(player.z/CHUNK_SIZE);

  // Generate chunks within 5 chunks radius
  var generated=0;
  var toGen=[];
  for(var dx=-5;dx<=5;dx++){
    for(var dz=-5;dz<=5;dz++){
      var cx=pcx+dx,cz=pcz+dz;
      var key=chunkKey(cx,cz);
      if(!chunks.has(key)){
        toGen.push({cx:cx,cz:cz});
      }
    }
  }
  // Sort by distance
  toGen.sort(function(a,b){
    var da=a.cx-pcx,da2=a.cz-pcz;
    var db=b.cx-pcx,db2=b.cz-pcz;
    return da*da+da2*da2-db*db-db2*db2;
  });

  for(var i=0;i<toGen.length&&generated<4;i++){
    var g=toGen[i];
    createChunk(g.cx,g.cz);
    generateChunkData(g.cx,g.cz);
    generated++;
  }

  // Build meshes within 4 chunks radius
  var meshed=0;
  for(var dx=-4;dx<=4;dx++){
    for(var dz=-4;dz<=4;dz++){
      var cx=pcx+dx,cz=pcz+dz;
      var key=chunkKey(cx,cz);
      var ch=chunks.get(key);
      if(!ch)continue;
      if(ch.mesh)continue;
      // Check all 4 neighbors have data
      var neighbors=[[cx-1,cz],[cx+1,cz],[cx,cz-1],[cx,cz+1]];
      var hasAllNeighbors=true;
      for(var ni=0;ni<neighbors.length;ni++){
        var nk=chunkKey(neighbors[ni][0],neighbors[ni][1]);
        if(!chunks.has(nk)||!chunks.get(nk).data){
          hasAllNeighbors=false;break;
        }
      }
      if(hasAllNeighbors){
        buildChunkMesh(cx,cz);
        meshed++;
        if(meshed>=2)break;
      }
    }
  }

  // Remove chunks beyond 7 chunks radius
  var toRemove=[];
  chunks.forEach(function(ch,key){
    var parts=key.split(',');
    var cx=parseInt(parts[0]),cz=parseInt(parts[1]);
    var dx=cx-pcx,dz=cz-pcz;
    if(dx*dx+dz*dz>7*7){
      toRemove.push(key);
    }
  });

  for(var i=0;i<toRemove.length;i++){
    var key=toRemove[i];
    var ch=chunks.get(key);
    if(ch.mesh){
      scene.remove(ch.mesh);
      ch.mesh.geometry.dispose();
      ch.mesh.material.dispose();
      chunkMeshes=chunkMeshes.filter(function(m){return m!==ch.mesh});
    }
    chunks.delete(key);
  }
}

// ===== HOTBAR UI =====
function createHotbar(){
  var hb=document.getElementById('hotbar');
  hb.innerHTML='';
  for(var i=0;i<7;i++){
    var slot=document.createElement('div');
    slot.className='slot'+(i===player.selectedSlot?' selected':'');
    var c='#'+BLOCK_COLORS[HOTBAR_BLOCKS[i]].toString(16).padStart(6,'0');
    slot.style.backgroundColor=c;
    slot.textContent=i+1;
    hb.appendChild(slot);
  }
}

function updateHotbar(){
  var slots=document.querySelectorAll('.slot');
  for(var i=0;i<slots.length;i++){
    slots[i].className='slot'+(i===player.selectedSlot?' selected':'');
  }
}

createHotbar();

// ===== RESIZE =====
window.addEventListener('resize',function(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});

// ===== MAIN LOOP =====
function gameLoop(){
  requestAnimationFrame(gameLoop);
  var now=performance.now();
  var dt=Math.min((now-lastTime)/1000,0.05);
  lastTime=now;

  if(pointerLocked){
    manageChunks();
    update(dt);
  }

  renderer.render(scene,camera);
}

// Initial chunk generation around spawn
for(var dx=-3;dx<=3;dx++){
  for(var dz=-3;dz<=3;dz++){
    var cx=Math.floor(8/CHUNK_SIZE)+dx;
    var cz=Math.floor(8/CHUNK_SIZE)+dz;
    createChunk(cx,cz);
    generateChunkData(cx,cz);
  }
}

// Build initial meshes
for(var dx=-2;dx<=2;dx++){
  for(var dz=-2;dz<=2;dz++){
    var cx=Math.floor(8/CHUNK_SIZE)+dx;
    var cz=Math.floor(8/CHUNK_SIZE)+dz;
    buildChunkMesh(cx,cz);
  }
}

gameLoop();

})();
</script>
</body>
</html>
```