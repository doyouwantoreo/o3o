import streamlit as st
import pandas as pd
import re

# =========================
# 페이지 설정
# =========================
st.set_page_config(
    page_title="글맞",
    page_icon="📝",
    layout="centered"
)

st.title("📝 글맞")
st.caption("자소서 · 과제 · 보고서 문장 분석기")

st.divider()

# =========================
# 입력
# =========================
text = st.text_area("내용 입력", height=350)

# =========================
# DB 구조 (안정형)
# =========================

WORD_DB = {
    # 위험 (구어체/비문서)
    "근데": ("🔴 위험", "그러나/하지만"),
    "암튼": ("🔴 위험", "어쨌든"),
    "겁나": ("🔴 위험", "삭제"),
    "ㅋㅋ": ("🔴 위험", "삭제"),
    "ㅎㅎ": ("🔴 위험", "삭제"),

    # 주의 (표현 문제)
    "진짜": ("🟡 주의", "매우/상당히"),
    "엄청": ("🟡 주의", "상당히"),
    "완전": ("🟡 주의", "과장 표현"),
    "되게": ("🟡 주의", "공식 표현"),
    "솔직히": ("🟡 주의", "삭제 권장"),
    "아마": ("🟡 주의", "추측 표현"),
    "같다": ("🟡 주의", "근거 필요"),

    # 추상어 (자소서 핵심 문제)
    "열심히": ("💡 추상어", "행동으로 설명"),
    "성장": ("💡 추상어", "과정/수치"),
    "도전": ("💡 추상어", "구체화"),
    "책임감": ("💡 추상어", "사례 필요"),
    "많은": ("💡 추상어", "수치화"),
    "다양한": ("💡 추상어", "구체화"),

    # 반복어 (자기소개서 특화)
    "제가": ("🔁 반복", "반복 줄이기"),
    "저는": ("🔁 반복", "반복 줄이기"),
}

# =========================
# 분석 함수
# =========================

def analyze(text):
    results = []

    for word, (level, tip) in WORD_DB.items():
        count = text.count(word)

        if count > 0:
            results.append({
                "등급": level,
                "표현": word,
                "횟수": count,
                "수정 가이드": tip
            })

    return results


# =========================
# 하이라이트 함수 (안전형)
# =========================

def highlight(text):

    if not text:
        return ""

    words = sorted(WORD_DB.keys(), key=len, reverse=True)
    pattern = "|".join(map(re.escape, words))

    def repl(m):
        return f":red[{m.group(0)}]"

    return re.sub(pattern, repl, text)


# =========================
# 통계
# =========================

char_with = len(text)
char_no = len(re.sub(r"\s", "", text))
word_count = len(text.split()) if text.strip() else 0
para_count = len([x for x in text.splitlines() if x.strip()])

st.subheader("📊 문서 통계")

c1, c2, c3, c4 = st.columns(4)

c1.metric("공백 포함", f"{char_with:,}")
c2.metric("공백 제외", f"{char_no:,}")
c3.metric("어절 수", f"{word_count:,}")
c4.metric("문단 수", f"{para_count:,}")

# =========================
# 목표 글자수
# =========================

target = st.number_input("목표 글자 수", 100, 5000, 1000)

progress = min(char_with / target, 1.0)

st.progress(progress)
st.caption(f"{char_with:,}/{target:,}자 ({progress*100:.1f}%)")

st.divider()

# =========================
# 분석 실행
# =========================

st.subheader("🚨 분석 결과")

if not text.strip():
    st.info("텍스트를 입력하세요")

else:

    results = analyze(text)

    if not results:
        st.success("문제 표현 없음")

    else:

        # 등급 집계
        levels = [r["등급"] for r in results]

        st.warning(
            f"🔴 위험 {levels.count('🔴 위험')} | "
            f"🟡 주의 {levels.count('🟡 주의')} | "
            f"💡 추상어 {levels.count('💡 추상어')} | "
            f"🔁 반복 {levels.count('🔁 반복')}"
        )

        st.markdown("### 🔍 수정 위치")
        st.markdown(highlight(text))

        st.markdown("### 📋 수정 가이드")

        df = pd.DataFrame(results)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

# =========================
# 다운로드
# =========================

st.divider()

st.download_button(
    "📥 결과 다운로드",
    text,
    file_name="글맞_결과.txt"
)
