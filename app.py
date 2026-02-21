import streamlit as st
from groq import Groq

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="번개 챗봇 AI", page_icon="⚡")

st.markdown(
    """
    <style>
    /* 전체 배경색: 레몬 쉬폰 */
    .stApp {
        background-color: #FFFACD;
    }
    /* 사이드바 스타일 조정: 불필요한 공백 제거 및 파일 업로더 강조 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
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

# 3. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "너는 코딩을 아주 쉽게 알려주는 친절한 선생님 '번개 챗봇 AI'야. "
                "사용자가 이름을 알려주면 반드시 기억하고 대화 중에 언급해줘. "
                "답변은 DBpia, 학술 논문, 뉴스 기사, 전문 서적 등 공신력 있는 자료를 최우선으로 참고해. "
                "사용자가 사진을 업로드하면, 그 사진의 맥락에 맞는 답변을 하도록 노력해줘."
            )
        },
        {
            "role": "assistant", 
            "content": "안녕하세요! 저는 ⚡ 번개 챗봇 AI입니다. 당신의 이름은 무엇인가요?"
        }
    ]

# 4. 사이드바 구성 (파일 업로드 기능이 확실히 보이도록 수정)
with st.sidebar:
    st.title("⚡ 번개 챗봇 메뉴")
    
    st.markdown("---")
    
    # [수정] 파일 업로더가 숨겨지지 않도록 표준 함수 사용
    st.subheader("📸 이미지 첨부")
    uploaded_file = st.file_uploader(
        "사진을 업로드하고 질문해보세요!", 
        type=["jpg", "png", "jpeg"],
        help="질문과 관련된 이미지가 있다면 여기에 올려주세요."
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
    # 이미지 업로드 여부에 따른 맥락 추가
    actual_prompt = prompt
    if uploaded_file is not None:
        actual_prompt = f"[참고: 사용자가 이미지를 업로드한 상태임] {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": m["role"], "content": m["content"] if m["role"] != "user" else actual_prompt}
                    for m in st.session_state.messages
                ],
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