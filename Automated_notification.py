#!/usr/bin/env python
# coding: utf-8

import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import traceback,logging
import configparser
import datetime
import smtplib, os


def timeit(method):
    def timed(*args,**kwargs):
        ts = time.time()
        result = method(*args,**kwargs)
        te = time.time()
        print(f'{method.__name__} ---> {te-ts:.2f} seconds')
        return result
    return timed


class CustomLoggingEventHandler(LoggingEventHandler):
    """Logs for created and deleted events"""

    def __init__(self, logger):
        self.logger = logger

    def on_created(self, event):
        super().on_created(event)

        if not event. is_directory:
            self.logger.info("Created %s: %s", 'file', event.src_path)

    def on_deleted(self, event):
        super().on_deleted(event)

        if not event. is_directory:
            self.logger.info("Deleted %s: %s", 'file', event.src_path)


class Mail():
    def __init__(self, conn_dict):
        self.conn_dict = conn_dict
        self.gmail_user = self.conn_dict['mail_id']
        self.gmail_password = self.conn_dict['password']
        self.to = self.conn_dict['to']

    def send_mail(self,subject, body):
        self.subject = subject
        self.body = body
        self.email_text = "\r\n".join([
          f"From: {self.gmail_user}",
          f"To: {', '.join(self.to.split(','))}",
          f"Subject: {self.subject}",
          "",
          f"{self.body}"
          ])
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com') as server:
                server = smtplib.SMTP_SSL('smtp.gmail.com')
                server.ehlo()
                server.login(self.gmail_user, self.gmail_password)
                server.sendmail(self.gmail_user, self.to, self.email_text)
        except Exception as e:
            print (f'Mail not sent due to following error >>> {e}')


class MyHandler(CustomLoggingEventHandler, Mail):
    
    def __init__(self,logger ,conn_dict ):
        CustomLoggingEventHandler.__init__(self,logger)
        Mail.__init__(self,conn_dict)
    @timeit    
    def on_created(self, event):
        file_name = os.path.basename(event.src_path)
        subject = f'{file_name} file_created'
        body = '-,\nScript Notification'
        Mail.send_mail(self,subject,body)
    @timeit    
    def on_deleted(self, event):
        file_name = os.path.basename(event.src_path)
        subject = f'{file_name} file_deleted'
        body = '-,\nScript Notification'
        Mail.send_mail(self,subject,body)


@timeit 
def config_unpacker(config_file):
    try:
        config = configparser.RawConfigParser()
        config.read(config_file)
        credentials = {key:value for key, value in config._sections['Credentials'].items()}
        return(credentials)
    except Exception as e:
        print(f'Error reading the config file :{e}')


def main():
    config_file = "./config.cfg"
    conn_dict = config_unpacker(config_file)
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    path = conn_dict['folder_path']
    if not os.path.exists(f"{path}/log"):
        os.makedirs(f"{path}/log") 
    log_filename = f"{path}/log/{today}'s log.log"

    logging.basicConfig(filename=log_filename,
                        level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%H:%M:%S')
    logger = logging.getLogger("{today}'s log")

    observer = Observer()
    observer.schedule(MyHandler(logger ,conn_dict ), path=path, recursive= False)
    observer.start()
    try:
        while datetime.datetime.now().hour < 18:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    try:
        main()
    except:
        print(traceback.format_exc())
    else:
        print('Done!')



