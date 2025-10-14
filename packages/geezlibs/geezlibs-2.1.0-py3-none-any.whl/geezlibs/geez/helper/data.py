from pyrogram.types import InlineKeyboardButton, WebAppInfo
from Geez import CMD_HNDLR as cmds
class Data:

    text_help_menu = (
        f"**Geez Pyro Help Menu**\n**Prefixes: **{cmds}"
    )
    reopen = [[InlineKeyboardButton("Open Menu", callback_data="reopen")]]
