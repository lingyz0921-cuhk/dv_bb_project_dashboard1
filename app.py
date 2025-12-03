import streamlit as st
import pandas as pd
import re
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Sunburst
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from streamlit_echarts import st_pyecharts
import plotly.express as px
import os
from pypinyin import lazy_pinyin # 新增导入 pypinyin

# ==========================================
# 0. 全局配置与颜色定义
# ==========================================
COLOR_BLUE = "#5470c6"
COLOR_YELLOW = "#fac858"
COLOR_BG = "#ffffff"

st.set_page_config(
    page_title="CHFS China Household Debt Analysis | Dashboard", # 标题调整
    page_icon="🇨🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #5470c6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {font-family: 'Microsoft YaHei', sans-serif; color: #333;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 核心字典：城市代码映射与坐标 (保持正确版本)
# ==========================================
# (代码映射表与坐标字典保持不变，为节省篇幅此处折叠，请保留原有的完整字典)
COMPREHENSIVE_CITY_CODE_MAP = {
    20130201: '北京', 2013020101: '北京', 2013020102: '北京', 2013020103: '北京',
    20110201: '上海', 2011020101: '上海', 2011020102: '上海',
    20132601: '天津', 2013260101: '天津', 2013260102: '天津',
    20131601: '重庆', 2013160101: '重庆', 2013160102: '重庆',
    20170301: '石家庄', 2017030101: '石家庄', 20170307: '唐山', 2017030701: '唐山',
    20170308: '秦皇岛', 2017030801: '秦皇岛', 20170314: '保定', 2017031401: '保定',
    20131001: '太原', 2013100101: '太原', 20131002: '大同', 2013100201: '大同',
    20130501: '呼和浩特', 2013050101: '呼和浩特', 20130509: '包头', 2013050901: '包头',
    20170601: '沈阳', 2017060101: '沈阳', 2017060111: '大连', 201706111: '大连',
    20170701: '长春', 2017070101: '长春', 20170702: '吉林', 2017070201: '吉林',
    20170801: '哈尔滨', 2017080101: '哈尔滨', 20170802: '齐齐哈尔', 2017080201: '齐齐哈尔',
    20170803: '鸡西', 2017080301: '鸡西', 2017080302: '鸡西', 20110901: '哈尔滨',
    20110902: '哈尔滨', 2011090201: '哈尔滨', 2011090202: '哈尔滨',
    20171001: '南京', 2017100101: '南京', 20171005: '苏州', 2017100501: '苏州',
    2017100503: '苏州',
    20171101: '杭州', 2017110101: '杭州', 2017110106: '宁波', 2017110601: '宁波',
    20130901: '合肥', 2013090101: '合肥', 20130902: '芜湖', 2013090201: '芜湖',
    20171201: '福州', 2017120101: '福州', 20171202: '厦门', 2017120201: '厦门',
    20130801: '南昌', 2013080101: '南昌', 20130802: '景德镇', 2013080201: '景德镇',
    20171301: '济南', 2017130101: '济南', 20171302: '青岛', 2017130201: '青岛',
    20131101: '郑州', 2013110101: '郑州', 2013110103: '郑州', 20131102: '开封', 2013110201: '开封',
    20131201: '武汉', 2013120101: '武汉', 20171701: '武汉', 2017170101: '武汉',
    20131301: '长沙', 2013130101: '长沙', 20131302: '株洲', 2013130201: '株洲',
    20171901: '广州', 2017190101: '广州', 20171914: '深圳', 2017191401: '深圳',
    20150503: '广州', 20150508: '深圳',
    20130701: '南宁', 2013070101: '南宁', 20130704: '柳州', 2013070401: '柳州',
    20110501: '南宁', 2011050101: '南宁',
    20172001: '海口', 2017200101: '海口', 20172002: '三亚', 2017200201: '三亚',
    20131701: '成都', 2013170101: '成都', 20131703: '自贡', 2013170301: '自贡',
    20172301: '成都', 20172317: '绵阳', 2017231701: '绵阳', 2017231706: '绵阳',
    20131501: '贵阳', 2013150101: '贵阳', 20131502: '六盘水', 2013150201: '六盘水',
    20131401: '昆明', 2013140101: '昆明', 20131402: '曲靖', 2013140201: '曲靖',
    20130201: '拉萨', 2013020101: '拉萨', 2013020103: '拉萨',
    20131801: '西安', 2013180101: '西安', 20131802: '铜川', 2013180201: '铜川',
    20132305: '西安', 2013230501: '西安',
    20130401: '兰州', 2013040101: '兰州', 20130402: '嘉峪关', 2013040201: '嘉峪关',
    20110301: '兰州', 2011030101: '兰州', 20172801: '兰州', 2017280101: '兰州',
    20172810: '天水', 2017281001: '天水',
    20130301: '西宁', 2013030101: '西宁', 20130304: '海东', 2013030401: '海东',
    20131901: '银川', 2013190101: '银川', 20131904: '石嘴山', 2013190401: '石嘴山',
    20130601: '乌鲁木齐', 2013060101: '乌鲁木齐', 20130603: '克拉玛依', 2013060301: '克拉玛依',
    20192304: '广州', 20192101: '深圳', 20192102: '珠海', 20130106: '北京',
    20132802: '上海', 20151709: '杭州', 20152901: '南京', 20150103: '武汉',
    20132205: '西安', 20172501: '成都', 20191005: '重庆', 20152102: '天津',
    20152106: '大连', 20132901: '青岛', 20110805: '沈阳', 20132501: '长春',
    20132004: '哈尔滨', 20111301: '石家庄', 20150108: '太原', 20110404: '郑州',
    20110402: '长沙', 20191001: '福州', 20131302: '南昌', 20111202: '合肥',
    20152304: '宁波', 20191603: '厦门', 20150606: '济南', 20132804: '苏州',
    20150906: '无锡'
}

PROVINCE_COORDS = {
    "北京": [116.40, 39.90], "天津": [117.20, 39.12], "河北": [114.48, 38.03],
    "山西": [112.53, 37.87], "内蒙古": [111.65, 40.82], "辽宁": [123.38, 41.80],
    "吉林": [125.35, 43.88], "黑龙江": [126.63, 45.75], "上海": [121.48, 31.22],
    "江苏": [118.78, 32.04], "浙江": [120.19, 30.26], "安徽": [117.27, 31.86],
    "福建": [119.30, 26.08], "江西": [115.89, 28.68], "山东": [117.00, 36.65],
    "河南": [113.65, 34.76], "湖北": [114.31, 30.52], "湖南": [113.00, 28.21],
    "广东": [113.23, 23.16], "广西": [108.33, 22.84], "海南": [110.35, 20.02],
    "重庆": [106.54, 29.59], "四川": [104.06, 30.67], "贵州": [106.71, 26.57],
    "云南": [102.73, 25.04], "西藏": [91.11, 29.97], "陕西": [108.95, 34.27],
    "甘肃": [103.73, 36.03], "青海": [101.74, 36.56], "宁夏": [106.27, 38.47],
    "新疆": [87.68, 43.77], "香港": [114.17, 22.28], "澳门": [113.54, 22.19],
    "台湾": [121.50, 25.03]
}

# ==========================================
# 2. 数据处理与清洗函数
# ==========================================

# --- 拼音转换辅助函数 ---
def chinese_to_pinyin(text, sep='', capitalize_first=True, remove_suffixes=True): # 新增 remove_suffixes 参数
    """
    将字符串中的连续中文段翻译成拼音：
    - sep: 拼音音节间分隔符，''（连写）或 ' '（空格分开）
    - capitalize_first: 是否将连续中文段第一个字母大写（便于显示）
    - remove_suffixes: 是否移除常见的行政区划后缀 (sheng, shi)
    """
    if text is None:
        return None
    s = str(text)
    # 保留非中文段，单独转换连续中文段
    parts = re.split(r'([\u4e00-\u9fff]+)', s)
    out_parts = []
    for p in parts:
        if re.match(r'^[\u4e00-\u9fff]+$', p):
            pinyin = sep.join(lazy_pinyin(p))
            if capitalize_first and pinyin:
                # 确保转换后首字母大写，其余小写，例如 "Beijing" 而非 "beijing" 或 "BEIJING"
                pinyin = pinyin.capitalize()
            out_parts.append(pinyin)
        else:
            out_parts.append(p)

    final_pinyin = ''.join(out_parts)

    if remove_suffixes:
        # 移除常见的行政区划拼音后缀
        final_pinyin = re.sub(r'(Sheng|Shi|Qu|Xian|Zizhiqu|Diqu)$', '', final_pinyin, flags=re.IGNORECASE)
        # 对于直辖市，可能转换后直接就是城市名，不需要移除后缀
        # 比如 "Beijing Shi" -> "Beijing"
        # 对于省份，比如 "Guangdong Sheng" -> "Guangdong"
    return final_pinyin

# --- 关键清洗函数：应用新的映射逻辑 ---
def convert_city_name_advanced(val):
    if pd.isna(val): return None
    val_str = str(val).strip()
    if re.search(r'[\u4e00-\u9fff]', val_str):
        clean_name = re.sub(r'[市县地区壮族回族维吾尔自治区省]$', '', val_str)
        clean_name = clean_name.replace('广西壮族', '广西').replace('内蒙古', '内蒙古')
        clean_name = clean_name.replace('新疆维吾尔', '新疆').replace('宁夏回族', '宁夏')
        return clean_name
    try:
        code_val = float(val_str)
        code_int = int(code_val)
        mapped_name = COMPREHENSIVE_CITY_CODE_MAP.get(code_int)
        if mapped_name: return mapped_name
        if '.' in val_str:
            code_parts = val_str.split('.')
            if len(code_parts) == 2:
                main_code = int(code_parts[0][:6])
                mapped_name = COMPREHENSIVE_CITY_CODE_MAP.get(main_code)
                if mapped_name: return mapped_name
    except (ValueError, TypeError):
        pass
    if re.search(r'\d+[\u4e00-\u9fff]+', val_str):
        chinese_part = re.findall(r'[\u4e00-\u9fff]+', val_str)[0]
        clean_name = re.sub(r'[市县地区壮族回族维吾尔自治区省]$', '', chinese_part)
        return clean_name
    return None

def clean_city_name_for_map(name):
    if pd.isna(name): return None
    name_str = str(name).strip()
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', name_str)
    if not chinese_chars: return None
    clean_name = chinese_chars[0]
    if clean_name in COMPREHENSIVE_CITY_COORDS: return clean_name
    for standard_name in COMPREHENSIVE_CITY_COORDS.keys():
        if clean_name in standard_name or standard_name in clean_name:
            return standard_name
    for suffix in ['市', '州', '盟']:
        candidate = clean_name + suffix
        if candidate in COMPREHENSIVE_CITY_COORDS: return candidate
    if len(clean_name) >= 2: return clean_name
    return None

@st.cache_data
def load_and_clean_data(master_file, hh_file):
    try:
        # 只读取需要的列
        master_cols = ['hhid', 'rural', 'total_debt', 'total_asset', 'weight_hh', 'total_income',
                       'city_lab', 'city_level', 'region', 'prov']
        hh_cols = ['hhid', 'house01num']

        master = pd.read_csv(master_file, low_memory=False, usecols=lambda x: x in master_cols)
        hh = pd.read_csv(hh_file, low_memory=False, usecols=lambda x: x in hh_cols)
        df = master.merge(hh[['hhid', 'house01num']], on='hhid', how='left')

        numeric_cols = ['rural', 'total_debt', 'total_asset', 'weight_hh', 'total_income']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df[df['weight_hh'] > 0].copy()
        df['total_debt'] = df['total_debt'].fillna(0).clip(lower=0)
        df['total_income'] = df['total_income'].fillna(0).clip(lower=0)

        if 'city_lab' in df.columns:
            df['city_raw'] = df['city_lab']
            df['city_mapped'] = df['city_lab'].apply(convert_city_name_advanced)
            df['final_city_name'] = df['city_mapped'].apply(clean_city_name_for_map)
        else:
            df['final_city_name'] = None

        if 'city_level' in df.columns:
            def map_city_tier(level):
                if pd.isna(level): return None
                level = str(level).strip()
                if '一线' in level: return 'Tier 1 / New Tier 1'
                elif '二线' in level: return 'Tier 2'
                elif '三线' in level or '以下' in level or '非一线' in level: return 'Tier 3 & Below'
                return 'Other'
            df['tier_label'] = df['city_level'].apply(map_city_tier)

        if 'region' in df.columns:
             region_mapping = {'东部': 'East', '中部': 'Central', '西部': 'West', '东北': 'Northeast'}
             df['region_en'] = df['region'].map(region_mapping).fillna(df['region'])

        # --- 新增：生成拼音列 ---
        if 'final_city_name' in df.columns:
            df['final_city_pinyin'] = df['final_city_name'].apply(lambda x: chinese_to_pinyin(x, sep='', capitalize_first=True, remove_suffixes=True))
        else:
            df['final_city_pinyin'] = None

        if 'prov' in df.columns:
            df['prov_pinyin'] = df['prov'].apply(lambda x: chinese_to_pinyin(x, sep='', capitalize_first=True, remove_suffixes=True))
        else:
            df['prov_pinyin'] = None
        # --- 结束新增 ---

        return df
    except Exception as e:
        st.error(f"Data loading failed: {e}") # 错误提示改为英文
        return None

# ==========================================
# 3. 图表生成函数
# ==========================================

AXIS_GRAY = "#6E7079"
LEFT_AXIS_NAME = "Avg Debt (10k RMB)" # 轴名称调整
RIGHT_AXIS_NAME = "D/I Ratio"

def plot_urban_rural(df):
    """图1"""
    df_rural = df.groupby('rural', group_keys=False).apply(
        lambda x: pd.Series({
            'avg_debt': (x['total_debt'] * x['weight_hh']).sum() / x['weight_hh'].sum(),
            'avg_income': (x['total_income'] * x['weight_hh']).sum() / x['weight_hh'].sum(),
        }), include_groups=False
    ).reset_index()

    df_rural['avg_debt_10k'] = df_rural['avg_debt'] / 10000
    df_rural['d_i_ratio'] = df_rural['avg_debt'] / df_rural['avg_income']
    df_rural['rural_name'] = df_rural['rural'].map({0: 'Urban', 1: 'Rural'})

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(df_rural['rural_name'].tolist())
        .add_yaxis(LEFT_AXIS_NAME, df_rural['avg_debt_10k'].round(2).tolist(), yaxis_index=0, color=COLOR_BLUE, bar_width="40%")
        .extend_axis(
            yaxis=opts.AxisOpts(
                name=RIGHT_AXIS_NAME, type_="value", min_=0, position="right",
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=AXIS_GRAY)),
                name_location="end"
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Urban vs. Rural: Debt Burden & Risk"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                name=LEFT_AXIS_NAME, name_location="end",
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=AXIS_GRAY))
            )
        )
    )
    line = (
        Line()
        .add_xaxis(df_rural['rural_name'].tolist())
        .add_yaxis(RIGHT_AXIS_NAME, df_rural['d_i_ratio'].round(2).tolist(), yaxis_index=1, z=10, color=COLOR_YELLOW, symbol="circle", symbol_size=8, linestyle_opts=opts.LineStyleOpts(width=3))
    )
    return bar.overlap(line)

def plot_regional_stack(df):
    """图2"""
    if 'region_en' not in df.columns: return None

    # 修正：确保聚合结果生成了名为 'avg' 的列
    df_agg = df.groupby(['region_en', 'rural'], group_keys=False).apply(
        lambda x: (x['total_debt'] * x['weight_hh']).sum() / x['weight_hh'].sum()
    ).reset_index(name='avg') # <--- 这里加上 name='avg'

    pivot = df_agg.pivot(index='region_en', columns='rural', values='avg').fillna(0)
    regions = pivot.index.tolist()
    urban_data = (pivot[0] / 10000).round(2).tolist()
    rural_data = (pivot[1] / 10000).round(2).tolist()

    df_ratio = df.groupby('region_en', group_keys=False).apply(
        lambda x: pd.Series({
            'total_w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'total_w_income': (x['total_income'] * x['weight_hh']).sum()
        })
    ).reset_index()

    df_ratio = df_ratio.set_index('region_en').reindex(regions).reset_index()
    df_ratio['d_i_ratio'] = df_ratio['total_w_debt'] / df_ratio['total_w_income']
    ratio_data = df_ratio['d_i_ratio'].round(2).tolist()

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(regions)
        .add_yaxis("Urban Debt (10k)", urban_data, stack="stack1", color=COLOR_BLUE, bar_width="40%") # 图例调整
        .add_yaxis("Rural Debt (10k)", rural_data, stack="stack1", color="#72b0ea") # 图例调整
        .extend_axis(
            yaxis=opts.AxisOpts(
                name=RIGHT_AXIS_NAME, type_="value", min_=0, position="right", name_location="end",
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=AXIS_GRAY)),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
                splitline_opts=opts.SplitLineOpts(is_show=False)
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Regional Debt Composition & Risk Level"),
            yaxis_opts=opts.AxisOpts(
                name=LEFT_AXIS_NAME, name_location="end",
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=AXIS_GRAY))
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_top="0%")
        )
    )

    line = (
        Line()
        .add_xaxis(regions)
        .add_yaxis(
            RIGHT_AXIS_NAME, ratio_data, yaxis_index=1, color=COLOR_YELLOW,
            symbol="circle", symbol_size=8, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=3), z=10
        )
    )
    return bar.overlap(line)

def plot_china_map_plotly(df):
    """图3"""
    df_prov = df.groupby('prov', group_keys=False).apply(
        lambda x: pd.Series({
            'avg_debt': (x['total_debt'] * x['weight_hh']).sum() / x['weight_hh'].sum(),
            'total_w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'total_w_income': (x['total_income'] * x['weight_hh']).sum(),
            'prov_pinyin_display': x['prov_pinyin'].iloc[0] if 'prov_pinyin' in x.columns and not x['prov_pinyin'].empty else None # 取第一个拼音名
        }), include_groups=False
    ).reset_index()

    df_prov['d_i_ratio'] = df_prov['total_w_debt'] / df_prov['total_w_income']
    df_prov['avg_debt_10k'] = (df_prov['avg_debt'] / 10000).round(2)
    df_prov['ratio_display'] = df_prov['d_i_ratio'].round(2)

    def get_lat_lon(prov_name):
        name_str = str(prov_name)
        for k, v in PROVINCE_COORDS.items():
            if k in name_str: return pd.Series([v[1], v[0]])
        return pd.Series([None, None])

    df_prov[['lat', 'lon']] = df_prov['prov'].apply(get_lat_lon)
    df_plot = df_prov.dropna(subset=['lat', 'lon', 'prov_pinyin_display']) # 确保拼音列不为空

    if df_plot.empty: return None

    # Hover name 使用拼音，hover_data 只显示拼音和数值
    fig = px.scatter_geo(
        df_plot, lat='lat', lon='lon', size='avg_debt_10k', color='ratio_display',
        hover_name='prov_pinyin_display', # 显示拼音
        # 彻底隐藏原始中文，只显示拼音显示名和数值
        hover_data={'prov_pinyin_display': True, 'avg_debt_10k': True, 'ratio_display': True, 'lat': False, 'lon': False},
        size_max=35, color_continuous_scale='RdYlBu_r',
        scope='asia', title="Provincial Debt Map: Volume vs. Risk"
    )
    fig.update_layout(
        geo=dict(center=dict(lat=35, lon=105), projection_scale=2.5, showland=True, landcolor="#f4f4f4", showcountries=True),
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar=dict(title="D/I Ratio")
    )
    return fig

def plot_city_tier_boxplot(df):
    """
    图4: [优化版] 城市层级 - 家庭负债金额分布 (Total Debt Distribution)
    改动：从 Ratio 改为 绝对金额，以展示明显的层级差异
    """
    if 'tier_label' not in df.columns: return None

    # 1. 数据准备
    df_plot = df[df['tier_label'] != 'Other'].copy()

    # 2. 数据清洗：只保留有负债的家庭
    df_valid = df_plot[df_plot['total_debt'] > 0]

    if df_valid.empty: return None

    # 3. 定义排序逻辑
    tier_order = ["Tier 1 / New Tier 1", "Tier 2", "Tier 3 & Below"]

    # 4. 绘制箱线图
    fig = px.box(
        df_valid,
        x="tier_label",
        y="total_debt",
        title="Distribution of Household Total Debt Amount (by City Tier)",
        color_discrete_sequence=[COLOR_BLUE], # 统一使用主题蓝
        category_orders={"tier_label": tier_order},
        notched=True
    )

    # 5. 样式优化
    fig.update_layout(
        height=400,
        xaxis_title="City Tier", # 增加X轴标题
        yaxis_title="Total Debt (RMB)",
        showlegend=False,
        yaxis=dict(
            gridcolor='#eee',
            zerolinecolor='#eee',
            # 设置显示范围：0 到 300万。
            range=[0, 3000000]
        )
    )

    return fig

def plot_city_rank(df):
    """图5: 城市排名 (Top黄色，Bottom绿色) - 字典兼容版"""
    if 'final_city_name' not in df.columns or 'final_city_pinyin' not in df.columns: return None
    df_valid = df.dropna(subset=['final_city_name', 'final_city_pinyin'])

    # 1. 数据计算
    df_city_agg = df_valid.groupby(['final_city_name', 'final_city_pinyin'], group_keys=False).apply(
        lambda x: pd.Series({
            'w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'w_weight': x['weight_hh'].sum()
        })
    ).reset_index()

    df_city_agg['weighted_avg_debt'] = df_city_agg['w_debt'] / df_city_agg['w_weight']
    df_city_agg = df_city_agg.sort_values('weighted_avg_debt', ascending=False)

    top5 = df_city_agg.head(5).reset_index(drop=True)
    bottom5 = df_city_agg.tail(5).sort_values('weighted_avg_debt', ascending=True).reset_index(drop=True)

    overall_val = (df_valid['total_debt'] * df_valid['weight_hh']).sum() / df_valid['weight_hh'].sum() / 10000

    # 2. X 轴标签 - 只显示拼音
    x_data = [f"Top{i+1}\n{row['final_city_pinyin']}" for i, row in top5.iterrows()] + \
             ["National\nAvg"] + \
             [f"Last{i+1}\n{row['final_city_pinyin']}" for i, row in bottom5.iterrows()]

    # 3. Y 轴数据 - 使用字典格式
    y_data_items = []

    COLOR_TOP = "#fac858"   # 黄色
    COLOR_AVG = "#c0c4c6"   # 灰色
    COLOR_BOT = "#91cc75"   # 绿色

    # Top 5 -> 黄色
    for val in (top5['weighted_avg_debt']/10000).tolist():
        y_data_items.append({
            "value": round(val, 2),
            "itemStyle": {"color": COLOR_TOP}
        })

    # National Avg -> 灰色
    y_data_items.append({
        "value": round(overall_val, 2),
        "itemStyle": {"color": COLOR_AVG}
    })

    # Bottom 5 -> 绿色
    for val in (bottom5['weighted_avg_debt']/10000).tolist():
        y_data_items.append({
            "value": round(val, 2),
            "itemStyle": {"color": COLOR_BOT}
        })

    # 4. 绘图
    c = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis(
            "Avg Debt (10k RMB)",
            y_data_items,  # 传入字典列表
            category_gap="30%"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="City Debt Ranking: Extremes vs. Average"),
            yaxis_opts=opts.AxisOpts(name="10k RMB"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30, font_size=10)), # 旋转标签以便显示
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return c

def plot_geo_debt_map_comprehensive(df):
    """图6: 城市债务地图"""
    if 'final_city_name' not in df.columns or 'final_city_pinyin' not in df.columns: return None

    df_city = df.groupby(['final_city_name', 'final_city_pinyin'], group_keys=False).apply(
        lambda x: pd.Series({
            'w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'w_income': (x['total_income'] * x['weight_hh']).sum(),
            'sum_weight': x['weight_hh'].sum()
        })
    ).reset_index()

    df_city['avg_debt'] = df_city['w_debt'] / df_city['sum_weight']
    df_city['d_i_ratio'] = df_city.apply(
        lambda x: x['w_debt'] / x['w_income'] if x['w_income'] > 0 else 0, axis=1
    )

    def get_lat_lon_city(city_name):
        if city_name in COMPREHENSIVE_CITY_COORDS:
            coords = COMPREHENSIVE_CITY_COORDS[city_name]
            return pd.Series([coords[1], coords[0]])
        return pd.Series([None, None])

    df_city[['lat', 'lon']] = df_city['final_city_name'].apply(get_lat_lon_city)
    df_plot = df_city.dropna(subset=['lat', 'lon', 'final_city_pinyin']) # 确保拼音列不为空

    if df_plot.empty: return None

    df_plot = df_plot.sort_values('avg_debt', ascending=False).head(80) # 限制显示城市数量，避免过载
    df_plot['avg_debt_10k'] = (df_plot['avg_debt'] / 10000).round(2)
    df_plot['Risk Ratio'] = df_plot['d_i_ratio'].round(2)

    fig = px.scatter_geo(
        df_plot,
        lat='lat',
        lon='lon',
        size='avg_debt_10k',
        color='Risk Ratio',
        hover_name='final_city_pinyin', # hover name 使用拼音
        # 彻底隐藏原始中文，只显示拼音显示名和数值
        hover_data={'final_city_pinyin': True, 'avg_debt_10k': True, 'Risk Ratio': True, 'lat': False, 'lon': False},
        size_max=25,
        color_continuous_scale='RdYlBu_r',
        scope='asia',
        title=f"Key City Debt Map (Size=Burden, Color=Risk)"
    )

    fig.update_layout(
        geo=dict(center=dict(lat=36, lon=104), projection_scale=3.0, showland=True, landcolor="#f4f4f4", showcountries=True, countrycolor="#dedede"),
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar=dict(title="D/I Ratio")
    )
    return fig

def plot_debt_sunburst(df):
    """图7: 旭日图"""
    df_sun = df.copy()
    if 'rural' in df_sun.columns:
        df_sun['rural_str'] = df_sun['rural'].map({0: 'Urban', 1: 'Rural'})
    else: return None

    required_cols = ['rural_str', 'region_en', 'prov_pinyin', 'tier_label'] # path中直接用拼音prov
    for col in required_cols:
        if col not in df_sun.columns: return None
        df_sun[col] = df_sun[col].fillna('Unknown')

    df_sun['weighted_debt'] = df_sun['total_debt'] * df_sun['weight_hh']
    df_agg = df_sun.groupby(required_cols)['weighted_debt'].sum().reset_index()

    fig = px.sunburst(
        df_agg, path=['rural_str', 'region_en', 'prov_pinyin', 'tier_label'], # path 调整，只用拼音
        values='weighted_debt',
        title="Hierarchical View: Where is the Total Debt Concentrated?",
        color='weighted_debt', color_continuous_scale='RdBu_r'
    )
    fig.update_layout(margin=dict(t=40, l=0, r=0, b=0), height=600)
    return fig

# ==========================================
# 5. 主程序逻辑
# ==========================================

with st.sidebar:
    st.header("📂 Data Source")
    DEFAULT_MASTER = "chfs2019_master_202112.csv"
    DEFAULT_HH = "chfs2019_hh_202112.csv"

    upload_files = st.file_uploader("Upload CSV Files (Optional)", type=['csv'], accept_multiple_files=True)
    master_path, hh_path = None, None

    if upload_files:
        for f in upload_files:
            if "master" in f.name: master_path = f
            if "hh" in f.name: hh_path = f

    if not master_path and os.path.exists("chfs2019_master_202112.csv"):
        master_path = "chfs2019_master_202112.csv"
        hh_path = "chfs2019_hh_202112.csv"
    elif not master_path and os.path.exists(DEFAULT_MASTER):
        master_path = DEFAULT_MASTER
        hh_path = DEFAULT_HH

    st.info("If no file is uploaded, default files from the repository will be loaded.") # 提示改为英文

st.title("🇨🇳CHFS-Based Analysis of Chinese Household Debt") # 标题调整
st.markdown("### Macro-Regional & City Analysis") # 副标题调整

if master_path and hh_path:
    with st.spinner("Loading and Processing Data..."):
        df = load_and_clean_data(master_path, hh_path)

    if df is not None:
        kpi_cols = st.columns(4)
        total_weight = df['weight_hh'].sum()
        weighted_avg_debt = (df['total_debt'] * df['weight_hh']).sum() / total_weight
        weighted_avg_income = (df['total_income'] * df['weight_hh']).sum() / total_weight
        debt_ratio = weighted_avg_debt / weighted_avg_income if weighted_avg_income > 0 else 0
        households_with_debt = df[df['total_debt'] > 0]['weight_hh'].sum() / total_weight

        kpi_cols[0].metric("Avg Household Debt", f"¥{weighted_avg_debt:,.0f}")
        kpi_cols[1].metric("Avg Household Income", f"¥{weighted_avg_income:,.0f}")
        kpi_cols[2].metric("Debt-to-Income Ratio", f"{debt_ratio:.1%}", delta_color="inverse")
        #kpi_cols[3].metric("Indebted Households", f"{households_with_debt:.1%}") # 暂时不显示这个

        st.markdown("---")

        # Row 1
        row1_col1, row1_col2 = st.columns([1, 1])
        with row1_col1:
            st.subheader("1. Urban vs Rural Debt & Risk")
            st_pyecharts(plot_urban_rural(df), height="400px")
        with row1_col2:
            st.subheader("2. Regional Debt & Risk")
            chart_reg = plot_regional_stack(df)
            if chart_reg: st_pyecharts(chart_reg, height="400px")

        # Row 2
        row2_col1, row2_col2 = st.columns([1, 1])
        with row2_col1:
            st.subheader("3. Provincial Debt & Risk Map ")
            fig_map = plot_china_map_plotly(df)
            if fig_map:
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No provincial data found.")

        with row2_col2:
            st.subheader("4. City Tier Leverage Distribution ")
            chart_tier = plot_city_tier_boxplot(df)
            if chart_tier:
                st.plotly_chart(chart_tier, use_container_width=True)
            else:
                st.info("Insufficient data for distribution analysis.")

        # Row 3
        st.markdown("---")
        st.subheader("5. Hierarchical Debt Distribution")
        st.markdown("**Hierarchy:** Urban/Rural > Region > Province > City Tier")

        chart_sun = plot_debt_sunburst(df)
        if chart_sun:
            st.plotly_chart(chart_sun, use_container_width=True)
        else:
            st.warning("Data missing for Sunburst Chart.")


        # Row 4
        row3_col1, row3_col2 = st.columns([1, 1])
        with row3_col1:
            st.subheader("6. Key City Debt & Risk Map")
            chart_geo = plot_geo_debt_map_comprehensive(df)
            if chart_geo:
                st.plotly_chart(chart_geo, use_container_width=True)
            else:
                st.info("Not enough city data matched to coordinates.")

        with row3_col2:
            st.subheader("7. City Debt Rankings (Top 5 vs Bottom 5)")
            chart_rank = plot_city_rank(df)
            if chart_rank: st_pyecharts(chart_rank, height="450px")

    else:
        st.error("Unable to process data. Please check file format.") # 错误提示改为英文
else:
    st.warning("⚠️ Data files not found. Please upload CSVs or ensure they are in the default path.") # 警告提示改为英文
