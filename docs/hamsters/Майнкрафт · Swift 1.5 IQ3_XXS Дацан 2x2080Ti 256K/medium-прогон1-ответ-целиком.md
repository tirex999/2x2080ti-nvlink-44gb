```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Minecraft Voxel</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{overflow:hidden;background:#000;font-family:Arial,sans-serif}
canvas{display:block;width:100vw;height:100vh}
#crosshair{position:fixed;top:50%;left:50%;width:2px;height:2px;background:white;transform:translate(-50%,-50%);pointer-events:none;z-index:10}
#hotbar{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);display:flex;gap:4px;background:rgba(0,0,0,0.7);padding:6px;border-radius:6px;z-index:10}
.slot{width:48px;height:48px;display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;border:2px solid #555;border-radius:4px;cursor:pointer}
.slot.sel{border-color:#fff;border-width:3px}
#overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:100;color:#fff;cursor:pointer}
#overlay h1{font-size:48px;margin-bottom:20px;text-shadow:2px 2px #333}
#overlay ul{list-style:none;font-size:16px;line-height:2}
#overlay p{margin-top:20px;font-size:20px;color:#ffcc00}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="overlay">
<h1>⛏ Minecraft Voxel</h1>
<ul>
<li>WASD – Move</li>
<li>Space – Jump</li>
<li>Mouse – Look</li>
<li>Left Click – Break block</li>
<li>Right Click – Place block</li>
<li>1-7 / Scroll – Select block</li>
</ul>
<p>Click to play</p>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
// Block colors
const COLORS=[0,0x4caf50,0x795548,0x9e9e9e,0xe7d9a8,0x8d6e63,0x2e7d32,0xffffff];
const HOTBAR_BLOCKS=[1,2,3,4,5,6,7];
let selectedSlot=0;

// Scene setup
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,40,110);
const camera=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,400);
camera.rotation.order='YXZ';
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

// Lights
scene.add(new THREE.AmbientLight(0xffffff,0.65));
const dirLight=new THREE.DirectionalLight(0xffffff,0.8);
dirLight.position.set(50,100,30);
scene.add(dirLight);

// Shared material
const sharedMat=new THREE.MeshLambertMaterial({vertexColors:true});

// Chunks
const chunks=new Map();
const chunkMeshes=[];

function chunkKey(cx,cz){return cx+','+cz;}
function getChunkData(cx,cz){
    const k=chunkKey(cx,cz);
    return chunks.has(k)?chunks.get(k).data:null;
}
function getBlock(wx,wy,wz){
    if(wy<0||wy>=80)return 0;
    const cx=Math.floor(wx/16),cz=Math.floor(wz/16);
    const k=chunkKey(cx,cz);
    if(!chunks.has(k))return 0;
    const lx=wx-cx*16,lz=wz-cz*16;
    return chunks.get(k).data[lx+lz*16+wy*256];
}
function setBlock(wx,wy,wz,val){
    if(wy<0||wy>=80)return;
    const cx=Math.floor(wx/16),cz=Math.floor(wz/16);
    const k=chunkKey(cx,cz);
    if(!chunks.has(k))return;
    const lx=wx-cx*16,lz=wz-cz*16;
    chunks.get(k).data[lx+lz*16+wy*256]=val;
}

// Noise functions
function hash2(x,y){
    let h=x*374761393+y*125204340;
    h=(h^(h>>13))*1274126177;
    h=h^(h>>16);
    return(h&0x7fffffff)/0x7fffffff;
}
function hash3(x,y,z){
    let h=x*374761393+y*125204340+z*1073741827;
    h=(h^(h>>13))*1274126177;
    h=h^(h>>16);
    h=(h^(h>>13))*1274126177;
    h=h^(h>>16);
    return(h&0x7fffffff)/0x7fffffff;
}
function smoothstep(t){return t*t*(3-2*t);}
function noise2D(x,y){
    const ix=Math.floor(x),iy=Math.floor(y);
    const fx=x-ix,fy=y-iy;
    const sx=smoothstep(fx),sy=smoothstep(fy);
    const a=hash2(ix,iy),b=hash2(ix+1,iy),c=hash2(ix,iy+1),d=hash2(ix+1,iy+1);
    return a+(b-a)*sx+(c-a)*sy+(a-b-c+d)*sx*sy;
}
function noise3D(x,y,z){
    const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
    const fx=x-ix,fy=y-iy,fz=z-iz;
    const sx=smoothstep(fx),sy=smoothstep(fy),sz=smoothstep(fz);
    const n000=hash3(ix,iy,iz),n100=hash3(ix+1,iy,iz),n010=hash3(ix,iy+1,iz),n110=hash3(ix+1,iy+1,iz);
    const n001=hash3(ix,iy,iz+1),n101=hash3(ix+1,iy,iz+1),n011=hash3(ix,iy+1,iz+1),n111=hash3(ix+1,iy+1,iz+1);
    const nx00=n000+(n100-n000)*sx,nx10=n010+(n110-n010)*sx;
    const nx01=n001+(n101-n001)*sx,nx11=n011+(n111-n011)*sx;
    const ny0=nx00+(nx10-nx00)*sy,ny1=nx01+(nx11-nx01)*sy;
    return ny0+(ny1-ny0)*sz;
}
function fractal2D(x,y,oct){
    let val=0,amp=1,freq=1,max=0;
    for(let i=0;i<oct;i++){val+=noise2D(x*freq,y*freq)*amp;max+=amp;amp*=0.5;freq*=2;}
    return val/max;
}
function fractal3D(x,y,z,oct){
    let val=0,amp=1,freq=1,max=0;
    for(let i=0;i<oct;i++){val+=noise3D(x*freq,y*freq,z*freq)*amp;max+=amp;amp*=0.5;freq*=2;}
    return val/max;
}

function getTerrainHeight(wx,wz){
    const m=fractal2D(wx*0.004,wz*0.004,4);
    const h=fractal2D(wx*0.02,wz*0.02,3);
    return Math.floor(5+m*m*58+h*10);
}

function generateChunk(cx,cz){
    const k=chunkKey(cx,cz);
    if(chunks.has(k))return;
    const data=new Uint8Array(16*16*80);
    const bx=cx*16,bz=cz*16;
    for(let lx=0;lx<16;lx++){for(let lz=0;lz<16;lz++){
        const wx=bx+lx,wz=bz+lz;
        const H=getTerrainHeight(wx,wz);
        for(let y=0;y<=Math.min(H,79);y++){
            let block=0;
            if(y===0){block=3;}
            else if(y<H-3){block=3;}
            else if(y>=H-3&&y<H){
                if(H<=16)block=4;
                else if(H>=37)block=3;
                else block=2;
            }
            else if(y===H){
                if(H>=46)block=7;
                else if(H>=37)block=3;
                else if(H<=16)block=4;
                else block=1;
            }
            // Caves
            if(y>=3&&y<=H-2){
                const cv=noise3D(wx*0.09,y*0.09,wz*0.09,3);
                if(cv>0.67)block=0;
            }
            data[lx+lz*16+y*256]=block;
        }
    }}
    // Trees - check expanded area for trees from neighbors
    for(let lx=-2;lx<18;lx++){for(let lz=-2;lz<18;lz++){
        const wx=bx+lx,wz=bz+lz;
        if(hash2(wx*7,wz*13)<0.02){
            const H=getTerrainHeight(wx,wz);
            if(H>16&&H<37){
                // Check surface is grass
                const scx=Math.floor(wx/16),scz=Math.floor(wz/16);
                // We check terrain height indicates grass
                // Tree trunk 4 blocks
                for(let ty=1;ty<=4;ty++){
                    const py=H+ty;
                    const px=wx,ppz=wz;
                    if(px>=bx&&px<bx+16&&ppz>=bz&&ppz<bz+16&&py<80){
                        const li=px-bx+(ppz-bz)*16+py*256;
                        if(data[li]===0)data[li]=5;
                    }
                }
                // Leaves 5x5 at y=H+5 and H+6
                for(let ly=5;ly<=6;ly++){
                    for(let dx=-2;dx<=2;dx++){for(let dz=-2;dz<=2;dz++){
                        const px=wx+dx,ppz=wz+dz,py=H+ly;
                        if(px>=bx&&px<bx+16&&ppz>=bz&&ppz<bz+16&&py<80){
                            const li=px-bx+(ppz-bz)*16+py*256;
                            if(data[li]===0)data[li]=6;
                        }
                    }}
                }
                // 3x3 at H+7
                for(let dx=-1;dx<=1;dx++){for(let dz=-1;dz<=1;dz++){
                    const px=wx+dx,ppz=wz+dz,py=H+7;
                    if(px>=bx&&px<bx+16&&ppz>=bz&&ppz<bz+16&&py<80){
                        const li=px-bx+(ppz-bz)*16+py*256;
                        if(data[li]===0)data[li]=6;
                    }
                }}
                // 1 at H+8
                {const px=wx,ppz=wz,py=H+8;
                if(px>=bx&&px<bx+16&&ppz>=bz&&ppz<bz+16&&py<80){
                    const li=px-bx+(ppz-bz)*16+py*256;
                    if(data[li]===0)data[li]=6;
                }}
            }
        }
    }}
    chunks.set(k,{data:data,mesh:null});
}

// Face definitions
const FACES=[
    {dir:[0,1,0],corners:[[0,1,0],[1,1,0],[1,1,1],[0,1,1]],light:1.0},
    {dir:[0,-1,0],corners:[[0,0,1],[1,0,1],[1,0,0],[0,0,0]],light:0.55},
    {dir:[0,0,1],corners:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]],light:0.8},
    {dir:[0,0,-1],corners:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]],light:0.8},
    {dir:[-1,0,0],corners:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]],light:0.8},
    {dir:[1,0,0],corners:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]],light:0.8}
];

function buildChunkMesh(cx,cz){
    const k=chunkKey(cx,cz);
    if(!chunks.has(k))return;
    const chunk=chunks.get(k);
    if(chunk.mesh){scene.remove(chunk.mesh);chunk.mesh.geometry.dispose();}
    const bx=cx*16,bz=cz*16;
    const positions=[],normals=[],colors=[];
    for(let lx=0;lx<16;lx++){for(let lz=0;lz<16;lz++){for(let y=0;y<80;y++){
        const block=chunk.data[lx+lz*16+y*256];
        if(block===0)continue;
        const wx=bx+lx,wz=bz+lz;
        const r=((COLORS[block]>>16)&0xff)/255;
        const g=((COLORS[block]>>8)&0xff)/255;
        const b=(COLORS[block]&0xff)/255;
        for(let fi=0;fi<6;fi++){
            const f=FACES[fi];
            const nx=wx+f.dir[0],ny=y+f.dir[1],nz=wz+f.dir[2];
            if(getBlock(nx,ny,nz)!==0)continue;
            const light=f.light;
            const cr=r*light,cg=g*light,cb=b*light;
            const c=f.corners;
            // Triangle 0,1,2
            positions.push(wx+c[0][0],y+c[0][1],wz+c[0][2]);
            positions.push(wx+c[1][0],y+c[1][1],wz+c[1][2]);
            positions.push(wx+c[2][0],y+c[2][1],wz+c[2][2]);
            // Triangle 0,2,3
            positions.push(wx+c[0][0],y+c[0][1],wz+c[0][2]);
            positions.push(wx+c[2][0],y+c[2][1],wz+c[2][2]);
            positions.push(wx+c[3][0],y+c[3][1],wz+c[3][2]);
            for(let i=0;i<6;i++){
                normals.push(f.dir[0],f.dir[1],f.dir[2]);
                colors.push(cr,cg,cb);
            }
        }
    }}}
    if(positions.length===0){chunk.mesh=null;return;}
    const geo=new THREE.BufferGeometry();
    geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
    geo.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
    geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
    const mesh=new THREE.Mesh(geo,sharedMat);
    scene.add(mesh);
    chunk.mesh=mesh;
}

function rebuildChunk(cx,cz){buildChunkMesh(cx,cz);}

// Player
let px=8,py=60,pz=8;
let vy=0,yaw=0,pitch=0;
let onGround=false;
let locked=false;
const keys={};
document.addEventListener('keydown',e=>{keys[e.code]=true;});
document.addEventListener('keyup',e=>{keys[e.code]=false;});

// Find spawn height
function findSpawnY(x,z){
    let h=getTerrainHeight(x,z);
    return Math.min(h+2,79);
}
py=findSpawnY(8,8);

// Pointer lock
const overlay=document.getElementById('overlay');
overlay.addEventListener('click',()=>{
    renderer.domElement.requestPointerLock();
});
document.addEventListener('pointerlockchange',()=>{
    locked=(document.pointerLockElement===renderer.domElement);
    overlay.style.display=locked?'none':'flex';
});
document.addEventListener('mousemove',e=>{
    if(!locked)return;
    yaw-=e.movementX*0.002;
    pitch-=e.movementY*0.002;
    pitch=Math.max(-Math.PI/2+0.01,Math.min(Math.PI/2-0.01,pitch));
});

// Hotbar
const hotbarEl=document.getElementById('hotbar');
function buildHotbar(){
    hotbarEl.innerHTML='';
    for(let i=0;i<7;i++){
        const s=document.createElement('div');
        s.className='slot'+(i===selectedSlot?' sel':'');
        const c=COLORS[HOTBAR_BLOCKS[i]];
        s.style.background='#'+c.toString(16).padStart(6,'0');
        s.textContent=(i+1);
        hotbarEl.appendChild(s);
    }
}
buildHotbar();

document.addEventListener('keydown',e=>{
    if(e.key>='1'&&e.key<='7'){selectedSlot=parseInt(e.key)-1;buildHotbar();}
});
document.addEventListener('wheel',e=>{
    selectedSlot=(selectedSlot+(e.deltaY>0?1:-1)+7)%7;
    buildHotbar();
});

// Suppress context menu
document.addEventListener('contextmenu',e=>e.preventDefault());

// Raycasting
const raycaster=new THREE.Raycaster();
raycaster.far=6;
let targetBlock=null;
let outlineMesh=null;

function updateRaycast(){
    if(outlineMesh){scene.remove(outlineMesh);outlineMesh=null;}
    targetBlock=null;
    if(!locked)return;
    raycaster.setFromCamera(new THREE.Vector2(0,0),camera);
    const meshes=chunkMeshes.filter(m=>m.parent===scene);
    const hits=raycaster.intersectObjects(meshes);
    if(hits.length>0){
        const hit=hits[0];
        const p=hit.point;
        const n=hit.face.normal;
        // Break target: floor(p - n*0.5)
        const bx=Math.floor(p.x-n.x*0.5);
        const by=Math.floor(p.y-n.y*0.5);
        const bz=Math.floor(p.z-n.z*0.5);
        if(getBlock(bx,by,bz)!==0){
            targetBlock={x:bx,y:by,z:bz,px:p.x,py:p.y,pz:p.z,nx:n.x,ny:n.y,nz:n.z};
            // Outline
            const geo=new THREE.BoxGeometry(1.005,1.005,1.005);
            const mat=new THREE.MeshBasicMaterial({color:0x000000,wireframe:true});
            outlineMesh=new THREE.Mesh(geo,mat);
            outlineMesh.position.set(bx+0.5,by+0.5,bz+0.5);
            scene.add(outlineMesh);
        }
    }
}

// Click handlers
renderer.domElement.addEventListener('mousedown',e=>{
    if(!locked)return;
    if(e.button===0&&targetBlock){
        // Break
        const t=targetBlock;
        if(t.y===0)return;
        setBlock(t.x,t.y,t.z,0);
        const cx=Math.floor(t.x/16),cz=Math.floor(t.z/16);
        rebuildChunk(cx,cz);
        // Neighbor chunks at borders
        const lx=t.x-cx*16,lz=t.z-cz*16;
        if(lx===0)rebuildChunk(cx-1,cz);
        if(lx===15)rebuildChunk(cx+1,cz);
        if(lz===0)rebuildChunk(cx,cz-1);
        if(lz===15)rebuildChunk(cx,cz+1);
    }
    if(e.button===2&&targetBlock){
        // Place
        const t=targetBlock;
        const cx=Math.floor(t.x/16),cz=Math.floor(t.z/16);
        const px2=Math.floor(t.px+t.nx*0.5);
        const py2=Math.floor(t.py+t.ny*0.5);
        const pz2=Math.floor(t.pz+t.nz*0.5);
        if(py2<0||py2>=80)return;
        if(getBlock(px2,py2,pz2)!==0)return;
        // Check player overlap
        const minX=px-0.3,maxX=px+0.3,minY=py,maxY=py+1.8,minZ=pz-0.3,maxZ=pz+0.3;
        if(px2+1>minX&&px2<maxX&&py2+1>minY&&py2<maxY&&pz2+1>minZ&&pz2<maxZ)return;
        setBlock(px2,py2,pz2,HOTBAR_BLOCKS[selectedSlot]);
        const ncx=Math.floor(px2/16),ncz=Math.floor(pz2/16);
        rebuildChunk(ncx,ncz);
        const lxx=px2-ncx*16,lzz=pz2-ncz*16;
        if(lxx===0)rebuildChunk(ncx-1,ncz);
        if(lxx===15)rebuildChunk(ncx+1,ncz);
        if(lzz===0)rebuildChunk(ncx,ncz-1);
        if(lzz===15)rebuildChunk(ncx,ncz+1);
    }
});

// Collision
function collides(x,y,z){
    const minX=Math.floor(x-0.3),maxX=Math.floor(x+0.3);
    const minY=Math.floor(y),maxY=Math.floor(y+1.79);
    const minZ=Math.floor(z-0.3),maxZ=Math.floor(z+0.3);
    for(let bx=minX;bx<=maxX;bx++)
        for(let by=minY;by<=maxY;by++)
            for(let bz=minZ;bz<=maxZ;bz++)
                if(getBlock(bx,by,bz)!==0)return true;
    return false;
}

// Clouds
const clouds=[];
for(let i=0;i<25;i++){
    const w=8+Math.random()*12,h=1,d=6+Math.random()*8;
    const geo=new THREE.BoxGeometry(w,h,d);
    const mat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.7});
    const m=new THREE.Mesh(geo,mat);
    m.position.set((i%5)*40-80+Math.random()*20,90,Math.floor(i/5)*40-60+Math.random()*20);
    scene.add(m);
    clouds.push({mesh:m,speed:0.3+Math.random()*0.5});
}

// Water plane
const waterGeo=new THREE.PlaneGeometry(400,400);
const waterMat=new THREE.MeshBasicMaterial({color:0x3388cc,transparent:true,opacity:0.55});
const waterMesh=new THREE.Mesh(waterGeo,waterMat);
waterMesh.rotation.x=-Math.PI/2;
waterMesh.position.y=14.3;
scene.add(waterMesh);

// Chunk management
function updateChunks(){
    const pcx=Math.floor(px/16),pcz=Math.floor(pz/16);
    // Generate
    let genCount=0;
    for(let dx=-5;dx<=5&&genCount<4;dx++){for(let dz=-5;dz<=5&&genCount<4;dz++){
        const cx=pcx+dx,cz=pcz+dz;
        const k=chunkKey(cx,cz);
        if(!chunks.has(k)){generateChunk(cx,cz);genCount++;}
    }}
    // Build meshes
    let meshCount=0;
    for(let dx=-4;dx<=4&&meshCount<2;dx++){for(let dz=-4;dz<=4&&meshCount<2;dz++){
        const cx=pcx+dx,cz=pcz+dz;
        const k=chunkKey(cx,cz);
        if(!chunks.has(k))continue;
        const chunk=chunks.get(k);
        if(chunk.mesh)continue;
        // Check 4 neighbors have data
        const n1=getChunkData(cx-1,cz),n2=getChunkData(cx+1,cz),n3=getChunkData(cx,cz-1),n4=getChunkData(cx,cz+1);
        if(n1&&n2&&n3&&n4){buildChunkMesh(cx,cz);meshCount++;}
    }}
    // Unload far chunks
    for(const[key,val]of chunks){
        const parts=key.split(',');
        const cx=parseInt(parts[0]),cz=parseInt(parts[1]);
        if(Math.abs(cx-pcx)>7||Math.abs(cz-pcz)>7){
            if(val.mesh){scene.remove(val.mesh);val.mesh.geometry.dispose();}
            chunks.delete(key);
        }
    }
}

// Update chunkMeshes array
function updateMeshArray(){
    chunkMeshes.length=0;
    for(const[key,val]of chunks){if(val.mesh)chunkMeshes.push(val.mesh);}
}

// Game loop
let lastTime=performance.now();
function gameLoop(){
    requestAnimationFrame(gameLoop);
    const now=performance.now();
    let dt=(now-lastTime)/1000;
    lastTime=now;
    if(dt>0.1)dt=0.1;

    // Update chunks
    updateChunks();
    updateMeshArray();

    // Player movement
    if(locked){
        const speed=5.5;
        let mx=0,mz=0;
        if(keys['KeyW'])mz-=1;
        if(keys['KeyS'])mz+=1;
        if(keys['KeyA'])mx-=1;
        if(keys['KeyD'])mx+=1;
        const sinY=Math.sin(yaw),cosY=Math.cos(yaw);
        const dx=(mx*cosY-mz*sinY)*speed*dt;
        const dz=(mx*sinY+mz*cosY)*speed*dt;

        // Move X
        const oldX=px;
        px+=dx;
        if(collides(px,py,pz))px=oldX;

        // Move Z
        const oldZ=pz;
        pz+=dz;
        if(collides(px,py,pz))pz=oldZ;

        // Gravity & jump
        vy-=25*dt;
        if(keys['Space']&&onGround){vy=8.5;onGround=false;}

        // Move Y
        const oldY=py;
        py+=vy*dt;
        if(collides(px,py,pz)){
            py=oldY;
            if(vy<0)onGround=true;
            vy=0;
        }else{
            onGround=false;
        }

        // Fall below -20
        if(py<-20){px=8;py=findSpawnY(8,8);pz=8;vy=0;}
    }

    // Camera
    camera.position.set(px,py+1.62,pz);
    camera.rotation.y=yaw;
    camera.rotation.x=pitch;

    // Water follows player
    waterMesh.position.x=px;
    waterMesh.position.z=pz;

    // Clouds drift
    for(const c of clouds){
        c.mesh.position.x+=c.speed*dt;
        if(c.mesh.position.x>px+150)c.mesh.position.x=px-150;
        if(c.mesh.position.x<px-150)c.mesh.position.x=px+150;
    }

    // Raycast
    updateRaycast();

    renderer.render(scene,camera);
}

// Resize
window.addEventListener('resize',()=>{
    camera.aspect=window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth,window.innerHeight);
});

gameLoop();
})();
</script>
</body>
</html>
```