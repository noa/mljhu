# -*- coding: utf-8 -*-

'''
This script connects directly to the google spreadsheet. You need the following library:
http://code.google.com/apis/documents/docs/3.0/developers_guide_python.html
'''
import sys, os, csv, codecs
from datetime import datetime 

from unicode_csv_reader import unicode_csv_reader

from generate_machine_learning_people_list import getUsernameAndPassword, getGoogleSpreadsheet

def cleanField(text):
	split_text = text.split('\n')
	if len(split_text) == 1:
		return text
	
	content = []
	for line in split_text:
		if line.startswith('>'):
			line = line[1:]
		content.append(line.strip())
	return ' '.join(content)
			
class CsvLoader:
	def __init__(self, filename):
		self.__loadFile(filename)
		
	def __mapColumns(self, entry):
		self.names_to_columns = {}
		self.columns_to_names = {}
		for ii, name in enumerate(entry):
			self.names_to_columns[name.lower()] = ii
			self.columns_to_names[ii] = name.lower()

	def getColumnNames(self):
		return self.names_to_columns.keys()
		
	def __loadFile(self, filename):
		file = codecs.open(filename, 'r', 'utf-8')
		#reader = csv.reader(file)
		reader = unicode_csv_reader(file)
		
		self.contents = []
		
		for ii, entry in enumerate(reader):
			if ii == 0:
				self.__mapColumns(entry)
				continue
			line = {}
			for jj in range(len(entry)):
				line[self.columns_to_names[jj]] = entry[jj]
			self.contents.append(line)

		file.close()
	
	def __iter__(self):
		return self.contents.__iter__()
	
	def __len__(self):
		return len(self.contents)
		
	def getContents(self):
		return self.contents

class GenerateStaticTalksPage:
	def __init__(self):
		self.spreadsheet_key = 'spreadsheet:0AgLn69AE8GTVdFVRMjQ1QmxnVHJiRWdKVC12QU8wRUE'
		self.gids = [0]
		self.talks_page_header_text = '''Click on a talk title for details. To receive talk announcements by email, <a href="http://ml.jhu.edu/signup-announce/">sign up for our mailing list.</a> In return, please forward announcements of ML-related talks to announce (at) ml.jhu.edu.<br><br>'''
		
		
		self.forum_text = { 'CLSP (Center for Language and Speech Processing)': ('http://www.clsp.jhu.edu/seminars/', 'CLSP'),
							'CS (Computer Science)': ('http://cs.jhu.edu/calendar/', 'CS'),
							'CIS (Center for Imaging Science)': ('http://cis.jhu.edu/seminars/', 'CIS'),
							'ECE (Electrical and Computer Engineering)': ('http://www.ece-jhu.org/index.php/seminars', 'ECE'),
							'LCSR (Laboratory for Computational Sensing and Robotics)': ('https://www.lcsr.jhu.edu/LCSR_CISST_Seminars', 'LCSR'),
							'HLTCOE (Human Language Technology Center of Excellence)': ('http://hltcoe.jhu.edu/category/talks/', 'HLTCOE'),
							'AMS (Applied Math & Stats)': ('http://www.ams.jhu.edu/~seminar/', 'AMS'),
							'CogSci (Cognitive Science)': ('http://cogsci.jhu.edu/events/', 'CogSci'),
							'Biostatistics': ('http://www.biostat.jhsph.edu/newsEvent/event/seminar/seminars.shtml', 'Biostatistics'),
		}
		
		self.preamble = '''<script type="text/javascript">// <![CDATA[
// thanks to http://blog.movalog.com/a/javascript-toggle-visibility/
function toggle_visibility(id) {
	var e = document.getElementById(id);
	if (e != null) {
		if(e.style.display == 'block')
			{ e.style.display = 'none'; }
		else
			{ e.style.display = 'block'; }
		}
	}
	function make_visible(id) {
	var e = document.getElementById(id);
	if (e != null) {
		e.style.display = 'block';
		}
	}
		function make_invisible(id) {
	var e = document.getElementById(id);
	if (e != null) {
		e.style.display = 'none';
		}
	}
// ]]>
</script>
		'''
		self.talk_template = '''%s, %s, %s<br><strong><a onclick="toggle_visibility('%s'); return false;" href="#">%s</a></strong><br><em>%s%s</em><br>
<div id="%s" style="display: none;"><br>

<strong>Abstract:</strong> %s<br><br>

%s

%s

%s

<hr />

</div><br>'''


	def sortTalks(self, talks):
		talks_list = []
		patterns = [
					'%a %m/%d/%y, %I:%M%p',
					'%m/%d/%Y, %I:%M%p',
					'%m/%d/%y, %I:%M%p',
					'%m/%d/%y',
					'%m/%d/%Y',
					]
		for talk in talks:
			date = talk['date'].strip()
			stripped_date = date[date.find(' ')+1:]
			date_obj = None
			for pattern in patterns:
				try:
					date_obj = datetime.strptime(date, pattern)
				except:
					pass
				if date_obj != None:
					break
				try:
					date_obj = datetime.strptime(stripped_date, pattern)
				except:
					pass
				if date_obj != None:
					break
				
			
			if date_obj == None:
				print 'Cannot parse: "%s" from %s' % (date, str(talk)) 
			talk['date_obj'] = date_obj
			talks_list.append((date_obj, talk))

		talks_list.sort(reverse=True)

		talks = []
		for date_obj, talk in talks_list:
			talks.append(talk)
			
		return talks
	
	def generateTalksPage(self, filename, talks):
		file = codecs.open(filename, mode='w', encoding='utf-8')
		#file = open(filename, 'w')
		
		file.write(self.preamble)
		
		file.write(self.talks_page_header_text)
		ids = []
		output_strings = []
		for ii, talk in enumerate(talks):

			date_obj = talk['date_obj']
			speaker = talk['speaker'].strip()
			title = talk['title'].strip()
			location = talk['location'].strip()
			forum = talk['forum'].strip()
			affiliation = talk['affiliation'].strip()
			abstract = talk['abstract'].strip()
			bio = talk['bio'].strip()
			other = talk['other'].strip()
			host = talk['host'].strip()
			
			
			bio  = cleanField(bio)
			abstract = cleanField(abstract)
			
			id = 'talk' + str(ii)
			date_string = date_obj.strftime('%a %m/%d/%y')
			time_string = date_obj.strftime('%I:%M%p').lower()
			
			ids.append(id)
			if affiliation:
				affiliation = ', ' + affiliation
			
			if other:
				other = '<strong>Note:</strong> %s<br><br>' % other

			if bio:
				bio = '<strong>Bio:</strong> %s<br><br>' % bio

			if forum == 'None of the below':
				forum = ''
			elif forum:
				forum_url, forum_text = self.forum_text[forum]
				forum = '(an ML talk in the <a href="%s">%s Speaker Series</a>)' % (forum_url, forum_text)
			
			output_string = self.talk_template % (date_string, time_string, location, id, title, \
												  speaker, affiliation, id, abstract, bio, other, forum)
			output_string = output_string.replace('\t', ' ')
			output_strings.append(output_string)
			
		
		all_functions_collapse = []
		all_functions_expand = []
		
		for id in ids:
			all_functions_expand.append("make_visible('%s')" % id)
			all_functions_collapse.append("make_invisible('%s')" % id)
		
		all_functions_expand = ';'.join(all_functions_expand)
		all_functions_collapse = ';'.join(all_functions_collapse)
		file.write('''<a onclick="%s; return false;" href="#">Expand All</a>/<a onclick="%s; return false;" href="#">Collapse All</a><br><br>''' % (all_functions_expand, all_functions_collapse))
		
		output_string = '\n'.join(output_strings)
		file.write(output_string)
		
		file.close()
		
	
	def generateWidget(self, filename, talks, num_talks=5):
		file = codecs.open(filename, 'w', 'utf-8')
		
		file.write('<ul>')
		for ii, talk in enumerate(talks[:num_talks]):
			date_obj = talk['date_obj']
			speaker = talk['speaker']
			title = talk['title']

			date_string = date_obj.strftime('%a %b %d')
			
			id = 'talk' + str(ii)
			
			output_string = []
			output_string.append('<li><a href="talks/">')
			output_string.append('%s - %s: %s<br>' % (date_string, speaker, title))
			output_string.append('</a></li>')
			file.write(''.join(output_string))
		file.write('</ul>')
		file.write('<a href="talks/">More talks</a>')
		file.close()
		
	def run(self):
		if len(sys.argv) != 3:
			print 'usage: %s talks_output widget_output' % sys.argv[0]
			sys.exit()

		talks_output_filename = sys.argv[1]
		widget_output_filename = sys.argv[2]
		
		google_username, google_password = getUsernameAndPassword()
		
		[talks_filepath] = \
				getGoogleSpreadsheet(google_username, google_password, self.spreadsheet_key, self.gids)
		reader = CsvLoader(talks_filepath)
		
		
		print 'Found %d talks.' % len(reader)
		talks = self.sortTalks(reader.getContents())
		
		self.generateTalksPage(talks_output_filename, talks)
		self.generateWidget(widget_output_filename, talks)

if __name__ == '__main__':
	GenerateStaticTalksPage().run()
