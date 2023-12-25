from azure.storage.blob import BlobServiceClient
import os

accountKey = "y53L9/fZGZGu+jE+heVzVCT1WC7NNgGud9K66yId6zyYDxOHR932GPZqmyDAmIJhs+VKlAE6SXsU+AStaQsOoQ=="
accountName = "varshethadata"
connectionString =  "DefaultEndpointsProtocol=https;AccountName=varshethadata;AccountKey=y53L9/fZGZGu+jE+heVzVCT1WC7NNgGud9K66yId6zyYDxOHR932GPZqmyDAmIJhs+VKlAE6SXsU+AStaQsOoQ==;EndpointSuffix=core.windows.net"
containerName = "varshethadc"

def upload(filePath,fileName):
    blob_service_client = BlobServiceClient.from_connection_string(connectionString)
    blob_client =  blob_service_client.get_blob_client(container = containerName,blob = fileName)
    with open(filePath,"rb") as data:
        blob_client.upload_blob(data)

    print(f'uploaded {fileName}')


upload(f'E:\\CloudPackage\\Images\\Anu.jpg', 'Anu.jpg')

