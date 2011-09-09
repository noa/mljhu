# -*- coding: utf-8 -*-

'''
This script connects directly to the google spreadsheet. You need the following library:
http://code.google.com/apis/documents/docs/3.0/developers_guide_python.html
'''
import sys, os, csv, tempfile
import gdata.spreadsheet.service
import gdata.docs.data
import gdata.docs.client

class GenerateMachineLearningPeopleList:
	def __init__(self):
		#self.text = '''<tr><td align="center"><h3><span class="Apple-style-span" style="font-size: 11px; font-weight: normal;">%s </span></h3></td><td><span class="Apple-style-span" style="font-size: 16px; font-weight: bold;">%s</span><br /> <span class="Apple-style-span" style="font-size: 11px; font-weight: normal;">%s%s</span><br /> %s<br /> <strong>Email | Website:</strong> %s (at) %s | <strong><a href="%s">website</a></strong><br /> <strong>Research interests</strong>: %s<br /> <strong>Applications</strong>: %s%s</td></tr>'''
		self.text = '''<tr valign="top"><td align="right" width="150"><a href="%s" target="_blank">%s</a></td><td align="left" width="10"></td>'''+ \
					'''<td align="left"><a href="%s" target="_blank"><span class="Apple-style-span" style="font-size: 16px; font-weight: bold;">%s</span></a><br />''' + \
					'''<span class="Apple-style-span" style="font-size: 11px; font-weight: normal;">%s%s</span><br /><br /> <strong>Research interests</strong>: %s<br />''' + \
					'''<a href="research/"><strong>Applications</strong></a>: %s%s</td></tr>'''
		self.photo = '<img title="%s" src="http://mljhu.files.wordpress.com/%s" />'
		self.centers = {			
			'IBBS': 'http://www.hopkinsmedicine.org/institute_basic_biomedical_sciences/research_centers/high_throughput_biology_hit/',
			'CLSP' : 'http://www.clsp.jhu.edu',
			'HLTCOE' : 'http://hltcoe.jhu.edu',
			'ICM' : 'http://www.icm.jhu.edu/',
			'CISST' : 'http://www.cisst.org/',
			'LCSR' : 'https://lcsr.jhu.edu/',
			'CIS' : 'http://www.cis.jhu.edu/',
		}
		self.department_urls = {
			'Computer Science': 'http://www.cs.jhu.edu',
			'Electrical and Computer Engineering': 'http://www.ece.jhu.edu',
			'Biomedical Engineering': 'http://www.bme.jhu.edu/',
			'Population, Family and Reproductive Health' : 'http://www.jhsph.edu/dept/pfrh/',
			'Physics and Astronomy' : 'http://physics-astronomy.jhu.edu/',
			'Applied Physics Laboratory' : 'http://www.jhuapl.edu/',
			'Oncology Biostatistics' : 'http://www.cancerbiostats.onc.jhmi.edu/',
			'Applied Mathematics and Statistics' : 'http://www.ams.jhu.edu/',
			'Chemical and Biomolecular Engineering' : 'http://www.jhu.edu/chembe/',
			'Biostatistics' : 'http://www.biostat.jhsph.edu/',
			'Molecular Microbiology and Immunology' : 'http://www.jhsph.edu/dept/mmi/',
		}
	
	def getGoogleSpreadsheet(self, username, password):
		file, people_file_path = tempfile.mkstemp(suffix='.csv')
		os.close(file)
		file, courses_file_path = tempfile.mkstemp(suffix='.csv')
		os.close(file)
		file, courses_category_text_file_path = tempfile.mkstemp(suffix='.csv')
		os.close(file)
						
		# Authorize this client
		client = gdata.docs.client.DocsClient()
		client.ssl = True  # Force all API requests through HTTPS
		client.http_client.debug = False  # Set to True for debugging HTTP requests
		client.ClientLogin(username, password, client.source);
		
		# Authorize the client for spreadsheet access.
		spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
		spreadsheets_client.ClientLogin(username, password, client.source)
		
		# Specify which Google Spreadsheet to download.
		entry = client.GetDoc('spreadsheet:0Ai_9m7n8XhYKdGZwTlQyWFNudkREVWtTbDBMRkRnc1E')
		
		# substitute the spreadsheets token into our client
		docs_token = client.auth_token
		client.auth_token = gdata.gauth.ClientLoginToken(spreadsheets_client.GetClientLoginToken())
		
		
		# The people csv
		client.Export(entry, people_file_path, gid=1)
		
		# The courses csv
		client.Export(entry, courses_file_path, gid=3)
		
		# The course category text csv files
		client.Export(entry, courses_category_text_file_path, gid=4)
		
		client.auth_token = docs_token  # reset the DocList auth token
		
		return people_file_path, courses_file_path, courses_category_text_file_path
		

	def generateCourseCategory(self, output_file, course_list, arg_subcategory, instructor_to_proper_name, courses_names_to_columns, prefix_text, suffix_text):
		output_file.write('<h2>%s</h2>' % arg_subcategory)
		output_file.write(prefix_text)
		output_file.write('<ul>')

		for entry in course_list:
			instructors_list = []
			instructors = self.getColumn(entry, courses_names_to_columns, 'instructor')
			department = self.getColumn(entry, courses_names_to_columns, 'department')
			id = self.getColumn(entry, courses_names_to_columns, 'id')
			url = self.getColumn(entry, courses_names_to_columns, 'url')
			title = self.getColumn(entry, courses_names_to_columns, 'title')
			
			for instructor in instructors.split(';'):
				instructor = instructor.strip()
				if instructor in instructor_to_proper_name:
					instructor = instructor_to_proper_name[instructor]
				instructors_list.append(instructor)
			instructors = ', '.join(instructors_list)
			output_file.write('<li>%s %s: <a href="%s" target="_blank">%s</a>&nbsp;&nbsp;<em>%s</em></li>' % (department, id, url, title, instructors))

		output_file.write('</ul>')
		output_file.write(suffix_text)
			
	def generateCourseCategoryStart(self, category, output_file):
		output_file.write('<h1>%s</h1>' % category)
					
	def generateFacultyCategory(self, faculty_output_file, faculty_list, category, faculty_names_to_columns, courses_names_to_columns):
		num_names = 0
		faculty_output_file.write('<h1>%s</h1><table border="0" bgcolor="#F3F0E9"><tbody>' % category)
		
		for last_name, entry in faculty_list:
			name = self.getColumn(entry, faculty_names_to_columns, 'name')
			centers = self.getColumn(entry, faculty_names_to_columns, 'centers')
			url = self.getColumn(entry, faculty_names_to_columns, 'url')
			research_interests = self.getColumn(entry, faculty_names_to_columns, 'research_interests')
			applications = self.getColumn(entry, faculty_names_to_columns, 'applications')
			photo = self.getColumn(entry, faculty_names_to_columns, 'photo')
			departments = self.getColumn(entry, faculty_names_to_columns, 'department')
			category = self.getColumn(entry, faculty_names_to_columns, 'category')

			name = name.strip()
			if photo.strip() == '':
				photo = '<br />'
			else:
				photo = self.photo % (name.strip(), photo)

			if centers != '':
				new_centers = []
				for center in centers.split(';'):
					center = center.strip()
					if center not in self.centers:
						print 'Missing ', center
					center_url = self.centers[center]
					center_text = '<a href="%s" target="_blank">%s</a>' % (center_url, center)
					new_centers.append(center_text)
				centers = '&nbsp;|&nbsp;' + ', '.join(new_centers)
			

			departments_list = []
			for department in departments.split(';'):
				department = department.strip()
				if department not in self.department_urls:
					print 'Unknown department: ' + department
					department = '%s' % (department)
				else:
					department_url = self.department_urls[department]
					department = '<a href="%s" target="_blank">%s</a>' % (department_url, department)

				departments_list.append(department)

			department = ', '.join(departments_list)
			
			teaching = ''
			if name.lower() in self.instructor_to_course_entry:
				teaching_list = self.instructor_to_course_entry[name.lower()]
				teaching_output = []
				for course_entry in teaching_list:
					course_url = self.getColumn(course_entry, courses_names_to_columns, 'url')
					course_department = self.getColumn(course_entry, courses_names_to_columns, 'department')
					course_id = self.getColumn(course_entry, courses_names_to_columns, 'id')
					course_title = self.getColumn(course_entry, courses_names_to_columns, 'title')
					
					course_url = course_url.strip()
					if course_url != '':
						course_string = '<a href="%s" target="_blank">%s %s: %s</a>' % (course_url, course_department, course_id, course_title)
					else:
						course_string = '%s %s: %s' % (course_department, course_id, course_title)
					teaching_output.append(course_string)
				teaching = ', ' .join(teaching_output)
	
			if teaching:
				teaching = '<br /> <a href="courses/"><strong>Teaching</strong></a>: %s' % teaching
			

			#text_to_write = self.text % (photo, name.strip(), department.strip(), centers.strip(), main_text.strip(), email_username.strip(), email_domainname.strip(), url.strip(), research_interests.strip(), applications.strip(), teaching.strip())
			text_to_write = self.text % (url.strip(), photo.strip(), url.strip(), name.strip(), department.strip(), centers.strip(), research_interests.strip(), applications.strip(), teaching.strip())
			faculty_output_file.write(text_to_write)
			faculty_output_file.write('\n')
			num_names += 1
		faculty_output_file.write('</tbody></table>')
		return num_names
	
	def loadCoursesText(self, courses_category_text_file_path):
		courses_category_text_file = open(courses_category_text_file_path)
		reader = csv.reader(courses_category_text_file)
		
		category_prefix_text = {}
		category_suffix_text = {}
		names_to_columns = {}
		for ii, entry in enumerate(reader):
			if ii == 0:
				names_to_columns = self.mapColumnNames(entry)
				continue

			category = self.getColumn(entry, names_to_columns, 'area_name')
			category_prefix_text[category] = self.getColumn(entry, names_to_columns, 'prefix_text')
			category_suffix_text[category] = self.getColumn(entry, names_to_columns, 'suffix_text')

		courses_category_text_file.close()
		
		return category_prefix_text, category_suffix_text
		
	def mapColumnNames(self, entry):
		map = {}
		for ii, name in enumerate(entry):
			map[name] = ii
		
		return map
	
	def getColumn(self, entry, names_to_columns, column):
		return entry[names_to_columns[column]]
		
	def run(self):
		if len(sys.argv) != 5:
			print 'usage: %s google_username google_password faculty_output courses_output' % sys.argv[0]
			sys.exit()
			
		
		google_username = sys.argv[1]
		google_password = sys.argv[2]
		faculty_output_filename = sys.argv[3]
		courses_output_filename = sys.argv[4]
		
		
		faculty_input_filename, courses_input_filename, courses_category_text_file_path = self.getGoogleSpreadsheet(google_username, google_password)
		faculty_input_file = open(faculty_input_filename)
		faculty_reader = csv.reader(faculty_input_file)
		faculty_output_file = open(faculty_output_filename, 'w')
		
		courses_input_file = open(courses_input_filename)
		courses_reader = csv.reader(courses_input_file)
		courses_output_file = open(courses_output_filename, 'w')
	
		category_to_subcategory = {}
		self.instructor_to_course_entry = {}
		num_courses = 0
		courses_names_to_columns = {}
		for ii, entry in enumerate(courses_reader):
			if ii == 0:
				courses_names_to_columns = self.mapColumnNames(entry)
				continue
			
			category = self.getColumn(entry, courses_names_to_columns, 'category')
			subcategory = self.getColumn(entry, courses_names_to_columns, 'subcategory')
			instructor = self.getColumn(entry, courses_names_to_columns, 'instructor')
			department = self.getColumn(entry, courses_names_to_columns, 'department')
			
			if category not in category_to_subcategory:
				category_to_subcategory[category] = {}
			course_list = category_to_subcategory[category].setdefault(subcategory, [])
			course_list.append((department, entry))
			
			instructor_list = self.instructor_to_course_entry.setdefault(instructor.lower(), [])
			instructor_list.append(entry)
				
			num_courses += 1
		
		category_prefix_text, category_suffix_text = self.loadCoursesText(courses_category_text_file_path)
		
		instructor_to_proper_name = {}
		core_faculty_list = []
		affiliated_faculty_list = []
		faculty_names_to_columns = {}
		for ii, entry in enumerate(faculty_reader):
			if ii == 0:
				faculty_names_to_columns = self.mapColumnNames(entry)
				continue
			
			
			name = self.getColumn(entry, faculty_names_to_columns, 'name').strip()
			category = self.getColumn(entry, faculty_names_to_columns, 'category')
			if category.lower() == 'core':
				core_faculty_list.append((name.split()[-1], entry))
			elif category.lower() == 'affiliated':
				affiliated_faculty_list.append((name.split()[-1], entry))
			else:
				print 'Unknown category: %s' % category
			
			instructor_to_proper_name[name.lower()] = name
			
		affiliated_faculty_list.sort()
		
		
		ordered_categories = ['Core Machine Learning', 'Applied Machine Learning']
		for category in category_to_subcategory.keys():
			if category not in ordered_categories:
				print 'Unknown course category: ' + category
				
		for category in ordered_categories:
			subcategory_dict = category_to_subcategory[category]
			self.generateCourseCategoryStart(category, courses_output_file)

			if category == 'Core Machine Learning':
				subcategory_dict_keys_list = ['Introductory', 'Advanced', 'Mathematical, Statistical, and Computational Background']
			else:
				subcategory_dict_keys_list = subcategory_dict.keys()
				subcategory_list.sort()
				
			subcategory_list = []
			for subcategory in subcategory_dict_keys_list:
				course_list = subcategory_dict[subcategory]
				prefix_text = category_prefix_text.setdefault(subcategory, '')
				suffix_text = category_suffix_text.setdefault(subcategory, '')
				subcategory_list.append((subcategory, course_list, prefix_text, suffix_text))
				
			for subcategory, course_list, prefix_text, suffix_text in subcategory_list:
				course_list.sort()
				new_course_list = []
				for key, entry in course_list:
					new_course_list.append(entry)
				self.generateCourseCategory(courses_output_file, new_course_list, subcategory, instructor_to_proper_name, courses_names_to_columns, prefix_text, suffix_text)
			
		
		
		num_names = 0
		#num_names += self.generateFacultyCategory(faculty_output_file, core_faculty_list, 'Core', faculty_names_to_columns, courses_names_to_columns)
		#num_names += self.generateFacultyCategory(faculty_output_file, affiliated_faculty_list, 'Affiliated', faculty_names_to_columns, courses_names_to_columns)
		num_names += self.generateFacultyCategory(faculty_output_file, affiliated_faculty_list, '', faculty_names_to_columns, courses_names_to_columns)
		
		faculty_output_file.close()
		faculty_input_file.close()
		courses_output_file.close()
		courses_input_file.close()
		
		print 'Wrote %d names to faculty file.' % num_names
		print 'Wrote %d courses to courses file.' % num_courses
		
		os.remove(faculty_input_filename)
		os.remove(courses_input_filename)
		

if __name__ == '__main__':
	GenerateMachineLearningPeopleList().run()