from PIL import Image, ImageDraw, ImageFont
import os

def generate_templates():
    # Create output directory if needed
    os.makedirs('card_templates', exist_ok=True)
    
    # Configuration
    image_size = (100, 140)
    background_color = (0, 0, 0)
    text_color = (255, 255, 255)
    font_size = 64
    
    # Generate for all required symbols
    symbols = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    for symbol in symbols:
        # Create blank image
        img = Image.new('RGB', image_size, background_color)
        draw = ImageDraw.Draw(img)
        
        # Load font and calculate text position
        try:
            font = ImageFont.truetype('Arial.ttf', font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (image_size[0] - text_width) / 2
        y = (image_size[1] - text_height) / 2
        
        # Draw symbol and save
        draw.text((x, y), symbol, fill=text_color, font=font)
        img.save(f'card_templates/{symbol}.png')

if __name__ == '__main__':
    generate_templates()