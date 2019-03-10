import lucia
from openal import al, alc, audio
from math import pi, cos, sin, radians
from .loaders import *
import io

class SoundPool():
	def __init__(self, rolloff_factor = 0.5, max_distance=10):
		self.sources = []
		self.all_paused = False
		self.default_rolloff_factor = rolloff_factor
		self.world = lucia.audio_world
		self.listener = self.world.listener
		#get list of available htrf tables
		self.hrtf_buffers = [alc.ALCint(),alc.ALCint*4,alc.ALCint()]
		alc.alcGetIntegerv(self.world.device,alc.ALC_NUM_HRTF_SPECIFIERS_SOFT, 1,self.hrtf_buffers[0])
		#attributes for device to set specified hrtf table
		self.hrtf_select = self.hrtf_buffers[1](alc.ALC_HRTF_SOFT,alc.ALC_TRUE,alc.ALC_HRTF_ID_SOFT,1)

	def set_hrtf(self,num):
		if num == None:
			alc.alcResetDeviceSOFT(self.world.device, None)
		elif num >= 0 and num <= self.hrtf_buffers[0].value:
			self.hrtf_select[3] = num
		#reset the device so the new hrtf settings take effect
			alc.alcResetDeviceSOFT(self.world.device, self.hrtf_select)

#confirm hrtf has been loaded and is enabled
	def is_hrtf_enabled(self):
		alc.alcGetIntegerv(self.world.device,alc.ALC_HRTF_SOFT,1,self.hrtf_buffers[2])
		if self.hrtf_buffers[2].value == alc.ALC_HRTF_DISABLED_SOFT:
			return False
		elif self.hrtf_buffers[2].value == alc.ALC_HRTF_ENABLED_SOFT:
			return True
		elif self.hrtf_buffers[2].value == alc.ALC_HRTF_DENIED_SOFT:
			return False
		elif self.hrtf_buffers[2].value == alc.ALC_HRTF_REQUIRED_SOFT:
			return True
		elif self.hrtf_buffers[2].value == alc.ALC_HRTF_HEADPHONES_DETECTED_SOFT:
			return True
		elif self.hrtf_buffers[2].value == alc.ALC_HRTF_UNSUPPORTED_FORMAT_SOFT:
			return False

	def pause_all(self):
		for source in self.sources:
			self.world.pause(source)
		self.world.update()
		self.all_paused = True

	def resume_all(self):
		for source in self.sources:
			self.world.play(source)
		self.world.update()
		self.all_paused = False

	def stop(self, source):
		try:
			self.world.stop(source)
		except:
			raise lucia.audio.SoundNotPlayingError(f"Sound {source} is no longer playing.")

	def play_stationary(self, soundfile, looping =False):
		source = audio.SoundSource()
		source.queue(lucia.audio._get_audio_data(soundfile))
		self.world.play(source)
		self.world.update()
		self.sources.append(source)
		return source

	def play_1d(self, soundfile, x, looping = False, rolloff_factor = -1):
		return play_3d(soundfile,x,0,0,looping,rolloff_factor)

	def play_2d(self, soundfile, x, y, looping = False, rolloff_factor = -1):
		return self.play_3d(soundfile,x,y,0,looping,rolloff_factor)

	def play_3d(self, soundfile, x, y, z, looping = False, pitch=1.0, volume=1.0, rolloff_factor=0.5):
		source = audio.SoundSource(1.0, pitch, (x,y,z))
		source.queue(lucia.audio._get_audio_data(soundfile))
		source.looping = looping
		self.world.play(source)
		self.world.update()
		self.sources.append(source)
		return source

	def update_listener_1d(self, x):
		self.update_listener_3d(x,0,0)

	def update_listener_2d(self, x, y):
		self.update_listener_3d(x,y,0)

	def update_listener_3d(self, x, y, z, direction=0, zdirection=0):
		if direction > 360:
			direction = direction - 360
		self.listener.position = (x,y,-z)
		ox=0+cos(radians(direction))
		oy=0+sin(radians(direction))
		oz=0+sin(radians(zdirection))
		self.listener.orientation = (ox, oz, -oy, 0, 1, 0)
		self.world.update()
