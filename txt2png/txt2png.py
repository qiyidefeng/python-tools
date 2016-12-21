# coding=utf-8
from PIL import Image, ImageFont, ImageDraw


def txt2png(txt, img_width, font_name, font_size, png_name, png_margin):
    font = ImageFont.truetype(font_name, font_size)
    lines = []
    for line in txt.split('\n'):
        while font.getsize(line)[0] > img_width:
            ix = 2
            while font.getsize(line[:ix])[0] < img_width - 2 * png_margin:
                ix += 1
            lines.append(line[:ix])
            line = line[ix:]
        lines.append(line)
    line_height = font.getsize(txt)[1]
    img_height = line_height * (len(lines) + 1)
    im = Image.new("RGB", (img_width,
                           img_height), (255, 255, 255))

    dr = ImageDraw.Draw(im)
    x, y = png_margin, 5
    for line in lines:
        dr.text((x, y), line, font=font, fill="#000000")
        y += line_height
    im.save(png_name)

if __name__ == '__main__':
    with open('test.txt', 'r') as f:
        txt2png(f.read().decode('utf-8'), 600, "msyh.ttf", 18, '2.png', 20)
