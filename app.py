import os
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask import send_from_directory
from record import Recorder
from flask_wtf.csrf import CSRFProtect

load_dotenv()
recorder = Recorder()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CSRF保護有効化
csrf = CSRFProtect(app)

# DBモデル
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# ルーティング
@app.route('/')
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # パスワードをハッシュ化して保存
        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            # セッション固定攻撃対策
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            return "ログインに失敗しました。"
    return render_template("login.html")

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ダッシュボード（録画制御ボタンあり）
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    # return f"ログイン中のユーザーID: {session["user_id"]}"
    return render_template("dashboard.html", user_id=session["user_id"])

# 録画ファイル一覧表示
@app.route("/recordings")
def recordings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    files = os.listdir("recordings")
    return render_template("recordings.html", files=files)

# 録画ファイルダウンロード
@app.route("/recordings/<filename>")
def download_file(filename):
    if "user_id" not in session:
        return redirect(url_for("login"))
    # send_from_directory パスインジェクション対策になる
    return send_from_directory ("recordings", filename, as_attachment=True)

# 録画開始（POST）
@app.route("/start_recording", methods=["POST"])
def start_recording():
    if "user_id" not in session:
        return jsonify({"message": "ログインが必要です。"}), 401
    if recorder.recording:
        return jsonify({"message": "録画はすでに開始されています。"}), 400
    recorder.start()
    return jsonify({"message": "録画を開始しました。"}), 200

# 録画停止（POST）
@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    if "user_id" not in session:
        return jsonify({"message": "ログインが必要です。"}), 401
    if not recorder.recording:
        return jsonify({"message": "録画は開始されていません。"}), 400
    recorder.stop()
    return jsonify({"message": "録画を停止しました。"}), 200

#  録画ステータス取得
@app.route("/recording_status")
def recording_status():
    if "user_id" not in session:
        return jsonify({"message": "ログインが必要です。"}), 401
    # Recorderクラスのrecording属性を参照している
    return jsonify({"recording": recorder.recording}), 200


if __name__ == "__main__":
    # 初期DB作成
    with app.app_context():
        db.create_all()
    app.run(debug=True)