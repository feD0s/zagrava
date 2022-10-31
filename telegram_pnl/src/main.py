import configparser
import gc
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as mplt
import pandas as pd
import telegram
import yaml
from telegram import InlineKeyboardButton
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import pnl_bot_persistence as persistence
from analysis import get_maxDrawdown, get_sharpeRatio
from db_management import check_table, get_table
from exchange import get_candlesDf, get_exchange_client
from processing import get_pnlDf

# Set logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level='INFO')
log = logging.getLogger('')

# get strategy parameters
with open("strategy.yaml", "r") as strategy:
    try:
        strat = yaml.safe_load(strategy)
    except yaml.YAMLError as exc:
        print(exc)

# get config parameters
with open("config.yaml", "r") as config:
    try:
        cfg = yaml.safe_load(config)
    except yaml.YAMLError as exc:
        print(exc)


symbol = cfg['symbol']
windowSize = strat['windowSize']
# add windowSize to timeLimit to calculate ewma properly for given timeLimit
timeLimit = cfg['timeLimit'] + windowSize
timeframe = cfg['timeframe']
comissionRate = cfg['comissionRate']
tradingDaysCount = cfg['tradingDaysCount']
riskFreeRate = cfg['riskFreeRate']
exchangeName = cfg['exchangeName']

exchange = get_exchange_client(exchangeName, log)
interval = exchange.parse_timeframe(timeframe) * 1000

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
TELEGRAM_HANDLE = os.getenv('TELEGRAM_HANDLE')
TELEGRAM_DB_FILE = os.getenv('TELEGRAM_DB_FILE')
TELEGRAM_CURRENT_DIR = os.getenv('TELEGRAM_CURRENT_DIR')

bot_properties_file = 'pnl_bot.properties'

if os.path.isfile(bot_properties_file):
    logging.info(f"Using {bot_properties_file}")
    config = configparser.ConfigParser()
    config.read(bot_properties_file)
    enabled_cmd = config['cmds_config']['enabled_cmd']
    broadcast_unkown_messages = config['cmds_config']['broadcast_unkown_messages']
    buttons_rows_per_page = int(config['cmds_config']['buttons_rows_per_page'])
else:
    if len(sys.argv) < 3:
        print('Usage: python pnl_bot.py TOKEN handle')
        exit()
    # enabled_cmd = 'explore,help,ip,webip,logo,whoami,chatid,img,exec,execa,get,down,broadcast,print,sql,store,value,values,downcfg,startbot,stopbot'
    enabled_cmd = 'downcfg,startbot,stopbot'
    buttons_rows_per_page = 10
    logging.info(
        'All commands are enabled, to disable them use a bot.properties file')

current_dir = str(Path(TELEGRAM_CURRENT_DIR).absolute())
logging.info(f'Enabled commands {enabled_cmd}')
allowed = enabled_cmd.split(',')

exists = os.path.isfile(TELEGRAM_DB_FILE)
if not exists:
    logging.info('Will create db file')
    persistence.create_db(TELEGRAM_DB_FILE)
    logging.info('Created db file')
persistence.add_bot(TELEGRAM_DB_FILE, TELEGRAM_API_TOKEN, TELEGRAM_HANDLE)
logging.info("Admins: %s" % str(persistence.get_admin(TELEGRAM_DB_FILE)))
waiting_for_first_connection = len(
    persistence.get_admin(TELEGRAM_DB_FILE)) == 0
updater = Updater(TELEGRAM_API_TOKEN, use_context=True)


def is_allowed(user_id):
    return user_id in map(lambda x: x[0], persistence.get_admin(TELEGRAM_DB_FILE))


def is_not_allowed(user_id):
    return not is_allowed(user_id)


def start(update, context):
    logging.info("========================= START")
    user = update.message.from_user
    user_id = user.id
    message = update.message.text
    message_chat_id = update.message.chat_id
    full_name = user.full_name
    username = user.username
    global waiting_for_first_connection
    persistence.record_msg(TELEGRAM_DB_FILE, user_id,
                           message_chat_id, full_name, username, message)
    logging.info("waiting_for_first_connection (%s): '%s'" % (
        waiting_for_first_connection, persistence.get_admin(TELEGRAM_DB_FILE)))
    if waiting_for_first_connection:
        persistence.add_admin(TELEGRAM_DB_FILE, user_id,
                              message_chat_id, full_name, username)
        waiting_for_first_connection = False
        context.bot.send_message(
            message_chat_id, text="You are now admin\nUse /help to see what you can do")
        logging.info("Added new admin (%s): '%s'" % (user_id, message))
        return

    if is_not_allowed(user_id):
        logging.info("Refused (%s): '%s'" % (user_id, message))
        logging.info("Admins: %s" %
                     str(persistence.get_admin(TELEGRAM_DB_FILE)))
        return

    persistence.update_admin_info(
        TELEGRAM_DB_FILE, user_id, message_chat_id, full_name, username)
    logging.info(f'Updated admin user_id: {user_id}, message_chat_id: {message_chat_id}, '
                 f'full_name: {full_name}, username: {username}')
    context.bot.send_message(
        message_chat_id, text="You are now admin\nUse /help to see what you can do")
    keyboard = []
    keyboard.append([InlineKeyboardButton(
        "Start the bot", callback_data="bot_start")])


def help_bot(update, context):
    '''print readme in telegram'''
    user = update.message.from_user
    user_id = user.id
    message_chat_id = update.message.chat_id
    logging.info("HELP (%s)" % (user_id,))
    with open('./pnl_bot_README.md', 'r') as file:
        context.bot.send_message(chat_id=message_chat_id, text=file.read(
        ), parse_mode=telegram.ParseMode.MARKDOWN)


def list_admins(update, context):
    '''list admins in telegram'''
    admin_list = []
    for admin_info in map(lambda x: f'user_id: {x[0]}, full_name: {x[1]}, username: {x[2]}',
                          persistence.get_admins(TELEGRAM_DB_FILE)):
        admin_list.append(str(admin_info))
    context.bot.send_message(update.message.chat_id,
                             text='\n'.join(admin_list))


def delete_admin(update, context):
    '''delete admin from pnl bot'''
    if len(persistence.get_admins(TELEGRAM_DB_FILE)) == 1:
        context.bot.send_message(update.message.chat_id, text="Can't delete the only admin, "
                                                              "please add another admin and then delete this.")
        return
    persistence.delete_admin(TELEGRAM_DB_FILE, context.args[0])
    context.bot.send_message(update.message.chat_id,
                             text=f'Deleted admin id {context.args[0]}')


def on_contact(update, context):
    user = update.message.from_user
    user_id = user.id
    contact_id = update.message.contact.user_id
    contact_name = update.message.contact.first_name
    message_chat_id = update.message.chat_id
    if is_not_allowed(user_id):
        logging.info("Refused contact: '%s'" % user_id)
        return
    logging.info("Received Contact (%s): '%s'" % (user_id, contact_id))
    persistence.add_admin(TELEGRAM_DB_FILE, contact_id, 0, "", "")
    context.bot.send_message(message_chat_id, text=(
        "Now %s is admin" % contact_name))
    logging.info("Admins: %s" % str(persistence.get_admin(TELEGRAM_DB_FILE)))


def backtest(update, context):
    message_chat_id = update.message.chat_id
    strategyName = context.args[0]
    tableName = 'strategy'
    if check_table(tableName, log):
        strategyDf = get_table(tableName, log)
        strat = strategyDf[strategyDf['name'] == strategyName]
        if strat.empty:
            context.bot.send_message(
                message_chat_id, text="Strategy not found")
        else:
            candlesDf = get_candlesDf(exchange, cfg, windowSize, interval)
            pnlDf = get_pnlDf(strat, comissionRate, candlesDf)
            annualizedSharpeRatio = get_sharpeRatio(
                pnlDf, tradingDaysCount, riskFreeRate)
            maxDrawdown = get_maxDrawdown(pnlDf)

            pnlDf['updatetime'] = pd.to_datetime(
                pnlDf['updatetime'], unit='ms')
            pnlDf = pnlDf.set_index('updatetime')

            fig, ax = mplt.subplots()
            fig.set_size_inches(16, 9, forward=True)
            ax.set_title(str(symbol) + ' PnL')
            ax.plot(pnlDf.pnlFinal, color='cornflowerblue')
            ax.set_ylabel('PnL')
            ax.set_title(symbol+" PnL")
            # добавляем текст справа сверху
            box_text = ''
            box_text += 'Sharpe Ratio: ' + \
                str(round(annualizedSharpeRatio, 2)) + '\n'
            box_text += 'Maximum Drawdown: ' + str(round(maxDrawdown)) + ' %'
            ax.text(0.8, 0.95, box_text, transform=ax.transAxes, fontsize=10,
                    verticalalignment='top')
            # saving image
            path = symbol.replace("/", "") + "_pnl.jpg"
            mplt.savefig(path, bbox_inches='tight')
            context.bot.send_photo(
                chat_id=update.message.chat_id, photo=open(path, 'rb'))
            # garbage collection
            del candlesDf
            del pnlDf
            gc.collect()
    else:
        text = f'strategy table was not found'
        context.bot.send_message(message_chat_id, text=text)


dispatcher = updater.dispatcher

cmds = [
    ('lsadmins', 'List all admins.\n    /lsadmins', list_admins),
    ('rmadmin', 'Deletes an admin.\n    /rmadmin <id>', delete_admin),
    ('backtest', 'Backtests strategy with <strategy name>.\n    /backtest <strategy>', backtest),
    ('help', 'Displays README.\n    /help', help_bot),
]


def closure(closure_alias, closure_callback):
    def run_cmd_if_allowed(update, context):
        if is_not_allowed(update.message.from_user.id):
            logging.info("Refused %s: '%s'" %
                         (closure_alias, update.message.from_user.id))
            return
        logging.info("Received command '%s' '%s'" %
                     (closure_alias, ' '.join(context.args)))
        closure_callback(update, context)
    return run_cmd_if_allowed


def command_not_enabled(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="This command is not enabled, "
                                                                  "change pnl_bot.properties to enable it")


for cmd in cmds:
    alias = cmd[0]
    if alias in allowed:
        callback = cmd[2]
        dispatcher.add_handler(CommandHandler(
            command=alias, callback=closure(alias, callback), pass_args=True))
    else:
        dispatcher.add_handler(CommandHandler(
            command=alias, callback=closure(alias, command_not_enabled)))

all_commands = ""

for cmd in cmds:
    all_commands = all_commands + ("%s - %s\n" % (cmd[0], cmd[1]))


def error_callback(update, context):
    error_description = f'Update:\n"{update}"\n caused error:\n"{context.error}"'
    logging.error(error_description)
    if is_allowed(update.message.from_user.id):
        context.bot.send_message(
            chat_id=update.message.chat_id, text=error_description)


def commands(update, context):
    if is_not_allowed(update.message.from_user.id):
        logging.info("Refused commands: '%s'" % (update.message.from_user.id,))
        return
    context.bot.send_message(chat_id=update.message.chat_id, text=all_commands)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('cmds', commands))
dispatcher.add_handler(MessageHandler(Filters.contact, on_contact))
dispatcher.add_error_handler(error_callback)

logging.info("Admins: %s" % str(persistence.get_admin(TELEGRAM_DB_FILE)))

logging.info("Starting bot")
updater.start_polling()

updater_bot = updater.bot


for chat in map(lambda x: x[0], persistence.get_admin_chat_ids(TELEGRAM_DB_FILE)):
    if chat != 0:
        updater_bot.send_message(
            chat, text=f'Bot {TELEGRAM_HANDLE} started {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}')
