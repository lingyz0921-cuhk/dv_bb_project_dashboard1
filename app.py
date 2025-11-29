import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CHFS 数据大屏", layout="wide")

st.title("🇨🇳 CHFS 数据可视化大屏")

# 加载数据
@st.cache_data
def load_data():
    try:
        master = pd.read_csv("chf_data/chfs2019_master_202112.csv", low_memory=False)
        hh = pd.read_csv("chf_data/chfs2019_ind_202112.csv", low_memory=False)
        
        # 合并
        df = master.merge(hh[['hhid', 'house01num']], on='hhid', how='left')
        
        # 数据清洗
        for col in ['rural', 'total_debt', 'total_asset', 'weight_hh', 'total_income']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df[df['weight_hh'] > 0].copy()
        df['total_debt'] = df['total_debt'].fillna(0)
        df['total_income'] = df['total_income'].fillna(0)
        df.loc[df['total_debt'] < 0, 'total_debt'] = 0
        df.loc[df['total_income'] < 0, 'total_income'] = 0
        
        return df
    except Exception as e:
        st.error(f"❌ 数据加载失败: {e}")
        return None

df = load_data()

if df is not None:
    st.success(f"✅ 数据加载成功！共 {len(df):,} 行")
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_debt = (df['total_debt'] * df['weight_hh']).sum() / df['weight_hh'].sum()
        st.metric("平均家庭债务", f"¥{avg_debt:,.0f}")
    
    with col2:
        avg_asset = (df['total_asset'] * df['weight_hh']).sum() / df['weight_hh'].sum()
        st.metric("平均家庭资产", f"¥{avg_asset:,.0f}")
    
    with col3:
        debt_ratio = avg_debt / avg_asset if avg_asset > 0 else 0
        st.metric("债务/资产比", f"{debt_ratio:.2%}")
    
    with col4:
        avg_income = (df['total_income'] * df['weight_hh']).sum() / df['weight_hh'].sum()
        st.metric("平均家庭收入", f"¥{avg_income:,.0f}")
    
    st.divider()
    
    # 城乡对比
    st.subheader("城乡债务对比")
    df_rural = df.groupby('rural').apply(
        lambda x: pd.Series({
            'avg_debt': (x['total_debt'] * x['weight_hh']).sum() / x['weight_hh'].sum(),
            'count': len(x)
        }), include_groups=False
    ).reset_index()
    df_rural['rural_name'] = df_rural['rural'].map({0: 'Urban', 1: 'Rural'})
    
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df_rural.set_index('rural_name')['avg_debt'])
    with col2:
        st.dataframe(df_rural[['rural_name', 'avg_debt', 'count']], use_container_width=True)
    
    st.divider()
    
    # 数据预览
    st.subheader("数据预览")
    st.dataframe(df.head(20), use_container_width=True)
    
else:
    st.error("数据加载失败，请检查文件路径")