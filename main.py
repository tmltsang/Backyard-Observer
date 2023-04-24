import cv2 as cv
from vision import Vision
from time import time


def main():
    capture = cv.VideoCapture('testament_vs_hc.mp4')
    #vision_fs = Vision('img/testament/GGST_Testament_fS_copy.png', threshold=0.85)
    #vision_fs_flipped = Vision('img/testament/GGST_Testament_fS_copy.png', threshold=0.85, flipped=True)
    #haystack_img = cv.imread('img/testament/GGST_Testament_ingame_fS.jpg', cv.IMREAD_UNCHANGED)
    # needle_img = cv.imread('GGST_Testament_fS_crop.jpg', cv.IMREAD_UNCHANGED)
    #needle_img = cv.imread('GGST_Testament_fS.png', cv.IMREAD_UNCHANGED)
    object_detector = cv.createBackgroundSubtractorMOG2()
    loop_time = time()

    if (capture.isOpened() == False):
        print("Error opening file")

    while(capture.isOpened()):
        ret, frame = capture.read()
        if ret == True:
            #rects = vision_fs.find(frame)
            #rects += vision_fs_flipped.find(frame)
            #output_img = vision_fs.draw_rectangles(frame, rects)
            mask = object_detector.apply(frame)
            contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv.contourArea(cnt)
                if area > 100:
                    cv.drawContours(frame, [cnt], -1 , (0, 255, 0), 2)
            cv.imshow("Frame", frame)
            cv.imshow("Mask", mask)
            #cv.imshow('Matches', output_img)
            #print('FPS {}'.format(1 / (time() - loop_time)))
            loop_time = time()
            #if (len(rects) > 0):
            #    cv.imwrite('debug/result' + str(time()) + '.jpg', output_img)

            # press 'q' with the output window focused to exit.
            # waits 1 ms every loop to process key presses
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                break
        else:
            break
    # When everything done, release the video capture object
    capture.release()

    # Closes all the frames
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
