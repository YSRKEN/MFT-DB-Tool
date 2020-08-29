import QueryType from "model/QueryType";
import { QueryTypeList } from "constant";

/**
 * クエリタイプ指定文字列によって、どういったクエリを生やすかを決める
 * @param queryType クエリタイプ指定文字列
 * @param value 値
 * @returns クエリ
 */
export const createQuery = (queryType: string, value: number): {type: QueryType, value: number} => {
  const temp = QueryTypeList.filter(q => q.name === queryType);
  if (temp.length > 0) {
    return {type: temp[0], value};
  } else {
    throw Error('誤ったクエリ種類が入力されました.');
  }
};
