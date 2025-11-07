import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import re

# -----------------------------------------------------
# 1. 繪圖的核心函式
# -----------------------------------------------------
def plot_hd_curve(od_values):
    try:
        od_for_plot = od_values[::-1]
        
        num_steps = len(od_for_plot)
        x_steps = list(range(1, num_steps + 1)) 

        fig, ax = plt.subplots(figsize=(10, 7))

        # 處理中文顯示
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False 

        # 畫出曲線
        ax.plot(x_steps, od_for_plot,
                 marker='o',
                 linestyle='-',
                 linewidth=2,
                 color='black')

        # 設定圖表
        ax.set_title("實驗數據：特性曲線 (Characteristic Curve)", fontsize=18)
        ax.set_xlabel(f"曝光階 (從第{num_steps}階到第1階)", fontsize=14)
        ax.set_ylabel("光密度 (OD值)", fontsize=14)

        # 設定 Y 軸刻度
        y_ticks = [0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        ax.set_yticks(y_ticks)
        ax.set_ylim(bottom=min(0.2, min(od_for_plot) - 0.2), top=max(3.6, max(od_for_plot) + 0.2))

        # 設定 X 軸刻度
        x_ticks = [] 
        if num_steps <= 25:
            x_ticks = list(range(1, num_steps + 1)) 
        elif num_steps <= 30:
            step_interval = 2
            x_ticks = list(range(1, num_steps + 1, step_interval))
        elif num_steps <= 70:
            step_interval = 5
            x_ticks = list(range(1, num_steps + 1, step_interval))
        else:
            step_interval = 10
            x_ticks = list(range(1, num_steps + 1, step_interval))

        if num_steps > 25 and num_steps not in x_ticks:
            x_ticks.append(num_steps) 

        ax.set_xticks(x_ticks)
        ax.set_xlim(left=0.5, right=num_steps + 0.5)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        return fig # 返回圖表物件

    except Exception as e:
        st.error(f"繪圖時發生錯誤：{e}")
        st.error("請檢查您的 OD 數據是否均為有效的數字。")
        return None

# -----------------------------------------------------
# 2. Streamlit App 主程式
# -----------------------------------------------------
# st.set_page_config(layout="wide") 
st.title("特性曲線的繪圖產生器(Characteristic Curve Plotter)")
st.info("您可以自訂曝光階數，並輸入對應的 OD 數據來產生曲線。")

# -----------------------------------------------------
# 3. 使用說明介面
# -----------------------------------------------------
with st.expander("點我查看「使用說明」", expanded=True): # 預設為展開
    st.markdown("""
    本工具專為繪製特性曲線 (Characteristic Curve) 而設計。
    
    **使用步驟：**
    1.  **輸入曝光階數**：在「1. 您總共有多少個曝光階？」中輸入您的總階數（例如 21），然後按下「產生輸入格」。
    2.  **輸入 OD 數據**：在「2. 請輸入 ... 數據」區塊中，依照您的實驗數據（從第1階到最後一階）依序填入所有的 OD 值。
    3.  **產生圖表**：按下「產生曲線圖」按鈕。
    
    **圖表解讀：**
    * **特性曲線**：系統會自動將您的數據反轉（從最低曝光到最高曝光）來繪製 S 形曲線。
    """)

# A. 詢問曝光階
if 'num_steps' not in st.session_state:
    st.session_state['num_steps'] = 0

st.header("1. 您總共有多少個曝光階？") 

num_input = st.number_input(
    " ", 
    min_value=1, 
    max_value=200, 
    value=21, 
    step=1, 
    label_visibility="hidden"
)

if st.button("產生輸入格"):
    st.session_state['num_steps'] = num_input
    st.session_state['od_values'] = ["0.0"] * num_input

# B. 只有當 'num_steps' > 0 時，才顯示 OD 輸入區
if st.session_state['num_steps'] > 0:
    
    st.header(f"2. 請輸入 {st.session_state['num_steps']} 個 OD 數據")
    
    # 建立一個 Form (表單)
    with st.form("od_form"):
        input_values = []
        num_columns = 5
        num_rows = (st.session_state['num_steps'] + num_columns - 1) // num_columns
        step_counter = 0
        
        for r in range(num_rows):
            cols = st.columns(num_columns) 
            
            for i in range(num_columns):
                if step_counter < st.session_state['num_steps']:
                    step_index = step_counter + 1
                    
                    val = cols[i].text_input(f"第 {step_index} 階", 
                                             key=f"od_{step_index}",
                                             placeholder="例如 3.08")
                    input_values.append(val)
                    step_counter += 1

        submitted = st.form_submit_button("產生曲線圖")
    
    # C. 當使用者按下「產生圖表」按鈕後
    if submitted:
        try:
            if any(val.strip() == "" for val in input_values):
                st.warning("您有部分數據尚未填寫，請填寫完畢後再試一次。")
            else:
                od_values_final = []
                for val in input_values:
                    match = re.search(r"[-+]?\d*\.\d+|\d+", val) 
                    if match:
                        od_values_final.append(float(match.group(0)))
                    else:
                        od_values_final.append(0.0)
                        st.warning(f"無法解析輸入值 '{val}'，已當作 0.0 處理。")

                # 呼叫上面定義的繪圖函式
                fig = plot_hd_curve(od_values_final) # 獲取圖表物件
                if fig:
                    st.pyplot(fig) # 在 Streamlit 中顯示圖表

        except Exception as e:
            st.error(f"處理數據時發生錯誤：{e}")
            st.error("請檢查您的輸入是否都為數字。")

# D. 重設按鈕           
st.divider()
if st.button("重設 (清除所有輸入值)"):
    st.session_state['num_steps'] = 0
    st.rerun() # 重新整理頁面

st.divider()
st.caption("© 2025 CSMU MIRS 1298002 wcy. 如果有發現未修復的 Bug 或建議，請聯絡 xes67421@gmail.com 謝謝。")
