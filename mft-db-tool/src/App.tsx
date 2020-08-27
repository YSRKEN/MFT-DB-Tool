import React, { useState } from 'react';
import { Container, Row, Col, Table } from 'react-bootstrap';
import 'App.css';

interface Lens {
  id: number
  maker: string
  name: string
  product_number: string
  wide_focal_length: number
  telephoto_focal_length: number
  wide_f_number: number
  telephoto_f_number: number
  wide_min_focus_distance: number
  telephoto_min_focus_distance: number
  max_photographing_magnification: number
  filter_diameter: number
  is_drip_proof: boolean
  has_image_stabilization: boolean
  is_inner_zoom: boolean
  overall_diameter: number
  overall_length: number
  weight: number
  price: number
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
