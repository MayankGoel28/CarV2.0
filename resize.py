from PIL import Image, ImageOps
img = Image.open('self.png')
img = img.resize((100, 100), Image.ANTIALIAS)
img_with_border = ImageOps.expand(img,border=5,fill='black')
img_with_border.save('imaged-with-border.png')