# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## Globals.py
##
## This file describes various bits of global data.
##

u"""
:doctest:

>>> from Globals import *

"""

from PyQt5.QtGui import QColor
from PyQt5.QtGui import QTextFormat


class FORMAT_PROPERTIES:

  ## Format property identifiers are defined on the basis of Qt properties.
  ## This saves us time when we apply them during the rendering process.

  BOLD       = QTextFormat.FontWeight
  ITALIC     = QTextFormat.FontItalic
  UNDERLINE  = QTextFormat.TextUnderlineStyle
  COLOR      = QTextFormat.ForegroundBrush
  BACKGROUND = QTextFormat.BackgroundBrush
  HREF       = QTextFormat.AnchorHref
  REVERSED = None
  BLINK    = None


class ANSI_COLORS:

  ## Dark colors:

  black     = "#000000"
  red       = "#800000"
  green     = "#008000"
  yellow    = "#808000"
  blue      = "#000080"
  magenta   = "#800080"
  cyan      = "#008080"
  lightgray = "#c0c0c0"

  ## Light colors:

  darkgray  = "#808080"
  red_h     = "#ff0000"
  green_h   = "#00ff00"
  yellow_h  = "#ffff00"
  blue_h    = "#0000ff"
  magenta_h = "#ff00ff"
  cyan_h    = "#00ffff"
  white     = "#ffffff"



## ANSI colors for 256 color terminals:

ANSI_COLORS_EXTENDED = {

  ## Base colors:
  0: ANSI_COLORS.black,
  1: ANSI_COLORS.red,
  2: ANSI_COLORS.green,
  3: ANSI_COLORS.yellow,
  4: ANSI_COLORS.blue,
  5: ANSI_COLORS.magenta,
  6: ANSI_COLORS.cyan,
  7: ANSI_COLORS.lightgray,
  8: ANSI_COLORS.darkgray,
  9: ANSI_COLORS.red_h,
  10: ANSI_COLORS.green_h,
  11: ANSI_COLORS.yellow_h,
  12: ANSI_COLORS.blue_h,
  13: ANSI_COLORS.magenta_h,
  14: ANSI_COLORS.cyan_h,
  15: ANSI_COLORS.white,

  ## Extended colors:
  16: "#000000",
  17: "#00005f",
  18: "#000087",
  19: "#0000af",
  20: "#0000d7",
  21: "#0000ff",
  22: "#005f00",
  23: "#005f5f",
  24: "#005f87",
  25: "#005faf",
  26: "#005fd7",
  27: "#005fff",
  28: "#008700",
  29: "#00875f",
  30: "#008787",
  31: "#0087af",
  32: "#0087d7",
  33: "#0087ff",
  34: "#00af00",
  35: "#00af5f",
  36: "#00af87",
  37: "#00afaf",
  38: "#00afd7",
  39: "#00afff",
  40: "#00d700",
  41: "#00d75f",
  42: "#00d787",
  43: "#00d7af",
  44: "#00d7d7",
  45: "#00d7ff",
  46: "#00ff00",
  47: "#00ff5f",
  48: "#00ff87",
  49: "#00ffaf",
  50: "#00ffd7",
  51: "#00ffff",
  52: "#5f0000",
  53: "#5f005f",
  54: "#5f0087",
  55: "#5f00af",
  56: "#5f00d7",
  57: "#5f00ff",
  58: "#5f5f00",
  59: "#5f5f5f",
  60: "#5f5f87",
  61: "#5f5faf",
  62: "#5f5fd7",
  63: "#5f5fff",
  64: "#5f8700",
  65: "#5f875f",
  66: "#5f8787",
  67: "#5f87af",
  68: "#5f87d7",
  69: "#5f87ff",
  70: "#5faf00",
  71: "#5faf5f",
  72: "#5faf87",
  73: "#5fafaf",
  74: "#5fafd7",
  75: "#5fafff",
  76: "#5fd700",
  77: "#5fd75f",
  78: "#5fd787",
  79: "#5fd7af",
  80: "#5fd7d7",
  81: "#5fd7ff",
  82: "#5fff00",
  83: "#5fff5f",
  84: "#5fff87",
  85: "#5fffaf",
  86: "#5fffd7",
  87: "#5fffff",
  88: "#870000",
  89: "#87005f",
  90: "#870087",
  91: "#8700af",
  92: "#8700d7",
  93: "#8700ff",
  94: "#875f00",
  95: "#875f5f",
  96: "#875f87",
  97: "#875faf",
  98: "#875fd7",
  99: "#875fff",
  100: "#878700",
  101: "#87875f",
  102: "#878787",
  103: "#8787af",
  104: "#8787d7",
  105: "#8787ff",
  106: "#87af00",
  107: "#87af5f",
  108: "#87af87",
  109: "#87afaf",
  110: "#87afd7",
  111: "#87afff",
  112: "#87d700",
  113: "#87d75f",
  114: "#87d787",
  115: "#87d7af",
  116: "#87d7d7",
  117: "#87d7ff",
  118: "#87ff00",
  119: "#87ff5f",
  120: "#87ff87",
  121: "#87ffaf",
  122: "#87ffd7",
  123: "#87ffff",
  124: "#af0000",
  125: "#af005f",
  126: "#af0087",
  127: "#af00af",
  128: "#af00d7",
  129: "#af00ff",
  130: "#af5f00",
  131: "#af5f5f",
  132: "#af5f87",
  133: "#af5faf",
  134: "#af5fd7",
  135: "#af5fff",
  136: "#af8700",
  137: "#af875f",
  138: "#af8787",
  139: "#af87af",
  140: "#af87d7",
  141: "#af87ff",
  142: "#afaf00",
  143: "#afaf5f",
  144: "#afaf87",
  145: "#afafaf",
  146: "#afafd7",
  147: "#afafff",
  148: "#afd700",
  149: "#afd75f",
  150: "#afd787",
  151: "#afd7af",
  152: "#afd7d7",
  153: "#afd7ff",
  154: "#afff00",
  155: "#afff5f",
  156: "#afff87",
  157: "#afffaf",
  158: "#afffd7",
  159: "#afffff",
  160: "#d70000",
  161: "#d7005f",
  162: "#d70087",
  163: "#d700af",
  164: "#d700d7",
  165: "#d700ff",
  166: "#d75f00",
  167: "#d75f5f",
  168: "#d75f87",
  169: "#d75faf",
  170: "#d75fd7",
  171: "#d75fff",
  172: "#d78700",
  173: "#d7875f",
  174: "#d78787",
  175: "#d787af",
  176: "#d787d7",
  177: "#d787ff",
  178: "#d7af00",
  179: "#d7af5f",
  180: "#d7af87",
  181: "#d7afaf",
  182: "#d7afd7",
  183: "#d7afff",
  184: "#d7d700",
  185: "#d7d75f",
  186: "#d7d787",
  187: "#d7d7af",
  188: "#d7d7d7",
  189: "#d7d7ff",
  190: "#d7ff00",
  191: "#d7ff5f",
  192: "#d7ff87",
  193: "#d7ffaf",
  194: "#d7ffd7",
  195: "#d7ffff",
  196: "#ff0000",
  197: "#ff005f",
  198: "#ff0087",
  199: "#ff00af",
  200: "#ff00d7",
  201: "#ff00ff",
  202: "#ff5f00",
  203: "#ff5f5f",
  204: "#ff5f87",
  205: "#ff5faf",
  206: "#ff5fd7",
  207: "#ff5fff",
  208: "#ff8700",
  209: "#ff875f",
  210: "#ff8787",
  211: "#ff87af",
  212: "#ff87d7",
  213: "#ff87ff",
  214: "#ffaf00",
  215: "#ffaf5f",
  216: "#ffaf87",
  217: "#ffafaf",
  218: "#ffafd7",
  219: "#ffafff",
  220: "#ffd700",
  221: "#ffd75f",
  222: "#ffd787",
  223: "#ffd7af",
  224: "#ffd7d7",
  225: "#ffd7ff",
  226: "#ffff00",
  227: "#ffff5f",
  228: "#ffff87",
  229: "#ffffaf",
  230: "#ffffd7",
  231: "#ffffff",

  ## 24 shades of grey:
  232: "#080808",
  233: "#121212",
  234: "#1c1c1c",
  235: "#262626",
  236: "#303030",
  237: "#3a3a3a",
  238: "#444444",
  239: "#4e4e4e",
  240: "#585858",
  241: "#626262",
  242: "#6c6c6c",
  243: "#767676",
  244: "#808080",
  245: "#8a8a8a",
  246: "#949494",
  247: "#9e9e9e",
  248: "#a8a8a8",
  249: "#b2b2b2",
  250: "#bcbcbc",
  251: "#c6c6c6",
  252: "#d0d0d0",
  253: "#dadada",
  254: "#e4e4e4",
  255: "#eeeeee",

}



## A regex to match URLs:

def re_group( regex ):

    return r"(?:%s)" % regex


def re_optional( regex ):

  return re_group( regex ) + "?"


def re_either( *regexes ):

    return re_group( r"|".join( regexes ) )


URL_RE = (
  r"\b"
  + re_either (
      re_either(  ## Recognizable prefix
        r"https?://",
        r"www\.",
      )
      + re_group( r"[\d\w_-]+\." ) + "*\w+", ## Host
      re_group(r"\d{1,3}\.") + r"{3}" + r"\d{1,3}"  ## IP
    )
  + re_optional( r":\d+" ) ## Port
  + re_optional(
      r"/"
      + re_optional(
          re_optional( r"[a-zA-Z0-9~.#/!?&=-]+" )
          + r"[a-zA-Z0-9~#/&_=-]"
        )
    )
)


def compute_closest_ansi_color( rgb ):

  u"""\
  Computes and returns the ANSI extended color number matching the given #rgb
  color most closely.

  Exact match:

  >>> print compute_closest_ansi_color( "#d7875f" )
  173

  Approximative match:

  >>> print compute_closest_ansi_color( "#d6885e" )
  173

  In case several matches are found, return the earliest:

  >>> print compute_closest_ansi_color( "#ffffff" )
  15

  """

  r, g, b, _ = QColor( rgb ).getRgb()

  curr_index = -1
  curr_dist = 3 * 256^2 + 1

  for i in range( 256 ):

    r2, g2, b2, _ = QColor( ANSI_COLORS_EXTENDED[ i ] ).getRgb()
    dist = (r-r2)**2 + (g-g2)**2 + (b-b2)**2

    if dist < curr_dist:
      curr_dist = dist
      curr_index = i

    if curr_dist == 0:
      return curr_index

  return curr_index



## Special characters:

ESC       = "\x1b"
LEFTARROW = unichr( 0x2192 )


## Command-related globals.

CMDCHAR = u"/"
HELP    = "help"
