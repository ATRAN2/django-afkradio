from afkradio.models import Songs, Types
import subprocess

class Playback:

	@staticmethod
	def mpc_play():
		proc = subprocess.Popen(["mpc", "play"], stdout=subprocess.PIPE)
		return "Played mpc"

	@staticmethod
	def mpc_stop():
		proc = subprocess.Popen(["mpc", "stop"], stdout=subprocess.PIPE)
		return "Stopped mpc"

	@staticmethod 
	def mpc_clear():
		proc = subprocess.Popen(["mpc", "clear"], stdout=subprocess.PIPE)
		return "Cleared mpc playlist"

	@staticmethod 
	def mpc_crop():
		proc = subprocess.Popen(["mpc", "crop"], stdout=subprocess.PIPE)
		return "Cleared mpc playlist except currently playing song"

	@staticmethod
	def mpc_update():
		proc = subprocess.Popen(["mpc", "update"], stdout=subprocess.PIPE)
		return "Scanned MPD root and updated MPD db (NOT models.Songs DB)"

	@staticmethod
	def mpc_add(song_path):
		proc = subprocess.Popen(["mpc", "add", song_path])
		return "Added " + song_path + " to the playlist"

	@staticmethod
	def mpc_currently_playing():
		proc = subprocess.Popen(["mpc"], stdout=subprocess.PIPE)
		line = proc.stdout.readline()
		if line.startswith("volume: n/a"):
			return "No song is currently playing"
		else:
			return line
		
