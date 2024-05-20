import logging
import re
import paramiko
import os
import psycopg2

from psycopg2 import Error
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(),override=True, verbose=True)

TOKEN = os.getenv('TOKEN')

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8", level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def echo(update: Update, context):
    message_text = update.message.text
    update.message.reply_text(message_text)
    logger.info(f'User {update.effective_user.username} sent message: {message_text}')

def find_emailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    logger.info("The user requested a search for email addresses")
    return 'find_email'

def find_email(update: Update, context):
    user_input = update.message.text
    update.message.reply_text("Hello")

    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_list = email_regex.findall(user_input)

    if not email_list:
        update.message.reply_text('Email-адреса не найдены')
        logging.info("Emails not found")
        return ConversationHandler.END
    
    emails = '\n'.join(email_list)
    context.user_data['email_list'] = email_list
    update.message.reply_text(f'Найденные email-адреса:\n{emails}')

    update.message.reply_text('Хотите сохранить найденные email-адреса в базе данных? (Да/Нет)')
    logger.info("The following email addresses were found:\n" + emails)
    return 'save_email'

def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    logger.info("The user requested a search for phone numbers")
    return 'find_phone_number'

def find_phone_number(update: Update, context):
    user_input = update.message.text 

    phoneNumRegex = re.compile(r'(?:\+7|8)[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}(?!\d)')
    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        logger.info("No phone numbers found")
        return ConversationHandler.END
    
    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n'  # Записываем очередной номер
    
    context.user_data['phoneNumberList'] = phoneNumberList
    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    logger.info("The following phone numbers were found:\n" + phoneNumbers)
    
    update.message.reply_text('Хотите сохранить найденные номера в базе данных? (Да/Нет)')
    return 'save_phone_number'

def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')
    logger.info("The user has requested password verification")
    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text

    # Пароль должен содержать не менее восьми символов,
    # включая как минимум одну заглавную букву, одну строчную букву,
    # одну цифру и один специальный символ.
    passwordRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')

    if passwordRegex.match(user_input):
        update.message.reply_text('Пароль сложный')
        logger.info("Password is difficult")
    else:
        update.message.reply_text('Пароль простой')
        logger.info("Password is simple")

    return ConversationHandler.END

def get_release(update: Update, context):
    logger.info("get_release requested")
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('cat /etc/*-release')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    return ConversationHandler.END

def get_uname (update: Update, context):
    logger.info("get_uname requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END

def get_uptime (update: Update, context):
    logger.info("get_uptime requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_df (update: Update, context):
    logger.info("get_df requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_free (update: Update, context):
    logger.info("get_free requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_mpstat (update: Update, context):
    logger.info("get_mpstat requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_w (update: Update, context):
    logger.info("get_w requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_auths (update: Update, context):
    logger.info("get_auths requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_critical (update: Update, context):
    logger.info("get_critical requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('journalctl -p crit -n 5')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_ps (update: Update, context):
    logger.info("get_ps requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('ps aux | tail -n 6')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_ss (update: Update, context):
    logger.info("get_ss requested")
    
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('ss -tuln')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите: <название пакета> для вывода определенного пакета или all для вывода всех(5) пакетов')
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    logger.info("get_apt_list requested")
    user_input = update.message.text.strip()

    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    if user_input.lower() == 'all':
        command = 'apt list --installed | tail -n 5'
    else:
        command = f'apt show {user_input}'
    
    stdin, stdout, stderr = client.exec_command(command)
    
    data = stdout.read().decode('utf-8')

    if not data.strip(): 
        logging.info(f'Package: {user_input} not found or empty output') 
        update.message.reply_text(f'Пакет: {user_input} не найден или нет данных')
        client.close()
        return ConversationHandler.END
    
    logging.info(f'Package: {user_input} is found') 
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_services (update: Update, context):
    logger.info("get_services requested")
     
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info(f'Connected via ssh to {host}') 

    stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service --state=running | tail -n 10')
    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END

def get_repl_logs (update: Update, context):
    logger.info("get_repl_logs requested")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("RM_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_DATABASE")
    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        cursor = connection.cursor()
        query = """
        SELECT pg_read_file('/var/log/postgresql/logfile.log') AS logfile;
        """
        cursor.execute(query)
        file_content = cursor.fetchone()[0]

        max_lines = 10
        lines_with_replication = file_content.split('\n')[-max_lines:]
        lines_with_replication = [line for line in lines_with_replication if 'replication' in line]

        update.message.reply_text("\n".join(lines_with_replication))
    except (Exception, Error) as error:
        logging.error("Error in PostgreSQL: %s", error)
        update.message.reply_text(f'Произошла ошибка{error}') # Отправляем сообщение пользователю
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    return ConversationHandler.END

def get_email (update: Update, context):
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("RM_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_DATABASE")
    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        cursor = connection.cursor()
        cursor.execute("SELECT email FROM email_addresses;")
        data = cursor.fetchall() 
        logging.info("Command is done")
    
    except (Exception, Error) as error:
        logging.error("Error in PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    logging.info(f'Connected to {host}') 

    update.message.reply_text(data)
    return ConversationHandler.END

def get_phone_numbers (update: Update, context):
    
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("RM_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_DATABASE")

    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phone_numbers;")
        data = cursor.fetchall() 
        logging.info("Command is done")
    
    except (Exception, Error) as error:
        logging.error("Error in PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    logging.info(f'Connected to {host}') 

    update.message.reply_text(data)
    return ConversationHandler.END

def save_email (update: Update, context):
    logging.info(f'saving emails') 
    confirmation = update.message.text.lower().strip()
    if confirmation == 'да':
        # Получение найденных email-адресов из контекста
        email_list = context.user_data.get('email_list')
        if email_list:
            try:
                user = os.getenv("DB_USER")
                password = os.getenv("DB_PASSWORD")
                host = os.getenv("RM_HOST")
                port = os.getenv("DB_PORT")
                database = os.getenv("DB_DATABASE")
                connection = psycopg2.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=database
                )

                cursor = connection.cursor()
                # Вставка email-адресов в базу данных
                for email in email_list:
                    cursor.execute("INSERT INTO email_addresses (email) VALUES (%s);", (email,))
                connection.commit() 
                logging.info("Email addresses have been successfully added to the database")
                update.message.reply_text("Email-адреса успешно добавлены в базу данных.")
            except (Exception, psycopg2.Error) as error:
                logging.error("Error in PostgreSQL: %s", error)
                update.message.reply_text(f"Произошла ошибка при добавлении email-адресов в базу данных.{error}")
            finally:
                if connection is not None:
                    cursor.close()
                    connection.close()
        else:
            update.message.reply_text("Нет email-адресов для добавления.")
    else:
        update.message.reply_text('Email-адреса не сохранены')

    return ConversationHandler.END

def save_phone_number (update: Update, context):
    logging.info(f'saving phone numbers') 
    confirmation = update.message.text.lower().strip()
    if confirmation == 'да':
        phoneNumberList = context.user_data.get('phoneNumberList')
        if phoneNumberList:
            try:
                user = os.getenv("DB_USER")
                password = os.getenv("DB_PASSWORD")
                host = os.getenv("RM_HOST")
                port = os.getenv("DB_PORT")
                database = os.getenv("DB_DATABASE")
                connection = psycopg2.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=database
                )

                cursor = connection.cursor()
                for phoneNumber in phoneNumberList:
                    cursor.execute("INSERT INTO phone_numbers (phone_number) VALUES (%s);", (phoneNumber,))
                connection.commit() 
                logging.info("Phone numbers have been successfully added to the database")
                update.message.reply_text("Номера телефонов успешно добавлены в базу данных.")
            except (Exception, psycopg2.Error) as error:
                logging.error("Error in PostgreSQL: %s", error)
                update.message.reply_text("Произошла ошибка при добавлении номеров телефонов в базу данных.")
            finally:
                if connection is not None:
                    cursor.close()
                    connection.close()
        else:
            update.message.reply_text("Нет номеров телефонов для добавления.")
    else:
        update.message.reply_text('Номера телефонов не сохранены')

    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'save_email': [MessageHandler(Filters.text & ~Filters.command, save_email)],
        },
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'save_phone_number': [MessageHandler(Filters.text & ~Filters.command, save_phone_number)],
        },
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_release', get_release)],
        states={'get_release': [MessageHandler(Filters.text & ~Filters.command, get_release)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_uname', get_uname)],
        states={'get_uname': [MessageHandler(Filters.text & ~Filters.command, get_uname)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_uptime', get_uptime)],
        states={'get_uptime': [MessageHandler(Filters.text & ~Filters.command, get_uptime)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_df', get_df)],
        states={'get_df': [MessageHandler(Filters.text & ~Filters.command, get_df)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_free', get_free)],
        states={'get_free': [MessageHandler(Filters.text & ~Filters.command, get_free)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_mpstat', get_mpstat)],
        states={'get_mpstat': [MessageHandler(Filters.text & ~Filters.command, get_mpstat)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_w', get_w)],
        states={'get_w': [MessageHandler(Filters.text & ~Filters.command, get_w)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_auths', get_auths)],
        states={'get_auths': [MessageHandler(Filters.text & ~Filters.command, get_auths)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_critical', get_critical)],
        states={'get_critical': [MessageHandler(Filters.text & ~Filters.command, get_critical)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_ps', get_ps)],
        states={'get_ps': [MessageHandler(Filters.text & ~Filters.command, get_ps)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_ss', get_ss)],
        states={'get_ss': [MessageHandler(Filters.text & ~Filters.command, get_ss)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_services', get_services)],
        states={'get_services': [MessageHandler(Filters.text & ~Filters.command, get_services)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_repl_logs', get_repl_logs)],
        states={'get_repl_logs': [MessageHandler(Filters.text & ~Filters.command, get_repl_logs)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_email', get_email)],
        states={'get_email_addresses': [MessageHandler(Filters.text & ~Filters.command, get_email)]},
        fallbacks=[]
    ))
    
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get_phone_numbers', get_phone_numbers)],
        states={'get_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, get_phone_numbers)]},
        fallbacks=[]
    ))
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("find_email", find_emailCommand))
    dp.add_handler(CommandHandler("find_phone_number", find_phone_numberCommand))
    dp.add_handler(CommandHandler("verify_password", verify_passwordCommand))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_listCommand))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_email", get_email))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(CommandHandler("save_email", save_email))
		
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
