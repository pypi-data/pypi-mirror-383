import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from randchain_core.config import EmailConfig, Whatsappconfig


def txt_writer(file_path, text):
    with open(file_path, "w") as f:
        f.write(text)
    return True


def output_conversion(output_type, original_output, function_name):
    try:
        if output_type == "int":
            return int(original_output)
        elif output_type == "str":
            return str(original_output)
        elif output_type == "float":
            return float(original_output)
    except Exception as e:
        print("Error in conversion: ", e)
        raise TypeError(f"Output of {function_name} is not convertable.")
    return original_output


def send_email(
        email_config : EmailConfig,
    body: str
):
    """
    Send an email using SMTP.
    
    Args:
        sender_email (str): Email address of sender.
        password (str): Password or app password of sender.
        recipient_email (str): Email address of recipient.
        subject (str): Email subject line.
        body (str): Email message body.
        smtp_server (str): SMTP server host (default: Gmail).
        smtp_port (int): SMTP server port (default: 587).
    """
    try:
        sender_email = email_config.sender_email
        recipient_email = email_config.recipient_email
        subject = email_config.subject
        smtp_server = email_config.smtp_server
        smtp_port = email_config.smtp_port
        password = email_config.password

        # Create email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)

        # Send email
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent to {recipient_email}")
        return True

    except Exception as e:
        print("❌ Error sending email:", e)
        return False
    

def send_whatsapp(whatsapp_config: Whatsappconfig, message: str):
    from twilio.rest import Client
    try:
        account_sid = whatsapp_config.account_sid
        auth_token = whatsapp_config.auth_token
        from_number = whatsapp_config.from_number
        to_number = whatsapp_config.to_number
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            from_=from_number,
            body=message,
            to=to_number
        )
        print(f"✅ Message sent successfully!")
        return msg.status
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")
        return False