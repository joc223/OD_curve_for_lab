import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import re

# -----------------------------------------------------
# 1. 繪圖的核心函式 (我們把它獨立出來)
# -----------------------------------------------------
def plot_hd_curve(od_values):
    """
    接收一個 OD 值的列表 (從第1階到最後一階)，
    然後繪製 H&D 曲線圖。
    """
    try:
        # 為了畫出S形曲線 (OD從低到高)，我們將列表反轉
        # (即從 最後一階 -> 第1階)
        od_for_plot = od_values[::-1]
        
        # 建立 X 軸 (代表 N 個數據點)
        num_steps = len(od_for_plot)
        x_steps = list(range(1, num_steps + 1)) # [1, 2, 3, ..., N]

        # --- 開始繪圖 ---
        fig, ax = plt.subplots(figsize=(10, 7))

        # 處理中文顯示 (Plan B: 使用文泉驛正黑)
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False 

        # 畫出曲線
        ax.plot(x_steps, od_for_plot, 
                 marker='o',       # 'o' 標記
                 linestyle='-',    # 實線
                 linewidth=2,      
                 color='black')

        # --- 設定圖表 ---
        ax.set_title("實驗數據：特性曲線 (Characteristic Curve)", fontsize=18)
        ax.set_xlabel(f"曝光階 (從第{num_steps}階到第1階)", fontsize=14)
        ax.set_ylabel("光密度 (OD值)", fontsize=14)

        # 設定 Y 軸刻度 (保留您原本的要求)
        y_ticks = [0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        ax.set_yticks(y_ticks)
        ax.set_ylim(bottom=min(0.2, min(od_for_plot) - 0.2), top=max(3.6, max(od_for_plot) + 0.2))


        # 設定 X 軸刻度 (讓它自動調整)

        # --- 修正：在這裡初始化 x_ticks 變數 ---
        x_ticks = [] 
        # ----------------------------------------

        # --- NEW LOGIC ---
        # 如果總階數小於等於 25，就顯示全部的刻度 (1, 2, 3...)
        if num_steps <= 25:
            x_ticks = list(range(1, num_steps + 1)) # [1, 2, 3, ..., 8]
        # 如果總階數比較多，才開始簡化刻度
        elif num_steps <= 30:
            step_interval = 2
            x_ticks = list(range(1, num_steps + 1, step_interval))
        elif num_steps <= 70:
            step_interval = 5
            x_ticks = list(range(1, num_steps + 1, step_interval))
        else:
            step_interval = 10
            x_ticks = list(range(1, num_steps + 1, step_interval))

        # 確保最後一階的刻度一定會被顯示 (for step_interval > 1 cases)
        if num_steps > 25 and num_steps not in x_ticks:
            x_ticks.append(num_steps) 

        ax.set_xticks(x_ticks)
        ax.set_xlim(left=0.5, right=num_steps + 0.5)

        # 加上網格線
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        # 在 Streamlit 中顯示圖表
        st.pyplot(fig)

    except Exception as e:
        st.error(f"繪圖時發生錯誤：{e}")
        st.error("請檢查您的 OD 數據是否均為有效的數字。")

# -----------------------------------------------------
# 2. Streamlit App 主程式
# -----------------------------------------------------
# st.set_page_config(layout="wide")
st.title("特性曲線的繪圖產生器(Characteristic Curve Plotter)")
st.info("您可以自訂曝光階數，並輸入對應的 OD 數據來產生曲線。")

# --- A. 詢問使用者有多少曝光階 ---

# 'st.session_state' 是 Streamlit 用來「記住」變數的方法
# 我們檢查 'num_steps' 是否已經被設定過了
if 'num_steps' not in st.session_state:
    st.session_state['num_steps'] = 0

# 建立一個輸入框和按鈕
num_input = st.number_input("1. 您總共有多少個曝光階？", min_value=1, max_value=200, value=21, step=1)
if st.button("產生輸入格"):
    st.session_state['num_steps'] = num_input
    # 清空可能存在的舊數據
    st.session_state['od_values'] = ["0.0"] * num_input

# --- B. 只有當 'num_steps' > 0 時，才顯示 OD 輸入區 ---

if st.session_state['num_steps'] > 0:
    
    st.header(f"2. 請輸入 {st.session_state['num_steps']} 個 OD 數據")
    
    # 建立一個 Form (表單)，這樣使用者輸入完20個值後，可以「一次提交」
    with st.form("od_form"):
        
        # 準備一個列表來儲存所有的輸入值
        input_values = []
        
        # 您的要求：5個為一排
        num_columns = 5
        
        # 計算總共需要多少「排」
        num_rows = (st.session_state['num_steps'] + num_columns - 1) // num_columns
        
        step_counter = 0 # 曝光階的計數器
        
        for r in range(num_rows):
            # 建立 5 個欄位 (5個為一排)
            cols = st.columns(num_columns) 
            
            for i in range(num_columns):
                if step_counter < st.session_state['num_steps']:
                    step_index = step_counter + 1
                    
                    # 在對應的欄位中建立一個文字輸入框
                    # 'key' 是必要的，用來區分不同的輸入框
                    val = cols[i].text_input(f"第 {step_index} 階", 
                                             key=f"od_{step_index}",
                                             placeholder="例如 3.08")
                    input_values.append(val)
                    step_counter += 1

        # 在 Form (表單) 的最後加上一個提交按鈕
        submitted = st.form_submit_button("產生曲線圖")

    # --- C. 當使用者按下「產生圖表」按鈕後 ---
    
    if submitted:
        # 開始處理數據
        try:
            # 檢查是否有空的輸入框
            if any(val.strip() == "" for val in input_values):
                st.warning("您有部分數據尚未填寫，請填寫完畢後再試一次。")
            else:
                # 嘗試將所有輸入值轉換為浮點數 (float)
                # 使用 re.findall 來抓取數字，避免因空格或非數字字元出錯
                od_values_final = []
                for val in input_values:
                    # 抓取輸入框中的第一個數字
                    match = re.search(r"[-+]?\d*\.\d+|\d+", val) 
                    if match:
                        od_values_final.append(float(match.group(0)))
                    else:
                        # 如果找不到數字，就當作 0.0
                        od_values_final.append(0.0)
                        st.warning(f"無法解析輸入值 '{val}'，已當作 0.0 處理。")

                # st.write(f"您輸入的數據 (共 {len(od_values_final)} 筆):", od_values_final) # 用於除錯
                
                # 呼叫我們在上面定義的繪圖函式
                plot_hd_curve(od_values_final)

        except Exception as e:
            st.error(f"處理數據時發生錯誤：{e}")
            st.error("請檢查您的輸入是否都為數字。")

# --- D. (可選) 增加一個重設按鈕 ---
st.divider()
if st.button("重設 (清除所有輸入值)"):
    st.session_state['num_steps'] = 0
    st.rerun() # 重新整理頁面
