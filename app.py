from flask import Flask, request, send_file, render_template_string, make_response
from PIL import Image, ImageDraw, ImageFont
import io
import os
import base64
import time
import random
import math
from datetime import datetime

app = Flask(__name__)

# Main template with embedded CSS and JavaScript
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProLogo Generator</title>
    <style>
        :root {
            --primary-color: #2D3142;
            --secondary-color: #4F5D75;
            --accent-color: #5C80BC;
            --light-color: #EDF2F4;
            --success-color: #44AF69;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f5f7;
            color: var(--primary-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px 0;
            background-color: var(--primary-color);
            color: var(--light-color);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        h2 {
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: var(--secondary-color);
        }

        .content {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .card {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }

        @media (max-width: 768px) {
            form {
                grid-template-columns: 1fr;
            }
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--secondary-color);
        }

        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            transition: border 0.3s;
        }

        input:focus, select:focus {
            border-color: var(--accent-color);
            outline: none;
        }

        .color-pickers {
            display: flex;
            gap: 20px;
        }

        .color-picker {
            flex: 1;
        }

        .color-preview {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: inline-block;
            margin-left: 10px;
            vertical-align: middle;
            border: 1px solid #ddd;
        }

        button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            font-weight: 600;
            width: 100%;
        }

        button:hover {
            background-color: #4a6fa5;
        }

        .btn-success {
            background-color: var(--success-color);
        }

        .btn-success:hover {
            background-color: #3a9459;
        }

        .logo-preview {
            margin: 30px 0;
            text-align: center;
        }

        .preview-image {
            max-width: 100%;
            height: auto;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        .download-section {
            text-align: center;
            margin-top: 30px;
        }

        .download-btn {
            display: inline-block;
            max-width: 300px;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: var(--secondary-color);
            font-size: 0.9rem;
        }

        .required:after {
            content: " *";
            color: red;
        }

        .split-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .split-section {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ProLogo Generator</h1>
            <p>Create professional logos for your business in seconds</p>
        </header>

        <div class="content">
            {% if logo_image %}
            <div class="card">
                <h2>Your Generated Logo</h2>
                <div class="logo-preview">
                    <img src="data:image/png;base64,{{ logo_image }}" alt="Generated Logo" class="preview-image">
                </div>
                <div class="download-section">
                    <form action="/download" method="post">
                        <input type="hidden" name="logo_data" value="{{ logo_image }}">
                        <button type="submit" class="btn-success download-btn">Download Logo (PNG)</button>
                    </form>
                </div>
                <p style="text-align: center; margin-top: 20px;">
                    <a href="/" style="color: var(--accent-color); text-decoration: none;">← Create another logo</a>
                </p>
            </div>
            {% else %}
            <div class="card">
                <h2>Design Your Logo</h2>
                <form action="/generate" method="post">
                    <div>
                        <div class="form-group">
                            <label for="company_name" class="required">Company Name</label>
                            <input type="text" id="company_name" name="company_name" required placeholder="Enter your company name">
                        </div>

                        <div class="form-group">
                            <label for="tagline">Tagline (optional)</label>
                            <input type="text" id="tagline" name="tagline" placeholder="Your company tagline">
                        </div>

                        <div class="form-group">
                            <label for="font_style">Font Style</label>
                            <select id="font_style" name="font_style">
                                <option value="serif">Serif</option>
                                <option value="sans-serif" selected>Sans-serif</option>
                                <option value="modern">Modern</option>
                                <option value="playful">Playful</option>
                                <option value="elegant">Elegant</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <div class="form-group">
                            <label for="icon_choice">Icon Style</label>
                            <select id="icon_choice" name="icon_choice">
                                <option value="abstract">Abstract</option>
                                <option value="geometric" selected>Geometric</option>
                                <option value="letter-based">Letter-based</option>
                                <option value="minimal">Minimal</option>
                                <option value="tech">Tech</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Colors</label>
                            <div class="color-pickers">
                                <div class="color-picker">
                                    <label for="primary_color">Primary</label>
                                    <input type="color" id="primary_color" name="primary_color" value="#4A90E2">
                                </div>
                                <div class="color-picker">
                                    <label for="secondary_color">Secondary</label>
                                    <input type="color" id="secondary_color" name="secondary_color" value="#50E3C2">
                                </div>
                            </div>
                        </div>

                        <div class="form-group" style="margin-top: 20px;">
                            <button type="submit">Generate Logo</button>
                        </div>
                    </div>
                </form>
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <p>© 2025 ProLogo Generator | Created with Flask and Pillow</p>
        </div>
    </div>
</body>
</html>
'''


def get_contrasting_text_color(bg_color):
    """Determine if text should be white or black based on background color brightness"""
    # Convert hex to RGB
    bg_color = bg_color.lstrip('#')
    r, g, b = int(bg_color[0:2], 16), int(bg_color[2:4], 16), int(bg_color[4:6], 16)

    # Calculate perceived brightness
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    # Return black for light backgrounds, white for dark backgrounds
    return (0, 0, 0) if brightness > 128 else (255, 255, 255)


def draw_abstract_icon(draw, x, y, size, primary_color, secondary_color):
    """Draw an abstract icon"""
    points = []
    for i in range(5):
        angle = math.pi * 2 * i / 5
        points.append((
            x + size * 0.8 * math.cos(angle),
            y + size * 0.8 * math.sin(angle)
        ))

    draw.polygon(points, fill=primary_color)

    # Add circle with secondary color
    draw.ellipse((x - size * 0.4, y - size * 0.4, x + size * 0.4, y + size * 0.4), fill=secondary_color)


def draw_geometric_icon(draw, x, y, size, primary_color, secondary_color):
    """Draw a geometric icon"""
    # Draw hexagon
    points = []
    for i in range(6):
        angle = math.pi * 2 * i / 6
        points.append((
            x + size * 0.8 * math.cos(angle),
            y + size * 0.8 * math.sin(angle)
        ))

    draw.polygon(points, fill=primary_color)

    # Inner triangle
    inner_points = []
    for i in range(3):
        angle = math.pi * 2 * i / 3 + math.pi / 6
        inner_points.append((
            x + size * 0.5 * math.cos(angle),
            y + size * 0.5 * math.sin(angle)
        ))

    draw.polygon(inner_points, fill=secondary_color)


def draw_letter_based_icon(draw, x, y, size, primary_color, secondary_color, letter):
    """Draw a letter-based icon"""
    # Background circle
    draw.ellipse((x - size, y - size, x + size, y + size), fill=primary_color)

    # Add the letter
    font_size = int(size * 1.5)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()

    # Get text dimensions using the newer method
    left, top, right, bottom = font.getbbox(letter)
    text_width = right - left
    text_height = bottom - top

    draw.text((x - text_width / 2, y - text_height / 2), letter, fill=secondary_color, font=font)


def draw_minimal_icon(draw, x, y, size, primary_color, secondary_color):
    """Draw a minimal icon"""
    # Simple square and circle
    draw.rectangle((x - size * 0.8, y - size * 0.8, x + size * 0.8, y + size * 0.8), fill=primary_color)
    draw.ellipse((x - size * 0.5, y - size * 0.5, x + size * 0.5, y + size * 0.5), fill=secondary_color)


def draw_tech_icon(draw, x, y, size, primary_color, secondary_color):
    """Draw a tech-themed icon"""
    # Circuit-like pattern
    draw.rectangle((x - size * 0.8, y - size * 0.8, x + size * 0.8, y + size * 0.8), fill=primary_color)

    # Add circuit lines
    line_color = secondary_color
    draw.line((x - size * 0.8, y, x + size * 0.8, y), fill=line_color, width=int(size * 0.1))
    draw.line((x, y - size * 0.8, x, y + size * 0.8), fill=line_color, width=int(size * 0.1))

    # Add corner elements
    circle_size = size * 0.2
    draw.ellipse((x - size * 0.8 - circle_size, y - size * 0.8 - circle_size,
                  x - size * 0.8 + circle_size, y - size * 0.8 + circle_size), fill=line_color)
    draw.ellipse((x + size * 0.8 - circle_size, y - size * 0.8 - circle_size,
                  x + size * 0.8 + circle_size, y - size * 0.8 + circle_size), fill=line_color)
    draw.ellipse((x - size * 0.8 - circle_size, y + size * 0.8 - circle_size,
                  x - size * 0.8 + circle_size, y + size * 0.8 + circle_size), fill=line_color)
    draw.ellipse((x + size * 0.8 - circle_size, y + size * 0.8 - circle_size,
                  x + size * 0.8 + circle_size, y + size * 0.8 + circle_size), fill=line_color)


def generate_logo(company_name, tagline, primary_color, secondary_color, font_style, icon_choice):
    """Generate a logo based on user inputs"""
    # Create a blank image with white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Convert hex colors to RGB tuples
    primary_rgb = tuple(int(primary_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    secondary_rgb = tuple(int(secondary_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

    # Background with primary color
    draw.rectangle((0, 0, width, height), fill=primary_rgb)

    # Determine text color based on background brightness
    text_color = get_contrasting_text_color(primary_color)

    # Choose font based on style
    font_paths = {
        'serif': 'times.ttf',
        'sans-serif': 'arial.ttf',
        'modern': 'calibri.ttf',
        'playful': 'comici.ttf',
        'elegant': 'georgia.ttf'
    }

    # Get a default font as fallback
    try:
        company_font = ImageFont.truetype(font_paths.get(font_style, 'arial.ttf'), 72)
        tagline_font = ImageFont.truetype(font_paths.get(font_style, 'arial.ttf'), 36)
    except IOError:
        # Fallback to default font
        company_font = ImageFont.load_default()
        tagline_font = ImageFont.load_default()

    # Draw icon based on choice
    icon_size = 100
    icon_x = width // 2
    icon_y = height // 3

    if icon_choice == 'abstract':
        draw_abstract_icon(draw, icon_x, icon_y, icon_size, secondary_rgb, primary_rgb)
    elif icon_choice == 'geometric':
        draw_geometric_icon(draw, icon_x, icon_y, icon_size, secondary_rgb, primary_rgb)
    elif icon_choice == 'letter-based':
        # Use the first letter of company name
        letter = company_name[0].upper() if company_name else 'A'
        draw_letter_based_icon(draw, icon_x, icon_y, icon_size, secondary_rgb, text_color, letter)
    elif icon_choice == 'minimal':
        draw_minimal_icon(draw, icon_x, icon_y, icon_size, secondary_rgb, primary_rgb)
    elif icon_choice == 'tech':
        draw_tech_icon(draw, icon_x, icon_y, icon_size, secondary_rgb, text_color)

    # Draw company name - Using the updated method for text dimensions
    left, top, right, bottom = company_font.getbbox(company_name)
    company_text_width = right - left
    company_text_height = bottom - top

    company_text_position = ((width - company_text_width) // 2, icon_y + icon_size + 40)
    draw.text(company_text_position, company_name, fill=text_color, font=company_font)

    # Draw tagline if provided - Using the updated method for text dimensions
    if tagline:
        left, top, right, bottom = tagline_font.getbbox(tagline)
        tagline_text_width = right - left
        tagline_text_height = bottom - top

        tagline_text_position = ((width - tagline_text_width) // 2,
                                 company_text_position[1] + company_text_height + 20)
        draw.text(tagline_text_position, tagline, fill=text_color, font=tagline_font)

    # Add a decorative element
    draw.rectangle((0, height - 50, width, height), fill=secondary_rgb)

    return image


@app.route('/')
def index():
    """Render the main page with the input form"""
    return render_template_string(MAIN_TEMPLATE)


@app.route('/generate', methods=['POST'])
def generate():
    """Handle form submission and generate logo"""
    company_name = request.form.get('company_name', 'Company Name')
    tagline = request.form.get('tagline', '')
    primary_color = request.form.get('primary_color', '#4A90E2')
    secondary_color = request.form.get('secondary_color', '#50E3C2')
    font_style = request.form.get('font_style', 'sans-serif')
    icon_choice = request.form.get('icon_choice', 'geometric')

    # Generate logo
    logo = generate_logo(company_name, tagline, primary_color, secondary_color, font_style, icon_choice)

    # Convert logo to base64 for embedding in HTML
    buffered = io.BytesIO()
    logo.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Render template with logo
    return render_template_string(MAIN_TEMPLATE, logo_image=img_str)


@app.route('/download', methods=['POST'])
def download():
    """Handle logo download"""
    logo_data = request.form.get('logo_data', '')

    if not logo_data:
        return "No logo data provided", 400

    # Decode the base64 image
    logo_bytes = base64.b64decode(logo_data)

    # Create a response with the image
    response = make_response(logo_bytes)

    # Set appropriate headers
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"prologo_{timestamp}.png"
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', f'attachment; filename={filename}')

    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)