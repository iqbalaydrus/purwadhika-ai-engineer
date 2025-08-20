from datetime import date
from enum import StrEnum
from typing import Optional, Type

import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as sa

db_url = "mysql://root:yu6queith2ooY6ah@127.0.0.1:3306/grocery_chain"


def read_input[T](prompt: str, target_type: Type[T]) -> T:
    t = input(prompt)
    try:
        if target_type is date:
            return date.fromisoformat(t)
        else:
            return target_type(t)
    except (TypeError, ValueError):
        print(f"Not a valid {target_type.__name__} value")
        return read_input(prompt, target_type)


def read_data(stmt=None, params=None) -> pd.DataFrame:
    if stmt is None:
        stmt = "select * from transactions"
    return pd.read_sql(
        stmt,
        db_url,
        params=params,
        parse_dates={"transaction_date": {"format": "%Y-%m-%d"}},
        index_col="tx_id",
    )


class SubChoice:
    summary: str
    entries: list["Choice"]

    def __init__(self, choices: list["Choice"], summary: str) -> None:
        self.summary = summary
        self.entries = choices


class Choice:
    description: Optional[str]
    sub_choice: Optional[SubChoice] = None

    def __init__(
        self,
        description: Optional[str] = None,
        sub_choice: Optional[SubChoice] = None,
    ):
        self.description = description
        self.sub_choice = sub_choice

    def action(self):
        pass

    def dialog(self):
        if self.sub_choice:
            while True:
                dialog = self.sub_choice.summary + "\n"
                for idx, choice in enumerate(self.sub_choice.entries):
                    dialog += f"{idx+1}. {choice.description}\n"
                dialog += f"{len(self.sub_choice.entries)+1}. Exit\n"
                print(dialog)
                choice_num = input("Enter your choice: ")
                if (
                    choice_num.isdigit()
                    and 0 < int(choice_num) <= len(self.sub_choice.entries) + 1
                ):
                    choice_num = int(choice_num)
                    break
                else:
                    print(f"{choice_num} is not a valid choice.")
            if choice_num == len(self.sub_choice.entries) + 1:
                print("Thank you for using this program.")
                return None
            else:
                return self.sub_choice.entries[choice_num - 1].dialog()
        else:
            return self.action()


class AllColumns(StrEnum):
    tx_id = "tx_id"
    customer_id = "customer_id"
    store_name = "store_name"
    transaction_date = "transaction_date"
    aisle = "aisle"
    product_name = "product_name"
    quantity = "quantity"
    unit_price = "unit_price"
    total_amount = "total_amount"
    discount_amount = "discount_amount"
    final_amount = "final_amount"
    loyalty_points = "loyalty_points"
    empty = ""


class Operator(StrEnum):
    eq = "="
    ne = "!="
    lt = "<"
    lte = "<="
    gt = ">"
    gte = ">="


class ReadTable(Choice):
    def action(self):
        max_rows = read_input("Enter max rows: ", int)
        col_name = read_input(
            f"Enter column name to filter, empty to retrieve all [{'/'.join(AllColumns)}]: ",
            AllColumns,
        )
        if col_name == AllColumns.empty:
            stmt = "select * from transactions"
            params = None
        else:
            op = read_input(
                f"Enter operation [{'/'.join(Operator)}]: ",
                Operator,
            )
            val = read_input("Enter value to filter: ", str)
            stmt = f"select * from transactions where {col_name.value} {op.value} %(filter_val)s"
            params = {"filter_val": val}
        df = read_data(stmt=stmt, params=params)
        print(df.to_string(max_rows=max_rows))


class StatType(StrEnum):
    mean = "mean"
    p25 = "p25"  # extra
    p50 = "p50"  # extra
    p75 = "p75"  # extra
    std = "std"  # extra
    min = "min"  # extra
    max = "max"  # extra


class StatCols(StrEnum):
    quantity = "quantity"
    unit_price = "unit_price"
    total_amount = "total_amount"
    discount_amount = "discount_amount"
    final_amount = "final_amount"
    loyalty_points = "loyalty_points"


class ShowStats(Choice):
    def action(self):
        col_name = read_input(
            f"Enter column name [{'/'.join(StatCols)}]: ",
            StatCols,
        )
        stat_type = read_input(
            f"Enter statistics type [{'/'.join(StatType)}]: ",
            StatType,
        )
        series = read_data()[col_name]
        if stat_type == StatType.mean:
            print(series.mean())
        elif stat_type == StatType.p25:
            print(series.quantile(0.25))
        elif stat_type == StatType.p50:
            print(series.quantile(0.50))
        elif stat_type == StatType.p75:
            print(series.quantile(0.75))
        elif stat_type == StatType.std:
            print(series.std())
        elif stat_type == StatType.min:
            print(series.min())
        elif stat_type == StatType.max:
            print(series.max())
        else:
            print(f"Not a valid {stat_type}.")


class CategoryCols(StrEnum):
    store_name = "store_name"
    aisle = "aisle"
    product_name = "product_name"


class CategoryPlot(StrEnum):
    pie = "pie"
    bar = "bar"


class VisCategory(Choice):
    def action(self):
        col_name = read_input(
            f"Enter column name [{'/'.join(CategoryCols)}]: ",
            CategoryCols,
        )
        plot_type = read_input(
            f"Enter plot type [{'/'.join(CategoryPlot)}]: ",
            CategoryPlot,
        )
        df = read_data()
        df = df.groupby(col_name).agg(count=(col_name, "count"))
        if plot_type == CategoryPlot.pie:
            df.plot.pie(y="count")
        elif plot_type == CategoryPlot.bar:
            df.plot.bar(y="count")
        else:
            print(f"Not a valid {plot_type}.")
        plt.tight_layout()
        plt.show()


class HistogramCols(StrEnum):
    quantity = "quantity"
    unit_price = "unit_price"
    total_amount = "total_amount"
    discount_amount = "discount_amount"
    final_amount = "final_amount"
    loyalty_points = "loyalty_points"


class VisHistogram(Choice):
    def action(self):
        col_name = read_input(
            f"Enter column name [{'/'.join(HistogramCols)}]: ",
            HistogramCols,
        )
        df = read_data()
        df[col_name].plot.hist()
        plt.tight_layout()
        plt.show()


class AddData(Choice):
    columns: list[tuple[str, type]] = [
        ("customer_id", int),
        ("store_name", str),
        ("transaction_date", date),
        ("aisle", str),
        ("product_name", str),
        ("quantity", int),
        ("unit_price", float),
        ("total_amount", float),
        ("discount_amount", float),
        ("final_amount", float),
        ("loyalty_points", int),
    ]

    def action(self):
        row = {}
        for col, typ in self.columns:
            value = read_input(f"Enter value for [{col}]: ", typ)
            row[col] = value
        engine = sa.create_engine(db_url)
        transactions = sa.Table("transactions", sa.MetaData(), autoload_with=engine)
        with engine.connect() as conn:
            stmt = sa.insert(transactions).values(**row)
            conn.execute(stmt)
            conn.commit()


def main():
    menu = Choice(
        sub_choice=SubChoice(
            summary="Welcome to Grocery Store Program, what would you like to do?",
            choices=[
                ReadTable(description="Read table"),
                ShowStats(description="Show statistics"),
                Choice(
                    description="Show visualization",
                    sub_choice=SubChoice(
                        summary="Choose visualization types",
                        choices=[
                            VisCategory(description="Categorical visualization"),
                            VisHistogram(description="Histogram visualization"),
                        ],
                    ),
                ),
                AddData(description="Add new transaction"),
            ],
        ),
    )
    menu.dialog()


if __name__ == "__main__":
    main()
