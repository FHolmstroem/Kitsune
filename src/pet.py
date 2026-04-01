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
    """String enum mapping directly to animation names."""
    IDLE = "idle"
    WALKING_LEFT = "walk_left"
    WALKING_RIGHT = "walk_right"
    FLEEING = "fleeing"
    # SLEEPING = "sleep"  # We'll add this later!


@dataclass
class StateConfig:
    """Configuration for a specific behavior state."""
    next_states: list[tuple[PetState, int]]  # List of (NextState, Weight)
    min_duration_ms: float
    max_duration_ms: float
    speed_x: float = 0.0  # Pixels per second


# The Fox's Brain: Defines how states flow into each other
STATE_MACHINE: dict[PetState, StateConfig] = {
    PetState.IDLE: StateConfig(
        next_states=[
            (PetState.WALKING_LEFT, 40),
            (PetState.WALKING_RIGHT, 40),
            (PetState.IDLE, 20)
        ],
        min_duration_ms=2000.0,
        max_duration_ms=4000.0,
    ),
    PetState.WALKING_LEFT: StateConfig(
        next_states=[(PetState.IDLE, 80), (PetState.WALKING_RIGHT, 20)],
        min_duration_ms=3000.0,
        max_duration_ms=5000.0,
        speed_x=-60.0,
    ),
    PetState.WALKING_RIGHT: StateConfig(
        next_states=[(PetState.IDLE, 80), (PetState.WALKING_LEFT, 20)],
        min_duration_ms=3000.0,
        max_duration_ms=5000.0,
        speed_x=60.0,
    ),
    PetState.FLEEING: StateConfig(
        next_states=[(PetState.WALKING_LEFT, 50), (PetState.WALKING_RIGHT, 50)],
        min_duration_ms=1500.0,
        max_duration_ms=2500.0,
        speed_x=120.0,  # Double speed!
    ),
}


class Pet:
    """Pure logic representation of the fox."""

    def __init__(self, start_x: float, start_y: float) -> None:
        self.x = start_x
        self.y = start_y
        
        # Safe defaults, will be updated by main.py based on screen size
        self.min_x = 0.0
        self.max_x = 1920.0
        
        self.state = PetState.IDLE
        self._state_timer_ms = 0.0
        
        self.enter_state(PetState.IDLE)

    def set_boundaries(self, min_x: float, max_x: float) -> None:
        """Define the walkable area so the fox doesn't leave the screen."""
        self.min_x = min_x
        self.max_x = max_x

    def enter_state(self, new_state: PetState) -> None:
        """Transition into a new state and roll for its duration."""
        self.state = new_state
        config = STATE_MACHINE[self.state]
        self._state_timer_ms = random.uniform(config.min_duration_ms, config.max_duration_ms)

    def _pick_next_state(self) -> None:
        """Weighted random selection of the next state."""
        config = STATE_MACHINE[self.state]
        states, weights = zip(*config.next_states)
        next_state = random.choices(states, weights=weights, k=1)[0]
        self.enter_state(next_state)

    def tick(self, delta_ms: float) -> None:
        """Update the logic. Called by the main loop every frame."""
        self._state_timer_ms -= delta_ms

        # 1. Change mind if timer runs out
        if self._state_timer_ms <= 0:
            self._pick_next_state()

        # 2. Move based on current state's speed
        config = STATE_MACHINE[self.state]
        if config.speed_x != 0:
            movement = config.speed_x * (delta_ms / 1000.0)
            self.x += movement

            # 3. Boundary checks (Bonk! Turn around)
            if self.x <= self.min_x:
                self.x = self.min_x
                self.enter_state(PetState.WALKING_RIGHT)
            elif self.x >= self.max_x:
                self.x = self.max_x
                self.enter_state(PetState.WALKING_LEFT)