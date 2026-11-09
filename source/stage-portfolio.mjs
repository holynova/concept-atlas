import {cp,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const source=fileURLToPath(new URL('../dist/',import.meta.url));
const target=fileURLToPath(new URL('../../holynova.github.io/concept-atlas/',import.meta.url));
await mkdir(target,{recursive:true});await cp(source,target,{recursive:true});
console.log(`Staged ${target}. Commit and push the portfolio master branch before npm run deploy.`);
