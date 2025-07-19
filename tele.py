from config import bot
import requests

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! Welcome to the DEW IT Bot. I am able to translate from Arubesh to English for you, What can I translate for you today? Upload as compress only")


from utils import arubesh_inference

# handling an image uploaded
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    # retrieving the user's chat id
    chat_id = message.chat.id

    # retrive the file_path from telegram
    file_id = message.photo[-1].file_id
    file_path = bot.get_file(file_id).file_path

    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

    # Download the image content
    response = requests.get(file_url)
    image_bytes = response.content

    # Saving the image locally
    with open("received_photo.jpg", "wb") as f:
        f.write(image_bytes)

    # processing the image
    translated_text = arubesh_inference("received_photo.jpg")
    
    # sending a message called DEW IT
    bot.reply_to(message, "DEWWW IT!")

    # sending an image to the user
    with open("result.jpg", "rb") as img:
        bot.send_photo(chat_id, img, caption=translated_text)

bot.infinity_polling()