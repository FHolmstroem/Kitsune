"""
Fox behavior and state machine.

The Pet class holds the fox's current state (walking, idle, sleeping,
hiding, peeking) and decides what it should do next each tick.

States:
    IDLE      — standing still, occasional ear twitch
    WALKING   — moving left or right across the screen
    SLEEPING  — zzz, triggered after long idle
    HIDING    — tucked behind a window edge
    PEEKING   — peeking out from behind a window
    FLEEING   — running away after being clicked/shooed

The state machine is intentionally simple — each state has
a duration and a set of possible next states with weights.
"""
"""
Fox behavior and state machine.

The Pet class holds the fox's current state (walking, idle, sleeping)
and decides what it should do next each tick.
"""

import random
from dataclasses import dataclass
from enum import Enum

class PetState(str, Enum):
    IDLE = "idle"
    WALKING_LEFT = "walk_left"
    WALKING_RIGHT = "walk_right"
    FLEEING_LEFT = "fleeing_left"    # Updated!
    FLEEING_RIGHT = "fleeing_right"  # Updated!
    WALK_UP = "walk_up"
    WALK_DOWN = "walk_down"
    DIAG_UP_RIGHT = "diag_up_right"
    DIAG_DOWN_LEFT = "diag_down_left"

    # TODO: add sleep state


@dataclass
class StateConfig:
    next_states: list[tuple[PetState, int]]
    min_duration_ms: float
    max_duration_ms: float
    speed_x: float = 0.0
    speed_y: float = 0.0

STATE_MACHINE: dict[PetState, StateConfig] = {
    PetState.IDLE: StateConfig(
        next_states=[
            (PetState.IDLE, 70),           # 70% chance to just stay idle again!
            (PetState.WALKING_LEFT, 5),
            (PetState.WALKING_RIGHT, 5),
            (PetState.WALK_UP, 5),
            (PetState.WALK_DOWN, 5),
            (PetState.DIAG_UP_RIGHT, 5),
            (PetState.DIAG_DOWN_LEFT, 5)
        ],
        min_duration_ms=5000.0,   # Sit still for at least 5 seconds
        max_duration_ms=15000.0,  # Up to 15 seconds of doing nothing
    ),
    PetState.WALKING_LEFT: StateConfig(
        next_states=[(PetState.IDLE, 85), (PetState.WALK_UP, 15)], # Almost always stop walking
        min_duration_ms=1500.0, max_duration_ms=3000.0, speed_x=-60.0, # Shorter walks
    ),
    PetState.WALKING_RIGHT: StateConfig(
        next_states=[(PetState.IDLE, 85), (PetState.WALK_DOWN, 15)],
        min_duration_ms=1500.0, max_duration_ms=3000.0, speed_x=60.0,
    ),
    PetState.WALK_UP: StateConfig(
        next_states=[(PetState.IDLE, 85), (PetState.WALKING_LEFT, 15)],
        min_duration_ms=1500.0, max_duration_ms=3000.0, speed_y=-50.0,
    ),
    PetState.WALK_DOWN: StateConfig(
        next_states=[(PetState.IDLE, 85), (PetState.WALKING_RIGHT, 15)],
        min_duration_ms=1500.0, max_duration_ms=3000.0, speed_y=50.0,
    ),
    PetState.DIAG_UP_RIGHT: StateConfig(
        next_states=[(PetState.IDLE, 90), (PetState.WALKING_RIGHT, 10)],
        min_duration_ms=1000.0, max_duration_ms=2500.0, speed_x=60.0, speed_y=-60.0,
    ),
    PetState.DIAG_DOWN_LEFT: StateConfig(
        next_states=[(PetState.IDLE, 90), (PetState.WALKING_LEFT, 10)],
        min_duration_ms=1000.0, max_duration_ms=2500.0, speed_x=-60.0, speed_y=60.0,
    ),
    PetState.FLEEING_LEFT: StateConfig(
        next_states=[(PetState.IDLE, 100)], # Stop and catch its breath after running
        min_duration_ms=1500.0, max_duration_ms=2000.0, speed_x=-180.0, speed_y=-100.0,
    ),
    PetState.FLEEING_RIGHT: StateConfig(
        next_states=[(PetState.IDLE, 100)], # Stop and catch its breath after running
        min_duration_ms=1500.0, max_duration_ms=2000.0, speed_x=180.0, speed_y=-100.0,
    ),
}

class Pet:
    def __init__(self, start_x: float, start_y: float) -> None:
        self.x = start_x
        self.y = start_y
        self.min_x = 0.0
        self.max_x = 1920.0
        self.min_y = 0.0    
        self.max_y = 1080.0 
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.state = PetState.IDLE
        self._state_timer_ms = 0.0
        self.enter_state(PetState.IDLE)

    def set_boundaries(self, min_x: float, max_x: float, min_y: float, max_y: float) -> None:
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def enter_state(self, new_state: PetState) -> None:
        self.state = new_state
        config = STATE_MACHINE[self.state]
        self._state_timer_ms = random.uniform(config.min_duration_ms, config.max_duration_ms)

        # Apply chaotic fleeing speeds based on direction
        if self.state == PetState.FLEEING_LEFT:
            self.speed_x = config.speed_x
            self.speed_y = random.choice([-150.0, 150.0])
        elif self.state == PetState.FLEEING_RIGHT:
            self.speed_x = config.speed_x
            self.speed_y = random.choice([-150.0, 150.0])
        else:
            self.speed_x = config.speed_x
            self.speed_y = getattr(config, 'speed_y', 0.0)

    def _pick_next_state(self) -> None:
        config = STATE_MACHINE[self.state]
        states, weights = zip(*config.next_states)
        next_state = random.choices(states, weights=weights, k=1)[0]
        self.enter_state(next_state)

    def tick(self, delta_ms: float) -> None:
        self._state_timer_ms -= delta_ms

        if self._state_timer_ms <= 0:
            self._pick_next_state()

        if self.speed_x != 0:
            self.x += self.speed_x * (delta_ms / 1000.0)
        if self.speed_y != 0:
            self.y += self.speed_y * (delta_ms / 1000.0)

        if self.x <= self.min_x:
            self.x = self.min_x
            self.enter_state(PetState.WALKING_RIGHT)
        elif self.x >= self.max_x:
            self.x = self.max_x
            self.enter_state(PetState.WALKING_LEFT)

        if self.y <= self.min_y:
            self.y = self.min_y
            self.enter_state(PetState.WALK_DOWN)
        elif self.y >= self.max_y:
            self.y = self.max_y
            self.enter_state(PetState.WALK_UP)