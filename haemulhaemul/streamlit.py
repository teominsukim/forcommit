import streamlit as st
import requests

# st.chat_message : 모델 답은 ai로, 사용자 답은 user로 이모지 표현
# 추가할 것: streamlit의 prompt를 전달하고, 주피터 노트북의 response를 가져옴

# 로고 주소, http로 불러와야 함
logo_name = "resources/logo/logo_name.png"
logo_wide = "resources/logo/logo_wide.png"
logo = "resources/logo/logo.png"
logo_white = "resources/logo/logo_white.png"

def page():
    # 페이지 제목, 가장 먼저 실행되어야함(중요)
    st.set_page_config(
        page_title="해물해물 - 해상물류 법률 챗봇",
        page_icon=logo_white
    )

    # 제목 설정
    st.header("해물해물 - 해상물류 법률 챗봇", anchor=False, divider="blue")

    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    

    # 로고 설정
    st.logo(
        logo_name, # 로고 이미지
        link="http://localhost:8502", # 링크 url
        icon_image=None # 대체 이미지
    )   

# 첫 채팅시 매크로 문구
def hello():
    with st.chat_message("ai", avatar=logo):
            st.write('''안녕하세요! 👋
                     저는 해상물류 법률을 잘 아는 챗봇 해물해물이에요!
                     궁금한 점이 있다면 무엇이든 물어보세요!
                     ''')

# 챗봇의 응답을 출력합니다
def printAi(response):
    with st.chat_message("ai", avatar=logo):
        st.write(response)
        st.session_state.chat_history.append({"role": "ai", "message": response})

# 사용자의 응답을 출력합니다
def printUser(userInput):
    with st.chat_message("user"):
        st.write(userInput)
        st.session_state.chat_history.append({"role": "user", "message": userInput})

def main():
    page()
    hello()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for content in st.session_state.chat_history:
        with st.chat_message(content["role"]):
            st.markdown(content['message'])    

    if prompt := st.chat_input("메시지를 입력하세요."):
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.chat_history.append({"role": "user", "message": prompt})

        # HTTP POST 요청으로 챗봇 flask 서버에 메세지를 요청함
        response = requests.post('http://localhost:5000/chatbot', json={'message': prompt})

        if response.status_code == 200:
            # HTTP 응답에서 JSON 데이터를 추출
            response_json = response.json()
            ai_message = response_json.get('response', '응답을 받을 수 없습니다.')
            with st.chat_message("ai"):                
                st.markdown(ai_message)
                st.session_state.chat_history.append({"role": "ai", "message": ai_message})
        else:
            st.markdown("오류가 발생했습니다. 다시 시도해 주세요.")



# main 함수 실행
if __name__ == '__main__':
    main()

