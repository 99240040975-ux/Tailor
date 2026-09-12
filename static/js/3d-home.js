/* =========================================================
   TAILORCONNECT 3D HOME EXPERIENCE
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const canvas =
        document.getElementById("tailorCanvas");

    const hero =
        document.getElementById("hero3D");

    const enterButton =
        document.getElementById("enterTailorButton");


    /*
     * ================================================
     * LOGIN TRANSITION
     * ================================================
     */

    if (enterButton) {

        enterButton.addEventListener("click", () => {

            enterButton.disabled = true;

            if (hero) {
                hero.classList.add("login-transition");
            }

            document.body.classList.add(
                "page-transition"
            );

            setTimeout(() => {

                window.location.href = "/login";

            }, 850);

        });

    }


    /*
     * ================================================
     * THREE.JS CHECK
     * ================================================
     */

    if (!canvas || typeof THREE === "undefined") {

        console.warn(
            "Three.js unavailable. CSS animation fallback enabled."
        );

        return;
    }


    /*
     * ================================================
     * REDUCED MOTION CHECK
     * ================================================
     */

    const reducedMotion =
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;


    /*
     * ================================================
     * SCENE
     * ================================================
     */

    const scene =
        new THREE.Scene();


    /*
     * ================================================
     * CAMERA
     * ================================================
     */

    const camera =
        new THREE.PerspectiveCamera(
            55,
            window.innerWidth /
            window.innerHeight,
            0.1,
            1000
        );

    camera.position.z = 7;


    /*
     * ================================================
     * RENDERER
     * ================================================
     */

    const renderer =
        new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: true
        });

    renderer.setPixelRatio(
        Math.min(
            window.devicePixelRatio,
            2
        )
    );

    renderer.setSize(
        window.innerWidth,
        window.innerHeight
    );


    /*
     * ================================================
     * LIGHTING
     * ================================================
     */

    const ambientLight =
        new THREE.AmbientLight(
            0xffffff,
            1.2
        );

    scene.add(
        ambientLight
    );


    const pinkLight =
        new THREE.PointLight(
            0xff3cac,
            4,
            12
        );

    pinkLight.position.set(
        -3,
        2,
        4
    );

    scene.add(
        pinkLight
    );


    const cyanLight =
        new THREE.PointLight(
            0x20d9d2,
            3,
            12
        );

    cyanLight.position.set(
        3,
        -1,
        3
    );

    scene.add(
        cyanLight
    );


    /*
     * ================================================
     * CENTRAL FASHION OBJECT
     * ================================================
     */

    const garmentGroup =
        new THREE.Group();


    /*
     * Garment body
     */

    const bodyGeometry =
        new THREE.SphereGeometry(
            1.25,
            32,
            32
        );

    const bodyMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x7b3fa0,
            roughness: 0.35,
            metalness: 0.1
        });

    const body =
        new THREE.Mesh(
            bodyGeometry,
            bodyMaterial
        );

    body.scale.set(
        0.9,
        1.35,
        0.55
    );

    body.position.y =
        -0.15;

    garmentGroup.add(
        body
    );


    /*
     * Shoulder pieces
     */

    const shoulderGeometry =
        new THREE.SphereGeometry(
            0.65,
            24,
            24
        );

    const shoulderMaterial =
        new THREE.MeshStandardMaterial({
            color: 0xff3cac,
            roughness: 0.3
        });


    const leftShoulder =
        new THREE.Mesh(
            shoulderGeometry,
            shoulderMaterial
        );

    leftShoulder.scale.set(
        1.25,
        0.65,
        0.65
    );

    leftShoulder.position.set(
        -1.0,
        0.65,
        0
    );

    garmentGroup.add(
        leftShoulder
    );


    const rightShoulder =
        new THREE.Mesh(
            shoulderGeometry,
            shoulderMaterial
        );

    rightShoulder.scale.set(
        1.25,
        0.65,
        0.65
    );

    rightShoulder.position.set(
        1.0,
        0.65,
        0
    );

    garmentGroup.add(
        rightShoulder
    );


    /*
     * Collar
     */

    const collarGeometry =
        new THREE.TorusGeometry(
            0.42,
            0.10,
            16,
            40,
            Math.PI
        );

    const collarMaterial =
        new THREE.MeshStandardMaterial({
            color: 0xffc6e5,
            roughness: 0.3
        });

    const collar =
        new THREE.Mesh(
            collarGeometry,
            collarMaterial
        );

    collar.rotation.x =
        Math.PI / 2;

    collar.position.y =
        0.95;

    garmentGroup.add(
        collar
    );


    /*
     * Buttons
     */

    const buttonGeometry =
        new THREE.SphereGeometry(
            0.075,
            16,
            16
        );

    const buttonMaterial =
        new THREE.MeshStandardMaterial({
            color: 0xffffff,
            emissive: 0xff3cac,
            emissiveIntensity: 0.3
        });


    for (let i = 0; i < 4; i++) {

        const button =
            new THREE.Mesh(
                buttonGeometry,
                buttonMaterial
            );

        button.position.set(
            0,
            0.55 - i * 0.38,
            0.57
        );

        garmentGroup.add(
            button
        );
    }


    garmentGroup.position.x =
        1.0;

    garmentGroup.position.y =
        0.1;

    garmentGroup.rotation.y =
        -0.2;

    scene.add(
        garmentGroup
    );


    /*
     * ================================================
     * FLOATING THREAD
     * ================================================
     */

    const threadPoints = [];

    for (
        let i = 0;
        i < 80;
        i++
    ) {

        const t =
            i / 79;

        const x =
            -3.3 + t * 6;

        const y =
            Math.sin(
                t * Math.PI * 3
            ) * 0.65;

        const z =
            Math.cos(
                t * Math.PI * 2
            ) * 0.3;

        threadPoints.push(
            new THREE.Vector3(
                x,
                y,
                z
            )
        );
    }


    const threadGeometry =
        new THREE.BufferGeometry()
            .setFromPoints(
                threadPoints
            );


    const threadMaterial =
        new THREE.LineBasicMaterial({
            color: 0xff8ac7,
            transparent: true,
            opacity: 0.6
        });


    const thread =
        new THREE.Line(
            threadGeometry,
            threadMaterial
        );

    thread.position.y =
        1.4;

    scene.add(
        thread
    );


    /*
     * ================================================
     * FLOATING PARTICLES
     * ================================================
     */

    const particleCount =
        500;

    const particlePositions =
        new Float32Array(
            particleCount * 3
        );


    for (
        let i = 0;
        i < particleCount;
        i++
    ) {

        particlePositions[i * 3] =
            (Math.random() - 0.5) * 12;

        particlePositions[
            i * 3 + 1
        ] =
            (Math.random() - 0.5) * 8;

        particlePositions[
            i * 3 + 2
        ] =
            (Math.random() - 0.5) * 6;
    }


    const particleGeometry =
        new THREE.BufferGeometry();

    particleGeometry.setAttribute(
        "position",
        new THREE.BufferAttribute(
            particlePositions,
            3
        )
    );


    const particleMaterial =
        new THREE.PointsMaterial({
            color: 0xffb4dc,
            size: 0.025,
            transparent: true,
            opacity: 0.7
        });


    const particles =
        new THREE.Points(
            particleGeometry,
            particleMaterial
        );

    scene.add(
        particles
    );


    /*
     * ================================================
     * MOUSE INTERACTION
     * ================================================
     */

    let mouseX = 0;
    let mouseY = 0;

    let targetX = 0;
    let targetY = 0;


    window.addEventListener(
        "mousemove",
        (event) => {

            mouseX =
                (event.clientX /
                    window.innerWidth) *
                2 -
                1;

            mouseY =
                (event.clientY /
                    window.innerHeight) *
                2 -
                1;

        }
    );


    /*
     * ================================================
     * ANIMATION
     * ================================================
     */

    const clock =
        new THREE.Clock();


    function animate() {

        requestAnimationFrame(
            animate
        );


        const elapsed =
            clock.getElapsedTime();


        /*
         * Garment rotation
         */

        if (!reducedMotion) {

            garmentGroup.rotation.y =
                -0.2 +
                Math.sin(
                    elapsed * 0.7
                ) * 0.15;

            garmentGroup.position.y =
                0.1 +
                Math.sin(
                    elapsed * 1.1
                ) * 0.08;


            /*
             * Thread movement
             */

            thread.rotation.z =
                Math.sin(
                    elapsed * 0.35
                ) * 0.08;


            /*
             * Particles
             */

            particles.rotation.y =
                elapsed * 0.015;

            particles.rotation.x =
                Math.sin(
                    elapsed * 0.1
                ) * 0.05;
        }


        /*
         * Smooth mouse movement
         */

        targetX +=
            (mouseX * 0.18 - targetX)
            * 0.04;

        targetY +=
            (mouseY * 0.10 - targetY)
            * 0.04;


        camera.position.x =
            targetX;

        camera.position.y =
            -targetY;


        camera.lookAt(
            0.5,
            0,
            0
        );


        renderer.render(
            scene,
            camera
        );

    }


    animate();


    /*
     * ================================================
     * RESPONSIVE RESIZE
     * ================================================
     */

    window.addEventListener(
        "resize",
        () => {

            camera.aspect =
                window.innerWidth /
                window.innerHeight;

            camera.updateProjectionMatrix();

            renderer.setSize(
                window.innerWidth,
                window.innerHeight
            );

        }
    );

});