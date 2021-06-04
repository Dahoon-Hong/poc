import sys, getopt
import os, shutil, glob
import random
import numpy as np
import cv2
import math
from datetime import datetime
import pandas as pd
import logging
from time import time
import warnings

warnings.filterwarnings(action='ignore')

log = None
pgtime = None

def set_logger():
    global log
    log = logging.getLogger(__file__)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(u'%(asctime)s [%(levelname)8s] %(filename)s (%(lineno)s) : %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    streamHandler.setLevel(logging.DEBUG)
    log.addHandler(streamHandler)


def printProgress(iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    global pgtime
    if not pgtime:
        pgtime = time()
    etime = time() - pgtime
    formatStr = "{0:." + str(decimals) + "f}" 
    percent_float = iteration / float(total)
    percent = formatStr.format(100 * (percent_float)) 
    if percent_float==0:
        expect_time = 0
    else:
        expect_time =  (1-percent_float)/percent_float * etime
    filledLength = int(round(barLength * iteration / float(total))) 
    bar = '#' * filledLength + '-' * (barLength - filledLength) 
    sys.stdout.write('\r%s |%s| %s%s %s (elapsed: %.2lf, expect_time: %.2lf)' % (prefix, bar, percent, '%', suffix, etime, expect_time))
    if iteration == total: 
        sys.stdout.write('\n') 
    sys.stdout.flush()


def parse_args(argv):
    source_image_dir_path = ''
    target_image_path = ''

    try:
        opts, args = getopt.getopt(argv, "s:t:", ["source-path=", "target-image"])
    except getopt.GetoptError:
        log.info(f"{__file__} -s <source-image-path> -t <target-image-path>")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-s", "--source-path"):
            source_image_dir_path = arg
        elif opt in ("-t", "--target-image"):
            target_image_path = arg
    
    log.info(f"source image path = {source_image_dir_path}")
    log.info(f"target image path = {target_image_path}")

    if not source_image_dir_path or not target_image_path:
        log.info("must enter both source image path and target image path")
        sys.exit(2)

    return source_image_dir_path, target_image_path


class MosaicGenerator:
    def __init__(self, source_image_dir_path, target_image_path, reuse=False):
        self.__source_image_dir_path = source_image_dir_path
        self.__target_image_path = target_image_path
        # log.debug(f"{self.__source_image_dir_path}, {self.__target_image_path}")
        self.__workspace = os.path.dirname(os.path.abspath(__file__)) + "/workspace"

        self.__max_source_image = 500

        self.__width_count = 100
        self.__height_count = 100

        self.__max_usage_count_for_single_image = int((self.__width_count * self.__height_count) / self.__max_source_image) + 25

        self.__window_width_px = 100
        self.__window_height_px = 100

        self.__max_dist = (255**2) * 3

        self.__init_dir()
        self.__reuse = reuse
        self.__extention = 'jpg'

    def __del__(self):
        pass

    def __init_dir(self):
        os.makedirs(self.__workspace, exist_ok=True)

    def __clean(self):
        shutil.rmtree(self.__workspace)

    def __get_source_images(self):
        file_list = glob.glob(f"{self.__workspace}/*.{self.__extention}")
        img_list = []
        if len(file_list) > 0 and self.__reuse:
            for f in file_list:
                img = cv2.imread(f)
                log.debug(f"{img.shape}")
                img_list.append(img)
            return img_list
        
        self.__clean()
        self.__init_dir()

        file_list = glob.glob(f"{self.__source_image_dir_path}/*.{self.__extention}")
        if len(file_list) > self.__max_source_image:
            random_sequence = random.sample(range(0, len(file_list)), self.__max_source_image)
            file_list = [file_list[x] for x in random_sequence]

        for f in file_list:
            f = os.path.basename(f)
            # log.debug(f"{self.__source_image_dir_path}/{os.path.basename(f)}")
            img = cv2.imread(f"{self.__source_image_dir_path}/{f}")
            log.debug(f"{f}, [{self.__window_height_px}, {self.__window_width_px}]")
            img = cv2.resize(img, (self.__window_width_px, self.__window_height_px), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(f"{self.__workspace}/{f}", img)
            img_list.append(img)

        return img_list
    
    def __read_target_image(self):
        
        img = cv2.imread(self.__target_image_path)
        h, w = img.shape[:2]

        self.__window_width_px = int(math.ceil(w / self.__width_count))
        self.__window_height_px = int(math.ceil(h / self.__height_count))
        
        return img

    def run(self, output_file_name):
        target_img = self.__read_target_image()
        source_imgs = self.__get_source_images()
        self.__build_source_image_table(source_imgs)

        result_img = np.zeros(
            (self.__window_height_px * self.__height_count,
            self.__window_width_px * self.__width_count,
            3),
            np.uint8
        )

        for y in range(self.__height_count):
            for x in range(self.__width_count):
                x1 = x * self.__window_width_px
                x2 = x1 + self.__window_width_px
                y1 = y * self.__window_height_px
                y2 = y1 + self.__window_height_px
                roi = target_img[y1:y2, x1:x2]
                # log.debug(f"{x1}, {x2}, {y1}, {y2}")
                if x2-x1 <=0 or y2-y1 <= 0:
                    break
                roi_rgb = roi.mean(axis=0).mean(axis=0)
                simg = self.__get_img_with_rgb(roi_rgb)
                # log.debug(simg)
                # log.debug(f"{x1}, {x2}, {y1}, {y2}")
                # log.debug(f"{result_img[x1:x2, y1:y2].shape}, {result_img.shape}")
                try:
                    result_img[y1:y2, x1:x2] = simg
                except ValueError as e:
                    log.error(f"{e}")
                    break
                printProgress(y*self.__width_count+x, self.__height_count * self.__width_count, 'Progress:', 'Complete', 1, 50)
        print("")

        log.info("DONE")
        cv2.imwrite(output_file_name, result_img)
        # cv2.imshow('img', result_img)
        cv2.waitKey(0)
        return 

    def __get_dist(self, rgb1, rgb2):
        dist = 0
        for i in range(0, 3):
            dist += (rgb1[i] - rgb2[i])**2
        return dist
    
    def __get_img_with_rgb(self, rgb):
        min_dist = self.__max_dist
        min_idx = -1

        for idx, dl in enumerate(self.__dl):
            if dl['count'] >= self.__max_usage_count_for_single_image:
                continue
            dist = self.__get_dist(dl['rgb'], rgb)

            if min_dist > dist:
                min_idx = idx
                min_dist = dist
        self.__dl[min_idx]['count'] += 1
        return self.__dl[min_idx]['img']
        
    def __build_source_image_table(self, image_list):
        self.__dl = list()

        for idx, img in enumerate(image_list):
            rgb = img.mean(axis=0).mean(axis=0)
            self.__dl.append(dict(
                gidx=idx,
                rgb=rgb,
                count=0,
                img=img
            ))


if __name__ == "__main__":
    set_logger()
    source_image_dir_path, target_image_path = parse_args(sys.argv[1:])
    mg = MosaicGenerator(source_image_dir_path, target_image_path, reuse=False)
    s = time()
    mg.run(datetime.now().strftime("result %Y-%m-%d %H%M%S") + '.jpg')
    e = time()
    log.info(f"etime: {(e-s):.3f} seconds")


# python main.py -s Y:/homes/dahoon/Drive/Camera -t Y:/homes/dahoon/Drive/Camera/20180925_131439.jpg