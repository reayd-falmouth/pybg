import struct

import moderngl
import pygame

from oblique_games import ASSETS_DIR


class ShaderRenderer:
    def __init__(self, screen, enabled=True):
        self.enabled = enabled
        self.ctx = moderngl.create_context()

        if self.enabled:
            # Load Shader
            self.prog = self.ctx.program(
                vertex_shader=open(f"{ASSETS_DIR}/shaders/vertex.glsl").read(),
                fragment_shader=open(f"{ASSETS_DIR}/shaders/fragment.glsl").read(),
            )

            # Fullscreen Quad for Shader
            texture_coordinates = [0, 1, 1, 1, 0, 0, 1, 0]
            world_coordinates = [-1, -1, 1, -1, -1, 1, 1, 1]
            render_indices = [0, 1, 2, 1, 2, 3]

            self.vbo = self.ctx.buffer(struct.pack("8f", *world_coordinates))
            self.uvmap = self.ctx.buffer(struct.pack("8f", *texture_coordinates))
            self.ibo = self.ctx.buffer(struct.pack("6I", *render_indices))

            vao_content = [(self.vbo, "2f", "vert"), (self.uvmap, "2f", "in_text")]
            self.vao = self.ctx.vertex_array(self.prog, vao_content, self.ibo)

            # Texture setup
            self.screen_texture = self.ctx.texture(
                screen.get_size(), 3, pygame.image.tostring(screen, "RGB", 1)
            )
            self.screen_texture.repeat_x = False
            self.screen_texture.repeat_y = False

    def render(self, screen):
        """Renders the shader effect."""
        if not self.enabled:
            pygame.display.flip()
            return

        # Flip the surface vertically before converting to texture
        flipped_screen = pygame.transform.flip(screen, False, True)

        # Convert to RGB format and upload to texture
        texture_data = pygame.image.tostring(flipped_screen, "RGB", 1)
        self.screen_texture.write(texture_data)  # Write converted texture

        self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
        self.screen_texture.use()
        self.vao.render()
        pygame.display.flip()

    def toggle(self):
        """Toggles the shader on/off"""
        self.enabled = not self.enabled
