import cv2
import numpy as np

# Create a 640x640 realistic flat roof image
img = np.full((640, 640, 3), (165, 175, 170), dtype=np.uint8)

# Add concrete/roof surface texture noise
noise = np.random.normal(0, 8, img.shape).astype(np.int16)
img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

# Roof parapet border
cv2.rectangle(img, (20, 20), (620, 620), (130, 140, 135), 8)

# 1. Stair headhouse / mumty structure (elevated rectangular building on roof)
cv2.rectangle(img, (70, 350), (220, 530), (195, 205, 200), -1)
cv2.rectangle(img, (70, 350), (220, 530), (90, 100, 95), 3)
# Shadow of headhouse
cv2.rectangle(img, (220, 370), (260, 530), (100, 105, 100), -1)

# 2. Cylindrical / overhead black water tank on metal stand
cv2.circle(img, (480, 140), 55, (25, 25, 30), -1)
cv2.circle(img, (480, 140), 55, (50, 50, 55), 3)
cv2.circle(img, (470, 130), 20, (60, 60, 65), -1) # lid
# Shadow of tank
cv2.ellipse(img, (530, 170), (45, 30), 30, 0, 360, (90, 95, 90), -1)

# 3. Air conditioner compressor unit (metal casing with fan grill)
cv2.rectangle(img, (420, 420), (520, 490), (230, 235, 235), -1)
cv2.rectangle(img, (420, 420), (520, 490), (110, 115, 115), 2)
cv2.circle(img, (470, 455), 22, (70, 75, 75), 2) # fan grill

# 4. Satellite dish (circular parabolic dish)
cv2.ellipse(img, (160, 130), (35, 25), -20, 0, 360, (220, 225, 225), -1)
cv2.ellipse(img, (160, 130), (35, 25), -20, 0, 360, (120, 125, 125), 2)
cv2.line(img, (160, 130), (180, 150), (80, 80, 80), 3) # feed horn arm

cv2.imwrite("sample_roof.jpg", img)
print("Saved sample_roof.jpg (640x640)")
