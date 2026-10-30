from pathlib import Path
import base64
root=Path(__file__).parent
html=(root/'sim/template.html').read_text()
engine=(root/'sim/engine.mjs').read_text().replace('export const ','const ').replace('export function ','function ').replace('export async function ','async function ').replace('export class ','class ')
html=html.replace('/*__ENGINE__*/',engine).replace('__WASM64__',base64.b64encode((root/'sim/controller.wasm').read_bytes()).decode('ascii'))
(root/'mini_waymo_micro_v9_demo.html').write_text(html)
print('Generated standalone HTML:',len(html),'bytes')
