from flask import current_app
import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock


def test_main_wrong_password(client, app):
    """Test authentication with incorrect password

    This test verifies that the application correctly rejects requests with an
    incorrect password. The endpoint should return a 200 status code with a
    specific error message indicating the password was wrong.
    """
    response_main_post = client.post("/", data={"password":"A"*24, "domain":"test.se", "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: wrong password" in response_main_post.data


def test_main_illigal_char_email(client, app, password):
    """Test email validation failure

    This test verifies that the application properly validates the email parameter
    and rejects requests containing invalid email formats. The endpoint should
    return a specific error message indicating the email validation failed.
    """
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@test..se"})
    assert response_main_post.status_code == 200
    assert b"error: email validation failed" in response_main_post.data


def test_main_illigal_char_password(client, app):
    """Test password validation failure

    This test verifies that the application properly validates the password parameter
    and rejects requests containing invalid password formats. The endpoint should
    return a specific error message indicating the password validation failed.
    """
    response_main_post = client.post("/", data={"password":"..password", "domain":"test.se", "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: password validation failed" in response_main_post.data


def test_main_illigal_char_domain(client, app, password):
    """Test domain validation failure

    This test verifies that the application properly validates the domain parameter
    and rejects requests containing invalid domain formats. The endpoint should
    return a specific error message indicating the domain validation failed.
    """
    response_main_post = client.post("/", data={"password":password, "domain":"..test.se", "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: domain validation failed" in response_main_post.data


def test_main_not_matching_domain(client, app, password):
    """Test email and domain matching validation

    This test verifies that the application properly validates that the email domain
    matches the specified domain parameter. The endpoint should return a specific
    error message when the email address domain does not match the provided domain.
    """
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@testtest.se"})
    assert response_main_post.status_code == 200
    assert b"error: email adress domain do not match domain" in response_main_post.data


def test_missing_password(client, app):
    """Test missing password parameter

    This test verifies that the application properly handles the case when
    the password parameter is missing from the request. The endpoint should
    return a specific error message indicating the password is none.
    """
    response_main_post = client.post("/", data={"domain":"test.se", "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: password is none" in response_main_post.data


def test_missing_domain(client, app, password):
    """Test missing domain parameter

    This test verifies that the application properly handles the case when
    the domain parameter is missing from the request. The endpoint should
    return a specific error message indicating the domain is none.
    """
    response_main_post = client.post("/", data={"password":password, "email":"test@test.se"})
    assert response_main_post.status_code == 200
    assert b"error: domain is none" in response_main_post.data


def test_missing_email(client, app, password):
    """Test missing email parameter

    This test verifies that the application properly handles the case when
    the email parameter is missing from the request. The endpoint should
    return a specific error message indicating the email is none.
    """
    response_main_post = client.post("/", data={"password":password, "domain":"test.se"})
    assert response_main_post.status_code == 200
    assert b"error: email is none" in response_main_post.data


@patch('os.path.exists')
@patch('subprocess.run')
def test_successful_email_deletion(mock_subprocess_run, mock_exists, client, app, password):
    """Test successful email deletion

    This test verifies that the application successfully processes a valid request
    to delete an email account. It mocks the subprocess call to simulate successful
    execution of the srm command with the doas wrapper.
    """
    # Configure mocks
    mock_exists.return_value = True
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_subprocess_run.return_value = mock_process

    # Make request
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@test.se"})

    # Verify response
    assert response_main_post.status_code == 200
    assert b"done" in response_main_post.data

    # Verify subprocess was called correctly with the expected command
    mock_subprocess_run.assert_called_once()


@patch('os.path.exists')
def test_srm_binary_not_found(mock_exists, client, app, password):
    """Test missing srm binary

    This test verifies that the application properly handles the case when
    the srm binary is not found at the expected location. The endpoint should
    return a specific error message.
    """
    # Configure mock
    mock_exists.return_value = False

    # Make request
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@test.se"})

    # Verify response
    assert response_main_post.status_code == 200
    assert b"error: srm binary location is wrong" in response_main_post.data


@patch('os.path.exists')
@patch('subprocess.run')
def test_subprocess_error(mock_subprocess_run, mock_exists, client, app, password):
    """Test subprocess execution error

    This test verifies that the application properly handles the case when
    the subprocess call to remove the email directory raises a CalledProcessError.
    The endpoint should return a specific error message.
    """
    # Configure mocks
    mock_exists.return_value = True
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "cmd")

    # Make request
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@test.se"})

    # Verify response
    assert response_main_post.status_code == 200
    assert b"error: returncode of cmd srm is non zero" in response_main_post.data


@patch('os.path.exists')
@patch('subprocess.run')
def test_subprocess_nonzero_return(mock_subprocess_run, mock_exists, client, app, password):
    """Test subprocess non-zero return code

    This test verifies that the application properly handles the case when
    the subprocess call to remove the email directory returns a non-zero exit code.
    The endpoint should return a specific error message.
    """
    # Configure mocks
    mock_exists.return_value = True
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_subprocess_run.return_value = mock_process

    # Make request
    response_main_post = client.post("/", data={"password":password, "domain":"test.se", "email":"test@test.se"})

    # Verify response
    assert response_main_post.status_code == 200
    assert b"error: returncode of cmd srm is non zero" in response_main_post.data
