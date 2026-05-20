import streamlit as st
import yt_dlp
import json
import re

# 페이지 설정
st.set_page_config(page_title="BrieFix - 유튜브 자막 요약기", page_icon="🎬")

st.title("🚀 BrieFy (브리파이)")
st.subheader("가장 안정적인 최신 엔진으로 유튜브 자막을 추출해 요약합니다.")
st.markdown("---")

# 유튜브 링크 입력란
url = st.text_input("유튜브 링크를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

# 핵심 문장 개수 선택
summary_len = st.slider("요약할 핵심 문장 개수", min_value=3, max_value=10, value=5)

if st.button("✨ 분석 및 요약 시작", type="primary"):
    if not url.strip():
        st.warning("유튜브 주소를 입력해 주세요!")
    else:
        with st.spinner("유튜브 서버에서 자막 데이터를 안전하게 수집하는 중입니다..."):
            try:
                # yt-dlp 설정 (자막만 추출하는 옵션)
                ydl_opts = {
                    'writeautomaticsub': True,  # 자동 생성 자막 허용
                    'writesubtitles': True,      # 수동 자막 허용
                    'skip_download': True,       # 영상 다운로드는 패스
                    'subtitlesformat': 'json3',  # 가장 읽기 쉬운 json3 형식
                    'quiet': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # 수동 자막이나 자동 자막 중 한국어(ko) 추출
                    subtitles = info.get('subtitles', {})
                    requested_subtitles = info.get('requested_subtitles', {})
                    automatic_captions = info.get('automatic_captions', {})
                    
                    sub_data = None
                    # 1순위: 한국어 수동 자막, 2순위: 한국어 자동 자막, 3순위: 영어 자막
                    if 'ko' in subtitles:
                        sub_data = subtitles['ko']
                    elif 'ko' in automatic_captions:
                        sub_data = automatic_captions['ko']
                    elif 'en' in subtitles:
                        sub_data = subtitles['en']
                    elif 'en' in automatic_captions:
                        sub_data = automatic_captions['en']
                        
                    if not sub_data:
                        raise Exception("이 영상에는 추출 가능한 자막 데이터가 존재하지 않습니다.")
                    
                    # json3 형식의 URL 주소 찾기
                    json_url = next((s['url'] for s in sub_data if s.get('ext') == 'json3'), None)
                    
                    if not json_url:
                        # json3가 없으면 첫 번째 포맷 사용
                        json_url = sub_data[0]['url']
                        
                    # 자막 텍스트 다운로드 및 파싱
                    import requests
                    response = requests.get(json_url)
                    sub_json = response.json()
                    
                    # 가독성 있게 텍스트 합치기
                    lines = []
                    if 'events' in sub_json:
                        for event in sub_json['events']:
                            if 'segs' in event:
                                text = "".join([seg['utf8'] for seg in event['segs'] if 'utf8' in seg]).strip()
                                if text and not text.isspace():
                                    lines.append(text)
                                    
                    full_text = " ".join(lines)
                    # 중복 공백 제거
                    full_text = re.sub(r'\s+', ' ', full_text)
                    
                    # 문장 단위 분리
                    sentences = [s.strip() for s in full_text.split('. ') if s.strip()]
                    if len(sentences) < 2:
                        sentences = full_text.split(' ') # 문장 부호가 없으면 띄어쓰기로 분리
                    
                    if not sentences or len(full_text) < 5:
                        st.error("❌ 자막을 파싱했으나 내용이 비어있습니다. 다른 영상으로 시도해 주세요.")
                    else:
                        st.balloons()
                        st.markdown("---")
                        
                        # [결과 화면 출력]
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.success("📌 AI 핵심 요약")
                            # 알고리즘 기반 요약 (균등 분포 추출)
                            chunk = max(1, len(sentences) // summary_len)
                            summary_list = [sentences[i*chunk] for i in range(summary_len) if i*chunk < len(sentences)]
                            
                            summary_html = ""
                            for i, s in enumerate(summary_list[:summary_len], 1):
                                summary_html += f"**{i}.** {s}...\n\n"
                            st.info(summary_html)
                            
                        with col2:
                            st.info("🗣️ 변환된 전체 대본")
                            st.text_area("전체 대본 박스", value="\n\n".join(sentences), height=400, label_visibility="collapsed")
                            
            except Exception as e:
                st.error(f"❌ 에러 발생: {str(e)}")
                st.info("💡 유튜브 링크 뒤에 플레이리스트 주소(&list=...) 등이 붙어있다면 지우고 순수한 영상 주소만 입력해 보세요!")
