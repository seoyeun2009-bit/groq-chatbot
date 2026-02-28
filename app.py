import streamlit as st
from groq import Groq

# 1. 페이지 설정 및 배경 디자인
st.set_page_config(page_title="번개 챗봇 AI", page_icon="⚡")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFACD; /* 레몬 쉬폰 배경 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. API 키 보안 로드 및 클라이언트 초기화
try:
    # Streamlit Cloud 배포 시 Secrets에 GROQ_API_KEY를 꼭 넣어주세요.
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Streamlit Secrets에 'GROQ_API_KEY'가 설정되지 않았습니다.")
    st.stop()

# 3. 세션 상태(대화 기록) 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "너는 코딩을 아주 쉽게 알려주는 친절한 선생님 '번개 챗봇 AI'야. "
                "사용자가 이름을 말하면 절대로 변환하지 말고 있는 그대로 기억해줘. "
                "답변은 반드시 DBpia, 외국 논문, 뉴스 기사 등을 위주로 공신력 있게 답변해줘."
            )
        },
        {
            "role": "assistant", 
            "content": "안녕하세요! 저는 ⚡ 번개 챗봇 AI입니다. 당신의 이름은 무엇인가요?"
        }
    ]

# 4. 사이드바 구성
with st.sidebar:
    st.title("⚡ 번개 챗봇 메뉴")
    st.markdown("---")
    st.write("친절한 코딩 선생님, 번개 챗봇과 대화해보세요!")
    
    if st.button("🔄 대화 내용 지우기"):
        st.session_state.messages = [
            st.session_state.messages[0],
            {"role": "assistant", "content": "대화가 초기화되었습니다! 성함이 어떻게 되시나요?"}
        ]
        st.rerun()

# 5. 채팅 기록 화면에 출력
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="⚡" if message["role"] == "assistant" else None):
            st.markdown(message["content"])

# 6. 사용자 입력 및 AI 답변 생성
if prompt := st.chat_input("메시지를 입력하세요..."):
    
    # 사용자 메시지 저장 및 출력
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 답변 생성 프로세스
    with st.chat_message("assistant", avatar="⚡"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Groq API 호출 (llama-3.3-70b-versatile 모델 사용)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
                max_tokens=1024
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            # 최종 답변 확정 및 세션 저장
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")