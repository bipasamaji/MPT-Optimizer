import React from 'react'
import { Container, Row, Col } from 'react-bootstrap'
import StockSelector from './components/StockSelector'
import Optimizer from './components/Optimizer'
import SavedPortfolios from './components/SavedPortfolios'
import './styles.css'

export default function App(){
  const [symbols, setSymbols] = React.useState('AAPL,MSFT,GOOGL')

  return (
    <Container className="py-4">
      <Row>
        <Col>
          <h1 className="mb-3">MPT Optimizer</h1>
          <p className="lead">Select tickers and run the optimizer to compute minimum-variance portfolios and the efficient frontier.</p>
        </Col>
      </Row>
      <Row>
        <Col md={4}>
          <StockSelector onSymbolsChange={setSymbols} />
          <SavedPortfolios />
        </Col>
        <Col md={8}>
          <Optimizer initialSymbols={symbols} />
        </Col>
      </Row>
    </Container>
  )
}
