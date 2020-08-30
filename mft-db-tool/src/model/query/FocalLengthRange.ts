import QueryType from "model/QueryType";
import { Lens } from "constant";

class FocalLengthRange implements QueryType {
  readonly name: string = 'FocalLengthRange';
  readonly prefixMessage: string = '焦点距離の取りうる倍率(＝望遠端/広角端)が';
  readonly suffixMessage: string = '倍以上';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.telephoto_focal_length >= lens.wide_focal_length * value);
  }
}

export default FocalLengthRange;
