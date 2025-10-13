import pandas as pd
import os
from datetime import datetime
from src.bank_package.log import Log


class BankStatementAnalyzer:
    def __init__(self, log_level: str = "info"):
        """
        初始化银行流水分析器。

        Args:
            log_level (str): 日志级别，可选值为 'debug', 'info', 'warning', 'error', 'critical'。
                             默认为 'info'。
        """
        self.log = Log
        self.log.reset_level(log_level)
        self.df = None
        self.log.logger.info("BankStatementAnalyzer initialized.")

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        从指定的CSV文件中加载银行流水数据。

        Args:
            file_path (str): CSV 文件的路径。

        Returns:
            pd.DataFrame: 加载后的银行流水数据。

        Raises:
            FileNotFoundError: 如果文件不存在。
            Exception: 如果加载数据过程中发生其他错误。
        """
        if not os.path.exists(file_path):
            self.log.logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            self.df = pd.read_csv(file_path)
            self.log.logger.info(
                f"成功加载数据: {file_path}, 包含 {len(self.df)} 条记录。"
            )
            return self.df
        except Exception as e:
            self.log.logger.error(f"加载数据失败: {e}")
            raise

    def standardize_transactions(
        self, column_name: str, replace_rules: dict
    ) -> pd.DataFrame:
        """
        统一银行流水中特定列（如“对方户名”）的名称。

        Args:
            column_name (str): 需要进行标准化的列名。
            replace_rules (dict): 替换规则字典，键为原始名称，值为替换后的标准名称。

        Returns:
            pd.DataFrame: 标准化后的银行流水数据。
                          如果数据未加载或指定列不存在，则返回 None 或原始 DataFrame。
        """
        if self.df is None:
            self.log.logger.warning("数据未加载，请先调用 load_data 方法。")
            return None

        if column_name not in self.df.columns:
            self.log.logger.warning(f"列 '{column_name}' 不存在，跳过标准化处理。")
            return self.df

        original_count = self.df[column_name].nunique()
        self.df[column_name] = self.df[column_name].replace(replace_rules)
        new_count = self.df[column_name].nunique()
        self.log.logger.info(
            f"列 '{column_name}' 标准化完成。原始唯一值数量: {original_count}, 标准化后唯一值数量: {new_count}。"
        )
        return self.df

    def categorize_payments(
        self,
        time_column: str = "交易时间",
        amount_column: str = "发生额",
        counterparty_column: str = "对方户名",
        summary_column: str = "业务摘要",
    ) -> pd.DataFrame:
        """
        为每笔交易自动添加一个“支付类别”标签。

        Args:
            time_column (str): 交易时间列的名称，默认为 '交易时间'。
            amount_column (str): 发生额列的名称，默认为 '发生额'。
            counterparty_column (str): 对方户名列的名称，默认为 '对方户名'。
            summary_column (str): 业务摘要列的名称，默认为 '业务摘要'。

        Returns:
            pd.DataFrame: 添加“支付类别”列后的银行流水数据。

        Raises:
            ValueError: 如果缺少必要的列。
            Exception: 如果时间列转换失败。
        """
        if self.df is None:
            self.log.logger.warning("数据未加载，请先调用 load_data 方法。")
            return None

        required_columns = [
            time_column,
            amount_column,
            counterparty_column,
            summary_column,
        ]
        for col in required_columns:
            if col not in self.df.columns:
                self.log.logger.error(f"缺少必要列 '{col}'，无法进行支付类别归类。")
                raise ValueError(f"缺少必要列 '{col}'，无法进行支付类别归类。")

        self.df["支付类别"] = "未知"

        # 确保时间列是datetime类型
        try:
            self.df[time_column] = pd.to_datetime(self.df[time_column])
        except Exception as e:
            self.log.logger.error(f"时间列 '{time_column}' 转换失败: {e}")
            raise

        # 定义分类规则
        def apply_category(row):
            counterparty = str(row[counterparty_column])
            amount = row[amount_column]
            transaction_time = row[time_column].hour
            summary = str(row[summary_column])

            # 收入
            if amount > 0:
                if "工资" in summary or "薪资" in summary:
                    return "工资收入"
                elif "利息" in summary:
                    return "利息收入"
                elif "转账" in summary:
                    return "转账收入"
                return "其他收入"

            # 支出
            # 工作餐
            if (
                "卤肉饭" in counterparty
                or "沙县小吃" in counterparty
                or (20 <= abs(amount) <= 50 and 11 <= transaction_time <= 14)
            ):
                return "工作餐"
            # 大餐
            if (
                "火锅" in counterparty
                or "烧烤" in counterparty
                or (abs(amount) > 50 and 18 <= transaction_time <= 22)
            ):
                return "大餐"
            # 会员费
            if "会员" in summary or "服务费" in summary or "年费" in summary:
                return "会员费"
            # 交通
            if "公交" in summary or "地铁" in summary or "打车" in summary:
                return "交通费"
            # 购物
            if "购物" in summary or "超市" in summary or "百货" in summary:
                return "购物"
            # 娱乐
            if "电影" in summary or "KTV" in summary or "游戏" in summary:
                return "娱乐"
            # 医疗
            if "医院" in summary or "药店" in summary:
                return "医疗"
            # 住房
            if "房租" in summary or "物业" in summary or "水电" in summary:
                return "住房"
            # 其他支出
            return "其他支出"

        self.df["支付类别"] = self.df.apply(apply_category, axis=1)
        self.log.logger.info("支付类别归类完成。")
        return self.df

    def analyze_income_expense_ratio(
        self, amount_column: str = "发生额", exclude_threshold: float = 8000
    ) -> dict:
        """
        计算一段时间内的总收入与总支出的比率。

        Args:
            amount_column (str): 发生额列的名称，默认为 '发生额'。
            exclude_threshold (float): 排除大额交易的阈值，超过此绝对值的交易不计入分析。默认为 8000。

        Returns:
            dict: 包含总收入、总支出和收支比例的字典。
                  如果总支出为零，收支比例为 "N/A"。

        Raises:
            ValueError: 如果缺少必要的列。
        """
        if self.df is None:
            self.log.logger.warning("数据未加载，请先调用 load_data 方法。")
            return None

        if amount_column not in self.df.columns:
            self.log.logger.error(
                f"缺少必要列 '{amount_column}'，无法进行收支比例分析。"
            )
            raise ValueError(f"缺少必要列 '{amount_column}'，无法进行收支比例分析。")

        # 过滤掉大额交易
        filtered_df = self.df[abs(self.df[amount_column]) <= exclude_threshold].copy()

        total_income = filtered_df[filtered_df[amount_column] > 0][amount_column].sum()
        total_expense = abs(
            filtered_df[filtered_df[amount_column] < 0][amount_column].sum()
        )

        if total_expense == 0:
            self.log.logger.warning("没有支出记录，无法计算收支比例。")
            return {"总收入": total_income, "总支出": total_expense, "收支比例": "N/A"}

        ratio = total_income / total_expense
        self.log.logger.info(
            f"收支比例分析完成。总收入: {total_income:.2f}, 总支出: {total_expense:.2f}, 比例: {ratio:.2f}。"
        )
        return {"总收入": total_income, "总支出": total_expense, "收支比例": ratio}
