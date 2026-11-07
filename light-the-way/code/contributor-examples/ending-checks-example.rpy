# Curated example from EXAMPLE_ending_check_example.rpy (Light the Way).
# Original API calls retained; tutorial narration and persistent-data reset omitted.
# Illustrative only: not a complete or standalone Ren'Py scene.

label ending_explained:
    python:
        add_ending("Ike", "Hope")
        add_ending("Vox", "Dark")
        add_ending("Mysta", "Dark")
        add_ending("Mysta", "Hope")
        add_ending("Luca", "Rainbow")

        all_endings = get_endings()
        hope_endings = get_endings("Hope")
        dark_endings = get_endings("Dark")
        rainbow_endings = get_endings("Rainbow")

    python:
        reached_any_luca_ending = check_ending_reached("Luca", "Any")
        reached_hope_vox_ending = check_ending_reached("Vox", "Hope")
        ending_count = get_ending_count()
        luca_ending_count = get_ending_count("Luca")
        mysta_hope_ending_count = get_ending_count("Mysta", "Hope")
        vox_hope_ending_count = get_ending_count("Vox", "Hope")
        rainbow_ending_count = get_ending_count("Any", "Rainbow")
