import os
import edge_tts

from langdetect import detect, LangDetectException

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


# =====================================================
# BOT TOKEN
# =====================================================

TOKEN = os.environ["8966768712:AAGPEtTSXQJqjcfflWaI6GjtiwfmjuY6uAo"]


# =====================================================
# LANGUAGE -> EDGE TTS VOICE
# =====================================================

LANGUAGE_VOICES = {

    "hi": "hi-IN-SwaraNeural",       # Hindi
    "en": "en-US-AriaNeural",        # English
    "pa": "hi-IN-MadhurNeural",      # Punjabi fallback
    "mr": "hi-IN-SwaraNeural",       # Marathi fallback
    "bn": "bn-IN-TanishaaNeural",    # Bengali
    "ta": "ta-IN-PallaviNeural",    # Tamil
    "te": "te-IN-ShrutiNeural",      # Telugu
    "gu": "gu-IN-DhwaniNeural",      # Gujarati
    "kn": "kn-IN-SapnaNeural",       # Kannada
    "ml": "ml-IN-SobhanaNeural",     # Malayalam
    "ur": "ur-PK-UzmaNeural",        # Urdu
    "fr": "fr-FR-DeniseNeural",      # French
    "de": "de-DE-KatjaNeural",       # German
    "es": "es-ES-ElviraNeural",      # Spanish
    "it": "it-IT-ElsaNeural",        # Italian
    "pt": "pt-BR-FranciscaNeural",  # Portuguese
    "ru": "ru-RU-SvetlanaNeural",    # Russian
    "ja": "ja-JP-NanamiNeural",      # Japanese
    "ko": "ko-KR-SunHiNeural",       # Korean
    "zh-cn": "zh-CN-XiaoxiaoNeural", # Chinese
}


# =====================================================
# DEFAULT SETTINGS
# =====================================================

DEFAULT_SETTINGS = {

    "speed": 0,
    "pitch": 0,
    "volume": 0

}


# =====================================================
# START
# =====================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        "👋 Welcome!\n\n"

        "🌍 Main automatically language detect karta hoon.\n\n"

        "Hindi text → Hindi voice 🇮🇳\n"
        "English text → English voice 🇺🇸\n"
        "Punjabi text → Punjabi voice 🇮🇳\n"
        "Marathi text → Marathi voice 🇮🇳\n\n"

        "⚙️ Voice settings ke liye:\n"
        "/settings\n\n"

        "📝 Ab mujhe koi bhi text bhejo."

    )


# =====================================================
# SETTINGS
# =====================================================

async def settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if "speed" not in context.user_data:

        context.user_data.update(
            DEFAULT_SETTINGS
        )


    speed = context.user_data["speed"]
    pitch = context.user_data["pitch"]
    volume = context.user_data["volume"]


    keyboard = [

        [
            InlineKeyboardButton(
                "🎚️ SPEED",
                callback_data="none"
            )
        ],

        [

            InlineKeyboardButton(
                "➖",
                callback_data="speed_down"
            ),

            InlineKeyboardButton(
                f"{speed:+d}%",
                callback_data="none"
            ),

            InlineKeyboardButton(
                "➕",
                callback_data="speed_up"
            )

        ],

        [
            InlineKeyboardButton(
                "🎛️ PITCH",
                callback_data="none"
            )
        ],

        [

            InlineKeyboardButton(
                "➖",
                callback_data="pitch_down"
            ),

            InlineKeyboardButton(
                f"{pitch:+d}Hz",
                callback_data="none"
            ),

            InlineKeyboardButton(
                "➕",
                callback_data="pitch_up"
            )

        ],

        [
            InlineKeyboardButton(
                "🔊 VOLUME",
                callback_data="none"
            )
        ],

        [

            InlineKeyboardButton(
                "➖",
                callback_data="volume_down"
            ),

            InlineKeyboardButton(
                f"{volume:+d}%",
                callback_data="none"
            ),

            InlineKeyboardButton(
                "➕",
                callback_data="volume_up"
            )

        ],

        [

            InlineKeyboardButton(
                "🔄 RESET",
                callback_data="reset"
            ),

            InlineKeyboardButton(
                "✅ APPLY",
                callback_data="apply"
            )

        ]

    ]


    await update.message.reply_text(

        "🎙️ VOICE SETTINGS\n\n"

        f"🎚️ Speed: {speed:+d}%\n"
        f"🎛️ Pitch: {pitch:+d}Hz\n"
        f"🔊 Volume: {volume:+d}%\n\n"

        "⬅️ ➡️ Buttons se adjust karo.",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )


# =====================================================
# UPDATE SETTINGS MESSAGE
# =====================================================

async def update_settings_message(
    query
):

    user_data = query.message.chat


# =====================================================
# BUTTON HANDLER
# =====================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if "speed" not in context.user_data:

        context.user_data.update(
            DEFAULT_SETTINGS
        )


    data = query.data


    # ==========================================
    # SPEED
    # ==========================================

    if data == "speed_up":

        context.user_data["speed"] += 5

        if context.user_data["speed"] > 100:

            context.user_data["speed"] = 100


    elif data == "speed_down":

        context.user_data["speed"] -= 5

        if context.user_data["speed"] < -100:

            context.user_data["speed"] = -100


    # ==========================================
    # PITCH
    # ==========================================

    elif data == "pitch_up":

        context.user_data["pitch"] += 5

        if context.user_data["pitch"] > 50:

            context.user_data["pitch"] = 50


    elif data == "pitch_down":

        context.user_data["pitch"] -= 5

        if context.user_data["pitch"] < -50:

            context.user_data["pitch"] = -50


    # ==========================================
    # VOLUME
    # ==========================================

    elif data == "volume_up":

        context.user_data["volume"] += 5

        if context.user_data["volume"] > 100:

            context.user_data["volume"] = 100


    elif data == "volume_down":

        context.user_data["volume"] -= 5

        if context.user_data["volume"] < -100:

            context.user_data["volume"] = -100


    # ==========================================
    # RESET
    # ==========================================

    elif data == "reset":

        context.user_data.update(
            DEFAULT_SETTINGS
        )


    # ==========================================
    # APPLY
    # ==========================================

    elif data == "apply":

        await query.edit_message_text(

            "✅ Settings Saved!\n\n"

            f"🎚️ Speed: "
            f"{context.user_data['speed']:+d}%\n"

            f"🎛️ Pitch: "
            f"{context.user_data['pitch']:+d}Hz\n"

            f"🔊 Volume: "
            f"{context.user_data['volume']:+d}%\n\n"

            "Ab text bhejo 🎙️"

        )

        return


    # ==========================================
    # REFRESH MENU
    # ==========================================

    speed = context.user_data["speed"]

    pitch = context.user_data["pitch"]

    volume = context.user_data["volume"]


    keyboard = [

        [
            InlineKeyboardButton(
                "🎚️ SPEED",
                callback_data="none"
            )
        ],

        [

            InlineKeyboardButton(
                "➖",
                callback_data="speed_down"
            ),

            InlineKeyboardButton(
                f"{speed:+d}%",
                callback_data="none"
            ),

            InlineKeyboardButton(
                "➕",
                callback_data="speed_up"
            )

        ],

        [
            InlineKeyboardButton(
                "🎛️ PITCH",
                callback_data="none"
            )
        ],

        [

            InlineKeyboardButton(
                "➖",
                callback_data="pitch_down"
            ),

            InlineKeyboardButton(
                f"{pitch:+d}Hz",
                callback_data="none"
            ),

            InlineKeyboardButton(
                "➕",
                callback_data="pitch_up"
            )

        ],

        [
            InlineKeyboardButton(
                "🔊 VOLUME",
                callback_data="none"
            )
        ],

        [

            InlineKeyboardButton(
                "➖",
                callback_data="volume_down"
            ),

            InlineKeyboardButton(
                f"{volume:+d}%",
                callback_data="none"
            ),

            InlineKeyboardButton(
                "➕",
                callback_data="volume_up"
            )

        ],

        [

            InlineKeyboardButton(
                "🔄 RESET",
                callback_data="reset"
            ),

            InlineKeyboardButton(
                "✅ APPLY",
                callback_data="apply"
            )

        ]

    ]


    await query.edit_message_text(

        "🎙️ VOICE SETTINGS\n\n"

        f"🎚️ Speed: {speed:+d}%\n"
        f"🎛️ Pitch: {pitch:+d}Hz\n"
        f"🔊 Volume: {volume:+d}%\n\n"

        "⬅️ ➡️ Buttons se adjust karo.",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )


# =====================================================
# TEXT TO VOICE
# =====================================================

async def text_to_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text


    # ==========================================
    # DETECT LANGUAGE
    # ==========================================

    try:

        language = detect(text)

    except LangDetectException:

        language = "en"


    # ==========================================
    # FIND VOICE
    # ==========================================

    voice = LANGUAGE_VOICES.get(

        language,

        "en-US-AriaNeural"

    )


    # ==========================================
    # SETTINGS
    # ==========================================

    speed = context.user_data.get(
        "speed",
        0
    )

    pitch = context.user_data.get(
        "pitch",
        0
    )

    volume = context.user_data.get(
        "volume",
        0
    )


    await update.message.reply_text(

        f"🌍 Language: {language}\n"
        f"🎙️ Voice generating...\n\n"

        f"🎚️ Speed: {speed:+d}%\n"
        f"🎛️ Pitch: {pitch:+d}Hz\n"
        f"🔊 Volume: {volume:+d}%"

    )


    user_id = update.effective_user.id


    output_file = (

        "voice_"

        + str(user_id)

        + ".mp3"

    )


    try:

        communicate = edge_tts.Communicate(

            text=text,

            voice=voice,

            rate=f"{speed:+d}%",

            pitch=f"{pitch:+d}Hz",

            volume=f"{volume:+d}%"

        )


        await communicate.save(

            output_file

        )


        with open(

            output_file,

            "rb"

        ) as audio:

            await update.message.reply_voice(

                voice=audio

            )


        if os.path.exists(

            output_file

        ):

            os.remove(

                output_file

            )


    except Exception as e:

        await update.message.reply_text(

            "❌ Voice Error:\n\n"

            + str(e)

        )


# =====================================================
# BOT
# =====================================================

app = ApplicationBuilder().token(

    TOKEN

).build()


app.add_handler(

    CommandHandler(

        "start",

        start

    )

)


app.add_handler(

    CommandHandler(

        "settings",

        settings

    )

)


app.add_handler(

    CallbackQueryHandler(

        button_handler

    )

)


app.add_handler(

    MessageHandler(

        filters.TEXT
        & ~filters.COMMAND,

        text_to_voice

    )

)


print(

    "🤖 Auto Language Text To Voice Bot Started!"

)


app.run_polling()
