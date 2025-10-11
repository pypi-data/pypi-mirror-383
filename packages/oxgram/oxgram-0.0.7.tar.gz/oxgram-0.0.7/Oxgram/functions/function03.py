from .collections import SMessage
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
#====================================================================

class Channel:

    async def main(users):
        if (users.status == ChatMemberStatus.BANNED):
            return 200
        else:
            return 100

#====================================================================

    async def get01(bot, update, channel=None):
        if not channel:
            return SMessage(taskcode=100)
        try:
            userid = update.from_user.id
            usered = await bot.get_chat_member(channel, userid)
            userod = await Channel.main(usered)
            return SMessage(taskcode=userod)
        except UserNotParticipant:
            return SMessage(taskcode=300)
        except Exception as errors:
            return SMessage(taskcode=400, errors=errors)

#====================================================================
