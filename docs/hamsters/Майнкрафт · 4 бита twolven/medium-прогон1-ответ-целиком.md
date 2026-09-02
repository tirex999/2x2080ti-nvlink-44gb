

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MC</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000}
canvas{display:block}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:10}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:#fff;mix-blend-mode:difference}
#crosshair::before{width:2px;height:16px;top:-8px;left:-1px}
#crosshair::after{width:16px;height:2px;top:-1px;left:-8px}
#hotbar{position:fixed;bottom:8px;left:50%;transform:translateX(-50%);display:flex;gap:2px;background:rgba(0,0,0,.55);padding:3px;border-radius:4px;z-index:10}
.slot{width:44px;height:44px;border:2px solid #666;border-radius:2px;display:flex;align-items:flex-end;justify-content:flex-start;padding:2px;font:bold 11px monospace;color:rgba(255,255,255,.8);text-shadow:1px 1px 1px rgba(0,0,0,.7);user-select:none}
.slot.sel{border-color:#fff;border-width:3px}
#overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center;z-index:100;cursor:pointer}
.panel{text-align:center;color:#eee;font-family:'Courier New',monospace}
.panel h1{font-size:38px;margin-bottom:16px;color:#4caf50;text-shadow:2px 2px 0 #2e7d32}
.ctrl{font-size:14px;line-height:1.9;color:#bbb}
.play{margin-top:20px;font-size:18px;color:#ff9800;animation:pulse 1.2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay"><div class="panel">
<h1>&#9632; VOXELCRAFT &#9632;</h1>
<div class="ctrl">WASD — Move &nbsp;|&nbsp; Mouse — Look &nbsp;|&nbsp; Space — Jump<br>Left Click — Break &nbsp;|&nbsp; Right Click — Place<br>1–7 / Scroll — Select Block</div>
<div class="play">&#9654; Click to Play &#9664;</div>
</div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

/* ===== CONSTANTS ===== */
var CW=16,CH=80,CD=16;
var GEN_R=5,MESH_R=4,CLEAN_R=7;
var MAX_GEN=4,MAX_MSH=2;
var GRAV=25,JVEL=8.5,MSPEED=5.5;
var PHW=0.3,PH=1.8,EYE=1.62;
var RDIST=6;
var BCOL=[null,
  new THREE.Color(0x4caf50),new THREE.Color(0x795548),
  new THREE.Color(0x9e9e9e),new THREE.Color(0xe7d9a8),
  new THREE.Color(0x8d6e63),new THREE.Color(0x2e7d32),
  new THREE.Color(0xffffff)];
var FACES=[
  {d:[0,1,0],c:[[0,1,0],[1,1,0],[1,1,1],[0,1,1]],m:1.0},
  {d:[0,-1,0],c:[[0,0,1],[1,0,1],[1,0,0],[0,0,0]],m:0.55},
  {d:[1,0,0],c:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]],m:0.8},
  {d:[-1,0,0],c:[[0,0,1],[0,0,0],[0,1,0],[0,1,1]],m:0.8},
  {d:[0,0,1],c:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]],m:0.8},
  {d:[0,0,-1],c:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]],m:0.8}
];

/* ===== NOISE ===== */
function h2(x,z){
  var h=Math.imul(x,374761393)+Math.imul(z,668265263);
  h=Math.imul(h^(h>>>13),1274126177);
  h^=h>>>16;
  return(h>>>0)/4294967296;
}
function h3(x,y,z){
  var h=Math.imul(x,374761393)+Math.imul(y,668265263)+Math.imul(z,1440662683);
  h=Math.imul(h^(h>>>13),1274126177);
  h^=h>>>16;
  return(h>>>0)/4294967296;
}
function sst(t){return t*t*(3-2*t)}
function n2(x,z){
  var ix=Math.floor(x),iz=Math.floor(z);
  var fx=x-ix,fz=z-iz;
  var sx=sst(fx),sz=sst(fz);
  var a=h2(ix,iz),b=h2(ix+1,iz),c=h2(ix,iz+1),d=h2(ix+1,iz+1);
  var ab=a+(b-a)*sx,cd=c+(d-c)*sx;
  return ab+(cd-ab)*sz;
}
function fb2(x,z,oct){
  var v=0,a=1,f=1,t=0;
  for(var i=0;i<oct;i++){v+=n2(x*f,z*f)*a;t+=a;a*=.5;f*=2}
  return v/t;
}
function n3(x,y,z){
  var ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
  var fx=x-ix,fy=y-iy,fz=z-iz;
  var sx=sst(fx),sy=sst(fy),sz=sst(fz);
  var c000=h3(ix,iy,iz),c100=h3(ix+1,iy,iz),c010=h3(ix,iy+1,iz),c110=h3(ix+1,iy+1,iz);
  var c001=h3(ix,iy,iz+1),c101=h3(ix+1,iy,iz+1),c011=h3(ix,iy+1,iz+1),c111=h3(ix+1,iy+1,iz+1);
  var a0=c000+(c100-c000)*sx,a1=c010+(c110-c010)*sx;
  var b0=c001+(c101-c001)*sx,b1=c011+(c111-c011)*sx;
  var a=a0+(a1-a0)*sy,b=b0+(b1-b0)*sy;
  return a+(b-a)*sz;
}

/* ===== CHUNKS ===== */
var chunks=new Map();
var chunkMeshes=[];
var blockMat=new THREE.MeshLambertMaterial({vertexColors:true,color:0xffffff});

function ckKey(cx,cz){return cx+','+cz}
function getBlk(wx,wy,wz){
  if(wy<0||wy>=CH)return 0;
  var cx=Math.floor(wx/16),cz=Math.floor(wz/16);
  var lx=wx-cx*16,lz=wz-cz*16;
  var ch=chunks.get(ckKey(cx,cz));
  if(!ch)return 0;
  return ch.data[lx+lz*16+wy*256];
}
function setBlk(wx,wy,wz,id){
  if(wy<0||wy>=CH)return;
  var cx=Math.floor(wx/16),cz=Math.floor(wz/16);
  var lx=wx-cx*16,lz=wz-cz*16;
  var ch=chunks.get(ckKey(cx,cz));
  if(!ch)return;
  ch.data[lx+lz*16+wy*256]=id;
}

/* ===== TERRAIN ===== */
function colH(wx,wz){
  var m=fb2(wx*.004,wz*.004,4);
  var h=fb2(wx*.02,wz*.02,4);
  return Math.floor(5+m*m*58+h*10);
}
function genChunk(cx,cz){
  var data=new Uint8Array(CW*CD*CH);
  var wx0=cx*16,wz0=cz*16;
  for(var lz=0;lz<CD;lz++){
    for(var lx=0;lx<CW;lx++){
      var wx=wx0+lx,wz=wz0+lz;
      var H=colH(wx,wz);
      if(H>=CH)H=CH-1;
      if(H<1)H=1;
      var surf,surfSub;
      if(H>=46)surf=7;
      else if(H>=37)surf=3;
      else if(H<=16)surf=4;
      else surf=1;
      if(H<=16)surfSub=4;
      else if(H>=37)surfSub=3;
      else surfSub=2;
      for(var y=0;y<=H&&y<CH;y++){
        var idx=lx+lz*16+y*256;
        if(y===0){data[idx]=3;continue}
        if(y<H-3){data[idx]=3;continue}
        if(y<H){data[idx]=surfSub;continue}
        data[idx]=surf;
      }
      /* caves */
      for(var y2=3;y2<H-1&&y2<CH;y2++){
        var idx2=lx+lz*16+y2*256;
        if(data[idx2]!==0&&data[idx2]!==3){
          if(n3(wx*.09,y2*.09,wz*.09)>0.67)data[idx2]=0;
        }
      }
    }
  }
  /* trees */
  for(var tz=0;tz<CD;tz++){
    for(var tx=0;tx<CW;tx++){
      var twx=wx0+tx,twz=wz0+tz;
      var tH=colH(twx,twz);
      if(tH>=CH)tH=CH-1;
      var si=tx+tz*16+tH*256;
      if(data[si]!==1)continue;
      var th=twx*374761393+twz*668265263;
      th=Math.imul(th^(th>>>13),1274126177);
      th^=th>>>16;
      if(((th>>>0)/4294967296)>=0.02)continue;
      var baseY=tH+1,topY=baseY+3;
      if(topY+4>=CH)continue;
      if(tx<1||tx>CW-2||tz<1||tz>CD-2)continue;
      /* trunk */
      for(var ty=baseY;ty<=topY;ty++){
        data[tx+tz*16+ty*256]=5;
      }
      /* leaves: 5x5 two layers, 3x3 one layer, 1 on top */
      var ly1=topY+1,ly2=topY+2,ly3=topY+3,ly4=topY+4;
      function putLeaf(lx2,ly2b,lz2){
        if(lx2<0||lx2>=CW||lz2<0||lz2>=CD||ly2b<0||ly2b>=CH)return;
        var ii=lx2+lz2*16+ly2b*256;
        if(data[ii]===0)data[ii]=6;
      }
      for(var ox=-2;ox<=2;ox++)for(var oz=-2;oz<=2;oz++){
        putLeaf(tx+ox,ly1,tz+oz);
        putLeaf(tx+ox,ly2,tz+oz);
      }
      for(var ox2=-1;ox2<=1;ox2++)for(var oz2=-1;oz2<=1;oz2++){
        putLeaf(tx+ox2,ly3,tz+oz2);
      }
      putLeaf(tx,ly4,tz);
    }
  }
  var key=ckKey(cx,cz);
  chunks.set(key,{data:data,mesh:null});
}

/* ===== MESH BUILD ===== */
function buildMesh(cx,cz){
  var key=ckKey(cx,cz);
  var ch=chunks.get(key);
  if(!ch)return;
  if(ch.mesh){
    scene.remove(ch.mesh);
    ch.mesh.geometry.dispose();
    var mi=chunkMeshes.indexOf(ch.mesh);
    if(mi>=0)chunkMeshes.splice(mi,1);
    ch.mesh=null;
  }
  var pos=[],nor=[],col=[];
  var wx0=cx*16,wz0=cz*16;
  for(var ly=0;ly<CH;ly++){
    for(var lz=0;lz<CD;lz++){
      for(var lx=0;lx<CW;lx++){
        var bid=ch.data[lx+lz*16+ly*256];
        if(bid===0)continue;
        var bc=BCOL[bid];
        if(!bc)continue;
        var wx=wx0+lx,wy=ly,wz=wz0+lz;
        for(var fi=0;fi<6;fi++){
          var f=FACES[fi];
          var nx=wx+f.d[0],ny=wy+f.d[1],nz=wz+f.d[2];
          var nb=getBlk(nx,ny,nz);
          if(nb!==0)continue;
          var idx6=[0,1,2,0,2,3];
          for(var vi=0;vi<6;vi++){
            var ci=idx6[vi];
            var cr=f.c[ci];
            pos.push(wx+cr[0],wy+cr[1],wz+cr[2]);
            nor.push(f.d[0],f.d[1],f.d[2]);
            col.push(bc.r*f.m,bc.g*f.m,bc.b*f.m);
          }
        }
      }
    }
  }
  if(pos.length===0)return;
  var geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(nor,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  var mesh=new THREE.Mesh(geo,blockMat);
  scene.add(mesh);
  chunkMeshes.push(mesh);
  ch.mesh=mesh;
}
function rebuildChunk(cx,cz){
  var key=ckKey(cx,cz);
  var ch=chunks.get(key);
  if(!ch)return;
  buildMesh(cx,cz);
}

/* ===== CHUNK UPDATE ===== */
function updChunks(px,pz){
  var pcx=Math.floor(px/16),pcz=Math.floor(pz/16);
  /* cleanup far */
  var toDel=[];
  chunks.forEach(function(v,k){
    var parts=k.split(',');
    var cx=parseInt(parts[0]),cz=parseInt(parts[1]);
    var dx=Math.abs(cx-pcx),dz=Math.abs(cz-pcz);
    if(Math.max(dx,dz)>CLEAN_R)toDel.push(k);
  });
  for(var di=0;di<toDel.length;di++){
    var dk=toDel[di];
    var dv=chunks.get(dk);
    if(dv&&dv.mesh){
      scene.remove(dv.mesh);
      dv.mesh.geometry.dispose();
      var mi2=chunkMeshes.indexOf(dv.mesh);
      if(mi2>=0)chunkMeshes.splice(mi2,1);
    }
    chunks.delete(dk);
  }
  /* generate data */
  var genCount=0;
  for(var gz=pcz-GEN_R;gz<=pcz+GEN_R&&genCount<MAX_GEN;gz++){
    for(var gx=pcx-GEN_R;gx<=pcx+GEN_R&&genCount<MAX_GEN;gx++){
      var gd=ckKey(gx,gz);
      if(!chunks.has(gd)){
        genChunk(gx,gz);
        genCount++;
      }
    }
  }
  /* build meshes */
  var mshCount=0;
  for(var mz2=pcz-MESH_R;mz2<=pcz+MESH_R&&mshCount<MAX_MSH;mz2++){
    for(var mx2=pcx-MESH_R;mx2<=pcx+MESH_R&&mshCount<MAX_MSH;mx2++){
      var mk=ckKey(mx2,mz2);
      var mv=chunks.get(mk);
      if(!mv)continue;
      if(mv.mesh)continue;
      /* check 4 neighbors have data */
      if(!chunks.has(ckKey(mx2+1,mz2)))continue;
      if(!chunks.has(ckKey(mx2-1,mz2)))continue;
      if(!chunks.has(ckKey(mx2,mz2+1)))continue;
      if(!chunks.has(ckKey(mx2,mz2-1)))continue;
      buildMesh(mx2,mz2);
      mshCount++;
    }
  }
}

/* ===== SCENE ===== */
var renderer=new THREE.WebGLRenderer({antialias:false});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
document.body.appendChild(renderer.domElement);

var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);

var camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order='YXZ';

var ambL=new THREE.AmbientLight(0xffffff,0.65);
scene.add(ambL);
var sunL=new THREE.DirectionalLight(0xffffff,0.8);
sunL.position.set(100,200,50);
scene.add(sunL);

/* water */
var waterGeo=new THREE.PlaneGeometry(512,512);
waterGeo.rotateX(-Math.PI/2);
var waterMat=new THREE.MeshLambertMaterial({color:0x3366cc,transparent:true,opacity:0.55});
var waterPlane=new THREE.Mesh(waterGeo,waterMat);
waterPlane.position.y=14.3;
scene.add(waterPlane);

/* clouds */
var cloudMeshes=[];
(function(){
  var cm=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.8});
  for(var i=0;i<25;i++){
    var w=8+(i*7)%13;
    var d=5+(i*5)%8;
    var g=new THREE.BoxGeometry(w,1,d);
    var m=new THREE.Mesh(g,cm);
    m.position.set((i*37)%400-200,90,(i*23)%400-200);
    scene.add(m);
    cloudMeshes.push(m);
  }
})();

/* ===== PLAYER ===== */
var player={x:8,y:50,z:8,vx:0,vy:0,vz:0,onG:false};
var yaw=0,pitch=0;
function spawnH(){return colH(8,8)+2}
player.y=spawnH();

var keys={};
function chkCol(){
  var hw=PHW,h=PH;
  var px=player.x,py=player.y,pz=player.z;
  var mnX=Math.floor(px-hw),mxX=Math.floor(px+hw);
  var mnY=Math.floor(py),mxY=Math.floor(py+h);
  var mnZ=Math.floor(pz-hw),mxZ=Math.floor(pz+hw);
  for(var bx=mnX;bx<=mxX;bx++)
    for(var by=mnY;by<=mxY;by++)
      for(var bz=mnZ;bz<=mxZ;bz++)
        if(getBlk(bx,by,bz)!==0)return true;
  return false;
}
function updPlayer(dt){
  var mx=0,mz=0;
  if(keys.KeyW)mz-=1;
  if(keys.KeyS)mz+=1;
  if(keys.KeyA)mx-=1;
  if(keys.KeyD)mx+=1;
  var len=Math.sqrt(mx*mx+mz*mz);
  if(len>0){mx/=len;mz/=len}
  var sy=Math.sin(yaw),cy=Math.cos(yaw);
  var dx=(mx*cy-mz*sy)*MSPEED*dt;
  var dz=(mx*sy+mz*cy)*MSPEED*dt;
  player.vy-=GRAV*dt;
  var dy=player.vy*dt;
  /* X */
  player.x+=dx;
  if(chkCol())player.x-=dx;
  /* Y */
  player.y+=dy;
  player.onG=false;
  if(chkCol()){
    player.y-=dy;
    if(dy<0)player.onG=true;
    player.vy=0;
  }
  /* Z */
  player.z+=dz;
  if(chkCol())player.z-=dz;
  /* jump */
  if(keys.Space&&player.onG){
    player.vy=JVEL;
    player.onG=false;
  }
  /* fell off */
  if(player.y<-20){
    player.x=8;player.z=8;
    player.y=spawnH();
    player.vy=0;
  }
}

/* ===== RAYCAST / TARGET ===== */
var raycaster=new THREE.Raycaster();
raycaster.far=RDIST;
var ndcCenter=new THREE.Vector2(0,0);
var targetPos=null;

/* wireframe outline */
var wireGeo=new THREE.EdgesGeometry(new THREE.BoxGeometry(1.005,1.005,1.005));
var wireMat=new THREE.LineBasicMaterial({color:0x000000});
var wireBox=new THREE.LineSegments(wireGeo,wireMat);
wireBox.visible=false;
scene.add(wireBox);

function updTarget(){
  if(!locked){targetPos=null;wireBox.visible=false;return}
  raycaster.setFromCamera(ndcCenter,camera);
  var hits=raycaster.intersectObjects(chunkMeshes);
  if(hits.length>0){
    var p=hits[0].point;
    var n=hits[0].face.normal;
    /* break target */
    var bx=Math.floor(p.x-n.x*0.5);
    var by=Math.floor(p.y-n.y*0.5);
    var bz=Math.floor(p.z-n.z*0.5);
    targetPos={x:bx,y:by,z:bz};
    wireBox.visible=true;
    wireBox.position.set(bx+0.5,by+0.5,bz+0.5);
  }else{
    targetPos=null;
    wireBox.visible=false;
  }
}

/* ===== HOTBAR ===== */
var selSlot=0;
var hbBlocks=[1,2,3,4,5,6,7];
var hbColors=['#4caf50','#795548','#9e9e9e','#e7d9a8','#8d6e63','#2e7d32','#ffffff'];
var hbDiv=document.getElementById('hotbar');
var slotEls=[];
for(var hi=0;hi<7;hi++){
  var sl=document.createElement('div');
  sl.className='slot'+(hi===0?' sel':'');
  sl.style.background=hbColors[hi];
  sl.textContent=String(hi+1);
  hbDiv.appendChild(sl);
  slotEls.push(sl);
}
function setSel(i){
  selSlot=((i%7)+7)%7;
  for(var si=0;si<7;si++){
    if(si===selSlot)slotEls[si].className='slot sel';
    else slotEls[si].className='slot';
  }
}

/* ===== INPUT ===== */
var locked=false;
var overlay=document.getElementById('overlay');

overlay.addEventListener('click',function(){
  document.body.requestPointerLock();
});
document.addEventListener('pointerlockchange',function(){
  locked=document.pointerLockElement===document.body;
  overlay.style.display=locked?'none':'flex';
});
document.addEventListener('pointerlockerror',function(){
  overlay.style.display='flex';
});
document.addEventListener('mousemove',function(e){
  if(!locked)return;
  yaw-=e.movementX*0.002;
  pitch-=e.movementY*0.002;
  var lim=Math.PI/2-0.01;
  if(pitch>lim)pitch=lim;
  if(pitch<-lim)pitch=-lim;
});
document.addEventListener('mousedown',function(e){
  if(!locked)return;
  e.preventDefault();
  if(!targetPos)return;
  if(e.button===0){
    /* break */
    if(targetPos.y>0){
      setBlk(targetPos.x,targetPos.y,targetPos.z,0);
      editRebuild(targetPos.x,targetPos.z);
    }
  }else if(e.button===2){
    /* place */
    var pnx=targetPos.x+0, pny=targetPos.y+0, pnz=targetPos.z+0;
    /* compute place cell from raycast */
    raycaster.setFromCamera(ndcCenter,camera);
    var hits2=raycaster.intersectObjects(chunkMeshes);
    if(hits2.length>0){
      var pp=hits2[0].point;
      var pn=hits2[0].face.normal;
      var pcx=Math.floor(pp.x+pn.x*0.5);
      var pcy=Math.floor(pp.y+pn.y*0.5);
      var pcz=Math.floor(pp.z+pn.z*0.5);
      if(getBlk(pcx,pcy,pcz)===0){
        /* check doesn't overlap player */
        var overlapP=false;
        if(pcx===Math.floor(player.x-PHW)||pcx===Math.floor(player.x+PHW)){
          if(pcy>=Math.floor(player.y)&&pcy<=Math.floor(player.y+PH)){
            if(pcz===Math.floor(player.z-PHW)||pcz===Math.floor(player.z+PHW)){
              overlapP=true;
            }
          }
        }
        /* simpler overlap check */
        var pbl=PHW;
        var bMinX=pcx,bMaxX=pcx+1,bMinY=pcy,bMaxY=pcy+1,bMinZ=pcz,bMaxZ=pcz+1;
        var pMinX=player.x-pbl,pMaxX=player.x+pbl;
        var pMinY=player.y,pMaxY=player.y+PH;
        var pMinZ=player.z-pbl,pMaxZ=player.z+pbl;
        if(bMinX<pMaxX&&bMaxX>pMinX&&bMinY<pMaxY&&bMaxY>pMinY&&bMinZ<pMaxZ&&bMaxZ>pMinZ){
          overlapP=true;
        }
        if(!overlapP){
          setBlk(pcx,pcy,pcz,hbBlocks[selSlot]);
          editRebuild(pcx,pcz);
        }
      }
    }
  }
});
document.addEventListener('contextmenu',function(e){e.preventDefault()});
window.addEventListener('keydown',function(e){
  keys[e.code]=true;
  if(e.code==='Space')e.preventDefault();
  for(var ki=1;ki<=7;ki++){
    if(e.code==='Digit'+ki)setSel(ki-1);
  }
});
window.addEventListener('keyup',function(e){keys[e.code]=false});
window.addEventListener('wheel',function(e){
  if(!locked)return;
  if(e.deltaY>0)setSel(selSlot+1);
  else setSel(selSlot-1);
},{passive:true});

/* ===== EDIT REBUILD ===== */
function editRebuild(wx,wz){
  var cx=Math.floor(wx/16),cz=Math.floor(wz/16);
  var lx=wx-cx*16,lz=wz-cz*16;
  rebuildChunk(cx,cz);
  if(lx===0)rebuildChunk(cx-1,cz);
  if(lx===15)rebuildChunk(cx+1,cz);
  if(lz===0)rebuildChunk(cx,cz-1);
  if(lz===15)rebuildChunk(cx,cz+1);
}

/* ===== CLOUDS UPDATE ===== */
function updClouds(dt){
  for(var ci=0;ci<cloudMeshes.length;ci++){
    var cl=cloudMeshes[ci];
    cl.position.x+=0.5*dt;
    if(cl.position.x>player.x+200)cl.position.x=player.x-200;
    if(cl.position.x<player.x-200)cl.position.x=player.x+200;
  }
}

/* ===== RESIZE ===== */
window.addEventListener('resize',function(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});

/* ===== GAME LOOP ===== */
var lastT=0;
function animate(t){
  requestAnimationFrame(animate);
  var dt=Math.min((t-lastT)/1000,0.05);
  if(dt<=0)dt=0.016;
  lastT=t;

  updPlayer(dt);
  updChunks(player.x,player.z);
  updTarget();

  camera.position.set(player.x,player.y+EYE,player.z);
  camera.rotation.y=yaw;
  camera.rotation.x=pitch;

  waterPlane.position.x=player.x;
  waterPlane.position.z=player.z;

  updClouds(dt);

  renderer.render(scene,camera);
}

/* ===== INIT ===== */
requestAnimationFrame(animate);

})();
</script>
</body>
</html>
```