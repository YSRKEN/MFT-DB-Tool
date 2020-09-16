import React, { useState } from "react";
import { Lens } from "constant";
import { Table, Button } from "react-bootstrap";

const LensTable: React.FC<{ lensList: Lens[] }> = ({ lensList }) => {
  // 選択されているレンズ名
  const [selectedLensName, setSelectedLensName] = useState('');

  // 選択されているレンズ名を前後に、配列を分割する
  const lensListA: Lens[] = [];
  const lensListB: Lens[] = [];
  let lensIndex = -1;
  for (let i = 0; i < lensList.length; i += 1) {
    lensListA.push(lensList[i]);
    if (lensList[i].name === selectedLensName) {
      lensIndex = i;
      for (let j = i + 1; j < lensList.length; j += 1) {
        lensListB.push(lensList[j]);
      }
      break;
    }
  }

  // 詳細ボタンを押した際の処理
  const onClickDetailButton = (lensName: string) => {
    if (lensName !== selectedLensName) {
      setSelectedLensName(lensName);
    } else {
      setSelectedLensName('');
    }
  };

  return (<Table size="sm" striped>
    <thead>
      <tr>
        <th>メーカー</th>
        <th>レンズ名</th>
        <th>価格(税抜)</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      {lensListA.map(lens => <tr key={lens.id}>
        <td className="align-middle text-nowrap">{lens.maker}</td>
        <td className="align-middle">{lens.name}</td>
        <td className="align-middle text-nowrap">{lens.price}</td>
        <td className="align-middle text-nowrap"><Button size="sm" onClick={() => onClickDetailButton(lens.name)}>詳細</Button></td>
      </tr>)}
      {selectedLensName !== '' && lensIndex >= 0
        ? <tr>
            <td colSpan={4}>
              <ul>
                <li>品番：{lensListA[lensIndex].product_number}</li>
                <li>換算焦点距離：{lensListA[lensIndex].wide_focal_length === lensListA[lensIndex].telephoto_focal_length
                  ? `${lensListA[lensIndex].wide_focal_length}mm`
                  : `${lensListA[lensIndex].wide_focal_length}mm～${lensListA[lensIndex].telephoto_focal_length}mm`}</li>
                <li>F値：{lensListA[lensIndex].wide_f_number === lensListA[lensIndex].telephoto_f_number
                  ? `F${lensListA[lensIndex].wide_f_number}`
                  : `F${lensListA[lensIndex].wide_f_number}～F${lensListA[lensIndex].telephoto_f_number}`}</li>
                <li>最短撮影距離：{lensListA[lensIndex].wide_min_focus_distance === lensListA[lensIndex].telephoto_min_focus_distance
                  ? `${lensListA[lensIndex].wide_min_focus_distance / 1000}m`
                  : `${lensListA[lensIndex].wide_min_focus_distance / 1000}m～${lensListA[lensIndex].telephoto_min_focus_distance / 1000}m`}</li>
                <li>換算最大撮影倍率：{lensListA[lensIndex].max_photographing_magnification}倍</li>
                <li>フィルター径：{
                  lensListA[lensIndex].filter_diameter >= 1
                  ? `${lensListA[lensIndex].filter_diameter}mm`
                  : '装着不可'
                }</li>
                <li>最大径×全長：{lensListA[lensIndex].overall_diameter}mm×{lensListA[lensIndex].overall_length}mm</li>
                <li>質量：{lensListA[lensIndex].weight}g</li>
                <li>レンズマウント：{lensListA[lensIndex].mount}</li>
                <li>その他属性：
                  {lensListA[lensIndex].is_drip_proof ? '防塵防滴　' : ''}
                  {lensListA[lensIndex].has_image_stabilization ? 'レンズ内手ブレ補正　' : ''}
                  {lensListA[lensIndex].is_inner_zoom ? 'インナーズーム　' : ''}</li>
              </ul>
            </td>
        </tr>
        : <></>}
      {lensListB.map(lens => <tr key={lens.id}>
        <td>{lens.maker}</td>
        <td>{lens.name}</td>
        <td>{lens.price}</td>
        <td><Button size="sm" className="text-nowrap" onClick={() => onClickDetailButton(lens.name)}>詳細</Button></td>
      </tr>)}
    </tbody>
  </Table>);
};

export default LensTable;
