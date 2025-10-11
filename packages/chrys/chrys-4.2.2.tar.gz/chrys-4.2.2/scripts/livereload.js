const _ = require('lodash');
const chokidar = require('chokidar');
const connect = require('connect');
const livereload = require('livereload');
const open = require('open');
const os = require('os');
const path = require('path');
const serveStatic = require('serve-static');
const {config} = require('../config');
const {buildDemo} = require('./build');

const webserver = connect();
webserver.use(serveStatic(path.join(__dirname, '..', config.webserver.path)));
webserver.listen(config.webserver.port);

const livereloadServer = livereload.createServer();

const browser = _.get(
  config.webserver.browsers,
  os.platform(),
  config.webserver.browsers.default
);

const livereloadOpen =
  (config.webserver.https ? 'https' : 'http') +
  '://' +
  config.webserver.host +
  ':' +
  config.webserver.port +
  (config.webserver.open ? config.webserver.open : '/');

buildDemo().then(async () => {
  await open(livereloadOpen, {app: browser});

  chokidar.watch([path.join(__dirname, '../src/demo')]).on('change', () => {
    buildDemo().then(() => {
      livereloadServer.refresh(path.join(__dirname, '../demo'));
    });
  });
});
