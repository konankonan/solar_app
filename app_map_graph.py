import streamlit as st
import pandas as pd
from  streamlit_folium import st_folium
import folium
import altair as alt
import datetime

df = pd.read_csv("solar_address.csv")
#st.table(df)

# ------------------------------------------------
# 地図の表示箇所とズームレベルを指定してマップデータを作成
# attr（アトリビュート）は地図右下に表示する文字列。
# ------------------------------------------------
# 地図の初期設定
# タイトル
st.title("メガソーラー監視")

with st.sidebar:

    # 機能選択
    option = st.radio(
        '処理選択',
        ['現在','日報','月報','年報'],
        index=1,
    )
    st.write(option)

    # 地図のタイトル
    st.subheader("監視メガソーラー位置")

    m = folium.Map(
        # 地図の中心位置の指定(今回は鶴居村を指定)
        location=[43.263124, 144.289747], 
        # タイル、アトリビュート(地図)の指定、デフォルトでは「OpenStreetMap」が使用される
        # tiles='https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png',  # 国土地理院
        # ズームを指定
        zoom_start=7.8,
        attr="メガソーラー設置場所",
    )

    # マーカーを作成してデータを追記
    for i,row in df.iterrows():
        # ポップアップの作成(名称、住所)
        pop=f"{row['名称']}({row['住所']})<br> 緯度{row['緯度'],}<br> 経度{row['経度'],}"
        # pop=f"{row['名称']}"
        # pop=f"{row['名称'],row['住所']}"

        folium.Marker(
            # 緯度と経度を指定
            location=[row['緯度'],row['経度']],
            # ツールチップの指定(名称)
            tooltip=row['名称'],
            # クリック時のポップアップの指定
            popup=folium.Popup(pop, max_width=300),
            # popup=i,
            # アイコンの指定(アイコン、色)
            icon=folium.Icon(icon="map-marker", icon_color="white", color="red")
        ).add_to(m)

    # 地図を表示
    # st_data = st_folium(m, width=1200, height=800)
    st_data = st_folium(m, width=1200, height=500)

# ------------------------------------------------
# 日付選択カレンダー
min_date = datetime.date(1900, 1, 1)
max_date = datetime.date(2100, 12, 31)
d = st.date_input('データ日付選択', value="default_value_today", min_value=min_date, max_value=max_date)

# ------------------------------------------------
# 棒グラフを表示
# グラフの描画用関数を定義
def get_chart(data):
    hover = alt.selection_single(
        fields=["time"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="temperature")
        .mark_line()
        .encode(
            x="time",
            y="data",
            # color="symbol",
            # strokeDash="symbol",
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="time",
            y="data",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("time", title="時刻"),
                alt.Tooltip("data", title="日射量(kWh)"),
            ],
        )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()

# グラフのタイトル
st.subheader('日報グラフ')

# ヘッダ行、集計行をスキップして読み込んでくれる
dataframe = pd.read_csv('s0_hd_20240512.csv', comment="#", skiprows=[0,1,27,28,29,30])
#print(dataframe)

# 線グラフの設定
# chart = get_chart(dataframe)

# バーグラフの設定
chart = alt.Chart(dataframe).mark_bar().encode(
    x='time',
    y='data'
)

st.altair_chart(chart, use_container_width=True)

# リストの表示
st.subheader('日報リスト')
st.dataframe(dataframe,600,400)
# st.table(dataframe)

