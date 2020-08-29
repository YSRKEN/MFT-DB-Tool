export interface Lens {
  id: number
  maker: string
  name: string
  product_number: string
  wide_focal_length: number
  telephoto_focal_length: number
  wide_f_number: number
  telephoto_f_number: number
  wide_min_focus_distance: number
  telephoto_min_focus_distance: number
  max_photographing_magnification: number
  filter_diameter: number
  is_drip_proof: boolean
  has_image_stabilization: boolean
  is_inner_zoom: boolean
  overall_diameter: number
  overall_length: number
  weight: number
  price: number
}
