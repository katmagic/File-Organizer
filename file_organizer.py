#!/usr/bin/env python
from __future__ import print_function
import rb
import rhythmdb
import gtk
import sys
import os

if sys.version_info.major > 2:
	from urllib.parse import unquote as unquote_url
else:
	from urllib import unquote as unquote_url

def super_rename(src, dst, force=False):
	"""Move the file at src to dst. If any of dst's parent directories don't
	exist, create them. Recursively prune blank parent directories of src."""

	if src == dst:
		return

	if not force and os.path.exists(dst):
		raise OSError("[Errno 17] File exists: '%r'" % dst)

	src_dir = os.path.split(src)[0]
	dst_dir = os.path.split(dst)[0]

	if not os.path.isdir(dst_dir):
		os.makedirs(dst_dir)

	os.rename(src, dst)

	try:
		os.removedirs(src_dir)
	except OSError:
		pass

class _RDBEntry(object):
	"""Our attributes are RhythmDB information."""

	def __init__(self, rdb, song):
		self.rdb = rdb
		self.song = song

	def __getattr__(self, prop):
		p = getattr(rhythmdb, "PROP_"+prop.upper())
		return self.rdb.entry_get(self.song, p)

class _EscapedRDBEntry(_RDBEntry):
	def __getattr__(self, prop):
		res = _RDBEntry.__getattr__(self, prop)
		if type(res) is str:
			return res.replace('/', '_')
		else:
			return res

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

		self.action_group = gtk.ActionGroup('OrganizeFilesActionGroup')
		self.action_group.add_action(action)
		self.uim.insert_action_group(self.action_group)

		ui_file = self.find_file("file_organizer.xml")
		# self.uim.remove_ui() needs this to destroy our menu entry.
		self.ui_id = self.uim.add_ui_from_file(ui_file)

	def remove_organize_tool(self):
		"""Remove the 'Organize Files' entry from the 'Tools' menu."""

		self.uim.remove_ui(self.ui_id)
		self.uim.remove_action_group(self.action_group)

	def deactivate(self, shell):
		"""This is called when we're deactivated or RhythmBox exits."""

		print("deactivating...")

		self.remove_organize_tool()
		del self.shell, self.rdb, self.uim

	def organize(self, *_): # The arguments that go into _ are useless.
		"""Rename all the music in our database based on its metadata."""

		self.rdb.entry_foreach(lambda e: self.organize_single_entry(e))

	def organize_single_entry(self, entry):
		"""We're needed because RhythmDB doesn't support the iteration
		protocol."""

		s = _EscapedRDBEntry(self.rdb, entry)

		uri = entry.get_playback_uri()

		if not uri or not uri.startswith("file://"):
			return

		src = unquote_url( uri.partition("://")[2] )
		dst = os.path.join(rb.music_dir(), self.new_path.format(s))

		try:
			print("%s -> %s" % (src, dst))
			super_rename(src, dst)
		except OSError as err:
			print( str(err) )
