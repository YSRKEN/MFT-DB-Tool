import React, { useState } from 'react';
import 'App.css';

interface Lens {
  filter_diameter: number
  has_image_stabilization: boolean
  id: number
  is_drip_proof: boolean
  is_inner_zoom: boolean
  maker: string
  max_photographing_magnification: number
  name: string
  overall_diameter: number
  overall_length: number
  price: number
  product_number: string
  telephoto_f_number: number
  telephoto_focal_length: number
  telephoto_min_focus_distance: number
  weight: number
  wide_f_number: number
  wide_focal_length: number
  wide_min_focus_distance: number
}

const App: React.FC = () => {
  const [lensList, setLensList] = useState<Lens[]>([]);

  fetch('./lens_data.json').then(res => {
    if (res.ok) {
      res.json().then(data => {
        setLensList(data);
      });
    }
  });

  return (<>
    <h1>レンズデータベース</h1>
    <table cellSpacing={0} cellPadding={5}>
      <thead>
        <th>メーカー</th>
        <th>レンズ名</th>
        <th>価格(税抜)</th>
      </thead>
      <tbody>
        {lensList.map(lens => <tr>
          <td>{lens.maker}</td>
          <td>{lens.name}</td>
          <td>{lens.price}</td>
        </tr>)}
      </tbody>
    </table>
  </>);
}

export default App;
