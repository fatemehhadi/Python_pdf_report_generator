# Author: Fatemeh Hadi
# Date: 2019/08
# Purpose: This code generates a report in PDF format using image, data and text files.
# External libraries used: ReportLab
# Compiler: Python 2

import time
import csv
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph, Spacer, Image, Table
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, NextPageTemplate
from reportlab.platypus.frames import Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import inch
from reportlab.lib import utils
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import yellow, red, black, white
from reportlab.platypus import PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
import os.path
from reportlab.rl_config import defaultPageSize
page_height = defaultPageSize[1]; page_width = defaultPageSize[0]

# Global and Modifiable Variables
Title = "Report"
Version = "Version 000"
pageinfo1 = "Page info 1"
pageinfo2 = "Page info 2"
logo = "Logo.png"

global_path = '/home/username/Work/Results/'
data_names = ['data_1.csv','data_2.csv']
image_names = ['image_1.png','image_2.png']

print "\nImage and csv files are located in a path like:"
print global_path
print "\nThe code looks for the follwoing csv files:"
for i in range(len(data_names)):
        print data_names[i][:]
print "\nThe code looks for the follwoing image files:"
for i in range(len(image_names)):
    print image_names[i][:]
message = "\nDo you want to enter the path name using command line? [Y/N] "
answer = raw_input(message)
if (answer == 'Y' or answer == 'y'):
    global_path = raw_input("\nEnter path: ")
elif (answer == 'N' or answer == 'n'):
    message = '''Using the existing path and folder name. The path can be 
    altered on line 28.'''
    print 
else:
    message = '''Incorrect input. Using the existing path and folder name. The path
     can be altered on line 28.'''
    print message

B_add_logo = False
B_add_time = False
B_add_data_screen = True

B_introduction = os.path.exists('Text/introduction.txt')
B_discussion = os.path.exists('Text/discussion.txt')
B_conclusion = os.path.exists('Text/conclusion.txt')

toc = TableOfContents()
styles=getSampleStyleSheet()
h1 = PS(fontName='Times-Bold', fontSize=14, name='Heading1',leftIndent=20, 
        firstLineIndent=-20, spaceBefore=5, leading=16)
h2 = PS(fontSize=12, name='Heading2', leftIndent=40, firstLineIndent=-20, 
        spaceBefore=0, leading=12)
h3 = PS(fontSize=10, name='Heading3', leftIndent=60, firstLineIndent=-20, 
        spaceBefore=0, leading=10)
h4 = PS(fontSize=10, name='Heading4', leftIndent=100, firstLineIndent=-20, 
        spaceBefore=0, leading=8)
toc.levelStyles = [h1, h2, h3, h4]
styles.add(PS(name='Justify', alignment=TA_JUSTIFY))

u = inch/10.0

divide_string_threshold = 12
table_font_size = 8
text_font_size = 10

# Functions
def title_page(canvas, doc):
    canvas.saveState()
    add_title_header(canvas)
    add_title_title(canvas)
    add_title_footer(canvas)
    canvas.restoreState()

def add_title_header(canvas):
    aspect_ratio = get_aspect_ratio(logo)
    logo_width = 0.9*inch
    canvas.drawImage(logo, doc.leftMargin, page_height-1.2*inch, width=logo_width, 
                     height=logo_width*aspect_ratio, mask=None)
    canvas.setFillColor(black)
    canvas.rect(doc.leftMargin, page_height-1.2*inch, text_width,u/2.0, stroke=1, fill=1)

def add_title_footer(canvas):
    canvas.setFillColor(black)
    canvas.rect(doc.leftMargin, 0.75*inch+inch/8.0, text_width,u/7.0, stroke=1, fill=1)
    canvas.setFont('Times-Roman',9)
    canvas.drawCentredString(page_width/2.0, 0.75*inch, "%s" % pageinfo1)

def add_title_title(canvas):
    canvas.setFont('Times-Bold',16)
    canvas.drawRightString(doc.leftMargin+text_width, page_height/2.0, Title)
    canvas.setFillColor(black)
    canvas.rect(doc.leftMargin, page_height/2.0-u, text_width,u/10.0, stroke=1, fill=1)
    canvas.setFont('Times-Roman',10)
    canvas.drawRightString(doc.leftMargin+text_width, page_height/2.0-3*u, Version)
    canvas.drawRightString(doc.leftMargin+text_width, page_height/2.0-5*u, time.ctime())

def later_pages(canvas, doc):
    canvas.saveState()
    add_later_header(canvas)
    add_later_footer(canvas)
    canvas.restoreState()

def add_later_header(canvas):
    canvas.setFont('Times-Roman',9)
    canvas.drawCentredString(page_width/2.0, page_height-(0.75*inch+u/2),
                             "%s" % pageinfo2)
    canvas.setFillColor(black)
    canvas.rect(doc.leftMargin, page_height-(0.75*inch+inch/8.0), text_width,u/7.0,
                stroke=1, fill=1)

def add_later_footer(canvas):
    canvas.setFont('Times-Roman',9)
    canvas.drawRightString(doc.leftMargin + text_width, 0.75*inch+inch/6.0,
                           "%d" % doc.page)
    canvas.setFillColor(black)
    canvas.rect(doc.leftMargin, 0.75*inch+inch/8.0, text_width, u/7.0, stroke=1, fill=1)

class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        frameT = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                       id='F1')
        template_title_page = PageTemplate('title_page', frames=frameT,
                                           onPage=title_page)
        template_later_pages = PageTemplate('later_pages', frames=frameT,
                                            onPage=later_pages)
        self.addPageTemplates(template_title_page)
        self.addPageTemplates(template_later_pages)
    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))
            if style == 'Heading2':
                self.notify('TOCEntry', (1, text, self.page))

doc = MyDocTemplate('Report.pdf')

text_width = doc.pagesize[0]-doc.leftMargin-doc.rightMargin
image_width = 0.9 * text_width

def add_logo():
    Report.append(get_image(logo, width=2*inch))

def add_time():
    formatted_time = time.ctime()
    ptext = '<font size=%d>%s</font>' % (text_font_size, formatted_time) 
    Report.append(Paragraph(ptext, styles["Normal"]))
    Report.append(Spacer(1, 12))

def add_data_screen(data_path,data_name):
    print "\nData file name: ", data_name
    with open(data_path) as csv_file:
        data = csv.reader(csv_file, delimiter=',')
        for row in data:
            print ', '.join(row)
        z = csv.reader(csv_file, delimiter='\t')

def fix_data_list(data_list):
    B_add_item_screen = False
    for row in data_list:
        for index in range(len(row)):
            item = row[index]
            if len(item) > divide_string_threshold:
                if B_add_item_screen: print len(item), item
                position = 0
                for x in range(1,len(item)//divide_string_threshold+1):
                    item = item[:x*divide_string_threshold+position] + '\n' +\
                           item[x*divide_string_threshold+position:]
                    position += 1
                if B_add_item_screen: print len(item), item
                row[index] = item

    return data_list

def add_data(data_path,data_name):
    B_data = os.path.exists(data_path)
    if B_data:
        if B_add_data_screen: add_data_screen(data_path,data_name)
        with open(data_path) as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            data_list=list(data)
            fix_data_list(data_list)
            data_list = map(list, zip(*data_list))
            t=Table(map(list, zip(*data_list[0:len(data_list)][:])),style=[
                                ('BOX',(0,0),(-1,-1),2,colors.black),
                                ('GRID',(0,0),(-1,-1),0.5,colors.black),
                                ('FONTSIZE',(0,0),(-1,-1),table_font_size)
                                ,])
            Report.append(t)

        Report.append(Spacer(1, 12))

        ptext = '<font size=%d>Data address: %s</font>' % (text_font_size, data_path)
        Report.append(Paragraph(ptext, styles["Normal"]))
        Report.append(Spacer(1, 12))

        ptext = '<font size=%d>Data name: %s</font>' % (text_font_size, data_name)
        Report.append(Paragraph(ptext, styles["Normal"]))
        Report.append(PageBreak())

def add_events_data():
    for i in range(len(data_names)):
        data_name=data_names[i][:]
        data_path=global_path+data_name
        add_data(data_path,data_name)

def get_image(image_path, width):
    img = utils.ImageReader(image_path)
    iw, ih = img.getSize()
    aspect_ratio = ih / float(iw)
    return Image(image_path, width=width, height=(width * aspect_ratio))

def get_aspect_ratio(image_path):
    img = utils.ImageReader(image_path)
    iw, ih = img.getSize()
    aspect_ratio = ih / float(iw)
    return aspect_ratio

def add_image(image_path,image_name,given_width):
    B_image = os.path.exists(image_path)
    if B_image:
        Report.append(get_image(image_path, width=given_width))
        Report.append(Spacer(1, 12))

        ptext = '<font size=%d>Image address: %s</font>' % (text_font_size,image_path)
        Report.append(Paragraph(ptext, styles["Normal"]))
        Report.append(Spacer(1, 12))

        ptext = '<font size=%d>Image name: %s</font>' % (text_font_size, image_name)
        Report.append(Paragraph(ptext, styles["Normal"]))
        Report.append(PageBreak())

def add_events_images():
    for i in range(len(image_names)):
        image_name=image_names[i][:]
        image_path=global_path+image_name
        add_image(image_path,image_name,image_width)

def add_toc():
    Report.append(NextPageTemplate('later_pages'))
    Report.append(PageBreak())
    Report.append(toc)
    Report.append(PageBreak())

def add_introduction():
    Report.append(Paragraph('Introduction',  h1))
    Report.append(Spacer(1, 12))
    with open("Text/introduction.txt", "r") as f:
        file_content = f.read()
        f.close()
    ptext = '<font size=%d>%s</font>' % (text_font_size,file_content)
    Report.append(Paragraph(ptext, styles["Normal"]))
    Report.append(Spacer(1, 12))

def add_results():
    Report.append(Paragraph('Results',  h1))
    Report.append(Spacer(1, 12))
    Report.append(Paragraph('Data',  h2))
    Report.append(Spacer(1, 12))
    add_events_data()
    Report.append(Paragraph('Plots',  h2))
    Report.append(Spacer(1, 12))
    add_events_images()
    
def add_discussion():
    Report.append(Paragraph('Discussion',  h1))
    Report.append(Spacer(1, 12))
    with open("Text/discussion.txt", "r") as f:
        file_content = f.read()
        f.close()
    ptext = '<font size=%d>%s</font>' % (text_font_size,file_content)
    Report.append(Paragraph(ptext, styles["Normal"]))
    Report.append(Spacer(1, 12))

def add_conclusion():
    Report.append(Paragraph('Conclusion',  h1))
    Report.append(Spacer(1, 12))
    with open("Text/conclusion.txt", "r") as f:
        file_content = f.read()
    f.close()
    ptext = '<font size=%d>%s</font>' % (text_font_size,file_content)
    Report.append(Paragraph(ptext, styles["Normal"]))
    Report.append(Spacer(1, 12))
    Report.append(PageBreak())

# Main program
if __name__ == '__main__':
    Report=[]
    if B_add_logo: add_logo()
    if B_add_time: add_time()
    add_toc()
    if B_introduction: add_introduction()
    add_results()
    if B_discussion: add_discussion()
    if B_conclusion: add_conclusion()
    doc.multiBuild(Report)
    print ""