# Curated source excerpt from backgroundAssets.rpy (Light the Way).
# Function body preserved; surrounding image/CG registrations omitted.
# Not runnable alone: depends on Ren'Py, game UI state, and gallery checks.

init python:
    def scene_transition(sceneName, fadeDuration, blackDuration, pauseDuration=0, ReOpenWindow=True, ReOpenQuickMenu=True):
        global quick_menu
        store._window = False
        quick_menu = False
        renpy.scene()
        renpy.show(sceneName)
        if not achievement.has("Ace of All Trades"):
            check_cg_status()
        renpy.with_statement(Fade(fadeDuration, blackDuration, fadeDuration))
        renpy.pause(pauseDuration)
        if(ReOpenWindow):
            store._window = True
        if(ReOpenQuickMenu):
            quick_menu = True
        renpy.pause(0.25)
