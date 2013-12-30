from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET
from boto.s3.connection import S3Connection
import requests
import uuid

class ReverseImageSearcher(object):
    def __init__(self):
        conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
        self.bucket = conn.get_bucket(AWS_BUCKET)

    def get_results(self, local_image_path):
        image_url = self._upload_to_s3(local_image_path)
        user_agent = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}
        r = requests.get("http://images.google.com/searchbyimage", params={'image_url': image_url}, headers=user_agent)
        return r.text

    def _upload_to_s3(self, local_image_path):
        k = self.bucket.new_key(str(uuid.uuid4()))
        k.set_contents_from_filename(local_image_path)
        # only hardcode metadata if we can guarantee the image type we're getting
        k.set_metadata('Content-Type', 'image/jpeg')
        k.make_public()
        url = k.generate_url(expires_in=300, query_auth=False, force_http=True)
        return url
