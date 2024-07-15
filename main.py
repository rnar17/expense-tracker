# basic Tkinter modules for GUI creation
from tkinter import ttk
from tkcalendar import *
from functools import partial

# data visualization modules
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style

# miscellaneous modules
from title_page import *
from datetime import datetime
from tkinter import filedialog
from PIL import ImageTk
import csv
import os

matplotlib.use('TkAgg')
style.use("ggplot")


# SET COLOUR CONSTANTS
BG_COLOUR = '#202124'
HOVER_COLOUR = "#CDB7F6"
DARK_PINK = "#e75480"
PURPLE = "#CDB7F6"


# function to change properties of button on hover
def change_on_hover(button):
    button.bind("<Enter>", func=lambda e: button.config(
        background=HOVER_COLOUR, foreground="black"))

    # background color on leaving widget
    button.bind("<Leave>", func=lambda e: button.config(
        background=BG_COLOUR, foreground="white"))


# Main screen class (tabs will be created on top of this layout)
class Main(Tk):
    def __init__(self):
        super().__init__()

        # app width and height
        APP_WIDTH = 813
        APP_HEIGHT = 650

        # set window features
        self.geometry(f'{APP_WIDTH}x{APP_HEIGHT}+{startup_screen.win_x_coord}+{startup_screen.win_y_coord}')

        # set window title
        self.title("Expense Tracker")

        # set colours scheme for widgets
        self.tk_setPalette(background=BG_COLOUR, foreground='white',
                           activeBackground=HOVER_COLOUR, activeForeground='white',
                           disabledbackground="white", disabledforeground="black")

        # SET IMAGE CONSTANTS
        self.REFRESH_IMAGE = ImageTk.PhotoImage(file="refresh.png")
        self.CHART_IMAGE = ImageTk.PhotoImage(file="chart.png")

        # SET FONT CONSTANTS
        self.BOLD_FONT = Font(family="Calibri", size=20, weight="bold")
        self.REGULAR_FONT = Font(family="Calibri", size=20)

        # make username accessible to other classes
        self.username = self.get_username()

        # connect/create table of categories from database
        START_CATEGORIES = ["Investments", "Education", "Entertainment", "Fees & Charges", "Personal Care", "Taxes",
                            "Travel", "Food & Dining", "Home", "Kids", "Shopping", "Bills & Utilities"]

        if len(query_categories(self.username)) == 0:
            for category in START_CATEGORIES:
                insert_category(self.username, category)

        # Add some style to the ttk module (used later for table formation)
        ttk_style = ttk.Style()
        ttk_style.theme_use('default')

        # configure the ttk colours for its different views (Treeview, Notebook view)
        ttk_style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        ttk_style.configure("TNotebook", background=DARK_PINK, borderwidth=0)
        ttk_style.configure("TNotebook.Tab", background=DARK_PINK, borderwidth=0)
        ttk_style.configure("TNotebook.Tab", focuscolor=PURPLE, borderwidth=0)
        ttk_style.map("Treeview", background=[('selected', DARK_PINK)])
        ttk_style.map("TNotebook.Tab", background=[("selected", PURPLE)])

        # Create Notebook (from the ttk module) to add tabs onto
        notebook = ttk.Notebook(self)

        # Tab1 - Home
        self.home_screen = HomeTab(self)
        notebook.add(self.home_screen, text='Dashboard')

        # Tab2 - Expenses
        self.expense_screen = ExpenseTab(self)
        notebook.add(self.expense_screen, text='Expenses')

        # Tab3 - Budgets
        self.budget_screen = BudgetTab(self)
        notebook.add(self.budget_screen, text='Budgets')

        # Tab4 - Stats
        self.stats_screen = StatsTab(self)
        notebook.add(self.stats_screen, text='Stats')

        # expanding tabs to their size
        notebook.pack(expand=1, fill="both")
        self.resizable(width=False, height=False)

    # getter method to access private username variable throughout file
    def get_username(self):
        # set username
        self._username = startup_screen.login_username.get()
        return self._username


# Home Tab (Dashboard)
class HomeTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # create export button
        notify_btn = Button(self, text="Notifications", command=self.notify)
        notify_btn.pack(padx=5, pady=(5, 0), anchor=NE)
        change_on_hover(notify_btn)

        # create Welcome label
        label = Label(self, text=f"Welcome back {parent.username}!", font=parent.BOLD_FONT)
        label.pack(side=TOP, padx=74, pady=(30, 0), anchor=NW)

        # set and format current month/year
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_year_name = datetime.strptime(str(current_year), '%Y')
        current_year_name = current_year_name.strftime("%Y")
        current_month_name = datetime.strptime(str(current_month), "%m")
        current_month_name = current_month_name.strftime("%B")

        # set lists to determine savings
        budgets = query_budgets(parent.username)
        expenses = fetch_expenses_from(parent.username, current_month_name, current_year_name)
        self._savings = []

        # algorithm to create a list of tuples that shows monthly savings in relation to budget
        for budget in budgets:
            budget_category = budget[1]
            budget_amt = float(budget[2])
            for expense in expenses:
                expense_category = expense[3]
                if budget_category == expense_category:
                    expense_amt = float(expense[2])
                    self._savings.append((budget_category, budget_amt - expense_amt))

        for budget in budgets:
            budget_category = budget[1]
            budget_amt = float(budget[2])
            if budget_category not in [saving[0] for saving in self._savings]:
                self._savings.append((budget_category, budget_amt))

        # Button to display categories
        display_cat_btn = Button(self, text="Display Categories", width=25, height=2,
                                 font=Font(family="Fixedsys", size=14, weight="bold"),
                                 command=partial(self._display_categories, parent))
        display_cat_btn.pack(padx=74, pady=10, anchor=NW)
        change_on_hover(display_cat_btn)

        # Button to add category
        add_cat_btn = Button(self, text="Add Category", width=25, height=2,
                             font=Font(family="Fixedsys", size=14, weight="bold"),
                             command=partial(self._add_category_page, parent))
        add_cat_btn.pack(padx=74, pady=10, anchor=NW)
        change_on_hover(add_cat_btn)

        # Buttons to display savings for current month
        top_savings_btn = Button(self, text="Top Monthly Savings", width=25, height=2,
                                 font=Font(family="Fixedsys", size=14, weight="bold"),
                                 command=partial(self.top_monthly_savings))
        top_savings_btn.pack(padx=74, pady=10, anchor=NW)
        change_on_hover(top_savings_btn)

        bottom_savings_btn = Button(self, text="Bottom Monthly Savings", width=25, height=2,
                                    font=Font(family="Fixedsys", size=14, weight="bold"),
                                    command=partial(self.bottom_monthly_savings))
        bottom_savings_btn.pack(padx=74, pady=10, anchor=NW)
        change_on_hover(bottom_savings_btn)

        # display savings table for current month
        self.display_savings_table(parent.username)

    def _display_categories(self, parent):
        # create display category window
        self.display_cat_window = Toplevel()
        self.display_cat_window.geometry(f"300x450+{int(self.winfo_rootx())}+{int(self.winfo_rooty())}")
        self.display_cat_window.title("Categories")

        # create frame for list
        frame = Frame(self.display_cat_window)
        # create scrollbar for list of categories
        scrollbar = Scrollbar(frame)

        # create list of categories
        self.category_list = Listbox(frame, yscrollcommand=scrollbar.set, width=45, height=12, selectmode="single",
                                     foreground="white", font=Font(family="Calibri", size=16), selectforeground="black",
                                     selectbackground=DARK_PINK, activestyle="none")

        scrollbar.config(command=self.category_list.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        # insert the categories into the ListBox
        for category in query_categories(parent.username):
            self.category_list.insert(END, category)
        self.category_list.pack(pady=20, padx=10)
        frame.pack()

        # add buttons for adding and deleting categories
        add_cat_btn = Button(frame, text="Add Category",
                             command=partial(self._add_category_page, parent)).pack()
        Label(frame, text="").pack()
        del_cat_btn = Button(frame, text="Delete Category",
                             command=partial(self._delete_category, parent)).pack()

    # add category
    def _add_category(self, parent):
        if self.new_category.get().strip() and self.new_category.get().replace(" ", "").isalpha():
            insert_category(parent.username, self.new_category.get())
        else:
            messagebox.showerror("Oops!", "Please enter a valid category\n(no digits/symbols)")
        ExpenseTab.update_categories(parent.expense_screen, parent)
        BudgetTab.update_categories(parent.budget_screen, parent)
        self.add_cat_window.destroy()
        if hasattr(self, "display_cat_window"):
            self.display_cat_window.destroy()
        self._display_categories(parent)

    def _add_category_page(self, parent):
        self.add_cat_window = Toplevel()
        self.add_cat_window.title("")
        self.add_cat_window.geometry(f"250x125+{int(self.winfo_rootx())}+{int(self.winfo_rooty())}")

        self.new_category = StringVar()
        Label(self.add_cat_window, text="").pack()
        Label(self.add_cat_window, text="New Category").pack()
        cat_entry = Entry(self.add_cat_window, textvariable=self.new_category)
        cat_entry.pack()
        submit_btn = Button(self.add_cat_window, text="Submit", command=partial(self._add_category,
                                                                                parent))
        submit_btn.pack(pady=20)

    def _delete_category(self, parent):
        cat_to_delete = self.category_list.get(ANCHOR)
        self.display_cat_window.destroy()
        delete_category(parent.username, cat_to_delete)
        ExpenseTab.update_categories(parent.expense_screen, parent)
        BudgetTab.update_categories(parent.budget_screen, parent)
        self._display_categories(parent)

    def top_monthly_savings(self):
        if len(self._savings) == 0:
            messagebox.showerror("Alert!", "Please add more information")
        else:
            self._savings.sort(key=lambda x: x[1])
            self._savings.reverse()
            savings = self._savings[:5]

            amt_savings = [saving[1] for saving in savings]
            cat_savings = [saving[0] for saving in savings]

            # hide every other x tick
            plt.figure(figsize=(5, 3), dpi=100)
            plt.barh(cat_savings, amt_savings, color=PURPLE)

            # hide every other x tick
            ax = plt.gca()
            temp = ax.xaxis.get_ticklabels()
            print(set(temp))
            print(set(temp[::2]))
            temp = list(set(temp) - set(temp[1::2]))

            for tick in temp:
                tick.set_visible(False)

            plt.title('Top Monthly Savings ($)')
            plt.subplots_adjust(left=0.27, right=0.86, bottom=0.15, top=0.88)
            plt.show()

    def bottom_monthly_savings(self):
        if len(self._savings) == 0:
            messagebox.showerror("Alert!", "Please add more information")
        else:
            self._savings.sort(key=lambda x: x[1])
            self._savings = self._savings[:5]

            amt_savings = [saving[1] for saving in self._savings]
            cat_savings = [saving[0] for saving in self._savings]

            plt.figure(figsize=(5, 3), dpi=100)
            plt.barh(cat_savings, amt_savings, color=DARK_PINK)

            # hide every other x tick
            ax = plt.gca()
            temp = ax.xaxis.get_ticklabels()
            temp = list(set(temp) - set(temp[1::2]))
            for tick in temp:
                tick.set_visible(False)

            plt.title('Bottom Monthly Savings ($)')
            plt.xlabel('$')
            plt.subplots_adjust(left=0.27, right=0.86, bottom=0.15, top=0.88)
            plt.show()

    def display_savings_table(self, user):
        # set and format current month/year
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_year_name = datetime.strptime(str(current_year), '%Y')
        current_year_name = current_year_name.strftime("%Y")
        current_month_name = datetime.strptime(str(current_month), "%m")
        current_month_name = current_month_name.strftime("%B")

        # set lists to create chart
        expenses = fetch_expenses_from(user, current_month_name, current_year_name)
        budgets = query_budgets(user)
        budget_amounts = [budget[2] for budget in budgets]
        budget_categories = [category[1] for category in budgets]
        categories = [category for category in query_categories(user)]
        categories = list(dict.fromkeys(categories))
        expense_categories = {}

        for category in categories:
            expense_amount = [
                float(expense[2]) for expense in expenses if expense[3] == category
            ]
            expense_categories[category] = sum(expense_amount)

        # creates a dictionary in the form {category: budget}
        budget_dict = {budget_categories[i]: budget_amounts[i] for i in range(len(budget_categories))}
        category_budget_dict = {}
        for budget_category in budget_dict:
            for category in categories:
                if category == budget_category:
                    category_budget_dict[category] = float(budget_dict[budget_category])
                else:
                    continue

        # creates a dictionary that associates categories with their respective budgets, total expenses, and savings
        self.expense_sum_dict = {
            cat: (category_budget_dict[cat], expense_categories[cat],
                  category_budget_dict[cat] - expense_categories[cat])
            for cat in category_budget_dict
        }

        # create a Treeview frame
        self.tree_frame = LabelFrame(self, text="Savings Table", font=Font(family="Calibri", size=15, weight="bold"))
        self.tree_frame.place(x=400, y=100)

        # create a Treeview scrollbar
        self.tree_scroll = Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=RIGHT, fill=Y)

        # create the Treeview table
        self.savings_table = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="extended",
                                          height=14)
        self.savings_table.pack()

        # configure the scrollbar
        self.tree_scroll.config(command=self.savings_table.yview)

        # define our columns
        self.savings_table['columns'] = ("Category", "Budget", "Spent", "Savings")

        # format our columns
        self.savings_table.column("#0", width=0, stretch=NO)
        self.savings_table.column("Category", anchor=W, width=100)
        self.savings_table.column("Budget", anchor=CENTER, width=80)
        self.savings_table.column("Spent", anchor=CENTER, width=80)
        self.savings_table.column("Savings", anchor=CENTER, width=80)

        # create headings
        self.savings_table.heading("#0", text="", anchor=W)
        self.savings_table.heading("Category", text="Category", anchor=W)
        self.savings_table.heading("Budget", text="Budget ($)", anchor=CENTER)
        self.savings_table.heading("Spent", text="Spent ($)", anchor=CENTER)
        self.savings_table.heading("Savings", text="Savings ($)", anchor=CENTER)

        for category, amounts in self.expense_sum_dict.items():
            self.savings_table.insert(parent='', index='end', text='',
                                      values=(category, amounts[0], amounts[1], amounts[2]))

    # create notifications that alert user when spending > budget
    def notify(self):
        exceeded_budget_categories = []
        for category, amounts in self.expense_sum_dict.items():

            # check if savings are less than zero
            if amounts[2] < 0:
                exceeded_budget_categories.append(category)

            # notify the user with a popup if they have exceeded any of their budgets
        if exceeded_budget_categories:
            messagebox.showwarning("Alert!", "You have exceeded your monthly budget in the following categories: "
                                             f"\n{exceeded_budget_categories}")
        else:
            messagebox.showinfo("No worries", "You haven't exceeded any of your monthly budgets...yet")


# Expense Tab
class ExpenseTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # create export button
        export_button = Button(self, text="Export Table", command=self.export_data)
        export_button.pack(padx=5, pady=(5, 0), anchor=NE)
        change_on_hover(export_button)

        # Create table label
        table_label = Label(self, text=f"{parent.username}'s Expense Catalog", font=parent.BOLD_FONT)
        table_label.pack(side=TOP, anchor=NW, padx=74, pady=(30, 0))

        # create a Treeview frame
        self.tree_frame = Frame(self)
        self.tree_frame.pack(pady=(15, 0))

        # create a Treeview scrollbar
        self.tree_scroll = Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=RIGHT, fill=Y)

        # create the Treeview table
        self.expense_table = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="extended",
                                          height=14)
        self.expense_table.pack()

        # configure the scrollbar
        self.tree_scroll.config(command=self.expense_table.yview)

        # define our columns
        self.expense_table['columns'] = ("Name", "Amount", "Category", "Date", "ID")

        # format our columns
        self.expense_table.column("#0", width=0, stretch=NO)
        self.expense_table.column("Name", anchor=W, width=140)
        self.expense_table.column("Amount", anchor=W, width=140)
        self.expense_table.column("Category", anchor=W, width=140)
        self.expense_table.column("Date", anchor=CENTER, width=140)
        self.expense_table.column("ID", anchor=CENTER, width=80)

        # create headings
        self.expense_table.heading("#0", text="", anchor=W)
        self.expense_table.heading("Name", text="Name", anchor=W)
        self.expense_table.heading("Amount", text="Amount ($)", anchor=W)
        self.expense_table.heading("Category", text="Category", anchor=W)
        self.expense_table.heading("Date", text="Date", anchor=CENTER)
        self.expense_table.heading("ID", text="ID", anchor=CENTER)

        # create striped row tags
        self.expense_table.tag_configure('evenrow', background="white")
        self.expense_table.tag_configure('oddrow', background=PURPLE)

        # Finally, display our table to the screen
        self.display_table(records=query_expense(parent.username))

        # Add record entry boxes
        data_frame = LabelFrame(self, text="Record")
        data_frame.pack(fill="x", expand=True, padx=74)

        # set category Tkinter variable and category options
        self.selected_category = StringVar()

        # create names and entries for adding, removing, and updating expenses
        self.name_label = Label(data_frame, text="Name")
        self.name_label.grid(row=0, column=0, padx=3, pady=10)
        self.name_entry = Entry(data_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.amt_label = Label(data_frame, text="Amount")
        self.amt_label.grid(row=0, column=2, padx=10, pady=10)
        self.amt_entry = Entry(data_frame)
        self.amt_entry.grid(row=0, column=3, padx=10, pady=10)

        self.category_label = Label(data_frame, text="Category")
        self.category_label.grid(row=1, column=0, padx=10, pady=10)
        self.category_entry = ttk.Combobox(data_frame, state="readonly", textvariable=self.selected_category,
                                           values=query_categories(parent.username), width=18)
        self.category_entry.grid(row=1, column=1, padx=10, pady=10)

        self.date_label = Label(data_frame, text="Date")
        self.date_label.grid(row=1, column=2, padx=10, pady=10)
        self.date_entry = DateEntry(data_frame, width=18)
        self.date_entry.grid(row=1, column=3, padx=10, pady=10)

        # add buttons
        update_button = Button(data_frame, text="Update Record(s)", command=partial(self.update_record, parent))
        update_button.grid(row=0, column=4, padx=(0, 10), pady=(3, 0))
        change_on_hover(update_button)

        add_button = Button(data_frame, text="Add Record", command=partial(self.add_record, parent))
        add_button.grid(row=1, column=4, padx=(0, 10), pady=3)
        change_on_hover(add_button)

        clear_entry_button = Button(data_frame, text="Clear Entry Boxes", command=self.clear_entries)
        clear_entry_button.grid(row=0, column=5, padx=(0, 10), pady=(3, 0))
        change_on_hover(clear_entry_button)

        remove_button = Button(data_frame, text="Remove Record(s)", command=partial(self.remove, parent))
        remove_button.grid(row=1, column=5, padx=(0, 10), pady=3)
        change_on_hover(remove_button)

        # Bind the treeview (focus on record when it is clicked)
        self.expense_table.bind("<ButtonRelease-1>", self.select_record)

        # Add sorting functionality to treeview table
        self.sort_method = StringVar()
        sort_options = ["name", "category", "amount", "date", "date-added"]
        sort_dropdown = ttk.Combobox(self, state="readonly", value=sort_options, textvariable=self.sort_method)
        sort_dropdown.place(x=570, y=75)
        self.sort_method.set(sort_options[-1])

        # add sort button
        Label(self, text="Sort By").place(x=525, y=75)
        Button(self, image=parent.REFRESH_IMAGE, borderwidth=0,
               command=partial(self.sort_expense, parent)) \
            .place(x=710, y=75)

    def update_categories(self, parent):
        self.category_entry['values'] = query_categories(parent.username)

    def sort_expense(self, parent):
        # refresh treeview table and list according to selected sort method (by id, date, expense amount, or category)
        self.expense_table.delete(*self.expense_table.get_children())
        self.display_table(records=sort_by(parent.username, self.sort_method.get()))

    # add our data to the treeview table
    def display_table(self, records):
        for count, record in enumerate(records):
            if count % 2 == 0:
                self.expense_table.insert(parent='', index='end', iid=count, text='',
                                          values=(
                                              record[1], format(float(record[2]), '.2f'), record[3], record[4],
                                              record[5]),
                                          tags=('evenrow',))
            else:
                self.expense_table.insert(parent='', index='end', iid=count, text='',
                                          values=(
                                              record[1], format(float(record[2]), '.2f'), record[3], record[4],
                                              record[5]),
                                          tags=('oddrow',))

    # clear entries under the treeview table
    def clear_entries(self):
        # clear entry boxes
        self.name_entry.delete(0, END)
        self.amt_entry.delete(0, END)
        self.category_entry.delete(0, END)
        self.date_entry.delete(0, END)

    # automatically fills entries with record information if a record is clicked
    def select_record(self, e):
        self.clear_entries()

        # Grab record Number
        selected = self.expense_table.focus()
        # Grab record values
        values = self.expense_table.item(selected, 'values')

        # output to entry boxes
        try:
            self.name_entry.insert(0, values[0])
            self.amt_entry.insert(0, values[1])
            self.category_entry.set(values[2])
            self.datetime_obj = datetime.strptime(values[3], '%Y-%m-%d')
            self.formatted_date = self.datetime_obj.strftime('%m/%d/%y')
            self.date_entry.insert(0, self.formatted_date)
        except IndexError:
            pass

    # remove record(s)
    def remove(self, parent):
        records = self.expense_table.selection()

        # Add a messagebox to confirm removal
        if len(records) > 0:
            response = messagebox.askyesno("Woah!", "Are you sure you want to delete these record(s)?")

            # add logic for message box
            if response == 1:  # if yes is clicked
                for record in records:
                    selected = int(record)
                    item_to_delete = self.expense_table.item(selected, 'values')
                    item_id = item_to_delete[4]

                    # delete record from database
                    delete_expense(item_id)

                # refresh treeview table to show changes onscreen
                self.expense_table.delete(*self.expense_table.get_children())
                self.display_table(records=sort_by(parent.username, self.sort_method.get()))

                # refresh savings table (in Dashboard)
                parent.home_screen.display_savings_table(parent.username)

                # pop-up indicating success
                messagebox.showinfo("Success!", "Item(s) successfully deleted")

    # update record
    def update_record(self, parent):

        # grab the record number
        records = self.expense_table.selection()
        # error checking to ensure all entries are filled
        if len(self.date_entry.get()) > 0 and len(self.name_entry.get()) > 0 and len(self.category_entry.get()) > 0:
            # error checking to ensure amount is inputted as a number
            try:
                # convert expense amount to a suitable format
                self.expense_amt = float(self.amt_entry.get())

                # convert date to a suitable format
                self.datetime_obj = datetime.strptime(self.date_entry.get(), '%m/%d/%y')
                self.formatted_date = self.datetime_obj.strftime('%Y-%m-%d')

                # loop through selected records and find the id of each one
                for record in records:
                    selected = int(record)
                    item_to_update = self.expense_table.item(selected, 'values')
                    item_id = item_to_update[4]

                    # apply the update to the backend database using the id of the record
                    update_expense(parent.username, self.name_entry.get(), self.expense_amt,
                                   self.selected_category.get(),
                                   self.formatted_date, item_id)

                # refresh treeview table to show changes onscreen
                self.expense_table.delete(*self.expense_table.get_children())
                self.display_table(records=sort_by(parent.username, self.sort_method.get()))

                # refresh savings table (in Dashboard)
                parent.home_screen.display_savings_table(parent.username)

                # pop-up indicating success
                messagebox.showinfo("Success!", "Item(s) successfully updated")

                # notify the user if they have exceeded any budgets
                exceeded_budget_categories = []
                for category, amounts in parent.home_screen.expense_sum_dict.items():

                    # check if savings are less than zero
                    if amounts[2] < 0 and category == self.selected_category.get():
                        exceeded_budget_categories.append(category)

                # notify the user with a popup if they have exceeded any of their budgets
                if exceeded_budget_categories:
                    messagebox.showwarning("Alert!",
                                           "You have exceeded your monthly budget in that category")

                # clear entries
                self.clear_entries()

            except ValueError:  # the inputted expense cannot be converted to a float
                messagebox.showerror("Oops!", "Please enter a valid amount!")
        else:  # all the entries have not been filled before updating record
            messagebox.showerror("Oops!", "Please fill in all the fields")

    # add record
    def add_record(self, parent):

        # error checking to ensure all entries are filled
        if len(self.date_entry.get()) > 0 and len(self.name_entry.get()) > 0 and len(self.category_entry.get()) > 0:
            # error checking to ensure amount is inputted as a number
            try:
                self.expense_amt = float(self.amt_entry.get())

                # convert date to a suitable format
                self.datetime_obj = datetime.strptime(self.date_entry.get(), '%m/%d/%y')
                self.formatted_date = self.datetime_obj.strftime('%Y-%m-%d')

                # insert expense into database
                insert_expense(parent.username, self.name_entry.get(), self.expense_amt, self.selected_category.get(),
                               self.formatted_date)
                self.clear_entries()

                # refresh treeview table to show changes onscreen
                self.expense_table.delete(*self.expense_table.get_children())
                self.display_table(records=sort_by(parent.username, self.sort_method.get()))

                # refresh savings table (in Dashboard)
                parent.home_screen.display_savings_table(parent.username)

                # pop-up indicating success
                messagebox.showinfo("Success!", "Item successfully added")

                # notify the user if they have exceeded any budgets
                exceeded_budget_categories = []
                for category, amounts in parent.home_screen.expense_sum_dict.items():

                    # check if savings are less than zero
                    if amounts[2] < 0 and category == self.selected_category.get():
                        exceeded_budget_categories.append(category)

                # popup warning
                if exceeded_budget_categories:
                    messagebox.showwarning("Alert!",
                                           "You have exceeded your monthly budget in that category")

            except ValueError:  # the inputted expense cannot be converted to a float
                messagebox.showerror("Oops!", "Please enter a valid amount!")
        else:  # all the entries have not been filled before updating record
            messagebox.showerror("Oops!", "Please fill in all the fields")

    # export table data (.csv file for excel, no file ending for text file)
    def export_data(self):
        # error check table length before exporting
        if len(self.expense_table.get_children()) < 1:
            messagebox.showinfo("Alert!", "No data available to export")
            return False

        # asks user to save file as a specified name
        file = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save Table",
                                            filetype=(("CSV File", "*.csv"), ("Text File", ".txt")),
                                            defaultextension=".txt")

        # ensures an error doesn't pop up if the user exits the export popup
        try:
            with open(file, mode='w', newline='') as myfile:
                exp_writer = csv.writer(myfile, delimiter=',')
                exp_writer.writerow(["Name", "Amount", "Category", "Date", "ID"])
                for i in self.expense_table.get_children():
                    row = self.expense_table.item(i)['values']
                    exp_writer.writerow(row)
            messagebox.showinfo("Success!", "File successfully exported")

        except FileNotFoundError:
            pass


# Budget Tab
class BudgetTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # create export button
        export_button = Button(self, text="Export Table", command=self.export_data)
        export_button.pack(padx=5, pady=(5, 0), anchor=NE)
        change_on_hover(export_button)

        # Create table label
        table_label = Label(self, text=f"{parent.username}'s Monthly Budget Catalog", font=parent.BOLD_FONT)
        table_label.pack(side=TOP, anchor=NW, padx=74, pady=(30, 0))

        # create a Treeview frame
        self.tree_frame = Frame(self)
        self.tree_frame.pack(pady=(15, 0))

        # create a treeview scrollbar
        self.tree_scroll = Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=RIGHT, fill=Y)

        # create the treeview
        self.budget_table = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="extended",
                                         height=14)
        self.budget_table.pack()

        # configure the scrollbar
        self.tree_scroll.config(command=self.budget_table.yview)

        # define our columns
        self.budget_table['columns'] = ("Category", "Amount", "ID")

        # format our columns
        self.budget_table.column("#0", width=0, stretch=NO)
        self.budget_table.column("Category", anchor=W, width=261)
        self.budget_table.column("Amount", anchor=W, width=261)
        self.budget_table.column("ID", anchor=CENTER, width=117)

        # create headings
        self.budget_table.heading("#0", text="", anchor=W)
        self.budget_table.heading("Category", text="Category", anchor=W)
        self.budget_table.heading("Amount", text="Amount ($)", anchor=W)
        self.budget_table.heading("ID", text="ID", anchor=CENTER)

        # create striped row tags
        self.budget_table.tag_configure('evenrow', background="white")
        self.budget_table.tag_configure('oddrow', background=PURPLE)

        # Finally, display our table to the screen
        self.display_table(records=query_budgets(parent.username))

        # Add record entry boxes
        data_frame = LabelFrame(self, text="Record")
        data_frame.pack(fill="x", expand=True, padx=74)

        # set Tkinter category variable
        self.selected_category = StringVar()

        self.category_label = Label(data_frame, text="Category")
        self.category_label.grid(row=0, column=0, padx=10, pady=10)
        self.category_entry = ttk.Combobox(data_frame, state="readonly", textvariable=self.selected_category,
                                           values=query_categories(parent.username), width=18)
        self.category_entry.grid(row=0, column=1, padx=10, pady=10)

        self.amt_label = Label(data_frame, text="Amount")
        self.amt_label.grid(row=1, column=0, padx=10, pady=10)
        self.amt_entry = Entry(data_frame)
        self.amt_entry.grid(row=1, column=1, padx=10, pady=10)

        # add buttons
        update_button = Button(data_frame, text="Update Record(s)", command=partial(self.update_record, parent))
        update_button.grid(row=0, column=2, padx=10, pady=3)
        change_on_hover(update_button)

        add_button = Button(data_frame, text="Add Record", command=partial(self.add_record, parent))
        add_button.grid(row=1, column=2, padx=10, pady=3)
        change_on_hover(add_button)

        clear_entry_button = Button(data_frame, text="Clear Entry Boxes", command=self.clear_entries)
        clear_entry_button.grid(row=0, column=3, padx=10, pady=3)
        change_on_hover(clear_entry_button)

        remove_button = Button(data_frame, text="Remove Record(s)", command=partial(self.remove, parent))
        remove_button.grid(row=1, column=3, padx=10, pady=3)
        change_on_hover(remove_button)

        # Bind the treeview
        self.budget_table.bind("<ButtonRelease-1>", self.select_record)

    def update_categories(self, parent):
        self.category_entry['values'] = query_categories(parent.username)

    # add our data to the screen
    def display_table(self, records):
        for count, record in enumerate(records):
            if count % 2 == 0:
                self.budget_table.insert(parent='', index='end', iid=count, text='',
                                         values=(record[1], format(float(record[2]), '.2f'), record[3]),
                                         tags=('evenrow',))
            else:
                self.budget_table.insert(parent='', index='end', iid=count, text='',
                                         values=(record[1], format(float(record[2]), '.2f'), record[3]),
                                         tags=('oddrow',))

    def clear_entries(self):
        # clear entry boxes
        self.amt_entry.delete(0, END)
        self.category_entry.delete(0, END)

    # automatically fills entries with record information if a record is clicked
    def select_record(self, e):
        self.clear_entries()

        # Grab record Number
        selected = self.budget_table.focus()
        # Grab record values
        values = self.budget_table.item(selected, 'values')

        # output to entry boxes
        try:
            self.category_entry.set(values[0])
            self.amt_entry.insert(0, values[1])
        except IndexError:
            pass

    # remove record(s)
    def remove(self, parent):
        records = self.budget_table.selection()

        # Add a messagebox to confirm removal
        if len(records) > 0:
            response = messagebox.askyesno("Woah!", "Are you sure you want to delete these record(s)?")

            # add logic for message box
            if response == 1:  # if yes is clicked
                for record in records:
                    selected = int(record)
                    item_to_delete = self.budget_table.item(selected, 'values')
                    item_id = item_to_delete[2]

                    # delete record from database
                    delete_budget(item_id)

                # refresh treeview table to show changes onscreen
                self.budget_table.delete(*self.budget_table.get_children())
                self.display_table(records=query_budgets(parent.username))

                # refresh savings table (in Dashboard)
                parent.home_screen.display_savings_table(parent.username)

                # pop-up indicating success
                messagebox.showinfo("Success!", "Item(s) successfully deleted")

    # update record
    def update_record(self, parent):
        # grab the record number
        records = self.budget_table.selection()

        # query budget
        budgets = query_budgets(parent.username)
        categories = [budget[0] for budget in budgets]  # creates list of categories that have had a budget set to it
        if len(budgets) > 0 and self.category_entry.get() in categories:
            # check if budget has already been set for category
            messagebox.showerror("Oops!", "You already set a budget for that category!")
        else:
            # error checking to ensure all entries are filled
            if len(self.category_entry.get()) > 0:
                # error checking to ensure amount is inputted as a number
                try:
                    self.budget_amt = float(self.amt_entry.get())

                    for record in records:
                        selected = int(record)
                        item_to_update = self.budget_table.item(selected, 'values')
                        item_id = item_to_update[2]

                        # apply the update to the backend database
                        update_budget(parent.username, self.selected_category.get(), self.budget_amt, item_id)

                    # refresh treeview table to show changes onscreen
                    self.budget_table.delete(*self.budget_table.get_children())
                    self.display_table(records=query_budgets(parent.username))

                    # refresh savings table (in Dashboard)
                    parent.home_screen.display_savings_table(parent.username)

                    # pop-up indicating success
                    messagebox.showinfo("Success!", "Item(s) successfully updated")

                    # notify the user if they have exceeded any budgets
                    exceeded_budget_categories = []
                    for category, amounts in parent.home_screen.expense_sum_dict.items():

                        # check if savings are less than zero
                        if amounts[2] < 0 and category == self.selected_category.get():
                            exceeded_budget_categories.append(category)

                    # popup warning
                    if exceeded_budget_categories:
                        messagebox.showwarning("Alert!",
                                               "You have exceeded your monthly budget in that category")

                    # clear entries
                    self.clear_entries()
                except ValueError:  # the inputted expense cannot be converted to a float
                    messagebox.showerror("Oops!", "Please enter a valid amount!")
            else:  # the category field has not been filled before updating record
                messagebox.showerror("Oops!", "Please fill in the Category field")

    # add record
    def add_record(self, parent):
        # query budget
        budgets = query_budgets(parent.username)
        # create list of categories that have had a budget set to it
        categories = [category[1] for category in budgets]
        if len(budgets) > 0 and self.category_entry.get() in categories:
            # check if budget has already been set for category
            messagebox.showerror("Oops!", "You already set a budget for that category!")
        else:
            # error checking to ensure all entries are filled
            if len(self.category_entry.get()) > 0:
                # error checking to ensure amount is inputted as a number
                try:
                    self.budget_amt = float(self.amt_entry.get())

                    # insert budget into database
                    insert_budget(parent.username, self.selected_category.get(), self.budget_amt)
                    self.clear_entries()

                    # refresh treeview table to show changes onscreen
                    self.budget_table.delete(*self.budget_table.get_children())
                    self.display_table(records=query_budgets(parent.username))

                    # refresh savings table (in Dashboard)
                    parent.home_screen.display_savings_table(parent.username)

                    # pop-up indicating success
                    messagebox.showinfo("Success!", "Item successfully added")

                    # notify the user if they have exceeded any budgets
                    exceeded_budget_categories = []
                    for category, amounts in parent.home_screen.expense_sum_dict.items():

                        # check if savings are less than zero
                        if amounts[2] < 0 and category == self.selected_category.get():
                            exceeded_budget_categories.append(category)

                    # popup warning
                    if exceeded_budget_categories:
                        messagebox.showwarning("Alert!",
                                               "You have exceeded your monthly budget in that category")

                except ValueError:  # the inputted expense cannot be converted to a float
                    messagebox.showerror("Oops!", "Please enter a valid amount!")
            else:  # the category field has not been filled before updating record
                messagebox.showerror("Oops!", "Please fill in the Category field")

    # export table data (.csv file for excel, no file ending for text file)
    def export_data(self):
        # error check table length before exporting
        if len(self.budget_table.get_children()) < 1:
            messagebox.showinfo("Alert!", "No data available to export")
            return False

        # asks user to save file as a specified name
        file = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save Table",
                                            filetype=(("CSV File", "*.csv"), ("Text File", ".txt")),
                                            defaultextension=".txt")

        # ensures an error doesn't pop up if the user exits the export popup
        try:
            with open(file, mode='w', newline='') as myfile:
                exp_writer = csv.writer(myfile, delimiter=',')
                exp_writer.writerow(["Category", "Amount", "ID"])
                for i in self.budget_table.get_children():
                    row = self.budget_table.item(i)['values']
                    exp_writer.writerow(row)
            messagebox.showinfo("Success!", "File successfully exported")

        except FileNotFoundError:
            pass


# Stats Tab
class StatsTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        label = Label(self, text="Your Spending, Visualized", font=parent.BOLD_FONT)
        label.pack(padx=74, pady=(60, 0), anchor='nw')

        # create entry frame for bar graph creation
        self.bar_frame = LabelFrame(self, text="Generate Budgets vs. Spending Chart")
        self.bar_frame.pack(padx=74, pady=10, anchor='nw')

        # create entry frame for pie chart creation
        self.pie_frame = LabelFrame(self, text="Generate Expense Distribution Chart")
        self.pie_frame.pack(padx=74, pady=(0, 10), anchor='nw')

        # create entry frame for line graph creation
        self.line_frame = LabelFrame(self, text="Generate Expense Sum Chart")
        self.line_frame.pack(padx=74, pady=0, anchor='nw')

        # Add chart image for the aesthetic
        Label(self, image=parent.CHART_IMAGE).place(relx=0.6, y=125)

        for frame in (self.bar_frame, self.pie_frame, self.line_frame):
            Label(frame, text="").grid(row=0, column=0)
            Label(frame, text="").grid(row=2, column=0)

        # Button that generates charts/graphs
        bar_btn = Button(self.bar_frame, text="Get Stats", command=partial(self.bar_chart, parent.username))
        bar_btn.grid(row=1, column=4, padx=10)

        pie_btn = Button(self.pie_frame, text="Get Stats", command=partial(self.pie_chart, parent.username))
        pie_btn.grid(row=1, column=4, padx=10)

        line_btn = Button(self.line_frame, text="Get Stats", command=partial(self.line_graph, parent.username))
        line_btn.grid(row=1, column=4, padx=10)

        for button in (bar_btn, pie_btn, line_btn):
            change_on_hover(button)

        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "November", "December", "All Time"]

        now = datetime.now()
        years = [*range(1990, now.year + 1)]
        years.reverse()

        # text variables to store user-selected months/years
        self.selected_month_bar = StringVar()
        self.selected_month_pie = StringVar()
        self.selected_month_line = StringVar()

        self.selected_year_bar = StringVar()
        self.selected_year_pie = StringVar()
        self.selected_year_line = StringVar()

        # loops through frames and create labels for month and year entries
        for frame in (self.bar_frame, self.pie_frame, self.line_frame):
            self.month_label = Label(frame, text="Month")
            self.month_label.grid(row=1, column=0, padx=(10, 5))
            self.year_label = Label(frame, text="Year")
            self.year_label.grid(row=1, column=2, padx=(10, 5))

        # labels and entries for bar graph
        self.bar_month_entry = ttk.Combobox(self.bar_frame, state="readonly", textvariable=self.selected_month_bar,
                                            values=months, width=12)
        self.bar_month_entry.set(months[-1])
        self.bar_month_entry.grid(row=1, column=1)

        self.bar_year_entry = ttk.Combobox(self.bar_frame, state="readonly", textvariable=self.selected_year_bar,
                                           values=years, width=12)
        self.bar_year_entry.set(years[0])
        self.bar_year_entry.grid(row=1, column=3)

        # labels and entries for pie chart
        self.pie_month_entry = ttk.Combobox(self.pie_frame, state="readonly", textvariable=self.selected_month_pie,
                                            values=months, width=12)
        self.pie_month_entry.set(months[-1])
        self.pie_month_entry.grid(row=1, column=1)

        self.pie_year_entry = ttk.Combobox(self.pie_frame, state="readonly", textvariable=self.selected_year_pie,
                                           values=years, width=12)
        self.pie_year_entry.set(years[0])
        self.pie_year_entry.grid(row=1, column=3)

        # labels and entries for line graphs
        self.line_month_entry = ttk.Combobox(self.line_frame, state="readonly", textvariable=self.selected_month_line,
                                             values=months[:-1], width=12)
        self.line_month_entry.set(months[0])
        self.line_month_entry.grid(row=1, column=1)

        self.line_year_entry = ttk.Combobox(self.line_frame, state="readonly", textvariable=self.selected_year_line,
                                            values=years, width=12)
        self.line_year_entry.set(years[0])
        self.line_year_entry.grid(row=1, column=3)

    # stats
    def bar_chart(self, user):
        # get user-chosen month
        expenses = fetch_expenses_from(user, self.bar_month_entry.get(), self.bar_year_entry.get())
        budgets = query_budgets(user)
        budget_amounts = [budget[2] for budget in budgets]
        budget_categories = [category[1] for category in budgets]
        categories = [category[1] for category in budgets]
        categories = list(dict.fromkeys(categories))
        expense_categories = {}

        for category in categories:
            expense_amount = [
                float(expense[2]) for expense in expenses if expense[3] == category
            ]
            expense_categories[category] = sum(expense_amount)

        # creates a dictionary in the form {category: budget}
        budget_dict = {budget_categories[i]: budget_amounts[i] for i in range(len(budget_categories))}
        category_budget_dict = {}
        for budget_category in budget_dict:
            for category in categories:
                if category == budget_category:
                    category_budget_dict[category] = float(budget_dict[budget_category])
                else:
                    continue

        # CREATE BUDGET VS. SPENT GRAPH
        # creates a dictionary that associates categories with their respective expense sums and budgets
        expense_sum_dict = {
            cat: (category_budget_dict[cat], expense_categories[cat])
            for cat in category_budget_dict
        }

        # error checks for category length before creating chart
        if not expense_sum_dict:
            messagebox.showerror("Alert!", "This time period doesn't contain information")
        else:
            # create chart figure
            plt.figure(figsize=(6, 5), dpi=100)

            # plot bars for the double-bar graph
            values = np.arange(len(expense_sum_dict.keys()))  # generate x-axis values for graph
            WIDTH = 0.4
            plt.bar(values, [budget[0] for budget in expense_sum_dict.values()],
                    color=PURPLE, label='BUDGET', width=WIDTH)  # budget bar
            plt.bar(values + WIDTH, [expense[1] for expense in expense_sum_dict.values()],
                    color=DARK_PINK, label='SPENT', width=WIDTH)  # spent bar

            # add features and display graph
            plt.xlabel("Categories", color='black')
            plt.ylabel("Amount ($)", color='black')
            plt.xticks(values + (WIDTH / 2), expense_sum_dict.keys(), rotation=20,
                       fontweight='light', fontsize='small', color='black')
            plt.yticks(fontweight='light', fontsize='small', color='black')
            plt.title(f"Budget vs. Spent, {self.bar_month_entry.get()}")
            plt.legend()
            plt.subplots_adjust(bottom=0.19)
            plt.show()

    # creation of pie chart
    def pie_chart(self, user):
        expenses = fetch_expenses_from(user, self.pie_month_entry.get(), self.pie_year_entry.get())
        categories = [category[3] for category in expenses]
        categories = list(dict.fromkeys(categories))
        expense_categories = {}
        for category in categories:
            expense_amount = [
                float(expense[2]) for expense in expenses if expense[3] == category
            ]
            expense_categories[category] = sum(expense_amount)

        # error checks for category length before creating chart
        if not expense_categories:
            messagebox.showerror("Alert!", "This time period doesn't contain information")
        else:
            # CREATE EXPENSE DISTRIBUTION PIE CHART
            # create a dictionary assigning in the form {category : sum of expenses in that category}
            explode_amt = 0.05
            explode = ((explode_amt,) * len(expense_categories))
            plt.figure(figsize=(7, 5), dpi=100)

            COLOURS = [DARK_PINK, PURPLE, '#fd788b', '#feb1b7', '#ECD4FF', '#FFDCF4', '#B28DFF', '#FFAACC']
            # plot pieces for pie chart
            plt.pie(expense_categories.values(),
                    autopct='%1.0f%%', shadow=True, colors=COLOURS, pctdistance=0.85, explode=explode)
            plt.legend(expense_categories.keys(),
                       bbox_to_anchor=(1.0, 0.5, 0.4, 0.1), loc='center', facecolor='white', frameon=False)
            plt.subplots_adjust(left=0.1, right=0.75)

            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            # add features and display chart
            plt.title(f"Expense Distribution, {self.pie_month_entry.get()} {self.pie_year_entry.get()}")
            plt.show()

    # creation of line graph
    def line_graph(self, user):
        expenses = fetch_expenses_from(user, self.line_month_entry.get(), self.line_year_entry.get())
        expense_amts = [float(item[2]) for item in expenses]
        # create list on the sum of expenses over time
        for i in range(len(expense_amts)):
            if i != 0:
                expense_amts[i] += expense_amts[i - 1]

        # create a list of the dates that correspond to these expenses
        expense_dates = [int(item[4][8:10]) for item in expenses]

        # create a dictionary of the two lists
        expense_info = dict(zip(expense_dates, expense_amts))
        expense_info[0] = 0
        if len(expense_info) == 1:
            messagebox.showerror("Alert!", "This time period doesn't contain information")
        else:
            plt.figure(figsize=(6, 5), dpi=100)
            plt.plot(sorted(expense_info.keys()), sorted(expense_info.values()), color=DARK_PINK)

            # show x and y coords live
            plt.gca().format_coord = lambda x, y: "Day: {:.0f}, Expense ($): {:.0f}".format(x, y)

            # add features and display line graph
            plt.ylabel("Amount Spent ($)", color='black')
            plt.xlabel("Time", color='black')
            # hide axes ticks
            plt.gca().axes.xaxis.set_ticks([])
            plt.gca().axes.yaxis.set_ticks([])
            plt.title(f"Expenditures Over Time, {self.line_month_entry.get()}")
            plt.subplots_adjust(bottom=0.19)
            plt.show()


# checks if the user is successfully logged in before proceeding to main screen
if startup_screen.check_login:
    app = Main()
    app.mainloop()
