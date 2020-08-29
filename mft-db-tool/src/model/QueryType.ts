import { Lens } from "constant";

abstract class QueryType {
  // 型名
  abstract readonly name: string = '';
  // 数値部分の「手前」に表示するMessage
  abstract readonly prefixMessage: string;
  // 数値部分の「後」に表示するMessage
  abstract readonly suffixMessage: string;

  // フィルタ処理
  abstract filter(lensList: Lens[], value: number): Lens[];
}

export default QueryType;
