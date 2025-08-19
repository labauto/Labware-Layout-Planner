import json
import pathlib
import unittest
from io import StringIO
import sys

# functions.pyからrun_check_chan関数をインポートする
from formationformatter.functions import run_check_chan

class TestA(unittest.TestCase):
    def test_run_check_chan(self):
        test_case_dir = "/home/cab314/Project/FormationFormatter-main/FF/results/c7f32c16-ff3b-4730-b7ac-64125bccc3f7_iteration_1"
        test_case_dir = pathlib.Path(test_case_dir)
        object_list_path = test_case_dir / "obj_chan/object_list.json"
        with open(object_list_path, "r") as f:
            object_list = json.load(f)
        
        haichi_path = test_case_dir / "haichi_chan/haichi.json"
        with open(haichi_path, "r") as f:
            haichi = json.load(f)


        print(f"{object_list=}")

        checker = False

        for hai in haichi:
            print(f"{haichi=}")
            if all(run_check_chan(object_list, hai, "id", base_path="")):
                print(f"OK: {hai}")
                checker = True
                break


        if checker:
            self.assertEqual("OK", "OK")

        

# functions.pyからrun_check_chan関数をインポートする
from formationformatter.functions import run_check_chan

class TestB(unittest.TestCase):
    def test_run_check_chan(self):
        # run_check_chan関数の戻り値を検証する
        self.assertEqual("OK", "OK")

if __name__ == '__main__':

    unittest.main()
