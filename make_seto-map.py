import pandas as pd
import folium
from folium.features import DivIcon
from branca.element import MacroElement, Template

print("RUNNING:", __file__)

# =====================
# 設定（ここだけで調整）
# =====================
NAME_ZOOM = 13  # このズーム以上で「全島が ●→name」に切り替わる

# =====================
# CSV読み込み
# =====================
df_sake    = pd.read_csv("sake.csv")
df_jinja   = pd.read_csv("jinja.csv")
df_arch    = pd.read_csv("architecture.csv")
df_art     = pd.read_csv("art.csv")
df_matsuri = pd.read_csv("matsuri.csv")
df_islands = pd.read_csv("islands.csv")   # min_zoom 列（任意）
df_regions = pd.read_csv("regions.csv")


# =====================
# 全CSV共通：lat/lon を「絶対落ちない」形に正規化
# =====================
def normalize_latlon(df: pd.DataFrame) -> pd.DataFrame:
    # 必須列を用意
    if "name" not in df.columns:
        df["name"] = ""
    if "lat" not in df.columns:
        df["lat"] = pd.NA
    if "lon" not in df.columns:
        df["lon"] = pd.NA
    if "url" not in df.columns:
        df["url"] = ""

    # 数値化（変換できないものは NaN）
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    # lat/lon が数値の行だけ残す
    df = df.dropna(subset=["lat", "lon"]).copy()
    return df


df_sake    = normalize_latlon(df_sake)
df_jinja   = normalize_latlon(df_jinja)
df_arch    = normalize_latlon(df_arch)
df_art     = normalize_latlon(df_art)
df_matsuri = normalize_latlon(df_matsuri)
df_islands = normalize_latlon(df_islands)
df_regions = normalize_latlon(df_regions)


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
layer_sake    = folium.FeatureGroup(name="酒蔵・醸造所", show=True)
layer_jinja   = folium.FeatureGroup(name="寺社", show=False)
layer_arch    = folium.FeatureGroup(name="建築", show=False)
layer_art     = folium.FeatureGroup(name="アート", show=False)
layer_matsuri = folium.FeatureGroup(name="祭り", show=False)
layer_area    = folium.FeatureGroup(name="地域・島", show=False)
layer_otafuku = folium.FeatureGroup(name="柄酒造", show=True)

# =====================
# サイズ
# =====================
size = 8
size_otafuku = 10
size_arch = 8
size_art = 8
size_matsuri = 9

# =====================
# 共通：ラベルHTML（regions と islands を完全に揃える）
# =====================
def label_html(name: str) -> str:
    name = str(name).strip()
    return f"""
    <div style="
      font-size:9px;
      color:rgba(0,0,0,0.6);
      white-space:nowrap;
      text-align:center;
      text-shadow:0 0 3px rgba(255,255,255,0.9);
      pointer-events:none;
    ">{name}</div>
    """

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
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    x_url = str(r.get("x_url", "")).strip()

    insta_url = ""
    if "instagram_url" in df_sake.columns and pd.notna(r.get("instagram_url", "")):
        insta_url = str(r.get("instagram_url", "")).strip()

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
        popup=folium.Popup(popup_html, max_width=240)
    )
    (marker.add_to(layer_otafuku) if is_otafuku else marker.add_to(layer_sake))

# =====================
# 寺社
# =====================
for _, r in df_jinja.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r.get("url", "")).strip() if pd.notna(r.get("url", "")) else ""

    color = "#1a7f37"
    popup_html = name if url == "" else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size, size),
            icon_anchor=(size // 2, size // 2),
            popup_anchor=(0, -size // 2),
            html=f"""<div style="width:{size}px;height:{size}px;background:{color};opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=220)
    ).add_to(layer_jinja)

# =====================
# 建築（黄色・2行目小さく）
# =====================
arch_color = "#f2c300"

def format_arch_name(raw: str) -> str:
    raw = str(raw).strip()
    if "<br>" in raw:
        main, sub = raw.split("<br>", 1)
        return f'{main}<br><span style="font-size:11px;color:rgba(0,0,0,0.6);">{sub}</span>'
    return raw

for _, r in df_arch.iterrows():
    name = format_arch_name(r.get("name", ""))
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r.get("url", "")).strip() if pd.notna(r.get("url", "")) else ""

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
            icon_anchor=(size_arch // 2, size_arch // 2),
            popup_anchor=(0, -size_arch // 2),
            html=f"""<div style="width:{size_arch}px;height:{size_arch}px;background:{arch_color};opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=280)
    ).add_to(layer_arch)

# =====================
# アート（紫）
# =====================
art_color = "#8e44ad"

for _, r in df_art.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r.get("url", "")).strip() if pd.notna(r.get("url", "")) else ""

    title_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>' if url else name
    popup_html = f'''
    <div style="text-align:center;font-size:13px;line-height:1.35;">
      <div>{title_html}</div>
    </div>
    '''

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_art, size_art),
            icon_anchor=(size_art // 2, size_art // 2),
            popup_anchor=(0, -size_art // 2),
            html=f"""<div style="width:{size_art}px;height:{size_art}px;background:{art_color};opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=280)
    ).add_to(layer_art)

# =====================
# 祭り（橙）
# =====================
matsuri_color = "#d16c00"

for _, r in df_matsuri.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r.get("url", "")).strip() if pd.notna(r.get("url", "")) else ""

    title_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>' if url else name
    popup_html = f'''
    <div style="text-align:center;font-size:13px;line-height:1.35;">
      <div>{title_html}</div>
    </div>
    '''

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_matsuri, size_matsuri),
            icon_anchor=(size_matsuri // 2, size_matsuri // 2),
            popup_anchor=(0, -size_matsuri // 2),
            html=f"""<div style="width:{size_matsuri}px;height:{size_matsuri}px;background:{matsuri_color};opacity:0.45;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=320)
    ).add_to(layer_matsuri)

# =====================
# 地域・島（濃いグレー）
# - 島：ズームで「dot / name / 非表示」を切り替え（min_zoom）
# - さらに zoom>=NAME_ZOOM で「全島が ●→name」
# - 地域：name 常時表示（トグル内）
# =====================
area_color = "#3a3a3a"
island_rules = []  # (dot_js, label_js, min_zoom_or_None)

for _, r in df_islands.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    min_zoom = None
    if "min_zoom" in df_islands.columns and pd.notna(r.get("min_zoom", "")) and str(r["min_zoom"]).strip() != "":
        min_zoom = int(float(r["min_zoom"]))

    dot = folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color=area_color,
        weight=0,
        fill=True,
        fill_color=area_color,
        fill_opacity=0.3,
        popup=folium.Popup(name, max_width=220)
    ).add_to(layer_area)

    label = folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(240, 24),
            icon_anchor=(120, 12),
            html=label_html(name)
        )
    ).add_to(layer_area)

    island_rules.append((dot.get_name(), label.get_name(), min_zoom))

for _, r in df_regions.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(240, 24),
            icon_anchor=(120, 12),
            html=label_html(name)
        )
    ).add_to(layer_area)

# =====================
# 地図に追加
# =====================
layer_sake.add_to(m)
layer_jinja.add_to(m)
layer_arch.add_to(m)
layer_art.add_to(m)
layer_matsuri.add_to(m)
layer_area.add_to(m)
layer_otafuku.add_to(m)

# =====================
# JS埋め込み用：island_rules
# =====================
def js_minzoom(v):
    return "null" if v is None else str(int(v))

island_rules_js = ", ".join([f"{{dot:{d}, label:{l}, minz:{js_minzoom(mz)}}}" for d, l, mz in island_rules])

# =====================
# 凡例UI（スマホ時は縮小）
# =====================
sake_var    = layer_sake.get_name()
jinja_var   = layer_jinja.get_name()
arch_var    = layer_arch.get_name()
art_var     = layer_art.get_name()
matsuri_var = layer_matsuri.get_name()
area_var    = layer_area.get_name()
map_var     = m.get_name()

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
.on-art  .sq {{ background:rgba(142,68,173,0.5); }}
.on-matsuri .sq {{ background:rgba(209,108,0,0.6); }}
.on-area .sq {{ background:rgba(58,58,58,0.55); }}

.toggle-static {{ cursor:default; }}
.toggle-static:hover {{ background:transparent; }}

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
  <div class="toggle-item" id="btn-sake"><span class="sq"></span><span class="label">酒蔵・醸造所</span></div>
  <div class="toggle-item" id="btn-jinja"><span class="sq"></span><span class="label">寺社</span></div>
  <div class="toggle-item" id="btn-arch"><span class="sq"></span><span class="label">建築</span></div>
  <div class="toggle-item" id="btn-art"><span class="sq"></span><span class="label">アート</span></div>
  <div class="toggle-item" id="btn-matsuri"><span class="sq"></span><span class="label">祭り</span></div>
  <div class="toggle-item" id="btn-area"><span class="sq"></span><span class="label">地域・島</span></div>
</div>

<script>
(function(){{
  function init() {{
    var map = {map_var};
    var ls = {sake_var}, lj = {jinja_var}, la = {arch_var}, lt = {art_var}, lm = {matsuri_var}, larea = {area_var};

    var bs=document.getElementById("btn-sake"),
        bj=document.getElementById("btn-jinja"),
        ba=document.getElementById("btn-arch"),
        bt=document.getElementById("btn-art"),
        bm=document.getElementById("btn-matsuri"),
        br=document.getElementById("btn-area"),
        box=document.getElementById("customToggle");

    if(!bs||!bj||!ba||!bt||!bm||!br||!box||typeof map==="undefined"){{setTimeout(init,50);return;}}
    if(window.L&&L.DomEvent){{L.DomEvent.disableClickPropagation(box);L.DomEvent.disableScrollPropagation(box);}}

    function set(b,on,c){{on?b.classList.add(c):b.classList.remove(c);}};

    set(bs,map.hasLayer(ls),"on-sake");
    set(bj,map.hasLayer(lj),"on-jinja");
    set(ba,map.hasLayer(la),"on-arch");
    set(bt,map.hasLayer(lt),"on-art");
    set(bm,map.hasLayer(lm),"on-matsuri");
    set(br,map.hasLayer(larea),"on-area");

    var NAME_ZOOM = {NAME_ZOOM};
    var islandRules = [{island_rules_js}];

    function applyIslandRules(){{
      if(!map.hasLayer(larea)) return;
      var z = map.getZoom();

      islandRules.forEach(function(r){{
        if(z >= NAME_ZOOM){{
          if(map.hasLayer(r.dot)) map.removeLayer(r.dot);
          if(!map.hasLayer(r.label)) r.label.addTo(map);
          return;
        }}

        if(r.minz !== null){{
          if(z < r.minz){{
            if(map.hasLayer(r.dot)) map.removeLayer(r.dot);
            if(map.hasLayer(r.label)) map.removeLayer(r.label);
          }} else {{
            if(map.hasLayer(r.dot)) map.removeLayer(r.dot);
            if(!map.hasLayer(r.label)) r.label.addTo(map);
          }}
        }} else {{
          if(!map.hasLayer(r.dot)) r.dot.addTo(map);
          if(map.hasLayer(r.label)) map.removeLayer(r.label);
        }}
      }});
    }}

    applyIslandRules();
    map.on("zoomend", applyIslandRules);

    bs.onclick=function(){{map.hasLayer(ls)?(map.removeLayer(ls),set(bs,false,"on-sake")):(map.addLayer(ls),set(bs,true,"on-sake"));}};
    bj.onclick=function(){{map.hasLayer(lj)?(map.removeLayer(lj),set(bj,false,"on-jinja")):(map.addLayer(lj),set(bj,true,"on-jinja"));}};
    ba.onclick=function(){{map.hasLayer(la)?(map.removeLayer(la),set(ba,false,"on-arch")):(map.addLayer(la),set(ba,true,"on-arch"));}};
    bt.onclick=function(){{map.hasLayer(lt)?(map.removeLayer(lt),set(bt,false,"on-art")):(map.addLayer(lt),set(bt,true,"on-art"));}};
    bm.onclick=function(){{map.hasLayer(lm)?(map.removeLayer(lm),set(bm,false,"on-matsuri")):(map.addLayer(lm),set(bm,true,"on-matsuri"));}};

    br.onclick=function(){{
      if(map.hasLayer(larea)) {{
        map.removeLayer(larea);
        set(br,false,"on-area");
      }} else {{
        map.addLayer(larea);
        set(br,true,"on-area");
        applyIslandRules();
      }}
    }};
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
