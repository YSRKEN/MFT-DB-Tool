import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Table, Form, Button } from 'react-bootstrap';
import 'App.css';
import { Lens, QueryTypeList } from 'constant';
import QueryType from 'model/QueryType';
import { createQuery } from 'utility';

interface Query {
  type: QueryType;
  value: number;
}

/**
 * フィルターされた後のレンズ一覧を返す
 * @param lensList レンズ一覧
 * @param queryList フィルター一覧
 * @returns フィルターされた後のレンズ一覧
 */
const calcFilteredLensList = (lensList: Lens[], queryList: Query[]) => {
  if (queryList.length === 0) {
    return lensList;
  }
  let temp = [...lensList];
  for (const query of queryList) {
    temp = query.type.filter(temp, query.value);
  }
  return temp;
};

const QueryButton: React.FC<{ query: Query, deleteQuery: () => void }> = ({ query, deleteQuery }) => {
  /*
  const value = ['MaxWideMinFocusDistance', 'MaxTelephotoMinFocusDistance'].includes(query.type) ? query.value / 1000 : query.value;
  const text = ['IsDripProof', 'HasImageStabilization', 'IsInnerZoom'].includes(query.type)
    ? `${QueryTypeToTextA[query.type as string]}`
    : `${QueryTypeToTextA[query.type as string]}${value}${QueryTypeToTextB[query.type as string]}`;
  return <Button variant="info" className="mr-3 mt-3" onClick={deleteQuery}>{text}</Button>*/
  const text = `${query.type.prefixMessage}${query.value}${query.type.suffixMessage}`;
  return <Button variant="info" className="mr-3 mt-3" onClick={deleteQuery}>{text}</Button>;
};

const App: React.FC = () => {
  const [lensList, setLensList] = useState<Lens[]>([]);
  const [lensList2, setLensList2] = useState<Lens[]>([]);
  const [queryType, setQueryType] = useState<string>('MaxWideFocalLength');
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
      const value = parseFloat(queryValue);
      if (isNaN(value)) {
        window.alert('エラー：その条件では追加できません。');
        return;
      }
      setQueryList([...queryList.filter(q => q.type.name !== queryType), createQuery(queryType, value)]);
    } catch {
      window.alert('エラー：その条件では追加できません。');
    };

/*    try {
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
    };*/
  };

  const deleteQuery = (queryType: string) => {
    setQueryList(queryList.filter(q => q.type.name !== queryType));
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
                onChange={e => setQueryType(e.currentTarget.value)}>
                {QueryTypeList.map(q => 
                  <option key={q.name} value={q.name}>{q.prefixMessage}</option>
                )}
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
                    {QueryTypeList.map(q =>
                      <option key={q.name} value={q.name}>{q.suffixMessage}</option>
                    )}
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
        {queryList.map(query => <QueryButton key={query.type.name} query={query} deleteQuery={() => deleteQuery(query.type.name)} />)}
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
