

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MineCraft JS</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;width:100vw;height:100vh;background:#000}
canvas{display:block}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:20px;height:20px;pointer-events:none;z-index:10}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:rgba(255,255,255,0.8)}
#crosshair::before{left:50%;top:0;width:2px;height:100%;transform:translateX(-50%)}
#crosshair::after{top:50%;left:0;height:2px;width:100%;transform:translateY(-50%)}
#hotbar{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:4px;background:rgba(0,0,0,0.5);padding:4px;border-radius:4px;z-index:10}
.slot{width:48px;height:48px;border:2px solid rgba(255,255,255,0.3);display:flex;align-items:center;justify-content:center;font-family:monospace;font-size:12px;color:white;text-shadow:1px 1px 2px black;position:relative}
.slot.selected{border:2px solid #fff}
.slot .bc{position:absolute;top:2px;left:2px;right:2px;bottom:16px;border-radius:2px}
.slot .sn{position:absolute;bottom:2px;left:50%;transform:translateX(-50%)}
#overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:100;color:#fff;font-family:'Courier New',monospace}
#overlay h1{font-size:48px;margin-bottom:20px;text-shadow:2px 2px 4px #000}
#overlay .ctrl{font-size:15px;line-height:1.9;margin-bottom:30px;text-align:center}
#playBtn{font-size:22px;padding:12px 32px;background:#4caf50;color:#fff;border:none;cursor:pointer;border-radius:4px;font-family:inherit}
#playBtn:hover{background:#66bb6a}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
<h1>MineCraft JS</h1>
<div class="ctrl">
WASD - Move &nbsp;|&nbsp; Space - Jump<br>
Mouse - Look Around<br>
Left Click - Break Block<br>
Right Click - Place Block<br>
1-7 / Scroll - Select Block
</div>
<button id="playBtn">Click to Play</button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

// --- Noise Functions ---
function hash2D(x,y){
  var h=x*374761393+y*668265263;
  h=(h^(h>>>13))*1274126177;
  h=h^(h>>>16);
  return(h>>>0)/4294967296;
}
function hash3D(x,y,z){
  var h=x*374761393+y*668265263+z*1274126177;
  h=(h^(h>>>13))*1274126177;
  h=h^(h>>>16);
  return(h>>>0)/4294967296;
}
function smoothNoise2D(x,y){
  var ix=Math.floor(x),iy=Math.floor(y);
  var fx=x-ix,fy=y-iy;
  var sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy);
  var n00=hash2D(ix,iy),n10=hash2D(ix+1,iy);
  var n01=hash2D(ix,iy+1),n11=hash2D(ix+1,iy+1);
  var nx0=n00+(n10-n00)*sx;
  var nx1=n01+(n11-n01)*sx;
  return nx0+(nx1-nx0)*sy;
}
function fractal2D(x,y){
  var val=0,amp=1,freq=1,max=0;
  for(var i=0;i<4;i++){
    val+=smoothNoise2D(x*freq,y*freq)*amp;
    max+=amp;amp*=0.5;freq*=2;
  }
  return val/max;
}
function smoothNoise3D(x,y,z){
  var ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
  var fx=x-ix,fy=y-iy,fz=z-iz;
  var sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy),sz=fz*fz*(3-2*fz);
  var n000=hash3D(ix,iy,iz),n100=hash3D(ix+1,iy,iz);
  var n010=hash3D(ix,iy+1,iz),n110=hash3D(ix+1,iy+1,iz);
  var n001=hash3D(ix,iy,iz+1),n101=hash3D(ix+1,iy,iz+1);
  var n011=hash3D(ix,iy+1,iz+1),n111=hash3D(ix+1,iy+1,iz+1);
  var nx00=n000+(n100-n000)*sx;
  var nx10=n010+(n110-n010)*sx;
  var nx01=n001+(n101-n001)*sx;
  var nx11=n011+(n111-n011)*sx;
  var ny0=nx00+(nx10-nx00)*sy;
  var ny1=nx01+(nx11-nx01)*sy;
  return ny0+(ny1-ny0)*sz;
}
function fractal3D(x,y,z){
  var val=0,amp=1,freq=1,max=0;
  for(var i=0;i<3;i++){
    val+=smoothNoise3D(x*freq,y*freq,z*freq)*amp;
    max+=amp;amp*=0.5;freq*=2;
  }
  return val/max;
}

// --- Constants ---
var CHUNK_W=16,CHUNK_H=80;
var BLOCK_IDS={AIR:0,GRASS:1,DIRT:2,STONE:3,SAND:4,WOOD:5,LEAVES:6,SNOW:7};
var BLOCK_COLORS={
  1:[0x4c/255,0xaf/255,0x50/255],
  2:[0x79/255,0x55/255,0x48/255],
  3:[0x9e/255,0x9e/255,0x9e/255],
  4:[0xe7/255,0xd9/255,0xa8/255],
  5:[0x8d/255,0x6e/255,0x63/255],
  6:[0x2e/255,0x7d/255,0x32/255],
  7:[1,1,1]
};
var FACES=[
  {dir:[1,0,0],bright:0.8,verts:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]]},
  {dir:[-1,0,0],bright:0.8,verts:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]},
  {dir:[0,1,0],bright:1.0,verts:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]},
  {dir:[0,-1,0],bright:0.55,verts:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
  {dir:[0,0,1],bright:0.8,verts:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]},
  {dir:[0,0,-1],bright:0.8,verts:[[0,0,0],[0,1,0],[1,1,0],[1,0,0]]}
];

// --- Scene Setup ---
var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);

var camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order='YXZ';

var renderer=new THREE.WebGLRenderer({antialias:false});
renderer.setSize(window.innerWidth,window.innerHeight);
document.body.appendChild(renderer.domElement);

var ambientLight=new THREE.AmbientLight(0xffffff,0.65);
scene.add(ambientLight);
var dirLight=new THREE.DirectionalLight(0xffffff,0.8);
dirLight.position.set(100,200,80);
scene.add(dirLight);

var sharedMaterial=new THREE.MeshLambertMaterial({vertexColors:true});

// --- Chunk Storage ---
var chunks=new Map();
var meshList=[];

function getBlock(wx,wy,wz){
  if(wy<0||wy>=CHUNK_H)return 0;
  var cx=Math.floor(wx/CHUNK_W);
  var cz=Math.floor(wz/CHUNK_W);
  var lx=wx-cx*CHUNK_W;
  var lz=wz-cz*CHUNK_W;
  var chunk=chunks.get(cx+','+cz);
  if(!chunk||!chunk.data)return 0;
  return chunk.data[wy*256+lz*16+lx];
}
function setBlock(wx,wy,wz,id){
  if(wy<0||wy>=CHUNK_H)return;
  var cx=Math.floor(wx/CHUNK_W);
  var cz=Math.floor(wz/CHUNK_W);
  var lx=wx-cx*CHUNK_W;
  var lz=wz-cz*CHUNK_W;
  var chunk=chunks.get(cx+','+cz);
  if(!chunk||!chunk.data)return;
  chunk.data[wy*256+lz*16+lx]=id;
}

// --- Terrain Generation ---
function generateChunkData(cx,cz){
  var data=new Uint8Array(CHUNK_W*CHUNK_H*CHUNK_W);
  for(var lx=0;lx<CHUNK_W;lx++){
    for(var lz=0;lz<CHUNK_W;lz++){
      var wx=cx*CHUNK_W+lx;
      var wz=cz*CHUNK_W+lz;
      var m=fractal2D(wx*0.004,wz*0.004);
      var h=fractal2D(wx*0.02,wz*0.02);
      var H=Math.floor(5+m*m*58+h*10);
      if(H>79)H=79;if(H<1)H=1;

      var surfaceBlock,subBlock;
      if(H>=46){surfaceBlock=7;subBlock=3;}
      else if(H>=37){surfaceBlock=3;subBlock=3;}
      else if(H<=16){surfaceBlock=4;subBlock=4;}
      else{surfaceBlock=1;subBlock=2;}

      for(var y=0;y<=H;y++){
        var block;
        if(y===0){block=3;}
        else if(y===H){block=surfaceBlock;}
        else if(y>=H-2){block=subBlock;}
        else{block=3;}

        if(y>=3&&y<H){
          var cv=fractal3D(wx*0.09,y*0.09,wz*0.09);
          if(cv>0.67)block=0;
        }
        data[y*256+lz*16+lx]=block;
      }

      // Trees
      if(surfaceBlock===1&&lx>=2&&lx<=13&&lz>=2&&lz<=13&&H+7<CHUNK_H){
        var th=hash2D(wx*7+13,wz*7+41);
        if(th<0.02){
          for(var ty=1;ty<=4;ty++){
            var yy=H+ty;
            if(yy<CHUNK_H)data[yy*256+lz*16+lx]=5;
          }
          for(var ly=4;ly<=5;ly++){
            var yy2=H+ly;
            if(yy2>=CHUNK_H)continue;
            for(var dx=-2;dx<=2;dx++){
              for(var dz=-2;dz<=2;dz++){
                var tx=lx+dx,tz=lz+dz;
                if(tx<0||tx>=16||tz<0||tz>=16)continue;
                var idx=yy2*256+tz*16+tx;
                if(data[idx]===0)data[idx]=6;
              }
            }
          }
          var y6=H+6;
          if(y6<CHUNK_H){
            for(var dx2=-1;dx2<=1;dx2++){
              for(var dz2=-1;dz2<=1;dz2++){
                var tx2=lx+dx2,tz2=lz+dz2;
                if(tx2<0||tx2>=16||tz2<0||tz2>=16)continue;
                var idx2=y6*256+tz2*16+tx2;
                if(data[idx2]===0)data[idx2]=6;
              }
            }
          }
          var y7=H+7;
          if(y7<CHUNK_H){
            var idx3=y7*256+lz*16+lx;
            if(data[idx3]===0)data[idx3]=6;
          }
        }
      }
    }
  }
  return data;
}

// --- Mesh Building ---
function buildChunkMesh(cx,cz){
  var key=cx+','+cz;
  var chunk=chunks.get(key);
  if(!chunk||!chunk.data)return;

  if(chunk.mesh){
    scene.remove(chunk.mesh);
    var mi=meshList.indexOf(chunk.mesh);
    if(mi>=0)meshList.splice(mi,1);
    chunk.mesh.geometry.dispose();
    chunk.mesh=null;
  }

  var positions=[],normals=[],colors=[],indices=[];
  var vc=0;

  for(var y=0;y<CHUNK_H;y++){
    for(var lz=0;lz<CHUNK_W;lz++){
      for(var lx=0;lx<CHUNK_W;lx++){
        var bid=chunk.data[y*256+lz*16+lx];
        if(bid===0)continue;
        var col=BLOCK_COLORS[bid];
        if(!col)continue;

        var wx=cx*CHUNK_W+lx;
        var wz=cz*CHUNK_W+lz;

        for(var f=0;f<6;f++){
          var face=FACES[f];
          var nb=getBlock(wx+face.dir[0],y+face.dir[1],wz+face.dir[2]);
          if(nb!==0)continue;

          var base=vc;
          for(var v=0;v<4;v++){
            positions.push(wx+face.verts[v][0],y+face.verts[v][1],wz+face.verts[v][2]);
            normals.push(face.dir[0],face.dir[1],face.dir[2]);
            colors.push(col[0]*face.bright,col[1]*face.bright,col[2]*face.bright);
          }
          indices.push(base,base+1,base+2,base,base+2,base+3);
          vc+=4;
        }
      }
    }
  }

  if(vc===0)return;

  var geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  geo.setIndex(indices);

  var mesh=new THREE.Mesh(geo,sharedMaterial);
  scene.add(mesh);
  chunk.mesh=mesh;
  meshList.push(mesh);
}

function rebuildChunk(cx,cz){
  var key=cx+','+cz;
  var chunk=chunks.get(key);
  if(!chunk||!chunk.data)return;
  buildChunkMesh(cx,cz);
}

function rebuildAfterEdit(wx,wy,wz){
  var cx=Math.floor(wx/CHUNK_W);
  var cz=Math.floor(wz/CHUNK_W);
  rebuildChunk(cx,cz);
  var lx=wx-cx*CHUNK_W;
  var lz=wz-cz*CHUNK_W;
  if(lx===0)rebuildChunk(cx-1,cz);
  if(lx===15)rebuildChunk(cx+1,cz);
  if(lz===0)rebuildChunk(cx,cz-1);
  if(lz===15)rebuildChunk(cx,cz+1);
}

// --- World Update ---
function updateWorld(){
  var pcx=Math.floor(player.x/CHUNK_W);
  var pcz=Math.floor(player.z/CHUNK_W);

  // Generate data (radius 5, max 4/frame)
  var genCands=[];
  for(var dx=-5;dx<=5;dx++){
    for(var dz=-5;dz<=5;dz++){
      var ccx=pcx+dx,ccz=pcz+dz;
      var ck=ccx+','+ccz;
      if(!chunks.has(ck)){
        genCands.push({cx:ccx,cz:ccz,key:ck,d:dx*dx+dz*dz});
      }
    }
  }
  genCands.sort(function(a,b){return a.d-b.d;});
  var genCount=0;
  for(var gi=0;gi<genCands.length&&genCount<4;gi++){
    var gc=genCands[gi];
    var gdata=generateChunkData(gc.cx,gc.cz);
    chunks.set(gc.key,{data:gdata,mesh:null});
    genCount++;
  }

  // Build meshes (radius 4, max 2/frame, neighbors must have data)
  var buildCands=[];
  for(var bx=-4;bx<=4;bx++){
    for(var bz=-4;bz<=4;bz++){
      var bcx=pcx+bcx2,bcz=pcz+bz;
      var bk=bcx+','+bcz;
      var bch=chunks.get(bk);
      if(!bch||!bch.data||bch.mesh)continue;
      var n1=chunks.get((bcx-1)+','+bcz);
      var n2=chunks.get((bcx+1)+','+bcz);
      var n3=chunks.get(bcx+','+(bcz-1));
      var n4=chunks.get(bcx+','+(bcz+1));
      if(!n1||!n2||!n3||!n4)continue;
      if(!n1.data||!n2.data||!n3.data||!n4.data)continue;
      buildCands.push({cx:bcx,cz:bcz,d:bx*bx+bz*bz});
    }
  }
  buildCands.sort(function(a,b){return a.d-b.d;});
  var buildCount=0;
  for(var bi=0;bi<buildCands.length&&buildCount<2;bi++){
    buildChunkMesh(buildCands[bi].cx,buildCands[bi].cz);
    buildCount++;
  }

  // Remove far chunks
  var toDel=[];
  for(var ek of chunks.keys()){
    var parts=ek.split(',');
    var ecx=parseInt(parts[0]),ec