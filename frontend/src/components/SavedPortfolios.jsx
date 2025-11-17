import React, {useEffect, useState} from 'react'
import axios from 'axios'

export default function SavedPortfolios(){
  const [list, setList] = useState([])

  const load = async ()=>{
    try{
      const r = await axios.get('/api/portfolios/')
      setList(r.data)
    }catch(e){ setList([]) }
  }

  useEffect(()=>{ load() },[])

  return (
    <div className="card p-3 mt-3">
      <h5>Saved Portfolios</h5>
      {list.length===0 && <div className="text-muted">No saved portfolios yet.</div>}
      {list.map(p=> (
        <div key={p.id} className="mb-2">
          <div><strong>{p.name}</strong> <small className="text-muted">target: {p.target_return ?? 'N/A'}</small></div>
          <table className="table table-sm mt-1">
            <thead><tr><th>Symbol</th><th>Weight</th></tr></thead>
            <tbody>
              {p.weights.map(w=> (
                <tr key={w.stock}><td>{w.stock}</td><td>{(w.weight*100).toFixed(2)}%</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  )
}
