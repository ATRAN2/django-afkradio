import logging
logging.basicConfig(level=100)

class FileTypeError( Exception ):
	def __init__(self, message):
		logging.error('FileTypeError ' + message)
	pass
	
class DuplicateEntryError( Exception ):
	def __init__(self, message):
		logging.error('DupliateEntryError ' + message)
	pass

class FileNotFoundError( Exception ):
	def __init__(self, message):
		logging.error('FileNotFoundError ' + message)
	pass

class FieldNotFoundError( Exception ):
	def __init__(self, message):
		logging.error('FieldNotFoundError ' + message)
	pass

class SongNotFoundError( Exception ):
	def __init__(self, message):
		logging.error('SongNotFoundError ' + message)
	pass

class SetlistNotFoundError( Exception ):
	def __init__(self, message):
		logging.error('TypeNotFoundError ' + message)
	pass

class MPDRootNotFound( Exception ):
	def __init__(self, message='No message'):
		if message == 'No message':
			self.message = 'MPD root not found.  Please set the folder ' + \
				'location in config.json or through the admin panel'
		logging.error('MPDRootNotFound ' + message)

	def __str__(self):
		return repr(self.message)
