import pandas as pd
import folium
from folium.features import DivIcon
from branca.element import MacroElement, Template

# =====================
# CSV読み込み
# =====================
df_sake = pd.read_csv("sake.csv")
df_jinja = pd.read_csv("jinja.csv")
df_arch = pd.read_csv("architecture.csv")
df_islands = pd.read_csv("islands.csv")   # ←追加：島CSV

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
layer_arch = folium.FeatureGroup(name="建築", show=False)
layer_islands = folium.FeatureGroup(name="島", show=False)   # ←追加
layer_otafuku = folium.FeatureGroup(name="柄酒造", show=True)  # 常時表示（UIでは表示のみ）

# サイズ
size = 8
size_otafuku = 10
size_arch = 8
size_islands = 5   # ←島は少しだけ小さく

# =====================
# アイコン（SVG）
# =====================
insta_svg = """
<svg width="18" height="18" viewBox="0 0 24 24">
  <path fill="rgba(0,0,0,0.65)" d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 4.5A5.5 5.5 0 1 1 6.5 14 5.5 5.5 0 0 1 12 8.5zm0 2A3.5 3.5 0 1 0 15.5 14 3.5 3.5 0 0 0 12 10.5zM18 6.8a1.2 1.2 0 1 1-1.2 1.2A1.2 1.2 0 0 1 18 6.8z"/>
</svg>
"""

x_svg = """
<svg width="18" height="18" viewBox="0 0 24 24">
  <path fill="rgba(0,0,0,0.65)" d="M18.9 2H22l-6.8 7.8L23 22h-6.4l-5-6.3L6 22H3l7.4-8.6L1 2h6.5l4.5 5.6L18.9 2zm-1.1 18h1.8L6.2 4H4.3l13.5 16z"/>
</svg>
"""

# =====================
# 酒蔵マーカー（柄酒造だけ別レイヤー＆サイズ別）
# =====================
for _, r in df_sake.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    x_url = str(r["x_url"]).strip()

    insta_url = ""
    if "instagram_url" in df_sake.columns and pd.notna(r.get("instagram_url", "")):
        insta_url = str(r["instagram_url"]).strip()

    is_otafuku = ("柄酒造" in name)

    color = "#c40000" if is_otafuku else "#0066cc"
    this_size = size_otafuku if is_otafuku else size

    popup_html = f'''
    <div style="text-align:center; font-size:13px; line-height:1.4;">
      <div style="margin-bottom:6px;">
        <a href="{x_url}" target="_blank" rel="noopener noreferrer">{name}</a>
      </div>
    '''

    if is_otafuku and insta_url:
        popup_html += f'''
        <div style="display:flex; justify-content:center; gap:10px; align-items:center;">
          <a href="{insta_url}" target="_blank" rel="noopener noreferrer" style="display:inline-block; text-decoration:none;">
            {insta_svg}
          </a>
        </div>
        '''

    popup_html += '</div>'

    marker = folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(this_size, this_size),
            icon_anchor=(this_size // 2, this_size // 2),
            popup_anchor=(0, -this_size // 2),
            html=f"""
            <div style="
              width:{this_size}px;
              height:{this_size}px;
              background:{color};
              opacity:0.4;
            "></div>
            """
        ),
        popup=folium.Popup(popup_html, max_width=260)
    )

    if is_otafuku:
        marker.add_to(layer_otafuku)
    else:
        marker.add_to(layer_sake)

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

    color = "#1a7f37"
    popup_html = name if url == "" else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

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
        popup=folium.Popup(popup_html, max_width=220)
    ).add_to(layer_jinja)

# =====================
# 建築マーカー（黄色）
# =====================
arch_color = "#f2c300"

def format_arch_name(raw: str) -> str:
    if "<br>" in raw:
        main, sub = raw.split("<br>", 1)
        return f'{main}<br><span style="font-size:11px; color:rgba(0,0,0,0.6);">{sub}</span>'
    return raw

for _, r in df_arch.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    url = ""
    if "url" in df_arch.columns and pd.notna(r.get("url", "")):
        url = str(r["url"]).strip()

    insta_url = ""
    if "instagram_url" in df_arch.columns and pd.notna(r.get("instagram_url", "")):
        insta_url = str(r["instagram_url"]).strip()

    x_url = ""
    if "x_url" in df_arch.columns and pd.notna(r.get("x_url", "")):
        x_url = str(r["x_url"]).strip()

    formatted_name = format_arch_name(name)

    if url:
        title_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{formatted_name}</a>'
    else:
        title_html = formatted_name

    icon_parts = []
    if x_url:
        icon_parts.append(
            f'<a href="{x_url}" target="_blank" rel="noopener noreferrer" style="display:inline-block; text-decoration:none;">{x_svg}</a>'
        )
    if insta_url:
        icon_parts.append(
            f'<a href="{insta_url}" target="_blank" rel="noopener noreferrer" style="display:inline-block; text-decoration:none;">{insta_svg}</a>'
        )

    icons = ""
    if icon_parts:
        icons = f'<div style="margin-top:6px; display:flex; justify-content:center; gap:10px; align-items:center;">{"".join(icon_parts)}</div>'

    popup_html = f'''
    <div style="text-align:center; font-size:13px; line-height:1.35;">
      <div>{title_html}</div>
      {icons}
    </div>
    '''

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_arch, size_arch),
            icon_anchor=(size_arch // 2, size_arch // 2),
            popup_anchor=(0, -size_arch // 2),
            html=f"""
            <div style="
              width:{size_arch}px;
              height:{size_arch}px;
              background:{arch_color};
              opacity:0.4;
            "></div>
            """
        ),
        popup=folium.Popup(popup_html, max_width=280)
    ).add_to(layer_arch)

# =====================
# 島マーカー（濃いグレー・小さめ）
# =====================
island_color = "#3a3a3a"  # 濃いグレー

for _, r in df_islands.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    url = ""
    if "url" in df_islands.columns and pd.notna(r.get("url", "")):
        url = str(r["url"]).strip()

    insta_url = ""
    if "instagram_url" in df_islands.columns and pd.notna(r.get("instagram_url", "")):
        insta_url = str(r["instagram_url"]).strip()

    x_url = ""
    if "x_url" in df_islands.columns and pd.notna(r.get("x_url", "")):
        x_url = str(r["x_url"]).strip()

    # タイトル（URLがあればリンク化）
    title_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>' if url else name

    # SNS（あれば）
    icon_parts = []
    if x_url:
        icon_parts.append(
            f'<a href="{x_url}" target="_blank" rel="noopener noreferrer" style="display:inline-block; text-decoration:none;">{x_svg}</a>'
        )
    if insta_url:
        icon_parts.append(
            f'<a href="{insta_url}" target="_blank" rel="noopener noreferrer" style="display:inline-block; text-decoration:none;">{insta_svg}</a>'
        )

    icons = ""
    if icon_parts:
        icons = f'<div style="margin-top:6px; display:flex; justify-content:center; gap:10px; align-items:center;">{"".join(icon_parts)}</div>'

    popup_html = f'''
    <div style="text-align:center; font-size:13px; line-height:1.35;">
      <div>{title_html}</div>
      {icons}
    </div>
    '''

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_islands, size_islands),
            icon_anchor=(size_islands // 2, size_islands // 2),
            popup_anchor=(0, -size_islands // 2),
            html=f"""
            <div style="
              width:{size_islands}px;
              height:{size_islands}px;
              background:{island_color};
              opacity:0.45;
            "></div>
            """
        ),
        popup=folium.Popup(popup_html, max_width=260)
    ).add_to(layer_islands)

# =====================
# 地図に追加
# =====================
layer_sake.add_to(m)
layer_jinja.add_to(m)
layer_arch.add_to(m)
layer_islands.add_to(m)
layer_otafuku.add_to(m)

# =====================
# カスタム凡例UI
# =====================
sake_var = layer_sake.get_name()
jinja_var = layer_jinja.get_name()
arch_var = layer_arch.get_name()
islands_var = layer_islands.get_name()
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
    min-width: 150px;
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

  .on-otafuku .sq {{ background: rgba(196,0,0,0.5); }}
  .on-sake .sq {{ background: rgba(0,102,204,0.5); }}
  .on-jinja .sq {{ background: rgba(26,127,55,0.5); }}
  .on-arch .sq {{ background: rgba(242,195,0,0.5); }}
  .on-islands .sq {{ background: rgba(58,58,58,0.55); }}

  .toggle-static {{ cursor: default; }}
  .toggle-static:hover {{ background: transparent; }}
</style>

<div class="toggle-box" id="customToggle">
  <div class="toggle-title">Layers</div>

  <div class="toggle-item toggle-static on-otafuku" id="btn-otafuku">
    <span class="sq"></span><span class="label">柄酒造</span>
  </div>

  <div class="toggle-item" id="btn-sake"><span class="sq"></span><span class="label">酒蔵</span></div>
  <div class="toggle-item" id="btn-jinja"><span class="sq"></span><span class="label">寺社</span></div>
  <div class="toggle-item" id="btn-arch"><span class="sq"></span><span class="label">建築</span></div>
  <div class="toggle-item" id="btn-islands"><span class="sq"></span><span class="label">島</span></div>
</div>

<script>
(function() {{
  function initWhenReady() {{
    var map = {map_var};
    var layerSake = {sake_var};
    var layerJinja = {jinja_var};
    var layerArch = {arch_var};
    var layerIslands = {islands_var};

    var btnSake = document.getElementById("btn-sake");
    var btnJinja = document.getElementById("btn-jinja");
    var btnArch = document.getElementById("btn-arch");
    var btnIslands = document.getElementById("btn-islands");
    var box = document.getElementById("customToggle");

    if (!btnSake || !btnJinja || !btnArch || !btnIslands || !box || typeof map === "undefined") {{
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
    setBtn(btnArch, map.hasLayer(layerArch), "on-arch");
    setBtn(btnIslands, map.hasLayer(layerIslands), "on-islands");

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

    btnArch.addEventListener("click", function() {{
      if (map.hasLayer(layerArch)) {{
        map.removeLayer(layerArch);
        setBtn(btnArch, false, "on-arch");
      }} else {{
        map.addLayer(layerArch);
        setBtn(btnArch, true, "on-arch");
      }}
    }});

    btnIslands.addEventListener("click", function() {{
      if (map.hasLayer(layerIslands)) {{
        map.removeLayer(layerIslands);
        setBtn(btnIslands, false, "on-islands");
      }} else {{
        map.addLayer(layerIslands);
        setBtn(btnIslands, true, "on-islands");
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
