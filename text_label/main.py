import copy
import tkinter
from tkinter import filedialog, scrolledtext, ttk
from collections import namedtuple
from dataclasses import dataclass
import json
import pathlib
from typing import Optional, Union, List, Tuple

from miros import ActiveObject
from miros import return_status, signals, Event
from miros import spy_on



class Bus:
    def __init__(self):
        self.objects = {}

    def register(self, name, obj):
        self.objects[name] = obj

    def __getitem__(self, item):
        return self.objects.get(item, None)

    def __getattr__(self, item):
        return self.objects.get(item, None)


class Gui:
    def __init__(self, bus: Bus):
        self.bus = bus
        self.bus.register('gui', self)

        self.current_text_idx: int = None
        self.categories_rb: dict[int, ttk.Radiobutton] = {}
        self.texts: List[TextInfo] = [TextInfo('xxx') for _ in range(10)]
        self.categories: dict[int, str] = {}

    def run(self):
        self.root = tkinter.Tk()

        self.main_menu = tkinter.Menu()
        self.project_menu = tkinter.Menu(self.main_menu, tearoff=False)
        self.categories_texts_menu = tkinter.Menu(self.main_menu, tearoff=False)

        self.main_frame = tkinter.Frame(self.root, background='yellow')
        self.categories_frame = tkinter.Frame(self.main_frame, background='red')

        self.texts_frame = tkinter.Frame(self.main_frame, background='green')
        self.texts_sv = tkinter.StringVar(value=[text.text for text in self.texts])
        self.texts_list = tkinter.Listbox(self.texts_frame, listvariable=self.texts_sv)
        self.texts_scrollbar = tkinter.Scrollbar(self.texts_frame, orient='vertical', command=self.texts_list.yview)
        self.texts_list['yscrollcommand'] = self.texts_scrollbar.set

        self.current_text_sv = tkinter.StringVar(value='Тестовый текст')
        self.current_text_frame = tkinter.Label(self.main_frame, background='blue', textvariable=self.current_text_sv)

        self.root.attributes('-zoomed', True)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.project_menu.add_command(label='New', accelerator='Ctrl-n', command=self.bus.statechart.launch_new_project_event)
        self.project_menu.add_command(label='Open', accelerator='Ctrl-o', command=self._show_load_project_popup)
        self.project_menu.add_command(label='Save', accelerator='Ctrl-s', command=self._show_save_project_popup, state='disabled')
        self.project_menu.add_command(label='Export', accelerator='Ctrl-e', command=self._show_export_project_popup, state='disabled')

        self.categories_texts_menu.add_command(label='Add Category', accelerator='Ctrl-k', command=self._show_add_category_popup_popup, state='disabled')
        self.categories_texts_menu.add_command(label='Remove Category', command=self._show_remove_category_popup, state='disabled')
        self.categories_texts_menu.add_separator()
        self.categories_texts_menu.add_command(label='Add Text', accelerator='Ctrl-i', command=self._show_import_text_from_input_popup, state='disabled')
        self.categories_texts_menu.add_command(label='Import Text From File', accelerator='Ctrl-f', command=self._show_import_text_from_file_popup, state='disabled')
        self.categories_texts_menu.add_separator()
        self.categories_texts_menu.add_command(label='Undo', accelerator='Ctrl-z', command=self.bus.statechart.launch_undo_event, state='disabled')

        self.main_menu.add_cascade(label='Project', menu=self.project_menu)
        self.main_menu.add_cascade(label='Categories/Texts', menu=self.categories_texts_menu)
        self.main_menu.add_command(label='Help')

        self.main_frame.grid(row=0, column=0, sticky='nesw')
        self.main_frame.rowconfigure(0, weight=5)
        self.main_frame.rowconfigure(1, weight=95)
        self.main_frame.columnconfigure(1, weight=90)

        self.categories_frame.grid(row=0, column=0, sticky='nesw', columnspan=2)

        self.texts_frame.grid(row=1, column=0, sticky='nesw')
        self.texts_frame.rowconfigure(0, weight=1)
        self.texts_list.grid(row=0, column=0, sticky='nesw')
        self.texts_scrollbar.grid(row=0, column=1, sticky='ns')

        self.current_text_frame.grid(row=1, column=1, sticky='nesw')

        self.root.bind('<Control-n>', lambda _: self.bus.statechart.launch_new_project_event())
        self.root.bind('<Control-o>', lambda _: self._show_load_project_popup())

        self.root.config(menu=self.main_menu)
        self.root.mainloop()

    def init_bindings(self):
        def _on_texts_list_listbox_select_event_cb(_):
            item_idx = self.texts_list.curselection()
            if len(item_idx) > 0:
                self._select_text(item_idx[0])

        self.texts_list.bind('<<ListboxSelect>>', _on_texts_list_listbox_select_event_cb)

        self.root.bind('<Control-s>', lambda _: self._show_save_project_popup())
        self.root.bind('<Control-e>', lambda _: self._show_export_project_popup())
        self.root.bind('<Control-k>', lambda _: self._show_add_category_popup_popup())
        self.root.bind('<Control-i>', lambda _: self._show_import_text_from_input_popup())
        self.root.bind('<Control-f>', lambda _: self._show_import_text_from_file_popup())
        self.root.bind('<Control-z>', lambda _: self.bus.statechart.launch_undo_event())

        def select_prev():
            text_idx = self._get_prev_text_idx()
            if text_idx is not None:
                self._select_text(text_idx)

        def select_next():
            text_idx = self._get_next_text_idx()
            if text_idx is not None:
                self._select_text(text_idx)
        self.root.bind('<KeyPress-Left>', lambda _: select_prev())
        self.root.bind('<KeyPress-Right>', lambda _: select_next())

    def enable_menus(self):
        self.project_menu.entryconfig('Save', state='normal')
        self.project_menu.entryconfig('Export', state='normal')
        self.categories_texts_menu.entryconfig('Add Category', state='normal')
        self.categories_texts_menu.entryconfig('Remove Category', state='normal')
        self.categories_texts_menu.entryconfig('Add Text', state='normal')
        self.categories_texts_menu.entryconfig('Import Text From File', state='normal')
        self.categories_texts_menu.entryconfig('Undo', state='normal')

    def update_categories(self, categories: dict):
        self.categories = categories

        for rb in self.categories_rb.values():
            rb.destroy()

        for k, v in self.categories.items():
            rb = ttk.Radiobutton(self.categories_frame, value=k, text=v)
            rb.grid(row=0, column=len(self.categories_rb.items()), sticky='nesw')
            self.categories_rb[k] = rb

    def update_texts(self, texts: List[str]):
        self.texts = texts
        self.texts_sv.set([text.text for text in self.texts])

    def _select_text(self, text_idx):
        self.current_text_idx = text_idx

        if self.current_text_idx is not None and self.current_text_idx <= (len(self.texts) - 1):
            text = self.texts[self.current_text_idx].text
            category_id: Optional[int] = self.texts[self.current_text_idx].category_id
            self.current_text_sv.set(text)
            if category_id:
                self.categories_rb[category_id].invoke()
        else:
            self.current_text_sv.set('')

    def _get_prev_text_idx(self) -> Optional[int]:
        if len(self.texts) == 0:
            return None
        if self.current_text_idx is None or self.current_text_idx == 0:
            return len(self.texts) - 1
        return self.current_text_idx - 1

    def _get_next_text_idx(self) -> Optional[int]:
        if len(self.texts) == 0:
            return None
        if self.current_text_idx is None or self.current_text_idx == (len(self.texts) - 1):
            return 0
        return self.current_text_idx + 1

    def _show_load_project_popup(self):
        if path_to_project := filedialog.askopenfilename(filetypes=[('Project', '.json.tl')]):
            self.bus.statechart.launch_load_project_event(path_to_project)

    def _show_save_project_popup(self):
        if path_to_project := filedialog.asksaveasfilename(filetypes=[('Project', '.json.tl')]):
            self.bus.statechart.launch_save_project_event(path_to_project)

    def _show_export_project_popup(self):
        pass

    def _show_add_category_popup_popup(self):
        def send_event():
            category = input_sv.get().strip()
            if len(category) > 0:
                self.bus.statechart.launch_add_category_event(category)
                root.destroy()

        root = tkinter.Toplevel()
        root.title('Add Category')

        main_frame = tkinter.Frame(root)
        input_sv = tkinter.StringVar()
        input_ = tkinter.Entry(main_frame, textvariable=input_sv)
        input_.bind('<Enter>', lambda _: send_event())
        input_.bind('<KP_Enter>', lambda _: send_event())

        button = tkinter.Button(main_frame, text='Add Category', command=send_event)

        root.resizable(False, False)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.grid(row=0, column=0, sticky='nesw')

        input_.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        button.grid(row=1, column=0, pady=10)

        input_.focus()

        root.grab_set()
        root.bind('<Escape>', lambda _: root.destroy())

        root.mainloop()

    def _show_remove_category_popup(self):
        pass

    def _show_import_text_from_input_popup(self):
        root = tkinter.Toplevel()
        root.title('Add Text')

        main_frame = tkinter.Frame(root)
        input_ = scrolledtext.ScrolledText(main_frame, width=50, height=15)

        button = tkinter.Button(main_frame, text='Add Text')

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.grid(row=0, column=0, sticky='nesw')

        input_.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        button.grid(row=1, column=0, pady=10)

        def send_event():
            text = input_.get('1.0', index2=tkinter.END).strip()
            if len(text) > 0:
                self.bus.statechart.launch_import_text_from_input(text)
                root.destroy()

        root.grab_set()
        root.bind('<Escape>', lambda _: root.destroy())

        input_.focus()
        button.configure(command=send_event)

        root.mainloop()

    def _show_import_text_from_file_popup(self):
        if path_to_file := filedialog.askopenfilename(filetypes=[('Text', '.txt')]):
            self.bus.statechart.launch_import_text_from_file(path_to_file)


class TestableGui(Gui):
    def __init__(self, bus: Bus):
        self.bus = bus
        self.bus.register('gui', self)

    def run(self):
        pass

    def init_bindings(self):
        pass

    def enable_menus(self):
        pass

    def update_categories(self, categories: dict):
        pass

    def update_texts(self, texts: dict):
        pass

    def _show_load_project_popup(self):
        pass

    def _show_save_project_popup(self):
        pass

    def _show_export_project_popup(self):
        pass

    def _show_add_category_popup_popup(self):
        pass

    def _show_remove_category_popup(self):
        pass

    def _show_import_text_from_input_popup(self):
        pass

    def _show_import_text_from_file_popup(self):
        pass


@dataclass
class TextInfo:
    text: str
    category_id: Optional[int] = None


class History:
    def __init__(self, initial_state):
        self.states: List = [initial_state]

    def add_state(self, new_state):
        self.states.append(copy.deepcopy(new_state))

    def rollback_state(self):
        if len(self.states) > 1:
            return self.states.pop()
        else:
            return copy.deepcopy(self.states[0])

    def get_current_state(self):
        return copy.deepcopy(self.states[-1])


class Project:
    def __init__(self, categories: Optional[dict[int, str]] = None, data: Optional[list] = ()):
        self.categories: dict[int, str] = self._make_categories_from_raw(categories if categories else {})
        self.data: list[TextInfo] = self._make_data_from_raw(data)
        self.history = History(self._get_snapshot())

    @staticmethod
    def _make_categories_from_raw(categories: dict[Union[str, int]]) -> dict[int, str]:
        return {int(k): str(v) for k, v in categories.items()}

    @staticmethod
    def _make_data_from_raw(data: list) -> list[TextInfo]:
        return [TextInfo(text=text_info[0], category_id=text_info[1]) if len(text_info) == 2 else TextInfo(text=text_info[0])
                for text_info in list(data)]

    def _get_snapshot(self) -> Tuple:
        return copy.deepcopy((self.categories, self.data))

    @staticmethod
    def load_project_from_path(path_to_project: pathlib.Path):
        with open(path_to_project, mode='r', encoding='utf-8') as project_handle:
            raw = json.loads(project_handle.read())
            return Project(categories=raw['categories'], data=raw['data'])

    def save_project(self, path_to_project: pathlib.Path):
        with open(path_to_project, mode='w', encoding='utf-8') as project_handle:
            raw = {"version": 0, "categories": self.categories, "data": [[text_info.text, text_info.category_id] for text_info in self.data]}
            project_handle.write(json.dumps(raw))
        self.history = History(self._get_snapshot())

    def add_category(self, category: str):
        if category not in self.categories.values():
            next_id = list(self.categories.keys())[-1]+1 if len(self.categories) > 0 else 0
            self.categories[next_id] = category
            self.history.add_state(self._get_snapshot())

    def remove_category(self, category_id: int):
        self.categories.pop(category_id)
        for text_id, text_info in enumerate(self.data):
            if text_info.category_id == category_id:
                self.data[text_id].category_id = None
                self.history.add_state(self._get_snapshot())

    def add_text(self, text: str):
        self.data.append(TextInfo(text=text))
        self.history.add_state(self._get_snapshot())

    def remove_text(self, text_id: int):
        self.data.pop(text_id)
        self.history.add_state(self._get_snapshot())

    def mark_text(self, text_id: int, category_id: int):
        self.data[text_id].category_id = category_id
        self.history.add_state(self._get_snapshot())

    def get_texts(self) -> list[TextInfo]:
        return self.data

    def undo(self):
        self.history.rollback_state()
        self.categories, self.data = self.history.get_current_state()


class Statechart(ActiveObject):
    def __init__(self, name: str, bus):
        super().__init__(name)
        self.bus = bus
        self.bus.register('statechart', self)
        self.project: Project = None

    def run(self):
        self.start_at(init)

    def on_new_project_in_init(self):
        self.project = Project()

        self.bus.gui.enable_menus()
        self.bus.gui.init_bindings()

        self.bus.gui.update_categories(self.project.categories)
        self.bus.gui.update_texts(self.project.get_texts())

    def on_load_project_in_init(self, path_to_project: pathlib.Path):
        self.project = Project.load_project_from_path(path_to_project)

        self.bus.gui.enable_menus()
        self.bus.gui.init_bindings()

        self.bus.gui.update_categories(self.project.categories)
        self.bus.gui.update_texts(self.project.get_texts())

    def on_add_category_in_in_project(self, category: str):
        self.project.add_category(category)

        self.bus.gui.update_categories(self.project.categories)

    def on_import_text_from_input_in_in_project(self, text: str):
        self.project.add_text(text)

        self.bus.gui.update_texts(self.project.get_texts())

    def on_import_text_from_file_in_in_project(self, path_to_file: pathlib.Path):
        with open(path_to_file, mode='r', encoding='utf-8') as text_handle:
            self.project.add_text(text_handle.read())

            self.bus.gui.update_texts(self.project.get_texts())

    def on_mark_text_in_in_project(self, text_id: int, category_id: int):
        self.project.mark_text(text_id=text_id, category_id=category_id)

        self.bus.gui.update_texts(self.project.get_texts())

    def on_save_project_in_in_project(self, path_to_project: pathlib.Path):
        self.project.save_project(path_to_project)

    def launch_new_project_event(self):
        self.post_fifo(Event(signal=signals.NEW_PROJECT))

    def launch_load_project_event(self, path_to_project: pathlib.Path):
        self.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=path_to_project))

    def launch_add_category_event(self, category: str):
        self.post_fifo(Event(signal=signals.ADD_CATEGORY, payload=category))

    def launch_import_text_from_input(self, text: str):
        self.post_fifo(Event(signal=signals.IMPORT_TEXT_FROM_INPUT, payload=text))

    def launch_import_text_from_file(self, path_to_file: pathlib.Path):
        self.post_fifo(Event(signal=signals.IMPORT_TEXT_FROM_FILE, payload=path_to_file))

    def launch_mark_text_event(self, text_id: int, category_id):
        self.post_fifo(Event(signal=signals.MARK_TEXT, payload=(text_id, category_id)))

    def launch_save_project_event(self, path_to_project: pathlib.Path):
        self.post_fifo(Event(signal=signals.SAVE_PROJECT, payload=path_to_project))

    def launch_undo_event(self):
        self.post_fifo(Event(signal=signals.UNDO))

    def on_undo_project_in_in_project(self):
        self.project.undo()


@spy_on
def init(s: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.NEW_PROJECT:
        status = s.trans(in_project)
        s.on_new_project_in_init()
    elif e.signal == signals.LOAD_PROJECT:
        status = s.trans(in_project)
        s.on_load_project_in_init(e.payload)
    else:
        status = return_status.SUPER
        s.temp.fun = s.top

    return status


@spy_on
def in_project(s: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.ADD_CATEGORY:
        status = return_status.HANDLED
        s.on_add_category_in_in_project(e.payload)
    elif e.signal == signals.REMOVE_CATEGORY:
        status = return_status.HANDLED
    elif e.signal == signals.IMPORT_TEXT_FROM_INPUT:
        status = return_status.HANDLED
        s.on_import_text_from_input_in_in_project(e.payload)
    elif e.signal == signals.IMPORT_TEXT_FROM_FILE:
        status = return_status.HANDLED
        s.on_import_text_from_file_in_in_project(e.payload)
    elif e.signal == signals.MARK_TEXT:
        status = return_status.HANDLED
        s.on_mark_text_in_in_project(text_id=e.payload[0], category_id=e.payload[1])
    elif e.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED
        s.on_save_project_in_in_project(e.payload)
    elif e.signal == signals.UNDO:
        status = return_status.HANDLED
        s.on_undo_project_in_in_project()
    else:
        status = return_status.SUPER
        s.temp.fun = init

    return status


def run():
    bus = Bus()
    statechart = Statechart(name='statechart', bus=bus)
    gui = Gui(bus=bus)

    statechart.run()
    gui.run()
    print(statechart.trace())
    print(statechart.spy())


if __name__ == '__main__':
    run()
