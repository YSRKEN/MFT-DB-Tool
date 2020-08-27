import React, { useState } from 'react';
import { Container, Row, Col, Table, Form, Button } from 'react-bootstrap';
import 'App.css';

type QueryType = 'MinWideFocalLength' | 'MaxTelephotoFocalLength';

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

interface Query {
  type: QueryType;
  value: number;
}

const QueryButton: React.FC<{query: Query}> = ({query}) => {
  let text = '';
  switch (query.type) {
    case 'MinWideFocalLength':
      text = `広角端の換算焦点距離が${query.value}mm 以下`;
      break;
    case 'MaxTelephotoFocalLength':
      text = `望遠端の換算焦点距離が${query.value}mm 以上`;
      break;
  }
  return <Button variant="info" className="mr-3 mt-3">{text}</Button>
};

const App: React.FC = () => {
  const [lensList, setLensList] = useState<Lens[]>([]);
  const [queryType, setQueryType] = useState<QueryType>('MinWideFocalLength');
  const [queryList] = useState<Query[]>([
    {type: 'MinWideFocalLength', value: 28},
    {type: 'MaxTelephotoFocalLength', value: 70},
  ]);

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
        <Form>
          <Form.Row>
            <Col xs="auto">
              <Form.Control as="select" value={queryType}
                onChange={e => setQueryType(e.currentTarget.value as QueryType)}>
                <option value="MinWideFocalLength">広角端の換算焦点距離が</option>
                <option value="MaxTelephotoFocalLength">望遠端の換算焦点距離が</option>
              </Form.Control>
            </Col>
            <Col xs={1}>
              <Form.Control />
            </Col>
            <Col xs="auto">
              <Form.Control as="select" value={queryType} readOnly>
                <option value="MinWideFocalLength">mm 以下</option>
                <option value="MaxTelephotoFocalLength">mm 以上</option>
              </Form.Control>
            </Col>
            <Col xs="auto">
              <Button>条件を追加</Button>
            </Col>
          </Form.Row>
        </Form>
      </Col>
    </Row>
    <Row className="my-3">
      <Col>
        {queryList.map(query => <QueryButton key={query.type} query={query} />)}
      </Col>
    </Row>
    <Row className="my-3">
      <Col>
        <Table size="sm" striped>
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
