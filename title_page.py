from tkinter import *
from tkinter import messagebox
from backend import *
from tkinter.font import Font


# COLOURS
BG_COLOUR = '#202124'
DARK_PINK = "#e75480"
PURPLE = "#CDB7F6"


# function to change properties of button on hover
def change_on_hover(button, hover_colour):
    button.bind("<Enter>", func=lambda e: button.config(
        background=hover_colour, foreground="white"))

    # background color on leaving widget
    button.bind("<Leave>", func=lambda e: button.config(
        background=BG_COLOUR, foreground="white"))


class RegisterScreen(Tk):
    def __init__(self):
        super().__init__()

        # set window title
        self.title("")

        # app width and height
        APP_WIDTH = 813
        APP_HEIGHT = 650

        # screen width and height
        SCREEN_WIDTH = self.winfo_screenwidth()
        SCREEN_HEIGHT = self.winfo_screenheight()

        # app placement
        x_pos = 0.53 * SCREEN_WIDTH
        y_pos = 0.08 * SCREEN_HEIGHT

        # set window features
        self.geometry(f'{APP_WIDTH}x{APP_HEIGHT}+{int(x_pos)}+{int(y_pos)}')

        # FONTS
        self.TITLE_FONT = Font(family="Calibri", size=80, weight="bold")
        self.BUTTON_FONT = Font(family="Calibri", size=15)

        # set colour scheme for widgets
        self.tk_setPalette(background=BG_COLOUR, foreground='white',
                           activeBackground=DARK_PINK, activeForeground='white')

        self.resizable(width=False, height=False)

        connect_user()
        connect_categories()
        connect_expense()
        connect_budget()

        # startup screen widgets
        Label(self, text="Expense Tracker", font=self.TITLE_FONT).place(relx=0.5, rely=0.35, anchor=CENTER)
        login_btn = Button(self, text="Login", command=self._login, font=self.BUTTON_FONT, width=20)
        login_btn.place(relx=0.5, rely=0.7, anchor=CENTER)
        signup_btn = Button(self, text="Sign Up", command=self._signup, font=self.BUTTON_FONT, width=20)
        signup_btn.place(relx=0.5, rely=0.8, anchor=CENTER)
        change_on_hover(login_btn, DARK_PINK)
        change_on_hover(signup_btn, DARK_PINK)

        # set login confirmation to False
        self.check_login = False

    # private signup method
    def _signup(self):
        # create signup window
        self.signup_screen = Toplevel()
        self.signup_screen.title("Sign up")
        self.signup_screen.geometry(f"300x250+{int(self.winfo_rootx())}+{int(self.winfo_rooty())}")

        self._username = StringVar()
        self._password = StringVar()

        # create signup buttons, labels, and variables
        Label(self.signup_screen, text="Please enter details below").pack()
        Label(self.signup_screen, text="").pack()

        username_label = Label(self.signup_screen, text="Username * ")
        username_label.pack()

        self.username_entry = Entry(self.signup_screen, textvariable=self._username)
        self.username_entry.pack()

        Label(self.signup_screen, text="").pack()  # adds space
        password_label = Label(self.signup_screen, text="Password * ")
        password_label.pack()

        self.password_entry = Entry(self.signup_screen, textvariable=self._password, show='*')
        self.password_entry.pack()

        Label(self.signup_screen, text="").pack()  # adds space
        Label(self.signup_screen, text="").pack()  # adds space
        Button(self.signup_screen, text="Register", width=10, height=1, command=self.register_user).pack()

    # private login method
    def _login(self):
        # create login window
        self.login_screen = Toplevel()
        self.login_screen.title("Login")
        self.login_screen.geometry(f"300x250+{int(self.winfo_rootx())}+{int(self.winfo_rooty())}")

        # create login buttons, labels and entries
        Label(self.login_screen, text="Please enter details below to login").pack()
        Label(self.login_screen, text="").pack()  # adds space

        self.login_username = StringVar()
        self.login_password = StringVar()

        Label(self.login_screen, text="Username * ").pack()
        self.username_login_entry = Entry(self.login_screen, textvariable=self.login_username)
        self.username_login_entry.pack()

        Label(self.login_screen, text="").pack()  # adds space
        Label(self.login_screen, text="Password * ").pack()

        self.password_login_entry = Entry(self.login_screen, textvariable=self.login_password, show='*')
        self.password_login_entry.pack()

        Label(self.login_screen, text="").pack()  # adds space
        Label(self.login_screen, text="").pack()  # adds space
        Button(self.login_screen, text="Login", width=10, height=1, command=self.login_verify).pack()

    # getter method for username
    def get_username(self):
        return self._username.get().strip()

    # getter method for password
    def get_password(self):
        return self._password.get().strip()

    # Implementing event on register button
    def register_user(self):
        # query user info from database
        connect_user()
        self._user_info_records = query_user()

        for record in self._user_info_records:
            # error check for already-existing usernames
            if record[0] == self.get_username():
                self.username_entry.delete(0, END)  # clears username input box
                self.password_entry.delete(0, END)  # clears password input box
                messagebox.showerror("Oops!", "Username already exists")
                break

            # error check for empty entries
            elif len(self.get_username()) == 0 or len(self.get_password()) == 0:
                self.username_entry.delete(0, END)  # clears username input box
                self.password_entry.delete(0, END)  # clears password input box
                messagebox.showerror("Oops!", "Please fill in both entries")
                break
        else:
            # Insert user info into database
            insert_user(self.get_username(), self.get_password())

            # pop up indicating success
            messagebox.showinfo("Success", "Registration Success")

            # close main window
            self.signup_screen.destroy()

    # Implementing event on login button
    def login_verify(self):

        # query user info from database
        self._user_info_records = query_user()

        for record in self._user_info_records:
            if record[0] == self.login_username.get():
                if record[1] == self.login_password.get():
                    self.login_success()
                else:
                    self.password_not_recognised()
                break
        else:
            self.user_not_found()

    # Designing popup for login success
    def login_success(self):
        messagebox.showinfo("Success", "Login Success")
        self.login_screen.destroy()
        self.win_x_coord = startup_screen.winfo_rootx()
        self.win_y_coord = startup_screen.winfo_rooty()
        startup_screen.destroy()
        self.confirm_login(login=True)

    # Designing popup for login invalid password
    def password_not_recognised(self):
        messagebox.showerror("Oops!", "Invalid Password")
        self.login_screen.destroy()
        self._login()
        self.confirm_login(login=False)

    # Designing popup for user not found
    def user_not_found(self):
        messagebox.showerror("Oops!", "User not found")
        self.login_screen.destroy()
        self._login()
        self.confirm_login(login=False)

    def confirm_login(self, login):
        self.check_login = login


startup_screen = RegisterScreen()
startup_screen.mainloop()
