import requests
import os
from xml.etree import ElementTree

class UploaderError(Exception):
    pass

class InvalidCredentialsError(UploaderError):
    pass

class APIError(UploaderError):
    pass

def upload(filename: str, file: bytes, max_size: int = 1, auth_token: str = None, x_api_key: str = None):
    """
    Uploads a file to the Datallog service using a presigned URL.

    The function first requests a presigned upload URL from the Datallog backend,
    providing the filename and the maximum allowed file size. It then performs a POST
    directly to the storage endpoint (S3 or similar) using the returned data. 
    The uploaded file will be accessible via the returned URL for one month.

    Args:
        filename (str): Name of the file to be uploaded.
        file (bytes): File content in bytes.
        max_size (int, optional): Maximum allowed file size in MB. Default is 1.
        auth_token (str, optional): User authorization token. If not provided,
            the environment variable 'datallog_user_auth_token' will be used.
        x_api_key (str, optional): API key for authentication. If not provided,
            the environment variable 'datallog_x_api_key' will be used.

    Raises:
        InvalidCredentialsError: If authorization or API key credentials are missing or invalid.
        APIError: If the request to the API fails for any reason.

    Returns:
        str: URL where the file will be accessible for one month after upload.
    """
    #Loads tokens
    uploader_authorization = auth_token or os.getenv('datallog_user_auth_token')
    uploader_x_api_key = x_api_key or os.getenv('datallog_x_api_key')
    if not uploader_authorization or not uploader_x_api_key:
        raise InvalidCredentialsError("Missing or invalid uploader credentials")
    payload = {
            "filename": filename,
            "max_size": max_size
        }
    headers = {
        "Authorization": f"{uploader_authorization}",
        "X-Api-Key": uploader_x_api_key
    }
    # Get presigned url
    try:
        response = requests.post('https://api-mwm.datallog.com/api/utils/uploader/get-presigned-url', headers=headers, json=payload)
        presigned_data = response.json()
        if 'message' in presigned_data:
            if presigned_data['message'] == "Forbidden":
                raise InvalidCredentialsError("Invalid uploader credentials")
        response.raise_for_status()
    except Exception as e:
        raise APIError(f"Failed to get presigned URL: {e}") from e
    presigned_post = presigned_data.get("presigned_post")

    # Upload to storage
    files = {"file": (filename, file)}
    try:
        post_response = requests.post(
            presigned_post["url"],
            data=presigned_post["fields"],
            files=files
        )
        post_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        code = None
        try:
            root = ElementTree.fromstring(post_response.text)
            code_elem = root.find("Code")
            if code_elem is not None:
                code = code_elem.text
        except Exception:
            pass 

        if code == "EntityTooLarge":
            raise APIError(
                    f"File upload failed: file is too large ({len(file)} bytes). "
                    f"Maximum allowed size: {max_size * 1024 * 1024} bytes ({max_size} MB). "
                    f"Please update your max_size parameter in your uploader.upload function call."
                )
        else:
            raise APIError(f"File upload failed: {e}") from e

    return presigned_data.get('cloudfront_url')
