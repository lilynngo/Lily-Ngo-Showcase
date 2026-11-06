extends Node

const POINTING_HAND = Input.CURSOR_POINTING_HAND
const CURSOR_HAND = Input.CURSOR_ARROW
const CURSOR_FORBIDDEN = Input.CURSOR_FORBIDDEN

const CONTROL_POINTING_HAND = Control.CURSOR_POINTING_HAND
const CONTROL_CURSOR_FORBIDDEN = Control.CURSOR_FORBIDDEN

# Enums.
const MainMenuOptions = {
		"WELCOME" : ["MISSION", "How to sabotage the lucubs' plan!"],
		"OBJECTIVE" : ["SCHEME?", "What are the lucubs planning?"],
		"CONTINUE": ["CONTINUE", "Continue from previous save"],
		"NEWGAME": ["START", "Start a new game"],
		"SETTINGS" : ["SETTINGS", "Change game, display, audio settings"],
		"CREDITS": ["CREDITS", "Meet the clowns!"],
		"QUIT" : ["QUIT", "Bye bye :("]
}

const InGameMenuOptions = {
		"MISSION" : ["MISSION", "Evil & Mean Mafia Plan"],
		"OBJECTIVE" : ["SCHEME?", "What are the lucubs planning?"],
		"LOOT": ["LOOT", "Review the items you've confiscated"],
		"SETTINGS" : ["SETTINGS", "Change game, display, audio settings"],
		"MAP" : ["SECRET", "Scroll of Secrets: Reveals the architecture of the area"],
		"MAINMENU": ["MENU", "Return to Main Menu"],
		"QUIT" : ["QUIT", "Bye bye :("]
}

const ThemeTypeVariations = {
	"NORMAL_BOOKMARK":"BookmarkLabel",
	"SELECTED_BOOKMARK": "BookmarkLabel_Selected"
}

const AvailableScenes = {
	"Splash Screen": "res://Scenes/Game/splash_screen.tscn",
	"Intro Video": "res://Scenes/Game/story_intro.tscn",
	"Story Mode": "res://Scenes/Game/story_mode.tscn",
	"Intro Cutscene": "res://Scenes/Game/story_intro.tscn",
	"Main Menu": "res://Scenes/Game/main_menu.tscn",
	"Speedrun": "res://Scenes/Game/speedrun_mode.tscn",
	"Exploration": "res://Scenes/Game/exploration_mode.tscn",
	"Ending Cutscene": "res://Scenes/Game/ending_cutscene.tscn"
}

const UNIT_SIZE = 32
const PLAYER_SCALE = 0.8
const FADE_IN_DURATION = 0.5
const FADE_OUT_DURATION = 0.5

enum Lucub_Stage {IDLE, SURPRISED, RUNNING_AWAY, ALERT, CAUGHT}
enum Box_Stage {APPEAR, IDLE, DISAPPEAR, HIGHLIGHT}
enum GameModes { STORYMODE, SPEEDRUN, EXPLORATION}
enum SessionStatus {CONTINUE, NEW}



const VeilLayers = {
	"FirstRoomVeil":6,
	"HACRoomVeil":7,
	"SecondRoomVeil":8,
	"ThirdRoomVeil":9,
	"FourthRoomVeil": 10,
	"SixthRoomVeil": 11,
	"TrollRoomVeil":12,
	"MainCastleVeil": 13,
	"Tutorial": 14
}

@export var DoorsToUnlock_ByLucub = {
	"Knife_Lucub":"FirstRoomVeil",
	"Gloves_Lucub":"First2RoomVeil",
	"Poggles_Lucub":"Sixth2RoomVeil",
	"Augustus_Lucub":"SecondRoomVeil",
	"Candle_Lucub":"ThirdRoomVeil",
	"Recorder_Lucub":"FourthRoomVeil",
	"Bone_Lucub":"SixthRoomVeil",
	"Pape_Lucub":"TrollRoomVeil",
	"Hat_Lucub":null,
	"Clown_Lucub":null,
	"FinalMap_Lucub":"HACRoomVeil"
}

const GiftsList = {
	"Knife":preload("res://Script/Resource/Collectibles/Knife.tres"),
	"BlackGloves":preload("res://Script/Resource/Collectibles/BlackGloves.tres"),
	"AugustusTail":preload("res://Script/Resource/Collectibles/AugustusTail.tres"),
	"Poggles":preload("res://Script/Resource/Collectibles/Poggles.tres"),
	"PogCandle":preload("res://Script/Resource/Collectibles/PogCandle.tres"),
	"Recorder":preload("res://Script/Resource/Collectibles/Recorder.tres"),
	"DogBone":preload("res://Script/Resource/Collectibles/DogBone.tres"),
	"BossPinata":preload("res://Script/Resource/Collectibles/BossPinata.tres"),
	"BdayHat":preload("res://Script/Resource/Collectibles/BdayHat.tres"),
	"ClownHat":preload("res://Script/Resource/Collectibles/ClownHat.tres"),
	"FinalMap": preload("res://Script/Resource/Collectibles/FinalMap.tres"),
	"Map": preload("res://Script/Resource/Collectibles/Map.tres")
}

const Balloons = [
"res://Asset/Sprites/DECORATIONS/Aia.png",
"res://Asset/Sprites/DECORATIONS/Alban.png",
"res://Asset/Sprites/DECORATIONS/Aster.png",
"res://Asset/Sprites/DECORATIONS/Boss.png",
"res://Asset/Sprites/DECORATIONS/Claude.png",
"res://Asset/Sprites/DECORATIONS/Doppio.png",
"res://Asset/Sprites/DECORATIONS/Elira.png",
"res://Asset/Sprites/DECORATIONS/Enna.png",
"res://Asset/Sprites/DECORATIONS/Finana.png",
"res://Asset/Sprites/DECORATIONS/Fulgur.png",
"res://Asset/Sprites/DECORATIONS/Hex.png",
"res://Asset/Sprites/DECORATIONS/Ike.png",
"res://Asset/Sprites/DECORATIONS/Kotoka.png",
"res://Asset/Sprites/DECORATIONS/Kunai.png",
"res://Asset/Sprites/DECORATIONS/Maria.png",
"res://Asset/Sprites/DECORATIONS/Meloco.png",
"res://Asset/Sprites/DECORATIONS/Millie.png",
"res://Asset/Sprites/DECORATIONS/Petra.png",
"res://Asset/Sprites/DECORATIONS/Reimu.png",
"res://Asset/Sprites/DECORATIONS/Ren.png",
"res://Asset/Sprites/DECORATIONS/Rosemi.png",
"res://Asset/Sprites/DECORATIONS/Scarle.png",
"res://Asset/Sprites/DECORATIONS/Shu.png",
"res://Asset/Sprites/DECORATIONS/Sonny.png",
"res://Asset/Sprites/DECORATIONS/Uki.png",
"res://Asset/Sprites/DECORATIONS/Vanta.png",
"res://Asset/Sprites/DECORATIONS/Ver.png",
"res://Asset/Sprites/DECORATIONS/Vezalius.png",
"res://Asset/Sprites/DECORATIONS/Victoria.png",
"res://Asset/Sprites/DECORATIONS/Vox.png",
"res://Asset/Sprites/DECORATIONS/Yu Q.png"
]
