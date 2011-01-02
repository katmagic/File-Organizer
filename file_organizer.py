#!/usr/bin/python
from __future__ import print_function
import rb
import rhythmdb
import gtk

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
		self.uim = shell.get_ui_manager()

		self.add_organize_tool()

	def add_organize_tool(self):
		"""Add an 'Organize Files' entry to the 'Tools' menu associated with
		self.organize()."""

		action = gtk.Action(
			"OrganizeFiles",
			"Organize Files",
			"Rename files on the basis of their metadata.",
			"OrganizeFiles"
		)
		action.connect('activate', self.organize, self.shell)

		action_group = gtk.ActionGroup('OrganizeFilesActionGroup')
		action_group.add_action(action)
		self.uim.insert_action_group(action_group)

		self.uim.add_ui_from_file( self.find_file("file_organizer.xml") )

	def deactivate(self, shell):
		"""This is called when we're deactivated or RhythmBox exits."""

		print("deactivating")

		del self.shell, self.rdb, self.uim

	def organize(self, *_): # The arguments that go into _ are useless.
		"""Rename all the music in our database based on its metadata."""

		self.rdb.entry_foreach(lambda e: self.organize_single_entry(e))

	def organize_single_entry(self, entry):
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
