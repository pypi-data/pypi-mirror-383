import math

from pygame._sdl2.video import Renderer

from .types import TextureIterable
from .visor import Visor as BaseVisor, VisorMode


class Visor(BaseVisor):
    def render(self, renderer: Renderer, texture_iterable: TextureIterable) -> None:
        factor = self.get_scaling_factor()
        draw_area = self.get_active_screen_area()

        if self.mode == VisorMode.RegionLetterbox:
            renderer.set_viewport(draw_area)
        else:
            renderer.set_viewport(None)

        for world_xy, tex in texture_iterable:
            w = int(math.ceil(tex.width * factor))
            h = int(math.ceil(tex.height * factor))

            sx, sy = self.world_to_screen(world_xy)
            if self.mode == VisorMode.RegionLetterbox:
                sx -= draw_area.x
                sy -= draw_area.y
            tex.draw(dstrect=(sx, sy, w, h))

        renderer.set_viewport(None)
