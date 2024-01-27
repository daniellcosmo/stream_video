from azure.storage.blob import BlobServiceClient
from datetime import datetime
import time
import sys

def apagar_blobs(blob_service_client, container_name):
    container_client = blob_service_client.get_container_client(container_name)

    # Nome do arquivo de saída
    start_time = time.time()
    microseconds = int((start_time - int(start_time)) * 1e6)
    output_file = f'blobs_apagados_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{microseconds}.txt'

    # Lista todos os blobs no contêiner
    blobs = container_client.list_blobs()

    with open(output_file, 'w') as f:
        # Redireciona a saída padrão para o arquivo
        original_stdout = sys.stdout
        sys.stdout = f

        # Apaga cada blob individualmente
        for blob in blobs:
            container_client.delete_blob(blob.name)
            print(f'Blob {blob.name} apagado com sucesso.')

        # Restaura a saída padrão
        sys.stdout = original_stdout




# Configurações do Azure Blob Storage
connection_string = "DefaultEndpointsProtocol=https;AccountName=azurestorageaccountiot;AccountKey=VC9uZhEdv83uNWIWV0jcnOTiYHUBwDW4k8W4nsFO92C81JgekSrFGvpUPXgIa2QxYzs5G6rZJDeV+ASt6T11vw==;EndpointSuffix=core.windows.net"
container_name = "data"

# Configuração do Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Chama a função para apagar os blobs
apagar_blobs(blob_service_client, container_name)