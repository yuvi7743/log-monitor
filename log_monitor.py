import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import smtplib
from email.mime.text import MIMEText

class LogHandler(FileSystemEventHandler):
    def __init__(self, log_file):
        self.log_file = log_file
        self._load_existing_logs()
        print(f"Monitoring started on {self.log_file}")

    def _load_existing_logs(self):
        with open(self.log_file, 'r') as file:
            self.logs = file.readlines()
        print("Loaded existing logs")

    def on_modified(self, event):
        print(f"Event detected: {event}")
        if event.src_path == self.log_file:
            print(f"Detected modification in {self.log_file}")
            self._check_new_logs()

    def _check_new_logs(self):
        with open(self.log_file, 'r') as file:
            new_logs = file.readlines()

        new_entries = [line for line in new_logs if line not in self.logs]
        self.logs = new_logs

        for entry in new_entries:
            if "ERROR" in entry:  # Change the condition as needed
                print(f"Error found: {entry}")
                self.send_alert(entry)

    def send_alert(self, message):
        print("Sending alert...")
        from_addr = os.getenv("EMAIL_USER")
        to_addr = "recipient_email@gmail.com"
        subject = "Log Alert"
        body = f"New error in log file:\n\n{message}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_addr, os.getenv("EMAIL_PASS"))
            server.sendmail(from_addr, [to_addr], msg.as_string())

if __name__ == "__main__":
    log_file = "C:\\logs\\test.log"  # Update this path as needed
    event_handler = LogHandler(log_file)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(log_file), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
