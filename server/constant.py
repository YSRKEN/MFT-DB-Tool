from dataclasses import dataclass

from dataclasses_json import dataclass_json

DATABASE_PATH = 'database.db'


@dataclass_json
@dataclass
class Lens:
    id: int
    maker: str
    name: str
    product_number: str
    wide_focal_length: int
    telephoto_focal_length: int
    wide_f_number: float
    telephoto_f_number: float
    wide_min_focus_distance: float
    telephoto_min_focus_distance: float
    max_photographing_magnification: float
    filter_diameter: float
    is_drip_proof: bool
    has_image_stabilization: bool
    is_inner_zoom: bool
    overall_diameter: float
    overall_length: float
    weight: float
    price: int
    mount: str
