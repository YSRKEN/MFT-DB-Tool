import React from "react";
import { Lens } from "constant";
import { Table } from "react-bootstrap";

const LensTable: React.FC<{ lensList: Lens[] }> = ({ lensList }) => {
  return (
    <Table size="sm" striped>
      <thead>
        <tr>
          <th>メーカー</th>
          <th>レンズ名</th>
          <th>価格(税抜)</th>
        </tr>
      </thead>
      <tbody>
        {lensList.map(lens => <tr key={lens.id}>
          <td>{lens.maker}</td>
          <td>{lens.name}</td>
          <td>{lens.price}</td>
        </tr>)}
      </tbody>
    </Table>
  );
};

export default LensTable;
