# Designing Shared Systems for Other Contributors

**Ren'Py · Python · Reusable interfaces · Integration examples · Team workflows**

On *Light the Way*, I was responsible not only for implementing shared game systems, but also for helping teammates use them in their own visual novel scripts. With several story routes being developed in parallel, contributors needed clear ways to invoke common behaviors without modifying the underlying implementation.

I addressed that through reusable entry points, example `.rpy` scenes, and recordings that showed the code alongside its in-game output.

## A developer-facing workflow

The intended workflow was simple: **find an example → use the shared call in a route script → verify the behavior in Ren'Py**. Example scenes provided working usage patterns and exposed practical requirements, such as which variables needed to be set before opening a phone UI.

| Example script | What it taught contributors |
| --- | --- |
| `EXAMPLE_ending_check_example.rpy` | Record endings and query cross-route progress |
| `EXAMPLE_gallery_example.rpy` | Demonstrate image/music unlocks and gallery navigation |
| `EXAMPLE_sfxExample.rpy` | Combine looping ambient audio, music, and one-shot sound effects |
| `EXAMPLE_gpi_example.rpy` | Trigger a reusable good-choice feedback indicator |
| `EXAMPLE_phone_example.rpy` | Author messages, update chat participants, and open call screens |

These scripts were written as **teammate-facing demonstrations**, not as story content intended for release.

## Example: a shared scene-transition interface

The `scene_transition()` helper provided one call for changing a background with a fade. Internally, it temporarily hides the dialogue window and quick menu, displays the new scene, checks gallery completion, runs the transition, and restores the relevant UI.

```renpy
$ scene_transition("MC Bedroom Night", 0.5, 0.5, 0.5)
```

That call comes from an example scene; the [original helper implementation](../code/shared-interfaces/scene-transition.rpy) is included as a focused excerpt. Other developers could use the same transition behavior without repeating its sequencing in every route.

## Example: showing how to use progression APIs

The ending tutorial demonstrated how to register several outcomes and ask questions about them:

```python
add_ending("Ike", "Hope")
get_ending_count("Any", "Rainbow")
check_ending_reached("Luca", "Any")
```

The [trimmed ending tutorial](../code/contributor-examples/ending-checks-example.rpy) keeps the relevant calls and leaves out the narrated walkthrough and its demo-only persistent-data reset. The corresponding implementation is covered in the [progression-and-gallery deep dive](progression-and-gallery.md).

## The surviving phone demonstration

For the phone interface, I recorded a **side-by-side code-and-game walkthrough** showing messages, group-chat changes, and an incoming call. It illustrated which lines a teammate could write in a normal script and what those lines produced on screen. A [curated phone example](../code/contributor-examples/phone-example.rpy) preserves representative calls without reproducing the full scene.

The general phone-UI approach was informed by another project. My contribution here was adapting, implementing, integrating, and documenting it for *Light the Way*; I do not claim to have originated the concept. The recording itself is not redistributed in this source-only showcase.

## Supporting the team's workflow

I also helped teammates set up GitHub and use pull requests, and reviewed scripts written by others. That review and onboarding work supported the team's delivery process; **reviewed code is not included here as my authored source**.

## What I'd improve

The examples depended on game-specific names, global variables, screens, and assets. The original gallery and ending tutorials also contained reset operations intended only for a demonstration environment. In a future project, I'd isolate safer sample data and add small integration checks so examples could be rerun without affecting player progress.

The linked `.rpy` files are **selected, non-standalone excerpts**. They preserve relevant function calls and behaviors while omitting unrelated dialogue, art references, and other game dependencies.

[← Back to the Light the Way overview](../README.md)
