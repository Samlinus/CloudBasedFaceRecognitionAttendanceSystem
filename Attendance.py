import os
from datetime import datetime

import cv2
import face_recognition
import numpy as np
import pandas as pd
from azure.storage.blob import BlobServiceClient


class Azure:
    def __init__(self):
        self.connectionString = ("DefaultEndpointsProtocol=https;AccountName=varshethadata;AccountKey=y53L9/fZGZGu+jE"
                                 "+heVzVCT1WC7NNgGud9K66yId6zyYDxOHR932GPZqmyDAmIJhs+VKlAE6SXsU+AStaQsOoQ"
                                 "==;EndpointSuffix=core.windows.net")
        self.containerName = 'varshethadc'

    def retrieveImages(self):
        blob_service_client = BlobServiceClient.from_connection_string(self.connectionString)

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(self.containerName)

        # List the blobs (images) in the container
        blob_list = container_client.list_blobs()
        imageList = []
        nameList = []
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
            imageList.append(image)
            nameList.append(os.path.splitext(blob.name)[0])

        return imageList, nameList


class ImageClassify:
    def __init__(self):
        self.azure = Azure()
        self.fileName = 'Attendance' + str(datetime.now().date())
        self.path = 'Images'
        self.images = []
        self.classNames = []
        self.myList = os.listdir(self.path)  # to get the list of images

    def importImages(self):
        try:
            self.images, self.classNames = self.azure.retrieveImages()
        except Exception:
            print('Error in downloading images...')
        print('Successfully downloaded the images...')

    def fit(self):
        self.importImages()
        self.encodeListKnown = self.findEncodings(self.images)
        self.setDf()
        self.capture()

    def setDf(self):
        self.df = {
            'Name': self.classNames,
            'Status': ['Absent'] * len(self.classNames)
        }
        self.df = pd.DataFrame(self.df)

    def capture(self):
        print('Capturing image..')
        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Webcam', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Webcam', 800, 600)
        while True:

            success, img = cap.read()
            imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # 1/4th of the size
            img = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)
            # There might be multiple faces in the webcam
            # Find the location of the face in webcam
            faceCurrFrame = face_recognition.face_locations(imgSmall)
            encodeCurrFrame = face_recognition.face_encodings(img, faceCurrFrame)

            # Now find the matching faces...
            for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
                # 1 value will be taken at a time in each list
                # Compare captured with the faces.
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                print(f'Face distance: {faceDis}')
                print(f'matches: {matches}')
                # Returns index of the minimum face distance...
                matchIndex = np.argmin(faceDis)
                # Now simply display the image with this index.
                if matches[matchIndex]:
                    # Name of the image...
                    name = self.classNames[matchIndex]
                    # If the name is found and is not empty....
                    # Then mark it as present
                    if name:
                        self.df.loc[self.df['Name'] == name, 'Status'] = 'Present'
                    print(name)
                    y1, x2, y2, x1 = faceLoc
                    cv2.rectangle(img, (x1, y2), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2)

                else:
                    print('Doesnt match')

            cv2.imshow('Webcam', img)
            key = cv2.waitKey(1)
            if key == 27 or key == ord('q'):
                # Save the csv file
                self.df.to_csv(f'{self.fileName}.csv', index=False)
                print('File saved successfully..')
                break

        cv2.destroyAllWindows()
        print(self.df)

    def findEncodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)

        return encodeList


model = ImageClassify()
model.fit()
