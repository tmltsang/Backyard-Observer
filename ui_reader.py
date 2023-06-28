import cv2
import numpy as np

#healthbar 1 = 100,75 580,95
#healthbar 2 = 700,75 1180,95
#healthbar colors = (237,190,170) (243,133,134) 
#             HSV = (0, 52, 190)  (179, 255, 255)
#healthbar Damaged = (164, 0, 1)
#             HSV = (0, 255, 150) (179, 255, 255)

def read_health_bars(img):
    p1_health_bar = img[75:95, 100:580]
    p2_health_bar = img[75:95, 700:1180]
    p2_health_bar = cv2.flip(p2_health_bar, 1)
    cv2.imshow("health", p1_health_bar)
    cv2.imshow("health_2", p2_health_bar)
    hsv = cv2.cvtColor(p2_health_bar, cv2.COLOR_BGR2HSV)
    healthbar_mask = cv2.inRange(hsv, np.array([0,52,190]), np.array([179,255,255]))
    healthbar = cv2.bitwise_and(p2_health_bar,p2_health_bar, mask=healthbar_mask)
    healthbar = cv2.cvtColor(healthbar, cv2.COLOR_BGR2GRAY)
    #blur = cv2.GaussianBlur(healthbar,(5,5),0)
    _, health_bar_thresh = cv2.threshold(healthbar, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    result = cv2.dilate(health_bar_thresh, kernel)
    cv2.imshow("test", result)
    contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    minX = 500
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        if (x < minX):
            minX = x
    print("Health %: %f", (480-x)/480)
    cv2.drawContours(p2_health_bar, contours, -1, (0, 255, 0), 3)
    cv2.imshow('Contours', p2_health_bar)
    cv2.waitKey(0)