from plate_locator import PlateLocator
import cv2

p = PlateLocator.PlateLocator('./static/weights/locator/best.pt')
img = cv2.imread('./static/test_img/img_1.png')
pred = p.predict(img)
print(pred)