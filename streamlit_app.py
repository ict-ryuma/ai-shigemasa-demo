import streamlit as st
import pandas as pd
import time
import random

# --- Streamlit Appの基本設定 ---
st.set_page_config(layout="wide", page_title="AI重政 最終デモ")

# --- このプロトタイプのための、仮の「マスタデータ」 ---
@st.cache_data
def get_mock_master_data():
    # ① 新規商談リスト
    leads = pd.DataFrame({
        "customer_name": ["田中 圭様", "鈴木 一恵様", "高橋 誠様", "伊藤 沙織様"],
        "customer_attributes": ["32歳/フリーランス", "45歳/主婦", "28歳/会社員(IT)", "55歳/自営業(飲食)"],
        "customer_score": [68, 75, 85, 62],
    })
    # 担当者リスト
    sales_reps = pd.DataFrame({
        "rep_name": ["佐藤さん", "加藤さん", "伊藤さん"],
        "specialty": ["若年層・単身者", "主婦・ファミリー層", "高価格帯・経営者"],
        "base_rate": [0.4, 0.5, 0.45] # 担当者ごとの基本成約率
    })
    # ② 商談コックピット用のデータ
    conversation_flow = [
        {"speaker": "お客様", "line": "子供が生まれたばかりで、安全な車を探しているんです。", "ai_suggestion": "お客様のニーズ（Why）をヒアリング中です..."},
        {"speaker": "お客様", "line": "ただ、フリーランスなので、将来の収入に少し不安があって…。初期費用はかけたくないんですよね。", "ai_suggestion": "【検知: `安全`, `不安`, `初期費用`】\n\nお客様は**安全性**と**初期費用**を気にされています。**共感**を示しつつ、**初期費用ゼロ**のプランを提示して不安を解消してください。"},
        {"speaker": "担当者", "line": "（AIの提案に基づき）お子様のお誕生おめでとうございます！…", "ai_suggestion": "お客様の反応を観察してください..."},
        {"speaker": "お客様", "line": "え、初期費用ゼロ！ぜひお願いします。ちなみに、納車まではどれくらいかかりますか？", "ai_suggestion": "【検知: `初期費用ゼロ`, `嬉しい`, `納期`】\n\n**ポジティブな反応**です！次に**納期（スピード感）**が重要因子になっています。即納可能な車両を提示しましょう。"},
    ]
    tezawari_tags = ["#価格に敏感", "#納期を重視", "#家族のために安全性を求めている", "#クルマに詳しい", "#とにかく乗りたい気持ちが強い"]
    knowledge_base = {
        "類似顧客の成功例は？": "はい。過去の類似フリーランス顧客15名中8名が成約しています。",
        "このお客様の最大の懸念点は？": "分析によると、このお客様の最大の懸念は『初期費用』です。次に『納期の速さ』を重視される傾向があります。"
    }
    # ④ 継続フォローリスト
    following_leads = pd.DataFrame({ "customer_name": ["渡辺 徹様", "山本 裕子様"], "last_contact": ["15日前", "28日前"], "thermometer_after": [70, 30], "ai_insight": ["料金ページを閲覧済。**再アプローチの好機！**", "アクセスが途絶えています。**冷却期間を推奨。**"] })
    return leads, sales_reps, conversation_flow, tezawari_tags, knowledge_base, following_leads

leads_df, reps_df, conversation_flow, tezawari_tags, knowledge_base, following_df = get_mock_master_data()

# --- アプリケーションの描画開始 ---
st.title("🧠 AI重政：商談成約率 最大化システム")

# Session State Management
if 'current_customer' not in st.session_state: st.session_state.current_customer = None
if 'conversation_step' not in st.session_state: st.session_state.conversation_step = 0
if 'tezawari_log' not in st.session_state: st.session_state.tezawari_log = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'final_status' not in st.session_state: st.session_state.final_status = "商談中"
if 'selected_reps' not in st.session_state: st.session_state.selected_reps = {}

# --- 4 Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["**① 新規商談リスト**", "**② 商談コックピット**", "**③ 商談サマリーと学習**", "**④ 継続フォローリスト**"])

# --- Tab 1: AI Matching ---
with tab1:
    st.header("今日の新規商談リスト（AIマッチング）")
    for index, lead in leads_df.iterrows():
        st.divider()
        if "フリーランス" in lead['customer_attributes'] or "会社員" in lead['customer_attributes']: recommended_rep_index = 0
        elif "主婦" in lead['customer_attributes']: recommended_rep_index = 1
        else: recommended_rep_index = 2
        
        if index not in st.session_state.selected_reps:
            st.session_state.selected_reps[index] = reps_df.iloc[recommended_rep_index]['rep_name']
        
        selected_rep_name = st.session_state.selected_reps[index]
        selected_rep = reps_df[reps_df['rep_name'] == selected_rep_name].iloc[0]

        compatibility_score = 1.2 if recommended_rep_index == selected_rep.name else 0.8
        final_conversion_rate = lead['customer_score'] * selected_rep['base_rate'] * compatibility_score / 50 

        col1, col2, col3, col4, col5 = st.columns([2, 0.5, 1.5, 2, 1.5])
        with col1:
            st.subheader(f"👤 {lead['customer_name']}")
            st.write(f"**属性:** {lead['customer_attributes']}")
            st.metric("顧客スコア", f"{lead['customer_score']} 点")
        col2.write("<br><br><div style='font-size: 3rem; text-align: center;'>→</div>", unsafe_allow_html=True)
        with col3:
            st.subheader("予測成約率")
            st.metric("", f"{final_conversion_rate:.1%}")
            st.caption("顧客スコアと担当者相性から算出")
        with col4:
            st.subheader("🤝 担当者")
            if recommended_rep_index == selected_rep.name:
                st.write(f"**AI推奨:** **{selected_rep_name}**")
            else:
                st.write(f"**手動選択:** **{selected_rep_name}**")
            st.info(f"**得意領域:** {selected_rep['specialty']}")
        with col5:
            st.selectbox(
                "担当者を変更", reps_df['rep_name'], index=int(selected_rep.name), key=f"rep_select_{index}",
                on_change=lambda: st.session_state.update(selected_reps={**st.session_state.selected_reps, index: st.session_state[f"rep_select_{index}"]}))
            if st.button(f"この商談を開始", key=f"start_{index}"):
                st.session_state.current_customer = lead
                st.session_state.current_rep = selected_rep
                st.session_state.conversation_step = 0
                st.session_state.tezawari_log = []
                st.session_state.final_status = "商談中"
                st.session_state.chat_history = [{"role": "assistant", "content": f"**{lead['customer_name']}**（担当: {selected_rep_name}）との商談を開始します。"}]
                st.success("タブ②に移動しました。")

# --- Tab 2: Cockpit ---
with tab2:
    st.header("📞 商談コックピット")
    if st.session_state.current_customer is None:
        st.warning("タブ①で「商談を開始」ボタンを押してください。")
    else:
        customer = st.session_state.current_customer
        rep = st.session_state.current_rep
        st.info(f"**{customer['customer_name']}** と **{rep['rep_name']}** の商談をシミュレーションしています。")
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.subheader("リアルタイム商談モニター")
            conversation_log = st.container(height=250, border=True)
            for i in range(st.session_state.conversation_step):
                if conversation_flow[i]['speaker'] == 'お客様': conversation_log.markdown(f"👤 **お客様:** {conversation_flow[i]['line']}")
                else: conversation_log.markdown(f"💼 **担当者:** {conversation_flow[i]['line']}")
            st.write("**🤖 AI重政からのリアルタイム・サジェスト**")
            ai_suggestion_area = st.container(height=150, border=True)
            current_suggestion = conversation_flow[st.session_state.conversation_step]['ai_suggestion'] if st.session_state.conversation_step < len(conversation_flow) else "商談を終了してください。下のボタンから結果を登録できます。"
            ai_suggestion_area.success(current_suggestion)
            
            # 【バグ修正点】ボタンの表示ロジックを、if/elseで明確に分離
            st.divider()
            c1, c2, c3 = st.columns(3)
            if st.session_state.conversation_step < len(conversation_flow):
                # 商談が進行中の場合
                if c1.button("▶ 次の会話へ進める"):
                    st.session_state.conversation_step += 1
                    st.rerun()
            else:
                # 商談が終了した場合
                if c1.button("↩️ リセット"):
                    st.session_state.clear()
                    st.rerun()
                if c2.button("✅ 商談成立", type="primary"):
                    st.session_state.final_status = "成約"
                    st.toast("おめでとうございます！タブ③でサマリーを確認できます。")
                    st.rerun()
                if c3.button("⏹️ 今回は見送り"):
                    st.session_state.final_status = "見送り"
                    st.toast("残念…このデータは次に活かされます。タブ③へどうぞ。")
                    st.rerun()

        with col2:
            st.subheader("「手触り感」学習データ入力")
            selected_tag = st.selectbox("商談中に感じた印象タグを選択", tezawari_tags)
            if st.button("この「手触り感」を記録する"):
                st.session_state.tezawari_log.append(selected_tag)
            st.subheader("AI重政に質問する")
            chat_area = st.container(height=280, border=True)
            for message in st.session_state.chat_history:
                with chat_area.chat_message(message["role"]): st.markdown(message["content"])
            if prompt := st.chat_input("（例：類似顧客の成功例は？）"):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                response = knowledge_base.get(prompt, "申し訳ありません、その質問にはまだお答えできません。")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

# --- Tab 3 & 4 (変更なし) ---
with tab3:
    st.header("📝 商談サマリーと学習データパッケージ")
    if st.session_state.final_status == "商談中" or st.session_state.current_customer is None:
        st.info("タブ②で商談を終了すると、ここにサマリーが表示されます。")
    else:
        st.subheader(f"商談結果： **{st.session_state.final_status}**")
        st.success("以下のデータパッケージが生成され、今晩のAIの学習に活用されます。")

with tab4:
    st.header("🔥 継続フォローリスト（顧客温度計）")
    for index, lead in following_df.iterrows():
        st.divider()
        col1, col2, col3 = st.columns([1.5, 1, 2])
        col1.subheader(f"👤 {lead['customer_name']}")
        col1.write(f"最終接触から: **{lead['last_contact']}**")
        col2.metric("熱意スコア", f"{lead['thermometer_after']} 点")
        if lead['thermometer_after'] > 50: col3.success(f"🤖 **AIインサイト:** {lead['ai_insight']}")
        else: col3.warning(f"🤖 **AIインサイト:** {lead['ai_insight']}")

