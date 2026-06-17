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

# =========================
# 금지어 DB
# =========================

WORD_DB = {
    "근데": ("🔴 위험", "그러나, 하지만 사용"),
    "암튼": ("🔴 위험", "어쨌든 사용"),
    "겁나": ("🔴 위험", "비속어 제거"),
    "ㅋㅋ": ("🔴 위험", "삭제"),
    "ㅎㅎ": ("🔴 위험", "삭제"),
    "ㄹㅇ": ("🔴 위험", "삭제"),

    "진짜": ("🟡 주의", "매우, 상당히 사용"),
    "엄청": ("🟡 주의", "상당히 사용"),
    "완전": ("🟡 주의", "과장 표현 수정"),
    "되게": ("🟡 주의", "공식 표현 사용"),
    "솔직히": ("🟡 주의", "삭제 권장"),
    "아마": ("🟡 주의", "추측 표현"),
    "같다": ("🟡 주의", "근거 제시"),
    "느꼈다": ("🟡 주의", "이유 추가"),

    "열심히": ("🔵 개선", "행동 사례 제시"),
    "최선을 다해": ("🔵 개선", "구체적 행동 작성"),
    "성실한": ("🔵 개선", "사례로 증명"),
    "책임감": ("🔵 개선", "행동으로 설명"),
    "도전": ("🔵 개선", "구체화"),
    "성장": ("🔵 개선", "변화 과정 작성"),
    "발전": ("🔵 개선", "결과 제시"),
    "많은": ("🔵 개선", "수치 사용"),
    "다양한": ("🔵 개선", "구체화"),
    "제가": ("🔵 개선", "반복 사용 줄이기"),
    "저는": ("🔵 개선", "반복 사용 줄이기"),
}

# =========================
# 함수
# =========================

def analyze_text(text):
    results = []

    for word, (level, guide) in WORD_DB.items():
        count = text.count(word)

        if count > 0:
            results.append({
                "등급": level,
                "표현": word,
                "횟수": count,
                "수정 가이드": guide
            })

    return results


def highlight_text(text):

    words = sorted(
        WORD_DB.keys(),
        key=len,
        reverse=True
    )

    pattern = "|".join(
        map(re.escape, words)
    )

    def replace(match):
        return f":red[{match.group(0)}]"

    return re.sub(
        pattern,
        replace,
        text
    )


# =========================
# 헤더
# =========================

st.title("📝 글맞")
st.caption("글자 수 분석 + 자소서/과제 문장 검사기")

st.divider()

# =========================
# 입력창
# =========================

text = st.text_area(
    "내용 입력",
    height=350,
    placeholder="내용을 입력하세요..."
)

# =========================
# 통계
# =========================

char_with_space = len(text)
char_without_space = len(re.sub(r"\s", "", text))
word_count = len(text.split()) if text.strip() else 0
paragraph_count = len(
    [x for x in text.splitlines() if x.strip()]
)

st.subheader("📊 문서 통계")

c1, c2, c3, c4 = st.columns(4)

c1.metric("공백 포함", f"{char_with_space:,}")
c2.metric("공백 제외", f"{char_without_space:,}")
c3.metric("어절 수", f"{word_count:,}")
c4.metric("문단 수", f"{paragraph_count:,}")

# =========================
# 목표 글자 수
# =========================

target = st.number_input(
    "목표 글자 수",
    min_value=100,
    value=1000,
    step=100
)

progress = min(
    char_with_space / target,
    1.0
)

st.progress(progress)

st.caption(
    f"{char_with_space:,} / {target:,}자 "
    f"({progress*100:.1f}%)"
)

st.divider()

# =========================
# 분석
# =========================

st.subheader("🚨 문장 분석")

if not text.strip():

    st.info(
        "텍스트를 입력하면 분석 결과가 표시됩니다."
    )

else:

    results = analyze_text(text)

    if not results:

        st.success(
            "✅ 감점 요소가 발견되지 않았습니다."
        )

    else:

        danger = sum(
            1 for r in results
            if r["등급"] == "🔴 위험"
        )

        warning = sum(
            1 for r in results
            if r["등급"] == "🟡 주의"
        )

        improve = sum(
            1 for r in results
            if r["등급"] == "🔵 개선"
        )

        st.warning(
            f"위험 {danger}개 | "
            f"주의 {warning}개 | "
            f"개선 {improve}개"
        )

        st.markdown("### 🔍 문제 표현")

        st.markdown(
            highlight_text(text)
        )

        st.markdown("### 📋 수정 가이드")

        df = pd.DataFrame(results)

        priority = {
            "🔴 위험": 0,
            "🟡 주의": 1,
            "🔵 개선": 2
        }

        df["정렬"] = df["등급"].map(priority)

        df = (
            df.sort_values("정렬")
              .drop(columns=["정렬"])
        )

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
    "📥 원문 다운로드",
    data=text,
    file_name="글맞_분석결과.txt",
    mime="text/plain"
)
