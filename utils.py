from firebase_admin import storage, initialize_app, credentials
import config
# utility functions


async def upload_to_cloud(file):
    """
    Handler to upload files to cloud storage.
    """
    credential_object = credentials.Certificate('./credentials.json')
    initialize_app(credential=credential_object, options={'storageBucket': 'mom-bot-f9dd8.appspot.com'})
    bucket = storage.bucket()
    audioFile = bucket.blob("test.wav")
    try:
        audioFile.upload_from_file(file)
    except:
        print("Error occured while uploading file to cloud.")
