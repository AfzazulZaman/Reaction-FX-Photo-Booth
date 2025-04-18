from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Reaction FX Photo Booth</title>
    <style>
        body {
            margin: 0;
            background-color: black;
            overflow: hidden;
        }

        #videoElement {
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            z-index: 1;
        }

        #overlayCanvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 2;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <video id="videoElement" autoplay muted playsinline></video>
    <canvas id="overlayCanvas"></canvas>

    <!-- Load face-api.js from CDN -->
    <script defer src="https://cdn.jsdelivr.net/npm/face-api.js"></script>

    <script>
        const video = document.getElementById('videoElement');
        const canvas = document.getElementById('overlayCanvas');
        const ctx = canvas.getContext('2d');
        let detections = null;
        let particles = [];

        // Resize canvas to match video
        function resizeCanvas() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        }

        // Particle constructor
        function Particle(x, y, type) {
            this.x = x;
            this.y = y;
            this.radius = Math.random() * 5 + 2;
            this.color = type === 'sparkle' ? 'yellow' : 'hsl(' + Math.random() * 360 + ', 100%, 50%)';
            this.velocityX = (Math.random() - 0.5) * 4;
            this.velocityY = (Math.random() - 0.5) * 4;
            this.life = 60;
        }

        // Update particles
        function updateParticles() {
            particles = particles.filter(p => p.life > 0);
            particles.forEach(p => {
                p.x += p.velocityX;
                p.y += p.velocityY;
                p.life--;
            });
        }

        // Render particles
        function drawParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
            });
        }

        // Trigger particle effects
        function triggerEffect(type, x, y) {
            for (let i = 0; i < 20; i++) {
                particles.push(new Particle(x, y, type));
            }
        }

        // Load face-api models
        async function loadModels() {
            const MODEL_URL = 'https://cdn.jsdelivr.net/npm/face-api.js/models';
            await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
            await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);
            await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
        }

        // Start video
        async function startVideo() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    resizeCanvas();
                    runDetection();
                };
            } catch (err) {
                alert("Webcam access denied.");
                console.error(err);
            }
        }

        // Facial expression detection loop
        async function runDetection() {
            const displaySize = { width: video.videoWidth, height: video.videoHeight };
            faceapi.matchDimensions(canvas, displaySize);

            setInterval(async () => {
                const result = await faceapi.detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
                                             .withFaceLandmarks()
                                             .withFaceExpressions();

                if (result) {
                    const resized = faceapi.resizeResults(result, displaySize);
                    const expressions = resized.expressions;
                    const landmarks = resized.landmarks;

                    if (expressions.happy > 0.7) {
                        const mouth = landmarks.getMouth();
                        const centerX = (mouth[3].x + mouth[9].x) / 2;
                        const centerY = (mouth[3].y + mouth[9].y) / 2;
                        triggerEffect('sparkle', centerX, centerY);
                    }

                    const leftEyeOpen = landmarks.getLeftEye()[1].y - landmarks.getLeftEye()[5].y;
                    const rightEyeOpen = landmarks.getRightEye()[1].y - landmarks.getRightEye()[5].y;
                    const winkThreshold = 3;

                    if (Math.abs(leftEyeOpen) < winkThreshold && Math.abs(rightEyeOpen) > winkThreshold) {
                        const eye = landmarks.getLeftEye();
                        const x = (eye[0].x + eye[3].x) / 2;
                        const y = (eye[1].y + eye[5].y) / 2;
                        triggerEffect('confetti', x, y);
                    } else if (Math.abs(rightEyeOpen) < winkThreshold && Math.abs(leftEyeOpen) > winkThreshold) {
                        const eye = landmarks.getRightEye();
                        const x = (eye[0].x + eye[3].x) / 2;
                        const y = (eye[1].y + eye[5].y) / 2;
                        triggerEffect('confetti', x, y);
                    }
                }
            }, 300);
        }

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            updateParticles();
            drawParticles();
        }

        // Start app
        loadModels().then(() => {
            startVideo();
            animate();
        });
    </script>
</body>
</html>
""")


# App setup and run
if __name__ == "__main__":
    app.run(debug=True, port=5000)
