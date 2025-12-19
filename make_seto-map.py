import pandas as pd
import folium
from folium.features import DivIcon
from branca.element import MacroElement, Template

# =====================
# CSV読み込み
# =====================
df_sake = pd.read_csv("sake.csv")
df_jinja = pd.read_csv("jinja.csv")

# =====================
# 地図（ベースマップ固定：control=False で標準レイヤーUIに出さない）
# =====================
m = folium.Map(
    location=[34.295, 132.81],
    zoom_start=12,
    tiles=None
)

folium.TileLayer(
    tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
    attr="© CARTO, © OpenStreetMap",
    control=False
).add_to(m)

# =====================
# レイヤー
# =====================
layer_sake = folium.FeatureGroup(name="酒蔵", show=True)
layer_jinja = folium.FeatureGroup(name="寺社", show=False)

size = 8  # ■マーカーの一辺(px)

# =====================
# Instagramアイコン（SVG）
# =====================
insta_svg = """
<svg width="18" height="18" viewBox="0 0 24 24">
  <path fill="rgba(0,0,0,0.65)" d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 4.5A5.5 5.5 0 1 1 6.5 14 5.5 5.5 0 0 1 12 8.5zm0 2A3.5 3.5 0 1 0 15.5 14 3.5 3.5 0 0 0 12 10.5zM18 6.8a1.2 1.2 0 1 1-1.2 1.2A1.2 1.2 0 0 1 18 6.8z"/>
</svg>
"""

# =====================
# 酒蔵マーカー（柄酒造だけpopup内にInstagramアイコン）
# =====================
for _, r in df_sake.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    x_url = str(r["x_url"]).strip()

    insta_url = ""
    if "instagram_url" in df_sake.columns and pd.notna(r.get("instagram_url", "")):
        insta_url = str(r["instagram_url"]).strip()

    # 1点だけ色を変える例（柄酒造）
    if "柄酒造" in name:
        color = "#c40000"
    else:
        color = "#0066cc"

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
        popup=folium.Popup(popup_html, max_width=240)
    ).add_to(layer_sake)

# =====================
# 寺社マーカー（緑）
# =====================
for _, r in df_jinja.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    url = ""
    if "url" in r and pd.notna(r["url"]):
        url = str(r["url"]).strip()

    color = "#1a7f37"  # 緑
    popup_html = name if url == "" else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

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
    ).add_to(layer_jinja)

# 地図に追加
layer_sake.add_to(m)
layer_jinja.add_to(m)

# =====================
# デザイン性の高い切替UI（自作コントロール）
# - 酒蔵：青い■
# - 寺社：緑の■
# - OFF：グレーの■
# =====================
sake_var = layer_sake.get_name()
jinja_var = layer_jinja.get_name()
map_var = m.get_name()

template = f"""
{{% macro html(this, kwargs) %}}
<style>
  .toggle-box {{
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 9999;
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(0,0,0,0.15);
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans JP", sans-serif;
    min-width: 140px;
  }}
  .toggle-title {{
    font-size: 12px;
    color: rgba(0,0,0,0.45);
    padding: 0 8px 6px 8px;
  }}
  .toggle-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 8px;
    border-radius: 8px;
    cursor: pointer;
    user-select: none;
  }}
  .toggle-item:hover {{ background: rgba(0,0,0,0.04); }}

  /* OFF時はグレー */
  .sq {{
    width: 10px;
    height: 10px;
    border-radius: 2px;
    background: rgba(160,160,160,0.25);
    flex: 0 0 auto;
  }}
  .label {{
    font-size: 13px;
    color: rgba(0,0,0,0.78);
    letter-spacing: 0.02em;
  }}

  /* ONの色（レイヤーONのときだけ色がつく） */
  .on-sake .sq {{ background: rgba(0,102,204,0.5); }}
  .on-jinja .sq {{ background: rgba(26,127,55,0.5); }}
</style>

<div class="toggle-box" id="customToggle">
  <div class="toggle-title">Layers</div>
  <div class="toggle-item" id="btn-sake"><span class="sq"></span><span class="label">酒蔵</span></div>
  <div class="toggle-item" id="btn-jinja"><span class="sq"></span><span class="label">寺社</span></div>
</div>

<script>
(function() {{
  function initWhenReady() {{
    var map = {map_var};
    var layerSake = {sake_var};
    var layerJinja = {jinja_var};

    var btnSake = document.getElementById("btn-sake");
    var btnJinja = document.getElementById("btn-jinja");
    var box = document.getElementById("customToggle");

    if (!btnSake || !btnJinja || !box || typeof map === "undefined") {{
      setTimeout(initWhenReady, 50);
      return;
    }}

    // ボタン押下が地図のドラッグ/ズームと競合しないようにする
    if (window.L && L.DomEvent) {{
      L.DomEvent.disableClickPropagation(box);
      L.DomEvent.disableScrollPropagation(box);
    }}

    function setBtn(btn, on, cls) {{
      if (on) btn.classList.add(cls);
      else btn.classList.remove(cls);
    }}

    // 初期状態を反映
    setBtn(btnSake, map.hasLayer(layerSake), "on-sake");
    setBtn(btnJinja, map.hasLayer(layerJinja), "on-jinja");

    // クリックでトグル
    btnSake.addEventListener("click", function() {{
      if (map.hasLayer(layerSake)) {{
        map.removeLayer(layerSake);
        setBtn(btnSake, false, "on-sake");
      }} else {{
        map.addLayer(layerSake);
        setBtn(btnSake, true, "on-sake");
      }}
    }});

    btnJinja.addEventListener("click", function() {{
      if (map.hasLayer(layerJinja)) {{
        map.removeLayer(layerJinja);
        setBtn(btnJinja, false, "on-jinja");
      }} else {{
        map.addLayer(layerJinja);
        setBtn(btnJinja, true, "on-jinja");
      }}
    }});
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", initWhenReady);
  }} else {{
    initWhenReady();
  }}
}})();
</script>
{{% endmacro %}}
"""

control = MacroElement()
control._template = Template(template)
m.get_root().add_child(control)

# =====================
# 保存
# =====================
m.save("seto-map.html")
print("saved: seto-map.html")
