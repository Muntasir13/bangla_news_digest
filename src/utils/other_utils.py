import hashlib
import mimetypes
import os
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage


def get_start_and_end_date(end_timedelta: int, today: bool = True, start_timedelta: float | None = None) -> tuple[datetime, datetime]:
    """As the method name suggests, we get start and end date.

    Args:
        end_timedelta (int): the timedelta to get the end date
        today (bool, optional): whether we are taking today's date. Defaults to True.
        start_timedelta (int | None, optional): If we are not taking today's date,
        then the timedelta to get the start date. Defaults to None.

    Returns:
        tuple[datetime, datetime]: yesterday's and today's date in
        datetime format
    """
    start_date = datetime.now()
    if not today and start_timedelta:
        start_date -= timedelta(days=start_timedelta)
    end_date = datetime.now() - timedelta(days=end_timedelta)
    return (
        start_date.replace(hour=7, minute=0, second=0),
        end_date.replace(hour=7, minute=0, second=0),
    )


def compute_news_article_fingerprint(title: str | None, body: str | None) -> str:
    text = (title or "") + "\n" + (body or "")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def send_email(
    smtp_config: dict[str, str | int],
    email_subject: str,
    email_body: str,
    from_addr: str,
    to_addr: list[str],
    cc_addr: list[str] | None = None,
    bcc_addr: list[str] | None = None,
    attachment_path: str | None = None,
    starttls: bool = True,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = email_subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addr)
    if cc_addr:
        msg["Cc"] = ", ".join(cc_addr)

    # plain text body
    msg.set_content(email_body)

    if attachment_path:
        email_file_attachment(attachment_path, msg)
    # aggregate recipients
    recipients = list(to_addr)
    if cc_addr:
        recipients += cc_addr
    if bcc_addr:
        recipients += bcc_addr

    with smtplib.SMTP(str(smtp_config["host"]), int(smtp_config["port"])) as server:
        server.ehlo()
        if starttls:
            server.starttls()
            server.ehlo()
        server.login(str(smtp_config["user"]), str(smtp_config["password"]))
        server.send_message(msg, from_addr=from_addr, to_addrs=recipients)
    return


def email_file_attachment(attachment_path: str, msg: EmailMessage) -> None:
    filename = os.path.basename(attachment_path)
    ctype, encoding = mimetypes.guess_type(attachment_path)
    if ctype is None or encoding is not None:
        # default for unknown types
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)

    with open(attachment_path, "rb") as f:
        file_data = f.read()

    # docx MIME type is commonly:
    # application/vnd.openxmlformats-officedocument.wordprocessingml.document
    msg.add_attachment(
        file_data,
        maintype=maintype,
        subtype=subtype,
        filename=filename,
    )

    return
