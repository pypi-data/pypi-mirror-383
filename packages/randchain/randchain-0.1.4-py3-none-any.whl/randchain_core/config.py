class EmailConfig:
    def __init__(self, sender_email :  str, password : str, recipient_email : str, subject : str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.sender_email = sender_email
        self.password = password
        self.recipient_email = recipient_email
        self.subject = subject
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port


class Whatsappconfig:
    def __init__(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.to_number = to_number
    
    
    
   