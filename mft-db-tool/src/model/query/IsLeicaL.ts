import QueryType from "model/QueryType";
import { Lens } from "constant";

class IsLeicaL implements QueryType {
  readonly name: string = 'IsLeicaL';
  readonly prefixMessage: string = 'ライカLマウントである';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.mount === 'ライカL');
  }
}

export default IsLeicaL;
