import os, csv, time
from datetime import datetime, timedelta
from calendar import monthrange

from flask import current_app as app
from jinja2 import Template
from weasyprint import HTML
from celery.schedules import crontab

from application.models import User, Board, List, Card
from application.database_queries import get_list_by_id, get_board_by_id, get_list_user, get_board_user
from .workers import celery
from .webhooks import gchat

#----------------------------------------------SETUP---------------------------------------------#

import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, body, attachment=None):
    # initialize mail object
    mail = MIMEMultipart()
    
    # add fields
    mail['From'] = app.config['SENDER_ADDRESS']
    mail['To'] = to
    mail['Subject'] = subject
    mail.attach(MIMEText(body, 'html'))
    if attachment:
        filename=attachment.split('/')[-1]
        with open(attachment, 'rb') as attachment:
            # convert file to application/octet-stream
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            # encode to base64
            encoders.encode_base64(part)
            # add header for filename
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            # finally add to the mail
            mail.attach(part)

    # connect to SMTP server
    s = smtplib.SMTP(host=app.config['SMTP_SERVER_HOST'], port=app.config['SMTP_SERVER_PORT'])

    # login to SMTP server with credentials
    s.login(app.config['SENDER_ADDRESS'], app.config['SENDER_PASSWORD'])

    # sending the mail
    s.send_message(mail)

    # closing the connection
    s.quit()

    return "Successfully sent mail!"

def generate_report(user_id, format):
    current_date = datetime.today()
    month_range = monthrange(current_date.year, current_date.month)
    first_date_tm = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    date_prev_month = first_date_tm - timedelta(days=1)
    prev_month_range = monthrange(date_prev_month.year, date_prev_month.month)

    first_date = date_prev_month.replace(day=1)
    last_date = date_prev_month.replace(day=prev_month_range[1], hour=23, minute=59, second=59)
    numdays = prev_month_range[1]
    date_list = [first_date + timedelta(days=x) for x in range(numdays)]
    data = {
        'month_year': first_date.strftime('%B, %Y'),
        'task_count': 0,
        'complete_count': 0,
        'pending_count': 0,
        'overdue_count': 0,
        'user': User.query.get(user_id),
        'timeline': {date:0 for date in date_list}
    }
    for board in data['user'].boards:
        for lst in board.lists:
            data['task_count'] += len(lst.cards)
            for card in lst.cards:
                if first_date <= card.created <= last_date:
                    if card.completed:
                        data['complete_count'] += 1
                        if card.completed_datetime.date() in date_list:
                            data['timeline'][card.completed.date()] += 1
                    elif card.deadline is not None and datetime.now() > card.deadline:
                        data['overdue_count'] += 1
                    else:
                        data['pending_count'] += 1
    if format == 'html':
        ATTACHMENT_URI = os.path.join(app.config["REPORTS_DIR"],f'monthly_report_{user_id}_{datetime.now().month}_{datetime.now().year}.html')
        with open(app.config['REPORT_TEMPLATE']) as report_template:
            template = Template(report_template.read())
            report = template.render(**data)
            with open(ATTACHMENT_URI,'w') as f:
                f.write(report)
    elif format == 'pdf':
        ATTACHMENT_URI = os.path.join(app.config["REPORTS_DIR"],f'monthly_report_{user_id}_{datetime.now().month}_{datetime.now().year}.pdf')
        with open(app.config['REPORT_TEMPLATE']) as report_template:
            template = Template(report_template.read())
            report = template.render(**data)
            html = HTML(string=report)
            html.write_pdf(target=ATTACHMENT_URI)
    return ATTACHMENT_URI
#------------------------------------------------------------------------------------------------#

# SCHEDULER
@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    
    # scheduling daily reminder task for UTC 7:00PM everyday
    sender.add_periodic_task(crontab(hour=7), daily_reminders.s(), name='daily reminders')
    # scheduling monthly email reports for 1st of every month
    sender.add_periodic_task(crontab(day_of_month=1), monthly_report.s(), name='monthly progress report')
    
    # testing
    # sender.add_periodic_task(120, daily_reminders.s(), name='daily reminders')
    # sender.add_periodic_task(10, monthly_report.s(), name='monthly progress report')

# SCHEDULED JOB 1 --- DAILY REMINDER
@celery.task()
def daily_reminders():
    send_count = 0
    for user in User.query.all():
        if user.send_daily_reminders:
            pending = 0
            pending_cards = []
            for board in user.boards:
                for lst in board.lists:
                    for card in lst.cards:
                        if not card.completed:
                            pending += 1
                            if card.deadline:
                                if card.deadline > datetime.now():
                                    if (card.deadline - datetime.now()).days > 0:
                                        remaining = f'Due in {(card.deadline - datetime.now()).days} days'
                                    elif (card.deadline - datetime.now()).seconds // 3600 > 1:
                                        remaining = f'Due in {(card.deadline - datetime.now()).seconds // 3600} hours'
                                    elif (card.deadline - datetime.now()).seconds // 3600 == 1:
                                        remaining = f'Due in an hour and {(card.deadline - datetime.now()).seconds // 60} minutes'
                                    else:
                                        remaining = 'Due in less than an hour'
                                else:
                                    if (datetime.now() - card.deadline).days > 0:
                                        remaining = f'{(datetime.now() - card.deadline).days} days past due'
                                    elif (datetime.now() - card.deadline).seconds // 3600 > 1:
                                        remaining = f'{(datetime.now() - card.deadline).seconds // 3600} hours past due'
                                    elif (datetime.now() - card.deadline).seconds // 3600 == 1:
                                        remaining = f'One hour and {(datetime.now() - card.deadline).seconds // 60} minutes past due'
                                    else:
                                        remaining = 'Less than an hour past due'
                            else:
                                remaining = 'No deadline'
                            pending_cards.append({
                                'title': card.title,
                                'time_remaining' : remaining,
                                'content' : card.content
                            })
            
            if len(pending_cards) > 0:
                res = gchat(user.username, pending_cards)
                send_count += 1
        
    return f"Succesfully sent push messages to {send_count} users!"

# SCHEDULED JOB 2 ---- MONTHLY REPORTS
@celery.task()
def monthly_report():
    send_count = 0
    error_count = 0
    for user in User.query.all():
        # generating email body
        with open(app.config['EMAIL_TEMPLATE']) as mail_template:
            template = Template(mail_template.read())
            mail_body = template.render(user=user)
        
        # generating email attachment
        ATTACHMENT_URI = generate_report(user.id, user.monthly_report_format)
        
        # sending email
        try:
            send_email(to=user.email, subject="Monthly Progress Report", body=mail_body, attachment=ATTACHMENT_URI)
        except Exception as e:
            print(e)
            error_count += 1
        else:
            send_count += 1
    return f"Successfully sent emails to {send_count} users! Error while sending to {error_count} users."

# ---------------------------------------------------------------------------------------------- #

# USER TRIGGERED ASYNC JOBS
@celery.task(bind=True)
def list_export_csv(self, list_id):
    list_obj = get_list_by_id(list_id)
    data = [['Sl.no', 'Created on', 'Last Updated on', 'Title', 'Description', 'Deadline', 'Completed', 'Completed on']]
    uname, bname, lname = get_list_user(list_id).username, list_obj.board.board_name, list_obj.list_name
    total = len(list_obj.cards)
    for index, card in enumerate(list_obj.cards):
        last_updated = '-' if card.updated is None else card.updated
        content = '-' if card.content is None else card.content
        deadline = '-' if card.deadline is None else card.deadline
        completed = 'yes' if card.completed is True else 'no'
        completed_on = card.completed_datetime if card.completed_datetime is not None else '-'
        row = [
                index+1,
                card.created,
                last_updated,
                card.title,
                content,
                deadline,
                completed,
                completed_on
            ]
        data.append(row)
        # time.sleep(1)
        self.update_state(state='PROGRESS', meta={'current': index+1, 'total': total, 'status': 'Export in progress...'})
    
    FILE_NAME = f"EXPORT-{'-'.join(uname.split(' '))}-{'-'.join(bname.split(' '))}-{'-'.join(lname.split(' '))}-{'-'.join(str(datetime.now()).replace(':','').split(' '))}.csv"
    FILE_URI = os.path.join(app.config['EXPORT_DIR'], FILE_NAME)
    
    with open(FILE_URI, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

    return { 'current': total, 'total': total, 'status': 'Export finished!', 'result': {'file_name': FILE_NAME } }

@celery.task(bind=True)
def board_export_csv(self, board_id):
    board_obj = get_board_by_id(board_id)
    data = [['Sl.no', 'Created on', 'List name', 'Number of cards', 'Number of pending cards', 'Number of completed cards', 'Number of overdue cards']]
    uname, bname = get_board_user(board_id).username, board_obj.board_name
    total = len(board_obj.lists)
    for index, lst in enumerate(board_obj.lists):
        completed = 0
        pending = 0
        overdue = 0
        for card in lst.cards:
            if card.completed == True:
                completed += 1
            elif card.deadline and card.deadline < datetime.now():
                overdue += 1
            else:
                pending += 1
        row = [
                index+1,
                lst.created,
                lst.list_name,
                len(lst.cards),
                pending,
                completed,
                overdue
            ]
        data.append(row)
        self.update_state(state='PROGRESS', meta={'current': index+1, 'total': total, 'status': 'Export in progress...'})
    
    FILE_NAME = f"EXPORT-{'-'.join(uname.split(' '))}-{'-'.join(bname.split(' '))}-{'-'.join(str(datetime.now()).replace(':','').split(' '))}.csv"
    FILE_URI = os.path.join(app.config['EXPORT_DIR'], FILE_NAME)
    
    with open(FILE_URI, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

    return { 'current': total, 'total': total, 'status': 'Export finished!', 'result': {'file_name': FILE_NAME } }