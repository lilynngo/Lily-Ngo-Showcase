class_name PlayerData extends Resource

@export_group("Game Progress")
@export var Version:float = 1.00
@export_subgroup("Completion")
@export var HasCompletedGame:bool = false
@export var HasSaveFile: bool = false
@export var HasOpenGame: bool = false
@export var HasSeenStoryCutscene: bool = false

@export_group("Current Session")
@export_subgroup("Current Game")
@export var boxes_instantiated: Array[PackedScene] = []
@export var current_time: float = 0.0

@export_group("Rooms")
@export var UnlockedRoomVeil = {
	"FirstRoomVeil":false,
	"First2RoomVeil":false,
	"HACRoomVeil":false,
	"SecondRoomVeil":false,
	"ThirdRoomVeil":false,
	"FourthRoomVeil": false,
	"FifthRoomVeil":false,
	"Sixth2RoomVeil": false,
	"SixthRoomVeil": false,
	"TrollRoomVeil":false,
	"MainCastleVeil": false,
	"Tutorial": false
}

@export_group("Lucubs")
@export var LucubsFound = 0
@export var LucubsStatus = {
	"Knife_Lucub":GC.Lucub_Stage.IDLE,
	"Gloves_Lucub":GC.Lucub_Stage.IDLE,
	"Augustus_Lucub":GC.Lucub_Stage.IDLE,
	"Poggles_Lucub":GC.Lucub_Stage.IDLE,
	"Candle_Lucub":GC.Lucub_Stage.IDLE,
	"Recorder_Lucub":GC.Lucub_Stage.IDLE,
	"Bone_Lucub":GC.Lucub_Stage.IDLE,
	"Pape_Lucub":GC.Lucub_Stage.IDLE,
	"Hat_Lucub":GC.Lucub_Stage.IDLE,
	"Clown_Lucub":GC.Lucub_Stage.IDLE,
	"FinalMap_Lucub":GC.Lucub_Stage.IDLE
}

@export_group("Gifts")
@export var GiftCollected = 0
@export var GiftsStatus = {
	"Map": false,
	"Knife":false,
	"BlackGloves":false,
	"AugustusTail":false,
	"Poggles":false,
	"PogCandle":false,
	"Recorder":false,
	"DogBone":false,
	"BossPinata":false,
	"BdayHat":false,
	"ClownHat":false,
	"FinalMap": false
}

@export_group("Player Movement")
@export_subgroup("SavedData")
@export var position: Vector2

@export_subgroup("Movement")
@export var movement_speed: float = GC.UNIT_SIZE * 5
@export var acceleration_speed: float = 10.0
@export var deceleration_speed: float = 20.0

@export_subgroup("Jumping")
@export var max_jumps: int = 1
@export var max_jump_speed: float = -500
@export var min_jump_speed: float = -100
@export var max_jump_height: float =  GC.UNIT_SIZE * 3.2
@export var min_jump_height: float = GC.UNIT_SIZE * 0.3
@export var jump_duration: float = 0.5
@export var jump_decelarator: float = 1.5

@export_subgroup("Falling")
@export var fall_speed: float = 350.0
@export var gravity: float = 2*max_jump_height / pow(jump_duration, 2) + 700


func reset_mode():
	reset_gifts()
	reset_rooms()
	reset_lucubs()
	reset_movement()

func reset_lucubs():
	LucubsFound = 0
	LucubsStatus = {
		"Knife_Lucub":GC.Lucub_Stage.IDLE,
		"Gloves_Lucub":GC.Lucub_Stage.IDLE,
		"Augustus_Lucub":GC.Lucub_Stage.IDLE,
		"Poggles_Lucub":GC.Lucub_Stage.IDLE,
		"Candle_Lucub":GC.Lucub_Stage.IDLE,
		"Recorder_Lucub":GC.Lucub_Stage.IDLE,
		"Bone_Lucub":GC.Lucub_Stage.IDLE,
		"Pape_Lucub":GC.Lucub_Stage.IDLE,
		"Hat_Lucub":GC.Lucub_Stage.IDLE,
		"Clown_Lucub":GC.Lucub_Stage.IDLE,
		"FinalMap_Lucub":GC.Lucub_Stage.IDLE
	}

func reset_gifts():
	current_time = 0.0
	GiftCollected = 0
	GiftsStatus = {

		"Map": false,
		"Knife":false,
		"BlackGloves":false,
		"AugustusTail":false,
		"Poggles":false,
		"PogCandle":false,
		"Recorder":false,
		"DogBone":false,
		"BossPinata":false,
		"BdayHat":false,
		"ClownHat":false,
		"FinalMap": false
	}
	boxes_instantiated = []

func reset_rooms():

	UnlockedRoomVeil = {
		"FirstRoomVeil":false,
		"First2RoomVeil":false,
		"HACRoomVeil":false,
		"SecondRoomVeil":false,
		"ThirdRoomVeil":false,
		"FourthRoomVeil": false,
		"FifthRoomVeil":false,
		"Sixth2RoomVeil": false,
		"SixthRoomVeil": false,
		"TrollRoomVeil":false,
		"MainCastleVeil": false,
		"Tutorial": false
	}

func reset_movement():
	max_jumps = 1
	max_jump_speed= -500
	min_jump_speed= -100
	max_jump_height=  GC.UNIT_SIZE * 3.2
	min_jump_height= GC.UNIT_SIZE * 0.3
	jump_duration = 0.5
	jump_decelarator = 1.5

	movement_speed = GC.UNIT_SIZE * 5
	acceleration_speed = 10.0
	deceleration_speed = 20.0

	fall_speed = 350.0
	gravity = 2*max_jump_height / pow(jump_duration, 2) + 700

	position = Vector2.ZERO

func set_exploration():
	reset_mode()
	UnlockedRoomVeil = {
		"FirstRoomVeil":true,
		"First2RoomVeil":true,
		"HACRoomVeil":true,
		"SecondRoomVeil":true,
		"ThirdRoomVeil":true,
		"FourthRoomVeil": true,
		"FifthRoomVeil":true,
		"Sixth2RoomVeil": true,
		"SixthRoomVeil": true,
		"TrollRoomVeil":true,
		"MainCastleVeil": true,
		"Tutorial": true
	}
	GiftsStatus = {

		"Map": true,
		"Knife":true,
		"BlackGloves":true,
		"AugustusTail":true,
		"Poggles":true,
		"PogCandle":true,
		"Recorder":true,
		"DogBone":true,
		"BossPinata":true,
		"BdayHat":true,
		"ClownHat":true,
		"FinalMap": true
	}
