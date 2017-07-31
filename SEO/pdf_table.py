# Remember to install or include reportlab library somehow
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

import csv

doc = SimpleDocTemplate("output.pdf", pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
doc.pagesize = landscape(A4)
elements = []


raw = [[100, 0, 20, 80],
			[0, 100, 0, 50], 
			[20, 0, 100, 0],
			[80, 50, 0, 100]]

data = raw
header = [""]
for x in range(len(data)):
	s = "URL " + str(x + 1)
	header.append(s)
	data[x].insert(0, s)
data.insert(0, header)


# Write csv with column & row names
with open("table.csv", "w", newline = "") as f:
    writer = csv.writer(f)
    writer.writerows(data)


# Define a style for the entire table
# See documentation @ https://www.reportlab.com/docs/reportlab-userguide.pdf page 84
style = TableStyle([('ALIGN',(1,1),(-1,-1),'RIGHT'),
                       ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                       ('TEXTCOLOR',(0,0),(-1,0),colors.blue),
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ])

# Create table from data and assign the style we defined
t=Table(data)
t.setStyle(style)

# Colour according to values.
# x > 0 && Y > 0 is to not parse row / column names
for x in range(len(data)):
    for y in range(len(data[x])):
        if (x > 0 and y > 0 and int(data[x][y]) > 50):
            t.setStyle(TableStyle([('TEXTCOLOR', (x, y), (x, y), colors.red)]))

elements.append(t)
doc.build(elements) # This writes to disk in the current directory.