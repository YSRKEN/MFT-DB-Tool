import QueryType from "model/QueryType";
import { Lens } from "constant";

class HasImageStabilization implements QueryType {
  readonly name: string = 'HasImageStabilization';
  readonly prefixMessage: string = '手ブレ補正機能がある';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.has_image_stabilization);
  }
}

export default HasImageStabilization;
