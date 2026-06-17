import streamlit as st
import re

# 페이지 설정
st.set_page_config(page_title="글맞 | 글자 수 세기 & 문장 교정", page_icon="📝", layout="centered")

st.title("📝 글맞")
st.caption("리포트, 자소서, 이력서 작성을 위한 실시간 글자 수 세기 & 문장 필터링 툴")
st.markdown("---")

# 메인 입력창
text = st.text_area(
    "여기에 내용을 입력하거나 붙여넣으세요.",
    placeholder="내용을 입력하면 하단 대시보드에 실시간으로 반영됩니다...",
    height=320,
    label_visibility="visible"
)

st.markdown("---")

# 글자 수 계산 (공백 문자 정밀 정제)
char_with_spaces = len(text)
char_no_spaces = len(re.sub(r'\s', '', text))
word_count = len(text.split()) if text.strip() else 0
paragraph_count = len([p for p in text.split('\n') if p.strip()]) if text.strip() else 0

# 실시간 분석 결과 대시보드
st.subheader("📊 실시간 분석 결과")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="공백 포함", value=f"{char_with_spaces:,} 자")
with col2:
    st.metric(label="공백 제외", value=f"{char_no_spaces:,} 자")
with col3:
    st.metric(label="단어 수", value=f"{word_count:,} 개")
with col4:
    st.metric(label="문단 수", value=f"{paragraph_count:,} 개")

st.markdown("---")

st.subheader("🚨 맞춤형 문장 필터링")

# 금지어 및 가이드 데이터셋
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
        # [핵심 수정] 정규식을 사용하여 독립된 단어이거나, 뒤에 조사(가, 는, 를, 에, 도 등)가 붙은 경우만 정확하게 타겟팅
        # 단어의 앞뒤가 다른 글자 속에 파묻혀 있는 경우(예: 사진작가)는 제외합니다.
        pattern = rf"\b{word}(?:이|가|은|는|을|를|에|와|과|도|로|으로)?\b"
        
        # 문장 내에서 해당 패턴을 찾아냄
        matches = re.findall(pattern, text)
        if matches:
            # 중복 제거를 위해 매칭된 실제 단어 형태와 팁을 저장
            found_forbidden.append((word, tip, len(matches)))

# 결과 출력 UI
if not text.strip():
    st.info("텍스트를 입력하면 분석 결과와 수정 제안이 여기에 표시됩니다.")
elif len(found_forbidden) == 0:
    st.success("✅ 감점 요인이 될 만한 구어체나 금지어가 없습니다. 완벽합니다!")
else:
    st.warning(f"문맥에 어울리지 않는 표현이 총 {sum(m[2] for m in found_forbidden)}회 발견되었습니다.")
    
    # 테이블 형식으로 깔끔하게 리스팅
    st.markdown("| 발견된 단어 | 발생 횟수 | 수정 가이드 |")
    st.markdown("| :--- | :--- | :--- |")
    for word, tip, count in found_forbidden:
        st.markdown(f"| **{word}** | {count}회 | {tip} |"))
