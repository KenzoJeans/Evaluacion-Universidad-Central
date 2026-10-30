import streamlit as st

HTML = """
<div id="c" style="width:100%;height:480px;position:relative;background:#0e1117;border-radius:8px;overflow:hidden">
  <div style="position:absolute;left:10px;top:8px;color:#8b949e;font:12px sans-serif;z-index:2">
    Arrastra para girar · rueda o pellizco para acercar · agua en verde · panal en azul claro</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function () {
  const el = document.getElementById('c');
  if (typeof THREE === 'undefined') { el.innerHTML = '<p style="color:#8b949e;padding:20px">No se pudo cargar Three.js (revisa la conexión).</p>'; return; }
  const W = el.clientWidth, H = 480;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0e1117);
  const cam = new THREE.PerspectiveCamera(45, W / H, 0.1, 100); cam.position.set(6.2, 3.6, 6.4);
  const ren = new THREE.WebGLRenderer({ antialias: true });
  ren.setSize(W, H); ren.setPixelRatio(Math.min(window.devicePixelRatio, 2)); el.appendChild(ren.domElement);
  const ctl = new THREE.OrbitControls(cam, ren.domElement);
  ctl.target.set(1.9, 1.1, 0.75); ctl.enableDamping = true; ctl.update();
  scene.add(new THREE.HemisphereLight(0xcfe3ff, 0x1a1f27, 0.9));
  const sun = new THREE.DirectionalLight(0xffffff, 0.9); sun.position.set(5, 8, 4); scene.add(sun);
  const grid = new THREE.GridHelper(10, 20, 0x30363d, 0x21262d); grid.position.set(1.9, -0.12, 0.75); scene.add(grid);

  // Coordenadas de la planta (x largo, y ancho, z alto) -> Three (x, z, y)
  const mat = (c, o, m, r) => new THREE.MeshStandardMaterial({ color: c, opacity: o, transparent: o < 1, metalness: m, roughness: r, side: THREE.DoubleSide, depthWrite: o >= 1 });
  function box(x0, y0, z0, L, B, Hh, mt, edge) {
    const g = new THREE.BoxGeometry(L, Hh, B), m = new THREE.Mesh(g, mt);
    m.position.set(x0 + L / 2, z0 + Hh / 2, y0 + B / 2); scene.add(m);
    if (edge) { const e = new THREE.LineSegments(new THREE.EdgesGeometry(g), new THREE.LineBasicMaterial({ color: 0x58a6ff })); e.position.copy(m.position); scene.add(e); }
  }
  function cyl(cx, cy, cz, len, rad, axis, mt) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(rad, rad, len, 20), mt);
    if (axis === 'x') { m.rotation.z = Math.PI / 2; m.position.set(cx + len / 2, cz, cy); } else { m.position.set(cx, cz + len / 2, cy); }
    scene.add(m);
  }

  const B = 1.5, x0 = 0.8, zt = 2.95, zb = 0.75;
  const wall = mat(0x1f6feb, 0.22, 0.2, 0.6), blue = mat(0x1f6feb, 0.96, 0.3, 0.5);
  const steel = mat(0xc9d1d9, 1, 0.8, 0.3), dark = mat(0x6e7681, 1, 0.5, 0.5);

  box(x0, 0, zb, 3.0, B, zt - zb, wall, true);              // zona de sedimentación
  box(0, 0, zt - 1.7, 0.8, B, 1.7, wall, true);              // compartimiento de entrada
  box(x0, 0, zb + 0.01, 3.0, B, 2.65 - zb - 0.01, mat(0x3fb950, 0.18, 0, 1));   // agua
  box(0, 0, zt - 1.7 + 0.01, 0.8, B, 2.65 - (zt - 1.7) - 0.01, mat(0x3fb950, 0.18, 0, 1));

  [0.8, 2.3].forEach(function (xi) {                        // tolvas piramidales
    const g = new THREE.CylinderGeometry(1.5 / Math.SQRT2, 0.2 / Math.SQRT2, zb, 4, 1, false); g.rotateY(Math.PI / 4);
    const m = new THREE.Mesh(g, blue); m.position.set(xi + 0.75, zb / 2, B / 2); scene.add(m);
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(g), new THREE.LineBasicMaterial({ color: 0x58a6ff })); e.position.copy(m.position); scene.add(e);
    cyl(xi + 0.75, B / 2, -0.1, 0.1, 0.045, 'z', steel);     // salida de lodos
  });

  // Panal: prismas hexagonales instanciados
  const s = 0.07, dx = 1.5 * s, dy = Math.sqrt(3) * s, pos = []; let i = 0;
  for (let cx = x0 + s; cx <= x0 + 3.0 - s; cx += dx, i++) {
    for (let cy = s + (i % 2 ? dy / 2 : 0); cy <= B - s; cy += dy) pos.push([cx, cy]);
  }
  const hg = new THREE.CylinderGeometry(s * 0.93, s * 0.93, 0.55, 6); hg.rotateY(Math.PI / 6);
  const im = new THREE.InstancedMesh(hg, mat(0x58a6ff, 1, 0.2, 0.6), pos.length), d = new THREE.Object3D();
  pos.forEach(function (p, k) { d.position.set(p[0], 1.51 + 0.275, p[1]); d.updateMatrix(); im.setMatrixAt(k, d.matrix); });
  scene.add(im);

  [0.85, 3.7].forEach(function (x) { [0.05, B - 0.05].forEach(function (y) { box(x - 0.05, y - 0.05, 0, 0.1, 0.1, 0.8, dark); }); });  // patas
  cyl(x0, B / 2, 2.65, 3.0, 0.045, 'x', steel);              // tubería de recolección
  cyl(x0, B / 2, 1.30, 3.0, 0.045, 'x', steel);              // tubería de distribución
  cyl(-0.3, B / 2, 2.65, 0.3, 0.08, 'x', dark);              // entrada
  cyl(-0.3, B / 2, 2.65, 0.03, 0.14, 'x', dark);             // brida

  window.addEventListener('resize', function () {
    const w = el.clientWidth; ren.setSize(w, H); cam.aspect = w / H; cam.updateProjectionMatrix();
  });
  (function loop() { requestAnimationFrame(loop); ctl.update(); ren.render(scene, cam); })();
})();
</script>
"""


def visor_sedimentador():
    if hasattr(st, "iframe"):  # Streamlit reciente
        st.iframe(HTML, height=500)
    else:  # versiones anteriores
        import streamlit.components.v1 as components
        components.html(HTML, height=500)
