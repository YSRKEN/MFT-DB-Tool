import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxOverallLength implements QueryType {
  readonly name: string = 'MaxOverallLength';
  readonly prefixMessage: string = 'レンズの全長が';
  readonly suffixMessage: string = 'mm 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.overall_length <= value);
  }
}

export default MaxOverallLength;
