from PIL import Image, ImageDraw

def create_icon(size):
    img = Image.new('RGB', (size, size), color='#1a73e8')
    draw = ImageDraw.Draw(img)
    margin = size // 6
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='white'
    )
    text_x = size // 2
    text_y = size // 2
    font_size = size // 3
    draw.ellipse(
        [text_x - font_size//2, text_y - font_size//2,
         text_x + font_size//2, text_y + font_size//2],
        fill='#1a73e8'
    )
    img.save(f'static/icon-{size}.png')
    print(f'Created: static/icon-{size}.png')

create_icon(192)
create_icon(512)
print('Both icons created successfully!')