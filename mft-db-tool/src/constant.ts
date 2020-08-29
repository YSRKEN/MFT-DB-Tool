import QueryType from "model/QueryType";
import MaxWideFocalLength from "model/query/MaxWideFocalLength";
import MinTelephotoFocalLength from "model/query/MinTelephotoFocalLength";
import MaxWideFNumber from "model/query/MaxWideFNumber";
import MaxTelephotoFNumber from "model/query/MaxTelephotoFNumber";
import MaxWideMinFocusDistance from "model/query/MaxWideMinFocusDistance";
import MaxTelephotoMinFocusDistance from "model/query/MaxTelephotoMinFocusDistance";
import MinMaxPhotographingMagnification from "model/query/MinMaxPhotographingMagnification";
import FilterDiameter from "model/query/FilterDiameter";
import IsDripProof from "model/query/IsDripProof";
import HasImageStabilization from "model/query/HasImageStabilization";
import IsInnerZoom from "model/query/IsInnerZoom";
import MaxOverallDiameter from "model/query/MaxOverallDiameter";
import MaxOverallLength from "model/query/MaxOverallLength";
import MaxWeight from "model/query/MaxWeight";
import MaxPrice from "model/query/MaxPrice";

/** レンズ情報 */
export interface Lens {
  // レンズID
  id: number
  // レンズメーカー
  maker: string
  // レンズ名
  name: string
  // 品番
  product_number: string
  // 広角端の換算焦点距離[mm]
  wide_focal_length: number
  // 望遠端の換算焦点距離[mm]
  telephoto_focal_length: number
  // 広角端の開放F値
  wide_f_number: number
  // 望遠端の開放F値
  telephoto_f_number: number
  // 広角端の最短撮影距離[mm]
  wide_min_focus_distance: number
  // 望遠端の最短撮影距離[mm]
  telephoto_min_focus_distance: number
  // 最大撮影倍率
  max_photographing_magnification: number
  // フィルター径[mm]
  filter_diameter: number
  // 防塵防滴か？
  is_drip_proof: boolean
  // 手ブレ補正があるか？
  has_image_stabilization: boolean
  // インナーズームか？
  is_inner_zoom: boolean
  // 最大径[mm]
  overall_diameter: number
  // 全長[mm]
  overall_length: number
  // 質量[g]
  weight: number
  // メーカー希望小売価格[円]
  price: number
}

/** クエリタイプの一覧 */
export const QueryTypeList: QueryType[] = [
  new MaxWideFocalLength(),
  new MinTelephotoFocalLength(),
  new MaxWideFNumber(),
  new MaxTelephotoFNumber(),
  new MaxWideMinFocusDistance(),
  new MaxTelephotoMinFocusDistance(),
  new MinMaxPhotographingMagnification(),
  new FilterDiameter(),
  new IsDripProof(),
  new HasImageStabilization(),
  new IsInnerZoom(),
  new MaxOverallDiameter(),
  new MaxOverallLength(),
  new MaxWeight(),
  new MaxPrice(),
];

/** mmからmへの単位変換を伴うクエリタイプの一覧 */
export const MilliMeterToMeterQueryTypeList: string[] = ['MaxWideMinFocusDistance', 'MaxTelephotoMinFocusDistance'];

/** boolean処理なクエリタイプの一覧 */
export const BooleanQueryTypeList: string[] = ['IsDripProof', 'HasImageStabilization', 'IsInnerZoom'];

/** クエリ */
export interface Query {
  type: QueryType;
  value: number;
}
