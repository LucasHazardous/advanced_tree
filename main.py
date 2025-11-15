from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class FlagData:
    show_hidden_objects: bool
    show_only_dirs: bool
    search_depth_limit: int = -1


@dataclass
class InputData:
    tree_map: Dict
    starting_dir: str
    flag_data: FlagData


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


def filter_out_objects_with_dot(objects_names: List[str]) -> List[str]:
    return list(
        filter(lambda name: name[0] != ".", objects_names)
    )


def filter_out_files(objects_names: List[str], tree_map: Dict) -> List[str]:
    return list(
        filter(lambda name: tree_map[name] != '', objects_names)
    )


def sort_objects_names(objects_names: List[str]) -> List[str]:
    return sorted(
        objects_names,
        key=lambda name: name[1:].lower() if name[0] == '.' else name.lower()
    )


def construct_depth_into(item_last_on_depths: List[bool]) -> str:
    depth_info = ""
    for item_last_on_depth in item_last_on_depths[:-1]:
        if item_last_on_depth:
            depth_info += "    "
        else:
            depth_info += "|   "
    return depth_info


def produce_tree_sorted_dir_contents(
    tree_map: Dict,
    item_last_on_depths: List[bool],
    flag_data: FlagData,
    depth: int = 1,
) -> str:
    result_tree = ""

    if (
        flag_data.search_depth_limit != -1 and
        depth > flag_data.search_depth_limit
    ):
        return result_tree

    if len(item_last_on_depths) < depth:
        item_last_on_depths = item_last_on_depths[:] + [False]

    objects_names = tree_map.keys()

    if not flag_data.show_hidden_objects:
        objects_names = filter_out_objects_with_dot(objects_names)

    if flag_data.show_only_dirs:
        objects_names = filter_out_files(objects_names, tree_map)

    objects_names = sort_objects_names(objects_names)

    for i, object_name in enumerate(objects_names):
        last_object_on_depth = (i == len(objects_names) - 1)

        item_last_on_depths[depth - 1] = last_object_on_depth

        depth_info = construct_depth_into(item_last_on_depths)

        result_tree += (
            f"{depth_info}{'`' if last_object_on_depth else '|'}"
            f"-- {object_name}\n"
        )

        if tree_map[object_name] != "":
            result_tree += produce_tree_sorted_dir_contents(
                tree_map[object_name],
                item_last_on_depths,
                flag_data,
                depth + 1
            )
    return result_tree


def count_dirs_and_files(
    tree_map: Dict,
    flag_data: FlagData,
    depth: int = 1
) -> Tuple[int, int]:
    if (
        flag_data.search_depth_limit != -1 and
        depth > flag_data.search_depth_limit
    ):
        return 0, 0

    directories, files = 0, 0
    for key, value in tree_map.items():
        if key[0] == "." and not flag_data.show_hidden_objects:
            continue

        if value == "":
            files += 1
        else:
            directories += 1
            sub_dirs, sub_files = count_dirs_and_files(
                value,
                flag_data,
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


def parse_flag_data(flags: str) -> FlagData:
    show_hidden = False
    show_only_dirs = False
    depth_limit = -1

    flags = flags.split(",")
    for flag in flags:
        flag = flag.strip()

        if flag[0:2] == "-L":
            try:
                depth_limit = int(flag[3:])
            except ValueError:
                pass
        elif flag == "-a":
            show_hidden = True
        elif flag == "-d":
            show_only_dirs = True

    return FlagData(show_hidden, show_only_dirs, depth_limit)


def load_inputs() -> InputData:
    tree_map = {}
    starting_dir = input()
    flags = input()

    flag_data = parse_flag_data(flags)

    number_of_files = int(input())
    for _ in range(number_of_files):
        line = input()
        dir_parts = split_directory_into_parts(line)
        add_dir_to_tree_map(tree_map, dir_parts)

    return InputData(tree_map, starting_dir, flag_data)


def error_opening_dir_summary(starting_dir: str, show_only_dirs: bool) -> str:
    return (
        f"{starting_dir} [error opening dir]\n\n"
        f"{generate_summary(0, 0, show_only_dirs)}"
    )


inputs = load_inputs()
tree_map = inputs.tree_map
try:
    if inputs.starting_dir != ".":
        tree_map = go_inside_tree_map(
            tree_map,
            split_directory_into_parts(inputs.starting_dir)
        )

    main_tree_content = produce_tree_sorted_dir_contents(
        tree_map,
        [],
        inputs.flag_data
    )
except (KeyError, AttributeError):
    print(error_opening_dir_summary(
        inputs.starting_dir,
        inputs.flag_data.show_only_dirs
    ))
    quit()

print(inputs.starting_dir)
print(main_tree_content)
dirs, files = count_dirs_and_files(tree_map, inputs.flag_data)

summary = generate_summary(dirs, files, inputs.flag_data.show_only_dirs)
print(summary)
