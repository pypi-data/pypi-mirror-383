from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from stkweight.core import plot_weight_candlestick_daily_full_range_with_volume

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from stkweight.core import (
    plot_weight_candlestick_daily_full_range_with_volume,
)  # 确保这个模块和函数可用
import dash

df = pd.read_csv("tests/resources/weight.csv", index_col=0)
df2 = pd.read_csv("tests/resources/weight2.csv", index_col=0)

df.columns = [i.strip() for i in df.columns]
df2.columns = [i.strip() for i in df2.columns]

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# app = Dash(__name__)


app.layout = html.Div(
    [
        html.Div(
            children="Weight Manager K",
            className="row",
            style={"textAlign": "center", "color": "purple", "fontSize": 30},
        ),
        html.H4("Weight_Manager_K"),
        html.Div(
            [
                html.Label("Enter Token: "),
                dcc.Input(
                    id="token-input",
                    type="text",
                    value="weight_data_1",  # 默认值，方便测试
                    placeholder="e.g., weight_data_1",
                    style={"marginRight": "10px"},
                ),
                html.Button("Load Data", id="load-data-button", n_clicks=0),
            ],
            style={"padding": "10px"},
        ),  # 简单样式使其居中显示
        dash_table.DataTable(
            id="table-editing-simple",
            columns=[{"name": i, "id": i} for i in df.columns],  # 更规范的列定义
            data=df.to_dict("records"),
            editable=True,  # 允许编辑
            row_deletable=True,  # 允许删除行
            page_size=10,  # 每页显示10行
            style_table={
                "overflowX": "auto",
                "minWidth": "100%",
            },  # 确保表格宽度自适应并支持滚动
            style_cell={
                "textAlign": "left",
                "minWidth": "100px",
                "width": "100px",
                "maxWidth": "180px",
            },
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
        ),
        dcc.Graph(id="graph-content"),
    ]
)

"""
@app.callback(
    Output("graph-content", "figure"),
    Input("table-editing-simple", "data"), # 修正：使用 'data' 属性获取表格的全部数据
    # Input("table-editing-simple", "data_previous") # 可以用来检测数据是否真的改变
)
def display_candlestick(rows):
    # rows 参数将包含当前表格的所有数据，是一个列表字典

    updated_df = pd.DataFrame(rows)


    print("\n--- 每日全范围波动蜡烛图 (带净卡路里成交量) 示例 ---")
    ma_config_daily = [
        {'period': 5, 'price_col': 'Eve_Weight', 'color': 'blue'},
        {'period': 10, 'price_col': 'Mon_Weight', 'color': 'purple'}
    ]

    fig = plot_weight_candlestick_daily_full_range_with_volume(
        updated_df,
        ma_configs=ma_config_daily,
        show_calorie_volume=True,
        show=False, # 在Dash回调中通常不需要
        # file_path="./interactive_bar_chart.html" # 在Dash回调中通常不需要
    )
    return fig

"""


@app.callback(
    Output("table-editing-simple", "data"),
    Output("table-editing-simple", "columns"),
    Output("graph-content", "figure"),  # 直接更新图表
    Input("load-data-button", "n_clicks"),  # 监听加载按钮的点击
    Input("token-input", "value"),  # 监听Token输入框的值
    prevent_initial_call=True,  # 避免应用启动时自动触发
)
def update_data_and_graph_by_token(n_clicks, token_value):
    print(n_clicks, "n_clicks")
    print(token_value, "token_value")
    if n_clicks == 0:
        # 初始加载时，n_clicks可能为None，我们希望prevent_initial_call处理
        # 或者如果你希望初始也显示数据，可以移除prevent_initial_call=True并处理这里的逻辑
        raise dash.exceptions.PreventUpdate

    if token_value == "123":

        empty_columns = [{"name": i, "id": i} for i in df.columns]
        empty_figure = go.Figure().update_layout(
            title_text="Please enter a token to load data."
        )
        table_data = df.to_dict("records")
        df_p = df
        empty_columns
        empty_figure

    elif token_value == "223":

        empty_columns = [{"name": i, "id": i} for i in df2.columns]
        empty_figure = go.Figure().update_layout(
            title_text="Please enter a token to load data."
        )
        table_data = df2.to_dict("records")
        df_p = df2
        empty_columns
        empty_figure

    print("\n--- 每日全范围波动蜡烛图 (带净卡路里成交量) 示例 ---")
    ma_config_daily = [
        {"period": 5, "price_col": "Eve_Weight", "color": "blue"},
        {"period": 10, "price_col": "Mon_Weight", "color": "purple"},
    ]

    fig = plot_weight_candlestick_daily_full_range_with_volume(
        df_p,
        ma_configs=ma_config_daily,
        show_calorie_volume=True,
        show=False,  # 在Dash回调中通常不需要
        # file_path="./interactive_bar_chart.html" # 在Dash回调中通常不需要
    )

    return table_data, empty_columns, fig


# --- 回调函数：DataTable编辑后更新K线图 ---
# 这个回调依然保持独立，只负责在DataTable数据被编辑时更新图表
@app.callback(
    Output(
        "graph-content", "figure", allow_duplicate=True
    ),  # allow_duplicate=True 允许同一个Output被多个回调更新
    Input("table-editing-simple", "data"),
    Input("table-editing-simple", "columns"),
    prevent_initial_call=True,  # 避免应用启动时自动触发
)
def update_graph_on_table_edit(rows, columns):
    updated_df = pd.DataFrame(rows)

    # numeric_cols = ['Mon_Weight', 'Eve_Weight', 'NetCalorie', 'MaxWeight', 'MinWeight', 'OpenWeight', 'CloseWeight']
    # for col in numeric_cols:
    #     if col in updated_df.columns:
    #         updated_df[col] = pd.to_numeric(updated_df[col], errors='coerce')

    # required_plot_cols = ['Mon_Weight', 'Eve_Weight', 'NetCalorie', 'OpenWeight', 'CloseWeight', 'MaxWeight', 'MinWeight']
    # if not all(col in updated_df.columns for col in required_plot_cols):
    #     missing_cols = [col for col in required_plot_cols if col not in updated_df.columns]
    #     return go.Figure().update_layout(
    #         title_text=f"Error: Missing required columns for K-line plot: {', '.join(missing_cols)}",
    #         height=300
    #     )

    # plot_df = updated_df.dropna(subset=required_plot_cols, how='all')

    ma_config_daily = [
        {"period": 5, "price_col": "Eve_Weight", "color": "blue"},
        {"period": 10, "price_col": "Mon_Weight", "color": "purple"},
    ]
    figure = plot_weight_candlestick_daily_full_range_with_volume(
        updated_df,
        ma_configs=ma_config_daily,
        show_calorie_volume=True,
        show=False,
    )
    return figure


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
