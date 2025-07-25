import cv2
import os
import threading
import time

# 保存先ディレクトリ
# カスケード分類器の読み込み
class Recorder:
    def __init__(self, output_dir="recordings"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        self.recording = False
        self.thread = None
        self.cap = None
        self.out = None
        self.output_file = None

# 開始
    def start(self):
        if self.recording:
            print("[INFO] 録画はすでに開始されています。")
            return
        # カメラ起動
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[ERROR] カメラを開くのに失敗しました。")
            self.cap = None
            return
        # 毎回新しいファイル名で保存 保存先指定
        self.output_file = os.path.join(self.output_dir, f"recording_{int(time.time())}.avi")
        # VideoWriterオブジェクトの作成
        # fourcc = cv2.VideoWriter_fourcc(*"XVID") = MPEG-4
        # fourcc = cv2.VideoWriter_fourcc(*"mp4v") = mp4
        # fourccとはFourCC (Four Character Code)の略
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (frame_width, frame_height))
        print(f"[INFO] 録画開始。保存先: {self.output_file}")
        self.recording = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

# 停止
    def stop(self):
        if not self.recording:
            print("[INFO] 録画は開始されていません。")
            return
        print("[INFO] 録画を停止します。")
        # _recordのwhileを終了させる
        self.recording = False
        # self.threadが存在し、かつスレッドが生きている時だけjoin()を呼ぶ
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.out:
            self.out.release()
            self.out = None
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
        print("[INFO] リソースを開放しました。")

    def _record(self):
        print("[INFO] 録画スレッドが開始されました。")
        while self.recording and self.cap and self.out.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] フレームが取得できません。")
                break
            # グレースケール変換
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 顔を検出。 1.1：スケールファクター、3：最小顔検出
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 3)
            if len(faces) > 0:
                self.out.write(frame)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.imshow("顔認識録画", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.recording = False
                break
        print("[INFO] 録画スレッドが終了しました。")