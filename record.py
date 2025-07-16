import cv2
import os

# 保存先ディレクトリ
output_dir = "recordings"
os.makedirs(output_dir, exist_ok=True)

# カスケード分類器の読み込み
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# カメラ起動
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("カメラが開けません。")
    exit()

# fourcc = cv2.VideoWriter_fourcc(*"XVID") = MPEG-4
# fourcc = cv2.VideoWriter_fourcc(*"mp4v") = mp4
# fourccとはFourCC (Four Character Code)の略
fourcc = cv2.VideoWriter_fourcc(*"XVID")
# 保存先指定
output_file = os.path.join(output_dir, "output.avi")
# VideoWriterオブジェクトの作成
out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))
print(f"'q'キーで録画を停止します。")

while True:
    ret, frame = cap.read()
    if not ret:
        print("フレームが取得できません。")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)

    if len(faces) > 0:
        out.write(frame) # フレームを保存
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # 描画
    cv2.imshow("顔認識録画", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
print(f"録画完了。保存先: {output_file}")