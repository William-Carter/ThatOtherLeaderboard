def sanitiseString(inp: str) -> str:
    """
    Ensures that a string is suitable to be sent over discord
    Parameters:
        inp - The string to sanitise

    Returns:
        out - The sanitised string
    """
    out = inp
    escapableCharacters = list("*`_")
    for character in escapableCharacters:
        out = out.replace(character, "\\"+character)

    out = out.replace("\n", " ")



    return out



    