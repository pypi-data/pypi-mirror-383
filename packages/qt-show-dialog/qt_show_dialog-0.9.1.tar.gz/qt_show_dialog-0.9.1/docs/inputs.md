# Inputs
Inputs are defined in the
[`Inputs`](https://github.com/joaonc/show_dialog/blob/main/src/show_dialog/inputs.py) class.

This class is serialized to/from file as JSON or YAML with the exact same fields.

# Formatting

## Buttons
Which buttons and text to be used.

Options:

* `Ok`  
  No icon is displayed unless `pass_button_icon` is set.
* `Pass/Fail` (default)
* `Ok/Cancel`
* `Yes/No`

With all options, the buttons can be further customized with these settings:

* `pass_button_text`
* `pass_button_icon`
* `fail_button_text`
* `fail_button_icon`

## Theme
Themes are styles and portions of it can be overwritten with other styling options.

Options:

* `Light`
* `Dark`
* `System`  
  No theme is applied and uses the system theme.
