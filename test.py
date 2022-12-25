from PIL import Image
import numpy

img = Image.open('ht.png')
hitboxes = numpy.zeros((img.size[0], img.size[1]))
for i in range(img.size[0]):
    for j in range(img.size[1]):
        pix = img.load()[i, j]
        if pix[0] != 255:
            hitboxes[i][j] = 1
print(len(hitboxes))
numpy.savetxt('xd.txt', hitboxes)