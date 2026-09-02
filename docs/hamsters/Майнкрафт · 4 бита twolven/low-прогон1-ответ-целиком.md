```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>VoxelCraft</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;font-family:Arial,sans-serif;background:#000}
canvas{display:block}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:10;width:20px;height:20px}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:rgba(255,255,255,0.8)}
#crosshair::before{width:2px;height:20px;left:9px;top:0}
#crosshair::after{width:20px;height:2px;left:0;top:9px}
#hotbar{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:2px;background:rgba(0,0,0,0.55);padding:4px;border-radius:4px;z-index:10}
.slot{width:48px;height:48px;display:flex;align-items:center;justify-content:center;border:2px solid #555;position:relative;background:rgba(0,0,0,0.3)}
.slot.selected{border-color:#fff}
.slot .num{position:absolute;top:1px;left:3px;font-size:10px;color:#ccc}
.slot .swatch{width:32px;height:32px;border:1px solid #333}
#overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.72);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:100;color:#fff}
#overlay h1{font-size:48px;margin-bottom:16px;text-shadow:0 2px 8px rgba(0,0,0,0.5)}
#overlay .ctrl{font-size:15px;line-height:1.9;margin-bottom:28px;text-align:center;opacity:0.9}
#overlay .go{font-size:22px;animation:pulse 1.4s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
<h1>&#x26CF; VoxelCraft</h1>
<div class="ctrl">
WASD Move &nbsp;&bull;&nbsp; Space Jump &nbsp;&bull;&nbsp; Mouse Look<br>
Left Click Break &nbsp;&bull;&nbsp; Right Click Place<br>
1&ndash;7 or Scroll &mdash; Select Block
</div>
<div class="go">Click to Play</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";

/* ===== CONSTANTS ===== */
var CHUNK_W=16,CHUNK_H=80;
var BLOCK_AIR=0,B_GRASS=1,B_DIRT=2,B_STONE=3,B_SAND=4,B_WOOD=5,B_LEAVES=6,B_SNOW=7;
var BLOCK_RGB={
1:[0.30,0.69,0.31],2:[0.47,0.33,0.28],3:[0.62,0.62,0.62],4:[0.91,0.85,0.66],
5:[0.55,0.43,0.39],6:[0.18,0.49,0.20],7:[1,1,1]
};
var HOTBAR=[B_GRASS,B_DIRT,B_STONE,B_SAND,B_WOOD,B_LEAVES,B_SNOW];
var HOTBAR_HEX=[0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
var P_HALF=0.3,P_H=1.8,EYE=1.62;
var GRAV=25,JUMP_V=8.5,WALK_SPD=5.5;
var REACH=6;

/* ===== FACE DATA ===== */
var FACES=[
{d:[0,1,0],v:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]],b:1.0},
{d:[0,-1,0],v:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]],b:0.55},
{d:[1,0,0],v:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]],b:0.8},
{d:[-1,0,0],v:[[0,0,1],[0,0,0],[0,1,0],[0,1,1]],b:0.8},
{d:[0,0,1],v:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]],b:0.8},
{d:[0,0,-1],v:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]],b:0.8}
];

/* ===== NOISE ===== */
function hash2(x,y){
var h=(x*374761393+y*668265263)|0;
h=((h^(h>>>13))*1274126177)|0;
h=(h^(h>>>16))|0;
return(h&0x7FFFFFFF)/0x7FFFFFFF;
}
function hash3(x,y,z){
var h=(x*374761393+y*668265263+z*2147483647)|0;
h=((h^(h>>>13))*1274126177)|0;
h=(h^(h>>>16))|0;
return(h&0x7FFFFFFF)/0x7FFFFFFF;
}
function noise2(x,y){
var ix=Math.floor(x),iy=Math.floor(y);
var fx=x-ix,fy=y-iy;
var sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy);
var v00=hash2(ix,iy),v10=hash2(ix+1,iy);
var v01=hash2(ix,iy+1),v11=hash2(ix+1,iy+1);
var a=v00+(v10-v00)*sx;
var b=v01+(v11-v01)*sx;
return a+(b-a)*sy;
}
function fractal2(x,y){
var v=0,a=1,f=1,mx=0;
for(var i=0;i<4;i++){v+=noise2(x*f,y*f)*a;mx+=a;a*=0.5;f*=2;}
return v/mx;
}
function noise3(x,y,z){
var ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
var fx=x-ix,fy=y-iy,fz=z-iz;
var sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy),sz=fz*fz*(3-2*fz);
var c000=hash3(ix,iy,iz),c100=hash3(ix+1,iy,iz);
var c010=hash3(ix,iy+1,iz),c110=hash3(ix+1,iy+1,iz);
var c001=hash3(ix,iy,iz+1),c101=hash3(ix+1,iy,iz+1);
var c011=hash3(ix,iy+1,iz+1),c111=hash3(ix+1,iy+1,iz+1);
var v00=c000+(c100-c000)*sx;
var v10=c010+(c110-c010)*sx;
var v01=c001+(c101-c001)*sx;
var v11=c011+(c111-c011)*sx;
var a=v00+(v10-v00)*sy;
var b=v01+(v11-v01)*sy;
return a+(b-a)*sz;
}

/* ===== CHUNK STORE ===== */
var chunks=new Map();
var chunkMeshList=[];
var sharedMat=null;

function chunkKey(cx,cz){return cx+','+cz;}

function getBlock(wx,wy,wz){
if(wy<0||wy>=CHUNK_H)return 0;
var cx=Math.floor(wx/16),cz=Math.floor(wz/16);
var ch=chunks.get(chunkKey(cx,cz));
if(!ch)return 0;
var lx=wx-cx*16,lz=wz-cz*16;
return ch.data[(wy*16+lz)*16+lx];
}
function setBlock(wx,wy,wz,id){
if(wy<0||wy>=CHUNK_H)return;
var cx=Math.floor(wx/16),cz=Math.floor(wz/16);
var ch=chunks.get(chunkKey(cx,cz));
if(!ch)return;
var lx=wx-cx*16,lz=wz-cz*16;
ch.data[(wy*16+lz)*16+lx]=id;
}

/* ===== TERRAIN GENERATION ===== */
function genChunkData(cx,cz){
var data=new Uint8Array(CHUNK_W*CHUNK_H*CHUNK_W);
for(var lx=0;lx<CHUNK_W;lx++){
for(var lz=0;lz<CHUNK_W;lz++){
var wx=cx*16+lx,wz=cz*16+lz;
var m=fractal2(wx*0.004,wz*0.004);
var h=fractal2(wx*0.02,wz*0.02);
var H=Math.floor(5+m*m*58+h*10);
if(H>79)H=79;
if(H<1)H=1;
for(var y=0;y<=H;y++){
var bl;
if(y===0)bl=B_STONE;
else if(y<H-3)bl=B_STONE;
else if(y<H){
if(H<=16)bl=B_SAND;
else if(H>=37)bl=B_STONE;
else bl=B_DIRT;
}else{
if(H>=46)bl=B_SNOW;
else if(H>=37)bl=B_STONE;
else if(H<=16)bl=B_SAND;
else bl=B_GRASS;
}
if(y>2&&y<H-1&&bl!==0){
if(noise3(wx*0.09,y*0.09,wz*0.09)>0.67)bl=0;
}
data[(y*16+lz)*16+lx]=bl;
}
/* Trees */
if(H>16&&H<37&&H+7<CHUNK_H){
if(data[(H*16+lz)*16+lx]===B_GRASS){
var th=hash2(wx*7+13,wz*7+29);
if(th<0.02){
for(var ty=1;ty<=4;ty++){
var yy=H+ty;
data[(yy*16+lz)*16+lx]=B_WOOD;
}
var layers=[
{dy:4,s:2},{dy:5,s:2},{dy:6,s:1},{dy:7,s:0}
];
for(var li=0;li<layers.length;li++){
var L=layers[li];
var ly2=H+L.dy;
if(ly2>=CHUNK_H)continue;
for(var dx=-L.s;dx<=L.s;dx++){
for(var dz2=-L.s;dz2<=L.s;dz2++){
var tx=lx+dx,tz=lz+dz2;
if(tx<0||tx>=CHUNK_W||tz<0||tz>=CHUNK_W)continue;
var idx=(ly2*16+tz)*16+tx;
if(data[idx]===0)data[idx]=B_LEAVES;
}
}
}
}
}
}
return data;
}

/* ===== MESH BUILDING ===== */
function buildChunkMesh(cx,cz){
var ch=chunks.get(chunkKey(cx,cz));
if(!ch)return;
var pos=[],nrm=[],col=[];
for(var lx=0;lx<CHUNK_W;lx++){
for(var lz=0;lz<CHUNK_W;lz++){
for(var ly=0;ly<CHUNK_H;ly++){
var bid=ch.data[(ly*16+lz)*16+lx];
if(bid===0)continue;
var wx=cx*16+lx,wy=ly,wz=cz*16+lz;
var bc=BLOCK_RGB[bid];
if(!bc)continue;
for(var fi=0;fi<6;fi++){
var F=FACES[fi];
var nx=wx+F.d[0],ny=wy+F.d[1],nz=wz+F.d[2];
var nid=getBlock(nx,ny,nz);
if(nid!==0)continue;
var v=F.v,b=F.b;
var cr=bc[0]*b,cg=bc[1]*b,cb=bc[2]*b;
var nr=F.d[0],ng=F.d[1],nb=F.d[2];
var tris=[[0,1,2],[0,2,3]];
for(var ti=0;ti<2;ti++){
var t=tris[ti];
for(var vi=0;vi<3;vi++){
var vv=t[vi];
pos.push(wx+v[vv][0],wy+v[vv][1],wz+v[vv][2]);
nrm.push(nr,ng,nb);
col.push(cr,cg,cb);
}
}
}
}
}
}
if(ch.mesh){removeChunkMesh(ch.mesh);ch.mesh=null;}
if(pos.length===0)return;
var geo=new THREE.BufferGeometry();
geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
geo.setAttribute('normal',new THREE.Float32BufferAttribute(nrm,3));
geo.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
ch.mesh=new THREE.Mesh(geo,sharedMat);
scene.add(ch.mesh);
chunkMeshList.push(ch.mesh);
}
function removeChunkMesh(m){
scene.remove(m);
m.geometry.dispose();
var i=chunkMeshList.indexOf(m);
if(i!==-1)chunkMeshList.splice(i,1);
}
function rebuildChunk(cx,cz){
var ch=chunks.get(chunkKey(cx,cz));
if(!ch)return;
if(ch.mesh){removeChunkMesh(ch.mesh);ch.mesh=null;}
buildChunkMesh(cx,cz);
}
function onBlockEdit(wx,wy,wz){
var cx=Math.floor(wx/16),cz=Math.floor(wz/16);
var lx=wx-cx*16,lz=wz-cz*16;
rebuildChunk(cx,cz);
if(lx===0)rebuildChunk(cx-1,cz);
if(lx===15)rebuildChunk(cx+1,cz);
if(lz===0)rebuildChunk(cx,cz-1);
if(lz===15)rebuildChunk(cx,cz+1);
if(lx===0&&lz===0)rebuildChunk(cx-1,cz-1);
if(lx===0&&lz===15)rebuildChunk(cx-1,cz+1);
if(lx===15&&lz===0)rebuildChunk(cx+1,cz-1);
if(lx===15&&lz===15)rebuildChunk(cx+1,cz+1);
}

/* ===== SCENE SETUP ===== */
var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);
var camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order='YXZ';
var renderer=new THREE.WebGLRenderer({antialias:false});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
document.body.insertBefore(renderer.domElement,document.body.firstChild);
var canvas=renderer.domElement;
scene.add(new THREE.AmbientLight(0xffffff,0.65));
var dl=new THREE.DirectionalLight(0xffffff,0.8);
dl.position.set(100,200,100);
scene.add(dl);
sharedMat=new THREE.MeshLambertMaterial({vertexColors:true});

/* ===== CLOUDS ===== */
var cloudGrp=new THREE.Group();
var cloudMat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.65});
for(var ci=0;ci<25;ci++){
var cw=10+hash2(ci,100)*18;
var cd=10+hash2(ci,200)*18;
var cg2=new THREE.BoxGeometry(cw,1.2,cd);
var cm=new THREE.Mesh(cg2,cloudMat);
cm.position.set((hash2(ci,300)-0.5)*220,88+hash2(ci,500)*6,(hash2(ci,400)-0.5)*220);
cloudGrp.add(cm);
}
scene.add(cloudGrp);

/* ===== WATER ===== */
var waterGeo=new THREE.PlaneGeometry(240,240);
waterGeo.rotateX(-Math.PI/2);
var waterMat=new THREE.MeshLambertMaterial({color:0x3388cc,transparent:true,opacity:0.55});
var waterPl=new THREE.Mesh(waterGeo,waterMat);
waterPl.position.y=14.3;
scene.add(waterPl);

/* ===== OUTLINE ===== */
var olGeo=new THREE.BoxGeometry(1.004,1.004,1.004);
var olMat=new THREE.MeshBasicMaterial({color:0x000000,wireframe:true});
var olMesh=new THREE.Mesh(olGeo,olMat);
olMesh.visible=false;
scene.add(olMesh);

/* ===== RAYCASTER ===== */
var raycaster=new THREE.Raycaster();
raycaster.far=REACH;
var centerVec=new THREE.Vector2(0,0);
var currentTarget=null;

function doRaycast(){
if(chunkMeshList.length===0){currentTarget=null;return;}
raycaster.setFromCamera(centerVec,camera);
var hits=raycaster.intersectObjects(chunkMeshList);
if(hits.length===0){currentTarget=null;return;}
var hit=hits[0];
var p=hit.point;
var n=hit.face.normal;
var bx=Math.floor(p.x-n.x*0.5);
var by=Math.floor(p.y-n.y*0.5);
var bz=Math.floor(p.z-n.z*0.5);
var px=Math.floor(p.x+n.x*0.5);
var py=Math.floor(p.y+n.y*0.5);
var pz=Math.floor(p.z+n.z*0.5);
currentTarget={brk:[bx,by,bz],plc:[px,py,pz]};
olMesh.visible=true;
olMesh.position.set(bx+0.5,by+0.5,bz+0.5);
}

/* ===== PLAYER ===== */
var player={x:8,y:50,z:8,vx:0,vy:0,vz:0,onG:false,yaw:0,pitch:0};
var keys={};

function findSpawnY(x,z){
for(var y=CHUNK_H-1;y>=0;y--){
if(getBlock(x,y,z)!==0)return y+1;
}
return 50;
}

function collides(px,py,pz){
var minX=Math.floor(px-P_HALF),maxX=Math.floor(px+P_HALF);
var minY=Math.floor(py),maxY=Math.floor(py+P_H);
var minZ=Math.floor(pz-P_HALF),maxZ=Math.floor(pz+P_HALF);
for(var bx=minX;bx<=maxX;bx++){
for(var by=minY;by<=maxY;by++){
for(var bz=minZ;bz<=maxZ;bz++){
if(getBlock(bx,by,bz)!==0)return true;
}
}
}
return false;
}

function updatePlayer(dt){
if(dt>0.1)dt=0.1;
var mx=0,mz=0;
if(keys['KeyW'])mz=-1;
if(keys['KeyS'])mz=1;
if(keys['KeyA'])mx=-1;
if(keys['KeyD'])mx=1;
var len=Math.sqrt(mx*mx+mz*mz);
if(len>0){mx/=len;mz/=len;}
var fwdX=-Math.sin(player.yaw),fwdZ=-Math.cos(player.yaw);
var rgtX=Math.cos(player.yaw),rgtZ=-Math.sin(player.yaw);
player.vx=(fwdX*(-mz)+rgtX*mx)*WALK_SPD;
player.vz=(fwdZ*(-mz)+rgtZ*mx)*WALK_SPD;
player.vy-=GRAV*dt;
if(keys['Space']&&player.onG){
player.vy=JUMP_V;
player.onG=false;
}
/* X */
player.x+=player.vx*dt;
if(collides(player.x,player.y,player.z)){
player.x-=player.vx*dt;
player.vx=0;
}
/* Z */
player.z+=player.vz*dt;
if(collides(player.x,player.y,player.z)){
player.z-=player.vz*dt;
player.vz=0;
}
/* Y */
player.y+=player.vy*dt;
if(collides(player.x,player.y,player.z)){
player.y-=player.vy*dt;
if(player.vy<0)player.onG=true;
player.vy=0;
}else{
player.onG=false;
}
if(player.y<-20){
player.x=8;player.y=findSpawnY(8,8)||50;player.z=8;
player.vx=player.vy=player.vz=0;
}
camera.position.set(player.x,player.y+EYE,player.z);
camera.rotation.set(player.pitch,player.yaw,0);
}

/* ===== CHUNK UPDATE ===== */
function updateChunks(){
var pcx=Math.floor(player.x/16),pcz=Math.floor(player.z/16);
var genC=0;
for(var dx=-5;dx<=5&&genC<4;dx++){
for(var dz=-5;dz<=5&&genC<4;dz++){
var cx=pcx+dx,cz=pcz+dz;
var k=chunkKey(cx,cz);
if(chunks.has(k))continue;
chunks.set(k,{data:genChunkData(cx,cz),mesh:null});
genC++;
}
}
var meshC=0;
for(var dx2=-4;dx2<=4&&meshC<2;dx2++){
for(var dz2=-4;dz2<=4&&meshC<2;dz2++){
var cx2=pcx+dx2,cz2=pcz+dz2;
var k2=chunkKey(cx2,cz2);
var ch2=chunks.get(k2);
if(!ch2||ch2.mesh)continue;
var nbrs=[[cx2+1,cz2],[cx2-1,cz2],[cx2,cz2+1],[cx2,cz2-1]];
var ok=true;
for(var ni=0;ni<4;ni++){
if(!chunks.has(chunkKey(nbrs[ni][0],nbrs[ni][1])){ok=false;break;}
}
if(!ok)continue;
buildChunkMesh(cx2,cz2);
meshC++;
}
}
var arr=Array.from(chunks.keys());
for(var ri=0;ri<arr.length;ri++){
var parts=arr[ri].split(',');
var rcx=parseInt(parts[0]),rcz=parseInt(parts[1]);
var d=Math.max(Math.abs(rcx-pcx),Math.abs(rcz-pcz));
if(d>7){
var rc=chunks.get(arr[ri]);
if(rc.mesh){removeChunkMesh(rc.mesh);rc.mesh=null;}
chunks.delete(arr[ri]);
}
}
}

/* ===== HOTBAR ===== */
var selSlot=0;
function buildHotbar(){
var bar=document.getElementById('hotbar');
bar.innerHTML='';
for(var i=0;i<7;i++){
var s=document.createElement('div');
s.className='slot'+(i===selSlot?' selected':'');
var n=document.createElement('span');
n.className='num';n.textContent=i+1;
s.appendChild(n);
var sw=document.createElement('div');
sw.className='swatch';
sw.style.backgroundColor='#'+HOTBAR_HEX[i].toString(16).padStart(6,'0');
s.appendChild(sw);
bar.appendChild(s);
}
}
function selSlotFn(i){
selSlot=((i%7)+7)%7;
buildHotbar();
}

/* ===== EVENTS ===== */
document.addEventListener('keydown',function(e){
keys[e.code]=true;
if(e.code==='Space')e.preventDefault();
var dm=e.code.match(/^Digit([1-7])$/);
if(dm)selSlotFn(parseInt(dm[1])-1);
});
document.addEventListener('keyup',function(e){keys[e.code]=false;});

document.addEventListener('mousemove',function(e){
if(document.pointerLockElement!==canvas)return;
player.yaw-=e.movementX*0.002;
player.pitch-=e.movementY*0.002;
var lim=Math.PI/2-0.01;
player.pitch=Math.max(-lim,Math.min(lim,player.pitch));
});

document.addEventListener('mousedown',function(e){
if(document.pointerLockElement!==canvas)return;
if(!currentTarget)return;
if(e.button===0){
var b=currentTarget.brk;
if(b[1]>0){
setBlock(b[0],b[1],b[2],0);
onBlockEdit(b[0],b[1],b[2]);
}
}else if(e.button===2){
var p=currentTarget.plc;
if(getBlock(p[0],p[1],p[2])===0){
var bmn=p[0],bmx=p[0]+1,bmy=p[1],bmy2=p[1]+1,bmz=p[2],bmz2=p[2]+1;
var pmn=player.x-P_HALF,pmx=player.x+P_HALF,pmy=player.y,pmy2=player.y+P_H,pmz=player.z-P_HALF,pmz2=player.z+P_H;
if(!(bmx>pmn&&bmn<pmx&&bmy2>pmy&&bmy<pmy2&&bmz2>pmz&&bmz<pmz2)){
setBlock(p[0],p[1],p[2],HOTBAR[selSlot]);
onBlockEdit(p[0],p[1],p[2]);
}
}
}
});
document.addEventListener('contextmenu',function(e){e.preventDefault();});
document.addEventListener('wheel',function(e){
if(document.pointerLockElement!==canvas)return;
selSlotFn(selSlot+(e.deltaY>0?1:-1));
},{passive:true});

/* Pointer lock */
var overlay=document.getElementById('overlay');
overlay.addEventListener('click',function(){
canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange',function(){
if(document.pointerLockElement===canvas){
overlay.style.display='none';
}else{
overlay.style.display='flex';
}
});

/* Resize */
window.addEventListener('resize',function(){
camera.aspect=window.innerWidth/window.innerHeight;
camera.updateProjectionMatrix();
renderer.setSize(window.innerWidth,window.innerHeight);
});

/* ===== INIT ===== */
buildHotbar();
/* Pre-generate spawn chunks */
var spcx=Math.floor(8/16),spcz=Math.floor(8/16);
var initKeys=[];
for(var ix=-1;ix<=1;ix++)for(var iz=-1;iz<=1;iz++)initKeys.push([spcx+ix,spcz+iz]);
for(var ii=0;ii<initKeys.length;ii++){
var ik=chunkKey(initKeys[ii][0],initKeys[ii][1]);
if(!chunks.has(ik))chunks.set(ik,{data:genChunkData(initKeys[ii][0],initKeys[ii][1]),mesh:null});
}
player.y=findSpawnY(8,8);
if(player.y<1)player.y=50;

/* ===== MAIN LOOP ===== */
var lastT=performance.now();
function loop(now){
requestAnimationFrame(loop);
var dt=(now-lastT)/1000;
lastT=now;
if(dt>0.25)dt=0.25;
updateChunks();
updatePlayer(dt);
doRaycast();
/* Clouds */
for(var cc=0;cc<cloudGrp.children.length;cc++){
var cl=cloudGrp.children[cc];
cl.position.x+=1.2*dt;
var cdx=cl.position.x-player.x;
var cdz=cl.position.z-player.z;
if(cdx>110)cl.position.x-=220;
if(cdx<-110)cl.position.x+=220;
if(cdz>110)cl.position.z-=220;
if(cdz<-110)cl.position.z+=220;
}
/* Water */
waterPl.position.x=player.x;
waterPl.position.z=player.z;
renderer.render(scene,camera);
}
requestAnimationFrame(loop);
})();
</script>
</body>
</html>
```