def allowed_characters_check(text, allowed_characters):
    new_text = text
    for character in text:
        if character not in allowed_characters:
            new_text = new_text.replace(character, '')
    return new_text


def forbidden_characters_check(text, forbidden_characters):
    new_text = text
    for character in text:
        if character in forbidden_characters:
            new_text = new_text.replace(character, '')
    return new_text
