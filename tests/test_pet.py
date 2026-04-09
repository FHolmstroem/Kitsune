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

def test_pet_default_boundaries():
    """Default boundaries should be sensible defaults."""
    pet = Pet(start_x=100.0, start_y=100.0)
    assert pet.min_x == 0.0
    assert pet.min_y == 0.0

def test_laser_mode_diagonal():
    """Laser should account for both x and y distance."""
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(120.0, 125.0)  # hypot(20,25)≈32 → walk. hypot(20)=20 → idle
    pet.tick(16.0)
    
    assert pet.state != PetState.IDLE
    assert pet.speed_y > 0.0

def test_init_default_boundaries():
    pet = Pet(start_x=100.0, start_y=100.0)
    assert pet.max_x == 1920.0
    assert pet.max_y == 1080.0

def test_init_speeds_zero():
    pet = Pet(start_x=100.0, start_y=100.0)
    assert pet.speed_x == 0.0
    assert pet.speed_y == 0.0
    assert type(pet.speed_x) is float
    assert type(pet.speed_y) is float

def test_init_state_is_idle():
    pet = Pet(start_x=100.0, start_y=100.0)
    assert pet.state == PetState.IDLE
    assert pet.state is not None

def test_init_timer_is_float():
    pet = Pet(start_x=100.0, start_y=100.0)
    assert isinstance(pet._state_timer_ms, float)
    assert pet._state_timer_ms > 0

def test_init_laser_defaults():
    pet = Pet(start_x=100.0, start_y=100.0)
    assert pet.is_laser_active is False
    assert pet.target_x == 0.0
    assert pet.target_y == 0.0
    assert type(pet.target_x) is float
    assert type(pet.target_y) is float

def test_fleeing_left_sets_speed():
    pet = Pet(start_x=500.0, start_y=500.0)
    pet.enter_state(PetState.FLEEING_LEFT)
    config = STATE_MACHINE[PetState.FLEEING_LEFT]
    assert pet.speed_x == config.speed_x
    assert pet.speed_y in (-150.0, 150.0)

def test_fleeing_right_sets_speed():
    pet = Pet(start_x=500.0, start_y=500.0)
    pet.enter_state(PetState.FLEEING_RIGHT)
    config = STATE_MACHINE[PetState.FLEEING_RIGHT]
    assert pet.speed_x == config.speed_x
    assert pet.speed_y in (-150.0, 150.0)

def test_enter_state_else_branch_speed_y():
    pet = Pet(start_x=500.0, start_y=500.0)
    pet.enter_state(PetState.WALKING_RIGHT)
    config = STATE_MACHINE[PetState.WALKING_RIGHT]
    expected = getattr(config, 'speed_y', 0.0)
    assert pet.speed_y == expected

def test_pick_next_state_weighted(monkeypatch):
    """Weights should matter in state transitions."""
    import random as rand_mod
    pet = Pet(start_x=500.0, start_y=500.0)
    pet.enter_state(PetState.IDLE)
    
    calls = []
    orig = rand_mod.choices
    def spy_choices(*args, **kwargs):
        calls.append(kwargs)
        return orig(*args, **kwargs)
    monkeypatch.setattr(rand_mod, 'choices', spy_choices)
    
    pet._pick_next_state()
    assert 'weights' in calls[0] and calls[0]['weights'] is not None
    assert calls[0].get('k') == 1

def test_timer_decrements():
    pet = Pet(start_x=500.0, start_y=500.0)
    pet.enter_state(PetState.IDLE)
    initial = pet._state_timer_ms
    pet.tick(100.0)
    assert pet._state_timer_ms == initial - 100.0

def test_timer_exactly_zero_triggers_transition():
    pet = Pet(start_x=500.0, start_y=500.0)
    pet.enter_state(PetState.IDLE)
    pet._state_timer_ms = 16.0
    old_state_timer = pet._state_timer_ms
    pet.tick(16.0)
    # Timer was exactly 0 after subtraction, should have transitioned
    assert pet._state_timer_ms > 0  # reset by new state

def test_movement_guard_zero():
    """Movement should only happen when speed != 0."""
    pet = Pet(start_x=500.0, start_y=500.0)
    pet.speed_x = 0
    pet.speed_y = 0
    pet._state_timer_ms = 99999.0
    pet.tick(1000.0)
    assert pet.x == 500.0
    assert pet.y == 500.0

def test_y_movement_applies():
    pet = Pet(start_x=500.0, start_y=500.0)
    pet._state_timer_ms = 99999.0
    pet.speed_x = 0.0
    pet.speed_y = 100.0
    pet.tick(1000.0)
    assert pet.y == 600.0

def test_x_movement_division():
    """Verify speed * (delta_ms / 1000) not speed / (delta_ms / 1000)."""
    pet = Pet(start_x=0.0, start_y=500.0)
    pet.set_boundaries(min_x=-9999.0, max_x=9999.0, min_y=0.0, max_y=1000.0)
    pet._state_timer_ms = 99999.0
    pet.speed_x = 60.0
    pet.tick(500.0)
    assert pet.x == 30.0  # 60 * 0.5

def test_y_movement_division():
    pet = Pet(start_x=500.0, start_y=0.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=-9999.0, max_y=9999.0)
    pet._state_timer_ms = 99999.0
    pet.speed_y = 60.0
    pet.tick(500.0)
    assert pet.y == 30.0

def test_boundary_x_left_exact():
    """Pet at exactly min_x should be clamped."""
    pet = Pet(start_x=0.0, start_y=500.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    pet.speed_x = -10.0
    pet._state_timer_ms = 99999.0
    pet.tick(0.001)  # tiny tick, x goes slightly negative
    assert pet.x == 0.0
    assert pet.state == PetState.WALKING_RIGHT

def test_boundary_x_right_exact():
    pet = Pet(start_x=1000.0, start_y=500.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    pet.speed_x = 10.0
    pet._state_timer_ms = 99999.0
    pet.tick(0.001)
    assert pet.x == 1000.0
    assert pet.state == PetState.WALKING_LEFT

def test_boundary_y_top():
    pet = Pet(start_x=500.0, start_y=5.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    pet.speed_y = -100.0
    pet._state_timer_ms = 99999.0
    pet.tick(1000.0)
    assert pet.y == 0.0
    assert pet.state == PetState.WALK_DOWN

def test_boundary_y_bottom():
    pet = Pet(start_x=500.0, start_y=995.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    pet.speed_y = 100.0
    pet._state_timer_ms = 99999.0
    pet.tick(1000.0)
    assert pet.y == 1000.0
    assert pet.state == PetState.WALK_UP

def test_boundary_y_top_laser_no_state_change():
    pet = Pet(start_x=500.0, start_y=5.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    pet.is_laser_active = True
    pet.update_laser_target(500.0, -100.0)
    pet.tick(1000.0)
    assert pet.y == 0.0
    assert pet.state != PetState.WALK_DOWN

def test_boundary_y_bottom_laser_no_state_change():
    pet = Pet(start_x=500.0, start_y=995.0)
    pet.set_boundaries(min_x=0.0, max_x=1000.0, min_y=0.0, max_y=1000.0)
    pet.is_laser_active = True
    pet.update_laser_target(500.0, 2000.0)
    pet.tick(1000.0)
    assert pet.y == 1000.0
    assert pet.state != PetState.WALK_UP

def test_laser_walk_speed_y_calculated():
    """Laser walk speed_y should use (dy/dist)*base_speed."""
    import math
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(100.0, 200.0)  # dist=100, pure vertical
    pet.tick(16.0)
    # base_speed=60 for walk, dy/dist=1.0, so speed_y=60
    assert abs(pet.speed_y - 60.0) < 1.0

def test_laser_run_left():
    pet = Pet(start_x=500.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(100.0, 100.0)  # dist=400, dx<0
    pet.tick(16.0)
    assert pet.state == PetState.FLEEING_LEFT

def test_laser_walk_left():
    pet = Pet(start_x=200.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(100.0, 100.0)  # dist=100, dx<0
    pet.tick(16.0)
    assert pet.state == PetState.WALKING_LEFT

def test_laser_exact_200_is_running():
    """dist==200 should count as running (>=200)."""
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(300.0, 100.0)  # dist=200 exactly
    pet.tick(16.0)
    assert pet.state == PetState.FLEEING_RIGHT
    assert abs(pet.speed_x) == 180.0

def test_laser_idle_at_29():
    """dist<30 should idle."""
    import math
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(120.0, 121.0)  # hypot(20,21)≈29
    pet.tick(16.0)
    assert pet.state == PetState.IDLE

def test_laser_not_idle_at_30():
    """dist==30 should NOT idle (< 30, not <=)."""
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(130.0, 100.0)  # dist=30 exactly
    pet.tick(16.0)
    assert pet.state != PetState.IDLE

def test_laser_dx_zero_walk():
    """When dx==0, should go left (else branch of dx > 0)."""
    pet = Pet(start_x=100.0, start_y=100.0)
    pet.is_laser_active = True
    pet.update_laser_target(100.0, 150.0)  # dx=0, dist=50
    pet.tick(16.0)
    assert pet.state == PetState.WALKING_LEFT  # dx=0, not > 0

def test_laser_walk_base_speed_60():
    """Walk base speed should be 60, not 61."""
    import math
    pet = Pet(start_x=0.0, start_y=0.0)
    pet.set_boundaries(min_x=-9999.0, max_x=9999.0, min_y=-9999.0, max_y=9999.0)
    pet.is_laser_active = True
    pet.update_laser_target(100.0, 0.0)  # dist=100, pure x
    pet.tick(16.0)
    assert pet.speed_x == 60.0