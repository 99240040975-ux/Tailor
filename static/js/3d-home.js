/* =========================================================
   TAILORCONNECT — 3D HOME EXPERIENCE  (light theme)
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* ── Login transition ───────────────────────────────── */

    const enterBtn = document.getElementById("enterTailorButton");
    const hero3D   = document.getElementById("hero3D");

    if (enterBtn) {
        enterBtn.addEventListener("click", () => {
            enterBtn.disabled = true;
            if (hero3D) hero3D.classList.add("login-transition");
            document.body.style.overflow = "hidden";
            setTimeout(() => { window.location.href = "/auth/register"; }, 850);
        });
    }

    /* ── Three.js guard ─────────────────────────────────── */

    const canvas = document.getElementById("tailorCanvas");
    if (!canvas || typeof THREE === "undefined") {
        console.warn("Three.js not available — CSS animation fallback active.");
        return;
    }

    const reducedMotion =
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ── Scene ──────────────────────────────────────────── */

    const scene  = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
        52,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.z = 7;

    const renderer = new THREE.WebGLRenderer({
        canvas,
        alpha: true,
        antialias: true
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0);   // transparent — shows CSS bg

    /* ── Lighting (soft, matches light bg) ─────────────── */

    scene.add(new THREE.AmbientLight(0xffffff, 1.6));

    const pinkLight = new THREE.PointLight(0xf472b6, 3.5, 14);
    pinkLight.position.set(-3, 2.5, 4);
    scene.add(pinkLight);

    const indigoLight = new THREE.PointLight(0x818cf8, 3.0, 14);
    indigoLight.position.set(3.5, -1, 3);
    scene.add(indigoLight);

    const mintLight = new THREE.PointLight(0x34d399, 2.0, 10);
    mintLight.position.set(0, 4, 2);
    scene.add(mintLight);

    /* ── Central garment group ──────────────────────────── */

    const garmentGroup = new THREE.Group();

    // Body
    const body = new THREE.Mesh(
        new THREE.SphereGeometry(1.2, 48, 48),
        new THREE.MeshStandardMaterial({
            color: 0xc7d2fe,
            roughness: 0.25,
            metalness: 0.08
        })
    );
    body.scale.set(0.88, 1.38, 0.52);
    body.position.y = -0.12;
    garmentGroup.add(body);

    // Left shoulder
    const shoulderMat = new THREE.MeshStandardMaterial({
        color: 0xf0abfc,
        roughness: 0.22
    });
    const lShoulder = new THREE.Mesh(
        new THREE.SphereGeometry(0.62, 28, 28),
        shoulderMat
    );
    lShoulder.scale.set(1.28, 0.62, 0.62);
    lShoulder.position.set(-0.98, 0.68, 0);
    garmentGroup.add(lShoulder);

    // Right shoulder
    const rShoulder = lShoulder.clone();
    rShoulder.position.set(0.98, 0.68, 0);
    garmentGroup.add(rShoulder);

    // Collar
    const collar = new THREE.Mesh(
        new THREE.TorusGeometry(0.40, 0.095, 16, 48, Math.PI),
        new THREE.MeshStandardMaterial({ color: 0xe0e7ff, roughness: 0.28 })
    );
    collar.rotation.x = Math.PI / 2;
    collar.position.y = 0.92;
    garmentGroup.add(collar);

    // Buttons
    const btnMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: 0x818cf8,
        emissiveIntensity: 0.4
    });
    for (let i = 0; i < 4; i++) {
        const btn = new THREE.Mesh(
            new THREE.SphereGeometry(0.07, 16, 16),
            btnMat
        );
        btn.position.set(0, 0.52 - i * 0.36, 0.55);
        garmentGroup.add(btn);
    }

    // Seam lines using EdgesGeometry illusion via a thin box
    const seamMat = new THREE.MeshStandardMaterial({
        color: 0xa5b4fc,
        roughness: 0.5,
        transparent: true,
        opacity: 0.6
    });
    for (const xPos of [-0.28, 0.28]) {
        const seam = new THREE.Mesh(
            new THREE.BoxGeometry(0.015, 1.8, 0.015),
            seamMat
        );
        seam.position.set(xPos, 0, 0.56);
        garmentGroup.add(seam);
    }

    garmentGroup.position.set(1.1, 0.1, 0);
    garmentGroup.rotation.y = -0.22;
    scene.add(garmentGroup);

    /* ── Needle ─────────────────────────────────────────── */

    const needleGroup = new THREE.Group();

    const needleShaft = new THREE.Mesh(
        new THREE.CylinderGeometry(0.012, 0.018, 2.2, 12),
        new THREE.MeshStandardMaterial({
            color: 0xe0e7ff,
            metalness: 0.6,
            roughness: 0.2
        })
    );
    needleShaft.rotation.z = Math.PI / 2;
    needleGroup.add(needleShaft);

    const needleTip = new THREE.Mesh(
        new THREE.ConeGeometry(0.018, 0.22, 12),
        new THREE.MeshStandardMaterial({ color: 0xa5b4fc, metalness: 0.7 })
    );
    needleTip.rotation.z = -Math.PI / 2;
    needleTip.position.x = -1.2;
    needleGroup.add(needleTip);

    needleGroup.position.set(-1.5, 1.6, 0.8);
    needleGroup.rotation.z = -0.4;
    scene.add(needleGroup);

    /* ── Floating thread curve ──────────────────────────── */

    const threadPts = [];
    for (let i = 0; i < 90; i++) {
        const t = i / 89;
        threadPts.push(new THREE.Vector3(
            -3.5 + t * 7,
            Math.sin(t * Math.PI * 3.5) * 0.7,
            Math.cos(t * Math.PI * 2.2) * 0.35
        ));
    }
    const thread = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(threadPts),
        new THREE.LineBasicMaterial({
            color: 0xf0abfc,
            transparent: true,
            opacity: 0.55
        })
    );
    thread.position.y = 1.5;
    scene.add(thread);

    /* ── Secondary thread (mint) ─────────────────────────── */

    const thread2Pts = [];
    for (let i = 0; i < 70; i++) {
        const t = i / 69;
        thread2Pts.push(new THREE.Vector3(
            -2.8 + t * 5.5,
            Math.cos(t * Math.PI * 4) * 0.5,
            Math.sin(t * Math.PI * 2) * 0.25
        ));
    }
    const thread2 = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(thread2Pts),
        new THREE.LineBasicMaterial({
            color: 0x34d399,
            transparent: true,
            opacity: 0.45
        })
    );
    thread2.position.y = -1.8;
    scene.add(thread2);

    /* ── Particles ──────────────────────────────────────── */

    const PARTICLE_COUNT = 750;
    const pos = new Float32Array(PARTICLE_COUNT * 3);
    const colors = new Float32Array(PARTICLE_COUNT * 3);

    // Colour palette matching light theme
    const palette = [
        new THREE.Color(0xf472b6),  // pink
        new THREE.Color(0x818cf8),  // indigo
        new THREE.Color(0x34d399),  // mint
        new THREE.Color(0xfb923c),  // peach
        new THREE.Color(0x38bdf8),  // sky
        new THREE.Color(0xfcd34d),  // amber
    ];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        pos[i * 3]     = (Math.random() - 0.5) * 14;
        pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
        pos[i * 3 + 2] = (Math.random() - 0.5) * 8;

        const c = palette[Math.floor(Math.random() * palette.length)];
        colors[i * 3]     = c.r;
        colors[i * 3 + 1] = c.g;
        colors[i * 3 + 2] = c.b;
    }

    const partGeo = new THREE.BufferGeometry();
    partGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    partGeo.setAttribute("color",    new THREE.BufferAttribute(colors, 3));

    const particles = new THREE.Points(
        partGeo,
        new THREE.PointsMaterial({
            size: 0.032,
            vertexColors: true,
            transparent: true,
            opacity: 0.65,
            sizeAttenuation: true
        })
    );
    scene.add(particles);

    /* ── Sparkle dodecahedrons ──────────────────────────── */

    const sparkleGroup = new THREE.Group();
    const sparkleMats  = [0xf472b6, 0x818cf8, 0x34d399, 0xfb923c, 0x38bdf8].map(
        c => new THREE.MeshStandardMaterial({
            color: c,
            emissive: c,
            emissiveIntensity: 0.55,
            roughness: 0.3,
            transparent: true,
            opacity: 0.8
        })
    );

    for (let i = 0; i < 18; i++) {
        const geo  = new THREE.DodecahedronGeometry(0.08 + Math.random() * 0.12);
        const mat  = sparkleMats[i % sparkleMats.length];
        const mesh = new THREE.Mesh(geo, mat);

        mesh.position.set(
            (Math.random() - 0.5) * 9,
            (Math.random() - 0.5) * 7,
            (Math.random() - 0.5) * 4
        );

        mesh.userData.speed  = 0.6 + Math.random() * 1.2;
        mesh.userData.offset = Math.random() * Math.PI * 2;
        sparkleGroup.add(mesh);
    }
    scene.add(sparkleGroup);

    /* ── Floating torus rings ───────────────────────────── */

    const ringColors = [0xf472b6, 0x818cf8, 0x34d399];
    const torusRings = ringColors.map((color, i) => {
        const ring = new THREE.Mesh(
            new THREE.TorusGeometry(0.55 + i * 0.25, 0.025, 16, 80),
            new THREE.MeshStandardMaterial({
                color,
                emissive: color,
                emissiveIntensity: 0.3,
                transparent: true,
                opacity: 0.55
            })
        );
        ring.position.set(
            -2.5 + i * 2.5,
            1.2 - i * 0.6,
            -1 + i * 0.5
        );
        ring.rotation.x = Math.PI / 4 + i * 0.3;
        ring.userData.speed  = 0.4 + i * 0.2;
        ring.userData.offset = i * (Math.PI * 2 / 3);
        scene.add(ring);
        return ring;
    });

    /* ── Mouse interaction ──────────────────────────────── */

    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;

    window.addEventListener("mousemove", e => {
        mouseX = (e.clientX / window.innerWidth)  * 2 - 1;
        mouseY = (e.clientY / window.innerHeight) * 2 - 1;
    });

    /* ── Animation loop ─────────────────────────────────── */

    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const t = clock.getElapsedTime();

        if (!reducedMotion) {

            // Garment
            garmentGroup.rotation.y  = -0.22 + Math.sin(t * 0.65) * 0.16;
            garmentGroup.position.y  =  0.10 + Math.sin(t * 1.05) * 0.10;

            // Needle drift
            needleGroup.position.y   = 1.6  + Math.sin(t * 0.9) * 0.22;
            needleGroup.rotation.z   = -0.4 + Math.sin(t * 0.5) * 0.12;

            // Threads
            thread.rotation.z  = Math.sin(t * 0.32) * 0.09;
            thread2.rotation.z = Math.cos(t * 0.28) * 0.07;

            // Particles drift
            particles.rotation.y =  t * 0.012;
            particles.rotation.x =  Math.sin(t * 0.09) * 0.06;

            // Sparkles bob individually
            sparkleGroup.children.forEach(m => {
                m.position.y += Math.sin(t * m.userData.speed + m.userData.offset) * 0.005;
                m.rotation.x  = t * 0.7 * m.userData.speed;
                m.rotation.y  = t * 0.5 * m.userData.speed;
            });

            // Torus rings spin
            torusRings.forEach(ring => {
                ring.rotation.x += 0.006 * ring.userData.speed;
                ring.rotation.y += 0.004 * ring.userData.speed;
                ring.position.y += Math.sin(t * ring.userData.speed + ring.userData.offset) * 0.003;
            });

            // Pulsing lights
            pinkLight.intensity   = 3.5 + Math.sin(t * 1.4) * 0.8;
            indigoLight.intensity = 3.0 + Math.cos(t * 1.1) * 0.7;
        }

        // Smooth camera follow mouse
        targetX += (mouseX * 0.16 - targetX) * 0.035;
        targetY += (mouseY * 0.09 - targetY) * 0.035;
        camera.position.x = targetX;
        camera.position.y = -targetY;
        camera.lookAt(0.5, 0, 0);

        renderer.render(scene, camera);
    }

    animate();

    /* ── Resize ─────────────────────────────────────────── */

    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

});
