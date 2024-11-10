import argparse
import json

from ultralytics import YOLO

model = YOLO('yolov8n.pt')

def predict(img_path, filename):
    results = model(img_path)
    boxes = results[0].boxes.xyxy.tolist()
    classes = results[0].boxes.cls.tolist()
    names = results[0].names
    # if names[2] == "car":
    #    names[2] = "vehicle"
    confidences = results[0].boxes.conf.tolist()

    prediction_result = []

    for box, cls, conf in zip(boxes, classes, confidences):
        x1, y1, x2, y2 = box
        confidence = conf
        name = names[int(cls)]
        if conf > 0.50:
            #print(f"{name} [{x1} {y1} {x2} {y2}]")
            prediction_result.append(
                {
                    "type": {"id": name, "xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2}
                }
            )

    with open(filename, "w") as file:
        file.write(json.dumps(prediction_result))
        file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Object Detection Prediction')
    parser.add_argument('--img_path', type=str, required=True, help='Path to the input image')
    parser.add_argument('--export_path', type=str, required=True, help='Path to the output json')
    args = parser.parse_args()
    predict(args.img_path, args.export_path)
