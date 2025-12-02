# Geninstaller (for linux)

_Universal linux installer system_
Installs applications in the user's space.


## For developers and common users

### Installation

```
$ pipx install geninstaller
```

### Common users
The applications installed with **geninstaller** are registrated in a small database.
The easiest way to list or uninstall them is to install the gui first:
```
$ geninstaller gui
```
Now you have 'Geninstaller gui' in your system's programs (system), use it as any application.

You can still use the CLI if you want

List the installed applications:

```
$ geninstaller list
```
uninstall your geninstaller applications:
```
$ geninstaller uninstall 'application name'
```
And other stuff, see:
```
$ geninstaller --help
```

### Developers

#### Get an 'installer' template
```
$ geninstaller plop installer
```
Geninstaller provides you an 'installer' file in your current working directory, you can join it to your projects. You just have to open it and change a few settings to adapt it to your application (the comments in the file will guide you).

The installer script is in python, but works for any kind of program to install.

Behind this, the 'installer' script will take care of the requirements, and install the geninstaller database on the system.

#### Limitation (and gain)
Geninstaller only installs applications in the user's space (no sudo required), the gain is that it makes it compatible with any linux distibution. So, if your application needs to be installed 'system wide', geninstaller is not the tool that you need.


## Changelog

- 2.0.0:
    - Geninstaller 2 is NOT compatible with the previous Geninstaller, please remove the former one (pip uninstall geninstaller) before using version 2.x.x
    - geninstaller uses no more third party dependencies.
    - python programs are installed with their own virtual env when they require third party libs.
    - geninstaller should be installed with 'pipx install geninstaller'.

## known issues to fix

- program names that contain a space can not be uninstall with the CLI (quick solution: use the GUI instead of the CLI)