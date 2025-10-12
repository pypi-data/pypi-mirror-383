import os
import time
import subprocess
from flask import Blueprint, current_app, request, make_response, Response
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import ddmail_validators.validators as validators

bp = Blueprint("application", __name__, url_prefix="/")

@bp.route("/", methods=["POST"])
def main() -> Response:
    """
    Processes a request to remove an email account from the system.

    This function handles a POST request containing email account information and authentication.
    It validates the inputs, verifies the password against a stored hash, and then
    removes the specified email directory from the filesystem using subprocess commands.

    Returns:
        Response: A Flask response object containing a success message if deletion was successful,
                 or an error message describing the issue encountered.

    Request Form Parameters:
        password (str): The password for authentication
        domain (str): The domain part of the email address
        email (str): The complete email address to be removed

    Error Responses:
        "error: password is none": If the password parameter is missing
        "error: domain is none": If the domain parameter is missing
        "error: email is none": If the email parameter is missing
        "error: password validation failed": If the password doesn't meet validation requirements
        "error: domain validation failed": If the domain format is invalid
        "error: email validation failed": If the email format is invalid
        "error: wrong password": If the provided password doesn't match the stored hash
        "error: email adress domain do not match domain": If the domain in the email doesn't match the domain parameter
        "error: srm binary location is wrong": If the srm binary doesn't exist at the expected location
        "error: returncode of cmd srm is non zero": If the email removal process fails

    Success Response:
        "done": Returns when the email account has been successfully removed
    """
    if request.method != 'POST':
        return make_response("Method not allowed", 405)

    ph = PasswordHasher()

    password = request.form.get('password')
    domain = request.form.get('domain')
    email = request.form.get('email')

    # Check if input from form is None.
    if password is None:
        current_app.logger.error("password is None")
        return make_response("error: password is none", 200)

    if domain is None:
        current_app.logger.error("domain is None")
        return make_response("error: domain is none", 200)

    if email is None:
        current_app.logger.error("email is None")
        return make_response("error: email is none", 200)

    # Validate password.
    if validators.is_password_allowed(password) is not True:
        current_app.logger.error("password validation failed")
        return make_response("error: password validation failed", 200)

    # Validate domain.
    if validators.is_domain_allowed(domain) is not True:
        current_app.logger.error("domain validation failed")
        return make_response("error: domain validation failed", 200)

    # Validate email.
    if validators.is_email_allowed(email) is not True:
        current_app.logger.error("domain validation failed")
        return make_response("error: email validation failed", 200)

    # Check if password is correct.
    try:
        if ph.verify(current_app.config["PASSWORD_HASH"], password) is not True:
            time.sleep(1)
            current_app.logger.error("wrong password")
            return make_response("error: wrong password", 200)
    except VerifyMismatchError:
        time.sleep(1)
        current_app.logger.error("VerifyMismatchError, wrong password")
        return make_response("error: wrong password", 200)
    time.sleep(1)

    # Split email and verify domain.
    splitted_email_domain = email.split('@')
    if splitted_email_domain[1] != domain:
        current_app.logger.error("email address domain do no match domain")
        return make_response("error: email adress domain do not match domain", 200)

    # Path to email folder on disc.
    email_path = current_app.config["EMAIL_ACCOUNT_PATH"] + "/" + domain + "/" + splitted_email_domain[0]

    # location of srm binary.
    srm = current_app.config["SRM_BIN"]

    # Check that srm exist.
    if os.path.exists(srm) is not True:
        current_app.logger.error("srm binary location is wrong")
        return make_response("error: srm binary location is wrong", 200)

    # Remove email folder from hdd.
    try:
        output = subprocess.run(
                ["/usr/bin/doas", "-u", "vmail", srm, "-zrl", email_path],
                check=True
                )
        if output.returncode != 0:
            current_app.logger.error("returncode of cmd srm is non zero")
            return make_response("error: returncode of cmd srm is non zero", 200)
    except subprocess.CalledProcessError:
        current_app.logger.error("returncode of cmd srm is non zero")
        return make_response("error: returncode of cmd srm is non zero", 200)

    current_app.logger.info("done")
    return make_response("done", 200)
