import emoji

async def rm(text):
    result = emoji.replace_emoji(text, replace='')
    return result