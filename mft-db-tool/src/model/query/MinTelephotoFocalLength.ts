import QueryType from "model/QueryType";
import { Lens } from "constant";

class MinTelephotoFocalLength implements QueryType {
  readonly name: string = 'MinTelephotoFocalLength';
  readonly prefixMessage: string = '望遠端の換算焦点距離が';
  readonly suffixMessage: string = 'mm 以上';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.telephoto_focal_length >= value);
  }
}

export default MinTelephotoFocalLength;
