# Curated source excerpt from achievements.rpy (Light the Way).
# Original function names and logic preserved; achievement declarations omitted.
# Not runnable alone: requires Ren'Py's achievement API and game UI/resources.

init python:
    def grant_achievement(title):

        if persistent.achievement_count == None:
            persistent.achievement_count = 0
        #$grant_achievement("[title of achievement]")
        if not achievement.has(title):
            persistent.achievement_count += 1
            renpy.sound.play(notification_cur_ach,channel="sound", relative_volume=0.5)
            achievement.grant(title)
            renpy.call_screen("new_ach")
            if not achievement.has("Time Traveler"):
                hasAllAchievements()

            #check if obtained all achievements



        #add code to initiate announcement
    def hasAllAchievements():
        if persistent.achievement_count < 29:
            return False

        achievement.grant("Time Traveler")
        persistent.achievement_count += 1
        if persistent.achievement_count > 30:
            persistent.achievement_count = 30
        return True
