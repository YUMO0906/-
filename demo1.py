import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from PIL import Image, ImageTk
import twstock
from matplotlib.widgets import Cursor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# 設定背景圖片的函數
def set_background(root, image_path):
    image = Image.open(image_path)
    image = image.resize((1920, 1080))
    bg_image = ImageTk.PhotoImage(image)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_image

# 獲取數據的函數
def fetch_data():
    target_stock = stock_code_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    # 檢查日期格式是否正確
    try:
        start_datetime = datetime.strptime(start_date, '%Y/%m/%d')
        end_datetime = datetime.strptime(end_date, '%Y/%m/%d')
    except ValueError as e:
        messagebox.showerror("錯誤", "日期格式錯誤，請使用 YYYY/MM/DD 格式")
        return

    try:
        stock = twstock.Stock(target_stock)
        target_price = stock.fetch_from(start_datetime.year, start_datetime.month)

        df = pd.DataFrame(target_price)
        df.columns = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transaction']
        df['Volume'] = df['Turnover']
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        df = df.loc[start_datetime:end_datetime]  # 使用 .loc[] 來選擇日期範圍

        show_data(df)
        plot_interactive_candlestick(df)

        messagebox.showinfo("成功", f"股票數據已獲取並繪製 K 線圖於 {start_date} 到 {end_date}")
    except Exception as e:
        messagebox.showerror("錯誤", str(e))

# 顯示數據的函數
def show_data(df):
    for i in table.get_children():
        table.delete(i)
    
    table["columns"] = ("Date", "Open", "High", "Low", "Close")
    table["show"] = "headings"
    table.heading("Date", text="日期")
    table.column("Date", width=100)
    table.heading("Open", text="開盤價")
    table.heading("High", text="最高價")
    table.heading("Low", text="最低價")
    table.heading("Close", text="收盤價")

    for date, row in df.iterrows():
        table.insert("", "end", values=(date.strftime('%Y-%m-%d'), row["Open"], row["High"], row["Low"], row["Close"]))

    table.pack(expand=True, fill='both')

# 清除數據的函數
def clear_data():
    for i in table.get_children():
        table.delete(i)
    for widget in frame_chart.winfo_children():
        widget.destroy()

# 繪製互動式 K 線圖的函數
def plot_interactive_candlestick(df):
    for widget in frame_chart.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(10, 8))
    mpf.plot(df, ax=ax, type='candle', mav=(3, 6, 9), show_nontrading=True)

    canvas = FigureCanvasTkAgg(fig, master=frame_chart)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')

    toolbar = NavigationToolbar2Tk(canvas, frame_chart)
    toolbar.update()

# 創建主窗口
root = tk.Tk()
root.title("股票數據獲取與 K 線圖繪製")
root.geometry("800x600")

# 設定背景圖片
set_background(root, "E:\原神甘雨-6d5rgq.jpg")  # 修改为您的背景图片路径

# 創建 GUI 組件
tk.Label(root, text="股票代碼:").pack()
stock_code_entry = tk.Entry(root)
stock_code_entry.pack()

tk.Label(root, text="起始日期 (YYYY/MM/DD):").pack()
start_date_entry = tk.Entry(root)
start_date_entry.pack()

tk.Label(root, text="結束日期 (YYYY/MM/DD):").pack()
end_date_entry = tk.Entry(root)
end_date_entry.pack()

tk.Button(root, text="獲取並繪製 K 線圖", command=fetch_data).pack()
tk.Button(root, text="清除數據", command=clear_data).pack()

frame_table = tk.Frame(root)
frame_table.pack(expand=True, fill='both')

frame_chart = tk.Frame(root)
frame_chart.pack(expand=True, fill='both')

table = ttk.Treeview(frame_table)  # 初始化 Treeview

# 主迴圈
root.mainloop()