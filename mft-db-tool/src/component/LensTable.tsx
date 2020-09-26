import React, { useState } from "react";
import { Lens } from "constant";
import { Table, Button } from "react-bootstrap";

const LensRecord: React.FC<{
  lens: Lens,
  onClickDetailButton: (s: string) => void
}> = ({ lens, onClickDetailButton }) => (
  <tr>
    <td className="align-middle text-nowrap">{lens.maker}</td>
    <td className="align-middle">{lens.name}</td>
    <td className="align-middle text-nowrap"><Button size="sm" onClick={() => onClickDetailButton(lens.name)}>詳細</Button></td>
  </tr>
);

const LensRecordDetail: React.FC<{ lens: Lens }> = ({ lens }) => {
  // 換算焦点距離
  const focalLength = lens.wide_focal_length === lens.telephoto_focal_length
    ? `${lens.wide_focal_length}mm`
    : `${lens.wide_focal_length}mm～${lens.telephoto_focal_length}mm`;

  // F値
  const fNumber = lens.wide_f_number === lens.telephoto_f_number
    ? `F${lens.wide_f_number}`
    : `F${lens.wide_f_number}～F${lens.telephoto_f_number}`;

  // 最短撮影距離
  const minFocusDistance = lens.wide_min_focus_distance === 0
    ? '不明'
    : lens.wide_min_focus_distance === lens.telephoto_min_focus_distance
      ? `${lens.wide_min_focus_distance / 1000}m`
      : `${lens.wide_min_focus_distance / 1000}m～${lens.telephoto_min_focus_distance / 1000}m`;

  // 換算最大撮影倍率
  const maxPhotographingMagnification = lens.max_photographing_magnification !== 0
    ? `${lens.max_photographing_magnification}倍`
    : '不明';

  // フィルター径
  const filterDiameter = lens.filter_diameter >= 1
    ? `${lens.filter_diameter}mm`
    : '装着不可';

  // その他属性
  const options: string[] = [];
  if (lens.is_drip_proof) {
    options.push('防塵防滴');
  }
  if (lens.has_image_stabilization) {
    options.push('レンズ内手ブレ補正');
  }
  if (lens.is_inner_zoom && lens.wide_focal_length !== lens.telephoto_focal_length) {
    options.push('インナーズーム');
  }

  // 価格
  const price = lens.price === 0 ? '不明' : `${lens.price}円`;

  return <tr>
    <td colSpan={4}>
      <ul>
        {lens.product_number !== '' ? <li>品番：{lens.product_number}</li> : <></>}
        <li>換算焦点距離：{focalLength}</li>
        <li>F値：{fNumber}</li>
        <li>最短撮影距離：{minFocusDistance}</li>
        <li>換算最大撮影倍率：{maxPhotographingMagnification}</li>
        <li>フィルター径：{filterDiameter}</li>
        <li>最大径×全長：{lens.overall_diameter}mm×{lens.overall_length}mm</li>
        <li>質量：{lens.weight}g</li>
        <li>レンズマウント：{lens.mount}</li>
        {options.length > 0
          ? <li>その他属性：{options.join('、')}</li>
          : <></>
        }
        <li>希望小売価格(税抜)：{price}</li>
        <li>製品URL：<a href={lens.url} rel="noopener noreferrer" target="_blank">{lens.url}</a></li>
      </ul>
    </td>
  </tr>;
};

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
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      {lensListA.map(lens => <LensRecord lens={lens} key={lens.id} onClickDetailButton={onClickDetailButton} />)}
      {selectedLensName !== '' && lensIndex >= 0
        ? <LensRecordDetail lens={lensListA[lensIndex]} />
        : <></>}
      {lensListB.map(lens => <LensRecord lens={lens} key={lens.id} onClickDetailButton={onClickDetailButton} />)}
    </tbody>
  </Table>);
};

export default LensTable;
