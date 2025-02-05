"""Unit core for the xcoding64 file"""

import devops_toolset as sut


# region encode()


def test_encode():
    """Given a UTF-8 string, it is encoded to base64 format """

    # Arrange
    text = "python"
    expected = "cHl0aG9u"

    # Act
    result = sut.encode(text)

    # Assert
    assert result == expected

# endregion

# region decode()


def test_decode():
    """Given a base64 string, it is decoded to UTF-8 format """

    # Arrange
    text = "cHl0aG9u"
    expected = "python"

    # Act
    result = sut.decode(text)

    # Assert
    assert result == expected

# endregion
