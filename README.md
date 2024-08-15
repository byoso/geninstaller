# Geninstaller (for linux)

## Ubuntu 24 and derivated: Now needs to add --break-system-packages on install.

_Universal linux installer system_
Installs applications in the user's space.


## For developers and common users

### Common users
The applications installed with __geninstaller__ are registrated in a small database.
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

#### Installation
```
$ pip install geninstaller --break-system-packages
```
Note that `--break-system-packages` allows to bypass the protection of Ubuntu 24, be sure you don't install nested dependencies that should be dangerous for your system. Geninstaller will install 2 additionnal PyPI libs: `silly-db` and `flamewok`, you may need to install them manually on Ubuntu 24+. A v2 is in progress and will get rid of this 2 dependencies.

#### Get an 'installer' template
```
$ geninstaller plop installer
```
Geninstaller provides you an 'installer' file in your current working directory, you can join it to your projects. You just have to open it and change a few settings to adapt it to your application (the comments in the file will guide you).

The installer script is in python, but works for any kind of program to install.

And that's all, __no requirements for the final user__, fast and easy.

Behind this, the 'installer' script will take care of the requirements, and install the geninstaller database on the system.

#### Limitation (and gain)
Geninstaller only installs applications in the user's space (no sudo required), the gain is that it makes it compatible with any linux distibution. So, if your application needs to be installed 'system wide', geninstaller is not the tool that you need.

# Change log

- 1.2.4: "--break-system-packages" added in the provided installer to bypass ubuntu 24 limitation.