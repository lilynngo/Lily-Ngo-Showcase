
class_name CharacterAssets
extends RefCounted

const BASE_PATH = "res://assets/characters/"
const THUMBNAIL_PATH =  "res://assets/characters/thumbnails/"


const CHARACTERS = {
	"king_marcello": {
		"base_path": BASE_PATH + "king_marcello",
		"psd_file_name": "art_character_king_marcello",
		"image_type": "webp",
		"back": {
			"hair": "hair"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_back": {
			"garment": "garment"
		},
		"lower_bottom": {
			"left_leg": "left_leg",
			"right_leg": "right_leg",
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso",
			"collar": "collar"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "hand"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"cane": "cane",
			"hand":"hand"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	},
	"queen_serafina": {
		"base_path": BASE_PATH + "queen_serafina",
		"psd_file_name": "art_character_queen_serafina",
		"image_type": "webp",
		"back": {
			"hair": "hair",
			"hair_ribbon": "hair_ribbon"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_bottom": {
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "arm"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"hand":"arm"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	}, 
	"princess_lucia": {
		"base_path": BASE_PATH + "princess_lucia",
		"psd_file_name": "art_character_princess_lucia",
		"image_type": "webp",
		"back": {
			"hair": "hair",
			"hair_ribbon": "hair_ribbon"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_bottom": {
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "arm"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"hand":"arm"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	}, 
	"prince_oliver": {
		"base_path": BASE_PATH + "prince_oliver",
		"psd_file_name": "art_character_prince_oliver",
		"image_type": "webp",
		"back": {
			"hair": "hair",
			"hair_ribbon": "hair_ribbon"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_bottom": {
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "arm"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"hand":"arm"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	}, 
	"melissa_cutwater": {
		"base_path": BASE_PATH + "melissa_cutwater",
		"psd_file_name": "art_character_melissa_cutwater",
		"image_type": "webp",
		"back": {
			"hair": "hair",
			"hair_ribbon": "hair_ribbon"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_bottom": {
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "arm"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"hand":"arm"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	}, 
	"count_holloway": {
		"base_path": BASE_PATH + "count_holloway",
		"psd_file_name": "art_character_count_holloway",
		"image_type": "webp",
		"back": {
			"hair": "hair",
			"hair_ribbon": "hair_ribbon"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_bottom": {
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "arm"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"hand":"arm"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	}, 
	"comodoro_ferreira": {
		"base_path": BASE_PATH + "comodoro_ferreira",
		"psd_file_name": "art_character_comodoro_ferreira",
		"image_type": "webp",
		"back": {
			"hair": "hair",
			"hair_ribbon": "hair_ribbon"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_bottom": {
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "arm"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"hand":"arm"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	}, 
	"lord_weatherby": {
		"base_path": BASE_PATH + "lord_weatherby",
		"psd_file_name": "art_character_lord_weatherby",
		"image_type": "webp",
		"back": {
			"hair": "hair",
			"hair_ribbon": "hair_ribbon"
		},
		"head": {
			"mouth": "face_mouth", #can add an expression
			"head_base": "head_base",
			"nose": "face_nose", #can add an expression
			"eyes": "face_eyes", #can add an expression
			"eyelids": "face_eyelids", #can add an expression
			"blush": "face_blush", #can add an expression
			"brows": "face_brows"
		},
		"lower_bottom": {
			"garment": "garment"
		}, 
		"upper" :{
			"torso": "torso"
		}, 
		"upper_right": {
			"sleeve": "sleeve",
			"hand": "arm"
		}, 
		"upper_left": {
			"sleeve": "sleeve",
			"hand":"arm"
		},
		"upper_accessories": {
			"necklace": "necklace"
		},
		"front": {
			"hair":"hair"
		}
	}
}
