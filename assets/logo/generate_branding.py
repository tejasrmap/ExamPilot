"""
ExamPilot Branding Generator — GT InnoX LLP
Generates custom ExamPilot branding assets:
- SVG master vector logo
- App icons (16, 32, 48, 128, 256, 512 px)
- Chrome extension icons (16, 32, 48, 128 px)
"""

import os
from PIL import Image, ImageDraw, ImageFont

SVG_CONTENT = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B1020" />
      <stop offset="100%" stop-color="#111827" />
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366F1" />
      <stop offset="100%" stop-color="#06B6D4" />
    </linearGradient>
    <linearGradient id="checkGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#22C55E" />
      <stop offset="100%" stop-color="#10B981" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background Shield / Squircle -->
  <rect x="24" y="24" width="464" height="464" rx="100" fill="url(#bgGrad)" stroke="#1E293B" stroke-width="4"/>
  <rect x="28" y="28" width="456" height="456" rx="96" fill="none" stroke="url(#accentGrad)" stroke-width="2" stroke-opacity="0.3"/>

  <!-- AI Neural Network Nodes & Links in Background -->
  <g opacity="0.4" stroke="#6366F1" stroke-width="2" fill="none">
    <line x1="160" y1="180" x2="256" y2="130" />
    <line x1="352" y1="180" x2="256" y2="130" />
    <line x1="160" y1="180" x2="256" y2="240" />
    <line x1="352" y1="180" x2="256" y2="240" />
    <line x1="256" y1="240" x2="256" y2="330" />
    <circle cx="160" cy="180" r="4" fill="#06B6D4" />
    <circle cx="352" cy="180" r="4" fill="#06B6D4" />
    <circle cx="256" cy="130" r="5" fill="#6366F1" />
    <circle cx="256" cy="240" r="5" fill="#6366F1" />
  </g>

  <!-- Academic Cap (Mortarboard Top) Combined with Navigation Wing -->
  <polygon points="256,120 400,185 256,245 112,185" fill="url(#accentGrad)" filter="url(#glow)"/>

  <!-- Cap Crown Base -->
  <path d="M 170,210 L 170,270 Q 256,320 342,270 L 342,210 Q 256,255 170,210 Z" fill="#1E1B4B" stroke="#6366F1" stroke-width="3"/>

  <!-- Academic Tassel Ribbon -->
  <path d="M 380,195 Q 400,240 405,290" fill="none" stroke="#06B6D4" stroke-width="4" stroke-linecap="round"/>
  <circle cx="405" cy="295" r="7" fill="#06B6D4"/>

  <!-- Dynamic Verification Checkmark (Passing MCQ / Success) -->
  <g filter="url(#glow)">
    <path d="M 190,320 L 235,365 L 340,260" fill="none" stroke="url(#checkGrad)" stroke-width="32" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>
'''

def generate_branding_images(base_dir: str):
    logo_dir = os.path.join(base_dir, "assets", "logo")
    icons_dir = os.path.join(base_dir, "assets", "icons")
    chrome_icons_dir = os.path.join(base_dir, "chrome-extension", "icons")
    
    os.makedirs(logo_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(chrome_icons_dir, exist_ok=True)
    
    svg_path = os.path.join(logo_dir, "exampilot_logo.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(SVG_CONTENT)
    print(f"Master SVG saved to {svg_path}")

    # Render PNGs using Pillow drawing
    sizes = [16, 32, 48, 64, 128, 256, 512]
    for s in sizes:
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Scaling factor
        scale = s / 512.0
        
        # Rounded background
        r = int(100 * scale)
        draw.rounded_rectangle([int(24 * scale), int(24 * scale), int(488 * scale), int(488 * scale)],
                               radius=r, fill=(11, 16, 32, 255), outline=(99, 102, 241, 180), width=max(1, int(3 * scale)))
        
        # Diamond / Mortarboard top
        diamond = [
            (int(256 * scale), int(120 * scale)),
            (int(400 * scale), int(185 * scale)),
            (int(256 * scale), int(245 * scale)),
            (int(112 * scale), int(185 * scale))
        ]
        draw.polygon(diamond, fill=(99, 102, 241, 255))
        
        # Cap base
        cap_base = [
            (int(170 * scale), int(210 * scale)),
            (int(170 * scale), int(270 * scale)),
            (int(256 * scale), int(310 * scale)),
            (int(342 * scale), int(270 * scale)),
            (int(342 * scale), int(210 * scale))
        ]
        draw.polygon(cap_base, fill=(30, 27, 75, 255), outline=(6, 182, 212, 255))
        
        # Checkmark
        check_width = max(2, int(28 * scale))
        check_points = [
            (int(190 * scale), int(320 * scale)),
            (int(235 * scale), int(365 * scale)),
            (int(340 * scale), int(260 * scale))
        ]
        draw.line([check_points[0], check_points[1]], fill=(34, 197, 94, 255), width=check_width)
        draw.line([check_points[1], check_points[2]], fill=(34, 197, 94, 255), width=check_width)
        
        # Save to assets/icons
        out_png = os.path.join(icons_dir, f"icon_{s}x{s}.png")
        img.save(out_png, "PNG")
        
        # Save extension icons (16, 32, 48, 128)
        if s in [16, 32, 48, 128]:
            chrome_png = os.path.join(chrome_icons_dir, f"icon_{s}.png")
            img.save(chrome_png, "PNG")

    # Also save standard app_icon.png and app_icon.ico
    icon_512 = os.path.join(icons_dir, "icon_512x512.png")
    app_icon_png = os.path.join(logo_dir, "exampilot_icon.png")
    app_icon_ico = os.path.join(icons_dir, "app_icon.ico")
    
    img_512 = Image.open(icon_512)
    img_512.save(app_icon_png, "PNG")
    
    # Save ICO containing multiple sizes
    img_ico_sizes = [Image.open(os.path.join(icons_dir, f"icon_{s}x{s}.png")) for s in [16, 32, 48, 64, 128, 256]]
    img_ico_sizes[0].save(app_icon_ico, format="ICO", sizes=[(s, s) for s in [16, 32, 48, 64, 128, 256]])
    print(f"Generated all icons and ICO to {icons_dir} and {chrome_icons_dir}")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    generate_branding_images(base)
 