# 🐠 Аквариум 36×24×20 — интерактивная морская симуляция

Единый HTML-файл:Three.js (importmap), процедурные рыбки с процедурными же чешуйчатыми текстурами, стаи с ИИ избегания/преследования, стеклянный резервуар с преломлением, каустика, световые шахты, кормление и «приборная» HUD-панель.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>АКВАРИУМ 36×24×20 — 3D морская симуляция</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Manrope:wght@400;500;600;800&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --abyss:#03101a; --deep:#07202f; --ink:#01080e;
  --foam:#e4f5fb; --mute:#7ba3b8; --line:rgba(125,223,245,.18);
  --aqua:#38e0c6; --cyan:#7ddff5; --sand:#e9c489; --coral:#ff6f5c; --gold:#ffd27a;
  --panel:linear-gradient(178deg,rgba(8,31,44,.82),rgba(3,14,22,.9));
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{
  background:radial-gradient(120% 90% at 50% -10%,#0d455c 0%,#062031 42%,#020a12 100%);
  color:var(--foam);font-family:"Manrope",system-ui,sans-serif;overflow:hidden;
  -webkit-font-smoothing:antialiased;
}
canvas#c{position:fixed;inset:0;width:100%;height:100%;display:block;cursor:crosshair}
.grain,.vig{position:fixed;inset:0;pointer-events:none;z-index:2}
.vig{background:radial-gradient(115% 85% at 50% 42%,rgba(0,0,0,0) 45%,rgba(0,6,12,.55) 88%,rgba(0,4,9,.82) 100%);mix-blend-mode:multiply}
.grain{opacity:.055;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/></filter><rect width='140' height='140' filter='url(%23n)'/></svg>")}

/* ---------- HUD ---------- */
.ui{position:fixed;inset:0;z-index:4;display:grid;pointer-events:none;
  grid-template-columns:minmax(258px,306px) 1fr auto;
  grid-template-rows:auto 1fr auto;gap:14px;padding:16px}
.panel{position:relative;pointer-events:auto;background:var(--panel);
  border:1px solid var(--line);box-shadow:0 26px 60px -30px rgba(0,0,0,.9),inset 0 1px 0 rgba(160,240,255,.09);
  -webkit-backdrop-filter:blur(11px) saturate(130%);backdrop-filter:blur(11px) saturate(130%);
  clip-path:polygon(0 13px,13px 0,100% 0,100% calc(100% - 13px),calc(100% - 13px) 100%,0 100%);
  padding:15px 16px 16px;opacity:0;transform:translateY(16px);
  transition:opacity .9s cubic-bezier(.2,.8,.2,1) var(--d,0s),transform .9s cubic-bezier(.2,.8,.2,1) var(--d,0s)}
body.live .panel{opacity:1;transform:none}
.panel::after{content:"";position:absolute;left:0;top:0;width:34px;height:2px;background:var(--aqua);box-shadow:0 0 14px var(--aqua)}
.kicker{font:500 9.5px/1.1 "IBM Plex Mono",monospace;letter-spacing:.26em;text-transform:uppercase;color:var(--cyan);opacity:.85}
.hr{height:1px;background:linear-gradient(90deg,var(--line),transparent);margin:11px 0}

/* brand */
.brand{grid-column:1;grid-row:1;align-self:start}
.brand h1{font-family:"Syne",sans-serif;font-weight:800;font-size:clamp(27px,2.5vw,40px);
  line-height:.92;letter-spacing:-.03em;text-transform:uppercase;margin:8px 0 4px}
.brand h1 b{color:var(--aqua);font-weight:800}
.dims{font:500 10px "IBM Plex Mono",monospace;color:var(--mute);letter-spacing:.16em}
.howto{list-style:none;margin-top:10px;display:grid;gap:6px}
.howto li{display:flex;gap:9px;align-items:baseline;font-size:12.5px;color:#bcd7e4;line-height:1.35}
.howto i{font:500 9px/1 "IBM Plex Mono",monospace;color:var(--ink);background:rgba(125,223,245,.75);
  padding:4px 5px;border-radius:2px;font-style:normal;letter-spacing:.06em;flex:0 0 auto}
.btns{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:13px}
.btns .wide{grid-column:1/-1}
.btn{position:relative;overflow:hidden;cursor:pointer;border:1px solid rgba(56,224,198,.34);
  background:linear-gradient(180deg,rgba(56,224,198,.17),rgba(56,224,198,.04));color:#c6f6ec;
  font:500 10px/1 "IBM Plex Mono",monospace;letter-spacing:.13em;text-transform:uppercase;
  padding:11px 9px;transition:transform .25s,box-shadow .25s,background .25s,color .25s;text-align:left}
.btn span.k{float:right;opacity:.55;border:1px solid currentColor;border-radius:2px;padding:1px 3px;font-size:8px}
.btn:hover{transform:translateY(-2px);color:#fff;background:linear-gradient(180deg,rgba(56,224,198,.34),rgba(56,224,198,.1));
  box-shadow:0 12px 26px -12px rgba(56,224,198,.75)}
.btn:active{transform:translateY(0) scale(.985)}
.btn::before{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 30%,rgba(255,255,255,.35),transparent 70%);
  transform:translateX(-120%);transition:transform .6s}
.btn:hover::before{transform:translateX(120%)}
.btn--coral{border-color:rgba(255,111,92,.4);background:linear-gradient(180deg,rgba(255,111,92,.18),rgba(255,111,92,.04));color:#ffd3cb}
.btn--coral:hover{background:linear-gradient(180deg,rgba(255,111,92,.34),rgba(255,111,92,.1));box-shadow:0 12px 26px -12px rgba(255,111,92,.8)}
.btn--sand{border-color:rgba(233,196,137,.4);background:linear-gradient(180deg,rgba(233,196,137,.17),rgba(233,196,137,.04));color:#f6ddb2}
.btn--gold{border-color:rgba(255,210,122,.4);background:linear-gradient(180deg,rgba(255,210,122,.16),rgba(255,210,122,.04));color:#ffe6b0}
.btn[data-on="0"]{opacity:.5;filter:saturate(.4)}
.sliders{display:grid;gap:10px;margin-top:12px}
.sl label{display:flex;justify-content:space-between;font:500 9.5px "IBM Plex Mono",monospace;
  letter-spacing:.16em;text-transform:uppercase;color:var(--mute);margin-bottom:6px}
.sl output{color:var(--aqua)}
input[type=range]{-webkit-appearance:none;width:100%;height:3px;background:rgba(125,223,245,.2);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;background:var(--aqua);
  border-radius:50%;box-shadow:0 0 12px rgba(56,224,198,.9);transition:transform .2s}
input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.35)}
input[type=range]::-moz-range-thumb{width:13px;height:13px;border:0;background:var(--aqua);border-radius:50%}

/* telemetry */
.tel{grid-column:3;grid-row:1;align-self:start;width:224px}
.tel-top{display:flex;align-items:flex-end;justify-content:space-between;gap:8px}
.fps{font-family:"Syne",sans-serif;font-weight:800;font-size:46px;line-height:.8;letter-spacing:-.04em;
  font-variant-numeric:tabular-nums;color:var(--foam)}
.fps small{display:block;font:400 9px "IBM Plex Mono",monospace;letter-spacing:.2em;color:var(--mute);margin-top:6px}
.dot{width:7px;height:7px;border-radius:50%;background:var(--aqua);box-shadow:0 0 10px var(--aqua);animation:pulse 1.6s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
#spark{width:100%;height:40px;display:block;margin:9px 0 4px;opacity:.9}
.rows{display:grid;gap:1px;background:var(--line)}
.row{display:flex;justify-content:space-between;align-items:baseline;background:rgba(4,18,27,.9);padding:7px 8px;
  transition:background .3s}
.row:hover{background:rgba(10,38,52,.95)}
.row span{font:400 9.5px "IBM Plex Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}
.row b{font-family:"Syne",sans-serif;font-weight:700;font-size:15px;letter-spacing:-.01em;font-variant-numeric:tabular-nums}

/* dock */
.dock{grid-column:2/-1;grid-row:3;align-self:end;justify-self:end;max-width:min(560px,58vw)}
.species{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:10px}
.chip{position:relative;cursor:pointer;border:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.03);
  padding:8px 7px 9px;text-align:left;transition:transform .22s,border-color .22s,background .22s;overflow:hidden}
.chip i{display:block;height:3px;margin-bottom:7px;box-shadow:0 0 9px currentColor}
.chip span{font:600 10.5px "Manrope",sans-serif;color:#cfe6ef;letter-spacing:.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block}
.chip:hover{transform:translateY(-3px);border-color:rgba(255,255,255,.3);background:rgba(255,255,255,.08)}
.chip:disabled{opacity:.35;cursor:not-allowed;transform:none}

/* hint + card + toasts */
.hint{grid-column:1/3;grid-row:3;align-self:end;align-self:end;justify-self:start;display:flex;gap:8px;flex-wrap:wrap;
  opacity:0;transition:opacity 1s .6s}
body.live .hint{opacity:1}
.pill{font:500 10px "IBM Plex Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:#a9cbdb;
  border:1px solid var(--line);background:rgba(3,15,23,.6);padding:8px 11px;-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.pill b{color:var(--aqua)}
.card{grid-column:3;grid-row:3;align-self:end;width:236px;transform:translateY(18px) scale(.97);opacity:0;
  transition:.45s cubic-bezier(.2,.9,.2,1);pointer-events:none}
.card.show{transform:none;opacity:1;pointer-events:auto}
.card h3{font-family:"Syne",sans-serif;font-weight:800;font-size:21px;line-height:1;margin:6px 0 3px;letter-spacing:-.02em}
.card .lat{font:italic 400 11px "Manrope",sans-serif;color:var(--mute);margin-bottom:11px}
.meter{height:4px;background:rgba(255,255,255,.09);margin:5px 0 10px;overflow:hidden}
.meter i{display:block;height:100%;background:var(--aqua);box-shadow:0 0 10px var(--aqua);transition:width .5s}
.card .row2{display:flex;justify-content:space-between;font:500 10px "IBM Plex Mono",monospace;letter-spacing:.1em;
  text-transform:uppercase;color:var(--mute);padding:4px 0;border-bottom:1px dashed rgba(125,223,245,.12)}
.card .row2 b{color:var(--foam);font-family:"Syne",sans-serif;font-size:12.5px}
#toasts{position:fixed;left:50%;top:18px;transform:translateX(-50%);z-index:6;display:grid;gap:7px;justify-items:center;pointer-events:none}
.toast{font:500 10.5px "IBM Plex Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:#d8f2fb;
  background:rgba(4,20,30,.9);border:1px solid var(--line);border-left:3px solid var(--aqua);padding:9px 14px;
  -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);animation:tin .35s cubic-bezier(.2,1,.3,1),tout .4s 2.3s forwards}
@keyframes tin{from{opacity:0;transform:translateY(-14px)}}
@keyframes tout{to{opacity:0;transform:translateY(-10px)}}

/* cursor ring */
#ring{position:fixed;width:26px;height:26px;border:1px solid rgba(125,223,245,.5);border-radius:50%;
  left:0;top:0;margin:-13px 0 0 -13px;z-index:5;pointer-events:none;transition:transform .18s,opacity .3s;opacity:0}
#ring.on{opacity:1}
#ring.press{transform:scale(.55);border-color:var(--coral)}
@media (hover:none){#ring{display:none}}

/* ---------- BOOT ---------- */
#boot{position:fixed;inset:0;z-index:9;display:grid;place-items:center;overflow:hidden;
  background:radial-gradient(90% 70% at 50% 30%,#0b3b53,#04141f 60%,#01070c);
  -webkit-backdrop-filter:blur(16px) saturate(120%);backdrop-filter:blur(16px) saturate(120%);
  transition:opacity 1s ease,filter 1s ease}
#boot.gone{opacity:0;pointer-events:none;filter:blur(30px)}
.binner{position:relative;z-index:2;text-align:center;padding:24px;max-width:min(680px,92vw)}
.bkick{font:500 9.5px "IBM Plex Mono",monospace;letter-spacing:.42em;text-transform:uppercase;color:var(--cyan);opacity:.8}
.btitle{position:relative;margin:16px 0 20px;font-family:"Syne",sans-serif;font-weight:800;
  font-size:clamp(48px,11.5vw,132px);line-height:.82;letter-spacing:-.045em;text-transform:uppercase;color:rgba(212,240,250,.13)}
.btitle .lq{position:absolute;inset:0;overflow:hidden;transform:scaleY(.04);transform-origin:bottom;
  transition:transform 2.6s cubic-bezier(.3,.7,.2,1);will-change:transform}
#boot.filling .btitle .lq{transform:scaleY(1)}
.btitle .lq span{display:block;background:linear-gradient(180deg,#b9f6ff 0%,#4ee7cf 48%,#12a6b8 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.btitle .lq span::after{content:"";position:absolute;left:0;right:0;top:0;height:9px;
  background:radial-gradient(50% 100% at 50% 0,rgba(255,255,255,.6),transparent 70%);animation:wv 2.4s infinite}
.meter2{position:relative;height:3px;background:rgba(125,223,245,.16);max-width:420px;margin:0 auto}
.meter2 i{position:absolute;inset:0 auto 0 0;width:0%;background:linear-gradient(90deg,var(--aqua),var(--cyan));
  box-shadow:0 0 16px var(--aqua);transition:width .12s linear}
.bnote{margin-top:14px;font:400 12px "IBM Plex Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
#bootBtn{margin-top:22px;cursor:pointer;border:1px solid rgba(56,224,198,.5);background:rgba(56,224,198,.1);
  color:#d5fff6;font:500 11px "IBM Plex Mono",monospace;letter-spacing:.24em;text-transform:uppercase;padding:15px 30px;
  opacity:.3;pointer-events:none;transition:.4s}
#bootBtn.ready{opacity:1;pointer-events:auto;box-shadow:0 0 40px -12px var(--aqua)}
#bootBtn.ready:hover{background:rgba(56,224,198,.25);transform:translateY(-2px)}
.bb{position:absolute;bottom:-8vh;border-radius:50%;background:radial-gradient(circle at 32% 28%,#fff,rgba(150,230,255,.25) 62%,rgba(120,220,255,.05));
  opacity:.5;animation:rise linear infinite}
@keyframes rise{from{transform:translateY(0) translateX(0) scale(.6);opacity:0}
  12%{opacity:.6} to{transform:translateY(-112vh) translateX(28px) scale(1.15);opacity:0}}

@media (max-width:900px){
  .ui{grid-template-columns:1fr auto;padding:10px;gap:10px}
  .brand{grid-column:1/-2}.tel{grid-column:1/-1;grid-row:2;width:auto;justify-self:end;align-self:start}
  .dock{grid-column:1/-1;grid-row:3;max-width:none;justify-self:stretch}
  .hint{display:none}.species{grid-template-columns:repeat(4,1fr)}
  .fps{font-size:34px}.btns{grid-template-columns:1fr 1fr}
}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.15s!important}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="grain"></div><div class="vig"></div>
<div id="ring"></div>

<div class="ui">
  <header class="panel brand" style="--d:.05s">
    <div class="kicker">Three.js · процедурная симуляция</div>
    <h1>Аква<b>риум</b></h1>
    <div class="dims">36 × 24 × 20 ЕД · СТЕКЛО IOR 1.33</div>
    <div class="hr"></div>
    <ul class="howto">
      <li><i>LMB</i>Облёт камеры вокруг резервуара</li>
      <li><i>RMB</i>Панорама · <i>COL</i>Зум 10–60</li>
      <li><i>КЛИК</i>По воде — бросить корм, по рыбке — досье</li>
    </ul>
    <div class="btns">
      <button class="btn" id="bFish">+ Рыбка<span class="k">N</span></button>
      <button class="btn btn--coral" id="bFeed">Корм<span class="k">F</span></button>
      <button class="btn" id="bBub">Пузыри<span class="k">B</span></button>
      <button class="btn btn--sand" id="bLight">Свет<span class="k">L</span></button>
      <button class="btn btn--gold" id="bNight">Ночь<span class="k">M</span></button>
      <button class="btn" id="bCam">Облёт<span class="k">C</span></button>
      <button class="btn wide" id="bReset">Очистить корм и перезапустить стаю<span class="k">R</span></button>
    </div>
    <div class="sliders">
      <div class="sl"><label>Скорость течения <output id="oSpeed">1.00×</output></label><input id="sSpeed" type="range" min="0.2" max="2" step="0.05" value="1"></div>
      <div class="sl"><label>Прозрачность воды <output id="oClarity">70%</output></label><input id="sClarity" type="range" min="0" max="1" step="0.01" value=".7"></div>
    </div>
  </header>

  <aside class="panel tel" style="--d:.2s">
    <div class="tel-top">
      <div><div class="kicker">FPS</div><div class="fps" id="tFps">60<small>кадр / сек</small></div></div>
      <div class="dot" id="tDot"></div>
    </div>
    <canvas id="spark" width="440" height="80"></canvas>
    <div class="rows">
      <div class="row"><span>Популяция</span><b id="tFish">15</b></div>
      <div class="row"><span>Частиц корма</span><b id="tFood">0</b></div>
      <div class="row"><span>Пузырьки</span><b id="tBub">30</b></div>
      <div class="row"><span>Освещённость</span><b id="tLux">2.20</b></div>
      <div class="row"><span>Температура</span><b id="tTemp">25.8°C</b></div>
      <div class="row"><span>Съедено сегодня</span><b id="tEat">0</b></div>
    </div>
  </aside>

  <div class="panel dock" style="--d:.35s">
    <div class="kicker">Ихтиофауна · 8 цветовых схем · клик — подсадить</div>
    <div class="species" id="species"></div>
  </div>

  <div class="hint">
    <div class="pill">Клик по воде — <b>корм</b></div>
    <div class="pill">Клик по рыбке — <b>досье</b></div>
    <div class="pill">Корм тонет · рыба <b>растёт на 5%</b></div>
  </div>

  <div class="panel card" id="card">
    <div class="kicker">Досье особи · <span id="dId">#00</span></div>
    <h3 id="dName">—</h3>
    <div class="lat" id="dLat">—</div>
    <div class="row2"><span>Длина</span><b id="dSize">—</b></div>
    <div class="row2"><span>Скорость</span><b id="dSpeed">—</b></div>
    <div class="row2"><span>Съедено</span><b id="dEat">—</b></div>
    <div class="hr" style="margin:9px 0"></div>
    <div class="kicker" style="letter-spacing:.2em">Сытость</div>
    <div class="meter"><i id="dFull" style="width:50%"></i></div>
    <button class="btn wide" id="dClose">Закрыть досье</button>
  </div>
</div>

<div id="toasts"></div>

<div id="boot">
  <div class="binner">
    <div class="bkick">Резервуар · подводная среда · three.js r169</div>
    <div class="btitle"><span>Аквариум</span><span class="lq" aria-hidden="true"><span>Аквариум</span></span></div>
    <div class="meter2"><i id="bWater"></i></div>
    <div class="bnote" id="bNote">Наполнение резервуара · 0%</div>
    <button id="bootBtn">Опустить камеру</button>
  </div>
</div>

<script type="importmap">
{"imports":{
  "three":"https://unpkg.com/three@0.169.0/build/three.module.js",
  "three/addons/":"https://unpkg.com/three@0.169.0/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

/* ══════════════ 0. УТИЛИТЫ ══════════════ */
const rand=(a,b)=>a+Math.random()*(b-a);
const ri=(a,b)=>Math.floor(rand(a,b+1));
const cl=(v,a,b)=>Math.min(b,Math.max(a,v));
const TAU=Math.PI*2;
function noise2(x,y){const s=Math.sin(x*127.1+y*311.7)*43758.5453;return (s-Math.floor(s))*2-1;}
function fbm(x,y){return noise2(x,y)*.5+noise2(x*2.3+7.1,y*2.3-3.3)*.3+noise2(x*4.7-11.3,y*4.7+5.9)*.2;}
const el=id=>document.getElementById(id);
function toast(msg,col='var(--aqua)'){
  const t=document.createElement('div');t.className='toast';t.textContent=msg;
  t.style.borderLeftColor=col;el('toasts').appendChild(t);
  setTimeout(()=>t.remove(),2800);
}

/* ══════════════ 1. ЦВЕТОВЫЕ СХЕМЫ ══════════════ */
const SPECIES=[
 {name:'Оранжевый клоун',   lat:'Amphiprion ocellaris',  base:'#ff8a2b',dark:'#a44a08',belly:'#ffe1b0',band:'#fff6e6',pat:'bands', fin:'#ffd7a0',acc:'#fff4dd',rough:.42},
 {name:'Хирург голубой',    lat:'Paracanthurus hepatus', base:'#2256c8',dark:'#0a1d55',belly:'#8fd0ff',band:'#ffd84d',pat:'palette',fin:'#4d7dff',acc:'#ffd84d',rough:.4},
 {name:'Желто-красный барс',lat:'Lutjanus sanguineus',   base:'#ff9a12',dark:'#a3202a',belly:'#ffe7ad',band:'#c81f36',pat:'flame',fin:'#ff5a4a',acc:'#ffcf6a',rough:.44},
 {name:'Амприприон фиолет.',lat:'Pseudochromis fridmani',base:'#8b4bd6',dark:'#301059',belly:'#e3c8ff',band:'#f0b6ff',pat:'ribbon',fin:'#c08cff',acc:'#ffe4ff',rough:.38},
 {name:'Кардинал красный',  lat:'Pterapogon kauderni',   base:'#d5253f',dark:'#4c0410',belly:'#ffc7c9',band:'#180a10',pat:'speck',fin:'#ff7b86',acc:'#ffd0d6',rough:.42},
 {name:'Морской лист',      lat:'Phyllopteryx taeniolatus',base:'#3f9d4a',dark:'#0f3d1d',belly:'#d5f2a5',band:'#1c5e2a',pat:'ribbon',fin:'#8fd06a',acc:'#e7ffb0',rough:.55},
 {name:'Розовый стеклянный',lat:'Apogon cyanosoma',      base:'#f579b6',dark:'#7b1f4e',belly:'#ffe6f3',band:'#ffd2e8',pat:'speck',fin:'#ffa8d2',acc:'#fff0f8',rough:.34},
 {name:'Золотой император', lat:'Semicossyphus pulcher', base:'#e9ae2b',dark:'#6a4205',belly:'#fff3c4',band:'#5c3c07',pat:'scales',fin:'#ffd97a',acc:'#fff7d0',rough:.28},
];

/* процедурная текстура чешуи */
function fishTexture(sp,idx){
  const W=512,H=256,c=document.createElement('canvas');c.width=W;c.height=H;const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,W,0);
  g.addColorStop(0,sp.band);g.addColorStop(.14,sp.dark);g.addColorStop(.36,sp.base);
  g.addColorStop(.62,sp.base);g.addColorStop(.84,sp.belly);g.addColorStop(1,sp.band);
  x.fillStyle=g;x.fillRect(0,0,W,H);
  const P=sp.pat;
  if(P==='bands'){
    x.fillStyle=sp.band;
    [[.16,.055],[.46,.075],[.76,.05]].forEach(([p,w])=>{x.save();x.translate(p*W,0);x.rotate(-.07);x.fillRect(-w*W,-20,w*W*2,H+40);x.restore();});
    x.fillStyle='rgba(0,0,0,.25)';x.fillRect(0,0,W,H);x.fillStyle=sp.base;x.globalCompositeOperation='lighter';
    for(let i=0;i<6;i++)x.fillRect(rand(0,W),0,3,H);
  }else if(P==='palette'){
    x.fillStyle=sp.base;x.globalCompositeOperation='source-over';x.fillRect(0,0,W,H);
    x.fillStyle=sp.dark;x.beginPath();
    x.moveTo(W*.05,H*.15);x.bezierCurveTo(W*.45,H*.05,W*.5,H*.9,W*.05,H*.85);
    x.bezierCurveTo(W*.3,H*.6,W*.3,H*.4,W*.05,H*.15);x.fill();
    x.fillStyle=sp.band;x.fillRect(W*.72,0,W*.28,H);
    x.fillStyle=sp.belly;globalThis.aa=0;
  }else if(P==='flame'){
    for(let i=0;i<26;i++){
      x.fillStyle=i%2?'rgba(215,25,45,.5)':'rgba(255,236,160,.35)';
      x.beginPath();const px=rand(0,W);
      x.moveTo(px,0);x.bezierCurveTo(px+22,H*.35,px-24,H*.68,px+8,H);x.lineTo(px+18,H);
      x.bezierCurveTo(px-14,H*.66,px+32,H*.34,px+12,0);x.fill();
    }
  }else if(P==='ribbon'){
    for(let i=0;i<9;i++){
      x.strokeStyle=i%2?'rgba(255,255,255,.34)':'rgba(0,0,0,.24)';x.lineWidth=rand(6,17);
      x.beginPath();x.arc(rand(0,W),H/2,rand(60,150),.3,2.9);x.stroke();
    }
  }else if(P==='speck'){
    for(let i=0;i<300;i++){x.fillStyle=Math.random()<.5?'rgba(255,255,255,.32)':'rgba(0,0,0,.3)';
      x.beginPath();x.ellipse(rand(0,W),rand(0,H),rand(1.4,5),rand(1.4,4),rand(0,3),0,TAU);x.fill();}
  }
  /* чешуйчатый ажур */
  x.globalCompositeOperation='overlay';
  for(let row=0;row<26;row++){
    for(let col=0;col<40;col++){
      const px=col*13+(row%2?6.5:0),py=row*10;
      x.strokeStyle='rgba(255,255,255,.10)';x.lineWidth=1;
      x.beginPath();x.arc(px,py,6.6,.25,Math.PI-.25);x.stroke();
      x.strokeStyle='rgba(0,0,0,.13)';
      x.beginPath();x.arc(px,py+1.6,6.2,.4,Math.PI-.4);x.stroke();
    }
  }
  x.globalCompositeOperation='source-over';
  /* затемнение к хвосту, блик по боковой линии */
  const tg=x.createLinearGradient(0,0,W,0);
  tg.addColorStop(0,'rgba(0,0,0,.5)');tg.addColorStop(.22,'rgba(0,0,0,0)');
  tg.addColorStop(.9,'rgba(0,0,0,.18)');tg.addColorStop(1,'rgba(0,0,0,.55)');
  x.fillStyle=tg;x.fillRect(0,0,W,H);
  const lg=x.createLinearGradient(0,H*.34,0,H*.52);
  lg.addColorStop(0,'rgba(255,255,255,0)');lg.addColorStop(.5,'rgba(255,255,255,.2)');lg.addColorStop(1,'rgba(255,255,255,0)');
  x.fillStyle=lg;x.fillRect(0,H*.34,W,H*.18);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=4;return t;
}
function causticTexture(){
  const S=512,c=document.createElement('canvas');c.width=c.height=S;const x=c.getContext('2d');
  x.fillStyle='#000';x.fillRect(0,0,S,S);
  for(let i=0;i<170;i++){
    const cx=rand(0,S),cy=rand(0,S),r=rand(14,62);
    const g=x.createRadialGradient(cx,cy,r*.15,cx,cy,r);
    g.addColorStop(0,'rgba(185,255,245,.75)');g.addColorStop(.55,'rgba(90,220,220,.14)');g.addColorStop(1,'rgba(0,0,0,0)');
    x.fillStyle=g;x.beginPath();x.arc(cx,cy,r,0,TAU);x.fill();
  }
  x.globalCompositeOperation='lighter';
  for(let i=0;i<90;i++){
    x.strokeStyle='rgba(200,255,255,.22)';x.lineWidth=rand(.6,2.4);x.beginPath();
    let px=rand(0,S),py=rand(0,S);x.moveTo(px,py);
    for(let k=0;k<6;k++){px+=rand(-60,60);py+=rand(-60,60);x.lineTo(px,py);}x.stroke();
  }
  const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.blendMode=undefined;return t;
}
function shaftTexture(){
  const W=128,H=256,c=document.createElement('canvas');c.width=W;c.height=H;const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'rgba(190,255,255,.95)');g.addColorStop(.45,'rgba(140,235,255,.28)');g.addColorStop(1,'rgba(90,200,255,0)');
  x.fillStyle=g;x.fillRect(0,0,W,H);
  const s=x.createLinearGradient(0,0,W,0);
  s.addColorStop(0,'rgba(0,0,0,1)');s.addColorStop(.5,'rgba(0,0,0,0)');s.addColorStop(1,'rgba(0,0,0,1)');
  x.globalCompositeOperation='destination-in';x.fillStyle=s;x.fillRect(0,0,W,H);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}

/* ══════════════ 2. РЕНДЕР / СЦЕНА ══════════════ */
const canvas=el('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.06;
renderer.outputColorSpace=THREE.SRGBColorSpace;
try{renderer.transmissionResolutionScale=.6;}catch(e){}

const scene=new THREE.Scene();
scene.background=new THREE.Color(0x03151f);
scene.fog=new THREE.FogExp2(0x073244,0.0082);
const FOG_BASE=0.0225,FOG_MIN=0.0028;

const camera=new THREE.PerspectiveCamera(52,innerWidth/innerHeight,.1,900);
camera.position.set(26,14,33);

const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.055;
controls.minDistance=10;controls.maxDistance=60;
controls.maxPolarAngle=Math.PI/1.8;
controls.target.set(0,1.5,0);
controls.autoRotateSpeed=.42;

const pmrem=new THREE.PMREMGenerator(renderer);
scene.environment=pmrem.fromScene(new RoomEnvironment(),0.05).texture;
if('environmentIntensity' in scene) scene.environmentIntensity=.45;

/* купол фона */
const dome=new THREE.Mesh(new THREE.SphereGeometry(320,32,16),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,
  uniforms:{top:{value:new THREE.Color(0x1a86a8)},mid:{value:new THREE.Color(0x0a4058)},bot:{value:new THREE.Color(0x020c14)},
            up:{value:new THREE.Color(0x0a4058)},dn:{value:new THREE.Color(0x01080e)}},
  vertexShader:'varying vec3 vP;void main(){vP=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
  fragmentShader:`varying vec3 vP;uniform vec3 top,mid,bot,up,dn;
   void main(){vec3 n=normalize(vP);float h=n.y*.5+.5;
   vec3 c=mix(bot,mid,smoothstep(0.,.58,h));c=mix(c,top,smoothstep(.58,1.,h));
   c=mix(c,up,smoothstep(.05,.6,n.y)*.35);c=mix(c,dn,smoothstep(.0,.5,-n.y)*.8);
   gl_FragColor=vec4(c,1.);}`}
));
dome.material.toneMapped=true;scene.add(dome);

/* ══════════════ 3. ОСВЕЩЕНИЕ ══════════════ */
const ambient=new THREE.AmbientLight(0x404040,.4);scene.add(ambient);
const sun=new THREE.DirectionalLight(0xffeac6,2.2);
sun.position.set(15,31,16);sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-26;sun.shadow.camera.right=26;
sun.shadow.camera.top=22;sun.shadow.camera.bottom=-22;
sun.shadow.camera.near=1;sun.shadow.camera.far=90;
sun.shadow.bias=-.0006;sun.shadow.normalBias=.035;sun.shadow.radius=2.4;
scene.add(sun,sun.target);
const rim=new THREE.DirectionalLight(0x8fe8ff,.5);rim.position.set(-16,10,-18);scene.add(rim);
const pt1=new THREE.PointLight(0x5fd9ff,430,110,2);pt1.position.set(-13,5,7);scene.add(pt1);
const pt2=new THREE.PointLight(0x2f66ff,360,110,2);pt2.position.set(13,-3,-6);scene.add(pt2);
const pt3=new THREE.PointLight(0x74ffd8,180,70,2);pt3.position.set(0,9,0);scene.add(pt3);
let sunOn=1,sunWant=2.2,nightMode=false;

/* ══════════════ 4. РЕЗЕРВУАР ══════════════ */
const TANK={w:36,h:24,d:20};
const GLASS=new THREE.MeshPhysicalMaterial({
  color:0xdff6ff,metalness:0,roughness:.045,transmission:.95,thickness:1.1,ior:1.33,
  transparent:false,side:THREE.BackSide,depthWrite:false,envMapIntensity:1.5,fog:false,
  specularIntensity:1,clearcoat:1,clearcoatRoughness:.03});
const glassBack=new THREE.Mesh(new THREE.BoxGeometry(TANK.w,TANK.h,TANK.d),GLASS);
glassBack.renderOrder=-2;scene.add(glassBack);

const glassFront=new THREE.Mesh(new THREE.BoxGeometry(TANK.w,TANK.h,TANK.d),new THREE.MeshPhysicalMaterial({
  color:0x9fe4ff,transparent:true,opacity:.085,metalness:0,roughness:.05,side:THREE.FrontSide,
  depthWrite:false,envMapIntensity:2.2,clearcoat:1,fog:false}));
glassFront.renderOrder=12;scene.add(glassFront);

const eg=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(TANK.w,TANK.h,TANK.d)),
  new THREE.LineBasicMaterial({color:0x9ff0e4,transparent:true,opacity:.3,fog:false}));
scene.add(eg);
/* металлический каркас */
const frameMat=new THREE.MeshStandardMaterial({color:0x2b3a44,metalness:.95,roughness:.32,envMapIntensity:1.3});
const fw=.45,grp=new THREE.Group();scene.add(grp);
const bar=(sx,sy,sz,x,y,z)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),frameMat);
  m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;grp.add(m);};
for(const sy of [-1,1])for(const sz of [-1,1])bar(fw,TANK.h+fw,fw,TANK.w/2,sy*TANK.h/2,sz*TANK.d/2);
for(const sx of [-1,1])for(const sz of [-1,1])bar(TANK.w+fw,fw,fw,0,sx*TANK.h/2,sz*TANK.d/2);
for(const sx of [-1,1])for(const sy of [-1,1])bar(fw,fw,TANK.d+fw,sx*TANK.w/2,sy*TANK.h/2,0);

/* ══════════════ 5. ПЕСОК ══════════════ */
const sandGeo=new THREE.PlaneGeometry(TANK.w-.6,TANK.d-.6,110,70);
sandGeo.rotateX(-Math.PI/2);
{
  const p=sandGeo.attributes.position,col=[];
  const cA=new THREE.Color(0xdcbd84),cB=new THREE.Color(0x8f7a52),cC=new THREE.Color(0xf3e0b6),tmp=new THREE.Color();
  for(let i=0;i<p.count;i++){
    const x=p.getX(i),z=p.getZ(i);
    const edge=Math.min(1,Math.min(1,(TANK.w/2-.5-Math.abs(x))/4,(TANK.d/2-.5-Math.abs(z))/4));
    const h=fbm(x*.13,z*.13)*.85+fbm(x*.42+9,z*.42-4)*.22;
    p.setY(i,-10.5+h*Math.max(0,edge));
    const n=fbm(x*.6,z*.6)*.5+.5;
    tmp.copy(cA).lerp(cB,cl(n*.9,0,1)).lerp(cC,cl((h+.5)*.35,0,.6));
    col.push(tmp.r,tmp.g,tmp.b);
  }
  sandGeo.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  sandGeo.computeVertexNormals();
}
const sand=new THREE.Mesh(sandGeo,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.95,metalness:0,envMapIntensity:.5}));
sand.receiveShadow=true;sand.name='sand';scene.add(sand);

/* ══════════════ 6. КАМНИ ══════════════ */
const rockMat=new THREE.MeshStandardMaterial({color:0x5b6670,roughness:.86,metalness:.06,flatShading:true,envMapIntensity:.8});
const rocks=[];
for(let i=0;i<8;i++){
  const g=new THREE.DodecahedronGeometry(rand(.9,2.3),0),p=g.attributes.position,v=new THREE.Vector3();
  for(let k=0;k<p.count;k++){v.fromBufferAttribute(p,k);
    v.multiplyScalar(1+fbm(v.x*1.5+i*3,v.y*1.5+v.z)*.34);p.setXYZ(k,v.x,v.y,v.z);}
  g.computeVertexNormals();
  const m=new THREE.Mesh(g,rockMat.clone());
  m.material.color.offsetHSL(rand(-.04,.04),rand(-.05,.05),rand(-.06,.06));
  const side=Math.random()<.5?-1:1;
  m.position.set(side*rand(6,15.5),-10.4,rand(-7,7));
  m.rotation.set(rand(0,6),rand(0,6),rand(0,6));m.scale.y*=rand(.6,1);
  m.castShadow=m.receiveShadow=true;scene.add(m);rocks.push(m);
}

/* ══════════════ 7. ВОДОРОСЛИ ══════════════ */
const plants=[];
function makePlant(x,z){
  const g=new THREE.Group();
  const hue=rand(.24,.42),col=new THREE.Color().setHSL(hue,rand(.42,.68),rand(.2,.33));
  const mat=new THREE.MeshStandardMaterial({color:col,roughness:.72,metalness:0,side:THREE.DoubleSide,flatShading:true,envMapIntensity:.6});
  const strands=ri(4,7),H=rand(3.4,8.2);
  for(let s=0;s<strands;s++){
    const pts=[],lean=rand(-2.4,2.4),hh=H*rand(.55,1.05),ph=rand(0,6);
    for(let i=0;i<=7;i++){const t=i/7;
      pts.push(new THREE.Vector3(lean*t*t*1.25+Math.sin(ph+t*3)*.35*t,hh*t,Math.cos(ph+t*2.4)*.9*t*1.4));}
    const blade=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),18,rand(.09,.19),5,false),mat);
    blade.castShadow=true;g.add(blade);
    const tip=new THREE.Mesh(new THREE.SphereGeometry(rand(.2,.34),7,5),mat);
    tip.scale.set(.22,1.1,1.15);tip.position.copy(pts[pts.length-1]);tip.castShadow=true;g.add(tip);
  }
  g.position.set(x,-10.3,z);
  g.userData={ph:rand(0,TAU),amp:rand(.05,.12)};
  scene.add(g);plants.push(g);return g;
}
for(let i=0;i<12;i++){
  const side=i%2?-1:1;
  makePlant(side*rand(6,16.5),rand(-8,8));
}

/* ══════════════ 8. ПОВЕРХНОСТЬ / КАУСТИКА / ШАХТЫ ══════════════ */
const surfGeo=new THREE.PlaneGeometry(TANK.w-1,TANK.d-1,58,34);
surfGeo.rotateX(-Math.PI/2);
const surface=new THREE.Mesh(surfGeo,new THREE.MeshPhysicalMaterial({
  color:0xa8ecff,transparent:true,opacity:.32,roughness:.06,metalness:0,side:THREE.DoubleSide,
  depthWrite:false,envMapIntensity:1.6,emissive:0x14425c,emissiveIntensity:.5,fog:false}));
surface.position.y=10.4;surface.renderOrder=8;scene.add(surface);
const sBase=surfGeo.attributes.position.array.slice();

const cTex=causticTexture();cTex.repeat.set(3,2);
const caustics=new THREE.Mesh(new THREE.PlaneGeometry(TANK.w-1,TANK.d-1),
  new THREE.MeshBasicMaterial({map:cTex,transparent:true,opacity:.5,blending:THREE.AdditiveBlending,
    depthWrite:false,fog:false,color:0x8ff0e6}));
caustics.rotation.x=-Math.PI/2;caustics.position.y=-10.1;caustics.renderOrder=3;scene.add(caustics);

const shTex=shaftTexture(),shafts=new THREE.Group();scene.add(shafts);
for(let i=0;i<6;i++){
  const m=new THREE.Mesh(new THREE.PlaneGeometry(rand(4,7),30),
    new THREE.MeshBasicMaterial({map:shTex,transparent:true,opacity:rand(.07,.15),
      blending:THREE.AdditiveBlending,depthWrite:false,fog:false,side:THREE.DoubleSide,color:0xa8f0ff}));
  m.position.set(rand(-13,13),1,rand(-6,6));m.rotation.z=rand(-.2,.2);
  m.userData={x0:m.position.x,ph:rand(0,6),sp:rand(.1,.3)};
  shafts.add(m);
}
/* взвесь */
const DUST=420,dPos=new Float32Array(DUST*3);
for(let i=0;i<DUST;i++){dPos[i*3]=rand(-17,17);dPos[i*3+1]=rand(-10,10);dPos[i*3+2]=rand(-9,9);}
const dGeo=new THREE.BufferGeometry();dGeo.setAttribute('position',new THREE.BufferAttribute(dPos,3));
const dust=new THREE.Points(dGeo,new THREE.PointsMaterial({color:0xbfeaff,size:.09,transparent:true,
  opacity:.5,sizeAttenuation:true,depthWrite:false}));
scene.add(dust);

/* ══════════════ 9. РЫБЫ ══════════════ */
const BODY_L=1.2;
function bodyGeo(){
  const g=new THREE.SphereGeometry(1,46,26);g.rotateZ(-Math.PI/2);
  const peak=(()=>{let m=0;for(let i=0;i<=60;i++){const pt=1-i/60;m=Math.max(m,Math.pow(Math.sin(Math.PI*(.13+.87*pt)),.75));}return m;})();
  const p=g.attributes.position,v=new THREE.Vector3();
  for(let i=0;i<p.count;i++){
    v.fromBufferAttribute(p,i);
    const pt=cl(1-(v.x+1)/2,0,1);
    const girth=Math.pow(Math.sin(Math.PI*(.13+.87*pt)),.75)/peak;
    const rr=Math.hypot(v.y,v.z);
    if(rr>1e-5){const k=girth/rr;v.y*=k;v.z*=k;}
    v.y*=1.16;v.z*=.56;
    v.z+=Math.sin(pt*Math.PI)*.04;
    p.setXYZ(i,v.x,v.y,v.z);
  }
  g.computeVertexNormals();return g;
}
const BODY_GEO=bodyGeo(),EYE_GEO=new THREE.SphereGeometry(.135,14,10),PUP_GEO=new THREE.SphereGeometry(.082,12,8);
function shapeGeo(build,seg=12){
  const s=new THREE.Shape();build(s);
  return new THREE.ExtrudeGeometry(s,{depth:.032,bevelEnabled:false,curveSegments:seg});
}
const TAIL_GEO=shapeGeo(s=>{
  s.moveTo(0,0);
  s.bezierCurveTo(-.26,.14,-.52,.34,-1.0,.88);
  s.bezierCurveTo(-.74,.4,-.62,.16,-.58,0);
  s.bezierCurveTo(-.62,-.16,-.74,-.4,-1.0,-.88);
  s.bezierCurveTo(-.52,-.34,-.26,-.14,0,0);
});
const DORSAL_GEO=shapeGeo(s=>{
  s.moveTo(-.62,0);s.bezierCurveTo(-.3,.66,.15,.98,.68,.2);s.bezierCurveTo(.5,.1,.2,0,-.62,0);
});
const PELV_GEO=shapeGeo(s=>{
  s.moveTo(0,0);s.bezierCurveTo(-.14,-.28,-.4,-.5,-.66,-.62);s.bezierCurveTo(-.3,-.3,-.12,-.1,0,0);
},8);
const PEC_GEO=shapeGeo(s=>{
  s.moveTo(0,0);s.bezierCurveTo(.24,-.1,.42,-.3,.36,-.6);
  s.bezierCurveTo(.1,-.44,-.14,-.24,-.36,-.06);s.bezierCurveTo(-.2,-.02,-.1,0,0,0);
});

const schemeCache=SPECIES.map(sp=>{
  const map=fishTexture(sp);
  const body=new THREE.MeshPhysicalMaterial({
    map,bumpMap:map,bumpScale:.012,roughness:sp.rough,metalness:.1,
    clearcoat:.65,clearcoatRoughness:.22,iridescence:.4,iridescenceIOR:1.28,envMapIntensity:.9});
  const fin=new THREE.MeshPhysicalMaterial({
    color:new THREE.Color(sp.fin),transparent:true,opacity:.82,roughness:.3,metalness:.05,
    side:THREE.DoubleSide,depthWrite:false,iridescence:.7,iridescenceIOR:1.4,
    emissive:new THREE.Color(sp.acc),emissiveIntensity:.08,envMapIntensity:.9});
  const eye=new THREE.MeshPhysicalMaterial({color:0xf6fbf4,roughness:.12,clearcoat:1,envMapIntensity:1.2});
  const pupil=new THREE.MeshPhysicalMaterial({color:0x07090c,roughness:.06,metalness:.2,clearcoat:1});
  const iris=new THREE.MeshStandardMaterial({color:new THREE.Color(sp.acc),roughness:.3,metalness:.4,emissive:new THREE.Color(sp.acc),emissiveIntensity:.15});
  return {body,fin,eye,pupil,iris};
});

let fishId=0;const fishes=[];
function createFish(spIdx,x,y,z,opt={}){
  const sp=SPECIES[spIdx],sch=schemeCache[spIdx];
  const root=new THREE.Group(),body=new THREE.Group();root.add(body);
  const trunk=new THREE.Mesh(BODY_GEO,sch.body);trunk.scale.set(BODY_L,1,.92);
  trunk.castShadow=true;trunk.receiveShadow=true;trunk.userData.fish=null;body.add(trunk);
  for(const s of[1,-1]){
    const e=new THREE.Mesh(EYE_GEO,sch.eye);e.position.set(.6,.15,s*.3);e.scale.set(.7,1,1);body.add(e);
    const pu=new THREE.Mesh(PUP_GEO,sch.pupil);pu.position.set(.7,.155,s*.36);body.add(pu);
    const ir=new THREE.Mesh(new THREE.TorusGeometry(.105,.026,6,16),sch.iris);
    ir.position.set(.655,.15,s*.32);ir.rotation.y=Math.PI/2;ir.scale.y=1;body.add(ir);
  }
  const dor=new THREE.Mesh(DORSAL_GEO,sch.fin);dor.scale.set(.95,1.05,.8);dor.position.y=.9;body.add(dor);
  const dor2=new THREE.Mesh(PELV_GEO,sch.fin);dor2.rotation.z=Math.PI;dor2.scale.set(.5,.55,.6);
  dor2.position.set(-.85,.2,0);body.add(dor2);
  const pecs=[];
  for(const s of[1,-1]){
    const g=new THREE.Group();g.position.set(.32,-.02,s*.44);g.rotation.y=s*1.35;
    const m=new THREE.Mesh(PEC_GEO,sch.fin);m.scale.set(.62,.62,.5);g.add(m);body.add(g);pecs.push(g);
  }
  for(const s of[1,-1]){
    const pv=new THREE.Mesh(PELV_GEO,sch.fin);pv.scale.set(.5,.6,.5);
    pv.position.set(.05,-.5,s*.16);pv.rotation.z=s*.2;body.add(pv);
  }
  const tailA=new THREE.Group();tailA.position.set(-.98,0,0);body.add(tailA);
  const tailB=new THREE.Group();tailB.position.set(-.42,0,0);tailA.add(tailB);
  const fin=new THREE.Mesh(TAIL_GEO,sch.fin);fin.position.x=-.1;fin.scale.set(1.05,1.1,1);tailB.add(fin);

  root.traverse(o=>{if(o.isMesh){o.castShadow=true;o.frustumCulled=false;}});
  trunk.userData.fish=null;
  scene.add(root);

  const f={
    id:++fishId,root,body,trunk,pecs,tailA,tailB,dorsal:dor,sp,spIdx,
    pos:new THREE.Vector3(x,y,z),vel:new THREE.Vector3(rand(-1,1),rand(-.2,.2),rand(-1,1)).normalize(),
    quat:new THREE.Quaternion(),yaw:0,
    scale:opt.scale||rand(.6,1.2),tscale:0,grow:0,
    speed:opt.speed||rand(1.7,3.5),avoid:rand(2.1,3.7),
    freq:rand(5.4,9.2),phase:rand(0,TAU),amp:rand(.35,.62),
    wanderT:0,wander:new THREE.Vector3(),homeY:y,eaten:0,target:null,hunger:rand(.2,.7),
    visible:true
  };
  f.tscale=f.scale;
  trunk.userData.fish=f;
  fishes.push(f);updateStats();return f;
}
function spawnRandom(spIdx){
  if(fishes.length>=90){toast('Перенаселение — макс. 90','var(--coral)');return null;}
  const i=spIdx==null?ri(0,7):spIdx;
  const f=createFish(i,rand(-12,12),rand(-5,7),rand(-6,6));
  ping(f.pos,new THREE.Color(SPECIES[i].fin),2.6,.8);
  toast('Подсажен: '+SPECIES[i].name,new THREE.Color(SPECIES[i].base).getStyle());
  return f;
}

/* ══════════════ 10. КОРМ / ПУЗЫРИ / ЭФФЕКТЫ ══════════════ */
const foods=[],FOOD_GEO=new THREE.IcosahedronGeometry(.19,0);
const foodMat=new THREE.MeshStandardMaterial({color:0x9c5f2a,roughness:.85,emissive:0x331200,emissiveIntensity:.4});
const foodMat2=new THREE.MeshStandardMaterial({color:0xd8842f,roughness:.8,emissive:0x441b00,emissiveIntensity:.5});
function spawnFood(x,y,z){
  if(foods.length>150)return;
  const m=new THREE.Mesh(FOOD_GEO,Math.random()<.5?foodMat:foodMat2);
  m.position.set(x,y,z);m.scale.setScalar(rand(.7,1.35));m.castShadow=false;scene.add(m);
  foods.push({mesh:m,pos:m.position,vel:new THREE.Vector3(rand(-.5,.5),rand(-.2,.4),rand(-.5,.5)),
    seed:rand(0,10),age:0,eaten:false});
}
function feedBurst(n=1){
  for(let i=0;i<n;i++)
    spawnFood(rand(-12,12),rand(8.6,10.2),rand(-6,6));
  toast('Порция корма опущена','var(--sand)');
}

const bubbles=[],BUB_GEO=new THREE.SphereGeometry(1,14,10);
const bubMat=new THREE.MeshPhysicalMaterial({color:0xdffaff,transparent:true,opacity:.24,roughness:.03,
  metalness:0,clearcoat:1,ior:1.33,envMapIntensity:2.4,depthWrite:false,side:THREE.FrontSide});
function addBubble(){
  const r=rand(.09,.32);
  const b=new THREE.Mesh(BUB_GEO,bubMat);
  b.scale.setScalar(r);
  b.position.set(rand(-16,16),rand(-10,10),rand(-8.5,8.5));
  scene.add(b);
  bubbles.push({m:b,r:r,sp:rand(1.1,3)+1/r*.15,ph:rand(0,TAU),sw:rand(.2,.7)});
}
for(let i=0;i<30;i++)addBubble();
function addBubbles(n){for(let i=0;i<n;i++){addBubble();const b=bubbles[bubbles.length-1];
  b.m.position.set(rand(-15,15),rand(-10,-6),rand(-8,8));}updateStats();}

/* FX-кольца */
const RING_GEO=new THREE.TorusGeometry(1,.055,6,44),fx=[];
function ping(pos,color=new THREE.Color(0x7fe9ff),size=3,life=.7){
  let r=fx.find(o=>!o.live);
  if(!r){r=new THREE.Mesh(RING_GEO,new THREE.MeshBasicMaterial({transparent:true,blending:THREE.AdditiveBlending,
    depthWrite:false,depthTest:false,fog:false}));r.live=false;scene.add(r);fx.push(r);}
  r.live=true;r.t=0;r.life=life;r.size=size;r.position.copy(pos);
  r.material.color.copy(color);r.visible=true;r.quaternion.copy(camera.quaternion);
}
/* кольцо выбора */
const selRing=new THREE.Mesh(new THREE.TorusGeometry(2.1,.03,4,64),
  new THREE.MeshBasicMaterial({color:0x38e0c6,transparent:true,opacity:0,blending:THREE.AdditiveBlending,
    depthWrite:false,depthTest:false,fog:false}));
selRing.visible=false;scene.add(selRing);

/* ══════════════ 11. ФИЗИКА ПОВЕДЕНИЯ ══════════════ */
const LIM=new THREE.Vector3(15.4,8.6,7.6);
const _s=new THREE.Vector3(),_a=new THREE.Vector3(),_d=new THREE.Vector3(),_m=new THREE.Matrix4();
const _q=new THREE.Quaternion(),UP=new THREE.Vector3(0,1,0),Z90=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),Math.PI/2);
let timeScale=1,eatenTotal=0,paused=false;

function updateFish(dt,t){
  for(const f of fishes){
    const p=f.pos,v=f.vel;
    f.hunger=cl(f.hunger+dt*.012,0,1.4);
    if(Math.random()<dt*.02){f.homeY=rand(-6.5,7);if(f.hunger>.9)f.homeY=rand(-9,-5);}
    f.wanderT-=dt;
    if(f.wanderT<=0){
      f.wanderT=rand(1.4,3.6);
      f.wander.set(rand(-1,1),rand(-.5,.5),rand(-1,1)).normalize().multiplyScalar(f.speed*.55);
    }
    _a.copy(f.wander);
    /* избегание сородичей */
    for(const o of fishes){
      if(o===f)continue;
      const d2=p.distanceToSquared(o.pos),R=f.avoid+o.avoid;
      if(d2<R*R&&d2>1e-5){const d=Math.sqrt(d2);
        _s.copy(p).sub(o.pos).multiplyScalar((R-d)/d*7.5/d*R*.3);_a.add(_s);}
    }
    /* границы */
    const soft=.72;
    for(const ax of['x','y','z']){
      const L=LIM[ax],ab=Math.abs(p[ax]);
      if(ab>L*soft){const ov=(ab-L*soft)/(L*(1-soft));_a[ax]-=Math.sign(p[ax])*ov*ov*f.speed*5.2;}
      if(ab>L){p[ax]=Math.sign(p[ax])*L;v[ax]*=-.55;}
    }
    _a.y+=(f.homeY-p.y)*.1;
    /* корм */
    let tgt=null,best=15;
    for(const fd of foods){
      if(fd.eaten)continue;
      const d=p.distanceTo(fd.pos);
      if(d<best&&fd.pos.y>-10.1){best=d;tgt=fd;}
    }
    f.target=tgt;
    if(tgt){
      _d.copy(tgt.pos).sub(p);
      const dd=Math.max(_d.length(),.001);_d.divideScalar(dd);
      _a.addScaledVector(_d,f.speed*(3.4+2.4/dd));
      _a.addScaledVector(v,-1.1);
      if(dd<.85+f.scale*.5){
        tgt.eaten=true;f.hunger=Math.max(0,f.hunger-.34);f.eaten++;eatenTotal++;
        f.grow=Math.min(f.grow+.05,.8);f.tscale=Math.min(f.tscale*1.05,2.6);
        ping(tgt.pos,new THREE.Color(0xffd9a0),1.4,.5);
      }
    }
    v.addScaledVector(_a,dt);
    const maxV=f.speed*(tgt?2.3:1.15),sp=v.length();
    if(sp>maxV)v.multiplyScalar(maxV/sp);
    else if(sp<f.speed*.4&&sp>1e-4)v.multiplyScalar(f.speed*.4/Math.max(sp,1e-4));
    p.addScaledVector(v,dt*timeScale);
    /* ориентация */
    const dir=v.clone().normalize();
    const yaw=Math.atan2(dir.z,dir.x);
    let dy=yaw-f.yaw;while(dy>Math.PI)dy-=TAU;while(dy<-Math.PI)dy+=TAU;
    f.yaw=yaw;
    _m.lookAt(_d.set(0,0,0),_d.set(Math.cos(yaw),0,Math.sin(yaw)),UP);
    _q.setFromRotationMatrix(_m).multiply(Z90);
    f.quat.slerp(_q,1-Math.exp(-6*dt));
    f.root.position.copy(p);f.root.quaternion.copy(f.quat);
    /* рост */
    if(Math.abs(f.scale-f.tscale)>.001){f.scale+=(f.tscale-f.scale)*(1-Math.exp(-4*dt));
      f.root.scale.setScalar(f.scale);}
    /* анимация */
    const tt=t*f.freq*.55+f.phase,w=f.speed/f.speed;
    const wagAmp=f.amp*(.55+sp/f.speed*.55);
    f.tailA.rotation.y=Math.sin(tt)*wagAmp;
    f.tailB.rotation.y=Math.sin(tt-.9)*wagAmp*.62;
    f.body.rotation.y=Math.sin(tt-.35)*wagAmp*.14;
    f.body.rotation.z=cl(Math.asin(cl(dir.y,-1,1)),-.7,.7)*.92-Math.sin(tt)*.03;
    f.body.rotation.x=cl(-dy*1.6,-.5,.5);
    for(let i=0;i<f.pecs.length;i++)f.pecs[i].rotation.x=Math.sin(tt*.7+i*2.1)*.4+(tgt?-.3:.12);
    f.dorsal.rotation.y=Math.sin(tt*.5)*.06;
  }
}
function updateFood(dt,t){
  for(let i=foods.length-1;i>=0;i--){
    const fd=foods[i];
    if(fd.eaten){scene.remove(fd.mesh);foods.splice(i,1);updateStats();continue;}
    fd.age+=dt;
    fd.vel.y-=4.4*dt;
    fd.vel.x+=Math.sin(t*1.7+fd.seed)*.5*dt;fd.vel.z+=Math.cos(t*1.3+fd.seed)*.5*dt;
    fd.vel.multiplyScalar(1-1.1*dt);
    fd.pos.addScaledVector(fd.vel,dt*timeScale);
    fd.mesh.rotation.x+=dt*1.4;fd.mesh.rotation.y+=dt*.9;
    if(fd.pos.y<=-10.05||fd.age>90){
      ping(fd.pos,new THREE.Color(0xc9a06a),1.1,.55);
      scene.remove(fd.mesh);foods.splice(i,1);updateStats();
    }
  }
}
function updateBubbles(dt,t){
  for(const b of bubbles){
    const m=b.m;
    m.position.y+=b.sp*dt*timeScale;
    m.position.x+=Math.sin(t*1.6+b.ph)*b.sw*dt*2.2;
    m.position.z+=Math.cos(t*1.25+b.ph*1.7)*b.sw*dt*2.2;
    const s=b.r*(1+Math.sin(t*4+b.ph)*.07);
    m.scale.set(s,s*(1+.1*Math.sin(t*5+b.ph)),s);
    if(m.position.y>10.2){
      m.position.set(rand(-16,16),rand(-10.4,-8.4),rand(-8.6,8.6));
    }
  }
}

/* ══════════════ 12. ВВОД ══════════════ */
const ray=new THREE.Raycaster();ray.params.Points.threshold=.4;
const ptr=new THREE.Vector2(),plane=new THREE.Plane(new THREE.Vector3(0,1,0),-2);
let selected=null,downX=0,downY=0,downT=0;
const ring=el('ring');
addEventListener('pointermove',e=>{ring.classList.add('on');ring.style.transform=`translate(${e.clientX}px,${e.clientY}px)`;});
addEventListener('pointerleave',()=>ring.classList.remove('on'));
canvas.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;downT=performance.now();ring.classList.add('press');});
addEventListener('pointerup',e=>{ring.classList.remove('press');
  if(e.target!==canvas)return;
  if(Math.hypot(e.clientX-downX,e.clientY-downY)>7||performance.now()-downT>450)return;
  tap(e.clientX,e.clientY);
});
function pickables(){return fishes.filter(f=>f.visible).map(f=>f.trunk).concat([sand,...rocks]);}
function tap(cx,cy){
  ptr.set(cx/innerWidth*2-1,-(cy/innerHeight)*2+1);
  ray.setFromCamera(ptr,camera);
  const hits=ray.intersectObjects(pickables(),false);
  if(hits.length){
    const h=hits[0];
    if(h.object.userData.fish){selectFish(h.object.userData.fish);ping(h.point,new THREE.Color(0x38e0c6),2.4,.7);return;}
    const p=h.point.clone();p.y=cl(p.y+3.5,-8,10);
    spawnFood(p.x,p.y,p.z);ping(p,new THREE.Color(0xffd27a),2.2,.6);
  }else{
    const p=new THREE.Vector3();
    plane.constant=-3;
    if(ray.ray.intersectPlane(plane,p)){
      p.x=cl(p.x,-16,16);p.z=cl(p.z,-9,9);
      spawnFood(p.x,cl(p.y+4,-8,10),p.z);ping(p,new THREE.Color(0xffd27a),2.2,.6);
    }
  }
}
function selectFish(f){
  selected=f;
  const c=el('card');c.classList.add('show');
  el('dId').textContent='#'+String(f.id).padStart(2,'0');
  el('dName').textContent=f.sp.name;el('dLat').textContent=f.sp.lat;
  selRing.visible=true;selRing.material.color.set(f.sp.fin);
  updateCard();
}
function updateCard(){
  if(!selected)return;
  const f=selected;
  el('dSize').textContent=(f.scale*11.6).toFixed(1)+' см';
  el('dSpeed').textContent=(f.speed*.28).toFixed(2)+' м/с';
  el('dEat').textContent=f.eaten+' порц.';
  el('dFull').style.width=cl((1.4-f.hunger)/1.4*100,4,100)+'%';
}
el('dClose').onclick=()=>{el('card').classList.remove('show');selRing.visible=false;selected=null;};

/* кнопки */
el('bFish').onclick=()=>spawnRandom();
el('bFeed').onclick=()=>feedBurst(ri(4,7));
el('bBub').onclick=()=>{addBubbles(10);toast('+10 пузырьков','var(--cyan)');};
el('bLight').onclick=()=>{sunOn=sunOn?0:1;sunWant=sunOn?(nightMode?.28:2.2):.12;
  el('bLight').dataset.on=sunOn?'1':'0';toast('Свет '+((sunOn&&1)?'включён':'приглушён'),'var(--sand)');};
el('bNight').onclick=()=>{
  nightMode=!nightMode;el('bNight').dataset.on=nightMode?'1':'0';
  sunWant=sunOn?(nightMode?.3:2.2):.1;
  scene.background.setHex(nightMode?0x010a12:0x03151f);
  scene.fog.color.setHex(nightMode?0x031724:0x073244);
  ambient.intensity=nightMode?.18:.4;rim.intensity=nightMode?.22:.5;
  rim.color.setHex(nightMode?0x5aa0ff:0x8fe8ff);
  pt1.intensity=nightMode?560:430;pt2.intensity=nightMode?480:360;
  caustics.material.opacity=nightMode?.2:.5;
  caustics.material.color.setHex(nightMode?0x5f9fff:0x8ff0e6);
  cTex.repeat.set(3,2);
  shafts.children.forEach(s=>s.material.opacity*=nightMode?.6:1.6);
  dome.material.uniforms.top.value.setHex(nightMode?0x0d3b55:0x1a86a8);
  dome.material.uniforms.mid.value.setHex(nightMode?0x051d2c:0x0a4058);
  toast(nightMode?'Ночной режим · лунный свет':'Дневной режим','var(--gold)');
};
el('bCam').onclick=()=>{controls.autoRotate=!controls.autoRotate;el('bCam').dataset.on=controls.autoRotate?'1':'0';
  toast(controls.autoRotate?'Автоматический облёт вкл':'Облёт выкл','var(--aqua)');};
el('bReset').onclick=()=>{
  while(foods.length){scene.remove(foods.pop().mesh);}
  while(fishes.length){scene.remove(fishes.pop().root);}
  fishId=0;eatenTotal=0;selRing.visible=false;selected=null;el('card').classList.remove('show');
  seedStock();updateStats();toast('Резервуар перезапущен · 15 особей','var(--coral)');
};
el('sSpeed').oninput=e=>{timeScale=+e.target.value;el('oSpeed').textContent=timeScale.toFixed(2)+'×';};
el('sClarity').oninput=e=>{
  const c=+e.target.value;el('oClarity').textContent=Math.round(c*100)+'%';
  scene.fog.density=FOG_BASE-(FOG_BASE-FOG_MIN)*c;
  glassFront.material.opacity=.03+c*.08;
};
addEventListener('keydown',e=>{
  if(e.metaKey||e.ctrlKey||e.altKey)return;
  const k=e.key.toLowerCase();
  const map={n:'bFish',f:'bFeed',b:'bBub',l:'bLight',m:'bNight',c:'bCam',r:'bReset'};
  if(map[k]){e.preventDefault();el(map[k]).click();}
  if(k===' '){e.preventDefault();paused=!paused;el('tDot').style.background=paused?'var(--coral)':'var(--aqua)';
    toast(paused?'Пауза симуляции':'Симуляция продолжается','var(--coral)');}
});

/* палитра видов */
const spWrap=el('species');
SPECIES.forEach((sp,i)=>{
  const b=document.createElement('button');b.className='chip';b.title=sp.lat;
  b.innerHTML=`<i style="background:${sp.base};color:${sp.base}"></i><span>${sp.name}</span>`;
  b.onclick=()=>spawnRandom(i);spWrap.appendChild(b);
});

/* телеметрия */
const spark=el('spark'),sctx=spark.getContext('2d'),hist=[];
function updateStats(){
  el('tFish').textContent=fishes.length;
  el('tFood').textContent=foods.length;
  el('tBub').textContent=bubbles.length;
  el('tEat').textContent=eatenTotal;
  [...spWrap.children].forEach(c=>c.disabled=fishes.length>=90);
}
function drawSpark(){
  const w=spark.width,h=spark.height;sctx.clearRect(0,0,w,h);
  if(hist.length<2)return;
  const mx=Math.max(30,...hist),n=hist.length;
  const pt=i=>[i/(n-1)*w,h-cl(hist[i]/mx,0,1)*(h-8)-4];
  const g=sctx.createLinearGradient(0,0,0,h);
  g.addColorStop(0,'rgba(56,224,198,.5)');g.addColorStop(1,'rgba(56,224,198,0)');
  sctx.beginPath();sctx.moveTo(0,h);
  for(let i=0;i<n;i++){const[x,y]=pt(i);sctx.lineTo(x,y);}
  sctx.lineTo(w,h);sctx.closePath();sctx.fillStyle=g;sctx.fill();
  sctx.beginPath();
  for(let i=0;i<n;i++){const[x,y]=pt(i);i?sctx.lineTo(x,y):sctx.moveTo(x,y);}
  sctx.strokeStyle='#7ddff5';sctx.lineWidth=1.6;sctx.stroke();
  const[lx,ly]=pt(n-1);sctx.beginPath();sctx.arc(lx-1,ly,3,0,TAU);
  sctx.fillStyle='#e4f5fb';sctx.fill();
}

/* ══════════════ 13. ЦИКЛ ══════════════ */
const clock=new THREE.Clock();
let fpsAcc=0,fpsFrames=0,uiT=0,temp=25.8;
function tick(){
  requestAnimationFrame(tick);
  const raw=clock.getDelta(),t=clock.elapsedTime;
  const dt=paused?0:Math.min(raw,.05);
  /* свет плавно */
  sun.intensity+=(sunWant-sun.intensity)*(1-Math.exp(-3*raw));
  rim.intensity+=((nightMode?.22:.5)-rim.intensity)*.02;
  /* окружение */
  const P=cl(16+Math.sin(t*.18)*7,6,26);
  pt1.position.set(Math.cos(t*.16)*P,5+Math.sin(t*.21)*3,Math.sin(t*.16)*P*.6);
  pt2.position.set(Math.cos(t*.13+2.4)*P*.9,-3+Math.cos(t*.19)*2,Math.sin(t*.13+2.4)*P*.55);
  const pp=pt1.position,tw=Math.sin(t*.9)*.5+.5;
  pt3.position.set(pp.x*.2,9.2,0);
  caustics.material.opacity=(nightMode?.2:.5)*(.85+tw*.15);
  if(caustics.material.map){caustics.material.map.offset.x=t*.012;caustics.material.map.offset.y=t*.008;
    caustics.material.map.needsUpdate=false;}
  /* поверхность */
  const sp2=surfGeo.attributes.position;
  for(let i=0;i<sp2.count;i++){
    const x=sBase[i*3],z=sBase[i*3+2];
    sp2.setY(i,Math.sin(x*.34+t*1.5)*.2+Math.cos(z*.42-t*1.1)*.16+Math.sin((x+z)*.19+t*.7)*.11);
  }
  sp2.needsUpdate=true;surfGeo.computeVertexNormals();
  /* шахты */
  for(const s of shafts.children){
    s.position.x=s.userData.x0+Math.sin(t*s.userData.sp+s.userData.ph)*3.4;
    s.rotation.z=Math.sin(t*s.userData.sp*.6+s.userData.ph)*.11;
    s.material.opacity=s.material.opacity;
  }
  /* пыль */
  const dp=dGeo.attributes.position.array;
  for(let i=0;i<DUST;i++){
    dp[i*3+1]+=dt*.14;if(dp[i*3+1]>10.4)dp[i*3+1]=-10.4;
    dp[i*3]+=Math.sin(t*.4+i)*dt*.06;
  }
  dGeo.attributes.position.needsUpdate=true;
  /* растения */
  for(const pl of plants){
    const u=pl.userData;
    pl.rotation.x=Math.sin(t*.6+u.ph)*u.amp;
    pl.rotation.z=Math.cos(t*.44+u.ph)*u.amp*1.35;
  }
  /* камни слегка покачиваются? нет. */
  if(!paused){updateFish(dt,t);updateFood(dt,t);updateBubbles(dt,t);}
  /* FX */
  for(const r of fx){
    if(!r.live)continue;
    r.t+=raw;const k=r.t/r.life;
    if(k>=1){r.live=false;r.visible=false;continue;}
    const s=.2+k*r.size;r.scale.setScalar(s);
    r.material.opacity=(1-k)*.85;r.quaternion.copy(camera.quaternion);
  }
  if(selected){
    selRing.position.copy(selected.pos);selRing.quaternion.copy(camera.quaternion);
    const s=selected.scale*(1.35+Math.sin(t*3)*.06);
    selRing.scale.setScalar(s);selRing.material.opacity=.55+Math.sin(t*3)*.22;
    if(!selected.root.parent){selected=null;el('card').classList.remove('show');selRing.visible=false;}
    else updateCard();
  }
  controls.update();
  renderer.render(scene,camera);
  /* телеметрия */
  fpsAcc+=raw;fpsFrames++;uiT+=raw;
  if(fpsAcc>=.28){
    const f=fpsFrames/fpsAcc;hist.push(f);if(hist.length>110)hist.shift();
    el('tFps').firstChild.nodeValue=Math.round(f);
    el('tLux').textContent=sun.intensity.toFixed(2);
    drawSpark();fpsAcc=0;fpsFrames=0;
  }
  if(uiT>1){uiT=0;temp=25.6+Math.sin(t*.07)*.4+fishes.length*.004;
    el('tTemp').textContent=temp.toFixed(1)+'°C';}
}

/* ══════════════ 14. RESIZE / VISIBILITY ══════════════ */
function resize(){
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.4:1.8));
}
addEventListener('resize',resize);
document.addEventListener('visibilitychange',()=>{if(document.hidden)clock.getDelta();});

/* ══════════════ 15. СТАРТОВАЯ ЗАГРУЗКА ══════════════ */
function seedStock(){
  const bag=[0,0,1,1,2,3,4,5,6,7,7,2,4,5,3];
  bag.forEach(i=>createFish(i,rand(-12,12),rand(-5,7),rand(-6,6)));
  for(let i=0;i<3;i++)makePlant(rand(-14,14),rand(-7,7));
}
seedStock();
updateStats();
resize();tick();

/* Boot: вода поднимается по названию */
const bootEl=el('boot'),notes=['Наполнение резервуара','Засыпка субстрата','Расстановка камней',
  'Высадка водорослей','Запуск аэрации','Настройка освещения','Выпуск ихтиофауны'];
for(let i=0;i<16;i++){
  const b=document.createElement('i');b.className='bb';
  const s=rand(6,26);
  b.style.cssText=`left:${rand(2,98)}%;width:${s}px;height:${s}px;
    animation-duration:${rand(6,14)}s;animation-delay:${rand(-12,0)}s`;
  bootEl.appendChild(b);
}
requestAnimationFrame(()=>bootEl.classList.add('filling'));
let bp=0;
const iv=setInterval(()=>{
  bp=Math.min(100,bp+rand(2.6,7.5));
  el('bWater').style.width=bp+'%';
  el('bNote').textContent=notes[Math.min(notes.length-1,Math.floor(bp/100*notes.length))]+' · '+Math.round(bp)+'%';
  if(bp>=100){clearInterval(iv);
    el('bNote').textContent='Резервуар стабилен · готов к погружению';
    el('bootBtn').classList.add('ready');}
},95);
el('bootBtn').onclick=()=>{
  bootEl.classList.add('gone');document.body.classList.add('live');
  setTimeout(()=>bootEl.remove(),1100);
  ping(new THREE.Vector3(0,6,0),new THREE.Color(0x7ddff5),9,1.3);
  setTimeout(()=>toast('15 тропических особей запущены','var(--aqua)'),700);
  setTimeout(()=>{controls.autoRotate=true;el('bCam').dataset.on='1';},1400);
};
el('bCam').dataset.on='0';el('bLight').dataset.on='1';el('bNight').dataset.on='0';
</script>
</body>
</html>
```

## Что внутри

**Рыбки.** Тело — сфера с процедурным сечением по функции толщины (тупая морда → максимальная упитанность → тонкий хвостовой стебель), расплющенной по вертикали/горизонту. К каждой особи: вилочный хвост на двух последовательных суставах (даёт бегущую волну, а не болтанку), спинной, брюшные, анальный и два грудных плавника на отдельных группах. Глаз = белок + роговичный блик + тор-радужка в акцентном цвете схемы.

**Окрас.** 8 схем рисуются на canvas 512×256: countershading по UV (тёмная спина → светлое брюхо), затем паттерн (полосы-«клоун», палитра хирурга, языки пламени, ленты, крап, чешуйчатый ажур «императора»), поверх — сетка чешуи в режиме `overlay`, затемнение к хвосту и блик по боковой линии. Та же карта идёт в `bumpMap`, материал — `MeshPhysicalMaterial` с clearcoat и иридесценцией.

**ИИ.** Блуждание по таймеру → сила отталкивания от соседей в радиусе `avoid` → квадратичный отпор у стенок (с мягкой зоной 72 %) → пружина к любимой глубине → преследование корма в радиусе 15 с торможением → поедание (рост ×1.05, «сытость» в досье, вспышка-кольцо). Ориентация: root берёт только рыскание, тангаж и крен (при повороте рыбу заваливает) считаются внутри, амплитуда махов привязана к текущей скорости.

**Среда.** Стекло — `transmission: 0.95`, `ior 1.33`, `BackSide`, так что преломляется дальняя стенка (быстро и без «каши» из прозрачных объектов), а ближняя даёт отражение и лёгкую дымку; по рёбрам — `EdgesGeometry` плюс настоящий металлический каркас из 12 брусьев. Песок — 110×70 сегментов с fbm-рельефом, вершинными цветами и плоским затуханием к стенкам. 12 кустов водорослей — `TubeGeometry` на `CatmullRomCurve3` с наклонной и изогнутой осью, плюс взвесь, каустика (additive, дрейфующая UV), 6 световых шахт и волнующаяся поверхность, пересчитывающая нормали каждый кадр.

**Взаимодействие.** Клик по воде/камню — порция корма с гравитацией и дрейфом, клик по рыбке — досье (длина, скорость, съедено, сытость). Палитра из 8 видов работает как «подсадка», слайдеры меняют течение и плотность тумана, «Ночь» перекрашивает купол, свет и каустику в лунный синий. Клавиши: `N F B L M C R`, `Space` — пауза.