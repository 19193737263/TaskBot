from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
import logging

user_tasks = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    if update.message:
        keyboard = [
            [InlineKeyboardButton("📅 Voir mes tâches d'aujourd'hui", callback_data="today_task")],        
            [InlineKeyboardButton("➕ Créer une nouvelle tâche", callback_data="add_task")],
            [InlineKeyboardButton("➖ Modifier/Supprimer une tâche", callback_data="adjust_task")],
            [InlineKeyboardButton("✅ Marquer une tâche comme terminée", callback_data="complete_task")],
            [InlineKeyboardButton("⏳ Mise à jour", callback_data="update")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("""🤖 <b>TASK BOT</b>\n\n
Bienvenue sur <b>TaskBot</b> 🚀\n
Ton assistant personnel pour gérer toutes tes <b>tâches</b> 📝 ! 
Organise ta journée, crée des rappels et reste productif en un clin d’œil 🔥. 
Plus de stress, que de l’action 💪. 
Prêt à attaquer ta <b>to-do list</b> ? 👊""", reply_markup=reply_markup, parse_mode='HTML')

async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'today_task':
        tasks = user_tasks.get(query.from_user.id, [])
        if tasks:
            tasks_text = "\n".join([f"{i+1}. {task['title']} {'✅' if task['completed'] else '🕐'}" for i, task in enumerate(tasks)])
        else:
            tasks_text = "Tu n'as pas encore de tâches."
        await query.edit_message_text(f"Voici tes tâches d'aujourd'hui :\n{tasks_text}")
    
    elif query.data == 'add_task':
        await query.edit_message_text("📝 Envoie le titre de ta tâche à ajouter !")

    elif query.data == 'adjust_task':
        tasks = user_tasks.get(query.from_user.id, [])
        if tasks:
            keyboard = [[InlineKeyboardButton(f"✏️ Modifier/Supprimer : {task['title']}", callback_data=f"modify_{i}")]
                        for i, task in enumerate(tasks)]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Choisis une tâche à modifier ou supprimer :", reply_markup=reply_markup)
        else:
            await query.edit_message_text("Tu n'as pas encore de tâches à modifier ou supprimer.")
    
    elif query.data == 'complete_task':
        tasks = user_tasks.get(query.from_user.id, [])
        if tasks:
            keyboard = [[InlineKeyboardButton(f"✅ Marquer comme terminée : {task['title']}", callback_data=f"complete_{i}")]
                        for i, task in enumerate(tasks)]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Choisis une tâche à marquer comme terminée :", reply_markup=reply_markup)
        else:
            await query.edit_message_text("Tu n'as pas encore de tâches à compléter.")
    
    elif query.data == 'update':
        await query.edit_message_text("🛠️ Mise à jour en cours... (Cette fonctionnalité est à venir!)")

async def add_task(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    title = update.message.text
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    user_tasks[user_id].append({"title": title, "description": "", "completed": False})
    await update.message.reply_text(f"🎉 Tâche ajoutée : {title}\nEnvoie une description pour cette tâche ou tape /skip pour ignorer.")

async def receive_description(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_tasks and len(user_tasks[user_id]) > 0:
        last_task = user_tasks[user_id][-1]
        if update.message.text.lower() != "/skip":
            last_task['description'] = update.message.text
            await update.message.reply_text(f"✅ Description ajoutée à la tâche : {last_task['title']}")
        else:
            await update.message.reply_text(f"Tâche {last_task['title']} sans description.")
    else:
        await update.message.reply_text("Tu n'as pas de tâche en cours d'ajout.")

async def modify_task(update: Update, context: CallbackContext):
    query = update.callback_query
    task_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    tasks = user_tasks.get(user_id, [])
    if task_id < len(tasks):
        task = tasks[task_id]
        await query.edit_message_text(f"✏️ Tu veux modifier la tâche : {task['title']} ? Envoie un nouveau titre ou une nouvelle description.")

async def delete_task(update: Update, context: CallbackContext):
    query = update.callback_query
    task_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    tasks = user_tasks.get(user_id, [])
    if task_id < len(tasks):
        del tasks[task_id]
        await query.edit_message_text("❌ Tâche supprimée avec succès.")
    else:
        await query.edit_message_text("🚫 Tâche non trouvée.")

async def complete_task(update: Update, context: CallbackContext):
    query = update.callback_query
    task_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    tasks = user_tasks.get(user_id, [])
    if task_id < len(tasks):
        tasks[task_id]['completed'] = True
        await query.edit_message_text(f"🎉 La tâche : {tasks[task_id]['title']} a été marquée comme terminée ! ✅")
    else:
        await query.edit_message_text("🚫 Tâche non trouvée.")

def main():
    app = Application.builder().token("8127156585:AAEwQeD0oHAQw6Cpcm0itODfYn48SfaiLYI").build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_task))
    app.add_handler(CallbackQueryHandler(modify_task, pattern="^modify_"))
    app.add_handler(CallbackQueryHandler(delete_task, pattern="^delete_"))
    app.add_handler(CallbackQueryHandler(complete_task, pattern="^complete_"))
    
    app.run_polling(poll_interval=5)

if __name__ == '__main__':
    main()
