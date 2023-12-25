from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import cv2
import numpy as np
import io

# Set your Azure Blob Storage connection string
connection_string = "DefaultEndpointsProtocol=https;AccountName=varshethadata;AccountKey=y53L9/fZGZGu+jE+heVzVCT1WC7NNgGud9K66yId6zyYDxOHR932GPZqmyDAmIJhs+VKlAE6SXsU+AStaQsOoQ==;EndpointSuffix=core.windows.net"

# Set the name of the container where your images are stored
container_name = "varshethadc"

# Initialize the BlobServiceClient using the connection string
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get a reference to the container
container_client = blob_service_client.get_container_client(container_name)

# List the blobs (images) in the container
blob_list = container_client.list_blobs()

# Loop through the blobs, download and display using cv2 without saving to a file
for blob in blob_list:
    blob_client = container_client.get_blob_client(blob.name)

    # Download the blob's data
    download_stream = blob_client.download_blob()
    image_data = download_stream.readall()

    # Convert the image data to a NumPy array
    nparr = np.frombuffer(image_data, np.uint8)

    # Decode the image using OpenCV
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Display the image using cv2
    cv2.imshow("Azure Blob Image", image)
    cv2.waitKey(0)

# Close the OpenCV window
cv2.destroyAllWindows()
