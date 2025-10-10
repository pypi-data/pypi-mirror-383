"Note: this can only be used in a connection function or else it won't work"
from pygame import scrap
from pygame import SCRAP_TEXT
def _init():
    scrap.init()
def get_text():
    return scrap.get(SCRAP_TEXT)
def set_text(text=""):
    scrap.put(SCRAP_TEXT, text.encode())