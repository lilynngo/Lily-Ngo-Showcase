extends Node2D

var new_box = preload("res://Scenes/Giftbox/gift_box.tscn")
@onready var door_manager = $"../Doors" as DoorManager

@onready var game_manager = $"../Game Manager" as GameManager

signal finished_spawn_box

func _ready():
	load_data()

func spawn_box(gift: Collectible, lucub: Lucub, spawn_loc: Vector2):
	var instance = new_box.instantiate() as Gift_Box
	var door = door_manager.get_door(lucub)  as Room_Door
	instance.initiate_box(gift, door, gift.wait_time, lucub, spawn_loc)
	instance.global_position = spawn_loc
	instance.open_door.connect(start_door_cutscene)
	instance.start_dialogue.connect(start_dialogue)
	self.add_child(instance)
	SessionManager.pause_game(false)
	finished_spawn_box.emit()

func delete_boxes():
	for box in self.get_children():
		box.queue_free()

func save_data():
	var boxes = self.get_children()
	var list : Array[PackedScene] = []

	for box in boxes:
		var box_scene = PackedScene.new()
		box_scene.pack(box)
		list.append(box_scene)
	return list

func load_data():
	for box in SessionManager.pd.boxes_instantiated:
		var instance = box.instantiate() as Gift_Box
		spawn_box(instance.item_to_unlock, instance.lucub_connected, instance.spawn_location)

func start_door_cutscene(door_to_open: Room_Door):
	game_manager.open_door(door_to_open)

func start_dialogue(gift_node):
	game_manager.start_giftbox_dialogue(gift_node)
	pass


func _on_spawn_gift(gift, lucub, marker):
	spawn_box(gift, lucub, marker)
