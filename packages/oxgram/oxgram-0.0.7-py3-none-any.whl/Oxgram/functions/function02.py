from pyrogram.enums import MessageEntityType
#==============================================================================================

class Flinks:

    async def get01(update, incoming):
        amoend = filter(lambda o: o.type == MessageEntityType.URL, update.entities)
        amoond = list(amoend)
        neomos = amoond[0].offset
        sosmso = amoond[0].length
        linked = incoming[ neomos : neomos + sosmso ]
        return linked

#==============================================================================================
