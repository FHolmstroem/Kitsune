"""
Sprite loading and frame cycling.

Handles loading sprite sheets from assets/sprites/, splitting them
into individual frames, and cycling through them at a given FPS.

Each animation (walk_left, walk_right, idle, sleep, etc.) is a
named sequence of frames. The AnimationController keeps track of
which animation is playing and which frame we're on.
"""
