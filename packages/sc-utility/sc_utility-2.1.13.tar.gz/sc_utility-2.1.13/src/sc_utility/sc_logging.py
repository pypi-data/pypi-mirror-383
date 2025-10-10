"""
Spello Consulting Logging Module.

Provides general purpose logging functions.
"""
import datetime as dt
import inspect
import smtplib
import ssl
import sys
import threading
import traceback
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from sc_utility.sc_common import SCCommon
from sc_utility.sc_date_helper import DateHelper


@dataclass
class NotifiableIssue:
    entity: str
    issue_type: str
    first_reported: dt.datetime
    last_reported: dt.datetime
    send_delay: int
    message: str
    email_sent: bool = False


class SCLogger:
    """A class to handle logging messages with different verbosity levels."""

    def __init__(self, logger_settings: dict):
        """
        Initializes the logger with configuration settings.

        The structure of logger_settings is as follows:
        {
            "logfile_name": Optional[str],  # The name of the log file. If None, no file logging will be done.
            "file_verbosity": Optional[str],  # Verbosity level for file logging
            "console_verbosity": Optional[str],  # Verbosity level for console logging
            "max_lines": Optional[int],  # Maximum number of lines to keep in the log file
            "log_process_id": Optional[bool],  # If True, include the process ID in log messages. Defaults to False.
            "log_thread_id": Optional[bool],  # If True, include the thread ID in log messages. Defaults to False.
        }

        Args:
            logger_settings (Optional[dict]): A dictionary containing logger settings
        """
        # Make a note of the app directory
        self.app_dir = self.client_dir = SCCommon.get_project_root()

        # Setup the path to the fatal error tracking file
        self.fatal_error_file_path = self.app_dir / f"{self.app_dir.name}_fatal_error.txt"

        # Use the register_email_settings method to set up email settings
        self.email_settings = None

        self.verbosity_levels = {
            "none": 0,
            "error": 1,
            "warning": 2,
            "summary": 3,
            "detailed": 4,
            "debug": 5,
            "all": 6,
        }
        # Attributes set in the initialise_logger method
        self.logfile_name = None
        self.logfile_path = None
        self.file_verbosity = "summary"
        self.console_verbosity = "summary"
        self.max_lines = 1000
        self.timestamp_format = "%Y-%m-%d %H:%M:%S"
        self.log_process_id = False
        self.log_thread_id = False
        self.file_logging_enabled = False
        self.notifiable_issues: list[NotifiableIssue] = []

        self.initialise_settings(logger_settings)

    def initialise_settings(self, logger_settings: dict):
        """
        Set / reset the logger configuration settings. See the __init__() method for the structure of logger_settings.

        Args:
            logger_settings (Optional[dict]): A dictionary containing logger settings.
        """
        self.logfile_name = logger_settings.get("logfile_name")
        self.file_verbosity = logger_settings.get("file_verbosity", "summary")
        self.console_verbosity = logger_settings.get("console_verbosity", "summary")
        self.max_lines = logger_settings.get("max_lines", 1000)
        self.timestamp_format = logger_settings.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
        self.log_process_id = logger_settings.get("log_process_id", False)
        self.log_thread_id = logger_settings.get("log_thread_id", False)

        # See if logfile writing is required
        self.file_logging_enabled = self.logfile_name is not None

        if self.file_logging_enabled and self.logfile_name is not None:
            self.logfile_path = SCCommon.select_file_location(self.logfile_name)

            # Truncate the log file if it exists
            self._initialise_monitoring_logfile()

    def _initialise_monitoring_logfile(self) -> None:
        """Initialise the monitoring log file. If it exists, truncate it to the max number of lines."""
        if not self.file_logging_enabled:
            return

        self.trim_logfile()

    def trim_logfile(self) -> None:
        """Trims the log file to the maximum number of lines specified."""
        if not self.file_logging_enabled:
            return

        assert self.logfile_path is not None, "Log file path must be set before trimming the log file."
        if self.logfile_path.exists() and self.max_lines is not None and self.max_lines > 0:
            # Monitoring log file exists - truncate excess lines if needed.
            with self.logfile_path.open(encoding="utf-8") as file:
                lines = file.readlines()

                if len(lines) > self.max_lines:
                    # Keep the last max_lines rows
                    keep_lines = lines[-self.max_lines:] if len(lines) > self.max_lines else lines

                    # Overwrite the file with only the last 1000 lines
                    with self.logfile_path.open("w", encoding="utf-8") as file2:
                        file2.writelines(keep_lines)

    def log_message(self, message: str, verbosity: str = "summary") -> None:
        """Writes a log message to the console and/or a file based on verbosity settings.

        Args:
            message (str): The message to log.
            verbosity (str): The verbosity level for the message. Must be one of "none", "error", "warning", "summary", "detailed", "debug", or "all".

        Raises:
            ValueError: If an invalid verbosity level is provided.

        """
        if verbosity not in self.verbosity_levels:
            exception_msg = f"log_message(): Invalid verbosity passed, must be one of {list(self.verbosity_levels.keys())}."
            raise ValueError(exception_msg)

        file_verbosity = self.file_verbosity if self.file_verbosity is not None else "none"
        console_verbosity = self.console_verbosity if self.console_verbosity is not None else "none"
        logfile_level = self.verbosity_levels.get(file_verbosity, 0)
        console_level = self.verbosity_levels.get(console_verbosity, 0)
        message_level = self.verbosity_levels.get(verbosity, 0)

        process_str = ""
        if self.log_process_id and self.log_thread_id:
            process_str = f"[Proc {SCCommon.get_process_id()}, Thread {threading.current_thread().name}] "
        elif self.log_process_id:
            process_str = f"[Proc {SCCommon.get_process_id()}] "
        elif self.log_thread_id:
            process_str = f"[Thread {threading.current_thread().name}] "

        # Deal with console message first
        if console_level >= message_level and console_level > 0:
            if verbosity == "error":
                print(f"ERROR: {process_str}{message}", file=sys.stderr)
            elif verbosity == "warning":
                print(f"WARNING: {process_str}{message}")
            else:
                print(f"{process_str}{message}")

        # Now write to the log file if needed
        if self.file_logging_enabled:
            assert self.logfile_path is not None, "Log file path must be set before trimming the log file."
            error_str = " ERROR" if verbosity == "error" else " WARNING" if verbosity == "warning" else ""
            if logfile_level >= message_level and logfile_level > 0:
                with self.logfile_path.open("a", encoding="utf-8") as file:
                    if not message:
                        file.write("\n")
                    else:
                        # Use the local timezone for the log timestamp
                        file.write(f"{DateHelper.now().strftime(self.timestamp_format)}{error_str}: {process_str}{message}\n")

    def register_email_settings(self, email_settings: dict | None) -> None:
        """
        Registers email settings for sending emails.

        Use the SCConfigManager.get_email_settings() method to get a dictionary containing the email settings. Otherwise, you can pass a
        dictionary directly to this method with these keys:
            SendEmailsTo: str, the email address to send emails to
            SMTPServer: str, the SMTP server address
            SMTPPort: int, the SMTP server port (optional, defaults to 587)
            SMTPUsername: str, the username for the SMTP server
            SMTPPassword: str, the password for the SMTP server (preferably an App Password)
            SubjectPrefix: str, a prefix for email subjects (optional, default to None)

        Args:
            email_settings (Optional[dict], optional): A dictionary containing email settings. If empty or None, no email settings will be registered.

        Raises:
            TypeError: If email_settings is not a dictionary.
            ValueError: If any required keys are missing from the email_settings dictionary.

        """
        if email_settings == {} or email_settings is None:
            return  # No email settings provided, so skip registration

        if not isinstance(email_settings, dict):
            msg = "register_email_settings(): Email settings must be a dictionary."
            raise TypeError(msg)

        # Check if all required keys are present
        required_keys = ["SendEmailsTo", "SMTPServer", "SMTPUsername", "SMTPPassword"]
        for key in required_keys:
            if key not in email_settings:
                msg = f"register_email_settings(): Missing required email setting: {key}"
                raise ValueError(msg)

        # Store the email settings in the config object
        self.email_settings = email_settings

    def send_email(self, subject: str, body: str | Path, test_mode: bool = False) -> bool:  # noqa: FBT001, FBT002, PLR0911, PLR0912, PLR0915
        """
        Sends an email using the SMTP server previously specified in register_email_settings().

        Args:
            subject (str): The subject of the email.
            body (str): The body of the email. This argument can be one of 4 things:
                1. A string containing the HTML body of the email
                2. A string or Path containing the path to an HTML file to read the body from
                3. A string containing the text body of the email
                4. A string or Path containing the path to an text file to read the body from
            test_mode (bool, optional): If True, the email will not be sent, but a message will be logged indicating that the email would have been sent. Defaults to False.

        Returns:
            result (bool): True if the email was sent successfully, False otherwise.
        """
        if self.email_settings is None:
            return False  # No email settings registered, so skip sending the email

        # First confirm that the body argument was passed as a string
        if not isinstance(body, str) and not isinstance(body, Path):
            self.log_fatal_error("body argument must be a string containing the body content or a file path.")
            return False

        # See if the body string is something that looks like a file path
        try:
            payload_path = SCCommon.select_file_location(str(body))
        except OSError:
            # Nothing to do here
            payload_path = None

        payload = body  # Default to the body as text content
        payload_type = "plain"

        # Default to treating the body a file path and see if we can resolve it
        if payload_path is not None:
            if payload_path.exists():
                # If the body is a file path, read the content
                with payload_path.open("r", encoding="utf-8") as file:
                    payload = file.read()

                # Determine the payload type based on the file extension
                if payload_path.suffix.lower() == ".html":
                    payload_type = "html"
                elif payload_path.suffix.lower() == ".txt":
                    payload_type = "plain"
                else:
                    self.log_fatal_error(f"Unsupported file type for email body: {payload_path.suffix}")
                    return False
            else:
                payload_path = None

        if payload_path is None:
            # If fall through to here, then the body was not a file path or the file did not exist
            # Assume that the body is a string containing the content
            payload = str(body)  # Default to the body as text content
            if payload.startswith(("<html", "<!DOCTYPE html")):
                payload_type = "html"
            else:
                payload_type = "plain"

        # Load the Gmail SMTP server configuration
        sender_email = self.email_settings.get("SMTPUsername")
        send_to = self.email_settings.get("SendEmailsTo")
        smtp_server = self.email_settings.get("SMTPServer")
        smtp_port = self.email_settings.get("SMTPPort", 587)
        smtp_password = self.email_settings.get("SMTPPassword")

        if not sender_email or not send_to or not smtp_server or not smtp_port or not smtp_password:
            self.log_fatal_error("send_email(): Email settings are incomplete. 'SMTPUsername', 'SendEmailsTo', 'SMTPServer' and 'SMTPPassword' must be provided.")
            return False

        try:
            # Create the email
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = send_to
            if self.email_settings.get("SubjectPrefix", None) is not None:
                msg["Subject"] = self.email_settings.get("SubjectPrefix", "") + subject
            else:
                msg["Subject"] = subject

            # Attach the payload as either plain text or HTML
            part = MIMEText(payload, payload_type)  # type: ignore[arg-type]
            msg.attach(part)

            # Connect to the Gmail SMTP server
            with smtplib.SMTP(host=smtp_server, port=smtp_port, timeout=10) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(sender_email, smtp_password)  # Log in using App Password
                if test_mode:
                    self.log_message(f"Test mode: Email with subject '{msg['Subject']}' would be sent to {send_to}.", "summary")
                else:
                    server.sendmail(sender_email, send_to, msg.as_string())  # Send the email

        except TimeoutError as e:
            self.log_message(f"send_email(): Timeout sending email: {e}", "error")
            return False
        except smtplib.SMTPAuthenticationError as e:
            self.log_message(f"send_email(): Authentication failed: {e}", "error")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            self.log_message(f"send_email(): Recipients refused: {e}", "error")
            return False
        except smtplib.SMTPSenderRefused as e:
            self.log_message(f"send_email(): Sender refused: {e}", "error")
            return False
        except (smtplib.SMTPException, ssl.SSLError) as e:
            self.log_message(f"send_email(): SMTP/SSL error: {e}", "error")
            return False
        except (OSError, ConnectionRefusedError, smtplib.SMTPServerDisconnected) as e:
            self.log_message(f"send_email(): Network error sending email: {e}", "error")
            return False
        except Exception as e:  # noqa: BLE001
            self.log_message(f"send_email(): Unexpected error: {e}", "error")
            return False
        else:
            return True  # Email sent successfully

    def log_fatal_error(self, message: str, report_stack: bool = False, calling_function: str | None = None) -> None:  # noqa: FBT001, FBT002
        """
        Log a fatal error, send an email if configured to so and then exit the program.

        Args:
            message (str): The error message to log.
            report_stack (Optional[bool], optional): If True, include the stack trace in the log message.
            calling_function (Optional[str], optional): The name of the function that called this method, if known. If None, the calling function will be determined automatically.

        Raises:
            SystemExit: Exits the program with a status code of 1 after logging the fatal error.

        """  # noqa: DOC502
        function_name = None
        if calling_function is None:
            stack = inspect.stack()
            # Get the frame of the calling function
            calling_frame = stack[1]
            # Get the function name
            function_name = calling_frame.function
            if function_name == "<module>":
                function_name = "main"
            # Get the class name (if it exists)
            class_name = None
            if "self" in calling_frame.frame.f_locals:
                class_name = calling_frame.frame.f_locals["self"].__class__.__name__
                full_reference = f"{class_name}.{function_name}()"
            else:
                full_reference = function_name + "()"
        else:
            full_reference = calling_function + "()"

        if report_stack:
            stack_trace = traceback.format_exc()
            message += f"\n\nStack trace:\n{stack_trace}"

        self.log_message(f"Function {full_reference}: FATAL ERROR: {message}", "error")

        # Try to send an email if configured to do so and we haven't already sent one for a fatal error
        # Don't send concurrent error emails
        if function_name != "send_email" and not self.get_fatal_error():
            self.send_email(
                f"{self.app_dir.name} terminated with a fatal error",
                f"{message} \nAdditional emails will not be sent for concurrent errors.",
            )

        # record the error in in a file so that we keep track of this next time round
        self.set_fatal_error(message)

        # Exit the program
        sys.exit(1)

    def get_fatal_error(self) -> bool:
        """Returns True if a fatal error was previously reported, false otherwise."""
        return Path(self.fatal_error_file_path).exists()

    def clear_fatal_error(self) -> bool:
        """
        Clear a previously logged fatal error.

        Returns:
            result (bool): True if the file was deleted, False if it did not exist.
        """
        if Path(self.fatal_error_file_path).exists():
            Path(self.fatal_error_file_path).unlink()
            return True
        return False

    def set_fatal_error(self, message: str) -> None:
        """
        Create a fatal error tracking file and write the message to it.

        Args:
            message (str): The error message to write to the fatal error file.
        """
        with Path(self.fatal_error_file_path).open("w", encoding="utf-8") as file:
            file.write(message)

    def report_notifiable_issue(self, entity: str, issue_type: str, send_delay: int, message: str) -> bool:
        """
        Log a notifiable issue and send an email if configured to do so.

        When a new combination of entity and issue_type is reported, it will be noted including the current timestamp.
        If one or more issues of the same type are reported for the same entity at least send_delay seconds after the last notification,
        an email will be sent including the first time this issue was reported. Subsequent issues of the same type for the same
        entity will be ignored until the issue is cleared.

        Args:
            entity (str): The entity reporting the issue (e.g., "Device 123", "Module", etc.)
            issue_type (str): A brief description of the issue (e.g. "Offline").
            send_delay (int): The delay in seconds before sending the email
            message (str): The issue message to log and email.

        Returns:
            result (bool): True if the email was sent, False otherwise.
        """
        # Search self.notifiable_issues to see if we have a match by entity and issue_type
        now = DateHelper.now()
        issue_found = False
        for issue in self.notifiable_issues:
            if issue.entity == entity and issue.issue_type == issue_type:
                issue_found = True
                # We have a match - see if we need to send an email
                if (now - issue.first_reported).total_seconds() >= issue.send_delay:
                    # Update the last reported time
                    issue.last_reported = now

                    # Send the email if not already sent
                    if not issue.email_sent:
                        email_subject = f"{self.app_dir.name} - {entity} {issue_type} issue"
                        email_body = f"{entity}: {message}\n\nFirst reported: {issue.first_reported.strftime('%Y-%m-%d %H:%M')}"
                        if self.send_email(email_subject, email_body):
                            issue.email_sent = True
                            return True

                break

        if not issue_found:
            # No existing issue found, create a new one
            new_issue = NotifiableIssue(
                entity=entity,
                issue_type=issue_type,
                first_reported=now,
                last_reported=now,
                send_delay=send_delay,
                message=message,
            )
            self.notifiable_issues.append(new_issue)

        return False

    def clear_notifiable_issue(self, entity: str, issue_type: str) -> bool:
        """
        Clear a notifiable issue.

        Args:
            entity (str): The entity reporting the issue (e.g., "Device 123", "Module", etc.)
            issue_type (str): A brief description of the issue (e.g. "Offline").

        Returns:
            result (bool): True if the issue was found and cleared, False otherwise.
        """
        # Search self.notifiable_issues to see if we have a match by entity and issue_type
        for issue in self.notifiable_issues:
            if issue.entity == entity and issue.issue_type == issue_type:
                self.notifiable_issues.remove(issue)
                return True

        return False
