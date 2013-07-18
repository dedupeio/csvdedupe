import curses

def main(screen) :
    height, width = screen.getmaxyx()

    screen.refresh()
     
    win = curses.newwin(height, width/2, 0, 0)
    win.addstr(2, 2, str(height))
    win.refresh()

    win = curses.newwin(height, (width/2 + 1), 0, (width/2-1))
    win.addstr(2, 2, str(height))
    win.refresh()


    c = screen.getch()

    output= """
    Phone :  4369244
    Address :  3450-54 w. 79th st
    Zip :  
    Site name :  pathways to learning i/t
    
    Phone :  5635800
    Address :  1701 west superior
    Zip :  60622
    Site name :  erie neighborhood house
    """
    
if __name__ == '__main__' :
   curses.wrapper(main)	      		 	      
