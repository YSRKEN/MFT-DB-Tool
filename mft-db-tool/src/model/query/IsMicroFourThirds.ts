import QueryType from "model/QueryType";
import { Lens } from "constant";

class IsMicroFourThirds implements QueryType {
  readonly name: string = 'IsMicroFourThirds';
  readonly prefixMessage: string = 'マイクロフォーサーズマウントである';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.mount === 'マイクロフォーサーズ');
  }
}

export default IsMicroFourThirds;
