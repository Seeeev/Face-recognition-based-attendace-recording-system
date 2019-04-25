import cv2
import os
from easygui import enterbox
import ctypes
import sqlite3
import sys

conn = sqlite3.connect('db_employees.db')
c = conn.cursor()
c.execute("""SELECT empID from tb_emp_info""")
id_list = c.fetchall()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "Training Face")

while True:
    # Create a folder for training set
    id_ = enterbox(msg='Please enter your ID.', title=' ', default='', strip=True)
    if id_ !=None:
        # Create Directory
        dirname = image_dir +'/'+ id_
        # Verify if folder exists and employee is registered already
        if not os.path.exists("training face/"+id_) and any(item for item in id_list if id_ in item):
            os.mkdir(dirname)
            faceCascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')

            cam = cv2.VideoCapture(0)

            cv2.namedWindow("Face Registration")

            img_counter = 0
            while True:
                ret, frame = cam.read()
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                for(x,y,w,h) in faces:
                    # Region of Interest/Determine the location of the face
                    roi_gray = gray[y:y + h, x:x + w]
                    roi_color = frame[y:y + h, x:x + w]
                # Create a rectangle on the face
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                cv2.imshow("Face Registration", frame)
                if not ret:
                    break
                k = cv2.waitKey(1)

                if k % 256 == 27:
                    # ESC pressed
                    print("Escape hit, closing...")
                    break
                elif k % 256 == 32:
                    # SPACE pressed
                    img_name = "opencv_frame_{}.png".format(img_counter)
                    cv2.imwrite(os.path.join(dirname, img_name), frame)
                    print("{} written!".format(img_name))
                    img_counter += 1

            cam.release()
            cv2.destroyAllWindows()
            break
        else:
            ctypes.windll.user32.MessageBoxW(0, "    Error! File already exists or you are not registered yet.", "Error", 0)
    else:
        break
   

    
