from dataclasses import dataclass

from dataclasses_json import dataclass_json

DATABASE_PATH = 'database.db'


@dataclass_json
@dataclass
class Lens:
    id: int = 0
    maker: str = ''
    name: str = ''
    product_number: str = ''
    wide_focal_length: int = 0
    telephoto_focal_length: int = 0
    wide_f_number: float = 0
    telephoto_f_number: float = 0
    wide_min_focus_distance: float = 0
    telephoto_min_focus_distance: float = 0
    max_photographing_magnification: float = 0
    filter_diameter: float = 0
    is_drip_proof: bool = False
    has_image_stabilization: bool = False
    is_inner_zoom: bool = False
    overall_diameter: float = 0
    overall_length: float = 0
    weight: float = 0
    price: int = 0
    mount: str = ''
