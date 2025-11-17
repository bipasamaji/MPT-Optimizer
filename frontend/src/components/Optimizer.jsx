import React, {useState, useEffect} from 'react'
import axios from 'axios'

export default function Optimizer({initialSymbols}){
  const [symbols, setSymbols] = useState(initialSymbols || 'AAPL,MSFT,GOOGL')
  const [start, setStart] = useState('2024-01-01')
  const [end, setEnd] = useState('')
  const [target, setTarget] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(()=>{
    if(initialSymbols) setSymbols(initialSymbols)
  },[initialSymbols])

  const run = async ({save=false} = {})=>{
    setLoading(true)
    setMessage(null)
    try{
      const payload = {symbols, start: start || undefined, end: end || undefined, target: target ? parseFloat(target) : undefined}
      const r = await axios.post('/api/optimize/', payload)
      setResult(r.data)
      setMessage('Optimization completed')
    }catch(err){
      const detail = err?.response?.data?.detail || err?.message || 'Error'
      setMessage(`Error: ${detail}`)
    }finally{setLoading(false)}
  }

  const fetchPrices = async ()=>{
    if(!symbols) return setMessage('No symbols to fetch')
    setLoading(true); setMessage(null)
    try{
      await axios.post('/api/fetch-prices/', {symbols, start, end})
      setMessage('Prices fetched')
    }catch(err){
      setMessage('Fetch failed')
    }finally{setLoading(false)}
  }

  const demo = async ()=>{
    // demo workflow: add common symbols, fetch prices, run optimizer
    const demoSymbols = 'AAPL,MSFT,GOOGL'
    setSymbols(demoSymbols)
    try{
      await axios.post('/api/stocks/', {symbol:'AAPL'})
    }catch(e){}
    try{ await axios.post('/api/stocks/', {symbol:'MSFT'}) }catch(e){}
    try{ await axios.post('/api/stocks/', {symbol:'GOOGL'}) }catch(e){}
    setMessage('Added demo symbols — fetching prices...')
    await fetchPrices()
    setMessage('Running optimizer...')
    await run()
  }

  return (
    <div className="card p-3">
      <h5>Optimizer</h5>
      <div className="mb-2">
        <label className="form-label">Symbols</label>
        <input className="form-control" value={symbols} onChange={e=>setSymbols(e.target.value)} />
      </div>
      <div className="row">
        <div className="col">
          <label className="form-label">Start</label>
          <input className="form-control" value={start} onChange={e=>setStart(e.target.value)} />
        </div>
        <div className="col">
          <label className="form-label">End</label>
          <input className="form-control" value={end} onChange={e=>setEnd(e.target.value)} />
        </div>
      </div>
      <div className="mt-2">
        <label className="form-label">Target annual return (decimal, e.g. 0.12)</label>
        <input className="form-control" value={target} onChange={e=>setTarget(e.target.value)} />
      </div>
      <div className="mt-3 d-flex gap-2">
        <button className="btn btn-secondary" onClick={fetchPrices} disabled={loading}>Fetch Prices</button>
        <button className="btn btn-success" onClick={()=>run()} disabled={loading}>{loading? 'Running...':'Run Optimizer'}</button>
        <button className="btn btn-outline-primary" onClick={demo} disabled={loading}>Demo</button>
      </div>

      {message && <div className="mt-3 alert alert-info">{message}</div>}

      {result && (
        <div className="mt-3">
          <h6>Result</h6>
          <div>Expected return: {result.expected_return?.toFixed(4)}</div>
          <table className="table table-sm mt-2">
            <thead><tr><th>Symbol</th><th>Weight</th></tr></thead>
            <tbody>
              {result.symbols.map((s,i)=> (
                <tr key={s}><td>{s}</td><td>{(result.weights[i]*100).toFixed(2)}%</td></tr>
              ))}
            </tbody>
          </table>
          {result.frontier_plot && (
            <div className="mt-2">
              <h6>Efficient Frontier</h6>
              <img src={`/media/${result.frontier_plot}`} alt="frontier" style={{maxWidth:'100%'}} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
