class_name DoorManager extends Node2D

@onready var all_doors: Array[Node] = get_children()

func get_door(lucub: Lucub):
	var veil_name = GC.DoorsToUnlock_ByLucub[lucub.Name]
	for door in all_doors:
		door = door as Room_Door
		if door.veil_to_unlock == veil_name:
			return door
	return null
