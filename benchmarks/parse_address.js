// Reads JSON list of address strings on stdin, prints parse-address output for each.
const p = require(process.argv[2] + '/node_modules/parse-address');
const inputs = JSON.parse(require('fs').readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(inputs.map(a => p.parseLocation(a) || {})));
