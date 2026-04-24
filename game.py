import streamlit as st
import numpy as np

# --- 頁面配置 ---
st.set_page_config(page_title="Lights Out 點燈挑戰", layout="centered")

# --- 核心邏輯 ---
def toggle(r, c, board, N):
    """標準點燈規則：切換自己與上下左右"""
    for dr, dc in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < N and 0 <= nc < N:
            board[nr, nc] = 1 - board[nr, nc]

def generate_solvable_board(N, shuffle_steps=15):
    """從全滅狀態開始隨機點擊，保證盤面必有解"""
    board = np.zeros((N, N), dtype=int)
    # 隨機挑選位置按下，步數越多盤面越亂
    indices = np.random.choice(N * N, size=shuffle_steps, replace=True)
    for idx in indices:
        toggle(idx // N, idx % N, board, N)
    # 如果隨機完剛好全滅，遞迴再跑一次
    if np.sum(board) == 0:
        return generate_solvable_board(N, shuffle_steps)
    return board

# --- 遊戲狀態初始化 ---
if 'N' not in st.session_state:
    st.session_state.N = 5
if 'board' not in st.session_state:
    st.session_state.board = generate_solvable_board(5)
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("遊戲控制")
    new_n = st.slider("選擇盤面大小", 3, 7, st.session_state.N)
    difficulty = st.select_slider("難度", options=[10, 20, 30, 50], value=20)
    
    if st.button("刷新設置") or new_n != st.session_state.N:
        st.session_state.N = new_n
        st.session_state.board = generate_solvable_board(new_n, difficulty)
        st.session_state.count = 0
        st.rerun()

# --- 主畫面 UI ---
st.title("Lights Out 點燈遊戲")
st.markdown(f"**目標：** 讓所有燈火熄滅。當前挑戰：**{st.session_state.N} x {st.session_state.N}**")

# 美化按鈕樣式
st.markdown("""
    <style>
    .stButton > button {
        height: 60px;
        width: 100%;
        font-size: 25px;
        border-radius: 10px;
        transition: 0.3s;
    }
    /* 亮燈狀態：黃色背景 */
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background-color: #FFD700 !important;
        color: black !important;
        box-shadow: 0 0 15px #FFD700;
    }
    /* 熄滅狀態：深色背景 */
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background-color: #333333 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 渲染遊戲盤面
N = st.session_state.N
grid = st.container()
with grid:
    for r in range(N):
        cols = st.columns(N)
        for c in range(N):
            is_on = st.session_state.board[r, c] == 1
            # 使用 Streamlit 的 type 來區分視覺效果 (primary = 亮, secondary = 暗)
            btn_type = "primary" if is_on else "secondary"
            btn_label = "💡" if is_on else "⚫"
            
            if cols[c].button(btn_label, key=f"cell_{r}_{c}", type=btn_type):
                toggle(r, c, st.session_state.board, N)
                st.session_state.count += 1
                st.rerun()

st.divider()

# --- 結算區 ---
if np.sum(st.session_state.board) == 0:
    st.balloons()
    st.success(f"恭喜！你用了 {st.session_state.count} 步解決了這個難題。")
    if st.button("挑戰下一局"):
        st.session_state.board = generate_solvable_board(N, difficulty)
        st.session_state.count = 0
        st.rerun()
else:
    st.write(f"當前步數：**{st.session_state.count}**")
    st.caption("小提醒：點擊一個格子會切換它自己以及上下左右鄰居的開關燈狀態。")