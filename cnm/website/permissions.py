
from AccessControl import ModuleSecurityInfo
from AccessControl.Permission import addPermission

security = ModuleSecurityInfo('cnm.website.permissions')

security.declarePublic('DeleteThisObject')
DeleteThisObject = 'CNM: Delete this object'
addPermission(DeleteThisObject, default_roles=('Manager', 'Owner'))
