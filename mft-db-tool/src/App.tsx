import React, { useState } from 'react';
import { Container, Row, Col, Table } from 'react-bootstrap';
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

  return (<Container>
    <Row className="my-3">
      <Col>
        <h1 className="text-center">レンズデータベース</h1>
      </Col>
    </Row>
    <Row className="my-3">
      <Col>
        <Table size="sm">
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
        </Table>
      </Col>
    </Row>
  </Container>);
}

export default App;
