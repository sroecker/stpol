class Variable:
   def __init__(self, name, lbound, ubound, bins=20, shortName="", displayName=""):
      self.name = name
      self.lbound = lbound
      self.ubound = ubound
      self.bins = bins
      self.shortName = shortName
      self.displayName = displayName
