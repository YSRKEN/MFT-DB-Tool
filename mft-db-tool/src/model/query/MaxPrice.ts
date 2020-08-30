import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxPrice implements QueryType {
  readonly name: string = 'MaxPrice';
  readonly prefixMessage: string = 'レンズの希望小売価格が';
  readonly suffixMessage: string = '円 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.price <= value);
  }
}

export default MaxPrice;
