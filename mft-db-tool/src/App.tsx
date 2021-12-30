import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { Decimal } from 'decimal.js';
import 'App.css';
import { Lens, MilliMeterToMeterQueryTypeList, BooleanQueryTypeList, Query, QueryTypeList } from 'constant';
import { createQuery, calcFilteredLensList, parseFloat2, queryListToqueryString } from 'utility';
import QueryButton from 'component/QueryButton';
import LensTable from 'component/LensTable';
import AddQueryForm from 'component/AddQueryForm';
import TwitterShareButton from 'react-share/lib/TwitterShareButton';
import TwitterIcon from 'react-share/lib/TwitterIcon';

/** メインとなるComponent */
const App: React.FC = () => {
  // フィルタ前のレンズ一覧
  const [lensList, setLensList] = useState<Lens[]>([]);
  // フィルタ後のレンズ一覧
  const [lensList2, setLensList2] = useState<Lens[]>([]);
  // 選択されているクエリタイプ
  const [queryType, setQueryType] = useState<string>('MaxWideFocalLength');
  // クエリに入力する値
  const [queryValue, setQueryValue] = useState<string>('');
  // クエリ一覧
  const [queryList, setQueryList] = useState<Query[]>([]);
  // シェア用のクエリパラメーター
  const [queryParameter, setQueryParameter] = useState('');

  /** 起動時の読み込み */
  useEffect(() => {
    fetch('./lens_data.json').then(res => {
      if (res.ok) {
        res.json().then(data => {
          setLensList(data);
        });
      }
    });
  }, []);

  /** GETパラメーターの解釈 */
  useEffect(() => {
    const newQueryList: Query[] = [];
    const params = new URLSearchParams(document.location.search.substring(1));
    for (const queryType of QueryTypeList) {
      let val = params.get(queryType.name);
      if (val === null) {
        val = params.get(queryType.name.toLowerCase());
        if (val === null) {
          continue;
        }
      }
      const valFloat = parseFloat2(val);
      if (valFloat !== null) {
        newQueryList.push({
          type: queryType,
          value: valFloat
        });
      }
    }
    setQueryList(newQueryList);
  }, []);

  /** 自動でクエリパラメーター情報を修正 */
  useEffect(() => {
    setQueryParameter(queryListToqueryString(queryList));
  }, [queryList]);

  // 自動でフィルタしておく
  useEffect(() => {
    setLensList2(calcFilteredLensList(lensList, queryList));
  }, [lensList, queryList]);

  // クエリを追加する
  const addQuery = () => {
    // Boolean型な判定条件の場合
    if (BooleanQueryTypeList.includes(queryType)) {
      setQueryList([...queryList.filter(q => q.type.name !== queryType), createQuery(queryType, 0)]);
      return;
    }

    // 入力チェック
    const value = parseFloat2(queryValue);
    if (value === null) {
      window.alert('エラー：その条件では追加できません。');
      return;
    }

    // 入力
    if (MilliMeterToMeterQueryTypeList.includes(queryType)) {
      // 単位変換を伴う場合
      const temp = new Decimal(queryValue);
      const temp2 = temp.mul(new Decimal(1000));
      const value2 = temp2.toNumber();
      setQueryList([...queryList.filter(q => q.type.name !== queryType), createQuery(queryType, value2)]);
      return;
    }
    // 単位変換を伴わない場合
    setQueryList([...queryList.filter(q => q.type.name !== queryType), createQuery(queryType, value)]);
  };

  // クエリを削除する
  const deleteQuery = (queryType: string) => {
    setQueryList(queryList.filter(q => q.type.name !== queryType));
  };

  // 検索URLをクリップボードにコピー
  const copyUrl = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText("https://mft-db-tool.web.app/" + queryParameter);
    }
  };

  return (<Container>
    <Row className="my-3">
      <Col>
        <h1 className="text-center d-none d-sm-block">レンズデータベース</h1>
        <h2 className="text-center d-block d-sm-none">レンズデータベース</h2>
      </Col>
    </Row>
    <Row className="my-3">
      <Col>
        <a href="https://github.com/YSRKEN/MFT-DB-Tool">GitHub</a>
        <span>　</span>
        <a href="https://twitter.com/YSRKEN">作者のTwitter</a>
        <span>　</span>
        <span>最終更新日：2021/12/30</span>
        <span>　</span>
        <TwitterShareButton url={"https://mft-db-tool.web.app/"} title={"レンズデータベース(マイクロフォーサーズ, ライカL マウント向け。スマホ対応！)"}>
          <TwitterIcon size={32} round />
        </TwitterShareButton>
      </Col>
    </Row>
    <Row className="my-3">
      <Col>
        <details>
          <summary>このWebアプリの使用方法</summary>
          <p>
            ・検索条件を「追加」すると、検索条件を表すボタンが追加され、その下のレンズ一覧がフィルタリングされます。<br />
            ・検索条件を表すボタンをクリックすると、その検索条件が削除されます。<br />
            ・検索条件を表すボタンは、同種の検索条件追加操作で上書きされます。<br />
            (例：フィルター径を52mm→62mmに変更する)<br />
            ・レンズ一覧において「詳細」ボタンを押すと、そのレンズの詳細情報が表示されます。<br />
            ・検索条件を含めたURLをシェアしたり、クリップボードにコピーしたりできます。<br />
            ・当WebアプリはPWA技術に対応しています。スマホで見ている場合、Webページを「ホーム画面に追加」することができます。<br />
            (ホーム画面に追加すると、ホーム画面のアイコンをタップするだけで起動できる)
          </p>
        </details>
      </Col>
    </Row>
    <Row className="mt-3">
      <Col>
        <Form>
          <TwitterShareButton url={"https://mft-db-tool.web.app/" + queryParameter} title={"検索条件をシェア"}>
            <Button>検索条件をシェア</Button>
          </TwitterShareButton>
          <Button className="ml-3" onClick={copyUrl}>検索URLをコピー</Button>
        </Form>
      </Col>
    </Row>
    <Row className="mt-3">
      <Col>
        <AddQueryForm queryType={queryType} setQueryType={setQueryType}
          queryValue={queryValue} setQueryValue={setQueryValue}
          addQuery={addQuery} />
      </Col>
    </Row>
    {queryList.length > 0
      ? <Row className="my-0">
        <Col>
          {queryList.map(query =>
            <QueryButton key={query.type.name} query={query} deleteQuery={() => deleteQuery(query.type.name)} />
          )}
        </Col>
      </Row>
      : <></>}
    <Row className="my-3">
      <Col>
        <LensTable lensList={lensList2} />
      </Col>
    </Row>
  </Container>);
}

export default App;
