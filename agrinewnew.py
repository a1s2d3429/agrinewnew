import streamlit as st
import pandas as pd
import os

# 页面基础全局配置
st.set_page_config(page_title="赣州富硒农产品产销便民服务平台", layout="wide")
st.title("赣州富硒农产品产销便民服务平台")

# 读取CSV，兼容Windows中文GBK编码
df = pd.read_csv("data.csv", encoding="gbk")
st.success("数据加载完成，可切换下方板块查看对应内容")

# 左侧身份下拉选择框
identity = st.selectbox("请选择您的身份", ["消费者（购买用户）", "经销商（收购商）", "农户（种植户）"])

# ---------------------- 1、消费者板块：完整表格 + 本地图片图文卡片（保留你原本读取本地图片逻辑） ----------------------
if identity == "消费者（购买用户）":
    st.header("🛒 消费者产品选购专区")
    st.subheader("全部富硒农产品介绍与售价（完整数据表）")
    # 保留原始完整数据表格
    consumer_df = df[["产品名称", "产品分类", "产地", "单价", "富硒等级", "上市季节"]]
    st.dataframe(consumer_df, use_container_width=True)

    st.divider()
    st.subheader("📖 农产品百科图文详情（下方可查看单品图文介绍）")
    st.markdown("每条数据自动匹配对应产品图片，信息全部读取自表格")
    st.divider()

    # 循环读取CSV每一行数据，生成图文卡片（本地图片读取逻辑）
    for index, row in df.iterrows():
        product_name = row["产品名称"]
        # 拼接本地图片路径
        img_path = f"./product_img/{product_name}.jpg"

        col1, col2 = st.columns([1, 3])
        with col1:
            # 判断图片是否存在，不存在则展示默认线上占位图
            if os.path.exists(img_path):
                st.image(img_path, width=220, caption=product_name)
            else:
                st.image("https://img0.baidu.com/it/u=3511123102,3922111230&fm=253&fmt=auto&app=138&f=JPEG?w=800&h=800", width=220, caption="暂无自定义产品图")

        with col2:
            st.subheader(f"【{product_name}】产品详情")
            # 自动从表格读取所有数据，以文字展示
            st.markdown(f"""
            - 产品分类：{row['产品分类']}
            - 原产地：{row['产地']}
            - 零售单价：{row['单价']}
            - 富硒品质等级：{row['富硒等级']}
            - 最佳采购/上市时段：{row['上市季节']}
            """)
            st.info(f"选购说明：{product_name}产自赣州富硒土壤产区，天然富含硒元素，推荐在{row['上市季节']}采购，新鲜度更高。")
        st.divider()

# ---------------------- 2、经销商板块：全新筛选+成本测算+仓储提示完整功能 ----------------------
elif identity == "经销商（收购商）":
    st.header("🤝 经销商收购参考专区")
    st.subheader("全部富硒农产品产地、单价、供货销量明细")
    # 原有明细表格保留
    dealer_df = df[["产品名称", "产品分类", "产地", "单价", "月度销量"]]
    st.dataframe(dealer_df, use_container_width=True)
    st.info("提示：本表展示各县域特色富硒单品，可筛选品类、价格匹配您的收购需求。")

    st.divider()
    st.subheader("🔍 货源精准筛选工具")
    # 品类筛选
    pick_category = st.selectbox("筛选收购品类", ["全品类"] + df["产品分类"].unique().tolist())
    # 价格区间滑块
    min_p = float(df["单价"].min())
    max_p = float(df["单价"].max())
    low_price, high_price = st.slider("收购单价区间筛选", min_p, max_p, (min_p, max_p))

    # 筛选后数据
    filter_df = df.copy()
    if pick_category != "全品类":
        filter_df = filter_df[filter_df["产品分类"] == pick_category]
    filter_df = filter_df[(filter_df["单价"] >= low_price) & (filter_df["单价"] <= high_price)]
    st.dataframe(filter_df[["产品名称", "产品分类", "产地", "单价", "月度销量"]], use_container_width=True)

    st.divider()
    st.subheader("🧮 进货成本测算工具")
    pick_goods = st.selectbox("选择要采购的单品", filter_df["产品名称"].tolist())
    goods_data = filter_df[filter_df["产品名称"] == pick_goods].iloc[0]
    buy_jin = st.number_input("计划采购斤数", min_value=0, value=500)
    all_cost = buy_jin * goods_data["单价"]
    # 货源等级判断
    if goods_data["月度销量"] >= 1000:
        supply_tip = "✅ 稳定大批量货源，适合长期批量收购"
    elif goods_data["月度销量"] >= 500:
        supply_tip = "🟡 中等稳定货源，常规零售采购适配"
    else:
        supply_tip = "🟠 少量精品货源，适合高端精品渠道"

    st.success(f"""
    单品：{pick_goods} | 产地：{goods_data['产地']} | 单价：{goods_data['单价']}元/斤
    采购{buy_jin}斤总进货成本：{all_cost:.2f}元
    供货规模提示：{supply_tip}
    """)

    st.divider()
    st.subheader("📦 仓储进货小贴士")
    if "茶叶" in goods_data["产品分类"] or "深加工类" in goods_data["产品分类"]:
        st.info("干货/深加工产品储存周期长，可趁货源充足时批量囤货，降低频繁运输成本")
    elif "新鲜蔬菜类" in goods_data["产品品类"]:
        st.warning("生鲜蔬菜保鲜周期短，建议按短期销量分批次少量收购，避免腐烂损耗")
    elif "粮食类" in goods_data["产品品类"]:
        st.info("粮食类易储存，全年可稳定补货，适合常年备货")
    elif "畜禽蛋类" in goods_data["产品品类"]:
        st.warning("蛋类需低温仓储，真空包装款可长期备货，新鲜款少量多次采购")

# ---------------------- 3、农户板块：保留表格、收益计算器、种植科普；图表模块完整注释预留，后续加数据再解除注释 ----------------------
elif identity == "农户（种植户）":
    st.header("👨‍🌾 农户种植参考专区")
    st.subheader("各县农产品月度总销量统计表（用来判断今年种什么更好卖）")
    # 原有销量统计表保留
    farmer_data = df.groupby("产地")["月度销量"].sum().reset_index()
    farmer_data.columns = ["产地", "月度量"]
    st.dataframe(farmer_data, use_container_width=True)
    st.info("提示：表格里销量越高的县域品类，本地市场需求越大，优先规划种植，减少滞销风险。")

    st.divider()
    # ===== 暂时注释可视化图表模块，后续补充多地区数据再取消注释恢复 =====
    """
    st.subheader("📊 本县农产品销量可视化分析")
    # 筛选自己的种植县域
    select_county = st.selectbox("请选择您的种植县城", list(df["产地"].unique()))
    county_df = df[df["产地"] == select_county]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{select_county}各类产品销量排行")
        st.bar_chart(county_df, x="产品名称", y="月度供货量", use_container_width=True)
    with col2:
        st.subheader(f"{select_county}品类销量占比")
        category_sale = county_df.groupby("产品品类")["月度供货量"].sum().reset_index()
        st.dataframe(category_sale, hide_index=True)
    """

    st.subheader("💰 种植收益预估计算器")
    # 收益测算
    select_county = st.selectbox("请选择您的种植县城", list(df["产地"].unique()))
    county_df = df[df["产地"] == select_county]
    select_product = st.selectbox("选择您计划种植的产品", county_df["产品名称"].tolist())
    product_info = county_df[county_df["产品名称"] == select_product].iloc[0]
    plant_weight = st.number_input("预计种植产出多少斤", min_value=0, value=1000)
    total_income = plant_weight * product_info["单价"]
    st.success(f"""
    品类：{select_product} | 本地零售价：{product_info['单价']}元/斤
    产出{plant_weight}斤预估总收入：{total_income:.2f} 元
    """)

    st.divider()
    st.subheader("🌱 本地种植科普建议")
    category_sale = county_df.groupby("产品分类")["月度销量"].sum().reset_index()
    hot_category = category_sale.sort_values('月度供货量',ascending=False).iloc[0]['产品分类']
    st.markdown(f"""
    您所在{select_county}属于天然富硒土壤，产出农产品更容易达到优质富硒等级，收购溢价更高。
    本地热销品类：{hot_category}，市场需求最大。
    该品类最佳上市供货时段：{product_info['上市季节']}，集中上市时收购商拿货量更高。
    """)
