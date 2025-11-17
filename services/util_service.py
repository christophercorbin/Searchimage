import os
import requests
import base64
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import hashlib
import logging
from config import Config
import pycountry
import numpy as np
from numpy.linalg import norm
from urllib.parse import urlparse, urljoin
import mimetypes
from datetime import datetime
from urllib.parse import urlparse, unquote
import re
import json

BASE_FILEPATH = os.path.dirname(os.path.realpath(__file__)) # get the directory of current file

class UtilService():
    __configs = Config.get()
    __logger = logging.getLogger(__configs.LOGGER_NAME_UTIL_SERVICE)
    __pillow_image_formats = Image.registered_extensions()
    __supported_image_ext = list(__pillow_image_formats.keys())
    __web_image_request_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'
    }

    @staticmethod
    def download_user_image(src_path, dst_dir) -> str:
        '''
        Download user provided image from the source path and save it to the destination directory

        :param src_path: the source path of the image
        :param dst_dir: the destination directory to save the image
        :return: the path of the downloaded image
        '''
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        if src_path is None or len(src_path) < 7:
            # invalid source path
            return ''

        # Download the image by mimicing request from browser
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = ''
        try:
            response = requests.get(src_path, headers=UtilService.__web_image_request_headers)
        except Exception as e:
            UtilService.__logger.error(f"failed to download image from: {src_path}, with error: {e}")
            return ''

        # Check if response.content is a base64 encoded string
        if response.text.startswith('data:image'):
            try:
                # Find and decode the base64 data
                base64_data = response.text.split(',', 1)[1]
                byte_data = base64.b64decode(base64_data)

                # Open the image
                image = Image.open(BytesIO(byte_data))
            except Exception as e:
                UtilService.__logger.error(f"downloaded image is invalid: {src_path}, with error: {e}")
                return ''
        else:
            try:
                # Try to open the image
                image = Image.open(BytesIO(response.content))
            except UnidentifiedImageError:
                UtilService.__logger.error(f"downloaded image is invalid: {src_path}")
                return ''

        image_path = os.path.join(dst_dir, os.path.basename(src_path))

        # check if the source path contains a valid extension, if not, append default extension
        filepath, ext = os.path.splitext(image_path)
        if ext not in UtilService.__supported_image_ext:
            UtilService.__logger.warning(f'original image url: {src_path} has unsupported extension: {ext}, using .jpg as the default')
            image_path = filepath + '.jpg'
        
        # Save the image in a temporarily destination folder
        try:
            if image.mode == 'RGBA':
                # PIL librarcy cannot save Transparency "A" into JPEG, convert to RGB first
                image = image.convert('RGB')
            image.save(image_path)
            image.close()
        except Exception as e:
            UtilService.__logger.error(f"Failed to safe image: {src_path}, reason: {e}")
            return ''

        return image_path
    
    @staticmethod
    def hash_file(file_path):
        # make a hash object with sha512
        h = hashlib.sha512()

        # open file for reading in binary mode
        with open(file_path,'rb') as file:
            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)
        
        return h.hexdigest()
    
    @staticmethod
    def get_country_code(country_name):
        try:
            country = pycountry.countries.get(name=country_name)
            if country:
                return country.alpha_2
        except LookupError:
            pass
        
        return 'US'
    
    @staticmethod
    def get_user_country_code(address):
        if address and isinstance(address, dict) and address.get('country'):
            return UtilService.get_country_code(address.get('country'))
        
        # TODO: support address format when it's a string

        return 'US'

    
    @staticmethod
    def find_cosine_similarity(source_representation, test_representation):
        # modified from Deepface's findCosineDistance
        a = np.matmul(np.transpose(source_representation), test_representation)
        b = np.sum(np.multiply(source_representation, source_representation))
        c = np.sum(np.multiply(test_representation, test_representation))
        return a / (np.sqrt(b) * np.sqrt(c))
    
    @staticmethod
    def find_cosine_distance(source_representation, test_representation):
        return 1 - UtilService.find_cosine_similarity(source_representation, test_representation)
    

    @staticmethod
    def generate_web_image_filename(url) -> str:
        # Parse the URL to extract the filename and extension which should be the last part of the path, after the last slash
        # Parse the URL
        parsed_url = urlparse(url)
        path = parsed_url.path

        # Handle URLs with fragments
        if parsed_url.fragment:
            fragment_parts = parsed_url.fragment.split('/media/')
            filename = fragment_parts[-1]
        else:
            filename = path.split('/')[-1]

        # Remove query parameters
        filename = filename.split('?')[0]

        # URL-decode the filename
        filename = unquote(filename)

        # if there is no extension, append .jpg as the default
        if not os.path.splitext(filename)[1]:
            return filename + '.jpg'
        
        # if the extension is not supported, replace it with .jpg as the default
        if os.path.splitext(filename)[1] not in UtilService.__supported_image_ext:
            return filename.replace(os.path.splitext(filename)[1], '.jpg')

        return filename    


    @staticmethod
    def download_web_image_from_data_uri(data_uri, file_path) -> str:
        """
        Helper method to download an image from a data URI and save it to the specified directory.
        NOTE: use download_web_image() instead as this is just a helper method.

        :param data_uri: the data URI of the image
        :param file_path: the file path to save the image
        :return: the path to the downloaded image
        """
        header, encoded = data_uri.split(",", 1)
        data = base64.b64decode(encoded)
        mime_type = header.split(';')[0].split(':')[1]
        extension = mimetypes.guess_extension(mime_type) or '.jpg'
        full_path = file_path + extension
        with open(full_path, 'wb') as file:
            file.write(data)
        return full_path

    @staticmethod
    def download_web_image_from_url(url, file_path) -> str:
        """
        Helper method to download an image from the web and save it to the specified directory.
        NOTE: use download_web_image() instead as this is just a helper method.

        :param url: the URL of the image
        :param file_path: the file path to save the image
        :return: the path to the downloaded image
        """
        response = requests.get(url, stream=True, headers=UtilService.__web_image_request_headers)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return file_path
        else:
            return None

    @staticmethod
    def build_web_image_url(url, base_url=None) -> str:
        """
        Some websites use relative URLs for images, this function converts relative URLs to absolute URLs.

        :param url: the URL of the image
        :param base_url: the base URL to resolve relative URL
        :return: the absolute URL of the image
        """

        # Handle protocol-relative URLs
        if url.startswith('//'):
            url = 'https:' + url

        # Adjust relative URL
        if not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url) if base_url else url

        return url

    @staticmethod
    def download_web_image(url: str, download_dir="downloads") -> (str, str):
        """
        Download an image from the web and save it to the specified directory.

        :param url: the URL of the image
        :param download_dir: the directory to save the image
        :return: the full src URL of the image formulated in this function, for binary image data, return its filename
        :return: the path to the downloaded image
        """
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Handle protocol-relative URLs
        if url.startswith('//'):
            url = 'https:' + url

        # Generate file path
        file_name = UtilService.generate_web_image_filename(url)
        file_path = os.path.join(download_dir, file_name)
        print(f"### downloaded image from {url} to {file_path}")

        # Download the image
        if url.startswith('data:image'):
            return file_name, UtilService.download_web_image_from_data_uri(url, file_path)
        else:
            return url, UtilService.download_web_image_from_url(url, file_path)
        
    @staticmethod
    def get_work_email_root_domains(emails: str) -> str:
        root_domains = []

        email_regex = re.compile(r'@([\w.-]+)')
        for email in emails:
            match = email_regex.search(email)
            if match:
                domain = match.group(1)
                parts = domain.split('.')
                if domain not in UtilService.__configs.COMMON_EMAIL_PROVIDERS and len(parts) > 1:
                    root_domain = '.'.join(parts[:-1])
                    root_domains.append(root_domain)

        return root_domains    

if __name__ == '__main__':
    fullname = "hello"
    url = "https://api.protexxa.com/v1/register/02944f8b-8a52-4fd6-94e3-dc6a8ded0d5b/original/avatar.jpeg"
    # url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Michelle_Obama_2013_official_portrait.jpg/220px-Michelle_Obama_2013_official_portrait.jpg"
    dir = f"temp/{fullname}"
    img_path = UtilService.download_user_image(url, dir)