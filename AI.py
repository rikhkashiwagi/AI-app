#対話アプリの作成

import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Geminiチャットボット")

if "model_name" not in st.session_state:#初回のみ初期化(アプリを開いたときのみ)、以降は保存された値
    st.session_state.model_name = "gemini-1.5-flash"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.0

st.sidebar.title("options")
st.session_state.model_name = st.sidebar.radio("choose a model", ("gemini-1.5-flash", "gemini-1.5-pro"))
st.session_state.temperature = st.sidebar.slider("Tempreture", min_value=0.0, max_value=2.0, value=st.session_state.temperature, step=0.1) #モデルに渡す創造性を調整するスライダー(0.0だと堅い答え、2.0だと創造的な答え)
clear_button = st.sidebar.button("Clear Conversation", key="clear") #st.session_state.chatbotなどの履歴を初期化することができる

def init_messages():#messages:geminiに何を渡して、どう応答させるかの履歴,chatbot:Streamlitのチャット画面に何を表示するかの履歴
    if clear_button:
        st.session_state.messages = [
            {"role": "system", "parts": [{"text": " You are a helphul assistant"}]}#役割設定を持たせる
        ]
        st.session_state.chatbot = []
    elif "messages" not in st.session_state:
        st.session_state.messages =[
            {"role": "system", "parts": [{"text": " You are a helphul assistant"}]}
        ]
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = []

#APIキーの設定
try:
    api_key = st.secrets["google_api_key"]
except(FileNotFoundError, KeyError):
    st.error("APIキーがsecrets.tolmに設定されていません")
    st.stop()

try:
    genai.configure(api_key=api_key)
except  Exception as e:
    st.error(f"APIキーの設定中にエラーが発生しました:{e}")
    st.stop()

#チャットの表示・入力・応答生成
def main():
    model_name = st.session_state.model_name
    temperature = st.session_state.temperature
    st.title(f"Gemini {model_name}とチャット")
    st.caption("APIキーはst.secretsで管理すること")
    
    init_messages()
    #過去チャット履歴の表示
    for msg in st.session_state.chatbot:
        role = msg.get("role")
        text = msg.get("text")
    
        if role and text:
            display_role = "assistant" if role == "model" else role #API→画面表示　APIで使われた"model"人間が読める"assistant"に直して表示する(user(自分の発言),modelはAIの発言)
            with st.chat_message(display_role):
                st.markdown(text)

    #ユーザーからチャットを受け取る
    user_input = st.chat_input("気になることを聞いてみよう")

    if user_input:
        st.session_state.chatbot.append({"role":"user", "text": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
    
        #gemini APIに渡す準備
        chatboted = []
        for msg in st.session_state.chatbot:
            role = msg.get("role")
            text = msg.get("text")

            if role and text:
                api_role = "model" if role == "assistant" else role #画面表示→API　ユーザの履歴内の"assistant"をAPIが期待する"model"に変換する
                chatboted.append({"role":api_role,"parts":[{"text":text}]})
        
        try:
            if chatboted:
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(chatboted,stream = False)


                bot_text = ""
                if hasattr(response, "parts") and response.parts: #responseにpartsという属性があるか？、かつそのpartsが空でないか?の両方をチェックしている
                    bot_text = response.parts[0].text #AIの生成したメッセージ
                elif hasattr(response, "text"):
                    bot_text = response.text
                else:
                    bot_text = "うまく処理できません"
                    print(f"予期しない応答構造: {response}") 
                st.session_state.chatbot.append({"role":"model", "text": bot_text})
                st.rerun() #アプリが即座に再実行される(表示の更新)

            else:
                st.warning("送信する履歴がありません")
        
        except Exception as e:
            st.error(f"AIの応答生成中にエラーが発生した:{e}")
            import traceback
            traceback.print_exc()
               
if __name__ == "__main__":
    main()


