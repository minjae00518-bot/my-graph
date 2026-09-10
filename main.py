import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 헤더
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("시간의 흐름에 따른 대한민국 박스오피스 영화 데이터의 변화를 시각화합니다.")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리
# -----------------------------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    # '날짜' 열(8자리 숫자/문자)을 진짜 datetime 객체로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    # 날짜 및 순위 기준으로 정렬
    df = df.sort_values(by=['날짜', '순위']).reset_index(drop=True)
    return df

try:
    with st.spinner("데이터를 불러오는 중입니다..."):
        df = load_data(DATA_URL)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 3. 사이드바 - 정보 및 내비게이션
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("📌 도감 정보")
    st.markdown(
        f"""
        - **분석 대상:** 1년치(365일) 일별 박스오피스 Top 10
        - **수집 기간:** {df['날짜'].min().strftime('%Y-%m-%d')} ~ {df['날짜'].max().strftime('%Y-%m-%d')}
        - **총 집계 영화 수:** {df['영화명'].nunique():,}개
        """
    )
    st.markdown("---")
    st.header("📂 그래프 목록")
    st.markdown("""
    1. 📈 **특정 영화의 일관객 변화**
    2. ⏳ *추가 그래프 영역 (업데이트 예정)*
    """)

# -----------------------------------------------------------------------------
# 4. [구역 1] 특정 영화의 일별 관객수 변화 추이
# -----------------------------------------------------------------------------
st.header("1. 특정 영화의 일별 관객수 변화 (시간의 흐름)")
st.write("선택한 영화가 박스오피스 10위권 내에 머무르는 동안의 일별 관객수 변화를 확인할 수 있습니다.")

# 영화 선택 드롭다운 (누적관객수가 높은 순서대로 정렬)
top_movies = df.groupby('영화명')['누적관객'].max().sort_values(ascending=False).index.tolist()
selected_movie = st.selectbox(
    "조회할 영화를 선택하세요:",
    options=top_movies,
    index=0,
    help="누적 관객수가 높은 순서대로 정렬되어 있습니다."
)

# 선택된 영화 데이터 필터링
movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')

if not movie_df.empty:
    # 핵심 요약 지표 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("최고 일관객수", f"{movie_df['일관객'].max():,} 명")
    with col2:
        st.metric("최고 순위", f"{movie_df['순위'].min()} 위")
    with col3:
        st.metric("최대 스크린수", f"{movie_df['스크린수'].max():,} 개")
    with col4:
        st.metric("Top 10 진입 일수", f"{len(movie_df)} 일")

    st.subheader("")

    # Plotly 라인 그래프 생성
    fig = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 일별 관객수 추이",
        markers=True,
        labels={'날짜': '날짜', '일관객': '일일 관객수(명)'}
    )

    # 마우스 오버(호버) 툴팁 및 디자인 세팅
    fig.update_traces(
        line=dict(color='#E50914', width=2.5),
        marker=dict(size=6, color='#111111'),
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    )

    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=450,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # [지정 영역] 이 그래프로 알 수 있는 것 문구
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "영화의 개봉 초기 관객 집중도, 주말과 평일 간의 관객 수 변동 폭, 그리고 흥행 유효 기간(관객 수 감소 추세)을 한눈에 파악할 수 있습니다."
    )
else:
    st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. [구역 2] 앞으로 추가될 그래프를 위한 확장 구역
# -----------------------------------------------------------------------------
st.header("2. 영화별 누적 관객수 및 상영 효율 분석 (추가 예정)")
st.info("🚧 새로운 시간 축 기반 시각화 그래프가 이 구역에 추가될 예정입니다.")

# [지정 영역] 이 그래프로 알 수 있는 것 문구 틀
st.caption("💡 **이 그래프로 알 수 있는 것:** (새로운 그래프가 추가되면 여기에 해당 시각화의 인사이트 요약 문구가 들어갑니다.)")
