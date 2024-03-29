import numpy as np
import cv2 as cv

video = cv.VideoCapture(0)
mog = cv.createBackgroundSubtractorMOG2()

def draw_roi(height, width):
    img = np.zeros((height, width), np.uint8)
    radius = int(height/3) if height < width else int(width/3)
    cv.circle(img, (int(width/2), int(height/2)), radius, (255, 255, 255), -1)
    return img

def filter(frame):
    kernel = np.array([
        [0,-1,0],
        [-1,5,-1],
        [0,-1,0],
    ])
    kernel2 = np.array([
        [0,0,0],
        [0,0,1],
        [0,1,1],
    ])
    kernel3 = np.array([
        [1,1,0],
        [1,0,0],
        [0,0,0],
    ])
    # blue_filter = np.zeros_like(frame)
    # blue_filter[:,:] = [100,0,0]  # b g r
    kernel99 = cv.getStructuringElement(cv.MORPH_ELLIPSE,(3,3))

    img = cv.filter2D(src=frame, ddepth=-1, kernel=kernel)
    fgm = mog.apply(frame)
    fgm = cv.morphologyEx(fgm, cv.MORPH_OPEN, kernel99)

    b,g,r = cv.split(img)
    z = np.zeros((frame.shape[0], frame.shape[1]), dtype='uint8')

    b = cv.merge([b, z, z])
    b = b.astype(np.float64)
    b = ((b/255)**(1/2.2))*255
    b = b.astype(np.uint8)

    r = cv.merge([z, z, r])
    r = cv.filter2D(src=r, ddepth=-1, kernel=kernel2)

    g = cv.merge([z, g, z])
    g = cv.filter2D(src=g, ddepth=-1, kernel=kernel3)
    return (b+r) * fgm[:, :, np.newaxis], img * np.logical_not(fgm[:, :, np.newaxis])

def filter2(frame):
    kernel = np.array([
        [0,-1,0],
        [-1,5,-1],
        [0,-1,0],
    ])
    kernel2 = np.array([
        [0.1,0,0],
        [0,0.5,0],
        [0,0,0],
    ])
    kernel3 = np.array([
        [0,0,0],
        [0,0.5,0],
        [0,0,0.1],
    ])
    img = cv.filter2D(src=frame, ddepth=-1, kernel=kernel)
    b,g,r = cv.split(img)
    z = np.zeros((frame.shape[0], frame.shape[1]), dtype='uint8')

    b = cv.merge([b, z, z])
    b = b.astype(np.float64)
    b = ((b/255)**(1/2.2))*255
    b = b.astype(np.uint8)

    r = cv.merge([z, z, r])
    r = cv.filter2D(src=r, ddepth=-1, kernel=kernel2)

    g = cv.merge([z, g, z])
    g = cv.filter2D(src=g, ddepth=-1, kernel=kernel3)
    return b+r


def watershed(frame, bg=None):
    img = frame
    origin = frame.copy()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    ret, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    thresh = np.uint8(thresh)
    kernel = np.ones((3,3), np.uint8)
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=2)
    
    sure_bg = cv.dilate(opening, kernel, iterations=3)
   
    dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
    ret, sure_fg = cv.threshold(dist_transform, 0.25*dist_transform.max(), 255, 0)
    sure_bg = np.uint8(sure_bg)
    sure_fg = np.uint8(sure_fg)
    unknown = cv.subtract(sure_bg, sure_fg)
    circle = draw_roi(height, width)
    sure_fg = cv.bitwise_and(sure_fg, circle)
    ret, markers = cv.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv.watershed(img, markers)
    
    img[markers == -1] = [0,0,0]
    img[markers == 1] = [0,0,0]
    #img[markers !=  1] = [255,0,255]
    img = np.uint8(img)
    img = filter2(img)
    if bg is not None:
        bg = bg * 0.1
        img = img*0.9
        imga = np.uint8(img + bg)
    return imga




while True:
    ret, frame = video.read()
    height, width, channels = frame.shape
    frame = cv.flip(frame, 1)
    bg = cv.imread('bg.jpg')
    bg = cv.resize(bg, dsize=(width, height), interpolation=cv.INTER_AREA)


    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    binary = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv.THRESH_BINARY, 15, 7)
    # ret, binary = cv.threshold(gray,127,254,cv.THRESH_BINARY)
    circle = draw_roi(height, width)
    ret, mask = cv.threshold(circle, 100, 255, cv.THRESH_BINARY)
    binary = cv.bitwise_and(binary, circle, mask=mask)

    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE,
                                          cv.CHAIN_APPROX_SIMPLE)
    black = np.zeros((height, width, 3), np.uint8)

    img = cv.drawContours(black, contours, -1, (10, 233, 10), 1)
    # fg, bg = filter(frame)
    cv.imshow('original', frame)
    # cv.imshow('frame', img)
    # cv.imshow('frame3', binary)
    #cv.imshow('fg', fg)
    #cv.imshow('bg', bg)
    # cv.imshow('merge', fg + bg)
    cv.imshow('markers', watershed(frame, bg))

    if cv.waitKey(1) & 0xFF == ord('q'):
        break


video.release()
cv.destroyAllWindows()
