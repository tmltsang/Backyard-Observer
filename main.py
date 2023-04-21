import cv2 as cv
from vision import Vision

def main():
    vision_fs = Vision('GGST_Testament_fS.png')
    haystack_img = cv.imread('GGST_Testament_ingame_fS.jpg', cv.IMREAD_UNCHANGED)
    # needle_img = cv.imread('GGST_Testament_fS_crop.jpg', cv.IMREAD_UNCHANGED)
    #needle_img = cv.imread('GGST_Testament_fS.png', cv.IMREAD_UNCHANGED)
    rects = vision_fs.find(haystack_img)
    output_img = vision_fs.draw_rectangles(haystack_img, rects)
    cv.imshow('Matches', output_img)
    cv.waitKey()

if __name__ == '__main__':
    main()
