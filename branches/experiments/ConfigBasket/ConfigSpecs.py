##
## ConfigSpecs.py
##
## Specifies configuration options and defaults for this app.
##



class ConfigSpecs:

  def __init__(s, specs):

    s.defaults  = {}
    s.docs      = {}
    s.typehints = {}

    s.updateFromSpecs(specs)


  def updateFromSpecs(s, specs):

    for line in specs:
    
      name, default, tail = line[0], line[1], line[2:]
      s.defaults[name] = default

      if not tail:
        continue

      doc, tail = tail[0], tail[1:]
      s.docs[name] = doc

      if not tail:
        continue

      s.typehints[name] = tail[0]


  def getDefault(s, k):

    try:
      return s.defaults[k]
      
    except KeyError:
      raise KeyError("There is no such configuration key as '%s'!" % k)


  def getDoc(s, k):
    
    return s.docs.get(k, "")


  def getTypehint(s, k):
  
    return s.typehints.get(k, None)
