extends Node

var pd: PlayerData = preload("res://Script/Resource/player_current_session.tres")
var save_path = "user://last_session.tres" ## WINDOWS: %APPDATA%\Godot\app_userdata\Lock In Gamers- Mafia Adventure
var previous_save: PlayerData
var save_file_available : bool = false
var isPaused: bool = false
var CutsceneInProgress: bool = false
var in_game_menu_page: String

## Set Game Mode
func load_previous_save():
	load_data()
	if SessionManager.previous_save != null:
		pd = SessionManager.previous_save
	else:
		load_new_game()


func load_new_game():
	pd.reset_mode()
	print("load new game")

var game_mode: GC.GameModes = GC.GameModes.STORYMODE
var game_status: GC.SessionStatus = GC.SessionStatus.NEW

## Player Data
func get_player_data():
	return pd

#Scoring
func update_gift(item):
	pd.GiftsStatus[item.Name] = true

## Room Data
func is_underground_room_open(veil_to_unlock):
	if pd.UnlockedRoomVeil.has(veil_to_unlock):
		return pd.UnlockedRoomVeil[veil_to_unlock]
	return false

func unlock_veil(veil_to_unlock):
	pd.UnlockedRoomVeil[veil_to_unlock] = true

func lock_veil (veil_to_lock):
	pd.UnlockedRoomVeil[veil_to_lock] = false

func pause_game(isPause, _NotCutscene=false, _pause_time:float = 0.0):
	isPaused = isPause
	CutsceneInProgress = !_NotCutscene
	await get_tree().create_timer(_pause_time).timeout
	if _pause_time > 0:
		pause_game(false, _NotCutscene, 0.0)

func unpause_from_dialogue():
	await get_tree().create_timer(0.15).timeout
	pause_game(false)
func pause_from_dialogue():
	await get_tree().create_timer(0.15).timeout
	pause_game(true)

func set_ingame_menu_page(pageName: String):
	in_game_menu_page = pageName

## Lucub Data
func get_lucub_status(lucub_name: String):
	return pd.LucubsStatus[lucub_name]

func update_lucub(lucub_name:String, lucub_stage: GC.Lucub_Stage):
	pd.LucubsStatus[lucub_name] = lucub_stage

func get_giftcollected():
	var gift_unlocked = 0
	for gift in SessionManager.pd.GiftsStatus:
		if SessionManager.pd.GiftsStatus[gift]:
			if !gift.to_upper().contains("MAP"):
				gift_unlocked += 1
	return gift_unlocked

## Save Data
func save_data():
	ResourceSaver.save(pd, save_path)

func _ready():
	pd.HasOpenGame = true
	load_data()

func load_data():
	if FileAccess.file_exists(save_path):
		previous_save = SafeResourceLoader.load(save_path) as PlayerData
		if previous_save == null:
			save_file_available = false
		else:
			if previous_save.Version != null and previous_save.Version >= 1.0:
				var version_num = pd.Version
				pd = previous_save
				pd.Version = version_num
			save_file_available = true
	else:
		save_file_available = false

func has_game_completed_before():
	return pd.HasCompletedGame

## ON QUIT
func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_data()
		get_tree().quit() # default behavior

# TODO: Code in the ending cutscene!!!
func return_to_main_menu():
	var menu = GC.AvailableScenes["Main Menu"]
	GameIndex.change_scene(menu)

var page_flip = preload("res://Asset/Sound/SFX/page-flip-modified.wav")
var speechless_loop = preload("res://Asset/Sound/Music/SPEECHLESS_LOOP.wav")
var fanfare_sfx = preload("res://Asset/Sound/SFX/medieval-fanfare-6826.mp3")
var beep_sfx = preload("res://Asset/Sound/SFX/censor-beep-88052.mp3")
var static_sfx = preload("res://Asset/Sound/SFX/radio-static-6382.mp3")
var nonono_sfx = preload("res://Asset/Sound/SFX/No No No No - Sound - SR.mp3")
var button_sfx = preload("res://Asset/Sound/SFX/projector-button-push-6258.mp3")
var old_door_sfx = preload("res://Asset/Sound/SFX/opening-metal-door-199581.mp3")
var reg_door_sfx = preload("res://Asset/Sound/SFX/large-metal-lift-door-openingwav-14459.mp3")
var wowie_sfx = preload("res://Asset/Sound/SFX/Wow_Wowie.wav")
var jump_sfx = preload("res://Asset/Sound/SFX/cartoon-jump-6462.mp3")
var running_sfx = preload("res://Asset/Sound/SFX/running-in-grass-6237.mp3")
var door_slam_sfx = preload("res://Asset/Sound/SFX/metal-door-slam-172172.mp3")
var rummaging_sfx= preload("res://Asset/Sound/SFX/backpack-rummaging-69868.mp3")
var luca_feel_sfx = preload("res://Asset/Sound/SFX/LucaBible/AllICanFeelIsLuca.wav")
var luca_see_sfx = preload("res://Asset/Sound/SFX/LucaBible/AllICanSeeInMyDreamIsLuca.wav")
var luca_hear_sfx = preload("res://Asset/Sound/SFX/LucaBible/AllIHearIsLuca.wav")
var luca_think_sfx = preload("res://Asset/Sound/SFX/LucaBible/AllICanThinkAboutIsLuca.wav")
var luca_life_sfx = preload("res://Asset/Sound/SFX/LucaBible/LifeWithoutLucaIsMeaningless.wav")
var luca_love_sfx = preload("res://Asset/Sound/SFX/LucaBible/LucaisLoveLucaisLife.wav")
var luca_everything_sfx = preload("res://Asset/Sound/SFX/LucaBible/LucaIsEverything.wav")
var horror_ambience_sfx = preload("res://Asset/Sound/SFX/LucaBible/occult-chant-ambience-192416.mp3")
var luca_world_sfx = preload("res://Asset/Sound/SFX/LucaBible/LucaIsMyworld.wav")
var luca_bonk_sfx = preload("res://Asset/Sound/SFX/BossBonk1.wav")
var voice_mumble_sfx = preload("res://Asset/Sound/SFX/cartoon-phone-voice-88637.mp3")
var cheering_sfx = preload("res://Asset/Sound/SFX/cheering_mixdown.wav")
var pog1_sfx = preload("res://Asset/Sound/SFX/Pog.wav")
var pog2_sfx = preload("res://Asset/Sound/SFX/Pog_2.wav")
var pog3_sfx = preload("res://Asset/Sound/SFX/Pog_3.wav")
## SOUNDS
func play_main_menu_music():
	SoundManager.play_music(speechless_loop, 2.0)
	pass



func play_ingame_music():
	SoundManager.play_music_from_position(speechless_loop, 0.0, 1.5)
	pass

func pause_ingame_music():
	SoundManager.pause_music()

func continue_ingame_music():
	SoundManager.resume_music(speechless_loop)
	pass

func play_page_flip_sfx():
	SoundManager.play_sound(page_flip)
	pass

func play_announcement_sound():
	SoundManager.play_sound(fanfare_sfx)
	pass

func stop_announcement_sound():
	SoundManager.stop_sound(fanfare_sfx)
	pass
func play_open_box_sound():
	SoundManager.play_sound(wowie_sfx)

func play_static_sound():
	SoundManager.play_sound(static_sfx)
	pass

func stop_static_sound():
	SoundManager.stop_sound(static_sfx)

func play_censor_sound():
	SoundManager.play_sound(beep_sfx)

func play_nonono_sound():
	SoundManager.play_sound(nonono_sfx)

func play_button_press_sound():
	SoundManager.play_sound(button_sfx)

func play_castle_door_opening():
	SoundManager.play_sound(old_door_sfx)

func play_regular_door_opening():
	SoundManager.play_sound(reg_door_sfx)

func play_oof_sound():
	pass


func play_jump_sound():
	SoundManager.play_sound(jump_sfx)

func play_running_sound():
	SoundManager.play_sound(running_sfx)

func stop_running_sound():
	SoundManager.stop_sound(running_sfx)

func play_door_slam():
	SoundManager.play_sound(door_slam_sfx)

func play_rummaging_sound():
	SoundManager.play_sound(rummaging_sfx)

func stop_rummaging_sound():
	SoundManager.stop_sound(rummaging_sfx)

func play_luca_hear_sound():
	SoundManager.play_sound(luca_hear_sfx)

func play_luca_feel_sound():
	SoundManager.play_sound(luca_feel_sfx)

func play_luca_think_sound():
	SoundManager.play_sound(luca_think_sfx)

func play_luca_see_sound():
	SoundManager.play_sound(luca_see_sfx)

func play_luca_life_sound():
	SoundManager.play_sound(luca_life_sfx)

func play_luca_love_sound():
	SoundManager.play_sound(luca_love_sfx)

func play_luca_everything_sound():
	SoundManager.play_sound(luca_everything_sfx)

func play_horror_ambience_sound():
	SoundManager.play_sound(horror_ambience_sfx)

func play_luca_world_sound():
	SoundManager.play_sound(luca_world_sfx)

func stop_horror_sounds():
	SoundManager.stop_sound(luca_hear_sfx)
	SoundManager.stop_sound(luca_feel_sfx)
	SoundManager.stop_sound(luca_think_sfx)
	SoundManager.stop_sound(luca_life_sfx)
	SoundManager.stop_sound(luca_love_sfx)
	SoundManager.stop_sound(horror_ambience_sfx)
	SoundManager.stop_sound(luca_see_sfx)
	SoundManager.stop_sound(luca_everything_sfx)
	SoundManager.stop_sound(luca_world_sfx)
	continue_ingame_music()

func play_luca_bonk_sound():
	SoundManager.play_sound(luca_bonk_sfx)

func play_voice_mumble():
	SoundManager.stop_sound(voice_mumble_sfx)
	SoundManager.play_sound(voice_mumble_sfx)

func play_cheering_sound():
	SoundManager.play_sound(cheering_sfx)

func play_pog_sound():
	var pogs = [pog1_sfx, pog2_sfx, pog3_sfx]
	SoundManager.play_sound(pogs.pick_random())

func stop_cheer_sounds():
	SoundManager.stop_sound(cheering_sfx)
