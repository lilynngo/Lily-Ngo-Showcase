class_name Gift_Box extends Node2D

@export var wait_seconds: float = 5.0
@export var item_to_unlock: Collectible = preload("res://Script/Resource/Collectibles/FinalMap.tres")
@export var veil_to_unlock: Room_Door
@export var lucub_connected: Lucub
@export var spawn_location: Vector2
## Nodes
@onready var item_animation = $Item_Animation
@onready var box_animation = $Box_Animation
@onready var tutorial_animation = $Tutorial_Animation

@onready var item = $Item
@onready var box_zone = $Box_Zone

## Signals
signal open_door(door)
signal start_dialogue(gift)

var firstRun = true
var box_stage = GC.Box_Stage.APPEAR

# Called when the node enters the scene tree for the first time.
func _ready():
	box_animation.play("appear")
	item.texture = item_to_unlock.Item_Image
	firstRun = true
	scale = Vector2(GC.PLAYER_SCALE, GC.PLAYER_SCALE)

	## Check if player is in area 2D
	pass # Replace with function body.

func play_open_sound():

	SessionManager.play_open_box_sound()

func initiate_box(gift: Collectible, door: Room_Door, wait_time: float, lucub, spawn_loc:Vector2):
	veil_to_unlock = door
	item_to_unlock = gift
	wait_seconds = wait_time
	lucub_connected = lucub
	spawn_location=spawn_loc
	pass


func _physics_process(_delta):
	if firstRun:
		for body in box_zone.get_overlapping_bodies():
			var found_body = _on_body_entered(body)
			if found_body:
				firstRun = false
				break

func item_collected():
	SessionManager.update_gift(item_to_unlock)
	start_dialogue.emit(self)

func finish_item_collection():
	open_door.emit(veil_to_unlock)
	queue_free()

func reveal_item():
	item_animation.play("appear")

func hide_item():
	item_animation.play("disappear")

func interact():
	box_animation.play("disappear")
	tutorial_animation.play("idle")

func update_to_appear():
	box_stage = GC.Box_Stage.APPEAR

func update_to_idle():
	box_stage = GC.Box_Stage.IDLE

func update_to_highlight():
	box_stage = GC.Box_Stage.HIGHLIGHT

func update_to_disappear():
	box_stage = GC.Box_Stage.DISAPPEAR

func _on_body_entered(body):
	if body.is_in_group("Player") && box_stage == GC.Box_Stage.IDLE:
		box_animation.play("highlight")
		body.set_nearest_gift_box(self)
		update_to_highlight()
		return true
	return false

func _on_body_exited(body):
	if body.is_in_group("Player") && box_stage == GC.Box_Stage.HIGHLIGHT:
		update_to_idle()
		box_animation.play("idle")
		body.set_reset_gift()
