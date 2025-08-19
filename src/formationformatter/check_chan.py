from typing import Union
from typing import List, Tuple, Dict
import inspect
import numpy as np
import pandas as pd
import json
from src.formationformatter.config import config

class Object:
    DEFAULT_NAME = "no name"

    def __init__(self, type_: str, holes: int, holes_r: int, top_left_coordinate: Tuple[float, float], bottom_right_coordinate: Tuple[float, float], name: str = "no name", other_info:dict = {}):
        self.type = type_
        self.name = name if name != Object.DEFAULT_NAME else type_  # Use type as name if name is not provided
        self.holes = holes
        self.holes_r = holes_r
        self.top_left_coordinate = top_left_coordinate
        self.bottom_right_coordinate = bottom_right_coordinate
        self.hole_coordinates = self.calculate_hole_coordinates()
        self.other_info = other_info

    def calculate_hole_coordinates(self) -> dict:
        coordinates = {}
        x1, y1 = self.top_left_coordinate
        x2, y2 = self.bottom_right_coordinate
        holes_c = self.holes // self.holes_r  # Number of holes in columns
        dx = (x2 - x1) / (holes_c - 1)
        dy = (y1 - y2) / (self.holes_r - 1)

        for row in range(self.holes_r):
            for col in range(holes_c):
                label = chr(ord('A') + row) + str(col + 1)
                x = x1 + col * dx
                y = y1 - row * dy
                coordinates[label] = (x, y)

        return coordinates

    def get_position(self, label: str) -> Tuple[float, float]:
        return self.hole_coordinates.get(label)

    def __repr__(self):
        return f"Object(name={self.name}, type={self.type}, holes={self.holes}, holes_r={self.holes_r}, top_left_coordinate={self.top_left_coordinate}, bottom_right_coordinate={self.bottom_right_coordinate})"

    @classmethod
    def create_df_from_class(cls):
        # クラスの __init__ メソッドからパラメータ情報を取得
        params = inspect.signature(cls.__init__).parameters

        data = {}

        for name, param in params.items():
            if name == 'self':
                continue
            if param.default != inspect.Parameter.empty:
                data[name] = param.default
            else:
                data[name] = np.nan  # ここでNaNを設定

        # DataFrameを作成
        df = pd.DataFrame([data], index=['DefaultValue'])
        return df


class Station:
    def __init__(self, height: float = 85.3, width: float = 127.6, row: int = 4, column: int = 3, gap: float = 2):
        self.height = height
        self.width = width
        self.row = row
        self.column = column
        self.gap = gap
        self.objects_grid = [["void" for _ in range(row)] for _ in range(column)]  # Grid to store objects in the station
        print(self.objects_grid)
        print(self.show_station_num())
        print(self.show_station_coordinate())

    def add_object(self, obj: Object, position: Union[int, Tuple[int, int]]):
        if isinstance(position, int):
            x, y = self.num_to_coordinate(position)
        elif isinstance(position, tuple):
            x, y = position
        else:
            raise ValueError(f"Invalid position type. It must be either an integer or a tuple: {position}.")

        if y >= self.row or x >= self.column:
            raise ValueError(f"Invalid row or column index for the station: {position}.")

        existing_obj = self.objects_grid[x][y]
        if existing_obj != "void":
            raise ValueError(f"An object ({existing_obj.name}) is already placed at the specified station position: {position}.")

        self.objects_grid[x][y] = obj

    def remove_object(self, position: Union[int, Tuple[int, int]]):
        """
        指定された位置にあるオブジェクトを取り除く関数。
        """
        if isinstance(position, int):
            x, y = self.num_to_coordinate(position)
        elif isinstance(position, tuple):
            x, y = position
        else:
            raise ValueError(f"Invalid position type. It must be either an integer or a tuple: {position}.")

        if y >= self.row or x >= self.column:
            raise ValueError(f"Invalid row or column index for the station: {position}.")

        self.objects_grid[x][y] = "void"



    def coordinate_to_num(self, station_position: Tuple[int, int]):
        x, y = station_position
        return x + y * self.column + 1

    def num_to_coordinate(self, station_position: int):
        station_position = station_position-1
        return (station_position % self.column, station_position // self.column)

    def show_station_num(self):
        table = "|"
        for _ in range(self.column):
            table += f"|"
        table += "\n|"
        for _ in range(self.column):
            table += "----|"
        table += "\n"
        for y in range(self.row):
            table += "|"
            for x in range(self.column):
                coordinate = (x, self.row - y - 1)
                num = self.coordinate_to_num(coordinate)
                table += f"{num:<4}|"
            table += "\n"
        return table

    def show_station_coordinate(self):
        table = "|"
        for _ in range(self.column):
            table += f"|"
        table += "\n|"
        for _ in range(self.column):
            table += "----|"
        table += "\n"
        for y in range(self.row):
            table += "|"
            for x in range(self.column):
                coordinate = (x, self.row - y - 1)
                table += f"{coordinate}|"
            table += "\n"
        return table


    def show_property(self):
        table = "|"
        for _ in range(self.column):
            table += "|"
        table += "\n"

        table += "|"
        for _ in range(self.column):
            table += "----|"
        table += "\n"

        for y in range(self.row):
            table += "|"
            for x in range(self.column):
                obj = self.objects_grid[x][self.row - y - 1]
                if obj == "void":
                    table += "void|"
                else:
                    table += f"{obj.name}:{obj.type}|"
            table += "\n"
        return table

    def __repr__(self):
        return f"Station(height={self.height}, width={self.width}, row={self.row}, column={self.column}, gap={self.gap})"

    # Moving the get_station_coordinate function as a method of Station class
    def get_station_coordinate(self, station_position: Union[int, Tuple[int, int]], hole_label: str = None) -> Union[Tuple[float, float], List[Tuple[float, float]]]:
        if isinstance(station_position, int):
            x, y = self.num_to_coordinate(station_position)
        elif isinstance(station_position, tuple):
            x, y = station_position
        else:
            raise ValueError(f"Invalid station position type: {station_position}. It must be either an integer or a tuple.")

        if y >= self.row or x >= self.column:
            raise ValueError(f"Invalid station position: {station_position}. It is out of range for the station.")

        obj = self.objects_grid[x][y]

        if hole_label is None:
            # If hole_label is None, return the coordinates of the four vertices of the station
            vertices = [
                (x * (self.width + self.gap), y * (self.height + self.gap)),
                (x * (self.width + self.gap), y * (self.height + self.gap) + self.height),
                (x * (self.width + self.gap) + self.width, y * (self.height + self.gap) + self.height),
                (x * (self.width + self.gap) + self.width, y * (self.height + self.gap))
            ]
            return vertices
        if obj == "void":
            raise ValueError(f"No object found at the specified station position: {station_position}.")
        hole_coordinate = obj.get_position(hole_label)
        if hole_coordinate is None:
            raise ValueError(f"Invalid hole label: {hole_label}. It does not exist in the object at the specified station position: {station_position}.")

        x_offset = x * (self.width + self.gap)
        y_offset = y * (self.height + self.gap)
        x, y = hole_coordinate
        absolute_x = x + x_offset
        absolute_y = y + y_offset

        return absolute_x, absolute_y




class Chack_chan(Station):

    def __init__(self, target_device = config.target_device, height: float = 85.3, width: float = 127.6, row: int = 4, column: int = 3, gap: float = 2):
        print(f"target_device: {target_device}")
        match target_device:
            case "OT-2":
                print("OT-2 is selected.")
                height: float = 85.3
                width: float = 127.6
                row: int = 4
                column: int = 3
                gap: float = 2
                super().__init__(height, width, row, column, gap)
            case "MAHOLO":
                print("MAHOLO is selected.")
                height: float = 85.3
                width: float = 127.6
                row: int = 1
                column: int = 170
                gap: float = 2
                super().__init__(height, width, row, column, gap)
            case _:
                print("Invalid target device. We use the input value as the target device.")
                super().__init__(height, width, row, column, gap)

    def get_station_num(self):
        return self.row * self.column

    def check_conditions(self, filename: str) -> List[bool]:
        """指定されたJSONファイルを読み込み、各エントリの条件をチェックする。

        Parameters:
        - filename (str): JSONファイルのパス

        Returns:
        - List[bool]: 各エントリが条件を満たしているかどうかの結果
        """
        with open(filename, 'r') as f:
            data: List[Dict[str, Union[int, str, List[int]]]] = json.load(f)

        results: List[bool] = [self.check_single_condition(entry=entry) for entry in data]

        return results

    def check_single_condition_labware_id(self, entry: Dict[str, Union[int, str, List[int]]]) -> bool:
        """単一のエントリの条件をチェックする。

        Parameters:
        - entry (Dict): JSONから読み込んだエントリ

        Returns:
        - bool: エントリが条件を満たしているかどうか
        """

        subject_labware_id = entry["labware_id"]
        labware_positions: dict = self.positions_from_labware_id()
        subject_positions_list = []

        try:
            subject_positions_list = labware_positions[subject_labware_id]
        except KeyError:
          return True

        neighbour_positions_list = []
        for neighbour_labware_id in entry["neighbour_types"]:
            positions_list = labware_positions.get(neighbour_labware_id)
            if positions_list is not None:
              neighbour_positions_list.extend(positions_list)
            else:
              continue



        if entry["restriction_type"] == "adjacent":
            if entry["adjacent_type"] == "grid":
                for position in subject_positions_list:
                    neighbour_positions: List[int] = self.besides_grid(position)
                    if any(neighbour in neighbour_positions_list for neighbour in neighbour_positions):
                        return False
            elif entry["adjacent_type"] == "around":
                for position in subject_positions_list:
                    neighbour_positions: List[int] = self.besides_around(position)
                    if any(neighbour in neighbour_positions_list for neighbour in neighbour_positions):
                        return False
        elif entry["restriction_type"] == "air_superiority":
            print("air_superiority checker unimplemented")
            return True
            for position in subject_positions_list:
                if position + self.row in neighbours:
                    return False
        return True
    
    def check_single_condition(self, entry: Dict[str, Union[int, str, List[int]]]) -> bool:
        """単一のエントリの条件をチェックする。

        Parameters:
        - entry (Dict): JSONから読み込んだエントリ

        Returns:
        - bool: エントリが条件を満たしているかどうか
        """
        print(f"entry: {entry}")
        restriction_category = entry["restriction_category"]
        subject_labware_id = entry["labware_id"]
        print(f"subject_labware_id: {subject_labware_id}")
        labware_positions: dict = self.positions_from_category(restriction_category)
        subject_positions_list = []

        try:
            subject_positions_list = labware_positions[subject_labware_id]
        except Exception as e:
            print(f"Error: {e}")
            return True

        neighbour_positions_list = []
        for neighbour_labware_id in entry["neighbour_types"]:
            positions_list = labware_positions.get(neighbour_labware_id)
            if positions_list is not None:
              neighbour_positions_list.extend(positions_list)
            else:
              continue



        if entry["restriction_type"] == "adjacent":
            if entry["adjacent_type"] == "grid":
                for position in subject_positions_list:
                    neighbour_positions: List[int] = self.besides_grid(position)
                    if any(neighbour in neighbour_positions_list for neighbour in neighbour_positions):
                        return False
            elif entry["adjacent_type"] == "around":
                for position in subject_positions_list:
                    neighbour_positions: List[int] = self.besides_around(position)
                    if any(neighbour in neighbour_positions_list for neighbour in neighbour_positions):
                        return False
        elif entry["restriction_type"] == "air_superiority":
            print("air_superiority checker unimplemented")
            return True
            for position in subject_positions_list:
                if position + self.row in neighbours:
                    return False
        return True

    # Common
    # ラボウェアIDごとの位置のリストを含む辞書を返します。
    def positions_from_labware_id(self):
        # 空の辞書を初期化します。これは、ラボウェアIDをキーとして、その位置のリストを値とする辞書です。
        positions_labware_id = {}

        # インスタンス変数self.rowとself.columnを使用して、グリッドの各行と列をループします。
        for y in range(self.row):
            for x in range(self.column):
                # self.objects_gridは二次元配列で、各要素にオブジェクトが格納されています。
                obj = self.objects_grid[x][y]

                # オブジェクトが"void"（何もないスペースを表す）の場合は何もしません。
                if obj == "void":
                    pass
                else:
                    # オブジェクトが"void"でない場合、その他の情報からラボウェアIDを取得します。
                    labware_id = obj.other_info["labware_id"]

                    # (x, y)座標を数値に変換するために、self.coordinate_to_numメソッドを使用します。
                    position = self.coordinate_to_num((x, y))

                    # positions_labware_id辞書にそのラボウェアIDがまだない場合は、キーとして追加し、空のリストを値として割り当てます。
                    if labware_id not in positions_labware_id:
                        positions_labware_id[labware_id] = []

                    # そのラボウェアIDのキーに対応する位置のリストに、新しい位置を追加します。
                    positions_labware_id[labware_id].append(position)

        # 最終的に、ラボウェアIDごとの位置のリストを含む辞書を返します。
        return positions_labware_id

    def positions_from_category(self, category: str):
        # 空の辞書を初期化します。これは、category_valueをキーとして、その位置のリストを値とする辞書です。
        positions_category_value = {}

        # インスタンス変数self.rowとself.columnを使用して、グリッドの各行と列をループします。
        for y in range(self.row):
            for x in range(self.column):
                # self.objects_gridは二次元配列で、各要素にオブジェクトが格納されています。
                obj = self.objects_grid[x][y]

                # オブジェクトが"void"（何もないスペースを表す）の場合は何もしません。
                if obj == "void":
                    pass
                else:
                    # オブジェクトが"void"でない場合、その他の情報からcategory_valueを取得します。
                    # TODO:other_infoがなにかわからない
                    try:
                        # category_value = obj.other_info.get(category)
                        category_value = getattr(obj.other_info, category)

                        # (x, y)座標を数値に変換するために、self.coordinate_to_numメソッドを使用します。
                        position = self.coordinate_to_num((x, y))

                        # positions_labware_id辞書にそのcategory_valueがまだない場合は、キーとして追加し、空のリストを値として割り当てます。
                        if category_value not in positions_category_value:
                            positions_category_value[category_value] = []

                        # そのcategory_valueのキーに対応する位置のリストに、新しい位置を追加します。
                        positions_category_value[category_value].append(position)
                    except Exception as e:
                        print(f"Error: {e}")
                        pass

        # 最終的に、category_valueごとの位置のリストを含む辞書を返します。
        return positions_category_value



    # For besides

    def position_from_number(self, A, N, M):
        """番号から行と列の位置を取得するヘルパー関数"""
        row = (A - 1) // M
        col = (A - 1) % M
        return row, col

    def besides_grid(self, A):
        """A番のマスの上下左右のマスの番号を列挙する関数"""
        N = self.row
        M = self.column
        row, col = self.position_from_number(A, N, M)
        neighbors = []

        # 上
        if row < N - 1:
            neighbors.append(A + M)
        # 下
        if row > 0:
            neighbors.append(A - M)
        # 左
        if col > 0:
            neighbors.append(A - 1)
        # 右
        if col < M - 1:
            neighbors.append(A + 1)

    def besides_around(self, A):
        """A番のマスの周囲八マスのマスの番号を列挙する関数"""
        N = self.row
        M = self.column
        row, col = self.position_from_number(A, N, M)
        around = []

        # 上
        if row < N - 1:
            around.append(A + M)
            # 左上
            if col > 0:
                around.append(A + M - 1)
            # 右上
            if col < M - 1:
                around.append(A + M + 1)
        # 下
        if row > 0:
            around.append(A - M)
            # 左下
            if col > 0:
                around.append(A - M - 1)
            # 右下
            if col < M - 1:
                around.append(A - M + 1)
        # 左
        if col > 0:
            around.append(A - 1)
        # 右
        if col < M - 1:
            around.append(A + 1)

        return around

    # For air_superiority
    def calculate_pathway(self, station_num1, hole_label1, station_num2, hole_label2, calculate_method="straight"):
        """
        Calculate the pathway between two holes based on the specified method.

        Parameters:
        - station_num1: Station number of the first hole
        - hole_label1: Label of the first hole
        - station_num2: Station number of the second hole
        - hole_label2: Label of the second hole
        - calculate_method: Name (String) of a method, default is "straight"

        Returns:
        A list of tuples representing the vertices of the path.
        """
        # Define a dictionary to map method names to corresponding functions
        method_mapping = {
            "straight": self._calculate_straight_path,
            "x_first": self._calculate_x_first_path,
            "y_first": self._calculate_y_first_path,
            "xy_equal_speed": self._calculate_xy_equal_speed_path,
            "remaining_axis_first": self._calculate_remaining_axis_first_path
        }

        # Get the corresponding function for the given method
        method_function = method_mapping.get(calculate_method)
        if method_function is None:
            raise ValueError(f"Invalid calculate_method: {calculate_method}. Available methods are: {list(method_mapping.keys())}.")

        # Call the method function and return the result
        return method_function(station_num1, hole_label1, station_num2, hole_label2)

    def _calculate_straight_path(self, station_num1, hole_label1, station_num2, hole_label2):
        """
        Calculate the straight path between two holes.

        Returns:
        A list of tuples representing the vertices of the straight path.
        """
        point1 = self.get_station_coordinate(station_num1, hole_label1)
        point2 = self.get_station_coordinate(station_num2, hole_label2)
        return [point1, point2]

    def _calculate_x_first_path(self, station_num1, hole_label1, station_num2, hole_label2):
        """
        Calculate the path that moves first along the x-axis and then along the y-axis.

        Returns:
        A list of tuples representing the vertices of the path.
        """
        point1 = self.get_station_coordinate(station_num1, hole_label1)
        point2 = self.get_station_coordinate(station_num2, hole_label2)
        intermediate_point = (point2[0], point1[1])
        return [point1, intermediate_point, point2]

    def _calculate_y_first_path(self, station_num1, hole_label1, station_num2, hole_label2):
        """
        Calculate the path that moves first along the y-axis and then along the x-axis.

        Returns:
        A list of tuples representing the vertices of the path.
        """
        point1 = self.get_station_coordinate(station_num1, hole_label1)
        point2 = self.get_station_coordinate(station_num2, hole_label2)
        intermediate_point = (point1[0], point2[1])
        return [point1, intermediate_point, point2]

    def _calculate_xy_equal_speed_path(self, station_num1, hole_label1, station_num2, hole_label2):
        """
        Calculate the path that moves along the x and y axes at equal speed, then moves along the remaining axis.

        Returns:
        A list of tuples representing the vertices of the path.
        """
        point1 = self.get_station_coordinate(station_num1, hole_label1)
        point2 = self.get_station_coordinate(station_num2, hole_label2)

        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]

        if abs(dx) > abs(dy):
            intermediate_x = point1[0] + dy
            intermediate_point = (intermediate_x, point2[1])
        else:
            intermediate_y = point1[1] + dx
            intermediate_point = (point2[0], intermediate_y)

        return [point1, intermediate_point, point2]

    def _calculate_remaining_axis_first_path(self, station_num1, hole_label1, station_num2, hole_label2):
        """
        Calculate the path that moves first along the remaining axis, then moves along the x and y axes at equal speed.

        Returns:
        A list of tuples representing the vertices of the path.
        """
        point1 = self.get_station_coordinate(station_num1, hole_label1)
        point2 = self.get_station_coordinate(station_num2, hole_label2)

        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]

        if abs(dx) < abs(dy):
            intermediate_x = point1[0] + dx
            intermediate_point = (intermediate_x, point1[1])
        else:
            intermediate_y = point1[1] + dy
            intermediate_point = (point1[0], intermediate_y)

        return [point1, intermediate_point, point2]


    def get_line_coordinates(self, station_num1, hole_label1, station_num2, hole_label2) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get the coordinates of the line segment connecting two holes.

        Parameters:
        - station_num1: Station number of the first hole
        - hole_label1: Label of the first hole
        - station_num2: Station number of the second hole
        - hole_label2: Label of the second hole

        Returns:
        A tuple containing the coordinates of the two endpoints of the line segment.
        """
        point1 = self.get_station_coordinate(station_num1, hole_label1)
        point2 = self.get_station_coordinate(station_num2, hole_label2)

        return point1, point2

    def intersection_ex(self, p1, p2, p3, p4):

        """
        Check if the line segment connecting two holes intersects with the stations.

        Parameters:
        - p1, p2: Tuple[float, float] - Coordinates of the endpoints of the first line segment
        - p3, p4: Tuple[float, float] - Coordinates of the endpoints of the second line segment

        Returns:
        True if the line segments intersect, False otherwise.
        """
        # x座標によるチェック
        x1 = p1[0]
        x2 = p2[0]
        x3 = p3[0]
        x4 = p4[0]

        y1 = p1[1]
        y2 = p2[1]
        y3 = p3[1]
        y4 = p4[1]
        if (x1 >= x2):
            if ((x1 < x3 and x1 < x4) or (x2 > x3 and x2 > x4)):
                return False
        else:
            if ((x2 < x3 and x2 < x4) or (x1 > x3 and x1 > x4)):
                return False

        # y座標によるチェック
        if (y1 >= y2):
            if ((y1 < y3 and y1 < y4) or (y2 > y3 and y2 > y4)):
                return False
        else:
            if ((y2 < y3 and y2 < y4) or (y1 > y3 and y1 > y4)):
                return False

        if (((x1 - x2) * (y3 - y1) + (y1 - y2) * (x1 - x3)) *
            ((x1 - x2) * (y4 - y1) + (y1 - y2) * (x1 - x4)) > 0):
            return False

        if (((x3 - x4) * (y1 - y3) + (y3 - y4) * (x3 - x1)) *
            ((x3 - x4) * (y2 - y3) + (y3 - y4) * (x3 - x2)) > 0):
            return False

        return True
    def does_line_intersect_station(self, point1, point2, station_position):
        # Get the vertices of the station
        vertices = self.get_station_coordinate(station_position)

        # Check if the line segment intersects with any of the edges of the station
        for i in range(4):
            if self.intersection_ex(point1, point2, vertices[i], vertices[(i + 1) % 4]):
                return True

        return False


    def is_line_intersecting_stations(self, station_num1, hole_label1, station_num2, hole_label2, station_positions):
        """
        Check if the line segment connecting two holes intersects with the stations.

        Parameters:
        - station_num1: Station number of the first hole
        - hole_label1: Label of the first hole (Like A1, B5, C7)
        - station_num2: Station number of the second hole
        - hole_label2: Label of the second hole
        - station_positions: List of station positions to check for intersection

        Returns:
        True if the line segment intersects with any of the specified stations, False otherwise.
        """
        point1, point2 = self.get_line_coordinates(station_num1, hole_label1, station_num2, hole_label2)

        for station_position in station_positions:
            if self.does_line_intersect_station(point1, point2, station_position):
                return True

        return False



if __name__ == "__main__":
    # Example usage
    station = Station()

    obj_with_name = Object(type_="96-well plate",
                        holes=96,
                        holes_r=8,
                        top_left_coordinate=(1, 9),
                        bottom_right_coordinate=(9, 1),
                        name="Plate 1")

    station.add_object(obj_with_name, 1)
    print(station.show_property())
    station.add_object(obj_with_name, 2)
    print(station.show_property())
    station.add_object(obj_with_name, 3)
    print(station.show_property())
    station.add_object(obj_with_name, 4)
    print(station.show_property())
    station.add_object(obj_with_name, 5)
    print(station.show_property())
    station.add_object(obj_with_name, 6)
    print(station.show_property())
    station.add_object(obj_with_name, 7)
    print(station.show_property())
    station.add_object(obj_with_name, 8)
    print(station.show_property())
    station.add_object(obj_with_name, 9)
    print(station.show_property())
    station.add_object(obj_with_name, 10)
    print(station.show_property())
    station.add_object(obj_with_name, 11)
    print(station.show_property())
    station.add_object(obj_with_name, 12)
    print(station.show_property())
    # station.add_object(obj_with_name, 13)
    # print(station.show_property())

    print(station.show_property())

    station_coordinate = station.get_station_coordinate((1,0), "A1")

    print(station_coordinate)

    station_coordinate = station.get_station_coordinate((1,0))

    print(station_coordinate)

    print(station.__repr__())


    # Creating a Station instance
    # ここでStationをセットします （ただし、今は手動になってます　スミマセン…）
    station = Chack_chan()

    station.add_object(Object(type_="96-well plate",
                        holes=96,
                        holes_r=8,
                        top_left_coordinate=(1, 9),
                        bottom_right_coordinate=(9, 1),
                        name="Plate 1",
                        other_info = {"labware_id":1}), 1)
    station.add_object(Object(type_="96-well plate",
                        holes=96,
                        holes_r=8,
                        top_left_coordinate=(1, 9),
                        bottom_right_coordinate=(9, 1),
                        name="Plate 1",
                        other_info = {"labware_id":2}), 2)
    print(station.show_property())
    station.add_object(Object(type_="96-well plate",
                        holes=96,
                        holes_r=8,
                        top_left_coordinate=(1, 9),
                        bottom_right_coordinate=(9, 1),
                        name="Plate 1",
                        other_info = {"labware_id":3}), 3)
    print(station.show_property())


    station.add_object(Object(type_="96-well plate",
                        holes=96,
                        holes_r=8,
                        top_left_coordinate=(1, 9),
                        bottom_right_coordinate=(9, 1),
                        name="Plate 1",
                        other_info = {"labware_id":4}), 4)
    print(station.show_property())
