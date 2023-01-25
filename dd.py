import cv2

img = cv2.imread(r'C:\\Users\\pc\\Desktop\\blender\\GettyImages-1092658864_hero-1024x575.jpg', cv2.IMREAD_COLOR)
img = cv2.resize(img, (610, 342))
cv2.imshow('image',img)
print(img.shape)
cv2.waitKey(0)
#img(y,x)
#skin
b,g,r = (img[112, 312])
"""
print (r)
print (g)
print (b)
"""
#hair
bh,gh,rh=(img[24, 321])
"""
print (rh)
print (gh)
print (bh)
"""




