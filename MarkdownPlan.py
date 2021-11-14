import sublime
import sublime_plugin

BLOCK_QUOTE_LINE_PREFIX = '> '

import re

task_regex = r'''^( *|\t*)(-|\*|[1-9][0-9]*\.|#{1,6}) '''
task_regex_with_block_comments = '^('+BLOCK_QUOTE_LINE_PREFIX+r''')*( *|\t*)(-|\*|[1-9][0-9]*\.|#{1,6}) '''
estimate_pattern = re.compile(r'''\[\.{1,3}\]''')
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
		text += " "+str(weeks)+"w"
	if days>0:
		text += " "+str(days)+"d"
	if hours>0:
		text += " "+str(hours)+"h"
	return text

class MdplanEventListener(sublime_plugin.ViewEventListener):
	@classmethod
	def is_applicable(cls, settings):
		return 'MarkdownPlan' in settings.get('syntax')

	def set_status(self):

		# find estimates and their corresponding measurements
		regions = self.view.find_all(task_regex)
		total = 0
		for region in regions:
			line = self.view.substr(self.view.line(region.a))
			estimate = estimate_pattern.search(line)
			if estimate:
				dots = estimate.group(0)
				remaining = DOTS_TO_HOURS[dots.count('.')]
				# check for measurements
				match = measurement_pattern.search(line)
				if match:
					completed = 0
					for c in match.group(0):
						completed += CHAR_TO_HOURS.get(c, 0)
					remaining = max(remaining - completed, 0)
				total += remaining

		# print a summary on the status bar
		self.view.set_status("markdown-plan", "remaining: "+printout_for(total))

	def on_modified(self):
		self.set_status()

	def on_load(self):
		self.set_status()

	def on_reload(self):
		self.set_status()

class MdplanCommentCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# get the starting points of all lines intersecting the selection
		task_line_points = set()
		for region in self.view.sel():
			for line in self.view.lines(region):
				point = line.begin()
				# check if the point is a task line
				if re.match(task_regex_with_block_comments, self.view.substr(self.view.line(point))):
					task_line_points.add(point)
		# order the task_line_points
		task_line_points = sorted(list(task_line_points), reverse=True)
		# determine if toggle comment should create or remove comments
		if all(self.view.substr(sublime.Region(point,point+2))==BLOCK_QUOTE_LINE_PREFIX for point in task_line_points):
			# remove comments
			for point in task_line_points:
				self.view.erase(edit, sublime.Region(point,point+2))
		else:
			# insert a block quote character at the beginning of each line
			for point in task_line_points:
				self.view.insert(edit, point, BLOCK_QUOTE_LINE_PREFIX)
