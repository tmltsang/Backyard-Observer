import cv2
import numpy as np

#healthbar 1 = 100,75 580,95
#healthbar 2 = 700,75 1180,95
#healthbar colors = (237,190,170) (243,133,134) 
#             HSV = [0,30,190] [179,255,255]
#healthbar Damaged = (164, 0, 1)
#             HSV = (0, 255, 150) (179, 255, 255)

#A class to read a bar in the UI, bar is using pixel position. Will resize the image to make this consistent
# x, int: X position of the bar
# y, int: Y position of the bar
# w, int: Width of the bar
# h, int: Height of the bar
# flipped, bool: Bars for P2 are generally the same as P1 but flipped
# hsv_lower_bound, [int,int,int]: The lower bound of the colour of the bar in hsv format
# hsv_upper_bound, [int,int,int]: The upper bound of the colour of the bar in hsv format
class Bar:
    def __init__(self, x, y, w, h, hsv_lower_bound, hsv_upper_bound,flipped=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hsv_lower_bound = hsv_lower_bound
        self.hsv_upper_bound = hsv_upper_bound
        self.flipped = flipped

    #
    def read_bar_percent(self, img):
        img = cv2.resize(img, (1280, 720), interpolation = cv2.INTER_AREA)
        bar = img[self.y:self.y+self.h, self.x:self.x+self.w]
        if self.flipped:
            bar = cv2.flip(bar, 1)
        #cv2.imshow("health", bar)
        hsv = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
        bar_mask = cv2.inRange(hsv, np.array(self.hsv_lower_bound), np.array(self.hsv_upper_bound))
        bar_filtered = cv2.bitwise_and(bar,bar, mask=bar_mask)
        bar_filtered = cv2.cvtColor(bar_filtered, cv2.COLOR_BGR2GRAY)
        #blur = cv2.GaussianBlur(healthbar,(5,5),0)
        _, health_bar_thresh = cv2.threshold(bar_filtered, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        kernel_erode = np.ones((3, 3), np.uint8)
        kernel_dialate = np.ones((5,5), np.uint8)
        bar_result = cv2.erode(health_bar_thresh, kernel_erode)
        bar_result = cv2.dilate(bar_result, kernel_dialate)
        contours, _ = cv2.findContours(bar_result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        minX = 500
        bar_contour = None
        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            if abs(h - self.h) < 5:
                bar_contour = contour
                if (x < minX):
                    minX = x
        bar_percent = 0
        if bar_contour is not None:
            bar_percent = (self.w-minX)/self.w
            #print(bar_contour)
            cv2.drawContours(bar, [bar_contour], -1, (0, 255, 0), 3)
            bar = cv2.putText(bar,str(bar_percent),(int((self.w + minX)/2), int(15)), cv2.FONT_HERSHEY_SIMPLEX, .5,(0,255,0),1,cv2.LINE_AA)
        #print("Health %: %f", bar_percent)
        return bar_percent, bar
        # cv2.waitKey(0)