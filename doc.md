#Display-o-tron Function Reference

##LCD

For Display-o-Tron HAT:

```python
import dothat.lcd as lcd
```

For Display-o-Tron 3000:

```python
import dot3k.lcd as lcd
```

###Methods

```python
lcd.write(value)
```
Writes a string to the LCD at the current cursor position.

You can use chr(0) to chr(7) to place custom characters and animations.

* value (string): The string to write

```python
lcd.clear()
```
Clears the display

```python
lcd.set_contrast(contrast)
```
Sets the display contrast

* contrast (int): contrast value
* Must be in the range 0 to 63

```python
lcd.set_cursor_position(column, row)
```
Sets the cursor position to column,row

* column (int): column ( horizontal ) position from 0 to 15
* row (int): row ( vertical ) position from 0 to 2

```python
lcd.create_char(char_pos, char_map)
```
Create a custom character and save into dot3k memory.

* char_pos (int): Value from 0-7
* char_map (list): LIst of 8, 8-bit integers describing the character

```python
lcd.create_animation(anim_pos, anim_map, frame_rate):
```
Create a custom animation. These are saved in the same memory locations as characters and will overwrite a slot used by create_char.

* char_pos (int): Value from 0-7, to save animation in dot3k memory
* anim_map (list): List of 8, 8-bit integers describing the animation
* frame_rate (int): Animation speed in FPS

```python
lcd.update_animations()
```
Advances all animations by one frame- this updates the character corresponding to each animation with the correct frame.

##Backlight

For Display-o-Tron HAT:

```python
import dothat.backlight as backlight
```

For Display-o-Tron 3000:

```python
import dot3k.backlight as backlight
```

###Methods

```python
backlight.use_rbg()
```
Applies to the Dot3k only. Changes the backlight driver to RBG mode ( instead of RGB ) for early Display-o-Tron boards with reversed B/G channels. Call once after importing dot3k.backlight.

```python
backlight.hue(hue)
```
Sets the backlight LEDs to supplied hue

* hue (float): hue value between 0.0 and 1.0

```python
backlight.hue_to_rgb(hue)
```
Converts a hue to RGB brightness values

* hue (float): hue value between 0.0 and 1.0

```python
backlight.left_hue(hue)
```
Set the left backlight to supplied hue

* hue (float): hue value between 0.0 and 1.0

```python
backlight.left_rgb(r, g, b)
```
Set the left backlight to supplied r, g, b colour. Will set the left-most two LEDs on DotHAT.

* r (int): red value between 0 and 255
* g (int): green value between 0 and 255
* b (int): blue value between 0 and 255

```python
backlight.mid_hue(hue)
```
Set the middle backlight to supplied hue. Will set the middle two LEDs on DotHAT.

* hue (float): hue value between 0.0 and 1.0

```python
backlight.mid_rgb(r, g, b)
```
Set the middle backlight to supplied r, g, b colour. Will set the right-most two LEDs on DotHAT.

* r (int): red value between 0 and 255
* g (int): green value between 0 and 255
* b (int): blue value between 0 and 255

```python
backlight.off()
```
Turns off the backlight.

```python
backlight.rgb(r, g, b)
```
Sets all backlights to supplied r, g, b colour

* r (int): red value between 0 and 255
* g (int): green value between 0 and 255
* b (int): blue value between 0 and 255

```python
backlight.right_hue(hue)
```
Set the right backlight to supplied hue

* hue (float): hue value between 0.0 and 1.0

```python
backlight.right_rgb(r, g, b)
```
Set the right backlight to supplied r, g, b colour

* r (int): red value between 0 and 255
* g (int): green value between 0 and 255
* b (int): blue value between 0 and 255

```python
backlight.set(index, value)
```
Set a specific LED to a value

* index (int): index of the LED from 0 to 18
* value (int): brightness value from 0 to 255

```python
backlight.set_bar(index, value)
```
Set a value or values to one or more LEDs

* index (int): starting index
* value (int or list): a single int, or list of brightness values from 0 to 255

```python
backlight.set_graph(value)
```
Lights a number of bargraph LEDs depending upon value

* value (float): percentage between 0.0 and 1.0

##Touch

For Display-o-Tron HAT only:

```python
import dothat.touch as touch
```

###Constants

Constants are defined for all the buttons, giving them friendly names like so:

```python
touch.UP
touch.DOWN
touch.LEFT
touch.RIGHT
touch.BUTTON
touch.CANCEL
```

###Methods

```python
touch.high_sensitivity()
```

Call once to enable high sensitivty mode.

```python
touch.enable_repeat(enable)
```

Pass true to enable repeat events (held buttons will re-trigger).

* enable (boolean): enable or disable repeat

```python
touch.on(buttons, bounce=1)
```

Used as a decorator to bind a function to a particular button, you should generally use it like so:

```
@touch.on(touch.LEFT)
def touch_left(channel, event):
    print(channel, event)
```

* buttons - list of, or single, button constant, one of: touch.UP, touch.DOWN, ... etc

```python
touch.bind_defaults(menu)
```

Pass an instance of a dot3k.menu class to bind all the default functions automatically for each button. This is much neater than creating your own button handlers. Binds Up, Down, Left, Right, Menu and Cancel.


************************************************************************************************************************************************************************
************************************************************************************************************************************************************************
************************************************************************************************************************************************************************
************************************************************************************************************************************************************************


# Display-o-Tron HAT Examples

Display-o-Tron HAT is the HAT version of Display-o-Tron 3000, it replaces the 3 zone RGB backlight with a whopping 6 zones, sports a 6-LED vertical bargraph and has 6 touch sensitive buttons in place of the joystick.

## Using The Touch Buttons

The example file `basic/captouch.py` demonstrates how you can use the new `captouch` library to get touch input into your projects. It's almost a drop-in replacement for the `joystick` library except that it includes one new button: `cancel`.

`cancel` is the touch button on the top left of Display-o-Tron HAT and is used for exiting menus that want to make full use of the up/down/left/right/select buttons. 

## Touch Reference

#### Import The Library

```python
import dothat.touch
```

#### Enable/disable auto-repeat

```python
dothat.touch.enable_repeat()
```

#### Enable High-Sensitivity mode

Great for using the touch buttons through a lid:

```python
dothat.touch.high_sensitivity()
```

#### Bind menu defaults

Bind all the default actions to a `dot3k.menu` instance:

```python
dothat.touch.bind_defaults(my_custom_menu)
```

#### Bind a single action

```python
@dothat.touch.on(dothat.touch.LEFT)
def handle_left(channel, event):
    print("Left Pressed!")
```

`channel` will be a number from 0 to 5 corresponding to `dothat.touch.LEFT/UP/DOWN/etc`

`event` will either be `press` or `held` depending on whether an initial touch has been detected, or a continuous hold.

## Using The Backlight

The backlight works in exactly the same was as it did on Display-o-Tron 3000, however it now has 6 zones instead of 3, for 100% more rainbow.

The methods `left_rgb`, `mid_rgb` and `right_rgb` still work, however they each control two LEDs instead of one. The recommended way to set a single RGB channel ( from 0 to 5 ) is now `single_rgb( channel, r, g, b )`.

## Backlight Reference

#### Import The Library

```python
import dothat.backlight
```

#### Set a single RGB LED

Set a single channel to an RGB colour of your choice:

```python
dothat.backlight.single_rgb(channel, r, g, b)
```

`channel` should be a number between 0 and 5, where 0 is the left-most RGB LEd and 5 is the right-most.

`r`, `g` and `b` should be numbers between 0 and 255, representing the intensity of red, green and blue light respectively.

#### Set all RGB LEDs

Set all channels to the same RGB colour:

```python
dothat.backlight.rgb(r,g,b)
```

Again, `r`, `g`, and `b` should be numbers between 0 and 255. `255,0,255` would be a lovely purple!

#### Turn all LEDS off

```python
dothat.backlight.off()
```

#### Display a percentage on the 6-LED graph

```python
dothat.backlight.set_graph(0.5) # 50%
```

Pass a number between 0 and 1 to set all the graph LEDs either on, off, or somewhere in between.

#### Set a single LED

```python
dothat.backlight.set(channel, brightness)
```

`channel` should be a value from 0 to 18. The LED channels go in the order: `bgrbgrbgrbgrbgrbgr`
