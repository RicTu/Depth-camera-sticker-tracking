import depthai as dai
import numpy as np
import cv2
import matplotlib.pyplot as plt

def createDepthPipeline():
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setIspScale(1,2)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName('rgb')
    print('Created color camera')

    monoLeft = pipeline.createMonoCamera()
    monoRight = pipeline.createMonoCamera()
    monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
    monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    print('Created mono camera objects')

    stereo = pipeline.createStereoDepth()
    stereo.setConfidenceThreshold(200)
    stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
    stereo.setLeftRightCheck(True)
    stereo.setMedianFilter(dai.StereoDepthProperties.MedianFilter.KERNEL_7x7)
    xout_depth = pipeline.createXLinkOut()
    xout_depth.setStreamName('depth')
    print('Created stereo object')

    #Link
    cam_rgb.isp.link(xout_rgb.input)
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)
    stereo.disparity.link(xout_depth.input)
    print('Finished creating pipeline')
    return pipeline

pipeline = createDepthPipeline()
device = dai.Device(pipeline)
device.startPipeline()

q_rgb = device.getOutputQueue(name='rgb', maxSize=4, blocking=False)
q_depth = device.getOutputQueue(name='depth', maxSize=4, blocking=False)

n = 0; dist_2d = 0; dist_3d = 0
frame_num = []; distances_3d = []; distances_2d = []
while True:
    in_rgb = q_rgb.get()
    in_depth = q_depth.get()

    rgb_frame = in_rgb.getCvFrame()
    depth_frame = in_depth.getCvFrame()

    img_hsv = cv2.cvtColor(rgb_frame.copy(), cv2.COLOR_BGR2HSV)
    #Mask red pixels
    lower_red = np.array([0,180,50])
    upper_red = np.array([5, 255, 255])
    mask_red = cv2.inRange(img_hsv, lower_red, upper_red)

    lower_red = np.array([170, 180, 50])
    upper_red = np.array([180, 255, 255])
    mask_red += cv2.inRange(img_hsv, lower_red, upper_red)

    lower_blue = np.array([95, 180, 50])
    upper_blue = np.array([125, 255, 255])
    mask_blue = cv2.inRange(img_hsv, lower_blue, upper_blue)

    mask_red = cv2.GaussianBlur(mask_red, (3,3), 0)
    mask_blue = cv2.GaussianBlur(mask_blue, (3,3), 0)

    circles_red = cv2.HoughCircles(mask_red, cv2.HOUGH_GRADIENT, dp = 1,
        minDist = 5, param1 = 200, param2 = 3, minRadius = 6, maxRadius=12)
    circles_blue = cv2.HoughCircles(mask_blue, cv2.HOUGH_GRADIENT, dp = 1,
        minDist = 5, param1 = 200, param2 = 3, minRadius = 6, maxRadius =12)

    r_threshold = 10
    if np.array(circles_red).any() and np.array(circles_blue).any() is not None:
        circles_red = circles_red[0]
        circles_blue = circles_blue[0]
        for i in range(circles_red.shape[0]):
            for j in range(circles_blue.shape[0]):
                circle_r_error = np.abs(circles_red[i][2]-circles_blue[j][2])
                if circle_r_error < r_threshold:
                    pair = (i, j)
                    r_threshold = circle_r_error
        p1, p2 = pair
        average_r = np.mean([circles_red[p1][2], circles_blue[p2][2]])
        x_red, y_red = circles_red[p1][0], circles_red[p1][1]
        x_blue, y_blue = circles_blue[p2][0], circles_blue[p2][1]
        bbox_red = np.array([x_red-average_r, y_red-average_r, x_red+average_r, y_red+average_r]).astype('int')
        bbox_blue = np.array([x_blue-average_r, y_blue-average_r, x_blue+average_r, y_blue+average_r]).astype('int')
        cv2.rectangle(rgb_frame, (bbox_red[0], bbox_red[1]), (bbox_red[2],bbox_red[3]), (0,255,0), 2)
        cv2.rectangle(rgb_frame, (bbox_blue[0], bbox_blue[1]), (bbox_blue[2], bbox_blue[3]), (0,255,0), 2)

        #Calculating the depth of the Rois
        red_roi = depth_frame[bbox_red[1]:bbox_red[3], bbox_red[0]:bbox_red[2]]
        blue_roi = depth_frame[bbox_blue[1]:bbox_blue[3], bbox_blue[0]:bbox_blue[2]]

        disp_red = np.mean(red_roi[np.nonzero(red_roi)])
        disp_blue = np.mean(blue_roi[np.nonzero(blue_roi)])

        z_red = 3277.5//disp_red
        z_blue = 3277.5//disp_blue
        unit_ratio = 0.7/average_r
        if np.isnan(z_red) ==False and np.isnan(z_blue)==False:
            cv2.putText(rgb_frame, str(z_red)+ ' cm', (bbox_red[0],bbox_red[1]), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(rgb_frame, str(z_blue)+ ' cm', (bbox_blue[0], bbox_blue[1]), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            dist_3d = np.sqrt((unit_ratio*(x_red-x_blue))**2+(unit_ratio*(y_red-y_blue))**2+(z_red-z_blue)**2)
            dist_2d = np.sqrt((unit_ratio*(x_red-x_blue))**2+(unit_ratio*(y_red-y_blue))**2)

    depth_frame = (depth_frame/95*255).astype('uint8')
    cv2.imshow('mask_red', mask_red)
    cv2.imshow('mask_blue', mask_blue)
    cv2.imshow('rgb', rgb_frame)
    cv2.imshow('depth', depth_frame)
    if cv2.waitKey(1)==ord('q'):
        break

    n += 1
    frame_num.append(n)
    distances_3d.append(dist_3d)
    distances_2d.append(dist_2d)
    plt.plot(frame_num[-50:], distances_2d[-50:], 'r-')
    plt.plot(frame_num[-50:], distances_3d[-50:], 'g-')
    plt.xlabel('Frame number')
    plt.ylabel('Euclidean distance')
    plt.pause(0.05)
    plt.clf()
