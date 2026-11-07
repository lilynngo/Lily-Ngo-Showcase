extends Node2D

class_name GossiperManager

var gossipers_available: Dictionary[int, CharacterController]
var current_hovering: bool = false
var hovered_character: CharacterController = null
@export var day_positions: Node2D

signal character_clicked(character_name)

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	gather_gossipers()
	get_positions_for_gossipers()
	self.hide()

func get_positions_for_gossipers():
	var current_day=0
	for day_node in day_positions.get_children():
		current_day += 1
		var current_character_index = 0
		for character_marker in day_node.get_children():
			if character_marker is Marker2D:
				var character_name = character_marker.name
				var chara_enum = Enums.Characters.get(character_name.to_snake_case().to_upper())
				var chara_controller = gossipers_available.get(chara_enum) as CharacterController
				chara_controller.set_position_data(current_day, character_marker, current_character_index)
				current_character_index += 1

func reset_node():
	for gossiper in gossipers_available.keys():
		gossipers_available[gossiper].reset_character()
	gather_gossipers()
	load_gossipers()
	
func gather_gossipers():
	for child in get_children():
		if child is CharacterController:
			gossipers_available[child.character_name] = child

func is_mouse_over_ui() -> bool:
	var hovered_control = get_viewport().gui_get_hovered_control()

	if hovered_control == null:
		return false

	return hovered_control.mouse_filter != Control.MOUSE_FILTER_IGNORE
	
func _process(_delta: float):

	var next_hovered: Node2D = null
	# find character currently hovering
	if not is_mouse_over_ui():
		for character in gossipers_available.keys():	
			var character_node = gossipers_available[character]
			if character_node.is_mouse_over():
				next_hovered = character_node
				
	if next_hovered == hovered_character:
		return
	if next_hovered == null:
		Input.set_default_cursor_shape(Input.CURSOR_ARROW)
	
	# remove glow from the previous character.
	if is_instance_valid(hovered_character):
		hovered_character.set_glow(false)
		hovered_character.currently_hovering = false

	hovered_character = next_hovered

	# apply glow to current character
	if is_instance_valid(hovered_character):
		Input.set_default_cursor_shape(Input.CURSOR_POINTING_HAND)
		hovered_character.set_glow(true)
		hovered_character.currently_hovering = true
		hovered_character.mouse_hovering.emit(
			hovered_character.character_name
		)
		
func _unhandled_input(event: InputEvent):
	#captures all mouse events not processed by other control nodes
	if event is InputEventMouseButton:
		if event.button_index != MOUSE_BUTTON_LEFT:
			return

		if not event.pressed:
			return

		# Recheck on click to avoid stale hover state.
		var character = get_topmost_hovered_character()

		if character == null:
			return

		if GameState.has_actions_left():
			emit_character_selection(character)

		get_viewport().set_input_as_handled()

func get_topmost_hovered_character() -> CharacterController:
	# only apply clicks on the top most hovered chara

	var hovered: CharacterController = null

	for child in get_current_day_gossipers().keys():
		var character = gossipers_available[child]
		if not character.is_mouse_over():
			continue

		if hovered == null or character.z_index >= hovered.z_index:
			hovered = character

	return hovered

func get_current_day_gossipers():
	var gossipers_to_display = {}
	if gossipers_available.size() == 0 or gossipers_available == null:
		gather_gossipers()
	var current_gossipers = GameState.get_gossipers()
	for gossiper in current_gossipers:
		var character_name = gossiper.get_character_name()
		var character_node = gossipers_available[character_name]
		gossipers_to_display[character_name] = character_node
	return gossipers_to_display
	
func get_selected_gossiper(character:CharacterController) -> Gossiper:
	var current_gossipers = GameState.get_gossipers()
	for gossiper in current_gossipers:
		var character_name = gossiper.get_character_name()
		var character_node = gossipers_available[character_name]
		if character_node == character:
			return gossiper
	return null

func hide_non_speakers() -> void:
	for idx in get_current_day_gossipers().keys():
		var gossiper = gossipers_available[idx]
		if not gossiper.in_convo:
			gossiper.hide()

func update_character_affinity(chara_name:Enums.Characters, current_score:int):
	var character_to_change = gossipers_available[chara_name] 
	character_to_change.update_affinity(current_score)

func show_hidden_gossipers_available() -> void:
	for idx in get_current_day_gossipers().keys():
		var gossiper = gossipers_available[idx]
		gossiper.show()

## Handler for when character is clicked on
func emit_character_selection(character:CharacterController):
	var character_name = character.get_character_name()
	GameState.log_gossiper_chat(character)
	GameState.track_event("selectCharacter", character_name)
	character.in_convo = true
	hide_non_speakers()
	await character.move_sprite()
	character_clicked.emit(character)

## Handler for when a character is finished with dialogue
func _on_dialogue_controller_dialogue_interaction_complete(character: CharacterController) -> void:
	character.in_convo = false
	character.spoken_to = true
	character.move_sprite()
	character.set_desaturation(true, true)
	show_hidden_gossipers_available()
	var gossiper = get_selected_gossiper(character)
	UIManager.record_clue(gossiper)
	GameState.action_used()

func load_gossipers():
	var current_gossipers = get_current_day_gossipers()
	for gossiper in gossipers_available.keys():
		if gossiper in current_gossipers.keys():
			var gossiper_to_load= gossipers_available[gossiper]
			if GameState.has_actions_left():
				var has_spoken_to = GameState.has_spoken_to(gossiper_to_load)
				if has_spoken_to:
					gossiper_to_load.set_active(false)
				else:
					gossiper_to_load.set_active(true)
			else:
				gossiper_to_load.set_active(false)
					
			gossiper_to_load.change_expression_by_affinity()
			gossiper_to_load.show()
		else:
			var gossiper_to_load= gossipers_available[gossiper]
			gossiper_to_load.hide()
