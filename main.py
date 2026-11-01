import os
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
warnings = {}

async def is_admin(update, context):
    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)
    return member.status in ("administrator", "creator")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bienvenue sur le bot de modération !\n\n"
        "Commandes disponibles :\n"
        "/help - Aide\n"
        "/ban - Bannir\n"
        "/kick - Expulser\n"
        "/mute - Rendre muet\n"
        "/unmute - Rétablir la parole\n"
        "/warn - Avertir\n"
        "/purge - Nettoyer des messages"
    )


async def help_command(update, context):
    await start(update, context)


async def target_command(update, context):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Réservé aux administrateurs.")
        return None

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ Réponds au message du membre concerné."
        )
        return None

    return update.message.reply_to_message.from_user


async def ban(update, context):
    user = await target_command(update, context)
    if user:
        await update.effective_chat.ban_member(user.id)
        await update.message.reply_text("🔨 Membre banni.")


async def kick(update, context):
    user = await target_command(update, context)
    if user:
        await update.effective_chat.ban_member(user.id)
        await update.effective_chat.unban_member(user.id)
        await update.message.reply_text("👢 Membre expulsé.")


async def mute(update, context):
    user = await target_command(update, context)
    if user:
        await update.effective_chat.restrict_member(
            user.id,
            ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text("🔇 Membre rendu muet.")


async def unmute(update, context):
    user = await target_command(update, context)
    if user:
        await update.effective_chat.restrict_member(
            user.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text("🔊 Membre rétabli.")


async def warn(update, context):
    user = await target_command(update, context)
    if user:
        key = (update.effective_chat.id, user.id)
        warnings[key] = warnings.get(key, 0) + 1
        await update.message.reply_text(
            f"⚠️ Avertissement pour {user.first_name} "
            f"({warnings[key]}/3)."
        )


async def purge(update, context):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Réservé aux administrateurs.")
        return

    try:
        count = int(context.args[0])
        if not 1 <= count <= 100:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Utilisation : /purge 10")
        return

    chat = update.effective_chat
    start_id = update.message.message_id

    for message_id in range(start_id - count, start_id + 1):
        try:
            await chat.delete_message(message_id)
        except Exception:
            pass


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN manquant dans les variables Render")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("purge", purge))

    print("Bot de modération démarré !")
    app.run_polling()


if __name__ == "__main__":
    main()
