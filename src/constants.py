class Consts:
    bot_url = "https://core.telegram.org/bots/api"


class Messages:
    start_message = ("Привет! Это \"Йоу, смотри\" - бот с необычными экскурсиями по Москве в разных форматах. "
                     "Пиши в чат \"/menu\", чтобы познакомиться со списком наших маршрутов!")


class Excursions:
    excursions = {
        "path_1":
            {
                "name": "Path 1",
                "keyboard_callback": "path1",
                "description": "",
                "path_map": "",
                "text_file": "",
                "audio_file": "",
                "video_file": ""
            },
        "path_2":
            {
                "name": "Path 2",
                "keyboard_callback": "path2",
                "description": "",
                "path_map": "",
                "text_file": "",
                "audio_file": "",
                "video_file": ""
            }
    }
