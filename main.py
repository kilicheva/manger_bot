from telegram import ReplyKeyboardMarkup, Bot, Update, Message, Document
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, Filters
from credits import bot_token


GENDER = 0
PHOTO = 1
BIO = 2
VIDEO = 3

bot = Bot(token=bot_token)
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext):
    reply_keyboard = [['Мужчина', 'Женщина']]
    update.message.reply_text(
        'Добрый день! Вас приветствует Крупная Компания! Расскажите о себе, вы мужчина или женщина?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return GENDER


def gender(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Отлично! Теперь отправьте нам свою фотографию, мы заведем личную карточку, или отправьте /skip если хотите пропустить этот шаг')
    return PHOTO


def photo(update: Update, context: CallbackContext):
    user = update.message.from_user
    photo_file = update.message.document.get_file()
    photo_file.download('user_photo.jpg')
    update.message.reply_text(
        'Отлично! Вы сегодня прекрасно выглядите! Теперь отправьте краткое сообщение о себе, или отправьте /skip если хотите пропустить этот шаг')
    return BIO


def skip_photo(update: Update, context: CallbackContext):
    update.message.reply_text('Значит без фото! Окей, отправьте краткое сообщение о себе или отправьте /skip.')
    return BIO


def video(update: Update, context: CallbackContext):
    user = update.message.from_user
    video_file = update.message.document.get_file()
    video_file.download(f'{user}_video.mp4')
    update.message.reply_text('Отлично - мы свяжемся с вами!')
    return ConversationHandler.END


def skip_video(update: Update, context: CallbackContext):
    update.message.reply_text('Возможно, мы свяжемся с вами!')
    return ConversationHandler.END


def bio(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Отлично! Мы получили ваше резюме - теперь в следующем сообщении вы можете отправить видеорезюме или написать /skip, чтобы пропустить этот шаг')
    return VIDEO


def skip_bio(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Давайте продолжим без резюме! В следующем сообщении вы можете отправить видеорезюме или написать /skip, чтобы пропустить этот шаг ')
    return VIDEO


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Надеюсь вы еще нам напишите - возможно мы нуждаемся именно в вас!')
    return ConversationHandler.END


# Обработчик команды /start
start_handler = CommandHandler('start', start)
# Обработчик выбора пола
gender_handler = MessageHandler(Filters.regex('^(Мужчина|Женщина)$'), gender)
# Обработчик отправки фотографии
photo_handler = MessageHandler(Filters.document.category("image"), photo)
# Обработчик команды /skip для пропуска отправки фотографии
skip_photo_handler = MessageHandler(Filters.text & Filters.regex('^/skip$'), skip_photo)
# Обработчик команды /cancel для отмены диалога
cancel_handler = CommandHandler('cancel', cancel)
# Обработчик отправки краткого сообщения о себе
bio_handler = MessageHandler(Filters.text, bio)
# Обработчик команды /skip для пропуска отправки краткого сообщения о себе
skip_bio_handler = MessageHandler(Filters.text & Filters.regex('^/skip$'), skip_bio)
# Обработчик отправки видеорезюме
video_handler = MessageHandler(Filters.document.category("video"), video)
# Обработчик команды /skip для пропуска отправки видеорезюме
skip_video_handler = MessageHandler(Filters.text & Filters.regex('^/skip$'), skip_video)
# Обработчик диалога с состояниями
conv_handler = ConversationHandler(
    entry_points=[start_handler],
    states={
        GENDER: [gender_handler],
        PHOTO: [photo_handler, skip_photo_handler],
        BIO: [bio_handler, skip_bio_handler],
        VIDEO: [video_handler, skip_video_handler]
    },
    fallbacks=[cancel_handler])

# Добавление обработчика диалога в диспетчер
dispatcher.add_handler(conv_handler)

# Запуск бота
updater.start_polling()
updater.idle()
