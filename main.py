# os library
import os.path
from tkinter.scrolledtext import ScrolledText
from dateutil.relativedelta import relativedelta

# utils py
import utils

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Tkinter libraries
from tkinter import *
from tkcalendar import Calendar

# Calendar libraries
import calendar
from datetime import datetime

PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"

# OS setting home folder
home_folder = os.path.dirname(__file__)

# date variables setting by first day and last day of month
date_today = datetime.now()
from_day = date_today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
to_day = datetime(date_today.year, date_today.month, calendar.monthrange(date_today.year, date_today.month)[1])

#google creds saved
creds = None
# select keys of each mail
selected_shop_list_keys = []
# Tk declararion
root = Tk()
# result messages
messages = []

def searchShoppings():
  global creds, selected_shop_list_keys, select_var, select_shop_list_key, root, messages, total_tickets_label, from_day, to_day
  #obtain creds to make service queries
  creds = utils.obtain_google_token(creds, home_folder)
  print( f"+------------SCANNING FROM {from_day} TO {to_day} -------------+" )
  # try to obtain results from google gmail
  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = utils.search_messages(service, "Mercadona *", from_day, to_day)
    # process results
    messages = []
    for msg in results:
      messages.append(utils.read_message(service, msg))
    # Insert list of new options
    select_var.set("")
    select_shop_list_key['menu'].delete(0, 'end')
    total_price = 0
    for choice in messages:
      subject = choice.subject.split(' ')
      price = float(subject[2].replace(',', '.'))
      name = f"{subject[0]} - {subject[2]}{subject[3]}"
      total_price += price
      select_shop_list_key['menu'].add_command(label=name, command=lambda x=choice, name=name: show_ticket(x, name))
    total_tickets_label.config(text=f"Total:{round(total_price, 2)}€")
  except HttpError as error:
    print(f"An error occurred: {error}")
      
def show_ticket(choice, name):
  global textArea, select_var
  select_var.set(name) # default value
  textArea.replace("1.0", END, '\n'.join(line + '\n' for line in choice.objects))
    
def pick_date(event, day, date_entry, is_from):
  global cal, delete_window
  
  date_window = Toplevel()
  date_window.grab_set()
  date_window.title('Choose date:')
  # Add Calendar
  cal = Calendar(date_window, selectmode = 'day',
                year = day.year, 
                month = day.month,
                day = day.day)
  cal.place(x=0, y=0)
  
  submit_btn = Button(date_window, text="Submit", command= lambda is_from=is_from, de=date_entry: grab_date(de, is_from))
  submit_btn.place(x=80, y=190)
  delete_window = date_window

def grab_date(de, is_from):
  global from_day, to_day
  de.delete(0, END)
  if is_from:
    from_day = cal.selection_get()
    de.insert(0, f"{from_day.strftime('%Y/%m/%d')}")
    print("changing 'from date'")
  else:
    to_day = cal.selection_get()
    de.insert(0, f"{to_day.strftime('%Y/%m/%d')}")
    print("changing 'to date'")
  delete_window.destroy()

def move_months(orientation):
  global from_day, to_day, date_to_value, date_from_value
  # Update variables
  if orientation > 0:
    from_day = from_day + relativedelta(months=1)
    to_day = to_day + relativedelta(months=1)
  else:
    from_day = from_day - relativedelta(months=1)
    to_day = to_day - relativedelta(months=1)
  # Update labels
  date_from_value.delete(0, END)
  date_from_value.insert(0, f"{from_day.strftime('%Y/%m/%d')}")
  
  date_to_value.delete(0, END)
  date_to_value.insert(0, f"{to_day.strftime('%Y/%m/%d')}")
  

def main():
  global select_var, select_shop_list_key, ticket_var, textArea, total_tickets_label, date_from_value, date_to_value
  
  # Set geometry
  root.config(padx=50, pady=20)
  
  #Image background load
  image1 = PhotoImage(f"{home_folder}/logo-Mercadona.png")
  reference_to_image = Canvas(root)
  reference_to_image.image = image1

  # logo img
  """ logo_frame = Frame(
           master=root,
           relief=RAISED
       )
  logo_frame.grid(row=0, column=0, rowspan=4, columnspan=4) 
  for count in range(10):
      canvas = Canvas(logo_frame)
      canvas.pack(side = LEFT)
      for counter in range(10):
          label1 = Label(canvas, image=image1, borderwidth=0, highlightthickness=0)
          label1.pack(side=LEFT) """
  
  date_frame = Frame(
           master=root,
           relief=RAISED,
           borderwidth=1
       )
  date_frame.grid(row=0, column=1) 
  
  label1 = Label(date_frame, image=image1, borderwidth=0, highlightthickness=0, width=50)
      
  # date from label
  date_from_label = Label(date_frame, text="Date from:", font=("Bahnschrift", 20, "italic"))
  date_from_label.grid(column=1, row=0, padx=10, pady=5)
  
  # date from value and button to change it
  date_from_value = Entry(date_frame, font=("Bahnschrift", 15, "bold"))
  date_from_value.insert(0, f"{from_day.strftime('%Y/%m/%d')}")
  date_from_value.grid(column=1, row=1, padx=10, pady=5)
  date_from_value.bind("<1>", lambda event, day=from_day, day_entry=date_from_value: pick_date(event, day, day_entry, True))
  
  # date to label
  date_to_label = Label(date_frame, text=f"Date to:", font=("Bahnschrift", 20, "italic"))
  date_to_label.grid(column=3, row=0, padx=10, pady=10)
  
  # date to value and button to change it
  date_to_value = Entry(date_frame, font=("Bahnschrift", 15, "bold"))
  date_to_value.insert(0, f"{to_day.strftime('%Y/%m/%d')}")
  date_to_value.grid(column=3, row=1, padx=10, pady=5)
  date_to_value.bind("<1>", lambda event, day=to_day, day_entry=date_to_value: pick_date(event, day, day_entry, False))
  
  # Add Button and Label
  submit_btn = Button(date_frame, text="Search Tickets", font=("Bahnschrift", 18, "bold"), command = searchShoppings, width=30, height=1)
  submit_btn.grid(column=1, row= 2, columnspan=3, pady=5, padx=10)
  
  # Substract month button
  less_month_btn = Button(date_frame, text="<<", font=("Bahnschrift", 15, "bold"), command = lambda x=-1: move_months(x), width=5, height=1)
  less_month_btn.grid(column=0, row= 1, pady=5, padx=7)
  
  # Add month button
  add_month_btn = Button(date_frame, text=">>", font=("Bahnschrift", 15, "bold"), command = lambda x=1: move_months(x), width=5, height=1)
  add_month_btn.grid(column=4, row= 1, pady=5, padx=7)
  
  
  # Result frame declaration
  results_frame = Frame(
      master=root,
      relief=RAISED,
      borderwidth=2,
      background=GREEN)
  results_frame.grid(row=1, column=1, pady=25)
  
  #select shopList
  select_var = StringVar(root)
  selected_shop_list_keys = [""]
  select_var.set("All")
  select_shop_list_key= OptionMenu(results_frame, select_var, *selected_shop_list_keys)
  select_shop_list_key.config(width=50)
  select_shop_list_key.grid(column=0, row=0, columnspan=2, sticky="W", padx=10)
  
  # Total tickets found
  total_tickets_label = Label(results_frame, text=f"Total: ", font=("Bahnschrift", 15, "italic"), anchor="w")
  total_tickets_label.grid(column=1, row=0, sticky="E", padx=5)
  total_tickets_label.config(width=15, background=GREEN)
  
  # shop list text area
  textArea = ScrolledText(results_frame, font='Bahnschrift 12', relief="solid", pady=10, width=100, height=20, padx=10)
  textArea.grid(column=0, row=3, columnspan=2)
  
  # Execute Tkinter
  root.mainloop()

if __name__ == "__main__":
  main()