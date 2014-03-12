class FileTypeError( Exception ): pass
class DuplicateEntryError( Exception ): pass
class FileNotFoundError( Exception ): pass
class FieldNotFoundError( Exception ): pass
class SongNotFoundError( Exception ): pass
class TypeNotFoundError( Exception ): pass
class MPDRootNotFound( Exception ):
	def __init__(self, message='No message'):
		if message == 'No message':
			self.message = 'MPD root not found.  Please set the folder ' + \
				'location in config.json or through the admin panel'
	def __str__(self):
		return repr(self.message)
