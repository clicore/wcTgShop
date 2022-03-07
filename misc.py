import re

def removeHTML(string):
    return re.sub('<[^>]*>', '', string)