import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Table, Form, Button } from 'react-bootstrap';
import { Decimal } from 'decimal.js';
import 'App.css';

type QueryType = 'MaxWideFocalLength' | 'MinTelephotoFocalLength' | 'MaxWideFNumber' | 'MaxTelephotoFNumber'
  | 'MaxWideMinFocusDistance' | 'MaxTelephotoMinFocusDistance';

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

const QueryButton: React.FC<{ query: Query, deleteQuery: () => void }> = ({ query, deleteQuery }) => {
  let text = '';
  switch (query.type) {
    case 'MaxWideFocalLength':
      text = `広角端の換算焦点距離が${query.value}mm 以下`;
      break;
    case 'MinTelephotoFocalLength':
      text = `望遠端の換算焦点距離が${query.value}mm 以上`;
      break;
    case 'MaxWideFNumber':
      text = `広角端のF値がF${query.value} 以下`;
      break;
    case 'MaxTelephotoFNumber':
      text = `望遠端のF値がF${query.value} 以下`;
      break;
    case 'MaxWideMinFocusDistance':
      text = `広角端の最短撮影距離が${query.value / 1000}m 以下`;
      break;
    case 'MaxTelephotoMinFocusDistance':
      text = `望遠端の最短撮影距離が${query.value / 1000}m 以下`;
      break;
  }
  return <Button variant="info" className="mr-3 mt-3" onClick={deleteQuery}>{text}</Button>
};

const App: React.FC = () => {
  const [lensList, setLensList] = useState<Lens[]>([]);
  const [lensList2, setLensList2] = useState<Lens[]>([]);
  const [queryType, setQueryType] = useState<QueryType>('MaxWideFocalLength');
  const [queryValue, setQueryValue] = useState<string>('');
  const [queryList, setQueryList] = useState<Query[]>([]);

  useEffect(() => {
    fetch('./lens_data.json').then(res => {
      if (res.ok) {
        res.json().then(data => {
          setLensList(data);
        });
      }
    });
  }, []);

  useEffect(() => {
    if (queryList.length === 0) {
      setLensList2([...lensList]);
      return;
    }
    let temp = [...lensList];
    for (const query of queryList) {
      switch (query.type) {
        case 'MaxWideFocalLength':
          temp = temp.filter(r => r.wide_focal_length <= query.value);
          break;
        case 'MinTelephotoFocalLength':
          temp = temp.filter(r => r.telephoto_focal_length >= query.value);
          break;
        case 'MaxWideFNumber':
          temp = temp.filter(r => r.wide_f_number <= query.value);
          break;
        case 'MaxTelephotoFNumber':
          temp = temp.filter(r => r.telephoto_f_number <= query.value);
          break;
        case 'MaxWideMinFocusDistance':
          temp = temp.filter(r => r.wide_min_focus_distance <= query.value);
          break;
        case 'MaxTelephotoMinFocusDistance':
          temp = temp.filter(r => r.telephoto_min_focus_distance <= query.value);
          break;
      }
    }
    setLensList2(temp);
  }, [lensList, queryList]);

  const addQuery = () => {
    try {
      const value = parseFloat(queryValue);
      if (isNaN(value)) {
        window.alert('エラー：その条件では追加できません。');
        return;
      }
      if (queryType === 'MaxWideMinFocusDistance' || queryType === 'MaxTelephotoMinFocusDistance') {
        const temp = new Decimal(queryValue);
        const temp2 = temp.mul(new Decimal(1000));
        const value2 = temp2.toNumber();
        console.log(value2);
        setQueryList([...queryList.filter(q => q.type !== queryType), { type: queryType, value: value2 }]);
      } else {
        setQueryList([...queryList.filter(q => q.type !== queryType), { type: queryType, value }]);
      }
    } catch {
      window.alert('エラー：その条件では追加できません。');
    };
  };

  const deleteQuery = (queryType: QueryType) => {
    setQueryList(queryList.filter(q => q.type !== queryType));
  };

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
                <option value="MaxWideFocalLength">広角端の換算焦点距離が</option>
                <option value="MinTelephotoFocalLength">望遠端の換算焦点距離が</option>
                <option value="MaxWideFNumber">広角端のF値がF</option>
                <option value="MaxTelephotoFNumber">望遠端のF値がF</option>
                <option value="MaxWideMinFocusDistance">広角端の最短撮影距離が</option>
                <option value="MaxTelephotoMinFocusDistance">望遠端の最短撮影距離が</option>
              </Form.Control>
            </Col>
            <Col xs={2}>
              <Form.Control value={queryValue} placeholder="数値を入力"
                onChange={e => setQueryValue(e.currentTarget.value)} />
            </Col>
            <Col xs="auto">
              <Form.Control as="select" value={queryType} readOnly>
                <option value="MaxWideFocalLength">mm 以下</option>
                <option value="MinTelephotoFocalLength">mm 以上</option>
                <option value="MaxWideFNumber">以下</option>
                <option value="MaxTelephotoFNumber">以下</option>
                <option value="MaxWideMinFocusDistance">m 以下</option>
                <option value="MaxTelephotoMinFocusDistance">m 以下</option>
              </Form.Control>
            </Col>
            <Col xs="auto">
              <Button onClick={addQuery}>条件を追加</Button>
            </Col>
          </Form.Row>
        </Form>
      </Col>
    </Row>
    <Row className="my-3">
      <Col>
        {queryList.map(query => <QueryButton key={query.type} query={query} deleteQuery={() => deleteQuery(query.type)} />)}
      </Col>
    </Row>
    <Row className="my-3">
      <Col>
        <Table size="sm" striped>
          <thead>
            <tr>
              <th>メーカー</th>
              <th>レンズ名</th>
              <th>価格(税抜)</th>
            </tr>
          </thead>
          <tbody>
            {lensList2.map(lens => <tr key={lens.id}>
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
