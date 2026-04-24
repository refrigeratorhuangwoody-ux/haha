import streamlit as st
import numpy as np

# --- 頁面配置 ---
st.set_page_config(page_title="Lights Out 求解器", layout="centered")

# --- 核心數學：高斯消去與無解判定 ---
def process_matrix(board, N):
    """
    使用高斯消去法同時判斷：
    1. 是否有解 (Solvability)
    2. 解的內容 (Solution)
    """
    size = N * N
    # 建立 Lights Out 係數矩陣 A
    A = np.zeros((size, size), dtype=int)
    for r in range(N):
        for c in range(N):
            idx = r * N + c
            for dr, dc in [(0,0), (0,1), (0,-1), (1,0), (-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < N and 0 <= nc < N:
                    A[nr * N + nc, idx] = 1
    
    # 增廣矩陣 [A | b]
    b = board.flatten()
    aug = np.column_stack((A, b))
    
    # GF(2) 高斯消去
    pivot = 0
    for j in range(size):
        if pivot >= size: break
        # 找主元
        rows = np.where(aug[pivot:, j] == 1)[0]
        if len(rows) == 0: continue
        row = rows[0] + pivot
        
        # 交換列
        aug[[pivot, row]] = aug[[row, pivot]]
        
        # 消去其他列
        for i in range(size):
            if i != pivot and aug[i, j] == 1:
                aug[i] ^= aug[pivot]
        pivot += 1
    
    # 判斷是否有解：檢查是否存在 [0 0 ... 0 | 1] 的行
    for i in range(pivot, size):
        if aug[i, -1] == 1:
            return None # 無解
            
    # 回傳解矩陣 (取增廣矩陣最後一欄)
    return aug[:, -1][:size].reshape((N, N))

# --- UI 介面 ---
st.title("Lights Out 點燈遊戲求解器")
st.markdown("""
這個工具專門用來**診斷與求解**。請在下方輸入你遇到的盤面狀態，
系統會自動判斷該盤面是否具備數學解。
""")

# 設定盤面大小
N = st.number_input("盤面大小 (N)", min_value=3, max_value=7, value=3)

# 初始化盤面
if 'input_board' not in st.session_state or st.session_state.get('last_N') != N:
    st.session_state.input_board = np.zeros((N, N), dtype=int)
    st.session_state.last_N = N

st.write("### 1. 請設定目前的燈號狀態")
st.caption("點擊方格：🟡 代表亮燈，⚫ 代表熄滅")

# 建立輸入網格
cols = st.columns(N)
for r in range(N):
    for c in range(N):
        label = "🟡" if st.session_state.input_board[r, c] == 1 else "⚫"
        if cols[c].button(label, key=f"in_{r}_{c}", use_container_width=True):
            st.session_state.input_board[r, c] = 1 - st.session_state.input_board[r, c]
            st.rerun()

st.divider()

# --- 求解邏輯 ---
st.write("### 2. 求解結果")

# 即時計算
solution = process_matrix(st.session_state.input_board, N)

if np.sum(st.session_state.input_board) == 0:
    st.info("盤面目前是空的，請先設定燈號狀態。")
elif solution is None:
    st.error("❌ **診斷：此盤面數學上無解**")
    st.warning("在 Lights Out 的機制下，這個特定的燈號組合永遠無法被完全熄滅。")
else:
    st.success("✅ **診斷：此盤面有解！**")
    st.write(f"最少需要按下 **{int(np.sum(solution))}** 個位置即可全數熄滅。")
    
    # 顯示解法
    st.write("#### 💡 解法指引：")
    st.write("請按下標記為 🎯 的位置（順序不影響結果）：")
    
   # 視覺化呈現解法 (使用表格確保絕對對齊)
    # 建立一個 N x N 的陣列，預設填入空點
    res_table = np.full((N, N), "·", dtype=object)
    
    # 根據解法矩陣填入目標
    for r in range(N):
        for c in range(N):
            if solution[r, c] == 1:
                res_table[r, c] = "🎯"
    
    st.table(res_table)

# 重置按鈕
if st.button("清空所有輸入"):
    st.session_state.input_board = np.zeros((N, N), dtype=int)
    st.rerun()
