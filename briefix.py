import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re

# [설정] 페이지 제목과 아이콘
st.set_page_config(page_title="BrieFix - 유튜브 AI 요약기", page_icon="📝")

# [디자인] 상단 타이틀
st.title("🚀 BrieFix (브리픽스)")
st.subheader("강의 영상을 10초 만에 텍스트로 요약해 드립니다.")
st.markdown("---")

# [함수] 유튜브 링크에서 영상 ID만 쏙 뽑아내는 강력한 필터
def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# [입력] 사용자로부터 링크 받기
url = st.text_input("유튜브 링크를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

# [옵션] 요약 강도 조절
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    summary_len = st.select_slider("요약 핵심 문장 개수", options=[3, 5, 7, 10], value=5)
with col_opt2:
    spacing = st.radio("대본 줄바꿈 스타일", ["기본", "가독성 우선(넓게)"])

# [실행] 변환 버튼
if st.button("✨ 분석 시작", type="primary"):
    video_id = get_video_id(url)
    
    if not video_id:
        st.error("⚠️ 올바른 유튜브 주소가 아닙니다. 주소를 다시 확인해 주세요!")
    else:
        with st.spinner("유튜브 자막을 긁어오는 중입니다... 잠시만 기다려 주세요."):
            try:
                # 자막 가져오기 (한국어 -> 영어 순서로 시도)
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
                full_text = " ".join([t['text'] for t in transcript])
                
                # 가독성을 위해 문장을 적절히 쪼개기
                sentences = full_text.split('. ') if '. ' in full_text else full_text.split(' ')
                
                # 요약 로직 (가장 중요한 부분들만 골라내기)
                chunk = len(sentences) // summary_len
                summary_list = [sentences[i*chunk] for i in range(summary_len) if i*chunk < len(sentences)]
                
                st.balloons() # 성공 축하 풍선 효과
                st.markdown("---")
                
                # [결과 출력]
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.success("📌 핵심 요약 결과")
                    summary_text = "\n\n".join([f"✅ {s}..." for s in summary_list])
                    st.info(summary_text)
                    
                with res_col2:
                    st.info("🗣️ 전체 대본 (가독성 버전)")
                    join_char = "\n\n\n" if spacing == "가독성 우선(넓게)" else "\n\n"
                    st.text_area("전체 텍스트", value=join_char.join(sentences), height=400)
                    
            except Exception as e:
                st.error("❌ 자막을 찾을 수 없습니다. (영상 설정에서 '자막'이 꺼져있거나 지원되지 않는 영상입니다.)")
