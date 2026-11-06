class_name PlayerEntity extends CharacterBody2D

@onready var gm = $"../Game Manager" as GameManager

var master_planpro = preload("res://Script/Resource/Collectibles/MasterPlanPro.tres")
@onready var point_light_2d = $PointLight2D

## Handlers to manage movement
@onready var input_handler = $InputHandler as InputHandler
@onready var movement_handler = $MovementHandler as MovementHandler
@onready var jump_handler = $JumpHandler as JumpHandler
@onready var state_chart = $StateChart as StateChart
@onready var animation_tree = $AnimationTree as AnimationTree
@onready var minimap = $"../UI/Minimap"
@onready var inventory_button = $"../UI/InventoryButton"

@onready var pd : PlayerData = SessionManager.pd

## STARTING MARKERS

@onready var luca_spawn = $"../luca_spawn"
@onready var luca_spawn_post_tutorial = $"../luca_spawn_post_tutorial"

@onready var luca_end_cutscene_spawn = $"../luca_end_cutscene_spawn"
@onready var luca_start_cutscene_spawn = $"../luca_start_cutscene_spawn"

## Marks spawn point for jump dust effect
@onready var jump_dust_marker = $JumpDustMarker
@onready var jump_dust = preload("res://Scenes/Dust/jump_dust.tscn")

## Marks spawn point for landed dust effect
@onready var landed_dust_marker = $LandedDustMarker
@onready var landed_dust = preload("res://Scenes/Dust/landed_dust.tscn")

## Marks spawn point for run dust effect when moving right
@onready var right_run_dust_marker = $RightRunDustMarker
## Marks spawn point for run dust effect when moving left
@onready var left_run_dust_marker = $LeftRunDustMarker
@onready var run_dust = preload("res://Scenes/Dust/run_dust.tscn")

## Player Nodes
@onready var luca = $"."

## TRACKS CLOSEST OBJECTS
var current_fall_through_platform: FallThroughPlatform
var nearest_gift_box: Gift_Box
var nearest_lucub: Lucub_Controller
var nearest_signpost: Signpost
var nearest_interactable: Lucub_Interactive

## MOVEMENT VARIABLES
var movement_speed: float
var current_speed:float
var current_direction: float = 1.0
var can_move: bool
var cutscene_end_pos
var current_delta_elapsed = 0.0
var cutscene_value
var cutscene_timer_start
var time_in_air = 0.0
## SIGNALS
signal collected_item (item_to_unlock)
signal start_ending
func _ready():
	time_in_air = 0.0
	cutscene_end_pos = null
	can_move = true

	movement_speed = pd.movement_speed
	current_speed = pd.movement_speed
	scale = Vector2(GC.PLAYER_SCALE, GC.PLAYER_SCALE)
	#HACK: when publishing uncomment this to reset position
	load_data()

func start_beginning_cutscene():
	cutscene_value = "Beginning"
	global_position = luca_start_cutscene_spawn.global_position
	can_move = false
	cutscene_timer_start = 0.0
	animation_tree["parameters/Run/blend_position"] = signf(0.5)
	cutscene_end_pos = luca_spawn
	gm.turn_on_cinematic()
	pass
func start_ending_cutscene():
	cutscene_value = "Ending"
	can_move = false
	cutscene_timer_start = 0.0
	animation_tree["parameters/Run/blend_position"] = signf(0.5)
	cutscene_end_pos = luca_end_cutscene_spawn
	start_ending.emit()
	gm.start_ending_scene()

	pass

func load_data():
	if SessionManager.game_mode == GC.GameModes.EXPLORATION:
		cutscene_value = null
	elif pd.position == Vector2.ZERO:
		#start_beginning_cutscene()
		global_position = luca_spawn.global_position
		cutscene_value = "Beginning"
		can_move = true
	else:
		global_position = pd.position

signal is_underground
signal is_aboveground
func _process(delta):
	if global_position.y >= 30:
		point_light_2d.show()
		is_underground.emit()
	else:
		is_aboveground.emit()
		point_light_2d.hide()

	if cutscene_value == "Beginning":
		collected_item.emit(master_planpro)
		can_move = true
		gm.player_starting_cutscene()
		gm.show_book()
		cutscene_value = null

	if cutscene_end_pos != null && global_position.x >= cutscene_end_pos.global_position.x:
		if cutscene_value == "Ending":
			state_chart.send_event("idle")
			cutscene_end_pos = null
			gm.player_ending_cutscene()
	if can_move:
		handle_pausing()

		handle_toggle_map()

		var direction = handle_horizontal_movement(delta)

		handle_fall_through_platforms()

		handle_early_jump_release()

		move_and_slide()

		handle_gravity(delta)

		handle_animation_movement(direction)

		handle_open_box()

		handle_catch_lucub()

		handle_signpost()

		handle_interactive()

		handle_image()

	elif !can_move && cutscene_end_pos != null: #is during a cutscene
		if cutscene_timer_start <= 0.25:
			cutscene_timer_start += delta
		else:
			if scale.x <= 1.25:
				scale = Vector2 (scale.x + delta, scale.y + delta)
				global_position.y += 5
			state_chart.send_event("moving")
			movement_handler.handle_movement(self, 0.5, delta, current_speed)
			move_and_slide()
			handle_gravity(delta)
	pd.position = global_position

func reset():
	state_chart.send_event("reset")

func unpause():
	inventory_button._close_inventory()

func pause():
	inventory_button._open_inventory()

func handle_pausing():
	if input_handler.get_input_pause():
		if SessionManager.isPaused && !SessionManager.CutsceneInProgress: ## Only unpause if not during a cutscene
			unpause()
		elif !SessionManager.isPaused:
			pause()

	if SessionManager.isPaused: ## Stops horizontal movement when paused
		velocity.x = 0

func handle_toggle_map():
	if input_handler.get_input_toggle_map() && minimap.visible:
		minimap.toggle_map()

func handle_horizontal_movement(delta):
	var direction = input_handler.get_input_left_right()
	if direction:
		movement_handler.handle_movement(self, direction, delta, current_speed)
		current_direction = direction
	else:
		movement_handler.handle_movement(self, 0, delta, current_speed)
	return direction

func handle_gravity(delta):
	if is_on_floor():
		time_in_air = 0.0
		current_speed = pd.movement_speed
		velocity.y = 0
		state_chart.send_event("grounded")
	else:
		time_in_air += delta
		gm.apply_gravity(self, delta, pd.gravity)
		state_chart.send_event("airborne")


func on_jump_enabled_state_physics_processing(_delta):
	if input_handler.get_input_jump() && can_move:
		current_speed = pd.movement_speed/pd.jump_decelarator
		state_chart.send_event("airborne")
		state_chart.send_event("jump")
		SessionManager.play_jump_sound()
		jump_handler.handle_jump(self)

func handle_early_jump_release():
	if Input.is_action_just_released("move_up") && velocity.y < pd.min_jump_speed:
		self.velocity.y = pd.min_jump_speed

func handle_animation_movement(direction):
	if direction:
		state_chart.send_event("moving")
	else:
		if velocity.length_squared() <= 0.005:
			state_chart.send_event("idle")

	animation_tree["parameters/Run/blend_position"] = signf(current_direction)
	animation_tree["parameters/Jump/blend_position"] = signf(current_direction)
	animation_tree["parameters/In Air (Short)/blend_position"] = signf(current_direction)
	animation_tree["parameters/In Air (Long)/blend_position"] = signf(current_direction)
	animation_tree["parameters/Landed/blend_position"] = signf(current_direction)

func handle_fall_through_platforms():
	if input_handler.get_input_down() && is_instance_valid(current_fall_through_platform) && velocity.y == 0:
		current_fall_through_platform.control_collision_way(false)
		global_position.y += 1
		current_fall_through_platform.control_collision_way(true)
		current_fall_through_platform = null

func handle_open_box():
	if is_on_floor():
		if is_instance_valid(nearest_gift_box) && input_handler.get_input_interact():
			global_position = nearest_gift_box.global_position
			SessionManager.pause_game(true, false)
			state_chart.send_event("open_box")
			nearest_gift_box.interact()
			collected_item.emit(nearest_gift_box.item_to_unlock)

func handle_catch_lucub():
	if is_on_floor():
		if is_instance_valid(nearest_lucub) && input_handler.get_input_interact():
			SessionManager.pause_game(true, false)
			state_chart.send_event("catch_lucub")
			nearest_lucub._on_capture()
			pass

func handle_signpost():
	if is_on_floor():
		if is_instance_valid(nearest_signpost) && input_handler.get_input_interact():
			SessionManager.pause_game(true, false)
			nearest_signpost.interact()

func handle_interactive():
	if is_on_floor():
		if is_instance_valid(nearest_interactable) && input_handler.get_input_interact():
			SessionManager.pause_game(true, false)
			nearest_interactable.interact()
func handle_image():
	if is_on_floor():
		if is_instance_valid(nearest_image) && input_handler.get_input_interact():
			SessionManager.pause_game(true, false)
			nearest_image.interact()

var nearest_image: Image_Highlight
func set_nearest_image(img):
	nearest_image = img
func set_reset_image():
	nearest_image = null
func set_nearest_interactable(interactive):
	nearest_interactable = interactive

func set_nearest_lucub(lucub_closest):
	nearest_lucub = lucub_closest

func set_reset_lucub():
	nearest_lucub = null

func set_nearest_signpost(signpost_closest):
	nearest_signpost = signpost_closest

func set_reset_signpost():
	nearest_signpost = null
func set_reset_interactive():
	nearest_interactable = null
func reveal_item():
	nearest_gift_box.reveal_item()

func set_nearest_gift_box(giftbox):
	nearest_gift_box = giftbox

func set_reset_gift():
	nearest_gift_box = null

func set_nearest_platform(platform):
	current_fall_through_platform = platform as FallThroughPlatform


func _on_landed_state_entered():
	var instance = landed_dust.instantiate()
	instance.global_position = jump_dust_marker.global_position
	get_parent().add_child(instance)
	if time_in_air >= 1.0:
		SessionManager.play_oof_sound()
	time_in_air = 0.0


func _on_jump_state_entered():
	var instance = jump_dust.instantiate()
	instance.global_position = jump_dust_marker.global_position
	get_parent().add_child(instance)


func _on_run_state_processing(delta):
	current_delta_elapsed += delta
	if current_direction == 0 || current_delta_elapsed <= 0.2:
		return
	var instance = run_dust.instantiate()
	if current_direction > 0:
		instance.global_position = right_run_dust_marker.global_position
		instance.scale.x = 1
	elif current_direction < 0:
		instance.global_position = left_run_dust_marker.global_position
		instance.scale.x = -1
	get_parent().add_child(instance)
	current_delta_elapsed = 0.0

func _on_maincastle_room_body_entered(body):
	if body.is_in_group("Player"):
		start_ending_cutscene()

func _on_maincastle_entrance_body_entered(body):
	if body.is_in_group("Player"):
		var result = gm.check_for_final_door()
		if result:
			$"../Game Manager/OpenDoor".queue_free()


func _on_run_state_entered():
	SessionManager.play_running_sound()

func _on_run_state_exited():
	SessionManager.stop_running_sound()
