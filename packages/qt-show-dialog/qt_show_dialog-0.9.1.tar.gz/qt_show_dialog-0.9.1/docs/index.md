# Show Dialog
Easily show a dialog window for miscellaneous purposes.

The initial use case is to show instructions in manual steps in tests.

See [features](#features) and [example](#example) for quick details.

## Getting started
### Installation
#### Library
```
pip install qt-show-dialog
```

```python
from show_dialog import show_dialog, Inputs

def test_manual():
    show_dialog(Inputs(
        title='The Title',
        description='The Description',
        timeout=10
    ))
```

#### CLI
After installing the `qt-show-dialog`, the `show_dialog` command becomes available in the terminal
(Command Line Interface).
```
show_dialog --help
```
Quick example:
```
show_dialog --inputs '{"title": "The Title", "description": "The Description", "timeout": 10}'
```
The options using the CLI are the same as when using the library.

#### Executable app
Go to the [release](https://github.com/joaonc/show_dialog/releases/latest) page and download the
file for your OS.

You can use the executable when working with languages other than Python or when you don't want to
add more dependencies to your project (see
[requirements.in](https://github.com/joaonc/show_dialog/blob/main/requirements.in) for a list of
dependencies).

See the [CLI](#cli) section above for more info. The interface is the same.

#### Pipx
[Pipx](https://pipx.pypa.io/stable/) installs Python applications globally in an isolated
environment, meaning the Python app will run as any other app installed in the OS.

To install with pipx (note that pipx needs to be installed first):
```
pipx install qt-show-dialog
```
To later upgrade to a newer version:
```
pipx upgrade qt-show-dialog
```

The command `show_dialog` will be available in the terminal. See the [CLI](#cli) section above for
more info.

### Use case
#### Testing
The main use case for which this project was created is to add in manual steps in tests.

```python
from show_dialog import Inputs, show_dialog
from show_dialog.utils_qt import read_file

def test_something():
    """
    This test case is semi-automated, ie, has some steps that
    are automated and then some manual ones.
    This happens mostly in integration or end-to-end tests.
    """
    # Some automated steps
    start_system()
    configure_system()

    # Manual step
    inputs_1 = Inputs.from_file('tests/inputs/input_10.yml')
    css = read_file('my_custom_style.css')
    show_dialog(inputs_1, css)

    # More automated steps
    verify_db_updated()
    
    # Another manual step
    inputs_2 = inputs_1.create(
      title='Submit readout',
      description='Submit the readout by uploading the file.'
    )
    show_dialog(inputs_2, css)
    
    # More automated steps
    verify_readout()
```

#### Script
The dialog can also be shown in a script (bash, bat, powershell) or any other (non-Python) language
that can run an executable.

```shell
#!/bin/bash

# Do some stuff

# Show the dialog
./show_dialog --inputs \
    '{"title": "The Title", "description": "The Description", "timeout": 10}'

# Handle the exit status
status=$?
if [ $status -ne 0 ]; then
    echo "show_dialog exited with status $status"
    exit $status
fi

# Do more stuff
```

## Features

* Big UI (by default) for easy readability.
* UI highly configurable via CSS and options.
* Timeout (optional).
* Can be used as a library or an external executable.
* Inputs can be in `yaml` or `json`, from file or string.
* Logging.

## Example
The example below has this `yaml` input:
```yaml
dialog_title: Manual step
title: Disconnect cable
description: |
    In this step we need to disconnect the power cable  
    and verify that the reserve battery gets discharged  
    within 5 seconds.
    
    ## Steps
    1. Disconnect power cable.  
       It's in the back.
    2. Wait 5 seconds.
    3. Check that reserve battery is empty.  
       See below for more info.

    ## Verifying battery is discharged
    There's a red light that goes off.
    
    **Do not touch** the button next to that light.
    
    More info on that light [here](#some-path).
description_md: true
timeout: 20
```
!!! Note

    * Description is in markdown format.
    * Some lines have a line break with 2 spaces at the end.  
      This applies to most MD formats.
    * Many options _not_ represented in this example.

![ShowDialog example](images/show_dialog_example.png)

