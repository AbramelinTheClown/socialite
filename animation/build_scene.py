import os
import json
import asyncio
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

# Configuration
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'renders')

# Asset paths
CHARACTER_ASSETS = {
    'coffee': {
        'background': r"D:\AI\nebles\images\set\coffee_house_back_stage.png",
        'body': r"D:\AI\nebles\images\set\coffee_body.png",
        'eyes': {
            'open': r"D:\AI\nebles\images\set\coffee_blinks.png",
            'closed': r"D:\AI\nebles\images\set\coffee_blinks.png"  # Same file with different CSS position
        },
        'mouth': {
            'closed': r"D:\AI\nebles\images\set\coffee_mouth_mid.png",
            'open': r"D:\AI\nebles\images\set\coffee_mouth_wide.png"
        },
        'effects': [
            r"D:\AI\nebles\images\set\smoke_1.png",
            r"D:\AI\nebles\images\set\smoke_2.png",
            r"D:\AI\nebles\images\set\smoke_3.png"
        ]
    },
    'nebbles': {
        'body': r"D:\AI\nebles\images\set\nebbles_body.png",
        'eyes': r"D:\AI\nebles\images\set\nebbles_eyes.png",
        'zodiac': r"D:\AI\nebles\images\set\nebbles_zodiac.png"
    }
}

class AnimationRenderer:
    def __init__(self, input_data):
        self.input_data = input_data
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        
    async def render_scene(self):
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Generate HTML
        template = self.env.get_template('scene_template.html.j2')
        html_content = template.render(
            character=self.input_data['character'],
            assets=CHARACTER_ASSETS[self.input_data['character']],
            timings=self.input_data['timings'],
            audio_path=self.input_data['audio_path']
        )
        
        html_path = os.path.join(OUTPUT_DIR, 'temp_scene.html')
        with open(html_path, 'w') as f:
            f.write(html_content)
            
        # Render video
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto(f'file:///{os.path.abspath(html_path)}')
            video_path = os.path.join(OUTPUT_DIR, 'output.webm')
            await page.video.start(path=video_path)
            
            # Wait for animation duration
            await page.wait_for_timeout(self.input_data['duration'] * 1000)
            
            await page.video.save_as(path=video_path)
            await browser.close()
            
        return video_path

if __name__ == "__main__":
    # Example test data
    test_data = {
        "character": "coffee",
        "audio_path": "/path/to/audio.mp3",
        "duration": 60,
        "timings": {
            "mouth_events": [
                {"type": "open", "start": 0.5, "end": 1.2},
                {"type": "closed", "start": 1.3, "end": 2.0}
            ],
            "blink_events": [
                {"timestamp": 0.8},
                {"timestamp": 1.5}
            ]
        }
    }
    
    renderer = AnimationRenderer(test_data)
    asyncio.run(renderer.render_scene())