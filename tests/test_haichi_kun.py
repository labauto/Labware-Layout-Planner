from pathlib import Path
from typing import List, Tuple
import unittest
from src.formationformatter.check_chan import Chack_chan
from src.formationformatter.functions import get_haichi, load_restricted_stations, run_check_chan
import tempfile
from src.formationformatter.obj_chan import Object as ObjchanObject
from src.formationformatter.obj_chan import load_objects

class TestHaichiKun(unittest.TestCase):

    def setUp(self):
        test_folder = Path(__file__).parent
        self.log_file_path = tempfile.mkstemp()[1]
        self.object_list = load_objects(test_folder / "test_data/artifacts/iteration_0/obj_chan/object_list.json")
        self.restricted_stations_path = test_folder / "test_data/Inputs/restricted_stations.json"
        self.relative_restriction_path = test_folder / "test_data/Inputs/relative_restriction_init_content/ng_position1.json"
        for var in vars(self):
            print(f"{var=}")
            print(f"{getattr(self, var)=}")


    def test_(self):
        restricted_stations: List[Tuple[ObjchanObject, List[int]]] = load_restricted_stations(object_list=self.object_list, resticted_stations_path=Path(self.restricted_stations_path))
        stations = Chack_chan()
        # List[List[Tuple[ObjchanObject, List[int]]]] を返すようにする
        haichi = get_haichi(stations, restricted_stations, id="0", log_file_path=self.log_file_path)
        for haichi in haichi:
            print(f"{haichi=}")
            check_chan_result, visualization = run_check_chan(
                haichi=haichi,
                id="0",
                base_path="",
                log_file_path=self.log_file_path,
                relative_restriction_path=self.relative_restriction_path
            )
            print(f"{check_chan_result=}")
            assert all(check_chan_result)
            assert len(check_chan_result) == 2


    def test_search_and_add(self):
        for input_object in self.object_list:
            print(f"{input_object=}")

        restricted_stations: List[Tuple[ObjchanObject, List[int]]] = load_restricted_stations(object_list=self.object_list, resticted_stations_path=Path(self.restricted_stations_path))
        for restricted_station in restricted_stations:
            print(f"{restricted_station=}")

        assert len(restricted_stations) == len(self.object_list)