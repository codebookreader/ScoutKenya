from ultralytics import YOLO 

model = YOLO('yolov8x')  # load a pretrained model (recommended for training)

results = model.predict(r'C:\Users\USER\.vscode\ScoutKenya\football_analysis-main\input_videos\Untitled video 10 - Made with Clipchamp.mp4', save=True)
print(results[0])
print('=====================================')
for box in results[0].boxes:
    print(box)