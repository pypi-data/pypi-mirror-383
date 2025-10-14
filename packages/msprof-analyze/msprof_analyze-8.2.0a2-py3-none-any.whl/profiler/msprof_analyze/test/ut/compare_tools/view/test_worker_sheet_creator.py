import os
import unittest

import pandas as pd
from xlsxwriter import Workbook

from msprof_analyze.compare_tools.compare_backend.utils.excel_config import ExcelConfig
from msprof_analyze.compare_tools.compare_backend.view.work_sheet_creator import WorkSheetCreator


class TestWorkerSheetCreator(unittest.TestCase):
    file_path = "./test.xlsx"
    table_name = "OperatorCompareStatistic"

    def tearDown(self) -> None:
        if not os.path.exists(self.file_path):
            raise RuntimeError("ut failed.")
        os.remove(self.file_path)

    def test_create_sheet_when_valid_data(self):
        class Args:
            def __init__(self, base, comparison):
                self.base_profiling_path = base
                self.comparison_profiling_path = comparison

        data = {"headers": ExcelConfig.HEADERS.get(self.table_name),
                "overhead": ExcelConfig.OVERHEAD.get(self.table_name),
                "rows": [[1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, float("inf")], [1, 2, 3, 4, 5, 6, 7, 0.45],
                         [1, 2, 3, 4, 5, 6, 7, 0]]}
        creator = WorkSheetCreator(Workbook(self.file_path), self.table_name, data, Args("base", "comparison"))
        creator.create_sheet()
        creator._work_book.close()
        data = pd.read_excel(self.file_path)
        self.assertEqual(data.shape[0], 6)
        self.assertEqual(data.shape[1], 8)

    def test_create_sheet_when_invalid_data(self):
        data = {"headers": ExcelConfig.HEADERS.get(self.table_name),
                "overhead": ExcelConfig.OVERHEAD.get(self.table_name),
                "rows": []}
        creator = WorkSheetCreator(Workbook(self.file_path), self.table_name, data, {})
        creator.create_sheet()
        creator._work_book.close()
        data = pd.read_excel(self.file_path)
        self.assertEqual(data.shape[0], 0)
