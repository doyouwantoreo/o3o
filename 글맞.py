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
# 금지어 DB
# =========================
WORD_DB = {
    "근데": ("🔴 위험", "그러나/하지만"),
    "암튼": ("🔴 위험", "어쨌든"),
    "겁나": ("🔴 위험", "삭제"),
    "ㅋㅋ": ("🔴 위험", "삭제"),

    "진짜": ("🟡 주의", "매우/상당히"),
    "엄청": ("🟡 주의", "상당히"),
    "완전": ("🟡 주의", "과장 표현"),
    "되게": ("🟡 주의", "공식 표현"),

    "열심히": ("💡 추상어", "행동으로 설명"),
    "성장": ("💡 추상어", "구체적 과정"),
    "도전": ("💡 추상어", "사례 필요"),
    "책임감": ("💡 추상어", "행동으로 설명"),

    "많은": ("💡 추상어", "수치화"),
    "다양한": ("💡 추상어", "구체화"),

    "제가": ("🔁 반복", "반복 줄이기"),
    "저는": ("🔁 반복", "반복 줄이기"),
}

# =========================
# 안전 매칭 함수
# =========================
def count_word(text, word):
    pattern = re.escape(word)
    return len(re.findall(pattern, text))


def highlight_text(text):
    if not text:
        return ""

    words = sorted(WORD_DB.keys(), key=len, reverse=True)
    pattern = "|".join(map(re.escape, words))

    return re.sub(pattern, lambda m: f":red[{m.group(0)}]", text)

# =========================
# 통계
# =========================
char_with = len(text)
char_no = len(re.sub(r"\s", "", text))
word_count = len(text.split()) if text.strip() else 0
para_count = len([x for x in text.splitlines() if x.strip()])

st.subheader("📊 통계")

c1, c2, c3, c4 = st.columns(4)
c1.metric("공백 포함", f"{char_with:,}")
c2.metric("공백 제외", f"{char_no:,}")
c3.metric("어절 수", f"{word_count:,}")
c4.metric("문단 수", f"{para_count:,}")

# =========================
# 분석
# =========================
st.subheader("🚨 분석 결과")

if not text.strip():
    st.info("텍스트를 입력하세요")

else:
    results = []

    for word, (level, tip) in WORD_DB.items():
        count = count_word(text, word)

        if count > 0:
            results.append({
                "등급": level,
                "표현": word,
                "횟수": count,
                "수정": tip
            })

    if not results:
        st.success("문제 표현 없음")

    else:
        st.warning(f"문제 표현 {len(results)}개 발견")

        st.markdown("### 🔍 위치")
        st.markdown(highlight_text(text))

        st.markdown("### 📋 수정 가이드")

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# 다운로드
# =========================
st.divider()

st.download_button(
    "📥 다운로드",
    data=text,
    file_name="글맞.txt"
)
