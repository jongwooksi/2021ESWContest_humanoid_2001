# -*- coding: utf-8 -*-

import numpy as np
import argparse
import cv2
import serial
import time
import pytesseract
from serialdata import *


def textImageProcessing(img, frame):

    img = cv2.Canny(img, 15, 40)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    img = cv2.dilate(img, kernel, iterations=2)

    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.erode(img, kernel)

    #cv2.imshow("daa", img)
    #key = cv2.waitKey(1)

    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        area = cv2.contourArea(c)
        approx = cv2.approxPolyDP(c, 0.01 * cv2.arcLength(c, True), True)


        if area > 3000:
            #cv2.drawContours(frame, [approx], 0, (0, 0, 255), 5)
            #cv2.imshow("d", frame)
            #cv2.waitKey(1)
            if len(approx) == 4:
                cv2.drawContours(frame, [approx], 0, (0, 0, 255), 5)
                #cv2.imshow("d", frame)
                #key = cv2.waitKey(1)
                left = list(tuple(c[c[:, :, 0].argmin()][0]))
                top = list(tuple(c[c[:, :, 1].argmin()][0]))
                right = list(tuple(c[c[:, :, 0].argmax()][0]))
                bottom = list(tuple(c[c[:, :, 1].argmax()][0]))

                x, y, w, h = cv2.boundingRect(c)

                distance_top = ((x - top[0])**2 + (y - top[1]) ** 2) ** 0.5

                distance_bottom = (((x+w) - bottom[0]) ** 2 + ((y+h) - bottom[1]) ** 2) ** 0.5

                return [[x, y], [x + w, y], [x, y + h], [x + w, y + h]], frame
                '''
                if distance_top < w * 0.1 or distance_top > w * 0.9:
                    print("회전없음")
                    return [[x, y], [x + w, y], [x, y + h], [x + w, y + h]], frame

                elif distance_bottom < w * 0.1 or distance_bottom > w * 0.9 :
                    print("회전없음")
                    return [[x, y], [x + w, y], [x, y + h], [x + w, y + h]], frame

                elif distance_top > (w/2):  
                    print("왼쪽")
                    return [left, top, bottom, right], frame

                else:
                    print("오른쪽")
                    return [top, right, left, bottom], frame
                '''


    return [[-1,-1], [-1,-1], [-1,-1], [-1,-1]], frame

cnt = 0

def textRecog(template):

    img = cv2.imread('abcd.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     
    th, tw = template.shape[:2]

    methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF_NORMED']

    count = [0,0,0,0] 


    for i, method_name in enumerate(methods):
        img_draw = img.copy()
        method = eval(method_name)
        res = cv2.matchTemplate(img, template, method)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
      
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
            match_val = 1-min_val
          
        else:
            top_left = max_loc
            match_val = max_val 
        
        if method_name == 'cv2.TM_CCOEFF_NORMED':
            match_val += 0.14
            
        
        print(match_val)
        if match_val <= 0.85:
            continue
            
        bottom_right = (top_left[0] + tw, top_left[1] + th)
        #print("크기 : ",top_left, bottom_right)
        if top_left[1] >= 0 and top_left[1] <= 162 and bottom_right[1] >= 0 and bottom_right[1] <= 163:
            count[0] += 1
        elif top_left[1] >= 163 and top_left[1] <= 359 and bottom_right[1] >= 163 and bottom_right[1] <= 359:
            count[1] += 1
        elif top_left[1] >= 360 and top_left[1] <= 557 and bottom_right[1] >= 360 and bottom_right[1] <= 557:
            count[2] += 1
        elif top_left[1] >= 558 and top_left[1] <= 720 and bottom_right[1] >= 558 and bottom_right[1] <= 720:
            count[3] += 1
        
    max_index = count.index(max(count))
    text = ""
    if max(count) == 3:
        if max_index == 0:
            text = "A"
        elif max_index == 1:
            text = "B"
        elif max_index == 2:
            text = "C"
        elif max_index == 3:
            text = "D"

    '''
    textimage = cv2.cvtColor(textimage, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    
    result = np.zeros((128, 128), np.uint8) + 255
    
    result[45:99, 25:79] = textimage
    result[45:99, 79:128] = textimage[:,5:]
    
    
    result[37:91, 37:91] = textimage

    
    cv2.imshow("canny", result)
    cv2.waitKey(1)

    text_image = pytesseract.image_to_string(result)
    
    text_image.replace(" ","")
    text_image.rstrip() 
    text_image = text_image[0:1]
    print("text "+text_image)
    if text_image == "A":
        text = "A"
    elif text_image == "B":
        text = "B"
    elif text_image == "C" or text_image == "c":
        text = "C"
    elif text_image == "D":
        text = "D"
    else :
        text = "error"

    if text == "error":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        textimage = cv2.dilate(textimage, kernel)
        textimage = cv2.dilate(textimage, kernel)
        result = np.zeros((128, 128), np.uint8) + 255
        result[45:99, 25:79] = textimage
        result[45:99, 79:128] = textimage[:,5:]
        
        cv2.imshow("canny", result)
        cv2.waitKey(1)

        text_image = pytesseract.image_to_string(result, lang='eng')
        text_image.replace(" ","")
        text_image.rstrip() 
        text_image = text_image[0:1]
        print("text "+text_image)
        if text_image == "A":
            text = "A"
        elif text_image == "B":
            text = "B"
        elif text_image == "C" or text_image == "c":
            text = "C"
        elif text_image == "D":
            text = "D"
        else :
            text = "error"
            
    if text == "error":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        textimage = cv2.dilate(textimage, kernel)
      
        result = np.zeros((128, 128), np.uint8) + 255
        result[45:99, 25:79] = textimage
        result[45:99, 79:128] = textimage[:,5:]
        
        cv2.imshow("canny", result)
        cv2.waitKey(1)

        text_image = pytesseract.image_to_string(result, lang='eng')
        text_image.replace(" ","")
        text_image.rstrip() 
        text_image = text_image[0:1]
        print("text "+text_image)
        if text_image == "A":
            text = "A"
        elif text_image == "B":
            text = "B"
        elif text_image == "C" or text_image == "c":
            text = "C"
        elif text_image == "D":
            text = "D"
        else :
            text = "error"
            
    if text == "error":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        textimage = cv2.erode(textimage, kernel)
       
        result = np.zeros((128, 128), np.uint8) + 255
        result[45:99, 25:79] = textimage
        result[45:99, 79:128] = textimage[:,5:]
    
        cv2.imshow("canny", result)
        cv2.waitKey(1)

        text_image = pytesseract.image_to_string(result, lang='eng')
        text_image.replace(" ","")
        text_image.rstrip() 
        text_image = text_image[0:1]
        print("text "+text_image)
        if text_image == "A":
            text = "A"
        elif text_image == "B":
            text = "B"
        elif text_image == "C" or text_image == "c":
            text = "C"
        elif text_image == "D":
            text = "D"
        else :
            text = "error"
        '''
        
    return text

def Recog(img_color):
    img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
   
    lower_red = np.array([0, 30, 60])
    upper_red = np.array([20, 255, 150])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

    lower_red = np.array([160, 30, 60])
    upper_red = np.array([180, 255, 150])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

    red_mask = mask0 + mask1

    lower_blue = np.array([90, 50, 60])
    upper_blue = np.array([130, 255, 150])
    blue_mask = cv2.inRange(img_hsv, lower_blue, upper_blue)

    red_hsv = img_hsv.copy()
    blue_hsv = img_hsv.copy()
    
    #cv2.imshow('sss',red_mask)
    #cv2.waitKey(1)
    
    #cv2.imshow('ssss',blue_mask)
    #cv2.waitKey(1)
    
    red_count = len(red_hsv[np.where(red_mask != 0)])
    blue_count = len(blue_hsv[np.where(blue_mask != 0)])
    print(red_count)
    print(blue_count)
    print()
    if red_count > blue_count:
        color = "red"
        red_hsv[np.where(red_mask != 0)] = 0
        red_hsv[np.where(red_mask == 0)] = 255
        #text = textRecog(red_hsv)

    else:
        color = "blue"
        blue_hsv[np.where(blue_mask != 0)] = 0
        blue_hsv[np.where(blue_mask == 0)] = 255
        #text = textRecog(blue_hsv)

    
    
    return color

def loop(serial_port):
    global cnt
    W_View_size = 320
    H_View_size = int(W_View_size / 1.333)

    FPS         = 1  #PI CAMERA: 320 x 240 = MAX 90

    rectangle_count = 0
    head_flag = False
    
    

    cap = cv2.VideoCapture(0)

    cap.set(3, W_View_size)
    cap.set(4, H_View_size)
    cap.set(5, FPS)  
    
    TX_data_py2(serial_port, 21)
    TX_data_py2(serial_port, 43)
    TX_data_py2(serial_port, 67)
    
    
    time.sleep(1)
    
    f = open("./data/area.txt","r")
    
    area = f.readline()
    f.close()
    
    f_dir = open("./data/arrow.txt", 'r')
    direction = f_dir.readline()
    print(direction)
    f_dir.close()
    
    
    f2 = open("./data/result.txt","a")
    f3 = open("./data/color.txt","w")
    head_flag = 0
    while True:
        #wait_receiving_exit()
        if not count_frame():
            continue
        _,frame = cap.read()
        frame = frame[60:160]
        frame = cv2.resize(frame, (480,220))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dst = img.copy()

        points, frame = textImageProcessing(img, frame)

        #cv2.imshow("Frame", frame)
        #key = cv2.waitKey(1)

        #if key == 27:
        #    break
        # original : only continue
        if points[0][0] is -1:
            
            
            
            if rectangle_count == 15 and head_flag is 0:
                # head left 28
                TX_data_py2(serial_port, 72)
                time.sleep(1)
                rectangle_count = 0
                head_flag = 1
                continue
            elif rectangle_count == 15 and head_flag is 1:
                # head right 30
                TX_data_py2(serial_port, 70)
                time.sleep(1)
                rectangle_count = 2
                head_flag = 2
                continue
            elif rectangle_count == 15 and head_flag is 2:
                # head right 30
                TX_data_py2(serial_port, 21)
                time.sleep(1)
                rectangle_count = 0
                head_flag = 3
                continue
            elif rectangle_count == 15 and head_flag is 3:
                # head right 30
                TX_data_py2(serial_port, 71)
                time.sleep(1)
                rectangle_count = 0
                head_flag = 4
                continue
            elif rectangle_count == 15 and head_flag is 4:
                # head right 30
                TX_data_py2(serial_port, 73)
                time.sleep(1)
                rectangle_count = 5
                head_flag = 0
                continue
            elif rectangle_count == 15 and head_flag is 5:
                # head right 30
                TX_data_py2(serial_port, 75)
                time.sleep(1)
                rectangle_count = 0
                head_flag = 6
                continue
            elif rectangle_count == 15 and head_flag is 6:
                # head right 30
                TX_data_py2(serial_port, 74)
                time.sleep(1)
                rectangle_count = 0
                head_flag = 0
                continue        
            rectangle_count += 1
            continue

        print(points)


        pts1 = np.float32([[ points[0], points[1], points[2], points[3]]])
        pts2 = np.float32([[0, 0], [128, 0], [0, 128], [128, 128]])

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        textimage = cv2.warpPerspective(dst, matrix, (128, 128))

        textimage = textimage[12:110, 12:110]
        textimage = cv2.resize(textimage, (128, 128))

        text = textRecog(textimage)
        
        img_color =  cv2.warpPerspective(frame, matrix, (128, 128))
        img_color = img_color[12:110, 12:110]
        img_color = cv2.resize(img_color, (54, 54))

        color = Recog(img_color)

        print("text : {} \ncolor : {}".format(text, color))
        
        if text =="A" or text =="B" or text=="C" or text=="D":
            TX_data_py2(serial_port, 26)
            time.sleep(1)
            
        continue
        
        if text == "A":
            f3.write(color)
            if area == "dangerous":
                f2.write(text)
                break
                
            if direction == "right":
                TX_data_py2(serial_port, 19)
            elif direction == "left":
                TX_data_py2(serial_port, 25)
                
            break
        elif text == "B":
            f3.write(color)
            if area == "dangerous":
                f2.write(text)
                break
                
            if direction == "right":
                TX_data_py2(serial_port, 19)
            elif direction == "left":
                TX_data_py2(serial_port, 25)
                
            break
        elif text == "C":
            f3.write(color)
            if area == "dangerous":
                f2.write(text)
                break
                
            if direction == "right":
                TX_data_py2(serial_port, 19)
            elif direction == "left":
                TX_data_py2(serial_port, 25)
                
            break
        elif text == "D":
            f3.write(color)
            if area == "dangerous":
                f2.write(text)
                break
                
            if direction == "right":
                TX_data_py2(serial_port, 19)
            elif direction == "left":
                TX_data_py2(serial_port, 25)
                
            break
        
        
    
            
        



    cap.release()
    cv2.destroyAllWindows()
    f.close()
    f2.close()
    f3.close()
    time.sleep(1)
    exit(1)
   
   
if __name__ == '__main__':

    BPS =  4800  # 4800,9600,14400, 19200,28800, 57600, 115200

       
    serial_port = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
    serial_port.flush() # serial cls
    
    
    serial_t = Thread(target=Receiving, args=(serial_port,))
    serial_t.daemon = True
    
    
    serial_d = Thread(target=loop, args=(serial_port,))
    serial_d.daemon = True
    
    print("start")
    serial_t.start()
    serial_d.start()
    
    #serial_t.join()
    serial_d.join()
    print("end")
    
        
    
    








