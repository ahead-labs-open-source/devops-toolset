"""Provides tools for managing the AWS CloudFront service"""

from devops_toolset.core.app import App
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.project_types.aws.literals import Literals as AwsLiterals

import boto3
import logging
import time

app: App = App()
cloudfront = boto3.client("cloudfront")
literals = LiteralsCore([AwsLiterals])


def create_invalidation(distribution_id: str, invalidation_paths: list[str] = ["/*"]):
    """Creates a CloudFront invalidation.

    Args:
        distribution_id: Id of the CloudFront distrbution where the
            invalidation will be created.
        invalidation_paths: List of all the paths to be invalidated.
    """

    response = cloudfront.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            "Paths": {
                "Quantity": len(invalidation_paths),
                "Items": invalidation_paths
            },
            "CallerReference": str(time.time()).replace(".", "")
        }
    )

    logging.info(literals.get("cloudfront_invalidation_created").format(id=response['Invalidation']['Id']))


if __name__ == "__main__":
    help(__name__)
