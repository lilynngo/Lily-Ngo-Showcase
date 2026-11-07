# Curated source excerpt from Gallery.rpy (Light the Way).
# Original function names and logic preserved; screen layout and art paths omitted.
# Not runnable alone: requires gallery globals, asset registries, and MusicRoom.

init python:
    def switch_tab(tab):
        global gallery_tab_name
        global gallery_filter
        global gallery_page
        if gallery_filter == "General" and tab == "CG":
            gallery_filter = "All"
        gallery_tab_name = tab
        gallery_page = 1

    def switch_filter(g_filter):
        global gallery_filter
        global gallery_page
        gallery_page = 1
        gallery_filter = g_filter

    def get_max_page():
        global gallery_page
        global gallery_filter
        global gallery_tab_name
        if gallery_tab_name == "BGM":
            gal_list = list(musicDictionary.keys())
        else:
            gal_tab = persistent.imagesGallery[gallery_tab_name]
            if len(gal_tab) <= 1:
                return 1
            gal_list = gal_tab[gallery_filter]

        max_page = (int(len(gal_list)/6) + (len(gal_list) % 6 > 0))
        if max_page < 1:
            return 1
        return max_page

    def switch_song(song2Play):
        global current_song_playing
        music_room.play(song2Play.file)
        current_song_playing = song2Play
