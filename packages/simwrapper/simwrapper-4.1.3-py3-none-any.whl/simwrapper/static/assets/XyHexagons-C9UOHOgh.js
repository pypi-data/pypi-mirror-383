import{d as R,m as K,g as b,n as H,S as v,V as _,C as Q}from"./index-CHe7BiNX.js";import{d as J}from"./index-CVL_6l40.js";import{Y as tt}from"./index-DFKcNkqO.js";import{H as et}from"./HTTPFileSystem-Cf8G_bcW.js";import{C as it}from"./CollapsiblePanel-GuobHpcZ.js";import{D as st}from"./DrawingTool-CaOc8yNx.js";import{Z as nt}from"./ZoomButtons-B7tt6RkT.js";import{c as ot}from"./index-B0QPu2l3.js";import{M as at}from"./mapbox-overlay-BWTNBTi1.js";import{A as rt}from"./arc-layer-BVLaP1vr.js";import{C as lt}from"./text-layer-Cpq7KRgR.js";import{Q as M,B as ut,X as ct,q as B,Y as ht,x as gt,I as dt,V as mt}from"./layer-GQvgsG1_.js";import{C as ft}from"./column-layer-BEEIazOy.js";import{W as pt}from"./NewXmlFetcher.worker-DSJgeOd2.js";import"./fxp-DjoqftHf.js";import"./geojson-layer-ClBV_VpI.js";import"./path-layer-BllYebBs.js";function bt(s){return new Worker("/assets/CsvGzipParser.worker-CmRyigJZ.js",{name:s?.name})}function vt({pointCount:s,getBinId:t}){const e=new Map;for(let i=0;i<s;i++){const n=t(i);if(n===null)continue;let o=e.get(String(n));o?o.points.push(i):(o={id:n,index:e.size,points:[i]},e.set(String(n),o))}return Array.from(e.values())}function yt({bins:s,dimensions:t,target:e}){const i=s.length*t;(!e||e.length<i)&&(e=new Float32Array(i));for(let n=0;n<s.length;n++){const{id:o}=s[n];Array.isArray(o)?e.set(o,n*t):e[n]=o}return e}const xt=s=>s.length,V=(s,t)=>{let e=0;for(const i of s)e+=t(i);return e},Ct=(s,t)=>s.length===0?NaN:V(s,t)/s.length,St=(s,t)=>{let e=1/0;for(const i of s){const n=t(i);n<e&&(e=n)}return e},wt=(s,t)=>{let e=-1/0;for(const i of s){const n=t(i);n>e&&(e=n)}return e},Mt={COUNT:xt,SUM:V,MEAN:Ct,MIN:St,MAX:wt};function At({bins:s,getValue:t,operation:e,target:i}){(!i||i.length<s.length)&&(i=new Float32Array(s.length));let n=1/0,o=-1/0;for(let a=0;a<s.length;a++){const{points:r}=s[a];i[a]=e(r,t),i[a]<n&&(n=i[a]),i[a]>o&&(o=i[a])}return{value:i,domain:[n,o]}}function D(s,t,e){const i={};for(const o of s.sources||[]){const a=t[o];if(a)i[o]=It(a);else throw new Error(`Cannot find attribute ${o}`)}const n={};return o=>{for(const a in i)n[a]=i[a](o);return s.getValue(n,o,e)}}function It(s){const t=s.value,{offset:e=0,stride:i,size:n}=s.getAccessor(),o=t.BYTES_PER_ELEMENT,a=e/o,r=i?i/o:n;if(n===1)return s.isConstant?()=>t[0]:c=>{const u=a+r*c;return t[u]};let l;return s.isConstant?(l=Array.from(t),()=>l):(l=new Array(n),c=>{const u=a+r*c;for(let h=0;h<n;h++)l[h]=t[u+h];return l})}class _t{constructor(t){this.bins=[],this.binIds=null,this.results=[],this.dimensions=t.dimensions,this.channelCount=t.getValue.length,this.props={...t,binOptions:{},pointCount:0,operations:[],customOperations:[],attributes:{}},this.needsUpdate=!0,this.setProps(t)}destroy(){}get binCount(){return this.bins.length}setProps(t){const e=this.props;if(t.binOptions&&(M(t.binOptions,e.binOptions,2)||this.setNeedsUpdate()),t.operations)for(let i=0;i<this.channelCount;i++)t.operations[i]!==e.operations[i]&&this.setNeedsUpdate(i);if(t.customOperations)for(let i=0;i<this.channelCount;i++)!!t.customOperations[i]!=!!e.customOperations[i]&&this.setNeedsUpdate(i);t.pointCount!==void 0&&t.pointCount!==e.pointCount&&this.setNeedsUpdate(),t.attributes&&(t.attributes={...e.attributes,...t.attributes}),Object.assign(this.props,t)}setNeedsUpdate(t){t===void 0?this.needsUpdate=!0:this.needsUpdate!==!0&&(this.needsUpdate=this.needsUpdate||[],this.needsUpdate[t]=!0)}update(){if(this.needsUpdate===!0){this.bins=vt({pointCount:this.props.pointCount,getBinId:D(this.props.getBin,this.props.attributes,this.props.binOptions)});const t=yt({bins:this.bins,dimensions:this.dimensions,target:this.binIds?.value});this.binIds={value:t,type:"float32",size:this.dimensions}}for(let t=0;t<this.channelCount;t++)if(this.needsUpdate===!0||this.needsUpdate[t]){const e=this.props.customOperations[t]||Mt[this.props.operations[t]],{value:i,domain:n}=At({bins:this.bins,getValue:D(this.props.getValue[t],this.props.attributes,void 0),operation:e,target:this.results[t]?.value});this.results[t]={value:i,domain:n,type:"float32",size:1},this.props.onUpdate?.({channel:t})}this.needsUpdate=!1}preDraw(){}getBins(){return this.binIds}getResult(t){return this.results[t]}getResultDomain(t){return this.results[t]?.domain??[1/0,-1/0]}getBin(t){const e=this.bins[t];if(!e)return null;const i=new Array(this.channelCount);for(let n=0;n<i.length;n++){const o=this.results[n];i[n]=o?.value[t]}return{id:e.id,value:i,count:e.points.length,pointIndices:e.points}}}function E(s,t,e){return s.createFramebuffer({width:t,height:e,colorAttachments:[s.createTexture({width:t,height:e,format:"rgba32float",mipmaps:!1,sampler:{minFilter:"nearest",magFilter:"nearest"}})]})}const Dt=`uniform binSorterUniforms {
  ivec4 binIdRange;
  ivec2 targetSize;
} binSorter;
`,Tt={name:"binSorter",vs:Dt,uniformTypes:{binIdRange:"vec4<i32>",targetSize:"vec2<i32>"}},k=[1,2,4,8],T=3e38,Pt={SUM:0,MEAN:0,MIN:0,MAX:0,COUNT:0},y=1024;class Ot{constructor(t,e){this.binsFBO=null,this.device=t,this.model=zt(t,e)}get texture(){return this.binsFBO?this.binsFBO.colorAttachments[0].texture:null}destroy(){this.model.destroy(),this.binsFBO?.colorAttachments[0].texture.destroy(),this.binsFBO?.destroy()}getBinValues(t){if(!this.binsFBO)return null;const e=t%y,i=Math.floor(t/y),n=this.device.readPixelsToArrayWebGL(this.binsFBO,{sourceX:e,sourceY:i,sourceWidth:1,sourceHeight:1}).buffer;return new Float32Array(n)}setDimensions(t,e){const i=y,n=Math.ceil(t/i);this.binsFBO?this.binsFBO.height<n&&this.binsFBO.resize({width:i,height:n}):this.binsFBO=E(this.device,i,n);const o={binIdRange:[e[0][0],e[0][1],e[1]?.[0]||0,e[1]?.[1]||0],targetSize:[this.binsFBO.width,this.binsFBO.height]};this.model.shaderInputs.setProps({binSorter:o})}setModelProps(t){const e=this.model;t.attributes&&e.setAttributes(t.attributes),t.constantAttributes&&e.setConstantAttributes(t.constantAttributes),t.vertexCount!==void 0&&e.setVertexCount(t.vertexCount),t.shaderModuleProps&&e.shaderInputs.setProps(t.shaderModuleProps)}update(t){if(!this.binsFBO)return;const e=Nt(t);this._updateBins("SUM",e.SUM+e.MEAN),this._updateBins("MIN",e.MIN),this._updateBins("MAX",e.MAX)}_updateBins(t,e){if(e===0)return;e|=k[3];const i=this.model,n=this.binsFBO,o=t==="MAX"?-T:t==="MIN"?T:0,a=this.device.beginRenderPass({id:`gpu-aggregation-${t}`,framebuffer:n,parameters:{viewport:[0,0,n.width,n.height],colorMask:e},clearColor:[o,o,o,0],clearDepth:!1,clearStencil:!1});i.setParameters({blend:!0,blendColorSrcFactor:"one",blendColorDstFactor:"one",blendAlphaSrcFactor:"one",blendAlphaDstFactor:"one",blendColorOperation:t==="MAX"?"max":t==="MIN"?"min":"add",blendAlphaOperation:"add"}),i.draw(a),a.end()}}function Nt(s){const t={...Pt};for(let e=0;e<s.length;e++){const i=s[e];i&&(t[i]+=k[e])}return t}function zt(s,t){let e=t.vs;t.dimensions===2&&(e+=`
void getBin(out int binId) {
  ivec2 binId2;
  getBin(binId2);
  if (binId2.x < binSorter.binIdRange.x || binId2.x >= binSorter.binIdRange.y) {
    binId = -1;
  } else {
    binId = (binId2.y - binSorter.binIdRange.z) * (binSorter.binIdRange.y - binSorter.binIdRange.x) + binId2.x;
  }
}
`);const i=`#version 300 es
#define SHADER_NAME gpu-aggregation-sort-bins-vertex

${e}

out vec3 v_Value;

void main() {
  int binIndex;
  getBin(binIndex);
  binIndex = binIndex - binSorter.binIdRange.x;
  if (binIndex < 0) {
    gl_Position = vec4(0.);
    return;
  }
  int row = binIndex / binSorter.targetSize.x;
  int col = binIndex - row * binSorter.targetSize.x;
  vec2 position = (vec2(col, row) + 0.5) / vec2(binSorter.targetSize) * 2.0 - 1.0;
  gl_Position = vec4(position, 0.0, 1.0);
  gl_PointSize = 1.0;

#if NUM_CHANNELS == 3
  getValue(v_Value);
#elif NUM_CHANNELS == 2
  getValue(v_Value.xy);
#else
  getValue(v_Value.x);
#endif
}
`,n=`#version 300 es
#define SHADER_NAME gpu-aggregation-sort-bins-fragment

precision highp float;

in vec3 v_Value;
out vec4 fragColor;

void main() {
  fragColor.xyz = v_Value;

  #ifdef MODULE_GEOMETRY
  geometry.uv = vec2(0.);
  DECKGL_FILTER_COLOR(fragColor, geometry);
  #endif

  fragColor.w = 1.0;
}
`;return new ut(s,{bufferLayout:t.bufferLayout,modules:[...t.modules||[],Tt],defines:{...t.defines,NON_INSTANCED_MODEL:1,NUM_CHANNELS:t.channelCount},isInstanced:!1,vs:i,fs:n,topology:"point-list",disableWarnings:!0})}const Lt=`uniform aggregatorTransformUniforms {
  ivec4 binIdRange;
  bvec3 isCount;
  bvec3 isMean;
  float naN;
} aggregatorTransform;
`,Rt={name:"aggregatorTransform",vs:Lt,uniformTypes:{binIdRange:"vec4<i32>",isCount:"vec3<f32>",isMean:"vec3<f32>"}};class Ht{constructor(t,e){this.binBuffer=null,this.valueBuffer=null,this._domains=null,this.device=t,this.channelCount=e.channelCount,this.transform=Bt(t,e),this.domainFBO=E(t,2,1)}destroy(){this.transform.destroy(),this.binBuffer?.destroy(),this.valueBuffer?.destroy(),this.domainFBO.colorAttachments[0].texture.destroy(),this.domainFBO.destroy()}get domains(){if(!this._domains){const t=this.device.readPixelsToArrayWebGL(this.domainFBO).buffer,e=new Float32Array(t);this._domains=[[-e[4],e[0]],[-e[5],e[1]],[-e[6],e[2]]].slice(0,this.channelCount)}return this._domains}setDimensions(t,e){const{model:i,transformFeedback:n}=this.transform;i.setVertexCount(t);const o={binIdRange:[e[0][0],e[0][1],e[1]?.[0]||0,e[1]?.[1]||0]};i.shaderInputs.setProps({aggregatorTransform:o});const a=t*e.length*4;(!this.binBuffer||this.binBuffer.byteLength<a)&&(this.binBuffer?.destroy(),this.binBuffer=this.device.createBuffer({byteLength:a}),n.setBuffer("binIds",this.binBuffer));const r=t*this.channelCount*4;(!this.valueBuffer||this.valueBuffer.byteLength<r)&&(this.valueBuffer?.destroy(),this.valueBuffer=this.device.createBuffer({byteLength:r}),n.setBuffer("values",this.valueBuffer))}update(t,e){if(!t)return;const i=this.transform,n=this.domainFBO,o=[0,1,2].map(l=>e[l]==="COUNT"?1:0),a=[0,1,2].map(l=>e[l]==="MEAN"?1:0),r={isCount:o,isMean:a,bins:t};i.model.shaderInputs.setProps({aggregatorTransform:r}),i.run({id:"gpu-aggregation-domain",framebuffer:n,parameters:{viewport:[0,0,2,1]},clearColor:[-3e38,-3e38,-3e38,0],clearDepth:!1,clearStencil:!1}),this._domains=null}}function Bt(s,t){const e=`#version 300 es
#define SHADER_NAME gpu-aggregation-domain-vertex

uniform sampler2D bins;

#if NUM_DIMS == 1
out float binIds;
#else
out vec2 binIds;
#endif

#if NUM_CHANNELS == 1
flat out float values;
#elif NUM_CHANNELS == 2
flat out vec2 values;
#else
flat out vec3 values;
#endif

const float NAN = intBitsToFloat(-1);

void main() {
  int row = gl_VertexID / SAMPLER_WIDTH;
  int col = gl_VertexID - row * SAMPLER_WIDTH;
  vec4 weights = texelFetch(bins, ivec2(col, row), 0);
  vec3 value3 = mix(
    mix(weights.rgb, vec3(weights.a), aggregatorTransform.isCount),
    weights.rgb / max(weights.a, 1.0),
    aggregatorTransform.isMean
  );
  if (weights.a == 0.0) {
    value3 = vec3(NAN);
  }

#if NUM_DIMS == 1
  binIds = float(gl_VertexID + aggregatorTransform.binIdRange.x);
#else
  int y = gl_VertexID / (aggregatorTransform.binIdRange.y - aggregatorTransform.binIdRange.x);
  int x = gl_VertexID - y * (aggregatorTransform.binIdRange.y - aggregatorTransform.binIdRange.x);
  binIds.y = float(y + aggregatorTransform.binIdRange.z);
  binIds.x = float(x + aggregatorTransform.binIdRange.x);
#endif

#if NUM_CHANNELS == 3
  values = value3;
#elif NUM_CHANNELS == 2
  values = value3.xy;
#else
  values = value3.x;
#endif

  gl_Position = vec4(0., 0., 0., 1.);
  // This model renders into a 2x1 texture to obtain min and max simultaneously.
  // See comments in fragment shader
  gl_PointSize = 2.0;
}
`,i=`#version 300 es
#define SHADER_NAME gpu-aggregation-domain-fragment

precision highp float;

#if NUM_CHANNELS == 1
flat in float values;
#elif NUM_CHANNELS == 2
flat in vec2 values;
#else
flat in vec3 values;
#endif

out vec4 fragColor;

void main() {
  vec3 value3;
#if NUM_CHANNELS == 3
  value3 = values;
#elif NUM_CHANNELS == 2
  value3.xy = values;
#else
  value3.x = values;
#endif
  if (isnan(value3.x)) discard;
  // This shader renders into a 2x1 texture with blending=max
  // The left pixel yields the max value of each channel
  // The right pixel yields the min value of each channel
  if (gl_FragCoord.x < 1.0) {
    fragColor = vec4(value3, 1.0);
  } else {
    fragColor = vec4(-value3, 1.0);
  }
}
`;return new ct(s,{vs:e,fs:i,topology:"point-list",modules:[Rt],parameters:{blend:!0,blendColorSrcFactor:"one",blendColorDstFactor:"one",blendColorOperation:"max",blendAlphaSrcFactor:"one",blendAlphaDstFactor:"one",blendAlphaOperation:"max"},defines:{NUM_DIMS:t.dimensions,NUM_CHANNELS:t.channelCount,SAMPLER_WIDTH:y},varyings:["binIds","values"],disableWarnings:!0})}class P{static isSupported(t){return t.features.has("float32-renderable-webgl")&&t.features.has("texture-blend-float-webgl")}constructor(t,e){this.binCount=0,this.binIds=null,this.results=[],this.device=t,this.dimensions=e.dimensions,this.channelCount=e.channelCount,this.props={...e,pointCount:0,binIdRange:[[0,0]],operations:[],attributes:{},binOptions:{}},this.needsUpdate=new Array(this.channelCount).fill(!0),this.binSorter=new Ot(t,e),this.aggregationTransform=new Ht(t,e),this.setProps(e)}getBins(){const t=this.aggregationTransform.binBuffer;return t?(this.binIds?.buffer!==t&&(this.binIds={buffer:t,type:"float32",size:this.dimensions}),this.binIds):null}getResult(t){const e=this.aggregationTransform.valueBuffer;return!e||t>=this.channelCount?null:(this.results[t]?.buffer!==e&&(this.results[t]={buffer:e,type:"float32",size:1,stride:this.channelCount*4,offset:t*4}),this.results[t])}getResultDomain(t){return this.aggregationTransform.domains[t]}getBin(t){if(t<0||t>=this.binCount)return null;const{binIdRange:e}=this.props;let i;if(this.dimensions===1)i=[t+e[0][0]];else{const[[r,l],[c]]=e,u=l-r;i=[t%u+r,Math.floor(t/u)+c]}const n=this.binSorter.getBinValues(t);if(!n)return null;const o=n[3],a=[];for(let r=0;r<this.channelCount;r++){const l=this.props.operations[r];l==="COUNT"?a[r]=o:o===0?a[r]=NaN:a[r]=l==="MEAN"?n[r]/o:n[r]}return{id:i,value:a,count:o}}destroy(){this.binSorter.destroy(),this.aggregationTransform.destroy()}setProps(t){const e=this.props;if("binIdRange"in t&&!M(t.binIdRange,e.binIdRange,2)){const i=t.binIdRange;if(B.assert(i.length===this.dimensions),this.dimensions===1){const[[n,o]]=i;this.binCount=o-n}else{const[[n,o],[a,r]]=i;this.binCount=(o-n)*(r-a)}this.binSorter.setDimensions(this.binCount,i),this.aggregationTransform.setDimensions(this.binCount,i),this.setNeedsUpdate()}if(t.operations)for(let i=0;i<this.channelCount;i++)t.operations[i]!==e.operations[i]&&this.setNeedsUpdate(i);if(t.pointCount!==void 0&&t.pointCount!==e.pointCount&&(this.binSorter.setModelProps({vertexCount:t.pointCount}),this.setNeedsUpdate()),t.binOptions&&(M(t.binOptions,e.binOptions,2)||this.setNeedsUpdate(),this.binSorter.model.shaderInputs.setProps({binOptions:t.binOptions})),t.attributes){const i={},n={};for(const o of Object.values(t.attributes))for(const[a,r]of Object.entries(o.getValue()))ArrayBuffer.isView(r)?n[a]=r:r&&(i[a]=r);this.binSorter.setModelProps({attributes:i,constantAttributes:n})}t.shaderModuleProps&&this.binSorter.setModelProps({shaderModuleProps:t.shaderModuleProps}),Object.assign(this.props,t)}setNeedsUpdate(t){t===void 0?this.needsUpdate.fill(!0):this.needsUpdate[t]=!0}update(){}preDraw(){if(!this.needsUpdate.some(Boolean))return;const{operations:t}=this.props,e=this.needsUpdate.map((i,n)=>i?t[n]:null);this.binSorter.update(e),this.aggregationTransform.update(this.binSorter.texture,t);for(let i=0;i<this.channelCount;i++)this.needsUpdate[i]&&(this.needsUpdate[i]=!1,this.props.onUpdate?.({channel:i}))}}class F extends lt{get isDrawable(){return!0}initializeState(){this.getAttributeManager().remove(["instancePickingColors"])}updateState(t){super.updateState(t);const e=this.getAggregatorType();if(t.changeFlags.extensionsChanged||this.state.aggregatorType!==e){this.state.aggregator?.destroy();const i=this.createAggregator(e);return i.setProps({attributes:this.getAttributeManager()?.attributes}),this.setState({aggregator:i,aggregatorType:e}),!0}return!1}finalizeState(t){super.finalizeState(t),this.state.aggregator.destroy()}updateAttributes(t){const{aggregator:e}=this.state;e.setProps({attributes:t});for(const i in t)this.onAttributeChange(i);e.update()}draw({shaderModuleProps:t}){const{aggregator:e}=this.state;e.setProps({shaderModuleProps:t}),e.preDraw()}_getAttributeManager(){return new ht(this.context.device,{id:this.props.id,stats:this.context.stats})}}F.layerName="AggregationLayer";const Vt=[[255,255,178],[254,217,118],[254,178,76],[253,141,60],[240,59,32],[189,0,38]];function Et(s,t=!1,e=Float32Array){let i;if(Number.isFinite(s[0]))i=new e(s);else{i=new e(s.length*4);let n=0;for(let o=0;o<s.length;o++){const a=s[o];i[n++]=a[0],i[n++]=a[1],i[n++]=a[2],i[n++]=Number.isFinite(a[3])?a[3]:255}}if(t)for(let n=0;n<i.length;n++)i[n]/=255;return i}const x={linear:"linear",quantile:"nearest",quantize:"nearest",ordinal:"nearest"};function kt(s,t){s.setSampler({minFilter:x[t],magFilter:x[t]})}function Ft(s,t,e="linear"){const i=Et(t,!1,Uint8Array);return s.createTexture({format:"rgba8unorm",mipmaps:!1,sampler:{minFilter:x[e],magFilter:x[e],addressModeU:"clamp-to-edge",addressModeV:"clamp-to-edge"},data:i,width:i.length/4,height:1})}class O{constructor(t,e){this.props={scaleType:"linear",lowerPercentile:0,upperPercentile:100},this.domain=null,this.cutoff=null,this.input=t,this.inputLength=e,this.attribute=t}getScalePercentile(){if(!this._percentile){const t=N(this.input,this.inputLength);this._percentile=jt(t)}return this._percentile}getScaleOrdinal(){if(!this._ordinal){const t=N(this.input,this.inputLength);this._ordinal=Ut(t)}return this._ordinal}getCutoff({scaleType:t,lowerPercentile:e,upperPercentile:i}){if(t==="quantile")return[e,i-1];if(e>0||i<100){const{domain:n}=this.getScalePercentile();let o=n[Math.floor(e)-1]??-1/0,a=n[Math.floor(i)-1]??1/0;if(t==="ordinal"){const{domain:r}=this.getScaleOrdinal();o=r.findIndex(l=>l>=o),a=r.findIndex(l=>l>a)-1,a===-2&&(a=r.length-1)}return[o,a]}return null}update(t){const e=this.props;if(t.scaleType!==e.scaleType)switch(t.scaleType){case"quantile":{const{attribute:i}=this.getScalePercentile();this.attribute=i,this.domain=[0,99];break}case"ordinal":{const{attribute:i,domain:n}=this.getScaleOrdinal();this.attribute=i,this.domain=[0,n.length-1];break}default:this.attribute=this.input,this.domain=null}return(t.scaleType!==e.scaleType||t.lowerPercentile!==e.lowerPercentile||t.upperPercentile!==e.upperPercentile)&&(this.cutoff=this.getCutoff(t)),this.props=t,this}}function Ut(s){const t=new Set;for(const n of s)Number.isFinite(n)&&t.add(n);const e=Array.from(t).sort(),i=new Map;for(let n=0;n<e.length;n++)i.set(e[n],n);return{attribute:{value:s.map(n=>Number.isFinite(n)?i.get(n):NaN),type:"float32",size:1},domain:e}}function jt(s,t=100){const e=Array.from(s).filter(Number.isFinite).sort($t);let i=0;const n=Math.max(1,t),o=new Array(n-1);for(;++i<n;)o[i-1]=Wt(e,i/n);return{attribute:{value:s.map(a=>Number.isFinite(a)?qt(o,a):NaN),type:"float32",size:1},domain:o}}function N(s,t){const e=(s.stride??4)/4,i=(s.offset??0)/4;let n=s.value;if(!n){const a=s.buffer?.readSyncWebGL(0,e*4*t);a&&(n=new Float32Array(a.buffer),s.value=n)}if(e===1)return n.subarray(0,t);const o=new Float32Array(t);for(let a=0;a<t;a++)o[a]=n[a*e+i];return o}function $t(s,t){return s-t}function Wt(s,t){const e=s.length;if(t<=0||e<2)return s[0];if(t>=1)return s[e-1];const i=(e-1)*t,n=Math.floor(i),o=s[n],a=s[n+1];return o+(a-o)*(i-n)}function qt(s,t){let e=0,i=s.length;for(;e<i;){const n=e+i>>>1;s[n]>t?i=n:e=n+1}return e}function Yt({dataBounds:s,getBinId:t,padding:e=0}){const i=[s[0],s[1],[s[0][0],s[1][1]],[s[1][0],s[0][1]]].map(l=>t(l)),n=Math.min(...i.map(l=>l[0]))-e,o=Math.min(...i.map(l=>l[1]))-e,a=Math.max(...i.map(l=>l[0]))+e+1,r=Math.max(...i.map(l=>l[1]))+e+1;return[[n,a],[o,r]]}const U=Math.PI/3,C=2*Math.sin(U),S=1.5,Gt=Array.from({length:6},(s,t)=>{const e=t*U;return[Math.sin(e),-Math.cos(e)]});function w([s,t],e){let i=Math.round(t=t/e/S),n=Math.round(s=s/e/C-(i&1)/2);const o=t-i;if(Math.abs(o)*3>1){const a=s-n,r=n+(s<n?-1:1)/2,l=i+(t<i?-1:1),c=s-r,u=t-l;a*a+o*o>c*c+u*u&&(n=r+(i&1?1:-1)/2,i=l)}return[n,i]}const Xt=`
const vec2 DIST = vec2(${C}, ${S});

ivec2 pointToHexbin(vec2 p, float radius) {
  p /= radius * DIST;
  float pj = round(p.y);
  float pjm2 = mod(pj, 2.0);
  p.x -= pjm2 * 0.5;
  float pi = round(p.x);
  vec2 d1 = p - vec2(pi, pj);

  if (abs(d1.y) * 3. > 1.) {
    vec2 v2 = step(0.0, d1) - 0.5;
    v2.y *= 2.0;
    vec2 d2 = d1 - v2;
    if (dot(d1, d1) > dot(d2, d2)) {
      pi += v2.x + pjm2 - 0.5;
      pj += v2.y;
    }
  }
  return ivec2(pi, pj);
}
`;function z([s,t],e){return[(s+(t&1)/2)*e*C,t*e*S]}const Zt=`
const vec2 DIST = vec2(${C}, ${S});

vec2 hexbinCentroid(vec2 binId, float radius) {
  binId.x += fract(binId.y * 0.5);
  return binId * DIST * radius;
}
`,Kt=`#version 300 es
#define SHADER_NAME hexagon-cell-layer-vertex-shader
in vec3 positions;
in vec3 normals;
in vec2 instancePositions;
in float instanceElevationValues;
in float instanceColorValues;
in vec3 instancePickingColors;
uniform sampler2D colorRange;
out vec4 vColor;
${Zt}
float interp(float value, vec2 domain, vec2 range) {
float r = min(max((value - domain.x) / (domain.y - domain.x), 0.), 1.);
return mix(range.x, range.y, r);
}
vec4 interp(float value, vec2 domain, sampler2D range) {
float r = (value - domain.x) / (domain.y - domain.x);
return texture(range, vec2(r, 0.5));
}
void main(void) {
geometry.pickingColor = instancePickingColors;
if (isnan(instanceColorValues) ||
instanceColorValues < hexagon.colorDomain.z ||
instanceColorValues > hexagon.colorDomain.w ||
instanceElevationValues < hexagon.elevationDomain.z ||
instanceElevationValues > hexagon.elevationDomain.w
) {
gl_Position = vec4(0.);
return;
}
vec2 commonPosition = hexbinCentroid(instancePositions, column.radius) + (hexagon.originCommon - project.commonOrigin.xy);
commonPosition += positions.xy * column.radius * column.coverage;
geometry.position = vec4(commonPosition, 0.0, 1.0);
geometry.normal = project_normal(normals);
float elevation = 0.0;
if (column.extruded) {
elevation = interp(instanceElevationValues, hexagon.elevationDomain.xy, hexagon.elevationRange);
elevation = project_size(elevation);
geometry.position.z = (positions.z + 1.0) / 2.0 * elevation;
}
gl_Position = project_common_position_to_clipspace(geometry.position);
DECKGL_FILTER_GL_POSITION(gl_Position, geometry);
vColor = interp(instanceColorValues, hexagon.colorDomain.xy, colorRange);
vColor.a *= layer.opacity;
if (column.extruded) {
vColor.rgb = lighting_getLightColor(vColor.rgb, project.cameraPosition, geometry.position.xyz, geometry.normal);
}
DECKGL_FILTER_COLOR(vColor, geometry);
}
`,Qt=`uniform hexagonUniforms {
  vec4 colorDomain;
  vec4 elevationDomain;
  vec2 elevationRange;
  vec2 originCommon;
} hexagon;
`,Jt={name:"hexagon",vs:Qt,uniformTypes:{colorDomain:"vec4<f32>",elevationDomain:"vec4<f32>",elevationRange:"vec2<f32>",originCommon:"vec2<f32>"}};class j extends ft{getShaders(){const t=super.getShaders();return t.modules.push(Jt),{...t,vs:Kt}}initializeState(){super.initializeState();const t=this.getAttributeManager();t.remove(["instanceElevations","instanceFillColors","instanceLineColors","instanceStrokeWidths"]),t.addInstanced({instancePositions:{size:2,type:"float32",accessor:"getBin"},instanceColorValues:{size:1,type:"float32",accessor:"getColorValue"},instanceElevationValues:{size:1,type:"float32",accessor:"getElevationValue"}})}updateState(t){super.updateState(t);const{props:e,oldProps:i}=t,n=this.state.fillModel;if(i.colorRange!==e.colorRange){this.state.colorTexture?.destroy(),this.state.colorTexture=Ft(this.context.device,e.colorRange,e.colorScaleType);const o={colorRange:this.state.colorTexture};n.shaderInputs.setProps({hexagon:o})}else i.colorScaleType!==e.colorScaleType&&kt(this.state.colorTexture,e.colorScaleType)}finalizeState(t){super.finalizeState(t),this.state.colorTexture?.destroy()}draw({uniforms:t}){const{radius:e,hexOriginCommon:i,elevationRange:n,elevationScale:o,extruded:a,coverage:r,colorDomain:l,elevationDomain:c}=this.props,u=this.props.colorCutoff||[-1/0,1/0],h=this.props.elevationCutoff||[-1/0,1/0],g=this.state.fillModel;g.vertexArray.indexBuffer&&g.setIndexBuffer(null),g.setVertexCount(this.state.fillVertexCount);const d={colorDomain:[Math.max(l[0],u[0]),Math.min(l[1],u[1]),Math.max(l[0]-1,u[0]),Math.min(l[1]+1,u[1])],elevationDomain:[Math.max(c[0],h[0]),Math.min(c[1],h[1]),Math.max(c[0]-1,h[0]),Math.min(c[1]+1,h[1])],elevationRange:[n[0]*o,n[1]*o],originCommon:i};g.shaderInputs.setProps({column:{extruded:a,coverage:r,radius:e},hexagon:d}),g.draw(this.context.renderPass)}}j.layerName="HexagonCellLayer";const te=`uniform binOptionsUniforms {
  vec2 hexOriginCommon;
  float radiusCommon;
} binOptions;
`,ee={name:"binOptions",vs:te,uniformTypes:{hexOriginCommon:"vec2<f32>",radiusCommon:"f32"}};function L(){}const ie={gpuAggregation:!0,colorDomain:null,colorRange:Vt,getColorValue:{type:"accessor",value:null},getColorWeight:{type:"accessor",value:1},colorAggregation:"SUM",lowerPercentile:{type:"number",min:0,max:100,value:0},upperPercentile:{type:"number",min:0,max:100,value:100},colorScaleType:"quantize",onSetColorDomain:L,elevationDomain:null,elevationRange:[0,1e3],getElevationValue:{type:"accessor",value:null},getElevationWeight:{type:"accessor",value:1},elevationAggregation:"SUM",elevationScale:{type:"number",min:0,value:1},elevationLowerPercentile:{type:"number",min:0,max:100,value:0},elevationUpperPercentile:{type:"number",min:0,max:100,value:100},elevationScaleType:"linear",onSetElevationDomain:L,radius:{type:"number",min:1,value:1e3},coverage:{type:"number",min:0,max:1,value:1},getPosition:{type:"accessor",value:s=>s.position},hexagonAggregator:{type:"function",optional:!0,value:null},extruded:!1,material:!0};class A extends F{getAggregatorType(){const{gpuAggregation:t,hexagonAggregator:e,getColorValue:i,getElevationValue:n}=this.props;return t&&(e||i||n)?(B.warn("Features not supported by GPU aggregation, falling back to CPU")(),"cpu"):t&&P.isSupported(this.context.device)?"gpu":"cpu"}createAggregator(t){if(t==="cpu"){const{hexagonAggregator:e,radius:i}=this.props;return new _t({dimensions:2,getBin:{sources:["positions"],getValue:({positions:n},o,a)=>{if(e)return e(n,i);const l=this.state.aggregatorViewport.projectPosition(n),{radiusCommon:c,hexOriginCommon:u}=a;return w([l[0]-u[0],l[1]-u[1]],c)}},getValue:[{sources:["colorWeights"],getValue:({colorWeights:n})=>n},{sources:["elevationWeights"],getValue:({elevationWeights:n})=>n}]})}return new P(this.context.device,{dimensions:2,channelCount:2,bufferLayout:this.getAttributeManager().getBufferLayouts({isInstanced:!1}),...super.getShaders({modules:[gt,ee],vs:`
  in vec3 positions;
  in vec3 positions64Low;
  in float colorWeights;
  in float elevationWeights;
  
  ${Xt}

  void getBin(out ivec2 binId) {
    vec3 positionCommon = project_position(positions, positions64Low);
    binId = pointToHexbin(positionCommon.xy, binOptions.radiusCommon);
  }
  void getValue(out vec2 value) {
    value = vec2(colorWeights, elevationWeights);
  }
  `})})}initializeState(){super.initializeState(),this.getAttributeManager().add({positions:{size:3,accessor:"getPosition",type:"float64",fp64:this.use64bitPositions()},colorWeights:{size:1,accessor:"getColorWeight"},elevationWeights:{size:1,accessor:"getElevationWeight"}})}updateState(t){const e=super.updateState(t),{props:i,oldProps:n,changeFlags:o}=t,{aggregator:a}=this.state;if((o.dataChanged||!this.state.dataAsArray)&&(i.getColorValue||i.getElevationValue)&&(this.state.dataAsArray=Array.from(dt(i.data).iterable)),e||o.dataChanged||i.radius!==n.radius||i.getColorValue!==n.getColorValue||i.getElevationValue!==n.getElevationValue||i.colorAggregation!==n.colorAggregation||i.elevationAggregation!==n.elevationAggregation){this._updateBinOptions();const{radiusCommon:r,hexOriginCommon:l,binIdRange:c,dataAsArray:u}=this.state;if(a.setProps({binIdRange:c,pointCount:this.getNumInstances(),operations:[i.colorAggregation,i.elevationAggregation],binOptions:{radiusCommon:r,hexOriginCommon:l},onUpdate:this._onAggregationUpdate.bind(this)}),u){const{getColorValue:h,getElevationValue:g}=this.props;a.setProps({customOperations:[h&&(d=>h(d.map(m=>u[m]),{indices:d,data:i.data})),g&&(d=>g(d.map(m=>u[m]),{indices:d,data:i.data}))]})}}return o.updateTriggersChanged&&o.updateTriggersChanged.getColorValue&&a.setNeedsUpdate(0),o.updateTriggersChanged&&o.updateTriggersChanged.getElevationValue&&a.setNeedsUpdate(1),e}_updateBinOptions(){const t=this.getBounds();let e=1,i=[0,0],n=[[0,1],[0,1]],o=this.context.viewport;if(t&&Number.isFinite(t[0][0])){let a=[(t[0][0]+t[1][0])/2,(t[0][1]+t[1][1])/2];const{radius:r}=this.props,{unitsPerMeter:l}=o.getDistanceScales(a);e=l[0]*r;const c=w(o.projectFlat(a),e);a=o.unprojectFlat(z(c,e));const u=o.constructor;o=o.isGeospatial?new u({longitude:a[0],latitude:a[1],zoom:12}):new mt({position:[a[0],a[1],0],zoom:12}),i=[Math.fround(o.center[0]),Math.fround(o.center[1])],n=Yt({dataBounds:t,getBinId:h=>{const g=o.projectFlat(h);return g[0]-=i[0],g[1]-=i[1],w(g,e)},padding:1})}this.setState({radiusCommon:e,hexOriginCommon:i,binIdRange:n,aggregatorViewport:o})}draw(t){t.shaderModuleProps.project&&(t.shaderModuleProps.project.viewport=this.state.aggregatorViewport),super.draw(t)}_onAggregationUpdate({channel:t}){const e=this.getCurrentLayer().props,{aggregator:i}=this.state;if(t===0){const n=i.getResult(0);this.setState({colors:new O(n,i.binCount)}),e.onSetColorDomain(i.getResultDomain(0))}else if(t===1){const n=i.getResult(1);this.setState({elevations:new O(n,i.binCount)}),e.onSetElevationDomain(i.getResultDomain(1))}}onAttributeChange(t){const{aggregator:e}=this.state;switch(t){case"positions":e.setNeedsUpdate(),this._updateBinOptions();const{radiusCommon:i,hexOriginCommon:n,binIdRange:o}=this.state;e.setProps({binIdRange:o,binOptions:{radiusCommon:i,hexOriginCommon:n}});break;case"colorWeights":e.setNeedsUpdate(0);break;case"elevationWeights":e.setNeedsUpdate(1);break}}renderLayers(){const{aggregator:t,radiusCommon:e,hexOriginCommon:i}=this.state,{elevationScale:n,colorRange:o,elevationRange:a,extruded:r,coverage:l,material:c,transitions:u,colorScaleType:h,lowerPercentile:g,upperPercentile:d,colorDomain:m,elevationScaleType:$,elevationLowerPercentile:W,elevationUpperPercentile:q,elevationDomain:Y}=this.props,G=this.getSubLayerClass("cells",j),I=t.getBins(),f=this.state.colors?.update({scaleType:h,lowerPercentile:g,upperPercentile:d}),p=this.state.elevations?.update({scaleType:$,lowerPercentile:W,upperPercentile:q});return!f||!p?null:new G(this.getSubLayerProps({id:"cells"}),{data:{length:t.binCount,attributes:{getBin:I,getColorValue:f.attribute,getElevationValue:p.attribute}},dataComparator:(X,Z)=>X.length===Z.length,updateTriggers:{getBin:[I],getColorValue:[f.attribute],getElevationValue:[p.attribute]},diskResolution:6,vertices:Gt,radius:e,hexOriginCommon:i,elevationScale:n,colorRange:o,colorScaleType:h,elevationRange:a,extruded:r,coverage:l,material:c,colorDomain:f.domain||m||t.getResultDomain(0),elevationDomain:p.domain||Y||t.getResultDomain(1),colorCutoff:f.cutoff,elevationCutoff:p.cutoff,transitions:u&&{getFillColor:u.getColorValue||u.getColorWeight,getElevation:u.getElevationValue||u.getElevationWeight},extensions:[]})}getPickingInfo(t){const e=t.info,{index:i}=e;if(i>=0){const n=this.state.aggregator.getBin(i);let o;if(n){const a=z(n.id,this.state.radiusCommon),r=this.context.viewport.unprojectFlat(a);o={col:n.id[0],row:n.id[1],position:r,colorValue:n.value[0],elevationValue:n.value[1],count:n.count},n.pointIndices&&(o.pointIndices=n.pointIndices,o.points=Array.isArray(this.props.data)?n.pointIndices.map(l=>this.props.data[l]):[])}e.object=o}return e}}A.layerName="HexagonLayer";A.defaultProps=ie;const se={ambient:.64,diffuse:.6,shininess:32,specularColor:[51,51,51]},ne=R({name:"XYHexMapComponent",props:{viewId:{type:Number,required:!0},colorRamp:{type:String,required:!0},coverage:{type:Number,required:!0},dark:{type:Boolean,required:!0},data:{type:Object,required:!0},extrude:{type:Boolean,required:!0},highlights:{type:Array,required:!0},mapIsIndependent:{type:Boolean,required:!0},maxHeight:{type:Number,required:!0},metric:{type:String,required:!0},radius:{type:Number,required:!0},selectedHexStats:{type:Object,required:!1},upperPercentile:{type:Number,required:!0},onClick:{type:Function,required:!0},agg:{type:Number,required:!0},group:{type:String,required:!0}},data(){return{mymap:null,deckOverlay:null,globalState:b.state,tooltipHTML:"",tooltipStyle:{position:"absolute",padding:"4px 8px",display:"block",top:0,left:0,color:this.dark?"#ccc":"#223",backgroundColor:this.dark?"#2a3c4f":"white",zIndex:2e4}}},watch:{layers(){this.deckOverlay?.setProps({layers:this.layers})},dark(){const s=`/map-styles/${this.dark?"dark":"positron"}.json`;this.mymap?.setStyle(s)},"globalState.viewState"(){if(this.mapIsIndependent||!this.mymap)return;const s=this.globalState.viewState,t=this.mymap?.getCenter();if(s.longitude!==t.lng||s.latitude!==t.lat||s.zoom!==this.mymap?.getZoom()||s.pitch!==this.mymap?.getPitch()||s.bearing!==this.mymap?.getBearing())try{this.mymap?.jumpTo(s)}catch(e){console.warn(""+e)}}},computed:{weightedRowData(){let s=[];return this.highlights.length?this.highlights.map(t=>t[0]):!this.data||!Object.keys(this.data).length?s:{length:this.data[this.group].positions[this.agg].length/2}},colors(){const s=ot({colormap:this.colorRamp,nshades:10,format:"rba",alpha:1}).map(t=>[t[0],t[1],t[2]]);return this.dark||s.reverse(),s.slice(1)},layers(){const s=this.data[this.group],t=this.highlights.length?{getPosition:a=>a}:{getPosition:(a,r)=>s.positions[this.agg].slice(r.index*2,r.index*2+2)},e=s?.positions[this.agg].length/2||0;let i=null;e<10&&(i=this.colors.slice(4,5));const n=[new rt({id:"arc-layer",data:this.highlights,getSourcePosition:a=>a[0],getTargetPosition:a=>a[1],pickable:!1,opacity:.4,getHeight:0,getWidth:1,getSourceColor:this.dark?[144,96,128]:[192,192,240],getTargetColor:this.dark?[144,96,128]:[192,192,240]})],o=Object.assign(t,{id:"hexlayer",data:this.weightedRowData,colorRange:i||this.colors,coverage:.98,autoHighlight:!0,elevationRange:[0,this.maxHeight],elevationScale:25,extruded:this.extrude,gpuAggregation:!1,selectedHexStats:this.selectedHexStats,material:se,opacity:this.dark&&this.highlights.length?.6:.8,pickable:!0,pickingRadius:2,positionFormat:"XY",radius:this.radius,upperPercentile:this.upperPercentile,updateTriggers:{},transitions:{elevationScale:{type:"interpolation",duration:1e3},opacity:{type:"interpolation",duration:200}},onHover:this.getTooltip});return n.push(new A(o)),n}},mounted(){const s=`/map-styles/${this.globalState.isDarkMode?"dark":"positron"}.json`,t=`map-${this.viewId}`,e=this.globalState.viewState;this.mymap=new K.Map({container:t,style:s,...e}),this.mymap.on("style.load",()=>{this.deckOverlay=new at({interleaved:!0,layers:this.layers,onClick:this.handleClick}),this.mymap?.addControl(this.deckOverlay)}),this.mymap?.on("move",()=>{const i=this.mymap?.getCenter(),n={latitude:i.lat,longitude:i.lng,zoom:this.mymap?.getZoom(),bearing:this.mymap?.getBearing(),pitch:this.mymap?.getPitch(),jump:!0};b.commit("setMapCamera",n)})},beforeDestroy(){this.deckOverlay&&this.mymap?.removeControl(this.deckOverlay),this.mymap?.remove()},methods:{getTooltip(s){const{x:t,y:e,object:i}=s;if(!i||!i.position||!i.position.length){this.tooltipStyle.display="none";return}const n=i.position[1],o=i.position[0],a=i.pointIndices.length,r=`        <b>${this.highlights.length?"Count":this.metric}: ${a} </b><br/>
        ${Number.isFinite(n)?n.toFixed(4):""} / ${Number.isFinite(o)?o.toFixed(4):""}
      `;this.tooltipStyle.display="block",this.tooltipStyle.top=`${e+12}px`,this.tooltipStyle.left=`${t+12}px`,this.tooltipHTML=r},handleClick(s,t){this.tooltipStyle.display="none",this.onClick&&this.onClick(s,t)}}});var oe=function(){var t=this,e=t._self._c;return t._self._setupProxy,e("div",{staticClass:"hex-map flex-col"},[e("div",{staticClass:"map-container",attrs:{id:`map-${t.viewId}`}}),e("div",{directives:[{name:"show",rawName:"v-show",value:t.tooltipHTML,expression:"tooltipHTML"}],staticClass:"deck-tooltip",style:t.tooltipStyle,domProps:{innerHTML:t._s(t.tooltipHTML)}})])},ae=[],re=H(ne,oe,ae,!1,null,null);const le=re.exports,ue={messages:{en:{loading:"Loading data...",sorting:"Sorting into bins...",aggregate:"Summary",maxHeight:"3D Height",showDetails:"Show Details",selection:"Selection",areas:"Areas",count:"Count"},de:{loading:"Dateien laden...",sorting:"Sortieren...",aggregate:"Daten",maxHeight:"3-D Höhe",showDetails:"Details anzeigen",selection:"Ausgewählt",areas:"Orte",count:"Anzahl"}}},ce=R({name:"XyHexagonsPlugin",i18n:ue,components:{CollapsiblePanel:it,DrawingTool:st,XyHexDeckMap:le,ToggleButton:J.ToggleButton,ZoomButtons:nt},props:{root:{type:String,required:!0},subfolder:{type:String,required:!0},yamlConfig:String,config:Object,thumbnail:Boolean},data:()=>{const s=["par","bathymetry","magma","chlorophyll"];return{id:Math.floor(1e12*Math.random()),resolvers:{},resolverId:0,_xmlConfigFetcher:{},standaloneYAMLconfig:{title:"",description:"",file:"",projection:"",thumbnail:"",aggregations:{},radius:250,maxHeight:0,center:null,zoom:9,mapIsIndependent:!1},YAMLrequirementsXY:{file:"",aggregations:{}},colorRamps:s,buttonColors:["#BF7230","#5E8AAE","#9C439C","#269367"],aggregations:{},aggNumber:0,gzipWorker:null,colorRamp:s[0],globalState:b.state,currentGroup:"",vizDetails:{title:"",description:"",file:"",projection:"",thumbnail:"",aggregations:{},radius:250,maxHeight:0,center:null,zoom:9},myState:{statusMessage:"",subfolder:"",yamlConfig:"",thumbnail:!1},requests:{},highlightedTrips:[],searchTerm:"",searchEnabled:!1,isLoaded:!1,activeAggregation:"",isHighlightingZone:!1,multiSelectedHexagons:{},thumbnailUrl:"url('assets/thumbnail.jpg') no-repeat;",hexStats:null,resizer:null}},computed:{fileApi(){return new et(this.fileSystem,b)},fileSystem(){const s=this.$store.state.svnProjects.filter(t=>t.slug===this.root);if(s.length===0)throw console.log("no such project"),Error;return s[0]},urlThumbnail(){return this.thumbnailUrl},buttonLabel(){const[s,t]=this.activeAggregation.split("~");return this.aggregations[s][t].title},extrudeTowers(){return this.vizDetails.maxHeight>0},mapProps(){return{viewId:this.id,group:this.currentGroup,agg:this.aggNumber,colorRamp:this.colorRamp,coverage:.7,dark:this.$store.state.isDarkMode,data:this.requests,extrude:this.extrudeTowers,highlights:this.highlightedTrips,mapIsIndependent:this.vizDetails.mapIsIndependent||!1,maxHeight:this.vizDetails.maxHeight,metric:this.buttonLabel,radius:this.vizDetails.radius,selectedHexStats:this.hexStats,upperPercentile:100,onClick:this.handleClick}},textColor(){const s={text:"#3498db",bg:"#eeeef480"},t={text:"white",bg:"#181518aa"};return this.$store.state.colorScheme===Q.DarkMode?t:s}},watch:{extrudeTowers(){this.extrudeTowers&&this.globalState.viewState.pitch==0&&b.commit("setMapCamera",Object.assign({},this.globalState.viewState,{pitch:10}))}},methods:{handleClick(s,t){s.layer?this.handleHexClick(s,t):this.handleEmptyClick()},handleEmptyClick(){this.flipViewToShowInvertedData({})},handleHexClick(s,t){if(!t.srcEvent.shiftKey){this.multiSelectedHexagons={},this.hexStats=null,this.flipViewToShowInvertedData(s);return}const e=s?.object?.index;e!==void 0&&(e in this.multiSelectedHexagons?delete this.multiSelectedHexagons[e]:this.multiSelectedHexagons[e]=s.object.points,this.hexStats=this.selectedHexagonStatistics())},flipViewToShowInvertedData(s){this.isHighlightingZone?this.isHighlightingZone=!1:this.isHighlightingZone=!!s.object;const t=this.activeAggregation.split("~");if(!this.isHighlightingZone){this.hexStats=null,this.multiSelectedHexagons={},this.handleOrigDest(t[0],parseInt(t[1])),this.highlightedTrips=[];return}let e=this.aggNumber+(this.aggNumber%2?-1:1);const i=[];for(const n of s.object.pointIndices){const o=n*2,a=[this.requests[this.currentGroup].positions[e][o],this.requests[this.currentGroup].positions[e][o+1]],r=[this.requests[this.currentGroup].positions[this.aggNumber][o],this.requests[this.currentGroup].positions[this.aggNumber][o+1]];i.push([a,r]),this.highlightedTrips=i}this.hexStats&&(this.hexStats.selectedHexagonIds=[]),this.multiSelectedHexagons={},this.colorRamp=this.colorRamps[e]},handleOrigDest(s,t){this.currentGroup=s,this.aggNumber=t,this.hexStats=null,this.multiSelectedHexagons={},this.highlightedTrips=[],this.activeAggregation=`${s}~${t}`,this.colorRamp=this.colorRamps[t]},async getVizDetails(){if(this.config){this.validateYAML(),this.vizDetails=Object.assign({},this.config),this.setRadiusAndHeight();return}new RegExp(".*(yml|yaml)$").test(this.myState.yamlConfig)?await this.loadStandaloneYAMLConfig():await this.loadOutputTripsConfig()},fetchXML(s){let t=s.worker;t.onmessage=n=>{const{resolve:o,reject:a}=this.resolvers[n.data.id];t.terminate(),n.data.error&&a(n.data.error),o(n.data.xml)};const e=this.resolverId++;return t.postMessage({id:e,fileSystem:this.fileSystem,filePath:s.filePath,options:s.options}),new Promise((n,o)=>{this.resolvers[e]={resolve:n,reject:o}})},async figureOutProjection(){const{files:s}=await this.fileApi.getDirectory(this.myState.subfolder),t=s.filter(e=>e.indexOf(".output_config.xml")>-1||e.indexOf(".output_config_reduced.xml")>-1);if(t.length&&this.fileSystem)for(const e of t)try{return(await this.fetchXML({worker:this._xmlConfigFetcher,slug:this.fileSystem.slug,filePath:this.myState.subfolder+"/"+e})).config.module.filter(r=>r.$name==="global")[0].param.filter(r=>r.$name==="coordinateSystem")[0].$value}catch{console.warn("Failed parsing",e)}},async loadOutputTripsConfig(){let s=await this.figureOutProjection();!this.myState.thumbnail&&!s&&(s=prompt('Enter projection: e.g. "EPSG:31468"')||"EPSG:31468",parseInt(s,10)&&(s="EPSG:"+s)),this.vizDetails={title:"Output Trips",description:this.myState.yamlConfig,file:this.myState.yamlConfig,projection:s,aggregations:{"Trip Summary":[{title:"Origins",x:"start_x",y:"start_y"},{title:"Destinations",x:"end_x",y:"end_y"}]},radius:this.vizDetails.radius,maxHeight:this.vizDetails.maxHeight,center:this.vizDetails.center,zoom:this.vizDetails.zoom},this.$emit("title",this.vizDetails.title)},setRadiusAndHeight(){this.vizDetails.radius||_.set(this.vizDetails,"radius",250),this.vizDetails.maxHeight||_.set(this.vizDetails,"maxHeight",0)},async loadStandaloneYAMLConfig(){try{const s=this.myState.yamlConfig.indexOf("/")>-1?this.myState.yamlConfig:this.myState.subfolder+"/"+this.myState.yamlConfig,t=await this.fileApi.getFileText(s);this.standaloneYAMLconfig=Object.assign({},tt.parse(t)),this.validateYAML(),this.setVizDetails()}catch(s){console.error("failed",""+s),this.$emit("error",`File not found: ${this.myState.subfolder}/${this.myState.yamlConfig}`)}},validateYAML(){const s=new RegExp(".*(yml|yaml)$").test(this.myState.yamlConfig);let t={};s?(console.log("has yaml"),t=this.standaloneYAMLconfig):(console.log("no yaml"),t=this.config);for(const e in this.YAMLrequirementsXY)e in t||this.$emit("error",{type:v.ERROR,msg:`XYHexagon: ${this.yamlConfig}: missing required key: ${e}`,desc:`XYHexagon requires ${Object.keys(this.YAMLrequirementsXY)}`});t.radius==0&&this.$emit("error",{type:v.WARNING,msg:"Radius set to zero",desc:"Radius can not be zero, preset value used instead. "}),(t.zoom<5||t.zoom>20)&&this.$emit("error",{type:v.WARNING,msg:"Zoom is out of the recommended range ",desc:"Zoom levels should be between 5 and 20. "})},setVizDetails(){this.vizDetails=Object.assign({},this.vizDetails,this.standaloneYAMLconfig),this.setRadiusAndHeight();const s=this.vizDetails.title?this.vizDetails.title:"Hex Aggregation";this.$emit("title",s)},handleShowSelectionButton(){const s=Object.values(this.multiSelectedHexagons);let t=[];s.map(i=>t=t.concat(i));const e={object:{points:t}};this.flipViewToShowInvertedData(e)},selectedHexagonStatistics(){const s=Object.keys(this.multiSelectedHexagons).map(i=>parseInt(i));return s.length?{rows:Object.values(this.multiSelectedHexagons).reduce((i,n)=>i+n.length,0),numHexagons:s.length,selectedHexagonIds:s}:null},setMapCenter(){if(this.vizDetails.center){typeof this.vizDetails.center=="string"&&(this.vizDetails.center=this.vizDetails.center.split(",").map(Number));const l={center:this.vizDetails.center,zoom:this.vizDetails.zoom||10,bearing:0,pitch:0};this.$store.commit("setMapCamera",Object.assign({},l));return}const s=Object.keys(this.requests);if(!s.length)return;const t=this.requests[s[0]].positions[0];let e=0,i=0,n=0;const o=t.length/2,a=512;for(let l=0;l<o;l+=a)i+=t[l*2],n+=t[l*2+1],e++;i=i/e,n=n/e;const r=this.$store.state.viewState;i&&n&&this.$store.commit("setMapCamera",{longitude:i,latitude:n,bearing:r.bearing,pitch:r.pitch,zoom:this.vizDetails.zoom||r.zoom,jump:!1})},async parseCSVFile(s){this.myState.statusMessage="Loading file...";let t=new bt;t.onmessage=async e=>{if(e.data.ready){t.postMessage({filepath:s,fileSystem:this.fileSystem,aggregations:this.vizDetails.aggregations,projection:this.vizDetails.projection});return}if(e.data.status)this.myState.statusMessage=e.data.status;else if(e.data.projection)console.log("dataset has a #EPSG:projection, using it",e.data.projection),this.vizDetails.projection=e.data.projection;else if(e.data.error)this.myState.statusMessage=e.data.error,this.$emit("error",{type:v.ERROR,msg:`Error loading: ${this.myState.subfolder}/${this.vizDetails.file}`});else{const{fullRowCache:i}=e.data;this.gzipWorker?.terminate(),this.dataIsLoaded({fullRowCache:i})}},this.gzipWorker=t},dataIsLoaded({fullRowCache:s}){this.requests=s,this.setMapCenter(),this.myState.statusMessage="",this.isLoaded=!0},async loadFiles(){let s=[];if(!this.fileApi)return{dataArray:s};try{let t=`${this.myState.subfolder}/${this.vizDetails.file}`;await this.parseCSVFile(t)}catch(t){console.error(t),this.myState.statusMessage=""+t,this.$emit("error",`Loading/parsing: ${this.myState.subfolder}/${this.vizDetails.file}`)}}},async mounted(){this.$store.commit("setFullScreen",!this.thumbnail),this.myState.thumbnail=this.thumbnail,this.myState.yamlConfig=this.yamlConfig||"",this.myState.subfolder=this.subfolder,this._xmlConfigFetcher=new pt,await this.getVizDetails(),this.myState.statusMessage=`${this.$i18n.t("loading")}`,this.aggregations=this.vizDetails.aggregations,await this.loadFiles(),this.handleOrigDest(Object.keys(this.aggregations)[0],0)},beforeDestroy(){this._xmlConfigFetcher&&this._xmlConfigFetcher.terminate(),this.resizer?.disconnect();try{this.gzipWorker&&this.gzipWorker.terminate()}catch(s){console.warn(s)}this.$store.commit("setFullScreen",!1)}});var he=function(){var t=this,e=t._self._c;return t._self._setupProxy,e("div",{staticClass:"xy-hexagons",attrs:{oncontextmenu:"return false",id:`id-${t.id}`}},[t.isLoaded?e("xy-hex-deck-map",t._b({staticClass:"hex-layer"},"xy-hex-deck-map",t.mapProps,!1)):t._e(),t.thumbnail?t._e():e("zoom-buttons"),t.isLoaded&&!t.thumbnail&&t.vizDetails.title?e("div",{staticClass:"left-side"},[e("collapsible-panel",{attrs:{direction:"left",locked:!0}},[t.hexStats?e("div",{staticClass:"panel-items",staticStyle:{color:"#c0f"}},[e("p",{staticClass:"big",staticStyle:{"margin-top":"2rem"}},[t._v(t._s(t.$t("selection"))+":")]),e("h3",{staticStyle:{"margin-top":"-1rem"}},[t._v(t._s(t.$t("areas"))+": "+t._s(t.hexStats.numHexagons)+", "+t._s(t.$t("count"))+": "+t._s(t.hexStats.rows))]),e("button",{staticClass:"button",staticStyle:{color:"#c0f","border-color":"#c0f"},on:{click:t.handleShowSelectionButton}},[t._v(t._s(t.$t("showDetails")))])]):t._e()])],1):t._e(),t.isLoaded&&!t.thumbnail&&!t.myState.statusMessage?e("div",{staticClass:"control-panel",attrs:{"data-testid":"xy-hexagons-control-panel"}},[t._l(Object.keys(t.aggregations),function(i){return e("div",{key:i,staticClass:"panel-item"},[e("p",{staticClass:"ui-label"},[t._v(t._s(i))]),t._l(t.aggregations[i],function(n,o){return e("button",{key:o,staticClass:"button is-small aggregation-button",style:{"margin-bottom":"0.25rem",color:t.activeAggregation===`${i}~${o}`?"white":t.buttonColors[o],border:`1px solid ${t.buttonColors[o]}`,"border-right":`0.4rem solid ${t.buttonColors[o]}`,"border-radius":"4px","background-color":t.activeAggregation===`${i}~${o}`?t.buttonColors[o]:t.$store.state.isDarkMode?"#333":"white"},on:{click:function(a){return t.handleOrigDest(i,o)}}},[t._v(t._s(n.title))])})],2)}),e("div",{staticClass:"panel-item"},[e("p",{staticClass:"ui-label"},[t._v(t._s(t.$t("maxHeight"))+": "+t._s(t.vizDetails.maxHeight))]),e("b-slider",{staticClass:"ui-slider",attrs:{size:"is-small",min:0,max:250,step:5,duration:0,dotSize:12,tooltip:!1},model:{value:t.vizDetails.maxHeight,callback:function(i){t.$set(t.vizDetails,"maxHeight",i)},expression:"vizDetails.maxHeight"}}),e("p",{staticClass:"ui-label"},[t._v("Hex Radius: "+t._s(t.vizDetails.radius))]),e("b-slider",{staticClass:"ui-slider",attrs:{size:"is-small",min:50,max:1e3,step:5,duration:0,dotSize:12,tooltip:!1},model:{value:t.vizDetails.radius,callback:function(i){t.$set(t.vizDetails,"radius",i)},expression:"vizDetails.radius"}})],1)],2):t._e(),!t.thumbnail&&t.myState.statusMessage?e("div",{staticClass:"message"},[e("p",{staticClass:"status-message"},[t._v(t._s(t.myState.statusMessage))])]):t._e()],1)},ge=[],de=H(ce,he,ge,!1,null,"274dcabd");const Oe=de.exports;export{Oe as default};
