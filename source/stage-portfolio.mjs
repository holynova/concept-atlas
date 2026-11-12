import {cp,mkdir,readdir,readFile,rm} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const source=fileURLToPath(new URL('../dist/',import.meta.url));
const target=fileURLToPath(new URL('../../holynova.github.io/concept-atlas/',import.meta.url));
const projectRoot=fileURLToPath(new URL('../',import.meta.url));
await mkdir(target,{recursive:true});
await cp(source,target,{recursive:true});

const config=JSON.parse(await readFile(`${projectRoot}/source/publication.json`,'utf8'));
const archived=new Set(config.unpublishedIds.map(Number));
let removed=0;
for(const name of await readdir(`${projectRoot}/source`)){
  if(!/^manifest-.*\.json$/.test(name))continue;
  const rows=JSON.parse(await readFile(`${projectRoot}/source/${name}`,'utf8'));
  for(const row of rows){
    if(!archived.has(Number(row.id)))continue;
    const poster=row.image.split('/').pop();
    const base=poster.replace(/\.png$/i,'');
    for(const path of [
      `${target}/${row.image}`,
      `${target}/assets/thumbs/${base}.webp`,
      `${target}/assets/detail/${base}.webp`,
    ]){
      await rm(path,{force:true});
      removed++;
    }
  }
}
console.log(`Staged ${target}; removed ${removed} unpublished asset paths. Commit and push the portfolio master branch before npm run deploy.`);
