import sublime
import sublime_plugin

import re
measurement_pattern = re.compile(r'''\[[ahd\s,]+\]''')

CHAR_TO_HOURS = {
	'h': 1,
	'a': 4,
	'd': 8
}

DOTS_TO_HOURS = {
	1: 4,
	2: 2*8,
	3: 7*8
}

def printout_for(hours):
	# create printout
	months = int(hours//(30*8))
	hours -= months*(30*8)
	weeks = int(hours//(7*8))
	hours -= weeks*(7*8)
	days = int(hours//8)
	hours -= days*8
	text = ""
	if months>0:
		text += str(months)+"m"
	if weeks>0:
		text += str(weeks)+"w"
	if days>0:
		text += str(days)+"d"
	if hours>0:
		text += str(hours)+"h"
	return text

class MdplanEventListener(sublime_plugin.ViewEventListener):
	@classmethod
	def is_applicable(cls, settings):
		return 'MarkdownPlan' in settings.get('syntax')

	def set_status(self):
		# find estimates and their corresponding measurements
		regions = self.view.find_all(r'''\[\.{1,3}\]''')
		total = 0
		for region in regions:
			dots = self.view.substr(region).count('.')
			remaining = DOTS_TO_HOURS[dots]
			line = self.view.substr(self.view.line(region.a))
			# check for measurements
			match = measurement_pattern.search(line)
			if match:
				completed = 0
				for c in match.group(0):
					completed += CHAR_TO_HOURS.get(c, 0)
				remaining = max(remaining - completed, 0)
			total += remaining
		printout = printout_for(total)
		self.view.set_status("markdown-plan", "remaining: "+printout)

	def on_modified(self):
		self.set_status()

	def on_load(self):
		self.set_status()

	def on_reload(self):
		self.set_status()
