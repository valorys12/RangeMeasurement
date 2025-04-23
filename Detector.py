import cv2, time, os, tensorflow as tf
import numpy as np
from tensorflow.python.keras.utils.data_utils import get_file
from cvzone.FaceMeshModule import FaceMeshDetector
import pyttsx3
from threading import Thread
import time

np.random.seed(123)

class Detector:
    
    def __init__(self):
        self.classesList = None
        self.colorList = None
        self.model = None
        self.modelName = ""
        self.faceMesh = FaceMeshDetector(maxFaces=1)
        self.focalLength = 1600
        self.realFaceWidth = 6.3
        self.distance = 0.0
        self.ttsEngine = pyttsx3.init()
        self.voices = self.ttsEngine.getProperty('voices')
        self.ttsEngine.setProperty('voice', self.voices[1].id)

    
    def play_warning(self, engine, message):
        engine.say(message)
        engine.runAndWait()
    
    def readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classesList = f.read().splitlines()
        
        # Colors for each class
        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList), 3))
        print(f"Total classes: {len(self.classesList)}")
    
    def downloadModel(self, modelURL):
        fileName = os.path.basename(modelURL)
        self.modelName = fileName[:fileName.index('.')]  # Remove extension
        
        self.cacheDir = "./pretrained_models"
        os.makedirs(self.cacheDir, exist_ok=True)

        print(f"Downloading {modelURL}...")
        get_file(fname=fileName,
                origin=modelURL,
                cache_dir=self.cacheDir,
                cache_subdir="",
                extract=True)
        
        print("Download complete.")
    
    def loadModel(self):
        print(f"Loading model {self.modelName}...")
        tf.keras.backend.clear_session()
        modelPath = os.path.join(self.cacheDir, self.modelName, "saved_model")
        
        if not os.path.exists(modelPath):
            raise Exception(f"Model not found at {modelPath}")
            
        self.model = tf.saved_model.load(modelPath)
        print("Model loaded successfully.")
    
    def createBoundingBox(self, image, threshold=0.5):
        if self.model is None:
            raise Exception("Model not loaded")
            
        inputTensor = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
        inputTensor = tf.convert_to_tensor(inputTensor, dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis,...]
        
        detections = self.model(inputTensor)
        
        bboxs = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()
        
        imH, imW, _ = image.shape
        bboxIdx = tf.image.non_max_suppression(bboxs, classScores, 
                                            max_output_size=50,
                                            iou_threshold=0.5,
                                            score_threshold=threshold)
        
        # Dictionary referensi objek (kalibrasi sesuai kebutuhan Anda)
        REFERENCE_SIZES = {
            "person": {"type": "height", "ref_px": 500, "ref_distance": 1.0},
            "car": {"type": "width", "ref_px": 300, "ref_distance": 1.0},
            # Tambahkan objek lain sesuai kebutuhan
            "default": {"type": "width", "ref_px": 200, "ref_distance": 1.0}
        }
        
        if len(bboxIdx) != 0:
            for i in bboxIdx:
                bbox = tuple(bboxs[i].tolist())
                classIndex = classIndexes[i]
                
                if classIndex >= len(self.classesList):
                    continue
                    
                classLabelText = self.classesList[classIndex]
                classColor = self.colorList[classIndex]
                
                ymin, xmin, ymax, xmax = bbox
                
                # Convert to pixel coordinates
                xmin_px, xmax_px = int(xmin * imW), int(xmax * imW)
                ymin_px, ymax_px = int(ymin * imH), int(ymax * imH)
                
                # Calculate bounding box dimensions
                bbox_width = xmax_px - xmin_px
                bbox_height = ymax_px - ymin_px
                
                # Initialize default distance
                
                distance_text = "N/A"
                warning_text = ""
                # Get reference data for the detected object
                imgForFace, faces = self.faceMesh.findFaceMesh(image.copy(), draw=False)

                if faces:
                    face = faces[0]
                    pointLeft = face[145]
                    pointRight = face[374]
                    w, _ = self.faceMesh.findDistance(pointLeft, pointRight)
                    
                    try:
                        self.distance = (self.realFaceWidth * self.focalLength) / w
                        distance_text = f"{self.distance / 100:.2f}m"
                        
                        if self.distance <= 100:
                            warning_text = f"Warning: {classLabelText} Is Too Close"
                            # Draw the warning text on the image at a position relative to the bounding box
                            cv2.putText(image, warning_text, (xmin_px, ymin_px - 40),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            if not hasattr(self, 'sound_thread') or not self.sound_thread.is_alive():
                                warning_message = f"Warning: {classLabelText} is too close"
                                self.sound_thread = Thread(target=self.play_warning, args=(self.ttsEngine, warning_message))
                                self.sound_thread.start()
                            
                    except ZeroDivisionError:
                        distance_text = "N/A"
                else:
                    distance_text = "N/A"
                
                displayText = f'{classLabelText}: {distance_text}'
                
                # Draw rectangle and text
                cv2.rectangle(image, (xmin_px, ymin_px), (xmax_px, ymax_px), 
                            color=classColor, thickness=2)
                cv2.putText(image, displayText, (xmin_px, ymin_px-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, classColor, 2)

        return image
    
    def predictVideo(self, videoPath, threshold=0.5):
        if isinstance(videoPath, int):
            print("Using webcam in FULLSCREEN mode...")
        else:
            print(f"Processing video: {videoPath}")
        
        cap = cv2.VideoCapture(videoPath)
        
        # Set resolusi maksimal webcam (sesuaikan dengan kemampuan webcam)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        if not cap.isOpened():
            raise Exception("Error opening video stream or file")
        
        # Buat window fullscreen
        cv2.namedWindow("Object Detection", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Object Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    if videoPath == 0:
                        continue  # Keep trying for webcam
                    else:
                        break  # End of video file
                
                # Dapatkan ukuran layar
                screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Resize frame ke ukuran layar (jika perlu)
                frame = cv2.resize(frame, (screen_width, screen_height))
                
                # Process frame
                processedFrame = self.createBoundingBox(frame, threshold)

                # Tampilkan frame fullscreen
                cv2.imshow("Object Detection", processedFrame)
                
                # Exit dengan tombol ESC
                if cv2.waitKey(1) == 27:  # 27 adalah kode tombol ESC
                    break
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()
                    
