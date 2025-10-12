from enum import Enum, auto
import math
import functools

import pygame
from pygame import FRect
from pygame.typing import RectLike

from .types import (
    WorldPos,
    ScreenPos,
    ScreenSize,
    ScreenRect,
    SurfaceIterable,
    is_screen_rect,
    is_screen_size,
    Limits,
    is_limits,
)

__all__ = ["VisorMode", "Visor"]


class VisorMode(Enum):
    RegionLetterbox = auto()
    RegionExpand = auto()


class Visor:
    mode: VisorMode
    screen: ScreenSize
    region: FRect
    limits: Limits | None

    def __init__(
        self,
        mode: VisorMode,
        screen: ScreenRect,
        *,
        region: RectLike,
        limits: Limits | None = None,
    ) -> None:
        self.mode = mode
        self.screen = self._screen_size(screen)
        self.region = FRect(region)
        self.set_limits(limits)

    def set_limits(self, limits: Limits | None) -> None:
        if limits is not None and not is_limits(limits):
            raise ValueError(
                f"Limits specified do not have the right format. "
                f"Makes sure they're of type: {Limits.__value__}"
            )
        self.limits = limits

    def update_screen(self, screen: ScreenRect) -> None:
        """
        Call this whenever your screen size or surface size changes.
        """
        old_screen = self.screen
        self.screen = self._screen_size(screen)
        if old_screen != self.screen:
            self.clear_scaling_cache()

    def lerp_to(self, pos: WorldPos, weight: float = 1.0) -> None:
        px, py = pos
        cx, cy = self.region.center
        x = pygame.math.lerp(cx, px, weight)
        y = pygame.math.lerp(cy, py, weight)
        self.move_to((x, y))

    def move_to(self, pos: WorldPos) -> None:
        self.region.center = pos[0], pos[1]
        if self.limits is None:
            return

        lx1, ly1, lx2, ly2 = self.limits

        l_width = abs(lx2 - lx1)
        l_height = abs(ly2 - ly1)

        if l_width < self.region.width:
            self.region.centerx = lx1 + l_width / 2
        elif self.region.left < lx1:
            self.region.left = lx1
        elif self.region.right > lx2:
            self.region.right = lx2

        if l_height < self.region.height:
            self.region.centery = ly1 + l_height / 2
        elif self.region.top < ly1:
            self.region.top = ly1
        elif self.region.bottom > ly2:
            self.region.bottom = ly2

    def scale_by_at(self, factor: int | float, pos: WorldPos | None = None) -> None:
        """Scale (zoom in/out) by factor around the given world pos. If None, center is used."""
        wx, wy = pos if pos is not None else self.region.center
        screen_pos = self.world_to_screen((wx, wy))
        self.region.scale_by_ip(factor, factor)

        wxy = self.screen_to_world(screen_pos)
        if wxy is None:
            raise ValueError("Cannot scale outside the world")

        wx2, wy2 = wxy
        wdx, wdy = wx - wx2, wy - wy2
        cx, cy = self.region.center
        self.move_to((wdx + cx, wdy + cy))

    @staticmethod
    def _screen_size(screen_rect: ScreenRect) -> ScreenSize:
        if is_screen_rect(screen_rect):
            sx, sy, sw, sh = screen_rect
            if (sx, sy) != (0, 0):
                raise ValueError("Screen rects must start at x=0, y=0")
            return sw, sh
        elif is_screen_size(screen_rect):
            sw, sh = screen_rect
            return sw, sh
        else:
            raise ValueError(
                f"screen_rect does not have a valid size of 2 or 4: {len(screen_rect)}"
            )

    def get_bounding_box(self) -> FRect:
        """
        Return the world region that needs to be rendered for display.
        """
        sw, sh = self.screen

        if self.mode == VisorMode.RegionLetterbox:
            # the region to render is exactly the current region stored
            return FRect(self.region)

        # we need a bit more, depending on the size of the screen
        screen_ratio = sw / sh
        region_ratio = self.region.width / self.region.height

        if screen_ratio > region_ratio:
            # screen is wider
            new_width = math.ceil(self.region.height * screen_ratio)
            extra_width = new_width - self.region.width
            return FRect(
                self.region.x - (extra_width // 2),
                self.region.y,
                new_width,
                self.region.height,
            )

        # screen is higher
        new_height = math.ceil(self.region.width / screen_ratio)
        extra_height = new_height - self.region.height
        return FRect(
            self.region.x,
            self.region.y - (extra_height // 2),
            self.region.width,
            new_height,
        )

    def get_scaling_factor(self) -> float:
        sw, sh = self.screen
        screen_ratio = sw / sh
        region_ratio = self.region.width / self.region.height

        if screen_ratio > region_ratio:
            return sh / self.region.height
        return sw / self.region.width

    def get_active_screen_area(self) -> pygame.Rect:
        """
        Returns a screen rect of the world region translated to the screen, excluding
        any extended areas (doesn't consider ViewMode for calculcatio).
        This is so we can place UI or similar within that area.
        """
        factor = self.get_scaling_factor()
        sw, sh = self.screen

        # world-screen width/height
        ws_width = self.region.width * factor
        ws_height = self.region.height * factor

        left = (sw - ws_width) // 2
        top = (sh - ws_height) // 2

        return pygame.Rect(left, top, ws_width, ws_height)

    def screen_to_world(self, screen_pos: ScreenPos) -> pygame.Vector2 | None:
        """May return None in RegionLetterbox, if the pos is outside the bounding box"""
        # ViewMode.RegionLetterbox
        # region = (0, 0, 400, 300)
        # screen_rect = (0, 0, 1920, 1080)   -- region scaled to: (1440, 1080)
        # pos = (384, 108)                   -- 240 + 144  (240 padding + 10% of 1440; 10% of 1080)
        # expected world_pos = (40, 30)      -- (10% of 400; 10% of 300)

        sx, sy = screen_pos
        factor = self.get_scaling_factor()
        ws_x, ws_y, _, _ = self.get_active_screen_area()

        wx = (sx - ws_x) / factor + self.region.x
        wy = (sy - ws_y) / factor + self.region.y

        if self.mode == VisorMode.RegionLetterbox:
            if (
                self.region.left <= wx < self.region.right
                and self.region.top <= wy < self.region.bottom
            ):
                return pygame.Vector2(wx, wy)
            return None

        return pygame.Vector2(wx, wy)

    def world_to_screen(self, world_pos: WorldPos) -> ScreenPos:
        # ViewMode.RegionLetterbox
        # region = (0, 0, 400, 300)
        # screen_rect = (0, 0, 1920, 1080)   -- region scaled to: (1440, 1080)
        # world_pos = (40, 30)               -- (10% of 400; 10% of 300)
        # expected screen_pos = (384, 108)   -- 240 + 144  (240 padding + 10% of 1440; 10% of 1080)

        wx, wy = world_pos
        factor = self.get_scaling_factor()
        ws_x, ws_y, _, _ = self.get_active_screen_area()

        sx = int((wx - self.region.x) * factor + ws_x)
        sy = int((wy - self.region.y) * factor + ws_y)

        return sx, sy

    @functools.lru_cache(maxsize=20)
    def _get_scaled_surface(
        self, surface: pygame.Surface, width: int, heigth: int
    ) -> pygame.Surface:
        return pygame.transform.scale(surface, (width, heigth))

    @classmethod
    def update_scaling_cache(cls, maxsize: int) -> None:
        """
        Usually 20 entries is enough if your surfaces are sufficiently large (recommended).
        But you can increase it using this method. Set it to a value of at *minimum* the number of
        surfaces you expect to be passed to the render method below.

        Use get_scaling_cache_info() to get stats on the current size and hits/misses.
        If the misses stay mostly static while the camera is not moving, that's usually a good sign.
        """
        original_method = getattr(cls._get_scaled_surface, "__wrapped__", None)
        if original_method is None:
            original_method = cls._get_scaled_surface

        cls.clear_scaling_cache()
        cls._get_scaled_surface = functools.lru_cache(maxsize=maxsize)(original_method)  # type: ignore[method-assign]

    @classmethod
    def get_scaling_cache_info(cls) -> functools._CacheInfo:
        return cls._get_scaled_surface.cache_info()

    @classmethod
    def clear_scaling_cache(cls) -> None:
        if hasattr(cls._get_scaled_surface, "cache_clear"):
            cls._get_scaled_surface.cache_clear()

    def render(
        self, surface: pygame.Surface, surface_iterable: SurfaceIterable
    ) -> None:
        screen_rect = surface.get_rect()
        assert screen_rect.size == self.screen, (
            "Screen rect sizes differ. Make sure to use update_screen(rect) "
            "before calling this method, if your screen size changed."
        )
        factor = self.get_scaling_factor()
        draw_area = self.get_active_screen_area()
        if self.mode == VisorMode.RegionLetterbox:
            subsurface = surface.subsurface(draw_area)
        else:
            subsurface = surface

        for world_xy, surf in surface_iterable:
            if not math.isclose(factor, 1.0):
                w = math.ceil(surf.get_width() * factor)
                h = math.ceil(surf.get_height() * factor)
                surf = self._get_scaled_surface(surf, w, h)
            sx, sy = self.world_to_screen(world_xy)
            if self.mode == VisorMode.RegionLetterbox:
                sx -= draw_area.x
                sy -= draw_area.y
            subsurface.blit(surf, (sx, sy))
