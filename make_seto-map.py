import pandas as pd
import folium
from folium.features import DivIcon

# =====================
# CSV読み込み
# =====================
df_sake = pd.read_csv("sake.csv")
df_jinja = pd.read_csv("jinja.csv")

# =====================
# 地図
# =====================
m = folium.Map(
    location=[34.295, 132.81],
    zoom_start=12,
    tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
    attr="© CARTO, © OpenStreetMap"
)

layer_sake = folium.FeatureGroup(name="酒蔵", show=True)
layer_jinja = folium.FeatureGroup(name="寺社", show=False)

size = 8  # ■サイズ

# =====================
# 酒蔵マーカー（popup内：中央揃え＋Instagramアイコンのみ）
# =====================
for _, r in df_sake.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    x_url = str(r["x_url"]).strip()

    insta_url = ""
    if "instagram_url" in df_sake.columns and pd.notna(r.get("instagram_url", "")):
        insta_url = str(r["instagram_url"]).strip()

    if "柄酒造" in name:
        color = "#c40000"
    else:
        color = "#0066cc"

    insta_svg = """
    <svg width="18" height="18" viewBox="0 0 24 24">
      <path fill="rgba(0,0,0,0.65)" d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 4.5A5.5 5.5 0 1 1 6.5 14 5.5 5.5 0 0 1 12 8.5zm0 2A3.5 3.5 0 1 0 15.5 14 3.5 3.5 0 0 0 12 10.5zM18 6.8a1.2 1.2 0 1 1-1.2 1.2A1.2 1.2 0 0 1 18 6.8z"/>
    </svg>
    """

    # popup（中央揃え）
    popup_html = f'''
    <div style="text-align:center; font-size:13px; line-height:1.4;">
      <div style="margin-bottom:6px;">
        <a href="{x_url}" target="_blank" rel="noopener noreferrer">{name}</a>
      </div>
    '''

    if ("柄酒造" in name) and insta_url:
        popup_html += f'''
        <div>
          <a href="{insta_url}" target="_blank" rel="noopener noreferrer"
             style="display:inline-block; text-decoration:none;">
            {insta_svg}
          </a>
        </div>
        '''

    popup_html += '</div>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size, size),
            icon_anchor=(size // 2, size // 2),
            popup_anchor=(0, -size // 2),
            html=f"""
            <div style="transform: translate(-50%, -50%);">
              <div style="
                  width:{size}px;
                  height:{size}px;
                  background:{color};
                  opacity:0.4;
              "></div>
            </div>
            """
        ),
        popup=folium.Popup(popup_html, max_width=220)
    ).add_to(layer_sake)

# =====================
# 寺社マーカー
# =====================
for _, r in df_jinja.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    url = ""
    if "url" in r and pd.notna(r["url"]):
        url = str(r["url"]).strip()

    color = "#1a7f37"
    popup_html = name if url == "" else f'<a href="{url}" target="_blank">{name}</a>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size, size),
            icon_anchor=(size // 2, size // 2),
            popup_anchor=(0, -size // 2),
            html=f"""
            <div style="transform: translate(-50%, -50%);">
              <div style="
                  width:{size}px;
                  height:{size}px;
                  background:{color};
                  opacity:0.4;
              "></div>
            </div>
            """
        ),
        popup=folium.Popup(popup_html, max_width=200)
    ).add_to(layer_jinja)

layer_sake.add_to(m)
layer_jinja.add_to(m)

# =====================
# 保存
# =====================
m.save("seto-map.html")
print("saved: seto-map.html")
