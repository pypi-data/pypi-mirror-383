import { c as create_ssr_component, b as createEventDispatcher, v as validate_component } from './ssr-C3HYbsxA.js';
import { c as Et, f as ie, U as Ue, M as Mt, j as O, $ as $t, G as Ge, k as _, _ as _t } from './2-B-4RU9Ii.js';
import { Z as Zt } from './AudioPlayer-DFObwDbA.js';
import './index-ClteBeTX.js';
import './Component-NmRBwSfF.js';
import 'path';
import 'url';
import 'fs';
import './hls-DpKhbIaL.js';

const j=create_ssr_component((l,e,o,M)=>{let{value:t=null}=e,{subtitles:i=null}=e,{label:d}=e,{show_label:n=!0}=e,{buttons:r=null}=e,{i18n:u}=e,{waveform_settings:_$1={}}=e,{waveform_options:c={show_recording_waveform:!0}}=e,{editable:f=!0}=e,{loop:v}=e,{display_icon_button_wrapper_top_corner:m=!1}=e;const y=createEventDispatcher();return e.value===void 0&&o.value&&t!==void 0&&o.value(t),e.subtitles===void 0&&o.subtitles&&i!==void 0&&o.subtitles(i),e.label===void 0&&o.label&&d!==void 0&&o.label(d),e.show_label===void 0&&o.show_label&&n!==void 0&&o.show_label(n),e.buttons===void 0&&o.buttons&&r!==void 0&&o.buttons(r),e.i18n===void 0&&o.i18n&&u!==void 0&&o.i18n(u),e.waveform_settings===void 0&&o.waveform_settings&&_$1!==void 0&&o.waveform_settings(_$1),e.waveform_options===void 0&&o.waveform_options&&c!==void 0&&o.waveform_options(c),e.editable===void 0&&o.editable&&f!==void 0&&o.editable(f),e.loop===void 0&&o.loop&&v!==void 0&&o.loop(v),e.display_icon_button_wrapper_top_corner===void 0&&o.display_icon_button_wrapper_top_corner&&m!==void 0&&o.display_icon_button_wrapper_top_corner(m),t&&y("change",t),`${validate_component(Et,"BlockLabel").$$render(l,{show_label:n,Icon:ie,float:!1,label:d||u("audio.audio")},{},{})} ${t!==null?`${validate_component(Ue,"IconButtonWrapper").$$render(l,{display_top_corner:m},{},{default:()=>`${r===null||r.includes("download")?`${validate_component(Mt,"DownloadLink").$$render(l,{href:t.is_stream?t.url?.replace("playlist.m3u8","playlist-file"):t.url,download:t.orig_name||t.path},{},{default:()=>`${validate_component(O,"IconButton").$$render(l,{Icon:$t,label:u("common.download")},{},{})}`})}`:""} ${r===null||r.includes("share")?`${validate_component(Ge,"ShareButton").$$render(l,{i18n:u,formatter:async w=>w?`<audio controls src="${await _(w.url)}"></audio>`:"",value:t},{},{})}`:""}`})} ${validate_component(Zt,"AudioPlayer").$$render(l,{value:t,subtitles:Array.isArray(i)?i:i?.url,label:d,i18n:u,waveform_settings:_$1,waveform_options:c,editable:f,loop:v},{},{})}`:`${validate_component(_t,"Empty").$$render(l,{size:"small"},{},{default:()=>`${validate_component(ie,"Music").$$render(l,{},{},{})}`})}`}`});

export { j as default };
//# sourceMappingURL=StaticAudio-BPuxvuzf.js.map
