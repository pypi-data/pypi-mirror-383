import dotenv
import heroku3
import os
import sys

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import *
from git import Repo
from git.exc import GitCommandError
from geezlibs.geez.assistant.host import where_hosted
from config import HEROKU_APP_NAME, HEROKU_API_KEY
HOSTED_ON = where_hosted()

@callback(pattern='update_now', client_only=True)
async def update_callback(_, cb: CallbackQuery):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if HOSTED_ON == "Heroku":
        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if not HEROKU_APP_NAME:
            await cb.answer(
                "<•> Please set up the HEROKU_APP_NAME variable to be able to update userbot.",
                show_alert=True,
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await cb.answer(
                f"<i>Invalid Heroku credentials for updating userbot dyno.</i>",
                show_alert=True,
            )
            repo.__del__()
            return
        try:
            await cb.edit_message_text(
            "<b>[HEROKU]:</b> <i>Update Deploy Geez-Pyro Sedang Dalam Proses...</i>"
            )
        except:
            pass
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            await cb.edit_message_text(
            "<i>Geez-Pyro Berhasil Diupdate! Userbot bisa di Gunakan Lagi.</i>"
            )
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await cb.edit_message_text(f"`Here is the error log:\n{error}`")
            repo.__del__()
            return
        except:
            pass
        try:
            await cb.edit_message_text(
            "<i>Geez-Pyro Berhasil Diupdate! Userbot bisa di Gunakan Lagi.</i>"
            )
        except:
            pass
    else:
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await install_requirements()
        try:
            await cb.edit_message_text(
            "<i>Geez-Pyro Berhasil Diupdate! Userbot bisa di Gunakan Lagi.</i>",
            )
        except:
            pass
        args = [sys.executable, "-m", "pyAyiin"]
        os.execle(sys.executable, *args, os.environ)
        return


@callback(pattern='changelog', client_only=True)
async def changelog_callback(client, cb: CallbackQuery):
    msg = cb.message
    changelog, tl_chnglog = await yins.gen_chlog(
        repo, f"HEAD..upstream/{branch}"
    )
    if changelog:
        if len(changelog) > 4096:
            await cb.edit_message_text("<b>Changelog terlalu besar, dikirim sebagai file.</b>")
            file = open("output.txt", "w+")
            file.write(changelog)
            file.close()
            await client.send_document(
                msg.chat.id,
                "output.txt",
                caption=f"**Klik Tombol** `Update` **Untuk Mengupdate Userbot.**",
                reply_to_message_id=yins.ReplyCheck(msg),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="•• Update ••",
                                callback_data=f"update_now",
                            )
                        ]
                    ]
                ),
            )
            os.remove("output.txt")
        await cb.edit_message_text(
            changelog,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="•• Update ••",
                            callback_data=f"update_now",
                        )
                    ]
                ]
            ),
        )


@callback(pattern="terima_(.*)", client_only=True)
async def get_back(client: Client, cb: CallbackQuery):
    user_ids = int(cb.matches[0].group(1))
    await yins.approve_pmpermit(cb, user_ids, OLD_MSG)


@callback(pattern="tolak_(.*)", client_only=True)
async def get_back(client: Client, cb: CallbackQuery):
    user_ids = int(cb.matches[0].group(1))
    await yins.disapprove_pmpermit(cb, user_ids)