from typing import TypeGuard, Iterable, TYPE_CHECKING
from pygame import Vector2, Rect, FRect, Surface

if TYPE_CHECKING:
    try:
        from pygame._sdl2.video import Texture
    except ImportError:
        pass

__all__ = [
    "IntPair",
    "FloatPair",
    "IntQuad",
    "FloatQuad",
    "WorldPos",
    "ScreenPos",
    "WorldSize",
    "ScreenSize",
    "WorldRect",
    "ScreenRect",
    "is_screen_rect",
    "is_screen_size",
    "is_world_rect",
    "is_world_size",
    "SurfaceIterable",
    "TextureIterable",
    "Limits",
    "is_limits",
]

type IntPair = tuple[int, int]
type IntQuad = tuple[int, int, int, int]
type FloatPair = tuple[float, float]
type FloatQuad = tuple[float, float, float, float]

type WorldPos = IntPair | FloatPair | Vector2
type ScreenPos = IntPair

type WorldSize = IntPair | FloatPair | Vector2
type ScreenSize = IntPair

type WorldRect = IntPair | FloatPair | IntQuad | FloatQuad | Rect | FRect
type ScreenRect = IntPair | IntQuad | Rect

type SurfaceIterable = Iterable[tuple[WorldPos, Surface]]
type TextureIterable = Iterable[tuple[WorldPos, Texture]]

type Limits = IntQuad | FloatQuad


def is_screen_rect(s: ScreenRect) -> TypeGuard[IntQuad | Rect]:
    return len(s) == 4


def is_screen_size(s: ScreenRect) -> TypeGuard[ScreenSize]:
    return len(s) == 2


def is_world_rect(s: WorldRect) -> TypeGuard[IntQuad | FloatQuad | Rect | FRect]:
    return len(s) == 4


def is_world_size(s: WorldRect) -> TypeGuard[WorldSize]:
    return len(s) == 2


def is_limits(s: Limits) -> TypeGuard[IntQuad | FloatQuad]:
    return (
        len(s) == 4
        and isinstance(s, tuple)
        and all(isinstance(v, (int, float)) for v in s)
    )
