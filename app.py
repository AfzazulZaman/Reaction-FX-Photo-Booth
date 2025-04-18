from flask import Flask, render_template_string
import random

app = Flask(__name__)

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Daydream Cloud Generator</title>
        <style>
            body {
                margin: 0;
                overflow: hidden;
                background: linear-gradient(to top, #aee1f9, #ffffff);
                font-family: 'Segoe UI', sans-serif;
            }
            canvas {
                display: block;
            }
            .prompt {
                position: absolute;
                background: rgba(255, 255, 255, 0.85);
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 16px;
                color: #333;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                pointer-events: none;
                transition: opacity 0.3s ease;
                opacity: 0;
            }
        </style>
    </head>
    <body>
        <canvas id="cloudCanvas"></canvas>
        <div id="promptBox" class="prompt"></div>

        <script>
            const canvas = document.getElementById("cloudCanvas");
            const ctx = canvas.getContext("2d");
            const promptBox = document.getElementById("promptBox");

            let clouds = [];
            let prompts = [
                "Invent a sandwich made of shadows",
                "Name a cloud that sings lullabies",
                "Describe a tea party between two invisible dragons",
                "What color is a whisper at sunset?",
                "Design a shoe for floating dreams",
                "What's the favorite song of a lightning bolt?",
                "Imagine a city made of jellybeans",
                "Build a telescope for looking into memories"
            ];

            // Resize canvas to fit window
            function resizeCanvas() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            window.addEventListener("resize", resizeCanvas);
            resizeCanvas();

            // Generate random clouds
            function createCloud() {
                const cloud = {
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height / 1.5,
                    size: 40 + Math.random() * 60,
                    speed: 0.2 + Math.random() * 0.4,
                    blobs: [],
                    id: Math.random().toString(36).substring(2)
                };
                const blobsCount = 3 + Math.floor(Math.random() * 5);
                for (let i = 0; i < blobsCount; i++) {
                    cloud.blobs.push({
                        x: (Math.random() - 0.5) * cloud.size,
                        y: (Math.random() - 0.5) * cloud.size,
                        r: cloud.size * (0.4 + Math.random() * 0.6),
                        opacity: 0.3 + Math.random() * 0.4
                    });
                }
                return cloud;
            }

            // Initial cloud generation
            for (let i = 0; i < 15; i++) {
                clouds.push(createCloud());
            }

            // Draw and animate clouds
            function drawCloud(cloud) {
                ctx.save();
                ctx.translate(cloud.x, cloud.y);
                cloud.blobs.forEach(blob => {
                    ctx.beginPath();
                    ctx.globalAlpha = blob.opacity;
                    ctx.fillStyle = "#fff";
                    ctx.arc(blob.x, blob.y, blob.r, 0, Math.PI * 2);
                    ctx.fill();
                });
                ctx.restore();
            }

            // Main animation loop
            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                clouds.forEach(cloud => {
                    cloud.x += cloud.speed;
                    if (cloud.x - cloud.size > canvas.width) {
                        cloud.x = -cloud.size;
                        cloud.y = Math.random() * canvas.height / 1.5;
                    }

                    // Morph blobs slightly
                    cloud.blobs.forEach(blob => {
                        blob.x += (Math.random() - 0.5) * 0.3;
                        blob.y += (Math.random() - 0.5) * 0.3;
                    });

                    drawCloud(cloud);
                });
                requestAnimationFrame(animate);
            }
            animate();

            // Check if click is on a cloud
            function isClickOnCloud(x, y, cloud) {
                return cloud.blobs.some(blob => {
                    const dx = x - (cloud.x + blob.x);
                    const dy = y - (cloud.y + blob.y);
                    return dx * dx + dy * dy < blob.r * blob.r;
                });
            }

            canvas.addEventListener("click", function(e) {
                const rect = canvas.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const clickY = e.clientY - rect.top;

                for (let cloud of clouds) {
                    if (isClickOnCloud(clickX, clickY, cloud)) {
                        const prompt = prompts[Math.floor(Math.random() * prompts.length)];
                        promptBox.innerText = prompt;
                        promptBox.style.left = (clickX + 10) + "px";
                        promptBox.style.top = (clickY + 10) + "px";
                        promptBox.style.opacity = 1;
                        setTimeout(() => {
                            promptBox.style.opacity = 0;
                        }, 4000);
                        break;
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
