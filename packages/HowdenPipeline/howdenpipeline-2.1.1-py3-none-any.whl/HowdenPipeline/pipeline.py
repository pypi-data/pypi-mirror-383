import json
import hashlib
from pathlib import Path
import networkx as nx
import concurrent.futures

class GraphPipeline:
    def __init__(self, root_folder: str):
        self.file_paths_pdf = list(Path(root_folder).rglob("*.pdf"))
        self.base_graph = nx.DiGraph()   # ✅ Base structure instead of single shared graph

    def traversal_order(self, graph):
        return list(nx.topological_sort(graph))

    def add_node(self, cls, dependencies=None, track: bool = False, filetype=None):
        node_id = hex(id(cls))
        name = self.ekstra_name(cls) if self.ekstra_name(cls) else cls.__class__.__name__
        node_hash = self.compute_hash(cls)
        node_label = f"{name}_{node_hash}" if node_hash else name

        if dependencies:
            for dep_obj in dependencies:
                dep = hex(id(dep_obj))  # normalize
                dep_path = self.base_graph.nodes[dep].get("full_path", [])
                full_path = dep_path + [node_label]

                self.base_graph.add_edge(dep, node_id)

                if node_id not in self.base_graph:
                    self.base_graph.add_node(node_id)

                self.base_graph.nodes[node_id].update(
                    cls=cls,
                    name=name,
                    track=track,
                    filetype=filetype,
                    result=None,
                    hash=node_hash,
                    hash_path=[node_hash],
                    full_path=full_path
                )
        else:
            self.base_graph.add_node(
                node_id,
                cls=cls,
                name=name,
                track=track,
                filetype=filetype,
                result=None,
                hash=node_hash,
                hash_path=[node_hash],
                full_path=[node_label]
            )

    def get_dependency_paths(self, graph):
        return ["/".join(graph.nodes[n]["full_path"]) for n in graph.nodes]

    def _run_for_file(self, file_path, graph):
        print(f"Processing {file_path}")

        for node in self.traversal_order(graph):
            step = graph.nodes[node]["cls"]
            dep_path = "/".join(graph.nodes[node]["full_path"])
            folder_path = Path(file_path.parent / dep_path)
            folder_path.mkdir(parents=True, exist_ok=True)

            result_file_path = folder_path / Path("result").with_suffix(
                f".{graph.nodes[node]['filetype']}"
            )

            if result_file_path.exists():
                # save parameters
                json_parameter = folder_path / "parameter.json"
                attrs = {
                    k: v
                    for k, v in step.__dict__.items()
                    if not k.startswith("_") and k not in ("client", "provider")
                }
                serializable_attrs = self._make_serializable(attrs)
                json_parameter.write_text(
                    json.dumps(serializable_attrs, indent=2, sort_keys=True, ensure_ascii=True),
                    encoding="utf-8",
                )

                # collect dependency **paths** (NOT contents)
                dep_paths = [
                    data["result_path_from_dep"]
                    for _pred, _succ, data in graph.in_edges(node, data=True)
                    if "result_path_from_dep" in data
                ]

                # ✅ Convert to Path objects for your step
                if dep_paths:
                    dep_paths = [Path(p) for p in dep_paths]
                    input_data = dep_paths[0] if len(dep_paths) == 1 else dep_paths
                else:
                    # root node: pass the current PDF as Path
                    input_data = Path(file_path) if not isinstance(file_path, Path) else file_path

                # run the step (now receiving Path or list[Path])
                result = step(input_data)
                result_file_path.write_text(result, encoding="utf-8")

            # propagate the **result path** to children
            for _u, _v, data in graph.out_edges(node, data=True):
                data["result_path_from_dep"] = str(result_file_path)

        return file_path


    def execute(self, workers=4):
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self._run_for_file, file_path, self.base_graph.copy())
               for file_path in self.file_paths_pdf]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        return results

    # ---------------------------
    # Helpers
    # ---------------------------
    @staticmethod
    def ekstra_name(step):
        try:
            return step.name
        except:
            return ""

    @staticmethod
    def _make_serializable(obj):
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple, set)):
            return [GraphPipeline._make_serializable(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: GraphPipeline._make_serializable(v) for k, v in sorted(obj.items())}
        elif hasattr(obj, "__dict__"):
            return GraphPipeline._make_serializable(vars(obj))
        else:
            return f"{type(obj).__name__}:{repr(obj)}"

    @staticmethod
    def compute_hash(cls) -> str:
        attrs = {
            k: v
            for k, v in cls.__dict__.items()
            if k != "hash" and not k.startswith("_") and k not in ("client", "provider")
        }
        serializable_attrs = GraphPipeline._make_serializable(attrs)
        attrs_str = json.dumps(serializable_attrs, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(attrs_str.encode()).hexdigest()[:8]
