import tkinter as tk
from tkinter import messagebox, scrolledtext
import cloudscraper
from bs4 import BeautifulSoup
import webbrowser

# Global variables
torrent_links = []
current_page = 1

def set_dark_mode():
    root.configure(bg="#2E2E2E")
    for widget in root.winfo_children():
        widget.configure(bg="#2E2E2E", fg="white", highlightbackground="#444")

def search_torrents(page=1):
    global torrent_links, current_page
    torrent_links = []  # Clear previous results
    current_page = page

    app_name = entry.get().strip()
    if not app_name:
        messagebox.showwarning("Warning", "Please enter a search term!")
        return

    result_text.delete("1.0", tk.END)
    base_url = f"https://www.1337x.to/search/{app_name.replace(' ', '+')}/{page}/"
    result_text.insert(tk.END, f"🔎 Searching: {base_url}\n\n")

    scraper = cloudscraper.create_scraper()
    response = scraper.get(base_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        rows = soup.select("table.table-list tbody tr")

        if rows:
            for i, row in enumerate(rows):
                try:
                    torrent_title = row.select("td.coll-1.name a")[1].text.strip()
                    torrent_page = "https://www.1337x.to" + row.select("td.coll-1.name a")[1]['href']
                    size = row.select_one("td.coll-4").text.strip() if row.select_one("td.coll-4") else "N/A"
                    time = row.select_one("td.coll-date").text.strip() if row.select_one("td.coll-date") else "N/A"
                
                    # Store the torrent link for later selection
                    torrent_links.append(torrent_page)

                    result_text.insert(tk.END, f"{i + 1}. {torrent_title} | Size: {size} | Uploaded: {time}\n")
                except (AttributeError, IndexError):
                    result_text.insert(tk.END, f"{i + 1}. Error parsing row, skipping.\n")

            # Show selection and navigation widgets
            show_selection_and_navigation_widgets()
        else:
            result_text.insert(tk.END, "No results found.\n")
            hide_selection_and_navigation_widgets()
    else:
        result_text.insert(tk.END, f"Failed to fetch search results. Status code: {response.status_code}\n")
        hide_selection_and_navigation_widgets()

def select_torrent():
    global torrent_links
    choice = selection_entry.get().strip()
    if not choice.isdigit() or not (0 < int(choice) <= len(torrent_links)):
        messagebox.showerror("Error", "Please enter a valid torrent number.")
        return

    torrent_page = torrent_links[int(choice) - 1]
    get_magnet_link(torrent_page)

def get_magnet_link(torrent_page):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(torrent_page)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        magnet_link = soup.select_one("a[href^='magnet:?']")
        if magnet_link:
            magnet_url = magnet_link['href']
            messagebox.showinfo("Magnet Link", "🚀 Opening magnet link in your default torrent client...")
            webbrowser.open(magnet_url)  # Automatically open the magnet link
        else:
            messagebox.showerror("Error", "Magnet link not found.")
    else:
        messagebox.showerror("Error", f"Failed to fetch the torrent page. Status code: {response.status_code}")

def next_page():
    global current_page
    search_torrents(page=current_page + 1)

def previous_page():
    global current_page
    if current_page > 1:
        search_torrents(page=current_page - 1)
    else:
        messagebox.showinfo("Info", "You are already on the first page.")

def show_selection_and_navigation_widgets():
    selection_label.pack(pady=5)
    selection_entry.pack(pady=5)
    download_button.pack(pady=10)
    nav_frame.pack(pady=5)

def hide_selection_and_navigation_widgets():
    selection_label.pack_forget()
    selection_entry.pack_forget()
    download_button.pack_forget()
    nav_frame.pack_forget()

def handle_enter(event):
    focused_widget = event.widget
    if focused_widget == entry:
        search_torrents(1)
    elif focused_widget == selection_entry:
        select_torrent()

# Create the GUI
root = tk.Tk()
root.title("1337x Torrent Downloader")
root.geometry("800x600")

# Set Dark Mode
set_dark_mode()

# GUI Elements
tk.Label(root, text="Enter the name of the app to search:", bg="#2E2E2E", fg="white").pack(pady=10)
entry = tk.Entry(root, width=50, bg="#444", fg="white", insertbackground="white")
entry.pack(pady=5)

tk.Button(root, text="Search Torrents", command=lambda: search_torrents(1), bg="#444", fg="white").pack(pady=10)
result_text = scrolledtext.ScrolledText(root, width=95, height=20, bg="#1E1E1E", fg="white", insertbackground="white")
result_text.pack(padx=10, pady=10)

selection_label = tk.Label(root, text="Enter the number of the torrent to download:", bg="#2E2E2E", fg="white")
selection_entry = tk.Entry(root, width=10, bg="#444", fg="white", insertbackground="white")
download_button = tk.Button(root, text="Download Torrent", command=select_torrent, bg="#444", fg="white")

# Navigation Frame for Previous/Next Buttons
nav_frame = tk.Frame(root, bg="#2E2E2E")
previous_button = tk.Button(nav_frame, text="Previous Page", command=previous_page, bg="#444", fg="white")
previous_button.pack(side="left", padx=5)
next_button = tk.Button(nav_frame, text="Next Page", command=next_page, bg="#444", fg="white")
next_button.pack(side="right", padx=5)

# Initially hide selection and navigation widgets
hide_selection_and_navigation_widgets()

# Bind Enter key to actions
entry.bind("<Return>", handle_enter)
selection_entry.bind("<Return>", handle_enter)

# Run the GUI
root.mainloop()
