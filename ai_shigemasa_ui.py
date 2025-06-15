import streamlit as st
import pandas as pd
import datetime as dt

# -------------------------------------------------
# 🎯 MOCK DATA GENERATORS
# -------------------------------------------------
@st.cache_data
def get_mock_master():
    leads = pd.DataFrame({
        "customer_name": ["田中 圭", "鈴木 一恵", "高橋 誠", "伊藤 沙織"],
        "customer_attr": ["32歳 / フリーランス", "45歳 / 主婦", "28歳 / IT系会社員", "55歳 / 飲食自営業"],
        "score": [68, 75, 85, 62],
    })
    reps = pd.DataFrame({
        "rep_name": ["佐藤さん", "加藤さん", "伊藤さん"],
        "specialty": ["若年層・単身者", "主婦・ファミリー", "高価格帯・経営者"]
    })
    conv = [
        {"speaker": "customer", "line": "安全な車が欲しいんです…", "ai": "ニーズヒアリングを深掘りしてください"},
        {"speaker": "agent", "line": "ご安心ください…", "ai": "お客様の反応を観察"},
        {"speaker": "customer", "line": "初期費用は抑えたい…", "ai": "初期費用ゼロプラン提案"},
    ]
    tags = ["#価格に敏感", "#納期重視", "#安全性重視", "#クルマ好き"]
    follow = pd.DataFrame({
        "customer_name": ["渡辺 徹", "山本 裕子"],
        "last_contact": ["15日前", "28日前"],
        "thermo": [70, 30],
        "insight": ["料金ページ閲覧3回、再アプローチ好機", "アクセス途絶、冷却推奨"]
    })
    kb = {
        "類似顧客の成功例は？": "過去15名中8名が成約、頭金10%が有効でした",
        "このお客様の懸念点は？": "初期費用と納期を重視しています"
    }
    return leads, reps, conv, tags, follow, kb

st.set_page_config(page_title="AI重政 DEMO", layout="wide")

leads_df, reps_df, conv_flow, tag_list, follow_df, kb = get_mock_master()

if "lead_idx" not in st.session_state: st.session_state.lead_idx = None
if "step" not in st.session_state: st.session_state.step = 0
if "tags" not in st.session_state: st.session_state.tags = []
if "chat" not in st.session_state: st.session_state.chat = []
if "outcome" not in st.session_state: st.session_state.outcome = None

T1, T2, T3, T4 = st.tabs(["① 新規リスト", "② コックピット", "③ サマリー", "④ フォロー"])

with T1:
    st.header("📋 新規商談リスト（スコア × 担当者マッチング）")
    for idx, row in leads_df.iterrows():
        color = "green" if row.score >= 80 else "yellow" if row.score >= 70 else "red"
        rep = reps_df.iloc[0] if "フリーランス" in row.customer_attr else reps_df.iloc[1] if "主婦" in row.customer_attr else reps_df.iloc[2]
        st.markdown(f"""
        <div style='background:#1e293b;padding:1em;margin:1em 0;border-radius:10px;color:white;'>
            <h4>👤 {row.customer_name} 様</h4>
            <p>🧬 {row.customer_attr}</p>
            <p>🔥 スコア: <span style='color:{'lime' if color=='green' else 'orange' if color=='yellow' else 'red'};'>{row.score}</span></p>
            <p>🤖 推奨担当: <b>{rep.rep_name}</b>（{rep.specialty}）</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"この商談を開始 ▶", key=f"start_{idx}"):
            st.session_state.lead_idx = idx
            st.session_state.step = 0
            st.session_state.tags = []
            st.session_state.chat = []
            st.session_state.outcome = None
            st.success("✅ タブ②『コックピット』に移動して商談を進めてください！")
            st.toast("👀 タブ②でAI重政が待っています")

with T2:
    st.header("📞 商談コックピット")
    if st.session_state.lead_idx is None:
        st.info("タブ①で商談を開始してください")
    else:
        lead = leads_df.iloc[st.session_state.lead_idx]
        st.subheader(f"お客様: {lead.customer_name} / スコア {lead.score}")

        log_container = st.container(height=250, border=True)
        for i in range(st.session_state.step):
            who = "👤 お客様:" if conv_flow[i]["speaker"] == "customer" else "💼 担当者:"
            log_container.markdown(f"{who} {conv_flow[i]['line']}")

        suggest = conv_flow[st.session_state.step]["ai"] if st.session_state.step < len(conv_flow) else "商談終了！成果を入力してください"
        st.success(suggest)

        c1, c2, c3 = st.columns(3)
        c1.button("▶ 次へ", on_click=lambda: st.session_state.__setitem__('step', st.session_state.step+1), disabled=st.session_state.step>=len(conv_flow))
        if st.session_state.step >= len(conv_flow):
            c2.button("✅ 成約", on_click=lambda: st.session_state.__setitem__('outcome', '成約'))
            c3.button("❌ 見送り", on_click=lambda: st.session_state.__setitem__('outcome', '見送り'))

        st.divider()
        tag = st.selectbox("感じた手触りタグを記録", tag_list)
        if st.button("タグを追加"):
            st.session_state.tags.append(tag)
        if st.session_state.tags:
            st.write("記録タグ:", ", ".join(st.session_state.tags))

        st.divider()
        chat_area = st.container(height=200, border=True)
        for m in st.session_state.chat:
            chat_area.markdown(m)
        if q := st.text_input("AI重政に質問 ⇩", placeholder="類似顧客の成功例は？"):
            st.session_state.chat.append(f"🧑‍💼 あなた: {q}")
            ans = kb.get(q, "すみません、まだ回答データがありません")
            st.session_state.chat.append(f"🤖 AI重政: {ans}")
            st.experimental_rerun()

with T3:
    st.header("📝 商談サマリー")
    if st.session_state.outcome is None:
        st.info("商談終了後に結果が表示されます")
    else:
        lead = leads_df.iloc[st.session_state.lead_idx]
        st.subheader(f"結果: {st.session_state.outcome}")
        st.write("**顧客:**", lead.customer_name)
        st.write("**タグ:**", ", ".join(st.session_state.tags) if st.session_state.tags else "なし")
        with st.expander("💬 会話ログ"):
            st.write(conv_flow)
        with st.expander("🤖 AIチャット履歴"):
            st.write(st.session_state.chat)
        st.success("このデータは夜間バッチでAI学習DBに反映され、明日以降のスコア精度が向上します！")

with T4:
    st.header("🔥 フォローアップ顧客 温度計")
    for _, r in follow_df.iterrows():
        color = "green" if r.thermo > 60 else "orange" if r.thermo > 40 else "red"
        st.markdown(f"""
        <div style='background:#1e293b;padding:1em;margin:1em 0;border-radius:10px;color:white;'>
            <h4>👤 {r.customer_name}</h4>
            <p>最終接触: {r.last_contact}</p>
            <p>🔥 温度: <span style='color:{color};'>{r.thermo}</span></p>
            <p>{r.insight}</p>
            <button style='background:#3b82f6;color:white;border:none;padding:0.5em 1em;border-radius:6px;'>今すぐリマインド📞</button>
        </div>
        """, unsafe_allow_html=True)
