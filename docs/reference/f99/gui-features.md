# OEM software feature baseline

This page records what the AULA OEM configuration software can do. It is a
baseline for comparison.

Source: screenshots of the OEM software, supplied 2026-08-11. Items marked
"Unconfirmed" could not be read reliably from the screenshots.

The vendor states that macros, custom key functions, and the
music-reactive lighting all need this software. The firmware alone does
not provide them. The `FN` shortcuts in
[keybindings.md](keybindings.md) are what the firmware provides on its
own.

## Screens

The software has four main screens. Each screen uses the same layout: a
list panel on the left, a keyboard preview in the middle, and a control
panel at the bottom.

| Screen | Purpose |
| --- | --- |
| Light effect | Pick a lighting effect. Set its color, brightness, and speed. |
| Effect (music) | Pick a sound-reactive lighting effect. Set its gain and smoothness. |
| Key assignment | Remap keys, per layer and per profile. |
| Macro edit panel | Record and edit macros. |

The keyboard preview shows the current per-key colors. A save button
(floppy icon) writes the current settings to the keyboard.

## Light effects

The effect list holds 15 selectable effects plus an `OFF` entry.

| Effect | Speed control |
| --- | --- |
| Fixed_on | No |
| Respire | Unconfirmed |
| Rainbow | Unconfirmed |
| Flash_away | Unconfirmed |
| Raindrops | Unconfirmed |
| Ripples_shining | Unconfirmed |
| Stars_twinkle | Yes |
| Retro_snake | Unconfirmed |
| Neon_stream | Unconfirmed |
| Reaction | Unconfirmed |
| Sine_wave | Unconfirmed |
| Rotating windmill | Unconfirmed |
| Colorful waterfall | Unconfirmed |
| Blossoming | Unconfirmed |
| Self-define | Unconfirmed |
| OFF | No |

`Fixed_on` shows a Brightness slider only. `Stars_twinkle` shows both
Brightness and Speed. The software appears to show the Speed slider only
for animated effects. This rule is inferred from two samples. It is not
confirmed for the other effects.

`Self-define` is assumed to be the per-key custom mode. Its editing
controls were not captured. The keyboard does have per-key RGB in
hardware, so a per-key mode is possible. See
[hardware.md](hardware.md#lighting-hardware).

These effects light the keys only. The keycaps are not shine-through, so
no effect lights a legend. The RGB ambient light bar has its own separate
controls, which this screen does not show.

## Music-reactive effects

A separate screen holds sound-reactive effects. Its caption reads: the
keyboard light changes with the rhythm of the system sound. A single
OFF/ON toggle enables the whole mode.

Each effect name carries a mood or genre suffix.

| Effect | Suffix |
| --- | --- |
| Audio dance | soft |
| Dazzling | rock |
| Clouds rise and snow fly | routine |
| Light Field Change | voice |
| The gurgling stream | regular |
| Blooming | passion |
| Pearl falling jade plate | rock |
| Clouds follow the moon | passion |
| Mountains and Flowing Waters | regular (Unconfirmed -- name truncated in the screenshot) |
| Raining like silk | regular |

The suffixes take six distinct values: `soft`, `rock`, `routine`, `voice`,
`regular`, and `passion`. Both the product manual and the vendor listing
state that this feature has five modes. Neither count matches the ten
effects and six suffixes seen in the software. See
[Open questions](#open-questions).

Controls for this screen:

| Control | Observed value | Range |
| --- | --- | --- |
| Gain factor | 1.0 | Unconfirmed. Uses one decimal place. |
| Smoothness | 4 | Unconfirmed. Whole numbers. |

## Color controls

Both lighting screens share the same color panel.

| Control | Behavior |
| --- | --- |
| Color wheel | Pick a color by clicking the wheel. |
| Hex field | Shows the color as a 6-digit hex value. |
| R, G, B sliders | Set each channel from 0 to 255. Each slider has a numeric box. |
| Preset swatches | 8 fixed colors: red, orange, yellow, green, blue, cyan, magenta, white. |
| Custom color | 10 user-defined slots, in 2 rows of 5. An "Add" link saves the current color to a slot. |
| Color | Shows the currently selected color. |
| Colourful | A checkbox. Labelled "Colourful" on the light-effect screen and "ColorFull" on the music screen. |

Brightness observed at values 2 and 4. Speed observed at value 4. The
maximum for each is unconfirmed. The slider positions suggest a 0-to-5
range, but this needs a check against the software.

### Hex field byte order

The hex field and the RGB sliders disagree in one screenshot. The field
reads `# 0000FF`. The sliders read R=255, G=0, B=0. The colour swatch is
red.

Read as `RRGGBB`, the hex value means blue. That contradicts the sliders.
Read as `BBGGRR`, it means red. That matches the sliders and the swatch.

This suggests the field prints the bytes in `BBGGRR` order. Two other
screenshots (`FFFFFF` and `00FF00`) are the same value in both orders, so
they do not settle it. This may also be a display bug in the OEM software.
Treat the finding as unconfirmed.

## Key assignment

| Element | Behavior |
| --- | --- |
| Device | Selects the target device. Only "Keyboard" was observed. |
| Profile | A named set of key assignments. The list held one profile, "default". |
| Profile toolbar | Export, import, rename, delete, and add. |
| Layer tabs | Four layers: `Default`, `FN1`, `FN2`, `Tap`. Each tab has a dropdown. |
| Keyboard preview | Shows which keys carry an assignment on the active layer. |
| Save / Reset | A save button and a reset button. |

To remap a key, select a layer, click a key in the preview, then pick a
new action from the tabbed picker below.

### Action picker

The picker has six tabs.

| Tab | Contents |
| --- | --- |
| Keyboard | Standard keycodes. See the groups below. |
| Mouse | Unconfirmed. Contents not captured. |
| Multimedia | Unconfirmed. Contents not captured. |
| Macro | Assigns a saved macro to the key. Contents not captured. |
| Commands | Unconfirmed. Contents not captured. |
| Key combination | Unconfirmed. Contents not captured. |

The Keyboard tab groups its keycodes into four blocks.

| Group | Contents |
| --- | --- |
| Comm | `A`-`Z`, `0`-`9`, `-`, `=`, `[`, `]`, `\`, `;`, `'`, `` ` ``, `,`, `.`, `/`, `FN`, `FN2` |
| Adv | `F1`-`F12`, `Esc`, `Tab`, `App`, `Ins`, `End`, `Del`, `PgDn`, `PgUp`, `Back`, `Home`, `CapsLk`, `Pause`, `Enter`, `Space`, `Print`, `ScrollLk`, `Left`, `Right`, `Up`, `Down` |
| Keypad | `Num0`-`Num9`, `Num +`, `Num -`, `Num *`, `Num /`, `Num .`, `Enter`, `NumLk` |
| Modify | `LCtrl`, `LShift`, `LAlt`, `LWin`, `RCtrl`, `RShift`, `RAlt`, `RWin` |

## Macros

The macro screen has a group tree on the left and an event list on the
right.

| Element | Behavior |
| --- | --- |
| Group tree | Macros sit inside named groups. One group, "gaming", held one macro, "zoom1". |
| Group toolbar | Export, import, copy, rename, delete, and add. |
| Event list | The ordered steps of the selected macro. Double-click a step to edit it. |
| Event toolbar | Save, delete, and add. |
| Record | Captures key presses into the event list. |

Each event holds three fields.

| Field | Meaning |
| --- | --- |
| Key | The key the event applies to, for example `Ctrl`. |
| Direction | A down arrow for press. An up arrow for release. |
| Delay | The wait after this event, in milliseconds. |

Press and release are separate events. This lets a macro hold a key down
while it sends other keys.

## Open questions

These points need a check against the OEM software or the keyboard:

1. Does the "Colourful" checkbox override the picked color with a
   multi-color pattern? Does it disable the color picker?
2. What are the maximum values for Brightness, Speed, Gain factor, and
   Smoothness?
3. Is the hex field really in `BBGGRR` order, or is the mismatch a
   display bug?
4. What does the `Tap` layer do? Does it hold a tap-versus-hold action?
5. The manual and the vendor listing both state five music-reactive
   modes. The software lists ten effects across six suffix values. Which
   count is correct?
6. What actions do the `Commands` and `Key combination` tabs offer?
7. How does `Self-define` set per-key colors? The hardware supports
   per-key RGB, so this is the mode that would use it.
