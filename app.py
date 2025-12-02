import streamlit as st
import pandas as pd
import re
from pyecharts import options as opts
from pyecharts.charts import Bar, Line
from pyecharts.globals import ThemeType
from streamlit_echarts import st_pyecharts
import plotly.express as px
import os
import numpy as np 

# ==========================================
# 0. Global Configuration and Color Definition
# ==========================================
COLOR_BLUE = "#5470c6"
COLOR_YELLOW = "#fac858"
COLOR_BG = "#ffffff"
PLOTLY_CONFIG = {'displayModeBar': False} # Configuration to suppress the deprecation warning

# Set page configuration
st.set_page_config(
    page_title="China Household Debt Analysis Dashboard | CHFS",
    page_icon="🇨🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styles - Enhance KPI visualization
st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    /* Optimize stMetric font size and style */
    .stMetric > div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700;
        color: #333;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 20px; /* Increase padding */
        border-radius: 10px;
        border-left: 6px solid #5470c6; /* Bold blue accent line on the left */
        box-shadow: 0 4px 10px rgba(0,0,0,0.08); /* Increase shadow depth */
    }
    h1, h2, h3 {font-family: 'Segoe UI', sans-serif; color: #333;}
    /* Adjust Streamlit Subheader spacing */
    h3 {margin-top: 0.5rem; margin-bottom: 0.8rem;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. Core Dictionaries: City Code Mapping and Coordinates (All in Pinyin)
#    IMPORTANT: Ensure these Pinyin names exactly match your desired display
#    and can be derived from your raw CSV data (via code mapping or explicit province_mapping).
# ==========================================
COMPREHENSIVE_CITY_CODE_MAP = {
    20130201: 'Beijing', 2013020101: 'Beijing', 2013020102: 'Beijing', 2013020103: 'Beijing',
    20110201: 'Shanghai', 2011020101: 'Shanghai', 2011020102: 'Shanghai',
    20132601: 'Tianjin', 2013260101: 'Tianjin', 2013260102: 'Tianjin',
    20131601: 'Chongqing', 2013160101: 'Chongqing', 2013160102: 'Chongqing',
    20170301: 'Shijiazhuang', 2017030101: 'Shijiazhuang', 20170307: 'Tangshan', 2017030701: 'Tangshan',
    20170308: 'Qinhuangdao', 2017030801: 'Qinhuangdao', 20170314: 'Baoding', 2017031401: 'Baoding',
    20131001: 'Taiyuan', 2013100101: 'Taiyuan', 20131002: 'Datong', 2013100201: 'Datong',
    # Note: Using 'Hohhot' to match COMPREHENSIVE_CITY_COORDS
    20130501: 'Hohhot', 2013050101: 'Hohhot', 20130509: 'Baotou', 2013050901: 'Baotou',
    20170601: 'Shenyang', 2017060101: 'Shenyang', 2017060111: 'Dalian', 201706111: 'Dalian',
    20170701: 'Changchun', 2017070101: 'Changchun', # Note: Using 'Jilin' for the city name, assuming no conflict with province
    20170702: 'Jilin', 2017070201: 'Jilin', 
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
    # Note: Using 'Lhasa' to match COMPREHENSIVE_CITY_COORDS
    20130201: 'Lhasa', 2013020101: 'Lhasa', 2013020103: 'Lhasa',
    # Note: Using 'Xi\'an' to match COMPREHENSIVE_CITY_COORDS
    20131801: 'Xi\'an', 2013180101: 'Xi\'an', 20131802: 'Tongchuan', 2013180201: 'Tongchuan',
    20132305: 'Xi\'an', 2013230501: 'Xi\'an',
    20130401: 'Lanzhou', 2013040101: 'Lanzhou', 20130402: 'Jiayuguan', 2013040201: 'Jiayuguan',
    20110301: 'Lanzhou', 2011030101: 'Lanzhou', 20172801: 'Lanzhou', 2017280101: 'Lanzhou',
    20172810: 'Tianshui', 2017281001: 'Tianshui',
    20130301: 'Xining', 2013030101: 'Xining', 20130304: 'Haidong', 2013030401: 'Haidong',
    20131901: 'Yinchuan', 2013190101: 'Yinchuan', 20131904: 'Shizuishan', 2013190401: 'Shizuishan',
    20130601: 'Urumqi', 2013060101: 'Urumqi', 20130603: 'Karamay', 2013060301: 'Karamay',
    20192304: 'Guangzhou', 20192101: 'Shenzhen', 20192102: 'Zhuhai', 20130106: 'Beijing',
    20132802: 'Shanghai', 20151709: 'Hangzhou', 20152901: 'Nanjing', 20150103: 'Wuhan',
    20132205: 'Xi\'an', 20172501: 'Chengdu', 20191005: 'Chongqing', 20152102: 'Tianjin',
    20152106: 'Dalian', 20132901: 'Qingdao', 20110805: 'Shenyang', 20132501: 'Changchun',
    20132004: 'Harbin', 20111301: 'Shijiazhuang', 20150108: 'Taiyuan', 20110404: 'Zhengzhou',
    20110402: 'Changsha', 20191001: 'Fuzhou', 20131302: 'Nanchang', 20111202: 'Hefei',
    20152304: 'Ningbo', 20191603: 'Xiamen', 20150606: 'Jinan', 20132804: 'Suzhou',
    20150906: 'Wuxi'
}

COMPREHENSIVE_CITY_COORDS = {
    "Beijing": [116.40, 39.90], "Shanghai": [121.48, 31.22], "Tianjin": [117.20, 39.12], "Chongqing": [106.55, 29.57],
    "Shijiazhuang": [114.48, 38.03], "Taiyuan": [112.54, 37.87], "Hohhot": [111.74, 40.84], # Changed to Hohhot
    "Shenyang": [123.38, 41.80], "Changchun": [125.35, 43.88], "Harbin": [126.63, 45.75],
    "Nanjing": [118.78, 32.04], "Hangzhou": [120.19, 30.26], "Hefei": [117.22, 31.82],
    "Fuzhou": [119.30, 26.08], "Nanchang": [115.85, 28.68], "Jinan": [117.00, 36.65],
    "Zhengzhou": [113.62, 34.75], "Wuhan": [114.30, 30.60], "Changsha": [112.93, 28.23],
    "Guangzhou": [113.23, 23.16], "Nanning": [108.36, 22.81], "Haikou": [110.32, 20.03],
    "Chengdu": [104.06, 30.67], "Guiyang": [106.63, 26.64], "Kunming": [102.83, 24.88],
    "Lhasa": [91.11, 29.97], # Changed to Lhasa
    "Xi'an": [108.93, 34.27], # Changed to Xi'an with apostrophe
    "Lanzhou": [103.83, 36.06],
    "Xining": [101.77, 36.62], "Yinchuan": [106.23, 38.48], "Urumqi": [87.61, 43.82],
    "Dalian": [121.62, 38.92], "Qingdao": [120.33, 36.07], "Ningbo": [121.55, 29.88],
    "Xiamen": [118.10, 24.46], "Shenzhen": [114.07, 22.62], "Suzhou": [120.62, 31.32],
    "Wuxi": [120.30, 31.57], "Foshan": [113.12, 23.02], "Dongguan": [113.75, 23.04],
    "Tangshan": [118.18, 39.63], "Yantai": [121.39, 37.52], "Wenzhou": [120.70, 28.00],
    "Quanzhou": [118.58, 24.93], "Changzhou": [119.95, 31.78], "Xuzhou": [117.20, 34.26],
    "Weifang": [119.10, 36.70], "Zibo": [118.05, 36.78], "Shaoxing": [120.58, 30.01],
    "Taizhou": [121.42, 28.65], "Jinhua": [119.65, 29.08], "Jiaxing": [120.75, 30.75],
    "Huzhou": [120.08, 30.90], "Yangzhou": [119.42, 32.39], "Zhenjiang": [119.45, 32.20],
    "Taizhou (JS)": [119.90, 32.49], # Differentiate from Zhejiang's Taizhou if needed
    "Yancheng": [120.13, 33.38], "Huai'an": [119.02, 33.62], # Changed to Huai'an with apostrophe
    "Lianyungang": [119.22, 34.60], "Suqian": [118.28, 33.97], "Quzhou": [118.87, 28.97],
    "Zhoushan": [122.20, 30.00], "Lishui": [119.92, 28.45],
    "Baotou": [109.82, 40.65], "Anshan": [122.85, 41.12], "Fushun": [123.97, 41.97],
    "Jilin City": [126.57, 43.87], # Differentiate from Jilin Province
    "Qiqihar": [123.97, 47.33], "Daqing": [125.03, 46.58],
    "Mudanjiang": [129.58, 44.58], "Jinzhou": [121.13, 41.10], "Yingkou": [122.23, 40.67],
    "Fuxin": [121.67, 42.02], "Liaoyang": [123.17, 41.27], "Panjin": [122.07, 41.12],
    "Tieling": [123.85, 42.32], "Chaoyang": [120.45, 41.58], "Huludao": [120.83, 40.72]
}
PROVINCE_COORDS = {
    "Beijing": [116.40, 39.90], "Tianjin": [117.20, 39.12], "Hebei": [114.48, 38.03],
    "Shanxi": [112.53, 37.87], "Inner Mongolia": [111.65, 40.82], # Changed to Inner Mongolia
    "Liaoning": [123.38, 41.80],
    "Jilin": [125.35, 43.88], "Heilongjiang": [126.63, 45.75], "Shanghai": [121.48, 31.22],
    "Jiangsu": [118.78, 32.04], "Zhejiang": [120.19, 30.26], "Anhui": [117.27, 31.86],
    "Fujian": [119.30, 26.08], "Jiangxi": [115.89, 28.68], "Shandong": [117.00, 36.65],
    "Henan": [113.65, 34.76], "Hubei": [114.31, 30.52], "Hunan": [113.00, 28.21],
    "Guangdong": [113.23, 23.16], "Guangxi": [108.33, 22.84], "Hainan": [110.35, 20.02],
    "Chongqing": [106.54, 29.59], "Sichuan": [104.06, 30.67], "Guizhou": [106.71, 26.57],
    "Yunnan": [102.73, 25.04], "Tibet": [91.11, 29.97], # Changed to Tibet
    "Shaanxi": [108.95, 34.27],
    "Gansu": [103.73, 36.03], "Qinghai": [101.74, 36.56], "Ningxia": [106.27, 38.47],
    "Xinjiang": [87.68, 43.77], "Hong Kong": [114.17, 22.28], "Macao": [113.54, 22.19],
    "Taiwan": [121.50, 25.03]
}

# ==========================================
# 2. Data Processing and Cleaning Functions 
# ==========================================

# NOTE: Since dictionaries are now Pinyin, these functions will mainly map raw codes to Pinyin
# or ensure consistency for already-Pinyin names.
# For province names in CSV, explicit `province_mapping` is used in `load_and_clean_data`.

def convert_city_name_advanced(val):
    """
    Converts city codes to Pinyin names from COMPREHENSIVE_CITY_CODE_MAP.
    For string values, it attempts to clean and match against Pinyin city names.
    """
    if pd.isna(val): return None
    val_str = str(val).strip()
    
    # If the input is a numeric code, map it directly to Pinyin from the code map
    try:
        code_val = float(val_str)
        code_int = int(code_val)
        mapped_name = COMPREHENSIVE_CITY_CODE_MAP.get(code_int)
        if mapped_name: return mapped_name
        # Handle codes with decimals, trying to map the main part
        if '.' in val_str:
            code_parts = val_str.split('.')
            if len(code_parts) == 2:
                main_code = int(code_parts[0][:6])
                mapped_name = COMPREHENSIVE_CITY_CODE_MAP.get(main_code)
                if mapped_name: return mapped_name
    except (ValueError, TypeError):
        pass
    
    # If it's a string (could be Chinese, or already Pinyin in original CSV)
    # This logic assumes that if Chinese characters are present, they are either
    # a direct match to one of the explicit `province_mapping` in `load_and_clean_data`
    # or will be handled by `clean_city_name_for_map` if they are already Pinyin-like.
    
    # Try to clean specific Chinese suffixes if the input itself contains Chinese characters
    # (This path will be mostly for Chinese strings not handled by province_mapping directly)
    if re.search(r'[\u4e00-\u9fff]', val_str):
        clean_chinese_name = re.sub(r'[市县地区壮族回族维吾尔自治区省]$', '', val_str)
        # Attempt to map these cleaned Chinese names to known Pinyin cities
        # This part might need further refinement if your `city_lab` has many unmapped Chinese city names
        # For now, it will return the cleaned Chinese which `clean_city_name_for_map` might then fail to match
        # The best approach here would be a pypinyin conversion, but we avoid it in this version.
        if clean_chinese_name == '呼和浩特': return 'Hohhot'
        if clean_chinese_name == '拉萨': return 'Lhasa'
        if clean_chinese_name == '西安': return 'Xi\'an'
        if clean_chinese_name == '淮安': return 'Huai\'an'
        if clean_chinese_name == '吉林': return 'Jilin City' # To differentiate from province
        
        # If still Chinese, it will likely not match Pinyin dictionaries further down
        return clean_chinese_name 
        
    # If it's already an English Pinyin string, ensure consistency
    for k_pinyin in COMPREHENSIVE_CITY_COORDS.keys():
        if val_str.lower() == k_pinyin.lower():
            return k_pinyin # Return the correctly cased Pinyin name
            
    return None

def clean_city_name_for_map(name):
    """
    Final cleaning and validation for city names against COMPREHENSIVE_CITY_COORDS.
    Assumes `name` is already Pinyin or has been converted/mapped.
    """
    if pd.isna(name): return None
    name_str = str(name).strip()
    
    # Direct match
    if name_str in COMPREHENSIVE_CITY_COORDS: return name_str
    
    # Case-insensitive match
    for standard_name_pinyin in COMPREHENSIVE_CITY_COORDS.keys():
        if name_str.lower() == standard_name_pinyin.lower():
            return standard_name_pinyin
    
    # Remove common Pinyin suffixes that might have been generated or remain
    cleaned_name = re.sub(r'(City|County|District|Region|Prefecture|AutonomousRegion|Province|Shi|Xian|Qu|Zizhiqu)$', '', name_str, flags=re.IGNORECASE).strip()
    if cleaned_name in COMPREHENSIVE_CITY_COORDS: return cleaned_name
    
    # Special handling for cities that might be confused with provinces (e.g., Jilin City)
    if cleaned_name == 'Jilin':
        if 'Jilin City' in COMPREHENSIVE_CITY_COORDS:
            return 'Jilin City'
            
    return None # No match found

@st.cache_data
def load_and_clean_data(master_file, hh_file):
    try:
        master_cols = ['hhid', 'rural', 'total_debt', 'total_asset', 'weight_hh', 'total_income',
                       'city_lab', 'city_level', 'region', 'prov']
        
        # Determine if file_uploader output (BytesIO) or local path (str)
        if isinstance(master_file, str):
            master = pd.read_csv(master_file, low_memory=False, usecols=lambda x: x in master_cols)
            hh = pd.read_csv(hh_file, low_memory=False, usecols=['hhid', 'house01num'])
        else: # Streamlit uploaded file
            master = pd.read_csv(master_file, low_memory=False, usecols=lambda x: x in master_cols)
            hh_file.seek(0) # Reset pointer for hh_file in case it was read before
            hh = pd.read_csv(hh_file, low_memory=False, usecols=['hhid', 'house01num'])
            
        df = master.merge(hh[['hhid', 'house01num']], on='hhid', how='left')
        
        numeric_cols = ['rural', 'total_debt', 'total_asset', 'weight_hh', 'total_income']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df[df['weight_hh'] > 0].copy()
        df['total_debt'] = df['total_debt'].fillna(0).clip(lower=0)
        df['total_income'] = df['total_income'].fillna(0).clip(lower=0)
        
        # City and Province Name Mapping to English Pinyin
        if 'city_lab' in df.columns:
            df['city_raw'] = df['city_lab'] # Keep original raw
            df['city_mapped'] = df['city_lab'].apply(convert_city_name_advanced) # Map codes/clean strings to Pinyin
            df['final_city_name'] = df['city_mapped'].apply(clean_city_name_for_map) # Final validation against coords
        else:
            df['final_city_name'] = None
        
        if 'prov' in df.columns:
            # Explicit Chinese to English Pinyin mapping for provinces
            # IMPORTANT: Add any missing Chinese province names from your raw data here if not covered
            province_mapping = {
                '北京': 'Beijing', '天津': 'Tianjin', '河北': 'Hebei', '山西': 'Shanxi', 
                '内蒙古': 'Inner Mongolia', '辽宁': 'Liaoning', '吉林': 'Jilin', 
                '黑龙江': 'Heilongjiang', '上海': 'Shanghai', '江苏': 'Jiangsu',
                '浙江': 'Zhejiang', '安徽': 'Anhui', '福建': 'Fujian', '江西': 'Jiangxi', 
                '山东': 'Shandong', '河南': 'Henan', '湖北': 'Hubei', '湖南': 'Hunan',
                '广东': 'Guangdong', '广西': 'Guangxi', '海南': 'Hainan', '重庆': 'Chongqing', 
                '四川': 'Sichuan', '贵州': 'Guizhou', '云南': 'Yunnan', '西藏': 'Tibet', 
                '陕西': 'Shaanxi', '甘肃': 'Gansu', '青海': 'Qinghai', '宁夏': 'Ningxia',
                '新疆': 'Xinjiang', '香港': 'Hong Kong', '澳门': 'Macao', '台湾': 'Taiwan'
            }
            # Remove common suffixes before mapping, then apply mapping
            df['prov'] = df['prov'].astype(str).str.replace(r'[省市壮族回族维吾尔自治区]$', '', regex=True)
            df['prov'] = df['prov'].map(province_mapping).fillna(df['prov'])
            # Ensure final province names are in PROVINCE_COORDS keys, set others to None
            df['prov'] = df['prov'].apply(lambda x: x if x in PROVINCE_COORDS else None)

        if 'city_level' in df.columns:
            def map_city_tier(level):
                if pd.isna(level): return None
                level = str(level).strip()
                # Ensure mapping works for both Chinese and potential Pinyin/English in raw data
                if '一线' in level or 'Tier 1' in level or 'New Tier 1' in level: return 'Tier 1 / New Tier 1'
                elif '二线' in level or 'Tier 2' in level: return 'Tier 2'
                elif '三线' in level or '以下' in level or '非一线' in level or 'Tier 3' in level: return 'Tier 3 & Below'
                return 'Other'
            df['tier_label'] = df['city_level'].apply(map_city_tier)
            
        if 'region' in df.columns:
            region_mapping = {'东部': 'East', '中部': 'Central', '西部': 'West', '东北': 'Northeast'}
            df['region_en'] = df['region'].map(region_mapping).fillna(df['region'])
            
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None

# ==========================================
# 3. Chart Generation Functions 
# ==========================================
AXIS_GRAY = "#6E7079"
LEFT_AXIS_NAME = "Avg Debt (10k RMB)"
RIGHT_AXIS_NAME = "Debt-to-Income Ratio"

# Function: plot_urban_rural (Urban vs. Rural Comparison)
def plot_urban_rural(df):
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
            title_opts=opts.TitleOpts(title="Urban vs. Rural: Debt Burden & Risk", pos_left='center'),
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

# Function: plot_regional_stack (Regional Comparison)
def plot_regional_stack(df):
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
            title_opts=opts.TitleOpts(title="Regional Debt Composition & Risk Level", pos_left='center'),
            yaxis_opts=opts.AxisOpts(
                name=LEFT_AXIS_NAME, name_location="end",
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=AXIS_GRAY))
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_top="5%", pos_left="center")
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

# Function: plot_city_tier_boxplot (City Tier Debt Distribution)
def plot_city_tier_boxplot(df):
    if 'tier_label' not in df.columns: return None
    df_plot = df[df['tier_label'] != 'Other'].copy()
    df_valid = df_plot[df_plot['total_debt'] > 0]
    if df_valid.empty: return None
    tier_order = ["Tier 1 / New Tier 1", "Tier 2", "Tier 3 & Below"]
    
    fig = px.box(
        df_valid,
        x="tier_label",
        y="total_debt", 
        title="Household Total Debt Amount Distribution (by City Tier)",
        color_discrete_sequence=[COLOR_BLUE], 
        category_orders={"tier_label": tier_order},
        notched=True
    )
    
    fig.update_layout(
        height=400, # Height set in Plotly object
        xaxis_title="City Tier",
        yaxis_title="Total Debt (RMB)",
        showlegend=False,
        yaxis=dict(
            gridcolor='#eee',
            zerolinecolor='#eee',
            range=[0, 3000000] # Set range to focus on median and IQR
        )
    )
    return fig

# Function: plot_city_rank (City Ranking)
def plot_city_rank(df):
    if 'final_city_name' not in df.columns: return None
    df_valid = df.dropna(subset=['final_city_name'])
    
    if df_valid.empty: return None
    
    df_city_agg = df_valid.groupby('final_city_name').apply(
        lambda x: pd.Series({
            'w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'w_weight': x['weight_hh'].sum()
        }), include_groups=False
    ).reset_index()
    df_city_agg['weighted_avg_debt'] = df_city_agg['w_debt'] / df_city_agg['w_weight']
    df_city_agg = df_city_agg.sort_values('weighted_avg_debt', ascending=False)
    
    if len(df_city_agg) < 10: # Ensure there are enough cities to show top5/bottom5
        st.info("Not enough distinct cities in the data to show a ranking chart.")
        return None
        
    top5 = df_city_agg.head(5).reset_index(drop=True)
    bottom5 = df_city_agg.tail(5).sort_values('weighted_avg_debt', ascending=True).reset_index(drop=True)
    
    overall_val = (df_valid['total_debt'] * df_valid['weight_hh']).sum() / df_valid['weight_hh'].sum() / 10000
    
    x_data = [f"Top{i+1}\n{n}" for i,n in enumerate(top5['final_city_name'])] + \
             ["National\nAvg"] + \
             [f"Last{i+1}\n{n}" for i,n in enumerate(bottom5['final_city_name'])]
    
    y_data_items = []
    COLOR_TOP = "#fac858" 
    COLOR_AVG = "#c0c4c6" 
    COLOR_BOT = "#91cc75" 
    
    for val in (top5['weighted_avg_debt']/10000).tolist():
        y_data_items.append({
            "value": round(val, 2),
            "itemStyle": {"color": COLOR_TOP}
        })
    y_data_items.append({
        "value": round(overall_val, 2),
        "itemStyle": {"color": COLOR_AVG}
    })
    for val in (bottom5['weighted_avg_debt']/10000).tolist():
        y_data_items.append({
            "value": round(val, 2),
            "itemStyle": {"color": COLOR_BOT}
        })
    
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(x_data)
        .add_yaxis(
            "Avg Debt (10k)",
            y_data_items, 
            category_gap="30%"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="City Debt Ranking: Extremes vs. Average", pos_left='center'),
            yaxis_opts=opts.AxisOpts(name="10k RMB"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0, font_size=10)),
            legend_opts=opts.LegendOpts(is_show=False) 
        )
    )
    return c

# Function: plot_debt_sunburst (Sunburst Chart)
def plot_debt_sunburst(df):
    df_sun = df.copy()
    if 'rural' in df_sun.columns:
        df_sun['rural_str'] = df_sun['rural'].map({0: 'Urban', 1: 'Rural'})
    else: return None
    
    # Fill NaN values for categorical columns used in path to prevent errors
    df_sun['tier_label'] = df_sun['tier_label'].fillna('Unknown')
    df_sun['region_en'] = df_sun['region_en'].fillna('Unknown')
    df_sun['prov'] = df_sun['prov'].fillna('Unknown')

    required_cols = ['rural_str', 'region_en', 'prov', 'tier_label']
    for col in required_cols:
        if col not in df_sun.columns: return None
    
    df_sun['weighted_debt'] = df_sun['total_debt'] * df_sun['weight_hh']
    # Filter out entries with zero debt if desired for cleaner visualization
    df_agg = df_sun[df_sun['weighted_debt'] > 0].groupby(required_cols)['weighted_debt'].sum().reset_index()
    
    if df_agg.empty: return None

    fig = px.sunburst(
        df_agg, path=['rural_str', 'region_en', 'prov', 'tier_label'],
        values='weighted_debt',
        title="Hierarchical View: Where is the Total Debt Concentrated?",
        color='weighted_debt', color_continuous_scale='RdBu_r'
    )
    fig.update_layout(margin=dict(t=40, l=0, r=0, b=0), height=600) # Height set in Plotly object
    return fig

# Function: plot_geo_debt_map_combined (Combined Map for Provincial and City)
def plot_geo_debt_map_combined(df, level="Provincial"):
    if df.empty: return None

    if level == "Provincial":
        if 'prov' not in df.columns: return None
        # Group by province (which should already be Pinyin)
        df_group = df.groupby('prov', dropna=True).apply(
            lambda x: pd.Series({
                'avg_debt': (x['total_debt'] * x['weight_hh']).sum() / x['weight_hh'].sum(),
                'total_w_debt': (x['total_debt'] * x['weight_hh']).sum(),
                'total_w_income': (x['total_income'] * x['weight_hh']).sum()
            }), include_groups=False
        ).reset_index()
        
        df_group['d_i_ratio'] = df_group.apply(
             lambda x: x['total_w_debt'] / x['total_w_income'] if x['total_w_income'] > 0 else np.nan, axis=1
        )
        
        df_group['Name'] = df_group['prov']
        coord_dict = PROVINCE_COORDS
        size_max = 35
        zoom_scale = 2.5
        center_lat, center_lon = 35, 105
        title = "Provincial Debt Map: Volume vs. Risk"
        
        def get_lat_lon(name):
            name_str = str(name)
            # Direct lookup as `prov` column should now contain clean Pinyin names matching `PROVINCE_COORDS`
            if name_str in coord_dict: return pd.Series([coord_dict[name_str][1], coord_dict[name_str][0]])
            return pd.Series([np.nan, np.nan])
        
    elif level == "City":
        if 'final_city_name' not in df.columns: return None
        # Group by final city name (which should already be Pinyin)
        df_group = df.groupby('final_city_name', dropna=True).apply(
            lambda x: pd.Series({
                'avg_debt': (x['total_debt'] * x['weight_hh']).sum() / x['weight_hh'].sum(),
                'w_debt': (x['total_debt'] * x['weight_hh']).sum(),
                'w_income': (x['total_income'] * x['weight_hh']).sum(),
            }), include_groups=False
        ).reset_index()
        
        df_group['d_i_ratio'] = df_group.apply(
            lambda x: x['w_debt'] / x['w_income'] if x['w_income'] > 0 else np.nan, axis=1
        )
        
        df_group['Name'] = df_group['final_city_name']
        coord_dict = COMPREHENSIVE_CITY_COORDS
        # Limit to top cities for clarity on the map
        df_group = df_group.sort_values('avg_debt', ascending=False).head(80) 
        size_max = 25
        zoom_scale = 3.0
        center_lat, center_lon = 36, 104
        title = "Key City Debt Map (Size=Burden, Color=Risk)"
        
        def get_lat_lon(name):
            # Direct lookup as `final_city_name` column should now contain clean Pinyin names
            if name in coord_dict:
                coords = coord_dict[name]
                return pd.Series([coords[1], coords[0]])
            return pd.Series([np.nan, np.nan])

    else:
        return None

    df_group[['lat', 'lon']] = df_group['Name'].apply(get_lat_lon)
    # Drop rows where coordinates or debt-to-income ratio couldn't be determined
    df_plot = df_group.dropna(subset=['lat', 'lon', 'd_i_ratio'])
    
    if df_plot.empty: 
        st.warning(f"No valid data points with coordinates found for {level} map.")
        return None

    df_plot['avg_debt_10k'] = (df_plot['avg_debt'] / 10000).round(2)
    df_plot['Risk Ratio'] = df_plot['d_i_ratio'].round(2)

    fig = px.scatter_geo(
        df_plot, lat='lat', lon='lon', size='avg_debt_10k', color='Risk Ratio',
        hover_name='Name', size_max=size_max, color_continuous_scale='RdYlBu_r',
        scope='asia', title=title
    )
    
    fig.update_layout(
        height=600, # Explicit height for Plotly charts
        geo=dict(
            center=dict(lat=center_lat, lon=center_lon), 
            projection_scale=zoom_scale, 
            showland=True, 
            landcolor="#f4f4f4", 
            showcountries=True, 
            countrycolor="#dedede"
        ),
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar=dict(title="D/I Ratio")
    )
    return fig

# ==========================================
# 5. Main Program Logic (English Layout)
# ==========================================
with st.sidebar:
    st.header("📂 Data Source")
    DEFAULT_MASTER = "chfs2019_master_202112.csv"
    DEFAULT_HH = "chfs2019_hh_202112.csv"
    
    upload_files = st.file_uploader("Upload CSV Files (Optional)", type=['csv'], accept_multiple_files=True)
    master_path, hh_path = None, None
    
    if upload_files:
        files_dict = {f.name: f for f in upload_files}
        for name in files_dict.keys():
            if "master" in name.lower(): master_path = files_dict[name]
            if "hh" in name.lower(): hh_path = files_dict[name]
    
    if not master_path:
        # Fallback to local files if not uploaded
        if os.path.exists("chfs2019_master_202112.csv"):
            master_path = "chfs2019_master_202112.csv"
        # Only set hh_path if master_path was found locally
        if master_path and os.path.exists("chfs2019_hh_202112.csv"):
            hh_path = "chfs2019_hh_202112.csv"
        elif os.path.exists(DEFAULT_MASTER): # If default file exists
            master_path = DEFAULT_MASTER
            if os.path.exists(DEFAULT_HH):
                hh_path = DEFAULT_HH
            
    st.info("If no file is uploaded, the dashboard will attempt to load the default local files.")
    
    st.markdown("---")
    st.header("🗺️ Map Configuration")
    map_level = st.selectbox(
        "Select Map Granularity",
        options=["Provincial", "City"],
        index=0,
        help="Select the geographic level for the map visualization: Provincial or City."
    )

st.title("🇨🇳 China Household Finance Survey (CHFS) Debt Analysis Dashboard")
st.markdown("## Insights into Chinese Household Debt Structure and Risk")

if master_path and hh_path:
    with st.spinner("Loading and Processing Data..."):
        df = load_and_clean_data(master_path, hh_path)
    
    if df is not None:
        
        # 1. Key Performance Indicators (KPIs) - Top Row
        st.header("⭐ Key Performance Indicators")
        kpi_cols = st.columns(4)
        total_weight = df['weight_hh'].sum()
        weighted_avg_debt = (df['total_debt'] * df['weight_hh']).sum() / total_weight
        weighted_avg_income = (df['total_income'] * df['weight_hh']).sum() / total_weight
        debt_ratio = weighted_avg_debt / weighted_avg_income if weighted_avg_income > 0 else 0
        
        # Calculate households with debt more robustly for weighted data
        indebted_households_weight = df[df['total_debt'] > 0]['weight_hh'].sum()
        total_households_weight = df['weight_hh'].sum()
        households_with_debt_ratio = indebted_households_weight / total_households_weight if total_households_weight > 0 else 0

        kpi_cols[0].metric("Avg Household Debt", f"¥{weighted_avg_debt/10000:,.1f} 10k")
        kpi_cols[1].metric("Avg Household Income", f"¥{weighted_avg_income/10000:,.1f} 10k")
        kpi_cols[2].metric("Debt-to-Income Ratio", f"{debt_ratio:.1%}", 
                           delta_color="inverse", help="Weighted average debt is 'X' times the average income.")
        kpi_cols[3].metric("Indebted Households", f"{households_with_debt_ratio:.1%}", 
                           help="Proportion of households with non-zero debt (weighted).")
        
        st.markdown("---")
        
        # 2. Macro Overview: Urban/Rural and Regional Comparison
        st.header("🔍 1. Macro Overview: Urban, Rural & Regional")
        row1_col1, row1_col2 = st.columns([1, 1])
        with row1_col1:
            st.subheader("1.1 Urban vs Rural Debt & Risk")
            st_pyecharts(plot_urban_rural(df), height="380px")
        with row1_col2:
            st.subheader("1.2 Regional Debt Composition & Risk")
            chart_reg = plot_regional_stack(df)
            if chart_reg: st_pyecharts(chart_reg, height="380px")
            else: st.info("Insufficient data for regional analysis.")
            
        st.markdown("---")
        
        # 3. Geographic Distribution: Map (Core Visualization)
        st.header(f"🗺️ 2. Geographic Distribution: Debt Burden & Risk")
        st.subheader(f"2.1 {map_level} Debt & Risk Map ")
        
        fig_map_combined = plot_geo_debt_map_combined(df, level=map_level)
        if fig_map_combined:
            st.plotly_chart(fig_map_combined, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.warning(f"No data available for the {map_level} map or insufficient coordinate matches.")

        st.markdown("---")

        # 4. Structure and Breakdown: Sunburst Chart (Using Expander)
        st.header("🧱 3. Debt Structure Decomposition")
        with st.expander("Click to View: Hierarchical Debt Sunburst Chart (Urban/Rural > Region > Province > City Tier)", expanded=False):
            chart_sun = plot_debt_sunburst(df)
            if chart_sun:
                st.plotly_chart(chart_sun, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.warning("Data missing or insufficient for Sunburst Chart.")
                
        st.markdown("---")

        # 5. Micro Comparison: City Tier Distribution and Ranking
        st.header("📉 4. Detailed City Comparison")
        row3_col1, row3_col2 = st.columns([1, 1])
        with row3_col1:
            st.subheader("4.1 City Tier Debt Distribution (Box Plot)")
            chart_tier = plot_city_tier_boxplot(df)
            if chart_tier:
                st.plotly_chart(chart_tier, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("Insufficient data for city tier distribution analysis.")
                
        with row3_col2:
            st.subheader("4.2 City Debt Rankings (Top 5 vs Bottom 5)")
            chart_rank = plot_city_rank(df)
            if chart_rank: st_pyecharts(chart_rank, height="450px")
            else: st.info("Insufficient data for city ranking.")

    else:
        st.error("Could not process data. Please check the file format.")
else:
    st.warning("⚠️ Data files not found. Please upload CSVs or ensure default files exist.")
