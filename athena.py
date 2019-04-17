# -*- coding: utf-8 -*-
import logging
import os
from time import sleep

import boto3
import pandas as pd
from backports.tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


class AthenaQueryFailed(Exception):
    pass


class Athena(object):
    S3_TEMP_BUCKET = "please-replace-with-your-bucket"

    def __init__(self, bucket=S3_TEMP_BUCKET):
        self.bucket = bucket
        self.client = boto3.Session().client("athena")

    def execute_with_pandas(self, query, database="csv_dumps"):
        """Query the athena database and get result in pandas.DataFrame

        :param query: Query to be executed in Athena
        :return: pd.DataFrame
        """
        s3_bucket_path = "s3://{bucket}".format(bucket=self.bucket)
        s3_result_path = self.execute_query_in_athena(
            query, output_s3_directory=s3_bucket_path, database=database
        )
        bucket, key = self.get_bucket_and_key_from_s3_absolute_path(s3_result_path)

        with TemporaryDirectory() as dir:
            path = "{dir}/result.csv".format(dir=dir)
            boto3.resource("s3").Bucket(bucket).download_file(key, path)
            result_df = pd.read_csv(path)
            os.remove(path)
            return result_df

    def execute_query_in_athena(self, query, output_s3_directory, database="csv_dumps"):
        """ Useful when client executes a query in Athena and want result in the given `s3_directory`

        :param query: Query to be executed in Athena
        :param output_s3_directory: s3 path in which client want results to be stored
        :return: s3 path
        """
        response = self.client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": database},
            ResultConfiguration={"OutputLocation": output_s3_directory},
        )
        query_execution_id = response["QueryExecutionId"]
        filename = "{filename}.csv".format(filename=response["QueryExecutionId"])
        s3_result_path = os.path.join(output_s3_directory, filename)
        logger.info(
            "Query query_execution_id <<{query_execution_id}>>, result_s3path <<{s3path}>>".format(
                query_execution_id=query_execution_id, s3path=s3_result_path
            )
        )
        self.wait_for_query_to_complete(query_execution_id)
        return s3_result_path

    def wait_for_query_to_complete(self, query_execution_id):
        is_query_running = True
        backoff_time = 10
        while is_query_running:
            response = self.__get_query_status_response(query_execution_id)
            status = response["QueryExecution"]["Status"][
                "State"
            ]  # possible responses: QUEUED | RUNNING | SUCCEEDED | FAILED | CANCELLED
            if status == "SUCCEEDED":
                is_query_running = False
            elif status in ["CANCELED", "FAILED"]:
                raise AthenaQueryFailed(status)
            elif status in ["QUEUED", "RUNNING"]:
                logger.info("Backing off for {} seconds.".format(backoff_time))
                sleep(backoff_time)
            else:
                raise AthenaQueryFailed(status)

    def __get_query_status_response(self, query_execution_id):
        response = self.client.get_query_execution(QueryExecutionId=query_execution_id)
        return response

    @staticmethod
    def get_bucket_and_key_from_s3_absolute_path(s3_result_path):
        path = s3_result_path[5:].split("/")
        bucket = path[0]
        key = "/".join(path[1:])
        return bucket, key
