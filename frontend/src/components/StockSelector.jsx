import React, {useState, useEffect} from 'react'
import axios from 'axios'

export default function StockSelector({onSymbolsChange}){
  const [stocks, setStocks] = useState([])
  const [symbols, setSymbols] = useState('AAPL,MSFT,GOOGL')
  const [loading, setLoading] = useState(false)

  const loadStocks = async ()=>{
    try{
      const r = await axios.get('/api/stocks/')
      setStocks(r.data)
    }catch(e){
      setStocks([])
    }
  }

  useEffect(()=>{ loadStocks() },[])

  useEffect(()=>{
    if(onSymbolsChange) onSymbolsChange(symbols)
  },[symbols])

  const addStock = async ()=>{
    const s = prompt('Enter symbol (e.g. AAPL)')
    if(!s) return
    try{
      setLoading(true)
      await axios.post('/api/stocks/', {symbol: s.toUpperCase()})
      await loadStocks()
      setSymbols(prev => prev ? `${prev},${s.toUpperCase()}` : s.toUpperCase())
    }catch(err){
      alert('Failed to add symbol')
    }finally{setLoading(false)}
  }

  return (
    <div className="card p-3">
      <h5>Stocks</h5>
      <div style={{maxHeight:260, overflow:'auto'}} className="mb-2">
        {stocks.length===0 && <div className="text-muted">No symbols yet. Click Add Symbol.</div>}
        {stocks.map(s=> (
          <div key={s.symbol} className="d-flex justify-content-between align-items-center py-1">
            <div><strong>{s.symbol}</strong> <small className="text-muted">{s.name}</small></div>
          </div>
        ))}
      </div>
      <hr/>
      <div>
        <label className="form-label">Symbols (comma separated)</label>
        <input className="form-control" value={symbols} onChange={e=>setSymbols(e.target.value)} />
      </div>
      <div className="d-flex gap-2 mt-2">
        <button className="btn btn-primary" onClick={addStock} disabled={loading}>{loading? 'Adding...':'Add Symbol'}</button>
      </div>
    </div>
  )
}
