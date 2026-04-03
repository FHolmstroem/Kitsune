"""Tests for pet.py state machine."""

from pet import Pet, PetState, STATE_MACHINE


def test_pet_initialization():
    """Pet should start at the given coordinates in the IDLE state."""
    pet = Pet(start_x=100.0, start_y=500.0)
    assert pet.x == 100.0
    assert pet.y == 500.0
    assert pet.state == PetState.IDLE
    assert pet._state_timer_ms > 0

def test_pet_movement():
    """Pet should update its X coordinate based on state speed and delta_ms."""
    pet = Pet(start_x=100.0, start_y=500.0)
    
    # Force state to walking right
    pet.enter_state(PetState.WALKING_RIGHT)
    speed = STATE_MACHINE[PetState.WALKING_RIGHT].speed_x
    
    # Tick for 1000ms (1 second). It should move exactly `speed` pixels.
    pet.tick(1000.0)
    assert pet.x == 100.0 + speed

def test_state_transition_on_timer():
    """Pet should pick a new state when the timer drops below zero."""
    pet = Pet(start_x=100.0, start_y=500.0)
    
    # Fast-forward the timer to 0
    pet._state_timer_ms = 0.0
    
    # Tick with a tiny delta. This should trigger _pick_next_state()
    pet.tick(16.0)
    
    # Timer should be reset to a new positive value
    assert pet._state_timer_ms > 0

def test_boundary_collision_left():
    """Hitting the left boundary should force the pet to walk right."""
    pet = Pet(start_x=10.0, start_y=500.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    
    pet.enter_state(PetState.WALKING_LEFT)
    
    # Tick 1 second (1000ms). At 60px/s, this attempts to move 60 pixels left.
    # It will hit the wall at 0.0 well before the state timer expires.
    pet.tick(1000.0)
    
    assert pet.x == 0.0
    assert pet.state == PetState.WALKING_RIGHT

def test_boundary_collision_right():
    """Hitting the right boundary should force the pet to walk left."""
    pet = Pet(start_x=990.0, start_y=500.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    
    pet.enter_state(PetState.WALKING_RIGHT)
    
    # Tick 1 second. Attempts to move 60 pixels right, hitting the 1000.0 wall.
    pet.tick(1000.0)
    
    assert pet.x == 1000.0
    assert pet.state == PetState.WALKING_LEFT


def test_laser_mode_idle():
    """Fox should idle if the cursor is very close."""
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(110.0, 110.0)  # Distance ~14, less than 30 threshold
    pet.tick(16.0)
    
    assert pet.state == PetState.IDLE
    assert pet.speed_x == 0.0
    assert pet.speed_y == 0.0

def test_laser_mode_walk():
    """Fox should walk towards the cursor if it's moderately far away."""
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(200.0, 100.0)  # Distance 100 (walk threshold is < 200)
    pet.tick(16.0)
    
    assert pet.state == PetState.WALKING_RIGHT
    assert pet.speed_x > 0.0
    assert pet.speed_y == 0.0  # Directly to the right

def test_laser_mode_run():
    """Fox should run (flee state visually) towards the cursor if it's far away."""
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(500.0, 100.0)  # Distance 400 (run threshold is >= 200)
    pet.tick(16.0)
    
    assert pet.state == PetState.FLEEING_RIGHT
    assert pet.speed_x == 180.0  # Flee base speed