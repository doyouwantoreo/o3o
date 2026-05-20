import streamlit as st
import re

# 페이지 설정 (넓은 화면 레이아웃)
st.set_page_config(page_title="자글자글(za-geul)프리미엄 글자 수 세기 & 맞춤형 검사기", page_icon="📝", layout="wide")

# 상단 타이틀
st.title("📝 BrieFix - 프리미엄 글자 수 세기 & 맞춤형 검사기")
st.subheader("리포트, 자소서, 이력서 작성을 위한 학생의 필수 툴")
st.markdown("---")

# 레이아웃 분할 (왼쪽: 입력창 / 오른쪽: 대시보드 및 결과)
col_input, col_result = st.columns([1, 1])

with col_input:
    st.markdown("### ✍️ 여기에 글을 작성하거나 붙여넣으세요")
    # 사용자 글 입력창
    text = st.text_area(
        "입력창",
        placeholder="여기에 내용을 입력하면 실시간으로 글자 수와 금지어가 분석됩니다...",
        height=400,
        label_visibility="collapsed"
    )

with col_result:
    st.markdown("### 📊 실시간 문서 분석 대시보드")
    
    # 1. 글자 수 계산 로직
    char_count_with_spaces = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    word_count = len(text.split()) if text.strip() else 0
    paragraph_count = len([p for p in text.split('\n') if p.strip()]) if text.strip() else 0

    # 메트릭(Metric) 박스로 예쁘게 화면 배치
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(label="공백 포함 글자 수", value=f"{char_count_with_spaces} 자")
        st.metric(label="총 단어 수", value=f"{word_count} 개")
    with m_col2:
        st.metric(label="공백 제외 글자 수", value=f"{char_count_no_spaces} 자")
        st.metric(label="문단 수", value=f"{paragraph_count} 개")
        
    st.markdown("---")
    st.markdown("### 🚨 과제/자소서 금지어 실시간 필터링")
    
    # 대학생들이 리포트나 자소서에 자주 쓰는 감점 대상 단어 리스트
    forbidden_words = {
        "근데": "구어체 표현입니다. '그러나', '하지만'으로 수정하세요.",
        "암튼": "속어 표현입니다. '어쨌든', '결과적으로'로 수정하세요.",
        "진짜": "주관적인 강조입니다. '매우', '상당히' 등으로 대체하세요.",
        "엄청": "과장된 표현입니다. '대단히', '극히' 등으로 수정하세요.",
        "알바": "공식 문서 표현이 아닙니다. '아르바이트'로 수정하세요.",
        "솔직히": "감정적 표현입니다. 이 단어를 빼고 문장을 담백하게 고치세요.",
        "제가": "자기소개서에서는 '제가'를 반복하기보다 주어를 생략하는 것이 좋습니다."
    }
    
    found_forbidden = []
    if text.strip():
        for word, tip in forbidden_words.items():
            if word in text:
                found_forbidden.append((word, tip))
                
    if not text.strip():
        st.info("💡 글을 입력하면 금지어 및 구어체 필터링 결과가 여기에 표시됩니다.")
    elif len(found_forbidden) == 0:
        st.success("✅ 감점 요인이 될 만한 구어체나 금지어가 발견되지 않았습니다. 훌륭합니다!")
    else:
        st.error(f"⚠️ 주의: 총 {len(found_forbidden)}개의 부적절한 표현이 발견되었습니다.")
        for word, tip in found_forbidden:
            st.markdown(f"- **'{word}'** : {tip}")
