import cv2 as cv
from vision import Vision
from time import time


def main():
    capture = cv.VideoCapture('testament_vs_hc.mp4')
    vision_fs = Vision('img/testament/GGST_Testament_fS.png')
    #haystack_img = cv.imread('img/testament/GGST_Testament_ingame_fS.jpg', cv.IMREAD_UNCHANGED)
    # needle_img = cv.imread('GGST_Testament_fS_crop.jpg', cv.IMREAD_UNCHANGED)
    #needle_img = cv.imread('GGST_Testament_fS.png', cv.IMREAD_UNCHANGED)
    if (capture.isOpened() == False):
        print("Error opening file")
    loop_time = time()
    while(capture.isOpened()):
        ret, frame = capture.read()
        if ret == True:
            rects = vision_fs.find(frame)
            output_img = vision_fs.draw_rectangles(frame, rects)
            cv.imshow('Matches', output_img)
            #print('FPS {}'.format(1 / (time() - loop_time)))
            loop_time = time()
            if (len(rects) > 0):
                cv.imwrite('debug/result' + str(time()) + '.jpg', output_img)

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
