import QueryType from "model/QueryType";
import { Lens } from "constant";

class FilterDiameter implements QueryType {
  readonly name: string = 'FilterDiameter';
  readonly prefixMessage: string = 'フィルター径が';
  readonly suffixMessage: string = 'mm';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.filter_diameter === value);
  }
}

export default FilterDiameter;
