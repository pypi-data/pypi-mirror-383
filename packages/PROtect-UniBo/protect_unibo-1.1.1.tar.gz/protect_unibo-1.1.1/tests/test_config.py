import pytest
from unittest.mock import patch, MagicMock
import string
import hashlib

from project.config import checkConfig, config, generateDeviceSecret

# Using FIXTURES to build a reusable setup to avoid repetitions 
@pytest.fixture
def mock_dbconfig():
    #Fixture to mock the DB connection + cursor
    mock_db=MagicMock()
    mock_cursor=MagicMock()
    mock_db.cursor.return_value=mock_cursor
    return mock_db, mock_cursor

#Checking CHECKCONFIG()
@patch ("project.config.dbconfig")
def test_checkConfig_schema_exists(mock_dbconfig_call, mock_dbconfig):
    mock_db, mock_cursor=mock_dbconfig
    mock_cursor.fetchall.return_value=[("PROtect",)]
    mock_dbconfig_call.return_value=mock_db
    assert checkConfig() is True
    mock_cursor.execute.assert_called_once()

@patch ("project.config.dbconfig")
def test_checkConfig_schema_missing(mock_dbconfig_call, mock_dbconfig):
    mock_db, mock_cursor=mock_dbconfig
    mock_cursor.fetchall.return_value=[]
    mock_dbconfig_call.return_value=mock_db
    assert checkConfig() is False
 
#ASSERT allows simple comparisons, quick to read and easy to understand and it shows detailed info whether assert fails
# In this way we can avoid using plenty of different methods from the library 

#Checking GENERATEDEVICESECRET()
def test_generateDeviceSecret_length():
    secret=generateDeviceSecret(15)
    assert len(secret)==15

def test_generateDeviceSecret_default_length():
    secret=generateDeviceSecret()
    assert len(secret)==10

def test_generateDeviceSecret_characters(): 
    secret=generateDeviceSecret(50)
    allowed_chars=set(string.ascii_uppercase+string.digits)
    assert all(c in allowed_chars for c in secret)

def test_generateDeviceSecret_length_and_chars():
    secret=generateDeviceSecret(12)
    assert len(secret)==12
    assert all(c in string.ascii_uppercase + string.digits for c in secret)

def test_generateDeviceSecret_randomness():
    secrets={generateDeviceSecret(20) for i in range(100)}
    assert len(secrets) > 90 
    #generates 100 random secrets and expects at least 90 to be unique so that randomness is not broken

#Checking CONFIG()
@patch("project.config.checkConfig", return_value=True)
@patch("project.config.dbconfig")
@patch("project.config.printc")
def test_config_already_configured(mock_printc, mock_dbconfig_call, mock_checkConfig):
    config()
    mock_printc.assert_any_call("[red][!] Already Configured [/red]")
    mock_dbconfig_call.assert_not_called()

@patch("project.config.checkConfig", return_value=False)
@patch("project.config.getpass", side_effect=["password", "nomatch", "password", "password"])
@patch("project.config.generateDeviceSecret", return_value="SECRET12345")
@patch("project.config.dbconfig")
@patch("project.config.printc")
@patch("project.config.console")
def test_config_flow(mock_console, mock_printc, mock_dbconfig_call, mock_secret, mock_getpass, mock_checkConfig):
    mock_db, mock_cursor=MagicMock(), MagicMock()
    mock_dbconfig_call.return_value=mock_db
    mock_db.cursor.return_value=mock_cursor

    config()

    #check DB and tables are created
    mock_cursor.execute.assert_any_call("CREATE DATABASE PROtect")
    mock_cursor.execute.assert_any_call("CREATE TABLE PROtect.secrets (masterpassword_hash TEXT NOT NULL, device_secret TEXT NOT NULL)")
    mock_cursor.execute.assert_any_call("CREATE TABLE PROtect.entries (sitename TEXT NOT NULL, siteurl TEXT NOT NULL, email TEXT , username TEXT, password TEXT NOT NULL)")

    #check password hash inserted 
    hashed = hashlib.sha256("password".encode()).hexdigest()
    mock_cursor.execute.assert_any_call("INSERT INTO PROtect.secrets (masterpassword_hash, device_secret) values (?,?)", (hashed, "SECRET12345"))

    #commit and close called
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()

    #output printed indicating success
    mock_printc.assert_any_call("[green][+] Configuration Completed! [/green]")

@patch("project.config.checkConfig", return_value=False)
@patch("project.config.printc")
@patch("project.config.console")
@patch("project.config.dbconfig")
def test_config_failure(mock_dbconfig_call, mock_console, mock_printc, mock_checkConfig):
    mock_db, mock_cursor=MagicMock(), MagicMock()
    mock_dbconfig_call.return_value=mock_db
    mock_db.cursor.return_value=mock_cursor 

    #simulate exception on CREATE DATABASE
    def raise_exc(query, *args, **kwargs):
        if query=="CREATE DATABASE PROtect":
            raise Exception("DB exists")
        return None
    mock_cursor.execute.side_effect=raise_exc

    #we patch getpass and generateDeviceSecret minimally for this test
    with patch("project.config.getpass", side_effect=["pw", "pw"]), \
         patch("project.config.generateDeviceSecret", return_value="SECRET"):
        
        config()
    
    #Ensure error message printed after DB creation failure
    mock_printc.assert_any_call("[red][!] An error occurred while trying to create the Database. Maybe it already exists? [/red]")
    mock_console.print_exception.assert_called_once()
