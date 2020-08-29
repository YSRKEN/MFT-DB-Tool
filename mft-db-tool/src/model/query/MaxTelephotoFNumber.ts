import QueryType from "model/QueryType";
import { Lens } from "constant";

class MaxTelephotoFNumber implements QueryType {
  readonly name: string = 'MaxTelephotoFNumber';
  readonly prefixMessage: string = '望遠端のF値がF';
  readonly suffixMessage: string = ' 以下';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.telephoto_f_number <= value);
  }
}

export default MaxTelephotoFNumber;
