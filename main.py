import discord
from discord import app_commands
from discord.ext import commands
import json
import datetime

# إعدادات البوت الأساسية
TOKEN ='MTUwMjA1MDQyNzg4ODIwOTk1MA.GAejvY.lU6aBEHkr7AwUR-UzIm20W7OJO8aihWspdz-QY'

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

# --- نظام قاعدة البيانات البسيطة ---
def load_data():
    try:
        with open('bank.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open('bank.json', 'w') as f:
        json.dump(data, f, indent=4)

# حالة الجلسة (للتحقق من وجود رول نشط)
session_active = False

# --- الأزرار والنوافذ المنبثقة ---

# نافذة أسئلة الهوست
class HostModal(discord.ui.Modal, title='إضافة هوست'):
    ans1 = discord.ui.TextInput(label='وش اسم حسابك روب الأساسي؟', placeholder='اكتب اسم روبلوكس الأساسي هنا...')
    ans2 = discord.ui.TextInput(label='هل تعلم أن التشرد بدون تصريح يوصل لباند؟', placeholder='اكتب إجابتك هنا...')
    ans3 = discord.ui.TextInput(label='تجاوز سرعة الهوست بـ 50 كم = حرمان 5 أيام؟', placeholder='اكتب إجابتك هنا...')
    ans4 = discord.ui.TextInput(label='هل تعلم أن قطع الإشارة = حرمان 5 أيام؟', placeholder='اكتب إجابتك هنا...')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"تم إرسال طلب الهوست الخاص بك بنجاح، انتظر المراجعة.", ephemeral=True)

# زر إضافة هوست
class HostView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="اضافة الهوست 👑", style=discord.ButtonStyle.primary, custom_id="add_host_btn")
    async def add_host(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not session_active:
            await interaction.response.send_message("❌ لا يوجد رول نشط! يجب فتح رول أولاً.", ephemeral=True)
        else:
            await interaction.response.send_modal(HostModal())

# زر اعرف رصيدي
class BalanceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="اعرف رصيدي 💰", style=discord.ButtonStyle.secondary, custom_id="check_bal_btn")
    async def check_balance(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        user_id = str(interaction.user.id)
        bal = data.get(user_id, 0)
        await interaction.response.send_message(f"💰 رصيدك الحالي: **{bal:,} ريال**", ephemeral=True)

# --- الأوامر (Slash Commands) ---

# 1. أمر المخالفة
@bot.tree.command(name="مخالفه", description="تسجيل مخالفة مرورية لشخص")
@app_commands.choices(المخالفة=[
    app_commands.Choice(name="قطع إشارة حمراء (3k)", value="3000"),
    app_commands.Choice(name="استخدام مركبة ممنوعة (9k)", value="9000"),
    app_commands.Choice(name="مراوغة بين المركبات (8k)", value="8000"),
    app_commands.Choice(name="تجمهر (4k)", value="4000"),
    app_commands.Choice(name="الانزلاق بالمركبة (تفحيط) (10k)", value="10000"),
    # يمكنك إضافة بقية القائمة هنا بنفس الطريقة
])
async def violation(interaction: discord.Interaction, الشخص: discord.Member, المخالفة: app_commands.Choice[str]):
    price = int(المخالفة.value)
    data = load_data()
    user_id = str(الشخص.id)
    
    # خصم المبلغ
    data[user_id] = data.get(user_id, 0) - price
    save_data(data)

    today = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")
    
    embed_text = (
        f"🛑 إشعار رسمي من **الأمن العام**\n"
        f"> مرحباً {الشخص.mention}\n"
        f"> نود إبلاغك بأنه تم تسجيل **مخالفة** بحقك في النظام.\n\n"
        f"📄 **تفاصيل المخالفة:**\n"
        f"- **المخالفة:** {المخالفة.name}\n"
        f"- **الغرامة:** {price:,} ريال\n"
        f"- **الضابط المسؤول:** {interaction.user.mention}\n\n"
        f"`صادر عن: إدارة الأمن العام • التاريخ: {today}`"
    )
    await interaction.response.send_message(embed_text)

# 2. أمر زر اعرف رصيدي
@bot.tree.command(name="زر_اعرف_رصيدي", description="إرسال رسالة زر الرصيد")
async def send_bal_button(interaction: discord.Interaction):
    await interaction.response.send_message("💰 **رصيدك البنكي**\nاضغط الزر أدناه لتشوف رصيدك\n⏱️ يمكنك الضغط مرة كل 5 دقائق", view=BalanceView())

# 3. أمر زر اضافة هوست
@bot.tree.command(name="زر_اضافه_هوست", description="إرسال رسالة قوانين وزر الهوست")
async def send_host_button(interaction: discord.Interaction):
    rules = (
        "⚠️ **قوانين الهوست**\n\n"
        "• تخريب خفيف يوصل الى باند سيرفر 🚫\n"
        "• تسرع اكثر من 30 كيلو يوصل الى حرمان 5 ايام ⚡\n"
        "• تفحيط يوصل الى حرمان يومين | يوم 🚗\n\n"
        "ملاحظة: يمكن استخدام هذا الزر فقط عند وجود جلسة نشطة!\n"
        "اضغط الزر أدناه لإضافة نفسك كهوست"
    )
    await interaction.response.send_message(rules, view=HostView())

# 4. أمر رول (بدء الجلسة)
@bot.tree.command(name="رول", description="فتح أو إغلاق جلسة الرول")
async def toggle_role(interaction: discord.Interaction, الحالة: bool):
    global session_active
    session_active = الحالة
    status = "مفتوح ✅" if الحالة else "مغلق ❌"
    await interaction.response.send_message(f"تبون رول اضغط تحت إذا تبي تدخل\nالحالة الآن: **{status}**")

# 5. أمر إيداع (للمدراء فقط)
@bot.tree.command(name="ايداع", description="إضافة مبلغ لرصيد شخص (للمدراء)")
@app_commands.checks.has_permissions(administrator=True)
async def deposit(interaction: discord.Interaction, الشخص: discord.Member, المبلغ: int):
    data = load_data()
    user_id = str(الشخص.id)
    data[user_id] = data.get(user_id, 0) + المبلغ
    save_data(data)
    await interaction.response.send_message(f"✅ تم إيداع {المبلغ:,} ريال في حساب {الشخص.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

bot.run('MTUwMjA1MDQyNzg4ODIwOTk1MA.GAejvY.lU6aBEHkr7AwUR-UzIm20W7OJO8aihWspdz-QY')
