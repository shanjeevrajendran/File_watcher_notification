from crontab import CronTab
import os,traceback
import PySimpleGUI as sg
import configparser

def fetch_configurations():
    form = sg.FlexForm('Inputs for Automated Notification') 
    layout = [
              [sg.Text('Please enter the configuration details:')],
              [sg.Text('Source Folder', size=(15, 1), auto_size_text=True, justification='right'), sg.InputText('Enter the folder to be watched'),sg.FolderBrowse()],
              [sg.Text('From mail id', size=(15, 1), auto_size_text=True, justification='right'), sg.InputText('Please enter your gmail address'),],
              [sg.Text('Password', size=(15, 1), auto_size_text=True, justification='right'), sg.InputText('Please enter your gmail password')],
              [sg.Text('To address', size=(15, 1), auto_size_text=True, justification='right'), sg.InputText('Please enter the email addresses for notification')],
              [sg.Submit(), sg.Cancel()]
             ]
    button, values = form.Layout(layout).Read()


    if button == 'Cancel' or None:
        values = {x:None for x,y in values.items()}
        form.Close()

    return([values[0], values[1], values[2], values [3]])

def create_config_file(config_file):
    values_dict = {}
    open(config_file, 'a').close()
    values = fetch_configurations()
    values_dict['folder_path'] = values[0]
    values_dict['mail_id'] = values[1]
    values_dict['password'] = values[2]
    values_dict['to'] = values[3]
    return(values_dict)
    
def create_cron():
    my_cron = CronTab(user=True)
        
    job = my_cron.new(command=f"{os.environ['_']} '{os.getcwd()}/Automated_notification.py'")
    job.minute.on(0)
    job.hour.on(9)
    job.dow.on('MON','TUE', 'WED', 'THU', 'FRI')

    my_cron.write()

    for job in my_cron:
        print(job)
    
def main():    
    config_file = f"./config.cfg"
    if not (os.path.exists(config_file)) or (os.stat(config_file).st_size == 0):
        values_dict = create_config_file(config_file)
        parser = configparser.ConfigParser()
        parser.add_section('Credentials')
        parser['Credentials']['folder_path'] = values_dict['folder_path']
        parser['Credentials']['mail_id'] = values_dict['mail_id']
        parser['Credentials']['password'] = values_dict['password']
        parser['Credentials']['to'] = values_dict['to']
        with open(config_file, 'w') as f:
            parser.write(f)
    create_cron()

if __name__ == '__main__':
    try:
        main()
    except:
        print(traceback.format_exc())
    else:
        print('Done!')
