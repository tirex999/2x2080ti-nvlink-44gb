```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MC</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000}
canvas{display:block}
#overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;font-family:monospace;z-index:100;cursor:pointer}
#overlay h1{font-size:48px;margin-bottom:20px;color:#4caf50}
#overlay p{font-size:14px;margin:4px 0;color:#ccc}
#overlay .start{margin-top:20px;font-size:20px;color:#fff}
#crosshair{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);color:#fff;font-size:24px;pointer-events:none;z-index:50;text-shadow:0 0 2px #000}
#hotbar{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:4px;background:rgba(0,0,0,0.6);padding:6px;border-radius:4px;z-index:50}
.slot{width:40px;height:40px;border:2px solid #555;display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;font-family:monospace;cursor:pointer}
.slot.sel{border-color:#fff}
</style>
</head>
<body>
<div id="overlay">
<h1>MINECRAFT</h1>
<p>WASD - Move | Space - Jump</p>
<p>Left Click - Break | Right Click - Place</p>
<p>1-7 or Mouse Wheel - Select Block</p>
<p>Mouse - Look Around</p>
<p class="start">Click to Play</p>
</div>
<div id="crosshair">+</div>
<div id="hotbar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
// === NOISE ===
function hash(x,y,z){
    let h=(Math.imul(x,374761393)^Math.imul(y,668265263)^Math.imul(z,1274126177))|0;
    h=Math.imul(h^(h>>>13),1274126177)|0;
    h=(h^(h>>>16))|0;
    return(h&0x7fffffff)/0x7fffffff;
}
function smoothstep(t){return t*t*(3-2*t)}
function lerp(a,b,t){return a+(b-a)*t}
function noise2D(x,y){
    const ix=Math.floor(x),iy=Math.floor(y);
    const fx=x-ix,fy=y-iy;
    const sx=smoothstep(fx),sy=smoothstep(fy);
    const v00=hash(ix,iy,0),v10=hash(ix+1,iy,0);
    const v01=hash(ix,iy+1,0),v11=hash(ix+1,iy+1,0);
    return lerp(lerp(v00,v10,sx),lerp(v01,v11,sx),sy);
}
function fractal2D(x,y){
    let val=0,amp=1,freq=1,total=0;
    for(let i=0;i<4;i++){val+=noise2D(x*freq,y*freq)*amp;total+=amp;amp*=0.5;freq*=2;}
    return val/total;
}
function noise3D(x,y,z){
    const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
    const fx=x-ix,fy=y-iy,fz=z-iz;
    const sx=smoothstep(fx),sy=smoothstep(fy),sz=smoothstep(fz);
    const v000=hash(ix,iy,iz),v100=hash(ix+1,iy,iz);
    const v010=hash(ix,iy+1,iz),v110=hash(ix+1,iy+1,iz);
    const v001=hash(ix,iy,iz+1),v101=hash(ix+1,iy,iz+1);
    const v011=hash(ix,iy+1,iz+1),v111=hash(ix+1,iy+1,iz+1);
    return lerp(lerp(lerp(v000,v100,sx),lerp(v010,v110,sx),sy),
                lerp(lerp(v001,v101,sx),lerp(v011,v111,sx),sy),sz);
}
function fractal3D(x,y,z){
    let val=0,amp=1,freq=1,total=0;
    for(let i=0;i<4;i++){val+=noise3D(x*freq,y*freq,z*freq)*amp;total+=amp;amp*=0.5;freq*=2;}
    return val/total;
}

// === BLOCK COLORS ===
const COLORS=[0,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
const BLOCK_NAMES=['Air','Grass','Dirt','Stone','Sand','Wood','Leaves','Snow'];

// === CHUNK SYSTEM ===
const CHUNK_SIZE=16,CHUNK_HEIGHT=80;
const chunks=new Map();
const chunkMeshes=[];

function chunkKey(cx,cz){return cx+','+cz}
function getChunk(cx,cz){return chunks.get(chunkKey(cx,cz))}

function getBlock(wx,wy,wz){
    if(wy<0||wy>=CHUNK_HEIGHT)return 0;
    const cx=Math.floor(wx/CHUNK_SIZE),cz=Math.floor(wz/CHUNK_SIZE);
    const ch=getChunk(cx,cz);
    if(!ch)return 0;
    const lx=wx-cx*CHUNK_SIZE,lz=wz-cz*CHUNK_SIZE;
    return ch[lx+lz*CHUNK_SIZE+wy*CHUNK_SIZE*CHUNK_SIZE];
}

function setBlock(wx,wy,wz,val){
    if(wy<0||wy>=CHUNK_HEIGHT)return;
    const cx=Math.floor(wx/CHUNK_SIZE),cz=Math.floor(wz/CHUNK_SIZE);
    const key=chunkKey(cx,cz);
    let ch=chunks.get(key);
    if(!ch){ch=new Uint8Array(CHUNK_SIZE*CHUNK_SIZE*CHUNK_HEIGHT);chunks.set(key,ch);}
    const lx=wx-cx*CHUNK_SIZE,lz=wz-cz*CHUNK_SIZE;
    ch[lx+lz*CHUNK_SIZE+wy*CHUNK_SIZE*CHUNK_SIZE]=val;
}

// === TERRAIN GENERATION ===
function generateChunk(cx,cz){
    const key=chunkKey(cx,cz);
    if(chunks.has(key))return;
    const data=new Uint8Array(CHUNK_SIZE*CHUNK_SIZE*CHUNK_HEIGHT);
    chunks.set(key,data);
    for(let lx=0;lx<CHUNK_SIZE;lx++){
        for(let lz=0;lz<CHUNK_SIZE;lz++){
            const wx=cx*CHUNK_SIZE+lx,wz=cz*CHUNK_SIZE+lz;
            const m=fractal2D(wx*0.004,wz*0.004);
            const h=fractal2D(wx*0.02,wz*0.02);
            const H=Math.floor(5+m*m*58+h*10);
            for(let y=0;y<CHUNK_HEIGHT;y++){
                let block=0;
                if(y===0){block=3;}
                else if(y<H-3){block=3;}
                else if(y<H){
                    if(H<=16)block=4;
                    else if(H>=37)block=3;
                    else block=2;
                }else if(y===H){
                    if(H>=46)block=7;
                    else if(H>=37)block=3;
                    else if(H<=16)block=4;
                    else block=1;
                }
                // Caves
                if(block!==0&&y>=3&&y<=H-2){
                    if(fractal3D(wx*0.09,y*0.09,wz*0.09)>0.67)block=0;
                }
                data[lx+lz*CHUNK_SIZE+y*CHUNK_SIZE*CHUNK_SIZE]=block;
            }
            // Trees
            if(H>16&&H<37){
                const treeHash=hash(wx,0,wz);
                if(treeHash<0.02&&lx>=2&&lx<=13&&lz>=2&&lz<=13&&H+7<CHUNK_HEIGHT){
                    // Trunk
                    for(let ty=1;ty<=4;ty++){
                        const idx=lx+lz*CHUNK_SIZE+(H+ty)*CHUNK_SIZE*CHUNK_SIZE;
                        if(data[idx]===0)data[idx]=5;
                    }
                    // Leaves 5x5 at H+4 and H+5
                    for(let dy=4;dy<=5;dy++){
                        for(let dx=-2;dx<=2;dx++){
                            for(let dz=-2;dz<=2;dz++){
                                const nlx=lx+dx,nlz=lz+dz,ny=H+dy;
                                if(nlx>=0&&nlx<CHUNK_SIZE&&nlz>=0&&nlz<CHUNK_SIZE&&ny<CHUNK_HEIGHT){
                                    const idx=nlx+nlz*CHUNK_SIZE+ny*CHUNK_SIZE*CHUNK_SIZE;
                                    if(data[idx]===0)data[idx]=6;
                                }
                            }
                        }
                    }
                    // 3x3 at H+6
                    for(let dx=-1;dx<=1;dx++){
                        for(let dz=-1;dz<=1;dz++){
                            const nlx=lx+dx,nlz=lz+dz,ny=H+6;
                            if(nlx>=0&&nlx<CHUNK_SIZE&&nlz>=0&&nlz<CHUNK_SIZE&&ny<CHUNK_HEIGHT){
                                const idx=nlx+nlz*CHUNK_SIZE+ny*CHUNK_SIZE*CHUNK_SIZE;
                                if(data[idx]===0)data[idx]=6;
                            }
                        }
                    }
                    // 1 on top at H+7
                    const topIdx=lx+lz*CHUNK_SIZE+(H+7)*CHUNK_SIZE*CHUNK_SIZE;
                    if(data[topIdx]===0)data[topIdx]=6;
                }
            }
        }
    }
}

// === MESHING ===
const FACES=[
    {dir:[1,0,0],light:0.8,verts:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]]},
    {dir:[-1,0,0],light:0.8,verts:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]},
    {dir:[0,1,0],light:1.0,verts:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]]},
    {dir:[0,-1,0],light:0.55,verts:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]},
    {dir:[0,0,1],light:0.8,verts:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]},
    {dir:[0,0,-1],light:0.8,verts:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]]}
];

function buildChunkMesh(cx,cz){
    const key=chunkKey(cx,cz);
    const data=chunks.get(key);
    if(!data)return;
    // Remove old mesh
    for(let i=chunkMeshes.length-1;i>=0;i--){
        if(chunkMeshes[i].userData.chunkKey===key){
            chunkMeshes[i].geometry.dispose();
            scene.remove(chunkMeshes[i]);
            chunkMeshes.splice(i,1);
        }
    }
    const positions=[],normals=[],colors=[];
    for(let lx=0;lx<CHUNK_SIZE;lx++){
        for(let lz=0;lz<CHUNK_SIZE;lz++){
            for(let y=0;y<CHUNK_HEIGHT;y++){
                const block=data[lx+lz*CHUNK_SIZE+y*CHUNK_SIZE*CHUNK_SIZE];
                if(block===0)continue;
                const wx=cx*CHUNK_SIZE+lx,wz=cz*CHUNK_SIZE+lz;
                const r=((COLORS[block]>>16)&0xff)/255;
                const g=((COLORS[block]>>8)&0xff)/255;
                const b=(COLORS[block]&0xff)/255;
                for(const face of FACES){
                    const nx=wx+face.dir[0],ny=y+face.dir[1],nz=wz+face.dir[2];
                    if(getBlock(nx,ny,nz)!==0)continue;
                    const light=face.light;
                    const cr=r*light,cg=g*light,cb=b*light;
                    const v=face.verts;
                    // Triangle 1: v[0],v[1],v[2]
                    positions.push(wx+v[0][0],y+v[0][1],wz+v[0][2]);
                    positions.push(wx+v[1][0],y+v[1][1],wz+v[1][2]);
                    positions.push(wx+v[2][0],y+v[2][1],wz+v[2][2]);
                    normals.push(face.dir[0],face.dir[1],face.dir[2]);
                    normals.push(face.dir[0],face.dir[1],face.dir[2]);
                    normals.push(face.dir[0],face.dir[1],face.dir[2]);
                    colors.push(cr,cg,cb,cr,cg,cb,cr,cg,cb);
                    // Triangle 2: v[0],v[2],v[3]
                    positions.push(wx+v[0][0],y+v[0][1],wz+v[0][2]);
                    positions.push(wx+v[2][0],y+v[2][1],wz+v[2][2]);
                    positions.push(wx+v[3][0],y+v[3][1],wz+v[3][2]);
                    normals.push(face.dir[0],face.dir[1],face.dir[2]);
                    normals.push(face.dir[0],face.dir[1],face.dir[2]);
                    normals.push(face.dir[0],face.dir[1],face.dir[2]);
                    colors.push(cr,cg,cb,cr,cg,cb,cr,cg,cb);
                }
            }
        }
    }
    if(positions.length===0)return;
    const geo=new THREE.BufferGeometry();
    geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
    geo.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
    geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
    const mesh=new THREE.Mesh(geo,material);
    mesh.userData.chunkKey=key;
    scene.add(mesh);
    chunkMeshes.push(mesh);
}

function rebuildChunk(cx,cz){
    buildChunkMesh(cx,cz);
}

// === THREE.JS SETUP ===
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);
const camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order='YXZ';
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const material=new THREE.MeshLambertMaterial({vertexColors:true});
const ambientLight=new THREE.AmbientLight(0xffffff,0.65);
scene.add(ambientLight);
const dirLight=new THREE.DirectionalLight(0xffffff,0.8);
dirLight.position.set(50,100,30);
scene.add(dirLight);

// === WATER ===
const waterGeo=new THREE.PlaneGeometry(200,200);
const waterMat=new THREE.MeshLambertMaterial({color:0x3388cc,transparent:true,opacity:0.5});
const waterMesh=new THREE.Mesh(waterGeo,waterMat);
waterMesh.rotation.x=-Math.PI/2;
waterMesh.position.y=14.3;
scene.add(waterMesh);

// === CLOUDS ===
const clouds=[];
const cloudMat=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.7});
for(let i=0;i<25;i++){
    const w=10+Math.random()*20;
    const d=8+Math.random()*15;
    const h=1+Math.random()*2;
    const geo=new THREE.BoxGeometry(w,h,d);
    const mesh=new THREE.Mesh(geo,cloudMat);
    mesh.position.set((Math.random()-0.5)*200,88+Math.random()*6,(Math.random()-0.5)*200);
    mesh.userData.speed=0.5+Math.random()*1.5;
    scene.add(mesh);
    clouds.push(mesh);
}

// === OUTLINE ===
const outlineGeo=new THREE.BoxGeometry(1.005,1.005,1.005);
const outlineEdges=new THREE.EdgesGeometry(outlineGeo);
const outlineMat=new THREE.LineBasicMaterial({color:0x000000,linewidth:2});
const outline=new THREE.LineSegments(outlineEdges,outlineMat);
outline.visible=false;
scene.add(outline);

// === PLAYER ===
let player={x:8,y:50,z:8,vx:0,vy:0,vz:0,onGround:false};
let yaw=0,pitch=0;
let selectedBlock=1;
let locked=false;

// Find spawn height
function findSpawnHeight(x,z){
    for(let y=CHUNK_HEIGHT-1;y>=0;y--){
        if(getBlock(x,y,z)!==0)return y+1;
    }
    return 40;
}

// === HOTBAR ===
const hotbar=document.getElementById('hotbar');
const slotColors=[0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
for(let i=0;i<7;i++){
    const slot=document.createElement('div');
    slot.className='slot'+(i===0?' sel':'');
    slot.style.background='#'+slotColors[i].toString(16).padStart(6,'0');
    slot.textContent=i+1;
    slot.addEventListener('click',()=>{selectedBlock=i+1;updateHotbar();});
    hotbar.appendChild(slot);
}
function updateHotbar(){
    const slots=hotbar.children;
    for(let i=0;i<7;i++){
        slots[i].className='slot'+(i===selectedBlock-1?' sel':'');
    }
}

// === INPUT ===
const keys={};
document.addEventListener('keydown',e=>{
    keys[e.code]=true;
    if(e.code>='Digit1'&&e.code<='Digit7'){
        selectedBlock=parseInt(e.code[5]);
        updateHotbar();
    }
});
document.addEventListener('keyup',e=>{keys[e.code]=false});
document.addEventListener('wheel',e=>{
    if(!locked)return;
    if(e.deltaY>0)selectedBlock=selectedBlock%7+1;
    else selectedBlock=((selectedBlock-2+7)%7)+1;
    updateHotbar();
});
document.addEventListener('contextmenu',e=>e.preventDefault());

// Pointer lock
const overlay=document.getElementById('overlay');
overlay.addEventListener('click',()=>{
    document.body.requestPointerLock();
});
document.addEventListener('pointerlockchange',()=>{
    locked=document.pointerLockElement===document.body;
    overlay.style.display=locked?'none':'flex';
});
document.addEventListener('mousemove',e=>{
    if(!locked)return;
    yaw-=e.movementX*0.002;
    pitch-=e.movementY*0.002;
    pitch=Math.max(-Math.PI/2+0.01,Math.min(Math.PI/2-0.01,pitch));
});

// Click for break/place
document.addEventListener('mousedown',e=>{
    if(!locked)return;
    if(e.button===0)breakBlock();
    else if(e.button===2)placeBlock();
});

// === RAYCASTING ===
const raycaster=new THREE.Raycaster();
raycaster.far=6;
let targetBlock=null;

function doRaycast(){
    raycaster.setFromCamera(new THREE.Vector2(0,0),camera);
    const hits=raycaster.intersectObjects(chunkMeshes);
    if(hits.length>0){
        const hit=hits[0];
        const p=hit.point;
        const n=hit.face.normal;
        const bx=Math.floor(p.x-n.x*0.5);
        const by=Math.floor(p.y-n.y*0.5);
        const bz=Math.floor(p.z-n.z*0.5);
        targetBlock={x:bx,y:by,z:bz,px:p.x,py:p.y,pz:p.z,nx:n.x,ny:n.y,nz:n.z};
        outline.visible=true;
        outline.position.set(bx+0.5,by+0.5,bz+0.5);
    }else{
        targetBlock=null;
        outline.visible=false;
    }
}

function breakBlock(){
    if(!targetBlock)return;
    const{x,y,z}=targetBlock;
    if(y===0)return;
    setBlock(x,y,z,0);
    const cx=Math.floor(x/CHUNK_SIZE),cz=Math.floor(z/CHUNK_SIZE);
    rebuildChunk(cx,cz);
    // Rebuild neighbors if on border
    const lx=x-cx*CHUNK_SIZE,lz=z-cz*CHUNK_SIZE;
    if(lx===0)rebuildChunk(cx-1,cz);
    if(lx===CHUNK_SIZE-1)rebuildChunk(cx+1,cz);
    if(lz===0)rebuildChunk(cx,cz-1);
    if(lz===CHUNK_SIZE-1)rebuildChunk(cx,cz+1);
}

function placeBlock(){
    if(!targetBlock)return;
    const{x,y,z,nx,ny,nz}=targetBlock;
    const px=Math.floor(x+nx*0.5+nx*0.5);
    const py=Math.floor(y+ny*0.5+ny*0.5);
    const pz=Math.floor(z+nz*0.5+nz*0.5);
    // Actually use the place cell formula
    const cx2=Math.floor(targetBlock.px+targetBlock.nx*0.5);
    const cy2=Math.floor(targetBlock.py+targetBlock.ny*0.5);
    const cz2=Math.floor(targetBlock.pz+targetBlock.nz*0.5);
    if(getBlock(cx2,cy2,cz2)!==0)return;
    // Check player overlap
    const minX=player.x-0.3,maxX=player.x+0.3;
    const minY=player.y,maxY=player.y+1.8;
    const minZ=player.z-0.3,maxZ=player.z+0.3;
    if(cx2+1>minX&&cx2<maxX&&cy2+1>minY&&cy2<maxY&&cz2+1>minZ&&cz2<maxZ)return;
    setBlock(cx2,cy2,cz2,selectedBlock);
    const ccx=Math.floor(cx2/CHUNK_SIZE),ccz=Math.floor(cz2/CHUNK_SIZE);
    rebuildChunk(ccx,ccz);
    const lx2=cx2-ccx*CHUNK_SIZE,lz2=cz2-ccz*CHUNK_SIZE;
    if(lx2===0)rebuildChunk(ccx-1,ccz);
    if(lx2===CHUNK_SIZE-1)rebuildChunk(ccx+1,ccz);
    if(lz2===0)rebuildChunk(ccx,ccz-1);
    if(lz2===CHUNK_SIZE-1)rebuildChunk(ccx,ccz+1);
}

// === COLLISION ===
function collides(px,py,pz){
    const minX=Math.floor(px-0.3),maxX=Math.floor(px+0.3);
    const minY=Math.floor(py),maxY=Math.floor(py+1.8);
    const minZ=Math.floor(pz-0.3),maxZ=Math.floor(pz+0.3);
    for(let bx=minX;bx<=maxX;bx++){
        for(let by=minY;by<=maxY;by++){
            for(let bz=minZ;bz<=maxZ;bz++){
                if(getBlock(bx,by,bz)!==0){
                    if(px-0.3<bx+1&&px+0.3>bx&&py<by+1&&py+1.8>by&&pz-0.3<bz+1&&pz+0.3>bz){
                        return true;
                    }
                }
            }
        }
    }
    return false;
}

// === CHUNK MANAGEMENT ===
function manageChunks(){
    const pcx=Math.floor(player.x/CHUNK_SIZE),pcz=Math.floor(player.z/CHUNK_SIZE);
    // Generate (max 4 per frame)
    let genCount=0;
    const genList=[];
    for(let dx=-5;dx<=5;dx++){
        for(let dz=-5;dz<=5;dz++){
            const cx=pcx+dx,cz=pcz+dz;
            if(!chunks.has(chunkKey(cx,cz))){
                genList.push({cx,cz,dist:Math.max(Math.abs(dx),Math.abs(dz))});
            }
        }
    }
    genList.sort((a,b)=>a.dist-b.dist);
    for(const c of genList){
        if(genCount>=4)break;
        generateChunk(c.cx,c.cz);
        genCount++;
    }
    // Mesh (max 2 per frame)
    let meshCount=0;
    const meshList=[];
    for(let dx=-4;dx<=4;dx++){
        for(let dz=-4;dz<=4;dz++){
            const cx=pcx+dx,cz=pcz+dz;
            const key=chunkKey(cx,cz);
            if(!chunks.has(key))continue;
            // Check if mesh exists
            let hasMesh=false;
            for(const m of chunkMeshes){
                if(m.userData.chunkKey===key){hasMesh=true;break;}
            }
            if(hasMesh)continue;
            // Check neighbors have data
            if(!chunks.has(chunkKey(cx-1,cz)))continue;
            if(!chunks.has(chunkKey(cx+1,cz)))continue;
            if(!chunks.has(chunkKey(cx,cz-1)))continue;
            if(!chunks.has(chunkKey(cx,cz+1)))continue;
            meshList.push({cx,cz,dist:Math.max(Math.abs(dx),Math.abs(dz))});
        }
    }
    meshList.sort((a,b)=>a.dist-b.dist);
    for(const c of meshList){
        if(meshCount>=2)break;
        buildChunkMesh(c.cx,c.cz);
        meshCount++;
    }
    // Remove far chunks
    const toRemove=[];
    for(const[key]of chunks){
        const parts=key.split(',');
        const cx=parseInt(parts[0]),cz=parseInt(parts[1]);
        const dist=Math.max(Math.abs(cx-pcx),Math.abs(cz-pcz));
        if(dist>7)toRemove.push(key);
    }
    for(const key of toRemove){
        chunks.delete(key);
        for(let i=chunkMeshes.length-1;i>=0;i--){
            if(chunkMeshes[i].userData.chunkKey===key){
                chunkMeshes[i].geometry.dispose();
                scene.remove(chunkMeshes[i]);
                chunkMeshes.splice(i,1);
            }
        }
    }
}

// === GAME LOOP ===
let lastTime=performance.now();
let initialized=false;

function update(){
    const now=performance.now();
    const dt=Math.min((now-lastTime)/1000,0.1);
    lastTime=now;

    if(!initialized){
        // Generate initial chunks
        const pcx=Math.floor(8/CHUNK_SIZE),pcz=Math.floor(8/CHUNK_SIZE);
        for(let dx=-5;dx<=5;dx++)for(let dz=-5;dz<=5;dz++)generateChunk(pcx+dx,pcz+dz);
        for(let dx=-4;dx<=4;dx++)for(let dz=-4;dz<=4;dz++){
            const cx=pcx+dx,cz=pcz+dz;
            if(chunks.has(chunkKey(cx-1,cz))&&chunks.has(chunkKey(cx+1,cz))&&
               chunks.has(chunkKey(cx,cz-1))&&chunks.has(chunkKey(cx,cz+1))){
                buildChunkMesh(cx,cz);
            }
        }
        player.y=findSpawnHeight(8,8);
        initialized=true;
    }

    // Player movement
    const speed=5.5;
    let mx=0,mz=0;
    if(keys['KeyW'])mz-=1;
    if(keys['KeyS'])mz+=1;
    if(keys['KeyA'])mx-=1;
    if(keys['KeyD'])mx+=1;
    const len=Math.sqrt(mx*mx+mz*mz);
    if(len>0){mx/=len;mz/=len;}
    const sinY=Math.sin(yaw),cosY=Math.cos(yaw);
    const moveX=(mx*cosY-mz*sinY)*speed;
    const moveZ=(mx*sinY+mz*cosY)*speed;

    // Gravity
    player.vy-=25*dt;
    if(keys['Space']&&player.onGround){
        player.vy=8.5;
        player.onGround=false;
    }

    // Move X
    const newX=player.x+moveX*dt;
    if(!collides(newX,player.y,player.z)){player.x=newX;}

    // Move Y
    const newY=player.y+player.vy*dt;
    if(!collides(player.x,newY,player.z)){
        player.y=newY;
        player.onGround=false;
    }else{
        if(player.vy<0)player.onGround=true;
        player.vy=0;
    }

    // Move Z
    const newZ=player.z+moveZ*dt;
    if(!collides(player.x,player.y,newZ)){player.z=newZ;}

    // Teleport if fallen
    if(player.y<-20){
        player.x=8;player.z=8;
        player.y=findSpawnHeight(8,8);
        player.vy=0;
    }

    // Camera
    camera.position.set(player.x,player.y+1.62,player.z);
    camera.rotation.set(pitch,yaw,0);

    // Manage chunks
    manageChunks();

    // Raycast
    doRaycast();

    // Water
    waterMesh.position.x=player.x;
    waterMesh.position.z=player.z;

    // Clouds
    for(const c of clouds){
        c.position.x+=c.userData.speed*dt;
        // Wrap around player
        const dx=c.position.x-player.x;
        const dz=c.position.z-player.z;
        if(dx>120)c.position.x-=240;
        if(dx<-120)c.position.x+=240;
        if(dz>120)c.position.z-=240;
        if(dz<-120)c.position.z+=240;
    }

    renderer.render(scene,camera);
    requestAnimationFrame(update);
}

// === RESIZE ===
window.addEventListener('resize',()=>{
    camera.aspect=window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth,window.innerHeight);
});

update();
})();
</script>
</body>
</html>
```