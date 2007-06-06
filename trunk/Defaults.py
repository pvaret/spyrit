##
## Defaults.py
##
## Contains the default configuration items.
##


_defaults = dict(

  mainwindow_title = "Spyrit",
  mainwindow_min_height = 200,
  mainwindow_min_width = 320,
  mainwindow_pos = None,

  show_splashscreen = True,
  mainwindow_size = ( 640, 480 ),
)


from ConfigBasket import ConfigBasket

defaults = ConfigBasket()
defaults.updateFromDict( _defaults )
