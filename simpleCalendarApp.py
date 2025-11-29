import datetime as dt
import csv
import os

"""Creates a string representation of a Calendar Event and allows ease of access for relative data"""
class Event:
    def __init__(self,t,s,e): #t=title of event, s=start of event, e=end of event
        self.title = t #title of event
        self.startList = s #start date's list of arguments for date objects initialization
        self.startD = dt.date(s[0],s[1],s[2]) #start date, ignoring the specific time
        self.startDT = dt.datetime(s[0],s[1],s[2],s[3],s[4]) #start date, including the specific time
        self.endList = e #end date's list of arguments for date objects initialization
        self.endD = dt.date(e[0],e[1],e[2]) #end date, ignoring the specific time
        self.endDT = dt.datetime(e[0],e[1],e[2],e[3],e[4]) #end date, including the specific time
        self.csvInput = [t] #The list of values representing a row/event in the Calendar csv file
        for l in [s,e]:
            for col in l:
                self.csvInput.append(col)
        
    def __str__(self):
        return f"{self.title}, Start: {self.startDT}, End: {self.endDT}"

class Calendar:
    def __init__(self, fn): 
        self.fileName = fn #self.fileName is the name of the csv file that the Calendar app stores data within
        columnHeaders = ["Event","Start Year","Start Month","Start Day","Start Hour","Start Minute",
                              "End Year","End Month","End Day","End Hour","End Minute"]
        #If the csv file exists, assumes it is for this Calendar app
        if not os.path.exists(fn):
            with open(self.fileName, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columnHeaders)
    
    "Sorts the given list of events in chronological order"
    def sortEvents(self,events,date):
        sortedList = []
        for e in events:
            #Adds to the end of the list if the end date is later than the given date without time or the list is currently empty
            if e.endD > date or len(sortedList) == 0:
                sortedList.append(e)
            #Adds to the front of the list if the start date is earlier than the given date without time
            elif e.startD < date:
                sortedList.insert(0,e)
            else: #Inserts the events into indices where its start date is earlier than the start of the previous index's event
                for i in range(len(sortedList)):
                    if e.startDT < sortedList[i].startDT:
                        sortedList.insert(i,e)
                        break
                    if i == len(sortedList)-1: #Appends the event to the list if its start date is later than the other events
                        sortedList.append(e)
        return sortedList
        
    def getEvent(self,ev):
        evTitle = ev[0]
        evStart = [int(ev[1]),int(ev[2]),int(ev[3]),int(ev[4]),int(ev[5])]
        evEnd = [int(ev[6]),int(ev[7]),int(ev[8]),int(ev[9]),int(ev[10])]
        return Event(evTitle,evStart,evEnd)
    
    """Stores a new event into the csv file if it does not overlap with an existing event"""
    def newEvent(self,t,s,e):#t=title of event, s=start of event, e=end of event
        newE = Event(t,s,e)
        with open(self.fileName, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for ev in reader:
                oldE = self.getEvent(ev)
                #Ensures that the new event does not overlap with existing events
                if not (newE.startDT >= oldE.endDT or newE.endDT <= oldE.startDT):
                    print("\nThis event overlaps with the following event:")
                    print(oldE)
                    input("Press Enter to continue...\n")
                    return
        with open(self.fileName, 'a', newline='') as csvfile: #Writes the new event into a new row in the Calendar csv file
            writer = csv.writer(csvfile)
            writer.writerow(newE.csvInput)
            print("\nThe event has been added to the calendar:")
            print(newE)
            input("Press Enter to continue...\n")

    """Shows the events of the given day"""
    def showDayEvents(self,date,withTime,today): #date=given date
        events = []
        with open(self.fileName, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for ev in reader:
                oldE = self.getEvent(ev)
                #Adds to the list of events of the day
                if not withTime and ((oldE.startD <= date.date() <= oldE.endD) or date.date() == oldE.startD or date.date() == oldE.endD):
                    events.append(oldE)
                #Adds to the list of remaining events of the day
                elif withTime and ((oldE.startDT <= date <= oldE.endDT) or (date.date() == oldE.startD and date <= oldE.startDT)):
                    events.append(oldE)
        date = date.date()
        day = date
        if today:
            day = "today"
        remaining = ""
        if withTime:
            remaining = "remaining "
        if len(events) == 0:
            input(f"\nThere are no {remaining}events for {day}. Press Enter to continue...\n")
        else:    
            events = self.sortEvents(events,date) #Sorts the list of events
            print(f"\nThese are the {remaining}events for {day}.")
            for e in events: #Shows the list of events
                print(e)
            input("Press Enter to continue...\n")

    """Finds the next available time slot for the given day, if there is one available"""
    def findTime(self,gd): #gd=given date with time starting at 00:00
        while True:
            duration = input("Enter the duration you would like to find time for in the following format (hh:mm): ")
            try:
                hrs, mins = int(duration[0:2]), int(duration[3:5])
                if (0 <= hrs < 24) and (0 <= mins < 60) and not (hrs == 0 and mins == 0):
                    break
                input("\nPlease enter a valid duration within 24 hours in the following format: (hh:mm). Press Enter to continue...\n")
            except:
                input("\nPlease enter a valid duration within 24 hours in the following format: (hh:mm). Press Enter to continue...\n")
        timeToAdd = dt.timedelta(hours=hrs, minutes=mins)
        gdEnd = gd + timeToAdd #gdEnd represents the end of the duration that starts from the time of gd
        events = []
        with open(self.fileName, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for ev in reader:
                oldE = self.getEvent(ev)
                if (oldE.startD < gd.date() and gd.date() < oldE.endD) or oldE.startD == gd.date() or oldE.endD == gd.date():
                    events.append(oldE)
        date = gd.date()
        events = self.sortEvents(events, date)
        for e in events:
            if gdEnd <= e.startDT:
                time = gd.time()
                input(f"\nThe next available time slot for this duration on {date} is {time}. Press Enter to continue...\n")
                return
            else:
                gd = e.endDT
                gdEnd = gd + timeToAdd
        if gdEnd.date() != date:
            input(f"\nThere are no available time slots for this duration on {date}. Press Enter to continue...\n")
        else:
            time = gd.time()
            input(f"\nThe next available time slot for this duration on {date} is {time}. Press Enter to continue...\n")

"""If the input in date is properly inputted, the input is validated, and the year, month and day are returned.
   Otherwise, invalidates the user's input"""
def isValidDate(date): #date is the string retrieved from User Input that should represent a date
    try: 
        yr, month, day = int(date[:4]), int(date[5:7]), int(date[8:10])
        dt.datetime(yr,month,day)
        return [True,yr,month,day]
    except:
        input("\nPlease enter a valid date in the following format: (YYYY-MM-DD). Press Enter to continue...\n")
        return [False]

"""Returns a list of the parameters to create a Date object, including hours and minutes"""
def createDate(string): #the string parameter will always be either "starting" or "ending"
    while True:
        date = input(f"Enter the {string} date in the following format (YYYY-MM-DD): ")
        iVD = isValidDate(date) #Ensures that the input follows the requested format
        if iVD[0]:
            break
    while True:
        time = input(f"Enter the {string} time in the following 24-hour clock format (hh:mm): ")
        try: #Ensures that the input follows the requested format
            h, m = int(time[:2]), int(time[3:5])
            dt.datetime(iVD[1],iVD[2],iVD[3],h,m)
            break
        except:
            input("\nPlease enter a valid time in the following 24-hour clock format: (hh:mm). Press Enter to continue...\n")
    return [iVD[1],iVD[2],iVD[3],h,m]

"""Compares the starting and ending dates that are passed through and returns whether the start is before the end"""
def validEvent(s,e):
    start = dt.datetime(s[0],s[1],s[2],s[3],s[4])
    end = dt.datetime(e[0],e[1],e[2],e[3],e[4])
    if start < end:
        return True
    return False

while True:
    file = input("Enter the name of the csv file you want to create or access: ")
    if file[-4:] == ".csv":
        break
    input("\nPlease make sure that your file ends in \".csv\". Press Enter to continue...\n")
cal = Calendar(file)
print()
while True:
    #Display the list of possible actions with corresponding inputs
    print("[1] Create a new event")
    print("[2] View today's events")
    print("[3] View today's remaining events")
    print("[4] View a specific day's events")
    print("[5] Find the next available time for a specific length of time")
    print("[0] Exit")
    choice = input("Enter the corresponding number for what you would like to do: ")
    match choice:
        case "1": #Create an event
            while True:
                title = input("\nEnter the title of the event: ")
                if title != "" and len(title) <= 50: #Ensures that every event has a title to label it
                    break
                input("\nThe title of the event cannot be blank or greater than 50 characters. Press Enter to continue...")
            while True:
                start = createDate("starting")
                end = createDate("ending")
                if validEvent(start,end): #Ensures that the starting date always comes before the ending date and vice versa
                    break
                input("\nThe end of the event must come after the start of the event. Press Enter to continue...\n")
            cal.newEvent(title,start,end) #Creates a new event in the calendar
        case "2": #List today's events
            cal.showDayEvents(dt.datetime.now(),False,True)
        case "3": #List today's remaining events
            cal.showDayEvents(dt.datetime.now(),True,True)
        case "4": #List any day's events
            while True:
                date = input("\nEnter the date you would like to view in the following format (YYYY-MM-DD): ")
                iVD = isValidDate(date)
                if iVD[0]:
                    break
            cal.showDayEvents(dt.datetime(iVD[1],iVD[2],iVD[3]),False,False)
        case "5": #Provide next available slot of specified size
            while True:
                date = input("\nEnter the date you would like to check in the following format (YYYY-MM-DD): ")
                iVD = isValidDate(date)
                if iVD[0]:
                    break
            cal.findTime(dt.datetime(iVD[1],iVD[2],iVD[3]))
        case "0": #Exit the program
            break
        case _:
            input("\nPlease enter a valid number corresponding to one of the choices. Press Enter to continue...\n")
            