import{j as r}from"./index-Cik4dQ-V.js";import"./helperFunctions-Cu3UKTnB.js";import"./index-DNvchQ_C.js";import"./svelte/svelte.js";const e="rgbdEncodePixelShader",t=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=toRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV).rgb);}`;r.ShadersStoreWGSL[e]||(r.ShadersStoreWGSL[e]=t);const p={name:e,shader:t};export{p as rgbdEncodePixelShaderWGSL};
//# sourceMappingURL=rgbdEncode.fragment-mSGqlXpI.js.map
