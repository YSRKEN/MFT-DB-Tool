import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Table, Form, Button } from 'react-bootstrap';
import { Decimal } from 'decimal.js';
import 'App.css';

type QueryType = 'MaxWideFocalLength' | 'MinTelephotoFocalLength' | 'MaxWideFNumber' | 'MaxTelephotoFNumber'
  | 'MaxWideMinFocusDistance' | 'MaxTelephotoMinFocusDistance' | 'MinMaxPhotographingMagnification'
  | 'FilterDiameter' | 'IsDripProof' | 'HasImageStabilization' | 'IsInnerZoom';

const QueryTypeList: QueryType[] = [
  'MaxWideFocalLength', 'MinTelephotoFocalLength', 'MaxWideFNumber', 'MaxTelephotoFNumber',
  'MaxWideMinFocusDistance', 'MaxTelephotoMinFocusDistance', 'MinMaxPhotographingMagnification',
  'FilterDiameter', 'IsDripProof', 'HasImageStabilization', 'IsInnerZoom',
];

const QueryTypeToTextA: { [key: string]: string } = {
  "MaxWideFocalLength": '広角端の換算焦点距離が',
  "MinTelephotoFocalLength": '望遠端の換算焦点距離が',
  "MaxWideFNumber": '広角端のF値がF',
  "MaxTelephotoFNumber": '望遠端のF値がF',
  "MaxWideMinFocusDistance": '広角端の最短撮影距離が',
  "MaxTelephotoMinFocusDistance": '望遠端の最短撮影距離が',
  "MinMaxPhotographingMagnification": '換算最大撮影倍率が',
  "FilterDiameter": 'フィルター径が',
  'IsDripProof': '防塵防滴である',
  'HasImageStabilization': '手ブレ補正機能がある',
  'IsInnerZoom': 'インナーズームである',
};

const QueryTypeToTextB: { [key: string]: string } = {
  "MaxWideFocalLength": 'mm 以下',
  "MinTelephotoFocalLength": 'mm 以上',
  "MaxWideFNumber": ' 以下',
  "MaxTelephotoFNumber": ' 以下',
  "MaxWideMinFocusDistance": 'm 以下',
  "MaxTelephotoMinFocusDistance": 'm 以下',
  "MinMaxPhotographingMagnification": '倍 以上',
  "FilterDiameter": 'mm',
  'IsDripProof': '',
  'HasImageStabilization': '',
  'IsInnerZoom': '',
};

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

const calcFilteredLensList = (lensList: Lens[], queryList: Query[]) => {
  if (queryList.length === 0) {
    return lensList;
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
      case 'MinMaxPhotographingMagnification':
        temp = temp.filter(r => r.max_photographing_magnification >= query.value);
        break;
      case 'FilterDiameter':
        temp = temp.filter(r => r.filter_diameter === query.value);
        break;
      case 'IsDripProof':
        temp = temp.filter(r => r.is_drip_proof);
        break;
      case 'HasImageStabilization':
        temp = temp.filter(r => r.has_image_stabilization);
        break;
      case 'IsInnerZoom':
        temp = temp.filter(r => r.is_inner_zoom);
        break;
    }
  }
  return temp;
};

const QueryButton: React.FC<{ query: Query, deleteQuery: () => void }> = ({ query, deleteQuery }) => {
  const value = ['MaxWideMinFocusDistance', 'MaxTelephotoMinFocusDistance'].includes(query.type) ? query.value / 1000 : query.value;
  const text = ['IsDripProof', 'HasImageStabilization', 'IsInnerZoom'].includes(query.type)
    ? `${QueryTypeToTextA[query.type as string]}`
    : `${QueryTypeToTextA[query.type as string]}${value}${QueryTypeToTextB[query.type as string]}`;
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
    setLensList2(calcFilteredLensList(lensList, queryList));
  }, [lensList, queryList]);

  const addQuery = () => {
    try {
      if (['IsDripProof', 'HasImageStabilization', 'IsInnerZoom'].includes(queryType)) {
        setQueryList([...queryList.filter(q => q.type !== queryType), { type: queryType, value: 0 }]);
      } else {
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
                {QueryTypeList.map(q => <option key={q as string} value={q as string}>{QueryTypeToTextA[q as string]}</option>)}
              </Form.Control>
            </Col>
            {['IsDripProof', 'HasImageStabilization', 'IsInnerZoom'].includes(queryType)
              ? <></>
              : <>
                <Col xs={2}>
                  <Form.Control value={queryValue} placeholder="数値を入力"
                    onChange={e => setQueryValue(e.currentTarget.value)} />
                </Col>
                <Col xs="auto">
                  <Form.Control as="select" value={queryType} readOnly>
                    {QueryTypeList.map(q => <option key={q as string} value={q as string}>{QueryTypeToTextB[q as string]}</option>)}
                  </Form.Control>
                </Col>
              </>}
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
