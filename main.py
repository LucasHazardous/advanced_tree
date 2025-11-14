# To debug: print("Debug messages...", file=sys.stderr, flush=True)
from typing import List, Dict, Tuple

tree_map = {}


def split_directory_into_parts(dir: str) -> List[str]:
    split_paths = dir.split("/")
    if split_paths[0] == ".":
        split_paths = split_paths[1:]
    return split_paths


def add_dir_to_tree_map(tree_map, dir_parts):
    current_map_to_insert_to = tree_map
    for dir_part in dir_parts[:-1]:
        if dir_part not in current_map_to_insert_to:
            current_map_to_insert_to[dir_part] = {}
        current_map_to_insert_to = current_map_to_insert_to[dir_part]

    current_map_to_insert_to[dir_parts[-1]] = ""


def print_sorted_dir_contents(
    tree_map: Dict,
    depth_items_ending_list,
    depth: int = 1
):
    if len(depth_items_ending_list) < depth:
        depth_items_ending_list = depth_items_ending_list[:] + [False]

    objects_names = sorted(tree_map.keys())
    for i, object_name in enumerate(objects_names):
        current_depth_touching_sign = "|"

        ending = False
        if i == len(objects_names) - 1:
            current_depth_touching_sign = "`"
            ending = True

        depth_items_ending_list[depth - 1] = ending

        depth_info = ""
        for depth_item_ending in depth_items_ending_list[:-1]:
            if depth_item_ending:
                depth_info += "    "
            else:
                depth_info += "|   "

        print(f"{depth_info}{current_depth_touching_sign}-- {object_name}")

        if tree_map[object_name] != "":
            print_sorted_dir_contents(
                tree_map[object_name], depth_items_ending_list, depth + 1
            )


def count_dirs_and_files(tree_map: Dict) -> Tuple[int, int]:
    directories, files = 0, 0
    for value in tree_map.values():
        if value == "":
            files += 1
        else:
            directories += 1
            sub_dirs, sub_files = count_dirs_and_files(value)
            directories += sub_dirs
            files += sub_files
    return directories, files


def go_inside_tree_map(tree_map: Dict, dir_parts: List[str]) -> Dict:
    for dir_part in dir_parts:
        tree_map = tree_map[dir_part]
    return tree_map


starting_dir = input()
flags = input()
number_of_files = int(input())
for i in range(number_of_files):
    line = input()
    dir_parts = split_directory_into_parts(line)
    add_dir_to_tree_map(tree_map, dir_parts)


print(starting_dir)
if starting_dir != ".":
    tree_map = go_inside_tree_map(
        tree_map,
        split_directory_into_parts(starting_dir)
    )

print_sorted_dir_contents(tree_map, [])
dirs, files = count_dirs_and_files(tree_map)
print()
print(
    f"{dirs} {'directory' if dirs == 1 else 'directories'},"
    f" {files} {'file' if files == 1 else 'files'}"
)
