import QueryType from "model/QueryType";
import { Lens } from "constant";

class IsDripProof implements QueryType {
  readonly name: string = 'IsDripProof';
  readonly prefixMessage: string = '防塵防滴である';
  readonly suffixMessage: string = '';

  filter(lensList: Lens[], value: number): Lens[] {
    return lensList.filter(lens => lens.is_drip_proof);
  }
}

export default IsDripProof;
