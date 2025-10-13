from unittest.mock import patch, MagicMock
from project.dbconfig import dbconfig 

@patch("project.dbconfig.mysql.connector.connect")
def test_dbconfig_success(mock_connect):
    mock_db=MagicMock()
    mock_connect.return_value=mock_db

    db=dbconfig()

    mock_connect.assert_called_once_with(
        host="localhost",
        user="pm",
        password="password"
    )
    assert db is mock_db

@patch("project.dbconfig.mysql.connector.connect", side_effect=Exception("DB connection failed"))
@patch("project.dbconfig.console.print_exception")
def test_dbconfig_failure(mock_print_exception, mock_connect):
    db=dbconfig()
    assert db is None #assuming the function returns None on failure
    mock_print_exception.assert_called_once()