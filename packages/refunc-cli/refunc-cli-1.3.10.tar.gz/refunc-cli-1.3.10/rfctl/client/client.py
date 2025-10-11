import json
import boto3
import os
from pretty_logging import pretty_logger
import base64


class LambdaClient:
    def __init__(self, region_name):
        endpoint_url = os.environ.get("AWS_DEFAULT_ENDPOINT")
        self.lambda_client = boto3.client('lambda',
                                          region_name=region_name,
                                          endpoint_url=endpoint_url,
                                          use_ssl=endpoint_url.startswith("https"),
                                          aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', "__none__"),
                                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', "__none__"))

    def invoke_function(self, function_name, function_params, get_log=False):
        response = self.lambda_client.invoke(FunctionName=function_name,
                                             Payload=json.dumps(function_params), LogType='Tail' if get_log else 'None')
        metadata = response["ResponseMetadata"]
        payload = response["Payload"]
        if get_log:
            headers = metadata["HTTPHeaders"]
            log_bts = headers.get("x-amz-log-result")
            if log_bts:
                converted_str = log_bts.replace("-", "+").replace("_", "/")
                while len(converted_str) % 4 != 0:
                    converted_str += "="
                for line in base64.b64decode(converted_str).decode("utf-8").splitlines():
                    pretty_logger.info(line)
        return json.loads(payload.read())
