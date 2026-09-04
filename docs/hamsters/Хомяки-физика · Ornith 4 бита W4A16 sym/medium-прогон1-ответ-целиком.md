This is a complex task requiring me to build a single-page Three.js application with hamsters in a cage with "honest physics." Let me carefully analyze the requirements and build this step by step.

Let me break down what I need to do:

**PART 1 - PHYSICS (the most important):**

1.1 WHEEL: 
- Horizontal axis wheel
- Hamster runs on INNER surface of rim at BOTTOM point
- Angular velocity ω = v/R where v is linear speed of feet, R is rim radius
- Empty wheel decays due to friction
- Show panel: foot speed, linear rim speed (|ω|·R), discrepancy %

1.2 HAMSTER SIZE & WHEEL SIZE:
- Wheel radius computed FROM hamster size
- Constants ДЛИНА_ЗВЕРЯ (body length) and ВЫСОТА_ЗВЕРЯ (body height)
- R computed from these

1.3 TUBE IS HOLLOW:
- Open cylinder lying on bedding
- Hamster enters ONLY through end (torus/cap)
- Side wall is solid
- Inside tube, hamster stands on inner bottom, not floating in center

1.4 OBJECTS HAVE BODIES:
- Collision shapes (circle or rectangle)
- Walking hamster doesn't pass through them
- Push out along shortest normal
- Hamsters don't stand in each other

1.5 FEET DON'T SLIDE:
- Step phase from DISTANCE traveled, not clock: phase += (distance / stepLength) · 2π
- When stop, feet freeze; when accelerate, frequency increases
- Diagonal pairs like real animal
- Same in wheel

1.6 TRANSITIONS WITHOUT TELEPORTS:
- Hamster enters smoothly into wheel
- One item - one user: while someone runs, second goes elsewhere

**PART 2 - BEHAVIOR:**
- 5 hamsters with names and different fur colors
- State machine: idle → go to target → activity → idle
- Activities: wheel, tube, bowl, walk
- Panel showing current activity
- Click on hamster - jump
- Resting hamster breathes (volume change), occasionally twitches ear
- Bowl: tilts head and chews

**PART 3 - SCENE:**
- Cage on table, room around
- Tray, bedding with wood shavings (InstancedMesh)
- Frequent bars around perimeter, frames on top
- Wheel, hollow tube, bowl with grains, water bottle
- Hamster built from parts: body, belly, head group, eyes with pupils, cheeks, nose, ears with inner part, four legs, tail
- Hamsters must be distinguishable

**PART 4 - TECHNICAL:**
- Three.js r128 + OrbitControls via specific CDNs
- Single self-contained HTML file
- Shadows PCFSoftShadowMap, 2048 map, directional + soft ambient light
- requestAnimationFrame with delta time, cap delta
- Handle window resize

**PART 5 - VERIFICATION:**
Numbers readable externally: keep hamsters in array, wheel and tube params in objects with clear fields.

Let me now write the code. This is going to be a large single HTML file.

Let me think about the architecture:

```javascript
// Constants
const ДЛИНА_ЗВЕРЯ = 0.4; // body length
const ВЫСОТА_ЗВЕРЯ = 0.25; // body height
const РАДИУС_КОЛЕСА = ...; // computed from hamster size

// Wheel object
const wheel = {
  radius: R,
  angularVelocity: 0, // omega
  // ...
};

// Tube object
const tube = {
  length: ...,
  radius: ...,
  axis: ...,
  // ...
};

// Hamsters array
const hamsters = [...];
```

Let me design the physics carefully.

**Wheel physics:**
When a hamster runs in the wheel, its feet move at linear velocity v along the inner rim surface. The angular velocity of the wheel is ω = v/R. 

The hamster is at the bottom of the wheel. Its feet touch the rim at the bottom. As the hamster runs forward (let's say forward means the rim moves backward under its feet), the wheel rotates.

Let me set up coordinates:
- Wheel axis is horizontal (say along Z axis for the wheel's rotation plane being X-Y... wait let me think)

Actually let me make the wheel rotate in a vertical plane. So the wheel is like a hamster wheel - a disc in the vertical plane (X-Y plane), rotating around the Z axis (horizontal).

Wait, but the hamster runs inside it. Let me reconsider. A hamster wheel typically has:
- Rotation axis horizontal
- The wheel spins in a vertical plane
- Hamster runs on the inner bottom surface

So the wheel plane is vertical (say the X-Y plane where Y is up), and it rotates around the Z axis.

The hamster sits at the bottom of the wheel at position (centerX, centerY - R, centerZ). Its feet touch the rim at the bottom.

When the hamster runs forward (in +X direction relative to wheel, i.e., toward the front), its feet push the rim backward, so the wheel rotates such that the bottom moves backward (-X direction). For a wheel rotating around Z axis, if the bottom moves in -X, then... let's see. Rotation around Z: a point at angle θ. Bottom is at θ = -90° (pointing down, -Y). 

For rotation, angular velocity ω (positive = counterclockwise in XY plane). The velocity of a point at position r is v = ω × r. For rotation around Z with angular velocity ω (scalar, positive CCW), a point at (x, y) has velocity (-ω·y, ω·x).

At the bottom point (0, -R): velocity = (-ω·(-R), ω·0) = (ω·R, 0). So the bottom point moves in +X if ω > 0.

But we want the bottom to move BACKWARD relative to the hamster's running direction. If the hamster runs in +X (forward), its feet would tend to push the rim backward (-X), meaning the rim bottom moves in -X, so ω < 0.

Hmm, let me just define it consistently. Let's say:
- Hamster runs in +X direction (forward)
- Feet velocity at contact = v in +X (the feet move forward with the hamster)

Wait, actually the feet are in contact with the rim. If there's no sliding, the foot at the contact point has zero velocity relative to the rim (like rolling without slipping). But the hamster's body moves forward at speed v, and the rim surface at the contact... 

Actually for a hamster wheel: the hamster's feet grip the rim. The hamster's body moves forward at speed v. At the contact point, the rim surface must move at the same velocity as the foot (no slip). The foot is attached to the hamster body which moves at +v in X. So the rim surface at the bottom moves at +v in X? No wait.

Let me reconsider. In a hamster wheel, when the hamster runs forward (+X), the wheel rotates. Think about it: the hamster runs forward, its feet push back on the rim, the rim's bottom goes backward relative to the hamster, but the hamster stays roughly in place horizontally (it's at the bottom).

Hmm, actually the classic result: the hamster's body stays at the bottom (roughly stationary horizontally), and the wheel rotates. The bottom of the wheel moves in the same direction as... let me think physically. 

If you're in a hamster wheel and run "forward" (toward the front of the cage), your feet push the rim backward, so the bottom of the wheel moves backward (toward the rear). Your body tends to stay at the bottom because gravity keeps you there.

So: hamster body velocity ≈ 0 (stays at bottom), rim bottom velocity is backward (-X if forward is +X)... 

No wait. Let me think again very carefully with a real example. Imagine the hamster wheel. The hamster faces right (+X). It runs to the right. Its right feet push against the rim. Because of friction, the rim at the bottom is dragged to the right along with the feet IF no slip... 

Ugh, I'm confusing myself. Let me think about the "no slip" condition properly.

Rolling without slipping: the contact point has zero velocity relative to the ground. For a hamster wheel, the "ground" is effectively the hamster's feet grip.

OK here's the clean way to think: The hamster's feet are like the contact patch. The hamster wants to move its body forward at speed v. For the hamster to move forward relative to the wheel's center... 

Actually, in a hamster wheel, the hamster does NOT move forward around the wheel (it stays at the bottom). Instead, the wheel spins. The relationship: the hamster's feet, relative to the hamster body, are stationary (body moves at v_body). The feet grip the rim. 

Let me use the constraint that the hamster stays at the bottom (its horizontal position is fixed at the wheel's bottom). Then the rim surface at the bottom moves with velocity equal to the hamster's feet velocity. The hamster's feet move with the hamster's body at v_body (forward). Wait, but if the hamster stays at the bottom and the bottom of the wheel moves at v = ωR, and the hamster's feet are at the bottom...

I think the key insight the problem wants: ω = v/R where v is the "foot speed" (speed of the feet). And the linear speed of the rim at the contact = |ω|·R = v. So they match. That's the "honest physics" check.

Let me just implement it as: 
- Hamster has a running speed v (linear speed of its feet/body along the running direction).
- Wheel angular velocity ω = v/R (with appropriate sign).
- Rim linear speed at contact = |ω|·R = v. ✓ These match.

The sign: if the hamster runs forward (+X), the wheel should rotate so the bottom goes backward. Let me determine: we want the rim surface velocity at the bottom to be... 

For no slipping between foot and rim: the foot velocity (which equals body velocity = v_forward) should equal the rim surface velocity at the bottom. 

Hmm, but that would mean rim bottom moves forward too. Let me reconsider whether the hamster moves forward or stays put.

Actually, you know what, in a real hamster wheel, the hamster's body DOES stay approximately at the bottom and doesn't travel around. The wheel spins beneath it. Let me reconsider the no-slip.

Consider the hamster standing on the rim at the bottom. The hamster's feet push backward on the rim to propel itself, but since it can't go forward (it's constrained at the bottom by gravity and the curved rim), the energy goes into spinning the wheel.

The no-slip condition: velocity of rim point at contact = velocity of hamster's foot. The hamster's foot is at the bottom. If the hamster body is stationary (not moving around the wheel), then... the foot is also stationary? That can't drive the wheel.

I think the resolution is: the hamster's body is NOT stationary. Let me reconsider. Actually in a hamster wheel, as the hamster runs, its body oscillates but on average stays near the bottom. The wheel spins continuously.

Let me look at this from the physics of the problem statement rather than trying to derive real hamster physics:

"Угловая скорость колеса вычисляется из скорости бега: ω = v / R, где v — линейная скорость лап хомяка"

So ω = v/R, v = linear speed of feet. Simple. The wheel spins at ω = v/R.

"Обод под лапами уходит НАЗАД относительно направления, куда смотрит зверь."

The rim under the feet moves BACKWARD relative to the direction the animal looks. So if the animal faces +X, the rim at the bottom moves in -X. This is the "rim goes backward" observation (like a treadmill - the belt goes backward under your feet while you stay put).

So the foot is like on a treadmill: feet stay roughly in place (horizontally), the surface (rim) moves backward under them. The feet "walk/run" pushing backward, rim moves backward.

So the rim bottom velocity = -v (backward), and the hamster's feet relative to the hamster body move backward then forward (running motion) but on average stay in place.

The angular velocity: rim bottom moves in -X. Using v_point = ω × r, at bottom (0,-R) relative to center: v = (ω·R, 0) for rotation around Z (as computed before, v = (-ω_y... let me recompute).

Rotation around Z-axis, angular velocity vector ω_vec = (0,0,ω). Point at position r = (0, -R, 0) relative to center. v = ω_vec × r = (0,0,ω) × (0,-R,0) = 
i: (0·0 - ω·(-R)) = ωR
j: (ω·0 - 0·0) = 0
k: (0·(-R) - 0·0) = 0
So v = (ωR, 0, 0). 

For rim bottom to move in -X: ωR < 0, so ω < 0.

OK so if hamster faces +X and runs forward, ω < 0 (clockwise when viewed from +Z... depends on orientation). Fine, I'll just handle signs carefully in code, or I can make the hamster face -X. Let me not overthink and just make it consistent: the wheel rotates such that the bottom moves opposite to the hamster's facing/running direction.

Actually, simplest: Let the hamster run in a direction, compute the wheel rotation accordingly. Since the hamster stays at the bottom, "running direction" is a bit ambiguous. Let me define: the hamster faces a direction on the ground, and "runs forward" means it would move that way if on ground. In the wheel, the rim at the bottom moves opposite. 

Let me simplify: I'll have the hamster in the wheel always at the bottom, facing some direction (let's say it faces +X consistently, or I'll give it a heading). The wheel rotates about the Z axis. The angular velocity magnitude = v/R. Sign chosen so the bottom rim moves opposite to the facing direction.

If hamster faces +X (heading angle 0), rim bottom should move -X, so ω = -v/R (from above, ω<0 gives -X at bottom). 

Hmm wait let me double check: ω<0, v_bottom = (ωR, 0) = negative x. Yes, -X. Good. So ω = -v/R when facing +X.

Alternatively if facing -X (heading π), then "forward" is -X, rim bottom should move +X, so ω > 0, ω = +v/R. So ω = -(v/R)·cos(heading)? Let me see: facing +X (heading 0), cos=1, ω=-v/R. Facing -X (heading π), cos=-1, ω=+v/R. Yes! ω = -(v/R)·cos(heading). Hmm, but that's only the z-component. Actually since the wheel axis is Z and hamster runs in the XY plane... 

Actually, let me simplify even more. Let me just have the hamster in the wheel face a fixed direction and run. I'll set heading = 0 (facing +X) for the wheel hamster. Then ω = -v/R. Or I could make the wheel axis along a different direction.

Hold on. Let me reconsider the wheel orientation. If the wheel rotates around the Z axis (horizontal), the wheel is in the XY plane (vertical). The hamster is at the bottom. The hamster faces... in the XY plane, tangent to the circle at the bottom, which is the X direction. So the hamster faces +X or -X. Good, consistent with above.

Let me make the hamster face +X and set ω = -v/R. Then rim bottom moves -X (backward relative to facing +X). ✓

Now the hamster's rotation: the wheel spins, so I apply rotation to the wheel mesh. The hamster itself doesn't rotate with the wheel (it stays upright at the bottom), but its legs animate based on the running.

Leg animation in wheel: phase advances based on distance traveled. Distance = v · dt. phase += (distance / stepLength) · 2π. Same as walking.

**Friction on empty wheel:**
When no hamster is running, ω decays: dω/dt = -k·ω (linear damping) or -k·ω·|ω| (air resistance). Let me use linear damping: ω *= exp(-k·dt) or ω -= k·ω·dt. This makes ω decay toward zero. ✓ (check #2)

**Tube physics:**
- Hollow cylinder lying on bedding. Axis horizontal, parallel to ground, at some height (resting on bedding so the bottom of the cylinder touches the bedding).
- Inner radius r_inner. Hamster inside stands on inner bottom.
- Hamster enters through an end (torus/cap opening). Moves along the axis inside.
- Side wall solid: hamster can't pass through the cylindrical wall.
- Inside, hamster on inner bottom: its position = axis point (along axis) with y = center_height - r_inner + hamster_radius (standing on bottom).

Collision for tube: 
- Along the axis: hamster constrained within [axis_start, axis_end] (can only enter/exit through ends). Actually the hamster CAN exit through either end, so it's not fully constrained, but it can't go through the walls.
- Radially: hamster can't penetrate the cylinder wall. Min distance from axis >= r_inner - hamster_clearance... but also the hamster is inside so it should stay within r_inner.
- Vertically: hamster stands on inner bottom, so y >= center_height - r_inner + hamster_radius.

Hmm, this is getting complex. Let me simplify the tube interaction:
- The hamster, when "in tube," moves along the axis (1D motion), standing on the inner bottom. Its radial position is fixed at the bottom of the cylinder.
- To enter: hamster walks to the near end, then moves along the axis into the tube, reaching the inner bottom position.
- To exit: moves to the other end and comes out.

For collision when walking (not in tube), the tube acts as a solid obstacle: the hamster can't pass through the cylindrical wall, and can't go past the ends into the tube interior unless it's the "in-tube" state.

Let me model the tube collision as: 
- Cylinder (outer radius R_tube). Hamster (radius r_h). 
- If hamster is outside the cylinder and within the tube's axial extent, push it out radially (min distance from axis = R_tube + r_h... but there's bedding and the tube rests on it).
- The ends are open, so if the hamster is beyond the axial extent, no radial constraint.

Actually, let me make the tube rest on the bedding such that the bottom is buried a bit, and the hamster enters at ground level. Hmm.

Let me reconsider. Maybe simpler: The tube is a horizontal cylinder. Its axis is at height h_axis above the floor. The hamster, when in the tube, is at the bottom of the inside, at height h_axis - R_inner + r_h (standing). The hamster enters through the end at the bottom-ish.

For the walking collision, I'll treat the tube as a solid cylinder obstacle. The hamster (a circle of radius r_h in top-down view) can't overlap the outer cylinder (radius R_outer). So min distance from tube axis (projected to ground) must be >= R_outer + r_h, EXCEPT within the end openings.

This is getting complicated. Let me simplify the whole thing:

For the purposes of this simulation, I'll implement:
1. Wheel: full physics as described.
2. Tube: the hamster, when assigned to the tube, travels along the axis from one end to the other, positioned on the inner bottom. Collision: while walking on the ground, the hamster is pushed away from the tube's outer surface (radially) if it gets too close, but can approach the ends.
3. Bowl: circular collision, hamster pushed out.
4. Hamster-hamster: circular collision, pushed apart.

Let me now think about the actual implementation structure.

Given the complexity, I'll write a fairly large but organized HTML file. Let me structure:

1. HTML with two panels (physics readout + activity status) and a canvas container.
2. CSS for panels.
3. JS:
   - Setup scene, camera, renderer, lights, controls.
   - Build room (floor, walls, table).
   - Build cage (tray, bedding, bars, frame).
   - Build objects (wheel, tube, bowl, water bottle).
   - Build hamster factory.
   - Physics/state machine update loop.
   - Interaction (click to jump, raycasting).
   - UI updates.

Let me write it.

Actually, given the enormous scope, let me focus on making it WORK correctly for the physics checks, and make it visually reasonable. I'll write comprehensive code.

Let me start coding.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D клетка с хомяками — честная физика</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #1a1a1a; font-family: monospace; }
  #app { position: relative; width: 100vw; height: 100vh; }
  canvas { display: block; }
  .panel {
    position: absolute; top: 12px; left: 12px;
    background: rgba(20,20,30,0.82); color: #d8f0d8;
    padding: 10px 14px; border-radius: 10px;
    font-size: 13px; line-height: 1.5; min-width: 250px;
    border: 1px solid rgba(120,255,120,0.25);
    pointer-events: none;
  }
  .panel h3 { font-size: 14px; margin-bottom: 6px; color: #90ff90; }
  .row { display: flex; justify-content: space-between; gap: 18px; }
  .ok { color: #90ff90; }
  .bad { color: #ff8080; }
  #status { left: auto; right: 12px; text-align: right; min-width: 230px; }
  .ham-name { color: #ffd27f; }
</style>
</head>
<body>
<div id="app">
  <div class="panel" id="physics">
    <h3>Физика колеса</h3>
    <div class="row"><span>Скорость лап v:</span><span id="p_v">—</span></div>
    <div class="row"><span>|ω|·R (обод):</span><span id="p_w">—</span></div>
    <div class="row"><span>Расхождение:</span><span id="p_d">—</span></div>
    <div class="row"><span>ω (угл. скор.):</span><span id="p_omega">—</span></div>
  </div>
  <div class="panel" id="status">
    <h3>Занятость</h3>
    <div id="statusList"></div>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ... all the code
</script>
</body>
</html>
```

Now the JavaScript. Let me write it carefully.

Constants:
```javascript
// --- Размеры зверя (отсюда считаем размер колеса) ---
const ДЛИНА_ЗВЕРЯ = 0.42;   // длина тела лежачего зверя (нос–хвост)
const ВЫСОТА_ЗВЕРЯ = 0.26;  // высота в стойке
const ШИРИНА_ЗВЕРЯ = 0.26;  // ширина тела
const РАДИУС_ЗВЕРЯ = ВЫСОТА_ЗВЕРЯ * 0.5; // радиус "тела" для коллизий ~0.13

// --- Размер колеса вычисляем от размера зверя ---
// Зверь должен целиком помещаться внутри с запасом,
// расстояние между ободами шире его боков.
const ЗАПАС_КОЛЕСА = 1.35;           // запас по высоте (зверь + место для ног)
const РАДИУС_КОЛЕСА = ДЛИНА_ЗВЕРЯ * 0.5 * ЗАПАС_КОЛЕСА; // ~0.28
```

Hmm, let me think about the wheel radius. The hamster needs to fit inside with room for its legs to run. The hamster's body height is ~0.26. The hamster sits at the bottom, its body extends upward. The wheel radius must be bigger than the hamster's body height plus leg room. 

Let me set РАДИУС_КОЛЕСА such that the hamster fits. If hamster body height is 0.26 and it sits at the bottom, the top of the hamster is at height (centerY - R + 0.26) from center... for the hamster to fit, R must be > 0.26 + clearance. Let me make R = 0.35 or so.

Actually, let me define:
```javascript
const РАДИУС_КОЛЕСА = (ВЫСОТА_ЗВЕРЯ + ДЛИНА_ЗВЕРЯ * 0.4) * 1.1;
```
Eh, let me just pick reasonable numbers derived from hamster size. Let me say the hamster's bounding sphere radius is about 0.18 (half of max dimension). Wheel radius should be at least ~2x that for comfort: R ≈ 0.4.

Let me use:
```javascript
const РАДИУС_КОЛЕСА = ДЛИНА_ЗВЕРЯ * 0.9; // ~0.38
```

Check #3: "гомяк в колесе стоит на нижней точке обода, а его габарит меньше радиуса колеса (обод не пересекает тело)". So the hamster's extent must be less than R. Hamster body height 0.26 < 0.38. Good. And the rim shouldn't intersect the body: the hamster sits at bottom, body extends up to (centerY - R + 0.26). The rim at the sides is at radius R from center. The hamster body, modeled as a shape of height 0.26 sitting on the rim bottom... the nearest rim points are at the bottom. As long as R > hamster height + leg clearance, fine.

Let me make the hamster's feet reach up from the rim bottom. The hamster stands on the rim at the bottom. Its feet are at radius R (touching rim). Its body extends up. Legs have length ~0.1. So the hamster's body center is at radius R + legLength + bodyHeight/2. The wheel radius R should accommodate: from center of wheel to top of hamster = R - legLength... 

This is getting complicated. Let me just position the hamster's contact point (feet) at the bottom of the wheel (angle -90°, i.e., directly below center), and place the hamster body above that. The hamster's overall height (feet to top of head) should be < R so it fits. With R = 0.38 and hamster height ~0.35 (including legs stretched?), might be tight. Let me increase R.

Let me reconsider dimensions for the scene scale. The cage might be ~3m x 2m. Hamsters ~0.4m. Wheel radius ~0.4m. That seems reasonable (wheel diameter 0.8m, about 2x hamster length).

Let me set:
- ДЛИНА_ЗВЕРЯ = 0.4
- ВЫСОТА_ЗВЕРЯ = 0.28
- РАДИУС_КОЛЕСА = 0.42 (diameter 0.84)

Hamster fits: at bottom, top of hamster reaches up to R - small gap. Body height 0.28 + legs 0.12 = 0.4 < 0.42. OK tight but ok. Let me make R = 0.46 to be safe.

Actually, let me define R clearly derived:
```javascript
const РАДИУС_КОЛЕСА = (ВЫСОТА_ЗВЕРЯ + ДЛИНА_ЗВЕРЯ) * 0.6; // (0.28+0.4)*0.6 = 0.408
```
Let me just use a constant that's clearly > hamster size with a comment.

Now let me think about how the hamster is placed in the wheel and how it animates.

**Hamster in wheel placement:**
- Wheel center at world position (wx, wy, wz). Wheel rotates around Z axis (so wheel plane is XY, vertical).
- Wait, I need to decide wheel orientation. Let me make the wheel's rotation axis horizontal and parallel to the cage's longer or shorter dimension. Let me say the wheel axis is along Z (into the screen / along cage depth). Wheel spins in XY vertical plane.
- Hamster at bottom: position = (wx, wy - R, wz). Facing +X (or -X). Let's say facing +X.
- The hamster mesh: I'll position it and its legs animate.

**Wheel rotation:**
- The wheel mesh rotates around Z by angle θ where dθ/dt = ω.
- ω = -v/R (for hamster facing +X). Sign so rim bottom moves -X.

Wait, I realize I should double-check the "rim goes backward" with the hamster running forward. If the hamster faces +X and runs "forward" (+X), then relative to the hamster, the rim moves backward (-X). With ω = -v/R (negative), rim bottom velocity = (ωR, 0) = (-v, 0) = -X. ✓. Good.

But actually, does the hamster move forward around the wheel or stay at the bottom? It stays at the bottom (that's how hamster wheels work - the hamster stays roughly at the bottom and the wheel spins). So the hamster's world position stays at (wx, wy-R, wz) while the wheel spins and its legs run.

**Leg animation:**
The hamster's legs move in a running pattern. Phase advances with distance: phase += (v·dt)/stepLength · 2π. Four legs in diagonal pairs: front-left + back-right share phase φ, front-right + back-left share phase φ + π. Each leg does a pedaling motion (like cycling) since the hamster is in a wheel. Actually in a wheel the legs move somewhat like running on a treadmill. Let me animate legs with a sinusoidal lift based on phase.

For a running/galloping hamster, legs alternate. Let me do: each leg's lift (how high the foot is) = amplitude * max(sin(phase + offset), 0) roughly, with offsets for diagonal pairs.

Let me define leg phase offsets:
- Back-left (BL): phase
- Front-right (FR): phase + π (diagonal)
- Front-left (FL): phase + π/2... 

Hmm, diagonal pairs run together in many quadrupeds (trotting): BL-FR and FL-BR. So BL and FR move together, FL and BR move together, and the two pairs are π apart.

For pedaling in a wheel, maybe simpler: legs cycle. Let me just do trotting: 
- BL and FR: lift = base + amp·sin(phase)
- FL and BR: lift = base + amp·sin(phase + π) = base - amp·sin(phase)

Each leg pivots at its shoulder/hip, swinging forward/back and up/down. Let me animate the leg rotation (swing) using sin/cos of phase.

Let me keep leg animation simple but visible: each leg rotates about its joint so the foot moves in an arc. I'll set the leg's rotation based on phase.

**State machine:**
States: 'idle', 'going', 'activity'. Activities: 'wheel', 'tube', 'bowl', 'walk'.

Transitions:
- idle → choose a goal (based on probability/time), transition to 'going' with target position.
- 'going' → move toward target. On arrival, if goal is wheel and wheel is free, enter wheel ('activity: wheel'). If wheel busy, pick another goal. Etc.
- 'activity' → perform activity for some duration, then return to idle.
- 'walk' → just wander to a random point, then idle.

Goal assignment with occupancy:
- Wheel: one occupant at a time. If occupied, skip.
- Tube: maybe one at a time too (or allow a couple). Let me make tube one-at-a-time for simplicity.
- Bowl: can have multiple? Let me allow one at a time near the bowl to avoid crowding, or allow a couple. Let me make bowl single too for simplicity, or allow up to 2.
- Walk: always available.

Occupancy tracking: each object has an `occupant` reference (null or hamster index).

**Entering the wheel smoothly:**
When a hamster is assigned to the wheel and it's free:
1. Hamster walks to a point near the wheel (at the bottom edge, on the ground).
2. Then smoothly moves from ground up/into the wheel bottom position (interpolate).
3. Once at wheel bottom, starts running.

Exit: reverse.

**Tube entry:**
1. Hamster walks to the near end of the tube (aligned with the axis, at ground level near the opening).
2. Moves into the tube along the axis, descending to the inner bottom.
3. Travels along the axis to the far end.
4. Exits at the far end, rises to ground level.

**Bowl:**
1. Hamster walks to the bowl.
2. Stands at the bowl, tilts head, chews.
3. After some time, leaves.

**Collision handling:**
For walking hamsters, apply collision resolution:
- Against wheel (as a vertical cylinder/solid): treat wheel's support + the wheel rim. Simplify: treat the wheel's center post / support base as a circle obstacle, and the wheel rim as... hmm. Actually the wheel is a big ring. A walking hamster shouldn't walk through the wheel. Let me treat the wheel as a solid disk/cylinder obstacle (the whole wheel area). But the hamster CAN be at the bottom running in it. 

This is tricky because the wheel hamster is "inside" the wheel but that's allowed. Let me separate: the wheel rim is a torus. A walking hamster collides with the outer surface of the rim. The wheel hamster is special-cased (it's the occupant).

Let me simplify collisions:
- Wheel: obstacle = circle of radius R_wheel_outer centered at wheel center, projected to ground. Walking hamsters pushed out if inside, UNLESS the hamster is the wheel occupant.
  - But also the wheel is elevated (on a stand), so the rim is above the ground. A walking hamster at ground level wouldn't hit the rim anyway if the rim is high enough. Let me elevate the wheel so its bottom rim is near the bedding but the hamster on the ground is below the rim's lowest point... 
  
Hmm, this is getting complicated. Let me reconsider the geometry.

Hamster wheel: typically mounted so the bottom of the wheel is slightly above the bedding (a few cm), and the hamster climbs in. Or the wheel bottom is at bedding level.

For simplicity: the wheel's bottom rim is at ground/bedding level. The hamster climbs in from the side (walks to the bottom of the wheel, then up into it). The stand holds the wheel.

Collisions for walking hamsters with the wheel: I'll treat the wheel as a vertical circle obstacle (radius R) at the wheel center, but only block the portion above ground. Since walking hamsters are at ground level and the wheel is a ring at ground level, the walking hamster would collide with the rim at the bottom. 

To keep it manageable, let me treat the wheel collision as: the hamster (top-down circle) must stay outside a circle of radius (R - smallGap) centered at wheel center. This prevents walking through the wheel. The wheel occupant is exempt.

Actually, wait. If the wheel is a ring lying vertically with its bottom at ground level, then top-down the wheel is a ring (torus) — an outer circle radius R and inner circle radius R - barThickness. The hamster running in it is in the middle (near center, at the bottom). A walking hamster approaching would hit the outer edge of the ring (radius R). So obstacle radius ≈ R for walking hamsters. The occupant is at the bottom inside, which is fine.

But the occupant is at the bottom (directly below center), so it's within radius R of center. If I push walking hamsters out to radius R, and the occupant is at radius 0 (bottom, directly below center means horizontal distance 0)... wait the occupant is directly below the center, so its horizontal (top-down) distance from center is 0. So the occupant is well within radius R. Good, no conflict. Walking hamsters get pushed to radius >= R. 

Hmm, but actually the occupant at the bottom: its horizontal position is the same as the wheel center (directly below). So top-down it's AT the center. Walking hamsters pushed to radius R won't reach the center. Good.

Let me set wheel collision obstacle radius = R (outer rim). Actually to be safe from visual clipping, maybe R + 0.02.

- Bowl: obstacle = circle radius (bowlRadius + hamsterRadius). Push out.
- Tube: obstacle = cylinder. Top-down, circle radius (tubeOuterRadius + hamsterRadius), BUT with openings at the ends. So within the tube's axial extent, block radius. Beyond the ends (past the tube caps), allow passage. 
  - Implementation: for a point (x,z), compute distance to tube axis line. If within [axisStart, axisEnd] along axis AND radial distance < tubeOuterRadius + hamsterRadius, push out. Else allow.
  - But the tube rests on bedding and the hamster enters at the end at ground level. The tube's inner bottom is where the occupant sits.

Let me define tube:
- Axis: a line segment from P1 to P2, horizontal, at height h_axis.
- Outer radius R_out, inner radius R_in.
- The tube rests on bedding: h_axis = beddingHeight + R_out (so the outer bottom touches bedding). Actually the tube lies ON the bedding, so its lowest point is at bedding level. h_axis = beddingLevel + R_out.
- Inner bottom at h_axis - R_in.
- Occupant inside: sits on inner bottom, at height h_axis - R_in + hamsterRadius, positioned along the axis at parameter t ∈ [0,1].

For the occupant, its position = P1 + t·(P2-P1), with y = h_axis - R_in + hamsterRadius. It moves t from 0 (near end) to 1 (far end) or vice versa.

Entry: hamster approaches the near end (say P1 side), positioned just outside the opening, then moves in.

Collision for walking hamsters with tube (excluding occupant):
- Project hamster to ground (x,z). Compute along-axis coordinate s = dot(P_pos - P1, axisDir) and radial distance d = distance from axis line (in top-down).
- If s < 0 or s > tubeLength (beyond the ends): no radial constraint (can be anywhere).
- If 0 <= s <= tubeLength: if d < R_out + hamsterRadius, push out radially to d = R_out + hamsterRadius. BUT if the hamster is near an end (s within some margin of 0 or tubeLength), allow it to enter/exit. Hmm, actually the hamster should be able to reach the opening. Let me allow it to get to d <= R_out + hamsterRadius (just touch outer surface) but not enter the cylinder interior. The opening is at the ends (s=0 or s=tubeLength) where the hamster can move along the axis.

Wait, but the occupant enters through the end and moves ALONG the axis. So at the ends, the hamster moves in the axis direction. For a walking hamster that's NOT the occupant, it just can't go through the tube wall. It can walk alongside the tube (outside) and reach the opening but not enter (unless it becomes occupant).

Let me implement tube collision as: if within axial extent [0, tubeLength] and radial dist < R_out + hamsterRadius + gap, push out. This blocks passing through the tube. At the very ends, the constraint naturally releases (s<0 or s>tubeLength), allowing the hamster to go around the end. Good.

But there's subtlety: the hamster walking along the tube's length (parallel to axis) outside the tube should be fine. The radial constraint only pushes it away from the axis if it's too close. That works.

Also the tube rests on bedding, so the bottom part of the tube is buried. The hamster walking alongside would collide with the tube wall. Fine.

Let me also consider: the tube is a solid obstacle for the hamster walking. But the hamster might need to walk from one side to the other, going around the ends. That's fine, it'll path around.

OK let me also handle hamster-hamster collision: circle-circle, push apart along the connecting line.

**Now, the big question: how detailed do I make the hamster model and behavior?**

Given the scope, I'll build a decent-looking hamster from primitives (spheres, ellipsoids, cylinders) grouped appropriately. I'll animate legs, head, ears.

Let me plan the hamster construction:

```javascript
function createHamster(color) {
  const group = new THREE.Group();
  const furMat = new THREE.MeshStandardMaterial({ color, roughness: 0.9, flatShading: false });
  const bellyMat = new THREE.MeshStandardMaterial({ color: lighten(color), roughness: 0.9 });
  // Body: ellipsoid
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 16), furMat);
  body.scale.set(0.5*ДЛИНА_ЗВЕРЯ, 0.5*ВЫСОТА_ЗВЕРЯ, 0.5*ШИРИНА_ЗВЕРЯ);
  // Belly: lighter ellipsoid in front/below
  // Head group (for nodding)
  const headGroup = new THREE.Group();
  // ... eyes, ears, cheeks, nose
  // Legs: 4, each a small group with upper+lower
  // Tail
}
```

Let me lay out coordinates for the hamster (local space):
- X: forward (toward nose)
- Y: up
- Z: left (right-hand: X forward, Y up, Z left)

Body center at origin (or slightly back). Nose at +X. Tail at -X.

Let me position:
- Body: ellipsoid centered at (0, bodyY, 0), semi-axes (lenX, lenY, lenZ).
- Head: sphere at (+headX, headY, 0), part of headGroup.
- Front legs: at (+legX, 0, ±legZ).
- Back legs: at (-legX, 0, ±legZ).
- Tail: small sphere/cylinder at (-tailX, 0, 0).

For legs, each leg is a group pivoting at the shoulder. I'll animate rotation about the Z axis (swing forward/back) and maybe a knee.

Let me keep legs simple: each leg = a cylinder (or capsule) that swings. I'll rotate the whole leg about the shoulder joint (Z axis) by an angle derived from phase. The foot traces an arc.

Actually, for a running motion, let me animate each leg with a rotation that makes the foot move. Let me define for each leg a pivot at the body and a rotation angle:
- swing angle = amp · sin(phase + offset)
This rotates the leg forward/back. Combined with a slight bend.

For diagonal pairs, offsets: 
- BL: 0, FR: 0 (same pair)
- FL: π, BR: π

Wait diagonal pairs: BL & FR are one pair, FL & BR are the other. In trotting, BL+FR move together, FL+BR move together, opposite phase. So:
- BL offset 0, FR offset 0
- FL offset π, BR offset π

Hmm but then BL and FR both at phase 0, FL and BR at phase π. When BL is forward, FL is back. Good (trotting gait).

But wait, for a hamster in a wheel pedaling, the motion might be more like all four legs pushing back in a burrowing motion. Let me just use the trotting/running pattern; it'll look like running.

Let me define each leg as having a "front-back swing" driven by sin(phase+offset). The foot goes forward when sin positive.

Actually, I realize the exact leg animation doesn't need to be biologically perfect, just look like running and satisfy "phase from distance, feet freeze when stopped, diagonal pairs." Let me implement:

```javascript
// per leg
const legPhase = phase + offset;
leg.pivot.rotation.z = Math.sin(legPhase) * swingAmp;  // swing in horizontal? 
```

Hmm, rotation about which axis to make the foot move forward/back in the X-Z plane? The leg hangs down from the body. To swing it forward/back (in X-Y plane, i.e., the hamster's forward direction), rotate about Z axis. rotation.z = swingAngle swings the leg in the X-Y plane (forward/back). 

But we also want the foot to lift off the ground (Y component). Let me add rotation about X too? That would swing it side to side. For running, let me combine: the leg swings forward-back (about Z) and lifts up (about X). 

Let me keep it moderate: 
- rotation.z = sin(phase+offset) * ampZ (forward-back swing)
- rotation.x = cos(phase+offset) * ampX (lift)

The foot position then traces an arc. When phase stops advancing, angles are constant → feet frozen. ✓ (check #6)

Good.

**Breathing in rest:** scale the body slightly: body.scale.y = 1 + 0.03·sin(t·2). And volume change — scale all slightly. I'll modulate body scale.

**Ear twitch:** rotate an ear occasionally: ear.rotation based on a random trigger.

**Bowl chewing:** head nods + jaw moves. headGroup.rotation.x oscillates, and a jaw sub-mesh moves.

OK this is a LOT. Let me write it all out. I'll aim for correctness of physics and reasonable visuals.

Let me also make sure to expose values for checking:
```javascript
window.__wheel = wheel; // { radius, angularVelocity, ... }
window.__tube = tube;
window.__hamsters = hamsters;
```

And the physics panel reads from the running wheel hamster.

Let me now think about the update loop and physics math precisely.

**Wheel update:**
```javascript
// wheel = { radius R, omega (angular velocity, rad/s), mesh, occupantIndex }
// When occupant running with foot speed v:
//   targetOmega = -v / R  (sign for rim backward)
//   omega lerps toward targetOmega (so it accelerates smoothly)
// When no occupant:
//   omega *= exp(-friction * dt)  -> decays to 0

// Wheel mesh rotation: theta += omega * dt; mesh.rotation.z = theta;
```

Wait, sign convention. Let me reconsider. The hamster faces +X. Running forward = +X. Rim at bottom should move -X (backward). We found ω_z = -v/R gives rim bottom velocity (-v, 0). Let me verify once more with cross product:
ω_vec = (0,0,ω_z). Contact point relative to center: r = (0, -R, 0). v = ω_vec × r = (ω_y·r_z - ω_z·r_y, ω_z·r_x - ω_x·r_z, ω_x·r_y - ω_y·r_x) = (ω_z·R... let me carefully:

v_x = ω_y·r_z - ω_z·r_y = 0·0 - ω_z·(-R) = ω_z·R
v_y = ω_z·r_x - ω_x·r_z = ω_z·0 - 0·0 = 0
v_z = ω_x·r_y - ω_y·r_x = 0

So v = (ω_z·R, 0, 0). For v_x = -v (backward), ω_z·R = -v → ω_z = -v/R. ✓ Confirmed.

So omega_z = -v/R when hamster faces +X.

But actually, I want the wheel to visibly spin in a way that looks like the hamster is running forward. If the hamster faces +X and the rim bottom goes -X, then looking at the wheel from the side (from +Z or -Z), the bottom moves backward. That's correct treadmill behavior.

Hmm, but which way does the hamster run? Let me have it face +X. The wheel spins so bottom goes -X. From the perspective of someone watching the hamster's side (looking in -X direction, i.e., from the +X side toward -X), we'd see the hamster's... this is getting confusing. Let me just make it consistent and move on.

Actually, let me reconsider: maybe it's more natural for the hamster to face -X so that when we view from the front it runs "into" ... no. Let me not overthink. Hamster faces +X, omega_z = -v/R. Done.

Wait, I want to double check the visual: if omega_z is negative, the wheel rotates clockwise when viewed from +Z looking toward -Z (standard math positive is CCW from +Z). Clockwise viewed from +Z. The bottom of a clockwise-spinning wheel (viewed from +Z) moves in... at the bottom, clockwise means moving to the left (-X) if we view with X right, Y up. Yes -X. ✓ Consistent.

Good.

**Foot speed v for the running hamster:**
The hamster has a target running speed (e.g., 0.5 m/s). Its feet move at v. The phase advances: phase += (v·dt)/stepLength · 2π.

The panel shows:
- v (foot speed) = hamster.runningSpeed
- |ω|·R = wheel.omega * R (should equal v)
- discrepancy % = |v - |ω|·R| / v * 100

Since we SET omega = -v/R exactly (via lerp), discrepancy → 0. But to make it a genuine check, I compute |ω|·R from the actual wheel angular velocity and compare to the hamster's foot speed. Since omega tracks v/R, they match. Good. The lerp introduces tiny transient discrepancies but settles to ~0.

Actually, to make the check meaningful and honest: I compute omega from v/R, apply it. Then readback |omega|*R and compare to v. They'll match to within lerp error. Good.

**Hamster running speed variation:** Let me have the hamster accelerate/decelerate its runningSpeed toward a target, and omega follows. This makes it look natural.

Let me set: hamster.runningSpeed lerps toward targetSpeed (e.g., 0.6 m/s). omega lerps toward -runningSpeed/R. Both smooth.

**Distance traveled for phase:** distance += runningSpeed · dt. phase += distance/stepLength · 2π.

Now let me handle the wheel occupant entering/exiting.

**Entering wheel sequence:**
State 'entering_wheel': 
- Target: a point on the ground near the wheel's bottom edge, at the side the hamster approaches. Since the hamster faces +X and runs, it approaches from... the front? Actually the hamster climbs into the wheel from the side and positions at the bottom facing +X. Let me have it approach the wheel from the -X side (behind its facing? no). 

Hmm. Let me think. The hamster walks up to the wheel, positions itself at the bottom inside, facing +X, and starts running. The approach point: ground position = (wx, groundY, wz) but offset so it approaches from one side. Let me have it approach along the Z axis (from +Z side to the bottom). Actually the bottom of the wheel is directly below center, at (wx, wy-R, wz). The hamster needs to get there from the ground.

Let me define the "wheel entry point" on the ground as (wx, groundY, wz + approachOffset) where approachOffset is small (the hamster steps up into the wheel). Then it moves from ground to the wheel bottom position (wx, wy - R + legClearance, wz) smoothly (interpolate y and maybe x).

Actually the wheel bottom is at wy - R. The hamster's feet should be at the rim (wy - R). The hamster body center is above that. Let me place the hamster's position at the wheel bottom: hamster.position.y = wy - R (feet at rim bottom), and the hamster mesh sits above. Since I build the hamster with body above origin, placing group at (wx, wy-R, wz) puts feet near the rim. Let me make the hamster's feet at local y=0 (group origin at feet level) and body above. Then group.position.y = wy - R places feet at rim. 

Hmm, let me define the hamster group origin at the feet/ground level (y=0 at ground), body extends up. That makes positioning easier. So:
- Hamster standing on ground: group.position.y = 0, feet at y=0.
- In wheel: group.position = (wx, wy - R, wz), feet at rim bottom (wy-R).

Good.

For the smooth entry, I interpolate position from ground approach point to wheel bottom, and fade in. During entry, the hamster is not yet "occupant" so no collision exemption until settled. Let me handle: during entry, the hamster moves to the position; once there, set occupant.

Let me define entry as a sub-state with a timer, moving along a path. I'll just lerp position over ~0.8s.

**Tube entry sequence:**
State 'entering_tube':
- Approach near end of tube (outside the opening), then move into the tube along the axis to the inner bottom, starting at t≈0.
- Then 'moving_tube': t goes 0→1 (or 1→0), traveling through the tube.
- Then 'exiting_tube': move out the far end to ground.

Let me define tube entry point on ground near end P1: position just outside the opening along the axis direction, at ground level. Then descend into tube and move along.

**Bowl entry:**
- Approach bowl, position beside it, tilt head, chew. Duration, then leave.

**Walk:**
- Choose random point in cage, walk there, then idle.

**Idle:**
- Stand, breathe, occasional ear twitch. Occasionally pick a new goal.

**Goal selection:** every few seconds when idle, roll for activity:
- 35% wheel (if free)
- 25% walk
- 20% tube (if free)
- 20% bowl
If the preferred is occupied, retry or pick walk.

Let me implement a simple scheduler.

Now, movement: hamsters move by setting a target velocity toward the goal, with a max speed. I'll implement simple steering: 
```
dir = normalize(target - pos)
pos += dir * speed * dt
rotation.y = atan2(dir.x, dir.z)  // face direction
```
With collision avoidance (push out from obstacles) applied after.

Let me also add slight wandering when idle-walking.

Alright, let me also think about the cage layout and positions:
- Cage: rectangular, say 3.0m (X) × 2.2m (Z), on a table.
- Table height ~0.7m. Bedding on the tray at table-top level.
- Wheel at one end (say back-left corner area).
- Tube in the middle-ish, lying along Z or X.
- Bowl near another spot.
- Water bottle on a wall.

Let me place:
- Wheel center: (-1.0, tableTop + R + 0.05, -0.6). Wheel axis along Z. Wheel plane XY.
  - Wait, if wheel axis is along Z, the wheel is in XY plane. The hamster runs in +X/-X. Good.
- Tube: lying along X axis, from (-0.4, ...) to (0.6, ...), at tableTop + R_tube. Let me place it along Z actually to vary. Let me place tube along Z: from (0.7, tableTop+R_tube, -0.7) to (0.7, tableTop+R_tube, 0.7). Axis along Z. Hamster travels in Z inside.
  - But wheel axis is also along Z. That's fine, different locations.
  - Actually, to make the tube collision distinct, let me orient tube along X: from (-0.3, h, -0.8) to (0.7, h, -0.8). Hamster travels in X.
- Bowl: at (1.0, tableTop, 0.7) on the bedding.
- Water bottle: on the wall at (1.45, tableTop + 0.4, 0).

Let me finalize coordinates in code.

**Cage bars:** vertical bars around the perimeter. I'll generate a ring of thin cylinders. And top frame bars.

**Bedding:** InstancedMesh of small wood-shavings (tiny boxes or cones) scattered on the tray.

Let me now write everything. This will be long. Let me be careful with Three.js r128 API (uses BufferGeometry, etc.). r128 supports most modern API. OrbitControls from the examples js.

Note: In r128, THREE.js from cdnjs "three.min.js" — the global is THREE. OrbitControls from the examples js file registers THREE.OrbitControls.

Let me be careful: the cdnjs three.min.js r128 and the examples js three@0.128.0 OrbitControls should be compatible.

One concern: newer Chrome may warn about WebGL1 deprecation but it still works. r128 uses WebGL1. Should be fine.

Let me write the code now.

Let me define helper functions:
- lerp, clamp, normalize2D, etc.

Let me write the hamster builder carefully.

```javascript
function makeHamster(spec) {
  const g = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({ color: spec.color, roughness: 0.85 });
  const bellyMat = new THREE.MeshStandardMaterial({ color: spec.belly, roughness: 0.85 });
  
  // Body (ellipsoid)
  const bodyGeo = new THREE.SphereGeometry(1, 24, 18);
  const body = new THREE.Mesh(bodyGeo, fur);
  body.scale.set(B_LEN*0.5, B_HEIGHT*0.5*0.9, B_WIDTH*0.5);
  body.position.set(0, B_HEIGHT*0.5*0.55, 0);
  body.castShadow = true; body.receiveShadow = true;
  g.add(body);
  
  // Belly
  const bellyGeo = new THREE.SphereGeometry(1, 24, 18);
  const belly = new THREE.Mesh(bellyGeo, bellyMat);
  belly.scale.set(B_LEN*0.45, B_HEIGHT*0.4, B_WIDTH*0.45);
  belly.position.set(B_LEN*0.12, B_HEIGHT*0.5*0.4, 0);
  g.add(belly);
  
  // Head group
  const head = new THREE.Group();
  head.position.set(B_LEN*0.45, B_HEIGHT*0.55, 0);
  const headGeo = new THREE.SphereGeometry(1, 24, 18);
  const headMesh = new THREE.Mesh(headGeo, fur);
  headMesh.scale.set(B_HEAD*0.5, B_HEAD*0.48, B_HEAD*0.5);
  headMesh.castShadow = true;
  head.add(headMesh);
  // eyes
  ... 
  // ears, cheeks, nose, jaw
  g.add(head);
  
  // Legs
  const legs = [];
  const legDefs = [
    { name:'BL', x:-B_LEN*0.28, z: B_WIDTH*0.32, phase:0 },
    { name:'BR', x:-B_LEN*0.28, z:-B_WIDTH*0.32, phase:Math.PI },
    { name:'FL', x: B_LEN*0.30, z: B_WIDTH*0.32, phase:Math.PI },
    { name:'FR', x: B_LEN*0.30, z:-B_WIDTH*0.32, phase:0 },
  ];
  // diagonal pairs: BL&FR phase 0; BR&FL phase PI
  ...
}
```

Wait, diagonal pairs: BL & FR are diagonal (both right-side? no). Let me define: front-right (FR) is diagonal to back-left (BL). front-left (FL) diagonal to back-right (BR). So FR&BL same phase, FL&BR same phase, and the two groups π apart.

FR: x:+, z:- (front, right if z- is right)
BL: x:-, z:+ (back, left)
These are diagonal. Same phase. ✓
FL: x:+, z:+ 
BR: x:-, z:-
Diagonal. Same phase, π from the other group. ✓

So:
- FR phase 0, BL phase 0
- FL phase π, BR phase π

Let me assign:
- FR (x+, z-): phase 0
- BL (x-, z+): phase 0
- FL (x+, z+): phase π
- BR (x-, z-): phase π

Good.

Each leg: pivot group at the limb location, containing an upper and lower segment and a foot. Rotate pivot about Z to swing.

Let me build each leg as:
```javascript
const pivot = new THREE.Group();
pivot.position.set(lx, ly, lz);
const upper = new THREE.Mesh(cyl, fur);
upper.scale.set(0.5, legUpperLen, 0.5);
upper.position.set(0, -legUpperLen/2, 0);
const lower = new THREE.Group();
lower.position.set(0, -legUpperLen, 0);
const foot = new THREE.Mesh(sphere, fur);
...
pivot.add(upper); pivot.add(lower);
g.add(pivot);
legs.push({ pivot, lower, phase });
```

Animate: pivot.rotation.z = sin(phase)*amp; lower.rotation.z = ... (knee bend).

Hmm, but rotation about Z swings the leg in X-Y plane (forward-back). For the leg at z+ (left side), swinging about Z rotates it in X-Y. That moves the foot forward/back. Good. But the leg is on the side; rotating about Z (the horizontal axis pointing left-right) swings the leg forward/backward in the X-Y plane. Yes that works for all legs regardless of side (Z axis is consistent).

Wait, rotation about Z-axis: a leg hanging down at (x, 0, z) rotating about Z... the rotation is around the vertical? No. Z axis is horizontal (points to the left/right). Rotating about Z means the leg swings in the X-Y plane (the vertical forward-back plane). Yes. So the foot moves forward/back. 

But hold on — for a leg on the right side (z-) vs left (z+), rotating about the same Z axis swings both in the same rotational sense (both feet move +X when rotation positive). Since they're on opposite sides, does that look right? The leg hangs down from the body; rotating about the body's Z axis (which passes through the body) — but each leg has its OWN pivot at its location. So each leg rotates about a Z axis through its own shoulder. A positive rotation.z lifts the foot toward +X (forward) for legs on both sides. That looks like both feet swinging forward together — which for diagonal pairing with π offset means one pair forward, other back. That's the trotting look. OK good.

Actually, I realize rotating about Z for a leg means the foot swings in X-Y (vertical plane). For running, we want feet to push back and lift. This gives forward-back swing plus we add a lift via... hmm, rotation about Z alone keeps the foot at roughly the same height range but swings it forward/back in an arc (the foot goes forward and slightly up at the extremes). That's basically a pendulum swing. For a running look, adding a knee bend (lower segment) helps. Let me add lower.rotation to bend the knee during the swing-up.

Let me keep it simple but effective:
```javascript
const p = phase + leg.phase;
pivot.rotation.z = Math.sin(p) * SWING;          // swing foot forward/back
lower.rotation.z = Math.max(0, Math.sin(p)) * KNEE - KNEE_BASE; // bend
```

This should look like running. When phase frozen, constant → frozen feet. ✓

Let me also add a tiny body bob with running.

Now, the head nod and ear twitch and jaw:
- Head group has: head mesh, two eyes (white + pupil), two ears (capsule with inner), cheeks (small spheres), nose (small sphere), jaw (small mesh under head for chewing).
- Ear twitch: ear.pivot.rotation set randomly occasionally.
- Breathing: body.scale modulation.
- Chewing (bowl): head.rotation.x small oscillation + jaw.open oscillation.

OK let me write it all. Given length, I'll be efficient.

Let me also implement raycasting for click-to-jump. On click, find hamster under cursor, set a jump velocity, apply gravity, animate a hop (raise position, maybe tuck legs). Set hamster.jumping.

Jump: hamster.jumpVel = 1.2 (up), position.y += jumpVel*dt - 0.5*g*dt^2, when landed reset.

Let me handle ground collision: hamster on ground has y = 0 (feet at bedding). Actually the hamster group origin — let me put it at feet level, so ground position y=0. When jumping, y = jumpHeight.

Wait, I need consistency: the hamster's vertical position. Let me define hamster.baseY = 0 (standing on bedding). For wheel, baseY = wy - R. For tube, baseY = tubeInnerBottom + hamsterRadius. Movement in X-Z is independent; Y is set by state.

Let me store hamster.pos = {x, z} for horizontal, and hamster.y for vertical (set by state/jump).

Actually let me just use hamster.group.position.x/y/z directly and track a target for horizontal movement.

Let me define:
```javascript
hamster = {
  name, color, group, legs, head, ...
  pos: new THREE.Vector2(x, z),  // horizontal position
  vel: new THREE.Vector2(0,0),
  heading: 0,
  state: 'idle',
  goal: null,
  activity: null,
  timer: 0,
  phase: 0,
  distTraveled: 0,
  runningSpeed: 0,
  targetSpeed: 0,
  occupantOf: null,  // 'wheel' | 'tube' | null
  // occupancy flags on objects
  jumpVel: 0,
  jumping: false,
  ...
}
```

Movement: while 'going', steer pos toward goal