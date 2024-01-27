from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# Nome do arquivo de vídeo MP4
video_file_path = r'C:\Users\daniel.cosmo\Documents\Codes\Python\Celanese\1. camera_simulator\bucket_360.mp4'  # Substitua pelo caminho correto do seu vídeo

# Abre o arquivo de vídeo usando OpenCV
cap = cv2.VideoCapture(video_file_path)

# Verifica se o arquivo foi aberto corretamente
if not cap.isOpened():
    print(f"Erro ao abrir o arquivo de vídeo MP4: {video_file_path}")
    exit()

def generate_frames():
    while True:
        # Lê um frame do vídeo
        ret, frame = cap.read()

        # Verifica se o vídeo chegou ao final e reinicia se necessário
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Converte o frame para um formato JPEG (pode ser otimizado conforme necessário)
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Retorna o frame como uma resposta HTTP multipart
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
