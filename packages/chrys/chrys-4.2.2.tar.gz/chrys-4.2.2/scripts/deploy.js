import ghpages from 'gh-pages';
import path from 'path';

ghpages.publish(path.join(__dirname, '../demo'));
