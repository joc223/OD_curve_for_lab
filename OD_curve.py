import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import re

# --- 1. 設定網頁標題和說明 ---
st.set_page_config(layout="wide") # 讓網頁寬一點
st.title("特性曲線 (Characteristic Curve) 產生器")
st.info("請在下面的文字框中輸入您的 OD 值 (從第1階到第21階)，並用逗號、空格或換行符號分隔。")

# --- 2. 準備預設的輸入數據 (來自您照片中的範例) ---
default_data_str = """
3.08, 3.08, 3.08, 3.08, 3.07,
3.05, 2.99, 2.89, 2.84, 2.74,
2.58, 2.44, 2.28, 2.04, 1.77,
1.56, 1.34, 1.14, 0.95, 0.86,
0.91
"""

# --- 3. 建立輸入框 ---
data_input = st.text_area("請在此輸入 OD 數據 (共 21 個值)：", 
                          value=default_data_str, 
                          height=200)

# --- 4. 建立繪圖按鈕 ---
if st.button("產生 H&D 曲線圖"):
    
    # --- 5. 處理並清理輸入的文字 ---
    try:
        # 抓取所有數字
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", data_input)
        
        # 將字串轉換為浮點數
        od_values_from_table = [float(num) for num in numbers]
        
        # 檢查數據數量
        if len(od_values_from_table) != 21:
            st.error(f"輸入錯誤！您輸入了 {len(od_values_from_table)} 個值，但需要剛好 21 個值。")
        else:
            st.success(f"成功讀取 {len(od_values_from_table)} 筆 OD 數據！")
            
            # --- 6. 繪圖邏輯 ---
            od_for_plot = od_values_from_table[::-1] # 反轉列表
            x_steps = list(range(1, len(od_for_plot) + 1)) # [1, 2, ..., 21]

            # --- 7. 開始繪圖 (使用 Matplotlib) ---
            fig, ax = plt.subplots(figsize=(8, 5))

            # 處理中文顯示 (使用 Noto Sans CJK TC，因為我們用 packages.txt 安裝了它)
            plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False 

            ax.plot(x_steps, od_for_plot, marker='o', linestyle='-', linewidth=2, color='black')
            ax.set_title("實驗數據：特性曲線 (H&D Curve)", fontsize=16)
            ax.set_xlabel("相對曝光階 (從 第21階 到 第1C階)", fontsize=12)
            ax.set_ylabel("光密度 (OD)", fontsize=12)

            # 設定 Y 軸刻度
            y_ticks = [0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
            ax.set_yticks(y_ticks)
            ax.set_ylim(bottom=0.2, top=3.6) 

            # 設定 X 軸刻度
            x_ticks = list(range(1, 22, 2)) # [1, 3, 5, ..., 21]
            ax.set_xticks(x_ticks)
            ax.set_xlim(left=0.5, right=21.5)

            ax.grid(True, which='both', linestyle='--', linewidth=0.5)

            # --- 8. 在 Streamlit 中顯示圖表 ---
            st.pyplot(fig)

    except Exception as e:
        st.error(f"發生錯誤： {e}")
