# List of all the project's strings.

GENERAL_STRINGS = {
    "GENERAL_WelcomeString": {
        "it": """
                 Ciao, sono TasteIT, ti aiuterò nella ricerca del locale perfetto in cui mangiare.\n\nDigita il comando /help per avere una completa panoramica delle funzionalità offerte.
              """,
        "en": """
                 Hi, I am TasteIT, and I will help you to search for the perfect restaurant to have a meal.\n\nTry the /help command for having a complete overview of my functionalities.
              """,
    },
}

ERROR_STRINGS = {}


def getString(stringName, language, *args):
    if stringName.startswith("GENERAL"):
        return GENERAL_STRINGS.get(stringName).get(language).format(*args)
    else:
        return ERROR_STRINGS.get(stringName).get(language).format(*args)
