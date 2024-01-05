import importlib.util
import subprocess
import sys

def check_and_install_package(package_name):
    if importlib.util.find_spec(package_name) is None:
        try:
            print(f"{package_name} 未安裝，正在嘗試自動安裝...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
            print(f"{package_name} 安裝成功。")
        except subprocess.CalledProcessError:
            print(f"無法自動安裝 {package_name}。請手動安裝後再運行程式。")
            sys.exit(1)
    else:
        print(f"{package_name} 已安裝。")

# Check and install required packages
check_and_install_package('pandas')
check_and_install_package('mplfinance')
check_and_install_package('Pillow')
check_and_install_package('twstock')
check_and_install_package('matplotlib')
check_and_install_package('lxml')  # 新增的檢查和安裝 lxml 的部分

import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import datetime
from PIL import Image, ImageTk
import twstock
import matplotlib.pyplot as plt
import tkinter.font as tkFont
from tkinter import filedialog

# 全局變數
current_xlim = None
current_ylim = None
zoom_factor = 0.1  # 缩放比例
df = None  # 初始化一个空的DataFrame
ax = None  # 初始化一个空的Axes
canvas = None  # 初始化一个空的Canvas
data_tree = None  # 初始化一个空的data_tree

# 顯示數據函數
def show_data(df):
    # 首先清除 Treeview 中的就數據
    for i in table.get_children():
        table.delete(i)
    
    # 設置 Treeview 控件以顯示列頭
    table['columns'] = list(df.reset_index().columns)
    table['show'] = 'headings'
    for col in table['columns']:
        table.heading(col, text=col)
        table.column(col, width=100)  # 設定列寬
    # 插入新數据
    for index, row in df.iterrows():
        table.insert('', 'end', values=[index] + row.tolist())  # 包含索引

# 在新窗口中顯示數据的函数
def show_data_in_new_window(df):
    global data_tree  # 添加這行来聲明 data_tree 為全局變量

    # 創建一個新視窗
    data_window = tk.Toplevel(root)
    data_window.title("股票數據")
    data_window.geometry("800x600")
     
     # 現在 data_tree 是一个全局變量，之後可以在其他函數中引用它
    data_tree = ttk.Treeview(data_window)

    # 創建 Treeview 控件以展示數據
    data_tree = ttk.Treeview(data_window)
    data_tree.pack(expand=True, fill='both')

    # 配置滾動條
    scrollbar = ttk.Scrollbar(data_window, orient="vertical", command=data_tree.yview)
    scrollbar.pack(side='right', fill='y')
    data_tree.configure(yscrollcommand=scrollbar.set)

    # 設置 Treeview 控件以顯示列頭
    columns = ['Date'] + list(df.columns)  # 包括日期列
    data_tree['columns'] = columns
    data_tree['show'] = 'headings'
    for col in columns:
        data_tree.heading(col, text=col)
        data_tree.column(col, width=100)  # 設定列寬

    # 插入新數据
    for index, row in df.iterrows():
        row_data = [index.strftime('%Y-%m-%d')] + list(row)  # 格式化日期並包括在數据中
        data_tree.insert('', 'end', values=row_data)

# 獲取股票數据的函數
def fetch_data():
    global df, ax, canvas
    target_stock = stock_code_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    # 检查日期格式是否正确
    try:
        start_datetime = datetime.strptime(start_date, '%Y/%m/%d')
        end_datetime = datetime.strptime(end_date, '%Y/%m/%d')
    except ValueError as e:
        messagebox.showerror("错误", "日期格式错误，请使用 YYYY/MM/DD 格式")
        return

    # 创建进度条窗口
    progress_win = tk.Toplevel(root)
    progress_win.title("加载进度")
    progress = ttk.Progressbar(progress_win, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)
    progress['maximum'] = 100
    progress_win.update()

    try:
        stock = twstock.Stock(target_stock)
        target_price = stock.fetch_from(start_datetime.year, start_datetime.month)
        
        df = pd.DataFrame(target_price)
        df.columns = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transaction']
        df['Volume'] = df['Turnover']
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        df = df.loc[start_datetime:end_datetime]
        
        show_data_in_new_window(df)  # 在新窗口中展示數據
        plot_interactive_candlestick(df)  # 繪制 K 線圖

        # 更新进度条
        progress['value'] = 50
        progress_win.update_idletasks()

    except Exception as e:
        messagebox.showerror("錯誤", str(e))
        return

    try:
        stock = twstock.Stock(target_stock)
        target_price = stock.fetch_from(start_datetime.year, start_datetime.month)
        
        df = pd.DataFrame(target_price)
        df.columns = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transaction']
        df['Volume'] = df['Turnover']
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        show_data(df)  # 調用 show_data 函数来展示數据
        plot_interactive_candlestick(df)  # 繪制 K 線圖

        df = df.loc[start_datetime:end_datetime]

        progress['value'] = 100
        progress_win.update_idletasks()

        # 打印整齊的表格格式到控制台，不顯示索引列
        print(df.reset_index().to_string(index=False))

        messagebox.showinfo("成功", f"股票數据已獲取並繪制 K 線圖於 {start_date} 到 {end_date}")
    except Exception as e:
        messagebox.showerror("錯誤", str(e))
        
    finally:
        # 关闭进度条窗口
        progress_win.destroy()

# 清除數据的函數
def clear_data():
    global ax, canvas
    if ax is not None:
        ax.cla()
    if canvas is not None:
        canvas.get_tk_widget().pack_forget()
    for i in table.get_children():
        table.delete(i)

# 缩放圖表的函数
def zoom_in(ax, canvas):
    global current_xlim
    global current_ylim
    if current_xlim is None:
        current_xlim = ax.get_xlim()
    if current_ylim is None:
        current_ylim = ax.get_ylim()
    
    # 計算新的x軸範圍
    cur_xrange = (current_xlim[1] - current_xlim[0]) * (1 - zoom_factor)
    cur_xlim_middle = (current_xlim[1] + current_xlim[0]) / 2
    new_xlim = (cur_xlim_middle - cur_xrange / 2, cur_xlim_middle + cur_xrange / 2)

    # 應用新的範圍
    ax.set_xlim(new_xlim)
    canvas.draw_idle()

def zoom_out(ax, canvas):
    global current_xlim
    global current_ylim
    if current_xlim is None:
        current_xlim = ax.get_xlim()
    if current_ylim is None:
        current_ylim = ax.get_ylim()
    
    # 計算新的x軸範圍
    cur_xrange = (current_xlim[1] - current_xlim[0]) * (1 + zoom_factor)
    cur_xlim_middle = (current_xlim[1] + current_xlim[0]) / 2
    new_xlim = (cur_xlim_middle - cur_xrange / 2, cur_xlim_middle + cur_xrange / 2)

    # 應用新的範圍
    ax.set_xlim(new_xlim)
    canvas.draw_idle()

# 平移圖表的函数
def pan_left(ax, canvas):
    global current_xlim
    if current_xlim is None:
        current_xlim = ax.get_xlim()
    
    # 計算新的x軸範圍
    shift = (current_xlim[1] - current_xlim[0]) * zoom_factor
    new_xlim = (current_xlim[0] - shift, current_xlim[1] - shift)

    # 應用新的範圍
    ax.set_xlim(new_xlim)
    canvas.draw_idle()

def pan_right(ax, canvas):
    global current_xlim
    if current_xlim is None:
        current_xlim = ax.get_xlim()
    
    # 計算新的x軸範圍
    shift = (current_xlim[1] - current_xlim[0]) * zoom_factor
    new_xlim = (current_xlim[0] + shift, current_xlim[1] + shift)

    # 應用新的範圍
    ax.set_xlim(new_xlim)
    canvas.draw_idle()

# 繪製交互式 K 線圖的函數
def plot_interactive_candlestick(df):
    global canvas, ax  # 宣告 ax 為全域變數
    # 清除之前的圖表
    for widget in frame_chart.winfo_children():
        widget.destroy()

    # 創建新的圖表和軸對象
    fig, ax = plt.subplots(figsize=(6, 4))  # 使用 ax 而非 ax1
    mpf.plot(df, ax=ax, type='candle', mav=(3, 6, 9))  # 使用 ax

    # 創建 FigureCanvasTkAgg 物件
    canvas = FigureCanvasTkAgg(fig, master=frame_chart)
    canvas.draw()

    # 把繪製的圖表顯示在 Tkinter 的 Frame 上
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # 添加 matplotlib 的導航工具欄到 Tkinter 的 Frame 上
    toolbar = NavigationToolbar2Tk(canvas, frame_chart)
    toolbar.update()

def save_data_as_csv():
    if df is not None:
        # 啟動檔案儲存對話框，讓用戶選擇保存位置和輸入檔案名稱
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
        if file_path:  # 確保用戶選擇了檔案路徑
            try:
                df.to_csv(file_path, index=True)  # 保存DataFrame到CSV檔案
                messagebox.showinfo("成功", "數據已成功保存為CSV檔案")
            except Exception as e:
                messagebox.showerror("錯誤", f"無法保存檔案: {e}")
    else:
        messagebox.showwarning("警告", "沒有數據可保存")


# 創建主窗口
root = tk.Tk()
root.title("股票數據獲取並繪製k線圖")
root.geometry("800x400")

# 創建 GUI 组件
tk.Label(root, text="股票代碼:").pack()
stock_code_entry = tk.Entry(root)
stock_code_entry.pack()

tk.Label(root, text="起始日期 (YYYY/MM/DD):").pack()
start_date_entry = tk.Entry(root)
start_date_entry.pack()

tk.Label(root, text="结束日期 (YYYY/MM/DD):").pack()
end_date_entry = tk.Entry(root)
end_date_entry.pack()

tk.Button(root, text="股票數據獲取並繪製k線圖", command=fetch_data).pack()
tk.Button(root, text="清除資料", command=clear_data).pack()

frame_table = tk.Frame(root)
frame_table.pack(expand=True, fill='both')

frame_chart = tk.Frame(root)
frame_chart.pack(expand=True, fill='both')

table = ttk.Treeview(frame_table)  # 初始化 Treeview

# 添加關閉應用程式的按钮
close_button = tk.Button(root, text="關閉程式", command=lambda: root.destroy())
close_button.pack()

tk.Button(root, text="保存數據為CSV", command=save_data_as_csv).pack()


# 主循環
root.mainloop()