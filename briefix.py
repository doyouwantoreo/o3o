import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re

# 페이지 기본 설정
st.set_page_config(
    page_title="BrieFix - 유튜브 요약기",
    page_icon="📺",
    layout="centered"
)

# 웹사이트 타이틀 (정하신 이름 적용)
st.title("🎬 BrieFix (브리픽스)")
st.markdown("유튜브 강의나 영상 링크를 넣으면 자막을 추출해 핵심 요약과 대본을 만들어 드립니다.")
st.markdown("---")

# 1. 유튜브 링크 입력 영역
st.subheader("1. 유튜브 영상 링크 입력")
video_url = st.text_input(
    "유튜브 URL 주소를 입력하세요.",
    placeholder="https://www.youtube.com/watch?v=..."
)

# 2. 변환 옵션 설정
st.subheader("2. 변환 옵션 설정")
summary_count = st.slider("핵심 요약 줄 수 선택", min_value=1, max_value=5, value=3)
line_spacing = st.selectbox("대본 줄바꿈 간격 설정", ["1줄 공백", "2줄 공백", "줄바꿈만"])

# 유튜브 URL에서 영상 ID(Video ID)를 추출하는 함수
def extract_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

# 3. 변환 실행 버튼 및 로직
if st.button("✨ 실시간 자막 추출 및 요약", type="primary"):
    if not video_url.strip():
        st.warning("유튜브 링크를 입력해 주세요!")
    else:
        video_id = extract_video_id(video_url)
        
        if not video_id:
            st.error("올바른 유튜브 링크 형식이 아닙니다. URL을 다시 확인해 주세요.")
        else:
            with st.spinner("유튜브 영상에서 자막을 추출하고 요약하는 중입니다..."):
                try:
                    # 유튜브 자막 추출 (한국어 자막 우선, 없으면 영어)
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                    
                    # 추출된 자막 텍스트를 하나의 문자열로 합치기
                    full_text = " ".join([t['text'] for t in transcript_list])
                    
                    # 문장 단위 분리 및 정제
                    sentences = [s.strip() for s in full_text.replace('\n', ' ').split(' ') if s.strip()]
                    
                    # 간단한 문장 그룹화 (자막은 단어 단위로 쪼개져 있어서 가독성을 위해 묶음)
                    grouped_sentences = []
                    chunk_size = 15  # 15단어씩 한 문장으로 묶기
                    for i in range(0, len(sentences), chunk_size):
                        grouped_sentences.append(" ".join(sentences[i:i+chunk_size]))
                    
                    total_chunks = len(grouped_sentences)
                    
                    # 규칙 기반 요약 로직
                    step = max(1, total_chunks // summary_count)
                    summarized_sentences = [grouped_sentences[i] for i in range(0, min(total_chunks, step * summary_count), step)]
                    summarized_sentences = summarized_sentences[:summary_count]
                    
                    st.markdown("---")
                    
                    # 결과 화면 레이아웃 (좌우 2단 분할)
                    col1, col2 = st.columns(2)
                    
                    # 왼쪽: 요약 결과 출력
                    with col1:
                        st.success(f"📌 강의 핵심 {summary_count}줄 요약")
                        summary_result = ""
                        for i, sentence in enumerate(summarized_sentences, 1):
                            summary_result += f"{i}. {sentence}...\n\n"
                        st.text_area("요약 결과 박스", value=summary_result, height=300, label_visibility="collapsed")
                        
                    # 오른쪽: 전체 대본 결과 출력
                    with col2:
                        st.info("🗣️ 전체 자막 대본 변환")
                        if line_spacing == "1줄 공백":
                            script_result = "\n\n".join(grouped_sentences)
                        elif line_spacing == "2줄 공백":
                            script_result = "\n\n\n".join(grouped_sentences)
                        else:
                            script_result = "\n".join(grouped_sentences)
                        st.text_area("대본 결과 박스", value=script_result, height=300, label_visibility="collapsed")
                        
                    st.balloons()
                    
                except Exception as e:
                    st.error("자막을 가져오지 못했습니다. 영상에 자막(자동 생성 포함)이 활성화되어 있는지 확인해 주세요.")
