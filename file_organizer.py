#!/usr/bin/python
from __future__ import print_function
import rb
import rhythmdb

class _RDBEntry(object):
	"""Our attributes are RhythmDB information."""

	def __init__(self, rdb, song):
		self.rdb = rdb
		self.song = song

	def __getattr__(self, prop):
		p = getattr(rhythmdb, "PROP_"+prop.upper())
		return self.rdb.entry_get(self.song, p)

class FileOrganizer(rb.Plugin):
	def activate(self, shell):
		"""This is called when we're activated or RhythmBox starts."""

		print("activating...")

		self.new_path = "{0.artist}/{0.album}/{0.track_number} - {0.title}.mp3"
		self.shell = shell
		self.rdb = shell.get_property("db")

		self.organize()

	def deactivate(self, shell):
		"""This is called when we're deactivated or RhythmBox exits."""

		print("deactivating")

		del self.shell, self.rdb

	def organize(self):
		"""Rename all the music in our database based on its metadata."""

		def organize_entry(entry):
			"""We're needed because RhythmDB doesn't support the iteration
			protocol."""

			s = _RDBEntry(self.rdb, entry)
			uri = entry.get_playback_uri()

			if not uri.startswith("file://"):
				print("ignoring " % uri)
				return
			else:
				new_path = self.new_path.format(s)
				print("%r -> %r" % (uri, new_path))

		self.rdb.entry_foreach(organize_entry)
