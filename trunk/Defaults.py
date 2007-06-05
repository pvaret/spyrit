##
## Defaults.py
##
## Contains the default configuration items.
##


_defaults = dict(
  show_splashscreen = True,
  mainwindow_size = ( 640, 480 ),
)


from ConfigBasket import ConfigBasket

defaults = ConfigBasket()
defaults.updateFromDict( _defaults )
