def get_token(path):
    with open(f"{path}.txt", "r", encoding="utf-8") as file:
        token = file.readline()
    return token


bot_token = get_token("bot_token")
user_token = get_token("user_token")
