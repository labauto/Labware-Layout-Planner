from src.formationformatter.obj_chan import  Object as ObjchanObject
from typing import Generator, List, Tuple


# def sort_objects_by_constraints(restricted_stations: List[Tuple[ObjchanObject, List[int]]]):
#     # オブジェクトを制約の厳しい順にソートして返す。
#     # lambda関数は各オブジェクトの禁止ステーションの数を使用してソートを行う。
#     return sorted(restricted_stations, key=lambda obj: len(restricted_stations[obj]), reverse=True)

def sort_objects_by_constraints(restricted_stations: List[Tuple[ObjchanObject, List[int]]]) -> dict[ObjchanObject, List[int]]:
    # オブジェクトを制約の厳しい順にソートして返す。
    # lambda関数は各オブジェクトの禁止ステーションの数を使用してソートを行う。
    print(f"{restricted_stations=}")
    sorted_obj = sorted(restricted_stations, key=lambda obj: len(restricted_stations[1]), reverse=True)
    return sorted_obj

def permutations(stations:List[int], objects: List[Tuple[ObjchanObject, List[int]]], selected_objects, selected_indices, results, batch_size = 32) -> Generator:
    # 現在の選択状態が全オブジェクトの数と同じかどうかを確認
    if len(selected_objects) == len(objects):
        results.append(selected_objects.copy())
        # batch_size個の結果が集まったら、それをyieldし、結果をクリア
        if len(results) >= batch_size:
            yield results.copy()
            results.clear()
        return

    current_object = objects[len(selected_objects)]  # 現在配置するべきオブジェクト

    for i in range(len(stations)):
        # ステーションがすでに選択されているか、禁止ステーションである場合、スキップ
        if i in selected_indices or stations[i] in current_object[1]:
            continue

        # オブジェクトをステーションに配置
        selected_objects.append((current_object, stations[i]))
        selected_indices.add(i)

        # 再帰的に次のオブジェクトの配置を試行
        yield from permutations(stations, objects,selected_objects, selected_indices, results)

        # 配置を取り消し、次のステーションを試す
        selected_objects.pop()
        selected_indices.remove(i)
