# 🐠 Аквариум — живая 3D-экосистема

Готовый однофайловый проект. Сохраните как `aquarium.html` и откройте в браузере.

```html
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>АКВАРИУМ · живая 3D-экосистема</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;0,9..144,900;1,9..144,700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ============ БАЗА ============ */
:root{
  --abyss:#02101b; --deep:#062234;
  --aqua:#5fe6d4; --aqua-d:#2b8ea3; --ice:#dff6ff;
  --sand:#e8c48d; --amber:#ffb45a; --coral:#ff6b5e;
  --txt:#e6f6ff; --muted:rgba(206,234,255,.56);
  --line:rgba(95,230,212,.22);
  --ch:14px;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0;overflow:hidden;background:#02101b;color:var(--txt);
  font-family:'IBM Plex Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
canvas#scene{position:fixed;inset:0;display:block;width:100%;height:100%;cursor:crosshair;touch-action:none}

/* ============ АТМОСФЕРНЫЕ ОВЕРЛЕИ ============ */
.fx{position:fixed;inset:0;pointer-events:none;z-index:2}
.fx--caustics{mix-blend-mode:screen;opacity:.85;
  background:
    radial-gradient(58% 42% at 18% -6%, rgba(130,235,255,.20), transparent 62%),
    radial-gradient(46% 34% at 82% -4%, rgba(80,190,255,.16), transparent 60%);
  animation:drift 26s ease-in-out infinite alternate}
.fx--caustics2{mix-blend-mode:screen;opacity:.5;
  background:radial-gradient(40% 30% at 55% -8%, rgba(190,255,245,.14), transparent 65%);
  animation:drift 17s ease-in-out infinite alternate-reverse}
@keyframes drift{from{transform:translate3d(-3%,0,0) scale(1)}to{transform:translate3d(4%,2%,0) scale(1.12)}}
.fx--vig{background:radial-gradient(125% 95% at 50% 42%, transparent 42%, rgba(0,7,14,.78) 100%)}
.fx--top{background:linear-gradient(180deg,rgba(3,26,42,.55),transparent 26%)}

/* ============ ПАНЕЛИ (сталь + стекло, фаска) ============ */
.panel{position:fixed;z-index:10;padding:1px;--ch:14px;
  background:linear-gradient(155deg,rgba(95,230,212,.46),rgba(95,230,212,.05) 46%,rgba(255,180,90,.26));
  clip-path:polygon(0 0,calc(100% - var(--ch)) 0,100% var(--ch),100% 100%,var(--ch) 100%,0 calc(100% - var(--ch)));
  backdrop-filter:blur(15px) saturate(150%);-webkit-backdrop-filter:blur(15px) saturate(150%);
  box-shadow:0 26px 60px -30px #000;
  transition:opacity .5s cubic-bezier(.2,.8,.2,1),transform .5s cubic-bezier(.2,.8,.2,1)}
.panel__in{--ch:13px;background:linear-gradient(168deg,rgba(7,36,55,.86),rgba(2,14,24,.9));
  clip-path:polygon(0 0,calc(100% - var(--ch)) 0,100% var(--ch),100% 100%,var(--ch) 100%,0 calc(100% - var(--ch)));
  padding:17px 17px 15px}
#panelL{left:20px;top:20px;width:302px;animation:panelInL 1s cubic-bezier(.2,.8,.2,1) .15s both}
#panelR{right:20px;top:20px;width:236px;animation:panelInR 1s cubic-bezier(.2,.8,.2,1) .3s both}
@keyframes panelInL{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes panelInR{from{opacity:0;transform:translateX(26px)}to{opacity:1;transform:none}}

/* ============ ЗАГОЛОВОК ============ */
.eyebrow{font:600 9.5px/1 'IBM Plex Mono',monospace;letter-spacing:.32em;color:var(--aqua);
  text-transform:uppercase;display:flex;align-items:center;gap:8px}
.eyebrow::before{content:"";width:16px;height:1px;background:var(--aqua);opacity:.7}
.pulse{width:5px;height:5px;border-radius:50%;background:var(--aqua);box-shadow:0 0 0 0 rgba(95,230,212,.7);
  animation:ping 2.4s ease-out infinite;flex:none}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(95,230,212,.6)}70%{box-shadow:0 0 0 9px rgba(95,230,212,0)}100%{box-shadow:0 0 0 0 rgba(95,230,212,0)}}
h1{margin:9px 0 0;font-family:'Fraunces',serif;font-weight:900;font-size:44px;line-height:.86;
  letter-spacing:-.035em;background:linear-gradient(178deg,#f4feff 8%,#7ef0dd 52%,#2a8fc0 96%);
  -webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 6px 18px rgba(60,190,220,.28))}
h1 em{display:block;font-style:italic;font-weight:700;font-size:20px;letter-spacing:.01em;
  background:linear-gradient(90deg,var(--amber),#ffd9a0);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{margin:10px 0 0;font-size:12.5px;line-height:1.45;color:var(--muted)}
.sub b{color:var(--ice);font-weight:600}

.rule{display:flex;align-items:center;gap:9px;margin:16px 0 11px;
  font:600 9px 'IBM Plex Mono',monospace;letter-spacing:.26em;color:rgba(206,234,255,.42);text-transform:uppercase}
.rule::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}

/* ============ ИНСТРУКЦИЯ ============ */
.keys{list-style:none;margin:0;padding:0;display:grid;gap:5px}
.keys li{display:grid;grid-template-columns:auto 1fr;gap:9px;align-items:center;
  font-size:11.5px;color:var(--muted)}
kbd{font:600 9px 'IBM Plex Mono',monospace;letter-spacing:.05em;padding:3px 6px;color:var(--ice);
  background:rgba(95,230,212,.09);border:1px solid rgba(95,230,212,.22);white-space:nowrap}

/* ============ КНОПКИ ============ */
.ctrls{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.btn{position:relative;display:flex;align-items:center;gap:8px;padding:9px 10px;border:0;cursor:pointer;
  color:#04222e;font:600 10px/1 'IBM Plex Mono',monospace;letter-spacing:.08em;text-transform:uppercase;
  background:linear-gradient(135deg,#7bf2e0,#2fb6c8);overflow:hidden;text-align:left;
  clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 8px));
  transition:transform .18s cubic-bezier(.2,.8,.2,1),box-shadow .25s,filter .25s}
.btn svg{width:14px;height:14px;flex:none;stroke-width:1.9}
.btn:hover{transform:translateY(-2px);box-shadow:0 10px 26px -10px rgba(95,230,212,.75);filter:brightness(1.07)}
.btn:active{transform:translateY(0) scale(.985)}
.btn::after{content:"";position:absolute;inset:0;transform:translateX(-125%);transition:transform .65s;
  background:linear-gradient(100deg,transparent 36%,rgba(255,255,255,.6) 50%,transparent 64%)}
.btn:hover::after{transform:translateX(125%)}
.btn--g{background:rgba(95,230,212,.07);color:var(--ice);box-shadow:inset 0 0 0 1px rgba(95,230,212,.26)}
.btn--g:hover{background:rgba(95,230,212,.15)}
.btn--w{grid-column:span 2;background:linear-gradient(135deg,var(--amber),#ff8f4a);color:#2a1200}
.btn--w:hover{box-shadow:0 10px 26px -10px rgba(255,160,80,.8)}
.btn[aria-pressed="true"]{background:linear-gradient(135deg,#ffe08a,#ffb45a);color:#2a1200;
  box-shadow:0 0 24px -6px rgba(255,180,90,.75)}
.btn[aria-pressed="true"]::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:#2a1200;opacity:.5}

/* ============ ЛЕГЕНДА МОРФ ============ */
.sp{display:grid;grid-template-columns:auto 1fr auto;gap:9px;align-items:center;padding:4px 5px;
  border-left:2px solid transparent;transition:.22s cubic-bezier(.2,.8,.2,1);cursor:default}
.sp:hover{background:rgba(95,230,212,.07);border-left-color:var(--aqua);transform:translateX(3px)}
.sw{width:11px;height:11px;background:currentColor;transform:rotate(45deg);
  box-shadow:0 0 14px -2px currentColor, inset 0 0 0 1px rgba(255,255,255,.35)}
.sp__n{font-size:11.5px;color:var(--ice);line-height:1.2}
.sp__l{display:block;font:400 8.5px 'IBM Plex Mono',monospace;letter-spacing:.06em;color:var(--muted);font-style:italic}
.sp__c{font:600 10px 'IBM Plex Mono',monospace;color:var(--aqua);
  background:rgba(95,230,212,.1);padding:2px 6px;min-width:22px;text-align:center}

/* ============ ТЕЛЕМЕТРИЯ ============ */
.fps{display:flex;align-items:flex-end;justify-content:space-between;gap:8px}
.big{font-family:'Fraunces',serif;font-weight:900;font-size:40px;line-height:.8;letter-spacing:-.04em;
  color:#fff;text-shadow:0 0 26px rgba(95,230,212,.4)}
.big small{font-size:11px;font-family:'IBM Plex Mono',monospace;font-weight:500;color:var(--muted);
  letter-spacing:.1em;margin-left:4px}
#spark{display:block;width:100%;height:30px;margin-top:8px;opacity:.9}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:12px}
.cell{padding:8px 9px;background:rgba(95,230,212,.05);box-shadow:inset 0 0 0 1px rgba(95,230,212,.13);
  transition:.25s}
.cell:hover{background:rgba(95,230,212,.11)}
.cell__k{display:block;font:500 8.5px 'IBM Plex Mono',monospace;letter-spacing:.16em;color:var(--muted);text-transform:uppercase}
.cell__v{display:block;font-family:'Fraunces',serif;font-weight:800;font-size:22px;line-height:1.15;color:var(--ice)}
.pop{animation:pop .5s cubic-bezier(.2,.8,.2,1)}
@keyframes pop{0%{transform:scale(1.28);color:var(--aqua)}100%{transform:scale(1);color:var(--ice)}}
.env__r{display:flex;justify-content:space-between;align-items:baseline;font-size:10.5px;color:var(--muted);margin-top:9px}
.env__r b{font:600 11px 'IBM Plex Mono',monospace;color:var(--ice);letter-spacing:.04em}
.bar{height:3px;background:rgba(255,255,255,.08);margin-top:4px;overflow:hidden}
.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--aqua-d),var(--aqua));
  transition:width 1.2s cubic-bezier(.4,0,.2,1);box-shadow:0 0 10px rgba(95,230,212,.6)}
.qual{margin-top:13px;font:500 9px 'IBM Plex Mono',monospace;letter-spacing:.14em;color:var(--muted);
  display:flex;justify-content:space-between;text-transform:uppercase}
.qual b{color:var(--amber)}

/* ============ ЛОГ + ПОДСКАЗКА ============ */
.log{position:fixed;left:20px;bottom:20px;z-index:9;display:flex;flex-direction:column-reverse;gap:5px;max-width:330px}
.log__i{font:500 10.5px/1.4 'IBM Plex Mono',monospace;letter-spacing:.02em;color:rgba(214,238,255,.75);
  background:rgba(2,16,26,.6);border-left:2px solid var(--aqua);padding:6px 9px;backdrop-filter:blur(7px);
  animation:logIn .5s cubic-bezier(.2,.8,.2,1) both}
.log__i--w{border-left-color:var(--amber)}
.log__i--c{border-left-color:var(--coral)}
.log__i.out{animation:logOut .5s forwards}
.log__t{color:var(--aqua);opacity:.6;margin-right:8px}
@keyframes logIn{from{opacity:0;transform:translateX(-16px)}to{opacity:1;transform:none}}
@keyframes logOut{to{opacity:0;transform:translateX(-10px)}}
.hint{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:9;display:flex;gap:10px;align-items:center;
  padding:9px 18px 9px 14px;background:rgba(2,18,28,.62);backdrop-filter:blur(10px);
  border:1px solid var(--line);font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.06em;color:var(--ice);
  transition:opacity .7s,transform .7s;animation:hintIn 1s cubic-bezier(.2,.8,.2,1) 1.4s both}
@keyframes hintIn{from{opacity:0;transform:translate(-50%,14px)}to{opacity:1;transform:translate(-50%,0)}}
.hint.off{opacity:0;transform:translate(-50%,14px);pointer-events:none}
.hint__d{width:8px;height:8px;border-radius:50%;background:var(--amber);animation:ping2 1.8s ease-out infinite}
@keyframes ping2{0%{box-shadow:0 0 0 0 rgba(255,180,90,.6)}75%{box-shadow:0 0 0 12px rgba(255,180,90,0)}}

/* ============ ТУЛТИП РЫБЫ ============ */
.tip{position:fixed;z-index:12;pointer-events:none;padding:7px 10px;background:rgba(2,16,26,.92);
  border:1px solid var(--line);box-shadow:0 10px 30px -12px #000;
  font:500 10.5px/1.45 'IBM Plex Mono',monospace;color:var(--ice);white-space:nowrap;
  opacity:0;transform:translate(-50%,-155%) scale(.94);transition:opacity .16s,transform .16s}
.tip.on{opacity:1;transform:translate(-50%,-155%) scale(1)}
.tip i{font-style:italic;color:var(--aqua)}

/* ============ КЛИК-ВОЛНА ============ */
.rip{position:fixed;z-index:11;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;
  border:1px solid rgba(95,230,212,.95);pointer-events:none;animation:rip .85s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes rip{to{width:120px;height:120px;margin:-60px 0 0 -60px;opacity:0;border-width:1px}}

/* ============ ЗАГРУЗЧИК ============ */
#loader{position:fixed;inset:0;z-index:60;display:grid;place-items:center;
  background:radial-gradient(circle at 50% 38%,#083450,#010a12 72%);transition:opacity .9s,visibility .9s}
#loader.gone{opacity:0;visibility:hidden}
.load{text-align:center}
.load__b{display:flex;gap:9px;justify-content:center;margin-bottom:20px}
.load__b i{width:9px;height:9px;border-radius:50%;background:rgba(140,235,255,.85);
  box-shadow:0 0 16px rgba(120,225,255,.8);animation:rise 1.5s ease-in-out infinite}
.load__b i:nth-child(2){animation-delay:.22s}.load__b i:nth-child(3){animation-delay:.44s}
.load__b i:nth-child(4){animation-delay:.66s}.load__b i:nth-child(5){animation-delay:.88s}
@keyframes rise{0%,100%{transform:translateY(8px) scale(.6);opacity:.35}50%{transform:translateY(-10px) scale(1.1);opacity:1}}
.load__t{font:600 12px 'IBM Plex Mono',monospace;letter-spacing:.42em;color:var(--ice);text-transform:uppercase}
.load__bar{width:220px;height:2px;background:rgba(255,255,255,.1);margin:16px auto 12px;overflow:hidden}
.load__bar i{display:block;height:100%;width:34%;background:linear-gradient(90deg,transparent,var(--aqua),transparent);
  animation:scan 1.4s linear infinite}
@keyframes scan{from{transform:translateX(-100%)}to{transform:translateX(400%)}}
.load__s{font:400 9.5px 'IBM Plex Mono',monospace;letter-spacing:.18em;color:var(--muted)}

/* ============ КНОПКА UI ============ */
#uiBtn{position:fixed;right:20px;bottom:20px;z-index:14;width:38px;height:38px;display:grid;place-items:center;
  cursor:pointer;background:rgba(2,18,28,.62);border:1px solid var(--line);color:var(--ice);backdrop-filter:blur(8px);
  transition:.25s}
#uiBtn:hover{background:rgba(95,230,212,.16);transform:translateY(-2px)}
body.ui-off .panel,body.ui-off .log,body.ui-off .hint{opacity:0;pointer-events:none}
body.ui-off #panelL{transform:translateX(-30px)}
body.ui-off #panelR{transform:translateX(30px)}

/* ============ АДАПТИВ ============ */
@media (max-width:1080px){
  h1{font-size:36px}#panelL{width:262px}#panelR{width:206px}
  .sp__l{display:none}
}
@media (max-width:820px){
  .keys,.legend,#panelR .grid2{display:none}
  #panelL{width:calc(100% - 32px);left:16px;top:16px}
  #panelR{width:auto;left:auto;right:16px;top:auto;bottom:70px}
  h1{font-size:30px}h1 em{font-size:15px}.sub{margin-bottom:2px}
  .log{display:none}.hint{font-size:9.5px;bottom:16px;padding:7px 12px}
  #uiBtn{bottom:16px;right:16px}
}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
</head>
<body>

<canvas id="scene"></canvas>
<div class="fx fx--caustics"></div>
<div class="fx fx--caustics2"></div>
<div class="fx fx--top"></div>
<div class="fx fx--vig"></div>

<!-- ================= ЛЕВО ПАНЕЛЬ ================= -->
<aside class="panel" id="panelL">
 <div class="panel__in">
  <div class="eyebrow">Гидросфера · модуль 07 <span class="pulse"></span></div>
  <h1>АКВАРИУМ<em>живая экосистема</em></h1>
  <p class="sub">Замкнутый биоконтур под наблюдением. В толще воды: <b id="sFish">15</b> особей, <b id="sBub">30</b> пузырьков, симуляция поведения в реальном времени.</p>

  <div class="rule">Управление</div>
  <ul class="keys">
    <li><kbd>ЛКМ</kbd><span>облёт вокруг аквариума</span></li>
    <li><kbd>ПКМ</kbd><span>сдвиг камеры</span></li>
    <li><kbd>КОЛЕСО</kbd><span>приближение 10–60</span></li>
    <li><kbd>КЛИК</kbd><span>уронить корм на воду</span></li>
  </ul>

  <div class="rule">Операции</div>
  <div class="ctrls">
    <button class="btn" id="bFish"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 12c4-6 12-6 16 0-4 6-12 6-16 0Z"/><path d="M19 12c1.5-2 3-3 3-3v6s-1.5-1-3-3Z"/><circle cx="8" cy="11" r=".8" fill="currentColor"/></svg>Рыбка</button>
    <button class="btn" id="bBub"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="9" cy="14" r="4"/><circle cx="16" cy="8" r="2.6"/><circle cx="17.5" cy="16" r="1.5"/></svg>Пузыри</button>
    <button class="btn btn--g" id="bLight" aria-pressed="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/></svg>Свет</button>
    <button class="btn btn--g" id="bRefr" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 6h16v12H4z"/><path d="M4 10h16M8 6v12"/></svg>Рефракция</button>
    <button class="btn btn--w" id="bFeed"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 3v8M8 6l4 5 4-5"/><circle cx="6" cy="18" r="1.6"/><circle cx="12" cy="19" r="1.6"/><circle cx="18" cy="18" r="1.6"/></svg>Покормить</button>
  </div>

  <div class="rule">Морфы · 8</div>
  <div class="legend" id="legend"></div>
 </div>
</aside>

<!-- ================= ПРАВО ПАНЕЛЬ ================= -->
<aside class="panel" id="panelR">
 <div class="panel__in">
  <div class="eyebrow">Телеметрия</div>
  <div class="fps"><div class="big" id="fps">60<small>К/С</small></div></div>
  <canvas id="spark" width="200" height="60"></canvas>
  <div class="grid2">
    <div class="cell"><span class="cell__k">Особей</span><span class="cell__v" id="cFish">15</span></div>
    <div class="cell"><span class="cell__k">Корм</span><span class="cell__v" id="cFood">0</span></div>
    <div class="cell"><span class="cell__k">Пузыри</span><span class="cell__v" id="cBub">30</span></div>
    <div class="cell"><span class="cell__k">Съедено</span><span class="cell__v" id="cEat">0</span></div>
  </div>
  <div class="rule">Среда</div>
  <div class="env__r"><span>Температура</span><b id="vT">24.8 °C</b></div><div class="bar"><i id="bT" style="width:62%"></i></div>
  <div class="env__r"><span>Кислотность</span><b id="vP">8.12 pH</b></div><div class="bar"><i id="bP" style="width:58%"></i></div>
  <div class="env__r"><span>Солёность</span><b id="vS">1.021</b></div><div class="bar"><i id="bS" style="width:44%"></i></div>
  <div class="qual"><span>Качество</span><b id="q">Ультра</b></div>
 </div>
</aside>

<div class="log" id="log"></div>
<div class="hint" id="hint"><span class="hint__d"></span>Кликните по воде — корм пойдёт ко дну</div>
<div class="tip" id="tip"></div>
<button id="uiBtn" title="Скрыть интерфейс (H)"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg></button>

<div id="loader"><div class="load">
  <div class="load__b"><i></i><i></i><i></i><i></i><i></i></div>
  <div class="load__t">Запуск экосистемы</div>
  <div class="load__bar"><i></i></div>
  <div class="load__s">инициализация гидросферы · three.js r128</div>
</div></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function(){
'use strict';
const $=s=>document.querySelector(s);
if(!window.THREE){$('#loader').innerHTML='<div class="load"><div class="load__t">Ошибка загрузки three.js</div></div>';return;}

/* ══════════════ КОНСТАНТЫ ══════════════ */
const TANK={w:36,h:24,d:20};
const HX=TANK.w/2, HY=TANK.h/2, HZ=TANK.d/2;
const SAND_Y=-HY+0.15, WATER_Y=HY-1.6;
const B={x:HX-1.5,yT:WATER_Y-1.3,yB:SAND_Y+1.7,z:HZ-1.5};
const C=h=>new THREE.Color(h).convertSRGBToLinear();
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const rnd=(a,b)=>a+Math.random()*(b-a);

/* ══════════════ РЕНДЕР ══════════════ */
const canvas=$('#scene');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
let DPR=Math.min(window.devicePixelRatio||1,1.75);
renderer.setPixelRatio(DPR); renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.32;
const WEBGL2=renderer.capabilities.isWebGL2;

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(C(0x073049),0.0155);

const camera=new THREE.PerspectiveCamera(52,innerWidth/innerHeight,.1,420);
const CAM_A=new THREE.Vector3(31,21,45), CAM_B=new THREE.Vector3(23,10.5,33);
camera.position.copy(CAM_A);

const controls=new THREE.OrbitControls(camera,canvas);
controls.enableDamping=true; controls.dampingFactor=.055;
controls.minDistance=10; controls.maxDistance=60;
controls.maxPolarAngle=Math.PI/1.8; controls.minPolarAngle=.12;
controls.zoomSpeed=.85; controls.target.set(0,-.5,0); controls.enabled=false;

/* ══════════════ ОКРУЖЕНИЕ (ENV) ══════════════ */
function buildEnv(){
  const cv=document.createElement('canvas');cv.width=256;cv.height=128;const g=cv.getContext('2d');
  const gr=g.createLinearGradient(0,0,0,128);
  gr.addColorStop(0,'#c8f4ff');gr.addColorStop(.3,'#57b9dd');gr.addColorStop(.62,'#0d4a6b');gr.addColorStop(1,'#02131f');
  g.fillStyle=gr;g.fillRect(0,0,256,128);
  const rg=g.createRadialGradient(66,16,0,66,16,52);rg.addColorStop(0,'rgba(255,255,238,1)');rg.addColorStop(1,'rgba(255,255,238,0)');
  g.fillStyle=rg;g.fillRect(0,0,256,70);
  const t=new THREE.CanvasTexture(cv);t.mapping=THREE.EquirectangularReflectionMapping;t.encoding=THREE.sRGBEncoding;
  const e=new THREE.PMREMGenerator(renderer).fromEquirectangular(t).texture;t.dispose();return e;
}
scene.environment=buildEnv();

/* градиентный купол «помещения */
const DOME_D={top:C(0x0d5c7f),mid:C(0x073049),bot:C(0x01080f)};
const DOME_N={top:C(0x04202f),mid:C(0x02121d),bot:C(0x00060b)};
const dome=new THREE.Mesh(new THREE.SphereGeometry(180,32,18),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,
  uniforms:{a:{value:DOME_D.top.clone()},b:{value:DOME_D.mid.clone()},c:{value:DOME_D.bot.clone()}},
  vertexShader:'varying vec3 vP;void main(){vP=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
  fragmentShader:'varying vec3 vP;uniform vec3 a,b,c;void main(){float h=normalize(vP).y;vec3 k=h>0.?mix(b,a,pow(h,.65)):mix(b,c,pow(-h,.55));gl_FragColor=vec4(k,1.);}'
}));
dome.frustumCulled=false;scene.add(dome);

/* ══════════════ СВЕТ ══════════════ */
const amb=new THREE.AmbientLight(C(0x40606f),0.55);scene.add(amb);
const sun=new THREE.DirectionalLight(C(0xfff2d6),1.55);
sun.position.set(16,34,12);sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.near=1;sun.shadow.camera.far=95;
sun.shadow.camera.left=-27;sun.shadow.camera.right=27;sun.shadow.camera.top=22;sun.shadow.camera.bottom=-22;
sun.shadow.bias=-0.0009;sun.shadow.normalBias=.03;
scene.add(sun);scene.add(sun.target);
const ptA=new THREE.PointLight(C(0x59e2ff),1.15,72,2);ptA.position.set(-12,7,-6);scene.add(ptA);
const ptB=new THREE.PointLight(C(0x2f6bff),.95,84,2);ptB.position.set(13,-6,7);scene.add(ptB);

/* ══════════════ ТЕКСТУРЫ ══════════════ */
function causticTex(){
  const S=256,cv=document.createElement('canvas');cv.width=cv.height=S;const g=cv.getContext('2d');
  const im=g.createImageData(S,S),d=im.data;
  for(let y=0;y<S;y++)for(let x=0;x<S;x++){
    const u=x/S*Math.PI*2,v=y/S*Math.PI*2;
    const f=(Math.sin(u*3+Math.sin(v*2+1.3)*1.6)+Math.sin(v*2-Math.sin(u*3)*1.3)+Math.sin((u+v)*2+.7))/3;
    let b=Math.pow(Math.max(0,Math.cos(f*Math.PI*1.55)),7);
    b+=Math.pow(Math.max(0,Math.cos(f*Math.PI*3.1)),14)*.5;
    const i=(y*S+x)*4;const c=Math.min(255,b*255)|0;d[i]=d[i+1]=d[i+2]=c;d[i+3]=255;
  }
  g.putImageData(im,0,0);
  const t=new THREE.CanvasTexture(cv);t.wrapS=t.wrapT=THREE.RepeatWrapping;return t;
}
function sandTex(){
  const S=512,cv=document.createElement('canvas');cv.width=cv.height=S;const g=cv.getContext('2d');
  g.fillStyle='#c9a878';g.fillRect(0,0,S,S);
  for(let i=0;i<300;i++){const x=Math.random()*S,y=Math.random()*S,r=12+Math.random()*70;
    const rg=g.createRadialGradient(x,y,0,x,y,r);const l=Math.random()>.5?'rgba(240,215,175,':'rgba(140,110,78,';
    rg.addColorStop(0,l+(.05+Math.random()*.13)+')');rg.addColorStop(1,l+'0)');g.fillStyle=rg;g.beginPath();g.arc(x,y,r,0,7);g.fill();}
  for(let i=0;i<14000;i++){const x=Math.random()*S|0,y=Math.random()*S|0;
    g.fillStyle=Math.random()>.5?'rgba(255,240,208,.30)':'rgba(88,66,42,.28)';g.fillRect(x,y,1,1);}
  const t=new THREE.CanvasTexture(cv);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(4,2.4);
  t.encoding=THREE.sRGBEncoding;t.anisotropy=4;return t;
}
function shaftTex(){
  const cv=document.createElement('canvas');cv.width=64;cv.height=256;const g=cv.getContext('2d');
  const gr=g.createLinearGradient(0,0,0,256);gr.addColorStop(0,'rgba(255,255,255,.9)');
  gr.addColorStop(.45,'rgba(255,255,255,.28)');gr.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=gr;g.fillRect(0,0,64,256);
  const hd=g.createLinearGradient(0,0,64,0);hd.addColorStop(0,'rgba(0,0,0,1)');hd.addColorStop(.5,'rgba(0,0,0,0)');
  hd.addColorStop(1,'rgba(0,0,0,1)');g.globalCompositeOperation='destination-out';g.fillStyle=hd;g.fillRect(0,0,64,256);
  return new THREE.CanvasTexture(cv);
}
const CAUS=causticTex();

/* ══════════════ ДНО ══════════════ */
function dune(x,z){
  let h=Math.sin(x*.32)*Math.cos(z*.41)*.55+Math.sin(x*.71+1.7)*Math.cos(z*.55-.6)*.28+Math.sin(x*1.6+z*.9)*.09;
  const e=Math.max(0,Math.abs(x)/HX-.62)*3.1+Math.max(0,Math.abs(z)/HZ-.62)*3.4;
  return h+e*e*.55;
}
const sandGeo=new THREE.PlaneGeometry(TANK.w,TANK.d,110,62);sandGeo.rotateX(-Math.PI/2);
{const p=sandGeo.attributes.position,v=new THREE.Vector3();
 for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);p.setZ(i,dune(v.x,v.y));}
 sandGeo.computeVertexNormals();}
const sandMat=new THREE.MeshStandardMaterial({map:sandTex(),roughness:.97,metalness:0,
  emissiveMap:CAUS.clone(),emissive:C(0x35b6d6),emissiveIntensity:.5});
sandMat.emissiveMap.repeat.set(2,1.2);sandMat.emissiveMap.wrapS=sandMat.emissiveMap.wrapT=THREE.RepeatWrapping;
sandMat.emissiveMap.needsUpdate=true;
const sand=new THREE.Mesh(sandGeo,sandMat);sand.position.y=SAND_Y;sand.receiveShadow=true;scene.add(sand);

/* пол «комнаты */
const floor=new THREE.Mesh(new THREE.CircleGeometry(140,48),
  new THREE.MeshStandardMaterial({color:C(0x061420),roughness:.9,metalness:.15}));
floor.rotation.x=-Math.PI/2;floor.position.y=-HY-1.3;floor.receiveShadow=true;scene.add(floor);

/* ══════════════ СТЕКЛ + РАМА ══════════════ */
const tank=new THREE.Group();scene.add(tank);
const glassMats=[];
function wall(w,h,pos,rotY){
  const m=new THREE.MeshPhysicalMaterial({color:C(0xaee9ff),transparent:true,opacity:.13,roughness:.03,
    metalness:0,clearcoat:1,clearcoatRoughness:.03,ior:1.45,envMapIntensity:1.5,depthWrite:false,side:THREE.DoubleSide});
  glassMats.push(m);
  const g=new THREE.Mesh(new THREE.PlaneGeometry(w,h),m);
  g.position.copy(pos);g.rotation.y=rotY;tank.add(g);
}
wall(TANK.w,TANK.h,new THREE.Vector3(0,0,-HZ),0);
wall(TANK.w,TANK.h,new THREE.Vector3(0,0,HZ),Math.PI);
wall(TANK.d,TANK.h,new THREE.Vector3(-HX,0,0),Math.PI/2);
wall(TANK.d,TANK.h,new THREE.Vector3(HX,0,0),-Math.PI/2);

const edges=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(TANK.w,TANK.h,TANK.d)),
  new THREE.LineBasicMaterial({color:C(0x8ff0ff),transparent:true,opacity:.3}));tank.add(edges);

const frameMat=new THREE.MeshStandardMaterial({color:C(0x9fb8c6),metalness:.88,roughness:.32,envMapIntensity:1.3});
const barG=new THREE.BoxGeometry(1,1,1);
function bar(w,h,d,x,y,z){const m=new THREE.Mesh(barG,frameMat);m.scale.set(w,h,d);m.position.set(x,y,z);m.castShadow=true;tank.add(m);}
[HY,-HY].forEach(y=>{bar(TANK.w+.7,.6,.6,0,y,HZ);bar(TANK.w+.7,.6,.6,0,y,-HZ);
  bar(.6,.6,TANK.d+.7,HX,y,0);bar(.6,.6,TANK.d+.7,-HX,y,0);});
[[HX,HZ],[HX,-HZ],[-HX,HZ],[-HX,-HZ]].forEach(p=>bar(.62,TANK.h,.62,p[0],0,p[1]));
const base=new THREE.Mesh(new THREE.BoxGeometry(TANK.w+1.6,1.4,TANK.d+1.6),
  new THREE.MeshStandardMaterial({color:C(0x16242e),metalness:.5,roughness:.65}));
base.position.y=-HY-.85;base.castShadow=true;base.receiveShadow=true;tank.add(base);

/* ══════════════ КАМНИ ══════════════ */
function hash3(x,y,z){const s=Math.sin(x*127.1+y*311.7+z*74.7)*43758.5453;return s-Math.floor(s);}
function vnoise(v){
  const x=Math.floor(v.x*1.7),y=Math.floor(v.y*1.7),z=Math.floor(v.z*1.7);
  const fx=v.x*1.7-x,fy=v.y*1.7-y,fz=v.z*1.7-z;
  let a=0;a+=hash3(x,y,z)*(1-fx)*(1-fy)*(1-fz);a+=hash3(x+1,y,z)*fx*(1-fy)*(1-fz);
  a+=hash3(x,y+1,z)*(1-fx)*fy*(1-fz);a+=hash3(x+1,y+1,z)*fx*fy*(1-fz);
  a+=hash3(x,y,z+1)*(1-fx)*(1-fy)*fz;a+=hash3(x+1,y,z+1)*fx*(1-fy)*fz;
  a+=hash3(x,y+1,z+1)*(1-fx)*fy*fz;a+=hash3(x+1,y+1,z+1)*fx*fy*fz;return a;
}
const rockGroup=new THREE.Group();scene.add(rockGroup);
for(let i=0;i<8;i++){
  const g=new THREE.DodecahedronGeometry(1,0),p=g.attributes.position,v=new THREE.Vector3();
  for(let k=0;k<p.count;k++){v.fromBufferAttribute(p,k);const n=.72+vnoise(v)*.62;v.multiplyScalar(n);p.setXYZ(k,v.x,v.y,v.z);}
  g.computeVertexNormals();
  const t=Math.random();
  const mat=new THREE.MeshStandardMaterial({color:C(0x6b7078).lerp(C(0x8a7a63),t),roughness:.92,metalness:.05,flatShading:true});
  const m=new THREE.Mesh(g,mat);
  const s=rnd(.9,2.5);m.scale.set(s*rnd(.8,1.3),s*rnd(.45,.8),s*rnd(.8,1.3));
  const a=Math.random()*Math.PI*2,r=rnd(4,15);
  const px=Math.cos(a)*r,pz=Math.sin(a)*rnd(3,7.5);
  m.position.set(px,SAND_Y+dune(px,pz)+m.scale.y*.28,pz);
  m.rotation.set(rnd(-.3,.3),Math.random()*6.28,rnd(-.3,.3));
  m.castShadow=m.receiveShadow=true;rockGroup.add(m);
}

/* ══════════════ ВОДОРОСЛИ ══════════════ */
const weeds=[];
for(let i=0;i<12;i++){
  const grp=new THREE.Group(),n=3+(Math.random()*4|0);
  const hue=.26+Math.random()*.17;
  const mat=new THREE.MeshStandardMaterial({color:new THREE.Color().setHSL(hue,.58,.31).convertSRGBToLinear(),
    roughness:.72,metalness:0,side:THREE.DoubleSide});
  for(let k=0;k<n;k++){
    const h=rnd(3.2,9),lx=rnd(-2.4,2.4),lz=rnd(-2.4,2.4),seed=Math.random()*10,pts=[];
    for(let j=0;j<=6;j++){const t=j/6;
      pts.push(new THREE.Vector3(lx*t*t+Math.sin(t*3.1+seed)*.3*t,t*h,lz*t*t+Math.cos(t*2.6+seed)*.3*t));}
    const geo=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),14,rnd(.09,.16),5,false);
    geo.scale(1,1,.3);
    const m=new THREE.Mesh(geo,mat);m.rotation.y=Math.random()*6.28;m.castShadow=true;grp.add(m);
  }
  const a=Math.random()*Math.PI*2,r=rnd(3,15.5);
  const px=Math.cos(a)*r,pz=Math.sin(a)*rnd(2.5,7.6);
  grp.position.set(px,SAND_Y+dune(px,pz)-.1,pz);
  grp.userData={ph:Math.random()*6.28,amp:rnd(.05,.11)};
  scene.add(grp);weeds.push(grp);
}

/* ══════════════ АМФОРА ══════════════ */
{
  const pts=[];for(let i=0;i<=12;i++){const t=i/12;pts.push(new THREE.Vector2(Math.sin(t*Math.PI*.9)*.85+.13,t*2.3));}
  const pot=new THREE.Mesh(new THREE.LatheGeometry(pts,18),
    new THREE.MeshStandardMaterial({color:C(0x9c5b38),roughness:.78,metalness:.05}));
  pot.position.set(-11,SAND_Y+dune(-11,-4)+.1,-4);pot.rotation.set(.42,1.1,.28);
  pot.castShadow=pot.receiveShadow=true;scene.add(pot);
  for(let i=0;i<14;i++){const s=rnd(.14,.34);
    const pb=new THREE.Mesh(new THREE.DodecahedronGeometry(s,0),new THREE.MeshStandardMaterial({color:C(0x7d848c),roughness:.9,flatShading:true}));
    const a=Math.random()*6.28,d=rnd(1.1,2.6),px=pot.position.x+Math.cos(a)*d,pz=pot.position.z+Math.sin(a)*d;
    pb.position.set(px,SAND_Y+dune(px,pz)+s*.5,pz);pb.rotation.set(Math.random()*3,Math.random()*3,0);
    pb.castShadow=pb.receiveShadow=true;scene.add(pb);}
}

/* ══════════════ ПОВЕРХНОСТЬ ВОДЫ + ЛУЧИ ══════════════ */
const surfTex=CAUS.clone();surfTex.wrapS=surfTex.wrapT=THREE.RepeatWrapping;surfTex.repeat.set(3,1.8);surfTex.needsUpdate=true;
const surf=new THREE.Mesh(new THREE.PlaneGeometry(TANK.w-.5,TANK.d-.5),
  new THREE.MeshBasicMaterial({map:surfTex,color:C(0x9fe8ff),transparent:true,opacity:.16,
    blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide}));
surf.rotation.x=-Math.PI/2;surf.position.y=WATER_Y;scene.add(surf);
const surf2=new THREE.Mesh(new THREE.PlaneGeometry(TANK.w-.5,TANK.d-.5),
  new THREE.MeshPhysicalMaterial({color:C(0x9de5ff),transparent:true,opacity:.11,roughness:.08,
    metalness:0,envMapIntensity:1.6,depthWrite:false,side:THREE.DoubleSide}));
surf2.rotation.x=-Math.PI/2;surf2.position.y=WATER_Y-.02;scene.add(surf2);

const shafts=new THREE.Group();scene.add(shafts);
const shTex=shaftTex();
for(let i=0;i<5;i++){
  const m=new THREE.Mesh(new THREE.PlaneGeometry(rnd(2.4,4.6),22),
    new THREE.MeshBasicMaterial({map:shTex,color:C(0xa9f0ff),transparent:true,opacity:rnd(.05,.10),
      blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:true}));
  m.position.set(rnd(-14,14),WATER_Y-11,rnd(-7,7));m.rotation.y=Math.random()*6.28;m.rotation.z=rnd(-.14,.14);
  shafts.add(m);
}

/* ══════════════ МОРФЫ РЫБ ══════════════ */
const SPECIES=[
 {k:'clown',ru:'Оранжевая',la:'Amphiprion ocellaris',base:0xff7a2f,dark:0x9c3a10,belly:0xffe0b5,fin:0xff9a4d,stripe:0xfff4e2,pat:'band',metal:.06,rough:.42},
 {k:'tang',ru:'Синяя',la:'Paracanthurus hepatus',base:0x2166d8,dark:0x082a63,belly:0x9ad6ff,fin:0xffd23f,stripe:0xa6e8ff,pat:'net',metal:.14,rough:.36},
 {k:'sunset',ru:'Жёлто-красная',la:'Symphysodon discus',base:0xffc42e,dark:0xc4331a,belly:0xffeab0,fin:0xff6f2c,stripe:0xffe3b8,pat:'gradient',metal:.1,rough:.4},
 {k:'violet',ru:'Фиолетовая',la:'Microlepidotus',base:0x8b5cf6,dark:0x351a70,belly:0xdcc9ff,fin:0xa78bfa,stripe:0xf2e9ff,pat:'band',metal:.12,rough:.38},
 {k:'cardinal',ru:'Красная',la:'Cardinalis cardinalis',base:0xe23b3b,dark:0x66111c,belly:0xffb8ac,fin:0xff7d6c,stripe:0xffd9cf,pat:'spot',metal:.08,rough:.42},
 {k:'emerald',ru:'Зелёная',la:'Chromis viridis',base:0x2fbf71,dark:0x0a4c33,belly:0xc4f7d6,fin:0x53dfa4,stripe:0xe2fff0,pat:'stripe',metal:.22,rough:.3},
 {k:'galaxy',ru:'Розовая',la:'Danio galacticus',base:0xf472b6,dark:0x762350,belly:0xffdcec,fin:0xff9dd0,stripe:0xffffff,pat:'spot',metal:.16,rough:.34},
 {k:'gold',ru:'Золотая',la:'Carassius auratus',base:0xf5c542,dark:0x8a5a12,belly:0xfff3c4,fin:0xffd97a,stripe:0xfff8dc,pat:'sheen',metal:.85,rough:.2}
];
function hashStr(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function mul(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function makeSkin(sp){
  if(sp._t)return sp._t;
  const W=160,H=256,cv=document.createElement('canvas');cv.width=W;cv.height=H;
  const ctx=cv.getContext('2d'),im=ctx.createImageData(W,H),d=im.data;
  const base=new THREE.Color(sp.base),dark=new THREE.Color(sp.dark),belly=new THREE.Color(sp.belly),stripe=new THREE.Color(sp.stripe);
  const c=new THREE.Color(),R=mul(hashStr(sp.k));
  const bands=[];if(sp.pat==='band'){const n=3+(R()*2|0);for(let i=0;i<n;i++)bands.push({c:.2+i*(.6/Math.max(1,n-1))+(R()-.5)*.05,w:.045+R()*.035});}
  const spots=[];if(sp.pat==='spot')for(let i=0;i<44;i++)spots.push({u:R(),v:.06+R()*.8,r:.016+R()*.028});
  for(let y=0;y<H;y++){
    const v=1-y/(H-1);
    for(let x=0;x<W;x++){
      const u=x/W,dorso=Math.cos((u-.25)*Math.PI*2);
      c.copy(base);
      c.lerp(dark,Math.pow(Math.max(0,-dorso),1.15)*.82);
      c.lerp(belly,Math.pow(Math.max(0,dorso),1.3)*.85);
      if(sp.pat==='band')for(const b of bands){const dd=Math.abs(v-b.c);if(dd<b.w*2.2)c.lerp(stripe,(1-dd/(b.w*2.2))*.88);}
      if(sp.pat==='gradient')c.lerp(dark,Math.pow(Math.max(0,(v-.3)/.7),1.4)*.85);
      if(sp.pat==='net'){const n=Math.abs(Math.sin(u*24+Math.sin(v*9)*2.2))*Math.abs(Math.sin(v*15-u*3));if(n<.14)c.lerp(dark,.62);}
      if(sp.pat==='stripe'){const lat=1-Math.pow(Math.abs(Math.sin(u*Math.PI*2)),.55);if(lat>.9&&v>.12&&v<.9)c.lerp(stripe,(lat-.9)*7*.8);}
      if(sp.pat==='spot')for(const s of spots){let du=Math.abs(u-s.u);du=Math.min(du,1-du);
        const dd=Math.sqrt(du*du*1.6+(v-s.v)*(v-s.v)*.35);if(dd<s.r)c.lerp(stripe,(1-dd/s.r)*.85);}
      if(sp.pat==='sheen'){const sh=Math.pow(Math.max(0,Math.sin((u*3.4+v*1.1)*Math.PI*5)),26);c.lerp(stripe,sh*.55+Math.pow(Math.max(0,dorso*.5+.5),4)*.2);}
      const lat2=1-Math.pow(Math.abs(Math.sin(u*Math.PI*2)),.35);if(lat2>.985)c.lerp(dark,.28);
      c.lerp(dark,Math.pow(Math.max(0,(.26-v)/.26),1.6)*.5);
      c.lerp(dark,Math.pow(Math.max(0,(v-.9)/.1),2)*.35);
      const nq=(Math.sin(v*96)*Math.sin(u*44))*.022+(R()-.5)*.05;
      const i=(y*W+x)*4;
      d[i]=clamp(c.r+nq,0,1)*255;d[i+1]=clamp(c.g+nq,0,1)*255;d[i+2]=clamp(c.b+nq,0,1)*255;d[i+3]=255;
    }
  }
  ctx.putImageData(im,0,0);
  const t=new THREE.CanvasTexture(cv);t.encoding=THREE.sRGBEncoding;t.wrapS=THREE.RepeatWrapping;t.anisotropy=4;
  sp._t=t;return t;
}

/* ══════════════ ГЕОМЕТРИИ РЫБЫ ══════════════ */
const FG={};
(function buildGeos(){
  const g=new THREE.SphereGeometry(1,26,18);g.rotateX(Math.PI/2);
  const p=g.attributes.position,v=new THREE.Vector3();
  for(let i=0;i<p.count;i++){
    v.fromBufferAttribute(p,i);
    const t=(v.z+1)*.5;
    const w=.36*Math.pow(Math.sin(Math.PI*Math.pow(t,.66)),.9)+.02;
    const h=.44*Math.pow(Math.sin(Math.PI*Math.pow(t,.58)),.8)+.025;
    const a=Math.atan2(v.y,v.x),ca=Math.cos(a),sa=Math.sin(a);
    const r=(w*h)/Math.sqrt(h*h*ca*ca+w*w*sa*sa);
    v.set(ca*r,sa*r+ .06*Math.pow(Math.max(0,-v.z),2),v.z);
    p.setXYZ(i,v.x,v.y,v.z);
  }
  g.computeVertexNormals();FG.body=g;

  const sh=(arr,rot)=>{const s=new THREE.Shape();s.moveTo(arr[0][0],arr[0][1]);
    for(let i=1;i<arr.length;i+=4){if(arr.length>i+3)s.bezierCurveTo(arr[i][0],arr[i][1],arr[i+1][0],arr[i+1][1],arr[i+2][0],arr[i+2][1]);else s.lineTo(arr[i][0],arr[i][1]);}
    s.closePath();const gg=new THREE.ShapeGeometry(s,10);if(rot)gg.rotateY(-Math.PI/2);return gg;};
  FG.tail=(()=>{const s=new THREE.Shape();s.moveTo(0,0);
    s.quadraticCurveTo(-.3,.14,-.66,.6);s.quadraticCurveTo(-.44,.13,-.4,0);
    s.quadraticCurveTo(-.44,-.13,-.66,-.6);s.quadraticCurveTo(-.3,-.14,0,0);
    const g=new THREE.ShapeGeometry(s,10);g.rotateY(-Math.PI/2);return g;})();
  FG.dorsal=sh([[-.55,.30],[-.34,.95],[.16,.98],[.44,.30]]);
  FG.anal=(()=>{const s=new THREE.Shape();s.moveTo(-.5,-.26);s.quadraticCurveTo(-.24,-.78),s.quadraticCurveTo(-.04,-.28,-.5,-.26);
    const g=new THREE.ShapeGeometry(s,8);g.rotateY(-Math.PI/2);return g;})();
  FG.pec=(()=>{const s=new THREE.Shape();s.moveTo(0,.13);s.quadraticCurveTo(.44,.22,.64,-.05);
    s.quadraticCurveTo(.36,-.24,0,-.11);s.closePath();const g=new THREE.ShapeGeometry(s,8);g.rotateX(-Math.PI/2);return g;})();
  FG.eye=new THREE.SphereGeometry(.085,12,10);
  FG.pupil=new THREE.SphereGeometry(.05,10,8);
})();
const eyeMat=new THREE.MeshStandardMaterial({color:C(0xf7fbff),roughness:.12,metalness:0,envMapIntensity:1.5});
const pupilMat=new THREE.MeshStandardMaterial({color:C(0x080c11),roughness:.05,metalness:.2,envMapIntensity:2});

/* ══════════════ РЫБЫ ══════════════ */
const fishes=[],fishBodies=[];
let fishId=0,eaten=0;
function addFish(speci,pos,silent){
  const sp=SPECIES[speci];
  const grp=new THREE.Group(),body=new THREE.Group();grp.add(body);
  if(!sp._bm){
    sp._bm=new THREE.MeshStandardMaterial({map:makeSkin(sp),roughness:sp.rough,metalness:sp.metal,envMapIntensity:.95});
    sp._fm=new THREE.MeshStandardMaterial({color:C(sp.fin),roughness:.48,metalness:sp.metal*.5,
      side:THREE.DoubleSide,transparent:true,opacity:.94,envMapIntensity:.9});
  }
  const bm=new THREE.Mesh(FG.body,sp._bm);bm.castShadow=true;body.add(bm);
  const tp=new THREE.Group();tp.position.z=-.92;body.add(tp);
  const tail=new THREE.Mesh(FG.tail,sp._fm);tail.castShadow=true;tp.add(tail);
  const dor=new THREE.Mesh(FG.dorsal,sp._fm);body.add(dor);
  const ana=new THREE.Mesh(FG.anal,sp._fm);body.add(ana);
  const pl=new THREE.Group(),pr=new THREE.Group();
  pl.position.set(-.23,-.09,.3);pr.position.set(.23,-.09,.3);
  const ml=new THREE.Mesh(FG.pec,sp._fm);ml.rotation.y=Math.PI;pl.add(ml);pr.add(new THREE.Mesh(FG.pec,sp._fm));
  body.add(pl,pr);
  [1,-1].forEach(s=>{
    const eg=new THREE.Group();eg.position.set(.2*s,.1,.44);
    eg.add(new THREE.Mesh(FG.eye,eyeMat));
    const pu=new THREE.Mesh(FG.pupil,pupilMat);pu.position.set(.052*s,.006,.062);eg.add(pu);body.add(eg);
  });
  const size=rnd(.6,1.2)*1.15;
  grp.scale.setScalar(size);
  grp.position.copy(pos||(function(){return new THREE.Vector3(rnd(-13,13),rnd(2,8),rnd(-6.5,6.5));})());
  scene.add(grp);
  const f={mesh:grp,body,bodyMesh:bm,tail:tp,leftFin:pl,rightFin:pr,dorsal:dor,
    velocity:new THREE.Vector3(rnd(-1,1),rnd(-.2,.2),rnd(-1,1)),speed:rnd(1.5,3.1),
    tailSpeed:rnd(4.5,8.5),phase:Math.random()*6.28,targetFood:null,avoidanceRadius:rnd(2.2,3.6),
    dir:new THREE.Vector3(rnd(-1,1),rnd(-.2,.2),rnd(-1,1)).normalize(),change:rnd(1,4),
    size:size,base:size,prevYaw:0,turn:0,scare:0,pulse:0,hover:0,speci:speci,id:++fishId};
  bm.userData.fish=f;fishes.push(f);fishBodies.push(bm);
  counts[speci]++;renderLegend();
  if(!silent)log('Новая особь · <i>'+sp.la.toLowerCase()+'</i> #'+f.id);
  return f;
}
const counts=new Array(8).fill(0);
for(let i=0;i<15;i++)addFish(i%8,null,true);

/* ══════════════ ПУЗЫРИ ══════════════ */
const bubbles=[];
const bubGeo=new THREE.SphereGeometry(1,12,10);
const bubMat=new THREE.MeshPhysicalMaterial({color:C(0xe4f8ff),transparent:true,opacity:.32,roughness:.02,
  metalness:0,clearcoat:1,ior:1.33,envMapIntensity:2.2,depthWrite:false});
function addBubble(n){
  for(let i=0;i<n;i++){
    const m=new THREE.Mesh(bubGeo,bubMat);const s=rnd(.1,.34);m.scale.setScalar(s);
    m.position.set(rnd(-15,15),rnd(SAND_Y,WATER_Y),rnd(-8,8));
    scene.add(m);bubbles.push({m:m,sp:rnd(1.4,3.4)*(1.3-s),ph:Math.random()*6.28,w:rnd(.7,2.1),bx:m.position.x,bz:m.position.z});
  }
}
addBubble(30);

/* ══════════════ КОРМ ══════════════ */
const foods=[],foodGeo=new THREE.IcosahedronGeometry(.17,0);
const foodMat=new THREE.MeshStandardMaterial({color:C(0xb4651f),roughness:.85,emissive:C(0x3a1a05),emissiveIntensity:.35});
function dropFood(x,z,silent){
  const n=3+(Math.random()*3|0);
  for(let i=0;i<n;i++){
    const m=new THREE.Mesh(foodGeo,foodMat);m.scale.setScalar(rnd(.65,1.3));
    m.position.set(clamp(x+rnd(-.9,.9),-B.x,B.x),WATER_Y-.25,clamp(z+rnd(-.9,.9),-B.z,B.z));
    m.castShadow=true;m.userData={v:new THREE.Vector3(rnd(-.5,.5),-.2,rnd(-.5,.5)),rest:0,seed:Math.random()*9};
    scene.add(m);foods.push(m);
  }
  ripple(x,z);
  if(!silent)log('Порция корма доставлена · '+n+' частиц','w');
}
const ripples=[];
const ripGeo=new THREE.RingGeometry(.3,.42,36);ripGeo.rotateX(-Math.PI/2);
function ripple(x,z){
  const m=new THREE.Mesh(ripGeo,new THREE.MeshBasicMaterial({color:C(0xa8f2ff),transparent:true,
    opacity:.6,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide}));
  m.position.set(clamp(x,-B.x,B.x),WATER_Y+.03,clamp(z,-B.z,B.z));
  scene.add(m);ripples.push({m:m,t:0});
}

/* ══════════════ ИИ РЫБ ══════════════ */
const tmp1=new THREE.Vector3(),tmp2=new THREE.Vector3(),dummy=new THREE.Object3D();
function soft(p,st,ax,mn,mx,k){
  const m=2.4;
  if(p[ax]>mx-m)st[ax]-=(p[ax]-(mx-m))*k;
  if(p[ax]<mn+m)st[ax]+=((mn+m)-p[ax])*k;
}
function updateFish(f,dt,t){
  const p=f.mesh.position,st=tmp1.set(0,0,0);
  f.change-=dt;
  if(f.change<=0){f.change=rnd(2.5,6);f.dir.set(rnd(-1,1),rnd(-.3,.3),rnd(-1,1)).normalize();}
  f.dir.x+=rnd(-.6,.6)*dt;f.dir.y+=rnd(-.25,.25)*dt;f.dir.z+=rnd(-.6,.6)*dt;f.dir.normalize();

  soft(p,st,'x',-B.x,B.x,3.1);soft(p,st,'y',B.yB,B.yT,3.4);soft(p,st,'z',-B.z,B.z,3.1);

  for(let i=0;i<fishes.length;i++){
    const o=fishes[i];if(o===f)continue;
    const d2=p.distanceToSquared(o.mesh.position),R=f.avoidanceRadius;
    if(d2<R*R&&d2>1e-4){const d=Math.sqrt(d2);tmp2.subVectors(p,o.mesh.position).multiplyScalar((1-d/R)/(d*R*.55));st.add(tmp2);}
  }
  f.targetFood=null;let best=15*15;
  for(let i=0;i<foods.length;i++){const d2=p.distanceToSquared(foods[i].position);if(d2<best){best=d2;f.targetFood=foods[i];}}

  let want=f.speed*(.55+.45*Math.sin(t*.35+f.phase));
  if(f.targetFood){tmp2.subVectors(f.targetFood.position,p).normalize();st.addScaledVector(tmp2,3.4);want=f.speed*2.3;}
  else st.addScaledVector(f.dir,1.15);
  if(f.scare>0){f.scare-=dt;want*=2.4;st.addScaledVector(f.dir,2.2);}

  f.velocity.addScaledVector(st,dt*2.4);
  const sp=f.velocity.length()||1e-5;
  const ns=sp+(want-sp)*Math.min(1,dt*1.7);
  f.velocity.multiplyScalar(ns/sp);
  p.addScaledVector(f.velocity,dt);
  p.x=clamp(p.x,-B.x,B.x);p.y=clamp(p.y,B.yB,B.yT);p.z=clamp(p.z,-B.z,B.z);

  dummy.position.copy(p);dummy.up.set(0,1,0);dummy.lookAt(tmp2.copy(p).add(f.velocity));
  f.mesh.quaternion.slerp(dummy.quaternion,1-Math.exp(-5.5*dt));

  const yaw=Math.atan2(f.velocity.x,f.velocity.z);
  let dy=yaw-f.prevYaw;while(dy>Math.PI)dy-=6.2832;while(dy<-Math.PI)dy+=6.2832;
  f.turn+=(dy/Math.max(dt,1e-3)-f.turn)*Math.min(1,dt*6);
  f.prevYaw=yaw;

  f.pulse*=Math.exp(-dt*3.2);f.hover+=(0-f.hover)*Math.min(1,dt*6);
  const hv=f.hoverT>0?(f.hoverT-=dt,1):0;f.hover=Math.max(f.hover,hv);
  const sc=1+f.pulse*.09+f.hover*.05;
  f.body.rotation.z=clamp(-f.turn*.2,-.5,.5);
  f.mesh.scale.setScalar(f.size*sc);

  const v=f.velocity.length(),amp=.26+Math.min(v*.17,.44);
  const wag=Math.sin(t*f.tailSpeed+f.phase);
  f.tail.rotation.y=wag*amp;
  f.body.rotation.y=Math.sin(t*f.tailSpeed+f.phase-.9)*.07;
  const fl=Math.sin(t*f.tailSpeed*.55+f.phase);
  f.rightFin.rotation.z=.3-fl*.3;f.leftFin.rotation.z=-.3+fl*.3;
  f.rightFin.rotation.y=fl*.16;f.leftFin.rotation.y=-fl*.16;
  f.dorsal.rotation.z=Math.sin(t*f.tailSpeed*.5+f.phase+1.4)*.05;

  if(f.targetFood&&p.distanceTo(f.targetFood.position)<.75*f.size+0.15){eat(f,f.targetFood);}
}
function eat(f,fd){
  const i=foods.indexOf(fd);if(i<0)return;
  scene.remove(fd);foods.splice(i,1);
  f.size=Math.min(f.base*1.9,f.size*1.05);f.pulse=1;eaten++;
  setVal('#cEat',eaten);
  log('Особь #'+f.id+' · корм +5% <i>'+SPECIES[f.speci].la.toLowerCase()+'</i>');
}

/* ══════════════ UI ══════════════ */
const logEl=$('#log');
function clock(){const s=(performance.now()/1000)|0;return 'T+'+String((s/60|0)%100).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}
function log(msg,k){
  const e=document.createElement('div');e.className='log__i'+(k?' log__i--'+k:'');
  e.innerHTML='<span class="log__t">'+clock()+'</span>'+msg;
  logEl.prepend(e);while(logEl.children.length>5)logEl.lastChild.remove();
  setTimeout(()=>{e.classList.add('out');setTimeout(()=>e.remove(),500);},7200);
}
function renderLegend(){
  const el=$('#legend');el.innerHTML='';
  SPECIES.forEach((s,i)=>{
    const li=document.createElement('div');li.className='sp';
    li.innerHTML='<span class="sw" style="color:#'+s.base.toString(16).padStart(6,'0')+'"></span>'+
      '<span class="sp__n">'+s.ru+'<i class="sp__l">'+s.la+'</i></span><span class="sp__c">'+counts[i]+'</span>';
    li.onmouseenter=()=>{hoverSpeci=i;};li.onmouseleave=()=>{hoverSpeci=-1;};
    el.appendChild(li);
  });
}
let hoverSpeci=-1;
function setVal(sel,v){const e=$(sel);if(e.textContent===String(v))return;e.textContent=v;e.classList.remove('pop');void e.offsetWidth;e.classList.add('pop');}

$('#bFish').onclick=()=>{if(fishes.length>=60){log('Достигнут предел популяции (60)','c');return;}addFish(Math.random()*8|0);};
$('#bBub').onclick=()=>{addBubble(10);log('Аэрация усилена · +10 пузырьков');};
$('#bFeed').onclick=()=>{for(let i=0;i<3;i++)dropFood(rnd(-12,12),rnd(-6,6),i>0);};
let sunOn=true;
$('#bLight').onclick=e=>{sunOn=!sunOn;e.currentTarget.setAttribute('aria-pressed',sunOn);
  log(sunOn?'Основной свет включён':'Основной свет выключен · ночной режим',sunOn?'':'w');};
let refract=false;
$('#bRefr').onclick=e=>{
  if(!WEBGL2){log('Рефракция требует WebGL2','c');return;}
  refract=!refract;e.currentTarget.setAttribute('aria-pressed',refract);
  glassMats.forEach(m=>{
    if(refract){m.transmission=.95;m.thickness=.5;m.ior=1.33;m.opacity=.9;m.roughness=.06;}
    else{m.transmission=0;m.thickness=0;m.opacity=.13;m.roughness=.03;}
    m.transparent=true;m.depthWrite=false;m.needsUpdate=true;
  });
  log(refract?'Преломление стекла включено':'Преломление стекла выключено');
};
$('#uiBtn').onclick=()=>document.body.classList.toggle('ui-off');
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k===' '){e.preventDefault();for(let i=0;i<3;i++)dropFood(rnd(-12,12),rnd(-6,6),i>0);}
  if(k==='f')$('#bFish').click(); if(k==='b')$('#bBub').click();
  if(k==='l')$('#bLight').click(); if(k==='h')$('#uiBtn').click();
});

/* клик = кормёжка (не путать с орбитой) */
let dx0=0,dy0=0,dt0=0,moved=false;const ndc=new THREE.Vector2(),ray=new THREE.Raycaster();
const tipEl=$('#tip');let tipOn=false,lastHover=0,mx=0,my=0;
const box=new THREE.Box3(new THREE.Vector3(-HX,-HY,-HZ),new THREE.Vector3(HX,HY,HZ));
canvas.addEventListener('pointerdown',e=>{dx0=e.clientX;dy0=e.clientY;dt0=performance.now();moved=false;controls.autoRotate=false;});
canvas.addEventListener('pointermove',e=>{
  if(Math.abs(e.clientX-dx0)+Math.abs(e.clientY-dy0)>7)moved=true;
  ndc.x=(e.clientX/innerWidth)*2-1;ndc.y=-(e.clientY/innerHeight)*2+1;mx=e.clientX;my=e.clientY;
});
addEventListener('pointerup',e=>{
  if(e.target!==canvas)return;
  if(moved||performance.now()-dt0>420)return;
  const r=document.createElement('div');r.className='rip';r.style.left=e.clientX+'px';r.style.top=e.clientY+'px';
  document.body.appendChild(r);setTimeout(()=>r.remove(),900);
  ndc.x=(e.clientX/innerWidth)*2-1;ndc.y=-(e.clientY/innerHeight)*2+1;
  ray.setFromCamera(ndc,camera);
  const hit=ray.ray.intersectBox(box,new THREE.Vector3());
  if(!hit)return;
  dropFood(hit.x,hit.z);
  $('#hint').classList.add('off');
  ray.setFromCamera(ndc,camera);
  const hs=ray.intersectObjects(fishBodies,false);
  if(hs.length){const f=hs[0].object.userData.fish;if(f){f.scare=.9;f.dir.x+=(Math.random()-.5);f.dir.normalize();}}
});

/* ══════════════ СПАРКЛАЙН FPS ══════════════ */
const sp=$('#spark'),sx=sp.getContext('2d'),hist=[];
function drawSpark(){
  const w=sp.width,h=sp.height;sx.clearRect(0,0,w,h);
  const g=sx.createLinearGradient(0,0,0,h);g.addColorStop(0,'rgba(95,230,212,.85)');g.addColorStop(1,'rgba(95,230,212,.06)');
  sx.fillStyle=g;sx.beginPath();sx.moveTo(0,h);
  hist.forEach((v,i)=>{const x=i/(hist.length-1)*w,y=h-clamp(v/75,0,1)*h;i?sx.lineTo(x,y):sx.lineTo(0,y);});
  sx.lineTo(w,h);sx.closePath();sx.fill();
  sx.strokeStyle='rgba(140,245,225,.9)';sx.lineWidth=1.5;sx.beginPath();
  hist.forEach((v,i)=>{const x=i/(hist.length-1)*w,y=h-clamp(v/75,0,1)*h;i?sx.lineTo(x,y):sx.moveTo(x,y);});
  sx.stroke();
}

/* ══════════════ ЦИКЛ ══════════════ */
let last=performance.now()/1000,T=0,frames=0,fpsT=0,fpsVal=60,intro=0,lowT=0,quality=2;
const qNames=['Эконом','Сбаланс.','Ультра'];
function loop(){
  requestAnimationFrame(loop);
  const now=performance.now()/1000;let dt=now-last;last=now;
  if(dt>.05)dt=.05;T+=dt;

  /* интро-наезд */
  if(intro<1){intro=Math.min(1,intro+dt/2.8);const e=1-Math.pow(1-intro,3);
    camera.position.lerpVectors(CAM_A,CAM_B,e);
    if(intro>=1){controls.enabled=true;controls.autoRotate=true;controls.autoRotateSpeed=.35;
      log('Экосистема стабильна · наблюдение начато');}}
  controls.update();

  /* рыба */
  for(let i=0;i<fishes.length;i++)updateFish(fishes[i],dt,T);

  /* корм */
  for(let i=foods.length-1;i>=0;i--){
    const fd=foods[i],u=fd.userData;
    if(u.rest>0){
      u.rest+=dt;
      const k=1-Math.max(0,(u.rest-6)/3);fd.scale.setScalar(Math.max(.001,k*(.65+.65*k)));
      if(u.rest>9){scene.remove(fd);foods.splice(i,1);}
      continue;
    }
    u.v.y-=4.4*dt;u.v.multiplyScalar(1-.55*dt);
    fd.position.addScaledVector(u.v,dt);
    fd.position.x+=Math.sin(T*1.5+u.seed)*.12*dt;
    fd.rotation.x+=dt*1.4;fd.rotation.z+=dt;
    const gy=SAND_Y+dune(fd.position.x,fd.position.z)+.16;
    if(fd.position.y<=gy){fd.position.y=gy;u.v.set(0,0,0);u.rest=.01;}
  }

  /* пузыри */
  for(let i=0;i<bubbles.length;i++){
    const b=bubbles[i];b.m.position.y+=b.sp*dt;
    b.m.position.x=b.bx+Math.sin(T*b.w+b.ph)*.55;
    b.m.position.z=b.bz+Math.cos(T*b.w*.8+b.ph)*.4;
    b.m.rotation.y+=dt;
    if(b.m.position.y>WATER_Y-.35){
      b.m.position.y=SAND_Y+rnd(.2,1.6);b.bx=rnd(-15,15);b.bz=rnd(-8,8);b.sp=rnd(1.4,3.4);
    }
  }

  /* волны на поверхности */
  for(let i=ripples.length-1;i>=0;i--){
    const r=ripples[i];r.t+=dt;const k=r.t/1.1;
    r.m.scale.setScalar(1+k*7);r.m.material.opacity=.6*(1-k);
    if(k>=1){scene.remove(r.m);r.m.material.dispose();ripples.splice(i,1);}
  }

  /* водоросли */
  for(let i=0;i<weeds.length;i++){const w=weeds[i],u=w.userData;
    w.rotation.x=Math.sin(T*.7+u.ph)*u.amp;w.rotation.z=Math.cos(T*.55+u.ph)*u.amp;}

  /* вода / каустика */
  surfTex.offset.x+=dt*.012;surfTex.offset.y+=dt*.008;
  sandMat.emissiveMap.offset.x+=dt*.006;sandMat.emissiveMap.offset.y-=dt*.004;
  shafts.rotation.y+=dt*.012;
  shafts.children.forEach((s,i)=>{s.material.opacity=(.045+.035*Math.sin(T*.4+i*1.7))*(sunOn?1:.35);});

  /* свет / ночной режим */
  const kL=Math.min(1,dt*2.2);
  sun.intensity+=((sunOn?1.55:.12)-sun.intensity)*kL;
  ptA.intensity+=((sunOn?1.15:2.1)-ptA.intensity)*kL;
  ptB.intensity+=((sunOn?.95:1.9)-ptB.intensity)*kL;
  renderer.toneMappingExposure+=((sunOn?1.32:.88)-renderer.toneMappingExposure)*kL;
  sandMat.emissiveIntensity+=((sunOn?.5:.16)-sandMat.emissiveIntensity)*kL;
  const tgt=sunOn?DOME_D:DOME_N;
  dome.material.uniforms.a.value.lerp(tgt.top,kL);
  dome.material.uniforms.b.value.lerp(tgt.mid,kL);
  dome.material.uniforms.c.value.lerp(tgt.bot,kL);
  scene.fog.color.lerp(sunOn?C(0x073049):C(0x02121d),kL);

  /* подсветка морфы при наведении на легенду */
  if(hoverSpeci>=0){for(const f of fishes)f.hoverT=f.speci===hoverSpeci?.05:f.hoverT;}

  /* hover-подсказка по рыбе */
  if(performance.now()-lastHover>60&&!moved){
    lastHover=performance.now();
    ray.setFromCamera(ndc,camera);
    const hs=ray.intersectObjects(fishBodies,false);
    if(hs.length){
      const f=hs[0].object.userData.fish;
      if(f){f.hoverT=.05;
        tipEl.innerHTML='<i>'+SPECIES[f.speci].la+'</i><br>особь #'+f.id+' · '+(f.size*13).toFixed(1)+' см';
        tipEl.style.left=mx+'px';tipEl.style.top=my+'px';tipEl.classList.add('on');tipOn=true;}
    }else if(tipOn){tipEl.classList.remove('on');tipOn=false;}
  }

  /* телеметрия */
  frames++;
  if(now-fpsT>.4){
    fpsVal=frames/(now-fpsT);frames=0;fpsT=now;
    hist.push(fpsVal);if(hist.length>56)hist.shift();
    drawSpark();$('#fps').innerHTML=Math.round(fpsVal)+'<small>К/С</small>';
    setVal('#cFish',fishes.length);setVal('#sFish',fishes.length);
    setVal('#cFood',foods.length);setVal('#cBub',bubbles.length);setVal('#sBub',bubbles.length);
    const t=24.6+Math.sin(T*.05)*.5,p=8.1+Math.sin(T*.031)*.09,s=1.021+Math.sin(T*.021)*.002;
    $('#vT').textContent=t.toFixed(1)+' °C';$('#bT').style.width=((t-20)/8*100).toFixed(0)+'%';
    $('#vP').textContent=p.toFixed(2)+' pH';$('#bP').style.width=((p-7.6)/1*100).toFixed(0)+'%';
    $('#vS').textContent=s.toFixed(3);$('#bS').style.width=((s-1.015)/.012*100).toFixed(0)+'%';
    /* авто-качество */
    if(fpsVal<28){lowT+=now-fpsT;
      if(lowT>3.5&&quality>0){quality--;
        if(quality===1){DPR=1;renderer.setPixelRatio(1);}
        else if(refract){$('#bRefr').click();}
        else{renderer.shadowMap.enabled=false;scene.traverse(o=>{if(o.material)o.material.needsUpdate=true;});}
        $('#q').textContent=qNames[quality];log('Авто-качество → '+qNames[quality],'w');lowT=0;}
    }else lowT=Math.max(0,lowT-.5);
  }

  renderer.render(scene,camera);
  if(intro<dt*1.2&&$('#loader')){$('#loader').classList.add('gone');setTimeout(()=>{const l=$('#loader');if(l)l.remove();},1000);}
}
loop();

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
setTimeout(()=>log('Совет: клик по воде запускает корм, клавиша <b>Space</b> — сытость'),3500);
})();
</script>
</body>
</html>
```

## Что внутри

**Рыбы.** Тело — сфера с loft-профилем (сечение-эллипс по длине), процедурная «кожа» генерируется попиксельно: спинка темнее, брюшко светлее, узор (полосы / пятна / продольная линия / сетка / перелив) оборачивается вокруг корпуса без шва. Хвост — веерная форма на шарнире по оси Y, грудные плавники машут в противофазе, спинной и подтыльный дополняют силуэт. Глаз = склера + зрачок.

**Поведение.** Блуждание с медленно дрейфующим вектором цели, мягкое отталкивание от соседей, упругое отражение от стенок, обнаружение корма в радиусе 15, рывок к нему, рост на 5 % с «глотком», крен при повороте (bank по угловой скорости), амплитуда хвоста зависит от реальной скорости.

**Среда.** Песок — procedural-дюны с бермами у стён, каустика на нём живёт в `emissiveMap` и дрейфует. 12 кустов TubeGeometry + CatmullRomCurve3, сплюснутые в ленты. 8 деформированных додекаэдров (шум детерминирован по позиции — грани не рвутся). Разбитая амфора с обломками, лучи света, поверхность воды с аддитивной каустикой, пузыри, рамка и стеклянные стены.

**Интерфейс.** HUD в стиле океанографического прибора: фаска вместо скруглений, Fraunces + IBM Plex, живая легенда 8 морф со счётчиками, спарклайн FPS, дрейфующие датчики среды, лента событий, тултип с латинским названием при наведении на рыбу. Ночной режим плавно перекрашивает туман, купол и тонмаппинг. Есть авто-деградация качества при просадке FPS.