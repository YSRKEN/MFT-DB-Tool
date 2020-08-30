import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxWideFNumber implements QueryType {
  readonly name: string = 'MaxWideFNumber';
  readonly prefixMessage: string = '広角端のF値がF';
  readonly suffixMessage: string = ' 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.wide_f_number <= value);
  }
}

export default MaxWideFNumber;
