class_name Lucub_Controller extends Path2D
@onready var game_manager = $"../../Game Manager"


@onready var state_chart = $StateChart as StateChart
@onready var zone = $FollowPath/LucubBody/DetectionZone/Zone
@onready var trail = $Trail
@onready var catch_lucub_cutscene = $"../../UI/Catch Lucub Cutscene"

@onready var follow_path = $FollowPath
@onready var tutorial_animation = $FollowPath/LucubBody/Tutorial/Tutorial_Animation

var current_state: GC.Lucub_Stage = GC.Lucub_Stage.IDLE

@export var Lucub_Base: Lucub
@export var gift_spawn_marker: Marker2D
@export var running_speed: float  = 0.35
@onready var idle_zone = preload("res://Scenes/Lucub/Lucub_IdleZone.tres")
@onready var alert_zone = preload("res://Scenes/Lucub/Lucub_AlertZone.tres")
@onready var dead_zone = preload("res://Scenes/Lucub/Lucub_GraveCollision.tres")
@onready var point_light_2d = $FollowPath/LucubBody/PointLight2D


signal spawn_box(gift, marker)
signal got_caught
signal running_away
var firstRun

func _physics_process(_delta):
	if firstRun:
		for body in $FollowPath/LucubBody/DetectionZone.get_overlapping_bodies():
			var found_body = _on_body_entered(body)
			if found_body:
				firstRun = false
				break
	if follow_path.global_position.y >= 30:
		point_light_2d.show()
	else:
		point_light_2d.hide()

# Called when the node enters the scene tree for the first time.
func _ready():
	firstRun = true
	global_position = Lucub_Base.StartPoint
	match SessionManager.get_lucub_status(Lucub_Base.Name):
		GC.Lucub_Stage.IDLE:
			follow_path.progress_ratio = 0.0
			current_state = GC.Lucub_Stage.IDLE
		GC.Lucub_Stage.SURPRISED:
			follow_path.progress_ratio = 0.0
			current_state = GC.Lucub_Stage.SURPRISED
			state_chart.send_event.call_deferred("surprised")
		GC.Lucub_Stage.RUNNING_AWAY:
			current_state = GC.Lucub_Stage.RUNNING_AWAY
			state_chart.send_event.call_deferred("alert")
		GC.Lucub_Stage.ALERT:
			follow_path.progress_ratio = 1.0
			current_state = GC.Lucub_Stage.ALERT
			state_chart.send_event.call_deferred("alert")
		GC.Lucub_Stage.CAUGHT:
			follow_path.progress_ratio = 1.0
			current_state = GC.Lucub_Stage.CAUGHT
			state_chart.send_event.call_deferred("died")
		_:
			push_error("Lucub in an unknown state. Default to Idle")
	reset_zones()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if current_state == GC.Lucub_Stage.RUNNING_AWAY:
		if follow_path.progress_ratio < 1.0:
			follow_path.progress_ratio += running_speed * delta
		else:
			SessionManager.update_lucub(Lucub_Base.Name, GC.Lucub_Stage.ALERT)
			current_state = GC.Lucub_Stage.ALERT
			reset_zones()


func finished_surprised():
	current_state = GC.Lucub_Stage.RUNNING_AWAY
	reset_zones()
	SessionManager.update_lucub(Lucub_Base.Name, GC.Lucub_Stage.RUNNING_AWAY)
	state_chart.send_event("alert")

func finished_caught():
	current_state = GC.Lucub_Stage.CAUGHT
	reset_zones()
	SessionManager.update_lucub(Lucub_Base.Name, GC.Lucub_Stage.CAUGHT)
	state_chart.send_event("died")
	trail.delete_all_points()
	tutorial_animation.play("idle")


func spawn_gift():
	spawn_box.emit(Lucub_Base.ItemToGive, Lucub_Base, gift_spawn_marker.global_position)


func reset_zones():
	match current_state:
		GC.Lucub_Stage.IDLE:
			zone.shape = idle_zone
		GC.Lucub_Stage.SURPRISED:
			zone.shape = null
		GC.Lucub_Stage.RUNNING_AWAY:
			zone.shape = null
		GC.Lucub_Stage.ALERT:
			zone.shape = alert_zone
		GC.Lucub_Stage.CAUGHT:
			zone.shape = dead_zone

func _on_body_entered(body):
	if body.is_in_group("Player"):
		match current_state:
			GC.Lucub_Stage.IDLE:
				zone.shape = null
				SessionManager.update_lucub(Lucub_Base.Name, GC.Lucub_Stage.SURPRISED)
				current_state = GC.Lucub_Stage.SURPRISED
				reset_zones()
				state_chart.send_event("surprised")
				game_manager.surprised_lucub_dialogue(Lucub_Base)
			GC.Lucub_Stage.ALERT:
				tutorial_animation.play("highlight")
				body.set_nearest_lucub(self)
			GC.Lucub_Stage.CAUGHT:
				tutorial_animation.play("idle")
				state_chart.send_event("open_dialogue")
			_:
				pass

func _on_capture():
	zone.shape = null
	catch_lucub_sequence()

func catch_lucub_sequence():
	catch_lucub_cutscene.play_cutscene(self)

#on video finish:
func catch_sequence_vid_finished():
	catch_sequence()

func catch_sequence():
	SessionManager.update_lucub(Lucub_Base.Name, GC.Lucub_Stage.CAUGHT)
	current_state = GC.Lucub_Stage.CAUGHT
	reset_zones()
	state_chart.send_event("caught")

func _on_body_exited(body):
	if body.is_in_group("Player"):
		match current_state:
			GC.Lucub_Stage.CAUGHT:
				state_chart.send_event("close_dialogue")
			GC.Lucub_Stage.ALERT:
				tutorial_animation.play("idle")
				body.set_reset_lucub()

func signal_running_away():

	running_away.emit()
