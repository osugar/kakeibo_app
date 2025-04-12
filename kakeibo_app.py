import streamlit as st
import pandas as pd
import os

# --- 設定 ---
FILE_PATH = "kakeibo.csv"
USER_FILE = "users.csv"
COLUMNS = ["日付", "カテゴリ", "品目", "金額", "区分"]

# --- データ読み込み ---
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH, encoding="cp932")
    return pd.DataFrame(columns=COLUMNS)

# --- データ保存 ---
def save_data(df):
    df.to_csv(FILE_PATH, index=False, encoding="cp932")

# --- ユーザー読み込み ---
def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    return pd.DataFrame(columns=["username", "password"])

# --- ユーザー保存 ---
def save_users(users_df):
    users_df.to_csv(USER_FILE, index=False)

# --- ログイン状態を初期化 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- ログインフォーム ---
def login_form():
    st.header("🔐 ログイン or 会員登録")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    users_df = load_users()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("ログイン"):
            if not username or not password:
                st.warning("すべて入力してください")
            elif not users_df[(users_df.username == username) & (users_df.password == password)].empty:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"ようこそ、{username} さん！")
                st.experimental_rerun()
            else:
                st.error("ユーザー名またはパスワードが違います")

    with col2:
        if st.button("会員登録"):
            if username in users_df.username.values:
                st.error("そのユーザー名はすでに使われています")
            else:
                users_df.loc[len(users_df)] = [username, password]
                save_users(users_df)
                st.success("登録成功！ログインできます")

# --- 家計簿アプリ画面 ---
def app_main():
    st.title("📒 家計簿アプリ")
    df = load_data()

    with st.form("entry_form"):
        st.subheader("🔸 入力")
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("日付")
            category = st.text_input("カテゴリ")
            item = st.text_input("品目")
        with col2:
            amount = st.number_input("金額", 0)
            ttype = st.radio("区分", ["支出", "収入"])
        submitted = st.form_submit_button("保存")

        if submitted:
            new_data = {"日付": date, "カテゴリ": category, "品目": item, "金額": amount, "区分": ttype}
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df)
            st.success("保存しました！")

    st.subheader("📋 データ一覧")
    if df.empty:
        st.info("データがまだありません。")
    else:
        for i, row in df.iterrows():
            st.write(f"{row['日付']} | {row['カテゴリ']} | {row['品目']} | {row['金額']}円 | {row['区分']}")
            if st.button("削除", key=f"del_{i}"):
                df = df.drop(i).reset_index(drop=True)
                save_data(df)
                st.experimental_rerun()

    st.subheader("📊 カテゴリ別合計")
    if not df.empty:
        df["金額"] = pd.to_numeric(df["金額"], errors='coerce')
        summary = df.groupby(["カテゴリ", "区分"])["金額"].sum().reset_index()
        st.dataframe(summary)

# --- 実行 ---
if not st.session_state.logged_in:
    login_form()
else:
    app_main()
