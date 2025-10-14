import { c as create_ssr_component, v as validate_component } from './ssr-C3HYbsxA.js';
import { P } from './JSON-SC1waj3E.js';
import { I as It, c as Et, as as re, E as Et$1 } from './2-B-4RU9Ii.js';
import './index-ClteBeTX.js';
import './Component-NmRBwSfF.js';
import 'path';
import 'url';
import 'fs';

const G=create_ssr_component((o,e,l,A)=>{let{elem_id:d=""}=e,{elem_classes:m=[]}=e,{visible:c=!0}=e,{value:t}=e,N,{loading_status:f}=e,{label:i}=e,{show_label:u}=e,{container:v=!0}=e,{scale:w=null}=e,{min_width:S=void 0}=e,{gradio:a}=e,{open:x=!1}=e,{theme_mode:B}=e,{show_indices:J}=e,{height:k}=e,{min_height:O}=e,{max_height:r}=e,{buttons:h=null}=e,j=0;return e.elem_id===void 0&&l.elem_id&&d!==void 0&&l.elem_id(d),e.elem_classes===void 0&&l.elem_classes&&m!==void 0&&l.elem_classes(m),e.visible===void 0&&l.visible&&c!==void 0&&l.visible(c),e.value===void 0&&l.value&&t!==void 0&&l.value(t),e.loading_status===void 0&&l.loading_status&&f!==void 0&&l.loading_status(f),e.label===void 0&&l.label&&i!==void 0&&l.label(i),e.show_label===void 0&&l.show_label&&u!==void 0&&l.show_label(u),e.container===void 0&&l.container&&v!==void 0&&l.container(v),e.scale===void 0&&l.scale&&w!==void 0&&l.scale(w),e.min_width===void 0&&l.min_width&&S!==void 0&&l.min_width(S),e.gradio===void 0&&l.gradio&&a!==void 0&&l.gradio(a),e.open===void 0&&l.open&&x!==void 0&&l.open(x),e.theme_mode===void 0&&l.theme_mode&&B!==void 0&&l.theme_mode(B),e.show_indices===void 0&&l.show_indices&&J!==void 0&&l.show_indices(J),e.height===void 0&&l.height&&k!==void 0&&l.height(k),e.min_height===void 0&&l.min_height&&O!==void 0&&l.min_height(O),e.max_height===void 0&&l.max_height&&r!==void 0&&l.max_height(r),e.buttons===void 0&&l.buttons&&h!==void 0&&l.buttons(h),t!==N&&(N=t,a.dispatch("change")),`${validate_component(It,"Block").$$render(o,{visible:c,test_id:"json",elem_id:d,elem_classes:m,container:v,scale:w,min_width:S,padding:!1,allow_overflow:!0,overflow_behavior:"auto",height:k,min_height:O,max_height:r},{},{default:()=>`<div>${i?`${validate_component(Et,"BlockLabel").$$render(o,{Icon:re,show_label:u,label:i,float:!1,disable:v===!1},{},{})}`:""}</div> ${validate_component(Et$1,"StatusTracker").$$render(o,Object.assign({},{autoscroll:a.autoscroll},{i18n:a.i18n},f),{},{})} ${validate_component(P,"JSON").$$render(o,{value:t,open:x,theme_mode:B,show_indices:J,label_height:j,show_copy_button:h===null?!0:h.includes("copy")},{},{})}`})}`});

export { P as BaseJSON, G as default };
//# sourceMappingURL=Index11-DjqHzvnm.js.map
