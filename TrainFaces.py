import cv2
import os
import numpy as np
from PIL import Image
import pickle
import time
import ctypes

def train():
        # Determine the time it takes to fininsh running
        start_time = time.time()

        #locating the base directory of the image set or the data set
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(BASE_DIR, "Training Face")

        #face detection using haar cascade 
        face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')

        #create a recognizer using Local Binary Pattern
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        current_id = 0
        label_ids = {} #EMPTY DICTIONARY
        y_labels = []
        x_train = []
        ctypes.windll.user32.MessageBoxW(0, "    Training in progress please wait.....", "In progress...", 0)
        for root, dirs, files in os.walk(image_dir):
                for file in files:
                        if file.endswith("png") or file.endswith("jpg") or file.endswith("pgm") :
                                path = os.path.join(root, file)
                                label = os.path.basename(os.path.dirname(path)).replace(" ","-").lower()
                                #print(label, path)
                                if not label in label_ids:
                                        label_ids[label] = current_id
                                        current_id += 1
                                id_ = label_ids[label]
                                #print(label_ids)
                                #y_labels.append(label)
                                #x_train.append(path)
                                 
                                #convert to grayscale
                                pil_image = Image.open(path).convert("L")
                                size = (550,550)
                                final_image = pil_image.resize(size, Image.ANTIALIAS)
                                #create a numpy array
                                image_array = np.array(pil_image, "uint8")
                                #print(image_array)
                                faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.5, minNeighbors=5)
                                
                                #determine the region of interest
                                for(x, y, w, h) in faces:
                                        roi = image_array[y:y+h, x:x+w]
                                        x_train.append(roi)
                                        y_labels.append(id_)
                                                
        #print (y_labels)
        #print(x_train)

        with open("labels.pickle", "wb") as f:
                pickle.dump(label_ids, f)
                
        # Train the data	
        recognizer.train(x_train, np.array(y_labels))
        # Save the tranined data
        recognizer.save("trainner.yml")
        # Prints the time it takes to finish running
        ctypes.windll.user32.MessageBoxW(0, "    Training finished! %s seconds." % (time.time() - start_time), "Success!", 0)


