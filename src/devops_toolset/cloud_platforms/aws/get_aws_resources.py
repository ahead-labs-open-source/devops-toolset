"""Gets the AWS resources in your account (uses your default machine
authentication settings)"""

import argparse
import json
import devops_toolset.tools.argument_validators
import devops_toolset.tools.cli as cli


def main(json_path: str, hosted_zone: str):
    """Gets the AWS resources and writes them to a JSON file.

    Args:
        json_path: Path to the JSON file to be written.
        hosted_zone: DNS zone ID to be queried.
            ie: /hostedzone/ABCDEFGHIJKL123456789 (must pass everything)
    """

    resources: dict = {}

    resources["commit_repositories"] = json.loads(cli.call_subprocess_with_result(
        "aws codecommit list-repositories --query \"repositories[].repositoryName\""))
    resources["codebuild_projects"] = json.loads(cli.call_subprocess_with_result(
        "aws codebuild list-projects --query \"projects[]\""))
    resources["codepipeline_pipelines"] = json.loads(cli.call_subprocess_with_result(
        "aws codepipeline list-pipelines --query \"pipelines[].name\""))
    resources["codeartifact_repositories"] = json.loads(cli.call_subprocess_with_result(
        "aws codeartifact list-repositories"))
    resources["event_buses"] = json.loads(cli.call_subprocess_with_result(
        "aws events list-event-buses --query \"EventBuses[].Name\""))
    resources["event_rules"] = json.loads(cli.call_subprocess_with_result(
        "aws events list-rules"))
    resources["ec2_instances"] = json.loads(cli.call_subprocess_with_result(
        "aws ec2 describe-instances"))
    resources["elasticbeanstalk_applications"] = json.loads(cli.call_subprocess_with_result(
        "aws elasticbeanstalk describe-applications"))
    resources["elasticbeanstalk_environments"] = json.loads(cli.call_subprocess_with_result(
        "aws elasticbeanstalk describe-environments"))
    resources["s3_buckets"] = json.loads(cli.call_subprocess_with_result(
        "aws s3api list-buckets --query \"Buckets[].Name\""))
    resources["route53_hosted_zones"] = json.loads(cli.call_subprocess_with_result(
        "aws route53 list-hosted-zones --query \"HostedZones[].Name\""))

    if hosted_zone is not None:
        resources["route53_recordsets"] = json.loads(cli.call_subprocess_with_result(
            f"aws route53 list-resource-record-sets --hosted-zone-id {hosted_zone}"))

    resources["iam_custom_policies"] = json.loads(cli.call_subprocess_with_result(
        "aws iam list-policies --scope Local --query \"Policies[].PolicyName\""))
    resources["iam_roles"] = json.loads(cli.call_subprocess_with_result(
        "aws iam list-roles --query \"Roles[].RoleName\""))

    with open(json_path, 'w') as data_file:
        json.dump(resources, data_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json-path", action=tools.argument_validators.PathValidator)
    parser.add_argument("--hosted-zone", default=None)
    args, args_unknown = parser.parse_known_args()

    main(args.json_path, args.hosted_zone)
