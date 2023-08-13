import random
import time
import json
import discord


def get_current_time():
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return now

# TODO: Add a check for if the directory ./config presents. If not, then mkdir
def load_config_file(filename):
    config_file = open(f"./config/{filename}", 'r', encoding = 'utf-8')
    config_file.seek(0, 0)
    config = json.loads(config_file.read())
    config_file.close()
    return config


# Append a random string from a list of strings to target_string
# Parameter target_string can be omitted to randomly select one string from string_list
def append_random_string(string_list, target_string = ""):
    if string_list == []:
        return ""

    selection = random.randint(0, len(string_list) - 1)
    target_string += str(string_list[selection])
    return target_string


def ping(user, bot):
    if bot.latency <= 0.5:
        return user.mention + " 小毛龙飞到服务器再飞回来大概得花...嗯...**%.2lf ms**左右！只是大概！" % (bot.latency * 1000)
    else:
        return user.mention + " 小毛龙打了个哈欠—— 这个动作花了他整整**%.2lf ms**" % (bot.latency * 1000)


# Open a file and generate a discord.py file object to append to messages
def generate_discord_py_file_object(filepath = None):
    try:
        with open(filepath, 'rb') as targetFile:
            return discord.File(targetFile)
    except Exception:
        return None


def reaction(img_filename):
    if img_filename == "" or img_filename is None: raise FileNotFoundError

    if type(img_filename) == int:
        if img_filename < 10: img_filename = f"0{img_filename}"
        else: img_filename = str(img_filename)

    return generate_discord_py_file_object(f"./data/reactions_images/{img_filename}.png")