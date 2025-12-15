# Uninstalling completelly Geninstaller

In case you have the crazy idea of getting rid of geninstaller, it is easy to do so, just follow this steps.

## uninstall the installed apps

The installed apps will still work without geninstaller, but it will be a pain to uninstall them without geninstaller.

So you may want to uninstall the apps installed with geninstaller first, the simpliest way is to use the gui.
install the gui: `geninstaller gui` then find the geninstaller_gui witin your installed apps and use it to clear all the apps, finishing by itself.

or you can do it with the terminal: `geninstaller list` to list them all, then for each app `geninstaller uninstall "<the name of the app>"`

**remember to uninstall the gui before uninstalling geninstaller totally** if you installed it: `geninstaller uninstall geninstaller_gui`

## uninstall geninstaller itself

`pipx uninstall geninstaller` for version 2.x.x or `pip uninstall geninstaller` for version 1.x.x (you can do both with no harm if not sure)

then:
```sh
cd ~/.local/share
rm -rf applications-files # for version 1.x.x
rm -rf geninstaller-applications # for version 2.x.x
```

you're done ! :)
