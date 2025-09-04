import cv2
import numpy as np

# Load YOLOv3 pre-trained model (make sure you have yolov3.cfg and yolov3.weights)
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Define lanes (adjust according to your video resolution)
LANE_BOUNDS = {
    "Lane 1": (0, 200),    # x range
    "Lane 2": (200, 400),
    "Lane 3": (400, 600),
    "Lane 4": (600, 800)
}

# Start video capture
cap = cv2.VideoCapture("traffic.mp4")

vehicle_counts = {"Lane 1": 0, "Lane 2": 0, "Lane 3": 0, "Lane 4": 0}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape

    # Prepare input for YOLO
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0,0,0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Process detections
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            # Detect only cars, trucks, buses, motorbikes
            if class_id in [2, 3, 5, 7] and confidence > 0.5:
                # Get bounding box
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Draw rectangle
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)

                # Determine lane by x position
                for lane, (xmin, xmax) in LANE_BOUNDS.items():
                    if xmin <= center_x < xmax:
                        vehicle_counts[lane] += 1
                        cv2.putText(frame, lane, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
                        break

    # Show lane dividers
    for _, (xmin, xmax) in LANE_BOUNDS.items():
        cv2.line(frame, (xmin, 0), (xmin, height), (255,0,0), 2)

    # Display counts
    y_offset = 30
    for lane, count in vehicle_counts.items():
        cv2.putText(frame, f"{lane}: {count}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
        y_offset += 30

    # Show video
    cv2.imshow("Traffic Lane Detection", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
