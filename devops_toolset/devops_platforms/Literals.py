"""devops_platforms module literals."""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the devops_platforms module."""

    # Add your core literal dictionaries here
    _info = {
        "environment_variable_log": _("=> {key} {value}"),
        "sonar_getting_qg": _("Getting quality gate for branch {branch} (original name)."),
        "sonar_pr_mode": _("Pull request mode: {pull_request}"),
        "sonar_config_file": _("Using {file} as the Sonar* configuration file."),
        "sonar_qg_ok": _("Quality gate succeeded"),
        "sonar_qg_json": _("This is the JSON data returned by Sonar*:\n\n{json}"),
        "sonar_qg_url": _("Request URL:\n{url}")
    }
    _errors = {
        "sonar_invalid_metric": _("Invalid metric value for {metricKey}: {actualValue} {comparator} {errorThreshold}"),
        "sonar_unexpected_status_code":
            _("Status code got from Sonar* was not 200, but {statusCode}. Please check it out."),
    }
