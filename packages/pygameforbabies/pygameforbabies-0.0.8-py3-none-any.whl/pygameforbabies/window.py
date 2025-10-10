import pygame
size = (800,600)
title = "Meow"
icon = pygame.Surface((1,1))
screencolor = "black"
resizeable = False
fullscreen = False
fps = 60
gl = False
def changeicon(path):
    global icon
    icon = pygame.image.load(path)