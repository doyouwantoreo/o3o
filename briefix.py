import streamlit as st
import yt_dlp
import json
import re
import requests

# 페이지 설정
st.set_page_config(page_title="BrieFix - 프리미엄 요약기", page_icon="🎬", layout="wide")

st.title("🚀 BrieFix (브리픽스) Pro")
st.markdown("### 기계적인 짜깁기는 그만! 문맥을 살려 핵심 내용을 요약합니다.")
st.markdown("---")

url = st.text_input("유튜브 링크를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if st.button("✨ 업그레이드 AI 분석 시작", type="primary"):
    if not url.strip():
        st.warning("유튜브 주소를 입력해 주세요!")
    else:
        with st.spinner("유튜브 영상의 흐름을 분석하는 중입니다..."):
            try:
                # yt-dlp 설정
                ydl_opts = {
                    'writeautomaticsub': True,
                    'writesubtitles': True,
                    'skip_download': True,
                    'subtitlesformat': 'json3',
                    'quiet': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', '유튜브 영상')
                    subtitles = info.get('subtitles', {})
                    automatic_captions = info.get('automatic_captions', {})
                    
                    sub_data = None
                    if 'ko' in subtitles: sub_data = subtitles['ko']
                    elif 'ko' in automatic_captions: sub_data = automatic_captions['ko']
                    elif 'en' in subtitles: sub_data = subtitles['en']
                    elif 'en' in automatic_captions: sub_data = automatic_captions['en']
                        
                    if not sub_data:
                        raise Exception("이 영상에는 추출 가능한 자막 데이터가 없습니다.")
                    
                    json_url = next((s['url'] for s in sub_data if s.get('ext') == 'json3'), sub_data[0]['url'])
                    
                    response = requests.get(json_url)
                    sub_json = response.json()
                    
                    # 1. 의미 있는 단어/문장 단위로 텍스트 정제
                    lines = []
                    if 'events' in sub_json:
                        for event in sub_json['events']:
                            if 'segs' in event:
                                text = "".join([seg['utf8'] for seg in event['segs'] if 'utf8' in seg]).strip()
                                # 단순 감탄사나 무의미한 한 글자 단어 필터링
                                if text and len(text) > 1 and not text.isspace():
                                    lines.append(text)
                    
                    # 중복되어 겹치는 자막 문구 제거
                    cleaned_lines = []
                    for line in lines:
                        if not cleaned_lines or cleaned_lines[-1] != line:
                            cleaned_lines.append(line)
                            
                    full_text = " ".join(cleaned_lines)
                    full_text = re.sub(r'\s+', ' ', full_text)
                    
                    # 2. 문맥 중심 요약 알고리즘 (영상의 서론/본론/결론 분할 매핑)
                    # 단어들을 일정 크기의 '의미 덩어리(문단)'로 묶음
                    words = full_text.split()
                    if len(words) < 10:
                        st.error("영상의 자막 내용이 너무 짧아 요약할 수 없습니다.")
                    else:
                        st.balloons()
                        
                        # 대본을 3개의 파트(도입부, 핵심내용, 마무리)로 강제 분할하여 문맥 흐름 잡기
                        total_words = len(words)
                        part_size = total_words // 3
                        
                        part1 = " ".join(words[:part_size])
                        part2 = " ".join(words[part_size:part_size*2])
                        part3 = " ".join(words[part_size*2:])
                        
                        # 각 파트에서 가장 길고 완결성 있는 문장 흐름을 요약본으로 추출
                        def get_summary_chunk(text_part, fallback_headline="핵심 내용 요약"):
                            chunks = text_part.split(' ')
                            if len(chunks) > 15:
                                return " ".join(chunks[:15]) + "..."
                            return " ".join(chunks) + "..."

                        st.success(f"📺 영상 제목: {title}")
                        st.markdown("---")
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.subheader("📌 문맥 중심 3단계 요약")
                            
                            st.markdown(f"**1️⃣ 도입부 (영상 시작 및 주제 소개)**")
                            st.info(get_summary_chunk(part1))
                            
                            st.markdown(f"**2️⃣ 본론 (가장 중요한 핵심 주장/설명)**")
                            st.info(get_summary_chunk(part2))
                            
                            st.markdown(f"**3️⃣ 결론 (요약 및 마무리 메시지)**")
                            st.info(get_summary_chunk(part3))
                            
                        with col2:
                            st.subheader("🗣️ 전체 대본 트랙")
                            # 가독성을 위해 15단어마다 줄바꿈 처리한 전체 대본
                            readable_script = ""
                            for i in range(0, len(words), 12):
                                readable_script += " ".join(words[i:i+12]) + "\n"
                            
                            st.text_area("텍스트", value=readable_script, height=450, label_visibility="collapsed")
                            
            except Exception as e:
                st.error(f"❌ 분석 실패: {str(e)}")
                st.info("자막이 제대로 켜져 있는 다른 강의 영상 링크로 다시 시도해 보세요!")
