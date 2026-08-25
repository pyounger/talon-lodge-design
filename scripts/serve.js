// Serve the prototypes over http://localhost so they behave like a real page.
//
// Opening a prototype by double-clicking it gives a file:// page, and Chrome/Edge
// deny the IndexedDB API on file:// origins — which is where the shared
// `talon-images` photo store lives. Everything still renders, but photos can't be
// saved. Serving over http fixes that, and matches how the real app will run.
//
//   node talon-lodge-design/scripts/serve.js          → http://localhost:8080
//   node talon-lodge-design/scripts/serve.js 3000     → pick a port
//
// Ctrl+C to stop. Static files only, bound to localhost — nothing is exposed to
// the network.
const http = require('http');
const fs = require('fs');
const path = require('path');

const DIR = path.resolve(__dirname, '..');          // talon-lodge-design/
const PORT = Number(process.argv[2]) || 8080;

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',  '.json': 'application/json; charset=utf-8',
  '.md': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.webp': 'image/webp', '.ico': 'image/x-icon',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.otf': 'font/otf'
};

const server = http.createServer((req, res) => {
  let rel;
  try { rel = decodeURIComponent(req.url.split('?')[0]); } catch (_) { rel = '/'; }
  if (rel === '/') rel = '/test-hub.html';

  // resolve inside DIR only — no ../ escapes
  const full = path.resolve(DIR, '.' + rel);
  if (full !== DIR && !full.startsWith(DIR + path.sep)) {
    res.writeHead(403, {'Content-Type': 'text/plain'});
    return res.end('Forbidden');
  }

  fs.stat(full, (err, st) => {
    if (err || !st.isFile()) {
      res.writeHead(404, {'Content-Type': 'text/html; charset=utf-8'});
      return res.end('<h1>404</h1><p>Not found. <a href="/">Back to the test hub</a></p>');
    }
    res.writeHead(200, {
      'Content-Type': TYPES[path.extname(full).toLowerCase()] || 'application/octet-stream',
      'Content-Length': st.size,
      'Cache-Control': 'no-cache'
    });
    fs.createReadStream(full).pipe(res);
  });
});

server.on('error', e => {
  if (e.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Try:  node scripts/serve.js ${PORT + 1}`);
    process.exit(1);
  }
  throw e;
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`\n  Talon prototypes → http://localhost:${PORT}/\n`);
  console.log(`  Test hub      http://localhost:${PORT}/`);
  console.log(`  Island Ops    http://localhost:${PORT}/island-ops.html\n`);
  console.log('  Ctrl+C to stop.\n');
});
