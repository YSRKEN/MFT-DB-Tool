import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxWideFocalLength implements QueryType {
  readonly name: string = 'MaxWideFocalLength';
  readonly prefixMessage: string = '広角端の換算焦点距離が';
  readonly suffixMessage: string = 'mm 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.wide_focal_length <= value);
  }
}

export default MaxWideFocalLength;
