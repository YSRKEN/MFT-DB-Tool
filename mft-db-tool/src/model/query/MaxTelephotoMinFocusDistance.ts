import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxTelephotoMinFocusDistance implements QueryType {
  readonly name: string = 'MaxTelephotoMinFocusDistance';
  readonly prefixMessage: string = '望遠端の最短撮影距離が';
  readonly suffixMessage: string = 'm 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.telephoto_min_focus_distance <= value);
  }
}

export default MaxTelephotoMinFocusDistance;
