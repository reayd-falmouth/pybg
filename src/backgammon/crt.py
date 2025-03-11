import json
import os
import random
import struct
import pygame
import pygame_gui
import moderngl
from pygame.locals import *
import asyncio

DIRNAME = os.path.dirname(__file__)

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800  # 640, 360 itchio default
VIRTUAL_RES = (320, 200)
# VIRTUAL_RES = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 30
WHITE, BLACK, GREY, TRANSLUCENT_BLACK, TRANSLUCENT = (
    (255, 255, 255),
    (0, 0, 0),
    (200, 200, 200),
    (0, 0, 0, 100),
    (0, 0, 0, 0),
)
TEXT_BOX_PADDING = 10
TEXT_BOX_WIDTH = SCREEN_WIDTH - 100
TEXT_BOX_HEIGHT_OFFSET = SCREEN_HEIGHT / 3
# Initialize pygame and OpenGL
pygame.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
ctx = moderngl.create_context()
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Oblique Strategy Games")

# Load Shader
prog = ctx.program(
    vertex_shader=open(f"{DIRNAME}/assets/shaders/vertex.glsl").read(),
    fragment_shader=open(f"{DIRNAME}/assets/shaders/fragment.glsl").read(),
)

# Fullscreen Quad for Shader
texture_coordinates = [0, 1, 1, 1, 0, 0, 1, 0]
world_coordinates = [-1, -1, 1, -1, -1, 1, 1, 1]
render_indices = [0, 1, 2, 1, 2, 3]

vbo = ctx.buffer(struct.pack("8f", *world_coordinates))
uvmap = ctx.buffer(struct.pack("8f", *texture_coordinates))
ibo = ctx.buffer(struct.pack("6I", *render_indices))

vao_content = [(vbo, "2f", "vert"), (uvmap, "2f", "in_text")]
vao = ctx.vertex_array(prog, vao_content, ibo)

# Load custom pixel fonts
BASE_FONT_SIZE = 48
TITLE_FONT_SIZE = BASE_FONT_SIZE
DESCRIPTION_FONT_SIZE = BASE_FONT_SIZE - 20
DETAILED_DESCRIPTION_FONT_SIZE = BASE_FONT_SIZE - 34
METADATA_FONT_SIZE = int(BASE_FONT_SIZE / 2)
TAGS_FONT_SIZE = BASE_FONT_SIZE - 28
title_font = pygame.font.Font(f"{DIRNAME}/assets/fonts/m6x11.ttf", TITLE_FONT_SIZE)
description_font = pygame.font.Font(
    f"{DIRNAME}/assets/fonts/m6x11.ttf", DESCRIPTION_FONT_SIZE
)
detailed_description_font = pygame.font.Font(
    f"{DIRNAME}/assets//fonts/m6x11.ttf", DETAILED_DESCRIPTION_FONT_SIZE
)
metadata_font = pygame.font.Font(
    f"{DIRNAME}/assets/fonts/m6x11.ttf", METADATA_FONT_SIZE
)
tags_font = pygame.font.Font(f"{DIRNAME}/assets/fonts/m6x11.ttf", TAGS_FONT_SIZE)

cover_path = f"{DIRNAME}/assets/img/banner/cover.png"

screen = pygame.Surface(VIRTUAL_RES).convert((255, 65280, 16711680, 0))
screen_texture = ctx.texture(VIRTUAL_RES, 3, pygame.image.tostring(screen, "RGB", 1))
screen_texture.repeat_x = False
screen_texture.repeat_y = False


# Shader Rendering Function
def render_shader():
    texture_data = screen.get_view("1")
    screen_texture.write(texture_data)
    ctx.clear(14 / 255, 40 / 255, 66 / 255)
    screen_texture.use()
    vao.render()
    pygame.display.flip()


# Main Loop
async def main():
    global current_game_index
    running = True
    while running:
        time_delta = clock.tick(FPS) / 1000.0
        screen.fill((0, 0, 0))
        cover_path = f"{DIRNAME}/assets/img/menu/banner/background.png"
        cover_image = pygame.image.load(cover_path).convert()
        cover_image = pygame.transform.scale(cover_image, VIRTUAL_RES)
        screen.blit(cover_image, (0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        render_shader()

    pygame.quit()


asyncio.run(main())
