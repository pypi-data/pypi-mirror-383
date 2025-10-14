from nicegui import ui
from nicegui.events import KeyEventArguments

class TListBox:
    def __init__(self, 
                 Pmi_width=200, 
                 Pmi_height=200,
                 Pms_bg_color='white',
                 Pms_font_color='black',
                 Pmi_font_size=14,
                 Pmb_multi_select=False,
                 Pms_selected_color='#add8e6'):   # 選中光棒顏色
        self.items = []
        self.selected_index = None
        self.selected_indices = set()   # 多選模式
        self.on_dblclick = None
        self.on_enter = None
        self.mb_multi_select = Pmb_multi_select
        self.ms_bg_color = Pms_bg_color
        self.ms_font_color = Pms_font_color
        self.mi_font_size = Pmi_font_size
        self.ms_selected_color = Pms_selected_color

        # 外層容器
        self.container = ui.column().style(
            f'border:1px solid #888; padding:0; '
            f'width:{Pmi_width}px; height:{Pmi_height}px; '
            f'overflow-y:auto; background-color:{self.ms_bg_color}; '
            'box-sizing:border-box;'
        )

        # 鍵盤事件監聽
        ui.add_head_html('''
        <script>
        document.addEventListener('keydown', function(event) {
            window.dispatchEvent(new CustomEvent('listbox_key', { detail: event.key }));
        });
        </script>
        ''')
        ui.on('listbox_key', self._on_key)

    # ======================================================
    # 新增項目
    def Add(self, Pms_text):
        index = len(self.items)
        with self.container:
            lbl = ui.label(Pms_text).style(
                f'display:block; text-align:left; width:100%; padding:4px; '
                f'cursor:pointer; background-color:{self.ms_bg_color}; '
                f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px; '
                'box-sizing:border-box; user-select:none;'
            )
            lbl.on('click', lambda e, idx=index: self._on_click(idx))
            lbl.on('dblclick', lambda e, idx=index: self._on_dblclick(idx))
        self.items.append(lbl)
        return index

    # 刪除指定項目
    def Delete(self, Pmi_index):
        if 0 <= Pmi_index < len(self.items) and self.items[Pmi_index]:
            self.items[Pmi_index].delete()
            self.items[Pmi_index] = None
            if self.selected_index == Pmi_index:
                self.selected_index = None
            if Pmi_index in self.selected_indices:
                self.selected_indices.remove(Pmi_index)

    # 清除全部項目
    def Clear(self):
        for lbl in self.items:
            if lbl:
                lbl.delete()
        self.items.clear()
        self.selected_index = None
        self.selected_indices.clear()

    # 設定選中光棒顏色
    def SetSelectedColor(self, Pms_color):
        self.ms_selected_color = Pms_color
        # 更新目前選中項目的背景色
        if not self.mb_multi_select and self.selected_index is not None:
            self.items[self.selected_index].style(
                f'display:block; text-align:left; width:100%; padding:4px; '
                f'cursor:pointer; background-color:{self.ms_selected_color}; '
                f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                'box-sizing:border-box; user-select:none;'
            )
        elif self.mb_multi_select:
            for idx in self.selected_indices:
                self.items[idx].style(
                    f'display:block; text-align:left; width:100%; padding:4px; '
                    f'cursor:pointer; background-color:{self.ms_selected_color}; '
                    f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                    'box-sizing:border-box; user-select:none;'
                )

    # ======================================================
    # 點擊事件
    def _on_click(self, index):
        if not self.mb_multi_select:
            # 單選模式
            if self.selected_index is not None and self.items[self.selected_index]:
                self.items[self.selected_index].style(
                    f'display:block; text-align:left; width:100%; padding:4px; '
                    f'cursor:pointer; background-color:{self.ms_bg_color}; '
                    f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                    'box-sizing:border-box; user-select:none;'
                )
            self.selected_index = index
            self.items[index].style(
                f'display:block; text-align:left; width:100%; padding:4px; '
                f'cursor:pointer; background-color:{self.ms_selected_color}; '
                f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                'box-sizing:border-box; user-select:none;'
            )
            print("選中項目索引:", self.selected_index)
        else:
            # 多選模式
            if index in self.selected_indices:
                self.selected_indices.remove(index)
                self.items[index].style(
                    f'display:block; text-align:left; width:100%; padding:4px; '
                    f'cursor:pointer; background-color:{self.ms_bg_color}; '
                    f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                    'box-sizing:border-box; user-select:none;'
                )
            else:
                self.selected_indices.add(index)
                self.items[index].style(
                    f'display:block; text-align:left; width:100%; padding:4px; '
                    f'cursor:pointer; background-color:{self.ms_selected_color}; '
                    f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                    'box-sizing:border-box; user-select:none;'
                )
            print("多選目前選中:", sorted(list(self.selected_indices)))

    # ======================================================
    # 雙擊事件
    def _on_dblclick(self, index):
        if self.on_dblclick:
            self.on_dblclick(index)
        print("雙擊項目索引:", index)

    # ======================================================
    # 鍵盤事件
    def _on_key(self, key):
        if not self.items:
            return
        if not self.mb_multi_select:
            if self.selected_index is None:
                self.selected_index = 0
                self._update_selection()
                return
            if key == 'ArrowUp':
                self.selected_index = max(0, self.selected_index - 1)
                self._update_selection()
            elif key == 'ArrowDown':
                self.selected_index = min(len(self.items)-1, self.selected_index + 1)
                self._update_selection()
            elif key == 'Enter':
                if self.on_enter:
                    self.on_enter(self.selected_index)
                print("Enter 選中項目索引:", self.selected_index)

    # ======================================================
    # 更新單選選中狀態
    def _update_selection(self):
        for i, lbl in enumerate(self.items):
            if not lbl:
                continue
            if i == self.selected_index:
                lbl.style(
                    f'display:block; text-align:left; width:100%; padding:4px; '
                    f'cursor:pointer; background-color:{self.ms_selected_color}; '
                    f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                    'box-sizing:border-box; user-select:none;'
                )
                lbl.element.scrollIntoView({'block':'nearest'})
            else:
                lbl.style(
                    f'display:block; text-align:left; width:100%; padding:4px; '
                    f'cursor:pointer; background-color:{self.ms_bg_color}; '
                    f'color:{self.ms_font_color}; font-size:{self.mi_font_size}px;'
                    'box-sizing:border-box; user-select:none;'
                )


# ============================================================
# 範例使用
# ============================================================
"""
listbox = TListBox(
    Pmi_width=300, 
    Pmi_height=200, 
    Pms_bg_color='#222', 
    Pms_font_color='white', 
    Pmi_font_size=16,
    Pmb_multi_select=True     # ← 支援多選
)
for i in range(15):
    listbox.Add(f'項目 {i+1}')

listbox.on_dblclick = lambda idx: print(f"雙擊事件: {idx}")
listbox.on_enter = lambda idx: print(f"Enter 選中: {idx}")

ui.run()
"""