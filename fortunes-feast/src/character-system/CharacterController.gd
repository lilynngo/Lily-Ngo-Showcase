extends Node2D
class_name CharacterController


@export_group("Dialogue")
@export var dialogue_resource: DialogueResource
var in_convo: bool = false
var spoken_to: bool = false

@export_group("Body Parts")
@export var eyes: Polygon2D
@export var mouth: Polygon2D 
@export var brow: Polygon2D
@export var effects: CanvasGroup
@export var visual_node: Node2D
@export var face_marker: Marker2D
@export var feet_marker: Marker2D
@export var center_marker: Marker2D
@export var collision_area: Area2D
@export var collision_polygon_2d: CollisionPolygon2D 

@export_group("Defaults")
@export var character_name: Enums.Characters
@export var default_expression: Enums.CharacterExpressions
var current_expression: Enums.CharacterExpressions
@export var should_animate:bool = true
@export var glow_enabled_on_start: bool = false
@export var glow_radius_default: float = 22.00
@export var glow_strength_default: float = 7.0
@export var glow_softness_default: float = 0.8
var glow_tween: Tween
var is_glowing:bool = false
@export var active_on_start: bool = true
@export var desat_default: float = 0.8
@export var brightness_default: float = 0.8
var desat_tween: Tween
var is_active:bool = true
@export var fliph_on_start: bool = false
var rest_position: Vector2
var rest_scale: Vector2
@export var hop_height: float = 8.0
@export var hop_duration: float = 0.3
var hop_tween: Tween
@export var can_animate:bool = false

@export_group("Blink Settings")
@onready var blinking_animation_player: AnimationPlayer = $BlinkingAnimationPlayer
@export var min_blink_interval: float = 3.0
@export var max_blink_interval: float = 7.0
@export var blink_timer: Timer
var is_blinking:bool = false

@export_group("Animation Settings")
@export var idle_animation_player: AnimationPlayer
var currently_hovering : bool = false

@export_group("Thumbnail Settings")
@export var portait_frame: ColorRect 
@export var thumbnail_texture: Texture2D

@export_group("Character Settings")
@export var affinity_total:int 
@export var affinity_by_day: Dictionary[int, int]

signal mouse_hovering(character_name)

#@export_group("Scene Settings")
var day_markers: Dictionary[int, Dictionary] = {} #Automatically done and set up via Gossipers Manager

func update_affinity(new_score:int):
	var current_day = GameState.get_day()
	affinity_by_day[current_day] = new_score
	affinity_total += new_score

const ANGRY_THRESHOLD = -10
const SAD_THRESHOLD = -3
const NEUTRAL_THRESHOLD = 10
const HAPPY_THRESHOLD = 20

func change_expression_by_affinity():
	pass
	# Base on affinity, the expression can change from neutral to happy to sad / angry
	# TODO: Update the thresholds: currently -2 to 31 
	if affinity_total < ANGRY_THRESHOLD:
		set_expression(Enums.CharacterExpressions.ANGRY, false)
	elif affinity_total < SAD_THRESHOLD:
		set_expression(Enums.CharacterExpressions.SAD, false)
	elif affinity_total < NEUTRAL_THRESHOLD:
		set_expression(Enums.CharacterExpressions.NEUTRAL, false)
	elif affinity_total < HAPPY_THRESHOLD:
		set_expression(Enums.CharacterExpressions.HAPPY, false)

func set_position_data(day: int, marker: Marker2D, z_index:int):
	day_markers[day] = {
		"position_marker":marker, 
		"z_index": z_index 
	}

func _ready():
	portait_frame.hide()
	initiate_values()
	change_expression()
	blink_timer.timeout.connect(_on_blink_timer_timeout)
	schedule_next_blink()
	reset_character()
	GameState.actions_changed.connect(_on_zero_actions)
	set_character_thumbnail()
	
	affinity_by_day = {}
	affinity_total = 0
	disable_control_mouse_input(self)
	visibility_changed.connect(_on_visibility_changed)
	
## This resets the position natively so we don't have to worry about resets etc. 
func _on_visibility_changed() -> void:
	if is_visible_in_tree():
		reset_position()
		
func set_character_thumbnail():
	var chara_name = Enums.Characters.keys()[character_name].to_lower() 
	var thumbnail_path = CharacterAssets.THUMBNAIL_PATH
	var art_character = CharacterAssets.CHARACTERS.get(chara_name, {}).get("psd_file_name", {})
	var image_type = CharacterAssets.CHARACTERS[chara_name]["image_type"]
	var full_path = CharacterAssets.THUMBNAIL_PATH + "thumbnail_" +art_character + "." + image_type
	
	thumbnail_texture = load(full_path) as Texture2D

func disable_control_mouse_input(node: Node):
	if node is Control:
		node.mouse_filter = Control.MOUSE_FILTER_IGNORE

	for child in node.get_children():
		disable_control_mouse_input(child)

func get_character_name() -> String:
	return Enums.Characters.keys()[character_name].to_lower()

func get_face_marker(): 
	return face_marker
func get_feet_marker(): 
	return feet_marker

func initiate_values():
	rest_position = position
	rest_scale = scale
	current_expression = default_expression
	is_glowing = glow_enabled_on_start
	
func reset_values():
	if not is_node_ready():
		return
	current_expression = default_expression
	set_expression(current_expression)
	reset_position()
	reset_glow()
	reset_desaturation()
	flip_character(false)
	idle_animation_player.play()
	in_convo = false
	spoken_to = false
	currently_hovering = false
	
func reset_position():
	var current_day = GameState.get_day()
	var get_position_data = day_markers.get(current_day, null)
	if get_position_data == null:
		position = rest_position
		self.z_index = 0.0
	else:
		var marker_position = get_position_data.get("position_marker").position
		var z_index = get_position_data.get("z_index")
		position = marker_position
		self.z_index = z_index
		rest_position = marker_position
	
	scale = rest_scale
	
func reset_glow():
	set_glow(false, should_animate)

func set_glow(enabled: bool, animated: bool = true, speed:float =  0.18):
	var target = glow_strength_default if enabled else 0.0
	is_glowing = enabled
	if glow_tween and glow_tween.is_running():
		glow_tween.kill()

	if not animated:
		effects.material.set_shader_parameter("glow_strength", target)
		return

	glow_tween = create_tween()
	glow_tween.set_trans(Tween.TRANS_SINE)
	glow_tween.set_ease(Tween.EASE_IN_OUT)

	glow_tween.tween_property(
		effects.material,
		"shader_parameter/glow_strength",
		target,
		speed
	)

func is_mouse_over():
	if not is_visible_in_tree():
		return false
		
	if not is_active:
		return false
		
	if collision_polygon_2d.polygon.size() < 3:
		return false
		
	if in_convo:
		return false
		
	if spoken_to:
		return false
		
	if UIManager.book_visible:
		return false

	var mouse_local = collision_polygon_2d.to_local(
		get_global_mouse_position()
	)

	return Geometry2D.is_point_in_polygon(
		mouse_local,
		collision_polygon_2d.polygon
	)


func reset_desaturation():
	set_desaturation(false, should_animate)

func set_desaturation(enabled: bool, animated: bool = true):
	var target_desat = desat_default if enabled else 0.0
	var target_brightness = brightness_default if enabled else 1.0
	is_active = not(enabled)

	if enabled:
		idle_animation_player.pause()
	else:
		idle_animation_player.play()
		
	if desat_tween and desat_tween.is_running():
		desat_tween.kill()

	if not animated:
		effects.material.set_shader_parameter(
			"desaturation", target_desat
		)
		effects.material.set_shader_parameter(
			"brightness", target_brightness
		)
		return

	desat_tween = create_tween()
	desat_tween.set_parallel(true)
	desat_tween.set_trans(Tween.TRANS_SINE)
	desat_tween.set_ease(Tween.EASE_IN_OUT)

	desat_tween.tween_property(
		effects.material,
		"shader_parameter/desaturation",
		target_desat,
		0.35
	)

	desat_tween.tween_property(
		effects.material,
		"shader_parameter/brightness",
		target_brightness,
		0.35
	)

func flip_character(toggled_on:bool):
	visual_node.scale.x = -abs(visual_node.scale.x) if toggled_on else abs(visual_node.scale.x)

	
func schedule_next_blink():
	var interval = randf_range(
		min_blink_interval,
		max_blink_interval
	)
	blink_timer.start(interval)


func _on_blink_timer_timeout():
	if is_active:
		blinking_animation_player.play("blink")
	schedule_next_blink()

func change_expression():
	if can_animate:
		eyes.texture = _get_texture(character_name, "head", "eyes",current_expression)
		mouth.texture = _get_texture(character_name, "head", "mouth",current_expression)
		brow.texture = _get_texture(character_name, "head", "brows",current_expression)

func _get_texture(character:Enums.Characters, body_section:String, body_part:String, expression:Variant = null) -> Texture2D:
	## example:
	##    character: KING_MARCELLO
	##    body_section: head
	##    body_part: mouth
	##    expression: NEUTRAL
	##    body_part_with_expression: face_mouth_neutral
	##    file_path: res://assets/characters/king_marcello
	##    filename_prefix: art_character_king_marcello
	##    image_type: webp
	##    texture_name: "face_mouth"
	##    full_path: "res://assets/characters/king_marcello/art_character_king_marcello_face_mouth_neutral.webp
	
	var chara_name = Enums.Characters.keys()[character].to_lower() #king_marcello
	var texture_name = CharacterAssets.CHARACTERS.get(chara_name, {}).get(body_section, {}).get(body_part, null)
	var file_path = CharacterAssets.CHARACTERS[chara_name]["base_path"]
	var filename_prefix = CharacterAssets.CHARACTERS[chara_name]["psd_file_name"]
	var image_type = CharacterAssets.CHARACTERS[chara_name]["image_type"]
	
	var full_path = file_path  +"/"+ filename_prefix + "_" + texture_name + "." + image_type
	if expression != null:
		var expression_to_use = Enums.CharacterExpressions.keys()[expression].to_lower()
		var default_expression_to_use = Enums.CharacterExpressions.keys()[Enums.CharacterExpressions.NEUTRAL].to_lower()
		full_path = file_path  +"/"+ filename_prefix + "_" +body_section+"_"+ texture_name + "_"+expression_to_use+ "." + image_type
		if not ResourceLoader.exists(full_path): #if a texture is not available for that expression, use neutral
			full_path = file_path  +"/"+ filename_prefix + "_" +body_section+"_"+ texture_name + "_"+default_expression_to_use+ "." + image_type
	return load(full_path) as Texture2D
		
func restore_eyes():
	is_blinking = false
	var body_part = "eyes"
	if can_animate:
		eyes.texture = _get_texture(character_name, "head", body_part,current_expression)

func close_eyes():
	is_blinking = true
	var body_part = "eyes"
	if can_animate:
		eyes.texture = _get_texture(character_name, "head", body_part,Enums.CharacterExpressions.CLOSED)


func play_expression_hop():
	if hop_tween and hop_tween.is_running():
		hop_tween.kill()
		position = rest_position

	var start_position = position

	hop_tween = create_tween()

	# Gentle upward movement.
	hop_tween.tween_property(
		self,
		"position:y",
		start_position.y - hop_height,
		hop_duration * 0.4
	).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)

	# Smooth, slower return.
	hop_tween.tween_property(
		self,
		"position:y",
		start_position.y,
		hop_duration * 0.6
	).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


## Move the character sprite to the center marker or back to original position
func move_sprite():
	var tween: Tween = create_tween().set_parallel()
	var destination: Vector2
	var scale_amount: Vector2
	
	if position == rest_position:
		destination = center_marker.position
	else:
		destination = rest_position
	if scale == rest_scale:
		scale_amount = Vector2(0.4, 0.4)
	else:
		scale_amount = rest_scale
	
	tween.tween_property(self, "position", destination, 0.5).set_ease(Tween.EASE_OUT_IN)
	tween.tween_property(self, "scale", scale_amount, 0.5).set_ease(Tween.EASE_OUT)

## --------- ##
## INTERFACE ##
## --------- ##

## Enables/disables character interaction and idle animation
func set_active(enabled:bool, animated:bool=true):
	if is_active == enabled:
		return
	set_desaturation(not enabled, animated)
	
## Controls whether character is highlighted/glow
func set_highlighted(enabled:bool, animated: bool = true):
	set_glow(enabled, animated)	

## Switches to designated expression
func set_expression(expression: Enums.CharacterExpressions, animated:bool=true):
	if current_expression != expression:
		current_expression = expression
		if not is_blinking:
			restore_eyes()
		change_expression()
		if animated:
			play_expression_hop()	

## Updates multiple character properties through 1 entry pt
func set_character_state (
	active: Variant = null,
	highlighted: Variant = null, 
	expression: Variant = null, ## must be from Enums.CharacterExpressions
	animated: bool = true
):
	if active != null:
		set_active(active, animated)
	
	if highlighted != null:
		set_highlighted(highlighted, animated)
	
	if expression != null:
		set_expression(expression)

## Sets horizontal facing direction
func set_face_opposite(enabled:bool):
	flip_character(enabled)
	
## Restores the character's default state
func reset_character():
	reset_values()
## Returns the  anchor used for positioning dialogue/UI
func get_marker(options: String):
	if options == "feet":
		return feet_marker
	elif options == "face":
		return face_marker
	

func _on_zero_actions(actions_changed):
	var current_actions = GameState.get_actions()
	if current_actions == 0:
		set_desaturation(true, true)
