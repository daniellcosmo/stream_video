import requests
import cv2
import numpy as np
import imageio
import os
import time
import tempfile
from azure.storage.blob import BlobServiceClient
from datetime import datetime

def captura_frames_azure(output_folder='videos', max_duration_seconds=15, fps=10):
    # Configurações do Azure Blob Storage
    connection_string = "DefaultEndpointsProtocol=https;AccountName=azurestorageaccountiot;AccountKey=VC9uZhEdv83uNWIWV0jcnOTiYHUBwDW4k8W4nsFO92C81JgekSrFGvpUPXgIa2QxYzs5G6rZJDeV+ASt6T11vw==;EndpointSuffix=core.windows.net"
    container_name = "data"
    video_server_ip='http://192.168.0.9:5000/video_feed'
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Nome do arquivo de vídeo
    start_time = time.time()
    microseconds = int((start_time - int(start_time)) * 1e6)
    video_filename = f'video_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{microseconds}.mp4'

    # Inicializa o objeto VideoWriter para escrever o vídeo
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
        video_writer = imageio.get_writer(temp_video.name, fps=fps)

        try:
            response = requests.get(video_server_ip, stream=True, timeout=(5, None))
            response.raise_for_status()

            while True:
                # Lê o próximo frame do stream
                byte_frame = bytes()
                for chunk in response.iter_content(chunk_size=1024):
                    byte_frame += chunk
                    a = byte_frame.find(b'\xff\xd8')
                    b = byte_frame.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = byte_frame[a:b+2]
                        byte_frame = byte_frame[b+2:]
                        
                        # Usando cv2.imdecode para garantir que o frame seja decodificado corretamente
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                        # Converte BGR para RGB
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        # Adiciona o frame ao vídeo
                        video_writer.append_data(frame)

                        # Aguarda o tempo necessário para atingir a taxa desejada de quadros por segundo
                        time.sleep(1 / fps)

                        # Verifica se atingiu a duração máxima
                        elapsed_time = time.time() - start_time
                        if elapsed_time >= max_duration_seconds:
                            break

                # Verifica se atingiu a duração máxima
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_duration_seconds:
                    break

            # Fecha a resposta HTTP
            response.close()

        except requests.exceptions.RequestException as req_error:
            if req_error.response is not None and len(req_error.response.content) > 0:
                # Imprime a mensagem de erro apenas se houver conteúdo na resposta
                print(f"Erro na solicitação HTTP: {req_error}")
                print(f"Response content: {req_error.response.content.decode()}")

        except Exception as e:
            print(f"Outro erro: {e}")

        finally:
            # Fecha o objeto VideoWriter
            video_writer.close()

            # # Faz o upload para o Azure Blob Storage
            # blob_client = blob_service_client.get_blob_client(container=container_name, blob=os.path.join(output_folder, video_filename))
            # with open(temp_video.name, "rb") as data:
            #     blob_client.upload_blob(data)

            # # Cria a pasta "videos" se ela não existir
            # os.makedirs(output_folder, exist_ok=True)
            # Caminho para o diretório local onde você deseja salvar o arquivo
            diretorio_local = "videos/"
            arquivo_local = os.path.join(diretorio_local, video_filename)

            # Faz o salvamento local
            with open(temp_video.name, "rb") as origem, open(arquivo_local, "wb") as destino:
                destino.write(origem.read())


            print("Captura de frames concluída. Video salvo no Azure Blob Storage.")
            print(video_filename)

# Exemplo de chamada da função
captura_frames_azure(output_folder='videos', max_duration_seconds=5, fps=10)
