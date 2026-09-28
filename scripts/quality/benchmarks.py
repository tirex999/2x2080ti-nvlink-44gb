# -*- coding: utf-8 -*-
"""Три эталонные задачи и проверки к ним.

Проверки выведены ИЗ ТЕКСТА задания: каждая соответствует явно названному в
промпте требованию, так что вердикт перепроверяется по спецификации, а не на
доверии ко мне.

ПРАВКА 01.09 после первого же прогона аквариума. Инструмент врал в обе стороны:
  - «8 цветовых схем» искала colorSchemes, а модель написала COLOR_SCHEMES —
    ложный промах. Теперь имя ловится в любом написании.
  - «отражение от стен» искала слова bounds/reflect, а модель сделала это через
    `if (p.x > BOUND_X) velocity.x = -Math.abs(...)` — тоже ложный промах.
  - у майнкрафта стояли проверки вида \\b16\\b, \\b80\\b, \\b7\\b — такие проходят
    на ЛЮБОМ тексте, то есть завышали оценку. Привязаны к смыслу.
Правило, которое из этого следует: проверка обязана ловить ТРЕБОВАНИЕ, а не
конкретное написание, и не должна проходить на постороннем коде.
"""

import os
_P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")

BENCHMARKS = {

    "хомяки": {
        "файл": os.path.join(_P, "hamster_prompt.txt"),
        "название": "Хомяки",
        "описание": "Клетка с лоу-поли хомяками, один предмет, автономное поведение",
        "порог": 7,
        "проверки": [
            ("есть html",        r"<!DOCTYPE|<html"),
            ("three.js",         r"three"),
            ("сцена",            r"\bScene\b"),
            ("вращение камеры",  r"OrbitControls|mousemove|pointermove"),
            ("цикл анимации",    r"requestAnimationFrame|setAnimationLoop"),
            ("хомяки",           r"hamster"),
            ("клетка",           r"cage|bars"),
            ("предмет",          r"wheel|tunnel|bowl|toy"),
        ],
    },

    "хомяки-физика": {
        "файл": os.path.join(_P, "hamster2_prompt.txt"),
        "название": "Хомяки-физика",
        "описание": "Колесо крутит бегун, труба полая с входом через торец, у предметов есть тела",
        "порог": 15,
        "проверки": [
            ('есть html', '<!DOCTYPE|<html'),
            ('three.js r128', 'three\\.min\\.js|three@0\\.1|r128'),
            ('OrbitControls', 'OrbitControls'),
            ('цикл анимации', 'requestAnimationFrame|setAnimationLoop'),
            ('дельта времени', 'getDelta|deltaTime'),
            ('омега из скорости', '\\w*(углов|омега|omega|angular|spin)\\w*\\s*=\\s*[^;\\n]{0,90}/\\s*\\w*\\.?R\\b'),
            ('колесо вращается', '(spin|wheel|колес)\\w*\\.rotation\\.[xz]\\s*[-+]?='),
            ('затухание колеса', 'трение|friction|затух|нужнаяУгловая|targetSpeed'),
            ('бег по нижней точке', 'низ|bottom|y\\s*-\\s*\\w*\\.?R\\b'),
            ('труба полая', 'CylinderGeometry\\([^)]*true\\s*\\)|openEnded|DoubleSide'),
            ('вход через торец', 'торец|endA|endB|входТрубы|tunnelExit|entrance'),
            ('движение по оси трубы', '(TUBE|tube|tunnel|труб)\\w*\\.(z|x)\\s*-\\s*\\w+\\.(z|x)|ignoreObstacles|сквозьТела'),
            ('тела препятствий', '(ТЕЛА|obstacle|препятств|collider|bodies)\\w*\\s*=\\s*\\['),
            ('выталкивание', 'вытолкн|resolveObstacle|pushOut|separate'),
            ('расталкивание зверей', 'расталкивание|separateHamsters|minD|мин\\s*=\\s*1'),
            ('фаза шага от пути', '(фаза|phase)\\s*\\+=\\s*[^;]{0,60}(шаг|step|dist|ДЛИНА_ШАГА|STEP)'),
            ('диагональные пары', 'лапы\\[0\\]|paws\\[0\\]|\\[\\s*\\[\\s*0\\s*,'),
            ('панель состояний', '(status|состоян|панель)[\\s\\S]{0,300}(innerHTML|textContent)'),
            ('тени', 'shadowMap|castShadow'),
            ('хомяк из частей', '(голова|head)[\\s\\S]{0,200}(ухо|ear|глаз|eye)'),
        ],
    },

    "аквариум": {
        "файл": os.path.join(_P, "aqua_prompt.txt"),
        "название": "Аквариум",
        "описание": "15 рыбок с ИИ, кормление по клику, пузыри, водоросли, стекло",
        "порог": 15,
        "проверки": [
            ("есть html",           r"<!DOCTYPE|<html"),
            ("three.js r128",       r"three\.min\.js|three@0\.1|r128"),
            ("OrbitControls",       r"OrbitControls"),
            # Число рыбок — либо именованная константа, либо цикл до 15.
            ("15 рыбок",            r"(?:FISH[_A-Z]*|fish\w*)\s*=\s*15\b|<\s*15\s*[;)]|createFish\w*\([^)]*\b15\b"),
            # Имя набора палитр в любом написании: COLOR_SCHEMES, colorSchemes, colourSchemes.
            ("8 цветовых схем",     r"colou?r[_\s]*schemes"),
            ("хвост крутится по Z", r"tail[\s\S]{0,120}rotation\.z"),
            ("глаза со зрачками",   r"pupil|зрач"),
            ("плавники",            r"[Ff]in\b|leftFin|rightFin|dorsal"),
            ("избегание рыбок",     r"avoidance|avoid\w*Radius|separation"),
            # Отражение чаще пишут через смену знака скорости у границы, а не словом.
            ("отражение от стен",   r"velocity\.[xyz]\s*=\s*-?\s*Math\.abs|BOUND|bounds|boundary|reflect"),
            ("корм по клику",       r"Raycaster"),
            ("гравитация корма",    r"food[\s\S]{0,200}(gravity|velocity\.y|vy\s*-=)"),
            ("рост после еды",      r"1\.05|scale[\s\S]{0,60}\*=\s*1\.0"),
            ("30 пузырей",          r"(?:BUBBLE[_A-Z]*|bubble\w*)\s*=\s*30\b|<\s*30\s*[;)]|createBubbles?\([^)]*\b30\b"),
            ("пузыри физические",   r"MeshPhysicalMaterial"),
            ("камни-додекаэдры",    r"Dodecahedron"),
            ("водоросли трубками",  r"TubeGeometry"),
            ("кривая водорослей",   r"CatmullRomCurve3"),
            ("стекло с преломлением", r"transmission"),
            ("туман FogExp2",       r"FogExp2"),
            ("теневая карта 2048",  r"mapSize[\s\S]{0,60}2048|shadow[\s\S]{0,80}2048"),
            ("мягкие тени",         r"PCFSoftShadowMap"),
            ("две точечные лампы",  r"PointLight[\s\S]{0,3000}PointLight"),
            ("счётчик FPS",         r"\bfps\b"),
            ("кнопки управления",   r"<button"),
        ],
    },

    "майнкрафт": {
        "файл": os.path.join(_P, "mc_prompt.txt"),
        "название": "Майнкрафт",
        "описание": "Воксельный мир с чанками, шумом, разрушением блоков и коллизиями",
        "порог": 18,
        "проверки": [
            ("есть html",            r"<!DOCTYPE|<html"),
            ("three.js r128 тегом",  r"<script[^>]*three\.min\.js"),
            ("чанки в Map",          r"new Map\("),
            ("массив блоков",        r"Uint8Array"),
            # Размер чанка — как именованная константа или как деление/остаток по 16.
            ("чанк 16",              r"CHUNK[_A-Z]*\s*=\s*16\b|[%&]\s*16\b|/\s*16\b|>>\s*4\b"),
            ("высота 80",            r"(HEIGHT|CHUNK_H|WORLD_H|MAX_Y)[_A-Z]*\s*=\s*80\b|\*\s*80\b|<\s*80\s*[;)]"),
            ("чтение блока",         r"(function\s+|const\s+|let\s+)get\w*Block"),
            ("запись блока",         r"(function\s+|const\s+|let\s+)set\w*Block"),
            ("одна геометрия чанка", r"BufferGeometry"),
            ("вершинные цвета",      r"vertexColors"),
            ("общий материал",       r"MeshLambertMaterial"),
            ("грани по соседям",     r"positions\.push|verts\.push|pos\.push"),
            ("свой хеш-шум",         r"(function\s+|const\s+)\w*(hash|noise)"),
            ("фрактальный шум",      r"octave|fractal|fbm"),
            ("пещеры 3D шумом",      r"0\.09|cave"),
            ("деревья",              r"\btree\b|0\.02"),
            ("захват мыши",          r"requestPointerLock"),
            ("порядок YXZ",          r"YXZ"),
            ("гравитация 25",        r"(GRAVITY|gravity)\s*=\s*25\b|25\s*\*\s*d"),
            ("прыжок 8.5",           r"8\.5"),
            ("коллизии по осям",     r"collid|collision|revert|overlap|resolveAxis"),
            ("луч на 6",             r"\.far\s*=\s*6\b|far\s*:\s*6\b|Raycaster[\s\S]{0,400}\b6\b"),
            # Смещение по нормали — суть механики установки и разрушения.
            ("смещение по нормали",  r"normal[\s\S]{0,80}0\.5|multiplyScalar\(\s*0\.5|n\.\w\s*\*\s*0\.5"),
            ("хотбар",               r"hotbar"),
            ("контекстное меню",     r"contextmenu"),
            ("облака",               r"cloud"),
            ("вода на 14.3",         r"14\.3"),
            ("оверлей старта",       r"overlay|Click to play"),
            ("удаление дальних чанков", r"dispose\(\)"),
        ],
    },
}
