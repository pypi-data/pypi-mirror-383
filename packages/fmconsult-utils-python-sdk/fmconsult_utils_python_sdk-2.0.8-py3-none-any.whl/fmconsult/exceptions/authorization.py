class AuthorizationError(Exception):
    
  def __init__(self, code, description):
    self.code = code
    self.description = description