import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxOverallDiameter implements QueryType {
  readonly name: string = 'MaxOverallDiameter';
  readonly prefixMessage: string = 'レンズ全体の直径が';
  readonly suffixMessage: string = 'mm 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.overall_diameter <= value);
  }
}

export default MaxOverallDiameter;
