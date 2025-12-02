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
from pypinyin import pinyin, Style # <--- NEW IMPORT for Pinyin conversion

# ==========================================
# 0. 全局配置与颜色定义
# ==========================================
COLOR_BLUE = "#5470c6"
COLOR_YELLOW = "#fac858"
COLOR_BG = "#ffffff"
PLOTLY_CONFIG = {'displayModeBar': False} # Added for Plotly charts

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
    /* Adjust Streamlit Subheader spacing */
    h3 {margin-top: 0.5rem; margin-bottom: 0.8rem;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 核心字典：城市代码映射与坐标 (仍然保持中文键)
#    这些字典的键将**在数据加载时**被转换为拼音以匹配处理后的DataFrame列。
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

COMPREHENSIVE_CITY_COORDS = {
    "北京": [116.40, 39.90], "上海": [121.48, 31.22], "天津": [117.20, 39.12], "重庆": [106.55, 29.57],
    "石家庄": [114.48, 38.03], "太原": [112.54, 37.87], "呼和浩特": [111.74, 40.84],
    "沈阳": [123.38, 41.80], "长春": [125.35, 43.88], "哈尔滨": [126.63, 45.75],
    "南京": [118.78, 32.04], "杭州": [120.19, 30.26], "合肥": [117.22, 31.82],
    "福州": [119.30, 26.08], "南昌": [115.85, 28.68], "济南": [117.00, 36.65],
    "郑州": [113.62, 34.75], "武汉": [114.30, 30.60], "长沙": [112.93, 28.23],
    "广州": [113.23, 23.16], "南宁": [108.36, 22.81], "海口": [110.32, 20.03],
    "成都": [104.06, 30.67], "贵阳": [106.63, 26.64], "昆明": [102.83, 24.88],
    "拉萨": [91.11, 29.97], "西安": [108.93, 34.27], "兰州": [103.83, 36.06],
    "西宁": [101.77, 36.62], "银川": [106.23, 38.48], "乌鲁木齐": [87.61, 43.82],
    "大连": [121.62, 38.92], "青岛": [120.33, 36.07], "宁波": [121.55, 29.88],
    "厦门": [118.10, 24.46], "深圳": [114.07, 22.62], "苏州": [120.62, 31.32],
    "无锡": [120.30, 31.57], "佛山": [113.12, 23.02], "东莞": [113.75, 23.04],
    "唐山": [118.18, 39.63], "烟台": [121.39, 37.52], "温州": [120.70, 28.00],
    "泉州": [118.58, 24.93], "常州": [119.95, 31.78], "徐州": [117.20, 34.26],
    "潍坊": [119.10, 36.70], "淄博": [118.05, 36.78], "绍兴": [120.58, 30.01],
    "台州": [121.42, 28.65], "金华": [119.65, 29.08], "嘉兴": [120.75, 30.75],
    "湖州": [120.08, 30.90], "扬州": [119.42, 32.39], "镇江": [119.45, 32.20],
    "泰州": [119.90, 32.49], "盐城": [120.13, 33.38], "淮安": [119.02, 33.62],
    "连云港": [119.22, 34.60], "宿迁": [118.28, 33.97], "衢州": [118.87, 28.97],
    "舟山": [122.20, 30.00], "丽水": [119.92, 28.45],
    "包头": [109.82, 40.65], "鞍山": [122.85, 41.12], "抚顺": [123.97, 41.97],
    "吉林": [126.57, 43.87], "齐齐哈尔": [123.97, 47.33], "大庆": [125.03, 46.58],
    "牡丹江": [129.58, 44.58], "锦州": [121.13, 41.10], "营口": [122.23, 40.67],
    "阜新": [121.67, 42.02], "辽阳": [123.17, 41.27], "盘锦": [122.07, 41.12],
    "铁岭": [123.85, 42.32], "朝阳": [120.45, 41.58], "葫芦岛": [120.83, 40.72]
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

# 动态生成拼音版本的字典，以便在数据处理后进行查找
# 这些将在 `load_and_clean_data` 中被创建并用于匹配
PINYIN_COMPREHENSIVE_CITY_CODE_MAP = {k: None for k in COMPREHENSIVE_CITY_CODE_MAP.keys()}
PINYIN_COMPREHENSIVE_CITY_COORDS = {}
PINYIN_PROVINCE_COORDS = {}

# ==========================================
# 2. 数据处理与清洗函数
# ==========================================

# Helper function to convert Chinese to Pinyin with capitalized first letter
def _to_pinyin_capitalized(text):
    if pd.isna(text):
        return None
    text_str = str(text).strip()
    if not re.search(r'[\u4e00-\u9fff]', text_str): # If no Chinese characters, return as is
        return text_str
    
    # Extract only Chinese characters for conversion
    chinese_chars = "".join(re.findall(r'[\u4e00-\u9fff]', text_str))
    if not chinese_chars:
        return text_str # Return original if no Chinese chars were found despite regex match
        
    pinyin_list = pinyin(chinese_chars, style=Style.NORMAL)
    pinyin_full = "".join([s[0] for s in pinyin_list])
    
    # Apply specific Pinyin corrections/standardizations if needed
    if pinyin_full.lower() == 'huhehaote': return 'Hohhot'
    if pinyin_full.lower() == 'lasa': return 'Lhasa'
    if pinyin_full.lower() == 'xian': return 'Xi\'an'
    if pinyin_full.lower() == 'huaian': return 'Huai\'an'
    if pinyin_full.lower() == 'jilin' and len(chinese_chars) < 3: # '吉林' city vs '吉林' province
        return 'Jilin City' 
    if pinyin_full.lower() == 'neimenggu': return 'Inner Mongolia'
    if pinyin_full.lower() == 'xizang': return 'Tibet'
    if pinyin_full.lower() == 'xianggang': return 'Hong Kong'
    if pinyin_full.lower() == 'aomen': return 'Macao'

    return pinyin_full.capitalize()


# --- 关键清洗函数：应用新的映射逻辑 (现在期望输入是拼音) ---
def convert_city_name_advanced(val, pinyin_city_code_map):
    """
    根据城市代码映射或清理后的城市名称，返回对应的拼音城市名称。
    此函数现在期望 `val` 已经是中文或数字代码，并在内部处理转换为拼音。
    """
    if pd.isna(val): return None
    val_str = str(val).strip()

    # 1. 尝试将原始值（可能是中文）转换为拼音
    pinyin_val = _to_pinyin_capitalized(val_str)
    
    # 2. 如果是数字代码，查找拼音映射
    try:
        code_val = float(val_str)
        code_int = int(code_val)
        mapped_name = pinyin_city_code_map.get(code_int) # 使用拼音代码映射表
        if mapped_name: return mapped_name
        if '.' in val_str:
            code_parts = val_str.split('.')
            if len(code_parts) == 2:
                main_code = int(code_parts[0][:6])
                mapped_name = pinyin_city_code_map.get(main_code)
                if mapped_name: return mapped_name
    except (ValueError, TypeError):
        pass # Not a numeric code, proceed to string matching

    # 3. 如果是已转换为拼音的字符串，进行匹配和清理
    if pinyin_val:
        # 直接匹配拼音字典的键 (PINYIN_COMPREHENSIVE_CITY_COORDS)
        if pinyin_val in PINYIN_COMPREHENSIVE_CITY_COORDS:
            return pinyin_val
            
        # 尝试移除常见后缀以提高匹配率
        cleaned_pinyin = re.sub(r'(City|County|District|Region|Prefecture|AutonomousRegion|Province|Shi|Xian|Qu|Zizhiqu)$', '', pinyin_val, flags=re.IGNORECASE).strip()
        if cleaned_pinyin in PINYIN_COMPREHENSIVE_CITY_COORDS:
            return cleaned_pinyin
        
        # 针对特定城市进行进一步匹配 (如果必要)
        if cleaned_pinyin.lower() == 'jilin' and 'Jilin City' in PINYIN_COMPREHENSIVE_CITY_COORDS:
            return 'Jilin City'

    return None

def clean_city_name_for_map(name):
    """
    最终清理和验证城市名称，确保它匹配拼音版的 COMPREHENSIVE_CITY_COORDS 键。
    这个函数现在期望输入已经是拼音名称。
    """
    if pd.isna(name): return None
    name_str = str(name).strip()
    
    if name_str in PINYIN_COMPREHENSIVE_CITY_COORDS: return name_str
    
    # 尝试移除常见后缀 (以防之前的步骤没有完全移除)
    cleaned_name = re.sub(r'(City|County|District|Region|Prefecture|AutonomousRegion|Province|Shi|Xian|Qu|Zizhiqu)$', '', name_str, flags=re.IGNORECASE).strip()
    if cleaned_name in PINYIN_COMPREHENSIVE_CITY_COORDS: return cleaned_name
    
    # 再次进行大小写不敏感匹配
    for standard_name_pinyin in PINYIN_COMPREHENSIVE_CITY_COORDS.keys():
        if cleaned_name.lower() == standard_name_pinyin.lower():
            return standard_name_pinyin
            
    return None

@st.cache_data
def load_and_clean_data(master_file, hh_file):
    global PINYIN_COMPREHENSIVE_CITY_CODE_MAP, PINYIN_COMPREHENSIVE_CITY_COORDS, PINYIN_PROVINCE_COORDS

    try:
        # 动态创建拼音版本的字典
        PINYIN_COMPREHENSIVE_CITY_COORDS = {
            _to_pinyin_capitalized(k): v for k, v in COMPREHENSIVE_CITY_COORDS.items() if _to_pinyin_capitalized(k) is not None
        }
        PINYIN_PROVINCE_COORDS = {
            _to_pinyin_capitalized(k): v for k, v in PROVINCE_COORDS.items() if _to_pinyin_capitalized(k) is not None
        }
        # 更新 COMPREHENSIVE_CITY_CODE_MAP 的值也为拼音
        PINYIN_COMPREHENSIVE_CITY_CODE_MAP = {
            code: _to_pinyin_capitalized(city_name) 
            for code, city_name in COMPREHENSIVE_CITY_CODE_MAP.items() 
            if _to_pinyin_capitalized(city_name) is not None
        }


        # 只读取需要的列
        master_cols = ['hhid', 'rural', 'total_debt', 'total_asset', 'weight_hh', 'total_income', 
                       'city_lab', 'city_level', 'region', 'prov']
        hh_cols = ['hhid', 'house01num']
        
        # 处理 Streamlit 文件上传或本地文件路径
        if isinstance(master_file, str):
            master = pd.read_csv(master_file, low_memory=False, usecols=lambda x: x in master_cols)
            hh = pd.read_csv(hh_file, low_memory=False, usecols=lambda x: x in hh_cols)
        else: # Streamlit uploaded file (BytesIO)
            master = pd.read_csv(master_file, low_memory=False, usecols=lambda x: x in master_cols)
            hh_file.seek(0) # Reset pointer for hh_file in case it was read before
            hh = pd.read_csv(hh_file, low_memory=False, usecols=lambda x: x in hh_cols)
            
        df = master.merge(hh[['hhid', 'house01num']], on='hhid', how='left')
        
        numeric_cols = ['rural', 'total_debt', 'total_asset', 'weight_hh', 'total_income']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df[df['weight_hh'] > 0].copy()
        df['total_debt'] = df['total_debt'].fillna(0).clip(lower=0)
        df['total_income'] = df['total_income'].fillna(0).clip(lower=0)
        
        # ==== 核心改动：将原始中文列转换为拼音，然后进行映射 ====
        if 'city_lab' in df.columns:
            df['city_raw'] = df['city_lab'] # 保留原始中文
            # 先将原始值（代码或中文）转换为拼音或映射到的拼音
            df['city_pinyin_temp'] = df['city_lab'].apply(lambda x: convert_city_name_advanced(x, PINYIN_COMPREHENSIVE_CITY_CODE_MAP))
            # 再进行最终的清理和匹配，确保与 PINYIN_COMPREHENSIVE_CITY_COORDS 兼容
            df['final_city_name'] = df['city_pinyin_temp'].apply(clean_city_name_for_map)
        else:
            df['final_city_name'] = None

        if 'prov' in df.columns:
            # 直接将省份列的中文转换为拼音，并与 PINYIN_PROVINCE_COORDS 键进行匹配
            df['prov_pinyin_temp'] = df['prov'].apply(_to_pinyin_capitalized)
            df['prov'] = df['prov_pinyin_temp'].apply(lambda x: x if x in PINYIN_PROVINCE_COORDS else None)
        # =======================================================
        
        if 'city_level' in df.columns:
            def map_city_tier(level):
                if pd.isna(level): return None
                level = str(level).strip()
                # 兼容中文和英文分级
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
        st.error(f"数据加载失败: {e}")
        return None

# ==========================================
# 3. 图表生成函数
#    这些函数现在将期望 `df['final_city_name']` 和 `df['prov']` 已经是拼音。
#    并且 `COMPREHENSIVE_CITY_COORDS` 和 `PROVINCE_COORDS` 的查找也应该对应拼音。
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
    # 这里 `df['prov']` 已经经过拼音转换
    df_prov = df.groupby('prov', group_keys=False, dropna=True).apply(
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
        # 查找 PINYIN_PROVINCE_COORDS
        if prov_name in PINYIN_PROVINCE_COORDS: return pd.Series([PINYIN_PROVINCE_COORDS[prov_name][1], PINYIN_PROVINCE_COORDS[prov_name][0]])
        return pd.Series([np.nan, np.nan]) # Changed to np.nan for consistency

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

    if df_valid.empty: return None

    # 1. 数据计算
    df_city_agg = df_valid.groupby('final_city_name', dropna=True).apply(
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

    # 2. X 轴标签 (现在会显示拼音城市名)
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
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
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
    
    df_city = df.groupby('final_city_name', dropna=True).apply(
        lambda x: pd.Series({
            'w_debt': (x['total_debt'] * x['weight_hh']).sum(),
            'w_income': (x['total_income'] * x['weight_hh']).sum(),
            'sum_weight': x['weight_hh'].sum()
        }), include_groups=False
    ).reset_index()

    df_city['avg_debt'] = df_city['w_debt'] / df_city['sum_weight']
    df_city['d_i_ratio'] = df_city.apply(
        lambda x: x['w_debt'] / x['w_income'] if x['w_income'] > 0 else np.nan, axis=1 # Use np.nan
    )

    def get_lat_lon_city(city_name):
        # 查找 PINYIN_COMPREHENSIVE_CITY_COORDS
        if city_name in PINYIN_COMPREHENSIVE_CITY_COORDS:
            coords = PINYIN_COMPREHENSIVE_CITY_COORDS[city_name]
            return pd.Series([coords[1], coords[0]])
        return pd.Series([np.nan, np.nan]) # Changed to np.nan for consistency

    df_city[['lat', 'lon']] = df_city['final_city_name'].apply(get_lat_lon_city)
    df_plot = df_city.dropna(subset=['lat', 'lon', 'd_i_ratio']) # Ensure ratio is also present
    
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
        height=600, # Explicit height for Plotly charts
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

    # 确保用于路径的列没有 NaN，否则 Plotly 会报错
    df_sun['tier_label'] = df_sun['tier_label'].fillna('Unknown')
    df_sun['region_en'] = df_sun['region_en'].fillna('Unknown')
    df_sun['prov'] = df_sun['prov'].fillna('Unknown') # `prov` 列现在是拼音

    required_cols = ['rural_str', 'region_en', 'prov', 'tier_label']
    for col in required_cols:
        if col not in df_sun.columns: 
            st.warning(f"Sunburst chart missing required column: {col}")
            return None
    
    df_sun['weighted_debt'] = df_sun['total_debt'] * df_sun['weight_hh']
    # 过滤掉负债为0的家庭，以免在旭日图中占据空间
    df_agg = df_sun[df_sun['weighted_debt'] > 0].groupby(required_cols)['weighted_debt'].sum().reset_index()
    
    if df_agg.empty: 
        st.info("Insufficient data (or no debt) to create Sunburst Chart.")
        return None

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
        files_dict = {f.name: f for f in upload_files}
        for name in files_dict.keys():
            if "master" in name.lower(): master_path = files_dict[name]
            if "hh" in name.lower(): hh_path = files_dict[name]
    
    # 尝试加载本地默认文件
    if not master_path and os.path.exists(DEFAULT_MASTER):
        master_path = DEFAULT_MASTER
    if not hh_path and os.path.exists(DEFAULT_HH): # 只有当master_path找到时，才去找hh_path
        hh_path = DEFAULT_HH
        
    st.info("若未上传文件，将尝试加载默认路径或当前目录文件。")
    
    st.markdown("---")
    st.header("🗺️ 地图配置") # Added map configuration to sidebar
    map_level = st.selectbox(
        "选择地图粒度",
        options=["Provincial", "City"],
        index=0,
        help="选择地图的可视化粒度：省份或城市。"
    )

st.title("🇨🇳 中国家庭债务分析大屏")
st.markdown("### 宏观区域与城市分析")

if master_path and hh_path:
    with st.spinner("正在加载和处理数据..."):
        df = load_and_clean_data(master_path, hh_path)

    if df is not None:
        kpi_cols = st.columns(4)
        total_weight = df['weight_hh'].sum()
        weighted_avg_debt = (df['total_debt'] * df['weight_hh']).sum() / total_weight
        weighted_avg_income = (df['total_income'] * df['weight_hh']).sum() / total_weight
        debt_ratio = weighted_avg_debt / weighted_avg_income if weighted_avg_income > 0 else 0
        
        # 加权计算有负债家庭的比例
        indebted_households_weight = df[df['total_debt'] > 0]['weight_hh'].sum()
        total_households_weight = df['weight_hh'].sum()
        households_with_debt_ratio = indebted_households_weight / total_households_weight if total_households_weight > 0 else 0


        kpi_cols[0].metric("家庭平均债务", f"¥{weighted_avg_debt/10000:,.1f} 万") # Adjusted to 10k RMB
        kpi_cols[1].metric("家庭平均收入", f"¥{weighted_avg_income/10000:,.1f} 万") # Adjusted to 10k RMB
        kpi_cols[2].metric("债务收入比", f"{debt_ratio:.1%}", delta_color="inverse")
        kpi_cols[3].metric("有负债家庭比例", f"{households_with_debt_ratio:.1%}") # New KPI

        st.markdown("---")
        
        # Row 1
        st.header("🔍 1. 宏观概览：城乡与区域对比")
        row1_col1, row1_col2 = st.columns([1, 1])
        with row1_col1:
            st.subheader("1.1 城乡债务负担与风险")
            st_pyecharts(plot_urban_rural(df), height="380px")
        with row1_col2:
            st.subheader("1.2 区域债务构成与风险水平")
            chart_reg = plot_regional_stack(df)
            if chart_reg: st_pyecharts(chart_reg, height="380px")
            else: st.info("区域数据不足。")

        st.markdown("---")
        
        # Row 2 - Geographic Map
        st.header(f"🗺️ 2. 地理分布：债务负担与风险")
        st.subheader(f"2.1 {map_level} 债务地图") # Dynamic title based on selection
        
        # 调用合并后的地图函数
        fig_map_combined = plot_geo_debt_map_comprehensive(df) if map_level == "City" else plot_china_map_plotly(df)
        if fig_map_combined:
            st.plotly_chart(fig_map_combined, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.warning(f"没有足够的 {map_level} 数据或坐标匹配失败来生成地图。")
            
        st.markdown("---")

        # Row 3 - Sunburst Chart (within an expander)
        st.header("🧱 3. 债务结构分解")
        with st.expander("点击展开：债务旭日图 (城乡 > 区域 > 省份 > 城市分级)", expanded=False):
            chart_sun = plot_debt_sunburst(df)
            if chart_sun:
                st.plotly_chart(chart_sun, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.warning("旭日图所需数据缺失或不足。")
                
        st.markdown("---")

        # Row 4 - City Tier Box Plot and City Ranking
        st.header("📉 4. 城市详细对比")
        row3_col1, row3_col2 = st.columns([1, 1])
        with row3_col1:
            st.subheader("4.1 城市分级债务分布 (箱线图)")
            chart_tier = plot_city_tier_boxplot(df)
            if chart_tier: 
                st.plotly_chart(chart_tier, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("城市分级债务分布数据不足。")
            
        with row3_col2:
            st.subheader("4.2 城市债务排名 (前5与后5)")
            chart_rank = plot_city_rank(df)
            if chart_rank: st_pyecharts(chart_rank, height="450px")
            else: st.info("城市排名数据不足。")

    else:
        st.error("无法处理数据，请检查文件格式。")
else:
    st.warning("⚠️ 数据文件未找到。请上传 CSV 文件或确保默认文件存在。")
