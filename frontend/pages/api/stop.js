import fetch from 'node-fetch';

export default async function handler(req, res) {
  const response = await fetch("http://127.0.0.1:4280/stop/" + req.query.stop_id);
  res.setHeader("Cache-Control", response.headers.cache_control || "max-age=300, s-maxage=180, public, stale-while-revalidate=30");
  let data = await response.json();
  if(!Object.keys(data).length) {
    res.status(404).json({error: "Stop not found"});
    return;
  }
  res.status(response.status).json(data);
}
