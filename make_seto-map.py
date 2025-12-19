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
# 地図（ベースマップ固定）
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
# 酒蔵マーカー
# =====================
for _, r in df_sake.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    x_url = str(r["x_url"]).strip()

    if "柄酒造" in name:
        color = "#c40000"
    else:
        color = "#0066cc"

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size, size),
            icon_anchor=(size // 2, size // 2),
            popup_anchor=(0, -size // 2),
            html=f"""
            <div style="
                width:{size}px;
                height:{size}px;
                background:{color};
                opacity:0.4;
            "></div>
            """
        ),
        popup=folium.Popup(
            f'<a href="{x_url}" target="_blank">{name}</a>',
            max_width=220
        )
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
            <div style="
                width:{size}px;
                height:{size}px;
                background:{color};
                opacity:0.4;
            "></div>
            """
        ),
        popup=folium.Popup(
            f'<a href="{x_url}" target="_blank">{name}</a>',
            max_width=220
        )
    ).add_to(layer_jinja)

# 地図に追加
layer_sake.add_to(m)
layer_jinja.add_to(m)

# =====================
# デザインUI（切替ボタン）
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

  .toggle-item:hover {{
    background: rgba(0,0,0,0.04);
  }}

  .sq {{
    width: 10px;
    height: 10px;
    border-radius: 2px;
    background: rgba(160,160,160,0.25);  /* OFF：薄いグレー */
    flex: 0 0 auto;
  }}

  .label {{
    font-size: 13px;
    color: rgba(0,0,0,0.78);
    letter-spacing: 0.02em;
  }}

  .on-sake .sq {{
    background: rgba(0,102,204,0.5);     /* 酒蔵ON：青 */
  }}

  .on-jinja .sq {{
    background: rgba(26,127,55,0.5);     /* 寺社ON：緑 */
  }}
</style>

<div class="toggle-box" id="customToggle">
  <div class="toggle-title">Layers</div>

  <div class="toggle-item on-sake" id="btn-sake">
    <span class="sq"></span>
    <span class="label">酒蔵</span>
  </div>

  <div class="toggle-item on-jinja" id="btn-jinja">
    <span class="sq"></span>
    <span class="label">寺社</span>
  </div>
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

    if (window.L && L.DomEvent) {{
      L.DomEvent.disableClickPropagation(box);
      L.DomEvent.disableScrollPropagation(box);
    }}

    function setBtn(btn, on, cls) {{
      if (on) btn.classList.add(cls);
      else btn.classList.remove(cls);
    }}

    setBtn(btnSake, map.hasLayer(layerSake), "on-sake");
    setBtn(btnJinja, map.hasLayer(layerJinja), "on-jinja");

    btnSake.onclick = function() {{
      if (map.hasLayer(layerSake)) {{
        map.removeLayer(layerSake);
        setBtn(btnSake, false, "on-sake");
      }} else {{
        map.addLayer(layerSake);
        setBtn(btnSake, true, "on-sake");
      }}
    }};

    btnJinja.onclick = function() {{
      if (map.hasLayer(layerJinja)) {{
        map.removeLayer(layerJinja);
        setBtn(btnJinja, false, "on-jinja");
      }} else {{
        map.addLayer(layerJinja);
        setBtn(btnJinja, true, "on-jinja");
      }}
    }};
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
