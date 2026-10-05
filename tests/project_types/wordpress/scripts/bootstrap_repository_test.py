""" Unit core for the bootstrap repository script """

from unittest.mock import patch

import pytest
import devops_toolset.project_types.wordpress.scripts.bootstrap_repository as sut


# region main


@patch("os.chdir")
@patch("devops_toolset.tools.git.git_init")
@patch("devops_toolset.tools.git.git_commit")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.main")
def test_main_given_given_arguments_then_call_dependencies(generate_wordpress_mock, git_commit_mock,
                                                           git_init_mock, chdir_mock, wordpressdata, tmp_path, monkeypatch):
    """ Given project path argument, then calls os.chdir to project_path """
    # Arrange
    monkeypatch.setattr(sut.Path, "cwd", lambda: tmp_path)
    project = tmp_path / "site"
    project.mkdir()
    project_path = str(project)
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


@pytest.mark.parametrize("relative", ["site", "."])
def test_accepts_existing_project_inside_invocation_directory(tmp_path, monkeypatch, relative):
    """Both project-root and parent-directory invocation remain supported."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "site").mkdir()
    assert sut.validate_project_path(relative) == str((tmp_path / relative).resolve())


@pytest.mark.parametrize("relative", ["../outside", "site/../../outside", "missing"])
def test_rejects_invalid_paths_before_any_side_effect(tmp_path, monkeypatch, relative):
    """Invalid CLI destinations cannot reach Git or WordPress generation."""
    monkeypatch.chdir(tmp_path)
    with patch.object(sut.os, "chdir") as chdir, patch.object(sut.git, "git_init") as init, \
            patch.object(sut.generate_wordpress, "main") as generate:
        with pytest.raises((ValueError, FileNotFoundError)):
            sut.main(relative, "secret", "secret", "secret", "localhost", [], [], False, False, True)
        chdir.assert_not_called()
        init.assert_not_called()
        generate.assert_not_called()


def test_rejects_absolute_destination_outside_boundary(tmp_path, monkeypatch):
    """An absolute path cannot bypass the invocation boundary."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        sut.validate_project_path(str(tmp_path.parent))


@pytest.mark.parametrize("child_link", [False, True])
def test_rejects_symbolic_link_destinations(tmp_path, monkeypatch, child_link):
    """Reject links in both the project path and the existing project content."""
    monkeypatch.chdir(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    project = tmp_path / "site"
    if child_link:
        project.mkdir()
        (project / "uploads").symlink_to(outside, target_is_directory=True)
    else:
        project.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="[Ss]ymbolic links"):
        sut.validate_project_path(str(project))


def test_rejects_regular_file_destination(tmp_path, monkeypatch):
    """A regular file is never a valid project root."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "file").write_text("preserve")
    with pytest.raises(ValueError):
        sut.validate_project_path("file")
    assert (tmp_path / "file").read_text() == "preserve"
