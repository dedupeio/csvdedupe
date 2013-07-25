import curses

y = 2 # global variable to keep track of printed lines

def printFields(win1, win2 ,value1, value2):
    global y
    win1.addstr(y, 2, value1)
    win1.refresh()

    win2.addstr(y, 2, value2)
    win2.refresh()

    y = y + 1

def printStatement(win, value):
    global y
    win.addstr(y, 2, value)
    win.refresh()

    y = y + 1

def main(screen) :
    height, width = screen.getmaxyx()

    screen.refresh()

    uncertain_pairs = [({'Purple binder service type': '', 'Zip': '60623', 'Site name': 'chicago public schools little village', 'Program Name': '', 'Agency': '', 'Source': 'dfss_agencysitelies_2012.csv', 'Eearly Head Start Fund': '', 'Length of Day': '', 'NAEYC Program Id': '', 'Website': '', 'Program Option': '', 'Fax': '', 'Head Start Fund': '', 'Ounce of Prevention Description': '', 'NAEYC Valid Until': 'elsa carmona', 'Director': '', 'Phone': '5341880', 'Address': '2620 s lawndale ave', 'ECE Available Programs': 'paula cottone', 'CC fund': '', 'Email Address': '', 'Column': '', 'Center Director': 'www.cps.edu', 'Funded Enrollment': 'chicago public schools', 'Column2': '', 'Number per Site EHS': '', 'Neighborhood': '', 'Progmod': '', 'IDHS Provider ID': '', 'Number per Site HS': '', 'Executive Director': '', 'Id': '2031'}, {'Purple binder service type': '', 'Zip': '60623', 'Site name': 'little village', 'Program Name': '', 'Agency': '', 'Source': 'ece chicago find a school scrape.csv', 'Eearly Head Start Fund': '', 'Length of Day': '', 'NAEYC Program Id': '', 'Website': '', 'Program Option': '', 'Fax': '', 'Head Start Fund': '', 'Ounce of Prevention Description': '', 'NAEYC Valid Until': '', 'Director': '', 'Phone': '5341880', 'Address': '2620 s. lawndale', 'ECE Available Programs': 'hs-hd', 'CC fund': '', 'Email Address': '', 'Column': '', 'Center Director': '', 'Funded Enrollment': '', 'Column2': '', 'Number per Site EHS': '', 'Neighborhood': 'south lawndale', 'Progmod': '', 'IDHS Provider ID': '', 'Number per Site HS': '', 'Executive Director': '', 'Id': '2621'})]
    fields = ['Phone', 'Address', 'Zip', 'Site name']
     
    width = int(.7 * width)
    win1 = curses.newwin(height, width/2, 0, 0)
    win2 = curses.newwin(height, (width/2 + 1), 0, (width/2-1))

    printFields(win1, win2, 'Record 1', 'Record 2')
    printFields(win1, win2, '----------------', '---------------')

    for field in fields:
        line_number = printFields(win1, win2, (field + ': ' + uncertain_pairs[0][0][field]), (field + ': ' + uncertain_pairs[0][1][field]))

    printStatement(win1, '')
    printStatement(win1, 'Do these records refer to the same thing?')
    printStatement(win1, '(y)es / (n)o / (u)nsure / (f)inished')

    finished = False
    while finished == False:
        label = screen.getch()
        if label == ord('y'):
            # duplicates.append(record_pair)
            printStatement(win1, 'yup!')
        elif label == ord('n'):
            # nonduplicates.append(record_pair)
            printStatement(win1, 'nope!')
        elif label == ord('f'):
            printStatement(win1, 'Finished labeling')
            finished = True
            break
        elif label != ord('u'):
            printStatement(win1, 'Nonvalid response')
            # raise
    
if __name__ == '__main__' :
   curses.wrapper(main)	      		 	      
