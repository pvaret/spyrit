##
## Defaults.py
##
## Contains the default configuration items.
##


_defaults = dict(

  app_name = "Spyrit",
  mainwindow_min_size = ( 160, 100 ),
  mainwindow_pos = None,
  worlds_section = "Worlds",

  show_splashscreen = False,
  mainwindow_size = ( 640, 480 ),
)


from ConfigBasket import ConfigBasket

defaults = ConfigBasket()
defaults.updateFromDict( _defaults )
