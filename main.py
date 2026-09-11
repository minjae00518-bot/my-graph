import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # 여덟 자리 숫자로 된 날짜 열을 진짜 날짜로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


df = load_data()

# ── 그래프 1. 영화 하나의 흥행 곡선 ──────────────────────────
st.header("1. 한 영화의 흥행 곡선")

movie_list = sorted(df["영화명"].unique())
movie = st.selectbox("영화를 고르세요", movie_list)

one = df[df["영화명"] == movie].sort_values("날짜")

if not one.empty:
    fig1 = px.line(
        one,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"<{movie}> 일별 관객 수 추이",
    )
    fig1.update_traces(
        hovertemplate="날짜 %{x|%Y-%m-%d}<br>관객 %{y:,}명<extra></extra>"
    )
    st.plotly_chart(fig1, use_container_width=True)

st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 영화 개봉 후 일별 관객 수의 증감과 주말/평일 간의 관객 동원력 차이를 확인할 수 있습니다."
)

st.markdown("---")

# ── 그래프 2. Top 5 영화 흥행 곡선 비교 ────────────────────────
st.header("2. 일관객 합계 Top 5 영화의 흥행 곡선 비교")

top5_movies = (
    df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
)
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="기간 내 일관객 합계 Top 5 영화 비교",
    labels={"날짜": "날짜", "일관객": "일일 관객 수", "영화명": "영화 제목"},
)
fig2.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>날짜: %{x|%Y-%m-%d}<br>관객: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 흥행 상위 5개 영화의 일별 관객 수 변동 흐름과 주요 흥행 시기를 서로 비교해볼 수 있습니다."
)

st.markdown("---")

# ── 그래프 3. 날짜별 Top 10 일관객 합계 (영역 그래프) ──────────
st.header("3. 날짜별 박스오피스 Top 10 일관객 합계")

daily_total = df.groupby("날짜")["일관객"].sum().reset_index().sort_values("날짜")

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 Top 10 일관객 합계 (전체 극장가 활성도)",
    labels={"날짜": "날짜", "일관객": "10위권 관객 합계(명)"},
)

fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>Top 10 관객 합계: %{y:,}명<extra></extra>",
    line=dict(color="#1f77b4", width=2),
    fillcolor="rgba(31, 119, 180, 0.3)",
)

top3_days = daily_total.nlargest(3, "일관객")

for idx, row in top3_days.iterrows():
    date_str = row["날짜"].strftime("%Y-%m-%d")
    val_str = f"{row['일관객']:,}명"
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=f"<b>{date_str}</b><br>({val_str})",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor="red",
        ax=0,
        ay=-45,
        font=dict(size=11, color="black"),
        bgcolor="white",
        bordercolor="red",
        borderwidth=1,
    )

fig3.add_trace(
    go.Scatter(
        x=top3_days["날짜"],
        y=top3_days["일관객"],
        mode="markers",
        marker=dict(color="red", size=8),
        name="Top 3 관객수 날짜",
        hovertemplate="<b>[Top 3 Peak]</b><br>날짜: %{x|%Y-%m-%d}<br>관객: %{y:,}명<extra></extra>",
    )
)

st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 명절 연휴나 대형 신작 개봉일 등 전체 극장가 관객 수가 가장 많이 몰렸던 대목 날짜와 계절별 시장 활성화 정도를 파악할 수 있습니다."
)

st.markdown("---")

# ── 그래프 4. 기간 내 총 관객 수 Top 10 영화 (가로 막대그래프) ──
st.header("4. 기간 내 일관객 합계 Top 10 영화 순위")

top10_stats = (
    df.groupby("영화명")
    .agg(
        총관객=("일관객", "sum"),
        진입일수=("날짜", "nunique")
    )
    .reset_index()
    .nlargest(10, "총관객")
    .sort_values("총관객", ascending=True)
)

fig4 = px.bar(
    top10_stats,
    x="총관객",
    y="영화명",
    orientation="h",
    title="기간 내 10위권 합계 관객 수 Top 10 영화",
    labels={"총관객": "총 관객 수 (명)", "영화명": "영화 제목"},
    text_auto=",.0f",
)

fig4.update_traces(
    customdata=top10_stats[["진입일수"]],
    hovertemplate="<b>%{y}</b><br>총 관객 수: %{x:,}명<br>10위권 진입 일수: %{customdata[0]}일<extra></extra>",
    marker_color="#2ca02c",
)

fig4.update_layout(
    xaxis_title="총 일관객 합계 (명)",
    yaxis_title=None,
    template="plotly_white",
    height=450,
)

st.plotly_chart(fig4, use_container_width=True)

st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 1년 동안 박스오피스 10위권 내에서 가장 많은 관객을 동원한 대형 흥행작 10편의 상대적 규모와 롱런(장기 상영) 여부를 비교할 수 있습니다."
)

st.markdown("---")

# ── 그래프 5. 월 × 요일별 일관객 합계 히트맵 ─────────────────────
st.header("5. 월 × 요일별 일관객 합계 히트맵")

# 1. 월 및 요일 파생변수 추출
df_heatmap = df.copy()
df_heatmap["월"] = df_heatmap["날짜"].dt.month.astype(str) + "월"

weekday_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
df_heatmap["요일"] = df_heatmap["날짜"].dt.weekday.map(weekday_map)

# 2. 월 및 요일 정렬 순서 정의
months_order = [f"{m}월" for m in sorted(df_heatmap["날짜"].dt.month.unique())]
days_order = ["월", "화", "수", "목", "금", "토", "일"]

# 3. 월 × 요일 피벗 테이블 생성 및 요일 순서(월~일) 적용
pivot_df = (
    df_heatmap.pivot_table(
        index="요일",
        columns="월",
        values="일관객",
        aggfunc="sum"
    )
    .reindex(index=days_order, columns=months_order)
)

# 4. 히트맵 생성 (색이 진할수록 관객 수가 많음)
fig5 = px.imshow(
    pivot_df,
    labels=dict(x="월", y="요일", color="일관객 합계"),
    x=pivot_df.columns,
    y=pivot_df.index,
    color_continuous_scale="Reds",
    title="월 × 요일별 일관객 합계 분포",
    aspect="auto",
)

# 마우스 오버 툴팁 설정
fig5.update_traces(
    hovertemplate="<b>%{x} %{y}요일</b><br>관객 합계: %{z:,}명<extra></extra>"
)

fig5.update_layout(
    xaxis_title="월",
    yaxis_title="요일",
    template="plotly_white",
    height=450,
)

st.plotly_chart(fig5, use_container_width=True)

st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 연중 어떤 월과 요일에 극장 관객이 집중되는지 패턴을 한눈에 확인하여 성수기와 비성수기, 주말과 평일의 관객 동원력 차이를 비교할 수 있습니다."
)
