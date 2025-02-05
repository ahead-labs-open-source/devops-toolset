"""tools module commands"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Commands(ValueDictsBase):
    """Commands for the tools module."""

    # Add your core literal dictionaries here
    _commands = {
        "git_init": "git init {path}",
        "git_add": "git add .",
        "git_commit_m": "git commit -m \"{message}\"",
        "git_push_tag": "git {auth} push origin {tag_name}",
        "git_push_tag_delete": "git {auth} push --delete origin {tag_name}",
        "git_tag_add": "git tag -a {tag_name} {commit_name} -m {tag_name}",
        "git_tag_check": "git {auth} ls-remote {remote_name} \"refs/tags/{tag_name}\"",
        "git_tag_delete": "git tag -d {tag_name}",
        "public_ip_address_service_url": "http://checkip.dyndns.org",
        "git_auth": "-c http.extraheader=\"AUTHORIZATION: {auth_header}\"",
        "svn_add": "svn add \"{files_glob}\"",
        "svn_checkin": "svn ci -m \"{comment}\" --username {username} --password {password}",
        "svn_checkout": "svn co \"{url}\" \"{local_path}\"",
        "svn_copy": "svn cp \"{origin}\" \"{destination}\""
    }
