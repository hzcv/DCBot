import os
import random
import discord
from discord.ext import commands

# ==========================
# BOT CONFIG
# ==========================
BOT_TOKEN = "MTMyNTEwMDM4ODk0NDE4MzM3OQ.G6RDDr.EfQd92L8XbXVdMTUZ0yHQcBqX2gkxdPb9UvwmI"

# Your Discord User ID
ADMIN_ID = 1325100388944183379

# ==========================
# FILES
# ==========================
INSURANCE_FILE = "Insurance.txt"
MFI_FILE = "Mfi.txt"
USERS_FILE = "users.txt"
STATS_FILE = "stats.txt"

# ==========================
# CREATE FILES
# ==========================
for file_name in [
    INSURANCE_FILE,
    MFI_FILE,
    USERS_FILE,
    STATS_FILE
]:
    if not os.path.exists(file_name):
        open(file_name, "w").close()

# ==========================
# LOAD NUMBERS
# ==========================
def load_numbers(file_name):
    with open(file_name, "r") as file:
        return set(
            line.strip()
            for line in file
            if line.strip()
        )

insurance_numbers = load_numbers(INSURANCE_FILE)
mfi_numbers = load_numbers(MFI_FILE)

# ==========================
# SAVE USER
# ==========================
def save_user(user_id, username):

    users = set()

    with open(USERS_FILE, "r") as file:
        users = set(
            line.strip()
            for line in file
            if line.strip()
        )

    user_data = f"{user_id}|{username}"

    if user_data not in users:
        with open(USERS_FILE, "a") as file:
            file.write(user_data + "\n")

# ==========================
# UPDATE STATS
# ==========================
def update_stats(user_id, amount):

    stats = {}

    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            for line in file:
                if "|" in line:
                    uid, count = line.strip().split("|")
                    stats[uid] = int(count)

    uid = str(user_id)

    if uid not in stats:
        stats[uid] = 0

    stats[uid] += amount

    with open(STATS_FILE, "w") as file:
        for uid, count in stats.items():
            file.write(f"{uid}|{count}\n")

# ==========================
# TOTAL USERS
# ==========================
def get_total_users():

    with open(USERS_FILE, "r") as file:
        users = [
            line.strip()
            for line in file
            if line.strip()
        ]

    return len(users)

# ==========================
# TOTAL GENERATED
# ==========================
def get_total_generated():

    total = 0

    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            for line in file:
                if "|" in line:
                    total += int(
                        line.strip().split("|")[1]
                    )

    return total

# ==========================
# USER STATS
# ==========================
def get_user_stats():

    users = {}

    with open(USERS_FILE, "r") as file:
        for line in file:
            if "|" in line:
                uid, username = line.strip().split("|")
                users[uid] = username

    stats = {}

    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            for line in file:
                if "|" in line:
                    uid, count = line.strip().split("|")
                    stats[uid] = count

    result = ""

    for uid, username in users.items():
        count = stats.get(uid, "0")

        result += (
            f"User: {username}\n"
            f"ID: {uid}\n"
            f"Generated: {count}\n\n"
        )

    return result

# ==========================
# GENERATE UNIQUE
# ==========================
def generate_unique(prefix, digits, existing_set):

    while True:

        random_digits = ''.join(
            str(random.randint(0, 9))
            for _ in range(digits)
        )

        number = prefix + random_digits

        if number not in existing_set:
            existing_set.add(number)
            return number

# ==========================
# SAVE NUMBER
# ==========================
def save_number(file_name, number):

    with open(file_name, "a") as file:
        file.write(number + "\n")

# ==========================
# DISCORD BOT
# ==========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# Store pending requests
user_mode = {}

# ==========================
# READY
# ==========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ==========================
# START
# ==========================
@bot.command()
async def start(ctx):

    save_user(
        ctx.author.id,
        ctx.author.name
    )

    await ctx.send(
        "**Generator Menu**\n\n"
        "`!insurance` - Insurance Generator\n"
        "`!mfi` - MFI Generator"
    )

# ==========================
# INSURANCE
# ==========================
@bot.command()
async def insurance(ctx):

    user_mode[ctx.author.id] = "insurance"

    await ctx.send(
        "How many Insurance numbers do you want?"
    )

# ==========================
# MFI
# ==========================
@bot.command()
async def mfi(ctx):

    user_mode[ctx.author.id] = "mfi"

    await ctx.send(
        "How many MFI numbers do you want?"
    )

# ==========================
# MESSAGE LISTENER
# ==========================
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    uid = message.author.id

    if uid in user_mode:

        if message.content.isdigit():

            count = int(message.content)

            generated = []

            if user_mode[uid] == "insurance":

                for _ in range(count):

                    number = generate_unique(
                        "T00",
                        15,
                        insurance_numbers
                    )

                    save_number(
                        INSURANCE_FILE,
                        number
                    )

                    generated.append(number)

            elif user_mode[uid] == "mfi":

                for _ in range(count):

                    number = generate_unique(
                        "CA041",
                        8,
                        mfi_numbers
                    )

                    save_number(
                        MFI_FILE,
                        number
                    )

                    generated.append(number)

            update_stats(uid, count)

            await message.channel.send(
                "\n".join(generated)
            )

            del user_mode[uid]

        else:

            await message.channel.send(
                "Please enter a valid number."
            )

    await bot.process_commands(message)

# ==========================
# ADMIN
# ==========================
@bot.command()
async def admin(ctx):

    if ctx.author.id != ADMIN_ID:
        return

    total_users = get_total_users()
    total_generated = get_total_generated()

    msg = (
        f"TOTAL USERS: {total_users}\n\n"
        f"TOTAL GENERATED: {total_generated}\n\n"
        f"{get_user_stats()}"
    )

    await ctx.send(f"```{msg[:1900]}```")

# ==========================
# BROADCAST
# ==========================
@bot.command()
async def broadcast(ctx, *, text=None):

    if ctx.author.id != ADMIN_ID:
        return

    if not text:
        await ctx.send(
            "!broadcast Your Message"
        )
        return

    success = 0
    failed = 0

    with open(USERS_FILE, "r") as file:
        users = [
            line.strip()
            for line in file
            if line.strip()
        ]

    for user in users:

        try:

            user_id = int(
                user.split("|")[0]
            )

            member = await bot.fetch_user(
                user_id
            )

            await member.send(text)

            success += 1

        except:
            failed += 1

    await ctx.send(
        f"Broadcast Complete\n"
        f"Success: {success}\n"
        f"Failed: {failed}"
    )

# ==========================
# RUN
# ==========================
bot.run(BOT_TOKEN)
