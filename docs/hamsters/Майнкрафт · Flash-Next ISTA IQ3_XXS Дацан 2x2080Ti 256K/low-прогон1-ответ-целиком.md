```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Voxel World</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000;font-family:monospace}
canvas{display:block;width:100vw;height:100vh}
#overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:10;color:#fff;text-align:center;flex-direction:column}
#overlay h1{font-size:2em;margin-bottom:16px}
#overlay p{font-size:1em;line-height:1.8;max-width:400px}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:5;color:#fff;font-size:24px;text-shadow:0 0 2px #000;display:none}
#hotbar{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:4px;background:rgba(0,0,0,0.6);padding:6px;border-radius:4px;z-index:5;display:none}
.slot{width:48px;height:48px;display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;border:2px solid transparent;border-radius:3px;cursor:pointer}
.slot.sel{border-color:#fff}
</style>
</head>
<body>
<div id="overlay"><h1>Voxel World</h1><p>WASD – Move<br>Space – Jump<br>Mouse – Look<br>Left Click – Break<br>Right Click – Place<br>1-7 / Scroll – Select Block<br><br>Click to Play</p></div>
<div id="crosshair">+</div>
<div id="hotbar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
const CHUNK_SIZE=16,CHUNK_HEIGHT=80,RENDER_DIST=4,GEN_DIST=5,CLEANUP_DIST=7;
const BLOCK_COLORS=[0,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
const BLOCK_NAMES=['Air','Grass','Dirt','Stone','Sand','Wood','Leaves','Snow'];

// Scene setup
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);
const camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order='YXZ';
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth,window.innerHeight);
document.body.appendChild(renderer.domElement);

// Lights
scene.add(new THREE.AmbientLight(0xffffff,0.65));
const dirLight=new THREE.DirectionalLight(0xffffff,0.8);
dirLight.position.set(1,2,1);
scene.add(dirLight);

// Shared material
const blockMaterial=new THREE.MeshLambertMaterial({vertexColors:true});

// Chunk storage
const chunks=new Map();
const chunkMeshes=[];

// Player state
let px=8,pz=8,py=40;
let vy=0,onGround=false;
let yaw=0,pitch=0;
let selectedBlock=1;
let pointerLocked=false;
let keys={};

// Outline box
const outlineGeo=new THREE.BoxGeometry(1.005,1.005,1.005);
const outlineEdges=new THREE.EdgesGeometry(outlineGeo);
const outlineLine=new THREE.LineSegments(outlineEdges,new THREE.LineBasicMaterial({color:0x000000}));
outlineLine.visible=false;
scene.add(outlineLine);

// Water plane
const waterGeo=new THREE.PlaneGeometry(200,200);
waterGeo.rotateX(-Math.PI/2);
const waterMat=new THREE.MeshBasicMaterial({color:0x3388cc,transparent:true,opacity:0.5});
const waterMesh=new THREE.Mesh(waterGeo,waterMat);
waterMesh.position.y=14.3;
scene.add(waterMesh);

// Clouds
const clouds=[];
for(let i=0;i<25;i++){
  const w=8+Math.random()*12;
  const d=6+Math.random()*8;
  const h=1+Math.random()*1.5;
  const geo=new THREE.BoxGeometry(w,h,d);
  const mat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.7});
  const mesh=new THREE.Mesh(geo,mat);
  mesh.position.set((Math.random()-0.5)*120,88+Math.random()*8,(Math.random()-0.5)*120);
  scene.add(mesh);
  clouds.push({mesh,speed:0.3+Math.random()*0.4});
}

// Noise functions
function ihash(x,y,z){
  let h=x*374761393+y*668265263+z*1274126177;
  h=((h^(h>>13))*1274126177)|0;
  h=((h^(h>>16))&0x7fffffff);
  return h/2147483647;
}
function smoothstep(t){return t*t*(3-2*t);}
function lerp(a,b,t){return a+(b-a)*t;}
function noise2D(x,y){
  const x0=Math.floor(x),x1=x0+1,y0=Math.floor(y),y1=y0+1;
  const sx=smoothstep(x-x0),sy=smoothstep(y-y0);
  return lerp(lerp(ihash(x0,y0,0),ihash(x1,y0,0),sx),lerp(ihash(x0,y1,0),ihash(x1,y1,0),sx),sy);
}
function fractal2D(x,y){
  let val=0,amp=0.5,freq=1;
  for(let i=0;i<4;i++){val+=amp*noise2D(x*freq,y*freq);amp*=0.5;freq*=2;}
  return val;
}
function noise3D(x,y,z){
  const x0=Math.floor(x),y0=Math.floor(y),z0=Math.floor(z);
  const x1=x0+1,y1=y0+1,z1=z0+1;
  const sx=smoothstep(x-x0),sy=smoothstep(y-y0),sz=smoothstep(z-z0);
  const v000=ihash(x0,y0,z0),v100=ihash(x1,y0,z0),v010=ihash(x0,y1,z0),v110=ihash(x1,y1,z0);
  const v001=ihash(x0,y0,z1),v101=ihash(x1,y0,z1),v011=ihash(x0,y1,z1),v111=ihash(x1,y1,z1);
  return lerp(lerp(lerp(v000,v100,sx),lerp(v010,v110,sx),sy),lerp(lerp(v001,v101,sx),lerp(v011,v111,sx),sy),sz);
}
function fractal3D(x,y,z){
  let val=0,amp=0.5,freq=1;
  for(let i=0;i<3;i++){val+=amp*noise3D(x*freq,y*freq,z*freq);amp*=0.5;freq*=2;}
  return val;
}

// Block access helpers
function getBlock(wx,wy,wz){
  if(wy<0||wy>=CHUNK_HEIGHT)return 0;
  const cx=Math.floor(wx/CHUNK_SIZE),cz=Math.floor(wz/CHUNK_SIZE);
  const key=cx+','+cz;
  const chunk=chunks.get(key);
  if(!chunk)return 0;
  const lx=wx-cx*CHUNK_SIZE,lz=wz-cz*CHUNK_SIZE;
  return chunk.data[lx+lz*CHUNK_SIZE+wy*CHUNK_SIZE*CHUNK_SIZE];
}
function setBlock(wx,wy,wz,val){
  if(wy<0||wy>=CHUNK_HEIGHT)return;
  const cx=Math.floor(wx/CHUNK_SIZE),cz=Math.floor(wz/CHUNK_SIZE);
  const key=cx+','+cz;
  const chunk=chunks.get(key);
  if(!chunk)return;
  const lx=wx-cx*CHUNK_SIZE,lz=wz-cz*CHUNK_SIZE;
  chunk.data[lx+lz*CHUNK_SIZE+wy*CHUNK_SIZE*CHUNK_SIZE]=val;
}

// Terrain generation for a chunk
function generateChunk(cx,cz){
  const key=cx+','+cz;
  if(chunks.has(key))return;
  const data=new Uint8Array(CHUNK_SIZE*CHUNK_SIZE*CHUNK_HEIGHT);
  const CS2=CHUNK_SIZE*CHUNK_SIZE;
  for(let lx=0;lx<CHUNK_SIZE;lx++){
    for(let lz=0;lz<CHUNK_SIZE;lz++){
      const wx=cx*CHUNK_SIZE+lx,wz=cz*CHUNK_SIZE+lz;
      const m=fractal2D(wx*0.004,wz*0.004);
      const h=fractal2D(wx*0.02,wz*0.02);
      const H=Math.floor(5+m*m*58+h*10);
      const treeHash=ihash(wx,0,wz);
      for(let y=0;y<CHUNK_HEIGHT;y++){
        let block=0;
        if(y===0){block=3;}
        else if(y<H-3){block=3;}
        else if(y<H){
          if(H<=16)block=4;else if(H>=37)block=3;else block=2;
        }else if(y===H){
          if(H>=46)block=7;else if(H>=37)block=3;else if(H<=16)block=4;else block=1;
        }
        // Caves
        if(block!==0&&y>=3&&y<=H-2){
          const caveVal=noise3D(wx*0.09,y*0.09,wz*0.09);
          if(caveVal>0.67)block=0;
        }
        data[lx+lz*CHUNK_SIZE+y*CS2]=block;
      }
      // Trees
      if(treeHash<0.02&&H>=17&&H<37){
        const surfaceBlock=data[lx+lz*CHUNK_SIZE+H*CS2];
        if(surfaceBlock===1){
          const trunkHeight=4;
          if(H+trunkHeight+5<CHUNK_HEIGHT){
            for(let ty=1;ty<=trunkHeight;ty++){
              data[lx+lz*CHUNK_SIZE+(H+ty)*CS2]=5;
            }
            const leafStart=H+trunkHeight-1;
            for(let ly=0;ly<2;ly++){
              const yy=leafStart+ly;
              for(let dx=-2;dx<=2;dx++){
                for(let dz=-2;dz<=2;dz++){
                  const nlx=lx+dx,nlz=lz+dz;
                  if(nlx>=0&&nlx<CHUNK_SIZE&&nlz>=0&&nlz<CHUNK_SIZE){
                    const idx=nlx+nlz*CHUNK_SIZE+yy*CS2;
                    if(data[idx]===0)data[idx]=6;
                  }
                }
              }
            }
            const yy3=leafStart+2;
            for(let dx=-1;dx<=1;dx++){
              for(let dz=-1;dz<=1;dz++){
                const nlx=lx+dx,nlz=lz+dz;
                if(nlx>=0&&nlx<CHUNK_SIZE&&nlz>=0&&nlz<CHUNK_SIZE){
                  const idx=nlx+nlz*CHUNK_SIZE+yy3*CS2;
                  if(data[idx]===0)data[idx]=6;
                }
              }
            }
            const yy4=leafStart+3;
            const idx4=lx+lz*CHUNK_SIZE+yy4*CS2;
            if(data[idx4]===0)data[idx4]=6;
          }
        }
      }
    }
  }
  chunks.set(key,{data,mesh:null,generated:true});
}

// Face definitions
const FACES=[
  {dir:[1,0,0],corners:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]],normal:[1,0,0]},
  {dir:[-1,0,0],corners:[[0,0,1],[0,0,0],[0,1,0],[0,1,1]],normal:[-1,0,0]},
  {dir:[0,1,0],corners:[[0,1,1],[0,1,0],[1,1,0],[1,1,1]],normal:[0,1,0]},
  {dir:[0,-1,0],corners:[[0,0,0],[0,0,1],[1,0,1],[1,0,0]],normal:[0,-1,0]},
  {dir:[0,0,1],corners:[[1,0,1],[0,0,1],[0,1,1],[1,1,1]],normal:[0,0,1]},
  {dir:[0,0,-1],corners:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]],normal:[0,0,-1]}
];

// Build chunk mesh
function buildChunkMesh(cx,cz){
  const key=cx+','+cz;
  const chunk=chunks.get(key);
  if(!chunk||!chunk.generated)return;
  if(chunk.mesh){
    scene.remove(chunk.mesh);
    chunk.mesh.geometry.dispose();
    const idx=chunkMeshes.indexOf(chunk.mesh);
    if(idx>=0)chunkMeshes.splice(idx,1);
  }
  const positions=[],normals=[],colors=[];
  const CS2=CHUNK_SIZE*CHUNK_SIZE;
  for(let lx=0;lx<CHUNK_SIZE;lx++){
    for(let lz=0;lz<CHUNK_SIZE;lz++){
      for(let y=0;y<CHUNK_HEIGHT;y++){
        const blockId=chunk.data[lx+lz*CHUNK_SIZE+y*CS2];
        if(blockId===0)continue;
        const wx=cx*CHUNK_SIZE+lx,wz=cz*CHUNK_SIZE+lz;
        const baseColor=BLOCK_COLORS[blockId];
        const r=(baseColor>>16&0xff)/255;
        const g=(baseColor>>8&0xff)/255;
        const b=(baseColor&0xff)/255;
        for(let fi=0;fi<6;fi++){
          const face=FACES[fi];
          const nx=wx+face.dir[0],ny=y+face.dir[1],nz=wz+face.dir[2];
          if(getBlock(nx,ny,nz)!==0)continue;
          const n=face.normal;
          let mult=0.8;
          if(n[1]>0)mult=1.0;
          else if(n[1]<0)mult=0.55;
          const cr=r*mult,cg=g*mult,cb=b*mult;
          const c=face.corners;
          const verts=[
            [wx+c[0][0],y+c[0][1],wz+c[0][2]],
            [wx+c[1][0],y+c[1][1],wz+c[1][2]],
            [wx+c[2][0],y+c[2][1],wz+c[2][2]],
            [wx+c[3][0],y+c[3][1],wz+c[3][2]]
          ];
          const triIndices=[0,1,2,0,2,3];
          for(let ti=0;ti<6;ti++){
            const v=verts[triIndices[ti]];
            positions.push(v[0],v[1],v[2]);
            normals.push(n[0],n[1],n[2]);
            colors.push(cr,cg,cb);
          }
        }
      }
    }
  }
  if(positions.length===0){chunk.mesh=null;return;}
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  const mesh=new THREE.Mesh(geo,blockMaterial);
  scene.add(mesh);
  chunk.mesh=mesh;
  chunkMeshes.push(mesh);
}

// Rebuild a specific chunk
function rebuildChunk(cx,cz){
  buildChunkMesh(cx,cz);
}

// Chunk management per frame
let genQueue=[],meshQueue=[];
function updateChunks(){
  const pcx=Math.floor(px/CHUNK_SIZE),pcz=Math.floor(pz/CHUNK_SIZE);
  // Generate
  genQueue=[];
  for(let dx=-GEN_DIST;dx<=GEN_DIST;dx++){
    for(let dz=-GEN_DIST;dz<=GEN_DIST;dz++){
      const cx=pcx+dx,cz=pcz+dz;
      const key=cx+','+cz;
      if(!chunks.has(key)){genQueue.push([cx,cz]);}
    }
  }
  genQueue.sort((a,b)=>{
    const da=(a[0]-pcx)*(a[0]-pcx)+(a[1]-pcz)*(a[1]-pcz);
    const db=(b[0]-pcx)*(b[0]-pcx)+(b[1]-pcz)*(b[1]-pcz);
    return da-db;
  });
  let genCount=0;
  for(const[cx,cz] of genQueue){
    if(genCount>=4)break;
    generateChunk(cx,cz);
    genCount++;
  }
  // Mesh
  meshQueue=[];
  for(let dx=-RENDER_DIST;dx<=RENDER_DIST;dx++){
    for(let dz=-RENDER_DIST;dz<=RENDER_DIST;dz++){
      const cx=pcx+dx,cz=pcz+dz;
      const key=cx+','+cz;
      const chunk=chunks.get(key);
      if(!chunk||!chunk.generated)continue;
      if(chunk.mesh!==null)continue;
      // Check all 4 neighbors have data
      const n1=chunks.get((cx-1)+','+cz);
      const n2=chunks.get((cx+1)+','+cz);
      const n3=chunks.get(cx+','+(cz-1));
      const n4=chunks.get(cx+','+(cz+1));
      if(!n1||!n1.generated)continue;
      if(!n2||!n2.generated)continue;
      if(!n3||!n3.generated)continue;
      if(!n4||!n4.generated)continue;
      meshQueue.push([cx,cz]);
    }
  }
  meshQueue.sort((a,b)=>{
    const da=(a[0]-pcx)*(a[0]-pcx)+(a[1]-pcz)*(a[1]-pcz);
    const db=(b[0]-pcx)*(b[0]-pcx)+(b[1]-pcz)*(b[1]-pcz);
    return da-db;
  });
  let meshCount=0;
  for(const[cx,cz] of meshQueue){
    if(meshCount>=2)break;
    buildChunkMesh(cx,cz);
    meshCount++;
  }
  // Cleanup
  for(const[key,chunk] of chunks){
    const parts=key.split(',');
    const cx=parseInt(parts[0]),cz=parseInt(parts[1]);
    const dx=Math.abs(cx-pcx),dz=Math.abs(cz-pcz);
    if(dx>CLEANUP_DIST||dz>CLEANUP_DIST){
      if(chunk.mesh){
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        const idx=chunkMeshes.indexOf(chunk.mesh);
        if(idx>=0)chunkMeshes.splice(idx,1);
      }
      chunks.delete(key);
    }
  }
}

// Spawn player
function findSpawnHeight(x,z){
  for(let y=CHUNK_HEIGHT-1;y>=0;y--){
    const cx=Math.floor(x/CHUNK_SIZE),cz=Math.floor(z/CHUNK_SIZE);
    const key=cx+','+cz;
    const chunk=chunks.get(key);
    if(!chunk)continue;
    const lx=x-cx*CHUNK_SIZE,lz=z-cz*CHUNK_SIZE;
    if(chunk.data[lx+lz*CHUNK_SIZE+y*CHUNK_SIZE*CHUNK_SIZE]!==0)return y+1;
  }
  return 40;
}

// Collision check
function collidesAt(x,y,z){
  const hw=0.3,hh=1.8;
  const minX=x-hw,maxX=x+hw,minY=y,maxY=y+hh,minZ=z-hw,maxZ=z+hw;
  const bx0=Math.floor(minX),bx1=Math.floor(maxX);
  const by0=Math.floor(minY),by1=Math.floor(maxY);
  const bz0=Math.floor(minZ),bz1=Math.floor(maxZ);
  for(let bx=bx0;bx<=bx1;bx++){
    for(let by=by0;by<=by1;by++){
      for(let bz=bz0;bz<=bz1;bz++){
        if(getBlock(bx,by,bz)!==0)return true;
      }
    }
  }
  return false;
}

// Player physics
function updatePlayer(dt){
  if(dt>0.1)dt=0.1;
  const speed=5.5;
  let mx=0,mz=0;
  if(keys['KeyW'])mz-=1;
  if(keys['KeyS'])mz+=1;
  if(keys['KeyA'])mx-=1;
  if(keys['KeyD'])mx+=1;
  const sinY=Math.sin(yaw),cosY=Math.cos(yaw);
  const moveX=(mx*cosY-mz*sinY)*speed*dt;
  const moveZ=(mx*sinY+mz*cosY)*speed*dt;
  // X axis
  if(moveX!==0){
    const oldX=px;
    px+=moveX;
    if(collidesAt(px,py,pz)){px=oldX;}
  }
  // Z axis
  if(moveZ!==0){
    const oldZ=pz;
    pz+=moveZ;
    if(collidesAt(px,py,pz)){pz=oldZ;}
  }
  // Y axis
  vy-=25*dt;
  if(keys['Space']&&onGround){vy=8.5;onGround=false;}
  const oldY=py;
  py+=vy*dt;
  if(collidesAt(px,py,pz)){
    py=oldY;
    if(vy<0)onGround=true;
    vy=0;
  }else{
    onGround=false;
  }
  // Fall below world
  if(py<-20){px=8;py=findSpawnHeight(8,8);pz=8;vy=0;}
  camera.position.set(px,py+1.62,pz);
}

// Raycasting & interaction
const raycaster=new THREE.Raycaster();
raycaster.far=6;
let targetBlock=null;

function doRaycast(){
  raycaster.setFromCamera(new THREE.Vector2(0,0),camera);
  const hits=raycaster.intersectObjects(chunkMeshes);
  targetBlock=null;
  if(hits.length>0){
    const hit=hits[0];
    const p=hit.point;
    const n=hit.face.normal;
    const bx=Math.floor(p.x-n.x*0.5);
    const by=Math.floor(p.y-n.y*0.5);
    const bz=Math.floor(p.z-n.z*0.5);
    targetBlock={x:bx,y:by,z:bz,px:p.x+n.x*0.5,py:p.y+n.y*0.5,pz:p.z+n.z*0.5};
    outlineLine.visible=true;
    outlineLine.position.set(bx+0.5,by+0.5,bz+0.5);
  }else{
    outlineLine.visible=false;
  }
}

function breakBlock(){
  if(!targetBlock)return;
  if(targetBlock.y===0)return;
  const{x,y,z}=targetBlock;
  setBlock(x,y,z,0);
  const cx=Math.floor(x/CHUNK_SIZE),cz=Math.floor(z/CHUNK_SIZE);
  rebuildChunk(cx,cz);
  const lx=x-cx*CHUNK_SIZE,lz=z-cz*CHUNK_SIZE;
  if(lx===0)rebuildChunk(cx-1,cz);
  if(lx===CHUNK_SIZE-1)rebuildChunk(cx+1,cz);
  if(lz===0)rebuildChunk(cx,cz-1);
  if(lz===CHUNK_SIZE-1)rebuildChunk(cx,cz+1);
}

function placeBlock(){
  if(!targetBlock)return;
  const{x,y,z}=targetBlock;
  const px2=Math.floor(targetBlock.px),py2=Math.floor(targetBlock.py),pz2=Math.floor(targetBlock.pz);
  if(getBlock(px2,py2,pz2)!==0)return;
  // Check player overlap
  const hw=0.3,hh=1.8;
  const blockMinX=px2,blockMaxX=px2+1,blockMinY=py2,blockMaxY=py2+1,blockMinZ=pz2,blockMaxZ=pz2+1;
  const playerMinX=px-hw,playerMaxX=px+hw,playerMinY=py,playerMaxY=py+hh,playerMinZ=pz-hw,playerMaxZ=pz+hw;
  if(blockMinX<playerMaxX&&blockMaxX>playerMinX&&blockMinY<playerMaxY&&blockMaxY>playerMinY&&blockMinZ<playerMaxZ&&blockMaxZ>playerMinZ)return;
  setBlock(px2,py2,pz2,selectedBlock);
  const cx=Math.floor(px2/CHUNK_SIZE),cz=Math.floor(pz2/CHUNK_SIZE);
  rebuildChunk(cx,cz);
  const lx2=px2-cx*CHUNK_SIZE,lz2=pz2-cz*CHUNK_SIZE;
  if(lx2===0)rebuildChunk(cx-1,cz);
  if(lx2===CHUNK_SIZE-1)rebuildChunk(cx+1,cz);
  if(lz2===0)rebuildChunk(cx,cz-1);
  if(lz2===CHUNK_SIZE-1)rebuildChunk(cx,cz+1);
}

// Input handling
const overlay=document.getElementById('overlay');
const crosshair=document.getElementById('crosshair');
const hotbar=document.getElementById('hotbar');

function showHotbar(){
  hotbar.style.display='flex';
  hotbar.innerHTML='';
  for(let i=1;i<=7;i++){
    const slot=document.createElement('div');
    slot.className='slot'+(i===selectedBlock?' sel':'');
    const c=BLOCK_COLORS[i];
    slot.style.background='#'+c.toString(16).padStart(6,'0');
    slot.textContent=i;
    slot.addEventListener('mousedown',e=>{e.stopPropagation();});
    hotbar.appendChild(slot);
  }
}

overlay.addEventListener('click',()=>{
  document.body.requestPointerLock();
});

document.addEventListener('pointerlockchange',()=>{
  pointerLocked=document.pointerLockElement===document.body;
  if(pointerLocked){
    overlay.style.display='none';
    crosshair.style.display='block';
    showHotbar();
  }else{
    overlay.style.display='flex';
    crosshair.style.display='none';
    hotbar.style.display='none';
  }
});

document.addEventListener('mousemove',e=>{
  if(!pointerLocked)return;
  yaw-=e.movementX*0.002;
  pitch-=e.movementY*0.002;
  pitch=Math.max(-Math.PI/2+0.01,Math.min(Math.PI/2-0.01,pitch));
  camera.rotation.set(pitch,yaw,0);
});

document.addEventListener('mousedown',e=>{
  if(!pointerLocked)return;
  if(e.button===0)breakBlock();
  if(e.button===2)placeBlock();
});

document.addEventListener('contextmenu',e=>e.preventDefault());

document.addEventListener('keydown',e=>{keys[e.code]=true;if(e.code>='Digit1'&&e.code<='Digit7'){selectedBlock=parseInt(e.code.slice(5));showHotbar();}});
document.addEventListener('keyup',e=>{keys[e.code]=false;});
document.addEventListener('wheel',e=>{
  if(!pointerLocked)return;
  if(e.deltaY>0)selectedBlock=selectedBlock%7+1;
  else selectedBlock=((selectedBlock-2+7)%7)+1;
  showHotbar();
});

window.addEventListener('resize',()=>{
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});

// Update clouds
function updateClouds(){
  for(const c of clouds){
    c.mesh.position.x+=c.speed*0.016;
    const dx=c.mesh.position.x-px,dz=c.mesh.position.z-pz;
    if(dx>80)c.mesh.position.x=px-80;
    if(dx<-80)c.mesh.position.x=px+80;
    if(dz>80)c.mesh.position.z=pz-80;
    if(dz<-80)c.mesh.position.z=pz+80;
  }
}

// Main loop
let lastTime=performance.now();
function gameLoop(){
  const now=performance.now();
  const dt=(now-lastTime)/1000;
  lastTime=now;
  updatePlayer(dt);
  updateChunks();
  if(pointerLocked)doRaycast();
  updateClouds();
  waterMesh.position.x=px;
  waterMesh.position.z=pz;
  renderer.render(scene,camera);
  requestAnimationFrame(gameLoop);
}

// Initial spawn
generateChunk(0,0);
py=findSpawnHeight(8,8);
camera.rotation.set(0,0,0);
gameLoop();
})();
</script>
</body>
</html>
```