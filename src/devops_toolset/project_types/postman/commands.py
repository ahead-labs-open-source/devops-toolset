"""Commands for the Postman project type module."""

from devops_toolset.core.ValueDictsBase import ValueDictsBase


class Commands(ValueDictsBase):
    """Commands for the Postman module."""

    _commands = {
        "convert_openapi": "python -m devops_toolset.project_types.postman.openapi_to_postman {source} {output} {environments}",
        "deploy_to_workspace": "python -m devops_toolset.project_types.postman.deploy_to_workspace {collection_path} --workspace-id {workspace_id} --environments {environment_paths}",
        "delete_from_workspace": "python -m devops_toolset.project_types.postman.delete_from_workspace --workspace-id {workspace_id} --x-api-id {x_api_id}",
        "validate_collection": "newman validate {collection_path}",
        "run_collection": "newman run {collection_path} -e {environment_path}",
        "export_collection": "postman collection export {collection_id} -o {output_path}"
    }
