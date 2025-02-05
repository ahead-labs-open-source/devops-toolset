""" This script allows the user to configure some initial settings """
import argparse
import json
import pkg_resources
import logging

logging.basicConfig(level=logging.INFO)
logging.Formatter("%(asctime)s %(levelname)-8s %(module)-15s %(message)s")
logger = logging.getLogger(__name__)


def main(devops_platform: str, language: str):
    """ Sets the configuration inside settings.json """
    settings_path = pkg_resources.resource_filename("devops_toolset.core", "settings.json")

    with open(settings_path, 'r') as settings_file:
        settings = json.load(settings_file)
        logger.info(f"Retrieved settings.json from {settings_path}")

    settings['platform'] = devops_platform
    settings['language'] = language

    with open(settings_path, 'w') as settings_file:
        logger.info(f"Setting 'devops_platform' -> {devops_platform}")
        logger.info(f"Setting 'language' -> {language}")
        json.dump(settings, settings_file)
        logger.info("Settings successfully saved")

# TODO(alberto.carbonell) Make a guided configuration using clint when no arguments
# TODO(alberto.carbonell) Create argument validators based on enums to avoid input errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--devops-platform", default="azuredevops")
    parser.add_argument("--language", default="en")
    args = parser.parse_args()
    main(args.devops_platform, args.language)
