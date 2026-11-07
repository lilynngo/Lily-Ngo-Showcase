# Curated source excerpt from game-ending-declarations.rpy (Light the Way).
# Original function names and logic preserved; unrelated content omitted.
# Not runnable alone: relies on the game's Ren'Py persistent state.

init python:
    def get_ending_count(route="Any", ending="Any"):
        #returns 0 if no endings have been reached
        if persistent.all_end == None: #remember to check b/c renpy defaults to None if has not been declared
            return 0

        #returns count of how many endings have been reached (good & bad, across all the boys)
        if route == "Any" and ending == "Any": #remember to check b/c renpy defaults to None if has not been declared
            return len(persistent.all_end)

        #returns count of how many endings (good & bad) for the given route
        if ending == "Any":
            return persistent.all_end.count(route)

        #returns count of how many endings (good) for given route
        if ending == "Hope":
            if persistent.hope_end == None: #remember to check b/c renpy defaults to None if has not been declared
                return 0
            if route == "Any":
                return len(persistent.hope_end)
            return persistent.hope_end.count(route)

        #returns count of how many endings (bad) for given route
        elif ending == "Dark":
            if persistent.dark_end == None: #remember to check b/c renpy defaults to None if has not been declared
                return 0
            if route == "Any":
                return len(persistent.dark_end)
            return persistent.dark_end.count(route)

        elif ending == "Rainbow":
            if persistent.rainbow_end == None: #remember to check b/c renpy defaults to None if has not been declared
                return 0
            if route == "Any":
                return len(persistent.rainbow_end)
            return persistent.rainbow_end.count(route)

    def check_ending_reached(route, ending):
        if persistent.all_end == None:
            return False
        if ending == "Hope":
            if persistent.hope_end == None: #remember to check b/c renpy defaults to None if has not been declared
                return False
            elif route == "Any":
                return True
            return route in persistent.hope_end
        #returns count of how many endings (bad) for given route
        elif ending == "Dark":
            if persistent.dark_end == None: #remember to check b/c renpy defaults to None if has not been declared
                return False
            elif route == "Any":
                return True
            return route in persistent.dark_end
        elif ending == "Rainbow":
            if persistent.rainbow_end == None: #remember to check b/c renpy defaults to None if has not been declared
                return False
            elif route == "Any":
                return True
            return route in persistent.rainbow_end
        else:
            if route == "Any":
                return True
            return route in persistent.all_end
