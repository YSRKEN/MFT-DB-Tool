import React from "react";
import { Form, Col, Button } from "react-bootstrap";
import { QueryTypeList, BooleanQueryTypeList } from "constant";

const AddQueryForm: React.FC<{
  queryType: string,
  setQueryType: (v: string) => void,
  queryValue: string,
  setQueryValue: (v: string) => void,
  addQuery: () => void
}> = ({queryType, setQueryType, queryValue, setQueryValue, addQuery}) => {
  return (
    <Form>
      <Form.Row>
        <Col xs="auto" className="mt-3">
          <Form.Control as="select" value={queryType}
            onChange={e => setQueryType(e.currentTarget.value)}>
            {QueryTypeList.map(q =>
              <option key={q.name} value={q.name}>{q.prefixMessage}</option>
            )}
          </Form.Control>
        </Col>
        {BooleanQueryTypeList.includes(queryType)
          ? <></>
          : <>
            <Col xs="auto" className="mt-3">
              <Form.Control value={queryValue} placeholder="数値を入力"
                onChange={e => setQueryValue(e.currentTarget.value)} />
            </Col>
            <Col xs="auto" className="mt-3">
              <Form.Control as="select" value={queryType} readOnly>
                {QueryTypeList.map(q =>
                  <option key={q.name} value={q.name}>{q.suffixMessage}</option>
                )}
              </Form.Control>
            </Col>
          </>}
        <Col xs="auto" className="mt-3">
          <Button onClick={addQuery}>条件を追加</Button>
        </Col>
      </Form.Row>
    </Form>
  );
};

export default AddQueryForm;
