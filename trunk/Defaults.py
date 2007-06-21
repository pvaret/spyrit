##
## Defaults.py
##
## Contains the default configuration items.
##


_defaults = dict(

  app_name            = "Spyrit",
  app_version         = "0.1",
  mainwindow_min_size = ( 160, 100 ),
  mainwindow_pos      = None,
  worlds_section      = "Worlds",

  show_splashscreen = False,
  mainwindow_size   = ( 800, 600 ),

  output_font_name  = "Courier",
  output_font_size  = 12,
  output_font_color = "#a0a0a4",  ## grey

  bold_as_highlight = True,

  info_font_color   = "#606060",  ## dark grey

  input_font_name  = "",  ## Nothing, system default will be used.
  input_font_size  = 0,   ## Nothing, system default will be used.
  input_font_color = "",  ## Nothing, system default will be used.

  output_background_color = "#000000",  ## black
  input_background_color  = "#ffffff",  ## white

  splitter_sizes = [ 1000, 100, 100 ],

)


from ConfigBasket import ConfigBasket

defaults = ConfigBasket()
defaults.updateFromDict( _defaults )
