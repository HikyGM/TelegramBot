from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
import csv
import logging
import sqlalchemy.ext.declarative as dec
from database import db_session
from database.users import User
from database.like_user import Like
import os

SqlAlchemyBase = dec.declarative_base()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
NAME, PHOTO, GENDER, AGE, SITY, INFO, CHECK = range(7)
LIKE, DISLIKE, SLEEP = range(3)
VIEW_PROF, MY_PROF, DEL_PROF = range(3)
TOKEN = '5176643091:AAEOUBusMJPyclk5sGeOsOEOSB87vh_EieU'



def add_csv(update, context, element):
    user = update.message.from_user
    with open(f'files/{user.id}.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow((element,))


def start(update, context):
    text = "Привет!\n" \
           "Я бот для поиска собеседника\n" \
           "Давай знакомиться! 😉\n" \
           "Как тебя зовут?"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return NAME


def name(update, context):
    reply_keyboard = [['Муж', 'Жен']]
    user = update.message.from_user
    name_input = update.message.text
    with open(f'files/{user.id}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow((user.id,))
        writer.writerow((user.name,))
        writer.writerow((name_input,))
    logger.info("Имя пользователя %s: %s", user.first_name, name_input)
    update.message.reply_text(
        'Теперь определимся с полом',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Какой твой пол?'))
    return GENDER


def gender(update, context):
    user = update.message.from_user
    gender_input = update.message.text
    add_csv(update, context, gender_input)
    logger.info("Пол пользователя %s: %s", user.first_name, gender_input)
    update.message.reply_text('Отправь своё фото', reply_markup=ReplyKeyboardRemove())
    return PHOTO


def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_name = f'{user.id}.jpg'
    photo_file.download(f'photo_users/{photo_name}')
    add_csv(update, context, photo_name)
    logger.info("Фото пользователя %s: %s", user.first_name, photo_name)
    update.message.reply_text('Сколько тебе лет?')
    return AGE


def age(update, context):
    user = update.message.from_user
    age_check = update.message.text
    if not age_check.isdigit():
        update.message.reply_text('Некорректный возраст')
        return AGE
    add_csv(update, context, age_check)
    logger.info("Возраст пользователя %s: %s", user.first_name, age_check)
    update.message.reply_text('Из какого ты города?')
    return SITY


def sity(update, context):
    user = update.message.from_user
    sity_input = update.message.text
    add_csv(update, context, sity_input)
    logger.info("Пол пользователя %s: %s", user.first_name, sity_input)
    update.message.reply_text('Добавь немного информации о себе', reply_markup=ReplyKeyboardRemove())
    return INFO


def info(update, context):
    reply_keyboard = [['Да', 'Заполнить заново']]
    user = update.message.from_user
    info_input = update.message.text
    add_csv(update, context, info_input)
    logger.info("Город пользователя %s: %s", user.first_name, info_input)
    with open(f'files/{user.id}.csv', 'r') as f:
        data = list(csv.reader(f))
    text = f'Имя: {data[2][0]}\n' \
           f'Пол: {data[3][0]}\n' \
           f'Возраст: {data[5][0]}\n' \
           f'Город: {data[6][0]}\n' \
           f'О себе: {data[7][0]}'
    context.bot.send_photo(chat_id=user.id, photo=open(f'photo_users/{data[4][0]}', 'rb'), caption=text)
    update.message.reply_text(
        'Всё верно?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Всё верно?'
        ),
    )
    return CHECK


def check_info(update, context):
    user = update.message.from_user
    ask = update.message.text
    if ask == 'Да':
        update.message.reply_text(
            'Приятно познакомиться!\n'
            'Удачи в поисках собеседника!😀',
            reply_markup=ReplyKeyboardRemove()
        )
        add_db_user(user.id)
        view_list_profiles(update, context)
        return ConversationHandler.END
    elif ask == 'Заполнить заново':
        update.message.reply_text(
            'Как тебя зовут?',
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME


def stop():
    pass


def add_db_user(id_user):
    with open(f'files/{id_user}.csv', 'r') as f:
        data = list(csv.reader(f))
    db_sess = db_session.create_session()
    user = User()
    if db_sess.query(User).filter(User.id_user_tg == data[0][0]).first():
        user = db_sess.query(User).filter(User.id_user_tg == data[0][0]).first()
    user.id_user_tg = data[0][0]
    user.name_user_tg = data[1][0]
    user.name_user = data[2][0]
    user.gender_user = data[3][0]
    user.photo_user = data[4][0]
    user.age_user = data[5][0]
    user.sity_user = data[6][0]
    user.info_user = data[7][0]
    db_sess.add(user)
    db_sess.commit()
    os.remove(f'files/{data[0][0]}.csv')
    generate_list_profiles(id_user)


def generate_list_profiles(id_user):
    db_sess = db_session.create_session()
    users = list(set([elem[0] for elem in db_sess.query(User.id_user_tg).filter(User.id_user_tg != id_user).all()]))
    with open(f'files/user_lists/list_{id_user}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(users)


def view_list_profiles(update, context):
    reply_keyboard = [['👍', '👎', '💤']]
    user = update.message.from_user
    answer = update.message.text
    if answer == '👍' or answer == '👎' or answer == '1' or answer == '2' or answer == 'Да':
        with open(f'files/user_lists/list_{user.id}.csv', 'r') as f:
            data = list(csv.reader(f))
        if answer == '👍' or answer == '1':
            db_sess = db_session.create_session()
            like = Like()
            if not db_sess.query(Like).filter(Like.user_tg == user.id and Like.like_user_tg == data[1][0]).first():
                like.user_tg = user.id
                like.like_user_tg = data[1][0]
                db_sess.add(like)
                db_sess.commit()
            db_sess = db_session.create_session()
            check_like = db_sess.query(Like).filter(Like.user_tg == data[1][0] and Like.like_user_tg == user.id).first()
            if check_like:
                profile = db_sess.query(User).filter(User.id_user_tg == data[1][0]).first()
                text = f'Поздравляю! У вас есть взаимный лайк с {profile.name_user_tg}'
                context.bot.send_photo(chat_id=user.id,
                                       photo=open(f'photo_users/{profile.photo_user}', 'rb'),
                                       caption=text,
                                       reply_markup=ReplyKeyboardMarkup(
                                           reply_keyboard,
                                           one_time_keyboard=True,
                                           resize_keyboard=True,
                                       ), )

                profile = db_sess.query(User).filter(User.id_user_tg == user.id).first()
                text = f'Поздравляю! У вас есть взаимный лайк с {profile.name_user_tg}'
                context.bot.send_photo(chat_id=data[1][0],
                                       photo=open(f'photo_users/{profile.photo_user}', 'rb'),
                                       caption=text,
                                       reply_markup=ReplyKeyboardMarkup(
                                           reply_keyboard,
                                           one_time_keyboard=True,
                                           resize_keyboard=True,
                                       ), )
                db_sess.delete(check_like)
                db_sess.commit()
                check_like = db_sess.query(Like).filter(
                    Like.user_tg == user.id and Like.like_user_tg == data[1][0]).first()
                db_sess.delete(check_like)
                db_sess.commit()
        try:
            list_profiles = list(map(lambda x: int(x), ' '.join(data[0]).split(';')))
            id_user = list_profiles.pop()
            with open(f'files/user_lists/list_{user.id}.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(list_profiles)
            with open(f'files/user_lists/list_{user.id}.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                writer.writerow((str(id_user),))
            db_sess = db_session.create_session()
            profile = db_sess.query(User).filter(User.id_user_tg == id_user).first()
            text = f'{profile.name_user}\n' \
                   f'{profile.gender_user}\n' \
                   f'{profile.age_user}\n' \
                   f'{profile.sity_user}\n' \
                   f'{profile.info_user}'
            context.bot.send_photo(chat_id=user.id,
                                   photo=open(f'photo_users/{profile.photo_user}', 'rb'),
                                   caption=text,
                                   reply_markup=ReplyKeyboardMarkup(
                                       reply_keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True,
                                   ), )
        except ValueError:
            update.message.reply_text(
                'Похоже что анкеты закончились\n'
                'Попробуй позже!',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard,
                    one_time_keyboard=True,
                    resize_keyboard=True, ), )
    elif answer == '💤' or answer == '3':
        update.message.reply_text('Возвращайся, я тебя жду!)')
    else:
        update.message.reply_text(
            'Нет такого варианта ответа',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True, ), )


def main():
    db_session.global_init("database/db.db")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    db_sess = db_session.create_session()
    for user in db_sess.query(User).all():
        generate_list_profiles(user.id_user_tg)
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text, name)],
            GENDER: [MessageHandler(Filters.regex('^(Муж|Жен)$'), gender)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            AGE: [MessageHandler(Filters.text, age)],
            SITY: [MessageHandler(Filters.text, sity)],
            INFO: [MessageHandler(Filters.text, info)],
            CHECK: [MessageHandler(Filters.text, check_info)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    view_profiles_handler = MessageHandler(Filters.text, view_list_profiles)
    dp.add_handler(start_handler)
    dp.add_handler(view_profiles_handler)
    updater.start_polling()
    updater.idle()


main()
