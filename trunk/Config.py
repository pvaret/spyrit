##
## Config.py
##
## Instanciates the configuration singleton.
##


from IniConfigBasket import IniConfigBasket
from ConfigPaths     import CONFIG_FILE
from Defaults        import defaults


config        = IniConfigBasket( CONFIG_FILE )
config.parent = defaults
