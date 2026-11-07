# Curated example from EXAMPLE_phone_example.rpy (Light the Way).
# Original calls and arguments retained; dialogue/narration shortened for focus.
# Illustrative only: this is not a complete or standalone Ren'Py scene.
# The general phone UI approach was informed by an existing project.

label PhoneExample:
    $ luca_name = "Luca Kaneshiro"
    $ phone_target = luca_name
    $ nvl_mode = "phone"
    $ PhonePower = "On"

    y_phone "MC sends first message"
    l_phone "POOOOGGGG YOOOOUUU"

    $ shu_name = "Shu Yamino"
    $ phone_target = "Luca & Shu"
    nvl_narrator "[shu_name] joined the chat."
    s_phone "Hi, I'm a sorcerer and hardly even know her"

    $ phone_target = "[luca_name]"
    nvl_narrator "[shu_name] left the chat."
    $ PhonePower = "Off"

    show screen PhoneIncomingCall(luca_name) with Dissolve(0.5)
    menu:
        "Accept the call":
            hide screen PhoneIncomingCall
            show screen PhoneCall(luca_name)
            l "POOOOOOOOOOOOOO-"
            hide screen PhoneCall
        "Refuse the call":
            hide screen PhoneIncomingCall with dissolve
