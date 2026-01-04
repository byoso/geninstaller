# Geninstaller (for linux)

_Universal linux installer system_
Installs applications in the user's space.

**please read the changelog** at the bottom.

Geninstaller is usually stable, but if you have some issue with geninstaller, try to completely uninstall it and re-install a newer version.

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

#### How to completely remove Geninstaller ?

[follow this steps](doc/uninstalling_geninstaller.md)


## Changelog
- 2.1.0:
    - pre/post installation scripts and pre uninstall script are working
- 2.0.9:
    - fixed a bug in the installer's error messages (if missing pipx or geninstaller)
- 2.0.8:
    - fixed a bug in the installer with python > 3.12
- 2.0.7:
    - now works with python 3.10+
- 2.0.6:
    - geninstaller's folder is now ~/.local/share/geninstaller-applications and not ~/.local/share/applications-files anymore
- 2.0.0:
    - BROKEN (should not work on new install, please uninstall and upgrade to 2.0.5)
    - python version issue: works only with python 3.12+
    - Geninstaller 2 is NOT compatible with the previous Geninstaller, please remove the former one (pip uninstall geninstaller) before using version 2.x.x
    - geninstaller uses no more third party dependencies.
    - python programs are installed with their own virtual env when they require third party libs.
    - geninstaller should be installed with 'pipx install geninstaller'.
