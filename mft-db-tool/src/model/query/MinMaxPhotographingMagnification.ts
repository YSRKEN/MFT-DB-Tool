import QueryType from "model/QueryType";
import { Lens } from "constant";

class MinMaxPhotographingMagnification implements QueryType {
  readonly name: string = 'MinMaxPhotographingMagnification';
  readonly prefixMessage: string = '換算最大撮影倍率が';
  readonly suffixMessage: string = '倍 以上';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.max_photographing_magnification >= value);
  }
}

export default MinMaxPhotographingMagnification;
