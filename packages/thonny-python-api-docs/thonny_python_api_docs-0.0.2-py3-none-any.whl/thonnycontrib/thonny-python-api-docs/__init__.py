import os.path
from lxml import etree
import re
import tkinter as tk
import tkinter.font
from tkinter import ttk, Toplevel

import thonny
from thonny import get_workbench, tktextext, ui_utils
from thonny.config import try_load_configuration
from thonny.tktextext import TextFrame
from thonny.ui_utils import AutoScrollbar

from tkinterweb import HtmlFrame

base_path = os.path.join(os.path.dirname(__file__), "python-documentation")
index = os.path.join(base_path, "index.html")

class PythonApiView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.back_history = []
        self.forward_history = []
        self.current_url = None
        self.current_search_index = None
        self.current_search_term = None
        self.current_search_results = None

        # Top bar with navigation buttons and search
        self.navi_frame = tk.Frame(self)

        self.back_button = tk.Button(self.navi_frame, text="Back", command=self.go_back, state=tk.DISABLED)
        self.forward_button = tk.Button(self.navi_frame, text="Forward", command=self.go_forward, state=tk.DISABLED)

        self.back_button.pack(side=tk.LEFT)
        self.forward_button.pack(side=tk.LEFT)

        self.search_entry = tk.Entry(self.navi_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5), ipadx=3)
        self.search_entry.bind("<Control-a>", self.select_all)

        self.search_button = ttk.Button(self.navi_frame, text="Search", command=self.perform_search)
        self.search_button.pack(side=tk.LEFT)

        self.occurrences_label = tk.Label(self.navi_frame, text="")
        self.occurrences_label.pack(side=tk.LEFT, padx=(5, 0))

        self.url_label = tk.Label(self.navi_frame, text="?")
        self.url_label.pack(side=tk.RIGHT, padx=(5, 0))

        self.navi_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Main HTML view
        self.html = HtmlFrame(self, on_link_click=self.navigate_to)
        self.html.pack(fill=tk.BOTH, expand=True)
        self.search_entry.bind("<Return>", self.on_enter)

        get_workbench().bind("WorkbenchReady", self.on_workbench_ready, True)

    def select_all(self, event):
        self.search_entry.select_range(0, tk.END)
        self.search_entry.icursor(tk.END)
        return "break"

    def on_workbench_ready(self, event=None):
        ...
        #self.load_index()

    def on_show(self):
        self.load_index()

    def load_index(self):
        self.current_url = index
        self.url_label.config(text=self.display_url(self.current_url))
        self.html.load_file(index)

    def display_url(self, url):
        snip = "/python-documentation/"
        prefix_index = url.rfind(snip)
        return url[prefix_index + len(snip):]

    def show_popup(self, message):
        popup = Toplevel(self)
        popup.overrideredirect(True)
        popup.geometry(f"300x20+{self.winfo_pointerx()}+{self.winfo_pointery()}")
        label = tk.Label(popup, text=message, padx=0, pady=0, bg='#ffffcc')
        label.pack()
        popup.after(1000, popup.destroy)

    def navigate_to(self, url):
        print(f"Navigate to {url}")
        if url.startswith("http"):
            self.show_popup("You can't leave the API documentation")
            return
        if self.back_history and self.back_history[-1] == self.current_url:
            # don't duplicate history
            pass
        else:
            self.back_history.append(self.current_url)
        self.forward_history.clear()
        self.html.load_file(url)
        self.current_url = url
        self.url_label.config(text=self.display_url(self.current_url))
        self.update_button_states()

    def go_back(self):
        if self.back_history:
            previous_url = self.back_history.pop()
            self.forward_history.append(self.current_url)
            self.html.load_file(previous_url)
            self.current_url = previous_url
            self.url_label.config(text=self.display_url(self.current_url))
            self.update_button_states()

    def go_forward(self):
        if self.forward_history:
            next_url = self.forward_history.pop()
            self.back_history.append(self.current_url)
            self.html.load_file(next_url)
            self.current_url = next_url
            self.url_label.config(text=self.display_url(self.current_url))
            self.update_button_states()

    def update_button_states(self):
        self.back_button.config(state=tk.NORMAL if self.back_history else tk.DISABLED)
        self.forward_button.config(state=tk.NORMAL if self.forward_history else tk.DISABLED)

    def on_enter(self, event):
        self.perform_search()

    def perform_search(self):
        term = self.search_entry.get()
        if term == self.current_search_term:
            num_results = len(self.current_search_results)
            self.current_search_index += 1
            if self.current_search_index == num_results:
                self.current_search_index = 0
            f = os.path.join(base_path, self.current_search_results[self.current_search_index])
            self.occurrences_label.config(text=f"{self.current_search_index + 1} of {num_results} Result{'s' if num_results != 1 else ''}")
            self.navigate_to(f)
        else:
            if term and len(term) >= 3:
                print(f"Searching for: {term}")
                self.current_search_results = self.search_html(term)
                print(self.current_search_results)
                num_results = len(self.current_search_results)
                if self.current_search_results:
                    f = os.path.join(base_path, self.current_search_results[0])
                    self.navigate_to(f)
                    self.current_search_term = term
                    self.current_search_index = 0
                    self.occurrences_label.config(text=f"{self.current_search_index + 1} of {num_results} Result{'s' if num_results != 1 else ''}")
                else:
                    self.occurrences_label.config(text=f"No Results")
            else:
                self.occurrences_label.config(text=f"Enter at least 3 characters!")

    def show_error_page(self, url, error, code):
        if self.winfo_exists():
            if not self._button:
                self._button = tk.Button(self, text="Go back")
            self._button.configure(command=self.go_back)
            self.load_html(BUILTIN_PAGES["about:error"].format(bg=self.about_page_background, fg=self.about_page_foreground, i1=code, i2=self._button), url)

    def search_html(self, term):
        base_path = os.path.join(os.path.dirname(__file__), "python-documentation")
        result = {"in_tags": [], "in_text":[]}
        total_count = 0

        html_files = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))

        for file_path in html_files:
            with open(file_path, 'rb') as file:
                content = file.read()
                tree = etree.HTML(content)
            occurrences = {
                "in_tags": tree.xpath(f"//dt[contains(., '{term}')]"),
                "in_text": tree.xpath(f"//text()[contains(., '{term}')]/parent::*")
            }

            for kind, elements in occurrences.items():
                fragments = []
                for element in elements:
                    if element.get('id') and term in element.get('id'):
                        fragments.append(element.get('id'))
                    else:
                        # Find the nearest preceding element with an 'id'
                        preceding = element.xpath("preceding::*[@id][1]")

                        if preceding:
                            fragments.append(preceding[0].get('id'))
                        else:
                            fragments.append('')
                    relative_filename = os.path.relpath(file_path, base_path)
                    for fragment in fragments:
                        url = f"{relative_filename}#{fragment}"
                        result[kind].append(url)
                    total_count += sum(len(v) for v in occurrences.values())

        #print(f"Total occurrences of '{term}': {total_count}")
        return list(set(result["in_tags"])) + list(set(result["in_text"]))


def open_python_api():
    get_workbench().show_view("PythonApiView")

def load_plugin() -> None:
    get_workbench().add_view(PythonApiView, "Python API", "ne")
    get_workbench().add_command("python_api", "help", "Python API Documentation", open_python_api, group=30)

