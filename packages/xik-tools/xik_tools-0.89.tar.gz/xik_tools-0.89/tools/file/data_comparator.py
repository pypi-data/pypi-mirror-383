import pandas as pd
import logging

class DataComparator:
    @staticmethod
    def is_equal_each_columns(ds1: pd.Series, ds2: pd.Series):
        """
        # 예시 데이터
        data1 = {'A': 1, 'B': 2, 'C': 3}
        data2 = {'A': 1, 'B': 5, 'C': 3}

        # Pandas Series 생성
        series1 = pd.Series(data1)
        series2 = pd.Series(data2)

        # DataComparator 인스턴스 생성
        comparator = DataComparator()

        # 메서드 호출
        comparator.is_equal_each_columns(series1, series2)
        """
        # 값이 같은지 여부 확인
        are_equal = ds1.equals(ds2)
        # 값이 다른 항목 확인
        diff_positions = (ds1 != ds2)
        # 차이가 있는 항목 출력
        diff_items = ds1.index[diff_positions].tolist()
        
        logging.info(f"두 행 간의 값이 같은지 여부: {are_equal}")
        logging.info(f"차이가 있는 항목: {diff_items}")
        print(f"두 행 간의 값이 같은지 여부: {are_equal}")
        print(f"차이가 있는 항목: {diff_items}")
