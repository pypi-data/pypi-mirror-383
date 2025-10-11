const ELK = require('elkjs');
var graph = require('./elk_source.json');

const elk = new ELK();
const fs = require('fs');
var layout = elk.layout(graph)
    .then(x=>{
        var json_var = JSON.stringify(x, null, 2);
        fs.writeFileSync('./elktarget.json', json_var);
        console.log(json_var);
    })
    .catch(console.error)