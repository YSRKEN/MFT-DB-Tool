import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxWeight implements QueryType {
  readonly name: string = 'MaxWeight';
  readonly prefixMessage: string = 'レンズの質量が';
  readonly suffixMessage: string = 'g 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.weight <= value);
  }
}

export default MaxWeight;
