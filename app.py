import streamlit as st
from groq import Groq

# 1. 페이지 설정 및 디자인
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

# 2. API 키 보안 로드
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Streamlit Secrets에 'GROQ_API_KEY'를 설정해주세요.")
    st.stop()

# 3. 세션 상태 초기화 (프롬프트 보강: 이름 오인식 방지)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "너는 코딩을 아주 쉽게 알려주는 친절한 선생님 '번개 챗봇 AI'야. "
                "사용자가 이름을 말하면 절대로 임의로 변환(예: '먀'를 'mxArray'로 변환 등)하지 말고 "
                "있는 그대로의 이름을 기억해서 대화 중에 불러줘. 한 글자나 두 글자 이름도 소중히 기억해줘. "
                "답변은 반드시 DBpia, 외국 논문, 뉴스 기사 등을 위주로 공신력 있게 답변하고, "
                "사이드바에 사진이 업로드되면 해당 사진의 내용을 기반으로 친절하게 설명해줘."
            )
        },
        {
            "role": "assistant", 
            "content": "안녕하세요! 저는 ⚡ 번개 챗봇 AI입니다. 당신의 이름은 무엇인가요?"
        }
    ]

# 4. 사이드바 구성 (파일 업로드)
with st.sidebar:
    st.title("⚡ 번개 챗봇 메뉴")
    st.markdown("---")
    st.subheader("📸 이미지 첨부")
    uploaded_file = st.file_uploader(
        "사진을 업로드하고 질문해보세요!", 
        type=["jpg", "png", "jpeg"]
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="업로드된 이미지", use_container_width=True)
        st.success("✅ 이미지가 준비되었습니다.")

    st.markdown("---")
    if st.button("🔄 대화 내용 지우기"):
        st.session_state.messages = [
            st.session_state.messages[0],
            {"role": "assistant", "content": "대화가 초기화되었습니다! 성함이 어떻게 되시나요?"}
        ]
        st.rerun()

# 5. 채팅 기록 출력
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="⚡" if message["role"] == "assistant" else None):
            st.markdown(message["content"])

# 6. 사용자 입력 및 AI 답변 생성
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 이미지 업로드 맥락 추가
    actual_prompt = prompt
    if uploaded_file is not None:
        actual_prompt = f"[이미지 참고함] {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # AI에게 현재 대화 맥락 전달 (마지막 사용자 입력은 actual_prompt로 대체)
            api_messages = []
            for m in st.session_state.messages[:-1]:
                api_messages.append({"role": m["role"], "content": m["content"]})
            api_messages.append({"role": "user", "content": actual_prompt})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")