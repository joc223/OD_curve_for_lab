import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import re

# -----------------------------------------------------
# 1. 繪圖的核心函式 (已升級)
# -----------------------------------------------------
def plot_hd_curve(od_values, auto_y_axis):
    """
    接收一個 OD 值的列表 (從第1階到最後一階)，
    和一個布林值 (是否自動Y軸)，然後繪製 H&D 曲線圖。
    """
    try:
        # 為了畫出S形曲線 (OD從低到高)，我們將列表反轉
        od_for_plot = od_values[::-1]
        
        # 建立 X 軸 (代表 N 個數據點)
        num_steps = len(od_for_plot)
        x_steps = list(range(1, num_steps + 1)) 

        # --- 【新功能 1：計算 Gamma 值】 ---
        # np.diff() 會計算列表中每個相鄰元素的差值 [od2-od1, od3-od2, ...]
        # 這代表了S曲線每一步的「斜率」或「對比度」
        # 我們找出最大的那個值，作為此曲線的「最大 Gamma (對比度)」
        if len(od_for_plot) > 1:
            max_gamma = np.max(np.diff(od_for_plot))
        else:
            max_gamma = 0 # 只有一個點，無法計算

        # --- 在圖表上方顯示 Gamma 值 ---
        # st.metric 是一個專門用來顯示「指標」的漂亮元件
        st.metric(label="最大 Gamma (對比度)", value=f"{max_gamma:.3f}")
        st.info("Gamma 值代表 H&D 曲線最陡處的斜率，值越大代表對比度越高。")


        # --- 開始繪圖 ---
        fig, ax = plt.subplots(figsize=(10, 7))

        # 處理中文顯示 (Plan B: 使用文泉驛正黑)
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False 

        ax.plot(x_steps, od_for_plot, marker='o', linestyle='-', linewidth=2, color='black')

        # --- 設定圖表 ---
        ax.set_title("實驗數據：特性曲線 (Characteristic Curve)", fontsize=18)
        ax.set_xlabel(f"曝光階 (從第{num_steps}階到第1階)", fontsize=14)
        ax.set_ylabel("光密度 (OD值)", fontsize=14)

        # --- 【新功能 2：自動Y軸】 ---
        if auto_y_axis:
            # 如果勾選了「自動」，我們就讓 Matplotlib 自己決定
            # 只需要設定一個合理的下限 (例如 0 或 0.3)
            # 這裡我們讓 Y 軸的頂部和底部都多留一點空間
            ax.set_ylim(bottom=min(od_for_plot) - 0.2, top=max(od_for_plot) + 0.2)
        else:
            # 如果未勾選，就使用您原來的「固定」刻度
            y_ticks = [0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
            ax.set_yticks(y_ticks)
            # 並且使用一個固定的範圍，確保所有刻度都顯示
            ax.set_ylim(bottom=0.2, top=max(3.6, max(od_for_plot) + 0.2))


        # --- 設定 X 軸刻度 (您調整過的 25 階邏輯) ---
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
        st.pyplot(fig)
        st.success("H&D 曲線產生完畢！")

    except Exception as e:
        st.error(f"繪圖時發生錯誤：{e}")
        st.error("請檢查您的 OD 數據是否均為有效的數字。")

# -----------------------------------------------------
# 2. Streamlit App 主程式
# -----------------------------------------------------
st.title("特性曲線的繪圖產生器 (Characteristic Curve Plotter)")
st.info("您可以自訂曝光階數，並輸入對應的 OD 數據來產生曲線。")

# --- A. 詢問使用者有多少曝光階 ---
if 'num_steps' not in st.session_state:
    st.session_state['num_steps'] = 0

st.header("1. 您總共有多少個曝光階？") 
num_input = st.number_input(
    " ",  # 標籤 (Label) 留空
    min_value=1, 
    max_value=200, 
    value=21, 
    step=1, 
    label_visibility="hidden" 
)

if st.button("產生輸入格"):
    st.session_state['num_steps'] = num_input
    st.session_state['od_values'] = ["0.0"] * num_input

# --- 【新功能 2：Y 軸選項】 ---
# 我們把 Y 軸的選項放在這裡
auto_y_axis_checkbox = st.checkbox("使用自動 Y 軸刻度 (建議新數據使用)", value=False)


# --- B. 只有當 'num_steps' > 0 時，才顯示 OD 輸入區 ---
if st.session_state['num_steps'] > 0:
    st.header(f"2. 請輸入 {st.session_state['num_steps']} 個 OD 數據")
    
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

    # --- C. 當使用者按下「產生圖表」按鈕後 ---
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

                # 呼叫繪圖函式，並把「Y 軸選項」傳遞進去
                plot_hd_curve(od_values_final, auto_y_axis_checkbox)

        except Exception as e:
            st.error(f"處理數據時發生錯誤：{e}")
            st.error("請檢查您的輸入是否都為數字。")

# --- D. 重設按鈕 ---
st.divider()
if st.button("重設 (清除所有輸入值)"):
    st.session_state['num_steps'] = 0
    st.rerun()
    