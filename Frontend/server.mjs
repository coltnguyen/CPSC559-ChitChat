import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = 3000;

app.use(express.static(path.join(__dirname, 'public'), { index: 'landingPage.html' }));

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
