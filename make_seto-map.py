import pandas as pd
import folium
from folium.features import DivIcon
from branca.element import MacroElement, Template

print("RUNNING:", __file__)

# =====================
# 設定
# =====================
NAME_ZOOM = 13  # PC基準：このズーム以上で「全島がname表示」

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
# lat/lon 正規化（全CSV共通）
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
# 地図（ベース）
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
layer_otafuku = folium.FeatureGroup(name="柄酒造", show=True)  # 常時表示

# =====================
# サイズ
# =====================
size = 8
size_otafuku = 10
size_arch = 8
size_art = 8
size_matsuri = 9

# =====================
# 共通：ラベルHTML（regions と islands を揃える）
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
# 酒蔵（柄酒造だけ別レイヤー＆サイズ）
# =====================
for _, r in df_sake.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    x_url = ""
    if "x_url" in df_sake.columns and pd.notna(r.get("x_url", "")):
        x_url = str(r.get("x_url", "")).strip()

    insta_url = ""
    if "instagram_url" in df_sake.columns and pd.notna(r.get("instagram_url", "")):
        insta_url = str(r.get("instagram_url", "")).strip()

    is_otafuku = ("柄酒造" in name)
    color = "#c40000" if is_otafuku else "#0066cc"
    this_size = size_otafuku if is_otafuku else size

    title = f'<a href="{x_url}" target="_blank" rel="noopener noreferrer">{name}</a>' if x_url else name
    extra = ""
    if is_otafuku and insta_url:
        extra = f'<div style="margin-top:6px;"><a href="{insta_url}" target="_blank" rel="noopener noreferrer">Instagram</a></div>'

    popup_html = f"""
    <div style="text-align:center;font-size:13px;line-height:1.35;">
      <div>{title}</div>
      {extra}
    </div>
    """

    marker = folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(this_size, this_size),
            icon_anchor=(this_size // 2, this_size // 2),
            popup_anchor=(0, -this_size // 2),
            html=f"""<div style="width:{this_size}px;height:{this_size}px;background:{color};opacity:0.4;"></div>"""
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

    popup_html = name if not url else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size, size),
            icon_anchor=(size // 2, size // 2),
            popup_anchor=(0, -size // 2),
            html=f"""<div style="width:{size}px;height:{size}px;background:#1a7f37;opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=260)
    ).add_to(layer_jinja)

# =====================
# 建築（黄色）
# =====================
for _, r in df_arch.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r.get("url", "")).strip() if pd.notna(r.get("url", "")) else ""

    popup_html = name if not url else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_arch, size_arch),
            icon_anchor=(size_arch // 2, size_arch // 2),
            popup_anchor=(0, -size_arch // 2),
            html=f"""<div style="width:{size_arch}px;height:{size_arch}px;background:#f2c300;opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=320)
    ).add_to(layer_arch)

# =====================
# アート（紫）
# =====================
for _, r in df_art.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r.get("url", "")).strip() if pd.notna(r.get("url", "")) else ""

    popup_html = name if not url else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_art, size_art),
            icon_anchor=(size_art // 2, size_art // 2),
            popup_anchor=(0, -size_art // 2),
            html=f"""<div style="width:{size_art}px;height:{size_art}px;background:#8e44ad;opacity:0.4;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=320)
    ).add_to(layer_art)

# =====================
# 祭り（橙）
# =====================
for _, r in df_matsuri.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])
    url = str(r.get("url", "")).strip() if pd.notna(r.get("url", "")) else ""

    popup_html = name if not url else f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'

    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(size_matsuri, size_matsuri),
            icon_anchor=(size_matsuri // 2, size_matsuri // 2),
            popup_anchor=(0, -size_matsuri // 2),
            html=f"""<div style="width:{size_matsuri}px;height:{size_matsuri}px;background:#d16c00;opacity:0.45;"></div>"""
        ),
        popup=folium.Popup(popup_html, max_width=360)
    ).add_to(layer_matsuri)

# =====================
# 地域・島（濃いグレー）
# - 島：ズームで dot / name / 非表示 を切り替え（min_zoom）
# - zoom>=NAME_ZOOM で「全島 name」
# - スマホは NAME_ZOOM と min_zoom を -2 して広域で出す
# =====================
area_color = "#3a3a3a"
island_rules = []  # (dot_var, label_var, min_zoom_or_None)

for _, r in df_islands.iterrows():
    name = str(r.get("name", "")).strip()
    lat = float(r["lat"])
    lon = float(r["lon"])

    min_zoom = None
    if "min_zoom" in df_islands.columns and pd.notna(r.get("min_zoom", "")) and str(r.get("min_zoom", "")).strip() != "":
        try:
            min_zoom = int(float(r.get("min_zoom")))
        except Exception:
            min_zoom = None

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

# 地域：name 常時表示（トグル内）
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
# 地図に追加（順番重要）
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

island_rules_js = ", ".join(
    [f"{{dot:{d}, label:{l}, minz:{js_minzoom(mz)}}}" for d, l, mz in island_rules]
)

# =====================
# 右上 UI（Layers）＋ 島表示制御（スマホ調整込み）
# =====================
map_var = m.get_name()
sake_var = layer_sake.get_name()
jinja_var = layer_jinja.get_name()
arch_var = layer_arch.get_name()
art_var = layer_art.get_name()
matsuri_var = layer_matsuri.get_name()
area_var = layer_area.get_name()

template = f"""
{{% macro html(this, kwargs) %}}
<style>
.toggle-box {{
  position:absolute; top:12px; right:12px; z-index:9999;
  background:rgba(255,255,255,0.92);
  border:1px solid rgba(0,0,0,0.15);
  border-radius:10px; padding:10px; min-width:160px;
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
  .toggle-box {{ top:8px; right:8px; padding:6px; min-width:120px; opacity:0.88; }}
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
    var ls = {sake_var};
    var lj = {jinja_var};
    var larch = {arch_var};
    var lart = {art_var};
    var lm = {matsuri_var};
    var larea = {area_var};

    var bs=document.getElementById("btn-sake"),
        bj=document.getElementById("btn-jinja"),
        ba=document.getElementById("btn-arch"),
        bt=document.getElementById("btn-art"),
        bm=document.getElementById("btn-matsuri"),
        br=document.getElementById("btn-area"),
        box=document.getElementById("customToggle");

    if(!bs||!bj||!ba||!bt||!bm||!br||!box||typeof map==="undefined"){{setTimeout(init,50);return;}}

    if(window.L&&L.DomEvent){{L.DomEvent.disableClickPropagation(box);L.DomEvent.disableScrollPropagation(box);}}

    function set(b,on,c){{on?b.classList.add(c):b.classList.remove(c);}}

    // 初期状態の色
    set(bs,map.hasLayer(ls),"on-sake");
    set(bj,map.hasLayer(lj),"on-jinja");
    set(ba,map.hasLayer(larch),"on-arch");
    set(bt,map.hasLayer(lart),"on-art");
    set(bm,map.hasLayer(lm),"on-matsuri");
    set(br,map.hasLayer(larea),"on-area");

    // ===== スマホは広域で島名を出す =====
    var NAME_ZOOM_BASE = {NAME_ZOOM};
    var isMobile = window.matchMedia && window.matchMedia("(max-width: 600px)").matches;
    var NAME_ZOOM = isMobile ? (NAME_ZOOM_BASE - 2) : NAME_ZOOM_BASE;
    var mobileBoost = isMobile ? 2 : 0;

    var islandRules = [{island_rules_js}];

    function applyIslandRules(){{
      if(!map.hasLayer(larea)) return;
      var z = map.getZoom();

      islandRules.forEach(function(r){{
        // 全島name
        if(z >= NAME_ZOOM){{
          if(map.hasLayer(r.dot)) map.removeLayer(r.dot);
          if(!map.hasLayer(r.label)) r.label.addTo(map);
          return;
        }}

        // min_zoom 指定島
        if(r.minz !== null){{
          var minz = r.minz - mobileBoost;
          if(z < minz){{
            if(map.hasLayer(r.dot)) map.removeLayer(r.dot);
            if(map.hasLayer(r.label)) map.removeLayer(r.label);
          }} else {{
            if(map.hasLayer(r.dot)) map.removeLayer(r.dot);
            if(!map.hasLayer(r.label)) r.label.addTo(map);
          }}
        }} else {{
          // 通常島は dot
          if(!map.hasLayer(r.dot)) r.dot.addTo(map);
          if(map.hasLayer(r.label)) map.removeLayer(r.label);
        }}
      }});
    }}

    applyIslandRules();
    map.on("zoomend", applyIslandRules);

    // トグル
    bs.onclick=function(){{map.hasLayer(ls)?(map.removeLayer(ls),set(bs,false,"on-sake")):(map.addLayer(ls),set(bs,true,"on-sake"));}};
    bj.onclick=function(){{map.hasLayer(lj)?(map.removeLayer(lj),set(bj,false,"on-jinja")):(map.addLayer(lj),set(bj,true,"on-jinja"));}};
    ba.onclick=function(){{map.hasLayer(larch)?(map.removeLayer(larch),set(ba,false,"on-arch")):(map.addLayer(larch),set(ba,true,"on-arch"));}};
    bt.onclick=function(){{map.hasLayer(lart)?(map.removeLayer(lart),set(bt,false,"on-art")):(map.addLayer(lart),set(bt,true,"on-art"));}};
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
