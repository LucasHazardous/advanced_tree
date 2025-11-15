# To debug: print("Debug messages...", file=sys.stderr, flush=True)
from typing import List, Dict, Tuple

tree_map = {}


def split_directory_into_parts(dir: str) -> List[str]:
    split_paths = dir.split("/")
    if split_paths[0] == ".":
        split_paths = split_paths[1:]
    return split_paths


def add_dir_to_tree_map(tree_map: Dict, dir_parts: List[str]):
    current_map_to_insert_to = tree_map
    for dir_part in dir_parts[:-1]:
        if dir_part not in current_map_to_insert_to:
            current_map_to_insert_to[dir_part] = {}
        current_map_to_insert_to = current_map_to_insert_to[dir_part]

    current_map_to_insert_to[dir_parts[-1]] = ""


def produce_tree_sorted_dir_contents(
    tree_map: Dict,
    depth_items_ending_list,
    depth_limit: int,
    show_hidden: bool = False,
    only_dirs: bool = False,
    depth: int = 1,
) -> str:
    result_tree = ""

    if depth_limit != -1 and depth > depth_limit:
        return result_tree

    if len(depth_items_ending_list) < depth:
        depth_items_ending_list = depth_items_ending_list[:] + [False]

    objects_names = tree_map.keys()

    if not show_hidden:
        objects_names = list(
            filter(lambda name: name[0] != ".", objects_names)
        )

    if only_dirs:
        objects_names = list(
            filter(lambda name: tree_map[name] != '', objects_names)
        )

    objects_names = sorted(
        objects_names,
        key=lambda name: name[1:].lower() if name[0] == '.' else name.lower()
    )

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

        result_tree += (
            f"{depth_info}{current_depth_touching_sign}"
            f"-- {object_name}\n"
        )

        if tree_map[object_name] != "":
            result_tree += produce_tree_sorted_dir_contents(
                tree_map[object_name],
                depth_items_ending_list,
                depth_limit,
                show_hidden,
                only_dirs,
                depth + 1
            )
    return result_tree


def count_dirs_and_files(
    tree_map: Dict,
    count_hidden: bool,
    depth_limit: int = -1,
    depth: int = 1
) -> Tuple[int, int]:
    if depth_limit != -1 and depth > depth_limit:
        return 0, 0

    directories, files = 0, 0
    for key, value in tree_map.items():
        if key[0] == "." and not count_hidden:
            continue

        if value == "":
            files += 1
        else:
            directories += 1
            sub_dirs, sub_files = count_dirs_and_files(
                value,
                count_hidden,
                depth_limit,
                depth+1
            )
            directories += sub_dirs
            files += sub_files
    return directories, files


def go_inside_tree_map(tree_map: Dict, dir_parts: List[str]) -> Dict:
    for dir_part in dir_parts:
        tree_map = tree_map[dir_part]
    return tree_map


def generate_summary(
    dir_count: int,
    file_count: int,
    only_dirs: bool = False
) -> str:
    summary = f"{dir_count} {'directory' if dir_count == 1 else 'directories'}"
    if not only_dirs:
        summary += f", {file_count} {'file' if file_count == 1 else 'files'}"
    return summary


starting_dir = input()
flags = input()
number_of_files = int(input())
for i in range(number_of_files):
    line = input()
    dir_parts = split_directory_into_parts(line)
    add_dir_to_tree_map(tree_map, dir_parts)

show_hidden = "-a" in flags
only_dirs = "-d" in flags

search_limit = "-L" in flags
depth_limit = -1
if search_limit:
    flags = flags.split(",")
    for flag in flags:
        flag = flag.strip()
        if flag[0:2] == "-L":
            depth_limit = int(flag[3:])

try:
    if starting_dir != ".":
        tree_map = go_inside_tree_map(
            tree_map,
            split_directory_into_parts(starting_dir)
        )
except KeyError:
    print(f"{starting_dir} [error opening dir]")
    print()
    print(generate_summary(0, 0, only_dirs))
    quit()

try:
    main_tree_content = produce_tree_sorted_dir_contents(
        tree_map,
        [],
        depth_limit,
        show_hidden,
        only_dirs
    )
except AttributeError:
    print(f"{starting_dir} [error opening dir]")
    print()
    print(generate_summary(0, 0, only_dirs))
    quit()

print(starting_dir)
print(main_tree_content)
dirs, files = count_dirs_and_files(tree_map, show_hidden, depth_limit)

summary = generate_summary(dirs, files, only_dirs)
print(summary)
