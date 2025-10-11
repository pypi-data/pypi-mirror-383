import requests
import os

class UploaderError(Exception):
    pass

class InvalidCredentialsError(UploaderError):
    pass

class Uploader:
    def __init__(self):
        pass

    def upload(self, filename: str, file: bytes, max_size: int = 1, authorization: str = None, x_api_key: str = None):
        payload = {
                "filename": filename,
                "max_size": max_size
            }
        uploader_authorization = authorization or os.getenv('datallog_user_auth_token')
        uploader_x_api_key = x_api_key or os.getenv('datallog_x_api_key')
        if not authorization or not x_api_key:
            raise InvalidCredentialsError("Missing or invalid uploader credentials")
        headers = {
            "Authorization": f"Token {uploader_authorization}",
            "X-Api-Key": uploader_x_api_key
        }
        response = requests.post('https://testuploader.requestcatcher.com/', headers=headers, json=payload)
        presigned_data = response.json()
        presigned_post = presigned_data["presigned_post"]
        files = {"file": (filename, file)}
        post_response = requests.post(presigned_post["url"], data=presigned_post["fields"], files=files)
        return presigned_data['cloudfront_url']

