import copy
import tkinter
from tkinter import filedialog, scrolledtext, ttk, font, messagebox
from typing import Optional, List

from text_label.bus import Bus
from text_label.text_info import TextInfo


class CategoryWidget(tkinter.Frame):
    def __init__(self, parent, text: str, value: str, variable, command, delete_command):
        super().__init__(parent)
        self.parent = parent
        self.text = text
        self.value = value
        self.variable = variable
        self.command = command
        self.delete_command = delete_command

        self.rb = ttk.Radiobutton(self,
                                  value=copy.copy(value),
                                  text=copy.copy(text),
                                  variable=self.variable,
                                  command=self.command)

        self.delete_btn = tkinter.Button(self, text='X', command=self.on_delete_btn_click)

        self.rb.grid(column=0, row=0)
        self.delete_btn.grid(column=0, row=1)

    def invoke(self):
        self.rb.invoke()

    def on_delete_btn_click(self):
        if messagebox.askokcancel(title='Are you sure?', message=f'Do you really want to delete `{self.text}` category?'):
            self.delete_command()


class Gui:
    def __init__(self, bus: Bus):
        self.bus = bus
        self.bus.register('gui', self)

        self.current_text_idx: int = None
        self.categories_rb: dict[int, CategoryWidget] = {}
        self.texts: List[TextInfo] = []
        self.categories: dict[int, str] = {}

    def run(self):
        self.root = tkinter.Tk()

        self.main_menu = tkinter.Menu()
        self.project_menu = tkinter.Menu(self.main_menu, tearoff=False)
        self.categories_texts_menu = tkinter.Menu(self.main_menu, tearoff=False)
        self.exports_menu = tkinter.Menu(self.main_menu, tearoff=False)

        self.main_frame = tkinter.Frame(self.root, background='yellow')
        self.categories_frame = tkinter.Frame(self.main_frame, background='red')
        self.categories_sv = tkinter.StringVar(value=-1)
        self.nocategory_rb = ttk.Radiobutton(self.categories_frame,
                                             value=-1,
                                             text='<NOCATEGORY>',
                                             variable=self.categories_sv,
                                             command=lambda: self._mark_text(self.current_text_idx, category_id=int(self.categories_sv.get())))

        self.texts_frame = tkinter.Frame(self.main_frame, background='green')
        self.texts_list = ttk.Treeview(self.texts_frame, columns=['Text', 'text_idx'], displaycolumns=['Text'], selectmode='browse', show='headings')
        self.texts_scrollbar = tkinter.Scrollbar(self.texts_frame, orient='vertical', command=self.texts_list.yview)

        self.texts_list['yscrollcommand'] = self.texts_scrollbar.set

        self.current_text_sv = tkinter.StringVar(value='Тестовый текст')
        self.current_text_font = font.Font(size=24)
        self.current_text_frame = tkinter.Label(self.main_frame, background='blue', textvariable=self.current_text_sv, font=self.current_text_font)

        self.root.attributes('-zoomed', True)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.project_menu.add_command(label='New', accelerator='Ctrl-n', command=self.bus.statechart.launch_new_project_event)
        self.project_menu.add_command(label='Open', accelerator='Ctrl-o', command=self._show_load_project_popup)
        self.project_menu.add_command(label='Save', accelerator='Ctrl-s', command=self._show_save_project_popup, state='disabled')

        self.categories_texts_menu.add_command(label='Add Category', accelerator='Ctrl-k', command=self._show_add_category_popup_popup, state='disabled')
        self.categories_texts_menu.add_separator()
        self.categories_texts_menu.add_command(label='Add Text', accelerator='Ctrl-i', command=self._show_import_text_from_input_popup, state='disabled')
        self.categories_texts_menu.add_command(label='Import Text From File', accelerator='Ctrl-f', command=self._show_import_text_from_file_popup, state='disabled')
        self.categories_texts_menu.add_separator()
        self.categories_texts_menu.add_command(label='Font Size +', accelerator='Ctrl-+', command=lambda: self.change_font_size(2), state='disabled')
        self.categories_texts_menu.add_command(label='Font Size -', accelerator='Ctrl--', command=lambda: self.change_font_size(-2), state='disabled')
        self.categories_texts_menu.add_separator()
        self.categories_texts_menu.add_command(label='Undo', accelerator='Ctrl-z', command=self.bus.statechart.launch_undo_event, state='disabled')

        if self.bus.exporters:
            for k, v in self.bus.exporters.items():
                self.exports_menu.add_command(label=k, command=lambda: v.show_options(), state='disabled')

        self.main_menu.add_cascade(label='Project', menu=self.project_menu)
        self.main_menu.add_cascade(label='Categories/Texts', menu=self.categories_texts_menu)
        self.main_menu.add_cascade(label='Export', menu=self.exports_menu)
        self.main_menu.add_command(label='Help', command=self._show_help_popup)

        self.main_frame.grid(row=0, column=0, sticky='nesw')
        self.main_frame.rowconfigure(0, weight=5)
        self.main_frame.rowconfigure(1, weight=95)
        self.main_frame.columnconfigure(1, weight=90)

        self.categories_frame.grid(row=0, column=0, sticky='nesw', columnspan=2)
        self.nocategory_rb.grid(row=0, column=0, sticky='nesw')

        self.texts_frame.grid(row=1, column=0, sticky='nesw')
        self.texts_frame.rowconfigure(0, weight=1)
        self.texts_list.grid(row=0, column=0, sticky='nesw')
        self.texts_scrollbar.grid(row=0, column=1, sticky='ns')

        self.current_text_frame.grid(row=1, column=1, sticky='nesw')

        self.root.bind('<Control-n>', lambda _: self.bus.statechart.launch_new_project_event())
        self.root.bind('<Control-o>', lambda _: self._show_load_project_popup())
        self.root.bind('<F1>', lambda _: self._show_help_popup())

        self.root.config(menu=self.main_menu)
        self.root.mainloop()

    def init_bindings(self):
        def _on_texts_list_listbox_select_event_cb(_):
            item_idx = self.texts_list.selection()
            if item_idx and len(item_idx) > 0:
                text_idx = self.texts_list.item(item_idx[0], 'values')[1]
                self._select_text(int(text_idx))

        self.texts_list.bind('<Double-Button-1>', _on_texts_list_listbox_select_event_cb)

        self.root.bind('<Control-s>', lambda _: self._show_save_project_popup())
        self.root.bind('<Control-k>', lambda _: self._show_add_category_popup_popup())
        self.root.bind('<Control-i>', lambda _: self._show_import_text_from_input_popup())
        self.root.bind('<Control-f>', lambda _: self._show_import_text_from_file_popup())
        self.root.bind('<Control-z>', lambda _: self.bus.statechart.launch_undo_event())
        self.root.bind('<KeyPress-Delete>', lambda _: self.bus.statechart.launch_remove_text_event(self.current_text_idx))

        self.root.bind('<KeyPress-Up>', lambda _: self.select_prev())
        self.root.bind('<KeyPress-Down>', lambda _: self.select_next())
        self.root.bind('<KeyPress-Left>', lambda _: self.select_prev())
        self.root.bind('<KeyPress-Right>', lambda _: self.select_next())

        self.root.bind('<KeyPress-equal>', lambda _: self.change_font_size(2))
        self.root.bind('<Control-KP_Add>', lambda _: self.change_font_size(2))

        self.root.bind('<Control-minus>', lambda _: self.change_font_size(-2))
        self.root.bind('<KeyPress-KP_Subtract>', lambda _: self.change_font_size(-2))

        for i in range(10):
            idx = copy.copy(i)

            # блять, какой же это пиздец
            def __closure():
                idx = i
                return lambda e: self._select_radiobutton(idx)

            self.root.bind(f'<KeyPress-KP_{i}>', __closure())

    def enable_menus(self):
        self.project_menu.entryconfig('Save', state='normal')
        self.categories_texts_menu.entryconfig('Add Category', state='normal')
        self.categories_texts_menu.entryconfig('Add Text', state='normal')
        self.categories_texts_menu.entryconfig('Import Text From File', state='normal')
        self.categories_texts_menu.entryconfig('Font Size +', state='normal')
        self.categories_texts_menu.entryconfig('Font Size -', state='normal')
        self.categories_texts_menu.entryconfig('Undo', state='normal')

        if self.exports_menu:
            for entry_idx in range(self.exports_menu.index('end') + 1):
                self.exports_menu.entryconfig(entry_idx, state='normal')


    def update_categories(self, categories: dict):
        self.categories = categories

        for rb in self.categories_rb.values():
            rb.destroy()

        self.categories_rb = {}

        for k, v in self.categories.items():
            rb_idx = copy.copy(k)

            def __rb_action_callback():
                self._mark_text(self.current_text_idx, category_id=int(self.categories_sv.get()))

            def __make_rb_delete_action_callback():
                category_id = k
                return lambda: self.bus.statechart.launch_remove_category_event(category_id)

            self.categories_rb[rb_idx] = CategoryWidget(self.categories_frame,
                                                        value=copy.copy(str(k)),
                                                        text=f'{v} <KP_{len(self.categories_rb) + 1}>',
                                                        variable=self.categories_sv,
                                                        command=__rb_action_callback,
                                                        delete_command=__make_rb_delete_action_callback())

            self.categories_rb[rb_idx].grid(row=0, column=len(self.categories_rb) + 1, sticky='nesw')

    def update_texts(self, texts: List[TextInfo]):
        same_size = len(texts) == self.texts
        self.texts = texts
        if self.texts_list.tag_has('#text'):
            for item in self.texts_list.get_children(''):
                self.texts_list.delete(item)

        for text_idx, text in enumerate(self.texts):
            self.texts_list.insert('', 'end', values=(copy.copy(text.text),copy.copy(text_idx)), tags=('#text',))
        if same_size:
            self._select_text(self.current_text_idx)
        else:
            self._select_text(0)

    def _select_text(self, text_idx):
        self.current_text_idx = text_idx

        if self.current_text_idx is not None and self.current_text_idx <= (len(self.texts) - 1):
            text = self.texts[self.current_text_idx].text
            category_id: Optional[int] = self.texts[self.current_text_idx].category_id
            self.current_text_sv.set(text)
            self.categories_sv.set(str(category_id) if category_id is not None else '-1')
            self._set_text_list_selection(self.current_text_idx)
        else:
            self.current_text_sv.set('')
            self.categories_sv.set('-1')

    def _set_text_list_selection(self, text_idx_to_select):
        for text_list_item_idx, text_list_item in enumerate(self.texts_list.get_children('')):
            if text_idx_to_select == text_list_item_idx:
                self.texts_list.selection_set((text_list_item,))
                break

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

    def _select_radiobutton(self, idx):
        if idx == 0:
            self.nocategory_rb.invoke()
        else:
            idx -= 1
            rb_keys = list(self.categories_rb.keys())
            if idx <= (len(rb_keys) - 1):
                rb_key_to_invoke = rb_keys[idx]
                self.categories_rb[rb_key_to_invoke].invoke()

    def _mark_text(self, text_id: int, category_id: int):
        self.bus.statechart.launch_mark_text_event(text_id, category_id)

    def select_prev(self):
        text_idx = self._get_prev_text_idx()
        if text_idx is not None:
            self._select_text(text_idx)

    def select_next(self):
        text_idx = self._get_next_text_idx()
        if text_idx is not None:
            self._select_text(text_idx)

    def change_font_size(self, direction: int = 2):
        current_font_size = int(self.current_text_font.cget('size'))
        new_font_size = current_font_size + direction
        self.current_text_font.config(size=new_font_size)

    def _show_load_project_popup(self):
        if path_to_project := filedialog.askopenfilename(filetypes=[('Project', '.json.tl')]):
            self.bus.statechart.launch_load_project_event(path_to_project)

    def _show_save_project_popup(self):
        if path_to_project := filedialog.asksaveasfilename(filetypes=[('Project', '.json.tl')]):
            self.bus.statechart.launch_save_project_event(path_to_project)

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
            self.bus.statechart.launch_import_text_from_file_event(path_to_file)

    @staticmethod
    def _show_help_popup():
        root = tkinter.Toplevel()
        root.title('Help')

        help_text = '''
<Double-Button-1> - select text from list
<Control-n> - new (empty) project
<Control-o> - open existing project
<Control-s> - save project
<Control-k> - add category
<Control-i> - insert text from popup
<Control-f> - import text from file
<Control-z> - undo
<KeyPress-Delete> - delete selected text

<KeyPress-Left>/<KeyPress-Up> - select previous text
<KeyPress-Right>/<KeyPress-Down> - select next text

<KeyPress-equal>/<Control-KP_Add> - make font larger
<KeyPress-KP_Subtract>/<Control-minus> - make font smaller
        '''

        main_frame = tkinter.Frame(root, pady=5, padx=5)
        text = tkinter.Label(main_frame, text=help_text)

        main_frame.grid(column=0, row=0, sticky='nesw')
        text.grid(column=0, row=0, sticky='nesw')

        root.grab_set()
        root.bind('<Escape>', lambda _: root.destroy())

        root.mainloop()

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


    def _show_add_category_popup_popup(self):
        pass

    def _show_import_text_from_input_popup(self):
        pass

    def _show_import_text_from_file_popup(self):
        pass

