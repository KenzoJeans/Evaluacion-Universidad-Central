import json
import math

import streamlit as st

from planos3d import HOMO_FRANCO, HOMO_H

AZUL, ACERO, GRIS, AGUA, FLUJO, LODO, AIRE = "#1f6feb", "#c9d1d9", "#6e7681", "#3fb950", "#00e5ff", "#f0883e", "#e6edf3"
R2 = math.sqrt(2)


def caja(p, s, c=AZUL, o=1.0, e=0):
    return {"k": "box", "p": p, "s": s, "c": c, "o": o, "e": e}


def cil(p, r, h, ax="z", c=ACERO, o=1.0, e=0):
    return {"k": "cyl", "p": p, "r": r, "h": h, "ax": ax, "c": c, "o": o, "e": e}


def tc(p, rt, rb, h, n=32, c=AZUL, o=0.96, e=1):  # tronco: p = centro (x, y) y z superior
    return {"k": "tc", "p": p, "rt": rt, "rb": rb, "h": h, "n": n, "c": c, "o": o, "e": e}


def flujo(pts, c=FLUJO):
    return {"k": "flow", "pts": pts, "c": c}


# ------------------------------- escenas (medidas en m) -------------------------------
def _sedimentador():
    B = 1.5
    it = [caja([0.8, 0, 0.75], [3, B, 2.2], AZUL, 0.22, 1), caja([0, 0, 1.25], [0.8, B, 1.7], AZUL, 0.22, 1),
          caja([0.8, 0, 0.76], [3, B, 1.89], AGUA, 0.18), caja([0, 0, 1.26], [0.8, B, 1.39], AGUA, 0.18),
          {"k": "hex", "p": [0.8, 0, 1.51], "s": [3, B, 0.55], "c": "#58a6ff"},
          cil([0.8, 0.75, 2.65], 0.045, 3, "x"), cil([0.8, 0.75, 1.30], 0.045, 3, "x"),
          cil([-0.3, 0.75, 2.65], 0.08, 0.3, "x", GRIS), cil([-0.3, 0.75, 2.65], 0.14, 0.03, "x", GRIS)]
    for xi in (0.8, 2.3):
        it += [tc([xi + 0.75, 0.75, 0.75], 1.5 / R2, 0.2 / R2, 0.75, 4), cil([xi + 0.75, 0.75, -0.1], 0.045, 0.1)]
    it += [caja([x - 0.05, y - 0.05, 0], [0.1, 0.1, 0.8], GRIS) for x in (0.85, 3.7) for y in (0.05, B - 0.05)]
    it += [flujo([[-0.4, .75, 2.65], [0.4, .75, 2.65], [0.4, .75, 1.30], [1.2, .75, 1.30]]),
           flujo([[1.4, .4, 1.35], [1.4, .4, 2.6]]), flujo([[2.3, .4, 1.35], [2.3, .4, 2.6]]), flujo([[3.2, .4, 1.35], [3.2, .4, 2.6]]),
           flujo([[3.0, .75, 2.65], [4.3, .75, 2.65]]),
           flujo([[1.55, .75, 0.7], [1.55, .75, 0.1]], LODO), flujo([[3.05, .75, 0.7], [3.05, .75, 0.1]], LODO)]
    return it


def _coagulacion():
    R = 0.75
    it = [cil([0, 0, 1.5], R, 1.5, "z", AZUL, 0.22, 1), tc([0, 0, 1.5], R, 0.08, 0.5, 32, AZUL, 0.5),
          cil([0, 0, 1.5], R - 0.01, 1.2, "z", AGUA, 0.18), tc([0, 0, 1.5], R - 0.01, 0.08, 0.5, 32, AGUA, 0.18, 0),
          cil([0, 0, 1.1], 0.025, 2.2), cil([0, 0, 1.2], 0.3, 0.02), cil([0, 0, 2.1], 0.3, 0.02),
          caja([-0.15, -0.1, 3.0], [0.3, 0.2, 0.25], GRIS),
          cil([-1.0, 0, 2.85], 0.03, 0.25, "x", GRIS), cil([R, 0, 2.7], 0.045, 0.25, "x", GRIS)]
    it += [caja([0.65 * math.cos(a) - 0.04, 0.65 * math.sin(a) - 0.04, 0], [0.08, 0.08, 1.5], GRIS)
           for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
    return it + [flujo([[-1.6, 0, 2.85], [-0.5, 0, 2.85]]), flujo([[0.6, 0, 2.7], [1.7, 0, 2.7]])]


def _homogenizacion():  # enterrado: la boca queda a nivel del piso (z = 0)
    L, B, H = 5.1, 2.4, HOMO_H
    it = [caja([0, 0, -H], [L, B, H], "#58a6ff", 0.18, 1), caja([0.01, 0.01, -H + 0.01], [L - 0.02, B - 0.02, H - HOMO_FRANCO - 0.01], AGUA, 0.2),
          caja([-1.5, -1.5, -0.1], [L + 3, 1.5, 0.1], GRIS), caja([-1.5, B, -0.1], [L + 3, 1.5, 0.1], GRIS),
          caja([-1.5, 0, -0.1], [1.5, B, 0.1], GRIS), caja([L, 0, -0.1], [1.5, B, 0.1], GRIS),
          cil([L - 0.5, B / 2, -H + 0.3], 0.04, H + 1.5), cil([L - 0.5, B / 2, 1.2], 0.04, 1.9, "x")]
    return it + [flujo([[0.3, 1.2, 1.4], [0.3, 1.2, -0.6]]), flujo([[L - 0.5, B / 2, -H + 0.5], [L - 0.5, B / 2, 1.2], [L + 1.5, B / 2, 1.2]])]


def _oxidacion():
    it = [cil([0, 0, 0], 0.9, 2.4, "z", AZUL, 0.22, 1), cil([0, 0, 0.01], 0.89, 2.27, "z", AGUA, 0.18),
          cil([0, 0, 2.4], 0.4, 0.1, "z", GRIS), cil([-1.15, 0, 2.2], 0.03, 0.25, "x", GRIS), cil([0.9, 0, 0.3], 0.03, 0.25, "x", GRIS)]
    return it + [flujo([[-1.8, 0, 2.2], [-0.7, 0, 2.2]]), flujo([[0.7, 0, 0.3], [1.8, 0, 0.3]])]


def _filtros():
    it, fl = [], []
    for x, h, c in ((0.0, 1.81, AZUL), (0.9, 1.81, AZUL), (1.8, 1.97, GRIS)):
        it += [cil([x, 0, 0], 0.3, 1.5, "z", c, 0.3, 1), tc([x, 0, h - 0.05], 0.3, 0.12, h - 1.55, 24, c, 0.3),
               cil([x, 0, h - 0.05], 0.12, 0.05), cil([x, 0, h - 0.03], 0.18, 0.03, "z", GRIS),
               cil([x, 0, 0], 0.31, 0.25, "z", GRIS), caja([x + 0.3, -0.1, 0.35], [0.08, 0.2, 0.25], GRIS)]
        fl.append(flujo([[x, 0, h - 0.1], [x, 0, 0.35]]))
    return it + fl


AIRE_SUBE = True  # False si el ventilador sopla el aire hacia abajo (confirmar en planta)


def _torre():  # ~6 m de alto, 1.3 x 1.3 m (estimadas); el interior es ilustrativo
    a, hb = 1.3, 5.35
    it = [caja([0, 0, 0], [a, a, hb], AZUL, 0.3, 1), cil([0, a / 2, hb], a / 2, a, "x", AZUL, 0.3, 1),
          caja([0.15, -0.02, 0.4], [1.0, 0.02, 0.6], LODO), caja([-1.3, 0.4, 0], [0.4, 0.5, 0.3], GRIS),
          cil([-0.2, a / 2, 0], 0.04, 5.2), cil([-0.2, a / 2, 5.2], 0.04, 0.9, "x"),
          cil([a / 2, a / 2, 5.0], 0.5, 0.04, "z", GRIS, 0.6), caja([0.15, a / 2 - 0.02, 5.02], [1.0, 0.04, 0.02], ACERO),
          caja([a / 2 - 0.02, 0.15, 5.02], [0.04, 1.0, 0.02], ACERO)]
    it += [caja([0.1, 0.1, 1.4 + k * 0.3], [1.1, 1.1, 0.02], "#58a6ff", 0.5) for k in range(12)]
    it += [flujo([[-2.0, .65, .15], [-0.2, .65, .15], [-0.2, .65, 5.2], [0.65, .65, 5.2]]),
           flujo([[0.4, .65, 4.9], [0.4, .65, 1.0]]), flujo([[0.9, .65, 4.9], [0.9, .65, 1.0]])]
    if AIRE_SUBE:
        it += [flujo([[0.65, -0.9, .7], [0.65, .3, .7]], AIRE), flujo([[0.65, .65, 1.2], [0.65, .65, 6.6]], AIRE)]
    else:
        it += [flujo([[0.65, .65, 6.4], [0.65, .65, 1.2]], AIRE), flujo([[0.65, .3, .7], [0.65, -0.9, .7]], AIRE)]
    return it


ESCENAS = {"sedimentador": _sedimentador, "coagulacion": _coagulacion, "homogenizacion": _homogenizacion,
           "oxidacion": _oxidacion, "filtros": _filtros, "torre_enfriamiento": _torre}

HTML = """
<div id="c" style="width:100%;height:480px;position:relative;background:#0e1117;border-radius:8px;overflow:hidden">
  <div style="position:absolute;left:10px;top:8px;color:#8b949e;font:12px sans-serif;z-index:2">
    Arrastra para girar · pellizca o usa la rueda para acercar</div></div>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function () {
  const el = document.getElementById('c');
  if (typeof THREE === 'undefined') { el.innerHTML = '<p style="color:#8b949e;padding:20px">No se pudo cargar Three.js. Usa la vista Alambre.</p>'; return; }
  const S = __SPEC__, W = el.clientWidth, H = 480;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0e1117);
  const cam = new THREE.PerspectiveCamera(45, W / H, 0.1, 200);
  const ren = new THREE.WebGLRenderer({ antialias: true });
  ren.setSize(W, H); ren.setPixelRatio(Math.min(window.devicePixelRatio, 2)); el.appendChild(ren.domElement);
  const ctl = new THREE.OrbitControls(cam, ren.domElement); ctl.enableDamping = true;
  scene.add(new THREE.HemisphereLight(0xcfe3ff, 0x1a1f27, 0.9));
  const sun = new THREE.DirectionalLight(0xffffff, 0.9); sun.position.set(5, 8, 4); scene.add(sun);
  const grp = new THREE.Group(); scene.add(grp);
  const mat = (c, o) => new THREE.MeshStandardMaterial({ color: c, opacity: o, transparent: o < 1, metalness: 0.3, roughness: 0.5, side: THREE.DoubleSide, depthWrite: o >= 1 });
  const T = (x, y, z) => new THREE.Vector3(x, z, y);   // planta (x,y,z) -> Three (x,z,y)
  function put(g, m, it) {
    grp.add(m);
    if (it.e) { const e = new THREE.LineSegments(new THREE.EdgesGeometry(g), new THREE.LineBasicMaterial({ color: 0x58a6ff })); e.position.copy(m.position); e.rotation.copy(m.rotation); grp.add(e); }
  }
  const parts = [];
  S.forEach(function (it) {
    const c = it.c || '#1f6feb', o = it.o === undefined ? 1 : it.o;
    if (it.k === 'box') {
      const g = new THREE.BoxGeometry(it.s[0], it.s[2], it.s[1]), m = new THREE.Mesh(g, mat(c, o));
      m.position.copy(T(it.p[0] + it.s[0] / 2, it.p[1] + it.s[1] / 2, it.p[2] + it.s[2] / 2)); put(g, m, it);
    } else if (it.k === 'cyl') {
      const g = new THREE.CylinderGeometry(it.r, it.r, it.h, 24), m = new THREE.Mesh(g, mat(c, o));
      if (it.ax === 'x') { m.rotation.z = Math.PI / 2; m.position.copy(T(it.p[0] + it.h / 2, it.p[1], it.p[2])); }
      else { m.position.copy(T(it.p[0], it.p[1], it.p[2] + it.h / 2)); }
      put(g, m, it);
    } else if (it.k === 'tc') {
      const g = new THREE.CylinderGeometry(it.rt, it.rb, it.h, it.n, 1, false); if (it.n === 4) g.rotateY(Math.PI / 4);
      const m = new THREE.Mesh(g, mat(c, o)); m.position.copy(T(it.p[0], it.p[1], it.p[2] - it.h / 2)); put(g, m, it);
    } else if (it.k === 'hex') {
      const s = 0.07, dx = 1.5 * s, dy = Math.sqrt(3) * s, pos = []; let i = 0;
      for (let cx = it.p[0] + s; cx <= it.p[0] + it.s[0] - s; cx += dx, i++)
        for (let cy = it.p[1] + s + (i % 2 ? dy / 2 : 0); cy <= it.p[1] + it.s[1] - s; cy += dy) pos.push([cx, cy]);
      const hg = new THREE.CylinderGeometry(s * 0.93, s * 0.93, it.s[2], 6); hg.rotateY(Math.PI / 6);
      const im = new THREE.InstancedMesh(hg, mat(c, 1), pos.length), d = new THREE.Object3D();
      pos.forEach(function (p, k) { d.position.copy(T(p[0], p[1], it.p[2] + it.s[2] / 2)); d.updateMatrix(); im.setMatrixAt(k, d.matrix); });
      grp.add(im);
    } else if (it.k === 'flow') {
      const pts = it.pts.map(function (p) { return T(p[0], p[1], p[2]); }), path = new THREE.CurvePath();
      for (let i = 0; i < pts.length - 1; i++) path.add(new THREE.LineCurve3(pts[i], pts[i + 1]));
      const col = new THREE.Color(it.c);
      grp.add(new THREE.Mesh(new THREE.TubeGeometry(path, Math.max(8, pts.length * 16), 0.02, 6, false), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.55 })));
      const b = pts[pts.length - 1], dir = b.clone().sub(pts[pts.length - 2]).normalize();
      const cone = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.22, 14), new THREE.MeshBasicMaterial({ color: col }));
      cone.position.copy(b.clone().sub(dir.clone().multiplyScalar(0.11))); cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir); grp.add(cone);
      for (let k = 0; k < 3; k++) {
        const sp = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 10), new THREE.MeshBasicMaterial({ color: 0xffffff }));
        scene.add(sp); parts.push({ s: sp, path: path, o: k / 3 });
      }
    }
  });
  const box = new THREE.Box3().setFromObject(grp), ctr = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
  const dist = Math.max(size.x, size.y, size.z) * 1.7 + 1;
  ctl.target.copy(ctr); cam.position.set(ctr.x + dist * 0.8, ctr.y + dist * 0.45, ctr.z + dist * 0.9); ctl.update();
  const grid = new THREE.GridHelper(Math.max(size.x, size.z) * 2.2 + 4, 24, 0x30363d, 0x21262d);
  grid.position.set(ctr.x, box.min.y - 0.02, ctr.z); scene.add(grid);
  window.addEventListener('resize', function () { const w = el.clientWidth; ren.setSize(w, H); cam.aspect = w / H; cam.updateProjectionMatrix(); });
  (function loop() {
    requestAnimationFrame(loop); const t = performance.now() / 1000;
    parts.forEach(function (p) { p.s.position.copy(p.path.getPointAt((t * 0.18 + p.o) % 1)); });
    ctl.update(); ren.render(scene, cam);
  })();
})();
</script>
"""


def visor(clave):
    html = HTML.replace("__SPEC__", json.dumps(ESCENAS[clave]()))
    if hasattr(st, "iframe"):  # Streamlit reciente
        st.iframe(html, height=500)
    else:  # versiones anteriores
        import streamlit.components.v1 as components
        components.html(html, height=500)
