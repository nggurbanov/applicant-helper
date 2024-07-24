import emoji


async def rm(text: str) -> str:
    result = emoji.replace_emoji(text, replace='')

    return result
