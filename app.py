
import streamlit as st
import pandas as pd
import re
from pyecharts import options as opts
from pyecharts.charts import Bar, Line
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from streamlit_echarts import st_pyecharts
import plotly.express as px
import os

# ==========================================
# 0. 全局配置与颜色定义
# ==========================================
COLOR_BLUE = "#5470c6"
COLOR_YELLOW = "#fac858"
COLOR_BG = "#ffffff"

st.set_page_config(
    page_title="中国家庭债务分析大屏 | CHFS Dashboard",
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
    20130201: 'Beijing', 2013020101: 'Beijing', 2013020102: 'Beijing', 2013020103: 'Beijing',
    20110201: 'Shanghai', 2011020101: 'Shanghai', 2011020102: 'Shanghai',
    20132601: 'Tianjin', 2013260101: 'Tianjin', 2013260102: 'Tianjin',
    20131601: 'Chongqing', 2013160101: 'Chongqing', 2013160102: 'Chongqing',
    20170301: 'Shijiazhuang', 2017030101: 'Shijiazhuang', 20170307: 'Tangshan', 2017030701: 'Tangshan',
    20170308: 'Qinhuangdao', 2017030801: 'Qinhuangdao', 20170314: 'Baoding', 2017031401: 'Baoding',
    20131001: 'Taiyuan', 2013100101: 'Taiyuan', 20131002: 'Datong', 2013100201: 'Datong',
    20130501: 'Huhehaote', 2013050101: 'Huhehaote', 20130509: 'Baotou', 2013050901: 'Baotou',
    20170601: 'Shenyang', 2017060101: 'Shenyang', 2017060111: 'Dalian', 201706111: 'Dalian',
    20170701: 'Changchun', 2017070101: 'Changchun', 20170702: 'Jilin', 2017070201: 'Jilin',
    20170801: 'Harbin', 2017080101: 'Harbin', 20170802: 'Qiqihar', 2017080201: 'Qiqihar',
    20170803: 'Jixi', 2017080301: 'Jixi', 2017080302: 'Jixi', 20110901: 'Harbin',
    20110902: 'Harbin', 2011090201: 'Harbin', 2011090202: 'Harbin',
    20171001: 'Nanjing', 2017100101: 'Nanjing', 20171005: 'Suzhou', 2017100501: 'Suzhou',
    2017100503: 'Suzhou',
    20171101: 'Hangzhou', 2017110101: 'Hangzhou', 2017110106: 'Ningbo', 2017110601: 'Ningbo',
    20130901: 'Hefei', 2013090101: 'Hefei', 20130902: 'Wuhu', 2013090201: 'Wuhu',
    20171201: 'Fuzhou', 2017120101: 'Fuzhou', 20171202: 'Xiamen', 2017120201: 'Xiamen',
    20130801: 'Nanchang', 2013080101: 'Nanchang', 20130802: 'Jingdezhen', 2013080201: 'Jingdezhen',
    20171301: 'Jinan', 2017130101: 'Jinan', 20171302: 'Qingdao', 2017130201: 'Qingdao',
    20131101: 'Zhengzhou', 2013110101: 'Zhengzhou', 2013110103: 'Zhengzhou', 20131102: 'Kaifeng', 2013110201: 'Kaifeng',
    20131201: 'Wuhan', 2013120101: 'Wuhan', 20171701: 'Wuhan', 2017170101: 'Wuhan',
    20131301: 'Changsha', 2013130101: 'Changsha', 20131302: 'Zhuzhou', 2013130201: 'Zhuzhou',
    20171901: 'Guangzhou', 2017190101: 'Guangzhou', 20171914: 'Shenzhen', 2017191401: 'Shenzhen',
    20150503: 'Guangzhou', 20150508: 'Shenzhen',
    20130701: 'Nanning', 2013070101: 'Nanning', 20130704: 'Liuzhou', 2013070401: 'Liuzhou',
    20110501: 'Nanning', 2011050101: 'Nanning',
    20172001: 'Haikou', 2017200101: 'Haikou', 20172002: 'Sanya', 2017200201: 'Sanya',
    20131701: 'Chengdu', 2013170101: 'Chengdu', 20131703: 'Zigong', 2013170301: 'Zigong',
    20172301: 'Chengdu', 20172317: 'Mianyang', 2017231701: 'Mianyang', 2017231706: 'Mianyang',
    20131501: 'Guiyang', 2013150101: 'Guiyang', 20131502: 'Liupanshui', 2013150201: 'Liupanshui',
    20131401: 'Kunming', 2013140101: 'Kunming', 20131402: 'Qujing', 2013140201: 'Qujing',
    20130201: 'Lasa', 2013020101: 'Lasa', 2013020103: 'Lasa',
    20131801: 'Xian', 2013180101: 'Xian', 20131802: 'Tongchuan', 2013180201: 'Tongchuan',
    20132305: 'Xian', 2013230501: 'Xian',
    20130401: 'Lanzhou', 2013040101: 'Lanzhou', 20130402: 'Jiayuguan', 2013040201: 'Jiayuguan',
    20110301: 'Lanzhou', 2011030101: 'Lanzhou', 20172801: 'Lanzhou', 2017280101: 'Lanzhou',
    20172810: 'Tianshui', 2017281001: 'Tianshui',
    20130301: 'Xining', 2013030101: 'Xining', 20130304: 'Haidong', 2013030401: 'Haidong',
    20131901: 'Yinchuan', 2013190101: 'Yinchuan', 20131904: 'Shizuishan', 2013190401: 'Shizuishan',
    20130601: 'Urumqi', 2013060101: 'Urumqi', 20130603: 'Karamay', 2013060301: 'Karamay',
    20192304: 'Guangzhou', 20192101: 'Shenzhen', 20192102: 'Zhuhai', 20130106: 'Beijing',
    20132802: 'Shanghai', 20151709: 'Hangzhou', 20152901: 'Nanjing', 20150103: 'Wuhan',
    20132205: 'Xian', 20172501: 'Chengdu', 20191005: 'Chongqing', 20152102: 'Tianjin',
    20152106: 'Dalian', 20132901: 'Qingdao', 20110805: 'Shenyang', 20132501: 'Changchun',
    20132004: 'Harbin', 20111301: 'Shijiazhuang', 20150108: 'Taiyuan', 20110404: 'Zhengzhou',
    20110402: 'Changsha', 20191001: 'Fuzhou', 20131302: 'Nanchang', 20111202: 'Hefei',
    20152304: 'Ningbo', 20191603: 'Xiamen', 20150606: 'Jinan', 20132804: 'Suzhou',
    20150906: 'Wuxi'
}

COMPREHENSIVE_CITY_COORDS = {
    "Beijing": [116.40, 39.90], "Shanghai": [121.48, 31.22], "Tianjin": [117.20, 39.12], "Chongqing": [106.55, 29.57],
    "Shijiazhuang": [114.48, 38.03], "Taiyuan": [112.54, 37.87], "Huhehaote": [111.74, 40.84],
    "Shenyang": [123.38, 41.80], "Changchun": [125.35, 43.88], "Harbin": [126.63, 45.75],
    "Nanjing": [118.78, 32.04], "Hangzhou": [120.19, 30.26], "Hefei": [117.22, 31.82],
    "Fuzhou": [119.30, 26.08], "Nanchang": [115.85, 28.68], "Jinan": [117.00, 36.65],
    "Zhengzhou": [113.62, 34.75], "Wuhan": [114.30, 30.60], "Changsha": [112.93, 28.23],
    "Guangzhou": [113.23, 23.16], "Nanning": [108.36, 22.81], "Haikou": [110.32, 20.03],
    "Chengdu": [104.06, 30.67], "Guiyang": [106.63, 26.64], "Kunming": [102.83, 24.88],
    "Lasa": [91.11, 29.97], "Xian": [108.93, 34.27], "Lanzhou": [103.83, 36.06],
    "Xining": [101.77, 36.62], "Yinchuan": [106.23, 38.48], "Urumqi": [87.61, 43.82],
    "Dalian": [121.62, 38.92], "Qingdao": [120.33, 36.07], "Ningbo": [121.55, 29.88],
    "Xiamen": [118.10, 24.46], "Shenzhen": [114.07, 22.62], "Suzhou": [120.62, 31.32],
    "Wuxi": [120.30, 31.57], "Foshan": [113.12, 23.02], "Dongguan": [113.75, 23.04],
    "Tangshan": [118.18, 39.63], "Yantai": [121.39, 37.52], "Wenzhou": [120.70, 28.00],
    "Quanzhou": [118.58, 24.93], "Changzhou": [119.95, 31.78], "Xuzhou": [117.20, 34.26],
    "Weifang": [119.10, 36.70], "Zibo": [118.05, 36.78], "Shaoxing": [120.58, 30.01],
    "Taizhou": [121.42, 28.65], "Jinhua": [119.65, 29.08], "Jiaxing": [120.75, 30.75],
    "Huzhou": [120.08, 30.90], "Yangzhou": [119.42, 32.39], "Zhenjiang": [119.45, 32.20],
    "Taizhou": [119.90, 32.49], "Yancheng": [120.13, 33.38], "Huaian": [119.02, 33.62],
    "Lianyungang": [119.22, 34.60], "Suqian": [118.28, 33.97], "Quzhou": [118.87, 28.97],
    "Zhoushan": [122.20, 30.00], "Lishui": [119.92, 28.45],
    "Baotou": [109.82, 40.65], "Anshan": [122.85, 41.12], "Fushun": [123.97, 41.97],
    "Jilin": [126.57, 43.87], "Qiqihar": [123.97, 47.33], "Daqing": [125.03, 46.58],
    "Mudanjiang": [129.58, 44.58], "Jinzhou": [121.13, 41.10], "Yingkou": [122.23, 40.67],
    "Fuxin": [121.67, 42.02], "Liaoyang": [123.17, 41.27], "Panjin": [122.07, 41.12],
    "Tieling": [123.85, 42.32], "Chaoyang": [120.45, 41.58], "Huludao": [120.83, 40.72]
}

PROVINCE_COORDS = {
    "Beijing": [116.40, 39.90], "Tianjin": [117.20, 39.12], "Hebei": [114.48, 38.03],
    "Shanxi": [112.53, 37.87], "Neimenggu": [111.65, 40.82], "Liaoning": [123.38, 41.80],
    "Jilin": [125.35, 43.88], "Heilongjiang": [126.63, 45.75], "Shanghai": [121.48, 31.22],
    "Jiangsu": [118.78, 32.04], "Zhejiang": [120.19, 30.26], "Anhui": [117.27, 31.86],
    "Fujian": [119.30, 26.08], "Jiangxi": [115.89, 28.68], "Shandong": [117.00, 36.65],
    "Henan": [113.65, 34.76], "Hubei": [114.31, 30.52], "Hunan": [113.00, 28.21],
    "Guangdong": [113.23, 23.16], "Guangxi": [108.33, 22.84], "Hainan": [110.35, 20.02],
    "Chongqing": [106.54, 29.59], "Sichuan": [104.06, 30.67], "Guizhou": [106.71, 26.57],
    "Yunnan": [102.73, 25.04], "Xizang": [91.11, 29.97], "Shaanxi": [108.95, 34.27],
    "Gansu": [103.73, 36.03], "Qinghai": [101.74, 36.56], "Ningxia": [106.27, 38.47],
    "Xinjiang": [87.68, 43.77], "Xianggang": [114.17, 22.28], "Aomen": [113.54, 22.19],
    "Taiwan": [121.50, 25.03]
}

# ==========================================
# 2. 数据处理与清洗函数
# ==========================================

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
             
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

# ==========================================
# 3. 图表生成函数
# ==========================================

AXIS_GRAY = "#6E7079"
LEFT_AXIS_NAME = "Avg Debt (10k)"
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
    
    df_agg = df.groupby(['region_en', 'rural']).apply(
        lambda x: (x['total_debt'] * x['weight_hh']).sum() / x['weight_hh'].sum(), 
        include_groups=False
    ).reset_index(name='avg')
    
    pivot = df_agg.pivot(index='region_en', columns='rural', values='avg').fillna(0)
    regions = pivot.index.tolist()
    urban_data = (pivot[0] / 10000).round(2).tolist()
    rural_data = (pivot[1] / 10000).round(2).tolist()
    
    df_ratio = df.groupby('region_en').apply(
        lambda x: pd.Series({
            'total_w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'total_w_income': (x['total_income'] * x['weight_hh']).sum()
        }), include_groups=False
    ).reset_index()
    
    df_ratio = df_ratio.set_index('region_en').reindex(regions).reset_index()
    df_ratio['d_i_ratio'] = df_ratio['total_w_debt'] / df_ratio['total_w_income']
    ratio_data = df_ratio['d_i_ratio'].round(2).tolist()
    
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(regions)
        .add_yaxis("Urban Debt", urban_data, stack="stack1", color=COLOR_BLUE, bar_width="40%")
        .add_yaxis("Rural Debt", rural_data, stack="stack1", color="#72b0ea") 
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
            'total_w_income': (x['total_income'] * x['weight_hh']).sum()
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
    df_plot = df_prov.dropna(subset=['lat', 'lon'])
    
    if df_plot.empty: return None

    fig = px.scatter_geo(
        df_plot, lat='lat', lon='lon', size='avg_debt_10k', color='ratio_display',
        hover_name='prov', size_max=35, color_continuous_scale='RdYlBu_r', 
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
        y="total_debt",  # <--- 关键修改：看绝对金额，不再看比例
        title="Distribution of Household Total Debt Amount (by Tier)",
        color_discrete_sequence=[COLOR_BLUE], # 统一使用主题蓝
        category_orders={"tier_label": tier_order}, 
        notched=True
    )
    
    # 5. 样式优化
    fig.update_layout(
        height=400,
        xaxis_title=None,
        yaxis_title="Total Debt (RMB)",
        showlegend=False,
        yaxis=dict(
            gridcolor='#eee',
            zerolinecolor='#eee',
            # 【关键】设置显示范围：0 到 300万。
            # 如果你的数据里大部分人负债都在100万以内，可以改成 1000000
            # 这样能过滤掉极少数的超级富豪，让箱体看起来更清楚
            range=[0, 3000000] 
        )
    )
    
    return fig

def plot_city_rank(df):
    """图5: 城市排名 (Top黄色，Bottom绿色) - 字典兼容版"""
    if 'final_city_name' not in df.columns: return None
    df_valid = df.dropna(subset=['final_city_name'])

    # 1. 数据计算
    df_city_agg = df_valid.groupby('final_city_name').apply(
        lambda x: pd.Series({
            'w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'w_weight': x['weight_hh'].sum()
        }), include_groups=False
    ).reset_index()

    df_city_agg['weighted_avg_debt'] = df_city_agg['w_debt'] / df_city_agg['w_weight']
    df_city_agg = df_city_agg.sort_values('weighted_avg_debt', ascending=False)

    top5 = df_city_agg.head(5).reset_index(drop=True)
    bottom5 = df_city_agg.tail(5).sort_values('weighted_avg_debt', ascending=True).reset_index(drop=True)
    
    overall_val = (df_valid['total_debt'] * df_valid['weight_hh']).sum() / df_valid['weight_hh'].sum() / 10000

    # 2. X 轴标签
    x_data = [f"Top{i+1}\n{n}" for i,n in enumerate(top5['final_city_name'])] + \
             ["National\nAvg"] + \
             [f"Last{i+1}\n{n}" for i,n in enumerate(bottom5['final_city_name'])]

    # 3. Y 轴数据 - 使用字典格式，避免 opts.BarItem 报错
    y_data_items = []

    # 颜色定义
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
            "Avg Debt (10k)", 
            y_data_items,  # 传入字典列表
            category_gap="30%"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="City Debt Ranking: Extremes vs. Average"),
            yaxis_opts=opts.AxisOpts(name="10k RMB"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0, font_size=10)),
            legend_opts=opts.LegendOpts(is_show=False) # 隐藏图例，因为颜色已能说明问题
        )
    )
    return c

def plot_geo_debt_map_comprehensive(df):
    """图6: 城市债务地图"""
    if 'final_city_name' not in df.columns: return None
    
    df_city = df.groupby('final_city_name').apply(
        lambda x: pd.Series({
            'w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'w_income': (x['total_income'] * x['weight_hh']).sum(),
            'sum_weight': x['weight_hh'].sum()
        }), include_groups=False
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
    df_plot = df_city.dropna(subset=['lat', 'lon'])
    
    if df_plot.empty: return None

    df_plot = df_plot.sort_values('avg_debt', ascending=False).head(80)
    df_plot['avg_debt_10k'] = (df_plot['avg_debt'] / 10000).round(2)
    df_plot['Risk Ratio'] = df_plot['d_i_ratio'].round(2)

    fig = px.scatter_geo(
        df_plot,
        lat='lat',
        lon='lon',
        size='avg_debt_10k',    
        color='Risk Ratio',     
        hover_name='final_city_name',
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

    required_cols = ['rural_str', 'region_en', 'prov', 'tier_label']
    for col in required_cols:
        if col not in df_sun.columns: return None
        df_sun[col] = df_sun[col].fillna('Unknown')
    
    df_sun['weighted_debt'] = df_sun['total_debt'] * df_sun['weight_hh']
    df_agg = df_sun.groupby(required_cols)['weighted_debt'].sum().reset_index()
    
    fig = px.sunburst(
        df_agg, path=['rural_str', 'region_en', 'prov', 'tier_label'],
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
        
    st.info("若未上传文件，将尝试加载默认路径或当前目录文件。")

st.title("🇨🇳 China Household Finance Survey (CHFS) Analysis")
st.markdown("### Macro-Regional & City Analysis")

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
        #kpi_cols[3].metric("Indebted Households", f"{households_with_debt:.1%}")

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
            # 修改这里：调用新的箱线图函数
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
        st.error("无法处理数据，请检查文件格式。")
else:
    st.warning("⚠️ Data files not found. Please upload CSVs.")
