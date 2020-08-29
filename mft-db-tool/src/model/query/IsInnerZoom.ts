import QueryType from "model/QueryType";
import { Lens } from "constant";

class IsInnerZoom implements QueryType {
  readonly name: string = 'IsInnerZoom';
  readonly prefixMessage: string = 'インナーズームである';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.is_inner_zoom);
  }
}

export default IsInnerZoom;
