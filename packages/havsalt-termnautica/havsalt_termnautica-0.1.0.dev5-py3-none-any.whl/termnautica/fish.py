import random
from enum import ReprEnum, Enum, auto
from typing import TYPE_CHECKING, assert_never

import pygame
import colex
from colex import ColorValue
from charz import Sprite, Scene, Group, Vec2, text, clamp, sign

from . import settings
from .props import Collectable, Interactable, Targetable, HasHealth
from .player import Player
from .item import ItemID
from .particles import Blood
from .utils import move_toward

# Type checking for lazy loading
if TYPE_CHECKING:
    from . import ocean
else:
    ocean = None


# Expand text flipping db
text._horizontal_conversions["»"] = "«"
text._horizontal_conversions["«"] = "»"


def _ensure_ocean() -> None:
    # Lazy loading - A quick workaround
    global ocean
    if ocean is None:
        from . import ocean


type MinFrameTime = int
type MaxFrameTime = int


class FishState(tuple[MinFrameTime, MaxFrameTime], ReprEnum):
    IDLE = (43, 63)
    WANDRING = (17, 87)
    FLEEING = (20, 40)
    FLOATING = (30, 42)


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()


class FishAI:
    _SPEED_SCALE: float = 0.1
    _ACCELERATION: Vec2 = Vec2(0.2, 1.1)
    _FRICTION: Vec2 = Vec2(0.15, 0.50)
    _MAX_SPEED: Vec2 = Vec2(7, 10)
    _QUICK_FACTOR: float = 3
    speed_x: float = 0
    speed_y: float = 0
    _state: FishState = FishState.IDLE
    _direction: Direction = Direction.LEFT  # Sprites are drawn facing left
    _action_time_remaining: int = 0
    assert _ACCELERATION > _FRICTION, "Invalid constants"

    def update(self) -> None:
        assert isinstance(self, Sprite), f"`Sprite` base missing for {self}"

        if self.is_submerged():  # Activate AI when in water
            self._action_time_remaining -= 1
            if self._action_time_remaining <= 0:
                states = tuple(FishState)
                self._state = (min_time, max_time) = random.choice(states)
                self._action_time_remaining = random.randint(min_time, max_time)
                self._direction = Direction.NONE
                # Random change of Y-level
                self.position.y += random.randint(-1, 1)

        match self._state:
            case FishState.IDLE:
                self.speed_x = move_toward(self.speed_x, 0, self._FRICTION.x)
                self.position.x += self.speed_x * self._SPEED_SCALE
            case FishState.WANDRING:
                self.move()
            case FishState.FLEEING:
                self.move(quick=True)
            case FishState.FLOATING:
                self.position.x += self.speed_x * self._SPEED_SCALE
            case _:
                assert_never(self._state)

        # Fall if above ocean top - Gravity
        if self.is_submerged():
            self.speed_y = move_toward(self.speed_y, 0, self._FRICTION.y)
            while ocean.Floor.has_loose_point_inside(self.global_position):
                self.position += Vec2.UP
        else:
            self.speed_y += self._ACCELERATION.y
            self.speed_y = clamp(self.speed_y, -self._MAX_SPEED.y, self._MAX_SPEED.y)
        self.position.y += self.speed_y * self._SPEED_SCALE

    def is_submerged(self) -> bool:
        _ensure_ocean()  # Lazy load `OceanWater`
        assert isinstance(self, Sprite), f"`Sprite` base missing for {self}"
        self_height = self.global_position.y - self.get_texture_size().y / 2
        wave_height = ocean.Water.wave_height_at(self.global_position.x)
        return self_height - wave_height > 0

    def move(self, quick: bool = False) -> None:
        assert isinstance(self, Sprite), f"`Sprite` base missing for {self}"

        acceleration = (
            self._ACCELERATION.x
            if not quick
            else self._QUICK_FACTOR * self._ACCELERATION.x
        )

        if self._direction is Direction.NONE:
            if random.randint(0, 1):
                self._direction = Direction.LEFT
                self.texture = self.__class__.texture
            else:
                self._direction = Direction.RIGHT
                self.texture = text.flip_lines_h(self.__class__.texture)

        if self._direction is Direction.LEFT:
            self.speed_x -= acceleration
        elif self._direction is Direction.RIGHT:
            self.speed_x += acceleration
        self.speed_x = clamp(self.speed_x, -self._MAX_SPEED.x, self._MAX_SPEED.x)

        self.position.x += self.speed_x * 0.1
        if not quick:  # Friction when moving normal
            self.speed_x = move_toward(self.speed_x, 0, self._FRICTION.x)


class BaseFish(FishAI, Interactable, Collectable, Sprite):
    _SOUND_COLLECT = pygame.mixer.Sound(settings.SOUNDS_FOLDER / "collect" / "fish.wav")
    centered = True


class SmallFish(BaseFish):
    _SOUND_COLLECT = pygame.mixer.Sound(
        settings.SOUNDS_FOLDER / "collect" / "small_fish.wav"
    )
    _ITEM = ItemID.GOLD_FISH
    color = colex.DARK_SALMON
    texture = ["<><"]


class MediumFish(BaseFish):
    _ITEM = ItemID.COD
    color = colex.from_hex("#659285")
    texture = ["<[Xx"]


class LongFish(BaseFish):
    _ITEM = ItemID.SALMON
    color = colex.SALMON
    texture = ["<º)))))}><"]


class WaterFish(BaseFish):
    _ITEM = ItemID.BLADDER_FISH
    color = colex.LAVENDER
    texture = ["<?))>("]


# TODO: Add achievement for this
class Nemo(BaseFish):
    _SOUND_COLLECT = pygame.mixer.Sound(settings.SOUNDS_FOLDER / "collect" / "nemo.wav")
    _ITEM = ItemID.NEMO
    color = colex.LIGHT_SALMON
    texture = ["<)))<"]


class SwordFish(FishAI, HasHealth, Interactable, Targetable, Sprite):
    _REACH = 6  # Shorter reach to attack it
    _REACH_CENTER = Vec2(6, 0)
    _DAMAGE: int = 15
    _ATTACK_INTERVAL: int = 10  # Frames
    _SOUND_HIT = pygame.mixer.Sound(settings.SOUNDS_FOLDER / "hit.wav")
    _SOUND_LURK = pygame.mixer.Sound(settings.SOUNDS_FOLDER / "hostile_fish_lurk.wav")
    _CHANNEL_LURK = pygame.mixer.Channel(4)
    _SOUND_LURK_CHANCE: int = 2000  # 1 out of X chance
    _STEALTH_COLOR: ColorValue = colex.from_hex("#2B2B2B")
    _ATTACKED_BLOOD_COUNT: int = 3
    _DEATH_BLOOD_COUNT: int = 10
    # color = colex.from_hex("#adcdc0")
    color = colex.from_hex("#ffd966")
    # texture = ["«««Ó(((()><"]
    # texture = ["«««°(((()><"]
    texture = ["«««Ó((ΞΞΞΞx<"]
    _health: float = 5
    _attack_cooldown: int = 0
    _is_highlighted: bool = False

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value: float) -> None:
        self._health = value
        if self._health <= 0:
            self.queue_free()

    def on_interact(self, actor: Sprite) -> None:
        assert isinstance(actor, Player), "Only `Player` can attack `SwordFish`"
        self._health -= actor.damage
        for _ in range(self._ATTACKED_BLOOD_COUNT):
            blood = Blood().with_global_position(self.global_position)
            blood.position.x += random.randint(-2, 2)
            self._SOUND_HIT.play()
        if self._health <= 0:
            self.queue_free()
            for _ in range(self._DEATH_BLOOD_COUNT):
                blood = Blood().with_global_position(self.global_position)
                blood.position.x += random.randint(-2, 2)

    def grab_focus(self) -> None:
        super().grab_focus()
        self._is_highlighted = True

    def loose_focus(self) -> None:
        super().loose_focus()
        self._is_highlighted = False

    def update(self) -> None:
        # TODO: Add spatial sound
        if (
            random.randint(1, self._SOUND_LURK_CHANCE) == 1
            and not self._CHANNEL_LURK.get_busy()
        ):
            self._CHANNEL_LURK.play(self._SOUND_LURK)
        # TODO: Refactor this quick solution
        super().update()  # Process `FishAI`
        if not self.is_submerged():
            return
        self._attack_cooldown -= 1
        if self._attack_cooldown >= 0:
            return
        for node in Scene.current.groups[Group.TEXTURE].values():
            if isinstance(node, Player):
                if node.is_in_building():
                    self.color = self.__class__.color
                    continue
                # TODO: Properly center fish
                dist = self.global_position.distance_to(node.global_position)
                if dist < 20:
                    direction = self.global_position.direction_to(node.global_position)
                    self.position += direction * 0.5
                    if sign(direction.x) == 1:
                        self.texture = text.flip_lines_h(self.__class__.texture)
                    else:
                        self.texture = self.__class__.texture
                    self.color = self._STEALTH_COLOR
                if dist < 4:
                    self._attack_cooldown = self._ATTACK_INTERVAL
                    node.health -= self._DAMAGE
                    self.color = self.__class__.color
                if dist >= 20:
                    self.color = self.__class__.color
                break
        # Respect highlight
        assert self.color is not None, "Color of `Swordfish` was None"
        # `colex.REVERSE` means highlighted
        if colex.REVERSE not in self.color and self._is_highlighted:
            self.color = colex.REVERSE + self.color
