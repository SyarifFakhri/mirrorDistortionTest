# import numpy as np
# import cv2
# from matplotlib import pyplot as plt
# import numpy as np
#
# percent_cutoff = 0.1
#
# img = cv2.imread('../assets/test_grid_1.jpeg')
# # img = cv2.resize(img, (500, 500))
# # img = img[0:0,0:350]
# # img = cv2.resize(img, (500, 500))
# gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# #
# # mask = cv2.imread('../assets/image_mask.png')
# # mask = cv2.resize(mask, (500,500))
# # mask_gray = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
# # ret, mask_thresh = cv2.threshold(mask_gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
#
# ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#
# kernel = np.ones((1,1),np.uint8)
# thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
#
# corners = cv2.goodFeaturesToTrack(thresh, 40, 0.5, 10) #, mask=mask_thresh)
#
# # dst = cv2.cornerHarris(thresh,10,3,0.04)
# # img[dst>0.01*dst.max()]=[0,0,255]
#
# corners = np.int0(corners)
#
# cv2.imshow("test", gray)
#
# for i in corners:
#     x,y = i.ravel()
#     cv2.circle(img,(x,y),3,255,-1)
#
# cv2.imshow("thresh", thresh)
#
# # added_image = cv2.addWeighted(img,0.4,mask,0.1,0)
# # cv2.imshow("img", added_image)
# cv2.imshow("img", img)
# # cv2.imshow("harris corner", dst)
# cv2.waitKey(0)

import cv2
import numpy as np

filename = '../assets/test_grid_1.jpeg'
img = cv2.imread(filename)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)


# find Harris corners
gray = np.float32(gray)
dst = cv2.cornerHarris(gray,2,5,0.007)
dst = cv2.dilate(dst,None)
ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
dst = np.uint8(dst)

# find centroids
ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

# define the criteria to stop and refine the corners
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)

# Now draw them
res = np.hstack((centroids,corners))
res = np.int0(res)
# img[res[:,1],res[:,0]]=[0,0,255]
img[res[:,3],res[:,2]] = [0,255,0]

cv2.imshow("image", img)
cv2.waitKey(0)