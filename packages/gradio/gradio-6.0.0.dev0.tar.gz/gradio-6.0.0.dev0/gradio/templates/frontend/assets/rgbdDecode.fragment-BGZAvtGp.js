import{j as r}from"./index-Cik4dQ-V.js";import"./helperFunctions-DB_WTpPU.js";import"./index-DNvchQ_C.js";import"./svelte/svelte.js";const e="rgbdDecodePixelShader",o=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;r.ShadersStore[e]||(r.ShadersStore[e]=o);const m={name:e,shader:o};export{m as rgbdDecodePixelShader};
//# sourceMappingURL=rgbdDecode.fragment-BGZAvtGp.js.map
