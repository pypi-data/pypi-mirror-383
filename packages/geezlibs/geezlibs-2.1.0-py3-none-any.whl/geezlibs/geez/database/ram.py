from geezlibs.geez.database import db_x

db = db_x
collection = db['ram']

async def ram_user(chat):
    doc = {"_id": "ram", "users": [chat]}
    r = await collection.find_one({"_id": "ram"})
    if r:
        await collection.update_one({"_id": "ram"}, {"$push": {"users": chat}})
    else:
        await collection.insert_one(doc)


async def get_ram_users():
    results = await collection.find_one({"_id": "ram"})
    if results:
        return results["users"]
    else:
        return []


async def unram_user(chat):
    await collection.update_one({"_id": "ram"}, {"$pull": {"users": chat}})