import sublime
import sublime_plugin

import re
measurement_pattern = re.compile(r'''\[[ahd\s,]+\]''')

DOTS_TO_DAYS = {
	1: 0.5,
	2: 2,
	3: 7
}

CHAR_TO_DAYS = {
	'h': 0.125,
	'a': 0.5,
	'd': 1
}

def printout_for(days):
	# create printout
	months = days//30
	days -= months*30
	weeks = days//7
	days -= weeks*7
	text = ""
	if months>0:
		text += str(int(months))+"m"
	if weeks>0:
		text += str(int(weeks))+"w"
	text += str(days)+"d"
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
			remaining = DOTS_TO_DAYS[dots]
			line = self.view.substr(self.view.line(region.a))
			# check for measurements
			match = measurement_pattern.search(line)
			if match:
				completed = 0
				for c in match.group(0):
					completed += CHAR_TO_DAYS.get(c, 0)
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
