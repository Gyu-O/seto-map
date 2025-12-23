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
df_islands = pd.read_csv("islands.csv")
df_regions = pd.read_csv("regions.csv")

# =====================
# 地図
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
layer_area = folium.FeatureGroup(name="地域・島", show=False)  # ← 島＋地域をまとめる
layer_otafuku = folium.FeatureGroup(name="柄酒造", show=True)  # 常時表示

# サイズ
size = 8
size_otafuku = 10
size_arch = 8

# =====================
# SVG
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
# 酒蔵（柄酒造だけ別レイヤー＆サイズ）
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
        <div>
          <a href="{insta_url}" target="_blank" rel="noopener noreferrer">{insta_svg}</a>
        </div>
        '''
    popup_html += '</div>'

    marker = folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(this_size, this_size),
            icon_anchor=(this_size//2, this_size//2),
            popup_anchor=(0, -this_size//2),
            html=f"""
            <div style="
              width:{this_size}px;
              height:{this_size}px;
              background:{color};
              opacity:0.4;
            "></div>
            """
        ),
        popup=folium.Popup(popup_html, max_width=240)
    )

    (marker.add_to(layer_otafuku) if is_otafuku else marker.add_to(layer_sake))

# =====================
# 寺社
# =====================
for _, r in df_jinja.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r["url"]).strip() if "url" in r and pd.notna(r["url"]) else ""

    color = "#1a7f37"
    popup_html = name if url == "" else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size, size),
            icon_anchor=(size//2, size//2),
            popup_anchor=(0, -size//2),
            html=f"""<div style="width:{size}px;height:{size}px;background:{color};opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=220)
    ).add_to(layer_jinja)

# =====================
# 建築（黄色・2行目小さく）
# =====================
arch_color = "#f2c300"

def format_arch_name(raw):
    if "<br>" in raw:
        main, sub = raw.split("<br>", 1)
        return f'{main}<br><span style="font-size:11px;color:rgba(0,0,0,0.6);">{sub}</span>'
    return raw

for _, r in df_arch.iterrows():
    name = format_arch_name(str(r["name"]).strip())
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r["url"]).strip() if "url" in df_arch.columns and pd.notna(r.get("url","")) else ""

    title_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>' if url else name

    popup_html = f'''
    <div style="text-align:center;font-size:13px;line-height:1.35;">
      <div>{title_html}</div>
    </div>
    '''

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_arch, size_arch),
            icon_anchor=(size_arch//2, size_arch//2),
            popup_anchor=(0, -size_arch//2),
            html=f"""<div style="width:{size_arch}px;height:{size_arch}px;background:{arch_color};opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=280)
    ).add_to(layer_arch)

# =====================
# 地域・島（濃いグレー）
# - 島：●（塗りつぶし）
# - 地域：◎（外円＋内円の二重丸）
# =====================
area_color = "#3a3a3a"

# 島：●
for _, r in df_islands.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    folium.CircleMarker(
        location=[lat, lon],
        radius=3,            # ●の大きさ
        color=area_color,
        weight=0,
        fill=True,
        fill_color=area_color,
        fill_opacity=0.65,
        popup=folium.Popup(name, max_width=220)
    ).add_to(layer_area)

# 地域：◎（二重丸）
for _, r in df_regions.iterrows():
    name = str(r["name"]).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    # 外側の輪
    folium.CircleMarker(
        location=[lat, lon],
        radius=4.5,
        color=area_color,
        weight=2,
        fill=False,
        opacity=0.65
    ).add_to(layer_area)

    # 内側の輪（popupはこちらに）
    folium.CircleMarker(
        location=[lat, lon],
        radius=2,
        color=area_color,
        weight=2,
        fill=False,
        opacity=0.65,
        popup=folium.Popup(name, max_width=220)
    ).add_to(layer_area)

# =====================
# 地図に追加
# =====================
layer_sake.add_to(m)
layer_jinja.add_to(m)
layer_arch.add_to(m)
layer_area.add_to(m)
layer_otafuku.add_to(m)

# =====================
# 凡例UI（スマホ時は縮小）
# =====================
sake_var = layer_sake.get_name()
jinja_var = layer_jinja.get_name()
arch_var = layer_arch.get_name()
area_var = layer_area.get_name()
map_var = m.get_name()

template = f"""
{{% macro html(this, kwargs) %}}
<style>
.toggle-box {{
  position:absolute; top:12px; right:12px; z-index:9999;
  background:rgba(255,255,255,0.92);
  border:1px solid rgba(0,0,0,0.15);
  border-radius:10px; padding:10px; min-width:150px;
  box-shadow:0 8px 24px rgba(0,0,0,0.12);
  font-family:system-ui, sans-serif;
}}
.toggle-title {{ font-size:12px; color:rgba(0,0,0,0.45); padding-bottom:6px; }}
.toggle-item {{ display:flex; align-items:center; gap:10px; padding:8px; border-radius:8px; cursor:pointer; user-select:none; }}
.toggle-item:hover {{ background:rgba(0,0,0,0.04); }}
.sq {{ width:10px; height:10px; border-radius:2px; background:rgba(160,160,160,0.25); }}
.label {{ font-size:13px; color:rgba(0,0,0,0.78); }}

.on-otafuku .sq {{ background:rgba(196,0,0,0.5); }}
.on-sake .sq {{ background:rgba(0,102,204,0.5); }}
.on-jinja .sq {{ background:rgba(26,127,55,0.5); }}
.on-arch .sq {{ background:rgba(242,195,0,0.5); }}
.on-area .sq {{ background:rgba(58,58,58,0.55); }}

.toggle-static {{ cursor:default; }}
.toggle-static:hover {{ background:transparent; }}

/* 📱 スマホ用 */
@media (max-width:600px) {{
  .toggle-box {{ top:8px; right:8px; padding:6px; min-width:110px; opacity:0.85; }}
  .toggle-title {{ font-size:10px; padding-bottom:4px; }}
  .toggle-item {{ padding:5px 6px; gap:6px; }}
  .label {{ font-size:11px; }}
  .sq {{ width:8px; height:8px; }}
}}
</style>

<div class="toggle-box" id="customToggle">
  <div class="toggle-title">Layers</div>
  <div class="toggle-item toggle-static on-otafuku"><span class="sq"></span><span class="label">柄酒造</span></div>
  <div class="toggle-item" id="btn-sake"><span class="sq"></span><span class="label">酒蔵</span></div>
  <div class="toggle-item" id="btn-jinja"><span class="sq"></span><span class="label">寺社</span></div>
  <div class="toggle-item" id="btn-arch"><span class="sq"></span><span class="label">建築</span></div>
  <div class="toggle-item" id="btn-area"><span class="sq"></span><span class="label">地域・島</span></div>
</div>

<script>
(function(){{
  function init() {{
    var map = {map_var};
    var ls = {sake_var}, lj = {jinja_var}, la = {arch_var}, larea = {area_var};
    var bs=document.getElementById("btn-sake"),
        bj=document.getElementById("btn-jinja"),
        ba=document.getElementById("btn-arch"),
        br=document.getElementById("btn-area"),
        box=document.getElementById("customToggle");
    if(!bs||!bj||!ba||!br||!box||typeof map==="undefined"){{setTimeout(init,50);return;}}
    if(window.L&&L.DomEvent){{L.DomEvent.disableClickPropagation(box);L.DomEvent.disableScrollPropagation(box);}}
    function set(b,on,c){{on?b.classList.add(c):b.classList.remove(c);}}
    set(bs,map.hasLayer(ls),"on-sake");
    set(bj,map.hasLayer(lj),"on-jinja");
    set(ba,map.hasLayer(la),"on-arch");
    set(br,map.hasLayer(larea),"on-area");
    bs.onclick=function(){{map.hasLayer(ls)?(map.removeLayer(ls),set(bs,false,"on-sake")):(map.addLayer(ls),set(bs,true,"on-sake"));}};
    bj.onclick=function(){{map.hasLayer(lj)?(map.removeLayer(lj),set(bj,false,"on-jinja")):(map.addLayer(lj),set(bj,true,"on-jinja"));}};
    ba.onclick=function(){{map.hasLayer(la)?(map.removeLayer(la),set(ba,false,"on-arch")):(map.addLayer(la),set(ba,true,"on-arch"));}};
    br.onclick=function(){{map.hasLayer(larea)?(map.removeLayer(larea),set(br,false,"on-area")):(map.addLayer(larea),set(br,true,"on-area"));}};
  }}
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
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
