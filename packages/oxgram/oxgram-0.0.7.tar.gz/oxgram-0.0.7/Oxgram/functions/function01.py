from pyrogram.file_id import FileId
#=========================================================================================================

class Pyrogram:

    async def get01(update):
        medias = await Pyrogram.get20(update)
        filexs = medias.file_id
        fileud = FileId.decode(filexs)
        moonus = fileud.dc_id
        return moonus

#=========================================================================================================

    async def get20(update):
        return update.video or update.audio or update.voice or update.document or update.video_note

#=========================================================================================================
