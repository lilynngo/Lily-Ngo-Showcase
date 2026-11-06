class_name Room_Door extends StaticBody2D
@onready var collision_shape_2d = $CollisionShape2D

@onready var anim = $TextureRect/AnimationPlayer
@export var veil_to_unlock: String = ""
@onready var gm = $"../../Game Manager"

signal door_opened
signal door_opening
# Called when the node enters the scene tree for the first time.
func _ready():
	if SessionManager.is_underground_room_open(veil_to_unlock) || veil_to_unlock == "Tutorial":
		anim.play("Door_Open")
		collision_shape_2d.disabled = true
	else:
		anim.play("Door_Close")
		collision_shape_2d.disabled = false

func close_door():
	collision_shape_2d.disabled = false
	anim.play("Door_Closing")
	SessionManager.lock_veil(veil_to_unlock)
	SessionManager.play_door_slam()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func open_door():
	await get_tree().create_timer(0.5).timeout
	SessionManager.unlock_veil(veil_to_unlock)
	if veil_to_unlock == "First2RoomVeil":
		SessionManager.unlock_veil("FirstRoomVeil")
	door_opening.emit()
	anim.play("Door_Opening")
	collision_shape_2d.disabled = true
	if veil_to_unlock == "Tutorial" || veil_to_unlock == "MainCastleVeil":
		SessionManager.play_castle_door_opening()
	else:
		SessionManager.play_regular_door_opening()

func done_open_door():
	door_opened.emit()
	gm.start_door_dialogue(veil_to_unlock)
