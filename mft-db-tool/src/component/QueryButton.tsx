import React from "react";
import { Query, BooleanQueryTypeList, MilliMeterToMeterQueryTypeList } from "constant";
import { Button } from "react-bootstrap";

const QueryButton: React.FC<{ query: Query, deleteQuery: () => void }> = ({ query, deleteQuery }) => {
  // Boolean型な判定条件の場合、数値を表示する必要がない
  if (BooleanQueryTypeList.includes(query.type.name)) {
    return <Button variant="info" className="mr-3 mt-3" onClick={deleteQuery}>{query.type.prefixMessage}</Button>;
  }

  // 単位変換を伴う場合
  if (MilliMeterToMeterQueryTypeList.includes(query.type.name)) {
    const text = `${query.type.prefixMessage}${query.value / 1000}${query.type.suffixMessage}`;
    return <Button variant="info" className="mr-3 mt-3" onClick={deleteQuery}>{text}</Button>;
  }

  // 単位変換を伴わない場合
  const text = `${query.type.prefixMessage}${query.value}${query.type.suffixMessage}`;
  return <Button variant="info" className="mr-3 mt-3" onClick={deleteQuery}>{text}</Button>;
};

export default QueryButton;
