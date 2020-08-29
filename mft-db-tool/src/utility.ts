import QueryType from "model/QueryType";
import { QueryTypeList, Lens, Query } from "constant";

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

/**
 * フィルターされた後のレンズ一覧を返す
 * @param lensList レンズ一覧
 * @param queryList フィルター一覧
 * @returns フィルターされた後のレンズ一覧
 */
export const calcFilteredLensList = (lensList: Lens[], queryList: Query[]) => {
  if (queryList.length === 0) {
    return lensList;
  }
  let temp = [...lensList];
  for (const query of queryList) {
    temp = query.type.filter(temp, query.value);
  }
  return temp;
};

/**
 * 文字列を浮動小数点数型に変換する。ただし変換できない場合、NaNになる場合はnullを返す
 * @param text 文字列
 * @returns 成功時はnumber型、失敗時はnullが返される
 */
export const parseFloat2 = (text: string): number | null => {
  try {
    // 入力チェック
    const value = parseFloat(text);
    if (isNaN(value)) {
      return null;
    }
    return value;
  } catch {
    return null;
  }
};
