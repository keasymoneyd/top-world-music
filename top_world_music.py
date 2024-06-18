import pandas as pd
import streamlit as st
import requests
import os

# 替換成你的 Musixmatch API 金鑰
MUSIXMATCH_API_KEY = "YOUR_MUSIXMATCH_API_KEY"

# 訂閱方案
subscription_plans = {
    "免費方案": {
        "features": ["瀏覽熱門歌曲", "觀看 YouTube 影片"],
        "price": "免費"
    },
    "進階方案": {
        "features": ["瀏覽熱門歌曲", "觀看 YouTube 影片", "查看完整歌詞"],
        "price": "每月 $9.99"
    },
}

# 模擬使用者資料和訂閱狀態 (實際應用中，你需要使用資料庫來儲存)
user_data = {
    "user1": {"subscribed": False, "plan": "免費方案"},
    "user2": {"subscribed": True, "plan": "進階方案"}
}

def get_lyrics(track_name, artist_name):
    """使用 Musixmatch API 抓取歌詞。"""
    api_url = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get"
    params = {
        "apikey": MUSIXMATCH_API_KEY,
        "q_track": track_name,
        "q_artist": artist_name
    }
    response = requests.get(api_url, params=params)
    data = response.json()

    if data['message']['header']['status_code'] == 200:
        lyrics = data['message']['body']['lyrics']['lyrics_body']
        return lyrics
    else:
        st.error(f"找不到 {track_name} - {artist_name} 的歌詞")
        return None

# 設定 CSV 檔案資料夾路徑
csv_folder = "./youtube_links"

# 取得所有國家名稱
country_options = [filename.replace("_youtube_links.csv", "") for filename in os.listdir(csv_folder) if filename.endswith("_youtube_links.csv")]

# Streamlit 應用程式
st.set_page_config(page_title="熱門歌曲資訊", page_icon="🎵", layout="wide")
st.title("🎵 熱門歌曲資訊")
st.markdown("透過我們的應用程式，您可以瀏覽和觀看來自不同國家的熱門歌曲。")

# 自定義CSS
st.markdown(
    """
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .st-expander {
        border: 1px solid #4CAF50;
        border-radius: 4px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 模擬使用者登入 (實際應用中，你需要使用安全的認證機制)
with st.sidebar:
    st.header("使用者登入")
    username = st.text_input("使用者名稱")

if username in user_data:
    st.sidebar.success(f"歡迎回來，{username}！")
    user = user_data[username]

    # 顯示訂閱方案資訊
    st.sidebar.header("你的訂閱方案")
    st.sidebar.write(f"方案名稱：{user['plan']}")
    st.sidebar.write(f"價格：{subscription_plans[user['plan']]['price']}")
    st.sidebar.write(f"功能：{', '.join(subscription_plans[user['plan']]['features'])}")

    # 顯示所有訂閱方案資訊
    st.sidebar.header("訂閱方案")
    for plan, details in subscription_plans.items():
        with st.sidebar.expander(f"### {plan}"):
            st.write(f"價格：{details['price']}")
            st.write(f"功能：{', '.join(details['features'])}")

    # 主界面
    col1, col2 = st.columns([1, 2])

    with col1:
        # 選擇國家
        selected_country = st.selectbox("選擇國家", country_options)

    with col2:
        # 讀取 YouTube 歌曲連結 CSV 檔案
        csv_file_path = os.path.join(csv_folder, f"{selected_country}_youtube_links.csv")
        if not os.path.exists(csv_file_path):
            st.error(f"找不到檔案: {csv_file_path}")
        else:
            df_youtube = pd.read_csv(csv_file_path, encoding='utf-8-sig')

            # 選擇歌曲
            song_name = st.selectbox("選擇歌曲", df_youtube["Song Name"])

            # 取得 YouTube 連結
            youtube_link = df_youtube[df_youtube["Song Name"] == song_name]["YouTube Link"].iloc[0]

            # 顯示 YouTube 影片
            st.video(youtube_link)

            # 從歌曲名稱中提取歌手名稱
            artist_name = song_name.split(" - ")[0]
            track_name = song_name.split(" - ")[1]

            # 根據訂閱方案顯示歌詞
            if "查看完整歌詞" in subscription_plans[user['plan']]['features']:
                with st.spinner('載入歌詞中...'):
                    lyrics = get_lyrics(track_name, artist_name)
                    if lyrics:
                        st.markdown("## 歌詞")
                        st.text(lyrics)
            else:
                st.warning("請升級至進階方案以查看完整歌詞。")
else:
    st.sidebar.warning("請輸入有效的使用者名稱。")