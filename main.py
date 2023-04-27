import cv2 as cv
from vision import Vision
from time import time


def main():
    capture = cv.VideoCapture('testament_vs_hc.mp4')
    #vision_fs = Vision('img/testament/GGST_Testament_fS_copy.png', threshold=0.85)
    #vision_fs_flipped = Vision('img/testament/GGST_Testament_fS_copy.png', threshold=0.85, flipped=True)
    train_img = cv.imread('img/testament/GGST_Testament_ingame_fS.jpg', cv.IMREAD_UNCHANGED)
    query_img = cv.imread('img/testament/GGST_Testament_fS_copy.png', cv.IMREAD_UNCHANGED)
    #needle_img = cv.imread('GGST_Testament_fS.png', cv.IMREAD_UNCHANGED)

    # orb = cv.ORB_create()
    # FLANN_INDEX_LSH = 6
    # index_params= dict(algorithm = FLANN_INDEX_LSH,
    #                table_number = 6, # 12
    #                key_size = 12,     # 20
    #                multi_probe_level = 1) #2
    # search_params = dict(checks=100)

    sift = cv.SIFT_create()
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=500)

    queryKeypoints, queryDescriptors = sift.detectAndCompute(query_img, None)
    trainKeypoints, trainDescriptors = sift.detectAndCompute(train_img, None)
    flann = cv.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(queryDescriptors, trainDescriptors, k=2)
    matchesMask = [[0,0] for i in range(len(matches))]
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            matchesMask[i]=[1,0]
    
    draw_params = dict(matchColor = (0, 255, 0), singlePointColor = (255,0,0), matchesMask = matchesMask, flags = 0)
    final_img = cv.drawMatchesKnn(query_img, queryKeypoints, train_img, trainKeypoints, matches, None, **draw_params)

    cv.imshow("Matches", final_img)
    cv.waitKey(0)
    loop_time = time()

    # if (capture.isOpened() == False):
    #     print("Error opening file")

    # while(capture.isOpened()):
    #     ret, frame = capture.read()
    #     if ret == True:
    #         #rects = vision_fs.find(frame)
    #         #rects += vision_fs_flipped.find(frame)
    #         #output_img = vision_fs.draw_rectangles(frame, rects)
    #         #cv.imshow('Matches', output_img)
    #         #print('FPS {}'.format(1 / (time() - loop_time)))
    #         loop_time = time()
    #         #if (len(rects) > 0):
    #         #    cv.imwrite('debug/result' + str(time()) + '.jpg', output_img)

    #         # press 'q' with the output window focused to exit.
    #         # waits 1 ms every loop to process key presses
    #         if cv.waitKey(1) == ord('q'):
    #             cv.destroyAllWindows()
    #             break
    #     else:
    #         break
    # # When everything done, release the video capture object
    # capture.release()

    # Closes all the frames
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
