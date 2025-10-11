# Development
Uses [Qt 6](https://www.qt.io) and [Qt for Python](https://wiki.qt.io/Qt_for_Python), aka _PySide_,
which includes _Qt Designer_, a WYSIWYG UI editor.

Docstrings are in [reStructuredText](https://docutils.sourceforge.io/rst.html) format.

## Contributing
### Requirements
```
pip install -r requirements-dev.txt
```

[PySide6](https://pypi.org/project/PySide6/) ([docs](https://wiki.qt.io/Qt_for_Python)) has a few
requirements. Details [here](https://code.qt.io/cgit/pyside/pyside-setup.git/about/#requirements).

#### GitHub CLI
This project uses [GitHub CLI](https://cli.github.com/) ([docs](https://cli.github.com/manual/))
to manage releases.

You'll need to install and authenticate `gh` in order to perform the release tasks.  
To install, download the file in the link above and follow the instructions.

Authenticate with this command:
```
gh auth login
```

??? Note "Sample output"

    Sample output from login with the `HTTPS` protocol and via web browser.
    ```
    gh auth login
    ? What account do you want to log into? GitHub.com
    ? What is your preferred protocol for Git operations on this host? HTTPS
    ? Authenticate Git with your GitHub credentials? Yes
    ? How would you like to authenticate GitHub CLI? Login with a web browser

    ! First copy your one-time code: 9999-9999
    Press Enter to open github.com in your browser... 
    ✓ Authentication complete.
    - gh config set -h github.com git_protocol https
    ✓ Configured git protocol
    ✓ Logged in as <GH username>
    ```

You can authenticate in other ways, see
[docs](https://cli.github.com/manual/gh_auth_login) for more info.

### Linting and Tests
Linting and unit tests are done as actions in GitHub, but should be executed locally with the
following commands:
```
inv lint.all
```
```
inv test.unit
```
If using an IDE such as PyCharm or VS Code, the tests can be executed from within the IDE.

Note that pytest options are in `pyproject.toml`, in the `[tool.pytest.ini_options]` section and
linting options are also in `pyproject.toml` and `setup.cfg`.

### Running
Running the code from the CLI or from the IDE needs be done as a module.  
If trying to run as a script, the relative imports won't work.

#### CLI
With an inputs file and log level specified.
```
python -m src.show_dialog.main --inputs-file assets/inputs/inputs_07.yaml --log-level debug
```

#### IDE
This section has screenshots from PyCharm. VS Code and other IDEs should have similar options.

When running from the IDE, make sure you specify to run `main` as a module, not a script.

![Module](images/run_main_module.png)

Here are the full options, including parameters.  
The working directory should be the project root, not the directory where `main.py` is located.

![Main](images/run_main_config.png)

## Build and Publish
There are two deliverables in this project: the library and the executable app.

This section goes over how to build the app, create a release in GitHub and publish to Pypi.

### Manually
1. Bump version
   ```
   inv build.version --mode pr
   ```
   This will:
   1. Update the necessary files to the new version.
   2. Create and merge a new PR called _"Release 1.2.3"_.  
      Use different values `--mode` for different behaviors, ex don't create a PR.

2. Create release in GitHub
   ```
   inv build.release
   ```
   Releases are published in GitHub, under the
   [Releases](https://github.com/joaonc/show_dialog/releases) page.  
   A tag is also created.

   Use the `--notes` or `--notes-file` to add more details to the release.  

  !!! Note "Recommended command"

      Create the file `release_notes.md` and _don't_ add it to the project (it's in `.gitignore`, so
      you should be ok).

      ```
      inv build.release --notes-file release_notes.md
      ```

3. Publish to Pypi
   ```
   inv build.publish
   ```

  !!! Note

      There's a similarly named project in Pypi called
      [`showdialog`](https://pypi.org/project/showdialog/), so the initially chosen names of
      `show-dialog` and `show_dialog` were not possible due to the similar name and Pypi didn't
      allow it, so ended up with the current `qt-show-dialog`.

4. Upload app to GitHub release

   This step is optional, but recommended. Each build (one per OS) is close to 50MB.
   ```
   inv build.app
   inv build.upload
   ```
   You can also use the _Build app_ GitHub action to create the app in any OS. See the
   [CI/CD](#cicd) section below.

### CI/CD
There are two different GitHub actions to handle the build/release/publish process.

#### Release
This action does steps 1-3 described in the [Manually](#manually) section.

1. Update version in required files.
2. Create and merge a PR with the updated files.
3. Create a GitHub release and tag.

To run the _Release_ action:

1. In the [Actions tab](https://github.com/joaonc/show_dialog/actions), select the
[Release](https://github.com/joaonc/show_dialog/actions/workflows/release.yml) workflow.
2. Click _Run workflow_.
3. Leave the `main` branch selected.
4. Select the version to bump.
5. Select whether to create a release in GitHub.
6. If creating a release in GitHub, add release notes.  
   When doing this step manually, a release notes file can be specified and include more
   information and in MD format.
7. Select whether to publish to Pypi.
8. Click _Run workflow_.

The version for both the GitHub release and Pypi package is defined in
`pyproject.toml::project::version` and `src/show_dialog/__init__.py::__version__`. They need to
match or the action will fail.

![Release workflow](images/gh_action_release.png)

#### Build App
This action does step 4 described in the [Manually](#manually) section, but any OS can be selected
(whereas manually is only in the OS in which the tasks are executed).

To run the _Build app_ action:

1. In the [Actions tab](https://github.com/joaonc/show_dialog/actions), select the
[Build app](https://github.com/joaonc/show_dialog/actions/workflows/build-app.yml) workflow.
2. Click _Run workflow_.
3. Select the tag (version) to build the app(s) for.  
   By default is `main`, which works, but is not what we want as an app may be created with 
   functionality not in the release if `main` has new commits.
4. Select which OS's to build the apps for.  
   The apps will be added to the assets in the release corresponding to the tag in the previous
   step.
5. Click _Run workflow_.

![Build app workflow](images/gh_action_build_app.png)

## More info
[Managing releases in a repository](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
