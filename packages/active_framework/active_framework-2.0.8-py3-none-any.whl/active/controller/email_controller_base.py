import smtplib

from email.mime.text import MIMEText

class EmailControllerBase():
    '''
    Base class for sending emails over SMTP.
    
    ACTIVE environment file prototype:
    
    {
        "password": "password", 
        "smtp_port": 587, 
        "smtp_url": "smtp.gmail.com", 
        "username": "myname@company.com"
    }
    
    Parameters:
        password: String password for the email account.
        smtp_port: Integer port number for the SMTP server.
        smtp_url: String url for the SMTP server.
        username: String username for the email account.
    '''
    
    def __init__(self, password="", smtp_port=0, smtp_url="", username=""):
        '''
        The default constructor.
        
        Args:
            password: String password for the email account.
            smtp_port: Integer port number for the SMTP server.
            smtp_url: String url for the SMTP server.
            username: String username for the email account.        
        '''

        # Save the data members
        self.password = password
        self_smtp_port = smtp_port
        self.smtp_url = url
        self.username = username
        
    def send(self, from_address, to_address, message, subject):
        '''
        Send an email.
        
        Args:
            from_addres: String address for the 
        '''
        
        # Construct the message to send
        msg = MIMEText(message)
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # Connect to the server and send the message
        server = smtplib.SMTP(self.smtp_url, self.smtp_port)
        server.ehlo()
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(from_address, [to_address], msg.as_string())
        server.quit()
