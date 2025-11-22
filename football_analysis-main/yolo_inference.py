from ultralytics import YOLO 

model = YOLO('models/best.pt')  # load a pretrained model (recommended for training)

results = model.predict(r'C:\Users\USER\.vscode\ScoutKenya\football_analysis-main\input_videos\Untitled video 13 -2 - Made with Clipchamp.mp4', save=True)
print(results[0])
print('=====================================')
for box in results[0].boxes:
    print(box)