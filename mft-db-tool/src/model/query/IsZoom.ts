import QueryType from "model/QueryType";
import { Lens } from "constant";

class IsZoom implements QueryType {
  readonly name: string = 'IsZoom';
  readonly prefixMessage: string = 'ズームレンズである';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.wide_focal_length !== lens.telephoto_focal_length);
  }
}

export default IsZoom;
