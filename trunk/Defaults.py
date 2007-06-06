##
## Defaults.py
##
## Contains the default configuration items.
##


_defaults = dict(

  mainwindow_title = "Spyrit",
  mainwindow_min_size = ( 160, 100 ),
  mainwindow_pos = None,

  show_splashscreen = False,
  mainwindow_size = ( 640, 480 ),
)


from ConfigBasket import ConfigBasket

defaults = ConfigBasket()
defaults.updateFromDict( _defaults )
