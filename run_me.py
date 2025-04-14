from Detector import *

# Configuration
modelURL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
classFile = "coco.names"
threshold = 0.5
videoPath = 0  # 0 for webcam

# Initialize detector
detector = Detector()

try:
    # Load classes
    detector.readClasses(classFile)
    
    # Download and load model
    detector.downloadModel(modelURL)
    detector.loadModel()
    
    # Start detection
    print("Starting webcam detection... Press 'q' to quit.")
    detector.predictVideo(videoPath, threshold)
    
except Exception as e:
    print(f"Error: {str(e)}")