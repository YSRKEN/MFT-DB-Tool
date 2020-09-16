import QueryType from "model/QueryType";
import { Lens } from "constant";

class IsLensFilter implements QueryType {
  readonly name: string = 'IsLensFilter';
  readonly prefixMessage: string = 'ねじ込み式フィルターを付けられる';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.filter_diameter >= 1);
  }
}

export default IsLensFilter;
