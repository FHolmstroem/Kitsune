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
