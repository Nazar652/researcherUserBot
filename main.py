from pyrogram import Client, filters
from urllib.request import urlopen
from bs4 import BeautifulSoup

from config import *

combot_url = 'https://combot.org/top/telegram/groups'
tgstat_url = 'https://uk.tgstat.com/ratings/channels'

is_searching = False


client = Client("client",
                api_id=api_id,
                api_hash=api_hash)


@client.on_message(filters.command(commands='start', prefixes='/'))
def start_command(c, m):
    global is_searching
    if is_searching:
        return
    client.send_message(m.from_user.id, 'Введіть назву каналу/чату для пошуку')
    is_searching = True


@client.on_message()
def searching(c, m):
    global is_searching
    if not is_searching:
        return

    tgstat_page = urlopen(tgstat_url)
    html = tgstat_page.read().decode("utf-8")
    tgstat_soup = BeautifulSoup(html, "html.parser")
    all_cards = tgstat_soup.find_all(class_=["card"])
    final_channels = []
    for card in all_cards:
        channel_name = card.find(class_='font-16').text
        if m.text.lower() in channel_name.lower():
            full_url = card.find('a').get('href')
            part_channel_url = full_url.split('/')[-2]
            if part_channel_url[0] == '@':
                full_channel_url = f'https://t.me/{part_channel_url[1:]}'
            else:
                full_channel_url = f'https://t.me/joinchat/{part_channel_url}'
            final_channels.append([
                full_channel_url,
                channel_name
            ])
    final_response = 'Список знайдених каналів:\n\n'
    if final_channels:
        for i in final_channels:
            final_response += f'<a href="{i[0]}">{i[1]}</a>\n'
    else:
        final_response += f'По заданому критерію не знайдено жодного чату\n'

    final_response += '\nЩоб здійснити пошук знову, введіть команду <code>/start</code>'
    is_searching = False
    client.send_message(m.from_user.id, final_response, disable_web_page_preview=True)


client.run()
