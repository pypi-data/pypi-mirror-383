import codecs
import pickle
from geezlibs.geez.database import db_x
from typing import Dict, List, Union

notesdb = db_x["notes"]

def obj_to_str(obj):
    if not obj:
        return False
    string = codecs.encode(pickle.dumps(obj), "base64").decode()
    return string


def str_to_obj(string: str):
    obj = pickle.loads(codecs.decode(string.encode(), "base64"))
    return obj


async def get_notes_count() -> dict:
    chats_count = 0
    notes_count = 0
    async for chat in notesdb.find({"chat_id": {"$exists": 1}}):
        notes_name = await get_note_names(chat["chat_id"])
        notes_count += len(notes_name)
        chats_count += 1
    return {"chats_count": chats_count, "notes_count": notes_count}


async def _get_notes(chat_id: int) -> Dict[str, int]:
    _notes = await notesdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_note_names(chat_id: int) -> List[str]:
    _notes = []
    for note in await _get_notes(chat_id):
        _notes.append(note)
    return _notes


async def get_note(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _notes = await _get_notes(chat_id)
    if name in _notes:
        return _notes[name]
    return False


async def save_note(chat_id: int, name: str, note: dict):
    name = name.lower().strip()
    _notes = await _get_notes(chat_id)
    _notes[name] = note

    await notesdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_note(chat_id: int, name: str) -> bool:
    notesd = await _get_notes(chat_id)
    name = name.lower().strip()
    if name in notesd:
        del notesd[name]
        await notesdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False
