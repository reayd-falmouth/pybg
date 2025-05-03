import struct
import moderngl
import pygame
from pybg.constants import ASSETS_DIR


class ShaderRenderer:
    def __init__(self, screen, enabled=True):
        self.enabled = enabled
        if self.enabled:
            self.ctx = moderngl.create_context()
            self.prog = self.ctx.program(
                vertex_shader=open(f"{ASSETS_DIR}/shaders/vertex.glsl").read(),
                fragment_shader=open(f"{ASSETS_DIR}/shaders/fragment.glsl").read(),
            )

            texture_coordinates = [0, 1, 1, 1, 0, 0, 1, 0]
            world_coordinates = [-1, -1, 1, -1, -1, 1, 1, 1]
            render_indices = [0, 1, 2, 1, 2, 3]

            self.vbo = self.ctx.buffer(struct.pack("8f", *world_coordinates))
            self.uvmap = self.ctx.buffer(struct.pack("8f", *texture_coordinates))
            self.ibo = self.ctx.buffer(struct.pack("6I", *render_indices))

            vao_content = [(self.vbo, "2f", "vert"), (self.uvmap, "2f", "in_text")]
            self.vao = self.ctx.vertex_array(self.prog, vao_content, self.ibo)

            # Create initial texture using the passed screen's size.
            self.screen_texture = self.ctx.texture(
                screen.get_size(), 3, pygame.image.tostring(screen, "RGB", 1)
            )
            self.screen_texture.repeat_x = False
            self.screen_texture.repeat_y = False
        else:
            self.ctx = None

    def render(self, surface):
        """Renders the shader effect using the given surface."""
        if not self.enabled:
            pygame.display.flip()
            return

        # Flip the surface vertically before converting to texture.
        flipped_surface = pygame.transform.flip(surface, False, True)
        new_size = surface.get_size()

        # If the texture size doesn't match the new size, recreate it.
        if self.screen_texture.size != new_size:
            self.screen_texture = self.ctx.texture(
                new_size, 3, pygame.image.tostring(surface, "RGB", 1)
            )
            self.screen_texture.repeat_x = False
            self.screen_texture.repeat_y = False

        texture_data = pygame.image.tostring(flipped_surface, "RGB", 1)
        self.screen_texture.write(texture_data)  # Update texture with new frame data.

        self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
        self.screen_texture.use()
        self.vao.render()
        pygame.display.flip()

    def toggle(self):
        """Toggles the shader on/off."""
        self.enabled = not self.enabled
