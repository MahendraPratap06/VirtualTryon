from typing import Optional, List
from typing_extensions import TypedDict


class TryOnState(TypedDict):
    # ── Person inputs (up to 3 pose photos) ───────────────────────────────────
    person_image_paths:          List[str]        # required — at least 1
    shirt_image_path:            Optional[str]
    pants_image_path:            Optional[str]
    dress_image_path:            Optional[str]

    # ── Preprocessed ───────────────────────────────────────────────────────────
    person_images_preprocessed:  List[str]
    shirt_image_preprocessed:    Optional[str]
    pants_image_preprocessed:    Optional[str]
    dress_image_preprocessed:    Optional[str]

    # ── Output ─────────────────────────────────────────────────────────────────
    result_image:                Optional[str]    # primary (first) result
    result_images:               List[str]        # all results (one per pose)
    intermediate_result_path:    Optional[str]

    # ── Status ─────────────────────────────────────────────────────────────────
    status:                      str
    error_message:               Optional[str]