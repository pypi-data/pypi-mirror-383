# for tests
sample = [
    {"id": "a", "priority": 0.4, "prerequisites": []},
    {"id": "b", "priority": 0.7, "prerequisites": []},
    {"id": "c", "priority": 0.4, "prerequisites": []},
    {"id": "d", "priority": 0.3, "prerequisites": []},
    {"id": "e", "priority": 0.8, "prerequisites": ["a", "b"]},
    {"id": "f", "priority": 0.9, "prerequisites": []},
    {"id": "g", "priority": 0.1, "prerequisites": ["i", "m"]},
    {"id": "h", "priority": 0.5, "prerequisites": []},
    {"id": "i", "priority": 0.45, "prerequisites": ["j"]},
    {"id": "j", "priority": 0.3, "prerequisites": []},
    {"id": "k", "priority": 0.8, "prerequisites": ["l", "m", "d"]},
    {"id": "l", "priority": 0.6, "prerequisites": ["o"]},
    {"id": "m", "priority": 0.9, "prerequisites": []},
    {"id": "n", "priority": 0.4, "prerequisites": ["o"]},
    {"id": "o", "priority": 0.2, "prerequisites": []},
    {"id": "p", "priority": 0.5, "prerequisites": []},
]


def dep_sort(task_list: list[dict]) -> list[dict]:
    """
    Sort list of dictionaries such that
      1) dependency constraints are satisfied and
      2) priority ordering is satisfied subject to (1)
    """
    # sort on priority to preserve priority order in the output
    task_list.sort(key=lambda t: t["priority"], reverse=True)
    task_ids = [t["id"] for t in task_list]

    # important to make changes in reverse priority order so that insertion preserves priority order
    dep_dict = {t["id"]: t["prerequisites"] for t in reversed(task_list) if t["prerequisites"]}
    print(dep_dict)

    def place_after(to_move: str, deps: list[str], id_list: list) -> bool:
        if not deps:
            return False
        idx1 = id_list.index(to_move)
        idx2 = max(map(id_list.index, deps))
        if idx1 > idx2:
            return False
        id_list.pop(idx1)
        id_list.insert(idx2, to_move)
        return True

    print(task_ids)
    count = 0
    maxcount = sum(range(len(task_ids) + 1))
    while count < maxcount:
        change_tracker = []
        for task_id, task_deps in dep_dict.items():
            changed = place_after(task_id, task_deps, task_ids)
            change_tracker.append(changed)
        unchanged = not any(change_tracker)
        print(task_ids)
        if unchanged:
            return sorted(task_list, key=lambda t: task_ids.index(t["id"]))
        count += 1

    print("ERROR ---------------------------------------------------")
    str(task_ids)
    for task_id, task_deps in dep_dict.items():
        changed = place_after(task_id, task_deps, task_ids)
        if changed:
            after = str(task_ids)
            print(after)

    raise ValueError("Graph contains a cycle.")

    # levels = {t: 0 for t in task_ids}
    # roots = list(filter(lambda t: t["depencies"] == [], task_list))
    # depended_on = {t: set() for t in task_ids}
    # for t in task_list:
    #     for d in t["prerequisites"]:
    #         depended_on[d].add(t)
    # dict_rep = json.dumps(levels)
    # new_rep = ""
    # while new_rep != dict_rep:
    #     dict_rep = json.dumps(levels)
    #     for t in task_list:
    #         levels[t["id"]] = max([levels[d] for d in t["prerequisites"]]) + 1
    #     new_rep = json.dumps(levels)
    # return sorted(task_list, key=lambda t: levels[t["id"]])
