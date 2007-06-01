from Defaults import SPECS
from ConfigSpecs import ConfigSpecs
from GenConfig import ConfigBasket

_conf = None



def Config():

  global _conf
  
  if _conf is None:
    
    _conf = ConfigBasket()
    _conf.specs = ConfigSpecs(SPECS)
    
  return _conf
