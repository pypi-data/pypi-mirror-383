from ..scripts import Scripted
from ..exceptions import InvalidReply
from pyrogram.types import ForceReply
#===========================================================================

class SRename:

    DATA01 = None
    DATA02 = "F01"
    DATA03 = "C01"
    DATA04 = "{filename}"

#===========================================================================

class BRename:

    async def get01(update, incoming):
        if (Scripted.DATA02 in incoming) and (update.reply_to_message):
            return True
        else:
            raise InvalidReply()


    async def get10(incoming):
        moonus = incoming.replace("/", Scripted.DATA02) if '/' in incoming else incoming
        return moonus.strip()

#===========================================================================================================================

    async def get20(update):
        if (update.reply_to_message.reply_markup) and isinstance(update.reply_to_message.reply_markup, ForceReply):
            return True
        else:
            return False

#===========================================================================================================================
