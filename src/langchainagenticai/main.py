from typing import Optional, List
from src.langchainagenticai.graph.graph import build_graph


async def run_pipeline(
    person_image_paths: List[str],
    shirt_image_path:   Optional[str] = None,
    pants_image_path:   Optional[str] = None,
    dress_image_path:   Optional[str] = None,
) -> dict:
    graph = build_graph()

    initial_state = {
        "person_image_paths":          person_image_paths,
        "shirt_image_path":            shirt_image_path,
        "pants_image_path":            pants_image_path,
        "dress_image_path":            dress_image_path,
        "person_images_preprocessed":  [],
        "shirt_image_preprocessed":    None,
        "pants_image_preprocessed":    None,
        "dress_image_preprocessed":    None,
        "intermediate_result_path":    None,
        "result_image":                None,
        "result_images":               [],
        "status":                      "started",
        "error_message":               None,
    }

    final_state = await graph.ainvoke(initial_state)

    return {
        "status":         final_state["status"],
        "result_image":   final_state.get("result_image"),
        "result_images":  final_state.get("result_images", []),
        "error_message":  final_state.get("error_message"),
    }