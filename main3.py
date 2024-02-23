from tkinter import *
from tkinter import ttk, messagebox
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import simpledialog
import sqlite3

# Database to store user information and surveys
user_information = []
survey_database = {}

DEFAULT_ADMIN_NAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# Connect to SQLite database
conn = sqlite3.connect('survey_responses.db')
cursor = conn.cursor()

# Check if the 'surveys' table exists, if not, create it
cursor.execute('''
    CREATE TABLE IF NOT EXISTS surveys (
        user_id TEXT,
        question TEXT,
        answer TEXT
    )
''')
conn.commit()


def user_input():
    def submit():
        try:
            name = entry_name.get()
            password = entry_password.get()

            if not name or not password:
                raise ValueError("Please Enter Both Name and Password ")

            if name == DEFAULT_ADMIN_NAME and password == DEFAULT_ADMIN_PASSWORD:
                window.destroy()
                messagebox.showinfo("Success", "Sign In Successful!")
                main_window()
            else:
                messagebox.showerror("Error", "Invalid Credentials")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    window = Tk()
    window.title("Admin")

    main_frame = Frame(window, bg="#f0f0f0")
    main_frame.pack(padx=15, pady=15)

    title_label = Label(main_frame, text="Log In", font="Arial 20 bold", bg="#f0f0f0")
    title_label.pack()

    entry_name_label = Label(main_frame, text="Enter UserName")
    entry_name_label.pack()

    entry_name = Entry(main_frame, width=40)  # Adjusted width here
    entry_name.pack()

    entry_password_label = Label(main_frame, text="Enter Password")
    entry_password_label.pack()

    entry_password = Entry(main_frame, show="*", width=40)  # Adjusted width here
    entry_password.pack()

    submit_button = Button(main_frame, text="Submit", command=submit)
    submit_button.pack(pady=40)

    # Center widgets within the main_frame
    for widget in main_frame.winfo_children():
        widget.pack_configure(anchor="center")

    window.mainloop()


def create_question(user_id):
    def submit():
        current_question = question_entry.get()
        if not current_question:
            messagebox.showerror("Error", "Please enter a question")
        else:
            if user_id not in survey_database:
                survey_database[user_id] = []
            survey_database[user_id].append({"Question": current_question, "Answer": []})
            print(f"Current Question: {current_question}")
            question_entry.delete(0, tk.END)
        

    window = tk.Tk()
    window.geometry("400x200")
    window.title("Question Form")

    form_frame = tk.Frame(window)
    form_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(form_frame, text="Enter a Question:").pack(pady=10)
    question_entry = tk.Entry(form_frame)
    question_entry.pack(pady=10)

    submit_button = tk.Button(form_frame, text="Submit", command=submit)
    submit_button.pack(pady=10)

    window.mainloop()


def display_survey(questions_list, user_id):
    window = Tk()
    window.title("Survey Form")
    window_width = 600
    window_height = 400

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2

    window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    main_frame = ttk.Frame(window)
    main_frame.pack(fill="both", expand=True)

    canvas = Canvas(main_frame, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    label = Label(frame, text="Please provide your responses:")
    label.pack(pady=10)

    responses = []

    def handle_option_selected(index, option):
        responses[index]["SelectedOption"] = option

    def submit_form():
        final_responses = []
        for i, item in enumerate(responses):
            question = questions_list[i]["Question"]
            selected_option = item["SelectedOption"]
            final_responses.append({"Question": question, "Response": selected_option})
            questions_list[i]["Answer"].append(selected_option)

            # Store the survey responses in the SQLite database
            cursor.execute("INSERT INTO surveys (user_id, question, answer) VALUES (?, ?, ?)",
                           (user_id, question, str(selected_option)))
            conn.commit()

        print(final_responses)
        window.destroy()
        messagebox.showinfo("Response Submitted", "Your response has been submitted.")

    for i, question_dic in enumerate(questions_list, start=1):
        question = question_dic["Question"]
        question_frame = ttk.Frame(frame)
        question_frame.pack(pady=5)

        label = ttk.Label(question_frame, text=f"{i}. {question}")
        label.pack(side="top", anchor="center", pady=(5, 0))

        response_var = IntVar(value=0)
        option_frame = ttk.Frame(question_frame)
        option_frame.pack(side="top", anchor="center")

        ttk.Label(
            option_frame,
            text="Strongly Disagree",
            padding=(5, 0),
        ).pack(side="left", padx=5)

        for j, option in enumerate(["1", "2", "3", "4", "5"], start=1):
            ttk.Radiobutton(
                option_frame,
                text=option,
                variable=response_var,
                value=j,
                command=lambda index=i - 1, option=option: handle_option_selected(index, option)
            ).pack(side="left", padx=5)

        ttk.Label(
            option_frame,
            text="Strongly Agree",
            padding=(5, 0),
        ).pack(side="left", padx=5)

        responses.append({"Question": question, "SelectedOption": None})

    submit_button = Button(frame, text="Submit", command=submit_form)
    submit_button.pack(pady=30)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    window.mainloop()


def view_responses(user_id):
    cursor.execute("SELECT question, answer FROM surveys WHERE user_id=?", (user_id,))
    survey_responses = cursor.fetchall()

    if not survey_responses:
        messagebox.showinfo("No Surveys", "No surveys found for the given ID.")
        return

    window = tk.Tk()
    window.title("Responses")
    window.geometry("600x400")

    tree = ttk.Treeview(window, show="headings")
    tree["columns"] = ("Question", "Answer")

    tree.column("Question", width=200, minwidth=150, anchor="center")
    tree.column("Answer", width=200, minwidth=150, anchor="center")

    tree.heading("Question", text="Question")
    tree.heading("Answer", text="Answer")

    style = ttk.Style()
    style.configure("Treeview", font=('Calibri', 11), rowheight=25)
    style.configure("Treeview.Heading", font=('Calibri', 12, 'bold'))
    tree.tag_configure('oddrow', background='#E8E8E8')
    tree.tag_configure('evenrow', background='#DFDFDF')

    for item in survey_responses:
        question, answer = item
        tree.insert("", "end", values=(question, answer))
        if len(tree.get_children()) % 2 == 0:
            tree.item(tree.get_children()[-1], tags=('evenrow',))
        else:
            tree.item(tree.get_children()[-1], tags=('oddrow',))

    tree.pack()
    generate_button = Button(window, text="Generate Pie Chart", command=lambda: generate_pie_chart(user_id))
    generate_button.pack()
    window.mainloop()


def generate_pie_chart(user_id):
    cursor.execute("SELECT answer FROM surveys WHERE user_id=?", (user_id,))
    survey_responses = cursor.fetchall()

    if not survey_responses:
        messagebox.showinfo("No Surveys", "No surveys found for the given ID.")
        return

    responses = [{"Answer": answer} for answer, in survey_responses]

    answer_counts = {}
    for response in responses:
        answer = response["Answer"]
        if answer in answer_counts:
            answer_counts[answer] += 1
        else:
            answer_counts[answer] = 1

    labels = list(answer_counts.keys())
    values = list(answer_counts.values())

    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.axis("equal")

    plt.title("Responses Analysis")
    plt.show()


def exit_program(window):
    window.destroy()


def main_window():
    def create_survey():
        user_id = simpledialog.askstring("User ID", "Enter User ID:")

        if user_id:
            # Check if the user_id already exists in the SQLite database
            cursor.execute("SELECT COUNT(*) FROM surveys WHERE user_id=?", (user_id,))
            count = cursor.fetchone()[0]

            if count > 0:
                messagebox.showinfo("Survey Exists", f"Survey already exists for the user ID: {user_id}")
            else:
                if user_id in survey_database:
                    messagebox.showinfo("Survey Exists", f"Survey already exists for the user ID: {user_id}")
                else:
                    create_question(user_id)
        else:
            messagebox.showerror("Error", "Please enter a valid User ID.")


    def view_survey_responses():
        user_id = simpledialog.askstring("User ID", "Enter User ID:")
        view_responses(user_id)

    def display_survey_form():
        user_id = simpledialog.askstring("User ID", "Enter User ID:")
        if user_id in survey_database:
            display_survey(survey_database[user_id], user_id)
        else:
            messagebox.showinfo("No Surveys", "No surveys found for the given ID.")

    window = Tk()
    window.title("Survey")
    window.geometry("780x500")

    window.configure(bg="#D7FCFC")

    title_label = Label(window, text="Online survey: ", font="Arial 20 bold",bg="#D7FCFC", fg="black")
    title_label.grid(row=0, column=0, columnspan=2, sticky='n')

    create_survey_button = Button(window, text="Create Survey", width=25, height=2, command=create_survey)
    create_survey_button.grid(row=2, column=0)

    view_survey_button = Button(window, text="View Responses", width=25, height=2, command=view_survey_responses)
    view_survey_button.grid(row=3, column=0)

    generate_survey_button = Button(window, text="Survey Form", width=25, height=2, command=display_survey_form)
    generate_survey_button.grid(row=4, column=0)

    exit_button = Button(window, text="Exit", width=25, height=2, command=lambda: exit_program(window))
    exit_button.grid(row=5, column=0)

    window.grid_columnconfigure(0, weight=1)
    window.mainloop()




user_input()
