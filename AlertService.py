import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    def analyze_data(self, data):
        if not data.empty:
            logging.info("Analyzing data.")
            alert_message = ""
            for i in range(min(3, len(data))):
                row = data.iloc[i]
                if row['Event'] is None:
                    continue
                event = row['Event'].split("(")[0]
                alert_message += (
                    f"Worst-Case%: {row['Worst-Case%']}, "
                    f"Event: {event}, "
                    f"Market: {row['Market']}, "
                    f"Bet Name: {row['Bet Name']}, "
                    f"Odds: {row['Odds']}, "
                    f"Sportsbook: {row['Sportsbook']}, "
                    f"Fair Odds: {row['Fair Odds']}, "
                    f"Books: {row['Books']}\n"
                )
            logging.info(f"Alert message: {alert_message}")
            self.send_alert("Positive EV Bets:", f"{alert_message}")
        else:
            logging.info("No positive ev bets found.")