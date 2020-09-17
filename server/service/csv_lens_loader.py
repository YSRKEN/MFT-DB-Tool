import csv

from constant import Lens

DIR = 'csv'


def load_csv_lens(name: str):
    with open(f'{DIR}/{name}') as f:
        reader = csv.reader(f)
        next(reader)
        return [
            Lens(
                id=0,
                maker=row[1],
                name=row[2],
                product_number=row[3],
                wide_focal_length=int(row[4]),
                telephoto_focal_length=int(row[5]),
                wide_f_number=float(row[6]),
                telephoto_f_number=float(row[7]),
                wide_min_focus_distance=float(row[8]),
                telephoto_min_focus_distance=float(row[9]),
                max_photographing_magnification=float(row[10]),
                filter_diameter=float(row[11]),
                is_drip_proof=bool(row[12]),
                has_image_stabilization=bool(row[13]),
                is_inner_zoom=bool(row[14]),
                overall_diameter=float(row[15]),
                overall_length=float(row[16]),
                weight=float(row[17]),
                price=int(row[18])
            ) for row in reader
        ]
