import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxWideMinFocusDistance implements QueryType {
  readonly name: string = 'MaxWideMinFocusDistance';
  readonly prefixMessage: string = '広角端の最短撮影距離が';
  readonly suffixMessage: string = 'm 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.wide_min_focus_distance <= value);
  }
}

export default MaxWideMinFocusDistance;
