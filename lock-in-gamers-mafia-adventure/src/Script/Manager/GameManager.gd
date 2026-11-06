class_name GameManager extends Node

@onready var game_instance = $".."
var lucub_diag = preload("res://Script/Lucub_Dialogue.dialogue")
var main_diag = preload("res://Script/MainDialogue.dialogue")
var sign_diag = preload("res://Script/Sign_Dialogue.dialogue")
var box_diag = preload("res://Script/Box_Dialogue.dialogue")
var door_diag = preload("res://Script/Door_Dialogue.dialogue")
var current_gift_node
var current_door
var number_of_lucubs_caught = 0.0

var ending_announcement = 0
var last_dialogue = false

@onready var pd: PlayerData = SessionManager.pd
@onready var cam_controller = $"../Camera_Controller"
@onready var main_map = $"../MainMap"
@onready var luca = $"../Luca"
@onready var minimap = $"../UI/Minimap"
@onready var inventory_button = $"../UI/InventoryButton"
@onready var ui = $"../UI"
@onready var main_castle_veil_door = get_node_or_null("../Doors/MainCastleVeil_Door")

@onready var catch_lucub_cutscene = get_node_or_null("../UI/Catch Lucub Cutscene")

## MANAGERS
@onready var box_spawner = get_node_or_null("../BoxSpawner")
@onready var lucubs = get_node_or_null("../Lucubs")

signal catch_cutscene_finished
signal dialogue_done

func save_gift_boxes():
	var boxes_list = box_spawner.save_data()
	pd.boxes_instantiated = boxes_list

func _ready():

	ui.show()
	set_up_map()
	current_gift_node = null
	DialogueManager.dialogue_ended.connect(dialogue_ended)
	number_of_lucubs_caught = 0.0
	number_of_lucubs_caught = 0.0
	ending_announcement = 0
	last_dialogue = false

@warning_ignore("unused_parameter")
func dialogue_ended(resource):
	if SessionManager.game_mode == GC.GameModes.EXPLORATION:
		return
	if current_gift_node != null:
		current_gift_node.finish_item_collection()

		current_gift_node = null
	if SessionManager.get_giftcollected() >= 10 && !last_dialogue:
		start_dialogue("LastBox_Dialogue", box_diag, 0.5)
		last_dialogue = true

	if ending_announcement > 0:
		process_ending_announcement()
@onready var castle_background = $"../CastleBackground"

func process_ending_announcement():
	#make lucubs jump up and down
	if ending_announcement == 1:
		castle_background.surprise_boss()
		ending_announcement+= 1
		start_dialogue("Ending_Announcement_02",main_diag, 1.0)
	elif ending_announcement == 2:
		ending_announcement+= 1
		cam_controller.flash_camera()
	pass

@warning_ignore("unused_parameter")
func _process(delta):
	pass#save_gift_boxes()

## CUTSCENES
func start_cutscene(cam_target):
	await Fade.fade_out(GC.FADE_OUT_DURATION).finished
	hide_UI()
	cam_controller.switch_cam(cam_target)
	cam_controller.change_follow_offset(0.0)
	cam_controller.turn_on_positioning_smoothing()
	await Fade.fade_in(GC.FADE_IN_DURATION).finished
	return

func finish_cutscene():
	await Fade.fade_out(GC.FADE_OUT_DURATION).finished
	reveal_UI()
	cam_controller.reset()
	SessionManager.pause_game(false)
	luca.reset()
	await Fade.fade_in(GC.FADE_IN_DURATION).finished
#
	#check_for_final_door()
	pass

func set_up_map():
	update_veils()

func update_veils():
	for layer in GC.VeilLayers:
		main_map.set_layer_enabled(GC.VeilLayers[layer], !SessionManager.is_underground_room_open(layer))

func open_door(door_to_open: Room_Door):
	if door_to_open:
		current_door = door_to_open
		await start_cutscene(door_to_open)
		door_to_open.door_opened.connect(finish_cutscene)
		door_to_open.door_opening.connect(set_up_map)
		door_to_open.open_door()
	else:
		show_minimap()
		luca.reset()
		SessionManager.pause_game(false)

func show_minimap():
	minimap.show()

func show_book():
	inventory_button.show()

func check_for_final_door():
	if SessionManager.get_giftcollected() >= 10 && !SessionManager.is_underground_room_open(main_castle_veil_door.veil_to_unlock):
		SessionManager.pause_game(true)
		open_door(main_castle_veil_door)
		return true
	return false

func turn_on_cinematic():

	$"../Camera_Controller/MainCamera".call_deferred("toggle_cinematic",true)

func turn_off_cinematic():
	$"../Camera_Controller/MainCamera".toggle_cinematic(false)

func hide_UI():
	ui.hide()

func reveal_UI():
	ui.show()
	minimap.show()
	inventory_button.show()

## Applies gravity to entity in question
func apply_gravity(entity: CharacterBody2D, delta:float, gravity:float) -> void:
	entity.velocity.y += gravity * delta

## DIALOGUE
func start_dialogue(dialogue_name, resource = main_diag, _delay_time=0.0):

	if dialogue_name in resource.titles.keys():
		SessionManager.pause_from_dialogue()
		await get_tree().create_timer(_delay_time).timeout
		DialogueManager.show_dialogue_balloon(resource, dialogue_name)
	else:
		dialogue_ended(resource)
func player_starting_cutscene():
	start_dialogue("Beginning_Dialogue", main_diag, 0.5)

func _on_entrance_dialogue_body_entered(body):
	if body.is_in_group("Player"):
		start_dialogue("Entrance_Dialogue", main_diag, 0.5)
		$Entrance_Dialogue_Area.queue_free()


func _on_beginning_entrance_dialogue(body):
	if body.is_in_group("Player"):
		start_dialogue("Beginning_Announcement",main_diag, 0.15)
		$Entrance_Beginning_Area.queue_free()

func player_ending_cutscene():
	start_dialogue("Ending_Announcement",main_diag, 1.0)
	ending_announcement = 1
	cam_controller.zoom_target = 2.0
	cam_controller.offset_target = -75.0

func surprised_lucub_dialogue(lucub):
	var dialogue_title = lucub.Name + "_Surprised_Dialogue"
	check_special_cutscene(lucub.Name)
	start_dialogue(dialogue_title,lucub_diag)

func caught_lucub_dialogue():
	if number_of_lucubs_caught == 0:
		start_dialogue("First_Caught_Dialogue",lucub_diag)
		number_of_lucubs_caught += 1

func start_signpost_dialogue(title):
	start_dialogue(title,sign_diag)
func start_cultlucub_dialogue(title):
	start_dialogue(title, lucub_diag)
func start_giftbox_dialogue(gift_node):
	var title = gift_node.item_to_unlock.dialogue_title
	if title == null || title.is_empty():
		title = gift_node.item_to_unlock.Name + "_Dialogue"
	current_gift_node = gift_node
	start_dialogue(title,box_diag)

func start_door_dialogue(veil_to_unlock):
	start_dialogue(veil_to_unlock + "_Dialogue",door_diag)
	pass

func check_special_cutscene(lucub_name):
	if lucub_name == "Knife_Lucub":
		$"../Doors/Tutorial_Door".call_deferred("close_door")


func _on_first_section_dialogue_body_entered(body):
	if body.is_in_group("Player"):
		start_dialogue("First_Section_Dialogue", main_diag, 0.5)
		$First_Section_Area.queue_free()


func _on_gold_dialogue_body_entered(body):
	if body.is_in_group("Player"):
		start_dialogue("Gold_Section_Dialogue", main_diag, 0.5)
		$Gold_Dialogue.queue_free()


func _on_booba_room_dialogue_body_entered(body):
	if body.is_in_group("Player"):
		start_dialogue("Booba_Room_Dialogue", main_diag, 0.5)
		$BoobaRoom_Area.queue_free()

func start_ending_scene():
	turn_on_cinematic()
	hide_UI()
