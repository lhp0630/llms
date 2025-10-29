import * as express from 'express';

const app = express();

app.get('/', (req: express.Request, res: express.Response) => {
  res.send('Hello, World!');
});

app.listen(3000, () => console.log('Now listening on: http://localhost:3000.'));