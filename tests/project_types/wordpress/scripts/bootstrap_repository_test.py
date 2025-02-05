""" Unit core for the bootstrap repository script """

from unittest.mock import patch
import devops_toolset as sut


# region main


@patch("os.chdir")
@patch("devops_toolset.tools.git.git_init")
@patch("devops_toolset.tools.git.git_commit")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.main")
def test_main_given_given_arguments_then_call_dependencies(generate_wordpress_mock, git_commit_mock,
                                                           git_init_mock, chdir_mock, wordpressdata):
    """ Given project path argument, then calls os.chdir to project_path """
    # Arrange
    project_path = wordpressdata.root_path
    db_user_password = db_admin_password = wp_admin_password = wordpressdata.default_pwd
    skip_git = False
    # Act
    sut.main(project_path, db_user_password, db_admin_password, wp_admin_password, wordpressdata.environment_name,
             [], [], False, False, skip_git)
    # Assert
    chdir_mock.assert_called_once_with(project_path)
    git_init_mock.assert_called_once_with(project_path, skip_git)
    generate_wordpress_mock.assert_called_once_with(project_path, db_user_password, db_admin_password,
                                                    wp_admin_password, wordpressdata.environment_name, [], [], False,
                                                    False)
    git_commit_mock.assert_called_once_with(skip_git)
# endregion main
