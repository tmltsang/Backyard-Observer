import cv2 as cv
import numpy as np

class Vision:
    # properties
    needle_img = None
    needle_alpha = None
    needle_w = 0
    needle_h = 0
    method = None
    threshold = 0.80

    def __init__(self, needle_img_path, threshold=0.80, scale_percent=25, method=cv.TM_CCORR_NORMED, flipped=False):
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        width = int(self.needle_img.shape[1] * scale_percent / 100)
        height = int(self.needle_img.shape[0] * scale_percent / 100)
        dim = (width, height)
  
        # resize image
        self.needle_img = cv.resize(self.needle_img, dim, interpolation = cv.INTER_AREA)
        # Save the dimensions of the needle image
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        
        needle_img = self.needle_img[:,:,0:3]
        alpha = self.needle_img[:,:,3]
        self.needle_alpha = cv.merge([alpha, alpha, alpha])
        self.needle_img = needle_img

        if flipped:
            self.needle_img = cv.flip(self.needle_img, 1)
            self.needle_alpha = cv.flip(self.needle_alpha, 1)

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method
        self.threshold = threshold

    def find(self, haystack_img):
        result_rect = []

        result = cv.matchTemplate(haystack_img, self.needle_img, method=self.method, mask=self.needle_alpha)
        #Get the best match position
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val >= self.threshold and max_val != np.inf:
            print('Found needle.')
            print('Best match top left position: %s' % str(max_loc))
            print('Best match confidence: %s' % max_val)
            needle_w = self.needle_img.shape[1]
            needle_h = self.needle_img.shape[0]
            result_rect.append([int(max_loc[0]), int(max_loc[1]), needle_w, needle_h])

        return result_rect

    def draw_rectangles(self, img, rects):
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in rects :
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv.rectangle(img, top_left, bottom_right,
                            color=line_color, thickness=2, lineType=line_type)
        # cv.imshow('Result', haystack_img)
        # cv.waitKey()
        return img