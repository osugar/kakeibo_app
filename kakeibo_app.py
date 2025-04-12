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
        try:
            return pd.read_csv(FILE_PATH, encoding="cp932")
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

# --- データ保存 ---
def save_data(df):
    df.to_csv(FILE_PATH, index=False, encoding="cp932")

# --- ユーザー読み込み ---
def load_users():
    if os.path.exists(USER_FILE):
        try:
            return pd.read_csv(USER_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["username", "password"])
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
                st.rerun()
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

    with st.expander("📋 データ一覧を表示／非表示", expanded=False):
        if df.empty:
            st.info("データがまだありません。")
        else:
            for i, row in df.iterrows():
                st.write(f"{row['日付']} | {row['カテゴリ']} | {row['品目']} | {row['金額']}円 | {row['区分']}")
                if st.button("削除", key=f"del_{i}"):
                    df = df.drop(i).reset_index(drop=True)
                    save_data(df)
                    st.rerun()

    with st.expander("📊 カテゴリ別合計を表示／非表示", expanded=False):
        if not df.empty:
            df["金額"] = pd.to_numeric(df["金額"], errors='coerce')
            summary = df.groupby(["カテゴリ", "区分"])["金額"].sum().reset_index()
            st.dataframe(summary)

    with st.expander("💰 残高を表示／非表示", expanded=False):
        if not df.empty:
            df["金額"] = pd.to_numeric(df["金額"], errors='coerce')
            total_income = df[df["区分"] == "収入"]["金額"].sum()
            total_expense = df[df["区分"] == "支出"]["金額"].sum()
            balance = total_income - total_expense

            st.metric("収入合計", f"{total_income:,.0f} 円")
            st.metric("支出合計", f"{total_expense:,.0f} 円")
            st.metric("残額", f"{balance:,.0f} 円")

    with st.expander("📆 月別残額の推移を表示", expanded=True):
        if not df.empty:
            df["金額"] = pd.to_numeric(df["金額"], errors='coerce')
            df["日付"] = pd.to_datetime(df["日付"], errors='coerce')
            df = df.dropna(subset=["日付"])
            df["年月"] = df["日付"].dt.to_period("M")

            monthly = df.pivot_table(index="年月", columns="区分", values="金額", aggfunc="sum", fill_value=0)
            monthly["残額"] = monthly.get("収入", 0) - monthly.get("支出", 0)
            monthly = monthly.sort_index()

            st.line_chart(monthly["残額"])
            st.dataframe(monthly)

# --- 実行 ---
if not st.session_state.logged_in:
    login_form()
else:
    app_main()
