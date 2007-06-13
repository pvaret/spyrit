##
## Defaults.py
##
## Contains the default configuration items.
##


_defaults = dict(

  app_name            = "Spyrit",
  mainwindow_min_size = ( 160, 100 ),
  mainwindow_pos      = None,
  worlds_section      = "Worlds",

  show_splashscreen = False,
  mainwindow_size   = ( 800, 600 ),

  output_font_name  = "Courier",
  output_font_size  = 11,
  output_font_color = "#a0a0a4",  ## grey
  info_font_color   = "#606060",  ## dark grey
  output_background_color = "#000000", ## black

)


from ConfigBasket import ConfigBasket

defaults = ConfigBasket()
defaults.updateFromDict( _defaults )
