import dedupe
from dedupe.training import consoleLabel

import curses

y = 2 # global variable to keep track of printed lines

def label(uncertain_pairs, fields):
  return curses.wrapper(_cursesLabel, (uncertain_pairs, fields))

def _printFields(win1, win2 ,value1, value2):
    global y
    win1.addstr(y, 2, value1)
    win1.refresh()

    win2.addstr(y, 2, value2)
    win2.refresh()

    y = y + 1

def _printStatement(win, value):
    global y
    win.addstr(y, 2, value)
    win.refresh()

    y = y + 1

def _cursesLabel(screen, (uncertain_pairs, fields)):
    '''Command line interface for presenting and labeling training pairs by the user'''
    global y
    duplicates = []
    nonduplicates = []
    finished = False

    height, width = screen.getmaxyx()

    for record_pair in uncertain_pairs:
        screen.clear()
        y = 2
        screen.refresh()
         
        win0 = curses.newwin(3, width, 0, 0)
        win1 = curses.newwin(height-3, width/2, 4, 0)
        win2 = curses.newwin(height-3, (width/2 + 1), 4, (width/2-1))

        #_printStatement(win0, 'Labeling possible record matches. The more you label, the more accurate dedupe will be.')
        # _printStatement(win0, ("Status: %s positive, %s negative" % (len(duplicates), len(nonduplicates))))

        _printFields(win1, win2, 'Record A', 'Record B')
        _printFields(win1, win2, '----------------', '---------------')

        for field in fields:
            line_number = _printFields(win1, win2, (field + ': ' + uncertain_pairs[0][0][field]), (field + ': ' + uncertain_pairs[0][1][field]))

        _printStatement(win1, '')
        _printStatement(win1, 'Do these records refer to the same thing?')
        _printStatement(win1, '(y)es / (n)o / (u)nsure / (f)inished')
        
        label = screen.getch()
        if label == ord('y'):
            duplicates.append(record_pair)
        elif label == ord('n'):
            nonduplicates.append(record_pair)
        elif label == ord('f'):
            _printStatement(win1, 'Finished labeling')
            finished = True
            break
        elif label != ord('u'):
            _printStatement(win1, 'Nonvalid response')
            raise

    return ({0: nonduplicates, 1: duplicates}, finished)
    
if __name__ == '__main__' :

    uncertain_pairs = [({'Purple binder service type': '', 'Zip': '60623', 'Site name': 'chicago public schools little village', 'Program Name': '', 'Agency': '', 'Source': 'dfss_agencysitelies_2012.csv', 'Eearly Head Start Fund': '', 'Length of Day': '', 'NAEYC Program Id': '', 'Website': '', 'Program Option': '', 'Fax': '', 'Head Start Fund': '', 'Ounce of Prevention Description': '', 'NAEYC Valid Until': 'elsa carmona', 'Director': '', 'Phone': '5341880', 'Address': '2620 s lawndale ave', 'ECE Available Programs': 'paula cottone', 'CC fund': '', 'Email Address': '', 'Column': '', 'Center Director': 'www.cps.edu', 'Funded Enrollment': 'chicago public schools', 'Column2': '', 'Number per Site EHS': '', 'Neighborhood': '', 'Progmod': '', 'IDHS Provider ID': '', 'Number per Site HS': '', 'Executive Director': '', 'Id': '2031'}, {'Purple binder service type': '', 'Zip': '60623', 'Site name': 'little village', 'Program Name': '', 'Agency': '', 'Source': 'ece chicago find a school scrape.csv', 'Eearly Head Start Fund': '', 'Length of Day': '', 'NAEYC Program Id': '', 'Website': '', 'Program Option': '', 'Fax': '', 'Head Start Fund': '', 'Ounce of Prevention Description': '', 'NAEYC Valid Until': '', 'Director': '', 'Phone': '5341880', 'Address': '2620 s. lawndale', 'ECE Available Programs': 'hs-hd', 'CC fund': '', 'Email Address': '', 'Column': '', 'Center Director': '', 'Funded Enrollment': '', 'Column2': '', 'Number per Site EHS': '', 'Neighborhood': 'south lawndale', 'Progmod': '', 'IDHS Provider ID': '', 'Number per Site HS': '', 'Executive Director': '', 'Id': '2621'})]
    fields = ['Phone', 'Address', 'Zip', 'Site name']
    val = curses.wrapper(_cursesLabel(uncertain_pairs, fields))
    print val
