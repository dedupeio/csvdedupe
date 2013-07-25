import curses

def printFields(win1, win2 ,value1, value2, y):
    win1.addstr(y, 2, value1)
    win1.refresh()

    win2.addstr(y, 2, value2)
    win2.refresh()

    return y + 1

def printStatement(win, value, y):
    win.addstr(y, 2, value)
    win.refresh()

    return y + 1

def main(screen) :
    height, width = screen.getmaxyx()

    screen.refresh()

    uncertain_pairs = [({'Purple binder service type': '', 'Zip': '60623', 'Site name': 'chicago public schools little village', 'Program Name': '', 'Agency': '', 'Source': 'dfss_agencysitelies_2012.csv', 'Eearly Head Start Fund': '', 'Length of Day': '', 'NAEYC Program Id': '', 'Website': '', 'Program Option': '', 'Fax': '', 'Head Start Fund': '', 'Ounce of Prevention Description': '', 'NAEYC Valid Until': 'elsa carmona', 'Director': '', 'Phone': '5341880', 'Address': '2620 s lawndale ave', 'ECE Available Programs': 'paula cottone', 'CC fund': '', 'Email Address': '', 'Column': '', 'Center Director': 'www.cps.edu', 'Funded Enrollment': 'chicago public schools', 'Column2': '', 'Number per Site EHS': '', 'Neighborhood': '', 'Progmod': '', 'IDHS Provider ID': '', 'Number per Site HS': '', 'Executive Director': '', 'Id': '2031'}, {'Purple binder service type': '', 'Zip': '60623', 'Site name': 'little village', 'Program Name': '', 'Agency': '', 'Source': 'ece chicago find a school scrape.csv', 'Eearly Head Start Fund': '', 'Length of Day': '', 'NAEYC Program Id': '', 'Website': '', 'Program Option': '', 'Fax': '', 'Head Start Fund': '', 'Ounce of Prevention Description': '', 'NAEYC Valid Until': '', 'Director': '', 'Phone': '5341880', 'Address': '2620 s. lawndale', 'ECE Available Programs': 'hs-hd', 'CC fund': '', 'Email Address': '', 'Column': '', 'Center Director': '', 'Funded Enrollment': '', 'Column2': '', 'Number per Site EHS': '', 'Neighborhood': 'south lawndale', 'Progmod': '', 'IDHS Provider ID': '', 'Number per Site HS': '', 'Executive Director': '', 'Id': '2621'})]
    fields = ['Phone', 'Address', 'Zip', 'Site name']
     
    width = int(.7 * width)
    win1 = curses.newwin(height, width/2, 0, 0)
    win2 = curses.newwin(height, (width/2 + 1), 0, (width/2-1))

    line_number = 2
    line_number = printFields(win1, win2, 'Record 1', 'Record 2', line_number)
    line_number = printFields(win1, win2, '----------------', '---------------', line_number)

    for field in fields:
        line_number = printFields(win1, win2, (field + ': ' + uncertain_pairs[0][0][field]), (field + ': ' + uncertain_pairs[0][1][field]), line_number)

    line_number = printStatement(win1, '', line_number)
    line_number = printStatement(win1, 'Do these records refer to the same thing?', line_number)
    line_number = printStatement(win1, '(y)es / (n)o / (u)nsure / (f)inished', line_number)
    
if __name__ == '__main__' :
   curses.wrapper(main)	      		 	      
