import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database.Repository import Market, Bet

logging.basicConfig(level=logging.INFO)

class AlertService:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password, from_email, to_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.to_email = to_email
        logging.info("AlertService initialized.")

    def send_alert(self, subject, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, self.to_email, msg.as_string())
            logging.info("Alert sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")

    def send_market_alert(self, market : Market):

      
        logging.info("Sending bet alert.")
        alert_message = ""
        event = market.event.split("(")[0]
        alert_message += (
            f"Sport {market.sport} \n"
            f"League: {market.league} \n"
            f"Event: {event} \n"
            f"Market: {market.market} \n"
            f"Bet Name: {market.bet_name} \n"
        )
        logging.info(f"Alert message: {alert_message}")
        self.send_alert("Positive EV Bet:", f"{alert_message}")
    