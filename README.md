# 🚦 Smart Traffic Signal Management System (TLMS)

An **AI-powered traffic management system** that uses **YOLO + OpenCV** for real-time vehicle detection, lane-wise counting, and intelligent traffic signal control. The system adapts signal timings based on vehicle density and can detect violations such as **no helmet, no seatbelt, and wrong-way driving**.

---

## ✨ Features

* Real-time vehicle detection using **YOLOv3**
* Lane-wise vehicle counting (2-wheeler & 4-wheeler)
* Adaptive traffic light control based on density
* Violation detection:

  * 🚫 No helmet
  * 🚫 No seatbelt
  * 🚫 Wrong-way driving
* Dashboard-ready logs for monitoring & analysis

---

## ⚙️ Setup Instructions

1. **Clone this repo**

   ```bash
   git clone https://github.com/nyx73/TLMS-.git
   cd TLMS-
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Download YOLOv3 pretrained weights & config**

   * [yolov3.weights](https://pjreddie.com/media/files/yolov3.weights)
   * [yolov3.cfg](https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg)
   * [coco.names](https://github.com/pjreddie/darknet/blob/master/data/coco.names)

   Place these files in the project folder.

4. **Add a traffic video**
   Save a video named `traffic.mp4` in the project root folder.

5. **Run the project**

   ```bash
   python traffic_data.py
   ```

---

## 📊 Future Enhancements

* Integration with **SUMO/CityFlow** for simulation
* Reinforcement Learning–based adaptive control
* Real-time violation challan system

---

## 📸 Demo

# Home Page
<img width="720" height="720" alt="Screenshot 2025-09-04 112942" src="https://github.com/user-attachments/assets/ae454773-c003-491e-aa2f-d404c66c738a" />

# Login Page
<img width="720" height="720" alt="Screenshot 2025-09-04 113012" src="https://github.com/user-attachments/assets/6c43a6c1-ca20-4076-9626-a162eed66f68" />

# Select Location 
<img width="1020" height="1020" alt="Screenshot 2025-09-04 113023" src="https://github.com/user-attachments/assets/42e4878c-1fac-4315-bbba-1ec79d344a05" />

# Dashboard
<img width="1920" height="1080" alt="Screenshot 2025-09-04 113039" src="https://github.com/user-attachments/assets/38ef82cd-630d-46ba-81d2-1c84654cce33" />

<img width="1553" height="622" alt="Screenshot 2025-09-04 113123" src="https://github.com/user-attachments/assets/036ffd4b-4adb-47f2-ae88-022284d5c7ab" />

# Challan 
<img width="1671" height="608" alt="Screenshot 2025-09-04 113137" src="https://github.com/user-attachments/assets/e61308c4-9efe-4b83-b8ad-80442bd54089" />

# Generated Challan
<img width="870" height="1013" alt="Screenshot 2025-09-04 113309" src="https://github.com/user-attachments/assets/4b3cc489-44ab-4c15-ae27-fee07850d916" />

# Payment of Challan
<img width="786" height="1017" alt="Screenshot 2025-09-04 113227" src="https://github.com/user-attachments/assets/3472ea74-355e-4039-b261-909c67a476f1" />

---

## 🛠 Tech Stack

* Python
* OpenCV
* YOLOv3 (Deep Learning Object Detection)

---

