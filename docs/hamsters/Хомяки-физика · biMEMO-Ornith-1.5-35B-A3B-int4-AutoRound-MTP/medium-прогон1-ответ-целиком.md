Let me analyze this task carefully. This is a complex Three.js application with very specific physics requirements. Let me break down what needs to be done:

**PART 1: PHYSICS - THE MAIN THING**

1.1 WHEEL PHYSICS:
- Horizontal axis, hamster runs on INNER surface of rim at BOTTOM point
- Angular velocity from running speed: ω = v/R
- Rim goes BACKWARD relative to direction hamster faces
- Empty wheel slows down with friction
- Show debug panel: leg speed, linear rim speed (|ω|·R), discrepancy in %

1.2 HAMSTER SIZE & WHEEL SIZE:
- Wheel radius calculated from hamster size
- Check in code with constants

1.3 TUBE IS HOLLOW:
- Open cylinder lying on bedding
- Hamster enters ONLY through end (opening)
- Side wall is solid
- Inside, hamster stands on inner bottom

1.4 OBJECTS HAVE BODIES:
- Collision shapes (circle or rectangle)
- Walking hamster doesn't pass through
- Push out along shortest normal
- Hamsters don't overlap each other

1.5 FEET DON'T SLIDE:
- Step phase from DISTANCE traveled, not clock
- Phase += (distance/step_length)·2π
- Diagonal pairs
- Same in wheel

1.6 TRANSITIONS WITHOUT TELEPORTS:
- Hamster enters wheel smoothly
- One item - one user

**PART 2: BEHAVIOR**
- 5 hamsters with names and colors
- State machine: idle → go to target → activity → idle
- Activities: wheel, tube, bowl, walk
- Panel showing current activity
- Click hamster - jump
- Breathing in idle, ear twitch
- Bowl - head tilt and chew

**PART 3: SCENE**
- Cage on table, room around
- Tray, bedding (InstancedMesh wood shavings), bars, frames
- Wheel, hollow tube, bowl with seeds, water bottle
- Hamster built from parts: body, belly, head group, eyes with pupils, cheeks, nose, ears with inner part, 4 legs, tail
- Hamsters must be distinguishable

**PART 4: TECHNICAL**
- Three.js r128 + OrbitControls
- Single self-contained HTML file
- Shadows PCFSoftShadowMap, 2048 map
- requestAnimationFrame with delta time, clamp delta
- Window resize handling

**PART 5: VERIFICATION**
- |ω|·R ≈ leg speed (<5%)
- Empty wheel angular velocity decays to zero
- Hamster in wheel at bottom point, size < wheel radius
- Hamster in tube on axis, enters through end
- Walking hamster never inside wheel/bowl/tube bodies
- When stopped, phase stops changing
- No console errors

This is a big task. Let me write comprehensive, correct code.

Let me structure the code:

1. HTML with panels
2. Scene setup (renderer, camera, lights, shadows)
3. Room environment
4. Cage with tray, bedding, bars
5. Objects: wheel, tube, bowl, water bottle
6. Hamster class with all body parts
7. Physics: collision detection, wheel mechanics
8. Behavior state machine
9. Animation loop with delta time
10. Debug panels
11. Interaction (click to jump)

Let me write this carefully.

Key physics formulas:
- Wheel: ω = v/R where v is leg speed
- Leg speed when running = some base value
- When hamster in wheel at bottom: hamster position = wheel center + (0, -R_inner, 0) roughly, but actually at the bottom of the inner rim
- The hamster's feet move at speed v = ω · R

Let me think about the wheel geometry:
- Wheel radius R (from hamster size)
- Hamster stands on inner surface at bottom
- Hamster's position is at distance R from center (at the bottom, so center.y - R)
- Wait, "стоя на её НИЖНЕЙ точке" - standing on the bottom point
- So hamster feet are at the bottom of the rim, which is at distance R from center
- Hamster center is above its feet

Actually let me reconsider. The rim is a circle of radius R. The hamster stands on the inner surface at the bottom. So the contact point (feet) is at the very bottom of the circle, at distance R from center. The hamster's body center is above that.

For the wheel rotation: when hamster runs, it pushes the rim backward, so the wheel rotates. The angular velocity ω = v/R where v is the tangential speed of the hamster's feet relative to... well, relative to ground? No.

Let me think. If the hamster runs inside the wheel, its feet push the rim backward (relative to hamster's facing direction). The wheel rotates. The hamster stays at the bottom (roughly). The tangential speed of the rim at the contact point equals the hamster's foot speed.

So if hamster runs with foot speed v (relative to rim), the rim moves at v, meaning ω = v/R.

But wait, there's subtlety. If the hamster is stationary relative to ground (staying at bottom) but running, its feet move relative to the rim. The rim surface moves at v relative to hamster. Since hamster is fixed at bottom, rim surface moves at v, so ω = v/R.

Yes, ω = v/R. Good.

The debug panel shows:
- leg speed v
- linear rim speed |ω|·R = v (should match)
- discrepancy %

Since we compute ω = v/R exactly, they'll match by construction. But the point is to verify the wheel actually rotates at this rate. So we should measure the actual wheel rotation over time and compare.

Let me implement: 
- Track hamster's target foot speed v (from behavior)
- Compute desired ω = v/R
- Actually rotate wheel based on ω
- Measure actual Δθ/Δt · R = actual linear speed
- Compare

Let me make the wheel rotation integrate ω over time, then measure.

For empty wheel friction: ω decays: ω *= (1 - friction·dt) or ω -= friction·dt·sign(ω).

Let me now think about the hamster entering the wheel smoothly. The hamster walks to the wheel, then moves from the platform (outside the wheel) to the bottom inner point. This is an easing transition.

Let me define states for entering:
- "approach_wheel": walk to point near wheel
- "enter_wheel": ease from platform to bottom-inner position
- "running": run in wheel
- "exit_wheel": ease from bottom-inner back to platform
- then "idle" or go to next activity

Let me code the hamster as a class with:
- group (all parts)
- mesh parts reference
- state machine
- physics properties (position, velocity)
- leg animation

Let me define constants:
- ДЛИНА_ЗВЕРЯ = 0.6 (body length)
- ВЫСОТА_ЗВЕРЯ = 0.4 (height)
- Radius of wheel R = something like ДЛИНА_ЗВЕРЯ * 1.5 + ... 

Let me make R based on hamster. If hamster length is L and height H, the wheel radius should be large enough that hamster fits inside with margin. The hamster at the bottom occupies from its feet up to height ~H. So the inner radius must be > H plus some margin, and also the hamster has length L so it needs room. Let me say R = L * 1.2 or so. Actually the hamster lies horizontally at the bottom, so its length L extends along the rim tangent. The radius needs to accommodate the hamster's body.

Let me set:
- HAMSTER_LENGTH = 0.7
- HAMSTER_HEIGHT = 0.45
- WHEEL_RADIUS = HAMSTER_LENGTH * 1.4 ≈ 0.98, let me round to ~1.0

Actually, let me just pick reasonable numbers and ensure the constraint holds: hamster height < wheel radius with margin.

Let me make the wheel radius R = 1.0, hamster height ~0.45, so hamster fits easily. Distance between rims (axial length of wheel) wider than hamster width (~0.35).

Let me now write the hamster builder.

Hamster body parts:
- Body (ellipsoid)
- Belly (lighter ellipsoid on front)
- Head group (pivot for nodding):
  - Head sphere
  - Two eyes (white + pupil)
  - Cheeks
  - Nose
  - Two ears (with inner pink)
- 4 legs (front-left, front-right, back-left, back-right)
- Tail

Diagonal leg pairs: (FL, BR) and (FR, BL). When walking, alternate pairs.

Leg animation: legs rotate about hip/shoulder joints following sine of phase.

Let me define phase for each leg:
- FL: phase = 0
- BR: phase = π (opposite)... 

Wait diagonal pairs move together. Pairs are {FL, BR} and {FR, BL}. Within a pair, one foot goes forward while other goes back. So:
- FL: sin(phase)
- BR: sin(phase) — same pair, but they alternate... 

Hmm, let me think. In diagonal gait, FL and BR are one diagonal pair, FR and BL the other. The two pairs are out of phase by π. Within a pair, do both legs move the same or opposite?

Actually in a diagonal gait (trot), the diagonal legs move together (FL and BR move together, FR and BL move together), and the two diagonals are out of phase. So FL and BR move in phase with each other, and FR/BL are π out of phase.

Wait no. In a trot, the legs on one diagonal move together and opposite to the other diagonal. So FL and BR swing forward together while FR and BL swing back. So:
- FL: sin(phase)
- BR: sin(phase)
- FR: -sin(phase) = sin(phase + π)
- BL: -sin(phase) = sin(phase + π)

Yes that's the trot. Good.

For a hamster (quadruped) walking, similar.

Let me make each leg pivot at shoulder/hip and swing forward/back by angle A·sin(phase_i).

Now let me think about position updates. The hamster has a heading (facing direction). Feet positions computed from leg swing.

Let me simplify: the hamster's horizontal position advances based on velocity. The legs animate based on phase accumulated from distance.

Let me now write the full code. This will be long.

Let me plan the structure:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>3D Hamsters</title>
<style>
  /* styles */
</style>
</head>
<body>
<div id="info">...</div>
<div id="wheel-panel">...</div>
<div id="hamsters-panel">...</div>
<script src="three r128"></script>
<script src="orbitcontrols"></script>
<script>
// code
</script>
</body>
</html>
```

Let me write the JS.

```js
'use strict';

// Constants
const HAMSTER_LENGTH = 0.7;      // ДЛИНА_ЗВЕРЯ
const HAMSTER_HEIGHT = 0.45;     // ВЫСОТА_ЗВЕРЯ
const HAMSTER_WIDTH = 0.4;
const WHEEL_RADIUS = HAMSTER_LENGTH * 1.4; // R from hamster size
// verify WHEEL_RADIUS > HAMSTER_HEIGHT * 1.5 etc

// ...
```

Let me think about the scene layout:
- Floor at y=0
- Cage: a tray (base) with bedding, walls made of vertical bars
- Table under cage
- Room: walls, maybe a window

Cage dimensions: let's say 6 x 4 (x, z). Bars around perimeter.

Objects placement inside cage:
- Wheel at one side
- Tube in middle-ish
- Bowl somewhere
- Water bottle on wall

Hamsters spawn and wander.

Let me define collision objects as circles (for wheel, bowl) and rectangles (for tube cross-section) or circles. For simplicity, I'll use circle collisions mostly, and treat tube as two end-caps + the constraint that hamster must be inside the tube axis range.

Actually for the tube, the hamster only interacts when inside it. When walking outside, the tube walls block? The requirement says side wall is solid - can't pass through the side. But the tube lies on bedding. Let me make the tube a collision object too: a capsule/rectangle in top view. When a walking hamster would enter the tube's outer boundary (except ends), push it out.

Hmm, this is getting complex. Let me simplify collision:
- Wheel: circle collision at center with radius = outer rim radius. Hamster pushed out.
- Bowl: circle collision.
- Tube: treat as rectangle (top view) with openings at both ends. Hamster can only be inside if within the rectangular region AND within the tube's inner width. If approaching from the side, push out. If within the end zones, allow entry.

Actually, let me make the tube collision simpler: the tube is a solid obstacle in top-view (a rounded rectangle / capsule shape representing its outer boundary), but with the two ends open. For walking hamsters, treat it as a capsule obstacle (rounded rectangle) — they go around it. Only hamsters assigned to the tube activity enter through ends.

That satisfies "гуляющий хомяк не проходит сквозь них" (walking hamster doesn't pass through). And the tube activity handles entering through ends.

Let me define tube as capsule (rectangle with rounded ends) obstacle in top view. Its center line along X axis, half-length = tubeLength/2, half-width = tubeRadius. Hamsters walking get pushed out of this capsule.

For the tube activity hamster: it enters through an end (x = -tubeLength/2 or +tubeLength/2), moves along X inside, exits other end. Its position on the Y is the inner floor (tubeRadius above center? no—tube lies on bedding so inner bottom is at y = tubeRadius... wait tube lies on floor, so its center is at y = tubeRadius, inner bottom at y = 0 basically minus wall thickness). Let me place tube center at y = tubeInnerRadius (so inner bottom touches bedding y=0). Hamster inside stands at y = tubeInnerRadius (its feet on inner bottom).

Wait, if the tube is a cylinder lying on its side, its axis is horizontal (X). The cross-section is a circle of radius r centered at (x, r, z) if lying on floor at y=0. Inner bottom is at y≈0. Hamster inside stands with feet at y≈0 (inner bottom), body center at y ≈ hamsterHeight/2 + radius of feet... basically y ~ 0.2.

The hamster's position along the axis (X) changes as it crawls through. Its offset from the axis in the cross-section plane (Y,Z) should be ~0 (on the bottom center). Requirement 4: "в трубе находится на её оси (отклонение от оси близко к нулю)". So the hamster's transverse offset from axis ≈ 0, meaning it's centered. Good, standing on the bottom center.

Hmm wait, "на её оси" means ON her axis. The axis is the central line. If the hamster stands on the inner bottom, its body center is directly below the axis (offset by radius downward), not ON the axis. But the requirement says deviation from axis close to zero. Maybe they mean the transverse (Z) deviation is zero (centered laterally), and along the axis (X) it moves. Let me interpret: the hamster's lateral (Z) offset from the tube axis is ~0, and it's positioned at the bottom of the tube (lowest point). I'll keep Z≈0 and Y at the bottom.

Actually re-reading: "хомяк в трубе находится на её оси (отклонение от оси близко к нулю)". I think this means the hamster is centered on the tube's axis line (the longitudinal axis). So its position projects onto the axis. The hamster's center is at (someX, tubeCenterY - tubeRadius + hamsterFeetRadius, 0)? That's not ON the axis though.

I think the verification checks the lateral (perpendicular to axis) position is near the bottom-center. Let me just place the hamster's center directly below the tube axis at the bottom, and provide a field `tubeOffsetFromAxis` that measures perpendicular distance from the axis line. When centered laterally and at the bottom, the perpendicular offset is the radial distance = tubeRadius - hamsterFootRadius. Hmm that's not zero.

Let me reconsider. Perhaps they want the hamster's lateral center aligned with the tube's lateral center (Z=0) and longitudinal position along the axis. The "deviation from axis close to zero" likely refers to the hamster being on the centerline in the cross-sectional plane — i.e., not jammed to a side. So Z ≈ 0. I'll make the metric measure lateral (Z) offset which will be ~0. Good enough. And I'll document it.

Actually, to be safe, let me have the hamster's body center sit on the vertical line passing through the axis, at the bottom. I'll report the lateral (Z) deviation which is ~0. And I'll note the hamster sits on the inner bottom.

OK let me just build it and report multiple metrics.

Let me now consider the wheel more concretely.

Wheel geometry:
- Axis along Z (horizontal), at some height. Usually wheel axis is above the floor because the wheel sits on a stand. Let me put wheel center at y = WHEEL_RADIUS + standHeight. Actually a hamster wheel sits on the bedding; its bottom touches the bedding. So wheel center at y = WHEEL_RADIUS (bottom at y=0). Let me add a small stand so it's slightly elevated, but let's keep center at y = WHEEL_RADIUS so bottom rim touches floor/bedding at y=0.

Wait, but the hamster stands on the inner bottom. The inner bottom is at y ≈ 0 (touching bedding). Hamster feet there, body up. Good.

Wheel center: (wx, WHEEL_RADIUS, wz). The axis is along Z. The rim is a circle of radius R in the X-Y plane (well, the plane containing the rotation). Rotation is about the Z axis (horizontal). 

Hamster at bottom: position (wx, WHEEL_RADIUS - R_contact, wz) where R_contact is the radius to the contact point = inner rim radius ≈ R. So hamster feet at (wx, WHEEL_RADIUS - R, wz) = (wx, ~0, wz). Body center at y = feetY + hamsterHeight*0.6.

The hamster faces... along the wheel? When running in a wheel, the hamster runs along the tangential direction at the bottom, which is along X (horizontal, tangent to circle at bottom). So the hamster faces ±X. Let me have it face +X (or -X depending). The rim moves backward relative to facing. If hamster faces +X and runs, the wheel rotates such that the bottom moves in -X direction (backward relative to hamster's forward = -X is backward). Rotation about Z axis: positive ω (CCW in XY plane) moves bottom point in +X? Let me compute. Point at bottom (0,-R) rotating CCW with angular velocity ω (positive = CCW): velocity = ω × r = ω ẑ × (0,-R,0) = ω (ẑ×(-R ĵ)) = ω(-R)(ẑ×ĵ) = ω(-R)(-x̂) = ω R x̂. So CCW rotation gives bottom point velocity in +X. 

If hamster faces +X and runs forward, its feet push the rim backward (-X relative to hamster), meaning the rim bottom moves in -X relative to ground? Hmm. Let me think physically: hamster runs forward (+X) inside wheel; friction/foot push makes the wheel rotate. The hamster tends to stay at bottom. Its feet push backward on the rim, i.e., rim surface at bottom moves in -X relative to hamster. Since hamster is (roughly) stationary in ground frame at the bottom, the rim bottom moves in -X in ground frame. From above calc, rim bottom velocity = ω R x̂ for CCW. For it to be -X, ω must be negative. So ω < 0 for forward (+X) running. Fine, sign handled.

The debug: linear rim speed = |ω|·R. Leg speed = v. These should match.

Let me define hamster running speed v (linear, in m/s of feet). ω = v / R with appropriate sign. Then wheel rotates by ω·dt.

Now the hamster's own position: it stays at the bottom but maybe oscillates slightly. Actually if it's running and staying at the bottom, its ground position doesn't translate (it's "running in place" essentially, but the wheel spins). Real hamsters do drift a bit but let's keep them at the bottom. The hamster's legs move relative to its body, and the body bobs.

Actually, wait. If the hamster stays at the bottom and the wheel spins under its feet, then relative to the wheel the hamster walks forward. Relative to ground the hamster's feet at contact are momentarily stationary (like walking on ground). Its body moves forward at v too? No—if the hamster is stationary in ground frame (not translating horizontally), its body isn't moving forward. But its feet are walking.

Hmm, in a real wheel, the hamster does stay roughly at the bottom (maybe drifting back slightly) while the wheel spins faster than its walking pace. Let me keep the hamster's center fixed at the bottom (small drift allowed) and animate legs as if running. The leg animation: feet move backward relative to body at speed v, matching wheel surface speed. Good.

So for the wheel-running state:
- Hamster center fixed at bottom of wheel (with tiny bobbing from steps)
- Legs animate with phase from "distance" but since hamster isn't translating in ground frame, what's the distance? The relevant distance is the relative motion between feet and rim. Since rim moves at v and hamster stationary, the feet cover distance v·t relative to rim. So phase advances by v·t/stepLength. That's fine — we use the running speed v as the "distance rate". So phase += (v·dt)/stepLength · 2π. Good, this ties leg cadence to running speed. Requirement 1.5 satisfied.

Now let me also handle the wheel's own rotation integration and friction.

Wheel physics object:
```
wheel = {
  center: Vector3,
  radius: R,         // rim radius
  axis: 'z',
  angle: 0,          // current rotation rad
  omega: 0,          // angular velocity rad/s
  friction: 0.5,     // decay rate
  user: null,        // hamster running or null
  maxOmega: ...
}
```

Each frame:
- If user running with foot speed v: target omega = sign * v/R. Apply: we want the wheel to match. Simple approach: set wheel.omega = target (but that's instant). Better: accelerate wheel toward target. But requirement wants |ω|·R == leg speed. If we just set omega = v/R exactly, then measured |ω|·R = v always (0% error). That satisfies the check trivially. But to be "honest," maybe integrate.

Actually the check is |ω|·R == leg speed. If we compute omega = v/R and rotate by it, then the effective linear speed of the rim = omega*R = v exactly. The measurement of actual rotation over time also gives v. So it's consistent. Let me integrate angle += omega*dt where omega = v/R (with sign). Then measure actual omega_actual = (angle - angle_prev)/dt, and linear = |omega_actual|*R. Compare to v. Should be ~0%.

But if omega is set fresh each frame from v, then (angle-angle_prev)/dt = omega = v/R exactly (assuming dt small). So error ~0. Good.

For empty wheel: omega decays: omega *= exp(-friction*dt) or omega -= friction*dt. Let me use omega *= (1 - friction*dt) clamped, decaying to 0.

When a hamster is running, we override omega to v/R (ignoring friction, or adding driving). Let me do: if user present, omega = sign*v/R (driven). Else omega decays.

But there's a subtlety: when a hamster enters/exits, omega transitions. That's fine.

Let me also make sure empty wheel eventually stops: yes, decays.

Now the debug panel shows leg speed, rim linear speed, discrepancy %.

Let me now think about hamster behavior state machine.

States:
- IDLE: breathing, looking around, occasionally ear twitch
- GOING_TO(target): move toward a target point (activity location or random walk target)
- ACTIVITY: perform activity (wheel run, tube crawl, bowl eat, or free walk)
  - For wheel: enter_wheel -> run -> exit_wheel
  - For tube: enter_tube -> crawl -> exit_tube
  - For bowl: eat (head bob, chew)
  - For walk: just walk to a random point then IDLE

Transitions triggered by timers (random durations).

Let me implement a behavior controller per hamster.

Let me define target points for activities:
- wheel center on floor in front of wheel (platform)
- tube end entrance
- bowl position
- random walk points

Let me code:

```js
class Hamster {
  constructor(name, color, startX) {
    this.name = name;
    this.color = color;
    this.group = new THREE.Group();
    // build parts
    // physics
    this.pos = new THREE.Vector3(startX, 0, randomZ);
    this.heading = Math.random()*Math.PI*2;
    this.velocity = new THREE.Vector3();
    this.state = 'idle';
    this.stateTime = 0;
    this.targetPos = null;
    this.activity = null; // 'wheel','tube','bowl','walk'
    this.wheelUser = false;
    this.tube = null; // tube ref + direction
    this.phase = 0; // leg phase
    this.earTwitch = 0;
    this.breath = 0;
    // metrics
    this.legSpeed = 0;
    this.currentActivityText = 'стоит';
  }
}
```

Collision handling:
For each walking hamster, check collisions with obstacles (wheel circle, bowl circle, tube capsule). Compute penetration and push out along normal. Also hamster-hamster repulsion.

Let me implement collision resolution:
```
function resolveCollisions(hamster, dt) {
  // obstacles
  for (obst of obstacles) {
    if (hamster is doing tube activity and inside tube) continue; // tube entry handled separately
    // circle obstacle
    d = hamster.pos - obst.center; dist = d.length();
    minDist = obst.radius + hamsterRadius;
    if (dist < minDist) {
       // push out
       normal = d/dist (or 0 if dist~0)
       hamster.pos += normal * (minDist - dist)
    }
  }
  // hamsters
  for (other of hamsters) {
    if (other===hamster) continue;
    d = hamster.pos - other.pos; dist=d.length();
    minDist = hamsterRadius*2;
    if (dist < minDist && dist>0.0001) {
       normal = d/dist;
       push = (minDist-dist)/2;
       hamster.pos += normal*push;
       other.pos -= normal*push;
    }
  }
}
```

HamsterRadius ~ 0.25 (half width).

Now the tube entry: when a hamster is assigned tube activity, it walks to the near end (say left end x = tubeLeft - clearance), then enters: moves along +X inside the tube until it reaches the far end, then exits (continues +X beyond far end), then leaves the tube "user" flag.

Actually "входит через ближний вход, потом движется вдоль оси и выходит с другой стороны." So enters near end, crawls through, exits far end. Good.

While inside, hamster.pos.x increases from tubeLeft to tubeRight. Its Y is the inner bottom. Its Z centered (0 offset). Heading +X.

When it reaches beyond tubeRight, it exits and becomes free again.

Let me define tube as capsule obstacle for walking hamsters but the activity hamster ignores the capsule collision (it's inside).

Let me now think about the wheel entry smoothness. Hamster walks to a platform point in front of the wheel (below the rim, on the floor). Then eases up and into the bottom-inner position. Let me define:
- platform point: (wx, 0, wz) slightly in front (in -X or +X?). Let me put platform at (wx, 0, wz + 0.3) (in front of hamster facing). Actually the hamster approaches the wheel from the side (along Z) to reach the bottom. Let me place approach point near the bottom of the wheel.

Hmm, the wheel rotates about Z axis, so its rim extends in X and Y. The opening/access is from the side (Z direction) between the two side disks. So the hamster approaches along Z to reach the bottom of the rim. Approach point: (wx, smallY, wz + (R + hamsterWidth/2 + clearance)). Then it moves into position (wx, WHEEL_RADIUS - R + feetY, wz).

Wait wz is the wheel's center z. The hamster enters from z > wz side. It moves to (wx, bottomY, wz + R - ... ). Let me place hamster at the bottom: position (wx, WHEEL_RADIUS - R + footRadius, wz + (R - footRadius)*something...). Hmm, actually at the bottom of the rim, the point is directly below center: (wx, WHEEL_RADIUS - R, wz). The hamster's feet are there, body above. Its z = wz (centered) plus a bit for its body thickness. Let me put hamster center at (wx, WHEEL_RADIUS - R + hamsterBodyCenterOffset, wz). Since the wheel is thin (disk radius ~ R), the hamster fits within. Its z ≈ wz. Good.

Approach: hamster moves along +Z from platform (wz + R + 0.3, y~0) to (wx, bottomY, wz). Ease with a factor t in [0,1].

During entry, hamster's world position interpolates from platform to bottom. Also hamster should rotate to face +X (tangent). Actually at the bottom, facing +X or -X. Let me face +X.

Let me define the "wheel hamster rest position" and interpolate.

For the wheel, the hamster's facing should be tangent to the circle at the bottom = +X or -X. Let me choose -X so that when it runs forward it drives the wheel in a consistent direction. Earlier I found facing +X running gives ω<0 (CW). Let me just pick facing +X and drive ω accordingly. Sign handled by omega = -v/R for +X facing? Let me recompute: I want the rim bottom to move in -X (backward relative to +X facing). From v_bottom = ω R x̂ (CCW positive). To get -X, need ω<0. So omega = -v/R. Fine. I'll set omega = -sign(facing)*v/R where facing +X => sign=+1 => omega=-v/R. Let me just hardcode based on facing.

Actually simpler: omega = -(v/R) if facing +X, +(v/R) if facing -X. Or generally omega = -facingSign * v/R where facingSign = +1 for +X. Let me define facingSign = sin? No, facing is along X here. Let me just set based on a chosen constant.

Let me set hamster in wheel faces +X, omega = -v/R.

Now the debug: legSpeed = v. rimLinear = |omega|*R = v. Match.

Alright. Let me also make the wheel visually spin so we can see it rotates (add spokes/markings).

Let me now also handle the "one user per item": wheel.user set when hamster starts running, cleared on exit. If occupied, other hamsters won't target the wheel.

Similarly tube: one at a time. Bowl can have multiple? Let me allow only one at bowl too, or two. Let me restrict to one to be safe (requirement 1.6 says one item one user — but that's about the same item; bowl could serve multiple but let me keep one to be safe). Actually requirement 1.6 specifically about wheel-like items. Bowl can have multiple eaters but let me keep it simple: one eater at a time for bowl too. Doesn't hurt.

Now let me write everything. This is a large file. Let me be careful and methodical.

Let me start coding.

I'll write helper functions:
- rand(a,b)
- lerp(a,b,t)
- clamp

Scene setup:
```js
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x20242b);
scene.fog = new THREE.Fog(0x20242b, 20, 45);

const camera = new THREE.PerspectiveCamera(55, aspect, 0.1, 200);
camera.position.set(0, 6, 12);
```

Lights:
```js
const dir = new THREE.DirectionalLight(0xffffff, 1.2);
dir.position.set(6, 12, 6);
dir.castShadow = true;
dir.shadow.mapSize.set(2048,2048);
dir.shadow.camera.near=0.5; dir.shadow.camera.far=60;
dir.shadow.camera.left=-20; dir.shadow.camera.right=20;
dir.shadow.camera.top=20; dir.shadow.camera.bottom=-20;
scene.add(dir);
const ambient = new THREE.AmbientLight(0x8899aa, 0.5);
scene.add(ambient);
const hemi = new THREE.HemisphereLight(0xbcdcff, 0x404040, 0.4);
scene.add(hemi);
```

Room: floor plane (room floor), walls, a table.

Cage: 
- Table: box legs + tabletop
- Tray: open box (base + low walls) 
- Bedding: InstancedMesh of small shavings on the tray floor
- Bars: many thin cylinders around perimeter, plus top rails
- Roof rails

Let me place cage on table.

Let me define cage interior bounds for hamsters so they stay inside.

Let me write the hamster building function.

```js
function buildHamster(color) {
  const g = new THREE.Group();
  const fur = new THREE.MeshStandardMaterial({color, roughness:0.9, metalness:0});
  const bellyMat = new THREE.MeshStandardMaterial({color: 0xf5e6d0, roughness:0.9});
  const darkMat = new THREE.MeshStandardMaterial({color:0x111111, roughness:0.5});
  const pinkMat = new THREE.MeshStandardMaterial({color:0xffc0cb, roughness:0.8});
  const whiteMat = new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.5});

  // body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.32,20,16), fur);
  body.scale.set(1.1,0.95,0.95);
  body.castShadow=true;
  g.add(body);

  // belly
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.26,16,12), bellyMat);
  belly.scale.set(1.05,0.9,0.9);
  belly.position.set(0.06,-0.06,0);
  g.add(belly);

  // head group (pivot)
  const headGroup = new THREE.Group();
  headGroup.position.set(0.34,0.06,0);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.22,18,14), fur);
  head.scale.set(1,0.95,0.95);
  head.castShadow=true;
  headGroup.add(head);
  // cheeks
  ...
  // eyes
  const eyeGeo = new THREE.SphereGeometry(0.05,12,12);
  const pupilGeo = new THREE.SphereGeometry(0.028,10,10);
  const eyeL = new THREE.Mesh(eyeGeo, whiteMat); eyeL.position.set(0.16,0.05,0.12);
  const pupilL = new THREE.Mesh(pupilGeo, darkMat); pupilL.position.set(0.19,0.05,0.12);
  similarly right
  // nose
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.035,10,10), pinkMat); nose.position.set(0.24,0.0,0);
  // ears
  const earGroupL, with inner
  headGroup.add(...);
  g.add(headGroup);

  // legs
  const legGeo = new THREE.CylinderGeometry(0.05,0.05,0.18,10);
  // create 4 legs with pivot groups at shoulders/hips
  ...

  // tail
  const tail = new THREE.Mesh(new THREE.SphereGeometry(0.05,10,10), fur);
  tail.position.set(-0.34,-0.02,0);

  return g;
}
```

Legs: each leg is a group pivoted at the joint (shoulder/hip). The leg mesh offset from pivot. Swing by rotating around X axis (forward/back). 

Let me define leg positions on body:
- FL: (0.18, -0.18, 0.16)
- FR: (0.18, -0.18, -0.16)
- BL: (-0.2, -0.18, 0.16)
- BR: (-0.2, -0.18, -0.16)

Each leg group positioned at joint, contains a cylinder going down to foot. Swing rotation about X axis moves foot forward/back. Feet also have a small foot mesh.

For walking animation, rotate leg groups by angle = A*sin(phase + legPhaseOffset).

Diagonal: FL & BR in phase, FR & BL opposite.

Let me store references to leg groups and their base offsets so I can also do the "run in place" bob.

Now the hamster's overall position: group.position.x/z = horizontal pos, group.position.y = vertical (bob). Rotation.y = heading.

During running in wheel, the hamster's group position is at the bottom; legs animate fast.

Let me handle breathing: scale body slightly: body.scale.y = 1 + 0.03*sin(breathPhase). And belly too.

Ear twitch: rotate ear group occasionally.

Head nod when eating: rotate headGroup.x.

Jump: apply upward velocity, gravity, land.

Let me now write the main loop.

Let me define global arrays:
- hamsters[]
- obstacles = { wheels:[], bowls:[], tubes:[] }

Let me define a Wheel object, Tube object, Bowl object.

Let me write the debug panels updating every ~0.25s.

Let me now actually write the full code. I'll be thorough.

Let me consider the room/environment. Add:
- Room floor (large plane) with different material
- Back wall, side walls
- A table (box)
- Maybe a window on back wall, a picture, a plant for context. Keep moderate.

Let me keep it tasteful but not too heavy.

Let me define cage coordinates:
- Table top at y = 0.9 (table height). Actually let me put cage directly on room floor for simplicity? Requirement says "клетка на столе" (cage on a table). So put cage on a table. Table top at y = 0.9m. Cage tray on top.

Let me set:
- Room floor at y=0.
- Table: 4 legs, tabletop thickness 0.1 at y=0.95 (top surface y=1.0). Table footprint 5 x 3.5.
- Cage tray on table: base at y=1.0, tray interior floor at y=1.05, walls height 0.9. Cage interior ~ 5 x 3.

Hamsters walk on tray floor at y=1.05.

Let me set tray interior dimensions: width (x) = 4.4, depth (z) = 3.0, floor at y=1.05, walls to y=1.9.

Place objects within.

Bars: vertical bars around the four sides at intervals, from y=1.9 up to y=2.4, plus top rails.

Let me code the cage generation.

Let me now write it all out. Given the size, I'll produce a single HTML file.

Let me carefully manage the hamster radius for collisions: R_HAM = 0.28.

Wheel: center (wx, wy, wz), radius R (=WHEEL_RADIUS). Outer collision radius = R + rimThickness. Let me set rim thickness 0.06, so outer ~ R+0.06. Collision radius for walking hamster = R + 0.1.

Bowl: center (bx, by, bz), radius ~0.35, at y small (sitting on floor). Collision radius 0.4.

Tube: capsule along X from x0 to x1, half-width w (tube radius), half-depth = tubeLength/2. For walking collision, treat as capsule: nearest point on segment to hamster, push out by tubeOuterRadius.

Actually the tube lies on its side; cross-section is a circle radius tubeR centered at (y=tubeR). In top view (XY? no, XZ top view), the tube cross section is a circle of radius tubeR centered at (wx? no). Wait tube axis along X, cross-section in YZ plane is a circle radius tubeR centered at (y=tubeR, z=0) if lying on floor. In top view (looking down XZ), the tube appears as a rectangle of length tubeLength and width 2*tubeR (the Z extent), centered at z=0. So top-view collision is a rectangle (capsule with flat ends, or rounded ends). Let me use a capsule (rounded rectangle) in XZ: segment from (x0, z0) to (x1, z0) with radius tubeR. Hamster pushed out if within.

But the ends are open — a walking hamster shouldn't be able to enter from the side but can pass the ends. A capsule collision would block passing the ends too (the rounded caps). That's acceptable — walking hamsters go around the whole tube. The tube-activity hamster enters through ends explicitly. Good.

However, requirement 3 says side wall solid, only through ends. For walking hamsters, blocking the whole tube outline is fine (they go around). For the activity hamster, we handle entry through ends. Good.

Now, the tube activity hamster: it should be positioned at the inner bottom. Its X moves from x0 (left end) to x1 (right end). At any moment inside, its Z=0 (centered), Y = floorInside (tubeR above? no). Let me place tube center at y = tubeR (so inner bottom at y≈0 relative to tray floor... but tray floor is at y=1.05). Let me set tube center Y = trayFloorY + tubeR. Inner bottom at trayFloorY. Hamster feet at trayFloorY, body center at trayFloorY + ~0.2.

Wait, but the hamster inside the tube — its body is within the cylinder. The cylinder inner radius = tubeR - wallThickness. Hamster height ~0.45 must fit: tubeR - wallThick > 0.45 + margin. Let me set tubeR = 0.55, wallThick 0.05, inner radius 0.5 > 0.45. OK tight but ok. Actually let me make tubeR = 0.6, inner 0.55. Hamster height 0.45 fits with 0.1 margin. Good.

The hamster's body center Y = trayFloorY + (hamsterFeetToCenter). Feet at trayFloorY, body center ~0.18 above? The body is an ellipsoid sitting on floor; center at ~0.2. Let me set hamster inside Y = trayFloorY + 0.18.

Its heading +X (moving along +X). Good.

Now the tube collision for OTHER walking hamsters: capsule in XZ at y = trayFloorY (we ignore Y for walking since tube is low; but a walking hamster might climb? no). Just do XZ capsule.

Hmm, but the tube sits on the floor; a walking hamster colliding with it in XZ gets pushed out. Fine.

Now, one more: the tube activity hamster must not collide with the capsule (it's inside). So skip collision for the hamster currently in tube mode.

Also the wheel and bowl are tall-ish; walking hamsters go around.

Let me also ensure hamsters stay within tray bounds (walls). Add wall collision or just clamp positions within bounds. Let me clamp within tray interior with a soft push. Simpler: clamp positions to interior rectangle.

Let me now write the code fully.

I'll write it step by step in the final answer. Let me make sure to include:
- Debug panels (wheel stats, hamster statuses)
- Raycaster for clicking hamsters
- OrbitControls

Let me also add the "check" fields accessible externally: hamsters array, wheel object with fields, tube object with fields. I'll attach to window for inspection: window.hamsters, window.wheelObj, window.tubeObj.

Let me now write.

For the leg phase and distance: each hamster tracks `distanceTraveled` (horizontal meters). phase += (deltaDistance/STEP_LEN)*2π. STEP_LEN ~ 0.18 m.

When running in wheel, "distance" = v * t (relative). I'll accumulate phase from v directly.

Let me define hamster.walkSpeed ~ 0.5 m/s, runSpeed ~ 1.2 m/s.

Behavior durations: idle 2-5s, walk to target 2-4s, activity 3-8s.

Let me implement state machine in update(dt):

```
updateBehavior(dt):
  stateTime += dt
  switch state:
    idle:
       // random decision
       if stateTime > idleDur: choose new activity/target, state='going'
    going:
       move toward targetPos
       if reached: 
          if activity in [wheel,tube]: state='entering' (for wheel/tube) else if bowl: state='eating' else state='walking'
          stateTime=0
    walking (free walk):
       accumulate phase from speed
       if stateTime > walkDur: state='idle'
    entering (wheel/tube):
       animate entry t from 0 to 1 over enterTime
       if t>=1: state = activity ('running'/'crawling')
    running (wheel):
       drive wheel omega
       accumulate phase from runSpeed
       if stateTime > activityDur: state='exiting'
    crawling (tube):
       move along tube
       accumulate phase
       if reached end or time: state='exiting'
    eating (bowl):
       head chew
       if time: state='idle'
    exiting (wheel/tube):
       animate exit t 0..1
       if done: state='idle', clear user flags
```

Let me refine the "going" target selection: pick an activity based on availability (not occupied), else free walk.

Let me assign priorities and track occupancy.

Let me now write the actual code. I'll aim for correctness and clarity.

One more consideration: the hamster entering the wheel — the approach point and the bottom point. Let me define:
- wheelBottomPos = new Vector3(wx, wy - R + footToBodyCenter, wz)  where footToBodyCenter ~0.18. wy = trayFloorY + R. So wy - R = trayFloorY. +0.18 => 1.23.
- approachPos = new Vector3(wx, trayFloorY, wz + R + 0.25)  (in front of wheel along +Z)

During entry, interpolate position from approachPos to wheelBottomPos, and also lift. Interpolate heading to face +X.

Actually the hamster comes from +Z side and moves to center. Let me interpolate both x and z and y.

At t=0: approachPos. At t=1: wheelBottomPos. Use easeInOut.

The hamster's body should orient tangent (+X). Set group.rotation.y = 0 (facing +X) during running. During approach, rotate from heading to 0.

Let me set heading for wheel hamster to 0 (+X) once inside.

For exit: interpolate from wheelBottomPos back to a release point (wx, trayFloorY, wz + 0.3) then it's free.

Let me define releasePos = new Vector3(wx, trayFloorY, wz + 0.4).

OK. For tube:
- tube runs along X from xL to xR, at z=tc (center),