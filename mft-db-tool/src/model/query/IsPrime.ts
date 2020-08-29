import QueryType from "model/QueryType";
import { Lens } from "constant";

class IsPrime implements QueryType {
  readonly name: string = 'IsPrime';
  readonly prefixMessage: string = '単焦点レンズである';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.wide_focal_length === lens.telephoto_focal_length);
  }
}

export default IsPrime;
