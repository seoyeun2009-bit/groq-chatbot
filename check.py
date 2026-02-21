import streamlit as st
import os

st.set_page_config(page_title="긴급 진단")

st.title("🛠️ 시스템 환경 진단")

# 1. 파일 시스템 체크
st.subheader("1. 파일 경로 체크")
current_dir = os.getcwd()
st.write(f"현재 실행 위치: `{current_dir}`")

dot_streamlit_exists = os.path.exists(".streamlit")
st.write(f".streamlit 폴더 존재 여부: {'✅ 있음' if dot_streamlit_exists else '❌ 없음 (폴더를 만드세요)'}")

# 2. Secrets 체크
st.subheader("2. Secrets 체크")
try:
    if "GROQ_API_KEY" in st.secrets:
        st.success("✅ secrets.toml 로드 성공!")
        st.code(f"키 시작 부분: {st.secrets['GROQ_API_KEY'][:7]}...")
    else:
        st.error("❌ secrets.toml 파일은 있으나 내부 내용이 비어있거나 'GROQ_API_KEY' 오타가 있습니다.")
except Exception as e:
    st.error(f"❌ 설정 로드 중 치명적 오류: {e}")
    st.info(".streamlit 폴더 안에 secrets.toml 파일이 있는지 다시 확인하세요.")